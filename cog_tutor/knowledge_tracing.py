import numpy as np
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3

@dataclass
class SkillMastery:
    skill: str
    theta: float  # IRT ability parameter (-3 to +3)
    sem: float    # Standard error of measurement
    last_practiced: datetime
    practice_count: int
    success_rate: float

@dataclass
class ItemResponse:
    item_id: str
    skill: str
    correct: bool
    response_time: float
    hints_used: int
    difficulty: float
    timestamp: datetime

class KnowledgeTracer:
    """Knowledge tracing system using Item Response Theory and Bayesian updating."""
    
    def __init__(self, db_path: str = "knowledge_tracing.sqlite"):
        self.db_path = db_path
        self._init_database()
        self.skill_masteries: Dict[str, SkillMastery] = {}
        self.response_history: List[ItemResponse] = []
    
    def _init_database(self):
        """Initialize database for storing tracing data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_mastery (
                    skill TEXT PRIMARY KEY,
                    theta REAL DEFAULT 0.0,
                    sem REAL DEFAULT 1.0,
                    last_practiced TIMESTAMP,
                    practice_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS item_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT,
                    skill TEXT,
                    correct BOOLEAN,
                    response_time REAL,
                    hints_used INTEGER,
                    difficulty REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill_responses ON item_responses(skill)
            """)
    
    def update_mastery(self, response: ItemResponse) -> float:
        """Update skill mastery using Bayesian updating with IRT."""
        skill = response.skill
        
        # Load current mastery if exists
        if skill not in self.skill_masteries:
            self._load_skill_mastery(skill)
        
        current = self.skill_masteries.get(skill, SkillMastery(
            skill=skill, theta=0.0, sem=1.0, 
            last_practiced=datetime.now(), 
            practice_count=0, success_rate=0.0
        ))
        
        # IRT 2-parameter model update
        # P(correct) = 1 / (1 + exp(-a*(theta - b)))
        # where a = discrimination (fixed at 1.0), b = difficulty
        
        # Calculate likelihood of response given current theta
        logit = current.theta - response.difficulty
        p_correct = 1.0 / (1.0 + np.exp(-logit))
        
        # Bayesian update using response as evidence
        # Posterior precision = prior precision + information
        prior_precision = 1.0 / (current.sem ** 2)
        
        # Information function for 2PL IRT
        information = p_correct * (1 - p_correct)
        
        posterior_precision = prior_precision + information
        posterior_sem = np.sqrt(1.0 / posterior_precision)
        
        # Update theta based on response
        if response.correct:
            # Correct response increases theta
            theta_update = (current.theta / (current.sem ** 2) + 
                          information * response.difficulty) / posterior_precision
        else:
            # Incorrect response decreases theta
            theta_update = (current.theta / (current.sem ** 2) - 
                          information * (1 - response.difficulty)) / posterior_precision
        
        # Apply forgetting factor for time since last practice
        days_since_practice = (response.timestamp - current.last_practiced).days
        forgetting_factor = np.exp(-0.05 * days_since_practice)  # 5% decay per day
        
        theta_update *= forgetting_factor
        
        # Update mastery
        updated = SkillMastery(
            skill=skill,
            theta=np.clip(theta_update, -3.0, 3.0),
            sem=posterior_sem,
            last_practiced=response.timestamp,
            practice_count=current.practice_count + 1,
            success_rate=self._update_success_rate(current.success_rate, current.practice_count, response.correct)
        )
        
        self.skill_masteries[skill] = updated
        self.response_history.append(response)
        
        # Save to database
        self._save_skill_mastery(updated)
        self._save_response(response)
        
        return updated.theta
    
    def _update_success_rate(self, current_rate: float, count: int, correct: bool) -> float:
        """Update exponential moving average of success rate."""
        alpha = 0.1  # Learning rate for EMA
        if count == 0:
            return 1.0 if correct else 0.0
        return alpha * (1.0 if correct else 0.0) + (1 - alpha) * current_rate
    
    def get_mastery_probability(self, skill: str) -> float:
        """Convert theta to mastery probability (0-1 scale)."""
        if skill not in self.skill_masteries:
            self._load_skill_mastery(skill)
        
        # Use default theta if skill not found
        theta = self.skill_masteries.get(skill, SkillMastery(
            skill=skill, theta=0.0, sem=1.0,
            last_practiced=datetime.now(),
            practice_count=0, success_rate=0.0
        )).theta
        
        # Logistic transformation: theta=0 -> 0.5, theta=+2 -> 0.88, theta=-2 -> 0.12
        return 1.0 / (1.0 + np.exp(-theta))
    
    def calculate_information_gain(self, skill: str, difficulty: float) -> float:
        """Calculate expected information gain for an item."""
        if skill not in self.skill_masteries:
            self._load_skill_mastery(skill)
        
        # Use default theta if skill not found
        theta = self.skill_masteries.get(skill, SkillMastery(
            skill=skill, theta=0.0, sem=1.0,
            last_practiced=datetime.now(),
            practice_count=0, success_rate=0.0
        )).theta
        
        # Expected information = I(theta) where I is Fisher information
        logit = theta - difficulty
        p_correct = 1.0 / (1.0 + np.exp(-logit))
        information = p_correct * (1 - p_correct)
        
        return information
    
    def get_next_item_recommendations(self, candidate_items: List[Dict[str, Any]], 
                                     max_items: int = 5) -> List[Dict[str, Any]]:
        """Recommend next items based on information gain and spacing."""
        scored_items = []
        
        for item in candidate_items:
            skill = item['skill']
            difficulty = item['difficulty']
            
            # Calculate information gain
            info_gain = self.calculate_information_gain(skill, difficulty)
            
            # Calculate spacing benefit (higher for items not practiced recently)
            if skill in self.skill_masteries:
                days_since = (datetime.now() - self.skill_masteries[skill].last_practiced).days
                spacing_bonus = min(days_since / 7.0, 1.0)  # Max bonus after 1 week
            else:
                spacing_bonus = 1.0  # New skill gets max bonus
            
            # Calculate mastery urgency (higher for lower mastery)
            mastery = self.get_mastery_probability(skill)
            urgency = 1.0 - mastery
            
            # Combined score
            score = 0.4 * info_gain + 0.3 * spacing_bonus + 0.3 * urgency
            
            scored_items.append({
                **item,
                'score': score,
                'information_gain': info_gain,
                'spacing_bonus': spacing_bonus,
                'urgency': urgency,
                'current_mastery': mastery
            })
        
        # Sort by score and return top items
        scored_items.sort(key=lambda x: x['score'], reverse=True)
        return scored_items[:max_items]
    
    def get_research_metrics(self, skill: str = None) -> Dict[str, Any]:
        """Calculate research metrics for evaluation."""
        if skill:
            responses = [r for r in self.response_history if r.skill == skill]
        else:
            responses = self.response_history
        
        if not responses:
            return {}
        
        # Basic metrics
        total_responses = len(responses)
        correct_responses = sum(1 for r in responses if r.correct)
        accuracy = correct_responses / total_responses
        
        # Time metrics
        avg_response_time = np.mean([r.response_time for r in responses])
        
        # Hint metrics
        hints_per_response = np.mean([r.hints_used for r in responses])
        
        # Learning gain (compare first vs last 10 responses)
        if len(responses) >= 20:
            early_responses = responses[:10]
            late_responses = responses[-10:]
            
            early_accuracy = sum(1 for r in early_responses if r.correct) / len(early_responses)
            late_accuracy = sum(1 for r in late_responses if r.correct) / len(late_responses)
            learning_gain = late_accuracy - early_accuracy
        else:
            learning_gain = 0.0
        
        # Retention (performance on items practiced > 3 days ago)
        retention_items = [r for r in responses 
                          if (datetime.now() - r.timestamp).days > 3]
        if retention_items:
            retention_rate = sum(1 for r in retention_items if r.correct) / len(retention_items)
        else:
            retention_rate = None
        
        return {
            'total_responses': total_responses,
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            'hints_per_response': hints_per_response,
            'learning_gain': learning_gain,
            'retention_rate': retention_rate,
            'skill_masteries': len(self.skill_masteries)
        }
    
    def _load_skill_mastery(self, skill: str):
        """Load skill mastery from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM skill_mastery WHERE skill = ?", (skill,)
            )
            row = cursor.fetchone()
            if row:
                self.skill_masteries[skill] = SkillMastery(
                    skill=row['skill'],
                    theta=row['theta'],
                    sem=row['sem'],
                    last_practiced=datetime.fromisoformat(row['last_practiced']),
                    practice_count=row['practice_count'],
                    success_rate=row['success_rate']
                )
    
    def _save_skill_mastery(self, mastery: SkillMastery):
        """Save skill mastery to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO skill_mastery 
                (skill, theta, sem, last_practiced, practice_count, success_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mastery.skill,
                mastery.theta,
                mastery.sem,
                mastery.last_practiced.isoformat(),
                mastery.practice_count,
                mastery.success_rate
            ))
    
    def _save_response(self, response: ItemResponse):
        """Save item response to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO item_responses 
                (item_id, skill, correct, response_time, hints_used, difficulty, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                response.item_id,
                response.skill,
                response.correct,
                response.response_time,
                response.hints_used,
                response.difficulty,
                response.timestamp.isoformat()
            ))
