# ADR-0073: Destructive reprovisioning and reset authority

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already decided the **product-shape default posture** for installation and recovery in
`adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`.
That decision intentionally left one sharp edge unresolved: the exact contract for **destructive reprovisioning**.

The archive repeatedly said some version of “signed reset bundles/markers” should exist,
but that phrase was still doing too much hand-waving:

- `disk.layout.plan` made wrong-disk and additive-vs-destructive intent reviewable,
  but not the final authority to actually wipe and reseed a host,
- breakglass could describe emergency operator authority,
  but not the normal factory/workstation/general-OS reset story,
- product profile D needed offline-capable, retained, strongly-approved reset behavior,
  while B and C still needed humane and viable local wipe/reinstall flows,
- and incidents/support could not answer one compact question:
  **what destructive reset was authorized, against which disk plan and install payload, and by which presence/approval signals?**

Without a stable contract, the archive drifts back toward destructive shell folklore,
weak disk confirmation, or “the reset button did something” operational ambiguity.

## Decision

DeriveBSD will treat **destructive reprovisioning / factory reset** as a small typed contract,
not an installer flag.

The accepted v0 boundary is:

1. `reset.authorization` is the authoritative object approving a destructive reprovision.
2. `reset.authorization` must bind:
   - the target host / device selector,
   - the `disk.layout.plan` digest,
   - the install payload digest,
   - the destructive scope,
   - the retention mode,
   - and the required authority signals.
3. `reset.receipt` records what destructive reprovision authority was actually observed,
   which target device was touched,
   which request digests were in force,
   and which downstream receipts were produced.
4. `disk.layout.plan` remains the typed storage mutation substrate,
   but destructive application is only coherent when joined to `reset.authorization` / `reset.receipt`.
5. The v0 authority vocabulary stays intentionally small:
   - `trusted-ui-confirmation`
   - `physical-reset-marker`
   - `station-presence-assertion`
   - `breakglass-grant`
   - `offline-quorum-approval`
   - `maintenance-window`
6. Product-shape defaults become explicit through the stable `destructive_reprovision` profile knob:
   - **A**: target-bound, digest-bound, breakglass-or-maintenance shaped
   - **B**: trusted-UI, disk-identity-confirmed, digest-bound
   - **C**: explicit admin or trusted-UI, still digest-bound and receipted
   - **D**: offline signed reset authority plus physical or attended-station presence by default

## Consequences

### Positive

- The archive now has a crisp answer to “what authorizes a wipe?” without inventing a giant installer subsystem.
- Wrong-disk avoidance, factory reset posture, and retained evidence now share one join path.
- Profile D’s “signed reset bundles/markers” language stops being folklore and becomes an implementable boundary.
- Workstation and general-OS resets can remain viable without inheriting ambient, invisible wipe paths.
- Support bundles and postmortems can join reset intent → disk mutation → first boot evidence.

### Negative / trade-offs

- Destructive reprovisioning now has another pair of typed objects to keep wired and explained.
- Some traditional “just rerun the installer with wipe” flows become explicitly out of bounds unless they emit the proper authority artifacts.
- General-purpose profile C keeps local-admin viability, but it loses the excuse for unreceipted destructive reset shortcuts.

## Non-goals

This ADR does **not** decide:

- the final installer or recovery UI stack,
- the exact removable-media / BMC / station transport for carrying `reset.authorization`,
- the exact trust-anchor distribution for signing reset authorizations,
- or the exact dataset-retention frontend above the retention modes.

Those remain implementation work or follow-on ADR material.

## Why this shape

The coherence win is deliberately narrow:

- keep `disk.layout.plan` for storage intent,
- add one authorization object for destructive reprovision intent,
- add one receipt object for what destructive authority was actually observed,
- and keep A–D defaults explicit enough that no product shape needs a fork.

That is enough to turn “signed reset bundles/markers” into a spec surface worth implementing,
without freezing the entire installer stack too early.
