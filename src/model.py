"""Pydantic models used to validate functions, parameters, output."""

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)
from typing import Any
from enum import Enum


class TypeSpecify(Enum):
    """Type a parameter and a value return can have."""

    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"


class ParamsType(BaseModel):
    """Validate a parameter type."""

    type: TypeSpecify


class ReturnType(BaseModel):
    """Validate a return type."""

    type: TypeSpecify


class FunctionCallingTest(BaseModel):
    """For the validation of the prompt."""

    model_config = ConfigDict(extra='forbid')
    prompt: str = Field()


class FunctionResult(BaseModel):
    """Validate the result format.

    Check if it contains the required
    keys with the excepted type.
    """

    model_config = ConfigDict(extra='forbid')
    prompt: str = Field()
    name: str = Field()
    parameters: dict[str, Any] = Field()


class FunctionDefinition(BaseModel):
    """Validate the function definition type.

    Check if it the exact keys and types for each.
    """

    model_config = ConfigDict(extra='forbid')
    name: str = Field()
    description: str = Field()
    parameters: dict[str, ParamsType] = Field()
    returns: ReturnType
