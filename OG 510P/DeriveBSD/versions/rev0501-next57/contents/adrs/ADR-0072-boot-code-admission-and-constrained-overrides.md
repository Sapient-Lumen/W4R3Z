# ADR-0072: Boot code admission and constrained overrides

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had most of the pieces needed for a credible kernel-code admission story:
`docs/276-kernel-module-policy-and-loading-as-evidence.md`,
`docs/277-loader-verification-and-boot-config-constraints.md`,
`docs/313-boot-manifests-and-eventlog-replay.md`,
and the existing `boot.manifest`, `boot.attestation`, `kmod.load.plan`, and `kmod.load.receipt`
schemas.

What the archive still lacked was the **official join contract** between those pieces.
Without that contract, boot security drifts into contradictory practice:

- a loader may verify some generation bytes without making clear which kernel-module policy it relied on,
- `loader.conf`-style mutability quietly becomes a policy bypass instead of a narrow operational surface,
- module plans and receipts can describe runtime posture without binding back to the boot closure that admitted the kernel code,
- and attestation can prove "something booted" without giving operators a compact answer to **which kernel bytes, which module policy, and which mutable overrides were actually in force**.

## Decision

DeriveBSD will treat **boot code admission** as a small typed contract, not a loose collection of boot features.

The accepted v0 boundary is:

1. `boot.manifest` is the authoritative boot-closure manifest for a deployed generation.
2. `boot.manifest` must carry `policy_digests.kmod_policy_digest` and `policy_digests.boot_override_policy_digest`.
3. `kmod.load.plan` and `kmod.load.receipt` must bind `boot_manifest_digest` so post-kernel module posture joins back to the boot closure.
4. `boot.attestation` must expose a compact `verified` block containing the digests for the kernel, kernel-module tree, `kmod.policy`, and `boot.override.policy`, plus an optional `override_receipt_digest` when mutable overrides were used.
5. Mutable boot overrides are constrained to a tiny typed surface:
   - `next-entry`
   - `boot-mode`
   - `console-profile`
6. Arbitrary loader variable mutation, module-path mutation, and open-ended kernel-argument injection are **not** part of the normal operational override surface. Recovery or maintenance needs a specialisation / breakglass lane rather than ambient config-file freedom.

To support that contract, DeriveBSD adds two typed artifacts:

- `boot.override.policy`
- `boot.override.receipt`

These objects define and receipt the narrow mutable boot surface instead of leaving it in comments or boot-menu folklore.

## Consequences

### Positive

- Boot security becomes explainable in one join path: `boot.manifest` → `boot.attestation` → `kmod.load.plan` / `kmod.load.receipt`.
- The archive now makes a real hard decision about mutable boot config: recovery-friendly, but not open-ended.
- Kernel-module admission and measured boot stop being parallel stories; they share stable digests and review surfaces.
- Support bundles and verifier outputs can answer *what kernel code was admitted and under which override policy?* without scraping raw bootloader files.

### Negative / trade-offs

- Some familiar debugging habits (`edit loader.conf`, add ad-hoc kernel args, change module paths live) are now explicitly out of bounds for the normal lane.
- General-purpose profile C still has to route unusual boot mutation through explicit admin / maintenance paths, which is a little more ceremony than traditional BSD custom.
- The boot pipeline now has another pair of typed artifacts to keep wired and tested.

## Non-goals

This ADR does **not** decide:

- the final loader implementation strategy,
- the exact signature transport for `boot.override.policy`,
- the exact trusted-UI / console UX for selecting approved overrides,
- or the final breakglass ceremony for out-of-policy boot mutation.

Those remain implementation work or follow-on ADR material.

## Why this shape

The coherence win is not "invent a large boot subsystem".
It is making a few narrow decisions that future implementation can rely on:

- `boot.manifest` names the boot closure **and** the policy digests that govern kernel-code admission,
- mutable boot configuration is tiny, typed, and receipted,
- attestation states what was actually verified,
- and post-boot module evidence joins back to the manifest that admitted the kernel bytes.

That is enough to move the archive from aspiration to implementable boundary without freezing backend details too early.
