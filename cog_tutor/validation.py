import json
from typing import Type, Any
from pydantic import BaseModel

def parse_and_validate(model: Type[BaseModel], text: str) -> Any:
    data = json.loads(text)
    # Support pydantic v1 and v2
    if hasattr(model, 'model_validate'):
        return model.model_validate(data)
    return model.parse_obj(data)
