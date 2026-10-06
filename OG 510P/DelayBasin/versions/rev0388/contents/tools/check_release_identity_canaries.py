import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from release_hygiene_lib import BUNDLE_RE, build_bundle_name, parse_bundle_name, release_identity_canary_results, validate_release_identity

rows = release_identity_canary_results()
failures = [row for row in rows if row.get("status") != "pass"]
if failures:
    raise SystemExit(f"release identity canary failures: {failures}")

canonical = "DelayBasin-rev0351-2026.06.10.12.04-nameguard-sidecar-releaseid.zip"
parsed = parse_bundle_name(canonical)
if parsed != {
    "project": "DelayBasin",
    "revision": "rev0351",
    "timestamp": "2026.06.10.12.04",
    "slug": "nameguard-sidecar-releaseid",
    "bundle": canonical,
}:
    raise SystemExit(f"canonical bundle parsing drifted: {parsed}")
if build_bundle_name("rev0351", "2026.06.10.12.04", "nameguard-sidecar-releaseid") != canonical:
    raise SystemExit("build_bundle_name drifted from canonical bundle structure")
if not BUNDLE_RE.fullmatch(canonical):
    raise SystemExit("canonical bundle regex rejected a valid release filename")
for bad_args in [
    ("rev0351", "2026/06/10/12/04", "nameguard"),
    ("rev0351", "2026.06.10.12.04", "nameguard_sidecar"),
    ("rev0351", "2026.06.10.12.04", "nameguard/sidecar"),
    ("rev351", "2026.06.10.12.04", "nameguard"),
]:
    try:
        validate_release_identity(*bad_args)
    except ValueError:
        continue
    raise SystemExit(f"invalid release identity accepted: {bad_args}")
print("check_release_identity_canaries: OK")
