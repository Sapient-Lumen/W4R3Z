# Cooperation benchmarks should publish intervention rights, delegation policy, and final-action authority

Two human-AI benchmark lanes can use the same task, partner pool, and score metric while still measuring materially different institutions.
If one lane treats the model as an **advisor**, another as a **delegate**, and another as a **co-actor with interruptible control**, then the resulting cooperation or task-success numbers are not directly comparable.
Two recent sources make the compact archive rule clear:

- `RS-GR-065` introduces HAI-Eval and explicitly benchmarks human-AI performance under **four levels of human intervention**, showing that collaboration conclusions shift with the intervention regime rather than with model quality alone.
- `RS-GR-066` studies **conditional delegation** as a distinct collaboration paradigm in which humans specify trusted regions for model action, showing that delegation policy itself can improve performance under distribution shift.

## Minimum contract

Whenever a cooperation benchmark includes both humans and AI, publish:

1. who has **final action authority** on each step or each episode;
2. whether the AI is acting as **advisor, delegate, co-actor, or autonomous actor with human escalation**;
3. what **override / interrupt / approve / abstain / escalate** rights each side has;
4. whether intervention is **continuous, bounded, batched, or only available at designated checkpoints**;
5. and whether headline results are pooled across multiple authority regimes or reported lane-by-lane.

## Implementor consequence

Do not compare or pool benchmark results across human-AI lanes unless their control split is actually aligned.
A system can look more cooperative or more capable simply because the human kept veto power, because the AI was allowed to act first, or because delegation only happened inside predeclared trust regions.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: intervention regime, delegation policy, final-action authority, and override / escalation rights.
That prevents future sessions from laundering an interface-control choice into a policy-quality claim.
