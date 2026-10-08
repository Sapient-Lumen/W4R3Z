# Frontier delta programs — 2026-03-25

This note keeps the frontier broadly stable **while making cheap change handling first-class**.

The archive no longer needs more sector inflation.
It needs sharper answers to:
- what kind of change happened,
- which prior conclusions still carry forward,
- and what the smallest honest rerun is.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of the leading lanes should now be planned as shipping **delta programs / change classes / rerun slices** rather than only renewal loops or review packets.

## Delta-leverage board

### 1. P-0431 + P-0496 + P-0125
**Role:** continuity / change-class / supersession ring

Why first under this lens:
- release, advisory, route, mirror, and boundary changes are the natural place where old trust can partially carry forward or collapse;
- this ring already sits closest to source identity, public exposure drift, and inventory changes;
- and it is the best place to define stable “carry”, “downgrade”, “reset”, and “manual review required” semantics.

What the crate should provide:
- `change-intake.json`,
- `change-classification.json`,
- `carry-forward-decision.json`,
- `supersession-diff.json`,
- `delta-summary.md`,
- and `confidence-reset.json`.

### 2. P-0509 + P-0536 + minimal P-0535
**Role:** decision / knowledge / rerun front door

Why second:
- it is where another team actually sees what changed in a recommendation, basis, or support posture;
- it can turn change classes into rerun slices, reopened sections, and updated review consequences;
- and it can compare old and new packets without pretending the whole decision was rebuilt from zero.

What the crate should provide:
- reviewed delta bundles,
- rerun-slice plans,
- carry-forward verdicts,
- reopened-section maps,
- and compact “why this recommendation changed” summaries.

### 3. P-0472 + P-0484
**Role:** basis-delta supplier

Why third:
- docs.rs, rustdoc JSON, downloads, and target/toolchain surfaces are increasingly machine-usable enough to power narrow basis diffs;
- default-target and build-recipe changes show that small substrate shifts can invalidate support claims selectively;
- but shared carry-forward semantics should stay above the raw import layer.

What the crate should provide:
- basis-delta receipts,
- docs/build/API/target diffs,
- support-scope change hints,
- and explicit “too much changed to carry forward” states.

### 4. P-0486
**Role:** debugger tuple-delta kit

Why fourth:
- official debugging material keeps stressing debugger / OS / version variance;
- delta handling is essential here because full-matrix reruns are expensive;
- but the shared change vocabulary should be proven in simpler lanes first.

What the crate should provide:
- tuple-diff receipts,
- matrix-cell carry-forward decisions,
- tuple-scoped rerun slices,
- and explicit expiry/reset outcomes.

### 5. P-0537
**Role:** iteration delta specialist

Why fifth:
- build-analysis, relink-don't-rebuild, and build-dir layout work make “what changed enough to rebuild or relink?” more plausible;
- but the substrate is still moving enough that this lane should borrow shared delta doctrine rather than define it first.

What the crate should provide:
- build-cause deltas,
- restart-vs-relink-vs-rebuild hints,
- and explicit “substrate changed, summary invalid” outcomes.

### 6. P-0538
**Role:** concurrency scenario delta later

Why sixth:
- highly important,
- but scenario maintenance is expensive and should inherit a proven change-class discipline rather than invent one early.

## Why the broad frontier still stays stable

This delta lens still does **not** justify resetting the archive toward giant umbrella frameworks for web, GUI, game, ML, or local-first work.
Those sectors may still have unmet needs, but the sharper cross-domain missing value is usually:
- explaining what changed,
- preserving what still carries,
- reducing rerun blast radius,
- and superseding old conclusions cleanly.

That is why the archive still prefers control-plane kits above broad sector reinventions.

## Guardrail

Do not strengthen a lane under the delta lens unless the pass can name:
1. the **change class**,
2. the **carry-forward rule**,
3. the **minimum rerun slice**,
4. the **confidence-reset rule**,
5. and the **supersession diff semantics**.
