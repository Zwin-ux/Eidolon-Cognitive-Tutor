from typing import List, Dict, Any
from pydantic import BaseModel, Field, confloat, conlist, RootModel

class ItemExplanationInput(BaseModel):
    question: str
    user_answer: str
    solution: str

class ItemExplanationOutput(BaseModel):
    hint: str
    guided: str
    full: str

class MasteryDiagEvent(BaseModel):
    correct: bool
    rt: int
    hints: int

class MasteryDiagnosticInput(BaseModel):
    skill: str
    history: conlist(MasteryDiagEvent, min_length=1, max_length=50)

class MasteryDiagnosticOutput(BaseModel):
    mastery: confloat(ge=0.0, le=1.0)
    comment: str

class NextItemCandidate(BaseModel):
    item_id: str
    skill: str
    p_correct: confloat(ge=0.0, le=1.0)
    due: bool

class NextItemSelectorInput(BaseModel):
    user_id: str
    candidates: conlist(NextItemCandidate, min_length=1)

class NextItemSelectorOutput(BaseModel):
    item_id: str
    reason: str

class SkillMastery(BaseModel):
    name: str
    mastery: confloat(ge=0.0, le=1.0)

class SkillFeedbackInput(BaseModel):
    skills: conlist(SkillMastery, min_length=1)

class SkillWeakness(BaseModel):
    skill: str
    tip: str

class SkillFeedbackOutput(BaseModel):
    strengths: List[str]
    weaknesses: List[SkillWeakness]

class HintGenerationInput(BaseModel):
    question: str

class HintGenerationOutput(BaseModel):
    field_1: str = Field(alias='1')
    field_2: str = Field(alias='2')
    field_3: str = Field(alias='3')
    class Config:
        populate_by_name = True

class ReflectionInput(BaseModel):
    session: Dict[str, Any]

class ReflectionOutput(BaseModel):
    reflection: str
    improvement: str

class InstructorItem(BaseModel):
    id: str
    discrimination: float
    accuracy: confloat(ge=0.0, le=1.0)

class InstructorInsightInput(BaseModel):
    items: conlist(InstructorItem, min_length=1)

class InstructorInsightRow(BaseModel):
    item_id: str
    flag: str

class ExplanationCompressionInput(BaseModel):
    explanation: str

class ExplanationCompressionOutput(BaseModel):
    recap: str

class QuestionAuthoringInput(BaseModel):
    skill: str
    difficulty: str

class QAItem(BaseModel):
    q: str
    a: str
    why: str

class QuestionAuthoringOutput(RootModel[List[QAItem]]):
    pass

class ToneNormalizerInput(BaseModel):
    raw: str

class ToneNormalizerOutput(BaseModel):
    normalized: str
