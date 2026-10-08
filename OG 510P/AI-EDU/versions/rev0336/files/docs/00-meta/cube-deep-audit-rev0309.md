# rev0309 cube deep audit

## Highest-risk seam inspected

This pass inspected the near-activation chain after the rev0308 lane firebreak.
The field lane now blocks checker/release/legacy scratch from sourcing later
field actions, but integrity also depends on the source snapshot hashes being
re-anchored to the referenced bytes at each major handoff.

Two guards were too permissive for a chain this close to activation:

1. A post-decision change ticket validated the referenced first-packet decision
   and checked many copied fields, but did not fail if the recorded
   `source_first_packet_decision.decision_sha256` was stale or wrong.
2. Live-window entry/card validation checked the referenced post-decision ticket
   and its copied fields, but the ticket snapshot hash needed an explicit
   equality check wherever that ticket was used as the next source.

Those gaps were not evidence acceptance by themselves, but they were wasteful and
risky because an operator could see a hash-bearing record and assume the whole
source snapshot had been revalidated.

## Correction made

`tools/ft0181_field_guards.py` now compares the stored snapshot hash to the
current SHA-256 of the referenced source file at the post-decision ticket and
live-window handoff points. The validators now include stale-hash regressions:

a stale decision hash blocks post-decision ticket integrity, and a stale ticket
hash blocks live-window card integrity.

## What was intentionally not added

No new registry, schema, queue item, or doctrine family was added. The practical
change is smaller and more valuable: source snapshot hash fields now have teeth
at the handoff where they matter.

## Next useful work

The next useful pass should keep reducing operator friction around the real owner
return path. In particular, prefer one-screen human-review handoffs, exact source
preflight checks, and tests that prove stale or copied source records cannot
advance the rail.
