# ADR-0206: Remote assistance recording detail and export posture by profile

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/461-remote-assistance-posture-by-profile.md` already fixed **who** remote assistance is for across A–D:

- A stays brokered TTY/console support rather than general host remoting,
- B keeps visible leased view/control with secure attention before control,
- C keeps explicit leased support without ambient helper folklore,
- D keeps remote assistance off the production baseline outside maintenance-shaped workflows.

`docs/291-remote-assistance-sessions-as-evidence.md` and `docs/292-terminal-session-recording-as-evidence.md` already fixed the capability lane and the existence of a typed TTY-recording artifact.
`docs/478-evidence-collection-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, and `docs/474-high-risk-approval-posture-by-profile.md` already fixed that evidence, export, and stronger approvals are profile-shaped.

One expensive ambiguity still remained open:
**what recording/detail/export posture should remote assistance normalize in each product shape?**

If the archive leaves that answer open, implementation pressure will pick for us:

- fleet/factory support quietly grows full-content surveillance or input capture by default,
- workstation support quietly normalizes background content recording,
- general-purpose OS support quietly inherits whichever vendor helper shape lands first,
- and every profile starts exporting richer assistance traces than its evidence/export posture actually intended.

This should remain a compiled consequence of existing posture surfaces rather than a new `product.profiles.defaults` key.

## Decision

1. Keep `support.session` as the mandatory baseline evidence object for remote assistance across all profiles.
   Even where richer content capture is not normal, the session envelope still records who participated, what scopes were granted, which leases existed, and what export path was used.

2. Keep **content recording posture** profile-shaped rather than universal.
   Remote assistance authority does not automatically imply the same recording detail for A, B, C, and D.

3. Keep **TTY recording** distinct from remote-control/screencast authority.
   Output-only TTY recording is the default “stronger content evidence” lane; TTY input capture is a higher-risk recording scope and is never the routine baseline.

4. Fix the product-shape defaults as follows:
   - **A:** brokered admin assistance normally carries session metadata plus output-only TTY/console recording; TTY input capture is forbidden by default and requires a stronger breakglass/quorum lane; external sharing stays redacted, encrypted, and incident-scoped.
   - **B:** session metadata is always normal, but workstation view/control does **not** automatically imply ambient screen/content recording; if support enters a terminal lane, output-only TTY recording is the default stronger evidence lane, while TTY input capture is an explicit trusted-UI escalation; sharing stays recipient-visible, user-mediated, and redaction-aware.
   - **C:** session metadata is always normal; output-only TTY recording is preferred for brokered operator/admin assistance, while richer content capture remains explicit and adapter-visible rather than ambient; sharing stays explicit and redacted by default.
   - **D:** approved maintenance assistance normally carries session metadata plus output-only TTY/console recording; production images do not normalize ambient content recording, and TTY input capture is forbidden by default outside stronger offline/approved exception lanes; exports stay minimal, redacted, and bundle-oriented.

5. Treat exported assistance recordings as the **smallest sufficient artifact**.
   Profile defaults should prefer metadata-only export when it explains enough, and otherwise use output-only TTY capture before richer capture shapes.

## Consequences

- Remote-assistance posture now has a real answer to “what evidence becomes normal?” without inventing a new profile knob.
- Fleet/factory support can keep strong operator trails without normalizing workstation-style surveillance.
- Workstation support can remain privacy-shaped without losing the ability to produce a stronger operator trail when support actually enters a terminal lane.
- General-purpose OS remains viable without pretending that compatibility helpers inherit the brokered evidence story automatically.
- Future support-session and recording schemas should compile toward this posture instead of defaulting to whichever backend captures the most bytes.

## Why this is narrow enough

This ADR does **not** standardize:

- exact relay/provider choice,
- exact retention windows,
- exact screen/video recording artifact shapes,
- exact quorum thresholds for every support scope,
- or exact backend restore-token mapping.

It only fixes the profile-shaped default for remote-assistance recording/detail/export posture so later specs and code can converge without accidental surveillance or folklore support paths.
