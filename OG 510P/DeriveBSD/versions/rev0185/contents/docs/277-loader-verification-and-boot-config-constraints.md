# Loader verification and boot config constraints (libsecureboot / veriexec lessons)

A common secure-boot failure mode is *semantic drift*:

- firmware verified the loader binary,
- but the loader booted an unexpected kernel or modules,
- or a mutable config file changed what was loaded,
- or the “integrity policy” only starts *after* the attacker already chose what to boot.

DeriveBSD is already opinionated about atomic generations and explicit intent.
We should be equally opinionated about the **pre-kernel phase**.

This doc is a design sketch for the “boring” guarantees we want from the boot loader.

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
- any override is turned into a typed evidence record and surfaced in attestation
- dangerous overrides require a specialisation / breakglass grant

### 3) Make “what was verified” exportable

The loader should emit (or hand off to early userland to emit):

- a `boot.attestation` (or a referenced structure) that includes:
  - which generation it booted
  - which digests it verified (kernel, modules, policy)
  - which bootchain policy was in force (`bootchain.policy` digest)
  - which overrides were applied

This makes remote verification possible and makes incident bundles useful.

### 4) Compose with securelevel/lockdown

The boot chain should set the stage for operational lockdown:

- preload required modules (per `kmod.load.plan`)
- enter operational mode
- raise lockdown/securelevel as policy dictates (`docs/230-lockdown-levels-and-securelevel.md`)

The “missing driver after lockdown” problem is solved by planning, not by leaving the door open.

## Open questions

- Where exactly do we store the signed boot manifest (inside the generation, beside it, or inside a capsule)?
- How do we bind manifests to revocation/allowlist policy (SBAT-shaped identities)?
- What is the minimal override vocabulary that covers real operations without becoming a policy bypass?

Track this in the risk register: `docs/266-open-questions-and-risk-register.md`.

Last updated: 2026-02-25
