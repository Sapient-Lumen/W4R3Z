# Structural audit rev0316 — BVPS ETE transcription, mass-care capacity, and AAR critical path

## Finding 1 — rev0315 ETE table was not source faithful

The rev0315 BVPS ETE loadcase table mixed official public ETE rows with supplemental model-demand rows and mis-transcribed several official values. Rev0316 replaces that surface with a 12-row source-faithful table and a separate supplemental loadcase-demand table. The old table remains historical context only.

## Finding 2 — mass-care capacity was under-normalized

Rev0315 carried at least three placeholder capacity rows. Rev0316 imports the public PEMA support-county requirements/capacities, 17 mass-care facilities, and 27 Pennsylvania municipality-to-reception-center assignments. These are still public context only, not operational readiness proof.

## Finding 3 — public numbers needed a hard claim firebreak

Correcting public numbers can accidentally make overclaiming easier. Rev0316 therefore adds leak tests, a KLD release hold, public-to-local closure leak view, and an 11-row critical path board.

## Compatibility note

Legacy 114,494-row universal nuclear crossproduct tables are still retained for compatibility. Emergency readiness and BVPS real-public queries route to sparse/local/public-firebreak surfaces instead.
