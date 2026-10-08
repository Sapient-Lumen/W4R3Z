# Revocation & eligibility transparency (mass-change paranoia)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This doc defines how to manage eligibility revocation (lost credential, death records, felony status, etc.) without enabling:
- quiet targeted disenfranchisement
- “stealth rollback” to earlier lists
- mass revocation without ceremony/evidence

## Core idea
Treat revocations and eligibility epochs as **transparent, witnessed, content-addressed objects**.
Conceptually similar to Key Transparency: you either prevent interference or detect it.

## Concepts
- **EligibilityEpoch**: a signed statement of “this is the active eligibility set version” plus references to snapshot roots.
- **RevocationEntry**: an append-only record (reason code + authority + effective date).
- **RevocationTransparencyLog**: Merkle log with witness cosigned checkpoints.

## Safety rules
1. **No silent revocations.** Every revocation is logged with reason code and authority signature.
2. **Mass-change budget.** If revocations exceed threshold, enter *Emergency Revocation Ceremony*:
   - dual control
   - public notice + signed statement
   - extra witness quorum requirement
3. **Rollback detection.** Clients reject epochs not supported by witness quorum checkpoints.

## Voter protections
- Voter can obtain a `VoterStatusProof` showing:
  - current epoch id
  - whether they are revoked
  - contest path + deadlines


## Privacy vs verifiability boundary (turnout surveillance risk)

Transparency objects can accidentally become a **turnout‑surveillance feed** (who/when/where),
via timing, geography, small batch sizes, or joinability with external identity signals.

Track B does **not** claim to solve this (see `docs/167` and `docs/172.3.1`).
Minimum posture while experimenting:

- publish log updates in **coarse batches** with an explicit metadata budget (no per‑person timestamps where avoidable),
- keep public fields minimal; use private `VoterStatusProof` lanes for individual resolution,
- treat any suspected deanonymization as an incident (hazard **HZ‑026**).
- run `CHECK:artifacts/checklists/turnout-oracle-risk-quickcheck.md` and log a bounded row in `artifacts/registries/turnout-oracle-risk-assessments.csv`.

## Operational notes
- Keep reasons minimally revealing (privacy) but sufficient for adjudication.
- Publish aggregate counts per reason (within disclosure policy constraints).