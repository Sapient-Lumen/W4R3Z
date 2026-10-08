# 37 — Integrator Arbitration + Conflict Resolution (v0.19)

The cheapest way to prevent engineering thrash is: **pick one integrator** and let them arbitrate.

This is not about truth. It’s about forward progress under jitter.

## 1) Integrator role
An integrator is the only actor allowed to:
- merge competing patch proposals
- apply the selected patch to canonical workspace (unless human overrides)
- decide the minimal shape of the next “working set”

## 2) Selecting the integrator (default)
- Integrator is the agent with the highest `floor{A#=...}` vote.
- If no floor votes: MetaLLM suggests one (or human picks).
- Integrator should take leases on the hot file/component scope (soft by default).

## 3) Arbitration rule (deterministic)
When two patch proposals conflict:
1. Prefer the patch that:
   - touches fewer files (smaller blast radius)
   - has clearer verify intent
   - has supporting evidence already (E#)
2. If still unclear:
   - run a cheap discriminative verifier (unit_fast/typecheck_fast)
3. If still unclear:
   - accept the smaller patch first; defer the other as “follow-up patch”

## 4) Merge policy
- If patches are compatible: integrator merges into a new P# (P_merge#) with a combined diff ref.
- If incompatible: loser becomes a “parked patch” (status: superseded but preserved).

## 5) Appeals (bounded)
Any agent can file an appeal:
- create REQ# to integrator with a discriminative check suggestion
- or propose a certifiable CE refuting the chosen path
Appeals are bounded to avoid endless court cases.

## 6) Human overrides
Human can override integrator decisions:
- router logs the override explicitly in mandatory deltas
- a SUM# should capture why

## 7) Why this works in your setting
Unknown slice counts punish multi-round consensus.
Integrator arbitration compresses multi-agent coordination into:
- diverge (parallel proposals)
- select (one vote)
- integrate (one actor)
- verify (cheap checks)
