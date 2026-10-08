# 176 — Canonicalization & Signing Rules for Evidence Envelopes

**Track:** Shared

## Purpose
Independent verifiers only agree if they hash and sign **the exact same bytes**. This doc defines the canonical byte sequences for:

- `payload_digest`
- `tbs_digest` (to‑be‑signed digest for `EvidenceEnvelope`)

This is a **format-drift firewall**.

## Canonical JSON
All canonicalization uses **RFC 8785: JSON Canonicalization Scheme (JCS)** (`source: rfc8785_txt`).

Constraints:
- Payloads SHOULD stay within the I‑JSON subset (no NaN/Infinity; avoid ambiguous number formatting).
- When in doubt, represent numeric identifiers as **strings**.

Implementation notes (JCS / JSON.stringify number rules):
- `-0` is canonicalized to `0`.
- Use decimal form when the base‑10 exponent is in `[-6, 21)`, otherwise use scientific form.
  Examples: `1e20 -> 100000000000000000000`, `1e21 -> 1e+21`, `1e-6 -> 0.000001`, `1e-7 -> 1e-7`.

## Payload digest
Given a payload JSON value `P`:

1. Serialize `P` using JCS to UTF‑8 bytes `B`.
2. Compute `D = sha256(B)`.
3. Set `payload_digest = "sha256:" + hex(D)`.

Notes:
- If the payload is detached (`payload_pointer`), `payload_digest` MUST match the detached bytes after JCS canonicalization **of the JSON payload**.
- `payload_pointer.uri` (and any attachment `uri`) MUST be a **safe relative path** within the packet (no `..`, no absolute paths, no backslashes; reject percent-escapes like `%2e%2e/`; reject control chars / leading-trailing whitespace).
- Packets SHOULD NOT include symlinks; verifiers SHOULD treat any detached-payload/attachment path that resolves outside the packet root as unsafe.
- `payload_pointer.media_type` SHOULD be `application/json` (or omitted). Explicit non-JSON media types are treated as schema violations by verifiers.
- For shipped examples in this archive, detached payloads and attachments SHOULD use content-addressed filenames: `sha256-<hex>.<ext>` where `<hex>` matches the declared digest (drift firewall).
- EvidenceEnvelope (as specified by `schemas/EvidenceEnvelope.json`) standardizes **JSON payloads** only.
  If you need to bind opaque bytes (PDF excerpts, images), include them as **attachments** (`EvidencePointer` + digest)
  or define a new envelope schema/kind that extends `canonicalization`.

## To‑be‑signed digest (tbs_digest)
Signatures bind the envelope header + the payload digest (not the inline payload bytes).

Define `TBS(envelope)` as the JSON object containing these fields exactly:

- `envelope_version`
- `kind`
- `track`
- `issued_at`
- `issuer`
- `subject`
- `payload_schema`
- `payload_digest`
- `canonicalization`
- `attachments` (if present)

The `signatures`, `payload_inline`, and `payload_pointer` fields are **excluded** from the signing input.

Algorithm:
1. Build `T = TBS(envelope)`.
2. Serialize `T` using JCS to UTF‑8 bytes `B`.
3. Compute `D = sha256(B)`.
4. Set `tbs_digest = "sha256:" + hex(D)`.
5. Each signature signs `B` (or signs `D` with a domain‑separated scheme; if so, document the scheme in `alg`).

## Required verifier behavior
A verifier MUST:
- recompute `payload_digest` from the payload bytes (inline or detached) using the rule above,
- recompute `tbs_digest` from `TBS(envelope)`,
- reject envelopes where either digest mismatches,
- treat missing detached payloads as **incomplete evidence** (publish a suppression / missing-object report if the bundle was promised).

## Why this is strict
Attackers (or accidents) win by creating ambiguity:
- different JSON serializers produce different bytes,
- different audiences see different “equivalent” objects,
- signatures become unverifiable.

This doc makes that failure mode *measurable* and *automatable*.

## Reference tooling
This archive includes a stdlib-only RFC8785-JCS canonicalizer:
- `tools/jcs.py` (library)
- `tools/jcs_canonicalize.py` (CLI)

Digest helpers are centralized in:
- `tools/envelope_common.py` (shared digest rules used by reference tools)

Drift tripwire:
- `artifacts/test-vectors/envelope_vectors.json` (tiny known-good digests)
- `scripts/check_envelope_vectors.py` (fails the release if digests change unexpectedly)

Verifiers SHOULD treat these as a *reference*, not a production crypto library.
