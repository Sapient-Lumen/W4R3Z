# rev0060 focused validation summary

Baseline audited before this revision: `GlassTTY-rev0059-2026.03.09.10.42-relatedframe-coverageaudit-gaptruth-lantern.zip`

## What changed

- added `bridge.probe.manifest.contentScriptPolicy` so probe artifacts preserve the current declarative content-script posture
- added shared `receiverAudit.coverageAudit.policyHints` so receiver gaps can suggest concrete Chrome levers (`runtime_priming`, `manifest_all_frames`, `manifest_match_about_blank`, `manifest_match_origin_as_fallback`)
- added `receiver_coverage_policy_hints` to `fixture.capture` metadata
- expanded deterministic receiver priming validation to cover related-frame scheme classification and policy-hint generation
- bumped extension/package version to `0.1.17`

## Commands run here

- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `node extension/scripts/receiver-inventory-check.mjs`
- `node extension/scripts/receiver-priming-check.mjs`
- `pytest -q tests/test_protocol.py tests/test_state.py tests/test_broker.py tests/test_cli.py tests/test_native_host.py tests/test_validate_release.py`
- `python scripts/doctor.py --pretty`
- `python scripts/seed-fixture-corpus.py`
- `python scripts/index-fixtures.py`
- `python scripts/compare-fixtures.py fixtures/corpus/fixturelab-home.json fixtures/corpus/fixturelab-thread.json --pretty`
- `python scripts/native-message-budget.py fixtures/corpus --pretty`

## Result

All commands above passed in this environment.

## Honest gaps

- no fresh live Chromium/native-messaging/browser round-trip was reproved here
- no real supported related-frame tab was captured to prove that the new policy hints line up with a live manifest-variant experiment
- this is strong code-level and archive-level proof, not a live browser-policy proof

## Key artifacts in this folder

- `01-extension-typecheck.txt`
- `02-extension-build.txt`
- `03-receiver-inventory-check.json`
- `04-receiver-priming-check.json`
- `05-pytest-focused.txt`
- `06-doctor.json`
- `07-seed-fixture-corpus.json`
- `08-index-fixtures.json`
- `09-compare-fixtures.json`
- `10-native-message-budget.json`
- `changed-vs-rev0059.txt`
