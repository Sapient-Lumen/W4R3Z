import pathlib
import sys

from release_integrity_lib import release_integrity_canary_results

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = release_integrity_canary_results()
failures = [row for row in rows if row.get("status") != "pass"]
if failures:
    raise SystemExit(f"release integrity negative canaries failed: {failures}")
required = {
    "release-integrity-valid-baseline",
    "release-integrity-content-hash-mutation",
    "release-integrity-checksum-drift",
    "release-integrity-manifest-row-omission",
    "release-integrity-path-count-drift",
    "release-integrity-provenance-command-drift",
    "release-integrity-provenance-policy-drift",
}
ids = {row.get("id") for row in rows}
missing = sorted(required - ids)
if missing:
    raise SystemExit(f"release integrity negative canaries missing required rows: {missing}")
print(f"check_release_integrity_negative_canaries: OK ({len(rows)} rows)")
