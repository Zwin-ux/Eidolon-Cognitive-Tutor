---
title: "Eidolon Cognitive Tutor"
emoji: "🧠"
colorFrom: "blue"
colorTo: "purple"
sdk: "gradio"
sdk_version: "4.0.0"
app_file: "app.py"
pinned: false
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

## Usage

1. Run the interactive CLI:
   ```bash
   python cognitive_llm.py
   ```

2. Enter your prompt when prompted with `>>` and press Enter
3. Type 'quit' or 'exit' to exit the program

### Example Usage

```python
from cognitive_llm import CognitiveLLM

# Initialize the LLM
llm = CognitiveLLM()

# Generate text
response = llm.generate(
    "Explain quantum computing in simple terms.",
    max_new_tokens=256,
    temperature=0.7
)
print(response)
```

## Configuration

You can customize the model and generation parameters:

```python
llm = CognitiveLLM(
    model_name="Qwen/Qwen3-7B-Instruct",  # Model name or path
    device="cuda"  # 'cuda', 'mps', or 'cpu'
)

# Generate with custom parameters
response = llm.generate(
    "Your prompt here",
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)
```

## Note

- First run will download the model weights (several GB)
- A CUDA-compatible GPU is recommended for reasonable performance
- Ensure you have sufficient disk space for the model weights
- Internet connection is required for the initial download
