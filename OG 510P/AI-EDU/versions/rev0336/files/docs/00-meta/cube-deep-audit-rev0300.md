# rev0300 cube deep audit

## Highest-risk incomplete seam

The cube had already compressed first contact, post-send clocking,
returned-reply intake, workbench review, first-packet decision, post-decision
ticketing, activation/live-window entry, and nonterminal-to-terminal live-window
handoff. The next brittle seam was the transition from a terminal live-window
card into a terminal aggregate readout.

The dangerous failure is subtle: a terminal card can look like the work is done,
or it can invite a jump straight to post-readout action, service-record edit,
public language, or closure. All of those are wrong unless the next bounded
human-owned record is the aggregate readout itself.

## Change made

`rev0300` adds `tools/prepare_ft0181_live_window_readout_brief.py` and
`make owner-live-window-readout-brief`. The helper validates only a scratch-local
terminal live-window card in `paused`, `rolled_back`, `completed_no_closure`, or
`quarantined` state, then emits a minimized handoff.

The field router now routes terminal cards to
`PREPARE-LIVE-WINDOW-READOUT-BRIEF`. If a valid readout brief exists, it routes
to the bounded `owner-live-window-readout` command from the brief.

`make owner-field-work` can execute this safe bridge-prep step automatically,
then reruns the router and stops at the human aggregate-readout boundary.

## Audit/refactor

This refactor removes one command-heavy late-field jump without opening a new
evidence path. The brief itself is scratch-local, `NOT_ACCEPTED`, `not_evidence`,
and records no readout, post-readout action, service-record edit, public
language, lifecycle movement, custody, acceptance, or closure.

It also corrects the live rail’s substance-to-bureaucracy balance: no new schema
family or registry family was added. The only added registry work is coverage for
one new executable bridge and its validator.

## What did not change

No real owner was contacted. No real CSV was accepted as evidence. No SRC2+
packet was imported or accepted. No terminal live-window readout was recorded by
the brief. No public claim was upgraded. No lifecycle move, service-record edit,
post-readout action, or closure was recorded. `FT-0181` remains live.
