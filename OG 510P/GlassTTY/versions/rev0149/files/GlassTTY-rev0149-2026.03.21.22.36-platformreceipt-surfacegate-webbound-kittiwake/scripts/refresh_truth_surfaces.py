#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from doctor import build_report as build_doctor_report
from native_host_report import build_report as build_native_host_report
from readiness_report import capture_readiness_report
from control_plane_report import capture_control_plane_report
from install_receipt import capture_install_receipt
from support_surface_snapshot import capture_support_surface_snapshot
from operator_handoff import capture_operator_handoff
from check_opening_contract import capture_opening_surface
from truth_surface_register import capture_truth_surface_register
from truth_surface_warnings import capture_truth_surface_warnings
from validation_artifact_inventory import capture_validation_artifact_inventory
from support_bundle_queue import capture_support_bundle_queue
from published_support_surface import capture_published_support_surface, write_root_published_support_surface
from support_publish_gate import capture_support_publish_gate, write_root_support_publish_gate
from support_source_baseline import capture_support_source_baseline, write_root_support_source_baseline
from check_support_bundle_contract import write_root_conformance as write_support_bundle_contract
from check_revision_receipt import write_root_conformance as write_revision_receipt_conformance
from second_adapter_report import capture_second_adapter_report, write_root_second_adapter_report
from second_adapter_brief import capture_second_adapter_brief, write_root_second_adapter_brief
from chatgpt_first_proof_kit import capture_chatgpt_first_proof_kit, write_root_chatgpt_first_proof_kit, write_candidate_bundle_manifest
from chatgpt_posture_matrix import capture_chatgpt_posture_matrix, write_root_chatgpt_posture_matrix
from chatgpt_branch_guard import capture_chatgpt_branch_guard, write_root_chatgpt_branch_guard
from chatgpt_route_witness_receipt import capture_chatgpt_route_witness_receipt, write_root_chatgpt_route_witness_receipt
from chatgpt_composer_witness_receipt import capture_chatgpt_composer_witness_receipt, write_root_chatgpt_composer_witness_receipt
from chatgpt_submit_witness_receipt import capture_chatgpt_submit_witness_receipt, write_root_chatgpt_submit_witness_receipt
from chatgpt_proof_bundle_receipt import capture_chatgpt_proof_bundle_receipt, write_root_chatgpt_proof_bundle_receipt
from chatgpt_promotion_stability_receipt import capture_chatgpt_promotion_stability_receipt, write_root_chatgpt_promotion_stability_receipt
from chatgpt_support_claim_receipt import capture_chatgpt_support_claim_receipt, write_root_chatgpt_support_claim_receipt
from chatgpt_capability_profile_receipt import capture_chatgpt_capability_profile_receipt, write_root_chatgpt_capability_profile_receipt
from chatgpt_auth_workspace_receipt import capture_chatgpt_auth_workspace_receipt, write_root_chatgpt_auth_workspace_receipt
from chatgpt_plan_envelope_receipt import capture_chatgpt_plan_envelope_receipt, write_root_chatgpt_plan_envelope_receipt
from chatgpt_browser_envelope_receipt import capture_chatgpt_browser_envelope_receipt, write_root_chatgpt_browser_envelope_receipt
from chatgpt_retention_envelope_receipt import capture_chatgpt_retention_envelope_receipt, write_root_chatgpt_retention_envelope_receipt
from chatgpt_platform_envelope_receipt import capture_chatgpt_platform_envelope_receipt, write_root_chatgpt_platform_envelope_receipt

ROOT = Path(__file__).resolve().parent.parent
REPORT_COMMAND = 'python scripts/refresh-truth-surfaces.py --pretty'


def refresh_truth_surfaces(*, root: Path = ROOT) -> dict[str, Any]:
    doctor_report = build_doctor_report()
    native_host_report = build_native_host_report()
    opening = capture_opening_surface(root=root)
    readiness = capture_readiness_report(root=root, doctor_report=doctor_report)
    control_plane = capture_control_plane_report(root=root, doctor_report=doctor_report)
    install_receipt = capture_install_receipt(root=root, doctor_report=doctor_report, native_host_report=native_host_report)
    support_surface = capture_support_surface_snapshot(root=root)
    operator_handoff = capture_operator_handoff(root=root, doctor_report=doctor_report)
    validation_inventory = capture_validation_artifact_inventory(validation_dir=root / 'validation' / 'latest')
    support_source_baseline = capture_support_source_baseline(root=root)
    second_adapter_report = capture_second_adapter_report(root=root)
    second_adapter_brief = capture_second_adapter_brief(root=root)
    chatgpt_first_proof_kit = capture_chatgpt_first_proof_kit(root=root)
    chatgpt_posture_matrix = capture_chatgpt_posture_matrix(root=root)
    chatgpt_branch_guard = capture_chatgpt_branch_guard(root=root)
    chatgpt_route_witness_receipt = capture_chatgpt_route_witness_receipt(root=root)
    chatgpt_composer_witness_receipt = capture_chatgpt_composer_witness_receipt(root=root)
    chatgpt_submit_witness_receipt = capture_chatgpt_submit_witness_receipt(root=root)
    chatgpt_proof_bundle_receipt = capture_chatgpt_proof_bundle_receipt(root=root)
    chatgpt_promotion_stability_receipt = capture_chatgpt_promotion_stability_receipt(root=root)
    chatgpt_support_claim_receipt = capture_chatgpt_support_claim_receipt(root=root)
    chatgpt_capability_profile_receipt = capture_chatgpt_capability_profile_receipt(root=root)
    chatgpt_auth_workspace_receipt = capture_chatgpt_auth_workspace_receipt(root=root)
    chatgpt_plan_envelope_receipt = capture_chatgpt_plan_envelope_receipt(root=root)
    chatgpt_browser_envelope_receipt = capture_chatgpt_browser_envelope_receipt(root=root)
    chatgpt_retention_envelope_receipt = capture_chatgpt_retention_envelope_receipt(root=root)
    chatgpt_platform_envelope_receipt = capture_chatgpt_platform_envelope_receipt(root=root)
    write_root_support_source_baseline(root=root)
    write_root_second_adapter_report(root=root)
    write_root_second_adapter_brief(root=root)
    write_root_chatgpt_first_proof_kit(root=root)
    write_root_chatgpt_posture_matrix(root=root)
    write_root_chatgpt_branch_guard(root=root)
    write_root_chatgpt_route_witness_receipt(root=root)
    write_root_chatgpt_composer_witness_receipt(root=root)
    write_root_chatgpt_submit_witness_receipt(root=root)
    write_root_chatgpt_proof_bundle_receipt(root=root)
    write_root_chatgpt_promotion_stability_receipt(root=root)
    write_root_chatgpt_support_claim_receipt(root=root)
    write_root_chatgpt_capability_profile_receipt(root=root)
    write_root_chatgpt_auth_workspace_receipt(root=root)
    write_root_chatgpt_plan_envelope_receipt(root=root)
    write_root_chatgpt_browser_envelope_receipt(root=root)
    write_root_chatgpt_retention_envelope_receipt(root=root)
    write_root_chatgpt_platform_envelope_receipt(root=root)
    write_candidate_bundle_manifest(root=root)
    truth_register = capture_truth_surface_register(root=root)
    truth_warnings = capture_truth_surface_warnings(root=root)
    support_bundle_queue = capture_support_bundle_queue(root=root)
    published_support_surface = capture_published_support_surface(root=root)
    support_publish_gate = capture_support_publish_gate(root=root)
    write_root_published_support_surface(root=root)
    write_root_support_publish_gate(root=root)
    support_bundle_contract = write_support_bundle_contract(root=root)
    revision_receipt = write_revision_receipt_conformance(root=root)
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'commands': {'refresh_truth_surfaces': REPORT_COMMAND},
        'captures': {
            'opening_surface': opening.get('history_update'),
            'readiness_report': readiness.get('history_update'),
            'control_plane_report': control_plane.get('history_update'),
            'install_receipt': install_receipt.get('history_update'),
            'support_surface': support_surface.get('history_update'),
            'operator_handoff': (operator_handoff.get('history_update') or {}).get('capture_count_after_write'),
            'truth_surface_register': str(root / 'validation' / 'latest' / 'truth-surface-register' / 'truth-surface-register.json'),
            'truth_surface_warnings': str(root / 'validation' / 'latest' / 'truth-surface-warnings' / 'truth-surface-warnings.json'),
            'validation_artifact_inventory': str(root / 'validation' / 'latest' / 'validation-artifact-inventory' / 'artifact-buckets.json'),
            'support_bundle_queue': str(root / 'validation' / 'latest' / 'support-bundle-queue' / 'support-bundle-queue.json'),
            'published_support_surface': str(root / 'validation' / 'latest' / 'published-support-surface' / 'support-public-surface.json'),
            'support_publish_gate': str(root / 'validation' / 'latest' / 'support-publish-gate' / 'support-publish-gate.json'),
            'support_source_baseline': str(root / 'validation' / 'latest' / 'support-source-baseline' / 'support-source-baseline.json'),
            'second_adapter_report': str(root / 'validation' / 'latest' / 'second-adapter-report' / 'second-adapter-report.json'),
            'second_adapter_brief': str(root / 'validation' / 'latest' / 'second-adapter-brief' / 'second-adapter-brief.json'),
            'chatgpt_first_proof_kit': str(root / 'validation' / 'latest' / 'chatgpt-first-proof-kit' / 'chatgpt-first-proof-kit.json'),
            'chatgpt_posture_matrix': str(root / 'validation' / 'latest' / 'chatgpt-posture-matrix' / 'chatgpt-posture-matrix.json'),
            'chatgpt_branch_guard': str(root / 'validation' / 'latest' / 'chatgpt-branch-guard' / 'chatgpt-branch-guard.json'),
            'chatgpt_route_witness_receipt': str(root / 'validation' / 'latest' / 'chatgpt-route-witness-receipt' / 'chatgpt-route-witness-receipt.json'),
            'chatgpt_composer_witness_receipt': str(root / 'validation' / 'latest' / 'chatgpt-composer-witness-receipt' / 'chatgpt-composer-witness-receipt.json'),
            'chatgpt_submit_witness_receipt': str(root / 'validation' / 'latest' / 'chatgpt-submit-witness-receipt' / 'chatgpt-submit-witness-receipt.json'),
            'chatgpt_proof_bundle_receipt': str(root / 'validation' / 'latest' / 'chatgpt-proof-bundle-receipt' / 'chatgpt-proof-bundle-receipt.json'),
            'chatgpt_promotion_stability_receipt': str(root / 'validation' / 'latest' / 'chatgpt-promotion-stability-receipt' / 'chatgpt-promotion-stability-receipt.json'),
            'chatgpt_support_claim_receipt': str(root / 'validation' / 'latest' / 'chatgpt-support-claim-receipt' / 'chatgpt-support-claim-receipt.json'),
            'chatgpt_capability_profile_receipt': str(root / 'validation' / 'latest' / 'chatgpt-capability-profile-receipt' / 'chatgpt-capability-profile-receipt.json'),
            'chatgpt_auth_workspace_receipt': str(root / 'validation' / 'latest' / 'chatgpt-auth-workspace-receipt' / 'chatgpt-auth-workspace-receipt.json'),
            'chatgpt_browser_envelope_receipt': str(root / 'validation' / 'latest' / 'chatgpt-browser-envelope-receipt' / 'chatgpt-browser-envelope-receipt.json'),
            'chatgpt_retention_envelope_receipt': str(root / 'validation' / 'latest' / 'chatgpt-retention-envelope-receipt' / 'chatgpt-retention-envelope-receipt.json'),
            'chatgpt_platform_envelope_receipt': str(root / 'validation' / 'latest' / 'chatgpt-platform-envelope-receipt' / 'chatgpt-platform-envelope-receipt.json'),
            'support_bundle_contract': str(root / 'SUPPORT-BUNDLE-CONTRACT.json'),
            'support_public_surface': str(root / 'SUPPORT-PUBLIC-SURFACE.json'),
            'support_publish_gate_root': str(root / 'SUPPORT-PUBLISH-GATE.json'),
            'support_source_baseline_root': str(root / 'SUPPORT-SOURCE-BASELINE.json'),
            'second_adapter_report_root': str(root / 'SECOND-ADAPTER-REPORT.json'),
            'second_adapter_brief_root': str(root / 'SECOND-ADAPTER-BRIEF.json'),
            'chatgpt_first_proof_kit_root': str(root / 'CHATGPT-FIRST-PROOF-KIT.json'),
            'chatgpt_posture_matrix_root': str(root / 'CHATGPT-POSTURE-MATRIX.json'),
            'chatgpt_branch_guard_root': str(root / 'CHATGPT-BRANCH-GUARD.json'),
            'chatgpt_route_witness_receipt_root': str(root / 'CHATGPT-ROUTE-WITNESS-RECEIPT.json'),
            'chatgpt_composer_witness_receipt_root': str(root / 'CHATGPT-COMPOSER-WITNESS-RECEIPT.json'),
            'chatgpt_submit_witness_receipt_root': str(root / 'CHATGPT-SUBMIT-WITNESS-RECEIPT.json'),
            'chatgpt_proof_bundle_receipt_root': str(root / 'CHATGPT-PROOF-BUNDLE-RECEIPT.json'),
            'chatgpt_promotion_stability_receipt_root': str(root / 'CHATGPT-PROMOTION-STABILITY-RECEIPT.json'),
            'chatgpt_support_claim_receipt_root': str(root / 'CHATGPT-SUPPORT-CLAIM-RECEIPT.json'),
            'chatgpt_capability_profile_receipt_root': str(root / 'CHATGPT-CAPABILITY-PROFILE-RECEIPT.json'),
            'chatgpt_auth_workspace_receipt': str(root / 'validation' / 'latest' / 'chatgpt-auth-workspace-receipt' / 'chatgpt-auth-workspace-receipt.json'),
            'chatgpt_plan_envelope_receipt': str(root / 'validation' / 'latest' / 'chatgpt-plan-envelope-receipt' / 'chatgpt-plan-envelope-receipt.json'),
            'chatgpt_browser_envelope_receipt': str(root / 'validation' / 'latest' / 'chatgpt-browser-envelope-receipt' / 'chatgpt-browser-envelope-receipt.json'),
            'chatgpt_auth_workspace_receipt_root': str(root / 'CHATGPT-AUTH-WORKSPACE-RECEIPT.json'),
            'chatgpt_plan_envelope_receipt_root': str(root / 'CHATGPT-PLAN-ENVELOPE-RECEIPT.json'),
            'chatgpt_browser_envelope_receipt_root': str(root / 'CHATGPT-BROWSER-ENVELOPE-RECEIPT.json'),
            'chatgpt_retention_envelope_receipt_root': str(root / 'CHATGPT-RETENTION-ENVELOPE-RECEIPT.json'),
            'chatgpt_platform_envelope_receipt_root': str(root / 'CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json'),
            'chatgpt_candidate_bundle': str(root / 'docs' / 'support-bundles' / 'candidate' / 'chatgpt-routefirst-chromium-live-candidate.json'),
            'revision_receipt_conformance': str(root / 'REVISION-RECEIPT-CONFORMANCE.json'),
        },
        'truth_surface_counts': (truth_register.get('counts') if isinstance(truth_register, dict) else None),
        'truth_surface_warning_counts': (truth_warnings.get('counts') if isinstance(truth_warnings, dict) else None),
        'validation_artifact_buckets': (validation_inventory.get('bucket_count') if isinstance(validation_inventory, dict) else None),
        'support_bundle_count': ((support_bundle_queue.get('report') or {}).get('counts') or {}).get('bundle_count') if isinstance(support_bundle_queue, dict) else None,
        'published_support_citable_surface_count': ((published_support_surface.get('snapshot') or {}).get('counts') or {}).get('citable_surface_count') if isinstance(published_support_surface, dict) else None,
        'support_publish_gate_ready_count': ((support_publish_gate.get('report') or {}).get('counts') or {}).get('published_ready_pass_count') if isinstance(support_publish_gate, dict) else None,
        'support_publish_gate_publish_count': ((support_publish_gate.get('report') or {}).get('counts') or {}).get('published_pass_count') if isinstance(support_publish_gate, dict) else None,
        'support_source_count': ((support_source_baseline.get('snapshot') or {}).get('counts') or {}).get('source_count') if isinstance(support_source_baseline, dict) else None,
        'support_source_warning_count': ((support_source_baseline.get('snapshot') or {}).get('counts') or {}).get('warning_count') if isinstance(support_source_baseline, dict) else None,
        'second_adapter_recommendation': ((second_adapter_report.get('recommendation') or {}).get('surface_key')) if isinstance(second_adapter_report, dict) else None,
        'second_adapter_phase_count': len((second_adapter_brief.get('phases') or [])) if isinstance(second_adapter_brief, dict) else None,
        'chatgpt_first_proof_hazard_count': len(((chatgpt_first_proof_kit.get('kit') or {}).get('ui_branching_hazards') or []) if isinstance(chatgpt_first_proof_kit, dict) else []),
        'chatgpt_posture_branch_count': ((chatgpt_posture_matrix.get('matrix') or {}).get('counts') or {}).get('branch_count') if isinstance(chatgpt_posture_matrix, dict) else None,
        'chatgpt_branch_guard_stop_count': ((chatgpt_branch_guard.get('guard') or {}).get('counts') or {}).get('stop_posture_count') if isinstance(chatgpt_branch_guard, dict) else None,
        'chatgpt_route_witness_quality_tier_count': len(((chatgpt_route_witness_receipt.get('receipt') or {}).get('quality_tiers') or []) if isinstance(chatgpt_route_witness_receipt, dict) else []),
        'chatgpt_composer_witness_quality_tier_count': len(((chatgpt_composer_witness_receipt.get('receipt') or {}).get('quality_tiers') or []) if isinstance(chatgpt_composer_witness_receipt, dict) else []),
        'chatgpt_promotion_stability_state_count': len(((chatgpt_promotion_stability_receipt.get('receipt') or {}).get('stability_readiness_states') or []) if isinstance(chatgpt_promotion_stability_receipt, dict) else []),
        'chatgpt_support_claim_state_count': len(((chatgpt_support_claim_receipt.get('receipt') or {}).get('claim_readiness_states') or []) if isinstance(chatgpt_support_claim_receipt, dict) else []),
        'chatgpt_capability_profile_state_count': len(((chatgpt_capability_profile_receipt.get('receipt') or {}).get('capability_readiness_states') or []) if isinstance(chatgpt_capability_profile_receipt, dict) else []),
        'chatgpt_auth_workspace_state_count': len(((chatgpt_auth_workspace_receipt.get('receipt') or {}).get('auth_workspace_readiness_states') or []) if isinstance(chatgpt_auth_workspace_receipt, dict) else []),
        'chatgpt_plan_envelope_state_count': len(((chatgpt_plan_envelope_receipt.get('receipt') or {}).get('plan_envelope_readiness_states') or []) if isinstance(chatgpt_plan_envelope_receipt, dict) else []),
        'chatgpt_browser_envelope_state_count': len(((chatgpt_browser_envelope_receipt.get('receipt') or {}).get('browser_envelope_readiness_states') or []) if isinstance(chatgpt_browser_envelope_receipt, dict) else []),
        'chatgpt_retention_envelope_state_count': len(((chatgpt_retention_envelope_receipt.get('receipt') or {}).get('retention_envelope_readiness_states') or []) if isinstance(chatgpt_retention_envelope_receipt, dict) else []),
        'chatgpt_platform_envelope_state_count': len(((chatgpt_platform_envelope_receipt.get('receipt') or {}).get('platform_envelope_readiness_states') or []) if isinstance(chatgpt_platform_envelope_receipt, dict) else []),
        'support_bundle_contract_valid': support_bundle_contract.get('all_valid') if isinstance(support_bundle_contract, dict) else None,
        'revision_receipt_valid': revision_receipt.get('all_valid') if isinstance(revision_receipt, dict) else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Refresh GlassTTY opening/install/readiness/support/handoff truth surfaces into validation/latest.')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    payload = refresh_truth_surfaces(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
