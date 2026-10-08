# rev0299 cube deep audit

## Highest-risk incomplete seam

The cube had already compressed first contact, post-send clocking,
returned-reply intake, first workbench-review handoff, first-packet
decision-board handoff, and first activation/live-window handoff. The next brittle
seam was the transition from a post-decision ticket into activation/live-window
work.

The dangerous failure is subtle: a `ready_for_real_packet` ticket can look like
permission to activate, and an `active_change` ticket can look like a live window
has already started. Both are wrong unless the next bounded human-owned record is
created from the right source artifact.

## Change made

`rev0299` adds `tools/prepare_ft0181_activation_live_window_brief.py` and
`make owner-activation-live-window-brief`. The helper validates only a
scratch-local post-decision ticket in `ready_for_real_packet` or `active_change`
state, then emits a minimized handoff.

The field router now routes both ready and active tickets to
`PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF`. If a valid ready brief exists, it routes
to `owner-activation-receipt` and keeps the same-source packet placeholder
visible. If a valid active brief exists, it routes to a bounded
`owner-live-window-card` command.

`make owner-field-work` can execute this safe bridge-prep step automatically,
then reruns the router and stops at the human activation/live-window boundary.

## Audit/refactor

The refactor removes one command-heavy late-field jump without opening a new
evidence path. The brief itself is scratch-local, `NOT_ACCEPTED`, `not_evidence`,
and records no activation receipt, active-change ticket, live-window card,
service-record edit, public language, lifecycle movement, custody, or closure.

## What did not change

No real owner was contacted. No real CSV was accepted as evidence. No SRC2+
packet was imported or accepted. No terminal live-window card was
recorded by the brief. No public claim was upgraded. No lifecycle move,
service-record edit, live-window action, or closure was recorded. `FT-0181`
remains live.
