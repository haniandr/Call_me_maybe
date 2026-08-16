def parse_file(name: str) -> list[str]:
    with open(name, "r") as f:
        content = file.readlines()
    return [line.split("\n") for line in content]


def parse_content_file(content: list[str]):
    
    