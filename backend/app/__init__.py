"""
Project Fly — Flask app factory
"""

import os
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

    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'project-fly'}

    return app
