
.PHONY: build up down test smoke logs ready

build:
	docker compose build orchestrator

up:
	docker compose up -d

down:
	docker compose down

ready:
	./scripts/wait-http.sh http://localhost:8000/health 60 0.25

test:
	docker compose up -d orchestrator
	./scripts/wait-http.sh http://localhost:8000/health 60 0.25
	PYTHONPATH=$PWD python3 -m pytest -q

smoke:
	./scripts/wait-http.sh http://localhost:8000/health 60 0.25
	./scripts/lemnisiana_smoke.sh

logs:
	docker logs -f lemnisiana-orchestrator
