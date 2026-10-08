# rev0062 focused validation summary

## Direct commands run

- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `node extension/scripts/receiver-inventory-check.mjs`
- `node extension/scripts/receiver-priming-check.mjs`
- `node extension/scripts/content-script-experiment-check.mjs`
- `pytest -q tests/test_protocol.py tests/test_state.py tests/test_broker.py tests/test_cli.py tests/test_native_host.py tests/test_validate_release.py`
- `python scripts/doctor.py --pretty`
- `python scripts/seed-fixture-corpus.py fixtures/corpus --force`
- `python scripts/index-fixtures.py fixtures/corpus --pretty`
- `python scripts/compare-fixtures.py fixtures/corpus/fixturelab-home.json fixtures/corpus/fixturelab-thread.json --pretty`
- `python scripts/native-message-budget.py fixtures/corpus --pretty`
- `python scripts/validate-release.py --out-dir validation/rev0062-wrapper` *(wrapper attempt preserved for honesty; not treated as the release gate here)*

## Result

- extension typecheck: passed
- extension build: passed
- deterministic receiver inventory check: passed
- deterministic receiver priming check: passed
- deterministic content-script experiment check: passed
- focused pytest slice: passed (`40 passed`)
- doctor / fixture-corpus / compare-fixtures / native-message-budget direct checks: passed
- wrapper validator: attempted, but still not treated as the authoritative release gate in this container

## Still not proven here

- one live Chromium/native-messaging/browser round-trip where `set-content-script-experiment` is exercised against a real supported tab
- one before/after coverage comparison showing the observed post-reload result matches the saved experiment-plan prediction closely enough to justify a default policy change
