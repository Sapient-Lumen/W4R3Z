# Destructive reprovisioning and reset authority

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, supply-chain  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already decided the product-shape default for installation and recovery.
What this doc decides is narrower and more useful for implementation:
**what is the official contract that authorizes destructive reprovisioning / factory reset without falling back to installer folklore?**

This is intentionally **not** a full installer stack spec.
It is a stable contract decision.

See also:
- ADR: `adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`
- installation/recovery posture by profile: `docs/473-installation-and-recovery-posture-by-profile.md`
- installation/recovery shared workflow: `docs/309-installation-and-recovery-as-derived-operations.md`
- disk mutation substrate: `docs/310-disk-layout-plans-and-receipts.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

“Signed reset bundles/markers” was directionally right but still too vague.
Without a small accepted contract, destructive reprovisioning drifts into one of four bad shapes:

- the installer grows an ambient `--wipe` path that can hit the wrong disk,
- factory reset becomes a bench ritual with no retained receipt,
- workstation/general-OS convenience paths silently become the real authority model,
- or headless fleet/appliance recovery has to choose between unsafe shell lore and unusable ceremony.

DeriveBSD needs a narrower rule: **destructive reprovisioning is a typed join, not a mode bit.**

## The official contract

The accepted v0 join path is:

1. **`reset.authorization`** approves a destructive reprovision.
2. **`reset.authorization`** binds the target selector, `disk.layout.plan` digest, install payload digest, destructive scope, retention mode, and required authority signals.
3. **`reset.receipt`** records which authority signals were actually observed, which device was touched, and which downstream receipts were produced.
4. **`disk.layout.receipt`** remains the storage mutation truth for what happened on disk.
5. Optional `breakglass.grant` remains a valid authority input for the profiles that use it, but it is no longer the only implied story.

This is the operational answer to “what authorized this wipe, on which target, and what did it rebuild?”

## New typed artifacts

### `reset.authorization`

`reset.authorization` is the canonical authority object for destructive reprovisioning.
It must be digest-bound and target-aware.

Minimum useful fields:

- target host identity
- target-device selector (serial / WWN / path / size bounds)
- `disk.layout.plan` digest
- install payload digest
- destructive scope (wipe GPT, destroy pools, erase user state, reseed system, etc.)
- retention mode
- required authority evidence
- expiry / signature metadata when applicable

### `reset.receipt`

`reset.receipt` is the evidence object for the destructive reprovision act.
It should capture:

- the referenced `reset.authorization` digest / id
- the target device actually touched
- the request digests actually used
- which required authority signals were observed, missing, or not required
- the resulting `disk.layout.receipt` digest and other downstream receipts when available
- outcome (`success`, `failed`, `partial`, `denied`)

## Authority vocabulary (kept intentionally small)

The accepted v0 authority signals are:

- `trusted-ui-confirmation`
- `physical-reset-marker`
- `station-presence-assertion`
- `breakglass-grant`
- `offline-quorum-approval`
- `maintenance-window`

The point is not to predict every implementation.
The point is to constrain the semantic space so the archive stops pretending all destructive reset ceremonies are equivalent.

## Product-shape defaults

| Profile | `destructive_reprovision` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `target-bound-digest-breakglass-or-maintenance` | Headless fleet wipe/reseed remains target-bound and digest-bound; destructive reprovision belongs to breakglass or maintenance lanes rather than an ambient reinstall toggle. |
| B (`workstation`) | `trusted-ui-target-confirm-digest-bound` | A destructive local wipe must surface disk identity and intent through trusted UI and remain bound to explicit reset authorization rather than hidden convenience UI. |
| C (`general_os`) | `explicit-admin-or-trusted-ui-digest-bound` | Broad viability remains, but destructive reinstall/reset still needs an explicit admin or trusted-UI decision object and retained receipt. |
| D (`appliance_factory`) | `offline-signed-authority-plus-reset-marker` | Production/factory destructive reprovision is offline-capable and digest-bound, and normally requires signed reset authority plus physical or attended-station presence. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- destructive reprovisioning must bind to an explicit target selector
- destructive reprovisioning must bind to a `disk.layout.plan` digest
- the install payload being reseeded must be named by digest, not folklore
- retained state exceptions must be named as retention policy, not hidden script behavior
- the observed authority signals must be receipted loudly enough for support and forensics

## What this fixes by profile

### A) Secure fleet host

Default: `target-bound-digest-breakglass-or-maintenance`

- Fleet recovery keeps remote/headless viability without normalizing “reinstall with wipe” as ambient automation.
- Destructive reprovision stays target-device-bound and reviewable.
- Breakglass or maintenance authority is explicit instead of hiding inside installer transport.

### B) Secure workstation

Default: `trusted-ui-target-confirm-digest-bound`

- Workstations need a humane local wipe/reinstall path.
- The hard decision is that this path still uses explicit reset authorization and trusted-UI disk identity confirmation.
- “Reset this laptop” remains viable without quietly becoming “erase whatever storage looks convenient.”

### C) General-purpose OS

Default: `explicit-admin-or-trusted-ui-digest-bound`

- General-purpose installs keep broad local-admin and classic-installer viability.
- The archive still refuses to treat invisible destructive reset as a legitimate default.
- Compatibility flows may remain, but they must feed the same typed authority/receipt surfaces.

### D) Appliance factory / regulatory

Default: `offline-signed-authority-plus-reset-marker`

- Factory/regulatory resets are now concretely shaped instead of gesturing at “markers”.
- The normal posture is offline-capable signed authority plus physical or attended-station presence.
- This keeps shipped production reset from collapsing into bench folklore or live-network dependency.

## Retention posture (kept simple)

`reset.authorization` carries a retention mode instead of silently preserving state.
The v0 retention vocabulary stays intentionally small:

- `wipe-all-state`
- `preserve-hardware-identity-only`
- `preserve-approved-anchors`
- `preserve-listed-datasets`

Anything richer belongs in a higher-level frontend that still compiles down to these explicit modes.

## Minimal invariants

A coherent destructive-reprovision story should satisfy these invariants:

- `reset.authorization` binds target, plan digest, install payload digest, destructive scope, and retention mode
- `reset.receipt` records the authority signals actually observed
- destructive reprovision never relies on “whoever had the installer open” as the authority model
- `disk.layout.receipt` remains the storage truth, while `reset.receipt` remains the destructive-authority truth
- profiles may differ in *which* authority signals they prefer, but not in whether destructive reprovision is explicit and receipted

## What this does **not** decide

Still open:

- the final installer / recovery UI stack
- the exact removable-media, BMC, or attended-station transport carrying reset authorization
- the exact trusted-UI copy and friction budget on B
- the exact hardware marker / GPIO / jumper / station assertion mechanism on D
- the final frontend for describing fine-grained dataset retention

Those are follow-on implementation or ADR items.

## Design cue from current systems

A few ecosystem lessons are stable even if the exact tooling differs:

- additive disk declaration is safer as the routine path than keeping destructive wipe ambient
- physical-presence or attended reset signals matter when a system claims safe recovery from hostile or ambiguous states
- reset flows should make destructive intent visible *before* bytes move
- factory/regulatory reset authority must survive offline and low-trust environments without degrading into shell-history ritual

DeriveBSD should steal those lessons while keeping backends and transport helpers replaceable.

Last updated: 2026-03-07r212
