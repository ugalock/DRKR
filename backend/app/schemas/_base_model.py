# backend/app/schemas/_base_model.py

from datetime import datetime

from pydantic import BaseModel
from pydantic_core import ValidationError
from typing import Any
from typing_extensions import Self

class CustomBaseModel(BaseModel):
    
    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to enforce types strictly.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises:
            ValidationError: If the object could not be validated.

        Returns:
            The validated model instance.
        """
        # `__tracebackhide__` tells pytest and some other tools to omit this function from tracebacks
        __tracebackhide__ = True
        try:
            return cls.__pydantic_validator__.validate_python(
                obj, strict=strict, from_attributes=from_attributes, context=context
            )
        except ValidationError as e:
            for error in e.errors():
                if type(error['input']) == datetime:
                    _obj = obj
                    for key in error['loc'][:-1]:
                        if isinstance(key, int):
                            _obj = _obj[key]
                        else:
                            _obj = getattr(_obj, key)
                    _obj.__dict__[error['loc'][-1]] = error['input'].isoformat()
            return cls.__pydantic_validator__.validate_python(
                obj, strict=strict, from_attributes=from_attributes, context=context
            )
