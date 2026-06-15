"""
Ka-Nova — Prometheus Metrics Exporter
Reads progress.json and suppression_log.jsonl every 15s
and exposes metrics on http://localhost:8000/metrics
Grafana scrapes this endpoint for live dashboards.
"""

import json
import time
import logging
from pathlib import Path
from prometheus_client import start_http_server, Gauge, Counter

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

RESULTS_DIR = Path("results_phase3")
PROGRESS_FILE = RESULTS_DIR / "progress.json"
SUPPRESSION_LOG = RESULTS_DIR / "suppression_log.jsonl"
SCRAPE_INTERVAL = 15  # seconds

# ─── Metrics ────────────────────────────────────────────────────────────────

# Progress
kanova_current_run       = Gauge("kanova_current_run",       "Current run number")
kanova_total_runs        = Gauge("kanova_total_runs",        "Total runs planned")
kanova_progress_pct      = Gauge("kanova_progress_pct",      "Completion percentage")
kanova_eta_minutes       = Gauge("kanova_eta_minutes",       "Estimated minutes remaining")
kanova_ok_runs           = Gauge("kanova_ok_runs",           "Successful runs")
kanova_err_runs          = Gauge("kanova_err_runs",          "Failed runs")

# KPIs
kanova_corruption        = Gauge("kanova_corruption",        "Latest corruption index")
kanova_trust             = Gauge("kanova_trust",             "Latest trust index")
kanova_coup_probability  = Gauge("kanova_coup_probability",  "Latest coup probability")
kanova_current_step      = Gauge("kanova_current_step",      "Current simulation year")

# Suppression
kanova_suppression_total = Gauge("kanova_suppression_total", "Total suppression events detected")
kanova_suppression_new   = Counter("kanova_suppression_new", "New suppression events (cumulative)")

# Health
kanova_exporter_up       = Gauge("kanova_exporter_up",       "Exporter is running (1=yes)")
kanova_last_update_age   = Gauge("kanova_last_update_age",   "Seconds since last progress.json update")


# ─── Reader ─────────────────────────────────────────────────────────────────

_last_suppression_count = 0


def read_and_export():
    global _last_suppression_count

    # ── Progress
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE) as f:
                p = json.load(f)

            current_run  = p.get("current_run", 0)
            total_runs   = p.get("total_runs", 100)
            pct          = round((current_run / total_runs) * 100) if total_runs else 0

            kanova_current_run.set(current_run)
            kanova_total_runs.set(total_runs)
            kanova_progress_pct.set(pct)
            kanova_eta_minutes.set(p.get("eta_minutes", 0))
            kanova_ok_runs.set(p.get("ok", 0))
            kanova_err_runs.set(p.get("err", 0))
            kanova_corruption.set(p.get("latest_corruption", 0))
            kanova_trust.set(p.get("latest_trust", 0))
            kanova_coup_probability.set(p.get("latest_coup", 0))
            kanova_current_step.set(p.get("current_step", 0))

            # Age of last update
            from datetime import datetime
            updated_at = p.get("updated_at")
            if updated_at:
                age = (datetime.now() - datetime.fromisoformat(updated_at)).total_seconds()
                kanova_last_update_age.set(age)

    except Exception as e:
        logger.error(f"Error reading progress.json: {e}")

    # ── Suppressions
    try:
        count = 0
        if SUPPRESSION_LOG.exists():
            with open(SUPPRESSION_LOG) as f:
                count = sum(1 for line in f if line.strip())

        kanova_suppression_total.set(count)

        # Increment counter for new suppressions
        if count > _last_suppression_count:
            new = count - _last_suppression_count
            kanova_suppression_new.inc(new)
            _last_suppression_count = count

    except Exception as e:
        logger.error(f"Error reading suppression_log.jsonl: {e}")

    kanova_exporter_up.set(1)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    port = 8000
    start_http_server(port)
    logger.info(f"Ka-Nova Prometheus exporter running on http://localhost:{port}/metrics")
    logger.info(f"Scraping every {SCRAPE_INTERVAL}s — watching {RESULTS_DIR}/")

    while True:
        read_and_export()
        time.sleep(SCRAPE_INTERVAL)


if __name__ == "__main__":
    main()
