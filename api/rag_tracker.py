"""RAG Pipeline Tracker - Mock retrieval-augmented generation stages for visualization."""
import hashlib
import time
from typing import List, Dict, Any
import random


class RAGTracker:
    """Tracks and mocks RAG pipeline stages for educational visualization."""
    
    def __init__(self):
        self.stages: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def track_query_encoding(self, query: str) -> Dict[str, Any]:
        """Stage 1: Encode query into embedding space."""
        # Generate deterministic pseudo-embedding from query
        query_hash = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
        random.seed(query_hash)
        
        # Mock 768-dim embedding (show first 10)
        embedding = [round(random.uniform(-1.0, 1.0), 3) for _ in range(768)]
        embedding_preview = embedding[:10]
        
        stage_data = {
            "stage": "query_encoding",
            "query": query,
            "embedding_dim": 768,
            "embedding_preview": embedding_preview,
            "encoding_method": "sentence-transformers (mock)",
            "timestamp_ms": round((time.time() - self.start_time) * 1000, 2)
        }
        self.stages.append(stage_data)
        return stage_data
    
    def track_retrieval(self, query: str, mode: str = "standard") -> Dict[str, Any]:
        """Stage 2: Semantic search over knowledge base."""
        # Mock document retrieval with realistic-looking results
        query_lower = query.lower()
        
        # Generate contextually relevant mock documents
        docs = self._generate_mock_documents(query_lower, mode)
        
        # Simulate semantic similarity scores (deterministic based on query)
        query_hash = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
        random.seed(query_hash)
        
        for doc in docs:
            # Higher scores for better matches
            base_score = random.uniform(0.75, 0.95)
            doc["relevance_score"] = round(base_score, 3)
            doc["retrieval_method"] = "Dense Passage Retrieval (DPR)"
        
        # Sort by relevance
        docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        stage_data = {
            "stage": "retrieval",
            "num_documents_searched": random.randint(50000, 500000),
            "top_k_retrieved": len(docs),
            "documents": docs,
            "search_time_ms": round(random.uniform(8, 25), 2),
            "timestamp_ms": round((time.time() - self.start_time) * 1000, 2)
        }
        self.stages.append(stage_data)
        return stage_data
    
    def track_reranking(self, documents: List[Dict]) -> Dict[str, Any]:
        """Stage 3: Re-rank retrieved documents with cross-encoder."""
        # Simulate re-ranking: slight score adjustments
        reranked = []
        for i, doc in enumerate(documents[:5]):  # Only rerank top 5
            old_score = doc.get("relevance_score", 0.8)
            # Some docs improve, some decrease
            adjustment = random.uniform(-0.08, 0.12)
            new_score = min(0.99, max(0.60, old_score + adjustment))
            
            reranked.append({
                "title": doc["title"],
                "snippet": doc["snippet"],
                "old_score": old_score,
                "new_score": round(new_score, 3),
                "score_change": round(adjustment, 3),
                "reranker": "cross-encoder/ms-marco-MiniLM (mock)"
            })
        
        # Sort by new score
        reranked.sort(key=lambda x: x["new_score"], reverse=True)
        
        stage_data = {
            "stage": "reranking",
            "reranked_documents": reranked,
            "reranking_time_ms": round(random.uniform(15, 40), 2),
            "timestamp_ms": round((time.time() - self.start_time) * 1000, 2)
        }
        self.stages.append(stage_data)
        return stage_data
    
    def track_generation(self, query: str, context_docs: List[Dict], response: str) -> Dict[str, Any]:
        """Stage 4: Generate response with attribution."""
        # Extract potential citations from top docs
        citations = []
        for i, doc in enumerate(context_docs[:3], 1):
            citations.append({
                "id": i,
                "title": doc.get("title", "Source"),
                "relevance": doc.get("new_score", doc.get("relevance_score", 0.8)),
                "used": random.choice([True, True, False])  # Most are used
            })
        
        stage_data = {
            "stage": "generation",
            "context_length": sum(len(d.get("snippet", "")) for d in context_docs),
            "num_context_docs": len(context_docs),
            "response_length": len(response),
            "citations": citations,
            "generation_time_ms": round(random.uniform(200, 800), 2),
            "timestamp_ms": round((time.time() - self.start_time) * 1000, 2)
        }
        self.stages.append(stage_data)
        return stage_data
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get complete pipeline visualization data."""
        total_time = round((time.time() - self.start_time) * 1000, 2)
        return {
            "stages": self.stages,
            "total_time_ms": total_time,
            "pipeline_type": "RAG (Retrieval-Augmented Generation)",
            "components": [
                "Query Encoder (sentence-transformers)",
                "Vector Database (FAISS/approximate NN)",
                "Re-ranker (cross-encoder)",
                "Generator (LLM with context)"
            ]
        }
    
    def _generate_mock_documents(self, query: str, mode: str) -> List[Dict[str, str]]:
        """Generate contextually relevant mock documents based on query keywords."""
        # Database of mock document templates
        doc_templates = {
            "default": [
                {
                    "title": "Introduction to {topic}",
                    "snippet": "This comprehensive guide covers the fundamentals of {topic}, including key concepts, practical applications, and real-world examples.",
                    "source": "Educational Resources Database",
                    "citations": random.randint(50, 500)
                },
                {
                    "title": "Advanced Concepts in {topic}",
                    "snippet": "Exploring advanced techniques and methodologies in {topic}, with detailed analysis of current research and best practices.",
                    "source": "Academic Journal Repository",
                    "citations": random.randint(100, 1000)
                },
                {
                    "title": "{topic}: A Practical Guide",
                    "snippet": "Step-by-step tutorial demonstrating how to apply {topic} concepts in real-world scenarios, with code examples and case studies.",
                    "source": "Technical Documentation",
                    "citations": random.randint(30, 200)
                },
                {
                    "title": "Understanding {topic} for Beginners",
                    "snippet": "Simplified introduction to {topic} designed for newcomers, breaking down complex ideas into digestible explanations.",
                    "source": "Learning Platform",
                    "citations": random.randint(20, 150)
                },
                {
                    "title": "Recent Advances in {topic}",
                    "snippet": "Survey of the latest developments and breakthrough research in {topic}, covering state-of-the-art techniques and future directions.",
                    "source": "Research Papers Archive",
                    "citations": random.randint(200, 2000)
                }
            ],
            "technical": [
                {
                    "title": "Technical Deep-Dive: {topic}",
                    "snippet": "Detailed technical analysis of {topic} architecture, implementation details, performance characteristics, and optimization strategies.",
                    "source": "Technical Specifications",
                    "citations": random.randint(150, 800)
                },
                {
                    "title": "{topic} Implementation Reference",
                    "snippet": "Complete reference implementation with benchmarks, complexity analysis, and comparison with alternative approaches.",
                    "source": "Engineering Documentation",
                    "citations": random.randint(80, 400)
                }
            ],
            "code": [
                {
                    "title": "{topic} Code Examples",
                    "snippet": "Annotated code samples demonstrating {topic} implementation patterns, with explanations of key design decisions and trade-offs.",
                    "source": "Code Repository",
                    "citations": random.randint(40, 300)
                },
                {
                    "title": "Building with {topic}: Tutorial",
                    "snippet": "Hands-on coding tutorial walking through {topic} implementation from scratch, including testing and debugging strategies.",
                    "source": "Developer Tutorials",
                    "citations": random.randint(60, 350)
                }
            ]
        }
        
        # Extract topic from query (simple heuristic)
        topic = self._extract_topic(query)
        
        # Select templates based on mode
        if mode == "technical":
            templates = doc_templates["technical"] + doc_templates["default"][:3]
        elif mode == "code":
            templates = doc_templates["code"] + doc_templates["default"][:3]
        else:
            templates = doc_templates["default"]
        
        # Fill templates with extracted topic
        docs = []
        for template in templates[:5]:  # Top 5 results
            docs.append({
                "title": template["title"].format(topic=topic.title()),
                "snippet": template["snippet"].format(topic=topic),
                "source": template["source"],
                "citations": template["citations"]
            })
        
        return docs
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query (simple keyword extraction)."""
        # Remove common question words
        stopwords = ["what", "how", "why", "when", "where", "who", "explain", "describe", "tell", "me", "about", "the", "is", "are", "can", "you", "do", "does"]
        words = query.lower().split()
        filtered = [w.strip("?.,!") for w in words if w not in stopwords and len(w) > 2]
        
        # Return multi-word topic or single word
        if len(filtered) >= 2:
            return " ".join(filtered[:3])  # Max 3 words
        elif len(filtered) == 1:
            return filtered[0]
        else:
            return "this concept"


def create_rag_pipeline(query: str, mode: str, response: str) -> Dict[str, Any]:
    """Create a complete RAG pipeline trace for visualization.
    
    Args:
        query: User's question
        mode: Learning mode (affects document selection)
        response: Generated response text
    
    Returns:
        Complete pipeline data with all stages
    """
    tracker = RAGTracker()
    
    # Stage 1: Query encoding
    tracker.track_query_encoding(query)
    
    # Stage 2: Retrieval
    retrieval_data = tracker.track_retrieval(query, mode)
    documents = retrieval_data["documents"]
    
    # Stage 3: Re-ranking
    reranking_data = tracker.track_reranking(documents)
    reranked_docs = reranking_data["reranked_documents"]
    
    # Stage 4: Generation with context
    tracker.track_generation(query, reranked_docs, response)
    
    return tracker.get_pipeline_summary()
