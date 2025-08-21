.PHONY: build up down test smoke logs

build:
\tdocker compose build orchestrator

up:
\tdocker compose up -d

down:
\tdocker compose down

test:
\tPYTHONPATH=$(PWD) python3 -m pytest -q

smoke:
\t./scripts/lemnisiana_smoke.sh

logs:
\tdocker logs -f lemnisiana-orchestrator
