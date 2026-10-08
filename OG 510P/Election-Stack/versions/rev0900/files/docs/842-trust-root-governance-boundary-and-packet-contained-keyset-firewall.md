# 842 — Trust-root governance boundary and packet-contained keyset firewall

**Track:** Shared / Verifier / Trust-root governance  
**Status:** executable boundary fixture, synthetic only  
**Revision:** v841

## Why this exists

v840 made `SIGNATURE_VERIFIED` real for a narrow Ed25519-JCS-TBS lane, but its demo command pointed at a trust keyset stored inside the packet being authenticated. That was safe only if readers understood the file as a fixture. It was still a bad affordance: a malicious or confused packet could carry its own public keyset and invite the verifier to accept self-supplied authority.

v841 makes the trust-root boundary executable: a packet may contain a keyset-shaped file for test or publication purposes, but the verifier refuses to use any `--trust-keyset` path that is inside the packet directory, whether by direct path or resolved route.

## New invariant

`SIGNATURE_VERIFIED` requires all of the following:

1. packet integrity checks pass;
2. every envelope meets the bounded Ed25519-JCS-TBS signature threshold;
3. the supplied public trust keyset is external to the packet boundary;
4. the trusted key is not revoked, is in scope for the envelope kind, and covers the envelope `issued_at` under the local validity window.

A packet-contained keyset now fails closed with:

```json
"authentication_status": "SIGNATURE_FAILED"
```

and problem code:

```json
"signature_trust_keyset_untrusted_location"
```

The public report also exposes:

```json
"trust_keyset_location": "packet_contained_rejected"
```

## Fixture refactor

Positive authenticated fixture:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_signed_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-demo.json
```

Negative self-supplied fixture:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_signed_minimal \
  --json --public \
  --trust-keyset artifacts/examples/evidence_packet_ed25519_signed_minimal/trust-keyset-ed25519-demo.json
```

The second command must fail. This is intentional even though the bytes describe the same public key. Location and governance boundary matter: a packet cannot authenticate itself by shipping a key that validates its own signature.

## Key lifecycle correction

v841 also corrects a rotation edge case. A key with `status: retired` can verify a historical envelope when the envelope `issued_at` is inside the key validity window and before `retired_at` when that timestamp is present. A retired key is still not a current signing authority. A revoked key remains fail-closed.

Synthetic lifecycle fixture:

```text
artifacts/examples/trust_keysets/trust-keyset-ed25519-demo-rotated-retired.json
```

## Not solved

This boundary does not establish real-world authority. It does not prove an election office approved the keyset, that signer employment was verified, that an HSM or hardware token protected the key, that online revocation was checked, that witness policy was met, that threshold policy is sufficient, or that a live pilot is authorized.

The remaining production gap is not another registry. It is a local evidence pack: key ceremony transcript, key publication channel, signer role authorization, witness list, revocation/rotation procedure, offline verifier drill transcript, and independent review of those records.

## Release-gated check

Run:

```bash
python3 scripts/check_signature_verifier_ed25519.py
```

The check now covers the positive external-keyset path, packet-contained keyset rejection, retired historical key verification, wrong-key/tamper failures, revoked/expired/disallowed-scope failures, missing-keyset failure, and payload-tamper downgrade.
