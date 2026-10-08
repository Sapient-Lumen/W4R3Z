# 851 — Trust-governance-bundle publication receipt and dead-code refactor

**Track:** Shared / Verifier / Trust-root governance  
**Status:** v845 synthetic verifier hardening  
**Scope:** `tools/observer_verify_packet.py`, `scripts/check_signature_verifier_ed25519.py`, `schemas/TrustGovernanceBundlePublicationReceipt.json`, `schemas/PacketVerificationReport.json`

## Why this exists

v844 added an external trust-governance bundle, but the remaining foot-gun was subtle: an operator could still copy the governance-bundle digest from the same local folder and treat that as independent publication evidence. v845 adds a separate external governance-bundle publication receipt so the verifier can require three separable inputs before reporting `SIGNATURE_VERIFIED` in the strongest synthetic path:

1. the external trust keyset and its digest pin;
2. the external trust-keyset publication receipt;
3. the external trust-governance bundle and its separate publication receipt.

The receipt is synthetic and offline. It does not fetch channels, prove legal authority, prove employment, prove HSM custody, or prove online revocation freshness.

## Positive command shape

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json \
  --trust-keyset-sha256 sha256:bff832d10da7444ec05d7e429a47c62c4ac9a65cd7ec2ac675f50a67a1422810 \
  --trust-keyset-receipt artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json \
  --require-trust-keyset-receipt \
  --trust-governance-bundle artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.json \
  --trust-governance-bundle-sha256 sha256:346f42e3ea9c4aba173c19bd9ffd41fcdedd5212e941c2e9df78d680674a84bd \
  --trust-governance-bundle-receipt artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.publication-receipt.json \
  --trust-governance-bundle-receipt-sha256 sha256:9e9fd52c2353fbbae64e333f5d167cef8ebf35ab26ea8a49d1bc2c39f6fdbfa8 \
  --require-trust-governance-bundle \
  --require-trust-governance-bundle-receipt
```

The positive public report now exposes `trust_governance_bundle_receipt_status=matched`, `trust_governance_bundle_receipt_pin_status=matched`, and an independent-channel count for the governance-bundle publication receipt.

## New fail-closed controls

`SIGNATURE_VERIFIED` is unavailable when the governance-bundle publication receipt is required and:

- the receipt is missing;
- the receipt is packet-contained;
- the receipt pin is malformed or mismatched;
- the receipt's observed governance-bundle digest differs from the supplied governance bundle;
- the receipt has fewer independent publication channels than required.

The regression gate is still `scripts/check_signature_verifier_ed25519.py`.

## Code refactor performed

v845 also removes the unused duplicate `validate_trust_keyset_governance_bundle` implementation and its unused profile constant from `tools/observer_verify_packet.py`. Keeping two similarly named governance validators was a future bug farm: one path was live and the other was dead, with partially overlapping semantics. The verifier now has one live trust-governance-bundle validation path plus one live governance-bundle-publication-receipt path.

## Boundary

This is a synthetic offline trust-boundary test. It does not establish production signer authority, legal delegation, key ceremony quality, HSM custody, independent publication governance, online revocation status, certification, live-pilot readiness, or current voter instruction.
