#!/usr/bin/env python3
import copy
import hashlib
import json
import math
from pathlib import Path

from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

CLAIM_ID = "anondht.reader_privacy.workedexample.v0"
TW_NAME = "tw.reader_24h.q500.v1"
RELEASE_ID = "worked-example-draft-194"
NOTE_VERSION = "1.94"
PRIMARY_EXPOSURE_LABEL = "enf.primary.linkability.v1"
PLAN_CATALOG_VERSION = "worked-example-plan-catalog-v2"
COMPARE_PROFILE_ID = "worked-example-compare-profile-v1"
INVENTORY_ID = "worked-example-artifact-inventory-v1"
MANIFEST_ID = "worked-example-support-manifest-v1"

Q = 500
FALLBACK_RATE_HAT = 0.05
R_PI_UPPER = 1.2
P_OBS_UPPER = 0.02
RHO_UPPER = 0.01
RAW_TIERS = [
    {"tier": "CSET", "raw_b": 1.40},
    {"tier": "TIME", "raw_b": 0.30},
    {"tier": "CONG", "raw_b": 0.15},
]
PRIMARY_LINKABILITY_BOUND = 0.0

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj) -> str:
    data = json.dumps(obj, indent=2, sort_keys=True).encode() + b"\n"
    path.write_bytes(data)
    return sha256_bytes(data)



def canon_bytes(obj) -> bytes:
    # Stable canonicalization for ids: sorted keys, no whitespace.
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_id(obj) -> str:
    return "sha256:" + sha256_bytes(canon_bytes(obj))


FALLBACK_CONTACT_SURFACE = {
    "method": "GET",
    "url": "https://cid.contact/routing/v1/providers",
    "filter_protocols": ["transport-bitswap"],
    "timeouts": {"http_router": "30s", "routing": "60s"},
}
FALLBACK_CONTACT_SURFACE_ID = sha256_id(FALLBACK_CONTACT_SURFACE)

FALLBACK_EMPTY_RESULT_EQUIVALENCE = {
    "server_preferred_status": 200,
    "client_must_treat_404_as_empty_result": True,
    "source": "Routing V1 interoperability / IPIP-0513",
}


# Human-facing labels for the worked example (used in the paper); ids are digest-bound claim fields.
FALLBACK_CCT_LABEL = "enf.fallback.cct.v1"
FALLBACK_VECTOR_LABEL = "enf.fallback.vector.v1"
PATHSELECT_LABEL = "enf.pathselect.fallbackbit.v1"

PROFILING_LABEL = "enf.profiling.retrybucket.v1"

PROFILING_PREFIXFETCH_LABEL = "enf.profiling.prefixfetch.v1"
PROFILING_PREFIXFETCH_STATECOND_LABEL = "enf.profiling.prefixfetch.statecond.v1"

PROFILING_CONTACT_COARSENED_LABEL = "enf.profiling.contact.coarsened.v1"

ENF_DECLS = {
    PRIMARY_EXPOSURE_LABEL: {
        "enf_schema": "enf.v1",
        "label": PRIMARY_EXPOSURE_LABEL,
        "tier": "primary_surface",
        "projection": "identity_to_destination_linkability",
        "unit": "lookup",
        "conditioning": {"separation_class": "sep.nr1"},
        "note": "Assumption-qualified primary-path surface for the worked example.",
    },
    FALLBACK_CCT_LABEL: {
        "enf_schema": "enf.v1",
        "label": FALLBACK_CCT_LABEL,
        "tier": "Tier2",
        "projection": "committee_contact_trace_failures",
        "unit": "lookup",
        "conditioning": {"committee_partition": "public"},
        "note": "Fallback ordered contact/failure trace (Tier 2) for the worked example.",
    },
    FALLBACK_VECTOR_LABEL: {
        "enf_schema": "enf.v1",
        "label": FALLBACK_VECTOR_LABEL,
        "tier": "TieredVector",
        "projection": "fallback_vector_contact_time_congestion",
        "unit": "lookup",
        "conditioning": {"bucket_coarsening": "public"},
        "note": "Tiered fallback observation vector (contact/time/congestion) for the worked example.",
    },
    PATHSELECT_LABEL: {
        "enf_schema": "enf.v1",
        "label": PATHSELECT_LABEL,
        "tier": "Tier0",
        "projection": "fallback_indicator_stream",
        "unit": "lookup",
        "conditioning": {"policy": "primary_or_fallback"},
        "note": "Fallback-indicator witness stream used by the path-selection tax.",
    },
    PROFILING_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_LABEL,
        "tier": "Tier1",
        "projection": "retry_bucket_trace",
        "unit": "lookup",
        "conditioning": {"bucket_width": "250ms", "window": "24h"},
        "note": "Profiling/equalization surface: a coarse retry-bucket trace used only to exercise the evidence_id interface in the worked example.",
    },

    PROFILING_PREFIXFETCH_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_PREFIXFETCH_LABEL,
        "tier": "Tier1",
        "projection": "prefix_fetch_signature",
        "unit": "lookup",
        "conditioning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix"},
        "note": "Profiling/equalization surface: a toy prefix-fetch signature used only to exercise a second evidence_id wiring path in the worked example (variant receipt).",
    },

    PROFILING_PREFIXFETCH_STATECOND_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_PREFIXFETCH_STATECOND_LABEL,
        "tier": "Tier1",
        "projection": "prefix_fetch_signature",
        "unit": "lookup",
        "conditioning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class:fresh|stale"},
        "note": "Profiling/equalization surface: prefix-fetch signature conditioned on a published bucket-staleness witness; used only to exercise conditional-witness plumbing (state-conditioned variant receipt).",
    },
PROFILING_CONTACT_COARSENED_LABEL: {
    "enf_schema": "enf.v1",
    "label": PROFILING_CONTACT_COARSENED_LABEL,
    "tier": "Tier1",
    "projection": "contact_set_hash (coarsened)",
    "unit": "lookup",
    "conditioning": {"source_projection": "contact_set_hash", "coarsening": "sig2 = first2bits(sha256(serialized_contact_set))"},
    "note": "Profiling/equalization surface illustrating Synthesis~28: a high-cardinality contact-set hash is declared, but audits are performed on a deterministic coarsening (2-bit signature) to keep the alphabet sample-feasible (coarsening variant receipt).",
},




}

ENF_IDS = {label: sha256_id(decl) for label, decl in ENF_DECLS.items()}

PRIMARY_EXPOSURE = ENF_IDS[PRIMARY_EXPOSURE_LABEL]
FALLBACK_CCT_EXPOSURE = ENF_IDS[FALLBACK_CCT_LABEL]
FALLBACK_VECTOR_EXPOSURE = ENF_IDS[FALLBACK_VECTOR_LABEL]
PATHSELECT_EXPOSURE = ENF_IDS[PATHSELECT_LABEL]
PROFILING_EXPOSURE = ENF_IDS[PROFILING_LABEL]
PREFIXFETCH_EXPOSURE = ENF_IDS[PROFILING_PREFIXFETCH_LABEL]
PREFIXFETCH_STATECOND_EXPOSURE = ENF_IDS[PROFILING_PREFIXFETCH_STATECOND_LABEL]
PROFILING_CONTACT_COARSENED_EXPOSURE = ENF_IDS[PROFILING_CONTACT_COARSENED_LABEL]

TW_DECL = {
    "tw_schema": "tw.v1",
    "label": TW_NAME,
    "secret": "queried_content_id_bucket",
    "unit": "lookup",
    "window": {"type": "sliding", "duration": "24h"},
    "usage": {"Q_upper": Q, "status": "policy_bound"},
    "active": {"template": "BossFight_B", "selective_failure_in_scope": True},
    "background": {"Q": "none", "note": "Worked example treats primary separation as a policy declaration and budgets only fallback surfaces."},
}
TW_ID = sha256_id(TW_DECL)

exposure_registry = {
    "registry_id": "worked-example-enf-registry-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "entries": [
        {"label": label, "exposure_nf_id": ENF_IDS[label], "enf": ENF_DECLS[label]}
        for label in sorted(ENF_DECLS.keys())
    ],
    "note": "Label-to-ENF-ID binding for the worked example. Labels are human-facing; exposure_nf_id is the digest-bound claim field.",
}
exposure_registry_digest = write_json(ART / "example_exposure_nf_registry.json", exposure_registry)

tw_decl_obj = {
    "tw_decl_id": "worked-example-tw-decl-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "label": TW_NAME,
    "tw_id": TW_ID,
    "tw": TW_DECL,
    "note": "Threat/window declaration for the worked example; tw_id is the digest-bound claim field.",
}
tw_decl_digest = write_json(ART / "example_tw_decl.json", tw_decl_obj)

def attenuated_bits(raw_b: float, p: float) -> float:
    return math.log2((1.0 - p) + p * (2.0 ** raw_b))


vector = []
for item in RAW_TIERS:
    eff = attenuated_bits(item["raw_b"], P_OBS_UPPER)
    vector.append({
        "tier": item["tier"],
        "p": P_OBS_UPPER,
        "raw_b": item["raw_b"],
        "effective_b": eff,
        "status": {"p": "policy_upper_bound", "raw_b": "illustrative_input"},
    })

fallback_cset_bits = vector[0]["effective_b"]
fallback_summary_bits = sum(v["effective_b"] for v in vector)
selection_tax_bits = math.log2(R_PI_UPPER)
total_summary_bits = math.log2(
    FALLBACK_RATE_HAT * (2.0 ** fallback_summary_bits)
    + (1.0 - FALLBACK_RATE_HAT) * (2.0 ** PRIMARY_LINKABILITY_BOUND)
) + selection_tax_bits

state_decl_core = {
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "state_contract_id": "stateadj.publicbucket.v1",
    "cache_policy": {
        "bucket_coarsening": "kademlia_prefix_bucket",
        "staleness_trigger": "public_bucket_staleness",
        "cache_key_scope": "bucket_level",
    },
    "routing_state": {
        "refresh_schedule": "6h_public_timer",
        "refresh_trigger": "time_only",
    },
    "rate_limit": {
        "Q_upper": Q,
        "window": "24h",
        "status": "policy_bound",
    },
    "included_state_surfaces": [
        "bucket_level_cache_staleness",
        "public_timer_routing_refresh",
        "24h_rate_limit_counter",
    ],
    "excluded_state_surfaces": [
        "long_lived_routing_table_content_beyond_public_refresh_schedule",
        "persistent_per_client_randomness_beyond_the_24h_window",
        "provider_side_or_server_side_state_not_named_in_the_receipt_bundle",
    ],
    "accounting_scope": "24h receipt-level summary with public-bucket fallback triggers and declared public timers only",
    "caveat": "Published summaries are 24h receipt-level summaries, not lifetime state-aware theorems. Persistent state may correlate successive lookups.",
}
state_decl_id = sha256_id(state_decl_core)
state_decl = dict(state_decl_core)
state_decl["state_decl_id"] = state_decl_id
state_decl_digest = write_json(ART / "example_state_decl.json", state_decl)

state_decl_registry = {
    "registry_id": "worked-example-state-decl-registry-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "entries": [
        {
            "state_contract_id": state_decl_core["state_contract_id"],
            "state_decl_id": state_decl_id,
            "state_decl": state_decl_core,
        }
    ],
    "canonicalization": "state_decl_id = sha256(canon(state_decl_core)) where canon uses sorted keys and no whitespace",
    "note": "State-declaration binding for the worked example; state_contract_id is human-facing, state_decl_id is the digest-bound claim field.",
}
state_decl_registry_digest = write_json(ART / "example_state_decl_registry.json", state_decl_registry)

effective_surface_resolution = {
    "resolution_id": "worked-example-effective-surface-resolution-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "state_decl_id": state_decl_id,
    "precedence_stack": [
        {"layer": "process_environment", "example_knobs": ["IPFS_HTTP_ROUTERS", "IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS"], "owner": "Synthesis~30"},
        {"layer": "explicit_config", "example_knobs": ["Routing.DelegatedRouters", "HTTPRetrieval.Allowlist", "HTTPRetrieval.Denylist", "Routing.IgnoreProviders"], "owner": "Synthesis~30"},
        {"layer": "autoconf_auto_expansion", "example_knobs": ["AutoConf.URL", "AutoConf.RefreshInterval", "RAINBOW_AUTOCONF_URL", "RAINBOW_AUTOCONF_REFRESH"], "owner": "Synthesis~30"},
        {"layer": "receipt_line_item", "example_knobs": ["contact_surface_id", "contact_surface"], "owner": "Synthesis~12"},
        {"layer": "projection_schema", "example_knobs": ["exposure_nf_id", "empty_result_equivalence", "streaming_or_status_semantics"], "owner": "Synthesis~3"},
    ],
    "resolved_state_defaults": {
        "router_selection_source": "autoconf+explicit pinning under state_decl_id",
        "request_shaping_defaults": {
            "filter_protocols": ["transport-bitswap"],
            "timeouts": {"http_router": "30s", "routing": "60s"},
            "empty_result_equivalence": FALLBACK_EMPTY_RESULT_EQUIVALENCE,
        },
        "note": "Long-lived control-plane selectors and fallback rules live under state_decl_id; per-contact service semantics stay with contact_surface_id.",
    },
    "line_item_bindings": [
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "effective_contact_surface": FALLBACK_CONTACT_SURFACE,
            "effective_contact_surface_digest_rule": "sha256(canon(effective_contact_surface))",
            "ownership_partition": {
                "state_decl_id_owns": ["router selection precedence", "allow/deny and ignore-provider policy", "autoconf refresh and downgrade rules"],
                "contact_surface_id_owns": ["HTTP method", "full path-scoped URL", "declared request-shaping defaults", "declared time budgets"],
                "exposure_nf_id_owns": ["committee-contact trace schema", "response/status interpretation", "empty-result equivalence", "streaming/pacing semantics"],
            },
        }
    ],
    "note": "Digest-bound worked-example adjunct for assembling the effective replay surface. It is not a new receipt primitive. Response/status semantics (for example 200-empty vs client-interpreted 404-empty compatibility) are treated as ENF/projection semantics, not state drift.",
}
effective_surface_resolution_digest = write_json(ART / "example_effective_surface_resolution.json", effective_surface_resolution)

primary_surface_manifest = {
    "claim_id": CLAIM_ID,
    "exposure_nf_id": PRIMARY_EXPOSURE,
    "surface": "identity_to_destination_linkability",
    "separation_class": "sep.nr1",
    "declared_value_bits_per_lookup": PRIMARY_LINKABILITY_BOUND,
    "rho_upper": RHO_UPPER,
    "rho_status": "policy_upper_bound",
    "status": "policy_declaration",
    "valid_if": [
        "relay and router operator sets are declared disjoint within the threat window",
        "relay egress telemetry is not joined with router request logs within the threat window",
        "relay rotation stays at or below the declared 24h horizon",
        "primary traffic is served only through the declared relay set",
    ],
    "invalidators": [
        "declared relay-router collusion within the threat window",
        "shared telemetry or common log joins across relay and router",
        "relay stickiness exceeds the declared 24h horizon without lineage update",
        "primary traffic bypasses the declared relay set",
    ],
    "evidence_hooks": {
        "operator_roster": "support://primary/operators.example",
        "config_snapshot": "support://primary/config.example",
        "telemetry_separation_attestation": "support://primary/telemetry.example",
    },
}
primary_surface_digest = write_json(ART / "example_primary_surface_manifest.json", primary_surface_manifest)

user_watch_policy = {
    "claim_id": CLAIM_ID,
    "primary_user_surface_exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
    "compare_fields": [
        "claim_pointer",
        "exposure_nf_id",
        "receipt_digest",
        "log_anchor.log_id",
        "consistency_context.checkpoint",
    ],
    "alarms": [
        {
            "when": "claim_pointer changes without a lineage note in the release-bound claim objects",
            "severity": "high",
            "action": "inspect new claim lineage before trusting the deployment",
        },
        {
            "when": "exposure_nf_id changes while claim_pointer remains the same",
            "severity": "high",
            "action": "treat as claim-surface drift and compare the new lineage relation",
        },
        {
            "when": "receipt_digest changes but no newer anchored checkpoint is supplied",
            "severity": "high",
            "action": "treat as an anchoring failure until the log context is refreshed",
        },
        {
            "when": "log_anchor.log_id changes",
            "severity": "medium",
            "action": "require a fresh trust decision and a new consistency chain",
        },
        {
            "when": "consistency proofs cannot be fetched for successive checkpoints",
            "severity": "medium",
            "action": "treat as a publication-integrity problem",
        },
    ],
    "note": "Operational client watch policy adjunct; not part of the minimal UVI tuple.",
}
user_watch_digest = write_json(ART / "example_user_watch_policy.json", user_watch_policy)

change_control = {
    "claim_id": CLAIM_ID,
    "change_control_id": "chgctl.receiptchain.v1",
    "release_action_matrix_id": "worked-example-release-action-matrix-v1",
    "release_id": RELEASE_ID,
    "interface_guard": {
        "required_exposures": [
            PRIMARY_EXPOSURE,
            FALLBACK_CCT_EXPOSURE,
            FALLBACK_VECTOR_EXPOSURE,
            PATHSELECT_EXPOSURE,
            PROFILING_EXPOSURE,
        ],
        "tw_id": TW_ID,
        "primary_separation_class": "sep.nr1",
        "primary_rho_upper": RHO_UPPER,
        "state_contract_id": state_decl["state_contract_id"],
        "state_decl_id": state_decl["state_decl_id"],
    },
    "refresh_only_if": [
        "required exposures are unchanged",
        "tw_id is unchanged",
        "primary separation class remains sep.nr1",
        "state_decl_id remains stable for stateadj.publicbucket.v1",
        "published total summary stays at or below 0.30 bits/lookup",
    ],
    "replay_changed_surfaces_if": [
        "budget_value changes on enf.fallback.vector.v1",
        "fallback trigger class changes",
        "p_obs upper bound changes",
        "watch-policy or replay-plan digests change",
    ],
    "full_recertify_if": [
        "any required exposure is removed or renamed",
        "tw_id changes",
        "primary separation class changes",
        "state_decl_id changes (state surface drift)",
        "lineage relation for a required exposure is new-interface",
        "published total summary exceeds 0.30 bits/lookup",
    ],
    "workflow_owner": "CertifiedC_disagreement_gated_recertification",
    "notes": [
        "Refresh-only means rebind the release receipt and transparency anchor without changing the certified interface.",
        "Changed-surface replay means rerun the named Evaluation2/Evaluation3 plans on the changed slices and issue a fresh notarized comparison.",
        "Full recertification means the certified interface changed and the deployment should not rely on a zero-label shortcut without a Certified C style disagreement gate or a fresh audit.",
        "Field-family-to-action defaults are published separately in example_release_action_matrix.json so users and auditors can classify a diff without re-reading every owner note.",
        "Per-action publication duties are published separately in example_release_obligation_profile.json so maintainers can tell what public outputs must be refreshed after classification.",
    ],
}
change_control_digest = write_json(ART / "example_change_control.json", change_control)

release_action_matrix = {
    "action_matrix_id": "worked-example-release-action-matrix-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "severity_order": ["refresh_only", "replay_changed_surfaces", "full_recertification"],
    "resolution_rule": "Match changed fields against rule match_terms; the highest-severity matched rule wins. If a contact-surface change also changes reader-visible transcript semantics, escalate by minting a new exposure_nf_id and let the interface-drift rule dominate.",
    "rules": [
        {
            "rule_id": "publication-refresh-only",
            "match_terms": ["log_checkpoint", "user_watch_policy"],
            "owner_notes": ["Synthesis~9", "Synthesis~13"],
            "default_classification": "refresh_only",
            "why": "Transparency-anchor refreshes and watch-text updates change publication/discovery metadata, not the certified privacy interface.",
        },
        {
            "rule_id": "plan-or-proof-replay",
            "match_terms": ["plan_spec_id", "plan_catalog_digest", "replay-plan", "watch-policy or replay-plan digests change"],
            "owner_notes": ["Synthesis~18", "Synthesis~20"],
            "default_classification": "replay_changed_surfaces",
            "escalate_if": ["the plan change is P2 claim-affecting semantics under Synthesis~18"],
            "why": "A changed replay promise forces at least a rerun/republication even when the interface ids are stable.",
        },
        {
            "rule_id": "contact-or-budget-replay",
            "match_terms": ["contact_surface_id", "obs_model.vector[*].p", "obs_model.p_obs_upper", "budget_value", "knobs", "evidence_id", "fallback trigger class"],
            "owner_notes": ["Synthesis~12", "Synthesis~18", "Synthesis~30"],
            "default_classification": "replay_changed_surfaces",
            "escalate_if": ["the changed contact surface induces a new reader-visible transcript semantics and therefore a new exposure_nf_id"],
            "why": "Same certified interface, but new effective service surface, evidence, or declared budget arithmetic requires replay and a fresh notarized comparison.",
        },
        {
            "rule_id": "interface-or-state-recertify",
            "match_terms": ["tw_id", "state_decl_id", "exposure_nf_id", "required exposure", "new-interface", "primary separation class"],
            "owner_notes": ["Synthesis~3", "Synthesis~4", "Synthesis~18", "Synthesis~30", "Certified~C"],
            "default_classification": "full_recertification",
            "why": "Threat-window, state-surface, projection, or primary-separation changes alter the certified interface or its guard and break zero-label continuity.",
        },
    ],
    "case_resolution_examples": [
        {
            "case_id": "refresh-only-A",
            "matched_rule_ids": ["publication-refresh-only"],
            "classification": "refresh_only",
        },
        {
            "case_id": "replay-required-B",
            "matched_rule_ids": ["contact-or-budget-replay"],
            "classification": "replay_changed_surfaces",
        },
        {
            "case_id": "full-recertification-C",
            "matched_rule_ids": ["interface-or-state-recertify"],
            "classification": "full_recertification",
        },
    ],
    "note": "Worked-example adjunct turning field-family diffs into default release actions. It instantiates the Synthesis~18 drift taxonomy for this bundle and is intended for user/auditor diff triage, not as a new receipt primitive.",
}
release_action_matrix_digest = write_json(ART / "example_release_action_matrix.json", release_action_matrix)

release_obligation_profile = {
    "obligation_profile_id": "worked-example-release-obligation-profile-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "release_action_matrix_id": release_action_matrix["action_matrix_id"],
    "resolution_rule": "Classify the diff first using the release-action matrix, then publish at least the output roles listed for the winning action class. Later notes can cite the obligation profile instead of rephrasing release-management duties.",
    "classes": [
        {
            "action_class": "refresh_only",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_user_pointer_or_watch_text", "binding": "example_uvi.json or example_user_watch_policy.json when changed"},
                {"role": "fresh_log_lineage", "binding": "transparency checkpoint / consistency context"},
            ],
            "continuity_status": "same_certified_interface_no_replay_needed",
            "note": "Publication metadata changed, but the certified interface and replay evidence remain reusable.",
        },
        {
            "action_class": "replay_changed_surfaces",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_compare_report", "binding": "example_compare_report.json"},
                {"role": "fresh_replay_verdict", "binding": "example_verifier_report.json"},
                {"role": "fresh_successor_continuity_verdict", "binding": "example_successor_continuity_verdict.json"},
                {"role": "fresh_successor_lineage_notice", "binding": "example_successor_lineage_notice.json"},
            ],
            "continuity_status": "same_certified_interface_replayed_surfaces",
            "note": "Same interface, changed budget-bearing surfaces: rerun the declared evaluators and publish the small cross-release outcome objects.",
        },
        {
            "action_class": "full_recertification",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_interface_ids", "binding": "tw_id / state_decl_id / exposure_nf_id family"},
                {"role": "recertification_packet", "binding": "Certified~C style disagreement gate or fresh audit packet"},
                {"role": "user_facing_lineage_notice", "binding": "release note / continuity stop notice"},
            ],
            "continuity_status": "no_automatic_continuity",
            "note": "Interface or guard drift breaks zero-label continuity and must be published as a new certified surface, not just a replay delta.",
        },
    ],
    "case_resolution_examples": [
        {
            "case_id": "refresh-only-A",
            "action_class": "refresh_only",
            "minimum_roles": ["fresh_release_binding", "fresh_log_lineage"],
        },
        {
            "case_id": "replay-required-B",
            "action_class": "replay_changed_surfaces",
            "minimum_roles": ["fresh_release_binding", "fresh_compare_report", "fresh_replay_verdict", "fresh_successor_continuity_verdict", "fresh_successor_lineage_notice"],
        },
        {
            "case_id": "full-recertification-C",
            "action_class": "full_recertification",
            "minimum_roles": ["fresh_release_binding", "fresh_interface_ids", "recertification_packet", "user_facing_lineage_notice"],
        },
    ],
    "note": "Worked-example adjunct mapping action classes to the minimal public outputs that should be refreshed after classification. It is publication policy, not a new receipt primitive.",
}
release_obligation_profile_digest = write_json(ART / "example_release_obligation_profile.json", release_obligation_profile)

successor_tw_decl_C = copy.deepcopy(TW_DECL)
successor_tw_decl_C["label"] = "tw.reader_24h.q750.v2"
successor_tw_decl_C["usage"] = {"Q_upper": 750, "status": "policy_bound"}
successor_tw_id_C = sha256_id(successor_tw_decl_C)
successor_state_decl_core_C = copy.deepcopy(state_decl_core)
successor_state_decl_core_C["tw_id"] = successor_tw_id_C
successor_state_decl_core_C["state_contract_id"] = "stateadj.prefixcache.v2"
successor_state_decl_core_C["cache_policy"]["staleness_trigger"] = "prefix_level_staleness"
successor_state_decl_id_C = sha256_id(successor_state_decl_core_C)

drift_cases = {
    "catalog_id": "worked-example-drift-cases-v1",
    "claim_id": CLAIM_ID,
    "base_release_id": RELEASE_ID,
    "cases": [
        {
            "case_id": "refresh-only-A",
            "classification": "refresh_only",
            "successor_release_id": RELEASE_ID + "a",
            "changed_fields": [
                "release_receipt.log_checkpoint",
                "example_user_watch_policy.json text only",
            ],
            "unchanged_guard_fields": change_control["interface_guard"],
            "published_total_summary_bits_per_lookup": total_summary_bits,
            "required_action": "rebind release receipt, publish fresh checkpoint lineage, keep prior certification surface",
        },
        {
            "case_id": "replay-required-B",
            "classification": "replay_changed_surfaces",
            "successor_release_id": RELEASE_ID + "b",
            "changed_fields": [
                "example_receipt.json: enf.fallback.vector.v1 obs_model.vector[*].p",
                "example_receipt.json: enf.fallback.cct.v1 obs_model.p_obs_upper",
            ],
            "old_values": {"p_obs_upper": 0.02},
            "new_values": {"p_obs_upper": 0.015},
            "unchanged_guard_fields": change_control["interface_guard"],
            "required_action": "rerun eval-fallback-cct-v1 and eval-fallback-vector-v1, publish fresh notarized comparison, update release lineage",
        },
        {
            "case_id": "full-recertification-C",
            "classification": "full_recertification",
            "successor_release_id": RELEASE_ID + "c",
            "changed_fields": [
                "tw_id",
                "example_state_decl.json: state_decl_id",
                "example_state_decl.json: cache_policy.staleness_trigger",
            ],
            "old_values": {
                "tw_id": TW_ID,
                "state_contract_id": state_decl["state_contract_id"],
                "state_decl_id": state_decl["state_decl_id"],
                "staleness_trigger": "public_bucket_staleness"
            },
            "new_values": {
                "tw_id": successor_tw_id_C,
                "state_contract_id": successor_state_decl_core_C["state_contract_id"],
                "state_decl_id": successor_state_decl_id_C,
                "staleness_trigger": successor_state_decl_core_C["cache_policy"]["staleness_trigger"]
            },
            "required_action": "treat as certified-interface change and require disagreement-gated recertification before continuity claims",
        },
    ],
}
drift_cases_digest = write_json(ART / "example_drift_cases.json", drift_cases)


# Replay plans: plan_id is a stable workflow handle; plan_spec_id digest-binds the replay semantics.
# This prevents ``same plan_id, different replay'' drift from hiding in prose.
PLAN_SPECS = [
    {
        "plan_id": "eval-primary-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation1_notarized_certificate_checks",
            "checks": [
                "exposure-id and separation-class match manifest",
                "relay/router policy identities match declared knobs",
                "attempt lineage matches release receipt",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_release_receipt.json",
                "example_primary_surface_manifest.json",
            ],
            "expected_output": "surface-bound notarized validation record for enf.primary.linkability.v1",
        },
    },
    {
        "plan_id": "eval-fallback-cct-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation3_calibration_plus_Evaluation1_notarization",
            "checks": [
                "recompute attenuated contact-surface bound from raw_b and p_obs",
                "check Q window and retry policy against declared knobs",
                "bind replay output to receipt digest",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "notarized attempt log (support artifact on request)",
            ],
            "expected_output": "recomputed fallback contact-surface budget and notarized comparison",
        },
    },
    {
        "plan_id": "eval-fallback-vector-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation3_calibration_plus_Evaluation1_notarization",
            "checks": [
                "recompute per-tier effective values from raw_b and p",
                "sum tier contributions under declared conditional-independence flag",
                "verify state declaration digest and schedule/equalization knobs",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "timing/certificate references named by the support bundle",
            ],
            "expected_output": "recomputed fallback vector summary and notarized comparison",
        },
    },
    {
        "plan_id": "eval-pathselect-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation2_advantage_contracts_plus_Evaluation1_notarization",
            "checks": [
                "recompute selection-tax term log2(R_pi)",
                "compare audit/live fallback-indicator behavior under the declared trigger class",
                "bind the monitored fallback-rate estimate to the declared state contract",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "audit/live fallback-indicator logs (support artifact on request)",
            ],
            "expected_output": "selection-tax replay record plus audit/live comparability note",
        },
    },
    {
        "plan_id": "eval-profiling-eq-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_profiling_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published evidence object",
                "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID) and TW-ID match the receipt"
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_profiling_evidence.json"
            ],
            "expected_output": "recomputed (eta,delta) equalization summary and notarized comparison"
        },
    },

    {
        "plan_id": "eval-profiling-prefixfetch-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_prefixfetch_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published prefix-fetch evidence object",
                "recompute (eta,delta) from the prefix evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID) and TW-ID match the variant receipt"
            ],
            "required_inputs": [
                "example_receipt_prefixfetch_variant.json",
                "example_profiling_evidence_prefixfetch.json"
            ],
            "expected_output": "recomputed (eta,delta) prefix-fetch equalization summary and notarized comparison"
        },
    },

    {
        "plan_id": "eval-profiling-prefixfetch-statecond-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_prefixfetch_statecond_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published state-conditioned prefix-fetch evidence object",
                "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID), TW-ID, and witness semantics match the variant receipt"
            ],
            "required_inputs": [
                "example_receipt_prefixfetch_statecond_variant.json",
                "example_profiling_evidence_prefixfetch_statecond.json"
            ],
            "expected_output": "recomputed (eta,delta) state-conditioned prefix-fetch equalization summary and notarized comparison"
        },
    },

{
    "plan_id": "eval-profiling-contact-coarsened-v1",
    "plan_spec": {
        "workflow_owner": "AnonymityB_contact_coarsening_audit_plus_Evaluation1_notarization",
        "checks": [
            "verify evidence_id binds the published coarsened-contact evidence object",
            "verify coarsening_map_id binds the declared deterministic partition map",
            "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
            "confirm the projection schema (ENF-ID), TW-ID, and coarsening map match the variant receipt"
        ],
        "required_inputs": [
            "example_receipt_contact_coarsened_variant.json",
            "example_profiling_evidence_contact_coarsened.json",
            "example_coarsening_map_contact.json"
        ],
        "expected_output": "recomputed (eta,delta) coarsened-contact equalization summary and notarized comparison"
    },
},


]
for _p in PLAN_SPECS:
    _p["plan_spec_id"] = sha256_id(_p["plan_spec"])
PLAN_SPEC_ID_BY_PLAN_ID = {_p["plan_id"]: _p["plan_spec_id"] for _p in PLAN_SPECS}


# Profiling/equalization evidence object (receipt-grade via evidence_id).
# Profiling/equalization evidence object (receipt-grade via evidence_id).
# We treat the projection as a finite alphabet X (bucketed retry-trace summary),
# and publish a conservative (eta, delta_slack) max-divergence-style equalization summary
# derived from exact binomial (Clopper--Pearson) intervals + a union bound.

PROF_BINS = ["0-250ms", "250-500ms", "500-750ms", "750-1000ms", "1000ms+"]
PROF_COUNTS = {
    "k0": [1460, 550, 240, 145, 5],
    "k1": [1390, 600, 264, 146, 0],
    "k2": [1438, 576, 240, 144, 2],
}
PROF_N = {k: sum(v) for k, v in PROF_COUNTS.items()}
assert len(set(PROF_N.values())) == 1
_PROF_N = next(iter(PROF_N.values()))

def clopper_pearson_interval(k: int, n: int, alpha: float):
    # Two-sided Clopper--Pearson interval with per-bin miscoverage alpha.
    a = alpha / 2.0
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1.0 - a, k + 1, n - k))
    return lo, hi

PROF_DELTA_STAT = 0.01
m = len(PROF_BINS)
K = len(PROF_COUNTS)
PROF_ALPHA = PROF_DELTA_STAT / (m * K)

# Compute per-(k,bin) intervals.
_prof_intervals = {k: [clopper_pearson_interval(PROF_COUNTS[k][i], _PROF_N, PROF_ALPHA) for i in range(m)]
                   for k in PROF_COUNTS.keys()}

# Rare-support set B: bins where at least one class has zero lower support.
_prof_rare_idx = [i for i in range(m) if min(_prof_intervals[k][i][0] for k in PROF_COUNTS.keys()) == 0.0]

# Deterministic summaries (see Anonymity~B).
def _eta_bits():
    eta = 0.0
    for k in PROF_COUNTS.keys():
        for kp in PROF_COUNTS.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m):
                if i in _prof_rare_idx:
                    continue
                lo = _prof_intervals[kp][i][0]
                hi = _prof_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)

def _delta_slack():
    # Worst-case upper bound on numerator mass that lands in the rare-support set.
    return float(max(sum(_prof_intervals[k][i][1] for i in _prof_rare_idx) for k in PROF_COUNTS.keys()))

PROF_ETA_BITS = _eta_bits()
PROF_DELTA_SLACK = _delta_slack()

profiling_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": ENF_IDS[PROFILING_LABEL],
    "tw_id": TW_ID,
    "projection": "retry_bucket_trace",
    "binning": {"bucket_width": "250ms", "max_span": "5s", "alphabet": "finite"},
    "classes": {k: {"n": _PROF_N} for k in PROF_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection",
        "delta_stat": PROF_DELTA_STAT,
        "alpha_per_bin": PROF_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(PROF_ETA_BITS, 6),
        "delta_slack": round(PROF_DELTA_SLACK, 6),
        "rare_bins": [PROF_BINS[i] for i in _prof_rare_idx],
        "note": "Synthetic toy counts; the purpose is to exercise evidence_id wiring and the CP+union-bound computation, not to claim a real deployment bound."
    },
    "table": [
        {
            "bin": PROF_BINS[i],
            "count": {k: int(PROF_COUNTS[k][i]) for k in PROF_COUNTS.keys()},
            "p_hat": {k: round(PROF_COUNTS[k][i] / _PROF_N, 6) for k in PROF_COUNTS.keys()},
            "cp_interval": {k: [round(_prof_intervals[k][i][0], 6), round(_prof_intervals[k][i][1], 6)] for k in PROF_COUNTS.keys()},
        }
        for i in range(m)
    ],
}
profiling_evidence_id = sha256_id(profiling_evidence_core)
profiling_evidence_obj = {"evidence_id": profiling_evidence_id, "evidence": profiling_evidence_core}
profiling_evidence_digest = write_json(ART / "example_profiling_evidence.json", profiling_evidence_obj)


# Optional second profiling evidence object: prefix-fetch signature (variant receipt).
PFX_BINS = ["pf:00", "pf:01", "pf:10", "pf:11", "other"]
PFX_COUNTS = {
    "k0": [1000, 1000, 1000, 995, 5],
    "k1": [1005, 995, 1000, 1000, 0],
    "k2": [990, 1010, 1000, 998, 2],
}
PFX_N = {k: sum(v) for k, v in PFX_COUNTS.items()}
assert len(set(PFX_N.values())) == 1
_PFX_N = next(iter(PFX_N.values()))
PFX_DELTA_STAT = 0.01
m2 = len(PFX_BINS)
K2 = len(PFX_COUNTS)
PFX_ALPHA = PFX_DELTA_STAT / (m2 * K2)

_pfx_intervals = {k: [clopper_pearson_interval(PFX_COUNTS[k][i], _PFX_N, PFX_ALPHA) for i in range(m2)]
                  for k in PFX_COUNTS.keys()}
_pfx_rare_idx = [i for i in range(m2) if min(_pfx_intervals[k][i][0] for k in PFX_COUNTS.keys()) == 0.0]

def _pfx_eta_bits():
    eta = 0.0
    for k in PFX_COUNTS.keys():
        for kp in PFX_COUNTS.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m2):
                if i in _pfx_rare_idx:
                    continue
                lo = _pfx_intervals[kp][i][0]
                hi = _pfx_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)

def _pfx_delta_slack():
    return float(max(sum(_pfx_intervals[k][i][1] for i in _pfx_rare_idx) for k in PFX_COUNTS.keys()))

PFX_ETA_BITS = _pfx_eta_bits()
PFX_DELTA_SLACK = _pfx_delta_slack()

profiling_prefix_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": PREFIXFETCH_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "prefix_fetch_signature",
    "binning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "alphabet": "finite"},
    "classes": {k: {"n": _PFX_N} for k in PFX_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection",
        "delta_stat": PFX_DELTA_STAT,
        "alpha_per_bin": PFX_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(PFX_ETA_BITS, 6),
        "delta_slack": round(PFX_DELTA_SLACK, 6),
        "rare_bins": [PFX_BINS[i] for i in _pfx_rare_idx],
        "note": "Synthetic toy counts; the purpose is to exercise a second evidence_id wiring path (prefix-fetch) in the worked example, not to claim a real deployment bound."
    },
    "table": [
        {
            "bin": PFX_BINS[i],
            "count": {k: int(PFX_COUNTS[k][i]) for k in PFX_COUNTS.keys()},
            "p_hat": {k: round(PFX_COUNTS[k][i] / _PFX_N, 6) for k in PFX_COUNTS.keys()},
            "cp_interval": {k: [round(_pfx_intervals[k][i][0], 6), round(_pfx_intervals[k][i][1], 6)] for k in PFX_COUNTS.keys()},
        }
        for i in range(m2)
    ],
}
profiling_prefix_evidence_id = sha256_id(profiling_prefix_evidence_core)
profiling_prefix_evidence_obj = {"evidence_id": profiling_prefix_evidence_id, "evidence": profiling_prefix_evidence_core}
profiling_prefix_evidence_digest = write_json(ART / "example_profiling_evidence_prefixfetch.json", profiling_prefix_evidence_obj)



# Optional third profiling evidence object: prefix-fetch signature conditioned on a published state witness (second variant receipt).
PFXSC_WITNESS = ["fresh", "stale"]
PFXSC_BASE_BINS = ["pf:00", "pf:01", "pf:10", "pf:11", "other"]
PFXSC_BINS = [f"w:{w}/{b}" for w in PFXSC_WITNESS for b in PFXSC_BASE_BINS]

# Split the toy prefix-fetch counts into two witness classes.
PFXSC_COUNTS = {
    "k0": {"fresh": [500, 500, 500, 498, 2], "stale": [500, 500, 500, 497, 3]},
    "k1": {"fresh": [503, 497, 500, 500, 0], "stale": [502, 498, 500, 500, 0]},
    "k2": {"fresh": [495, 505, 500, 499, 1], "stale": [495, 505, 500, 499, 1]},
}

_pfxsc_flat = {k: [PFXSC_COUNTS[k][w][i] for w in PFXSC_WITNESS for i in range(len(PFXSC_BASE_BINS))] for k in PFXSC_COUNTS.keys()}
PFXSC_N = {k: sum(v) for k, v in _pfxsc_flat.items()}
assert len(set(PFXSC_N.values())) == 1
_PFXSC_N = next(iter(PFXSC_N.values()))

PFXSC_DELTA_STAT = 0.01
m3 = len(PFXSC_BINS)
K3 = len(_pfxsc_flat)
PFXSC_ALPHA = PFXSC_DELTA_STAT / (m3 * K3)

_pfxsc_intervals = {k: [clopper_pearson_interval(_pfxsc_flat[k][i], _PFXSC_N, PFXSC_ALPHA) for i in range(m3)]
                  for k in _pfxsc_flat.keys()}
_pfxsc_rare_idx = [i for i in range(m3) if min(_pfxsc_intervals[k][i][0] for k in _pfxsc_flat.keys()) == 0.0]


def _pfxsc_eta_bits():
    eta = 0.0
    for k in _pfxsc_flat.keys():
        for kp in _pfxsc_flat.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m3):
                if i in _pfxsc_rare_idx:
                    continue
                lo = _pfxsc_intervals[kp][i][0]
                hi = _pfxsc_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)


def _pfxsc_delta_slack():
    return float(max(sum(_pfxsc_intervals[k][i][1] for i in _pfxsc_rare_idx) for k in _pfxsc_flat.keys()))


PFXSC_ETA_BITS = _pfxsc_eta_bits()
PFXSC_DELTA_SLACK = _pfxsc_delta_slack()

profiling_statecond_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "prefix_fetch_signature",
    "binning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class", "witness_values": PFXSC_WITNESS, "alphabet": "finite"},
    "classes": {k: {"n": _PFXSC_N} for k in _pfxsc_flat.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection, conditioned on the published witness",
        "delta_stat": PFXSC_DELTA_STAT,
        "alpha_per_bin": PFXSC_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(PFXSC_ETA_BITS, 6),
        "delta_slack": round(PFXSC_DELTA_SLACK, 6),
        "rare_bins": [PFXSC_BINS[i] for i in _pfxsc_rare_idx],
        "note": "Synthetic toy counts split across a published witness; exercises conditional-witness plumbing (state-conditioned variant receipt) in the worked example."
    },
    "table": [
        {
            "bin": PFXSC_BINS[i],
            "count": {k: int(_pfxsc_flat[k][i]) for k in _pfxsc_flat.keys()},
            "p_hat": {k: round(_pfxsc_flat[k][i] / _PFXSC_N, 6) for k in _pfxsc_flat.keys()},
            "cp_interval": {k: [round(_pfxsc_intervals[k][i][0], 6), round(_pfxsc_intervals[k][i][1], 6)] for k in _pfxsc_flat.keys()},
        }
        for i in range(m3)
    ],
}
profiling_statecond_evidence_id = sha256_id(profiling_statecond_evidence_core)
profiling_statecond_evidence_obj = {"evidence_id": profiling_statecond_evidence_id, "evidence": profiling_statecond_evidence_core}
profiling_statecond_evidence_digest = write_json(ART / "example_profiling_evidence_prefixfetch_statecond.json", profiling_statecond_evidence_obj)


receipt = {
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "state_decl_id": state_decl_id,
    "line_items": [
        {
            "name": "primary_path_declaration",
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "witness_tier": "split_identity_destination_surface",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "assumption_qualified_MaxL_bits_per_lookup",
            "budget_value": PRIMARY_LINKABILITY_BOUND,
            "budget_value_qualifier": "valid only on the identity-to-destination linkability surface under separation class sep.nr1",
            "obs_model": {
                "separation_class": "sep.nr1",
                "relay_sees": ["client_identity", "timing", "sizes"],
                "router_sees": ["query_destination", "timing", "sizes"],
                "collusion_assumption": "no_declared_relay_router_collusion_within_TW",
                "rho_upper": RHO_UPPER,
                "rho_status": "policy_upper_bound",
                "status": "policy_declaration",
            },
            "knobs": {
                "relay_set_id": "relay-set-A",
                "relay_rotation": "24h",
                "router_key_id": "router-key-2026-02",
                "primary_surface_digest": primary_surface_digest,
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-primary-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-primary-v1"], "artifact_bundle": "bundle://worked-example/primary"},
        },
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "witness_tier": "Tier2_contact_failure_trace",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "MaxL_bits_per_lookup",
            "budget_value": fallback_cset_bits,
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "contact_surface": FALLBACK_CONTACT_SURFACE,
            "obs_model": {
                "p_obs_upper": P_OBS_UPPER,
                "status": {"p_obs_upper": "policy_upper_bound"},
            },
            "knobs": {
                "raw_b": RAW_TIERS[0]["raw_b"],
                "raw_b_status": "illustrative_input",
                "dummy_width_w": 4,
                "effective_bucket_K": 256,
                "retry_policy": "schedule_only",
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-fallback-cct-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-cct-v1"], "artifact_bundle": "bundle://worked-example/fallback-cct"},
        },
        {
            "name": "fallback_tiered_vector",
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "witness_tier": "tiered_vector",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "tiered_MaxL_summary",
            "budget_value": fallback_summary_bits,
            "obs_model": {"vector": vector},
            "knobs": {
                "mc_eq_session_T": 6,
                "per_step_epsilon_t": 0.02,
                "schedule_form": "deadline_normal_form",
                "conditional_independence_assumption": True,
                "state_decl_id": state_decl_id,
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-fallback-vector-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-vector-v1"], "artifact_bundle": "bundle://worked-example/fallback-vector"},
        },
        {
            "name": "path_selection_indicator",
            "exposure_nf_id": PATHSELECT_EXPOSURE,
            "witness_tier": "fallback_indicator",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "selection_tax_bits",
            "budget_value": selection_tax_bits,
            "obs_model": {
                "fallback_rate_hat": FALLBACK_RATE_HAT,
                "fallback_rate_status": "empirical_estimate",
                "R_pi_upper": R_PI_UPPER,
                "R_pi_status": "policy_upper_bound",
            },
            "knobs": {
                "trigger_class": ["availability", "public_bucket_staleness", "cid_independent_audit_sampling"],
                "state_decl_id": state_decl_id,
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-pathselect-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-pathselect-v1"], "artifact_bundle": "bundle://worked-example/pathselect"},
        },
        {
            "name": "profiling_equalization",
            "exposure_nf_id": PROFILING_EXPOSURE,
            "witness_tier": "Tier1_retry_bucket_trace",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "pairwise_equalization_eta_delta_bits",
            "budget_value": {"eta_bits": profiling_evidence_core["certificate_summary"]["eta_bits"], "delta": profiling_evidence_core["certificate_summary"]["delta_slack"]},
            "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; one-vs-mixture conversion is imported from Anonymity~B",
            "obs_model": {
                "audit_assumption": "i.i.d. samples within each class for the declared projection",
                "audit_delta_stat": profiling_evidence_core["audit_params"]["delta_stat"],
                "alpha_per_bin": profiling_evidence_core["audit_params"]["alpha_per_bin"],
                "rare_bins": profiling_evidence_core["certificate_summary"]["rare_bins"],
                "rare_bin_mass_upper": profiling_evidence_core["certificate_summary"]["delta_slack"],
            },
            "knobs": {
                "projection": "retry_bucket_trace",
                "bucket_width": "250ms",
            },
            "evidence_id": profiling_evidence_id,
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-profiling-eq-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-eq-v1"], "artifact_bundle": "bundle://worked-example/profiling-eq"},
        }
    ],
}
receipt_digest = write_json(ART / "example_receipt.json", receipt)

line_item_owner_map = {
    "owner_map_id": "worked-example-line-item-owner-map-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "note": "Digest-bound, non-schema adjunct naming which archive note owns each worked-example line item and which published wiki-note import point (if any) is the intended mathematical root.",
    "entries": [
        {
            "name": "primary_path_declaration",
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "replay_plan_id": "eval-primary-v1",
            "public_objects": [
                "example_primary_surface_manifest.json",
                "example_state_decl.json",
                "example_replay_plans.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~22", "path": "series/synthesis/paper22_primary_separation_manifests", "role": "guard object / separation-class declaration"},
                {"id": "Synthesis~23", "path": "series/synthesis/paper23_probabilistic_separation_budgets", "role": "guarded (0,rho) adjunct"},
                {"id": "Synthesis~30", "path": "series/synthesis/paper30_deployed_surfaces_control_plane", "role": "deployed control-plane surfaces that must be pinned"},
                {"id": "Anonymity~D", "path": "series/anonymity_series/paperD_spectral_delegation_certificates", "role": "receipt-grade delegation budget when the primary path is backed by a delegation witness"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:spectral", "link": "[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]", "role": "direct mathematical root when the primary path is delegation-certified"}
            ],
        },
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "replay_plan_id": "eval-fallback-cct-v1",
            "public_objects": [
                "example_state_decl.json",
                "example_effective_surface_resolution.json",
                "example_replay_plans.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~3", "path": "series/synthesis/paper3_trace_interfaces_dht", "role": "committee-contact ENF semantics"},
                {"id": "Synthesis~11", "path": "series/synthesis/paper11_observation_attenuation", "role": "attenuation by activation probability"},
                {"id": "Synthesis~14", "path": "series/synthesis/paper14_fallback_selection_tax", "role": "fallback activation and selection-tax semantics"},
                {"id": "Synthesis~30", "path": "series/synthesis/paper30_deployed_surfaces_control_plane", "role": "semantic contact-surface and request-shaping semantics"},
            ],
            "backbone_wikilinks": [],
        },
        {
            "name": "fallback_tiered_vector",
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "replay_plan_id": "eval-fallback-vector-v1",
            "public_objects": [
                "example_state_decl.json",
                "example_replay_plans.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~15", "path": "series/synthesis/paper15_tiered_observation_vectors", "role": "tier-vector packing and conservative composition surface"},
                {"id": "Synthesis~11", "path": "series/synthesis/paper11_observation_attenuation", "role": "attenuation of the raw tier budgets"},
                {"id": "Synthesis~5", "path": "series/synthesis/paper5_endpoint_metrics_bridge", "role": "bridge from per-lookup summary to endpoint-consumable units"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:scheduling", "link": "[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]", "role": "root import when the timing component is derived from schedule/termination-time hiding"},
                {"bibkey": "wiki:stopadd", "link": "[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]", "role": "normal-form import for deadline-shaped timing witnesses"}
            ],
        },
        {
            "name": "path_selection_indicator",
            "exposure_nf_id": PATHSELECT_EXPOSURE,
            "replay_plan_id": "eval-pathselect-v1",
            "public_objects": [
                "example_change_control.json",
                "example_compare_profile.json",
                "example_replay_plans.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~14", "path": "series/synthesis/paper14_fallback_selection_tax", "role": "fallback-indicator witness semantics and activation cap"},
                {"id": "Synthesis~19", "path": "series/synthesis/paper19_receipt_accounting_rulebook", "role": "how the selection term composes in release summaries"},
            ],
            "backbone_wikilinks": [],
        },
        {
            "name": "profiling_equalization",
            "exposure_nf_id": PROFILING_EXPOSURE,
            "evidence_id": profiling_evidence_id,
            "replay_plan_id": "eval-profiling-eq-v1",
            "public_objects": [
                "example_profiling_evidence.json",
                "example_replay_plans.json",
            ],
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract and one-vs-mixture interpretation"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "finite-sample menu-level audit certificate"},
                {"id": "Synthesis~26", "path": "series/synthesis/paper26_anytime_menu_spending", "role": "change-control-safe confidence spending"},
                {"id": "Synthesis~28", "path": "series/synthesis/paper28_coarsening_large_alphabet", "role": "coarsening rule when the projection alphabet is too large"},
                {"id": "Synthesis~29", "path": "series/synthesis/paper29_selection_discipline_datadependent", "role": "selection discipline for data-dependent bucket maps"},
            ],
            "backbone_wikilinks": [],
        },
    ],
    "variant_entries": [
        {
            "name": "profiling_equalization_prefixfetch",
            "exposure_nf_id": PREFIXFETCH_EXPOSURE,
            "replay_plan_id": "eval-profiling-prefixfetch-v1",
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract for a prefix-fetch projection"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "log-audit certificate shape"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:prefixcap", "link": "[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]", "role": "mathematical root when the prefix-fetch variant is justified by shared-kernel prefix/privacy arguments"}
            ],
        },
        {
            "name": "profiling_equalization_prefixfetch_statecond",
            "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
            "replay_plan_id": "eval-profiling-prefixfetch-statecond-v1",
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract"},
                {"id": "Synthesis~18", "path": "series/synthesis/paper18_plan_and_state_equivalence", "role": "state-conditioned witness discipline"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "log-audit certificate shape"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:prefixcap", "link": "[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]", "role": "shared-kernel prefix/privacy root for the state-conditioned prefix-fetch variant"}
            ],
        },
        {
            "name": "profiling_equalization_contact_coarsened",
            "exposure_nf_id": PROFILING_CONTACT_COARSENED_EXPOSURE,
            "replay_plan_id": "eval-profiling-contact-coarsened-v1",
            "owner_notes": [
                {"id": "Synthesis~28", "path": "series/synthesis/paper28_coarsening_large_alphabet", "role": "coarsening map and data-processing-safe audit surface"},
                {"id": "Synthesis~29", "path": "series/synthesis/paper29_selection_discipline_datadependent", "role": "selection discipline if the map family is data-tuned"},
            ],
            "backbone_wikilinks": [],
        },
    ],
}
line_item_owner_map_digest = write_json(ART / "example_line_item_owner_map.json", line_item_owner_map)

# Variant receipt that appends a second profiling line item for prefix-fetch signatures.
variant_receipt = copy.deepcopy(receipt)
variant_receipt["variant_of"] = "example_receipt.json"
variant_receipt["variant_note"] = "Optional extension exercising prefix-fetch profiling equalization plumbing; does not alter any schemas."
variant_receipt["line_items"] = list(variant_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_prefixfetch",
        "exposure_nf_id": PREFIXFETCH_EXPOSURE,
        "witness_tier": "Tier1_prefix_fetch_signature",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(PFX_ETA_BITS, 6), "delta": round(PFX_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; one-vs-mixture conversion is imported from Anonymity~B",
        "evidence_id": profiling_prefix_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared projection",
            "audit_delta_stat": PFX_DELTA_STAT,
            "alpha_per_bin": PFX_ALPHA,
            "rare_bin_mass_upper": round(PFX_DELTA_SLACK, 6),
            "rare_bins": [PFX_BINS[i] for i in _pfx_rare_idx],
        },
        "knobs": {"projection": "prefix_fetch_signature", "prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix"},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-prefixfetch-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-prefixfetch-v1"], "artifact_bundle": "bundle://worked-example/profiling-prefixfetch"},
    }
]
variant_receipt_digest = write_json(ART / "example_receipt_prefixfetch_variant.json", variant_receipt)


# Second variant receipt that appends a state-conditioned prefix-fetch profiling line item (conditional witness).
statecond_receipt = copy.deepcopy(receipt)
statecond_receipt["variant_of"] = "example_receipt.json"
statecond_receipt["variant_note"] = "Optional extension exercising prefix-fetch equalization conditioned on a published state witness; does not alter any schemas."
statecond_receipt["line_items"] = list(statecond_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_prefixfetch_statecond",
        "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
        "witness_tier": "Tier1_prefix_fetch_signature_conditional",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(PFXSC_ETA_BITS, 6), "delta": round(PFXSC_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; conditional-witness lifting is imported from Synthesis~18 and Anonymity~B",
        "evidence_id": profiling_statecond_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared projection, conditioned on the published witness",
            "audit_delta_stat": PFXSC_DELTA_STAT,
            "alpha_per_bin": PFXSC_ALPHA,
            "rare_bin_mass_upper": round(PFXSC_DELTA_SLACK, 6),
            "rare_bins": [PFXSC_BINS[i] for i in _pfxsc_rare_idx],
            "state_witness": {"name": "bucket_staleness_class", "values": PFXSC_WITNESS, "declared_public": True},
        },
        "knobs": {"projection": "prefix_fetch_signature", "prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class"},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-prefixfetch-statecond-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-prefixfetch-statecond-v1"], "artifact_bundle": "bundle://worked-example/profiling-prefixfetch-statecond"},
    }
]


# Third variant receipt: coarsening a large-alphabet contact-set hash to a sample-feasible signature (Synthesis~28).
COARSENING_MAP_CORE = {
    "coarsening_schema": "coarsening_map.v1",
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "source_projection": "contact_set_hash",
    "target_projection": "contact_hash_sig2",
    "rule": "sig2 = first2bits(sha256(serialized_contact_set))",
    "alphabet": ["00", "01", "10", "11"],
    "note": "Toy coarsening used only for the worked example: a huge contact-set hash alphabet is made audit-feasible by declaring a deterministic 2-bit signature partition (Synthesis~28).",
}
COARSENING_MAP_ID = sha256_id(COARSENING_MAP_CORE)
coarsening_map_obj = {"coarsening_map_id": COARSENING_MAP_ID, "coarsening_map": COARSENING_MAP_CORE}
coarsening_map_digest = write_json(ART / "example_coarsening_map_contact.json", coarsening_map_obj)

CONTACT_COARSENED_EXPOSURE = ENF_IDS[PROFILING_CONTACT_COARSENED_LABEL]

CC_BINS = ["00", "01", "10", "11"]
CC_COUNTS = {
    "k0": [630, 590, 600, 580],
    "k1": [610, 610, 590, 590],
    "k2": [620, 600, 600, 580],
}
CC_N = {k: sum(v) for k, v in CC_COUNTS.items()}
assert len(set(CC_N.values())) == 1
_CC_N = next(iter(CC_N.values()))
CC_DELTA_STAT = 0.01
m3 = len(CC_BINS)
K3 = len(CC_COUNTS)
CC_ALPHA = CC_DELTA_STAT / (m3 * K3)

_cc_intervals = {k: [clopper_pearson_interval(CC_COUNTS[k][i], _CC_N, CC_ALPHA) for i in range(m3)]
                 for k in CC_COUNTS.keys()}
_cc_rare_idx = [i for i in range(m3) if min(_cc_intervals[k][i][0] for k in CC_COUNTS.keys()) == 0.0]

def _cc_eta_bits():
    eta = 0.0
    for k in CC_COUNTS.keys():
        for kp in CC_COUNTS.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m3):
                if i in _cc_rare_idx:
                    continue
                lo = _cc_intervals[kp][i][0]
                hi = _cc_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)

def _cc_delta_slack():
    return float(max(sum(_cc_intervals[k][i][1] for i in _cc_rare_idx) for k in CC_COUNTS.keys()))

CC_ETA_BITS = _cc_eta_bits()
CC_DELTA_SLACK = _cc_delta_slack()

contact_coarsened_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": CONTACT_COARSENED_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "contact_hash_sig2 (coarsening of contact_set_hash)",
    "coarsening_map_id": COARSENING_MAP_ID,
    "classes": {k: {"n": _CC_N} for k in CC_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared coarsened projection",
        "delta_stat": CC_DELTA_STAT,
        "alpha_per_bin": CC_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(CC_ETA_BITS, 6),
        "delta_slack": round(CC_DELTA_SLACK, 6),
        "rare_bins": [CC_BINS[i] for i in _cc_rare_idx],
        "note": "Synthetic toy counts; demonstrates a digest-bound coarsening map + audit-feasible alphabet, not a real deployment bound.",
    },
    "table": [
        {
            "bin": CC_BINS[i],
            "count": {k: int(CC_COUNTS[k][i]) for k in CC_COUNTS.keys()},
            "p_hat": {k: round(CC_COUNTS[k][i] / _CC_N, 6) for k in CC_COUNTS.keys()},
            "cp_interval": {k: [round(_cc_intervals[k][i][0], 6), round(_cc_intervals[k][i][1], 6)] for k in CC_COUNTS.keys()},
        }
        for i in range(m3)
    ],
}
contact_coarsened_evidence_id = sha256_id(contact_coarsened_evidence_core)
contact_coarsened_evidence_obj = {"evidence_id": contact_coarsened_evidence_id, "evidence": contact_coarsened_evidence_core}
contact_coarsened_evidence_digest = write_json(ART / "example_profiling_evidence_contact_coarsened.json", contact_coarsened_evidence_obj)

contact_coarsened_receipt = copy.deepcopy(receipt)
contact_coarsened_receipt["variant_of"] = "example_receipt.json"
contact_coarsened_receipt["variant_note"] = "Optional extension exercising Synthesis~28: a large-alphabet contact-set hash is made audit-feasible by declaring a digest-bound coarsening map (2-bit signature) and auditing only the coarsened projection."
contact_coarsened_receipt["line_items"] = list(contact_coarsened_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_contact_coarsened",
        "exposure_nf_id": CONTACT_COARSENED_EXPOSURE,
        "witness_tier": "Tier1_contact_hash_sig2",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(CC_ETA_BITS, 6), "delta": round(CC_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; coarsening is declared via coarsening_map_id (Synthesis~28)",
        "evidence_id": contact_coarsened_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared coarsened projection",
            "audit_delta_stat": CC_DELTA_STAT,
            "alpha_per_bin": CC_ALPHA,
            "rare_bin_mass_upper": round(CC_DELTA_SLACK, 6),
            "rare_bins": [CC_BINS[i] for i in _cc_rare_idx],
            "coarsening_map_id": COARSENING_MAP_ID,
        },
        "knobs": {"source_projection": "contact_set_hash", "coarsened_projection": "contact_hash_sig2", "coarsening_map_id": COARSENING_MAP_ID},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-contact-coarsened-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-contact-coarsened-v1"], "artifact_bundle": "bundle://worked-example/profiling-contact-coarsened"},
    }
]
contact_coarsened_receipt_digest = write_json(ART / "example_receipt_contact_coarsened_variant.json", contact_coarsened_receipt)

statecond_receipt_digest = write_json(ART / "example_receipt_prefixfetch_statecond_variant.json", statecond_receipt)



plan_catalog = {
    "catalog_id": PLAN_CATALOG_VERSION,
    "claim_id": CLAIM_ID,
    "canonicalization": "plan_spec_id = sha256(canon(plan_spec)) where canon uses sorted keys and no whitespace.",
    "plans": PLAN_SPECS,
}
plan_catalog_digest = write_json(ART / "example_replay_plans.json", plan_catalog)

support_bundle_map = {
    "bundle_map_id": "worked-example-support-bundles-v1",
    "claim_id": CLAIM_ID,
    "bundles": [
        {
            "bundle_id": "bundle://worked-example/primary",
            "consumed_by": ["eval-primary-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_release_receipt.json",
                "example_primary_surface_manifest.json",
            ],
            "support_pointers": [
                "support://primary/operators.example",
                "support://primary/config.example",
                "support://primary/telemetry.example",
            ],
            "failure_if_missing": "cannot validate sep.nr1 identity-to-destination separation declaration",
        },
        {
            "bundle_id": "bundle://worked-example/fallback-cct",
            "consumed_by": ["eval-fallback-cct-v1"],
            "required_artifacts": ["example_receipt.json", "example_state_decl.json"],
            "support_pointers": ["support://fallback/notarized-attempt-log.example"],
            "failure_if_missing": "cannot replay fallback contact-surface bound against notarized evidence",
        },
        {
            "bundle_id": "bundle://worked-example/fallback-vector",
            "consumed_by": ["eval-fallback-vector-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_support_bundle_map.json",
            ],
            "support_pointers": [
                "support://fallback/timing-certificates.example",
                "support://fallback/equalization-slice.example",
            ],
            "failure_if_missing": "cannot replay tiered summary or verify supporting schedule/equalization references",
        },
        {
            "bundle_id": "bundle://worked-example/pathselect",
            "consumed_by": ["eval-pathselect-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_change_control.json",
            ],
            "support_pointers": ["support://pathselect/audit-live-fallback-indicators.example"],
            "failure_if_missing": "cannot compare audit/live fallback-indicator behavior under the declared trigger class",
        },
        {
            "bundle_id": "bundle://worked-example/profiling-eq",
            "consumed_by": ["eval-profiling-eq-v1"],
            "required_artifacts": ["example_receipt.json", "example_profiling_evidence.json"],
            "support_pointers": ["support://profiling/log-slice.example"],
            "failure_if_missing": "cannot validate profiling/equalization evidence_id against the published receipt"
        },
        {
            "bundle_id": "bundle://worked-example/profiling-prefixfetch",
            "consumed_by": ["eval-profiling-prefixfetch-v1"],
            "required_artifacts": [
                "example_receipt_prefixfetch_variant.json",
                "example_profiling_evidence_prefixfetch.json",
            ],
            "support_pointers": ["support://profiling/prefixfetch-log-slice.example"],
            "failure_if_missing": "cannot validate prefix-fetch profiling evidence_id against the variant receipt",
        },

        {
            "bundle_id": "bundle://worked-example/profiling-prefixfetch-statecond",
            "consumed_by": ["eval-profiling-prefixfetch-statecond-v1"],
            "required_artifacts": [
                "example_receipt_prefixfetch_statecond_variant.json",
                "example_profiling_evidence_prefixfetch_statecond.json"
            ],
            "support_pointers": ["support://profiling/prefixfetch-statecond-log-slice.example"],
            "failure_if_missing": "cannot validate state-conditioned prefix-fetch evidence_id against the variant receipt",
        },

{
    "bundle_id": "bundle://worked-example/profiling-contact-coarsened",
    "consumed_by": ["eval-profiling-contact-coarsened-v1"],
    "required_artifacts": [
        "example_receipt_contact_coarsened_variant.json",
        "example_profiling_evidence_contact_coarsened.json",
        "example_coarsening_map_contact.json"
    ],
    "support_pointers": ["support://profiling/contactset-hash.example"],
    "failure_if_missing": "cannot validate coarsening_map_id or recompute (eta,delta) for coarsened contact-set equalization claim",
},


    ],
    "note": "Operational map from artifact_bundle ids to concrete archive artifacts and off-bundle support pointers; not a new receipt primitive.",
}
support_bundle_map_digest = write_json(ART / "example_support_bundle_map.json", support_bundle_map)

compare_profile = {
    "compare_profile_id": COMPARE_PROFILE_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "primary_compare_surface": {
        "exposure_nf_id": PRIMARY_EXPOSURE,
        "budget_type": "assumption_qualified_MaxL_bits_per_lookup",
        "budget_value": PRIMARY_LINKABILITY_BOUND,
        "qualifier": "under separation class sep.nr1",
        "manifest_digest": primary_surface_digest,
        "rho_upper": RHO_UPPER,
    },
    "user_compare_surface": {
        "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
        "budget_type": "tiered_MaxL_summary",
        "budget_value": fallback_summary_bits,
        "selection_tax_bits": selection_tax_bits,
        "total_summary_bits_per_lookup": total_summary_bits,
        "tw_id": TW_ID,
        "state_contract_id": state_decl["state_contract_id"],
        "state_decl_id": state_decl["state_decl_id"],
        "receipt_digest": receipt_digest,
    },
    "diff_views": {
        "user_fast_diff": [
            "claim_id",
            "user_compare_surface.exposure_nf_id",
            "user_compare_surface.budget_value",
            "user_compare_surface.selection_tax_bits",
            "user_compare_surface.total_summary_bits_per_lookup",
            "user_compare_surface.receipt_digest",
        ],
        "auditor_fast_diff": [
            "claim_id",
            "tw_id",
            "covered_exposures",
            "primary_compare_surface.manifest_digest",
            "primary_compare_surface.rho_upper",
            "user_compare_surface.state_decl_id",
            "receipt_digest",
            "plan_catalog_digest",
            "change_control_id",
        ],
        "release_guard_fields": [
            "tw_id",
            "covered_exposures",
            "primary_separation_class",
            "state_decl_id",
            "max_total_budget_bits_per_lookup",
        ],
    },
    "source_fields": {
        "abom": [
            "covered_exposures",
            "budget_summary.primary_surface",
            "budget_summary.fallback_summary",
            "budget_summary.selection_tax",
            "budget_summary.total_summary",
        ],
        "receipt": [
            "tw_id",
            "line_items[*].exposure_nf_id",
            "line_items[*].budget_value",
            "line_items[*].lineage.relation",
        ],
        "release_receipt": [
            "policy_gate.change_control_id",
            "policy_gate.max_total_budget_bits_per_lookup",
            "policy_gate.required_exposures",
            "adjunct_digests.state_decl",
            "adjunct_digests.primary_surface_manifest",
        ],
        "uvi": [
            "claim_pointer",
            "exposure_nf_id",
            "receipt_digest",
            "log_anchor.log_id",
            "consistency_context.checkpoint",
        ],
    },
    "note": "Operational diff profile for OINL-style release comparison; not a new receipt or UVI primitive.",
}
compare_profile_digest = write_json(ART / "example_compare_profile.json", compare_profile)

successor_p = 0.015
successor_vector = []
for item in RAW_TIERS:
    eff = attenuated_bits(item["raw_b"], successor_p)
    successor_vector.append({
        "tier": item["tier"],
        "p": successor_p,
        "raw_b": item["raw_b"],
        "effective_b": eff,
        "status": {"p": "policy_upper_bound", "raw_b": "illustrative_input"},
    })
successor_cset_bits = successor_vector[0]["effective_b"]
successor_fallback_summary_bits = sum(v["effective_b"] for v in successor_vector)
successor_total_summary_bits = math.log2(
    FALLBACK_RATE_HAT * (2.0 ** successor_fallback_summary_bits)
    + (1.0 - FALLBACK_RATE_HAT) * (2.0 ** PRIMARY_LINKABILITY_BOUND)
) + selection_tax_bits
successor_receipt = copy.deepcopy(receipt)
for item in successor_receipt["line_items"]:
    if item["exposure_nf_id"] == FALLBACK_CCT_EXPOSURE:
        item["budget_value"] = successor_cset_bits
        item["obs_model"]["p_obs_upper"] = successor_p
    elif item["exposure_nf_id"] == FALLBACK_VECTOR_EXPOSURE:
        item["budget_value"] = successor_fallback_summary_bits
        item["obs_model"]["vector"] = successor_vector
successor_receipt_digest = sha256_bytes(json.dumps(successor_receipt, indent=2, sort_keys=True).encode() + b"\n")

compare_walkthrough = {
    "walkthrough_id": "worked-example-compare-walkthrough-v1",
    "claim_id": CLAIM_ID,
    "base_release_id": RELEASE_ID,
    "focus_case": "replay-required-B",
    "compare_profile_id": COMPARE_PROFILE_ID,
    "release_action_matrix_id": release_action_matrix["action_matrix_id"],
    "release_obligation_profile_id": release_obligation_profile["obligation_profile_id"],
    "successor_receipt_digest_basis": "synthetic_case_B_successor_receipt",
    "changed_line_items": ["fallback_contact_surface", "fallback_tiered_vector"],
    "replay_plan_ids": ["eval-fallback-cct-v1", "eval-fallback-vector-v1"],
    "continuity_decision": "same_certified_interface_replayed_surfaces",
    "continuity_basis": [
        "tw_id is unchanged",
        "state_decl_id is unchanged",
        "required exposures remain unchanged",
        "primary separation class remains sep.nr1",
        "only the fallback contact/budget surface was replayed"
    ],
    "base_fields": {
        "user_fast_diff": {
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "budget_value": fallback_summary_bits,
            "selection_tax_bits": selection_tax_bits,
            "total_summary_bits_per_lookup": total_summary_bits,
            "receipt_digest": receipt_digest,
        },
        "auditor_fast_diff": {
            "tw_id": TW_ID,
            "covered_exposures": [
                PRIMARY_EXPOSURE,
                FALLBACK_CCT_EXPOSURE,
                FALLBACK_VECTOR_EXPOSURE,
                PATHSELECT_EXPOSURE,
            ],
            "primary_surface_manifest_digest": primary_surface_digest,
            "primary_rho_upper": RHO_UPPER,
            "state_contract_id": state_decl["state_contract_id"],
            "state_decl_id": state_decl["state_decl_id"],
            "plan_catalog_digest": plan_catalog_digest,
            "change_control_id": change_control["change_control_id"],
        },
    },
    "successor_fields": {
        "release_id": RELEASE_ID + "b",
        "user_fast_diff": {
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "budget_value": successor_fallback_summary_bits,
            "selection_tax_bits": selection_tax_bits,
            "total_summary_bits_per_lookup": successor_total_summary_bits,
            "receipt_digest": successor_receipt_digest,
        },
        "auditor_fast_diff": {
            "tw_id": TW_ID,
            "covered_exposures": [
                PRIMARY_EXPOSURE,
                FALLBACK_CCT_EXPOSURE,
                FALLBACK_VECTOR_EXPOSURE,
                PATHSELECT_EXPOSURE,
            ],
            "primary_surface_manifest_digest": primary_surface_digest,
            "primary_rho_upper": RHO_UPPER,
            "state_contract_id": state_decl["state_contract_id"],
            "state_decl_id": state_decl["state_decl_id"],
            "plan_catalog_digest": plan_catalog_digest,
            "change_control_id": change_control["change_control_id"],
        },
    },
    "observed_diffs": [
        "fallback obs_model.p_obs_upper decreases from 0.02 to 0.015",
        "fallback-vector budget_value decreases accordingly",
        "total-summary field decreases accordingly",
        "receipt digest changes",
        "guard fields tw_id, covered exposures, separation class, and state_decl_id remain stable",
    ],
    "user_first_alarm": "receipt digest changed; compare-profile then shows the fallback summary improved while exposure_nf_id and log family are stable",
    "auditor_first_alarm": "receipt digest changed with stable guard fields; change-control classifies this as replay_changed_surfaces, so rerun eval-fallback-cct-v1 and eval-fallback-vector-v1",
    "classification_result": "replay_changed_surfaces",
    "matched_rule_ids": ["contact-or-budget-replay"],
    "required_action": "publish fresh notarized comparison for the changed fallback surfaces and update release lineage without full recertification",
    "required_publication_roles": [
        "fresh_release_binding",
        "fresh_compare_report",
        "fresh_replay_verdict",
        "fresh_successor_continuity_verdict",
        "fresh_successor_lineage_notice",
    ],
    "note": "Concrete compare walk-through for the compare profile; explanatory adjunct rather than a new receipt primitive.",
}
compare_walkthrough_digest = write_json(ART / "example_compare_walkthrough.json", compare_walkthrough)

abom = {
    "abom_version": "0.3-worked-example",
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "release_label": RELEASE_ID,
    "covered_exposures": [
        PRIMARY_EXPOSURE,
        FALLBACK_CCT_EXPOSURE,
        FALLBACK_VECTOR_EXPOSURE,
        PATHSELECT_EXPOSURE,
        PROFILING_EXPOSURE,
    ],
    "budget_summary": {
        "type": "MaxL_bits_per_lookup",
        "primary_surface": {
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "value": PRIMARY_LINKABILITY_BOUND,
            "qualifier": "under separation class sep.nr1",
        },
        "fallback_summary": fallback_summary_bits,
        "selection_tax": selection_tax_bits,
        "total_summary": total_summary_bits,
        "window": "24h",
        "usage": f"Q<={Q}",
    },
    "artifacts": [
        {"name": "example_exposure_nf_registry.json", "sha256": exposure_registry_digest, "availability": "in_archive"},
        {"name": "example_tw_decl.json", "sha256": tw_decl_digest, "availability": "in_archive"},
        {"name": "example_receipt.json", "sha256": receipt_digest, "availability": "in_archive"},
        {"name": "example_state_decl.json", "sha256": state_decl_digest, "availability": "in_archive"},
        {"name": "example_state_decl_registry.json", "sha256": state_decl_registry_digest, "availability": "in_archive"},
        {"name": "example_effective_surface_resolution.json", "sha256": effective_surface_resolution_digest, "availability": "in_archive"},
        {"name": "example_primary_surface_manifest.json", "sha256": primary_surface_digest, "availability": "in_archive"},
        {"name": "example_user_watch_policy.json", "sha256": user_watch_digest, "availability": "in_archive"},
        {"name": "example_change_control.json", "sha256": change_control_digest, "availability": "in_archive"},
        {"name": "example_release_action_matrix.json", "sha256": release_action_matrix_digest, "availability": "in_archive"},
        {"name": "example_release_obligation_profile.json", "sha256": release_obligation_profile_digest, "availability": "in_archive"},
        {"name": "example_replay_plans.json", "sha256": plan_catalog_digest, "availability": "in_archive"},
        {"name": "example_support_bundle_map.json", "sha256": support_bundle_map_digest, "availability": "in_archive"},
        {"name": "example_profiling_evidence.json", "sha256": profiling_evidence_digest, "availability": "in_archive"},
        {"name": "example_compare_profile.json", "sha256": compare_profile_digest, "availability": "in_archive"},
        {"name": "example_drift_cases.json", "sha256": drift_cases_digest, "availability": "in_archive"},
        {"name": "example_compare_walkthrough.json", "sha256": compare_walkthrough_digest, "availability": "in_archive"},
        {"name": "example_line_item_owner_map.json", "sha256": line_item_owner_map_digest, "availability": "in_archive"},
    ],
    "signing": {"scheme": "ed25519", "key_id": "worked-example-key", "signature": "EXAMPLE_ONLY"},
}
abom_digest = write_json(ART / "example_abom.json", abom)

release_receipt = {
    "release_id": RELEASE_ID,
    "claim_id": CLAIM_ID,
    "abom_digest": abom_digest,
    "receipt_digest": receipt_digest,
    "plan_catalog_digest": plan_catalog_digest,
    "adjunct_digests": {
        "primary_surface_manifest": primary_surface_digest,
        "state_decl": state_decl_digest,
        "effective_surface_resolution": effective_surface_resolution_digest,
        "user_watch_policy": user_watch_digest,
        "change_control": change_control_digest,
        "release_action_matrix": release_action_matrix_digest,
        "release_obligation_profile": release_obligation_profile_digest,
        "support_bundle_map": support_bundle_map_digest,
        "compare_profile": compare_profile_digest,
        "compare_walkthrough": compare_walkthrough_digest,
        "line_item_owner_map": line_item_owner_map_digest,
    },
    "policy_gate": {
        "change_control_id": change_control["change_control_id"],
        "max_total_budget_bits_per_lookup": 0.30,
        "required_exposures": [FALLBACK_VECTOR_EXPOSURE, PATHSELECT_EXPOSURE],
        "require_uvi": True,
        "require_state_decl": True,
    },
    "pvsa": {
        "summary": "worked-example release binding",
        "digest": "EXAMPLE_ONLY",
    },
}
release_digest = write_json(ART / "example_release_receipt.json", release_receipt)

uvi = {
    "claim_pointer": CLAIM_ID,
    "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
    "receipt_digest": receipt_digest,
    "log_anchor": {
        "log_id": "example-transparency-log",
        "checkpoint": "tree_size=42 root=EXAMPLE_ONLY",
        "inclusion_proof": ["EXAMPLE_ONLY"],
    },
    "consistency_context": {
        "checkpoint": "tree_size=42 root=EXAMPLE_ONLY",
        "proof_pointer": "consistency://example-transparency-log/41-42",
    },
}
uvi_digest = write_json(ART / "example_uvi.json", uvi)

verifier_report = {
    "claim_id": CLAIM_ID,
    "plans_checked": [
        {"plan_id": "eval-primary-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-primary-v1"]},
        {"plan_id": "eval-fallback-cct-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-cct-v1"]},
        {"plan_id": "eval-fallback-vector-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-vector-v1"]},
        {"plan_id": "eval-pathselect-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-pathselect-v1"]},
    ],
    "recomputed": {
        "fallback_contact_bits_per_lookup": fallback_cset_bits,
        "fallback_summary_bits_per_lookup": fallback_summary_bits,
        "selection_tax_bits": selection_tax_bits,
        "total_summary_bits_per_lookup": total_summary_bits,
    },
    "support_artifacts": {
        "state_decl_id": state_decl_id,
        "state_decl_digest": state_decl_digest,
        "state_decl_registry_digest": state_decl_registry_digest,
        "plan_catalog_digest": plan_catalog_digest,
        "primary_surface_digest": primary_surface_digest,
        "change_control_digest": change_control_digest,
        "support_bundle_map_digest": support_bundle_map_digest,
        "compare_profile_digest": compare_profile_digest,
        "compare_walkthrough_digest": compare_walkthrough_digest,
        "effective_surface_resolution_digest": effective_surface_resolution_digest,
        "line_item_owner_map_digest": line_item_owner_map_digest,
        "release_receipt_digest": release_digest,
        "user_watch_policy_digest": user_watch_digest,
        "uvi_digest": uvi_digest,
        "drift_cases_digest": drift_cases_digest,
    },
    "notes": [
        "Worked example only; no live deployment evidence implied.",
        "Primary-path contribution is assumption-qualified and valid only on the identity-to-destination linkability surface under sep.nr1.",
        "Primary-path line item also publishes rho_upper as a policy upper bound on separation failure (interpreted as a guarded (0,rho) adjunct).",
        "Path-selection term uses log2(R_pi) with R_pi<=1.2.",
        "Fallback-rate hat value is treated as an empirical estimate; p_obs and R_pi are policy upper bounds.",
        "User-facing drift checks are externalized to example_user_watch_policy.json rather than the minimal UVI tuple.",
        "Release-side drift handling is externalized to example_change_control.json so refresh-only updates can be distinguished from replay-required or full-recertification updates.",
        "example_drift_cases.json gives one tiny refresh-only case, one replay-required case, and one full-recertification case so the change-control categories are visible on concrete field diffs.",
        "example_support_bundle_map.json resolves artifact_bundle ids to the concrete in-archive artifacts and off-bundle support pointers each replay plan expects.",
        "example_compare_profile.json names the fastest cross-release diff surfaces for users and auditors without changing the core receipt tuple.",
        "example_compare_walkthrough.json shows one concrete prior-vs-current comparison using those diff fields so the compare profile is not just a list of names.",
    ],
}
verifier_digest = write_json(ART / "example_verifier_report.json", verifier_report)

artifact_inventory = {
    "inventory_id": INVENTORY_ID,
    "support_manifest_id": MANIFEST_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "groups": [
        {
            "group": "claim_objects",
            "visibility": "published",
            "entries": [
                {"path": "example_receipt.json", "role": "receipt tuple", "consumed_by": ["abom", "release_receipt", "uvi", "auditor"]},
                {"path": "example_receipt_prefixfetch_variant.json", "role": "optional variant receipt (prefix-fetch profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_receipt_prefixfetch_statecond_variant.json", "role": "optional variant receipt (state-conditioned prefix-fetch profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_receipt_contact_coarsened_variant.json", "role": "optional variant receipt (coarsened contact-set profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_abom.json", "role": "claim manifest", "consumed_by": ["release_receipt", "user", "auditor"]},
                {"path": "example_exposure_nf_registry.json", "role": "label-to-ENF-ID binding registry", "consumed_by": ["user", "auditor"]},
                {"path": "example_tw_decl.json", "role": "threat/window declaration (label-to-TW-ID binding)", "consumed_by": ["user", "auditor"]},
                {"path": "example_state_decl_registry.json", "role": "label-to-state-decl-id binding registry", "consumed_by": ["user", "auditor"]},
                {"path": "example_release_receipt.json", "role": "release binding", "consumed_by": ["auditor", "user"]},
                {"path": "example_uvi.json", "role": "minimal user discovery object", "consumed_by": ["user"]},
            ],
        },
        {
            "group": "guard_and_compare_adjuncts",
            "visibility": "published_adjunct",
            "entries": [
                {"path": "example_primary_surface_manifest.json", "role": "primary declaration guard surface", "consumed_by": ["auditor", "release_receipt"]},
                {"path": "example_state_decl.json", "role": "scoped state declaration", "consumed_by": ["auditor", "replay_plans"]},
                {"path": "example_effective_surface_resolution.json", "role": "effective replay-surface assembly adjunct", "consumed_by": ["auditor", "validator", "maintainer"]},
                {"path": "example_change_control.json", "role": "release drift policy", "consumed_by": ["release_receipt", "auditor"]},
                {"path": "example_release_action_matrix.json", "role": "field-family diff-to-action matrix", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_release_obligation_profile.json", "role": "action-class to publication-duty profile", "consumed_by": ["maintainer", "auditor", "user"]},
                {"path": "example_compare_profile.json", "role": "cross-release diff profile", "consumed_by": ["user", "auditor"]},
                {"path": "example_compare_walkthrough.json", "role": "illustrative prior-vs-current diff", "consumed_by": ["user", "auditor"]},
                {"path": "example_successor_continuity_verdict.json", "role": "base-to-successor continuity verdict adjunct", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_publication_closure_verdict.json", "role": "successor publication-package closure verdict adjunct", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_successor_status_envelope.json", "role": "narrow summary-stage status envelope for one successor comparison", "consumed_by": ["user", "referee", "release_note"]},
                {"path": "example_successor_lineage_notice.json", "role": "outward-facing successor lineage notice adjunct", "consumed_by": ["user", "maintainer", "release_note"]},
                {"path": "example_successor_derivation_graph.json", "role": "maintenance DAG for one successor comparison", "consumed_by": ["maintainer", "referee", "auditor"]},
                {"path": "example_release_spine.json", "role": "stable stage map for successor maintenance", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_release_stage_walkthrough.json", "role": "stage-by-stage worked release walk for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_claim_support_map.json", "role": "statement-to-evidence support map for one successor comparison", "consumed_by": ["user", "referee", "maintainer"]},
                {"path": "example_successor_citation_map.json", "role": "minimal-citation map for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_challenge_routes.json", "role": "audience-keyed challenge routes for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note", "auditor"]},
                {"path": "example_successor_challenge_branches.json", "role": "piece-keyed challenge branches for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note", "auditor"]},
                {"path": "example_successor_quote_map.json", "role": "exact-field quote map for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_clause_pack.json", "role": "canonical clause pack for one successor comparison", "consumed_by": ["maintainer", "release_note", "referee"]},
                {"path": "example_successor_sentence_locks.json", "role": "pair-anchored sentence-lock ledger for one successor comparison", "consumed_by": ["maintainer", "release_note", "referee"]},
                {"path": "example_line_item_owner_map.json", "role": "line-item owner/import crosswalk", "consumed_by": ["referee", "auditor", "maintainer"]},
                {"path": "example_drift_cases.json", "role": "tiny successor-release catalog", "consumed_by": ["auditor", "maintainer"]},
                {"path": "example_user_watch_policy.json", "role": "client drift alarms", "consumed_by": ["user"]},
            ],
        },
        {
            "group": "replay_and_evidence_adjuncts",
            "visibility": "published_adjunct",
            "entries": [
                {"path": "example_replay_plans.json", "role": "plan-id catalog", "consumed_by": ["auditor", "validator"]},
                {"path": "example_support_bundle_map.json", "role": "artifact-bundle resolver", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence.json", "role": "profiling/equalization audit evidence table", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_prefixfetch.json", "role": "prefix-fetch profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_prefixfetch_statecond.json", "role": "state-conditioned prefix-fetch profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_contact_coarsened.json", "role": "coarsened-contact profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_coarsening_map_contact.json", "role": "declared coarsening/partition map for contact-set hash", "consumed_by": ["auditor", "validator"]},
                {"path": "example_verifier_report.json", "role": "worked replay summary", "consumed_by": ["maintainer", "auditor"]},
            ],
        },
        {
            "group": "maintenance_outputs",
            "visibility": "maintenance_only",
            "entries": [
                {"path": "example_artifact_inventory.json", "role": "machine-readable artifact inventory", "consumed_by": ["maintainer", "validator"]},
                {"path": "example_compare_report.json", "role": "machine-readable cross-release diff report", "consumed_by": ["maintainer", "validator"]},
                {"path": "support_manifest.json", "role": "digest manifest for support artifacts", "consumed_by": ["maintainer", "validator"]},
                {"path": "example_validation_report.json", "role": "validator output", "consumed_by": ["maintainer"]},
            ],
        },
        {
            "group": "maintenance_helpers",
            "visibility": "maintenance_only",
            "entries": [
                {"path": "README.md", "role": "human maintenance guide", "consumed_by": ["maintainer"]},
                {"path": "paper.tex", "role": "worked-note source", "consumed_by": ["maintainer"]},
                {"path": "tools/materialize_example.py", "role": "deterministic artifact generator", "consumed_by": ["maintainer"]},
                {"path": "tools/emit_compare_report.py", "role": "compare-report emitter", "consumed_by": ["maintainer"]},
                {"path": "tools/validate_example.py", "role": "local consistency validator", "consumed_by": ["maintainer"]},
                {"path": "tools/refine_terminal_witnesses.py", "role": "terminal-witness ledger refiner", "consumed_by": ["maintainer"]},
                {"path": "tools/rebuild_example.sh", "role": "one-shot rebuild helper", "consumed_by": ["maintainer"]},
            ],
        },
    ],
    "note": "Maintenance inventory for the worked-example support bundle maintained alongside the worked note. It groups published adjuncts, the note source, and local maintenance helpers by operational role without making them part of the receipt schema, and it points back to the companion support manifest for the same maintained bundle cut.",
}
artifact_inventory_digest = write_json(ART / "example_artifact_inventory.json", artifact_inventory)

support_manifest = {
    "manifest_id": MANIFEST_ID,
    "artifact_inventory_id": INVENTORY_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "note": "Digest-bound maintenance manifest for the worked-example support bundle. It points back to the companion artifact inventory for the same maintained bundle cut.",
    "files": [
        {"path": "example_abom.json", "sha256": abom_digest},
        {"path": "example_exposure_nf_registry.json", "sha256": exposure_registry_digest},
        {"path": "example_tw_decl.json", "sha256": tw_decl_digest},
        {"path": "example_state_decl_registry.json", "sha256": state_decl_registry_digest},
        {"path": "example_receipt.json", "sha256": receipt_digest},
        {"path": "example_receipt_prefixfetch_variant.json", "sha256": variant_receipt_digest},
        {"path": "example_receipt_prefixfetch_statecond_variant.json", "sha256": statecond_receipt_digest},
        {"path": "example_receipt_contact_coarsened_variant.json", "sha256": contact_coarsened_receipt_digest},
        {"path": "example_release_receipt.json", "sha256": release_digest},
        {"path": "example_primary_surface_manifest.json", "sha256": primary_surface_digest},
        {"path": "example_replay_plans.json", "sha256": plan_catalog_digest},
        {"path": "example_support_bundle_map.json", "sha256": support_bundle_map_digest},
        {"path": "example_profiling_evidence.json", "sha256": profiling_evidence_digest},
        {"path": "example_profiling_evidence_prefixfetch.json", "sha256": profiling_prefix_evidence_digest},
        {"path": "example_profiling_evidence_prefixfetch_statecond.json", "sha256": profiling_statecond_evidence_digest},
        {"path": "example_profiling_evidence_contact_coarsened.json", "sha256": contact_coarsened_evidence_digest},
        {"path": "example_coarsening_map_contact.json", "sha256": coarsening_map_digest},
        {"path": "example_compare_profile.json", "sha256": compare_profile_digest},
        {"path": "example_compare_walkthrough.json", "sha256": compare_walkthrough_digest},
        {"path": "example_successor_derivation_graph.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_status_envelope.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_release_spine.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_release_stage_walkthrough.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_claim_support_map.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_citation_map.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_challenge_stop_profiles.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_challenge_routes.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_challenge_branches.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_quote_map.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_clause_pack.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_successor_sentence_locks.json", "sha256": "EMITTED_BY_COMPARE_HELPER"},
        {"path": "example_line_item_owner_map.json", "sha256": line_item_owner_map_digest},
        {"path": "example_effective_surface_resolution.json", "sha256": effective_surface_resolution_digest},
        {"path": "example_state_decl.json", "sha256": state_decl_digest},
        {"path": "example_user_watch_policy.json", "sha256": user_watch_digest},
        {"path": "example_change_control.json", "sha256": change_control_digest},
        {"path": "example_release_action_matrix.json", "sha256": release_action_matrix_digest},
        {"path": "example_release_obligation_profile.json", "sha256": release_obligation_profile_digest},
        {"path": "example_drift_cases.json", "sha256": drift_cases_digest},
        {"path": "example_uvi.json", "sha256": uvi_digest},
        {"path": "example_verifier_report.json", "sha256": verifier_digest},
        {"path": "example_artifact_inventory.json", "sha256": artifact_inventory_digest},
        {"path": "../README.md", "sha256": sha256_bytes((ROOT / "README.md").read_bytes())},
        {"path": "../paper.tex", "sha256": sha256_bytes((ROOT / "paper.tex").read_bytes())},
        {"path": "../tools/materialize_example.py", "sha256": sha256_bytes((ROOT / "tools" / "materialize_example.py").read_bytes())},
        {"path": "../tools/emit_compare_report.py", "sha256": sha256_bytes((ROOT / "tools" / "emit_compare_report.py").read_bytes())},
        {"path": "../tools/validate_example.py", "sha256": sha256_bytes((ROOT / "tools" / "validate_example.py").read_bytes())},
        {"path": "../tools/refine_terminal_witnesses.py", "sha256": sha256_bytes((ROOT / "tools" / "refine_terminal_witnesses.py").read_bytes())},
        {"path": "../tools/rebuild_example.sh", "sha256": sha256_bytes((ROOT / "tools" / "rebuild_example.sh").read_bytes())},
    ]
}
write_json(ART / "support_manifest.json", support_manifest)
