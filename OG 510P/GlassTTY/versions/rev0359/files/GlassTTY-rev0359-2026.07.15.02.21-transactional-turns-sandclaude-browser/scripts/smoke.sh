#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GLASSTTY_BROWSER_BIN="${GLASSTTY_BROWSER_BIN:-/usr/bin/chromium}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"

# Linux limits AF_UNIX paths to roughly 108 bytes. Nix shells may inherit a
# deeply nested TMPDIR, making otherwise healthy broker tests fail at bind().
SMOKE_TMP_ROOT="${GLASSTTY_SMOKE_TMP_ROOT:-/tmp}"
mkdir -p -- "$SMOKE_TMP_ROOT"
SMOKE_TMPDIR="$(mktemp -d "$SMOKE_TMP_ROOT/glasstty-smoke.XXXXXX")"
trap 'rm -rf -- "$SMOKE_TMPDIR"' EXIT
export TMPDIR="$SMOKE_TMPDIR"

pushd "$ROOT/extension" >/dev/null
npm run typecheck
npm run build
for bundle in background content sidepanel options probe offscreen; do
  artifact="$ROOT/extension/dist/$bundle/main.js"
  command test -s "$artifact"
  node --check "$artifact"
  if grep -Eq '^[[:space:]]*(import|export)[[:space:]{*]' "$artifact"; then
    echo "browser bundle retains module syntax: $artifact" >&2
    exit 1
  fi
done
popd >/dev/null

pushd "$ROOT" >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python -m pytest -q
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-extension-readiness.py" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-extension-readiness.json" \
  --require-build \
  >/dev/null
node --check "$ROOT/tools/chatgpt-surface-megathing.js"
node --check "$ROOT/tools/chatgpt-surface-capsule.js"
node --check "$ROOT/tools/chatgpt-sendpath-probe.js"
node --check "$ROOT/tools/chatgpt-composer-send-drill.js"
node --check "$ROOT/tools/chatgpt-surface-oracle.user.js"
node --check "$ROOT/tools/chatgpt-pageworld-restprobe.js"
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-preflight.py" \
  --out "$ROOT/validation/latest/chatgpt-proof-preflight.json" \
  --rehearsal-out "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --evaluation-out "$ROOT/validation/latest/chatgpt-proof-rehearsal-evaluation" \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-ingest.py" \
  --input "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --out "$ROOT/validation/latest/chatgpt-proof-ingest-rehearsal-normalized.json" \
  --redacted-out "$ROOT/validation/latest/chatgpt-proof-ingest-rehearsal-redacted.json" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-ingest-summary.json" \
  >/dev/null

set +e
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-transfer-audit.py" \
  --input "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-transfer-audit.json" \
  --require-ready-to-download \
  --require-full-screenshot \
  >/dev/null
transfer_audit_status=$?
set -e
if [ "$transfer_audit_status" -ne 2 ]; then
  echo "expected rehearsal proof-transfer-audit to block with exit 2, got $transfer_audit_status" >&2
  exit 1
fi

set +e
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-attempt-audit.py" \
  --input "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-attempt-audit.json" \
  --require-ready-to-download \
  >/dev/null
attempt_audit_status=$?
set -e
if [ "$attempt_audit_status" -ne 2 ]; then
  echo "expected rehearsal proof-attempt-audit to block with exit 2, got $attempt_audit_status" >&2
  exit 1
fi
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-recovery-vault.py" \
  --input "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --out "$ROOT/validation/latest/chatgpt-first-proof-capture.from-recovery-vault.json" \
  --redacted-out "$ROOT/validation/latest/chatgpt-first-proof-capture.from-recovery-vault.redacted.json" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-recovery-vault-summary.json" \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-finalize-pack.py" \
  --input "$ROOT/validation/latest/chatgpt-proof-rehearsal.json" \
  --pack-dir "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-finalize-summary.json" \
  --export-summary-out "$ROOT/validation/latest/chatgpt-proof-pack-export-summary.json" \
  --check-summary-out "$ROOT/validation/latest/chatgpt-proof-pack-check-summary.json" \
  --clean \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-privacy-review.py" \
  --pack-dir "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack" \
  --json-out "$ROOT/validation/latest/chatgpt-proof-privacy-review.json" \
  --markdown-out "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack/privacy-redaction-review.md" \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-pack-check.py" \
  --pack-dir "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-pack-check-summary.json" \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-pack-integrity.py" \
  --pack-dir "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-pack-integrity-summary.json" \
  --refresh-ledger \
  --write-pack-file \
  --require-existing-match \
  --require-ok \
  >/dev/null

set +e
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-publish-bundle.py" \
  --pack-dir "$ROOT/validation/latest/chatgpt-proof-rehearsal-evidence-pack" \
  --out "$ROOT/validation/latest/chatgpt-proof-publish-bundle.zip" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-publish-summary.json" \
  >/dev/null
publish_status=$?
set -e
if [ "$publish_status" -ne 2 ]; then
  echo "expected rehearsal proof-publish-bundle to block with exit 2, got $publish_status" >&2
  exit 1
fi
if [ -f "$ROOT/validation/latest/chatgpt-proof-publish-bundle.zip" ]; then
  echo "proof-publish-bundle created a zip for rehearsal evidence; this must block" >&2
  exit 1
fi
set +e
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-publish-verify.py" \
  --bundle "$ROOT/validation/latest/chatgpt-proof-publish-bundle.zip" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-publish-verify-summary.json" \
  >/dev/null
verify_status=$?
set -e
if [ "$verify_status" -ne 2 ]; then
  echo "expected proof-publish-verify to block missing rehearsal publish zip with exit 2, got $verify_status" >&2
  exit 1
fi
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-status.py" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-operator-state.json" \
  --no-require-live \
  >/dev/null
PYTHONPATH="$ROOT/daemon/src:$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python "$ROOT/scripts/chatgpt-proof-autopilot.py" \
  --summary-out "$ROOT/validation/latest/chatgpt-proof-autopilot-summary.json" \
  >/dev/null
find "$ROOT" -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.pyc' -delete
python "$ROOT/scripts/verify-package.py"
popd >/dev/null
