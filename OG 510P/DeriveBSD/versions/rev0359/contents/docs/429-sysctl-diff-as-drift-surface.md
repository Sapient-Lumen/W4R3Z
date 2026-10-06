# Sysctl diff as a drift surface (review kernel knob changes)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, reproducibility
**Patterns:** Plan→Receipt, Registry→Diff→Gate, Bundles

DeriveBSD already treats kernel knob mutation as a derived operation:

Profile default note: the review surface now plugs into `docs/475-kernel-mutation-posture-by-profile.md`, which fixes when runtime kernel mutation is normal, maintenance-shaped, or out of bounds across A–D.
`sysctl.plan` (intent) → `sysctl.receipt` (result) with drift events (`sysctl.event`).

The missing review surface is: **what kernel knob posture changed between two generations**.
Without a compact diff object, reviewers end up spelunking plans/receipts by hand and the most security-relevant deltas (“routing was enabled”, “hardening flipped”, “lockdown changed”) become folklore.

This doc introduces a single, stable diff artifact that makes planned sysctl posture changes **gateable** and **exportable**.

## The artifact: `sysctl.diff`

`sysctl.diff` compares two sysctl plans (by digest) and produces a compact, deterministic drift surface:

- sysctl keys added / removed
- sysctl keys with changed planned values
- an optional `risk_flags` set suitable for review UI and policy gates

Schema: `spec/sysctl.diff.schema.json`  
Example: `spec/examples/sysctl.diff.json`

### Why a diff object (instead of “just look at the plans”)

Plans answer *what we intend to set*.
Diffs answer *what changed and why should I care*.

A good kernel knob workflow needs both:

- **Plans/receipts/events** for durable evidence and live drift alarms.
- **Diffs** for review ergonomics, alerting, and promotion gates.

### Noise rule (keep the diff surface stable)

`sysctl.diff` is intentionally **not** a full `sysctl -a` inventory.
It only covers the planned keyset from `sysctl.plan`.

If a future lane needs inventory coverage, add it as a separate *inventory/snapshot* artifact (not by bloating this diff surface).

## Where it plugs in

### 1) Drift bundles (one review attachment)

A sysctl diff is a natural drift surface:

- attach `sysctl.diff` to `drift.bundle` whenever the planned sysctl set changes between generations,
- keep it adjacent to other operator-facing drift surfaces (`authority.diff`, `etc.config.diff`, `fw.inventory.diff`).

See: `docs/395-drift-bundles-and-review-summaries.md`.

### 2) Evidence spine (kernel mutation is evidence)

Kernel knob posture belongs in the evidence spine alongside config transactions and runtime posture changes.

See: `docs/229-evidence-spine-overview.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`.

### 3) Policy gates

Policy can require a `sysctl.diff` in higher-assurance lanes:

- any change to “security posture” sysctls (hardening, routing, debugging toggles)
- fleet hosts with strict lockdown policies
- regulated appliance build/promotion workflows

Gates can start simple:

- fail promotion if `risk_flags` includes `kernel-posture-changed` without required approvals
- require explicit acknowledgement if `risk_flags` includes `lockdown-level-changed`

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):

- `lockdown-level-changed`
- `kernel-posture-changed`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References (primitives)

- FreeBSD sysctl(8): https://man.freebsd.org/cgi/man.cgi?query=sysctl&sektion=8
- FreeBSD sysctl.conf(5): https://man.freebsd.org/cgi/man.cgi?query=sysctl.conf&sektion=5

Last updated: 2026-03-06r204
