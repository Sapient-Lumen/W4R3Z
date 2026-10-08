# 66 — Disagreement Introductions + Objection Budget (v0.19)

To fight consensus collapse, you wanted “agreement and disagreement” from each agent.
This doc makes it cheap.

## 1) Disagreement introduction requirement
In certain modes/phases (e.g., EK bootstrap, Gatekeeper on hard sections):
Each agent must provide:
- 1 line “agree strongest point”
- 1 line “objection / risk / unknown”
- 1 line “discriminative check or CE attempt”

Total: 3 lines max.

## 2) Objection budget
To prevent infinite negativity:
- each agent has an objection budget per round (e.g., 2 objections)
- objections must be tied to a testable claim or an evidence plan
- pure style objections go to ledger and do not count

## 3) Waivers
Agents can vote to waive objection requirements when:
- evidence density is high and progress is steady
- the section is low risk

Waiver vote:
- `waive_objections{yes=...}` (sparse)
Router decides; MetaLLM can recommend.

## 4) Payoff
This yields:
- at least one “anti-story” per agent
- a path to evidence
- minimal token cost

## 5) Failure mode
Agents produce generic objections like “might be wrong.”
Mitigation:
- require objections to name a specific failure mode or a specific missing check.
