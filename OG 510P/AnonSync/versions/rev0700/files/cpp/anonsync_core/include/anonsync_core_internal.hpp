#pragma once

#include "anonsync_core.hpp"

#include <openssl/bn.h>
#include <openssl/core_names.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/param_build.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <limits>
#include <locale>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

namespace anonsync {

struct Json {
    enum class Type { Null, Bool, Number, String, Array, Object } type = Type::Null;
    bool b = false;
    double n = 0.0;
    std::string s;
    std::vector<Json> a;
    std::map<std::string, Json> o;

    bool is_null() const { return type == Type::Null; }
    bool is_bool() const { return type == Type::Bool; }
    bool is_number() const { return type == Type::Number; }
    bool is_string() const { return type == Type::String; }
    bool is_array() const { return type == Type::Array; }
    bool is_object() const { return type == Type::Object; }

    const Json& at(const std::string& key) const {
        static const Json null_json;
        if (!is_object()) return null_json;
        auto it = o.find(key);
        return it == o.end() ? null_json : it->second;
    }
    const Json& at(size_t idx) const {
        static const Json null_json;
        if (!is_array() || idx >= a.size()) return null_json;
        return a[idx];
    }
    std::string str(const std::string& fallback = "") const { return is_string() ? s : fallback; }
    bool boolean(bool fallback = false) const { return is_bool() ? b : fallback; }
    long long integer(long long fallback = 0) const {
        if (!is_number()) return fallback;
        constexpr double kMaximumExactJsonInteger = 9007199254740991.0;
        if (!std::isfinite(n) || std::trunc(n) != n || n < -kMaximumExactJsonInteger || n > kMaximumExactJsonInteger) {
            throw std::runtime_error("JSON number is not an exact interoperable signed integer");
        }
        return static_cast<long long>(n);
    }
};

struct OpenSSLDeleter {
    void operator()(EVP_PKEY* p) const;
    void operator()(EVP_MD_CTX* p) const;
};
using PKeyPtr = std::unique_ptr<EVP_PKEY, OpenSSLDeleter>;
using MdCtxPtr = std::unique_ptr<EVP_MD_CTX, OpenSSLDeleter>;

std::string read_file(const std::string& path);
void write_file(const std::string& path, const std::string& text);
Json parse_json_text(const std::string& text);
Json load_json(const std::string& path);
std::string json_escape(const std::string& value);
std::string canonical_json(const Json& value);
std::string b64url_encode(const unsigned char* data, size_t len);
std::string b64url_encode(const std::vector<unsigned char>& bytes);
std::vector<unsigned char> b64url_decode(const std::string& input);
std::string sha256_hex(const std::string& data);
std::string hmac_sha256_hex(const std::string& key, const std::string& data);
std::string length_prefixed_security_tuple(const std::string& domain, const std::vector<std::pair<std::string, std::string>>& fields);
bool contains_disallowed_security_control(const std::string& value);
std::string join_bytes(const std::vector<unsigned char>& bytes);
PKeyPtr jwk_to_pkey(const std::string& n_b64, const std::string& e_b64);
PKeyPtr pem_private_key_to_pkey(const std::string& pem_text);
std::string sign_rs256(EVP_PKEY* key, const std::string& signing_input);
bool verify_rs256(EVP_PKEY* pkey, const std::string& signing_input, const std::string& signature_b64url, std::string& reason);
std::vector<std::string> split_words(const std::string& text);
bool array_contains_string(const Json& arr, const std::string& value);
std::string strict_utc_from_epoch(long long epoch);
bool is_lowercase_sha256_hex(const std::string& value);

struct Profile {
    std::string issuer;
    std::string audience;
    std::string active_kid;
    std::string required_typ;
    long long now_epoch = 0;
    long long fresh_jwks_expires_epoch = 0;
    long long stale_jwks_expires_epoch = 0;
    PKeyPtr public_key;
    bool proof_binding_required = false;
    std::string proof_binding_active_kid;
    std::string proof_binding_material_version;
    std::string proof_binding_secret_id;
    std::string proof_binding_hmac_sha256_secret;
};

struct PolicyProfile {
    std::string payload_type;
    std::string expected_revision;
    std::string expected_bundle_version;
    long long minimum_sequence = 0;
    std::string operation_contract_root_sha256;
    std::string operation_contract_table_digest_sha256;
    std::map<std::string, Json> envelopes;
};

struct OperationContract {
    std::string kind;
    std::string file;
    std::string operation_id;
    std::string contract_digest_sha256;
    std::string required_scope;
    std::vector<std::string> required_roles;
    std::string expected_tenant_id;
    std::string method;
    std::string path_template;
    std::string channel;
    std::string action;
};

struct OperationContractTable {
    std::string revision_id;
    std::string operation_contract_root_sha256;
    std::string table_digest_sha256;
    std::map<std::string, OperationContract> rows;
};

std::string contract_key(const std::string& kind, const std::string& file, const std::string& operation_id);
std::vector<std::string> string_array(const Json& arr);
bool same_string_set(std::vector<std::string> a, std::vector<std::string> b);
OperationContractTable load_operation_contract_table(const std::string& path, const std::string& text);
bool validate_operation_contract_binding(const OperationContractTable& table, const Profile& profile, const Json& tc, const Json& claims, std::string& reason);

std::string ascii_lower(std::string value);
std::string ascii_upper(std::string value);
std::map<std::string, std::string> string_object_lower_keys(const Json& obj);
std::string map_value(const std::map<std::string, std::string>& values, const std::string& key, const std::string& fallback = "");
bool starts_with(const std::string& text, const std::string& prefix);
std::vector<std::string> split_path(const std::string& raw_path);
bool path_template_matches(const std::string& tmpl, const std::string& path);
const OperationContract* find_http_contract(const OperationContractTable& table, const std::string& method, const std::string& path, std::string& reason);
const OperationContract* find_event_contract(const OperationContractTable& table, const std::string& channel, const std::string& action, const std::string& file_hint, std::string& reason);
Json json_string_value(const std::string& value);
Json json_bool_value(bool value);
Json json_array_strings_value(const std::vector<std::string>& values);
Json json_null_value();
Json make_normalized_legacy_case(const Json& raw, const OperationContract& contract, const std::string& token, const std::string& policy_envelope_key, const std::string& ledger_mode, bool cloud_event_id_present, bool cloud_event_source_present, const std::string& cloud_event_source, const std::string& cloud_event_id);
std::string proof_binding_material_for_envelope(const std::string& kind, const OperationContract& contract, const std::string& proof_kid, const std::string& tenant, const std::string& token, const Json& request_or_event);
std::string expected_proof_binding_digest(const Profile& profile, const std::string& kind, const OperationContract& contract, const std::string& proof_kid, const std::string& tenant, const std::string& token, const Json& request_or_event);

struct DecisionResult {
    std::string action;
    bool passed = false;
    std::string reason;
    bool ledger_appended = false;
    bool durable_replay_ledger_rejection = false;
    bool event_identity_rejection = false;
    bool effect_idempotency_rejection = false;
};

struct NormalizedCaseResult {
    Json tc;
    DecisionResult preblocked;
    bool has_preblocked_decision = false;
    bool route_matched = false;
    std::string preblock_category;
};

DecisionResult make_preblocked_decision(const std::string& kind, const std::string& expected, const std::string& reason);
std::string bearer_token_from_headers(const std::map<std::string, std::string>& headers, std::string& reason);
NormalizedCaseResult normalize_case_from_envelope(const OperationContractTable& table, const Profile& profile, const Json& raw);

struct ReplayLedgerStats {
    std::string backend_name = "disabled";
    long long loaded_entries = 0;
    long long appended_entries = 0;
    long long atomic_rewrite_commits = 0;
    long long directory_fsync_attempts = 0;
    long long lock_acquire_attempts = 0;
    long long lock_contention_denials = 0;
    long long journal_records_written = 0;
    long long journal_recovered_after_commit = 0;
    long long journal_rejections = 0;
    long long batch_flush_commits = 0;
    long long batch_pending_entries_peak = 0;
    long long sqlite_transactions = 0;
    long long sqlite_wal_checkpoints = 0;
    long long sqlite_integrity_checks = 0;
    long long sqlite_profile_checks = 0;
    long long sqlite_corruption_rejections = 0;
    long long sqlite_backup_snapshots = 0;
    long long sqlite_snapshot_verifications = 0;
    long long sqlite_snapshot_restores = 0;
    long long sqlite_snapshot_manifest_verifications = 0;
    long long sqlite_restore_rollback_guard_checks = 0;
    long long durable_line_count = 0;
    std::string durable_head_hash = "GENESIS";
    long long host_capability_probe_checks = 0;
    long long backend_factory_selections = 0;
    long long backend_capability_manifest_checks = 0;
    long long backend_capability_manifest_mismatches = 0;
    long long effect_idempotency_rejections = 0;
    long long effect_terminal_transitions = 0;
    long long effect_transition_rejections = 0;
    long long effect_transition_line_count = 0;
    std::string effect_transition_head_hash = "GENESIS";
    long long effect_outbox_reserved = 0;
    long long effect_outbox_inflight = 0;
    long long effect_outbox_terminal = 0;
};

struct IReplayLedgerBackend {
    virtual ~IReplayLedgerBackend() = default;
    virtual void load(const std::string& ledger_path, bool reset, const std::string& mode = "immediate") = 0;
    virtual bool is_enabled() const = 0;
    virtual std::string backend_name() const = 0;
    virtual ReplayLedgerStats stats() const = 0;
    virtual bool contains_jti(const std::string& jti) const = 0;
    virtual bool contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const = 0;
    virtual bool contains_effect_idempotency_key(const std::string& effect_idempotency_key) const = 0;
    virtual bool stage(const Json& tc, const Json& claims, const std::string& action, std::string& reason) = 0;
    virtual bool commit(std::string& reason) = 0;
    virtual bool backup_snapshot(const std::string& snapshot_path, std::string& reason) = 0;
    virtual void recover() = 0;
    virtual void close() = 0;
};

std::unique_ptr<IReplayLedgerBackend> create_replay_ledger_backend(const std::string& backend_name);
struct SqliteSnapshotManifestVerification {
    long long line_count = 0;
    std::string head_hash;
    std::string snapshot_sha256;
    std::string signer_kid;
};
SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest(const std::string& manifest_path, const std::string& trust_profile_path, const std::string& snapshot_path);
SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest_with_trust_profile_text(const std::string& manifest_path, const std::string& trust_profile_text, const std::string& snapshot_path);
std::string read_trust_profile_with_digest_pin(const std::string& trust_profile_path, const std::string& expected_sha256);
void verify_trust_profile_digest_pin(const std::string& trust_profile_path, const std::string& expected_sha256);
void restore_sqlite_snapshot_into_ledger(const std::string& snapshot_path, const std::string& ledger_path);
void restore_sqlite_snapshot_into_ledger_verified(const std::string& snapshot_path, const std::string& ledger_path, const SqliteSnapshotManifestVerification& expected);
std::string validate_replay_backend_capability_manifest(const std::string& manifest_text, const std::string& backend_name, const std::string& commit_mode, const std::string& ledger_path);

struct ReplayLedger : public IReplayLedgerBackend {
    bool enabled = false;
    std::string path;
    long long loaded_entries = 0;
    long long appended_entries = 0;
    long long atomic_rewrite_commits = 0;
    long long directory_fsync_attempts = 0;
    long long lock_acquire_attempts = 0;
    long long lock_contention_denials = 0;
    long long journal_records_written = 0;
    long long journal_recovered_after_commit = 0;
    long long journal_rejections = 0;
    long long ledger_batch_flush_commits = 0;
    long long ledger_batch_pending_entries_peak = 0;
    std::string commit_mode = "immediate";
    bool batch_dirty = false;
    long long batch_pending_entries = 0;
    long long durable_line_count = 0;
    std::string durable_head_hash = "GENESIS";
    std::string lock_path;
    int lock_fd = -1;
    std::string head_hash = "GENESIS";
    std::unordered_set<std::string> committed_jtis;
    std::unordered_set<std::string> committed_event_identities;
    std::unordered_set<std::string> committed_effect_idempotency_keys;
    std::unordered_map<std::string, std::string> terminal_effect_states;
    long long effect_transition_line_count = 0;
    long long effect_terminal_transitions = 0;
    long long effect_transition_rejections = 0;
    std::string effect_transition_head_hash = "GENESIS";
    std::vector<std::string> canonical_lines;

    bool is_enabled() const override { return enabled; }
    std::string backend_name() const override { return "local-jsonl"; }
    ReplayLedgerStats stats() const override;
    static std::string entry_hash_material(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key = "", const std::string& effect_state = "");
    static std::string compute_entry_hash(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key = "", const std::string& effect_state = "");
    ~ReplayLedger();
    void load(const std::string& ledger_path, bool reset, const std::string& mode = "immediate") override;
    void release_lock();
    bool contains_jti(const std::string& jti) const override;
    bool contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const override;
    bool contains_effect_idempotency_key(const std::string& effect_idempotency_key) const override;
    bool append(const Json& tc, const Json& claims, const std::string& action, std::string& reason);
    bool stage(const Json& tc, const Json& claims, const std::string& action, std::string& reason) override;
    bool flush(std::string& reason);
    bool commit(std::string& reason) override;
    bool backup_snapshot(const std::string& snapshot_path, std::string& reason) override;
    void recover() override;
    void close() override;

  private:
    std::string journal_path() const;
    void acquire_lock();
    void recover_or_reject_journal();
    void maybe_inject_crash(const std::string& checkpoint);
    bool write_journal_record(const std::string& previous_head, long long previous_line_count, const std::string& next_head, long long next_line_count, const std::string& last_entry_previous_hash, const std::string& payload_sha256, std::string& reason);
    bool durable_replace_lines(const std::vector<std::string>& next_lines, std::string& reason);
};

std::pair<std::string, std::string> split_token_part(const std::string& token, size_t& p1, size_t& p2);
std::string decode_jti_untrusted(const std::string& token);
bool verify_token(const Profile& profile, const Json& tc, std::unordered_set<std::string>& seen_jti, const IReplayLedgerBackend* ledger, Json& claims, std::string& reason);
std::string pae(const std::string& payload_type, const std::string& payload_bytes);
bool verify_policy_envelope(const Profile& profile, const PolicyProfile& policy, const std::string& key, std::map<std::string, std::pair<bool, std::string>>& cache, std::string& reason);
DecisionResult evaluate_case(const Profile& profile, const PolicyProfile& policy, const OperationContractTable* contracts, IReplayLedgerBackend* ledger, const Json& tc, std::unordered_set<std::string>& seen_jti, std::map<std::string, std::pair<bool, std::string>>& policy_cache);

struct Counters {
    long long total_cases = 0;
    long long passed = 0;
    long long failed = 0;
    long long openapi_cases = 0;
    long long asyncapi_cases = 0;
    long long positive_cases = 0;
    long long positive_passed = 0;
    long long failure_cases = 0;
    long long failure_passed = 0;
    long long deny_or_quarantine = 0;
    long long allow_or_accept = 0;
    long long contract_checked_cases = 0;
    long long contract_table_rows = 0;
    long long normalized_context_cases = 0;
    long long normalizer_matched_cases = 0;
    long long normalizer_preblocked_cases = 0;
    long long normalizer_route_rejections = 0;
    long long normalizer_authorization_rejections = 0;
    long long normalizer_proof_rejections = 0;
    long long normalizer_tenant_context_rejections = 0;
    long long event_identity_rejections = 0;
    long long durable_replay_ledger_rejections = 0;
    long long effect_idempotency_rejections = 0;
    long long ledger_loaded_entries = 0;
    long long ledger_appended_entries = 0;
    long long ledger_atomic_rewrite_commits = 0;
    long long ledger_directory_fsync_attempts = 0;
    long long ledger_lock_acquire_attempts = 0;
    long long ledger_lock_contention_denials = 0;
    long long ledger_journal_records_written = 0;
    long long ledger_journal_recovered_after_commit = 0;
    long long ledger_journal_rejections = 0;
    long long ledger_batch_flush_commits = 0;
    long long ledger_batch_pending_entries_peak = 0;
    long long ledger_sqlite_transactions = 0;
    long long ledger_sqlite_wal_checkpoints = 0;
    long long ledger_sqlite_integrity_checks = 0;
    long long ledger_sqlite_profile_checks = 0;
    long long ledger_sqlite_corruption_rejections = 0;
    long long ledger_sqlite_backup_snapshots = 0;
    long long ledger_sqlite_snapshot_verifications = 0;
    long long ledger_sqlite_snapshot_restores = 0;
    long long ledger_sqlite_snapshot_manifest_verifications = 0;
    long long ledger_sqlite_trust_profile_digest_verifications = 0;
    long long ledger_sqlite_restore_rollback_guard_checks = 0;
    long long ledger_durable_line_count = 0;
    std::string ledger_durable_head_hash = "GENESIS";
    long long ledger_host_capability_probe_checks = 0;
    long long ledger_backend_factory_selections = 0;
    long long ledger_backend_capability_manifest_checks = 0;
    long long ledger_backend_capability_manifest_mismatches = 0;
    long long ledger_effect_terminal_transitions = 0;
    long long ledger_effect_transition_rejections = 0;
    long long ledger_effect_transition_line_count = 0;
    std::string ledger_effect_transition_head_hash = "GENESIS";
    long long ledger_effect_outbox_reserved = 0;
    long long ledger_effect_outbox_inflight = 0;
    long long ledger_effect_outbox_terminal = 0;
    std::string ledger_backend_name = "disabled";
    long long streamed_case_lines = 0;
};

std::string report_json(const Json& root, const Counters& c, const std::vector<std::string>& failed_samples, const std::string& controls_sha, const std::string& contracts_sha, const std::string& contract_root, const std::string& capabilities_sha, const std::string& binary_profile);

}  // namespace anonsync
