install:
	poetry config virtualenvs.in-project true
	poetry install

format:
	poetry run isort .
	poetry run black .

hash-password:
	@poetry run python scripts/hash_password.py

run: ## Run the FastAPI server in development mode
	poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

up:
	docker compose up --build