from typing import Any
from parsing_file import Parsing
from llm_sdk import Small_LLM_Model

#
# func_name = {
#     "fn_add_numbers": "Add two numbers together and return their sum",
#     "fn_greet": "Generate a greeting message for a person by name",
#     "fn_reverse_string": "Reverse a string and return the reversed result",
#     "fn_get_square_root": "Calculate square root of the number",
#     "fn_substitute_string_with_regex": "Replace all" 
#         "occurrences matching a regex pattern in a string"
# }
#

class GenerationFuncName:
    def __init__(self) -> None:
        self._model = Small_LLM_Model()
        self.prompt = ""
        self._parsed = Parsing()

    def get_func_name(self) -> None:
        func_name = []

        content = self._parsed.parsing_arguments()
        function_list = content[1]

        for function in function_list:
            func_name.append({
                "name": function.name,
                "description": function.description
            })
        return func_name

    def create_prompt(
        self,
        query: str,
        functions: dict[str, str]
    ) -> str:
        new = "".join(f" - {name}: {description}\n" for name, description in functions.items())
        return f"""Give the appropriate function name \
according to the user's query.

query: {query}

Functions:
{new}

name: """
    def get_name_value(self, request) -> dict[str, Any]:
        i = 0
        result = []

        func_name = self.get_func_name()

        self.prompt = self.create_prompt(
            query=request,
            functions=func_name
        )
        print(self.prompt)

        function_token = [
            self._model.encode(name).tolist()[0]
            for name in func_name
        ]

        while True:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )

            candidates = [
                name[i]
                for name in function_token
                if i < len(name) and name[:i] == result
            ]
            print(candidates)

            if not candidates:
                break

            score = float('-inf')
            token = 0

            for id in candidates:
                if logits[id] > score:
                    token = id
                    score = logits[id]

            result.append(token)
            word = self._model.decode(token)
            self.prompt += word
            i += 1

            # for function in function_token:
            #     if function == result:
            #         break

        return {"name": self._model.decode(result).strip()}


if __name__ == "__main__":
     gen = GenerationFuncName()
     print(gen.get_name_value("Hello world reverse"))
