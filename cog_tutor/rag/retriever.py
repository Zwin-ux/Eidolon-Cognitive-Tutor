import hashlib
import sqlite3
from typing import List, Dict, Any, Tuple
from .knowledge_base import KnowledgeBase
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeRetriever:
    """Retrieval-augmented generation system for educational content."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self._build_index()
    
    def _build_index(self):
        """Build TF-IDF index for semantic search."""
        # Get all knowledge items
        all_items = []
        with sqlite3.connect(self.kb.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM knowledge_items")
            for row in cursor.fetchall():
                all_items.append({
                    "id": row["id"],
                    "skill": row["skill"],
                    "content": row["content"],
                    "facts": eval(row["facts"]),
                    "difficulty": row["difficulty"]
                })
        
        self.all_items = all_items
        
        # Build corpus for vectorization
        corpus = []
        for item in self.all_items:
            text = f"{item['skill']} {item['content']} {' '.join(item['facts'])}"
            corpus.append(text)
        
        # Fit vectorizer
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
    
    def retrieve_relevant_knowledge(self, query: str, skill: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge items for a query."""
        # If skill is specified, prioritize skill-specific items
        if skill:
            skill_items = self.kb.retrieve_by_skill(skill, limit=top_k)
            if len(skill_items) >= top_k:
                return skill_items[:top_k]
        
        # Use semantic search
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top-k most similar items
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                item = self.all_items[idx].copy()
                item["relevance_score"] = float(similarities[idx])
                results.append(item)
        
        return results
    
    def get_facts_for_explanation(self, question: str, user_answer: str, solution: str) -> List[str]:
        """Extract relevant facts for explaining a problem."""
        query = f"{question} {solution}"
        relevant_items = self.retrieve_relevant_knowledge(query, top_k=5)
        
        # Collect and deduplicate facts
        all_facts = []
        seen_facts = set()
        
        for item in relevant_items:
            for fact in item["facts"]:
                if fact not in seen_facts:
                    all_facts.append(fact)
                    seen_facts.add(fact)
        
        return all_facts[:5]  # Return top 5 most relevant facts
    
    def get_contextual_hints(self, question: str, hint_level: int = 1) -> List[str]:
        """Generate contextual hints based on retrieved knowledge."""
        relevant_items = self.retrieve_relevant_knowledge(question, top_k=3)
        
        if hint_level == 1:
            # Conceptual nudge
            hints = [item["content"].split('.')[0] + "." for item in relevant_items]
        elif hint_level == 2:
            # Procedural cue
            hints = [item["content"] for item in relevant_items]
        else:
            # Near-solution scaffold
            hints = []
            for item in relevant_items:
                for fact in item["facts"]:
                    if "step" in fact.lower() or "method" in fact.lower():
                        hints.append(fact)
        
        return hints[:3]
    
    def get_explanation_with_citations(self, question: str, user_answer: str, solution: str) -> Dict[str, Any]:
        """Generate explanation with knowledge citations."""
        facts = self.get_facts_for_explanation(question, user_answer, solution)
        relevant_items = self.retrieve_relevant_knowledge(f"{question} {solution}", top_k=3)
        
        return {
            "facts": facts,
            "citations": [{"id": item["id"], "skill": item["skill"]} for item in relevant_items],
            "sources": [item["content"] for item in relevant_items]
        }
