import json
from pydantic import (
    model_validator,
    BaseModel,
    Field,
    ValidationError
)
from enum import Enum
from typing import Any


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

class Parsing:
    def parse_file(name: str) -> None | list[dict[str, Any]]:
        try:
            with open(name, "r") as file:
                data = json.load(file)
            if len(data) == 0:
                raise ValidationError(
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
            result = []
            if function_list:
                for func in function_list:
                    result.append({
                        "name": func.name,
                        "description": func.description,
                        "parameters": {
                            key: param.type.value
                            for key, param in func.parameters.items() 
                        },
                        "return": func.returns.type.value
                })
            return result


        except json.JSONDecodeError:
            print(f"You have an invalid format JSON in the file '{name}'")

        except ValidationError as e:
            print(f"Error found: {e}")

        except FileNotFoundError:
            print("No such file or directory"
                f" in the current project: {name}"
            )
        except PermissionError:
            print(f"No permission to open this file {name}.")

if __name__ == "__main__":
    print(Parsing.parse_file("data/input/functions_definition.json"))
