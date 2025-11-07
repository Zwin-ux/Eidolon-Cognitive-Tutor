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
from .papers import get_relevant_papers

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
    mode: Optional[str] = "standard"  # learning mode: standard, socratic, eli5, technical, analogy, code
    difficulty: Optional[int] = 3  # 1-5 difficulty scale
    persona: Optional[str] = "friendly"  # friendly, strict, enthusiastic, professional


class AskOut(BaseModel):
    result: Optional[str] = None
    error: Optional[str] = None
    source: str = "demo"  # "demo", "inference", or "error"
    session_id: str = ""  # returned session ID
    # Optional research data to support the response (citations, RAG pipeline, attention, etc.)
    research_data: Optional[dict] = None


def get_demo_response(prompt: str, mode: str = "standard", difficulty: int = 3, persona: str = "friendly") -> str:
    """Generate deterministic demo responses with learning modes and personalization."""
    p = prompt.strip().lower()
    if not p:
        return "Please enter a question for the demo tutor."
    
    # Persona prefixes
    persona_styles = {
        "friendly": "😊 ",
        "strict": "📚 ",
        "enthusiastic": "🎉 ",
        "professional": "🎓 ",
        "playful": "🎮 "
    }
    prefix = persona_styles.get(persona, "")
    
    # Mode-specific responses
    if mode == "socratic":
        return f"{prefix}**Socratic Mode** 🤔\n\nGreat question! Let me guide you with some questions:\n\n1. What do you already know about *\"{prompt}\"*?\n2. Can you think of a similar concept you're familiar with?\n3. What would happen if we changed one key variable?\n4. How would you explain this to someone younger?\n\n[Demo mode - these questions would adapt based on your actual responses]"
    
    elif mode == "eli5":
        return f"{prefix}**ELI5 Mode** 👶\n\nOkay, imagine *\"{prompt}\"* like this:\n\nThink of it like building with LEGO blocks. Each block is a simple piece, but when you put them together in the right way, you can build amazing things!\n\n[Demo mode - real responses would use age-appropriate analogies]"
    
    elif mode == "technical":
        difficulty_markers = ["Beginner", "Intermediate", "Advanced", "Expert", "Research-Level"]
        level = difficulty_markers[min(difficulty - 1, 4)]
        return f"{prefix}**Technical Deep-Dive** 🔬 (Level: {level})\n\n**Topic:** {prompt}\n\n**Core Concepts:**\n- Fundamental principles and definitions\n- Mathematical/logical foundations\n- Implementation details and edge cases\n- Performance considerations\n- Common pitfalls and best practices\n\n[Demo mode - depth would match difficulty level {difficulty}/5]"
    
    elif mode == "analogy":
        analogies = [
            "a restaurant kitchen (preparation → cooking → serving)",
            "a postal system (sending → routing → delivery)",
            "a factory assembly line (input → processing → output)",
            "a team sport (strategy → execution → scoring)"
        ]
        import random
        random.seed(len(prompt))  # deterministic
        analogy = random.choice(analogies)
        return f"{prefix}**Analogy Master** 🎭\n\nLet me explain *\"{prompt}\"* using an analogy:\n\nIt's like {analogy}.\n\nEach step has a purpose, and when they work together, magic happens!\n\n[Demo mode - analogies would be carefully crafted for each topic]"
    
    elif mode == "code":
        return f"{prefix}**Code Mentor** 💻\n\n```python\n# Pseudocode for: {prompt}\n\nclass Solution:\n    def solve(self, problem):\n        # Step 1: Understand the requirements\n        requirements = self.analyze(problem)\n        \n        # Step 2: Break down into smaller pieces\n        components = self.decompose(requirements)\n        \n        # Step 3: Implement each piece\n        for component in components:\n            self.implement(component)\n        \n        # Step 4: Test and refine\n        return self.test_and_validate()\n```\n\n[Demo mode - would provide working code examples]"
    
    # Standard mode (fallback)
    if "explain" in p or "what is" in p:
        return f"{prefix}**Standard Explanation:**\n\nHere's a concise explanation for *\"{prompt}\"*:\n\n• **Key Point 1:** Main concept overview\n• **Key Point 2:** Why it matters\n• **Key Point 3:** How it's used in practice\n\n[Demo mode - set DEMO_MODE=1 or configure INFERENCE_API_URL]"
    
    if "code" in p or "how to" in p or "implement" in p:
        return f"{prefix}**Implementation Guide:**\n\n**Problem:** {prompt}\n\n**Approach:**\n1. Define the requirements clearly\n2. Choose the right data structures\n3. Write clean, testable code\n4. Handle edge cases\n\n[Demo mode]"
    
    return f"{prefix}**Response:**\n\nI understood your prompt: *\"{prompt}\"*.\n\nThis is a demo response. Try different **learning modes** (Socratic, ELI5, Technical, Analogy, Code) for varied approaches!\n\n[Demo mode]"


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
        result_text = get_demo_response(in_data.prompt, in_data.mode, in_data.difficulty, in_data.persona)
        save_conversation(session_id, in_data.prompt, result_text, "demo")
        # Attach relevant paper citations for the prompt/mode
        papers = get_relevant_papers(in_data.prompt, in_data.mode)
        return AskOut(result=result_text, source="demo", session_id=session_id, research_data={"papers": papers})

    # Call inference API
    result = await call_inference_api(
        in_data.prompt, api_url, api_key, in_data.max_tokens, in_data.temperature
    )
    
    # Save to history
    if result.get("result"):
        save_conversation(session_id, in_data.prompt, result["result"], result.get("source", "inference"))

    # Add research citations for inference responses as well
    papers = get_relevant_papers(in_data.prompt, in_data.mode)
    out_payload = {**result, "session_id": session_id, "research_data": {"papers": papers}}
    return AskOut(**out_payload)


@app.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Retrieve conversation history for a session."""
    return {"session_id": session_id, "history": get_conversation_history(session_id, limit)}
