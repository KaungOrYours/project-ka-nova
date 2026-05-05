#!/bin/bash

RUNPOD_HOST="203.57.40.176"
RUNPOD_PORT="10002"
RUNPOD_KEY="~/.ssh/id_ed25519"
RUNPOD_PATH="/workspace/ka-nova/results/"
LOCAL_PATH="~/Desktop/ka-nova/results_phase2/"
LOG_PATH="/workspace/ka-nova/output_phase2.log"

echo "=== Ka-Nova Result Sync ==="
echo "Downloading results from RunPod..."

# Download results
scp -P $RUNPOD_PORT -i $RUNPOD_KEY -r \
  root@$RUNPOD_HOST:$RUNPOD_PATH \
  $LOCAL_PATH

# Download logs too
scp -P $RUNPOD_PORT -i $RUNPOD_KEY \
  root@$RUNPOD_HOST:$LOG_PATH \
  ~/Desktop/ka-nova/output_phase2.log

echo "✓ Results downloaded to $LOCAL_PATH"

# Ask before deleting
read -p "Delete results from RunPod to save storage? (y/n): " confirm
if [ "$confirm" = "y" ]; then
  ssh -p $RUNPOD_PORT -i $RUNPOD_KEY root@$RUNPOD_HOST \
    "rm -rf /workspace/ka-nova/results/scenario_a/* /workspace/ka-nova/results/scenario_b/* /workspace/ka-nova/results/scenario_c/* /workspace/ka-nova/results/all_results.csv /workspace/ka-nova/results/summary_statistics.csv"
  echo "✓ RunPod results cleared"
else
  echo "RunPod results kept"
fi

echo "=== Done ==="
