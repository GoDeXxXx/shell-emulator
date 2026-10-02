.PHONY: run test

run:
	python3 src/main.py

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
