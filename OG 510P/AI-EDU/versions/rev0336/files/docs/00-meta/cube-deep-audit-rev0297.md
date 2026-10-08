# rev0297 cube deep audit

## Highest-risk incomplete seam

The cube had already compressed first contact, post-send clocking, returned-reply
intake, first workbench-review handoff, and first-packet decision-board handoff.
The next brittle seam was the post-decision change ticket. It is the point where
a useful board decision can be laundered into active change, service-record
mutation, public language, or live-window work before real SRC2+ acceptance.

## Change made

`rev0297` adds `tools/prepare_ft0181_post_decision_change_ticket_brief.py` and
`make owner-post-decision-change-ticket-brief`. The helper validates only a
scratch-local first-packet decision and emits a minimized ticket brief plus
bounded ticket command skeletons.

The field router now routes a valid first-packet decision to
`PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF`. If a valid change-ticket brief
exists, it routes to `owner-post-decision-change-ticket` and states that the
brief is not the ticket.

`make owner-field-work` can execute this safe bridge-prep step automatically,
then reruns the router and stops at the human ticket-choice boundary.

## Audit/refactor

The refactor keeps the existing activation firebreak intact. The brief contains
an active-change command template only as a boundary marker, and that template
requires a valid activation receipt. The normal router path remains
pre-activation readiness, not active change.

## What did not change

No real owner was contacted. No real CSV was accepted as evidence. No SRC2+
packet was imported or accepted. No public claim was upgraded. No lifecycle move,
activation, service-record edit, live-window action, or closure was recorded.
`FT-0181` remains live.
