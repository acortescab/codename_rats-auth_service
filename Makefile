# Variables
COMPOSE_FILE_DEV=docker-compose.dev.yml
COMPOSE_FILE_TEST=docker-compose.test.yml

MAIN_SERVICE=api

# Raise containers
test-up:
	docker compose -f $(COMPOSE_FILE_TEST) up --build

dev-up:
	docker compose -f $(COMPOSE_FILE_DEV) up --build

# Shutdown containers
test-down:
	docker compose -f $(COMPOSE_FILE_TEST) down -v

dev-down:
	docker compose -f $(COMPOSE_FILE_DEV) down -v

# test all files inside running container
test-exec:
	docker compose -f $(COMPOSE_FILE_TEST) exec $(MAIN_SERVICE) pytest -q

# Rebuild docker containers
test-rebuild:
	docker compose -f $(COMPOSE_FILE_TEST) down -v
	docker compose -f $(COMPOSE_FILE_TEST) up --build --force-recreate

dev-rebuild:
	docker compose -f $(COMPOSE_FILE_DEV) down -v
	docker compose -f $(COMPOSE_FILE_DEV) up --build --force-recreate

# Shell inside docker container
test-shell:
	docker compose -f $(COMPOSE_FILE_DEV) exec $(MAIN_SERVICE) /bin/sh

dev-shell:
	docker compose -f $(COMPOSE_FILE_TEST) exec $(MAIN_SERVICE) /bin/sh
