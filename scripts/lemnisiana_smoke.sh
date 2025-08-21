#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE:-http://localhost:8000}

# Usa jq se existir, senão imprime bruto
if command -v jq >/dev/null 2>&1; then JQ="jq"; else JQ="cat"; fi

echo "1) Health & Guard-rails"
curl -sf "$BASE/health" | $JQ
curl -sf "$BASE/guard/check" | $JQ

echo "2) EDNAG propose (2 candidatos)"
curl -sf "$BASE/ednag/propose?n=2" | $JQ

echo "3) Evolve (força shadow)"
curl -sf -X POST "$BASE/evolve?force=true" | $JQ

echo "4) Caminho feliz do canário -> promoção automática para main"
curl -sf -X POST "$BASE/guard/force?reset=true" | $JQ
curl -sf "$BASE/mode?set=shadow" | $JQ
curl -sf -X POST "$BASE/deploy/canary?traffic=0.1&windows=2&window_seconds=3" | $JQ
sleep 7
curl -sf "$BASE/deploy/status" | $JQ

echo "5) Caminho de falha: força vdot>0 e verifica rollback para shadow"
curl -sf -X POST "$BASE/guard/force?vdot_v=0.05" | $JQ
curl -sf "$BASE/mode?set=shadow" | $JQ
curl -sf -X POST "$BASE/deploy/canary?traffic=0.1&windows=2&window_seconds=2" | $JQ
sleep 5
curl -sf "$BASE/deploy/status" | $JQ
curl -sf -X POST "$BASE/guard/force?reset=true" | $JQ

echo "6) Testes negativos (espera erros corretos)"
# 6.1 tentar ajustar traffic sem estar em canary -> 400
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/mode?traffic=0.5")
echo "HTTP ao ajustar traffic fora de canary: $HTTP (esperado 400)"

# 6.2 promoção concorrente -> 409
curl -sf "$BASE/mode?set=shadow" | $JQ
curl -sf -X POST "$BASE/deploy/canary?window_seconds=2&windows=2" | $JQ
HTTP2=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/deploy/canary?window_seconds=2&windows=2")
echo "HTTP ao iniciar canary com promoção em andamento: $HTTP2 (esperado 409)"
sleep 5
curl -sf "$BASE/deploy/status" | $JQ

echo "7) Últimos eventos"
curl -sf "$BASE/events?limit=15" | $JQ

echo "8) Métricas Prometheus (amostra)"
curl -sf "$BASE/metrics" | head -n 15
