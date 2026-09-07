from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any
from llm_sdk import Small_LLM_Model


class State(str, Enum):
    START = auto()
    STRING = auto()
    SIGN = auto()
    NUMBER = auto()
    COMMA = auto()
    DECIMAL = auto()
    END = auto()


prompt = ""

class TYPEARG(ABC):
    @abstractmethod
    def take_state(state: State, char: Any) -> None | State:
        ...

    def func_verify(self, state: State, content: str) -> None:
        for char in content:
            if self.take_state(state, char) is None:
                return None
        return state


class STRING(TYPEARG):
    def take_state(state: State, char: Any) -> State | None:
        if state == State.START:
            return State.STRING
        if state == State.STRING:
            if char == '"':
                return State.END
            return State.STRING
        return None


class NUMBER(TYPEARG):
    def take_state(state: State, char: Any) -> None | State:
        if state == State.START:
            if char in "-+":
                return State.SIGN
            if char.isdigit():
                return State.NUMBER
        if state == State.SIGN and char.isdigit():
                return State.NUMBER
        if state == State.NUMBER:
            if char == ".":
                return State.COMMA
            if char == '"':
                return State.END
            elif char.isdigit():
                return State.NUMBER
        if state == State.COMMA and char.isdigit():
                return State.DECIMAL
        if state == State.DECIMAL:
            if char.isdigit():
                return State.DECIMAL
            if char == '"':
                return State.END
        return None


class BOOLEAN(TYPEARG):
    ...


class ConstraintParams:
    def __init__(self) -> None:
        self.prompt = prompt
        self._model = Small_LLM_Model()
        self._arg = TYPEARG()

    def choose_type_state(self, name: str) -> None:
        if name == "string":
            self._arg = STRING()
        elif name == "number":
            self._arg = NUMBER()
        elif name == "boolean":
            self._arg = BOOLEAN()

    def extract_params(self, all_params) -> State:
        for param in all_params.key():
            self.prompt += f'"{param}": '
            state = State.START
            while state != State.END:
                input_ids = self._model.encode(self.prompt)
                logits = self._model.get_logits_from_input_ids(
                    input_ids.tolist()[0]
                )
                sorted_logits = sorted(
                    range(len(logits)),
                    key=lambda x: logits[x],
                    reverse=True,
                )
                for token in sorted_logits:
                    word = self._model.decode(token)
                    self.choose_type_state(all_params[param])
                    current_state = self._arg.func_verify(state, word)
                    if current_state is None:
                        continue
                    self.prompt += token + ","
                    state = current_state

