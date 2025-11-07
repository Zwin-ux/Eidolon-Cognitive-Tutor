import gradio as gr
import os
import httpx
from typing import Optional

# If an external inference endpoint is configured, the Gradio app will proxy to it.
# Otherwise, if DEMO_MODE is set, the app will run in safe demo mode that does not
# attempt to load large model weights. When neither is set, the app will try to
# instantiate the local CognitiveLLM (for developers running locally with the model).
INFERENCE_API_URL = os.getenv("INFERENCE_API_URL")
INFERENCE_API_KEY = os.getenv("INFERENCE_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "0").lower() in ("1", "true", "yes")


def _demo_reply(prompt: str) -> str:
    """Generate deterministic demo responses."""
    p = (prompt or "").strip()
    if not p:
        return "Please enter a question for the demo tutor."
    if "explain" in p.lower() or "what is" in p.lower():
        return f"**Demo Explanation:**\n\nHere's a concise explanation for your question: *\"{p}\"*.\n\n[Demo mode active. Configure `INFERENCE_API_URL` to use a real model.]"
    if "code" in p.lower() or "how to" in p.lower() or "implement" in p.lower():
        return f"**Demo Steps:**\n\n1. Understand the problem: *\"{p}\"*\n2. Break it down into smaller steps\n3. Implement and test\n4. Iterate and refine\n\n[Demo-mode response]"
    if "compare" in p.lower() or "difference" in p.lower():
        return f"**Demo Comparison:**\n\nKey differences related to *\"{p}\"*:\n- Point A vs Point B\n- Tradeoffs and use cases\n\n[Demo mode]"
    return f"**Demo Response:**\n\nI understood your prompt: *\"{p}\"*.\n\nThis is a demo response showing how the tutor would reply. Set `INFERENCE_API_URL` to enable real model inference."


def ask_sync(question: str, mode: str = "standard", difficulty: int = 3, persona: str = "friendly") -> str:
    """Handle question answering with learning modes, demo mode, inference API, or local model fallback."""
    if not question or not question.strip():
        return "Please enter a question for the tutor."
    
    question = question.strip()
    
    # Try inference API first if configured
    if INFERENCE_API_URL:
        try:
            headers = {"Content-Type": "application/json"}
            if INFERENCE_API_KEY:
                headers["Authorization"] = f"Bearer {INFERENCE_API_KEY}"
            
            resp = httpx.post(
                INFERENCE_API_URL,
                json={
                    "prompt": question,
                    "mode": mode,
                    "difficulty": difficulty,
                    "persona": persona
                },
                headers=headers,
                timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Normalize response
            if isinstance(data, dict) and "result" in data:
                return data["result"]
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"]
                if isinstance(first, str):
                    return first
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            return str(data)
        except Exception as e:
            return f"⚠️ Inference API error: {e}\n\nFalling back to demo mode..."

    # Demo mode with learning modes support
    if DEMO_MODE:
        mode_emoji = {
            "socratic": "🤔",
            "eli5": "👶",
            "technical": "🔬",
            "analogy": "🎭",
            "code": "💻"
        }.get(mode, "📚")
        
        persona_prefix = {
            "friendly": "Hey there! 😊",
            "strict": "Attention, student.",
            "enthusiastic": "OMG this is so cool! 🎉",
            "professional": "Greetings.",
            "playful": "Hehe, ready to learn? 😄"
        }.get(persona, "Hello!")
        
        base_reply = _demo_reply(question)
        
        return (
            f"{mode_emoji} **{mode.upper()} Mode** | Difficulty: {difficulty}/5 | Persona: {persona}\n\n"
            f"{persona_prefix}\n\n"
            f"{base_reply}\n\n"
            "---\n"
            "💡 **Learning Mode Active**: This demo shows how different modes adapt content!\n"
            "Try other modes like Socratic (questions), ELI5 (simple), Technical (deep), Analogy (metaphors), or Code (examples)."
        )

    # Fallback to local model (only for developers with model weights)
    try:
        from cognitive_llm import CognitiveLLM
        tutor = CognitiveLLM()
        return tutor.generate(question)
    except Exception as e:
        return f"❌ Local model unavailable and no `INFERENCE_API_URL` configured.\n\nError: {e}\n\n**To fix this:**\n- Set `DEMO_MODE=1` for demo responses, or\n- Set `INFERENCE_API_URL` to use a hosted inference endpoint"


iface = gr.Interface(
    fn=ask_sync,
    inputs=[
        gr.Textbox(
            label="Ask the tutor",
            placeholder="Enter your question here (e.g., 'Explain Newton's laws')",
            lines=3
        ),
        gr.Radio(
            choices=["standard", "socratic", "eli5", "technical", "analogy", "code"],
            label="📚 Learning Mode",
            value="standard",
            info="Choose how you want to learn: Socratic (questions), ELI5 (simple), Technical (deep), Analogy (metaphors), Code (examples)"
        ),
        gr.Slider(
            minimum=1,
            maximum=5,
            step=1,
            value=3,
            label="🎯 Difficulty Level",
            info="1 = Beginner, 5 = Expert"
        ),
        gr.Radio(
            choices=["friendly", "strict", "enthusiastic", "professional", "playful"],
            label="🎭 Tutor Persona",
            value="friendly",
            info="Pick your tutor's personality style"
        )
    ],
    outputs=gr.Textbox(label="Tutor response", lines=12),
    title="🧠 Eidolon Cognitive Tutor",
    description="""
    **Interactive AI Tutor with Multiple Learning Modes**
    
    Choose your learning style, adjust difficulty, and pick your tutor's personality!
    Running in demo mode by default (set `DEMO_MODE=1` or configure `INFERENCE_API_URL` for real inference).
    """,
    examples=[
        ["Explain Newton's laws in simple terms", "eli5", 2, "friendly"],
        ["How do I implement a binary search in Python?", "code", 3, "professional"],
        ["Compare supervised vs unsupervised learning", "technical", 4, "enthusiastic"],
        ["What is the difference between HTTP and HTTPS?", "analogy", 2, "playful"]
    ],
    theme="soft"
)


if __name__ == "__main__":
    iface.launch()
