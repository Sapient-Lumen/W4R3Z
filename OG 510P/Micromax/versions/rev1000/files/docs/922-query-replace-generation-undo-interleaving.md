# Query-replace generation and undo interleaving

Rev0966 closes a supported data-corruption path in the ordinary query-replace
loop. The change is deliberately one interaction repair, not a new registry or
general transaction framework.

## The defect

A query-replace session already held a weak witness for the exact
`EditorBuffer`, but its match coordinates were not tied to the text generation
that produced them. The normal action API could therefore do this:

```text
buffer:             one one
qreplace one -> X:  [one] one
InsertText "ZZ":    ZZZZ one
late qreplace yes:  XZ one
```

`InsertText` consumed query-replace's transient selected range. The session then
remained live with old offsets and a later answer replaced the wrong text. The
same missing boundary could collapse accepted replacements and a later command
or hostcall into the wrong undo order.

This is the kind of failure the mission treats as highest priority: a familiar,
repeated editing loop can silently edit text other than the text the user was
shown.

## Repair

`QueryReplaceBufferWitness` now captures both weak object identity and the
buffer's monotonic `Buffer.version`. Every delayed response checks that exact
generation before using saved match coordinates. An accepted replacement
refreshes the witness to the generation it created.

The normal action path closes query-replace before any other known buffer-mutating
action can consume its transient selection. Accepted replacements are finalized
as their own undo row first; the later action is recorded after it, so undo
reverses the later action before the earlier replacement transaction.

Commands and hostcalls that record undo only after mutation use the central
snapshot recorder as a fallback boundary. Their pre-edit snapshot is compared
with the text owned by the live session, the transient primary selection is
removed from both sides, and the two edits become separate undo rows.

If text changes outside a trackable edit boundary, every query-replace response
fails closed and clears the capture mode. A broad grouped undo is created only
when current text is still exactly the session-owned text; otherwise Micromax
keeps the outside text and reports that grouped undo is unavailable rather than
silently overwriting it.

## Audit and refactor

The repair consolidates interleaving behavior in three small editor-owned seams:

- generation check/refresh around delayed match coordinates;
- proactive close before ordinary mutating actions;
- post-hoc transaction split in the shared undo snapshot recorder.

`qreplace all` also now propagates a stale/error failure instead of breaking its
loop and returning success. The witness fails closed when a previously readable
version counter becomes unreadable. No alternate transaction registry, buffer
ID system, or plugin-specific replacement path was introduced.

The audit checked the `Buffer` mutation helpers and direct structural mutation
sites. Supported text mutations advance `Buffer.version`; direct line-list edits
in movement/indent actions call `touch_external()`. Raw in-process code that
mutates private line storage without advancing the version remains outside the
application boundary and is not claimed safe.

## Headless evidence

`tests/test_qreplace_generation_journey.py` pins a complete 80x24 product
journey:

1. select the first match;
2. accept one replacement and show the next match;
3. perform an external insert without consuming the selected match;
4. undo the external insert;
5. undo the earlier query-replace transaction.

Additional regressions cover every delayed response after generation drift,
same-name/different-object rejection, plugin snapshot restore, direct recorded
host-style edits, grouped-undo refusal after untracked text, read-only behavior,
and exact undo ordering.

## Research used

The design follows established editor/protocol practice without copying a larger
architecture:

- Neovim exposes `b:changedtick` as a total change counter and advises API clients
  to compare it before sending commands back to a buffer:
  <https://neovim.io/doc/user/vimeval/> and
  <https://neovim.io/doc/user/api/>.
- The Language Server Protocol attaches monotonically increasing document
  versions to text documents and lets clients reject edits for the wrong
  version: <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/>.
- CodeMirror models an edit as a transaction from `startState` through `changes`
  to `newDoc`, which supports the same principle that one visible edit boundary
  should not absorb an unrelated later edit: <https://codemirror.net/docs/ref/>.

Micromax uses its existing monotonic buffer counter and undo snapshots rather
than importing a document protocol, transaction engine, or generalized version
registry.

## Residual boundary

- `Buffer.version` is an in-process generation witness, not a persistent document
  revision or distributed concurrency protocol.
- Raw Python/native code can bypass `Buffer` helpers and application policy.
- When an untracked text mutation crosses accepted replacements, Micromax
  preserves current text but cannot safely synthesize a grouped query-replace
  undo row.
- Undo remains snapshot-based and can be expensive for very large buffers; this
  revision does not introduce a rope, piece table, or operation journal.
