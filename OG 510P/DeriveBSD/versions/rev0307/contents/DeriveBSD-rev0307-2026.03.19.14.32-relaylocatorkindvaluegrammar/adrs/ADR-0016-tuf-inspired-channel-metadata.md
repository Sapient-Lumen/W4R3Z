# ADR-0016: Adopt TUF-inspired channel metadata

- Status: proposed
- Date: 2026-02-25

## Context

Signed artifacts alone do not prevent:
- **rollback** (serve an older-but-valid generation)
- **freeze** (serve stale metadata forever)
- **mix-and-match** (serve mutually inconsistent metadata/artifacts)

TUF’s core value is its *client-side verification rules* (expiry + monotonic versions + consistent snapshot binding + root/key-rotation ergonomics).

References:
- TUF overview: https://theupdateframework.io/docs/overview/
- TUF spec (latest): https://theupdateframework.github.io/specification/latest/

## Decision

DeriveBSD adopts a **minimal TUF-shaped channel metadata model**.

Each channel publishes **pure data** objects, signed under a role-separated key hierarchy:

1) `channel.root`
- Long-lived root of trust: keys + thresholds for the other roles.
- Has a monotonic `root_version`.
- Supports explicit key rotation.

2) `channel.timestamp`
- Short-lived, frequently updated “heartbeat”.
- Has an `expires_at` (anti-freeze).
- Indicates the current `snapshot` version/digest.

3) `channel.snapshot`
- Binds the complete set of *current* metadata versions/digests.
- Enables “consistent snapshot” semantics: the client must fetch exactly what the snapshot binds.

4) `channel.targets`
- Human-facing mapping of names → artifact digests, plus metadata needed for selection/policy.
- Optional delegations live here in the “full adapter” interop lane.

The client MUST enforce these invariants:

- **Expiry**: reject expired `timestamp`/`snapshot`/`targets` relative to a fixed update-start time.
- **Monotonic versions**: persist the highest accepted version per role; refuse lower versions.
- **Consistency**: only accept metadata/artifacts whose digests match what the snapshot/targets bind.
- **Root safety**: reject unexpected root version jumps; require sequential root updates unless policy-authorized.

All verification steps MUST emit structured evidence so `derive explain` can show:
- which metadata was used
- which keys/thresholds were required
- why acceptance succeeded or failed

## Consequences

- Operators need a clear key-management story (thresholds + offline root keys).
- Expiry requires trustworthy time (see `docs/142-trustworthy-time-roughtime.md`).
- A minimal model stays small, but we keep an optional interop lane:
  - full TUF repository publication/ingestion (`docs/203-full-tuf-metadata-adapter.md`)
  - Uptane-style assignment separation for fleets (`docs/127-uptane-director-targets.md`)

