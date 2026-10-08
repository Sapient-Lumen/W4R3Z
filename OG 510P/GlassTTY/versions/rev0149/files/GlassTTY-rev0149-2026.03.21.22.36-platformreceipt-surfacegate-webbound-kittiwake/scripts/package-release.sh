#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 REPO_DIR OUTPUT_ZIP" >&2
  exit 1
fi

ARCHIVE_NAME_RE='^GlassTTY-rev[0-9]+-[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}-.+$'
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

REPO_DIR="$1"
OUTPUT_ZIP_INPUT="$2"
mkdir -p "$(dirname "$OUTPUT_ZIP_INPUT")"
OUTPUT_ZIP="$(cd "$(dirname "$OUTPUT_ZIP_INPUT")" && pwd)/$(basename "$OUTPUT_ZIP_INPUT")"
REPO_DIR_ABS="$(cd "$REPO_DIR" && pwd)"
REPO_NAME="$(basename "$REPO_DIR_ABS")"
OUTPUT_STEM="$(basename "$OUTPUT_ZIP" .zip)"
PACKAGE_NAME="$REPO_NAME"
if [[ "$OUTPUT_STEM" =~ $ARCHIVE_NAME_RE ]]; then
  PACKAGE_NAME="$OUTPUT_STEM"
fi

STAGE_PARENT="$(mktemp -d -t glasstty-package-release-XXXXXX)"
STAGE_ROOT="$STAGE_PARENT/$PACKAGE_NAME"
cleanup() {
  rm -rf "$STAGE_PARENT"
}
trap cleanup EXIT

mkdir -p "$STAGE_ROOT"
cp -a "$REPO_DIR_ABS"/. "$STAGE_ROOT"/

find "$STAGE_ROOT" -type d \( -name __pycache__ -o -name .pytest_cache -o -name node_modules -o -name .venv \) -prune -exec rm -rf {} +
find "$STAGE_ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '.DS_Store' \) -delete
find "$STAGE_ROOT/validation" -type d -name steps -prune -exec rm -rf {} + 2>/dev/null || true

if [[ "${GLASSTTY_PACKAGE_INCLUDE_VALIDATION_BINARIES:-0}" != "1" && -d "$STAGE_ROOT/validation" ]]; then
  find "$STAGE_ROOT/validation" -type f \( -name '*.zip' -o -name '*.patch' \) -delete
fi

rm -f "$STAGE_ROOT/RELEASE-MANIFEST.json"
RELEASE_MANIFEST_SCRIPT="$STAGE_ROOT/scripts/release_manifest.py"
if [[ ! -f "$RELEASE_MANIFEST_SCRIPT" ]]; then
  RELEASE_MANIFEST_SCRIPT="$SCRIPT_DIR/release_manifest.py"
fi
python "$RELEASE_MANIFEST_SCRIPT" --package-root "$STAGE_ROOT" --archive-name "$PACKAGE_NAME" >/dev/null

rm -f "$OUTPUT_ZIP"
(
  cd "$STAGE_PARENT"
  zip -qr "$OUTPUT_ZIP" "$PACKAGE_NAME"
)

VERIFY_SCRIPT="$REPO_DIR_ABS/scripts/verify-package.py"
if [[ ! -f "$VERIFY_SCRIPT" ]]; then
  VERIFY_SCRIPT="$SCRIPT_DIR/verify-package.py"
fi
if ! python "$VERIFY_SCRIPT" "$OUTPUT_ZIP" >/dev/null; then
  if [[ "${GLASSTTY_PACKAGE_STRICT_VERIFY:-0}" == "1" ]]; then
    echo "package verification failed for $OUTPUT_ZIP" >&2
    exit 1
  fi
  echo "warning: package verification failed for $OUTPUT_ZIP" >&2
fi

echo "$OUTPUT_ZIP"
