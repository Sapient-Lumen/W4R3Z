# 185 — Receipt semantics tiers (acknowledged vs included vs consistency)

**Track:** Shared

This archive uses receipt *attachments* (`TransparencyReceipt`) to make publication hard to deny.
But “receipt” can mean different things in different ecosystems.

This doc defines a small set of **receipt semantics tiers** and how we encode them.

## Background (why multiple tiers exist)

Certificate Transparency (CT) distinguishes:
- a **promise** to include within an MMD (SCT), and
- later **proofs** (inclusion / consistency) tied to a tree head.  
RFC 9162 describes bounded-delay behavior (MMD-style) (`source: rfc9162_txt`).

SCITT similarly frames transparency services and receipt profiles, often using COSE-based receipts:
- SCITT architecture (work in progress) (`source: draft_scitt_architecture_22_txt`).
- SCITT receipt profile draft (CCF profile, work in progress) (`source: draft_scitt_receipts_ccf_profile_00_txt`).
- SCITT reference APIs (SCRAPI, work in progress) (`source: draft_scitt_scrapi_07_txt`).

We avoid prematurely freezing a single receipt wire format, but we **do** freeze the vocabulary of what
a receipt is *claiming*, at a coarse level.

## Semantics tiers

We standardize these tiers for `TransparencyReceipt.semantics_tier`:

- **acknowledged**: the service accepted the statement and promises inclusion within a bounded delay (MMD-style).
- **included**: a proof that the statement is included in the log/ledger at (or before) a stated tree head.
- **consistent**: a proof that the service is append-only between two tree heads (anti-equivocation support).
- **witnessed**: a receipt that is additionally witnessed / co-signed by an external entity (optional ecosystem feature).

A single receipt object may convey more than one tier; in that case:
- set `semantics_tier` to the *strongest* tier it directly supports,
- record additional semantics in `notes`, and/or via additional receipts.

## Encoding rules (A2 posture)

We store receipts as JSON objects (`TransparencyReceipt`) for offline presence checks.

- `receipt_type` identifies the family (`scitt`, `ct`, `custom`).
- `profile` identifies a specific profile string registered in `artifacts/registries/receipt-profiles.csv`.
- `proof_type` is the local, schema-level marker (`acknowledgement`, `inclusion`, `consistency`, `custom`).
- `semantics_tier` is the cross-ecosystem tier (above).
- `mmd_seconds` is optional and should be present for **acknowledged** receipts.

Offline verifiers MUST be able to check:
- the receipt object is present,
- it is content-addressed (sha256 matches),
- its `profile` is in the registry.

Semantic verification (cryptographic) is profile-specific and may be performed by specialized tools.

## Profile registry

See `docs/182` for the registry and mapping guidance.
