# 867 — Verification-policy receipt identity and signer-authorization publication firewall

**Track:** Shared  
**Release:** v852  
**Status:** Synthetic verifier boundary, not production authority

## Why this exists

The strict policy-lockfile path is now the safest way to invoke the long synthetic Ed25519 trust chain, but that makes the policy-publication receipt itself more important. A receipt that binds the right policy bytes but describes the wrong policy id or packet scope is a replay/substitution smell, even when the SHA-256 digest matches.

v852 therefore makes policy-publication receipt identity and selector coherence executable:

- the receipt's `verification_policy_lockfile_id` must match the policy lockfile's `policy_id`;
- the receipt's `packet_selector.packet_id` must match the policy lockfile selector;
- the receipt's `packet_selector.election_id` must match the policy lockfile selector;
- the receipt's `packet_selector.jurisdiction` must match the policy lockfile selector;
- mismatches fail closed with `signature_verification_policy_lockfile_receipt_identity_mismatch`.

The strongest synthetic path also uses the packet-external, byte-pinned signer-authorization roster publication receipt as part of the strict authorized profile. This reduces the chance that a locally swapped signer-authorization roster is mistaken for a published authorization surface.

## Current strongest synthetic command shape

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --verification-policy-lockfile artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0852.json \
  --verification-policy-lockfile-sha256 $(cat artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0852.json.sha256 | awk '{print $1}') \
  --verification-policy-lockfile-receipt artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0852.publication-receipt.json \
  --verification-policy-lockfile-receipt-sha256 $(cat artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0852.publication-receipt.json.sha256 | awk '{print $1}') \
  --verification-time 2026-06-04T20:50:00Z
```

Expected public report highlights:

```text
authentication_status: SIGNATURE_VERIFIED
auth_profile_status: requirements_met
signer_authorization_roster_receipt_status: matched
verification_policy_lockfile_receipt_policy_id_status: matched
verification_policy_lockfile_receipt_packet_selector_status: matched
```

## New negative controls

`scripts/check_signature_verifier_ed25519.py` now proves fail-closed behavior for:

- policy-publication receipt with the wrong policy id;
- policy-publication receipt with the wrong election selector;
- policy-publication receipt with a missing selector field;
- the existing digest, pin, channel-quorum, temporal-order, packet-contained, path-scope, exact-selector, signer-authorization, status, governance, keyset, and tamper failures.

## Boundary

This still authenticates bytes and synthetic local trust-chain evidence only. It does not prove signer employment, statutory delegation, HR records, production HSM custody, independent publication governance, live online revocation freshness, certification, legal reliance, current voter instruction, or live-pilot readiness.
