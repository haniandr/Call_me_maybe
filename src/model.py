from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ValidationError
)
from typing import Any
from enum import Enum


class TypeSpecify(Enum):
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"


class ParamsType(BaseModel):
    type: TypeSpecify


class ReturnType(BaseModel):
    type: TypeSpecify


class FunctionCallingTest(BaseModel):
    """
    For the validation of the prompt.
    """

    prompt: str = Field()


class FunctionResult(BaseModel):
    """
    Validate the result format if it contains the required
    keys with the excepted type
    """

    prompt: str = Field()
    name: str = Field()
    parameters: dict[str, Any] = Field()


class FunctionDefinition(BaseModel):
    """
    Validate the function definition type 
    with its exact keys and type each
    """
    name: str = Field()
    description: str = Field()
    parameters: dict[str, ParamsType] = Field()
    returns: ReturnType


