#!/bin/bash
# =============================================================================
# PROJECT KA-NOVA
# scripts/retest_symmetric.sh
#
# The symmetric-prompt re-test: the gate that must pass before any paid
# campaign is launched.
#
# WHY THIS FILE EXISTS. RunPod's ssh.runpod.io proxy requires a PTY and
# ignores a remote command argument, so driving a run from a laptop means
# feeding an interactive bash session through stdin with sleep-based timing.
# That is fragile: quoting breaks, writes race the shell, and a mistyped
# heredoc silently produces no run at all. Twice on 2026-11-24 that cost a
# pod session. Committing the script to the repo means the pod pulls it with
# `git pull` at boot and the whole launch becomes one short command with no
# quoting:
#
#     bash scripts/retest_symmetric.sh
#
# WHAT IT TESTS. With Scenario A dropped, the paper needs at least one real
# constitution whose elite agents emit coup signals that CVES L2 can
# intercept. Until 2026-11-24 no real constitution had ever produced a
# cves_violations file, but two separate defects explain that and both are now
# fixed (daab19c, cd94e93). This run establishes, on real LLM output, which of
# Germany, South Korea, Chile and Pakistan actually emit.
#
# Small by design: 3 runs x 10 years x 300 citizens per scenario, about 40
# minutes and well under a dollar. It is a gate, not a result.
#
# Results go to KA_NOVA_RESULTS_DIR, never to the tracked results_phase3/
# audit trail. That directory was polluted twice by runs that forgot to set
# it, so it is set here rather than left to the caller.
# =============================================================================
set -u

cd "$(dirname "$0")/.." || exit 1

export WANDB_MODE=disabled                 # env var, never the `wandb` CLI
export CVES_L2_MODE="${CVES_L2_MODE:-enforce}"
export KA_NOVA_RESULTS_DIR="${KA_NOVA_RESULTS_DIR:-/workspace/retest_symmetric}"

RUNS="${RUNS:-3}"
CITIZENS="${CITIZENS:-300}"
STEPS="${STEPS:-10}"
SCENARIOS="${SCENARIOS:-DE SK CL PK}"
MODEL="${LLM_MODEL:-llama3.2:3b}"
LOGDIR="${LOGDIR:-/workspace}"

mkdir -p "$KA_NOVA_RESULTS_DIR" "$LOGDIR"
STATUS="$LOGDIR/retest_status.log"
: > "$STATUS"

echo "scenarios=$SCENARIOS runs=$RUNS citizens=$CITIZENS steps=$STEPS l2=$CVES_L2_MODE" | tee -a "$STATUS"
echo "results -> $KA_NOVA_RESULTS_DIR" | tee -a "$STATUS"

FAILED=""
for S in $SCENARIOS; do
    echo "START $S $(date -u +%H:%M:%S)" | tee -a "$STATUS"
    # No `set -e`: a scenario that produces zero successful runs now exits
    # non-zero (run_phase3.py), and under `set -e` that would abort the loop
    # and silently skip every scenario after it — losing all four results
    # instead of one. Record and continue.
    if python3 -u run_phase3.py \
            --scenario "$S" \
            --runs "$RUNS" \
            --citizens "$CITIZENS" \
            --steps "$STEPS" \
            --model "$MODEL" \
            --use-llm >> "$LOGDIR/retest_$S.log" 2>&1; then
        echo "DONE $S $(date -u +%H:%M:%S)" | tee -a "$STATUS"
    else
        FAILED="$FAILED $S"
        echo "FAILED $S $(date -u +%H:%M:%S)" | tee -a "$STATUS"
    fi
done

if [ -n "$FAILED" ]; then
    echo "SCENARIOS WITH ZERO SUCCESSFUL RUNS:$FAILED" | tee -a "$STATUS"
fi
echo "ALL_RETESTS_DONE" | tee -a "$STATUS"
