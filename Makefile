fmt:
	poetry run black .
	poetry run isort .
lint:
	poetry run flake8p .
	poetry run mypy .
dev:
	poetry run uvicorn app.main:app --reload

# allow no tests
.PHONY: test
test:
	sh -c 'PYTHONPATH=. poetry run pytest . || ([ $$? = 5 ] && exit 0 || exit $$?)'
