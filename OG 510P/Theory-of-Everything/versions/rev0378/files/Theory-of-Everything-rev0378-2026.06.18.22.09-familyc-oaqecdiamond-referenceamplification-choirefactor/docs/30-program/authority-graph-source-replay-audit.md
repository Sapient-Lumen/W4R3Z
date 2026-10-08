# Authority graph source-replay audit

## Revision

`rev0317` repairs the highest-risk gap left after graph compaction: the graph was compact and codec-checked, but the default rebuild path still carried forward the previous graph rather than proving that the stored graph could be reconstructed from source ledgers.

## Failure mode found

In `rev0316`, `make index` ran a fast registered edge repair and regenerated summaries, but it did not fully replay `AUTHORITY-DEPENDENCY-GRAPH.json` from the route, claim-binding, public-record, acquisition, rollback, and route-support ledgers. The compact graph was therefore protected against storage corruption, but not against stale generated-edge content. That is a serious control-plane risk: a future ledger edit could leave rollback and claim-support propagation attached to yesterday's graph while lint still passed.

## Repair implemented

`tools/sync_generated_surfaces.py` now has `replay_authority_dependency_graph()`. It runs the base graph generator, replays the non-superseded historical augmentation passes in source order, applies the registry-driven route/binding edge repair, and writes the compact graph once at the end. The replay is in memory, so the full graph can be rebuilt without repeatedly serializing the compact artifact after every augmentation pass.

`tools/lint_archive.py` now imports the same replay function and rejects any stored compact graph that differs from deterministic source-ledger replay. This is stronger than the rev0316 codec check: codec roundtrip proves that the stored compact graph is internally well-formed; replay equality proves that the graph still follows from executable source ledgers.

## Superseded pass

The old prospective/preregistration/blinding augmentation pass remains in the file for history, but the replay wrapper excludes it because the later registry-driven route/binding repair covers that route-local-plus-wrapper family together with later support families. Replaying both in the wrong order changes wording for the same dependency keys without adding coverage. The registry pass is the current source for those generic registered route/binding edges.

## Measured result

- Prior stored logical edge count: `51,599`.
- Replayed logical edge count in this revision: `51,673`.
- Prior logical edges lost: `0`.
- New logical edges added by source replay: `74`.
- New edge classes: `26` route-to-open-question claim-support edges, `22` carrier-to-open-question claim-carrier-support edges, and `26` protocol-to-open-question claim-protocol-support edges.
- Affected open questions: `OQ-0111` unit/constant/scale-setting controls and `OQ-0112` uncertainty/significance/coverage controls.

## Why this is substantive

The repair attaches newest support-family claim bindings to the same rollback/dependency machinery already used by earlier controls. Without these edges, route-local handles existed in ledgers and summaries, but some open-question wording did not have explicit route/carrier/protocol support edges in the dependency graph.

## Non-promotion boundary

No route is promoted. Added claim-support edges can only freeze, cap, demote, or roll back dependent wording when a route, carrier, or acquisition protocol fails. They cannot create observed-sector recovery, public-record closure, negative-control survival, or `S4`/`S5` evidence.
