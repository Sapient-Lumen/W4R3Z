# ADR-0209: Destructive reprovision evidence detail and export posture by profile

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/473-installation-and-recovery-posture-by-profile.md` and `docs/483-destructive-reprovisioning-and-reset-authority.md` already fixed **who may authorize destructive reprovisioning** and **what typed authority/evidence objects exist**:

- target-bound install/recovery posture by product shape,
- typed `reset.authorization` and `reset.receipt` evidence,
- digest-bound joins to `disk.layout.plan`, `disk.layout.receipt`, and install payloads,
- and stronger approval/presence requirements where A/D need them.

`docs/292-terminal-session-recording-as-evidence.md` already fixed that TTY recording is its own leased evidence lane rather than ambient surveillance.

But one expensive ambiguity remained:

**what evidence/detail/export posture should destructive reprovisioning normalize in each product shape?**

Without that answer:

- fleet reprovisioning can become an invisible remote wipe/reseed ritual,
- workstation reset UX can fall back to screenshots, shell transcripts, or vague “user confirmed it” folklore,
- general-purpose installs can inherit whichever compatibility installer or admin helper happened to run first,
- and factory/regulatory reset lanes can normalize bench rituals or universal camera/video capture instead of typed reset proof.

That ambiguity is especially dangerous because destructive reset sits between several already-decided posture surfaces (`destructive_reprovision`, `installation_recovery`, `evidence`, `evidence_exports`, `high_risk_approvals`) and will otherwise compile differently on every backend.
This ADR therefore fixes the compilation target without inventing a new `product.profiles.defaults` key for reset recording.

## Decision

1. Keep `reset.receipt` as the mandatory baseline authoritative evidence object for destructive reprovisioning across all profiles.
   A destructive reset must always produce typed reset evidence plus the joined `disk.layout.receipt` when storage mutation happened.

2. Keep **destructive-reset evidence posture** profile-shaped rather than universal.
   Reset authority does not automatically imply the same evidence detail for A, B, C, and D.

3. Keep **interactive confirmation proof** distinct from **execution-lane recording**.
   On interactive products, trusted-UI/presence evidence recorded in `reset.receipt.observed_evidence[]` is the normal stronger human-intent proof. Output-only TTY/console recording is the default stronger execution-evidence lane only when reset actually runs through a brokered terminal/maintenance/recovery console lane. Ambient screen/video capture is never the routine baseline.

4. Compile the profile-shaped default as follows:
   - **A:** destructive remote reprovision normally carries `reset.receipt` + `disk.layout.receipt` plus output-only TTY/console recording when execution occurs through a brokered maintenance/admin lane; no hidden reinstall-with-wipe path, no ambient input capture, exports stay incident-scoped and redacted.
   - **B:** destructive local reset always carries `reset.receipt` with trusted-UI disk identity and observed confirmation evidence; output-only terminal recording is the default stronger evidence lane only if workstation reset drops into a terminal/recovery shell lane, while ambient screen recording stays out of baseline posture.
   - **C:** `reset.receipt` is always normal for Derive-managed destructive reset; trusted-UI/admin confirmation evidence is routine, output-only TTY recording is preferred for Derive-managed remote or recovery-console reset flows, and classic installer/admin compatibility paths remain explicit adapter territory rather than inherited baseline truth.
   - **D:** approved factory/regulatory destructive reprovision normally carries `reset.receipt` + `disk.layout.receipt` plus the observed physical/station/quorum evidence that satisfied the authorization, and output-only TTY/console recording is routine when reset executes through an approved maintenance station or offline recovery console; exports stay minimal, redacted, and bundle-oriented.

5. Treat exported destructive-reset evidence as the **smallest sufficient artifact**.
   The normal export is the typed `reset.receipt`, joined `disk.layout.receipt`, and any joined approval/consent/maintenance evidence digests or redacted summaries needed to explain the act. Richer console artifacts remain explicit stronger exports rather than the default product truth.

## Consequences

- DeriveBSD now has one coherent answer to “what proves this destructive reset happened, on purpose, on the intended target?” across A–D.
- Workstations keep humane reset proof without normalizing panic video capture or screenshot archaeology.
- Fleet/factory reprovision stays auditable without requiring every reset to become a universal terminal or camera recording product.
- Future installer/recovery specs can compile toward one evidence package instead of rediscovering whether `reset.receipt`, `disk.layout.receipt`, trusted-UI proof, and TTY/console output are all optional folklore.

## What this does not decide

This ADR does **not** decide:

- the final reset/recovery UI stack,
- the exact shape of terminal/console recording envelopes,
- the exact consent/physical-attendance evidence adapters,
- or whether a future implementation should use one operator tool or several.

Those stay downstream design choices as long as they preserve the typed evidence package and keep authority and recording lanes separately.
This ADR only fixes the profile-shaped default for destructive-reset evidence/detail/export posture so later specs and code can converge without invisible wipe/reseed folklore, privacy-toxic reset capture, or bench-only reset rituals.
