# 190 — Envelope interop vectors & drift tripwires

**Track:** Shared

## Purpose
If independent verifiers don’t hash and sign **the same bytes**, the whole ecosystem fractures.

This doc defines a **tiny** interoperability surface for EvidenceEnvelope digest rules:
- `payload_digest`
- `tbs_digest`

It is intentionally **not** a giant conformance suite (we can’t afford archive bloat).
Instead, it’s a **tripwire**: if a maintainer changes canonicalization or the TBS field set,
CI fails loudly.

Normative reference: `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`.

## What’s in the vector set
- `artifacts/test-vectors/envelope_vectors.json`
  - 2–5 minimal envelopes/payloads
  - expected `payload_digest` and `tbs_digest`
  - vectors MAY reference an existing JSON payload via `payload_path` to avoid duplication/bloat
  - includes at least one case with `attachments` present

These vectors are designed to be:
- **stable** across languages
- **small** (bytes, not pages)
- **human-auditable**

## How the tripwire works
- `scripts/check_envelope_vectors.py` recomputes digests using the reference implementation:
  - `tools/jcs.py` (RFC8785-JCS)
  - `tools/envelope_common.py` (shared digest rules)

If any vector digest changes, the script fails with a diff.

## How to extend safely
When adding or changing vectors:
1. Keep the vector file under ~5KB.
2. Prefer **new cases** over expanding existing cases.
3. Avoid “real” election data; use synthetic payloads.
4. If you change the digest rules, record the rationale as an ADR and update `docs/176`.

## Why this matters
The most damaging failure mode is “everyone thinks they verified, but they verified different bytes.”
Tiny vectors catch that drift early.
