#!/bin/bash
# Ka-Nova — Automated Launch Script
# Usage: bash scripts/launch.sh --scenario A --runs 20 --citizens 300 --steps 50 --model llama3.2:1b

SCENARIO=${SCENARIO:-A}
RUNS=${RUNS:-20}
CITIZENS=${CITIZENS:-300}
STEPS=${STEPS:-50}
MODEL=${MODEL:-llama3.2:1b}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --scenario) SCENARIO="$2"; shift ;;
        --runs) RUNS="$2"; shift ;;
        --citizens) CITIZENS="$2"; shift ;;
        --steps) STEPS="$2"; shift ;;
        --model) MODEL="$2"; shift ;;
    esac
    shift
done

echo "============================================================"
echo "KA-NOVA LAUNCH SCRIPT"
echo "============================================================"
echo "Scenario:  $SCENARIO"
echo "Runs:      $RUNS"
echo "Citizens:  $CITIZENS"
echo "Steps:     $STEPS"
echo "Model:     $MODEL"
echo "============================================================"

echo "[1/5] Pulling latest codebase..."
git pull origin main

echo "[2/5] Cleaning up old processes..."
pkill -f run_phase3.py || true
pkill -f telegram_bot.py || true
pkill -f metrics_exporter.py || true
sleep 2

echo "[3/5] Setting up directories..."
mkdir -p logs

echo "[4/5] Starting monitoring stack..."
nohup python3 monitor/telegram_bot.py > logs/bot.log 2>&1 &
sleep 3
nohup python3 monitor/metrics_exporter.py > logs/metrics.log 2>&1 &
sleep 2

echo "[5/5] Launching simulation..."
nohup python3 -u run_phase3.py \
    --scenario $SCENARIO \
    --runs $RUNS \
    --citizens $CITIZENS \
    --steps $STEPS \
    --model $MODEL \
    --use-llm >> logs/simulation.log 2>&1 &

echo ""
echo "All processes started."
echo "Monitor: tail -f logs/simulation.log"
