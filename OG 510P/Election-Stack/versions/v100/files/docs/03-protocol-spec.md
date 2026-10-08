# Protocol spec (draft, normative)

**Track:** A (Deployable core)


Conventions: **MUST/SHOULD/MAY** follow RFC 2119 semantics.

This spec covers the networked system as a **Public Bulletin Board (PBB)** plus verifiable tallying. It is intentionally compatible with “E2E verifiability on top of paper” deployments (e.g., ElectionGuard-style approaches).

---

## 1) Cryptographic primitives (baseline)
Implementations MUST declare an explicit crypto suite identifier. Baseline guidance:
- Hash: SHA-256
- Signatures: Ed25519 (preferred) or P-256
- Ballot encryption: ElGamal-style public-key encryption suitable for homomorphic tally and/or mixnets
- Ballot well-formedness proofs: NIZK proof(s) that the ciphertext encodes a valid ballot (no overvoting, valid options)
- Threshold cryptography: DKG + threshold decryption (t-of-n trustees)

---

## 2) Core objects (canonical serialization required)

### 2.1 BallotSubmission
A `BallotSubmission` MUST contain:
- `election_id`
- `ballot_ciphertext` (opaque bytes)
- `ballot_proof` (well-formedness proof(s))
- `eligibility_proof` (one of):
  - signature by voter credential key, or
  - anonymous credential proof, or
  - one-time eligibility token with anti-double-vote guarantees
- `client_nonce` (random 128+ bits)
- `client_timestamp_ms` (informational only)

### 2.2 LogEntry
A `LogEntry` MUST contain:
- `entry_type` (`BALLOT`, `PARAMS`, `REVOCATION`, `CLOSE`, etc.)
- `payload_hash` (hash of canonical payload)
- `server_timestamp_ms`
- `node_id`
- `node_signature` over all prior fields

### 2.3 SignedTreeHead (STH)
An `STH` MUST contain:
- `tree_size`
- `root_hash`
- `timestamp_ms`
- `node_id`
- `signature`

If using witness cosigning, `STH` MUST include `witness_cosignatures[]`.

---

## 3) Phases

### Phase 0: Setup (before voting)
1. Trustees MUST run DKG to produce:
   - election public key `PK`
   - trustee shares `{sk_i}`
2. Election parameters MUST be posted to the PBB:
   - `PK`
   - ballot definition hash
   - revoting policy (if any)
   - cryptographic suite id
3. Federation nodes and witnesses MUST publish their public keys.

### Phase 1: Cast/Accept (during voting)
When a node receives a `BallotSubmission`, it MUST:
1. verify `election_id` is active and parameters match,
2. verify eligibility proof and anti-double-voting rules,
3. verify ballot well-formedness proof(s),
4. append a `BALLOT` `LogEntry` (or reject),
5. update its Merkle tree state and (periodically) publish an `STH`.

**Receipt requirement:** the node MUST return either:
- an inclusion proof against a published STH (RECORDED), or
- a short-lived pending receipt that MUST become an inclusion proof quickly (PENDING),
otherwise the client MUST treat the ballot as NOT RECORDED.

Clients MUST verify inclusion using STHs from multiple sources (node + mirror/witness).

### Phase 2: Close (end of voting)
At poll close:
- the federation MUST publish a `CLOSE` entry,
- witnesses MUST freeze and archive final STHs and publish them widely.

### Phase 3: Tally (after close)
Two supported privacy-preserving tally paths:

**A) Mixnet**
- Servers perform verifiable shuffles of ciphertexts.
- Trustees threshold-decrypt the shuffled ciphertexts.
- Publish shuffle proofs + decryption proofs.

**B) Homomorphic tally**
- Aggregate ciphertexts per contest.
- Trustees threshold-decrypt only totals.
- Publish aggregation evidence + decryption proofs.

The system MUST publish sufficient evidence for independent verifiers to confirm “tallied-as-recorded.”

### Phase 4: Audit & recovery
If the election uses paper as ballot of record:
- perform risk-limiting audits (RLA) against the paper trail.
- if cryptographic evidence and paper disagree, pre-defined adjudication rules MUST be followed.

---

## 4) Privacy & metadata notes (non-exhaustive)
- The PBB MUST minimize identity linkage (prefer tokens/anonymous credentials).
- Network metadata can still reveal participation; consider optional privacy transports where legally/operationally acceptable.
- Logs and proofs MUST be publishable without exposing vote content.
