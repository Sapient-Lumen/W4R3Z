# Post-decision change-ticket gate audit rev0277

Rev0277 targets the next completion risk after the first-packet decision board. A valid `first-packet-decision.json` still routed the operator into a prose-only post-decision change ticket. That was risky because the first real owner packet could move from a bounded decision record into service-record edits, public-summary changes, lifecycle motion, or live-window preparation without a machine-checkable change boundary.

## Concrete change

Rev0277 adds a local post-decision change-ticket recorder:

- `tools/record_ft0181_post_decision_change_ticket.py` writes `post-decision-change-ticket.json` and `POST-DECISION-CHANGE-TICKET-SUMMARY.md` under `scratch/` or an external local path only.
- `tools/check_ft0181_post_decision_change_ticket.py` validates the new gate.
- `tools/ft0181_field_guards.py` now exposes `owner_post_decision_change_ticket_integrity_error(...)` so the router and validator share one boundary.
- `tools/decide_ft0181_field_next_action.py` now routes a valid first-packet decision to `make owner-post-decision-change-ticket ...`, not to prose-only ticket work.
- `Makefile` now has `owner-post-decision-change-ticket` as the bounded next target.

## What the gate records

The artifact records only:

1. ticket state;
2. change class;
3. source truth required before activation;
4. public claim ceiling class;
5. allowed-change, prohibited-change, rollback-trigger, and rollback-owner counts;
6. live-window requirement flag; and
7. source decision reference/hash and revalidation status.

It copies no owner answers, raw CSV rows, first-packet decision prose, contact details, learner data, protected facts, small cells, screenshots, credentials, security payloads, or public claim language.

## What the gate blocks

The new gate blocks:

- non-scratch or missing first-packet decision sources;
- edited decisions that claim acceptance, custody, closure, or stronger evidence;
- ready/active tickets without allowed change counts;
- missing prohibited-change, rollback-trigger, or rollback-owner counts;
- active changes without a required live-window stop/rollback card;
- bounded-pilot changes without `SRC2`/`SRC3`/`SRC4` source truth requirement and a live-window card;
- quarantine class with a non-quarantine/non-rollback state;
- raw learner data, protected facts, security payloads, or public-claim-upgrade flags;
- release-controlled output paths; and
- ticket records that try to become evidence, custody, acceptance, closure, service-record mutation, live-window approval, or public-summary support.

## Audit/refactor finding

The live field path is now less prose-dependent:

`workbench-review.json` → `first-packet-decision.json` → `post-decision-change-ticket.json` → live-window stop/rollback card.

This replaces the weaker route where the first-packet decision opened a prose ticket and trusted the operator not to overreach. The change is deliberately not a new governance family. It is a small executable gate in the existing `FT-0181` path.

## Remaining risk

The next bottleneck is the live-window stop/rollback card. A post-decision ticket can name what may change and what must not change, but it still cannot authorize live operation, service-record mutation, lifecycle promotion, public-summary changes, custody, acceptance, or closure. The next execution pass should turn the live-window card into a local artifact before any active use or window readout can be claimed.
