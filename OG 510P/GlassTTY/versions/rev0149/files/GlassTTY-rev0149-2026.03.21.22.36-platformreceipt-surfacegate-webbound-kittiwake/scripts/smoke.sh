#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pushd "$ROOT/extension" >/dev/null
npm run typecheck
npm run build
test -f "$ROOT/extension/sidepanel/index.html"
test -f "$ROOT/extension/options/index.html"
test -f "$ROOT/extension/dist/sidepanel/main.js"
test -f "$ROOT/extension/dist/options/main.js"
popd >/dev/null

PYTHONPATH="$ROOT/daemon/src${PYTHONPATH:+:$PYTHONPATH}" python -m pytest -q "$ROOT/tests"
PYTHONPATH="$ROOT/daemon/src${PYTHONPATH:+:$PYTHONPATH}" python -m glassttyd.cli doctor >/dev/null
./scripts/seed-fixture-corpus.py "$ROOT/fixtures/corpus" --force >/dev/null
./scripts/index-fixtures.py "$ROOT/fixtures/corpus" >/dev/null
./scripts/compare-fixtures.py "$ROOT/fixtures/corpus/fixturelab-home.json" "$ROOT/fixtures/corpus/fixturelab-thread.json" >/dev/null
