.PHONY: init
init:
	@uv sync --dev

.PHONY: ci
ci:
	@uv run tox -m ci

.PHONY: check
check:
	@uv run tox -m checkm

.PHONY: dist
dist:
	uv run python setup.py sdist

.PHONY: clean
clean:
	@rm -rf build dist .pytest_cache .tox
	@find . -name "*.egg" -exec rm -rf {} +
	@find . -name "*.egg-info" -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -exec rm -rf {} +
