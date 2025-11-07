from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import httpx

app = FastAPI()


class AskIn(BaseModel):
    prompt: str


@app.post("/")
async def ask(in_data: AskIn, request: Request):
    """Simple proxy to a hosted inference API.

    Expects environment variables:
      - INFERENCE_API_URL: full URL of the model inference endpoint (e.g. Hugging Face Inference API)
      - INFERENCE_API_KEY: optional bearer token for auth

    This function is intentionally lightweight and delegates heavy model work to a hosted service
    because serverless functions are not suitable for large local models.
    """
    api_url = os.environ.get("INFERENCE_API_URL")
    api_key = os.environ.get("INFERENCE_API_KEY")
    demo_mode = os.environ.get("DEMO_MODE", "0").lower() in ("1", "true", "yes")

    if not api_url:
        if demo_mode:
            # Return a deterministic demo-style reply so the app can be shown without a backend
            prompt = in_data.prompt.strip()
            # Simple heuristic demo replies
            if not prompt:
                return {"result": "Please enter a question for the demo tutor."}
            if "explain" in prompt.lower() or "what is" in prompt.lower():
                return {"result": f"Demo answer (short):\n\nHere's a concise explanation for: '{prompt}'.\n\n[This is demo-mode output. Configure INFERENCE_API_URL to use a real model.]"}
            if "code" in prompt.lower() or "how to" in prompt.lower():
                return {"result": f"Demo answer (steps):\n\n1) Understand the problem: '{prompt}'.\n2) Break it down into smaller steps.\n3) Implement and test.\n\n[Demo-mode response]."}
            # Generic echo-like fallback
            return {"result": f"Demo reply: I understood your prompt '{prompt}'. This is a demo response. Set INFERENCE_API_URL to enable real model responses."}
        return {"error": "INFERENCE_API_URL not configured. Set environment variable or enable DEMO_MODE."}

    payload = {"inputs": in_data.prompt}
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            return {"error": "Inference request failed", "detail": str(e)}

    data = resp.json()

    # Try to normalize common inference API responses
    if isinstance(data, dict) and "error" in data:
        return {"error": data.get("error")}

    # Hugging Face Inference API often returns a list of {"generated_text": ...}
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and "generated_text" in first:
            return {"result": first["generated_text"]}
        # some models return plain strings in a list
        if isinstance(first, str):
            return {"result": first}

    # fallback: return raw JSON as string
    return {"result": data}
