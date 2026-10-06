# Kernel module policy and loading as evidence (kld/securelevel lessons)

Kernel modules are a special kind of “runtime change”:

- they run in the most privileged context,
- they are often loaded dynamically,
- and many systems treat them as *ambient admin lore* (“load the driver, hope it’s fine”).

For DeriveBSD, **kernel module loading must be planned, auditable, and lockable**—the same way we treat activation, state migrations, and trust policy.

This lane is about:

- making *which kernel modules may exist* an explicit policy artifact,
- making *which modules must be loaded* an explicit plan,
- and emitting receipts so incident bundles can answer **“what code was in the kernel?”**.

## Goals

- Eliminate “surprise kernel code” by default.
- Make module diffs reviewable (shows up in blast-radius diffs).
- Make lockdown postures operable: preload required modules, then raise securelevel/lockdown and **prevent runtime loads**.
- Record module identity in the evidence spine (events + receipts), and optionally in measured boot.

## What to steal

### 1) Securelevel as the “last mile” guardrail

BSD securelevel-style lockdown is a blunt but useful primitive: after boot/activation, raise the level and refuse operations such as kernel module load/unload.

We treat securelevel as a posture output already (`docs/230-lockdown-levels-and-securelevel.md`).
This doc makes the *module* part explicit.

### 2) Loader verification is where “mutable config” breaks integrity

Even if firmware verifies the loader, you still need to ensure the loader verifies:

- kernel
- modules
- and the integrity policy/manifests that govern both

…and that any boot-time overrides (e.g. a debug toggle) are constrained and receipted, not “edit loader.conf and hope”.

See: `docs/277-loader-verification-and-boot-config-constraints.md`.

## Core objects (schemas)

This lane introduces four evidence objects plus an optional drift diff surface:

- **Module policy:** `spec/kmod.policy.schema.json`
- **Module policy diff (drift surface):** `spec/kmod.policy.diff.schema.json`
- **Module load plan:** `spec/kmod.load.plan.schema.json`
- **Module load receipt:** `spec/kmod.load.receipt.schema.json`
- **Module events (live monitoring + drift):** `spec/kmod.event.schema.json`

Examples:

- `spec/examples/kmod.policy.json`
- `spec/examples/kmod.policy.diff.json`
- `spec/examples/kmod.load.plan.json`
- `spec/examples/kmod.load.receipt.json`
- `spec/examples/kmod.event.json`

## Design sketch

### 1) `kmod.policy`: what may be loaded (and how)

A `kmod-policy` binds:

- scope (host / fleet, generation context, kernel ABI)
- allowlist of module **digests** (name + digest + optional path/classification)
- optional denylist (names/digests)
- autoload mode: `deny`, `allowlisted`, or `open` (default should be `allowlisted`)
- allowed sources (e.g. “only from the generation’s immutable module set”)

Key idea: **policy is about bytes, not names.** Names are UX; digests are enforcement.

### 2) `kmod.load.plan`: what must be loaded before lockdown

A `kmod-load-plan` is derived during activation planning:

- the required module set (including dependency closure)
- reasons (device match, filesystem, crypto, hypervisor backend, etc.)
- the intended enforcement: “deny runtime loads after activation” and *when* to raise lockdown

The plan is what turns securelevel from “breaks my system randomly” into “operable”.

### 3) `kmod.load.receipt`: what actually happened

The load runner emits a `kmod-load-receipt`:

- the plan digest + policy digest used
- loaded modules (name + digest + observed id/index)
- denied attempts (name/digest + reason)
- the exact knobs touched (e.g. securelevel/lockdown transitions)
- timing (applied_at/finished_at) for correlation with boot/activation receipts

This receipt should also be emitted as a typed event stream (`kmod.event`; see `docs/215-structured-event-log-as-evidence.md`) for live monitoring and drift alarms.

## Enforcement rules (boring on purpose)

1) **Default deny at runtime (post-activation).**  
   Once the system is “operational”, module load/unload should be blocked unless a policy-governed maintenance window is in effect.

2) **Preload during activation.**  
   Activation is allowed to load modules needed for the selected generation; this is exactly why we distinguish activation/posture/lockdown.

3) **No ambient module search paths.**  
   Module discovery should be constrained to the generation’s immutable module set (or an explicitly mounted “driver pack” artifact), not “whatever is on /boot”.

4) **Autoload is policy-mediated.**  
   If the kernel requests an autoload (device attach, filesystem mount), the request must resolve through `kmod.policy` and be receipted.

5) **Divergence is explainable.**  
   If a module load is denied, the system should produce a human legible explanation that points to the exact policy field that blocked it.

## Recovery + maintenance windows

Sometimes you *do* need to load a driver:

- add a new NIC
- recover a pool with a missing module
- attach forensic tooling

DeriveBSD should make this safe and reviewable:

- boot into a **specialisation** / maintenance profile (`docs/174-specialisations-and-variants.md`)
- lower lockdown only by rebooting into that profile (securelevel semantics)
- issue a **time-bounded maintenance grant** (see breakglass patterns in `docs/236-breakglass-and-recovery-mode.md`)
- and emit receipts for any module set divergence

## Interactions

- Verified execution (userland): `docs/233-verified-execution-as-evidence.md`
- Bootchain policy and revocation: `docs/244-bootchain-revocation-and-allowlists.md`
- Measured boot ergonomics: `docs/176-measured-boot-attestation.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`
- Lockdown levels (securelevel): `docs/230-lockdown-levels-and-securelevel.md`
- Module policy drift review surface: `docs/439-kmod-policy-diff-as-review-surface.md`

Last updated: 2026-02-28r158
