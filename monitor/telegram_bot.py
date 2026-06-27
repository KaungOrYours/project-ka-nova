"""
Ka-Nova — Telegram Monitor Bot v2
Monitors Phase 3 RunPod simulation in real time.
Scenario-aware: works for both Scenario A and C pods simultaneously.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN")
GRAFANA_URL  = os.getenv("GRAFANA_URL", "http://localhost:3000")
RESULTS_DIR  = Path("results_phase3")
PROGRESS_FILE = RESULTS_DIR / "progress.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SUBSCRIBERS: set[int] = set()


# ── Readers ───────────────────────────────────────────────────────────────────

def read_progress() -> dict:
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def read_suppressions(scenario: str = None) -> list[dict]:
    events = []
    try:
        files = []
        if scenario:
            f = RESULTS_DIR / f"suppression_log_{scenario}.jsonl"
            if f.exists():
                files = [f]
        else:
            files = list(RESULTS_DIR.glob("suppression_log_*.jsonl"))
        for fp in files:
            with open(fp) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
    except Exception:
        pass
    return events


def read_decisions(scenario: str = None) -> list[dict]:
    events = []
    try:
        files = []
        if scenario:
            f = RESULTS_DIR / f"elite_decisions_{scenario}.jsonl"
            if f.exists():
                files = [f]
        else:
            files = list(RESULTS_DIR.glob("elite_decisions_*.jsonl"))
        for fp in files:
            with open(fp) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
    except Exception:
        pass
    return events


# ── Formatters ────────────────────────────────────────────────────────────────

def format_status(p: dict) -> str:
    if not p:
        return "[--] No simulation running or progress file not found."

    scenario     = p.get("scenario", "?")
    current_run  = p.get("current_run", 0)
    total_runs   = p.get("total_runs", 100)
    current_step = p.get("current_step", 0)
    total_steps  = p.get("total_steps", 50)
    eta          = p.get("eta_minutes", "?")
    ok           = p.get("ok", 0)
    err          = p.get("err", 0)
    corruption   = p.get("latest_corruption", "?")
    trust        = p.get("latest_trust", "?")
    coup         = p.get("latest_coup", "?")
    supp_count   = p.get("suppression_count", 0)
    pct          = round((current_run / total_runs) * 100) if total_runs else 0

    # Suppression rate
    decisions    = read_decisions(scenario)
    total_llm    = len([d for d in decisions if "LLM error" not in d.get("reasoning_text", "")])
    supp_rate    = f"{round((supp_count / total_llm) * 100, 1)}%" if total_llm > 0 else "N/A"

    bar_filled = int(pct / 10)
    bar = "#" * bar_filled + "." * (10 - bar_filled)

    updated_at = p.get("updated_at", "?")

    return (
        f"[LIVE] *Ka-Nova Phase 3 — Scenario {scenario}*\n"
        f"{'─' * 32}\n"
        f"Progress:     `[{bar}] {pct}%`\n"
        f"Run:          `{current_run}/{total_runs}`\n"
        f"Year:         `{current_step}/{total_steps}`\n"
        f"ETA:          `{eta} min`\n"
        f"OK/Err:       `{ok}/{err}`\n"
        f"{'─' * 32}\n"
        f"*Latest KPIs*\n"
        f"Corruption:   `{corruption}`\n"
        f"Trust:        `{trust}`\n"
        f"Coup prob:    `{coup}`\n"
        f"{'─' * 32}\n"
        f"*Suppression*\n"
        f"Count:        `{supp_count}`\n"
        f"Rate:         `{supp_rate}`\n"
        f"{'─' * 32}\n"
        f"Updated:      `{updated_at}`\n"
        f"Dashboard:    {GRAFANA_URL}"
    )


def format_suppressions(scenario: str = None, page: int = 0) -> str:
    events = read_suppressions(scenario)
    if not events:
        return "[OK] No suppression events detected."

    per_page = 5
    total_pages = (len(events) + per_page - 1) // per_page
    start = page * per_page
    end = start + per_page
    page_events = events[start:end]

    if not page_events:
        return f"[!!] Page {page} out of range. Total: 0 to {total_pages - 1}"

    # Suppression rate
    total_llm = len(read_decisions(scenario))
    supp_rate = f"{round((len(events) / total_llm) * 100, 1)}%" if total_llm > 0 else "N/A"

    scen_label = f"Scenario {scenario}" if scenario else "All Scenarios"
    lines = [
        f"[!!] *Suppression Log — {scen_label}*\n"
        f"Total: {len(events)} | Rate: {supp_rate} | Page {page}/{total_pages - 1}\n"
        f"{'─' * 32}"
    ]
    for e in page_events:
        lines.append(
            f"Run {e.get('run','?')} | Year {e.get('year','?')} | "
            f"Agent: {e.get('agent','?')}\n"
            f"  corruption={e.get('corruption','?')} trust={e.get('trust','?')}\n"
            f"  [{e.get('reasoning_tokens','?')} tokens] {str(e.get('decision_output','?'))[:80]}\n"
            f"  {e.get('timestamp', '')[:19]}"
        )
    lines.append(f"\n/suppressions {(page+1) % total_pages} — next page")
    return "\n".join(lines)


def format_kpis(p: dict) -> str:
    if not p:
        return "[--] No KPI data available."
    scenario = p.get("scenario", "?")
    return (
        f"*KPIs — Scenario {scenario}*\n"
        f"{'─' * 32}\n"
        f"Corruption:      `{p.get('latest_corruption', '?')}`  (target < 0.20)\n"
        f"Trust:           `{p.get('latest_trust', '?')}`  (target > 0.70)\n"
        f"Coup prob:       `{p.get('latest_coup', '?')}`  (target = 0.00)\n"
        f"{'─' * 32}\n"
        f"Run:             `{p.get('current_run', '?')}/{p.get('total_runs', '?')}`\n"
        f"Year:            `{p.get('current_step', '?')}/{p.get('total_steps', '?')}`\n"
        f"ETA:             `{p.get('eta_minutes', '?')} min`"
    )


def format_agents(scenario: str = None) -> str:
    decisions = read_decisions(scenario)
    if not decisions:
        return "[--] No agent decision data yet."

    agent_stats: dict = {}
    for d in decisions:
        agent = d.get("agent", "?")
        rt = d.get("reasoning_text", "")
        if agent not in agent_stats:
            agent_stats[agent] = {"llm": 0, "error": 0, "suppressed": 0}
        if "LLM error" in rt:
            agent_stats[agent]["error"] += 1
        elif len(rt) < 20:
            agent_stats[agent]["suppressed"] += 1
        else:
            agent_stats[agent]["llm"] += 1

    scen_label = f"Scenario {scenario}" if scenario else "All"
    lines = [f"*Agent Status — {scen_label}*\n{'─' * 32}"]
    for agent, stats in agent_stats.items():
        total = sum(stats.values())
        supp_pct = round((stats["suppressed"] / total) * 100) if total else 0
        lines.append(
            f"{agent}\n"
            f"  LLM: {stats['llm']} | Error: {stats['error']} | "
            f"Suppressed: {stats['suppressed']} ({supp_pct}%)"
        )
    return "\n".join(lines)


# ── Command handlers ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    SUBSCRIBERS.add(chat_id)
    await update.message.reply_text(
        "Ka-Nova Monitor Bot v2\n\n"
        "Subscribed to live alerts.\n\n"
        "Commands:\n"
        "/status      — progress + KPIs + suppression rate\n"
        "/kpis        — KPI targets vs current values\n"
        "/agents      — per-agent LLM vs suppression breakdown\n"
        "/suppressions [scenario] [page] — suppression log\n"
        "/grafana     — live dashboard link\n"
        "/help        — all commands\n\n"
        "Auto alerts: simulation start, 20/40/60/80/100%, completion, crash"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ka-Nova Monitor Bot v2 — Commands\n"
        "─────────────────────────────────\n"
        "/status               — progress + KPIs + suppression\n"
        "/check                — same as /status\n"
        "/kpis                 — KPI targets vs actuals\n"
        "/agents               — per-agent LLM/suppression breakdown\n"
        "/agents A             — Scenario A agents only\n"
        "/agents C             — Scenario C agents only\n"
        "/suppressions         — all suppressions page 0\n"
        "/suppressions A       — Scenario A suppressions\n"
        "/suppressions C 2     — Scenario C page 2\n"
        "/grafana              — live dashboard URL\n"
        "/start                — subscribe to alerts\n"
        "/help                 — this message\n"
        "─────────────────────────────────\n"
        "Auto alerts:\n"
        "  [START]     simulation detected\n"
        "  [MILESTONE] 20/40/60/80/100%\n"
        "  [DONE]      scenario complete\n"
        "  [CRASH]     no progress 30min\n"
        "  [WARN]      KPI anomaly\n"
        "  [SUPPRESS]  suppression rate > 30%"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = read_progress()
    await update.message.reply_text(format_status(p), parse_mode="Markdown")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await status(update, context)


async def kpis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = read_progress()
    await update.message.reply_text(format_kpis(p), parse_mode="Markdown")


async def agents_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scenario = context.args[0].upper() if context.args else None
    await update.message.reply_text(format_agents(scenario), parse_mode="Markdown")


async def suppressions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scenario = None
    page = 0
    if context.args:
        if context.args[0].upper() in ["A", "B", "C"]:
            scenario = context.args[0].upper()
            if len(context.args) > 1:
                try:
                    page = int(context.args[1])
                except ValueError:
                    page = 0
        else:
            try:
                page = int(context.args[0])
            except ValueError:
                page = 0
    await update.message.reply_text(
        format_suppressions(scenario, page), parse_mode="Markdown"
    )


async def grafana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"*Ka-Nova Live Dashboard*\n"
        f"{'─' * 32}\n"
        f"URL: {GRAFANA_URL}\n"
        f"Anonymous read-only access.\n"
        f"Updates every 30s.",
        parse_mode="Markdown"
    )


# ── Auto alert loop ───────────────────────────────────────────────────────────

ALERTED_MILESTONES: set[int] = set()
LAST_SCENARIO: str = ""
LAST_SUPPRESSION_COUNT: int = 0
LAST_HEARTBEAT_RUN: int = -1
HEARTBEAT_INTERVAL_SECONDS: int = 1800
last_heartbeat_time: float = 0.0
SIMULATION_STARTED: bool = False
SIMULATION_COMPLETED: bool = False
SUPPRESSION_RATE_ALERTED: bool = False


async def auto_alert_loop(app: Application):
    global LAST_SUPPRESSION_COUNT, last_heartbeat_time, LAST_HEARTBEAT_RUN
    global SIMULATION_STARTED, SIMULATION_COMPLETED, SUPPRESSION_RATE_ALERTED
    global LAST_SCENARIO, ALERTED_MILESTONES

    await asyncio.sleep(10)

    while True:
        try:
            p = read_progress()

            if p and SUBSCRIBERS:
                scenario     = p.get("scenario", "?")

                # Reset flags when scenario changes (C -> A transition)
                if scenario != LAST_SCENARIO and LAST_SCENARIO != "":
                    SIMULATION_STARTED = False
                    SIMULATION_COMPLETED = False
                    SUPPRESSION_RATE_ALERTED = False
                    ALERTED_MILESTONES = set()
                LAST_SCENARIO = scenario
                current_run  = p.get("current_run", 0)
                total_runs   = p.get("total_runs", 100)
                current_step = p.get("current_step", 0)
                ok           = p.get("ok", 0)
                pct          = round((current_run / total_runs) * 100) if total_runs else 0
                supp_count   = p.get("suppression_count", 0)
                corruption   = p.get("latest_corruption")
                trust        = p.get("latest_trust")

                # Alert 1 — Simulation start detected
                if not SIMULATION_STARTED and ok > 0:
                    SIMULATION_STARTED = True
                    for chat_id in SUBSCRIBERS:
                        await app.bot.send_message(
                            chat_id,
                            f"[START] *Scenario {scenario} simulation started*\n"
                            f"Runs: {total_runs} | Steps: {p.get('total_steps', 50)}\n"
                            f"LLM: ON",
                            parse_mode="Markdown"
                        )

                # Alert 2 — Milestone alerts
                for milestone in [20, 40, 60, 80, 100]:
                    if pct >= milestone and milestone not in ALERTED_MILESTONES:
                        ALERTED_MILESTONES.add(milestone)
                        for chat_id in SUBSCRIBERS:
                            await app.bot.send_message(
                                chat_id,
                                f"[MILESTONE] *{milestone}% complete — Scenario {scenario}*\n\n"
                                + format_status(p),
                                parse_mode="Markdown"
                            )

                # Alert 3 — Simulation complete
                if pct >= 100 and not SIMULATION_COMPLETED:
                    SIMULATION_COMPLETED = True
                    events = read_suppressions(scenario)
                    decisions = read_decisions(scenario)
                    total_llm = len(decisions)
                    supp_rate = f"{round((len(events) / total_llm) * 100, 1)}%" if total_llm > 0 else "N/A"
                    for chat_id in SUBSCRIBERS:
                        await app.bot.send_message(
                            chat_id,
                            f"[DONE] *Scenario {scenario} COMPLETE*\n"
                            f"{'─' * 32}\n"
                            f"Runs:         `{ok}/{total_runs}`\n"
                            f"Corruption:   `{p.get('latest_corruption', '?')}`\n"
                            f"Trust:        `{p.get('latest_trust', '?')}`\n"
                            f"Coup prob:    `{p.get('latest_coup', '?')}`\n"
                            f"Suppressions: `{len(events)} ({supp_rate})`\n"
                            f"{'─' * 32}\n"
                            f"Use /agents {scenario} to see per-agent breakdown.",
                            parse_mode="Markdown"
                        )

                # Alert 4 — Suppression rate warning
                decisions = read_decisions(scenario)
                total_llm = len(decisions)
                if total_llm > 50 and not SUPPRESSION_RATE_ALERTED:
                    rate = (supp_count / total_llm) * 100
                    if rate > 30:
                        SUPPRESSION_RATE_ALERTED = True
                        for chat_id in SUBSCRIBERS:
                            await app.bot.send_message(
                                chat_id,
                                f"[SUPPRESS] *High suppression rate: {round(rate, 1)}%*\n"
                                f"Scenario {scenario} | {supp_count}/{total_llm} calls suppressed\n"
                                f"Consider checking encode/decode layer.",
                                parse_mode="Markdown"
                            )

                # Alert 5 — KPI anomaly
                if corruption is not None and (float(corruption) > 1.0 or float(corruption) < 0.0):
                    for chat_id in SUBSCRIBERS:
                        await app.bot.send_message(
                            chat_id,
                            f"[WARN] *ANOMALY: Corruption out of range*\nValue: `{corruption}`",
                            parse_mode="Markdown"
                        )
                if trust is not None and (float(trust) > 1.0 or float(trust) < 0.0):
                    for chat_id in SUBSCRIBERS:
                        await app.bot.send_message(
                            chat_id,
                            f"[WARN] *ANOMALY: Trust out of range*\nValue: `{trust}`",
                            parse_mode="Markdown"
                        )

                # Alert 6 — Crash detection
                now = asyncio.get_event_loop().time()
                if now - last_heartbeat_time > HEARTBEAT_INTERVAL_SECONDS:
                    last_heartbeat_time = now
                    if current_run == LAST_HEARTBEAT_RUN and pct < 100:
                        for chat_id in SUBSCRIBERS:
                            await app.bot.send_message(
                                chat_id,
                                f"[CRASH] *No progress in {HEARTBEAT_INTERVAL_SECONDS // 60} min*\n"
                                f"Scenario {scenario} | Last run: `{current_run}/{total_runs}`\n"
                                f"Check the pod immediately.",
                                parse_mode="Markdown"
                            )
                    LAST_HEARTBEAT_RUN = current_run

        except Exception as e:
            logger.error(f"Auto alert loop error: {e}")

        await asyncio.sleep(30)


async def post_init(app: Application):
    asyncio.create_task(auto_alert_loop(app))


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start",        start))
    app.add_handler(CommandHandler("status",       status))
    app.add_handler(CommandHandler("check",        check))
    app.add_handler(CommandHandler("kpis",         kpis))
    app.add_handler(CommandHandler("agents",       agents_cmd))
    app.add_handler(CommandHandler("suppressions", suppressions_cmd))
    app.add_handler(CommandHandler("grafana",      grafana))
    app.add_handler(CommandHandler("help",         help_cmd))

    logger.info("Ka-Nova Monitor Bot v2 started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
