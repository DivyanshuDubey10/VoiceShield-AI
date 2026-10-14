import sys
import os
import traceback

try:
    from app.main import app  # noqa: F401
except Exception as exc:
    print(f"FATAL: Error importing app in backend/main.py: {exc}", file=sys.stderr)
    traceback.print_exc()
    raise
