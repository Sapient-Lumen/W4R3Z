# Lacuna documentation

## Begin here

1. [`../PLAY_NOW.md`](../PLAY_NOW.md) — player-only entrance: say “Will you DM?” and begin.
2. [`../FOR_GWERN.md`](../FOR_GWERN.md) — concise gift claim, nonclaims, and experiment smoke path.
3. [`../OPERATE_LACUNA.md`](../OPERATE_LACUNA.md) — shortest capability-first operator entrance.
4. [`operators/ONE_SENTENCE_START.md`](operators/ONE_SENTENCE_START.md) — the complete “Will you DM?” governed-play procedure.
5. [`../PLAY_WITH_AN_LLM.md`](../PLAY_WITH_AN_LLM.md) — player/model entrance and capability table.
6. [`operators/FRESH_NARRATOR.md`](operators/FRESH_NARRATOR.md) — exact post-checkpoint turn handoff and context reset.
7. [`operators/PUBLIC_HISTORY.md`](operators/PUBLIC_HISTORY.md) — explicit partial prose custody or checkpoint-bound complete durable-turn census.
8. [`design/THREE_SERIOUS_QUESTIONS.md`](design/THREE_SERIOUS_QUESTIONS.md) — gift value, ChatGPT playability, and provider/subagent design.
9. [`design/GWERN_GIFT_TEST.md`](design/GWERN_GIFT_TEST.md) — what Lacuna answers in retcon planning and how to evaluate it.
10. [`NORTHSTAR.md`](NORTHSTAR.md) — governing doctrine and nonclaims.
11. [`operators/MODEL_ENTRANCE.md`](operators/MODEL_ENTRANCE.md) — intent routing and capability profiles.
12. [`operators/TURN_RUNS.md`](operators/TURN_RUNS.md) — request-scoped resumable state machine, dispatch, recovery, and exact commit.
13. [`operators/CHATGPT.md`](operators/CHATGPT.md) — ordinary chat, Project/custom GPT, human bridge, role, and connected-host paths.
14. [`operators/MULTI_AGENT.md`](operators/MULTI_AGENT.md) — least-context role separation and parent-only authority.
15. [`operators/CHECKPOINT_RUNS.md`](operators/CHECKPOINT_RUNS.md) — managed generator/judge/compressor/verifier walk plus fresh source-bound continuation.
16. [`operators/SCENARIO_CAPSULES.md`](operators/SCENARIO_CAPSULES.md) — exact single-block four-condition comparison and blind ratings.
17. [`operators/CONTAMINATION_CANARIES.md`](operators/CONTAMINATION_CANARIES.md) — preregistered operator/filesystem canaries and complete pre-rating retained-tree scan.
18. [`operators/SCENARIO_BUNDLES.md`](operators/SCENARIO_BUNDLES.md) — preregistered replicated blocks, witness gate, scan-bound seals, seal-all-before-unblind, and exports.
19. [`operators/CHECKPOINTS.md`](operators/CHECKPOINTS.md) — lower-level stateless checkpoint exchange for custom hosts.
20. [`architecture/ARCHITECTURE_rev0169.md`](architecture/ARCHITECTURE_rev0169.md) — current test-harness, license, and template-gate polish architecture.
21. [`protocols/TURN_CONTRACT.md`](protocols/TURN_CONTRACT.md) — typed source-bound input and atomic proposals.
22. [`protocols/CONTEXT_ACCESS.md`](protocols/CONTEXT_ACCESS.md) — audience/planner structural separation.
23. [`protocols/INTERACTION_SURFACES.md`](protocols/INTERACTION_SURFACES.md) — human CLI, model, Python, and host boundaries.

## Model and host operation

- [`operators/README.md`](operators/README.md)
- [`operators/PROVIDER_CONFIGS.md`](operators/PROVIDER_CONFIGS.md)
- [`../integrations/chatgpt/README.md`](../integrations/chatgpt/README.md)
- [`../schemas/play-start.v1.schema.json`](../schemas/play-start.v1.schema.json)
- [`../schemas/agent-dispatch.v1.schema.json`](../schemas/agent-dispatch.v1.schema.json)
- [`../schemas/model-brief.v1.schema.json`](../schemas/model-brief.v1.schema.json)
- [`../schemas/turn-request.v3.schema.json`](../schemas/turn-request.v3.schema.json)
- [`../schemas/turn-request.v4.schema.json`](../schemas/turn-request.v4.schema.json)
- [`../schemas/checkpoint-request.v1.schema.json`](../schemas/checkpoint-request.v1.schema.json)
- [`../schemas/checkpoint-task-card.v1.schema.json`](../schemas/checkpoint-task-card.v1.schema.json)
- [`../schemas/checkpoint-candidates.v1.schema.json`](../schemas/checkpoint-candidates.v1.schema.json)
- [`../schemas/checkpoint-judgment.v1.schema.json`](../schemas/checkpoint-judgment.v1.schema.json)
- [`../schemas/checkpoint-compression.v1.schema.json`](../schemas/checkpoint-compression.v1.schema.json)
- [`../schemas/checkpoint-proposal.v1.schema.json`](../schemas/checkpoint-proposal.v1.schema.json)
- [`../schemas/checkpoint-verifier-return.v1.schema.json`](../schemas/checkpoint-verifier-return.v1.schema.json)
- [`../schemas/checkpoint-review.v1.schema.json`](../schemas/checkpoint-review.v1.schema.json)
- [`../schemas/checkpoint-commit-receipt.v1.schema.json`](../schemas/checkpoint-commit-receipt.v1.schema.json)
- [`../schemas/checkpoint-agent-dispatch.v1.schema.json`](../schemas/checkpoint-agent-dispatch.v1.schema.json)
- [`../schemas/checkpoint-run.v1.schema.json`](../schemas/checkpoint-run.v1.schema.json)
- [`../schemas/checkpoint-run-agent-dispatch.v1.schema.json`](../schemas/checkpoint-run-agent-dispatch.v1.schema.json)
- [`../schemas/checkpoint-invocation-receipt.v1.schema.json`](../schemas/checkpoint-invocation-receipt.v1.schema.json)
- [`../schemas/checkpoint-narrator-capsule.v1.schema.json`](../schemas/checkpoint-narrator-capsule.v1.schema.json)
- [`../schemas/checkpoint-continuation-dispatch.v1.schema.json`](../schemas/checkpoint-continuation-dispatch.v1.schema.json)
- [`../schemas/checkpoint-continuation-dispatch.v2.schema.json`](../schemas/checkpoint-continuation-dispatch.v2.schema.json)
- [`../schemas/public-history.v1.schema.json`](../schemas/public-history.v1.schema.json)
- [`../schemas/public-history.v2.schema.json`](../schemas/public-history.v2.schema.json)
- [`../schemas/public-history-view.v1.schema.json`](../schemas/public-history-view.v1.schema.json)
- [`../schemas/public-history-view.v2.schema.json`](../schemas/public-history-view.v2.schema.json)
- [`../schemas/scenario-capsule.v1.schema.json`](../schemas/scenario-capsule.v1.schema.json)
- [`../schemas/scenario-run.v1.schema.json`](../schemas/scenario-run.v1.schema.json)
- [`../schemas/scenario-run.v2.schema.json`](../schemas/scenario-run.v2.schema.json)
- [`../schemas/scenario-run.v3.schema.json`](../schemas/scenario-run.v3.schema.json)
- [`../schemas/scenario-assignment.v1.schema.json`](../schemas/scenario-assignment.v1.schema.json)
- [`../schemas/scenario-cell-driver.v1.schema.json`](../schemas/scenario-cell-driver.v1.schema.json)
- [`../schemas/scenario-cell-driver.v2.schema.json`](../schemas/scenario-cell-driver.v2.schema.json)
- [`../schemas/scenario-contamination-plan.v1.schema.json`](../schemas/scenario-contamination-plan.v1.schema.json)
- [`../schemas/scenario-contamination-scan.v1.schema.json`](../schemas/scenario-contamination-scan.v1.schema.json)
- [`../schemas/scenario-cell-return.v1.schema.json`](../schemas/scenario-cell-return.v1.schema.json)
- [`../schemas/scenario-cell-receipt.v1.schema.json`](../schemas/scenario-cell-receipt.v1.schema.json)
- [`../schemas/scenario-blind-rating-packet.v1.schema.json`](../schemas/scenario-blind-rating-packet.v1.schema.json)
- [`../schemas/scenario-rating.v1.schema.json`](../schemas/scenario-rating.v1.schema.json)
- [`../schemas/scenario-masking-assessment.v1.schema.json`](../schemas/scenario-masking-assessment.v1.schema.json)
- [`../schemas/scenario-report.v1.schema.json`](../schemas/scenario-report.v1.schema.json)
- [`../schemas/scenario-report.v2.schema.json`](../schemas/scenario-report.v2.schema.json)
- [`../schemas/scenario-report.v3.schema.json`](../schemas/scenario-report.v3.schema.json)
- [`../schemas/scenario-bundle-plan.v1.schema.json`](../schemas/scenario-bundle-plan.v1.schema.json)
- [`../schemas/scenario-bundle-schedule.v1.schema.json`](../schemas/scenario-bundle-schedule.v1.schema.json)
- [`../schemas/scenario-bundle-commitment.v1.schema.json`](../schemas/scenario-bundle-commitment.v1.schema.json)
- [`../schemas/scenario-bundle.v1.schema.json`](../schemas/scenario-bundle.v1.schema.json)
- [`../schemas/scenario-bundle.v2.schema.json`](../schemas/scenario-bundle.v2.schema.json)
- [`../schemas/scenario-bundle-witness.v1.schema.json`](../schemas/scenario-bundle-witness.v1.schema.json)
- [`../schemas/scenario-bundle-block-seal.v1.schema.json`](../schemas/scenario-bundle-block-seal.v1.schema.json)
- [`../schemas/scenario-bundle-block-seal.v2.schema.json`](../schemas/scenario-bundle-block-seal.v2.schema.json)
- [`../schemas/scenario-bundle-block-seal.v3.schema.json`](../schemas/scenario-bundle-block-seal.v3.schema.json)
- [`../schemas/scenario-bundle-report.v1.schema.json`](../schemas/scenario-bundle-report.v1.schema.json)
- [`../schemas/scenario-bundle-report.v2.schema.json`](../schemas/scenario-bundle-report.v2.schema.json)
- [`../schemas/scenario-bundle-report.v3.schema.json`](../schemas/scenario-bundle-report.v3.schema.json)
- [`../schemas/turn-run.v2.schema.json`](../schemas/turn-run.v2.schema.json)
- [`../schemas/turn-preparation.v1.schema.json`](../schemas/turn-preparation.v1.schema.json)
- [`../schemas/turn-receipt.v3.schema.json`](../schemas/turn-receipt.v3.schema.json)
- [`../schemas/orchestration-plan.v1.schema.json`](../schemas/orchestration-plan.v1.schema.json)
- [`../schemas/turn-task-card.v1.schema.json`](../schemas/turn-task-card.v1.schema.json)
- [`../schemas/planner-return.v1.schema.json`](../schemas/planner-return.v1.schema.json)
- [`../schemas/narrator-return.v1.schema.json`](../schemas/narrator-return.v1.schema.json)
- [`../schemas/verifier-return.v1.schema.json`](../schemas/verifier-return.v1.schema.json)

## Stable protocols

- [`protocols/FACTOR_LEDGER_RECONCILIATION.md`](protocols/FACTOR_LEDGER_RECONCILIATION.md)
- [`protocols/PARTICLE_BANK.md`](protocols/PARTICLE_BANK.md)
- [`protocols/SCHEMA_LINEAGE.md`](protocols/SCHEMA_LINEAGE.md)
- [`protocols/COMMITMENT_GOVERNANCE.md`](protocols/COMMITMENT_GOVERNANCE.md)
- [`protocols/CONSEQUENCE_LINKS.md`](protocols/CONSEQUENCE_LINKS.md)
- [`protocols/CONSEQUENCE_REPAIR.md`](protocols/CONSEQUENCE_REPAIR.md)
- [`protocols/REVISION_IMPACT.md`](protocols/REVISION_IMPACT.md)
- [`protocols/FAIR_PLAY_SEALS.md`](protocols/FAIR_PLAY_SEALS.md)
- [`protocols/EXPLANATIONS.md`](protocols/EXPLANATIONS.md)

## Current revision records

- [`research/RESEARCH_rev0169.md`](research/RESEARCH_rev0169.md)
- [`decisions/DECISIONS_rev0169.md`](decisions/DECISIONS_rev0169.md)
- [`audits/AUDIT_rev0169.md`](audits/AUDIT_rev0169.md)
- [`audits/DIRECT_UPLOAD_FEEDBACK_AUDIT_rev0163.md`](audits/DIRECT_UPLOAD_FEEDBACK_AUDIT_rev0163.md)
- [`acceptance/ACCEPTANCE_rev0169.json`](acceptance/ACCEPTANCE_rev0169.json)

## Design, risk, and future work

- [`design/BEYOND_RETCON_PLANNING.md`](design/BEYOND_RETCON_PLANNING.md)
- [`THREAT_MODEL.md`](THREAT_MODEL.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`GLOSSARY.md`](GLOSSARY.md)

Historical revision-specific records remain in their directories as immutable project memory.
