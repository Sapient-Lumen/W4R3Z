# Key ceremony checklist (minimum viable, paranoid)

**Track:** Shared (cross-cutting)


## Objectives
- Generate election public key `PK` and trustee shares `{sk_i}` with no single party ever holding the private key.
- Produce auditable evidence (transcripts, hashes, recordings) suitable for later dispute resolution.

## Pre-ceremony (weeks before)
- Select trustees with organizational diversity; publish trustee identities/roles.
- Define threshold `t-of-n` with rationale.
- Prepare clean-room ceremony devices (fresh OS image, no prior secrets).
- Prepare tamper-evident storage, seals, and inventory logs.
- Pre-register ceremony software hashes and verifier hashes (publicly).
- Run a full “dress rehearsal” with dummy keys.

## Ceremony room controls (day of)
- Physical access control + sign-in.
- Continuous video recording with time overlay.
- No personal devices on the table; no network connections on ceremony devices.
- Two-person integrity for every step (read-aloud + cross-check).

## DKG execution
- Verify ceremony software hashes match published values.
- Generate key shares via DKG.
- Output artifacts:
  - election public key `PK`
  - trustee share commitments (as applicable)
  - transcript hashes (canonical)
- Immediately print/write and seal:
  - `PK`
  - transcript hash
  - trustee share identifiers

## Post-ceremony publication
- Post `PK` and parameter hashes to the Public Bulletin Board (PBB) as a `PARAMS` entry.
- Publish:
  - ceremony report (what/when/who)
  - transcript hash
  - verifier/tooling hashes used to validate artifacts

## Storage & access
- Store trustee shares in HSMs if possible; otherwise sealed, controlled storage.
- Define unlock policy (M-of-N operators), rate limits, audit logs.

## Compromise triggers (predefined)
- Any hash mismatch
- Any unexplained seal break
- Any missing recording segment
- Any unauthorized person in room
- Any unexplained device reboot

If triggered: STOP, preserve evidence, re-run with new devices and keys.

