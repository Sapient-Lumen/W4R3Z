# ADR-0207: Operator-access recording detail and export posture by profile

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/467-operator-access-posture-by-profile.md` already fixed **who** operator access is for across A–D:

- A stays brokered, JIT, certificate-based, role-shell-first, and separate from escalation,
- B keeps local secure-attention/user-presence admin as the default and remote shell admin exceptional,
- C keeps classic local admin viable while Derive-managed remote admin stays leased/JIT preferred,
- D keeps maintenance-window-shaped operator access and forbids standing vendor/admin keys by default.

`docs/311-operator-access-leases-and-ssh-certs.md` and `docs/292-terminal-session-recording-as-evidence.md` already fixed the capability lane and the existence of typed `operator.session` and `tty.session.recording` evidence.
`docs/478-evidence-collection-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, and `docs/474-high-risk-approval-posture-by-profile.md` already fixed that evidence, export, and stronger approvals are profile-shaped.

One expensive ambiguity still remained open:
**what recording/detail/export posture should operator access normalize in each product shape?**

If the archive leaves that answer open, implementation pressure will pick for us:

- fleet shell access quietly becomes an unrecorded bastion habit,
- workstation admin helpers quietly normalize ambient local or remote privileged-session recording,
- general-purpose installs inherit whichever SSH/session-recorder folklore arrived first,
- and factory/regulatory maintenance lanes quietly export richer operator traces than the product’s evidence/export posture actually intended.

This should remain a compiled consequence of existing posture surfaces rather than a new `product.profiles.defaults` key.

## Decision

1. Keep `operator.session` as the mandatory baseline evidence object for brokered/operator-managed access across all profiles.
   Even where richer content capture is not routine, the session envelope still records who authenticated, what scopes were granted, which leases existed, which transport was used, and what export path was used.

2. Keep **content recording posture** profile-shaped rather than universal.
   Operator-access authority does not automatically imply the same recording detail for A, B, C, and D.

3. Keep **TTY recording** distinct from mere session admission.
   Output-only TTY recording is the default stronger content-evidence lane; TTY input capture is a higher-risk recording scope and is never the routine baseline.

4. Fix the product-shape defaults as follows:
   - **A:** brokered remote operator sessions normally carry session metadata plus output-only TTY/console recording; TTY input capture is forbidden by default and requires a stronger breakglass/quorum lane; external sharing stays redacted, encrypted, and incident-scoped.
   - **B:** session metadata is always normal for brokered operator sessions, but local secure-attention elevation does **not** automatically imply ambient terminal recording; if workstation operator access enters a remote-shell or breakglass terminal lane, output-only TTY recording is the default stronger evidence lane, while TTY input capture is an explicit trusted-UI/high-risk escalation; sharing stays trusted-UI-visible, user-mediated, and redaction-aware.
   - **C:** session metadata is always normal for Derive-managed operator sessions; output-only TTY recording is preferred for brokered remote operator/admin assistance, while richer capture remains explicit and adapter-visible rather than ambient; sharing stays explicit and redacted by default.
   - **D:** approved maintenance operator sessions normally carry session metadata plus output-only TTY/console recording; production images do not normalize ambient content recording, and TTY input capture is forbidden by default outside stronger offline/approved exception lanes; exports stay minimal, redacted, and bundle-oriented.

5. Treat exported operator-session recordings as the **smallest sufficient artifact**.
   Profile defaults should prefer metadata-only export when it explains enough, and otherwise use output-only TTY capture before richer capture shapes.

## Consequences

- Operator-access posture now has a real answer to “what evidence becomes normal?” without inventing a new profile knob.
- Fleet/factory operator lanes keep strong reviewable shell trails without normalizing workstation-style surveillance or permanent bastion folklore.
- Workstations keep local-presence admin humane without silently turning ordinary privileged local work into an ambient recorder, while remote/breakglass shell work still lands in a stronger evidence lane.
- General-purpose OS remains viable without pretending every static-key or compatibility helper automatically inherits the brokered evidence story.
- Future operator-session and recording schemas should compile toward this posture instead of defaulting to whichever backend captures the most bytes.

## Why this is narrow enough

This ADR does **not** standardize:

- exact role-shell / forced-command vocabulary,
- exact retention windows,
- exact workstation local-elevation UX,
- exact broker/CA partition handling,
- or exact long-running session renewal/revoke semantics.

It only fixes the profile-shaped default for operator-access recording/detail/export posture so later specs and code can converge without static-key relapse, ambient privileged-session recording, or folklore maintenance lanes.
