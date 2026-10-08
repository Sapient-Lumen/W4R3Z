# Repeated selection, simultaneous edits, and one macro transaction

Rev0968 follows the first ordinary editing loop made inspectable by rev0967:

```text
select next -> select next -> skip -> type -> play macro -> undo
```

The loop looked finished in the action list and was now visible on screen, but it
was not trustworthy. Repeating `SpawnMultiCursorSelect` stopped advancing after
the second occurrence while continuing to report success. Typing over two
selected occurrences replaced both and then inserted the same text again, so
`foo foo` became `XX XX` instead of `X X`. Newline followed the same two-pass
shape. Unselected later cursors were left in pre-edit coordinates after earlier
insertions or deletions. Replaying a repeated macro retained one full undo
snapshot per step and exposed those implementation steps as separate undo rows.

These are not missing decorations. They break the core promise that visible
selections name the text one command will change and that one user invocation
has one understandable undo boundary.

## The repaired journey

With `foo foo foo foo` and the primary cursor on the first word:

1. the first select-next invocation selects the first and second occurrences;
2. the second invocation adds the third, using the newest selected occurrence as
   the continuation point;
3. skip moves only that newest selection to the fourth occurrence, preserving
   the first two choices and the primary designation;
4. typing `bar` produces `bar bar foo bar` exactly once at each selected range;
5. all resulting cursors land at their own replacement ends;
6. undo restores the original text and selections; redo restores the edited
   text and rebased cursors.

The public `micromax.screen.v1` journey validates the selection cues before the
edit. There is no renderer-only state and no hidden global “last match” offset.

## Occurrence continuation is derived from live state

`SpawnMultiCursorSelect` and `SkipMultiCursor` now derive their needle and
continuation point from the active buffer's normalized cursor/selection state.
Cursor lists remain in document order, while monotonic cursor IDs retain
creation order. The highest matching cursor ID is therefore the newest selected
occurrence even after sorting, cycling the primary cursor, switching buffers, or
editing elsewhere.

The first invocation may create the primary word selection and add the next
literal occurrence. Later invocations skip already-selected ranges. Exhaustion
returns false unless the invocation itself created the initial selection; there
is no phantom success. Skip advances the newest matching selection rather than
moving the primary or discarding earlier choices.

The search remains intentionally small: forward, literal, non-wrapping, and
line-local, with the existing `ignorecase` behavior. A multiline selection is
refused rather than assigned a fabricated same-line endpoint. Regex, whole-word,
backward, wrap, and cross-buffer occurrence selection remain future product
choices, not accidental semantics.

## One immutable coordinate space for an edit

`simultaneous_edits.py` is a small pure planner. Every requested range refers to
one normalized pre-edit document. It converts line/column coordinates to flat
offsets once, validates the complete set before mutation, constructs the result
once, and supplies one mapping from original positions into the result.

The installed rules are:

- exact duplicate edits coalesce, allowing multiple owners to land at the same
  replacement end;
- any other same-start or overlapping ranges fail closed before text, cursor,
  selection, undo, or VM argument state changes;
- adjacent edits are valid;
- owner cursors land at the end of their own replacement;
- every other cursor and retained anchor uses right-affinity mapping through the
  same plan;
- a genuine multi-location operation advances `Buffer.version` once.

Micromax deliberately chooses a stricter same-start rule than the Language
Server Protocol. LSP permits ordered multiple inserts at one position. The
editor has no user-visible ordering contract for competing cursors at one point,
so ambiguous non-identical same-start edits are rejected instead of relying on
cursor-list accident.

The shared transaction now backs ordinary text, newline, tab, paste, backspace,
delete, selected cut, indent/unindent line edits, query-replace's accepted
match, and the `ed.replace-selections`, `ed.replace-range`, and
`ed.delete-range` hostcalls. Hostcall arguments are consumed only after the plan
succeeds. This gives action and script entry points the same geometry and the
same fail-closed boundary.

## The one-cursor path remains cheap

A general immutable-document planner would flatten, index, rebuild, split, and
re-index the whole buffer for every ordinary keystroke. The editor therefore
keeps a narrow fast path for exactly one owned edit and one cursor. `Buffer`
performs replacement as one direct line-vector splice rather than composing a
delete and an insert, so one logical replacement has one version/dirty
transition and no observable intermediate document.

That audit also removed an inconsistent text boundary. Python `splitlines()`
recognizes Unicode separators such as U+2028; some old mutation paths therefore
treated them as line breaks while others treated them as data. Buffer text now
normalizes only CRLF and CR to LF. Other Unicode characters remain ordinary
buffer content, matching the editor's documented fileformat contract.

## One macro invocation, one undo row

Successful macro playback now records one aggregate editor transaction for the
invocation, including repeated playback and changes spanning multiple open
buffers. A 64-step built-in action macro no longer retains 64 discarded full
text snapshots. Known built-in action-only macros run with per-step undo
recording suppressed; the enclosing before/after snapshots own rollback and the
single aggregate row.

Command steps, extension actions, and macros containing Undo or Redo take the
exact-history path because they may intentionally inspect or manipulate history.
Their temporary rows are discarded only after successful playback and replaced
with the aggregate transaction. Navigation-only playback does not invent an
undo row or clear existing redo history. The aggregate row keeps the playback
caller's script/plugin authority.

This is an editor-state transaction, not universal atomicity. A failed replay
restores captured buffers, cursors, selections, editor registers, and undo
history. It cannot roll back arbitrary filesystem writes, processes, network
activity, native effects, memory use, or wall-clock work performed by an
extension.

## Audit and refactor result

The changed action/hostcall inventory has one live primitive for per-cursor text
geometry. No editor action or hostcall directly calls `Buffer.insert`,
`delete_range`, or `replace_range`; the sole direct replacement call is the
single-cursor fast path inside the shared owner. Bulk whole-buffer owners still
use `set_text` and remain separately visible in the mutation inventory.

Suppressed undo recording now captures a monotonic buffer-version witness plus
cursor sidecars instead of copying full text for nested edit-boundary and
replace-all rows. The enclosing macro or `ed.with-undo` snapshot remains the
rollback authority. Query-replace is the exception because its post-hoc boundary
repair still requires exact before/after text. Aggregate callbacks strip both
discarded undo/redo rows and transient action input because their restore path
deliberately restores neither; otherwise the visible history collapse would
still retain the discarded closures and their full-text snapshots.

Randomized reference checks compared 20,000 non-overlapping edit sets against a
simple reverse-application oracle and another 20,000 position mappings against a
right-affinity oracle. Committed seeded tests cover 500 additional plans,
overlap atomicity, argument preservation, one-mutation witnesses, newline
normalization, mixed selected/unselected cursors, and line indentation geometry.

One final bounded cloudtainer probe replayed a one-step insert macro 256 times
in a 262,144-character fast-dirty buffer. The recovered rev0967 baseline retained
256 undo rows and reported 1.61 seconds / 361,496 KiB maximum RSS; this tree
retained one row and reported 1.69 seconds / 301,536 KiB. That is one comparative
run, not a universal latency claim. It verifies the history collapse and a lower
retained-memory witness on the exercised path; the small elapsed-time difference
is treated as noise, not an improvement.

## Primary-source research reviewed on 2026-07-18

- VS Code documents repeated selection of the next occurrence and a separate
  command that skips the next match. That supports preserving earlier choices
  while moving the newest selection, not moving the primary selection:
  https://code.visualstudio.com/docs/editing/codebasics
- Sublime Text documents the same “Quick Add Next” / “Quick Skip Next” loop and
  selection undo, reinforcing that repetition is a stateful direct-manipulation
  journey rather than a stateless search command:
  https://www.sublimetext.com/docs/multiple_selection_with_the_keyboard.html
- Micro's current action source chooses the last/newest cursor as the spawner and
  skip target. Micromax retains document-order cursor lists, so cursor creation
  IDs provide the equivalent continuation fact without editor-global offsets:
  https://github.com/micro-editor/micro/blob/master/internal/action/actions.go
- CodeMirror's change model groups ranges that refer to the starting document,
  and `changeByRange` derives one change plus resulting range per selection. That
  independently supports one shared plan rather than sequential cursor loops:
  https://codemirror.net/examples/change/ and
  https://codemirror.net/docs/ref/#state.EditorState.changeByRange
- VS Code's `TextEditorEdit` batches one editor transaction and rejects invalid
  overlap or a document that changed before application:
  https://code.visualstudio.com/api/references/vscode-api#TextEditorEdit
- LSP 3.17 states that a text-edit array moves one document state S1 to S2, all
  ranges refer to S1, and ranges must not overlap. That is the basis for the
  immutable-source planner and pre-mutation validation:
  https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
- Vim documents undo blocks as user-visible change units and exposes `:undojoin`
  only when a caller deliberately wants a following change in the same block.
  That supports one macro invocation producing one deliberate history row rather
  than leaking each implementation step:
  https://vimhelp.org/undo.txt.html
- Kakoune makes multiple selections the central editing primitive rather than a
  side mode. That reinforces the requirement that selection visibility, text
  geometry, and command/undo boundaries agree:
  https://kakoune.org/why-kakoune/why-kakoune.html

The research validates the interaction and coordinate models. It does not
justify importing a general search engine, workspace-edit protocol, selection
registry, or macro framework.

## Honest residual boundary and speculation

- Occurrence matching is still line-local and uses Python character coordinates;
  grapheme clusters, terminal cells, and Unicode case transformations that
  change string length remain broader editor concerns.
- Large simultaneous edits build one complete result string. This is coherent
  and bounded by the current in-memory buffer model, but it is not a rope or
  piece-table solution for hostile multi-gigabyte buffers.
- Line-oriented commands such as cut-line, duplicate-line, and move-lines still
  have specialized geometry and deserve future transcript-driven scrutiny; they
  were not folded into this revision merely for symmetry.
- External macro effects remain outside rollback. Isolation should follow a
  smaller extension interface, not a larger snapshot claim.

The next likely high-value risk is no longer invisible multicursor mutation. It
is repeated navigation across lines and buffers: find-next/find-previous,
project picker, recent files, and buffer switching still form separate loops.
That is a hypothesis, not a roadmap mandate. Capture one transcript and repair
its first recurring failure before adding wrap modes, search registries, result
panes, or background indexing.
