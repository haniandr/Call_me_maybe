.PHONY: install run debug clean lint lint-strict


run:
    uv run python -m src

install:
    uv sync

debug:
    uv run python -m pdb -m src

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".mypy_cache__" -exec rm -rf {} +
