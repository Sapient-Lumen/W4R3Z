#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f'[check_cube] FAIL: {msg}')
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f'[check_cube] OK: {msg}')


def text(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        fail(f'missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def j(rel: str):
    try:
        return json.loads(text(rel))
    except Exception as exc:
        fail(f'{rel} invalid JSON: {exc}')


def require_all(rel: str, needles: list[str]) -> None:
    body = text(rel)
    missing = [needle for needle in needles if needle not in body]
    if missing:
        fail(f'{rel} missing {missing}')


def require_all_lower(rel: str, needles: list[str]) -> None:
    body = text(rel).lower()
    missing = [needle for needle in needles if needle.lower() not in body]
    if missing:
        fail(f'{rel} missing {missing}')


def runtime_revision() -> tuple[str, str, str, str]:
    rt = text('src/browserrt.mjs')
    rev = re.search(r"export const REVISION = '([^']+)';", rt)
    ver = re.search(r"export const VERSION = '([^']+)';", rt)
    if not rev or not ver:
        fail('src/browserrt.mjs missing REVISION/VERSION constants')
    revision = rev.group(1)
    prefix = 'REV' + revision[3:]
    previous = f"rev{int(revision[3:]) - 1:04d}"
    return revision, prefix, ver.group(1), previous


REV, PFX, VERSION, PREV = runtime_revision()
EXPECTED = {
    'revision': REV,
    'version': VERSION,
    'previous_revision': PREV,
    'codename': 'OPFS Block Store Rollback Valid Block Preserve',
    'package_slug': 'opfs-block-store-rollback-valid-block-preserve-current-proof',
    'current_task': 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
    'current_slice': 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
    'current_runtime_slice': 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
    'current_audit': 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
    'current_audit_slice': 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
}
CORE_NONCLAIMS = ['cross-browser', 'quota', 'eviction', 'crash', 'browser-light']

REQUIRED_FILES = [
    'README.md', 'START_HERE.md', 'CONTEXT-PACK.md', 'AGENTS.md', 'CHANGELOG.md', 'Makefile', 'package.json',
    'REVISION-RECEIPT.json', 'CUBE-META.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json',
    'src/browserrt.mjs', 'src/types.d.ts', 'src/opfs-block-store.mjs', 'src/web-lock-coordinator.mjs', 'src/opfs-web-lock-guarded-block-store.mjs', 'src/storage-lane-scheduler.mjs', 'src/block-store-lane-adapter.mjs',


    'tools/storage_lane_quarantine_status_transition_import_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_status_transition_import_probe.mjs',
    'tools/storage_lane_quarantine_status_transition_import_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-status-transition-import-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-status-transition-import-slice.md',
    'docs/40-validation/storage-lane-quarantine-status-transition-import-contract-audit-slice.md',
    'tools/storage_lane_quarantine_receipt_restore_integrity_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_receipt_restore_integrity_probe.mjs',
    'tools/storage_lane_quarantine_receipt_restore_integrity_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-receipt-restore-integrity-slice.md',
    'docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-contract-audit-slice.md',
    'tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs',
    'tools/storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs',
    'tools/lib/quarantine_restore_expected_fingerprint_harness.mjs',
    'tools/current_office_audit.mjs',
    'tools/web_lock_strict_option_guard_probe.mjs',
    'tools/browser_opfs_web_lock_strict_option_guard_probe.mjs',
    'tools/web_lock_strict_option_guard_contract_audit.mjs',
    'docs/40-validation/web-lock-strict-option-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-strict-option-guard-slice.md',
    'docs/40-validation/web-lock-strict-option-guard-contract-audit-slice.md',
    'tools/lib/fake_opfs_harness.mjs',
    'tools/opfs_block_store_abort_signal_probe.mjs',
    'tools/browser_opfs_block_store_abort_signal_probe.mjs',
    'tools/opfs_block_store_abort_signal_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-abort-signal-slice.md',
    'docs/40-validation/browser-opfs-block-store-abort-signal-slice.md',
    'docs/40-validation/opfs-block-store-abort-signal-contract-audit-slice.md',
    'tools/opfs_block_store_write_budget_guard_probe.mjs',
    'tools/browser_opfs_block_store_write_budget_guard_probe.mjs',
    'tools/opfs_block_store_write_budget_guard_contract_audit.mjs',
    'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-write-budget-guard-slice.md',
    'docs/40-validation/browser-opfs-block-store-write-budget-guard-slice.md',
    'docs/40-validation/opfs-block-store-write-budget-guard-contract-audit-slice.md',
    'tools/opfs_block_store_owned_rollback_guard_probe.mjs',
    'tools/browser_opfs_block_store_owned_rollback_guard_probe.mjs',
    'tools/opfs_block_store_owned_rollback_guard_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-owned-rollback-guard-slice.md',
    'docs/40-validation/browser-opfs-block-store-owned-rollback-guard-slice.md',
    'docs/40-validation/opfs-block-store-owned-rollback-guard-contract-audit-slice.md',
    'tools/opfs_block_store_write_budget_duplicate_bypass_probe.mjs',
    'tools/browser_opfs_block_store_write_budget_duplicate_bypass_probe.mjs',
    'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-slice.md',
    'docs/40-validation/browser-opfs-block-store-write-budget-duplicate-bypass-slice.md',
    'docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-contract-audit-slice.md',
    'tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs',
    'tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs',
    'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md',
    'docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md',
    'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-contract-audit-slice.md',
    'tools/lib/quarantine_restore_expected_fingerprint_harness.mjs',
    'tools/current_office_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-restore-expected-fingerprint-slice.md',
    'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_replay_key_receipt_integrity_probe.mjs',
    'tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit-slice.md',
    'tools/storage_lane_quarantine_review_replay_key_scope_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_review_replay_key_scope_probe.mjs',
    'tools/storage_lane_quarantine_review_replay_key_scope_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-review-replay-key-scope-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-review-replay-key-scope-slice.md',
    'docs/40-validation/storage-lane-quarantine-review-replay-key-scope-contract-audit-slice.md',
    'tools/storage_lane_unsettled_orphan_review_probe.mjs',
    'tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs',
    'tools/storage_lane_unsettled_orphan_review_contract_audit.mjs',
    'docs/40-validation/storage-lane-unsettled-orphan-review-slice.md',
    'docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md',
    'docs/40-validation/storage-lane-unsettled-orphan-review-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_receipt_provenance_binding_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_receipt_provenance_binding_probe.mjs',
    'tools/storage_lane_quarantine_clearance_receipt_provenance_binding_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-receipt-provenance-binding-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_row_replay_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_row_replay_guard_probe.mjs',
    'tools/storage_lane_quarantine_clearance_row_replay_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-row-replay-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-row-replay-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-row-replay-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_epoch_replay_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_epoch_replay_guard_probe.mjs',
    'tools/storage_lane_quarantine_clearance_epoch_replay_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-epoch-replay-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_epoch_replay_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_epoch_replay_guard_probe.mjs',
    'tools/storage_lane_quarantine_clearance_epoch_replay_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-epoch-replay-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_noop_clearance_receipt_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_noop_clearance_receipt_guard_probe.mjs',
    'tools/storage_lane_quarantine_noop_clearance_receipt_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-noop-clearance-receipt-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_replay_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_replay_guard_probe.mjs',
    'tools/storage_lane_quarantine_clearance_replay_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_noop_clearance_receipt_guard_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_noop_clearance_receipt_guard_probe.mjs',
    'tools/storage_lane_quarantine_noop_clearance_receipt_guard_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-noop-clearance-receipt-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-slice.md',
    'docs/40-validation/storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit-slice.md',
    'tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs',
    'tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-contract-audit-slice.md',
    'tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs',
    'tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-contract-audit-slice.md',
    'tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs',
    'tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-contract-audit-slice.md',
    'tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs',
    'tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-legacy-clear-binding-slice.md',
    'docs/40-validation/storage-lane-quarantine-legacy-clear-binding-contract-audit-slice.md',
    'tools/storage_lane_quarantine_ledger_persistence_integrity_probe.mjs',
  'tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs',
  'tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs',
  'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-slice.md',
  'docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-integrity-slice.md',
  'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-contract-audit-slice.md',
  'tools/storage_lane_quarantine_ledger_persistence_integrity_probe.mjs',
  'tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs',
  'tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs',
  'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-slice.md',
  'docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-integrity-slice.md',
  'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-contract-audit-slice.md',
  'tools/storage_lane_quarantine_ledger_roundtrip_probe.mjs', 'tools/browser_opfs_web_lock_quarantine_ledger_roundtrip_probe.mjs', 'tools/storage_lane_quarantine_ledger_contract_audit.mjs',
    'tools/storage_lane_quarantine_ledger_persistence_integrity_probe.mjs', 'tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs', 'tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-ledger-roundtrip-slice.md', 'docs/40-validation/browser-opfs-web-lock-quarantine-ledger-roundtrip-slice.md', 'docs/40-validation/storage-lane-quarantine-ledger-contract-audit-slice.md',
    'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-slice.md', 'docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-integrity-slice.md', 'docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-contract-audit-slice.md',
    'tools/storage_lane_quarantine_handoff_probe.mjs', 'tools/browser_opfs_web_lock_quarantine_handoff_probe.mjs', 'tools/storage_lane_quarantine_handoff_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-handoff-slice.md', 'docs/40-validation/browser-opfs-web-lock-quarantine-handoff-slice.md', 'docs/40-validation/storage-lane-quarantine-handoff-contract-audit-slice.md',
    'tools/storage_lane_late_settlement_recovery_gate_probe.mjs', 'tools/browser_opfs_web_lock_late_settlement_recovery_gate_probe.mjs', 'tools/storage_lane_late_settlement_contract_audit.mjs',
    'tools/storage_lane_late_failure_quarantine_probe.mjs', 'tools/browser_opfs_web_lock_late_failure_quarantine_probe.mjs', 'tools/storage_lane_late_failure_quarantine_contract_audit.mjs',
    'tools/storage_lane_late_success_quarantine_probe.mjs', 'tools/browser_opfs_web_lock_late_success_quarantine_probe.mjs', 'tools/storage_lane_late_success_quarantine_contract_audit.mjs',
    'tools/storage_lane_operation_context_propagation_probe.mjs', 'tools/browser_opfs_web_lock_operation_context_propagation_probe.mjs', 'tools/operation_context_propagation_contract_audit.mjs',
    'tools/storage_lane_operation_timeout_probe.mjs', 'tools/browser_opfs_web_lock_operation_timeout_probe.mjs', 'tools/storage_lane_operation_timeout_contract_audit.mjs',
    'tools/storage_lane_web_lock_read_timeout_nonpoison_probe.mjs', 'tools/browser_opfs_web_lock_read_timeout_nonpoison_probe.mjs', 'tools/web_lock_read_timeout_nonpoison_contract_audit.mjs',
    'tools/browser_cdp_fixture.mjs', 'tools/browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs', 'tools/service_worker_fetch_lifecycle_contract_audit.mjs', 'tools/browser_opfs_web_lock_service_worker_update_race_probe.mjs', 'tools/service_worker_update_race_contract_audit.mjs', 'tools/browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs', 'tools/service_worker_shutdown_boundary_contract_audit.mjs', 'tools/browser_opfs_web_lock_service_worker_restart_update_probe.mjs', 'tools/service_worker_restart_update_contract_audit.mjs', 'tools/browser_opfs_web_lock_service_worker_lifecycle_probe.mjs', 'tools/browserrt_opfs_web_lock_service_worker_holder.mjs', 'tools/service_worker_lifecycle_contract_audit.mjs', 'tools/browser_opfs_web_lock_settled_recovery_probe.mjs', 'tools/storage_lane_web_lock_settled_recovery_probe.mjs', 'tools/web_lock_settled_recovery_contract_audit.mjs',
    'tools/browser_opfs_web_lock_tab_timeout_probe.mjs', 'tools/storage_lane_web_lock_timeout_health_probe.mjs',
    'tools/browser_opfs_web_lock_tab_termination_probe.mjs', 'tools/web_lock_lifecycle_contract_audit.mjs', 'tools/branch_continuity_audit.mjs',
    'tools/browser_opfs_guarded_corrupt_repair_timeout_probe.mjs', 'tools/revision_lineage_merge_audit.mjs',
    'tools/opfs_block_store_corrupt_block_repair_probe.mjs', 'tools/browser_opfs_corrupt_block_repair_probe.mjs',
    'tools/web_lock_timeout_probe.mjs', 'tools/browser_opfs_web_lock_timeout_probe.mjs', 'tools/web_lock_timeout_contract_audit.mjs',
    'tools/browser_opfs_web_lock_guarded_contention_probe.mjs', 'tools/browser_opfs_abrupt_kill_boundary_probe.mjs', 'tools/browser_process_cleanup_audit.mjs',
    'tools/browser_opfs_lane_quota_backpressure_probe.mjs', 'tools/storage_lane_opfs_error_health_probe.mjs', 'tools/browser_opfs_quota_pressure_probe.mjs',
    'tools/artifact_budget_audit.mjs', 'tools/compact_duplicate_docs.mjs', 'tools/deep_cube_audit.mjs', 'tools/audit_cube_surfaces.mjs', 'tools/package_release.py', 'tools/verify_release.py',
    'docs/40-validation/storage-lane-late-settlement-recovery-gate-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-settlement-recovery-gate-slice.md', 'docs/40-validation/storage-lane-late-settlement-contract-audit-slice.md',
    'docs/40-validation/storage-lane-late-failure-quarantine-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md', 'docs/40-validation/storage-lane-late-failure-quarantine-contract-audit-slice.md',
    'docs/40-validation/storage-lane-late-success-quarantine-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-success-quarantine-slice.md', 'docs/40-validation/storage-lane-late-success-quarantine-contract-audit-slice.md',
    'docs/40-validation/storage-lane-operation-context-propagation-slice.md', 'docs/40-validation/browser-opfs-web-lock-operation-context-propagation-slice.md', 'docs/40-validation/operation-context-propagation-contract-audit-slice.md',
    'docs/40-validation/storage-lane-operation-timeout-slice.md', 'docs/40-validation/browser-opfs-web-lock-operation-timeout-boundary-slice.md',
    'docs/40-validation/browser-opfs-web-lock-read-timeout-nonpoison-slice.md', 'docs/40-validation/web-lock-read-timeout-nonpoison-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-fetch-lifecycle-slice.md', 'docs/40-validation/service-worker-fetch-lifecycle-contract-audit-slice.md', 'docs/40-validation/browser-opfs-web-lock-service-worker-update-race-slice.md', 'docs/40-validation/service-worker-update-race-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-shutdown-boundary-slice.md', 'docs/40-validation/service-worker-shutdown-boundary-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-restart-update-slice.md', 'docs/40-validation/service-worker-restart-update-contract-audit-slice.md', 'docs/40-validation/browser-opfs-web-lock-service-worker-lifecycle-slice.md', 'docs/40-validation/service-worker-lifecycle-contract-audit-slice.md', 'docs/40-validation/browser-opfs-web-lock-settled-recovery-slice.md', 'docs/40-validation/storage-lane-web-lock-settled-recovery-slice.md',
    'docs/40-validation/browser-opfs-web-lock-tab-timeout-slice.md', 'docs/40-validation/storage-lane-web-lock-timeout-health-slice.md',
    'docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md', 'docs/40-validation/browser-opfs-guarded-corrupt-repair-timeout-slice.md', 'docs/00-meta/rev0062-lineage-merge-note.md',
    'docs/40-validation/browser-opfs-corrupt-block-repair-slice.md', 'docs/40-validation/browser-opfs-web-lock-timeout-slice.md', 'docs/40-validation/branch-continuity-audit-slice.md',
    'docs/40-validation/web-lock-guarded-block-store-slice.md', 'docs/40-validation/browser-opfs-web-lock-guarded-contention-slice.md',
    'docs/40-validation/browser-opfs-abrupt-kill-boundary-slice.md', 'docs/40-validation/browser-opfs-lane-quota-backpressure-slice.md',
    'docs/40-validation/browser-opfs-quota-pressure-slice.md', 'docs/40-validation/browser-opfs-restart-persistence-slice.md',
    f'docs/00-meta/revision-doc-compaction-index-{REV}.md', f'artifacts/datacube-audit/{PFX}-DUPLICATE-DOC-COMPACTION.json',
    'tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_replay_key_receipt_integrity_probe.mjs',
    'tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit-slice.md',
    'test/manifest.json', 'test/impact-map.json', 'test/surface-inventory.json', 'test/quarantine.json',
    'artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json', 'artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json',
]
for rel in REQUIRED_FILES:
    text(rel)
ok('required files present')

package = j('package.json')
if package.get('revision') != REV or package.get('version') != VERSION:
    fail(f'package.json {package.get("revision")} {package.get("version")} != runtime {REV} {VERSION}')
for key in ['codename', 'package_slug', 'current_task', 'current_slice']:
    if package.get(key) != EXPECTED[key]:
        fail(f'package.json {key} {package.get(key)!r} != {EXPECTED[key]!r}')
ok('package metadata aligned')

current_scripts = package.get('scripts', {})
current_script_expectations = {
    'test:current': [
        'opfs:block-store-rollback-valid-block-preserve-proof',
        'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
        f'{PFX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json',
    ],
    'test:browser:current': [
        'browser:opfs-block-store-rollback-valid-block-preserve-proof',
        f'{PFX}-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json',
    ],
    'test:browser-current': [
        'browser:opfs-block-store-rollback-valid-block-preserve-proof',
        f'{PFX}-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json',
    ],
    'audit:current': [
        'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
        f'{PFX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-CONTRACT-AUDIT.json',
        'tools/current_office_audit.mjs',
        f'{PFX}-CURRENT-OFFICE-AUDIT.json',
    ],
    'package:current': [
        'tools/package_release.py',
        EXPECTED['package_slug'],
        '--reuse-validation',
    ],
}
for name, needles in current_script_expectations.items():
    body = current_scripts.get(name, '')
    if not body:
        fail(f'package.json scripts.{name} is missing')
    missing = [needle for needle in needles if needle not in body]
    if missing:
        fail(f'package.json scripts.{name} is stale; missing {missing}')
    stale_needles = [
        'quarantine-clearance-receipt-provenance-binding',
        'quarantine-clearance-replay-guard',
        'quarantine-restore-expected-fingerprint',
        'expected-fingerprint',
        'REV0089',
        'REV0090',
        'REV0091',
        'REV0092',
        'REV0093',
        'REV0094',
        'strict-option',
        'WEB-LOCK-STRICT-OPTION',
        'abort-signal',
        'OPFS-BLOCK-STORE-ABORT-SIGNAL', 'OPFS-BLOCK-STORE-WRITE-BUDGET-GUARD', 'OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD',
        'REV0095',
        'REV0096',
        'REV0097', 'REV0098',
    ]
    stale = [needle for needle in stale_needles if needle in body]
    if stale:
        fail(f'package.json scripts.{name} carries stale current alias needles {stale}')
allowed_current_scripts = set(current_script_expectations)
extra_current_scripts = sorted(name for name in current_scripts if 'current' in name and name not in allowed_current_scripts)
if extra_current_scripts:
    fail(f'package.json has historical scripts masquerading as current aliases: {extra_current_scripts}')
for replay_name in ['replay:quarantine-status-transition-import', 'replay:quarantine-receipt-restore-integrity', 'replay:quarantine-clearance-receipt-provenance-binding']:
    if replay_name not in current_scripts:
        fail(f'package.json missing explicit historical replay alias {replay_name}')
for script_name, script_body in current_scripts.items():
    for hit in re.findall(r'REV\d{4}-', script_body):
        if hit != f'{PFX}-':
            fail(f'package.json scripts.{script_name} emits stale generated-artifact prefix {hit}')
makefile_all = text('Makefile')
def make_target_blocks(body, names):
    blocks = []
    capture = False
    current = []
    for line in body.splitlines():
        m = re.match(r'^([A-Za-z0-9_.:-]+):', line)
        if m:
            if capture:
                blocks.append('\n'.join(current))
            capture = m.group(1) in names
            current = [line] if capture else []
        elif capture:
            current.append(line)
    if capture:
        blocks.append('\n'.join(current))
    return '\n'.join(blocks)
make_head = make_target_blocks(makefile_all, {'current', 'browser', 'release', 'audit', 'package', 'verify'})
for needle in ['opfs:block-store-rollback-valid-block-preserve-proof', 'browser:opfs-block-store-rollback-valid-block-preserve-proof', 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit', 'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs', 'tools/current_office_audit.mjs', EXPECTED['package_slug'], 'ZIP ?=']:
    if needle not in (make_head + '\n' + makefile_all):
        fail(f'Makefile primary current office missing {needle!r}')
for stale in ['REV0089', 'REV0090', 'REV0091', 'REV0092', 'REV0093', 'REV0094', 'REV0095', 'REV0096', 'REV0097', 'REV0098', 'provenance-binding', 'replay-guard', 'expected-fingerprint', 'strict-option', 'abort-signal', 'owned-rollback', 'OPFS-BLOCK-STORE-ABORT-SIGNAL', 'OPFS-BLOCK-STORE-WRITE-BUDGET-GUARD', 'OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD']:
    if stale in make_head:
        fail(f'Makefile primary current office carries stale needle {stale!r}')
ok('package current convenience scripts and Makefile current office aligned')

def check_current_metadata_file(rel, obj):
    for key, expected in EXPECTED.items():
        if obj.get(key) != expected:
            fail(f'{rel} {key} {obj.get(key)!r} != {expected!r}')
    for key in ['filename', 'packaged_bundle_filename', 'package_filename', 'package_files', 'packageFileName', 'package_file_name']:
        if key not in obj or obj.get(key) is None:
            continue
        value = str(obj.get(key))
        if REV not in value or EXPECTED['package_slug'] not in value:
            fail(f'{rel} {key} is stale: {value!r}')
        if re.search(r'rev009[0-8]', value) or 'write-budget-guard-current-proof' in value or 'open-failure-recovery-current-proof' in value or 'write-budget-duplicate-bypass-current-proof' in value:
            fail(f'{rel} {key} carries stale package filename: {value!r}')
    current = obj.get('browserrt_current')
    if current:
        expected_current = {
            'revision': REV,
            'version': VERSION,
            'codename': EXPECTED['codename'],
            'release_task': 'opfs:block-store-rollback-valid-block-preserve-proof',
            'browser_task': 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
            'audit_task': 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
            'package_slug': EXPECTED['package_slug'],
        }
        for key, expected in expected_current.items():
            if current.get(key) != expected:
                fail(f'{rel} browserrt_current.{key} {current.get(key)!r} != {expected!r}')

for rel in ['package.json', 'CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json']:
    check_current_metadata_file(rel, j(rel))
ok('central current-office metadata aligned')

for rel in ['test/manifest.json', 'test/impact-map.json', 'test/surface-inventory.json', 'test/quarantine.json', 'artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json', 'artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json']:
    obj = j(rel)
    if obj.get('revision') != REV:
        fail(f'{rel} revision {obj.get("revision")} != {REV}')
ok('registry/test metadata revisions aligned')

if not text('CHANGELOG.md').startswith(f'## {REV} —'):
    fail('CHANGELOG.md top heading is not current revision')
if f'Current packaged head: `{REV}`' not in text('README.md') or f'Current packaged head: `{REV}`' not in text('START_HERE.md'):
    fail('README.md or START_HERE.md lacks current packaged head')
if f'Current revision: {REV}' not in text('AGENTS.md') or EXPECTED['codename'] not in text('AGENTS.md'):
    fail('AGENTS.md lacks current revision/codename')
if REV not in text('CONTEXT-PACK.md') or EXPECTED['codename'] not in text('CONTEXT-PACK.md'):
    fail('CONTEXT-PACK.md header is stale')
for rel in ['README.md', 'START_HERE.md', 'CONTEXT-PACK.md', 'AGENTS.md', 'REVISION-RECEIPT.json']:
    body = text(rel).lower()
    missing = [needle for needle in CORE_NONCLAIMS if needle not in body]
    if missing:
        fail(f'{rel} missing core nonclaim terms {missing}')
ok('first-read docs current and non-claims visible')

for rel in [
    'docs/40-validation/storage-lane-late-settlement-recovery-gate-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-settlement-recovery-gate-slice.md', 'docs/40-validation/storage-lane-late-settlement-contract-audit-slice.md',
    'docs/40-validation/storage-lane-late-failure-quarantine-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md', 'docs/40-validation/storage-lane-late-failure-quarantine-contract-audit-slice.md',
    'docs/40-validation/storage-lane-late-success-quarantine-slice.md', 'docs/40-validation/browser-opfs-web-lock-late-success-quarantine-slice.md', 'docs/40-validation/storage-lane-late-success-quarantine-contract-audit-slice.md',
    'docs/40-validation/storage-lane-operation-context-propagation-slice.md', 'docs/40-validation/browser-opfs-web-lock-operation-context-propagation-slice.md', 'docs/40-validation/operation-context-propagation-contract-audit-slice.md',
    'docs/40-validation/storage-lane-operation-timeout-slice.md', 'docs/40-validation/browser-opfs-web-lock-operation-timeout-boundary-slice.md',
    'docs/40-validation/browser-opfs-web-lock-read-timeout-nonpoison-slice.md', 'docs/40-validation/web-lock-read-timeout-nonpoison-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-fetch-lifecycle-slice.md', 'docs/40-validation/service-worker-fetch-lifecycle-contract-audit-slice.md', 'docs/40-validation/browser-opfs-web-lock-service-worker-update-race-slice.md', 'docs/40-validation/service-worker-update-race-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-shutdown-boundary-slice.md', 'docs/40-validation/service-worker-shutdown-boundary-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-restart-update-slice.md',
    'docs/40-validation/service-worker-restart-update-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-service-worker-lifecycle-slice.md',
    'docs/40-validation/service-worker-lifecycle-contract-audit-slice.md',
    'docs/40-validation/browser-opfs-web-lock-settled-recovery-slice.md',
    'docs/40-validation/storage-lane-web-lock-settled-recovery-slice.md',
    'docs/40-validation/browser-opfs-web-lock-tab-timeout-slice.md',
    'docs/40-validation/storage-lane-web-lock-timeout-health-slice.md',
    'docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md',
    'docs/40-validation/browser-opfs-guarded-corrupt-repair-timeout-slice.md',
    'docs/40-validation/browser-opfs-corrupt-block-repair-slice.md',
    'docs/40-validation/browser-opfs-web-lock-timeout-slice.md',
    'docs/40-validation/branch-continuity-audit-slice.md',
]:
    require_all_lower(rel, ['cross-browser', 'quota', 'eviction', 'crash'])
ok('slice docs preserve non-claims')



require_all('src/storage-lane-scheduler.mjs', ['timedOutQuarantineFingerprint', 'quarantineFingerprint', 'createTimedOutOperationQuarantineReview', 'reviewFingerprint', 'timed-out-quarantine-clear-review-fingerprint-mismatch', 'storage-lane:timed-out-quarantine-review-created'])
require_all('src/block-store-lane-adapter.mjs', ['createTimedOutOperationQuarantineReview', 'reviewFingerprint', 'requireReviewFingerprint', 'reviewManifest'])
require_all('src/types.d.ts', ['createTimedOutOperationQuarantineReview', 'reviewFingerprint', 'requireReviewFingerprint', 'reviewManifest'])
require_all('tools/storage_lane_quarantine_review_binding_probe.mjs', ['scheduler:storage-lane-quarantine-review-binding-proof', 'timed-out-quarantine-clear-review-fingerprint-required', 'timed-out-quarantine-clear-review-fingerprint-mismatch', 'tamperedLedger', 'createTimedOutOperationQuarantineReview'])
require_all('tools/browser_opfs_web_lock_quarantine_review_binding_probe.mjs', ['browser:opfs-web-lock-quarantine-review-binding-proof', 'tamperedLedger', 'missingFingerprintClear', 'staleFingerprintClear', 'reviewManifest', 'clearWithManifest'])
require_all('tools/storage_lane_quarantine_review_binding_contract_audit.mjs', ['facility:storage-lane-quarantine-review-binding-contract-audit', 'surface:storage-lane-quarantine-review-binding', 'surface:browser-opfs-web-lock-quarantine-review-binding'])
require_all('docs/40-validation/storage-lane-quarantine-review-binding-slice.md', ['quarantineFingerprint', 'reviewFingerprint', 'not cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-review-binding-slice.md', ['Managed Chromium only', 'quarantineFingerprint', 'reviewFingerprint', 'not cryptographic attestation', 'not claim rollback'])
ok('quarantine review binding hooks present')





require_all('src/storage-lane-scheduler.mjs', ['validateTimedOutOperationQuarantineClearanceReceiptRegistrationProvenance', 'quarantineClearanceReceiptProvenanceRejected', 'timed-out-quarantine-clearance-receipt-provenance-rejected', 'rejected-clearance-receipt-provenance', 'adapter-create-clearance-receipt', 'block-store-restore-clearance-receipt'])
require_all('src/block-store-lane-adapter.mjs', ['registrationProvenance', 'adapter-create-clearance-receipt', 'block-store-restore-clearance-receipt'])
require_all('tools/storage_lane_quarantine_clearance_receipt_provenance_binding_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-receipt-provenance-binding-proof', 'bareValidDirectRegister', 'mismatchedProvenanceRegister', 'rejected-clearance-receipt-provenance'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_receipt_provenance_binding_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof', 'opfsWebLockGuardedBlockStore', 'rejected-clearance-receipt-provenance'])
require_all('tools/storage_lane_quarantine_clearance_receipt_provenance_binding_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit', 'surface:storage-lane-quarantine-clearance-receipt-provenance-binding', 'surface:browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding'])
require_all('src/storage-lane-scheduler.mjs', ['clearedRowKeys', 'clearedOperationKeys', 'clearedReplayKeys', 'timed-out-quarantine-import-rejected-cleared-row', 'rejected-cleared-quarantine-row-replay', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'quarantineLedgerRowReplayRejected'])
require_all('tools/storage_lane_quarantine_clearance_row_replay_guard_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof', 'rowReplay', 'statusRewriteReplay', 'operationKey', 'rejected-cleared-quarantine-row-replay'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_row_replay_guard_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof', 'opfsWebLockGuardedBlockStore', 'statusRewriteReplay', 'rejected-cleared-quarantine-row-replay'])
require_all('tools/storage_lane_quarantine_clearance_row_replay_guard_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit', 'surface:storage-lane-quarantine-clearance-row-replay-guard', 'surface:browser-opfs-web-lock-quarantine-clearance-row-replay-guard'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-row-replay-guard-slice.md', ['clearedRowKeys', 'clearedOperationKeys', 'status-rewritten', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-row-replay-guard-slice.md', ['Managed Chromium', 'status-rewritten', 'rejected-cleared-quarantine-row-replay', 'not cross-browser'])
ok('quarantine clearance row replay guard hooks present')

require_all('src/storage-lane-scheduler.mjs', ['operationEpoch', 'operationReplayKey', 'operationEpochForExecutor', 'clearedLegacyOperationKeys', 'timed-out-quarantine-import-rejected-cleared-row-downgrade', 'rejected-cleared-quarantine-row-replay-downgrade', 'quarantineLedgerLegacyRowReplayRejected'])
require_all('src/block-store-lane-adapter.mjs', ['operationEpoch', 'operationReplayKey'])
require_all('src/types.d.ts', ['operationEpoch', 'operationReplayKey', 'rejected-cleared-quarantine-row-replay-downgrade'])
require_all('tools/storage_lane_quarantine_clearance_epoch_replay_guard_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-epoch-replay-guard-proof', 'same-opId', 'statusRewriteDowngrade', 'collisionImport', 'markUnhealthyForced'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_epoch_replay_guard_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof', 'opfsWebLockGuardedBlockStore', 'statusRewriteDowngrade', 'collisionImport', 'markUnhealthyForced'])
require_all('tools/storage_lane_quarantine_clearance_epoch_replay_guard_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit', 'surface:storage-lane-quarantine-clearance-epoch-replay-guard', 'surface:browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-epoch-replay-guard-slice.md', ['operation epoch', 'same-opId', 'downgrade replay', 'not cryptographic'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard-slice.md', ['Managed Chromium', 'operation epoch', 'same-opId', 'not cryptographic'])
ok('quarantine clearance epoch replay guard hooks present')

require_all('src/storage-lane-scheduler.mjs', ['timed-out-quarantine-clearance-receipt-lane-mismatch', 'rejected-clearance-receipt-lane-binding', 'quarantineClearanceReceiptLaneBindingRejected', 'cleared row lane'])
require_all('src/block-store-lane-adapter.mjs', ['inferClearanceReceiptLane', 'lane-wide receipts are lane-scoped', 'cleared row lane'])
require_all('tools/storage_lane_quarantine_clearance_receipt_lane_binding_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof', 'rowLaneMismatchValidation', 'wrongLaneRegister', 'rejected-clearance-receipt-lane-binding', 'markUnhealthyForced'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_receipt_lane_binding_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof', 'opfsWebLockGuardedBlockStore', 'rowLaneMismatchValidation', 'wrongLaneRegister'])
require_all('tools/storage_lane_quarantine_clearance_receipt_lane_binding_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit', 'surface:storage-lane-quarantine-clearance-receipt-lane-binding', 'surface:browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-receipt-lane-binding-slice.md', ['lane binding', 'wrong-lane', 'row lane', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding-slice.md', ['Managed Chromium', 'lane-bound', 'wrong-lane', 'cross-browser'])
ok('quarantine clearance receipt lane-binding hooks present')


require_all('src/storage-lane-scheduler.mjs', ['allowPartialImport', 'allowEmptyImport', 'filteredOutCount', 'quarantineLedgerLaneFilterRejected', 'quarantineLedgerPartialImportRejected', 'quarantineLedgerEmptyLaneFilterRejected', 'timed-out-quarantine-import-rejected-lane-filter-empty', 'timed-out-quarantine-import-rejected-lane-filter-partial', 'storage-lane:timed-out-quarantine-import-lane-filter-rejected'])
require_all('src/block-store-lane-adapter.mjs', ['allowPartialImport: options.allowPartialImport === true', 'allowEmptyImport: options.allowEmptyImport === true'])
require_all('tools/storage_lane_quarantine_lane_filter_import_guard_probe.mjs', ['scheduler:storage-lane-quarantine-lane-filter-import-guard-proof', 'rejected-lane-filter-empty-import', 'rejected-lane-filter-partial-import', 'allowPartialImport', 'markUnhealthyForced'])
require_all('tools/browser_opfs_web_lock_quarantine_lane_filter_import_guard_probe.mjs', ['browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof', 'opfsWebLockGuardedBlockStore', 'rejected-lane-filter-empty-import', 'rejected-lane-filter-partial-import', 'rejected-lane-unhealthy'])
require_all('tools/storage_lane_quarantine_lane_filter_import_guard_contract_audit.mjs', ['facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit', 'surface:storage-lane-quarantine-lane-filter-import-guard', 'surface:browser-opfs-web-lock-quarantine-lane-filter-import-guard'])
require_all('docs/40-validation/storage-lane-quarantine-lane-filter-import-guard-slice.md', ['lane-filtered import', 'wrong-lane', 'partial import', 'allowPartialImport'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-lane-filter-import-guard-slice.md', ['Managed Chromium', 'lane-filtered import', 'wrong-lane', 'cross-browser'])
ok('quarantine lane-filter import guard hooks present')


require_all('src/storage-lane-scheduler.mjs', ['lane-wide receipts are lane-scoped', 'receipt lane must be present', 'quarantineClearanceReceiptIntegrityRejected'])
require_all('src/block-store-lane-adapter.mjs', ['lane-wide receipts are lane-scoped', 'receipt lane must be present', 'createTimedOutOperationQuarantineClearanceReceipt'])
require_all('src/types.d.ts', ['rev0086', 'lane-wide timeout-quarantine clearance receipts are lane-scoped'])
require_all('tools/storage_lane_quarantine_clearance_lanewide_scope_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof', 'ambiguousLaneWideReceipt', 'lane-wide receipts are lane-scoped', 'importAfterAmbiguousReject', 'rejected-cleared-quarantine-replay'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_lanewide_scope_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof', 'opfsWebLockGuardedBlockStore', 'ambiguousLaneWideReceipt', 'lane-wide receipts are lane-scoped'])
require_all('tools/storage_lane_quarantine_clearance_lanewide_scope_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit', 'surface:storage-lane-quarantine-clearance-lanewide-scope', 'surface:browser-opfs-web-lock-quarantine-clearance-lanewide-scope'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-lanewide-scope-slice.md', ['lane-wide', 'lane-scoped', 'lane-ambiguous', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-lanewide-scope-slice.md', ['Managed Chromium', 'lane-ambiguous', 'cross-browser'])
ok('quarantine clearance lane-wide scope hooks present')


require_all('src/block-store-lane-adapter.mjs', ['quarantineClearanceReceiptRegistrationRejectedOnRestore', 'registration?.ok !== true', 'block-store-lane:quarantine-clearance-receipt-restore-rejected'])
require_all('src/types.d.ts', ['rev0086', 'restore registration gate fails closed'])
require_all('tools/storage_lane_quarantine_clearance_restore_registration_gate_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof', 'wrongLaneRestore', 'restore-storage-receipt-into-maintenance-lane', 'block-store-restore-clearance-receipt', 'rejected-cleared-quarantine-replay'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_restore_registration_gate_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof', 'opfsWebLockGuardedBlockStore', 'wrongLaneRestore', 'receiptVerifyBeforeRestore', 'block-store-restore-clearance-receipt'])
require_all('tools/storage_lane_quarantine_clearance_restore_registration_gate_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit', 'surface:storage-lane-quarantine-clearance-restore-registration-gate', 'surface:browser-opfs-web-lock-quarantine-clearance-restore-registration-gate'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-restore-registration-gate-slice.md', ['restore registration gate', 'wrong-lane restore', 'registration rejects', 'not OPFS/Web Locks'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-restore-registration-gate-slice.md', ['Managed Chromium', 'wrong-lane restore', 'profile restart', 'cross-browser'])
ok('quarantine clearance restore registration gate hooks present')

require_all('src/block-store-lane-adapter.mjs', ['verifyBeforeRestore', 'rejected-clearance-receipt-block-integrity', 'rejected-quarantine-ledger-block-integrity', 'block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected', 'quarantineClearanceReceiptRestoreBlockIntegrityRejected'])
require_all('src/types.d.ts', ['verifyBeforeRestore?: boolean', 'verifyOptions?: Record<string, unknown>', 'rejected-clearance-receipt-block-integrity'])
require_all('tools/storage_lane_quarantine_receipt_restore_integrity_probe.mjs', ['scheduler:storage-lane-quarantine-receipt-restore-integrity-proof', 'rejected-clearance-receipt-block-integrity', 'rejected-quarantine-ledger-block-integrity', 'must not call get() after failed verify'])
require_all('tools/browser_opfs_web_lock_quarantine_receipt_restore_integrity_probe.mjs', ['browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof', 'opfsWebLockGuardedBlockStore', 'storage:opfs-block-corrupt', 'rejected-clearance-receipt-block-integrity'])
require_all('tools/storage_lane_quarantine_receipt_restore_integrity_contract_audit.mjs', ['facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit', 'surface:storage-lane-quarantine-receipt-restore-integrity', 'surface:browser-opfs-web-lock-quarantine-receipt-restore-integrity'])
require_all('docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-slice.md', ['verifyBeforeRestore', 'block integrity', 'not cryptographic attestation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-receipt-restore-integrity-slice.md', ['Managed Chromium', 'rejected-clearance-receipt-block-integrity', 'cross-browser'])
require_all('docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-contract-audit-slice.md', ['contract audit', 'restore block integrity', 'browser-light'])
ok('quarantine receipt restore integrity hooks present')
require_all('src/block-store-lane-adapter.mjs', ['expectedQuarantineFingerprint', 'expectedReceiptFingerprint', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint'])
require_all('src/block-store-lane-adapter.mjs', ['blankExpectedFingerprintOption', 'timed-out-quarantine-restore-expected-fingerprint-blank', 'timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-blank'])
require_all('tools/lib/quarantine_restore_expected_fingerprint_harness.mjs', ['assertExpectedFingerprintRestoreReport', 'blank expected quarantine/receipt fingerprint intent rejects', 'EXPECTED_FINGERPRINT_RESTORE_CLAIMS'])
require_all('tools/current_office_audit.mjs', ['facility:current-office-command-surface-audit', 'historical-current-aliases-renamed-to-replay', 'manifest-output-prefixes-current'])
require_all('tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs', ['scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof', 'blankLedgerRestore', 'blankReceiptRestore', 'assertExpectedFingerprintRestoreReport', 'EXPECTED_FINGERPRINT_RESTORE_CLAIMS'])
require_all('tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs', ['browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof', 'blankLedgerRestore', 'expectedQuarantineFingerprint', 'expectedReceiptFingerprint', 'guarded OPFS write verifies'])
require_all('tools/storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs', ['facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit', 'blank expected-fingerprint', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint'])
require_all('docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-slice.md', ['expected fingerprint', 'valid-but-wrong', 'not cryptographic attestation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-restore-expected-fingerprint-slice.md', ['Managed Chromium', 'expected-fingerprint', 'cross-browser'])
require_all('docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-contract-audit-slice.md', ['contract audit', 'expected-fingerprint', 'browser proof'])
ok('quarantine restore expected-fingerprint hooks present')

require_all('src/storage-lane-scheduler.mjs', ['statusTransitionReplacementCount', 'quarantineLedgerStatusTransitionReplacements', 'storage-lane:timed-out-quarantine-import-status-transition-replaced', 'removeExistingTimedOutRow'])
require_all('tools/storage_lane_quarantine_status_transition_import_probe.mjs', ['scheduler:storage-lane-quarantine-status-transition-import-proof', 'importFailed.statusTransitionReplacementCount', 'successful -> failed -> unsettled -> successful', 'staleReplay.disposition'])
require_all('tools/browser_opfs_web_lock_quarantine_status_transition_import_probe.mjs', ['browser:opfs-web-lock-quarantine-status-transition-import-proof', 'opfsWebLockGuardedBlockStore', 'statusTransitionReplacementCount', 'guard.put'])
require_all('tools/storage_lane_quarantine_status_transition_import_contract_audit.mjs', ['facility:storage-lane-quarantine-status-transition-import-contract-audit', 'surface:storage-lane-quarantine-status-transition-import', 'surface:browser-opfs-web-lock-quarantine-status-transition-import'])
require_all('docs/40-validation/storage-lane-quarantine-status-transition-import-slice.md', ['operationReplayKey', 'status transition', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-status-transition-import-slice.md', ['Managed Chromium', 'status-transition', 'cross-browser'])
require_all('docs/40-validation/storage-lane-quarantine-status-transition-import-contract-audit-slice.md', ['contract audit', 'status-transition import', 'operationReplayKey'])
ok('quarantine status-transition import hooks present')

require_all('src/storage-lane-scheduler.mjs', ['operationReplayKeys must match cleared row operationReplayKeys', 'cleared row operationReplayKey mismatch', 'quarantineClearanceReceiptReplayKeyBindingRejected'])
require_all('src/block-store-lane-adapter.mjs', ['operationReplayKeys must match cleared row operationReplayKeys', 'cleared row operationReplayKey mismatch', 'clearanceRowsOperationReplayKeys'])
require_all('tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof', 'missing operationReplayKeys', 'extra operationReplayKeys', 'cleared row operationReplayKey mismatch'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_replay_key_receipt_integrity_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof', 'opfsWebLockGuardedBlockStore', 'operationReplayKeys must match cleared row operationReplayKeys'])
require_all('tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit', 'surface:storage-lane-quarantine-clearance-replay-key-receipt-integrity'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-slice.md', ['operationReplayKeys', 'clearance receipt', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-slice.md', ['Managed Chromium', 'operationReplayKeys', 'cross-browser'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit-slice.md', ['contract audit', 'operationReplayKeys', 'current slice'])
ok('quarantine clearance replay-key receipt integrity hooks present')

require_all('src/storage-lane-scheduler.mjs', ['importedTimedOutReplayCandidates', 'clearanceReceiptReplayMatches', '#findClearanceReceiptForQuarantineFingerprint(quarantineFingerprint, imported', 'matchedRows: clearanceReceipt.matchedRows'])
require_all('tools/storage_lane_quarantine_partial_clearance_replay_scope_probe.mjs', ['scheduler:storage-lane-quarantine-partial-clearance-replay-scope-proof', 'partialClear', 'exactAfterPartial', 'unclearedImport', 'forgedFullCountReceipt', 'rejected-cleared-quarantine-row-replay', 'rejected-cleared-quarantine-replay'])
require_all('tools/browser_opfs_web_lock_quarantine_partial_clearance_replay_scope_probe.mjs', ['browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof', 'opfsWebLockGuardedBlockStore', 'partialClear', 'exactAfterPartial', 'unclearedImport'])
require_all('tools/storage_lane_quarantine_partial_clearance_replay_scope_contract_audit.mjs', ['facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit', 'surface:storage-lane-quarantine-partial-clearance-replay-scope', 'surface:browser-opfs-web-lock-quarantine-partial-clearance-replay-scope'])
require_all('docs/40-validation/storage-lane-quarantine-partial-clearance-replay-scope-slice.md', ['partial clearance', 'uncleared row', 'full-fingerprint', 'row coverage'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-partial-clearance-replay-scope-slice.md', ['Managed Chromium', 'partial clearance', 'uncleared row', 'cross-browser'])
ok('quarantine partial clearance replay scope hooks present')


require_all('src/storage-lane-scheduler.mjs', ['Lane-wide clearance receipts are still lane-scoped', 'laneFilter == null || row.lane === laneFilter', 'receipt.lane == null || !laneSet.has(receipt.lane)'])
require_all('tools/storage_lane_quarantine_clearance_lanewide_query_scope_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-lanewide-query-scope-proof', 'storageReceiptFromStorageQuery', 'maintenanceReceiptFromMaintenanceQuery', 'storageReceiptFromMaintenanceQuery', 'importAfterWrongLaneRegistration'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_lanewide_query_scope_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof', 'opfsWebLockGuardedBlockStore', 'storageReceiptFromMaintenanceQuery', 'importAfterWrongLaneRegistration'])
require_all('tools/storage_lane_quarantine_clearance_lanewide_query_scope_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit', 'surface:storage-lane-quarantine-clearance-lanewide-query-scope', 'surface:browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-lanewide-query-scope-slice.md', ['lane-wide', 'query', 'lane-scoped', 'wrong-lane'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope-slice.md', ['Managed Chromium', 'lane-wide', 'query', 'cross-browser'])
ok('quarantine clearance lane-wide query scope hooks present')

require_all('src/block-store-lane-adapter.mjs', ['validateTimedOutOperationQuarantineClearanceReceipt', 'opIds must match cleared row opIds', 'preClearanceFingerprint must match reviewFingerprint'])
require_all('tools/storage_lane_quarantine_noop_clearance_receipt_guard_probe.mjs', ['scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof', 'timed-out-quarantine-clear-noop', 'zeroReceiptValidation', 'rejected-cleared-quarantine-replay'])
require_all('tools/browser_opfs_web_lock_quarantine_noop_clearance_receipt_guard_probe.mjs', ['browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof', 'opfsWebLockGuardedBlockStore', 'timed-out-quarantine-clear-noop', 'zeroReceiptValidation'])
require_all('docs/40-validation/storage-lane-quarantine-noop-clearance-receipt-guard-slice.md', ['zero-row', 'clearance receipt', 'timed-out-quarantine-clear-noop', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-slice.md', ['Managed Chromium', 'zero-row', 'timed-out-quarantine-clear-noop', 'not a cross-browser'])
ok('quarantine no-op clearance receipt guard hooks present')

require_all('src/storage-lane-scheduler.mjs', ['registerTimedOutOperationQuarantineClearanceReceipt', 'clearedTimedOutOperationQuarantineClearanceReceipts', 'timed-out-quarantine-import-rejected-cleared', 'rejected-cleared-quarantine-replay', 'storage-lane:timed-out-quarantine-import-replay-rejected'])
require_all('src/block-store-lane-adapter.mjs', ['createTimedOutOperationQuarantineClearanceReceipt', 'persistTimedOutOperationQuarantineClearanceReceipt', 'restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore', 'clearedTimedOutOperationQuarantineClearanceReceipts'])
require_all('src/browserrt.mjs', ['createTimedOutOperationQuarantineClearanceReceipt', 'validateTimedOutOperationQuarantineClearanceReceipt', 'timedOutOperationQuarantineClearanceReceiptFingerprint'])
require_all('src/types.d.ts', ['QuarantineClearanceReceipt', 'restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore', 'rejected-cleared-quarantine-replay'])
require_all('tools/storage_lane_quarantine_clearance_replay_guard_probe.mjs', ['scheduler:storage-lane-quarantine-clearance-replay-guard-proof', 'rejected-cleared-quarantine-replay', 'persistTimedOutOperationQuarantineClearanceReceipt', 'restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore'])
require_all('tools/browser_opfs_web_lock_quarantine_clearance_replay_guard_probe.mjs', ['browser:opfs-web-lock-quarantine-clearance-replay-guard-proof', 'opfsWebLockGuardedBlockStore', 'rejected-cleared-quarantine-replay', 'same profile'])
require_all('tools/storage_lane_quarantine_clearance_replay_guard_contract_audit.mjs', ['facility:storage-lane-quarantine-clearance-replay-guard-contract-audit', 'surface:storage-lane-quarantine-clearance-replay-guard', 'surface:browser-opfs-web-lock-quarantine-clearance-replay-guard'])
require_all('docs/40-validation/storage-lane-quarantine-clearance-replay-guard-slice.md', ['clearance receipt', 'stale', 'replay', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-guard-slice.md', ['Managed Chromium', 'same profile', 'rejected-cleared-quarantine-replay', 'not cross-browser'])
require_all('src/block-store-lane-adapter.mjs', ['clearance receipt requires at least one cleared timed-out quarantine row', 'receipt must clear at least one timed-out quarantine row'])
ok('quarantine clearance replay guard hooks present')

require_all('src/storage-lane-scheduler.mjs', ['finalizeUnsettledTimedOutOperations', 'timed-out-quarantine-finalize-review-fingerprint-required', 'timed-out-quarantine-finalize-review-fingerprint-mismatch', 'storage-lane:timed-out-quarantine-orphans-finalized', 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED'])
require_all('src/block-store-lane-adapter.mjs', ['finalizeUnsettledTimedOutOperations(options = {})', 'quarantineOrphanFinalizations', 'block-store-lane:recover-timed-out-ops-blocked'])
require_all('src/types.d.ts', ['finalizeUnsettledTimedOutOperations', 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED', 'reviewFingerprint'])
require_all('tools/storage_lane_unsettled_orphan_review_probe.mjs', ['scheduler:storage-lane-unsettled-orphan-review-proof', 'timed-out-operation-still-unsettled', 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED', 'staleFinalize'])
require_all('tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs', ['browser:opfs-web-lock-unsettled-orphan-review-proof', 'opfsWebLockGuardedBlockStore', 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED', 'reviewManifest'])
require_all('tools/storage_lane_unsettled_orphan_review_contract_audit.mjs', ['facility:storage-lane-unsettled-orphan-review-contract-audit', 'surface:storage-lane-unsettled-orphan-review', 'surface:browser-opfs-web-lock-unsettled-orphan-review'])
require_all('docs/40-validation/storage-lane-unsettled-orphan-review-slice.md', ['unsettled', 'orphan', 'reviewFingerprint', 'not cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md', ['Managed Chromium', 'real OPFS', 'real Web Locks', 'not cross-browser'])
ok('unsettled orphan review hooks present')

require_all('src/storage-lane-scheduler.mjs', ['late-success-clear-review-fingerprint-required', 'late-success-clear-review-fingerprint-mismatch', 'late-failure-clear-review-fingerprint-required', 'late-failure-clear-review-fingerprint-mismatch', 'storage-lane:late-provider-success-clear-rejected', 'storage-lane:late-provider-failure-clear-rejected'])
require_all('src/block-store-lane-adapter.mjs', ['clearSuccessfulTimedOutOperations(options = {})', 'clearFailedTimedOutOperations(options = {})', 'reviewManifest: options.reviewManifest', 'requireReviewFingerprint: options.requireReviewFingerprint !== false'])
require_all('tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs', ['scheduler:storage-lane-quarantine-legacy-clear-binding-proof', 'late-success-clear-review-fingerprint-required', 'late-failure-clear-review-fingerprint-required', 'staleOldSuccessReviewOnFailure', 'reviewManifest'])
require_all('tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs', ['browser:opfs-web-lock-quarantine-legacy-clear-binding-proof', 'opfsWebLockGuardedBlockStore', 'late-success-clear-review-fingerprint-required', 'late-failure-clear-review-fingerprint-required'])
require_all('tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs', ['facility:storage-lane-quarantine-legacy-clear-binding-contract-audit', 'surface:storage-lane-quarantine-legacy-clear-binding', 'surface:browser-opfs-web-lock-quarantine-legacy-clear-binding'])
require_all('docs/40-validation/storage-lane-quarantine-legacy-clear-binding-slice.md', ['legacy clear helpers', 'review-fingerprint', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-legacy-clear-binding-slice.md', ['Managed Chromium', 'real OPFS', 'real Web Locks', 'not cross-browser'])
ok('quarantine legacy clear binding hooks present')

require_all('src/storage-lane-scheduler.mjs', ['exportTimedOutOperationQuarantine', 'importTimedOutOperationQuarantine', 'brt.storageLane.timedOutOperationQuarantine.v1', 'storage-lane:timed-out-quarantine-import', 'timed-out-quarantine-clear-review-token-required'])
require_all('src/block-store-lane-adapter.mjs', ['exportTimedOutOperationQuarantine', 'importTimedOutOperationQuarantine', 'clearTimedOutOperationQuarantine', 'timedOutOperationQuarantine'])
require_all('src/block-store-lane-adapter.mjs', ['persistTimedOutOperationQuarantine', 'restoreTimedOutOperationQuarantineFromBlockStore', 'block-store-lane:quarantine-ledger-persisted', 'block-store-lane:quarantine-ledger-restore-rejected'])
require_all('tools/storage_lane_quarantine_ledger_persistence_integrity_probe.mjs', ['scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof', 'malformed persisted ledger restore is rejected atomically', 'restoreTimedOutOperationQuarantineFromBlockStore'])
require_all('tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs', ['browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof', 'malformedRestore', 'same-profile browser restart'])
require_all('tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs', ['facility:storage-lane-quarantine-ledger-persistence-integrity-contract-audit', 'surface:storage-lane-quarantine-ledger-persistence'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-integrity-slice.md', ['managed Chromium', 'malformed', 'cross-browser'])
require_all('tools/storage_lane_quarantine_ledger_persistence_integrity_probe.mjs', ['scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof', 'persistTimedOutOperationQuarantine', 'restoreTimedOutOperationQuarantineFromBlockStore', 'block-store-lane:quarantine-ledger-persisted'])
require_all('tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs', ['browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof', 'runManagedBrowserPage', 'keepProfile: true', 'restoreTimedOutOperationQuarantineFromBlockStore'])
require_all('tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs', ['facility:storage-lane-quarantine-ledger-persistence-integrity-contract-audit', 'surface:storage-lane-quarantine-ledger-persistence'])
require_all('docs/40-validation/storage-lane-quarantine-ledger-persistence-integrity-slice.md', ['persistTimedOutOperationQuarantine', 'restoreTimedOutOperationQuarantineFromBlockStore', 'not cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-integrity-slice.md', ['Managed Chromium', 'same profile', 'cross-browser'])
require_all('tools/storage_lane_quarantine_ledger_roundtrip_probe.mjs', ['scheduler:storage-lane-quarantine-ledger-roundtrip-proof', 'timed-out-quarantine-clear-review-token-required', 'storage-lane:timed-out-quarantine-import'])
require_all('tools/browser_opfs_web_lock_quarantine_ledger_roundtrip_probe.mjs', ['browser:opfs-web-lock-quarantine-ledger-roundtrip-proof', 'real OPFS/Web Lock', 'timed-out-quarantine-clear-review-token-required'])
require_all('tools/storage_lane_quarantine_ledger_contract_audit.mjs', ['facility:storage-lane-quarantine-ledger-contract-audit', 'surface:storage-lane-quarantine-ledger-roundtrip'])
require_all('docs/40-validation/storage-lane-quarantine-ledger-roundtrip-slice.md', ['brt.storageLane.timedOutOperationQuarantine.v1', 'review token', 'not prove'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-roundtrip-slice.md', ['Managed Chromium', 'cross-browser', 'not prove'])
ok('quarantine ledger roundtrip hooks present')

require_all('src/storage-lane-scheduler.mjs', ['BRT_STORAGE_OPERATION_TIMEOUT', 'operationTimeoutMs', 'storage-lane:operation-timeout', 'isReadOnlyWebLockTimeout', 'READ_ONLY_WEB_LOCK_OPS', 'unsettledTimedOutOperations', 'waitForTimedOutOperationsSettled', 'storage-lane:late-provider-settlement'])
require_all('src/block-store-lane-adapter.mjs', ['defaultOperationTimeoutMs', 'operationTimeoutMs', 'recoverWhenStoreSettled', 'requireTimedOutOperationsSettled', 'timed-out-operation-still-unsettled'])
require_all('tools/storage_lane_late_settlement_recovery_gate_probe.mjs', ['scheduler:storage-lane-late-settlement-recovery-gate-proof', 'timed-out-operation-still-unsettled', 'storage-lane:late-provider-settlement', 'adapterResultAfterLateSettlement'])
require_all('tools/browser_opfs_web_lock_late_settlement_recovery_gate_probe.mjs', ['browser:opfs-web-lock-late-settlement-recovery-gate-proof', 'locksAfterTimeout', 'timeoutBlockPresentBeforeRelease', 'adapterResultAfterLateSettlement'])
require_all('tools/storage_lane_late_settlement_contract_audit.mjs', ['facility:storage-lane-late-settlement-contract-audit', 'surface:storage-lane-late-settlement-recovery-gate'])
require_all('tools/storage_lane_operation_timeout_probe.mjs', ['scheduler:storage-lane-operation-timeout-proof', 'BRT_STORAGE_OPERATION_TIMEOUT', 'not provider cancellation'])
require_all('tools/browser_opfs_web_lock_operation_timeout_probe.mjs', ['browser:opfs-web-lock-operation-timeout-boundary-proof', 'BRT_STORAGE_OPERATION_TIMEOUT', 'providerWroteBeforeTimeout', 'blockedRecovery'])
require_all('tools/storage_lane_operation_timeout_contract_audit.mjs', ['facility:storage-lane-operation-timeout-contract-audit', 'surface:storage-lane-operation-timeout'])
require_all('tools/storage_lane_web_lock_read_timeout_nonpoison_probe.mjs', ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof', 'read-only Web Lock timeout', 'laneHealthFailures'])
require_all('tools/browser_opfs_web_lock_read_timeout_nonpoison_probe.mjs', ['browser:opfs-web-lock-read-timeout-nonpoison-proof', 'BRT_WEB_LOCK_TIMEOUT', 'finalLocks'])
require_all('tools/web_lock_read_timeout_nonpoison_contract_audit.mjs', ['facility:web-lock-read-timeout-nonpoison-contract-audit', 'surface:web-lock-read-timeout-nonpoison-contract-audit'])
require_all('src/web-lock-coordinator.mjs', ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED', 'defaultTimeoutMs', 'coord:web-lock-timeout', 'queryLocks', 'waitForSettled'])
require_all('src/opfs-web-lock-guarded-block-store.mjs', ['WebLockGuardedBlockStore', 'lockTimeoutMs', 'queryLocks(', 'waitForSettled(', 'storage:opfs-web-lock-guard-op-error', 'storage:opfs-web-lock-guard-settled'])
require_all('src/block-store-lane-adapter.mjs', ['recoverWhenStoreSettled', 'block-store-lane:recover-settled', 'block-store-lane:recover-settled-blocked', 'store-coordination-still-contended', 'exportTimedOutOperationQuarantine', 'importTimedOutOperationQuarantine', 'timedOutOperationQuarantine'])
require_all('src/opfs-block-store.mjs', ['verifyExistingBlocksOnPut', 'verifyAfterWrite', 'verifyOnHas', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'storage:opfs-block-repair'])
require_all('src/storage-lane-scheduler.mjs', ['isStorageHealthFailure', 'BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCKS_UNAVAILABLE', 'storage-lane:provider-unhealthy', 'exportTimedOutOperationQuarantine', 'importTimedOutOperationQuarantine', 'timed-out-operation-quarantine-imported', 'rejected-timed-out-operation-quarantine'])
require_all('tools/browser_cdp_fixture.mjs', ['connectBrowserCdp', 'openPageTarget', 'closePageTarget', 'closeServiceWorkerTargets', 'routes = {}', 'routeEntries', 'Target.createTarget', 'Target.closeTarget', 'Target.getTargets', 'Storage.getUsageAndQuota', 'killProcessGroup'])
require_all('tools/browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs', ['browser:opfs-web-lock-service-worker-fetch-lifecycle-proof', 'SW_ROUTE', 'browserrt-sw-fetch-lifecycle', 'fetch(', 'BRT_WEB_LOCK_TIMEOUT', 'blockedRecovery', 'holderVerify', 'timeoutPresent', 'settledRecovery', 'reapBrowserProfileProcesses'])
require_all('tools/service_worker_fetch_lifecycle_contract_audit.mjs', ['facility:service-worker-fetch-lifecycle-contract-audit', 'surface:browser-opfs-web-lock-service-worker-fetch-lifecycle', 'surface:service-worker-fetch-lifecycle-contract-audit'])
require_all('tools/browserrt_opfs_web_lock_service_worker_holder.mjs', ['handleFetchLifecycleRequest', "self.addEventListener('fetch'", 'event.respondWith', 'browserrt-sw-fetch-lifecycle', 'handleSkipWaiting'])
require_all('tools/browser_opfs_web_lock_service_worker_update_race_probe.mjs', ['browser:opfs-web-lock-service-worker-update-race-proof', 'SW_V1_ROUTE', 'SW_V2_ROUTE', "updateViaCache: 'none'", 'BRT_WEB_LOCK_TIMEOUT', 'blockedRecovery', 'v2Version', 'timeoutPresent', 'settledRecovery'])
require_all('tools/service_worker_update_race_contract_audit.mjs', ['facility:service-worker-update-race-contract-audit', 'surface:browser-opfs-web-lock-service-worker-update-race', 'surface:service-worker-update-race-contract-audit'])
require_all('tools/browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs', ['browser:opfs-web-lock-service-worker-shutdown-boundary-proof', 'SW_ROUTE', "updateViaCache: 'none'", "cmd: 'hold'", 'BRT_WEB_LOCK_TIMEOUT', "teardownMode: 'kill'", 'lockQueryAtRestart', 'holderVerify', 'timeoutPresent', 'reapBrowserProfileProcesses'])
require_all('tools/service_worker_shutdown_boundary_contract_audit.mjs', ['facility:service-worker-shutdown-boundary-contract-audit', 'surface:browser-opfs-web-lock-service-worker-shutdown-boundary', 'surface:service-worker-shutdown-boundary-contract-audit'])
require_all('tools/browser_opfs_web_lock_service_worker_restart_update_probe.mjs', ['browser:opfs-web-lock-service-worker-restart-update-proof', 'startProbeServer', 'profileDir', 'keepProfile: true', 'SW_V1_ROUTE', 'SW_V2_ROUTE', "updateViaCache: 'none'", 'versionedWorkerSource', 'reapBrowserProfileProcesses', 'registrationsBefore', 'registrationsAfterUpdate'])
require_all('tools/service_worker_restart_update_contract_audit.mjs', ['facility:service-worker-restart-update-contract-audit', 'surface:browser-opfs-web-lock-service-worker-restart-update', 'surface:service-worker-restart-update-contract-audit'])
require_all('tools/browser_opfs_web_lock_service_worker_lifecycle_probe.mjs', ['browser:opfs-web-lock-service-worker-lifecycle-proof', 'serviceWorker.register', 'closeServiceWorkerTargets', 'BRT_WEB_LOCK_TIMEOUT', 'recoverWhenStoreSettled', 'lockQueryWhilePending', 'timeoutPresent', 'holderVerify', 'recoveredVerify'])
require_all('tools/browserrt_opfs_web_lock_service_worker_holder.mjs', ['createOpfsAsyncBlockStore', 'createWebLockGuardedBlockStore', "cmd === 'hold'", "cmd === 'put-once'", "cmd === 'release'", 'BRT_SW_VERSION', 'workerIdentity'])
require_all('tools/service_worker_lifecycle_contract_audit.mjs', ['facility:service-worker-lifecycle-contract-audit', 'surface:browser-opfs-web-lock-service-worker-lifecycle', 'surface:service-worker-lifecycle-contract-audit'])
require_all('tools/browser_opfs_web_lock_settled_recovery_probe.mjs', ['browser:opfs-web-lock-settled-recovery-proof', 'recoverWhenStoreSettled', 'BRT_WEB_LOCK_TIMEOUT', 'lockQueryWhilePending', 'closePageTarget'])
require_all('tools/storage_lane_web_lock_settled_recovery_probe.mjs', ['storage-lane-web-lock-settled-recovery-proof', 'recoverWhenStoreSettled', 'BRT_WEB_LOCK_TIMEOUT', 'store-coordination-still-contended'])
require_all('tools/web_lock_settled_recovery_contract_audit.mjs', ['facility:web-lock-settled-recovery-contract-audit', 'surface:browser-opfs-web-lock-settled-recovery', 'surface:storage-lane-web-lock-settled-recovery'])
require_all('tools/browser_opfs_web_lock_tab_timeout_probe.mjs', ['browser:opfs-web-lock-tab-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'holderStillHeldAfterTimeout', 'timeoutPresent', 'lockQueryWhilePending', 'closePageTarget'])
require_all('tools/storage_lane_web_lock_timeout_health_probe.mjs', ['storage-lane-web-lock-timeout-health-proof', 'BRT_WEB_LOCK_TIMEOUT', 'rejected-lane-unhealthy', 'maintenance fallback'])
require_all('tools/browser_opfs_guarded_corrupt_repair_timeout_probe.mjs', ['browser:opfs-guarded-corrupt-repair-timeout-proof', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'BRT_WEB_LOCK_TIMEOUT', 'corruptRepairs'])
require_all('tools/revision_lineage_merge_audit.mjs', ['parallel rev0061', 'corrupt-block repair', 'Web Lock timeout', 'tab-timeout', 'tab-termination'])
require_all('tools/branch_continuity_audit.mjs', ['corrupt-block repair', 'Web Lock timeout', 'tab-termination', 'storage-lane'])
require_all('src/types.d.ts', [f"revision: '{REV}'", f"version: '{VERSION}'", 'lockTimeoutMs', 'queryLocks', 'waitForSettled', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'BRT_WEB_LOCK_TIMEOUT', 'operationTimeoutMs', 'failedTimedOutOperations', 'clearFailedTimedOutOperations', 'successfulTimedOutOperations', 'clearSuccessfulTimedOutOperations', 'timed-out-operation-late-success', 'late-success-clear-review-required', 'late-success-clear-scope-required', 'requireNoFailedTimedOutOperations', 'exportTimedOutOperationQuarantine', 'importTimedOutOperationQuarantine', 'rejected-timed-out-operation-quarantine'])
if 'rev0039' in text('src/types.d.ts'):
    fail('src/types.d.ts still carries stale rev0039 declarations')
ok('runtime/refactor hooks present')

require_all('tools/storage_lane_late_failure_quarantine_probe.mjs', ['scheduler:storage-lane-late-failure-quarantine-proof', 'timed-out-operation-late-failure', 'clearFailedTimedOutOperations', 'late failure must not publish a successful adapter result'])
require_all('tools/browser_opfs_web_lock_late_failure_quarantine_probe.mjs', ['browser:opfs-web-lock-late-failure-quarantine-proof', 'BRT_OPFS_OPERATION_FAILED', 'timeoutVerifyAfterLateFailure', 'storage-lane:late-provider-failure'])
require_all('tools/storage_lane_late_failure_quarantine_contract_audit.mjs', ['facility:storage-lane-late-failure-quarantine-contract-audit', 'surface:storage-lane-late-failure-quarantine', 'surface:browser-opfs-web-lock-late-failure-quarantine'])
require_all('docs/40-validation/storage-lane-late-failure-quarantine-slice.md', ['timed-out-operation-late-failure', 'clearFailedTimedOutOperations', 'not cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md', ['Managed Chromium', 'not prove cross-browser', 'not prove cancellation'])
ok('late-failure quarantine hooks present')

require_all('tools/storage_lane_late_success_quarantine_probe.mjs', ['scheduler:storage-lane-late-success-quarantine-proof', 'timed-out-operation-late-success', 'clearSuccessfulTimedOutOperations', 'unreviewedClearRejected', 'unscopedClearRejected', 'late provider success must not retroactively publish success'])
require_all('tools/browser_opfs_web_lock_late_success_quarantine_probe.mjs', ['browser:opfs-web-lock-late-success-quarantine-proof', 'timeoutVerifyAfterLateSuccess', 'storage-lane:late-provider-success', 'timed-out-operation-late-success'])
require_all('tools/storage_lane_late_success_quarantine_contract_audit.mjs', ['facility:storage-lane-late-success-quarantine-contract-audit', 'surface:storage-lane-late-success-quarantine', 'surface:browser-opfs-web-lock-late-success-quarantine'])
require_all('docs/40-validation/storage-lane-late-success-quarantine-slice.md', ['timed-out-operation-late-success', 'clearSuccessfulTimedOutOperations', 'late-success-clear-review-required', 'not provider cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-late-success-quarantine-slice.md', ['Managed Chromium', 'not cross-browser', 'not cancellation'])
ok('late-success quarantine hooks present')

require_all('tools/storage_lane_multi_failure_quarantine_probe.mjs', ['scheduler:storage-lane-multi-failure-quarantine-proof', 'late-failure-clear-review-required', 'late-failure-clear-scope-required', 'both failed timed-out operations'])
require_all('tools/browser_opfs_web_lock_multi_failure_quarantine_probe.mjs', ['browser:opfs-web-lock-multi-failure-quarantine-proof', 'providerCommittedBeforeRelease', 'timedOutVerifiesAfterLateFailures', 'remainingAfterRejectedClears'])
require_all('tools/storage_lane_multi_failure_quarantine_contract_audit.mjs', ['facility:storage-lane-multi-failure-quarantine-contract-audit', 'surface:storage-lane-multi-failure-quarantine', 'surface:browser-opfs-web-lock-multi-failure-quarantine'])
require_all('docs/40-validation/storage-lane-multi-failure-quarantine-slice.md', ['reviewed', 'scoped', 'not cancellation'])
require_all('docs/40-validation/browser-opfs-web-lock-multi-failure-quarantine-slice.md', ['Managed Chromium', 'not prove cross-browser', 'not prove rollback'])
ok('multi-failure quarantine hooks present')


require_all('tools/storage_lane_quarantine_handoff_probe.mjs', ['scheduler:storage-lane-quarantine-handoff-proof', 'timed-out-operation-quarantine-imported', 'direct markHealthy', 'late success and late failure'])
require_all('tools/browser_opfs_web_lock_quarantine_handoff_probe.mjs', ['browser:opfs-web-lock-quarantine-handoff-proof', 'Managed Chromium proof', 'real OPFS/Web Lock', 'imported quarantine'])
require_all('tools/storage_lane_quarantine_handoff_contract_audit.mjs', ['facility:storage-lane-quarantine-handoff-contract-audit', 'surface:storage-lane-quarantine-handoff', 'surface:browser-opfs-web-lock-quarantine-handoff'])
require_all('docs/40-validation/storage-lane-quarantine-handoff-slice.md', ['reviewed/scoped', 'not cancellation', 'not rollback'])
require_all('docs/40-validation/browser-opfs-web-lock-quarantine-handoff-slice.md', ['Managed Chromium', 'not prove cross-browser', 'not cancellation'])
ok('quarantine handoff hooks present')

require_all('src/web-lock-coordinator.mjs', ['BRT_WEB_LOCK_OPTION_TYPE', 'BRT_WEB_LOCK_OPTION_CONFLICT', 'BRT_WEB_LOCK_SIGNAL_INVALID', 'coord:web-lock-option-rejected', 'cleanOptionalBooleanOption', 'validateLockOptionCombinations'])
require_all('tools/web_lock_strict_option_guard_probe.mjs', ['coord:web-lock-strict-option-guard-proof', 'ifAvailable-string-false', 'steal-string-false', 'ifAvailable-plus-steal', 'plain-object-signal', 'optionRejected'])
require_all('tools/browser_opfs_web_lock_strict_option_guard_probe.mjs', ['browser:opfs-web-lock-strict-option-guard-proof', 'navigator.locks?.request', 'opfsWebLockGuardedBlockStore', 'plain-object-signal', 'storage:opfs-block-put'])
require_all('tools/web_lock_strict_option_guard_contract_audit.mjs', ['facility:web-lock-strict-option-guard-contract-audit', 'surface:web-lock-strict-option-guard', 'runtime-no-boolean-string-coercion'])
require_all_lower('docs/40-validation/web-lock-strict-option-guard-slice.md', ['cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/browser-opfs-web-lock-strict-option-guard-slice.md', ['cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/web-lock-strict-option-guard-contract-audit-slice.md', ['cross-browser', 'quota', 'eviction', 'crash'])
ok('web-lock strict option guard hooks present')


require_all('src/opfs-block-store.mjs', ['abortSignalFromOptions', 'BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'storage:opfs-block-abort', 'storage:opfs-block-abort-signal-invalid', 'async put(value, fields = {}, options = {})', 'storage:opfs-block-put-rollback'])
require_all('src/types.d.ts', ['BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'RtOpfsOperationOptions', 'signal?: AbortSignal | null', 'abortSignal?: AbortSignal | null'])
require_all('tools/lib/fake_opfs_harness.mjs', ['FakeDirectoryHandle', 'FakeFileHandle', 'withFakeNavigator', 'fakeTreeSummary', 'onBeforeClose', 'onAbort'])
require_all('tools/opfs_block_store_corrupt_block_repair_probe.mjs', ["from './lib/fake_opfs_harness.mjs'", 'withFakeNavigator', 'writeFakePath'])
require_all('tools/opfs_block_store_abort_signal_probe.mjs', ['opfs:block-store-abort-signal-proof', 'pre-aborted-put', 'invalid-signal-put', 'mid-write-abort-onWrite', 'mid-write-abort-onBeforeClose', 'BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'storage-lane operation timeouts'])
require_all('tools/browser_opfs_block_store_abort_signal_probe.mjs', ['browser:opfs-block-store-abort-signal-proof', 'raw-pre-aborted-put', 'raw-invalid-signal-put', 'raw-pre-aborted-get', 'snapshotAfterRejectedPrePut.opened', 'guarded null-signal OPFS put'])
require_all('tools/opfs_block_store_abort_signal_contract_audit.mjs', ['facility:opfs-block-store-abort-signal-contract-audit', 'surface:opfs-block-store-abort-signal', 'fake-opfs-harness:shared-refactor'])
require_all_lower('docs/40-validation/opfs-block-store-abort-signal-slice.md', ['abortsignal', 'cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/browser-opfs-block-store-abort-signal-slice.md', ['managed chromium', 'abortsignal', 'cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/opfs-block-store-abort-signal-contract-audit-slice.md', ['audit', 'cross-browser', 'quota', 'eviction', 'crash'])
ok('opfs block-store abort signal guard hooks present')


require_all('src/opfs-block-store.mjs', ['writeBudgetGuard', 'normalizeWriteBudgetGuard', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_WRITE_BUDGET_INVALID', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'storage:opfs-block-write-budget-check', 'storage:opfs-block-write-budget-reject', 'navigator.storage.estimate'])
require_all('src/types.d.ts', ['RtOpfsWriteBudgetGuard', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_WRITE_BUDGET_INVALID', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'minFreeBytesForPut', 'maxUsageRatioForPut', 'requireStorageEstimateForPut'])
require_all('src/browserrt.mjs', ['opfsWriteBudgetGuardProof'])
require_all('tools/lib/fake_opfs_harness.mjs', ['estimate = null', 'storageExtras', 'navigator.storage.estimate'])
require_all('tools/opfs_block_store_write_budget_guard_probe.mjs', ['opfs:block-store-write-budget-guard-proof', 'reserve-budget-reject-before-open', 'per-put-ratio-budget-reject-before-open', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'BRT_OPFS_WRITE_BUDGET_INVALID'])
require_all('tools/browser_opfs_block_store_write_budget_guard_probe.mjs', ['browser:opfs-block-store-write-budget-guard-proof', 'navigator.storage.estimate', 'raw-write-budget-reject-before-open', 'raw-per-put-write-budget-reject-before-open', 'opfsWebLockGuardedBlockStore', 'locksAfterGuarded'])
require_all('tools/opfs_block_store_write_budget_guard_contract_audit.mjs', ['facility:opfs-block-store-write-budget-guard-contract-audit', 'surface:opfs-block-store-write-budget-guard', 'fake-opfs-harness:storage-estimate-refactor'])
require_all_lower('docs/40-validation/opfs-block-store-write-budget-guard-slice.md', ['writebudgetguard', 'storagemanager.estimate', 'reservation', 'cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/browser-opfs-block-store-write-budget-guard-slice.md', ['managed chromium', 'navigator.storage.estimate', 'cross-browser', 'quota', 'eviction', 'crash'])
require_all_lower('docs/40-validation/opfs-block-store-write-budget-guard-contract-audit-slice.md', ['audit', 'writebudgetguard', 'cross-browser', 'quota', 'eviction', 'crash'])

require_all('src/opfs-block-store.mjs', ['rollbackOwnsFinalBlock', 'rollbackOwnershipSkips', 'storage:opfs-block-put-rollback-skipped', 'pre-existing-duplicate-block-not-owned-by-put', 'final-block-not-created-by-put'])
require_all('tools/opfs_block_store_owned_rollback_guard_probe.mjs', ['opfs:block-store-owned-rollback-guard-proof', 'duplicate-put-trace-failure-must-not-delete-existing-block', 'duplicate-put-abort-during-inspection-must-not-delete-existing-block', 'owned-write-failure-still-rolls-back-created-final-block', 'rollbackOwnershipSkips'])
require_all('tools/browser_opfs_block_store_owned_rollback_guard_probe.mjs', ['browser:opfs-block-store-owned-rollback-guard-proof', 'browser-duplicate-put-trace-failure-must-not-delete-existing-block', 'bytesPreserved', 'opfsWebLockGuardedBlockStore', 'locksAfterGuarded'])
require_all('tools/opfs_block_store_owned_rollback_guard_contract_audit.mjs', ['facility:opfs-block-store-owned-rollback-guard-contract-audit', 'surface:opfs-block-store-owned-rollback-guard', 'owned rollback guard'])
require_all_lower('docs/40-validation/opfs-block-store-owned-rollback-guard-slice.md', ['ownership-aware rollback', 'duplicate', 'pre-existing valid block', 'cross-browser', 'fsync', 'crash', 'eviction'])
require_all_lower('docs/40-validation/browser-opfs-block-store-owned-rollback-guard-slice.md', ['managed chromium', 'duplicate', 'rollback', 'cross-browser', 'fsync', 'crash', 'eviction'])
require_all_lower('docs/40-validation/opfs-block-store-owned-rollback-guard-contract-audit-slice.md', ['audit', 'ownership-aware rollback', 'cross-browser', 'fsync', 'crash', 'eviction'])
ok('opfs block-store owned rollback guard hooks present')

manifest = j('test/manifest.json')
impact = j('test/impact-map.json')
inventory = j('test/surface-inventory.json')
tasks = manifest.get('tasks') or []
task_ids = [task.get('id') for task in tasks]
if len(task_ids) != len(set(task_ids)):
    fail('test/manifest.json has duplicate task ids')
required_tasks = [
    'scheduler:storage-lane-quarantine-clearance-receipt-provenance-binding-proof',
    'facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof',
    'scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof',
    'facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof',
    'scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof',
    'facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof',
    'scheduler:storage-lane-quarantine-lane-filter-import-guard-proof',
    'facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit',
    'browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof',
    'scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof',
    'facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof',
    'scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof',
    'facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof',
    'scheduler:storage-lane-quarantine-status-transition-import-proof',
    'facility:storage-lane-quarantine-status-transition-import-contract-audit',
    'browser:opfs-web-lock-quarantine-status-transition-import-proof',
    'scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof',
    'facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof',
    'scheduler:storage-lane-quarantine-review-replay-key-scope-proof',
    'facility:storage-lane-quarantine-review-replay-key-scope-contract-audit',
    'browser:opfs-web-lock-quarantine-review-replay-key-scope-proof',
    'scheduler:storage-lane-quarantine-partial-clearance-replay-scope-proof',
    'facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit',
    'browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof',
    'scheduler:storage-lane-quarantine-clearance-lanewide-query-scope-proof',
    'facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit',
    'browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof',
    'scheduler:storage-lane-quarantine-legacy-clear-binding-proof',
    'facility:storage-lane-quarantine-legacy-clear-binding-contract-audit',
    'browser:opfs-web-lock-quarantine-legacy-clear-binding-proof',
    'scheduler:storage-lane-unsettled-orphan-review-proof',
    'facility:storage-lane-unsettled-orphan-review-contract-audit',
    'browser:opfs-web-lock-unsettled-orphan-review-proof',
    'scheduler:storage-lane-quarantine-review-binding-proof',
    'scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof',
    'facility:storage-lane-quarantine-review-binding-contract-audit',
    'browser:opfs-web-lock-quarantine-review-binding-proof',
    'scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof',
    'facility:storage-lane-quarantine-review-binding-contract-audit',
    'browser:opfs-web-lock-quarantine-review-binding-proof',
    'scheduler:storage-lane-quarantine-ledger-roundtrip-proof',
    'facility:storage-lane-quarantine-ledger-contract-audit',
    'browser:opfs-web-lock-quarantine-ledger-roundtrip-proof',
    'scheduler:storage-lane-quarantine-handoff-proof',
    'facility:storage-lane-quarantine-handoff-contract-audit',
    'browser:opfs-web-lock-quarantine-handoff-proof',
    'scheduler:storage-lane-late-failure-quarantine-proof',
    'facility:storage-lane-late-failure-quarantine-contract-audit',
    'browser:opfs-web-lock-late-failure-quarantine-proof',
    'scheduler:storage-lane-late-settlement-recovery-gate-proof',
    'facility:storage-lane-late-settlement-contract-audit',
    'browser:opfs-web-lock-late-settlement-recovery-gate-proof',
    'scheduler:storage-lane-operation-timeout-proof',
    'facility:storage-lane-operation-timeout-contract-audit',
    'browser:opfs-web-lock-operation-timeout-boundary-proof',
    'scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof',
    'facility:web-lock-read-timeout-nonpoison-contract-audit',
    'browser:opfs-web-lock-read-timeout-nonpoison-proof',
    'browser:opfs-web-lock-service-worker-fetch-lifecycle-proof',
    'facility:service-worker-fetch-lifecycle-contract-audit',
    'browser:opfs-web-lock-service-worker-update-race-proof',
    'facility:service-worker-update-race-contract-audit',
    'browser:opfs-web-lock-service-worker-shutdown-boundary-proof',
    'facility:service-worker-shutdown-boundary-contract-audit',
    'browser:opfs-web-lock-service-worker-restart-update-proof',
    'facility:service-worker-restart-update-contract-audit',
    'browser:opfs-web-lock-service-worker-lifecycle-proof',
    'facility:service-worker-lifecycle-contract-audit',
    'browser:opfs-web-lock-settled-recovery-proof',
    'scheduler:storage-lane-web-lock-settled-recovery-proof',
    'facility:web-lock-settled-recovery-contract-audit',
    'browser:opfs-web-lock-tab-timeout-proof',
    'scheduler:storage-lane-web-lock-timeout-health-proof',
    'facility:branch-continuity-audit',
    'facility:web-lock-lifecycle-contract-audit',
    'browser:opfs-web-lock-tab-termination-proof',
    'browser:opfs-web-lock-timeout-proof',
    'coord:web-lock-timeout-proof',
    'browser:opfs-guarded-corrupt-repair-timeout-proof',
    'facility:revision-lineage-merge-audit',
    'opfs:block-store-corrupt-block-repair-proof',
    'browser:opfs-corrupt-block-repair-proof',
    'browser:opfs-web-lock-guarded-contention-proof',
    'coord:web-lock-strict-option-guard-proof',
    'facility:web-lock-strict-option-guard-contract-audit',
    'browser:opfs-web-lock-strict-option-guard-proof',
    'opfs:block-store-abort-signal-proof',
    'facility:opfs-block-store-abort-signal-contract-audit',
    'browser:opfs-block-store-abort-signal-proof',
    'opfs:block-store-write-budget-guard-proof',
    'facility:opfs-block-store-write-budget-guard-contract-audit',
    'browser:opfs-block-store-write-budget-guard-proof',
    'opfs:block-store-owned-rollback-guard-proof',
    'facility:opfs-block-store-owned-rollback-guard-contract-audit',
    'browser:opfs-block-store-owned-rollback-guard-proof',
    'opfs:block-store-rollback-valid-block-preserve-proof',
    'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
    'browser:opfs-block-store-rollback-valid-block-preserve-proof',
    'opfs:block-store-write-budget-duplicate-bypass-proof',
    'facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit',
    'browser:opfs-block-store-write-budget-duplicate-bypass-proof',
    'cube:deep-audit',
    'cube:artifact-budget-audit',
]
missing_tasks = [tid for tid in required_tasks if tid not in set(task_ids)]
if missing_tasks:
    fail(f'test/manifest.json missing tasks {missing_tasks}')
by_id = {task.get('id'): task for task in tasks}
for tid in [tid for tid in task_ids if tid and tid.startswith('browser:')]:
    task = by_id[tid]
    if 'release' in task.get('tiers', []):
        fail(f'{tid} must stay out of release tier')
    if task.get('lane') != 'browser' or task.get('parallelGroup') != 'browser-process':
        fail(f'{tid} must be a serial browser-process task')
violations = []
for task in tasks:
    command = ' '.join(task.get('command') or [])
    for hit in re.findall(r'REV\d{4}-', command):
        if hit != f'{PFX}-':
            violations.append({'id': task.get('id'), 'commandHit': hit})
    for output in task.get('outputs') or []:
        for hit in re.findall(r'REV\d{4}-', output):
            if hit != f'{PFX}-':
                violations.append({'id': task.get('id'), 'outputHit': hit})
if violations:
    fail(f'manifest has stale REV output prefixes: {violations[:5]}')
ok('manifest current tasks and output prefixes aligned')

impact_task_ids = {tid for rule in (impact.get('rules') or []) for tid in (rule.get('taskIds') or [])}
surface_ids = {surface.get('id') for surface in (inventory.get('surfaces') or [])}
for tid in required_tasks:
    if tid not in impact_task_ids:
        fail(f'test/impact-map.json missing task coverage for {tid}')
for sid in [
    'surface:storage-lane-quarantine-restore-expected-fingerprint',
    'surface:browser-opfs-web-lock-quarantine-restore-expected-fingerprint',
    'surface:storage-lane-quarantine-restore-expected-fingerprint-contract-audit',
    'surface:storage-lane-quarantine-status-transition-import',
    'surface:browser-opfs-web-lock-quarantine-status-transition-import',
    'surface:storage-lane-quarantine-status-transition-import-contract-audit',
    'surface:storage-lane-quarantine-clearance-replay-key-receipt-integrity',
    'surface:browser-opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity',
    'surface:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit',
    'surface:storage-lane-quarantine-clearance-row-replay-guard-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-clearance-row-replay-guard',
    'surface:storage-lane-quarantine-clearance-row-replay-guard',
    'surface:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard',
    'surface:storage-lane-quarantine-clearance-epoch-replay-guard',
    'surface:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard',
    'surface:storage-lane-quarantine-noop-clearance-receipt-guard',
    'surface:storage-lane-unsettled-orphan-review-contract-audit',
    'surface:browser-opfs-web-lock-unsettled-orphan-review',
    'surface:storage-lane-unsettled-orphan-review',
    'surface:storage-lane-quarantine-legacy-clear-binding-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-legacy-clear-binding',
    'surface:storage-lane-quarantine-legacy-clear-binding',
    'surface:storage-lane-quarantine-restore-backpressure-binding-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-restore-backpressure-binding',
    'surface:storage-lane-quarantine-restore-backpressure-binding',
    'surface:storage-lane-quarantine-review-binding-contract-audit',
    'surface:browser-opfs-web-lock-quarantine-review-binding',
    'surface:storage-lane-quarantine-review-binding',
    'surface:storage-lane-quarantine-ledger-persistence',
    'surface:browser-opfs-web-lock-quarantine-ledger-persistence',
    'surface:storage-lane-quarantine-ledger-persistence-integrity-contract-audit',
    'surface:storage-lane-late-settlement-recovery-gate',
    'surface:storage-lane-late-settlement-contract-audit',
    'surface:browser-opfs-web-lock-late-settlement-recovery-gate',
    'surface:storage-lane-quarantine-handoff',
    'surface:browser-opfs-web-lock-quarantine-handoff',
    'surface:storage-lane-quarantine-handoff-contract-audit',
    'surface:browser-opfs-web-lock-operation-timeout-boundary',
    'surface:storage-lane-operation-timeout',
    'surface:storage-lane-operation-timeout-contract-audit',
    'surface:storage-lane-web-lock-read-timeout-nonpoison',
    'surface:browser-opfs-web-lock-read-timeout-nonpoison',
    'surface:web-lock-read-timeout-nonpoison-contract-audit',
    'surface:browser-opfs-web-lock-service-worker-fetch-lifecycle',
    'surface:service-worker-fetch-lifecycle-contract-audit',
    'surface:browser-opfs-web-lock-service-worker-update-race',
    'surface:service-worker-update-race-contract-audit',
    'surface:browser-opfs-web-lock-service-worker-shutdown-boundary',
    'surface:service-worker-shutdown-boundary-contract-audit',
    'surface:browser-opfs-web-lock-service-worker-restart-update',
    'surface:service-worker-restart-update-contract-audit',
    'surface:browser-opfs-web-lock-service-worker-lifecycle',
    'surface:service-worker-lifecycle-contract-audit',
    'surface:browser-opfs-web-lock-settled-recovery',
    'surface:storage-lane-web-lock-settled-recovery',
    'surface:browser-opfs-web-lock-tab-timeout',
    'surface:storage-lane-web-lock-timeout-health',
    'surface:browser-opfs-web-lock-tab-termination',
    'surface:browser-opfs-web-lock-timeout',
    'surface:browser-opfs-corrupt-block-repair',
    'surface:opfs-guarded-corrupt-repair-timeout-merge',
    'surface:browser-opfs-web-lock-tab-timeout',
    'surface:storage-lane-web-lock-timeout-health',
    'surface:branch-continuity',
    'surface:opfs-block-store-abort-signal',
    'surface:browser-opfs-block-store-abort-signal',
    'surface:opfs-block-store-abort-signal-contract-audit',
    'surface:opfs-block-store-write-budget-guard',
    'surface:browser-opfs-block-store-write-budget-guard',
    'surface:opfs-block-store-write-budget-guard-contract-audit',
    'surface:opfs-block-store-owned-rollback-guard',
    'surface:browser-opfs-block-store-owned-rollback-guard',
    'surface:opfs-block-store-owned-rollback-guard-contract-audit',
    'surface:opfs-block-store-write-budget-duplicate-bypass',
    'surface:browser-opfs-block-store-write-budget-duplicate-bypass',
    'surface:opfs-block-store-write-budget-duplicate-bypass-contract-audit',
    'surface:opfs-block-store-rollback-valid-block-preserve',
    'surface:browser-opfs-block-store-rollback-valid-block-preserve',
    'surface:opfs-block-store-rollback-valid-block-preserve-contract-audit',
]:
    if sid not in surface_ids:
        fail(f'test/surface-inventory.json missing surface {sid}')
ok('impact map and surface inventory cover current work')

plan_files = [
    'src/storage-lane-scheduler.mjs',
    'src/block-store-lane-adapter.mjs',
    'src/browserrt.mjs',
    'src/types.d.ts',
    'tools/storage_lane_quarantine_receipt_restore_integrity_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_receipt_restore_integrity_probe.mjs',
    'tools/storage_lane_quarantine_receipt_restore_integrity_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-receipt-restore-integrity-slice.md',
    'docs/40-validation/storage-lane-quarantine-receipt-restore-integrity-contract-audit-slice.md',
    'tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs',
    'tools/storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs',
    'tools/lib/quarantine_restore_expected_fingerprint_harness.mjs',
    'tools/current_office_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-restore-expected-fingerprint-slice.md',
    'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-contract-audit-slice.md',

    'tools/storage_lane_quarantine_review_replay_key_scope_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_review_replay_key_scope_probe.mjs',
    'tools/storage_lane_quarantine_review_replay_key_scope_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-review-replay-key-scope-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-review-replay-key-scope-slice.md',
    'docs/40-validation/storage-lane-quarantine-review-replay-key-scope-contract-audit-slice.md',
    'tools/storage_lane_quarantine_partial_clearance_replay_scope_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_partial_clearance_replay_scope_probe.mjs',
    'tools/storage_lane_quarantine_partial_clearance_replay_scope_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-partial-clearance-replay-scope-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-partial-clearance-replay-scope-slice.md',
    'docs/40-validation/storage-lane-quarantine-partial-clearance-replay-scope-contract-audit-slice.md',
    'tools/storage_lane_quarantine_clearance_lanewide_query_scope_probe.mjs',
    'tools/browser_opfs_web_lock_quarantine_clearance_lanewide_query_scope_probe.mjs',
    'tools/storage_lane_quarantine_clearance_lanewide_query_scope_contract_audit.mjs',
    'docs/40-validation/storage-lane-quarantine-clearance-lanewide-query-scope-slice.md',
    'docs/40-validation/browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope-slice.md',
    'docs/40-validation/storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit-slice.md',
    'tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs',
    'tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs',
    'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md',
    'docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md',
    'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-contract-audit-slice.md',
    'test/manifest.json',
    'test/impact-map.json',
    'test/surface-inventory.json',
    'README.md',
    'START_HERE.md',
    'AGENTS.md',
    'CONTEXT-PACK.md',
    'tools/web_lock_strict_option_guard_probe.mjs',
    'tools/browser_opfs_web_lock_strict_option_guard_probe.mjs',
    'tools/web_lock_strict_option_guard_contract_audit.mjs',
    'docs/40-validation/web-lock-strict-option-guard-slice.md',
    'docs/40-validation/browser-opfs-web-lock-strict-option-guard-slice.md',
    'docs/40-validation/web-lock-strict-option-guard-contract-audit-slice.md',
    'src/web-lock-coordinator.mjs',
    'CHANGELOG.md',
    'tools/lib/fake_opfs_harness.mjs',
    'tools/opfs_block_store_abort_signal_probe.mjs',
    'tools/browser_opfs_block_store_abort_signal_probe.mjs',
    'tools/opfs_block_store_abort_signal_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-abort-signal-slice.md',
    'docs/40-validation/browser-opfs-block-store-abort-signal-slice.md',
    'docs/40-validation/opfs-block-store-abort-signal-contract-audit-slice.md',
    'tools/opfs_block_store_write_budget_guard_probe.mjs',
    'tools/browser_opfs_block_store_write_budget_guard_probe.mjs',
    'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
    'docs/40-validation/opfs-block-store-write-budget-guard-slice.md',
    'docs/40-validation/browser-opfs-block-store-write-budget-guard-slice.md',
    'docs/40-validation/opfs-block-store-write-budget-guard-contract-audit-slice.md',
    'CUBE-META.json',
    'REVISION-RECEIPT.json',
    'REENTRY-CONTRACT.json',
    'SURFACE-STATUS.json',
    'VALIDATION-INDEX.json',
    'tools/check_cube.py',
    'tools/deep_cube_audit.mjs',
    'package.json',
    'Makefile',
]
package_plan = ' '.join(package.get('scripts', {}).get('plan', '').split())
makefile = text('Makefile')
missing_plan = [rel for rel in plan_files if rel not in package_plan]
if missing_plan:
    fail(f'package.json plan command missing current files {missing_plan}')
ok('plan command covers current files')

old = []
for path in (ROOT / 'artifacts').rglob('*'):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    hits = re.findall(r'REV\d{4}-', rel)
    if hits and not any(hit in {f'{PFX}-', f'REV{PREV[3:]}-'} for hit in hits):
        old.append(rel)
if old:
    fail(f'stale generated artifact revisions present: {old[:10]}')
ok('artifact revision retention bounded')


require_all('src/opfs-block-store.mjs', ['rollbackValidBlockPreserves', 'rollbackIntegrityChecks', 'rollbackIntegrityCheckFailures', 'storage:opfs-block-put-rollback-preserved', 'valid-final-block-preserved', 'failed-put-rollback-preserve-check'])
require_all('tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs', ['opfs:block-store-rollback-valid-block-preserve-proof', 'trace-failure-after-close-preserves-valid-final-block', 'abort-after-close-preserves-valid-final-block', 'invalid-owned-failure-still-rolls-back-file'])
require_all('tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs', ['browser:opfs-block-store-rollback-valid-block-preserve-proof', 'browser-trace-failure-after-close-preserves-valid-final-block', 'opfsRollbackValidBlockPreserveProof', 'locksAfterGuarded'])
require_all('tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs', ['facility:opfs-block-store-rollback-valid-block-preserve-contract-audit', 'surface:opfs-block-store-rollback-valid-block-preserve', 'current-office:current-needles', 'rollbackValidBlockPreserves'])
require_all_lower('docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md', ['rollback', 'valid block', 'preserve', 'cross-browser', 'fsync', 'crash', 'eviction'])
require_all_lower('docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md', ['managed chromium', 'rollback', 'preserve', 'cross-browser', 'fsync', 'crash', 'eviction'])
require_all_lower('docs/40-validation/opfs-block-store-rollback-valid-block-preserve-contract-audit-slice.md', ['audit', 'rollback', 'preserve', 'cross-browser', 'fsync', 'crash', 'eviction'])
ok('opfs block-store rollback valid block preserve hooks present')

print(f'[check_cube] PASS: {REV} {VERSION} {EXPECTED["codename"]}')
