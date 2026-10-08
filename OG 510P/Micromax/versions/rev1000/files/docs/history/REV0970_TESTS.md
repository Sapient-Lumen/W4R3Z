# Revision 0970 test evidence

## Focused executable slice

```bash
pytest -q \
  tests/test_regex_containment.py \
  tests/test_regex_hostcalls.py \
  tests/test_search_navigation_journey.py \
  tests/test_tui_hlsearch.py \
  tests/test_editor_core.py \
  tests/test_editor_query_replace.py
```

Result: **154 passed in 10.81s** against the final pre-seal source generation.

This slice covers the one-shot worker protocol, catastrophic timeout, deep parser-recursion classification, startup/request clocks, slow teardown, match/result ceilings, VM operand preservation, all-positive-timeout routing, editor candidate-state preservation, exact search snapshots, TUI compatibility behavior, Unicode source offsets, immutable query-replace rows, and ordinary editor replacement/search journeys.

## Static and generated contracts

- `bash scripts/lint.sh` — passed (`mxlint: ok`).
- Python bytecode compilation of every modified runtime, editor search/replacement, audit, and regression module — passed.
- `python tools/mxaudit.py --check` — passed after the compile-boundary audit was strengthened.
- `python tools/mxeffects.py --write-help-doc --check-help-doc --check` — passed; generated effect/resource help is current for rev0970.
- Living-doc hygiene, revision-index, context, structural-audit, effect-contract, and docs-index tests — **35 passed** across their isolated files.
- `tests/test_mkrevzip.py` — **52 passed**; duplicate-member rejection intentionally emits one standard-library warning in its adversarial fixture.
- `python tools/mxcontext.py --json --check` — passed with **64** curated documents, the enforced handoff ceiling.

## Aggregate-suite honesty

`make test PYTEST_ARGS='-q' TEST_TIMEOUT=1800` collected **2,938 tests** under the process-group-aware aggregate runner. That isolated run exceeded the available execution window and was terminated; the runner reported that its pytest child was cleaned up. It is not counted as a pass and this revision makes **no complete-suite claim**.

The archive contains only scoped evidence that completed against this revision. Prior revision manifests are not reused as rev0970 proof.

## Final archive evidence

Target archive:

`Micromax-rev0970-2026.07.18.03.29-regex-compile-match-containment-qreplace-plan-bronzeauk.zip`

Final acceptance checks performed on the exact named archive:

- `python tools/mkrevzip.py --verify-archive` — passed revision/filename agreement, context and manifest lineage, member-name/path policy, duplicate detection, CRC, and declared digest checks.
- `unzip -t` — passed with no compressed-data errors.
- clean extraction followed by `python tools/mxcontext.py --check` — passed at rev0970 with the 64-document curated handoff.
- archive member audit — zero `__pycache__`, `.pytest_cache`, `.pyc`, or `.pyo` members.

The archive is rebuilt after this evidence is recorded and the same checks are repeated before the delivery link is emitted.
