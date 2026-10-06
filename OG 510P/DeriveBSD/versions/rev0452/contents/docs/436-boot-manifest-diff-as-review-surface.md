# Boot manifest diffs as a review surface (boot.manifest.diff)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability, isolation
**Patterns:** Registry→Diff→Gate, Bundles

Boot-critical bytes are a **trust boundary**:
- kernel + modules
- loader/shim/boot config
- activation/init plumbing
- cmdline profiles

DeriveBSD already treats the activated generation as a content-addressed closure.
A `boot-manifest` is the **human-friendly, boot-focused projection** of that closure.

This doc makes boot manifest drift **mechanically reviewable** by introducing a typed diff surface:

- Schema: `spec/boot.manifest.diff.schema.json`
- Example: `spec/examples/boot.manifest.diff.json`

## What it compares

`boot.manifest.diff` compares two `boot-manifest` objects and emits stable, deterministic lists of:
- `components_added`
- `components_removed`
- `components_changed`

The diff is keyed by component role (and optionally `path_key` when a role is repeated).

## Why this exists (pillars)

- **Reproducibility / derivation-first:** upgrades should surface the *exact* boot-critical digests that changed.
- **Supply-chain integrity:** boot-critical drift becomes a typed artifact that can be attached to promotion decisions.
- **Operability + forensics UX:** “what did we actually boot?” becomes explainable (diffs + manifests + receipts).
- **Isolation:** cmdline/profile drift can directly affect sandboxing and capability boundaries; it must be reviewable.

## Where it plugs in

### Drift bundles

When a host activates a new generation and the `boot-manifest` digest changes, attach `boot.manifest.diff` to the `drift.bundle` as an optional **posture diff**.

See:
- Drift bundles: `docs/395-drift-bundles-and-review-summaries.md`
- Canonical diff list: `docs/430-diff-surface-registry.md`
- Boot manifests + event-log replay: `docs/313-boot-manifests-and-eventlog-replay.md`

### Gates (policy chooses)

Suggested gates (illustrative):
- If `risk_flags` contains `bootloader-changed`, require **two-person** approval for profiles A/D.
- If `risk_flags` contains `kernel-image-changed`, require approval and (optionally) attach a `repro.check.receipt`.
- If `risk_flags` contains `cmdline-profile-changed`, require review for sandbox-meaningful flags.

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):
- `bootloader-changed`
- `kernel-image-changed`
- `cmdline-profile-changed`

Profiles can override the default gate posture without forking the lane.

## Sources (ecosystem anchors)

These are not dependencies; they are useful reference points:
- IETF RATS Architecture (evidence/verifier vocabulary): https://datatracker.ietf.org/doc/rfc9334/
- systemd-measure (PCR pre-calculation for UKI): https://www.freedesktop.org/software/systemd/man/systemd-measure.html
- Unified Kernel Image (UKI) specification: https://uapi-group.org/specifications/specs/unified_kernel_image/

Last updated: 2026-02-27r153
