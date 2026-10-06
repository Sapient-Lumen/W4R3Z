from packet_contract_common import require_named_standard_packet_and_vocabulary

# These are mechanically declarative packet/vocabulary contracts that formerly
# lived as one tiny wrapper file per kind. Keeping them in one batch preserves
# the exact packet specs while reducing validation-toolchain file sprawl.
CONSOLIDATED_WITNESS_CONTRACTS = [
    "stake_refresh_witness_contract",
    "selector_witness_contract",
    "selector_freshness_witness_contract",
    "selector_provenance_witness_contract",
    "response_witness_contract",
    "recovery_loss_witness_contract",
    "refresh_support_witness_contract",
    "recovery_anchor_witness_contract",
    "repair_scope_witness_contract",
    "refresh_strength_witness_contract",
    "stake_continuity_witness_contract",
    "refresh_elevation_witness_contract",
    "recovery_identity_witness_contract",
    "enforcement_regime_witness_contract",
    "recovery_promotion_witness_contract",
    "recovery_writeback_witness_contract",
    "refresh_scope_basis_witness_contract",
    "selector_enforcement_witness_contract",
    "refresh_burden_scope_witness_contract",
    "refresh_independence_witness_contract",
    "refresh_scope_extent_witness_contract",
    "refresh_scope_axis_witness_contract",
    "refresh_scope_axis_coupling_witness_contract",
    "refresh_scope_distribution_witness_contract",
    "refresh_scope_axis_durability_witness_contract",
    "refresh_scope_axis_enforcement_witness_contract",
    "refresh_scope_axis_materiality_witness_contract",
    "refresh_scope_axis_remediation_witness_contract",
    "refresh_scope_axis_independence_witness_contract",
    "refresh_scope_axis_remediation_collateral_witness_contract",
    "refresh_scope_axis_remediation_capacity_source_witness_contract",
    "refresh_scope_axis_remediation_displacement_aftercare_witness_contract",
    "refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract",
    "refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract",
    "refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract",
    "refresh_scope_axis_remediation_displacement_performance_shadow_source_witness_contract",
]

seen = set()
for kind in CONSOLIDATED_WITNESS_CONTRACTS:
    if kind in seen:
        raise SystemExit(f"duplicate declarative witness contract in batch: {kind}")
    seen.add(kind)
    require_named_standard_packet_and_vocabulary(kind)

print(f"check_declarative_witness_contract_batch: OK ({len(CONSOLIDATED_WITNESS_CONTRACTS)} contracts)")
