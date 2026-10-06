# Removable-media local fallback post-detach state machine and post-expiry ledgers are runtime-verifiable

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r520 made expired compacted reader-use ledger roots deny with a typed, redacted enforcement receipt. r521 turns the broader lifecycle into a runtime-verifiable spine. The new posture token is `runtime-verifiable-post-detach-state-machine-and-post-expiry-ledgers`: post-detach authority is now described as a state machine with computed digest joins, explicit denial precedence, committed enforcement-ledger roots, rate-limit ledger binding, trustworthy-time carry-forward, an allowlisted support projection, a positive fresh-authority recovery path, and FreeBSD backend enforcement evidence.

See also:

- ADR: `adrs/ADR-0365-removable-media-local-fallback-post-detach-state-machine-and-post-expiry-ledgers-are-runtime-verifiable.md`
- state-machine manifest schema: `spec/removable.media.local.post_detach.state_machine.manifest.schema.json`
- state-machine manifest example: `spec/examples/removable.media.local.post_detach.state_machine.manifest.json`
- enforcement ledger schema: `spec/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.schema.json`
- enforcement ledger example: `spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json`
- fresh-authority recovery schema: `spec/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.schema.json`
- support projection schema: `spec/removable.media.local.post_detach.support.projection.schema.json`
- backend evidence schema: `spec/removable.media.local.post_detach.backend.enforcement.evidence.schema.json`
- checker: `tools/check_removable_media_local_post_detach_runtime_state_machine.py`
- README front-door checker: `tools/check_readme_latest_cut.py`
- current lifecycle view: `docs/current/removable-media-post-detach-lifecycle.md`
- current denial matrix: `docs/current/removable-media-post-detach-denial-matrix.md`
- current digest joins: `docs/current/removable-media-post-detach-digest-joins.md`
- current redaction surfaces: `docs/current/removable-media-post-detach-redaction-surfaces.md`

## Decision

The ordinary B/C removable-media local fallback now carries `runtime-verifiable-post-detach-state-machine-and-post-expiry-ledgers` after `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded`.

The r521 state-machine manifest records the lifecycle from r504 through r521 as explicit states and transitions. It also records the lane identity rule: `lane_family` is `removable-media-local-fallback`, while the dotted artifact kind `removable.media.local.post_detach.*` marks the post-detach phase. The drifted alias `removable-media-local-post-detach` is retired and only appears in the manifest's retired-alias list.

## New artifact families

### State-machine manifest

`removable.media.local.post_detach.state_machine.manifest` is the current graph. It lists states, predecessor requirements, transitions, current docs, denial precedence, invariants, and computed canonical example digests. The manifest does not claim old placeholder digest fields are magically real; it makes the r521 join rule explicit: new state-machine joins use computed canonical JSON example digests, while old repeated placeholder digests remain legacy fixture fields.

### Post-expiry enforcement ledger

`removable.media.local.post_detach.expiry.enforcement.ledger.receipt` binds the r520 denial to an enforcement root. It carries:

- prior enforcement root;
- expected CAS root;
- new enforcement root;
- enforcement root anchor;
- monotonic sequence;
- broker epoch;
- idempotency key digest;
- replay outcome;
- rollback/fork/stale-root rejection;
- denial kind/schema/digest/reason code/precedence;
- rate-limit subject, policy, window, debit, retry-not-before, debit receipt, and prior/new rate-limit roots;
- time proof that `attempt_observed_at >= expiry_observed_at >= retention_expires_at`;
- support projection and backend evidence bindings.

### Fresh-authority recovery

`removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt` is the positive path after an expired-root denial. It proves that fresh authority was present, consumed once, not widened, and bound to a successor root. The expired root remains terminal; only the successor root may be admitted for new observation/export/rehydration.

### Support projection

`removable.media.local.post_detach.support.projection` is an allowlist, not a forbidden-token blacklist. Support-visible fields are reason code, state label, digest facts, bounded retry guidance, and fresh-authority instruction. Raw path, raw locator, raw handle, filename, host identity, body text, full text, and secret material are represented only as false forbidden-surface booleans.

### FreeBSD backend enforcement evidence

`removable.media.local.post_detach.backend.enforcement.evidence` makes the implementation proof concrete enough to review. It records devfs ruleset digest, mount-table evidence digest, fd inventory digest, Capsicum capability-mode entry, limited `cap_rights`, retained-fd-rights digest, Casper-service posture, jail/VNET posture, worker reaping, detach race outcome, and absence of raw path/device reopen authority.

## r520 production/fixture split

The r520 enforcement receipt now has two validation surfaces:

- `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json` is the production contract. IDs, timestamps, digest values, and monotonic sequence values can vary while the required denial/redaction/rate-limit/fresh-authority semantics stay fixed.
- `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.fixture.schema.json` is the exact golden fixture schema for the canonical r520 example.

The r521 checker mutates the r520 positive example into a dynamic valid receipt. The production schema accepts it; the exact fixture schema rejects it. That is the point: runtime receipts should not have to be clones of a single example.

## Red corpora

r521 adds red corpora for:

- state-machine manifest drift: wrong lane alias, missing computed join, support projection not allowlisted, fresh-authority recovery not successor-only, degraded time not fail-closed;
- enforcement ledger drift: CAS expected-root mismatch, missing denial reason, missing rate-limit debit, degraded-clock warn-only, raw support leak, stale-root acceptance;
- fresh-authority recovery drift: absent fresh authority, reused authority, widened scope, expired-root resurrection, successor root equal to expired root, expired root admitted;
- support projection drift: raw path visible, raw locator field, filename field, full-text visibility, secret visibility;
- backend evidence drift: Capsicum missing, fd rights broad, raw path reopen authority, devfs node visible, worker not reaped.

## Implementation rule

The behavioral floor is now: an expired compacted root cannot be queried, exported, rehydrated, debugged through raw support output, or recovered into the same root. It can only produce a typed denial/enforcement ledger path, or a fresh-authority success path that creates or binds to a successor root.

## Hygiene

Run `tools/check_removable_media_local_post_detach_runtime_state_machine.py`. It validates positive examples, proves red corpora fail by schema or semantic checks, computes manifest example digests, checks the r520 production/fixture split, checks lane-family normalization, and verifies the post-expiry denial/recovery/support/backend joins.

Last updated: 2026-05-30r521
