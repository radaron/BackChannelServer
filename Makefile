install:
	poetry config virtualenvs.in-project true
	poetry install

format:
	poetry run isort .
	poetry run black .

mypy:
	poetry run mypy app/

lint:
	poetry run pylint app/

hash-password:
	@poetry run python scripts/hash_password.py

generate-secret:
	@poetry run python scripts/generate_secret_key.py

run: ## Run the FastAPI server in development mode
	poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

up: build-frontend
	docker compose up --build

build-frontend:
	export NVM_DIR="$$HOME/.nvm" && \
	[ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh" && \
	cd frontend && \
	nvm use && \
	pnpm build
	rm -rf app/assets/*
	rm -f app/templates/index.html
	cp -r frontend/dist/assets/* app/assets/
	cp frontend/dist/index.html app/templates/