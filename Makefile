lint: typecheck
	isort --recursive . --check-only
	flake8
	black . --check

fmt:
	isort --recursive .
	autoflake --recursive --in-place --remove-all-unused-imports --remove-unused-variables .
	black .

test:
	pytest .

typecheck:
	mypy .
