import json
from pydantic import (
    model_validator,
    BaseModel,
    Field
)
from enum import Enum
from typing import Any


class FunctionDefinitionError(Exception):
    ...


class TypeSpecify(Enum):
    Number = "number"
    String = "string"
    Boolean = "boolean"
    Null = "None"


class ParamsType(BaseModel):
    type: TypeSpecify


class ReturnType(BaseModel):
    type: TypeSpecify


class FunctionDefinition(BaseModel):
    name: str = Field()
    description: str = Field()
    parameters: dict[str, ParamsType] = Field()
    returns: ReturnType = Field()

    @model_validator(mode="after")
    def validate_model(self) -> "FunctionDefinition":
        for key in self.parameters:
            if 'type' not in self.parameters[key]:
                raise ValueError("Unexpected key in place of 'type'")
        return self


def parse_file(name: str) -> None | list[dict[str, Any]]:
    try:
        with open(name, "r") as file:
            data = json.load(file)
        if len(data) == 0:
            raise FunctionDefinitionError(
                f"Your file '{name}'"
                "has no content. Please check!!"
            )

        function_list: list[FunctionDefinition] = []
        for function in data:
            function_list.append(FunctionDefinition(
                name=function["name"],
                description=function["description"],
                parameters=function["parameters"],
                returns=function["returns"]
            ))
        return function_list

    except json.JSONDecodeError:
        print(f"You have an invalid format JSON in the file '{name}'")

    except FunctionDefinitionError:
        ...

    except FileNotFoundError:
        print("No such file or directory"
              f" in the current project: {name}"
        )
    except PermissionError:
        print(f"No permission to open this file {name}.")

if __name__ == "__main__":
    print(parse_file("data/input/functions_definition.json"))
