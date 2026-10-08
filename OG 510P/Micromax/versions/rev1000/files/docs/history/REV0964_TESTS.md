# Revision 0964 validation

Rev0964 is accepted with focused screen-contract, consumer, renderer, CLI,
packaging, audit, and archive evidence. Counts from overlapping invocations are
not summed. No complete repository-suite claim is made.

## Contract, consumer, and renderer regressions

- `tests/test_screen_contract.py`, `tests/test_screen_consumer.py`,
  `tests/test_screen_budget.py`, `tests/test_tui_highlight_precedence.py`,
  `tests/test_tui_matchbrace.py`, and `tests/test_tui_colorcolumn.py`:
  **44 passed**.
- Coverage includes exact fixture equality, strict JSON/token grammar and schema
  agreement, dynamic v1 relationships, short and over-budget stream reads,
  exact JSON container/scalar shapes and non-string names, terminal-control and bidi
  escaping in both text and error CLI channels, producer self-consistency,
  pre-startup geometry
  rejection, pre-deduplication diagnostic traversal bounds, live REPL refusal, color-pair
  replacement, current-only search rendering, and existing brace/color-column
  regressions.

## Targeted process and CLI evidence

- Compact file dump, explicit diagnostic dump, and failed-initial-open JSON/nonzero
  behavior: **3 passed**.
- A real producer subprocess piped its bytes into a separate consumer subprocess
  in the focused consumer suite.
- A broader dump-screen selector advanced through 13 tests but hit the
  five-minute cloudtainer command limit before a pytest summary. It is not
  counted as evidence.

## Packaging

- `tests/test_packaging_stdlib.py`: **1 passed**, including a built wheel whose
  console-script table exposes `micromax-screen`; the installed wheel loads the
  packaged v1 schema and validates a real four-row editor snapshot.

## Repository acceptance

- Revision-index and living-doc hygiene: **5 passed**.
- Compact context regressions: **6 passed**. The first acceptance run exposed
  66 document and 65 code handoff entries; removing two static chronology-heavy
  audits and listing only modified current-revision code restored the enforced
  64-entry ceilings without deleting history.
- Audit integrity regressions: **4 passed**.
- Effect/resource contract regressions: **5 passed**.
- `python -m compileall -q src tests tools`: passed.
- `python tools/mxlint.py`: passed.
- `python tools/mxaudit.py --check`: passed with current curated entrypoints and
  generated effect/resource help.
- `python tools/mxeffects.py --check-help-doc --check`: passed.
- `PYTHONPATH=tools:src python tools/mxcontext.py --check`: passed with no
  revision warnings.

## Archive acceptance

- `tests/test_mkrevzip.py`: **34 passed** with one expected duplicate-member
  warning in its rejection case. The first run correctly refused the stale
  rev0963 context snapshot; after regenerating checked rev0964 context, all
  generation, lineage, provenance, unsafe-member, and tamper tests passed.
- The emitted rev0964 archive is additionally checked with
  `mkrevzip --verify-archive`, which validates canonical naming, revision
  agreement, safe members, embedded context, package-input policy, lineage, and
  provenance hashes.

## Honest limits

Focused tests do not establish a complete repository pass, cross-terminal
Unicode-cell equivalence, visual correctness on every curses implementation,
streaming JSON rendering, or reproducible builds. `ruff` was unavailable as a
standalone module in this cloudtainer.
