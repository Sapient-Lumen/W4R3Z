# Evidence spine: receipts everywhere (why DeriveBSD treats operations like builds)

DeriveBSD’s “Spec → Lock → Plan → Artifact” pipeline is only half the story.
The other half is that **operations are also artifacts**: every privileged or security-relevant action should produce a **typed, immutable receipt** that can be queried, shipped, and audited.

This “evidence spine” is how we keep the system **explainable** when something goes wrong:
- *What changed?* (change sets + apply receipts)
- *What did the host observe?* (structured event journal)
- *What is the host’s current declared state?* (snapshots)
- *What did the system decide and why?* (policy decisions + gate reports)

The greenfield advantage is that we can bake this in *before* ad‑hoc log piles and tribal knowledge form.

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
- MicroVM lifecycle as evidence: `microvm.launch.plan`/`microvm.launch.receipt` + `microvm.stop.plan`/`microvm.stop.receipt` (core runtime join keys)
  See: `docs/455-microvm-launch-plans-and-receipts.md`.
- Devfs views as authority posture: `devfs.view.plan` / `devfs.view.receipt` / `devfs.view.event` (+ optional `devfs.view.diff` for drift review)
  See: `docs/323-devfs-views-plans-and-receipts.md`, `docs/450-devfs-view-diff-as-review-surface.md`.
- Adapter lane kill posture (interop toggles): `adapter.kill.policy` (+ optional `adapter.kill.policy.diff` for drift review) (optional but high leverage)
  See: `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/444-adapter-kill-policy-diff-as-review-surface.md`.
- Impurity waiver posture (determinism exceptions): `impurity.waiver.policy` (+ optional `impurity.waiver.policy.diff` for drift review) (optional but high leverage)
  See: `docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `docs/367-reproducible-generations-and-determinism-checks.md`.
- Structured event journal (ETW/journald lessons): `event.record`, `event.segment`
  See: `docs/215-structured-event-log-as-evidence.md`.
- Optional sealing receipts for tamper-evident local evidence: `event.seal.receipt` (optional lane)
  See: `docs/424-forward-secure-event-log-sealing.md`.

- Incident snapshots and bounded support bundles: `incident.bundle`
  See: `docs/216-incident-snapshots-and-support-bundles.md`.
- Incident timelines (human orientation surface): `incident.timeline` (optional, but strongly recommended for support bundles)
  See: `docs/419-incident-timelines-as-derived-artifacts.md`.
- Deterministic export/sharing evidence: `export.policy`, `export.receipt` (+ optional `export.policy.diff` for drift review) (optional but high leverage)
  See: `docs/251-export-policies-and-support-bundle-portal.md`.
- Optional ecosystem attestation exports (killable adapter lane): `attestation.adapter.intoto.report` (optional)
  See: `docs/454-intoto-slsa-adapter-lane.md`.
- Deterministic selection plans for bundle-min: `bundle.plan` (optional) (+ optional `bundle.plan.diff` for drift review)
  See: `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/441-bundle-plan-diff-as-review-surface.md`.
- Bundle build receipts (plan→bytes binding): `bundle.build.receipt` (optional, but high leverage)
  See: `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/441-bundle-plan-diff-as-review-surface.md`.
- Bundle payload member manifests (bytes→members binding): `bundle.payload.manifest` (optional, but high leverage)
  See: `docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `docs/253-bundle-plans-and-deterministic-exports.md`.
- Store retention / garbage collection as evidence: `store.gc.plan`, `store.gc.receipt` (recommended)
  See: `docs/426-store-gc-plans-and-receipts.md` and `docs/175-pins-roots-and-garbage-collection.md`.
- Lease issuance/use/revocation evidence: `lease.issue.receipt`, `lease.use.receipt`, `lease-snapshot`, `lease-revoke-event` (optional but high leverage)
  See: `docs/449-lease-issue-and-use-receipts.md`, `docs/249-lease-registry-and-cross-lane-revocation.md`.
- Cross-lane lease join metadata: `lease.envelope` (optional)
- Admission control policy for attestation-gated actions: `attestation.admission.policy` (+ optional `attestation.admission.policy.diff` for drift review) (optional but high leverage)
  See: `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`.
- Minimal evidence index: `causality.graph` (optional, but strongly recommended for support bundles)
  See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.
- Breakglass + recovery sessions: `breakglass.*` (optional lane)
  See: `docs/236-breakglass-and-recovery-mode.md`.
- State datasets + migrations: `state-snapshot`, `state-migration-*` receipts  
  See: `docs/217-state-datasets-and-migrations-as-evidence.md`.

### “Hardware / platform truth” as evidence
- Platform provenance reports: `platform-report` (recommended)
  See: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`.
- Firmware inventories, update plans, update receipts  
  See: `docs/221-firmware-updates-as-artifacts.md`.
- Firmware inventory diffs (optional, but high leverage): `fw.inventory.diff`
  See: `docs/428-fw-inventory-diff-as-drift-surface.md`.
- Storage health + scrub receipts
  See: `docs/225-storage-health-and-scrubbing-as-evidence.md`.
- Verified execution posture (optional): `exec-verify-policy`, `exec-verify-receipt`, `exec-verify-snapshot` (+ optional `exec.verify.policy.diff` for drift review)
  See: `docs/233-verified-execution-as-evidence.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`.
- Platform posture + attestation verifier receipts  
  See: `docs/226-platform-posture-and-attestation-results-as-evidence.md`.
- Bootchain allowlists + revocations (policy object): `bootchain.policy` (optional lane)
  See: `docs/244-bootchain-revocation-and-allowlists.md`.
- Boot manifests for activated generations: `boot-manifest` (+ optional `boot.manifest.diff` for drift review)
  See: `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/176-measured-boot-attestation.md`, `docs/436-boot-manifest-diff-as-review-surface.md`.
- Canonical boot event log transcript (for replay + verifier explainability): `boot.eventlog.canon` (optional lane)
  See: `docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `docs/313-boot-manifests-and-eventlog-replay.md`.
- Time discipline: inventories, snapshots, receipts, requirements (+ optional `time.source.policy.diff` for drift review)
  See: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/438-time-source-policy-diff-as-review-surface.md`.
- Trust policy as data (what signatures/roles/attestations are accepted): `trust-policy` (+ optional `trust.policy.diff` for drift review)
  See: `docs/57-namespaces-channels-trust.md`, `docs/446-trust-policy-diff-as-review-surface.md`.
- PKI lifecycle: trust bundles, issuance plans, issuance receipts, PKI events (+ optional `pki.trust.bundle.diff` for drift review)
  See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`.

## The “evidence graph” mental model

The system should make it easy to answer questions by **walking edges**:

- Lint results: `lint-report` objects can be attached to change receipts and incident bundles to capture why compilers/validators complained.
  See: `docs/237-lint-reports-and-contract-testing.md`.


- A `boot.health.report` references the `change-receipt` it validated.
- That `change-receipt` references:
  - the `closure.proof` / `closure.manifest` digests it installed,
  - any `config-receipt` / `state-migration-receipt` created,
  - the `pki-issue-receipt` digests produced during the change.
- The incident bundle includes bounded `event.segment` references covering the window.

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

Last updated: 2026-03-04r180