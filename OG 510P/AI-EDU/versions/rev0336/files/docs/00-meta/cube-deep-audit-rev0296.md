# rev0296 cube deep audit

## Highest-risk incomplete seam

The cube had already compressed first contact, post-send clocking, returned-reply
intake, and the first workbench-review handoff. The next brittle seam was the
five-slice first-packet decision board: it was executable, but the command was
long enough that a valid human review could still stall before a bounded board
record existed.

## Change made

`rev0296` adds `tools/prepare_ft0181_first_packet_decision_brief.py` and
`make owner-first-packet-decision-brief`. The helper validates only a scratch-local
`PROCEED-DECISION-BOARD` workbench review and emits a minimized board brief plus
bounded decision command skeletons.

The field router now routes a proceed review to `PREPARE-FIRST-PACKET-DECISION-BRIEF`.
If a valid decision brief exists, it routes to `owner-first-packet-decision` and
states that the brief is not the board decision.

`make owner-field-work` can execute this safe bridge-prep step automatically,
then reruns the router and stops at the human board-choice boundary.

## Audit/refactor

A stale summary label in `record_ft0181_post_decision_change_ticket.py` called the
post-decision ticket a live-window card. `rev0296` corrects that label to prevent
source-truth laundering from a readiness ticket into live-window authority.

## What did not change

No real owner was contacted. No real CSV was accepted as evidence. No SRC2+
packet was imported or accepted. No public claim was upgraded. No lifecycle move,
activation, service-record edit, live-window action, or closure was recorded.
`FT-0181` remains live.
