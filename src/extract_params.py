from llm_sdk import Small_LLM_Model
from gen_func_name import GenerationFuncName


template = """
The task is to generate the arguments value
expected according to the type of function and 
the types of arguments.

query: "{query}"
The arguments type with its function:
{func_type}



"""

class GenerationArguments:
    def __init__(self) -> None:
        self._model = Small_LLM_Model()
        self.arguments = []
        self.prompt = None

    def gen_arg_value(self) -> None:
        

