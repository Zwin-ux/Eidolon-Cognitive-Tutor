import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import Optional, Dict, Any

class CognitiveLLM:
    def __init__(self, model_name: str = "Qwen/Qwen3-7B-Instruct", device: str = None):
        """
        Initialize the Cognitive LLM with the specified model.
        
        Args:
            model_name: Name of the model to use (default: Qwen/Qwen3-7B-Instruct)
            device: Device to run the model on ('cuda', 'mps', or 'cpu'). Auto-detects if None.
        """
        self.model_name = model_name
        self.device = device if device else 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        
        print(f"Loading {model_name} on {self.device}...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Load model with 4-bit quantization for efficiency
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2" if self.device.startswith('cuda') else None,
            load_in_4bit=True
        )
        
        # Create text generation pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto"
        )
        
        print(f"Model {model_name} loaded successfully on {self.device}")
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **generation_kwargs
    ) -> str:
        """
        Generate text from a prompt using the loaded model.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more focused, higher = more creative)
            top_p: Nucleus sampling parameter
            **generation_kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        # Format the prompt for Qwen3 chat
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Generate response
        response = self.pipe(
            messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            **generation_kwargs
        )
        
        # Extract and return the generated text
        return response[0]["generated_text"][-1]["content"]


def main():
    # Initialize the cognitive LLM
    llm = CognitiveLLM()
    
    print("\nCognitive LLM initialized. Type 'quit' to exit.")
    print("Enter your prompt:")
    
    # Interactive loop
    while True:
        try:
            user_input = input(">> ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if user_input.strip() == '':
                continue
                
            # Generate response
            response = llm.generate(user_input)
            print("\nResponse:")
            print(response)
            print("\n---\nEnter another prompt or 'quit' to exit:")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue


if __name__ == "__main__":
    main()
