from typing import Optional, List
from cognitive_llm import CognitiveLLM

class QwenAdapter:
    def __init__(self, model_name: str = "Qwen/Qwen3-7B-Instruct"):
        # Store model name for lazy initialization
        self.model_name = model_name
        self.client = None

    def _initialize_client(self):
        # Lazy initialization of the CognitiveLLM client
        if self.client is None:
            self.client = CognitiveLLM(model_name=self.model_name)

    def generate(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
        stop: Optional[List[str]] = None,
        seed: Optional[int] = None,
    ) -> str:
        # Initialize client if not already done
        self._initialize_client()
        
        # Compose a strict prompt: JSON only, no commentary
        prompt = f"System: {system}\nReturn JSON only. No commentary.\nInput: {user}"
        
        # Use the existing generate method with appropriate parameters
        text = self.client.generate(
            prompt,
            max_new_tokens=max_tokens,
            temperature=max(0.1, temperature),
            top_p=0.9,
            do_sample=temperature > 0.3
        )
        
        if stop:
            for s in stop:
                i = text.find(s)
                if i != -1:
                    text = text[:i]
                    break
        return text.strip()
