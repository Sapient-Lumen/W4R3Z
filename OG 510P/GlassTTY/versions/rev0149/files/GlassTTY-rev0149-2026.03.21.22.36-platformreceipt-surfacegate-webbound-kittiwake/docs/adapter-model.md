# Adapter model

GlassTTY adapters translate one browser surface into shared workflows and shared state families.

## Adapter responsibilities

Every adapter should define:

- surface-detection rules
- route and session assumptions
- receiver resolution rules
- composer read/write rules
- submit rules
- generation-state cues
- latest-turn extraction rules
- evidence capture hints
- drift notes
- known unsupported workflows

## Adapter outputs

An adapter should not only “perform actions.” It should also emit:
- shared state families
- receiver-audit and resolution reasons
- action outcomes
- support-bundle hints
- drift clues when a workflow appears broken

## Capability layering

### Level 0 — detect only
Can recognize the surface, but not yet meaningfully interact.

### Level 1 — compose only
Can resolve receiver and read/write the prompt draft.

### Level 2 — turn loop
Can read/write/submit and read latest turn.

### Level 3 — support-grade
Can emit stable evidence bundles, structured diagnostics, and support-truth records.

### Level 4 — agent-grade
Can support policy-bound repeated action loops with meaningful state and outcome surfaces.

## Shared vs surface-specific knowledge

Shared:
- workflow names
- state family names
- evidence family names
- support tiers
- action/outcome semantics

Surface-specific:
- DOM/ARIA cues
- frame/route caveats
- generation-state hints
- edge-case blockers
- rollout risk notes

## Reference adapter

Claude is the current reference adapter because it already has real implementation work and evidence lanes in-tree. It should be used to extract generic patterns, not to freeze the project into Claude-only assumptions.
