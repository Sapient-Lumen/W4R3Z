# Remote assistance recording detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already decided three important things:

- remote assistance itself is profile-shaped,
- evidence collection/export are profile-shaped,
- and terminal recording is a separate leased evidence lane rather than ambient surveillance.

This doc decides the smaller but expensive follow-on question:
**what recording detail is normal to keep and share for remote assistance in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `remote_assistance`, `evidence`, `evidence_exports`, and `high_risk_approvals` posture surfaces.

See also:
- ADR: `adrs/ADR-0206-remote-assistance-recording-detail-and-export-posture-by-profile.md`
- remote-assistance posture: `docs/461-remote-assistance-posture-by-profile.md`
- support-session lane: `docs/291-remote-assistance-sessions-as-evidence.md`
- TTY recording lane: `docs/292-terminal-session-recording-as-evidence.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- high-risk approvals: `docs/474-high-risk-approval-posture-by-profile.md`

## Why this needs a hard decision

Remote assistance without a recording/detail default is a fork generator.
The authority boundary may look correct on paper, but implementation pressure will still choose what becomes routine:

- fleet and factory support tools start capturing more than operators meant to normalize,
- workstation support quietly turns into privacy-toxic background recording,
- general-purpose installs inherit whichever adapter or vendor helper shipped first,
- and exported support evidence drifts away from the product’s declared evidence/export posture.

A coherent archive needs a durable answer to four questions:

- is `support.session` metadata-only evidence enough by default, or is content capture normal?
- when is output-only TTY recording the right stronger lane?
- when is TTY input capture ever normal?
- what detail is allowed to leave the box or organization boundary by default?

## Accepted baseline

Across all profiles:

- `support.session` remains the mandatory baseline evidence object,
- remote-assistance authority does **not** automatically imply rich content recording,
- output-only TTY recording is the default stronger content-evidence lane,
- TTY input capture is a higher-risk scope than output-only capture and is never the routine baseline,
- and exported assistance evidence should use the smallest artifact that still explains the incident.

That keeps support operable without letting the support lane silently become a generalized surveillance lane.

## Product-shape defaults

| Profile | Local recording/detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `session-metadata-plus-output-only-tty-recording-required-for-brokered-admin-sessions` | `redacted-encrypted-incident-scoped-export` | Fleet support normally keeps a durable operator trail for brokered TTY/console work, but does not normalize input capture or broad off-box session disclosure. |
| **B workstation** | `session-metadata-always-terminal-output-only-when-terminal-assist-is-used-no-ambient-screen-recording` | `recipient-visible-user-mediated-redacted-sharing` | Workstation help sessions are visible and receipted by default; richer content capture is explicit, and ordinary screen/control assistance does not quietly become a full session-recording product. |
| **C general_os** | `session-metadata-always-output-only-tty-preferred-for-brokered-operator-lanes-richer-capture-explicit` | `explicit-redacted-export` | General-purpose installs keep a useful brokered operator trail without pretending every compatibility helper or desktop-share path inherits the full Derive evidence story. |
| **D appliance_factory** | `session-metadata-plus-output-only-tty-recording-required-in-approved-maintenance-lanes-only` | `minimal-redacted-bundle-oriented-export` | Production/factory support remains maintenance-shaped and auditable; richer content capture is not normalized on production images. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of the existing support/evidence/export/approval posture surfaces when remote assistance is in play.

## What this fixes by profile

### A) Secure fleet host

Default: session metadata plus output-only TTY recording for brokered admin assistance.

- Fleet support must leave a credible operator trail when somebody takes a console or TTY lane.
- That justifies output-only terminal evidence as the routine stronger capture lane.
- It does **not** justify normalizing TTY input capture or workstation-style content recording on headless hosts.
- External sharing therefore stays incident-scoped, encrypted, and redacted by default.

### B) Secure workstation

Default: session metadata always; output-only TTY recording only when support actually enters a terminal lane; no ambient screen-content recording.

- Workstations are where remote assistance most easily drifts into privacy-toxic “record everything” habits.
- The archive still needs visible, receipted support and a stronger evidence lane when a helper enters terminal/admin territory.
- So B keeps `support.session` metadata as the routine floor, treats terminal output recording as the normal stronger lane when that lane is used, and keeps TTY input capture or richer content capture behind explicit trusted-UI escalation.
- Sharing remains recipient-visible, user-mediated, and redaction-aware.

### C) General-purpose OS

Default: session metadata always; output-only TTY recording preferred for brokered operator/admin assistance; richer capture explicit.

- C needs practical support without assuming a single blessed vendor tool or a hidden collector backend.
- Brokered/operator assistance should still leave a useful output-only trail by default.
- Compatibility helpers and richer desktop-share capture remain explicit lanes, not ambient inherited posture.
- Export stays explicit and redacted rather than “support helper uploads whatever it has.”

### D) Appliance factory / regulatory

Default: approved maintenance assistance keeps session metadata plus output-only TTY recording; production images do not normalize richer content capture.

- D often needs a durable operator trail more than it needs an expansive content log.
- Output-only TTY/console recording in approved maintenance lanes fits the regulatory/forensics shape without normalizing broad capture on production images.
- TTY input capture is forbidden by default outside stronger offline/approved exception lanes.
- Export stays minimal, redacted, and bundle-oriented.

## Cross-profile invariants

Regardless of profile:

- `support.session` is mandatory whenever remote assistance is used,
- recording authority is separate from file transfer/export authority,
- TTY input capture is stronger than output-only TTY recording,
- support backends must not smuggle remembered recording posture in a restore token or ambient agent,
- and exported assistance artifacts should prefer metadata-only or output-only forms before richer capture.

## What remains open

This doc does **not** freeze:

- exact retention windows,
- exact screen/video recording artifact shapes,
- exact relay/provider posture,
- exact quorum thresholds for every support scope,
- or exact restore-token / adapter mapping.

Those are future implementation/spec questions.
The product-shaped default for recording/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It keeps DeriveBSD viable across all four product shapes without forcing fleet/factory support, workstation privacy, and general-purpose compatibility into one accidental support product.

Last updated: 2026-03-21r346
