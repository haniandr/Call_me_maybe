from llm_sdk import Small_LLM_Model
import sys

func_name = [
    "fn_add_numbers",
    "fn_greet",
    "fn_reverse_string",
    "fn_get_square_root",
    "fn_substitute_string_with_regex"
]

class GenerationFuncName:
    first_arg = '{"name": '

    prompt = """
You are a function-calling assistant. Your task is to translate the user's request into a 
structural JSON format with the names, the user's request, the arguments with their values.

The functions: {func_name}

request: "{query}"
output: {
        "name": "fn_add_numbers",
        "arguments": {"a": 3.0, "b": 2.0}"
Result:

"""

    def __init__(self) -> None:
        
        self._model = Small_LLM_Model()
        self._valid_pos = 0
        self.result = []

    def get_first_arg(self, request) -> None | list[..., ...]:
        prompt = self.prompt.format(func_name="".join(func_name), query=request)
        while True:
            input_ids = self._model.encode(self.prompt)
            first_key_token = self._model.encode(self.first_arg)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )
            for i in range(len(logits)):
                if i != first_key_token[self._valid_pos]:
                    logits[i] = float('-inf')
            argmax = max(logits)
            valid_token = self._model.decode(argmax)
            if valid_token == first_key_token[self._valid_pos]:
                self._valid_pos += 1
                self.result.append(valid_token)
            self.prompt += valid_token
            if self._valid_pos == len(first_key_token):
                break
        return self.result


gen = GenerationFuncName()
print(gen.get_first_arg())