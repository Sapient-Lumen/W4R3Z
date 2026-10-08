# GlassTTY rev0043 focused validation

- timestamp: 2026-03-08T19:06:28Z
- overall_ok: True
- planner_scope_tests: 3/3 passed
- validate_release_helper_tests: 2/2 passed
- fixture_corpus_count: 4
- fixture_corpus_by_adapter: {"claude": 1, "fixturelab": 3}

## Included artifacts

- `pytest-planner-scope.json`
- `pytest-validate-release.json`
- `extension-typecheck.stdout.txt`
- `extension-build.stdout.txt`
- `index-corpus.json`
- `planner-frame-plan.json`
- `compare-root-drift.json`
- `native-message-budget-frame.json`

## Honest limits

- no fresh live Chromium/native-host/browser round-trip proof exists in this bundle
- no browser-sourced scoped fixture exists in this bundle; frame/form/group root planning is synthetic-only here
