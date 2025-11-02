import gradio as gr
from cognitive_llm import CognitiveLLM

# Initialize the cognitive tutor
_tutor = CognitiveLLM()


def ask(question: str) -> str:
    """Generate a response from the cognitive tutor."""
    if not question or not question.strip():
        return "Please enter a question for the tutor."
    return _tutor.generate(question.strip())


iface = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(label="Ask the tutor", placeholder="Enter your question here"),
    outputs=gr.Textbox(label="Tutor response"),
    title="Eidolon Cognitive Tutor",
    description="Retrieval-augmented cognitive tutoring powered by Qwen3."
)


if __name__ == "__main__":
    iface.launch()
