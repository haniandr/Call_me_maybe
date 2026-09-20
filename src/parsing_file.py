import argparse
import sys
import json
from typing import Any
from pydantic import ValidationError, BaseModel
from .model import FunctionDefinition, FunctionCallingTest
from pathlib import Path


class Parsing:
    def __init__(self) -> None:
        ...

    def parse_function(
            self,
            content: list[dict[str, Any]]
    ) -> list[FunctionDefinition]:
        """
        Function that validate the file content
        in the functions_definition file with all the
        name, parameters type, description and the returns type

        Return:
            A list of pydantic validated or not with
            FunctionDefinition
        """

        function_list = []
        for function in content:
            function_list.append(FunctionDefinition(
                name=function["name"],
                description=function["description"],
                parameters=function["parameters"],
                returns=function["returns"]
            ))
        return function_list

    def parse_test(
            self,
            content: list[dict[str, Any]]
    ) -> list[FunctionCallingTest]:
        """
        Parse the file with the user's question
        and return an object validated by pydantic
        with FunctionCallingTest

        Return:
            An list of object validated by pydantic
        """

        input_test = []
        for item in content:
            input_test.append(FunctionCallingTest(
                prompt=item["prompt"]
            ))
        return input_test

    def parse_file(
            self,
            name: str,
            model: BaseModel
    ) -> None | list[BaseModel]:
        """
        Open a file and read it with a json.load which
        read and decode  a JSON file and return a python object
        LIST or DICT

        Return:
            None if the file is not the excepted
            The content validated by pydantic in a list
        """
        try:
            with open(name, "r") as file:
                data = json.load(file)
            if len(data) == 0:
                raise ValidationError(
                    f"Your file '{name}'"
                    "has no content. Please check!!"
                )

            if not (isinstance(data, (list, dict))):
                sys.exit(f"The file {name} must contain valid JSON")

            if model == FunctionDefinition:
                return self.parse_function(data)

            if model == FunctionCallingTest:
                return self.parse_test(data)

        except json.JSONDecodeError:
            sys.exit(f"You have an invalid format JSON in the file '{name}'")

        except ValidationError as e:
            sys.exit(f"Error found: {e}")

        except FileNotFoundError:
            sys.exit("No such file or directory"
                     f" in the current project: {name}")
        except PermissionError:
            sys.exit(f"No permission to open this file {name}.")

    def parsing_arguments(self) -> (
            tuple[Path, list[FunctionDefinition],
                  list[FunctionCallingTest]]):
        """
        The root of the parsing
        """
        parser = argparse.ArgumentParser()

        # c pour dire que --... est un arg
        # optionnel et que la valeur apres l'est aussi
        parser.add_argument("--functions_definition", type=Path,
                            default=Path("data/input/\
functions_definition.json"))

        parser.add_argument("--input", type=Path,
                            default=Path("data/input/\
function_calling_tests.json"))

        parser.add_argument("--output", type=Path,
                            default=Path("data/output/\
function_calling_results.json"))

        # analyser les arguments donnes pour acceder a les valeurs
        args = parser.parse_args()

        for file_path in [args.functions_definition, args.input]:
            if not file_path.exists():
                raise argparse.ArgumentTypeError(
                    f"The file {file_path} doesn't exist..."
                )
            if file_path == args.output:
                raise parser.error(
                    "The input filename and the output "
                    "filename must be different"
                )

        func_def = self.parse_file(
            args.functions_definition,
            FunctionDefinition
        )
        input_test = self.parse_file(
            args.input,
            FunctionCallingTest
        )

        return args.output, func_def, input_test

