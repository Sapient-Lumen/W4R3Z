# Rev0986 audit — first-write `ed.with-undo` transaction journal

The deep implementation, research, measurement, and residual-risk record is
`docs/943-first-write-with-undo-transaction-journal.md`.

## Heart of the mission

Micromax is a calm editor for understandable least-authority automation. A script
that asks for one undoable action should not make cost scale with every open
workspace document, and a failed grouped edit must not strand partial text or an
ambiguous history row. Evidence and policy exist to protect that lived loop.

## Severe corrected defect

Before rev0986, `ed.with-undo` eagerly joined complete text for every open buffer
before running its quotation. A mark-only operation could copy megabytes and
retain no text; one failed local edit could rebuild every captured line vector.
Rev0984 compacted the eventual row but not this temporary rollback owner.

Rev0986 captures a non-text state shell first, then joins one pre-existing
buffer's complete old text immediately before its first actual write. Untouched
buffers remain unjoined. Finalization materializes only changed identities, and a
version change without a first-write row fails closed.

In the permanent eight-buffer × 1,000,000-character witness, one-character
success drops from 9 complete joins to 2 and median traced peak from 9,035,339 B
to 2,038,868 B (77.435%). Failure drops from 8 joins to 1 and peak from
20,886,816 B to 2,634,393 B (87.387%). Retained success text remains 2,000,001 B
and undo/redo/rollback are exact.

## Refactor and atomicity audit

Every editor-owned text write now crosses `Buffer.observe_before_text_mutation()`.
The one bypass—line-plan `Buffer.lines[:]` followed by late `touch_external()`—now
uses `Buffer.replace_lines()`. A source scan finds no remaining editor-owned
direct line-vector write.

After-state capture and aggregate row recording moved inside the hostcall rollback
boundary. An injected failure after the row helper mutates history proves editor
state, undo/redo stacks, and consumed VM operands restore exactly.

A permanent observed-list prototype was rejected: it measured 11.445% slower than
the branch-free mutation control. The shipped raw list plus cold observer check
measured 1.298% overhead in the same microloop.

## Research-informed design

Qt edit blocks support one user-visible undo operation and nested grouping;
SQLite rollback-journal design preserves original units before first write; and
CodeMirror inversion requires the pre-change document. Micromax adopts only the
ownership timing: its journal is ordinary process memory, whole-buffer-grained,
non-durable, single-writer, and not database atomicity.

## Missing or still risky

- A touched aggregate buffer still retains complete old/new generations.
- Macro replay still eagerly captures every open buffer; accepted query-replace
  and specialized line-plan history remain broad.
- A raw line-list alias retained before observation can bypass the temporary view.
- Simultaneous planning/replay still construct complete result strings.
- Logical `undobytes` accounting excludes object/sidecar/native/RSS overhead;
  typing remains uncoalesced.
- Sustained-use/taste evidence, signed/hermetic release, and explicit platform
  support remain incomplete.

## Executed validation

- `tests/test_rev0986_first_write_transactions.py`: **92 passed in 4.23 s**.
- The transaction, macro, hostcall, line-plan, multi-cursor, simultaneous-edit,
  rev0984, rev0985, and rev0986 behavioral union: **212 passed in 23.26 s**.
- Revision index, living-doc hygiene, context, structural-audit, and generated
  effect-contract pytest files: **21 passed** when run independently.
- Archive construction and adversarial verifier coverage: **53 passed**.
- Touched Python compilation, `scripts/lint.sh`, `mxaudit --check`, and
  `mxeffects --json --check`: passed.
- `mxportable --quiet`: **172/172 portability cases passed**.
- The regenerated context reports rev0986, 64 curated documents, five current
  priorities, and clean reference/revision checks.

The draft per-revision changelog and test receipt were folded into this audit
instead of shipping two redundant registry documents. The executable witness,
deep design record, tests, and revision index remain the sources of detail.

## What should change next

Measure sustained typing retention and Undo feel. Measure macro eager capture and
failed replay before reusing this owner. Measure accepted query-replace
separately because delayed interaction changes the boundary. Prefer lived product
evidence and net coordinator deletion over a generic transaction registry.

## What should not change yet

Do not add an undo tree, persistent journal, independent per-buffer graph, piece
table, broker, watcher, background index, generic owner framework, or Wasm host
without measured product pressure and an executable compatibility oracle.
