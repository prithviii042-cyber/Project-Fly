"""
Agent API — chat and agent execution endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
import anthropic

agent_bp = Blueprint('agent', __name__)


def get_client():
    return anthropic.Anthropic(api_key=current_app.config['ANTHROPIC_API_KEY'])


@agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    Simple single-turn chat with Claude.

    Request body:
        { "message": "Hello!", "system": "Optional system prompt" }

    Response:
        { "response": "...", "model": "claude-sonnet-4-6" }
    """
    data = request.get_json(force=True)
    user_message = data.get('message', '').strip()
    system_prompt = data.get('system', 'You are a helpful AI assistant.')

    if not user_message:
        return jsonify({'error': 'message is required'}), 400

    client = get_client()
    model = current_app.config['CLAUDE_MODEL']

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_message}]
    )

    return jsonify({
        'response': message.content[0].text,
        'model': model
    })


@agent_bp.route('/stream', methods=['POST'])
def stream():
    """
    Streaming chat — returns Server-Sent Events.

    Request body:
        { "message": "...", "system": "Optional system prompt" }
    """
    from flask import Response

    data = request.get_json(force=True)
    user_message = data.get('message', '').strip()
    system_prompt = data.get('system', 'You are a helpful AI assistant.')

    if not user_message:
        return jsonify({'error': 'message is required'}), 400

    client = get_client()
    model = current_app.config['CLAUDE_MODEL']

    def generate():
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{'role': 'user', 'content': user_message}]
        ) as stream:
            for text in stream.text_stream:
                yield f'data: {text}\n\n'
        yield 'data: [DONE]\n\n'

    return Response(generate(), mimetype='text/event-stream',
                    headers={'X-Accel-Buffering': 'no'})
