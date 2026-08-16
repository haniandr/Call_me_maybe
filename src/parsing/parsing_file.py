def parse_file(name: str) -> list[str]:
    with open(name, "r") as f:
        content = file.read(name)
    