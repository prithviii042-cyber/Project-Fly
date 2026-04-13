# Project Fly

AI agent builder with a prompt-driven development workflow.

## Stack

- **Frontend**: Vue.js 3 + Vite → deployed on Netlify
- **Backend**: Python Flask + Anthropic Claude → deployed on Railway
- **LLM**: Claude Sonnet 4.6 (`claude-sonnet-4-6`)

## Local Development

1. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`
2. Install and run:
   ```bash
   npm install        # root dev tools
   npm run dev        # starts backend (port 5001) + frontend (port 3000)
   ```

## Deployment

### Backend (Railway)
1. Connect this repo in Railway → Dockerfile deployment
2. Set environment variables: `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `CORS_ORIGINS`

### Frontend (Netlify)
1. Connect this repo in Netlify — it will pick up `netlify.toml` automatically
2. In `netlify.toml`, replace `YOUR_RAILWAY_URL` with your Railway service URL
3. Set env var `VITE_API_BASE_URL` = Railway URL in Netlify site settings

### GitHub Secret
Add `RAILWAY_BACKEND_URL` as a GitHub Actions secret for the smoke-test job.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/agent/chat` | Single-turn chat with Claude |
| POST | `/api/agent/stream` | Streaming chat (Server-Sent Events) |
