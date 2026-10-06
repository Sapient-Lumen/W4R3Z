# Kernel module policy diff as a drift surface (review privileged code injection)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, supply-chain, operability, reproducibility
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate, Bundles

DeriveBSD already treats kernel module loading as a planned, receipted operation:
`kmod.load.plan` → `kmod.load.receipt` (+ `kmod.event`).

The missing review surface is: **what changed in the policy that governs which privileged code may enter the kernel**.
Without a compact diff object, reviewers end up reading signed policy blobs by hand, and high-leverage posture changes ("runtime loads enabled", "new driver class allowed", "denylist removed") become folklore.

This doc introduces `kmod.policy.diff`: a stable, deterministic-by-default artifact that makes kernel module policy drift **gateable** and **exportable**.

## The artifact: `kmod.policy.diff`

`kmod.policy.diff` compares two `kmod-policy` objects (by digest) and produces a compact drift surface:

- default posture changes (`allow_runtime_load`, `allow_unload`, `deny_unknown`)
- allow/deny rule additions/removals
- rule changes (effect/match/constraints)
- optional `risk_flags` suitable for review UI and policy gates

Schema: `spec/kmod.policy.diff.schema.json`  
Example: `spec/examples/kmod.policy.diff.json`

### Why a diff object (instead of “just look at the policy”)

Policies answer **what is allowed**.
Diffs answer **what changed and why should I care**.

A good module workflow needs both:

- **Policy + load plan + receipt** for durable evidence and attribution.
- **Diffs** for review ergonomics, alerting, and promotion gates.

## Where it plugs in

### 1) Drift bundles (one review attachment)

Attach `kmod.policy.diff` to `drift.bundle` whenever the governing module policy digest changes between generations.
Keep it adjacent to other posture diffs:

- `/etc` drift (`etc.config.diff`)
- firmware/platform drift (`fw.inventory.diff`)
- boot-critical drift (`boot.manifest.diff`)
- sysctl posture drift (`sysctl.diff`)

See: `docs/395-drift-bundles-and-review-summaries.md`.

### 2) Evidence spine (kernel mutation is evidence)

Kernel module allow/deny posture is part of the evidence spine:

- what policy was in force
- what modules were loaded during activation
- whether runtime loads were allowed

See: `docs/229-evidence-spine-overview.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`.

### 3) Policy gates

High-assurance profiles can gate promotion on `kmod.policy.diff`:

- enabling runtime loads (`allow_runtime_load: false → true`)
- removing a deny rule for a risky class (storage/usb/debug)
- broadening match scope (e.g., adding `name_regex` where an exact `name` existed)

Gates can start boring:

- require explicit approval when `risk_flags` includes `kmod-policy-runtime-load-enabled`
- require two-person integrity in regulated lanes when policy drift includes any `kmod-policy-rule-removed`

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):

- `kmod-policy-runtime-load-enabled`
- `kmod-policy-rule-added`
- `kmod-policy-rule-removed`

Also consider emitting `kernel-posture-changed` when any kernel mutation posture surface changes.

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## Noise rule (stable diff surface)

`kmod.policy.diff` is intentionally scoped to **policy drift**, not observed runtime state.
Observed module load/unload events remain the job of:

- `kmod.load.receipt` / `kmod.event`

If you need an observed inventory/snapshot, add it as a separate snapshot/report artifact (do not bloat this diff).

## References (primitives)

- FreeBSD kldload(8): https://man.freebsd.org/kldload
- FreeBSD kldunload(8): https://man.freebsd.org/kldunload
- FreeBSD kldstat(8): https://man.freebsd.org/kldstat

Last updated: 2026-02-28r158
