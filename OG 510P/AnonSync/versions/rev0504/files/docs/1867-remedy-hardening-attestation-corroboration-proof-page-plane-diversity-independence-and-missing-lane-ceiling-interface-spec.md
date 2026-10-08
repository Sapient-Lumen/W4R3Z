# Remedy-hardening-attestation-corroboration proof page — plane diversity, independence, and missing-lane ceiling

## Proof purpose

This page is where the product proves the highest honest corroboration sentence.
It exists so a later verifier can see whether the strongest sentence depends on one dominant evidence lane or is actually supported across the required independent planes.

## Proof payload

The proof page must preserve at least:

- case identifier
- source attestation-freshness receipt identifier
- attestation bundle identifier
- current corroboration posture rung
- required evidence-plane set
- satisfied evidence-plane set
- independence floor
- dominant-plane warning flag
- contradiction set
- stale-plane set
- same-world reuse set
- cross-world corroboration status
- highest honest corroborated sentence
- strongest blocked stronger sentence

## Mandatory proof language

Examples the page must support:

- `fresh sealed bundle only; corroboration floor not met`
- `desktop and storage planes agree, but runtime corroboration remains pending`
- `same-world corroboration only; stronger cross-world sentence blocked`
- `contradiction open between service world and storage world`
- `independently corroborated for required verifier cohort`

## Prohibited overstatements

The page must never let these overstatements pass unscarred:

- `corroborated` when the product really means `seen twice from one underlying lane`
- `independent` when all evidence was derived from one restart-gated workflow
- `cross-world` when the product only proved one storage world
- `stable` when a required plane is stale or absent
- `strong verifier sentence stands` when the contradiction set is still open
