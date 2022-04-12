SHELL := /bin/bash

.env:
	python -m venv .env

install: .env
	source .env/bin/activate && python -m pip install -e .[dev]

pretty:
	. .env/bin/activate && \
	python -m black terrapy && \
	isort terrapy

.PHONY: tests
tests: install pytest isort_check black_check

pytest:
	. .env/bin/activate && \
	python -m pytest

pytest_loud:
	. .env/bin/activate && \
	python -m pytest -s

isort_check:
	. .env/bin/activate && \
	python -m isort terrapy --check-only

black_check:
	. .env/bin/activate && \
	python -m black terrapy --check
