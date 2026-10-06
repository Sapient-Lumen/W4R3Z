# Channel metadata and anti-freeze protections (TUF-inspired)

Even with signed artifacts, update systems face:
- **rollback** attacks (serve older-but-valid artifacts/metadata)
- **freeze** attacks (serve stale metadata indefinitely)
- **mix-and-match** inconsistencies (different parts of the “view” don’t match)

TUF exists largely to address these classes of failures.

References:
- TUF specification (latest): https://theupdateframework.github.io/specification/latest/
- TUF security overview (attack classes): https://theupdateframework.io/docs/security/

## DeriveBSD direction (minimal, sufficient)

DeriveBSD doesn’t need to copy TUF wholesale to benefit from its *client-side rules*.
We can adopt a small set of invariants for signed **channel metadata** (see ADR-0016):

### Invariants the client MUST enforce

1) **Expiry / heartbeats**
- Every channel view includes an `expires_at`.
- The client rejects metadata that is expired *relative to a fixed update-start time* (anti-freeze).

Time note: expiry is only meaningful if the client has **trustworthy time**.
High-assurance channels should require a fresh `time-sync-snapshot` (optionally backed by a `time-proof-bundle`) before evaluating expiry.
See: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`, `docs/200-secure-time-bootstrapping.md`.

2) **Monotonic versions (anti-rollback)**
- Every channel view includes a `version`.
- The client persists the highest accepted version and refuses lower ones.

3) **Consistent snapshot binding (anti mix-and-match)**
- The channel view binds:
  - artifact target digests (or a snapshot digest over them)
  - delegated metadata digests (if any)
- The client verifies the bound digests exactly match what it fetches.

4) **Key rotation without bricking**
- A “root of trust” record supports threshold signing and explicit version bumps.
- The client rejects non-sequential root version jumps (rollback detection) unless an operator override is policy-authorized.

## What this looks like in DeriveBSD terms

- `channel.root` (long-lived, rarely updated): trusted keys + thresholds + root version
- `channel.snapshot` (binds the set of target manifests and their versions)
- `channel.timestamp` (short-lived heartbeat / anti-freeze)
- `channel.targets` (the human-facing mapping: name → artifact digest, with metadata)

We keep these as **pure data**, and make the verification steps emit structured evidence so `derive explain` can show *exactly why* a channel view was accepted or rejected.

See RFC-0038 and ADR-0016.
\
Optional interop lane: if we want full TUF repository compatibility and delegations, see `docs/203-full-tuf-metadata-adapter.md`.

Last updated: 2026-02-26
