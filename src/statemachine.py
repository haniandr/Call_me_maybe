"""Finite State Machine used to validate the result generated."""

from enum import Enum, auto
from typing import Any


class State(str, Enum):
    """States shared by all the fsm."""

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
    """Finite State Machine that parses a string.

    Check if it agrees with states.
    """

    def __init__(self) -> None:
        """Initialize the machine with the value and state."""
        self.value = ""
        self.state: State | None = State.START

    def take_next_state(
        self,
        state: State | None,
        char: Any
    ) -> State | None:
        """Return the next state that validate that reaches the fsm.

        Arguments:
        state: the actual state
        char: the character to check where in the fsm.
        """
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
        """Verify if the content is accepted with the fsm."""
        state: State | None = self.state

        for char in content:
            state = self.take_next_state(state, char)
            if state is None:
                return False

        return True

    def check_and_load(self, content: str) -> bool:
        """Check the content against the fsm and load it."""
        for char in content:
            next_state: State | None = self.take_next_state(
                self.state,
                char
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
        """Verify if the state is in the case finished or not."""
        return self.state == State.END


class FsmNumber:
    """Finite State Machine that parses a decimal value."""

    def __init__(self) -> None:
        """Initialize the State Machine with delimiters specified."""
        self.value = ""
        self.state = State.START
        self.delimiters = {'"', "\"", "\n"}

    def take_next_state(
        self,
        state: State | None,
        char: Any
    ) -> None | State:
        """Return the state reached from a `char`.

        Arguments:
        state: the actual state
        char: the character to check where in the fsm.
        """
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
        """Verify the state for each character."""
        state: State | None = self.state

        for char in content:
            state = self.take_next_state(state, char)
            if state is None:
                return False

        return True

    def check_and_load(self, content: str) -> bool:
        """Check the content against the fsm and load it."""
        for char in content:
            next_state = self.take_next_state(
                self.state,
                char
            )

            if next_state is None:
                return False

            if next_state in (
                State.SIGN,
                State.NUMBER,
                State.COMMA,
                State.DECIMAL,
            ):
                self.value += char

            self.state = next_state

        return True

    def is_stopped(self) -> bool:
        """Verify if it's the state is in case to be finished."""
        return self.state in (
            State.DECIMAL,
            State.END,
        )


class FsmInteger:
    """Finite State Machine that parses an integer value."""

    def __init__(self) -> None:
        """Initialize the machine with delimiters, value, state."""
        self.value = ""
        self.state = State.START
        self.delimiters = {'"', "\n", ","}

    def take_next_state(
        self,
        state: State | None,
        char: Any
    ) -> State | None:
        """Return the state reached from a char.

        Arguments:
        state: the actual state
        char: the character to check where in the fsm.
        """
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
        """Check each character in the string with the actual state."""
        state: State | None = self.state

        for char in content:
            next_state = self.take_next_state(state, char)
            if next_state is None:
                return False
            state = next_state

        return True

    def check_and_load(self, content: str) -> bool:
        """Check the content against the fsm and load it."""
        for char in content:
            next_state = self.take_next_state(
                self.state,
                char
            )

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
        """Check is the actual state is at the END."""
        return self.state == State.END
