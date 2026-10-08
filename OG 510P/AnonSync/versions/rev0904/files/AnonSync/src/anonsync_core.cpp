#include "anonsync_core.hpp"
#include "anonsync_selftest_api.hpp"

#include <exception>
#include <iostream>
#include <string>

// rev0594 small CLI translation unit. Implementation lives in anonsync_core_lib.
// Compatibility/source-surface needles retained for historical validators:
// OperationContractTable load_operation_contract_table validate_operation_contract_binding --contracts contract_digest_sha256 tenant_id cnf
// path_template_matches find_http_contract find_event_contract normalize_case_from_envelope bearer_token_from_headers x-anonsync-contract-file --selftest-json-parser unescaped control character in JSON string base64url input uses forbidden padding
// struct ReplayLedger entry_hash_material --cases-jsonl explicit-reset-request cloud_event_source_present durable replay ledger already contains JWT jti streamed_case_lines
// duplicate JSON object key rejected, invalid JSON number: leading zero, JSON nesting depth exceeded, --selftest-boundary-fuzz
// rev0593 partition compatibility: anonsync_core_parts/01_json_codec_crypto.inc anonsync_core_parts/02_contracts_policy_profiles.inc anonsync_core_parts/03_normalizer_envelopes.inc anonsync_core_parts/04_replay_ledger.inc anonsync_core_parts/05_jwt_policy_decision.inc anonsync_core_parts/06_reporting_selftests.inc anonsync_core_parts/07_runner.inc
// rev0594 extraction needles: anonsync_core_lib run_json_codec_fuzz_selftest run_jwt_codec_fuzz_selftest run_route_event_ledger_fuzz_selftest base64url canonical residual bits rejected percent-encoded dot segment rejected
// rev0601 CLI needle: --ledger-backend local-jsonl|sqlite-wal --selftest-ledger-sqlite-wal run_ledger_sqlite_wal_selftest backend factory SQLite WAL replay ledger
// rev0603 CLI needle: --ledger-backend-capabilities --selftest-ledger-backend-capabilities --selftest-ledger-sqlite-crash-corpus --selftest-ledger-sqlite-hold-writer capability manifest consumption SQLite crash corpus multiprocess contention
// rev0602 CLI needle: --selftest-ledger-sqlite-hardening run_ledger_sqlite_hardening_selftest SQLite/WAL integrity_check backend_profile sidecar symlink corruption recovery hardening
// rev0651 CLI needle: --selftest-sync-domain-model run_sync_domain_model_selftest sync relative path manifest entry chunk lineage idempotency key

int main(int argc, char** argv) {
    const int replay_ledger_helper =
        anonsync::dispatch_sqlite_replay_ledger_self_exec_helper(argc, argv);
    if (replay_ledger_helper !=
        anonsync::kSqliteReplayLedgerSelfExecHelperNotMatched) {
        return replay_ledger_helper;
    }

    std::string controls;
    std::string report;
    std::string contracts;
    std::string cases_jsonl;
    std::string ledger;
    std::string ledger_commit_mode = "immediate";
    std::string ledger_backend = "local-jsonl";
    std::string ledger_backend_capabilities;
    std::string ledger_snapshot;
    std::string ledger_restore_from_snapshot;
    std::string ledger_snapshot_manifest;
    std::string ledger_snapshot_trust_profile;
    std::string ledger_snapshot_trust_profile_sha256;
    std::string ledger_reset_state;
    std::string ledger_reset_state_report;
    std::string ledger_reset_request;
    std::string ledger_reset_request_sha256;
    std::string ledger_reset_receipt;
    std::string ingress_profile;
    std::string ingress_profile_sha256;
    std::string ingress_service_config;
    std::string ingress_service_config_sha256;
    std::string ingress_transport_context;
    std::string ingress_request;
    std::string ingress_report;
    std::string sync_checkpoint;
    std::string sync_session_id;
    std::string sync_operator_status_report;
    std::string sync_operator_recovery_workflow_config;
    std::string sync_operator_recovery_workflow_report;
    std::string sync_peer_ingress_retention_report;
    std::string sync_peer_authority_supersession_report;
    std::string sync_sidecar_repair_reset_report;
    std::string sync_staging_root;
    std::string sync_path;
    std::string sync_review_event_idempotency_key;
    std::string sync_operator_id;
    std::string sync_repair_reason = "sidecar-review-repaired-reset-by-operator-cli";
    std::string sync_retention_reason;
    std::string sync_supersession_reason;
    std::string sync_repair_worker_id;
    std::string sync_daemon_report;
    std::string sync_source_root;
    std::string sync_destination_root;
    std::string sync_expected_folder_id;
    std::string sync_expected_source_device_id;
    std::string sync_expected_destination_device_id;
    std::string sync_expected_peer_id;
    std::string sync_peer_id;
    std::string sync_peer_session_id;
    std::string sync_transport_instance_id;
    std::string sync_old_transport_key_id;
    std::string sync_replacement_transport_key_id;
    std::string sync_worker_id;
    std::string sync_daemon_id;
    std::string sync_daemon_heartbeat_path;
    long long sync_operator_now_epoch = 0;
    long long sync_sqlite_busy_timeout_ms = static_cast<long long>(anonsync::kSyncPeerTransportDefaultSqliteBusyTimeoutMs);
    long long sync_retention_now_epoch = 0;
    long long sync_retention_completed_older_than_epoch = 0;
    long long sync_retention_abandoned_older_than_epoch = 0;
    long long sync_retention_authority_denial_older_than_epoch = 0;
    long long sync_retention_max_completed_rows = 0;
    long long sync_retention_max_abandoned_rows = 0;
    long long sync_retention_max_authority_denial_rows = 0;
    long long sync_retention_max_frame_bytes = 16 * 1024 * 1024;
    long long sync_retention_max_chunk_count = 1024;
    long long sync_retention_max_metadata_field_bytes = 64 * 1024;
    long long sync_supersession_overlap_from_epoch = 0;
    long long sync_supersession_overlap_until_epoch = 0;
    long long sync_repair_at_epoch = 0;
    long long sync_repair_worker_lease_epoch = 1;
    long long sync_repair_worker_lease_seconds = 1;
    long long sync_repair_retry_backoff_seconds = 0;
    long long sync_daemon_initial_worker_lease_epoch = 1;
    long long sync_daemon_now_epoch = 0;
    long long sync_daemon_worker_lease_seconds = 60;
    long long sync_daemon_loop_tick_seconds = 1;
    long long sync_daemon_max_loop_passes = 1;
    long long sync_daemon_max_actions_per_pass = 0;
    long long sync_daemon_workorder_retry_backoff_seconds = 0;
    long long sync_daemon_heartbeat_stale_after_seconds = 0;
    bool sync_daemon_recover_sidecars = false;
    bool sync_daemon_without_owner_lock = false;
    bool sync_retention_dry_run = false;
    std::string ledger_effect_idempotency_key;
    std::string ledger_effect_terminal_state;
    std::string ledger_effect_result_sha256;
    std::string ledger_effect_prepared_entry_hash;
    long long ledger_effect_prepared_sequence = 0;
    std::string ledger_effect_transition_reason = "operator-confirmed downstream terminal effect";
    std::string ledger_effect_pending_report;
    std::string ledger_effect_outbox_claim_report;
    std::string ledger_effect_outbox_worker_id;
    long long ledger_effect_outbox_claim_now_epoch = 0;
    long long ledger_effect_outbox_lease_seconds = 0;
    std::string ledger_effect_relay_report;
    std::string ledger_effect_relay_config;
    std::string ledger_effect_relay_config_sha256;
    std::string ledger_effect_relay_registry;
    std::string ledger_effect_relay_registry_sha256;
    std::string ledger_effect_relay_config_handle;
    std::string ledger_effect_relay_downstream_store;
    std::string ledger_effect_relay_worker_id;
    long long ledger_effect_relay_now_epoch = 0;
    long long ledger_effect_relay_lease_seconds = 0;
    std::string ledger_effect_relay_terminal_state = "applied";
    std::string ledger_effect_relay_signer_private_key_pem;
    std::string ledger_effect_relay_signer_kid;
    bool ledger_effect_relay_inject_crash_after_downstream = false;
    std::string ledger_effect_transition_intent;
    std::string ledger_effect_transition_trust_profile;
    std::string ledger_effect_transition_trust_profile_sha256;
    bool selftest_sync_domain_model = false;
    bool selftest_sync_peer_ingress_lifecycle = false;
    bool selftest_parser = false;
    bool selftest_boundary_fuzz = false;
    bool selftest_fuzz_json = false;
    bool selftest_fuzz_jwt = false;
    bool selftest_fuzz_route_event_ledger = false;
    bool selftest_ledger_durable_io = false;
    bool selftest_ledger_backend_adapter = false;
    bool selftest_ledger_crash_injection = false;
    bool selftest_ledger_journal_hardening = false;
    bool selftest_ledger_backend_interface = false;
    bool selftest_ledger_sqlite_wal = false;
    bool selftest_ledger_event_identity_replay = false;
    bool selftest_ledger_effect_idempotency = false;
    bool selftest_ledger_sqlite_effect_transition = false;
    bool selftest_ledger_sqlite_effect_pending_recovery = false;
    bool selftest_ledger_sqlite_effect_signed_transition = false;
    bool selftest_ledger_sqlite_effect_outbox_claim = false;
    bool selftest_ledger_sqlite_effect_relay = false;
    bool selftest_ledger_sqlite_effect_relay_configured = false;
    bool selftest_ledger_sqlite_effect_relay_handle = false;
    bool selftest_ledger_sqlite_hardening = false;
    bool selftest_ledger_backend_capabilities = false;
    bool selftest_ledger_sqlite_crash_corpus = false;
    bool selftest_ledger_sqlite_backup_restore = false;
    bool selftest_ledger_host_capability_probe = false;
    bool selftest_ledger_sqlite_snapshot_corpus = false;
    bool selftest_ledger_sqlite_restore_corpus = false;
    bool selftest_ledger_snapshot_manifest_verifier = false;
    bool selftest_ledger_sqlite_restore_rollback_guard = false;
    bool selftest_ledger_sqlite_restore_atomicity = false;
    bool selftest_ledger_sqlite_restore_locking = false;
    bool selftest_ledger_sqlite_restore_manifest_binding = false;
    bool selftest_ledger_sqlite_restore_write_gate = false;
    bool selftest_ledger_sqlite_restore_prefix_continuity = false;
    bool selftest_ledger_sqlite_readonly_snapshot_verifier = false;
    std::string host_capability_report_path;
    std::string sqlite_writer_lock_hold_path;
    long long sqlite_writer_lock_hold_seconds = 0;
    std::string sqlite_restore_lock_hold_path;
    long long sqlite_restore_lock_hold_seconds = 0;
    std::string sqlite_write_gate_hold_path;
    long long sqlite_write_gate_hold_seconds = 0;
    std::string ledger_lock_hold_path;
    long long ledger_lock_hold_seconds = 0;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--controls" && i + 1 < argc) controls = argv[++i];
        else if (arg == "--report" && i + 1 < argc) report = argv[++i];
        else if (arg == "--contracts" && i + 1 < argc) contracts = argv[++i];
        else if (arg == "--cases-jsonl" && i + 1 < argc) cases_jsonl = argv[++i];
        else if (arg == "--ledger" && i + 1 < argc) ledger = argv[++i];
        else if (arg == "--ledger-commit-mode" && i + 1 < argc) ledger_commit_mode = argv[++i];
        else if (arg == "--ledger-backend" && i + 1 < argc) ledger_backend = argv[++i];
        else if (arg == "--ledger-backend-capabilities" && i + 1 < argc) ledger_backend_capabilities = argv[++i];
        else if (arg == "--ledger-snapshot" && i + 1 < argc) ledger_snapshot = argv[++i];
        else if (arg == "--ledger-restore-from-snapshot" && i + 1 < argc) ledger_restore_from_snapshot = argv[++i];
        else if (arg == "--ledger-snapshot-manifest" && i + 1 < argc) ledger_snapshot_manifest = argv[++i];
        else if (arg == "--ledger-snapshot-trust-profile" && i + 1 < argc) ledger_snapshot_trust_profile = argv[++i];
        else if (arg == "--ledger-snapshot-trust-profile-sha256" && i + 1 < argc) ledger_snapshot_trust_profile_sha256 = argv[++i];
        else if (arg == "--ledger-reset-state" && i + 1 < argc) ledger_reset_state = argv[++i];
        else if (arg == "--ledger-reset-state-report" && i + 1 < argc) ledger_reset_state_report = argv[++i];
        else if (arg == "--ledger-reset-request" && i + 1 < argc) ledger_reset_request = argv[++i];
        else if (arg == "--ledger-reset-request-sha256" && i + 1 < argc) ledger_reset_request_sha256 = argv[++i];
        else if (arg == "--ledger-reset-receipt" && i + 1 < argc) ledger_reset_receipt = argv[++i];
        else if (arg == "--ingress-profile" && i + 1 < argc) ingress_profile = argv[++i];
        else if (arg == "--ingress-profile-sha256" && i + 1 < argc) ingress_profile_sha256 = argv[++i];
        else if (arg == "--ingress-service-config" && i + 1 < argc) ingress_service_config = argv[++i];
        else if (arg == "--ingress-service-config-sha256" && i + 1 < argc) ingress_service_config_sha256 = argv[++i];
        else if (arg == "--ingress-transport-context" && i + 1 < argc) ingress_transport_context = argv[++i];
        else if (arg == "--ingress-request" && i + 1 < argc) ingress_request = argv[++i];
        else if (arg == "--ingress-report" && i + 1 < argc) ingress_report = argv[++i];
        else if (arg == "--sync-checkpoint" && i + 1 < argc) sync_checkpoint = argv[++i];
        else if (arg == "--sync-session-id" && i + 1 < argc) sync_session_id = argv[++i];
        else if (arg == "--sync-operator-now-epoch" && i + 1 < argc) sync_operator_now_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-sqlite-busy-timeout-ms" && i + 1 < argc) sync_sqlite_busy_timeout_ms = std::stoll(argv[++i]);
        else if (arg == "--sync-operator-status-report" && i + 1 < argc) sync_operator_status_report = argv[++i];
        else if (arg == "--sync-operator-recovery-workflow-config" && i + 1 < argc) sync_operator_recovery_workflow_config = argv[++i];
        else if (arg == "--sync-operator-recovery-workflow-report" && i + 1 < argc) sync_operator_recovery_workflow_report = argv[++i];
        else if (arg == "--sync-peer-ingress-retention-report" && i + 1 < argc) sync_peer_ingress_retention_report = argv[++i];
        else if (arg == "--sync-peer-authority-supersession-report" && i + 1 < argc) sync_peer_authority_supersession_report = argv[++i];
        else if (arg == "--sync-sidecar-repair-reset-report" && i + 1 < argc) sync_sidecar_repair_reset_report = argv[++i];
        else if (arg == "--sync-staging-root" && i + 1 < argc) sync_staging_root = argv[++i];
        else if (arg == "--sync-path" && i + 1 < argc) sync_path = argv[++i];
        else if (arg == "--sync-review-event-key" && i + 1 < argc) sync_review_event_idempotency_key = argv[++i];
        else if (arg == "--sync-operator-id" && i + 1 < argc) sync_operator_id = argv[++i];
        else if (arg == "--sync-repair-reason" && i + 1 < argc) sync_repair_reason = argv[++i];
        else if (arg == "--sync-retention-reason" && i + 1 < argc) sync_retention_reason = argv[++i];
        else if (arg == "--sync-supersession-reason" && i + 1 < argc) sync_supersession_reason = argv[++i];
        else if (arg == "--sync-retention-now-epoch" && i + 1 < argc) sync_retention_now_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-completed-older-than-epoch" && i + 1 < argc) sync_retention_completed_older_than_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-abandoned-older-than-epoch" && i + 1 < argc) sync_retention_abandoned_older_than_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-authority-denial-older-than-epoch" && i + 1 < argc) sync_retention_authority_denial_older_than_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-completed-rows" && i + 1 < argc) sync_retention_max_completed_rows = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-abandoned-rows" && i + 1 < argc) sync_retention_max_abandoned_rows = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-authority-denial-rows" && i + 1 < argc) sync_retention_max_authority_denial_rows = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-frame-bytes" && i + 1 < argc) sync_retention_max_frame_bytes = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-chunk-count" && i + 1 < argc) sync_retention_max_chunk_count = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-max-metadata-field-bytes" && i + 1 < argc) sync_retention_max_metadata_field_bytes = std::stoll(argv[++i]);
        else if (arg == "--sync-retention-dry-run") sync_retention_dry_run = true;
        else if (arg == "--sync-supersession-overlap-from-epoch" && i + 1 < argc) sync_supersession_overlap_from_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-supersession-overlap-until-epoch" && i + 1 < argc) sync_supersession_overlap_until_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-repair-at-epoch" && i + 1 < argc) sync_repair_at_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-repair-worker-id" && i + 1 < argc) sync_repair_worker_id = argv[++i];
        else if (arg == "--sync-repair-worker-lease-epoch" && i + 1 < argc) sync_repair_worker_lease_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-repair-worker-lease-seconds" && i + 1 < argc) sync_repair_worker_lease_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-repair-retry-backoff-seconds" && i + 1 < argc) sync_repair_retry_backoff_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-report" && i + 1 < argc) sync_daemon_report = argv[++i];
        else if (arg == "--sync-source-root" && i + 1 < argc) sync_source_root = argv[++i];
        else if (arg == "--sync-destination-root" && i + 1 < argc) sync_destination_root = argv[++i];
        else if (arg == "--sync-expected-folder-id" && i + 1 < argc) sync_expected_folder_id = argv[++i];
        else if (arg == "--sync-expected-source-device-id" && i + 1 < argc) sync_expected_source_device_id = argv[++i];
        else if (arg == "--sync-expected-destination-device-id" && i + 1 < argc) sync_expected_destination_device_id = argv[++i];
        else if (arg == "--sync-expected-peer-id" && i + 1 < argc) sync_expected_peer_id = argv[++i];
        else if (arg == "--sync-peer-id" && i + 1 < argc) sync_peer_id = argv[++i];
        else if (arg == "--sync-peer-session-id" && i + 1 < argc) sync_peer_session_id = argv[++i];
        else if (arg == "--sync-transport-instance-id" && i + 1 < argc) sync_transport_instance_id = argv[++i];
        else if (arg == "--sync-old-transport-key-id" && i + 1 < argc) sync_old_transport_key_id = argv[++i];
        else if (arg == "--sync-replacement-transport-key-id" && i + 1 < argc) sync_replacement_transport_key_id = argv[++i];
        else if (arg == "--sync-worker-id" && i + 1 < argc) sync_worker_id = argv[++i];
        else if (arg == "--sync-daemon-id" && i + 1 < argc) sync_daemon_id = argv[++i];
        else if (arg == "--sync-daemon-initial-worker-lease-epoch" && i + 1 < argc) sync_daemon_initial_worker_lease_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-now-epoch" && i + 1 < argc) sync_daemon_now_epoch = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-worker-lease-seconds" && i + 1 < argc) sync_daemon_worker_lease_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-loop-tick-seconds" && i + 1 < argc) sync_daemon_loop_tick_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-max-loop-passes" && i + 1 < argc) sync_daemon_max_loop_passes = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-max-actions-per-pass" && i + 1 < argc) sync_daemon_max_actions_per_pass = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-retry-backoff-seconds" && i + 1 < argc) sync_daemon_workorder_retry_backoff_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-heartbeat" && i + 1 < argc) sync_daemon_heartbeat_path = argv[++i];
        else if (arg == "--sync-daemon-heartbeat-stale-after-seconds" && i + 1 < argc) sync_daemon_heartbeat_stale_after_seconds = std::stoll(argv[++i]);
        else if (arg == "--sync-daemon-recover-sidecars") sync_daemon_recover_sidecars = true;
        else if (arg == "--sync-daemon-without-owner-lock") sync_daemon_without_owner_lock = true;
        else if (arg == "--ledger-effect-idempotency-key" && i + 1 < argc) ledger_effect_idempotency_key = argv[++i];
        else if (arg == "--ledger-effect-terminal-state" && i + 1 < argc) ledger_effect_terminal_state = argv[++i];
        else if (arg == "--ledger-effect-result-sha256" && i + 1 < argc) ledger_effect_result_sha256 = argv[++i];
        else if (arg == "--ledger-effect-prepared-sequence" && i + 1 < argc) ledger_effect_prepared_sequence = std::stoll(argv[++i]);
        else if (arg == "--ledger-effect-prepared-entry-hash" && i + 1 < argc) ledger_effect_prepared_entry_hash = argv[++i];
        else if (arg == "--ledger-effect-transition-reason" && i + 1 < argc) ledger_effect_transition_reason = argv[++i];
        else if (arg == "--ledger-effect-pending-report" && i + 1 < argc) ledger_effect_pending_report = argv[++i];
        else if (arg == "--ledger-effect-outbox-claim-report" && i + 1 < argc) ledger_effect_outbox_claim_report = argv[++i];
        else if (arg == "--ledger-effect-outbox-worker-id" && i + 1 < argc) ledger_effect_outbox_worker_id = argv[++i];
        else if (arg == "--ledger-effect-outbox-claim-now-epoch" && i + 1 < argc) ledger_effect_outbox_claim_now_epoch = std::stoll(argv[++i]);
        else if (arg == "--ledger-effect-outbox-lease-seconds" && i + 1 < argc) ledger_effect_outbox_lease_seconds = std::stoll(argv[++i]);
        else if (arg == "--ledger-effect-relay-report" && i + 1 < argc) ledger_effect_relay_report = argv[++i];
        else if (arg == "--ledger-effect-relay-config" && i + 1 < argc) ledger_effect_relay_config = argv[++i];
        else if (arg == "--ledger-effect-relay-config-sha256" && i + 1 < argc) ledger_effect_relay_config_sha256 = argv[++i];
        else if (arg == "--ledger-effect-relay-registry" && i + 1 < argc) ledger_effect_relay_registry = argv[++i];
        else if (arg == "--ledger-effect-relay-registry-sha256" && i + 1 < argc) ledger_effect_relay_registry_sha256 = argv[++i];
        else if (arg == "--ledger-effect-relay-config-handle" && i + 1 < argc) ledger_effect_relay_config_handle = argv[++i];
        else if (arg == "--ledger-effect-relay-downstream-store" && i + 1 < argc) ledger_effect_relay_downstream_store = argv[++i];
        else if (arg == "--ledger-effect-relay-worker-id" && i + 1 < argc) ledger_effect_relay_worker_id = argv[++i];
        else if (arg == "--ledger-effect-relay-now-epoch" && i + 1 < argc) ledger_effect_relay_now_epoch = std::stoll(argv[++i]);
        else if (arg == "--ledger-effect-relay-lease-seconds" && i + 1 < argc) ledger_effect_relay_lease_seconds = std::stoll(argv[++i]);
        else if (arg == "--ledger-effect-relay-terminal-state" && i + 1 < argc) ledger_effect_relay_terminal_state = argv[++i];
        else if (arg == "--ledger-effect-relay-signer-private-key-pem" && i + 1 < argc) ledger_effect_relay_signer_private_key_pem = argv[++i];
        else if (arg == "--ledger-effect-relay-signer-kid" && i + 1 < argc) ledger_effect_relay_signer_kid = argv[++i];
        else if (arg == "--ledger-effect-relay-inject-crash-after-downstream") ledger_effect_relay_inject_crash_after_downstream = true;
        else if (arg == "--ledger-effect-transition-intent" && i + 1 < argc) ledger_effect_transition_intent = argv[++i];
        else if (arg == "--ledger-effect-transition-trust-profile" && i + 1 < argc) ledger_effect_transition_trust_profile = argv[++i];
        else if (arg == "--ledger-effect-transition-trust-profile-sha256" && i + 1 < argc) ledger_effect_transition_trust_profile_sha256 = argv[++i];
        else if (arg == "--ledger-reset") {
            std::cerr << "--ledger-reset was removed because ordinary open must not mint destructive authority; inspect with --ledger-reset-state and use the digest-pinned standalone --ledger-reset-request command\n";
            return 64;
        }
        else if (arg == "--selftest-sync-domain-model") selftest_sync_domain_model = true;
        else if (arg == "--selftest-sync-peer-ingress-lifecycle") selftest_sync_peer_ingress_lifecycle = true;
        else if (arg == "--selftest-json-parser") selftest_parser = true;
        else if (arg == "--selftest-boundary-fuzz") selftest_boundary_fuzz = true;
        else if (arg == "--selftest-fuzz-json") selftest_fuzz_json = true;
        else if (arg == "--selftest-fuzz-jwt") selftest_fuzz_jwt = true;
        else if (arg == "--selftest-fuzz-route-event-ledger") selftest_fuzz_route_event_ledger = true;
        else if (arg == "--selftest-ledger-durable-io") selftest_ledger_durable_io = true;
        else if (arg == "--selftest-ledger-backend-adapter") selftest_ledger_backend_adapter = true;
        else if (arg == "--selftest-ledger-crash-injection") selftest_ledger_crash_injection = true;
        else if (arg == "--selftest-ledger-batch-transaction") return anonsync::run_ledger_batch_transaction_selftest();
        else if (arg == "--selftest-ledger-journal-hardening") selftest_ledger_journal_hardening = true;
        else if (arg == "--selftest-ledger-backend-interface") selftest_ledger_backend_interface = true;
        else if (arg == "--selftest-ledger-sqlite-wal") selftest_ledger_sqlite_wal = true;
        else if (arg == "--selftest-ledger-event-identity-replay") selftest_ledger_event_identity_replay = true;
        else if (arg == "--selftest-ledger-effect-idempotency") selftest_ledger_effect_idempotency = true;
        else if (arg == "--selftest-ledger-sqlite-effect-transition") selftest_ledger_sqlite_effect_transition = true;
        else if (arg == "--selftest-ledger-sqlite-effect-pending-recovery") selftest_ledger_sqlite_effect_pending_recovery = true;
        else if (arg == "--selftest-ledger-sqlite-effect-signed-transition") selftest_ledger_sqlite_effect_signed_transition = true;
        else if (arg == "--selftest-ledger-sqlite-effect-outbox-claim") selftest_ledger_sqlite_effect_outbox_claim = true;
        else if (arg == "--selftest-ledger-sqlite-effect-relay") selftest_ledger_sqlite_effect_relay = true;
        else if (arg == "--selftest-ledger-sqlite-effect-relay-configured") selftest_ledger_sqlite_effect_relay_configured = true;
        else if (arg == "--selftest-ledger-sqlite-effect-relay-handle") selftest_ledger_sqlite_effect_relay_handle = true;
        else if (arg == "--selftest-ledger-sqlite-hardening") selftest_ledger_sqlite_hardening = true;
        else if (arg == "--selftest-ledger-backend-capabilities") selftest_ledger_backend_capabilities = true;
        else if (arg == "--selftest-ledger-sqlite-crash-corpus") selftest_ledger_sqlite_crash_corpus = true;
        else if (arg == "--selftest-ledger-sqlite-backup-restore") selftest_ledger_sqlite_backup_restore = true;
        else if (arg == "--selftest-ledger-host-capability-probe") selftest_ledger_host_capability_probe = true;
        else if (arg == "--selftest-ledger-sqlite-snapshot-corpus") selftest_ledger_sqlite_snapshot_corpus = true;
        else if (arg == "--selftest-ledger-sqlite-restore-corpus") selftest_ledger_sqlite_restore_corpus = true;
        else if (arg == "--selftest-ledger-snapshot-manifest-verifier") selftest_ledger_snapshot_manifest_verifier = true;
        else if (arg == "--selftest-ledger-sqlite-restore-rollback-guard") selftest_ledger_sqlite_restore_rollback_guard = true;
        else if (arg == "--selftest-ledger-sqlite-restore-atomicity") selftest_ledger_sqlite_restore_atomicity = true;
        else if (arg == "--selftest-ledger-sqlite-restore-locking") selftest_ledger_sqlite_restore_locking = true;
        else if (arg == "--selftest-ledger-sqlite-restore-manifest-binding") selftest_ledger_sqlite_restore_manifest_binding = true;
        else if (arg == "--selftest-ledger-sqlite-restore-write-gate") selftest_ledger_sqlite_restore_write_gate = true;
        else if (arg == "--selftest-ledger-sqlite-restore-prefix-continuity") selftest_ledger_sqlite_restore_prefix_continuity = true;
        else if (arg == "--selftest-ledger-sqlite-readonly-snapshot-verifier") selftest_ledger_sqlite_readonly_snapshot_verifier = true;
        else if (arg == "--ledger-host-capability-report" && i + 1 < argc) host_capability_report_path = argv[++i];
        else if (arg == "--selftest-ledger-hold-lock" && i + 2 < argc) { ledger_lock_hold_path = argv[++i]; ledger_lock_hold_seconds = std::stoll(argv[++i]); }
        else if (arg == "--selftest-ledger-sqlite-hold-writer" && i + 2 < argc) { sqlite_writer_lock_hold_path = argv[++i]; sqlite_writer_lock_hold_seconds = std::stoll(argv[++i]); }
        else if (arg == "--selftest-ledger-sqlite-hold-restore-lock" && i + 2 < argc) { sqlite_restore_lock_hold_path = argv[++i]; sqlite_restore_lock_hold_seconds = std::stoll(argv[++i]); }
        else if (arg == "--selftest-ledger-sqlite-hold-write-gate" && i + 2 < argc) { sqlite_write_gate_hold_path = argv[++i]; sqlite_write_gate_hold_seconds = std::stoll(argv[++i]); }
        else if (arg == "--help") {
            std::cout << "usage: anonsync_core --controls <controls.json> [--cases-jsonl <cases.jsonl>] [--contracts <operation-contracts.json>] [--ledger <ledger.jsonl>] [--ledger-backend local-jsonl|sqlite-wal] [--ledger-backend-capabilities <capabilities.json>] [--ledger-snapshot <snapshot.sqlite>] [--ledger-restore-from-snapshot <snapshot.sqlite>] [--ledger-snapshot-manifest <manifest.json>] [--ledger-snapshot-trust-profile <trust.json>] [--ledger-snapshot-trust-profile-sha256 <hex>] [--ledger-commit-mode immediate|batch] --report <report.json>\n"
                      << "       anonsync_core --ledger-reset-state <ledger.sqlite> --ledger-reset-state-report <state.json>\n"
                      << "       anonsync_core --ledger-reset-request <request.json> --ledger-reset-request-sha256 <hex> --ledger-reset-receipt <receipt.json>\n"
                      << "       anonsync_core --selftest-sync-domain-model\n"
                      << "       anonsync_core --selftest-sync-peer-ingress-lifecycle\n"
                      << "       anonsync_core --selftest-json-parser\n"
                      << "       anonsync_core --selftest-boundary-fuzz\n"
                      << "       anonsync_core --selftest-fuzz-json\n"
                      << "       anonsync_core --selftest-fuzz-jwt\n"
                      << "       anonsync_core --selftest-fuzz-route-event-ledger\n"
                      << "       anonsync_core --selftest-ledger-durable-io\n"
                      << "       anonsync_core --selftest-ledger-backend-adapter\n"
                      << "       anonsync_core --selftest-ledger-crash-injection\n"
                      << "       anonsync_core --selftest-ledger-batch-transaction\n"
                      << "       anonsync_core --selftest-ledger-journal-hardening\n"
                      << "       anonsync_core --selftest-ledger-backend-interface\n"
                      << "       anonsync_core --selftest-ledger-sqlite-wal\n"
                      << "       anonsync_core --selftest-ledger-event-identity-replay\n"
                      << "       anonsync_core --selftest-ledger-effect-idempotency\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-transition\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-pending-recovery\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-signed-transition\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-outbox-claim\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-transition-intent <intent.json> --ledger-effect-transition-trust-profile <trust.json> --ledger-effect-transition-trust-profile-sha256 <hex>\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-pending-report <report.json>\n"
                      << "       anonsync_core --ingress-profile <profile.json> --ingress-profile-sha256 <hex> --ingress-request <request.json> --ingress-report <report.json>\n"
                      << "       anonsync_core --ingress-service-config <service.json> --ingress-service-config-sha256 <hex> --ingress-transport-context <trusted-context.json> --ingress-request <request.json> --ingress-report <report.json>\n"
                      << "       anonsync_core --sync-checkpoint <checkpoint.sqlite> --sync-session-id <session> --sync-operator-now-epoch <epoch> --sync-operator-status-report <report.json> [--sync-daemon-heartbeat <heartbeat.json>]\n"
                      << "       anonsync_core --sync-checkpoint <checkpoint.sqlite> --sync-session-id <session> --sync-operator-id <operator> --sync-retention-now-epoch <epoch> --sync-retention-reason <reason> [--sync-retention-dry-run] [--sync-retention-completed-older-than-epoch <epoch>] [--sync-retention-abandoned-older-than-epoch <epoch>] [--sync-retention-authority-denial-older-than-epoch <epoch>] [--sync-retention-max-completed-rows <n>] [--sync-retention-max-abandoned-rows <n>] [--sync-retention-max-authority-denial-rows <n>] [--sync-retention-max-frame-bytes <bytes>] [--sync-retention-max-chunk-count <n>] [--sync-retention-max-metadata-field-bytes <bytes>] [--sync-sqlite-busy-timeout-ms <0..60000>] --sync-peer-ingress-retention-report <report.json>\n"
                      << "       anonsync_core --sync-checkpoint <checkpoint.sqlite> --sync-session-id <session> --sync-operator-id <operator> --sync-peer-id <peer> --sync-peer-session-id <peer-session> --sync-transport-instance-id <transport> --sync-old-transport-key-id <old-key> --sync-replacement-transport-key-id <new-key> --sync-supersession-overlap-from-epoch <epoch> --sync-supersession-overlap-until-epoch <epoch> --sync-operator-now-epoch <epoch> --sync-supersession-reason <reason> [--sync-sqlite-busy-timeout-ms <0..60000>] --sync-peer-authority-supersession-report <report.json>\n"
                      << "       anonsync_core --sync-operator-recovery-workflow-config <workflow.json> --sync-operator-recovery-workflow-report <report.json>\n"
                      << "       anonsync_core --sync-checkpoint <checkpoint.sqlite> --sync-session-id <session> --sync-staging-root <dir> --sync-path <relative/path> --sync-review-event-key <key> --sync-operator-id <operator> --sync-repair-at-epoch <epoch> --sync-repair-worker-id <worker> --sync-sidecar-repair-reset-report <report.json>\n"
                      << "       anonsync_core --sync-checkpoint <checkpoint.sqlite> --sync-session-id <session> --sync-source-root <dir> --sync-destination-root <dir> --sync-staging-root <dir> --sync-expected-folder-id <id> --sync-expected-source-device-id <id> --sync-expected-destination-device-id <id> --sync-expected-peer-id <id> --sync-worker-id <worker> --sync-daemon-now-epoch <epoch> --sync-daemon-report <report.json> [--sync-daemon-heartbeat <heartbeat.json>]\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-outbox-claim-report <claim.json> --ledger-effect-outbox-worker-id <worker> --ledger-effect-outbox-claim-now-epoch <epoch> --ledger-effect-outbox-lease-seconds <seconds>\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-relay-report <relay.json> --ledger-effect-relay-registry <registry.json> --ledger-effect-relay-registry-sha256 <hex> --ledger-effect-relay-config-handle <handle> --ledger-effect-relay-now-epoch <epoch> [--ledger-effect-relay-inject-crash-after-downstream]\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-relay-report <relay.json> --ledger-effect-relay-config <config.json> --ledger-effect-relay-config-sha256 <hex> --ledger-effect-relay-now-epoch <epoch> [--ledger-effect-relay-inject-crash-after-downstream]\n"
                      << "       anonsync_core --ledger <ledger.sqlite> --ledger-effect-relay-report <relay.json> --ledger-effect-relay-downstream-store <downstream.sqlite> --ledger-effect-relay-worker-id <worker> --ledger-effect-relay-now-epoch <epoch> --ledger-effect-relay-lease-seconds <seconds> --ledger-effect-relay-signer-private-key-pem <key.pem> --ledger-effect-relay-signer-kid <kid> --ledger-effect-transition-trust-profile <trust.json> --ledger-effect-transition-trust-profile-sha256 <hex> [--ledger-effect-relay-inject-crash-after-downstream]\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-relay\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-relay-configured\n"
                      << "       anonsync_core --selftest-ledger-sqlite-effect-relay-handle\n"
                      << "       anonsync_core --selftest-ledger-sqlite-hardening\n"
                      << "       anonsync_core --selftest-ledger-backend-capabilities\n"
                      << "       anonsync_core --selftest-ledger-sqlite-crash-corpus\n"
                      << "       anonsync_core --selftest-ledger-sqlite-backup-restore\n"
                      << "       anonsync_core --selftest-ledger-host-capability-probe\n"
                      << "       anonsync_core --selftest-ledger-sqlite-snapshot-corpus\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-corpus\n"
                      << "       anonsync_core --selftest-ledger-snapshot-manifest-verifier\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-rollback-guard\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-atomicity\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-locking\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-manifest-binding\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-write-gate\n"
                      << "       anonsync_core --selftest-ledger-sqlite-restore-prefix-continuity\n"
                      << "       anonsync_core --selftest-ledger-sqlite-readonly-snapshot-verifier\n"
                      << "       anonsync_core --ledger-host-capability-report <report.json>\n";
            return 0;
        } else {
            std::cerr << "unknown or incomplete argument: " << arg << "\n";
            return 64;
        }
    }
    const bool reset_state_command_selected =
        !ledger_reset_state.empty() || !ledger_reset_state_report.empty();
    const bool reset_command_selected =
        !ledger_reset_request.empty() ||
        !ledger_reset_request_sha256.empty() ||
        !ledger_reset_receipt.empty();
    if (reset_state_command_selected && reset_command_selected) {
        std::cerr << "sqlite-wal replay ledger reset-state inspection and reset execution are separate commands\n";
        return 64;
    }
    if (reset_state_command_selected) {
        if (ledger_reset_state.empty() || ledger_reset_state_report.empty()) {
            std::cerr << "sqlite-wal replay ledger reset-state inspection requires --ledger-reset-state and --ledger-reset-state-report\n";
            return 64;
        }
        if (argc != 5) {
            std::cerr << "sqlite-wal replay ledger reset-state inspection accepts exactly two flag/value pairs and no unrelated arguments\n";
            return 64;
        }
        return anonsync::run_sqlite_replay_ledger_reset_state_command(
            ledger_reset_state, ledger_reset_state_report);
    }
    if (reset_command_selected) {
        if (ledger_reset_request.empty() ||
            ledger_reset_request_sha256.empty() ||
            ledger_reset_receipt.empty()) {
            std::cerr << "sqlite-wal replay ledger reset requires --ledger-reset-request, --ledger-reset-request-sha256, and --ledger-reset-receipt\n";
            return 64;
        }
        // The administrative transition is intentionally standalone. The
        // request owns the exact absolute path and complete prior logical
        // image; unrelated CLI state must not broaden that authority.
        if (argc != 7) {
            std::cerr << "sqlite-wal replay ledger reset accepts exactly three flag/value pairs and no unrelated arguments\n";
            return 64;
        }
        return anonsync::run_sqlite_replay_ledger_reset_command(
            ledger_reset_request, ledger_reset_request_sha256,
            ledger_reset_receipt);
    }
    if (selftest_sync_peer_ingress_lifecycle) return anonsync::run_sync_peer_ingress_lifecycle_selftest();

    if (selftest_sync_domain_model) return anonsync::run_sync_domain_model_selftest();
    if (selftest_parser) return anonsync::run_parser_boundary_selftest();
    if (selftest_boundary_fuzz) return anonsync::run_boundary_fuzz_selftest();
    if (selftest_fuzz_json) return anonsync::run_json_codec_fuzz_selftest();
    if (selftest_fuzz_jwt) return anonsync::run_jwt_codec_fuzz_selftest();
    if (selftest_fuzz_route_event_ledger) return anonsync::run_route_event_ledger_fuzz_selftest();
    if (selftest_ledger_durable_io) return anonsync::run_ledger_durable_io_selftest();
    if (selftest_ledger_backend_adapter) return anonsync::run_ledger_backend_adapter_selftest();
    if (selftest_ledger_crash_injection) return anonsync::run_ledger_crash_injection_selftest();
    if (selftest_ledger_journal_hardening) return anonsync::run_ledger_journal_hardening_selftest();
    if (selftest_ledger_backend_interface) return anonsync::run_ledger_backend_interface_selftest();
    if (selftest_ledger_sqlite_wal) return anonsync::run_ledger_sqlite_wal_selftest();
    if (selftest_ledger_event_identity_replay) return anonsync::run_ledger_event_identity_replay_selftest();
    if (selftest_ledger_effect_idempotency) return anonsync::run_ledger_effect_idempotency_selftest();
    if (selftest_ledger_sqlite_effect_transition) return anonsync::run_ledger_sqlite_effect_transition_selftest();
    if (selftest_ledger_sqlite_effect_pending_recovery) return anonsync::run_ledger_sqlite_effect_pending_recovery_selftest();
    if (selftest_ledger_sqlite_effect_signed_transition) return anonsync::run_ledger_sqlite_effect_signed_transition_selftest();
    if (selftest_ledger_sqlite_effect_outbox_claim) return anonsync::run_ledger_sqlite_effect_outbox_claim_selftest();
    if (selftest_ledger_sqlite_effect_relay) return anonsync::run_ledger_sqlite_effect_relay_selftest();
    if (selftest_ledger_sqlite_effect_relay_configured) return anonsync::run_ledger_sqlite_effect_relay_configured_selftest();
    if (selftest_ledger_sqlite_effect_relay_handle) return anonsync::run_ledger_sqlite_effect_relay_handle_selftest();
    if (!sync_operator_recovery_workflow_report.empty() || !sync_operator_recovery_workflow_config.empty()) {
        return anonsync::run_sync_checkpoint_operator_recovery_workflow_command(sync_operator_recovery_workflow_config,
                                                                                sync_operator_recovery_workflow_report);
    }
    if (!sync_operator_status_report.empty()) {
        return anonsync::run_sync_checkpoint_operator_status_report_command(sync_checkpoint,
                                                                            sync_session_id,
                                                                            sync_operator_now_epoch,
                                                                            sync_operator_status_report,
                                                                            sync_daemon_heartbeat_path);
    }
    if (!sync_peer_ingress_retention_report.empty()) {
        return anonsync::run_sync_peer_ingress_retention_command(sync_checkpoint,
                                                                 sync_session_id,
                                                                 sync_operator_id,
                                                                 sync_retention_reason,
                                                                 sync_retention_now_epoch,
                                                                 sync_retention_completed_older_than_epoch,
                                                                 sync_retention_abandoned_older_than_epoch,
                                                                 sync_retention_authority_denial_older_than_epoch,
                                                                 sync_retention_max_completed_rows,
                                                                 sync_retention_max_abandoned_rows,
                                                                 sync_retention_max_authority_denial_rows,
                                                                 sync_retention_dry_run,
                                                                 sync_peer_ingress_retention_report,
                                                                 sync_sqlite_busy_timeout_ms,
                                                                 sync_retention_max_frame_bytes,
                                                                 sync_retention_max_chunk_count,
                                                                 sync_retention_max_metadata_field_bytes);
    }
    if (!sync_peer_authority_supersession_report.empty()) {
        return anonsync::run_sync_peer_authority_supersession_command(sync_checkpoint,
                                                                      sync_session_id,
                                                                      sync_operator_id,
                                                                      sync_peer_id,
                                                                      sync_peer_session_id,
                                                                      sync_transport_instance_id,
                                                                      sync_old_transport_key_id,
                                                                      sync_replacement_transport_key_id,
                                                                      sync_supersession_overlap_from_epoch,
                                                                      sync_supersession_overlap_until_epoch,
                                                                      sync_operator_now_epoch,
                                                                      sync_supersession_reason,
                                                                      sync_peer_authority_supersession_report,
                                                                      sync_sqlite_busy_timeout_ms);
    }
    if (!sync_sidecar_repair_reset_report.empty()) {
        return anonsync::run_sync_checkpoint_sidecar_repair_reset_command(sync_checkpoint,
                                                                          sync_session_id,
                                                                          sync_staging_root,
                                                                          sync_path,
                                                                          sync_review_event_idempotency_key,
                                                                          sync_operator_id,
                                                                          sync_repair_reason,
                                                                          sync_repair_at_epoch,
                                                                          sync_repair_worker_id,
                                                                          sync_repair_worker_lease_epoch,
                                                                          sync_repair_worker_lease_seconds,
                                                                          sync_repair_retry_backoff_seconds,
                                                                          sync_sidecar_repair_reset_report);
    }
    if (!sync_daemon_report.empty()) {
        return anonsync::run_sync_checkpoint_daemon_run_command(sync_checkpoint,
                                                                sync_session_id,
                                                                sync_source_root,
                                                                sync_destination_root,
                                                                sync_staging_root,
                                                                sync_expected_folder_id,
                                                                sync_expected_source_device_id,
                                                                sync_expected_destination_device_id,
                                                                sync_expected_peer_id,
                                                                sync_peer_id,
                                                                sync_peer_session_id,
                                                                sync_worker_id,
                                                                sync_daemon_id,
                                                                sync_daemon_initial_worker_lease_epoch,
                                                                sync_daemon_now_epoch,
                                                                sync_daemon_worker_lease_seconds,
                                                                sync_daemon_loop_tick_seconds,
                                                                sync_daemon_max_loop_passes,
                                                                sync_daemon_max_actions_per_pass,
                                                                sync_daemon_workorder_retry_backoff_seconds,
                                                                sync_daemon_recover_sidecars,
                                                                !sync_daemon_without_owner_lock,
                                                                sync_daemon_report,
                                                                sync_daemon_heartbeat_path,
                                                                sync_daemon_heartbeat_stale_after_seconds);
    }
    if (!ingress_service_config.empty() || !ingress_service_config_sha256.empty() || !ingress_transport_context.empty()) {
        if (!ingress_profile.empty() || !ingress_profile_sha256.empty()) {
            std::cerr << "ingress service reservation cannot be combined with --ingress-profile or --ingress-profile-sha256\n";
            return 64;
        }
        return anonsync::run_ingress_reservation_service_command(ingress_service_config,
                                                                 ingress_service_config_sha256,
                                                                 ingress_transport_context,
                                                                 ingress_request,
                                                                 ingress_report);
    }
    if (!ingress_profile.empty() || !ingress_profile_sha256.empty() || !ingress_request.empty() || !ingress_report.empty()) {
        return anonsync::run_ingress_reservation_command(ingress_profile, ingress_profile_sha256, ingress_request, ingress_report);
    }
    if (!ledger_effect_relay_registry.empty() || !ledger_effect_relay_registry_sha256.empty() || !ledger_effect_relay_config_handle.empty()) {
        if (ledger.empty() || ledger_effect_relay_report.empty()) {
            std::cerr << "handle-bound effect relay requires --ledger, --ledger-effect-relay-report, --ledger-effect-relay-registry, --ledger-effect-relay-registry-sha256, --ledger-effect-relay-config-handle, and --ledger-effect-relay-now-epoch\n";
            return 64;
        }
        return anonsync::run_sqlite_effect_relay_handle_once_command(ledger,
                                                                     ledger_effect_relay_registry,
                                                                     ledger_effect_relay_registry_sha256,
                                                                     ledger_effect_relay_config_handle,
                                                                     ledger_effect_relay_now_epoch,
                                                                     ledger_effect_relay_report,
                                                                     ledger_effect_relay_inject_crash_after_downstream);
    }
    if (!ledger_effect_relay_config.empty() || !ledger_effect_relay_config_sha256.empty()) {
        if (ledger.empty() || ledger_effect_relay_report.empty()) {
            std::cerr << "configured effect relay requires --ledger, --ledger-effect-relay-report, --ledger-effect-relay-config, --ledger-effect-relay-config-sha256, and --ledger-effect-relay-now-epoch\n";
            return 64;
        }
        return anonsync::run_sqlite_effect_relay_configured_once_command(ledger,
                                                                         ledger_effect_relay_config,
                                                                         ledger_effect_relay_config_sha256,
                                                                         ledger_effect_relay_now_epoch,
                                                                         ledger_effect_relay_report,
                                                                         ledger_effect_relay_inject_crash_after_downstream);
    }
    if (!ledger_effect_relay_report.empty() || !ledger_effect_relay_downstream_store.empty() || !ledger_effect_relay_worker_id.empty() || ledger_effect_relay_now_epoch != 0 || ledger_effect_relay_lease_seconds != 0 || !ledger_effect_relay_signer_private_key_pem.empty() || !ledger_effect_relay_signer_kid.empty()) {
        if (ledger.empty()) {
            std::cerr << "effect relay requires --ledger and --ledger-effect-relay-report\n";
            return 64;
        }
        return anonsync::run_sqlite_effect_relay_once_command(ledger,
                                                              ledger_effect_relay_downstream_store,
                                                              ledger_effect_relay_worker_id,
                                                              ledger_effect_relay_now_epoch,
                                                              ledger_effect_relay_lease_seconds,
                                                              ledger_effect_relay_terminal_state,
                                                              ledger_effect_relay_signer_private_key_pem,
                                                              ledger_effect_relay_signer_kid,
                                                              ledger_effect_transition_trust_profile,
                                                              ledger_effect_transition_trust_profile_sha256,
                                                              ledger_effect_relay_report,
                                                              ledger_effect_relay_inject_crash_after_downstream);
    }
    if (!ledger_effect_transition_intent.empty() || !ledger_effect_transition_trust_profile.empty() || !ledger_effect_transition_trust_profile_sha256.empty()) {
        return anonsync::run_sqlite_effect_signed_transition_command(ledger, ledger_effect_transition_intent, ledger_effect_transition_trust_profile, ledger_effect_transition_trust_profile_sha256);
    }
    if (!ledger_effect_pending_report.empty()) {
        if (ledger.empty()) {
            std::cerr << "effect pending report requires --ledger and --ledger-effect-pending-report\n";
            return 64;
        }
        return anonsync::run_sqlite_effect_pending_report_command(ledger, ledger_effect_pending_report);
    }
    if (!ledger_effect_outbox_claim_report.empty() || !ledger_effect_outbox_worker_id.empty() || ledger_effect_outbox_claim_now_epoch != 0 || ledger_effect_outbox_lease_seconds != 0) {
        if (ledger.empty()) {
            std::cerr << "effect outbox claim requires --ledger and --ledger-effect-outbox-claim-report\n";
            return 64;
        }
        return anonsync::run_sqlite_effect_outbox_claim_command(ledger, ledger_effect_outbox_worker_id, ledger_effect_outbox_claim_now_epoch, ledger_effect_outbox_lease_seconds, ledger_effect_outbox_claim_report);
    }
    if (!ledger_effect_idempotency_key.empty() || !ledger_effect_terminal_state.empty() || !ledger_effect_result_sha256.empty() || ledger_effect_prepared_sequence != 0 || !ledger_effect_prepared_entry_hash.empty()) {
        std::cerr << "effect transition CLI now requires signed intent: use --ledger-effect-transition-intent, --ledger-effect-transition-trust-profile, and --ledger-effect-transition-trust-profile-sha256\n";
        return 64;
    }
    if (selftest_ledger_sqlite_hardening) return anonsync::run_ledger_sqlite_hardening_selftest();
    if (selftest_ledger_backend_capabilities) return anonsync::run_ledger_backend_capabilities_selftest();
    if (selftest_ledger_sqlite_crash_corpus) return anonsync::run_ledger_sqlite_crash_corpus_selftest();
    if (selftest_ledger_sqlite_backup_restore) return anonsync::run_ledger_sqlite_backup_restore_selftest();
    if (selftest_ledger_host_capability_probe) return anonsync::run_ledger_host_capability_probe_selftest();
    if (selftest_ledger_sqlite_snapshot_corpus) return anonsync::run_ledger_sqlite_snapshot_corpus_selftest();
    if (selftest_ledger_sqlite_restore_corpus) return anonsync::run_ledger_sqlite_restore_corpus_selftest();
    if (selftest_ledger_snapshot_manifest_verifier) return anonsync::run_ledger_snapshot_manifest_verifier_selftest();
    if (selftest_ledger_sqlite_restore_rollback_guard) return anonsync::run_ledger_sqlite_restore_rollback_guard_selftest();
    if (selftest_ledger_sqlite_restore_atomicity) return anonsync::run_ledger_sqlite_restore_atomicity_selftest();
    if (selftest_ledger_sqlite_restore_locking) return anonsync::run_ledger_sqlite_restore_locking_selftest();
    if (selftest_ledger_sqlite_restore_manifest_binding) return anonsync::run_ledger_sqlite_restore_manifest_binding_selftest();
    if (selftest_ledger_sqlite_restore_write_gate) return anonsync::run_ledger_sqlite_restore_write_gate_selftest();
    if (selftest_ledger_sqlite_restore_prefix_continuity) return anonsync::run_ledger_sqlite_restore_prefix_continuity_selftest();
    if (selftest_ledger_sqlite_readonly_snapshot_verifier) return anonsync::run_ledger_sqlite_readonly_snapshot_verifier_selftest();
    if (!sqlite_restore_lock_hold_path.empty()) return anonsync::run_sqlite_restore_lock_holder(sqlite_restore_lock_hold_path, sqlite_restore_lock_hold_seconds);
    if (!sqlite_write_gate_hold_path.empty()) return anonsync::run_sqlite_write_gate_holder(sqlite_write_gate_hold_path, sqlite_write_gate_hold_seconds);
    if (!host_capability_report_path.empty()) return anonsync::run_ledger_host_capability_report(host_capability_report_path);
    if (!ledger_lock_hold_path.empty()) return anonsync::run_ledger_lock_holder(ledger_lock_hold_path, ledger_lock_hold_seconds);
    if (!sqlite_writer_lock_hold_path.empty()) return anonsync::run_sqlite_writer_lock_holder(sqlite_writer_lock_hold_path, sqlite_writer_lock_hold_seconds);
    if (controls.empty() || report.empty()) {
        std::cerr << "usage: anonsync_core --controls <controls.json> [--cases-jsonl <cases.jsonl>] [--contracts <operation-contracts.json>] [--ledger <ledger.jsonl>] [--ledger-backend local-jsonl|sqlite-wal] [--ledger-backend-capabilities <capabilities.json>] [--ledger-snapshot <snapshot.sqlite>] [--ledger-restore-from-snapshot <snapshot.sqlite>] [--ledger-snapshot-manifest <manifest.json>] [--ledger-snapshot-trust-profile <trust.json>] [--ledger-snapshot-trust-profile-sha256 <hex>] [--ledger-commit-mode immediate|batch] --report <report.json>\n";
        return 64;
    }
    try {
        return anonsync::run(controls, report, contracts, cases_jsonl, ledger, ledger_commit_mode, ledger_backend, ledger_backend_capabilities, ledger_snapshot, ledger_restore_from_snapshot, ledger_snapshot_manifest, ledger_snapshot_trust_profile, ledger_snapshot_trust_profile_sha256);
    } catch (const std::exception& e) {
        std::cerr << "anonsync_core failed: " << e.what() << "\n";
        return 1;
    }
}

// rev0595 CLI needle: --selftest-ledger-durable-io run_ledger_durable_io_selftest atomic temp-write fsync rename directory-fsync

// rev0596 CLI needle: --selftest-ledger-backend-adapter run_ledger_backend_adapter_selftest flock nonblocking write-ahead journal recovery fail-closed dirty journal

// rev0597 CLI needle: --selftest-ledger-crash-injection --selftest-ledger-hold-lock run_ledger_crash_injection_selftest semantic journal recovery validation crash-point fault injection

// rev0598 CLI needle: --ledger-commit-mode batch --selftest-ledger-batch-transaction run_ledger_batch_transaction_selftest explicit batch transaction flush

// rev0599 CLI needle: --selftest-ledger-journal-hardening run_ledger_journal_hardening_selftest strict journal-v2 only recovery hostile journal parser cases

// rev0600 CLI needle: --selftest-ledger-backend-interface run_ledger_backend_interface_selftest explicit replay-ledger backend interface and sidecar symlink hardening

// rev0601 CLI needle: --ledger-backend sqlite-wal --selftest-ledger-sqlite-wal backend factory local-jsonl sqlite-wal replay-ledger candidate.

// rev0602 CLI needle: --selftest-ledger-sqlite-hardening run_ledger_sqlite_hardening_selftest SQLite integrity/profile/corruption hardening.

// rev0603 CLI needle: --ledger-backend-capabilities run_ledger_backend_capabilities_selftest run_ledger_sqlite_crash_corpus_selftest run_sqlite_writer_lock_holder SQLite crash corpus and backend capability manifest consumption.
// rev0604 CLI needle: --ledger-snapshot --selftest-ledger-sqlite-backup-restore --selftest-ledger-host-capability-probe sqlite3_backup snapshot restore and host capability probe.

// rev0605 CLI needle: --selftest-ledger-sqlite-snapshot-corpus --ledger-host-capability-report hostile snapshot corpus and machine-emitted host capability report.
// rev0606 CLI needle: --ledger-restore-from-snapshot --selftest-ledger-sqlite-restore-corpus compiled SQLite snapshot restore command with hostile restore corpus.
// rev0607 CLI needle: --ledger-snapshot-manifest --ledger-snapshot-trust-profile signed SQLite snapshot manifest and restore-root verification.
// rev0612 CLI needle: --selftest-ledger-snapshot-manifest-verifier strict canonical UTC manifest time parsing, max-age staleness bound, duplicate signer rejection, and restore-root rotation/overlap.
// rev0612 CLI needle: --ledger-snapshot-trust-profile-sha256 digest-pins restore trust material.
// rev0616 CLI needle: --selftest-ledger-sqlite-restore-rollback-guard rejects older or divergent signed snapshot restore over active destination ledgers.
// rev0609 CLI needle: --selftest-ledger-snapshot-manifest-verifier signed snapshot manifest v2 trust-window subject allowlist verifier hardening.
// rev0616 CLI needle: --selftest-ledger-sqlite-restore-atomicity verifies staged temp snapshot restore keeps active destination intact before atomic replace.

// rev0616 CLI needle: --selftest-ledger-sqlite-restore-locking and --selftest-ledger-sqlite-hold-restore-lock serialize signed SQLite/WAL restore replacement.

// rev0616 CLI needle: --selftest-ledger-sqlite-restore-manifest-binding signed snapshot manifest bound inside restore with source digest stability checks.
// rev0616 CLI needle: --selftest-ledger-sqlite-restore-write-gate and --selftest-ledger-sqlite-hold-write-gate coordinate normal SQLite writer/open lifetime with signed restore replacement.

// rev0620 CLI needle: operator-pinned enriched operation-contract table digest rejects table substitution while rev0631 SQLite/WAL schema v9 persists operation identity, contract digest, prepared-effect idempotency key, prepared effect state, ledger_instance_id, and ledger-instance-bound append-only terminal effect transitions.

// rev0624 CLI needle: --selftest-ledger-sqlite-readonly-snapshot-verifier verifies untrusted snapshots without reopening the mutable SQLite backend loader.

// rev0625 CLI needle: --selftest-ledger-effect-idempotency verifies prepared-effect idempotency keys survive reload and reject duplicate effects with fresh JWT ids.

// rev0626 CLI needle: --selftest-ledger-sqlite-effect-transition and --ledger-effect-terminal-state append terminal downstream effect evidence without mutating prepared decision rows.
// rev0631 CLI needle: terminal effect transitions require --ledger-effect-transition-intent plus digest-pinned trust profile and a ledger_instance_id-bound payload; raw prepared-sequence/hash closure is rejected at the CLI and public API.

// rev0633 CLI needle: SQLite/WAL schema v9 effect_outbox atomically reserves dispatchable effects with prepared ledger entries and terminally updates them under signed transition intent.
// rev0634 CLI needle: --ledger-effect-outbox-claim-report schema v10 effect_outbox inflight worker leases and stale-lease reclaim for relay workers.

// rev0635 CLI needle: --ledger-effect-relay-report --ledger-effect-relay-downstream-store --ledger-effect-relay-inject-crash-after-downstream simulate downstream apply and reconcile stale inflight leases to signed terminal evidence.
// rev0636 CLI needle: --ledger-effect-relay-config --ledger-effect-relay-config-sha256 bind relay adapter identity, downstream store, signer, trust pin, worker id, lease, and terminal state to an operator digest-pinned config rather than per-invocation request fields.
// rev0637 CLI needle: --ledger-effect-relay-registry --ledger-effect-relay-registry-sha256 --ledger-effect-relay-config-handle resolve a caller-facing handle through an operator-pinned registry before loading the adapter config.

// rev0638 CLI needle: --ingress-profile --ingress-profile-sha256 --ingress-request --ingress-report accepts authenticated context plus a handle while operator paths, backend, controls, contracts, capability pins, and time policy come from a digest-pinned profile.
// rev0639 CLI needle: --ingress-service-config --ingress-service-config-sha256 loads a service boot config so per-request ingress supplies only request JSON plus a handle, while profile path/digest remain service/operator owned.

// rev0640 CLI needle: service-bound ingress config v2 requires sender_possession HMAC proof before profile adapter invocation or SQLite append.
// rev0641 CLI needle: service-bound ingress config v3 requires sender_possession RS256 proof against a service-pinned public JWK and rejects symmetric caller secrets.
// rev0642 CLI needle: service-bound ingress config v4 requires sender_possession nonce/issued_at freshness and service-owned SQLite replay-cache reservation before profile adapter invocation or ledger append.
// rev0643 CLI needle: service-bound ingress config v5 binds sender_possession and the SQLite replay cache to an operator-configured replay-cache instance id and rejects cache metadata identity drift before append.
// rev0644 CLI needle: --ingress-transport-context carries trusted identity separately from the untrusted request body; request-side authenticated_context/principal/authenticator/transport_authenticated fields fail closed.

// rev0651 CLI needle: C++ sync domain model introduces normalized portable relative paths, manifest entries, chunk coverage, lineage ordering, and sync-scoped mutation idempotency keys.
