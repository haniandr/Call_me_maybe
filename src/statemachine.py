from enum import Enum, auto
from typing import Any


class State(str, Enum):
    START = auto()
    STRING = auto()
    SIGN = auto()
    NUMBER = auto()
    COMMA = auto()
    ESCAPE = auto()
    INTEGER = auto()
    DECIMAL = auto()
    END = auto()


class FsmString:
    def __init__(self) -> None:
        self.value = ""
        self.state = State.START

    def take_next_state(
        self,
        state: State,
        char: Any
    ) -> State | None:
        if state == State.START:
            return State.STRING

        if state == State.STRING:
            if char == '"':
                return State.END
            elif char == "\\":
                return State.ESCAPE
            return State.STRING

        if state == State.ESCAPE:
            if char in '"\\/vntrfb':
                return State.STRING
            return None

        if state == State.END:
            return None
        return None

    def verify_content(self, content: str) -> bool:
        """
        Verify if the content is accepted by the fsm 
        without modifying the actual state.
        """
        state = self.state
        for char in content:
            state = self.take_next_state(state, char)
            if state is None:
                return False
        return True
        
    def check_and_load(self, content: str) -> bool:
        for char in content:
            next_state = self.take_next_state(
                self.state, char
            )
            if self.state == State.START:
                self.state = State.STRING

            if self.state == State.STRING:
                if char == '"':
                    self.state = State.END
                elif char == "\\":
                    self.state = State.ESCAPE
                else:
                    self.value += char
                    self.state = next_state
                continue
            if self.state == State.ESCAPE:
                self.value += char
                self.state = State.STRING
                continue
            else:
                return False
        return True

    def is_stopped(self) -> bool:
        """
        Verify if the state is in the case finished or not.
        """
        return self.state == State.END


class FsmNumber:
    def __init__(self) -> None:
        self.value = ""
        self.state = State.START
        self.delimiters = {'"', "\"", "\n"}

    def take_next_state(self, state: State, char: Any) -> None | State:
        if state == State.START:
            if char in "-+":
                return State.SIGN

            if char.isdigit():
                return State.NUMBER

            return None

        if state == State.SIGN:
            if char.isdigit():
                return State.NUMBER

            return None

        if state == State.NUMBER:
            if char == ".":
                return State.COMMA

            elif char.isdigit():
                return State.NUMBER

            elif char in self.delimiters:
                return State.END

            return None

        if state == State.COMMA:
            if char.isdigit():
                return State.DECIMAL

            return None

        if state == State.DECIMAL:
            if char.isdigit():
                return State.DECIMAL

            if char in self.delimiters:
                return State.END

            return None

        return None

    def verify_content(self, content: str) -> bool:
        """
        Verify the state if it's valid for every
        character in the gotten string.
        """
        state = self.state
        for char in content:
            state = self.take_next_state(state, char)
            if state is None:
                return False
        return True

    def check_and_load(self, content: str) -> bool:
        """
        Check the content gotten if 
        it follows the fsm and load it in the result
        """
        for char in content:
            next_state = self.take_next_state(self.state, char)
            if next_state is None:
                return False

            if next_state in (
                State.SIGN,
                State.NUMBER,
                State.COMMA,
                State.DECIMAL
            ):
                self.value += char

            self.state = next_state
        return True

    def is_stopped(self) -> bool:
        return self.state in (
            State.DECIMAL,
            State.END
        )


class FsmInteger:
    def __init__(self) -> None:
        self.value = ""
        self.state = State.START
        self.delimiters = {'"', "\n", ","}

    def take_next_state(self, state: State, char: Any) -> State:
        if state == State.START:
            if char in "-+":
                return State.SIGN

            if char.isdigit():
                return State.INTEGER

            if char.isspace():
                return State.START

            return None

        elif state == State.SIGN:
            if char.isdigit():
                return State.INTEGER

            return None

        if state == State.INTEGER:
            if char.isdigit():
                return State.INTEGER

            if char in self.delimiters:
                return State.END

            return None

        return None

    def verify_content(self, content: str) -> bool:
        """
        Check every character in the gotten string
        if it follows the fsm state
        """
        state = self.state
        for char in content:
            state = self.take_next_state(state, char)
            if state is None:
                return False
        return True

    def check_and_load(self, content: str) -> bool:
        """
        Check the content gotten if 
        it follows the fsm and load it in the result
        """
        for char in content:
            next_state = self.take_next_state(self.state, char)
            if next_state is None:
                return False

            if next_state in (
                State.SIGN,
                State.INTEGER,
            ):
                self.value += char

            self.state = next_state
        return True

    def is_stopped(self) -> bool:
        return self.state == State.END
