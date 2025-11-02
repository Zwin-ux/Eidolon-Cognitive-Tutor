from typing import Dict, Any, List

class RAGEnhancedPrompts:
    """RAG-enhanced prompts with knowledge grounding and citations."""
    
    @staticmethod
    def item_explanation_with_rag() -> str:
        return """You are a tutoring engine for short-form questions with access to educational knowledge.
        
Given a question, user answer, correct solution, and relevant facts from the knowledge base, explain the reasoning step-by-step in plain language.

IMPORTANT: 
- Use ONLY the provided facts to build your explanation
- Cite the knowledge sources using [Source X] notation
- Output three tiers: Hint, Guided reasoning, Full explanation
- Never invent new facts beyond the provided knowledge

Output JSON with keys: hint, guided, full, citations

Example citation format: "Combine like terms by adding coefficients [Source 1]." """

    @staticmethod
    def hint_generation_with_rag() -> str:
        return """You are generating hints using educational knowledge.
        
Given a question and relevant facts, provide a tiered hint sequence:
- Level 1: conceptual nudge using the facts
- Level 2: procedural cue based on the knowledge  
- Level 3: near-solution scaffold

IMPORTANT:
- Use ONLY the provided facts
- Do not reveal the final answer
- Cite sources using [Source X]

Return JSON with keys '1','2','3' and include citations in each hint."""

    @staticmethod
    def adaptive_question_generation() -> str:
        return """You are generating adaptive practice questions based on student performance.
        
Given a skill, mastery level, and knowledge content, create a question that:
- Matches the student's current mastery (difficulty = 1 - mastery)
- Uses concepts from the provided knowledge
- Includes the correct answer and explanation

Output JSON with keys: question, answer, explanation, difficulty, skill"""

    @staticmethod
    def next_item_selector_with_entropy() -> str:
        return """You are a learning planner using entropy-based scheduling.
        
Given candidate items, student mastery, and recent performance, select the next item that:
- Maximizes expected learning gain (high information gain for uncertain skills)
- Balances review and new content
- Considers prerequisite relationships

Return JSON with keys: item_id, reason, expected_gain, information_gain"""

    @staticmethod
    def mastery_diagnostic_with_irt() -> str:
        return """You are estimating mastery using Item Response Theory (IRT).
        
Given skill performance data including:
- Response accuracy
- Item difficulty
- Response time
- Hint usage

Estimate:
- Theta (ability parameter): -3 to +3 scale
- Standard error of measurement
- Mastery probability (0-1)

Return JSON with keys: theta, sem, mastery, confidence_interval"""

    @staticmethod
    def research_metrics() -> str:
        return """You are calculating research metrics for learning analytics.
        
Given session data, compute:
- Learning gain (pre/post mastery difference)
- Retention rate (accuracy on review items)
- Hint efficiency (hints per correct answer)
- Time on task
- Knowledge transfer (cross-skill performance)

Return JSON with all metrics and statistical significance where applicable."""
