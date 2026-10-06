# Kernel tunables + sysctls as evidence (no “mystery knobs”)

Most operating systems accumulate “mystery knobs”:
`sysctl` values, loader tunables, `kenv` variables, and hidden defaults applied by scripts.
During incidents this becomes un-debuggable:
operators can’t answer **what was set**, **when**, **by whom**, or **whether it drifted**.

DeriveBSD’s posture is simple:

Profile default note: the A–D boundary is now explicit in `docs/475-kernel-mutation-posture-by-profile.md`. A keeps runtime sysctl mutation maintenance-shaped, B keeps risky host-kernel mutation trusted-UI-visible, C preserves explicit local-admin fallback, and D treats preload + lockdown as the production baseline.

> Kernel mutation is a supply-chain event.
> If it isn’t derived + receipted, it is **unverified**.

## The knobs we care about

### 1) Boot-time tunables
Examples (FreeBSD-shaped): `loader.conf` variables, boot environment vars, early `kenv`.

**DeriveBSD rule:** boot-time tunables are part of the **generation closure**.
They must be visible in:
- `boot.manifest` (when the measured/secure boot lanes are used)
- the generation’s configuration tree (so `derive explain` can show them)

Why: boot-time tunables can weaken hardening or change security posture before any service manager starts.

### 2) Runtime sysctls
Examples: jail hardening knobs, PF defaults, network stack toggles, per-host tuning.

**DeriveBSD rule:** runtime sysctls are applied only by the activation/apply engine as a **derived operation**.

## The derived operation

### Plan
Activation produces a small plan object:

- `sysctl.plan` (what values we intend to set, under what constraints)

The plan is referenced by the change-set that applied it.
See: `docs/219-change-sets-and-apply-engine.md`, `docs/218-configuration-transactions-and-receipts.md`.

### Receipt
Applying a plan produces:

- `sysctl.receipt` (what actually changed, what was already correct, and what failed)

Receipts are **digest-first**: include only the keys touched and old/new values.
Bulk inventory (`sysctl -a`) is never a default artifact.

### Drift detection
Drift is inevitable (drivers, admins, third-party tools).
DeriveBSD treats drift as an **incident-grade fact**, not a shrug.

- periodic drift checks compare current values against the last applied plan
- drift produces a typed event: `sysctl.event`

The default is *detect + alert*, not “auto-heal”.
Auto-heal is a policy choice (and should emit its own receipts).

## Least authority

Services should not have ambient authority to mutate kernel knobs.

DeriveBSD posture:
- keep `sysctl` writes in the activation/apply compartment
- deny `sysctl` write capability to normal service compartments
- where a service truly needs it, require an explicit lease and receipt (treat it like other privileged portals)

This aligns with the broader “authority budgets” lane.
See: `docs/298-authority-budgets-and-permission-drift-alarms.md`.

## Practical notes (FreeBSD-first)

- Prefer **boot-time** hardening knobs to be fixed per generation; runtime mutation should be the exception.
- For runtime sysctls, apply in a deterministic order and avoid “depends-on-current-state” logic.
- Treat sysctl writes as part of the “configuration transaction” story: commit-confirmed for risky knobs.

## Output surfaces

- `derive explain kernel` should show:
  - boot-time tunables (from generation config / boot manifest)
  - last applied `sysctl.plan` digest
  - the most recent `sysctl.receipt`
  - any drift `sysctl.event`s since last apply
  - the most recent bounded `sysctl.snapshot` (when drift checks collect one)

Last updated: 2026-03-06r204
