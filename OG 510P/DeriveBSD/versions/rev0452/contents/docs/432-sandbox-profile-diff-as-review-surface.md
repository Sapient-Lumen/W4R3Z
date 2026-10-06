# Sandbox profile diff as a drift surface (review least-authority changes)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, reproducibility
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD already has a “pledge/unveil mindset” expressed as typed sandbox promise profiles (`sandbox-profile`).
They are the ergonomic on-ramp to least authority:
- human-readable promises
- explicit filesystem allowlists
- brokered network classes
- explicit portal surfaces
- optional Capsicum/Casper affordances

The missing review surface is: **what sandbox posture changed between two profile revisions or generations**.
Without a compact diff object, reviewers end up scanning raw profile JSON and subtle authority expansion (“new egress class”, “filesystem exec allowed”, “new portal”) becomes easy to miss.

This doc introduces a single, stable diff artifact that makes sandbox profile changes **gateable** and **exportable**.

## The artifact: `sandbox.profile.diff`

`sandbox.profile.diff` compares two sandbox profiles (by digest) and produces a compact, deterministic drift surface:

- promises added / removed
- filesystem rule deltas (added / removed / mode-changed)
- network class deltas (egress + listen)
- portal surface deltas
- Casper service deltas (when used)
- optional `risk_flags` suitable for review UI + policy gates

Schema: `spec/sandbox.profile.diff.schema.json`  
Example: `spec/examples/sandbox.profile.diff.json`

### Why a diff object (instead of “just look at the profiles”)

Profiles answer *what the sandbox intends to allow*.
Diffs answer *what changed and why should I care*.

A good least-authority workflow needs both:
- **Profiles** for durable intent (and compilation to enforcement like capsets, mounts, brokers).
- **Diffs** for review ergonomics, alerting, and promotion gates.

### Noise rule (keep the diff surface stable)

`sandbox.profile.diff` is intentionally a **high-signal summary**, not a full runtime attestation.
Runtime enforcement evidence belongs elsewhere (activation receipts, capset digests, policy traces, attestations).

If a future lane needs enforcement attestation, add it as a separate *receipt/snapshot* artifact (do not bloat this diff surface).

## Where it plugs in

### 1) Drift bundles (one review attachment)

Sandbox profiles are security posture.
When a unit’s sandbox profile digest changes between generations, attach `sandbox.profile.diff` to the `drift.bundle` next to other operator-facing drift surfaces.

See: `docs/395-drift-bundles-and-review-summaries.md` and `docs/430-diff-surface-registry.md`.

### 2) Evidence spine (least authority is evidence)

Least-authority posture should be explainable:
- the sandbox profile digest used
- the derived enforcement artifacts (capsets, mounts, broker leases)
- the drift diff when posture changes

See: `docs/229-evidence-spine-overview.md`, `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`.

### 3) Policy gates

Policy can require a `sandbox.profile.diff` in higher-assurance lanes:
- any new `promises` token (authority family expansion)
- any filesystem rule that adds `x` (execute) or `rw` to previously read-only paths
- any new egress/listen class
- any new portal surface

Gates can start simple:
- fail promotion if `risk_flags` includes `new-portal-surface` without explicit approval
- require explicit approval if `risk_flags` includes `fs-execute-added`
- require two-person integrity if `risk_flags` includes `new-net-egress` in fleet host profiles

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):

- `new-net-egress`
- `fs-execute-added`
- `new-portal-surface`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References (mindset primitives)

- OpenBSD pledge(2): https://man.openbsd.org/pledge.2
- OpenBSD unveil(2): https://man.openbsd.org/unveil.2
- FreeBSD capsicum(4): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4

Last updated: 2026-02-28r155
