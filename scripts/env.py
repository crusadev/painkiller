"""Load .env into os.environ. No dependency, no overwrite of real env vars."""
import os, pathlib

def load_env(path=None):
    p = pathlib.Path(path or pathlib.Path(__file__).resolve().parent.parent / ".env")
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
