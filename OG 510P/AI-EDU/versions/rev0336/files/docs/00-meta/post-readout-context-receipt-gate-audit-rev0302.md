# rev0302 post-readout context receipt gate audit

`rev0302` preserves the post-readout context receipt gate and adds a preceding
recheck brief only for due-date operator handoff.

## Preserved rule

A recheck outcome of `new_owner_context_available` is not itself context intake.
The actual returned owner context file must remain outside the archive until the
router links it to the current `new_owner_context_available` recheck through
`owner-post-readout-context-receipt`.

## New recheck brief interaction

The recheck brief may print the command skeleton for that outcome, but the skeleton
requires `NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1` and does not accept `CSV=` or
raw context. The bridge therefore makes the correct human choice visible without
weakening the receipt gate.

## Boundary

The brief is not evidence, not custody, not accepted `SRC2+`, not intake, not a
service-record edit, not public-summary support, not lifecycle movement, and not
closure. The receipt gate still remains the first local lineage step for actual
post-readout context.
