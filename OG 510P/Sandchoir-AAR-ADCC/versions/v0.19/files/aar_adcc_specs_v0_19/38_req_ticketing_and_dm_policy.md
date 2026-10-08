# 38 — REQ# Ticketing + “DM” Policy (v0.19)

You asked: can agents DM each other? Yes — but if you let it become an unstructured backchannel, you lose coherence.

Solution: all directed requests are **REQ# tickets** with strict caps.

## 1) What REQ# is (and isn’t)
REQ# is a tiny, typed request object.
It is not a freeform chat channel.

## 2) Allowed REQ# types (starter set)
- `review` (inspect patch P#)
- `test` (run verifier / certify CE)
- `falsify` (try to find counterexample)
- `clarify` (ask for 1 missing field needed to proceed)
- `implement` (draft a patch proposal)
- `summarize` (produce a SUM#)

## 3) Inbound caps (anti-spam)
Per agent:
- max open inbound REQs: 3
- REQ TTL: next “round” by default (or expires at cursor+N)
Expired REQs auto-close with status “expired”.

## 4) Required fields
REQ# must include:
- `from`, `to`, `type`, `targets`, `deliverable`, `deadline`, `priority(1–3)`
Anything else is ledger-only prose.

## 5) Replies
Replies should be:
- a single WS object (P#, E#, CE#, SUM#) OR
- `@CTRL DONE=yes` with “no further thoughts”
Router links reply → REQ# and closes it.

## 6) Promotion rules
REQs are shown:
- in recipient’s ROLE area
- in mandatory deltas if they touch selected patch or certified CE

## 7) “Give each other the floor”
Agents can request floor delegation via REQ:
- `REQ# type=clarify deliverable="Please take integrator for scope X"`
But the system authority is still the floor/lease votes and MetaLLM/human.
