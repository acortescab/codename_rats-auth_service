# Variables
COMPOSE_FILE_DEV=docker-compose.dev.yml
COMPOSE_FILE_TEST=docker-compose.test.yml

# Raise containers
test:
	docker compose -f $(COMPOSE_FILE_TEST) down -v
	docker compose -f $(COMPOSE_FILE_TEST) up --build --abort-on-container-exit test

dev-up:
	docker compose -f $(COMPOSE_FILE_DEV) up --build --abort-on-container-exit

test-up:
	docker compose -f $(COMPOSE_FILE_TEST) up --build --abort-on-container-exit

# Shutdown containers
dev-down:
	docker compose -f $(COMPOSE_FILE_DEV) down -v

test-down:
	docker compose -f $(COMPOSE_FILE_TEST) down -v

# Rebuild docker containers
dev-rebuild:
	docker compose -f $(COMPOSE_FILE_DEV) down -v
	docker compose -f $(COMPOSE_FILE_DEV) up --build --force-recreate

test-rebuild:
	docker compose -f $(COMPOSE_FILE_TEST) down -v
	docker compose -f $(COMPOSE_FILE_TEST) up --build --force-recreate

# Shell inside docker container
shell:
	docker compose -f $(COMPOSE_FILE_DEV) exec api /bin/sh

shell-db:
	docker compose -f $(COMPOSE_FILE_DEV) exec db psql -U user -d db

migrate:
	docker compose -f $(COMPOSE_FILE_DEV) exec api alembic revision --autogenerate -m "$(msg)"

update-db:
	docker compose -f $(COMPOSE_FILE_DEV) exec api alembic upgrade head
