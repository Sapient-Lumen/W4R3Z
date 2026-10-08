# Everlasting privacy, retention windows, and key-destruction ceremonies

**Track:** A (Deployable core)


## Why this exists
If encrypted ballots remain publicly archived, then **future key compromise** (or future cryptanalytic breakthroughs) can retroactively expose votes.
This is catastrophic for:
- ballot secrecy,
- receipt-freeness (voters can prove how they voted if ciphertexts become decryptable),
- coercion resistance.

This document defines a practical “everlasting privacy” posture:
- minimize what must remain public,
- time-box exposure,
- use strict key-destruction ceremonies.

## 1) Baseline privacy guarantee

### 1.1 Strongest achievable claim (with E2E publication)
With standard E2E designs that publish ballot ciphertexts, secrecy is only as strong as:
- the long-term security of the cryptography,
- and the operational security of the tally private key shares.

### 1.2 Operationally enforceable improvement
If trustees can credibly destroy all key shares after tally and audit finalization, then later compromise of trustee devices SHOULD NOT enable decryption of archived ciphertexts.

This is NOT a cure-all (attackers may steal shares before destruction), but it makes long-term privacy strictly better.

## 2) Retention windows (normative)

1. The system MUST define a published **Verification Window** (e.g., 30–180 days):
   - during this window, full ciphertexts and proofs are publicly available.
2. After the window, the official election authority MAY publish an **Archive Commitment**:
   - keep Merkle commitments and checkpoints forever,
   - optionally remove bulk ciphertext payloads from official hosting.

Note: third parties may mirror ciphertexts; the privacy posture depends on key destruction.

## 3) Key-destruction ceremony (normative)

### 3.1 Inputs
- tally complete
- audits complete (including risk-limiting audits if paper-of-record exists)
- final verification bundle published

### 3.2 Procedure
- trustees attest the custody of their key shares
- independent observers verify device states and logging
- trustees execute destruction (HSM erase or physical destruction)
- a signed `KeyDestructionAttestation` is published to the log

### 3.3 Evidence requirements
The attestation MUST include:
- trustee identities (organizational, not personal if avoidable)
- device/HSM identifiers
- timestamps
- witness cosignatures
- hash of the final verification bundle

## 4) Design choices that improve everlasting privacy

### 4.1 Prefer totals-only decryption where possible
If homomorphic tally is feasible, decrypting only totals reduces the harm of future key exposure.

### 4.2 Strong separation between receipts and plaintext
Receipts MUST never contain plaintext or decryptable hints.
They SHOULD be inclusion proofs only.

### 4.3 Avoid publishing unnecessary metadata
See: 22-metadata-privacy-and-traffic-analysis.md

## 5) What this does NOT solve
- coercion during the election window
- client malware altering voter intent
- an attacker who steals key shares before destruction
