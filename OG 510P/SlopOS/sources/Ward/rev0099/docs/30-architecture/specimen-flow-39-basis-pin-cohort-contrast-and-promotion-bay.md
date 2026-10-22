# Specimen flow 39 — basis pin, cohort contrast, and promotion bay

Goal: keep Ward honest when a useful trust exploration graduates from one-off query to repeatedly useful derivative surface.

## Scenario
A reviewer investigates whether a newly observed approval cohort looks suspiciously different from the background population.
The sequence unfolds in eight steps:
1. the reviewer starts from a concrete trust cut and saves an explicit **basis pin** `B7` rather than asking follow-up questions against ambient latest;
2. they define a selected cohort `C_sel` (for example, approvals carrying one unusual attestation profile or one policy epoch) and a background cohort `C_bg` drawn from the same pinned basis;
3. a contrast pass compares `C_sel` against `C_bg` across many high-cardinality dimensions instead of only across predeclared dashboard buckets;
4. the most interesting differences are not the obvious summary counters but a surprising issuer path, one endorsement cohort, and one policy-epoch boundary that would likely have been hidden by a premature fixed rollup;
5. the reviewer saves the exploration as a **query recipe** whose identity includes the basis pin, cohort definitions, comparison logic, and visible freshness posture;
6. other reviewers reuse the same saved recipe several times over the next week, sometimes against the original pinned basis for forensics and sometimes against a newer basis for current monitoring;
7. because the recipe keeps paying rent, the team moves it through a **promotion bay** into a maintained derivative surface with an explicit owner, refresh cadence, lineage header, and warning that it remains weaker than source evidence/appraisal;
8. downstream consumers can now use the promoted derivative for orientation, triage, and prioritization, but any spendable or irreversible consequence still traces back through the underlying evidence/appraisal path rather than treating the derivative as self-authorizing truth.

At first glance, a product might flatten this into “we found a useful chart, so make it the main dashboard.”
That would be a mistake.
A pinned basis is different from ambient latest.
A contrast surface is different from a pre-baked rollup.
A promoted derivative is different from source truth.
And a repeatedly useful query still needs explicit lineage and ownership before it becomes team-facing infrastructure.

Ward should therefore record three distinct residues rather than one vague “dashboard answer” object:
1. a **basis pin** for the exact cut/scope the exploration anchors to;
2. a **cohort contrast** surface that reveals what is unusual without requiring predeclared winning dimensions;
3. a **promotion bay** step where a saved query earns owner, freshness posture, and lineage before it becomes a maintained derivative.

## Why this matters
- Trust questions are often discovered, not predefined.
- High-cardinality differences are easy to lose if the cube decides the summary buckets too early.
- Repeatedly useful explorations deserve promotion, but promotion should stay explicit and reversible.
- Fast maintained derivatives are valuable, but they should remain visibly weaker than evidence, appraisal recipe, and consequence.
- Basis-pinned replay is essential when reviewers later disagree about whether a contrast was real or merely drift.

## Ward pressure
This specimen pressures Ward to keep basis pin, cohort contrast, and promotion bay distinct while still leaving open whether later implementation rides on one event store, one OLAP engine, one lakehouse, one streaming planner, or a thinner federated query posture.
