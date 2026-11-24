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
echo "Job:        ${JOB:-run}"
echo "Use LLM:    ${USE_LLM:-true}"
echo "CVES L2:    ${CVES_L2_MODE:-enforce}"
echo "============================================================"

# JOB=run       (default) — the Monte Carlo campaign via run_phase3.py
# JOB=gsa                 — Sobol global sensitivity analysis via analysis/kpi.py --gsa
# JOB=benchmark            — the wall-clock-capped real-LLM-path throughput
#   benchmark (scripts/benchmark_llm_throughput.py). Run this BEFORE any real
#   scenario launch, not instead of one: it replaces the unmeasured
#   "35,000 calls / 24-30 hrs" assumption with a measured number before a
#   paid campaign is costed. Writes to its own throwaway results dir
#   (BENCH_RESULTS_DIR below), never to results_phase3/.
#
# USE_LLM=true (default) — unchanged published behaviour: Ollama + --use-llm.
# USE_LLM=false          — rule-based. Skips Ollama entirely (no serve, no
#   model pull) and drops --use-llm/--model. This matters commercially, not
#   just cosmetically: run_phase3.py forces workers=1 whenever use_llm is set,
#   so an LLM scenario is ~35,000 sequential calls and 24-30 hrs, whereas the
#   same scenario rule-based parallelises across cores and finishes in minutes
#   (measured: 23.2s per 11,000-citizen 50-year run, so 100 runs is ~39 min
#   single-process). Before this flag existed there was no way to run the cheap
#   path through the pipeline at all.
JOB="${JOB:-run}"
USE_LLM="${USE_LLM:-true}"
if [ "$JOB" != "run" ] && [ "$JOB" != "gsa" ] && [ "$JOB" != "benchmark" ]; then
    echo "FATAL: JOB must be 'run', 'gsa' or 'benchmark', got '${JOB}'" >&2
    exit 1
fi
if [ "$USE_LLM" != "true" ] && [ "$USE_LLM" != "false" ]; then
    echo "FATAL: USE_LLM must be 'true' or 'false', got '${USE_LLM}'" >&2
    exit 1
fi
# CVES_L2_MODE is read by engine/cves.py straight from the environment, so it
# never appeared anywhere in this script and was invisible in the pod log.
# That is a money problem, not a cosmetic one: the L2 ablation differs from the
# enforced run ONLY by this variable, so a missing or mistyped value silently
# defaults to "enforce" and buys a 16-hour duplicate of a run you already have.
# Echo it, validate it here, and export it so the value is unambiguous in the
# log before a single GPU-second is spent.
export CVES_L2_MODE="${CVES_L2_MODE:-enforce}"
case "$CVES_L2_MODE" in
    enforce|observe|off) ;;
    *) echo "FATAL: CVES_L2_MODE must be enforce/observe/off, got '${CVES_L2_MODE}'" >&2; exit 1 ;;
esac
# A GSA is rule-based by construction (run_sobol_gsa passes use_llm=False).
if [ "$JOB" = "gsa" ]; then USE_LLM="false"; fi
# A benchmark with no LLM measures nothing it exists to measure — force it on
# rather than silently producing an all-rule-based report that looks like a
# real LLM-throughput measurement.
if [ "$JOB" = "benchmark" ] && [ "$USE_LLM" = "false" ]; then
    echo "NOTE: JOB=benchmark forces USE_LLM=true (a rule-based benchmark measures nothing)."
    USE_LLM="true"
fi

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
if [ "$USE_LLM" = "true" ]; then
    echo "[3/5] Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5

    echo "Pulling model: ${LLM_MODEL:-llama3.2:3b}..."
    ollama pull ${LLM_MODEL:-llama3.2:3b}
    echo "Ollama ready."
else
    echo "[3/5] Skipping Ollama (USE_LLM=false) — no serve, no model pull."
fi

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
export WANDB_MODE=disabled
echo "Scenario: ${SCENARIO:-A}"

mkdir -p logs

IFS=',' read -ra SCENARIO_LIST <<< "${SCENARIO:-A}"

if [ "$JOB" = "benchmark" ]; then
    # Real-LLM-path throughput benchmark, run BEFORE costing/launching a real
    # scenario. Wall-clock-capped by BENCH_BUDGET_SECONDS (default 900 = 15
    # min), never by a fixed call count. Writes its own throwaway results
    # dir (BENCH_RESULTS_DIR), never results_phase3/. Scenario list reuses
    # $SCENARIO (default A,C — one civilian, one military chain, per the
    # design constraint); survival-year/runs-plan/hourly-rate assumptions
    # are documented defaults inside the script, overridable via
    # BENCH_SURVIVAL_YEARS / BENCH_RUNS_PLAN / BENCH_HOURLY_RATES (each a
    # JSON string / comma-list matching the script's own --survival-years /
    # --runs-plan / --hourly-rates flags) if you want to override them here
    # instead of editing the script.
    echo "Running LLM throughput benchmark: scenarios=${SCENARIO:-A,C} budget=${BENCH_BUDGET_SECONDS:-900}s"
    BENCH_ARGS=(
        --budget-seconds "${BENCH_BUDGET_SECONDS:-900}"
        --scenarios "${SCENARIO:-A,C}"
        --citizens "${CITIZENS:-11000}"
        --model "${LLM_MODEL:-llama3.2:3b}"
        --results-dir "${BENCH_RESULTS_DIR:-/workspace/project-ka-nova/results_benchmark}"
        --budget-dollars "${BENCH_BUDGET_DOLLARS:-80}"
    )
    [ -n "${BENCH_SURVIVAL_YEARS:-}" ] && BENCH_ARGS+=(--survival-years "${BENCH_SURVIVAL_YEARS}")
    [ -n "${BENCH_RUNS_PLAN:-}" ]      && BENCH_ARGS+=(--runs-plan "${BENCH_RUNS_PLAN}")
    [ -n "${BENCH_HOURLY_RATES:-}" ]   && BENCH_ARGS+=(--hourly-rates "${BENCH_HOURLY_RATES}")
    python3 -u scripts/benchmark_llm_throughput.py "${BENCH_ARGS[@]}" >> "logs/benchmark.log" 2>&1
    echo "=== BENCHMARK COMPLETE ===" >> "logs/benchmark.log"
    # Completion ping, same convention and same chat as the pod-boot message
    # above. Skipped silently when no bot token is configured, so a pod
    # without Telegram set up does not fire a malformed request.
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
        curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
          -d chat_id="${TELEGRAM_CHAT_ID:-1096527379}" \
          -d text="Ka-Nova LLM throughput benchmark complete. See logs/benchmark.log and ${BENCH_RESULTS_DIR:-/workspace/project-ka-nova/results_benchmark}/benchmark_summary.txt on the pod." \
          > /dev/null
    else
        echo "NOTE: TELEGRAM_BOT_TOKEN unset, skipping benchmark completion ping."
    fi
elif [ "$JOB" = "gsa" ]; then
    # Sobol GSA. One invocation per scenario in SCENARIO, so
    # SCENARIO=A,C GSA_KPI=trust_index runs both. Reviewer 1 pt.2 wants the
    # trust/coup effect sizes shown not to be artifacts of the feedback
    # constants, which means running this on a MILITARY chain for trust_index
    # (the fear-compliance floor only binds there), not only on A.
    for SCEN in "${SCENARIO_LIST[@]}"; do
        echo "Running Sobol GSA: scenario=${SCEN} kpi=${GSA_KPI:-corruption_index}"
        python3 -u analysis/kpi.py --gsa \
            --gsa-scenario "${SCEN}" \
            --gsa-kpi "${GSA_KPI:-corruption_index}" \
            --gsa-samples ${GSA_SAMPLES:-64} \
            --gsa-citizens ${CITIZENS:-1000} \
            --gsa-steps ${STEPS:-50} \
            >> "logs/gsa_${SCEN}_${GSA_KPI:-corruption_index}.log" 2>&1
        echo "=== GSA ${SCEN} COMPLETE ===" >> "logs/gsa_${SCEN}_${GSA_KPI:-corruption_index}.log"
    done
else
    # run_phase3.py now exits non-zero when a scenario produces zero
    # successful runs. This script runs under `set -e`, so without the
    # explicit `|| FAILED=...` below a single failing scenario would abort the
    # whole loop and silently skip every scenario after it. On a multi-scenario
    # campaign that is the difference between losing one result and losing
    # all of them, so per-scenario failure is caught, recorded, and the loop
    # continues; the run is then reported as failed at the end rather than
    # exiting 0 like it used to.
    FAILED_SCENARIOS=""
    for SCEN in "${SCENARIO_LIST[@]}"; do
        echo "Running scenario: ${SCEN} (use_llm=${USE_LLM}, l2=${CVES_L2_MODE})"
        if [ "$USE_LLM" = "true" ]; then
            python3 -u run_phase3.py \
                --scenario "${SCEN}" \
                --runs ${RUNS:-100} \
                --citizens ${CITIZENS:-11000} \
                --steps ${STEPS:-50} \
                --model ${LLM_MODEL:-llama3.2:3b} \
                --use-llm >> "logs/paper_${SCEN}.log" 2>&1 \
                || FAILED_SCENARIOS="${FAILED_SCENARIOS} ${SCEN}"
        else
            python3 -u run_phase3.py \
                --scenario "${SCEN}" \
                --runs ${RUNS:-100} \
                --citizens ${CITIZENS:-11000} \
                --steps ${STEPS:-50} >> "logs/paper_${SCEN}.log" 2>&1 \
                || FAILED_SCENARIOS="${FAILED_SCENARIOS} ${SCEN}"
        fi
        echo "=== SCENARIO ${SCEN} COMPLETE ===" >> "logs/paper_${SCEN}.log"
    done
    if [ -n "${FAILED_SCENARIOS}" ]; then
        echo ""
        echo "============================================================"
        echo "SCENARIOS THAT PRODUCED ZERO SUCCESSFUL RUNS:${FAILED_SCENARIOS}"
        echo "Check logs/paper_<scenario>.log before trusting any output."
        echo "============================================================"
        if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
            curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
              -d chat_id="${TELEGRAM_CHAT_ID:-1096527379}" \
              -d text="Ka-Nova WARNING: zero successful runs for scenario(s):${FAILED_SCENARIOS}. Do not trust the campaign output until checked." \
              > /dev/null
        fi
    fi
fi

echo ""
echo "============================================================"
echo "SIMULATION COMPLETE"
echo "End time: $(date)"
echo "============================================================"

# Keep container alive so results can be pulled
echo "Container staying alive. Pull results before terminating."
tail -f /dev/null
