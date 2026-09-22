import json
import sys
import os
from llm_sdk import Small_LLM_Model
from typing import Any
from pydantic import ValidationError
from .parsing_file import Parsing
from .model import FunctionResult
from .extract_params import ConstraintParams
from .gen_func_name import GenerationFuncName


model = Small_LLM_Model()


class Test:
    def __init__(self) -> None:
        self._parsed = Parsing()
        self._func = GenerationFuncName(model)
        self._param = ConstraintParams(model)

    def check_output(
        self,
        output: dict[str, Any] | list[dict[str, Any]]
    ) -> FunctionResult | list[FunctionResult] | None:
        """
        Validate the output gotten if it follows the appropriate type
        """
        try:
            if isinstance(output, dict):
                return FunctionResult(
                    prompt=output["prompt"],
                    name=output["name"],
                    parameters=output["parameters"]
                )
            return [
                FunctionResult(
                    prompt=item["prompt"],
                    name=item["name"],
                    parameters=item["parameters"]
                )
                for item in output
            ]
        except ValidationError as e:
            msg = e.errors()[0]["msg"]
            sys.exit(f"Error gotten: {msg}")

    def write_to_output(self, output: dict[str, Any]) -> None:
        name = self._parsed.parsing_arguments()[0]
        result = self.check_output(output)

        if result is None:
            sys.exit("Can't write in the output file")

        if isinstance(result, FunctionResult):
            output = result.model_dump()

        else:
            output = [
                res.model_dump()
                for res in result
            ]

        try:
            os.makedirs(os.path.dirname(name), exist_ok=True)
            with open(name, "w") as file:
                json.dump(output, file, indent=4)

        except PermissionError:
            sys.exit(f"No permission to open this file {name}.")

        except OSError:
            sys.exit(f"This file {name} already exists")

    def main(self) -> None:
        """
        The main of this projects where the projects
        do all of tests and write the output in the output_file
        """
        try:
            prompts = self._parsed.parsing_arguments()[2]

            if isinstance(prompts, list):
                output = []

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
                    print(param)

                    output.append({
                        "prompt": request,
                        "name": name,
                        "parameters": param
                    })

            else:
                output = {}
                p = prompts.prompt
                name = self._func.get_name_value(p)

                param = self._param.combine_param(name, p)
                print(param)

                output = {
                    "prompt": p,
                    "name": name,
                    "parameters": param
                }

            if output:
                self.write_to_output(output)
            print(output)
        except KeyboardInterrupt:
            sys.exit("Don't interrupt the process.")
