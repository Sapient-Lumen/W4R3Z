# Undo, redo, and grouping (rev0992)

Micromax implements a **linear** undo/redo stack. Common one-cursor edits retain one inverse splice; eligible adjacent one-character typing/deletion may replace the newest row with one bounded exact span; immediate simultaneous edits and accepted query-replace sessions retain sparse atomic groups. `ed.with-undo` and immediate macro replay retain shallow immutable canonical line-vector generations only for touched buffers. Navigation-only macro replay remains outside history. Specialized line plans retain a broader source/projection boundary.

## Direct one-range splices

Ordinary insert, delete, newline, tab replacement, paste, and one-range hostcall edits use `Buffer.replace_range_with_witness()`. The buffer performs one normalized replacement and returns exact coordinates plus old/new slices. History retains only those slices and exact before/after cursor-selection sidecars. An equal-text replacement may therefore produce a sidecar-only row with zero retained document text.

A one-range edit has no overlap geometry to plan. Even with secondary cursors or selections, the editor maps each sidecar through the replacement's local line/column geometry and reserves the line-vector simultaneous planner for genuine multi-range operations. A seeded differential test proves left/right local mapping against the flat oracle.

## Bounded typing groups

Top-level one-code-point InsertText, Backspace, and Delete actions may replace the exact newest compatible row rather than append a new one. Continuity requires matching action kind, authority, buffer identity, action serial, buffer version, timing, sidecars, and adjacent splice geometry. The group ends after 500 ms or 256 code points and at commands, motion, nesting, selection, multicursor, structural work, failure, or authority changes. Multi-code-point input is deliberately not grouped.

`UndoManager.replace_last(expected, edit)` uses object identity, refreshes cached retained-text charges, and clears redo only after replacing the exact newest row. If the lease is lost, the editor records only the current primitive edit; it never appends an overlapping merged inverse.

## Sparse atomic groups

Every range in one simultaneous action refers to one immutable source generation. Genuine multi-range application indexes the canonical line vector directly, coalesces exact duplicates, rejects ambiguous same-start or overlapping edits before result construction, joins only touched output lines, reuses complete untouched strings, and publishes one detached vector. It never constructs complete source/result document strings solely for planning or sidecar mapping. Exact old text is captured only for changed ranges when immediate history needs it; equal replacements and aggregate-history-suppressed steps allocate no discarded old slice. Component edits that compose back into the exact source generation remain sidecar-only.

Undo and Redo resolve every addressed offset against the authoritative canonical line vector, validate every expected slice before mutation, then use the same line-vector builder and publish one detached result through `Buffer.replace_lines()`. Under fast-dirty policy neither immediate application nor sparse replay calls `Buffer.get_text()` or `Buffer.set_text()` for genuine grouped work. A stale later target cannot leave an earlier splice half-applied. Adjacent deletes remain valid when inverse insertions share a zero-width offset; source order is preserved. The flat-string implementation remains the differential oracle and exceptional query-replace generation checker.

## Delayed query-replace: sparse accepted-slice history

Query-replace remains a delayed interaction, but its history is not a broad before/after document snapshot. The bounded planner obtains one immutable session-start source and concrete ordered replacement rows. Each answer checks exact target identity/version and one local old-text range. Accepted slices record old coordinates in the source and new coordinates in the final result.

At completion, navigation away, cancellation after accepted work, or successful lifecycle cleanup, one `SimultaneousEditWitness` plus exact sidecars is recorded. Undo/Redo validates all accepted slices before one result commit. Unrelated same-width text outside addressed ranges survives; a stale addressed range refuses atomically and keeps the row. Exceptional stale boundaries reconstruct the session-owned result from source plus witness. Initial planning still retains one complete immutable source.

## `ed.with-undo`: first-write line-vector capture

`ed.with-undo` (`"desc" q -- ok`) suppresses per-step rows and emits at most one aggregate action. Its in-process transaction proceeds as follows:

1. Capture a text-free shell containing buffer membership/identity, versions, paths, dirty/saved state, cursor/selection sidecars, active/MRU/mark/search/register state, and the pre-call undo snapshot.
2. Install a transaction-local pre-text-mutation observer on every buffer present at transaction start.
3. Immediately before a buffer's first actual write, retain one detached tuple of its canonical immutable line strings. If capture fails, block the mutation. Continue observing only to distinguish one mutation boundary from several, saturating the count at two.
4. Run the quotation while nested local history is suppressed.
5. Capture another text-free shell, identify changed/removed identities, and retain after tuples only for changed buffers. Metadata-only changes may share one detached vector. A changed initial version without a first-write row fails closed.
6. Record one changed-buffer aggregate row only if durable editor state changed.
7. On quotation, finalization, accounting, or recording failure, restore the journaled vectors, non-text state, history stacks, and VM operands consumed by the hostcall.

Nested `ed.with-undo` remains one outer action. Untouched open buffers have no content generation. A touched buffer retains a complete logical before generation because arbitrary quotations need exact rollback, but unchanged line strings are shared into the after generation instead of joining and retaining a second complete document string.

`Buffer.observe_before_text_mutation()` is the mutation seam. Ordinary editor-owned mutations announce immediately before writing only while observers exist. `Buffer._restore_lines_snapshot()` also announces before trusted aggregate Undo/Redo restoration. This is essential when Undo or Redo runs inside a wider transaction: the outer first-write journal must capture the true entry text before the nested history operation changes it.

During active observation, retrieving mutable `Buffer.lines` returns a live temporary view whose mutations cross the same seam; outside observation it remains the exact raw list. An alias retained before observation is an explicit unsupported residual.

## Immediate macro replay

Immediate macro replay shares the same first-write line-vector owner but keeps macro-specific policy. Recorded provenance is used for every step. Eligible built-in action-only macros suppress temporary local rows; commands, extension actions, and Undo/Redo retain exact-history execution. One text-free after shell decides whether durable state changed. Navigation/selection-only playback records no row and retains no content vector.

Step failure restores only after any inner history-suppression guard has unwound, preserving an enclosing `ed.with-undo` depth. Finalization failure restores text vectors, non-text editor state, history, input, and macro runtime flags. A regression macro that begins with Undo and then inserts text proves the aggregate row captures the true macro-entry document and that both nested rows Undo/Redo exactly.

The eager joined-text path remains an executable differential oracle in tests and measurement tools, not a shipped mode.

## Retained-text budget

`undobytes` is a visible local soft limit, defaulting to 32 MiB per buffer; `0` means unlimited. Recording a row clears abandoned redo accounting and may retire only a complete oldest prefix of global linear history. Transactions are never split, and the newest row remains recoverable even when it alone exceeds the limit. `undostatus` reports undo/redo depth, current-buffer usage/limit, and total accounted text from cached owner totals.

For aggregate line-vector rows, logical accounting charges the complete before generation plus after separators and changed after-line content. Exact `BufferChange` geometry is admitted only when the transaction-local observer recorded exactly one mutation boundary and version/geometry checks agree. Rewound-history, multi-write, restore, and external paths use a conservative shared-prefix/suffix fallback. This prevents version rewind plus several edits from masquerading as one splice, avoids complete joins and a per-line identity set, and may overcharge a changed middle but never more than two complete logical documents.

The budget does not bound tuple/list pointers, snapshot dataclasses, callbacks, sidecars, metadata-only rows, allocator arenas, RSS, native memory, or temporary non-history work.

## Recovery feedback

Key-driven and command-bar Undo/Redo report the traversed description and target when available. Empty stacks fail explicitly. Guarded replay refusal does not consume stack membership. Budget trimming and newest-row overage remain visible.

The per-buffer `ed.push-selections`, `ed.pop-selections`, and `ed.clear-saved-selections` register is cursor/selection recovery state, not edit history, and is not governed by `undobytes`.

## Remaining pressure and next work

- Query-replace planning still retains one complete immutable source for its delayed interaction.
- Aggregate before/after/restore still copy O(number of lines) pointers even though content strings are shared.
- The broad arbitrary-rollback shell still owns many non-text sidecars and registries.
- Specialized line-plan history retains its broader source/projection owner.
- One huge logical line still rebuilds one immutable Python string per mutation.
- Eligible typing rows are bounded and code-point based; IME/grapheme semantics and one oversized newest-row policy remain explicit limits.
- First-write observation is single-process, non-durable, and not thread-safe.

Next, run one concise sustained-use journey across startup, movement, editing, search, save/recovery, plugin failure, and visual hierarchy. Reproduce a user-visible long-line or many-million-line pointer cliff before prototyping a new representation. Branching history, persistent journals, independent per-buffer graphs, a generic transaction registry, and a text-engine rewrite remain non-goals until a concrete product journey proves them necessary.
