"""
================================================================================
PROJECT KA-NOVA
scripts/benchmark_llm_throughput.py

Pod-only, wall-clock-capped benchmark of the REAL elite-agent LLM path
(engine/elite_agents_v3.py + engine/cves.py via model_phase3.py), run before
any full scenario launch, to replace the unmeasured "35,000 calls / 24-30 hrs"
assumption with a measured number before a paid RunPod campaign is costed.

What this measures (see module docstrings below for detail):
    1. Mean / p95 seconds per real LLM call, plus observed prompt/completion
       token counts (falls back to a documented word-count proxy if the
       Ollama server does not return usage metadata).
    2. Mean seconds per simulated year (7 elite agents + CVES L1-L4
       overhead + the Mesa citizen layer) and per full run.
    3. CVES reprompt rate — L1 structural reprompts and L2 constitutional-
       violation reprompts, read from the real cves_scores_<scenario>.jsonl
       / cves_violations_<scenario>.jsonl files this run produces.
    4. An extrapolated cost table for the planned 7-scenario campaign, built
       from the MEASURED per-year rate, not the original 24-30hr assumption.
    5. A verdict line: does the planned campaign fit a stated budget.

    Also settles Opening 5 / Exposure 5 (the seeding question): runs one
    run_id twice and diffs the resulting elite_decisions_<scenario>.jsonl
    to report determinism as a hard yes/no.

HOW TO RUN ON A FRESH POD (system Python, no venv — RunPod has none):
    cd /workspace/project-ka-nova
    export KA_NOVA_RESULTS_DIR=/workspace/project-ka-nova/results_benchmark
    python3 scripts/benchmark_llm_throughput.py --budget-seconds 900

    (The script also sets KA_NOVA_RESULTS_DIR itself if you don't; the env
    var above is shown because it is the one override you may want to point
    somewhere with more disk if /workspace is small.)

    Ollama must already be serving the target model on this pod, e.g.:
        apt-get update && apt-get install -y zstd
        ollama serve &
        OLLAMA_KEEP_ALIVE=-1 ollama pull llama3.2:3b

NEVER RUN WITH A REAL LLM ON THE MAC — no Ollama, insufficient RAM. Use
`--dry-run` on the Mac instead, which never touches Ollama/LangChain network
calls and only exercises argument handling, the registry wiring, a tiny
rule-based (use_llm=False) model step, and the statistics/report code with
synthetic fixture data.

Writes results to <results-dir>/benchmark_report.json and
<results-dir>/benchmark_summary.txt (also printed to stdout), so the output
survives an SSH disconnect. Never writes into results_phase3/.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

# Documented placeholder survival/collapse years for the 5 not-yet-benchmarked
# scenarios. These are NOT measured by this script (it only runs two
# scenarios live, per the design constraint). They are the best numbers on
# record in .claude/memory.md as of 2026-10-29:
#   - A: locked at 50 (full survival, published pair).
#   - C: locked at ~15-16 (published collapse year, matches the 12.68-year
#     real Myanmar anchor reasonably well).
#   - TH/PK: currently collapse near year 15-16 in rule-based testing because
#     their encoded COUP_TRIGGER_* fields are still both 0.0, identical to
#     Myanmar's (open research question, .claude/memory.md bug list, "should
#     failure-year diverge by country"). Using 16 here is a PLACEHOLDER tied
#     to that still-open bug, not a prediction — it will very likely change
#     once/if that question is resolved, and the free rule-based survey
#     mentioned in the task is the thing that should actually set it.
#   - SK/CL/DE: civilian-chain, assumed to survive the full 50 years (no
#     coup-risk floor pinning them to an early collapse the way the military
#     chains are) — again a PLACEHOLDER, not a real-world-anchored number.
DEFAULT_SURVIVAL_YEARS = {
    "A":  50,
    "C":  16,
    "SK": 50,
    "TH": 16,
    "PK": 16,
    "CL": 50,
    "DE": 50,
}

DEFAULT_RUNS_PLAN = {
    "A": 100, "C": 100,
    "SK": 50, "TH": 50, "PK": 50, "CL": 50, "DE": 50,
}

DEFAULT_HOURLY_RATES = {"RTX_A6000": 0.59, "RTX_5090": 1.19}


def parse_hourly_rates(raw: str) -> dict:
    out = {}
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        name, _, val = part.partition("=")
        out[name.strip()] = float(val.strip())
    return out


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Ka-Nova real-LLM-path throughput benchmark (pod-only).",
    )
    p.add_argument("--budget-seconds", type=float, default=900.0,
                    help="Hard wall-clock cap for the whole benchmark (default 900 = 15 min).")
    p.add_argument("--determinism-budget-seconds", type=float, default=150.0,
                    help="Slice of the total budget reserved for the seeding/determinism check.")
    p.add_argument("--scenarios", type=str, default="A,C",
                    help="Comma-separated scenario codes to actually run live. Must include "
                         "at least one civilian-chain and one military-chain code (default A,C).")
    p.add_argument("--citizens", type=int, default=11000,
                    help="Citizen count for the live benchmark runs (default matches production "
                         "scale, 11000, so Mesa/CVES overhead is realistic, not a toy number).")
    p.add_argument("--model", type=str, default=None,
                    help="Override ELITE_LLM_MODEL (default: env var or llama3.2:3b).")
    p.add_argument("--base-url", type=str, default=None,
                    help="Override ELITE_LLM_BASE_URL (default: env var or http://localhost:11434/v1).")
    p.add_argument("--temp", type=float, default=None,
                    help="Override ELITE_LLM_TEMP (default: env var or 0.4).")
    p.add_argument("--results-dir", type=str, default=None,
                    help="Throwaway results directory. Default: ./results_benchmark_<timestamp> "
                         "under the current directory. MUST NOT be results_phase3.")
    p.add_argument("--seed", type=int, default=0,
                    help="Base run_id/seed used for both the main benchmark and the determinism check.")
    p.add_argument("--runs-plan", type=str, default=None,
                    help='JSON dict overriding DEFAULT_RUNS_PLAN, e.g. \'{"A":100,"C":100}\'.')
    p.add_argument("--survival-years", type=str, default=None,
                    help='JSON dict overriding DEFAULT_SURVIVAL_YEARS (the dominant cost term — '
                         'see the module docstring; these are documented placeholders).')
    p.add_argument("--hourly-rates", type=str, default="RTX_A6000=0.59,RTX_5090=1.19",
                    help="Comma-separated name=dollars-per-hour pairs for the cost table.")
    p.add_argument("--budget-dollars", type=float, default=80.0,
                    help="Ceiling the verdict line checks the extrapolated cost against.")
    p.add_argument("--dry-run", action="store_true",
                    help="Mac-safe self-check: never touches Ollama/LangChain network calls. "
                         "Validates CLI handling, scenario-registry wiring, a tiny rule-based "
                         "model step, and the stats/report code against synthetic fixtures.")
    return p.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────
# Environment setup — MUST happen before any ka-nova module import, because
# model_phase3 / engine.elite_agents_v3 / engine.cves / run_phase3 all read
# KA_NOVA_RESULTS_DIR as a module-level `Path(os.getenv(...))` at import
# time, not lazily. Setting it after import is a silent no-op.
# ──────────────────────────────────────────────────────────────────────────

def resolve_results_dir(args) -> Path:
    if args.results_dir:
        d = Path(args.results_dir).resolve()
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        d = (Path.cwd() / f"results_benchmark_{ts}").resolve()
    # Hard safety check (non-negotiable per project rules): this directory
    # must never be, or live inside, the tracked results_phase3 audit trail.
    if "results_phase3" in d.parts:
        raise SystemExit(
            f"FATAL: --results-dir resolves to {d}, which is inside the "
            f"tracked results_phase3/ audit trail. Refusing to risk "
            f"contaminating elite_decisions_A.jsonl/_C.jsonl."
        )
    return d


def set_env_before_import(args, results_dir: Path) -> None:
    os.environ["KA_NOVA_RESULTS_DIR"] = str(results_dir)
    # Hard rule: WANDB_MODE as an env var, never the `wandb disabled` CLI
    # form (fails under subprocess inheritance on RunPod). This script does
    # not itself call wandb, but sets this defensively/consistently with
    # every other pod-side entry point in case that ever changes.
    os.environ["WANDB_MODE"] = "disabled"
    if args.model:
        os.environ["ELITE_LLM_MODEL"] = args.model
    if args.base_url:
        os.environ["ELITE_LLM_BASE_URL"] = args.base_url
    if args.temp is not None:
        os.environ["ELITE_LLM_TEMP"] = str(args.temp)


# ──────────────────────────────────────────────────────────────────────────
# Hardware / software provenance probe
# ──────────────────────────────────────────────────────────────────────────

def _run(cmd, timeout=10):
    try:
        out = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return out.stdout.strip() if out.returncode == 0 else f"(exit {out.returncode}) {out.stderr.strip()}"
    except Exception as e:
        return f"(unavailable: {e})"


def hardware_probe(model_name: str) -> dict:
    gpu_raw = _run(
        "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"
    )
    ollama_version = _run("ollama --version")
    ollama_list = _run("ollama list")
    model_digest = "unknown"
    for line in ollama_list.splitlines():
        if line.strip().lower().startswith(model_name.split(":")[0].lower()):
            parts = line.split()
            if len(parts) >= 2:
                model_digest = parts[1]
            break
    return {
        "gpu_raw_nvidia_smi": gpu_raw,
        "ollama_version": ollama_version,
        "ollama_list_raw": ollama_list,
        "resolved_model_digest": model_digest,
        "probed_at": datetime.now().isoformat(),
    }


# ──────────────────────────────────────────────────────────────────────────
# LLM-call instrumentation — monkeypatches EliteAgentLayerV3._invoke_llm at
# the class level so every real call made by the REAL pipeline (the 7-agent
# chain in elite_agents_v3.step(), plus any L1/L2 reprompt calls issued by
# cves.py's l1_parse/l2_constitutional) is timed and token-counted, without
# editing engine/elite_agents_v3.py or engine/cves.py on disk (both are
# outside this task's file ownership — see the task brief).
# ──────────────────────────────────────────────────────────────────────────

CALL_LOG: list[dict] = []
CURRENT_CONTEXT = {"scenario": None, "year": None}


def install_llm_instrumentation(elite_agents_v3_module):
    """
    Returns a context manager-like pair (install, uninstall). The
    instrumented version calls self._llm.invoke(...) directly (bypassing the
    ChatPromptTemplate | StrOutputParser chain used in production) so the
    raw AIMessage — and its usage_metadata, if the Ollama server returns
    one — is visible before the StrOutputParser strips it away. The STRING
    content returned is identical to what the original chain would have
    produced (same system/human messages, same model, same client), so CVES
    L1/L2/L3/L4 behave exactly as in a real run. On any failure the original
    chain-based path is used as a fallback so the benchmark can never break
    the pipeline it is trying to measure.
    """
    EliteAgentLayerV3 = elite_agents_v3_module.EliteAgentLayerV3
    original_invoke = EliteAgentLayerV3._invoke_llm

    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        _HAVE_MESSAGES = True
    except ImportError:
        _HAVE_MESSAGES = False

    def instrumented(self, system_prompt, user_message):
        t0 = time.perf_counter()
        prompt_tokens = None
        completion_tokens = None
        used_fallback_path = False
        content = None
        try:
            if not _HAVE_MESSAGES:
                raise RuntimeError("langchain_core.messages unavailable")
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
            ai_msg = self._llm.invoke(messages)
            content = ai_msg.content
            usage = getattr(ai_msg, "usage_metadata", None)
            if usage:
                prompt_tokens = usage.get("input_tokens")
                completion_tokens = usage.get("output_tokens")
            else:
                token_usage = (getattr(ai_msg, "response_metadata", None) or {}).get("token_usage")
                if token_usage:
                    prompt_tokens = token_usage.get("prompt_tokens")
                    completion_tokens = token_usage.get("completion_tokens")
        except Exception:
            used_fallback_path = True
            content = original_invoke(self, system_prompt, user_message)
        latency_s = time.perf_counter() - t0
        CALL_LOG.append({
            "scenario": CURRENT_CONTEXT["scenario"],
            "year": CURRENT_CONTEXT["year"],
            "latency_s": latency_s,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "completion_words": len((content or "").split()),
            "had_real_usage": prompt_tokens is not None and completion_tokens is not None,
            "used_fallback_path": used_fallback_path,
        })
        return content

    def install():
        EliteAgentLayerV3._invoke_llm = instrumented

    def uninstall():
        EliteAgentLayerV3._invoke_llm = original_invoke

    return install, uninstall


# ──────────────────────────────────────────────────────────────────────────
# Live scenario benchmark (pod-only path)
# ──────────────────────────────────────────────────────────────────────────

def run_scenario_benchmark(KaNovaModelPhase3, scenario, seed, n_citizens, use_llm, deadline):
    """
    Steps one model, one simulated year at a time, until either the model
    itself reports simulation_failed or the wall-clock deadline is hit.
    Caps by wall-clock, never by a fixed run/step count, per the hard
    15-minute budget constraint.
    """
    model = KaNovaModelPhase3(scenario=scenario, seed=seed, n_citizens=n_citizens, use_llm=use_llm)
    model.shared_data["run_id"] = seed
    year_times = []
    CURRENT_CONTEXT["scenario"] = scenario
    failed = False
    while time.time() < deadline:
        CURRENT_CONTEXT["year"] = model.current_year
        t0 = time.perf_counter()
        model.step()
        year_times.append(time.perf_counter() - t0)
        if model.shared_data.get("simulation_failed", False):
            failed = True
            break
    return {
        "scenario": scenario,
        "chain_type": model.chain_type,
        "constitution_name": model.constitution_name,
        "years_completed": len(year_times),
        "final_year": model.current_year,
        "simulation_failed": failed,
        "year_times_s": year_times,
        "mean_seconds_per_year": statistics.fmean(year_times) if year_times else None,
    }


def read_cves_reprompt_stats(results_dir: Path, scenario: str) -> dict:
    """
    Reads this run's own real cves_scores_<scenario>.jsonl (L1) and
    cves_violations_<scenario>.jsonl (L2) — written by the unmodified,
    real engine/cves.py — to compute the reprompt rate. Memory records a
    0-reprompt rate across 35,000 published calls; this is the first check
    of that figure against live hardware/model behaviour, and the first
    real-LLM check on bug #19's prompt fixes for the five new constitutions.

    L1: engine/cves.py writes exactly one score row per decision, with an
    "attempt" field (0, 1 or 2). attempt > 0 means at least one L1
    structural reprompt happened before that decision resolved.

    L2: engine/cves.py writes one violation row per violated field. Each
    violation triggers at most one L2 reprompt call (not one per violated
    field), so this is reported as a violation RATE per decision, clearly
    labelled as a proxy for L2 reprompt volume, not an exact reprompt count.
    """
    scores_path = results_dir / f"cves_scores_{scenario}.jsonl"
    violations_path = results_dir / f"cves_violations_{scenario}.jsonl"

    l1_attempts = []
    l1_decisions = 0
    if scores_path.exists():
        with open(scores_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("layer") == "L1":
                    l1_decisions += 1
                    l1_attempts.append(int(row.get("attempt", 0)))

    l1_reprompt_rate = (
        sum(1 for a in l1_attempts if a > 0) / l1_decisions if l1_decisions else None
    )

    l2_violation_count = 0
    if violations_path.exists():
        with open(violations_path) as f:
            for line in f:
                if line.strip():
                    l2_violation_count += 1

    return {
        "l1_decisions_logged": l1_decisions,
        "l1_reprompt_rate": l1_reprompt_rate,
        "l1_attempt_histogram": {
            str(a): l1_attempts.count(a) for a in sorted(set(l1_attempts))
        } if l1_attempts else {},
        "l2_violation_rows": l2_violation_count,
        # Denominator uses L1-logged decisions (one L1 row per decision);
        # if L1 never ran (e.g. rule-based fallback mid-benchmark) this is None.
        "l2_violation_rate_per_decision": (
            l2_violation_count / l1_decisions if l1_decisions else None
        ),
    }


def run_determinism_check(KaNovaModelPhase3, results_dir, scenario,
                           seed, n_citizens, use_llm, deadline, estimated_year_seconds=None):
    """
    Opening 5 / Exposure 5: runs ONE run_id/seed TWICE for a single
    simulated year and diffs the resulting elite_decisions_<scenario>.jsonl
    content (excluding wall-clock-only fields: timestamp, time_ms). Reports
    determinism as a hard yes/no, per the task brief, rather than leaving
    the manuscript's "All runs are seeded" claim unverified.

    `estimated_year_seconds`, if available from the earlier live-scenario
    phase for this same scenario, is used as a safety margin: a step is
    never STARTED unless there is at least 1.5x that much time left before
    `deadline`, since a model.step() call cannot be interrupted mid-way once
    started. Without an estimate, a conservative fixed 90s margin is used.
    This keeps the whole script's wall-clock cap honoured even though this
    phase runs after the main per-scenario budget has already been spent.
    """
    decisions_path = results_dir / f"elite_decisions_{scenario}.jsonl"
    margin = 1.5 * estimated_year_seconds if estimated_year_seconds else 90.0

    def _reset():
        if decisions_path.exists():
            decisions_path.unlink()

    def _read_rows():
        rows = []
        if decisions_path.exists():
            with open(decisions_path) as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
        return rows

    def _strip(row):
        return {k: v for k, v in row.items() if k not in ("timestamp", "time_ms")}

    if time.time() + margin >= deadline:
        return {
            "attempted": False,
            "reason": f"insufficient remaining budget before determinism check "
                      f"(need >= {margin:.0f}s margin per step)",
        }

    _reset()
    CURRENT_CONTEXT["scenario"] = scenario
    model1 = KaNovaModelPhase3(scenario=scenario, seed=seed, n_citizens=n_citizens, use_llm=use_llm)
    model1.shared_data["run_id"] = seed
    CURRENT_CONTEXT["year"] = model1.current_year
    model1.step()
    run1_rows = [_strip(r) for r in _read_rows()]

    if time.time() + margin >= deadline:
        return {
            "attempted": True, "completed": False,
            "reason": "deadline (plus safety margin) hit after run 1, before run 2 could start",
        }

    _reset()
    model2 = KaNovaModelPhase3(scenario=scenario, seed=seed, n_citizens=n_citizens, use_llm=use_llm)
    model2.shared_data["run_id"] = seed
    CURRENT_CONTEXT["year"] = model2.current_year
    model2.step()
    run2_rows = [_strip(r) for r in _read_rows()]

    deterministic = run1_rows == run2_rows
    mismatches = []
    if not deterministic:
        if len(run1_rows) != len(run2_rows):
            mismatches.append(
                f"row count differs: run1={len(run1_rows)} run2={len(run2_rows)}"
            )
        for i, (a, b) in enumerate(zip(run1_rows, run2_rows)):
            if a != b:
                mismatches.append(f"row {i} ({a.get('agent', '?')}): {a} != {b}")

    return {
        "attempted": True,
        "completed": True,
        "scenario": scenario,
        "seed": seed,
        "deterministic": deterministic,
        "run1_row_count": len(run1_rows),
        "run2_row_count": len(run2_rows),
        "mismatches": mismatches[:10],
        "mismatch_count": len(mismatches),
    }


# ──────────────────────────────────────────────────────────────────────────
# Aggregation
# ──────────────────────────────────────────────────────────────────────────

def _percentile(values, pct):
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def aggregate_call_stats(call_log: list[dict]) -> dict:
    by_scenario = {}
    for row in call_log:
        by_scenario.setdefault(row["scenario"], []).append(row)

    def _summarize(rows):
        lat = [r["latency_s"] for r in rows]
        real_usage_rows = [r for r in rows if r["had_real_usage"]]
        prompt_tok = [r["prompt_tokens"] for r in real_usage_rows]
        completion_tok = [r["completion_tokens"] for r in real_usage_rows]
        completion_words = [r["completion_words"] for r in rows]
        return {
            "n_calls": len(rows),
            "mean_latency_s": statistics.fmean(lat) if lat else None,
            "p95_latency_s": _percentile(lat, 95),
            "min_latency_s": min(lat) if lat else None,
            "max_latency_s": max(lat) if lat else None,
            "n_calls_with_real_token_usage": len(real_usage_rows),
            "fraction_with_real_token_usage": (
                len(real_usage_rows) / len(rows) if rows else None
            ),
            "mean_prompt_tokens": statistics.fmean(prompt_tok) if prompt_tok else None,
            "mean_completion_tokens": statistics.fmean(completion_tok) if completion_tok else None,
            "p95_completion_tokens": _percentile(completion_tok, 95) if completion_tok else None,
            # Fallback proxy, ALWAYS computed, clearly separate from the real
            # figures above — used only if the Ollama server never returned
            # usage metadata for any call in this run.
            "mean_completion_words_proxy": (
                statistics.fmean(completion_words) if completion_words else None
            ),
            "n_calls_used_fallback_chain_path": sum(1 for r in rows if r["used_fallback_path"]),
        }

    out = {"overall": _summarize(call_log)}
    for scen, rows in by_scenario.items():
        out[scen] = _summarize(rows)
    return out


def build_cost_table(scenario_year_seconds: dict, runs_plan: dict, survival_years: dict,
                      hourly_rates: dict) -> dict:
    """
    scenario_year_seconds: {chain_type: measured mean seconds/year}, i.e.
    exactly two entries if the benchmark ran A and C ("civilian"/"military").
    For scenarios not actually benchmarked (SK/TH/PK/CL/DE), this uses the
    MEASURED rate of the same chain_type as the best available proxy —
    documented explicitly as an assumption, since prompt length/CVES
    ethnic-schema size differs per constitution and could move the real
    number once that scenario is benchmarked directly.
    """
    rows = []
    for code, runs in runs_plan.items():
        years = survival_years.get(code)
        if years is None:
            continue
        chain_type = "civilian" if code in ("A", "SK", "CL", "DE") else "military"
        sec_per_year = scenario_year_seconds.get(chain_type)
        proxied = code not in scenario_year_seconds.get("_measured_codes", [])
        total_years = runs * years
        total_seconds = (total_years * sec_per_year) if sec_per_year is not None else None
        row = {
            "scenario": code,
            "chain_type": chain_type,
            "runs": runs,
            "years_per_run": years,
            "total_simulated_years": total_years,
            "seconds_per_year_used": sec_per_year,
            "rate_is_proxied_from_other_scenario": proxied,
            "total_hours": (total_seconds / 3600.0) if total_seconds is not None else None,
            "cost_by_rate": (
                {name: round(total_seconds / 3600.0 * rate, 2) for name, rate in hourly_rates.items()}
                if total_seconds is not None else None
            ),
        }
        rows.append(row)

    total_hours = sum(r["total_hours"] for r in rows if r["total_hours"] is not None)
    total_cost_by_rate = {
        name: round(sum(r["cost_by_rate"][name] for r in rows if r["cost_by_rate"]), 2)
        for name in hourly_rates
    }
    return {"rows": rows, "total_hours": round(total_hours, 2), "total_cost_by_rate": total_cost_by_rate}


# ──────────────────────────────────────────────────────────────────────────
# Report writing
# ──────────────────────────────────────────────────────────────────────────

def write_outputs(results_dir: Path, report: dict) -> tuple[Path, Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / "benchmark_report.json"
    txt_path = results_dir / "benchmark_summary.txt"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    with open(txt_path, "w") as f:
        f.write(render_summary(report))
    return json_path, txt_path


def render_summary(report: dict) -> str:
    lines = []
    a = lines.append
    a("=" * 72)
    a("KA-NOVA LLM THROUGHPUT BENCHMARK")
    a("=" * 72)
    a(f"Run at:            {report.get('run_started_at')}")
    a(f"Budget (s):        {report.get('budget_seconds')}")
    a(f"Wall-clock used:   {report.get('wall_clock_used_s'):.1f}s" if report.get('wall_clock_used_s') else "Wall-clock used:   n/a")
    a(f"Dry run:           {report.get('dry_run')}")
    a("")
    hw = report.get("hardware", {})
    a("-- Hardware / software provenance --")
    a(f"GPU (nvidia-smi):  {hw.get('gpu_raw_nvidia_smi')}")
    a(f"Ollama version:    {hw.get('ollama_version')}")
    a(f"Model digest:      {hw.get('resolved_model_digest')}")
    a("")
    a("-- Per-scenario live run --")
    for s in report.get("scenario_runs", []):
        a(f"  {s['scenario']} ({s['chain_type']}, {s['constitution_name']}): "
          f"{s['years_completed']} years completed, "
          f"mean {s['mean_seconds_per_year']:.2f}s/year, "
          f"failed={s['simulation_failed']}" if s.get('mean_seconds_per_year') else
          f"  {s['scenario']}: no full year completed within budget")
        rp = report.get("reprompt_stats", {}).get(s["scenario"], {})
        a(f"      L1 reprompt rate: {rp.get('l1_reprompt_rate')} "
          f"({rp.get('l1_decisions_logged')} decisions logged)")
        a(f"      L2 violation rate/decision: {rp.get('l2_violation_rate_per_decision')} "
          f"({rp.get('l2_violation_rows')} violation rows)")
    a("")
    a("-- LLM call latency / tokens --")
    cs = report.get("call_stats", {})
    overall = cs.get("overall", {})
    a(f"  overall: n={overall.get('n_calls')} mean={fmt(overall.get('mean_latency_s'))}s "
      f"p95={fmt(overall.get('p95_latency_s'))}s")
    a(f"  real token usage available for {overall.get('n_calls_with_real_token_usage')}/"
      f"{overall.get('n_calls')} calls")
    if overall.get("fraction_with_real_token_usage"):
        a(f"  mean prompt tokens: {fmt(overall.get('mean_prompt_tokens'))}  "
          f"mean completion tokens: {fmt(overall.get('mean_completion_tokens'))} "
          f"(cap=512, p95={fmt(overall.get('p95_completion_tokens'))})")
    else:
        a(f"  NO real token usage returned by the Ollama server this run — "
          f"using word-count proxy: mean {fmt(overall.get('mean_completion_words_proxy'))} words/completion. "
          f"Treat all token-based figures above as an approximation, not a measurement.")
    for scen, stats in cs.items():
        if scen == "overall":
            continue
        a(f"  {scen}: n={stats.get('n_calls')} mean={fmt(stats.get('mean_latency_s'))}s "
          f"p95={fmt(stats.get('p95_latency_s'))}s")
    a("")
    det = report.get("determinism_check", {})
    a("-- Determinism check (Opening 5 / Exposure 5) --")
    if not det.get("attempted"):
        a(f"  SKIPPED: {det.get('reason')}")
    elif not det.get("completed"):
        a(f"  INCOMPLETE: {det.get('reason')}")
    else:
        a(f"  Scenario {det.get('scenario')}, seed {det.get('seed')}: "
          f"DETERMINISTIC = {det.get('deterministic')}")
        if not det.get("deterministic"):
            a(f"  {det.get('mismatch_count')} mismatches (showing up to 10):")
            for m in det.get("mismatches", []):
                a(f"    - {m}")
    a("")
    a("-- Extrapolated cost table (measured rate, not the 24-30hr assumption) --")
    ct = report.get("cost_table", {})
    for row in ct.get("rows", []):
        proxy_note = " [PROXIED from same chain_type]" if row.get("rate_is_proxied_from_other_scenario") else ""
        a(f"  {row['scenario']:>3} ({row['chain_type']:>9}): {row['runs']:>3} runs x "
          f"{row['years_per_run']:>2} yrs = {row['total_simulated_years']:>5} sim-years, "
          f"{fmt(row.get('total_hours'))}h{proxy_note}")
        if row.get("cost_by_rate"):
            costs = ", ".join(f"{k}=${v}" for k, v in row["cost_by_rate"].items())
            a(f"        cost: {costs}")
    a("")
    a(f"  TOTAL: {fmt(ct.get('total_hours'))} wall-clock hours")
    for k, v in (ct.get("total_cost_by_rate") or {}).items():
        a(f"  TOTAL COST @ {k}: ${v}")
    a("")
    a("-- VERDICT --")
    for line in report.get("verdict_lines", []):
        a(f"  {line}")
    a("")
    a("-- Assumptions a reviewer of this cost model should know --")
    for a2 in report.get("assumptions", []):
        a(f"  * {a2}")
    a("=" * 72)
    return "\n".join(lines) + "\n"


def fmt(v):
    if v is None:
        return "n/a"
    if isinstance(v, (int, float)):
        return f"{v:.3f}" if abs(v) < 1000 else f"{v:.1f}"
    return str(v)


# ──────────────────────────────────────────────────────────────────────────
# Dry run (Mac-safe self-check — NEVER touches Ollama/LangChain network)
# ──────────────────────────────────────────────────────────────────────────

def dry_run(args) -> int:
    print("DRY RUN: validating argument handling, scenario registry, a tiny")
    print("rule-based model step, and the stats/report code with synthetic")
    print("fixture data. No Ollama/LangChain network call will be made.\n")

    results_dir = resolve_results_dir(args)
    set_env_before_import(args, results_dir)
    sys.path.insert(0, str(REPO_ROOT))

    from config.scenario_registry import get_scenario, SCENARIOS  # noqa: F401
    from model_phase3 import KaNovaModelPhase3

    scenario_codes = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    chain_types = set()
    for code in scenario_codes:
        entry = get_scenario(code)  # raises loudly if unknown/not encoded
        chain_types.add(entry.chain_type)
        print(f"  registry OK: {code} -> {entry.label} ({entry.chain_type})")
    if len(chain_types) < 2 and len(scenario_codes) >= 2:
        print("  WARNING: scenario list does not include both a civilian and a "
              "military chain_type — design constraint not satisfied.")

    # Tiny RULE-BASED (use_llm=False) structural run — exercises the harness's
    # timing loop and model wiring without ever touching Ollama.
    for code in scenario_codes[:2]:
        model = KaNovaModelPhase3(scenario=code, seed=args.seed, n_citizens=50, use_llm=False)
        model.shared_data["run_id"] = args.seed
        for _ in range(2):
            model.step()
        print(f"  rule-based structural step OK: {code}, "
              f"year={model.current_year}, failed={model.shared_data.get('simulation_failed', False)}")

    # Synthetic fixture tests of the pure-python aggregation/report code —
    # this is what actually exercises the logic that would run against real
    # Ollama output, without needing Ollama to exist.
    fake_calls = [
        {"scenario": "A", "year": 0, "latency_s": 2.1, "prompt_tokens": 900,
         "completion_tokens": 140, "completion_words": 100, "had_real_usage": True,
         "used_fallback_path": False},
        {"scenario": "A", "year": 0, "latency_s": 3.4, "prompt_tokens": 950,
         "completion_tokens": 180, "completion_words": 130, "had_real_usage": True,
         "used_fallback_path": False},
        {"scenario": "C", "year": 0, "latency_s": 1.8, "prompt_tokens": 600,
         "completion_tokens": 90, "completion_words": 70, "had_real_usage": True,
         "used_fallback_path": False},
    ]
    stats = aggregate_call_stats(fake_calls)
    assert stats["overall"]["n_calls"] == 3
    assert stats["A"]["n_calls"] == 2
    print("  aggregate_call_stats() OK on synthetic data:", stats["overall"])

    cost = build_cost_table(
        {"civilian": 20.0, "military": 15.0, "_measured_codes": ["A", "C"]},
        DEFAULT_RUNS_PLAN, DEFAULT_SURVIVAL_YEARS, DEFAULT_HOURLY_RATES,
    )
    assert cost["rows"], "cost table produced no rows"
    print("  build_cost_table() OK on synthetic data, total_hours=", cost["total_hours"])

    # Determinism-diff logic, tested against two synthetic in-memory fixture
    # row sets (never touching the real elite_decisions file or Ollama).
    rows_same = [
        {"run": 0, "year": 0, "agent": "General", "decision_output": "hold",
         "parse_failure": False, "timestamp": "t1", "time_ms": 111.0},
    ]
    rows_diff = [
        {"run": 0, "year": 0, "agent": "General", "decision_output": "attack",
         "parse_failure": False, "timestamp": "t2", "time_ms": 222.0},
    ]

    def _strip(r):
        return {k: v for k, v in r.items() if k not in ("timestamp", "time_ms")}

    same_ok = [_strip(r) for r in rows_same] == [_strip(r) for r in rows_same]
    diff_ok = [_strip(r) for r in rows_same] != [_strip(r) for r in rows_diff]
    assert same_ok and diff_ok
    print("  determinism-diff logic OK on synthetic fixtures (identical/"
          "different content both detected correctly).")

    # Full synthetic report render + write, exercising the exact code path
    # `main()` uses to produce benchmark_report.json / benchmark_summary.txt,
    # with fabricated-but-realistically-shaped data standing in for a real
    # Ollama run.
    fake_report = {
        "run_started_at": datetime.now().isoformat(),
        "budget_seconds": args.budget_seconds,
        "wall_clock_used_s": 42.0,
        "dry_run": True,
        "results_dir": str(results_dir),
        "hardware": hardware_probe("llama3.2:3b"),
        "scenario_runs": [
            {"scenario": "A", "chain_type": "civilian", "constitution_name": "mfu_v7",
             "years_completed": 3, "final_year": 3, "simulation_failed": False,
             "mean_seconds_per_year": 18.4},
            {"scenario": "C", "chain_type": "military", "constitution_name": "2008_myanmar_military",
             "years_completed": 5, "final_year": 5, "simulation_failed": False,
             "mean_seconds_per_year": 14.1},
        ],
        "reprompt_stats": {
            "A": {"l1_decisions_logged": 21, "l1_reprompt_rate": 0.0,
                  "l2_violation_rows": 18, "l2_violation_rate_per_decision": 0.857},
            "C": {"l1_decisions_logged": 35, "l1_reprompt_rate": 0.028,
                  "l2_violation_rows": 2, "l2_violation_rate_per_decision": 0.057},
        },
        "call_stats": stats,
        "determinism_check": {
            "attempted": True, "completed": True, "scenario": "A", "seed": 0,
            "deterministic": False, "mismatch_count": 1,
            "mismatches": ["row 3 (General): {...} != {...}"],
        },
        "cost_table": cost,
        "verdict_lines": ["@ RTX_A6000: extrapolated total = $57.30, FITS the $80.0 ceiling (headroom = $22.70)"],
        "assumptions": ["synthetic dry-run fixture — not a real measurement"],
    }
    summary_text = render_summary(fake_report)
    assert "KA-NOVA LLM THROUGHPUT BENCHMARK" in summary_text
    assert "VERDICT" in summary_text
    json_path, txt_path = write_outputs(results_dir, fake_report)
    assert json_path.exists() and txt_path.exists()
    print(f"  render_summary()/write_outputs() OK on synthetic data -> {txt_path}")

    print("\nDRY RUN OK — safe to proceed on a pod with --dry-run removed.")
    return 0


# ──────────────────────────────────────────────────────────────────────────
# Main (pod-only live path)
# ──────────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    args = parse_args(argv)

    if args.dry_run:
        return dry_run(args)

    start = time.time()
    overall_deadline = start + args.budget_seconds

    results_dir = resolve_results_dir(args)
    set_env_before_import(args, results_dir)
    sys.path.insert(0, str(REPO_ROOT))

    runs_plan = DEFAULT_RUNS_PLAN.copy()
    if args.runs_plan:
        runs_plan.update(json.loads(args.runs_plan))
    survival_years = DEFAULT_SURVIVAL_YEARS.copy()
    if args.survival_years:
        survival_years.update(json.loads(args.survival_years))
    hourly_rates = parse_hourly_rates(args.hourly_rates)

    scenario_codes = [s.strip() for s in args.scenarios.split(",") if s.strip()]

    report = {
        "run_started_at": datetime.now().isoformat(),
        "budget_seconds": args.budget_seconds,
        "dry_run": False,
        "results_dir": str(results_dir),
        "scenarios_requested": scenario_codes,
        "n_citizens": args.citizens,
        "assumptions": [],
    }

    def checkpoint():
        write_outputs(results_dir, report)

    try:
        # ── Hardware probe ──────────────────────────────────────────────
        model_name = os.environ.get("ELITE_LLM_MODEL", "llama3.2:3b")
        report["hardware"] = hardware_probe(model_name)
        checkpoint()

        # ── Imports (AFTER env vars set) ────────────────────────────────
        from config.scenario_registry import get_scenario
        from model_phase3 import KaNovaModelPhase3
        import engine.elite_agents_v3 as elite_agents_v3_module

        chain_types_seen = set()
        for code in scenario_codes:
            entry = get_scenario(code)
            chain_types_seen.add(entry.chain_type)
        if len(chain_types_seen) < 2:
            report["assumptions"].append(
                "Scenario list did not include both a civilian and a military "
                "chain_type — the cost table's proxy rows for the missing chain "
                "type have NO measured basis at all this run."
            )

        install, uninstall = install_llm_instrumentation(elite_agents_v3_module)
        install()

        # ── Live scenario benchmark, splitting the remaining budget minus
        #    the reserved determinism slice evenly across scenarios ───────
        determinism_reserve = min(args.determinism_budget_seconds,
                                   max(0.0, overall_deadline - time.time() - 30.0))
        scenario_budget_end = overall_deadline - determinism_reserve
        per_scenario_seconds = max(
            10.0, (scenario_budget_end - time.time()) / max(1, len(scenario_codes))
        )

        scenario_runs = []
        reprompt_stats = {}
        measured_seconds_by_chain_type = {}
        measured_codes = []
        for code in scenario_codes:
            if time.time() >= scenario_budget_end:
                break
            scen_deadline = min(scenario_budget_end, time.time() + per_scenario_seconds)
            result = run_scenario_benchmark(
                KaNovaModelPhase3, code, args.seed, args.citizens, True, scen_deadline
            )
            scenario_runs.append(result)
            if result["mean_seconds_per_year"] is not None:
                measured_seconds_by_chain_type[result["chain_type"]] = result["mean_seconds_per_year"]
                measured_codes.append(code)
            reprompt_stats[code] = read_cves_reprompt_stats(results_dir, code)
            report["scenario_runs"] = scenario_runs
            report["reprompt_stats"] = reprompt_stats
            checkpoint()

        # ── Determinism check — uses one of the benchmarked scenarios. The
        #    function itself gates on wall-clock with a safety margin (see
        #    its docstring), so passing the plain overall_deadline here is
        #    safe — it will not overrun the budget to attempt this. ────────
        det_scenario = scenario_codes[0] if scenario_codes else None
        det_estimate = next(
            (r["mean_seconds_per_year"] for r in scenario_runs
             if r["scenario"] == det_scenario and r["mean_seconds_per_year"] is not None),
            None,
        )
        determinism_check = {"attempted": False, "reason": "no scenario available"}
        if det_scenario:
            determinism_check = run_determinism_check(
                KaNovaModelPhase3, results_dir, det_scenario,
                args.seed, args.citizens, True, overall_deadline,
                estimated_year_seconds=det_estimate,
            )
        report["determinism_check"] = determinism_check
        checkpoint()

        uninstall()

        # ── Aggregate call stats ────────────────────────────────────────
        report["call_stats"] = aggregate_call_stats(CALL_LOG)
        report["n_llm_calls_total"] = len(CALL_LOG)

        # ── Cost table ───────────────────────────────────────────────────
        measured_seconds_by_chain_type["_measured_codes"] = measured_codes
        report["cost_table"] = build_cost_table(
            measured_seconds_by_chain_type, runs_plan, survival_years, hourly_rates
        )

        # ── Verdict ──────────────────────────────────────────────────────
        total_cost_by_rate = report["cost_table"]["total_cost_by_rate"]
        verdict_lines = []
        for rate_name, cost in total_cost_by_rate.items():
            fits = cost <= args.budget_dollars
            verdict_lines.append(
                f"@ {rate_name}: extrapolated total = ${cost}, "
                f"{'FITS' if fits else 'EXCEEDS'} the ${args.budget_dollars} ceiling "
                f"({'headroom' if fits else 'overage'} = ${abs(args.budget_dollars - cost):.2f})"
            )
        report["verdict_lines"] = verdict_lines

        report["assumptions"].extend([
            "Scenarios not directly benchmarked this run (any of SK/TH/PK/CL/DE not in "
            "--scenarios) use the MEASURED seconds/year of the OTHER scenario sharing "
            "their chain_type as a proxy — real per-call latency may differ because "
            "prompt length and ethnic_weights schema size differ per constitution.",
            "Survival/collapse years for SK/TH/PK/CL/DE are documented PLACEHOLDERS "
            "(see DEFAULT_SURVIVAL_YEARS in this script), not measurements — the "
            "planned free rule-based survey is what should actually set them, and "
            "doing so will change this cost table's dominant term.",
            "Completion token counts are only real measurements if the Ollama "
            "server's OpenAI-compatible endpoint returned usage metadata for this "
            "run (check call_stats.overall.fraction_with_real_token_usage) — "
            "otherwise the reported figure is a word-count proxy, not a token count.",
            "The determinism check covers only ONE scenario, ONE simulated year, "
            "ONE seed — it establishes whether Ollama honours `seed` at all on this "
            "pod/version, not whether every decision across a full 50-year run would "
            "reproduce identically.",
        ])

    finally:
        report["wall_clock_used_s"] = time.time() - start
        json_path, txt_path = write_outputs(results_dir, report)
        print(render_summary(report))
        print(f"Full JSON report: {json_path}")
        print(f"Text summary:     {txt_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
