"""
Project Fly — Flask app factory
"""

import os
import sys
from flask import Flask
from flask_cors import CORS

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configurable CORS origins (comma-separated list or '*')
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    origins = [o.strip() for o in cors_origins.split(',')] if cors_origins != '*' else '*'
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Register blueprints
    from .api import agent_bp, experiments_bp
    app.register_blueprint(agent_bp, url_prefix='/api/agent')
    app.register_blueprint(experiments_bp, url_prefix='/api/experiments')

    # Initialise DB once at startup
    from .models.experiment import init_db
    try:
        init_db()
        print('[startup] Database initialised', flush=True)
    except Exception as e:
        print(f'[startup] WARNING: DB init failed: {e}', file=sys.stderr, flush=True)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'project-fly'}

    return app
