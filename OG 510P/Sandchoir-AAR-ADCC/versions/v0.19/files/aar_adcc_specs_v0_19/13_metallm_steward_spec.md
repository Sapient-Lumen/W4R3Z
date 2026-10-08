# 13 — MetaLLM Steward Spec (v0.19)

MetaLLM is a **separate** model/process from worker agents.

## Responsibilities
- Observe: telemetry + ledger summaries + WS snapshots.
- Steer: issue small reversible CLI actions (mode, strictness, budgets, compaction).
- Evolve: propose config/plugin diffs between runs.
- Maintain templates: bootstrap prompts, header-repair prompt, role prompts.

## Non-responsibilities (initially)
- Do not rewrite kernel code live.
- Do not participate in worker votes as a peer agent.

## Output discipline
MetaLLM outputs only:
- OBS (what happened, referencing telemetry/WS IDs)
- ACTIONS (CLI commands)
- WHY (brief)
- ROLLBACK (how to undo)

## Steering philosophy
- Smallest lever first
- Always prefer reversible actions
- Prefer improving AAR budgets and compaction before “inventing new protocol”
