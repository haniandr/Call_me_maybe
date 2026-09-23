*This project has been created as part of the curriculum by haniandr.*

<div align=center>

# Call_me_maybe

</div>

## Description

Call_me_maybe is a Python project focused on using Large Language Model to transform natural language request into structured functions calls with JSON format.

As well as we know, AI is good at chatting and giving the right and appropriate answer for the user's request but here, the goal is to make the LLM to generate a function name and its corresponding parameters while preventing invalid outputs. Instead of allowing the LLM to generate its choices text, the project uses **constrained decoding** to restrict the possible tokens according to the expected output structure.

Request: 
```
What is the sum of 3 and 4?
```
Output:
```
{
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 2.0,
        "b": 3.0
    }
}
```


The project conbines several knowledges and phases:

-  Python language 
-  Small_LLM_Model
-  POO
-  Logits and tokens for constrained decoding
-  Finite State Machine(FSM)
-  Pydantic for validation
-  JSON
-  Argparse module for the command-line arguments parsing


## Instructions