# Canonical JSON for hashing (RFC 8785 JCS)

DeriveBSD relies on digests everywhere:
- manifest digests
- policy digests
- closure digests
- attestation digests

To avoid “same data, different bytes”, DeriveBSD needs a canonical JSON encoding.

## Adopt JCS (RFC 8785)
JCS defines a deterministic JSON representation by:
- deterministic object member sorting
- strict primitive serialization compatible with ECMAScript JSON
- constraining data to the I-JSON subset for “hashability”

## DeriveBSD rules (v1)
- All hashed JSON objects MUST be JCS-canonicalized.
- Schemas MUST reject non-I-JSON values (NaN/Infinity, etc.).
- Any producer must pass `derive validate` before its output can be hashed.

## Practical implementation notes (Rust)
- Avoid floating point ambiguity by:
  - rejecting floats outright in core schemas, OR
  - representing decimals as strings with explicit semantics, OR
  - using a deterministic decimal library and JCS-compatible rendering.

- Canonicalizer MUST:
  - UTF-8 output
  - no whitespace beyond required JSON
  - lexicographic key sort (Unicode code points)

## Where this applies
- Spec/Lock/Plan JSON hashing (identity)
- runtime manifest hashing
- policy context digest
- attestation payload hashing

See RFC-0053 and ADR-0022.

Last updated: 2026-02-23
