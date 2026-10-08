#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pushd "$ROOT/extension" >/dev/null
npm run build
popd >/dev/null

exec "$ROOT/scripts/launch-chromium-profile.sh" dev chrome://extensions/
