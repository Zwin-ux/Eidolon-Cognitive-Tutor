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


async def _call_inference_api(prompt: str) -> str:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if INFERENCE_API_KEY:
        headers["Authorization"] = f"Bearer {INFERENCE_API_KEY}"
    payload = {"inputs": prompt}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(INFERENCE_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    # normalize common shapes
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and "generated_text" in first:
            return first["generated_text"]
        if isinstance(first, str):
            return first
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    return str(data)


def _demo_reply(prompt: str) -> str:
    p = (prompt or "").strip()
    if not p:
        return "Please enter a question for the demo tutor."
    if "explain" in p.lower() or "what is" in p.lower():
        return f"Demo answer (short):\n\nHere's a concise explanation for: '{p}'.\n\n[This is demo-mode output. Configure INFERENCE_API_URL to use a real model.]"
    if "code" in p.lower() or "how to" in p.lower():
        return (
            f"Demo answer (steps):\n\n1) Understand the problem: '{p}'.\n2) Break it down into smaller steps.\n3) Implement and test.\n\n[Demo-mode response]."
        )
    return f"Demo reply: I understood your prompt '{p}'. This is a demo response. Set INFERENCE_API_URL to enable real model responses."


def ask_sync(question: str) -> str:
    if INFERENCE_API_URL:
        # call remote inference API synchronously via httpx (simple blocking call)
        try:
            resp = httpx.post(INFERENCE_API_URL, json={"inputs": question}, headers={"Authorization": f"Bearer {INFERENCE_API_KEY}"} if INFERENCE_API_KEY else {"Content-Type": "application/json"}, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
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
            return f"Inference API error: {e}"

    if DEMO_MODE:
        return _demo_reply(question)

    # Fallback to local model for developers who have the weights available
    try:
        from cognitive_llm import CognitiveLLM

        tutor = CognitiveLLM()
        return tutor.generate(question)
    except Exception as e:
        return f"Local model unavailable and no INFERENCE_API_URL configured. Error: {e}\n\nSet INFERENCE_API_URL or DEMO_MODE to run safely in hosted environments."


iface = gr.Interface(
    fn=ask_sync,
    inputs=gr.Textbox(label="Ask the tutor", placeholder="Enter your question here"),
    outputs=gr.Textbox(label="Tutor response"),
    title="Eidolon Cognitive Tutor",
    description="Retrieval-augmented cognitive tutoring powered by Qwen3."
)


if __name__ == "__main__":
    iface.launch()
