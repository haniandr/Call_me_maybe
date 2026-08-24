from llm_sdk import Small_LLM_Model
from pathlib import Path
import json


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

first_arg = '{\n"name": '

model = Small_LLM_Model()

input_ids = model.encode(prompt)

logits = model.get_logits_from_input_ids(input_ids.tolist()[0])

real_logit = max(logits)

first_valid_tokens = model.encode(first_arg)

# for i in range():






def turn_into_inf(logits: list[int]) -> None:
    for i in range(len(logits)):
        if logits[i] < real_logit:
            logits[i] = float('-inf')

if __name__ == "__main__":
    print()
    print(len(logits))
    print(real_logit)