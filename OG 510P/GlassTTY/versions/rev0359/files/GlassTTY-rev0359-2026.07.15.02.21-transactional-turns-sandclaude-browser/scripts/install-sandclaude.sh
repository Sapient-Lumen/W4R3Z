#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
MANIFEST="$ROOT/extension/manifest.json"
ENTRYPOINT="$ROOT/scripts/native-host-entrypoint.sh"
TARGET="$HOME/.config/google-chrome-for-testing/NativeMessagingHosts/com.glasstty.bridge.json"

[[ -f $MANIFEST && ! -L $MANIFEST ]] || {
  printf 'GlassTTY extension manifest is missing: %s\n' "$MANIFEST" >&2
  exit 1
}
[[ -x $ENTRYPOINT && ! -L $ENTRYPOINT ]] || {
  printf 'GlassTTY native-host entrypoint is not executable: %s\n' "$ENTRYPOINT" >&2
  exit 1
}

extension_id=$(python3 "$ROOT/scripts/extension-id.py" "$MANIFEST")
"$ROOT/scripts/install-native-host.sh" \
  --target chrome-for-testing \
  --extension-id "$extension_id" \
  --host-exe "$ENTRYPOINT"

python3 - "$TARGET" "$ENTRYPOINT" "$extension_id" <<'PY'
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
entrypoint = sys.argv[2]
extension_id = sys.argv[3]
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
expected_origin = f"chrome-extension://{extension_id}/"
if payload.get("name") != "com.glasstty.bridge":
    raise SystemExit("installed native-host manifest has the wrong host name")
if payload.get("path") != entrypoint:
    raise SystemExit("installed native-host manifest has the wrong entrypoint")
if payload.get("allowed_origins") != [expected_origin]:
    raise SystemExit("installed native-host manifest has the wrong extension origin")
PY

printf 'GlassTTY native host ready for extension %s\n' "$extension_id"
printf 'CLI: %s/glassttyd\n' "$ROOT"
