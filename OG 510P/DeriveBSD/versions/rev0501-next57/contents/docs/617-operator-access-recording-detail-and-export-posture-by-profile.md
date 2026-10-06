# Operator-access recording detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already decided three important things:

- operator access itself is profile-shaped,
- evidence collection/export are profile-shaped,
- and terminal recording is a separate leased evidence lane rather than ambient surveillance.

This doc decides the smaller but expensive follow-on question:
**what recording detail is normal to keep and share for operator access in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `operator_access`, `evidence`, `evidence_exports`, and `high_risk_approvals` posture surfaces.

See also:
- ADR: `adrs/ADR-0207-operator-access-recording-detail-and-export-posture-by-profile.md`
- operator-access posture: `docs/467-operator-access-posture-by-profile.md`
- operator-session lane: `docs/311-operator-access-leases-and-ssh-certs.md`
- TTY recording lane: `docs/292-terminal-session-recording-as-evidence.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- high-risk approvals: `docs/474-high-risk-approval-posture-by-profile.md`

## Why this needs a hard decision

Operator access without a recording/detail default is a fork generator.
The admission boundary may look correct on paper, but implementation pressure will still choose what becomes routine:

- fleet and factory operators drift back toward unrecorded shell folklore or broad bastion reuse,
- workstation admin helpers quietly normalize ambient privileged-session recording,
- general-purpose installs inherit whichever recorder or bastion pattern shipped first,
- and exported operator evidence drifts away from the product’s declared evidence/export posture.

A coherent archive needs a durable answer to four questions:

- is `operator.session` metadata-only evidence enough by default, or is content capture normal?
- when is output-only TTY recording the right stronger lane?
- when is TTY input capture ever normal?
- what detail is allowed to leave the box or organization boundary by default?

## Accepted baseline

Across all profiles:

- `operator.session` remains the mandatory baseline evidence object,
- operator-access authority does **not** automatically imply rich content recording,
- output-only TTY recording is the default stronger content-evidence lane,
- TTY input capture is a higher-risk scope than output-only capture and is never the routine baseline,
- and exported operator evidence should use the smallest artifact that still explains the privileged action.

That keeps operator access operable without letting the admin lane silently become a universal privileged-session recorder.

## Product-shape defaults

| Profile | Local recording/detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `session-metadata-plus-output-only-tty-recording-required-for-brokered-remote-operator-sessions` | `redacted-encrypted-incident-scoped-export` | Fleet admin normally keeps a durable brokered shell/console trail, but does not normalize input capture or broad off-box privileged-session disclosure. |
| **B workstation** | `session-metadata-always-output-only-tty-only-for-remote-or-breakglass-operator-sessions-no-ambient-local-admin-recording` | `trusted-ui-visible-user-mediated-redacted-sharing` | Workstation admin stays visible and receipted by default; stronger content capture is explicit, and ordinary local elevation does not quietly become a privileged-session recording product. |
| **C general_os** | `session-metadata-always-output-only-tty-preferred-for-brokered-remote-admin-lanes-local-admin-recording-explicit` | `explicit-redacted-export` | General-purpose installs keep a useful Derive-managed remote-admin trail without pretending every compatibility helper, static-key adapter, or classic local shell inherits the full Derive evidence story. |
| **D appliance_factory** | `session-metadata-plus-output-only-tty-recording-required-in-approved-maintenance-operator-lanes-only` | `minimal-redacted-bundle-oriented-export` | Production/factory operator access remains maintenance-shaped and auditable; richer content capture is not normalized on production images. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of the existing operator/evidence/export/approval posture surfaces when operator access is in play.

## What this fixes by profile

### A) Secure fleet host

Default: session metadata plus output-only TTY recording for brokered remote operator sessions.

- Fleet operator access must leave a credible privileged-session trail when somebody takes an SSH, serial, or console lane.
- That justifies output-only terminal evidence as the routine stronger capture lane.
- It does **not** justify normalizing TTY input capture or broad off-box session sharing.
- External sharing therefore stays incident-scoped, encrypted, and redacted by default.

### B) Secure workstation

Default: session metadata always; output-only TTY recording only for remote or breakglass operator sessions; no ambient local-admin recording.

- Workstations are where operator access most easily drifts into privacy-toxic “record every privileged action” habits.
- The archive still needs visible, receipted admin work and a stronger evidence lane when a helper enters remote-shell or breakglass territory.
- So B keeps `operator.session` metadata as the routine floor, treats output-only terminal recording as the normal stronger lane only for remote/breakglass operator sessions, and keeps input capture or richer capture behind explicit trusted-UI escalation.
- Sharing remains trusted-UI-visible, user-mediated, and redaction-aware.

### C) General-purpose OS

Default: session metadata always; output-only TTY recording preferred for brokered remote operator/admin lanes; local-admin recording explicit.

- C needs practical admin paths without assuming a single blessed vendor tool or a hidden collector backend.
- Derive-managed remote operator access should still leave a useful output-only trail by default.
- Compatibility helpers, static-key adapters, and classic local admin remain explicit lanes, not ambient inherited posture.
- Export stays explicit and redacted rather than “the admin helper uploads whatever it has.”

### D) Appliance factory / regulatory

Default: approved maintenance operator access keeps session metadata plus output-only TTY recording; production images do not normalize richer content capture.

- D often needs a durable operator trail more than it needs an expansive content log.
- Output-only TTY/console recording in approved maintenance lanes fits the regulatory/forensics shape without normalizing broad capture on production images.
- TTY input capture is forbidden by default outside stronger offline/approved exception lanes.
- Export stays minimal, redacted, and bundle-oriented.

## Cross-profile invariants

Regardless of profile:

- `operator.session` is mandatory whenever Derive-managed operator access is used,
- recording authority is separate from login, escalation, and file-transfer/export authority,
- TTY input capture is stronger than output-only TTY recording,
- operator-access backends must not smuggle remembered recording posture through ambient agents or standing bastion config,
- and exported operator artifacts should prefer metadata-only or output-only forms before richer capture.

## What remains open

This doc does **not** freeze:

- exact role-shell / forced-command vocabulary,
- exact retention windows,
- exact workstation local-elevation affordances,
- exact offline/partitioned broker behavior,
- or exact renewal/revoke semantics for long-running sessions.

Those are future implementation/spec questions.
The product-shaped default for recording/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It keeps DeriveBSD viable across all four product shapes without forcing fleet/factory shell evidence, workstation local admin, and general-purpose compatibility into one accidental privileged-session recorder.

Last updated: 2026-03-21r347
