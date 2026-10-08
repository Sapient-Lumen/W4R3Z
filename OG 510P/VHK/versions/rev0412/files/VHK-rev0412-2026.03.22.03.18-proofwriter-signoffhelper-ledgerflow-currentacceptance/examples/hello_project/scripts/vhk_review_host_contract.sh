#!/usr/bin/env sh
set -eu

DEST="${DEST:-./build/host-contract}"
mkdir -p "$DEST"

run_json() {
  name="$1"
  shift
  printf "+ %s\n" "$*"
  sh -lc "$*" > "$DEST/$name" 2> "$DEST/${name%.json}.stderr" || true
}

echo "Collecting VHK host-contract evidence into $DEST"
run_json doctor.json "vhk doctor --json"
run_json validate.json "vhk validate . --json"
run_json plan-project.json "vhk plan-project . --json"
printf "+ %s\n" "vhk gen-host-contract-pack . --force --quiet"
sh -lc "vhk gen-host-contract-pack . --force --quiet" || true
echo "Host-contract refresh complete."
echo "Review: $DEST/doctor.json, $DEST/validate.json, and $DEST/plan-project.json"
