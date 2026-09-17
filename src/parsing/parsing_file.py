import argparse
from parsing_function import Parsing
from pathlib import Path


class Parser:
    def __init__(self) -> None:
        self._loader = Parsing()

    def parsing_file(self) -> None:
        parser = argparse.ArgumentParser()

        # c pour dire que --... est un arg optionnel et que la valeur apres l'est aussi
        parser.add_argument("--functions_definition", type=Path,
                            default=Path("data/input/functions_definition.json"))

        parser.add_argument("--input", type=Path,
                            default=Path("data/input/function_calling_tests.json"))

        parser.add_argument("--output", type=Path,
                            default=Path("data/output/function_calling_results.json"))

        # analyser les arguments donnes pour acceder a les valeurs
        args = parser.parse_args()

        for file_path in [args.functions_definition, args.input]:
            if not file_path.exists():
                raise argparse.ArgumentTypeError(
                    f"The file {file_path} doesn't exist..."
                )
            if file_path == args.input:
                raise parser.error(
                    "The input filename and the output "
                    "filename must be different"
                )

        func_def = self._loader.parse_file(args.functions_definition)
        input_test = self._loader.parse_file(args.input)
