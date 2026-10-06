# Lockdown levels: BSD securelevel as a posture control (and why it fits DeriveBSD)

Most systems rely on discretionary policy (“don’t do that”) to keep the host safe after boot.
*BSD has a blunt but powerful primitive: **securelevel**—a kernel “lockdown” dial that can restrict even `root` once the system is in steady-state.

DeriveBSD already has a posture lane (`docs/226-platform-posture-and-attestation-results-as-evidence.md`).
Securelevel-style lockdown is a natural complement:

Profile default note: `docs/475-kernel-mutation-posture-by-profile.md` now makes the A–D boundary explicit. A raises lockdown after activation and keeps risky runtime mutation maintenance-shaped, B keeps risky host-kernel mutation trusted-UI-visible, C keeps stronger lockdown as an explicit lane rather than a hidden prerequisite, and D treats preload-only + lockdown as the production baseline.
- posture answers **“what is true about this host?”**
- lockdown answers **“what is this host allowed to do right now?”**

## What securelevel gives us (lessons)

- **Monotonic hardening:** on a running system, securelevel can usually be raised but not lowered (except by `init` / reboot), making it useful as a “last line” after compromise.
- **Concrete guardrails:** typical effects include enforcing immutable flags, restricting raw disk writes, restricting kernel module loading / kernel memory writes, and (on OpenBSD) preventing PF rule changes at high levels.

See: FreeBSD securelevel overview (Handbook) and OpenBSD `securelevel(7)` for explicit restrictions and semantics.  
(References in `docs/32-curated-references.md`.)

## DeriveBSD direction

Treat “lockdown level” as an **explicit policy output** with a receipt, not a hidden sysctl tweak.

### Concepts

- `platform.posture.profile` gains an optional `lockdown` section:
  - `level`: e.g. `bootstrap`, `operational`, `high`
  - `allowed_ops`: coarse list for humans (“load kmods”, “edit pf rules”, “mount raw disks”, “enter debugger”)
  - `requires`: prerequisites before raising (e.g. “all required kernel modules preloaded”, “pf rules committed”, “state migrations done”, “attestation verified”, “time sync ok”)

- `platform.lockdown.receipt` records:
  - requested level + effective level
  - policy digest
  - evidence digests used to justify raising (attestation receipt, time snapshot, storage health snapshot, etc.)
  - the exact kernel knobs touched (e.g., `kern.securelevel`), and any ancillary measures (e.g., disabling kernel debugger consoles)

### Behavior

1) **Boot / activation runs “unlocked”** enough to:
   - mount / import pools
   - load required kernel modules / firmware
   - bring up required services
   - apply pf rules / network posture
   - apply change sets / state migrations

2) Once health gates pass, DeriveBSD **raises lockdown** to the target level and emits a receipt.

3) High-privilege workflows that require “unlocking” are modeled as:
   - a separate boot path (specialisation / rescue mode), or
   - a policy-governed, time-bounded *maintenance window* that postpones raising lockdown until work is done (still receipted).

This is consistent with DeriveBSD’s general theme: **capability-gated, receipted privilege**, rather than ambient root powers.

## Why this is “juicy” for a greenfield system

Legacy systems struggle because lockdown choices become ad-hoc and undocumented.
DeriveBSD can make it boring:
- lockdown is part of the **plan**
- lockdown changes are part of the **audit trail**
- lockdown level is a **first-class gate input** (some operations require a minimum posture and a minimum lockdown, others require `bootstrap`).

## Interactions (gotchas we should embrace early)

- **Kernel module loading:** securelevel typically restricts it → make “preload required kmods” a first-class planning step.
- **Firewall changes:** if we want “pf rules can’t be changed post-boot”, we should encode that as policy and enforce it (even if FreeBSD securelevel doesn’t cover PF the way OpenBSD does).
- **Debuggers:** disable in-kernel debugger consoles at operational/higher levels unless policy explicitly allows them.
- **Jails / compartments:** consider letting workload compartments run at a higher lockdown than the host (or the reverse), but keep the relationship explicit and receipted.

## Related

- Kernel module policy + loading receipts: `docs/276-kernel-module-policy-and-loading-as-evidence.md`
- Platform posture & attestation receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- Specialisations / safe-mode: `docs/174-specialisations-and-variants.md`
- Change sets & apply engine: `docs/219-change-sets-and-apply-engine.md`

Last updated: 2026-03-06r204
