# Cube deep audit — rev0334

## Finding

The cube had become safer at entry, result capture, redaction, hash-locking, and chronology, but the
post-result state was still under-specified. Once `MICRO-PILOT-RESULT.json` existed, the router stopped
with a general warning. That prevented accidental evidence import, but it failed to turn the owner’s
actual decision into a bounded next operational move.

This is a field-execution risk. A real owner will not merely ask “is the receipt safe?” They will ask
what happens next. Without a decision map, `continue-bounded` can drift into repeated cycles,
`repeat-narrower` can become cumulative evidence, `escalate-to-pilot-review` can be mistaken for
permission, and `retire` can be ignored because a completed artifact feels like progress.

## Refactor

- Added `decision_followthrough` to result receipts.
- Rendered the decision map in result markdown.
- Updated the next-action router to read an existing result and expose the bounded next step.
- Required repeat/continue to use a fresh packet and new owner-plan/run-definition hashes.
- Converted escalation into a separate future gate requirement with no evidence-import command.
- Updated generated run sheets, checklists, and decision memos so the operator sees the boundary before
  a result exists.

## Waste avoided

No new schema, branch family, custody lane, public-claim policy, or validator family was added. The
fix lives in the hot path: packet generation, result recording, next-action routing, startup guidance,
and current audit surfaces.

## Remaining risk

The archive still has no real teacher/tutor partner, no observed local instructional problem, no real
cycle, no owner-reviewed legitimate result, and no accepted `SRC2+` packet. The next meaningful work is
human field execution, not more doctrine.
