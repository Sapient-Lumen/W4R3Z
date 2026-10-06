# DeriveBSD Design Archive

A living archive for **DeriveBSD**—a hypervisor-centric, **FreeBSD-first**, BSD-native, “planned-from-scratch Nix successor” whose core aim is to **derive**
(**Spec → Lock → Plan → Artifact**) *verifiable, reproducible, policy-governed, rollbackable* host systems and workload images.

This archive is intentionally small: we **cite/link** external work instead of copying it. Start at `docs/00-index.md`.

## How to read

- **Entry point:** `docs/00-index.md`
- Then: `docs/00-vision.md`, `docs/01-glossary.md`, `docs/02-derive-core.md`
- Day-0 behavioral contract: `docs/97-non-negotiable-behaviors.md`
- Evidence spine overview: `docs/229-evidence-spine-overview.md`
- RFCs propose changes; ADRs record decisions.

## The non-negotiables

1. Artifacts are **immutable**
2. Inputs are **explicit**
3. Deterministic-by-default (impurity is **policy-controlled and logged**)
4. System changes are **atomic** and **rollbackable**
5. The Derive core stays **small, typed, and stable**
6. Dev environments (`derive develop` / `derive shell`) are **first-class derived artifacts**

## Repo map

- `docs/` : canonical reference docs (short, current truth)
- `rfcs/` : proposals under debate
- `adrs/` : decisions (append-only)
- `spec/` : schemas + examples

Notable v0.1 schema additions:
- trust policy: `spec/trust.policy.schema.json`
- closure proofs: `spec/closure.manifest.schema.json`, `spec/closure.proof.schema.json`
- boot attestation (optional lane): `spec/boot.attestation.schema.json`
- canonical boot event log transcript (measured boot replay + verifier explainability): `spec/boot.eventlog.canon.schema.json`
- boot health gate policy (health-gated rollback inputs): `spec/boot.health.gate.policy.schema.json`
- boot manifest (boot-critical closure for secure/measured boot): `spec/boot.manifest.schema.json`
- platform report (platform provenance evidence object): `spec/platform.report.schema.json`
- attester provisioning receipts (optional, makes enrollment auditable/operable): `spec/attester.provision.receipt.schema.json`
- policy module diffs (review policy-code drift): `spec/policy.module.diff.schema.json`
- attestation admission policy (make “what is gated?” reviewable): `spec/attestation.admission.policy.schema.json`
- crypto registry + crypto diffs (review crypto drift): `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- crypto key policies (non-exportable keys as policy objects): `spec/crypto.key.policy.schema.json`
- devshell spec: `spec/devshell.spec.schema.json`
- component descriptors (runtime contract source): `spec/derive.unit.schema.json`
- contract registries + diffs (interface surfaces as derived artifacts): `spec/contract.registry.schema.json`, `spec/contract.diff.schema.json`
- UAPI registries + diffs (kernel surfaces as contracts): `spec/uapi.registry.schema.json`, `spec/uapi.diff.schema.json`
- authority diffs (reviewable authority deltas between generations): `spec/authority.diff.schema.json`
- parser registries + diffs (machine-checkable decode surface drift): `spec/parser.registry.schema.json`, `spec/parser.diff.schema.json`
- trust boundary graphs + diffs (threat boundary drift as a review surface): `spec/trust.boundary.graph.schema.json`, `spec/trust.boundary.diff.schema.json`
- drift bundles (one review attachment links all diffs + evidence): `spec/drift.bundle.schema.json`
- adapter kill policy + diffs (interop kill switches; Adapter→Shadow→Replace posture is reviewable): `spec/adapter.kill.policy.schema.json`, `spec/adapter.kill.policy.diff.schema.json`
- closure diffs (new code ingestion review surface): `spec/closure.diff.schema.json`
- information-flow labels + declassification receipts (optional lane): `spec/flow.label.schema.json`, `spec/declass.request.schema.json`, `spec/declass.receipt.schema.json`
- deprecation notices (bounded lifecycle for removals): `spec/deprecation.notice.schema.json`
- user environment activation (UserEnv profile switch plans/receipts): `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`
- TEE attestation (optional confidential microVM lane): `spec/tee.attestation.reference.schema.json`, `spec/tee.attestation.evidence.schema.json`, `spec/tee.attestation.receipt.schema.json`
- change sets + receipts: `spec/change.set.schema.json`, `spec/change.receipt.schema.json`
- lint reports: `spec/lint.report.schema.json`
- policy suggestions (learn/audit workflows; reviewable patches): `spec/policy.suggestion.schema.json`
- policy test suites + reports (regression vectors; optional mutation testing): `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`
- chaos experiment plans/receipts (fault injection lane): `spec/chaos.experiment.plan.schema.json`, `spec/chaos.experiment.receipt.schema.json`
- breakglass lane (recovery): `spec/breakglass.grant.schema.json`, `spec/breakglass.receipt.schema.json`, `spec/breakglass.event.schema.json`
- bootchain policy (revocation/allowlists): `spec/bootchain.policy.schema.json`
- disk layout plans + receipts (installer lane): `spec/disk.layout.plan.schema.json`, `spec/disk.layout.receipt.schema.json`
- kernel tunables + sysctl plans/receipts/events (kernel mutation as evidence): `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`, `spec/sysctl.diff.schema.json`
- kernel module policy + load plans/receipts/events (kmods as executable code): `spec/kmod.policy.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`
- hardware inventory receipts (privacy-safe hardware facts): `spec/hw.inventory.receipt.schema.json`
- hardware compatibility reports (preflight gates before switching generations): `spec/hw.compat.report.schema.json`
- causality graphs (evidence index): `spec/causality.graph.schema.json`
- lease authority evidence (issue/use/snapshot/revoke): `spec/lease.issue.receipt.schema.json`, `spec/lease.use.receipt.schema.json`, `spec/lease.snapshot.schema.json`, `spec/lease.revoke.event.schema.json`
- export + consent + transport lanes: `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/consent.request.schema.json`, `spec/transport.policy.schema.json`
- transparency proof + entries: `spec/transparency.proof.schema.json`, `spec/export.transparency.entry.schema.json`, `spec/release.transparency.entry.schema.json`
- release capsules + authority: `spec/release.capsule.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`
- staged rollout + cohorts: `spec/rollout.policy.schema.json`, `spec/rollout.receipt.schema.json`
- rollout graphs + explicit assignments (multi-hop paths / barriers / traversal evidence): `spec/rollout.graph.schema.json`, `spec/rollout.assignment.schema.json`, `spec/rollout.traversal.receipt.schema.json`
- transparency monitoring: `spec/transparency.monitor.policy.schema.json`, `spec/transparency.monitor.alert.event.schema.json`
- content import + origin labels: `spec/content.origin.schema.json`, `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`
- network egress policy (egress classes): `spec/net.egress.policy.schema.json`
- DNS query receipts (optional, brokered DNS evidence): `spec/net.dns.query.receipt.schema.json`
- PKI trust bundles + issuance receipts: `spec/pki.trust.bundle.schema.json`, `spec/pki.issue.plan.schema.json`, `spec/pki.issue.receipt.schema.json`
- crypto operation requests + receipts (split keys lane): `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`
- operator session envelopes (JIT access lane): `spec/operator.session.schema.json`
- network listen policy (listen classes): `spec/net.listen.policy.schema.json`
- network topology plans/receipts/events (host substrate: links/routes/pf): `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- devfs view plans/receipts/events (compiled `/dev` exposure for jails): `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`
- workload identity leases + issuance receipts (mTLS lane): `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`
- exec integrity policy + receipts (verified execution lane): `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`
- publisher identity receipts (keyless signing lane): `spec/publisher.identity.receipt.schema.json`
- sigstore bundles (offline verification material for keyless lane): `spec/sigstore.bundle.schema.json`
- SBOM statement wrappers (indexable SBOM evidence pointers): `spec/sbom.statement.schema.json`
- VEX statement wrappers (indexable exploitability evidence pointers): `spec/vex.statement.schema.json`
- vulnerability snapshots + query/gate receipts (optional policy lane): `spec/vuln.db.snapshot.schema.json`, `spec/vuln.query.receipt.schema.json`, `spec/vuln.gate.policy.schema.json`, `spec/vuln.gate.receipt.schema.json`

- backup plans + receipts (state replication lane): `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`
- restore drill receipts (continuous recovery testing): `spec/restore.drill.receipt.schema.json`

- firmware inventory + updates (capsule/live/BMC lanes): `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`
- UEFI variable set plans + receipts (boot/capsule/secureboot mutation): `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`

## Archive hygiene

See: `docs/98-archive-hygiene.md`

Last updated: 2026-03-04r185