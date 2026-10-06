# ADR-0365: Removable-media local fallback post-detach state machine and post-expiry ledgers are runtime-verifiable

## Status

Accepted.

## Context

r504 through r520 made the removable-media local fallback post-detach lane progressively typed: contract, launch evidence, recovery, query projection, export bundle, tombstone, denial, fresh authority, fresh-authority consumption, successor-index cutover and checkpoint, reader admission, reader use, reader-use ledger, bounded retention, retention expiry, and expiry enforcement. That sequence was correct, but it still left too much of the lifecycle distributed across append-only prose and golden fixtures.

The missing spine was a machine-readable state graph: which state may follow which predecessor, which digest joins are computed rather than symbolic, which denial reason wins when several failures are true, which support/debug facts are allowlisted, and which FreeBSD backend controls make the denial real rather than a broker log story. r520 also made the expired-root denial visible, but its enforcement receipt still needed a committed enforcement-ledger root, rate-limit ledger binding, time proof, and a positive post-expiry fresh-authority recovery path.

## Decision

Add a runtime-verifiable post-detach state-machine cut for the ordinary B/C removable-media local fallback. The new posture token is `runtime-verifiable-post-detach-state-machine-and-post-expiry-ledgers`.

This cut adds:

- `spec/removable.media.local.post_detach.state_machine.manifest.schema.json` and `spec/examples/removable.media.local.post_detach.state_machine.manifest.json` as the current state graph from r504 through r521;
- `spec/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.schema.json` and its example/red corpus so r520 denials commit to a monotonic enforcement ledger root with CAS, rate-limit debit, denial reason precedence, and time proof;
- `spec/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.schema.json` and its example/red corpus so a successful post-expiry path consumes fresh authority and admits only a successor root, never the expired root;
- `spec/removable.media.local.post_detach.support.projection.schema.json` and its example/red corpus as the allowlisted support/debug projection for expired-root denials;
- `spec/removable.media.local.post_detach.backend.enforcement.evidence.schema.json` and its example/red corpus for FreeBSD controls: devfs/mount/fd evidence, Capsicum capability mode, cap-rights limiting, Casper posture, jail/VNET posture, worker reaping, and absence of raw path/device reopen authority;
- `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.fixture.schema.json` so the r520 golden example remains exact while the sibling production schema now accepts runtime-shaped IDs, timestamps, digest values, and monotonic sequence values;
- `tools/check_removable_media_local_post_detach_runtime_state_machine.py` for semantic joins that JSON Schema cannot express;
- `tools/check_readme_latest_cut.py` so the first README screen cannot drift behind the newest ADR/changelog cut.

The lane-family drift introduced by the r518-r520 retention/expiry/enforcement examples is normalized: these artifacts now use `lane_family = removable-media-local-fallback`. The `post_detach` kind path remains the phase marker; the retired alias `removable-media-local-post-detach` is recorded only in the state-machine manifest's retired-alias section.

## Consequences

- The removable-media post-detach lifecycle is now queryable as a state machine rather than only recoverable from release chronology.
- r520 expired-root enforcement has a committed enforcement ledger root: prior root, expected CAS root, new root, root anchor, broker epoch, idempotency key, and replay posture are typed.
- Denial receipts are bound by reason code and precedence: `expired-ledger-root-fresh-authority-required` wins over stale-root/missing-fresh-authority subordinate causes after the expiry receipt is present.
- Rate limiting is no longer a boolean: subject digest, policy digest, window id, debit amount, retry-not-before, debit receipt, and rate-limit prior/new roots are carried.
- Time proof is carried forward from r519: attempts must be observed after expiry observation, which must be observed after the retention end; degraded or unavailable clocks fail closed.
- Support/debug output becomes allowlist-based. Raw paths, locators, handles, filenames, host identity, body text, full text, and secret material stay outside the support projection.
- FreeBSD backend proof is first-class enough for implementation review: Capsicum/devfs/mount/fd/Casper/jail/VNET/reap evidence can be checked without claiming that the schema alone enforces kernel behavior.
- Existing symbolic fixture digest fields remain as historical placeholder facts where they already existed, but new r521 state-machine joins record computed canonical example digests.

## Validation

Run:

```text
python3 tools/check_readme_latest_cut.py
python3 tools/check_removable_media_local_post_detach_runtime_state_machine.py
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_runtime_state_machine.py` validates the new positive examples, proves the red corpora fail by schema or semantic checks, verifies computed digest joins in the state-machine manifest, checks r520 production-vs-fixture schema split, proves lane-family normalization, and checks the non-circular post-expiry recovery/support/backend joins.

Last updated: 2026-05-30r521
