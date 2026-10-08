# 887 — Public-fingerprint symlink surface audit and profile-bump refactor

**Track:** Shared / Verification / Audit
**Status:** v859 generated audit and release-surface refactor

rev0859 adds a focused audit for the public-fingerprint helper because that helper now sits in the strict synthetic authentication path. The audit keeps the change bounded: one helper profile bump, one strict policy fixture refresh, one symlink negative control, and no new trust-chain bureaucracy.

## Audit result

Current positive fixture:

```text
packet: artifacts/examples/evidence_packet_ed25519_threshold2_minimal
policy: artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0859.json
policy receipt: artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0859.publication-receipt.json
public fingerprint profile: 1.1
public fingerprint warnings: 0
authentication_status: SIGNATURE_VERIFIED
```

Current symlink negative control:

```text
same selector: true
public README surface replaced with symlink: true
public fingerprint warning count: 1
authentication_status: SIGNATURE_FAILED
```

Generated reports:

```text
artifacts/reports/public-fingerprint-symlink-surface-audit-rev0859.md
artifacts/reports/public-fingerprint-symlink-surface-audit-rev0859.json
artifacts/reports/verification-policy-lockfile-scope-rev0859.json
artifacts/reports/trust-chain-fixture-surface-rev0859.json
```

## Refactor value

This keeps the replay guard from becoming brittle. The packet-public-fingerprint digest is now bound to both:

```text
1. the packet's bounded public bytes
2. the helper profile that defines warning/fail-closed semantics
```

That is the minimum useful change: the verifier rejects symlink-tainted public surfaces without expanding the trust-chain fixture family.
