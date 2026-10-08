
## rev0026 control-change notes

The control-change slice was selected because controller metadata cuts across object identity, battlefield zone containers, combat cleanup, summoning-sickness control-start tracking, and layer-2 continuous effects. The cube still treats the official Comprehensive Rules as external source material and stores only metadata/test references, not copied rules text.


## rev0027 type/color layer notes

The current slice follows the rule-613 shape where type-changing effects and color-changing effects live in separate ordered layers. The implementation remains metadata-only and narrow: it adds reusable derived-characteristic queries and focused tests, not a complete timestamp/dependency engine.

The larger architecture lesson from Forge/XMage-style engines remains the same: as soon as card effects can rewrite object characteristics, every gameplay consumer needs a shared query seam or the codebase drifts into inconsistent one-off checks.


## rev0028 research note: projector-first layers

This slice reinforces a lesson seen in other rules-engine writeups: separate stored/base state from projected/current characteristics. The independent Argentum writeup describes applying active continuous effects in layer order to compute what players see; MTGSim's rev0028 implementation is still tiny, but it deliberately routes consumers through derived helpers as a stepping stone toward a real projector.

The official rules layer structure also makes the order important: layer 6 handles ability adding/removing, layer 7b sets power/toughness to specific values, and layer 7c applies P/T modifications and counters. rev0028 records those as metadata-only ledger hooks and focused tests without bundling official rules text.
## rev0029 research note: generated continuous effects

The current Comprehensive Rules index checked for this revision reports effective date 2026-04-17 and points back to Wizards for the official download. Rules 611/613/514 motivated this slice: generated continuous effects have durations, effects that modify object characteristics lock their affected set when the effect begins, effects within a layer use timestamp order, and cleanup ends until-end-of-turn style effects. MTGSim implements only a narrow until-cleanup scaffold.

## rev0031 research note: timestamp order as projector infrastructure

The current slice follows the rule-613 shape that continuous effects inside a layer or sublayer are usually applied by timestamp order, with static-ability effects using the timestamp of their source and generated effects receiving a timestamp when created. MTGSim implements only a narrow metadata-driven version, but the engineering direction is important: collect active effects, sort them in the projector, and keep combat/SBA/action consumers asking for projected characteristics instead of reading printed state directly.


## rev0032 research note: dependency before full Oracle inference

The official continuous-effect dependency rules are semantic and can override timestamp order inside a layer or sublayer. rev0032 therefore adds an explicit metadata seam rather than pretending MTGSim can infer all dependencies from card text today. This mirrors the broader architecture direction: build deterministic, auditable hooks first, then replace hand-authored metadata with increasingly rich analyzers.

CTest resource allocation remains relevant to the harness roadmap: once fuzz, scenario shards, and long simulation batches have heterogeneous cost, resource-aware scheduling can avoid oversubscribing scarce local slots while still exposing high parallelism.
