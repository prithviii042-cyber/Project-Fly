"""Entry point for the Project Fly backend."""

from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    errors = Config.validate()
    if errors:
        print('Configuration warnings:')
        for e in errors:
            print(f'  - {e}')

    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
