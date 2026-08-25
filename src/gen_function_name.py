from llm_sdk import Small_LLM_Model
from pathlib import Path
import json
from math import inf

prompt = """
You are a function-calling assistant.
Your task is to translate natural langage into a structural JSON format containing the prompt, names 
of the functions and arguments as keys with their values.
Found the appropriate functions for the user's query and give its name and arguments in the output.

The available functions:
fn_add_numbers(a: float, b: float): add two numbers.
fn_greet(name: str): greets a person by name.
fn_reverse_string(s: str): reverse a string and return the new string reversed. 
fn_get_square_root(a: int): calculate the root of the given number.
fn_substitute_string(source_string: str, regex: str, replacement: str): Replace 
all occurrences matching a regex pattern in a string

Examples:
prompt: "What is the sum of 3 and 2?"
output: {
        "prompt": "What is the sum of 3 and 2?",
        "name": "fn_add_numbers",
        "arguments": {"a": 3.0, "b": 2.0}"
    }
"""

first_arg = '{"name": '

class Generation:
    def __init__(self) -> None:
        self._model = Small_LLM_Model()

    # c pour verifier la position a verifier du valid_tokens 
        self._valid_pos = 0

        self.gotten_token: list[str, str] = []

    def process_for_next_token(self) -> None:
        """
        Englobe tous les etapes pour la generation du next_token
        """
    # encode the prompt
        input_ids = self._model.encode(prompt)

    # encode the first key model
        first_tokens = self._model.encode(first_arg)

    # get the logits with proba of the next token
        _logits = self._model.get_logits_from_input_ids(input_ids.tolist()[0])
        checked_logits = self.check_valid_token(_logits, first_tokens)
        self.get_valid_token(_logits)

    def check_valid_token(self, logits, tokens) -> list[float]:
        """
        Check all the logits and put to -inf all those not valid.
        If the index are same as in the first_tokens, it's valid.
        """
        for i in range(len(logits)):
            if i not in tokens[self._valid_pos]:
                logits[i] = float('-inf')
        return logits


    def get_valid_token(self, logits) -> None:
        """
        Take and decode the token max got from the list of logits 
        """
        logit_max = max(logits)
        valid_token = self._model.decode(logit_max)
        if valid_token == self._first_tokens[self._valid_pos]:
            self._valid_pos += 1
            self.gotten_token.append(valid_token)

    # def generate_first_token

if __name__ == "__main__":
    gen = Generation()
    gen.process_for_next_token()
    print(gen.gotten_token)