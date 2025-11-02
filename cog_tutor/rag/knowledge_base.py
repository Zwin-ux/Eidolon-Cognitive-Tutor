import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3

class KnowledgeBase:
    """Knowledge base for educational content with fact-grounded explanations."""
    
    def __init__(self, db_path: str = "knowledge_base.sqlite"):
        self.db_path = db_path
        self._init_database()
        self._load_sample_content()
    
    def _init_database(self):
        """Initialize SQLite database for knowledge storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id TEXT PRIMARY KEY,
                    skill TEXT NOT NULL,
                    content TEXT NOT NULL,
                    facts TEXT NOT NULL,
                    difficulty REAL DEFAULT 0.5,
                    prerequisite_skills TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill ON knowledge_items(skill)
            """)
    
    def _load_sample_content(self):
        """Load sample educational content for testing."""
        sample_items = [
            {
                "id": "algebra_simplify_001",
                "skill": "algebra_simplification",
                "content": "To simplify algebraic expressions, combine like terms by adding or subtracting coefficients of the same variable. For example, 3x + 2x = 5x.",
                "facts": [
                    "Like terms have the same variable raised to the same power",
                    "Coefficients of like terms can be combined through addition",
                    "The variable part remains unchanged when combining like terms"
                ],
                "difficulty": 0.3,
                "prerequisite_skills": ["basic_arithmetic", "variables"]
            },
            {
                "id": "algebra_simplify_002", 
                "skill": "algebra_simplification",
                "content": "When simplifying expressions with division, first combine like terms in the numerator, then divide by the denominator. Example: (3x + 2x) / 5 = 5x / 5 = x.",
                "facts": [
                    "Division applies to the entire expression",
                    "Simplify numerator before dividing",
                    "A term divided by itself equals 1"
                ],
                "difficulty": 0.5,
                "prerequisite_skills": ["algebra_simplification", "division"]
            },
            {
                "id": "linear_eq_001",
                "skill": "linear_equations",
                "content": "To solve linear equations, isolate the variable by performing inverse operations. Add/subtract to isolate the variable term, then multiply/divide to solve for the variable.",
                "facts": [
                    "Inverse operations undo each other (addition ↔ subtraction, multiplication ↔ division)",
                    "Apply the same operation to both sides to maintain equality",
                    "Goal is to isolate the variable on one side"
                ],
                "difficulty": 0.4,
                "prerequisite_skills": ["algebra_simplification"]
            },
            {
                "id": "fraction_div_001",
                "skill": "fraction_operations",
                "content": "To divide fractions, multiply by the reciprocal of the second fraction. The reciprocal of a/b is b/a.",
                "facts": [
                    "Division is equivalent to multiplication by the reciprocal",
                    "Reciprocal flips numerator and denominator",
                    "Multiply numerators together and denominators together"
                ],
                "difficulty": 0.6,
                "prerequisite_skills": ["fraction_multiplication"]
            },
            {
                "id": "ratio_001",
                "skill": "ratios",
                "content": "Ratios compare quantities. To solve ratio problems, set up proportions and cross-multiply. a:b = c:d means a×d = b×c.",
                "facts": [
                    "Ratios show relative sizes of quantities",
                    "Equivalent ratios have the same value when simplified",
                    "Cross-multiplication solves proportion equations"
                ],
                "difficulty": 0.5,
                "prerequisite_skills": ["proportions"]
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for item in sample_items:
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_items 
                    (id, skill, content, facts, difficulty, prerequisite_skills)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item["id"],
                    item["skill"], 
                    item["content"],
                    json.dumps(item["facts"]),
                    item["difficulty"],
                    json.dumps(item["prerequisite_skills"])
                ))
    
    def retrieve_by_skill(self, skill: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve knowledge items for a specific skill."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM knowledge_items 
                WHERE skill = ? OR skill LIKE ?
                ORDER BY difficulty ASC
                LIMIT ?
            """, (skill, f"%{skill}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "skill": row["skill"],
                    "content": row["content"],
                    "facts": json.loads(row["facts"]),
                    "difficulty": row["difficulty"],
                    "prerequisite_skills": json.loads(row["prerequisite_skills"])
                })
            return results
    
    def retrieve_by_query(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve knowledge items based on text search."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM knowledge_items 
                WHERE content LIKE ? OR skill LIKE ?
                ORDER BY difficulty ASC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "skill": row["skill"],
                    "content": row["content"],
                    "facts": json.loads(row["facts"]),
                    "difficulty": row["difficulty"],
                    "prerequisite_skills": json.loads(row["prerequisite_skills"])
                })
            return results
    
    def add_knowledge_item(self, item: Dict[str, Any]):
        """Add a new knowledge item to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_items 
                (id, skill, content, facts, difficulty, prerequisite_skills)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item["id"],
                item["skill"],
                item["content"], 
                json.dumps(item["facts"]),
                item["difficulty"],
                json.dumps(item.get("prerequisite_skills", []))
            ))
