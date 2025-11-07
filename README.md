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

# Eidolon — interactive tutor demo

This repository contains a small demo app: a static frontend plus a lightweight serverless API that accepts prompts and returns text responses. The project is organized so you can run a demo locally or deploy the static site and API to Vercel.

This README focuses only on the repository's functions and how to run or present it.

## Quick start (demo mode)

1. Install the developer dependencies (lightweight):

```powershell
pip install -r dev-requirements.txt
```

2. Start the demo (PowerShell):

```powershell
.\scripts\run_demo.ps1
```

The demo runs the local UI and API in `DEMO_MODE`, which returns canned responses suitable for public demos.

## Files and functionality

- `public/index.html` — static single-page UI used for demos.
- `api/ask.py` — serverless API endpoint (FastAPI). It forwards requests to an external service when configured, or returns demo responses when `DEMO_MODE` is enabled.
- `app.py` — local Gradio UI that can run in demo mode or proxy to an external service.
- `cognitive_llm.py` — local model loader and interface (for development only; not required for demos).
- `vercel.json` — Vercel configuration (serves `public/` and `api/`).
- `dev-requirements.txt` — lightweight packages used for running tests and the demo without heavy ML libraries.
- `tests/test_api.py` — a small test that verifies the API demo behavior.
- `.github/workflows/ci.yml` — CI: installs `dev-requirements.txt`, runs tests and lint checks.

## Deploying (Vercel)

The repo includes a `vercel.json` to serve the static site and Python serverless functions. To publish a public demo on Vercel:

1. (Optional) Configure environment variables in the Vercel project settings:

   - `DEMO_MODE=1` — run demo-mode responses without external services.
   - `INFERENCE_API_URL` / `INFERENCE_API_KEY` — optional: if you have an external text-generation service, set these to enable real responses.

2. Deploy with the Vercel CLI or the Vercel dashboard. From the repo root:

```powershell
vercel --prod
```

When `DEMO_MODE` is set, the deployed site will return safe demo responses and requires no external services or keys.

## Testing and CI

Run the lightweight tests locally after installing dev dependencies:

```powershell
pip install -r dev-requirements.txt
pytest -q
```

CI is configured to run the same test and lint steps on push/pull requests.

## Presenting this repository

For public presentations or a minimal demo, set `DEMO_MODE=1` and deploy to Vercel or run the local demo script. The UI and API are designed so reviewers can interact with the demo without installing large models or sharing API keys.

If you want the README even shorter or want me to remove files not needed for the public demo, tell me which files to remove and I will prepare a clean branch for presentation.
