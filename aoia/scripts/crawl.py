#!/usr/bin/env python3
"""Daily crawler runner script for AOIA (Art Opportunity Intelligence Agent).

This script:
1. Executes the polite asynchronous crawl across registered official fine arts sources.
2. Normalizes, deduplicates, and scores opportunities.
3. Performs a SQLite WAL checkpoint to ensure the database file is cleanly written to disk.
"""

from __future__ import annotations

import sys
import shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# Ensure aoia package is discoverable
_script_dir = Path(__file__).resolve().parent
_aoia_root = _script_dir.parent
_repo_root = _aoia_root.parent

for p in (_aoia_root, _repo_root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from aoia import pipeline, db


def run():
    now_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"==================================================")
    print(f"[{now_str}] Starting AOIA Scheduled Crawl Pipeline")
    print(f"==================================================")

    def log_cb(msg: str):
        ts = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%H:%M:%S")
        print(f"[{ts}] {msg}", flush=True)

    try:
        ranked, checked_sources, diagnostics = pipeline.run_pipeline(progress_callback=log_cb)
    except Exception as e:
        print(f"\n[ERROR] Pipeline run failed: {e}", file=sys.stderr)
        raise

    total_opps = len(ranked)
    passed_sources = diagnostics.get("sources_passed", 0)
    duration = diagnostics.get("duration_seconds", 0)

    print(f"\n==================================================")
    print(f"Pipeline finished successfully in {duration}s!")
    print(f"Active sources processed: {passed_sources}")
    print(f"Total scored opportunities: {total_opps}")
    print(f"==================================================")

    # Clean WAL checkpoint so aoia_data.db is fully self-contained
    print("[*] Performing SQLite WAL checkpoint (TRUNCATE)...")
    with db._repo.get_connection() as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    # If repo root has a copy of aoia_data.db, keep it in sync
    primary_db = _aoia_root / "aoia_data.db"
    root_db = _repo_root / "aoia_data.db"
    if primary_db.exists() and root_db.exists():
        shutil.copy2(primary_db, root_db)
        print(f"[*] Synced updated database to repo root ({root_db})")

    print("[*] Database checkpoint completed cleanly.")


if __name__ == "__main__":
    run()
