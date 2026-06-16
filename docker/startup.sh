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
cat > /workspace/project-ka-nova/.env << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
WANDB_API_KEY=${WANDB_API_KEY}
GRAFANA_URL=${GRAFANA_URL:-http://localhost:3000}
ELITE_LLM_MODEL=${LLM_MODEL:-llama3.2:3b}
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

# ── 5. Start Telegram bot ─────────────────────────────────────────────────────
echo ""
echo "Starting Telegram monitor bot..."
python3 monitor/telegram_bot.py &
BOT_PID=$!
echo "Telegram bot PID: $BOT_PID"

# ── 6. Launch simulation ──────────────────────────────────────────────────────
echo ""
echo "[5/5] Launching Phase 3 simulation..."
echo "Scenario: ${SCENARIO:-A}"

python3 run_phase3.py \
    --scenario ${SCENARIO:-A} \
    --runs ${RUNS:-100} \
    --citizens ${CITIZENS:-11000} \
    --steps ${STEPS:-50} \
    --model ${LLM_MODEL:-llama3.2:3b} \
    --use-llm

echo ""
echo "============================================================"
echo "SIMULATION COMPLETE"
echo "End time: $(date)"
echo "============================================================"

# Keep container alive so results can be pulled
echo "Container staying alive. Pull results before terminating."
tail -f /dev/null
