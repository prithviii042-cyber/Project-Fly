"""
Configuration — loaded from environment variables.
Copy .env.example to .env and fill in your values for local development.
"""

import os
from dotenv import load_dotenv

# Load .env from project root (../../.env relative to this file)
_root_env = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(_root_env if os.path.exists(_root_env) else None, override=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'project-fly-dev-key')
    # Default DEBUG=False for production; set FLASK_DEBUG=True locally
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Anthropic Claude API
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-6')

    # CORS: comma-separated allowed origins, or '*'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    @classmethod
    def validate(cls):
        errors = []
        if not cls.ANTHROPIC_API_KEY:
            errors.append('ANTHROPIC_API_KEY is not set')
        return errors
