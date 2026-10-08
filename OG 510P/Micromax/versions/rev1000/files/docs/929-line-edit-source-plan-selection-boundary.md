# Line edits: one source plan, semantic selection boundaries (rev0972)

## Why this became the next priority

The plugin interface work in rev0972 closed an architectural authority gap. The
next roadmap item deliberately asked for an ordinary editing failure before any
more framework work. Two small transcripts exposed a shared defect immediately:

1. Selecting whole lines `B\nC\n` as the half-open range `(1,0)..(3,0)` and
   moving them down produced the right bytes (`A D B C E`) but selected `D\n`.
   Moving the same range up selected `B\nC\nA\n`.
2. Duplicating the primary line with cursors at `(0,2)` and `(2,1)` inserted the
   right bytes but reset the primary column to zero and left the secondary cursor
   on the old numeric row, now attached to different text. Undo and redo
   faithfully preserved the wrong geometry.

These are trust failures: the visible object moved, while the direct-manipulation
state silently referred to something else.

## Root cause

The line actions changed text first and repaired cursor and anchor rows with
separate action-local conditionals. That loses one critical semantic bit. In a
half-open whole-line selection, `(end + 1, 0)` means **the boundary after the
selected block**. The same raw coordinate can also mean **the first character of
the displaced neighboring line**. Numeric line/column comparison alone cannot
distinguish those roles.

`DuplicateLine` had a second variant of the same problem: `Buffer.duplicate_line`
returned a fresh `(line + 1, 0)` cursor and the action updated only the primary
cursor. It did not project every cursor/anchor through the insertion, so columns
and source-line identity diverged.

`CutLine` also contained measurable waste and an incomplete selection contract.
It ignored selected line spans and deleted each cursor line individually. With
exact dirty checking enabled by default, every deletion rebuilt and hashed the
whole document and advanced the buffer witness. One user invocation therefore
looked like hundreds or thousands of document mutations.

## Correction

`src/micromax_editor/line_edits.py` now owns three small immutable plans:

- `MoveLineBlockPlan`: one line permutation, a bijective old-line-to-new-line
  map, and an explicit projection for a trailing selection boundary;
- `DuplicateLineBlockPlan`: one contiguous duplication with distinct
  projections for source-attached positions, the duplicate, and the insertion
  boundary; and
- `DeleteLinesPlan`: one sorted unique deletion set with source-identity cursor
  projection and deterministic landing for deleted rows.

`actions_default.py` constructs a plan from one normalized pre-edit source,
projects every cursor and anchor, commits the planned lines once, advances the
buffer mutation witness once, and records one undo snapshot. The action layer
identifies boundary-role endpoints by pairing the raw coordinate with its
anchor/cursor selection sidecar; the pure plan does not guess.

Behavior now includes:

- forward and reverse whole-line selections remain directed and select the same
  text after `MoveLinesUp` or `MoveLinesDown`;
- ordinary cursors on the displaced neighboring line follow that line rather
  than being mistaken for a selection boundary;
- `DuplicateLine` preserves the primary column, keeps later cursors attached to
  their source text, and duplicates all fully or partially selected lines;
- selection-aware duplication keeps the original directed block selected,
  matching Micro's current action behavior;
- `CutLine` removes every fully or partially selected line, otherwise every
  unique cursor line, preserves ascending source order in the linewise clipboard,
  clears selections, projects all cursors, and commits the complete row set as one
  document mutation; and
- edge moves are true no-ops with no mutation witness or undo row.

No generic edit registry, buffer rewrite, new option, schema, worker, or
background service was added.

## Measured waste removed

A fresh five-process probe used the rev0971 archive and the final rev0972
source, a 4,000-line buffer, and 1,000 cursors cutting every fourth line under
the default exact dirty check. Rev0971 took 0.598-0.657 seconds (median 0.642
seconds) and advanced `Buffer.version` 1,000 times. Rev0972 took 0.048-0.054
seconds (median 0.050 seconds) and advanced the witness once: about 12.8x faster
in this local probe while retaining one undo boundary. This is environment-
specific evidence, not a portable performance guarantee.

## External research and interpretation

Micro's current `actions.go`, read on 2026-07-18, explicitly makes `CutLine` and
`DuplicateLine` selection-aware. Its `MoveLinesUp` code also has a special
compensation branch when the trailing selection endpoint is at column zero. That
is independent evidence that a line-start coordinate can carry boundary meaning
that an ordinary line permutation must not erase.

- https://github.com/micro-editor/micro/blob/master/internal/action/actions.go
- https://github.com/micro-editor/micro/blob/master/runtime/help/keybindings.md

A current Micro issue opened 2026-06-30 reports a different `MoveLinesUp`
continuation defect: the selected bytes move but the viewport does not follow
above the top edge. Micromax already calls its shared cursor-visibility owner
after every action, but the issue reinforces the broader lesson: line movement
is complete only when text, directed selection, cursor identity, undo, and view
continuation agree.

- https://github.com/micro-editor/micro/issues/4134

The speculative architectural lesson is narrow. Line-oriented actions do not yet
justify a universal edit algebra. They do justify preserving semantic coordinate
roles through one immutable plan. If later line actions repeatedly need copied
line identity, marks, diagnostics, or folds to follow transformations, the next
owner should likely be an explicit source-line identity map—not another set of
post-mutation row patches. That should wait for a concrete failing consumer.

## Evidence

`tests/test_line_edit_geometry.py` covers the two original failures, forward and
reverse selections, ordinary displaced cursors, selection-aware duplication,
fully/partially selected cut spans, half-open cut boundaries, secondary cursor
identity, cut-all behavior, one-touch multi-line cutting, edge no-ops,
undo/redo exactness, and pure-plan properties across every valid
span in a six-line source. Existing editor-core, clipboard-authority,
multicursor, selection-stack, undo-authority, transaction, and visible-selection
suites remain part of the focused regression lane.

## Remaining limits

- Duplicate-without-selection still follows the established primary-line
  command semantics; it does not implicitly duplicate every secondary cursor
  line.
- Line plans project editor cursors and selection anchors. Marks, diagnostics,
  folds, and third-party decorations are separate owners and are not claimed to
  follow these actions.
- The current line-vector buffer still hashes full text for exact dirty state on
  each logical mutation. This revision removes repeated hashes inside one line
  action; it does not introduce a rope, piece table, incremental hash, or large-
  file claim.
- Equal adjacent line contents still count as a real move and create an undo row,
  because source-line identity and cursor movement can change even when joined
  text bytes happen to compare equal.
