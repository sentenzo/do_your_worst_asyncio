.PHONY: mypy ruff style style-check test lint all deps poetry-check

CODE=research

style:
	black $(CODE)
	isort $(CODE)

mypy:
	python -m mypy --enable-error-code ignore-without-code $(CODE)

ruff:
	python -m ruff check $(CODE)

poetry-check:
	poetry check

lint: poetry-check style-check ruff mypy

test:
	pytest -vsx -m "not slow"

test-all:
	pytest -vsx
