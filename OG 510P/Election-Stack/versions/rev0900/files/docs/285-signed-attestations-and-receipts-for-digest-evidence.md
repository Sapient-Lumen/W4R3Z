# 285. Signed attestations and receipts for digest-first evidence surfaces

**Track:** Shared

This note extends the *digest-first evidence surface* pattern (`docs/279–284`) with a minimal, interoperable way to produce **signed statements** about digests (and optionally obtain **receipts**) without publishing raw logs.

The goal is not “blockchain elections.” The goal is **portable, verifier-friendly** artifacts that (a) bind a digest to a signer and a time, and (b) can be independently checked later, even by a skeptical adversary, **without** forcing unsafe disclosure.

## What this adds (one new surface)

**Surface:** *Signed Digest Statement (SDS)*

- Input: a canonical digest from an evidence surface (e.g., AuLD / ICLD / HoldCapsule / Disclosure Packet).
- Output: a small signed statement that says, effectively: “At time T, signer S attests that digest D describes artifact set A under policy P.”
- Optional: a **receipt** from a transparency log or notary service that proves the statement was logged (or otherwise observed) at/after time T.

This composes with `docs/284` (transparency anchoring) and `docs/282` (controlled disclosure).

## Why: avoid raw log dumps while enabling external verification

External observers frequently demand “proof.” The SDS is a middle layer:

- **You disclose the *digest* and the *signature*, not the raw data.**
- If escalation is warranted, you disclose a bounded **Disclosure Packet** (`docs/282`) that *explains* the digest and (optionally) contains redacted excerpts.

In other words: **digest → signed statement → optional receipt → controlled disclosure**.

## SDS minimum fields (HFV)

See `artifacts/templates/hfv.signed_digest_statement.v1.json`.

Required minimum:
- `subject.digest` (algorithm + value) — what is being attested.
- `issuer` (organization + key id / certificate reference).
- `issued_at` (timestamp; include the clock source and uncertainty if known).
- `claims` — *what you assert about the digest* (e.g., “AuLD for precinct reporting pipeline, window 2026-11-03T00:00Z–06:00Z”).
- `signature` — detached signature over a canonical serialization of the statement.

Strongly recommended:
- `scope` (what is included/excluded).
- `pii_risk` and `disclosure_level` (align with `docs/283` and `docs/282`).
- `verification` (how a third party can validate keys and canonicalization).

## Signature envelopes: keep it boring

Use a widely deployed envelope format and treat envelope choice as an *implementation detail* so long as:
- canonicalization is explicit,
- signature verification is deterministic,
- key discovery is auditable.

Existing ecosystems provide options such as:
- **DSSE-style envelopes** (used by in-toto / Sigstore tooling). xref: `dsse_envelope_spec_page`, `intoto_envelope_v1_md`
- **Transparency log receipts** (e.g., Rekor-style inclusion proofs). xref: `sigstore_rekor_overview`
- **SCITT-style architecture components** for transparency + receipts + claim distribution. xref: `draft_scitt_architecture_22_txt`, `ietf_scitt_about`

The Election Stack does not require endorsing any one ecosystem; the requirement is **verifiable signatures + stable receipts**.

## Receipts: what you need and what you should avoid

A receipt should be *small* and independently verifiable, typically including:
- log identifier / public key,
- entry identifier,
- inclusion proof (or receipt structure),
- signed tree head / checkpoint (if applicable),
- timestamp evidence (if provided).

Avoid:
- linking receipts to **voter-identifying** data,
- embedding raw logs in receipts,
- using mutable URLs as “proof.”

If using transparency logs, you can publish only:
- SDS digest + signature,
- receipt metadata (entry id + inclusion proof),
- a pointer to a **public checkpoint** if the ecosystem supports it.

## Operational pattern (recommended)

1. Generate evidence surface digest (AuLD / ICLD / HoldCapsule / Disclosure Packet).
2. Create SDS (sign it with the designated comms/ops key).
3. Optionally log SDS (or its digest) to a transparency log and store the receipt.
4. Publish *only* SDS + (optional) receipt summary.
5. If challenged: issue a bounded **Disclosure Packet** tied to the same digest lineage.

## Failure modes and mitigations

- **Key compromise:** rotate keys; cross-sign the new key; publish an SDS about the rotation event itself.
- **Bad clocks:** include clock source, uncertainty; prefer multiple independent timestamp signals (`docs/177`, `docs/184`).
- **Canonicalization mismatch:** mandate a single canonical JSON serialization (or COSE/CBOR profile) per HFV template.
- **Receipt service outage:** SDS still stands; receipts are *additive*, not required.
- **Over-disclosure pressure:** enforce `docs/282` — publish digests + SDS first; escalate only via packets.

## Where this fits

- Use SDS for **public-facing assurance** about operational artifacts (status pages, incident updates, canvass milestones).
- Use SDS internally to bind digests to incident command decisions and preservation actions.
- Use SDS in legal contexts as a compact “what we knew and when” companion to HoldCapsule.

