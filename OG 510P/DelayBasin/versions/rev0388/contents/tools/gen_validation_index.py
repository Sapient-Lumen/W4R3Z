import json
import pathlib
import re
from collections import OrderedDict

from validation_inventory_lib import ordered_validation_tools

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "VALIDATION-INDEX.json"
OUT_MD = ROOT / "docs/00-meta/validation-index.md"
RUN_LINT = ROOT / "tools/run_lint_suite.py"
MAKEFILE = ROOT / "Makefile"
CHANGELOG = ROOT / "CHANGELOG.md"


def current_revision() -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"(rev\d{4})", text)
    if not m:
        raise SystemExit("CHANGELOG.md missing current revision header")
    return m.group(1)


def ordered_tools() -> list[str]:
    return ordered_validation_tools(ROOT)


def tool_bucket(tool: str) -> str:
    if tool in {"check_discovery.py", "check_registry_ids.py", "check_archive_index_order.py", "check_archive_index_table_shape.py", "check_revision_sync.py", "check_release_hygiene.py", "check_internal_surface_references.py", "check_path_portability_contract.py", "check_generated_surface_drift.py", "gen_external_metadata.py", "check_external_metadata_contract.py", "check_package_identity_witness_contract.py", "check_package_identity_audit_contract.py", "check_schema_coverage_audit_contract.py", "check_json_schema_surface_contract.py", "check_frontier_backlog_contract.py", "check_link_integrity_policy_contract.py", "check_canary_protocol_contract.py", "check_canary_runs_contract.py", "check_ledger_audit_contract.py", "check_archive_economy_audit_contract.py", "check_open_question_tail_ordinal_contract.py", "check_latest_revision_cue_contract.py", "check_startup_current_head_contract.py", "check_landing_current_additions_alignment.py", "check_docs_readme_current_docs_head_alignment.py", "check_frozen_head_alignment.py", "check_currentness_cue_audit_contract.py", "check_currentness_witness_contract.py"}:
        return "discovery_release_identity"
    if tool in {"gen_context_pack.py", "gen_innovation_packet.py", "gen_frontier_ticket.py", "gen_compact_surface_bundle.py", "gen_canary_runs.py", "gen_reentry_surface_conformance.py", "gen_release_integrity.py", "gen_ledger_audit.py", "gen_archive_economy_audit.py", "gen_validation_index.py", "gen_validation_toolchain_manifest.py", "gen_currentness_cue_audit.py", "gen_package_identity_audit.py", "gen_schema_coverage_audit.py", "gen_schema_conformance_audit.py", "check_agents_contract.py", "check_currentness_cue_audit_contract.py", "check_context_pack_budget.py", "check_context_pack_fidelity.py", "check_context_pack_contract.py", "check_context_pack_warning_contract.py", "check_context_pack_open_question_contract.py", "check_current_innovation_packet_contract.py", "check_frontier_ticket_contract.py", "check_compact_surface_bundle_contract.py", "check_reentry_surface_contract.py", "check_reentry_generation_closure_contract.py", "check_reentry_command_visibility_contract.py", "check_validation_index_contract.py", "check_release_integrity_contract.py", "check_canary_protocol_contract.py", "check_canary_runs_contract.py", "check_ledger_audit_contract.py"}:
        return "startup_derivative_packets"
    if tool.startswith("check_basis") or tool in {"check_scope_witness_contract.py", "check_authorship_witness_contract.py", "check_status_lane_witness_contract.py", "check_revision_receipt_contract.py", "check_receipt_freshness_contract.py", "check_receipt_delta_coherence.py", "check_revision_receipt_refs.py", "check_revision_receipt_pointer_integrity.py", "check_operational_head_contract.py", "check_status_lane_contract.py", "check_reentry_cue_contract.py"}:
        return "receipt_basis_status"
    if tool in {"check_core_lexicon_contract.py", "check_move_registry_contract.py", "check_prompt_pair_contract.py", "check_promotion_contract.py", "check_decay_watch_contract.py", "check_vocabulary_witness_contract.py"}:
        return "governed_vocab_registries"
    if tool in {"check_followthrough_witness_contract.py", "check_assumption_witness_contract.py", "check_obligation_witness_contract.py", "check_foreign_pressure_witness_contract.py", "check_transfer_ledger_contract.py", "check_import_hygiene_contract.py", "check_action_lane_contract.py", "check_gate_class_contract.py", "check_resolution_witness_contract.py", "check_quarantine_contract.py", "check_self_sufficiency_assay_contract.py"}:
        return "continuity_ledgers_transfer"
    if tool.startswith("check_gpustorming") or tool == "check_sink_namespace_contract.py":
        return "gpustorming_handle_family"
    return "method_witness_families"


CATEGORY_META = OrderedDict([
    ("discovery_release_identity", {
        "label": "discovery, release identity, and package coherence",
        "claim": "keep named bundle lineage, release metadata, and discovery surfaces machine-checkable so the current packaged archive stays inspectable rather than recency-shaped.",
        "surfaces": ["README.md", "docs/README.md", "ARCHIVE_INDEX.md", "CHANGELOG.md", "RELEASE-MANIFEST.json", "FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json", "CANARY-PROTOCOL.json", "CANARY-RUNS.json", "LEDGER-AUDIT.json", "docs/00-meta/ledger-audit.md", "VALIDATION-TOOLCHAIN-MANIFEST.json", "docs/00-meta/validation-toolchain.md", "CURRENTNESS-CUE-AUDIT.json", "docs/00-meta/currentness-cue-audit.md", "PACKAGE-IDENTITY-AUDIT.json", "docs/00-meta/package-identity-audit.md", "SCHEMA-CONFORMANCE-AUDIT.json", "docs/00-meta/schema-conformance-audit.md", "SCHEMA-COVERAGE-AUDIT.json", "docs/00-meta/schema-coverage-audit.md", "ALIAS-RETENTION-POLICY.json", "CANARY-RUNS.json"],
    }),
    ("startup_derivative_packets", {
        "label": "startup and derivative packet surfaces",
        "claim": "keep the compact startup wrappers, current-focus packet, exact current innovation packet, bounded replay capsule, compact family card, reentry conformance, and validation inventory source-backed and derivative rather than ambient or silently stale.",
        "surfaces": ["START_HERE.md", "AGENTS.md", "context-pack.json", "innovation-packet.json", "frontier-ticket.json", "replay-capsule.json", "compact-surface-bundle.json", "REENTRY-CONTRACT.json", "REENTRY-SURFACE-CONFORMANCE.json", "VALIDATION-INDEX.json", "docs/00-meta/validation-index.md", "VALIDATION-TOOLCHAIN-MANIFEST.json", "docs/00-meta/validation-toolchain.md", "CURRENTNESS-CUE-AUDIT.json", "docs/00-meta/currentness-cue-audit.md", "SCHEMA-CONFORMANCE-AUDIT.json", "docs/00-meta/schema-conformance-audit.md", "SCHEMA-COVERAGE-AUDIT.json", "docs/00-meta/schema-coverage-audit.md"],
    }),
    ("receipt_basis_status", {
        "label": "receipt, basis, scope, and status honesty",
        "claim": "keep revision receipts explicit about basis precision, scope, authorship, operational-vs-citation heads, status lanes, and terse-key freshness rather than letting one lively surface inherit flattering authority.",
        "surfaces": ["REVISION-RECEIPT.json", "SURFACE-STATUS.json", "docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md", "docs/10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md", "docs/10-method/scope-witnesses-active-request-packets-and-ambient-roster-guards.md", "docs/10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md", "docs/10-method/receipt-freshness-witnesses-bundle-stem-truth-and-carryforward-key-coherence.md"],
    }),
    ("governed_vocab_registries", {
        "label": "governed vocabularies, registries, and controlled tokens",
        "claim": "keep prompt pairs, moves, lexicon entries, decay watches, and witness vocabulary synchronized so later comparisons do not drift into checker-local synonyms or orphan ids.",
        "surfaces": ["WITNESS-VOCABULARY.json", "docs/20-constitution/core-lexicon-registry.md", "docs/20-constitution/move-registry.md", "docs/20-constitution/prompt-pair-registry.md", "docs/20-constitution/promotion-contract-registry.md", "docs/20-constitution/decay-watch-registry.md"],
    }),
    ("continuity_ledgers_transfer", {
        "label": "continuity ledgers and cross-datacube transfer memory",
        "claim": "keep live followthrough, assumptions, obligations, imports, action lanes, gate classes, resolutions, and quarantine boundaries durable rather than scattered across revision prose.",
        "surfaces": ["FOLLOWTHROUGH-QUEUE.json", "ASSUMPTION-LEDGER.json", "OBLIGATION-LEDGER.json", "FOREIGN-PRESSURE-LEDGER.json", "DATACUBE-TRANSFER-LEDGER.json", "RESOLUTION-LEDGER.json", "RETROSPECTIVE-QUEUE.json", "FIREBREAK-LEDGER.json"],
    }),
    ("gpustorming_handle_family", {
        "label": "GPUstorming handle-family controls",
        "claim": "keep the accumulated exact-handle anti-overclaim and anti-derivative-laundering ratchets synchronized across method, promptcraft, trajectory, and registry surfaces.",
        "surfaces": ["docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md", "docs/50-promptcraft/prompt-pairs.md", "docs/20-constitution/claim-registry.md", "docs/20-constitution/open-question-registry.md"],
    }),
    ("method_witness_families", {
        "label": "broader method witness families",
        "claim": "keep the large witness and packet families in docs/10-method tied to their registries, prompts, and receipts so make lint does not collapse into one opaque green light.",
        "surfaces": ["docs/10-method/", "docs/20-constitution/claim-registry.md", "docs/20-constitution/invariant-registry.md", "docs/20-constitution/open-question-registry.md", "docs/50-promptcraft/prompt-pairs.md"],
    }),
])


def commands() -> list[dict]:
    mk = MAKEFILE.read_text(encoding="utf-8")
    rows = []
    for name, command, outputs in [
        ("all_generated_surfaces", "python3 tools/gen_all_generated_surfaces.py", ["LICENSE", "CITATION.cff", "codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json", "context-pack.json", "innovation-packet.json", "frontier-ticket.json", "replay-capsule.json", "compact-surface-bundle.json", "CANARY-RUNS.json", "VALIDATION-INDEX.json", "VALIDATION-TOOLCHAIN-MANIFEST.json", "LINT-IDEMPOTENCE-AUDIT.json", "CURRENTNESS-CUE-AUDIT.json", "PACKAGE-IDENTITY-AUDIT.json", "BASIS-PROVENANCE-AUDIT.json", "SCHEMA-COVERAGE-AUDIT.json", "SCHEMA-CONFORMANCE-AUDIT.json", "REENTRY-SURFACE-CONFORMANCE.json", "LEDGER-AUDIT.json", "ARCHIVE-ECONOMY-AUDIT.json", "FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json"]),
        ("external_metadata", "python3 tools/gen_external_metadata.py", ["LICENSE", "CITATION.cff", "codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json"]),
        ("context_pack", "python3 tools/gen_context_pack.py", ["context-pack.json"]),
        ("innovation_packet", "python3 tools/gen_innovation_packet.py", ["innovation-packet.json"]),
        ("frontier_ticket", "python3 tools/gen_frontier_ticket.py", ["frontier-ticket.json"]),
        ("replay_capsule", "python3 tools/gen_replay_capsule.py", ["replay-capsule.json"]),
        ("validation_index", "python3 tools/gen_validation_index.py", ["VALIDATION-INDEX.json", "docs/00-meta/validation-index.md"]),
        ("validation_toolchain", "python3 tools/gen_validation_toolchain_manifest.py", ["VALIDATION-TOOLCHAIN-MANIFEST.json", "docs/00-meta/validation-toolchain.md"]),
        ("currentness_audit", "python3 tools/gen_currentness_cue_audit.py", ["CURRENTNESS-CUE-AUDIT.json", "docs/00-meta/currentness-cue-audit.md"]),
        ("package_identity_audit", "python3 tools/gen_package_identity_audit.py", ["PACKAGE-IDENTITY-AUDIT.json", "docs/00-meta/package-identity-audit.md"]),
        ("basis_provenance_audit", "python3 tools/gen_basis_provenance_audit.py", ["BASIS-PROVENANCE-AUDIT.json", "docs/00-meta/basis-provenance-audit.md"]),
        ("schema_coverage_audit", "python3 tools/gen_schema_coverage_audit.py", ["SCHEMA-COVERAGE-AUDIT.json", "docs/00-meta/schema-coverage-audit.md"]),
        ("schema_conformance_audit", "python3 tools/gen_schema_conformance_audit.py", ["SCHEMA-CONFORMANCE-AUDIT.json", "docs/00-meta/schema-conformance-audit.md"]),
        ("lint_idempotence_audit", "python3 tools/gen_lint_idempotence_audit.py", ["LINT-IDEMPOTENCE-AUDIT.json", "docs/00-meta/lint-idempotence-audit.md"]),
        ("compact_surface_bundle", "python3 tools/gen_compact_surface_bundle.py", ["compact-surface-bundle.json"]),
        ("canary_runs", "python3 tools/gen_canary_runs.py", ["CANARY-RUNS.json"]),
        ("reentry_conformance", "python3 tools/gen_reentry_surface_conformance.py", ["REENTRY-SURFACE-CONFORMANCE.json"]),
        ("release_integrity", "python3 tools/gen_release_integrity.py", ["FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json"]),
        ("ledger_audit", "python3 tools/gen_ledger_audit.py", ["LEDGER-AUDIT.json", "docs/00-meta/ledger-audit.md"]),
        ("archive_economy_audit", "python3 tools/gen_archive_economy_audit.py", ["ARCHIVE-ECONOMY-AUDIT.json", "docs/00-meta/archive-economy-audit.md"]),
        ("lint", "make lint", []),
        ("package_release", "make package-release STAMP=... SLUG=...", ["RELEASE-MANIFEST.json"]),
    ]:
        rows.append({
            "name": name,
            "command": command,
            "listed_in_makefile": name.split('_')[0] in mk or command in mk,
            "outputs": outputs,
        })
    return rows


def build_payload() -> dict:
    tools = ordered_tools()
    buckets = {key: [] for key in CATEGORY_META}
    for tool in tools:
        buckets[tool_bucket(tool)].append(tool)
    payload = {
        "project": "DelayBasin",
        "revision": current_revision(),
        "surface": "VALIDATION-INDEX.json",
        "guide_surface": "docs/00-meta/validation-index.md",
        "derivative_note": "Compact validation inventory; `make lint` still remains the admission wrapper.",
        "tool_count": len(tools),
        "commands": commands(),
        "generated_surfaces": [
            {"surface": "LICENSE", "generator": "tools/gen_external_metadata.py", "role": "external metadata identity surface"},
            {"surface": "CITATION.cff", "generator": "tools/gen_external_metadata.py", "role": "external citation metadata"},
            {"surface": "codemeta.json", "generator": "tools/gen_external_metadata.py", "role": "external software metadata"},
            {"surface": "ro-crate-metadata.json", "generator": "tools/gen_external_metadata.py", "role": "external RO-Crate metadata"},
            {"surface": "SBOM.spdx.json", "generator": "tools/gen_external_metadata.py", "role": "external SBOM metadata"},
            {"surface": "context-pack.json", "generator": "tools/gen_context_pack.py", "role": "compact reentry packet"},
            {"surface": "innovation-packet.json", "generator": "tools/gen_innovation_packet.py", "role": "exact current innovation packet"},
            {"surface": "frontier-ticket.json", "generator": "tools/gen_frontier_ticket.py", "role": "selected-focus handoff"},
            {"surface": "replay-capsule.json", "generator": "tools/gen_replay_capsule.py", "role": "bounded replay-sufficiency card"},
            {"surface": "VALIDATION-INDEX.json", "generator": "tools/gen_validation_index.py", "role": "validation inventory"},
            {"surface": "compact-surface-bundle.json", "generator": "tools/gen_compact_surface_bundle.py", "role": "compact derivative family card"},
            {"surface": "CANARY-RUNS.json", "generator": "tools/gen_canary_runs.py", "role": "executable canary run evidence"},
            {"surface": "docs/00-meta/validation-index.md", "generator": "tools/gen_validation_index.py", "role": "human-facing validation guide"},
            {"surface": "VALIDATION-TOOLCHAIN-MANIFEST.json", "generator": "tools/gen_validation_toolchain_manifest.py", "role": "validation toolchain fingerprint"},
            {"surface": "docs/00-meta/validation-toolchain.md", "generator": "tools/gen_validation_toolchain_manifest.py", "role": "human-facing validation toolchain guide"},
            {"surface": "CURRENTNESS-CUE-AUDIT.json", "generator": "tools/gen_currentness_cue_audit.py", "role": "currentness cue audit"},
            {"surface": "docs/00-meta/currentness-cue-audit.md", "generator": "tools/gen_currentness_cue_audit.py", "role": "human-facing currentness cue audit"},
            {"surface": "PACKAGE-IDENTITY-AUDIT.json", "generator": "tools/gen_package_identity_audit.py", "role": "package identity audit"},
            {"surface": "docs/00-meta/package-identity-audit.md", "generator": "tools/gen_package_identity_audit.py", "role": "human-facing package identity audit"},
            {"surface": "BASIS-PROVENANCE-AUDIT.json", "generator": "tools/gen_basis_provenance_audit.py", "role": "basis provenance audit"},
            {"surface": "docs/00-meta/basis-provenance-audit.md", "generator": "tools/gen_basis_provenance_audit.py", "role": "human-facing basis provenance audit"},
            {"surface": "SCHEMA-COVERAGE-AUDIT.json", "generator": "tools/gen_schema_coverage_audit.py", "role": "schema coverage audit"},
            {"surface": "docs/00-meta/schema-coverage-audit.md", "generator": "tools/gen_schema_coverage_audit.py", "role": "human-facing schema coverage audit"},
            {"surface": "SCHEMA-CONFORMANCE-AUDIT.json", "generator": "tools/gen_schema_conformance_audit.py", "role": "schema conformance audit"},
            {"surface": "docs/00-meta/schema-conformance-audit.md", "generator": "tools/gen_schema_conformance_audit.py", "role": "human-facing schema conformance audit"},
            {"surface": "LINT-IDEMPOTENCE-AUDIT.json", "generator": "tools/gen_lint_idempotence_audit.py", "role": "lint idempotence audit"},
            {"surface": "docs/00-meta/lint-idempotence-audit.md", "generator": "tools/gen_lint_idempotence_audit.py", "role": "human-facing lint idempotence audit"},
            {"surface": "ALIAS-RETENTION-POLICY.json", "generator": "manual/revision", "role": "bounded alias-retention policy"},
            {"surface": "REENTRY-SURFACE-CONFORMANCE.json", "generator": "tools/gen_reentry_surface_conformance.py", "role": "startup-contract witness"},
            {"surface": "RELEASE-MANIFEST.json", "generator": "tools/package_release.py", "role": "packaged bundle identity"},
            {"surface": "FILE-MANIFEST.json", "generator": "tools/gen_release_integrity.py", "role": "per-file release hashes"},
            {"surface": "CHECKSUMS.sha256", "generator": "tools/gen_release_integrity.py", "role": "human-readable release checksums"},
            {"surface": "RELEASE-PROVENANCE.json", "generator": "tools/gen_release_integrity.py", "role": "release integrity provenance"},
            {"surface": "LEDGER-AUDIT.json", "generator": "tools/gen_ledger_audit.py", "role": "continuity ledger audit"},
            {"surface": "docs/00-meta/ledger-audit.md", "generator": "tools/gen_ledger_audit.py", "role": "human-facing ledger audit"},
            {"surface": "ARCHIVE-ECONOMY-AUDIT.json", "generator": "tools/gen_archive_economy_audit.py", "role": "archive economy audit"},
            {"surface": "docs/00-meta/archive-economy-audit.md", "generator": "tools/gen_archive_economy_audit.py", "role": "human-facing archive economy audit"},
            {"surface": "CANARY-PROTOCOL.json", "generator": "manual/revision", "role": "bounded canary evidence protocol"},
        ],
        "coverage_scope": {
            "claim": "This inventory names the major command surfaces and the main validation families behind `make lint`; it is not a proof graph for every single tool-level semantic distinction.",
            "non_claim": "Do not treat this surface as a workflow-state machine, lint court, or exhaustive per-check theorem map. Reopen the named governing surfaces before inheriting any stronger claim.",
        },
        "families": [],
    }
    for key, meta in CATEGORY_META.items():
        payload["families"].append({
            "id": key,
            "label": meta["label"],
            "coverage_claim": meta["claim"],
            "governing_surface_hints": meta["surfaces"],
            "tool_count": len(buckets[key]),
            "tools": buckets[key],
        })
    return payload


def render_md(payload: dict) -> str:
    lines = []
    lines.append("# Validation index")
    lines.append("")
    lines.append("This is a compact human-facing inventory for what the current checked command surface is doing.")
    lines.append("It exists so `make lint` can stay the admission wrapper without becoming a discovery black box.")
    lines.append("")
    lines.append("## Commands")
    for row in payload["commands"]:
        outputs = ", ".join(f"`{x}`" for x in row["outputs"]) if row["outputs"] else "admission wrapper / no direct artifact"
        lines.append(f"- `{row['command']}` — {outputs}")
    lines.append("")
    lines.append("## Coverage honesty")
    lines.append(f"- {payload['coverage_scope']['claim']}")
    lines.append(f"- {payload['coverage_scope']['non_claim']}")
    lines.append("")
    lines.append("## Main validation families")
    for family in payload["families"]:
        lines.append(f"### {family['label']}")
        lines.append(f"- Tool count: {family['tool_count']}")
        lines.append(f"- Coverage claim: {family['coverage_claim']}")
        lines.append(f"- Governing surface hints: {', '.join('`'+x+'`' for x in family['governing_surface_hints'])}")
        if family['tools']:
            preview = ", ".join(f"`{x}`" for x in family['tools'][:8])
            if len(family['tools']) > 8:
                preview += ", …"
            lines.append(f"- Representative tools: {preview}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


payload = build_payload()
OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
OUT_MD.write_text(render_md(payload), encoding="utf-8")
print(f"wrote {OUT_JSON}")
print(f"wrote {OUT_MD}")
