# DeriveBSD Design Archive

Latest narrow contract decisions: `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md` keeps relay-side temporary-sharing locator values coherent by requiring URI-shaped values only for `uri-hint` and keeping `portal-object` / `object-path` / `opaque` values non-URI-shaped, `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md` keeps relay-side temporary-sharing locators coherent by binding `relay.remote_locator.kind` back to access model (`uri-hint` stays `relay-url`, `portal-object` / `opaque` stays `peer-relay`, `object-path` / `opaque` stays `reverse-forward`), `docs/575-publish-session-endpoint-hints-follow-access-model.md` keeps temporary-sharing endpoint hints coherent by requiring `hostname + port` for `relay-url` and `reverse-forward` shares while keeping `peer-relay` free of URL/host endpoint hints, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md` keeps `support-peer` temporary sharing subordinate to an exact `support.session` support-session authority join instead of support-flavored URL folklore, `docs/568-publish-session-secret-consumption-semantics-boundary.md` keeps secret-gated temporary sharing honest about whether a handoff is `single-successful-admission` or `reusable-until-expiry`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md` keeps secret-gated temporary sharing actually temporary by forcing the separate secret handoff to stay `session-authority-bounded` and expire no later than the publish-session authority, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md` keeps secret-gated temporary shares redacted by forcing usable secrets onto the existing `secret.receipt` lane instead of embedding them in bearer URLs or evidence objects, `docs/565-publish-session-session-scoped-locator-posture-boundary.md` keeps public/org/support relay locators session-scoped so reserved relay domains or remembered public hostnames cannot become a backdoor durable-ingress surface, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md` keeps relay-backed temporary sharing reboot-cleared and `new-session-with-fresh-authority` instead of silently restart-persistent, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md` keeps relay-backed temporary sharing audience-bound by default so `public-link` is always explicit instead of silently public-by-default, `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md` keeps temporary sharing distinct from durable ingress, and `docs/536-workstation-display-composition-and-gpu-boundary.md` makes the workstation graphics boundary explicit, `docs/537-workstation-remoted-session-surface-boundary.md` keeps the baseline GUI crossing session-surface-first, `docs/538-workstation-cross-domain-datatransfer-floor.md` now fixes cross-domain clipboard/file movement as an explicit brokered lane with **no ambient shared clipboard** and **single-delivery by default**, `docs/539-workstation-intent-routed-uri-opening-floor.md` now keeps URI opening compartment-preserving by routing `http` / `https` into a designated browsing compartment, routing `mailto` into a designated communications compartment, and keeping `file://` out of the cross-domain URI lane, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` now keeps chooser/default-app UX on trusted host-managed role slots instead of arbitrary "open with…" discovery or first-open default rewrites, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` now keeps the remembered defaults in typed `intent.role.binding` state that routing receipts can digest-bind back to, `docs/542-role-binding-diff-as-review-surface.md` now makes remembered role/default changes reviewable through `intent.role.binding.diff` instead of desktop-registry or settings-blob folklore, `docs/543-role-binding-event-as-durable-mutation-evidence.md` now makes those trusted changes land in a typed `intent.role.binding.event` trail for event journals and support bundles, and `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md` now keeps interactive workstation role/default changes on the generic consent substrate with a joined `consent.receipt` instead of unreceipted trusted-settings writes, and `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` now keeps non-interactive reconcile/import changes on the existing `policy.decision` lane instead of inheriting workstation prompts or admin folklore, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md` now makes admin tools compile through that same authority vocabulary instead of growing a separate `admin-cli` trigger, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md` now turns the non-interactive lane into an exact-mutation `policy.decision` profile instead of a vague class of allowed writes, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` now keeps those same non-interactive policy decisions short-lived single-apply through `must_apply_before` plus `max_successful_events = 1` instead of reusable standing permission, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` now requires `decision_instance_id` on the joined policy profile so separately issued authorizations for the same exact tuple do not collapse to the same digest, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` now keeps remembered-role policy denial evidence typed as `policy-expired` or `policy-consumed` instead of flattening expired or already-spent authorizations into generic `policy-denied`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` now fixes the denial ladder so non-interactive policy-window validity wins before compare-and-swap and `policy-consumed` stays primary even after later expiry, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` now makes that spent-authority denial actionable by requiring `consumed_by_event_id` to point at the earlier successful consuming event, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` now makes retry recovery deterministic by allowing **already-applied** only when that consuming success matches the same exact mutation tuple, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` now makes that derived retry/export answer stable and queryable through `recovery_interpretation` instead of leaving support bundles and clients to recompute it from raw joins, `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` now makes the winning retry proof portable by requiring `consumed_by_event_digest` next to `consumed_by_event_id`, so detached exports can verify the exact consuming event bytes that justified `already-applied`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` now makes the winning result directly queryable by requiring `consumed_binding_digest` next to those fields, so retry/support/export surfaces can read the earlier winner's resulting binding digest without reopening the event body, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now makes the winning reviewed change directly queryable by also requiring `consumed_diff_digest`, so those same surfaces can name the earlier winner's applied `intent.role.binding.diff` digest without reopening the event body, and `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` now makes the winning old side of that same update edge directly queryable by carrying `consumed_previous_binding_digest` for updated winners, so support/retry/export surfaces can read the earlier winner's replaced binding digest without reopening the event body, and `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` now makes the winner shape itself directly queryable by carrying `consuming_event_action`, so those same surfaces can tell whether the earlier success was an `initialized` first-write or an `updated` compare-and-swap and can interpret the presence or absence of `consumed_previous_binding_digest` without reopening the event body, while `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` now makes reviewed role-binding diffs double as mutation preconditions so stale remembered-role writes leave typed `precondition-failed` evidence instead of silently rebasing, and `docs/547-role-binding-support-import-join-via-content-import-receipt.md` now keeps support/import remembered-role mutations joined to typed `content.import.receipt` evidence through `import_receipt_digest` instead of restore-log folklore. Together those cuts turn the workstation story into a smaller, more implementable target without making the trusted host the ambient renderer, registry browser, or data broker for untrusted content. `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md` now also fixes the missing temporary-sharing boundary: B/C share flows compile to relay-backed `net.publish.session` evidence instead of normalizing shadow tunnels or casual public listeners, while A/D keep durable ingress on the stricter brokered service lane. `docs/535-hardware-support-qualification-target-scope-boundary.md` still keeps workstation trusted-UI proof target-scope-bound across release trains and boot-manifest lineages, `docs/534-hardware-support-conditions-and-known-limitations-boundary.md` still keeps non-fully-supported support claims typed instead of caveat prose, and `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md` still keeps stronger packet export bound to the same approved destination tuple across approval, transport, recipient acceptance, and final export.

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
- base sets: `spec/base.set.schema.json`
- closure proofs: `spec/closure.manifest.schema.json`, `spec/closure.proof.schema.json`
- boot attestation (optional lane): `spec/boot.attestation.schema.json`
- canonical boot event log transcript (measured boot replay + verifier explainability): `spec/boot.eventlog.canon.schema.json`
- boot health gate policy (health-gated rollback inputs): `spec/boot.health.gate.policy.schema.json`
- boot manifest (boot-critical closure for secure/measured boot): `spec/boot.manifest.schema.json`
- boot override policy + receipts (typed mutable boot surface): `spec/boot.override.policy.schema.json`, `spec/boot.override.receipt.schema.json`
- platform report (platform provenance evidence object): `spec/platform.report.schema.json`
- attester provisioning receipts (optional, makes enrollment auditable/operable): `spec/attester.provision.receipt.schema.json`
- policy module diffs (review policy-code drift): `spec/policy.module.diff.schema.json`
- attestation admission policy (make “what is gated?” reviewable): `spec/attestation.admission.policy.schema.json`
- product profiles (A–D defaults as a first-class artifact): `spec/examples/product.profiles.json`
- crypto registry + crypto diffs (review crypto drift): `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- crypto key policies (non-exportable keys as policy objects): `spec/crypto.key.policy.schema.json`
- devshell spec: `spec/devshell.spec.schema.json`
- component descriptors (runtime contract source): `spec/derive.unit.schema.json`
- explicit runtime composition artifacts: `spec/stratum.manifest.schema.json`, `spec/stratum.stack.schema.json`, `spec/mount.view.schema.json`
- contract registries + diffs (interface surfaces as derived artifacts): `spec/contract.registry.schema.json`, `spec/contract.diff.schema.json`
- UAPI registries + diffs (kernel surfaces as contracts): `spec/uapi.registry.schema.json`, `spec/uapi.diff.schema.json`
- authority diffs (reviewable authority deltas between generations): `spec/authority.diff.schema.json`
- authority budgets + checks + exceptions (narrow component-runtime least-authority lane): `spec/authority.budget.schema.json`, `spec/authority.budget.check.schema.json`, `spec/authority.exception.schema.json`
- frontend compile receipts (source/compiler provenance; evidence-only): `spec/frontend.compile.receipt.schema.json`
- packet-capture summary (typed summary-first review/export surface for bounded capture): `spec/packet.capture.summary.schema.json`
- packet-capture selector (typed capture-intent surface compiled to backend filters): `spec/packet.capture.selector.schema.json`
- packet-capture session retention budget + local-artifact metadata posture (bounded raw-file lifetime and strict packet-records-only default): `spec/packet.capture.session.schema.json`, `spec/packet.capture.summary.schema.json`
- packet-capture strong-artifact safe-open intake profile (typed import/normalize path for sideband or decryption-bearing captures): `spec/content.import.packet-capture.plan.schema.json`, `spec/content.import.packet-capture.receipt.schema.json`
- packet-capture normalization redaction proof profile (typed deterministic sanitization evidence for stronger imported captures): `spec/redaction.transform.packet-capture.schema.json`, `spec/redaction.receipt.packet-capture.schema.json`
- packet-capture export policy/receipt/transport profiles (summary-first ordinary export + proof-bound, destination-bound stronger approval, transport-bound, digest-stable, recipient-accepted stronger raw-byte export): `spec/packet.capture.export.policy.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/packet.capture.export.consent.request.profile.schema.json`, `spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`
- fuzz receipts + crash cases (target-class and replayable fuzz evidence): `spec/fuzz.receipt.schema.json`, `spec/crash.case.schema.json`
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
- destructive reprovision authority + receipts: `spec/reset.authorization.schema.json`, `spec/reset.receipt.schema.json`
- kernel tunables + sysctl plans/receipts/events (kernel mutation as evidence): `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`, `spec/sysctl.diff.schema.json`
- kernel module policy + load plans/receipts/events (kmods as executable code): `spec/kmod.policy.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`
- hardware inventory receipts (privacy-safe hardware facts): `spec/hw.inventory.receipt.schema.json`
- hardware compatibility reports (preflight gates before switching generations): `spec/hw.compat.report.schema.json`
- hardware support matrices (approved-hardware catalogs for release/reset admission): `spec/hw.support.matrix.schema.json`
- hardware support qualification profiles (typed qualification standards / playlists): `spec/hw.support.qualification.profile.schema.json`
- hardware support qualification receipts (typed qualification proof objects): `spec/hw.support.qualification.receipt.schema.json`
- causality graphs (evidence index): `spec/causality.graph.schema.json`
- lease authority evidence (issue/use/snapshot/revoke): `spec/lease.issue.receipt.schema.json`, `spec/lease.use.receipt.schema.json`, `spec/lease.snapshot.schema.json`, `spec/lease.revoke.event.schema.json`
- export + consent + transport lanes: `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/consent.request.schema.json`, `spec/transport.policy.schema.json`
- incident support handoff artifacts: `spec/incident.bundle.schema.json`, `spec/incident.timeline.schema.json`, `spec/bundle.plan.schema.json`, `spec/bundle.payload.manifest.schema.json`, `spec/bundle.build.receipt.schema.json`
- transparency proof + entries: `spec/transparency.proof.schema.json`, `spec/export.transparency.entry.schema.json`, `spec/release.transparency.entry.schema.json`, `spec/log.checkpoint.receipt.schema.json`, `spec/transparency.monitor.snapshot.schema.json`
- release capsules + authority: `spec/release.capsule.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`
- staged rollout + cohorts: `spec/rollout.policy.schema.json`, `spec/rollout.receipt.schema.json`
- rollout graphs + explicit assignments (multi-hop paths / barriers / traversal evidence): `spec/rollout.graph.schema.json`, `spec/rollout.assignment.schema.json`, `spec/rollout.traversal.receipt.schema.json`
- transparency monitoring: `spec/transparency.monitor.policy.schema.json`, `spec/transparency.monitor.alert.event.schema.json`
- tree-mount projection plans + receipts (verified lazy mount posture without transport folklore): `spec/tree.mount.plan.schema.json`, `spec/tree.mount.receipt.schema.json`
- content import + origin labels: `spec/content.origin.schema.json`, `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json` (now including the execution boundary for safe-open import work)
- typed support-bundle intake specializations: `spec/content.import.support-bundle.plan.schema.json`, `spec/content.import.support-bundle.receipt.schema.json`
- network egress policy (egress classes): `spec/net.egress.policy.schema.json`
- DNS query receipts (optional, brokered DNS evidence): `spec/net.dns.query.receipt.schema.json`
- network flow summaries (bounded learn/audit review surface): `spec/net.flow.summary.schema.json`
- PKI trust bundles + issuance receipts: `spec/pki.trust.bundle.schema.json`, `spec/pki.issue.plan.schema.json`, `spec/pki.issue.receipt.schema.json`
- crypto operation requests + receipts (split keys lane): `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`
- operator session envelopes (JIT access lane): `spec/operator.session.schema.json`
- network listen policy (listen classes): `spec/net.listen.policy.schema.json`
- temporary relay-backed service sharing: `spec/net.publish.session.schema.json`
- network topology plans/receipts/events (host substrate: links/routes/pf): `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- devfs view plans/receipts/events (compiled `/dev` exposure for jails): `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`
- workload identity leases + issuance receipts (mTLS lane): `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`
- exec integrity policy + receipts (verified execution lane): `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/exec.verify.policy.diff.schema.json`
- publisher identity receipts (keyless signing lane; supplemental identity evidence, not publish authority): `spec/publisher.identity.receipt.schema.json`
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

- Recent packet-capture strong-artifact boundary: `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`
- Recent packet-capture normalization proof boundary: `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`
- Recent packet-capture export proof boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- Recent runtime-authoring boundary: `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md`
- Recent product-profile vocabulary boundary: `docs/501-product-profile-default-vocabulary-boundary.md`

- Recent support-bundle intake typed shapes: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`
- Recent telemetry/profile-vocabulary entropy cut: `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`

- Recent network learn/audit convergence contract: `docs/505-network-learn-audit-convergence-contract.md`
- Stronger packet-capture raw-byte export now also requires explicit non-`auto` approval evidence on the generic consent lane (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`).
- Stronger packet-capture raw-byte export must also stay digest-stable across approval, transport, recipient acceptance, and final export evidence so the same normalized bytes are provably what was approved and sent (`docs/517-packet-capture-strong-export-digest-stability-boundary.md`).
- Final stronger packet-capture raw-byte export now also requires recipient acceptance evidence on the generic transport lane (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`).
- Stronger packet-capture recipient acceptance must now also echo `acceptance.remote_artifact_digest` on the same normalized digest before the stronger handoff counts as canonical (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`).
- Stronger packet-capture closure must now also keep `transport.receipt.result.remote_id`, `acceptance.remote_reference`, and `export.receipt.adapter.remote_id` on the same remote object id before the stronger handoff counts as canonical (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`).
- Stronger packet-capture closure must now also keep `transport.receipt.result.remote_validator`, `acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` on the same remote validator before the stronger handoff counts as canonical (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`).
- Stronger packet-capture closure must now also keep `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` on the same remote protection posture before the stronger handoff counts as canonical (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`).
- Stronger packet-capture closure must now also keep `transport.receipt.result.remote_locator`, `acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` on the same remote locator before the stronger handoff counts as canonical (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`).
- Later stronger packet-capture evidence re-check must now also use typed `transport.reverification.receipt` evidence with `reverification.body_downloaded = false`, keeping the same accepted remote validator / protection posture / locator instead of re-downloading packet bytes or trusting portal screenshots (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`).

Last updated: 2026-03-19r307
See also `docs/570-publish-session-access-model-posture-boundary.md` for the initial temporary-sharing access-model split, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md` for the private tailnet lane, and `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md` for the ordinary human-share lane; public callback/demo publication stays `relay-url` shaped, `organization-users` / `named-recipients` stay `relay-url` shaped, support-peer sharing stays `peer-relay` shaped, and private tailnet sharing stays `reverse-forward` shaped. See also `docs/573-publish-session-audience-bound-shares-require-binding-hints.md` for the exact audience-binding hint floor; audience-bound receipts now also name `identity_provider_hint` / `recipient_hint` where needed. `public-webhook` shares must now also name `audience.validation_hint`; see `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`. `docs/575-publish-session-endpoint-hints-follow-access-model.md` now fixes the remaining endpoint grammar: `relay-url` and `reverse-forward` shares carry `hostname + port`, while `peer-relay` shares keep URL/host endpoint hints absent. `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md` then keeps the relay-side locator grammar aligned too: `relay.remote_locator.kind = uri-hint` stays in the `relay-url` lane, `peer-relay` stays `portal-object` / `opaque`, and `reverse-forward` stays `object-path` / `opaque`. `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md` tightens the remaining loophole by making `relay.remote_locator.value` follow locator kind too: URI-shaped only for `uri-hint`, and non-URI-shaped for `portal-object` / `object-path` / `opaque`.
