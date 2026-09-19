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
    find . -type d -name ".pytest_cache__" -exec rm -rf {} +

lint:
    uv run flake8 .
    uv run mypy . --warn-return-any \
        --warn-unused-ignores \
        --ignore-missing-imports \
        --disallow-untyped-defs \
        --check-untyped-defs

lint-strict:
    uv run flake8.
    uv run mypy . --strict
