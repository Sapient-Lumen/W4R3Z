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

- `breakglass.receipt` remains the mandatory authoritative evidence object, and it now also carries typed `repair_outcome` closeout truth so shell transcripts and incident notes do not become the only repair story,
- `breakglass.event` entry/exit state remains mandatory whenever breakglass is exercised,
- breakglass authority does **not** automatically imply rich content recording,
- output-only TTY/console recording is the default stronger emergency-session evidence lane,
- for the reviewed interactive breakglass shell/console lane, that stronger recording starts at session open before the first prompt and joins back through `breakglass.receipt.evidence.tty_recording_digests`,
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
- If a reviewed maintenance boot or reset materially enabled the session, `breakglass.receipt.evidence.bootstrap_receipt_joins[]` should pin the exact `boot.override.receipt` / `reset.receipt` digest with `bootstrap_join_posture = pre-session-recovery-path-only` instead of relying on BMC breadcrumbs or virtual-media notes. When plural, `bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only` keeps that array to the actual enabling chain instead of denied attempts or failed dead ends. In the common paired one-time-boot case, keep `boot.override.receipt` before the later `reset.receipt` that actuated it.
- richer adapter launch/runtime detail stays redacted side evidence outside the baseline receipt; `notes` is not a loophole; notes is not a loophole for console URLs, ports, session ids/tokens, image locators, or copied console-entry hints (`docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`).
- breakglass session methods stay concrete at `console` / `serial` / `ssh`; remote-presence plumbing may project into those methods, but it is not a generic `oob` method (`docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`).
- official support handoff stays authority-first on `breakglass_receipt_digests`; if richer adapter/runtime investigation material must travel before a dedicated typed family exists, keep it as supplementary side evidence or external case attachments rather than widening the first-class bundle contract (`docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`).
- when that richer supplementary material does travel, keep the portable story receipt-first on typed redaction/export/transport proof rather than raw attachment ids or portal handles (`docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`).
- that richer supplementary receipt chain still needs the authority anchor: keep at least one exact `breakglass_receipt_digests` join in the same bundle/handoff so later review does not have to infer emergency authority from attachment or transport history alone (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`).
- that same portable story must stay artifactized too: exported artifacts and typed handling receipts may travel, but live console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, image locators, and session tokens do not (`docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`).
- that same portable story must stay payload-anchored too: richer supplementary breakglass evidence should include at least one passive artifact digest or accepted case-object proof so the exported story does not collapse into receipt-only transport archaeology (`docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`).
- if that payload anchor uses accepted case-object proof, keep it object-exact too: name the accepted remote attachment/object/message-part rather than only the surrounding case/ticket/thread/container (`docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`).
- if that same accepted object also exposes a revision/version/generation/ETag-like validator, keep it validator-pinned too when visible instead of letting support handoff slide back into object-latest portal semantics (`docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`).
- if that same accepted object also exposes a protection/retention/hold posture, keep it remote-protection-shaped too when visible instead of quietly treating any accepted portal object as durable evidence by implication (`docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`).
- keep that visible protection posture exact to the same accepted object revision/version too; ambient case/container/bucket policy is context only rather than a substitute for object-exact protection proof (`docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`).
- if that same accepted object also exposes a redacted/non-secret passive locator, keep it remote-locator-continuous too when visible on that same accepted object revision/version instead of falling back to parent case/container browse URLs or portal clicking; live control locators remain forbidden (`docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`).
- if that same accepted object can later be checked metadata-first without re-downloading the body, keep metadata-only reverification too when visible on typed `transport.reverification.receipt`; canonical follow-up keeps `body_downloaded = false` instead of screenshots or body-download folklore (`docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md`).

## What remains open

This doc does **not** freeze:

- exact retention windows,
- exact recovery-media UI or trusted-console UX,
- whether a dedicated adapter-side-evidence artifact family is worth standardizing now that the baseline breakglass receipt stays adapter-thin,
- exact quorum thresholds for every breakglass scope,
- or exact remote reverification / external case-system mapping.

Those are future implementation/spec questions.
The product-shaped default for recording/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It keeps DeriveBSD viable across all four product shapes without forcing fleet/factory recovery, workstation privacy, and general-purpose compatibility into one accidental panic-recorder product or one invisible rescue-shell folklore lane.

Last updated: 2026-03-23r452
