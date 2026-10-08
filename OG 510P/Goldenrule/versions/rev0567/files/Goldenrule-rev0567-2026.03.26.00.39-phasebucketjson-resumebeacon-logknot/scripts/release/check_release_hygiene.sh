#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${RELEASE_VERSION:-dev}"
MANIFEST="$ROOT/artifacts/release/$VER/manifest.json"
SUMS="$ROOT/artifacts/release/$VER/checksums.txt"
CHANGELOG="$ROOT/CHANGELOG.md"

[[ -f "$CHANGELOG" ]] || { echo "release-hygiene: missing CHANGELOG.md" >&2; exit 1; }
[[ -f "$MANIFEST" ]] || { echo "release-hygiene: missing $MANIFEST" >&2; exit 1; }
[[ -f "$SUMS" ]] || { echo "release-hygiene: missing $SUMS" >&2; exit 1; }

grep -q "Unreleased" "$CHANGELOG" || { echo "release-hygiene: changelog missing Unreleased section" >&2; exit 1; }
python3 - <<'PY' "$MANIFEST"
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
if obj.get("schema_version") != 1:
    raise SystemExit("release-hygiene: bad manifest schema_version")
if not isinstance(obj.get("entries"), list) or not obj["entries"]:
    raise SystemExit("release-hygiene: manifest has no entries")
print("release-hygiene: manifest ok")
PY

echo "release-hygiene: ok"
