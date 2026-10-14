import sys
import os
import traceback

# Add backend directory to Python search path so `app.*` imports resolve correctly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app  # noqa: F401
except Exception as exc:
    print(f"FATAL: Error importing app in root main.py: {exc}", file=sys.stderr)
    traceback.print_exc()
    raise
