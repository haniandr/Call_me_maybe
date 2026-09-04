import json
from typing import Any


class FunctionDefinitionError(Exception):
    ...

def parse_file(name: str) -> None | list[dict[str, Any]]:
    try:
        with open(name, "r") as file:
            data = json.load(file)
        if len(data) == 0:
            raise FunctionDefinitionError(
                f"Your file '{name}'"
                "has no content. Please check!!"
            )
        return data

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



# if __name__ == "__main__":
#  print(take_content("data/input/functions_definition.json"))
