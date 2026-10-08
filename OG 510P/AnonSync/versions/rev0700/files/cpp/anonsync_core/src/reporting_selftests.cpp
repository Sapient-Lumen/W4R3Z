#include "anonsync_core_internal.hpp"
#include <ctime>
#include <cctype>
#include <cstdlib>
#include <chrono>
#include <filesystem>
#include <thread>
#include <unistd.h>
#include <sqlite3.h>
#include <openssl/rsa.h>

namespace anonsync {


namespace {
struct SelftestLedgerSummary {
    long long line_count = 0;
    std::string head = "GENESIS";
    std::string previous_head = "GENESIS";
    std::vector<std::string> heads_by_line;
};


struct SelftestPreparedEffectRef {
    long long sequence = 0;
    std::string entry_hash;
};

SelftestPreparedEffectRef selftest_prepared_effect_ref_for_key(const std::string& ledger_path, const std::string& effect_key) {
    sqlite3* db = nullptr;
    if (sqlite3_open_v2(ledger_path.c_str(), &db, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
        std::string msg = db ? sqlite3_errmsg(db) : "sqlite open failed";
        if (db) sqlite3_close(db);
        throw std::runtime_error("selftest prepared-effect reference open failed: " + msg);
    }
    sqlite3_stmt* stmt = nullptr;
    const char* sql = "SELECT sequence, entry_hash FROM ledger_entries WHERE effect_idempotency_key=?1 LIMIT 1";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string msg = sqlite3_errmsg(db);
        sqlite3_close(db);
        throw std::runtime_error("selftest prepared-effect reference prepare failed: " + msg);
    }
    sqlite3_bind_text(stmt, 1, effect_key.c_str(), -1, SQLITE_TRANSIENT);
    SelftestPreparedEffectRef out;
    int rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        out.sequence = sqlite3_column_int64(stmt, 0);
        const unsigned char* raw = sqlite3_column_text(stmt, 1);
        out.entry_hash = raw ? reinterpret_cast<const char*>(raw) : std::string();
    } else {
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        throw std::runtime_error("selftest prepared-effect reference row not found");
    }
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return out;
}

SelftestPreparedEffectRef selftest_prepared_effect_ref_from_pending_report(const std::string& report_text, const std::string& effect_key) {
    Json report = parse_json_text(report_text);
    const Json& rows = report.at("pending_effects");
    if (!rows.is_array()) throw std::runtime_error("pending report missing pending_effects array");
    for (const auto& row : rows.a) {
        if (row.at("effect_idempotency_key").str() == effect_key) {
            SelftestPreparedEffectRef out;
            out.sequence = row.at("sequence").integer(0);
            out.entry_hash = row.at("entry_hash").str();
            if (out.sequence <= 0 || out.entry_hash.size() != 64) throw std::runtime_error("pending report row missing prepared evidence binding");
            return out;
        }
    }
    throw std::runtime_error("pending report does not contain requested effect key");
}

SelftestLedgerSummary summarize_selftest_ledger_payload(const std::string& payload) {
    SelftestLedgerSummary summary;
    std::istringstream lines(payload);
    std::string line;
    while (std::getline(lines, line)) {
        if (line.empty()) continue;
        Json entry = parse_json_text(line);
        summary.previous_head = entry.at("previous_hash").str();
        summary.head = entry.at("entry_hash").str();
        summary.heads_by_line.push_back(summary.head);
        summary.line_count++;
    }
    if (summary.line_count == 0) {
        summary.head = "GENESIS";
        summary.previous_head = "GENESIS";
    }
    return summary;
}

std::string make_selftest_journal_v2(const std::string& ledger_path,
                                     const std::string& previous_head,
                                     long long previous_line_count,
                                     const std::string& next_head,
                                     long long next_line_count,
                                     const std::string& last_entry_previous_hash,
                                     const std::string& payload_sha256) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-replay-ledger-journal-v2\",\n"
        << "  \"ledger_path\": \"" << json_escape(ledger_path) << "\",\n"
        << "  \"previous_head\": \"" << json_escape(previous_head) << "\",\n"
        << "  \"previous_line_count\": " << previous_line_count << ",\n"
        << "  \"next_head\": \"" << json_escape(next_head) << "\",\n"
        << "  \"next_line_count\": " << next_line_count << ",\n"
        << "  \"last_entry_previous_hash\": \"" << json_escape(last_entry_previous_hash) << "\",\n"
        << "  \"payload_sha256\": \"" << payload_sha256 << "\",\n"
        << "  \"commit_protocol\": \"lock write-journal fsync-journal temp-write fsync rename fsync-dir unlink-journal\"\n"
        << "}\n";
    return out.str();
}


std::string bn_to_b64url_selftest(const BIGNUM* bn) {
    if (!bn) throw std::runtime_error("missing RSA BIGNUM");
    std::vector<unsigned char> buf(static_cast<size_t>(BN_num_bytes(bn)));
    BN_bn2bin(bn, buf.data());
    return b64url_encode(buf);
}

struct SelftestRestoreRoot {
    PKeyPtr key;
    std::string kid;
    std::string n;
    std::string e;
};

SelftestRestoreRoot make_selftest_restore_root(const std::string& kid) {
    EVP_PKEY_CTX* raw_ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
    if (!raw_ctx) throw std::runtime_error("selftest restore-root RSA context allocation failed");
    std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)> ctx(raw_ctx, EVP_PKEY_CTX_free);
    if (EVP_PKEY_keygen_init(ctx.get()) != 1) throw std::runtime_error("selftest restore-root keygen init failed");
    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx.get(), 2048) != 1) throw std::runtime_error("selftest restore-root RSA bit-size setup failed");
    EVP_PKEY* raw_key = nullptr;
    if (EVP_PKEY_keygen(ctx.get(), &raw_key) != 1 || raw_key == nullptr) throw std::runtime_error("selftest restore-root keygen failed");
    PKeyPtr key(raw_key);
    BIGNUM* n = nullptr;
    BIGNUM* e = nullptr;
    if (EVP_PKEY_get_bn_param(key.get(), OSSL_PKEY_PARAM_RSA_N, &n) != 1 || EVP_PKEY_get_bn_param(key.get(), OSSL_PKEY_PARAM_RSA_E, &e) != 1) {
        BN_free(n); BN_free(e);
        throw std::runtime_error("selftest restore-root public-key extraction failed");
    }
    std::string n_b64 = bn_to_b64url_selftest(n);
    std::string e_b64 = bn_to_b64url_selftest(e);
    BN_free(n);
    BN_free(e);
    SelftestRestoreRoot out;
    out.key = std::move(key);
    out.kid = kid;
    out.n = n_b64;
    out.e = e_b64;
    return out;
}

std::string sign_rs256_selftest(EVP_PKEY* key, const std::string& signing_input) {
    return sign_rs256(key, signing_input);
}

std::string private_key_pem_selftest(EVP_PKEY* key) {
    BIO* raw = BIO_new(BIO_s_mem());
    if (!raw) throw std::runtime_error("selftest private-key PEM BIO allocation failed");
    std::unique_ptr<BIO, decltype(&BIO_free)> bio(raw, BIO_free);
    if (PEM_write_bio_PrivateKey(bio.get(), key, nullptr, nullptr, 0, nullptr, nullptr) != 1) {
        throw std::runtime_error("selftest private-key PEM serialization failed");
    }
    char* data = nullptr;
    const long len = BIO_get_mem_data(bio.get(), &data);
    if (len <= 0 || data == nullptr) throw std::runtime_error("selftest private-key PEM extraction failed");
    return std::string(data, static_cast<size_t>(len));
}


std::string sqlite_snapshot_manifest_signing_input_selftest(const std::string& manifest_revision_id,
                                                            const std::string& parent_revision,
                                                            const std::string& issued_at,
                                                            const std::string& snapshot_sha,
                                                            long long line_count,
                                                            const std::string& head_hash,
                                                            const std::string& expected_revision,
                                                            const std::string& source_revision,
                                                            const std::string& subject,
                                                            const std::string& ceiling) {
    std::ostringstream in;
    in << "anonsync-sqlite-snapshot-manifest-v2\n"
       << manifest_revision_id << "\n"
       << parent_revision << "\n"
       << issued_at << "\n"
       << snapshot_sha << "\n"
       << "sqlite-wal\n"
       << "sqlite-wal\n"
       << 10 << "\n"
       << "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent\n"
       << "sha256\n"
       << "sqlite-wal-begin-immediate-full-sync\n"
       << line_count << "\n"
       << head_hash << "\n"
       << expected_revision << "\n"
       << source_revision << "\n"
       << subject << "\n"
       << ceiling << "\n";
    return in.str();
}

std::string make_sqlite_snapshot_manifest_v2_selftest(const SelftestRestoreRoot& root,
                                                      const std::string& snapshot_path,
                                                      long long line_count,
                                                      const std::string& head_hash,
                                                      const std::string& issued_at,
                                                      const std::string& expected_revision,
                                                      const std::string& source_revision,
                                                      const std::string& subject) {
    const std::string ceiling = "local selftest SQLite/WAL snapshot only; not distributed replay prevention, custody proof, delivery proof, or legal finality";
    const std::string snapshot_sha = sha256_hex(read_file(snapshot_path));
    const std::string parent_revision = "rev0620";
    const std::string signing_input = sqlite_snapshot_manifest_signing_input_selftest(expected_revision, parent_revision, issued_at, snapshot_sha, line_count, head_hash, expected_revision, source_revision, subject, ceiling);
    const std::string signature = sign_rs256_selftest(root.key.get(), signing_input);
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sqlite-snapshot-manifest-v2\",\n"
        << "  \"revision_id\": \"" << json_escape(expected_revision) << "\",\n"
        << "  \"parent_revision\": \"" << json_escape(parent_revision) << "\",\n"
        << "  \"payload\": {\n"
        << "    \"format\": \"anonsync-sqlite-snapshot-manifest-payload-v2\",\n"
        << "    \"manifest_revision_id\": \"" << json_escape(expected_revision) << "\",\n"
        << "    \"parent_revision\": \"" << json_escape(parent_revision) << "\",\n"
        << "    \"manifest_issued_at\": \"" << json_escape(issued_at) << "\",\n"
        << "    \"backend_name\": \"sqlite-wal\",\n"
        << "    \"backend_profile\": {\n"
        << "      \"backend_name\": \"sqlite-wal\",\n"
        << "      \"schema_version\": 10,\n"
        << "      \"entry_material_version\": \"anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent\",\n"
        << "      \"hash_algorithm\": \"sha256\",\n"
        << "      \"commit_protocol\": \"sqlite-wal-begin-immediate-full-sync\"\n"
        << "    },\n"
        << "    \"snapshot_sha256\": \"" << snapshot_sha << "\",\n"
        << "    \"line_count\": " << line_count << ",\n"
        << "    \"head_hash\": \"" << json_escape(head_hash) << "\",\n"
        << "    \"expected_revision\": \"" << json_escape(expected_revision) << "\",\n"
        << "    \"source_controls_revision\": \"" << json_escape(source_revision) << "\",\n"
        << "    \"manifest_subject\": \"" << json_escape(subject) << "\",\n"
        << "    \"durability_ceiling\": \"" << json_escape(ceiling) << "\"\n"
        << "  },\n"
        << "  \"payload_signing_input_sha256\": \"" << sha256_hex(signing_input) << "\",\n"
        << "  \"signature\": {\n"
        << "    \"alg\": \"RS256\",\n"
        << "    \"kid\": \"" << json_escape(root.kid) << "\",\n"
        << "    \"signature_b64url\": \"" << signature << "\"\n"
        << "  },\n"
        << "  \"blocked_claim\": \"C++ selftest manifest only.\"\n"
        << "}\n";
    return out.str();
}

std::string restore_root_signer_json_selftest(const SelftestRestoreRoot& root,
                                               const std::string& not_before,
                                               const std::string& not_after,
                                               const std::string& status) {
    std::ostringstream out;
    out << "  {\n"
        << "    \"kid\": \"" << json_escape(root.kid) << "\",\n"
        << "    \"alg\": \"RS256\",\n"
        << "    \"status\": \"" << json_escape(status) << "\",\n"
        << "    \"not_before\": \"" << json_escape(not_before) << "\",\n"
        << "    \"not_after\": \"" << json_escape(not_after) << "\",\n"
        << "    \"jwk\": {\n"
        << "      \"kty\": \"RSA\",\n"
        << "      \"kid\": \"" << json_escape(root.kid) << "\",\n"
        << "      \"use\": \"sig\",\n"
        << "      \"alg\": \"RS256\",\n"
        << "      \"n\": \"" << json_escape(root.n) << "\",\n"
        << "      \"e\": \"" << json_escape(root.e) << "\"\n"
        << "    }\n"
        << "  }";
    return out.str();
}

std::string make_sqlite_snapshot_trust_profile_v3_selftest(const SelftestRestoreRoot& root,
                                                           const std::string& required_subject,
                                                           const std::string& expected_revision,
                                                           const std::string& source_revision,
                                                           const std::string& not_before = "2026-06-13T00:00:00Z",
                                                           const std::string& not_after = "2026-06-30T00:00:00Z",
                                                           const std::string& status = "trusted",
                                                           const std::string& verification_time = "2026-06-13T03:10:00Z",
                                                           long long max_manifest_age_seconds = 3600,
                                                           const std::string& extra_signers_json = "") {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-sqlite-snapshot-trust-profile-v3\",\n"
        << "  \"revision_id\": \"" << json_escape(expected_revision) << "\",\n"
        << "  \"parent_revision\": \"rev0612\",\n"
        << "  \"verification_time\": \"" << json_escape(verification_time) << "\",\n"
        << "  \"max_manifest_age_seconds\": " << max_manifest_age_seconds << ",\n"
        << "  \"canonical_utc_times_required\": true,\n"
        << "  \"required_backend_name\": \"sqlite-wal\",\n"
        << "  \"required_manifest_subject\": \"" << json_escape(required_subject) << "\",\n"
        << "  \"allowed_expected_revisions\": [\"" << json_escape(expected_revision) << "\"],\n"
        << "  \"allowed_source_controls_revisions\": [\"" << json_escape(source_revision) << "\"],\n"
        << "  \"allowed_manifest_revisions\": [\"" << json_escape(expected_revision) << "\"],\n"
        << "  \"trusted_signers\": [\n"
        << restore_root_signer_json_selftest(root, not_before, not_after, status);
    if (!extra_signers_json.empty()) out << ",\n" << extra_signers_json;
    out << "\n  ],\n"
        << "  \"blocked_claim\": \"C++ selftest restore-root trust profile only; not production PKI, HSM custody, or legal finality.\"\n"
        << "}\n";
    return out.str();
}

std::string effect_transition_intent_signing_input_selftest(const std::string& intent_id,
                                                               const std::string& issued_at,
                                                               const std::string& ledger_instance_id,
                                                               const std::string& prepared_ledger_head_hash,
                                                               const std::string& effect_transition_previous_hash,
                                                               const std::string& effect_idempotency_key,
                                                               long long prepared_sequence,
                                                               const std::string& prepared_entry_hash,
                                                               const std::string& terminal_state,
                                                               const std::string& result_digest_sha256,
                                                               const std::string& transition_reason) {
    std::ostringstream in;
    in << "anonsync-effect-transition-intent-v2-ledger-instance\n"
       << intent_id << "\n"
       << "sqlite-wal-effect-terminal-transition\n"
       << issued_at << "\n"
       << "sqlite-wal\n"
       << ledger_instance_id << "\n"
       << prepared_ledger_head_hash << "\n"
       << effect_transition_previous_hash << "\n"
       << effect_idempotency_key << "\n"
       << prepared_sequence << "\n"
       << prepared_entry_hash << "\n"
       << terminal_state << "\n"
       << result_digest_sha256 << "\n"
       << transition_reason << "\n";
    return in.str();
}

std::string make_effect_transition_intent_v1_selftest(const SelftestRestoreRoot& root,
                                                      const std::string& intent_id,
                                                      const std::string& issued_at,
                                                      const std::string& ledger_instance_id,
                                                      const std::string& prepared_ledger_head_hash,
                                                      const std::string& effect_transition_previous_hash,
                                                      const std::string& effect_idempotency_key,
                                                      long long prepared_sequence,
                                                      const std::string& prepared_entry_hash,
                                                      const std::string& terminal_state,
                                                      const std::string& result_digest_sha256,
                                                      const std::string& transition_reason) {
    const std::string signing_input = effect_transition_intent_signing_input_selftest(intent_id, issued_at, ledger_instance_id, prepared_ledger_head_hash, effect_transition_previous_hash, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason);
    const std::string signature = sign_rs256_selftest(root.key.get(), signing_input);
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-effect-transition-intent-v2-ledger-instance\",\n"
        << "  \"payload\": {\n"
        << "    \"format\": \"anonsync-effect-transition-intent-payload-v2-ledger-instance\",\n"
        << "    \"intent_id\": \"" << json_escape(intent_id) << "\",\n"
        << "    \"intent_subject\": \"sqlite-wal-effect-terminal-transition\",\n"
        << "    \"issued_at\": \"" << json_escape(issued_at) << "\",\n"
        << "    \"ledger_backend\": \"sqlite-wal\",\n"
        << "    \"ledger_instance_id\": \"" << json_escape(ledger_instance_id) << "\",\n"
        << "    \"prepared_ledger_head_hash\": \"" << json_escape(prepared_ledger_head_hash) << "\",\n"
        << "    \"effect_transition_previous_hash\": \"" << json_escape(effect_transition_previous_hash) << "\",\n"
        << "    \"effect_idempotency_key\": \"" << json_escape(effect_idempotency_key) << "\",\n"
        << "    \"prepared_sequence\": " << prepared_sequence << ",\n"
        << "    \"prepared_entry_hash\": \"" << json_escape(prepared_entry_hash) << "\",\n"
        << "    \"terminal_state\": \"" << json_escape(terminal_state) << "\",\n"
        << "    \"result_digest_sha256\": \"" << json_escape(result_digest_sha256) << "\",\n"
        << "    \"transition_reason\": \"" << json_escape(transition_reason) << "\"\n"
        << "  },\n"
        << "  \"payload_signing_input_sha256\": \"" << sha256_hex(signing_input) << "\",\n"
        << "  \"signature\": {\n"
        << "    \"alg\": \"RS256\",\n"
        << "    \"kid\": \"" << json_escape(root.kid) << "\",\n"
        << "    \"signature_b64url\": \"" << signature << "\"\n"
        << "  },\n"
        << "  \"blocked_claim\": \"C++ selftest transition intent only; not HSM custody or downstream delivery proof.\"\n"
        << "}\n";
    return out.str();
}

std::string make_effect_transition_trust_profile_v1_selftest(const SelftestRestoreRoot& root,
                                                             const std::string& verification_time = "2026-06-18T02:45:00Z",
                                                             long long max_intent_age_seconds = 3600,
                                                             const std::string& status = "trusted") {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-effect-transition-trust-profile-v2\",\n"
        << "  \"revision_id\": \"rev0631\",\n"
        << "  \"verification_time\": \"" << json_escape(verification_time) << "\",\n"
        << "  \"max_intent_age_seconds\": " << max_intent_age_seconds << ",\n"
        << "  \"required_intent_subject\": \"sqlite-wal-effect-terminal-transition\",\n"
        << "  \"allowed_terminal_states\": [\"applied\", \"failed\", \"compensated\"],\n"
        << "  \"trusted_signers\": [\n"
        << restore_root_signer_json_selftest(root, "2026-06-18T00:00:00Z", "2026-06-19T00:00:00Z", status)
        << "\n  ],\n"
        << "  \"blocked_claim\": \"Selftest transition trust profile only; not production PKI or HSM custody.\"\n"
        << "}\n";
    return out.str();
}

std::string host_capability_report_json() {
    int compile_option_count = 0;
    while (sqlite3_compileoption_get(compile_option_count) != nullptr) compile_option_count++;
    bool wal_ok = false;
    bool begin_immediate_ok = false;
    bool integrity_ok = false;
    bool backup_api_ok = false;
    const std::string stem = "anonsync_core_rev0605_host_report_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string copy = "/tmp/" + stem + "_copy.sqlite";
    sqlite3* db = nullptr;
    if (sqlite3_open_v2(base.c_str(), &db, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr) == SQLITE_OK) {
        char* err = nullptr;
        wal_ok = sqlite3_exec(db, "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; CREATE TABLE t(id INTEGER PRIMARY KEY, value TEXT); INSERT INTO t(value) VALUES('ok');", nullptr, nullptr, &err) == SQLITE_OK;
        if (err) sqlite3_free(err);
        sqlite3_stmt* stmt = nullptr;
        if (sqlite3_prepare_v2(db, "PRAGMA integrity_check;", -1, &stmt, nullptr) == SQLITE_OK && sqlite3_step(stmt) == SQLITE_ROW) {
            integrity_ok = std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0))) == "ok";
        }
        if (stmt) sqlite3_finalize(stmt);
        err = nullptr;
        begin_immediate_ok = sqlite3_exec(db, "BEGIN IMMEDIATE; ROLLBACK;", nullptr, nullptr, &err) == SQLITE_OK;
        if (err) sqlite3_free(err);
        sqlite3* dst = nullptr;
        if (sqlite3_open_v2(copy.c_str(), &dst, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr) == SQLITE_OK) {
            sqlite3_backup* backup = sqlite3_backup_init(dst, "main", db, "main");
            int rc = backup ? sqlite3_backup_step(backup, -1) : SQLITE_ERROR;
            int frc = backup ? sqlite3_backup_finish(backup) : SQLITE_ERROR;
            backup_api_ok = backup && frc == SQLITE_OK && (rc == SQLITE_DONE || rc == SQLITE_OK);
            sqlite3_close(dst);
        }
        sqlite3_close(db);
    }
    std::remove(base.c_str()); std::remove((base + "-wal").c_str()); std::remove((base + "-shm").c_str());
    std::remove(copy.c_str()); std::remove((copy + "-wal").c_str()); std::remove((copy + "-shm").c_str());
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"anonsync-cpp-host-capability-report-v1\",\n"
        << "  \"revision_id\": \"rev0623\",\n"
        << "  \"sqlite_version\": \"" << json_escape(sqlite3_libversion()) << "\",\n"
        << "  \"sqlite_version_number\": " << sqlite3_libversion_number() << ",\n"
        << "  \"sqlite_threadsafe\": " << sqlite3_threadsafe() << ",\n"
        << "  \"sqlite_compile_option_count\": " << compile_option_count << ",\n"
#ifdef SQLITE_OPEN_NOFOLLOW
        << "  \"sqlite_open_nofollow_compiled\": true,\n"
#else
        << "  \"sqlite_open_nofollow_compiled\": false,\n"
#endif
        << "  \"wal_full_profile_probe_ok\": " << (wal_ok ? "true" : "false") << ",\n"
        << "  \"integrity_check_probe_ok\": " << (integrity_ok ? "true" : "false") << ",\n"
        << "  \"begin_immediate_probe_ok\": " << (begin_immediate_ok ? "true" : "false") << ",\n"
        << "  \"sqlite_backup_api_probe_ok\": " << (backup_api_ok ? "true" : "false") << ",\n"
        << "  \"blocked_claim\": \"Host capability probe is local cloudtainer evidence, not production filesystem, power-loss, distributed-storage, or custody proof.\"\n"
        << "}\n";
    return out.str();
}

}  // namespace

// rev0606 translation unit: report rendering plus compiled SQLite snapshot restore corpus selftests
// rev0605 translation unit: report rendering plus hostile snapshot corpus and host capability report emission selftests
// rev0603 translation unit: report rendering plus backend-capability and SQLite crash-corpus selftests
// rev0601 translation unit: report rendering and parser/fuzz/ledger-backend/crash-injection/batch-transaction/journal-hardening/backend-interface/sqlite-wal selftests
// rev0600 translation unit: report rendering and parser/fuzz/ledger-backend/crash-injection/batch-transaction/journal-hardening/backend-interface selftests
// rev0599 compatibility needle: report rendering and parser/fuzz/ledger-backend/crash-injection/batch-transaction/journal-hardening selftests
// rev0598 compatibility needle: report rendering and parser/fuzz/ledger-backend/crash-injection/batch-transaction selftests
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

int run_parser_boundary_selftest() {
    int passed = 0;
    int failed = 0;
    auto expect_ok = [&](const std::string& label, const std::string& json_text) {
        try { (void)parse_json_text(json_text); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "parser selftest unexpected failure " << label << ": " << e.what() << "\n"; }
    };
    auto expect_throw_json = [&](const std::string& label, const std::string& json_text) {
        try { (void)parse_json_text(json_text); failed++; std::cerr << "parser selftest expected JSON rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    auto expect_throw_codec = [&](const std::string& label, const std::string& codec_text) {
        try { (void)b64url_decode(codec_text); failed++; std::cerr << "parser selftest expected base64url rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    auto expect_integer = [&](const std::string& label, const std::string& json_text, long long expected) {
        try {
            const long long actual = parse_json_text(json_text).at("n").integer();
            if (actual == expected) passed++;
            else { failed++; std::cerr << "parser selftest integer mismatch " << label << " expected=" << expected << " actual=" << actual << "\n"; }
        } catch (const std::exception& e) {
            failed++;
            std::cerr << "parser selftest unexpected integer failure " << label << ": " << e.what() << "\n";
        }
    };
    auto expect_throw_integer = [&](const std::string& label, const std::string& json_text) {
        try { (void)parse_json_text(json_text).at("n").integer(); failed++; std::cerr << "parser selftest expected exact-integer rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    expect_ok("surrogate_pair", "{\"emoji\":\"\\uD83D\\uDE00\"}");
    std::string raw_control = "{\"bad\":\"";
    raw_control.push_back(static_cast<char>(0x01));
    raw_control += "\"}";
    expect_throw_json("raw_control_character", raw_control);
    expect_throw_json("non_json_vertical_tab_whitespace", std::string("{\"n\":") + static_cast<char>(0x0b) + "1}");
    expect_throw_json("non_json_form_feed_whitespace", std::string("{\"n\":") + static_cast<char>(0x0c) + "1}");
    std::string malformed_utf8 = "{\"bad\":\"";
    malformed_utf8.push_back(static_cast<char>(0xC0));
    malformed_utf8.push_back(static_cast<char>(0xAF));
    malformed_utf8 += "\"}";
    expect_throw_json("overlong_raw_utf8", malformed_utf8);
    expect_ok("valid_raw_utf8", "{\"text\":\"café 😀\"}");
    expect_throw_json("unpaired_high_surrogate", "{\"bad\":\"\\uD800\"}");
    expect_throw_json("low_surrogate_without_high", "{\"bad\":\"\\uDC00\"}");
    expect_throw_codec("base64url_plus", "YWJj+");
    expect_throw_codec("base64url_slash", "YWJj/");
    expect_throw_codec("base64url_padding", "YWJj=");
    try {
        const std::string long_input(4096, 'A');
        const auto decoded = b64url_decode(long_input);
        if (decoded.size() == 3072) passed++;
        else { failed++; std::cerr << "parser selftest long base64url decode length mismatch\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "parser selftest long base64url decode failed: " << e.what() << "\n";
    }
    expect_integer("maximum_interoperable_integer", "{\"n\":9007199254740991}", 9007199254740991LL);
    expect_throw_integer("fractional_integer_accessor", "{\"n\":1.5}");
    expect_throw_integer("non_interoperable_integer_accessor", "{\"n\":9007199254740992}");
    std::cout << "anonsync_core parser/codec boundary selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_boundary_fuzz_selftest() {
    int passed = 0;
    int failed = 0;
    auto expect_ok = [&](const std::string& label, const std::string& json_text) {
        try { (void)parse_json_text(json_text); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "boundary fuzz unexpected JSON failure " << label << ": " << e.what() << "\n"; }
    };
    auto expect_json_throw = [&](const std::string& label, const std::string& json_text) {
        try { (void)parse_json_text(json_text); failed++; std::cerr << "boundary fuzz expected JSON rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    auto expect_b64_throw = [&](const std::string& label, const std::string& text) {
        try { (void)b64url_decode(text); failed++; std::cerr << "boundary fuzz expected base64url rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    auto expect_path = [&](const std::string& label, const std::string& tmpl, const std::string& path, bool expected) {
        bool got = path_template_matches(tmpl, path);
        if (got == expected) passed++;
        else { failed++; std::cerr << "boundary fuzz path mismatch " << label << " expected=" << expected << " got=" << got << "\n"; }
    };
    auto expect_ledger_throw = [&](const std::string& label, const std::string& line) {
        const std::string path = "/tmp/anonsync_core_rev0593_ledger_selftest.jsonl";
        { std::ofstream out(path, std::ios::binary | std::ios::trunc); out << line << "\n"; }
        try { ReplayLedger ledger; ledger.load(path, false); failed++; std::cerr << "boundary fuzz expected ledger rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
        std::remove(path.c_str());
    };

    expect_ok("strict_number_valid", "{\"n\":-12.25e+2}");
    expect_json_throw("duplicate_key_smuggling", "{\"tenant\":\"alpha\",\"tenant\":\"beta\"}");
    expect_json_throw("leading_zero_number", "{\"n\":01}");
    expect_json_throw("missing_fractional_digit", "{\"n\":1.}");
    expect_json_throw("missing_exponent_digit", "{\"n\":1e+}");
    expect_json_throw("missing_integer_digit", "{\"n\":-}");
    std::string deep = "[";
    for (int i = 0; i < 270; ++i) deep += "[";
    deep += "0";
    for (int i = 0; i < 271; ++i) deep += "]";
    expect_json_throw("nesting_depth_limit", deep);
    expect_b64_throw("base64url_space", "YW Jj");
    expect_b64_throw("base64url_percent", "YW%2F");
    expect_path("normal_templated_route", "/objects/{object_id}/receipts", "/objects/abc-123/receipts", true);
    expect_path("reject_encoded_slash_upper", "/objects/{object_id}/receipts", "/objects/a%2Fb/receipts", false);
    expect_path("reject_encoded_slash_lower", "/objects/{object_id}/receipts", "/objects/a%2fb/receipts", false);
    expect_path("reject_dot_segment", "/objects/{object_id}/receipts", "/objects/../receipts", false);
    expect_path("reject_double_slash", "/objects/{object_id}/receipts", "/objects//receipts", false);
    expect_ledger_throw("bad_hash", "{\"sequence\":1,\"previous_hash\":\"GENESIS\",\"entry_hash\":\"bad\",\"case_id\":\"c\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"d\",\"jti\":\"j\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}");
    expect_ledger_throw("missing_jti", "{\"sequence\":1,\"previous_hash\":\"GENESIS\",\"entry_hash\":\"" + ReplayLedger::compute_entry_hash(1, "GENESIS", "c", "openapi", "op", "d", "", "allow", "", "") + "\",\"case_id\":\"c\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"d\",\"jti\":\"\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}");

    std::cout << "anonsync_core boundary fuzz selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}
int run_json_codec_fuzz_selftest() {
    int passed = 0;
    int failed = 0;
    auto expect_ok = [&](const std::string& label, const std::string& text) {
        try { (void)parse_json_text(text); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "json codec fuzz expected accept but rejected " << label << ": " << e.what() << "\n"; }
    };
    auto expect_throw = [&](const std::string& label, const std::string& text) {
        try { (void)parse_json_text(text); failed++; std::cerr << "json codec fuzz expected rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    expect_ok("empty_object", "{}");
    expect_ok("nested_valid", R"({"a":[true,false,null,-12.5e+2,"\uD834\uDD1E"]})");
    expect_ok("valid_zero", R"({"n":0})");
    expect_throw("duplicate_smuggling", R"({"role":"reader","role":"admin"})");
    expect_throw("leading_zero", R"({"n":00})");
    expect_throw("missing_fractional_digit", R"({"n":1.})");
    expect_throw("missing_exponent_digit", R"({"n":1e})");
    expect_throw("lone_high_surrogate", R"({"s":"\uD800"})");
    expect_throw("lone_low_surrogate", R"({"s":"\uDC00"})");
    expect_throw("trailing_comma_array", R"([1,])");
    expect_throw("trailing_content", "{}[] ");
    std::cout << "anonsync_core json codec fuzz selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_jwt_codec_fuzz_selftest() {
    int passed = 0;
    int failed = 0;
    auto expect_split_ok = [&](const std::string& label, const std::string& token) {
        try { size_t p1 = 0, p2 = 0; (void)split_token_part(token, p1, p2); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "jwt codec fuzz expected compact accept but rejected " << label << ": " << e.what() << "\n"; }
    };
    auto expect_split_throw = [&](const std::string& label, const std::string& token) {
        try { size_t p1 = 0, p2 = 0; (void)split_token_part(token, p1, p2); failed++; std::cerr << "jwt codec fuzz expected compact rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    auto expect_decode_jti = [&](const std::string& label, const std::string& token, const std::string& expected) {
        std::string got = decode_jti_untrusted(token);
        if (got == expected) passed++; else { failed++; std::cerr << "jwt codec fuzz jti mismatch " << label << " expected=" << expected << " got=" << got << "\n"; }
    };
    auto expect_b64_throw = [&](const std::string& label, const std::string& text) {
        try { (void)b64url_decode(text); failed++; std::cerr << "jwt codec fuzz expected base64url rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
    };
    expect_split_ok("three_parts", "a.b.c");
    expect_split_throw("one_part", "abc");
    expect_split_throw("two_parts", "a.b");
    expect_split_throw("four_parts", "a.b.c.d");
    expect_decode_jti("valid_untrusted_jti", "eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJhYmMifQ.AA", "abc");
    expect_decode_jti("malformed_payload", "eyJhbGciOiJSUzI1NiJ9.A.AA", "");
    expect_b64_throw("length_mod_one", "A");
    expect_b64_throw("nonzero_residual_len_two", "YR");
    expect_b64_throw("nonzero_residual_len_three", "YWF");
    try {
        std::string decoded = join_bytes(b64url_decode("YQ"));
        if (decoded == "a") passed++; else { failed++; std::cerr << "jwt codec fuzz canonical YQ decoded unexpected bytes\n"; }
    } catch (const std::exception& e) { failed++; std::cerr << "jwt codec fuzz canonical YQ rejected: " << e.what() << "\n"; }
    std::cout << "anonsync_core jwt codec fuzz selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_route_event_ledger_fuzz_selftest() {
    int passed = 0;
    int failed = 0;
    auto expect_path = [&](const std::string& label, const std::string& tmpl, const std::string& path, bool expected) {
        bool got = path_template_matches(tmpl, path);
        if (got == expected) passed++; else { failed++; std::cerr << "route/event/ledger fuzz path mismatch " << label << " expected=" << expected << " got=" << got << "\n"; }
    };
    auto expect_event_lookup = [&](const std::string& label, const OperationContractTable& table, const std::string& channel, const std::string& action, const std::string& hint, bool expected) {
        std::string reason;
        const OperationContract* c = find_event_contract(table, channel, action, hint, reason);
        bool got = c != nullptr;
        if (got == expected) passed++; else { failed++; std::cerr << "route/event/ledger fuzz event lookup mismatch " << label << " reason=" << reason << "\n"; }
    };
    auto expect_ledger_throw = [&](const std::string& label, const std::string& body) {
        const std::string path = "/tmp/anonsync_core_rev0594_route_ledger_fuzz.jsonl";
        { std::ofstream out(path, std::ios::binary | std::ios::trunc); out << body << "\n"; }
        try { ReplayLedger ledger; ledger.load(path, false); failed++; std::cerr << "route/event/ledger fuzz expected ledger rejection but accepted " << label << "\n"; }
        catch (...) { passed++; }
        std::remove(path.c_str());
    };
    expect_path("templated_ok", "/objects/{object_id}/receipts", "/objects/abc/receipts", true);
    expect_path("encoded_dot_segment", "/objects/{object_id}/receipts", "/objects/%2e%2e/receipts", false);
    expect_path("encoded_dot_mixed_case", "/objects/{object_id}/receipts", "/objects/%2E/receipts", false);
    expect_path("encoded_backslash", "/objects/{object_id}/receipts", "/objects/a%5Cb/receipts", false);
    expect_path("raw_backslash", "/objects/{object_id}/receipts", "/objects/a\\b/receipts", false);
    OperationContractTable table;
    OperationContract a; a.kind = "asyncapi"; a.file = "a.asyncapi.json"; a.operation_id = "opA"; a.contract_digest_sha256 = "dA"; a.channel = "events.shared"; a.action = "receive"; a.expected_tenant_id = "tenant-alpha";
    OperationContract b = a; b.file = "b.asyncapi.json"; b.operation_id = "opB"; b.contract_digest_sha256 = "dB";
    table.rows.emplace(contract_key(a.kind, a.file, a.operation_id), a);
    table.rows.emplace(contract_key(b.kind, b.file, b.operation_id), b);
    expect_event_lookup("ambiguous_without_file_hint", table, "events.shared", "receive", "", false);
    expect_event_lookup("namespaced_file_hint", table, "events.shared", "receive", "a.asyncapi.json", true);

    // rev0632 regression: newline-delimited labeled proof/effect fields allowed cross-field
    // substitution. Length framing must distinguish the exact reproduced pair.
    const std::string tuple_a = length_prefixed_security_tuple("anonsync-cloud-event-identity-v2", {
        {"source", "A\ncloud_event_id=B"}, {"id", "C"}});
    const std::string tuple_b = length_prefixed_security_tuple("anonsync-cloud-event-identity-v2", {
        {"source", "A"}, {"id", "B\ncloud_event_id=C"}});
    if (tuple_a != tuple_b && sha256_hex(tuple_a) != sha256_hex(tuple_b)) passed++;
    else { failed++; std::cerr << "route/event/ledger fuzz length-prefixed event identity collision\n"; }

    Json duplicate_headers; duplicate_headers.type = Json::Type::Object;
    duplicate_headers.o["Authorization"] = json_string_value("Bearer first");
    duplicate_headers.o["authorization"] = json_string_value("Bearer second");
    try {
        (void)string_object_lower_keys(duplicate_headers);
        failed++; std::cerr << "route/event/ledger fuzz accepted duplicate case-insensitive authorization headers\n";
    } catch (...) { passed++; }
    if (contains_disallowed_security_control("source\nid")) passed++;
    else { failed++; std::cerr << "route/event/ledger fuzz did not detect control character\n"; }

    const std::string collision_ledger = "/tmp/anonsync_core_rev0632_event_tuple_collision.jsonl";
    std::remove(collision_ledger.c_str());
    std::remove((collision_ledger + ".lock").c_str());
    std::remove((collision_ledger + ".journal").c_str());
    try {
        ReplayLedger ledger;
        ledger.load(collision_ledger, true);
        auto make_event_tc = [](const std::string& case_id, const std::string& source, const std::string& id) {
            Json tc; tc.type = Json::Type::Object;
            tc.o["case_id"] = json_string_value(case_id);
            tc.o["kind"] = json_string_value("asyncapi");
            tc.o["cloud_event_source"] = json_string_value(source);
            tc.o["cloud_event_id"] = json_string_value(id);
            return tc;
        };
        auto make_event_claims = [](const std::string& jti) {
            Json claims; claims.type = Json::Type::Object;
            claims.o["operation_id"] = json_string_value("op");
            claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("contract"));
            claims.o["jti"] = json_string_value(jti);
            return claims;
        };
        std::string r1, r2;
        // The legacy event identity key source + "\n" + id collapsed these distinct pairs.
        const bool ok1 = ledger.append(make_event_tc("collision-a", "A\nB", "C"), make_event_claims("jti-a"), "accept", r1);
        const bool ok2 = ledger.append(make_event_tc("collision-b", "A", "B\nC"), make_event_claims("jti-b"), "accept", r2);
        if (ok1 && ok2) passed++;
        else { failed++; std::cerr << "route/event/ledger fuzz length-framed ledger identity rejected distinct pairs: " << r1 << " / " << r2 << "\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "route/event/ledger fuzz collision ledger exception: " << e.what() << "\n";
    }
    std::remove(collision_ledger.c_str());
    std::remove((collision_ledger + ".lock").c_str());
    std::remove((collision_ledger + ".journal").c_str());
    const std::string h1 = ReplayLedger::compute_entry_hash(1, "GENESIS", "c1", "openapi", "op", "d", "j", "allow", "", "");
    const std::string line1 = "{\"sequence\":1,\"previous_hash\":\"GENESIS\",\"entry_hash\":\"" + h1 + "\",\"case_id\":\"c1\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"d\",\"jti\":\"j\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}";
    const std::string h2dup = ReplayLedger::compute_entry_hash(2, h1, "c2", "openapi", "op", "d", "j", "allow", "", "");
    const std::string line2dup = "{\"sequence\":2,\"previous_hash\":\"" + h1 + "\",\"entry_hash\":\"" + h2dup + "\",\"case_id\":\"c2\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"d\",\"jti\":\"j\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}";
    expect_ledger_throw("duplicate_jti", line1 + "\n" + line2dup);
    const std::string h2gap = ReplayLedger::compute_entry_hash(3, h1, "c3", "openapi", "op", "d", "j3", "allow", "", "");
    const std::string line2gap = "{\"sequence\":3,\"previous_hash\":\"" + h1 + "\",\"entry_hash\":\"" + h2gap + "\",\"case_id\":\"c3\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"d\",\"jti\":\"j3\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}";
    expect_ledger_throw("sequence_gap", line1 + "\n" + line2gap);
    std::cout << "anonsync_core route/event/ledger fuzz selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}



int run_ledger_durable_io_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string base = "/tmp/anonsync_core_rev0595_durable_ledger_" + std::to_string(static_cast<long long>(std::time(nullptr))) + ".jsonl";
    auto make_tc = [](const std::string& case_id, const std::string& kind, const std::string& source, const std::string& id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value(kind);
        tc.o["cloud_event_source"] = json_string_value(source);
        tc.o["cloud_event_id"] = json_string_value(id);
        return tc;
    };
    auto make_claims = [](const std::string& op, const std::string& digest, const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(digest);
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    try {
        long long rewrites = 0;
        long long dirsyncs = 0;
        {
            ReplayLedger ledger;
            ledger.load(base, true);
            std::string reason;
            if (ledger.append(make_tc("case-1", "openapi", "", ""), make_claims("op", "digest", "jti-1"), "allow", reason)) passed++; else { failed++; std::cerr << "durable ledger append rejected: " << reason << "\n"; }
            rewrites = ledger.atomic_rewrite_commits;
            dirsyncs = ledger.directory_fsync_attempts;
        }
        if (rewrites == 2 && dirsyncs == 2) passed++; else { failed++; std::cerr << "durable ledger expected reset+append atomic rewrite/fsync counts, got rewrites=" << rewrites << " dirsync=" << dirsyncs << "\n"; }
        { std::ofstream stale(base + ".tmp.stale", std::ios::binary | std::ios::trunc); stale << "partial"; }
        {
            ReplayLedger reload;
            reload.load(base, false);
            if (reload.loaded_entries == 1 && reload.contains_jti("jti-1")) passed++; else { failed++; std::cerr << "durable ledger reload did not preserve committed jti\n"; }
            const std::string corrupt = base + ".corrupt";
            { std::ofstream out(corrupt, std::ios::binary | std::ios::trunc); out << reload.canonical_lines.front() << "\n" << "{\"sequence\":2,\"previous_hash\":\"bad\",\"entry_hash\":\"bad\",\"case_id\":\"c\",\"kind\":\"openapi\",\"operation_id\":\"op\",\"contract_digest_sha256\":\"digest\",\"jti\":\"jti-2\",\"action\":\"allow\",\"cloud_event_source\":\"\",\"cloud_event_id\":\"\"}\n"; }
            try { ReplayLedger bad; bad.load(corrupt, false); failed++; std::cerr << "durable ledger accepted corrupt hash chain\n"; }
            catch (...) { passed++; }
            std::remove(corrupt.c_str());
        }
        std::remove(base.c_str());
        std::remove((base + ".tmp.stale").c_str());
        std::remove((base + ".lock").c_str());
        std::remove((base + ".journal").c_str());
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "durable ledger selftest exception: " << e.what() << "\n";
    }
    std::cout << "anonsync_core durable ledger io selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_backend_adapter_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string base = "/tmp/anonsync_core_rev0596_backend_adapter_" + std::to_string(static_cast<long long>(std::time(nullptr))) + ".jsonl";
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto write_recoverable_journal = [&](const std::string& ledger_path) {
        std::string payload = read_file(ledger_path);
        SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
        write_file(ledger_path + ".journal", make_selftest_journal_v2(
            ledger_path,
            "GENESIS",
            0,
            summary.head,
            summary.line_count,
            summary.previous_head,
            sha256_hex(payload)));
    };
    try {
        long long journal_records = 0;
        {
            ReplayLedger ledger;
            ledger.load(base, true);
            std::string reason;
            if (!ledger.append(make_tc("case-1"), make_claims("jti-lock-1"), "allow", reason)) {
                failed++; std::cerr << "backend adapter append rejected: " << reason << "\n";
            }
            journal_records = ledger.journal_records_written;
        }
        if (journal_records == 2) passed++; else { failed++; std::cerr << "backend adapter expected reset+append journal records=2 got=" << journal_records << "\n"; }
        {
            ReplayLedger locker;
            locker.load(base, false);
            try { ReplayLedger contender; contender.load(base, false); failed++; std::cerr << "backend adapter accepted concurrent second ledger owner\n"; }
            catch (...) { passed++; }
        }
        write_recoverable_journal(base);
        {
            ReplayLedger recover;
            recover.load(base, false);
            if (recover.journal_recovered_after_commit == 1 && !std::filesystem::exists(base + ".journal")) passed++; else { failed++; std::cerr << "backend adapter did not recover completed stale journal\n"; }
        }
        write_file(base + ".journal", make_selftest_journal_v2(base, "GENESIS", 0, "bad", 99, "GENESIS", "not-the-ledger"));
        try { ReplayLedger dirty; dirty.load(base, false); failed++; std::cerr << "backend adapter accepted dirty journal mismatch\n"; }
        catch (...) { passed++; }
        std::remove((base + ".journal").c_str());
        {
            ReplayLedger reload;
            reload.load(base, false);
            if (reload.loaded_entries == 1 && reload.contains_jti("jti-lock-1")) passed++; else { failed++; std::cerr << "backend adapter final reload lost committed jti\n"; }
        }
        std::remove(base.c_str());
        std::remove((base + ".lock").c_str());
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "backend adapter selftest exception: " << e.what() << "\n";
    }
    std::cout << "anonsync_core ledger backend adapter selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_crash_injection_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0597_crash_injection_" + std::to_string(static_cast<long long>(std::time(nullptr)));
    const std::string dir = "/tmp";
    auto base_path = [&](const std::string& suffix) { return dir + "/" + stem + "_" + suffix + ".jsonl"; };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto cleanup = [&](const std::string& base) {
        std::filesystem::path p(base);
        std::filesystem::path parent = p.parent_path().empty() ? std::filesystem::path(".") : p.parent_path();
        std::string prefix = p.filename().string();
        std::error_code ec;
        for (const auto& entry : std::filesystem::directory_iterator(parent, ec)) {
            if (ec) break;
            const std::string name = entry.path().filename().string();
            if (name == prefix || starts_with(name, prefix + ".")) {
                std::filesystem::remove(entry.path(), ec);
            }
        }
    };
    auto seed = [&](const std::string& base, const std::string& jti) -> bool {
        cleanup(base);
        try {
            ReplayLedger ledger;
            ledger.load(base, true);
            std::string reason;
            if (!ledger.append(make_tc("seed-" + jti), make_claims(jti), "allow", reason)) {
                std::cerr << "crash injection seed append rejected: " << reason << "\n";
                return false;
            }
            return true;
        } catch (const std::exception& e) {
            std::cerr << "crash injection seed failed: " << e.what() << "\n";
            return false;
        }
    };
    auto attempt_faulted_append = [&](const std::string& base, const std::string& checkpoint, const std::string& jti) -> bool {
        ::setenv("ANONSYNC_LEDGER_FAULT_AT", checkpoint.c_str(), 1);
        try {
            ReplayLedger ledger;
            ledger.load(base, false);
            std::string reason;
            (void)ledger.append(make_tc("fault-" + checkpoint), make_claims(jti), "allow", reason);
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            std::cerr << "crash injection expected checkpoint failure but append returned at " << checkpoint << "\n";
            return false;
        } catch (const std::exception&) {
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            return true;
        }
    };
    auto expect_dirty_journal_rejects = [&](const std::string& base, const std::string& label) {
        try { ReplayLedger reload; reload.load(base, false); failed++; std::cerr << "crash injection accepted dirty journal after " << label << "\n"; }
        catch (...) { passed++; }
        std::filesystem::remove(base + ".journal");
        try { ReplayLedger clean; clean.load(base, false); if (clean.loaded_entries == 1) passed++; else { failed++; std::cerr << "crash injection clean reload count mismatch after " << label << "\n"; } }
        catch (const std::exception& e) { failed++; std::cerr << "crash injection clean reload failed after " << label << ": " << e.what() << "\n"; }
        cleanup(base);
    };
    auto expect_completed_journal_recovers = [&](const std::string& base, const std::string& label, const std::string& jti) {
        try {
            ReplayLedger recover;
            recover.load(base, false);
            if (recover.journal_recovered_after_commit == 1 && recover.loaded_entries == 2 && recover.contains_jti(jti) && !std::filesystem::exists(base + ".journal")) passed++;
            else { failed++; std::cerr << "crash injection recovery counters mismatch after " << label << "\n"; }
        } catch (const std::exception& e) {
            failed++; std::cerr << "crash injection recovery failed after " << label << ": " << e.what() << "\n";
        }
        cleanup(base);
    };
    auto write_semantic_journal = [&](const std::string& base, const std::string& next_head, long long next_line_count, const std::string& previous_head) {
        std::string payload = read_file(base);
        SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
        write_file(base + ".journal", make_selftest_journal_v2(
            base,
            previous_head,
            0,
            next_head,
            next_line_count,
            summary.previous_head,
            sha256_hex(payload)));
    };
    try {
        {
            std::string base = base_path("after_journal");
            if (seed(base, "seed-journal") && attempt_faulted_append(base, "after-journal-fsync", "jti-after-journal")) passed++; else failed++;
            expect_dirty_journal_rejects(base, "after-journal-fsync");
        }
        {
            std::string base = base_path("after_temp");
            if (seed(base, "seed-temp") && attempt_faulted_append(base, "after-temp-fsync", "jti-after-temp")) passed++; else failed++;
            expect_dirty_journal_rejects(base, "after-temp-fsync");
        }
        {
            std::string base = base_path("after_rename");
            if (seed(base, "seed-rename") && attempt_faulted_append(base, "after-rename-before-dir-fsync", "jti-after-rename")) passed++; else failed++;
            expect_completed_journal_recovers(base, "after-rename-before-dir-fsync", "jti-after-rename");
        }
        {
            std::string base = base_path("after_dirfsync");
            if (seed(base, "seed-dirfsync") && attempt_faulted_append(base, "after-dir-fsync-before-journal-unlink", "jti-after-dirfsync")) passed++; else failed++;
            expect_completed_journal_recovers(base, "after-dir-fsync-before-journal-unlink", "jti-after-dirfsync");
        }
        {
            std::string base = base_path("wrong_head");
            if (!seed(base, "seed-wrong-head")) { failed++; }
            else {
                write_semantic_journal(base, "not-the-actual-head", 1, "GENESIS");
                try { ReplayLedger reload; reload.load(base, false); failed++; std::cerr << "crash injection accepted journal with wrong next_head\n"; }
                catch (...) { passed++; }
            }
            cleanup(base);
        }
        {
            std::string base = base_path("wrong_count");
            if (!seed(base, "seed-wrong-count")) { failed++; }
            else {
                Json first = parse_json_text(read_file(base).substr(0, read_file(base).find('\n')));
                write_semantic_journal(base, first.at("entry_hash").str(), 99, "GENESIS");
                try { ReplayLedger reload; reload.load(base, false); failed++; std::cerr << "crash injection accepted journal with wrong next_line_count\n"; }
                catch (...) { passed++; }
            }
            cleanup(base);
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger crash injection selftest exception: " << e.what() << "\n";
    }
    ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
    std::cout << "anonsync_core ledger crash injection selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_batch_transaction_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0598_batch_transaction_" + std::to_string(static_cast<long long>(std::time(nullptr)));
    auto base_path = [&](const std::string& suffix) { return std::string("/tmp/") + stem + "_" + suffix + ".jsonl"; };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto cleanup = [&](const std::string& base) {
        std::filesystem::path p(base);
        std::filesystem::path parent = p.parent_path().empty() ? std::filesystem::path(".") : p.parent_path();
        std::string prefix = p.filename().string();
        std::error_code ec;
        for (const auto& entry : std::filesystem::directory_iterator(parent, ec)) {
            if (ec) break;
            const std::string name = entry.path().filename().string();
            if (name == prefix || starts_with(name, prefix + ".")) std::filesystem::remove(entry.path(), ec);
        }
    };
    auto append_three = [&](ReplayLedger& ledger, const std::string& prefix) -> bool {
        for (int i = 1; i <= 3; ++i) {
            std::string reason;
            if (!ledger.append(make_tc(prefix + "-case-" + std::to_string(i)), make_claims(prefix + "-jti-" + std::to_string(i)), "allow", reason)) {
                std::cerr << "batch transaction append rejected: " << reason << "\n";
                return false;
            }
        }
        return true;
    };
    try {
        {
            const std::string base = base_path("happy");
            cleanup(base);
            ReplayLedger ledger;
            ledger.load(base, true, "batch");
            if (append_three(ledger, "happy")) passed++; else failed++;
            std::string payload_before = read_file(base);
            if (payload_before.empty() && ledger.atomic_rewrite_commits == 1 && ledger.journal_records_written == 1) passed++;
            else { failed++; std::cerr << "batch transaction wrote pending entries before flush or reset counters unexpected\n"; }
            if (ledger.contains_jti("happy-jti-2") && ledger.ledger_batch_pending_entries_peak == 3) passed++;
            else { failed++; std::cerr << "batch transaction did not expose staged jti for same-process replay guard\n"; }
            std::string reason;
            if (ledger.flush(reason)) passed++; else { failed++; std::cerr << "batch transaction flush rejected: " << reason << "\n"; }
            if (ledger.atomic_rewrite_commits == 2 && ledger.directory_fsync_attempts == 2 && ledger.journal_records_written == 2 && ledger.ledger_batch_flush_commits == 1) passed++;
            else { failed++; std::cerr << "batch transaction commit counters unexpected rewrites=" << ledger.atomic_rewrite_commits << " journal=" << ledger.journal_records_written << " batch=" << ledger.ledger_batch_flush_commits << "\n"; }
            ledger.release_lock();
            { ReplayLedger reload; reload.load(base, false, "batch"); if (reload.loaded_entries == 3 && reload.contains_jti("happy-jti-3")) passed++; else { failed++; std::cerr << "batch transaction reload lost committed staged entries\n"; } }
            cleanup(base);
        }
        {
            const std::string base = base_path("dirty");
            cleanup(base);
            bool faulted = false;
            try {
                ReplayLedger ledger;
                ledger.load(base, true, "batch");
                if (!append_three(ledger, "dirty")) throw std::runtime_error("append_three failed");
                ::setenv("ANONSYNC_LEDGER_FAULT_AT", "after-journal-fsync", 1);
                std::string reason;
                (void)ledger.flush(reason);
            } catch (...) { faulted = true; }
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            if (faulted) passed++; else { failed++; std::cerr << "batch transaction did not fault at after-journal-fsync\n"; }
            try { ReplayLedger reload; reload.load(base, false, "batch"); failed++; std::cerr << "batch transaction accepted dirty pre-commit journal\n"; }
            catch (...) { passed++; }
            std::filesystem::remove(base + ".journal");
            { ReplayLedger clean; clean.load(base, false, "batch"); if (clean.loaded_entries == 0) passed++; else { failed++; std::cerr << "batch transaction dirty-clean reload should preserve old empty ledger\n"; } }
            cleanup(base);
        }
        {
            const std::string base = base_path("recover");
            cleanup(base);
            bool faulted = false;
            try {
                ReplayLedger ledger;
                ledger.load(base, true, "batch");
                if (!append_three(ledger, "recover")) throw std::runtime_error("append_three failed");
                ::setenv("ANONSYNC_LEDGER_FAULT_AT", "after-dir-fsync-before-journal-unlink", 1);
                std::string reason;
                (void)ledger.flush(reason);
            } catch (...) { faulted = true; }
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            if (faulted) passed++; else { failed++; std::cerr << "batch transaction did not fault at after-dir-fsync-before-journal-unlink\n"; }
            try {
                ReplayLedger recover;
                recover.load(base, false, "batch");
                if (recover.loaded_entries == 3 && recover.journal_recovered_after_commit == 1 && recover.contains_jti("recover-jti-3")) passed++;
                else { failed++; std::cerr << "batch transaction completed multi-entry journal did not recover cleanly\n"; }
            } catch (const std::exception& e) { failed++; std::cerr << "batch transaction completed journal recovery failed: " << e.what() << "\n"; }
            cleanup(base);
        }
        {
            const std::string base = base_path("unsupported");
            cleanup(base);
            try { ReplayLedger bad; bad.load(base, true, "not-a-mode"); failed++; std::cerr << "batch transaction accepted unsupported commit mode\n"; }
            catch (...) { passed++; }
            cleanup(base);
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger batch transaction selftest exception: " << e.what() << "\n";
    }
    ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
    std::cout << "anonsync_core ledger batch transaction selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_journal_hardening_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0599_journal_hardening_" + std::to_string(static_cast<long long>(std::time(nullptr)));
    auto base_path = [&](const std::string& suffix) { return std::string("/tmp/") + stem + "_" + suffix + ".jsonl"; };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto cleanup = [&](const std::string& base) {
        std::filesystem::path p(base);
        std::filesystem::path parent = p.parent_path().empty() ? std::filesystem::path(".") : p.parent_path();
        std::string prefix = p.filename().string();
        std::error_code ec;
        for (const auto& entry : std::filesystem::directory_iterator(parent, ec)) {
            if (ec) break;
            const std::string name = entry.path().filename().string();
            if (name == prefix || starts_with(name, prefix + ".")) std::filesystem::remove(entry.path(), ec);
        }
    };
    auto seed = [&](const std::string& base, int entries, const std::string& prefix) -> bool {
        cleanup(base);
        try {
            ReplayLedger ledger;
            ledger.load(base, true, "immediate");
            for (int i = 1; i <= entries; ++i) {
                std::string reason;
                if (!ledger.stage(make_tc(prefix + "-case-" + std::to_string(i)), make_claims(prefix + "-jti-" + std::to_string(i)), "allow", reason)) {
                    std::cerr << "journal hardening seed rejected: " << reason << "\n";
                    return false;
                }
            }
            std::string reason;
            if (!ledger.commit(reason)) {
                std::cerr << "journal hardening seed commit rejected: " << reason << "\n";
                return false;
            }
            ledger.close();
            return true;
        } catch (const std::exception& e) {
            std::cerr << "journal hardening seed failed: " << e.what() << "\n";
            return false;
        }
    };
    auto write_v2_for_current_payload = [&](const std::string& base,
                                            const std::string& ledger_path,
                                            const std::string& previous_head,
                                            long long previous_line_count,
                                            const std::string& next_head,
                                            long long next_line_count,
                                            const std::string& last_entry_previous_hash,
                                            const std::string& payload_sha256) {
        write_file(base + ".journal", make_selftest_journal_v2(
            ledger_path, previous_head, previous_line_count, next_head, next_line_count, last_entry_previous_hash, payload_sha256));
    };
    auto expect_reject = [&](const std::string& base, const std::string& label) {
        try { ReplayLedger reload; reload.load(base, false); failed++; std::cerr << "journal hardening accepted hostile journal: " << label << "\n"; }
        catch (...) { passed++; }
        std::filesystem::remove(base + ".journal");
        cleanup(base);
    };
    try {
        {
            const std::string base = base_path("recover_v2");
            if (!seed(base, 2, "recover")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base, "GENESIS", 0, summary.head, summary.line_count, summary.previous_head, sha256_hex(payload));
                try {
                    ReplayLedger reload;
                    reload.load(base, false);
                    if (reload.loaded_entries == 2 && reload.journal_recovered_after_commit == 1 && !std::filesystem::exists(base + ".journal")) passed++;
                    else { failed++; std::cerr << "journal hardening v2 completed journal recovery counters mismatch\n"; }
                } catch (const std::exception& e) { failed++; std::cerr << "journal hardening v2 completed journal recovery failed: " << e.what() << "\n"; }
            }
            cleanup(base);
        }
        {
            const std::string base = base_path("legacy_v1");
            if (!seed(base, 1, "legacy")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_file(base + ".journal", "{\n  \"format\": \"anonsync-replay-ledger-journal-v1\",\n  \"ledger_path\": \"" + json_escape(base) + "\",\n  \"previous_head\": \"GENESIS\",\n  \"next_head\": \"" + json_escape(summary.head) + "\",\n  \"next_line_count\": " + std::to_string(summary.line_count) + ",\n  \"payload_sha256\": \"" + sha256_hex(payload) + "\"\n}\n");
                expect_reject(base, "legacy-v1-format");
            }
        }
        {
            const std::string base = base_path("truncated");
            if (!seed(base, 1, "truncated")) { failed++; }
            else { write_file(base + ".journal", "{\"format\":\"anonsync-replay-ledger-journal-v2\",\"ledger_path\":"); expect_reject(base, "truncated-json"); }
        }
        {
            const std::string base = base_path("duplicate_key");
            if (!seed(base, 1, "duplicate")) { failed++; }
            else { write_file(base + ".journal", "{\"format\":\"anonsync-replay-ledger-journal-v2\",\"format\":\"anonsync-replay-ledger-journal-v2\",\"ledger_path\":\"" + json_escape(base) + "\"}\n"); expect_reject(base, "duplicate-json-key"); }
        }
        {
            const std::string base = base_path("wrong_path");
            if (!seed(base, 2, "wrongpath")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base + ".other", "GENESIS", 0, summary.head, summary.line_count, summary.previous_head, sha256_hex(payload));
                expect_reject(base, "wrong-ledger-path");
            }
        }
        {
            const std::string base = base_path("wrong_prefix");
            if (!seed(base, 2, "wrongprefix")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base, "GENESIS", 1, summary.head, summary.line_count, summary.previous_head, sha256_hex(payload));
                expect_reject(base, "wrong-previous-prefix-head");
            }
        }
        {
            const std::string base = base_path("wrong_last_previous");
            if (!seed(base, 2, "wronglast")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base, "GENESIS", 0, summary.head, summary.line_count, "not-the-last-previous-head", sha256_hex(payload));
                expect_reject(base, "wrong-last-entry-previous-hash");
            }
        }
        {
            const std::string base = base_path("rollback_count");
            if (!seed(base, 2, "rollback")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base, "GENESIS", 0, summary.head, 1, summary.previous_head, sha256_hex(payload));
                expect_reject(base, "rollback-next-line-count");
            }
        }
        {
            const std::string base = base_path("wrong_payload_digest");
            if (!seed(base, 1, "payloaddigest")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_v2_for_current_payload(base, base, "GENESIS", 0, summary.head, summary.line_count, summary.previous_head, "bad-payload-digest");
                expect_reject(base, "dirty-payload-digest");
            }
        }
        {
            const std::string base = base_path("unknown_format");
            if (!seed(base, 1, "unknown")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                std::string body = make_selftest_journal_v2(base, "GENESIS", 0, summary.head, summary.line_count, summary.previous_head, sha256_hex(payload));
                size_t pos = body.find("anonsync-replay-ledger-journal-v2");
                if (pos != std::string::npos) body.replace(pos, std::string("anonsync-replay-ledger-journal-v2").size(), "anonsync-replay-ledger-journal-v3");
                write_file(base + ".journal", body);
                expect_reject(base, "unknown-journal-format");
            }
        }
        {
            const std::string base = base_path("missing_previous_count");
            if (!seed(base, 1, "missingcount")) { failed++; }
            else {
                std::string payload = read_file(base);
                SelftestLedgerSummary summary = summarize_selftest_ledger_payload(payload);
                write_file(base + ".journal", "{\n  \"format\": \"anonsync-replay-ledger-journal-v2\",\n  \"ledger_path\": \"" + json_escape(base) + "\",\n  \"previous_head\": \"GENESIS\",\n  \"next_head\": \"" + json_escape(summary.head) + "\",\n  \"next_line_count\": " + std::to_string(summary.line_count) + ",\n  \"last_entry_previous_hash\": \"" + json_escape(summary.previous_head) + "\",\n  \"payload_sha256\": \"" + sha256_hex(payload) + "\"\n}\n");
                expect_reject(base, "missing-previous-line-count");
            }
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger journal hardening selftest exception: " << e.what() << "\n";
    }
    ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
    std::cout << "anonsync_core ledger journal hardening selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_backend_interface_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0600_backend_interface_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string dir = "/tmp";
    auto base_path = [&](const std::string& suffix) { return dir + "/" + stem + "_" + suffix + ".jsonl"; };
    auto cleanup = [&](const std::string& base) {
        std::filesystem::path p(base);
        std::filesystem::path parent = p.parent_path().empty() ? std::filesystem::path(".") : p.parent_path();
        std::string prefix = p.filename().string();
        std::error_code ec;
        for (const auto& entry : std::filesystem::directory_iterator(parent, ec)) {
            if (ec) break;
            const std::string name = entry.path().filename().string();
            if (name == prefix || starts_with(name, prefix + ".")) {
                std::filesystem::remove(entry.path(), ec);
            }
        }
    };
    auto make_tc = [](const std::string& case_id, const std::string& source = "", const std::string& id = "") {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["cloud_event_source"] = json_string_value(source);
        tc.o["cloud_event_id"] = json_string_value(id);
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto expect_load_reject = [&](const std::string& base, const std::string& label) {
        try { ReplayLedger ledger; ledger.load(base, false, "batch"); failed++; std::cerr << "backend interface accepted hostile sidecar case: " << label << "\n"; }
        catch (...) { passed++; }
        cleanup(base);
    };
    try {
        {
            const std::string base = base_path("interface_stage_commit");
            cleanup(base);
            std::unique_ptr<IReplayLedgerBackend> backend = std::make_unique<ReplayLedger>();
            backend->load(base, true, "batch");
            std::string reason;
            if (backend->stage(make_tc("case-a"), make_claims("jti-a"), "allow", reason) && backend->contains_jti("jti-a")) passed++;
            else { failed++; std::cerr << "backend interface stage did not publish staged jti: " << reason << "\n"; }
            if (backend->stage(make_tc("case-b"), make_claims("jti-b"), "allow", reason) && backend->commit(reason)) passed++;
            else { failed++; std::cerr << "backend interface commit failed: " << reason << "\n"; }
            backend->close();
            ReplayLedger reload;
            reload.load(base, false, "batch");
            if (reload.loaded_entries == 2 && reload.contains_jti("jti-a") && reload.contains_jti("jti-b")) passed++;
            else { failed++; std::cerr << "backend interface reload did not preserve committed staged entries\n"; }
            cleanup(base);
        }
        {
            const std::string base = base_path("batch_lock");
            cleanup(base);
            ReplayLedger holder;
            holder.load(base, true, "batch");
            try { ReplayLedger contender; contender.load(base, false, "batch"); failed++; std::cerr << "backend interface accepted concurrent batch owner\n"; }
            catch (...) { passed++; }
            cleanup(base);
        }
        {
            const std::string base = base_path("interrupted_unlink");
            cleanup(base);
            try {
                ReplayLedger ledger;
                ledger.load(base, true, "batch");
                std::string reason;
                if (!ledger.stage(make_tc("case-unlink"), make_claims("jti-unlink"), "allow", reason)) {
                    throw std::runtime_error("stage failed before journal-unlink fault: " + reason);
                }
                ::setenv("ANONSYNC_LEDGER_FAULT_AT", "after-dir-fsync-before-journal-unlink", 1);
                (void)ledger.commit(reason);
                failed++;
                std::cerr << "backend interface expected interrupted journal unlink fault but commit returned\n";
            } catch (const std::exception&) {
                passed++;
            }
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            try {
                ReplayLedger recover;
                recover.load(base, false, "batch");
                if (recover.journal_recovered_after_commit == 1 && recover.loaded_entries == 1 && recover.contains_jti("jti-unlink") && !std::filesystem::exists(base + ".journal")) passed++;
                else { failed++; std::cerr << "backend interface did not recover interrupted journal unlink\n"; }
            } catch (const std::exception& e) { failed++; std::cerr << "backend interface interrupted unlink recovery failed: " << e.what() << "\n"; }
            cleanup(base);
        }
        {
            const std::string base = base_path("dirty_batch");
            cleanup(base);
            try {
                ReplayLedger ledger;
                ledger.load(base, true, "batch");
                std::string reason;
                if (!ledger.stage(make_tc("case-dirty"), make_claims("jti-dirty"), "allow", reason)) {
                    throw std::runtime_error("stage failed before dirty batch fault: " + reason);
                }
                ::setenv("ANONSYNC_LEDGER_FAULT_AT", "after-journal-fsync", 1);
                (void)ledger.commit(reason);
                failed++;
                std::cerr << "backend interface expected dirty batch journal fault but commit returned\n";
            } catch (const std::exception&) { passed++; }
            ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
            expect_load_reject(base, "dirty-batch-journal");
        }
        {
            const std::string base = base_path("ledger_symlink");
            cleanup(base);
            const std::string target = base + ".target";
            write_file(target, "");
            if (::symlink(target.c_str(), base.c_str()) != 0) { failed++; std::cerr << "backend interface could not create ledger symlink\n"; cleanup(base); }
            else expect_load_reject(base, "ledger-symlink");
        }
        {
            const std::string base = base_path("journal_symlink");
            cleanup(base);
            write_file(base, "");
            const std::string target = base + ".journal.target";
            write_file(target, "{}");
            if (::symlink(target.c_str(), (base + ".journal").c_str()) != 0) { failed++; std::cerr << "backend interface could not create journal symlink\n"; cleanup(base); }
            else expect_load_reject(base, "journal-symlink");
        }
        {
            const std::string base = base_path("lock_symlink");
            cleanup(base);
            const std::string target = base + ".lock.target";
            write_file(target, "");
            if (::symlink(target.c_str(), (base + ".lock").c_str()) != 0) { failed++; std::cerr << "backend interface could not create lock symlink\n"; cleanup(base); }
            else expect_load_reject(base, "lock-symlink");
        }
        {
            const std::string base = base_path("temp_symlink");
            cleanup(base);
            const std::string target = base + ".tmp.target";
            write_file(target, "");
            const std::string predictable_tmp = base + ".tmp." + std::to_string(static_cast<long long>(::getpid())) + ".1";
            if (::symlink(target.c_str(), predictable_tmp.c_str()) != 0) { failed++; std::cerr << "backend interface could not create temp symlink\n"; cleanup(base); }
            else {
                try { ReplayLedger ledger; ledger.load(base, true, "batch"); failed++; std::cerr << "backend interface accepted temp symlink collision\n"; }
                catch (...) { passed++; }
                cleanup(base);
            }
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger backend interface selftest exception: " << e.what() << "\n";
    }
    ::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
    std::cout << "anonsync_core ledger backend interface selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}




int run_ledger_effect_idempotency_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0625_effect_idempotency_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string jsonl_path = "/tmp/" + stem + ".jsonl";
    const std::string sqlite_path = "/tmp/" + stem + ".sqlite";
    const std::string shared_effect = sha256_hex("rev0625-shared-prepared-effect");
    auto cleanup = [&]() {
        std::remove(jsonl_path.c_str());
        std::remove((jsonl_path + ".journal").c_str());
        std::remove((jsonl_path + ".lock").c_str());
        std::remove(sqlite_path.c_str());
        std::remove((sqlite_path + "-wal").c_str());
        std::remove((sqlite_path + "-shm").c_str());
        std::remove((sqlite_path + ".write.lock").c_str());
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect_key) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-effect-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect_key);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-effect-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-effect-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto exercise_backend = [&](const std::string& backend_name, const std::string& path) {
        try {
            auto backend = create_replay_ledger_backend(backend_name);
            backend->load(path, true, "batch");
            std::string reason;
            if (backend->stage(make_tc(backend_name + "-effect-a", shared_effect), make_claims(backend_name + "-jti-a"), "allow", reason) && backend->contains_effect_idempotency_key(shared_effect)) passed++;
            else { failed++; std::cerr << backend_name << " did not stage/publish prepared effect key: " << reason << "\n"; }
            if (!backend->stage(make_tc(backend_name + "-effect-b", shared_effect), make_claims(backend_name + "-jti-b"), "allow", reason) && reason.find("effect idempotency") != std::string::npos) passed++;
            else { failed++; std::cerr << backend_name << " did not reject duplicate staged prepared effect key: " << reason << "\n"; }
            if (!backend->stage(make_tc(backend_name + "-bad-effect", "not-a-sha256"), make_claims(backend_name + "-jti-bad"), "allow", reason) && reason.find("effect_idempotency_key") != std::string::npos) passed++;
            else { failed++; std::cerr << backend_name << " did not reject invalid effect key: " << reason << "\n"; }
            const std::string fallback_case_id = backend_name + "-fallback-effect";
            const std::string fallback_jti = backend_name + "-jti-fallback";
            const std::string fallback_key = sha256_hex(length_prefixed_security_tuple("anonsync-effect-idempotency-legacy-v1", {
                {"case_id", fallback_case_id},
                {"kind", "openapi"},
                {"operation_id", "selftest-effect-op"},
                {"contract_digest_sha256", sha256_hex("selftest-effect-contract")},
                {"cloud_event_source", ""},
                {"cloud_event_id", ""},
            }));
            if (backend->stage(make_tc(fallback_case_id, ""), make_claims(fallback_jti), "allow", reason) && backend->contains_effect_idempotency_key(fallback_key)) passed++;
            else { failed++; std::cerr << backend_name << " did not derive the framed legacy-v1 fallback effect key: " << reason << "\n"; }
            if (backend->commit(reason)) passed++;
            else { failed++; std::cerr << backend_name << " prepared-effect commit failed: " << reason << "\n"; }
            backend->close();
            auto reload = create_replay_ledger_backend(backend_name);
            reload->load(path, false, "batch");
            if (reload->contains_effect_idempotency_key(shared_effect)) passed++;
            else { failed++; std::cerr << backend_name << " reload lost prepared effect key index\n"; }
            if (!reload->stage(make_tc(backend_name + "-effect-c", shared_effect), make_claims(backend_name + "-jti-c"), "allow", reason) && reason.find("effect idempotency") != std::string::npos) passed++;
            else { failed++; std::cerr << backend_name << " did not reject duplicate prepared effect key after reload: " << reason << "\n"; }
            reload->close();
        } catch (const std::exception& e) {
            failed++;
            std::cerr << backend_name << " prepared-effect idempotency selftest exception: " << e.what() << "\n";
        }
    };
    cleanup();
    exercise_backend("local-jsonl", jsonl_path);
    exercise_backend("sqlite-wal", sqlite_path);
    cleanup();
    std::cout << "anonsync_core ledger effect idempotency selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_effect_transition_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0631_sqlite_effect_transition_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string snapshot_path = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string report_path = "/tmp/" + stem + "_pending.json";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string bad_binding_intent_path = "/tmp/" + stem + "_bad_binding_intent.json";
    const std::string valid_intent_path = "/tmp/" + stem + "_valid_intent.json";
    const std::string wrong_ledger_intent_path = "/tmp/" + stem + "_wrong_ledger_intent.json";
    const std::string duplicate_intent_path = "/tmp/" + stem + "_duplicate_intent.json";
    const std::string unknown_intent_path = "/tmp/" + stem + "_unknown_intent.json";
    const std::string bad_digest_intent_path = "/tmp/" + stem + "_bad_digest_intent.json";
    const std::string effect_key = sha256_hex("rev0631-prepared-effect-key");
    const std::string unknown_effect_key = sha256_hex("rev0631-unknown-prepared-effect-key");
    const std::string result_digest = sha256_hex("downstream response: applied rev0631 ledger-instance signed only");
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, snapshot_path, report_path, trust_path, bad_binding_intent_path, valid_intent_path, wrong_ledger_intent_path, duplicate_intent_path, unknown_intent_path, bad_digest_intent_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-effect-transition-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-effect-transition-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-effect-transition-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    cleanup();
    try {
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            if (backend->stage(make_tc("sqlite-effect-transition-case-a", effect_key), make_claims("sqlite-effect-transition-jti-a"), "allow", reason) && backend->commit(reason)) passed++;
            else { failed++; std::cerr << "effect transition seed prepared effect failed: " << reason << "\n"; }
            backend->close();
        }
        SelftestPreparedEffectRef effect_ref = selftest_prepared_effect_ref_for_key(ledger_path, effect_key);
        if (run_sqlite_effect_transition_command(ledger_path, effect_key, effect_ref.sequence, effect_ref.entry_hash, "applied", result_digest, "raw public API should fail closed") != 0) passed++;
        else { failed++; std::cerr << "effect transition raw public API accepted an unsigned terminal transition\n"; }
        if (run_sqlite_effect_pending_report_command(ledger_path, report_path) == 0) passed++;
        else { failed++; std::cerr << "effect transition selftest pending report command failed\n"; }
        const std::string before_text = read_file(report_path);
        Json before = parse_json_text(before_text);
        const std::string prepared_head = before.at("decision_head_hash").str();
        const std::string transition_head = before.at("effect_transition_head_hash").str();
        const std::string ledger_instance_id = before.at("ledger_instance_id").str();
        effect_ref = selftest_prepared_effect_ref_from_pending_report(before_text, effect_key);
        auto root = make_selftest_restore_root("rev0631-effect-transition-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root);
        write_file(trust_path, trust);
        const std::string trust_sha = sha256_hex(trust);
        auto write_intent = [&](const std::string& path,
                                const std::string& intent_id,
                                const std::string& effect,
                                long long sequence,
                                const std::string& entry_hash,
                                const std::string& terminal_state,
                                const std::string& digest,
                                const std::string& reason,
                                const std::string& prepared_head_override = std::string(),
                                const std::string& transition_head_override = std::string(),
                                const std::string& ledger_instance_override = std::string()) {
            const std::string intent = make_effect_transition_intent_v1_selftest(root,
                                                                                 intent_id,
                                                                                 "2026-06-18T02:44:00Z",
                                                                                 ledger_instance_override.empty() ? ledger_instance_id : ledger_instance_override,
                                                                                 prepared_head_override.empty() ? prepared_head : prepared_head_override,
                                                                                 transition_head_override.empty() ? transition_head : transition_head_override,
                                                                                 effect,
                                                                                 sequence,
                                                                                 entry_hash,
                                                                                 terminal_state,
                                                                                 digest,
                                                                                 reason);
            write_file(path, intent);
        };
        write_intent(bad_binding_intent_path, "rev0631-selftest-bad-binding", effect_key, effect_ref.sequence, std::string(64, '0'), "applied", result_digest, "bad prepared binding should fail");
        if (run_sqlite_effect_signed_transition_command(ledger_path, bad_binding_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect transition accepted signed intent with stale/mismatched prepared-entry hash\n"; }
        write_intent(wrong_ledger_intent_path, "rev0631-selftest-wrong-ledger", effect_key, effect_ref.sequence, effect_ref.entry_hash, "applied", result_digest, "wrong ledger instance should fail", std::string(), std::string(), std::string(64, '0'));
        if (run_sqlite_effect_signed_transition_command(ledger_path, wrong_ledger_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect transition accepted signed intent for a different ledger instance id\n"; }
        write_intent(valid_intent_path, "rev0631-selftest-intent-a", effect_key, effect_ref.sequence, effect_ref.entry_hash, "applied", result_digest, "selftest downstream applied under signed intent");
        if (run_sqlite_effect_signed_transition_command(ledger_path, valid_intent_path, trust_path, trust_sha) == 0) passed++;
        else { failed++; std::cerr << "effect transition signed command rejected valid applied transition\n"; }
        {
            auto reload = create_replay_ledger_backend("sqlite-wal");
            reload->load(ledger_path, false, "batch");
            ReplayLedgerStats st = reload->stats();
            if (st.effect_transition_line_count == 1 && st.effect_terminal_transitions == 0 && st.effect_transition_head_hash != "GENESIS") passed++;
            else { failed++; std::cerr << "effect transition reload stats unexpected count=" << st.effect_transition_line_count << " head=" << st.effect_transition_head_hash << "\n"; }
            reload->close();
        }
        {
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(ledger_path.c_str(), &raw, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "effect transition selftest could not inspect sqlite ledger\n";
                if (raw) sqlite3_close(raw);
            } else {
                sqlite3_stmt* stmt = nullptr;
                const char* sql = "SELECT COUNT(*), SUM(CASE WHEN effect_idempotency_key=?1 AND terminal_state='applied' AND result_digest_sha256=?2 AND transition_intent_id='rev0631-selftest-intent-a' THEN 1 ELSE 0 END) FROM effect_transitions";
                if (sqlite3_prepare_v2(raw, sql, -1, &stmt, nullptr) != SQLITE_OK) {
                    failed++; std::cerr << "effect transition inspect prepare failed\n";
                } else {
                    sqlite3_bind_text(stmt, 1, effect_key.c_str(), -1, SQLITE_TRANSIENT);
                    sqlite3_bind_text(stmt, 2, result_digest.c_str(), -1, SQLITE_TRANSIENT);
                    if (sqlite3_step(stmt) == SQLITE_ROW && sqlite3_column_int64(stmt, 0) == 1 && sqlite3_column_int64(stmt, 1) == 1) passed++;
                    else { failed++; std::cerr << "effect transition row not persisted as signed applied transition\n"; }
                }
                if (stmt) sqlite3_finalize(stmt);
                sqlite3_close(raw);
            }
        }
        write_intent(duplicate_intent_path, "rev0631-selftest-duplicate", effect_key, effect_ref.sequence, effect_ref.entry_hash, "failed", sha256_hex("second terminal attempt"), "duplicate should fail");
        if (run_sqlite_effect_signed_transition_command(ledger_path, duplicate_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect transition accepted duplicate signed terminal transition\n"; }
        write_intent(unknown_intent_path, "rev0631-selftest-unknown", unknown_effect_key, effect_ref.sequence, effect_ref.entry_hash, "applied", sha256_hex("unknown result"), "unknown key should fail");
        if (run_sqlite_effect_signed_transition_command(ledger_path, unknown_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect transition accepted signed intent for unknown prepared effect key\n"; }
        write_intent(bad_digest_intent_path, "rev0631-selftest-bad-digest", effect_key, effect_ref.sequence, effect_ref.entry_hash, "applied", "not-a-sha256", "bad digest should fail");
        if (run_sqlite_effect_signed_transition_command(ledger_path, bad_digest_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect transition accepted invalid result digest under signed intent\n"; }
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, false, "batch");
            std::string reason;
            if (backend->backup_snapshot(snapshot_path, reason)) passed++;
            else { failed++; std::cerr << "effect transition snapshot verification failed: " << reason << "\n"; }
            backend->close();
        }
        {
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(ledger_path.c_str(), &raw, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "effect transition selftest could not tamper transition hash\n";
                if (raw) sqlite3_close(raw);
            } else {
                char* err = nullptr;
                int rc = sqlite3_exec(raw, "UPDATE effect_transitions SET transition_hash='0000000000000000000000000000000000000000000000000000000000000000' WHERE sequence=1;", nullptr, nullptr, &err);
                if (rc != SQLITE_OK) { failed++; std::cerr << "effect transition tamper exec failed: " << (err ? err : "") << "\n"; if (err) sqlite3_free(err); }
                sqlite3_close(raw);
                try { auto bad = create_replay_ledger_backend("sqlite-wal"); bad->load(ledger_path, false, "batch"); failed++; std::cerr << "effect transition reload accepted tampered transition hash\n"; }
                catch (...) { passed++; }
            }
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite effect transition selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite effect transition selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_effect_pending_recovery_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0631_sqlite_effect_pending_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string report_path = "/tmp/" + stem + "_pending.json";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string stale_intent_path = "/tmp/" + stem + "_stale_intent.json";
    const std::string valid_intent_path = "/tmp/" + stem + "_valid_intent.json";
    const std::string wrong_ledger_intent_path = "/tmp/" + stem + "_wrong_ledger_intent.json";
    const std::string effect_a = sha256_hex("rev0631-pending-effect-a");
    const std::string effect_b = sha256_hex("rev0631-pending-effect-b");
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, report_path, trust_path, stale_intent_path, valid_intent_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-effect-pending-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-effect-pending-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-effect-pending-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto check_pending = [&](const std::string& report_text, long long expected_prepared, long long expected_terminal, long long expected_pending, const std::string& expected_pending_key) {
        Json report = parse_json_text(report_text);
        bool ok = report.at("format").str() == "anonsync-sqlite-effect-pending-report-v5-outbox-claim" &&
                  report.at("outbox_format").str() == "anonsync-sqlite-effect-outbox-v1" &&
                  report.at("prepared_effect_count").integer(-1) == expected_prepared &&
                  report.at("terminal_effect_count").integer(-1) == expected_terminal &&
                  report.at("pending_effect_count").integer(-1) == expected_pending &&
                  report.at("outbox_reserved_count").integer(-1) == expected_pending &&
                  report.at("outbox_inflight_count").integer(-1) == 0 &&
                  report.at("outbox_terminal_count").integer(-1) == expected_terminal &&
                  report.at("effect_transition_head_hash").str().size() > 0 &&
                  report.at("ledger_instance_id").str().size() == 64;
        if (expected_pending == 1) {
            ok = ok && report.at("pending_effects").is_array() && report.at("pending_effects").a.size() == 1 &&
                 report.at("pending_effects").at(0).at("effect_idempotency_key").str() == expected_pending_key &&
                 report.at("pending_effects").at(0).at("entry_hash").str().size() == 64 &&
                 report.at("pending_effects").at(0).at("outbox_state").str() == "reserved";
        }
        if (expected_pending == 2) {
            ok = ok && report.at("pending_effects").is_array() && report.at("pending_effects").a.size() == 2 &&
                 report.at("pending_effects").at(0).at("outbox_state").str() == "reserved" &&
                 report.at("pending_effects").at(1).at("outbox_state").str() == "reserved";
        }
        return ok;
    };
    cleanup();
    try {
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            if (!backend->stage(make_tc("pending-case-a", effect_a), make_claims("pending-jti-a"), "allow", reason)) throw std::runtime_error("pending recovery stage A failed: " + reason);
            if (!backend->stage(make_tc("pending-case-b", effect_b), make_claims("pending-jti-b"), "allow", reason)) throw std::runtime_error("pending recovery stage B failed: " + reason);
            if (!backend->commit(reason)) throw std::runtime_error("pending recovery commit failed: " + reason);
            backend->close();
        }
        if (run_sqlite_effect_pending_report_command(ledger_path, report_path) == 0) passed++;
        else { failed++; std::cerr << "effect pending recovery initial report command failed\n"; }
        const std::string before = read_file(report_path);
        if (check_pending(before, 2, 0, 2, "")) passed++;
        else { failed++; std::cerr << "effect pending report did not list both prepared effects before terminal transition\n"; }
        SelftestPreparedEffectRef pending_ref_a = selftest_prepared_effect_ref_from_pending_report(before, effect_a);
        Json before_report = parse_json_text(before);
        const std::string prepared_head = before_report.at("decision_head_hash").str();
        const std::string transition_head = before_report.at("effect_transition_head_hash").str();
        const std::string ledger_instance_id = before_report.at("ledger_instance_id").str();
        auto root = make_selftest_restore_root("rev0631-pending-transition-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root);
        write_file(trust_path, trust);
        const std::string trust_sha = sha256_hex(trust);
        const std::string stale_intent = make_effect_transition_intent_v1_selftest(root,
                                                                                   "rev0631-pending-stale-sequence",
                                                                                   "2026-06-18T02:44:00Z",
                                                                                   ledger_instance_id,
                                                                                   prepared_head,
                                                                                   transition_head,
                                                                                   effect_a,
                                                                                   pending_ref_a.sequence + 1,
                                                                                   pending_ref_a.entry_hash,
                                                                                   "applied",
                                                                                   sha256_hex("rev0631 pending effect stale sequence"),
                                                                                   "stale pending evidence should fail");
        write_file(stale_intent_path, stale_intent);
        if (run_sqlite_effect_signed_transition_command(ledger_path, stale_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "effect pending recovery accepted signed stale prepared sequence\n"; }
        const std::string valid_intent = make_effect_transition_intent_v1_selftest(root,
                                                                                   "rev0631-pending-valid-applied",
                                                                                   "2026-06-18T02:44:00Z",
                                                                                   ledger_instance_id,
                                                                                   prepared_head,
                                                                                   transition_head,
                                                                                   effect_a,
                                                                                   pending_ref_a.sequence,
                                                                                   pending_ref_a.entry_hash,
                                                                                   "applied",
                                                                                   sha256_hex("rev0631 pending effect applied"),
                                                                                   "selftest pending effect applied");
        write_file(valid_intent_path, valid_intent);
        if (run_sqlite_effect_signed_transition_command(ledger_path, valid_intent_path, trust_path, trust_sha) == 0) passed++;
        else { failed++; std::cerr << "effect pending recovery signed transition command rejected valid transition\n"; }
        if (run_sqlite_effect_pending_report_command(ledger_path, report_path) == 0) passed++;
        else { failed++; std::cerr << "effect pending recovery report command failed\n"; }
        const std::string after = read_file(report_path);
        if (check_pending(after, 2, 1, 1, effect_b)) passed++;
        else { failed++; std::cerr << "effect pending report did not exclude terminal effect after transition\n"; }
        {
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(ledger_path.c_str(), &raw, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "effect pending selftest could not open sqlite ledger for tamper\n";
                if (raw) sqlite3_close(raw);
            } else {
                char* err = nullptr;
                int rc = sqlite3_exec(raw, "UPDATE effect_transition_metadata SET head_hash='0000000000000000000000000000000000000000000000000000000000000000' WHERE id=1;", nullptr, nullptr, &err);
                if (rc != SQLITE_OK) { failed++; std::cerr << "effect pending tamper exec failed: " << (err ? err : "") << "\n"; if (err) sqlite3_free(err); }
                sqlite3_close(raw);
                if (run_sqlite_effect_pending_report_command(ledger_path, report_path) != 0) passed++;
                else { failed++; std::cerr << "effect pending report accepted tampered transition metadata\n"; }
            }
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite effect pending recovery selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite effect pending recovery selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_effect_signed_transition_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0631_signed_effect_transition_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string report_path = "/tmp/" + stem + "_pending.json";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string intent_path = "/tmp/" + stem + "_intent.json";
    const std::string tampered_intent_path = "/tmp/" + stem + "_tampered_intent.json";
    const std::string stale_intent_path = "/tmp/" + stem + "_stale_intent.json";
    const std::string effect_key = sha256_hex("rev0631-signed-transition-effect");
    const std::string result_digest = sha256_hex("rev0631 signed transition downstream result");
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, report_path, trust_path, intent_path, tampered_intent_path, stale_intent_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-signed-effect-transition-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-signed-effect-transition-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-signed-effect-transition-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    cleanup();
    try {
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            if (backend->stage(make_tc("signed-transition-case-a", effect_key), make_claims("signed-transition-jti-a"), "allow", reason) && backend->commit(reason)) passed++;
            else { failed++; std::cerr << "signed effect transition seed prepared effect failed: " << reason << "\n"; }
            backend->close();
        }
        if (run_sqlite_effect_pending_report_command(ledger_path, report_path) == 0) passed++;
        else { failed++; std::cerr << "signed transition selftest pending report command failed\n"; }
        const std::string before_text = read_file(report_path);
        Json before = parse_json_text(before_text);
        const std::string prepared_head = before.at("decision_head_hash").str();
        const std::string transition_head = before.at("effect_transition_head_hash").str();
        const std::string ledger_instance_id = before.at("ledger_instance_id").str();
        SelftestPreparedEffectRef effect_ref = selftest_prepared_effect_ref_from_pending_report(before_text, effect_key);
        auto root = make_selftest_restore_root("rev0631-effect-transition-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root);
        write_file(trust_path, trust);
        const std::string trust_sha = sha256_hex(trust);
        const std::string valid_intent = make_effect_transition_intent_v1_selftest(root,
                                                                                   "rev0631-selftest-intent-a",
                                                                                   "2026-06-18T02:44:00Z",
                                                                                   ledger_instance_id,
                                                                                   prepared_head,
                                                                                   transition_head,
                                                                                   effect_key,
                                                                                   effect_ref.sequence,
                                                                                   effect_ref.entry_hash,
                                                                                   "applied",
                                                                                   result_digest,
                                                                                   "signed selftest downstream applied");
        write_file(intent_path, valid_intent);
        if (run_sqlite_effect_signed_transition_command(ledger_path, intent_path, trust_path, std::string(64, '0')) != 0) passed++;
        else { failed++; std::cerr << "signed transition accepted wrong trust digest pin\n"; }
        {
            std::string tampered_intent = valid_intent;
            const std::string tampered_digest = sha256_hex("tampered transition result");
            size_t pos = tampered_intent.find(result_digest);
            if (pos == std::string::npos) throw std::runtime_error("signed transition selftest could not find result digest for tamper");
            tampered_intent.replace(pos, result_digest.size(), tampered_digest);
            write_file(tampered_intent_path, tampered_intent);
        }
        if (run_sqlite_effect_signed_transition_command(ledger_path, tampered_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "signed transition accepted tampered intent under old signature\n"; }
        const std::string stale_intent = make_effect_transition_intent_v1_selftest(root,
                                                                                   "rev0631-selftest-stale-intent",
                                                                                   "2026-06-18T02:44:00Z",
                                                                                   ledger_instance_id,
                                                                                   std::string(64, '0'),
                                                                                   transition_head,
                                                                                   effect_key,
                                                                                   effect_ref.sequence,
                                                                                   effect_ref.entry_hash,
                                                                                   "applied",
                                                                                   result_digest,
                                                                                   "stale prepared ledger head should fail");
        write_file(stale_intent_path, stale_intent);
        if (run_sqlite_effect_signed_transition_command(ledger_path, stale_intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "signed transition accepted stale prepared-ledger head\n"; }
        if (run_sqlite_effect_signed_transition_command(ledger_path, intent_path, trust_path, trust_sha) == 0) passed++;
        else { failed++; std::cerr << "signed transition rejected valid signed intent\n"; }
        {
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(ledger_path.c_str(), &raw, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "signed transition selftest could not inspect sqlite ledger\n";
                if (raw) sqlite3_close(raw);
            } else {
                sqlite3_stmt* stmt = nullptr;
                const char* sql = "SELECT transition_intent_id, transition_intent_signer_kid, transition_intent_sha256 FROM effect_transitions WHERE effect_idempotency_key=?1";
                if (sqlite3_prepare_v2(raw, sql, -1, &stmt, nullptr) != SQLITE_OK) {
                    failed++; std::cerr << "signed transition inspect prepare failed\n";
                } else {
                    sqlite3_bind_text(stmt, 1, effect_key.c_str(), -1, SQLITE_TRANSIENT);
                    if (sqlite3_step(stmt) == SQLITE_ROW) {
                        const std::string intent_id = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
                        const std::string signer = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
                        const std::string digest = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
                        if (intent_id == "rev0631-selftest-intent-a" && signer == root.kid && digest == sha256_hex(valid_intent)) passed++;
                        else { failed++; std::cerr << "signed transition did not persist expected intent metadata\n"; }
                    } else { failed++; std::cerr << "signed transition row absent\n"; }
                }
                if (stmt) sqlite3_finalize(stmt);
                sqlite3_close(raw);
            }
        }
        if (run_sqlite_effect_signed_transition_command(ledger_path, intent_path, trust_path, trust_sha) != 0) passed++;
        else { failed++; std::cerr << "signed transition accepted duplicate terminal intent\n"; }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite signed effect transition selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite signed effect transition selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_effect_outbox_claim_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0634_effect_outbox_claim_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string claim_a_path = "/tmp/" + stem + "_claim_a.json";
    const std::string claim_b_path = "/tmp/" + stem + "_claim_b.json";
    const std::string reclaim_path = "/tmp/" + stem + "_reclaim.json";
    const std::string no_work_path = "/tmp/" + stem + "_no_work.json";
    const std::string pending_path = "/tmp/" + stem + "_pending.json";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string intent_path = "/tmp/" + stem + "_intent.json";
    const std::string bad_claim_path = "/tmp/" + stem + "_bad_claim.json";
    const std::string effect_a = sha256_hex("rev0634-outbox-claim-effect-a");
    const std::string effect_b = sha256_hex("rev0634-outbox-claim-effect-b");
    const std::string result_digest = sha256_hex("rev0634 outbox claim applied result");
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, claim_a_path, claim_b_path, reclaim_path, no_work_path, pending_path, trust_path, intent_path, bad_claim_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-outbox-claim-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-outbox-claim-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-outbox-claim-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto lower_hex_sha256 = [](const std::string& s) {
        if (s.size() != 64) return false;
        for (char c : s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
        return true;
    };
    auto read_json = [](const std::string& path) { return parse_json_text(read_file(path)); };
    auto check_claim = [&](const Json& claim, bool claimed, const std::string& expected_effect, const std::string& expected_worker, const std::string& expected_previous, long long expected_attempts) {
        const Json& row = claim.at("claim");
        bool ok = claim.at("format").str() == "anonsync-sqlite-effect-outbox-claim-v1" &&
                  claim.at("claimed").boolean(false) == claimed &&
                  claim.at("worker_id").str() == expected_worker &&
                  row.at("dispatch_attempts").integer(-1) == expected_attempts;
        if (claimed) {
            ok = ok && row.at("effect_idempotency_key").str() == expected_effect &&
                 row.at("previous_outbox_state").str() == expected_previous &&
                 row.at("outbox_state").str() == "inflight" &&
                 lower_hex_sha256(row.at("worker_claim_id").str()) &&
                 row.at("claimed_at_epoch").integer(0) > 0 &&
                 row.at("lease_expires_at_epoch").integer(0) >= row.at("claimed_at_epoch").integer(0) &&
                 row.at("prepared_sequence").integer(0) > 0 &&
                 lower_hex_sha256(row.at("prepared_entry_hash").str());
        }
        if (ok) passed++;
        else { failed++; std::cerr << "outbox claim report mismatch for worker=" << expected_worker << " effect=" << expected_effect << "\n"; }
    };
    auto pending_counts_ok = [&](long long reserved, long long inflight, long long terminal) {
        if (run_sqlite_effect_pending_report_command(ledger_path, pending_path) != 0) {
            failed++; std::cerr << "outbox claim pending report command failed\n";
            return Json();
        }
        Json report = read_json(pending_path);
        bool ok = report.at("format").str() == "anonsync-sqlite-effect-pending-report-v5-outbox-claim" &&
                  report.at("outbox_reserved_count").integer(-1) == reserved &&
                  report.at("outbox_inflight_count").integer(-1) == inflight &&
                  report.at("terminal_effect_count").integer(-1) == terminal &&
                  report.at("pending_effect_count").integer(-1) == reserved + inflight;
        if (ok) passed++;
        else { failed++; std::cerr << "outbox claim pending counters mismatch\n"; }
        return report;
    };
    auto json_int_value_local = [](long long value) { Json v; v.type = Json::Type::Number; v.n = static_cast<double>(value); return v; };
    auto query_outbox = [&](const std::string& effect) {
        sqlite3* db = nullptr;
        if (sqlite3_open_v2(ledger_path.c_str(), &db, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
            std::string msg = db ? sqlite3_errmsg(db) : "sqlite open failed";
            if (db) sqlite3_close(db);
            throw std::runtime_error("outbox claim inspect open failed: " + msg);
        }
        sqlite3_stmt* stmt = nullptr;
        const char* sql = "SELECT outbox_state, dispatch_attempts, worker_claim_id, worker_id, claimed_at_epoch, lease_expires_at_epoch, last_result_digest_sha256, updated_at_sequence FROM effect_outbox WHERE effect_idempotency_key=?1";
        if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
            std::string msg = sqlite3_errmsg(db);
            sqlite3_close(db);
            throw std::runtime_error("outbox claim inspect prepare failed: " + msg);
        }
        sqlite3_bind_text(stmt, 1, effect.c_str(), -1, SQLITE_TRANSIENT);
        Json row; row.type = Json::Type::Object;
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            row.o["outbox_state"] = json_string_value(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0)));
            row.o["dispatch_attempts"] = json_int_value_local(sqlite3_column_int64(stmt, 1));
            row.o["worker_claim_id"] = json_string_value(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2)));
            row.o["worker_id"] = json_string_value(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3)));
            row.o["claimed_at_epoch"] = json_int_value_local(sqlite3_column_int64(stmt, 4));
            row.o["lease_expires_at_epoch"] = json_int_value_local(sqlite3_column_int64(stmt, 5));
            row.o["last_result_digest_sha256"] = json_string_value(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6)));
            row.o["updated_at_sequence"] = json_int_value_local(sqlite3_column_int64(stmt, 7));
        } else {
            sqlite3_finalize(stmt);
            sqlite3_close(db);
            throw std::runtime_error("outbox claim inspect row missing");
        }
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return row;
    };
    cleanup();
    try {
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            bool ok = backend->stage(make_tc("outbox-claim-case-a", effect_a), make_claims("outbox-claim-jti-a"), "allow", reason) &&
                      backend->stage(make_tc("outbox-claim-case-b", effect_b), make_claims("outbox-claim-jti-b"), "allow", reason) &&
                      backend->commit(reason);
            if (ok) passed++; else { failed++; std::cerr << "outbox claim seed failed: " << reason << "\n"; }
            backend->close();
        }
        pending_counts_ok(2, 0, 0);
        if (run_sqlite_effect_outbox_claim_command(ledger_path, "worker-A", 1800000000LL, 60LL, claim_a_path) == 0) passed++;
        else { failed++; std::cerr << "outbox claim first command failed\n"; }
        Json claim_a = read_json(claim_a_path);
        check_claim(claim_a, true, effect_a, "worker-A", "reserved", 1);
        pending_counts_ok(1, 1, 0);
        if (run_sqlite_effect_outbox_claim_command(ledger_path, "worker-B", 1800000001LL, 60LL, claim_b_path) == 0) passed++;
        else { failed++; std::cerr << "outbox claim second command failed\n"; }
        Json claim_b = read_json(claim_b_path);
        check_claim(claim_b, true, effect_b, "worker-B", "reserved", 1);
        if (claim_b.at("claim").at("effect_idempotency_key").str() != claim_a.at("claim").at("effect_idempotency_key").str()) passed++;
        else { failed++; std::cerr << "outbox claim claimed same effect twice before lease expiry\n"; }
        pending_counts_ok(0, 2, 0);
        if (run_sqlite_effect_outbox_claim_command(ledger_path, "worker-D", 1800000050LL, 60LL, no_work_path) == 0) passed++;
        else { failed++; std::cerr << "outbox no-work claim command failed before lease expiry\n"; }
        {
            Json no_work = read_json(no_work_path);
            if (!no_work.at("claimed").boolean(true) && no_work.at("format").str() == "anonsync-sqlite-effect-outbox-claim-v1") passed++;
            else { failed++; std::cerr << "outbox no-work claim report unexpected before lease expiry\n"; }
        }
        if (run_sqlite_effect_outbox_claim_command(ledger_path, "worker-C", 1800000061LL, 90LL, reclaim_path) == 0) passed++;
        else { failed++; std::cerr << "outbox stale reclaim command failed\n"; }
        Json reclaim = read_json(reclaim_path);
        check_claim(reclaim, true, effect_a, "worker-C", "inflight", 2);
        if (reclaim.at("claim").at("worker_claim_id").str() != claim_a.at("claim").at("worker_claim_id").str()) passed++;
        else { failed++; std::cerr << "outbox stale reclaim reused old worker claim id\n"; }
        if (run_sqlite_effect_outbox_claim_command(ledger_path, "bad\nworker", 1800000062LL, 60LL, bad_claim_path) != 0) passed++;
        else { failed++; std::cerr << "outbox claim accepted control-bearing worker id\n"; }
        Json pending = pending_counts_ok(0, 2, 0);
        const std::string prepared_head = pending.at("decision_head_hash").str();
        const std::string transition_head = pending.at("effect_transition_head_hash").str();
        const std::string ledger_instance_id = pending.at("ledger_instance_id").str();
        SelftestPreparedEffectRef effect_ref = selftest_prepared_effect_ref_from_pending_report(read_file(pending_path), effect_a);
        auto root = make_selftest_restore_root("rev0634-effect-outbox-claim-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root);
        write_file(trust_path, trust);
        const std::string trust_sha = sha256_hex(trust);
        const std::string intent = make_effect_transition_intent_v1_selftest(root,
                                                                             "rev0634-outbox-claim-terminal-intent",
                                                                             "2026-06-18T02:44:00Z",
                                                                             ledger_instance_id,
                                                                             prepared_head,
                                                                             transition_head,
                                                                             effect_a,
                                                                             effect_ref.sequence,
                                                                             effect_ref.entry_hash,
                                                                             "applied",
                                                                             result_digest,
                                                                             "rev0634 selftest terminal close from inflight outbox lease");
        write_file(intent_path, intent);
        if (run_sqlite_effect_signed_transition_command(ledger_path, intent_path, trust_path, trust_sha) == 0) passed++;
        else { failed++; std::cerr << "outbox claim selftest rejected signed terminal from inflight row\n"; }
        Json terminal_row = query_outbox(effect_a);
        bool terminal_ok = terminal_row.at("outbox_state").str() == "applied" &&
                           terminal_row.at("dispatch_attempts").integer(-1) == 2 &&
                           terminal_row.at("worker_id").str() == "worker-C" &&
                           lower_hex_sha256(terminal_row.at("worker_claim_id").str()) &&
                           terminal_row.at("last_result_digest_sha256").str() == result_digest;
        if (terminal_ok) passed++;
        else { failed++; std::cerr << "outbox claim terminal row did not preserve worker claim evidence\n"; }
        pending_counts_ok(0, 1, 1);
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite effect outbox claim selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite effect outbox claim selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_effect_relay_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0635_effect_relay_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string downstream_path = "/tmp/" + stem + "_downstream.sqlite";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string key_path = "/tmp/" + stem + "_signer.pem";
    const std::string crash_report_path = "/tmp/" + stem + "_crash_report.json";
    const std::string early_report_path = "/tmp/" + stem + "_early_report.json";
    const std::string reconcile_report_path = "/tmp/" + stem + "_reconcile_report.json";
    const std::string pending_path = "/tmp/" + stem + "_pending.json";
    const std::string effect_key = sha256_hex("rev0635-relay-effect-a");
    const long long t0 = 1781750700LL;   // 2026-06-18T02:45:00Z
    const long long t_stale = 1781750761LL;
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, downstream_path, trust_path, key_path, crash_report_path, early_report_path, reconcile_report_path, pending_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-effect-relay-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-effect-relay-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-effect-relay-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto read_json = [](const std::string& path) { return parse_json_text(read_file(path)); };
    auto is_hex = [](const std::string& s) {
        if (s.size() != 64) return false;
        for (char c : s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
        return true;
    };
    auto pending_counts_ok = [&](long long reserved, long long inflight, long long terminal) {
        if (run_sqlite_effect_pending_report_command(ledger_path, pending_path) != 0) {
            failed++; std::cerr << "effect relay pending report command failed\n";
            return Json();
        }
        Json report = read_json(pending_path);
        bool ok = report.at("outbox_reserved_count").integer(-1) == reserved &&
                  report.at("outbox_inflight_count").integer(-1) == inflight &&
                  report.at("terminal_effect_count").integer(-1) == terminal &&
                  report.at("pending_effect_count").integer(-1) == reserved + inflight;
        if (ok) passed++;
        else { failed++; std::cerr << "effect relay pending counters mismatch\n"; }
        return report;
    };
    cleanup();
    try {
        auto root = make_selftest_restore_root("rev0635-effect-relay-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root, "2026-06-18T02:46:30Z", 600);
        write_file(trust_path, trust);
        write_file(key_path, private_key_pem_selftest(root.key.get()));
        const std::string trust_sha = sha256_hex(trust);
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            bool ok = backend->stage(make_tc("relay-case-a", effect_key), make_claims("relay-jti-a"), "allow", reason) && backend->commit(reason);
            if (ok) passed++; else { failed++; std::cerr << "effect relay seed failed: " << reason << "\n"; }
            backend->close();
        }
        pending_counts_ok(1, 0, 0);
        int crash_rc = run_sqlite_effect_relay_once_command(ledger_path,
                                                            downstream_path,
                                                            "relay-worker-A",
                                                            t0,
                                                            60,
                                                            "applied",
                                                            key_path,
                                                            root.kid,
                                                            trust_path,
                                                            trust_sha,
                                                            crash_report_path,
                                                            true);
        if (crash_rc == 75) passed++;
        else { failed++; std::cerr << "effect relay did not expose injected dispatch/terminal gap\n"; }
        Json crash = read_json(crash_report_path);
        const std::string result_digest = crash.at("downstream").at("result_digest_sha256").str();
        bool crash_ok = crash.at("format").str() == "anonsync-sqlite-effect-relay-report-v1" &&
                        crash.at("claimed").boolean(false) &&
                        crash.at("downstream_touched").boolean(false) &&
                        !crash.at("transition_closed").boolean(true) &&
                        crash.at("downstream").at("inserted").boolean(false) &&
                        !crash.at("downstream").at("replayed_existing").boolean(true) &&
                        is_hex(result_digest) &&
                        crash.at("claim").at("dispatch_attempts").integer(-1) == 1;
        if (crash_ok) passed++;
        else { failed++; std::cerr << "effect relay crash report did not show downstream-only apply\n"; }
        pending_counts_ok(0, 1, 0);
        int early_rc = run_sqlite_effect_relay_once_command(ledger_path,
                                                            downstream_path,
                                                            "relay-worker-B",
                                                            t0 + 30,
                                                            60,
                                                            "applied",
                                                            key_path,
                                                            root.kid,
                                                            trust_path,
                                                            trust_sha,
                                                            early_report_path,
                                                            false);
        if (early_rc == 0) passed++;
        else { failed++; std::cerr << "effect relay early no-work command failed\n"; }
        Json early = read_json(early_report_path);
        if (!early.at("claimed").boolean(true) && !early.at("downstream_touched").boolean(true) && !early.at("transition_closed").boolean(true)) passed++;
        else { failed++; std::cerr << "effect relay double-claimed fresh inflight lease\n"; }
        int reconcile_rc = run_sqlite_effect_relay_once_command(ledger_path,
                                                                downstream_path,
                                                                "relay-worker-C",
                                                                t_stale,
                                                                60,
                                                                "applied",
                                                                key_path,
                                                                root.kid,
                                                                trust_path,
                                                                trust_sha,
                                                                reconcile_report_path,
                                                                false);
        if (reconcile_rc == 0) passed++;
        else { failed++; std::cerr << "effect relay stale reconciliation command failed\n"; }
        Json reconcile = read_json(reconcile_report_path);
        bool reconcile_ok = reconcile.at("claimed").boolean(false) &&
                            reconcile.at("transition_authority_preflight_verified").boolean(false) &&
                            reconcile.at("downstream_touched").boolean(false) &&
                            reconcile.at("transition_closed").boolean(false) &&
                            reconcile.at("claim").at("previous_outbox_state").str() == "inflight" &&
                            reconcile.at("claim").at("dispatch_attempts").integer(-1) == 2 &&
                            reconcile.at("downstream").at("replayed_existing").boolean(false) &&
                            reconcile.at("downstream").at("observation_count").integer(-1) == 2 &&
                            reconcile.at("downstream").at("result_digest_sha256").str() == result_digest &&
                            is_hex(reconcile.at("transition").at("transition_intent_id").str()) &&
                            is_hex(reconcile.at("transition").at("transition_intent_sha256").str());
        if (reconcile_ok) passed++;
        else { failed++; std::cerr << "effect relay reconciliation report did not show idempotent downstream replay plus terminal close\n"; }
        pending_counts_ok(0, 0, 1);
        int after_terminal_rc = run_sqlite_effect_relay_once_command(ledger_path,
                                                                     downstream_path,
                                                                     "relay-worker-D",
                                                                     t_stale + 1,
                                                                     60,
                                                                     "applied",
                                                                     key_path,
                                                                     root.kid,
                                                                     trust_path,
                                                                     trust_sha,
                                                                     early_report_path,
                                                                     false);
        if (after_terminal_rc == 0 && !read_json(early_report_path).at("claimed").boolean(true)) passed++;
        else { failed++; std::cerr << "effect relay found work after terminal closure\n"; }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite effect relay selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite effect relay selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_effect_relay_configured_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0636_effect_relay_configured_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string downstream_path = "/tmp/" + stem + "_downstream.sqlite";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string key_path = "/tmp/" + stem + "_signer.pem";
    const std::string config_path = "/tmp/" + stem + "_adapter_config.json";
    const std::string crash_report_path = "/tmp/" + stem + "_crash_report.json";
    const std::string early_report_path = "/tmp/" + stem + "_early_report.json";
    const std::string reconcile_report_path = "/tmp/" + stem + "_reconcile_report.json";
    const std::string pending_path = "/tmp/" + stem + "_pending.json";
    const std::string effect_key = sha256_hex("rev0636-configured-relay-effect-a");
    const long long t0 = 1781751000LL;      // 2026-06-18T02:50:00Z
    const long long t_stale = 1781751061LL;
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, downstream_path, trust_path, key_path, config_path, crash_report_path, early_report_path, reconcile_report_path, pending_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-configured-relay-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-configured-relay-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-configured-relay-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto read_json = [](const std::string& path) { return parse_json_text(read_file(path)); };
    auto is_hex = [](const std::string& s) {
        if (s.size() != 64) return false;
        for (char c : s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
        return true;
    };
    auto pending_counts_ok = [&](long long reserved, long long inflight, long long terminal) {
        if (run_sqlite_effect_pending_report_command(ledger_path, pending_path) != 0) {
            failed++; std::cerr << "configured effect relay pending report command failed\n";
            return Json();
        }
        Json report = read_json(pending_path);
        bool ok = report.at("outbox_reserved_count").integer(-1) == reserved &&
                  report.at("outbox_inflight_count").integer(-1) == inflight &&
                  report.at("terminal_effect_count").integer(-1) == terminal &&
                  report.at("pending_effect_count").integer(-1) == reserved + inflight;
        if (ok) passed++;
        else { failed++; std::cerr << "configured effect relay pending counters mismatch\n"; }
        return report;
    };
    auto write_config = [&](const SelftestRestoreRoot& root, const std::string& trust_sha, bool allow_crash) {
        std::ostringstream cfg;
        cfg << "{\n"
            << "  \"format\": \"anonsync-effect-relay-adapter-config-v1\",\n"
            << "  \"revision_id\": \"rev0636-selftest\",\n"
            << "  \"adapter_id\": \"relay-configured-A\",\n"
            << "  \"adapter_kind\": \"local-sqlite-downstream-journal\",\n"
            << "  \"downstream_store_path\": \"" << json_escape(downstream_path) << "\",\n"
            << "  \"worker_id\": \"configured-worker-A\",\n"
            << "  \"lease_seconds\": 60,\n"
            << "  \"terminal_state\": \"applied\",\n"
            << "  \"signer_private_key_pem_path\": \"" << json_escape(key_path) << "\",\n"
            << "  \"signer_kid\": \"" << json_escape(root.kid) << "\",\n"
            << "  \"transition_trust_profile_path\": \"" << json_escape(trust_path) << "\",\n"
            << "  \"transition_trust_profile_sha256\": \"" << json_escape(trust_sha) << "\",\n"
            << "  \"debug_inject_crash_after_downstream_allowed\": " << (allow_crash ? "true" : "false") << ",\n"
            << "  \"blocked_claim\": \"selftest adapter config only; not external transport or HSM custody.\"\n"
            << "}\n";
        const std::string text = cfg.str();
        write_file(config_path, text);
        return sha256_hex(text);
    };
    cleanup();
    try {
        auto root = make_selftest_restore_root("rev0636-effect-relay-configured-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root, "2026-06-18T02:51:30Z", 600);
        write_file(trust_path, trust);
        write_file(key_path, private_key_pem_selftest(root.key.get()));
        const std::string trust_sha = sha256_hex(trust);
        const std::string config_sha = write_config(root, trust_sha, true);
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            bool ok = backend->stage(make_tc("configured-relay-case-a", effect_key), make_claims("configured-relay-jti-a"), "allow", reason) && backend->commit(reason);
            if (ok) passed++; else { failed++; std::cerr << "configured effect relay seed failed: " << reason << "\n"; }
            backend->close();
        }
        pending_counts_ok(1, 0, 0);
        int crash_rc = run_sqlite_effect_relay_configured_once_command(ledger_path,
                                                                       config_path,
                                                                       config_sha,
                                                                       t0,
                                                                       crash_report_path,
                                                                       true);
        if (crash_rc == 75) passed++;
        else { failed++; std::cerr << "configured effect relay did not expose injected gap\n"; }
        Json crash = read_json(crash_report_path);
        const std::string result_digest = crash.at("downstream").at("result_digest_sha256").str();
        bool crash_ok = crash.at("format").str() == "anonsync-sqlite-effect-relay-report-v2-configured-boundary" &&
                        crash.at("revision_id").str() == "rev0636" &&
                        crash.at("relay_adapter_config").at("format").str() == "anonsync-effect-relay-adapter-config-v1" &&
                        crash.at("relay_adapter_config").at("adapter_id").str() == "relay-configured-A" &&
                        crash.at("relay_adapter_config").at("adapter_kind").str() == "local-sqlite-downstream-journal" &&
                        crash.at("relay_adapter_config").at("config_sha256").str() == config_sha &&
                        crash.at("relay_adapter_config").at("digest_pin_verified").boolean(false) &&
                        crash.at("claimed").boolean(false) &&
                        crash.at("downstream_touched").boolean(false) &&
                        !crash.at("transition_closed").boolean(true) &&
                        crash.at("downstream").at("inserted").boolean(false) &&
                        is_hex(result_digest);
        if (crash_ok) passed++;
        else { failed++; std::cerr << "configured effect relay crash report did not bind config identity\n"; }
        pending_counts_ok(0, 1, 0);
        int early_rc = run_sqlite_effect_relay_configured_once_command(ledger_path, config_path, config_sha, t0 + 30, early_report_path, false);
        if (early_rc == 0 && !read_json(early_report_path).at("claimed").boolean(true)) passed++;
        else { failed++; std::cerr << "configured effect relay double-claimed a fresh lease\n"; }
        int reconcile_rc = run_sqlite_effect_relay_configured_once_command(ledger_path, config_path, config_sha, t_stale, reconcile_report_path, false);
        if (reconcile_rc == 0) passed++;
        else { failed++; std::cerr << "configured effect relay stale reconciliation command failed\n"; }
        Json reconcile = read_json(reconcile_report_path);
        bool reconcile_ok = reconcile.at("claimed").boolean(false) &&
                            reconcile.at("transition_authority_preflight_verified").boolean(false) &&
                            reconcile.at("downstream_touched").boolean(false) &&
                            reconcile.at("transition_closed").boolean(false) &&
                            reconcile.at("claim").at("previous_outbox_state").str() == "inflight" &&
                            reconcile.at("downstream").at("replayed_existing").boolean(false) &&
                            reconcile.at("downstream").at("result_digest_sha256").str() == result_digest &&
                            reconcile.at("transition").at("transition_reason").str().find(config_sha) != std::string::npos &&
                            is_hex(reconcile.at("transition").at("transition_intent_id").str()) &&
                            is_hex(reconcile.at("transition").at("transition_intent_sha256").str());
        if (reconcile_ok) passed++;
        else { failed++; std::cerr << "configured effect relay reconciliation did not use config-bound signed terminal evidence\n"; }
        pending_counts_ok(0, 0, 1);
        write_file(config_path, read_file(config_path) + "\n");
        int tamper_rc = run_sqlite_effect_relay_configured_once_command(ledger_path, config_path, config_sha, t_stale + 2, early_report_path, false);
        if (tamper_rc != 0) passed++;
        else { failed++; std::cerr << "configured effect relay accepted adapter config after digest-pin tamper\n"; }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite configured effect relay selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite configured effect relay selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_effect_relay_handle_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0637_effect_relay_handle_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string ledger_path = "/tmp/" + stem + ".sqlite";
    const std::string downstream_path = "/tmp/" + stem + "_downstream.sqlite";
    const std::string trust_path = "/tmp/" + stem + "_trust.json";
    const std::string key_path = "/tmp/" + stem + "_signer.pem";
    const std::string config_path = "/tmp/" + stem + "_adapter_config.json";
    const std::string registry_path = "/tmp/" + stem + "_adapter_registry.json";
    const std::string crash_report_path = "/tmp/" + stem + "_crash_report.json";
    const std::string early_report_path = "/tmp/" + stem + "_early_report.json";
    const std::string reconcile_report_path = "/tmp/" + stem + "_reconcile_report.json";
    const std::string pending_path = "/tmp/" + stem + "_pending.json";
    const std::string effect_key = sha256_hex("rev0637-handle-relay-effect-a");
    const std::string handle = "payments.primary";
    const long long t0 = 1781751300LL;      // 2026-06-18T02:55:00Z
    const long long t_stale = 1781751361LL;
    auto cleanup = [&]() {
        for (const auto& p : {ledger_path, downstream_path, trust_path, key_path, config_path, registry_path, crash_report_path, early_report_path, reconcile_report_path, pending_path}) {
            std::remove(p.c_str());
            std::remove((p + "-wal").c_str());
            std::remove((p + "-shm").c_str());
            std::remove((p + ".write.lock").c_str());
        }
    };
    auto make_tc = [&](const std::string& case_id, const std::string& effect) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("selftest-handle-relay-op");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        tc.o["effect_idempotency_key"] = json_string_value(effect);
        tc.o["effect_state"] = json_string_value("prepared");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-handle-relay-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-handle-relay-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto read_json = [](const std::string& path) { return parse_json_text(read_file(path)); };
    auto is_hex = [](const std::string& s) {
        if (s.size() != 64) return false;
        for (char c : s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
        return true;
    };
    auto pending_counts_ok = [&](long long reserved, long long inflight, long long terminal) {
        if (run_sqlite_effect_pending_report_command(ledger_path, pending_path) != 0) {
            failed++; std::cerr << "handle-bound effect relay pending report command failed\n";
            return Json();
        }
        Json report = read_json(pending_path);
        bool ok = report.at("outbox_reserved_count").integer(-1) == reserved &&
                  report.at("outbox_inflight_count").integer(-1) == inflight &&
                  report.at("terminal_effect_count").integer(-1) == terminal &&
                  report.at("pending_effect_count").integer(-1) == reserved + inflight;
        if (ok) passed++;
        else { failed++; std::cerr << "handle-bound effect relay pending counters mismatch\n"; }
        return report;
    };
    auto write_config = [&](const SelftestRestoreRoot& root, const std::string& trust_sha, bool allow_crash) {
        std::ostringstream cfg;
        cfg << "{\n"
            << "  \"format\": \"anonsync-effect-relay-adapter-config-v1\",\n"
            << "  \"revision_id\": \"rev0637-selftest\",\n"
            << "  \"adapter_id\": \"relay-handle-A\",\n"
            << "  \"adapter_kind\": \"local-sqlite-downstream-journal\",\n"
            << "  \"downstream_store_path\": \"" << json_escape(downstream_path) << "\",\n"
            << "  \"worker_id\": \"handle-worker-A\",\n"
            << "  \"lease_seconds\": 60,\n"
            << "  \"terminal_state\": \"applied\",\n"
            << "  \"signer_private_key_pem_path\": \"" << json_escape(key_path) << "\",\n"
            << "  \"signer_kid\": \"" << json_escape(root.kid) << "\",\n"
            << "  \"transition_trust_profile_path\": \"" << json_escape(trust_path) << "\",\n"
            << "  \"transition_trust_profile_sha256\": \"" << json_escape(trust_sha) << "\",\n"
            << "  \"debug_inject_crash_after_downstream_allowed\": " << (allow_crash ? "true" : "false") << ",\n"
            << "  \"blocked_claim\": \"selftest adapter config only; resolved by registry handle, not caller-selected paths.\"\n"
            << "}\n";
        const std::string text = cfg.str();
        write_file(config_path, text);
        return sha256_hex(text);
    };
    auto write_registry = [&](const std::string& config_sha, const std::string& selected_handle, bool enabled, bool duplicate) {
        std::ostringstream reg;
        reg << "{\n"
            << "  \"format\": \"anonsync-effect-relay-config-registry-v1\",\n"
            << "  \"revision_id\": \"rev0637-selftest\",\n"
            << "  \"entries\": [\n"
            << "    {\n"
            << "      \"handle\": \"" << json_escape(selected_handle) << "\",\n"
            << "      \"enabled\": " << (enabled ? "true" : "false") << ",\n"
            << "      \"adapter_id\": \"relay-handle-A\",\n"
            << "      \"adapter_kind\": \"local-sqlite-downstream-journal\",\n"
            << "      \"adapter_config_path\": \"" << json_escape(config_path) << "\",\n"
            << "      \"adapter_config_sha256\": \"" << json_escape(config_sha) << "\"\n"
            << "    }";
        if (duplicate) {
            reg << ",\n    {\n"
                << "      \"handle\": \"" << json_escape(selected_handle) << "\",\n"
                << "      \"enabled\": true,\n"
                << "      \"adapter_config_path\": \"" << json_escape(config_path) << "\",\n"
                << "      \"adapter_config_sha256\": \"" << json_escape(config_sha) << "\"\n"
                << "    }";
        }
        reg << "\n  ],\n"
            << "  \"blocked_claim\": \"operator registry selftest only; not signed control plane.\"\n"
            << "}\n";
        const std::string text = reg.str();
        write_file(registry_path, text);
        return sha256_hex(text);
    };
    cleanup();
    try {
        auto root = make_selftest_restore_root("rev0637-effect-relay-handle-root");
        const std::string trust = make_effect_transition_trust_profile_v1_selftest(root, "2026-06-18T02:56:30Z", 600);
        write_file(trust_path, trust);
        write_file(key_path, private_key_pem_selftest(root.key.get()));
        const std::string trust_sha = sha256_hex(trust);
        const std::string config_sha = write_config(root, trust_sha, true);
        std::string registry_sha = write_registry(config_sha, handle, true, false);
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(ledger_path, true, "batch");
            std::string reason;
            bool ok = backend->stage(make_tc("handle-relay-case-a", effect_key), make_claims("handle-relay-jti-a"), "allow", reason) && backend->commit(reason);
            if (ok) passed++; else { failed++; std::cerr << "handle-bound effect relay seed failed: " << reason << "\n"; }
            backend->close();
        }
        pending_counts_ok(1, 0, 0);
        int mismatch_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, std::string(64, '0'), handle, t0, early_report_path, false);
        if (mismatch_rc != 0) passed++;
        else { failed++; std::cerr << "handle-bound effect relay accepted registry digest mismatch before claim\n"; }
        pending_counts_ok(1, 0, 0);
        int crash_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t0, crash_report_path, true);
        if (crash_rc == 75) passed++;
        else { failed++; std::cerr << "handle-bound effect relay did not expose injected gap\n"; }
        Json crash = read_json(crash_report_path);
        const std::string result_digest = crash.at("downstream").at("result_digest_sha256").str();
        bool crash_ok = crash.at("format").str() == "anonsync-sqlite-effect-relay-report-v3-handle-boundary" &&
                        crash.at("revision_id").str() == "rev0648" &&
                        crash.at("transition_authority_preflight_verified").boolean(false) &&
                        crash.at("relay_config_registry").at("format").str() == "anonsync-effect-relay-config-registry-v1" &&
                        crash.at("relay_config_registry").at("config_handle").str() == handle &&
                        crash.at("relay_config_registry").at("registry_sha256").str() == registry_sha &&
                        crash.at("relay_config_registry").at("digest_pin_verified").boolean(false) &&
                        crash.at("relay_adapter_config").at("config_sha256").str() == config_sha &&
                        crash.at("relay_adapter_config").at("adapter_id").str() == "relay-handle-A" &&
                        crash.at("claimed").boolean(false) &&
                        crash.at("downstream_touched").boolean(false) &&
                        !crash.at("transition_closed").boolean(true) &&
                        is_hex(result_digest);
        if (crash_ok) passed++;
        else { failed++; std::cerr << "handle-bound effect relay crash report did not bind registry handle and adapter config\n"; }
        pending_counts_ok(0, 1, 0);
        int early_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t0 + 30, early_report_path, false);
        if (early_rc == 0 && !read_json(early_report_path).at("claimed").boolean(true)) passed++;
        else { failed++; std::cerr << "handle-bound effect relay double-claimed a fresh lease\n"; }
        int reconcile_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t_stale, reconcile_report_path, false);
        if (reconcile_rc == 0) passed++;
        else { failed++; std::cerr << "handle-bound effect relay stale reconciliation command failed\n"; }
        Json reconcile = read_json(reconcile_report_path);
        bool reconcile_ok = reconcile.at("claimed").boolean(false) &&
                            reconcile.at("transition_authority_preflight_verified").boolean(false) &&
                            reconcile.at("downstream_touched").boolean(false) &&
                            reconcile.at("transition_closed").boolean(false) &&
                            reconcile.at("claim").at("previous_outbox_state").str() == "inflight" &&
                            reconcile.at("downstream").at("replayed_existing").boolean(false) &&
                            reconcile.at("downstream").at("result_digest_sha256").str() == result_digest &&
                            reconcile.at("transition").at("transition_reason").str().find(handle) != std::string::npos &&
                            reconcile.at("transition").at("transition_reason").str().find(registry_sha) != std::string::npos &&
                            is_hex(reconcile.at("transition").at("transition_intent_id").str()) &&
                            is_hex(reconcile.at("transition").at("transition_intent_sha256").str());
        if (reconcile_ok) passed++;
        else { failed++; std::cerr << "handle-bound effect relay reconciliation did not use registry-handle signed terminal evidence\n"; }
        pending_counts_ok(0, 0, 1);
        write_file(registry_path, read_file(registry_path) + "\n");
        int tamper_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t_stale + 2, early_report_path, false);
        if (tamper_rc != 0) passed++;
        else { failed++; std::cerr << "handle-bound effect relay accepted registry after digest-pin tamper\n"; }
        registry_sha = write_registry(config_sha, handle, false, false);
        int disabled_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t_stale + 3, early_report_path, false);
        if (disabled_rc != 0) passed++;
        else { failed++; std::cerr << "handle-bound effect relay accepted disabled registry handle\n"; }
        registry_sha = write_registry(config_sha, handle, true, true);
        int duplicate_rc = run_sqlite_effect_relay_handle_once_command(ledger_path, registry_path, registry_sha, handle, t_stale + 4, early_report_path, false);
        if (duplicate_rc != 0) passed++;
        else { failed++; std::cerr << "handle-bound effect relay accepted duplicate registry handle\n"; }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite handle-bound effect relay selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite handle-bound effect relay selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_event_identity_replay_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0623_event_identity_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string jsonl_path = "/tmp/" + stem + ".jsonl";
    const std::string sqlite_path = "/tmp/" + stem + ".sqlite";
    auto cleanup = [&]() {
        std::remove(jsonl_path.c_str());
        std::remove((jsonl_path + ".journal").c_str());
        std::remove((jsonl_path + ".lock").c_str());
        std::remove(sqlite_path.c_str());
        std::remove((sqlite_path + "-wal").c_str());
        std::remove((sqlite_path + "-shm").c_str());
        std::remove((sqlite_path + ".write.lock").c_str());
    };
    auto make_event_tc = [](const std::string& case_id, const std::string& source, const std::string& event_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("asyncapi");
        tc.o["operation_id"] = json_string_value("selftest-event-op");
        tc.o["cloud_event_source"] = json_string_value(source);
        tc.o["cloud_event_id"] = json_string_value(event_id);
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("selftest-event-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("selftest-event-contract"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto exercise_backend = [&](const std::string& backend_name, const std::string& path) {
        try {
            auto backend = create_replay_ledger_backend(backend_name);
            backend->load(path, true, "batch");
            std::string reason;
            const Json first = make_event_tc(backend_name + "-event-a", "urn:anonsync:selftest:source", "ce-rev0623-duplicate-event");
            const Json dup = make_event_tc(backend_name + "-event-b", "urn:anonsync:selftest:source", "ce-rev0623-duplicate-event");
            if (backend->stage(first, make_claims(backend_name + "-jti-a"), "accept", reason) && backend->contains_event_identity("urn:anonsync:selftest:source", "ce-rev0623-duplicate-event")) passed++;
            else { failed++; std::cerr << backend_name << " did not stage/publish event identity: " << reason << "\n"; }
            if (!backend->stage(dup, make_claims(backend_name + "-jti-b"), "accept", reason) && reason.find("CloudEvents source/id") != std::string::npos) passed++;
            else { failed++; std::cerr << backend_name << " did not reject duplicate staged event identity: " << reason << "\n"; }
            if (backend->commit(reason)) passed++;
            else { failed++; std::cerr << backend_name << " event identity commit failed: " << reason << "\n"; }
            backend->close();
            auto reload = create_replay_ledger_backend(backend_name);
            reload->load(path, false, "batch");
            if (reload->contains_event_identity("urn:anonsync:selftest:source", "ce-rev0623-duplicate-event")) passed++;
            else { failed++; std::cerr << backend_name << " reload lost event identity index\n"; }
            const Json dup_after_reload = make_event_tc(backend_name + "-event-c", "urn:anonsync:selftest:source", "ce-rev0623-duplicate-event");
            if (!reload->stage(dup_after_reload, make_claims(backend_name + "-jti-c"), "accept", reason) && reason.find("CloudEvents source/id") != std::string::npos) passed++;
            else { failed++; std::cerr << backend_name << " did not reject duplicate event identity after reload: " << reason << "\n"; }
            reload->close();
        } catch (const std::exception& e) {
            failed++;
            std::cerr << backend_name << " event identity replay selftest exception: " << e.what() << "\n";
        }
    };
    cleanup();
    exercise_backend("local-jsonl", jsonl_path);
    exercise_backend("sqlite-wal", sqlite_path);
    cleanup();
    std::cout << "anonsync_core ledger event identity replay selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_wal_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0601_sqlite_wal_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    auto cleanup = [&]() {
        std::remove(base.c_str());
        std::remove((base + "-wal").c_str());
        std::remove((base + "-shm").c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("untrusted-normalized-operation");
        // Deliberately omit contract_digest_sha256. The backend must not source
        // security identity from the normalized case after JWT verification.
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    try {
        cleanup();
        try { (void)create_replay_ledger_backend("not-a-backend"); failed++; std::cerr << "sqlite-wal selftest accepted unsupported backend name\n"; }
        catch (...) { passed++; }
        {
            auto local = create_replay_ledger_backend("local-jsonl");
            if (local->backend_name() == "local-jsonl") passed++; else { failed++; std::cerr << "factory did not return local-jsonl backend\n"; }
        }
        {
            auto sqlite = create_replay_ledger_backend("sqlite-wal");
            if (sqlite->backend_name() == "sqlite-wal") passed++; else { failed++; std::cerr << "factory did not return sqlite-wal backend\n"; }
        }
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(base, true, "batch");
            std::string reason;
            if (backend->stage(make_tc("sqlite-case-a"), make_claims("sqlite-jti-a"), "allow", reason) && backend->contains_jti("sqlite-jti-a")) passed++;
            else { failed++; std::cerr << "sqlite-wal stage did not publish staged jti: " << reason << "\n"; }
            if (!backend->stage(make_tc("sqlite-case-dup"), make_claims("sqlite-jti-a"), "allow", reason) && reason.find("durable replay ledger") != std::string::npos) passed++;
            else { failed++; std::cerr << "sqlite-wal did not reject staged duplicate jti: " << reason << "\n"; }
            if (backend->stage(make_tc("sqlite-case-b"), make_claims("sqlite-jti-b"), "allow", reason) && backend->commit(reason)) passed++;
            else { failed++; std::cerr << "sqlite-wal batch commit failed: " << reason << "\n"; }
            ReplayLedgerStats st = backend->stats();
            if (st.sqlite_transactions == 1 && st.sqlite_wal_checkpoints == 1 && st.batch_flush_commits == 1 && st.batch_pending_entries_peak >= 2) passed++;
            else { failed++; std::cerr << "sqlite-wal stats unexpected transactions=" << st.sqlite_transactions << " checkpoints=" << st.sqlite_wal_checkpoints << " batch=" << st.batch_flush_commits << " peak=" << st.batch_pending_entries_peak << "\n"; }
            backend->close();
        }
        {
            auto reload = create_replay_ledger_backend("sqlite-wal");
            reload->load(base, false, "batch");
            ReplayLedgerStats st = reload->stats();
            if (st.loaded_entries == 2 && reload->contains_jti("sqlite-jti-a") && reload->contains_jti("sqlite-jti-b")) passed++;
            else { failed++; std::cerr << "sqlite-wal reload lost committed jtis loaded=" << st.loaded_entries << "\n"; }
            reload->close();
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(base.c_str(), &raw, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "sqlite-wal selftest could not inspect persisted verified claims\n";
                if (raw) sqlite3_close(raw);
            } else {
                sqlite3_stmt* stmt = nullptr;
                const char* sql = "SELECT COUNT(*), SUM(CASE WHEN operation_id=?1 AND contract_digest_sha256=?2 THEN 1 ELSE 0 END) FROM ledger_entries;";
                if (sqlite3_prepare_v2(raw, sql, -1, &stmt, nullptr) != SQLITE_OK) {
                    failed++; std::cerr << "sqlite-wal selftest persisted binding query prepare failed\n";
                } else {
                    sqlite3_bind_text(stmt, 1, "sqlite-op", -1, SQLITE_STATIC);
                    const std::string expected_digest = sha256_hex("sqlite-digest");
                    sqlite3_bind_text(stmt, 2, expected_digest.c_str(), -1, SQLITE_TRANSIENT);
                    if (sqlite3_step(stmt) == SQLITE_ROW && sqlite3_column_int64(stmt, 0) == 2 && sqlite3_column_int64(stmt, 1) == 2) passed++;
                    else { failed++; std::cerr << "sqlite-wal persisted rows were not bound to verified claims\n"; }
                }
                if (stmt) sqlite3_finalize(stmt);
                sqlite3_close(raw);
            }
        }
        {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(base, false, "batch");
            std::string reason;
            Json invalid_claims = make_claims("sqlite-jti-invalid-digest");
            invalid_claims.o["contract_digest_sha256"] = json_string_value("");
            if (!backend->stage(make_tc("sqlite-case-invalid-digest"), invalid_claims, "allow", reason) && reason.find("contract_digest_sha256") != std::string::npos) passed++;
            else { failed++; std::cerr << "sqlite-wal accepted empty verified contract digest: " << reason << "\n"; }
            backend->close();
        }
        {
            auto immediate = create_replay_ledger_backend("sqlite-wal");
            immediate->load(base, false, "immediate");
            std::string reason;
            if (!immediate->stage(make_tc("sqlite-case-replay"), make_claims("sqlite-jti-a"), "allow", reason) && reason.find("durable replay ledger") != std::string::npos) passed++;
            else { failed++; std::cerr << "sqlite-wal immediate mode did not reject committed replay: " << reason << "\n"; }
            immediate->close();
        }
        {
            sqlite3* db = nullptr;
            if (sqlite3_open_v2(base.c_str(), &db, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "sqlite-wal selftest could not open database for metadata tamper\n";
            } else {
                char* err = nullptr;
                int rc = sqlite3_exec(db, "UPDATE metadata SET head_hash='tampered-head' WHERE id=1;", nullptr, nullptr, &err);
                if (rc != SQLITE_OK) { failed++; std::cerr << "sqlite-wal metadata tamper exec failed: " << (err ? err : "") << "\n"; sqlite3_free(err); }
                else {
                    try { auto bad = create_replay_ledger_backend("sqlite-wal"); bad->load(base, false, "batch"); failed++; std::cerr << "sqlite-wal accepted metadata/head tamper\n"; }
                    catch (...) { passed++; }
                }
                sqlite3_close(db);
            }
        }
        {
            auto reset = create_replay_ledger_backend("sqlite-wal");
            reset->load(base, true, "batch");
            ReplayLedgerStats st = reset->stats();
            if (st.loaded_entries == 0 && !reset->contains_jti("sqlite-jti-a")) passed++;
            else { failed++; std::cerr << "sqlite-wal reset did not clear prior rows\n"; }
            reset->close();
        }
        cleanup();
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite-wal selftest exception: " << e.what() << "\n";
        cleanup();
    }
    std::cout << "anonsync_core ledger sqlite-wal selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_hardening_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0602_sqlite_hardening_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string root = "/tmp/" + stem;
    auto base_path = [&](const std::string& label) { return root + "_" + label + ".sqlite"; };
    auto cleanup = [&](const std::string& base) {
        std::remove(base.c_str());
        std::remove((base + "-wal").c_str());
        std::remove((base + "-shm").c_str());
        std::remove((base + ".target").c_str());
        std::remove((base + "-wal.target").c_str());
        std::remove((base + "-shm.target").c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-hardening-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-hardening-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-hardening-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-hardening-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto raw_exec = [&](const std::string& base, const std::string& sql) {
        sqlite3* db = nullptr;
        if (sqlite3_open_v2(base.c_str(), &db, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
            std::string msg = db ? sqlite3_errmsg(db) : "sqlite open failed";
            if (db) sqlite3_close(db);
            throw std::runtime_error("sqlite hardening raw open failed: " + msg);
        }
        char* err = nullptr;
        int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err);
        std::string msg = err ? err : "";
        if (err) sqlite3_free(err);
        sqlite3_close(db);
        if (rc != SQLITE_OK) throw std::runtime_error("sqlite hardening raw exec failed: " + msg + " sql=" + sql);
    };
    auto seed_two = [&](const std::string& base) {
        cleanup(base);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        std::string reason;
        if (!backend->stage(make_tc("case-a"), make_claims("jti-a"), "allow", reason)) throw std::runtime_error("seed stage a failed: " + reason);
        if (!backend->stage(make_tc("case-b"), make_claims("jti-b"), "allow", reason)) throw std::runtime_error("seed stage b failed: " + reason);
        if (!backend->commit(reason)) throw std::runtime_error("seed commit failed: " + reason);
        backend->close();
    };
    auto expect_load_reject = [&](const std::string& base, const std::string& label) {
        try {
            auto bad = create_replay_ledger_backend("sqlite-wal");
            bad->load(base, false, "batch");
            failed++;
            std::cerr << "sqlite hardening accepted hostile ledger case " << label << "\n";
        } catch (const std::exception&) {
            passed++;
        }
        cleanup(base);
    };
    try {
        {
            const std::string base = base_path("profile_stats");
            seed_two(base);
            auto reload = create_replay_ledger_backend("sqlite-wal");
            reload->load(base, false, "batch");
            ReplayLedgerStats st = reload->stats();
            if (st.loaded_entries == 2 && st.sqlite_integrity_checks >= 1 && st.sqlite_profile_checks >= 1 && reload->contains_jti("jti-a") && reload->contains_jti("jti-b")) passed++;
            else { failed++; std::cerr << "sqlite hardening profile/integrity stats mismatch loaded=" << st.loaded_entries << " integrity=" << st.sqlite_integrity_checks << " profile=" << st.sqlite_profile_checks << "\n"; }
            reload->close();
            cleanup(base);
        }
        {
            const std::string base = base_path("bad_profile");
            seed_two(base);
            raw_exec(base, "DROP TABLE backend_profile; CREATE TABLE backend_profile(id INTEGER PRIMARY KEY, backend_name TEXT, schema_version INTEGER, hash_algorithm TEXT, entry_material_version TEXT, commit_protocol TEXT); INSERT INTO backend_profile VALUES(1,'evil-backend',2,'sha256','anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent','sqlite-wal-begin-immediate-full-sync');");
            expect_load_reject(base, "backend-profile-mismatch");
        }
        {
            const std::string base = base_path("metadata_rollback");
            seed_two(base);
            raw_exec(base, "UPDATE metadata SET line_count=1 WHERE id=1;");
            expect_load_reject(base, "metadata-rollback");
        }
        {
            const std::string base = base_path("entry_hash_tamper");
            seed_two(base);
            raw_exec(base, "UPDATE ledger_entries SET entry_hash='0000000000000000000000000000000000000000000000000000000000000000' WHERE sequence=1;");
            expect_load_reject(base, "entry-hash-tamper");
        }
        {
            const std::string base = base_path("previous_hash_tamper");
            seed_two(base);
            raw_exec(base, "UPDATE ledger_entries SET previous_hash='GENESIS' WHERE sequence=2;");
            expect_load_reject(base, "previous-hash-tamper");
        }
        {
            const std::string base = base_path("sequence_gap");
            seed_two(base);
            raw_exec(base, "UPDATE ledger_entries SET sequence=5 WHERE sequence=2;");
            expect_load_reject(base, "sequence-gap");
        }
        {
            const std::string base = base_path("garbage_file");
            cleanup(base);
            write_file(base, "not a sqlite database");
            expect_load_reject(base, "garbage-file");
        }
        {
            const std::string base = base_path("ledger_symlink");
            cleanup(base);
            const std::string target = base + ".target";
            write_file(target, "");
            if (::symlink(target.c_str(), base.c_str()) != 0) { failed++; std::cerr << "sqlite hardening could not create ledger symlink\n"; cleanup(base); }
            else expect_load_reject(base, "ledger-symlink");
        }
        {
            const std::string base = base_path("wal_symlink");
            cleanup(base);
            write_file(base, "");
            const std::string target = base + "-wal.target";
            write_file(target, "");
            if (::symlink(target.c_str(), (base + "-wal").c_str()) != 0) { failed++; std::cerr << "sqlite hardening could not create WAL symlink\n"; cleanup(base); }
            else expect_load_reject(base, "wal-symlink");
        }
        {
            const std::string base = base_path("shm_symlink");
            cleanup(base);
            write_file(base, "");
            const std::string target = base + "-shm.target";
            write_file(target, "");
            if (::symlink(target.c_str(), (base + "-shm").c_str()) != 0) { failed++; std::cerr << "sqlite hardening could not create SHM symlink\n"; cleanup(base); }
            else expect_load_reject(base, "shm-symlink");
        }
        {
            const std::string base = base_path("writer_contention");
            seed_two(base);
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(base.c_str(), &raw, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "sqlite hardening could not open raw writer contention connection\n";
                if (raw) sqlite3_close(raw);
                cleanup(base);
            } else {
                char* err = nullptr;
                int rc = sqlite3_exec(raw, "BEGIN IMMEDIATE;", nullptr, nullptr, &err);
                if (rc != SQLITE_OK) {
                    failed++; std::cerr << "sqlite hardening could not acquire raw BEGIN IMMEDIATE lock: " << (err ? err : "") << "\n";
                    if (err) sqlite3_free(err);
                    sqlite3_close(raw);
                    cleanup(base);
                } else {
                    auto contended = create_replay_ledger_backend("sqlite-wal");
                    std::string reason;
                    bool rejected = false;
                    try {
                        contended->load(base, false, "batch");
                        if (!contended->stage(make_tc("case-c"), make_claims("jti-c"), "allow", reason)) rejected = true;
                        else if (!contended->commit(reason)) rejected = true;
                    } catch (const std::exception&) {
                        rejected = true;
                    }
                    if (rejected) passed++; else { failed++; std::cerr << "sqlite hardening did not reject writer contention\n"; }
                    sqlite3_exec(raw, "ROLLBACK;", nullptr, nullptr, nullptr);
                    sqlite3_close(raw);
                    cleanup(base);
                }
            }
        }
        {
            const std::string base = base_path("unsupported_mode");
            cleanup(base);
            try { auto bad = create_replay_ledger_backend("sqlite-wal"); bad->load(base, true, "unsafe"); failed++; std::cerr << "sqlite hardening accepted unsupported commit mode\n"; }
            catch (...) { passed++; }
            cleanup(base);
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite hardening selftest exception: " << e.what() << "\n";
    }
    std::cout << "anonsync_core ledger sqlite hardening selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_backend_capabilities_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string good_manifest = R"JSON({
  "format": "anonsync-ledger-backend-capabilities-v1",
  "revision_id": "rev0603",
  "backends": {
    "sqlite-wal": {
      "backend_name": "sqlite-wal",
      "status": "supported",
      "commit_modes": ["immediate", "batch"],
      "requires_nonempty_ledger_path": true,
      "requires_sqlite_wal": true,
      "integrity_check_on_load": true,
      "profile_check_on_load": true,
      "reject_symlink_sidecars": true,
      "durability_ceiling": "local SQLite/WAL only; not distributed or tamper-proof"
    },
    "local-jsonl": {
      "backend_name": "local-jsonl",
      "status": "supported",
      "commit_modes": ["immediate", "batch"],
      "requires_nonempty_ledger_path": true,
      "journal_v2_only": true,
      "reject_symlink_sidecars": true,
      "durability_ceiling": "local JSONL only; not distributed or tamper-proof"
    }
  }
})JSON";
    auto expect_ok = [&](const std::string& label, const std::string& text, const std::string& backend, const std::string& mode, const std::string& path) {
        try {
            std::string digest = validate_replay_backend_capability_manifest(text, backend, mode, path);
            if (digest.size() == 64) passed++;
            else { failed++; std::cerr << "backend capability selftest digest length mismatch " << label << "\n"; }
        } catch (const std::exception& e) {
            failed++; std::cerr << "backend capability selftest expected accept but rejected " << label << ": " << e.what() << "\n";
        }
    };
    auto expect_throw = [&](const std::string& label, const std::string& text, const std::string& backend, const std::string& mode, const std::string& path) {
        try {
            (void)validate_replay_backend_capability_manifest(text, backend, mode, path);
            failed++; std::cerr << "backend capability selftest expected rejection but accepted " << label << "\n";
        } catch (...) { passed++; }
    };
    expect_ok("sqlite-batch", good_manifest, "sqlite-wal", "batch", "/tmp/anonsync-cap.sqlite");
    expect_ok("local-immediate", good_manifest, "local-jsonl", "immediate", "/tmp/anonsync-cap.jsonl");
    expect_throw("unknown-backend", good_manifest, "not-a-backend", "batch", "/tmp/anonsync-cap.sqlite");
    expect_throw("unsupported-commit-mode", good_manifest, "sqlite-wal", "unsafe", "/tmp/anonsync-cap.sqlite");
    expect_throw("empty-ledger-path", good_manifest, "sqlite-wal", "batch", "");
    std::string bad_format = good_manifest;
    size_t pos = bad_format.find("anonsync-ledger-backend-capabilities-v1");
    bad_format.replace(pos, std::string("anonsync-ledger-backend-capabilities-v1").size(), "wrong-format");
    expect_throw("bad-format", bad_format, "sqlite-wal", "batch", "/tmp/anonsync-cap.sqlite");
    std::string trailing_version = good_manifest;
    pos = trailing_version.find("anonsync-ledger-backend-capabilities-v1");
    trailing_version.replace(pos, std::string("anonsync-ledger-backend-capabilities-v1").size(), "anonsync-ledger-backend-capabilities-v1junk");
    expect_throw("trailing-version-text", trailing_version, "sqlite-wal", "batch", "/tmp/anonsync-cap.sqlite");
    std::string missing_integrity = good_manifest;
    pos = missing_integrity.find("\"integrity_check_on_load\": true");
    missing_integrity.replace(pos, std::string("\"integrity_check_on_load\": true").size(), "\"integrity_check_on_load\": false");
    expect_throw("missing-integrity-requirement", missing_integrity, "sqlite-wal", "batch", "/tmp/anonsync-cap.sqlite");
    std::string missing_journal_v2 = good_manifest;
    pos = missing_journal_v2.find("\"journal_v2_only\": true");
    missing_journal_v2.replace(pos, std::string("\"journal_v2_only\": true").size(), "\"journal_v2_only\": false");
    expect_throw("missing-journal-v2-requirement", missing_journal_v2, "local-jsonl", "batch", "/tmp/anonsync-cap.jsonl");
    std::string missing_local_ceiling = good_manifest;
    pos = missing_local_ceiling.find("local SQLite/WAL only");
    missing_local_ceiling.replace(pos, std::string("local SQLite/WAL only").size(), "distributed miracle");
    expect_throw("missing-local-storage-ceiling", missing_local_ceiling, "sqlite-wal", "batch", "/tmp/anonsync-cap.sqlite");
    std::cout << "anonsync_core ledger backend capabilities selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_crash_corpus_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0603_sqlite_crash_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string root = "/tmp/" + stem;
    auto base_path = [&](const std::string& label) { return root + "_" + label + ".sqlite"; };
    auto cleanup = [&](const std::string& base) {
        std::remove(base.c_str());
        std::remove((base + "-wal").c_str());
        std::remove((base + "-shm").c_str());
        std::remove((base + ".target").c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-crash-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-crash-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-crash-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-crash-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto raw_exec = [&](const std::string& base, const std::string& sql) {
        sqlite3* db = nullptr;
        if (sqlite3_open_v2(base.c_str(), &db, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
            std::string msg = db ? sqlite3_errmsg(db) : "sqlite open failed";
            if (db) sqlite3_close(db);
            throw std::runtime_error("sqlite crash corpus raw open failed: " + msg);
        }
        char* err = nullptr;
        int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err);
        std::string msg = err ? err : "";
        if (err) sqlite3_free(err);
        sqlite3_close(db);
        if (rc != SQLITE_OK) throw std::runtime_error("sqlite crash corpus raw exec failed: " + msg + " sql=" + sql);
    };
    auto seed = [&](const std::string& base, int entries) {
        cleanup(base);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        std::string reason;
        for (int i = 1; i <= entries; ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i)), make_claims("jti-" + std::to_string(i)), "allow", reason)) {
                throw std::runtime_error("seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("seed commit failed: " + reason);
        backend->close();
    };
    auto expect_load_ok = [&](const std::string& base, const std::string& label, long long expected_entries) {
        try {
            auto backend = create_replay_ledger_backend("sqlite-wal");
            backend->load(base, false, "batch");
            ReplayLedgerStats st = backend->stats();
            if (st.loaded_entries == expected_entries && backend->contains_jti("jti-1")) passed++;
            else { failed++; std::cerr << "sqlite crash corpus ok case counter mismatch " << label << " loaded=" << st.loaded_entries << "\n"; }
            backend->close();
        } catch (const std::exception& e) {
            failed++; std::cerr << "sqlite crash corpus expected load ok but rejected " << label << ": " << e.what() << "\n";
        }
        cleanup(base);
    };
    auto expect_load_reject = [&](const std::string& base, const std::string& label) {
        try {
            auto bad = create_replay_ledger_backend("sqlite-wal");
            bad->load(base, false, "batch");
            failed++; std::cerr << "sqlite crash corpus accepted hostile snapshot: " << label << "\n";
        } catch (...) { passed++; }
        cleanup(base);
    };
    auto copy_family = [&](const std::string& from, const std::string& to, bool sidecars) {
        cleanup(to);
        std::filesystem::copy_file(from, to, std::filesystem::copy_options::overwrite_existing);
        if (sidecars) {
            for (const auto& suffix : {std::string("-wal"), std::string("-shm")}) {
                if (std::filesystem::exists(from + suffix)) {
                    std::filesystem::copy_file(from + suffix, to + suffix, std::filesystem::copy_options::overwrite_existing);
                }
            }
        }
    };
    try {
        {
            const std::string base = base_path("reload_ok");
            seed(base, 2);
            expect_load_ok(base, "fresh-reload", 2);
        }
        {
            const std::string base = base_path("snapshot_src");
            const std::string copy = base_path("snapshot_copy");
            seed(base, 2);
            copy_family(base, copy, true);
            expect_load_ok(copy, "checkpointed-family-copy", 2);
            cleanup(base);
        }
        {
            const std::string base = base_path("db_only_src");
            const std::string copy = base_path("db_only_copy");
            seed(base, 2);
            copy_family(base, copy, false);
            expect_load_ok(copy, "db-only-checkpointed-copy", 2);
            cleanup(base);
        }
        {
            const std::string base = base_path("truncated");
            seed(base, 2);
            std::uintmax_t size = std::filesystem::file_size(base);
            std::filesystem::resize_file(base, std::max<std::uintmax_t>(1, size / 2));
            expect_load_reject(base, "truncated-main-db");
        }
        {
            const std::string base = base_path("garbage");
            cleanup(base);
            write_file(base, "not a sqlite database");
            expect_load_reject(base, "garbage-main-db");
        }
        {
            const std::string base = base_path("delete_metadata");
            seed(base, 2);
            raw_exec(base, "DELETE FROM metadata WHERE id=1;");
            expect_load_reject(base, "missing-or-reset-metadata-row");
        }
        {
            const std::string base = base_path("bad_profile_version");
            seed(base, 2);
            raw_exec(base, "DROP TABLE backend_profile; CREATE TABLE backend_profile(id INTEGER PRIMARY KEY, backend_name TEXT, schema_version INTEGER, hash_algorithm TEXT, entry_material_version TEXT, commit_protocol TEXT); INSERT INTO backend_profile VALUES(1,'sqlite-wal',99,'sha256','anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent','sqlite-wal-begin-immediate-full-sync');");
            expect_load_reject(base, "bad-backend-profile-version");
        }
        {
            const std::string base = base_path("metadata_rollback");
            seed(base, 2);
            raw_exec(base, "UPDATE metadata SET line_count=1 WHERE id=1;");
            expect_load_reject(base, "metadata-rollback");
        }
        {
            const std::string base = base_path("metadata_head");
            seed(base, 2);
            raw_exec(base, "UPDATE metadata SET head_hash='bad-head' WHERE id=1;");
            expect_load_reject(base, "metadata-head-mismatch");
        }
        {
            const std::string base = base_path("entry_hash");
            seed(base, 2);
            raw_exec(base, "UPDATE ledger_entries SET entry_hash='1111111111111111111111111111111111111111111111111111111111111111' WHERE sequence=1;");
            expect_load_reject(base, "entry-hash-mismatch");
        }
        {
            const std::string base = base_path("previous_hash");
            seed(base, 2);
            raw_exec(base, "UPDATE ledger_entries SET previous_hash='not-the-previous-head' WHERE sequence=2;");
            expect_load_reject(base, "previous-hash-mismatch");
        }
        {
            const std::string base = base_path("sequence_gap");
            seed(base, 2);
            raw_exec(base, "UPDATE ledger_entries SET sequence=4 WHERE sequence=2;");
            expect_load_reject(base, "sequence-gap");
        }
        {
            const std::string base = base_path("drop_entries");
            seed(base, 2);
            raw_exec(base, "DROP TABLE ledger_entries;");
            expect_load_reject(base, "missing-ledger-entries-with-metadata");
        }
        {
            const std::string base = base_path("writer_contention");
            seed(base, 2);
            sqlite3* raw = nullptr;
            if (sqlite3_open_v2(base.c_str(), &raw, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
                failed++; std::cerr << "sqlite crash corpus could not open raw writer contention connection\n";
                if (raw) sqlite3_close(raw);
                cleanup(base);
            } else {
                char* err = nullptr;
                int rc = sqlite3_exec(raw, "BEGIN IMMEDIATE;", nullptr, nullptr, &err);
                if (rc != SQLITE_OK) {
                    failed++; std::cerr << "sqlite crash corpus could not acquire raw writer lock: " << (err ? err : "") << "\n";
                    if (err) sqlite3_free(err);
                    sqlite3_close(raw);
                    cleanup(base);
                } else {
                    auto contended = create_replay_ledger_backend("sqlite-wal");
                    bool rejected = false;
                    std::string reason;
                    try {
                        contended->load(base, false, "batch");
                        if (!contended->stage(make_tc("case-3"), make_claims("jti-3"), "allow", reason)) rejected = true;
                        else if (!contended->commit(reason)) rejected = true;
                    } catch (...) { rejected = true; }
                    if (rejected) passed++; else { failed++; std::cerr << "sqlite crash corpus did not reject writer contention\n"; }
                    sqlite3_exec(raw, "ROLLBACK;", nullptr, nullptr, nullptr);
                    sqlite3_close(raw);
                    cleanup(base);
                }
            }
        }
        {
            const std::string base = base_path("unsupported_mode");
            cleanup(base);
            try { auto bad = create_replay_ledger_backend("sqlite-wal"); bad->load(base, true, "unsafe"); failed++; std::cerr << "sqlite crash corpus accepted unsupported commit mode\n"; }
            catch (...) { passed++; }
            cleanup(base);
        }
    } catch (const std::exception& e) {
        failed++;
        std::cerr << "ledger sqlite crash corpus selftest exception: " << e.what() << "\n";
    }
    std::cout << "anonsync_core ledger sqlite crash corpus selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_host_capability_probe_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0604_host_probe_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string copy = "/tmp/" + stem + "_copy.sqlite";
    auto cleanup = [&]() {
        for (const auto& p : {base, base + "-wal", base + "-shm", copy, copy + "-wal", copy + "-shm"}) std::remove(p.c_str());
    };
    cleanup();
    try {
        if (sqlite3_libversion_number() >= 3000000) passed++; else { failed++; std::cerr << "host probe SQLite library version too old\n"; }
        if (sqlite3_threadsafe() != 0) passed++; else { failed++; std::cerr << "host probe SQLite library is not threadsafe\n"; }
        if (sqlite3_compileoption_used("THREADSAFE=1") || sqlite3_compileoption_used("THREADSAFE=2") || sqlite3_threadsafe() != 0) passed++; else { failed++; std::cerr << "host probe THREADSAFE compile option unavailable\n"; }
        sqlite3* db = nullptr;
        if (sqlite3_open_v2(base.c_str(), &db, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr) != SQLITE_OK) {
            failed++; std::cerr << "host probe could not open SQLite database\n";
        } else {
            char* err = nullptr;
            if (sqlite3_exec(db, "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; CREATE TABLE t(id INTEGER PRIMARY KEY, value TEXT); INSERT INTO t(value) VALUES('ok');", nullptr, nullptr, &err) == SQLITE_OK) passed++;
            else { failed++; std::cerr << "host probe WAL/FULL/create failed: " << (err ? err : "") << "\n"; }
            if (err) sqlite3_free(err);
            sqlite3_stmt* stmt = nullptr;
            if (sqlite3_prepare_v2(db, "PRAGMA integrity_check;", -1, &stmt, nullptr) == SQLITE_OK && sqlite3_step(stmt) == SQLITE_ROW && std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0))) == "ok") passed++;
            else { failed++; std::cerr << "host probe integrity_check failed\n"; }
            if (stmt) sqlite3_finalize(stmt);
            err = nullptr;
            if (sqlite3_exec(db, "BEGIN IMMEDIATE; ROLLBACK;", nullptr, nullptr, &err) == SQLITE_OK) passed++;
            else { failed++; std::cerr << "host probe BEGIN IMMEDIATE failed: " << (err ? err : "") << "\n"; }
            if (err) sqlite3_free(err);
            sqlite3* dst = nullptr;
            if (sqlite3_open_v2(copy.c_str(), &dst, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr) == SQLITE_OK) {
                sqlite3_backup* backup = sqlite3_backup_init(dst, "main", db, "main");
                int rc = backup ? sqlite3_backup_step(backup, -1) : SQLITE_ERROR;
                int frc = backup ? sqlite3_backup_finish(backup) : SQLITE_ERROR;
                if (backup && frc == SQLITE_OK && (rc == SQLITE_DONE || rc == SQLITE_OK)) passed++;
                else { failed++; std::cerr << "host probe sqlite3_backup API failed\n"; }
                sqlite3_close(dst);
            } else { failed++; std::cerr << "host probe could not open backup destination\n"; }
            sqlite3_close(db);
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger host capability probe selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger host capability probe selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_backup_restore_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0604_backup_restore_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string target = "/tmp/" + stem + "_target.sqlite";
    const std::string link = "/tmp/" + stem + "_link.sqlite";
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto cleanup = [&]() {
        cleanup_path(base); cleanup_path(snapshot); cleanup_path(target); cleanup_path(link); std::remove(link.c_str()); std::remove(target.c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-backup-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-backup-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-backup-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-backup-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    cleanup();
    try {
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        if (backend->stage(make_tc("case-1"), make_claims("jti-1"), "allow", reason) && backend->stage(make_tc("case-2"), make_claims("jti-2"), "allow", reason) && backend->commit(reason)) passed++;
        else { failed++; std::cerr << "backup restore seed commit failed: " << reason << "\n"; }
        if (backend->backup_snapshot(snapshot, reason)) passed++; else { failed++; std::cerr << "backup snapshot failed: " << reason << "\n"; }
        if (backend->stats().sqlite_backup_snapshots == 1) passed++; else { failed++; std::cerr << "backup snapshot counter mismatch\n"; }
        backend->close();
        auto restored = create_replay_ledger_backend("sqlite-wal");
        restored->load(snapshot, false, "batch");
        if (restored->stats().loaded_entries == 2) passed++; else { failed++; std::cerr << "snapshot loaded entry count mismatch\n"; }
        if (restored->contains_jti("jti-1") && restored->contains_jti("jti-2")) passed++; else { failed++; std::cerr << "snapshot missing seeded jti\n"; }
        if (restored->stage(make_tc("case-3"), make_claims("jti-3"), "allow", reason) && restored->commit(reason)) passed++; else { failed++; std::cerr << "snapshot append failed: " << reason << "\n"; }
        restored->close();
        auto original_reload = create_replay_ledger_backend("sqlite-wal");
        original_reload->load(base, false, "batch");
        if (!original_reload->contains_jti("jti-3")) passed++; else { failed++; std::cerr << "original ledger was mutated by snapshot append\n"; }
        original_reload->close();
        write_file(target, "not a real sqlite ledger");
        if (::symlink(target.c_str(), link.c_str()) == 0) {
            auto symlink_case = create_replay_ledger_backend("sqlite-wal");
            symlink_case->load(base, false, "batch");
            std::string symlink_reason;
            if (!symlink_case->backup_snapshot(link, symlink_reason)) passed++; else { failed++; std::cerr << "backup snapshot accepted symlink destination\n"; }
            symlink_case->close();
        } else { failed++; std::cerr << "backup restore selftest could not create symlink destination\n"; }
        auto local = create_replay_ledger_backend("local-jsonl");
        local->load("/tmp/" + stem + ".jsonl", true, "batch");
        if (!local->backup_snapshot(snapshot + ".unsupported", reason)) passed++; else { failed++; std::cerr << "local-jsonl accepted SQLite backup snapshot\n"; }
        local->close();
        auto disabled = create_replay_ledger_backend("sqlite-wal");
        if (!disabled->backup_snapshot(snapshot + ".disabled", reason)) passed++; else { failed++; std::cerr << "disabled sqlite backend accepted backup snapshot\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite backup restore selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite backup restore selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_host_capability_report(const std::string& report_path) {
    try {
        write_file(report_path, host_capability_report_json());
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ledger host capability report emission failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_sqlite_snapshot_corpus_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0605_snapshot_corpus_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto cleanup = [&]() {
        for (const auto& p : {base, snapshot,
                              "/tmp/" + stem + "_truncated.sqlite",
                              "/tmp/" + stem + "_garbage.sqlite",
                              "/tmp/" + stem + "_profile.sqlite",
                              "/tmp/" + stem + "_meta.sqlite",
                              "/tmp/" + stem + "_entry.sqlite",
                              "/tmp/" + stem + "_prev.sqlite",
                              "/tmp/" + stem + "_gap.sqlite",
                              "/tmp/" + stem + "_append.sqlite",
                              "/tmp/" + stem + "_link.sqlite",
                              "/tmp/" + stem + "_target.sqlite",
                              "/tmp/" + stem + "_wal_link.sqlite",
                              "/tmp/" + stem + "_shm_link.sqlite"}) cleanup_path(p);
        std::remove(("/tmp/" + stem + "_link.sqlite").c_str());
        std::remove(("/tmp/" + stem + "_wal_link.sqlite-wal").c_str());
        std::remove(("/tmp/" + stem + "_shm_link.sqlite-shm").c_str());
        std::remove(("/tmp/" + stem + "_target.sqlite").c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-snapshot-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-snapshot-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-snapshot-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-snapshot-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto copy_db = [&](const std::string& dst) {
        cleanup_path(dst);
        std::filesystem::copy_file(snapshot, dst, std::filesystem::copy_options::overwrite_existing);
    };
    auto exec_update = [&](const std::string& db_path, const std::string& sql) {
        sqlite3* raw = nullptr;
        if (sqlite3_open_v2(db_path.c_str(), &raw, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX, nullptr) != SQLITE_OK) throw std::runtime_error("open tamper db failed");
        char* err = nullptr;
        if (sqlite3_exec(raw, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
            std::string msg = err ? err : sqlite3_errmsg(raw);
            if (err) sqlite3_free(err);
            sqlite3_close(raw);
            throw std::runtime_error("tamper sql failed: " + msg);
        }
        sqlite3_close(raw);
    };
    auto expect_reject = [&](const std::string& label, const std::string& db_path) {
        try {
            auto candidate = create_replay_ledger_backend("sqlite-wal");
            candidate->load(db_path, false, "batch");
            failed++; std::cerr << "snapshot corpus accepted hostile snapshot " << label << "\n";
        } catch (...) { passed++; }
    };
    cleanup();
    try {
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        bool seeded = backend->stage(make_tc("case-1"), make_claims("jti-1"), "allow", reason) &&
                      backend->stage(make_tc("case-2"), make_claims("jti-2"), "allow", reason) &&
                      backend->stage(make_tc("case-3"), make_claims("jti-3"), "allow", reason) &&
                      backend->commit(reason);
        if (seeded) passed++; else { failed++; std::cerr << "snapshot corpus seed commit failed: " << reason << "\n"; }
        if (backend->backup_snapshot(snapshot, reason)) passed++; else { failed++; std::cerr << "snapshot corpus backup failed: " << reason << "\n"; }
        if (backend->stats().sqlite_snapshot_verifications == 1) passed++; else { failed++; std::cerr << "snapshot corpus strict verification counter mismatch\n"; }
        backend->close();
        auto restored = create_replay_ledger_backend("sqlite-wal");
        restored->load(snapshot, false, "batch");
        if (restored->stats().loaded_entries == 3 && restored->contains_jti("jti-1") && restored->contains_jti("jti-3")) passed++; else { failed++; std::cerr << "snapshot corpus restored snapshot missing rows\n"; }
        restored->close();
        const std::string append_snapshot = "/tmp/" + stem + "_append.sqlite";
        copy_db(append_snapshot);
        auto append = create_replay_ledger_backend("sqlite-wal");
        append->load(append_snapshot, false, "batch");
        if (append->stage(make_tc("case-4"), make_claims("jti-4"), "allow", reason) && append->commit(reason)) passed++; else { failed++; std::cerr << "snapshot corpus append-to-copy failed: " << reason << "\n"; }
        append->close();
        auto original = create_replay_ledger_backend("sqlite-wal");
        original->load(base, false, "batch");
        if (!original->contains_jti("jti-4")) passed++; else { failed++; std::cerr << "snapshot corpus append mutated original ledger\n"; }
        original->close();
        std::string body = read_file(snapshot);
        const std::string truncated = "/tmp/" + stem + "_truncated.sqlite";
        write_file(truncated, body.substr(0, std::max<size_t>(1, body.size() / 2)));
        expect_reject("truncated", truncated);
        const std::string garbage = "/tmp/" + stem + "_garbage.sqlite";
        write_file(garbage, "not a sqlite snapshot");
        expect_reject("garbage", garbage);
        const std::string profile = "/tmp/" + stem + "_profile.sqlite";
        copy_db(profile); exec_update(profile, "DELETE FROM backend_profile WHERE id=1;"); expect_reject("backend_profile", profile);
        const std::string meta = "/tmp/" + stem + "_meta.sqlite";
        copy_db(meta); exec_update(meta, "UPDATE metadata SET head_hash='bad-head' WHERE id=1;"); expect_reject("metadata_head", meta);
        const std::string entry = "/tmp/" + stem + "_entry.sqlite";
        copy_db(entry); exec_update(entry, "UPDATE ledger_entries SET case_id='tampered' WHERE sequence=1;"); expect_reject("entry_hash", entry);
        const std::string prev = "/tmp/" + stem + "_prev.sqlite";
        copy_db(prev); exec_update(prev, "UPDATE ledger_entries SET previous_hash='bad-prev' WHERE sequence=2;"); expect_reject("previous_hash", prev);
        const std::string gap = "/tmp/" + stem + "_gap.sqlite";
        copy_db(gap); exec_update(gap, "DELETE FROM ledger_entries WHERE sequence=2;"); expect_reject("sequence_gap", gap);
        const std::string target = "/tmp/" + stem + "_target.sqlite";
        write_file(target, "target");
        const std::string link = "/tmp/" + stem + "_link.sqlite";
        if (::symlink(target.c_str(), link.c_str()) == 0) {
            auto symlink_case = create_replay_ledger_backend("sqlite-wal");
            symlink_case->load(base, false, "batch");
            std::string symlink_reason;
            if (!symlink_case->backup_snapshot(link, symlink_reason)) passed++; else { failed++; std::cerr << "snapshot corpus accepted symlink snapshot destination\n"; }
            symlink_case->close();
        } else { failed++; std::cerr << "snapshot corpus could not create snapshot symlink\n"; }
        const std::string wal_link = "/tmp/" + stem + "_wal_link.sqlite";
        write_file(wal_link, "placeholder");
        std::remove(wal_link.c_str());
        if (::symlink(target.c_str(), (wal_link + "-wal").c_str()) == 0) {
            auto wal_sidecar = create_replay_ledger_backend("sqlite-wal");
            wal_sidecar->load(base, false, "batch");
            std::string wal_reason;
            if (!wal_sidecar->backup_snapshot(wal_link, wal_reason)) passed++; else { failed++; std::cerr << "snapshot corpus accepted WAL sidecar symlink\n"; }
            wal_sidecar->close();
        } else { failed++; std::cerr << "snapshot corpus could not create WAL sidecar symlink\n"; }
        const std::string shm_link = "/tmp/" + stem + "_shm_link.sqlite";
        if (::symlink(target.c_str(), (shm_link + "-shm").c_str()) == 0) {
            auto shm_sidecar = create_replay_ledger_backend("sqlite-wal");
            shm_sidecar->load(base, false, "batch");
            std::string shm_reason;
            if (!shm_sidecar->backup_snapshot(shm_link, shm_reason)) passed++; else { failed++; std::cerr << "snapshot corpus accepted SHM sidecar symlink\n"; }
            shm_sidecar->close();
        } else { failed++; std::cerr << "snapshot corpus could not create SHM sidecar symlink\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite snapshot corpus selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite snapshot corpus selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_sqlite_restore_corpus_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0606_restore_corpus_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string restored_path = "/tmp/" + stem + "_restored.sqlite";
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto cleanup = [&]() {
        for (const auto& p : {base, snapshot, restored_path,
                              "/tmp/" + stem + "_append.sqlite",
                              "/tmp/" + stem + "_truncated.sqlite",
                              "/tmp/" + stem + "_garbage.sqlite",
                              "/tmp/" + stem + "_profile.sqlite",
                              "/tmp/" + stem + "_meta.sqlite",
                              "/tmp/" + stem + "_entry.sqlite",
                              "/tmp/" + stem + "_prev.sqlite",
                              "/tmp/" + stem + "_gap.sqlite",
                              "/tmp/" + stem + "_src_link.sqlite",
                              "/tmp/" + stem + "_dst_link.sqlite",
                              "/tmp/" + stem + "_src_wal_link.sqlite",
                              "/tmp/" + stem + "_dst_wal_link.sqlite",
                              "/tmp/" + stem + "_src_shm_link.sqlite",
                              "/tmp/" + stem + "_dst_shm_link.sqlite",
                              "/tmp/" + stem + "_target.sqlite"}) cleanup_path(p);
        std::remove(("/tmp/" + stem + "_src_link.sqlite").c_str());
        std::remove(("/tmp/" + stem + "_dst_link.sqlite").c_str());
        std::remove(("/tmp/" + stem + "_src_wal_link.sqlite-wal").c_str());
        std::remove(("/tmp/" + stem + "_dst_wal_link.sqlite-wal").c_str());
        std::remove(("/tmp/" + stem + "_src_shm_link.sqlite-shm").c_str());
        std::remove(("/tmp/" + stem + "_dst_shm_link.sqlite-shm").c_str());
        std::remove(("/tmp/" + stem + "_target.sqlite").c_str());
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-restore-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-restore-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto copy_db = [&](const std::string& dst) {
        cleanup_path(dst);
        std::filesystem::copy_file(snapshot, dst, std::filesystem::copy_options::overwrite_existing);
    };
    auto exec_update = [&](const std::string& db_path, const std::string& sql) {
        sqlite3* raw = nullptr;
        if (sqlite3_open_v2(db_path.c_str(), &raw, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX, nullptr) != SQLITE_OK) throw std::runtime_error("restore corpus open tamper db failed");
        char* err = nullptr;
        if (sqlite3_exec(raw, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
            std::string msg = err ? err : sqlite3_errmsg(raw);
            if (err) sqlite3_free(err);
            sqlite3_close(raw);
            throw std::runtime_error("restore corpus tamper sql failed: " + msg);
        }
        sqlite3_close(raw);
    };
    auto expect_restore_reject = [&](const std::string& label, const std::string& src, const std::string& dst) {
        try {
            restore_sqlite_snapshot_into_ledger(src, dst);
            failed++; std::cerr << "restore corpus accepted hostile restore " << label << "\n";
        } catch (...) { passed++; }
    };
    cleanup();
    try {
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        bool seeded = backend->stage(make_tc("case-1"), make_claims("jti-1"), "allow", reason) &&
                      backend->stage(make_tc("case-2"), make_claims("jti-2"), "allow", reason) &&
                      backend->stage(make_tc("case-3"), make_claims("jti-3"), "allow", reason) &&
                      backend->commit(reason);
        if (seeded) passed++; else { failed++; std::cerr << "restore corpus seed commit failed: " << reason << "\n"; }
        if (backend->backup_snapshot(snapshot, reason)) passed++; else { failed++; std::cerr << "restore corpus backup failed: " << reason << "\n"; }
        backend->close();

        restore_sqlite_snapshot_into_ledger(snapshot, restored_path);
        auto restored = create_replay_ledger_backend("sqlite-wal");
        restored->load(restored_path, false, "batch");
        if (restored->stats().loaded_entries == 3 && restored->contains_jti("jti-1") && restored->contains_jti("jti-3")) passed++; else { failed++; std::cerr << "restore corpus restored destination missing rows\n"; }
        if (restored->stage(make_tc("case-4"), make_claims("jti-4"), "allow", reason) && restored->commit(reason)) passed++; else { failed++; std::cerr << "restore corpus append to restored ledger failed: " << reason << "\n"; }
        restored->close();
        auto source_reload = create_replay_ledger_backend("sqlite-wal");
        source_reload->load(snapshot, false, "batch");
        if (!source_reload->contains_jti("jti-4")) passed++; else { failed++; std::cerr << "restore corpus append mutated source snapshot\n"; }
        source_reload->close();

        expect_restore_reject("identical_source_destination", snapshot, snapshot);
        std::string body = read_file(snapshot);
        const std::string truncated = "/tmp/" + stem + "_truncated.sqlite";
        write_file(truncated, body.substr(0, std::max<size_t>(1, body.size() / 2)));
        expect_restore_reject("truncated", truncated, "/tmp/" + stem + "_truncated_dst.sqlite");
        const std::string garbage = "/tmp/" + stem + "_garbage.sqlite";
        write_file(garbage, "not a sqlite snapshot");
        expect_restore_reject("garbage", garbage, "/tmp/" + stem + "_garbage_dst.sqlite");
        const std::string profile = "/tmp/" + stem + "_profile.sqlite";
        copy_db(profile); exec_update(profile, "DELETE FROM backend_profile WHERE id=1;"); expect_restore_reject("backend_profile", profile, "/tmp/" + stem + "_profile_dst.sqlite");
        const std::string meta = "/tmp/" + stem + "_meta.sqlite";
        copy_db(meta); exec_update(meta, "UPDATE metadata SET head_hash='bad-head' WHERE id=1;"); expect_restore_reject("metadata_head", meta, "/tmp/" + stem + "_meta_dst.sqlite");
        const std::string entry = "/tmp/" + stem + "_entry.sqlite";
        copy_db(entry); exec_update(entry, "UPDATE ledger_entries SET case_id='tampered' WHERE sequence=1;"); expect_restore_reject("entry_hash", entry, "/tmp/" + stem + "_entry_dst.sqlite");
        const std::string prev = "/tmp/" + stem + "_prev.sqlite";
        copy_db(prev); exec_update(prev, "UPDATE ledger_entries SET previous_hash='bad-prev' WHERE sequence=2;"); expect_restore_reject("previous_hash", prev, "/tmp/" + stem + "_prev_dst.sqlite");
        const std::string gap = "/tmp/" + stem + "_gap.sqlite";
        copy_db(gap); exec_update(gap, "DELETE FROM ledger_entries WHERE sequence=2;"); expect_restore_reject("sequence_gap", gap, "/tmp/" + stem + "_gap_dst.sqlite");

        const std::string target = "/tmp/" + stem + "_target.sqlite";
        write_file(target, "target");
        const std::string src_link = "/tmp/" + stem + "_src_link.sqlite";
        if (::symlink(target.c_str(), src_link.c_str()) == 0) expect_restore_reject("source_symlink", src_link, "/tmp/" + stem + "_src_link_dst.sqlite"); else { failed++; std::cerr << "restore corpus could not create source symlink\n"; }
        const std::string dst_link = "/tmp/" + stem + "_dst_link.sqlite";
        write_file(dst_link + ".target", "target");
        std::remove(dst_link.c_str());
        if (::symlink(target.c_str(), dst_link.c_str()) == 0) expect_restore_reject("destination_symlink", snapshot, dst_link); else { failed++; std::cerr << "restore corpus could not create destination symlink\n"; }
        const std::string src_wal = "/tmp/" + stem + "_src_wal_link.sqlite";
        copy_db(src_wal); std::remove((src_wal + "-wal").c_str());
        if (::symlink(target.c_str(), (src_wal + "-wal").c_str()) == 0) expect_restore_reject("source_wal_sidecar_symlink", src_wal, "/tmp/" + stem + "_src_wal_dst.sqlite"); else { failed++; std::cerr << "restore corpus could not create source WAL sidecar symlink\n"; }
        const std::string dst_wal = "/tmp/" + stem + "_dst_wal_link.sqlite";
        std::remove((dst_wal + "-wal").c_str());
        if (::symlink(target.c_str(), (dst_wal + "-wal").c_str()) == 0) expect_restore_reject("destination_wal_sidecar_symlink", snapshot, dst_wal); else { failed++; std::cerr << "restore corpus could not create destination WAL sidecar symlink\n"; }
        const std::string src_shm = "/tmp/" + stem + "_src_shm_link.sqlite";
        copy_db(src_shm); std::remove((src_shm + "-shm").c_str());
        if (::symlink(target.c_str(), (src_shm + "-shm").c_str()) == 0) expect_restore_reject("source_shm_sidecar_symlink", src_shm, "/tmp/" + stem + "_src_shm_dst.sqlite"); else { failed++; std::cerr << "restore corpus could not create source SHM sidecar symlink\n"; }
        const std::string dst_shm = "/tmp/" + stem + "_dst_shm_link.sqlite";
        std::remove((dst_shm + "-shm").c_str());
        if (::symlink(target.c_str(), (dst_shm + "-shm").c_str()) == 0) expect_restore_reject("destination_shm_sidecar_symlink", snapshot, dst_shm); else { failed++; std::cerr << "restore corpus could not create destination SHM sidecar symlink\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore corpus selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger sqlite restore corpus selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}



int run_ledger_sqlite_restore_rollback_guard_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_rollback_guard_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-rollback-guard-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-rollback-guard-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, true, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("rollback guard seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("rollback guard seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("rollback guard snapshot failed: " + reason);
        backend->close();
    };
    auto expect_restore_ok = [&](const std::string& label, const std::string& snapshot, const std::string& dst) {
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst);
            passed++;
        } catch (const std::exception& e) {
            failed++; std::cerr << "rollback guard rejected valid restore " << label << ": " << e.what() << "\n";
        }
    };
    auto expect_restore_reject = [&](const std::string& label, const std::string& snapshot, const std::string& dst, const std::string& needle) {
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst);
            failed++; std::cerr << "rollback guard accepted hostile restore " << label << "\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find(needle) != std::string::npos) passed++;
            else { failed++; std::cerr << "rollback guard reject reason mismatch for " << label << ": " << e.what() << "\n"; }
        }
    };
    const std::string old_ledger = "/tmp/" + stem + "_old.sqlite";
    const std::string newer_ledger = "/tmp/" + stem + "_newer.sqlite";
    const std::string divergent_a = "/tmp/" + stem + "_div_a.sqlite";
    const std::string divergent_b = "/tmp/" + stem + "_div_b.sqlite";
    const std::string empty_dest = "/tmp/" + stem + "_empty_dest.sqlite";
    const std::string forward_dest = "/tmp/" + stem + "_forward_dest.sqlite";
    const std::string idempotent_dest = "/tmp/" + stem + "_idempotent_dest.sqlite";
    const std::string old_snapshot = "/tmp/" + stem + "_old_snapshot.sqlite";
    const std::string newer_snapshot = "/tmp/" + stem + "_newer_snapshot.sqlite";
    const std::string divergent_snapshot = "/tmp/" + stem + "_div_snapshot.sqlite";
    try {
        seed_ledger(old_ledger, {"old-jti-1", "old-jti-2"}, "sqlite-rollback-old-op");
        seed_ledger(newer_ledger, {"new-jti-1", "new-jti-2", "new-jti-3"}, "sqlite-rollback-new-op");
        seed_ledger(divergent_a, {"same-height-a-1", "same-height-a-2"}, "sqlite-rollback-div-a-op");
        seed_ledger(divergent_b, {"same-height-b-1", "same-height-b-2"}, "sqlite-rollback-div-b-op");
        snapshot_from(old_ledger, old_snapshot);
        snapshot_from(newer_ledger, newer_snapshot);
        snapshot_from(divergent_a, divergent_snapshot);

        cleanup_path(empty_dest);
        expect_restore_ok("empty_destination", old_snapshot, empty_dest);

        seed_ledger(forward_dest, {"new-jti-1"}, "sqlite-rollback-new-op");
        expect_restore_ok("forward_snapshot_over_shorter_destination", newer_snapshot, forward_dest);

        cleanup_path(idempotent_dest);
        std::filesystem::copy_file(old_snapshot, idempotent_dest, std::filesystem::copy_options::overwrite_existing);
        expect_restore_ok("idempotent_same_head_same_height", old_snapshot, idempotent_dest);

        expect_restore_reject("older_snapshot_over_newer_destination", old_snapshot, newer_ledger, "older snapshot line count");
        expect_restore_reject("divergent_same_height_snapshot", divergent_snapshot, divergent_b, "divergent same-height snapshot head");
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore rollback guard selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {old_ledger, newer_ledger, divergent_a, divergent_b, empty_dest, forward_dest, idempotent_dest, old_snapshot, newer_snapshot, divergent_snapshot}) cleanup_path(p);
    std::cout << "anonsync_core ledger sqlite restore rollback guard selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_restore_atomicity_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_atomicity_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-atomic-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-atomic-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, true, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("atomic restore seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("atomic restore seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("atomic restore snapshot failed: " + reason);
        backend->close();
    };
    auto stats_for = [&](const std::string& path) {
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, false, "batch");
        ReplayLedgerStats st = backend->stats();
        backend->close();
        return st;
    };
    auto expect_entries = [&](const std::string& label, const std::string& path, long long count, const std::string& head) {
        try {
            ReplayLedgerStats st = stats_for(path);
            if (st.durable_line_count == count && (head.empty() || st.durable_head_hash == head)) passed++;
            else { failed++; std::cerr << "atomic restore " << label << " expected count=" << count << " head=" << head << " got count=" << st.durable_line_count << " head=" << st.durable_head_hash << "\n"; }
        } catch (const std::exception& e) {
            failed++; std::cerr << "atomic restore " << label << " failed to load destination: " << e.what() << "\n";
        }
    };
    auto expect_fault_preserves = [&](const std::string& label, const std::string& checkpoint, const std::string& snapshot, const std::string& dst, long long expected_count, const std::string& expected_head) {
        ::setenv("ANONSYNC_SQLITE_RESTORE_FAULT_AT", checkpoint.c_str(), 1);
        bool threw = false;
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst);
        } catch (const std::exception& e) {
            threw = std::string(e.what()).find(checkpoint) != std::string::npos;
        }
        ::unsetenv("ANONSYNC_SQLITE_RESTORE_FAULT_AT");
        if (threw) passed++; else { failed++; std::cerr << "atomic restore fault injection did not throw at " << label << "\n"; }
        expect_entries(label + " destination state", dst, expected_count, expected_head);
    };
    const std::string old_ledger = "/tmp/" + stem + "_old.sqlite";
    const std::string new_ledger = "/tmp/" + stem + "_new.sqlite";
    const std::string old_snapshot = "/tmp/" + stem + "_old_snapshot.sqlite";
    const std::string new_snapshot = "/tmp/" + stem + "_new_snapshot.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    try {
        seed_ledger(old_ledger, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        seed_ledger(new_ledger, {"old-jti-1", "old-jti-2", "new-jti-3"}, "sqlite-atomic-old-op");
        snapshot_from(old_ledger, old_snapshot);
        snapshot_from(new_ledger, new_snapshot);
        const std::string old_head = stats_for(old_ledger).durable_head_hash;
        const std::string new_head = stats_for(new_ledger).durable_head_hash;

        seed_ledger(dst, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        expect_fault_preserves("after-temp-verify-before-replace", "after-temp-verify-before-replace", new_snapshot, dst, 2, old_head);

        seed_ledger(dst, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        expect_fault_preserves("after-destination-checkpoint-before-replace", "after-destination-checkpoint-before-replace", new_snapshot, dst, 2, old_head);

        seed_ledger(dst, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        try { restore_sqlite_snapshot_into_ledger(new_snapshot, dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "atomic restore valid forward replace failed: " << e.what() << "\n"; }
        expect_entries("valid forward atomic replace", dst, 3, new_head);

        seed_ledger(dst, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        expect_fault_preserves("after-atomic-rename-before-parent-fsync", "after-atomic-rename-before-parent-fsync", new_snapshot, dst, 3, new_head);

        seed_ledger(dst, {"old-jti-1", "old-jti-2"}, "sqlite-atomic-old-op");
        expect_fault_preserves("after-parent-fsync-before-final-verify", "after-parent-fsync-before-final-verify", new_snapshot, dst, 3, new_head);
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore atomicity selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {old_ledger, new_ledger, old_snapshot, new_snapshot, dst}) cleanup_path(p);
    ::unsetenv("ANONSYNC_SQLITE_RESTORE_FAULT_AT");
    std::cout << "anonsync_core ledger sqlite restore atomicity selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


int run_ledger_snapshot_manifest_verifier_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0612_manifest_verifier_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    const std::string base = "/tmp/" + stem + ".sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string manifest = "/tmp/" + stem + "_manifest.json";
    const std::string trust = "/tmp/" + stem + "_trust.json";
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
    };
    auto cleanup = [&]() {
        cleanup_path(base);
        cleanup_path(snapshot);
        std::remove(manifest.c_str());
        std::remove(trust.c_str());
        for (const auto& suffix : {"_badalg.json", "_badsig.json", "_badprofile.json", "_old.json", "_future.json"}) {
            std::remove(("/tmp/" + stem + suffix).c_str());
        }
        for (const auto& suffix : {"_wrongsubject.json", "_retired.json", "_revision.json", "_source.json", "_oldtrust.json", "_futuretrust.json", "_badtime.json", "_stale.json", "_duplicatekid.json", "_rotation_manifest.json", "_rotation_trust.json", "_v1trust.json", "_digest_tamper.json"}) {
            std::remove(("/tmp/" + stem + suffix).c_str());
        }
    };
    auto make_tc = [](const std::string& case_id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("sqlite-manifest-op");
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-manifest-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("sqlite-manifest-op");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-manifest-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto expect_verify_ok = [&](const std::string& label, const std::string& manifest_path, const std::string& trust_path) {
        try {
            auto v = verify_sqlite_snapshot_manifest(manifest_path, trust_path, snapshot);
            if (v.line_count == 2 && !v.head_hash.empty() && !v.snapshot_sha256.empty()) passed++;
            else { failed++; std::cerr << "manifest verifier valid case had bad summary " << label << "\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "manifest verifier rejected valid case " << label << ": " << e.what() << "\n"; }
    };
    auto expect_verify_reject = [&](const std::string& label, const std::string& manifest_path, const std::string& trust_path) {
        try {
            (void)verify_sqlite_snapshot_manifest(manifest_path, trust_path, snapshot);
            failed++; std::cerr << "manifest verifier accepted hostile case " << label << "\n";
        } catch (...) { passed++; }
    };
    auto replace_one = [](std::string text, const std::string& needle, const std::string& replacement) {
        size_t pos = text.find(needle);
        if (pos == std::string::npos) throw std::runtime_error("replace_one could not find needle: " + needle);
        text.replace(pos, needle.size(), replacement);
        return text;
    };
    cleanup();
    try {
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(base, true, "batch");
        bool seeded = backend->stage(make_tc("case-1"), make_claims("jti-manifest-1"), "allow", reason) &&
                      backend->stage(make_tc("case-2"), make_claims("jti-manifest-2"), "allow", reason) &&
                      backend->commit(reason);
        if (!seeded) throw std::runtime_error("manifest verifier seed commit failed: " + reason);
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("manifest verifier snapshot backup failed: " + reason);
        auto stats = backend->stats();
        backend->close();

        const std::string expected_revision = "rev0612";
        const std::string source_revision = "rev0612-slim";
        const std::string subject = "rev0612-slim-sqlite-snapshot";
        auto root = make_selftest_restore_root("rev0612-selftest-restore-root-kid-1");
        const std::string good_manifest = make_sqlite_snapshot_manifest_v2_selftest(root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-06-13T03:00:00Z", expected_revision, source_revision, subject);
        const std::string good_trust = make_sqlite_snapshot_trust_profile_v3_selftest(root, subject, expected_revision, source_revision);
        write_file(manifest, good_manifest);
        write_file(trust, good_trust);
        expect_verify_ok("valid-v3", manifest, trust);
        try { verify_trust_profile_digest_pin(trust, sha256_hex(read_file(trust))); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "trust-profile digest pin rejected valid profile: " << e.what() << "\n"; }
        try { verify_trust_profile_digest_pin(trust, std::string(64, '0')); failed++; std::cerr << "trust-profile digest pin accepted wrong digest\n"; }
        catch (...) { passed++; }
        std::string uppercase_digest = sha256_hex(read_file(trust));
        std::transform(uppercase_digest.begin(), uppercase_digest.end(), uppercase_digest.begin(), [](unsigned char c){ return static_cast<char>(std::toupper(c)); });
        try { verify_trust_profile_digest_pin(trust, uppercase_digest); failed++; std::cerr << "trust-profile digest pin accepted uppercase alternate spelling\n"; }
        catch (...) { passed++; }
        const std::string digest_tamper = "/tmp/" + stem + "_digest_tamper.json";
        write_file(digest_tamper, replace_one(good_trust, "C++ selftest restore-root", "Tampered C++ selftest restore-root"));
        try { verify_trust_profile_digest_pin(digest_tamper, sha256_hex(read_file(trust))); failed++; std::cerr << "trust-profile digest pin accepted modified profile under old digest\n"; }
        catch (...) { passed++; }

        const std::string badalg = "/tmp/" + stem + "_badalg.json";
        write_file(badalg, replace_one(good_manifest, "\"alg\": \"RS256\"", "\"alg\": \"none\""));
        expect_verify_reject("bad_alg", badalg, trust);

        const std::string badsig = "/tmp/" + stem + "_badsig.json";
        write_file(badsig, replace_one(good_manifest, "\"signature_b64url\": \"", "\"signature_b64url\": \"A"));
        expect_verify_reject("bad_signature", badsig, trust);

        const std::string badprofile = "/tmp/" + stem + "_badprofile.json";
        write_file(badprofile, replace_one(good_manifest, "\"schema_version\": 10", "\"schema_version\": 2"));
        expect_verify_reject("backend_profile_tamper", badprofile, trust);

        const std::string wrongsubject = "/tmp/" + stem + "_wrongsubject.json";
        write_file(wrongsubject, make_sqlite_snapshot_trust_profile_v3_selftest(root, "wrong-subject", expected_revision, source_revision));
        expect_verify_reject("required_subject_mismatch", manifest, wrongsubject);

        const std::string retired = "/tmp/" + stem + "_retired.json";
        write_file(retired, make_sqlite_snapshot_trust_profile_v3_selftest(root, subject, expected_revision, source_revision, "2026-06-13T00:00:00Z", "2026-06-30T00:00:00Z", "retired"));
        expect_verify_reject("retired_signer", manifest, retired);

        const std::string revision = "/tmp/" + stem + "_revision.json";
        write_file(revision, make_sqlite_snapshot_trust_profile_v3_selftest(root, subject, "rev9999", source_revision));
        expect_verify_reject("expected_revision_allowlist", manifest, revision);

        const std::string source = "/tmp/" + stem + "_source.json";
        write_file(source, make_sqlite_snapshot_trust_profile_v3_selftest(root, subject, expected_revision, "rev9999-slim"));
        expect_verify_reject("source_revision_allowlist", manifest, source);

        const std::string outer_revision_tamper = "/tmp/" + stem + "_outer_revision_tamper.json";
        write_file(outer_revision_tamper, replace_one(good_manifest, "\"revision_id\": \"" + expected_revision + "\"", "\"revision_id\": \"rev9999\""));
        expect_verify_reject("outer_revision_unsigned_tamper", outer_revision_tamper, trust);

        const std::string payload_revision_tamper = "/tmp/" + stem + "_payload_revision_tamper.json";
        write_file(payload_revision_tamper, replace_one(good_manifest, "\"manifest_revision_id\": \"" + expected_revision + "\"", "\"manifest_revision_id\": \"rev9999\""));
        expect_verify_reject("payload_revision_signature_tamper", payload_revision_tamper, trust);

        const std::string outer_parent_tamper = "/tmp/" + stem + "_outer_parent_tamper.json";
        write_file(outer_parent_tamper, replace_one(good_manifest, "\"parent_revision\": \"rev0620\"", "\"parent_revision\": \"rev0000\""));
        expect_verify_reject("outer_parent_unsigned_tamper", outer_parent_tamper, trust);

        const std::string old_manifest = "/tmp/" + stem + "_old.json";
        write_file(old_manifest, make_sqlite_snapshot_manifest_v2_selftest(root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-06-12T23:59:59Z", expected_revision, source_revision, subject));
        expect_verify_reject("manifest_before_trust_window", old_manifest, trust);

        const std::string future_manifest = "/tmp/" + stem + "_future.json";
        write_file(future_manifest, make_sqlite_snapshot_manifest_v2_selftest(root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-07-01T00:00:01Z", expected_revision, source_revision, subject));
        expect_verify_reject("manifest_after_trust_window", future_manifest, trust);

        const std::string bad_time = "/tmp/" + stem + "_badtime.json";
        write_file(bad_time, make_sqlite_snapshot_manifest_v2_selftest(root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-06-13 03:00:00Z", expected_revision, source_revision, subject));
        expect_verify_reject("non_canonical_issued_at", bad_time, trust);

        const std::string stale = "/tmp/" + stem + "_stale.json";
        write_file(stale, make_sqlite_snapshot_manifest_v2_selftest(root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-06-13T01:00:00Z", expected_revision, source_revision, subject));
        expect_verify_reject("manifest_stale_by_max_age", stale, trust);

        const std::string duplicate_kid = "/tmp/" + stem + "_duplicatekid.json";
        write_file(duplicate_kid, make_sqlite_snapshot_trust_profile_v3_selftest(root, subject, expected_revision, source_revision, "2026-06-13T00:00:00Z", "2026-06-30T00:00:00Z", "trusted", "2026-06-13T03:10:00Z", 3600, restore_root_signer_json_selftest(root, "2026-06-13T00:00:00Z", "2026-06-30T00:00:00Z", "trusted")));
        expect_verify_reject("duplicate_signer_kid", manifest, duplicate_kid);

        auto rotated_root = make_selftest_restore_root("rev0612-selftest-restore-root-kid-2");
        const std::string rotation_manifest = "/tmp/" + stem + "_rotation_manifest.json";
        const std::string rotation_trust = "/tmp/" + stem + "_rotation_trust.json";
        write_file(rotation_manifest, make_sqlite_snapshot_manifest_v2_selftest(rotated_root, snapshot, stats.durable_line_count, stats.durable_head_hash, "2026-06-13T03:00:00Z", expected_revision, source_revision, subject));
        write_file(rotation_trust, make_sqlite_snapshot_trust_profile_v3_selftest(rotated_root, subject, expected_revision, source_revision, "2026-06-13T02:00:00Z", "2026-06-30T00:00:00Z", "trusted", "2026-06-13T03:10:00Z", 3600, restore_root_signer_json_selftest(root, "2026-05-01T00:00:00Z", "2026-06-13T02:30:00Z", "retired")));
        expect_verify_ok("restore_root_rotation_overlap", rotation_manifest, rotation_trust);

        const std::string v1_manifest = "/tmp/" + stem + "_v1.json";
        write_file(v1_manifest, replace_one(good_manifest, "anonsync-sqlite-snapshot-manifest-v2", "anonsync-sqlite-snapshot-manifest-v1"));
        expect_verify_reject("legacy_v1_manifest", v1_manifest, trust);

        const std::string v1_trust = "/tmp/" + stem + "_v1trust.json";
        write_file(v1_trust, replace_one(good_trust, "anonsync-sqlite-snapshot-trust-profile-v3", "anonsync-sqlite-snapshot-trust-profile-v2"));
        expect_verify_reject("legacy_v2_trust", manifest, v1_trust);
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger snapshot manifest verifier selftest exception: " << e.what() << "\n";
    }
    cleanup();
    std::cout << "anonsync_core ledger snapshot manifest verifier selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_sqlite_writer_lock_holder(const std::string& ledger_path, long long seconds) {
    sqlite3* raw = nullptr;
    try {
        auto initializer = create_replay_ledger_backend("sqlite-wal");
        initializer->load(ledger_path, false, "batch");
        initializer->close();
        if (sqlite3_open_v2(ledger_path.c_str(), &raw, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
            std::string msg = raw ? sqlite3_errmsg(raw) : "sqlite open failed";
            if (raw) sqlite3_close(raw);
            std::cerr << "sqlite writer lock holder open failed: " << msg << "\n";
            return 1;
        }
        char* err = nullptr;
        if (sqlite3_exec(raw, "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; BEGIN IMMEDIATE;", nullptr, nullptr, &err) != SQLITE_OK) {
            std::cerr << "sqlite writer lock holder BEGIN IMMEDIATE failed: " << (err ? err : "") << "\n";
            if (err) sqlite3_free(err);
            sqlite3_close(raw);
            return 1;
        }
        std::cout << "anonsync_core sqlite writer lock holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        sqlite3_exec(raw, "ROLLBACK;", nullptr, nullptr, nullptr);
        sqlite3_close(raw);
        return 0;
    } catch (const std::exception& e) {
        if (raw) sqlite3_close(raw);
        std::cerr << "sqlite writer lock holder failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_lock_holder(const std::string& ledger_path, long long seconds) {
    try {
        ReplayLedger ledger;
        ledger.load(ledger_path, false);
        std::cout << "anonsync_core ledger lock holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ledger lock holder failed: " << e.what() << "\n";
        return 1;
    }
}

}  // namespace anonsync
