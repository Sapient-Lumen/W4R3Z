# ADR-0208: Breakglass recording detail and export posture by profile

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/236-breakglass-and-recovery-mode.md` and `docs/250-breakglass-and-recovery-workflows.md` already fixed **what breakglass is for**:

- explicit, time-bounded, digest-bound emergency authority,
- typed `breakglass.grant`, `breakglass.receipt`, and `breakglass.event` evidence,
- recovery/install/reset work that stays receipted instead of turning into a root-shell folklore lane,
- and stronger maintenance/reset workflows for A/D without making recovery disappear for B/C.

`docs/473-installation-and-recovery-posture-by-profile.md` already fixed that installation/recovery posture is profile-shaped.
`docs/478-evidence-collection-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, and `docs/474-high-risk-approval-posture-by-profile.md` already fixed that evidence, export, and stronger approvals are profile-shaped.
`docs/292-terminal-session-recording-as-evidence.md` already fixed that TTY recording is its own leased evidence lane rather than ambient surveillance.

One expensive ambiguity still remained open:
**what recording/detail/export posture should breakglass normalize in each product shape?**

If the archive leaves that answer open, implementation pressure will pick for us:

- fleet/factory emergency shells quietly become invisible because “it was recovery,”
- workstation recovery quietly becomes either untrailed root folklore or a privacy-toxic universal panic recorder,
- general-purpose installs inherit whichever rescue environment or BMC helper happened to ship first,
- and exported emergency evidence drifts away from the product’s declared evidence/export posture.

This should remain a compiled consequence of existing posture surfaces rather than a new `product.profiles.defaults` key.

## Decision

1. Keep `breakglass.receipt` as the mandatory baseline authoritative evidence object for breakglass across all profiles.
   Even where richer content capture is not normal, the receipt still records who received emergency authority, what scope was granted, which method was used, what session window existed, and which approvals/attestation gates were satisfied.

2. Keep **emergency-session recording posture** profile-shaped rather than universal.
   Breakglass authority does not automatically imply the same recording detail for A, B, C, and D.

3. Keep **TTY/console recording** distinct from mere breakglass admission.
   Output-only TTY/console recording is the default stronger emergency-session evidence lane; TTY input capture is a higher-risk recording scope and is never the routine baseline.

4. Fix the product-shape defaults as follows:
   - **A:** breakglass shell or console sessions normally carry session metadata plus output-only TTY/console recording; TTY input capture is forbidden by default and requires a stronger quorum/exception lane; external sharing stays redacted, encrypted, and incident-scoped.
   - **B:** breakglass stays stronger than ordinary local admin: session metadata is always normal, and if workstation recovery enters a shell/console lane, output-only terminal recording is the default stronger evidence lane, while ambient screen recording and TTY input capture remain explicit trusted-UI/high-risk escalation only; sharing stays trusted-UI-visible, user-mediated, and redaction-aware.
   - **C:** session metadata is always normal for Derive-managed breakglass; output-only TTY recording is preferred for Derive-managed breakglass shells or recovery consoles, while richer capture and classic local rescue environments remain explicit adapter territory rather than inherited baseline posture; sharing stays explicit and redacted by default.
   - **D:** approved offline breakglass or maintenance recovery sessions normally carry session metadata plus output-only TTY/console recording; production images do not normalize richer content capture, and TTY input capture is forbidden by default outside stronger offline/approved exception lanes; exports stay minimal, redacted, and bundle-oriented.

5. Treat exported breakglass recordings as the **smallest sufficient artifact**.
   Profile defaults should prefer metadata-only export when it explains enough, and otherwise use output-only TTY/console capture before richer capture shapes.

## Consequences

- Breakglass now has a real answer to “what emergency evidence becomes routine?” without inventing a new profile knob.
- Fleet and factory recovery can keep strong, reviewable shell trails instead of relying on “recovery mode is outside the normal rules.”
- Workstations keep privacy-respecting recovery by refusing ambient panic recording, but emergency shell work is no longer allowed to hide behind ordinary local-admin assumptions.
- General-purpose OS remains viable without pretending every classic rescue medium or BMC helper inherits the full Derive evidence story automatically.
- Future recovery/breakglass implementations should compile toward this posture instead of defaulting to whichever rescue backend captures either too little or too much.

## Why this is narrow enough

This ADR does **not** standardize:

- exact recovery-media packaging or rescue-shell frontend UX,
- exact retention windows,
- exact offline approval ceremony details,
- exact BMC / virtual-media adapter behavior,
- or exact post-session reverification and remote export tooling.

It only fixes the profile-shaped default for breakglass recording/detail/export posture so later specs and code can converge without invisible emergency shells, privacy-toxic panic recording, or rescue-media folklore.
