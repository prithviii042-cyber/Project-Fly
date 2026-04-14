"""Entry point for the Project Fly backend."""

import os
import sys

print('[startup] Starting Project Fly backend...', flush=True)

try:
    from app import create_app
    from app.config import Config
except Exception as e:
    print(f'[startup] FATAL import error: {e}', file=sys.stderr, flush=True)
    raise

app = create_app()

if __name__ == '__main__':
    errors = Config.validate()
    if errors:
        print('[startup] Configuration warnings:', flush=True)
        for e in errors:
            print(f'  - {e}', flush=True)

    # Railway (and most PaaS) sets PORT dynamically — always read from env
    port = int(os.environ.get('PORT', 5001))
    print(f'[startup] Listening on 0.0.0.0:{port}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
