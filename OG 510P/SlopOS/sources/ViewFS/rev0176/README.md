# Revision 176 host-adapter compatibility and operation-catalog audit spine

Revision 176 expands the checked v0 model into host-filesystem compatibility: adapter mounts, stat projections, inode aliases, xattr parcels, watcher subscriptions, lock tokens, rename plans, tempfile leases, hydration tickets, and external-app handoffs. The fixture corpus now includes 568 specimens, adds `out/host_adapter_trace_report.md`, and raises proof-obligation coverage to 166 obligations.

The central rule is that compatibility artifacts are projections, not authority. A mounted adapter, stat result, inode number, xattr, watcher event, advisory lock, rename plan, staged tempfile, hydration ticket, or open-with handoff may make ViewFS usable by legacy tools. It must not silently become root authority, object identity, policy, read authority, write authority, completion proof, or persistent delegation.

## What Revision 176 adds

- expands the executable ViewFS fixture corpus from 528 to 568 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with ten host-adapter record families and ten checked operations.
- adds `tools/build_host_adapter_trace_report.py` and generated `out/host_adapter_trace_report.md`.
- adds `docs/30-architecture/host-adapter-compatibility-v0.md`, `docs/40-verification/host-adapter-trace-reporting-v0.md`, and `docs/70-shell/host-adapter-stat-watch-handoff-cards.md`.
- adds `rfcs/0164-viewfs-host-adapter-filesystem-compatibility-and-operation-catalog-audit.md`.
- audits/refactors operation growth with `tools/operation_catalog.py`, `tools/check_operation_catalog.py`, `tools/build_operation_catalog_report.py`, and `out/operation_catalog_report.md`.
- adds `docs/40-verification/operation-catalog-audit-v0.md`.
- adds `docs/00-meta/research-synthesis-2026-05-26-pass-cmq.md`, incorporating FUSE, ProjFS, File Provider, stat/inode, inotify, xattr, locking, rename, and placeholder/handoff pressure.

# Revision 175 schema ontology interoperability and record-family audit spine

Revision 175 expands the checked v0 model from personalization/convenience into schema and ontology interoperability: namespace bindings, external references, vocabulary terms, crosswalk mappings, shape constraints, ontology alignments, catalog entries, and interop cards. The fixture corpus now includes 528 specimens, adds `out/interop_trace_report.md`, and raises proof-obligation coverage to 155 obligations.

The central rule is that interoperability artifacts are not authority. Prefixes, contexts, URIs, IRIs, vocabulary terms, crosswalk rows, shape validations, ontology alignments, catalog entries, and interop cards may connect, translate, validate, and explain. They must not silently become object handles, policy, classification authority, exact equivalence proof, disclosure authority, public-release approval, or canonical truth.

## What Revision 175 adds

- expands the executable ViewFS fixture corpus from 496 to 528 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with eight schema/ontology interoperability record families and eight checked operations.
- adds `tools/build_interop_trace_report.py` and generated `out/interop_trace_report.md`.
- adds `docs/30-architecture/schema-ontology-interoperability-v0.md`, `docs/40-verification/interop-trace-reporting-v0.md`, and `docs/70-shell/interop-reference-crosswalk-cards.md`.
- adds `rfcs/0163-viewfs-schema-ontology-reference-crosswalk-and-record-family-audit.md`.
- audits/refactors record-family growth with `tools/check_record_family_catalog.py`, `tools/build_record_family_report.py`, `out/record_family_report.md`, and `docs/40-verification/record-family-catalog-audit-v0.md`.
- adds `docs/00-meta/research-synthesis-2026-05-26-pass-cmp.md`, incorporating RDF, JSON-LD, URI, SHACL, OWL/SKOS, DCAT, and PROV pressure.

# Revision 174 personalization convenience and lint-manifest audit spine

Revision 174 expands the checked v0 model from workflow/automation into personalization and convenience custody: user profiles, preference sets, personalization models, recommendation sets, shortcut bindings, autofill proposals, experiment assignments, feedback signals, and personalization cards. The fixture corpus now includes 496 specimens, adds `out/personalization_trace_report.md`, and raises proof-obligation coverage to 146 obligations.

The central rule is that personalization artifacts are not authority. Profile rows, preferences, recommender scores, suggestions, shortcuts, autofill proposals, cohort assignments, feedback signals, and personalization cards may narrow, explain, or prepare work. They must not silently become identity proof, consent, policy, training permission, write authority, object authority, or deterministic user truth.

## What Revision 174 adds

- expands the executable ViewFS fixture corpus from 460 to 496 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with nine personalization/convenience record families and nine checked operations.
- adds `tools/build_personalization_trace_report.py` and generated `out/personalization_trace_report.md`.
- adds `docs/30-architecture/personalization-preferences-recommendation-v0.md`, `docs/30-architecture/shortcut-autofill-feedback-experiment-v0.md`, `docs/40-verification/personalization-trace-reporting-v0.md`, and `docs/70-shell/personalization-preference-shortcut-cards.md`.
- adds `rfcs/0162-viewfs-personalization-recommendation-shortcut-and-lint-manifest-audit.md`.
- audits/refactors top-level lint with `tools/lint_manifest.py`, `tools/check_lint_manifest.py`, and `docs/40-verification/lint-manifest-refactor-v0.md`.
- adds `docs/00-meta/research-synthesis-2026-05-26-pass-cmo.md`, incorporating privacy preference, permissions, recommender, feature-flag, and privacy-engineering pressure.

# Revision 173 workflow automation custody and trace-report registry audit spine

Revision 173 expands the checked v0 model from governance/change-management into workflow and automation custody: event envelopes, trigger rules, schedule windows, workflow runs, step invocations, idempotency keys, retry policies, compensation plans, human tasks, and workflow cards. The fixture corpus now includes 460 specimens, adds `out/automation_trace_report.md`, and raises proof-obligation coverage to 136 obligations.

The central rule is that automation artifacts are not authority. Event delivery, trigger matches, cron/schedule eligibility, queued run state, step rows, idempotency keys, retry policies, compensation recipes, human-task rows, and workflow cards may prepare, explain, narrow, or guard work. They must not silently become object authority, approval, target authority, replay authority, or proof of completion.

## What Revision 173 adds

- expands the executable ViewFS fixture corpus from 420 to 460 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with ten workflow/automation record families and ten checked operations.
- adds `tools/build_automation_trace_report.py` and generated `out/automation_trace_report.md`.
- adds `docs/30-architecture/workflow-automation-custody-v0.md`, `docs/30-architecture/workflow-idempotency-compensation-human-tasks-v0.md`, `docs/40-verification/automation-trace-reporting-v0.md`, and `docs/70-shell/workflow-automation-cards.md`.
- adds `rfcs/0161-viewfs-workflow-automation-custody-and-trace-report-registry-audit.md`.
- audits/refactors trace-report generation with `tools/report_registry.py`, `tools/build_all_trace_reports.py`, and `tools/check_report_registry.py`, so lint uses a registry rather than a hard-coded report-builder list.
- adds `docs/40-verification/trace-report-registry-refactor-v0.md`.
- adds `docs/00-meta/research-synthesis-2026-05-25-pass-cmn.md`, incorporating CloudEvents, Temporal, OpenFeature, HTTP idempotency-key, and ActivityPub pressure.

# Revision 171 incident/forensic response and operation-balance audit spine

Revision 171 expands the checked v0 model from query/evaluation surfaces into incident response: alert signals, incident cases, triage verdicts, forensic snapshots, evidence chains, containment plans, remediation plans, recovery rollbacks, and postmortem records. The fixture corpus now includes 384 specimens, adds `out/incident_response_trace_report.md`, and makes every checked operation carry both positive and negative evidence.

The central rule is that incident-response artifacts are evidence and workflow state, not authority. Alerts, case status, triage verdicts, forensic snapshots, evidence chains, containment plans, remediation plans, rollback plans, receipts, and postmortem cards may guide response. They must not silently become object authority, disclosure authority, remediation authority, closure proof, or a guarantee that recurrence is impossible.

## What Revision 171 adds

- expands the executable ViewFS fixture corpus from 344 to 384 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with `AlertSignal`, `IncidentCase`, `TriageVerdict`, `ForensicSnapshot`, `EvidenceChain`, `ContainmentPlan`, `RemediationPlan`, `RecoveryRollback`, and `PostmortemRecord` record families plus nine checked operations.
- adds four positive balance fixtures for pre-existing denial-only operations: `read_handle`, `semantic_open`, `retain_source_via_index`, and `reacquire_from_restore_token`.
- adds `tools/build_incident_response_trace_report.py` and generated `out/incident_response_trace_report.md`.
- adds `tools/fixture_schema.py` and refactors fixture schema metadata out of the large fixture checker.
- adds `tools/check_fixture_operation_balance.py`, requiring each checked operation to have at least one positive and one negative fixture.
- adds `docs/30-architecture/incident-forensic-remediation-v0.md`, `docs/40-verification/incident-response-trace-reporting-v0.md`, `docs/40-verification/fixture-schema-and-operation-balance-audit-v0.md`, and `docs/70-shell/incident-forensic-remediation-cards.md`.
- adds `rfcs/0159-viewfs-incident-forensic-remediation-and-operation-balance-audit.md`.
- adds proof obligations `PO-VIEWFS-ALERT-001`, `PO-VIEWFS-INCIDENT-001`, `PO-VIEWFS-TRIAGE-001`, `PO-VIEWFS-FORENSIC-001`, `PO-VIEWFS-EVIDENCECHAIN-001`, `PO-VIEWFS-CONTAINMENT-001`, `PO-VIEWFS-REMEDIATION-001`, `PO-VIEWFS-ROLLBACK-001`, and `PO-VIEWFS-POSTMORTEM-001`.
- adds `docs/00-meta/research-synthesis-2026-05-25-pass-cml.md`, incorporating NIST/CISA/FIRST incident-response pressure and OpenTelemetry trace-context pressure.

# Revision 170 query/evaluation and trace-report refactor spine

Revision 170 expands the checked v0 model from compliance-label/release gates into query, planning, result, aggregation, evaluation, scoring, and model-selection surfaces. The fixture corpus now includes query specs, planner traces, result sets, aggregation views, evaluation sets, benchmark runs, scoring rubrics, model-selection cards, and a generated `out/query_eval_trace_report.md`.

The central rule is that query/eval artifacts are selectors and assessment evidence, not authority. Saved queries, query text, ranked hits, snippets, planner traces, aggregate cells, eval-set labels, benchmark scores, rubrics, leaderboards, and model-selection cards may guide review. They must not silently become object authority, raw disclosure authority, deployment authority, or production-readiness authority.

## What Revision 170 adds

- expands the executable ViewFS fixture corpus from 312 to 344 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with `QuerySpec`, `PlannerTrace`, `ResultSet`, `AggregationView`, `EvaluationSet`, `BenchmarkRun`, `ScoringRubric`, and `ModelSelectionCard` record families plus `admit_query_scope`, `admit_planner_trace`, `open_result_member`, `render_aggregation_view`, `admit_evaluation_set`, `record_benchmark_run`, `apply_scoring_rubric`, and `render_model_selection_card` operations.
- adds `tools/build_query_eval_trace_report.py` and generated `out/query_eval_trace_report.md`.
- adds `docs/30-architecture/query-planning-result-evaluation-v0.md`, `docs/40-verification/query-eval-trace-reporting-v0.md`, and `docs/70-shell/query-eval-cards-and-benchmark-dashboards.md`.
- adds `rfcs/0158-viewfs-query-planning-result-evaluation-and-trace-report-refactor.md`.
- adds proof obligations `PO-VIEWFS-QUERY-001`, `PO-VIEWFS-PLANNER-001`, `PO-VIEWFS-RESULTSET-001`, `PO-VIEWFS-AGGREGATION-001`, `PO-VIEWFS-EVALSET-001`, `PO-VIEWFS-BENCHMARK-001`, `PO-VIEWFS-SCORING-001`, and `PO-VIEWFS-MODELCARD-001`.
- audits/refactors the trace reporting layer with `tools/trace_report_common.py` and `docs/40-verification/trace-report-helper-refactor-v0.md`.
- replaces the fixture-checker operation chain with an `EVALUATORS` dispatch table.
- adds `docs/00-meta/research-synthesis-2026-05-25-pass-cmk.md`, incorporating SPARQL query scope pressure, NIST/OWASP AI risk and evaluation pressure, HELM/MLCommons benchmark transparency pressure, and W3C PROV trace discipline.

# Revision 169 executable compliance-label and release-gate spine

Revision 169 expands the checked v0 model from transform/lineage interpretation into classification, licensing, jurisdiction, purpose, public-release, and compliance-card surfaces. The fixture corpus now includes classification marks, license terms, jurisdiction fences, compliance obligations, public-release reviews, purpose bindings, compliance cards, and a generated `out/compliance_trace_report.md`.

The central rule is that compliance metadata is not authority. Labels such as `confidential`, `public`, `safe`, `export-controlled`, SPDX/license identifiers, permissions, obligations, purpose statements, region badges, release receipts, and shell compliance cards may constrain or explain effects. They must not silently become read, disclose, export, publish, training, processing, or public-release authority.

## What Revision 169 adds

- expands the executable ViewFS fixture corpus from 281 to 312 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with `ClassificationMark`, `LicenseTerm`, `JurisdictionFence`, `ComplianceObligation`, `PublicReleaseReview`, `PurposeBinding`, and `ComplianceCard` record families plus `evaluate_classification_mark`, `authorize_license_use`, `check_jurisdiction_fence`, `enforce_compliance_obligation`, `approve_public_release`, `bind_purpose_use`, and `render_compliance_card` operations.
- adds `tools/build_compliance_trace_report.py` and generated `out/compliance_trace_report.md`, giving reviewers a compact map of compliance-label fixtures.
- adds `docs/30-architecture/classification-license-purpose-v0.md`, `docs/30-architecture/jurisdiction-public-release-compliance-v0.md`, `docs/40-verification/compliance-trace-reporting-v0.md`, and `docs/70-shell/classification-license-jurisdiction-and-release-cards.md`.
- adds `rfcs/0157-viewfs-classification-license-jurisdiction-purpose-and-release-gates.md`.
- adds proof obligations `PO-VIEWFS-CLASSIFICATION-001`, `PO-VIEWFS-LICENSE-001`, `PO-VIEWFS-JURISDICTION-001`, `PO-VIEWFS-OBLIGATION-001`, `PO-VIEWFS-PUBLICRELEASE-001`, `PO-VIEWFS-PURPOSE-001`, and `PO-VIEWFS-COMPLIANCECARD-001`.
- adds `docs/00-meta/research-synthesis-2026-05-25-pass-cmj.md`, incorporating FIPS 199 categorization, SPDX license metadata, ODRL permissions/prohibitions/obligations, Creative Commons rights expressions, export-control classification pressure, and privacy-purpose management pressure.

# Revision 168 executable transform and lineage spine

Revision 168 expands the checked v0 model from host/runtime/device boundaries into interpretation and derived-artifact surfaces. The fixture corpus now includes transform plans, codec profiles, schema migrations, patch sets, annotation layers, lineage links, preview artifacts, canonicalization profiles, and a generated `out/transform_lineage_trace_report.md`.

The central rule is that transform recipes, decoded renderings, migrated payloads, patches, annotations, lineage/provenance chains, preview caches, OCR-like text, normalized strings, and canonicalized digests are authority-adjacent evidence or new derived objects. They must not silently inherit source authority, bypass redaction, or present transformed/canonical equality as original-byte identity.

## What Revision 168 adds

- expands the executable ViewFS fixture corpus from 251 to 281 specimens.
- extends `tools/check_viewfs_core_fixtures.py` with `TransformPlan`, `CodecProfile`, `SchemaMigration`, `PatchSet`, `AnnotationLayer`, `LineageLink`, `PreviewArtifact`, and `CanonicalizationProfile` record families plus `apply_transform_plan`, `decode_codec_payload`, `apply_schema_migration`, `apply_patch_set`, `attach_annotation_layer`, `verify_lineage_link`, `render_preview_artifact`, and `admit_canonicalization_claim` operations.
- adds `tools/build_transform_lineage_trace_report.py` and generated `out/transform_lineage_trace_report.md`, giving reviewers a compact map of transform/lineage fixtures.
- adds `docs/30-architecture/transform-codec-migration-lineage-v0.md`, `docs/30-architecture/annotation-preview-canonicalization-v0.md`, `docs/40-verification/transform-lineage-trace-reporting-v0.md`, and `docs/70-shell/transform-lineage-preview-and-annotation-cards.md`.
- adds `rfcs/0156-viewfs-transform-codec-migration-annotation-lineage-and-preview-gates.md`.
- adds proof obligations `PO-VIEWFS-TRANSFORM-001`, `PO-VIEWFS-CODEC-001`, `PO-VIEWFS-SCHEMAMIGRATION-001`, `PO-VIEWFS-PATCH-001`, `PO-VIEWFS-ANNOTATION-001`, `PO-VIEWFS-LINEAGE-001`, `PO-VIEWFS-PREVIEW-001`, and `PO-VIEWFS-CANONICALIZATION-001`.
- adds `docs/00-meta/research-synthesis-2026-05-25-pass-cmi.md`, incorporating W3C PROV, Web Annotation, JSON Schema dialect/validation, and Unicode security/confusable pressure.

## Revision 167 executable boundary-reality spine

Revision 167 expands the checked v0 core from identity/secret custody into host/runtime, device, network, clipboard, drag/drop, peripheral, and sensor boundary discipline. The corpus now includes 251 fixtures and adds runtime postures, device attestations, network connectors, clipboard parcels, drag/drop parcels, peripheral grants, sensor observations, and a generated `out/boundary_reality_trace_report.md`.

The central rule is that boundary facts are not authority. A local runtime, locked-host badge, admitted connector, fresh DNS proof, clipboard parcel, drag/drop gesture, device descriptor, peripheral grant, sensor sample, or old receipt may explain eligibility, but the effect still needs current live authority, exact scope, trusted path where relevant, redaction/classification posture, freshness, sandbox fit, and policy admission.

## Revision 165 executable resource / side-effect spine

Revision 165 expands the checked v0 core from package/tool-boundary evidence into resource and side-effect discipline. The corpus now includes 198 fixtures and adds resource budgets, spend reservations, rate limiters, background jobs, cache entries, capacity signals, metering receipts, and a generated `out/resource_trace_report.md`.

The central rule is that resource state is a brake and explainer, not authority. A quota card, budget row, reservation, rate token, queue job, cache hit, capacity signal, or metering receipt may bound or explain work, but the effect still needs a typed plan, approval cut, current lease/freshness where relevant, and a live handle with the requested right.

## Revision 164 executable supply-chain / plugin-tool boundary spine

Revision 164 expands the checked v0 core from deletion/restore lifecycle into package and extension-tool boundaries. The corpus now includes 172 fixtures and adds package envelopes, dependency pins, provenance attestations, transparency entries, verifier roots, extension manifests, tool schemas, tool bindings, install plans, sandbox profiles, and a generated `out/supply_chain_trace_report.md`.

The central rule is that supply-chain evidence and plugin metadata are authority-adjacent, not authority. A package name, SBOM, dependency range, exact pin, provenance statement, transparency inclusion, verifier-root claim, extension manifest, tool schema, installed-tool badge, sandbox label, or old receipt may support review, but install/bind/invoke still requires a typed plan, approval cut, sandbox fit, and current live authority.

# Revision 162 executable collaboration and namespace-composition spine

Revision 162 expands the checked v0 model from disclosure/observation into collaboration and namespace composition. The fixture corpus now includes shared rooms, mount edges, group-membership gates, label overlays, handoff packets, and collaboration-card honesty checks. `make lint` regenerates `out/conformance_report.md`, `out/policy_trace_report.md`, `out/freshness_trace_report.md`, `out/disclosure_trace_report.md`, and `out/collaboration_trace_report.md`.

The central rule is that room membership, group labels, mounted-view projections, collaborator badges, label overlays, handoff receipts, and collaboration cards are authority-adjacent evidence until a checked lane binds them to exact scope, current membership epoch, approved propagation or acceptance cuts, narrowed delegation, honest rights rendering, and current live authority.

## What Revision 162 adds
- expands the executable ViewFS fixture corpus from 98 to 121 specimens, adding shared-room, mount-edge, group-membership, label-overlay, handoff, and collaboration-card pressure.
- extends `tools/check_viewfs_core_fixtures.py` with `SharedRoom`, `MountEdge`, `GroupMembership`, `LabelOverlay`, `HandoffPacket`, and `CollaborationCard` record families plus `compose_shared_view`, `group_bound_authority`, `resolve_label_overlay`, `handoff_packet`, and `render_collaboration_card` operations.
- adds `tools/build_collaboration_trace_report.py` and generated `out/collaboration_trace_report.md`, giving reviewers a compact map of collaboration/namespace fixtures.
- adds `docs/30-architecture/shared-rooms-mount-edges-and-group-gates-v0.md`, `docs/30-architecture/label-overlays-handoff-packets-and-collaboration-cards-v0.md`, `docs/40-verification/collaboration-trace-reporting-v0.md`, and `docs/70-shell/collaboration-room-mount-label-and-handoff-cards.md`.
- adds `rfcs/0150-viewfs-shared-rooms-mount-edges-group-labels-and-handoff-gates.md`.
- adds proof obligations `PO-VIEWFS-SHAREDROOM-001`, `PO-VIEWFS-MOUNTEDGE-001`, `PO-VIEWFS-GROUP-001`, `PO-VIEWFS-LABEL-001`, `PO-VIEWFS-HANDOFF-001`, and `PO-VIEWFS-COLLAB-001`.
- adds `docs/00-meta/research-synthesis-2026-05-22-pass-cmc.md`, incorporating RBAC, room-state, ACL, mount-propagation, Ward, and Foundry pressure.

## What Revision 159 adds
- expands the executable ViewFS fixture corpus from 40 to 54 specimens, adding policy-decision, witness-bundle, replay-scenario, and breakglass/override pressure.
- extends `tools/check_viewfs_core_fixtures.py` with `PolicyBundle`, `PolicyDecision`, `WitnessBundle`, `ScenarioReplay`, and `OverrideWarrant` record families plus `policy_decision`, `witness_bundle_verify`, `scenario_replay`, and `override_grant` operations.
- adds `tools/build_policy_trace_report.py` and generated `out/policy_trace_report.md`, giving reviewers a compact map of policy bundles, decisions, witnesses, scenarios, and override warrants involved in the new fixtures.
- adds `docs/30-architecture/policy-decision-witness-bundles-v0.md`, `docs/30-architecture/replay-scenarios-and-breakglass-v0.md`, `docs/40-verification/policy-trace-reporting-v0.md`, and `docs/70-shell/why-allowed-panels-policy-witness-cards.md`.
- adds `rfcs/0147-viewfs-policy-witness-bundles-replay-scenarios-and-breakglass-gates.md`.
- adds proof obligations `PO-VIEWFS-POLICY-001`, `PO-VIEWFS-WITNESS-001`, `PO-VIEWFS-REPLAY-001`, and `PO-VIEWFS-OVERRIDE-001`.
- adds `docs/00-meta/research-synthesis-2026-05-22-pass-clz.md`, incorporating policy-decision logs, principal/action/resource/context authorization models, attestation/witness subject binding, trace/report generation, and Ward-style stewardship pressure.
- refreshes assurance registries, context pack, conformance report, policy trace report, and release manifest for `ViewFS-rev0159-2026.05.22.16.08-policywitnesses-replayscenarios-breakglassgates-jadelantern.zip`.

## Revision 160 executable distributed-state spine

Revision 160 expands the checked v0 model from policy/witness traces into freshness and distributed-state traces. The fixture corpus now includes lease renewal, offline branch publish/revalidation, merge reconciliation, remote attestation verification, freshness fences, and journal checkpoint finalization. `make lint` regenerates `out/conformance_report.md`, `out/policy_trace_report.md`, and `out/freshness_trace_report.md`.

The central rule is that leases, timestamps, remote heads, local commits, merge receipts, attestations, and checkpoint records are explanatory or freshness evidence until a checked lane binds them to current live authority.


## What Revision 158 adds
- expands the executable ViewFS fixture corpus from 30 to 40 specimens, adding quarantine, trust-transition, authority-diff, export-plan, and receipt-replay pressure.
- extends `tools/check_viewfs_core_fixtures.py` with `OriginEvidence`, `QuarantineCapsule`, `TrustTransition`, `AuthorityDiff`, and `ExportPlan` record families plus `quarantine_open`, `trust_transition_release`, `render_authority_diff`, and `export_plan` operations.
- adds `tools/build_conformance_report.py` and generated `out/conformance_report.md`; `make lint` now regenerates the report so fixture/proof coverage is reviewable as a single markdown artifact.
- adds `docs/30-architecture/quarantine-trust-transition-v0.md`, `docs/30-architecture/authority-diff-and-export-plan-v0.md`, `docs/40-verification/conformance-reporting-v0.md`, and `docs/70-shell/authority-diff-cards-and-conformance-dashboards.md`.
- adds `rfcs/0146-viewfs-quarantine-authority-diff-export-and-conformance-reporting.md`.
- adds proof obligations `PO-VIEWFS-QUARANTINE-001`, `PO-VIEWFS-AUTHDIFF-001`, `PO-VIEWFS-EXPORT-001`, and `PO-VIEWFS-CONFORMANCE-001`.
- adds `docs/00-meta/research-synthesis-2026-05-21-pass-cly.md`, incorporating TUF freshness/rollback pressure, SLSA provenance separation, Sigstore/Rekor transparency-history pressure, OCI sidecar/referrer pressure, WASI descriptor access, and OpenTelemetry generated-report posture.
- refreshes assurance registries, evidence hooks, context pack, conformance report, and release manifest for `ViewFS-rev0158-2026.05.21.14.09-quarantineauthdiff-exportplans-conformancereports-jadebastion.zip`.

## What Revision 157 adds
- expands the executable ViewFS fixture corpus from 20 to 30 specimens, adding adversarial path resolver checks, delegation-chain checks, shell-card honesty checks, and derived-artifact cleanup checks.
- extends `tools/check_viewfs_core_fixtures.py` with `PathNode`, `Delegation`, `ShellCard`, and `CopyInventory` record families plus `delegate_handle`, `render_shell_card`, and `forget_source` operations.
- strengthens `compat_pathwalk` so symlink, magic/synthetic, and mount/provider crossings are distinct checked denial reasons rather than generic path failures.
- adds `docs/30-architecture/resolver-conformance-v0.md`, `docs/30-architecture/delegation-chain-and-shell-card-honesty-v0.md`, and `docs/30-architecture/derived-artifact-cleanup-ledger-v0.md`.
- adds `rfcs/0145-viewfs-resolver-delegation-shell-and-derived-cleanup-fixture-hardening.md`.
- adds proof obligations `PO-VIEWFS-PATHWALK-001`, `PO-VIEWFS-DELEGATION-001`, `PO-VIEWFS-SHELL-001`, and `PO-VIEWFS-DERIVED-001`, all covered by fixtures.
- adds `docs/00-meta/research-synthesis-2026-05-21-pass-clx.md`, incorporating openat2 resolver flags, WASI descriptor-relative paths, File System Access handle/persistence pressure, SLSA provenance analogy, and companion-cube pressure.
- refreshes assurance registries, evidence hooks, context pack, and release manifest for `ViewFS-rev0157-2026.05.21.13.18-resolverdelegation-shellhonesty-copyinventories-jadecairn.zip`.

## What Revision 156 adds
- expands the executable ViewFS spine from 8 to 20 fixtures, covering handle attenuation, mutable commit cuts, stale-base denial, restore-token death verdicts, explicit retention roots, prompt/action-plan toolcall boundaries, portal grant replay, and revoked-handle inertness.
- extends `docs/30-architecture/core-schema-v0.md` with `MutableSession`, `RevocationEvent`, `RetentionRoot`, and `ActionPlan` families plus new checked operations.
- adds `docs/30-architecture/mutable-anchor-commit-cut-v0.md`, `docs/30-architecture/revocation-stale-brakes-and-retention-roots-v0.md`, and `docs/30-architecture/action-plan-toolcall-lane-v0.md`.
- adds `rfcs/0144-viewfs-fixture-coverage-lifecycle-hardening-and-agentic-action-cuts.md`.
- adds `tools/check_proof_fixture_coverage.py`; fixtures now carry `covers` lists and `make lint` fails if proof-obligation coverage drifts.
- updates `docs/40-verification/proof-obligations-v0.md` with mutable, revocation, retention, and fixture-coverage obligations.
- adds `docs/00-meta/research-synthesis-2026-05-21-pass-clw.md`, incorporating ambient-rights, WASI/capability, persistent bookmark/token, MCP/LLM agency, and lifecycle-state pressure.
- refreshes assurance registries, evidence hooks, roadmap, trajectory, companion seam intake, context pack, and release manifest for `ViewFS-rev0156-2026.05.21.12.31-lifecyclefixtures-coveragegates-stalebrakes-opalharbor.zip`.

## What Revision 155 adds
- switches ViewFS from prose-only seam accumulation toward an executable spine: `docs/30-architecture/core-schema-v0.md`, `docs/40-verification/proof-obligations-v0.md`, `fixtures/viewfs-core-v0/`, and `tools/check_viewfs_core_fixtures.py`.
- adds `rfcs/0143-viewfs-executable-core-schema-proof-obligation-and-fixture-spine.md`, requiring each future noun to earn a specimen, negative test, shell representation, assurance hook, and companion-seam note before promotion.
- adds checked fixtures for portal import + view pathwalk success, receipt non-authority, digest non-authority, rooted path escape denial, semantic answer-card non-authority, click-without-approval denial, approval-cut export success, and derived-artifact non-retention.
- adds semantic lint gates: duplicate RFC-number detection (`tools/check_rfc_numbers.py`), duplicate/malformed registry-ID detection (`tools/check_registry_ids.py`), and fixture execution inside `make lint`.
- repairs archive hygiene by renumbering the duplicate semantic-object-core RFC from `0109` to `0142`; see `docs/00-meta/rfc-renumbering-ledger.md`.
- repairs duplicated claim/invariant/assumption IDs in the assurance registries and adds new executable-spine claim/invariant/assumption entries.
- adds `docs/30-architecture/companion-seam-intake.md`, mapping SlopOS, Schell, Harbor, Steward, Ward, Helm, and Foundry pressure into ViewFS without importing their nouns as authority.
- replaces the embedded `slopos/` companion snapshot with uploaded SlopOS `rev0720` so ViewFS is no longer packaged with stale SlopOS `rev0655`.
- regenerates `out/context_pack.md` and `RELEASE-MANIFEST.json` for `ViewFS-rev0155-2026.05.21.11.44-executablespine-proofobligations-fixturecorpus-jadebridge.zip`.

## What Revision 154 adds
- continued external research on trusted-path and human-consent hygiene: EROS user-volition traceability, HTML sticky/transient/consuming user activation, Wayland xdg-activation tokens, Microsoft Secure Attention Sequence, WebAuthn/CTAP user presence versus verification, OWASP clickjacking defenses, and the included SlopOS D-VOLITION / D-POWERBOX posture.
- added `rfcs/0141-viewfs-keep-consent-summaries-presentation-surfaces-gesture-evidence-volition-tokens-approval-cuts-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/consent-summaries-presentation-surfaces-gesture-evidence-volition-tokens-approval-cuts-live-authority-and-receipts.md` and `docs/70-shell/consent-cards-trusted-path-lamps-volition-tokens-clickjacking-shields-and-approval-receipts.md`.
- expanded the SlopOS datacube evaluation with the seam: consent candidate/authority diff versus canonical summary versus presentation surface record versus trusted-path posture versus gesture evidence versus volition token versus approval cut versus execution arm/live authority versus outcome/cleanup versus receipt/history.
- refreshed architecture, design splits, SlopOS seam map, shell idea/protocol notes, bibliography/source-head/review-queue entries, evidence hooks, claim/invariant/assumption registries, roadmap, trajectory map, and lint coverage.
- regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for `ViewFS-rev0154-2026.05.18.20.28-volitioncards-trustedpaths-consentfences-jadegate.zip`.

## What Revision 153 adds
- continued external research on instruction/prompt/agent hygiene: OWASP LLM01 prompt injection, OpenAI prompt-injection guidance, Microsoft and Google indirect-prompt-injection defenses, MCP security/tool/resource/prompt seams, VS Code custom instruction and parent-repository discovery behavior, instruction-hierarchy research, and SlopOS D-LLM/MCP/tool-UI boundary posture.
- added `rfcs/0140-viewfs-keep-instruction-sources-context-frames-proposal-text-action-plans-tool-invocations-approvals-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/instruction-sources-context-frames-proposal-text-action-plans-tool-invocations-approvals-live-authority-and-receipts.md` and `docs/70-shell/instruction-rails-context-shutters-action-plan-cards-toolcall-fuses-and-approval-receipts.md`.
- expanded the SlopOS datacube evaluation with the seam: instruction source record versus trust/priority label versus context frame versus model/prompt profile versus proposal text versus typed action plan versus tool invocation candidate versus approval/adoption cut versus current live authority versus result/observation versus receipt/history.
- refreshed architecture, design-split, SlopOS seam, inspirations, shell idea/protocol notes, bibliography/source-head/review-queue entries, evidence hooks, claim/invariant/assumption registries, roadmap, trajectory map, and lint coverage, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 152 adds
- continued external research on semantic derivation and retrieval-store hygiene: desktop search privacy controls, sandboxed/segmented metadata extraction, vector-store multitenancy/isolation choices, embedding inversion leakage, OWASP vector/embedding risks, and the included SlopOS quarantined content-index / derived-attribute / result-preview boundaries.
- added `rfcs/0139-viewfs-keep-semantic-extraction-intents-derived-artifacts-embedding-stores-query-scopes-result-projections-answer-cards-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/semantic-extraction-intents-derived-artifacts-embedding-stores-query-scopes-result-projections-answer-cards-live-authority-and-receipts.md` and `docs/70-shell/semantic-derivation-cards-embedding-vaults-scope-filters-result-shades-and-answer-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that semantic extraction intents, source input capsules, extractor/model profiles, derived artifacts, index/store membership, query authority scopes, result projections, answer/suggestion cards, current live authority, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, roadmap, trajectory, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 151 adds
- continued external research on content-address / dedup privacy hygiene: Venti/Foundation content-addressed storage, IPFS CIDs, Nix content-addressed store objects, Tahoe-LAFS convergence secrets, client-side dedup proof-of-ownership attacks, DupLESS/message-locked encryption, ZFS dedup resource costs, KSM/memory-dedup side channels, and the included SlopOS fresh-identity / verified-blob / microVM-dedup posture.
- added `rfcs/0138-viewfs-keep-content-addresses-equality-witnesses-dedup-hints-convergence-domains-cache-hits-materializations-live-facets-and-receipts-separate.md`.
- added `docs/30-architecture/content-addresses-equality-witnesses-dedup-hints-convergence-domains-cache-hits-materializations-live-facets-and-receipts.md` and `docs/70-shell/digest-shades-equality-rails-dedup-shutters-convergence-lamps-and-cache-ghosts.md`.
- expanded the SlopOS datacube evaluation with the lesson that content addresses, equality witnesses, dedup eligibility hints, convergence/privacy domains, cache-hit observations, proof-of-possession checks, materialization decisions, current live facets, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, roadmap, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 150 adds
- continued external research on secure-transport identity hygiene: TLS 1.3, service identity verification, channel bindings, certificate transparency, SSH known-host checking, SPIFFE X.509-SVIDs, DANE/TLSA, and the included SlopOS D-NETLEASE certificate/verifier/resumption boundaries.
- added `rfcs/0137-viewfs-keep-transport-identities-verifier-profiles-trust-anchor-inputs-channel-bindings-session-resumption-live-secure-channels-and-receipts-separate.md`.
- added `docs/30-architecture/transport-identities-verifier-profiles-trust-anchor-inputs-transparency-status-evidence-channel-bindings-session-resumption-live-secure-channels-and-receipts.md` and `docs/70-shell/channel-binder-cards-cert-braids-trust-anchor-chips-resumption-shades-and-secure-channel-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that transport intent, reference identity, presented evidence, verifier profile, trust-anchor/pin inputs, verification verdicts, channel bindings, session resumption/0-RTT state, current live secure channels, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 149 adds
- continued external research on service discovery and binding hygiene: DNS-SD/mDNS browse-vs-resolve, Kubernetes Service/EndpointSlice dynamics, xDS discovery/update/TTL behavior, systemd socket-activation fd delivery, SPIFFE workload identity, and the included SlopOS D-NETLEASE/service-binding/name-context pressure.
- added `rfcs/0136-viewfs-keep-service-designators-discovery-snapshots-readiness-claims-binding-cuts-activation-targets-live-service-handles-advertisements-and-receipts-separate.md`.
- added `docs/30-architecture/service-designators-discovery-snapshots-readiness-claims-binding-cuts-activation-targets-live-handles-advertisements-and-receipts.md` and `docs/70-shell/service-cards-discovery-drawers-readiness-lamps-binding-braids-activation-rails-advert-shutters-and-call-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that service intent, designator, catalog/discovery authority, discovery snapshot, readiness evidence, binding cut, activation target, live service handle, advertisement, and receipt must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 148 adds
- continued external research on network capability hygiene: sandboxed no-network defaults, static network entitlements, local-network permission prompts, DNS-over-HTTPS, SVCB/HTTPS service binding, Happy-Eyeballs address racing, private/local-network browser protections, and the included SlopOS D-NETLEASE boundary family.
- added `rfcs/0135-viewfs-keep-network-intents-resolution-witnesses-connection-leases-stream-handles-local-exposures-egress-cuts-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/network-intents-resolution-witnesses-connection-leases-stream-handles-local-exposures-egress-cuts-live-authority-and-receipts.md` and `docs/70-shell/net-lease-cards-resolver-braids-egress-meters-local-exposure-shutters-and-send-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that network intents, destination designators, resolution witnesses, admission/lease descriptors, live dialers/resolvers/listeners/streams, local exposures, egress/import cuts, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 147 adds
- continued external research on process/namespace inspection, procfs/ptrace/dumpability, core/crash capture hygiene, structured diagnostics, trace/probe systems, subresource authorization, platform privacy gates, and the included SlopOS capshell/observation/trace/debug-introspection posture.
- added `rfcs/0134-viewfs-keep-inspection-lenses-namespace-snapshots-fd-peeks-memory-captures-trace-probes-debug-controls-redaction-policy-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/process-inspection-lenses-namespace-snapshots-fd-peeks-memory-captures-trace-probes-debug-controls-redaction-policies-live-authority-and-receipts.md` and `docs/70-shell/inspect-lenses-proc-shades-fd-peek-cards-trace-fuses-dump-guards-and-export-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that inspection intents, target locators, namespace snapshots, handle/fd peeks, memory/core captures, trace probes, debug controls, redaction/export cuts, live inspection authority, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, assumption, and lint hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

# ViewFS datacube

## What Revision 146 adds
- continued external research on capability delegation and revocation hygiene: derivation-tree revocation, membranes/revocable proxies, caveat-bearing delegation, UCAN/OAuth revocation, short-lived credentials, capability-URL leakage, and object-capability RPC reference passing.
- added `rfcs/0133-viewfs-keep-delegation-intents-attenuation-envelopes-membrane-leases-revocation-wavefronts-stale-brakes-live-authority-and-receipts-separate.md`.
- added `docs/30-architecture/delegation-intents-attenuation-envelopes-membrane-leases-revocation-wavefronts-stale-brakes-live-authority-and-receipts.md` and `docs/70-shell/delegation-cards-membrane-lamps-revocation-wavefronts-stale-brakes-and-recall-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that delegation intents, attenuation/caveat envelopes, membrane leases, delegated handles, revocation requests, wavefront checkpoints, stale brakes, renewal/redelegation controls, live authority, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.


## What Revision 145 adds
- continued external research on secret/credential delivery hygiene: activation-time credentials, Kubernetes/Docker secret projection, desktop secret-store prompting, environment-variable leakage, transcript redaction, temporary credential renewal, and SlopOS D-APPSECRET/capshell boundary posture.
- added `rfcs/0132-viewfs-keep-secret-descriptors-acquisition-prompts-delivery-slots-env-shadows-redaction-lenses-renewal-leases-live-use-handles-and-receipts-separate.md`.
- added `docs/30-architecture/secret-descriptors-acquisition-prompts-delivery-slots-environment-shadows-redaction-lenses-renewal-leases-live-use-handles-and-receipts.md` and `docs/70-shell/secret-slot-cards-env-shadow-lamps-redaction-lenses-renewal-rails-and-use-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that secret descriptors, acquisition prompts, delivery slots/projections, environment shadows, redaction lenses, renewal/rotation leases, live-use handles, residue markers, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.


## What Revision 144 adds
- continued external research on SBOM/VEX/provenance/update metadata and the SlopOS datacube's existing supply-chain evidence posture.
- added `rfcs/0131-viewfs-keep-artifact-envelopes-inventory-claims-locator-aliases-vulnerability-statements-admission-verdicts-activation-targets-live-facets-and-receipts-separate.md`.
- added `docs/30-architecture/artifact-envelopes-inventory-claims-locator-aliases-vulnerability-statements-admission-verdicts-activation-targets-live-facets-and-receipts.md` and `docs/70-shell/sbom-drawers-locator-chips-vex-shutters-admission-cuts-and-live-rails.md`.
- expanded the SlopOS datacube evaluation with the lesson that artifact envelopes, inventory/SBOM claims, locator aliases, vulnerability/advisory/VEX statements, verification evidence, local admission verdicts, activation targets, current live facets, and receipts must stay separate.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.




## What Revision 143 adds
- continued external research on archive/container extraction hazards: Zip Slip/path traversal, TAR/ZIP extraction filters, symlink/hardlink escape, device/xattr/permission metadata, layered image layout, and safer extraction defaults.
- added `rfcs/0130-viewfs-keep-container-envelopes-member-claims-extraction-plans-materialization-roots-namespace-commits-live-opens-and-receipts-separate.md`.
- added `docs/30-architecture/container-envelopes-member-claims-extraction-plans-materialization-roots-namespace-commits-live-opens-and-receipts.md` and `docs/70-shell/extract-plan-cards-member-capsules-path-guard-badges-and-unpack-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that archive/container envelopes, member claims, extraction plans, sterile materialization roots, extracted member capsules, namespace commits, live opens, and receipts should stay separate so member names never become namespace authority.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 142 adds
- continued external research on quarantine metadata, Mark-of-the-Web-style origin signals, guarded document opens, isolated safe-open, browser download warnings, portal-mediated document access, and SlopOS D-QUAR anti-laundering posture.
- added `rfcs/0129-viewfs-keep-origin-evidence-quarantine-marks-safe-open-capsules-viewer-residue-derived-artifacts-trust-clearances-live-opens-and-receipts-separate.md`.
- added `docs/30-architecture/origin-evidence-quarantine-marks-safe-open-capsules-viewer-residue-derived-artifacts-trust-clearances-live-opens-and-receipts.md` and `docs/70-shell/quarantine-capsules-safe-open-shutters-residue-lamps-derived-artifact-rails-and-trust-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that origin evidence, quarantine marks, safe-open capsules, viewer residue, derived artifacts, trust clearances, live opens, and receipts should stay separate so portal imports and semantic indexing do not launder risky content.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, review queue, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 141 adds
- continued external research on object-store liveness, GC roots, pins/holds/leases, sweep dry-runs, deletion finalizers, and ash/tombstone receipts for the future SlopOS/ViewFS datacube.
- added `rfcs/0128-viewfs-keep-reachability-roots-live-handle-roots-pin-holds-leases-sweep-candidates-finalizers-collected-ash-live-facets-and-receipts-separate.md`.
- added `docs/30-architecture/reachability-roots-live-handle-roots-pin-holds-leases-sweep-candidates-finalizers-collected-ash-live-facets-and-receipts.md` and `docs/70-shell/gc-halos-pin-badges-sweep-previews-finalizer-rails-and-ash-receipts.md`.
- expanded the SlopOS datacube evaluation with the lesson that durable roots, live handles, pins/holds/leases, sweep candidates, finalizers, collected ash, live facets, and receipts should stay separate while the object store and capability handle model are still in design.
- refreshed architecture, design-split, SlopOS seam, shell, terminal protocol, bibliography/source-head, evidence, claim, invariant, and assumption hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 140 adds
- continued external research on durable roots, persistent capability stores, anti-rollback/currentness witnesses, restore/recovery ceremonies, and design-phase non-decisions for the future SlopOS/ViewFS datacube.
- added `rfcs/0127-viewfs-keep-durable-root-commits-epoch-fences-restore-intents-activation-targets-live-binds-and-receipts-separate.md`.
- added `docs/30-architecture/durable-root-commits-epoch-fences-restore-intents-activation-targets-live-binds-and-receipts.md` and `docs/70-shell/root-ledgers-epoch-fences-restore-tickets-and-activation-rails.md`.
- expanded the SlopOS datacube evaluation with the lesson that CapStore-like durable roots, epoch fences, restore intents, resurrection gates, activation targets, live handle sets, and receipts should stay separate while SlopOS and ViewFS are still in design.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography/source-head hygiene, evidence/claim/invariant/assumption registries, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 139 adds
- continued external research on capability-flow hygiene, capability graph/diff redaction, custody and export posture, portal-mediated delegation, path-escape hardening, and object-store currentness witnesses for the future SlopOS/ViewFS datacube.
- added `rfcs/0126-viewfs-keep-handle-inventories-custody-chains-outflow-gates-flow-snapshots-leak-verdicts-live-exports-and-receipts-separate.md`.
- added `docs/30-architecture/handle-inventories-custody-chains-outflow-gates-flow-snapshots-leak-verdicts-live-exports-and-receipts.md` and `docs/70-shell/flow-maps-custody-badges-outflow-gates-leak-sirens-and-audit-drawers.md`.
- expanded the SlopOS datacube evaluation with the lesson that SlopOS's capability graph, capability diff, capability export, wallet, portal, and capshell materials are best treated as redacted explanation and mediation posture, not as a final ViewFS authority ABI.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography/source-head hygiene, evidence/claim/invariant/assumption registries, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 138 adds
- continued external research on explicit per-process namespaces, exact handle-slot tables, portal-mediated imports, capability references, object-store currentness witnesses, and design-phase non-decisions for the future SlopOS datacube.
- added `rfcs/0125-viewfs-keep-launch-view-plans-bound-roots-handle-slots-portal-import-tickets-live-binds-and-receipts-separate.md`.
- added `docs/30-architecture/launch-view-plans-bound-roots-handle-slots-portal-import-tickets-live-binds-and-receipts.md` and `docs/70-shell/slot-maps-root-badges-import-tickets-and-live-bind-rails.md`.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with a new seam: launch view plan versus bound root versus handle slot table versus portal import ticket versus live bind/facet versus receipt/history, drawing especially on current SlopOS capshell/portal posture plus Fuchsia namespaces/capabilities, Capsicum/WASI, XDG Documents, Tahoe-LAFS, Cap'n Proto, EROS, and cloud object-store precondition discipline.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, review queue, and evidence index, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 134 adds
- continued external research on archive-tier honesty, thaw-job posture, temporary readable copies, expiry visibility, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0121-viewfs-keep-committed-objects-archive-tiers-thaw-jobs-thawed-copies-live-facets-and-receipts-separate.md`.
- added `docs/30-architecture/committed-objects-archive-tiers-thaw-jobs-thawed-copies-live-facets-and-receipts.md` and `docs/70-shell/frost-badges-thaw-beads-copy-thaw-ladders-expiry-lanterns-and-live-rails.md`.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with a new seam: committed object versus archive tier versus thaw job versus thawed copy versus live facet versus receipt/history, drawing especially on current SlopOS import/materialize/CapStore posture plus Amazon S3 restore semantics and Azure archive rehydration semantics.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, review queue, and evidence index, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## Revision 131 — 2026-03-28
- continued external research on retention clocks, hold-state honesty, purge eligibility, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0118-viewfs-keep-committed-objects-retention-clocks-hold-states-purge-verdicts-live-facets-and-receipts-separate.md`.
- added `docs/30-architecture/committed-objects-retention-clocks-hold-states-purge-verdicts-live-facets-and-receipts.md` and `docs/70-shell/hold-badges-retention-rails-purge-lamps-and-live-rails.md`.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with a new seam: committed object versus retention clock versus hold state versus purge verdict versus live facet versus receipt/history, drawing especially on current SlopOS persistence/verified-blob posture plus Amazon S3 Object Lock, Google Cloud Storage object holds and Object Retention Lock, and Azure immutable storage.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/slopos-seam-map.md`, `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-protocol-sketch.md`, `docs/00-meta/bibliography.md`, `docs/00-meta/external-source-head-register.md`, `docs/00-meta/external-source-review-queue.md`, and `docs/00-meta/evidence-index.md`.
- regenerated repo hygiene surfaces with `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 129 adds
- continued external research on assembly-by-reference honesty, member-descriptor graphs, aggregate-object birth, realized work-surface posture, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0116-viewfs-keep-assembly-recipes-member-descriptors-aggregate-objects-realized-work-surfaces-live-facets-and-receipts-separate.md` to keep recipe intent, exact member evidence, durable aggregate birth, realized work surfaces, live authority, and receipts visibly distinct.
- added `docs/30-architecture/assembly-recipes-member-descriptors-aggregate-objects-realized-work-surfaces-live-facets-and-receipts.md` and `docs/70-shell/recipe-cards-member-rails-aggregate-seals-unpack-lamps-and-live-rails.md` to sharpen assembly/materialize/unpack honesty without prematurely freezing one package, bundle, or aggregate-object ABI.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from current SlopOS composition/persistence posture plus Google Cloud Storage composite objects, OCI manifests/indexes, `git write-tree`, and containerd pull/unpack.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, review queue, and evidence index.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 128 adds
- continued external research on resumable upload/session honesty, staged part coverage, explicit finalization, abort/expiry truth, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0115-viewfs-keep-upload-sessions-part-coverage-completion-manifests-committed-objects-abort-verdicts-live-facets-and-receipts-separate.md` to keep upload sessions, part coverage, completion manifests, committed objects, abort verdicts, live facets, and receipts visibly distinct.
- added `docs/30-architecture/upload-sessions-part-coverage-completion-manifests-committed-objects-abort-verdicts-live-facets-and-receipts.md` and `docs/70-shell/session-beads-part-gauges-seal-ladders-abort-ash-and-live-rails.md` to sharpen resumable-import/object-commit honesty without freezing one universal multipart ABI or one final staging protocol.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from current SlopOS persistence/import/jobs posture plus Amazon S3 multipart upload, tus resumable uploads, OCI chunked blob upload, and Google Cloud Storage resumable sessions.
- refreshed architecture notes, shell idea/protocol notes, bibliography/source-head tracking, and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 127 adds
- continued external research on cheap clones, shared-backing honesty, copy-lineage receipts, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0114-viewfs-keep-fresh-object-identities-shared-backing-copy-lineage-live-facets-and-receipts-separate.md` to keep fresh logical object identity, shared-backing optimization, copy lineage, current live facet, and receipts visibly distinct.
- added `docs/30-architecture/fresh-object-identities-shared-backing-copy-lineage-live-facets-and-receipts.md` and `docs/70-shell/birth-badges-backing-ghosts-lineage-ladders-and-live-rails.md` to sharpen clone/reflink/snapshot-origin honesty without freezing one universal clone ABI or one final deep-copy policy.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from current SlopOS fresh-identity / explicit-lineage posture plus Linux reflink, Btrfs reflink, OpenZFS clone concepts, and APFS clones.
- refreshed architecture notes, shell idea/protocol notes, bibliography/source-head tracking, and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 125 adds
- continued external research on object-core versus name/head/order/supersession truth, with extra care not to let a design-phase object store pick one universal version mythology too early.
- added `rfcs/0112-viewfs-keep-object-cores-designations-revision-tokens-order-scopes-supersession-rows-live-facets-and-receipts-separate.md` to keep semantic object core, designation, revision token, ordered conflict scope, supersession evidence, current live facet, and receipts visibly distinct.
- added `docs/30-architecture/object-cores-designations-revision-tokens-order-scopes-supersession-rows-live-facets-and-receipts.md` and `docs/70-shell/head-badges-order-pips-supersession-ladders-and-facet-rails.md` to sharpen head/version/supersession honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from current SlopOS ordering-token/conflict-key posture, Kubernetes names/UIDs/resourceVersions, etcd revisions, Amazon S3 version IDs/delete markers, and Git reflogs.
- refreshed architecture notes, shell idea/protocol notes, bibliography/source-head tracking, and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 123 adds
- continued external research on stable review/gate digests, descriptive envelopes, explain-sidecar posture, and design-phase non-decisions for the future custom shell+terminal.
- added `rfcs/0110-viewfs-keep-authority-core-stamps-descriptive-review-envelopes-explain-sidecars-live-binds-and-receipts-separate.md` to keep stable review stamps, richer envelopes, explain/diff/provenance sidecars, current live binds, and receipts visibly distinct.
- added `docs/30-architecture/authority-core-stamps-descriptive-review-envelopes-explain-sidecars-live-binds-and-receipts.md` and `docs/70-shell/core-stamps-envelope-drawers-sidecar-lamps-and-live-rails.md` to sharpen drift/reconsent and review-envelope honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from current SlopOS wallet/core-digest posture, Git patch-id, OCI descriptor/annotations, in-toto statement subjects, and SLSA provenance.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell terminal protocol sketch, bibliography, moving-head source tracking, review queue, and evidence index, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 120 adds
- continued external research on descriptor-only versus verify-only versus read/write/publish handle classes, safe proof surfaces, and design-phase non-decisions for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with a new seam: descriptor/proof-only rows versus verify-only facets versus current read/edit/publish facets versus live room binds, drawing especially on current SlopOS wallet/docref/lease posture plus Tahoe-LAFS capability flavors, Linux `O_PATH`, and CHERIoT sealing.
- refreshed `docs/30-architecture/object-store-posture-v0.md`, `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can keep safe descriptive surfaces and live authority surfaces honest without freezing one universal proof or handle ABI too early.
- refreshed shell idea/protocol notes, bibliography/source-head tracking, and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 119 adds
- continued external research on capability facets, opaque handle classes, grouped authority kits, room-bound facet binding, and design-phase non-decisions for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with a new seam: object identity versus capability facet versus grouped kit versus live room bind versus published name, drawing especially on current SlopOS drafts plus Sandstorm Powerbox/grains, Fuchsia capabilities+dictionaries, Capsicum rights attenuation, and CHERIoT sealing.
- refreshed `docs/30-architecture/object-store-posture-v0.md`, `docs/30-architecture/viewfs-namespace-posture-v0.md`, `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can stay object-forward and capability-honest without freezing one universal handle taxonomy too early.
- refreshed shell idea/protocol notes, bibliography/source-head tracking, and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 118 adds
- continued external research on object-centered rooms, late tool attachment, mediated imports, and explicit retention-root posture for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Sandstorm grains/powerbox, Fuchsia namespaces, and Nix GC roots about keeping object homes, attached tools, imported binds, published names, and retention roots on distinct seams.
- refreshed `docs/30-architecture/object-store-posture-v0.md`, `docs/30-architecture/viewfs-namespace-posture-v0.md`, `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can stay object-forward without prematurely freezing one universal app or room model.
- refreshed bibliography/source-head tracking and evidence-index hygiene, then regenerated `out/context_pack.md` and `RELEASE-MANIFEST.json` for the new archive.

## What Revision 116 adds
- continued external research on explicit payer selection, requester-pays posture, budget leases, sponsorship-vs-authorization, separate resource ceilings, and shell-visible spend honesty for the future custom shell+terminal.
- added `rfcs/0108-viewfs-keep-action-authority-payer-roots-budget-leases-spend-reservations-charge-verdicts-and-receipts-separate.md` to keep action authority, payer roots, budget leases, spend reservations, charge verdicts, provider effects, and receipts visibly distinct.
- added `docs/30-architecture/action-authority-payer-roots-budget-leases-spend-reservations-charge-verdicts-and-receipts.md` and `docs/70-shell/payer-chips-spend-rails-charge-ghosts-and-burn-ladders.md` to sharpen sponsorship/cost honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from SlopOS budget-payer posture, Amazon S3 Requester Pays, Google Cloud Storage Requester Pays, Kubernetes ResourceQuota vs RBAC, seL4 MCS scheduling-context donation, Genode session resource donation, and cgroup v2 resource control.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 115 adds
- continued external research on caller-bound request contexts, detached continuation roots, deadline propagation, cooperative cancellation, cleanup-after-cancel posture, and shell-visible continue-without-me honesty for the future custom shell+terminal.
- added `rfcs/0107-viewfs-keep-caller-request-contexts-detached-roots-deadline-intents-cancellation-state-provider-operations-and-receipts-separate.md` to keep caller request context, detached roots, deadline/cancellation posture, provider follow-up tickets, and receipts visibly distinct.
- added `docs/30-architecture/caller-request-contexts-detached-roots-deadline-intents-cancellation-state-and-provider-operations.md` and `docs/70-shell/cutoff-lamps-detach-root-cards-and-continue-without-me-ladders.md` to sharpen cancellation/deadline/detach honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from SlopOS request-context posture, Go `context` / `WithoutCancel`, gRPC deadlines, Kotlin cancellation + `NonCancellable`, Temporal disconnected cleanup, and Cap'n Proto RPC cancellation logistics.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 114 adds
- continued external research on retry-safe sameness witnesses, idempotency keys, canonical-request mismatch handling, key expiry/pruning, and shell-visible duplicate-versus-fresh honesty for the future custom shell+terminal.
- added `rfcs/0106-viewfs-keep-live-room-bindings-local-edit-shadows-intent-keys-accepted-pushback-requests-provider-operations-completion-verdicts-adopted-results-and-receipts-separate.md` to keep current binds, local edit shadows, retry-safe sameness witnesses, request admission, provider operation handles, completion verdicts, local adopted results, and receipts visibly distinct.
- added `docs/30-architecture/live-room-bindings-local-edit-shadows-intent-keys-accepted-pushback-requests-provider-operations-and-adopted-results.md` and `docs/70-shell/intent-lamps-retry-braids-sameness-chips-and-not-the-same-request-shutters.md` to sharpen retry/dedupe/adoption honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from SlopOS request-key discipline, the HTTP Idempotency-Key draft, AWS EC2 client tokens, Stripe idempotent requests, and long-running-operation follow-up posture.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 113 adds
- continued external research on accepted-versus-completed mutation posture, HTTP 202 humility, long-running operation handles, async request-reply status endpoints, and shell-visible settlement honesty for the future custom shell+terminal.
- added `rfcs/0105-viewfs-keep-live-room-bindings-local-edit-shadows-accepted-pushback-requests-provider-operations-completion-verdicts-adopted-results-and-receipts-separate.md` to keep current binds, local edit shadows, request admission, provider operation handles, completion verdicts, local adopted results, and receipts visibly distinct.
- added `docs/30-architecture/live-room-bindings-local-edit-shadows-accepted-pushback-requests-provider-operations-completion-verdicts-and-adopted-results.md` and `docs/70-shell/accept-slips-operation-beads-settle-rails-and-expiry-lanterns.md` to sharpen acceptance/completion/adoption honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from SlopOS acceptance/completion posture, HTTP 202, XDG request handles, Google-style long-running operations, and Azure asynchronous request-reply patterns.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 112 adds
- continued external research on exact pushback bases, conditional writes, lease-vs-commit posture, provider verdicts, and shell-visible conflict/adoption honesty for the future custom shell+terminal.
- added `rfcs/0104-viewfs-keep-live-room-bindings-local-edit-shadows-pushback-bases-provider-verdicts-adopted-results-and-receipts-separate.md` to keep current binds, local editable shadows, exact pushback basis/preconditions, provider-side verdicts, local adopted results, and receipts visibly distinct.
- added `docs/30-architecture/live-room-bindings-local-edit-shadows-pushback-bases-provider-verdicts-and-adopted-results.md` and `docs/70-shell/basis-lamps-verdict-cards-adopt-rails-and-lease-ladders.md` to sharpen pushback/conflict/adoption honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from SlopOS precondition witnesses and commit schemas, HTTP conditional requests, S3 and Cloud Storage preconditions, Git force-with-lease/update-ref posture, WebDAV locking, etcd conditional transactions, and writable-session staging.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 111 adds
- continued external research on ordered union directories, writable lower/upper merge posture, placeholder/materialize/evict ladders, explicit realization, and shell-visible edit-shadow honesty for the future custom shell+terminal.
- added `rfcs/0103-viewfs-keep-live-room-bindings-projected-bases-local-upper-overlays-merged-room-presentations-publish-results-and-receipts-separate.md` to keep current binds, projected bases, writable uppers, merged views, publish/commit results, and receipts visibly distinct.
- added `docs/30-architecture/live-room-bindings-projected-bases-local-upper-overlays-and-merged-room-presentations.md` and `docs/70-shell/stack-badges-whiteout-ghosts-and-commit-ladders.md` to sharpen overlay/merge/edit-shadow honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from OverlayFS, Plan 9 union directories, Kubernetes projected volumes, Apple File Provider placeholder/materialize/evict posture, and Nix realisation.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 110 adds
- continued external research on projected document views, provider-backed hierarchies, namespace publication, placeholder/hydration posture, and shell-visible locality honesty for the future custom shell+terminal.
- added `rfcs/0102-viewfs-keep-live-room-bindings-provider-backed-projection-sites-published-room-aliases-localizations-and-receipts-separate.md` to keep current binds, scoped projection sites, room-local publication, local realization, and receipts visibly distinct.
- added `docs/30-architecture/live-room-bindings-provider-projection-sites-published-room-aliases-and-localizations.md` and `docs/70-shell/site-ledgers-provider-halos-and-bind-here-ladders.md` to sharpen projection/publication/locality honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from XDG Documents, Android SAF and FileProvider, Fuchsia namespaces/directory capabilities, and Windows Cloud Files placeholder/hydration posture.
- refreshed the architecture overview, design-splits note, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 109 adds
- continued external research on clipboard/selection offers, XDG transfer sessions, clipboard-manager retention, typed clipboard APIs, and paste-origin signaling for the future custom shell+terminal.
- added `rfcs/0101-viewfs-keep-live-room-bindings-selection-owners-transfer-offers-manager-retentions-paste-capsules-materialized-imports-and-receipts-separate.md` to keep current offer source, manager-retained ghosts, prompt-local paste, and later local materialization visibly distinct.
- added `docs/30-architecture/live-room-bindings-selection-owners-transfer-offers-manager-retentions-paste-capsules-and-materialized-imports.md` and `docs/70-shell/offer-cards-paste-capsules-and-history-ghosts.md` to sharpen transfer/history/paste honesty for the future shell.
- expanded `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with new lessons from Wayland selection/data-control, XDG FileTransfer, the Clipboard API, xterm bracketed paste, and kitty clipboard posture.
- refreshed the architecture overview, SlopOS seam map, shell super-awesome moves, shell-terminal protocol sketch, bibliography, source-head register, evidence index, and repo lint coverage.
- regenerated repo hygiene surfaces via `make lint`, `make context-pack`, and `make release-manifest` before packaging.

## What Revision 108 adds
- added `rfcs/0100-viewfs-keep-live-room-bindings-observe-mirrors-automation-leases-synthetic-input-lanes-secure-entry-exclusions-and-receipts-separate.md` so **live room bindings**, **observe/semantic mirrors**, **automation lease/session posture**, **actual synthetic-input lanes**, **secure-entry exclusion/redaction state**, and **receipts/history** stay visibly distinct.
- added `docs/30-architecture/live-room-bindings-observe-mirrors-automation-leases-synthetic-input-lanes-and-secure-entry-exclusions.md` and `docs/70-shell/mirror-strips-rehearsal-rails-and-secure-entry-curtains.md` so ViewFS can sharpen assistive/automation honesty without prematurely freezing one automation substrate, one mirror store, or one secure-entry clamp carrier.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS accessibility/automation/trusted-UI posture does and does not settle about observe-only mirrors, leased automation, synthetic input, and secure-entry blocking.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from XDG InputCapture, XDG RemoteDesktop, Android MediaProjection plus `FLAG_SECURE`, Fuchsia accessibility/focus-chain posture, and shell-integration quality precedents.
- refreshed shell notes and protocol sketches with **mirror strips**, **lease chips**, **rehearsal rails**, **secure-entry curtains**, and **quality badges** worth stealing for the future custom shell+terminal.

## What Revision 107 adds
- added `rfcs/0099-viewfs-keep-live-room-bindings-summon-beacons-activation-batons-foreground-turns-secure-entry-gates-and-receipts-separate.md` so **live room bindings**, **summon/surface-me cues**, **activation/raise eligibility**, **actual foreground turns**, **secure-entry/trusted-input posture**, and **receipts/history** stay visibly distinct.
- added `docs/30-architecture/live-room-bindings-summon-beacons-activation-batons-foreground-turns-and-secure-entry.md` and `docs/70-shell/summon-beacons-front-latches-and-secure-entry-shutters.md` so ViewFS can sharpen shell visibility and trusted-entry honesty without prematurely freezing one focus manager, one summon schema, or one secure-entry carrier.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS tool-ui/trusted-ui/attention posture does and does not settle about summon cues, activation batons, actual foreground turns, and secure-entry state.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Wayland xdg-activation, Windows foreground delegation, xterm focus events, and Ghostty/WezTerm-style prompt-aware shell integration.
- refreshed shell notes and protocol sketches with **summon beacons**, **activation baton chips**, **front latches**, **secure-entry shutters**, and **quality badges** worth stealing for the future custom shell+terminal.

## What Revision 106 adds
- added `rfcs/0098-viewfs-keep-live-room-bindings-attention-cues-interrupt-grades-quiet-windows-ack-ledgers-and-receipts-separate.md` so **live room bindings**, **attention cues/adverts**, **interrupt grades**, **quiet/suppression posture**, **durable ack/follow-up rows**, and **receipts/history** stay visibly distinct.
- added `docs/30-architecture/live-room-bindings-attention-cues-interrupt-grades-quiet-windows-and-ack-ledgers.md` and `docs/70-shell/attention-pips-quiet-shutters-and-ack-ledgers.md` so ViewFS can sharpen shell attention honesty without prematurely freezing one inbox/history surface, one interrupt-entitlement lane, or one final quiet-mode carrier.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS attention/background posture does and does not settle about pips, interruption grades, suppression posture, and durable follow-up.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from XDG Notification, Android notification channels and time-sensitive notifications, Apple critical alerts, and tmux activity/bell/silence chrome.
- refreshed shell notes and protocol sketches with **attention pips**, **interrupt ladders**, **quiet shutters**, and **ack ledgers** worth stealing for the future custom shell+terminal.
## What Revision 105 adds
- added `rfcs/0097-viewfs-keep-live-room-bindings-visibility-states-keep-warm-leases-restore-intents-deferred-repair-jobs-and-receipts-separate.md` so **live room bindings**, **visibility state**, **keep-warm/background-presence grants**, **restore/autostart intents**, **deferred repair jobs**, and **receipts/history** stay visibly distinct.
- added `docs/30-architecture/live-room-bindings-visibility-states-keep-warm-leases-restore-intents-and-deferred-repair-jobs.md` and `docs/70-shell/warmth-rails-login-lanterns-and-defer-drawers.md` so ViewFS can sharpen warm/background continuity honesty without prematurely freezing one background-presence model, one restore carrier, or one deferred-repair substrate.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS background/job/portal posture does and does not settle about keep-warm continuity, restore intent, and deferred repair.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from XDG Background, Android background execution limits, Apple BackgroundTasks, Kubernetes Leases, EndpointSlice lifecycle conditions, and shell-integration quality precedents.
- refreshed shell notes and protocol sketches with **warmth rails**, **keep-warm badges**, **login lanterns**, **defer drawers**, and **quality chips** worth stealing for the future custom shell+terminal.

## What Revision 102 adds
- added `rfcs/0094-viewfs-keep-activation-kits-restart-lockers-namespace-pins-live-room-bindings-and-receipts-separate.md` so **activation kits**, **restart lockers**, **namespace pins**, **current live room bindings**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/activation-kits-restart-lockers-namespace-pins-and-live-room-bindings.md` and `docs/70-shell/restart-shelves-wake-kits-pin-badges-and-cold-start-honesty.md` so ViewFS can sharpen warm-restart and room continuity honesty without prematurely freezing one restart-locker model, one namespace-pin primitive, or one final room-manager split.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS capstore/capshell/wallet posture does and does not settle about restart lockers, namespace pins, warm exact versus warm partial starts, and cold fallback.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from systemd socket activation and fdstore, Linux namespace fd lifetime, launchd socket activation, and sibling pressure from Schell anchor-death cards, Ward revalidation fences, and Steward adaptation witnesses.
- refreshed shell notes and protocol sketches with **restart shelves**, **wake kits**, **pin badges**, **warm-start lamps**, **cold-start honesty cards**, and **replay-with-honesty rails** worth stealing for the future custom shell+terminal.

## What Revision 101 adds
- added `rfcs/0093-viewfs-keep-durable-import-anchors-live-room-bindings-stale-shadows-repair-plans-and-receipts-separate.md` so **durable import anchors**, **current live room bindings**, **stale-but-repairable shadows**, **repair/rebind plans**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/durable-import-anchors-live-room-bindings-stale-shadows-and-repair-plans.md` and `docs/70-shell/stale-shadows-repair-ladders-and-rebind-receipts.md` so ViewFS can sharpen durable-access / restore / repair honesty without prematurely freezing one final durable-handle schema, repair carrier, or continuity object model.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS capstore/document/capshell posture does and does not settle about durable anchors, stale shadows, and repair plans.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from XDG documents/request/transfer, Apple security-scoped bookmark resolve/start-accessing/stale flow, Android SAF persistence, Windows FutureAccessList hygiene, Web File System Access permission ladders, and Capsicum/pidfd current-handle truth.
- refreshed shell notes and protocol sketches with **stale shadow chips**, **repair ladders**, **durable-access racks**, **rebind receipts**, and **bounded durable-list hygiene** worth stealing for the future custom shell+terminal.

# ViewFS datacube
## What Revision 100 adds
- added `rfcs/0092-viewfs-keep-namespace-plans-live-room-bindings-portal-import-sessions-local-overlays-and-receipts-separate.md` so **namespace plans**, **live room bindings**, **portal import/request sessions**, **local-only overlays**, **anchor/reset death signals**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/namespace-plans-live-room-bindings-import-sessions-and-local-overlays.md` and `docs/70-shell/switchboards-overlay-racks-and-anchor-death-cards.md` so ViewFS can sharpen custom-shell switch/import honesty without prematurely freezing one object-store schema, one overlay model, one namespace-switch ABI, or one final shell wire format.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS view/capshell/wallet/plumb/document-portal posture does and does not settle about namespace planning, live room-local binding, portal-session truth, and local overlay residue.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Plan 9 namespaces, Fuchsia dictionary capabilities, XDG request/document/session splits, browser and desktop durable-access repair ladders, Helm local overlays, and Schell anchor-death/reset-scope honesty.
- refreshed shell notes and protocol sketches with **namespace switchboards**, **overlay racks**, **import session strips**, **anchor death cards**, and **reset-scope chips** worth stealing for the future custom shell+terminal.
# ViewFS datacube
## What Revision 099 adds
- added `rfcs/0091-viewfs-keep-room-identities-current-views-context-inheritance-child-spawn-recipes-imported-bindings-and-receipts-separate.md` so **room identities**, **current room-local views**, **context-inheritance postures**, **prepared child spawn/import recipes**, **child-received bindings/imports**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/room-identities-current-views-context-inheritance-and-child-spawns.md` and `docs/70-shell/room-badges-context-diffs-and-spawn-recipes.md` so ViewFS can sharpen custom-shell room honesty without prematurely freezing one namespace-clone model, one spawn-recipe schema, or one final object-store/import contract.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS view/capshell/wallet/plumb posture does and does not settle about room identity versus current view versus inheritance versus child-import truth.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Fuchsia namespaces and dictionary capabilities, XDG request/documents/file-transfer splits, WezTerm semantic zones, fish delight, Nushell overlays, Ghostty room/palette ideas, Linux `O_CLOEXEC`, and Capsicum adoption diagnostics.
- refreshed shell notes and protocol sketches with **room badges**, **context diffs**, **spawn recipes**, **child import trays**, and **receipt-first room restore** worth stealing for the future custom shell+terminal.
## What Revision 098 adds
- added `rfcs/0090-viewfs-keep-editable-buffers-parsed-structures-advisory-diagnostics-compiled-command-packets-prepared-actions-and-receipts-separate.md` so **editable buffers**, **parsed structures/highlight models**, **advisory diagnostics**, **compiled command packets**, **prepared actions**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/editable-buffers-parsed-structures-advisory-diagnostics-and-compiled-packets.md` and `docs/70-shell/parse-lenses-diagnostic-rails-and-packet-gutters.md` so ViewFS can sharpen custom-shell editing honesty without prematurely freezing one parser, one lint engine, or one packet format.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS capshell/shell-string posture does and does not settle about editable text versus bound packet truth.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Tree-sitter, LSP diagnostics, ShellCheck, and fish syntax highlighting.
- refreshed shell notes and protocol sketches with **parse lenses**, **recovery veils**, **diagnostic rails**, **packet gutters**, and **compile-diff cards** worth stealing for the future custom shell+terminal.
## What Revision 097 adds
- added `rfcs/0089-viewfs-keep-built-in-verbs-lexical-expansions-semantic-command-layers-key-actions-external-launches-and-receipts-separate.md` so **built-in verbs**, **typed lexical expansions**, **semantic command layers**, **key actions/widgets**, **external launches**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/command-surface-layers-key-actions-and-external-launches.md` and `docs/70-shell/verb-provenance-cards-overlay-racks-and-keytable-lamps.md` so ViewFS can sharpen command-surface honesty for the future custom shell without prematurely freezing one alias model, one overlay format, one palette protocol, or one final shell language.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS capshell posture and sibling config-layer pressure do and do not settle about built-in verbs versus expansions versus overlays versus widgets versus external launches.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from fish abbreviations, Nushell overlays/custom commands/which, zsh ZLE widgets, Ghostty key tables and command palette, and VS Code profiles.
- refreshed shell notes and protocol sketches with **verb provenance cards**, **abbr gutters**, **overlay racks**, **key-table lamps**, and **which ladders** worth stealing for the future custom shell+terminal.
## What Revision 096 adds
- added `rfcs/0088-viewfs-keep-built-in-shell-affordances-explicit-customization-bundles-startup-files-project-hooks-and-receipts-separate.md` so **built-in shell affordances**, **explicit reviewed customization bundles**, **ambient startup/profile files**, **project-local activation hooks**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/built-in-shell-affordances-customization-bundles-startup-files-and-project-hooks.md` and `docs/70-shell/clean-start-lamps-bundle-ledgers-and-hook-quarantine.md` so ViewFS can sharpen custom-shell startup honesty without prematurely freezing one bundle schema, one hook scope lattice, or one legacy-profile import story.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS Capshell startup-profile work does and does not settle about built-in shell delight versus reviewed bundles versus ambient startup files versus project hooks.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from SlopOS Capshell startup-profile posture, direnv allow/re-allow, VS Code Workspace Trust, Ghostty shell integration, and PowerShell profiles.
- refreshed shell notes and protocol sketches with **clean-start lamps**, **bundle ledgers**, **profile-debt drawers**, **hook quarantine shutters**, and **prompt provenance cards** worth stealing for the future custom shell+terminal.
## What Revision 095 adds
- added `rfcs/0087-viewfs-keep-native-attaches-adapted-attaches-coerced-representations-local-realizations-and-receipts-separate.md` so **native attaches**, **adapted attaches**, **coerced representations**, **local realizations**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/native-attaches-adapted-attaches-coerced-representations-and-local-realizations.md` and `docs/70-shell/attach-mode-badges-adapter-veils-and-virtuality-lamps.md` so ViewFS can sharpen receiver-side fit/fidelity honesty without prematurely freezing one wrapper ABI, one representation taxonomy, or one final object-store contract.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS document/import/view seams do and do not settle about native fit versus adapter-backed usability versus translated representation truth.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Android virtual files, WebAssembly component-model resource handles, XDG document projection, Fuchsia namespaces, and sibling-cube pressure toward explicit receiver-side fit/fidelity truth.
- refreshed shell notes and protocol sketches with **attach-mode badges**, **adapter veils**, **virtuality lamps**, **same-object-versus-translated drawers**, and **make-local-for-native ladders** worth stealing for the future custom shell+terminal.
## What Revision 094 adds
- added `rfcs/0086-viewfs-keep-privilege-brackets-borrowed-authority-call-chain-contexts-deny-only-hints-and-receipts-separate.md` so **privilege brackets**, **borrowed authority**, **call-chain context**, **deny-only routing hints**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/privilege-brackets-borrowed-authority-call-chain-contexts-and-deny-only-hints.md` and `docs/70-shell/bracket-rails-caller-badges-and-who-asked-drawers.md` so ViewFS can sharpen helper/plugin/automation honesty without prematurely freezing one call-chain schema, one bracket carrier, or one deny-only rule family.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS privilege-bracketing and sibling issuer/helper/origin material do and do not settle about borrowed authority versus caller context.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from the confused deputy paper, Java Scoped Values, Python `contextvars`, Node `AsyncLocalStorage`, and ASP.NET’s caution about ambient async-local request state.
- refreshed shell notes and protocol sketches with **bracket rails**, **caller badges**, **who-asked drawers**, **borrowed-authority drawers**, **deny-only shutters**, and **deputy-fog warnings** worth stealing for the future custom shell+terminal.
## What Revision 093 adds
- added `rfcs/0085-viewfs-keep-route-envelopes-authority-sidecars-sink-bindings-and-receipts-separate.md` so **typed route capsules**, **authority sidecars**, **actual sink-side binds/imports**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/route-envelopes-authority-sidecars-sink-bindings-and-receipts.md` and `docs/70-shell/route-slips-authority-sidecars-and-sink-trays.md` so ViewFS can sharpen plumb/share/import honesty without prematurely freezing one route-envelope schema, one sidecar taxonomy, or one sink-binding backend.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS plumb / wallet / document / transfer seams do and do not settle about designation-only routing versus sink-held authority.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Plan 9 plumbing, Android Intent URI grants and temporary access, XDG request lifetimes, Wayland representation offers, and Foundry’s sidecar/adoption discipline.
- refreshed shell notes and protocol sketches with **route slips**, **authority sidecar chips**, **designation-only pills**, **sink trays**, and **dry-run route diffs** worth stealing for the future custom shell+terminal.
## What Revision 092 adds
- added `rfcs/0084-viewfs-keep-foreign-backed-borrows-compat-attaches-projected-imports-local-realizations-and-receipts-separate.md` so **foreign-backed borrows**, **receiver-local compat attaches**, **projected imports**, **local realizations**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/foreign-backed-borrows-compat-attaches-projected-imports-and-local-realizations.md` and `docs/70-shell/borrow-rails-projection-badges-and-make-here-ladders.md` so ViewFS can sharpen receiver-side import/adoption honesty without prematurely freezing one wrapper ABI, one projection protocol, or one final localization contract.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS document/portal/import seams do and do not settle about borrowed foreign-backed usability versus projected locality versus truly local realization.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Android SAF, Apple document-picker and File Provider materialization, XDG Documents portal projection, Fuchsia namespace attachments, and Foundry's foreign-cell / borrowed-handle posture.
- refreshed shell notes and protocol sketches with **borrow rails**, **projection badges**, **make-here ladders**, **provider-owned halos**, and **dataless/materialized lamps** worth stealing for the future custom shell+terminal.
## What Revision 091 adds
- added `rfcs/0083-viewfs-keep-current-possession-local-duplication-live-lends-representation-exports-and-receipts-separate.md` so **current possession**, **local duplication posture**, **live-lend posture**, **representation-export posture**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/current-possession-local-duplication-live-lends-and-representation-exports.md` and `docs/70-shell/lend-ladders-lane-fit-badges-and-bytes-only-fallbacks.md` so ViewFS can sharpen share/send/export honesty without prematurely freezing one live-transfer ABI, one representation-export taxonomy, or one receiver-adoption model.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS transfer-portal / attenuation posture does and does not settle about held-here versus lendable-here versus bytes-only export truth.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Mach port rights, seL4 Grant/GrantReply transfer rules, UNIX `SCM_RIGHTS`, Wayland data offers, XDG FileTransfer, and kitty's explicit TTY file-transfer lane.
- refreshed shell notes and protocol sketches with **lend ladders**, **lane-fit badges**, **bytes-only fallback chips**, **share sheets**, and **same-object versus new-representation drawers** worth stealing for the future custom shell+terminal.
## What Revision 090 adds
- added `rfcs/0082-viewfs-keep-live-possession-status-carriers-local-holds-successor-refresh-and-receipts-separate.md` so **live possession**, **watch/status carriers**, **local hold/quarantine posture**, **successor/refresh posture**, **post-watch invocability**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/live-possession-status-carriers-local-holds-and-successor-refresh.md` and `docs/70-shell/watch-braids-hold-rails-and-successor-lanterns.md` so ViewFS can sharpen watch/hold/refresh honesty without prematurely freezing one status transport, watch receiver, or successor-adoption mechanism.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS, Ward, and Harbor material does and does not settle about standing-watch good status versus mere live possession.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from OAuth token introspection/revocation, W3C Bitstring Status Lists, OCSP/CRL hold semantics, TUF freshness/root rotation, and Ward’s status-carrier / attenuation-event posture.
- refreshed shell notes and protocol sketches with **watch braids**, **hold rails**, **successor lanterns**, **stale-watch fog**, and **quarantine shutters** worth stealing for the future custom shell+terminal.
## What Revision 089 adds
- added `rfcs/0081-viewfs-keep-current-possession-freshness-step-up-current-invocability-and-receipts-separate.md` so **current possession**, **freshness/recency posture**, **step-up/stronger-auth posture**, **local presence or user-verification posture**, **current invocability**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/current-possession-freshness-step-up-and-current-invocability.md` and `docs/70-shell/step-up-ladders-recency-shutters-and-why-not-now-drawers.md` so ViewFS can sharpen action-time truth without prematurely freezing one assurance taxonomy, proof carrier, or auth-mediation substrate.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS auth-recency / user-presence posture does and does not settle about possession versus invocability.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from RFC 9470 step-up auth, OpenID Connect `max_age` / `auth_time`, WebAuthn UP/UV posture, Android Keystore authentication gating, and Harbor's proximity/timebound continuation ideas.
- refreshed shell notes and protocol sketches with **step-up ladders**, **recency shutters**, **presence pins**, **satisfaction ghosts**, and **why-not-now drawers** worth stealing for the future custom shell+terminal.
## What Revision 088 adds
- added `rfcs/0080-viewfs-keep-claim-tickets-holder-bound-grants-passable-live-handles-spent-tickets-and-receipts-separate.md` so **claim/redeem tickets**, **holder-bound grants**, **passable live handles**, **spent/expired tickets**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/claim-tickets-holder-bound-grants-and-spent-receipts.md` and `docs/70-shell/redemption-ladders-holder-proof-badges-and-spent-ghosts.md` so ViewFS can sharpen redeem/replay/passability honesty without prematurely freezing one final token wallet, proof mechanism, or CapStore redemption substrate.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS and Steward seams do and do not settle about one-shot claims, holder-bound grants, and live-handle passability.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from OAuth authorization codes, DPoP sender-constrained tokens, Android PendingIntent one-shot guidance, XDG portal request/session handles, and Steward’s consumable/holder-bound grant posture.
- refreshed shell notes and protocol sketches with **redemption ladders**, **holder-proof badges**, **burn-after-use chips**, and **spent ghosts** worth stealing for the future custom shell+terminal.
## What Revision 087 adds
- added `rfcs/0079-viewfs-keep-provider-ready-claims-reacquire-obligations-local-realizations-live-handles-and-receipts-separate.md` so **provider-ready claims**, **reacquire/repair duties**, **local realization**, **current live handles**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/provider-ready-claims-reacquire-obligations-local-realizations-and-live-handles.md` and `docs/70-shell/make-local-ladders-provider-owned-badges-and-repair-rails.md` so ViewFS can sharpen `make local` and restore/repair honesty without prematurely freezing one final object-store, fetch, or portal-localization mechanism.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper evaluation of what current SlopOS continuity/import seams do and do not settle about provider-ready versus local-realized truth.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Git partial clone/promisor remotes, Nix realisation/substituters, Fuchsia capability availability, Foundry restore/reacquire ideas, and semantic terminal protocols.
- refreshed shell notes and protocol sketches with **make-local ladders**, **provider-owned badges**, **repair rails**, **offline fog**, and **locality lamps** worth stealing for the future custom shell+terminal.
## What Revision 086 adds
- added `rfcs/0078-viewfs-keep-presence-adverts-readiness-current-authority-and-receipts-separate.md` so **provider/catalog presence**, **freshness-scoped readiness**, **grant-needed posture**, **direct current authority**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/presence-adverts-readiness-current-authority-and-receipts.md` and `docs/70-shell/presence-halos-readiness-lamps-and-withdrawn-ghosts.md` so ViewFS can sharpen advert/readiness/grant honesty without prematurely freezing one final provider-catalog, readiness-watch, or mediation protocol.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS MCP/catalog/presence seams do and do not settle about advertised presence versus readiness versus current authority.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Fuchsia outgoing capabilities, MCP roots/resources/prompts/tools catalogs, DNS-SD service discovery, Kubernetes EndpointSlice readiness, and semantic terminal protocols.
- refreshed shell notes and protocol sketches with **presence halos**, **readiness lamps**, **withdrawn ghosts**, **grant-needed ladders**, and **advert ledgers** worth stealing for the future custom shell+terminal.

## What Revision 085 adds
- added `rfcs/0077-viewfs-keep-discoverability-enumeration-exact-opens-fit-notes-and-receipts-separate.md` so **direct current authority**, **exact-name reachability**, **enumeration/listability**, **mediated fit notes/suggestions**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/discoverability-enumeration-exact-name-reachability-and-fit-notes.md` and `docs/70-shell/dark-directories-known-name-chips-and-browse-gates.md` so ViewFS can sharpen browse/open/search honesty without prematurely freezing one final directory-rights lattice, search/index substrate, or provider disclosure policy.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS capshell/MCP/namecert seams do and do not settle about discoverability versus authority.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Linux search permission, WASI rights, Fuchsia capability namespaces, Sandstorm powerbox match quality, and semantic terminal protocols.
- refreshed shell notes and protocol sketches with **dark directories**, **known-name chips**, **browse gates**, **fit sheets**, and **search-result dimmers** worth stealing for the future custom shell+terminal.

## What Revision 084 adds
- added `rfcs/0076-viewfs-keep-explicit-handle-opens-rooted-compat-pathwalks-ambient-escapes-and-receipts-separate.md` so **direct current-handle opens**, **rooted compat walkers**, **portal-mediated grants/projections**, **ambient host escapes**, and **durable receipts/history** stay visibly distinct.
- added `docs/30-architecture/explicit-handle-opens-rooted-compat-pathwalks-and-ambient-escapes.md` and `docs/70-shell/ambient-debt-sirens-safe-open-ladders-and-escape-hatch-receipts.md` so ViewFS can sharpen the `safe open` story without prematurely freezing one final object-store schema, portal protocol, or compat API.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a stronger evaluation of what current SlopOS capshell/view/document seams do and do not settle about explicit authority versus rooted compat versus ambient escape.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Capsicum/cap-std, `openat2`, Sandstorm powerbox, Plan 9 import/plumb, Foundation CAS, and semantic terminal protocols.
- refreshed shell notes and protocol sketches with **safe-open ladders**, **ambient-debt sirens**, **route provenance drawers**, **import fit notes**, and **replace-this-debt** affordances worth stealing for the future custom shell+terminal.

## What Revision 083 adds
- added `rfcs/0075-viewfs-keep-store-membership-synthetic-views-live-handles-published-names-and-receipts-separate.md` so **store membership**, **synthetic/portal view projection**, **live current handles**, **published names in one process view**, and **receipt/history** stay visibly distinct.
- added `docs/30-architecture/store-membership-synthetic-views-live-handles-and-published-names.md` and `docs/70-shell/published-name-ledgers-and-synthetic-view-badges.md` so ViewFS can sharpen object-store + per-process namespace + portal-import posture without prematurely freezing one final publication, projection, or durable-reopen mechanism.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with the new store/projection/publication seam and a sharper evaluation of what current SlopOS view-namespace and document-portal posture does and does not settle.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with stronger lessons from Plan 9 private namespaces, Fuchsia namespace publication and dictionary capabilities, and XDG request/file/document portal restricted-view behavior.
- refreshed shell notes and protocol sketches with **published-name ledgers**, **synthetic-view badges**, **publish-here ladders**, and **projection/locality adjuncts** worth stealing for the future custom shell+terminal.

## What Revision 082 adds
- added `docs/30-architecture/activation-carriers-badged-handle-copies-and-object-identity.md` so startup carriers, live handle copies, issuer badges/witnesses, object refs, local binds, reopen lanes, and receipts stay visibly distinct while SlopOS is still deciding more of the surrounding runtime.
- added `docs/70-shell/activation-slots-issuer-badges-and-handoff-sheets.md` and refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-ideas.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with **activation sheets**, **handoff sheets**, **copy-lineage drawers**, **issuer chips**, and **truth-grade blocks** worth stealing for a future custom shell+terminal.
- refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can sharpen object-store + capability-handle + explicit-namespace posture without prematurely freezing one durable-handle, portal, or continuity model.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with sharper lessons from Plan 9 namespaces, Fuchsia capability-routed namespaces, systemd socket activation/fd store, UNIX descriptor passing, and semantic terminal protocols.

## What Revision 081 adds
- `rfcs/0074-viewfs-keep-delta-recipes-exact-bases-apply-sessions-reconstructed-objects-and-receipts-separate.md` so delta recipes, exact basis requirements, current apply sessions, reconstructed target objects, fallback full-fetch lanes, and durable receipts/history stay visibly distinct.
- added architecture and shell notes for delta recipes, basis cards, apply ladders, and rebuilt-from lineage without prematurely standardizing one final patch format or apply owner.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with sharper lessons from HTTP `If-Range`, delta encoding, VCDIFF, OSTree static deltas, and zsync.

## What Revision 080 adds
- `rfcs/0073-viewfs-keep-partial-residency-chunk-layouts-whole-object-proofs-live-range-sessions-and-receipts-separate.md` so sparse local coverage, partition/layout knowledge, whole-object completeness/proof, live range-fill state, and durable receipts/history stay visibly distinct.
- added `docs/30-architecture/partial-residency-chunk-layouts-and-whole-object-proofs.md` and refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can sharpen sparse/lazy object truth without overcommitting one final sparse-store or proof policy.
- added `docs/70-shell/hole-maps-range-panels-and-whole-proof-ladders.md` and refreshed `docs/70-shell/shell-super-awesome-moves.md` with **hole maps**, **range panels**, **whole-proof ladders**, **offline honesty lamps**, and **composite-checksum warnings** worth stealing for a future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with sharper lessons from HTTP range semantics, incomplete-response caching, eStargz lazy pulling, S3 multipart checksum/ETag caveats, and Zarr chunk layouts.
- expanded bibliography and moving-head source tracking, refreshed the external review queue, regenerated the context pack and release manifest, and kept lint clean for the new revision.

## What Revision 079 adds
- `rfcs/0072-viewfs-keep-observed-validators-writable-sessions-write-holds-commit-preconditions-committed-versions-and-receipts-separate.md` so observed validators/bases, private writable sessions, live write holds, exact commit preconditions, winning committed versions, and durable receipts/history stay visibly distinct.
- added `docs/30-architecture/observed-validators-writable-sessions-and-commit-cuts.md` and refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so ViewFS can sharpen edit/commit truth without overcommitting one final transaction model.
- added `docs/70-shell/draft-gutters-commit-shutters-and-stale-base-lamps.md` and refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-ideas.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with **stale-base lamps**, **draft gutters**, **hold meters**, and **commit shutters** worth stealing for a future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with sharper lessons from HTTP conditional requests, Cloud Storage preconditions, etcd compare-and-swap, WebDAV lock refresh, browser writable sessions, and SlopOS precondition/commit seams.
- expanded bibliography and moving-head source tracking, refreshed the external review queue, regenerated the context pack and release manifest, and kept lint clean for the new revision.

## What Revision 075 adds
- `rfcs/0068-viewfs-keep-object-identity-view-placement-current-handle-rights-advertised-operations-and-receipts-separate.md` so exact object identity, current placement in a view, current handle-rights posture, advertised operations, and durable receipts/history stay visibly distinct.
- added `docs/30-architecture/identity-placement-rights-and-affordances.md` and refreshed `docs/30-architecture/architecture-overview.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` so action menus can be driven by affordance truth instead of path folklore.
- refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-protocol-sketch.md`, and `docs/70-shell/shell-terminal-ideas.md` with **place cards**, **verb ledgers**, **affordance lenses**, and **why-not drawers** worth stealing for a future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md` and `docs/90-inspirations/inspirations-mapped.md` with sharper lessons from Android document IDs/flags, Linux `O_PATH`, Capsicum rights, Fuchsia namespace/rights, and HTTP `Allow` affordance advertisement.
- expanded bibliography and moving-head source tracking, refreshed the external review queue, regenerated the context pack and release manifest, and kept lint clean for the new revision.

## What Revision 074 adds
- `rfcs/0067-viewfs-keep-gesture-evidence-activation-tokens-armed-state-active-control-and-receipts-separate.md` so fresh gesture proof, transferable activation batons, armed/enabled interaction state, active control, and durable receipts/history stay visibly distinct.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/90-inspirations/slopos-datacube-evaluation.md` with the new interaction-proof / active-control seam and a sharper evaluation of what SlopOS capture/attention posture does and does not settle.
- refreshed `docs/70-shell/shell-terminal-protocol-sketch.md` and `docs/70-shell/shell-super-awesome-moves.md` with **activation baton chips**, **arming rails**, and **foreground-transfer cards** worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with HTML / Wayland / XDG portal / Win32 foreground-transfer precedents, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 071 adds
- `rfcs/0064-viewfs-keep-query-manifests-result-snapshots-live-feeds-materialized-collections-live-binds-and-receipts-separate.md` to keep saved smart-query recipes, frozen hit sets, live feeds, materialized local collections, current binds, and durable receipts on different seams.
- stronger query/smart-folder notes around `freeze to basket`, `query-versus-basket drift`, and explicit `bound here` truth.
- refreshed SlopOS datacube evaluation, inspiration mapping, bibliography/source-tracking, assurance registries, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 069 adds
- `rfcs/0062-viewfs-keep-provenance-attestations-endorsement-bundles-local-admission-verdicts-live-handles-and-receipts-separate.md` so provenance claims, endorsement bundles/trust-root inputs, local admission verdicts, live handles, and durable receipts/history stay visibly distinct.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/90-inspirations/slopos-datacube-evaluation.md` with the new provenance-versus-admission seam and a sharper evaluation of what SlopOS attestation / endorsement / document-portal posture does and does not settle.
- refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-ideas.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with **provenance ribbons**, **endorsement stacks**, **verdict shutters**, and **why-runnable** shell ideas that keep claim/endorsement/admission separate from live authority.
- expanded bibliography and moving-head source tracking with RATS / in-toto / SLSA / TUF / Sigstore precedents for keeping claim, endorsement, local appraisal, and live authority separate, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 068 adds
- `rfcs/0061-viewfs-keep-permission-outlooks-revival-designators-live-handles-death-state-verdicts-and-receipts-separate.md` so permission outlook, later revival designators, current live handles, explicit death-state verdicts, and durable receipts/history stay visibly distinct.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/revocation-and-durable-grants-design-space.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/90-inspirations/slopos-datacube-evaluation.md` with the new permission-versus-liveness seam and a sharper evaluation of what SlopOS document/lease/powerbox posture does and does not settle.
- refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-ideas.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with **permission lights**, **death certificates**, **repair ladders**, and **preflight gutters** worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with W3C Permissions / File System Access precedents for explicit permission-state and repairable liveness UI, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 065 adds
- `rfcs/0058-viewfs-keep-transfer-offers-live-handle-copies-revival-designators-adopted-binds-and-receipts-separate.md` so a transfer/courier offer, a live copied handle, a later revival designator, a receiver-local adopted bind, and durable history cannot silently collapse into one vague `shared/opened` story.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/30-architecture/architecture-overview.md` with a sharper handoff/adoption seam: offer/courier event vs accepted representation vs live authority now vs later revival vs local bind vs receipt/history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with transfer sheets, adoption rails, issuer/courier witness chips, and `offer-only` versus `adopted-here` shell truth ideas for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, evidence index, context-pack coverage, and release manifest for the new revision.

## What Revision 059 adds
- `rfcs/0052-viewfs-keep-object-identity-parent-anchors-namespace-mutations-and-receipts-separate.md` so an object, the source parent anchor, the destination parent anchor, the reviewed namespace mutation, and durable history cannot silently collapse into one vague `move/open` story.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md` and `docs/30-architecture/slopos-seam-map.md` with a sharper namespace-mutation seam: object identity vs source parent vs destination parent vs rename/link/replace/exchange act vs mutation receipt/history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with two-anchor rename cards, overwrite/exchange ladders, and name-diff receipts for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, evidence index, context-pack coverage, and release manifest for the new revision.

## What Revision 058 adds
- `rfcs/0051-viewfs-keep-current-handles-launch-inheritance-child-slots-and-launch-receipts-separate.md` so a handle held in the current pane, its launch-boundary inheritance posture, the exact child slot that receives a copy, and durable launch history cannot silently collapse into one vague `passed to child` story.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md` and `docs/30-architecture/slopos-seam-map.md` with a sharper launch-inheritance seam: held-now vs launch-shuttered/eligible vs exact child slot vs launch receipt/history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with inheritance shutters, child-slot maps, launch-boundary diffs, and authority-leak sirens for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, evidence index, context-pack coverage, and release manifest for the new revision.

## What Revision 057 adds
- `rfcs/0050-viewfs-keep-locator-handles-byte-io-handles-and-durable-refs-separate.md` so locator/metadata handles, live byte-I/O handles, reopen/escalation acts, and durable history cannot silently collapse into one vague open row.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md` and `docs/30-architecture/slopos-seam-map.md` with a sharper handle-class seam: locate/inspect/walk versus live byte I/O versus reopen/escalation versus durable ref/history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with handle-class badges, inspect-first cards, and open-for-more-power ladders for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, evidence index, context-pack coverage, and release manifest for the new revision.

## What Revision 056 adds
- `rfcs/0049-viewfs-keep-handle-slots-live-handle-copies-shared-open-state-and-independent-reopens-separate.md` so an exact child handle slot, a live copied handle, a shared open-state/cursor/lock group, an independent reopen, and durable history cannot silently collapse into one vague handle row.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md` and `docs/30-architecture/slopos-seam-map.md` with a sharper handle-topology seam: slot/local binding vs live alias vs shared open state vs fresh reopen vs history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with twin-handle badges, duplicate-versus-reopen ladders, and shared-open-state drawer ideas for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, evidence index, context-pack coverage, and release manifest for the new revision.

## What Revision 055 adds
- `rfcs/0048-viewfs-keep-exec-objects-runners-bootstrap-posture-and-live-sessions-separate.md` so the thing selected to run, the runner/runtime that hosts it, bootstrap posture, the resulting live session, and durable history cannot silently collapse into one vague run row.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md` and `docs/30-architecture/slopos-seam-map.md` with a sharper launch-hosting seam: exec object vs runner/runtime vs bootstrap posture vs live session vs history.
- expanded `docs/70-shell/shell-super-awesome-moves.md` and `docs/70-shell/shell-terminal-protocol-sketch.md` with runner badges, bootstrap shutters, and mutable-prompt-dock ideas for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, context-pack coverage, and release manifest for the new revision.

## What Revision 054 adds
- `rfcs/0047-viewfs-keep-live-process-handles-terminal-streams-controlling-tty-and-foreground-turns-separate.md` so a running command, its stream lanes, its controlling-terminal posture, its foreground input/signal turn, and durable history cannot silently collapse into one fake `attached terminal` story.
- refreshed `docs/30-architecture/observe-attach-control-and-sideband-lanes.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper live-session seam: process handle vs stream lane vs controlling tty vs foreground baton vs history.
- expanded `docs/70-shell/follow-tails-attach-rails-and-control-panes.md`, `docs/70-shell/shell-super-awesome-moves.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with foreground-baton pills, tty-lease badges, and interrupt-preview ideas for the future custom shell+terminal.
- deepened `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, context-pack coverage, evidence index, and release manifest for the new revision.

## What Revision 053 adds
- `rfcs/0046-viewfs-keep-selection-owners-offers-pasted-input-and-imported-objects-separate.md` so current selection ownership, offered representations, pasted prompt bytes, imported objects, and durable receipts cannot silently collapse into one magical clipboard/open story.
- refreshed `docs/30-architecture/imports-exports-transfers-and-promised-files.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and `docs/30-architecture/slopos-seam-map.md` with a sharper transfer/clipboard seam: owner/source vs offer vs accepted representation vs pasted input vs imported object.
- expanded `docs/70-shell/shipping-lanes-boundary-previews-and-promised-outputs.md`, `docs/70-shell/shell-super-awesome-moves.md`, and `docs/70-shell/shell-terminal-protocol-sketch.md` with clipboard-offer cards, MIME truth, and paste-versus-import ladders for the future custom shell+terminal.
- refreshed `docs/90-inspirations/slopos-datacube-evaluation.md`, `docs/90-inspirations/inspirations-mapped.md`, bibliography/review tracking, context pack coverage, evidence index, and release manifest for the new revision.

## What Revision 052 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **exact executable objects versus exact startup code closure** so ViewFS can steal loader-history lessons without freezing a loader/runtime mechanism too early.
- refreshed `docs/30-architecture/slopos-seam-map.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and added `rfcs/0045-viewfs-keep-exec-objects-startup-code-closure-loader-policy-and-late-imports-separate.md` so exec objects, startup code closure, loader/search posture, late plugin/import lanes, and launch/history artifacts stay visibly distinct while SlopOS remains in design.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with **closure-certainty badges**, **loader-debt warnings**, and **late-import route sheets** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head tracking with `ld.so`, `dlopen`, Windows DLL search order, and `LoadLibrary` precedents, refreshed the external review queue, repaired lint/context-pack coverage for RFCs 0044 and 0045, and regenerated the context pack and release manifest for the new archive.

## What Revision 051 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **exact executable objects** and **activation-time startup credentials** so ViewFS can steal launch-by-handle ideas without collapsing them into path folklore, env folklore, or generic durable authority.
- refreshed `docs/30-architecture/slopos-seam-map.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and added `rfcs/0044-viewfs-keep-exec-objects-startup-credentials-and-launch-basis-separate.md` so exec objects, script/interpreter entry, argv/env basis, startup credential slots, and launch/history artifacts stay visibly distinct while SlopOS remains in design.
- refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-protocol-sketch.md`, and `docs/90-inspirations/inspirations-mapped.md` with **launch basis cards**, **credential drawers**, and **exact-exec-object badges** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head tracking with `fexecve`, `execveat`, and systemd credential precedents, refreshed the external review queue, and regenerated the context pack and release manifest for the new archive.

## What Revision 048 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **exact running-process identity** so ViewFS can steal process-descriptor ideas without collapsing them into transcript folklore or broad debugger power.
- refreshed `docs/30-architecture/slopos-seam-map.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and added `rfcs/0042-viewfs-keep-command-packets-live-process-handles-control-rights-and-deep-inspection-separate.md` so command packets, live process handles, lifecycle-control rights, deeper inspection rights, and history rows stay visibly distinct while SlopOS remains in design.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with **live process cards**, **right badges**, and **running-versus-history truth transitions** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head tracking with Linux pidfd and FreeBSD procdesc precedents, refreshed the external review queue, and regenerated the context pack and release manifest for the new archive.

# ViewFS living archive

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md).

Revision notes: [`CHANGELOG.md`](CHANGELOG.md).

This repo is a **living archive** for designing **ViewFS**, a capability-native storage and namespace substrate for SlopOS built around four pillars:
- immutable-first object storage,
- capability handles,
- explicit per-process views,
- portal-mediated imports/exports.

This archive is intentionally **design-phase first**. It records guardrails, lessons, open questions, and staged build order before heavy implementation lock-in.

A newer guardrail now matters too: binding a workspace tree should stay separate from trusting that workspace to run its own tasks, env hooks, notebook cells, debug launchers, or agents. Previewing and extracting should stay separate from open/execute/trust as well. Watching and auto-refresh should stay advisory and rebuild-friendly instead of posing as perfect truth or authority. Link-like things should stay class-aware too: a live handle, local alias, durable reopen ref, launch route, and transcript receipt should not collapse into one clickable fiction. Delete-like actions need the same discipline: unbinding a name, moving something to trash, retaining it because of an explicit root, and actually purging it are different seams. Time-travel features need it too: a local checkpoint, a writable fork, a replicated backup stream, a publish candidate, and an activation target should not collapse into one magical “snapshot” word. Concurrent-write coordination needs the same discipline too: expected-old preconditions, create-if-absent guards, short reservations, ownership hints, conflict receipts, and explicit takeovers should not collapse into one vague lock bit. Smart queries need it too: a saved query manifest, a current result snapshot, a live update feed, and a smart-folder UI surface should not collapse into one magical query object. Cross-boundary object workflows need the same discipline: import/copy-in, open-in-place, save/export, move/rehome, transfer, share/delegate, and promised-file materialization should not collapse into one generic file operation. Warm-state and offline workflows need it too: prefetch hints, caches, hydrated closures, pins, mirrors, and offline bundles should not collapse into one vague download/cache state. Grouped authority needs the same discipline too: a bundle, a view fragment, a live workspace bind, a child launch kit, and a historical receipt should not collapse into one magical convenience object. Mediated import workflows need the same discipline too: a request object, chooser-owned candidate set, selected result, minted grant/ref, live bind, and historical receipt should not collapse into one magical “opened object”. Prepared action workflows need it too: user intent, route plan, approval checkpoint, committed execution, and result receipt should not collapse into one magical shell action either. Saved automation needs the same discipline too: an externally suggested recipe, a promoted user-owned workflow, a prepared run plan, a committed run, and a historical receipt should not collapse into one magical saved command. Borrowed authority needs it too: a lend request, a live borrowed handle set, a durable delegated ref, an issuer-side recall/expiry control, and a loan-end receipt should not collapse into one magical shared handle. Reuse and renewal need the same discipline too: a past success, exact prior basis, current drift verdict, fresh reconsent, renewed authority, and new receipt should not collapse into one magical replay object. Explanation material needs it too: admissible witness packs, caveat sets, freshness/consistency witnesses, why-records, and durable receipts should not collapse into one magical justification object. Policy-aware shelling needs the same discipline too: validation/schema material, authoritative policy/caveat material, shell advice/ranking, per-decision diagnostics, and durable logs/receipts should not collapse into one magical policy helper. Policy-family choice needs the same discipline too: policy family/catalog choice, exact authoritative cut/consistency posture, fallback candidates, repair proposals, and selection receipts/history should not collapse into one magical judge-switching helper. Proposal-driven recovery needs one more seam too: proposal origin/source, proposal lane/scope, escalation requests, authoritative adoptions, and adoption receipts/history should not collapse into one magical helper-lane either. Scope-control recovery needs one more seam after that: deny ceilings, scope-eligibility rules, narrowing transforms, escalation attempts, and adoption receipts/history should not collapse into one magical permission helper either. Source layering needs one more seam after that: owner/org policy, trust-state gates, user/profile preferences, workspace/imported helper material, effective active state, and durable receipts/history should not collapse into one hidden settings blob either. Authoring discipline needs one more seam after that: author classes, carriers/containers, trust gates, advisory-only helper sources, effective active state, and durable receipts/history should not collapse into one hidden trust tunnel either. Protected authorability needs one more seam after that: protected-only state, invoke-only helper material, trust-gated adoption lanes, effective active state, and durable receipts/history should not collapse into one hidden auto-apply tunnel either. Helper lifecycle needs one more seam after that too: publisher trust, installed helper packages, configured servers/tools, enabled state, start approvals, live sessions, request-scoped selections, and durable receipts/history should not collapse into one magical installed helper either. Helper feature kinds need one more seam after that too: resources, prompts, tools, interactive apps, completion suggestions, request-bound attachments, live invocations/results, and durable receipts/history should not collapse into one magical helper item either. Deferred work needs one more seam after that too: immediate requests, accepted task wrappers, live progress/status, input-needed checkpoints, deferred final results, and durable receipts/history should not collapse into one magical background job either. Deferred control needs one more seam after that too: close/cancel acts, force termination, detach/delete acts, retry-fresh acts, reset/fork/attach acts, and durable receipts/history should not collapse into one magical stop-or-rerun menu either. Live-session ergonomics need one more seam after that too: read-only observe/query/follow lanes, interactive attach lanes, control-message lanes, injected exec/debug lanes, sideband tunnel/forward lanes, and durable transcripts/history should not collapse into one magical connected session either.

## How to navigate
0. Mile-high map: [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
0.5 Editing runbook: [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
1. Threat model assumptions: [`docs/10-threat-model/assumption-registry.md`](docs/10-threat-model/assumption-registry.md)
2. Assurance framing: [`docs/20-assurance/`](docs/20-assurance/)
3. Architecture: [`docs/30-architecture/`](docs/30-architecture/)
4. Shell / terminal ideas: [`docs/70-shell/shell-terminal-ideas.md`](docs/70-shell/shell-terminal-ideas.md)
5. Inspirations mapped to ViewFS: [`docs/90-inspirations/inspirations-mapped.md`](docs/90-inspirations/inspirations-mapped.md)
5.5 SlopOS datacube evaluation for ViewFS: [`docs/90-inspirations/slopos-datacube-evaluation.md`](docs/90-inspirations/slopos-datacube-evaluation.md)
6. Proposal track: [`rfcs/`](rfcs/)

## Archive discipline
- Cite with REF-IDs; register internal artifacts as EVID-IDs.
- Prefer editing existing docs over spraying new files.
- Keep Phase 1 claims narrow. Explicit non-claims live in [`docs/20-assurance/non-claims.md`](docs/20-assurance/non-claims.md).
- Keep mutable external sources reviewable through [`docs/00-meta/external-source-head-register.md`](docs/00-meta/external-source-head-register.md).
- Ship a compact release manifest so each archive revision can be diffed and trusted mechanically.

## What Revision 067 adds
- `rfcs/0060-viewfs-keep-caveat-sets-membrane-leases-live-handles-and-receipts-separate.md` so declared caveat sets, enforced membrane/lease proxies, current live handles, later revival designators, and durable receipts/history stay visibly distinct.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/rights-attenuation-and-bundles.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/90-inspirations/slopos-datacube-evaluation.md` with the new caveat-versus-enforcement seam and a sharper evaluation of what SlopOS D-LEASE / CH-CAPX / capability-semantics posture does and does not settle.
- refreshed `docs/70-shell/shell-super-awesome-moves.md`, `docs/70-shell/shell-terminal-ideas.md`, `docs/70-shell/shell-terminal-protocol-sketch.md`, and `docs/90-inspirations/inspirations-mapped.md` with **caveat laminates**, **membrane badges**, **expiry gutters**, and **renew/revalidate/adopt ladders** worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with macaroons / zcap / seL4 / Capsicum / Fuchsia precedents for keeping declared caveats separate from enforced attenuation, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.


## What Revision 047 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **courier provenance** and **structured command packets** so ViewFS can steal exact local-transfer and escalation patterns without collapsing them into object identity, durable receipts, or transcript folklore.
- refreshed `docs/30-architecture/slopos-seam-map.md` and `docs/30-architecture/design-splits-and-non-decisions.md` so peer witnesses, transferred live handles, structured command packets, plain transcript rows, and durable receipts stay visibly distinct while SlopOS is still moving.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with **peer-witness courier drawers** and **explicit command-packet promotion** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with Linux peer-credential / SO_PASSCRED and VS Code structured terminal-command attachment precedents, then refreshed the external review queue.
- repaired a small repo-hygiene gap by bringing `rfcs/0041-viewfs-keep-activation-carriers-badged-handle-copies-and-object-identity-separate.md` into lint/context-pack coverage, then regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 046 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **activation kits** and **issuer-visible handle copies** so ViewFS can steal explicit startup delivery without collapsing it into durable identity, durable reopen, or hidden rediscovery.
- refreshed `docs/30-architecture/slopos-seam-map.md`, `docs/30-architecture/design-splits-and-non-decisions.md`, and added `rfcs/0041-viewfs-keep-activation-carriers-badged-handle-copies-and-object-identity-separate.md` so activation slots, live handle copies, issuer badges, immutable object refs, and receipts stay visibly distinct.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with **activation-kit cards**, **truth-grade command blocks**, **selection packets / primary target**, and **badged-handle drawer** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with seL4 badged-capability, systemd socket-activation, and VS Code shell-integration precedents, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 045 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now adds a new low-regret seam around **transient exact-byte staging capsules** so ViewFS can steal commit-last / courier-exactly ideas without collapsing them into durable storage or durable reopen.
- refreshed `docs/30-architecture/slopos-seam-map.md` and `docs/30-architecture/design-splits-and-non-decisions.md` so staged capsules, couriered live handles, committed objects, and durable reopen refs stay visibly distinct while SlopOS is still moving.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with **sealed-capsule**, **handle-courier**, and **commit-last rail** ideas worth stealing for a future custom shell+terminal.
- expanded bibliography and moving-head source tracking with Linux memfd/file-seal and explicit fd-courier precedents, then refreshed the external review queue.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 044 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now goes one step further on the current SlopOS datacube by treating restart-stable exact-handle continuity and provider-declared action surfaces as ideas to steal carefully without freezing broad persistence or UI contracts.
- refreshed `docs/30-architecture/slopos-seam-map.md` and `docs/30-architecture/design-splits-and-non-decisions.md` so resumable lane lockers, durable reopen refs, persistent roots, object identity, current placement, and advertised operations stay visibly distinct.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with handle-locker, resumable-lane, exact-action-menu, and provider-flag shell ideas worth stealing for a future custom shell+terminal.
- refreshed bibliography and moving-head source tracking with a systemd file-descriptor-store precedent and re-reviewed Android/terminal sources that remain hot-moving.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 043 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now reads the current SlopOS datacube through a new continuity lens: narrow escrow/resume should stay separate from durable reopen and persistent authority.
- refreshed `docs/30-architecture/slopos-seam-map.md` and `docs/30-architecture/design-splits-and-non-decisions.md` so continuity/escrow, durable reopen, persistent roots, and queued follow-up control stay visibly distinct while SlopOS is still moving.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with trusted-review-lane, collapsible-command-section, steering-rail, and structured-object-drawer ideas that make the terminal richer without lying about authority.
- extended bibliography and moving-head review tracking with current Fuchsia idle-stop and VS Code terminal-section precedents.
- regenerated the context pack and release manifest for the new revision.

## What Revision 042 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` now goes deeper on the SlopOS datacube itself by reading CapStore, AttrFS, and Capshell as low-regret seam lessons for ViewFS instead of as mechanisms to freeze immediately.
- refreshed `docs/30-architecture/slopos-seam-map.md` and `docs/30-architecture/design-splits-and-non-decisions.md` so immutable storage, optional durable roots, durable reopen, snapshot query, live feeds, and ambient inventory stay visibly distinct.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` and `docs/90-inspirations/inspirations-mapped.md` with pane-var, semantic-zone, prompt-local, semantic-history, and persistence/query lessons worth stealing for a future custom shell+terminal.
- repaired bibliography hygiene by adding missing referenced sources already used by the archive, plus CapROS and TreeSLS persistence references, and updated moving-head source tracking accordingly.
- regenerated the context pack and release manifest for the new revision.

## What Revision 041 adds
- `docs/90-inspirations/slopos-datacube-evaluation.md` to capture a fresh decision-light evaluation of what ViewFS should copy now from the uploaded SlopOS datacube, what it should only copy lightly, what it should postpone, and which shell/terminal moves are promising without freezing them.
- refreshed non-decision guidance in `docs/30-architecture/design-splits-and-non-decisions.md` so immutable identity, mutable heads, creator-populated namespaces, request/selection/grant/bind, and compat debt stay visibly separate while SlopOS is still moving.
- refreshed `docs/70-shell/shell-super-awesome-moves.md` with semantic-inspector, restricted-mode, typed-link, and prompt-local click ideas that keep terminal delight subordinate to authority truth.
- refreshed `docs/90-inspirations/inspirations-mapped.md`, bibliography, and external-source review tracking with another pass through portal, capability, terminal, trust, and transfer precedents.
- tightened repo hygiene by bringing inspiration docs into the context pack and lint requirements, and by requiring the Revision 040 live-session seam files that earlier lint rules forgot to enumerate.
- regenerated the context pack, evidence index, and release manifest for the new revision.

## What Revision 040 adds
- `docs/30-architecture/observe-attach-control-and-sideband-lanes.md` to keep read-only observe/query/follow lanes, interactive attach lanes, control-message lanes, injected exec/debug lanes, sideband tunnel/forward lanes, and durable transcripts on distinct seams.
- `docs/70-shell/follow-tails-attach-rails-and-control-panes.md` to collect shell ideas around follow tails, attach rails, control panes, debug launch drawers, sideband badges, and live-session receipts.
- `rfcs/0040-viewfs-keep-observe-attach-control-and-sideband-lanes-separate.md` so future design work must classify whether it is changing observe/query, interactive attach, control-message, exec/debug, sideband, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 039 adds
- `docs/30-architecture/cancel-terminate-forget-reset-and-rerun.md` to keep close/cancel acts, force termination, detach/delete acts, retry-fresh acts, reset/fork/attach acts, and durable receipts on distinct seams.
- `docs/70-shell/stop-ladders-detach-rails-and-rerun-forks.md` to collect shell ideas around stop ladders, detach rails, termination fuses, retry-vs-fork drawers, result-retention lockers, and stop receipts.
- `rfcs/0039-viewfs-keep-cancel-terminate-forget-reset-and-rerun-separate.md` so future design work must classify whether it is changing close/cancel, termination, detach/delete, retry-fresh, reset/fork/attach, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 038 adds
- `docs/30-architecture/requests-tasks-progress-and-results.md` to keep immediate requests, accepted task wrappers, live progress/status, input-required checkpoints, deferred final results, and durable receipts on distinct seams.
- `docs/70-shell/task-badges-progress-lanes-and-result-lockers.md` to collect shell ideas around task badges, progress lanes, input-required drawers, queue rails, result lockers, and task receipts.
- `rfcs/0038-viewfs-keep-requests-tasks-progress-and-results-separate.md` so future design work must classify whether it is changing immediate request submission, accepted task wrappers, live progress, input checkpoints, deferred result retrieval, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 037 adds
- `docs/30-architecture/resources-prompts-tools-apps-and-bindings.md` to keep helper-exposed resources, prompts, tools, app surfaces, completion suggestions, request-bound attachments, live invocation/results, and durable receipts on distinct seams.
- `docs/70-shell/resource-shelves-prompt-chips-tool-racks-and-app-docks.md` to collect shell ideas around resource shelves, prompt chips, tool racks, app docks, completion popovers, binding trays, and invocation receipts.
- `rfcs/0037-viewfs-keep-resources-prompts-tools-apps-and-bindings-separate.md` so future design work must classify whether it is changing feature catalogs, completion hints, request bindings, live invocations/results, or only durable history.
- fixed a small repo hygiene gap by adding missing helper-lifecycle assurance entries before layering the new helper-feature seam on top.
- refreshed architecture notes, SlopOS seam mapping, shell idea docs, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## Current thesis
ViewFS should **not** begin as “our ext4.”

The first viable slice is:
1. immutable object store,
2. handle-based object model,
3. explicit process view root,
4. portal import/export seams,
5. path compatibility as a subordinate membrane.


## What Revision 036 adds
- `docs/30-architecture/publisher-trust-helper-installs-and-live-sessions.md` to keep publisher trust, installed helper packages, configured helper/server definitions, enabled state, start approvals, live sessions, request-scoped selections, and durable receipts on distinct seams.
- `docs/70-shell/publisher-badges-start-gates-and-tool-racks.md` to collect shell ideas around publisher badges, installed cards, start-gate drawers, live-session beacons, tool racks, trust-reset sparks, and lifecycle receipts.
- `rfcs/0036-viewfs-keep-publisher-trust-helper-installs-and-live-sessions-separate.md` so future design work must classify whether it is changing publisher trust, install/config state, enablement, start approvals, live sessions, request-scoped selections, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 035 adds
- `docs/30-architecture/protected-scopes-authorability-and-invocation-lanes.md` to keep protected-authorable state, carrier/discovery presence, invoke-only helper material, trust-gated adoption lanes, effective active state, and durable receipts on distinct seams.
- `docs/70-shell/protected-badges-authorability-matrices-and-latched-invokes.md` to collect shell ideas around protected chips, authorability matrix drawers, latched invokes, broker badges, and invoke-vs-adopt receipt cards.
- `rfcs/0035-viewfs-keep-protected-scopes-authorability-and-invocation-lanes-separate.md` so future design work must classify whether it is changing protected-only state classes, invoke-only helpers, adoption lanes, effective active state, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 034 adds
- `docs/30-architecture/policy-authors-carriers-and-advisory-sources.md` to keep author classes, carriers/containers, trust gates, advisory-only helper sources, effective active state, and durable receipts on distinct seams.
- `docs/70-shell/author-badges-carrier-tags-and-advisory-rails.md` to collect shell ideas around author badges, carrier tags, advisory-only rails, trust-tunnel warnings, and authorability fuse drawers.
- `rfcs/0034-viewfs-keep-policy-authors-carriers-and-advisory-sources-separate.md` so future design work must classify whether it is changing author classes, carrier classes, trust gates, advisory-only rails, effective active state, or only durable history.
- refreshed architecture notes, shell notes, SlopOS seam mapping, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 033 adds
- `docs/30-architecture/policy-sources-trust-gates-and-precedence.md` to keep owner/org policy sources, trust-state gates, user/profile preferences, workspace/imported proposal sources, effective active state, and durable receipts on distinct seams.
- `docs/70-shell/origin-stacks-trust-shutters-and-override-ledgers.md` to collect shell ideas around origin stacks, trust shutters, import quarantine trays, winner chips, and override ledgers.
- `rfcs/0033-viewfs-keep-policy-sources-trust-gates-and-precedence-separate.md` so future design work must classify whether it is changing authoritative policy sources, trust-state gating, lower-precedence preferences, imported helper material, effective active state, or only durable history.
- refreshed architecture notes, shell notes, SlopOS seam mapping, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 032 adds
- `docs/30-architecture/deny-ceilings-narrowing-and-scope-eligibility.md` to keep deny ceilings, scope-eligibility rules, narrowing transforms, escalation attempts, and durable adoption receipts on distinct seams.
- `docs/70-shell/ceiling-pills-narrowing-previews-and-scope-fuses.md` to collect shell ideas around ceiling pills, narrowing previews, scope fuses, adopt-the-narrowest-safe-rung, and honest receipt-only outcomes.
- `rfcs/0032-viewfs-keep-deny-ceilings-narrowing-and-scope-eligibility-separate.md` so future proposals must classify whether they are changing authoritative ceilings, authoritative scope eligibility, narrowing transforms, escalation interactions, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 031 adds
- `docs/30-architecture/proposers-lanes-escalations-and-adoptions.md` to keep proposal origins, proposal scopes, escalation requests, authoritative adoptions, and durable adoption receipts on distinct seams.
- `docs/70-shell/proposer-badges-escalation-ladders-and-adoption-gates.md` to collect shell ideas around proposer badges, scope chips, escalation ladders, adoption gates, and decline/adoption receipt cards.
- `rfcs/0031-viewfs-keep-proposers-lanes-escalations-and-adoptions-separate.md` so future design work must classify whether it is changing proposal sources, proposal scopes, escalation interactions, authoritative adoptions, or only durable adoption history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 030 adds
- `docs/30-architecture/policy-families-cuts-fallbacks-and-repair.md` to keep policy-family/catalog choice, exact authoritative cuts, fallback candidates, repair proposals, and durable selection receipts on distinct seams.
- `docs/70-shell/cut-pickers-fallback-rails-and-repair-prompts.md` to collect shell ideas around policy cut pickers, fallback rails, repair prompts, consistency badges, and selection receipt chips.
- `rfcs/0030-viewfs-keep-policy-families-cuts-fallbacks-and-repair-separate.md` so future design work must classify whether it is changing policy-family choice, exact cuts, fallback candidates, repair proposals, or only durable selection history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 029 adds
- `docs/30-architecture/schemas-policies-advice-diagnostics-and-decision-logs.md` to keep validation/schema material, authoritative policy/caveat material, shell advice rails, decision diagnostics, and durable logs/receipts on distinct seams.
- `docs/70-shell/policy-lenses-advice-rails-and-decision-traces.md` to collect shell ideas around policy lenses, advice rails, diagnostic cards, and audit-trace chips.
- `rfcs/0029-viewfs-keep-schemas-policies-advice-diagnostics-and-decision-logs-separate.md` so future design work must classify whether it is changing validation material, policy material, shell advice, decision diagnostics, or only durable logs/history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 028 adds
- `docs/30-architecture/witness-packs-caveats-freshness-and-why-records.md` to keep admissible witness material, caveat sets, freshness/consistency witnesses, why-records, and durable receipts on distinct seams.
- `docs/70-shell/caveat-chips-witness-drawers-and-why-panels.md` to collect shell ideas around witness drawers, caveat chips, freshness badges, and why panels.
- `rfcs/0028-viewfs-keep-witness-packs-caveats-freshness-and-why-records-separate.md` so future design work must classify whether it is changing witness material, caveats, freshness evidence, why-records, or only durable history.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspirations, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 027 adds
- `docs/30-architecture/basis-records-drift-checks-and-reconsent.md` to keep prior reuse candidates, exact basis records, present drift checks, fresh reconsent checkpoints, renewed artifacts, and reuse receipts on distinct seams.
- `docs/70-shell/basis-diffs-reconsent-ladders-and-renewal-guards.md` to collect shell ideas around basis diff drawers, reconsent ladders, renewal strip knobs, watched-input chips, and typed reuse result cards.
- `rfcs/0027-viewfs-keep-basis-records-drift-checks-and-reconsent-separate.md` so future design work must classify whether it is changing reuse candidates, basis records, drift checks, reconsent checkpoints, renewed artifacts, or only history/receipts.
- refreshed architecture notes, SlopOS seam mapping, shell protocol/ideas, inspirations, bibliography/review tracking, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 026 adds
- `docs/30-architecture/loans-delegations-recalls-and-expiry.md` to keep lend requests, live borrowed authority, durable delegated refs, issuer-side recall/expiry controls, and loan-end receipts on distinct seams.
- `docs/70-shell/lend-once-drawers-borrow-badges-and-recall-rails.md` to collect shell ideas around lend-once drawers, borrowed-authority badges, expiry rails, recall cards, and promote-from-borrow flows.
- `rfcs/0026-viewfs-keep-loans-delegations-recalls-and-expiry-separate.md` so future design work must classify whether it is changing borrow requests, live loans, durable delegated refs, issuer-side recall/expiry controls, or only history/receipts.
- refreshed architecture notes, SlopOS seam mapping, shell ideas, inspirations, bibliography, assumptions/claims/invariants/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 025 adds
- `docs/30-architecture/suggestions-recipes-promotions-and-runs.md` to keep externally suggested automation, promoted user-owned workflows, prepared run plans, committed runs, and receipts on distinct seams.
- `docs/70-shell/suggestion-trays-promotion-lanes-and-replay-guards.md` to collect shell ideas around suggestion trays, explicit promotion, source-drift badges, notebook truth states, and replay guards.
- `rfcs/0025-viewfs-keep-suggestions-recipes-promotions-and-runs-separate.md` so future design work must classify whether it is changing suggestion sources, promotion acts, user-owned workflows, prepared plans, committed runs, or only history/receipts.
- refreshed architecture notes, shell notes, SlopOS seam mapping, inspiration map, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 024 adds
- `docs/30-architecture/intents-route-plans-approvals-and-results.md` to keep user intent, prepared route plans, approval checkpoints, committed execution, and result receipts on distinct seams.
- `docs/70-shell/route-plans-approval-checkpoints-and-result-cards.md` to collect shell ideas around route-plan cards, exact approval diffs, prepare-versus-commit, restricted-but-productive states, and result cards.
- `rfcs/0024-viewfs-keep-intents-plans-approvals-and-results-separate.md` so future design work must classify whether it is changing intent, plan, approval, execution, or only result/history surfaces.
- refreshed architecture notes, design-splits guidance, SlopOS seam mapping, shell protocol/ideas, inspiration map, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 023 adds
- `docs/30-architecture/requests-candidates-selections-and-imports.md` to keep request objects, chooser-owned candidate sets, selected outcomes, minted grants/refs, live binds, and receipts on distinct seams.
- `docs/70-shell/chooser-sheets-staging-trays-and-grant-ledgers.md` to collect shell ideas around chooser sheets, staging trays, request chips, provider-ops-aware route sheets, and grant ledgers.
- `rfcs/0023-viewfs-keep-requests-selections-grants-and-binds-separate.md` so future design work must classify whether it is changing request state, candidate/designation surfaces, selected outcomes, minted grants/refs, live binds, or only historical receipts.
- refreshed architecture notes, portal-lifecycle guidance, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 022 adds
- `docs/30-architecture/bundles-view-fragments-and-launch-kits.md` to keep grouped authority objects, namespace fragments/templates, live binds, child launch kits, and receipts on distinct seams.
- `docs/70-shell/launch-rehearsals-kit-cards-and-view-panes.md` to collect shell ideas around launch rehearsals, kit cards, pane view cards, authority diffs, and rebind-first workflows.
- `rfcs/0022-viewfs-keep-bundles-view-fragments-and-launch-kits-separate.md` so future design work must classify whether it is changing grouped authority, namespace templates, live binds, launch assembly, or only historical receipts.
- refreshed architecture notes, design-splits guidance, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 021 adds
- `docs/30-architecture/pins-caches-prefetch-and-hydration.md` to keep prefetch hints, caches, hydration acts, pins, mirrors, and offline bundles on distinct seams.
- `docs/70-shell/offline-readiness-hydration-and-pin-hygiene.md` to collect shell ideas around offline-readiness badges, hydration plans, warm-up trays, bundle lanes, and pin explain flows.
- `rfcs/0021-viewfs-keep-pins-caches-prefetch-and-hydration-separate.md` so future design work must classify whether it is changing hinting, caching, hydration, retention, mirroring, or offline-bundle semantics.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 020 adds
- `docs/30-architecture/imports-exports-transfers-and-promised-files.md` to keep import/open/save/move/transfer/share/promise lanes on distinct seams.
- `docs/70-shell/shipping-lanes-boundary-previews-and-promised-outputs.md` to collect shell ideas around boundary previews, shipping lanes, move outcome cards, and promise/materialize UX.
- `rfcs/0020-viewfs-keep-import-export-transfer-share-and-promises-separate.md` so future proposals must classify whether they are importing, opening in place, saving/exporting, moving, transferring, delegating, or only promising future materialization.
- refreshed architecture notes, SlopOS seam mapping, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 018 adds
- `docs/30-architecture/leases-preconditions-and-conflicts.md` to keep optimistic preconditions, short leases/reservations, ownership hints, conflict receipts, and explicit override acts on distinct seams.
- `docs/70-shell/reservations-preconditions-and-merge-lanes.md` to collect shell ideas around guarded saves, reservation badges, blocked-write explain panels, merge lanes, and force-with-lease style takeovers.
- `rfcs/0018-viewfs-keep-preconditions-leases-and-conflicts-separate.md` so future design work must classify whether it is changing expected-old guards, create-if-absent semantics, leases, ownership hints, conflict artifacts, or override acts.
- refreshed architecture notes, SlopOS seam mapping, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 017 adds
- `docs/30-architecture/checkpoints-clones-and-publication.md` to keep local checkpoints, writable forks/worktrees, backup/replication streams, publish candidates, and activation targets on distinct seams.
- `docs/70-shell/checkpoints-forks-and-time-travel.md` to collect shell ideas around one-keystroke checkpoints, instant forks/worktrees, truthful time-travel badges, promotion lanes, and rollback previews.
- `rfcs/0017-viewfs-keep-checkpoints-clones-backups-and-publication-separate.md` so future design work must classify whether it is changing checkpoint, fork, branch/head, replication, publication, or activation semantics.
- refreshed architecture notes, SlopOS seam mapping, bibliography/review tracking, assumptions/claims/invariants/non-claims, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 016 adds
- `docs/30-architecture/trash-retention-and-purge.md` to keep remove/unbind, trash entries, recovery history, retention roots, and purge/GC on distinct seams.
- `docs/70-shell/trash-trays-retention-lenses-and-undo.md` to collect shell ideas around trash trays, retention inspectors, purge previews, restore-plan cards, and undo timelines.
- `rfcs/0016-viewfs-keep-trash-retention-and-purge-separate.md` so future design work must classify whether it is changing names/bindings, trash state, recovery history, retention roots, or purge acts.
- refreshed architecture notes, SlopOS seam mapping, bibliography/review tracking, evidence index, context pack, lint requirements, and release manifest for the new revision.

## What Revision 014 adds
- `docs/30-architecture/links-aliases-and-shortcuts.md` to keep namespace links, durable reopen refs, route/launch shortcuts, and transcript hyperlinks separate from live authority.
- `docs/70-shell/link-lenses-breadcrumbs-and-relink.md` to collect shell ideas around link lenses, breadcrumb provenance, dead-link triage, and explicit relink/retarget flows.
- `rfcs/0014-viewfs-keep-links-aliases-and-shortcuts-separate.md` so future proposals must classify whether they are changing live handles, local names, alias objects, durable refs, routes, or only receipt surfaces.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, context pack, lint requirements, evidence index, and release manifest for the new revision.

## What Revision 013 adds
- `docs/30-architecture/watchers-notifications-and-rebuilds.md` to keep live authority, watch registrations, event feeds, rebuilt snapshots, and watch receipts on separate seams.
- `docs/70-shell/watch-blocks-and-settle-badges.md` to collect shell ideas around watch blocks, health badges, pulse cards, rebuild actions, and scoped live panes.
- `rfcs/0013-viewfs-keep-watchers-and-event-feeds-advisory.md` so future design work must classify whether it is changing authority, subscriptions, event feeds, rebuilt snapshots, or only transcript UX.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, context pack, lint requirements, evidence index, and release manifest for the new revision.

## What Revision 012 adds
- `docs/30-architecture/previews-extractors-and-observation-surfaces.md` to keep live authority, preview sessions, derived observation artifacts, and transcript receipts on separate seams.
- `docs/70-shell/peek-panes-and-inert-inspectors.md` to collect shell ideas around space-to-peek, provider badges, compare panes, authority ladders, and preview receipt cards.
- `rfcs/0012-viewfs-keep-previews-and-extractors-separate-from-authority.md` so future design work must classify whether it is changing authority, observation sessions, derived artifacts, or only transcript UX.
- refreshed architecture notes, SlopOS seam mapping, bibliography/review tracking, context pack, lint requirements, evidence index, and release manifest for the new revision.

## What Revision 011 adds
- `docs/30-architecture/workspace-trust-and-automation-gates.md` to keep workspace/tree access, inert workspace metadata, workspace-defined automation, and user/global automation on distinct seams.
- `docs/70-shell/workspace-onboarding-and-trust-badges.md` to collect shell ideas around browse-first workspace opening, trust badges, automation manifests, reapproval diffs, and user-vs-workspace workflows.
- `rfcs/0011-viewfs-keep-workspace-access-separate-from-workspace-trust.md` so future proposals must classify whether they are granting access to a workspace tree or permission to execute workspace-defined automation.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 010 adds
- `docs/30-architecture/indexes-recents-and-selectors.md` to keep indexes, recents, query registries, and selector rows advisory rather than identity- or authority-bearing.
- `docs/70-shell/palette-selectors-and-provenance-lenses.md` to collect palette/omnibox ideas around provenance peeks, typed selector rows, and action truth badges.
- `rfcs/0010-viewfs-keep-indexes-recents-and-palettes-advisory.md` so future design work must classify registry/search surfaces separately from handles, refs, receipts, and names.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 009 adds
- `docs/30-architecture/session-state-and-authority.md` to keep saved shell state, pane/workspace memory, notebooks, and workflows from silently counting as live authority.
- `docs/70-shell/journals-notebooks-and-safe-replay.md` to collect shell ideas around journals, notebooks, workflows, typed palette rows, and safe replay modes.
- `rfcs/0009-viewfs-keep-session-state-and-authority-separate.md` so future proposals must classify saved state separately from live handles, durable refs, and receipts.
- refreshed architecture notes, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, context pack, lint requirements, and release manifest for the new revision.

## What Revision 008 adds
- `docs/30-architecture/handles-refs-and-receipts.md` to keep live handles, durable reopen refs, and transcript receipts on distinct seams.
- `docs/70-shell/authority-hud-and-receipt-cards.md` to collect shell ideas around visible authority summaries, compact receipt cards, safe transcript sharing, and honest replay/rebind UX.
- `rfcs/0008-viewfs-keep-handles-refs-and-receipts-separate.md` so future proposals must classify whether they are changing live authority, durable reopen, or transcript/audit artifacts.
- refreshed portal lifecycle notes, shell protocol ideas, SlopOS seam mapping, inspirations, bibliography/review tracking, assumptions/claims/non-claims, evidence index, context pack, and release hygiene for the new research pass.

## What Revision 007 adds
- `docs/30-architecture/object-identity-recents-and-reveal.md` to keep immutable object IDs, view-local names, durable reopen handles, workspace binds, and reveal/launch routes from collapsing into one primitive.
- `docs/70-shell/semantic-marks-links-and-overlays.md` to collect shell/terminal ideas around prompt marks, typed object links, inspect overlays, and honest recent-item states.
- `rfcs/0007-viewfs-keep-identity-recents-and-reveal-separate.md` so future design work must classify whether it is changing identity, naming, reopen, workspace binding, or routing.
- refreshed architecture notes, SlopOS seam mapping, shell protocol sketches, inspirations, bibliography/review tracking, and release hygiene for the new research pass.

## What Revision 006 adds
- `docs/30-architecture/workspace-grants-and-rebinding.md` to keep workspace/tree binds distinct from single opens, transfer receipts, durable recents, and generic URI launch.
- `docs/70-shell/truthful-completions-and-routing.md` to push the shell toward authority-aware suggestions, truthful previews, typed routing, and receipt-aware palette UX.
- `rfcs/0006-viewfs-separate-workspace-grants-from-recents-and-openuri.md` so future design work has to classify chooser/open/rebind/reopen/reveal flows instead of collapsing them into generic “open”.
- refreshed SlopOS seam mapping, architecture notes, portal-grant notes, inspiration map, bibliography/review surfaces, and release hygiene for the new research pass.

## What Revision 005 adds
- `docs/30-architecture/host-bridge-and-backstop-posture.md` to keep preopen adapters, rooted host path walkers, ambient-authority escape hatches, and Linux sandboxing clearly subordinate to actual ViewFS semantics.
- stronger portal-grant notes distinguishing open/import, transfer, save/export, durable reopen, and bound-workspace grants without freezing a final schema.
- `docs/70-shell/shell-super-awesome-moves.md` to collect genuinely exciting shell/terminal product ideas that still keep authority honest.
- a tighter SlopOS seam map around OpenURI/reveal flows so typed routing does not collapse back into generic helper execution.
- refreshed inspiration/research notes, shell protocol events, and repo hygiene surfaces for the new pass.

## What Revision 004 adds
- a stronger design-phase posture around **not collapsing separate questions too early**, especially object identity, namespace naming, mutable current state, and durable grant persistence,
- `docs/30-architecture/design-splits-and-non-decisions.md` to keep the most dangerous couplings visible and deferred until evidence justifies them,
- `docs/30-architecture/revocation-and-durable-grants-design-space.md` to separate ephemeral grants, durable reopen, and strong live revocation instead of treating them as one feature,
- `docs/70-shell/shell-terminal-protocol-sketch.md` to record the minimum shell-to-terminal metadata that could make ViewFS blocks, receipts, and view badges feel first-class,
- `rfcs/0004-viewfs-separate-questions-before-freezing.md` so future proposals have to earn any coupling between identity, naming, mutation, and durable authority,
- refreshed lessons/inspirations, SlopOS seam framing, and repo hygiene surfaces for the new research pass.

## Previous revision highlights
- Revision 003 added a stronger “lessons we must not ignore” pass, new notes on mutable work state / capability bundles / portal grant lifecycles, a clearer SlopOS seam map, and a research-spike RFC.
- Revision 002 added the first SlopOS seam map, a decision-freeze RFC, and broader shell/terminal inspiration.
- Revision 001 seeded the repo hygiene, charter, architecture postures, and first RFC.

## What Revision 073 adds
- `rfcs/0066-viewfs-keep-selected-regions-entity-candidates-route-envelopes-prepared-actions-and-receipts-separate.md` so highlighted transcript regions, extracted typed entities, lazy target resolution, typed route envelopes, prepared actions, and durable receipts cannot silently collapse into one magical click/open story.
- refreshed `docs/30-architecture/design-splits-and-non-decisions.md`, `docs/30-architecture/slopos-seam-map.md`, and `docs/90-inspirations/slopos-datacube-evaluation.md` with a sharper transcript-entity/routed-action seam that steals from SlopOS plumb drafts without forcing a final packet schema.
- refreshed `docs/70-shell/semantic-marks-links-and-overlays.md` and `docs/70-shell/shell-super-awesome-moves.md` with **entity peels**, **lazy resolve drawers**, **route slips**, and **hypertruth badges** worth stealing for the future custom shell+terminal.
- expanded bibliography and moving-head source tracking with Plan 9 plumber, OSC 8, LSP document-link resolve, and kitty hints precedents, then refreshed the external review queue.
- fixed repo hygiene so the context-pack builder now carries RFCs 0065 and 0066 instead of silently stopping at 0064, then regenerated the context pack and release manifest for the new archive.


Latest seam work: keep delta recipes, exact bases, apply sessions, reconstructed targets, and receipts separate so efficient repair/update/import flows do not quietly become object identity or authority truth.
## Revision 163 executable GC/archive/deletion spine

Revision 163 expands the fixture corpus to 146 specimens and adds checked lanes for GC candidates, snapshot pins, archive/legal holds, backup sets, restore plans, deletion claims, and sanitization proofs. The core rule is that `deleted`, `retained`, `restorable`, `sanitized`, and `gone from this view` are separate states. A backup manifest cannot restore by itself; a deletion claim cannot reopen authority; a snapshot pin blocks collection but is not a handle; a legal hold blocks collection without granting read access.

Generated reports now include `out/gc_archive_trace_report.md` alongside conformance, policy, freshness, disclosure, and collaboration traces.

