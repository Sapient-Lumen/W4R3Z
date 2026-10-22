# Helm

[SlopOS](../README.md) · [Complete editions](../DOWNLOADS.md#helm)

## A desktop you can steer

Helm imagines the desktop as an instrument: something a person can arrange, inspect, remember, and program without having to guess what lies behind its surfaces. Its ambition brings together the determinism of a tiling window manager, the immediacy of desktop automation, the reach of a summon-and-search box, and the explanatory power of an unusually good task manager. Within OG 510P's SlopOS constellation, Helm asks what capability-oriented computing might feel like to inhabit.

Its proposed desktop has seven first-party pillars: Tiling Shell, Omnibox, Object Browser, Operations Center, Desktop Flow, Recall, and Exchange. A native terminal/capshell front end joins them. The important design decision is that these are different faces of one object world, not unrelated applications. Focus, placement, identity, transfer, and continuity belong to a shared shell model. Automation begins with that model, reaches structural UI next, and retains a visibly separate raw-automation lane. Power is the point; making hacks the exception is the aspiration. [Read the architecture](../sources/Helm/rev0221/docs/30-architecture/architecture-overview.md).

## Returning to work

Imagine returning to a release workspace after several days away. You summon “Release readiness” in the Omnibox. Helm's specimen distinguishes the saved doorway from the current state of the release: opening that doorway retrieves a definition, while the Object Browser's live provider card supplies a fresh observation. An Operations Center summary may be older than both. Instead of folding those objects into one reassuring green panel, the proposed interface offers the appropriate next move: inspect, compare, or recheck. These are concrete card texts and affordances in the archive, not merely a principle about transparency. [Explore the release-readiness cards](../sources/Helm/rev0221/fixtures/release-readiness/surface-affordance-cards.json).

A remembered workspace receives the same treatment. The proposed capsule diff compares expected bindings with present objects. One window might match exactly, another need repair, and a third no longer be available. You could rebind the missing slot rather than surrender the whole workspace or accept an inaccurate “restored” banner. This is continuity conceived as a useful negotiation with the present, rather than a screenshot of the past. [Read the capsule-diff contract](../sources/Helm/rev0221/docs/30-architecture/capsule-diff-candidate-contract-v0.md).

Before a stronger action, a rehearsal card would show the selected object, route, provider, known effects, and unresolved parts. Rehearsal does not promise omniscience: “deferred-to-runtime” is an admissible answer. Its value is to make an action understandable before commitment, without turning every ordinary operation into a simulation project. [Read the rehearsal contract](../sources/Helm/rev0221/docs/30-architecture/action-rehearsal-candidate-contract-v0.md).

## Making state perceptible

Helm's artistic vocabulary is spatial and tactile: cards, ribbons, rails, beacons, lamps, and drawers. These names give otherwise invisible relationships somewhere to appear. A saved entry can feel inviting without pretending to be live; a repair can be helpful without pretending to be complete. The central aesthetic challenge is compression: how little chrome can carry enough truth for the next decision, while leaving exact detail within reach?

The later archive puts that question into a bounded SlopOS seam. Its network-consent specimen separates proposal, authority difference, presentation, fresh gesture, approval, admission or denial, receipt, and retention. Helm would make the action legible; SlopOS would own enforcement. The map names the specific `portal.net.request` family and its replay identity rather than declaring a universal integration layer. [Read the Helm–SlopOS seam map](../sources/Helm/rev0221/docs/30-architecture/helm-slopos-seam-map-v0.md).

## What the archive makes executable

By rev0221, Helm has moved beyond design prose into a queryable specimen archive. Its Python query tool reads structured records and answers bounded questions about stale affordances, imported arrivals, derived claims, fresh rechecks, and historical Recall. Its contradiction query uses explicitly named event pairs, not a general reasoning engine. [Inspect the query implementation](../sources/Helm/rev0221/tools/query_specimen_cube.py).

Other Python checkers test declared specimen requirements. The audit/export checker, for example, checks case references, required fields, posture-specific conditions, and the separation between portable evidence and portable permission. It does not send an export or establish that a person understood a screen. These are concrete archive mechanisms, not a running compositor or a demonstrated whole-OS desktop. [Inspect the audit/export checker](../sources/Helm/rev0221/tools/check_audit_export_pack.py).

Helm is compelling because its desired computer is generous. It wants fast navigation, rich memory, automation, and beautiful surfaces. Its distinctive contribution is the insistence that those pleasures can invite action while still showing what, exactly, the next action rests on.
