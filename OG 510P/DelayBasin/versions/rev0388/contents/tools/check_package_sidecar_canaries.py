import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from package_preflight_lib import package_sidecar_canary_results

rows = package_sidecar_canary_results()
failures = [row for row in rows if row.get("status") != "pass"]
if failures:
    raise SystemExit(f"package sidecar canary failures: {failures}")
print("check_package_sidecar_canaries: OK")
