.PHONY: build up down test smoke logs

build:
	docker compose build orchestrator

up:
	docker compose up -d

down:
	docker compose down

test:
	PYTHONPATH=$$PWD python3 -m pytest -q

smoke:
	./scripts/lemnisiana_smoke.sh

logs:
	docker logs -f lemnisiana-orchestrator
