# Raise containers
dev-up:
	docker compose up --build --abort-on-container-exit

# Shutdown containers
dev-down:
	docker compose down -v

test-down:
	docker compose down -v

# Rebuild docker containers
dev-rebuild:
	docker compose down -v
	docker compose up --build --force-recreate

test-rebuild:
	docker compose down -v
	docker compose up --build --force-recreate

# Shell inside docker container
shell:
	docker compose exec api /bin/sh

shell-db:
	docker compose exec db psql -U user -d db

migrate:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

update-db:
	docker compose exec api alembic upgrade head
