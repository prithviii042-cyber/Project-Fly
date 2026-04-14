"""
SQLite-backed store for A/B test experiments and variants.
Database file: backend/data/abtest.db
"""

import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/abtest.db')


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                description TEXT,
                goal        TEXT,
                status      TEXT DEFAULT 'running',
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS variants (
                id              TEXT PRIMARY KEY,
                experiment_id   TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
                name            TEXT NOT NULL,
                content         TEXT NOT NULL,
                views           INTEGER DEFAULT 0,
                conversions     INTEGER DEFAULT 0,
                created_at      TEXT NOT NULL
            );
        """)


def _row_to_dict(row):
    return dict(row) if row else None


# ── Experiments ────────────────────────────────────────────────

def create_experiment(name, description='', goal=''):
    exp_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO experiments (id, name, description, goal, status, created_at) VALUES (?,?,?,?,?,?)",
            (exp_id, name, description, goal, 'running', now)
        )
    return get_experiment(exp_id)


def list_experiments():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM experiments ORDER BY created_at DESC"
        ).fetchall()
    experiments = [_row_to_dict(r) for r in rows]
    for exp in experiments:
        exp['variants'] = list_variants(exp['id'])
    return experiments


def get_experiment(exp_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM experiments WHERE id=?", (exp_id,)
        ).fetchone()
    if not row:
        return None
    exp = _row_to_dict(row)
    exp['variants'] = list_variants(exp_id)
    return exp


def delete_experiment(exp_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM experiments WHERE id=?", (exp_id,))


def update_experiment_status(exp_id, status):
    with get_conn() as conn:
        conn.execute(
            "UPDATE experiments SET status=? WHERE id=?", (status, exp_id)
        )


# ── Variants ───────────────────────────────────────────────────

def create_variant(experiment_id, name, content):
    var_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO variants (id, experiment_id, name, content, views, conversions, created_at) VALUES (?,?,?,?,0,0,?)",
            (var_id, experiment_id, name, content, now)
        )
    return get_variant(var_id)


def list_variants(experiment_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM variants WHERE experiment_id=? ORDER BY created_at ASC",
            (experiment_id,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_variant(var_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM variants WHERE id=?", (var_id,)
        ).fetchone()
    return _row_to_dict(row)


def record_view(var_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE variants SET views = views + 1 WHERE id=?", (var_id,)
        )


def record_conversion(var_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE variants SET conversions = conversions + 1 WHERE id=?", (var_id,)
        )
