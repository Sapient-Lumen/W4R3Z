# 55 — Consensus Collapse + Drift Detection (v0.19)

Your concern: agents converge too easily, even when wrong.
We treat “agreement without evidence” as a measurable failure mode.

## 1) Signals of consensus collapse
- high agreement votes with low evidence density
- repeated “looks good” / “agree” language in ledger
- few or zero E# events per cursor window
- no counterexamples proposed even when uncertainty is high
- selected patch changes frequently without verifier runs

## 2) Drift vs collapse
- Collapse: “everyone agrees” too early.
- Drift: agents start optimizing different goals (views diverge, REQ spam, incompatible patches).

## 3) Mitigations (bounded)
### Collapse mitigations
- require at least one cheap verifier before selecting a patch (Gatekeeper mode)
- turn on DISCOVERY exploration (and optionally RANDOM) for a few cycles
- force “disagreement introductions”:
  - each agent must provide 1 risk/objection line
  - or propose 1 discriminative check / CE attempt

### Drift mitigations
- tighten ROLE subscriptions (menu-based)
- reduce REQ inflow caps temporarily
- switch to PatchOnly mode with a single integrator
- force compaction and re-pin H0

## 4) MetaLLM policy
MetaLLM watches:
- evidence density
- vote variance
- truncation/parse failures
Then chooses one mitigation at a time.

Use disagreement introductions and objection budgets to fight collapse (66_disagreement_introductions_and_objection_budget.md).

Objection discipline + prompt pack: see 66_disagreement_introductions_and_objection_budget.md and 68_prompt_pack_agent_and_metallm.md.
