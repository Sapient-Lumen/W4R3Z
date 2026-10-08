# Rev0984 tests and evidence

This record reports Linux-cloudtainer evidence. Retained-allocation figures use
Python `tracemalloc`; they are not RSS, allocator-arena, native-memory, latency,
or cross-platform bounds.

## Focused history and command boundary

The final focused union completed **68 passed in 2.73 s**. It covered:

- exact UTF-8 logical-text charging, owner-identity accounting, undo/redo moves,
  abandoned-redo release, snapshot-cache rebuild, complete-prefix trimming, and
  oversized-newest-row semantics;
- cached/no-rescan accounting, deque-backed retirement, and a fixed-seed
  2,000-transition scan oracle across record, undo, redo, restore, and trim;
- local `undobytes`, `undostatus`, script read/write policy, stale replay
  membership, and command discovery;
- bounded mutation-compatible trim/overage feedback, including repeated
  oversized rows and lower-authority message boundaries;
- equal-text compact-splice release, changed-buffer aggregate retention,
  multi-buffer whole-row budgets, unchanged-text reuse, and exact transaction
  undo/redo; and
- rev0983 compact-history, macro, `ed.with-undo`, option, and undo-authority
  regressions.

## Broader editor lanes

The final source completed these bounded non-overlapping-by-command lanes:

- **179 passed in 10.54 s** — editor core, simultaneous edits, multicursor
  journeys, query-replace generation/buffer witnesses, and named macros;
- **45 passed in 14.02 s** — hostcall transactions, buffer creation, recent-file
  authority, and selection-stack authority;
- **91 passed in 15.96 s** — jump-history authority, plugin option rollback, and
  plugin runtime-group policy; and
- **17 passed in 24.20 s** — persistence capability/state behavior.

A larger combined persistence/authority process exceeded its outer ceiling while
the same component files passed in isolated processes above. This record keeps
the isolated receipts and does not relabel the combined timeout as a pass.

## Permanent retained-history witness

```bash
PYTHONPATH=src python tools/measure_history_retention.py
```

Default three-buffer, 4,000,000-character transaction:

| Metric | Broad rev0983 retained shape | Rev0984 changed-buffer shape |
| --- | ---: | ---: |
| full-text snapshot rows | 6 | 2 |
| retained snapshot text | 24,000,001 B | 8,000,001 B |
| median traced current | 24,010,323 B | 8,010,799 B |
| median traced peak | 28,211,686 B | 20,212,412 B |
| exact undo / redo | yes / yes | yes / yes |

This is a **66.636%** reduction in median traced current allocation, a **28.354%**
reduction in median traced peak, and a **66.667%** reduction in retained snapshot
text. Peak falls less because initial rollback capture still visits every open
buffer an arbitrary transaction may mutate.

The same receipt records:

- an 80-edit, 128-character, 4,096-byte budget journey retaining exactly 32
  complete rows / 4,096 bytes, retiring 48 rows / 6,144 bytes into one bounded
  feedback row, and exactly undoing/redoing the retained suffix; and
- a deterministic 20,000-row accounting probe with zero historical charge reads
  for two retained-byte queries plus a no-op budget check, and one charge read to
  retire one oldest row. A linear-rescan reference would perform 60,000 reads for
  the first operations.

The machine-readable receipt is
`.artifacts/rev0984-history-retention.json`. Archive tests pin its actual member
presence, reject duplicate-key/non-object JSON, and reject canonical revision
receipts above the 1 MiB per-file ceiling.

## Structural, portability, and timely evidence

The final source completed:

- Python bytecode compilation for touched source, tool, and regression files;
- `python tools/mxlint.py` and `bash scripts/lint.sh` with `mxlint: ok`;
- generated effect/resource contract write/check with **24 live rows**;
- `python tools/mxaudit.py --check`;
- revision-index, living-doc, audit, and effect-contract tests with **14 passed**;
- revision/context/audit/effect/archive integration with **74 passed**; the standard-library duplicate-member adversarial fixture emitted its expected warning;
- `python tools/mxportable.py --quiet` with **172/172** cases passed; and
- `make timely-tests` in **23.26 s**: context, audit, lint, and portability passed,
  while the bounded `mxtest` slice was classified as a clean budget-limited
  checkpoint. `.artifacts/mxtimely-summary.json` is the receipt.

The typecheck wrapper ran, but this offline environment does not contain mypy and
therefore reported a documented skip; no mypy-clean claim is made.

## Publication and complete-suite boundary

The publication sequence regenerates and checks `MICROMAX-CONTEXT.json`; the
compact handoff now retains the newest eleven revision entries so current
plus core evidence stays within the 64-document ceiling. It runs the
context/archive integration tests, removes caches, builds through
`tools/mkrevzip.py`, and verifies revision lineage, member provenance, digests,
CRCs, modes, timestamps, and filename policy before the archive is linked.

No completed repository-wide pytest suite, Windows run, hard process-memory
bound, or cross-platform timing claim is made. The archive claims only the
focused, bounded editor, structural, portability, timely, witness, and exact
archive verification evidence named above.
