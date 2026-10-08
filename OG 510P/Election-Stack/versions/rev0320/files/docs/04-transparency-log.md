# Transparency log & federation (Public Bulletin Board / PBB)

**Track:** A (Deployable core)

> **Read-first:** before treating anything here as deployment guidance, read `166-scope-and-claims-contract.md` and `167-non-claims-and-boundaries.md` (they are binding on interpretation).



## Threat focus
The federation layer must defend primarily against:
- **equivocation** (split views / forked histories),
- **selective censorship** (dropping ballots for specific groups),
- **retroactive edits** (rewriting or deleting accepted ballots),
- **availability attacks** (DDoS / routing attacks / partition),
- **ordering attacks** (strategic reordering to influence revote/last-vote rules).

Core stance: **the log is untrusted**; its job is to emit cryptographic evidence that makes misbehavior *detectable*.

This design is intentionally aligned with the transparency-log pattern of Certificate Transparency (Merkle log + inclusion/consistency proofs).

---

## 1) Data model

### 1.1 Log entry (leaf)
Each accepted submission produces exactly one immutable `LogEntry` (see `schemas/LogEntry.json`):
- `election_id`
- `entry_type` (`BALLOT`, `PARAMS`, `REVOCATION`, `RESULTS`, `CLOSE`, ...)
- `payload_hash_b64` (base64-encoded hash of canonical serialized payload)
- `node_id` (which log node accepted the entry)
- `server_timestamp_ms` (informational wall-clock; do not use as an ordering oracle)
- `node_signature_b64` (signature over canonical LogEntry fields)
- *(optional)* `time_beacon_digests` (sha256 digests of published `hfv.time.beacon` envelopes for this epoch; see `31`/`38`/`192`)
- *(optional)* `sth_ref` (tree_size/root hash hint for later proof fetching)

**Canonical payload for `BALLOT`:**
- ballot ciphertext
- well-formedness proof(s) (ZK)
- eligibility proof (anonymous token OR signature + privacy wrapper)
- revote policy fields (if used)
- safe-to-publish metadata only (minimize!)

**Canonical payload for `RESULTS`:**
- the ResultsReleasePackage manifest JSON for the release interval (`236`)


### 1.2 Signed Tree Head (STH)
Periodically, the log operator publishes an `STH` that commits to the log state:
- `tree_size`
- `root_hash`
- `timestamp_ms`
- `log_id`
- `signature`

### 1.3 Witness-cosigned checkpoint (recommended)
Clients SHOULD treat only *witness-cosigned* STHs as final. A checkpoint is:
- `STH` + a set of `WitnessCosignature` objects
- each cosignature attests: “I observed and verified this STH; I will gossip it.”

---

## 2) Hashing and proofs (normative)

### 2.1 Hash function & encoding
- MUST use SHA-256 (or a named suite with agility plan).
- All fields MUST be canonicalized and length-delimited before hashing.

### 2.2 Merkle tree hashing (CT-style)
- `LeafHash(x) = SHA256(0x00 || x)`
- `NodeHash(l, r) = SHA256(0x01 || l || r)`
Carry behavior on odd nodes: promote last node unchanged.

### 2.3 Inclusion proof
Nodes MUST provide inclusion proofs for any leaf <= current `tree_size - 1`.

### 2.4 Consistency proof
Nodes MUST provide consistency proofs between any two STHs they have published.
Clients and witnesses MUST reject inconsistent STH pairs.

---

## 3) Topology options

### Option A: BFT replicated state machine
Nodes run a BFT protocol to agree on total order of accepted entries.
- Pros: single canonical history; simple verifier story.
- Cons: operational complexity; membership and liveness under attack are hard.

### Option B: Sequencer + witness cosigning (recommended “hard but operable”)
- Sequencer proposes append batches; emits STHs.
- A quorum of independent witnesses **co-sign** each STH.
- Clients treat only quorum-cosigned STHs as FINAL.

If the sequencer equivocates, witnesses will observe conflicting STHs and publish **fork proofs**.

---

## 4) Witnesses & gossip (anti-split-view)

### 4.1 Witness requirements
Witnesses MUST:
- fetch STHs from multiple endpoints (sequencer + mirrors),
- verify STH signatures, inclusion proofs, and consistency proofs,
- exchange STHs with other witnesses (gossip),
- publish signed alerts + evidence on equivocation or missing checkpoints.

### 4.2 Minimum viable gossip protocol
- Witnesses periodically exchange “latest STH per log_id” + signatures.
- If a witness observes two STHs with the same `log_id` and `tree_size` but different `root_hash`,
  it MUST publish a **ForkProof** containing both signed STHs.

### 4.3 Client verification rule (simple)
Clients MUST:
- fetch checkpoints from ≥2 independent sources,
- verify cosignatures meet the quorum policy,
- accept a ballot as FINAL only if inclusion is proven against a quorum checkpoint.

---

## 5) Availability & safe failure
Availability is not guaranteed. The system MUST degrade safely:
- if an inclusion proof is not obtained, UI MUST instruct the voter to use a safe fallback.
- during partitions, the sequencer MUST NOT declare FINAL without witness quorum.
- emergency procedures MUST be pre-committed and published (see `18-failure-drills.md`).

---

## 6) Test vectors & independent implementations
Publish test vectors and require ≥2 independent verifiers.
See `artifacts/test-vectors/merkle_test_vectors.json`.
