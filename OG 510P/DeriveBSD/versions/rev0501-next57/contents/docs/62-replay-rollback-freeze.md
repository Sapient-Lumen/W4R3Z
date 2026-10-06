# Replay, rollback, and freeze attacks (threats + mitigations)

Threats:
- rollback: old valid artifact
- freeze: no updates
- mix-and-match: inconsistent metadata views

Mitigations:
- verify digests + signatures (`adrs/ADR-0009-artifact-verification.md`)
- TUF-inspired channel metadata (`docs/61-channel-metadata-tuf-inspired.md`)
- optional transparency logs (`docs/59-transparency-log-rekor.md`)

Reference:
- TUF spec’s explicit rollback/freeze checks (monotonic versions + expiry): https://theupdateframework.github.io/specification/latest/

Rollback overrides must be explicit, logged, and policy-governed.

## DeriveBSD interpretation (tight)

1) **“Signed” is not enough**

If an attacker can replay an older signed view, you can be stuck on a vulnerable version forever.

2) **Clients must persist *state***

At minimum:
- highest `channel.root.version` accepted
- highest `channel.timestamp.version` accepted
- last accepted `channel.timestamp.expires_at` and the fixed update-start time

3) **Policy-only escape hatches**

Any rollback must produce a `policy.decision` that:
- states why a rollback is allowed
- binds to the exact artifact digest(s) being rolled back to
- is attached to the deployment record so it remains reviewable

Last updated: 2026-02-23
