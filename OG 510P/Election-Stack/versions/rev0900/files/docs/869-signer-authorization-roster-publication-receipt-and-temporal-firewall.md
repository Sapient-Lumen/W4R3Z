# 869 — Signer-authorization roster publication receipt and temporal firewall

**Track:** Shared / verifier boundary  
**Revision:** v852  
**Status:** synthetic-only verifier hardening

v852 closes two practical gaps in the strict local authorized verifier lane. A byte-valid signer-authorization roster is no longer enough for the strongest synthetic policy-lockfile path; the verifier also requires an external, caller-pinned signer-authorization roster publication receipt. The roster itself must also carry coherent issuance, validity-window, authority-observation, and per-row authorization timing before it can contribute to SIGNATURE_VERIFIED.

The receipt is deliberately packet-external. It binds the signer-authorization roster digest to independent synthetic publication channels and fails closed when the receipt is missing, packet-contained, byte-pin mismatched, digest mismatched, or below the independent-channel quorum.

## What now has to line up

The strongest synthetic policy path uses all of these external byte-pinned inputs:

1. threshold-2 Ed25519 trust keyset
2. trust-keyset publication receipt
3. trust-governance bundle
4. trust-governance bundle publication receipt
5. trust-status snapshot
6. trust-status snapshot publication receipt
7. signer-authorization roster
8. signer-authorization roster publication receipt
9. verification-policy lockfile
10. verification-policy lockfile publication receipt

The new signer-authorization roster receipt fixture is:

```text
artifacts/examples/trust_keysets/signer-authorization-roster-ed25519-threshold2-rev0852.publication-receipt.json
sha256:713f733dc9552b8d90952fe999b6a3066e44bab8c28d6547ff10bd5ae2b4ed6b
```

The corresponding roster fixture is:

```text
artifacts/examples/trust_keysets/signer-authorization-roster-ed25519-threshold2-rev0852.json
sha256:09c640ffae5496823ae2fd6ad84d91a2847d0a984a8e0377f8c9ad0dfa4b4fcd
```

## Executable controls

`scripts/check_signature_verifier_ed25519.py` now proves fail-closed behavior for these receipt cases:

- missing required signer-authorization roster publication receipt
- signer-authorization roster receipt byte-pin mismatch
- signer-authorization roster digest mismatch inside the receipt
- weak/single-channel signer-authorization roster receipt quorum
- packet-contained signer-authorization roster receipt

The same gate still exercises the earlier negative controls for wrong keys, revoked keys, expired keys, stale governance, status snapshot replay, signer-role/kind/scope/time failures, unsafe policy paths, exact-scope policy-selector mismatches, policy-publication receipt replay, and payload tampering.

## Boundary

This receipt proves only a local, synthetic publication-gating rule over bytes supplied to the verifier. It does **not** prove real signer employment, legal delegation, HR identity proofing, procurement authorization, HSM custody, live online revocation freshness, independent production publication governance, current voter instruction, certification, or live-pilot readiness.


## Temporal gate added in rev0852

The signer-authorization roster now fails closed when its `issued_at`, `valid_from`, or `valid_until` fields are missing, unparseable, future-dated, outside the verifier-supplied `--verification-time`, or internally reversed. Authority observations must be present and must not postdate the roster issuance or verifier time. Active signer-authorization rows must have parseable bounded `authorized_from` and `authorized_until` windows.

The public `PacketVerificationReport.signature_verification` object now exposes:

```text
signer_authorization_roster_temporal_status
signer_authorization_authority_observed_at_status
signer_authorization_row_validity_status
signer_authorization_roster_issued_at
signer_authorization_roster_valid_from
signer_authorization_roster_valid_until
signer_authorization_roster_verification_time
```

These fields are synthetic verifier controls only. They do not prove employment, appointment, legal delegation, procurement authority, production key custody, or live-pilot authorization.
