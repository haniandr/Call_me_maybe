"""Parsing of the file and get from the command-line arguments."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .model import FunctionCallingTest, FunctionDefinition


class Parsing:
    """Parse functions, prompts files and the command-line."""

    def __init__(self) -> None:
        """Initialize the class."""

    def parse_function(
        self, content: list[dict[str, Any]] | dict[str, Any]
    ) -> list[FunctionDefinition]:
        """Validate the function file content.

        It is in the functions_definition file with all the
        name, parameters type, description and the returns type.

        Return:
            A list of pydantic validated or not with
            FunctionDefinition.
        """
        required_keys = {"name", "description", "parameters", "returns"}
        function_list = []

        try:
            if isinstance(content, list):
                for function in content:

                    if not required_keys.issubset(function.keys()):
                        sys.exit(
                            "Missing key in the "
                            '"data/input/functions_definition.json"'
                        )

                    function_list.append(
                        FunctionDefinition.model_validate(function)
                    )

            elif isinstance(content, dict):
                if not required_keys.issubset(content.keys()):
                    sys.exit("Missing key")

                function_list.append(
                    FunctionDefinition.model_validate(content)
                )
            return function_list

        except ValidationError as e:
            msg = e.errors()[0]['msg']
            print(f"Error found in the function file: {msg}")
            sys.exit()

    def parse_test(
        self, content: list[dict[str, Any]] | dict[str, Any]
    ) -> list[FunctionCallingTest] | FunctionCallingTest:
        """Parse the file with the user's question.

        Return an object validated by pydantic
        with FunctionCallingTest.

        Return:
            An list of object validated by pydantic.
        """
        required_keys = {"prompt"}

        try:
            if isinstance(content, list):
                input_test = []
                for item in content:
                    if not required_keys.issubset(item.keys()):
                        sys.exit('Missing key "prompt"')

                    input_test.append(
                        FunctionCallingTest.model_validate(item)
                    )
                return input_test

            if not required_keys.issubset(content.keys()):
                sys.exit('Missing key "prompt"')

            return FunctionCallingTest.model_validate(content)

        except ValidationError as e:
            msg = e.errors()[0]['msg']
            print(f"Error found in the tests file: {msg}")
            sys.exit()

    def parse_file(
        self,
        name: str,
    ) -> Any:
        """Open a file and read it with a json.load.

        It reads and decodes a JSON file and return a python object
        LIST or DICT

        Return:
            None if the file is not the excepted.
            The content validated by pydantic in a list.
        """
        try:
            with open(name, "r") as file:
                data = json.load(file)
            if len(data) == 0:
                sys.exit(f"Your file '{name}' has no content. Please check!!")

            if not (isinstance(data, (list, dict))):
                sys.exit(f"The file {name} must contain valid JSON format")

            if isinstance(data, list):
                for element in data:
                    if not isinstance(element, dict):
                        sys.exit(f"The file {name} must contain a JSON")

            return data

        except json.JSONDecodeError:
            sys.exit(f"You have an invalid format JSON in the file '{name}'")

        except PermissionError:
            sys.exit(f"No permission to open this file {name}.")

    def parsing_arguments(
        self,
    ) -> tuple[
        Path,
        list[FunctionDefinition],
        list[FunctionCallingTest] | FunctionCallingTest,
        str,
    ]:
        """Parse the arguments on the command line.

        Check if it exists by default or not.

        Return:
             a tuple with the path of the output
        with the list of functions validated on pydantic
        and the list or dictionnary of the input file with the tests.
        """
        try:
            parser = argparse.ArgumentParser()

            # c pour dire que --... est un arg
            # optionnel et que la valeur apres l'est aussi
            parser.add_argument(
                "--functions_definition",
                type=Path,
                default=Path(
                    "data/input/\
functions_definition.json"
                ),
            )

            parser.add_argument("--model", default="Qwen/Qwen3-0.6B")

            parser.add_argument(
                "--input",
                type=Path,
                default=Path(
                    "data/input/\
function_calling_tests.json"
                ),
            )

            parser.add_argument(
                "--output",
                type=Path,
                default=Path(
                    "data/output/\
function_calling_results.json"
                ),
            )

            # analyser les arguments donnes pour acceder a les valeurs
            args = parser.parse_args()

            if args.output.suffix != ".json":
                raise argparse.ArgumentTypeError(
                    f"the output file {args.output}"
                    " must be a .json file"
                )

            for file_path in [
                args.functions_definition,
                args.input
            ]:
                if file_path.suffix != ".json":
                    raise argparse.ArgumentTypeError(
                        f"the file {file_path} must be a '.json' file"
                    )
                if not file_path.exists():
                    raise argparse.ArgumentTypeError(
                        f"the file {file_path} doesn't exist..."
                    )
                if file_path == args.output:
                    raise parser.error(
                        "The input filename and the"
                        " output filename must be different"
                    )

            func_def = self.parse_function(
                self.parse_file(
                    args.functions_definition
                )
            )

            input_test = self.parse_test(
                self.parse_file(
                    args.input
                )
            )

            return Path(args.output), func_def, input_test, str(args.model)

        except ValidationError as e:
            sys.exit(f"{e}")
