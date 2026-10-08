#include "anonsync_core_internal.hpp"
#include "sync_sqlite_runtime.hpp"

#include "sqlite_exact_value.hpp"

#include <chrono>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <filesystem>

#include <sqlite3.h>

namespace anonsync {


namespace {

bool json_array_has_string(const Json& arr, const std::string& needle) {
    if (!arr.is_array()) return false;
    for (const auto& item : arr.a) {
        if (item.is_string() && item.s == needle) return true;
    }
    return false;
}

int replay_backend_capability_manifest_version(const Json& root) {
    const std::string format = root.at("format").str();
    const std::string prefix = "anonsync-ledger-backend-capabilities-v";
    if (!starts_with(format, prefix)) throw std::runtime_error("replay-ledger backend capability manifest has unsupported format");
    const std::string suffix = format.substr(prefix.size());
    if (suffix.empty() || !std::all_of(suffix.begin(), suffix.end(), [](unsigned char c) { return c >= '0' && c <= '9'; })) {
        throw std::runtime_error("replay-ledger backend capability manifest has unsupported format");
    }
    int version = 0;
    try { version = std::stoi(suffix); }
    catch (...) { throw std::runtime_error("replay-ledger backend capability manifest has unsupported format"); }
    return version;
}

}  // namespace

std::string validate_replay_backend_capability_manifest(const std::string& manifest_text,
                                                        const std::string& backend_name,
                                                        const std::string& commit_mode,
                                                        const std::string& ledger_path) {
    Json root = parse_json_text(manifest_text);
    const int version = replay_backend_capability_manifest_version(root);
    if (version < 1 || version > 42) throw std::runtime_error("replay-ledger backend capability manifest has unsupported format");
    const Json& backends = root.at("backends");
    if (!backends.is_object()) throw std::runtime_error("replay-ledger backend capability manifest missing backends object");
    const Json& selected = backends.at(backend_name);
    if (!selected.is_object()) throw std::runtime_error("replay-ledger backend capability manifest does not describe selected backend: " + backend_name);
    if (selected.at("backend_name").str() != backend_name) {
        throw std::runtime_error("replay-ledger backend capability manifest backend_name mismatch for " + backend_name);
    }
    if (selected.at("status").str() != "supported") {
        throw std::runtime_error("replay-ledger backend capability manifest marks backend unsupported: " + backend_name);
    }
    if (!json_array_has_string(selected.at("commit_modes"), commit_mode)) {
        throw std::runtime_error("replay-ledger backend capability manifest does not allow commit mode " + commit_mode + " for " + backend_name);
    }
    if (selected.at("requires_nonempty_ledger_path").boolean(false) && ledger_path.empty()) {
        throw std::runtime_error("replay-ledger backend capability manifest requires a nonempty ledger path for " + backend_name);
    }
    if (backend_name == "sqlite-wal") {
        if (!selected.at("requires_sqlite_wal").boolean(false)) throw std::runtime_error("sqlite-wal capability manifest does not require WAL mode");
        if (!selected.at("integrity_check_on_load").boolean(false)) throw std::runtime_error("sqlite-wal capability manifest does not require integrity_check on load");
        if (!selected.at("profile_check_on_load").boolean(false)) throw std::runtime_error("sqlite-wal capability manifest does not require backend_profile check on load");
        if (!selected.at("reject_symlink_sidecars").boolean(false)) throw std::runtime_error("sqlite-wal capability manifest does not require sidecar symlink rejection");
        if (version >= 2) {
            if (!selected.at("sqlite_backup_api_snapshot_supported").boolean(false)) throw std::runtime_error("sqlite-wal v2 capability manifest must require sqlite3_backup snapshot support");
            if (!selected.at("snapshot_restore_verification_required").boolean(false)) throw std::runtime_error("sqlite-wal v2 capability manifest must require snapshot restore verification");
            if (!selected.at("host_capability_probe_required").boolean(false)) throw std::runtime_error("sqlite-wal v2 capability manifest must require host capability probing");
            if (!selected.at("requires_sqlite_threadsafe").boolean(false)) throw std::runtime_error("sqlite-wal v2 capability manifest must require a threadsafe SQLite build");
        }
        if (version >= 3) {
            if (!selected.at("snapshot_hostile_corpus_required").boolean(false)) throw std::runtime_error("sqlite-wal v3 capability manifest must require hostile snapshot corpus coverage");
            if (!selected.at("host_capability_report_emit_supported").boolean(false)) throw std::runtime_error("sqlite-wal v3 capability manifest must support host capability report emission");
            if (!selected.at("snapshot_profile_hash_chain_verification_required").boolean(false)) throw std::runtime_error("sqlite-wal v3 capability manifest must require profile/hash-chain snapshot verification");
        }
        if (version >= 4) {
            if (!selected.at("snapshot_restore_command_supported").boolean(false)) throw std::runtime_error("sqlite-wal v4 capability manifest must support compiled snapshot restore command");
            if (!selected.at("snapshot_restore_hostile_corpus_required").boolean(false)) throw std::runtime_error("sqlite-wal v4 capability manifest must require hostile snapshot restore corpus coverage");
            if (!selected.at("restore_profile_hash_chain_verification_required").boolean(false)) throw std::runtime_error("sqlite-wal v4 capability manifest must require restore profile/hash-chain verification");
        }
        if (version >= 5) {
            if (!selected.at("signed_snapshot_manifest_required").boolean(false)) throw std::runtime_error("sqlite-wal v5 capability manifest must require signed snapshot manifests");
            if (!selected.at("restore_root_trust_profile_required").boolean(false)) throw std::runtime_error("sqlite-wal v5 capability manifest must require restore-root trust profiles");
            if (!selected.at("snapshot_manifest_digest_binding_required").boolean(false)) throw std::runtime_error("sqlite-wal v5 capability manifest must require snapshot digest binding");
            if (!selected.at("snapshot_manifest_head_binding_required").boolean(false)) throw std::runtime_error("sqlite-wal v5 capability manifest must require snapshot head binding");
        }
        if (version >= 6) {
            if (selected.at("snapshot_manifest_format").str() != "anonsync-sqlite-snapshot-manifest-v2") throw std::runtime_error("sqlite-wal v6 capability manifest must require snapshot manifest v2");
            if (!selected.at("snapshot_manifest_issued_at_signed").boolean(false)) throw std::runtime_error("sqlite-wal v6 capability manifest must require signed manifest issued-at");
            if (!selected.at("snapshot_manifest_trust_window_required").boolean(false)) throw std::runtime_error("sqlite-wal v6 capability manifest must require restore-root trust windows");
            if (!selected.at("snapshot_manifest_subject_binding_required").boolean(false)) throw std::runtime_error("sqlite-wal v6 capability manifest must require manifest-subject binding");
            if (!selected.at("snapshot_manifest_revision_allowlist_required").boolean(false)) throw std::runtime_error("sqlite-wal v6 capability manifest must require revision allowlists");
        }
        if (version >= 7) {
            if (selected.at("snapshot_trust_profile_format").str() != "anonsync-sqlite-snapshot-trust-profile-v3") throw std::runtime_error("sqlite-wal v7 capability manifest must require snapshot trust profile v3");
            if (!selected.at("snapshot_manifest_canonical_utc_required").boolean(false)) throw std::runtime_error("sqlite-wal v7 capability manifest must require canonical UTC manifest times");
            if (!selected.at("snapshot_manifest_staleness_window_required").boolean(false)) throw std::runtime_error("sqlite-wal v7 capability manifest must require manifest staleness window checks");
            if (!selected.at("restore_root_rotation_overlap_supported").boolean(false)) throw std::runtime_error("sqlite-wal v7 capability manifest must support restore-root rotation/overlap");
            if (!selected.at("snapshot_manifest_duplicate_signer_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v7 capability manifest must require duplicate signer rejection");
        }
        if (version >= 8) {
            if (!selected.at("snapshot_trust_profile_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v8 capability manifest must require trust-profile digest pinning");
            if (selected.at("snapshot_trust_profile_digest_algorithm").str() != "sha256") throw std::runtime_error("sqlite-wal v8 capability manifest must require sha256 trust-profile digest pins");
            if (selected.at("snapshot_trust_profile_pin_source").str() != "operator-cli-argument") throw std::runtime_error("sqlite-wal v8 capability manifest must bind trust-profile pin source to operator CLI argument");
        }
        if (version >= 9) {
            if (!selected.at("snapshot_restore_rollback_guard_required").boolean(false)) throw std::runtime_error("sqlite-wal v9 capability manifest must require restore rollback guard checks");
            if (!selected.at("snapshot_restore_refuses_older_destination_overwrite").boolean(false)) throw std::runtime_error("sqlite-wal v9 capability manifest must reject older snapshot overwrites");
            if (!selected.at("snapshot_restore_refuses_divergent_same_height_overwrite").boolean(false)) throw std::runtime_error("sqlite-wal v9 capability manifest must reject divergent same-height snapshot overwrites");
            if (!selected.at("snapshot_restore_forward_only_unless_destination_removed").boolean(false)) throw std::runtime_error("sqlite-wal v9 capability manifest must require forward-only restore unless destination is removed");
        }
        if (version >= 10) {
            if (!selected.at("snapshot_restore_atomic_staging_required").boolean(false)) throw std::runtime_error("sqlite-wal v10 capability manifest must require atomic restore staging");
            if (!selected.at("snapshot_restore_temp_verified_before_replace").boolean(false)) throw std::runtime_error("sqlite-wal v10 capability manifest must require temp restore verification before replacement");
            if (!selected.at("snapshot_restore_destination_checkpoint_before_replace").boolean(false)) throw std::runtime_error("sqlite-wal v10 capability manifest must require destination checkpoint before replacement");
            if (!selected.at("snapshot_restore_parent_fsync_after_replace").boolean(false)) throw std::runtime_error("sqlite-wal v10 capability manifest must require parent directory fsync after replacement");
            if (!selected.at("snapshot_restore_pre_replace_fault_keeps_destination").boolean(false)) throw std::runtime_error("sqlite-wal v10 capability manifest must require pre-replace fault preservation of destination");
        }
        if (version >= 11) {
            if (!selected.at("snapshot_restore_lock_required").boolean(false)) throw std::runtime_error("sqlite-wal v11 capability manifest must require restore-side locking");
            if (!selected.at("snapshot_restore_lock_sidecar_symlink_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v11 capability manifest must require restore-lock symlink rejection");
            if (!selected.at("snapshot_restore_concurrent_restore_contention_required").boolean(false)) throw std::runtime_error("sqlite-wal v11 capability manifest must require concurrent restore contention fail-closed coverage");
            if (!selected.at("snapshot_restore_stale_regular_lock_tolerated").boolean(false)) throw std::runtime_error("sqlite-wal v11 capability manifest must tolerate stale regular lock sidecars only when unlocked");
        }
        if (version >= 12) {
            if (!selected.at("snapshot_restore_manifest_reverified_inside_restore").boolean(false)) throw std::runtime_error("sqlite-wal v12 capability manifest must require manifest re-verification inside restore");
            if (!selected.at("snapshot_restore_source_digest_stability_required").boolean(false)) throw std::runtime_error("sqlite-wal v12 capability manifest must require source digest stability checks around staged backup");
            if (!selected.at("snapshot_restore_source_head_bound_to_manifest_required").boolean(false)) throw std::runtime_error("sqlite-wal v12 capability manifest must require source head binding to verified manifest");
            if (!selected.at("snapshot_restore_source_line_count_bound_to_manifest_required").boolean(false)) throw std::runtime_error("sqlite-wal v12 capability manifest must require source line-count binding to verified manifest");
        }
        if (version >= 13) {
            if (!selected.at("sqlite_wal_backend_write_gate_lifetime_required").boolean(false)) throw std::runtime_error("sqlite-wal v13 capability manifest must require backend-lifetime write-gate locking");
            if (!selected.at("snapshot_restore_write_gate_required").boolean(false)) throw std::runtime_error("sqlite-wal v13 capability manifest must require restore write-gate locking");
            if (!selected.at("snapshot_restore_write_gate_sidecar_symlink_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v13 capability manifest must require write-gate sidecar symlink rejection");
            if (!selected.at("snapshot_restore_blocks_active_sqlite_backend_load").boolean(false)) throw std::runtime_error("sqlite-wal v13 capability manifest must require restore rejection while a C++ SQLite backend has the destination loaded");
        }
        if (version >= 14) {
            if (!selected.at("snapshot_restore_append_continuity_guard_required").boolean(false)) throw std::runtime_error("sqlite-wal v14 capability manifest must require append-prefix continuity for snapshot restore");
            if (!selected.at("snapshot_restore_refuses_non_extending_newer_snapshot").boolean(false)) throw std::runtime_error("sqlite-wal v14 capability manifest must reject newer snapshots that do not extend the destination prefix");
            if (!selected.at("snapshot_restore_destination_prefix_head_binding_required").boolean(false)) throw std::runtime_error("sqlite-wal v14 capability manifest must bind destination head to the source snapshot prefix before replacement");
        }
        if (version >= 15) {
            if (!selected.at("snapshot_restore_current_capability_manifest_required").boolean(false)) throw std::runtime_error("sqlite-wal v15 capability manifest must require the current capability manifest for restore");
            if (!selected.at("snapshot_restore_missing_capability_manifest_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v15 capability manifest must require missing capability-manifest rejection for restore");
            if (!selected.at("snapshot_restore_capability_downgrade_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v15 capability manifest must require capability downgrade rejection for restore");
            if (!selected.at("snapshot_restore_unsigned_path_disabled").boolean(false)) throw std::runtime_error("sqlite-wal v15 capability manifest must disable unsigned SQLite snapshot restore");
            if (selected.at("snapshot_restore_minimum_capability_version").integer(0) < 15) throw std::runtime_error("sqlite-wal v15+ capability manifest must set minimum restore capability version at least 15");
        }
        if (version >= 16) {
            if (version < 20) {
                if (selected.at("ledger_schema_version").integer(0) != 3) throw std::runtime_error("sqlite-wal v16 capability manifest must require ledger schema version 3");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v2-verified-claims") throw std::runtime_error("sqlite-wal v16 capability manifest must require verified-claims entry material v2");
            }
            if (!selected.at("ledger_operation_id_from_verified_claims_required").boolean(false)) throw std::runtime_error("sqlite-wal v16 capability manifest must source operation_id from verified claims");
            if (!selected.at("ledger_contract_digest_from_verified_claims_required").boolean(false)) throw std::runtime_error("sqlite-wal v16 capability manifest must source contract digest from verified claims");
            if (!selected.at("ledger_contract_digest_lower_hex_sha256_required").boolean(false)) throw std::runtime_error("sqlite-wal v16 capability manifest must require lowercase SHA-256 contract digests");
            if (!selected.at("ledger_legacy_empty_contract_digest_rows_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v16 capability manifest must reject legacy empty contract-digest rows");
            if (version == 16 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 16) throw std::runtime_error("sqlite-wal v16 capability manifest must set minimum restore capability version 16");
        }
        if (version >= 17) {
            if (!selected.at("snapshot_manifest_revision_fields_signed_required").boolean(false)) throw std::runtime_error("sqlite-wal v17 capability manifest must require signed manifest revision fields");
            if (!selected.at("snapshot_manifest_outer_revision_payload_match_required").boolean(false)) throw std::runtime_error("sqlite-wal v17 capability manifest must require outer revision fields to match signed payload");
            if (!selected.at("snapshot_manifest_allowlist_uses_signed_payload_revision_required").boolean(false)) throw std::runtime_error("sqlite-wal v17 capability manifest must require manifest allowlist checks against signed payload revision");
            if (!selected.at("snapshot_manifest_parent_revision_signed_required").boolean(false)) throw std::runtime_error("sqlite-wal v17 capability manifest must require signed manifest parent revision");
            if (version == 17 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 17) throw std::runtime_error("sqlite-wal v17 capability manifest must set minimum restore capability version 17");
        }
        if (version >= 18) {
            if (!selected.at("ledger_async_event_identity_replay_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v18 capability manifest must require durable async CloudEvents source/id replay rejection");
            if (!selected.at("ledger_async_event_identity_unique_index_required").boolean(false)) throw std::runtime_error("sqlite-wal v18 capability manifest must require a unique async CloudEvents source/id index");
            if (!selected.at("ledger_async_event_identity_reload_duplicate_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v18 capability manifest must reject duplicate async event identities during reload");
            if (!selected.at("ledger_async_event_identity_source_id_required").boolean(false)) throw std::runtime_error("sqlite-wal v18 capability manifest must require CloudEvents source/id material for async ledger rows");
            if (version == 18 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 18) throw std::runtime_error("sqlite-wal v18 capability manifest must set minimum restore capability version 18");
        }
        if (version >= 19) {
            if (!selected.at("snapshot_readonly_verifier_required").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must require the dedicated read-only snapshot verifier");
            if (!selected.at("snapshot_readonly_verifier_schema_allowlist_required").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must require snapshot schema allowlisting");
            if (!selected.at("snapshot_readonly_verifier_defensive_profile_required").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must require the defensive read-only SQLite profile");
            if (!selected.at("snapshot_readonly_verifier_rejects_mutable_loader_sidecars").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must reject mutable-loader sidecar creation during snapshot verification");
            if (!selected.at("snapshot_manifest_verification_uses_readonly_snapshot_verifier").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must use the read-only verifier during manifest verification");
            if (!selected.at("snapshot_restore_source_staged_destination_readonly_verifier_required").boolean(false)) throw std::runtime_error("sqlite-wal v19 capability manifest must require read-only verification of restore source, staged temp, and destination");
            if (version == 19 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 19) throw std::runtime_error("sqlite-wal v19 capability manifest must set minimum restore capability version 19");
        }
        if (version >= 20) {
            if (!selected.at("ledger_effect_idempotency_key_required").boolean(false)) throw std::runtime_error("sqlite-wal v20 capability manifest must require effect idempotency keys");
            if (!selected.at("ledger_effect_state_prepared_required").boolean(false)) throw std::runtime_error("sqlite-wal v20 capability manifest must require prepared effect state rows");
            if (!selected.at("ledger_duplicate_effect_idempotency_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v20 capability manifest must reject duplicate prepared effect idempotency keys");
            if (version == 20) {
                if (selected.at("ledger_schema_version").integer(0) != 4) throw std::runtime_error("sqlite-wal v20 capability manifest must require ledger schema version 4");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v3-effect-prepared") throw std::runtime_error("sqlite-wal v20 capability manifest must require prepared-effect entry material v3");
                if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 20) throw std::runtime_error("sqlite-wal v20 capability manifest must set minimum restore capability version 20");
            }
        }
        if (version >= 21) {
            if (version < 23) {
                if (selected.at("ledger_schema_version").integer(0) != 5) throw std::runtime_error("sqlite-wal v21/v22 capability manifest must require ledger schema version 5");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v4-effect-transition-chain") throw std::runtime_error("sqlite-wal v21/v22 capability manifest must require effect-transition entry material v4");
            } else if (version == 23) {
                if (selected.at("ledger_schema_version").integer(0) != 6) throw std::runtime_error("sqlite-wal v23 capability manifest must require ledger schema version 6");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v5-effect-transition-prepared-binding") throw std::runtime_error("sqlite-wal v23 capability manifest must require prepared-entry-bound effect-transition material v5");
            }
            if (!selected.at("ledger_effect_transition_chain_required").boolean(false)) throw std::runtime_error("sqlite-wal v21 capability manifest must require an append-only effect transition chain");
            if (!selected.at("ledger_effect_terminal_states_required").boolean(false)) throw std::runtime_error("sqlite-wal v21 capability manifest must require terminal effect states");
            if (!selected.at("ledger_effect_transition_duplicate_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v21 capability manifest must reject duplicate terminal effect transitions");
            if (!selected.at("snapshot_readonly_verifier_checks_effect_transitions").boolean(false)) throw std::runtime_error("sqlite-wal v21 capability manifest must require read-only verification of effect transitions");
            if (version == 21 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 21) throw std::runtime_error("sqlite-wal v21 capability manifest must set minimum restore capability version 21");
        }
        if (version >= 22) {
            if (!selected.at("ledger_effect_pending_report_supported").boolean(false)) throw std::runtime_error("sqlite-wal v22 capability manifest must support pending-effect recovery reports");
            if (!selected.at("ledger_effect_pending_report_readonly_verifier_required").boolean(false)) throw std::runtime_error("sqlite-wal v22 capability manifest must require read-only verification before pending-effect reports");
            if (!selected.at("ledger_effect_pending_report_excludes_terminal_effects").boolean(false)) throw std::runtime_error("sqlite-wal v22 capability manifest must exclude terminal effects from pending reports");
            if (version == 22 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 22) throw std::runtime_error("sqlite-wal v22 capability manifest must set minimum restore capability version 22");
        }
        if (version >= 23) {
            if (version == 23) {
                if (selected.at("ledger_schema_version").integer(0) != 6) throw std::runtime_error("sqlite-wal v23 capability manifest must require ledger schema version 6");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v5-effect-transition-prepared-binding") throw std::runtime_error("sqlite-wal v23 capability manifest must require prepared-entry-bound effect-transition material v5");
            }
            if (!selected.at("ledger_effect_transition_prepared_entry_binding_required").boolean(false)) throw std::runtime_error("sqlite-wal v23 capability manifest must require terminal transitions to bind prepared ledger entries");
            if (!selected.at("ledger_effect_transition_prepared_sequence_required").boolean(false)) throw std::runtime_error("sqlite-wal v23 capability manifest must require prepared ledger sequence on terminal transition");
            if (!selected.at("ledger_effect_transition_prepared_entry_hash_required").boolean(false)) throw std::runtime_error("sqlite-wal v23 capability manifest must require prepared entry hash on terminal transition");
            if (!selected.at("ledger_effect_pending_report_includes_entry_hash").boolean(false)) throw std::runtime_error("sqlite-wal v23 capability manifest must require pending reports to include prepared entry hashes");
            if (!selected.at("snapshot_readonly_verifier_checks_effect_transition_prepared_binding").boolean(false)) throw std::runtime_error("sqlite-wal v23 capability manifest must require read-only verification of transition prepared-entry binding");
            if (version == 23 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 23) throw std::runtime_error("sqlite-wal v23 capability manifest must set minimum restore capability version 23");
        }
        if (version >= 24) {
            if (version < 26) {
                if (selected.at("ledger_schema_version").integer(0) != 7) throw std::runtime_error("sqlite-wal v24/v25 capability manifest must require ledger schema version 7");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v6-signed-effect-transition-intent") throw std::runtime_error("sqlite-wal v24/v25 capability manifest must require signed effect-transition intent material v6");
            } else if (version < 28) {
                if (selected.at("ledger_schema_version").integer(0) != 8) throw std::runtime_error("sqlite-wal v26/v27 capability manifest must require ledger schema version 8");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent") throw std::runtime_error("sqlite-wal v26/v27 capability manifest must require ledger-instance-bound effect-transition material v7");
            } else if (version < 29) {
                if (selected.at("ledger_schema_version").integer(0) != 9) throw std::runtime_error("sqlite-wal v28 capability manifest must require ledger schema version 9");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent") throw std::runtime_error("sqlite-wal v28 capability manifest must require ledger-instance-bound effect-transition material v7");
            } else {
                if (selected.at("ledger_schema_version").integer(0) != 10) throw std::runtime_error("sqlite-wal v29 capability manifest must require ledger schema version 10");
                if (selected.at("ledger_entry_material_version").str() != "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent") throw std::runtime_error("sqlite-wal v29 capability manifest must require ledger-instance-bound effect-transition material v7");
            }
            if (!selected.at("ledger_effect_transition_signed_intent_required").boolean(false)) throw std::runtime_error("sqlite-wal v24 capability manifest must require signed terminal transition intents");
            if (!selected.at("ledger_effect_transition_intent_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v24 capability manifest must require transition-intent trust-profile digest pins");
            if (!selected.at("ledger_effect_transition_intent_binds_prepared_ledger_head").boolean(false)) throw std::runtime_error("sqlite-wal v24 capability manifest must require transition intents to bind prepared ledger head");
            if (!selected.at("ledger_effect_transition_intent_binds_transition_head").boolean(false)) throw std::runtime_error("sqlite-wal v24 capability manifest must require transition intents to bind effect transition head");
            if (!selected.at("snapshot_readonly_verifier_checks_effect_transition_intent_metadata").boolean(false)) throw std::runtime_error("sqlite-wal v24 capability manifest must require read-only verification of signed transition intent metadata");
            if (version == 24 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 24) throw std::runtime_error("sqlite-wal v24 capability manifest must set minimum restore capability version 24");
            if (version == 25) {
                if (!selected.at("ledger_effect_transition_raw_public_api_disabled").boolean(false)) throw std::runtime_error("sqlite-wal v25 capability manifest must disable raw terminal transition API");
                if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 25) throw std::runtime_error("sqlite-wal v25 capability manifest must set minimum restore capability version 25");
            }
            if (version >= 26) {
                if (!selected.at("ledger_effect_transition_raw_public_api_disabled").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must keep raw terminal transition API disabled");
                if (!selected.at("ledger_instance_id_required").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require a per-ledger instance id");
                if (!selected.at("ledger_effect_transition_intent_binds_ledger_instance_id").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require transition intents to bind ledger_instance_id");
                if (!selected.at("ledger_effect_transition_row_binds_ledger_instance_id").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require transition rows to bind ledger_instance_id");
                if (!selected.at("ledger_effect_transition_intent_id_unique").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require unique signed transition intent ids");
                if (!selected.at("ledger_effect_pending_report_includes_ledger_instance_id").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require pending-effect reports to include ledger_instance_id");
                if (!selected.at("snapshot_readonly_verifier_checks_ledger_instance_binding").boolean(false)) throw std::runtime_error("sqlite-wal v26 capability manifest must require read-only ledger-instance binding checks");
                if (version == 26 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 26) throw std::runtime_error("sqlite-wal v26 capability manifest must set minimum restore capability version 26");
                if (version >= 27) {
                    if (selected.at("security_tuple_framing").str() != "anonsync-length-prefixed-tuple-v1") throw std::runtime_error("sqlite-wal v27 capability manifest must require length-prefixed security tuples");
                    if (selected.at("proof_binding_material_version").str() != "anonsync-proof-binding-v2-lp-hmac-sha256") throw std::runtime_error("sqlite-wal v27 capability manifest must require proof-binding material v2");
                    if (selected.at("cloud_event_identity_material_version").str() != "anonsync-cloud-event-identity-v2") throw std::runtime_error("sqlite-wal v27 capability manifest must require CloudEvents identity material v2");
                    if (selected.at("effect_idempotency_material_version").str() != "anonsync-effect-idempotency-v2") throw std::runtime_error("sqlite-wal v27 capability manifest must require effect-idempotency material v2");
                    if (selected.at("legacy_effect_idempotency_fallback_material_version").str() != "anonsync-effect-idempotency-legacy-v1") throw std::runtime_error("sqlite-wal v27 capability manifest must frame legacy effect-idempotency fallback material");
                    if (selected.at("ledger_instance_id_generation").str() != "anonsync-sqlite-ledger-instance-v2-openssl-rand") throw std::runtime_error("sqlite-wal v27 capability manifest must require OpenSSL-random ledger instance ids");
                    if (!selected.at("ledger_instance_id_csprng_failure_fails_closed").boolean(false)) throw std::runtime_error("sqlite-wal v27 capability manifest must fail closed on ledger instance CSPRNG failure");
                    if (!selected.at("case_insensitive_security_metadata_duplicate_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v27 capability manifest must reject duplicate case-insensitive security metadata");
                    if (!selected.at("security_metadata_control_character_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v27 capability manifest must reject control characters in security metadata and event identity");
                    if (version == 27 && selected.at("snapshot_restore_minimum_capability_version").integer(0) != 27) throw std::runtime_error("sqlite-wal v27 capability manifest must set minimum restore capability version 27");
                    if (version >= 28) {
                        if (version < 29 && selected.at("ledger_schema_version").integer(0) != 9) throw std::runtime_error("sqlite-wal v28 capability manifest must require ledger schema version 9");
                        if (version >= 29 && selected.at("ledger_schema_version").integer(0) != 10) throw std::runtime_error("sqlite-wal v29+ capability manifest must require ledger schema version 10");
                        if (selected.at("effect_outbox_material_version").str() != "anonsync-sqlite-effect-outbox-v1") throw std::runtime_error("sqlite-wal v28 capability manifest must require effect outbox material v1");
                        if (!selected.at("effect_outbox_inserted_atomically_with_prepared_entry").boolean(false)) throw std::runtime_error("sqlite-wal v28 capability manifest must require atomic prepared-entry/outbox insertion");
                        if (!selected.at("effect_outbox_terminal_update_bound_to_signed_transition").boolean(false)) throw std::runtime_error("sqlite-wal v28 capability manifest must bind terminal outbox updates to signed transitions");
                        if (!selected.at("snapshot_readonly_verifier_checks_effect_outbox").boolean(false)) throw std::runtime_error("sqlite-wal v28 capability manifest must require read-only effect outbox verification");
                        const std::string expected_pending_report = version >= 29 ? "anonsync-sqlite-effect-pending-report-v5-outbox-claim" : "anonsync-sqlite-effect-pending-report-v4-outbox";
                        if (selected.at("effect_pending_report_format").str() != expected_pending_report) throw std::runtime_error("sqlite-wal capability manifest has unsupported pending-effect report format");
                        if (version >= 29) {
                            if (selected.at("effect_outbox_claim_material_version").str() != "anonsync-sqlite-effect-outbox-claim-v1") throw std::runtime_error("sqlite-wal v29 capability manifest must require effect outbox claim material v1");
                            if (!selected.at("effect_outbox_inflight_lease_supported").boolean(false)) throw std::runtime_error("sqlite-wal v29 capability manifest must support inflight outbox leases");
                            if (!selected.at("effect_outbox_stale_lease_reclaim_supported").boolean(false)) throw std::runtime_error("sqlite-wal v29 capability manifest must support stale lease reclaim");
                            if (!selected.at("snapshot_readonly_verifier_checks_effect_outbox_claims").boolean(false)) throw std::runtime_error("sqlite-wal v29 capability manifest must require read-only verification of outbox claims");
                            if (version >= 30) {
                                if (!selected.at("effect_relay_once_command_supported").boolean(false)) throw std::runtime_error("sqlite-wal v30 capability manifest must support effect relay once command");
                                const std::string expected_relay_report = version >= 32 ? "anonsync-sqlite-effect-relay-report-v3-handle-boundary" : (version >= 31 ? "anonsync-sqlite-effect-relay-report-v2-configured-boundary" : "anonsync-sqlite-effect-relay-report-v1");
                                if (selected.at("effect_relay_report_format").str() != expected_relay_report) throw std::runtime_error("sqlite-wal capability manifest has unsupported relay report format");
                                const std::string expected_downstream_store_format = version >= 41 ? "anonsync-relay-downstream-store-v2-provenance-bound" : "anonsync-relay-downstream-store-v1";
                                if (selected.at("effect_relay_downstream_store_format").str() != expected_downstream_store_format) throw std::runtime_error("sqlite-wal v30+ capability manifest must require the active relay downstream store format");
                                if (!selected.at("effect_relay_signed_transition_intent_required").boolean(false)) throw std::runtime_error("sqlite-wal v30 capability manifest must require signed relay terminal transition intents");
                                if (!selected.at("effect_relay_transition_trust_profile_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v30 capability manifest must require digest-pinned relay transition trust profile");
                                if (!selected.at("effect_relay_reconciliation_after_downstream_apply_gap_supported").boolean(false)) throw std::runtime_error("sqlite-wal v30 capability manifest must support reconciliation after downstream apply gap");
                                if (!selected.at("effect_relay_injected_crash_after_downstream_selftest_required").boolean(false)) throw std::runtime_error("sqlite-wal v30 capability manifest must require injected crash-after-downstream relay selftest");
                                if (version >= 31) {
                                    if (selected.at("effect_relay_adapter_config_format").str() != "anonsync-effect-relay-adapter-config-v1") throw std::runtime_error("sqlite-wal v31 capability manifest must require relay adapter config v1");
                                    if (!selected.at("effect_relay_adapter_config_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v31 capability manifest must require digest-pinned relay adapter config");
                                    if (!selected.at("effect_relay_operator_configured_boundary_required").boolean(false)) throw std::runtime_error("sqlite-wal v31 capability manifest must require an operator-configured relay boundary");
                                    if (!selected.at("effect_relay_config_binds_adapter_worker_lease_terminal_signer_trust_downstream").boolean(false)) throw std::runtime_error("sqlite-wal v31 capability manifest must bind adapter, worker, lease, terminal state, signer, trust pin, and downstream path in config");
                                    if (!selected.at("effect_relay_legacy_cli_marked_nonproduction").boolean(false)) throw std::runtime_error("sqlite-wal v31 capability manifest must mark legacy relay CLI as non-production harness");
                                    if (version >= 32) {
                                        if (selected.at("effect_relay_config_registry_format").str() != "anonsync-effect-relay-config-registry-v1") throw std::runtime_error("sqlite-wal v32 capability manifest must require relay config registry v1");
                                        if (!selected.at("effect_relay_config_registry_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v32 capability manifest must require digest-pinned relay config registry");
                                        if (!selected.at("effect_relay_handle_command_supported").boolean(false)) throw std::runtime_error("sqlite-wal v32 capability manifest must support handle-bound relay command");
                                        if (!selected.at("effect_relay_request_selects_handle_only").boolean(false)) throw std::runtime_error("sqlite-wal v32 capability manifest must require caller selection by handle only");
                                        if (!selected.at("effect_relay_registry_resolves_adapter_config_digest").boolean(false)) throw std::runtime_error("sqlite-wal v32 capability manifest must resolve adapter config digest through the registry");
                                        if (version >= 33) {
                                            if (selected.at("ingress_reservation_profile_format").str() != "anonsync-ingress-reservation-profile-v1") throw std::runtime_error("sqlite-wal v33 capability manifest must require ingress reservation profile v1");
                                            if (selected.at("ingress_reservation_request_format").str() != "anonsync-ingress-reservation-request-v1") throw std::runtime_error("sqlite-wal v33 capability manifest must require ingress reservation request v1");
                                            if (selected.at("ingress_reservation_report_format").str() != "anonsync-ingress-reservation-report-v1") throw std::runtime_error("sqlite-wal v33 capability manifest must require ingress reservation report v1");
                                            if (!selected.at("ingress_reservation_command_supported").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must support profile-bound ingress reservation command");
                                            if (!selected.at("ingress_profile_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must require digest-pinned ingress profile");
                                            if (!selected.at("ingress_request_selects_handle_only").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must require ingress request selection by handle only");
                                            if (!selected.at("ingress_operator_paths_loaded_from_profile").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must load operator paths only from profile");
                                            if (!selected.at("ingress_request_forbidden_operator_field_rejection_required").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must reject operator fields in ingress requests");
                                            if (!selected.at("ingress_request_failure_injection_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must reject ingress failure injection");
                                            if (!selected.at("ingress_request_ledger_mode_policy_envelope_constrained_by_profile").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must constrain ingress ledger-mode and policy-envelope selection by profile");
                                            if (!selected.at("ingress_controls_contracts_capability_digest_pins_required").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must require profile digest pins for controls, contracts, and backend capabilities");
                                            if (!selected.at("ingress_report_binds_profile_request_and_reserved_outbox").boolean(false)) throw std::runtime_error("sqlite-wal v33 capability manifest must bind ingress report to profile, request, and reserved outbox evidence");
                                            if (version >= 34) {
                                                std::string expected_service_config_format = "anonsync-ingress-service-config-v1";
                                                std::string expected_service_report_format = "anonsync-ingress-reservation-report-v2-service-boundary";
                                                if (version >= 40) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v6-trusted-context-separated";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v8-ledger-integrated-replay";
                                                } else if (version >= 39) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v6-trusted-context-separated";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v7-trusted-context-boundary";
                                                } else if (version >= 38) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v5-asymmetric-sender-replay-cache-bound";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v6-asymmetric-sender-cache-boundary";
                                                } else if (version >= 37) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v4-asymmetric-sender-replay-cache";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v5-asymmetric-sender-replay-boundary";
                                                } else if (version >= 36) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v3-asymmetric-sender-possession";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v4-asymmetric-sender-boundary";
                                                } else if (version >= 35) {
                                                    expected_service_config_format = "anonsync-ingress-service-config-v2-sender-possession";
                                                    expected_service_report_format = "anonsync-ingress-reservation-report-v3-sender-boundary";
                                                }
                                                if (selected.at("ingress_service_config_format").str() != expected_service_config_format) throw std::runtime_error("sqlite-wal v34+ capability manifest must require the current ingress service config format");
                                                if (selected.at("ingress_reservation_service_report_format").str() != expected_service_report_format) throw std::runtime_error("sqlite-wal v34+ capability manifest must require the current service-bound ingress report format");
                                                if (!selected.at("ingress_reservation_service_api_supported").boolean(false)) throw std::runtime_error("sqlite-wal v34 capability manifest must support service-bound ingress reservation API");
                                                if (!selected.at("ingress_service_config_digest_pin_required").boolean(false)) throw std::runtime_error("sqlite-wal v34 capability manifest must require digest-pinned ingress service config");
                                                if (!selected.at("ingress_service_config_pins_profile").boolean(false)) throw std::runtime_error("sqlite-wal v34 capability manifest must require service config to pin an ingress profile");
                                                if (!selected.at("ingress_request_no_filesystem_operands_required").boolean(false)) throw std::runtime_error("sqlite-wal v34 capability manifest must require request-side ingress without filesystem operands");
                                                if (!selected.at("ingress_service_report_binds_service_profile_request_and_reservation").boolean(false)) throw std::runtime_error("sqlite-wal v34 capability manifest must bind service, profile, request, and reservation evidence");
                                                if (version >= 35) {
                                                    if (!selected.at("ingress_service_sender_possession_required").boolean(false)) throw std::runtime_error("sqlite-wal v35+ capability manifest must require sender-possession before ingress reservation");
                                                    if (!selected.at("ingress_sender_possession_binds_service_profile_request_principal_case").boolean(false)) throw std::runtime_error("sqlite-wal v35+ capability manifest must bind sender proof to service/profile/request/principal/case");
                                                    if (!selected.at("ingress_service_rejects_bad_sender_possession_before_append").boolean(false)) throw std::runtime_error("sqlite-wal v35+ capability manifest must reject bad sender possession before append");
                                                    if (version >= 36) {
                                                        if (version >= 37) {
                                                            const std::string expected_sender_material = version >= 39
                                                                ? "anonsync-ingress-sender-possession-v5-lp-rs256-trusted-context"
                                                                : (version >= 38 ? "anonsync-ingress-sender-possession-v4-lp-rs256-nonce-cache"
                                                                                 : "anonsync-ingress-sender-possession-v3-lp-rs256-nonce");
                                                            if (selected.at("ingress_sender_possession_material_version").str() != expected_sender_material) throw std::runtime_error("sqlite-wal v37+ capability manifest must require the current sender possession material");
                                                            if (!selected.at("ingress_sender_replay_cache_required").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must require a sender replay cache");
                                                            const std::string expected_replay_cache_format = version >= 40
                                                                ? "anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction"
                                                                : (version >= 39 ? "anonsync-ingress-sender-replay-cache-v4-sqlite-trusted-context-nonce-window-unique"
                                                                                 : (version >= 38 ? "anonsync-ingress-sender-replay-cache-v2-sqlite-bound-instance"
                                                                                                  : "anonsync-ingress-sender-replay-cache-v1-sqlite"));
                                                            if (selected.at("ingress_sender_replay_cache_format").str() != expected_replay_cache_format) throw std::runtime_error("sqlite-wal v37+ capability manifest must require the current replay-cache format");
                                                            if (!selected.at("ingress_sender_possession_nonce_required").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must require sender proof nonce");
                                                            if (!selected.at("ingress_sender_possession_issued_at_required").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must require sender proof issued_at");
                                                            if (!selected.at("ingress_sender_replay_cache_duplicate_nonce_rejected_before_append").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must reject duplicate sender nonces before append");
                                                            if (!selected.at("ingress_sender_replay_window_enforced_before_append").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must enforce sender replay freshness before append");
                                                            if (!selected.at("ingress_sender_replay_cache_operator_configured_path_required").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must require operator-configured replay-cache path");
                                                            if (!selected.at("ingress_sender_replay_cache_symlink_family_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v37 capability manifest must reject sender replay-cache symlink family");
                                                            if (version >= 38) {
                                                                if (!selected.at("ingress_sender_replay_cache_instance_id_required").boolean(false)) throw std::runtime_error("sqlite-wal v38 capability manifest must require a replay-cache instance id");
                                                                if (!selected.at("ingress_sender_replay_cache_identity_metadata_required").boolean(false)) throw std::runtime_error("sqlite-wal v38 capability manifest must require replay-cache identity metadata");
                                                                if (!selected.at("ingress_sender_proof_binds_replay_cache_instance").boolean(false)) throw std::runtime_error("sqlite-wal v38 capability manifest must bind sender proof to replay-cache instance identity");
                                                                if (!selected.at("ingress_sender_replay_cache_identity_mismatch_rejected_before_append").boolean(false)) throw std::runtime_error("sqlite-wal v38 capability manifest must reject replay-cache identity mismatch before append");
                                                                if (version >= 39) {
                                                                    if (selected.at("ingress_service_request_format").str() != "anonsync-ingress-reservation-request-v2-trusted-context-separated") throw std::runtime_error("sqlite-wal v39 capability manifest must require service request v2 with trusted context separated");
                                                                    if (selected.at("ingress_transport_context_format").str() != "anonsync-ingress-transport-context-v1") throw std::runtime_error("sqlite-wal v39 capability manifest must require transport context v1");
                                                                    if (!selected.at("ingress_trusted_transport_context_out_of_band_required").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require out-of-band trusted transport context");
                                                                    if (!selected.at("ingress_request_trusted_identity_fields_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must reject request-supplied trusted identity fields");
                                                                    if (!selected.at("ingress_sender_replay_cache_nofollow_required").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require SQLite NOFOLLOW for sender replay cache opens");
                                                                    if (!selected.at("ingress_sender_replay_clock_override_forbidden").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must forbid service-config replay clock overrides");
                                                                    if (!selected.at("ingress_numeric_fields_integral_and_bounded").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require bounded integral ingress numeric fields");
                                                                    const std::string expected_sender_replay_key_material = version >= 40
                                                                        ? "anonsync-ingress-sender-replay-key-v5-ledger-integrated-nonce-window-unique"
                                                                        : "anonsync-ingress-sender-replay-key-v4-nonce-window-unique";
                                                                    if (selected.at("ingress_sender_replay_key_material_version").str() != expected_sender_replay_key_material) throw std::runtime_error("sqlite-wal v39+ capability manifest must require the current sender replay-key material");
                                                                    if (!selected.at("ingress_sender_replay_nonce_unique_within_retained_window").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must reject nonce reuse across distinct valid proofs within the retained replay window");
                                                                    if (!selected.at("ingress_public_api_digest_pinned_operator_config_handle_required").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require a digest-pinned operator config handle at the public API");
                                                                    if (!selected.at("ingress_ascii_casefold_duplicate_fields_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must reject ASCII-casefold duplicate security fields");
                                                                    if (!selected.at("ingress_sender_replay_rows_pruned_by_issued_at_window").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must state replay rows are pruned by the issued-at window");
                                                                    if (!selected.at("ingress_sender_replay_cache_clock_metadata_monotonic").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require monotonic replay-cache clock metadata");
                                                                    if (!selected.at("ingress_sender_replay_cache_wal_and_full_sync_verified").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must verify replay-cache WAL and FULL synchronous settings");
                                                                    if (selected.at("ingress_sender_replay_cache_busy_timeout_milliseconds").integer(0) != 5000) throw std::runtime_error("sqlite-wal v39 capability manifest must require the 5000ms replay-cache busy timeout");
                                                                    if (selected.at("ingress_service_config_maximum_bytes").integer(0) != 262144) throw std::runtime_error("sqlite-wal v39 capability manifest must bound service configuration at 262144 bytes");
                                                                    if (!selected.at("ingress_json_whitespace_strict_rfc8259").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require strict RFC 8259 JSON whitespace");
                                                                    if (!selected.at("ingress_json_raw_utf8_validation_required").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require raw UTF-8 validation");
                                                                    if (!selected.at("ingress_base64url_decoder_unsigned_accumulator_required").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must require an unsigned base64url accumulator");
                                                                    if (selected.at("ingress_rsa_public_key_minimum_bits").integer(0) != 2048) throw std::runtime_error("sqlite-wal v39 capability manifest must require RSA public keys of at least 2048 bits");
                                                                    if (!selected.at("ingress_private_workspace_permissions_fail_closed").boolean(false)) throw std::runtime_error("sqlite-wal v39 capability manifest must fail closed when private workspace permissions cannot be set");
                                                                    if (version >= 40) {
                                                                        if (!selected.at("ingress_sender_replay_cache_and_ledger_atomic_transaction").boolean(false)) throw std::runtime_error("sqlite-wal v40 capability manifest must claim integrated sender replay/ledger transaction");
                                                                        if (!selected.at("ingress_sender_replay_ledger_integrated_transaction").boolean(false)) throw std::runtime_error("sqlite-wal v40 capability manifest must require ledger-integrated sender replay rows");
                                                                        if (!selected.at("ingress_sender_replay_cache_external_service_write_removed").boolean(false)) throw std::runtime_error("sqlite-wal v40 capability manifest must remove the service-side external replay-cache write");
                                                                        if (version >= 41) {
                                                                            if (selected.at("effect_relay_downstream_store_format").str() != "anonsync-relay-downstream-store-v2-provenance-bound") throw std::runtime_error("sqlite-wal v41 capability manifest must require provenance-bound downstream store v2");
                                                                            if (selected.at("effect_relay_downstream_result_material_version").str() != "anonsync-relay-downstream-result-v2-provenance-bound") throw std::runtime_error("sqlite-wal v41 capability manifest must require provenance-bound downstream result material v2");
                                                                            if (!selected.at("effect_relay_downstream_store_nofollow_required").boolean(false)) throw std::runtime_error("sqlite-wal v41 capability manifest must require NOFOLLOW downstream store opens");
                                                                            if (!selected.at("effect_relay_downstream_store_wal_and_full_sync_verified").boolean(false)) throw std::runtime_error("sqlite-wal v41 capability manifest must verify downstream WAL and FULL sync");
                                                                            if (!selected.at("effect_relay_downstream_result_digest_binds_adapter_provenance").boolean(false)) throw std::runtime_error("sqlite-wal v41 capability manifest must bind downstream result digests to adapter provenance");
                                                                            if (!selected.at("effect_relay_downstream_existing_row_provenance_mismatch_rejected").boolean(false)) throw std::runtime_error("sqlite-wal v41 capability manifest must reject downstream existing-row provenance mismatches");
                                                                            if (version >= 42) {
                                                                                if (!selected.at("effect_relay_transition_authority_preflight_before_claim").boolean(false)) throw std::runtime_error("sqlite-wal v42 capability manifest must preflight relay transition authority before outbox claim");
                                                                                if (!selected.at("effect_relay_bad_signer_or_trust_rejected_before_downstream_touch").boolean(false)) throw std::runtime_error("sqlite-wal v42 capability manifest must reject bad relay signer/trust before downstream touch");
                                                                            }
                                                                        }
                                                                    } else if (selected.at("ingress_sender_replay_cache_and_ledger_atomic_transaction").boolean(true)) throw std::runtime_error("sqlite-wal v39 capability manifest must not claim one atomic replay-cache/ledger transaction");
                                                                }
                                                            }
                                                            const long long expected_min_restore_capability = version >= 41 ? 41 : (version >= 40 ? 40 : (version >= 39 ? 39 : (version >= 38 ? 38 : 37)));
                                                            if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != expected_min_restore_capability) throw std::runtime_error("sqlite-wal v37+ capability manifest must set minimum restore capability version to the active sender replay capability");
                                                        } else {
                                                            if (selected.at("ingress_sender_possession_material_version").str() != "anonsync-ingress-sender-possession-v2-lp-rs256") throw std::runtime_error("sqlite-wal v36 capability manifest must require sender possession material v2 RS256");
                                                            if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 36) throw std::runtime_error("sqlite-wal v36 capability manifest must set minimum restore capability version 36");
                                                        }
                                                        if (!selected.at("ingress_sender_possession_rs256_required").boolean(false)) throw std::runtime_error("sqlite-wal v36+ capability manifest must require RS256 sender possession proof");
                                                        if (!selected.at("ingress_sender_possession_public_jwk_required").boolean(false)) throw std::runtime_error("sqlite-wal v36+ capability manifest must require a service-pinned caller public JWK");
                                                        if (!selected.at("ingress_service_rejects_symmetric_caller_secret").boolean(false)) throw std::runtime_error("sqlite-wal v36+ capability manifest must reject symmetric caller secrets");
                                                        if (!selected.at("ingress_sender_possession_private_secret_absent_from_service_config").boolean(false)) throw std::runtime_error("sqlite-wal v36+ capability manifest must keep caller private material out of service config");
                                                    } else {
                                                        if (selected.at("ingress_sender_possession_material_version").str() != "anonsync-ingress-sender-possession-v1-lp-hmac-sha256") throw std::runtime_error("sqlite-wal v35 capability manifest must require sender possession material v1");
                                                        if (!selected.at("ingress_sender_possession_hmac_sha256_required").boolean(false)) throw std::runtime_error("sqlite-wal v35 capability manifest must require HMAC-SHA256 sender possession proof");
                                                        if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 35) throw std::runtime_error("sqlite-wal v35 capability manifest must set minimum restore capability version 35");
                                                    }
                                                } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 34) throw std::runtime_error("sqlite-wal v34 capability manifest must set minimum restore capability version 34");
                                            } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 33) throw std::runtime_error("sqlite-wal v33 capability manifest must set minimum restore capability version 33");
                                        } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 32) throw std::runtime_error("sqlite-wal v32 capability manifest must set minimum restore capability version 32");
                                    } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 31) throw std::runtime_error("sqlite-wal v31 capability manifest must set minimum restore capability version 31");
                                } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 30) throw std::runtime_error("sqlite-wal v30 capability manifest must set minimum restore capability version 30");
                            } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 29) throw std::runtime_error("sqlite-wal v29 capability manifest must set minimum restore capability version 29");
                        } else if (selected.at("snapshot_restore_minimum_capability_version").integer(0) != 28) throw std::runtime_error("sqlite-wal v28 capability manifest must set minimum restore capability version 28");
                    }
                }
            }
        }
        if (!selected.at("durability_ceiling").is_string() || selected.at("durability_ceiling").str().find("local") == std::string::npos) {
            throw std::runtime_error("sqlite-wal capability manifest must explicitly bound local-storage durability");
        }
    }
    if (backend_name == "local-jsonl") {
        if (!selected.at("journal_v2_only").boolean(false)) throw std::runtime_error("local-jsonl capability manifest must require journal-v2-only recovery");
        if (!selected.at("reject_symlink_sidecars").boolean(false)) throw std::runtime_error("local-jsonl capability manifest must require sidecar symlink rejection");
        if (version >= 18) {
            if (!selected.at("ledger_async_event_identity_replay_rejection_required").boolean(false)) throw std::runtime_error("local-jsonl v18 capability manifest must require durable async CloudEvents source/id replay rejection");
            if (!selected.at("ledger_async_event_identity_reload_duplicate_rejection_required").boolean(false)) throw std::runtime_error("local-jsonl v18 capability manifest must reject duplicate async event identities during reload");
        }
        if (version >= 20) {
            if (!selected.at("ledger_effect_idempotency_key_required").boolean(false)) throw std::runtime_error("local-jsonl v20 capability manifest must require effect idempotency keys");
            if (!selected.at("ledger_effect_state_prepared_required").boolean(false)) throw std::runtime_error("local-jsonl v20 capability manifest must require prepared effect state rows");
            if (!selected.at("ledger_duplicate_effect_idempotency_rejected").boolean(false)) throw std::runtime_error("local-jsonl v20 capability manifest must reject duplicate prepared effect idempotency keys");
            if (version == 20 && selected.at("entry_material_version").str() != "anonsync-replay-ledger-entry-v3-effect-prepared") throw std::runtime_error("local-jsonl v20 capability manifest must require prepared-effect entry material v3");
        }
        if (version >= 21) {
            if (selected.at("entry_material_version").str() != "anonsync-replay-ledger-entry-v3-effect-prepared") throw std::runtime_error("local-jsonl v21 capability manifest must still require prepared-effect entry material v3");
            if (!selected.at("ledger_effect_transition_unsupported_without_sqlite").boolean(false)) throw std::runtime_error("local-jsonl v21 capability manifest must explicitly state that effect transition chain is sqlite-only");
        }
        if (version >= 22) {
            if (!selected.at("ledger_effect_pending_report_unsupported_without_sqlite").boolean(false)) throw std::runtime_error("local-jsonl v22 capability manifest must explicitly state that pending-effect reports are sqlite-only");
        }
        if (version >= 27) {
            if (selected.at("security_tuple_framing").str() != "anonsync-length-prefixed-tuple-v1") throw std::runtime_error("local-jsonl v27 capability manifest must require length-prefixed security tuples");
            if (selected.at("proof_binding_material_version").str() != "anonsync-proof-binding-v2-lp-hmac-sha256") throw std::runtime_error("local-jsonl v27 capability manifest must require proof-binding material v2");
            if (selected.at("cloud_event_identity_material_version").str() != "anonsync-cloud-event-identity-v2") throw std::runtime_error("local-jsonl v27 capability manifest must require CloudEvents identity material v2");
            if (selected.at("effect_idempotency_material_version").str() != "anonsync-effect-idempotency-v2") throw std::runtime_error("local-jsonl v27 capability manifest must require effect-idempotency material v2");
            if (selected.at("legacy_effect_idempotency_fallback_material_version").str() != "anonsync-effect-idempotency-legacy-v1") throw std::runtime_error("local-jsonl v27 capability manifest must frame legacy effect-idempotency fallback material");
            if (!selected.at("case_insensitive_security_metadata_duplicate_rejection_required").boolean(false)) throw std::runtime_error("local-jsonl v27 capability manifest must reject duplicate case-insensitive security metadata");
            if (!selected.at("security_metadata_control_character_rejection_required").boolean(false)) throw std::runtime_error("local-jsonl v27 capability manifest must reject control characters in security metadata and event identity");
        }
    }
    return sha256_hex(manifest_text);
}

// rev0635 translation unit: backend capability v30 requires local relay/downstream reconciliation after downstream apply before terminal transition gaps.
// rev0636 translation unit: backend capability v31 requires digest-pinned operator relay adapter config for the production-shaped relay boundary.
// rev0612 translation unit: backend capability v8 requires operator-provided trust-profile sha256 digest pins.
// rev0612 translation unit: backend capability v7 requires trust-profile v3, canonical UTC time parsing, staleness windows, duplicate-signer rejection, and restore-root rotation/overlap support.
// rev0609 translation unit: backend capability v6 requires snapshot manifest v2, signed issued-at, trust-window, subject, and revision allowlist enforcement.
// rev0603 translation unit: streamed runner consumes replay-ledger backend capability manifests before selecting local-jsonl or SQLite/WAL storage.
// rev0601 translation unit: streamed execution runner with replay-ledger backend factory and SQLite/WAL candidate backend.
// rev0600 compatibility needle: rev0600 real translation units and IReplayLedgerBackend sidecar symlink hardening remain valid under the backend factory.
// rev0600 translation unit: streamed execution runner with explicit replay-ledger backend interface and sidecar-hardened local JSONL backend
// rev0598 compatibility needle: streamed execution runner with explicit replay-ledger commit modes


const char* kIngressReservationProfileFormat = "anonsync-ingress-reservation-profile-v1";
const char* kIngressReservationProfileRequestFormat = "anonsync-ingress-reservation-request-v1";
const char* kIngressReservationServiceRequestFormat = "anonsync-ingress-reservation-request-v2-trusted-context-separated";
const char* kIngressTransportContextFormat = "anonsync-ingress-transport-context-v1";
const char* kIngressReservationReportFormat = "anonsync-ingress-reservation-report-v1";
const char* kIngressReservationServiceConfigFormat = "anonsync-ingress-service-config-v6-trusted-context-separated";
const char* kIngressReservationServiceReportFormat = "anonsync-ingress-reservation-report-v8-ledger-integrated-replay";
const char* kIngressSenderPossessionMaterialVersion = "anonsync-ingress-sender-possession-v5-lp-rs256-trusted-context";
const char* kIngressSenderReplayCacheFormat = "anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction";
const char* kIngressSenderReplayKeyMaterialVersion = "anonsync-ingress-sender-replay-key-v5-ledger-integrated-nonce-window-unique";

struct IngressReservationServiceConfig {
    std::string service_id;
    std::string service_config_path;
    std::string service_config_sha256;
    bool service_config_digest_pin_verified = false;
    std::string ingress_profile_path;
    std::string ingress_profile_sha256;
    bool caller_binding_required = false;
    std::string caller_binding_material_version;
    std::string caller_binding_secret_id;
    std::string caller_binding_hmac_sha256_secret;
    std::string caller_binding_public_jwk_kid;
    std::string caller_binding_public_jwk_alg;
    std::string caller_binding_public_jwk_n;
    std::string caller_binding_public_jwk_e;
    std::string sender_replay_cache_path;
    std::string sender_replay_cache_instance_id;
    long long sender_replay_window_seconds = 0;
    long long sender_replay_future_skew_seconds = 0;
};

bool is_printable_handle(const std::string& value) {
    if (value.empty() || value.size() > 128) return false;
    if (contains_disallowed_security_control(value)) return false;
    for (unsigned char c : value) {
        if (c < 0x21 || c > 0x7e) return false;
    }
    return true;
}

std::string lower_ascii_copy(const std::string& value) {
    std::string out = value;
    for (char& c : out) {
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
    }
    return out;
}

void reject_case_insensitive_duplicate_object_keys(const Json& value, const std::string& label) {
    if (!value.is_object()) throw std::runtime_error(label + " must be an object");
    std::set<std::string> seen;
    for (const auto& kv : value.o) {
        const std::string folded = lower_ascii_copy(kv.first);
        if (!seen.insert(folded).second) {
            throw std::runtime_error(label + " contains duplicate ASCII-case-insensitive field: " + folded);
        }
    }
}

struct IngressReservationProfileSelection {
    std::string profile_path;
    std::string profile_sha256;
    std::string handle;
    std::string controls_path;
    std::string controls_sha256;
    std::string contracts_path;
    std::string contracts_sha256;
    std::string ledger_path;
    std::string ledger_backend;
    std::string ledger_commit_mode;
    std::string ledger_backend_capabilities_path;
    std::string ledger_backend_capabilities_sha256;
    std::string policy_envelope_key;
    std::string ledger_mode;
};

bool json_has_key_case_insensitive(const Json& obj, const std::string& key) {
    if (!obj.is_object()) return false;
    const std::string wanted = lower_ascii_copy(key);
    for (const auto& kv : obj.o) {
        if (lower_ascii_copy(kv.first) == wanted) return true;
    }
    return false;
}

std::string json_string_field_case_insensitive(const Json& obj, const std::string& key, const std::string& fallback = "") {
    if (!obj.is_object()) return fallback;
    const std::string wanted = lower_ascii_copy(key);
    for (const auto& kv : obj.o) {
        if (lower_ascii_copy(kv.first) == wanted) return kv.second.str(fallback);
    }
    return fallback;
}

bool is_control_free_string(const std::string& value) {
    return !value.empty() && !contains_disallowed_security_control(value);
}

struct IngressSenderPossessionVerification {
    bool required = false;
    bool verified = false;
    std::string material_version;
    std::string secret_id;
    std::string proof_kid;
    std::string proof_alg;
    std::string verification_reason;
    std::string principal;
    std::string authenticator;
    std::string case_sha256;
    std::string material_sha256;
    std::string nonce;
    long long issued_at_epoch = 0;
    long long replay_observed_at_epoch = 0;
    long long replay_window_seconds = 0;
    std::string replay_cache_path;
    std::string replay_cache_instance_id;
    std::string replay_cache_key_sha256;
    std::string replay_cache_format;
    bool replay_cache_reserved = false;
};

bool is_sender_replay_cache_instance_id(const std::string& value) {
    if (value.size() < 8 || value.size() > 128) return false;
    for (unsigned char c : value) {
        const bool ok = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                        (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~';
        if (!ok) return false;
    }
    return true;
}

bool is_sender_nonce(const std::string& value) {
    if (value.size() < 16 || value.size() > 128) return false;
    for (unsigned char c : value) {
        const bool ok = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                        (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~';
        if (!ok) return false;
    }
    return true;
}

constexpr size_t kIngressMaximumRequestBytes = 1024 * 1024;
constexpr size_t kIngressMaximumTransportContextBytes = 16 * 1024;
constexpr size_t kIngressMaximumServiceConfigBytes = 256 * 1024;
constexpr size_t kIngressMaximumIdentityFieldBytes = 512;
constexpr int kIngressReplayCacheBusyTimeoutMilliseconds = 5000;

std::string read_file_bounded(const std::string& path, size_t maximum_bytes, const std::string& label) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("could not open " + path);
    std::string out;
    out.reserve(std::min<size_t>(maximum_bytes, 64 * 1024));
    std::array<char, 8192> buffer{};
    while (in) {
        in.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = in.gcount();
        if (count > 0) {
            const size_t chunk = static_cast<size_t>(count);
            if (chunk > maximum_bytes - out.size()) {
                throw std::runtime_error(label + " exceeds the maximum accepted size");
            }
            out.append(buffer.data(), chunk);
        }
    }
    if (!in.eof()) throw std::runtime_error("could not read " + path);
    return out;
}

long long require_json_integer_in_range(const Json& value,
                                        const std::string& label,
                                        long long minimum,
                                        long long maximum) {
    if (!value.is_number() || !std::isfinite(value.n) || std::trunc(value.n) != value.n ||
        value.n < static_cast<double>(minimum) || value.n > static_cast<double>(maximum)) {
        throw std::runtime_error(label + " must be an integral JSON number in the allowed range");
    }
    return static_cast<long long>(value.n);
}

long long ingress_sender_replay_now() {
    const std::time_t now = std::time(nullptr);
    if (now <= 0) throw std::runtime_error("ingress service could not read the system clock");
    return static_cast<long long>(now);
}

void reject_sender_replay_cache_symlinks(const std::string& path) {
    if (path.empty()) throw std::runtime_error("ingress service sender replay cache path is required");
    for (const std::string& candidate : {path, path + "-wal", path + "-shm"}) {
        std::error_code ec;
        auto st = std::filesystem::symlink_status(candidate, ec);
        if (ec) {
            if (ec == std::errc::no_such_file_or_directory) continue;
            throw std::runtime_error("sender replay cache symlink-status failed for " + candidate + ": " + ec.message());
        }
        if (std::filesystem::is_symlink(st)) {
            throw std::runtime_error("sender replay cache refuses symlink path: " + candidate);
        }
    }
}

void sqlite_exec_checked(sqlite3* db, const std::string& sql, const std::string& label) {
    char* err = nullptr;
    if (sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
        std::string msg = err ? err : sqlite3_errmsg(db);
        sqlite3_free(err);
        throw std::runtime_error(label + ": " + msg);
    }
}

std::string sqlite_scalar_text_checked(sqlite3* db, const std::string& sql, const std::string& label) {
    sqlite3_stmt* stmt_raw = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt_raw, nullptr) != SQLITE_OK) {
        throw std::runtime_error(label + " prepare failed: " + std::string(sqlite3_errmsg(db)));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(stmt_raw, sqlite3_finalize);
    if (sqlite3_step(stmt.get()) != SQLITE_ROW) {
        throw std::runtime_error(label + " did not return a value: " + std::string(sqlite3_errmsg(db)));
    }
    return persistence::sqlite_exact_text_or_throw(stmt.get(), 0, label);
}

void sqlite_bind_text_checked(sqlite3_stmt* stmt, int idx, const std::string& value, const std::string& label) {
    if (sqlite3_bind_text(stmt, idx, value.c_str(), static_cast<int>(value.size()), SQLITE_TRANSIENT) != SQLITE_OK) {
        throw std::runtime_error("sender replay cache bind failed for " + label);
    }
}

void sqlite_bind_int64_checked(sqlite3_stmt* stmt, int idx, long long value, const std::string& label) {
    if (sqlite3_bind_int64(stmt, idx, static_cast<sqlite3_int64>(value)) != SQLITE_OK) {
        throw std::runtime_error("sender replay cache bind failed for " + label);
    }
}

std::string sender_replay_cache_meta_value(sqlite3* db, const std::string& key) {
    sqlite3_stmt* stmt_raw = nullptr;
    const char* sql = "SELECT meta_value FROM sender_replay_meta WHERE meta_key = ?;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt_raw, nullptr) != SQLITE_OK) {
        throw std::runtime_error("sender replay cache meta read prepare failed: " + std::string(sqlite3_errmsg(db)));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(stmt_raw, sqlite3_finalize);
    sqlite_bind_text_checked(stmt.get(), 1, key, "meta_key");
    const int rc = sqlite3_step(stmt.get());
    if (rc == SQLITE_ROW) {
        return persistence::sqlite_exact_text_or_throw(
            stmt.get(), 0, "sender replay cache metadata value");
    }
    if (rc == SQLITE_DONE) return "";
    throw std::runtime_error("sender replay cache meta read failed: " + std::string(sqlite3_errmsg(db)));
}

void sender_replay_cache_put_meta(sqlite3* db, const std::string& key, const std::string& value) {
    sqlite3_stmt* stmt_raw = nullptr;
    const char* sql = "INSERT INTO sender_replay_meta(meta_key, meta_value) VALUES (?, ?) "
                      "ON CONFLICT(meta_key) DO UPDATE SET meta_value = excluded.meta_value;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt_raw, nullptr) != SQLITE_OK) {
        throw std::runtime_error("sender replay cache meta write prepare failed: " + std::string(sqlite3_errmsg(db)));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(stmt_raw, sqlite3_finalize);
    sqlite_bind_text_checked(stmt.get(), 1, key, "meta_key");
    sqlite_bind_text_checked(stmt.get(), 2, value, "meta_value");
    const int rc = sqlite3_step(stmt.get());
    if (rc != SQLITE_DONE) throw std::runtime_error("sender replay cache meta write failed: " + std::string(sqlite3_errmsg(db)));
}

long long parse_sender_replay_meta_epoch(const std::string& value, const std::string& label) {
    if (value.empty()) return 0;
    try {
        size_t pos = 0;
        long long parsed = std::stoll(value, &pos, 10);
        if (pos != value.size()) throw std::runtime_error("trailing text");
        return parsed;
    } catch (...) {
        throw std::runtime_error("sender replay cache meta " + label + " is malformed");
    }
}

void ensure_sender_replay_cache_metadata(sqlite3* db,
                                         const IngressReservationServiceConfig& service_config,
                                         long long now_epoch) {
    if (!is_sender_replay_cache_instance_id(service_config.sender_replay_cache_instance_id)) {
        throw std::runtime_error("ingress service sender replay cache instance id is required");
    }
    sqlite_exec_checked(db,
        "CREATE TABLE IF NOT EXISTS sender_replay_meta ("
        "meta_key TEXT PRIMARY KEY,"
        "meta_value TEXT NOT NULL);",
        "sender replay cache metadata schema setup failed");
    const std::string existing_format = sender_replay_cache_meta_value(db, "format");
    if (existing_format.empty()) {
        sender_replay_cache_put_meta(db, "format", kIngressSenderReplayCacheFormat);
        sender_replay_cache_put_meta(db, "instance_id", service_config.sender_replay_cache_instance_id);
        sender_replay_cache_put_meta(db, "service_id", service_config.service_id);
        sender_replay_cache_put_meta(db, "service_config_sha256", service_config.service_config_sha256);
        sender_replay_cache_put_meta(db, "ingress_profile_sha256", service_config.ingress_profile_sha256);
        sender_replay_cache_put_meta(db, "caller_binding_public_jwk_kid", service_config.caller_binding_public_jwk_kid);
        sender_replay_cache_put_meta(db, "replay_key_material_version", kIngressSenderReplayKeyMaterialVersion);
        sender_replay_cache_put_meta(db, "created_at_epoch", std::to_string(now_epoch));
        sender_replay_cache_put_meta(db, "last_seen_epoch", std::to_string(now_epoch));
        return;
    }
    auto require_meta = [&](const std::string& key, const std::string& expected) {
        const std::string actual = sender_replay_cache_meta_value(db, key);
        if (actual != expected) {
            throw std::runtime_error("sender replay cache identity mismatch for " + key);
        }
    };
    require_meta("format", kIngressSenderReplayCacheFormat);
    require_meta("instance_id", service_config.sender_replay_cache_instance_id);
    require_meta("service_id", service_config.service_id);
    require_meta("service_config_sha256", service_config.service_config_sha256);
    require_meta("ingress_profile_sha256", service_config.ingress_profile_sha256);
    require_meta("caller_binding_public_jwk_kid", service_config.caller_binding_public_jwk_kid);
    require_meta("replay_key_material_version", kIngressSenderReplayKeyMaterialVersion);
    const long long created_at = parse_sender_replay_meta_epoch(sender_replay_cache_meta_value(db, "created_at_epoch"), "created_at_epoch");
    const long long last_seen = parse_sender_replay_meta_epoch(sender_replay_cache_meta_value(db, "last_seen_epoch"), "last_seen_epoch");
    if (created_at <= 0 || last_seen <= 0 || last_seen < created_at) {
        throw std::runtime_error("sender replay cache clock metadata is missing or non-monotonic");
    }
    if (created_at > now_epoch + service_config.sender_replay_future_skew_seconds ||
        last_seen > now_epoch + service_config.sender_replay_future_skew_seconds) {
        throw std::runtime_error("sender replay cache clock metadata is ahead of service time");
    }
    sender_replay_cache_put_meta(db, "last_seen_epoch", std::to_string(std::max(last_seen, now_epoch)));
}

Json json_number_value(long long value) {
    Json v;
    v.type = Json::Type::Number;
    v.n = static_cast<double>(value);
    return v;
}

std::string ingress_sender_replay_key_material(const IngressReservationServiceConfig& service_config,
                                               const IngressSenderPossessionVerification& sender) {
    return length_prefixed_security_tuple(kIngressSenderReplayKeyMaterialVersion, {
        {"service_id", service_config.service_id},
        {"service_config_sha256", service_config.service_config_sha256},
        {"ingress_profile_sha256", service_config.ingress_profile_sha256},
        {"sender_replay_cache_instance_id", service_config.sender_replay_cache_instance_id},
        {"sender_proof_kid", sender.proof_kid},
        {"nonce", sender.nonce}
    });
}

void prepare_ingress_sender_replay_for_ledger(const IngressReservationServiceConfig& service_config,
                                              IngressSenderPossessionVerification& sender) {
    if (!sender.verified) throw std::runtime_error("ingress sender_possession must verify before replay evidence is prepared");
    if (service_config.sender_replay_window_seconds < 1 || service_config.sender_replay_window_seconds > 86400) {
        throw std::runtime_error("ingress service sender replay window must be between 1 and 86400 seconds");
    }
    if (service_config.sender_replay_future_skew_seconds < 0 || service_config.sender_replay_future_skew_seconds > 300) {
        throw std::runtime_error("ingress service sender replay future skew must be between 0 and 300 seconds");
    }
    const long long now_epoch = ingress_sender_replay_now();
    if (sender.issued_at_epoch <= 0) throw std::runtime_error("ingress sender_possession issued_at_epoch is required");
    if (sender.issued_at_epoch < now_epoch - service_config.sender_replay_window_seconds) {
        throw std::runtime_error("ingress sender_possession issued_at_epoch is outside the sender replay window");
    }
    if (sender.issued_at_epoch > now_epoch + service_config.sender_replay_future_skew_seconds) {
        throw std::runtime_error("ingress sender_possession issued_at_epoch is too far in the future");
    }
    sender.replay_cache_key_sha256 = sha256_hex(ingress_sender_replay_key_material(service_config, sender));
    sender.replay_observed_at_epoch = now_epoch;
    sender.replay_window_seconds = service_config.sender_replay_window_seconds;
    sender.replay_cache_instance_id = service_config.sender_replay_cache_instance_id;
    sender.replay_cache_format = kIngressSenderReplayCacheFormat;
    sender.replay_cache_reserved = false;
}

Json ingress_sender_replay_evidence_json(const IngressReservationServiceConfig& service_config,
                                         const IngressSenderPossessionVerification& sender) {
    if (!sender.verified || sender.replay_cache_key_sha256.empty() || sender.replay_observed_at_epoch <= 0) {
        throw std::runtime_error("ingress sender replay evidence is not prepared");
    }
    Json replay;
    replay.type = Json::Type::Object;
    replay.o["format"] = json_string_value(kIngressSenderReplayCacheFormat);
    replay.o["replay_key_sha256"] = json_string_value(sender.replay_cache_key_sha256);
    replay.o["service_config_sha256"] = json_string_value(service_config.service_config_sha256);
    replay.o["ingress_profile_sha256"] = json_string_value(service_config.ingress_profile_sha256);
    replay.o["sender_replay_cache_instance_id"] = json_string_value(service_config.sender_replay_cache_instance_id);
    replay.o["sender_proof_kid"] = json_string_value(sender.proof_kid);
    replay.o["principal"] = json_string_value(sender.principal);
    replay.o["nonce"] = json_string_value(sender.nonce);
    replay.o["issued_at_epoch"] = json_number_value(sender.issued_at_epoch);
    replay.o["observed_at_epoch"] = json_number_value(sender.replay_observed_at_epoch);
    replay.o["replay_window_seconds"] = json_number_value(sender.replay_window_seconds);
    replay.o["material_sha256"] = json_string_value(sender.material_sha256);
    return replay;
}

void reserve_ingress_sender_replay_nonce(const IngressReservationServiceConfig& service_config,
                                         IngressSenderPossessionVerification& sender) {
    if (service_config.sender_replay_cache_path.empty()) throw std::runtime_error("ingress service sender replay cache path is required");
    if (service_config.sender_replay_window_seconds < 1 || service_config.sender_replay_window_seconds > 86400) {
        throw std::runtime_error("ingress service sender replay window must be between 1 and 86400 seconds");
    }
    if (service_config.sender_replay_future_skew_seconds < 0 || service_config.sender_replay_future_skew_seconds > 300) {
        throw std::runtime_error("ingress service sender replay future skew must be between 0 and 300 seconds");
    }
    const long long now_epoch = ingress_sender_replay_now();
    if (sender.issued_at_epoch <= 0) throw std::runtime_error("ingress sender_possession issued_at_epoch is required");
    if (sender.issued_at_epoch < now_epoch - service_config.sender_replay_window_seconds) {
        throw std::runtime_error("ingress sender_possession issued_at_epoch is outside the sender replay window");
    }
    if (sender.issued_at_epoch > now_epoch + service_config.sender_replay_future_skew_seconds) {
        throw std::runtime_error("ingress sender_possession issued_at_epoch is too far in the future");
    }
    reject_sender_replay_cache_symlinks(service_config.sender_replay_cache_path);
    std::filesystem::path cache_path(service_config.sender_replay_cache_path);
    if (!cache_path.parent_path().empty()) std::filesystem::create_directories(cache_path.parent_path());
    sqlite3* db_raw = nullptr;
    const int open_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_NOFOLLOW;
    if (sqlite3_open_v2(service_config.sender_replay_cache_path.c_str(), &db_raw, open_flags, nullptr) != SQLITE_OK) {
        std::string msg = db_raw ? sqlite3_errmsg(db_raw) : "unknown open failure";
        if (db_raw) sqlite3_close(db_raw);
        throw std::runtime_error("sender replay cache open failed: " + msg);
    }
    std::unique_ptr<sqlite3, decltype(&sqlite3_close)> db(db_raw, sqlite3_close);
    if (sqlite3_busy_timeout(db.get(), kIngressReplayCacheBusyTimeoutMilliseconds) != SQLITE_OK) {
        throw std::runtime_error("sender replay cache busy-timeout setup failed: " + std::string(sqlite3_errmsg(db.get())));
    }
    sqlite3_limit(db.get(), SQLITE_LIMIT_LENGTH, static_cast<int>(kIngressMaximumRequestBytes));
    sqlite3_limit(db.get(), SQLITE_LIMIT_SQL_LENGTH, 64 * 1024);
    sqlite3_limit(db.get(), SQLITE_LIMIT_COLUMN, 64);
    const SyncSqliteConcurrentJournalProfile durability_profile =
        configure_sync_sqlite_concurrent_durable_journal_or_throw(
            db.get(), "sender replay cache durability profile");
    sqlite_exec_checked(db.get(), "PRAGMA trusted_schema=OFF;", "sender replay cache trusted-schema hardening failed");
    sqlite_exec_checked(db.get(), "BEGIN IMMEDIATE;", "sender replay cache begin failed");
    bool committed = false;
    try {
        ensure_sender_replay_cache_metadata(db.get(), service_config, now_epoch);
        sender_replay_cache_put_meta(db.get(), "sqlite_runtime_version",
                                     durability_profile.runtime_version);
        sender_replay_cache_put_meta(db.get(), "sqlite_runtime_source_id",
                                     durability_profile.runtime_source_id);
        sender_replay_cache_put_meta(db.get(), "sqlite_journal_mode",
                                     durability_profile.journal_mode);
        sender_replay_cache_put_meta(db.get(), "sqlite_runtime_bundled",
                                     durability_profile.bundled ? "true" : "false");
        sender_replay_cache_put_meta(db.get(), "sqlite_wal_reset_fix_known",
                                     durability_profile.wal_reset_fix_known ? "true" : "false");
        sender_replay_cache_put_meta(
            db.get(), "sqlite_rollback_journal_fallback_active",
            durability_profile.rollback_journal_fallback_active ? "true" : "false");
        sqlite_exec_checked(db.get(),
            "CREATE TABLE IF NOT EXISTS sender_replay_cache ("
            "replay_key_sha256 TEXT PRIMARY KEY,"
            "format TEXT NOT NULL,"
            "service_config_sha256 TEXT NOT NULL,"
            "ingress_profile_sha256 TEXT NOT NULL,"
            "sender_proof_kid TEXT NOT NULL,"
            "principal TEXT NOT NULL,"
            "nonce TEXT NOT NULL,"
            "issued_at_epoch INTEGER NOT NULL,"
            "first_seen_epoch INTEGER NOT NULL,"
            "material_sha256 TEXT NOT NULL);",
            "sender replay cache schema setup failed");
        sqlite_exec_checked(db.get(), "CREATE INDEX IF NOT EXISTS idx_sender_replay_expiry ON sender_replay_cache(issued_at_epoch);", "sender replay cache expiry index setup failed");
        sqlite_exec_checked(db.get(), "CREATE UNIQUE INDEX IF NOT EXISTS idx_sender_replay_nonce_unique ON sender_replay_cache(sender_proof_kid, nonce);", "sender replay cache nonce uniqueness index setup failed");
        {
            sqlite3_stmt* stmt_raw = nullptr;
            const char* sql = "DELETE FROM sender_replay_cache WHERE issued_at_epoch < ?;";
            if (sqlite3_prepare_v2(db.get(), sql, -1, &stmt_raw, nullptr) != SQLITE_OK) throw std::runtime_error("sender replay cache prune prepare failed: " + std::string(sqlite3_errmsg(db.get())));
            std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(stmt_raw, sqlite3_finalize);
            sqlite_bind_int64_checked(stmt.get(), 1, now_epoch - service_config.sender_replay_window_seconds, "prune_epoch");
            int rc = sqlite3_step(stmt.get());
            if (rc != SQLITE_DONE) throw std::runtime_error("sender replay cache prune failed: " + std::string(sqlite3_errmsg(db.get())));
        }
        sender.replay_cache_key_sha256 = sha256_hex(ingress_sender_replay_key_material(service_config, sender));
        sender.replay_observed_at_epoch = now_epoch;
        sender.replay_window_seconds = service_config.sender_replay_window_seconds;
        sender.replay_cache_path = service_config.sender_replay_cache_path;
        sender.replay_cache_instance_id = service_config.sender_replay_cache_instance_id;
        sender.replay_cache_format = kIngressSenderReplayCacheFormat;
        {
            sqlite3_stmt* stmt_raw = nullptr;
            const char* sql = "INSERT INTO sender_replay_cache "
                              "(replay_key_sha256, format, service_config_sha256, ingress_profile_sha256, sender_proof_kid, principal, nonce, issued_at_epoch, first_seen_epoch, material_sha256) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);";
            if (sqlite3_prepare_v2(db.get(), sql, -1, &stmt_raw, nullptr) != SQLITE_OK) throw std::runtime_error("sender replay cache insert prepare failed: " + std::string(sqlite3_errmsg(db.get())));
            std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(stmt_raw, sqlite3_finalize);
            sqlite_bind_text_checked(stmt.get(), 1, sender.replay_cache_key_sha256, "replay_key_sha256");
            sqlite_bind_text_checked(stmt.get(), 2, kIngressSenderReplayCacheFormat, "format");
            sqlite_bind_text_checked(stmt.get(), 3, service_config.service_config_sha256, "service_config_sha256");
            sqlite_bind_text_checked(stmt.get(), 4, service_config.ingress_profile_sha256, "ingress_profile_sha256");
            sqlite_bind_text_checked(stmt.get(), 5, sender.proof_kid, "sender_proof_kid");
            sqlite_bind_text_checked(stmt.get(), 6, sender.principal, "principal");
            sqlite_bind_text_checked(stmt.get(), 7, sender.nonce, "nonce");
            sqlite_bind_int64_checked(stmt.get(), 8, sender.issued_at_epoch, "issued_at_epoch");
            sqlite_bind_int64_checked(stmt.get(), 9, now_epoch, "first_seen_epoch");
            sqlite_bind_text_checked(stmt.get(), 10, sender.material_sha256, "material_sha256");
            int rc = sqlite3_step(stmt.get());
            if (rc == SQLITE_CONSTRAINT) throw std::runtime_error("ingress sender_possession replay nonce was already reserved");
            if (rc != SQLITE_DONE) throw std::runtime_error("sender replay cache insert failed: " + std::string(sqlite3_errmsg(db.get())));
        }
        sqlite_exec_checked(db.get(), "COMMIT;", "sender replay cache commit failed");
        committed = true;
        sender.replay_cache_reserved = true;
    } catch (...) {
        if (!committed) {
            char* err = nullptr;
            sqlite3_exec(db.get(), "ROLLBACK;", nullptr, nullptr, &err);
            sqlite3_free(err);
        }
        throw;
    }
}

void validate_authenticated_context_shape(const Json& authenticated_context) {
    reject_case_insensitive_duplicate_object_keys(authenticated_context, "internal ingress profile authenticated_context");
    static const std::set<std::string> allowed = {"authenticator", "principal", "sender_possession", "transport_authenticated"};
    for (const auto& kv : authenticated_context.o) {
        if (!allowed.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("internal ingress profile authenticated_context contains unsupported field: " + kv.first);
        }
    }
    if (!authenticated_context.at("transport_authenticated").boolean(false)) {
        throw std::runtime_error("internal ingress profile adapter requires transport_authenticated context");
    }
    if (!is_control_free_string(authenticated_context.at("authenticator").str())) {
        throw std::runtime_error("internal ingress profile adapter requires a control-free authenticator");
    }
    if (!is_control_free_string(authenticated_context.at("principal").str())) {
        throw std::runtime_error("internal ingress profile adapter requires a control-free principal");
    }
}

void validate_trusted_transport_context(const IngressTransportContext& trusted_context) {
    if (!trusted_context.transport_authenticated) {
        throw std::runtime_error("trusted transport context must assert transport_authenticated");
    }
    auto require_identity = [](const std::string& value, const std::string& label) {
        if (!is_control_free_string(value) || value.size() > kIngressMaximumIdentityFieldBytes) {
            throw std::runtime_error("trusted transport context requires a bounded control-free " + label);
        }
    };
    require_identity(trusted_context.authenticator, "authenticator");
    require_identity(trusted_context.principal, "principal");
}

IngressTransportContext load_ingress_transport_context(const std::string& context_path) {
    if (context_path.empty()) throw std::runtime_error("ingress service requires an out-of-band transport context path");
    const std::string text = read_file_bounded(context_path, kIngressMaximumTransportContextBytes, "ingress transport context");
    const Json root = parse_json_text(text);
    reject_case_insensitive_duplicate_object_keys(root, "ingress transport context");
    static const std::set<std::string> allowed = {"authenticator", "format", "principal", "transport_authenticated"};
    for (const auto& kv : root.o) {
        if (!allowed.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("ingress transport context contains unsupported field: " + kv.first);
        }
    }
    if (root.at("format").str() != kIngressTransportContextFormat) {
        throw std::runtime_error("ingress transport context has unsupported format");
    }
    IngressTransportContext out;
    out.transport_authenticated = root.at("transport_authenticated").boolean(false);
    out.authenticator = root.at("authenticator").str();
    out.principal = root.at("principal").str();
    validate_trusted_transport_context(out);
    return out;
}

std::string ingress_sender_possession_material(const IngressReservationServiceConfig& service_config,
                                               const IngressTransportContext& trusted_context,
                                               const Json& request,
                                               const Json& proof,
                                               const std::string& case_sha256,
                                               long long issued_at_epoch) {
    return length_prefixed_security_tuple(kIngressSenderPossessionMaterialVersion, {
        {"service_id", service_config.service_id},
        {"service_config_sha256", service_config.service_config_sha256},
        {"ingress_profile_sha256", service_config.ingress_profile_sha256},
        {"sender_replay_cache_instance_id", service_config.sender_replay_cache_instance_id},
        {"sender_proof_alg", service_config.caller_binding_public_jwk_alg},
        {"sender_proof_kid", service_config.caller_binding_public_jwk_kid},
        {"request_format", request.at("format").str()},
        {"request_revision_id", request.at("revision_id").str()},
        {"request_id", request.at("request_id").str()},
        {"config_handle", request.at("config_handle").str()},
        {"transport_authenticated", trusted_context.transport_authenticated ? "true" : "false"},
        {"authenticator", trusted_context.authenticator},
        {"principal", trusted_context.principal},
        {"sender_nonce", proof.at("nonce").str()},
        {"sender_issued_at_epoch", std::to_string(issued_at_epoch)},
        {"case_sha256", case_sha256}
    });
}

IngressSenderPossessionVerification verify_ingress_sender_possession(const IngressReservationServiceConfig& service_config,
                                                                     const IngressTransportContext& trusted_context,
                                                                     const Json& request,
                                                                     bool reserve_replay_nonce) {
    IngressSenderPossessionVerification out;
    out.required = service_config.caller_binding_required;
    out.material_version = service_config.caller_binding_material_version;
    out.secret_id = service_config.caller_binding_public_jwk_kid.empty() ? service_config.caller_binding_secret_id : service_config.caller_binding_public_jwk_kid;
    out.proof_kid = out.secret_id;
    out.proof_alg = service_config.caller_binding_public_jwk_alg;
    validate_trusted_transport_context(trusted_context);
    if (request.at("format").str() != kIngressReservationServiceRequestFormat) {
        throw std::runtime_error("ingress service request has unsupported format");
    }
    out.principal = trusted_context.principal;
    out.authenticator = trusted_context.authenticator;
    if (!request.at("case").is_object()) throw std::runtime_error("ingress service request requires one case object");
    out.case_sha256 = sha256_hex(canonical_json(request.at("case")));
    if (!service_config.caller_binding_required) return out;
    if (service_config.caller_binding_material_version != kIngressSenderPossessionMaterialVersion) {
        throw std::runtime_error("ingress service caller binding material version is unsupported");
    }
    if (!is_printable_handle(service_config.caller_binding_public_jwk_kid) ||
        service_config.caller_binding_public_jwk_alg != "RS256" ||
        service_config.caller_binding_public_jwk_n.empty() ||
        service_config.caller_binding_public_jwk_e.empty()) {
        throw std::runtime_error("ingress service caller binding public JWK is not configured");
    }
    if (!service_config.caller_binding_hmac_sha256_secret.empty() || !service_config.caller_binding_secret_id.empty()) {
        throw std::runtime_error("ingress service asymmetric caller binding rejects symmetric caller secrets");
    }
    if (!is_lowercase_sha256_hex(service_config.service_config_sha256)) {
        throw std::runtime_error("ingress service caller binding requires a digest-pinned service config");
    }
    const Json& proof = request.at("sender_possession");
    reject_case_insensitive_duplicate_object_keys(proof, "ingress sender_possession proof");
    static const std::set<std::string> allowed_proof = {"alg", "case_sha256", "format", "issued_at_epoch", "kid", "nonce", "signature_b64url"};
    for (const auto& kv : proof.o) {
        if (!allowed_proof.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("ingress sender_possession contains unsupported field: " + kv.first);
        }
    }
    if (proof.at("format").str() != kIngressSenderPossessionMaterialVersion) {
        throw std::runtime_error("ingress sender_possession proof has unsupported format");
    }
    if (proof.at("alg").str() != service_config.caller_binding_public_jwk_alg) {
        throw std::runtime_error("ingress sender_possession proof alg does not match service caller binding public key");
    }
    if (proof.at("kid").str() != service_config.caller_binding_public_jwk_kid) {
        throw std::runtime_error("ingress sender_possession proof kid does not match service caller binding public key");
    }
    if (proof.at("case_sha256").str() != out.case_sha256) {
        throw std::runtime_error("ingress sender_possession case digest mismatch");
    }
    out.nonce = proof.at("nonce").str();
    if (!is_sender_nonce(out.nonce)) throw std::runtime_error("ingress sender_possession proof nonce is required and must be base64url-like printable text");
    out.issued_at_epoch = require_json_integer_in_range(proof.at("issued_at_epoch"),
                                                        "ingress sender_possession issued_at_epoch",
                                                        1,
                                                        9007199254740991LL);
    const std::string supplied = proof.at("signature_b64url").str();
    if (supplied.empty() || contains_disallowed_security_control(supplied)) throw std::runtime_error("ingress sender_possession proof must carry an RS256 signature_b64url");
    const std::string material = ingress_sender_possession_material(service_config,
                                                                    trusted_context,
                                                                    request,
                                                                    proof,
                                                                    out.case_sha256,
                                                                    out.issued_at_epoch);
    out.material_sha256 = sha256_hex(material);
    out.proof_kid = service_config.caller_binding_public_jwk_kid;
    out.proof_alg = service_config.caller_binding_public_jwk_alg;
    PKeyPtr public_key = jwk_to_pkey(service_config.caller_binding_public_jwk_n, service_config.caller_binding_public_jwk_e);
    std::string verify_reason;
    if (!verify_rs256(public_key.get(), material, supplied, verify_reason)) {
        throw std::runtime_error("ingress sender_possession RS256 proof mismatch: " + verify_reason);
    }
    out.verification_reason = verify_reason;
    out.verified = true;
    if (reserve_replay_nonce) {
        reserve_ingress_sender_replay_nonce(service_config, out);
    }
    return out;
}

Json make_internal_profile_request(const Json& service_request,
                                   const IngressTransportContext& trusted_context) {
    Json legacy = service_request;
    legacy.o["format"] = json_string_value(kIngressReservationProfileRequestFormat);
    legacy.o.erase("sender_possession");
    Json authenticated_context;
    authenticated_context.type = Json::Type::Object;
    authenticated_context.o["transport_authenticated"] = json_bool_value(trusted_context.transport_authenticated);
    authenticated_context.o["authenticator"] = json_string_value(trusted_context.authenticator);
    authenticated_context.o["principal"] = json_string_value(trusted_context.principal);
    authenticated_context.o["sender_possession"] = service_request.at("sender_possession");
    legacy.o["authenticated_context"] = authenticated_context;
    return legacy;
}

void reject_forbidden_ingress_request_fields(const Json& request) {
    static const std::set<std::string> allowed_top_level = {
        "authenticated_context", "case", "config_handle", "format", "request_id", "revision_id"
    };
    reject_case_insensitive_duplicate_object_keys(request, "ingress reservation request");
    for (const auto& kv : request.o) {
        if (!allowed_top_level.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("ingress reservation request contains unsupported operator field: " + kv.first);
        }
    }
    static const std::vector<std::string> forbidden = {
        "ledger", "ledger_path", "ledger_backend", "ledger_commit_mode", "ledger_backend_capabilities", "ledger_backend_capabilities_path",
        "controls", "controls_path", "contracts", "contracts_path", "cases_jsonl", "cases_jsonl_path", "ledger_reset",
        "evaluation_time_epoch", "now_epoch", "clock", "trusted_time", "time_policy", "proof_binding_hmac_sha256_secret", "proof_binding_secret_id", "jwk", "jwks", "policy_profile",
        "profile", "profile_path", "profile_sha256", "operator_profile", "operator_profile_path", "operator_profile_sha256", "ingress_profile", "ingress_profile_sha256",
        "relay_registry_path", "relay_registry_sha256", "relay_config_path", "relay_config_sha256", "signer_private_key_pem", "signer_key_id", "trust_profile_path", "trust_profile_sha256",
        "worker_id", "lease_seconds", "terminal_state", "downstream_store", "downstream_store_path", "adapter_id", "adapter_kind",
        "snapshot_path", "restore_from_snapshot", "backend_mode", "commit_mode"
    };
    for (const auto& key : forbidden) {
        if (json_has_key_case_insensitive(request, key)) throw std::runtime_error("ingress reservation request may not select operator field: " + key);
    }
}

void reject_forbidden_ingress_service_request_fields(const Json& request) {
    reject_case_insensitive_duplicate_object_keys(request, "ingress service request");
    static const std::set<std::string> allowed_top_level = {
        "case", "config_handle", "format", "request_id", "revision_id", "sender_possession"
    };
    for (const auto& kv : request.o) {
        const std::string key = lower_ascii_copy(kv.first);
        if (key == "authenticated_context" || key == "transport_authenticated" || key == "authenticator" || key == "principal") {
            throw std::runtime_error("ingress service request may not supply trusted transport identity field: " + kv.first);
        }
        if (!allowed_top_level.count(key)) {
            throw std::runtime_error("ingress service request contains unsupported operator field: " + kv.first);
        }
    }
    static const std::vector<std::string> forbidden = {
        "ledger", "ledger_path", "ledger_backend", "ledger_commit_mode", "ledger_backend_capabilities", "ledger_backend_capabilities_path",
        "controls", "controls_path", "contracts", "contracts_path", "cases_jsonl", "cases_jsonl_path", "ledger_reset",
        "evaluation_time_epoch", "now_epoch", "clock", "trusted_time", "time_policy", "proof_binding_hmac_sha256_secret", "proof_binding_secret_id", "jwk", "jwks", "policy_profile",
        "profile", "profile_path", "profile_sha256", "operator_profile", "operator_profile_path", "operator_profile_sha256", "ingress_profile", "ingress_profile_sha256",
        "relay_registry_path", "relay_registry_sha256", "relay_config_path", "relay_config_sha256", "signer_private_key_pem", "signer_key_id", "trust_profile_path", "trust_profile_sha256",
        "worker_id", "lease_seconds", "terminal_state", "downstream_store", "downstream_store_path", "adapter_id", "adapter_kind",
        "snapshot_path", "restore_from_snapshot", "backend_mode", "commit_mode"
    };
    for (const auto& key : forbidden) {
        if (json_has_key_case_insensitive(request, key)) throw std::runtime_error("ingress service request may not select operator field: " + key);
    }
}

IngressReservationProfileSelection load_ingress_reservation_profile_selection(const std::string& profile_path,
                                                                              const std::string& expected_sha256,
                                                                              const std::string& handle) {
    if (profile_path.empty()) throw std::runtime_error("ingress reservation requires an operator profile path");
    if (!is_lowercase_sha256_hex(expected_sha256)) throw std::runtime_error("ingress reservation requires a lowercase sha256 operator profile pin");
    if (!is_printable_handle(handle)) throw std::runtime_error("ingress reservation request requires a printable config_handle");
    const std::string text = read_file(profile_path);
    const std::string actual_sha256 = sha256_hex(text);
    if (actual_sha256 != expected_sha256) throw std::runtime_error("ingress reservation operator profile digest pin mismatch");
    Json root = parse_json_text(text);
    if (root.at("format").str() != kIngressReservationProfileFormat) throw std::runtime_error("ingress reservation operator profile has unsupported format");
    const Json& entries = root.at("handles");
    if (!entries.is_array()) throw std::runtime_error("ingress reservation operator profile requires handles array");
    const Json* selected = nullptr;
    std::set<std::string> seen;
    for (const auto& entry : entries.a) {
        if (!entry.is_object()) throw std::runtime_error("ingress reservation operator profile handle entry must be an object");
        const std::string candidate = entry.at("handle").str();
        if (!is_printable_handle(candidate)) throw std::runtime_error("ingress reservation operator profile contains malformed handle");
        if (!seen.insert(candidate).second) throw std::runtime_error("ingress reservation operator profile contains duplicate handle");
        if (candidate == handle) selected = &entry;
    }
    if (selected == nullptr) throw std::runtime_error("ingress reservation operator profile does not contain requested handle");
    if (!selected->at("enabled").boolean(false)) throw std::runtime_error("ingress reservation operator profile handle is disabled");
    IngressReservationProfileSelection out;
    out.profile_path = profile_path;
    out.profile_sha256 = actual_sha256;
    out.handle = handle;
    out.controls_path = selected->at("controls_path").str();
    out.controls_sha256 = selected->at("controls_sha256").str();
    out.contracts_path = selected->at("contracts_path").str();
    out.contracts_sha256 = selected->at("contracts_sha256").str();
    out.ledger_path = selected->at("ledger_path").str();
    out.ledger_backend = selected->at("ledger_backend").str("sqlite-wal");
    out.ledger_commit_mode = selected->at("ledger_commit_mode").str("immediate");
    out.ledger_backend_capabilities_path = selected->at("ledger_backend_capabilities_path").str();
    out.ledger_backend_capabilities_sha256 = selected->at("ledger_backend_capabilities_sha256").str();
    out.policy_envelope_key = selected->at("policy_envelope_key").str("normal");
    out.ledger_mode = selected->at("ledger_mode").str("normal");
    if (out.controls_path.empty() || !is_lowercase_sha256_hex(out.controls_sha256)) throw std::runtime_error("ingress reservation profile handle lacks digest-pinned controls path");
    if (out.contracts_path.empty() || !is_lowercase_sha256_hex(out.contracts_sha256)) throw std::runtime_error("ingress reservation profile handle lacks digest-pinned contracts path");
    if (out.ledger_path.empty()) throw std::runtime_error("ingress reservation profile handle lacks ledger path");
    if (out.ledger_backend != "sqlite-wal") throw std::runtime_error("ingress reservation profile only supports sqlite-wal for durable reservations");
    if (out.ledger_commit_mode != "immediate" && out.ledger_commit_mode != "batch") throw std::runtime_error("ingress reservation profile has unsupported ledger commit mode");
    if (out.ledger_backend_capabilities_path.empty() || !is_lowercase_sha256_hex(out.ledger_backend_capabilities_sha256)) throw std::runtime_error("ingress reservation profile handle lacks digest-pinned backend capabilities path");
    if (out.policy_envelope_key.empty() || contains_disallowed_security_control(out.policy_envelope_key)) throw std::runtime_error("ingress reservation profile has malformed policy envelope key");
    if (out.ledger_mode != "normal") throw std::runtime_error("ingress reservation profile only allows normal ledger mode at the production boundary");
    const std::string controls_actual = sha256_hex(read_file(out.controls_path));
    if (controls_actual != out.controls_sha256) throw std::runtime_error("ingress reservation controls digest pin mismatch");
    const std::string contracts_actual = sha256_hex(read_file(out.contracts_path));
    if (contracts_actual != out.contracts_sha256) throw std::runtime_error("ingress reservation contracts digest pin mismatch");
    const std::string capabilities_text = read_file(out.ledger_backend_capabilities_path);
    const std::string capabilities_actual = sha256_hex(capabilities_text);
    if (capabilities_actual != out.ledger_backend_capabilities_sha256) throw std::runtime_error("ingress reservation backend capabilities digest pin mismatch");
    return out;
}

Json sanitized_ingress_case(const Json& request, const IngressReservationProfileSelection& profile) {
    if (request.at("format").str() != kIngressReservationProfileRequestFormat) throw std::runtime_error("ingress reservation request has unsupported format");
    if (request.at("request_id").str().empty() || contains_disallowed_security_control(request.at("request_id").str())) throw std::runtime_error("ingress reservation request requires a control-free request_id");
    const std::string handle = request.at("config_handle").str();
    if (handle != profile.handle) throw std::runtime_error("ingress reservation request config_handle does not match selected operator profile handle");
    const Json& authenticated_context = request.at("authenticated_context");
    validate_authenticated_context_shape(authenticated_context);
    reject_forbidden_ingress_request_fields(request);
    Json tc = request.at("case");
    if (!tc.is_object()) throw std::runtime_error("ingress reservation request requires one case object");
    if (!tc.at("ingress_sender_replay").is_null()) {
        throw std::runtime_error("ingress reservation request case may not supply ledger-integrated sender replay evidence");
    }
    const std::string kind = tc.at("kind").str();
    if (kind != "openapi" && kind != "asyncapi") throw std::runtime_error("ingress reservation request case kind must be openapi or asyncapi");
    if (!tc.at("failure_injection").is_null() && !tc.at("failure_injection").str().empty()) {
        throw std::runtime_error("ingress reservation request cannot select failure_injection");
    }
    if (tc.at("preseed_replay_jti").boolean(false)) throw std::runtime_error("ingress reservation request cannot preseed replay jti state");
    if (tc.at("use_stale_jwks").boolean(false)) throw std::runtime_error("ingress reservation request cannot select stale JWKS behavior");
    if (tc.at("ledger_mode").is_string() && tc.at("ledger_mode").str("normal") != profile.ledger_mode) throw std::runtime_error("ingress reservation request cannot select ledger_mode");
    if (tc.at("policy_envelope_key").is_string() && tc.at("policy_envelope_key").str("normal") != profile.policy_envelope_key) throw std::runtime_error("ingress reservation request cannot select policy_envelope_key");
    const Json& metadata = kind == "openapi" ? tc.at("http_request").at("headers") : tc.at("event_envelope").at("attributes");
    const std::string requested_ledger_mode = json_string_field_case_insensitive(metadata, "x-anonsync-ledger-mode", profile.ledger_mode);
    if (requested_ledger_mode != profile.ledger_mode) throw std::runtime_error("ingress reservation request metadata cannot select ledger mode");
    const std::string requested_policy = json_string_field_case_insensitive(metadata, "x-anonsync-policy-envelope", profile.policy_envelope_key);
    if (requested_policy != profile.policy_envelope_key) throw std::runtime_error("ingress reservation request metadata cannot select policy envelope");
    tc.o["expected_action"] = json_string_value(kind == "asyncapi" ? "accept" : "allow");
    tc.o["failure_injection"] = Json();
    return tc;
}

std::string find_reserved_row_from_pending_report(const Json& pending_report, long long sequence) {
    const Json& rows = pending_report.at("pending_effects");
    if (!rows.is_array()) return "";
    for (const auto& row : rows.a) {
        if (row.at("sequence").integer(-1) == sequence && row.at("outbox_state").str() == "reserved") {
            std::ostringstream out;
            out << "    \"accepted\": true,\n"
                << "    \"ledger_sequence\": " << row.at("sequence").integer(0) << ",\n"
                << "    \"entry_hash\": \"" << json_escape(row.at("entry_hash").str()) << "\",\n"
                << "    \"case_id\": \"" << json_escape(row.at("case_id").str()) << "\",\n"
                << "    \"kind\": \"" << json_escape(row.at("kind").str()) << "\",\n"
                << "    \"operation_id\": \"" << json_escape(row.at("operation_id").str()) << "\",\n"
                << "    \"contract_digest_sha256\": \"" << json_escape(row.at("contract_digest_sha256").str()) << "\",\n"
                << "    \"action\": \"" << json_escape(row.at("action").str()) << "\",\n"
                << "    \"effect_idempotency_key\": \"" << json_escape(row.at("effect_idempotency_key").str()) << "\",\n"
                << "    \"outbox_state\": \"" << json_escape(row.at("outbox_state").str()) << "\",\n"
                << "    \"dispatch_attempts\": " << row.at("dispatch_attempts").integer(0) << "\n";
            return out.str();
        }
    }
    return "";
}

std::string ingress_reservation_report_json(const IngressReservationProfileSelection& profile,
                                            const std::string& request_sha256,
                                            const Json& request,
                                            const Json& kernel_report,
                                            const std::string& kernel_report_sha256,
                                            const std::string& pending_report_sha256,
                                            const std::string& reservation_fragment,
                                            int kernel_exit_code,
                                            const std::string& failure_reason) {
    const Json& counters = kernel_report.at("counters");
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << kIngressReservationReportFormat << "\",\n"
        << "  \"revision_id\": \"rev0638\",\n"
        << "  \"profile\": {\n"
        << "    \"format\": \"" << kIngressReservationProfileFormat << "\",\n"
        << "    \"profile_sha256\": \"" << json_escape(profile.profile_sha256) << "\",\n"
        << "    \"config_handle\": \"" << json_escape(profile.handle) << "\",\n"
        << "    \"digest_pin_verified\": true,\n"
        << "    \"controls_sha256\": \"" << json_escape(profile.controls_sha256) << "\",\n"
        << "    \"contracts_sha256\": \"" << json_escape(profile.contracts_sha256) << "\",\n"
        << "    \"ledger_backend_capabilities_sha256\": \"" << json_escape(profile.ledger_backend_capabilities_sha256) << "\",\n"
        << "    \"ledger_backend\": \"" << json_escape(profile.ledger_backend) << "\",\n"
        << "    \"ledger_commit_mode\": \"" << json_escape(profile.ledger_commit_mode) << "\",\n"
        << "    \"operator_paths_loaded_from_profile\": true\n"
        << "  },\n"
        << "  \"request\": {\n"
        << "    \"format\": \"" << json_escape(request.at("format").str()) << "\",\n"
        << "    \"request_id\": \"" << json_escape(request.at("request_id").str()) << "\",\n"
        << "    \"config_handle\": \"" << json_escape(request.at("config_handle").str()) << "\",\n"
        << "    \"request_sha256\": \"" << json_escape(request_sha256) << "\",\n"
        << "    \"transport_authenticated\": " << (request.at("authenticated_context").at("transport_authenticated").boolean(false) ? "true" : "false") << ",\n"
        << "    \"operator_field_rejection_enforced\": true,\n"
        << "    \"request_selects_handle_only\": true\n"
        << "  },\n"
        << "  \"kernel\": {\n"
        << "    \"exit_code\": " << kernel_exit_code << ",\n"
        << "    \"kernel_report_sha256\": \"" << json_escape(kernel_report_sha256) << "\",\n"
        << "    \"pending_report_sha256\": \"" << json_escape(pending_report_sha256) << "\",\n"
        << "    \"ledger_appended_entries\": " << counters.at("ledger_appended_entries").integer(0) << ",\n"
        << "    \"ledger_durable_line_count\": " << counters.at("ledger_durable_line_count").integer(0) << ",\n"
        << "    \"ledger_durable_head_hash\": \"" << json_escape(counters.at("ledger_durable_head_hash").str()) << "\",\n"
        << "    \"ledger_effect_outbox_reserved\": " << counters.at("ledger_effect_outbox_reserved").integer(0) << ",\n"
        << "    \"ledger_effect_outbox_inflight\": " << counters.at("ledger_effect_outbox_inflight").integer(0) << ",\n"
        << "    \"ledger_effect_outbox_terminal\": " << counters.at("ledger_effect_outbox_terminal").integer(0) << "\n"
        << "  },\n"
        << "  \"reservation\": {\n";
    if (!reservation_fragment.empty()) out << reservation_fragment;
    else out << "    \"accepted\": false,\n    \"failure_reason\": \"" << json_escape(failure_reason.empty() ? "no durable reservation was appended" : failure_reason) << "\"\n";
    out << "  },\n"
        << "  \"blocked_claim\": \"rev0638 profile-bound ingress reservation command returns local durable reservation evidence; it is not a deployed HTTP service, TLS terminator, proof-of-possession system, remote delivery proof, or distributed exactly-once protocol.\"\n"
        << "}\n";
    return out.str();
}


std::string random_hex_token(size_t byte_count) {
    std::vector<unsigned char> bytes(byte_count);
    if (bytes.empty() || RAND_bytes(bytes.data(), static_cast<int>(bytes.size())) != 1) {
        throw std::runtime_error("CSPRNG failure while creating ingress service workspace");
    }
    static const char* hex = "0123456789abcdef";
    std::string out;
    out.reserve(bytes.size() * 2);
    for (unsigned char b : bytes) {
        out.push_back(hex[(b >> 4) & 0xf]);
        out.push_back(hex[b & 0xf]);
    }
    return out;
}

std::filesystem::path create_private_ingress_workspace() {
    const std::filesystem::path base = std::filesystem::temp_directory_path();
    for (int i = 0; i < 32; ++i) {
        const std::filesystem::path dir = base / ("anonsync-ingress-service-" + random_hex_token(16));
        std::error_code ec;
        if (std::filesystem::create_directory(dir, ec)) {
            std::filesystem::permissions(dir,
                                         std::filesystem::perms::owner_all,
                                         std::filesystem::perm_options::replace,
                                         ec);
            if (ec) {
                std::error_code remove_ec;
                std::filesystem::remove(dir, remove_ec);
                throw std::runtime_error("could not restrict ingress service workspace permissions: " + ec.message());
            }
            return dir;
        }
    }
    throw std::runtime_error("could not create private ingress service workspace");
}

std::string service_failure_report_json(const IngressReservationServiceConfig& service_config,
                                        const std::string& request_sha256,
                                        const std::string& failure_reason,
                                        const IngressSenderPossessionVerification* sender_possession = nullptr) {
    const IngressSenderPossessionVerification empty_sender;
    const IngressSenderPossessionVerification& sender = sender_possession == nullptr ? empty_sender : *sender_possession;
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << kIngressReservationServiceReportFormat << "\",\n"
        << "  \"revision_id\": \"rev0647\",\n"
        << "  \"service\": {\n"
        << "    \"format\": \"" << kIngressReservationServiceConfigFormat << "\",\n"
        << "    \"service_id\": \"" << json_escape(service_config.service_id) << "\",\n"
        << "    \"service_config_sha256\": \"" << json_escape(service_config.service_config_sha256) << "\",\n"
        << "    \"service_config_digest_pin_verified\": " << (service_config.service_config_digest_pin_verified ? "true" : "false") << ",\n"
        << "    \"profile_sha256\": \"" << json_escape(service_config.ingress_profile_sha256) << "\",\n"
        << "    \"caller_binding_required\": " << (service_config.caller_binding_required ? "true" : "false") << ",\n"
        << "    \"caller_binding_material_version\": \"" << json_escape(service_config.caller_binding_material_version) << "\",\n"
        << "    \"caller_binding_key_id\": \"" << json_escape(service_config.caller_binding_public_jwk_kid) << "\",\n"
        << "    \"caller_binding_alg\": \"" << json_escape(service_config.caller_binding_public_jwk_alg) << "\",\n"
        << "    \"symmetric_caller_secret_present\": " << (!service_config.caller_binding_hmac_sha256_secret.empty() ? "true" : "false") << ",\n"
        << "    \"sender_possession_verified\": " << (sender.verified ? "true" : "false") << ",\n"
        << "    \"sender_possession_material_sha256\": \"" << json_escape(sender.material_sha256) << "\",\n"
        << "    \"sender_replay_cache_format\": \"" << json_escape(sender.replay_cache_format.empty() ? kIngressSenderReplayCacheFormat : sender.replay_cache_format) << "\",\n"
        << "    \"sender_replay_key_material_version\": \"" << kIngressSenderReplayKeyMaterialVersion << "\",\n"
        << "    \"sender_replay_cache_instance_id\": \"" << json_escape(sender.replay_cache_instance_id.empty() ? service_config.sender_replay_cache_instance_id : sender.replay_cache_instance_id) << "\",\n"
        << "    \"sender_replay_cache_key_sha256\": \"" << json_escape(sender.replay_cache_key_sha256) << "\",\n"
        << "    \"sender_replay_cache_reserved\": " << (sender.replay_cache_reserved ? "true" : "false") << ",\n"
        << "    \"sender_replay_observed_at_epoch\": " << sender.replay_observed_at_epoch << ",\n"
        << "    \"sender_replay_cache_required\": true,\n"
        << "    \"sender_replay_window_seconds\": " << (sender.replay_window_seconds > 0 ? sender.replay_window_seconds : service_config.sender_replay_window_seconds) << ",\n"
        << "    \"sender_replay_future_skew_seconds\": " << service_config.sender_replay_future_skew_seconds << ",\n"
        << "    \"sender_replay_nonce_uniqueness_scope\": \"retained-replay-window\",\n"
        << "    \"trusted_transport_context_required\": true,\n"
        << "    \"request_identity_fields_forbidden\": true,\n"
        << "    \"operator_profile_digest_pin_configured\": " << (!service_config.ingress_profile_sha256.empty() ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"request\": {\n"
        << "    \"request_sha256\": \"" << json_escape(request_sha256) << "\",\n"
        << "    \"request_filesystem_operands_accepted\": false,\n"
        << "    \"request_body_supplied_as_string_to_service_api\": true,\n"
        << "    \"trusted_transport_context_is_separate_api_parameter\": true,\n"
        << "    \"request_body_trusted_identity_fields_are_forbidden\": true,\n"
        << "    \"sender_principal\": \"" << json_escape(sender.principal) << "\",\n"
        << "    \"sender_authenticator\": \"" << json_escape(sender.authenticator) << "\",\n"
        << "    \"sender_nonce\": \"" << json_escape(sender.nonce) << "\",\n"
        << "    \"sender_issued_at_epoch\": " << sender.issued_at_epoch << "\n"
        << "  },\n"
        << "  \"reservation\": {\n"
        << "    \"accepted\": false,\n"
        << "    \"failure_reason\": \"" << json_escape(failure_reason) << "\"\n"
        << "  },\n"
        << "  \"service_boundary\": {\n"
        << "    \"profile_preflight_before_sender_replay_reservation\": true,\n"
        << "    \"profile_rejection_consumes_sender_nonce\": false,\n"
        << "    \"sender_replay_cache_and_ledger_share_one_transaction\": true,\n"
        << "    \"sender_replay_reservation_survived_failed_request\": " << (sender.replay_cache_reserved ? "true" : "false") << ",\n"
        << "    \"post_preflight_crash_or_ledger_failure_can_consume_sender_nonce\": false\n"
        << "  },\n"
        << "  \"blocked_claim\": \"rev0648 retains ledger-integrated sender replay and provenance-bound relay/downstream evidence, and preflights relay signer/trust authority before any outbox claim or downstream touch. It is still a local CLI/library adapter, not TLS, mTLS, DPoP, a distributed nonce authority, HSM custody, or proof of remote delivery.\"\n"
        << "}\n";
    return out.str();
}

std::string ingress_reservation_service_report_json(const IngressReservationServiceConfig& service_config,
                                                    const IngressSenderPossessionVerification& sender_possession,
                                                    const std::string& request_sha256,
                                                    const std::string& legacy_report_sha256,
                                                    const Json& legacy_report,
                                                    int status_code) {
    const Json& legacy_reservation = legacy_report.at("reservation");
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << kIngressReservationServiceReportFormat << "\",\n"
        << "  \"revision_id\": \"rev0647\",\n"
        << "  \"service\": {\n"
        << "    \"format\": \"" << kIngressReservationServiceConfigFormat << "\",\n"
        << "    \"service_id\": \"" << json_escape(service_config.service_id) << "\",\n"
        << "    \"service_config_sha256\": \"" << json_escape(service_config.service_config_sha256) << "\",\n"
        << "    \"service_config_digest_pin_verified\": " << (service_config.service_config_digest_pin_verified ? "true" : "false") << ",\n"
        << "    \"profile_sha256\": \"" << json_escape(service_config.ingress_profile_sha256) << "\",\n"
        << "    \"caller_binding_required\": " << (service_config.caller_binding_required ? "true" : "false") << ",\n"
        << "    \"caller_binding_material_version\": \"" << json_escape(service_config.caller_binding_material_version) << "\",\n"
        << "    \"caller_binding_key_id\": \"" << json_escape(service_config.caller_binding_public_jwk_kid) << "\",\n"
        << "    \"caller_binding_alg\": \"" << json_escape(service_config.caller_binding_public_jwk_alg) << "\",\n"
        << "    \"symmetric_caller_secret_present\": " << (!service_config.caller_binding_hmac_sha256_secret.empty() ? "true" : "false") << ",\n"
        << "    \"sender_possession_verified\": " << (sender_possession.verified ? "true" : "false") << ",\n"
        << "    \"sender_possession_material_sha256\": \"" << json_escape(sender_possession.material_sha256) << "\",\n"
        << "    \"sender_replay_cache_format\": \"" << json_escape(sender_possession.replay_cache_format) << "\",\n"
        << "    \"sender_replay_key_material_version\": \"" << kIngressSenderReplayKeyMaterialVersion << "\",\n"
        << "    \"sender_replay_cache_instance_id\": \"" << json_escape(sender_possession.replay_cache_instance_id) << "\",\n"
        << "    \"sender_replay_cache_key_sha256\": \"" << json_escape(sender_possession.replay_cache_key_sha256) << "\",\n"
        << "    \"sender_replay_cache_reserved\": " << (sender_possession.replay_cache_reserved ? "true" : "false") << ",\n"
        << "    \"sender_replay_observed_at_epoch\": " << sender_possession.replay_observed_at_epoch << ",\n"
        << "    \"sender_replay_window_seconds\": " << sender_possession.replay_window_seconds << ",\n"
        << "    \"sender_replay_nonce_uniqueness_scope\": \"retained-replay-window\",\n"
        << "    \"sender_replay_rows_pruned_by_issued_at_window\": true,\n"
        << "    \"operator_profile_digest_pin_verified_before_adapter_execution\": true,\n"
        << "    \"trusted_transport_context_required\": true,\n"
        << "    \"request_identity_fields_forbidden\": true,\n"
        << "    \"request_cannot_select_profile_or_operator_paths\": true\n"
        << "  },\n"
        << "  \"request\": {\n"
        << "    \"request_sha256\": \"" << json_escape(request_sha256) << "\",\n"
        << "    \"request_supplied_filesystem_operands\": false,\n"
        << "    \"request_body_supplied_as_string_to_service_api\": true,\n"
        << "    \"trusted_transport_context_supplied_as_separate_argument\": true,\n"
        << "    \"request_body_trusted_identity_fields_rejected\": true,\n"
        << "    \"sender_principal\": \"" << json_escape(sender_possession.principal) << "\",\n"
        << "    \"sender_authenticator\": \"" << json_escape(sender_possession.authenticator) << "\",\n"
        << "    \"sender_case_sha256\": \"" << json_escape(sender_possession.case_sha256) << "\",\n"
        << "    \"sender_nonce\": \"" << json_escape(sender_possession.nonce) << "\",\n"
        << "    \"sender_issued_at_epoch\": " << sender_possession.issued_at_epoch << ",\n"
        << "    \"sender_proof_kid\": \"" << json_escape(sender_possession.proof_kid) << "\",\n"
        << "    \"sender_proof_alg\": \"" << json_escape(sender_possession.proof_alg) << "\",\n"
        << "    \"sender_proof_verification_reason\": \"" << json_escape(sender_possession.verification_reason) << "\",\n"
        << "    \"legacy_request_evidence\": " << canonical_json(legacy_report.at("request")) << "\n"
        << "  },\n"
        << "  \"profile\": " << canonical_json(legacy_report.at("profile")) << ",\n"
        << "  \"kernel\": " << canonical_json(legacy_report.at("kernel")) << ",\n"
        << "  \"reservation\": " << canonical_json(legacy_reservation) << ",\n"
        << "  \"service_boundary\": {\n"
        << "    \"status_code\": " << status_code << ",\n"
        << "    \"profile_preflight_before_sender_replay_reservation\": true,\n"
        << "    \"profile_rejection_consumes_sender_nonce\": false,\n"
        << "    \"legacy_profile_command_report_format\": \"" << json_escape(legacy_report.at("format").str()) << "\",\n"
        << "    \"legacy_profile_command_report_sha256\": \"" << json_escape(legacy_report_sha256) << "\",\n"
        << "    \"profile_command_reused_as_internal_adapter\": true,\n"
        << "    \"public_api_accepts_digest_pinned_operator_config_handle_not_mutable_security_fields\": true,\n"
        << "    \"public_api_accepts_trusted_context_and_request_as_separate_parameters\": true,\n"
        << "    \"public_api_accepts_request_json_text_not_request_path\": true,\n"
        << "    \"sender_possession_checked_before_profile_adapter\": true,\n"
        << "    \"sender_replay_cache_checked_after_profile_preflight_before_actual_append\": true,\n"
        << "    \"sender_replay_cache_and_ledger_share_one_transaction\": true,\n"
        << "    \"valid_sender_proof_can_be_consumed_by_profile_rejection\": false,\n"
        << "    \"post_preflight_crash_or_ledger_failure_can_consume_sender_nonce\": false\n"
        << "  },\n"
        << "  \"blocked_claim\": \"rev0648 keeps sender replay reservation in the same SQLite/WAL transaction as the prepared entry and outbox row, binds local downstream relay results to adapter provenance, and verifies relay transition authority before claiming work. It is still a local library/CLI adapter, not a deployed HTTP service, TLS authenticator, DPoP verifier, remote delivery proof, distributed nonce authority, or distributed exactly-once protocol.\"\n"
        << "}\n";
    return out.str();
}

IngressReservationServiceConfig load_ingress_service_config(const std::string& service_config_path,
                                                            const std::string& expected_sha256) {
    if (service_config_path.empty()) throw std::runtime_error("ingress service requires a service config path");
    if (!is_lowercase_sha256_hex(expected_sha256)) throw std::runtime_error("ingress service requires a lowercase sha256 service config pin");
    const std::string text = read_file_bounded(service_config_path, kIngressMaximumServiceConfigBytes, "ingress service config");
    const std::string actual_sha256 = sha256_hex(text);
    if (actual_sha256 != expected_sha256) throw std::runtime_error("ingress service config digest pin mismatch");
    Json root = parse_json_text(text);
    reject_case_insensitive_duplicate_object_keys(root, "ingress service config");
    static const std::set<std::string> allowed_config_fields = {
        "blocked_claim", "caller_binding_hmac_sha256_secret", "caller_binding_material_version",
        "caller_binding_public_jwk", "caller_binding_required", "caller_binding_secret_id", "enabled",
        "format", "ingress_profile_path", "ingress_profile_sha256", "revision_id",
        "sender_replay_cache_instance_id", "sender_replay_cache_path", "sender_replay_future_skew_seconds",
        "sender_replay_window_seconds", "service_id"
    };
    for (const auto& kv : root.o) {
        if (!allowed_config_fields.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("ingress service config contains unsupported field: " + kv.first);
        }
    }
    if (root.at("format").str() != kIngressReservationServiceConfigFormat) throw std::runtime_error("ingress service config has unsupported format");
    if (!root.at("enabled").boolean(false)) throw std::runtime_error("ingress service config is disabled");
    IngressReservationServiceConfig out;
    out.service_id = root.at("service_id").str();
    out.service_config_path = service_config_path;
    out.service_config_sha256 = actual_sha256;
    out.service_config_digest_pin_verified = true;
    out.ingress_profile_path = root.at("ingress_profile_path").str();
    out.ingress_profile_sha256 = root.at("ingress_profile_sha256").str();
    out.caller_binding_required = root.at("caller_binding_required").boolean(false);
    out.caller_binding_material_version = root.at("caller_binding_material_version").str();
    out.caller_binding_secret_id = root.at("caller_binding_secret_id").str();
    out.caller_binding_hmac_sha256_secret = root.at("caller_binding_hmac_sha256_secret").str();
    const Json& public_jwk = root.at("caller_binding_public_jwk");
    reject_case_insensitive_duplicate_object_keys(public_jwk, "ingress service caller public JWK");
    static const std::set<std::string> allowed_jwk_fields = {"alg", "e", "kid", "kty", "n"};
    for (const auto& kv : public_jwk.o) {
        if (!allowed_jwk_fields.count(lower_ascii_copy(kv.first))) {
            throw std::runtime_error("ingress service caller public JWK contains unsupported field: " + kv.first);
        }
    }
    out.caller_binding_public_jwk_kid = public_jwk.at("kid").str();
    out.caller_binding_public_jwk_alg = public_jwk.at("alg").str();
    out.caller_binding_public_jwk_n = public_jwk.at("n").str();
    out.caller_binding_public_jwk_e = public_jwk.at("e").str();
    out.sender_replay_cache_path = root.at("sender_replay_cache_path").str();
    out.sender_replay_cache_instance_id = root.at("sender_replay_cache_instance_id").str();
    out.sender_replay_window_seconds = require_json_integer_in_range(root.at("sender_replay_window_seconds"),
                                                                      "ingress service sender_replay_window_seconds",
                                                                      1,
                                                                      86400);
    out.sender_replay_future_skew_seconds = require_json_integer_in_range(root.at("sender_replay_future_skew_seconds"),
                                                                           "ingress service sender_replay_future_skew_seconds",
                                                                           0,
                                                                           300);
    if (!is_printable_handle(out.service_id)) throw std::runtime_error("ingress service config has malformed service_id");
    if (out.ingress_profile_path.empty() || !is_lowercase_sha256_hex(out.ingress_profile_sha256)) throw std::runtime_error("ingress service config must digest-pin an ingress profile");
    if (!out.caller_binding_required) throw std::runtime_error("ingress service config must require caller sender-possession binding");
    if (out.caller_binding_material_version != kIngressSenderPossessionMaterialVersion) throw std::runtime_error("ingress service config has unsupported caller binding material version");
    if (!out.caller_binding_secret_id.empty() || !out.caller_binding_hmac_sha256_secret.empty()) {
        throw std::runtime_error("ingress service config must not contain a symmetric caller binding secret under asymmetric sender possession");
    }
    if (!public_jwk.is_object() || public_jwk.at("kty").str() != "RSA" || out.caller_binding_public_jwk_alg != "RS256" || !is_printable_handle(out.caller_binding_public_jwk_kid)) {
        throw std::runtime_error("ingress service config must own a pinned RSA RS256 caller public JWK");
    }
    if (out.sender_replay_cache_path.empty()) throw std::runtime_error("ingress service config must own a sender replay cache path");
    if (!is_sender_replay_cache_instance_id(out.sender_replay_cache_instance_id)) throw std::runtime_error("ingress service config must own a printable sender replay cache instance id");
    if (out.sender_replay_window_seconds < 1 || out.sender_replay_window_seconds > 86400) throw std::runtime_error("ingress service config must set sender replay window between 1 and 86400 seconds");
    if (out.sender_replay_future_skew_seconds < 0 || out.sender_replay_future_skew_seconds > 300) throw std::runtime_error("ingress service config must set sender replay future skew between 0 and 300 seconds");
    reject_sender_replay_cache_symlinks(out.sender_replay_cache_path);
    try { (void)jwk_to_pkey(out.caller_binding_public_jwk_n, out.caller_binding_public_jwk_e); }
    catch (const std::exception& e) { throw std::runtime_error(std::string("ingress service config caller public JWK is invalid: ") + e.what()); }
    return out;
}



struct IngressProfileAdapterExecution {
    IngressReservationProfileSelection profile;
    int kernel_exit_code = 1;
    Json kernel_report;
    std::string kernel_report_sha256;
    std::string pending_report_sha256;
    std::string reservation_fragment;
    std::string failure_reason;
    std::string request_sha256;
};

IngressProfileAdapterExecution execute_ingress_profile_adapter(const std::string& ingress_profile_path,
                                                               const std::string& ingress_profile_sha256,
                                                               const Json& internal_request,
                                                               const std::string& artifact_stem,
                                                               const std::string& ledger_path_override,
                                                               const IngressReservationServiceConfig* service_config,
                                                               const IngressSenderPossessionVerification* sender_replay) {
    IngressProfileAdapterExecution out;
    const std::string internal_request_text = canonical_json(internal_request) + "\n";
    out.request_sha256 = sha256_hex(internal_request_text);
    const std::string handle = internal_request.at("config_handle").str();
    out.profile = load_ingress_reservation_profile_selection(ingress_profile_path, ingress_profile_sha256, handle);
    IngressReservationProfileSelection run_profile = out.profile;
    if (!ledger_path_override.empty()) {
        run_profile.ledger_path = ledger_path_override;
    }
    Json one_case = sanitized_ingress_case(internal_request, out.profile);
    if (service_config != nullptr && sender_replay != nullptr) {
        one_case.o["ingress_sender_replay"] = ingress_sender_replay_evidence_json(*service_config, *sender_replay);
    }
    const std::string case_jsonl_path = artifact_stem + ".case.jsonl";
    const std::string kernel_report_path = artifact_stem + ".kernel.json";
    const std::string pending_report_path = artifact_stem + ".pending.json";
    write_file(case_jsonl_path, canonical_json(one_case) + "\n");
    out.kernel_exit_code = run(run_profile.controls_path,
                               kernel_report_path,
                               run_profile.contracts_path,
                               case_jsonl_path,
                               run_profile.ledger_path,
                               false,
                               run_profile.ledger_commit_mode,
                               run_profile.ledger_backend,
                               run_profile.ledger_backend_capabilities_path,
                               "", "", "", "", "");
    const std::string kernel_text = read_file(kernel_report_path);
    out.kernel_report_sha256 = sha256_hex(kernel_text);
    out.kernel_report = parse_json_text(kernel_text);
    const Json& counters = out.kernel_report.at("counters");
    const Json& failed_samples = out.kernel_report.at("failed_samples");
    if (failed_samples.is_array() && !failed_samples.a.empty()) out.failure_reason = failed_samples.at(0).str();
    if (out.kernel_exit_code == 0 && counters.at("ledger_appended_entries").integer(0) == 1) {
        const int pending_rc = run_sqlite_effect_pending_report_command(run_profile.ledger_path, pending_report_path);
        if (pending_rc != 0) throw std::runtime_error("ingress reservation could not read pending-effect report after append");
        const std::string pending_text = read_file(pending_report_path);
        out.pending_report_sha256 = sha256_hex(pending_text);
        Json pending = parse_json_text(pending_text);
        out.reservation_fragment = find_reserved_row_from_pending_report(pending, counters.at("ledger_durable_line_count").integer(0));
        if (out.reservation_fragment.empty()) out.failure_reason = "durable append succeeded but reserved outbox row was not found for the new ledger sequence";
    }
    if (out.pending_report_sha256.empty()) out.pending_report_sha256 = std::string(64, '0');
    return out;
}

void cleanup_ingress_profile_adapter_artifacts(const std::string& artifact_stem) {
    std::remove((artifact_stem + ".case.jsonl").c_str());
    std::remove((artifact_stem + ".kernel.json").c_str());
    std::remove((artifact_stem + ".pending.json").c_str());
}

bool ingress_profile_adapter_accepted(const IngressProfileAdapterExecution& execution) {
    return execution.kernel_exit_code == 0 && !execution.reservation_fragment.empty();
}
IngressReservationResult reserve_ingress_request_json(const IngressReservationServiceHandle& operator_service_handle,
                                                       const IngressTransportContext& trusted_transport_context,
                                                       const std::string& request_json_text) {
    IngressReservationResult result;
    const bool request_size_ok = request_json_text.size() <= kIngressMaximumRequestBytes;
    const std::string request_sha = request_size_ok ? sha256_hex(request_json_text) : std::string(64, '0');
    IngressReservationServiceConfig service_config;
    service_config.service_config_path = operator_service_handle.service_config_path;
    service_config.service_config_sha256 = operator_service_handle.service_config_sha256;
    IngressSenderPossessionVerification sender_possession;
    bool sender_possession_result_available = false;
    std::filesystem::path dir;
    try {
        if (!request_size_ok) throw std::runtime_error("ingress service request exceeds the maximum accepted size");
        validate_trusted_transport_context(trusted_transport_context);
        service_config = load_ingress_service_config(operator_service_handle.service_config_path,
                                                     operator_service_handle.service_config_sha256);
        Json request = parse_json_text(request_json_text);
        reject_forbidden_ingress_service_request_fields(request);
        sender_possession = verify_ingress_sender_possession(service_config,
                                                              trusted_transport_context,
                                                              request,
                                                              false);
        prepare_ingress_sender_replay_for_ledger(service_config, sender_possession);
        sender_possession_result_available = true;
        const Json internal_request = make_internal_profile_request(request, trusted_transport_context);
        dir = create_private_ingress_workspace();
        const std::string stem_base = (dir / ("ingress-" + request_sha.substr(0, 12))).string();
        const std::string preflight_ledger_path = (dir / "preflight-ledger.sqlite").string();
        IngressProfileAdapterExecution preflight;
        try {
            preflight = execute_ingress_profile_adapter(service_config.ingress_profile_path,
                                                        service_config.ingress_profile_sha256,
                                                        internal_request,
                                                        stem_base + ".preflight",
                                                        preflight_ledger_path,
                                                        &service_config,
                                                        &sender_possession);
        } catch (const std::exception& e) {
            cleanup_ingress_profile_adapter_artifacts(stem_base + ".preflight");
            throw std::runtime_error(std::string("ingress profile preflight rejected before sender replay reservation: ") + e.what());
        }
        cleanup_ingress_profile_adapter_artifacts(stem_base + ".preflight");
        if (!ingress_profile_adapter_accepted(preflight)) {
            throw std::runtime_error("ingress profile preflight rejected before sender replay reservation: " +
                                     (preflight.failure_reason.empty() ? "no durable reservation would be appended" : preflight.failure_reason));
        }
        IngressProfileAdapterExecution actual = execute_ingress_profile_adapter(service_config.ingress_profile_path,
                                                                                service_config.ingress_profile_sha256,
                                                                                internal_request,
                                                                                stem_base + ".actual",
                                                                                "",
                                                                                &service_config,
                                                                                &sender_possession);
        cleanup_ingress_profile_adapter_artifacts(stem_base + ".actual");
        sender_possession.replay_cache_path = actual.profile.ledger_path;
        sender_possession.replay_cache_reserved = ingress_profile_adapter_accepted(actual);
        result.status_code = ingress_profile_adapter_accepted(actual) ? 0 : (actual.kernel_exit_code == 0 ? 2 : actual.kernel_exit_code);
        result.accepted = ingress_profile_adapter_accepted(actual);
        result.failure_reason = result.accepted ? std::string() :
                                (actual.failure_reason.empty() ? "no durable reservation was appended" : actual.failure_reason);
        const std::string legacy_report = ingress_reservation_report_json(actual.profile,
                                                                          actual.request_sha256,
                                                                          internal_request,
                                                                          actual.kernel_report,
                                                                          actual.kernel_report_sha256,
                                                                          actual.pending_report_sha256,
                                                                          actual.reservation_fragment,
                                                                          actual.kernel_exit_code,
                                                                          actual.failure_reason);
        const std::string legacy_sha = sha256_hex(legacy_report);
        Json legacy = parse_json_text(legacy_report);
        result.report_json = ingress_reservation_service_report_json(service_config, sender_possession, request_sha, legacy_sha, legacy, result.status_code);
    } catch (const std::exception& e) {
        result.status_code = 1;
        result.accepted = false;
        result.failure_reason = e.what();
        result.report_json = service_failure_report_json(service_config,
                                                         request_sha,
                                                         result.failure_reason,
                                                         sender_possession_result_available ? &sender_possession : nullptr);
    }
    if (!dir.empty()) {
        std::error_code ec;
        std::filesystem::remove_all(dir, ec);
    }
    return result;
}


int run(const std::string& controls_path, const std::string& report_path, const std::string& contracts_path, const std::string& cases_jsonl_path, const std::string& ledger_path, bool ledger_reset, const std::string& ledger_commit_mode, const std::string& ledger_backend, const std::string& ledger_backend_capabilities_path, const std::string& ledger_snapshot_path, const std::string& ledger_restore_from_snapshot_path, const std::string& ledger_snapshot_manifest_path, const std::string& ledger_snapshot_trust_profile_path, const std::string& ledger_snapshot_trust_profile_sha256) {
    std::string controls_text = read_file(controls_path);
    Json root = parse_json_text(controls_text);
    const Json& profile_json = root.at("identity_profile");
    const Json& jwk_json = profile_json.at("active_jwk");
    Profile profile;
    profile.issuer = profile_json.at("issuer").str();
    profile.audience = profile_json.at("audience").str();
    profile.active_kid = profile_json.at("active_kid").str();
    profile.required_typ = profile_json.at("required_jwt_typ").str("at+jwt");
    profile.now_epoch = root.at("evaluation_time_epoch").integer();
    profile.fresh_jwks_expires_epoch = profile_json.at("fresh_jwks_expires_epoch").integer();
    profile.stale_jwks_expires_epoch = profile_json.at("stale_jwks_expires_epoch").integer();
    profile.public_key = jwk_to_pkey(jwk_json.at("n").str(), jwk_json.at("e").str());
    profile.proof_binding_required = profile_json.at("proof_binding_required").boolean(false);
    profile.proof_binding_active_kid = profile_json.at("proof_binding_active_kid").str(profile.active_kid);
    profile.proof_binding_material_version = profile_json.at("proof_binding_material_version").str("anonsync-proof-binding-v2-lp-hmac-sha256");
    profile.proof_binding_secret_id = profile_json.at("proof_binding_secret_id").str();
    profile.proof_binding_hmac_sha256_secret = profile_json.at("proof_binding_hmac_sha256_secret").str();
    if (profile.proof_binding_required) {
        if (profile.proof_binding_active_kid.empty() || profile.proof_binding_active_kid != profile.active_kid) {
            throw std::runtime_error("object/event proof binding active kid must match the JWT cnf.kid fixture profile");
        }
        if (profile.proof_binding_material_version != "anonsync-proof-binding-v2-lp-hmac-sha256") {
            throw std::runtime_error("unsupported object/event proof binding material version");
        }
        if (profile.proof_binding_secret_id.empty() || profile.proof_binding_hmac_sha256_secret.empty()) {
            throw std::runtime_error("object/event proof binding requires a configured HMAC secret id and secret");
        }
    }

    const Json& policy_json = root.at("policy_profile");
    PolicyProfile policy;
    policy.payload_type = policy_json.at("payload_type").str();
    policy.expected_revision = policy_json.at("expected_revision").str();
    policy.expected_bundle_version = policy_json.at("expected_bundle_version").str();
    policy.minimum_sequence = policy_json.at("minimum_sequence").integer();
    policy.operation_contract_root_sha256 = policy_json.at("operation_contract_root_sha256").str();
    policy.operation_contract_table_digest_sha256 = policy_json.at("operation_contract_table_digest_sha256").str();
    if (policy_json.at("envelopes").is_object()) {
        for (const auto& kv : policy_json.at("envelopes").o) policy.envelopes.emplace(kv.first, kv.second);
    }

    std::string contracts_text;
    std::unique_ptr<OperationContractTable> contracts;
    std::string contracts_sha;
    std::string contract_root;
    if (!contracts_path.empty()) {
        contracts_text = read_file(contracts_path);
        contracts = std::make_unique<OperationContractTable>(load_operation_contract_table(contracts_path, contracts_text));
        contracts_sha = contracts->table_digest_sha256;
        contract_root = contracts->operation_contract_root_sha256;
        if (contract_root != policy.operation_contract_root_sha256) {
            throw std::runtime_error("operation contract table root does not match signed policy bundle root");
        }
        if (!is_lowercase_sha256_hex(policy.operation_contract_table_digest_sha256)) {
            throw std::runtime_error("policy profile is missing the operator-pinned operation_contract_table_digest_sha256");
        }
        if (contracts_sha != policy.operation_contract_table_digest_sha256) {
            throw std::runtime_error("operation contract table digest does not match operator-pinned policy profile digest");
        }
    }

    std::unordered_set<std::string> seen_jti;
    std::map<std::string, std::pair<bool, std::string>> policy_cache;
    Counters counters;
    std::string capabilities_text;
    std::string capabilities_sha;
    bool capability_requires_signed_snapshot_manifest = false;
    bool capability_requires_trust_profile_digest_pin = false;
    int capability_manifest_version = 0;
    if (!ledger_backend_capabilities_path.empty()) {
        capabilities_text = read_file(ledger_backend_capabilities_path);
        capabilities_sha = validate_replay_backend_capability_manifest(capabilities_text, ledger_backend, ledger_commit_mode, ledger_path);
        Json capability_root = parse_json_text(capabilities_text);
        capability_manifest_version = replay_backend_capability_manifest_version(capability_root);
        capability_requires_signed_snapshot_manifest = capability_manifest_version >= 5 && capability_root.at("backends").at(ledger_backend).at("signed_snapshot_manifest_required").boolean(false);
        capability_requires_trust_profile_digest_pin = capability_manifest_version >= 8 && capability_root.at("backends").at(ledger_backend).at("snapshot_trust_profile_digest_pin_required").boolean(false);
        if (ledger_backend == "sqlite-wal" && capability_manifest_version != 42) {
            throw std::runtime_error("sqlite-wal replay-ledger backend rejects downgraded backend capability manifest; v42 is required");
        }
        counters.ledger_backend_capability_manifest_checks = 1;
    }
    if (!ledger_restore_from_snapshot_path.empty()) {
        if (ledger_backend != "sqlite-wal") throw std::runtime_error("snapshot restore is only supported for the sqlite-wal replay-ledger backend");
        if (ledger_path.empty()) throw std::runtime_error("snapshot restore requires --ledger destination path");
        if (ledger_backend_capabilities_path.empty()) {
            throw std::runtime_error("sqlite-wal signed snapshot restore requires current v42 backend capability manifest");
        }
        if (capability_manifest_version != 42) {
            throw std::runtime_error("sqlite-wal signed snapshot restore rejects downgraded backend capability manifest; v42 is required");
        }
        if (!capability_requires_signed_snapshot_manifest || !capability_requires_trust_profile_digest_pin) {
            throw std::runtime_error("sqlite-wal v31 signed snapshot restore requires signed manifests and trust-profile digest pins");
        }
        if (ledger_snapshot_manifest_path.empty() || ledger_snapshot_trust_profile_path.empty()) {
            throw std::runtime_error("signed snapshot restore requires --ledger-snapshot-manifest and --ledger-snapshot-trust-profile");
        }
        if (ledger_snapshot_trust_profile_sha256.empty()) {
            throw std::runtime_error("capability v8+ signed snapshot restore requires --ledger-snapshot-trust-profile-sha256");
        }
        const std::string pinned_trust_profile_text = read_trust_profile_with_digest_pin(ledger_snapshot_trust_profile_path, ledger_snapshot_trust_profile_sha256);
        counters.ledger_sqlite_trust_profile_digest_verifications = 1;
        SqliteSnapshotManifestVerification signed_snapshot_verification = verify_sqlite_snapshot_manifest_with_trust_profile_text(ledger_snapshot_manifest_path, pinned_trust_profile_text, ledger_restore_from_snapshot_path);
        counters.ledger_sqlite_snapshot_manifest_verifications = 1;
        restore_sqlite_snapshot_into_ledger_verified(ledger_restore_from_snapshot_path, ledger_path, signed_snapshot_verification);
        counters.ledger_sqlite_snapshot_restores = 1;
        counters.ledger_sqlite_restore_rollback_guard_checks = 1;
    }
    const bool restored_from_snapshot = !ledger_restore_from_snapshot_path.empty();
    std::unique_ptr<IReplayLedgerBackend> ledger = create_replay_ledger_backend(ledger_backend);
    ledger->load(ledger_path, ledger_reset && ledger_restore_from_snapshot_path.empty(), ledger_commit_mode);
    auto copy_ledger_stats = [&]() {
        ReplayLedgerStats st = ledger->stats();
        counters.ledger_backend_name = st.backend_name;
        counters.ledger_loaded_entries = st.loaded_entries;
        counters.ledger_appended_entries = st.appended_entries;
        counters.ledger_atomic_rewrite_commits = st.atomic_rewrite_commits;
        counters.ledger_directory_fsync_attempts = st.directory_fsync_attempts;
        counters.ledger_lock_acquire_attempts = st.lock_acquire_attempts;
        counters.ledger_lock_contention_denials = st.lock_contention_denials;
        counters.ledger_journal_records_written = st.journal_records_written;
        counters.ledger_journal_recovered_after_commit = st.journal_recovered_after_commit;
        counters.ledger_journal_rejections = st.journal_rejections;
        counters.ledger_batch_flush_commits = st.batch_flush_commits;
        counters.ledger_batch_pending_entries_peak = st.batch_pending_entries_peak;
        counters.ledger_sqlite_transactions = st.sqlite_transactions;
        counters.ledger_sqlite_wal_checkpoints = st.sqlite_wal_checkpoints;
        counters.ledger_sqlite_integrity_checks = st.sqlite_integrity_checks;
        counters.ledger_sqlite_profile_checks = st.sqlite_profile_checks;
        counters.ledger_sqlite_corruption_rejections = st.sqlite_corruption_rejections;
        counters.ledger_sqlite_backup_snapshots = st.sqlite_backup_snapshots;
        counters.ledger_sqlite_snapshot_verifications = st.sqlite_snapshot_verifications;
        counters.ledger_sqlite_snapshot_restores = (restored_from_snapshot ? 1 : 0) + st.sqlite_snapshot_restores;
        counters.ledger_sqlite_snapshot_manifest_verifications = std::max(counters.ledger_sqlite_snapshot_manifest_verifications, st.sqlite_snapshot_manifest_verifications);
        counters.ledger_durable_line_count = st.durable_line_count;
        counters.ledger_durable_head_hash = st.durable_head_hash;
        counters.ledger_host_capability_probe_checks = st.host_capability_probe_checks;
        counters.ledger_backend_factory_selections = st.backend_factory_selections;
        counters.ledger_backend_capability_manifest_mismatches = st.backend_capability_manifest_mismatches;
        counters.ledger_effect_terminal_transitions = st.effect_terminal_transitions;
        counters.ledger_effect_transition_rejections = st.effect_transition_rejections;
        counters.ledger_effect_transition_line_count = st.effect_transition_line_count;
        counters.ledger_effect_transition_head_hash = st.effect_transition_head_hash;
        counters.ledger_effect_outbox_reserved = st.effect_outbox_reserved;
        counters.ledger_effect_outbox_inflight = st.effect_outbox_inflight;
        counters.ledger_effect_outbox_terminal = st.effect_outbox_terminal;
    };
    copy_ledger_stats();
    std::vector<std::string> failed_samples;
    const Json& normalized_cases = root.at("normalized_cases");
    const bool use_jsonl_cases = !cases_jsonl_path.empty();
    const bool use_normalized_cases = use_jsonl_cases || normalized_cases.is_array();
    if (use_normalized_cases && contracts == nullptr) {
        throw std::runtime_error("normalized request/event controls require --contracts for C++ route/channel selection");
    }

    auto process_case = [&](const Json& raw_case) {
        DecisionResult result;
        Json effective_case;
        const Json* tc_ptr = &raw_case;
        bool evaluated_contract_binding = false;
        if (use_normalized_cases) {
            counters.normalized_context_cases++;
            NormalizedCaseResult norm = normalize_case_from_envelope(*contracts, profile, raw_case);
            if (norm.route_matched) counters.normalizer_matched_cases++;
            if (norm.has_preblocked_decision) {
                counters.normalizer_preblocked_cases++;
                if (norm.preblock_category == "route") counters.normalizer_route_rejections++;
                else if (norm.preblock_category == "authorization") counters.normalizer_authorization_rejections++;
                else if (norm.preblock_category == "proof") counters.normalizer_proof_rejections++;
                else if (norm.preblock_category == "tenant_context") counters.normalizer_tenant_context_rejections++;
                result = norm.preblocked;
            } else {
                effective_case = std::move(norm.tc);
                tc_ptr = &effective_case;
                result = evaluate_case(profile, policy, contracts.get(), ledger.get(), *tc_ptr, seen_jti, policy_cache);
                evaluated_contract_binding = true;
            }
        } else {
            result = evaluate_case(profile, policy, contracts.get(), ledger->is_enabled() ? ledger.get() : nullptr, raw_case, seen_jti, policy_cache);
            evaluated_contract_binding = contracts != nullptr;
        }

        const Json& tc = *tc_ptr;
        const std::string kind = raw_case.at("kind").str();
        counters.total_cases++;
        counters.passed += result.passed ? 1 : 0;
        counters.failed += result.passed ? 0 : 1;
        if (kind == "openapi") counters.openapi_cases++; else if (kind == "asyncapi") counters.asyncapi_cases++;
        bool positive = raw_case.at("failure_injection").is_null() || raw_case.at("failure_injection").str().empty();
        if (positive) { counters.positive_cases++; counters.positive_passed += result.passed ? 1 : 0; }
        else { counters.failure_cases++; counters.failure_passed += result.passed ? 1 : 0; }
        if (evaluated_contract_binding) counters.contract_checked_cases++;
        if (result.action == "allow" || result.action == "accept") counters.allow_or_accept++;
        else counters.deny_or_quarantine++;
        copy_ledger_stats();
        if (result.durable_replay_ledger_rejection) counters.durable_replay_ledger_rejections++;
        if (result.effect_idempotency_rejection) counters.effect_idempotency_rejections++;
        if (result.event_identity_rejection) counters.event_identity_rejections++;
        if (!result.passed && failed_samples.size() < 16) {
            failed_samples.push_back(raw_case.at("case_id").str() + " expected=" + raw_case.at("expected_action").str() + " got=" + result.action + " reason=" + result.reason + " normalized_operation=" + tc.at("operation_id").str());
        }
    };

    if (use_jsonl_cases) {
        std::ifstream in(cases_jsonl_path, std::ios::binary);
        if (!in) throw std::runtime_error("could not open cases JSONL file " + cases_jsonl_path);
        std::string line;
        while (std::getline(in, line)) {
            if (line.empty()) continue;
            counters.streamed_case_lines++;
            process_case(parse_json_text(line));
        }
    } else {
        const Json& cases = use_normalized_cases ? normalized_cases : root.at("test_cases");
        if (!cases.is_array()) throw std::runtime_error("controls file missing test_cases or normalized_cases array");
        for (const auto& raw_case : cases.a) process_case(raw_case);
    }
    std::string flush_reason;
    if (!ledger->commit(flush_reason)) {
        throw std::runtime_error("replay ledger final flush failed: " + flush_reason);
    }
    if (!ledger_snapshot_path.empty()) {
        std::string snapshot_reason;
        if (!ledger->backup_snapshot(ledger_snapshot_path, snapshot_reason)) {
            throw std::runtime_error("replay ledger backup snapshot failed: " + snapshot_reason);
        }
    }
    copy_ledger_stats();
    if (contracts) counters.contract_table_rows = static_cast<long long>(contracts->rows.size());
    std::string binary_profile = "g++ C++20 + OpenSSL RS256/DSSE local evidence kernel; rev0632 length-prefixed security tuple framing for proof binding, effect idempotency, and CloudEvents identity; duplicate case-insensitive security metadata and ASCII control characters fail closed; rev0631 transition intents remain bound to a per-ledger instance id for use against different initialized ledgers, but byte-for-byte clones retain the same identity; SQLite schema v10 with atomic effect outbox, inflight worker leases, stale-lease reclaim, and exact capability v42; rev0635 relay reconciliation can recover an injected crash after downstream apply using a local downstream journal; rev0636/rev0637 relay paths bind adapter material through config/handle; rev0638 ingress reservation loads operator policy from a digest-pinned profile; rev0639-rev0643 add service binding, asymmetric sender proof, freshness, replay-cache reservation, and cache instance identity; rev0644 separates trusted transport identity from the untrusted request body, rejects body-supplied identity claims, uses SQLite NOFOLLOW/FULLMUTEX for the sender replay cache, removes the service-config replay clock override, and requires bounded integral ingress numbers; rev0645 preflights profile/contract acceptance before replay mutation; rev0646 moves service-path sender replay rows into the same SQLite/WAL transaction as prepared ledger entries and outbox reservations; rev0647 binds local downstream result digests to adapter provenance and hardens downstream SQLite opens; rev0648 preflights relay signer/trust authority before any outbox claim or downstream touch; still not a deployed HTTP service, TLS authenticator, DPoP verifier, distributed nonce authority, external delivery protocol, tamper-proof witness, or distributed exactly-once service";
    std::string controls_digest_input = controls_text;
    if (use_jsonl_cases) controls_digest_input += "\n--cases-jsonl--\n" + read_file(cases_jsonl_path);
    write_file(report_path, report_json(root, counters, failed_samples, sha256_hex(controls_digest_input), contracts_sha, contract_root, capabilities_sha, binary_profile));
    return counters.failed == 0 ? 0 : 2;
}





int run_ingress_reservation_command(const std::string& ingress_profile_path,
                                    const std::string& ingress_profile_sha256,
                                    const std::string& ingress_request_path,
                                    const std::string& ingress_report_path) {
    if (ingress_profile_path.empty() || ingress_profile_sha256.empty() || ingress_request_path.empty() || ingress_report_path.empty()) {
        std::cerr << "ingress reservation requires --ingress-profile, --ingress-profile-sha256, --ingress-request, and --ingress-report\n";
        return 64;
    }
    std::string artifact_stem;
    try {
        const std::string request_text = read_file(ingress_request_path);
        Json request = parse_json_text(request_text);
        const std::string request_sha = sha256_hex(request_text);
        const std::string handle = request.at("config_handle").str();
        artifact_stem = ingress_report_path + ".rev0648-" + request_sha.substr(0, 12) + "-" + sha256_hex(handle).substr(0, 12);
        IngressProfileAdapterExecution execution = execute_ingress_profile_adapter(ingress_profile_path,
                                                                                   ingress_profile_sha256,
                                                                                   request,
                                                                                   artifact_stem,
                                                                                   "",
                                                                                   nullptr,
                                                                                   nullptr);
        write_file(ingress_report_path,
                   ingress_reservation_report_json(execution.profile,
                                                   request_sha,
                                                   request,
                                                   execution.kernel_report,
                                                   execution.kernel_report_sha256,
                                                   execution.pending_report_sha256,
                                                   execution.reservation_fragment,
                                                   execution.kernel_exit_code,
                                                   execution.failure_reason));
        cleanup_ingress_profile_adapter_artifacts(artifact_stem);
        if (ingress_profile_adapter_accepted(execution)) {
            std::cout << "ingress reservation accepted request " << request.at("request_id").str() << " using handle " << execution.profile.handle << "\n";
            return 0;
        }
        std::cout << "ingress reservation rejected request " << request.at("request_id").str() << " using handle " << execution.profile.handle << "\n";
        return execution.kernel_exit_code == 0 ? 2 : execution.kernel_exit_code;
    } catch (const std::exception& e) {
        if (!artifact_stem.empty()) cleanup_ingress_profile_adapter_artifacts(artifact_stem);
        try {
            std::ostringstream out;
            out << "{\n"
                << "  \"format\": \"" << kIngressReservationReportFormat << "\",\n"
                << "  \"revision_id\": \"rev0638\",\n"
                << "  \"reservation\": {\n"
                << "    \"accepted\": false,\n"
                << "    \"failure_reason\": \"" << json_escape(e.what()) << "\"\n"
                << "  },\n"
                << "  \"blocked_claim\": \"rev0638 failed-closed ingress reservation error report; no asynchronous work is implied.\"\n"
                << "}\n";
            write_file(ingress_report_path, out.str());
        } catch (...) {}
        std::cerr << "ingress reservation failed: " << e.what() << "\n";
        return 1;
    }
}


int run_ingress_reservation_service_command(const std::string& ingress_service_config_path,
                                            const std::string& ingress_service_config_sha256,
                                            const std::string& ingress_transport_context_path,
                                            const std::string& ingress_request_path,
                                            const std::string& ingress_report_path) {
    if (ingress_service_config_path.empty() || ingress_service_config_sha256.empty() ||
        ingress_transport_context_path.empty() || ingress_request_path.empty() || ingress_report_path.empty()) {
        std::cerr << "ingress service reservation requires --ingress-service-config, --ingress-service-config-sha256, --ingress-transport-context, --ingress-request, and --ingress-report\n";
        return 64;
    }
    IngressReservationServiceConfig service_config;
    service_config.service_config_path = ingress_service_config_path;
    service_config.service_config_sha256 = ingress_service_config_sha256;
    try {
        service_config = load_ingress_service_config(ingress_service_config_path, ingress_service_config_sha256);
        const IngressTransportContext trusted_context = load_ingress_transport_context(ingress_transport_context_path);
        const std::string request_text = read_file_bounded(ingress_request_path, kIngressMaximumRequestBytes, "ingress service request");
        IngressReservationServiceHandle operator_service_handle;
        operator_service_handle.service_config_path = ingress_service_config_path;
        operator_service_handle.service_config_sha256 = ingress_service_config_sha256;
        IngressReservationResult result = reserve_ingress_request_json(operator_service_handle, trusted_context, request_text);
        write_file(ingress_report_path, result.report_json);
        Json report = parse_json_text(result.report_json);
        std::string request_id = report.at("request").at("legacy_request_evidence").at("request_id").str();
        if (request_id.empty()) {
            try { request_id = parse_json_text(request_text).at("request_id").str(); }
            catch (...) {}
        }
        if (result.accepted) {
            std::cout << "ingress service reservation accepted request " << request_id << " using service " << service_config.service_id << "\n";
            return 0;
        }
        std::cout << "ingress service reservation rejected request " << request_id << " using service " << service_config.service_id << "\n";
        return result.status_code == 0 ? 2 : result.status_code;
    } catch (const std::exception& e) {
        try {
            const std::string request_text = ingress_request_path.empty() ? std::string() : read_file(ingress_request_path);
            const std::string request_sha = request_text.size() <= kIngressMaximumRequestBytes ? sha256_hex(request_text) : std::string(64, '0');
            write_file(ingress_report_path, service_failure_report_json(service_config, request_sha, e.what()));
        } catch (...) {}
        std::cerr << "ingress service reservation failed: " << e.what() << "\n";
        return 1;
    }
}


}  // namespace anonsync

// rev0599 runner needle: ReplayLedger::stage ReplayLedger::commit backend interface; ledger.flush compatibility wrapper retained for older validators.

// rev0632 translation unit: capability v27 adds length-prefixed ingress security material and fail-closed metadata normalization while retaining SQLite schema v8 prepared-effect rows, ledger-instance-bound signed-intent transitions, read-only pending-effect recovery, and v15 restore downgrade defenses.

// rev0633 translation unit: capability v28 adds a SQLite schema v9 effect_outbox row atomically inserted with each prepared decision row and terminally updated only inside the signed transition transaction.

// rev0634 translation unit: capability v29 advances SQLite to schema v10 with effect_outbox inflight claim leases and stale-lease reclaim for a local worker relay boundary.

// rev0635 translation unit: capability v30 adds a local effect relay/reconciliation harness for crash-after-downstream-apply gaps.
// rev0636 translation unit: capability v31 adds a digest-pinned configured relay adapter boundary so requests cannot pick downstream path, signer, trust pin, worker id, lease, or terminal state.

// rev0638 translation unit: capability v33 adds a profile-bound ingress reservation command so requests supply authenticated context plus a handle, not paths, proof secrets, clocks, backend mode, or ledger reset controls.

// rev0639 translation unit: capability v34 adds a service-bound ingress reservation API/CLI config so per-request ingress supplies request JSON rather than profile paths, profile pins, or operator filesystem operands.
// rev0640 translation unit: capability v35 adds service-owned sender_possession HMAC verification before invoking the profile adapter or appending a durable reservation.
// rev0641 translation unit: capability v36 replaces symmetric caller secrets in the service config with a pinned RSA public JWK and request-bound sender_possession RS256 signatures.
// rev0642 translation unit: capability v37 adds nonce, issued_at_epoch freshness, and service-owned SQLite sender replay-cache reservation before profile adapter invocation or ledger append.
// rev0643 translation unit: capability v38 binds sender proofs and the SQLite replay cache to an operator-configured replay-cache instance id and rejects metadata identity drift before append.
// rev0648 translation unit: capability v42 preflights relay transition signer/trust authority before any outbox claim or downstream touch while retaining ledger-integrated sender replay and provenance-bound local downstream evidence.
