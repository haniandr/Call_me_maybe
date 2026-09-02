from llm_sdk import Small_LLM_Model


func_name = [
    "fn_add_numbers",
    "fn_greet",
    "fn_reverse_string",
    "fn_get_square_root",
    "fn_substitute_string_with_regex"
]

first_arg = '{"name": '

template = """
You are a function-calling assistant. Your task is to translate the user's request into a 
structural JSON format with the names, the user's request, the arguments with their values.

The functions: {func_name}

request: "{query}"
Result:

"""


class GenerationFuncName:
    def __init__(self) -> None:
        self._model = Small_LLM_Model()
        self._valid_pos = 0
        self.result: list[str] = []

    def get_name_key(self, request) -> None | list[str]:
        """
        Get the name key.
        """
        # combine the prompt and the function name needed
        # inside with the user's query
        self.prompt = template.format(
            func_name="".join(func_name),
            query=request
        )

        first_key_token = self._model.encode(first_arg).tolist()[0]

        while True:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )
            for i in range(len(logits)):
                if i != first_key_token[self._valid_pos]:
                    logits[i] = float('-inf')
            argmax = logits.index(max(logits))
            if argmax == first_key_token[self._valid_pos]:
                valid_token = self._model.decode(argmax)
                self._valid_pos += 1
                self.result.append(valid_token)
            self.prompt += valid_token
            if self._valid_pos == len(first_key_token):
                break
        # self.result = "".join(self.result)
        return self.result

    def get_name_value(self) -> None | list[str]:
        func_tok_value = [
            self._model.encode(f'"{candidate}"').tolist()[0]
            for candidate in func_name
        ]
        candidates = func_tok_value
        
        pos = 0

        while True:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )

            # sort the logits by their value but return the index
            sorted_logits = sorted(
                    range(len(logits)),
                    key=lambda x: logits[x],
                    reverse=True,
            )

            # token attendu pour chq tour dans les func_token
            expected_token = [
                tokens[pos]
                for tokens in candidates
                if pos < len(tokens)
            ]

            chosen = None

            for token in sorted_logits:
                if token in expected_token:
                    chosen = token
                    break

            if chosen is None:
                return None

            gotten_name = self._model.decode(chosen)
            self.result.append(gotten_name)
            self.prompt += gotten_name

            # sort the name_func to reduce the unuseful name
            new_func_name = [
                needed
                for needed in candidates
                if pos < len(needed) and needed[pos] == chosen
            ]
            candidates = new_func_name

            if len(candidates) == 1 and pos == len(candidates[0]) - 1:
                if candidates[0][pos] == chosen:
                    break

            pos += 1

        return "".join(self.result)


if __name__ == "__main__":
    gen = GenerationFuncName()
    print(gen.get_name_key("What is the sum of 3 and 2?"))
    print(gen.get_name_value())
