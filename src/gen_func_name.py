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
        self.result = []

    def get_name_key(self, request) -> None | list[..., ...]:
        """
        Get the name key 
        """
        # combine the prompt and the function name needed 
        # inside with the user's query 
        self.prompt = template.format(func_name="".join(func_name), query=request)

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
            valid_token = self._model.decode(argmax)
            if argmax == first_key_token[self._valid_pos]:
                self._valid_pos += 1
                self.result.append(valid_token)
            self.prompt += valid_token
            if self._valid_pos == len(first_key_token):
                break
        self.result = "".join(self.result)
        return self.result


    # def get_name_value(self) -> None:
    #     index = 0
    #     func_tok_value = self._model.encode(func_name)
        
    #     if self.result:
    #         input_ids = self._model.encode(self.prompt)
    #         logits = self._model.get_logits_from_input_ids(
    #             input_ids()[0]
    #         )
            
    #         # sort the logits by their value but return the index
    #         sorted_logits = sorted(
    #                 range(len(logits)),
    #                 key=lambda x: logits[x],
    #                 reverse=True,
    #         )

            # name_supposed = ""            
            # for i in range(len(sorted_logits[:100])):
            #     max_token = self._model.decode(sorted_logits[i])
            #     for name in func_tok_value:
            #         if max_token in name:
            #             name_supposed += name
            #             index = len(max_token)
                    



if __name__ == "__main__":
    gen = GenerationFuncName()
    print(gen.get_name_key("What is the sum of 3 and 2?" ))