# 06 — ADCC Governance (v0.19)

ADCC provides modes, voting, leases, canonicalization, CE lifecycle.

## Modes (operator + MetaLLM controllable)
1. Recorder: capture and salvage only; minimal enforcement
2. Gatekeeper: strict WS promotion + patch summaries; soft leases
3. PatchOnly: canonical workspace is read-only unless via patches
4. Freeze: no canonical changes; analysis/proposals only
5. Jailer: hard leases + strict formatting; violations lose influence

## Strictness ladder (S0–S3)
- S0: tolerate messy outputs; salvage header if possible
- S1: require patch summaries for canonical changes; soft leases advised
- S2: lease compliance required; header repair allowed; compact aggressively
- S3: hard enforcement; non-compliant slices are ignored for WS

## Voting (top-K sparse)
Voting guides scarcity allocation: attention, floor, ownership, acceptance.
- QV/STAR-style budgets are enforced by router math, not text length.

## Canonicalization
- No direct canonical changes in PatchOnly/Freeze.
- In Gatekeeper/Jailer: canonical changes require P# with patch summary/diff.
- Human can override selection, but router logs it explicitly.

## Counterexample (CE) lifecycle
- Nominate: create CE# (must include witness+repro+expected signal)
- Admit: vote to spend budget on certification attempt
- Certify: run verifier/repro; create E#; mark CE certified if expected signal observed
- After certification: claims contradicted are tagged “Contradicted,” but can be kept via expensive override votes.

## Dispute micro-phase (bandwidth-safe)
When a dispute blocks progress:
- 1 slice: CE proposer or tester provides minimal repro/test plan
- 1 slice: skeptic tries to break repro or propose alternative
- Optional: run verifier and emit E#
No long debates.

## Integrator arbitration
- Prefer selecting a single integrator (via floor vote) to merge/apply canonical changes.
- See: 37_integrator_arbitration_and_conflict_resolution.md

## Directed requests
- Allow REQ# tickets, not freeform DMs; cap inbound REQs to prevent backchannel drift.
- See: 38_req_ticketing_and_dm_policy.md

System evolution: prefer CFG# plugin/config proposals over kernel rewrite (64_config_proposal_protocol_plugins_not_kernel.md).
