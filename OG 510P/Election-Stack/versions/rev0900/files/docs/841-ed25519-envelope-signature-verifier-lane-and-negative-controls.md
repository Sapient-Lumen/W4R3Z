# 841 — Ed25519 envelope-signature verifier lane and negative controls

**Track:** Shared / Verifier / Release gate  
**Status:** bounded implementation lane, synthetic fixture only  
**Revision:** v840; amended by v841 trust-root boundary firewall

## Why this exists

v839 made the default verifier boundary explicit: `status: PASS` meant packet integrity checks passed, not that any signer identity was authenticated. That was safer than silence, but it left the riskiest practical gap unfinished: a local operator or reviewer still needed a narrow way to check that evidence envelopes were signed by a supplied public trust keyset.

v840 adds that narrow lane to `tools/observer_verify_packet.py`.

## What changed

The verifier remains hash-only by default and still emits:

```json
"authentication_status": "HASH_ONLY_NOT_AUTHENTICATED"
```

When a caller supplies a local public trust keyset, the verifier can now authenticate `EvidenceEnvelope.signatures[]` over the RFC8785-JCS to-be-signed bytes defined in `tools/envelope_common.py` and `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`.

Preferred command shape:

```bash
python tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_signed_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-demo.json
```

The legacy alias `--auth-keyring` is still accepted, but new docs should prefer `--trust-keyset` because the file is a public trust-keyset, not secret key material. As of v841, that keyset must be supplied from outside the packet directory. A packet-contained trust-keyset copy is treated as self-supplied authority and rejected.

A successful authenticated fixture emits:

```json
"authentication_status": "SIGNATURE_VERIFIED"
```

and includes a bounded `signature_verification` summary with public-only fields such as the trust-keyset SHA-256, envelope counts, checked/valid signature counts, and the explicit non-claims.

## What this does not prove

`SIGNATURE_VERIFIED` means only this bounded local profile succeeded: the envelope signature bytes verified against a public key in the supplied local trust keyset, and the surrounding packet integrity checks did not fail.

It does **not** prove legal authority, real election-office adoption, current office custody, current voter instruction, online revocation freshness, signer employment, witness independence, live-pilot authorization, or certification.

## New fixtures and negative controls

v840 adds:

- `artifacts/examples/evidence_packet_ed25519_signed_minimal/`
- `artifacts/examples/trust_keysets/trust-keyset-ed25519-demo.json`
- `artifacts/examples/trust_keysets/trust-keyset-ed25519-demo-rotated-retired.json`
- `schemas/EnvelopeTrustKeyset.json`
- `scripts/check_signature_verifier_ed25519.py`

The regression check exercises substantive failure modes, not just a happy path:

- known-good signed fixture with an external trust keyset must produce `SIGNATURE_VERIFIED`;
- packet-contained/self-supplied trust keyset must produce `SIGNATURE_FAILED` with `signature_trust_keyset_untrusted_location`;
- retired-but-valid historical key must still verify an envelope issued before retirement;
- tampered signature or wrong public key must produce `SIGNATURE_FAILED` with `signature_invalid` and `signature_threshold_not_met`;
- revoked key must produce `SIGNATURE_FAILED` with `signature_key_revoked`;
- expired key must produce `SIGNATURE_FAILED` with `signature_key_expired`;
- disallowed envelope kind must produce `SIGNATURE_FAILED` with `signature_kind_not_allowed`;
- `--require-authentication` without a supplied trust keyset must fail closed;
- payload tampering after signature must make the packet fail and downgrade authentication to `SIGNATURE_FAILED`.

Run the focused check:

```bash
python scripts/check_signature_verifier_ed25519.py
```

## Source anchors

This lane is intentionally pinned to a small standards surface: EdDSA/Ed25519 signature behavior (`source: rfc8032_txt`), FIPS 186-5 digital-signature context (`source: nist_fips_186_5_pdf`), RFC8785 JSON canonicalization for the TBS bytes (`source: rfc8785_txt`), and NIST key-management guidance for the remaining trust-root governance problem (`source: nist_sp800_57_pt1_r5_pdf`).

## Audit artifact

The focused v840 audit/refactor record is `artifacts/reports/signature-verifier-boundary-audit-rev0840.md` plus the machine-readable summary `artifacts/reports/signature-verifier-boundary-audit-rev0840.json`. The v841 trust-root boundary audit is `artifacts/reports/trust-root-boundary-audit-rev0841.md`.

## Refactor/audit result

This revision turns the verifier-signature boundary from a prose no-go into an executable two-lane path:

1. default integrity-only verification, intentionally unauthenticated;
2. optional local Ed25519 trust-keyset verification with negative controls.

That is deliberately smaller than a full PKI. v841 removes the most dangerous fixture ambiguity by rejecting packet-contained trust roots and moving the positive fixture keyset to `artifacts/examples/trust_keysets/`. The remaining work is real key governance: signer identity proofing, role authorization, revocation distribution, key rotation, threshold policy, hardware-backed key storage, independent witness policy, and local legal authority mapping.
