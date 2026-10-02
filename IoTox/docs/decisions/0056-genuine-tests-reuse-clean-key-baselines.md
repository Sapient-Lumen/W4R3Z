# ADR 0056 — Genuine tests reuse clean test-only key baselines by default

- Status: accepted for repository test policy
- Date: 2026-08-15 America/New_York
- Preserves: identity separation in ADR 0030 and the full genuine lifecycle gates

## Context

The genuine-peer harness previously created and destroyed two Tox savedata identities and two
stable device identities on every invocation. That is a useful clean-room proof, but it makes the
ordinary laboratory identity unstable and prevents repeated observations of the same test peers.
The mock provider already has deterministic transport identity, RecallRoot uses fixed test-fixture
phrases, and focused creation/tamper tests correctly generate isolated identities for their own
contracts.

Reusing an entire completed genuine-peer profile is unsafe and invalid as a test shortcut. The
lifecycle deliberately adds and removes friendship, grants and revokes principals, changes owner
epochs, and commits commands. Starting from that mutated profile would make later outcomes depend
on test history.

## Decision

The genuine-peer harness defaults to `reuse` key mode. It maintains one private, test-only pair of:

```text
Tox savedata baseline
stable device identity
```

The cache is namespaced by the pinned c-toxcore version and excluded from Git, packages, retained
evidence, and conversation datacubes. On first use, the harness provisions each peer in an isolated
private directory, stops it cleanly, and atomically publishes only those four files. Existing caches
must contain exactly those files under owned `0700` directories with nonsymlink, nonempty `0600`
files. The peer baselines must be distinct.

Every actual run copies the cached files into a new disposable work directory. It creates fresh
authority ledgers, command stores, runtimes, and file/message state, and rejects a savedata baseline
that exposes any pre-existing friend or request. A nonblocking whole-run lock prevents concurrent
public-network use of the same test identities. A digest check proves the immutable cache was not
changed by the run.

`--fresh-keys` (or `IOTOX_REAL_PEER_KEYS=fresh`) retains generation from scratch as an explicit
qualification gate. Release/network qualification runs both the ordinary reused-baseline lifecycle
and at least one fresh-key lifecycle. Focused tests whose subject is key creation, persistence,
replacement, or tamper handling continue to create isolated material; they do not consume this
cache.

The cache is never a production identity store. Operators must not seed it from a live profile,
point it at customer state, share it, or treat its survival as backup. Earlier disposable genuine
test keys were intentionally destroyed and are not recoverable from redacted evidence.

## Consequences

- Ordinary genuine testing observes stable test peer identities across runs.
- Each run remains logically clean and repeatable above the identity layer.
- First use creates new test keys; later uses are byte-stable until the cache is deliberately
  replaced or the provider-version namespace changes.
- Concurrent reused-key runs fail closed instead of presenting one Tox identity from two processes.
- Fresh generation remains slower but continues to catch first-boot and persistence defects.
- Private test material remains local and absent from every distributable artifact.

## Rejected alternatives

- **Reuse completed work directories:** imports friendship, authority, and command history.
- **Commit private fixture keys:** publishes impersonation material and makes forks collide.
- **Use live/production keys:** the harness intentionally performs destructive authority and
  friendship transitions.
- **Make every test consume one shared cache:** breaks hermetic unit/process concurrency and weakens
  tests whose subject is identity creation or corruption.
- **Silently repair malformed caches:** can hide substitution, permission, or partial-write defects.
