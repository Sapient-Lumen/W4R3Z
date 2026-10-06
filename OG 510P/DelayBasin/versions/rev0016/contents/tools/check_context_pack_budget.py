import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = ROOT / "context-pack.json"
MAX_BYTES = 4096

size = PACK.stat().st_size
if size > MAX_BYTES:
    print(f"context-pack.json too large: {size} bytes > {MAX_BYTES} bytes")
    sys.exit(1)

print(f"check_context_pack_budget: OK ({size} bytes)")
