# First-packet decision gate audit rev0276

Rev0276 targets the next completion risk after the rev0276 workbench-review gate. A proceed-capable `workbench-review.json` still routed the operator into a prose decision board. That was risky because the first real owner packet could be interpreted, summarized, or acted on before the five decision slices were captured in a minimized local artifact.

## Concrete change

Rev0276 adds a local first-packet decision-board recorder:

- `tools/record_ft0181_first_packet_decision.py` writes `first-packet-decision.json` and `FIRST-PACKET-DECISION-SUMMARY.md` under `scratch/` or an external local path only.
- `tools/check_ft0181_first_packet_decision.py` validates the new gate.
- `tools/ft0181_field_guards.py` now exposes `owner_first_packet_decision_integrity_error(...)` so the router and validator share one boundary.
- `tools/decide_ft0181_field_next_action.py` now routes a valid `PROCEED-DECISION-BOARD` review to `make owner-first-packet-decision ...`, not to prose-only board work.
- `Makefile` now has `owner-first-packet-decision` as the bounded next target.

## What the gate records

The artifact records only five slice classes:

1. authority;
2. evidence;
3. construct/proof;
4. public-summary posture;
5. lifecycle posture.

It also records a changed-slice count, rollback owner role count, source review hash, source truth class, route labels, and the post-decision change-ticket surface. It copies no owner answers, raw CSV rows, workbench-review prose, contact details, learner data, protected facts, small cells, screenshots, credentials, or public claim text.

## What the gate blocks

The new gate blocks:

- non-scratch or non-proceed workbench-review sources;
- edited reviews that claim acceptance, custody, closure, or stronger evidence;
- all-no-change boards after a proceed-capable review;
- changed-slice-count mismatches;
- missing rollback owner role count;
- raw learner data, protected facts, security payloads, or public-claim-upgrade flags;
- release-controlled output paths; and
- board records that try to become evidence, custody, acceptance, closure, live-window approval, or public-summary support.

## Audit/refactor finding

While wiring the new gate, the `check_ft0181_field_next_action.py` copied-stale-status test exposed a flaky fixture: a simulated copied stale `SENT_AWAITING_REPLY` status could receive a fresh `created_at_utc` timestamp. The test now explicitly preserves the historical manifest clock, so the router is being tested against the intended risk: filesystem copy freshness must not outrank the manifest-clock terminal `NO_OWNER_PACKET` state.

## Remaining risk

The next bottleneck is the post-decision change ticket. A valid first-packet decision record can say what changed, but it still cannot authorize service-record edits, public-summary edits, custody, live-window operation, or closure. The next execution pass should turn the post-decision change ticket into a minimized local artifact with rollback owner, prohibited changes, public-claim ceiling, and live-window boundary.
