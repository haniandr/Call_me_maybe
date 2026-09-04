from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any


prompt = "Replace all numbers in \"Hello I'm 34 bla bla\" with NUMBERS"

class State(str, Enum):
    START = auto()
    WAIT_QUOTE = auto()
    CONTENT = auto()
    END = auto()


class TYPE_ARG(ABC):
    @abstractmethod
    def take_state(state: str, content: Any) -> None:
        ...


class STRING(TYPE_ARG):
    def take_state(state: str, char: str) -> str:
        if char == ' ':
            return state
        if state == "START":
            if char == ' ':
                return "START"
            else:
                return "STRING"
        elif state == "STRING":
            return "WAIT_QUOTE" if char else None
        elif state == "WAIT_QUOTE":
            return "END" if char == '"' else None
        return None


class NUMBER(TYPE_ARG):
    def take_state(state: str, char: Any) -> None:
        if state == "START":
            if char == '-' or char == '+':
                return "SIGN"
            return "NUMBERS"
        elif state == "SIGN":
            return "NUMBERS"
        elif state == "NUMBERS":
            if char == ".":
                return "COMMA"
            elif char.isdigit():
                return "WAIT_QUOTE"
            else:
                return None
        if state == "COMMA":
            return "DECIMAL" if char else None
        if state == "DECIMAL":
            if char.isdigit():
                return "WAIT_QUOTE"
            return None
        return None
