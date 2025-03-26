from typing import List, Optional, Type
from pydantic import BaseModel, create_model
from fastapi import Query


class ResponseModelDependency:
    def __init__(self, model_class: Type[BaseModel]):
        self.model_class = model_class

    def __call__(self, response_fields: Optional[List[str]] = Query(None)) -> Type[BaseModel]:
        def process_result(result, fields=None):
            if not fields:
                return result

            if hasattr(result, "_fields"):
                row_fields = result._fields
                return dict(zip(row_fields, result))
            elif isinstance(result, tuple):
                return dict(zip(fields, result))
            elif isinstance(result, dict):
                return result
            else:
                return {field: getattr(result, field) for field in fields if hasattr(result, field)}

        if not response_fields:
            return self.model_class, None, process_result

        all_annotations = {}
        for cls in self.model_class.__mro__:
            if hasattr(cls, "__annotations__"):
                all_annotations.update(cls.__annotations__)

        fields = {}
        for field in response_fields:
            if field in all_annotations:
                fields[field] = (all_annotations[field], None)

        dynamic_model = create_model(f"Dynamic{self.model_class.__name__}", **fields)

        return dynamic_model, response_fields, process_result
