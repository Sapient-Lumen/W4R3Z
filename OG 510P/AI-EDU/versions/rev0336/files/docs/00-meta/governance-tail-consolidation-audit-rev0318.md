# rev0318 governance-tail consolidation audit

## Audit target

The waste pattern in rev0318 is not just excess doctrine. It is hot-path assembly burden. When a real
operator must gather pieces from many files, the cube can fail even when the right surfaces exist.
This audit therefore treats "number of surfaces needed before action" as a burden measure.

## Measured burden and refactor

Rev0317's teacher/tutor path required consulting at least the run card, owner-plan template, session
log template, final readout template, service record, and startup docs before a packet existed. The
rev0318 refactor collapses the assembly step into one utility command while preserving the source
surfaces for inspection.

| Hot-path task | Before rev0318 | rev0318 operator path | Treatment |
|---|---:|---|---|
| prepare owner-contact packet | router plus send pack | `make owner-field-work`, then send pack | still human-gated |
| prepare teacher/tutor micro-pilot packet | 4+ surfaces manually copied | `make micro-pilot-pack` | scratch-only, not evidence |
| inspect doctrine tail | broad archive scan | re-entry map and indexes only | cold retrieval |
| decide deletion after real cycle | informal judgment | four-question deletion test below | pending real evidence |

## Deletion test for the next real cycle

After an accepted owner packet or completed micro-pilot readout, every candidate governance surface
must answer four questions:

1. Which decision did this surface change?
2. Which harm did it prevent that an existing surface did not already prevent?
3. Which command, field, or owner action depends on it?
4. Would deleting or cold-parking it increase learner harm, privacy risk, access harm, workload harm,
   or false claims?

If the answer is unclear, merge the surface into an index row or cold archive note. Do not create a
replacement control unless the real cycle exposed a concrete uncovered failure.

## Claim boundary

This audit lowers assembly burden and names deletion criteria. It does not remove historical
obligations, accept evidence, authorize service changes, upgrade claims, or close `FT-0181`.
