# Destructive reprovision evidence detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

DeriveBSD already decided four important things:

- destructive reprovision authority is profile-shaped,
- installation/recovery posture is profile-shaped,
- evidence collection/export are profile-shaped,
- and terminal recording is a separate leased evidence lane rather than ambient surveillance.

This doc decides the smaller but expensive follow-on question:
**what evidence detail is normal to keep and share for destructive reprovisioning in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `destructive_reprovision`, `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals` posture surfaces.

See also:
- ADR: `adrs/ADR-0209-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`
- destructive reprovision authority: `docs/483-destructive-reprovisioning-and-reset-authority.md`
- installation/recovery posture: `docs/473-installation-and-recovery-posture-by-profile.md`
- install/recovery lane: `docs/309-installation-and-recovery-as-derived-operations.md`
- disk mutation lane: `docs/310-disk-layout-plans-and-receipts.md`
- TTY recording lane: `docs/292-terminal-session-recording-as-evidence.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- high-risk approvals: `docs/474-high-risk-approval-posture-by-profile.md`

## Why this needs a hard decision

Destructive reprovision without an evidence/detail default is a fork generator.
The authority boundary may look correct on paper, but implementation pressure will still choose what becomes routine:

- fleet reset tooling can silently normalize invisible remote wipe/reseed work,
- workstation reset UX can fall back to screenshots, shell transcripts, or a vague “the user definitely confirmed it”,
- general-purpose installs can inherit whichever compatibility installer or admin helper happened to run first,
- and factory/regulatory reset lanes can normalize bench rituals or universal camera/video capture instead of typed reset proof.

A coherent archive needs a durable answer to four questions:

- is `reset.receipt` plus `disk.layout.receipt` enough by default, or is richer content capture normal?
- when is trusted-UI/presence proof the right stronger lane?
- when is output-only TTY/console recording the right stronger lane?
- what detail is allowed to leave the box or organization boundary by default?

## Accepted baseline

Across all profiles:

- `reset.receipt` remains the mandatory baseline authoritative evidence object,
- `disk.layout.receipt` remains the mandatory joined storage truth whenever destructive disk mutation happened,
- destructive reset authority does **not** automatically imply rich content recording,
- trusted-UI or attended/presence evidence recorded through `reset.receipt.observed_evidence[]` is the normal stronger human-intent proof,
- output-only TTY/console recording is the default stronger execution-evidence lane only when reset actually uses a brokered terminal, maintenance console, or recovery shell lane,
- ambient screen/video recording is never the routine baseline,
- and exported reset evidence should use the smallest artifact that still explains the destructive act.

That keeps reset operable and reviewable without letting the reset lane silently become either invisible folklore or a universal panic recorder.

## Product-shape defaults

| Profile | Local recording/detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `reset-receipt-plus-disk-layout-receipt-always-output-only-tty-for-remote-maintenance-reset` | `redacted-encrypted-incident-scoped-export` | Fleet destructive reprovision keeps typed reset/storage truth, and remote maintenance reset work normally leaves an output-only console trail without normalizing invisible wipe/reseed or input capture. |
| **B workstation** | `reset-receipt-plus-observed-trusted-ui-evidence-always-output-only-terminal-only-if-recovery-shell-is-used-no-ambient-screen-recording` | `recipient-visible-user-mediated-redacted-sharing` | Workstation reset proof is trusted-UI-first and disk-identity-explicit; terminal output becomes the stronger lane only if reset actually enters a recovery shell, and richer capture is never ambient. |
| **C general_os** | `reset-receipt-always-trusted-ui-or-admin-evidence-normal-output-only-tty-preferred-for-derive-managed-remote-reset` | `explicit-redacted-export` | General-purpose installs keep explicit typed reset proof without pretending every classic installer or local-admin adapter inherits the full Derive evidence story. |
| **D appliance_factory** | `reset-receipt-plus-disk-layout-receipt-plus-physical-or-station-evidence-always-output-only-tty-for-approved-maintenance-reset` | `minimal-redacted-bundle-oriented-export` | Factory/regulatory destructive reprovision stays offline/auditable with typed observed presence/quorum evidence and output-only console trails where execution actually used a maintenance/reset station. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of the existing reset/install/evidence/export/approval posture surfaces when destructive reprovisioning is in play.

## What this fixes by profile

### A) Secure fleet host

Default: `reset.receipt` + `disk.layout.receipt` always; output-only TTY/console recording for remote maintenance reset lanes.

- Fleet reprovision must answer which target was wiped, which plan was used, and which install payload was reseeded.
- That makes typed reset/storage receipts non-negotiable.
- If reset execution actually runs through a brokered remote maintenance console, output-only console evidence is the routine stronger lane.
- It does **not** justify ambient input capture or silent reinstall-with-wipe folklore.
- External sharing therefore stays incident-scoped, encrypted, and redacted by default.

### B) Secure workstation

Default: `reset.receipt` with observed trusted-UI confirmation evidence always; output-only terminal recording only when a recovery shell is actually used; no ambient screen recording.

- Workstations are where destructive reset most easily drifts into screenshot archaeology or privacy-toxic “record the whole thing” habits.
- The archive still needs proof that the intended disk and destructive scope were made visible to the human.
- So B keeps typed reset evidence plus trusted-UI confirmation/presence detail as the normal stronger proof, and only uses output-only terminal recording when reset actually enters a recovery shell lane.
- Sharing remains recipient-visible, user-mediated, and redaction-aware.

### C) General-purpose OS

Default: `reset.receipt` always; trusted-UI/admin confirmation evidence routine; output-only TTY preferred for Derive-managed remote or recovery-console reset.

- C needs practical reset proof without assuming a single blessed installer, vendor helper, or support backend.
- Derive-managed reset should still leave useful typed evidence and prefer output-only terminal trails for remote or recovery-console execution.
- Compatibility installers and richer capture remain explicit adapter lanes, not ambient inherited posture.
- Export stays explicit and redacted rather than “the installer logs whatever it wants and uploads it somewhere”.

### D) Appliance factory / regulatory

Default: `reset.receipt` + `disk.layout.receipt` always; observed physical/station/quorum evidence routine; output-only TTY/console recording for approved maintenance reset lanes.

- D often needs durable proof of attended destructive reset more than it needs expansive content logs.
- Typed observed evidence for physical reset markers, station presence, and offline/quorum approval is therefore routine.
- Output-only TTY/console recording fits the factory/regulatory forensics shape when reset actually runs through a maintenance station or recovery console.
- Ambient camera/screen recording and terminal input capture stay out of the default production posture.
- Export remains minimal, redacted, and bundle-oriented.

## Cross-profile invariants

Regardless of profile:

- `reset.receipt` is mandatory whenever destructive reprovision is used,
- `disk.layout.receipt` remains the storage truth rather than being collapsed into reset authority,
- human-intent proof and execution-lane recording stay distinct,
- richer console artifacts must not be smuggled in through ambient reset helpers, restore tokens, or installer defaults,
- and exported reset evidence should prefer typed receipt joins before richer content capture.

## What remains open

This doc does **not** freeze:

- exact trusted-UI consent artifact joins for reset flows,
- exact console/video artifact shapes,
- exact retention windows,
- exact station-attestation or physical-marker adapters,
- or exact reset/recovery frontend wording.

Those are future implementation/spec questions.
The product-shaped default for destructive-reset evidence/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It keeps DeriveBSD viable across all four product shapes without forcing fleet/factory reprovision, workstation reset UX, and general-purpose compatibility into one accidental reset recorder.

Last updated: 2026-03-21r349
