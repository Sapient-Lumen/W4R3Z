# Cube deep audit rev0234

## Finding

Rev0233 solved the packet-to-decision gap, but it left a last-mile risk: after the first-packet
decision board, a maintainer could still turn a narrow board result into a broader lifecycle, public
claim, schema, validator, or closeout change. That is exactly the kind of drift this archive tends to
produce when the work is almost execution-ready: the control plane is strong, but the actual permitted
change is not compact enough.

The riskiest unfinished work is still not another registry. It is a real owner-reviewed `SRC2+`
packet. The best local improvement before that packet arrives is to make the post-board change small,
reversible, and hard to overstate.

## What changed

Rev0234 adds a post-decision change ticket for `FT-0181`. It is a short bridge between the
first-packet decision board and any concrete change. The ticket names:

- exact allowed changes;
- prohibited changes;
- source truth required;
- public claim ceiling;
- rollback owner;
- rollback triggers;
- closure boundary.

The ticket is deliberately not a new governance family. It is an overreach brake. If it grows, the
extra material belongs back in the owner packet workbench, first-packet decision board, decision-delta
log, lifecycle decision, or closeout board.

## Audit/refactor

The targeted refactor is the lifecycle decision record. Before rev0234, the lifecycle example could
say `sandbox`, `pilot`, `watch`, or `deprecate`, but it did not require a concrete change ticket. That
made rollback and public-claim ceilings too easy to leave implicit.

Rev0234 extends `schemas/service-lifecycle-decision.schema.json` and
`tools/check_service_lifecycle_decisions.py` so lifecycle decisions now carry a board reference and a
post-decision change ticket. The current hint-tutor lifecycle row remains `sandbox` and
`blocked_no_real_packet`; it is more executable, but not more evidentiary.

## Severity

This was a medium-to-high execution risk. It would not necessarily break lint, but it could let a
future session do the wrong thing with clean tooling: promote, publish, or expand schema from a narrow
packet signal. That would be worse than a missing validator because it would look like forward motion.

## Waste corrected

The waste corrected here is not file count. It is decision ambiguity. A board result now has to pass
through one compact change ticket before service/public/lifecycle/schema changes. That reduces the
chance that the archive spends another session expanding controls instead of making a bounded,
reversible first change when real evidence appears.

## Remaining risk

`FT-0181` remains live. No real `SRC2+` packet has been imported. The new ticket can block overreach,
but it cannot substitute for source evidence, owner review, reviewer calibration, public rendering,
signoff, or closeout.

## Next best move

Acquire or simulate with a real owner the minimum first packet for `AIEDU-SR-004`, or fall back to
`AIEDU-SR-003` if the hint-tutor packet cannot stay aggregate-only. Then complete the owner packet
workbench, first-packet decision board, post-decision change ticket, decision-delta log, acceptance,
public rendering, lifecycle decision, closeout, quorum, and closure checklist in that order.
