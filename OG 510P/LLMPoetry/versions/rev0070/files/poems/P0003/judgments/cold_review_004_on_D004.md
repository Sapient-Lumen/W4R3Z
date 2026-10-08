# Cold Review — P0003-D004 “No One Left” — rev0066

**Verdict:** `promote_to_internal_anthology_candidate_not_evidence`  
**Band:** `A`  
**Temporal status:** later-turn review of the exact rev0065 draft, packet, database, WAL, spec, receipt, and rendered surfaces.  
**Lineage action:** freeze at D004; no D005 by inertia.

## Decision

D004 passes the internal candidate threshold. It is the first P0003 draft whose page and artifact make the same event. The base database says people are living in the unit, their usual residence is here, no departures exist, and the generated status is OCCUPIED. The paired WAL changes one field to elsewhere; the trigger records OCCUPIED becoming VACANT. The committed page does not summarize that event from outside it. It is the event’s readable state.

The strongest fact is not that a unit can be called vacant while people are present. It is that **nothing leaves**. The row persists, the people-present value persists, the departures relation remains empty, and only the administrative relation to elsewhere changes. The title therefore has two simultaneous readings: nobody departed; nobody is left in the category that makes the unit occupied.

## Criterion-first read

- **Form integrity — A.** Removing the WAL removes the committed poem’s state. The formal dependency is irreducible rather than decorative.
- **Specificity density — A.** Each field does pressure; the zero-departure line prevents the ending from becoming ordinary vacancy.
- **Closure risk — A.** `CURRENT STATUS | VACANT` leaves a contradiction with the still-present persons instead of resolving it.
- **Diction risk — B/A boundary.** The administrative language is exact and unsentimental, but the title may pre-solve the double meaning.
- **Disclosure survival — A.** Full disclosure deepens rather than deflates the work because the base/committed difference is materially real.
- **Need test — A.** The database/WAL split is the poem’s event, not an explanatory appendix.

## Pairwise and order-swap control

Against D003, D004 wins in both orders: it removes the unrelated HUD branch, eliminates familiar room traces, and realizes the previously missing occupied-to-vacant transition. Against D001, D004 also wins in both orders: D001’s absence inventory can be paraphrased without its storage mechanism, while D004’s one-field transition cannot.

## Residual risk

A hostile reader may still experience the title plus `VACANT` as a solved logic puzzle. The Census category may feel like borrowed institutional authority. The single-file reader edition is only an accessible presentation of verified states, not the canonical execution. Most importantly, no real disclosed reader has tested whether interest survives the explanation.

## Candidate action

Freeze the exact D004 bytes as an internal anthology candidate. Do not create D005 simply because another turn exists. A successor requires a concrete later external-reader failure or project-owner line-level instruction.

This review is not evidence, admission, publication clearance, a real housing determination, or a reader response.
