import json
from pydantic import (
    model_validator,
    BaseModel,
    Field
)
from typing import Any


class FunctionDefinitionError(Exception):
    ...


class FunctionDefinition(BaseModel):
    name: str = Field()
    description: str = Field()
    parameters: dict[str, dict[str, str]] = Field()
    returns: dict[str, str] = Field()

    @model_validator(mode="after")
    def validate_model(self) -> "FunctionDefinition":
        for key in self.parameters.keys():
            if 'type' not in self.parameters[key].keys():
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

    except FunctionDefinitionError as e:
        print(e)

    except FileNotFoundError:
        print("No such file or directory"
              f" in the current project: {name}"
        )
    except PermissionError:
        print(f"No permission to open this file {name}.")

if __name__ == "__main__":
    print(parse_file("data/input/functions_definition.json"))
