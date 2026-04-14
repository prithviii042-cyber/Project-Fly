"""Entry point for the Project Fly backend."""

import os
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    errors = Config.validate()
    if errors:
        print('Configuration warnings:')
        for e in errors:
            print(f'  - {e}')

    # Railway (and most PaaS) sets PORT dynamically — always read from env
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
