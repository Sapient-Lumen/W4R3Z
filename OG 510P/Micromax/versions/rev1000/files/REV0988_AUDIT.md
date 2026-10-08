# Rev0988 audit — bounded typing history and exact replacement leases

The deep implementation, measurement, research, and residual-risk record is
`docs/945-bounded-typing-history-groups.md`.

## Heart of the mission

Ordinary typing should be cheap to retain and sensible to undo. The editor had
already stopped copying whole documents per character, but it still built one
undo object graph and two sidecar snapshots for every keystroke. Rev0988 fixes
that lived-loop waste without adding a generic transaction framework.

## Severe corrected waste

In the permanent 10,000-character witness, bounded groups reduce:

- undo rows from 10,000 to 40 (99.600%);
- retained sidecar snapshots from 20,000 to 80 (99.600%);
- callback closure cells from 160,000 to 160 (99.900%);
- traced current Python allocations from 27,401,089 B to 146,456 B (99.466%);
  and
- traced peak Python allocations from 27,420,822 B to 168,877 B (99.384%).

Both paths retain exactly 10,000 logical text bytes and round-trip exact text and
cursor state through complete Undo and Redo.

## Shipped change

Consecutive top-level one-character InsertText, Backspace, or Delete actions may
share one exact splice row when action serial, nesting, time, geometry, buffer
identity/version, sidecars, authority, and edit kind remain continuous. A pause
of 500 ms, any intervening action or command, structural input, selection,
multicursor work, nesting, authority change, generation discontinuity, or the
256-character ceiling starts a new row.

`UndoManager` now has an identity-checked newest-row replacement primitive with
exact cached accounting and redo-branch cleanup. Merged callbacks share one
immutable span and retain only the first before-sidecars, final after-sidecars,
and aggregate old/new slices.

## Audit and refactor findings

- A first insertion of the span dataclass accidentally split `EditorBuffer` and
  removed save-recovery/disk fields from the owner. Existing interrupted-save
  tests caught it; the class boundary is corrected.
- A failed row-replacement lease initially would have appended an overlapping
  merged inverse. The recording API now reports replacement failure and falls
  back to only the current primitive edit. Forced lease loss proves two clean
  undos.
- Direct command and `mx:` keybinding paths bypass `run_action`; they now consume
  an explicit typing-history boundary. A product `Ctrl-S` journey proves Save
  cannot disappear inside a typing burst.
- Randomized differential replay compares grouped and independent-row editors
  after every mixed operation and at every grouped Undo/Redo boundary.

## Online evidence

Scintilla, CodeMirror, ProseMirror, and Qt all treat typing history as a grouped
user interaction rather than one row per primitive mutation. CodeMirror and
ProseMirror use a 500 ms default and adjacency; Scintilla and Qt expose explicit
and nested transaction boundaries. Rev0988 combines those directions with
Micromax-specific version, authority, sidecar, stale-replay, and hard-size
checks. Source URLs and retrieval details are in the deep record.

## Executed validation

- 234 focused rev0983–rev0988 history, budget, simultaneous-edit,
  first-write, macro-transaction, grouping, and measurement tests passed.
- 26 default-keybinding, action-authority, and command-authority tests passed;
  24 hostcall-transaction and interaction-authority tests passed.
- 13 delayed query-replace boundary tests, 6 focused macro/command-dispatch
  tests, and 2 interrupted-save recovery journeys passed in fresh processes.
- `mxdoctor` passed its 19-test, 9-test, and 3-test bounded risk lanes.
- `mxformat`, the offline `mxlint` fallback, bytecode compilation,
  `mxaudit --check`, `mxeffects --check`, and package-input policy checks passed.
  Optional `mypy` was unavailable in the offline environment.

These are focused and bounded gates, not a complete current full-suite claim.
The exact archive verifier is run after packaging.

## Missing or still risky

- Long-line mutation CPU is not solved; retained history shrank, but immutable
  line-string rebuilding remains.
- Multi-code-point IME/grapheme input is conservatively outside grouping.
- Accepted query-replace remains a broad delayed-session owner.
- Touched aggregate transactions still retain complete old/new generations.
- Complete-result planners and huge logical lines remain allocation risks.
- Logical `undobytes` is not total heap, RSS, sidecar, allocator, or native
  memory.
- Signed/hermetic provenance and explicit platform support remain incomplete.

## Highest-value next work

Measure accepted query-replace as a delayed interaction before compacting it.
Then profile the actual long-line mutation hot path; do not prescribe a text
engine until the measured cost and required semantics are clear.
