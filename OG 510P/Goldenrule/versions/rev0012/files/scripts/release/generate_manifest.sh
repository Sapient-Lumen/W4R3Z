#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VER="${1:-${RELEASE_VERSION:-dev}}"
OUT_DIR="$ROOT/artifacts/release/$VER"
mkdir -p "$OUT_DIR"

FILES=(
  "Cargo.toml"
  "Cargo.lock"
  "pyproject.toml"
  "README.md"
  "docs/PROJECT_CHARTER.md"
  "docs/SCIENCE_PLAN.md"
  "examples/gauntlet/gauntlet_v2.json"
  "specs/spec_ledger.yaml"
)

SUMS="$OUT_DIR/checksums.txt"
MANIFEST="$OUT_DIR/manifest.json"
: > "$SUMS"

for f in "${FILES[@]}"; do
  if [[ -f "$ROOT/$f" ]]; then
    (cd "$ROOT" && sha256sum "$f") >> "$SUMS"
  fi
done

python3 - <<'PY' "$MANIFEST" "$VER" "$SUMS"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

manifest_path = Path(sys.argv[1])
ver = sys.argv[2]
sums_path = Path(sys.argv[3])

entries = []
for line in sums_path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    digest, rel = line.split("  ", 1)
    entries.append({"path": rel, "sha256": digest})

payload = {
    "schema_version": 1,
    "version": ver,
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "entries": entries,
}
manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

echo "release-manifest: wrote $MANIFEST and $SUMS"
