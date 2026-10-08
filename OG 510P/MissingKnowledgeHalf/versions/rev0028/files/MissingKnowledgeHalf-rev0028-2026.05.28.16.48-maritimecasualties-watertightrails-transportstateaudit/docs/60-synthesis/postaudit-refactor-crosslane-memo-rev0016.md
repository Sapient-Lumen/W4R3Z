# Post-audit refactor cross-lane memo — rev0016

Rev0015 found that the cube was coherent but not clean enough to scale blindly. Rev0016 pays the first major structural debt before adding more cases.

## The deepest repair

The cube now admits that evidence is not one thing.

A claim can be supported by an official report, a peer-reviewed article, a source-index record, a promoted incident record, a replication record, an infrastructure record, a pattern's own status caution, or a meta-research audit. These objects should not all be called sources.

Typed `evidence_refs` makes this distinction explicit.

## The second repair

Pattern candidates now have to face controls.

The early cube naturally produced pattern candidates: numeric representation assumptions, warning proof-burden inversion, hard-endpoint reversals, signal commons, denominator rails, audit pairs, software control planes, software attribution traps, multi-lab boundary maps, and practice-lag/de-adoption. These are useful but seductive. Rev0016 makes each one carry positive controls, negative controls, counterexamples, rollback triggers, and maturity gates.

## The third repair

The graph is now visible as a graph.

`GRAPH-EDGES.json` is not final, but it makes relationships queryable: records cite sources; records contain claims; claims cite evidence; patterns are supported by records; compact link dictionaries become edges.

## What remains unpaid

Locator debt remains. Second review remains. Genealogy remains thin. Pattern controls are scaffolded but not yet promoted. Source vocabulary is controlled at major-class level but raw subtypes remain messy.

This is progress because the cube is more honest about its own uncertainty.
