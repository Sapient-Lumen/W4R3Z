# Micromax revision 0966

## Outcome

Rev0966 prevents delayed query-replace answers from applying stale match
coordinates after another supported edit. Ordinary interleaving edits now close
the session before consuming its selected range, and query-replace plus the later
edit retain correct two-step undo order.

## Product repair

- Extended `QueryReplaceBufferWitness` from exact weak identity to exact identity
  plus `Buffer.version` generation.
- Checked generation before select, replace, skip, all, last, quit, and finish;
  accepted replacements refresh the witness.
- Closed query-replace before other mutating actions can consume its transient
  selection.
- Split direct command/hostcall edits from a live replacement transaction in the
  central undo recorder using their pre-edit snapshot.
- Refused unsafe broad grouped undo after untracked text drift and left current
  text untouched with an explicit message.
- Made `qreplace all` return failure when generation/error handling aborts the
  loop instead of reporting success.

## Audit/refactor

- Consolidated generation, stale-abort, external-action close, and post-hoc undo
  split behavior into editor-owned helpers rather than per-action patches.
- Audited supported `Buffer` mutation paths for monotonic version advancement.
- Made a versioned witness fail closed if its counter later becomes unreadable.
- Added one strict 80x24 headless journey plus interaction, identity, lifecycle,
  stale-drift, and undo-order regressions.

## Honest boundary

The counter is an in-process content-generation witness, not persistent revision
history. Raw Python/native code can bypass it. When untracked text crosses an
accepted replacement transaction, current text wins and grouped replacement
undo is intentionally unavailable rather than fabricated unsafely.
