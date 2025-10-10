install: reqs-fe
	uv sync --dev

format:
	uv run isort .
	uv run black .

mypy:
	uv run mypy app/

lint:
	uv run pylint app/

hash-password:
	@uv run python scripts/hash_password.py

generate-secret:
	@uv run python scripts/generate_secret_key.py

run:
	SECRET_KEY="dummy_secret" \
	MASTER_PASSWORD_HASH="JDJiJDEyJHgvYVd6RkJyTU01QlZCQy9wMS9CNk9lLlpXU09YRDF1QVBPaTNDY09VWjl6bUhERlcuM3Nx" \
	ALLOWED_ORIGINS="*" \
	uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

up: build-frontend
	docker compose up --build

reqs-fe-ci:
	cd frontend && pnpm install

build-frontend-ci:
	cd frontend && pnpm build
	rm -rf app/assets/*
	rm -f app/templates/index.html
	cp -r frontend/dist/assets/* app/assets/
	cp frontend/dist/index.html app/templates/

reqs-fe:
	export NVM_DIR="$$HOME/.nvm" && \
	[ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh" && \
	cd frontend && \
	nvm use && \
	pnpm install

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