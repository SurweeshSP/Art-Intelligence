"""Root entry point for Streamlit Cloud deployment."""
import sys
from pathlib import Path
import runpy

_root = Path(__file__).resolve().parent
_aoia_dir = _root / "aoia"

for _p in (_aoia_dir, _root):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

main_app_path = _aoia_dir / "app.py"
if main_app_path.exists():
    runpy.run_path(str(main_app_path), run_name="__main__")
else:
    raise FileNotFoundError(f"AOIA main dashboard not found at {main_app_path}")
