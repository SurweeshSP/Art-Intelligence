#!/usr/bin/env python3
"""Root entry point for scheduled crawler runs."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_aoia_dir = _root / "aoia"
if str(_aoia_dir) not in sys.path:
    sys.path.insert(0, str(_aoia_dir))

from scripts.crawl import run

if __name__ == "__main__":
    run()
