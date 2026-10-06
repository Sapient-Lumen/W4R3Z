# Glossary (canonical)

- **Spec**: user-authored, typed intent (declarative).
- **Lock**: fully resolved sources + hashes + constraints.
- **Plan**: machine-produced dependency DAG + steps + policy decisions.
- **Artifact**: immutable build output in the store.
- **Closure**: artifact plus its transitive runtime dependencies.
- **Realizer**: executes a Plan to produce Artifacts.
- **Store**: artifact storage (hash-addressed and/or content-addressed).
- **Cache**: remote distribution of artifacts + metadata + signatures.

- **Attestation**: verifiable statement about how/what was built.
- **Supplychain layout policy**: a signed object binding an in-toto layout (workflow declaration) and its trust roots, used as an optional promotion/verification gate.
- **Supplychain verification receipt**: evidence that a set of attestations satisfied a layout policy for a specific artifact (pass/fail + reasons).
- **TUF adapter**: optional compatibility lane that publishes/ingests full TUF repository metadata for channels.

- **Activation broker**: a supervisor that pre-opens and rights-minimizes capabilities for a service, hands them off at start, and may escrow them across restarts.
- **svcdb**: compiled service database derived from the Plan: services, placement, dependencies, restart policy, bundles.
- **statedb**: compiled state database derived from the Plan: persistent volumes, schema ids/versions, and snapshot/migration policy.
- **state-snapshot**: runtime snapshot of persistent volumes and their observed schema versions, with pointers to the latest migration receipts.
- **state-migration-plan**: explicit, signed plan listing ordered per-volume state migrations required between generations (artifact digests, timeouts, placement).
- **state-migration-receipt**: evidence emitted per volume migration (from/to versions, pre-snapshot + hold tag, success/failure, event pointers).
- **change-set**: signed multi-step transition plan that references config/state/service component plans and required checks.
- **change-receipt**: evidence emitted by the apply engine summarizing per-step receipts/events and the final commit/rollback decision.
- **sysctl-plan**: explicit plan listing runtime sysctl key/value mutations to apply (and whether missing keys are errors).
- **sysctl-receipt**: evidence emitted for a sysctl plan (old/new values per key, status).
- **sysctl-event**: typed event for sysctl application/drift/denial, used for live monitoring and incident context.
- **kmod-policy**: signed policy describing which kernel modules may be loaded (and under what constraints).
- **kmod-policy-diff**: typed diff surface summarizing drift between two module policies (rules/defaults), used for review bundles and promotion gates.
- **kmod-load-plan**: explicit plan listing kernel modules to preload during activation (with digests and reasons).
- **kmod-load-receipt**: evidence emitted for module loading (loaded/denied modules + posture knobs like lockdown/securelevel).
- **kmod-event**: typed event for kernel module load/unload/denial/drift.
- **fw-device-inventory**: privacy-safe inventory snapshot of firmware-bearing components and their observed versions + update mechanisms.
- **fw-update-plan**: explicit plan referencing firmware payloads by digest, including preconditions and mechanisms (capsule, NVMe slot, BMC, etc.).
- **fw-update-receipt**: append-only evidence emitted for a firmware update plan (per-component outcome, versions, reboot requirement, event pointers).

- **storage-pool-inventory**: privacy-safe inventory snapshot of pools/vdev topology (device ids hashed by default).
- **storage-health-snapshot**: compact view of pool health, errors, last scrub outcome, and device health summaries.
- **storage-scrub-plan**: explicit plan to run integrity scrubs (targets, time window, throttling hints).
- **storage-scrub-receipt**: append-only evidence emitted for scrub execution (what was checked, what was found/repaired, event pointers).
- **storage-event**: typed event record for pool health transitions and scrub/resilver/checkpoint milestones.
- **pool checkpoint**: a pool-wide rewind point (distinct from snapshots) used as an optional, policy-gated safety valve for risky maintenance.

- **svc.snapshot**: runtime snapshot of service states (online/offline/degraded/maintenance) plus evidence pointers.
- **event.record**: a common envelope for structured host events (service transitions, fault reports, audit/policy milestones).
- **event.segment**: journal segment metadata evidence binding an on-disk event segment to digests (file digest, Merkle root, continuity chain heads).
- **incident.bundle**: a bounded, verifiable support/incident snapshot that packages selected evidence (event segments, svc/fault snapshots) into a shareable payload (optionally encrypted/redacted).
- **debug.record.grant**: explicit, time-bounded authority to perform privileged record/replay capture for a specific target under declared constraints.
- **debug.replay.capsule**: evidence object binding a recording trace/snapshot digest (and side artifacts) to a grant digest, making failures deterministically replayable.
- **debug-event**: structured event-journal record emitted by the debug broker (record start/stop, capsule emitted, export attempts), optionally correlated to a change.
- **breakglass-grant**: explicit, time-bounded authorization for emergency recovery access (who/where/what scope).
- **breakglass-receipt**: evidence of an approved breakglass session (approvals, method, timebox).
- **breakglass-event**: typed structured-journal event for breakglass entry/exit/extension/denial.
- **operator.session**: typed envelope describing an operator login session (SSH/console), with principal, constraints, lease pointers, and optional TTY recording digests.
- **lint-report**: typed output from lints/compilers (`derive lint --json`), used for gating and incident context.
- **svc.event**: append-only supervision event for a service (transitions, restarts, crashes, maintenance).
- **Time authority**: a leased, policy-governed grant describing what wall clock/entropy a process may observe (deterministic profiles for builds/tests).

- **Portal**: a mediated broker for dynamic authority acquisition (file picks, leased debug/trace grants, bookmarks, clipboard/data-transfer offers).
- **Bookmark**: a signed, persistable claim ticket for re-acquiring a narrow file capability via the portal (revocable; evidence-bearing).
- **Intent router**: a capability-mediated service that resolves open/view/share requests to handlers and brokers the handoff, emitting route receipts.

- **Time source policy**: a signed policy describing acceptable secure time sources (e.g., NTS/Roughtime) and quorum/skew rules.
- **Time proof bundle**: a signed evidence object from `system.time` capturing time observations and the agreement decision under policy.
- **time-source-inventory**: inventory of time sources available on a host (NTP/NTS/PTP/RTC/optional sources).
- **time-sync-plan**: explicit plan describing how the host disciplines the clock (sources, auth mode, step/slew policy).
- **time-sync-snapshot**: compact snapshot of time sync health (state, offset/uncertainty, reference source, last sync).
- **time-sync-receipt**: append-only evidence for time actions (step/slew/source changes/leap handling).
- **time-requirement**: policy-shaped gate describing what “good enough time” means for a workflow.
- **time-event**: typed structured journal event for time discipline milestones and clock steps.
- **Net egress grant**: a signed authorization permitting limited outbound network actions (DNS/connect rules), typically enforced by `system.net`.

- **Device domain**: a dedicated microVM that owns passthrough hardware (USB/NIC/GPU) and exports narrow services to other domains; used to reduce hardware driver blast radius.
- **Device profile**: host classification evidence for a device endpoint/controller, including risk tags (e.g., HID danger classes) used as policy input.

- **Data offer**: a scoped, expiring object representing transferable data (clipboard entry / drag&drop payload) that can be granted by a portal with constraints and optional redaction binding.
- **ScreenCast grant**: a leased authorization to produce a screen share stream (monitor/window/virtual) through a portal broker.
- **RemoteDesktop grant**: a leased authorization to inject input (keyboard/pointer/touch) through a portal broker.
- **Camera grant**: a leased authorization to access camera capture as a brokered stream.
- **Audio capture grant**: a leased authorization to access microphone/audio capture as a brokered stream.


- **Notification broker (non-observing)**: a host service that accepts publish/withdraw requests but does not reveal whether notifications were shown/clicked/dismissed.
- **Secure Attention Key (SAK)**: a reserved key chord that transfers control to a host-controlled trusted prompt path.
- **Trusted prompt mode**: a visually distinctive host UI mode entered via SAK for credential entry and sensitive approvals.
- **Input stream grant**: a leased authorization for a workload to receive brokered keyboard/pointer events, typically constrained to focus/surface.

- **Portal session**: a long-lived portal-mediated capability (e.g. screencast stream) identified by a session_id; closed/revoked independently of the original request.
- **Portal permission store**: persistent, revocable storage of remembered portal grants (“allow this app to do X again”) bound to request/prompt digests.
- **Location portal**: brokered access to geolocation (coarse-first, policy-gated, receipted).
- **Printing portal**: brokered access to printing/spooling destinations (printer/PDF/remote), avoiding ambient spooler access.

- **Content origin**: an evidence record binding a content digest to its capture context (`content.origin`), used to answer “where did this file come from?”
- **Quarantine label**: file metadata (xattr/sidecar) pointing to a content origin record and marking content as untrusted until explicitly imported/sanitized.
- **content-import-plan**: a typed plan describing how inbound bytes will be scanned/sanitized/unpacked/placed (`content.import.plan`).
- **content-import-receipt**: append-only evidence emitted for an import attempt (including denials) that records outputs, quarantine state, and per-step results (`content.import.receipt`).


- **config-plan**: explicit transition plan for candidate→active system configuration (including validators and optional confirm window).
- **config-snapshot**: compact view of effective configuration roots (digests + pointers) on a host at a time.
- **config-receipt**: append-only evidence emitted for config apply/confirm/rollback attempts.
- **commit-confirmed**: safety mode where config changes auto-rollback unless explicitly confirmed within a timeout.

- **secret-policy**: signed inventory and access rules for secrets (ids, sources, rotation expectations, delivery constraints).
- **secret-grant**: time-bounded authorization to materialize a secret for a subject via the credential broker.
- **secret-snapshot**: safe host-local view of secret health/rotation state (never includes secret bytes).
- **secret-receipt**: evidence emitted for provisioning/rotation/unseal/materialization actions (metadata-only).
- **secret-event**: typed event-journal record for secret access/denials/rotation milestones (metadata-only).

- **pki-trust-bundle**: signed, versioned trust-root artifact (TLS/SSH/package-signing anchors) referenced by services and policy.
- **pki-issue-plan**: desired issuance/renewal plan for an identity slot (issuer backend, subject/SANs/usages, key reference).
- **pki-issue-receipt**: append-only evidence emitted for issue/renew/install outcomes (serial, validity, chain digests; no key bytes).
- **pki-event**: typed event-journal record for PKI milestones (bundle update, issuance, renewal, install failure).


- **resource-policy**: signed, structured declaration of resource budgets/caps/shares per subject (service/workload/jail/vm), suitable for fleet rollout.
- **resource-receipt**: append-only evidence emitted for resource policy apply attempts (backend, applied rules, result).
- **resource-snapshot**: compact view of effective resource limits and coarse usage/pressure per subject at a time.
- **resource-event**: typed event record for resource violations, pressure, and enforcement actions.


- **crash-report**: metadata-first evidence object describing a crash, with digests to heavy artifacts (minidump/core/kernel dump).
- **crash-event**: typed event emitted when a crash is observed; used for correlation and fleet queries.
- **build-id**: stable identifier embedded in an object file used to look up matching debug symbols.
- **symbolication**: mapping crash addresses to function/file/line using debug symbols (ideally via build-id lookups).
- **debuginfod**: HTTP service that returns debug files by build-id (symbol server ergonomics).

Avoid (unless intentionally adopted): derivation/flake/channel/profile.

Last updated: 2026-02-26

## Attestation receipt
A signed verifier statement (`attestation.receipt`) binding evidence (e.g. `boot.attestation`) to reference values/policy and a verdict, with an expiry.

## Attestation reference
Reference values (`attestation.reference`) describing what “good” looks like for a policy scope (boot manifests, PCR selection, optional runtime policy).

## Attestation requirement
A small gate object (`attestation.requirement`) describing freshness + minimum verdict for accepting receipts.
