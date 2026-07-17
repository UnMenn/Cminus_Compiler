.PHONY: run test clean

PROGRAM ?= examples/num.c-

run:
	python main.py $(PROGRAM)

test:
	python -m pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
