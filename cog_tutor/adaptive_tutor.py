import json
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from .knowledge_tracing import KnowledgeTracer, ItemResponse, SkillMastery
from .rag.knowledge_base import KnowledgeBase
from .rag.retriever import KnowledgeRetriever
from .rag.rag_prompts import RAGEnhancedPrompts
from .inference import run_prompt

class AdaptiveTutor:
    """RAG-enhanced adaptive tutoring system with knowledge tracing."""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.knowledge_tracer = KnowledgeTracer()
        self.knowledge_base = KnowledgeBase()
        self.retriever = KnowledgeRetriever(self.knowledge_base)
        self.rag_prompts = RAGEnhancedPrompts()
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_responses = []
    
    def process_student_response(self, item_id: str, skill: str, question: str,
                                user_answer: str, correct_answer: str,
                                response_time: float, hints_used: int = 0) -> Dict[str, Any]:
        """Process a student response and update knowledge tracing."""
        
        # Determine correctness
        is_correct = self._evaluate_answer(user_answer, correct_answer)
        
        # Create item response
        difficulty = self._estimate_item_difficulty(skill, question)
        response = ItemResponse(
            item_id=item_id,
            skill=skill,
            correct=is_correct,
            response_time=response_time,
            hints_used=hints_used,
            difficulty=difficulty,
            timestamp=datetime.now()
        )
        
        # Update knowledge tracing
        new_theta = self.knowledge_tracer.update_mastery(response)
        mastery_prob = self.knowledge_tracer.get_mastery_probability(skill)
        
        # Generate RAG-enhanced explanation
        explanation = self.generate_rag_explanation(question, user_answer, correct_answer)
        
        # Track session
        self.session_responses.append(response)
        
        return {
            "correct": is_correct,
            "mastery_theta": new_theta,
            "mastery_probability": mastery_prob,
            "explanation": explanation,
            "next_recommendations": self.get_next_items(skill)
        }
    
    def generate_rag_explanation(self, question: str, user_answer: str, 
                                correct_answer: str) -> Dict[str, Any]:
        """Generate explanation with knowledge grounding."""
        
        # Retrieve relevant knowledge
        knowledge_context = self.retriever.get_explanation_with_citations(
            question, user_answer, correct_answer
        )
        
        # Prepare input for RAG-enhanced prompt
        prompt_input = {
            "question": question,
            "user_answer": user_answer,
            "solution": correct_answer,
            "facts": knowledge_context["facts"],
            "sources": knowledge_context["sources"]
        }
        
        # Generate explanation using RAG prompt
        try:
            explanation = run_prompt(
                "item_explanation_with_rag",
                prompt_input,
                model_id="Qwen/Qwen3-7B-Instruct"
            )
            
            # Add citations from knowledge base
            explanation["knowledge_citations"] = knowledge_context["citations"]
            explanation["fact_sources"] = knowledge_context["facts"]
            
        except Exception as e:
            # Fallback to basic explanation
            explanation = {
                "hint": "Review the problem steps carefully.",
                "guided": "Compare your answer with the correct solution.",
                "full": f"The correct answer is {correct_answer}. Please review the method.",
                "knowledge_citations": [],
                "fact_sources": []
            }
        
        return explanation
    
    def generate_adaptive_hints(self, question: str, hint_level: int = 1) -> List[str]:
        """Generate contextual hints using RAG."""
        return self.retriever.get_contextual_hints(question, hint_level)
    
    def generate_adaptive_question(self, skill: str, difficulty: Optional[float] = None) -> Dict[str, Any]:
        """Generate an adaptive question based on current mastery."""
        
        if difficulty is None:
            mastery = self.knowledge_tracer.get_mastery_probability(skill)
            difficulty = 1.0 - mastery  # Inverse relationship
        
        # Retrieve relevant knowledge for the skill
        knowledge_items = self.knowledge_base.retrieve_by_skill(skill, limit=3)
        
        # Prepare input for question generation
        prompt_input = {
            "skill": skill,
            "mastery_level": 1.0 - difficulty,
            "knowledge_content": [item["content"] for item in knowledge_items],
            "difficulty": difficulty
        }
        
        try:
            question = run_prompt(
                "adaptive_question_generation",
                prompt_input,
                model_id="Qwen/Qwen3-7B-Instruct"
            )
            
            # Add knowledge citations
            question["knowledge_sources"] = [item["id"] for item in knowledge_items]
            
        except Exception as e:
            # Fallback question template
            question = {
                "question": f"Practice problem for {skill} at difficulty {difficulty:.2f}",
                "answer": "Answer to be determined",
                "explanation": "Explanation to be provided",
                "difficulty": difficulty,
                "skill": skill,
                "knowledge_sources": []
            }
        
        return question
    
    def get_next_items(self, current_skill: str = None, max_items: int = 5) -> List[Dict[str, Any]]:
        """Get next item recommendations using entropy-based scheduling."""
        
        # Generate candidate items
        candidates = []
        skills = ["algebra_simplification", "linear_equations", "fraction_operations", "ratios"]
        
        for skill in skills:
            for i in range(3):  # 3 items per skill
                mastery = self.knowledge_tracer.get_mastery_probability(skill)
                difficulty = 1.0 - mastery + np.random.normal(0, 0.1)  # Add noise
                
                candidates.append({
                    "item_id": f"{skill}_{i}",
                    "skill": skill,
                    "difficulty": np.clip(difficulty, 0.1, 0.9),
                    "type": "practice"
                })
        
        # Get recommendations from knowledge tracer
        recommendations = self.knowledge_tracer.get_next_item_recommendations(
            candidates, max_items
        )
        
        # Add adaptive questions for top recommendations
        for rec in recommendations:
            if rec["type"] == "practice":
                adaptive_q = self.generate_adaptive_question(rec["skill"], rec["difficulty"])
                rec.update(adaptive_q)
        
        return recommendations
    
    def evaluate_mastery_with_irt(self, skill: str) -> Dict[str, Any]:
        """Evaluate mastery using IRT parameters."""
        
        # Get recent responses for the skill
        skill_responses = [r for r in self.session_responses if r.skill == skill]
        
        if not skill_responses:
            # Get from database if no session responses
            mastery_prob = self.knowledge_tracer.get_mastery_probability(skill)
            return {
                "theta": 0.0,
                "sem": 1.0,
                "mastery": mastery_prob,
                "confidence_interval": [-1.96, 1.96]
            }
        
        # Prepare input for IRT evaluation
        responses_data = []
        for r in skill_responses[-10:]:  # Last 10 responses
            responses_data.append({
                "correct": r.correct,
                "difficulty": r.difficulty,
                "response_time": r.response_time,
                "hints": r.hints_used
            })
        
        prompt_input = {
            "skill": skill,
            "responses": responses_data
        }
        
        try:
            irt_result = run_prompt(
                "mastery_diagnostic_with_irt",
                prompt_input,
                model_id="Qwen/Qwen3-7B-Instruct"
            )
            return irt_result
        except:
            # Fallback to knowledge tracer estimates
            if skill in self.knowledge_tracer.skill_masteries:
                mastery = self.knowledge_tracer.skill_masteries[skill]
                return {
                    "theta": mastery.theta,
                    "sem": mastery.sem,
                    "mastery": self.knowledge_tracer.get_mastery_probability(skill),
                    "confidence_interval": [
                        mastery.theta - 1.96 * mastery.sem,
                        mastery.theta + 1.96 * mastery.sem
                    ]
                }
            else:
                return {
                    "theta": 0.0,
                    "sem": 1.0,
                    "mastery": 0.5,
                    "confidence_interval": [-1.96, 1.96]
                }
    
    def get_research_metrics(self) -> Dict[str, Any]:
        """Get comprehensive research metrics for evaluation."""
        
        # Basic session metrics
        session_duration = (datetime.now() - self.session_start).total_seconds()
        total_responses = len(self.session_responses)
        correct_responses = sum(1 for r in self.session_responses if r.correct)
        
        # Get detailed metrics from knowledge tracer
        tracer_metrics = self.knowledge_tracer.get_research_metrics()
        
        # Calculate additional session-based metrics
        if total_responses > 0:
            session_accuracy = correct_responses / total_responses
            avg_session_time = np.mean([r.response_time for r in self.session_responses])
            hints_per_response = np.mean([r.hints_used for r in self.session_responses])
        else:
            session_accuracy = 0.0
            avg_session_time = 0.0
            hints_per_response = 0.0
        
        # Learning gain calculation
        if len(self.session_responses) >= 10:
            early_accuracy = sum(1 for r in self.session_responses[:5] if r.correct) / 5
            late_accuracy = sum(1 for r in self.session_responses[-5:] if r.correct) / 5
            session_learning_gain = late_accuracy - early_accuracy
        else:
            session_learning_gain = 0.0
        
        # Combine all metrics
        research_metrics = {
            "session_metrics": {
                "duration_seconds": session_duration,
                "total_responses": total_responses,
                "accuracy": session_accuracy,
                "avg_response_time": avg_session_time,
                "hints_per_response": hints_per_response,
                "learning_gain": session_learning_gain
            },
            "cumulative_metrics": tracer_metrics,
            "knowledge_tracing": {
                "tracked_skills": len(self.knowledge_tracer.skill_masteries),
                "skill_masteries": {
                    skill: {
                        "theta": mastery.theta,
                        "mastery_prob": self.knowledge_tracer.get_mastery_probability(skill),
                        "practice_count": mastery.practice_count
                    }
                    for skill, mastery in self.knowledge_tracer.skill_masteries.items()
                }
            }
        }
        
        return research_metrics
    
    def _evaluate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """Evaluate if user answer is correct."""
        # Simple string comparison - can be enhanced with semantic matching
        return user_answer.strip().lower() == correct_answer.strip().lower()
    
    def _estimate_item_difficulty(self, skill: str, question: str) -> float:
        """Estimate item difficulty based on skill and question complexity."""
        # Base difficulty on skill type
        skill_difficulties = {
            "algebra_simplification": 0.3,
            "linear_equations": 0.5,
            "fraction_operations": 0.6,
            "ratios": 0.5
        }
        
        base_difficulty = skill_difficulties.get(skill, 0.5)
        
        # Adjust based on question length (proxy for complexity)
        length_factor = min(len(question) / 100.0, 0.3)
        
        return np.clip(base_difficulty + length_factor, 0.1, 0.9)
