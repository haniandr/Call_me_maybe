from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any
from llm_sdk import Small_LLM_Model
from src.parsing.parsing_function import Parsing
from src.gen_func_name import GenerationFuncName


class State(str, Enum):
    START = auto()
    STRING = auto()
    SIGN = auto()
    NUMBER = auto()
    COMMA = auto()
    DECIMAL = auto()
    END = auto()


prompt = """
Extract the right parameters for each functions 
following the type matched for the functions/
Choose well which type and value should fill the parameter's value.

The functions with their appropriate arguments:
{func_param_list}

parameters:
"{param_key}":  
"""

class TYPEARG(ABC):
    @abstractmethod
    def take_state(self, state: State, char: Any) -> None | State:
        ...

    def func_verify(self, state: State, content: str) -> None | State:
        for char in content:
            state = self.take_state(state, char)
            if state is None:
                return None
        return state


class STRING(TYPEARG):
    def take_state(self, state: State, char: Any) -> State | None:
        if state == State.START:
            return State.STRING
        if state == State.STRING:
            if char == '"':
                return State.END
            return State.STRING
        return None


class NUMBER(TYPEARG):
    def take_state(self, state: State, char: Any) -> None | State:
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
            elif char.isdigit():
                return State.NUMBER
            else:
                return State.END
        if state == State.COMMA and char.isdigit():
                return State.DECIMAL
        if state == State.DECIMAL:
            if char.isdigit():
                return State.DECIMAL
            else:
                return State.END
        return None


class BOOLEAN(TYPEARG):
    ...


class ConstraintParams:
    def __init__(self) -> None:
        self.prompt = ""
        self._model = Small_LLM_Model()
        self._arg = TYPEARG()
        self._func = GenerationFuncName()

    def get_param_func(self) -> list[dict[str, Any]]:
        func_list = Parsing().parse_file("data/input/functions_calling_definition.json")
        needed_list = []
        for func in func_list:
            needed_list.append({
                "name": func.name,
                "parameters": {
                    key: value
                    for key, value in func.parameters.items()
                }
            })
        return needed_list

    def choose_type_state(self, name: str) -> None:
        if name == "string":
            self._arg = STRING()
            self.prompt += '"'
        elif name == "number":
            self._arg = NUMBER()
        elif name == "boolean":
            self._arg = BOOLEAN()
        elif name == "integer" or name == "float":
            self._arg = NUMBER()

    def generate_param(self) -> str:
        """
        Generate only the parameters by the LLM model.
        """
        result = ""
        state = State.START
        while state != State.END:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )
            sorted_logits = sorted(
                range(len(logits)),
                key=lambda x: logits[x],
                reverse=True
            )

            for token in sorted_logits:
                word = self._model.decode(token)
                current_state = self._arg.func_verify(state, word)
                if current_state is None:
                    continue
                self.prompt += word
                state = current_state
                result += word
                break
        return result


    def combine_param(self, name_func: str) -> dict[str, Any]:
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
            if func_name != name_func:
                continue
            for param_key, param_type in param.items():
                self.prompt = prompt.format(
                    func_param_list=all_params,
                    param_key=param_key
                )
                self.choose_type_state(param_type.lower())
                param = self.generate_param()
                if param:
                    param_result[param_key] = "".join(param)
        return param_result

            #state = State.START
                #while state != State.END:
                #input_ids = self._model.encode(self.prompt)
                #logits = self._model.get_logits_from_input_ids(
                #   input_ids.tolist()[0]
                #)
                #sorted_logits = sorted(
                #   range(len(logits)),
                #    key=lambda x: logits[x#],
                #   reverse=True,
                #)
                #for token in sorted_logits:
                #   word = self._model.decode(token)
                #    self.choose_type_state(all_params[param])
            #   current_state = self._arg.func_verify(state, word)
                #   if current_state is None:
                #       continue
                #   self.prompt += token + ","
                #   state = current_state

