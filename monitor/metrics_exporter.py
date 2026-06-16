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
kanova_current_run          = Gauge("kanova_current_run",          "Current run number")
kanova_runs_completed       = Gauge("kanova_runs_completed",       "Runs completed (alias for Grafana gauge panel)")
kanova_total_runs           = Gauge("kanova_total_runs",           "Total runs planned")
kanova_progress_pct         = Gauge("kanova_progress_pct",         "Completion percentage")
kanova_eta_minutes          = Gauge("kanova_eta_minutes",          "Estimated minutes remaining")
kanova_ok_runs              = Gauge("kanova_ok_runs",              "Successful runs")
kanova_err_runs             = Gauge("kanova_err_runs",             "Failed runs")

# KPIs — names match Grafana dashboard expressions exactly
kanova_corruption_index     = Gauge("kanova_corruption_index",     "Latest corruption index")
kanova_trust_index          = Gauge("kanova_trust_index",          "Latest trust index")
kanova_coup_probability     = Gauge("kanova_coup_probability",     "Latest coup probability")
kanova_gini_coefficient     = Gauge("kanova_gini_coefficient",     "Latest Gini coefficient")
kanova_iig_effectiveness    = Gauge("kanova_iig_effectiveness",    "Latest IIG effectiveness")
kanova_north_star_progress  = Gauge("kanova_north_star_progress",  "Latest North Star progress")
kanova_vpn_floor            = Gauge("kanova_vpn_floor",            "Latest VPN floor (info access)")
kanova_social_media_openness= Gauge("kanova_social_media_openness","Latest social media openness")
kanova_china_influence      = Gauge("kanova_china_influence",      "Latest China influence index")
kanova_total_shocks_fired   = Gauge("kanova_total_shocks_fired",   "Total external shocks fired")
kanova_total_shutdowns      = Gauge("kanova_total_shutdowns",      "Total social media shutdowns")
kanova_current_step         = Gauge("kanova_current_step",         "Current simulation year")

# Suppression
kanova_suppression_total    = Gauge("kanova_suppression_total",    "Total suppression events detected")
kanova_suppression_new      = Counter("kanova_suppression_new",    "New suppression events (cumulative)")

# Health
kanova_exporter_up          = Gauge("kanova_exporter_up",          "Exporter is running (1=yes)")
kanova_last_update_age      = Gauge("kanova_last_update_age",      "Seconds since last progress.json update")


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
            kanova_runs_completed.set(current_run)
            kanova_total_runs.set(total_runs)
            kanova_progress_pct.set(pct)
            kanova_eta_minutes.set(p.get("eta_minutes", 0))
            kanova_ok_runs.set(p.get("ok", 0))
            kanova_err_runs.set(p.get("err", 0))
            kanova_corruption_index.set(p.get("latest_corruption", 0))
            kanova_trust_index.set(p.get("latest_trust", 0))
            kanova_coup_probability.set(p.get("latest_coup", 0))
            kanova_gini_coefficient.set(p.get("latest_gini", 0))
            kanova_iig_effectiveness.set(p.get("latest_iig", 0))
            kanova_north_star_progress.set(p.get("latest_north_star", 0))
            kanova_vpn_floor.set(p.get("latest_vpn_floor", 0))
            kanova_social_media_openness.set(p.get("latest_social_media_openness", 0))
            kanova_china_influence.set(p.get("latest_china_influence", 0))
            kanova_total_shocks_fired.set(p.get("total_shocks_fired", 0))
            kanova_total_shutdowns.set(p.get("total_shutdowns", 0))
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
