# Trust-status snapshot freshness and revocation firewall

**Track:** Shared verifier / trust-root boundary  
**Status:** v846 synthetic verifier hardening  
**Scope:** `tools/observer_verify_packet.py`, `schemas/TrustStatusSnapshot.json`, `schemas/PacketVerificationReport.json`, `scripts/check_signature_verifier_ed25519.py`, `artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0846.json`

## Problem fixed

v840-v845 progressively made the authenticated verifier lane harder to overclaim: external Ed25519 keysets, byte pins, threshold-2 signing, publication receipts, a synthetic governance bundle, and a governance-bundle publication receipt. The remaining dangerous gap was status freshness. A packet could verify against a keyset and governance bundle, but the verifier still had no bounded way to reject a key that was revoked, suspended, missing from the current status surface, or covered only by stale status evidence.

v846 adds an **optional external trust-status snapshot** lane. In the strongest synthetic path, `SIGNATURE_VERIFIED` now requires all previous external trust-root/governance inputs plus a fresh, byte-pinned, external status snapshot that binds to the same trust keyset and governance evidence and does not revoke or omit trusted signing keys.

## Strongest synthetic verifier path

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
  --require-trust-governance-bundle \
  --trust-governance-bundle-receipt artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.publication-receipt.json \
  --trust-governance-bundle-receipt-sha256 sha256:9e9fd52c2353fbbae64e333f5d167cef8ebf35ab26ea8a49d1bc2c39f6fdbfa8 \
  --require-trust-governance-bundle-receipt \
  --trust-status-snapshot artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0846.json \
  --trust-status-snapshot-sha256 sha256:552c0f8e64056e7a2c784c2035fb67c90fdcd44a0611c9c54c82c62e36ba2d74 \
  --require-trust-status-snapshot \
  --verification-time 2026-06-04T11:30:00Z \
  --auth-profile strict-local-trust-chain-v1
```

Expected public summary fields include:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "trust_status_snapshot_status": "matched",
  "trust_status_snapshot_pin_status": "matched",
  "trust_status_snapshot_authority_count": 2,
  "trust_status_snapshot_key_status_count": 3,
  "trust_status_snapshot_revoked_key_count": 1,
  "auth_profile": "strict-local-trust-chain-v1",
  "auth_profile_status": "requirements_met"
}
```

The revoked key in the fixture is a historical synthetic key that is **not** part of the active threshold keyset. If the snapshot revokes one of the currently trusted keys, omits a trusted key, mismatches public-key material, mismatches keyset/governance digests, lacks authority quorum, is stale, is packet-contained, misses its byte pin, or is supplied without an explicit `--verification-time`, the verifier fails closed.

## Strict authentication profile

The v846 verifier also adds `--auth-profile strict-local-trust-chain-v1`. Without this flag, the verifier can still be used intentionally for narrower tests, such as checking a signature against an external keyset only. With this flag, `SIGNATURE_VERIFIED` requires the strongest synthetic trust chain now present in the cube:

- an external trust keyset and matching trust-keyset SHA-256 pin;
- a matching external trust-keyset publication receipt;
- threshold signing with at least two distinct valid key materials;
- a matching external trust-governance bundle, byte pin, witness quorum, and lifecycle evidence;
- a matching external governance-bundle publication receipt and byte pin;
- a matching external trust-status snapshot, byte pin, freshness window, and status-authority quorum.

A weaker flag combination now fails closed under the strict profile with `signature_auth_profile_not_met`, even when raw signature bytes would otherwise verify. This prevents the strongest example command from being diluted accidentally into a weaker local-authentication claim.

## New negative controls

`scripts/check_signature_verifier_ed25519.py` now covers:

- missing required trust-status snapshot;
- packet-contained status snapshot;
- status-snapshot byte-pin mismatch;
- missing explicit `--verification-time` for a supplied/required status snapshot;
- stale or expired status window;
- revoked/suspended/compromised/disabled active signer;
- missing active key status;
- public-key digest mismatch;
- trust-keyset digest mismatch;
- trust-governance-bundle or governance-receipt digest mismatch;
- insufficient status-authority quorum;
- weak ad hoc authenticated flag combinations under `--auth-profile strict-local-trust-chain-v1`;
- all earlier wrong-key, revoked-key, expired-key, disallowed-kind, repeated-signature, receipt, governance, and payload-tamper cases.

## Boundary

This is not an online revocation protocol. The verifier does not fetch status channels, prove status-board independence, prove signer employment, prove production HSM custody, prove legal authority, or authorize live-pilot use. It only proves that the caller supplied an external local status snapshot whose bytes, freshness window, key statuses, digest bindings, and explicit verification timestamp satisfy the bounded synthetic policy.

The default verifier remains hash-only and emits `HASH_ONLY_NOT_AUTHENTICATED` unless `--trust-keyset` is supplied. The trust-status snapshot lane is opt-in and fail-closed when required.
