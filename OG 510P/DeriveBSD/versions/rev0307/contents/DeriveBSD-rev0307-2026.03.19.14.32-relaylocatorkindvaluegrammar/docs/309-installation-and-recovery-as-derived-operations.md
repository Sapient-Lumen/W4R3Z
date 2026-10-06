# Installation and recovery as derived operations

Most systems treat “install” and “recovery” as a one-off, script-heavy phase that sits *outside* the project’s normal verification and policy model.
DeriveBSD should do the opposite: **installation is just another Plan→Apply operation**, producing the same kind of receipts and supportable artifacts as any other state transition.

Greenfield advantage:
- install media is **a derived artifact** (pinned toolchain, hermetic-ish), not an ad-hoc live image
- disk mutation is **typed + receipted**, not “whatever the installer did”
- recovery is **a normal workflow**, not a separate folklore toolset

Related docs:
- Trust bootstrap and first activation evidence: `docs/155-trust-bootstrap.md`
- Host generations and switching: `docs/69-host-generations-bectl.md`, `docs/284-bootenv-switching-as-evidence.md`
- Change sets / apply engine: `docs/219-change-sets-and-apply-engine.md`
- Breakglass lane: `docs/236-breakglass-and-recovery-mode.md`, `docs/250-breakglass-and-recovery-workflows.md`
- Disk layout plans and receipts: `docs/310-disk-layout-plans-and-receipts.md`


## 1) Concepts

### Install media is an artifact
DeriveBSD should ship at least two bootable images, both built through the normal Derive pipeline:

- **`installer.image`**: minimal environment to lay down a host disk layout and activate the first generation.
- **`recovery.image`**: superset of installer tooling (diagnostics, ZFS recovery, network only as policy allows).

Both images:
- have a **content digest** and signature
- ship with a small, stable **verifier** and **policy evaluation** path
- prefer **no network by default** (network access is a mediated capability, even in recovery)

This borrows the “recovery image as a first-class product” ergonomics seen in projects like ZFSBootMenu recovery shells, while keeping DeriveBSD’s evidence posture.


### Installation is a change set
Model installation as a `change.set` that includes:

1) `disk.layout.plan` → `disk.layout.receipt`
2) root pool / datasets / boot environment creation
3) initial store seed (optional)
4) activation of generation 0 → activation receipt / generation-switch evidence
5) emission of a **`bootstrap.evidence`** bundle for the first successful activation (existing requirement)

If any step fails, the installer either:
- rolls back (where possible), or
- emits a **partial receipt set** that makes the failure diagnosable.


## 2) Desired properties (invariants)

- **Idempotent-by-default:** rerunning install with the same inputs should converge to the same on-disk result.
- **No silent shrink:** disk layout changes should be additive unless explicitly breakglass-approved.
- **No ambient trust roots:** installer/recovery must not “just use whatever CA bundle is in /etc”. Trust bundles are explicit artifacts.
- **No ambient secrets:** enrollment bundles / decryption keys are acquired through explicit broker/portal lanes.
- **Receipted mutation:** all destructive actions (partitioning, pool creation, bootloader writes) emit receipts.


## 3) Workflow sketches

### A) Local install (USB / console)

1) Boot `installer.image`.
2) Provide an **install bundle** (USB, ISO, or pre-provisioned local mirror):
   - target host deployment ref (generation tree digest)
   - `disk.layout.plan`
   - bootchain policies (optional)
   - enrollment bundle / trust bootstrap inputs
3) Installer verifies the bundle (signatures, trust policy, time requirements as applicable).
4) Installer applies `disk.layout.plan` (gpart/zpool/bectl), emitting `disk.layout.receipt`.
5) Installer materializes the target deployment into the new boot environment.
6) Installer activates generation 0 and reboots.
7) First successful boot emits `bootstrap.evidence` (must include the disk layout receipt and the exact install bundle digests).


### B) Remote install (out-of-band console + signed bundle)

Remote installs fail when they depend on interactive, stateful scripts.
Instead, make remote install:

- **bundle-driven** (single signed object)
- **idempotent** (safe to retry)
- **minimal-network** (only what policy allows)

A common pattern:
1) Boot into recovery via remote console.
2) Import a signed install bundle via a policy-constrained transport (or attach a virtual media ISO).
3) Apply the same change set as local install.


### C) Re-provision / factory reset

A “factory reset” shouldn’t be “delete random state until it boots”.
Make it a policy-controlled operation:

- destructive reprovision now uses **`reset.authorization`** + **`reset.receipt`** as the official authority/evidence contract (see `docs/483-destructive-reprovisioning-and-reset-authority.md`)
- a reserved **factory-reset partition** or marker may remain one valid authority signal, but it is no longer the whole story by itself
- reset still emits a `change.receipt` and a new `bootstrap.evidence` bundle
- reset may retain specific identity anchors if policy allows (e.g., hardware identity) while erasing user/state datasets


## 4) Recovery posture

Product-shape note: the default install/recovery authority model now comes from `docs/473-installation-and-recovery-posture-by-profile.md`; this doc stays focused on the shared operation shape.

Recovery is not a special root shell. It is a controlled workflow:

- Boot `recovery.image`.
- Acquire needed authorities via explicit grants:
  - mount/dataset leases
  - debug/trace leases
  - network leases
  - export/share leases
- Produce an **incident bundle** early (before you “poke the system”), so the original failure context isn’t lost.

A useful default: a recovery session auto-creates a small incident bundle containing:
- boot failure reason(s) and bootchain policies
- last boot assessment status
- time trust status (if time is relevant)
- disk layout receipt + bootenv switch receipts


## 5) Prior art worth stealing (with taste)

DeriveBSD doesn’t need to adopt these systems wholesale, but their *shapes* are valuable:

- **Declarative partitioning**:
  - systemd-repart (additive GPT layout changes; discoverable images; factory reset markers)
  - Nix `disko` (disk layout as code)
- **Atomic deployments**:
  - OSTree (multiple deployments on disk; always boot exactly one; power-loss safe transitions)
- **Recovery UX**:
  - ZFS boot environment tooling and “recovery shells” (boot into a tooling-rich environment that can mount/repair other environments)

These are especially relevant because DeriveBSD already has:
- activation receipts
- boot environment switching receipts
- a policy engine
- bundle/receipt mechanics

The missing piece is making disk mutation and initial provisioning fully first-class.

Last updated: 2026-03-07r212
