#!/bin/bash
# Monitor the local 2-hour diagnostic run (GSA x2 + external-mode comparison).
# Progress is derived from each model's init line, since run_sobol_gsa prints
# no per-run counter: seed = row_idx*100 + ord(scenario), and total runs =
# n_sample*(k+2) = 64*15 = 960.
L="${KANOVA_LOGDIR:-/private/tmp/claude-501/-Users-kaunghtet-Desktop-ka-nova/4ff9268d-7d10-4598-b1c1-473371375b49/scratchpad}"
TOTAL=960

step_line() {
  local f="$1" label="$2"
  if [ ! -f "$f" ]; then printf "  %-26s not started\n" "$label"; return; fi
  local done pct eta start now elapsed
  done=$(grep -c "Phase 3 initialized" "$f" 2>/dev/null || echo 0)
  if grep -q "saved:" "$f" 2>/dev/null; then
    printf "  %-26s COMPLETE\n" "$label"; return
  fi
  pct=$(( done * 100 / TOTAL ))
  start=$(stat -f %B "$f" 2>/dev/null || echo 0)
  now=$(date +%s); elapsed=$(( now - start ))
  if [ "$done" -gt 3 ]; then
    eta=$(( (TOTAL - done) * elapsed / done / 60 ))
    printf "  %-26s %4d/%d  %3d%%  elapsed %dm  eta ~%dm\n" "$label" "$done" "$TOTAL" "$pct" $((elapsed/60)) "$eta"
  else
    printf "  %-26s %4d/%d  starting\n" "$label" "$done" "$TOTAL"
  fi
}

echo "=============================================="
echo " Ka-Nova local diagnostic run   $(date +%H:%M:%S)"
echo "=============================================="
sed -n '1,20p' "$L"/../tasks/*.output 2>/dev/null | grep -E "^\[" | tail -4
echo "----------------------------------------------"
step_line "$L/gsa_C_trust.log"       "1. GSA C / trust"
step_line "$L/gsa_A_corruption.log"  "2. GSA A / corruption"
echo "----------------------------------------------"
echo "  3. external-mode comparison"
for M in real controlled; do
  n=$(ls "$L"/mode_${M}_*.log 2>/dev/null | wc -l | tr -d ' ')
  printf "     %-11s %s/7 scenarios\n" "$M" "$n"
done
echo "=============================================="
echo "Results land in: results_phase3/sobol_sensitivity_<scen>_<kpi>.csv"
