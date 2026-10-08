#include "anonsync_core_internal.hpp"

namespace anonsync {

std::string report_json(const Json& root, const Counters& c, const std::vector<std::string>& failed_samples, const std::string& controls_sha, const std::string& contracts_sha, const std::string& contract_root, const std::string& capabilities_sha, const std::string& binary_profile) {
    std::ostringstream out;
    out << "{\n";
    out << "  \"revision_id\": \"" << json_escape(root.at("revision_id").str("rev0589")) << "\",\n";
    out << "  \"parent_revision\": \"" << json_escape(root.at("parent_revision").str("rev0588")) << "\",\n";
    out << "  \"generated_by\": \"cpp/anonsync_core/anonsync_core\",\n";
    out << "  \"source_controls_revision\": \"" << json_escape(root.at("source_controls_revision").str()) << "\",\n";
    out << "  \"controls_digest_sha256\": \"" << controls_sha << "\",\n";
    out << "  \"operation_contract_table_digest_sha256\": \"" << json_escape(contracts_sha) << "\",\n";
    out << "  \"operation_contract_root_sha256\": \"" << json_escape(contract_root) << "\",\n";
    out << "  \"ledger_backend_capabilities_digest_sha256\": \"" << json_escape(capabilities_sha) << "\",\n";
    out << "  \"binary_profile\": \"" << json_escape(binary_profile) << "\",\n";
    out << "  \"counters\": {\n";
    out << "    \"total_cases\": " << c.total_cases << ",\n";
    out << "    \"passed\": " << c.passed << ",\n";
    out << "    \"failed\": " << c.failed << ",\n";
    out << "    \"openapi_cases\": " << c.openapi_cases << ",\n";
    out << "    \"asyncapi_cases\": " << c.asyncapi_cases << ",\n";
    out << "    \"positive_cases\": " << c.positive_cases << ",\n";
    out << "    \"positive_passed\": " << c.positive_passed << ",\n";
    out << "    \"failure_cases\": " << c.failure_cases << ",\n";
    out << "    \"failure_passed\": " << c.failure_passed << ",\n";
    out << "    \"allow_or_accept\": " << c.allow_or_accept << ",\n";
    out << "    \"deny_or_quarantine\": " << c.deny_or_quarantine << ",\n";
    out << "    \"contract_checked_cases\": " << c.contract_checked_cases << ",\n";
    out << "    \"contract_table_rows\": " << c.contract_table_rows << ",\n";
    out << "    \"normalized_context_cases\": " << c.normalized_context_cases << ",\n";
    out << "    \"normalizer_matched_cases\": " << c.normalizer_matched_cases << ",\n";
    out << "    \"normalizer_preblocked_cases\": " << c.normalizer_preblocked_cases << ",\n";
    out << "    \"normalizer_route_rejections\": " << c.normalizer_route_rejections << ",\n";
    out << "    \"normalizer_authorization_rejections\": " << c.normalizer_authorization_rejections << ",\n";
    out << "    \"normalizer_proof_rejections\": " << c.normalizer_proof_rejections << ",\n";
    out << "    \"normalizer_tenant_context_rejections\": " << c.normalizer_tenant_context_rejections << ",\n";
    out << "    \"event_identity_rejections\": " << c.event_identity_rejections << ",\n";
    out << "    \"durable_replay_ledger_rejections\": " << c.durable_replay_ledger_rejections << ",\n";
    out << "    \"effect_idempotency_rejections\": " << c.effect_idempotency_rejections << ",\n";
    out << "    \"ledger_loaded_entries\": " << c.ledger_loaded_entries << ",\n";
    out << "    \"ledger_appended_entries\": " << c.ledger_appended_entries << ",\n";
    out << "    \"ledger_atomic_rewrite_commits\": " << c.ledger_atomic_rewrite_commits << ",\n";
    out << "    \"ledger_directory_fsync_attempts\": " << c.ledger_directory_fsync_attempts << ",\n";
    out << "    \"ledger_lock_acquire_attempts\": " << c.ledger_lock_acquire_attempts << ",\n";
    out << "    \"ledger_lock_contention_denials\": " << c.ledger_lock_contention_denials << ",\n";
    out << "    \"ledger_journal_records_written\": " << c.ledger_journal_records_written << ",\n";
    out << "    \"ledger_journal_recovered_after_commit\": " << c.ledger_journal_recovered_after_commit << ",\n";
    out << "    \"ledger_journal_rolled_back_before_commit\": " << c.ledger_journal_rolled_back_before_commit << ",\n";
    out << "    \"ledger_journal_rejections\": " << c.ledger_journal_rejections << ",\n";
    out << "    \"ledger_batch_flush_commits\": " << c.ledger_batch_flush_commits << ",\n";
    out << "    \"ledger_batch_pending_entries_peak\": " << c.ledger_batch_pending_entries_peak << ",\n";
    out << "    \"ledger_sqlite_transactions\": " << c.ledger_sqlite_transactions << ",\n";
    out << "    \"ledger_sqlite_wal_checkpoints\": " << c.ledger_sqlite_wal_checkpoints << ",\n";
    out << "    \"ledger_sqlite_integrity_checks\": " << c.ledger_sqlite_integrity_checks << ",\n";
    out << "    \"ledger_sqlite_profile_checks\": " << c.ledger_sqlite_profile_checks << ",\n";
    out << "    \"ledger_sqlite_corruption_rejections\": " << c.ledger_sqlite_corruption_rejections << ",\n";
    out << "    \"ledger_sqlite_backup_snapshots\": " << c.ledger_sqlite_backup_snapshots << ",\n";
    out << "    \"ledger_sqlite_snapshot_verifications\": " << c.ledger_sqlite_snapshot_verifications << ",\n";
    out << "    \"ledger_sqlite_snapshot_restores\": " << c.ledger_sqlite_snapshot_restores << ",\n";
    out << "    \"ledger_sqlite_snapshot_manifest_verifications\": " << c.ledger_sqlite_snapshot_manifest_verifications << ",\n";
    out << "    \"ledger_sqlite_trust_profile_digest_verifications\": " << c.ledger_sqlite_trust_profile_digest_verifications << ",\n";
    out << "    \"ledger_sqlite_restore_rollback_guard_checks\": " << c.ledger_sqlite_restore_rollback_guard_checks << ",\n";
    out << "    \"ledger_durable_line_count\": " << c.ledger_durable_line_count << ",\n";
    out << "    \"ledger_durable_head_hash\": \"" << json_escape(c.ledger_durable_head_hash) << "\",\n";
    out << "    \"ledger_host_capability_probe_checks\": " << c.ledger_host_capability_probe_checks << ",\n";
    out << "    \"ledger_backend_factory_selections\": " << c.ledger_backend_factory_selections << ",\n";
    out << "    \"ledger_backend_capability_manifest_checks\": " << c.ledger_backend_capability_manifest_checks << ",\n";
    out << "    \"ledger_backend_capability_manifest_mismatches\": " << c.ledger_backend_capability_manifest_mismatches << ",\n";
    out << "    \"ledger_effect_terminal_transitions\": " << c.ledger_effect_terminal_transitions << ",\n";
    out << "    \"ledger_effect_transition_rejections\": " << c.ledger_effect_transition_rejections << ",\n";
    out << "    \"ledger_effect_transition_line_count\": " << c.ledger_effect_transition_line_count << ",\n";
    out << "    \"ledger_effect_transition_head_hash\": \"" << json_escape(c.ledger_effect_transition_head_hash) << "\",\n";
    out << "    \"ledger_effect_outbox_reserved\": " << c.ledger_effect_outbox_reserved << ",\n";
    out << "    \"ledger_effect_outbox_inflight\": " << c.ledger_effect_outbox_inflight << ",\n";
    out << "    \"ledger_effect_outbox_terminal\": " << c.ledger_effect_outbox_terminal << ",\n";
    out << "    \"ledger_backend_name\": \"" << json_escape(c.ledger_backend_name) << "\",\n";
    out << "    \"streamed_case_lines\": " << c.streamed_case_lines << "\n";
    out << "  },\n";
    out << "  \"failed_samples\": [";
    for (size_t i = 0; i < failed_samples.size(); ++i) {
        if (i) out << ", ";
        out << "\"" << json_escape(failed_samples[i]) << "\"";
    }
    out << "],\n";
    out << "  \"blocked_claim\": \"C++ kernel execution is local compiled OpenSSL-backed evidence, not a deployed gateway, not a production IdP, not TLS/certificate-chain validation, not HSM custody, not broker enforcement, not replicated durable storage, not public transparency inclusion, not custody proof, and not legal finality.\"\n";
    out << "}\n";
    return out.str();
}

}  // namespace anonsync
