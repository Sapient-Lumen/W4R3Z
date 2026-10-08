# Revocation & eligibility transparency (mass-change paranoia)

**Track:** B (Remote return / hard-mode research)


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

## Operational notes
- Keep reasons minimally revealing (privacy) but sufficient for adjudication.
- Publish aggregate counts per reason (within disclosure policy constraints).