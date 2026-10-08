#pragma once

#include <string>

// Test/support entry points for the anonsync_core diagnostic CLI and the
// deterministic corpus wrappers.  Runtime consumers should include
// anonsync_core.hpp instead; this header is intentionally outside that API.
namespace anonsync {

// Exact self-exec modes are dispatched before ordinary CLI parsing. A return
// value equal to this sentinel means argv is not a replay-ledger helper mode.
inline constexpr int kSqliteReplayLedgerSelfExecHelperNotMatched = -1;
int dispatch_sqlite_replay_ledger_self_exec_helper(int argc, char** argv);

int run_sync_domain_model_selftest();
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
int run_sync_peer_ingress_lifecycle_selftest();
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

// Diagnostic CLI helpers.  These intentionally live beside the selftest API
// because the runtime library must not acquire their subprocess/test support.
int run_ledger_host_capability_report(const std::string& report_path);
int run_sqlite_writer_lock_holder(const std::string& ledger_path,
                                  long long seconds);
int run_sqlite_restore_lock_holder(const std::string& ledger_path,
                                   long long seconds);
int run_sqlite_write_gate_holder(const std::string& ledger_path,
                                 long long seconds);
int run_ledger_lock_holder(const std::string& ledger_path, long long seconds);

}  // namespace anonsync
