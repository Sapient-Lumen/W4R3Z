# Cargo Install Policy & Cooldown Kit fixtures

These fixtures are for **P-0056 Cargo Install Policy & Cooldown Kit**.

The point is to freeze the policy layer above installer substrate:

- install-policy files,
- dry-run plans,
- cooldown reports,
- and install receipts.

These fixtures should stay distinct from:

- workspace tool manifests and runner receipts,
- rustup compiler/toolchain policy,
- and publish-surface rehearsal or post-publish release receipts.

Scenario families in this pass:
- `packaged_lock_requires_locked/`
- `pubtime_cooldown_block/`
- `git_source_age_unknown/`
- `no_track_disallowed/`
