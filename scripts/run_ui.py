#!/usr/bin/env python3
"""Start the Aetheris navigator UI.

    .venv/bin/pip install -e '.[web]'
    .venv/bin/python scripts/run_ui.py
    # open http://127.0.0.1:8765
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    import uvicorn

    uvicorn.run("uap_kg.web.app:app", host="127.0.0.1", port=8765, reload=True)


if __name__ == "__main__":
    main()
