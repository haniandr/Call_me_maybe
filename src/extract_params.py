from llm_sdk import Small_LLM_Model


arg_key = '"parameters": '

template = """
The task is to generate the arguments value
expected according to the type of function and 
what that function expects as arguments.

query: "{query}"
The arguments prototype: {arg_type}

Function:
{func_name}: {description}
The arguments must follow the arg_type and the value extracted in
the query and based on func_name + the description

Gotten arguments:

"""

class GenerationArguments:
    def __init__(self) -> None:
        self.arguments = []
        self.prompt = None

    def gen_arg_key(self, arg, name, defin, query)-> None:
        """
        Generate the key of the part of the arguments.
        """
        self.prompt = template.format(
            arg_type=arg,
            func_name=name,
            description=defin,
            query=query
        )
        index = 0
        arg_token = self._model.encode(arg_key).tolist()[0]

        while True:
            input_ids = self._model.encode(self.prompt)
            logits = self._model.get_logits_from_input_ids(
                input_ids.tolist()[0]
            )
            for i in range(len(logits)):
                if i != arg_key[index]:
                    logits[i] = float('-inf')
            argmax = logits.index[max(logits)]
            if argmax == arg_token[index]:
                token = self._model.decode(argmax)
                self.arguments.append(token)
                index += 1
                self.prompt += token
            else:
                return None
            if index == len(arg_token):
                break
        return self.result


