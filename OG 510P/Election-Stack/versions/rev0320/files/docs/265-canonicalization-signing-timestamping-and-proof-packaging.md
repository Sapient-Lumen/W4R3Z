# 265 — Canonicalization, signing, timestamping, and proof packaging

**Purpose:** make the archive’s “publishable evidence surfaces” durable, comparable, and independently checkable *without* leaking sensitive configuration details, voter information, or operational security (ops-sec).

This document defines a small, composable **Crypto-Proof Packaging (CPP)** pattern: *canonicalize → hash → sign → timestamp → (optionally) transparency-log*.

> **Design constraint:** prefer **hashes, digests, and attestations** over raw artifacts. Publish the minimum necessary to enable independent verification.

## Core ingredients

### Canonicalization (so hashes are stable)
If you publish hashes of structured data, you must specify how the bytes are produced.

- For JSON, default to **JCS (JSON Canonicalization Scheme)** so different serializers produce the same bytes. ([RFC 8785 — JSON Canonicalization Scheme](https://datatracker.ietf.org/doc/rfc8785/))
- If you must accept arbitrary JSON, constrain inputs to a deterministic subset and document that constraint (JCS’s I‑JSON posture is one reasonable baseline). ([RFC 8785 — JSON Canonicalization Scheme](https://datatracker.ietf.org/doc/rfc8785/))

**Rule:** every “hash commitment” in this repo must state *either* (a) the canonicalization used, or (b) that the artifact is already a byte-for-byte file.

### Hashing
Use a modern collision-resistant hash (e.g., SHA‑256) for commitments and manifesting.

**Rule:** each publishable surface that produces a hash should emit:
- `hash_alg`
- `canonicalization` (or `raw_bytes: true`)
- `digest` (hex/base64, clearly specified)

### Signing
Sign *the digest and metadata*, not the raw sensitive artifact.

Minimal pattern:
- `subject`: what is being committed to (e.g., “ENR snapshot pack #12”)
- `digest`: the hash
- `context`: election + jurisdiction identifiers (coarse, no PII)
- `issuer`: who is attesting
- `issued_at`: timestamp (see below)

## Timestamping and “time of existence”
Timestamps matter in election disputes, audits, and incident timelines.

Two levels:
1) **Local timestamp**: a signed statement including `issued_at`.
2) **Third-party timestamp token** (optional): RFC 3161 Time-Stamp Protocol (TSP) can bind a trusted timestamp to a digest without disclosing the underlying artifact. ([RFC 3161 — Time-Stamp Protocol](https://www.ietf.org/rfc/rfc3161.txt))

**Rule:** if you claim “this existed by time T”, prefer an externally verifiable timestamp token over uncorroborated wall-clock logs.

## Transparency logs (optional, powerful)
If you want public, append-only commitments with independent monitoring:

- Certificate Transparency popularized **Merkle tree–based append-only logs** with **inclusion proofs** and **consistency proofs**. ([RFC 6962 — Certificate Transparency](https://www.rfc-editor.org/rfc/rfc6962.html))
- Sigstore’s **Rekor** provides a transparency log and tooling to query entries and inclusion proofs. ([Sigstore Rekor overview](https://docs.sigstore.dev/logging/overview/) and [Rekor CLI: verify proof of entry](https://docs.sigstore.dev/logging/cli/))

**Rule:** transparency logging is for *commitments* (digests + coarse metadata), not for sensitive internal artifacts.

## CPP: Crypto-Proof Packaging pattern

A **CPP bundle** is a small JSON (or CBOR) object that can be published and re-checked.

**CPP fields (minimum):**
- `cpp_version`
- `subject`
- `digest` (`alg`, `value`)
- `canonicalization` (or `raw_bytes`)
- `issuer` (entity + role)
- `issued_at`
- `signature` (scheme + value)  
- `related_commitments[]` (optional: link to CommitLog Entry (CLE), audit pack, incident digest, etc.)

**CPP extensions (optional):**
- `rfc3161_tst` (timestamp token) ([RFC 3161 — Time-Stamp Protocol](https://www.ietf.org/rfc/rfc3161.txt))
- `transparency_log` (log id, entry id, inclusion proof pointer) ([RFC 6962 — Certificate Transparency](https://www.rfc-editor.org/rfc/rfc6962.html); [Sigstore Rekor overview](https://docs.sigstore.dev/logging/overview/))

## How CPP composes with existing surfaces

- **CommitLog / transparency logs (doc 261):** CPP is the per-artifact “proof envelope”; CLE is the append-only “publication rail”.
- **ENR snapshot packs (doc 252):** CPP wraps the snapshot digest + correction log digest.
- **Change-control / updates (doc 256):** CPP wraps baseline attestation digests and drift ledger digests.
- **Incident digests (doc 259):** CPP wraps timeline digests and notification ledgers.
- **Audit packs (doc 260):** CPP wraps randomness ceremony record digests and final report digests.

## Stop conditions (non-negotiable)
Do **not** publish CPP bundles that would:
- expose voter identities, ballot images, CVRs that can be re-identified, or precinct/style mappings,
- provide operational details that materially increase attack capability (network diagrams, credentials, admin URLs, detailed step-by-step exploitation),
- enable intimidation, doxxing, or targeted harassment of election workers,
- “launder” sensitive contents by hashing them if the hash itself is linkable to a public corpus (treat linkability as a privacy risk).

If a stakeholder requests such materials, route through **Public Records + Retention + Access Bounds** (doc 253) and your jurisdiction’s policy surface registry (doc 262).
