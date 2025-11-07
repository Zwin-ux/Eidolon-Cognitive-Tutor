"""Lightweight paper database and lookup helpers for research citations."""
from typing import List, Dict

# Minimal curated set of influential papers to cite in the demo. Add more as needed.
RESEARCH_PAPERS: Dict[str, Dict] = {
    "attention": {
        "id": "attention",
        "title": "Attention Is All You Need",
        "authors": "Vaswani et al.",
        "year": 2017,
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/1706.03762",
        "summary": "Introduced the Transformer architecture using self-attention; foundational for modern LLMs."
    },
    "rag": {
        "id": "rag",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP",
        "authors": "Lewis et al.",
        "year": 2020,
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/2005.11401",
        "summary": "Combines retrieval with generation to ground answers in external documents."
    },
    "tot": {
        "id": "tot",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "authors": "Yao et al.",
        "year": 2023,
        "venue": "ArXiv/NeurIPS",
        "url": "https://arxiv.org/abs/2305.10601",
        "summary": "Explores branching reasoning strategies to improve complex problem solving."
    },
    "maml": {
        "id": "maml",
        "title": "Model-Agnostic Meta-Learning for Fast Adaptation",
        "authors": "Finn et al.",
        "year": 2017,
        "venue": "ICML",
        "url": "https://arxiv.org/abs/1703.03400",
        "summary": "Meta-learning method for quick adaptation to new tasks with few examples."
    },
    "uncertainty": {
        "id": "uncertainty",
        "title": "Uncertainty in Deep Learning",
        "authors": "Gal",
        "year": 2016,
        "venue": "PhD Thesis / Review",
        "url": "https://arxiv.org/abs/1708.07250",
        "summary": "Surveys Bayesian and practical approaches to uncertainty estimation in neural networks."
    },
    "constitutional": {
        "id": "constitutional",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": "Bai et al.",
        "year": 2022,
        "venue": "ArXiv",
        "url": "https://arxiv.org/abs/2212.08073",
        "summary": "Technique for using a set of principles to align model behavior with safety goals."
    },
    "dpo": {
        "id": "dpo",
        "title": "Direct Preference Optimization",
        "authors": "Rafailov et al.",
        "year": 2023,
        "venue": "ArXiv",
        "url": "https://arxiv.org/abs/2305.19343",
        "summary": "Preference optimization method that avoids separate reward model training."
    },
    "gnn": {
        "id": "gnn",
        "title": "A Comprehensive Survey on Graph Neural Networks",
        "authors": "Zhou et al.",
        "year": 2020,
        "venue": "IEEE Transactions",
        "url": "https://arxiv.org/abs/1901.00596",
        "summary": "Survey of graph neural network models and applications, relevant for knowledge graphs."
    },
    "clip": {
        "id": "clip",
        "title": "Learning Transferable Visual Models From Natural Language Supervision (CLIP)",
        "authors": "Radford et al.",
        "year": 2021,
        "venue": "ICML",
        "url": "https://arxiv.org/abs/2103.00020",
        "summary": "Demonstrates strong zero-shot transfer for image-text tasks using contrastive learning."
    },
    "dpr": {
        "id": "dpr",
        "title": "Dense Passage Retrieval for Open-Domain Question Answering",
        "authors": "Karpukhin et al.",
        "year": 2020,
        "venue": "EMNLP",
        "url": "https://arxiv.org/abs/2004.04906",
        "summary": "Dense retrieval technique that improves recall for RAG pipelines."
    }
}


def get_relevant_papers(prompt: str = "", mode: str = "standard", top_k: int = 3) -> List[Dict]:
    """Return a small list of relevant papers for a prompt or mode.

    Heuristic matching: checks for keywords in the prompt and preferred mode
    to return a concise, curated set of citations suitable for display in the UI.
    """
    prompt_l = (prompt or "").lower()
    keys = set()

    # Mode-based preferences
    if mode == "socratic":
        keys.add("tot")
    if mode == "technical":
        keys.add("attention")
        keys.add("dpr")
    if mode == "code" or "implement" in prompt_l:
        keys.add("dpr")
        keys.add("rag")
    if mode == "analogy":
        keys.add("attention")
    if mode == "eli5":
        keys.add("constitutional")

    # Keyword heuristics
    if any(k in prompt_l for k in ["attention", "transformer", "self-attention"]):
        keys.add("attention")
    if any(k in prompt_l for k in ["retrieval", "rag", "search", "docs", "sources"]):
        keys.add("rag")
        keys.add("dpr")
    if any(k in prompt_l for k in ["reasoning", "tree", "thought", "chain of thought"]):
        keys.add("tot")
    if any(k in prompt_l for k in ["meta", "maml", "adapt", "few-shot"]):
        keys.add("maml")
    if any(k in prompt_l for k in ["uncertainty", "confidence", "calibration"]):
        keys.add("uncertainty")
    if any(k in prompt_l for k in ["safety", "harm", "alignment", "constitutional"]):
        keys.add("constitutional")
    if any(k in prompt_l for k in ["graph", "knowledge graph", "gnn"]):
        keys.add("gnn")
    if any(k in prompt_l for k in ["image", "vision", "clip"]):
        keys.add("clip")

    # If no keys were found, return general high-impact papers
    if not keys:
        keys.update(["attention", "rag", "dpr"])

    # Build list preserving some priority: attention -> rag -> dpr -> others
    priority = ["attention", "rag", "dpr", "tot", "maml", "uncertainty", "constitutional", "dpo", "gnn", "clip"]
    selected = [RESEARCH_PAPERS[k] for k in priority if k in keys and k in RESEARCH_PAPERS]

    return selected[:top_k]
