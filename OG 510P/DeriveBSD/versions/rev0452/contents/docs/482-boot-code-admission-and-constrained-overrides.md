# Boot code admission and constrained overrides

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, reproducibility, isolation  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had boot manifests, measured-boot evidence, kernel-module policy, and loader-verification notes.
What this doc decides is narrower and more useful for implementation:
**what is the official contract that joins boot manifests, mutable boot overrides, module loading, and attestation into one explainable kernel-code admission story?**

This is intentionally **not** a full loader backend spec.
It is a stable contract decision.

See also:
- ADR: `adrs/ADR-0072-boot-code-admission-and-constrained-overrides.md`
- loader verification notes: `docs/277-loader-verification-and-boot-config-constraints.md`
- kernel modules as evidence: `docs/276-kernel-module-policy-and-loading-as-evidence.md`
- boot manifests + replay: `docs/313-boot-manifests-and-eventlog-replay.md`
- kernel mutation posture by profile: `docs/475-kernel-mutation-posture-by-profile.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

Measured boot, signed loaders, and kernel-module policy all become theatre if mutable boot config remains an unbounded loophole.
The archive was already converging on the right ingredients, but not yet on one small contract.
Without that contract:

- the loader can verify some bytes without exposing the module policy it trusted,
- `loader.conf`-style mutability quietly becomes the real authority surface,
- module receipts can describe what loaded without joining back to the boot closure,
- and attestation can prove a quote without telling a responder which kernel bytes, module policy, and boot overrides mattered.

DeriveBSD needs a narrower rule: **boot code admission is a typed join, not a bag of boot features**.

## The official contract

The accepted v0 join path is:

1. **`boot.manifest`** names the boot closure for a deployed generation.
2. **`boot.override.policy`** defines the tiny set of mutable boot choices that remain legal.
3. **`boot.override.receipt`** records which approved mutable choices were requested, applied, or denied.
4. **`boot.attestation`** states which digests were actually verified and, when relevant, which override receipt was in force.
5. **`kmod.load.plan`** and **`kmod.load.receipt`** bind back to `boot_manifest_digest` so post-kernel module posture remains part of the same story.

This is the operational answer to “what kernel code was admitted and why?”

## Boot manifest requirements

`boot.manifest` remains the authoritative boot-closure manifest, but it now carries an explicit policy join block:

- `policy_digests.kmod_policy_digest`
- `policy_digests.boot_override_policy_digest`

That means the boot closure is no longer just “loader + kernel + modules tree”.
It also says **which policy objects governed those bytes**.

A manifest still stays intentionally small:

- loader digest
- kernel digest
- kernel-module tree digest
- activation / init digest when relevant
- command-line / boot-profile digest when relevant
- the required policy digests above

## Constrained mutable boot surface

DeriveBSD keeps a tiny, typed mutable boot vocabulary.
Normal operational overrides are limited to:

- **`next-entry`** — select the next approved boot entry / generation
- **`boot-mode`** — select an approved mode such as `normal`, `recovery`, or `maintenance`
- **`console-profile`** — select a predeclared console profile such as local console vs serial

This is deliberately small.
The following are **not** part of the normal override surface:

- arbitrary loader variables
- arbitrary kernel arguments
- arbitrary `kenv` / tunable injection
- mutable module search paths
- open-ended “debug flags” with undefined blast radius

If an operator needs more than the tiny override surface, the path is a **specialisation** / maintenance / breakglass lane, not ambient boot config freedom.

## Attestation requirements

`boot.attestation` must do more than point at a boot manifest digest.
It now includes a compact `verified` block that states the digests for:

- the verified kernel
- the verified kernel-module tree
- the verified `kmod.policy`
- the verified `boot.override.policy`

When mutable overrides were applied, attestation also carries `override_receipt_digest`.
That keeps remote verification, support bundles, and local explainability aligned.

## Kernel-module join requirements

`kmod.load.plan` and `kmod.load.receipt` now carry `boot_manifest_digest`.
That makes the join explicit:

- `boot.manifest` says which kernel/module bytes and policies were admitted,
- `kmod.load.plan` says what had to be loaded before lockdown,
- `kmod.load.receipt` says what actually loaded or was denied.

This keeps module posture from floating free of the boot closure.

## Product-shape consequences

### A) Secure fleet host

- Boot mutation stays narrow and policy-shaped.
- Runtime kernel-code surprises become easier to block and explain.
- Remote responders can join manifest → attestation → kmod receipt without shell folklore.

### B) Secure workstation

- Recovery-friendly choices stay available, but risky host-boot mutation remains trusted-UI / maintenance-shaped rather than hidden config drift.
- The host can explain to the user or support what boot override, if any, was used.

### C) General-purpose OS

- Viability is preserved: selecting a recovery entry or console profile stays possible without inventing fleet infrastructure.
- The archive still refuses to pretend that arbitrary boot-variable freedom is the coherent default.

### D) Appliance factory / regulatory

- Production images get a real preload-and-lockdown story instead of a signed-loader checkbox with mutable boot folklore underneath.
- Approved offline maintenance can remain possible without turning production boot config into ambient mutable state.

## Minimal invariants

A coherent boot-code admission story should satisfy these invariants:

- `boot.manifest` identifies both boot-critical bytes and the policy digests that govern them
- `boot.override.policy` defines a tiny mutable surface, not a general scripting escape hatch
- `boot.override.receipt` explains any mutable choice that affected boot
- `boot.attestation` states what was verified, not just that a quote exists
- `kmod.load.plan` / `kmod.load.receipt` bind back to `boot_manifest_digest`
- lockdown claims are only credible if required module loading is already accounted for in the manifest + kmod join

## What this does **not** decide

Still open:

- the exact loader implementation path on each BSD target
- the final signature / trust-anchor transport for `boot.override.policy`
- the final trusted-UI / serial-console UX for choosing approved overrides
- the exact out-of-policy breakglass ceremony

Those are follow-on implementation or ADR items.

## Design cue from current systems

A few ecosystem lessons are stable even if the exact tooling differs:

- signed boot components are necessary but insufficient when mutable boot config stays unconstrained
- module-loading policy only matters if it joins back to the boot closure and lockdown posture
- operators need a **small** mutable boot surface for recovery and console bring-up
- anything larger than that should be explicit maintenance, not ambient convenience

DeriveBSD should steal those lessons while keeping the backend replaceable and the contract small.

Last updated: 2026-03-07r211
