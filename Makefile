# Variables
COMPOSE_FILE_DEV=docker-compose.dev.yml
COMPOSE_FILE_TEST=docker-compose.test.yml

# Raise containers
test:
	docker compose -f $(COMPOSE_FILE_TEST) run --rm test
	docker compose -f $(COMPOSE_FILE_TEST) down -v

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
