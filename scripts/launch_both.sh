#!/bin/bash
# Ka-Nova — Run Scenario A then C sequentially

RUNS=${RUNS:-20}
CITIZENS=${CITIZENS:-300}
STEPS=${STEPS:-50}
MODEL=${MODEL:-llama3.2:1b}

echo "Starting Scenario A..."
bash scripts/launch.sh --scenario A --runs $RUNS --citizens $CITIZENS --steps $STEPS --model $MODEL

echo "Waiting for Scenario A to complete..."
while ps aux | grep -q "[r]un_phase3.py"; do
    sleep 30
done

echo "Scenario A complete. Starting Scenario C..."
bash scripts/launch.sh --scenario C --runs $RUNS --citizens $CITIZENS --steps $STEPS --model $MODEL

echo "Both scenarios launched."
