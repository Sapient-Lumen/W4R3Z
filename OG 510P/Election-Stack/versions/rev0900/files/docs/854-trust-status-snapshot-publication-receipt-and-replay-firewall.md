# 854. Trust-status snapshot publication receipt and replay/substitution firewall

**Track:** Shared / verifier boundary  
**Revision:** v847

## Why this exists

The v846 status snapshot gate was useful but incomplete. It could prove that a caller supplied a fresh, byte-pinned snapshot saying trusted signing keys were active, but the snapshot did not yet have its own separately byte-pinned publication evidence. That made replay and local substitution harder to reason about than the keyset/governance lanes.

rev0847 adds an external status-snapshot publication receipt lane. The verifier can now require a receipt that binds to the exact status-snapshot digest, lives outside the packet under test, has its own caller-supplied SHA-256 pin, and meets a synthetic independent-channel quorum.

## Strongest synthetic command shape

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json \
  --trust-keyset-sha256 sha256:bff832d10da7444ec05d7e429a47c62c4ac9a65cd7ec2ac675f50a67a1422810 \
  --trust-keyset-receipt artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json \
  --trust-keyset-receipt-sha256 sha256:bd66c5b8c0d023431695efd067c4a4cfa06fa717567cc14468bff4328562ff28 \
  --require-trust-keyset-receipt \
  --trust-governance-bundle artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.json \
  --trust-governance-bundle-sha256 sha256:346f42e3ea9c4aba173c19bd9ffd41fcdedd5212e941c2e9df78d680674a84bd \
  --require-trust-governance-bundle \
  --trust-governance-bundle-receipt artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.publication-receipt.json \
  --trust-governance-bundle-receipt-sha256 sha256:9e9fd52c2353fbbae64e333f5d167cef8ebf35ab26ea8a49d1bc2c39f6fdbfa8 \
  --require-trust-governance-bundle-receipt \
  --trust-status-snapshot artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0847.json \
  --trust-status-snapshot-sha256 sha256:a2516a17c31055e5a7bb68c473bf5dd0b9f96e23cb6e6d1cecf91a64b6c51619 \
  --require-trust-status-snapshot \
  --trust-status-snapshot-receipt artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0847.publication-receipt.json \
  --trust-status-snapshot-receipt-sha256 sha256:3becac5dd9684d5d1678dc12c753fc5ab6cd82f21449eb258760421555e66212 \
  --require-trust-status-snapshot-receipt \
  --auth-profile strict-local-trust-chain-v1 \
  --verification-time 2026-06-04T12:50:00Z
```

A successful public report exposes:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "trust_status_snapshot_status": "matched",
  "trust_status_snapshot_pin_status": "matched",
  "trust_status_snapshot_receipt_status": "matched",
  "trust_status_snapshot_receipt_pin_status": "matched",
  "trust_status_snapshot_receipt_independent_channel_count": 2
}
```

## New fail-closed conditions

The verifier now fails closed if:

- a required status-snapshot receipt is missing or invalid;
- the receipt is inside the packet under test;
- the caller-supplied receipt pin does not match the external receipt bytes;
- the receipt binds to a different status-snapshot digest; or
- the receipt cannot satisfy the required independent-channel quorum.

## What this still does not prove

This lane only makes a bounded synthetic fixture harder to misread. It still does not prove real signer authority, employment, production key ceremony, hardware custody, independent publication governance, online revocation freshness, jurisdiction-specific threshold adequacy, certification, current voter instruction, legal reliance, or live-pilot authorization.

See also `artifacts/reports/trust-status-snapshot-receipt-audit-rev0847.md` and `scripts/check_signature_verifier_ed25519.py`.
