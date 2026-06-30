#!/bin/bash
# Ka-Nova Phase 3 — Pod Startup Script
# Runs on every pod boot — pulls latest code, starts Ollama, launches simulation

set -e

echo "============================================================"
echo "KA-NOVA PHASE 3 — POD STARTUP"
echo "============================================================"
echo "Start time: $(date)"
echo "Scenario:   ${SCENARIO:-NOT SET}"
echo "Runs:       ${RUNS:-100}"
echo "Citizens:   ${CITIZENS:-11000}"
echo "Steps:      ${STEPS:-50}"
echo "============================================================"

# ── 1. Pull latest codebase ───────────────────────────────────────────────────
echo ""
echo "[1/5] Pulling latest codebase from GitHub..."
if [ -d "/workspace/project-ka-nova" ]; then
    cd /workspace/project-ka-nova
    git pull https://${GITHUB_TOKEN}@github.com/KaungOrYours/project-ka-nova main
else
    git clone https://${GITHUB_TOKEN}@github.com/KaungOrYours/project-ka-nova /workspace/project-ka-nova
    cd /workspace/project-ka-nova
fi
echo "Codebase ready."

# ── 2. Write .env from pod environment variables ──────────────────────────────
echo ""
echo "[2/5] Writing .env..."
GRAFANA_PUBLIC_URL="https://${RUNPOD_POD_ID}-3000.proxy.runpod.net"
cat > /workspace/project-ka-nova/.env << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
WANDB_API_KEY=${WANDB_API_KEY}
GRAFANA_URL=${GRAFANA_PUBLIC_URL}
ELITE_LLM_MODEL=${LLM_MODEL:-llama3.2:3b}
RUNPOD_POD_ID=${RUNPOD_POD_ID}
EOF
echo ".env written."

# ── 3. Start Ollama and pull model ────────────────────────────────────────────
echo ""
echo "[3/5] Starting Ollama..."
ollama serve &
OLLAMA_PID=$!
sleep 5

echo "Pulling model: ${LLM_MODEL:-llama3.2:3b}..."
ollama pull ${LLM_MODEL:-llama3.2:3b}
echo "Ollama ready."

# ── 4. Start Prometheus metrics exporter ─────────────────────────────────────
echo ""
echo "[4/5] Starting Prometheus metrics exporter on :8000..."
cd /workspace/project-ka-nova
python3 monitor/metrics_exporter.py &
METRICS_PID=$!
echo "Metrics exporter PID: $METRICS_PID"
sleep 3

echo ""
echo "Starting Prometheus server on :9090..."
/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus \
    --web.listen-address=:9090 &
PROMETHEUS_PID=$!
echo "Prometheus PID: $PROMETHEUS_PID"
sleep 3

# ── 5. Start Grafana ─────────────────────────────────────────────────────────
echo ""
echo "Starting Grafana on :3000..."
cat >> /etc/grafana/grafana.ini << EOF

[paths]
provisioning = /etc/grafana/provisioning

[server]
domain = ${RUNPOD_POD_ID}-3000.proxy.runpod.net
root_url = https://%(domain)s/

[security]
allow_embedding = true
cookie_secure = true
cookie_samesite = none

[live]
max_connections = 0
EOF
/usr/share/grafana/bin/grafana server --config=/etc/grafana/grafana.ini --homepath=/usr/share/grafana &
sleep 5
echo "Grafana ready."

# ── Send Grafana URL + quick-start instructions via Telegram ──────────────────
GRAFANA_PUBLIC_URL="https://${RUNPOD_POD_ID}-3000.proxy.runpod.net"
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=1096527379 \
  -d text="Ka-Nova pod is up!

Grafana dashboard: ${GRAFANA_PUBLIC_URL}
Login: admin / admin

IMPORTANT: Send /start to this bot now to subscribe to alerts (START, MILESTONE, DONE, FINAL). Alerts will NOT fire automatically until you do this.

Monitor commands: /status /kpis /agents /reasoning /help" \
  -d parse_mode="Markdown" > /dev/null
echo "Grafana URL + instructions sent to Telegram."

# ── 6. Start Telegram bot ─────────────────────────────────────────────────────
echo ""
echo "Starting Telegram monitor bot..."
cd /workspace/project-ka-nova
python3 monitor/telegram_bot.py &
BOT_PID=$!
echo "Telegram bot PID: $BOT_PID"

# ── 6. Launch simulation ──────────────────────────────────────────────────────
echo ""
echo "[5/5] Launching Phase 3 simulation..."
wandb disabled
echo "Scenario: ${SCENARIO:-A}"

mkdir -p logs

python3 -u run_phase3.py \
    --scenario C \
    --runs ${RUNS:-100} \
    --citizens ${CITIZENS:-11000} \
    --steps ${STEPS:-50} \
    --model ${LLM_MODEL:-llama3.2:3b} \
    --use-llm >> logs/paper_C.log 2>&1
echo '=== SCENARIO C COMPLETE ===' >> logs/paper_C.log

python3 -u run_phase3.py \
    --scenario A \
    --runs ${RUNS:-100} \
    --citizens ${CITIZENS:-11000} \
    --steps ${STEPS:-50} \
    --model ${LLM_MODEL:-llama3.2:3b} \
    --use-llm >> logs/paper_A.log 2>&1
echo '=== SCENARIO A COMPLETE ===' >> logs/paper_A.log

echo ""
echo "============================================================"
echo "SIMULATION COMPLETE"
echo "End time: $(date)"
echo "============================================================"

# Keep container alive so results can be pulled
echo "Container staying alive. Pull results before terminating."
tail -f /dev/null
