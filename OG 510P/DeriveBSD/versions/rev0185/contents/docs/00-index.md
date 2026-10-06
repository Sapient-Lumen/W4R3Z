# Index















## New in 2026-03-04r185

- Eliminate spec-example drift warnings by validating long-lived *variant* examples via thin wrapper schemas (`microvm.stop.plan.force`, `microvm.stop.receipt.denied`). The wrappers `$ref` the base contracts and pin the variant semantics so examples remain mechanically checkable without expanding the core surface (`spec/microvm.stop.plan.force.schema.json`, `spec/microvm.stop.receipt.denied.schema.json`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r184

- Stabilize the microVM “why” surface by introducing a central reason-code registry for lifecycle receipts, capturing the governance rule in an accepted ADR, and enforcing it with a hygiene check so example receipts can't invent ad-hoc codes (`docs/456-microvm-receipt-reason-code-registry.md`, `adrs/ADR-0046-microvm-reason-code-registry.md`, `tools/check_microvm_reason_code_registry.py`, `tools/hygiene.py`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/99-llm-runbook.md`).
- Add an explicit denied stop receipt example that demonstrates the two-code pattern (`denied-by-policy` + `force-stop-denied`) and is mechanically guarded against drift (`spec/examples/microvm.stop.plan.force.json`, `spec/examples/microvm.stop.receipt.denied.json`).
- Refresh curated references with high-signal cues for stable error vocabularies (gRPC status codes; systemd symbolic exit-status names) and extend juicy lessons so the registry stays discoverable (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r183

- Make microVM lifecycle receipts operationally deterministic by requiring non-empty `reasons[]` with stable `reasons[].code` on non-success outcomes (denied/failed/timeout); capture the rule in an ADR and enforce it with a hygiene guardrail (`adrs/ADR-0045-microvm-receipt-reason-codes.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`, `tools/check_microvm_receipt_reason_requirements.py`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Extend juicy lessons and the LLM runbook with the new invariant so it stays discoverable and amnesia-resistant (`docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`).
- Refresh curated references with high-signal cues for structured, machine-readable error detail envelopes and stable reason-code vocabularies (`docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r182

- Make microVM launches more forensic and spec-able by recording attached host↔guest IO crossings in the receipt: add `assigned.io_channels` (vsock/virtio-console/nmdm/stdio), update the example receipt, and capture the decision in an ADR so A–D behavior doesn’t drift (`spec/microvm.launch.receipt.schema.json`, `spec/examples/microvm.launch.receipt.json`, `adrs/ADR-0044-microvm-io-channels-in-receipts.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/110-juicy-os-lessons.md`).
- Refresh curated references with concrete vsock semantics pointers (CID/port model, well-known CIDs) so cross-backend implementers stay aligned (`docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r181

- Make microVM plan identity mechanically implementable: define `plan_digest = sha256(utf8(JCS(plan)))` and capture the rule in an ADR (`adrs/ADR-0043-microvm-plan-digest-sha256.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`).
- Add an amnesia-resistor guardrail: `tools/check_microvm_example_plan_digests.py` verifies receipt examples actually bind the computed plan digest, and update the microVM lifecycle examples to use real sha256 digests (no `...` placeholders) so drift is caught early (`spec/examples/microvm.launch.plan.json`, `spec/examples/microvm.launch.receipt.json`, `spec/examples/microvm.stop.plan.json`, `spec/examples/microvm.stop.receipt.json`, `tools/hygiene.py`).
- Refresh curated references with RFC 8785 JCS implementation pointers (keeps cross-language implementers aligned) and extend juicy lessons with a durable “content identity must be checkable” rule of thumb (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r180

- Make microVM **stop** spec-able (like launch) by introducing `microvm.stop.plan` + `microvm.stop.receipt` (schemas + examples) and wiring stop into the control-plane and evidence-spine docs so terminations are auditable and queryable across A–D (`spec/microvm.stop.plan.schema.json`, `spec/examples/microvm.stop.plan.json`, `spec/microvm.stop.receipt.schema.json`, `spec/examples/microvm.stop.receipt.json`, `docs/29-vm-control-plane.md`, `docs/229-evidence-spine-overview.md`).
- Decide stop semantics conservatively: Plan→Receipt, bounded `graceful` vs explicit `force`, idempotent `already-stopped`, and optional `expect_running_plan_digest` safety guard (`adrs/ADR-0042-microvm-stop-semantics.md`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Extend juicy lessons and curated references so “no silent kills” and backend stop primitives stay discoverable (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r179

- Decide strict microVM launch idempotency: `derive-vmmd` is strict-idempotent by `(instance_id, plan_digest)` (retries are safe; implicit replacement is denied) and capture the rule in an ADR so A–D behavior does not fork (`adrs/ADR-0041-microvm-instance-idempotency.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`).
- Extend the microVM juicy lessons to make “no surprise restarts” a stable rule of thumb for fleet/workstation UX (`docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r178

- Make the `derive-vmmd` runtime boundary spec-able by introducing a digest-bound Plan→Receipt join key for microVM launches: `microvm.launch.plan` + `microvm.launch.receipt` (schema + examples) and wire it into the evidence spine and control-plane docs (`docs/455-microvm-launch-plans-and-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/29-vm-control-plane.md`, `spec/microvm.launch.plan.schema.json`, `spec/microvm.launch.receipt.schema.json`).
- Add a juicy lesson that makes “launch is evidence” a stable rule of thumb for runtime isolation/forensics (`docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r177

- Decide the microVM orchestration boundary in v0: keep `derive-vmmd` **host-local** (verify → enforce → receipt) and treat distributed scheduling/reconciliation as an external, killable adapter concern (`adrs/ADR-0040-microvm-orchestration-host-local.md`, `docs/266-open-questions-and-risk-register.md`).
- Add an amnesia-resistor convention for the risk register: tag decided items with **[DECIDED]** and exclude them from generated “top open questions” surfaces; add a warning check to keep decided items pinned to ADRs (`docs/266-open-questions-and-risk-register.md`, `tools/gen_context_pack.py`, `tools/gen_risk_register_index.py`, `tools/check_open_questions_decisions.py`, `docs/420-context-pack.md`, `docs/415-risk-register-index.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r176

- Add a killable ecosystem interop lane for standard attestations by documenting an in-toto/SLSA export adapter and introducing a typed export report artifact: `attestation.adapter.intoto.report` (schema + example) (keeps DeriveBSD receipts as source of truth while enabling downstream verifier tooling) (`docs/454-intoto-slsa-adapter-lane.md`, `spec/attestation.adapter.intoto.report.schema.json`, `spec/examples/attestation.adapter.intoto.report.json`).
- Wire the new lane into adapter discipline, the evidence spine, juicy lessons, and curated references (adds current SLSA v1.2 pointers) so the interop remains discoverable and amnesia-resistant (`docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.


## New in 2026-02-28r175

- Make Capsicum capability-set drift mechanically reviewable by introducing typed preopen map artifacts and a compact diff surface: `preopen.map` + `preopen.map.diff` (schemas + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/453-preopen-map-diff-as-review-surface.md`, `spec/preopen.map.schema.json`, `spec/examples/preopen.map.json`, `spec/preopen.map.diff.schema.json`, `spec/examples/preopen.map.diff.json`).
- Wire `preopen.map.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine so “what handles/rights changed?” stays explainable and gateable without forks; refresh Capsicum launcher + descriptor docs with schema pointers (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Extend the canonical risk-flag vocabulary with stable preopen-map drift reason codes (`preopen-map-egress-added`, `preopen-map-handle-added`, `preopen-map-rights-broadened`) and update curated references with Capsicum primitives (`cap_enter(2)`, `cap_rights_limit(2)`) (`spec/examples/risk.flag.registry.json`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.


## New in 2026-02-28r174

- Make sysctl drift explainable without bulk inventory by introducing a bounded observation artifact: `sysctl.snapshot` (schema + example) plus a tight wiring doc. Drift checks can capture snapshots and bundles can include them without shipping raw command output (`docs/452-sysctl-snapshot-as-evidence-artifact.md`, `spec/sysctl.snapshot.schema.json`, `spec/examples/sysctl.snapshot.json`).
- Tighten sysctl drift evidence by allowing `sysctl.event` to point at the snapshot digest (`snapshot_digest`), and wire snapshots into the evidence spine + kernel knobs lane (`spec/sysctl.event.schema.json`, `spec/examples/sysctl.event.json`, `docs/229-evidence-spine-overview.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r173

- Make policy evaluator code drift mechanically reviewable by introducing a typed policy module diff surface: `policy.module.diff` (schema + example) plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/451-policy-module-diff-as-review-surface.md`, `spec/policy.module.diff.schema.json`, `spec/examples/policy.module.diff.json`).
- Wire `policy.module.diff` into the canonical diff surface registry, drift bundle posture guidance, the evidence spine, and the policy-module juicy lesson so changes in policy-module authority (hostcalls/limits) stay explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r172

- Add a guardrail that keeps per-diff review-surface docs uniform and mechanically jumpable: `tools/check_diff_review_docs.py` enforces Tier placement, requires the canonical `Registry→Diff→Gate` token, and requires schema+example pointers; wire it into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_diff_review_docs.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Entropy-reducing refactor: add an explicit “The artifacts” schema/example block to the adapter-kill and impurity-waiver diff wiring docs so reviewers can jump directly to contracts (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `docs/445-impurity-waiver-policy-diff-as-review-surface.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r171

- Make `/dev` authority drift mechanically reviewable by introducing a typed devfs view diff surface: `devfs.view.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/450-devfs-view-diff-as-review-surface.md`, `spec/devfs.view.diff.schema.json`, `spec/examples/devfs.view.diff.json`).
- Wire `devfs.view.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with stable `/dev` exposure reason codes (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r170

- Complete Broker→Lease→Receipt evidence by introducing generic lease issuance + use receipts: `lease.issue.receipt` and `lease.use.receipt` (schemas + examples) plus a tight wiring doc (keeps temporary authority explainable and bundle-friendly without forks) (`docs/449-lease-issue-and-use-receipts.md`, `spec/lease.issue.receipt.schema.json`, `spec/examples/lease.issue.receipt.json`, `spec/lease.use.receipt.schema.json`, `spec/examples/lease.use.receipt.json`).
- Update the lease registry and evidence spine to treat issuance/use as first-class evidence (and fix a small lease-envelope reference miswire); update the pattern catalog to point at the canonical receipts (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/229-evidence-spine-overview.md`, `docs/397-pattern-catalog.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r169

- Make exported support bundles self-describing by introducing a typed bundle payload member manifest artifact: `bundle.payload.manifest` (schema + example) and a tight wiring doc (turns “what was in the bundle?” into queryable evidence) (`docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `spec/bundle.payload.manifest.schema.json`, `spec/examples/bundle.payload.manifest.json`).
- Tighten bundle build receipts to optionally bind the payload manifest digest (`bundle.build.receipt.output.payload_manifest_digest`) and refresh the deterministic export lane doc + evidence spine so plan→bytes→members stays replayable without forks (`spec/bundle.build.receipt.schema.json`, `spec/examples/bundle.build.receipt.json`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/229-evidence-spine-overview.md`).
- Update curated references with the OCI image digest/manifest model pointer and refresh wiring/version stamps; regenerate generated discovery surfaces (`docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-28r168

- Make offline mirror kits self-describing by introducing a typed kit manifest artifact: `mirror.kit.manifest` (schema + example) and a tight wiring doc for evidence/receipt binding (keeps air-gap imports explainable and resumable without forks) (`docs/447-mirror-kit-manifest-as-evidence-artifact.md`, `spec/mirror.kit.manifest.schema.json`, `spec/examples/mirror.kit.manifest.json`).
- Tighten mirror-kit import receipts to record the kit manifest digest when present (`mirror.import.receipt.source.kit_manifest_digest`), and refresh the air-gap mirror-kit lane doc + juicy lesson so operators can always answer "what exactly was on that kit?" with receipts (`spec/mirror.import.receipt.schema.json`, `spec/examples/mirror.import.receipt.json`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r167

- Make trust-policy drift mechanically reviewable by introducing a typed diff surface: `trust.policy.diff` (schema + example) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/446-trust-policy-diff-as-review-surface.md`, `spec/trust.policy.diff.schema.json`, `spec/examples/trust.policy.diff.json`).
- Wire `trust.policy.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with a stable trust-policy drift reason code (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r166

- Make “known impurity” non-ambient by introducing an explicit impurity waiver policy and a gateable diff surface: `impurity.waiver.policy` + `impurity.waiver.policy.diff` (schema + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `spec/impurity.waiver.policy.schema.json`, `spec/impurity.waiver.policy.diff.schema.json`, `spec/examples/impurity.waiver.policy.json`, `spec/examples/impurity.waiver.policy.diff.json`).
- Wire `impurity.waiver.policy.diff` into the canonical diff registry, drift bundle posture guidance, the evidence spine, and the determinism-check lane; extend the canonical risk-flag vocabulary with impurity waiver drift reason codes and add the primary Nix impurity reference to curated references (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/367-reproducible-generations-and-determinism-checks.md`, `spec/examples/risk.flag.registry.json`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r165

- Add an amnesia-resistor guardrail that keeps the meta-engineering "design law" docs discoverable: `tools/check_meta_doc_discoverability.py` requires every numbered doc >=397 to be linked from `docs/00-index.md` or `docs/110-juicy-os-lessons.md`; wire the check into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_meta_doc_discoverability.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces (product profile matrix, context pack, doc catalog, risk index, artifact index).
## New in 2026-02-28r164

- Make adapter lanes *actually killable* by introducing an explicit adapter posture policy and a gateable diff surface: `adapter.kill.policy` + `adapter.kill.policy.diff` (schema + examples) with a tight wiring doc mapping it to Adapter→Shadow→Replace + Registry→Diff→Gate (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `spec/adapter.kill.policy.schema.json`, `spec/adapter.kill.policy.diff.schema.json`, `spec/examples/adapter.kill.policy.json`, `spec/examples/adapter.kill.policy.diff.json`).
- Wire `adapter.kill.policy.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine so “interop toggles” stay explainable and gateable without forks; update adapter lane discipline and the killability juicy lesson (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with adapter kill/phase reason codes and refresh discovery/version wiring (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r163

- Make measured boot event logs explainable and replayable by introducing a typed canonical event log artifact: `boot.eventlog.canon` (schema + example) plus a tight wiring doc for bundle/export posture and verifier ergonomics (`docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `spec/boot.eventlog.canon.schema.json`, `spec/examples/boot.eventlog.canon.json`).
- Flesh out the measured-boot lane to treat `boot.eventlog.canon` as the canonical object behind `boot.attestation.tpm.eventlog_digest`, and add an explicit `eventlog_canon` identifier to `boot.attestation` evidence for deterministic replay/verifier behavior (`docs/176-measured-boot-attestation.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `spec/boot.attestation.schema.json`, `spec/examples/boot.attestation.json`, `spec/examples/boot.manifest.json`).
- Wire the new evidence artifact into discovery and evidence UX surfaces (evidence spine + juicy lessons) and extend curated references with primary TCG CEL/PFP/event-log-processing specs (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`).

## New in 2026-02-28r162

- Make verified-execution posture drift mechanically reviewable by introducing a typed diff surface: `exec.verify.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/442-exec-verify-policy-diff-as-review-surface.md`, `spec/exec.verify.policy.diff.schema.json`, `spec/examples/exec.verify.policy.diff.json`).
- Wire `exec.verify.policy.diff` into the canonical diff surface registry, drift bundle posture guidance, the evidence spine, and the verified-exec juicy lesson so “runtime integrity posture” stays explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with verified-exec drift reason codes (disable/relax/exception) and refresh wiring/version stamps (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r161

- Make incident/support bundle **plan drift** mechanically reviewable by introducing a typed bundle plan diff surface: `bundle.plan.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/441-bundle-plan-diff-as-review-surface.md`, `spec/bundle.plan.diff.schema.json`, `spec/examples/bundle.plan.diff.json`).
- Wire `bundle.plan.diff` into the canonical diff surface registry (keeps review surfaces discoverable and gateable) and update the bundle export lane + juicy lessons to reference the stable diff surface (`docs/430-diff-surface-registry.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r160

- Add a guardrail that keeps the canonical risk-flag registry wired to real review surfaces: `tools/check_risk_flag_typical_sources.py` validates that each `typical_sources` entry in `risk.flag.registry` points at a real schema under `spec/` and that any `*.diff` sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`).
- Wire the new check into `python3 tools/hygiene.py` and document the invariant in archive hygiene guidance (`docs/98-archive-hygiene.md`).
- Refresh discovery/version stamps (`docs/00-index.md`, `README.md`, `docs/110-juicy-os-lessons.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r159

- Make attestation admission policy drift mechanically reviewable by introducing a typed diff surface: `attestation.admission.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.diff.schema.json`, `spec/examples/attestation.admission.policy.diff.json`).
- Wire the new diff surface into the canonical diff registry, drift bundle posture-diff guidance, the evidence spine, and the Keylime/admission juicy lesson so “what is attestation-gated?” stays explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the open-questions register with the remaining admission-policy drift/gate questions and refresh discovery/version wiring (`docs/266-open-questions-and-risk-register.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-28r158

- Make kernel module policy drift mechanically reviewable by introducing a typed module policy diff surface: `kmod.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/439-kmod-policy-diff-as-review-surface.md`, `spec/kmod.policy.diff.schema.json`, `spec/examples/kmod.policy.diff.json`).
- Wire `kmod.policy.diff` into the canonical diff surface registry and drift bundle posture-diff guidance, and update the evidence spine + kernel module lane + juicy lessons so “privileged code allowlists” stay explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Extend the canonical risk-flag vocabulary with kmod policy drift reason codes (e.g. `kmod-policy-runtime-load-enabled`) and refresh discovery/version stamps + regenerate generated discovery surfaces (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`).

## New in 2026-02-28r157

- Make time-source posture drift mechanically reviewable by introducing a typed time source policy diff surface: `time.source.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/438-time-source-policy-diff-as-review-surface.md`, `spec/time.source.policy.diff.schema.json`, `spec/examples/time.source.policy.diff.json`).
- Extend the canonical risk-flag vocabulary with time authority drift reason codes (e.g. `time-quorum-relaxed`, `time-bootstrap-relaxed`) and wire the new diff surface into the canonical diff registry, drift bundle guidance, and the evidence spine (`spec/examples/risk.flag.registry.json`, `docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Refresh discovery/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`).

## New in 2026-02-28r156

- Harden discovery-surface drift control by extending `python3 tools/check_discovery.py` to require that the newest `## New in <version>` block is the **first** such block in `docs/00-index.md`, and that the index `Last updated:` stamp matches the newest release (prevents stale top-of-file release notes from lingering) (`tools/check_discovery.py`, `docs/00-index.md`).
- Update archive hygiene guidance to reflect the new invariant (`docs/98-archive-hygiene.md`) and bump version stamps / regenerate generated discovery surfaces.

## New in 2026-02-28r155

- Add an incremental guardrail that ties the canonical diff surface registry to the canonical `risk_flags` vocabulary: diff wiring docs must declare a `## Risk flags` section (or be explicitly allowlisted) so gates and review UI have a stable jump-to reason-code surface (`tools/check_diff_wiring_risk_flags.py`, `tools/baselines/diff_wiring_missing_risk_flags.txt`, `docs/98-archive-hygiene.md`, `docs/430-diff-surface-registry.md`).
- Refactor the sandbox/sysctl/export diff wiring docs to declare their minimal starter `risk_flags` sets (keeps posture drift gateable without forks): `docs/432-sandbox-profile-diff-as-review-surface.md`, `docs/429-sysctl-diff-as-drift-surface.md`, `docs/433-export-policy-diff-as-review-surface.md`.


## New in 2026-02-28r154

- Add a Tier C optional lane describing **split secrets brokers** (Split GPG / Split SSH style): keep private keys in a more trusted compartment and delegate bounded crypto operations via Broker→Lease→Receipt; interop via Adapter→Shadow→Replace (`docs/437-split-secrets-brokers.md`).
- Wire the new lane into the juicy lessons discovery surface and curated references (keeps citations centralized) (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Update the open-questions/risk register entry for the crypto operations portal to include split-secrets workflow questions (`docs/266-open-questions-and-risk-register.md`).


## New in 2026-02-27r153

- Make boot-critical closure drift mechanically reviewable by introducing a typed boot manifest diff surface: `boot.manifest.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/436-boot-manifest-diff-as-review-surface.md`, `spec/boot.manifest.diff.schema.json`, `spec/examples/boot.manifest.diff.json`).
- Extend the canonical diff surface registry and drift bundle guidance to include `boot.manifest.diff` as a posture diff attachment (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and wire it into the evidence spine and measured-boot lesson so “what did we boot?” stays explainable (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with boot-drift reason codes (`bootloader-changed`, `kernel-image-changed`, `cmdline-profile-changed`) and refresh version stamps + regenerate generated discovery surfaces (`spec/examples/risk.flag.registry.json`, `README.md`, `CHANGELOG.md`).



## New in 2026-02-27r152

- Add a canonical risk-flag vocabulary registry (`risk.flag.registry`) so `risk_flags` reason codes used by diff summaries and gates stay explicit, stable, and profile-aware without forks (`docs/435-risk-flags-registry-and-gate-vocabulary.md`, `spec/risk.flag.registry.schema.json`, `spec/examples/risk.flag.registry.json`).
- Add a drift guardrail (`tools/check_risk_flag_registry.py`) wired into `python3 tools/hygiene.py` to prevent ad-hoc risk-flag strings (requires canonical kebab-case ids in spec examples and in gate docs lines mentioning `risk_flags`).
- Entropy-reducing refactor: normalize existing diff examples + gate docs to canonical kebab-case risk flags (keeps review surfaces mechanically gateable); update curated references with primary policy engine pointers used by the new doc, bump version stamps, and regenerate generated discovery surfaces.


## New in 2026-02-27r151

- Entropy-reducing refactor: extend the canonical diff surface registry to include a per-diff wiring doc pointer (so every `*.diff` review surface has a direct jump-to for gate semantics + bundle attachment): `docs/430-diff-surface-registry.md`.
- Add a new guardrail check (`tools/check_diff_surface_registry_wiring.py`) and wire it into `python3 tools/hygiene.py`; document the invariant in archive hygiene (`docs/98-archive-hygiene.md`).
- Extend the “registries + diffs + gates” juicy lesson with the canonical diff registry discipline (`docs/110-juicy-os-lessons.md`), bump version stamps, and regenerate generated discovery surfaces (`docs/00-index.md`).


## New in 2026-02-27r150

- Make trust root drift mechanically reviewable by introducing a typed trust bundle diff artifact: `pki.trust.bundle.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/434-pki-trust-bundle-diff-as-review-surface.md`, `spec/pki.trust.bundle.diff.schema.json`, `spec/examples/pki.trust.bundle.diff.json`).
- Wire `pki.trust.bundle.diff` into the canonical diff surface registry, drift bundle guidance, the evidence spine, and the trust roots juicy lesson; extend the trust bundle open-question block with default gating questions (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.



## New in 2026-02-27r149

- Make data-egress boundary drift mechanically reviewable by introducing a typed export policy diff artifact: `export.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/433-export-policy-diff-as-review-surface.md`, `spec/export.policy.diff.schema.json`, `spec/examples/export.policy.diff.json`).
- Update the canonical diff surface registry and drift bundle guidance to include export boundary diffs (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and wire export diffs into the evidence spine (`docs/229-evidence-spine-overview.md`).
- Extend the export portal juicy lesson (#122) with export boundary drift discipline and add the primary sosreport upstream reference to curated references (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`); capture remaining export boundary drift questions in the risk register (`docs/266-open-questions-and-risk-register.md`).



## New in 2026-02-27r148

- Make sandbox posture changes mechanically reviewable by introducing a typed sandbox profile diff artifact: `sandbox.profile.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles: `docs/432-sandbox-profile-diff-as-review-surface.md`, `spec/sandbox.profile.diff.schema.json`, `spec/examples/sandbox.profile.diff.json`.
- Update the canonical diff surface registry to include `sandbox.profile.diff` (`docs/430-diff-surface-registry.md`) and refactor drift bundle guidance to eliminate redundant lists while still calling out posture diffs (`docs/395-drift-bundles-and-review-summaries.md`).
- Wire sandbox profile diffs into evidence + discovery surfaces (`docs/229-evidence-spine-overview.md` + juicy lesson #225 in `docs/110-juicy-os-lessons.md`), update this discovery surface (`docs/00-index.md`), bump version stamps, and regenerate generated discovery surfaces.

## New in 2026-02-27r147

- Add a juicy-lessons citation guardrail (`tools/check_juicy_lesson_references.py`) that blocks *new* uncataloged external URLs in `docs/110-juicy-os-lessons.md` without forcing retroactive churn (uses a baseline allowlist under `tools/baselines/`; documented in `docs/98-archive-hygiene.md`).
- Add a conservative Tier C stabilization lane note + typed receipt artifact for explicit determinism normalizers: `build.stabilizer.receipt` (schema + example) and a tight mapping doc (`docs/431-build-stabilizers-and-determinism-normalizers.md`).
- Extend curated references with primary reproducible-builds normalization sources (SOURCE_DATE_EPOCH + strip-nondeterminism + OSS-Rebuild stabilizers).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r146

- Add a canonical diff surface registry (`docs/430-diff-surface-registry.md`) so the set of typed `*.diff` review surfaces stays explicit and stable as the archive grows (reduces review-surface entropy; improves drift bundle UX).
- Add a new guardrail check (`tools/check_diff_surface_registry.py`) and wire it into `python3 tools/hygiene.py`, preventing new `*.diff` schemas from landing without being listed in the registry (documented in `docs/98-archive-hygiene.md`).
- Refactor drift bundle guidance to reference the canonical registry (reduces duplication and keeps the review funnel stable): `docs/395-drift-bundles-and-review-summaries.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r145

- Make kernel knob posture drift reviewable by introducing a typed sysctl plan diff artifact: `spec/sysctl.diff.schema.json`, `spec/examples/sysctl.diff.json`, plus a tight wiring doc mapping the lane to Plan→Receipt + Registry→Diff→Gate and drift bundles (`docs/429-sysctl-diff-as-drift-surface.md`).
- Wire `sysctl.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`), extend juicy lesson #183 with “planned sysctl diffs” (`docs/110-juicy-os-lessons.md`), and refresh the kernel mutation control open question block (`docs/266-open-questions-and-risk-register.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r144

- Make platform posture drift reviewable by introducing a typed firmware inventory diff surface: `fw.inventory.diff` (schema + example) and a tight wiring doc (`docs/428-fw-inventory-diff-as-drift-surface.md`). This turns firmware/UEFI posture changes (including Secure Boot digest summaries) into a gateable, exportable diff artifact.
- Wire `fw.inventory.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and extend juicy lesson #187 with “firmware posture diffs” (`docs/110-juicy-os-lessons.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r143

- Add a release-scope stamp guardrail: `tools/check_release_last_updated.py` requires docs mentioned in the newest `CHANGELOG.md` entry to be stamped `Last updated: 2026-02-28r174
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r142

- Make `/etc` drift a first-class, typed diff surface by introducing `etc.config.diff` (schema + example) and a tight wiring doc that maps it to Registry→Diff→Gate + drift bundles: `docs/427-etc-config-diff-as-a-drift-surface.md`, `spec/etc.config.diff.schema.json`, `spec/examples/etc.config.diff.json`.
- Wire `/etc` drift diffs into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and add a juicy lesson subchapter on `/etc` drift discipline (`docs/110-juicy-os-lessons.md`).
- Extend curated references with the FreeBSD `etcupdate(8)` primary reference (keeps citations centralized): `docs/32-curated-references.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r141

- Make store retention *explainable* by adding typed GC artifacts: `store.gc.plan` and `store.gc.receipt` (schemas + examples) and a tight doc that maps GC to Plan→Receipt + policy gates (`docs/426-store-gc-plans-and-receipts.md`).
- Close a paper-artifact gap by adding typed pin receipts used by GC roots: `spec/pin.add.receipt.schema.json`, `spec/pin.rm.receipt.schema.json` plus examples (matches RFC-0110 and `docs/175-pins-roots-and-garbage-collection.md`).
- Wire GC receipts into the evidence spine and extend GC ergonomics with “retention as evidence” (`docs/229-evidence-spine-overview.md`, `docs/175-pins-roots-and-garbage-collection.md`, `docs/110-juicy-os-lessons.md`).
- Extend curated references with primary Nix GC docs (keeps citations centralized): `docs/32-curated-references.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r140

- Add a drift guardrail: `tools/check_doc_patterns.py` requires meta docs (>=397) to declare `**Patterns:**` near the top (explicit mapping to the pattern catalog; stable review surface).
- Refactor the meta-doc range (>=397) to include `**Patterns:**` metadata and tighten `docs/397-pattern-catalog.md` + `docs/99-llm-runbook.md` to treat explicit pattern mapping as part of the archive contract.
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r139

- Add an optional TPM-sealed secrets lane with typed, diffable PCR policies: `docs/425-tpm-sealed-secrets-and-pcr-policies.md`, `spec/tpm.pcr.policy.schema.json`, `spec/examples/tpm.pcr.policy.json`.
- Add a release drift guardrail: `tools/check_release_curated_references.py` ensures numbered docs mentioned in the newest `CHANGELOG.md` entry do not introduce external URLs without also adding them to `docs/32-curated-references.md` (keeps citations centralized for new work).
- Wire the new guardrail into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`; update curated references with TPM sealing + PCR measurement sources.
- Extend juicy lesson #59 with TPM-sealed secrets as a high-leverage optional lane (`docs/110-juicy-os-lessons.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r138

- Add a schema drift guardrail: `tools/check_schema_kind_matches_filename.py` enforces that dotted-kind schemas keep a stable schema naming discipline (e.g. `spec/mirror.import.receipt.schema.json` declares kind `mirror.import.receipt`) (prevents kind/filename mismatch drift).
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r137

- Add a changelog-format guardrail (`tools/check_changelog_format.py`) and normalize CHANGELOG spacing to keep release notes compact and diff-friendly.
- Document the new guardrail in `docs/98-archive-hygiene.md` and keep the hygiene wrapper wired.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r136

- Make bundle-min builds first-class evidence by adding the typed `bundle.build.receipt` artifact (schema + example) and wiring it into deterministic export + incident bundle guidance (`docs/253-bundle-plans-and-deterministic-exports.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`).
- Reduce drift by unifying the bundle include-knob surface: `spec/incident.bundle.schema.json` now defines `#/$defs/include_knobs`, and `spec/bundle.plan.schema.json` references it (keeps selection plans aligned with bundle include knobs).
- Extend juicy lesson #99 with the plan+build-receipt discipline, bump version stamps, and regenerate generated discovery surfaces (`docs/110-juicy-os-lessons.md`, `docs/414-doc-catalog.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).


## New in 2026-02-27r135

- Make offline mirror kits concrete as typed **Plan→Receipt** artifacts for quarantine-first imports and policy-gated promotion: add `mirror.import.plan`/`mirror.import.receipt`/`mirror.promote.plan`/`mirror.promote.receipt` (schemas + examples) and update `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`.
- Add a drift guardrail to prevent “paper artifacts”: `tools/check_changelog_artifact_mentions.py` ensures docs referenced by the newest `CHANGELOG.md` entry don't mention non-existent typed artifacts; wired into `tools/hygiene.py` and documented in `docs/98-archive-hygiene.md`.
- Extend curated references with the Uptane Standard and add a new juicy lesson on offline update ergonomics (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-02-27r134

- Add an optional forward-secure event log sealing lane (tamper-evident local evidence) by introducing the typed `event.seal.receipt` artifact and wiring it into the evidence docs: `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`, `spec/examples/event.seal.receipt.json`, plus updates to `docs/215-structured-event-log-as-evidence.md`, `docs/229-evidence-spine-overview.md`, and `docs/110-juicy-os-lessons.md`.
- Reduce refresh friction by extending the context pack generator to include a compact “Recent changes” section sourced from `CHANGELOG.md` (Markdown + JSON), and regenerate `docs/420-context-pack.md` + `docs/_generated/context_pack.json` (`tools/gen_context_pack.py`).
- Update curated references with official FSS/digest-chain sources and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-02-27r133

- Make the “reproducible generations” lane concrete by adding typed Plan→Receipt artifacts for determinism checks: `docs/367-reproducible-generations-and-determinism-checks.md`, `spec/repro.check.plan.schema.json`, `spec/repro.check.receipt.schema.json`, `spec/examples/repro.check.plan.json`, `spec/examples/repro.check.receipt.json`.
- Wire determinism receipts into the review funnel by adding `repro.check.receipt` as an optional drift-bundle attachment (`docs/395-drift-bundles-and-review-summaries.md`) and regenerate the artifact index so `kind → schema → example` stays current (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-27r132

- Add **persist sets** as a stable diff surface for “what is allowed to persist” (impermanence/stateless-root lesson): `docs/423-persist-sets-and-ephemeral-root.md`, `spec/persist.set.registry.schema.json`, `spec/examples/persist.set.registry.json`.
- Strengthen anti-amnesia release wiring: `tools/check_discovery.py` now enforces that any numbered docs mentioned in the newest `CHANGELOG.md` entry are linked from the appropriate discovery surface (index vs juicy lessons) *and* appear in the matching “New in …” section.
- Update discovery wiring + curated references for the new lane, and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/98-archive-hygiene.md`, `README.md`).

## New in 2026-02-27r131

- Add an **invariant registry** as a stable diff surface (Registry → Diff → Gate): `docs/422-invariant-registry-and-design-invariants.md`, `spec/invariant.registry.schema.json`, `spec/examples/invariant.registry.json`.
- Fix a quiet “must-read drift” hole: normalize the runbook’s mandatory refresh list and harden the context pack generator to extract **all** backticked items (so `docs/01-glossary.md` and `docs/02-derive-core.md` can’t disappear from the generated pack).
- Add a new guardrail to prevent accidental refresh-path erosion: `tools/check_must_read_set.py` (wired into `tools/hygiene.py`).

## New in 2026-02-27r130

- Add a research **disposable workspace** lane (Template → Lease → Dispose) translated from Qubes TemplateVM/DisposableVM into DeriveBSD patterns and evidence surfaces: `docs/421-disposable-workspaces-and-template-microvms.md`.
- Add a guardrail that keeps **external URLs** for meta docs (>=397) centralized in `docs/32-curated-references.md`: new check `tools/check_curated_references.py` wired into `tools/hygiene.py`.
- Tighten version stamp discipline: extend `tools/check_version.py` to also validate the `Last updated:` tag in `docs/00-index.md`.

## New in 2026-02-27r129

- Add a generated **context pack** (Markdown + JSON) as a first-class “amnesia resistor”, so a single file captures current version, must-read set, A–D summary, and top risks: `docs/420-context-pack.md`, `docs/_generated/context_pack.json`, `tools/gen_context_pack.py`.
- Wire the context pack into discovery + hygiene: `tools/check_generated_docs.py` validates it, and `tools/check_discovery.py` requires it to be linked from this index.

## New in 2026-02-27r128

- Add a typed **incident timeline** artifact (`incident.timeline`) as a human-scale orientation surface for incidents (schema + example + doc): `docs/419-...`, `spec/incident.timeline.schema.json`.
- Wire timelines into the evidence spine and support bundle story: incident bundles can include an `incident.timeline` digest, and causality graphs now explicitly pair with timeline views.
- Refresh structured output contract with a canonical domain output example for incident timelines (`docs/87-structured-output-contract.md`).

## New in 2026-02-27r127

- Make A–D **profile naming** mechanically stable: canonical ids live in `spec/examples/product.profiles.json`, and a single alias map lives in `spec/product.profile_aliases.json`.
- Strengthen doc metadata guardrails: meta docs can list either A–D or canonical ids; tools normalize and detect duplicates.
- Improve the generated profile matrix and context pack so “what profile is this?” is always answerable.

## New in 2026-02-27r126

- Add a generated **artifact index** (Markdown + JSON) that maps `kind` → canonical schema → example(s), to make typed outputs discoverable and reduce LLM/human navigation friction (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`, `tools/gen_artifact_index.py`).
- Fix a drift hole: `tools/check_generated_docs.py` now actually checks the risk register index outputs (and also validates the new artifact index), so generated discovery surfaces can't silently stale.
- Add a lightweight **spec example coverage** guardrail and wire it into hygiene, ensuring every plan/receipt/event/report/registry/diff schema has a matching example (`tools/check_spec_example_coverage.py`, `tools/hygiene.py`).

## New in 2026-02-27r125

- Add a typed **platform provenance report** (`platform-report`) and a tight doc that binds platform/firmware lifecycle into the evidence model (`docs/417-...`, `spec/platform.report.schema.json`).
- Treat firmware lifecycle as derived ops using the existing `fw.update.*` artifacts, and refresh the structured output contract to include the new domain output (`docs/87-...`).
- Tighten curated references for firmware/UEFI tooling (fwupd/LVFS, FreeBSD fwget/efivar, DICE) and add a new juicy lesson item tying it together.

## New in 2026-02-27r124

- Add a first-class **policy trace** artifact (schema + example) and a doc that binds `derive explain-policy` to stable JSON traces (`docs/416-...`, `spec/policy.trace.schema.json`).

This is a living design archive for **DeriveBSD**: a hypervisor-centric, BSD-native, planned-from-scratch successor to Nix-like systems.

We keep it small by:
- **one concept per file**
- proposals in **RFCs**, decisions in **ADRs**
- **links/citations** instead of copying external text

## Reading paths

### 0) Running the archive (humans + LLMs)
- LLM runbook (invariants + must-read + output contract): `docs/99-llm-runbook.md`
- Context pack (generated short refresh + JSON pack): `docs/420-context-pack.md`, `docs/_generated/context_pack.json`
- Product profiles as compilation targets (A–D, no forks): `docs/411-product-profiles-as-compilation-target.md`
- Product profiles artifact (example): `spec/examples/product.profiles.json`
- Product profiles matrix (generated): `docs/412-product-profile-matrix.md`
- Doc catalog (generated nav map + JSON index): `docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`
- Risk register index (generated summary + JSON): `docs/415-risk-register-index.md`, `docs/_generated/risk_register.json`
- Artifact index (generated schema→kind→example + JSON): `docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`
- Context pack generator (memory prosthetic): `tools/gen_context_pack.py`


### 1) The Derive pipeline (Spec → Lock → Plan → Artifact)
- Vision + glossary: `docs/00-vision.md`, `docs/01-glossary.md`
- Day-0 behaviors: `docs/97-non-negotiable-behaviors.md`
- The pipeline contract: `docs/02-derive-core.md`
- Spec authoring frontends (compile-to-IR): `docs/79-derive-spec-frontends.md`, ADR-0023
- Store + hashing: `docs/03-store.md`, `docs/56-store-layout-and-digests.md`
- Long-term source availability (SWHID fallback): `docs/403-swhid-fallback-and-long-term-source-availability.md`
- Closure proofs: `docs/90-closure-proof.md`, `docs/92-verification-matrix.md`
- Policy decision records: `docs/93-policy-decision-records.md`
- Policy trace format + explain surfaces: `docs/416-policy-trace-format-and-explain-surfaces.md`
- Platform provenance + firmware lifecycle as derived ops: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `spec/platform.report.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`
- DevShells (developer UX parity): `docs/159-devshells.md`, `adrs/ADR-0039-devshells-first-class.md`
- Sandbox + hardening: `docs/04-sandbox.md`, `docs/45-build-sandbox-jails.md`, `docs/49-capsicum-casper-hardening.md`, `docs/325-rootless-jails-and-unprivileged-compartments.md`
- Hostile builders: `docs/91-hostile-builders.md`
- Trust + caches: `docs/46-cache-trust-model.md`, `docs/61-channel-metadata-tuf-inspired.md`, `docs/127-uptane-director-targets.md`, `adrs/ADR-0009-artifact-verification.md`
  - immutable objects + revocable name indirection (Amoeba lesson): `docs/345-amoeba-bullet-server-and-capability-directories.md`
  - optional full TUF metadata adapter (interop + delegations): `docs/203-full-tuf-metadata-adapter.md`
  - optional transparency evidence: `docs/131-sigsum-lightweight-transparency.md`, `docs/132-scitt-ledger-receipts.md`, `docs/324-transparent-key-directories-and-minimal-tlogs.md`
  - optional cache witness quorums (reproducibility corroboration): `docs/190-cache-witness-quorums-trustix.md`
- Trust policy as data: `docs/57-namespaces-channels-trust.md`, `spec/trust.policy.schema.json` (+ drift review surface: `docs/446-trust-policy-diff-as-review-surface.md`, `spec/trust.policy.diff.schema.json`)
- Shadow trust prevention (system CA governance): `docs/327-shadow-trust-and-system-ca-governance.md`
- Publisher identity receipts (keyless signing, optional): `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `spec/publisher.identity.receipt.schema.json`, `spec/sigstore.bundle.schema.json`
- Provenance + SBOM: `docs/31-provenance-and-sbom.md`, `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/75-sbom-formats-spdx-cyclonedx.md`
- Supply-chain workflow policy (in-toto layouts, optional): `docs/202-in-toto-layouts-and-step-policy.md`
- SBOM + VEX evidence objects (policy-bound inventory + exploitability): `docs/168-sboms-and-vex-as-evidence.md`
- Vulnerability intelligence + gates (optional; snapshot + receipts): `docs/60-vulnerability-intel-and-gates.md`, `docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`
- Artifact knowledge graph (GUAC-style) + supply-chain queries: `docs/334-artifact-knowledge-graph-and-supply-chain-queries.md`
- Tests as evidence (optional policy gate): `docs/166-test-receipts-and-promotion-gates.md`
- Fuzzing as evidence (optional long-running gate): `docs/274-continuous-fuzzing-farm.md`
- Policy: `docs/30-policy-engine.md`, `docs/85-policy-engine-options-and-traces.md`
- Process topology / least authority: `docs/96-process-topology.md`
- Unit manifests as component declarations (capability-first, contract-bound): `docs/344-derive-unit-manifests-and-capability-routing.md`
- Hermetic component test realms (realm-builder-style; tests as routed capabilities): `docs/354-realm-builder-style-hermetic-component-tests.md`
- Wasm component model / WIT as a standard contract language (digestable interfaces): `docs/356-wasm-component-model-and-wit-contracts.md`
- Contract registries + API diff gates (interfaces are versioned surfaces): `docs/370-contract-registries-and-api-diff-gates.md`
- Parser surface registry + fuzz gates (treat “new parser” as first-class drift): `docs/376-parser-surface-registry-and-fuzz-gates.md`
- Surface registries as a meta-pattern (keep drift gateable as the system grows): `docs/379-surface-registry-pattern.md`
- Pattern catalog (keep new subsystems in a small set of reusable shapes): `docs/397-pattern-catalog.md`
- Spec schema conventions + evolution (keep artifacts legible as the archive grows): `docs/407-spec-schema-conventions-and-evolution.md`
- v0 cutline + feature tiers (keep the project shippable): `docs/401-v0-cutline-and-feature-tiers.md`
- Adapter lanes + strangler discipline (interop without forever-legacy): `docs/402-adapter-lanes-and-strangler-discipline.md`
- Drift bundles (one review attachment that summarizes all drift surfaces): `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`
- Closure diffs (make “new code ingestion” reviewable): `docs/396-closure-diffs-and-new-code-surfaces.md`, `spec/closure.diff.schema.json`
- Deprecation policies + removal receipts (no silent breaks): `docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`
- Safe boundary APIs (kernel boundary is also a contract surface): `docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`
- Userspace driver/kernel-subsystem testing lane (rump kernels lesson): `docs/355-rump-kernels-and-userspace-driver-testing.md`
- Kernel extensibility (BPF/JIT risk) is authority (lease-gated, brokered, diffable): `docs/384-kernel-extensibility-bpf-and-jit-risk.md`
- Promise profiles (reviewable least-authority declarations): `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`, `spec/sandbox.profile.schema.json`
- Learned promise profiles (observation mode; tighten-by-running): `docs/326-learned-promise-profiles-and-observation-mode.md`
- Denial-driven policy suggestions (denials → reviewable policy patches): `docs/378-denial-driven-policy-suggestions.md`
- Policy tests as artifacts (suites + reports + mutation, optional): `docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`
- Policy analysis as evidence (automated reasoning, optional high-assurance lane): `docs/394-policy-analysis-and-automated-reasoning.md`
- Learned network policies (audit mode; flows → reviewable diffs): `docs/328-learned-network-policies-from-flow-receipts.md`
- Learned resource budgets (observation mode; usage → reviewable diffs): `docs/329-learned-resource-budgets-and-observation-mode.md`
- Oblivious sandboxing launchers (Capsicum by default; preopen maps as artifacts): `docs/294-oblivious-sandboxing-launchers.md`, `docs/180-capability-mode-dynamic-linking.md`
- Exec integrity policy + verified execution (no unverified code runs, optional backend): `docs/289-exec-integrity-policy-and-verified-execution.md`, `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`
- Network egress broker + flow receipts (outbound is a lease, not ambient): `docs/281-network-egress-broker-and-consent.md`, `spec/net.egress.policy.schema.json`, `spec/net.egress.grant.schema.json`, `spec/net.flow.receipt.schema.json`
  - DNS mediation + hostname binding (optional receipt lane): `docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`
- Inbound listen broker + firewall leases (listening is a lease, not ambient): `docs/286-inbound-listen-broker-and-firewall-leases.md`, `spec/net.listen.policy.schema.json`, `spec/net.listen.grant.schema.json`, `spec/net.listen.receipt.schema.json`
- Host network topology + firewall substrate as derived operations (links/routes/pf root ruleset are receipted): `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- Optional netgraph/netmap fabrics (graph-shaped datapaths + VALE fast path): `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`
- Workload identity + secretless deploys (SPIFFE/SPIRE-shaped, optional lane): `docs/181-workload-identity-and-secretless-deploys.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`, `spec/workload.identity.grant.schema.json`
- Desktop viability checklist (constraints to keep profile B possible): `docs/410-desktop-viability-checklist.md`
- Disposable workspaces (Template → Lease → Dispose; Qubes lessons, optional lane): `docs/421-disposable-workspaces-and-template-microvms.md`
- Portals / mediated dynamic access: `docs/179-portals-and-powerbox.md`
- Persistent file capabilities (bookmarks): `docs/198-persistent-file-capabilities-bookmarks.md`
- Intent routing (plumber-style): `docs/199-intent-routing-and-plumbing.md`
- Data transfer portals (clipboard / drag&drop): `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- Notification portal (non-observing): `docs/206-notification-portal-non-observing.md`
- Input authority (secure attention + HID risk): `docs/207-input-authority-secure-attention-and-hid-risk.md`
- Screen sharing + remote control (screencast + injected input): `docs/208-screencast-and-remote-desktop-portals.md`
- Camera + audio capture portals: `docs/209-camera-and-audio-capture-portals.md`
- Portal sessions + permission store: `docs/210-portal-sessions-and-permission-store.md`
- Location portal: `docs/211-location-portal.md`
- Printing portal: `docs/212-printing-portal.md`
- Sanitization portal (open safely; disposable sandbox transform): `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- Origin labels + quarantine attributes (imports): `docs/280-origin-labels-and-quarantine-attributes.md`
- Information-flow labels + explicit declassification (optional lane): `docs/381-information-flow-labels-and-declassification.md`
- Attribute-indexed metadata + live queries (BFS lesson): `docs/293-attribute-indexed-metadata-and-live-queries.md`
- Evidence queries over fact tables (osquery-shaped ergonomics, but derived and receipted): `docs/399-evidence-queries-and-fact-tables.md`
- Portable home areas + embedded user records (optional lane): `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage contract (template/private/volatile + optional home areas): `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- Toolchain trust hardening (optional DDC lane): `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`
  - optional Zig toolchain wedge for cross-compiling C/C++ dependencies: `docs/398-zig-toolchain-wedge-and-cross-compilation.md`

### 2) Host systems (atomic switch, ZFS generations)
- Activation + switching: `docs/06-system-activation.md`, `docs/86-host-activation-rcd-and-service-jails.md`, `docs/404-zfs-boot-environments-as-system-generations.md`
- Service supervision + compiled service DB: `docs/214-service-supervision-health-as-evidence.md`, `docs/114-service-manifests-smf-lessons.md`, `docs/173-compiled-service-database-bundles.md`, `docs/235-process-contracts-and-service-ownership.md`, `docs/239-service-lifecycle-restarters-and-repo.md`, `docs/349-supervision-trees-and-restart-strategies.md`, `docs/352-crash-only-and-roc-for-system-services.md`, `docs/238-portal-activated-services-and-socket-activation.md`, `docs/240-dynamic-service-identities.md`, `docs/342-minix-self-healing-and-reincarnation.md`
- State datasets + migrations as evidence: `docs/217-state-datasets-and-migrations-as-evidence.md`, `spec/statedb.schema.json`, `spec/state.snapshot.schema.json`, `spec/state.migration.plan.schema.json`, `spec/state.migration.receipt.schema.json`
- Persist sets + ephemeral root (explicit persistence boundary; diffable + gateable): `docs/423-persist-sets-and-ephemeral-root.md`, `spec/persist.set.registry.schema.json`
  - checkpoint boundaries + durable identities (orthogonal persistence lessons): `docs/347-orthogonal-persistence-and-checkpointed-systems.md`
- Optional activation broker (restart-safe handle escrow): `docs/196-capability-activation-and-escrow.md`
- ZFS boot environments: `docs/69-host-generations-bectl.md`, `docs/284-bootenv-switching-as-evidence.md`, `docs/27-vm-storage-zfs.md`, `docs/126-zfs-send-distribution.md`
- Health-gated updates + boot assessment: `docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`, `spec/boot.health.gate.policy.schema.json`, `spec/boot.health.report.schema.json`, `spec/boot.bless.receipt.schema.json`
- Slot-based A/B update mental model (Android/ChromeOS lessons): `docs/359-slot-based-updates-and-boot-assessment-lessons.md`

- Installation + recovery as derived operations (installer/recovery images as artifacts; install as change sets): `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/250-breakglass-and-recovery-workflows.md`
- Derived recovery images + minimal userspace (repair ergonomics as artifacts): `docs/360-derived-recovery-images-and-minimal-userspace.md`
- Disk layout plans/receipts (partitioning as evidence): `docs/310-disk-layout-plans-and-receipts.md`, `spec/disk.layout.plan.schema.json`, `spec/disk.layout.receipt.schema.json`
- Hardware inventory + driver binding as evidence (privacy-safe, digest-first): `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `spec/hw.inventory.receipt.schema.json`
- Hardware compatibility gates (preflight before switching generations): `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.compat.report.schema.json`
- Firmware inventory + updates + UEFI variable writes as evidence (no platform drift folklore): `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`

- Operator access as leases (SSH certs; session evidence; optional TTY recording): `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`
- Data at rest (ZFS encryption + key management lanes, A–D viable): `docs/409-zfs-encryption-and-key-management.md` (see also: `docs/146-zfs-native-encryption-for-generations.md`)
- Optional OCI host transport (bootc lessons): `docs/133-bootable-oci-host-images-bootc-lessons.md`
- Secure boot hooks (optional): `docs/51-secure-boot-integration.md`, `docs/244-bootchain-revocation-and-allowlists.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`
- Measured boot + posture receipts (optional, explainable): `docs/176-measured-boot-attestation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`, `spec/boot.manifest.schema.json`, `spec/boot.attestation.schema.json`
- Unified boot capsules (single signed/measurable boot payload): `docs/358-unified-boot-capsules-and-measured-boot-receipts.md`
- Measured launch / DRTM lane (late launch integrity, optional): `docs/390-measured-launch-and-drtm-trenchboot-lane.md`
- Attester provisioning receipts (optional, makes enrollment auditable/operable): `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `spec/attester.provision.receipt.schema.json`

### 3) Hypervisor-centric runtime (microVM-first)
- Direction + rationale: `docs/22-scope-and-direction.md`, `docs/23-hypervisor-centric-derivebsd.md`
- MicroVM artifact target: `docs/24-microvm-artifact-target.md`, `docs/73-artifact-target-framework.md`
- Optional ABI compatibility adapter lane (Linux emulation vs microVMs): `docs/408-abi-compatibility-lanes-linuxulator-vs-microvms.md`
- Runtime manifest + bundle format: `docs/33-runtime-manifest-schema.md`, `docs/34-microvm-bundle-format.md`, `docs/128-image-registry-imgadm-lessons.md`
- Optional verified lazy rootfs mounts (on-demand): `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- Optional P2P distribution/swarm caches (fleet rollout acceleration): `docs/301-p2p-distribution-and-swarm-caches.md`
- Control plane: `docs/29-vm-control-plane.md`
- Launch plans + receipts (runtime join key; receipts even on denial): `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.plan.schema.json`, `spec/microvm.launch.receipt.schema.json`
- bhyve backend mapping: `docs/40-bhyve-config-mapping.md`, `docs/25-hypervisor-backends.md`
- IO/control channels: `docs/72-bhyve-io-channels.md`
- Runtime blast-radius contract: `docs/94-runtime-blast-radius-contract.md`
- Optional confidential microVMs (TEE-backed isolation + attestable receipts): `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`, `docs/331-tee-attestation-in-practice-snp-tdx-and-verifier-services.md`, `spec/tee.attestation.reference.schema.json`, `spec/tee.attestation.evidence.schema.json`, `spec/tee.attestation.receipt.schema.json`
- Networking: `docs/26-virtual-networking-pf.md`, `docs/67-pf-anchors-per-instance.md`, `docs/64-networking-modes-mapping.md`, `docs/322-network-topology-and-firewall-as-derived-operations.md`
- Device isolation domains (driver VMs): `docs/204-device-isolation-domains.md`
- Device grants + /dev authority (devfs rulesets): `docs/278-device-grants-and-devfs-rulesets.md`
- Devfs views as derived operations (plans/receipts/events for `/dev` exposure): `docs/323-devfs-views-plans-and-receipts.md`, `spec/devfs.view.plan.schema.json`
- USB quarantine + removable media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- Resource governance (limits + optional budget capabilities): `docs/65-resource-governance.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/193-resource-budget-capabilities.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/285-hierarchical-resource-limits-compilation.md`
  - QoS/accounting discipline (isolation + exposure + responsibility): `docs/346-nemesis-isolation-exposure-responsibility.md`
- Rollout + rollback: `docs/35-workload-rollout-rollback.md`

### 4) “Explainability” surfaces (why/what/where-from)
- Explainability contract: `docs/95-explainability-contract.md`
- Policy replay + counterfactual explanations: `docs/312-policy-replay-and-counterfactual-explanations.md`
- Structured outputs: `docs/87-structured-output-contract.md`, `docs/38-structured-outputs.md`
- Diff + review workflows: `docs/66-diff-and-review-workflows.md`
- Repro capsules: `docs/39-repro-capsules.md`
- Observability evidence (DTrace/audit): `docs/120-observability-explainability-dtrace.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/52-host-auditing-openbsm.md`
- Structured diagnostics (Inspect-style trees) as queryable state: `docs/302-structured-diagnostics-inspect-trees.md`
- Diagnostics query plane (selectors + snapshots; Archivist-style): `docs/372-inspect-style-structured-introspection.md`
- Flight recorder tracing + budgeted diagnostics (always-on, bounded): `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`
- Evidence vault (write-once, content-addressed history for receipts/traces): `docs/350-venti-fossil-write-once-archive-store.md`
- Observability as capability (no ambient debug authority): `docs/192-observability-as-capability.md`
- Structured event journal (typed logs as evidence): `docs/215-structured-event-log-as-evidence.md`
- Optional event sealing receipts (tamper-evident local evidence): `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`
- Durable attestation / posture timelines (time series of verifier receipts, retention budgeted): `docs/315-durable-attestation-and-posture-timelines.md`, `spec/attestation.receipt.schema.json`
- Remote attestation admission policy (make “what is gated?” reviewable, optional): `docs/388-remote-attestation-admission-and-enrollment.md`, `spec/attestation.admission.policy.schema.json`, `spec/attestation.requirement.schema.json`
- Incident snapshots + support bundles (shareable context as evidence): `docs/216-incident-snapshots-and-support-bundles.md`
- Incident timelines (human-scale orientation surface): `docs/419-incident-timelines-as-derived-artifacts.md`, `spec/incident.timeline.schema.json`
- Hardware inventory receipts + hardware compat reports (supportability without SSH; preflight safety): `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`
- Time-travel snapshots as leases ("previous versions" without ambient snapshot exposure): `docs/300-time-travel-snapshots-as-leases.md`
- Export policies + support-bundle portal (user/policy-mediated sharing): `docs/251-export-policies-and-support-bundle-portal.md`
- Remote assistance sessions as evidence (screen share + control without backdoors): `docs/291-remote-assistance-sessions-as-evidence.md`, `spec/support.session.schema.json`
- Terminal session recording as evidence (TTY I/O logs, optional): `docs/292-terminal-session-recording-as-evidence.md`, `spec/tty.session.recording.schema.json`
- Bundle plans + deterministic exports (selection+transforms as evidence): `docs/253-bundle-plans-and-deterministic-exports.md`
- Export transparency logs (prove what left the system, optional): `docs/254-export-transparency-logs.md`
- Release capsules + transparency (single verifiable release handle): `docs/257-release-capsules-and-transparency.md`
- Transparency monitors + witness gossip (alerts as evidence): `docs/259-transparency-monitors-and-witness-gossip.md`
- Witness networks + checkpoint cosigning (split-view defense as an operable parameter): `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `spec/log.checkpoint.receipt.schema.json`
- Release authority policy (threshold publishing + emergency halts): `docs/260-release-authority-policy-and-key-management.md`
- Rollout privacy constraints (cohort hygiene): `docs/261-rollout-privacy-and-cohort-hygiene.md`
- Policy-constrained transports (ticketing uploads as evidence, optional): `docs/255-policy-constrained-transports.md`
- Consent UX contract (uniform approvals across GUI/TTY/OOB): `docs/256-consent-ux-contract.md`
- Multiparty approvals + separation of duties (quorum approvals as evidence): `docs/288-multiparty-approvals-and-separation-of-duties.md`

- Causality graphs (minimal evidence index): `docs/246-causality-graphs-and-minimal-evidence-bundles.md`
- Crash artifacts + symbolication as evidence (crash reports, dumps, build-id symbols): `docs/224-crash-artifacts-and-symbolication-as-evidence.md`, `spec/crash.report.schema.json`
- State snapshot + migration receipts (what schema changed, and why): `docs/217-state-datasets-and-migrations-as-evidence.md`
- Backups + restores as derived operations (state replication + rehearsed recovery as evidence): `docs/316-backups-and-restores-as-derived-operations.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `spec/restore.drill.receipt.schema.json`
- Configuration transactions + receipts (commit-confirmed for risky changes): `docs/218-configuration-transactions-and-receipts.md`
- /etc drift diffs as a stable review surface (gateable; attach to drift bundles): `docs/427-etc-config-diff-as-a-drift-surface.md`
- Change sets + apply engine (unify multi-step transitions): `docs/219-change-sets-and-apply-engine.md`
- Kernel tunables + sysctls as evidence (no mystery knobs; drift is a fact): `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`
- Kernel module policy + loading as evidence (treat kmods as executable code): `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `spec/kmod.policy.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`
- Secrets and key management as evidence (brokered creds, no inline secrets): `docs/223-secrets-and-key-management-as-evidence.md`
- Crypto operations portal (split keys; sign/decrypt by lease + receipts): `docs/306-crypto-operations-portal-and-split-keys.md`, `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`
- Crypto key policies (non-exportable default; quorum + presence hooks): `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`
- Crypto surface registry + diff gates (protocol/suite/library drift is reviewable): `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- PKI + trust bundles as evidence (trust-store is a versioned object; CA injection is digest-pinned): `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `spec/pki.trust.bundle.schema.json`, `spec/pki.issue.plan.schema.json`, `spec/pki.issue.receipt.schema.json`
- Sealed secrets + attested unsealing (TPM policy lane, optional): `docs/272-sealed-secrets-attested-unsealing.md`
- Platform posture + attestation receipts as evidence (reusable verifier results): `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- Firmware updates as artifacts (inventory + plans + receipts): `docs/221-firmware-updates-as-artifacts.md`
- Debugging by lease (record/replay capsules): `docs/194-debugging-by-lease-and-replay-capsules.md`
- Deterministic concurrency lane (optional; shrink replay capsules, tame heisenbugs): `docs/377-deterministic-concurrency-lane.md`
- Chaos experiments + fault injection as leases (optional; resilient-by-practice): `docs/389-chaos-experiments-and-fault-injection-as-leases.md`, `spec/chaos.experiment.plan.schema.json`, `spec/chaos.experiment.receipt.schema.json`
- Automated bisection + root-cause certificates (optional): `docs/275-root-cause-certificates-and-bisection.md`
- Lease envelope + cross-lane joins (unified temporary authority metadata): `docs/252-lease-envelope-and-cross-lane-joins.md`
- Operational time-travel debugging (replay capsules in change/incident workflows): `docs/220-operational-time-travel-debugging.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Time + entropy authority for determinism and replay: `docs/197-time-and-rng-authority.md`
- Time discipline + trustworthy timestamps as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- Time sources in practice (chrony NTS + Roughtime quorum): `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- Time monitors + lie detection (treat time like a transparency problem): `docs/308-time-monitors-and-lie-detection.md`
- Evidence spine overview (receipts everywhere): `docs/229-evidence-spine-overview.md`
- Capability activation + escrow (restart-safe authority, socket-activation generalized): `docs/196-capability-activation-and-escrow.md`

### 5) Mile-high directions (brainstorm → RFCs)

These are intentionally **short**: they capture promising paradigms and where they plug into the pipeline.

- Roadmap / idea inventory: `docs/99-mile-high-directions.md`
- Feature-harvest rubric (keep “ecosystem steals” disciplined): `docs/296-feature-harvest-rubric.md`
- “Deployments are commits” (ZFS-native): `docs/100-deployments-are-commits.md`
- CAS everywhere (beyond “binary cache”): `docs/101-cas-everywhere.md`
- Emergency patch mode (graft-like, auditable): `docs/102-emergency-grafts.md`
- Breakglass + recovery mode (repair without destroying evidence): `docs/236-breakglass-and-recovery-mode.md` (RFC-0168)
- Verified execution at runtime (optional MAC/veriexec): `docs/103-runtime-verified-execution.md`
- Builder strategy (jail builds + optional microVM builders): `docs/104-builder-tiers.md`
- Compatibility view for foreign binaries (libmap/hints): `docs/105-compat-view-foreign-binaries.md`
- Strata and multi-origin userlands (explicit composition of adapter trees): `docs/295-strata-and-multi-origin-userlands.md`
- Blast-radius diffs as first-class review: `docs/106-blast-radius-diff.md`
- Drift bundles as the default review attachment (link all diffs + evidence): `docs/395-drift-bundles-and-review-summaries.md`
- Authority graphs + `authority.diff` as a review substrate: `docs/366-capability-graphs-and-authority-diff-surfaces.md`
- Trust boundary graphs + threat diffs (new boundary = reviewable artifact): `docs/380-trust-boundary-graphs-and-threat-diff.md`
- Two-person integrity (separate approvals): `docs/107-two-person-integrity.md`
- Ports/pkg adapter lane (breadth without chaos): `docs/108-ports-pkg-adapter-lane.md`
- Repo signing UX lessons (pkg-style ergonomics): `docs/109-repo-signing-ux.md`
- Juicy OS lessons index: `docs/110-juicy-os-lessons.md`
- Feature flags as typed inputs (USE lessons): `docs/262-feature-flags-and-constraints.md`
- Flake-style input graphs + registries (composition lessons): `docs/263-flake-style-input-graphs-and-registries.md`
- Filesystem views as capabilities (Plan 9 union lessons): `docs/264-mount-namespaces-and-union-views.md`
- Portable service bundles (attach/detach ops tooling lane): `docs/265-portable-service-bundles.md`
- Open questions + risk register (what to decide next): `docs/266-open-questions-and-risk-register.md`
- Sanitization portal (Dangerzone-style disposable transform): `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- Desktop AppVMs + portalized apps (Qubes/Flatpak stance): `docs/268-desktop-appvms-and-portalized-apps.md`
- Consent ledgers + permission review UI: `docs/369-consent-ledgers-and-permission-review-ui.md`
- Permission center + authority introspection (review/revoke/explain in one place): `docs/371-permission-center-and-authority-introspection.md`
- Portable home areas + embedded user records (systemd-homed lesson): `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage: template + private + volatile (+ optional home areas): `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- Packaged base sets (pkgbase lessons): `docs/111-packaged-base-pkgbase.md`
- Health-gated updates (boot success gate): `docs/112-health-gated-updates.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`
- Signed revertible patchsets (syspatch-style): `docs/113-syspatch-style-patchsets.md`
- Service manifests as derived graphs (SMF lessons): `docs/114-service-manifests-smf-lessons.md`
- Compartmentalized control planes (Qubes lessons): `docs/115-compartmentalized-control-planes.md`
- Witness rebuilders + deep diffs: `docs/116-witness-rebuilders-diffoscope.md`
- Reproducible generations + determinism check lane: `docs/367-reproducible-generations-and-determinism-checks.md`
- Impurity waiver policy + gateable diff surface (keep “known impurity” non-ambient): `docs/445-impurity-waiver-policy-diff-as-review-surface.md`
- Pledge/unveil mindset (ergonomics): `docs/117-pledge-unveil-mindset.md`
- pledge/unveil-style promises compiled to Derive profiles: `docs/368-pledge-unveil-style-promises-and-derive-profiles.md`
- Distributed unprivileged builds (pbulk lessons): `docs/118-distributed-builds-pbulk.md`
- Store/image distribution adapters (casync/CernVM-FS): `docs/119-casync-cvmfs-distribution.md`
- Verified lazy rootfs + on-demand mounts (composefs/eStargz/Nydus): `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- P2P distribution + swarm caches (Dragonfly lesson): `docs/301-p2p-distribution-and-swarm-caches.md`
- Observability as explainability (DTrace): `docs/120-observability-explainability-dtrace.md`
- Jailed hypervisor workers (bhyve-in-jail): `docs/121-jailed-hypervisor-workers.md`
- System extensions for immutable bases: `docs/122-system-extensions.md`
- Ignition-style first boot provisioning: `docs/123-ignition-style-firstboot.md`
- virtio-9p as a restricted file channel: `docs/124-virtio-9p-injection-channel.md`
- Per-jail hardening knobs (secadm mindset): `docs/125-hardening-knobs-per-jail.md`
- ZFS send/recv distribution lane: `docs/126-zfs-send-distribution.md`
- Uptane “director” role (bytes vs assignment): `docs/127-uptane-director-targets.md`
- Image registry lessons (SmartOS imgadm/IMGAPI): `docs/128-image-registry-imgadm-lessons.md`
- Template microVMs and disposable instances (Qubes disk model): `docs/129-template-microvms-and-disposables.md`
- ZFS bookmarks and redaction bookmarks (sanitized replication): `docs/130-zfs-bookmarks-and-redaction.md`
- Sigsum transparency lane (lightweight): `docs/131-sigsum-lightweight-transparency.md`
- SCITT ledger receipts (publication evidence): `docs/132-scitt-ledger-receipts.md`
- Bootable OCI host images (bootc lessons): `docs/133-bootable-oci-host-images-bootc-lessons.md`
- Declarative image pipelines (apko/melange/Wolfi lessons): `docs/134-declarative-image-pipelines-apko-melange.md`
- Cross-compartment RPC policy (qrexec lessons): `docs/135-qrexec-style-rpc-policy.md`
- Remote execution API builder pools (REAPI lessons): `docs/136-remote-execution-api-builder-pools.md`
- Anti-rollback rollback indices (Verified Boot lesson): `docs/137-anti-rollback-rollback-index.md`
- Offline signed update bundles (RAUC/fwup lessons): `docs/138-offline-signed-update-bundles.md`
- Air-gap mirror kits + sneakernet updates (offline happy path): `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`
- Mirror kit manifest (self-describing offline kit index): `docs/447-mirror-kit-manifest-as-evidence-artifact.md`
- Bandwidth-efficient deltas (OSTree static deltas): `docs/139-bandwidth-efficient-deltas.md`
- Capability routing manifests (Fuchsia lessons): `docs/140-capability-routing-manifests.md`
- Component descriptors → compiled runtime manifests (single source of “how it runs”): `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- Build records (`.buildinfo` lessons) + witness rebuilders: `docs/141-build-records-buildinfo-and-rebuilders.md`
- Trustworthy time inputs (Roughtime + LKGT): `docs/142-trustworthy-time-roughtime.md`
- Trustworthy time: NTS + Roughtime + LKGT wiring: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- Policy-derived resource budgets (rctl/racct/cpuset): `docs/143-resource-controls-rctl-racct-cpuset.md`
- Authority budgets + permission drift alarms (stop capability creep early): `docs/298-authority-budgets-and-permission-drift-alarms.md`
- Routing isolation via multiple FIBs (setfib): `docs/144-routing-isolation-fibs-setfib.md`
- Optional unikernel lane (Solo5/rump lessons): `docs/145-unikernel-lane-rump-solo5.md`
- Optional CHERI lane (capability hardware memory safety + compartmentalization): `docs/387-cheri-capability-hardware-and-memory-safety-lane.md`
- ZFS native encryption for state/generations (key-use evidence): `docs/146-zfs-native-encryption-for-generations.md`
- Minimal privilege escalation rules (doas-style): `docs/147-doas-minimal-privilege-escalation.md`
- Reproducibility variation harness (reprotest/diffoscope/stabilizers): `docs/148-reproducibility-variation-harness-reprotest.md`
- Human-editable policy sources (HuJSON) + canonical signing (JCS): `docs/149-human-policy-hujson-and-canonicalization.md`
- Jail profiles as derived allowlists (allow.* knobs + devfs rulesets): `docs/150-jail-profiles-and-allowlist-knobs.md`
- Factotum-style credential broker (protocol-agnostic agent): `docs/151-factotum-style-credential-broker.md`
- Store view minimization (hide non-required store paths from builders): `docs/152-store-view-minimization.md`
- sandboxfs-accelerated store views (optional performance optimization): `docs/167-sandboxfs-accelerated-storeviews.md`
- Store immutability invariants (prevent post-build mutation / TOCTOU): `docs/153-store-immutability-and-toc-tou.md`
- SBOM + VEX as evidence objects (inventory + exploitability context): `docs/168-sboms-and-vex-as-evidence.md`
- Jobsets + build farms (Hydra lessons): `docs/169-jobsets-and-build-farms.md`
- Remote cache threat model (poisoning + verification): `docs/170-remote-cache-threat-model.md`
- VNET jails as network compartments (separate per-domain stacks): `docs/171-vnet-jails-network-compartments.md`
- Hypervisor device backend isolation (hardening lane): `docs/172-device-backend-isolation-bhyve.md`
- Compiled service database + bundles (s6-rc lessons): `docs/173-compiled-service-database-bundles.md`
- Specialisations/variants within a generation (safe-mode, role-mode): `docs/174-specialisations-and-variants.md`
- Pins/roots and garbage collection (retention ergonomics): `docs/175-pins-roots-and-garbage-collection.md`
- Receipted store GC plans/receipts (retention as evidence): `docs/426-store-gc-plans-and-receipts.md`, `spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json`
- Measured boot + remote attestation lane (optional): `docs/176-measured-boot-attestation.md`
- Fleet-coordinated staged rollouts (optional): `docs/177-fleet-coordinated-rollouts.md`
- Sigstore keyless signing adapter (optional): `docs/178-sigstore-keyless-signing-adapter.md`
- Portals / powerbox broker (mediated capability acquisition): `docs/179-portals-and-powerbox.md`
- ScreenCast + RemoteDesktop portals (screen sharing + remote control): `docs/208-screencast-and-remote-desktop-portals.md`
- Camera + audio capture portals (AV devices as leased streams): `docs/209-camera-and-audio-capture-portals.md`
- Capability mode + dynamic linking strategy: `docs/180-capability-mode-dynamic-linking.md`
- Workload identity + secretless deploys (SPIFFE/SPIRE-shaped lane): `docs/181-workload-identity-and-secretless-deploys.md`
- Capability leases + revocation (revocable grants): `docs/182-capability-leases-and-revocation.md`
- Lease registry + cross-lane revocation (unify all temporary authority): `docs/249-lease-registry-and-cross-lane-revocation.md`
- Object-capability RPC lane (capability-carrying crossings): `docs/183-object-capability-rpc.md`
  - Contract channels as policy inputs (Singularity lesson): `docs/339-singularity-manifests-and-contract-channels.md`
  - FD-first capability IPC (Doors lesson): `docs/341-doors-lightweight-capability-rpc.md`
  - File-shaped broker APIs (Inferno lesson): `docs/340-inferno-styx-and-distributed-namespaces.md`
  - Capability-kernel lessons (KeyKOS/EROS): `docs/343-keykos-eros-capability-kernel-lessons.md`
- Attenuating delegation tokens (Macaroons/Biscuit lane): `docs/184-attenuating-delegation-tokens.md`
- Portal consent receipts (auditable interactive ask): `docs/185-portal-consent-and-audit-receipts.md`
- Policy modules as WebAssembly (sandboxed extensibility lane): `docs/186-policy-modules-wasm.md`
- Policy module diff as a review surface (gateable policy-code drift): `docs/451-policy-module-diff-as-review-surface.md`
- Witnessed transparency checkpoints (split-view defense): `docs/187-witnessed-transparency-checkpoints.md`
- Debugging by lease (record/replay capsules): `docs/194-debugging-by-lease-and-replay-capsules.md`
- Automated bisection + root-cause certificates (optional): `docs/275-root-cause-certificates-and-bisection.md`
- Lease envelope + cross-lane joins (unified temporary authority metadata): `docs/252-lease-envelope-and-cross-lane-joins.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Time + entropy authority for determinism and replay: `docs/197-time-and-rng-authority.md`
- Time discipline + trustworthy timestamps as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- Evidence spine overview (receipts everywhere): `docs/229-evidence-spine-overview.md`
- Capability activation + escrow (restart-safe authority, socket-activation generalized): `docs/196-capability-activation-and-escrow.md`
- DevShells (nix-shell parity): `docs/159-devshells.md`
- Overlay transforms (Nix overlay analogue): `docs/160-overlay-transforms.md`
- Module + options layer (NixOS-ish composition): `docs/161-module-and-options-layer.md`
- User environments (Home-Manager analogue): `docs/162-user-environments.md`
  - Activation plans/receipts (profiles, generations, atomic switch): `docs/386-userenv-activation-plans-and-receipts.md`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`
- CHERI capability lane (optional hardening): `docs/163-cheri-capability-lane.md`
- CHERI temporal revocation vs authority revocation (design with indirection): `docs/250-cheri-temporal-revocation-and-indirection.md`
- Split crypto domains (split-GPG lesson): `docs/164-split-crypto-domains.md`
- FreeBSD pkg repository adapter (optional compatibility lane): `docs/165-freebsd-pkg-repo-adapter.md`
- Test receipts as evidence (promotion gates): `docs/166-test-receipts-and-promotion-gates.md`

### 6) Tests + promotion gates
- Conformance/regression harness: `docs/88-conformance-tests-kyua-atf.md`
- Test receipts as evidence: `docs/166-test-receipts-and-promotion-gates.md`
- Scenario tests (multi-machine): `docs/188-scenario-tests-multimachine.md`
- Interactive VM test driver + artifact capture: `docs/405-interactive-vm-tests-and-artifact-capture.md`
- Model checking as evidence: `docs/287-formal-model-checking-and-invariants.md` (starter models in `docs/models/`).

### 7) Authority graphs
- Capability routing manifests (Fuchsia lessons): `docs/140-capability-routing-manifests.md`
- Genode init + nested capability distribution lessons: `docs/375-genode-init-and-capability-routing-lessons.md`
- Component descriptors → compiled runtime manifests (single source of “how it runs”): `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- Capability graph lint/viz: `docs/189-capability-graph-lint-and-viz.md`
- Authority diff schema + review workflows: `docs/374-authority-diff-schema-and-review-workflows.md`

### 7.1) Observability and budgets as authority
- Observability authority as leased grants: `docs/192-observability-as-capability.md`
- Delegable resource budgets as grants (optional): `docs/193-resource-budget-capabilities.md`

### 8) Cache and toolchain trust (optional high-assurance lanes)
- Cache witness quorums (Trustix-style): `docs/190-cache-witness-quorums-trustix.md`
- DDC + bootstrappable toolchains: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`
- Proof artifacts and formal verification lanes (proofs as supply-chain evidence): `docs/373-proof-artifacts-and-formal-verification-lanes.md`

## Where to add new work

- New proposal → `rfcs/` (draft first)
- Accepted decision → `adrs/` (append-only)
- Consolidated “current truth” → `docs/` (short, updated)

## References

Start at: `docs/32-curated-references.md`

Last updated: 2026-03-04r185
## New in 2026-02-27r123 (risk register index + risk lint)

- Add a generated **risk register index** (markdown + JSON) so `docs/266` stays scannable and machine-usable (`docs/415-risk-register-index.md`, `docs/_generated/risk_register.json`, `tools/gen_risk_register_index.py`).
- Add a simple **risk register lint** and wire into hygiene to keep failure modes explicit (`tools/check_risk_register.py`, `tools/hygiene.py`).
- Extend generated-doc guardrails + discovery wiring to cover the new risk index (`tools/check_generated_docs.py`, `tools/check_discovery.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-02-27r122 (doc catalog + generated-doc guardrail)

- Added a generated doc catalog + JSON index as a navigation/memory prosthetic: `docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`, generator `tools/gen_doc_catalog.py`
- Extended generated-doc checks to cover the doc catalog outputs (prevents silent drift): `tools/check_generated_docs.py`

## New in 2026-02-27r121 (profile matrix + doc metadata guardrail + ZFS replication robustness)

- Add a generated **A–D product profile matrix** doc plus a generator + stale-check so profile defaults/invariants stay mechanically visible and don't drift (`docs/412-product-profile-matrix.md`, `tools/gen_product_profile_matrix.py`, `tools/check_generated_docs.py`).
- Add a lightweight **doc metadata** guardrail for the meta-engineering doc range (>=397): new docs must declare Tier/Profiles/Pillars near the top; wire check into hygiene (`tools/check_doc_metadata.py`, `tools/hygiene.py`).
- Add a tight ZFS replication operations doc focused on **resume tokens**, **bookmarks**, and **encryption-aware** replication, and wire it into backup/distribution lanes + profile defaults (`docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/126-zfs-send-distribution.md`, `spec/examples/product.profiles.json`).

## New in 2026-02-27r120 (profiles + at-rest encryption + desktop viability + anti-amnesia tooling)

- [99 LLM runbook](99-llm-runbook.md)
- [411 Product profiles as compilation targets](411-product-profiles-as-compilation-target.md)
- [409 ZFS encryption and key management](409-zfs-encryption-and-key-management.md)
- [410 Desktop viability checklist](410-desktop-viability-checklist.md)

## New in 2026-02-27r119 (schema conventions + ABI compatibility lane)

- [407 Spec schema conventions and evolution](407-spec-schema-conventions-and-evolution.md)
- [408 ABI compatibility lanes: Linux emulation vs microVMs](408-abi-compatibility-lanes-linuxulator-vs-microvms.md)

## New in 2026-02-27r118 (interactive VM tests + UAPI fuzz descriptors)

- [405 Interactive VM tests and artifact capture](405-interactive-vm-tests-and-artifact-capture.md)
- [406 UAPI fuzz descriptors and conformance](406-uapi-fuzz-descriptors-and-conformance.md)

## New in 2026-02-27r117 (SWHID source archival + ZFS BE generation contract)

- [403 SWHID fallback + long-term source availability](403-swhid-fallback-and-long-term-source-availability.md)
- [404 ZFS boot environments as system generations](404-zfs-boot-environments-as-system-generations.md)

## New in 2026-02-27r116 (v0 cutline + killable adapters)

- [401 v0 cutline and feature tiers](401-v0-cutline-and-feature-tiers.md)
- [402 Adapter lanes and strangler discipline](402-adapter-lanes-and-strangler-discipline.md)

## New in 2026-02-27r115 (netgraph + netmap/VALE derived fabrics)

- [400 Netgraph and netmap as derived network fabrics](400-netgraph-and-netmap-as-derived-network-fabrics.md)

## New in 2026-02-27r114 (pattern catalog + Zig toolchain wedge + evidence queries)

- [397 DeriveBSD pattern catalog](397-pattern-catalog.md)
- [398 Zig toolchain wedge and cross compilation](398-zig-toolchain-wedge-and-cross-compilation.md)
- [399 Evidence queries and fact tables](399-evidence-queries-and-fact-tables.md)

## New in 2026-02-27r113 (drift bundles + closure diffs)

- [395 Drift bundles and review summaries](395-drift-bundles-and-review-summaries.md)
- [396 Closure diffs and new code surfaces](396-closure-diffs-and-new-code-surfaces.md)

## New in 2026-02-27r112 (policy test suites + mutation testing + policy analysis lane)

- Policy tests as first-class artifacts: introduce `policy.test.suite` + `policy.test.report` schemas and document the regression/mutation testing posture (`docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`, and examples).
- Add an optional policy analysis lane (automated reasoning complements tests for high-assurance authorization) (`docs/394-policy-analysis-and-automated-reasoning.md`).
- Wire the new lane into discovery surfaces and meta-engineering guardrails (design rubric + principles + references) (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/12-design-principles.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## New in 2026-02-27r111 (crypto drift surfaces + key policies + blast-radius crypto section)

- Make crypto drift reviewable with `crypto.registry` + `crypto.diff` (protocols/suites/blessed libraries/key policies as first-class surfaces): `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- Introduce `crypto.key.policy` to standardize non-exportable key definitions (backend binding, subject selectors, quorum/presence hooks): `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`
- Extend blast-radius diffs to optionally include a `crypto` section (umbrella report can carry crypto drift): `spec/blast_radius.diff.schema.json`, `spec/examples/blast_radius.diff.json`, `docs/106-blast-radius-diff.md`
- Wire crypto surfaces into the meta-engineering guardrails (design rubric + surface registry pattern + design principles): `docs/348-design-review-rubric-and-feature-intake.md`, `docs/379-surface-registry-pattern.md`, `docs/12-design-principles.md`

## New in 2026-02-27r110 (CHERI lane + attestation admission policy + chaos leases + measured launch)

- [387 CHERI: capability hardware and a memory-safety lane](387-cheri-capability-hardware-and-memory-safety-lane.md)
- [388 Remote attestation: admission and enrollment](388-remote-attestation-admission-and-enrollment.md)
- [389 Chaos experiments and fault injection as leases](389-chaos-experiments-and-fault-injection-as-leases.md)
- [390 Measured launch (DRTM) and late-launch integrity](390-measured-launch-and-drtm-trenchboot-lane.md)

## New in 2026-02-27r109 (kernel extensibility + deprecation lifecycle + userenv activation)

- [384 Kernel extensibility: BPF/JIT risk](384-kernel-extensibility-bpf-and-jit-risk.md)
- [385 Deprecation policies and removal receipts](385-deprecation-policies-and-removal-receipts.md)
- [386 UserEnv activation plans and receipts](386-userenv-activation-plans-and-receipts.md)
- (New schemas) `spec/deprecation.notice.schema.json`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`

## New in 2026-02-27r108 (trust boundaries + info-flow labels)

- [380 Trust boundary graphs and threat diff](380-trust-boundary-graphs-and-threat-diff.md)
- [381 Information-flow labels and declassification](381-information-flow-labels-and-declassification.md)
- [383 Surface ids: namespacing and stability](383-surface-ids-namespacing-and-stability.md)

## New in 2026-02-27r107 (determinism + denial-driven suggestions + surface registries)

- [377 Deterministic concurrency lane](377-deterministic-concurrency-lane.md)
- [378 Denial-driven policy suggestions](378-denial-driven-policy-suggestions.md)
- [379 Surface registry pattern](379-surface-registry-pattern.md)

## New in 2026-02-27r106 (parser registry + fuzz gates)

- [376 Parser surface registry and fuzz gates](376-parser-surface-registry-and-fuzz-gates.md)

## New in 2026-02-27r105 (inspect + proof lanes + authority.diff schema)

- [372 Inspect-style structured introspection](372-inspect-style-structured-introspection.md)
- [373 Proof artifacts and formal verification lanes](373-proof-artifacts-and-formal-verification-lanes.md)
- [374 Authority diff schema and review workflows](374-authority-diff-schema-and-review-workflows.md)
- [375 Genode init and capability-routing lessons](375-genode-init-and-capability-routing-lessons.md)

## New in 2026-02-27r104 (contract registries + permission center)

- [370 Contract registries and API-diff gates](370-contract-registries-and-api-diff-gates.md)
- [371 Permission center and authority introspection](371-permission-center-and-authority-introspection.md)

## New in 2026-02-27r103 (authority graphs + reproducible generations + consent ledger)

- [366 Capability graphs and authority-diff surfaces](366-capability-graphs-and-authority-diff-surfaces.md)
- [367 Reproducible generations and determinism checks](367-reproducible-generations-and-determinism-checks.md)
- [368 Pledge/unveil-style promises and derive profiles](368-pledge-unveil-style-promises-and-derive-profiles.md)
- [369 Consent ledgers and permission review UI](369-consent-ledgers-and-permission-review-ui.md)

## New in 2026-02-27r102 (UAPI registry + driver tiering + hotpatch lane)

- [362 UAPI surface registry and compatibility gates](362-uapi-surface-registry-and-compat-gates.md)
- [363 Driver safety tiering (Rust-first, user-mode by default)](363-driver-safety-tiering-rust-and-user-mode.md)
- [364 Live patching lane (hotpatch capsules)](364-live-patching-lane-hotpatch-capsules.md)
- [365 Userspace filesystem servers (puffs/FUSE)](365-userspace-filesystems-puffs-fuse.md)


## New in 2026-02-25 (release capsules + staged rollouts)
- [257 Release capsules and transparency](257-release-capsules-and-transparency.md)
- [258 Staged rollouts and cohorts](258-staged-rollouts-and-cohorts.md)
- [259 Transparency monitors and witness gossip](259-transparency-monitors-and-witness-gossip.md)
- [260 Release authority policy and key management](260-release-authority-policy-and-key-management.md)
- [261 Rollout privacy and cohort hygiene](261-rollout-privacy-and-cohort-hygiene.md)
- [RFC-0189 Release capsules and transparency](../rfcs/RFC-0189-release-capsules-and-transparency.md)
- [RFC-0190 Staged rollouts and cohorts](../rfcs/RFC-0190-staged-rollouts-and-cohorts.md)
- [RFC-0191 Transparency monitors and alert evidence](../rfcs/RFC-0191-transparency-monitors-and-alert-evidence.md)
- [RFC-0192 Release authority policy](../rfcs/RFC-0192-release-authority-policy.md)
- [RFC-0193 Rollout privacy constraints](../rfcs/RFC-0193-rollout-privacy-constraints.md)

## New in 2026-02-25 (exports: policy + plans + transports + consent + transparency)
- [251 Export policies + support-bundle portal](251-export-policies-and-support-bundle-portal.md)
- [252 Lease envelope and cross-lane joins](252-lease-envelope-and-cross-lane-joins.md)
- [253 Bundle plans and deterministic exports](253-bundle-plans-and-deterministic-exports.md)
- [254 Export transparency logs](254-export-transparency-logs.md)
- [255 Policy-constrained transports](255-policy-constrained-transports.md)
- [256 Consent UX contract](256-consent-ux-contract.md)
- [RFC-0183 Export policies and support-bundle portal](../rfcs/RFC-0183-export-policies-and-support-bundle-portal.md)
- [RFC-0184 Lease envelope and cross-lane joins](../rfcs/RFC-0184-lease-envelope-and-cross-lane-joins.md)
- [RFC-0185 Bundle plans and deterministic exports](../rfcs/RFC-0185-bundle-plans-and-deterministic-exports.md)
- [RFC-0186 Export transparency logs](../rfcs/RFC-0186-export-transparency-logs.md)
- [RFC-0187 Policy-constrained transports](../rfcs/RFC-0187-policy-constrained-transports.md)
- [RFC-0188 Consent UX contract](../rfcs/RFC-0188-consent-ux-contract.md)

## New in 2026-02-25 (evidence spine overview + posture lockdown + explicit A/B lifecycle + boot assessment + confirmable change-sets + service contract handles)
- [229 Evidence spine overview](229-evidence-spine-overview.md)
- [230 Lockdown levels and securelevel](230-lockdown-levels-and-securelevel.md)
- [231 A/B updates and recovery semantics](231-ab-updates-and-recovery-semantics.md)
- [241 Boot try-counters and boot assessment](241-boot-try-counters-and-boot-assessment.md)
- [242 Confirmable change-sets and auto-revert](242-confirmable-change-sets-and-auto-revert.md)
- [243 Service contract handles and membership](243-service-contract-handles-and-membership.md)
- [244 Boot-chain revocation and allowlists](244-bootchain-revocation-and-allowlists.md)
- [245 Boot measurement phases and PCR separation](245-boot-measurement-phases-and-pcr-separation.md)
- [246 Causality graphs and minimal evidence bundles](246-causality-graphs-and-minimal-evidence-bundles.md)
- [RFC-0164 Lockdown levels as a first-class posture output](../rfcs/RFC-0164-lockdown-levels-as-a-first-class-posture-output.md)
- [RFC-0165 A/B update lifecycle on ZFS boot environments](../rfcs/RFC-0165-ab-update-lifecycle-on-zfs-boot-environments.md)
- [RFC-0173 Boot try-counters and boot assessment](../rfcs/RFC-0173-boot-try-counters-and-boot-assessment.md)
- [RFC-0174 Confirmable change-sets and auto-revert](../rfcs/RFC-0174-confirmable-change-sets-and-auto-revert.md)
- [RFC-0175 Service contract handles and membership](../rfcs/RFC-0175-service-contract-handles-and-membership.md)

## New in 2026-02-24 (ops evidence: faults + supervision + events + state + config + change sets + resources)
- [213 Fault management architecture](213-fault-management-architecture.md)
- [214 Service supervision + health as evidence](214-service-supervision-health-as-evidence.md)
- [215 Structured event journal as evidence](215-structured-event-log-as-evidence.md)
- [216 Incident snapshots + support bundles](216-incident-snapshots-and-support-bundles.md)
- [217 State datasets + migrations as evidence](217-state-datasets-and-migrations-as-evidence.md)
- [218 Configuration transactions + receipts](218-configuration-transactions-and-receipts.md)
- [219 Change sets + apply engine](219-change-sets-and-apply-engine.md)
- [220 Operational time-travel debugging](220-operational-time-travel-debugging.md)
- [221 Firmware updates as artifacts](221-firmware-updates-as-artifacts.md)
- [222 Resource governance as evidence](222-resource-governance-as-evidence.md)
- [223 Secrets and key management as evidence](223-secrets-and-key-management-as-evidence.md)
- [224 Crash artifacts and symbolication as evidence](224-crash-artifacts-and-symbolication-as-evidence.md)
- [225 Storage health + scrubbing as evidence](225-storage-health-and-scrubbing-as-evidence.md)
- [226 Platform posture + attestation receipts as evidence](226-platform-posture-and-attestation-results-as-evidence.md)
- [227 Time discipline + trustworthy timestamps as evidence](227-time-discipline-and-trustworthy-timestamps-as-evidence.md)
- [228 PKI + identity lifecycle as evidence](228-pki-and-identity-lifecycle-as-evidence.md)

## New in 2026-02-25 (promise profiles + verified exec as evidence)
- [232 Service promise profiles](232-service-promise-profiles.md)
- [233 Verified execution as evidence](233-verified-execution-as-evidence.md)
- [234 Anykernel + rump kernels](234-anykernel-and-rump-kernels.md)
- [235 Process contracts + service ownership](235-process-contracts-and-service-ownership.md)
- [236 Breakglass + recovery mode](236-breakglass-and-recovery-mode.md)
- [237 Lint reports + contract testing](237-lint-reports-and-contract-testing.md)
- [238 Portal-activated services + socket activation](238-portal-activated-services-and-socket-activation.md)
- [RFC-0166 Service promise profiles](../rfcs/RFC-0166-service-promise-profiles.md)
- (Updated) [RFC-0072 Runtime verified execution](../rfcs/RFC-0072-runtime-verified-execution.md)

## New in 2026-02-25 (bootchain revocation + measured-boot ergonomics + causality graphs)
- [244 Boot-chain revocation and allowlists](244-bootchain-revocation-and-allowlists.md)
- [245 Boot measurement phases and PCR separation](245-boot-measurement-phases-and-pcr-separation.md)
- [246 Causality graphs and minimal evidence bundles](246-causality-graphs-and-minimal-evidence-bundles.md)
- [RFC-0176 Bootchain policy and revocation](../rfcs/RFC-0176-bootchain-policy-and-revocation.md)
- [RFC-0177 Boot measurement phases](../rfcs/RFC-0177-boot-measurement-phases.md)
- [RFC-0178 Causality graphs as evidence](../rfcs/RFC-0178-causality-graphs-as-evidence.md)

## New in 2026-02-25 (sealed secrets + air-gap mirror kits)
- [272 Sealed secrets + attested unsealing (TPM policy lane)](272-sealed-secrets-attested-unsealing.md)
- [273 Air-gap mirror kits + sneakernet updates](273-airgap-mirror-kits-and-sneakernet-updates.md)

## New in 2026-02-25 (fuzzing farm + bisection certificates)
- [274 Continuous fuzzing farm](274-continuous-fuzzing-farm.md)
- [275 Root-cause certificates + bisection](275-root-cause-certificates-and-bisection.md)
- (Updated) [234 Anykernel + rump kernels](234-anykernel-and-rump-kernels.md)
- (Updated) [166 Test receipts + promotion gates](166-test-receipts-and-promotion-gates.md)

## New in 2026-02-25 (kmods + loader verification)
- [276 Kernel module policy + loading as evidence](276-kernel-module-policy-and-loading-as-evidence.md)
- [277 Loader verification + boot config constraints](277-loader-verification-and-boot-config-constraints.md)
- (Updated) [230 Lockdown levels and securelevel](230-lockdown-levels-and-securelevel.md)

## New in 2026-02-25 (remote assistance + terminal session recording)
- [291 Remote assistance sessions as evidence](291-remote-assistance-sessions-as-evidence.md)
- [292 Terminal session recording as evidence](292-terminal-session-recording-as-evidence.md)


## New in 2026-02-26r76 (operator access + policy replay)
- [311 Operator access as leases (SSH certificates + recorded sessions)](311-operator-access-leases-and-ssh-certs.md)
- [312 Policy replay and counterfactual explanations](312-policy-replay-and-counterfactual-explanations.md)


## New in 2026-02-26r80 (kernel mutation as evidence)
- [318 Kernel tunables + sysctls as evidence](318-kernel-tunables-and-sysctls-as-evidence.md)
- (Updated) [276 Kernel module policy + loading as evidence](276-kernel-module-policy-and-loading-as-evidence.md)


## New in 2026-02-26r81 (hardware inventory + compatibility gates)
- [319 Hardware inventory + driver binding as evidence](319-hardware-inventory-and-driver-binding-as-evidence.md)
- [320 Hardware compatibility gates + safe upgrades](320-hardware-compatibility-gates-and-safe-upgrades.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)


## New in 2026-02-26r82 (firmware updates + UEFI variable evidence)
- [321 Firmware updates + UEFI variables as evidence](321-firmware-updates-and-uefi-variables-as-evidence.md)
- (New schemas) `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [32 Curated references](32-curated-references.md)



## New in 2026-02-26r83 (host networking substrate as evidence)
- [322 Network topology + firewall as derived operations](322-network-topology-and-firewall-as-derived-operations.md)
- (New schemas) `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- (Updated) [67 pf anchors per instance](67-pf-anchors-per-instance.md)
- (Updated) [64 Networking modes mapping](64-networking-modes-mapping.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md)
- (Updated) [32 Curated references](32-curated-references.md)


## New in 2026-02-26r84 (devfs views as derived operations)
- [323 Devfs views: plans, receipts, and drift events](323-devfs-views-plans-and-receipts.md)
- (New schemas) `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`
- (Updated) [278 Device grants + devfs rulesets](278-device-grants-and-devfs-rulesets.md) (formalize `devfs.view.*` objects)
- (Updated) [297 Component descriptors + compiled runtime manifests](297-component-descriptors-and-compiled-runtime-manifests.md) (add devfs view output)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md) (add `/dev` views derived + receipted)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md) (device budgets consume devfs view receipts/events)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md) (add `/dev` drift risk item)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md) (add `/dev` view lesson)


## New in 2026-02-27r101 (capability hygiene + boot capsules + recovery ergonomics)
- [357 Capability attenuation, revocation, and membranes](357-capability-attenuation-revocation-and-membranes.md)
- [358 Unified boot capsules and measured-boot receipts](358-unified-boot-capsules-and-measured-boot-receipts.md)
- [359 Slot-based A/B updates and boot assessment lessons](359-slot-based-updates-and-boot-assessment-lessons.md)
- [360 Derived recovery images and minimal userspace](360-derived-recovery-images-and-minimal-userspace.md)
- [361 Safe crossing APIs and boundary bugs (Tock lessons)](361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md)
- (Updated) [12 Design principles](12-design-principles.md) (authority engineering principle)
- (Updated) [348 Design review rubric](348-design-review-rubric-and-feature-intake.md) (attenuation/revocation patterns)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md) (add 214–218)
- Update the open-questions/risk register entry for the crypto operations portal to include split-secrets workflow questions (`docs/266-open-questions-and-risk-register.md`).
