#pragma once

#include <string>


namespace anonsync {

struct IngressReservationServiceHandle {
    std::string service_config_path;
    std::string service_config_sha256;
};

struct IngressTransportContext {
    bool transport_authenticated = false;
    std::string authenticator;
    std::string principal;
};

struct IngressReservationResult {
    int status_code = 1;
    bool accepted = false;
    std::string report_json;
    std::string failure_reason;
};

IngressReservationResult reserve_ingress_request_json(const IngressReservationServiceHandle& operator_service_handle,
                                                        const IngressTransportContext& trusted_transport_context,
                                                        const std::string& request_json_text);
int run(const std::string& controls_path,
        const std::string& report_path,
        const std::string& contracts_path,
        const std::string& cases_jsonl_path,
        const std::string& ledger_path,
        bool ledger_reset,
        const std::string& ledger_commit_mode = "immediate",
        const std::string& ledger_backend = "local-jsonl",
        const std::string& ledger_backend_capabilities_path = "",
        const std::string& ledger_snapshot_path = "",
        const std::string& ledger_restore_from_snapshot_path = "",
        const std::string& ledger_snapshot_manifest_path = "",
        const std::string& ledger_snapshot_trust_profile_path = "",
        const std::string& ledger_snapshot_trust_profile_sha256 = "");
int run_parser_boundary_selftest();
int run_boundary_fuzz_selftest();
int run_json_codec_fuzz_selftest();
int run_jwt_codec_fuzz_selftest();
int run_route_event_ledger_fuzz_selftest();
int run_ledger_durable_io_selftest();
int run_ledger_backend_adapter_selftest();
int run_ledger_crash_injection_selftest();
int run_ledger_batch_transaction_selftest();
int run_ledger_journal_hardening_selftest();
int run_ledger_backend_interface_selftest();
int run_ledger_sqlite_wal_selftest();
int run_ledger_event_identity_replay_selftest();
int run_ledger_effect_idempotency_selftest();
int run_ledger_sqlite_effect_transition_selftest();
int run_ledger_sqlite_effect_pending_recovery_selftest();
int run_ledger_sqlite_effect_signed_transition_selftest();
int run_sqlite_effect_transition_command(const std::string& ledger_path, const std::string& effect_idempotency_key, long long prepared_sequence, const std::string& prepared_entry_hash, const std::string& terminal_state, const std::string& result_digest_sha256, const std::string& transition_reason);
int run_sqlite_effect_signed_transition_command(const std::string& ledger_path, const std::string& intent_path, const std::string& trust_profile_path, const std::string& trust_profile_sha256);
int run_sqlite_effect_pending_report_command(const std::string& ledger_path, const std::string& report_path);
int run_sqlite_effect_outbox_claim_command(const std::string& ledger_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& claim_report_path);
int run_sqlite_effect_relay_once_command(const std::string& ledger_path, const std::string& downstream_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& terminal_state, const std::string& signer_private_key_pem_path, const std::string& signer_kid, const std::string& trust_profile_path, const std::string& trust_profile_sha256, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_configured_once_command(const std::string& ledger_path, const std::string& relay_config_path, const std::string& relay_config_sha256, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_handle_once_command(const std::string& ledger_path, const std::string& relay_registry_path, const std::string& relay_registry_sha256, const std::string& relay_config_handle, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_ingress_reservation_command(const std::string& ingress_profile_path, const std::string& ingress_profile_sha256, const std::string& ingress_request_path, const std::string& ingress_report_path);
int run_ingress_reservation_service_command(const std::string& ingress_service_config_path,
                                            const std::string& ingress_service_config_sha256,
                                            const std::string& ingress_transport_context_path,
                                            const std::string& ingress_request_path,
                                            const std::string& ingress_report_path);
int run_ingress_reservation_service_selftest();
int run_ledger_sqlite_effect_outbox_claim_selftest();
int run_ledger_sqlite_effect_relay_selftest();
int run_ledger_sqlite_effect_relay_configured_selftest();
int run_ledger_sqlite_effect_relay_handle_selftest();
int run_ledger_sqlite_hardening_selftest();
int run_ledger_backend_capabilities_selftest();
int run_ledger_sqlite_crash_corpus_selftest();
int run_ledger_sqlite_backup_restore_selftest();
int run_ledger_host_capability_probe_selftest();
int run_ledger_sqlite_snapshot_corpus_selftest();
int run_ledger_sqlite_restore_corpus_selftest();
int run_ledger_snapshot_manifest_verifier_selftest();
int run_ledger_sqlite_restore_rollback_guard_selftest();
int run_ledger_sqlite_restore_atomicity_selftest();
int run_ledger_sqlite_restore_locking_selftest();
int run_ledger_sqlite_restore_manifest_binding_selftest();
int run_ledger_sqlite_restore_write_gate_selftest();
int run_ledger_sqlite_restore_prefix_continuity_selftest();
int run_ledger_sqlite_readonly_snapshot_verifier_selftest();
int run_ledger_host_capability_report(const std::string& report_path);
int run_sqlite_writer_lock_holder(const std::string& ledger_path, long long seconds);
int run_sqlite_restore_lock_holder(const std::string& ledger_path, long long seconds);
int run_sqlite_write_gate_holder(const std::string& ledger_path, long long seconds);
int run_ledger_lock_holder(const std::string& ledger_path, long long seconds);
}  // namespace anonsync
