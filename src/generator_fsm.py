"""Generate the type value wanted of the function parameter."""

from typing import Any
from .statemachine import (
        FsmString,
        FsmInteger,
        FsmNumber
)
from llm_sdk import Small_LLM_Model  # type: ignore


class GenerationParams:
    """Generate a parameter value with constrained to restrict the result."""

    def __init__(
        self,
        prompt: str,
        model: Small_LLM_Model
    ) -> None:
        """Initialize the generator with the prompt and the LLM."""
        self._model = model
        self.prompt: str = prompt
        self.delimiters = {'"', "\n", ","}

    def _get_sorted_logits(self) -> list[int]:
        """Get the top 100 highest tokens in descending order."""
        input_ids = self._model.encode(self.prompt)

        logits = self._model.get_logits_from_input_ids(
            input_ids.tolist()[0]
        )

        return (sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
                )[:100])

    def gen_string_value(self) -> None | str:
        """Generate a string value token by token with the fsm."""
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
        """Generate an integer value token by token with its fsm."""
        integer = FsmInteger()
        i = 0

        while not integer.is_stopped() and i < 20:
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
            i += 1

        if not integer.is_stopped():
            return None

        return integer.value

    def gen_number_value(self) -> None | str:
        """Generate a decimal number token by token with its fsm."""
        number = FsmNumber()
        i = 0

        while not number.is_stopped() and i < 20:
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
            i += 1

        if not number.is_stopped():
            return None

        return number.value

    def gen_boolean_value(self) -> None | str:
        """Generate a boolean value with constrained True/False."""
        waited_value = ["true", "True", "false", "False"]

        value: str = ""

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

    def choose_function(self, param_type: str) -> Any:
        """Choose and cast the value into the parameter type."""
        if param_type == "number" or param_type == "float":
            return self.gen_number_value()

        elif param_type == "integer":
            return self.gen_integer_value()

        elif param_type == "boolean":
            return self.gen_boolean_value()

        return self.gen_string_value()
