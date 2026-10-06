# Devfs view diff as a drift surface (review /dev authority changes)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, reproducibility
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD treats device nodes as **authority**.
Even a “locked down” jail or microVM can be effectively compromised if it unexpectedly gains access to powerful `/dev` nodes:

- packet capture (`bpf`)
- raw storage (`da*`, `ada*`, `nvd*`, …)
- input devices (HID injection)
- GPU/control ioctls

DeriveBSD already models `/dev` views as a derived operation:

- `devfs.view.plan` (portable IR rules)
- `devfs.view.receipt` (what was applied + what was observed)
- `devfs.view.event` (drift/deny incidents)

See: `docs/323-devfs-views-plans-and-receipts.md`.

What was missing was a compact review surface for **posture drift**:

> “Did this compartment’s `/dev` exposure expand between generations?”

This doc introduces a single, stable diff artifact that makes `/dev` authority drift **gateable** and **bundle-friendly**.

## The artifact: `devfs.view.diff`

`devfs.view.diff` compares two `devfs.view.plan` objects (by digest) and produces a compact, deterministic summary of changes:

- baseline posture drift (`service-minimal` → `interactive-minimal`, etc.)
- rules added / removed
- permission/ownership changes (when expressed as `perm` rules)
- optional `risk_flags` suitable for review UI + policy gates

Schema: `spec/devfs.view.diff.schema.json`
Example: `spec/examples/devfs.view.diff.json`

### Noise rule (keep this surface stable)

`devfs.view.diff` is intentionally a **high-signal summary**.

- It should not embed full device inventories.
- Raw node lists belong in `devfs.view.receipt` (under retention/export policy).
- Drift incidents belong in `devfs.view.event`.

This keeps the diff surface stable and avoids privacy surprises in review bundles.

## Where it plugs in

### 1) Drift bundles

When a unit’s devfs view digest changes between generations, attach `devfs.view.diff` next to other posture diffs.

See: `docs/395-drift-bundles-and-review-summaries.md` and the canonical registry `docs/430-diff-surface-registry.md`.

### 2) Evidence spine

Least-authority posture should be explainable:

- the devfs view plan digest used
- the apply receipt
- the drift diff when posture changes

See: `docs/229-evidence-spine-overview.md`.

### 3) Gates (profile/policy controlled)

Profiles can gate on the summary and/or risk flags:

- raw storage exposed → require two-person integrity in strict profiles
- packet capture exposed → require explicit approval
- input/HID exposed → require approval and an export-safe incident note

Gates should start simple and conservative.
If more nuance is needed later, add additional reason codes (don’t overload a single flag).

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):

- `devfs-raw-disk-exposed`
- `devfs-bpf-exposed`
- `devfs-input-exposed`
- `devfs-perms-relaxed`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References (primary primitives)

- devfs rulesets: https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5
- jail devfs warning (device exposure is authority): https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=8

Last updated: 2026-02-28r171
