# Incident snapshots + support bundles as evidence (sosreport / Apport / ABRT lessons)

Every OS eventually needs a “send me the context” workflow.
Most ecosystems build this as a pile of scripts (or a vendor support tool) that:
- runs commands
- slurps logs
- zips everything
- and then prays secrets didn’t leak

DeriveBSD is in a rare position: **we can bake the incident bundle format into the evidence model**.
That makes debugging, vendor support, and fleet ops far safer and far more automatable.

## Prior art worth stealing

- **`sos report`**: standardized “diagnostic bundle” collection for support (system config, running services, logs, command output).  
  Reference: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/generating_sos_reports_for_technical_support/index
- **Apport (Ubuntu)**: crash reports are useful but can contain sensitive data; privacy and review gates matter.  
  Reference: https://wiki.ubuntu.com/Apport
- **ABRT (Fedora/RHEL)**: problem detectors + report generation; encourages structured reports rather than ad-hoc logs.  
  Reference: https://fedoraproject.org/wiki/Automatic_Bug_Reporting_Tool
- **systemd-coredump**: core dumps are objects with metadata; retrieval is a separate tool (`coredumpctl`).  
  Reference: https://www.freedesktop.org/software/systemd/man/systemd-coredump.html

## DeriveBSD direction

Treat “incident context” as a **first-class artifact target**:

Crashes should plug into this directly via `crash-report` evidence (metadata-first), with dump blobs only included when explicitly enabled by policy.
See: `docs/224-crash-artifacts-and-symbolication-as-evidence.md`.


- `incident.bundle` — a small evidence object that describes what was captured
- a bundle payload blob (e.g. `tar.zst`) referenced by digest

Bundles are not “logs”. They are **bounded, policy-governed snapshots** built from existing evidence streams.

### Goals

- Make incident context **shareable without ambient root**.
- Make bundles **bounded** (size/time) and **verifiable** (digests/signatures).
- Make privacy defaults good:
  - no secrets by construction
  - deterministic redaction transforms at export/view time
  - optional encryption by recipient
- Make bundles composable:
  - include pointers to store objects instead of copying them
  - include only the minimum raw bytes needed for the incident

## Profile-shaped bundle posture

`incident.bundle` is universal, but the *default expectation* for how incidents are captured and handed off is now profile-shaped (see `docs/478-evidence-collection-posture-by-profile.md`):

- **A / fleet host**: bundles are built from always-on bounded evidence that already exists locally.
- **B / workstation**: bundle creation and sharing stay trusted-UI-visible and user-mediated.
- **C / general OS**: bundles remain locally buildable without a mandatory remote collector or support service.
- **D / appliance/factory**: bundles are the normal production evidence handoff surface, and minimal/redacted posture is the default rather than an afterthought.

### What goes in a bundle (suggested default profile)

Think “enough to explain the system”, not “vacuum the disk”.

- **Identity + generation**
  - host id, boot id
  - active generation digest + channel assignment
- **Ops snapshots**
  - `svc.snapshot` (what’s up/down)
  - `fault.snapshot` (what the host thinks is broken)
  - `config-snapshot` (what configuration is effective)
  - recent `config-receipt` records (what changed, and whether it was confirmed)
  - recent `change-receipt` records (multi-step change outcomes + rollbacks)
  - `state-snapshot` (what schema versions are present)
  - `lease-snapshot` (which temporary authority leases were active at capture time; metadata-only)
- `resource-snapshot` (effective limits + pressure summary)
  - recent `resource-receipt` records (policy application outcomes)
  - `fw-device-inventory` (firmware-bearing component inventory)
  - recent `fw-update-receipt` records (firmware change outcomes)
  - `pki-trust-bundle` (trust roots in effect for identity verification)
  - recent `pki-issue-receipt` records (issuance/renewal/install outcomes; metadata-only)
  - `storage-health-snapshot` (pool health, last scrub outcome, device health summaries)
  - recent `storage-scrub-receipt` records (integrity verification outcomes)
  - (optional) `storage-pool-inventory` (vdev topology; device ids hashed)
- **Packet-capture joins**
  - `packet.capture.session` digests when bounded packet capture participated in the incident
  - `packet.capture.summary` digests as the default review/export surface
  - `content.import.packet-capture.receipt` digests when a stronger imported artifact entered the safe-open lane
  - packet-capture `redaction.receipt` digests when a stronger artifact yielded a normalized derivative (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`)
- **Event ranges**
  - bounded `event.segment` references for the relevant time window
  - an `incident.timeline` digest for human orientation by default
    (see `docs/419-incident-timelines-as-derived-artifacts.md`)
- **Recent decisions**
  - recent `policy-decision` records (digests)
  - recent activation/health gate records
- **Optional crash payloads** (explicitly requested)
  - coredumps/minidumps (policy gated; size capped)
  - replay capsules (`debug.replay.capsule`) (only if a `debug.record.grant` existed and policy allows)

Bundles should prefer **references by digest** to store objects and only embed copies when an operator requests it.


## Official support handoff contract

DeriveBSD now treats the **official support handoff** as a small typed contract rather than “whatever the collector happened to zip up”.

The canonical handoff is:

1. `incident.timeline` — one-page human orientation
2. `incident.bundle` — metadata envelope
3. `bundle.plan` — deterministic selection + transforms
4. `bundle.payload.manifest` — deterministic member listing
5. `bundle.build.receipt` — plan→bytes binding

If the bundle actually leaves the machine, add the existing export lane objects (`export.receipt`, and optionally `consent.receipt` / `transport.receipt` / `export.transparency.entry`).

The canonical payload format is **`tar.zst`**. `zip` remains an explicit compatibility adapter, not the default support-bundle contract. The canonical foreign-intake shapes now mirror that choice: `spec/content.import.support-bundle.plan.schema.json` and `spec/content.import.support-bundle.receipt.schema.json` describe the typed `tar.zst` intake profile rather than inventing a second support import kind.

This means a support bundle should open with the story (`incident.timeline`), not a directory walk.

## safe-open intake path

Support bundles are foreign artifacts too.
The official intake path is now:

- import through `content.import.plan` / `content.import.receipt`,
- unpack/preview inside a disposable no-network compartment,
- orient with `incident.timeline` + `bundle.payload.manifest` first,
- and only then stage deeper reproduction if needed.

That keeps the bundle a foreign evidence package instead of encouraging responders to untar and inspect raw bytes on the long-lived host.
See `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`.

## Data model

See `spec/incident.bundle.schema.json`.

Key fields:

- `trigger`: why the bundle was created (manual, fault, crash, failed health gate)
- `scope`: time bounds and inclusion knobs
- `includes`: digests of included evidence objects + journal segments
- `includes.packet_capture_*`: first-class digest joins for packet-capture session/summary/import/redaction evidence when packet troubleshooting participated
- `redaction`: transform digest (see `docs/195-deterministic-redaction-transforms.md`)
- `includes.incident_timeline_digest`: digest of the default human orientation surface when present
- `payload`: bundle blob digest + packaging/encryption metadata

## Security + privacy

### 1) Collection runs in a tight compartment

A bundle collector should run as a supervised service in its own service jail and:
- only read from approved sources (event journal API, snapshot APIs)
- never have ambient filesystem traversal
- emit an `incident.bundle` evidence object signed by the host

### 2) Privacy gates are the default

Apport’s lesson is blunt: crash context often contains secrets.
DeriveBSD should treat “include memory/coredumps” as:
- **off by default**
- **explicitly granted** (and time-bounded)
- optionally “encrypt-for-recipient” by default

### 3) Bundles are exportable but not mutable

- Stored bundles are immutable blobs addressed by digest.
- Redaction happens at **export/view time** (deterministic transforms with receipts).
- Policy can require that exported bundles include redaction receipts.

## CLI affordances (suggested)

- `derive incident bundle --since 30m` (manual support bundle; emits `incident.timeline` by default)
- `derive incident bundle --trigger fault:<id>`
- `derive export --policy <export.policy-digest> --artifact <bundle-digest> --ticket CASE-…` (policy-bound export; emits `export.receipt`)

## Integration points

- Health-gated updates: on rollback, produce an `incident.bundle` with the failing health evidence (including `state-snapshot` when relevant).
- Fault management: detectors can request a bounded bundle when a new critical fault appears.
- Service supervision: persistent flapping can trigger an operator-facing “collect context” suggestion.
- Time-travel debugging: if a record/replay capture ran, the bundle can reference the resulting `debug.replay.capsule` digest (see `docs/220-operational-time-travel-debugging.md`).
- Remote assistance: if a support session occurred, include the `support.session` envelope and referenced UI/network/export receipts (see `docs/291-remote-assistance-sessions-as-evidence.md`).
- Platform posture: when enabled, include `boot.attestation` and verifier `attestation.receipt` digests so incidents capture *what the verifier believed* (see `docs/226-platform-posture-and-attestation-results-as-evidence.md`).
- Packet capture stays summary-first: bundles may include `packet.capture.session` digests, typed `packet.capture.summary` digests, and when relevant the matching packet-capture import/redaction receipt digests, but should not include raw packet payloads by default; raw packet payload export remains an explicit stronger policy/approval path (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/509-packet-capture-selector-compiler-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`).
- If a bundle references a retained local raw artifact at all, the ordinary expectation is `metadata_posture = packet-records-only`; richer sideband/decryption-bearing packet files belong to the typed safe-open packet-capture intake profile and normalize-before-promotion lane rather than the default support bundle contract (`docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`).
- When a stronger imported packet capture yields a normalized derivative, the bundle should carry the matching packet-capture import + redaction receipt digests alongside the summary/session joins; otherwise keep the workflow summary-first and do not treat the derived raw bytes as an ordinary handoff object (`docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`).
- Bootchain revocation: if boot or admission failed due to allowlist/revocation policy, include the referenced `bootchain.policy` digests (see `docs/244-bootchain-revocation-and-allowlists.md`).
- Time discipline: include `time-sync-snapshot` (and recent `time-sync-receipt` digests) so incident timelines can be interpreted correctly when clocks step or drift (see `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`).
- Breakglass sessions: include recent `breakglass-receipt` digests (metadata only) so postmortems can see whether emergency access occurred (see `docs/236-breakglass-and-recovery-mode.md`).
- Lease state: include a `lease-snapshot` digest and relevant `lease-revoke-event` ids so postmortems can see what temporary authority was live (and what was revoked) around the incident (see `docs/249-lease-registry-and-cross-lane-revocation.md`).
- Lint context: include relevant `lint-report` digests from compilers/validators so support can see the exact “complaints” that preceded the incident (see `docs/237-lint-reports-and-contract-testing.md`).
- Causality graphs: include a `causality.graph` digest when available to make “what caused what” mechanically navigable (see `docs/246-causality-graphs-and-minimal-evidence-bundles.md`).
- Export policies + receipts: when bundles are shared externally, record an `export.receipt` digest and cite the governing `export.policy` digest (see `docs/251-export-policies-and-support-bundle-portal.md`).
- Transport/consent/transparency receipts (optional): include `consent.receipt`, `transport.receipt`, and `export.transparency.entry` digests when available to strengthen auditability (see `docs/256-consent-ux-contract.md`, `docs/255-policy-constrained-transports.md`, `docs/254-export-transparency-logs.md`).
- Bundle plans + build receipts: when using `bundle-min`, include the `bundle.plan` digest (selection + transforms) and the `bundle.build.receipt` digest (plan→bytes binding) for reproducibility and explainability (see `docs/253-bundle-plans-and-deterministic-exports.md`).

Last updated: 2026-03-09r242
