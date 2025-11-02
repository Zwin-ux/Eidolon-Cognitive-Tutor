import json
from typing import Dict, Any
from . import prompts
from .schemas import (
    ItemExplanationInput, ItemExplanationOutput,
    MasteryDiagnosticInput, MasteryDiagnosticOutput,
    NextItemSelectorInput, NextItemSelectorOutput,
    SkillFeedbackInput, SkillFeedbackOutput,
    HintGenerationInput, HintGenerationOutput,
    ReflectionInput, ReflectionOutput,
    InstructorInsightInput, InstructorInsightRow,
    ExplanationCompressionInput, ExplanationCompressionOutput,
    QuestionAuthoringInput, QuestionAuthoringOutput,
    ToneNormalizerInput, ToneNormalizerOutput,
)
from .validation import parse_and_validate
from .cache import make_key, get as cache_get, set as cache_set
from .adapters.qwen_adapter import QwenAdapter

PRESETS = {
    'item_explanation': dict(temperature=0.2, max_tokens=256),
    'mastery_diagnostic': dict(temperature=0.2, max_tokens=128),
    'next_item_selector': dict(temperature=0.2, max_tokens=128),
    'skill_feedback': dict(temperature=0.3, max_tokens=256),
    'hint_generation': dict(temperature=0.6, max_tokens=200),
    'reflection': dict(temperature=0.3, max_tokens=120),
    'instructor_insight': dict(temperature=0.2, max_tokens=160),
    'explanation_compression': dict(temperature=0.2, max_tokens=80),
    'question_authoring': dict(temperature=0.6, max_tokens=400),
    'tone_normalizer': dict(temperature=0.2, max_tokens=60),
}

SYSTEMS = {
    'item_explanation': prompts.item_explanation,
    'mastery_diagnostic': prompts.mastery_diagnostic,
    'next_item_selector': prompts.next_item_selector,
    'skill_feedback': prompts.skill_feedback,
    'hint_generation': prompts.hint_generation,
    'reflection': prompts.reflection,
    'instructor_insight': prompts.instructor_insight,
    'explanation_compression': prompts.explanation_compression,
    'question_authoring': prompts.question_authoring,
    'tone_normalizer': prompts.tone_normalizer,
}

INPUT_MODELS = {
    'item_explanation': ItemExplanationInput,
    'mastery_diagnostic': MasteryDiagnosticInput,
    'next_item_selector': NextItemSelectorInput,
    'skill_feedback': SkillFeedbackInput,
    'hint_generation': HintGenerationInput,
    'reflection': ReflectionInput,
    'instructor_insight': InstructorInsightInput,
    'explanation_compression': ExplanationCompressionInput,
    'question_authoring': QuestionAuthoringInput,
    'tone_normalizer': ToneNormalizerInput,
}

OUTPUT_MODELS = {
    'item_explanation': ItemExplanationOutput,
    'mastery_diagnostic': MasteryDiagnosticOutput,
    'next_item_selector': NextItemSelectorOutput,
    'skill_feedback': SkillFeedbackOutput,
    'hint_generation': HintGenerationOutput,
    'reflection': ReflectionOutput,
    'instructor_insight': InstructorInsightRow,  # list validated separately
    'explanation_compression': ExplanationCompressionOutput,
    'question_authoring': QuestionAuthoringOutput,
    'tone_normalizer': ToneNormalizerOutput,
}

_adapter = None
SPECIAL_CACHE_KEYS = {'item_explanation', 'hint_generation'}


def _get_adapter(model_id: str) -> QwenAdapter:
    global _adapter
    if _adapter is None:
        _adapter = QwenAdapter(model_name=model_id)
    return _adapter

def _cache_key(prompt_name: str, input_data: Dict[str, Any], model_id: str, temperature: float) -> str:
    special = None
    if prompt_name in SPECIAL_CACHE_KEYS:
        if prompt_name == 'item_explanation':
            q = input_data.get('question', '')
            ua = input_data.get('user_answer', '')
            special = f"{q}\u241f{ua}"
        elif prompt_name == 'hint_generation':
            q = input_data.get('question', '')
            special = q
    base = json.dumps(input_data, sort_keys=True)
    parts = [prompt_name, base, model_id, temperature, special or '-']
    return make_key(*parts)


def run_prompt(prompt_name: str, input_payload: Dict[str, Any], *, model_id: str = 'Qwen/Qwen3-7B-Instruct', seed: int = 42) -> Any:
    if prompt_name not in PRESETS:
        raise ValueError(f'Unknown prompt: {prompt_name}')

    input_model = INPUT_MODELS[prompt_name]
    parsed_input = input_model.parse_obj(input_payload)

    preset = PRESETS[prompt_name]
    ckey = _cache_key(prompt_name, parsed_input.dict(by_alias=True), model_id, preset['temperature'])
    cached = cache_get(ckey)
    if cached is not None:
        return json.loads(cached)

    # Get adapter with lazy initialization
    adapter = _get_adapter(model_id)
    
    system = SYSTEMS[prompt_name]()
    user = json.dumps(parsed_input.dict(by_alias=True), ensure_ascii=False)

    text = adapter.generate(
        system=system,
        user=f"Return JSON only. No commentary.\nInput: {user}",
        temperature=preset['temperature'],
        max_tokens=preset['max_tokens'],
        stop=None,
        seed=seed,
    )

    if prompt_name == 'instructor_insight':
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError('Expected a JSON array')
        from .schemas import InstructorInsightRow
        validated = [InstructorInsightRow.parse_obj(x).dict() for x in data]
        out_obj = validated
    else:
        out_model = OUTPUT_MODELS[prompt_name]
        out_obj = parse_and_validate(out_model, text)
        # Handle RootModel (Pydantic v2)
        if hasattr(out_obj, 'root'):
            out_obj = out_obj.root
        elif hasattr(out_obj, 'dict'):
            out_obj = out_obj.dict(by_alias=True)
        elif hasattr(out_obj, '__root__'):
            out_obj = out_obj.__root__

    cache_set(ckey, json.dumps(out_obj, ensure_ascii=False))
    return out_obj
