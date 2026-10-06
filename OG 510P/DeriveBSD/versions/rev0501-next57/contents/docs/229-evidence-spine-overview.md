# Evidence spine: receipts everywhere (why DeriveBSD treats operations like builds)

DeriveBSD’s “Spec → Lock → Plan → Artifact” pipeline is only half the story.
The other half is that **operations are also artifacts**: every privileged or security-relevant action should produce a **typed, immutable receipt** that can be queried, shipped, and audited.

This “evidence spine” is how we keep the system **explainable** when something goes wrong:
- *What changed?* (change sets + apply receipts)
- *What did the host observe?* (structured event journal)
- *What is the host’s current declared state?* (snapshots)
- *What did the system decide and why?* (policy decisions + gate reports)

The greenfield advantage is that we can bake this in *before* ad‑hoc log piles and tribal knowledge form.

Evidence collection defaults are now explicitly profile-shaped: see `docs/478-evidence-collection-posture-by-profile.md` for the A/B/C/D boundary between always-on fleet evidence, user-exportable workstation evidence, local-retained general-OS evidence, and bundle-oriented factory/regulatory evidence.

## Design stance

1) **Evidence is a product**, not a debugging afterthought.  
2) Evidence objects are:
   - **typed** (schema)
   - **content-addressed** (digest)
   - **immutable** (append-only; no in-place edits)
   - **capability-governed** (who can read/export)
   - **shipppable** (support bundles; remote verifiers; auditors)
3) Evidence is **cross-linked by digest**, so we can build a provenance graph without relying on filenames.

## Evidence storage lane (optional, but recommended)

Evidence objects should have a well-defined home:
- keep build artifacts in the main store (`docs/03-store.md`)
- keep operational receipts, trace slices, and incident bundles in an **evidence vault**

The vault can be implemented as a *write-once, content-addressed store* (Venti/Fossil lesson):
`docs/350-venti-fossil-write-once-archive-store.md`.


## What counts as evidence in DeriveBSD?

### “Change intent” → “change result”
- Desired change: `change-set` (what we intend to do)
- Execution result: `change-receipt` (what happened)

See: `docs/219-change-sets-and-apply-engine.md`.

### “Configuration intent” → “configuration result”
- Policy-governed configuration transaction: `config-transaction`
- Receipt: `config-receipt` (+ optional `config-snapshot`)
- /etc drift diff surface: `etc.config.diff` (recommended; makes local overrides reviewable)

See: `docs/218-configuration-transactions-and-receipts.md` and `docs/427-etc-config-diff-as-a-drift-surface.md`.

### Runtime operations as evidence (ops spine)
- Service supervision + health: `svc.*` + `svc.event`  
  See: `docs/214-service-supervision-health-as-evidence.md`.
- Fault management: `fault.*` (+ diagnosis / actions)  
  See: `docs/213-fault-management-architecture.md`.
- Kernel mutation (sysctls + kmods): `sysctl.plan`/`sysctl.receipt`/`sysctl.snapshot`/`sysctl.event` (+ optional `sysctl.diff`), `kmod-policy` (+ optional `kmod.policy.diff`), `kmod.load.plan`/`kmod.load.receipt`/`kmod.event`
  See: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/452-sysctl-snapshot-as-evidence-artifact.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/429-sysctl-diff-as-drift-surface.md`, `docs/439-kmod-policy-diff-as-review-surface.md`.
- Policy modules as evidence (sandboxed extensibility lane): `policy-module` (+ optional `policy.module.diff` for drift review) (optional but high leverage)
  See: `docs/186-policy-modules-wasm.md`, `docs/451-policy-module-diff-as-review-surface.md`.
- Sandbox posture (promise profiles): `sandbox-profile` (declared least-authority intent) + derived enforcement artifacts (e.g., `activation.capset`) (+ optional `sandbox.profile.diff` for drift review)
  See: `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`, `docs/432-sandbox-profile-diff-as-review-surface.md`.
- Capsicum preopen maps (oblivious sandboxing grants): `preopen.map` (+ optional `preopen.map.diff` for drift review) (optional but high leverage)
  See: `docs/294-oblivious-sandboxing-launchers.md`, `docs/453-preopen-map-diff-as-review-surface.md`.
- Remembered workstation role/default posture: authoritative `intent.role.binding` snapshots + `intent.role.binding.event` durable mutation trace (+ optional `intent.role.binding.diff` for drift review, joined `consent.receipt` digests when the interactive workstation approval lane was used, joined `policy_decision_digest` values when non-interactive reconcile/import policy authorized the change through an exact-mutation `intent.role.binding.policy.profile` with a short-lived single-apply window (`must_apply_before`, `max_successful_events = 1`) and `decision_instance_id` for unique issuance identity, caller-shaped `source.*` when local or remote admin tooling invoked the write, joined `import_receipt_digest` values when support/import/recovery workflows actually produced or attempted the change, typed `reason_code = policy-expired` / `policy-consumed` when an exact authorization was too late or already spent (with policy-window validity winning before compare-and-swap; see `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`), and `consumed_by_event_id` plus `consumed_by_event_digest` when `policy-consumed` won so the earlier successful consuming event is explicit and verifiable away from the live journal, plus `consuming_event_action` so the winner's `initialized` vs `updated` shape is queryable as evidence-only summary data, `consumed_binding_digest` so the winner's resulting binding digest is queryable as evidence-only summary data, `consumed_diff_digest` so the winner's applied review-surface digest is queryable as evidence-only summary data, and for updated winners `consumed_previous_binding_digest` so the winner's replaced `previous_binding.digest` is queryable as evidence-only summary data (`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`, `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md`); if that digest-bound consuming success matches the same exact tuple, support/retry views may collapse the retry to **already-applied** per `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, and `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` now makes that derived answer stable through `recovery_interpretation`, and typed `reason_code` plus `observed_binding` when a stale reviewed diff was denied after authority was still live) (optional but high leverage)
  See: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`.
- MicroVM lifecycle as evidence: `microvm.launch.plan`/`microvm.launch.receipt` + `microvm.stop.plan`/`microvm.stop.receipt` (core runtime join keys)
  See: `docs/455-microvm-launch-plans-and-receipts.md`.
- Devfs views as authority posture: `devfs.view.plan` / `devfs.view.receipt` / `devfs.view.event` (+ optional `devfs.view.diff` for drift review)
  See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/450-devfs-view-diff-as-review-surface.md`.
- Adapter lane kill posture (interop toggles): `adapter.kill.policy` (+ optional `adapter.kill.policy.diff` for drift review) (optional but high leverage)
  See: `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/444-adapter-kill-policy-diff-as-review-surface.md`.
- Impurity waiver posture (determinism exceptions): `impurity.waiver.policy` (+ optional `impurity.waiver.policy.diff` for drift review) (optional but high leverage)
  See: `docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `docs/367-reproducible-generations-and-determinism-checks.md`.
- Structured event journal (ETW/journald lessons): `event.record`, `event.segment`
  See: `docs/215-structured-event-log-as-evidence.md`, `docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md`.
- Optional sealing receipts for tamper-evident local evidence: `event.seal.receipt` (optional lane)
  See: `docs/424-forward-secure-event-log-sealing.md`, `docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md`, `docs/625-incident-bundles-carry-event-seal-proof-by-digest.md`.

- Incident snapshots and bounded support bundles: `incident.bundle`
  See: `docs/216-incident-snapshots-and-support-bundles.md`.
- Incident timelines (human orientation surface): `incident.timeline` (the default one-page orientation surface for official support handoff)
  See: `docs/419-incident-timelines-as-derived-artifacts.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.
- Deterministic export/sharing evidence: `export.policy`, `export.receipt` (+ optional `export.policy.diff` for drift review) (optional but high leverage)
  See: `docs/251-export-policies-and-support-bundle-portal.md`.
- Release publication evidence: authoritative `release.publish.receipt`, plus supplemental `release.transparency.entry`, `log.checkpoint.receipt`, `witness.policy`, and `transparency.monitor.snapshot` when transparency-gated channels are used; publication gating should be summarized only in `release.publish.receipt.transparency_verification`
- Workflow-verification evidence for promotion / publication review: `supplychain-verify-receipt` under `supplychain-layout-policy`, with publish-time workflow gating summarized only in `release.publish.receipt.supplychain_verification`
- Vulnerability-verification evidence for promotion / publication review: `vuln.query.receipt` + `vuln-gate-receipt` under `vuln.gate.policy`, with publish-time vulnerability gating summarized only in `release.publish.receipt.vulnerability_verification`
  See: `docs/257-release-capsules-and-transparency.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`.
- Optional ecosystem attestation exports (killable adapter lane): `attestation.adapter.intoto.report` (optional)
  See: `docs/454-intoto-slsa-adapter-lane.md`.
- Deterministic selection plans for bundle-min: `bundle.plan` (part of the official support handoff contract) (+ optional `bundle.plan.diff` for drift review)
  See: `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/441-bundle-plan-diff-as-review-surface.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.
- Bundle build receipts (plan→bytes binding): `bundle.build.receipt` (part of the official support handoff contract)
  See: `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/441-bundle-plan-diff-as-review-surface.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.
- Bundle payload member manifests (bytes→members binding): `bundle.payload.manifest` (part of the official support handoff contract)
  See: `docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.
- Store retention / garbage collection as evidence: `store.gc.plan`, `store.gc.receipt` (recommended)
  `store.gc.plan` distinguishes soft retention preference from hard rollback floor, and `store.gc.receipt.rollback_coverage` records whether cleanup preserved recovery coverage.
  See: `docs/426-store-gc-plans-and-receipts.md`, `docs/175-pins-roots-and-garbage-collection.md`, and `docs/496-store-retention-and-gc-posture-by-profile.md`.
- Lease issuance/use/revocation evidence: `lease.issue.receipt`, `lease.use.receipt`, `lease-snapshot`, `lease-revoke-event` (optional but high leverage). The authoritative object remains the lane-specific grant / lease / session; `lease.issue.receipt` and `lease.use.receipt` are evidence-only. Official support handoff can also carry `lease_snapshot_digest` when responders need one typed answer to what temporary authority was still live at capture time.
- Secret state/action evidence: `secret-snapshot`, `secret-receipt` (optional but high leverage). Secrets stay metadata-first; `secret-snapshot` is the safe current-health/rotation surface and `secret-receipt` is the exact action proof. Official support handoff can also carry `secret_snapshot_digest` + `secret_receipt_digests` when responders need a typed answer about safe current secret posture and which exact secret actions materially participated.
- PKI issuance evidence: `pki-issue-receipt` (optional but high leverage). Reviewed trust roots and served trust views stay distinct from exact issuance actions; Official support handoff can also carry `pki_issue_receipt_digests` when responders need exact PKI issuance/renewal/install/revoke proof instead of CA dashboards, ACME logs, or ticket prose.
- Network-learning evidence: bounded `net-flow-summary` objects summarize `net-flow-receipt` (+ optional `net-dns-query-receipt`) observations into a compact review surface, while `policy-suggestion` remains the proposed patch and `net-egress-policy` remains authoritative.
  See: `docs/328-learned-network-policies-from-flow-receipts.md`, `docs/505-network-learn-audit-convergence-contract.md`.
  See: `docs/449-lease-issue-and-use-receipts.md`, `docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/493-temporary-authority-grant-lease-and-use-boundary.md`.
- Packet-capture session authority stays typed and bounded: `packet.capture.session` is the authoritative session object for bounded capture, embedded `packet.capture.selector` keeps capture intent reviewable, `packet.capture.summary` is the compact evidence-only review/export surface for that session, any retained local raw artifact is described by digest + `metadata_posture` + `retention_until`, stronger sideband/decryption-bearing artifacts use the typed safe-open import profile and normalize before ordinary promotion/export, normalized raw-byte derivatives bind to generic `redaction-transform` / `redaction-receipt` evidence before they become ordinary review/export candidates, incident/support bundles now join packet-capture participation through `packet_capture_session_digests` / `packet_capture_summary_digests` / packet-capture import+redaction receipt digests rather than default raw-byte members, stronger raw-byte export stays on the generic export lane through `packet.capture.normalized` plus a typed `supporting_evidence` proof chain, stronger packet raw-byte export approval now also joins through typed consent request/receipt evidence and cannot use `method = auto`, completed stronger packet raw-byte export must also join through typed `transport.receipt` evidence and cannot terminate as `destination.type = file`, final stronger handoff now also requires typed `transport.acceptance.receipt` evidence so the archive can distinguish transported from `recipient-accepted`, that stronger chain must also stay digest-stable so `consent.request.action.artifact_digest`, `transport.receipt.artifact.digest`, `transport.acceptance.receipt.artifact.digest`, `transport.acceptance.receipt.acceptance.remote_artifact_digest`, and `export.receipt.artifact.digest` keep the same normalized digest, recipient acceptance is now digest-confirming as well so the remote-side receipt must echo the same normalized bytes (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`), the stronger closure is now remote-object-continuous too so `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` keep the same remote object id (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`), the stronger closure is now remote-validator-continuous too so `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` keep the same remote validator (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`), the stronger closure is now remote-protection-shaped too so `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` keep the same remote protection posture instead of treating any accepted upload as durable evidence (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`), the stronger closure is now remote-locator-continuous too so `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` keep the same remote locator instead of leaving later evidence retrieval to portal folklore (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`), later remote follow-up now uses typed `transport.reverification.receipt` metadata-only reverification so stronger evidence re-check can keep the same accepted remote validator / protection posture / locator without re-downloading packet bytes or trusting portal screenshots (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`), and the stronger approval is now destination-bound too so `consent.request.action.destination`, `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` keep the same approved destination tuple, incident/export receipts remain evidence about what was shared, and raw packet payloads stay summary-first by default.
  See: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/509-packet-capture-selector-compiler-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`.
- Authority-budget policy and review evidence: authoritative `authority.budget` + authoritative `authority.exception`, with evidence-only `authority.budget.check` for plan-time and drift-time comparison of compiled runtime posture (optional but high leverage).
- Frontend/source compile provenance: authoritative compiled canonical JSON objects stay authoritative, while `frontend.compile.receipt` is evidence-only for source digests, compiler posture, and optional explain traces (optional but high leverage).
- Component-runtime source compilation: reviewed `derive.unit` source stays authoritative, compiled `runtime.manifest` stays launch authority, and `derive.unit.compile.receipt` is evidence-only source→compiled provenance for runtime IR / launch outputs (optional but high leverage).
  See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`.
- Cross-lane lease join metadata: `lease.envelope` (optional, and it points at the authoritative grant / lease / session rather than a later action receipt)
- Admission control policy for attestation-gated actions: `attestation.admission.policy` (+ optional `attestation.admission.policy.diff` for drift review) (optional but high leverage)
- Attestation results stay verifier evidence: `attestation.receipt` is evidence-only, while `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt` remain the authoritative consuming receipts via `attestation_verification`
  See: `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`.
- Minimal evidence index: `causality.graph` (optional, but strongly recommended for support bundles)
  See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.
- Breakglass + recovery sessions: `breakglass.*` (optional lane)
  See: `docs/236-breakglass-and-recovery-mode.md`.
- Destructive reprovision authority + use receipts: `reset.authorization`, `reset.receipt` (high leverage for install/recovery and factory reset lanes)
  See: `docs/483-destructive-reprovisioning-and-reset-authority.md`, `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`.
- Restore apply evidence: `restore.plan`, `restore.receipt`, plus supplemental `restore.drill.receipt` where rehearsal/testing ran (quarantine-first restore is the ordinary path; `replacement-target` remains a stronger promotion-shaped step)
  See: `docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`.
- State datasets + migrations: `state-snapshot`, `state-migration-*` receipts  
  See: `docs/217-state-datasets-and-migrations-as-evidence.md`.

### “Hardware / platform truth” as evidence
- Platform provenance reports: `platform-report` (recommended)
  See: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`.
- Firmware inventory + mutation evidence: `fw.inventory.receipt`, `fw.inventory.diff`, `fw.update.plan`, `fw.update.receipt`, `uefi.var.set.plan`, `uefi.var.set.receipt`
  See: `docs/221-firmware-updates-as-artifacts.md`, `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`.
- Storage health + scrub receipts
  See: `docs/225-storage-health-and-scrubbing-as-evidence.md`.
- Verified execution posture (optional): authoritative `exec.integrity.policy` / `exec.integrity.plan` / `exec.integrity.receipt`, plus backend observation `exec-verify-snapshot` / `exec-verify-event` (+ optional `exec.verify.policy.diff` for drift review)
  See: `docs/233-verified-execution-as-evidence.md`, `docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`.
- Platform posture + attestation verifier receipts  
  See: `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/639-incident-bundles-carry-attestation-proof-by-digest.md`.
- Bootchain allowlists + revocations (policy object): `bootchain.policy` (optional lane)
  See: `docs/244-bootchain-revocation-and-allowlists.md`.
- Boot manifests for activated generations: `boot-manifest` (+ optional `boot.manifest.diff` for drift review)
  See: `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/176-measured-boot-attestation.md`, `docs/436-boot-manifest-diff-as-review-surface.md`, `docs/482-boot-code-admission-and-constrained-overrides.md`.
- Boot override policy + receipts for the tiny mutable boot surface: `boot.override.policy`, `boot.override.receipt`
  See: `docs/277-loader-verification-and-boot-config-constraints.md`, `docs/482-boot-code-admission-and-constrained-overrides.md`.
- boot assessment / finalization decisions: `boot.health.report`, `boot-bless-receipt` (with `boot_bless_receipt_digests` available on the official support handoff when health-gated finalization or rollback matters)
  See: `docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`, `docs/633-incident-bundles-carry-boot-bless-proof-by-digest.md`.
- Canonical boot event log transcript (for replay + verifier explainability): `boot.eventlog.canon` (optional lane)
  See: `docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `docs/313-boot-manifests-and-eventlog-replay.md`.
- Time discipline: inventories, snapshots, receipts, requirements (+ optional `time.source.policy.diff` for drift review)
  See: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/438-time-source-policy-diff-as-review-surface.md`.
- Storage integrity now also has a support-handoff join: `storage_pool_inventory_digest`, `storage_health_snapshot_digest`, and `storage_scrub_receipt_digests` keep exact scrub / repair proof on the typed bundle contract when integrity verification or degraded-pool recovery matters.
- Time discipline now also has a support-handoff join: `time_source_inventory_digest`, `time_sync_snapshot_digest`, and `time_sync_receipt_digests` keep trustworthy-time action proof on the typed bundle contract when clock correction or source failover matters.
- Trust policy as data (what signatures/roles/attestations are accepted): `trust-policy` (+ optional `trust.policy.diff` for drift review)
  See: `docs/57-namespaces-channels-trust.md`, `docs/446-trust-policy-diff-as-review-surface.md`.
- PKI lifecycle: trust bundles, trust-bundle apply receipts, issuance plans, issuance receipts, PKI events (+ optional `pki.trust.bundle.diff` for drift review)
  See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`, `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`.
- Publisher identity evidence (supplemental, not release authority): `publisher.identity.receipt` + `sigstore.bundle`, with bundle-first offline verification material for `sigstore-keyless` and optional joins from `release.publish.receipt`
- Provenance / SBOM / VEX / VSA objects are evidence inputs to policy engines and verifiers; they should not be read as ambient publication authority
  See: `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`.

## The “evidence graph” mental model

The system should make it easy to answer questions by **walking edges**:

- Lint results: `lint-report` objects can be attached to change receipts and incident bundles to capture why compilers/validators complained.
  See: `docs/237-lint-reports-and-contract-testing.md`.


- A `boot.health.report` references the `change-receipt` it validated.
- That `change-receipt` references:
  - the `closure.proof` / `closure.manifest` digests it installed,
  - any `config-receipt` / `state-migration-receipt` created,
  - the `pki-issue-receipt` digests produced during the change.
- The incident bundle includes bounded `event.segment` references covering the window and may also carry `event_seal_receipt_digests` when sealing was enabled and continuity proof matters to the support story.
- When trust-view activation changed or matters to the incident, the incident bundle can also carry `pki_trust_bundle_digest` plus `pki_trust_bundle_apply_receipt_digests` so support handoff can prove both reviewed trust roots and the exact served trust view.
- When remote assistance participated in the incident/support story, the incident bundle can also carry `support_session_digests` so support handoff can prove which exact bounded helper session participated instead of reconstructing it from side receipts or helper dashboards.
- When firmware/platform drift participated in the incident/support story, the incident bundle can also carry `fw_inventory_diff_digest` so support handoff can prove which exact bounded `fw.inventory.diff` participated instead of reconstructing it from screenshots, dashboard comparisons, or ticket prose.
- When firmware-update stage/apply outcomes participated in the incident/support story, the incident bundle can also carry `fw_update_receipt_digests` so support handoff can prove which exact bounded `fw.update.receipt` participated instead of reconstructing it from updater dashboards, helper stdout, or ticket notes.
- When UEFI-variable mutation participated in the incident/support story, the incident bundle can also carry `uefi_var_set_receipt_digests` so support handoff can prove which exact bounded `uefi.var.set.receipt` participated instead of reconstructing it from raw efivar dumps or helper stdout.
- Official support handoff can also carry `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` so support can prove what exact measured-boot evidence participated, what verifier/reference scope judged it, and what exact verifier judgments mattered instead of reconstructing the story from verifier dashboards, portal screenshots, or ticket prose.
- When live temporary authority participated in or materially shaped the incident/support story, the incident bundle can also carry `lease_snapshot_digest` so support handoff can prove what temporary authority was still live at capture time instead of reconstructing it from bastion dashboards, control-plane screenshots, operator memory, or chat archaeology.
- When measured posture participated in or materially shaped the incident/support story, the incident bundle can also carry `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests`; see `docs/639-incident-bundles-carry-attestation-proof-by-digest.md`.

This is the “why” behind the consistent schema strategy:
**If it isn’t typed and digest-addressed, it can’t participate in the evidence graph.**

## Practical archive rule

When we add a new “lane”:
- define **(a) inventory, (b) plan, (c) receipt, (d) snapshot, (e) event** objects where applicable,
- integrate with:
  - `change-set` ordering (optional, but preferred),
  - incident bundle defaults (safe, privacy-conscious),
  - the structured journal (typed events),
  - health gates (when relevant).

This keeps the OS coherent instead of becoming a bag of one-off subsystems.

- When recovery or stronger replacement apply matters to the incident, the incident bundle can also carry `restore_receipt_digests`; see `docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md`.
- When remote assistance mattered, the incident bundle can also carry `support_session_digests`; see `docs/627-incident-bundles-carry-support-session-proof-by-digest.md`.

- When operator access mattered, the incident bundle can also carry `operator_session_digests`; see `docs/628-incident-bundles-carry-operator-session-proof-by-digest.md`.
- When emergency access mattered, the incident bundle can also carry `breakglass_receipt_digests`; see `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`.
- When storage integrity / scrub outcomes mattered, the incident bundle can also carry `storage_scrub_receipt_digests`; see `docs/635-incident-bundles-carry-storage-scrub-proof-by-digest.md`.
- When firmware/platform drift mattered, the incident bundle can also carry `fw_inventory_diff_digest`; see `docs/632-incident-bundles-carry-fw-inventory-diff-proof-by-digest.md`.
- When firmware-update stage/apply outcomes mattered, the incident bundle can also carry `fw_update_receipt_digests`; see `docs/631-incident-bundles-carry-fw-update-proof-by-digest.md`.
- When UEFI-variable mutation mattered, the incident bundle can also carry `uefi_var_set_receipt_digests`; see `docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md`.

Last updated: 2026-03-21r369
