# Post-quantum readiness & cryptographic agility

**Track:** A (Deployable core)


## Why this exists
Election artifacts (logs, receipts, proofs, audit bundles) often need to remain **verifiable for decades**.
That makes elections unusually exposed to “**harvest-now, decrypt-later**” risk: an attacker records encrypted ballots today and waits for future cryptanalytic advances or key compromise.

This document defines:
- a **crypto suite registry** for the system,
- a **migration plan** that preserves verifiability,
- minimum requirements for **hybrid** (classical + PQ) operations during the transition.

## 1) Agility goals (normative)

1. The system MUST be able to **introduce new suites** without changing message semantics.
2. Clients MUST be able to validate **old artifacts** after a suite transition.
3. Nodes MUST NOT silently switch suites; every artifact MUST carry an explicit `crypto_suite_id`.
4. Election setup MUST publish a `CryptoPolicy` that lists:
   - allowed suites,
   - deprecation dates,
   - mandatory verifier behavior.

## 2) Recommended suites (2026 baseline)

### 2.1 Hashing
- Default: SHA-256 for Merkle log hashing (CT-style).
- Migration option: SHA-512/256 or SHA-3-256.

### 2.2 Signatures (log, witness, trustees)
During the transition, artifacts SHOULD be signed using **hybrid signatures**:
- Classical: Ed25519 or P-256 (deployment choice)
- PQ: **ML-DSA (FIPS 204)** and/or **SLH-DSA (FIPS 205)**

Hybrid means: a verifier accepts only if **both** signatures validate.

### 2.3 Key establishment (optional)
If the protocol needs KEM-style key establishment (e.g., for secure channels between trustees), prefer:
- **ML-KEM (FIPS 203)**

## 3) Hybrid checkpoints (normative)

### 3.1 Signed Tree Head (STH)
An STH MUST carry `crypto_suite_id` and a `SignatureBundle`.
If the suite is `HYBRID_CLASSICAL_PQ`, the bundle MUST contain:
- 1 classical signature
- 1 PQ signature

### 3.2 Witness cosignatures
Witnesses MUST cosign using the same suite as the STH.
Witness quorum MUST be evaluated *after* signature validation.

## 4) Migration protocol

### 4.1 Election-to-election migration
Preferred: choose a stable suite per election, change between elections.

### 4.2 In-election migration (emergency)
Allowed only if a critical vulnerability is discovered.
Rules:
- A `PARAMS` log entry MUST announce the new suite.
- A checkpoint MUST include both old and new suite commitments for a transition window.
- Verifiers MUST enforce a strict, published cutover rule.

## 5) Long-term verification bundle
At election close, produce a **Verification Bundle** with:
- final witness-quorum checkpoint
- hash of all published proofs
- verifier version hashes (multi-implementation)
- decryption proof transcripts

The bundle MUST be signed by trustees and witnesses under the active suite.

## 6) Open questions
- How to handle large PQ signatures in constrained channels (SMS/QR)?
- How to keep verification fast on low-end devices?
