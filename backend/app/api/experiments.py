from flask import Blueprint, request, jsonify, current_app
import anthropic
import math

from ..models.experiment import (
    init_db, create_experiment, list_experiments, get_experiment,
    delete_experiment, update_experiment_status,
    create_variant, record_view, record_conversion
)

experiments_bp = Blueprint('experiments', __name__)


# ── Helpers ────────────────────────────────────────────────────

def _get_client():
    return anthropic.Anthropic(api_key=current_app.config['ANTHROPIC_API_KEY'])


def _conversion_rate(variant):
    if variant['views'] == 0:
        return 0.0
    return round(variant['conversions'] / variant['views'] * 100, 2)


def _z_score(p1, n1, p2, n2):
    """Two-proportion z-test."""
    if n1 == 0 or n2 == 0:
        return 0.0
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0
    return (p1 - p2) / se


# ── Experiment CRUD ────────────────────────────────────────────



@experiments_bp.route('', methods=['GET'])
def list_exps():
    return jsonify(list_experiments())


@experiments_bp.route('', methods=['POST'])
def create_exp():
    data = request.get_json(force=True)
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    exp = create_experiment(
        name=name,
        description=data.get('description', ''),
        goal=data.get('goal', '')
    )

    # Create variants if provided
    for v in data.get('variants', []):
        if v.get('name') and v.get('content'):
            create_variant(exp['id'], v['name'], v['content'])

    return jsonify(get_experiment(exp['id'])), 201


@experiments_bp.route('/<exp_id>', methods=['GET'])
def get_exp(exp_id):
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({'error': 'not found'}), 404
    return jsonify(exp)


@experiments_bp.route('/<exp_id>', methods=['DELETE'])
def delete_exp(exp_id):
    if not get_experiment(exp_id):
        return jsonify({'error': 'not found'}), 404
    delete_experiment(exp_id)
    return jsonify({'ok': True})


@experiments_bp.route('/<exp_id>/status', methods=['PATCH'])
def update_status(exp_id):
    data = request.get_json(force=True)
    status = data.get('status')
    if status not in ('running', 'paused', 'completed'):
        return jsonify({'error': 'invalid status'}), 400
    update_experiment_status(exp_id, status)
    return jsonify(get_experiment(exp_id))


# ── Variant tracking ────────────────────────────────────────────

@experiments_bp.route('/<exp_id>/variants', methods=['POST'])
def add_variant(exp_id):
    if not get_experiment(exp_id):
        return jsonify({'error': 'experiment not found'}), 404
    data = request.get_json(force=True)
    name = data.get('name', '').strip()
    content = data.get('content', '').strip()
    if not name or not content:
        return jsonify({'error': 'name and content are required'}), 400
    variant = create_variant(exp_id, name, content)
    return jsonify(variant), 201


@experiments_bp.route('/<exp_id>/variants/<var_id>/view', methods=['POST'])
def track_view(exp_id, var_id):
    record_view(var_id)
    return jsonify({'ok': True})


@experiments_bp.route('/<exp_id>/variants/<var_id>/convert', methods=['POST'])
def track_conversion(exp_id, var_id):
    record_conversion(var_id)
    return jsonify({'ok': True})


# ── Claude AI features ─────────────────────────────────────────

@experiments_bp.route('/<exp_id>/analyze', methods=['POST'])
def analyze(exp_id):
    """Ask Claude to analyze results and recommend a winner."""
    exp = get_experiment(exp_id)
    if not exp:
        return jsonify({'error': 'not found'}), 404

    variants = exp['variants']
    if not variants:
        return jsonify({'error': 'no variants to analyze'}), 400

    # Build stats summary for Claude
    stats = []
    for v in variants:
        cr = _conversion_rate(v)
        stats.append(
            f"- **{v['name']}**: {v['views']} views, {v['conversions']} conversions, "
            f"{cr}% conversion rate\n  Content: \"{v['content']}\""
        )

    # Statistical significance between best and worst
    sorted_v = sorted(variants, key=lambda x: _conversion_rate(x), reverse=True)
    sig_note = ''
    if len(sorted_v) >= 2:
        best, worst = sorted_v[0], sorted_v[-1]
        p1 = best['conversions'] / max(best['views'], 1)
        p2 = worst['conversions'] / max(worst['views'], 1)
        z = abs(_z_score(p1, best['views'], p2, worst['views']))
        confidence = 'low (need more data)'
        if z > 2.576:
            confidence = '99%'
        elif z > 1.96:
            confidence = '95%'
        elif z > 1.645:
            confidence = '90%'
        sig_note = f"\nStatistical confidence between best and worst: {confidence} (z={z:.2f})"

    prompt = f"""You are an A/B testing expert. Analyze these experiment results and give a clear recommendation.

Experiment: {exp['name']}
Goal: {exp['goal'] or 'maximize conversions'}

Variant results:
{chr(10).join(stats)}
{sig_note}

Provide:
1. A clear winner recommendation (or "need more data" if insufficient)
2. Why this variant is winning (or likely to win)
3. One specific suggestion to improve the losing variant(s)
4. Whether the results are statistically significant enough to act on

Be concise and actionable."""

    client = _get_client()
    message = client.messages.create(
        model=current_app.config['CLAUDE_MODEL'],
        max_tokens=600,
        messages=[{'role': 'user', 'content': prompt}]
    )

    return jsonify({'analysis': message.content[0].text})


@experiments_bp.route('/generate-variants', methods=['POST'])
def generate_variants():
    """Ask Claude to generate A/B variant suggestions."""
    data = request.get_json(force=True)
    description = data.get('description', '').strip()
    goal = data.get('goal', '').strip()
    context = data.get('context', '').strip()

    if not description:
        return jsonify({'error': 'description is required'}), 400

    prompt = f"""You are a conversion rate optimization expert. Generate exactly 2 compelling A/B test variants.

What we're testing: {description}
Goal: {goal or 'maximize conversions/engagement'}
{f'Context: {context}' if context else ''}

Return ONLY a JSON array with exactly 2 objects, no other text:
[
  {{"name": "Variant A", "content": "...the actual copy/content..."}},
  {{"name": "Variant B", "content": "...the actual copy/content..."}}
]

Make the variants meaningfully different (e.g. emotional vs rational, short vs detailed, direct vs curiosity-driven)."""

    client = _get_client()
    message = client.messages.create(
        model=current_app.config['CLAUDE_MODEL'],
        max_tokens=400,
        messages=[{'role': 'user', 'content': prompt}]
    )

    import json, re
    raw = message.content[0].text.strip()
    # Extract JSON array from response
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return jsonify({'error': 'Could not parse variants from Claude response', 'raw': raw}), 500

    try:
        variants = json.loads(match.group())
        return jsonify({'variants': variants})
    except json.JSONDecodeError as e:
        return jsonify({'error': str(e), 'raw': raw}), 500
