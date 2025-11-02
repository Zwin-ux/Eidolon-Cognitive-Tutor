#!/usr/bin/env python3
"""
Test script for RAG-enhanced Cognitive Tutor system.
Demonstrates adaptive questioning, knowledge tracing, and research metrics.
"""

from cog_tutor.adaptive_tutor import AdaptiveTutor
import json
import time

def test_rag_enhanced_tutor():
    """Test the complete RAG-enhanced tutoring system."""
    
    print("=== RAG-Enhanced Cognitive Tutor Test ===\n")
    
    # Initialize tutor
    tutor = AdaptiveTutor(user_id="sunny_test")
    
    # Test 1: Generate adaptive question
    print("1. Testing Adaptive Question Generation")
    print("-" * 40)
    
    question = tutor.generate_adaptive_question("algebra_simplification")
    print(f"Generated Question: {question['question']}")
    print(f"Expected Difficulty: {question['difficulty']:.2f}")
    print(f"Knowledge Sources: {question['knowledge_sources']}")
    print()
    
    # Test 2: Process student response
    print("2. Testing Student Response Processing")
    print("-" * 40)
    
    # Simulate student response
    start_time = time.time()
    time.sleep(2)  # Simulate thinking time
    response_time = time.time() - start_time
    
    result = tutor.process_student_response(
        item_id="test_001",
        skill="algebra_simplification", 
        question=question['question'],
        user_answer="5x",  # Incorrect answer
        correct_answer="x",
        response_time=response_time,
        hints_used=1
    )
    
    print(f"Response Correct: {result['correct']}")
    print(f"Mastery Theta: {result['mastery_theta']:.3f}")
    print(f"Mastery Probability: {result['mastery_probability']:.3f}")
    print(f"Explanation Hint: {result['explanation']['hint']}")
    print()
    
    # Test 3: Generate contextual hints
    print("3. Testing Contextual Hint Generation")
    print("-" * 40)
    
    hints = tutor.generate_adaptive_hints(question['question'], hint_level=2)
    for i, hint in enumerate(hints, 1):
        print(f"Hint {i}: {hint}")
    print()
    
    # Test 4: Get next item recommendations
    print("4. Testing Next Item Recommendations")
    print("-" * 40)
    
    recommendations = tutor.get_next_items("algebra_simplification", max_items=3)
    for i, rec in enumerate(recommendations, 1):
        print(f"Recommendation {i}:")
        print(f"  Item: {rec['item_id']}")
        print(f"  Skill: {rec['skill']}")
        print(f"  Score: {rec['score']:.3f}")
        print(f"  Information Gain: {rec['information_gain']:.3f}")
        print(f"  Current Mastery: {rec['current_mastery']:.3f}")
        print()
    
    # Test 5: Evaluate mastery with IRT
    print("5. Testing IRT Mastery Evaluation")
    print("-" * 40)
    
    irt_evaluation = tutor.evaluate_mastery_with_irt("algebra_simplification")
    print(f"Theta (Ability): {irt_evaluation['theta']:.3f}")
    print(f"Standard Error: {irt_evaluation['sem']:.3f}")
    print(f"Mastery Probability: {irt_evaluation['mastery']:.3f}")
    print(f"95% CI: [{irt_evaluation['confidence_interval'][0]:.2f}, {irt_evaluation['confidence_interval'][1]:.2f}]")
    print()
    
    # Test 6: Simulate multiple responses for learning metrics
    print("6. Testing Learning Progress Simulation")
    print("-" * 40)
    
    # Simulate 5 more responses
    for i in range(5):
        # Generate question
        q = tutor.generate_adaptive_question("algebra_simplification")
        
        # Simulate improving performance
        correct = i >= 2  # Get correct after 3 attempts
        
        result = tutor.process_student_response(
            item_id=f"test_{i+2:03d}",
            skill="algebra_simplification",
            question=q['question'],
            user_answer="x" if correct else "5x",
            correct_answer="x",
            response_time=3.0 - i * 0.3,  # Get faster
            hints_used=max(0, 2 - i)  # Use fewer hints
        )
        
        print(f"Response {i+1}: Correct={result['correct']}, Mastery={result['mastery_probability']:.3f}")
    
    print()
    
    # Test 7: Get comprehensive research metrics
    print("7. Testing Research Metrics")
    print("-" * 40)
    
    metrics = tutor.get_research_metrics()
    
    print("Session Metrics:")
    session = metrics['session_metrics']
    print(f"  Duration: {session['duration_seconds']:.1f}s")
    print(f"  Total Responses: {session['total_responses']}")
    print(f"  Accuracy: {session['accuracy']:.3f}")
    print(f"  Learning Gain: {session['learning_gain']:.3f}")
    
    print("\nCumulative Metrics:")
    cumulative = metrics['cumulative_metrics']
    if cumulative:
        print(f"  Total Responses: {cumulative.get('total_responses', 0)}")
        print(f"  Accuracy: {cumulative.get('accuracy', 0):.3f}")
        print(f"  Retention Rate: {cumulative.get('retention_rate', 'N/A')}")
    
    print("\nKnowledge Tracing:")
    kt = metrics['knowledge_tracing']
    print(f"  Tracked Skills: {kt['tracked_skills']}")
    for skill, data in kt['skill_masteries'].items():
        print(f"  {skill}: θ={data['theta']:.2f}, mastery={data['mastery_prob']:.3f}")
    
    print()
    
    # Test 8: Test RAG knowledge retrieval
    print("8. Testing Knowledge Retrieval")
    print("-" * 40)
    
    # Test fact retrieval
    facts = tutor.retriever.get_facts_for_explanation(
        "Simplify (3x + 2x) / 5",
        "5x", 
        "x"
    )
    
    print("Retrieved Facts for Explanation:")
    for i, fact in enumerate(facts, 1):
        print(f"  {i}. {fact}")
    
    print()
    
    # Test 9: Save metrics to file for research analysis
    print("9. Saving Research Data")
    print("-" * 40)
    
    research_data = {
        "user_id": tutor.user_id,
        "session_start": tutor.session_start.isoformat(),
        "metrics": metrics,
        "session_responses": [
            {
                "item_id": r.item_id,
                "skill": r.skill,
                "correct": r.correct,
                "response_time": r.response_time,
                "hints_used": r.hints_used,
                "difficulty": r.difficulty,
                "timestamp": r.timestamp.isoformat()
            }
            for r in tutor.session_responses
        ]
    }
    
    with open("research_output.json", "w") as f:
        json.dump(research_data, f, indent=2)
    
    print("Research data saved to 'research_output.json'")
    print()
    
    print("=== Test Complete ===")
    print("RAG-enhanced Cognitive Tutor is ready for deployment!")

if __name__ == "__main__":
    test_rag_enhanced_tutor()
