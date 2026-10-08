# 886 — Public-fingerprint symlink warning and strict-policy fail-closed

**Track:** Shared / Verification / Policy lockfile
**Status:** v859 executable verifier hardening

rev0859 closes the next safety gap in the strict synthetic policy path: the packet-public-fingerprint helper must not silently follow symlinked public surfaces when its digest is being used as a replay/substitution boundary.

The bounded public fingerprint remains a publishable comparison digest, not a sandbox. Still, strict policy verification now treats public-fingerprint warnings as authentication failures, so the helper must emit stable warnings for suspicious local filesystem routes instead of reading through them quietly.

## Change

`tools/public_fingerprint_report.py` now reports warnings for:

```text
packet_root_symlink_rejected_for_hash:.
directory_symlink_rejected_for_hash:<relpath>
file_symlink_rejected_for_hash:<relpath>
unsafe_relpath_rejected_for_hash:<relpath>
file_resolved_outside_packet_rejected_for_hash:<relpath>
non_file_rejected_for_hash:<relpath>
```

The helper skips rejected surfaces before calculating the public fingerprint. `tools/observer_verify_packet.py` already treats any public-fingerprint warning as invalid in strict policy mode, so a same-selector packet with symlinked public bytes now reaches:

```text
authentication_status: SIGNATURE_FAILED
problem: signature_verification_policy_lockfile_packet_fingerprint_invalid
```

## Profile bump

Because this changes public-fingerprint inclusion-safety semantics, the helper profile advances from `1.0` to `1.1`. The strict rev0859 verification-policy lockfile and its publication receipt both bind:

```text
packet_public_fingerprint_profile: 1.1
packet_public_fingerprint_sha256: sha256:a0d2485f3e8746cf8cdeae8017278046d4b9c409788d8dc07c03c03c2d3f6346
```

The digest for the current non-symlinked threshold fixture is unchanged; the profile changed because the helper's warning/fail-closed semantics changed.

## Non-claims

This is still synthetic verifier hardening. It does not prove production filesystem sandboxing, legal signer authority, live online revocation freshness, current voter instruction, certification, or live-pilot readiness.
