---
title: Eidolon Cognitive Tutor
emoji: 🧠
sdk: gradio
app_file: app.py
license: apache-2.0
---

# Cognitive LLM with Qwen3

A simple implementation of a cognitive language model using Qwen3-7B-Instruct from Hugging Face.

## Features

- Easy-to-use Python interface for Qwen3-7B-Instruct
- Optimized for both CUDA and CPU
- 4-bit quantization for reduced memory usage
- Interactive command-line interface
- Configurable generation parameters

## Prerequisites

- Python 3.8 or higher
- PyTorch (will be installed via requirements.txt)
- CUDA-compatible GPU (recommended) or CPU

## Installation

1. Clone this repository
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

---
title: Eidolon
---

# Eidolon — Interactive Tutor Demo

Production-ready demo application: a static frontend with a serverless API that accepts prompts and returns adaptive responses. Built for easy deployment to Vercel or Hugging Face Spaces with optional inference backend integration.

## ✨ Features

- **Demo Mode**: Safe, deterministic responses for public demos (no API keys or model hosting required)
- **External Inference**: Plug in any hosted inference API (Hugging Face, Replicate, custom endpoints)
- **Conversation History**: SQLite-backed session storage with history retrieval
- **Rate Limiting**: Configurable IP-based rate limiting to prevent abuse
- **Modern UI**: Interactive interface with example prompts, copy buttons, and loading states
- **Retry Logic**: Automatic retries with exponential backoff for inference calls
- **CORS Support**: Cross-origin requests enabled for flexible deployment

## Quick Start (Demo Mode)

Run the demo locally without any external services:

```powershell
# Install lightweight dependencies
pip install -r dev-requirements.txt

# Start demo (PowerShell)
.\scripts\run_demo.ps1

# Or manually
$env:DEMO_MODE = "1"
python app.py
```

Visit the Gradio URL shown in the terminal (usually http://localhost:7860).

## Project Structure

```
├── api/
│   ├── ask.py          # FastAPI serverless endpoint (main API)
│   └── history.py      # Conversation history storage (SQLite)
├── public/
│   ├── index.html      # Static demo UI
│   └── assets/         # UI assets (screenshot, etc.)
├── tests/
│   └── test_api.py     # API tests
├── scripts/
│   └── run_demo.ps1    # Quick demo launcher
├── app.py              # Gradio UI (optional local interface)
├── dev-requirements.txt # Lightweight dependencies (FastAPI, pytest, etc.)
├── vercel.json         # Vercel deployment config
└── README.md
```

## Environment Variables

### Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEMO_MODE` | Enable demo responses (no external services) | `0` | No |
| `INFERENCE_API_URL` | URL of hosted inference endpoint | - | No (required for real inference) |
| `INFERENCE_API_KEY` | Bearer token for inference API | - | No |

### Rate Limiting

| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_REQUESTS` | Max requests per window | `10` |
| `RATE_LIMIT_WINDOW` | Window size in seconds | `60` |

### Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `HISTORY_DB_PATH` | SQLite database path | `conversation_history.db` |

## Deployment

### Vercel (Recommended)

1. Set environment variables in Vercel project settings:
   - `DEMO_MODE=1` (for public demo)
   - Or `INFERENCE_API_URL` + `INFERENCE_API_KEY` (for real inference)

2. Deploy:
```powershell
vercel --prod
```

The `vercel.json` config automatically serves `public/` as static files and `api/*.py` as Python serverless functions.

### Hugging Face Spaces

1. In Space Settings:
   - Set Branch to `demo`
   - Add environment variable: `DEMO_MODE` = `1`
   - Restart the Space

2. Or use the `main` branch with `INFERENCE_API_URL` configured to call a hosted model.

### One-Click Deploy

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/git/external?repository-url=https://github.com/Zwin-ux/Eidolon-Cognitive-Tutor)

## API Reference

### POST `/api/ask`

Request body:
```json
{
  "prompt": "Your question here",
  "max_tokens": 512,
  "temperature": 0.7,
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "result": "Response text",
  "source": "demo",
  "session_id": "generated-or-provided-session-id"
}
```

### GET `/api/history/{session_id}`

Retrieve conversation history for a session.

Response:
```json
{
  "session_id": "...",
  "history": [
    {
      "prompt": "...",
      "response": "...",
      "source": "demo",
      "timestamp": "2025-11-06 12:34:56"
    }
  ]
}
```

## Testing

Run the test suite:

```powershell
pip install -r dev-requirements.txt
pytest -v
```

CI is configured via `.github/workflows/ci.yml` and runs automatically on push/PR.

## Development

### Running with a Real Inference Backend

Set environment variables and run:

```powershell
$env:INFERENCE_API_URL = "https://api-inference.huggingface.co/models/your-org/your-model"
$env:INFERENCE_API_KEY = "hf_..."
python app.py
```

The API will automatically retry failed requests and fall back to demo mode if the backend is unavailable.

### Conversation History

History is stored in SQLite (`conversation_history.db` by default). The UI includes a "View History" button that loads past conversations for the current session.

## Production Recommendations

- **Inference Backend**: Use a hosted service (Hugging Face Inference Endpoints, Replicate, or self-hosted container) rather than loading models in serverless functions.
- **Rate Limiting**: Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` based on your traffic expectations.
- **Caching**: Consider adding Redis or similar for distributed rate limiting in multi-instance deployments.
- **Authentication**: Add API key authentication for production usage (not included in demo).
- **Monitoring**: Set up logging and error tracking (Sentry, Datadog, etc.).

## Current Stage

**Demo-ready for public presentation.** Key milestones:

- ✅ Demo mode with safe, deterministic responses
- ✅ External inference adapter with retries
- ✅ Conversation history storage
- ✅ Rate limiting
- ✅ Modern, interactive UI
- ✅ CI/CD with tests and linting
- ✅ One-click deployment options

## Troubleshooting

### "Repository Not Found" error on Hugging Face Spaces

- **Cause**: The Space is trying to load a model at startup (e.g., `Qwen/Qwen3-7B-Instruct`) but the model is gated, private, or doesn't exist.
- **Fix**: Set `DEMO_MODE=1` in Space environment variables and restart, or switch the Space to use the `demo` branch.

### Rate limit errors in testing

- **Cause**: Default rate limit is 10 requests per 60 seconds.
- **Fix**: Set `RATE_LIMIT_REQUESTS=100` or higher when running local tests.

### Conversation history not persisting

- **Cause**: SQLite database may not be writable in some serverless environments.
- **Fix**: Set `HISTORY_DB_PATH` to a writable location or use an external database (Postgres, etc.) for production.

## Contributing

Issues and PRs welcome at https://github.com/Zwin-ux/Eidolon-Cognitive-Tutor

## License

Apache 2.0
