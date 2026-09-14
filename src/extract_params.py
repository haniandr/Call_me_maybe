from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any
from llm_sdk import Small_LLM_Model
from parsing.parsing_function import Parsing
from gen_func_name import GenerationFuncName


model = Small_LLM_Model()

class State(str, Enum):
    START = auto()
    STRING = auto()
    SIGN = auto()
    NUMBER = auto()
    COMMA = auto()
    DECIMAL = auto()
    END = auto()


prompt = """
Extract the parameters from the user's query for each functions

Choose well which type and value should fill the parameter's value.

The functions with their appropriate arguments:
{func_param_list}


parameters: {type}
"{param_key}": 
"""

class FsmString:
    def __init__(self) -> None:
        self.result = ""
        self.state = State.START

    def take_next_state(
        self,
        state: State,
        char: Any
    ) -> State | None:
        if state == State.START:
            if char == '"':
                return State.STRING
            return None

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
        Verify the state if it's valid for every
        character in the gotten string.
        """
        for char in content:
            state = self.take_next_state(self.state, char)
            if state is None:
                return False
        return True
        
    def check_and_load(self, content: str) -> bool:
        for char in content:
            if self.state == State.START:
                self.state = State.STRING
            if self.state == State.STRING:
                if char == '"':
                    self.state = State.END
                elif char == "\\":
                    self.state = State.ESCAPE
                else:
                    self.value += char
            elif self.state == State.ESCAPE:
                self.value += char
                self.state = State.STRING
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

    def take_state(self, state: State, char: Any) -> None | State:
        if state == State.START:
            if char in "-+":
                return State.SIGN
            if char.isdigit():
                return State.NUMBER
            return None

        if state == State.SIGN and char.isdigit():
                return State.NUMBER

        if state == State.NUMBER:
            if char == ".":
                return State.COMMA
            elif char.isdigit():
                return State.NUMBER
            elif char in self.delimiters:
                return State.END
            return None

        if state == State.COMMA and char.isdigit():
                return State.DECIMAL

        if state == State.DECIMAL:
            if char.isdigit():
                return State.DECIMAL
            if char in self.delimiters:
                return State.END

        return None

    def verify_content(self, content: str) -> bool:
        """
        Verify the state if it's valid for every
        character in the gotten string.
        """
        state = self.state
        for char in content:
            state = self.take_next_state(self.state, char)
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


class FsmInteger:
    def __init(self) -> None:
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
            next_state = self.take_next_state(state, char)
            if next_state is None:
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
        return self.state in (State.INTEGER, State.END)


class GenerationParams:
    def __init__(self, prompt: str) -> None:
        self._model = model
        self.prompt = prompt
        self.delimiters = {'"', "\n", ","}

    def gen_string_value(self) -> None | str:
        while True:
            input_ids = self._model.encode(self.prompt).tolist()[0]
            logits = self._model.get_logits_from_input_ids(input_ids)

            string = FsmString()

            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if string.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)
            if string.check_and_load(word):
                self.prompt += word

            if string.is_stopped():
                break

        if not string.is_stopped():
            return None

        return string.value

    def gen_integer_value(self) -> None | str:
        while True:
            input_ids = self._model.encode(self.prompt).tolist()[0]
            logits = self._model.get_logits_from_input_ids(input_ids)

            integer = FsmInteger()

            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if integer.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)
            if integer.check_and_load(word):
                self.prompt += word

            if integer.is_stopped():
                break

        if not integer.is_stopped():
            return None

        return integer.value

    def gen_number_value(self) -> None | str:
        while True:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )

            number = FsmNumber()

            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            token_id = None

            for token in sorted_logits:
                chosen = self._model.decode(token)
                if number.verify_content(chosen):
                    token_id = token
                    break

            if token_id is None:
                break

            word = self._model.decode(token_id)
            if number.check_and_load(word):
                self.prompt += word

            if number.is_stopped():
                break

        if not number.is_stopped():
            return None

        return number.value

    def gen_boolean_value(self) -> None | str:
        waited_value = ["true", "True", "false", "False"]

        value = ""

        while True:
            input_ids = self._model.encode(self.prompt).tolist()[0]
            logits = self._model.get_logits_from_input_ids(input_ids)

            waited_token = self._model.encode(waited_value)

            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            chosen = None

            for token in sorted_logits:
                if token in waited_token:
                    chosen = token
                    break
            if chosen is not None:
                word = self._model.decode(chosen)
                value += word
                break

        return value


    def choose_function(self, param_type: str) -> None | str:
        if param_type == "number" or param_type == "float":
            return self.gen_number_value()

        elif param_type == "integer":
            return self.gen_integer_value()

        elif param_type == "boolean":
            return self.gen_boolean_value()

        else:
            return self.gen_string_value()


class ConstraintParams:
    def __init__(self) -> None:
        self.prompt = ""
        self._model = model
        self._func = GenerationFuncName()
        self._param = GenerationParams(self.prompt)

    def get_param_func(self) -> list[dict[str, Any]]:
        """
        Get a dictionary of the function name as a key
        and its available parameters as values
        """
        func_list = Parsing.parse_file("data/input/functions_definition.json")
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
#
#     def choose_type_state(self, name: str) -> None:
#         if name == "string":
#             self._arg = STRING()
#             self.prompt += '"'
#         elif name == "number":
#             self._arg = NUMBER()
#         elif name == "boolean":
#             self._arg = BOOLEAN()
#         elif name == "integer" or name == "float":
#             self._arg = NUMBER()
#
    # def generate_param(self) -> str:
    #     """
    #     Generate only the parameters by the LLM model.
    #     """
    #     result = ""
    #     state = State.START
    #     while state != State.END:
    #         input_ids = self._model.encode(self.prompt)
    #         logits = self._model.get_logits_from_input_ids(
    #             input_ids.tolist()[0]
    #         )
    #         sorted_logits = sorted(
    #             range(len(logits)),
    #             key=lambda x: logits[x],
    #             reverse=True
    #         )
    #
    #         for token in sorted_logits:
    #             word = self._model.decode(token)
    #             current_state = self._arg.func_verify(state, word)
    #             if current_state is None:
    #                 continue
    #             self.prompt += word
    #             state = current_state
    #             result += word
    #             break
    #     return result
    #

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
        func_list = self.get_param_func()

        all_params = {}
        for func in func_list:
            all_params[func["name"]] = func["parameters"]

        param_result = {}
        for func_name, param in all_params.items():
            if func_name == name_func:
                for param_key, param_type in param.items():
                    # self.choose_type_state(param_type)
                    self.prompt = self.create_prompt(
                        query=request,
                        func_param_list=all_params,
                        param_key=param_key,
                        types = param_type
                    )

                    res = self._param.choose_function(param_type)
                    if res:
                        param_result[param_key] = "".join(res.strip('"'))
        return param_result

    def create_prompt(
        self,
        query: str,
        func_param_list: dict[str, str],
        param_key: str,
        types: str
    ) -> str:
        return f"""
query: {query}
Give the appropriate parameters for each functions from the user's query.

Choose well which type and value should fill the parameter's value.

The functions with their appropriate arguments:
{func_param_list}

parameters: {types}
"{param_key}": "
"""


if __name__ == "__main__":
    param = ConstraintParams()
    request = "What is the sum of 4 and 3?"
    func = GenerationFuncName()
    name = func.get_name_value(request)
    print(param.combine_param(name, request))
