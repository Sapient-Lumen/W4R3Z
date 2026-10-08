# Revision 0968 audit

## Why this work outranked new features

Rev0967 made selections visible. The first repeated editing transcript then
proved that the underlying loop was not merely rough but incorrect. Repeated
select-next stopped progressing while claiming success; selected typing applied
replacement twice; and later cursors kept stale coordinates. Macro replay added
an undo row and retained full text snapshots for every internal step. These
failures attacked trust and flow simultaneously, so another pane, registry,
indexer, or doctrine document would have been waste.

## Severe failures corrected

1. **Phantom occurrence progress.** A hidden coordinate remembered the previous
   match but was not advanced from the newest cursor. The third invocation
   retried an occupied range and returned true without changing state.
2. **Cross-buffer/stale continuation.** The hidden coordinate survived buffer
   switches and edits even though the visible selections were the real source of
   truth.
3. **Double selected insertion.** The action first replaced every selection and
   then ran a second insertion pass at the resulting cursors. Newline shared the
   defect and could normalize sidecars while mutating them.
4. **Stale multi-cursor geometry.** Sequential edits in reverse document order
   protected source ranges but did not correctly map all cursor/anchor positions
   into the final document.
5. **Macro history amplification.** One repeated user command exposed and
   retained every implementation step as a separate undo snapshot.

## Refactor boundary

The correction introduces one pure planner and one editor application seam,
not a general transaction framework. The planner owns original-document text
geometry. `Editor` owns cursor/anchor mapping, one buffer mutation, and selection
cleanup. Actions and hostcalls own only the edits they intend and their public
failure messages.

A mutation inventory after the refactor finds no direct calls from action or
hostcall implementations to `Buffer.insert`, `delete_range`, or `replace_range`.
The only direct replacement is the shared owner's one-cursor fast path. Whole-
buffer operations remain explicit `set_text` owners and were not disguised as
per-cursor edits.

## Atomicity and failure review

- All range conflicts are detected before buffer and sidecar mutation.
- Exact duplicate replacements coalesce; ambiguous overlaps and non-identical
  same-start edits fail closed.
- Hostcall arguments are peeked/planned before consumption, so a failed plan
  preserves the VM stack.
- One multi-location transaction advances the buffer mutation witness once.
- Cursor-only selection cleanup remains a real undoable editor change even when
  replacement bytes are identical and `Buffer.version` does not advance.
- Macro failure restores the broad editor replay snapshot and original history.
- Macro success discards temporary rows before recording the aggregate row.
- Navigation-only playback does not consume undo capacity or invalidate redo.

## Performance and retained-state review

The general planner is intentionally not used for the common one-cursor edit.
The direct `Buffer.replace_range()` splice performs one line-vector mutation and
one dirty/version recomputation. Its selected-range fast path reads the source
range once rather than pre-reading it and then reading it again inside the buffer.
Multi-location edits flatten and rebuild once, not once per cursor.

Known built-in action-only macro replay suppresses nested undo recording.
Suppressed snapshots retain a buffer version and cursor vectors instead of full
text. Aggregate callback closures retain one replay snapshot whose embedded
undo/redo tuples and transient action input are empty, rather than the discarded
per-step history and last input payload.

This reduces repeat-count memory growth without claiming bounded whole-editor
memory. The replay snapshot still intentionally contains complete open-buffer
text so failure and aggregate undo can span buffers.

## Baseline and historical integrity review

The working tree was compared against the verified rev0967 archive, not merely a
surviving work directory. An accidentally weakened copy of `REV0967_TESTS.md`
was restored byte-for-byte from that archive. All other non-revision differences
were classified as current source/test changes, including the deliberate buffer
splice and suppressed-snapshot refactors.

## Documentation and generated-contract reconciliation

A late audit found two independent rev0968 draft narratives pointing to different
`docs/924-*` filenames plus two D22 entries in the durable decision log. The
implementation evidence was coherent, but the handoff surface was not. The drafts
were merged into one canonical 924 note, every living link was repointed, and one
D22 now owns the coordinate-space plus undo-boundary decision.

`mxaudit --check` then exposed a stale generated effect/resource help page. It was
regenerated through `tools/mxeffects.py`; the only generated-table change is the
revision witness from rev0967 to rev0968, and the live 23-row contract now checks.

## Residual risks

- Literal occurrence selection does not wrap, search backward, cross buffers, or
  support regex/whole-word modes.
- Case-insensitive matching follows the editor's existing Python-character
  behavior; Unicode case transformations and grapheme/cell geometry remain open.
- The planner materializes complete source and result strings and is therefore
  not a large-file data-structure redesign.
- Specialized line operations still use their own geometry.
- Macro rollback covers captured editor state, not arbitrary external effects.
- Built-in action classification uses the installed action function module;
  extension and command macros intentionally take the slower exact-history path.
- No complete repository-suite or universal performance claim is made.
