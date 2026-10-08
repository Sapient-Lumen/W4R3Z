# 24 — Blackboard + Contract Net Mapping (Non-normative) (v0.19)

This system resembles:
- Blackboard: WS is the blackboard; AAR is a control shell scheduling attention.
- Contract Net: compact bid/award can allocate tasks/ownership under jitter.

## One-turn contract-net variant (slice-safe)
- Agents place bids in @VOTE:
  - floor{A2=5} lease{src/parser.py->A2=4} checks{pytest_fast=3}
- Router awards:
  - assigns lease + gives floor
  - posts awarded tasks in WS
No multi-round negotiation required.
