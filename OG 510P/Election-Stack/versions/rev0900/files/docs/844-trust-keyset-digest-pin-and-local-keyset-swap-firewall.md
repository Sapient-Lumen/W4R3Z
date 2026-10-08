# 844 — Trust-keyset digest pin and local keyset-swap firewall

**Track:** Shared / Verifier / Trust-root governance  
**Status:** executable boundary fixture, synthetic only  
**Revision:** v842

## Why this exists

rev0841 correctly blocked packet-contained/self-supplied trust keysets, but one byte-level trust-root hazard remained: an operator could point the verifier at an external keyset whose bytes had silently changed. That can happen through a stale checkout, a copied demo file, a local path mix-up, or a malicious replacement outside the packet boundary.

rev0842 adds caller-pinned trust-keyset bytes. The verifier can now require the supplied external keyset to match a known SHA-256 digest before it will emit `SIGNATURE_VERIFIED`.

## New command shape

Preferred synthetic fixture command:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_signed_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-demo.json \
  --trust-keyset-sha256 sha256:01012aad1fe6bb32d3b2ad1914422df3915d8be7c99221e66cd9e2c8e96d7899
```

The verifier accepts either `sha256:<hex>` or bare 64-hex input. If a pin is supplied and the external keyset bytes differ, authentication fails closed with:

```json
"authentication_status": "SIGNATURE_FAILED"
```

and problem code:

```json
"signature_trust_keyset_pin_mismatch"
```

Malformed expected pins fail with:

```json
"signature_trust_keyset_pin_invalid"
```

The public report also exposes `trust_keyset_pin_required`, `trust_keyset_pin_status`, and `trust_keyset_pin_sha256` inside `signature_verification`.

## What this actually fixes

This narrows `SIGNATURE_VERIFIED` from "the external path contained a matching trusted key" to "the external path contained a matching trusted key and the caller supplied the expected keyset-byte digest."

That matters because the trust-keyset file is now part of the reproducible verifier input. A reviewer can compare the packet, verifier version, verifier-problem-code registry pin, policy-profile pin, and trust-keyset pin without assuming that every local path label is honest.

## What this does not fix

The digest pin is not a trust root by itself. It does not prove signer employment, local election-office authorization, public key publication ceremony, HSM custody, witness independence, online revocation freshness, threshold-policy sufficiency, or live-pilot authorization.

For a real deployment, the expected keyset digest must come from an independently governed channel. The packet must not supply it. A local checklist, public notice, paper record, or independently witnessed key ceremony can carry the digest; this synthetic cube only demonstrates the byte-level verifier behavior.

## Standards and design references

The signature lane remains Ed25519 over the envelope TBS bytes (`source: rfc8032_txt`). JSON surfaces that need deterministic signing or hashing use JSON Canonicalization Scheme (`source: rfc8785_txt`). TUF-style root-key separation and rotation remain a useful design analogy for offline roots and threshold-governed rotation, but the cube treats the mutable latest TUF page as an informative cross-reference rather than a pinned source (`xref: tuf_spec_latest_html`).

## Release-gated check

Run:

```bash
python3 scripts/check_signature_verifier_ed25519.py
```

The check covers positive pinned authentication, wrong-pin failure, malformed-pin failure, packet-contained keyset rejection, retired historical key behavior, revoked/expired/disallowed-scope failures, wrong-key failure, tampered-signature failure, missing-keyset failure, and payload-tamper downgrade.
