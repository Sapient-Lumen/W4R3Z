# RFC-0132: Time + entropy as authority (determinism, testing, and replay)

Status: draft

## Motivation

DeriveBSD aims for deterministic-by-default builds and explainable systems.
Time and randomness are major sources of nondeterminism, policy ambiguity, and cross-compartment leakage.

We already treat *trustworthy wall clock for verification* as a policy-governed input (see `docs/142-trustworthy-time-roughtime.md`).
This RFC extends the same mindset into the runtime: *who may observe what time/entropy, and under what constraints?*

## Proposal

1. Define a signed, leased evidence object: `time.authority.grant`.
2. Define a lightweight receipt: `time.snapshot`.
3. Require that deterministic build/test environments run under an explicit time/entropy profile.
4. Encourage (optional) per-compartment virtual clocks.

## `time.authority.grant` semantics

A grant binds:

- subject identity (service/workload digest)
- context (plan digest, policy snapshot digest, policy decision digest)
- permissions:
  - wall clock: deny | read | bounded
  - monotonic: read (always) with optional virtualization offset
  - entropy: real | deterministic | recorded
- lease duration (issued/expires)

### Deterministic mode

If entropy is `deterministic`, the grant includes a `seed_digest` derived from:

- plan digest
- policy snapshot digest
- optional domain separation string (e.g., "build", "test")

Seeds are never logged in raw form; only digests.

## `time.snapshot` receipt

A snapshot records the realized runtime time profile:

- grant digest
- the effective clock profile digest (including offsets)
- entropy mode and seed digest
- any adjustments made during the run

## Virtual clock mechanism (optional)

DeriveBSD may implement a virtual clock per jail/microVM as an affine transform of a monotonic reference.
This follows patterns used in:

- Linux time namespaces (offsets)
- Fuchsia clock objects (privileged maintainer adjusts a shared clock)

The v0 evidence objects do not require a specific kernel mechanism; they define the contract needed by higher layers.

## Interaction with record/replay

Replay capsules should embed:

- the time authority grant digest
- the time snapshot digest

and be able to restore deterministic time/entropy behavior.

## Open questions

- Is a jail-scoped virtual clock sufficient, or do we need finer granularity?
- How to expose virtual time to unmodified binaries: vDSO hook, libc shim, or microVM-only?
- Which ops are allowed to request wall clock via portals vs pre-derived grants?

