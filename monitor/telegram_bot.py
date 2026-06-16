"""
Ka-Nova — Telegram Monitor Bot
Monitors Phase 3 RunPod simulation in real time.
Commands: /status, /suppressions, /check, /grafana
Auto-alerts: 20% milestones, crashes, anomalies, suppression events
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

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
RESULTS_DIR = Path("results_phase3")
SUPPRESSION_LOG = RESULTS_DIR / "suppression_log.jsonl"
PROGRESS_FILE = RESULTS_DIR / "progress.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SUBSCRIBERS: set[int] = set()


def read_progress() -> dict:
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def read_suppressions() -> list[dict]:
    events = []
    try:
        if SUPPRESSION_LOG.exists():
            with open(SUPPRESSION_LOG) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
    except Exception:
        pass
    return events


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
    suppressions = p.get("suppression_count", 0)
    pct          = round((current_run / total_runs) * 100) if total_runs else 0

    bar_filled = int(pct / 10)
    bar = "#" * bar_filled + "." * (10 - bar_filled)

    return (
        f"[LIVE] *Ka-Nova Phase 3 — Status*\n"
        f"{'─' * 32}\n"
        f"Scenario:     `{scenario}`\n"
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
        f"[!!] Suppressions: `{suppressions}`\n"
        f"{'─' * 32}\n"
        f"*Live Dashboard*\n"
        f"{GRAFANA_URL}"
    )


def format_suppressions(events: list[dict]) -> str:
    if not events:
        return "[OK] No suppression events detected so far."

    lines = [f"[!!] *Suppression Log — {len(events)} event(s)*\n{'─' * 32}"]
    for e in events[-5:]:
        lines.append(
            f"Run `{e.get('run','?')}` | Year `{e.get('year','?')}` | "
            f"Agent: `{e.get('agent','?')}`\n"
            f"  Conditions: corruption=`{e.get('corruption','?')}`, "
            f"trust=`{e.get('trust','?')}`\n"
            f"  Tokens: `{e.get('reasoning_tokens','?')}` | "
            f"Output: `{e.get('decision_output','?')}`"
        )
    if len(events) > 5:
        lines.append(f"_...and {len(events) - 5} more. Check suppression_log.jsonl_")
    return "\n".join(lines)


def format_grafana() -> str:
    return (
        f"*Ka-Nova Live Dashboard*\n"
        f"{'─' * 32}\n"
        f"URL:    {GRAFANA_URL}\n"
        f"Access: Anonymous read-only (no login required)\n"
        f"{'─' * 32}\n"
        f"_Dashboard updates every 30s._\n"
        f"_You cannot modify runs from this link._"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    SUBSCRIBERS.add(chat_id)
    await update.message.reply_text(
        "*Ka-Nova Monitor Bot*\n\n"
        "You are now subscribed to live alerts.\n\n"
        "Commands:\n"
        "`/status` — current progress + KPIs\n"
        "`/suppressions` — list suppression events\n"
        "`/check` — same as /status\n"
        "`/grafana` — get live dashboard link\n\n"
        "Auto alerts fire at: 20%, 40%, 60%, 80%, 100%\n"
        "and on any suppression, crash, or anomaly.",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = read_progress()
    await update.message.reply_text(format_status(p), parse_mode="Markdown")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await status(update, context)


async def suppressions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = read_suppressions()
    await update.message.reply_text(format_suppressions(events), parse_mode="Markdown")


async def grafana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_grafana(), parse_mode="Markdown")


ALERTED_MILESTONES: set[int] = set()
LAST_SUPPRESSION_COUNT: int = 0
LAST_HEARTBEAT_RUN: int = -1
HEARTBEAT_INTERVAL_SECONDS: int = 600
last_heartbeat_time: float = 0.0


async def auto_alert_loop(app: Application):
    global LAST_SUPPRESSION_COUNT, last_heartbeat_time, LAST_HEARTBEAT_RUN

    await asyncio.sleep(10)

    while True:
        try:
            p = read_progress()
            events = read_suppressions()

            if p and SUBSCRIBERS:
                current_run = p.get("current_run", 0)
                total_runs = p.get("total_runs", 100)
                pct = round((current_run / total_runs) * 100) if total_runs else 0
                suppression_count = p.get("suppression_count", len(events))

                for milestone in [20, 40, 60, 80, 100]:
                    if pct >= milestone and milestone not in ALERTED_MILESTONES:
                        ALERTED_MILESTONES.add(milestone)
                        msg = (
                            f"[MILESTONE] *{milestone}% complete*\n\n"
                            + format_status(p)
                        )
                        for chat_id in SUBSCRIBERS:
                            await app.bot.send_message(chat_id, msg, parse_mode="Markdown")

                if suppression_count > LAST_SUPPRESSION_COUNT:
                    LAST_SUPPRESSION_COUNT = suppression_count
                corruption = p.get("latest_corruption")
                trust = p.get("latest_trust")
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

                now = asyncio.get_event_loop().time()
                if now - last_heartbeat_time > HEARTBEAT_INTERVAL_SECONDS:
                    last_heartbeat_time = now
                    if current_run == LAST_HEARTBEAT_RUN and pct < 100:
                        for chat_id in SUBSCRIBERS:
                            await app.bot.send_message(
                                chat_id,
                                f"[CRASH] *No progress in {HEARTBEAT_INTERVAL_SECONDS // 60} minutes.*\n"
                                f"Last run: `{current_run}/{total_runs}`\n"
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
    app.add_handler(CommandHandler("suppressions", suppressions))
    app.add_handler(CommandHandler("grafana",      grafana))

    logger.info("Ka-Nova Monitor Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
