from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import time
import uuid
from collections import defaultdict
from typing import Optional
from .history import save_conversation, get_conversation_history

app = FastAPI(title="Eidolon Tutor API", version="0.2.0")

# CORS for local development and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiter (IP-based)
_rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds


def check_rate_limit(client_ip: str) -> bool:
    """Simple sliding window rate limiter."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    # Clean old requests
    _rate_limit_store[client_ip] = [
        req_time for req_time in _rate_limit_store[client_ip] if req_time > window_start
    ]
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    _rate_limit_store[client_ip].append(now)
    return True


class AskIn(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    session_id: Optional[str] = None  # for conversation history


class AskOut(BaseModel):
    result: Optional[str] = None
    error: Optional[str] = None
    source: str = "demo"  # "demo", "inference", or "error"
    session_id: str = ""  # returned session ID


def get_demo_response(prompt: str) -> str:
    """Generate deterministic demo responses."""
    p = prompt.strip().lower()
    if not p:
        return "Please enter a question for the demo tutor."
    if "explain" in p or "what is" in p:
        return f"**Demo Explanation:**\n\nHere's a concise explanation for your question: *\"{prompt}\"*.\n\n[Demo mode active. Configure `INFERENCE_API_URL` to use a real model.]"
    if "code" in p or "how to" in p or "implement" in p:
        return f"**Demo Steps:**\n\n1. Understand the problem: *\"{prompt}\"*\n2. Break it down into smaller steps\n3. Implement and test\n4. Iterate and refine\n\n[Demo-mode response]"
    if "compare" in p or "difference" in p:
        return f"**Demo Comparison:**\n\nKey differences related to *\"{prompt}\"*:\n- Point A vs Point B\n- Tradeoffs and use cases\n\n[Demo mode]"
    # Generic fallback
    return f"**Demo Response:**\n\nI understood your prompt: *\"{prompt}\"*.\n\nThis is a demo response showing how the tutor would reply. Set `INFERENCE_API_URL` to enable real model inference."


async def call_inference_api(
    prompt: str, api_url: str, api_key: Optional[str], max_tokens: int, temperature: float
) -> dict:
    """Call external inference API with retries and timeout."""
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": temperature},
    }
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Retry logic: 2 attempts with exponential backoff
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                # Normalize response
                if isinstance(data, dict) and "error" in data:
                    return {"error": data.get("error"), "source": "inference"}
                if isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    if isinstance(first, dict) and "generated_text" in first:
                        return {"result": first["generated_text"], "source": "inference"}
                    if isinstance(first, str):
                        return {"result": first, "source": "inference"}
                if isinstance(data, dict) and "generated_text" in data:
                    return {"result": data["generated_text"], "source": "inference"}
                return {"result": str(data), "source": "inference"}

        except httpx.HTTPError as e:
            if attempt == 0:
                await httpx.AsyncClient().aclose()
                time.sleep(1)  # backoff
                continue
            return {"error": f"Inference API failed after retries: {str(e)}", "source": "error"}

    return {"error": "Inference API failed", "source": "error"}


@app.post("/", response_model=AskOut)
async def ask(in_data: AskIn, request: Request):
    """
    Main API endpoint: accepts a prompt and returns a response.
    
    Supports:
    - Demo mode (DEMO_MODE=1): returns canned responses
    - External inference (INFERENCE_API_URL set): calls hosted model
    - Rate limiting (configurable via RATE_LIMIT_REQUESTS/RATE_LIMIT_WINDOW)
    - Conversation history (optional session_id)
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    # Generate or use provided session ID
    session_id = in_data.session_id or str(uuid.uuid4())

    api_url = os.environ.get("INFERENCE_API_URL")
    api_key = os.environ.get("INFERENCE_API_KEY")
    demo_mode = os.environ.get("DEMO_MODE", "0").lower() in ("1", "true", "yes")

    # Demo mode
    if demo_mode or not api_url:
        result_text = get_demo_response(in_data.prompt)
        save_conversation(session_id, in_data.prompt, result_text, "demo")
        return AskOut(result=result_text, source="demo", session_id=session_id)

    # Call inference API
    result = await call_inference_api(
        in_data.prompt, api_url, api_key, in_data.max_tokens, in_data.temperature
    )
    
    # Save to history
    if result.get("result"):
        save_conversation(session_id, in_data.prompt, result["result"], result.get("source", "inference"))
    
    return AskOut(**result, session_id=session_id)


@app.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Retrieve conversation history for a session."""
    return {"session_id": session_id, "history": get_conversation_history(session_id, limit)}
