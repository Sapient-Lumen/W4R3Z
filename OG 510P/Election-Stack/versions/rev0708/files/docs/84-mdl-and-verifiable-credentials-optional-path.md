# 84 — mDL and verifiable credentials (optional identity proofing path)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This section outlines an **optional** approach for remote identity proofing using a mobile driver’s license (mDL) ecosystem.

## What it is
ISO/IEC 18013-5 defines interface specifications for an mDL between:
- mDL and reader,
- reader and issuing infrastructure.

## Why it might help
- Remote recovery for displaced voters.
- Reduced friction compared to video calls.

## Why it is risky
- Reader app spoofing and malware.
- Liveness bypass and synthetic identities.
- Reliance on device ecosystem availability and vendor security.

## Policy constraints
- MUST NOT make mDL the only recovery path.
- MUST NOT use mDL presentation as a voting credential.
- SHOULD require a second independent factor or in-person confirmation for high-impact actions.

## Recommended safe scope
Use mDL only for **recovery initiation** (opening a case), not for immediate credential issuance.

## Evidence
Any mDL-based recovery decision should result in a `RecoveryRequest` record, and follow `59-dispute-resolution-and-adjudication.md`.