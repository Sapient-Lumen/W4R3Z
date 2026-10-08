# Key management & ceremonies

**Track:** A (Deployable core)


Security-critical keys in this system are **governance objects**. Handle them like nuclear material.

## 1) Key types
### 1.1 Voter credential keys
Assumption: citizens hold private keys, ideally hardware-backed (smartcard/FIDO/secure enclave).

### 1.2 Registration Authority (RA) keys
- Issuance / certification keys for voter credentials or eligibility tokens
- Revocation signing keys

### 1.3 Log / federation keys
- PBB node signing keys (acceptance signatures, STH signatures)
- Witness cosigning keys (STH quorum)

### 1.4 Election cryptographic keys
- Election public key `PK` for ballot encryption
- Trustee secret shares `{sk_i}` produced by DKG (no single private key ever exists)

---

## 2) Privacy-preserving eligibility: tokens over identity (recommended)
If you can, avoid using “identity-bound signatures” directly on ballot submissions.

Two common approaches:
1. **Anonymous eligibility tokens**: RA issues one-time election tokens (e.g., blind-signed or anonymous credentials).  
   The token proves eligibility but is unlinkable to identity by the PBB.
2. **Linkable ring / group signatures**: voter proves membership in the eligible set without revealing which member, while preventing double-voting.

This pack does not mandate one scheme, but strongly recommends **minimizing identity linkage** and “turnout surveillance” risk.

---

## 3) Ceremonies (minimum viable)
### 3.1 DKG ceremony (election key generation)
- MUST be public/observable and recorded.
- MUST produce a publicly verifiable transcript where possible.
- MUST include pre-defined disaster procedures (trustee missing, device failure, compromise suspicion).

### 3.2 Separation of duties
Strict separation between:
- offline ceremony devices,
- online serving infrastructure,
- build/signing infrastructure,
- monitoring/verifier infrastructure.

No shared admin accounts across these domains.

---

## 4) Threshold design
Choose t-of-n so:
- t resists collusion (insider threat),
- n tolerates absence/attacks (availability),
- trustees are organizationally diverse.

Typical: 5-of-9, 7-of-13, etc. Document rationale and assumptions.

---

## 5) Hardware security posture
- Trustee shares SHOULD be in HSMs where possible (audited, rate-limited).
- If HSMs are not feasible, use hardware-backed enclaves + strict physical controls + independent auditing.

---

## 6) Revocation & reissuance (critical safety valve)
- Credential recovery MUST be in-person (or equivalently strong identity proofing).
- Revocation list MUST be signed and posted to the PBB as a log entry type so that revocations are auditable.
- Reissuance MUST rotate keys and invalidate prior credentials/tokens immediately.

---

## 7) Key compromise handling (pre-written)
Predefine:
- threshold for “trustee share suspected compromised”,
- how to re-run DKG and migrate elections,
- how to invalidate affected ballots (if required) while preserving evidence for courts.
