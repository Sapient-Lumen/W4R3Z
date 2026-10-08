# Cube deep audit rev0283

Rev0283 audits source-truth language at the transition from local packet review
to bounded change control. The cube had already made first contact, route block,
and reask clocks harder to fake. The next risk was semantic: command fields were
using accepted-looking source classes before acceptance had occurred.

## What is healthy

The executable field lane remains compact and useful. Scratch routes to packet
prep; no-route routes to a no-send stop; send and reask clocks require separate
send/reask logs; returned CSVs are tied to active clocks; intake, seed, review,
decision, ticket, and live-window artifacts all state that they are not evidence
or closure.

That shape is still right. Rev0283 changes the words and gates at the point
where the old route was too easy to overread.

## What was still risky

Two meanings were too close together:

- `SOURCE_TRUTH_REQUIRED=SRC2`: the class of evidence needed before a bounded
  change can proceed.
- `SOURCE_TRUTH_CLASS=SRC2`: a statement that the current source is SRC2.

A `ready_for_real_packet` ticket should carry the first meaning, not the second.
Before rev0283, the router could immediately print a live-window-card command
with `SOURCE_TRUTH_CLASS=SRC2` after a readiness ticket. That did not import real
evidence, but it did create a false-progress affordance.

## Refactor made

- Added the explicit candidate class `SRC2-CANDIDATE-NOT-ACCEPTED` for the
  workbench-review proceed route.
- Updated `tools/decide_ft0181_field_next_action.py` so readiness tickets stop
  at `WAIT-FOR-REAL-SRC2-PACKET-BEFORE-LIVE-WINDOW` and active-change tickets
  alone emit live-window-card commands.
- Updated `tools/record_ft0181_live_window_card.py` and
  `tools/ft0181_field_guards.py` so live/staged window cards require an
  `active_change` ticket.
- Updated owner-field validators and the workbench-review operator surface so the
  distinction is tested and visible.

## What remains outside the cloudtainer

The archive still cannot receive, authenticate, or accept a real owner source
packet by itself. Rev0283 only prevents local readiness and candidate records from
borrowing accepted source-truth language. The next real progress remains an
external owner route and a returned packet that survives the actual intake and
acceptance sequence.

## Refactor posture

This pass reduced drift without widening the archive: one new source-truth label,
one router stop, one ticket-state guard, and tests at the seam. Future changes
should continue to prefer executable stops over new explanatory registries.
