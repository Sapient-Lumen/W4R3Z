# 846 — Trust-keyset publication receipt and distinct-quorum firewall

**Track:** Shared / Verifier / Trust-root governance  
**Status:** executable synthetic boundary, not production authority  
**Revision:** v843

## Why this exists

rev0842 made local keyset swaps harder by allowing `--trust-keyset-sha256`. That still left two operational foot-guns:

1. a one-key fixture could still look too much like a real trust model;
2. a digest pin could be copied from the same local folder as the keyset, rather than from an independently governed channel.

rev0843 adds a bounded fix for both. The verifier now understands a distinct-key-material threshold declared by the public trust keyset, and it can require a separate external publication receipt that binds the keyset digest to named channel records.

## New command shape

Synthetic threshold fixture:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json \
  --trust-keyset-sha256 sha256:bff832d10da7444ec05d7e429a47c62c4ac9a65cd7ec2ac675f50a67a1422810 \
  --trust-keyset-receipt artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json \
  --require-trust-keyset-receipt
```

Expected public result:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "signature_threshold": 2,
  "signature_verification": {
    "trust_keyset_receipt_status": "matched",
    "trust_keyset_receipt_independent_channel_count": 2
  }
}
```

## What changed in the verifier

`tools/observer_verify_packet.py` now emits `report_version: 1.6.0` and recognizes these trust-keyset features:

```json
{
  "signature_policy": {
    "minimum_distinct_valid_signatures_per_envelope": 2,
    "require_distinct_key_material": true,
    "require_distinct_kids": true,
    "require_all_envelopes_authenticated": true
  }
}
```

A threshold is satisfied only by distinct trusted key material. Repeating one valid signature, or repeating one key record, does not create a quorum.

The verifier can also consume an external `TrustKeysetPublicationReceipt` object. The receipt is rejected if it is packet-contained, malformed, bound to a different keyset digest, or lacks enough distinct publication channels.

## New fail-closed problem codes

```text
signature_trust_keyset_receipt_invalid
signature_trust_keyset_receipt_untrusted_location
signature_trust_keyset_receipt_digest_mismatch
signature_trust_keyset_receipt_channel_quorum_not_met
```

## Fixtures and schemas

```text
artifacts/examples/evidence_packet_ed25519_threshold2_minimal/
artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json
artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json.sha256
artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json
artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json.sha256
schemas/TrustKeysetPublicationReceipt.json
```

## Release-gated check

Run:

```bash
python3 scripts/check_signature_verifier_ed25519.py
```

The check now covers the threshold-positive path and the high-risk failures: repeated one-key signature, missing required receipt, receipt digest mismatch, single-channel receipt, packet-contained receipt, packet-contained keyset, wrong pin, malformed pin, wrong key, revoked key, expired key, disallowed kind, tampered signature, and payload tamper.

## Standards and design references

The signature primitive remains Ed25519 (`source: rfc8032_txt`). The signed bytes remain RFC8785-JCS envelope TBS bytes (`source: rfc8785_txt`). TUF root-role practice is a useful analogy for offline roots, threshold signatures, and out-of-band recovery (`xref: tuf_spec_latest_html`), but this cube still does not implement TUF production governance.

## Non-claims

This does not prove signer employment, election-office authorization, independent witness identity, HSM custody, online revocation freshness, legal sufficiency, certification, or live-pilot readiness. It only makes the synthetic verifier boundary harder to misread and harder to accidentally satisfy with self-selected trust material.
