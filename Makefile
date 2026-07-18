.PHONY: test install lint clean

install:
	pip install -e .

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -rf build dist *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
