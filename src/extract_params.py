import sys
from typing import Any
from .gen_func_name import GenerationFuncName
from llm_sdk import Small_LLM_Model
from .generator_fsm import GenerationParams


class ConstraintParams:
    def __init__(
        self,
        model: Small_LLM_Model
    ) -> None:
        self.prompt: str = ""
        self.model = model
        self._param = None
        self._func = GenerationFuncName(model)

    def get_param_func(self) -> list[dict[str, Any]]:
        """
        Get a dictionary of the function name as a key
        and its available parameters as values
        """
        func_list = self._func.get_func_list()
        needed_list = []
        for func in func_list:
            needed_list.append({
                "name": func["name"],
                "parameters": func["parameters"]
            })

        return needed_list

    def transform_to_real_type(self, param_type: str, word: str) -> Any:
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
        """
        Combine all of the process to get the param's value
        following the appropriate type according
        to the function name.

        Args:
            name_func: name of the function obtained by the LLM
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
                            types = param_type
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
        func_param: dict[str, str],
        param_key: str,
        types: str
    ) -> str:
        return f"""Extract the value.

query: {query}

Functions:
{func_param}

parameters: {types}
{param_key}: \""""

#
# def main():
#     model = Small_LLM_Model()
#     param = ConstraintParams(model)
#     func = GenerationFuncName(model)
#
#     # prompt = "What is the sum of 5 and 3?"
#     # name = func.get_name_value(prompt)
#     # print(param.combine_param(name, prompt))
#     prompt = Parsing().parsing_arguments()[2]
#     # print(type(prompt))
#     if isinstance(prompt, list):
#          for p in prompt:
#             request = p.prompt
#             name = func.get_name_value(request)
#             print(param.combine_param(name, request))
#
#     else:
#         p = prompt.prompt
#         name = func.get_name_value(p)
#         print(param.combine_param(name,p))
#
#
# if __name__ == "__main__":
#     main()
