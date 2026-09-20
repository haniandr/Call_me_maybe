from typing import Any
from .statemachine import (
        FsmString,
        FsmInteger,
        FsmNumber
)
from .gen_func_name import GenerationFuncName
from llm_sdk import Small_LLM_Model


class GenerationParams:
    def __init__(
        self,
        prompt: str,
        model: Small_LLM_Model
    ) -> None:
        self._model = model
        self.prompt: str = prompt
        self.delimiters = {'"', "\n", ","}

    def _get_sorted_logits(self) -> list[int]:
        input_ids = self._model.encode(self.prompt)

        logits = self._model.get_logits_from_input_ids(
            input_ids.tolist()[0]
        )

        return sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

    def gen_string_value(self) -> None | str:
        string = FsmString()
        while not string.is_stopped():
            sorted_logits = self._get_sorted_logits()
            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if string.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)

            if not string.check_and_load(word):
                return None

            self.prompt += word

        return string.value

    def gen_integer_value(self) -> None | str:
        integer = FsmInteger()

        while not integer.is_stopped():
            sorted_logits = self._get_sorted_logits()

            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if integer.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)

            if not integer.check_and_load(word):
                return None

            self.prompt += word

        if not integer.is_stopped():
            return None

        return integer.value

    def gen_number_value(self) -> None | str:
        number = FsmNumber()

        while not number.is_stopped():
            sorted_logits = self._get_sorted_logits()

            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if number.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)
            if not number.check_and_load(word):
                return None
    
            self.prompt += word

        if not number.is_stopped():
            return None

        return number.value

    def gen_boolean_value(self) -> None | str:
        waited_value = ["true", "True", "false", "False"]

        value = ""

        sorted_logits = self._get_sorted_logits()

        waited_token = []

        for item in waited_value:
            ids = self._model.encode(item).tolist()[0]
            waited_token.extend(ids)

        while True:
            input_ids = self._model.encode(self.prompt).tolist()[0]
            logits = self._model.get_logits_from_input_ids(input_ids)

            waited_token = self._model.encode(waited_value)

            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            for token in sorted_logits:
                if token in waited_token:
                    word = self._model.decode(token)
                    value += word
                    return value

        return None


    def choose_function(self, param_type: str) -> None | str:
        if param_type == "number" or param_type == "float":
            return self.gen_number_value()

        elif param_type == "integer":
            return self.gen_integer_value()

        elif param_type == "boolean":
            return self.gen_boolean_value()

        return self.gen_string_value()


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
                "parameters": {
                    key: value
                    for key, value in func["parameters"].items()
                }
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
            request: str
    ) -> dict[str, Any]:
        """
        Combine all of the process to get the param's value
        following the appropriate type according
        to the function name.

        Args:
            name_func: name of the function obtained by the LLM
        """

        name_func = self._func.get_name_value(request)

        func_list = self.get_param_func()

        all_params = {}
        for func in func_list:
            all_params[func["name"]] = func["parameters"]

        param_result = {}
        for func_name, param in all_params.items():
            if func_name == name_func:
                for param_key, param_type in param.items():
                    self.prompt = self.create_prompt(
                        query=request,
                        func_param=name_func["name"],
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
        return param_result

    def create_prompt(
        self,
        query: str,
        func_param: dict[str, str],
        param_key: str,
        types: str
    ) -> str:
        return f"""Only change the value when necessary.

query: {query}

Functions:
{func_param}

parameters:
{param_key}: \""""

