# 856. Signer-authorization roster and verification-policy lockfile firewall

**Track:** Shared / verifier boundary  
**Revision:** v847

## Why this exists

The v840-v846 verifier hardening made the archive much better at authenticating bytes against a packet-external trust chain. That still left a dangerous interpretation gap: a key can be cryptographically valid and current while the person or role behind that key is not authorized for the envelope kind being checked.

rev0847 adds two bounded synthetic controls:

1. an external signer-authorization roster that binds trusted signing keys to signer IDs, roles, allowed envelope kinds, scope, and authorization authorities; and
2. an external verification-policy lockfile that assembles the long trust-chain inputs and pins into one auditable policy object.

This is an implementation/refactor change, not another doctrine layer. It reduces hand-assembled CLI sprawl and makes role/scope authorization fail closed in the same executable regression path as signature, trust-root, governance, status, and receipt checks.

## Strongest synthetic policy-lockfile command

```bash
python3 tools/observer_verify_packet.py   artifacts/examples/evidence_packet_ed25519_threshold2_minimal   --json --public   --verification-policy-lockfile artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0847.json   --verification-policy-lockfile-sha256 sha256:470a6fa69dd3793b90502da9d9cc332b3ff8813a05de9b46d8c721bd9b590a7b
```

A successful public report exposes the authorized strict profile and the signer-authorization roster gate:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "verification_policy_lockfile_status": "matched",
  "verification_policy_lockfile_auth_profile": "strict-local-authorized-trust-chain-v1",
  "signer_authorization_roster_status": "matched",
  "signer_authorization_roster_pin_status": "matched",
  "signer_authorization_authority_count": 2,
  "signer_authorization_active_entry_count": 2
}
```

## New fail-closed conditions

The verifier now fails closed if:

- the strict authorized profile is requested without a signer-authorization roster;
- the roster lives inside the packet being authenticated;
- the roster bytes do not match the caller-supplied SHA-256 pin;
- the roster binds to a different trust keyset or trust-status snapshot;
- the roster has too few distinct authorization authorities;
- a trusted signing key is missing from the active authorization rows;
- a row authorizes the wrong public-key material, signer ID, role, kind, scope, or time window;
- the verification-policy lockfile lives inside the packet, has a bad pin, is inactive/malformed, or is supplied together with manual trust-chain flags that would make the effective inputs ambiguous.

## Maintainer rule

Use the verification-policy lockfile for the strongest synthetic path. The long CLI is still useful as a diagnostic form, but humans should not have to hand-copy every trust input and pin for routine regression checks.

## Boundary

This proves only bounded synthetic authorization semantics. It does not prove real employment, legal appointment, delegation under state law, procurement approval, HSM custody, production key ceremony, current voter instruction, certification, live-pilot readiness, or legal reliance.

See also `schemas/SignerAuthorizationRoster.json`, `schemas/VerificationPolicyLockfile.json`, `artifacts/examples/trust_keysets/signer-authorization-roster-ed25519-threshold2-rev0847.json`, `artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0847.json`, and `scripts/check_signature_verifier_ed25519.py`.

## v848 path-scope update

The policy-lockfile fast path introduced here is now path-scoped by `docs/857-verification-policy-lockfile-path-scope-and-trust-input-base-dir.md`. Use the rev0848 policy fixture for the strongest synthetic path; the older rev0847 policy fixture is retained as historical context but does not exercise the strict `trust_input_base_dir` child-path firewall.
