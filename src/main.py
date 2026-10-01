"""Test all the functions from parsing to parameters."""

import json
import os
import sys
from argparse import ArgumentTypeError
from typing import Any

from pydantic import ValidationError

from llm_sdk import Small_LLM_Model  # type: ignore

from .extract_params import ConstraintParams
from .gen_func_name import GenerationFuncName
from .model import FunctionResult
from .parsing_file import Parsing


class Test:
    """Main to test the generation and write the output."""

    def __init__(self) -> None:
        """Initialize the function, parameters, LLM class."""
        self._parsed = Parsing()
        self.model = Small_LLM_Model()
        self._func = GenerationFuncName(self.model)
        self._param = ConstraintParams(self.model)

    def check_output(
        self,
        output: dict[str, Any] | list[dict[str, Any]]
    ) -> FunctionResult | list[FunctionResult] | None:
        """Validate the output gotten if it follows the type wanted."""
        try:
            if isinstance(output, dict):
                return FunctionResult.model_validate(
                    output
                )
            return [
                FunctionResult.model_validate(
                    item
                )
                for item in output
            ]
        except ValidationError as e:
            msg = e.errors()[0]["msg"]
            sys.exit(f"Error gotten: {msg}")

    def write_to_output(
            self,
            output: dict[str, Any] | list[dict[str, Any]]
    ) -> None:
        """Write the output validated in the file.

        Arguments:
        the result gotten not validated yet.
        """
        try:
            name = self._parsed.parsing_arguments()[0]
            result = self.check_output(output)

            if result is None:
                sys.exit("Can't write in the output file")

            if isinstance(result, list):
                output = [
                    res.model_dump()
                    for res in result
                ]
            else:
                output = result.model_dump()

            os.makedirs(os.path.dirname(name), exist_ok=True)
            with open(name, "w") as file:
                json.dump(output, file, indent=4)

        except ArgumentTypeError as e:
            sys.exit(f"Error: {e}")

        except PermissionError:
            sys.exit(f"No permission to open this file {name}.")

        except OSError:
            sys.exit(f"This file {name} already exists")

    def main(self) -> None:
        """Combine the process from the function to the parameters.

        Then launch the function that writes the content.
        """
        try:
            arg_model = self._parsed.parsing_arguments()[3]
            if arg_model != "Qwen/Qwen3-0.6B":
                self.model = Small_LLM_Model(arg_model)

            prompts = self._parsed.parsing_arguments()[2]

            output: Any

            if isinstance(prompts, list):
                results: list[dict[str, Any]] = []

                i = 0
                print("⏳ The output generation:")
                for p in prompts:
                    request = p.prompt

                    name = self._func.get_name_value(request)
                    if name is None:
                        print("The function has no name, the generation "
                              "stops here...")
                        continue

                    param = self._param.combine_param(
                        name,
                        request
                    )

                    results.append({
                        "prompt": request,
                        "name": name,
                        "parameters": param
                    })
                    print(json.dumps(results[i], indent=4))
                    i += 1
                output = results

            else:
                result: dict[str, Any] = {}
                prompt_ = prompts.prompt

                name = self._func.get_name_value(prompt_)
                if name is None:
                    sys.exit("The function has no name, "
                             "the generation stops here...")

                param = self._param.combine_param(name, prompt_)

                result = {
                    "prompt": prompt_,
                    "name": name,
                    "parameters": param
                }
                output = result
                print("⏳ The output generation:")
                print(json.dumps(output, indent=4))

            if output:
                self.write_to_output(output)

        except ArgumentTypeError as e:
            sys.exit(f"There is an error: {e}")

        except KeyboardInterrupt:
            sys.exit("Don't interrupt the process.")
