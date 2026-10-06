# Breakglass recording detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already decided three important things:

- breakglass itself is an explicit typed lane,
- installation/recovery and evidence/export posture are profile-shaped,
- and terminal recording is a separate leased evidence lane rather than ambient surveillance.

This doc decides the smaller but expensive follow-on question:
**what recording detail is normal to keep and share for breakglass in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals` posture surfaces.

See also:
- ADR: `adrs/ADR-0208-breakglass-recording-detail-and-export-posture-by-profile.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- installation/recovery posture: `docs/473-installation-and-recovery-posture-by-profile.md`
- TTY recording lane: `docs/292-terminal-session-recording-as-evidence.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- high-risk approvals: `docs/474-high-risk-approval-posture-by-profile.md`

## Why this needs a hard decision

Breakglass without a recording/detail default is a fork generator.
The emergency authority boundary may look correct on paper, but implementation pressure will still choose what becomes routine:

- fleet and factory recovery shells quietly become invisible because "it was breakglass",
- workstation recovery quietly becomes either untrailed root folklore or a privacy-toxic universal panic recorder,
- general-purpose installs inherit whichever rescue environment, BMC helper, or console stack happens to ship first,
- and exported emergency evidence drifts away from the product's declared evidence/export posture.

A coherent archive needs a durable answer to four questions:

- is `breakglass.receipt` plus typed entry/exit events enough by default, or is content capture normal?
- when is output-only TTY/console recording the right stronger lane?
- when is TTY input capture ever normal?
- what detail is allowed to leave the box or organization boundary by default?

## Accepted baseline

Across all profiles:

- `breakglass.receipt` remains the mandatory authoritative evidence object,
- `breakglass.event` entry/exit state remains mandatory whenever breakglass is exercised,
- breakglass authority does **not** automatically imply rich content recording,
- output-only TTY/console recording is the default stronger emergency-session evidence lane,
- TTY input capture is a higher-risk scope than output-only capture and is never the routine baseline,
- and exported emergency evidence should use the smallest artifact that still explains the incident and the repair.

That keeps recovery operable without letting the emergency lane silently become either invisible shell work or a universal panic recorder.

## Product-shape defaults

| Profile | Local recording/detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `session-metadata-plus-output-only-tty-recording-required-for-breakglass-shell-or-console-sessions` | `redacted-encrypted-incident-scoped-export` | Fleet breakglass normally leaves a durable shell/console trail, but does not normalize TTY input capture or broad off-box emergency-session disclosure. |
| **B workstation** | `session-metadata-always-output-only-terminal-recording-required-for-breakglass-shell-or-recovery-console-no-ambient-screen-recording` | `recipient-visible-user-mediated-redacted-sharing` | Workstation breakglass is stronger than ordinary local admin: emergency shell/recovery work keeps a stronger terminal trail, but the product still refuses ambient whole-screen panic recording by default. |
| **C general_os** | `session-metadata-always-output-only-tty-preferred-for-derive-managed-breakglass-explicit-local-recovery-adapter` | `explicit-redacted-export` | General-purpose installs keep a useful Derive-managed recovery trail without pretending every classic rescue medium or compatibility helper inherits the full Derive evidence story. |
| **D appliance_factory** | `session-metadata-plus-output-only-tty-recording-required-in-approved-offline-breakglass-maintenance-lanes-only` | `minimal-redacted-bundle-oriented-export` | Factory/regulatory breakglass remains offline/maintenance-shaped and auditable; richer content capture is not normalized on production images. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of the existing install/recovery, evidence, export, and approval posture surfaces when breakglass is in play.

## What this fixes by profile

### A) Secure fleet host

Default: session metadata plus output-only TTY/console recording for breakglass shell or console sessions.

- Fleet breakglass is already an exceptional authority lane, so invisible shell work is the wrong default.
- Output-only terminal evidence gives incident review and follow-up repair analysis a durable operator trail without normalizing input capture.
- External sharing therefore stays incident-scoped, encrypted, and redacted by default.

### B) Secure workstation

Default: session metadata always; output-only terminal recording for breakglass shell or recovery-console lanes; no ambient screen recording.

- B is where recovery most easily drifts into a false choice between untrailed local root and privacy-toxic panic capture.
- The archive needs a harder answer: breakglass is stronger than ordinary local admin, so emergency shell/recovery work should leave a stronger terminal trail.
- But that does **not** justify ambient whole-screen recording, hidden input capture, or permanent support-agent semantics.
- Sharing remains recipient-visible, user-mediated, and redaction-aware.

### C) General-purpose OS

Default: session metadata always; output-only TTY recording preferred for Derive-managed breakglass; classic rescue environments remain explicit adapters.

- C needs a practical recovery story without pretending one rescue frontend or one remote-management backend owns the whole product.
- Derive-managed breakglass should still leave a useful output-only trail by default.
- Classic local rescue environments, compatibility installers, and BMC helpers remain explicit adapter territory rather than inherited product truth.
- Export stays explicit and redacted instead of "recovery helper uploads whatever it has."

### D) Appliance factory / regulatory

Default: approved offline breakglass or maintenance recovery keeps session metadata plus output-only TTY/console recording; production images do not normalize richer capture.

- D often needs a durable emergency-maintenance trail more than it needs expansive content logging.
- Output-only terminal evidence in approved offline maintenance lanes fits the regulatory/forensics shape without normalizing broad capture on production images.
- TTY input capture is forbidden by default outside stronger offline/approved exception lanes.
- Export stays minimal, redacted, and bundle-oriented.

## Cross-profile invariants

Regardless of profile:

- `breakglass.receipt` and `breakglass.event` entry/exit evidence are mandatory whenever breakglass is exercised,
- recording authority is separate from network/export authority,
- TTY input capture is stronger than output-only TTY/console recording,
- recovery backends must not smuggle remembered recording posture in rescue media, restore tokens, or ambient agents,
- and exported breakglass artifacts should prefer metadata-only or output-only forms before richer capture.

## What remains open

This doc does **not** freeze:

- exact retention windows,
- exact recovery-media UI or trusted-console UX,
- exact BMC / virtual-media / serial adapter posture,
- exact quorum thresholds for every breakglass scope,
- or exact remote reverification / external case-system mapping.

Those are future implementation/spec questions.
The product-shaped default for recording/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It keeps DeriveBSD viable across all four product shapes without forcing fleet/factory recovery, workstation privacy, and general-purpose compatibility into one accidental panic-recorder product or one invisible rescue-shell folklore lane.

Last updated: 2026-03-21r348
