"""Bridge proxy to launch the full AOIA dashboard at aoia/app.py.

This file resolves the path whether Streamlit Cloud is configured to run
aoia/aoia/app.py or aoia/app.py.
"""
import sys
from pathlib import Path
import runpy

_this = Path(__file__).resolve()
_aoia_pkg = _this.parent          # .../aoia/aoia
_aoia_root = _aoia_pkg.parent     # .../aoia
_repo_root = _aoia_root.parent    # repo root

for _p in (_aoia_root, _repo_root, _aoia_pkg):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

main_app_path = _aoia_root / "app.py"
if main_app_path.exists():
    runpy.run_path(str(main_app_path), run_name="__main__")
else:
    raise FileNotFoundError(f"AOIA main dashboard not found at {main_app_path}")
