# Loader verification and boot config constraints (libsecureboot / veriexec lessons)

A common secure-boot failure mode is *semantic drift*:

- firmware verified the loader binary,
- but the loader booted an unexpected kernel or modules,
- or a mutable config file changed what was loaded,
- or the “integrity policy” only starts *after* the attacker already chose what to boot.

DeriveBSD is already opinionated about atomic generations and explicit intent.
We should be equally opinionated about the **pre-kernel phase**.

This doc now describes the accepted v0 boundary for the “boring” guarantees we want from the boot loader.

## Goals

- The loader should verify the kernel + required boot artifacts for the chosen generation.
- Module loading at boot should be constrained by explicit policy (`docs/276-kernel-module-policy-and-loading-as-evidence.md`).
- “Mutable boot config” (tunable overrides) should be **constrained and receipted**, not a loophole.
- Boot-time verification should compose with:
  - bootchain revocation/allowlists (`docs/244-bootchain-revocation-and-allowlists.md`)
  - measured boot (`docs/176-measured-boot-attestation.md`)
  - verified execution at runtime (`docs/233-verified-execution-as-evidence.md`)

## Lessons to steal

### 1) Loader verification is a practical project

FreeBSD’s boot-security work shows a realistic path: use a lightweight verification library in the loader (e.g., BearSSL-backed) and verify a signed manifest of hashes for the kernel and modules.

This is a better mental model than “just turn on UEFI Secure Boot” because it answers *what the loader actually loaded*.

### 2) “Allow mutable loader.conf” is a hard requirement in the real world

Operators need safe knobs:

- enable serial console
- flip a safe-mode flag
- adjust a device quirk
- select a previous generation or recovery entry

If these knobs are unconstrained, integrity collapses.
If they are fully forbidden, operations becomes brittle.

So: **allow a small, typed override surface** that is visible in evidence and can be policy-gated.
The accepted vocabulary is now deliberately tiny: `next-entry`, `boot-mode`, and `console-profile` via `boot.override.policy` / `boot.override.receipt`.

## DeriveBSD direction

### 1) Treat boot artifacts as part of the generation closure

A host generation should include an explicit “boot closure”:

- loader (if DeriveBSD ships one)
- kernel
- initrd / early userland capsule (if used)
- module set needed at boot time
- optional device tree / microcode / firmware capsules

This closure already exists conceptually; the loader should enforce it.

### 2) Verification model: signed boot manifest + constrained overrides

At minimum:

- the generation publishes a signed list of expected digests (kernel + boot-critical modules + policy digests)
- the loader verifies those digests before handing off

To keep operations viable:

- `loader.conf` can exist, but only a **constrained subset** is honored in operational mode
- the normal mutable surface is `next-entry`, `boot-mode`, and `console-profile` via `boot.override.policy`
- any applied or denied override is turned into `boot.override.receipt` and surfaced in attestation
- dangerous or open-ended overrides require a specialisation / breakglass grant instead of ambient config-file freedom

### 3) Make “what was verified” exportable

The loader should emit (or hand off to early userland to emit):

- a `boot.attestation` (or a referenced structure) that includes:
  - which generation it booted
  - which digests it verified (`kernel`, `kernel-modules`, `kmod.policy`, `boot.override.policy`)
  - which overrides were applied (`boot.override.receipt` digest when present)

This makes remote verification possible and makes incident bundles useful.

### 4) Compose with securelevel/lockdown

The boot chain should set the stage for operational lockdown:

- preload required modules (per `kmod.load.plan`)
- enter operational mode
- raise lockdown/securelevel as policy dictates (`docs/230-lockdown-levels-and-securelevel.md`)

The “missing driver after lockdown” problem is solved by planning, not by leaving the door open.

## What remains open

- Where exactly the signed manifest/policy bytes live in each boot backend
- How the trust-anchor transport works for `boot.override.policy`
- The final trusted-UI / console UX for selecting approved overrides

Track implementation follow-ups in the risk register and future ADRs; the contract boundary itself is now fixed in `docs/482-boot-code-admission-and-constrained-overrides.md`.

Last updated: 2026-03-07r211
