# Drift-resilient autonomy versus public-auditability-closure gate

Purpose: split the archive's **witness-package progress** one step further.
A candidate should not earn the same witness credit merely because it can **keep a control loop live through drift, recalibration, relocation, and long-horizon use without stop-the-world interruption or continuous expert babysitting** and because it can **make the reasons for each intervention, threshold crossing, policy choice, and failure boundary public enough for outside audit, replay, and contest**.
Those are related, but they are not the same achievement.

Read this together with:
- `docs/40-model/empirical-contact-burden-router.md`
- `docs/40-model/witness-closure-gate-family-frame.md`
- `docs/40-model/intervention-grade-control-vs-drift-resilient-autonomy-closure-gate.md`
- `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`
- `docs/40-model/completion-bid-cashout-sieve.md`

## Compression verdict

Inside the archive's witness package, once a lane has already moved beyond intervention-grade control and drift-resilient autonomy, the current score should now distinguish three nested layers:

1. **drift-resilient autonomy closure** — the same control loop stays live through drift, recalibration, relocation, decoder retuning, or maintenance events across long runtimes without stop-the-world interruption or one silently inherited expert maintenance ecology;
2. **public auditability closure** — outsiders can reconstruct why a particular intervention, escalation, remapping, or refusal happened under the policy, thresholds, state snapshot, and action lineage that existed at decision time, rather than merely being told that the loop behaved correctly;
3. **local public witness closure** — a lane can say where the physical records live, what stabilizes them, how they are reread, why they remain public evidence, and why that empirical loop is not mainly outsourced.

A lane may earn real credit on layer 1 while still being weak on layer 2.
That is progress.
It is just not yet public auditability closure, much less full witness closure.

## Why this gate exists

Shared witness-gate scaffolding now lives in `docs/40-model/witness-closure-gate-family-frame.md`. This document only names the pair-specific inflation move below.

**self-maintaining control being retold as if the reasons, thresholds, and failure boundaries behind that control were already public enough for outside audit and contest.**

That inflation can happen in at least five ways:
- a control loop can remain live for hours or days while the decision logic that triggered interventions is visible only in private dashboards or tacit operator lore;
- an autonomous maintenance system can expose execution events but not the policy version, threshold table, or state digest that authorized those events;
- a lane can advertise replayable outcomes while the exact decision context at intervention time is lost, overwritten, or reconstructed only after the fact;
- a public benchmark or dashboard can summarize results while hiding the raw provenance path needed to trace a disputed point back to configuration choices, metadata, and device state;
- or a lane can release action logs without a cheap route for outsiders to ask which claim, alert, or branch decision each artifact is supposed to support.

## The five-step public-auditability test

### 1. Decision artifact over effect log

Before awarding auditability credit, the archive should ask whether the primary provenance unit is a **decision record** or merely a downstream execution log.
At minimum, a lane should disclose:
- what action or intervention unit is being authorized,
- what counts as the prior decision artifact that licensed it,
- whether execution without such a prior artifact is rejected,
- and which parts of the loop still infer intent from side effects after the fact.

A lane that wins only here earns **drift-resilient autonomy credit**, not yet public auditability closure.

### 2. Frozen evaluation context

A lane earns more than autonomy credit only when it can say which context was bound at decision time.
At minimum, the archive should ask:
- which policy set, threshold table, calibration version, or decision rule was active,
- what state snapshot, digest, or sufficient context summary was frozen when the decision was made,
- how context drift or later hot-fixes are kept from silently rewriting the historical rationale,
- and which decision-relevant variables still remain private, tacit, or unlogged.

Without that route, apparent auditability may still be a trustworthy operator story rather than public evidence.

### 3. Action-lineage and replay path

A lane earns stronger auditability credit only when it can link each execution-capable action back to the prior decision artifact and replay that relation.
At minimum, the archive should ask:
- how actions, branch points, remappings, refusals, or escalations are keyed to the decision record that authorized them,
- whether the linkage is append-only, immutable, or otherwise tamper-evident enough for later dispute,
- what portion of the loop can be replayed, re-simulated, or re-audited without privileged internal access,
- and where replay still fails because one-off hot patches, hidden prompts, or non-exported context intervene.

Without those answers, apparent auditability may still be execution history without decision lineage.

### 4. Public export and audit effort

A lane earns still stronger auditability credit only when outsiders can actually follow the provenance path without prohibitive reconstruction cost.
At minimum, the archive should ask:
- whether raw artifacts, metadata, configuration choices, and device / stack identifiers are exported through a public or inspectable path,
- whether claims, alerts, or summary surfaces point back to the exact supporting artifacts rather than a general log reservoir,
- how much labor is required for an outsider to verify one disputed intervention or branch decision,
- and whether contradictions, anomalies, or missing evidence are surfaced rather than silently normalized away.

Without that export path, apparent auditability may still be an internal compliance story rather than public contestability.

### 5. Closure boundary

A lane earns **public auditability closure** credit only when it can say how long-run autonomous control remains contestable as evidence rather than merely trustable as performance.
At minimum, it should name:
- the action or intervention unit,
- the prior decision artifact,
- the frozen policy / threshold / state context,
- the action-lineage and replay route,
- the public export path and approximate audit effort,
- and the remaining debt to full local record-carrier, rereadability, and objectivity closure.

This is still not the same thing as full local witness closure.
A lane may be highly auditable while still borrowing the public record carrier, rereadability, or objectivity side from ordinary laboratory witness structure.

## Common failure modes

1. **execution-only logging** — the system records what happened but not why it was allowed.
2. **threshold opacity** — decisions depend on private trigger tables, hidden prompts, or tacit escalation rules.
3. **dashboard laundering** — polished summary views stand in for exportable decision provenance.
4. **irreplayable hot-fix debt** — the loop works, but disputed actions cannot be reconstructed under the original context.
5. **audit-cost laundering** — provenance exists in principle, but only insiders can afford to use it.
6. **auditability-to-closure inflation** — public auditability is retold as if local public witness closure were therefore solved too.

## Compact current readout

- **Recent decision-centric agent-control work** makes the stronger burden explicit by arguing that execution logs alone do not answer why an action was permitted, deferred, or denied, and by elevating authorization decisions plus frozen evaluation context into replayable provenance artifacts.
- **Recent reproducibility-constrained scientific workflow work** shows what partial payment looks like when actions are treated as structured immutable units with deterministic execution, persisted outputs, and replayable branching rather than opaque free-form tool use.
- **Recent public benchmarking platform work in quantum computing** sharpens the public-contestability requirement by separating schema-validated datasets from display surfaces and by insisting on a traceable path from public plots back to raw data, configuration choices, and device metadata rather than summary rhetoric alone.

That does not refute current observer-relative or bridge-theory programs.
It just means they have not yet paid this stronger auditability debt.

## Net rule

Within the archive:
- drift-resilient autonomy closure earns real witness-package credit;
- but it does **not** yet count as public auditability closure;
- and neither of those automatically counts as local public witness closure.

Any future completion bid or bridge-family claim that wants stronger witness credit should now say not only how the same evidential state remains controlled through drift and maintenance, but how the intervention rationale, thresholds, state context, action lineage, and replay path become public enough for outside audit and contest.
