"""Generate the function name matching the user's request."""

import sys
from typing import Any

from llm_sdk import Small_LLM_Model  # type: ignore

from .parsing_file import Parsing


class GenerationFuncName:
    """Choose a function name with the LLM, token by token."""

    def __init__(self, model: Small_LLM_Model) -> None:
        """Initialize the generator with the given LLM model."""
        self._model = model
        self.prompt = ""
        self._parsed = Parsing()

    def get_func_list(
            self
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get the available functions with their details.

        Return:
        A list of dictionary or a dictionary
        of the functions existing in the funcyions_definition file
        """
        func_def_list = []

        function_list = self._parsed.parsing_arguments()[1]

        for function in function_list:
            func_def_list.append({
                "name": function.name,
                "description": function.description,
                "parameters": {
                    key: param.type.value
                    for key, param in function.parameters.items()
                },
                "returns": function.returns.type.value
            })
        return func_def_list

    def get_func_name(self) -> dict[str, str]:
        """Get the available function names.

        Return only a content with the function name and the description
        """
        func_list = self.get_func_list()
        func_name = {}

        if isinstance(func_list, list):
            for element in func_list:
                func_name[element["name"]] = element["description"]

        elif isinstance(func_list, dict):
            func_name[func_list["name"]] = func_list["description"]

        return func_name

    def create_prompt(
        self,
        query: str,
        functions: dict[str, str]
    ) -> str:
        """Create prompt to generate the function name.

        Arguments:
        query: the user's prompt
        functions: all the available function with their description each
        """
        new = "".join(
            f" - {name}: {description}\n"
            for name, description in functions.items()
        )
        return f"""Give the appropriate function name \
according to the user's query.

query: {query}

Functions:
{new}

name: """

    def get_name_value(self, request: Any) -> Any:
        """Generate the name of the function matching the request.

        Arguments:
        request: prompt

        Return:
        A dict with the key as name and the name gotten as value
        """
        i = 0
        result: list[int] = []

        try:
            func_name = self.get_func_name()

            self.prompt = self.create_prompt(
                query=request,
                functions=func_name
            )

            function_token = [
                self._model.encode(name).tolist()[0]
                for name in func_name
            ]

            while True:
                input_ids = self._model.encode(self.prompt)
                logits = self._model.get_logits_from_input_ids(
                    input_ids.tolist()[0]
                )

                candidates = [
                    name[i]
                    for name in function_token
                    if i < len(name) and name[:i] == result
                ]

                if not candidates:
                    break

                score = float('-inf')
                token = 0

                for id in candidates:
                    if logits[id] > score:
                        token = id
                        score = logits[id]

                result.append(token)
                word = self._model.decode(token)
                self.prompt += word
                i += 1

            return self._model.decode(result).strip()

        except KeyboardInterrupt:
            sys.exit("\nThe name can't be generated.")
