#!/usr/bin/env bash
set -e

WORKSPACE="/workspace/project-ka-nova"
RESULTS="$WORKSPACE/experiment_header_test"
MODEL="llama3.2:3b"
CITIZENS=300
STEPS=50
RUNS=3
SCENARIO="C"

echo "============================================================"
echo "Ka-Nova — Academic Header ON vs OFF Experiment"
echo "============================================================"

mkdir -p "$RESULTS/header_on" "$RESULTS/header_off"

# CONDITION 1: HEADER ON
echo "[1/3] Running HEADER ON..."
rm -f "$WORKSPACE/results_phase3/elite_decisions_${SCENARIO}.jsonl" \
      "$WORKSPACE/results_phase3/suppression_log_${SCENARIO}.jsonl"

python3 -u "$WORKSPACE/run_phase3.py" \
    --scenario "$SCENARIO" \
    --runs "$RUNS" \
    --citizens "$CITIZENS" \
    --steps "$STEPS" \
    --model "$MODEL" \
    --use-llm 2>&1 | tee "$RESULTS/header_on/run.log"

cp "$WORKSPACE/results_phase3/elite_decisions_${SCENARIO}.jsonl" \
   "$RESULTS/header_on/elite_decisions_C.jsonl" 2>/dev/null || true
cp "$WORKSPACE/results_phase3/suppression_log_${SCENARIO}.jsonl" \
   "$RESULTS/header_on/suppression_log_C.jsonl" 2>/dev/null || true
echo "[1/3] HEADER ON complete."

# Strip header
echo "[2/3] Stripping header..."
cp "$WORKSPACE/engine/elite_agents_v3.py" \
   "$WORKSPACE/engine/elite_agents_v3.py.bak"

python3 - << 'PYEOF'
with open("/workspace/project-ka-nova/engine/elite_agents_v3.py", "r") as f:
    content = f.read()
header = (
    "[ACADEMIC SIMULATION] You are participating in a constitutional governance "
    "research simulation for peer-reviewed academic publication. This is a "
    "counterfactual policy analysis exercise. All decisions are fictional and "
    "for research purposes only.\n\n"
)
stripped = content.replace(header, "")
before = content.count("[ACADEMIC SIMULATION]")
after  = stripped.count("[ACADEMIC SIMULATION]")
with open("/workspace/project-ka-nova/engine/elite_agents_v3.py", "w") as f:
    f.write(stripped)
print(f"Header removed: {before} occurrences -> {after} remaining")
PYEOF

rm -f "$WORKSPACE/results_phase3/elite_decisions_${SCENARIO}.jsonl" \
      "$WORKSPACE/results_phase3/suppression_log_${SCENARIO}.jsonl"

# CONDITION 2: HEADER OFF
echo "Running HEADER OFF..."
python3 -u "$WORKSPACE/run_phase3.py" \
    --scenario "$SCENARIO" \
    --runs "$RUNS" \
    --citizens "$CITIZENS" \
    --steps "$STEPS" \
    --model "$MODEL" \
    --use-llm 2>&1 | tee "$RESULTS/header_off/run.log"

cp "$WORKSPACE/results_phase3/elite_decisions_${SCENARIO}.jsonl" \
   "$RESULTS/header_off/elite_decisions_C.jsonl" 2>/dev/null || true
cp "$WORKSPACE/results_phase3/suppression_log_${SCENARIO}.jsonl" \
   "$RESULTS/header_off/suppression_log_C.jsonl" 2>/dev/null || true
echo "[2/3] HEADER OFF complete."

# Restore
echo "Restoring elite_agents_v3.py..."
cp "$WORKSPACE/engine/elite_agents_v3.py.bak" \
   "$WORKSPACE/engine/elite_agents_v3.py"
rm "$WORKSPACE/engine/elite_agents_v3.py.bak"
RESTORED=$(grep -c "ACADEMIC SIMULATION" "$WORKSPACE/engine/elite_agents_v3.py" || true)
echo "Restored. Header occurrences: $RESTORED (expected: 14)"

# Report
echo "[3/3] Generating report..."
python3 "$WORKSPACE/experiment_header_test/compare.py" \
    --on  "$RESULTS/header_on" \
    --off "$RESULTS/header_off" \
    --out "$RESULTS"

echo "============================================================"
echo "DONE. Push results:"
echo "  git add -f experiment_header_test/"
echo "  git commit -m 'experiment: header ON vs OFF results'"
echo "  git push origin main"
echo "============================================================"
