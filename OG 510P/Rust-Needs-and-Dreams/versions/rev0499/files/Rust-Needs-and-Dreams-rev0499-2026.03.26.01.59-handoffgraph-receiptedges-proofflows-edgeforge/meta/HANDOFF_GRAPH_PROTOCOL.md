# Meta: Handoff Graph Protocol

## Purpose
Use this protocol when the archive needs a compact, validated answer to:
> **what exact receipt-bearing edges should connect the strongest Rust contribution shipsets, and what stability posture does each edge rely on?**

This protocol is **not** the same as:
- reranking the broad ladder,
- naming a launch wedge,
- describing a full decision journey,
- writing a seam-local contract,
- or widening to a platform charter.

It exists for the narrower question:
> once top seams already have wedges, journeys, and first shipsets, how does the repo keep the cross-seam artifact handoffs explicit enough that future revisions do not replace them with vague “integration” language?

Read with:
- `design/epic-contribution-handoff-graph-2026Q1.md`
- `design/epic-contribution-kernel-shipset-ledger-2026Q1.md`
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `ledgers/top-band-handoff-graph-v0/handoffs.json`

## Core rule
If a revision materially changes **what artifact should move from one strong seam into another**, that revision should refresh both:
1. the relevant prose note; and
2. the machine-readable handoff card.

If the handoff answer changes but only the prose changes, treat the revision as **receipt-edge-lossy**.

## When to use this layer
Prefer the handoff graph when the user is really asking:
- how the strongest kernels should exchange facts or receipts;
- what adapter boundary should be stabilized first;
- what stable, unstable, or service truth a cross-seam flow may depend on;
- what output receipt should exist after one contribution hands off to another; or
- whether a new proposed contribution is actually a missing edge rather than a missing seam.

## When not to use this layer
Do **not** use the handoff graph to:
- promote a new worthy-contribution seam;
- pretend every seam needs a direct edge to every other seam;
- replace journey cards or kernel contracts;
- or claim that a passing check proves a handoff is strategically sufficient or semantically sound.

## Required card fields
Each card in `ledgers/top-band-handoff-graph-v0/handoffs.json` should include:
- `handoff_id`
- `title`
- `handoff_class`
- `status`
- `producer`
- `consumer`
- `primary_journeys`
- `entry_artifacts`
- `transforms`
- `output_receipts`
- `stable_surfaces`
- `unstable_or_service_boundaries`
- `refused_collapses`
- `credible_home`
- `related_assets`
- `supporting_sources`
- `review_horizon`
- `notes`

## Required posture
A good handoff card must:
1. name a real producer and consumer rather than generic “the ecosystem” language;
2. end in a reviewable receipt rather than hidden state;
3. keep stable, unstable, and service truth visibly distinct;
4. link to nearby shipset and journey assets; and
5. carry at least one refused collapse that keeps the edge from widening into platform theater.

## Structural non-claims
A passing `check_handoff_graph.py` run proves:
- the ledger parses,
- required fields exist,
- linked assets exist,
- and the required class and seam coverage are present.

It does **not** prove:
- that the edge is strategically correct,
- that the transforms are sufficient,
- that the cited upstream surfaces are semantically stable,
- or that the edge deserves implementation priority over all other work.

## Default coverage rule
At the moment the handoff graph should at least cover these edges:
- Cargo raw facts → Build-State Pack
- Build-State Pack → Debug Acceptance Matrix
- Registry/security truth → Intake Review Kit
- Structured API facts → Release-Boundary Review
- Intake + compatibility receipts → Safety Readiness Cards
- Reviewed receipts → Conservative defaults / atlas guidance

That coverage exists to keep all current top seams visible in at least one explicit receipt edge.

## Maintenance rule
When the handoff graph changes, refresh in the same revision:
- `design/epic-contribution-handoff-graph-2026Q1.md`
- `ledgers/top-band-handoff-graph-v0/README.md`
- `ledgers/top-band-handoff-graph-v0/handoffs.json`
- `tools/check_handoff_graph.py`
- the nearest affected shipset, journey, or routing assets
- front-door continuity rails if the default answer changed
