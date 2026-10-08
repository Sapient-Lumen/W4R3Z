#!/usr/bin/env bash
set -euo pipefail
bundle_dir="${1:?Usage: verify_source_bundle.sh <extracted-source-bundle-dir>}"
if [ ! -f "$bundle_dir/SHA256SUMS" ]; then
  echo "Missing SHA256SUMS in $bundle_dir" >&2
  exit 1
fi
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$bundle_dir" && sha256sum -c SHA256SUMS)
elif command -v shasum >/dev/null 2>&1; then
  (cd "$bundle_dir" && shasum -a 256 -c SHA256SUMS)
else
  echo "Need sha256sum or shasum" >&2
  exit 1
fi
