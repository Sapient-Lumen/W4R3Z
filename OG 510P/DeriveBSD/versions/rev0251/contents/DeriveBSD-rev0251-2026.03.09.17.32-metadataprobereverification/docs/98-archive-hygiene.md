# Archive hygiene (how we avoid a monster)

This repo must grow over time, but not explode.

## Rules

1) Prefer **RFCs** for proposals, then accept via **ADRs**.
2) Keep docs small:
   - “one concept per file”
   - link out to RFCs/ADRs instead of duplicating content
3) Any new subsystem must pass the **design review rubric** (copy the template into the RFC):
   - contract surface (typed, digest-bound)
   - authority changes (attenuation + revocation + diff surfaces)
   - threat model impact + trust boundaries
   - failure modes + rollback behavior
   - evidence outputs + retention budget

See: `docs/348-design-review-rubric-and-feature-intake.md`.

4) Add references as links; avoid copying external text.
5) When a topic becomes stale, move it to `docs/attic/` and leave a one-line pointer.

## Checks

- Quick path: `python3 tools/hygiene.py` runs the lightweight checks below in one go.

- Run `python3 tools/check_consistency.py` before committing:
  - missing RFC/ADR ids
  - broken backticked repo paths
  - broken internal markdown links (repo-relative or relative-to-file links)
  - rejects accidental ChatGPT citation markers (use explicit URLs in docs)

- Run `python3 tools/check_discovery.py` before committing when you added/renamed docs or changed the reading paths:
  - ensures `docs/00-index.md` contains a `New in <version>` section for the newest CHANGELOG entry
  - ensures the newest `New in <version>` block is the **first** `New in ...` section (prevents stale top-of-file release notes)
  - ensures `docs/00-index.md` has a `
  - ensures critical “amnesia-resistor” entry points remain wired (LLM runbook, product profiles, etc.)
  - ensures numbered docs mentioned in the newest CHANGELOG entry are wired into discovery surfaces (index vs juicy lessons)
  - ensures those docs also appear in the matching `New in <version>` block (so release notes don't go stale)
  - ensures repo paths mentioned in the newest CHANGELOG entry actually exist

- Run `python3 tools/check_changelog_format.py` to keep release notes compact and diff-friendly:
  - enforces that `CHANGELOG.md` has minimal leading whitespace after the top heading
  - rejects trailing whitespace (prevents noisy diffs)

- Run `python3 tools/check_changelog_artifact_mentions.py` to prevent 'paper artifact' drift in the newest release:
  - for docs mentioned in the newest CHANGELOG entry, ensures any backticked `*.plan`/`*.receipt`/etc artifact kinds have a matching schema under `spec/` (e.g. `spec/mirror.import.receipt.schema.json`)

- Run `python3 tools/check_release_last_updated.py` to keep release-touched docs stamped:
  - for docs mentioned in the newest `CHANGELOG.md` entry, requires a `
  - keeps doc changes mechanically visible without forcing retroactive churn


- Run `python3 tools/check_must_read_set.py` to prevent 'must-read' drift:
  - ensures the runbook’s mandatory refresh list keeps the canonical start-here docs
  - keeps the generated context pack’s must-read section complete (since it is derived from the runbook)

- Run `python3 tools/check_doc_metadata.py` when editing docs in the meta-engineering range (>=397):
  - enforces a tiny Tier/Profiles/Pillars metadata block near the top of the doc
  - validates Tier/Profiles/Pillars values against the allowed enums

- Run `python3 tools/check_meta_doc_discoverability.py` when adding/moving meta-engineering docs (>=397):
  - ensures every meta doc remains linked from either `docs/00-index.md` or `docs/110-juicy-os-lessons.md`
  - prevents quiet drift where the "design law" docs exist but are unreachable


- Run `python3 tools/check_diff_surface_registry.py` when adding or refactoring diff artifacts:
  - enforces that every `*.diff` schema under `spec/` is listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)
  - prevents quiet review-surface drift where new diffs exist but aren’t discoverable

- Run `python3 tools/check_diff_surface_registry_wiring.py` when editing the diff surface registry table:
  - enforces that each `*.diff` row includes at least one backticked wiring-doc pointer (e.g. `docs/428-...`)
  - prevents “registry lists a diff but nobody can find the gate semantics” drift

- Run `python3 tools/check_diff_review_docs.py` when adding or refactoring per-diff review-surface docs:
  - enforces that each `*diff-as-*surface*.md` doc declares Tier placement
  - requires the canonical pattern token `Registry→Diff→Gate`
  - requires schema + example pointers so reviewers can jump directly to contracts
  - keeps the family of “diff review surface” docs uniform (reduces amnesia drift)


- Run `python3 tools/check_diff_wiring_risk_flags.py` when adding new diff wiring docs:
  - incrementally requires wiring docs listed in `docs/430-diff-surface-registry.md` to declare a `## Risk flags` section (or be explicitly allowlisted under `tools/baselines/`)
  - keeps `risk_flags` reason codes as a stable jump-to review surface for UI + policy gates

- Run `python3 tools/check_juicy_lesson_references.py` when adding new external URLs to the juicy lessons index (`docs/110-juicy-os-lessons.md`):
  - blocks new uncataloged citations without forcing retroactive churn (uses a baseline allowlist)
  - prefer adding new URLs to `docs/32-curated-references.md`; extend the allowlist only for historic gaps

- Run `python3 tools/check_risk_flag_registry.py` when introducing or renaming `risk_flags` reason codes:
  - enforces that a canonical risk flag registry exists as a typed artifact (`risk.flag.registry`)
  - ensures spec examples and gate docs use canonical kebab-case ids (prevents ad-hoc flag drift)

- Run `python3 tools/check_risk_flag_typical_sources.py` to keep risk flag metadata wired to real artifacts:
  - ensures each `typical_sources` entry in `risk.flag.registry` refers to a real schema under `spec/`
  - requires diff kinds referenced as typical sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)

- Run `python3 tools/check_doc_patterns.py` for meta docs (>=397):
  - requires a `**Patterns:**` metadata line near the top
  - forces new ideas to explicitly map to existing patterns (reduces design sprawl)

- Run `python3 tools/check_curated_references.py` when introducing new external work in meta docs (>=397):
  - ensures each external URL in meta docs is listed in `docs/32-curated-references.md`
  - keeps citations centralized and reduces long-term “link drift”

- Run `python3 tools/check_release_curated_references.py` when cutting a release that introduces new numbered docs:
  - for numbered docs mentioned in the newest `CHANGELOG.md` entry, ensures any external URLs are also listed in `docs/32-curated-references.md`
  - prevents new “uncataloged citations” without forcing retroactive churn across the full archive



- Run `python3 tools/check_support_bundle_contract.py` when editing incident/support handoff docs or schemas:
  - keeps the official support handoff contract wired (`incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`)
  - enforces timeline-first example wiring and the canonical `tar.zst` payload default

- Run `python3 tools/check_safe_open_contract.py` when editing content-import, safe-open, or support-bundle intake docs/schemas:
  - keeps the safe-open support-bundle intake boundary wired (`content.import.plan` + `content.import.receipt` execution boundary, no-network disposable intake, timeline-first preview posture)
  - enforces the canonical example wiring so support-bundle intake does not drift back to direct-host-open folklore

- Run `python3 tools/check_support_bundle_import_contract.py` when editing the typed support-bundle intake shapes or canonical import examples:
  - keeps `spec/content.import.support-bundle.plan.schema.json` / `spec/content.import.support-bundle.receipt.schema.json` aligned with the generic import lane
  - enforces that the official support-bundle path remains a constrained specialization of `content.import.plan` / `content.import.receipt`, not a new authority kind
  - keeps the canonical support-bundle example shapes, preview members, and disposable microVM posture wired

- Run `python3 tools/check_boot_contract.py` when editing boot admission, loader-verification, or kernel-module join docs/schemas:
  - keeps the boot-code admission contract wired (`boot.manifest` + `boot.override.policy` + `boot.override.receipt` + `boot.attestation` + `kmod.load.plan` + `kmod.load.receipt`)
  - enforces example digest joins so manifests, attestation, override receipts, and kmod receipts cannot drift apart silently

- Run `python3 tools/check_reset_contract.py` when editing install/recovery, destructive reprovision, or reset-authority docs/schemas:
  - keeps the destructive-reprovision contract wired (`reset.authorization` + `reset.receipt` + `disk.layout.plan` + `disk.layout.receipt`)
  - enforces example digest joins so reset authority, disk mutation evidence, and A–D profile defaults cannot drift apart silently

- Run `python3 tools/check_strata_contract.py` when editing runtime-composition docs or schemas:
  - keeps the explicit userland-composition contract wired (`stratum.manifest` + `stratum.stack` + `mount.view` + `runtime.manifest`)
  - enforces the example digest joins and the no-host-fallback / single-ABI-anchor boundary so multi-origin userlands do not drift back into ad-hoc chroot folklore

- Run `python3 tools/check_keyless_identity_contract.py` when editing keyless identity, Sigstore bundle, or release-authority join docs/schemas:
  - keeps `publisher.identity.receipt` supplemental (`authority_semantics = identity-evidence-only`) and bundle-first for `sigstore-keyless`
  - enforces the example digest joins across `publisher.identity.receipt`, `sigstore.bundle`, trust roots, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_release_transparency_contract.py` when editing release transparency, checkpoint receipts, monitor snapshots, or release-authority gating docs/schemas:
  - keeps `release.publish.receipt` authoritative while `release.transparency.entry`, `log.checkpoint.receipt`, and `transparency.monitor.snapshot` stay evidence-only
  - enforces the example digest joins across `release.authority.policy`, `release.transparency.entry`, `log.checkpoint.receipt`, `transparency.monitor.snapshot`, and `release.publish.receipt`

- Run `python3 tools/check_witness_policy_contract.py` when editing witness rosters, checkpoint receipts, monitor policy, or release-authority witness gating docs/schemas:
  - keeps `witness.policy` as the authoritative witness-trust surface instead of inline quorum folklore
  - enforces the example digest joins across `witness.policy`, `log.checkpoint.receipt`, `transparency.monitor.policy`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_supplychain_verification_contract.py` when editing workflow-verification, in-toto layout-policy, or release-authority gating docs/schemas:
  - keeps `supplychain-verify-receipt` supplemental (`authority_semantics = workflow-verification-evidence-only`)
  - enforces the example digest joins across `supplychain-layout-policy`, `supplychain-verify-receipt`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_vulnerability_verification_contract.py` when editing vulnerability-intel, VEX, or release-authority gating docs/schemas:
  - keeps `vuln-gate-receipt` supplemental (`authority_semantics = vulnerability-verification-evidence-only`)
  - enforces the example digest joins across `vuln.gate.policy`, `vuln.query.receipt`, `vuln-gate-receipt`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_attestation_admission_contract.py` when editing attestation evidence, admission-policy, or consuming action-receipt docs/schemas:
  - keeps `attestation.receipt` evidence-only (`authority_semantics = attestation-evidence-only`)
  - enforces the example digest joins across `attestation.requirement`, `attestation.admission.policy`, `attestation.receipt`, `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt`

- Run `python3 tools/check_lease_authority_contract.py` when editing temporary-authority grant / lease / use docs or schemas:
  - keeps the authoritative temporary-authority object lane-specific (grant / lease / session) while `lease.envelope`, `lease.issue.receipt`, and `lease.use.receipt` stay metadata / evidence-only
  - enforces the canonical example joins across `portal-grant`, `lease.envelope`, `lease.issue.receipt`, `lease.use.receipt`, and `export.receipt`

- Run `python3 tools/check_authority_budget_contract.py` when editing authority-budget docs or schemas:
  - keeps `authority.budget` authoritative for the narrow component-runtime lane while `authority.budget.check` stays evidence-only
  - enforces the v0 dimension set and the canonical example joins across `authority.budget`, `authority.budget.check`, and `authority.exception`

- Run `python3 tools/check_store_gc_contract.py` when editing retention, GC, or boot-environment wiring docs/schemas:
  - keeps the store-retention contract wired (`store_retention` profile defaults + `store.gc.plan` + `store.gc.receipt`)
  - enforces the hard rollback-floor split from soft retention preference and the canonical rollback-coverage example wiring

- Run `python3 tools/check_learn_net_contract.py` when editing learned-network-policy docs or schemas:
  - keeps `net-flow-summary` as the compact evidence-only learn-session surface rather than a hidden authority object
  - enforces bounded learn/audit sessions, canonical example digest joins to `net-flow-receipt` / `net-dns-query-receipt` / `net-egress-policy`, and keeps review-before-enforce visible in the core docs

- Run `python3 tools/check_packet_capture_boundary.py` when editing packet-capture, raw-socket, BPF-risk, or fast-packet-I/O docs:
  - keeps packet capture / raw packet visibility distinct from ordinary `net-egress-policy`
  - enforces that flight recorder, network, device, and netmap docs all point at the same stronger boundary in `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`

- Run `python3 tools/check_packet_capture_session_contract.py` when editing packet-capture session, export, or incident-bundle docs/schemas:
  - keeps packet capture lease-shaped through `packet.capture.session` rather than ad-hoc blob workflows
  - enforces summary-first export posture across the packet-capture, export, incident-bundle, evidence, and risk-register docs

- Run `python3 tools/check_packet_capture_summary_contract.py` when editing packet-capture summary, export, or evidence docs/schemas:
  - keeps `packet.capture.summary` distinct from `net-flow-summary` so packet-capture review does not blur into network-policy learning
  - enforces the canonical summary digest join back to `packet.capture.session` and keeps export/incident/evidence docs centered on the summary-first review surface

- Run `python3 tools/check_packet_capture_selector_contract.py` when editing packet-capture selector/session docs or schemas:
  - keeps `packet.capture.selector` as the typed review surface inside `packet.capture.session`
  - prevents free-form backend filter strings from quietly returning to the authoritative session object
  - keeps the selector compiler boundary visible in the session, summary, runbook, and evidence docs

- Run `python3 tools/check_packet_capture_artifact_contract.py` when editing packet-capture retention/summary/export docs or schemas:
  - keeps retained raw packet files subordinate to the typed session/summary lane

- Run `python3 tools/check_packet_capture_import_contract.py` when editing packet-capture import, safe-open, or export docs/schemas:
  - keeps stronger sideband/decryption-bearing packet-capture artifacts on the typed safe-open import profile rather than host-open folklore
  - enforces normalize-before-promotion so ordinary support/export lanes prefer `packet.capture.summary` or normalized `packet-records-only` derivatives
- Run `python3 tools/check_packet_capture_normalization_contract.py` when editing packet-capture normalization, redaction, or export docs/schemas:
  - keeps packet-capture normalization on the generic `redaction-transform` / `redaction-receipt` evidence lane
  - enforces that packet-capture import receipts point at typed normalization proof instead of treating `strip-metadata` as a free-floating tool side effect
- Run `python3 tools/check_packet_capture_bundle_contract.py` when editing packet-capture bundle, support-handoff, or incident-bundle docs/schemas:
  - keeps `incident.bundle` / `bundle.plan` packet-capture joins explicit through session/summary/import/redaction receipt digests
  - enforces that support bundles stay summary-first for packet capture rather than quietly regressing into raw `.pcapng` payload defaults
  - enforces explicit `max_local_retention_seconds`, `metadata_posture`, and `retention_until` joins so local packet files do not quietly become the real product surface

- Run `python3 tools/check_packet_capture_export_contract.py` when editing packet-capture export-policy / export-receipt docs or schemas:
  - keeps `packet.capture.summary` as the ordinary export class and `packet.capture.normalized` as the stronger explicit raw-byte class
  - requires proof-bound stronger exports to carry typed `supporting_evidence` joins back to session / summary / import / redaction evidence instead of normalized `.pcapng` folklore
- Run `python3 tools/check_packet_capture_export_approval_contract.py` when editing stronger packet-capture export approval docs or schemas:
  - keeps `consent_receipt_digest` required for `packet.capture.normalized` export
  - prevents approval drift back to `method = auto` when stronger packet bytes leave the system
- Run `python3 tools/check_packet_capture_export_transport_contract.py` when editing stronger packet-capture export transport or handoff docs/schemas:
  - keeps `transport_receipt_digest` required for completed `packet.capture.normalized` export
  - prevents `destination.type = file` from quietly becoming the completed stronger export act
- Run `python3 tools/check_packet_capture_export_acceptance_contract.py` when editing stronger packet-capture export closure docs/schemas:
  - keeps `transport_acceptance_receipt_digest` required for final `packet.capture.normalized` export
  - keeps `spec/transport.acceptance.receipt.schema.json` + `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json` wired as the transport acceptance receipt surface
  - keeps final stronger handoff at `delivery_state = recipient-accepted` rather than treating send success as acceptance
  - keeps stronger packet approval destination-bound by checking `action.destination` against transport / recipient acceptance / export destination evidence (`tools/check_packet_capture_export_destination_binding_contract.py`)
- Run `python3 tools/check_packet_capture_export_recipient_digest_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `acceptance.remote_artifact_digest` required for stronger packet recipient acceptance
  - enforces that the recipient-side acceptance receipt echoes the same normalized digest instead of merely a plausible remote reference
- Run `python3 tools/check_packet_capture_export_remote_object_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `adapter.remote_id` required for canonical stronger packet export receipts
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote object identifier instead of drifting across multiple remote attachments in one case
- Run `python3 tools/check_packet_capture_export_remote_validator_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_validator` continuity required when the stronger adapter can see a remote representation/version token
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote validator instead of collapsing back to object id alone
- Run `python3 tools/check_packet_capture_export_remote_protection_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_protection` continuity required for canonical stronger packet handoff
  - enforces that recipient acceptance / final export evidence stay on the same remote protection posture instead of treating any accepted upload as durable evidence by implication
- Run `python3 tools/check_packet_capture_export_remote_locator_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_locator` continuity required for canonical stronger packet handoff
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote locator instead of leaving later evidence retrieval to portal folklore
- Run `python3 tools/check_packet_capture_export_reverification_contract.py` when editing stronger packet-capture export follow-up/recheck docs or schemas:
  - keeps `transport.reverification.receipt` as the typed metadata-only reverification lane for later stronger packet evidence checks
  - enforces `body_downloaded = false` plus the same accepted remote validator / protection posture / locator instead of portal screenshots or packet re-downloads
- Run `python3 tools/check_packet_capture_export_digest_stability_contract.py` when editing stronger packet-capture export proof-chain, approval, or transport docs/schemas:
  - keeps stronger packet export digest-stable across normalization, approval, transport, recipient acceptance, and export
  - enforces that approval / transport / transport-acceptance / export receipts keep the same normalized digest instead of drifting across related derivatives

- Run `python3 tools/check_frontend_compile_contract.py` when editing frontend-authoring boundary docs or schemas:
  - keeps compiled canonical JSON authoritative while `frontend.compile.receipt` stays evidence-only
  - enforces the canonical HuJSON example joins across `frontend.compile.receipt`, `spec/examples/trust.policy.hujson`, and `spec/examples/trust.policy.json`


- Run `python3 tools/check_fuzz_contract.py` when editing fuzzing, crash-replay, or regression-localization docs/schemas:
  - keeps `fuzz.receipt` evidence-only and `crash.case` replay-focused with explicit reproducibility state
  - enforces the v0 target-class set, keeps coverage percentages advisory, and prevents drift across fuzz receipts, crash cases, and product-shape fuzz target classes


- Run `python3 tools/check_product_profiles.py` when editing `spec/examples/product.profiles.json` or profile-shape docs:
  - keeps the A–D runtime and authority defaults stable
  - prevents profile drift on network-topology posture, hardware-compatibility posture, device-authority posture, installation/recovery posture, kernel-mutation posture, update-delivery posture, high-risk approval posture, workstation runtime, removable media, firmware-update posture, backup/recovery posture, data-at-rest posture, trustworthy-time posture, platform-provenance / attestation-admission posture, inbound/outbound networking posture, remote-assistance posture, private-key posture, human-identity/home-state posture, evidence-collection posture, evidence-export posture, trust-bundle posture, and workload-identity / credential-issuance posture

- Run `python3 tools/check_generated_docs.py` to ensure generated discovery docs are up to date:
  - checks `docs/412-product-profile-matrix.md`
  - checks `docs/420-context-pack.md` and `docs/_generated/context_pack.json`
  - checks `docs/414-doc-catalog.md` and `docs/_generated/doc_catalog.json`
  - checks `docs/415-risk-register-index.md` and `docs/_generated/risk_register.json`
  - checks `docs/418-artifact-index.md` and `docs/_generated/artifact_index.json`
  - fix by running:
    - `python3 tools/gen_product_profile_matrix.py --write`
    - `python3 tools/gen_context_pack.py --write`
    - `python3 tools/gen_doc_catalog.py --write`
    - `python3 tools/gen_risk_register_index.py --write`
    - `python3 tools/gen_artifact_index.py --write`

- Run `python3 tools/check_risk_register.py` when editing the open questions/risk register:
  - enforces that each numeric item in `docs/266-open-questions-and-risk-register.md` contains an explicit `Risk:` line

- Run `python3 tools/check_schema_kind_matches_filename.py` when adding or renaming dotted-kind schemas:
  - enforces that schemas with dotted `kind` names (e.g. `mirror.import.receipt`) keep a stable filename mapping (e.g. `spec/mirror.import.receipt.schema.json` for kind `mirror.import.receipt`)
  - prevents quiet drift where docs/tooling refer to one kind while the schema declares another

- Run `python3 tools/check_spec_example_coverage.py` when adding or refactoring artifacts:
  - ensures each critical artifact schema (plan/receipt/event/report/registry/diff) has a matching example in `spec/examples/`

- Run `python3 tools/check_product_profiles.py` when changing A–D defaults or wording around their hard boundaries:
  - keeps profile-shaped defaults (runtime, hardware compatibility, network topology, device authority, installation/recovery, kernel mutation, operator access, media/USB, firmware updates, networking, support, key use, home state, recovery, data at rest, trustworthy time, platform provenance, export, trust bundles, workload identity) stable and reviewable

- Run `python3 tools/check_version.py` before committing if you touched discovery surfaces or version stamps:
  - ensures README + docs/00-index + docs/110 last-updated tags match the newest CHANGELOG entry

- Run `python3 tools/lint_spec_schemas.py` when touching `spec/` schemas:
  - checks schema convention drift (kind/version/id/timestamp fields; catches copy/paste errors)

- Run `python3 tools/validate_spec_examples.py` when touching `spec/`:
  - validates examples under `spec/examples/` against schemas under `spec/`
  - catches schema/example drift early
  - if an example is intended as a long-lived contract, add a matching schema (even a thin `$ref` wrapper)
  - if you want multiple long-lived variants for a single contract, suffix the example filename (e.g. `microvm.stop.receipt.denied.json`) **and** add a matching wrapper schema (e.g. `spec/microvm.stop.receipt.denied.schema.json`) that `$ref`s the base schema and pins the variant semantics

## Document lifecycle

- `rfcs/` = debate + iteration
- `adrs/` = decisions (append-only)
- `docs/` = current truth (concise, updated when ADR lands)

Last updated: 2026-03-09r254