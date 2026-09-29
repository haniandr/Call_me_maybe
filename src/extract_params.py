"""Extract the parameter values of a function from a natural langage."""

import sys
from typing import Any
from .gen_func_name import GenerationFuncName
from llm_sdk import Small_LLM_Model  # type: ignore
from .generator_fsm import GenerationParams


class ConstraintParams:
    """Build prompts and extract the typed parameters of a function."""

    def __init__(
        self,
        model: Small_LLM_Model
    ) -> None:
        """Initialize the extractor with the given LLM model."""
        self.prompt: str = ""
        self.model = model
        self._param: GenerationParams | None = None
        self._func = GenerationFuncName(model)

    def get_param_func(self) -> list[dict[str, Any]]:
        """Get the available function with their parameters.

        Return:
        A list of dictionary with function name and parameters
        for each element inside.
        """
        func_list = self._func.get_func_list()

        needed_list = []
        if isinstance(func_list, list):
            for func in func_list:
                needed_list.append({
                    "name": func["name"],
                    "parameters": func["parameters"]
                })
        else:
            needed_list.append({
                "name": func_list["name"],
                "parameters": func_list["parameters"]
            })

        return needed_list

    def transform_to_real_type(
            self,
            param_type: str,
            word: str
    ) -> Any:
        """Convert a word to the type matching the `param_type`."""
        if param_type in ("number", "float"):
            return float(word)

        elif param_type == "integer":
            return int(word)

        elif param_type == "boolean":
            return bool(word)

        return word

    def combine_param(
            self,
            name_func: str,
            request: str
    ) -> dict[str, Any]:
        """Combine all of the process to get the param's value.

        It follows the appropriate type according
        to the function name.

        Args:
            name_func: name of the function obtained by the LLM
            request: prompt given from the parsing_file
        """
        try:
            func_list = self.get_param_func()

            all_params = {}
            for func in func_list:
                all_params[func["name"]] = func["parameters"]

            param_result = {}
            for func_name, param in all_params.items():
                self.prompt = ""
                if func_name != name_func:
                    continue
                elif func_name == name_func:
                    for param_key, param_type in param.items():
                        self.prompt += self.create_prompt(
                            query=request,
                            func_param=name_func,
                            param_key=param_key,
                            types=param_type
                        )

                        self._param = GenerationParams(self.prompt, self.model)

                        res = self._param.choose_function(param_type)
                        if res:
                            res_typed = self.transform_to_real_type(
                                param_type, res
                            )
                            param_result[param_key] = res_typed
                            self.prompt += res + '"\n'
            return param_result
        except KeyboardInterrupt:
            sys.exit("Still generating the parameters :(!!")

    def create_prompt(
        self,
        query: str,
        func_param: str,
        param_key: str,
        types: str
    ) -> str:
        """Create prompt base used to extract the parameters.

        Arguments:
        query: the query given by the user
        func_param: name of the function for the query
        param_key: the key of the parameter to generate
        types: type of the parameter to fill
        """
        return f"""Extract the value.

query: {query}

Functions:
{func_param}

parameters: {types}
{param_key}: \""""
