import json
import sys
import os
from typing import Any
from pydantic import ValidationError
from parsing_file import Parsing
from model import FunctionResult
from extract_param import ConstraintParams
from gen_func_name import GenerationFuncName


class Browse:
    def __init__(self) -> None:
        self._parsed = Parsing()
        self._func = GenerationFuncName()
        self._param = ConstraintParams()

    def check_output(self, output: dict[str, Any]) -> list[FunctionResult] | None:
        try:
            verified_result = FunctionResult(
                prompt=output["prompt"],
                name=output["name"],
                parameters=output["parameters"]
            )
            return verified_result
        except ValidationError as e:
            msg = e.errors()[0]["msg"]
            sys.exit(f"Error gotten: {msg}")
        

    def write_to_output(self, output: dict[str, Any]) -> None:
        name = self._parsed.parsing_arguments()[0]
        result = self.check_output(output)
        if result:
            if isinstance(output, dict):
                output = {
                    "prompt": result.prompt,
                    "name": result.name,
                    "parameters": {
                        key: param
                        for key, param in result.parameters.items()
                    }
                }
            elif isinstance(output, list):
                output = []
                for res in result:
                    output.append({
                        "prompt": result.prompt,
                        "name": result.name,
                        "parameters": {
                            key: param
                            for key, param in result.parameters.items()
                        }
                    })

        try:
            with open(name, "w") as file:
                json.dump(output, file, indent=4)

        except json.JSONDecodeError:
            sys.exit(f"You have an invalid format JSON in the file '{name}'")

        except ValidationError as e:
            sys.exit(f"Error found: {e}")

        except os.OSError:
            sys.exit(f"This file {name} already exists")

        except PermissionError:
            sys.exit(f"No permission to open this file {name}.")


    def browse_prompt(self) -> None:
        prompts = self._parsed.parsing_arguments()[2]


        if len(prompts) > 1:
            output = []
            for p in prompts.prompt.prompt.prompt.value:
                try:
                    name = self._func.get_name_value(p)
                    param = self._param.combine_param(p)
                    output.append({
                        "prompt": p,
                        "name": name,
                        "parameters": param
                    })
                except Exception:
                    sys.exit("No parameter or function generated")

        else:
            p = prompts.prompt.prompt.value
            try:
                name = self._func.get_name_value(p)
                param = self._param.combine_param(p)
                output.append({
                    "prompt": p,
                    "name": name,
                    "parameters": param
                })
                except Exception:
                    sys.exit("No parameter or function generated")


        if output:
            self.write_to_output(output)
