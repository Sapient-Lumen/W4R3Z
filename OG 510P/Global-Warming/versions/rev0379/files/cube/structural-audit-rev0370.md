# Structural audit rev0370

## Scope

Bounded audit of the active BVPS evidence-acquisition hotpath after rev0369.

## Findings

- The highest immediate risk is procedural loss: meeting notes, public handouts, or records responses could be captured without source/custodian and hash metadata.
- The second risk is stale routing: ADAMS and FOIA/public-record routes can change, and NRC Web-Based ADAMS retirement makes old assumptions unsafe.
- The third risk is packet drift: request templates can become unsynchronized from blockers unless generated and validated.

## Corrective actions in rev0370

- Generated request packets from templates and mapped them to blockers/proofcut classes.
- Added route-verification and ADAMS-transition audit tables.
- Added empty lockbox templates and a reproducible builder.
- Rebuilt active hotpath SQLite/capsule from a source list.

## Deferred

- No real evidence adjudication because no real or lawfully anonymized packet is present.
- No destructive removal of historical matrices or mirrors.
