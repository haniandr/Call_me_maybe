from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any


prompt = "Replace all numbers in \"Hello I'm 34 bla bla\" with NUMBERS"

class State(str, Enum):
    START = auto()
    STRING = auto()
    SIGN = auto()
    NUMBER = auto()
    COMMA = auto()
    DECIMAL = auto()
    END = auto()


class TYPE_ARG(ABC):
    @abstractmethod
    def take_state(state: str, content: Any) -> None | State:
        ...


class STRING(TYPE_ARG):
    def take_state(state: State, char: Any) -> State | None:
        if state == State.START:
            return State.STRING
        if state == State.STRING:
            elif char == '"':
                return State.END
            return State.STRING
        return None


class NUMBER(TYPE_ARG):
    def take_state(state: State, char: Any) -> None | State:
        if state == State.START:
            if char in "-+":
                return State.SIGN
            if char.isdigit():
                return State.NUMBER
        if state == State.SIGN:
            if char.isdigit():
                return State.NUMBER
        if state == State.NUMBER:
            if char == ".":
                return State.COMMA
            if char == '"':
                return State.END
            elif char.isdigit():
                return State.NUMBER
        if state == State.COMMA:
            if char.isdigit():
                return State.DECIMAL
        if state == State.DECIMAL:
            if char.isdigit():
                return State.DECIMAL
            if char == '"':
                return State.END
        return None
