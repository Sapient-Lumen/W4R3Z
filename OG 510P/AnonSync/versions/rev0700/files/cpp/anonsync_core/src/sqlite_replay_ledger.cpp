#include "anonsync_core_internal.hpp"

#include <sqlite3.h>

#include <cerrno>
#include <climits>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <chrono>
#include <thread>

#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace anonsync {

// rev0605 translation unit: SQLite/WAL backup snapshots are verified through the normal profile/integrity/hash-chain loader and hostile snapshot corpus.
// rev0622 translation unit: runner restore passes a single digest-pinned trust-profile read into manifest verification.
// rev0621 translation unit: SQLite/WAL signed snapshot manifests bind outer revision fields to signed payload fields before trust allowlist checks.
// rev0631 translation unit: terminal-effect transition intents are bound to a per-ledger instance id so signed closure cannot be replayed onto a differently initialized ledger with matching heads; byte-for-byte clones retain the same identity.
// rev0631 translation unit: raw terminal-effect transition API is fail-closed; only signed, digest-pinned transition intents bound to this ledger_instance_id may append terminal state.
// rev0601 translation unit: production-shaped replay-ledger backend factory with SQLite/WAL candidate backend.
namespace {

std::string event_identity_key(const std::string& cloud_event_source, const std::string& cloud_event_id) {
    if (cloud_event_source.empty() || cloud_event_id.empty()) return "";
    return length_prefixed_security_tuple("anonsync-cloud-event-identity-v2", {
        {"source", cloud_event_source},
        {"id", cloud_event_id},
    });
}

const int kSqliteLedgerSchemaVersion = 10;
const char* kSqliteLedgerEntryMaterialVersion = "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent";
const char* kSqliteLedgerCommitProtocol = "sqlite-wal-begin-immediate-full-sync";
const char* kPreparedEffectState = "prepared";
const char* kAppliedEffectState = "applied";
const char* kFailedEffectState = "failed";
const char* kCompensatedEffectState = "compensated";
const char* kEffectOutboxReservedState = "reserved";
const char* kEffectOutboxInflightState = "inflight";
const char* kEffectOutboxFormat = "anonsync-sqlite-effect-outbox-v1";
const char* kEffectOutboxClaimFormat = "anonsync-sqlite-effect-outbox-claim-v1";
const char* kIngressSenderReplayLedgerFormat = "anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction";
const char* kEffectRelayReportFormat = "anonsync-sqlite-effect-relay-report-v1";
const char* kEffectRelayConfiguredReportFormat = "anonsync-sqlite-effect-relay-report-v2-configured-boundary";
const char* kEffectRelayHandleReportFormat = "anonsync-sqlite-effect-relay-report-v3-handle-boundary";
const char* kEffectRelayAdapterConfigFormat = "anonsync-effect-relay-adapter-config-v1";
const char* kEffectRelayHandleRegistryFormat = "anonsync-effect-relay-config-registry-v1";
const char* kEffectRelayAdapterKindLocalSqlite = "local-sqlite-downstream-journal";
const char* kEffectRelayDownstreamStoreFormat = "anonsync-relay-downstream-store-v2-provenance-bound";
const char* kEffectRelayResultMaterialVersion = "anonsync-relay-downstream-result-v2-provenance-bound";
const char* kEffectTransitionMaterialVersion = kSqliteLedgerEntryMaterialVersion;
const char* kEffectTransitionIntentSubject = "sqlite-wal-effect-terminal-transition";
const char* kEffectTransitionIntentFormat = "anonsync-effect-transition-intent-v2-ledger-instance";
const char* kEffectTransitionIntentPayloadFormat = "anonsync-effect-transition-intent-payload-v2-ledger-instance";
const char* kEffectTransitionTrustProfileFormat = "anonsync-effect-transition-trust-profile-v2";

bool is_terminal_effect_state(const std::string& value) {
    return value == kAppliedEffectState || value == kFailedEffectState || value == kCompensatedEffectState;
}

bool is_effect_outbox_state(const std::string& value) {
    return value == kEffectOutboxReservedState || value == kEffectOutboxInflightState || is_terminal_effect_state(value);
}

bool is_nonterminal_effect_outbox_state(const std::string& value) {
    return value == kEffectOutboxReservedState || value == kEffectOutboxInflightState;
}

std::string effect_transition_hash_material(long long sequence,
                                            const std::string& previous_hash,
                                            const std::string& ledger_instance_id,
                                            const std::string& effect_idempotency_key,
                                            long long prepared_sequence,
                                            const std::string& prepared_entry_hash,
                                            const std::string& terminal_state,
                                            const std::string& result_digest_sha256,
                                            const std::string& transition_reason,
                                            const std::string& transition_intent_id,
                                            const std::string& transition_intent_signer_kid,
                                            const std::string& transition_intent_sha256) {
    return std::string(kEffectTransitionMaterialVersion) + "\n" +
           std::to_string(sequence) + "\n" + previous_hash + "\n" + ledger_instance_id + "\n" +
           effect_idempotency_key + "\n" + std::to_string(prepared_sequence) + "\n" +
           prepared_entry_hash + "\n" + terminal_state + "\n" +
           result_digest_sha256 + "\n" + transition_reason + "\n" +
           transition_intent_id + "\n" + transition_intent_signer_kid + "\n" +
           transition_intent_sha256;
}

std::string compute_effect_transition_hash(long long sequence,
                                           const std::string& previous_hash,
                                           const std::string& ledger_instance_id,
                                           const std::string& effect_idempotency_key,
                                           long long prepared_sequence,
                                           const std::string& prepared_entry_hash,
                                           const std::string& terminal_state,
                                           const std::string& result_digest_sha256,
                                           const std::string& transition_reason,
                                           const std::string& transition_intent_id,
                                           const std::string& transition_intent_signer_kid,
                                           const std::string& transition_intent_sha256) {
    return sha256_hex(effect_transition_hash_material(sequence, previous_hash, ledger_instance_id, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256));
}

struct PendingSqliteEntry {
    long long sequence = 0;
    std::string previous_hash;
    std::string entry_hash;
    std::string case_id;
    std::string kind;
    std::string operation_id;
    std::string contract_digest;
    std::string jti;
    std::string action;
    std::string cloud_event_source;
    std::string cloud_event_id;
    std::string effect_idempotency_key;
    std::string effect_state;
    bool ingress_sender_replay_required = false;
    std::string ingress_sender_replay_format;
    std::string ingress_sender_replay_key_sha256;
    std::string ingress_sender_replay_service_config_sha256;
    std::string ingress_sender_replay_profile_sha256;
    std::string ingress_sender_replay_cache_instance_id;
    std::string ingress_sender_replay_proof_kid;
    std::string ingress_sender_replay_principal;
    std::string ingress_sender_replay_nonce;
    long long ingress_sender_replay_issued_at_epoch = 0;
    long long ingress_sender_replay_observed_at_epoch = 0;
    long long ingress_sender_replay_window_seconds = 0;
    std::string ingress_sender_replay_material_sha256;
};

struct PreparedEffectReference {
    long long sequence = 0;
    std::string entry_hash;
    std::string effect_idempotency_key;
};

struct EffectTransitionRow {
    long long sequence = 0;
    std::string previous_hash;
    std::string transition_hash;
    std::string ledger_instance_id;
    std::string effect_idempotency_key;
    long long prepared_sequence = 0;
    std::string prepared_entry_hash;
    std::string terminal_state;
    std::string result_digest_sha256;
    std::string transition_reason;
    std::string transition_intent_id;
    std::string transition_intent_signer_kid;
    std::string transition_intent_sha256;
};

struct VerifiedEffectTransitionIntent {
    std::string intent_id;
    std::string issued_at;
    std::string ledger_instance_id;
    std::string effect_idempotency_key;
    long long prepared_sequence = 0;
    std::string prepared_entry_hash;
    std::string terminal_state;
    std::string result_digest_sha256;
    std::string transition_reason;
    std::string prepared_ledger_head_hash;
    std::string effect_transition_previous_hash;
    std::string signer_kid;
    std::string intent_sha256;
};


struct EffectOutboxClaimResult {
    bool claimed = false;
    std::string ledger_instance_id;
    std::string decision_head_hash;
    std::string effect_transition_head_hash;
    std::string worker_id;
    std::string worker_claim_id;
    std::string effect_idempotency_key;
    long long prepared_sequence = 0;
    std::string prepared_entry_hash;
    long long dispatch_attempts = 0;
    long long claimed_at_epoch = 0;
    long long lease_expires_at_epoch = 0;
    std::string previous_outbox_state;
};

struct RelayAdapterProvenance {
    std::string adapter_id;
    std::string adapter_kind;
    std::string adapter_config_sha256;
    std::string config_handle;
    std::string registry_sha256;
};

struct RelayAdapterConfig {
    std::string config_path;
    std::string config_sha256;
    std::string adapter_id;
    std::string adapter_kind;
    std::string downstream_path;
    std::string worker_id;
    long long lease_seconds = 0;
    std::string terminal_state;
    std::string signer_private_key_pem_path;
    std::string signer_kid;
    std::string trust_profile_path;
    std::string trust_profile_sha256;
    bool debug_inject_crash_after_downstream_allowed = false;
};

struct RelayHandleResolution {
    std::string registry_path;
    std::string registry_sha256;
    std::string handle;
    RelayAdapterConfig adapter;
};

struct RelayDownstreamResult {
    bool touched = false;
    bool inserted = false;
    bool replayed_existing = false;
    std::string terminal_state;
    std::string result_digest_sha256;
    std::string result_material_version;
    std::string adapter_id;
    std::string adapter_kind;
    std::string adapter_config_sha256;
    std::string config_handle;
    std::string registry_sha256;
    long long observation_count = 0;
    std::string first_worker_claim_id;
    std::string last_worker_claim_id;
};

struct EffectRelayOnceResult {
    bool claimed = false;
    bool downstream_touched = false;
    bool transition_closed = false;
    bool injected_crash_after_downstream = false;
    bool transition_authority_preflight_verified = false;
    EffectOutboxClaimResult claim;
    RelayDownstreamResult downstream;
    std::string transition_intent_id;
    std::string transition_intent_sha256;
    std::string signer_kid;
    std::string terminal_state;
    std::string adapter_config_format;
    std::string adapter_config_sha256;
    std::string adapter_id;
    std::string adapter_kind;
    std::string config_handle;
    std::string registry_format;
    std::string registry_sha256;
    std::string transition_reason;
    std::string failure_reason;
};

struct RelayTransitionAuthority {
    PKeyPtr signer;
    std::string trust_profile_text;
};

[[noreturn]] void sqlite_throw(sqlite3* db, const std::string& prefix) {
    throw std::runtime_error(prefix + ": " + (db ? sqlite3_errmsg(db) : "sqlite database is not open"));
}

void sqlite_exec_or_throw(sqlite3* db, const std::string& sql, const std::string& label) {
    char* err = nullptr;
    if (sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
        std::string msg = err ? err : sqlite3_errmsg(db);
        sqlite3_free(err);
        throw std::runtime_error(label + ": " + msg);
    }
}

void sqlite_close_best_effort(sqlite3*& db) {
    if (db) sqlite3_close_v2(db);
    db = nullptr;
}

void sqlite_close_or_throw(sqlite3*& db, const std::string& label) {
    if (!db) return;
    int rc = sqlite3_close(db);
    if (rc != SQLITE_OK) {
        std::string msg = sqlite3_errmsg(db);
        sqlite3_close_v2(db);
        db = nullptr;
        throw std::runtime_error(label + ": " + msg);
    }
    db = nullptr;
}

sqlite3* sqlite_open_or_throw(const std::string& path, int flags, const std::string& label) {
    sqlite3* db = nullptr;
    if (sqlite3_open_v2(path.c_str(), &db, flags, nullptr) != SQLITE_OK) {
        std::string msg = db ? sqlite3_errmsg(db) : "sqlite open failed";
        sqlite_close_best_effort(db);
        throw std::runtime_error(label + ": " + msg);
    }
    return db;
}

struct Stmt {
    sqlite3_stmt* stmt = nullptr;
    sqlite3* db = nullptr;
    Stmt(sqlite3* db_, const std::string& sql, const std::string& label) : db(db_) {
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) sqlite_throw(db, label);
    }
    ~Stmt() { if (stmt) sqlite3_finalize(stmt); }
    Stmt(const Stmt&) = delete;
    Stmt& operator=(const Stmt&) = delete;
};

std::string column_text(sqlite3_stmt* stmt, int col) {
    const unsigned char* raw = sqlite3_column_text(stmt, col);
    return raw ? reinterpret_cast<const char*>(raw) : std::string();
}

std::string sqlite_query_single_text(sqlite3* db, const std::string& sql, const std::string& label) {
    Stmt stmt(db, sql, label + " prepare failed");
    int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) sqlite_throw(db, label + " query failed");
    return column_text(stmt.stmt, 0);
}

long long sqlite_query_single_int64(sqlite3* db, const std::string& sql, const std::string& label) {
    Stmt stmt(db, sql, label + " prepare failed");
    int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) sqlite_throw(db, label + " query failed");
    return sqlite3_column_int64(stmt.stmt, 0);
}

void bind_text_or_throw(sqlite3* db, sqlite3_stmt* stmt, int index, const std::string& value, const std::string& label) {
    if (sqlite3_bind_text(stmt, index, value.c_str(), static_cast<int>(value.size()), SQLITE_TRANSIENT) != SQLITE_OK) sqlite_throw(db, label);
}

void bind_int64_or_throw(sqlite3* db, sqlite3_stmt* stmt, int index, long long value, const std::string& label) {
    if (sqlite3_bind_int64(stmt, index, static_cast<sqlite3_int64>(value)) != SQLITE_OK) sqlite_throw(db, label);
}


void assert_restore_destination_not_writer_locked(const std::string& path) {
    if (path.empty()) return;
    std::error_code ec;
    if (!std::filesystem::exists(path, ec) || ec) return;
    sqlite3* db = nullptr;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (sqlite3_open_v2(path.c_str(), &db, flags, nullptr) != SQLITE_OK) {
        if (db) sqlite3_close(db);
        return;
    }
    sqlite3_busy_timeout(db, 100);
    char* err = nullptr;
    int rc = sqlite3_exec(db, "BEGIN IMMEDIATE; ROLLBACK;", nullptr, nullptr, &err);
    std::string msg = err ? err : sqlite3_errmsg(db);
    if (err) sqlite3_free(err);
    sqlite3_close(db);
    if (rc == SQLITE_BUSY || rc == SQLITE_LOCKED || msg.find("locked") != std::string::npos || msg.find("busy") != std::string::npos) {
        throw std::runtime_error("sqlite-wal snapshot restore refuses destination with active writer lock: " + path);
    }
}

void unlink_sqlite_family(const std::string& path) {
    if (path.empty()) return;
    std::remove(path.c_str());
    std::remove((path + "-wal").c_str());
    std::remove((path + "-shm").c_str());
}

void reject_sqlite_family_symlinks(const std::string& path) {
    if (path.empty()) return;
    for (const auto& candidate : {path, path + "-wal", path + "-shm", path + ".write.lock"}) {
        std::error_code ec;
        auto st = std::filesystem::symlink_status(candidate, ec);
        if (ec) {
            if (ec == std::errc::no_such_file_or_directory) continue;
            throw std::runtime_error("sqlite-wal replay ledger symlink-status failed for " + candidate + ": " + ec.message());
        }
        if (std::filesystem::is_symlink(st)) {
            throw std::runtime_error("sqlite-wal replay ledger refuses symbolic-link ledger or sidecar path: " + candidate);
        }
    }
}

void reject_single_symlink_path(const std::string& path, const std::string& label) {
    if (path.empty()) return;
    std::error_code ec;
    auto st = std::filesystem::symlink_status(path, ec);
    if (ec) {
        if (ec == std::errc::no_such_file_or_directory) return;
        throw std::runtime_error(label + " symlink-status failed for " + path + ": " + ec.message());
    }
    if (std::filesystem::is_symlink(st)) {
        throw std::runtime_error(label + " refuses symbolic-link path: " + path);
    }
}

std::string sqlite_restore_lock_path_for(const std::string& ledger_path) {
    if (ledger_path.empty()) throw std::runtime_error("sqlite-wal snapshot restore lock requires nonempty ledger path");
    return ledger_path + ".restore.lock";
}

class SqliteRestoreLock {
  public:
    explicit SqliteRestoreLock(const std::string& ledger_path) : path_(sqlite_restore_lock_path_for(ledger_path)) {
        std::filesystem::path parent = std::filesystem::path(path_).parent_path();
        if (!parent.empty()) std::filesystem::create_directories(parent);
        reject_single_symlink_path(path_, "sqlite-wal snapshot restore lock");
        int flags = O_RDWR | O_CREAT;
#ifdef O_CLOEXEC
        flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
        flags |= O_NOFOLLOW;
#endif
        fd_ = ::open(path_.c_str(), flags, 0600);
        if (fd_ < 0) {
            throw std::runtime_error(std::string("sqlite-wal snapshot restore lock open failed: ") + std::strerror(errno));
        }
        struct stat st{};
        if (::fstat(fd_, &st) != 0 || !S_ISREG(st.st_mode)) {
            const std::string msg = std::string("sqlite-wal snapshot restore lock refuses non-regular lock path: ") + path_;
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error(msg);
        }
        if (::flock(fd_, LOCK_EX | LOCK_NB) != 0) {
            const std::string msg = std::string("sqlite-wal snapshot restore lock contention on ") + path_ + ": " + std::strerror(errno);
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error(msg);
        }
        const std::string marker = "pid=" + std::to_string(static_cast<long long>(::getpid())) + "\n";
        (void)::ftruncate(fd_, 0);
        (void)::write(fd_, marker.data(), marker.size());
        (void)::fsync(fd_);
    }
    ~SqliteRestoreLock() {
        if (fd_ >= 0) {
            (void)::flock(fd_, LOCK_UN);
            (void)::close(fd_);
            fd_ = -1;
        }
    }
    SqliteRestoreLock(const SqliteRestoreLock&) = delete;
    SqliteRestoreLock& operator=(const SqliteRestoreLock&) = delete;
  private:
    std::string path_;
    int fd_ = -1;
};

std::string sqlite_write_gate_path_for(const std::string& ledger_path) {
    if (ledger_path.empty()) throw std::runtime_error("sqlite-wal replay ledger write-gate requires nonempty ledger path");
    return ledger_path + ".write.lock";
}

thread_local std::unordered_set<std::string> held_sqlite_write_gate_paths;

class SqliteWriteGateLock {
  public:
    explicit SqliteWriteGateLock(const std::string& ledger_path) : path_(sqlite_write_gate_path_for(ledger_path)) {
        std::filesystem::path parent = std::filesystem::path(path_).parent_path();
        if (!parent.empty()) std::filesystem::create_directories(parent);
        std::error_code abs_ec;
        key_ = std::filesystem::absolute(path_, abs_ec).lexically_normal().string();
        if (abs_ec) key_ = path_;
        if (held_sqlite_write_gate_paths.find(key_) != held_sqlite_write_gate_paths.end()) {
            nested_ = true;
            return;
        }
        reject_single_symlink_path(path_, "sqlite-wal replay ledger write-gate");
        int flags = O_RDWR | O_CREAT;
#ifdef O_CLOEXEC
        flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
        flags |= O_NOFOLLOW;
#endif
        fd_ = ::open(path_.c_str(), flags, 0600);
        if (fd_ < 0) {
            throw std::runtime_error(std::string("sqlite-wal replay ledger write-gate open failed: ") + std::strerror(errno));
        }
        struct stat st{};
        if (::fstat(fd_, &st) != 0 || !S_ISREG(st.st_mode)) {
            const std::string msg = std::string("sqlite-wal replay ledger write-gate refuses non-regular lock path: ") + path_;
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error(msg);
        }
        if (::flock(fd_, LOCK_EX | LOCK_NB) != 0) {
            const std::string msg = std::string("sqlite-wal replay ledger write-gate lock contention on ") + path_ + ": " + std::strerror(errno);
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error(msg);
        }
        const std::string marker = "pid=" + std::to_string(static_cast<long long>(::getpid())) + "\n";
        (void)::ftruncate(fd_, 0);
        (void)::write(fd_, marker.data(), marker.size());
        (void)::fsync(fd_);
        held_sqlite_write_gate_paths.insert(key_);
    }
    ~SqliteWriteGateLock() {
        if (nested_) return;
        if (fd_ >= 0) {
            (void)::flock(fd_, LOCK_UN);
            (void)::close(fd_);
            fd_ = -1;
        }
        if (!key_.empty()) held_sqlite_write_gate_paths.erase(key_);
    }
    SqliteWriteGateLock(const SqliteWriteGateLock&) = delete;
    SqliteWriteGateLock& operator=(const SqliteWriteGateLock&) = delete;
  private:
    std::string path_;
    std::string key_;
    int fd_ = -1;
    bool nested_ = false;
};

int sqlite_open_flags_for_ledger() {
    int open_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    open_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    return open_flags;
}

std::string sqlite_entry_hash_at_sequence(const std::string& path, long long sequence) {
    if (path.empty()) throw std::runtime_error("sqlite-wal replay ledger prefix continuity check requires nonempty snapshot path");
    if (sequence <= 0) return "GENESIS";
    reject_sqlite_family_symlinks(path);
    sqlite3* db = nullptr;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    db = sqlite_open_or_throw(path, flags, "sqlite-wal replay ledger prefix continuity open failed");
    sqlite3_busy_timeout(db, 1000);
    try {
        std::string out;
        bool missing = false;
        {
            Stmt stmt(db, "SELECT entry_hash FROM ledger_entries WHERE sequence=?;", "sqlite-wal replay ledger prefix continuity prepare failed");
            bind_int64_or_throw(db, stmt.stmt, 1, sequence, "sqlite-wal replay ledger prefix continuity sequence bind failed");
            int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_ROW) out = column_text(stmt.stmt, 0);
            else if (rc == SQLITE_DONE) missing = true;
            else sqlite_throw(db, "sqlite-wal replay ledger prefix continuity query failed");
        }  // Finalize the statement before closing the database handle.
        sqlite_close_or_throw(db, "sqlite-wal replay ledger prefix continuity close failed");
        if (missing) {
            throw std::runtime_error("sqlite-wal replay ledger prefix continuity missing entry at destination sequence " + std::to_string(sequence));
        }
        return out;
    } catch (...) {
        if (db) sqlite3_close_v2(db);
        throw;
    }
}


void maybe_inject_restore_fault(const std::string& checkpoint) {
    const char* fault = std::getenv("ANONSYNC_SQLITE_RESTORE_FAULT_AT");
    if (fault && checkpoint == fault) {
        throw std::runtime_error("injected sqlite-wal snapshot restore fault at " + checkpoint);
    }
}

void fsync_parent_directory_for_restore(const std::string& path) {
    std::filesystem::path parent = std::filesystem::path(path).parent_path();
    if (parent.empty()) parent = ".";
    int dfd = ::open(parent.string().c_str(), O_RDONLY | O_DIRECTORY);
    if (dfd < 0) throw std::runtime_error(std::string("sqlite-wal snapshot restore parent directory open failed: ") + std::strerror(errno));
    if (::fsync(dfd) != 0) {
        std::string msg = std::string("sqlite-wal snapshot restore parent directory fsync failed: ") + std::strerror(errno);
        ::close(dfd);
        throw std::runtime_error(msg);
    }
    ::close(dfd);
}

std::string restore_temp_path_for(const std::string& ledger_path) {
    std::filesystem::path p(ledger_path);
    std::filesystem::path parent = p.parent_path();
    if (parent.empty()) parent = ".";
    std::ostringstream name;
    name << "." << p.filename().string() << ".restore-tmp-" << static_cast<long long>(::getpid()) << "-" << static_cast<long long>(std::time(nullptr)) << ".sqlite";
    return (parent / name.str()).string();
}

void checkpoint_destination_before_restore_replace(const std::string& ledger_path) {
    if (ledger_path.empty()) return;
    std::error_code ec;
    if (!std::filesystem::exists(ledger_path, ec) || ec) return;
    std::error_code size_ec;
    const auto existing_size = std::filesystem::file_size(ledger_path, size_ec);
    if (size_ec || existing_size == 0) {
        std::remove((ledger_path + "-wal").c_str());
        std::remove((ledger_path + "-shm").c_str());
        return;
    }
    sqlite3* db = nullptr;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    db = sqlite_open_or_throw(ledger_path, flags, "sqlite-wal snapshot restore destination checkpoint open failed");
    int log_frames = 0;
    int checkpointed_frames = 0;
    int rc = sqlite3_wal_checkpoint_v2(db, nullptr, SQLITE_CHECKPOINT_TRUNCATE, &log_frames, &checkpointed_frames);
    if (rc != SQLITE_OK) {
        std::string msg = sqlite3_errmsg(db);
        sqlite_close_best_effort(db);
        throw std::runtime_error("sqlite-wal snapshot restore destination checkpoint failed: " + msg);
    }
    sqlite_close_or_throw(db, "sqlite-wal snapshot restore destination checkpoint close failed");
    std::remove((ledger_path + "-wal").c_str());
    std::remove((ledger_path + "-shm").c_str());
}


std::string snapshot_manifest_signing_input(const Json& payload) {
    std::ostringstream in;
    in << "anonsync-sqlite-snapshot-manifest-v2\n"
       << payload.at("manifest_revision_id").str() << "\n"
       << payload.at("parent_revision").str() << "\n"
       << payload.at("manifest_issued_at").str() << "\n"
       << payload.at("snapshot_sha256").str() << "\n"
       << payload.at("backend_name").str() << "\n"
       << payload.at("backend_profile").at("backend_name").str() << "\n"
       << payload.at("backend_profile").at("schema_version").integer() << "\n"
       << payload.at("backend_profile").at("entry_material_version").str() << "\n"
       << payload.at("backend_profile").at("hash_algorithm").str() << "\n"
       << payload.at("backend_profile").at("commit_protocol").str() << "\n"
       << payload.at("line_count").integer() << "\n"
       << payload.at("head_hash").str() << "\n"
       << payload.at("expected_revision").str() << "\n"
       << payload.at("source_controls_revision").str() << "\n"
       << payload.at("manifest_subject").str() << "\n"
       << payload.at("durability_ceiling").str() << "\n";
    return in.str();
}

bool json_string_array_contains(const Json& arr, const std::string& needle) {
    if (!arr.is_array()) return false;
    for (const auto& item : arr.a) {
        if (item.is_string() && item.s == needle) return true;
    }
    return false;
}

int two_digits(const std::string& text, size_t pos) {
    if (pos + 1 >= text.size() || text[pos] < '0' || text[pos] > '9' || text[pos + 1] < '0' || text[pos + 1] > '9') {
        throw std::runtime_error("timestamp contains non-digit field");
    }
    return (text[pos] - '0') * 10 + (text[pos + 1] - '0');
}

int four_digits(const std::string& text, size_t pos) {
    int out = 0;
    for (size_t i = 0; i < 4; ++i) {
        char c = text[pos + i];
        if (c < '0' || c > '9') throw std::runtime_error("timestamp contains non-digit year");
        out = out * 10 + (c - '0');
    }
    return out;
}

bool is_leap_year(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int days_in_month(int year, int month) {
    static const int dim[] = {0,31,28,31,30,31,30,31,31,30,31,30,31};
    if (month == 2) return is_leap_year(year) ? 29 : 28;
    if (month < 1 || month > 12) return 0;
    return dim[month];
}

long long days_from_civil(int y, unsigned m, unsigned d) {
    // Howard Hinnant's civil calendar transform; returns days since 1970-01-01.
    y -= m <= 2;
    const int era = (y >= 0 ? y : y - 399) / 400;
    const unsigned yoe = static_cast<unsigned>(y - era * 400);
    const unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return static_cast<long long>(era) * 146097LL + static_cast<long long>(doe) - 719468LL;
}

long long parse_strict_utc_epoch(const std::string& ts, const std::string& label) {
    if (ts.size() != 20 || ts[4] != '-' || ts[7] != '-' || ts[10] != 'T' || ts[13] != ':' || ts[16] != ':' || ts[19] != 'Z') {
        throw std::runtime_error(label + " must use canonical UTC form YYYY-MM-DDTHH:MM:SSZ");
    }
    const int year = four_digits(ts, 0);
    const int month = two_digits(ts, 5);
    const int day = two_digits(ts, 8);
    const int hour = two_digits(ts, 11);
    const int minute = two_digits(ts, 14);
    const int second = two_digits(ts, 17);
    if (year < 1970 || month < 1 || month > 12) throw std::runtime_error(label + " has out-of-range date");
    if (day < 1 || day > days_in_month(year, month)) throw std::runtime_error(label + " has out-of-range day");
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || second < 0 || second > 59) {
        throw std::runtime_error(label + " has out-of-range time");
    }
    return days_from_civil(year, static_cast<unsigned>(month), static_cast<unsigned>(day)) * 86400LL + hour * 3600LL + minute * 60LL + second;
}


bool is_lower_hex_sha256(const std::string& value) {
    if (value.size() != 64) return false;
    for (char c : value) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

std::string random_bytes_for_ledger_instance_seed() {
    std::array<unsigned char, 32> bytes{};
    if (RAND_bytes(bytes.data(), static_cast<int>(bytes.size())) != 1) {
        throw std::runtime_error("OpenSSL CSPRNG failed while creating SQLite ledger_instance_id");
    }
    return std::string(reinterpret_cast<const char*>(bytes.data()), bytes.size());
}

std::string generate_ledger_instance_id(const std::string& ledger_path) {
    return sha256_hex(length_prefixed_security_tuple("anonsync-sqlite-ledger-instance-v2", {
        {"ledger_path", ledger_path},
        {"random_seed", random_bytes_for_ledger_instance_seed()},
    }));
}

void validate_outbox_worker_claim_inputs(const std::string& worker_id, long long now_epoch, long long lease_seconds) {
    if (worker_id.empty()) throw std::runtime_error("sqlite-wal effect outbox claim requires nonempty worker_id");
    if (worker_id.size() > 128) throw std::runtime_error("sqlite-wal effect outbox claim refuses worker_id longer than 128 bytes");
    if (contains_disallowed_security_control(worker_id)) throw std::runtime_error("sqlite-wal effect outbox claim refuses control characters in worker_id");
    for (char c : worker_id) {
        const unsigned char u = static_cast<unsigned char>(c);
        if (u < 0x21 || u > 0x7e) throw std::runtime_error("sqlite-wal effect outbox claim worker_id must be printable ASCII without spaces");
    }
    if (now_epoch <= 0) throw std::runtime_error("sqlite-wal effect outbox claim requires positive now_epoch");
    if (lease_seconds <= 0 || lease_seconds > 86400) throw std::runtime_error("sqlite-wal effect outbox claim lease_seconds must be 1..86400");
    if (now_epoch > LLONG_MAX - lease_seconds) throw std::runtime_error("sqlite-wal effect outbox claim lease expiration overflow");
}

std::string compute_outbox_worker_claim_id(const std::string& ledger_instance_id,
                                           const std::string& effect_idempotency_key,
                                           long long prepared_sequence,
                                           const std::string& prepared_entry_hash,
                                           const std::string& worker_id,
                                           const std::string& previous_claim_id,
                                           long long dispatch_attempts,
                                           long long claimed_at_epoch,
                                           long long lease_expires_at_epoch,
                                           const std::string& decision_head_hash,
                                           const std::string& effect_transition_head_hash) {
    return sha256_hex(length_prefixed_security_tuple(kEffectOutboxClaimFormat, {
        {"ledger_instance_id", ledger_instance_id},
        {"effect_idempotency_key", effect_idempotency_key},
        {"prepared_sequence", std::to_string(prepared_sequence)},
        {"prepared_entry_hash", prepared_entry_hash},
        {"worker_id", worker_id},
        {"previous_claim_id", previous_claim_id},
        {"dispatch_attempts", std::to_string(dispatch_attempts)},
        {"claimed_at_epoch", std::to_string(claimed_at_epoch)},
        {"lease_expires_at_epoch", std::to_string(lease_expires_at_epoch)},
        {"decision_head_hash", decision_head_hash},
        {"effect_transition_head_hash", effect_transition_head_hash},
        {"random_seed", random_bytes_for_ledger_instance_seed()},
    }));
}

std::string query_ledger_instance_id(sqlite3* db, const std::string& label) {
    Stmt stmt(db, "SELECT ledger_instance_id FROM ledger_identity WHERE id=1", label + " ledger_identity prepare failed");
    int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw std::runtime_error(label + " ledger_identity row is absent");
    const std::string instance_id = column_text(stmt.stmt, 0);
    if (!is_lower_hex_sha256(instance_id)) throw std::runtime_error(label + " ledger_identity has invalid ledger_instance_id");
    return instance_id;
}

std::string effect_idempotency_key_from_case_or_legacy(const Json& tc, const Json& claims) {
    const std::string supplied = tc.at("effect_idempotency_key").str();
    if (!supplied.empty()) return supplied;
    // Compatibility fallback for pre-normalized callers. Keep this domain aligned with
    // the JSONL backend so both persistence implementations derive identical safe keys.
    return sha256_hex(length_prefixed_security_tuple("anonsync-effect-idempotency-legacy-v1", {
        {"case_id", tc.at("case_id").str()},
        {"kind", tc.at("kind").str()},
        {"operation_id", claims.at("operation_id").str()},
        {"contract_digest_sha256", claims.at("contract_digest_sha256").str()},
        {"cloud_event_source", tc.at("cloud_event_source").str()},
        {"cloud_event_id", tc.at("cloud_event_id").str()},
    }));
}

std::string effect_state_from_case_or_default(const Json& tc) {
    const std::string supplied = tc.at("effect_state").str();
    return supplied.empty() ? std::string(kPreparedEffectState) : supplied;
}

bool is_replay_printable_token(const std::string& value) {
    if (value.size() < 1 || value.size() > 512) return false;
    for (unsigned char c : value) {
        const bool ok = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                        (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~' || c == ':' || c == '@' || c == '/';
        if (!ok) return false;
    }
    return true;
}

bool is_sender_nonce_for_ledger(const std::string& value) {
    if (value.size() < 16 || value.size() > 128) return false;
    for (unsigned char c : value) {
        const bool ok = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                        (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~';
        if (!ok) return false;
    }
    return true;
}

bool populate_ingress_sender_replay_from_case(const Json& tc, PendingSqliteEntry& row, std::string& reason) {
    const Json& replay = tc.at("ingress_sender_replay");
    if (replay.is_null()) return true;
    if (!replay.is_object()) { reason = "sqlite-wal ingress sender replay evidence must be an object"; return false; }
    row.ingress_sender_replay_required = true;
    row.ingress_sender_replay_format = replay.at("format").str();
    row.ingress_sender_replay_key_sha256 = replay.at("replay_key_sha256").str();
    row.ingress_sender_replay_service_config_sha256 = replay.at("service_config_sha256").str();
    row.ingress_sender_replay_profile_sha256 = replay.at("ingress_profile_sha256").str();
    row.ingress_sender_replay_cache_instance_id = replay.at("sender_replay_cache_instance_id").str();
    row.ingress_sender_replay_proof_kid = replay.at("sender_proof_kid").str();
    row.ingress_sender_replay_principal = replay.at("principal").str();
    row.ingress_sender_replay_nonce = replay.at("nonce").str();
    row.ingress_sender_replay_issued_at_epoch = replay.at("issued_at_epoch").integer(-1);
    row.ingress_sender_replay_observed_at_epoch = replay.at("observed_at_epoch").integer(-1);
    row.ingress_sender_replay_window_seconds = replay.at("replay_window_seconds").integer(-1);
    row.ingress_sender_replay_material_sha256 = replay.at("material_sha256").str();
    if (row.ingress_sender_replay_format != kIngressSenderReplayLedgerFormat) { reason = "sqlite-wal ingress sender replay evidence has unsupported format"; return false; }
    if (!is_lower_hex_sha256(row.ingress_sender_replay_key_sha256) ||
        !is_lower_hex_sha256(row.ingress_sender_replay_service_config_sha256) ||
        !is_lower_hex_sha256(row.ingress_sender_replay_profile_sha256) ||
        !is_lower_hex_sha256(row.ingress_sender_replay_material_sha256)) {
        reason = "sqlite-wal ingress sender replay evidence carries malformed digest material"; return false;
    }
    if (!is_replay_printable_token(row.ingress_sender_replay_cache_instance_id) ||
        !is_replay_printable_token(row.ingress_sender_replay_proof_kid) ||
        row.ingress_sender_replay_principal.empty() || contains_disallowed_security_control(row.ingress_sender_replay_principal) ||
        !is_sender_nonce_for_ledger(row.ingress_sender_replay_nonce)) {
        reason = "sqlite-wal ingress sender replay evidence carries malformed identity or nonce material"; return false;
    }
    if (row.ingress_sender_replay_window_seconds < 1 || row.ingress_sender_replay_window_seconds > 86400 ||
        row.ingress_sender_replay_issued_at_epoch <= 0 || row.ingress_sender_replay_observed_at_epoch <= 0) {
        reason = "sqlite-wal ingress sender replay evidence carries invalid time window material"; return false;
    }
    if (row.ingress_sender_replay_issued_at_epoch < row.ingress_sender_replay_observed_at_epoch - row.ingress_sender_replay_window_seconds ||
        row.ingress_sender_replay_issued_at_epoch > row.ingress_sender_replay_observed_at_epoch + 300) {
        reason = "sqlite-wal ingress sender replay evidence is outside the accepted time window"; return false;
    }
    return true;
}

std::string ingress_sender_replay_nonce_stage_key(const PendingSqliteEntry& row) {
    std::string out = "anonsync-ingress-sender-replay-nonce-unique-v1";
    auto append = [&](const std::string& value) {
        out += std::to_string(value.size());
        out.push_back(':');
        out += value;
    };
    append(row.ingress_sender_replay_service_config_sha256);
    append(row.ingress_sender_replay_profile_sha256);
    append(row.ingress_sender_replay_cache_instance_id);
    append(row.ingress_sender_replay_proof_kid);
    append(row.ingress_sender_replay_nonce);
    return out;
}

void require_nonempty_string_field(const Json& obj, const std::string& field, const std::string& label);
bool json_string_array_contains(const Json& arr, const std::string& needle);

bool is_sha256_or_genesis(const std::string& value) {
    return value == "GENESIS" || is_lower_hex_sha256(value);
}

std::string effect_transition_intent_signing_input(const Json& payload) {
    std::ostringstream in;
    in << kEffectTransitionIntentFormat << "\n"
       << payload.at("intent_id").str() << "\n"
       << payload.at("intent_subject").str() << "\n"
       << payload.at("issued_at").str() << "\n"
       << payload.at("ledger_backend").str() << "\n"
       << payload.at("ledger_instance_id").str() << "\n"
       << payload.at("prepared_ledger_head_hash").str() << "\n"
       << payload.at("effect_transition_previous_hash").str() << "\n"
       << payload.at("effect_idempotency_key").str() << "\n"
       << payload.at("prepared_sequence").integer() << "\n"
       << payload.at("prepared_entry_hash").str() << "\n"
       << payload.at("terminal_state").str() << "\n"
       << payload.at("result_digest_sha256").str() << "\n"
       << payload.at("transition_reason").str() << "\n";
    return in.str();
}

void validate_effect_transition_intent_payload(const Json& payload) {
    if (payload.at("format").str() != kEffectTransitionIntentPayloadFormat) throw std::runtime_error("effect transition intent payload has unsupported format");
    require_nonempty_string_field(payload, "intent_id", "effect transition intent payload");
    require_nonempty_string_field(payload, "intent_subject", "effect transition intent payload");
    require_nonempty_string_field(payload, "issued_at", "effect transition intent payload");
    require_nonempty_string_field(payload, "ledger_backend", "effect transition intent payload");
    require_nonempty_string_field(payload, "ledger_instance_id", "effect transition intent payload");
    require_nonempty_string_field(payload, "prepared_ledger_head_hash", "effect transition intent payload");
    require_nonempty_string_field(payload, "effect_transition_previous_hash", "effect transition intent payload");
    require_nonempty_string_field(payload, "effect_idempotency_key", "effect transition intent payload");
    require_nonempty_string_field(payload, "prepared_entry_hash", "effect transition intent payload");
    require_nonempty_string_field(payload, "terminal_state", "effect transition intent payload");
    require_nonempty_string_field(payload, "result_digest_sha256", "effect transition intent payload");
    require_nonempty_string_field(payload, "transition_reason", "effect transition intent payload");
    if (payload.at("intent_subject").str() != kEffectTransitionIntentSubject) throw std::runtime_error("effect transition intent subject mismatch");
    if (payload.at("ledger_backend").str() != "sqlite-wal") throw std::runtime_error("effect transition intent ledger_backend must be sqlite-wal");
    if (!is_lower_hex_sha256(payload.at("ledger_instance_id").str())) throw std::runtime_error("effect transition intent has invalid ledger_instance_id");
    if (!is_sha256_or_genesis(payload.at("prepared_ledger_head_hash").str())) throw std::runtime_error("effect transition intent has invalid prepared_ledger_head_hash");
    if (!is_sha256_or_genesis(payload.at("effect_transition_previous_hash").str())) throw std::runtime_error("effect transition intent has invalid effect_transition_previous_hash");
    if (!is_lower_hex_sha256(payload.at("effect_idempotency_key").str())) throw std::runtime_error("effect transition intent has invalid effect_idempotency_key");
    if (payload.at("prepared_sequence").integer() <= 0) throw std::runtime_error("effect transition intent requires positive prepared_sequence");
    if (!is_lower_hex_sha256(payload.at("prepared_entry_hash").str())) throw std::runtime_error("effect transition intent has invalid prepared_entry_hash");
    if (!is_terminal_effect_state(payload.at("terminal_state").str())) throw std::runtime_error("effect transition intent has unsupported terminal_state");
    if (!is_lower_hex_sha256(payload.at("result_digest_sha256").str())) throw std::runtime_error("effect transition intent has invalid result_digest_sha256");
    if (payload.at("transition_reason").str().size() > 1024) throw std::runtime_error("effect transition intent transition_reason is too long");
    (void)parse_strict_utc_epoch(payload.at("issued_at").str(), "effect transition intent issued_at");
}

const Json& trusted_effect_transition_signer(const Json& trust, const Json& payload, const std::string& kid, const std::string& alg) {
    if (trust.at("format").str() != kEffectTransitionTrustProfileFormat) throw std::runtime_error("effect transition trust profile has unsupported format");
    require_nonempty_string_field(trust, "verification_time", "effect transition trust profile");
    if (!trust.at("max_intent_age_seconds").is_number() || trust.at("max_intent_age_seconds").integer() <= 0) {
        throw std::runtime_error("effect transition trust profile requires positive max_intent_age_seconds");
    }
    const long long issued_epoch = parse_strict_utc_epoch(payload.at("issued_at").str(), "effect transition intent issued_at");
    const long long verification_epoch = parse_strict_utc_epoch(trust.at("verification_time").str(), "effect transition trust profile verification_time");
    const long long max_age = trust.at("max_intent_age_seconds").integer();
    if (issued_epoch > verification_epoch) throw std::runtime_error("effect transition intent issued after verifier time");
    if (verification_epoch - issued_epoch > max_age) throw std::runtime_error("effect transition intent is older than trust-profile max age");
    if (trust.at("required_intent_subject").str() != kEffectTransitionIntentSubject) throw std::runtime_error("effect transition trust profile subject requirement mismatch");
    if (trust.at("allowed_terminal_states").is_array() && !json_string_array_contains(trust.at("allowed_terminal_states"), payload.at("terminal_state").str())) {
        throw std::runtime_error("effect transition trust profile terminal_state allowlist mismatch");
    }
    const Json& signers = trust.at("trusted_signers");
    if (!signers.is_array()) throw std::runtime_error("effect transition trust profile missing trusted_signers array");
    std::set<std::string> seen_kids;
    const Json* selected = nullptr;
    for (const auto& signer : signers.a) {
        require_nonempty_string_field(signer, "kid", "effect transition trusted signer");
        require_nonempty_string_field(signer, "alg", "effect transition trusted signer");
        const std::string signer_kid = signer.at("kid").str();
        if (!seen_kids.insert(signer_kid).second) throw std::runtime_error("effect transition trust profile has duplicate signer kid: " + signer_kid);
        if (signer_kid == kid && signer.at("alg").str() == alg) {
            if (signer.at("status").str() != "trusted") throw std::runtime_error("effect transition intent signer is not trusted-active: " + kid);
            require_nonempty_string_field(signer, "not_before", "effect transition trusted signer");
            require_nonempty_string_field(signer, "not_after", "effect transition trusted signer");
            const long long not_before = parse_strict_utc_epoch(signer.at("not_before").str(), "effect transition signer not_before");
            const long long not_after = parse_strict_utc_epoch(signer.at("not_after").str(), "effect transition signer not_after");
            if (not_after < not_before) throw std::runtime_error("effect transition signer trust window is inverted");
            if (issued_epoch < not_before) throw std::runtime_error("effect transition intent issued before signer trust window");
            if (issued_epoch > not_after) throw std::runtime_error("effect transition intent issued after signer trust window");
            const Json& jwk = signer.at("jwk");
            if (!jwk.is_object()) throw std::runtime_error("effect transition trusted signer missing jwk object");
            if (jwk.at("kty").str() != "RSA" || jwk.at("alg").str() != "RS256" || jwk.at("kid").str() != kid) {
                throw std::runtime_error("effect transition trusted signer JWK metadata mismatch");
            }
            selected = &signer;
        }
    }
    if (!selected) throw std::runtime_error("effect transition intent signer is not trusted: " + kid);
    return *selected;
}

VerifiedEffectTransitionIntent verify_effect_transition_intent_text_with_trust_profile_text(const std::string& intent_text, const std::string& trust_profile_text) {
    if (intent_text.empty()) throw std::runtime_error("effect transition signed intent text is required");
    if (trust_profile_text.empty()) throw std::runtime_error("effect transition trust profile text is required");
    Json intent = parse_json_text(intent_text);
    Json trust = parse_json_text(trust_profile_text);
    if (intent.at("format").str() != kEffectTransitionIntentFormat) throw std::runtime_error("effect transition intent has unsupported format");
    const Json& payload = intent.at("payload");
    const Json& sig = intent.at("signature");
    if (!payload.is_object() || !sig.is_object()) throw std::runtime_error("effect transition intent missing payload or signature object");
    validate_effect_transition_intent_payload(payload);
    const std::string alg = sig.at("alg").str();
    const std::string kid = sig.at("kid").str();
    if (alg != "RS256" || kid.empty()) throw std::runtime_error("effect transition intent requires RS256 and nonempty kid");
    const Json& signer = trusted_effect_transition_signer(trust, payload, kid, alg);
    const Json& jwk = signer.at("jwk");
    PKeyPtr pkey = jwk_to_pkey(jwk.at("n").str(), jwk.at("e").str());
    std::string verify_reason;
    const std::string signing_input = effect_transition_intent_signing_input(payload);
    if (intent.at("payload_signing_input_sha256").str() != sha256_hex(signing_input)) throw std::runtime_error("effect transition intent signing-input digest mismatch");
    if (!verify_rs256(pkey.get(), signing_input, sig.at("signature_b64url").str(), verify_reason)) throw std::runtime_error("effect transition intent signature verification failed: " + verify_reason);
    VerifiedEffectTransitionIntent out;
    out.intent_id = payload.at("intent_id").str();
    out.issued_at = payload.at("issued_at").str();
    out.ledger_instance_id = payload.at("ledger_instance_id").str();
    out.effect_idempotency_key = payload.at("effect_idempotency_key").str();
    out.prepared_sequence = payload.at("prepared_sequence").integer();
    out.prepared_entry_hash = payload.at("prepared_entry_hash").str();
    out.terminal_state = payload.at("terminal_state").str();
    out.result_digest_sha256 = payload.at("result_digest_sha256").str();
    out.transition_reason = payload.at("transition_reason").str();
    out.prepared_ledger_head_hash = payload.at("prepared_ledger_head_hash").str();
    out.effect_transition_previous_hash = payload.at("effect_transition_previous_hash").str();
    out.signer_kid = kid;
    out.intent_sha256 = sha256_hex(intent_text);
    return out;
}

VerifiedEffectTransitionIntent verify_effect_transition_intent_with_trust_profile_text(const std::string& intent_path, const std::string& trust_profile_text) {
    if (intent_path.empty()) throw std::runtime_error("effect transition signed intent path is required");
    return verify_effect_transition_intent_text_with_trust_profile_text(read_file(intent_path), trust_profile_text);
}

std::string read_effect_transition_trust_profile_with_digest_pin(const std::string& trust_profile_path, const std::string& expected_sha256) {
    if (!is_lower_hex_sha256(expected_sha256)) throw std::runtime_error("effect transition trust-profile digest pin must be lowercase sha256 hex");
    if (trust_profile_path.empty()) throw std::runtime_error("effect transition trust-profile digest pin requires a trust profile path");
    const std::string text = read_file(trust_profile_path);
    if (sha256_hex(text) != expected_sha256) throw std::runtime_error("effect transition trust-profile digest pin mismatch");
    return text;
}

void require_nonempty_string_field(const Json& obj, const std::string& field, const std::string& label) {
    if (!obj.at(field).is_string() || obj.at(field).str().empty()) {
        throw std::runtime_error(label + " missing nonempty string field: " + field);
    }
}

void validate_manifest_payload_profile(const Json& payload) {
    if (payload.at("format").str() != "anonsync-sqlite-snapshot-manifest-payload-v2") throw std::runtime_error("SQLite snapshot manifest payload has unsupported format");
    require_nonempty_string_field(payload, "manifest_revision_id", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "parent_revision", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "manifest_issued_at", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "snapshot_sha256", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "backend_name", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "head_hash", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "expected_revision", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "source_controls_revision", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "manifest_subject", "SQLite snapshot manifest payload");
    require_nonempty_string_field(payload, "durability_ceiling", "SQLite snapshot manifest payload");
    if (payload.at("line_count").integer() <= 0) throw std::runtime_error("SQLite snapshot manifest line_count must be positive");
    if (payload.at("backend_name").str() != "sqlite-wal") throw std::runtime_error("SQLite snapshot manifest backend_name must be sqlite-wal");
    const Json& backend_profile = payload.at("backend_profile");
    if (!backend_profile.is_object()) throw std::runtime_error("SQLite snapshot manifest payload missing backend_profile object");
    if (backend_profile.at("backend_name").str() != "sqlite-wal") throw std::runtime_error("SQLite snapshot manifest backend_profile backend_name mismatch");
    if (backend_profile.at("schema_version").integer() != kSqliteLedgerSchemaVersion) throw std::runtime_error("SQLite snapshot manifest backend_profile schema_version mismatch");
    if (backend_profile.at("entry_material_version").str() != kSqliteLedgerEntryMaterialVersion) throw std::runtime_error("SQLite snapshot manifest backend_profile entry material mismatch");
    if (backend_profile.at("hash_algorithm").str() != "sha256") throw std::runtime_error("SQLite snapshot manifest backend_profile hash algorithm mismatch");
    if (backend_profile.at("commit_protocol").str() != kSqliteLedgerCommitProtocol) throw std::runtime_error("SQLite snapshot manifest backend_profile commit protocol mismatch");
}

const Json& trusted_snapshot_signer(const Json& trust, const Json& manifest, const Json& payload, const std::string& kid, const std::string& alg) {
    if (trust.at("format").str() != "anonsync-sqlite-snapshot-trust-profile-v3") {
        throw std::runtime_error("SQLite snapshot trust profile has unsupported format");
    }
    require_nonempty_string_field(trust, "verification_time", "SQLite snapshot trust profile");
    if (!trust.at("max_manifest_age_seconds").is_number() || trust.at("max_manifest_age_seconds").integer() <= 0) {
        throw std::runtime_error("SQLite snapshot trust profile requires positive max_manifest_age_seconds");
    }
    const long long issued_epoch = parse_strict_utc_epoch(payload.at("manifest_issued_at").str(), "SQLite snapshot manifest issued-at");
    const long long verification_epoch = parse_strict_utc_epoch(trust.at("verification_time").str(), "SQLite snapshot trust profile verification_time");
    const long long max_age = trust.at("max_manifest_age_seconds").integer();
    if (issued_epoch > verification_epoch) throw std::runtime_error("SQLite snapshot manifest issued after verifier time");
    if (verification_epoch - issued_epoch > max_age) throw std::runtime_error("SQLite snapshot manifest is older than trust-profile max age");

    if (!trust.at("required_backend_name").is_string() || trust.at("required_backend_name").str().empty()) {
        throw std::runtime_error("SQLite snapshot trust profile missing required_backend_name");
    }
    if (!trust.at("required_manifest_subject").is_string() || trust.at("required_manifest_subject").str().empty()) {
        throw std::runtime_error("SQLite snapshot trust profile missing required_manifest_subject");
    }
    if (!manifest.at("revision_id").is_string() || manifest.at("revision_id").str().empty()) {
        throw std::runtime_error("SQLite snapshot manifest missing revision_id");
    }
    if (!manifest.at("parent_revision").is_string() || manifest.at("parent_revision").str().empty()) {
        throw std::runtime_error("SQLite snapshot manifest missing parent_revision");
    }
    if (manifest.at("revision_id").str() != payload.at("manifest_revision_id").str()) {
        throw std::runtime_error("SQLite snapshot manifest outer revision_id is not bound to signed payload manifest_revision_id");
    }
    if (manifest.at("parent_revision").str() != payload.at("parent_revision").str()) {
        throw std::runtime_error("SQLite snapshot manifest outer parent_revision is not bound to signed payload parent_revision");
    }

    const Json& signers = trust.at("trusted_signers");
    if (!signers.is_array()) throw std::runtime_error("SQLite snapshot trust profile missing trusted_signers array");
    std::set<std::string> seen_kids;
    const Json* selected = nullptr;
    for (const auto& signer : signers.a) {
        require_nonempty_string_field(signer, "kid", "SQLite snapshot trust signer");
        require_nonempty_string_field(signer, "alg", "SQLite snapshot trust signer");
        const std::string signer_kid = signer.at("kid").str();
        if (!seen_kids.insert(signer_kid).second) {
            throw std::runtime_error("SQLite snapshot trust profile has duplicate signer kid: " + signer_kid);
        }
        if (signer_kid == kid && signer.at("alg").str() == alg) {
            if (signer.at("status").str() != "trusted") {
                throw std::runtime_error("SQLite snapshot manifest signer is not trusted-active: " + kid);
            }
            require_nonempty_string_field(signer, "not_before", "SQLite snapshot trust signer");
            require_nonempty_string_field(signer, "not_after", "SQLite snapshot trust signer");
            const long long not_before = parse_strict_utc_epoch(signer.at("not_before").str(), "SQLite snapshot restore-root not_before");
            const long long not_after = parse_strict_utc_epoch(signer.at("not_after").str(), "SQLite snapshot restore-root not_after");
            if (not_after < not_before) throw std::runtime_error("SQLite snapshot restore-root trust window is inverted");
            if (issued_epoch < not_before) throw std::runtime_error("SQLite snapshot manifest issued before restore-root trust window");
            if (issued_epoch > not_after) throw std::runtime_error("SQLite snapshot manifest issued after restore-root trust window");
            const Json& jwk = signer.at("jwk");
            if (!jwk.is_object()) throw std::runtime_error("SQLite snapshot trusted signer missing jwk object");
            if (jwk.at("kty").str() != "RSA" || jwk.at("alg").str() != "RS256" || jwk.at("kid").str() != kid) {
                throw std::runtime_error("SQLite snapshot trusted signer JWK metadata mismatch");
            }
            selected = &signer;
        }
    }
    if (!selected) throw std::runtime_error("SQLite snapshot manifest signer is not trusted: " + kid);

    if (payload.at("backend_name").str() != trust.at("required_backend_name").str()) {
        throw std::runtime_error("SQLite snapshot trust profile backend requirement mismatch");
    }
    if (payload.at("manifest_subject").str() != trust.at("required_manifest_subject").str()) {
        throw std::runtime_error("SQLite snapshot trust profile subject requirement mismatch");
    }
    if (trust.at("allowed_expected_revisions").is_array() && !json_string_array_contains(trust.at("allowed_expected_revisions"), payload.at("expected_revision").str())) {
        throw std::runtime_error("SQLite snapshot trust profile expected_revision allowlist mismatch");
    }
    if (trust.at("allowed_source_controls_revisions").is_array() && !json_string_array_contains(trust.at("allowed_source_controls_revisions"), payload.at("source_controls_revision").str())) {
        throw std::runtime_error("SQLite snapshot trust profile source_controls_revision allowlist mismatch");
    }
    if (trust.at("allowed_manifest_revisions").is_array() && !json_string_array_contains(trust.at("allowed_manifest_revisions"), payload.at("manifest_revision_id").str())) {
        throw std::runtime_error("SQLite snapshot trust profile manifest revision allowlist mismatch");
    }
    return *selected;
}


std::string read_trust_profile_with_digest_pin_impl(const std::string& trust_profile_path, const std::string& expected_sha256) {
    if (!is_lower_hex_sha256(expected_sha256)) {
        throw std::runtime_error("SQLite snapshot trust-profile digest pin must be lowercase sha256 hex");
    }
    if (trust_profile_path.empty()) {
        throw std::runtime_error("SQLite snapshot trust-profile digest pin requires a trust profile path");
    }
    const std::string trust_profile_text = read_file(trust_profile_path);
    const std::string actual = sha256_hex(trust_profile_text);
    if (actual != expected_sha256) {
        throw std::runtime_error("SQLite snapshot trust-profile digest pin mismatch");
    }
    return trust_profile_text;
}


void apply_untrusted_snapshot_readonly_profile(sqlite3* db, const std::string& label) {
#ifdef SQLITE_DBCONFIG_DEFENSIVE
    int defensive_out = 0;
    if (sqlite3_db_config(db, SQLITE_DBCONFIG_DEFENSIVE, 1, &defensive_out) != SQLITE_OK) {
        sqlite_throw(db, label + " could not enable SQLITE_DBCONFIG_DEFENSIVE");
    }
#endif
#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
    int trusted_schema_out = 0;
    if (sqlite3_db_config(db, SQLITE_DBCONFIG_TRUSTED_SCHEMA, 0, &trusted_schema_out) != SQLITE_OK) {
        sqlite_throw(db, label + " could not disable trusted_schema");
    }
#endif
#ifdef SQLITE_LIMIT_ATTACHED
    sqlite3_limit(db, SQLITE_LIMIT_ATTACHED, 0);
#endif
#ifdef SQLITE_LIMIT_TRIGGER_DEPTH
    sqlite3_limit(db, SQLITE_LIMIT_TRIGGER_DEPTH, 0);
#endif
#ifdef SQLITE_LIMIT_VARIABLE_NUMBER
    sqlite3_limit(db, SQLITE_LIMIT_VARIABLE_NUMBER, 64);
#endif
#ifdef SQLITE_LIMIT_SQL_LENGTH
    sqlite3_limit(db, SQLITE_LIMIT_SQL_LENGTH, 1024 * 1024);
#endif
    sqlite_exec_or_throw(db, "PRAGMA query_only=ON;", label + " could not enable query_only");
    sqlite_exec_or_throw(db, "PRAGMA trusted_schema=OFF;", label + " could not disable trusted_schema pragma");
    sqlite_exec_or_throw(db, "PRAGMA foreign_keys=ON;", label + " could not enable foreign_keys");
}

std::set<std::string> table_columns(sqlite3* db, const std::string& table_name) {
    std::set<std::string> columns;
    Stmt stmt(db, "PRAGMA table_info('" + table_name + "');", "sqlite-wal read-only snapshot table_info failed for " + table_name);
    while (true) {
        int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) sqlite_throw(db, "sqlite-wal read-only snapshot table_info step failed for " + table_name);
        columns.insert(column_text(stmt.stmt, 1));
    }
    return columns;
}

void require_exact_columns(sqlite3* db, const std::string& table_name, const std::set<std::string>& expected) {
    const std::set<std::string> actual = table_columns(db, table_name);
    if (actual != expected) {
        throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected column set for table " + table_name);
    }
}

void verify_readonly_snapshot_schema(sqlite3* db) {
    std::set<std::string> required_objects = {
        "table:metadata",
        "table:ledger_entries",
        "table:backend_profile",
        "table:ledger_identity",
        "table:effect_transition_metadata",
        "table:effect_transitions",
        "table:effect_outbox",
        "table:ingress_sender_replay_cache",
        "index:ingress_sender_replay_expiry",
        "index:ingress_sender_replay_nonce_unique",
        "index:ledger_async_event_identity_unique",
        "index:ledger_effect_prepared_entry_evidence_unique",
        "index:effect_transitions_key_unique",
        "index:effect_transitions_intent_id_unique"
    };
    std::set<std::string> seen_objects;
    Stmt stmt(db,
              "SELECT type, name, tbl_name, COALESCE(sql, '') FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name;",
              "sqlite-wal read-only snapshot schema select prepare failed");
    while (true) {
        int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) sqlite_throw(db, "sqlite-wal read-only snapshot schema select step failed");
        const std::string type = column_text(stmt.stmt, 0);
        const std::string name = column_text(stmt.stmt, 1);
        const std::string tbl_name = column_text(stmt.stmt, 2);
        const std::string sql = column_text(stmt.stmt, 3);
        const std::string object_key = type + ":" + name;
        if (required_objects.find(object_key) == required_objects.end()) {
            throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected schema object: " + type + ":" + name);
        }
        if (type == "table") {
            if (tbl_name != name) throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected table/tbl_name mismatch for " + name);
            const std::string lower_sql = ascii_lower(sql);
            if (lower_sql.find("create virtual table") != std::string::npos) {
                throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected virtual table schema for " + name);
            }
        } else if (type == "index") {
            const std::string lower_sql = ascii_lower(sql);
            if (name == "ledger_async_event_identity_unique") {
                if (tbl_name != "ledger_entries") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create unique index") == std::string::npos ||
                    lower_sql.find("cloud_event_source") == std::string::npos ||
                    lower_sql.find("cloud_event_id") == std::string::npos ||
                    lower_sql.find("where") == std::string::npos ||
                    lower_sql.find("asyncapi") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed async event identity index");
                }
            } else if (name == "ledger_effect_prepared_entry_evidence_unique") {
                if (tbl_name != "ledger_entries") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create unique index") == std::string::npos ||
                    lower_sql.find("sequence") == std::string::npos ||
                    lower_sql.find("entry_hash") == std::string::npos ||
                    lower_sql.find("effect_idempotency_key") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed prepared-effect evidence index");
                }
            } else if (name == "effect_transitions_key_unique") {
                if (tbl_name != "effect_transitions") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create unique index") == std::string::npos ||
                    lower_sql.find("effect_idempotency_key") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed effect transition key index");
                }
            } else if (name == "effect_transitions_intent_id_unique") {
                if (tbl_name != "effect_transitions") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create unique index") == std::string::npos ||
                    lower_sql.find("transition_intent_id") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed effect transition intent id index");
                }
            } else if (name == "ingress_sender_replay_nonce_unique") {
                if (tbl_name != "ingress_sender_replay_cache") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create unique index") == std::string::npos ||
                    lower_sql.find("service_config_sha256") == std::string::npos ||
                    lower_sql.find("ingress_profile_sha256") == std::string::npos ||
                    lower_sql.find("sender_replay_cache_instance_id") == std::string::npos ||
                    lower_sql.find("sender_proof_kid") == std::string::npos ||
                    lower_sql.find("nonce") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed ingress sender replay nonce index");
                }
            } else if (name == "ingress_sender_replay_expiry") {
                if (tbl_name != "ingress_sender_replay_cache") {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
                }
                if (lower_sql.find("create index") == std::string::npos || lower_sql.find("issued_at_epoch") == std::string::npos) {
                    throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected malformed ingress sender replay expiry index");
                }
            } else {
                throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected unexpected index target: " + name);
            }
        } else {
            throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected non-table/index schema object: " + type + ":" + name);
        }
        if (!seen_objects.insert(object_key).second) {
            throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected duplicate schema object: " + object_key);
        }
    }
    if (seen_objects != required_objects) {
        throw std::runtime_error("sqlite-wal read-only snapshot verifier rejected missing required schema object");
    }
    require_exact_columns(db, "metadata", {"id", "line_count", "head_hash"});
    require_exact_columns(db, "ledger_entries", {"sequence", "previous_hash", "entry_hash", "case_id", "kind", "operation_id", "contract_digest_sha256", "jti", "action", "cloud_event_source", "cloud_event_id", "effect_idempotency_key", "effect_state"});
    require_exact_columns(db, "backend_profile", {"id", "backend_name", "schema_version", "hash_algorithm", "entry_material_version", "commit_protocol"});
    require_exact_columns(db, "ledger_identity", {"id", "ledger_instance_id"});
    require_exact_columns(db, "effect_transition_metadata", {"id", "line_count", "head_hash"});
    require_exact_columns(db, "effect_transitions", {"sequence", "previous_hash", "transition_hash", "ledger_instance_id", "effect_idempotency_key", "prepared_sequence", "prepared_entry_hash", "terminal_state", "result_digest_sha256", "transition_reason", "transition_intent_id", "transition_intent_signer_kid", "transition_intent_sha256"});
    require_exact_columns(db, "effect_outbox", {"effect_idempotency_key", "prepared_sequence", "prepared_entry_hash", "outbox_state", "dispatch_attempts", "worker_claim_id", "worker_id", "claimed_at_epoch", "lease_expires_at_epoch", "last_result_digest_sha256", "updated_at_sequence"});
    require_exact_columns(db, "ingress_sender_replay_cache", {"replay_key_sha256", "format", "service_config_sha256", "ingress_profile_sha256", "sender_replay_cache_instance_id", "sender_proof_kid", "principal", "nonce", "issued_at_epoch", "observed_at_epoch", "replay_window_seconds", "material_sha256", "prepared_sequence", "prepared_entry_hash", "effect_idempotency_key"});
}

ReplayLedgerStats verify_open_sqlite_ledger_snapshot_readonly(sqlite3* db, const std::string& label) {
    if (!db) throw std::runtime_error(label + " requires an open read-only database handle");
    sqlite3_busy_timeout(db, 1000);
    apply_untrusted_snapshot_readonly_profile(db, label);
    verify_readonly_snapshot_schema(db);
    long long integrity_checks = 0;
    long long profile_checks = 0;
    {
        Stmt stmt(db, "PRAGMA integrity_check;", label + " integrity_check prepare failed");
        int rc = sqlite3_step(stmt.stmt);
        if (rc != SQLITE_ROW) throw std::runtime_error(label + " integrity_check returned no row");
        const std::string verdict = column_text(stmt.stmt, 0);
        if (verdict != "ok") throw std::runtime_error(label + " integrity_check failed: " + verdict);
        integrity_checks++;
    }
    {
        Stmt stmt(db, "SELECT backend_name, schema_version, hash_algorithm, entry_material_version, commit_protocol FROM backend_profile WHERE id=1", label + " backend_profile prepare failed");
        int rc = sqlite3_step(stmt.stmt);
        if (rc != SQLITE_ROW) throw std::runtime_error(label + " backend_profile row is absent");
        const std::string backend = column_text(stmt.stmt, 0);
        const long long schema_version = sqlite3_column_int64(stmt.stmt, 1);
        const std::string hash_algorithm = column_text(stmt.stmt, 2);
        const std::string material_version = column_text(stmt.stmt, 3);
        const std::string commit_protocol = column_text(stmt.stmt, 4);
        if (backend != "sqlite-wal" || schema_version != kSqliteLedgerSchemaVersion || hash_algorithm != "sha256" || material_version != kSqliteLedgerEntryMaterialVersion || commit_protocol != kSqliteLedgerCommitProtocol) {
            throw std::runtime_error(label + " backend_profile mismatch");
        }
        profile_checks++;
    }
    const std::string ledger_instance_id = query_ledger_instance_id(db, label);
    std::unordered_set<std::string> jtis;
    std::unordered_set<std::string> event_identities;
    std::unordered_map<std::string, PreparedEffectReference> prepared_effect_refs;
    long long loaded_entries = 0;
    long long expected_sequence = 1;
    std::string previous = "GENESIS";
    {
        Stmt stmt(db, "SELECT sequence, previous_hash, entry_hash, case_id, kind, operation_id, contract_digest_sha256, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state FROM ledger_entries ORDER BY sequence", label + " ledger_entries prepare failed");
        while (true) {
            int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) sqlite_throw(db, label + " ledger_entries step failed");
            const long long sequence = sqlite3_column_int64(stmt.stmt, 0);
            const std::string previous_hash = column_text(stmt.stmt, 1);
            const std::string entry_hash = column_text(stmt.stmt, 2);
            const std::string case_id = column_text(stmt.stmt, 3);
            const std::string kind = column_text(stmt.stmt, 4);
            const std::string operation_id = column_text(stmt.stmt, 5);
            const std::string contract_digest = column_text(stmt.stmt, 6);
            const std::string jti = column_text(stmt.stmt, 7);
            const std::string action = column_text(stmt.stmt, 8);
            const std::string cloud_event_source = column_text(stmt.stmt, 9);
            const std::string cloud_event_id = column_text(stmt.stmt, 10);
            const std::string effect_idempotency_key = column_text(stmt.stmt, 11);
            const std::string effect_state = column_text(stmt.stmt, 12);
            if (sequence != expected_sequence) throw std::runtime_error(label + " sequence gap or rollback detected");
            if (previous_hash != previous) throw std::runtime_error(label + " previous hash chain mismatch");
            if (kind != "openapi" && kind != "asyncapi") throw std::runtime_error(label + " row has invalid kind");
            if (action != "allow" && action != "accept") throw std::runtime_error(label + " row has invalid action");
            if (operation_id.empty()) throw std::runtime_error(label + " row missing verified operation_id");
            if (!is_lower_hex_sha256(contract_digest)) throw std::runtime_error(label + " row has invalid verified contract_digest_sha256");
            if (jti.empty()) throw std::runtime_error(label + " row missing nonempty jti");
            if (!jtis.insert(jti).second) throw std::runtime_error(label + " duplicate jti detected during read-only verification");
            if (!is_lower_hex_sha256(effect_idempotency_key)) throw std::runtime_error(label + " row missing valid effect_idempotency_key");
            if (effect_state != kPreparedEffectState) throw std::runtime_error(label + " row has unsupported effect_state");
            if (!prepared_effect_refs.emplace(effect_idempotency_key, PreparedEffectReference{sequence, entry_hash, effect_idempotency_key}).second) throw std::runtime_error(label + " duplicate effect_idempotency_key detected during read-only verification");
            if (kind == "asyncapi") {
                const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
                if (event_key.empty()) throw std::runtime_error(label + " async row missing CloudEvents source/id identity");
                if (!event_identities.insert(event_key).second) throw std::runtime_error(label + " duplicate CloudEvents source/id identity detected during read-only verification");
            }
            const std::string expected_hash = ReplayLedger::compute_entry_hash(sequence, previous_hash, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state);
            if (entry_hash != expected_hash) throw std::runtime_error(label + " entry hash mismatch");
            previous = entry_hash;
            expected_sequence++;
            loaded_entries++;
        }
    }
    {
        Stmt meta(db, "SELECT line_count, head_hash FROM metadata WHERE id=1", label + " metadata prepare failed");
        int rc = sqlite3_step(meta.stmt);
        if (rc != SQLITE_ROW) throw std::runtime_error(label + " metadata row is absent");
        const long long meta_count = sqlite3_column_int64(meta.stmt, 0);
        const std::string meta_head = column_text(meta.stmt, 1);
        if (meta_count != loaded_entries || meta_head != previous) throw std::runtime_error(label + " metadata does not match verified chain");
    }
    std::unordered_set<std::string> transitioned_effect_keys;
    std::unordered_set<std::string> transitioned_intent_ids;
    std::unordered_map<std::string, std::string> transitioned_effect_states;
    std::unordered_map<std::string, std::string> transitioned_effect_digests;
    std::unordered_map<std::string, long long> transitioned_effect_sequences;
    long long transition_count = 0;
    long long expected_transition_sequence = 1;
    std::string transition_previous = "GENESIS";
    std::unordered_set<std::string> committed_transition_intent_ids;
    {
        Stmt stmt(db, "SELECT sequence, previous_hash, transition_hash, ledger_instance_id, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256 FROM effect_transitions ORDER BY sequence", label + " effect_transitions prepare failed");
        while (true) {
            int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) sqlite_throw(db, label + " effect_transitions step failed");
            const long long sequence = sqlite3_column_int64(stmt.stmt, 0);
            const std::string previous_hash = column_text(stmt.stmt, 1);
            const std::string transition_hash = column_text(stmt.stmt, 2);
            const std::string transition_ledger_instance_id = column_text(stmt.stmt, 3);
            const std::string effect_idempotency_key = column_text(stmt.stmt, 4);
            const long long prepared_sequence = sqlite3_column_int64(stmt.stmt, 5);
            const std::string prepared_entry_hash = column_text(stmt.stmt, 6);
            const std::string terminal_state = column_text(stmt.stmt, 7);
            const std::string result_digest_sha256 = column_text(stmt.stmt, 8);
            const std::string transition_reason = column_text(stmt.stmt, 9);
            const std::string transition_intent_id = column_text(stmt.stmt, 10);
            const std::string transition_intent_signer_kid = column_text(stmt.stmt, 11);
            const std::string transition_intent_sha256 = column_text(stmt.stmt, 12);
            if (sequence != expected_transition_sequence) throw std::runtime_error(label + " effect transition sequence gap or rollback detected");
            if (previous_hash != transition_previous) throw std::runtime_error(label + " effect transition previous hash mismatch");
            if (transition_ledger_instance_id != ledger_instance_id) throw std::runtime_error(label + " effect transition ledger_instance_id does not match ledger identity");
            if (!is_lower_hex_sha256(effect_idempotency_key)) throw std::runtime_error(label + " effect transition has invalid effect_idempotency_key");
            auto ref_it = prepared_effect_refs.find(effect_idempotency_key);
            if (ref_it == prepared_effect_refs.end()) throw std::runtime_error(label + " effect transition references unknown prepared effect");
            if (prepared_sequence <= 0 || !is_lower_hex_sha256(prepared_entry_hash)) throw std::runtime_error(label + " effect transition has invalid prepared-effect evidence binding");
            if (ref_it->second.sequence != prepared_sequence || ref_it->second.entry_hash != prepared_entry_hash) throw std::runtime_error(label + " effect transition prepared-effect evidence does not match ledger row");
            if (!is_terminal_effect_state(terminal_state)) throw std::runtime_error(label + " effect transition has unsupported terminal state");
            if (!is_lower_hex_sha256(result_digest_sha256)) throw std::runtime_error(label + " effect transition has invalid result digest");
            if (transition_intent_id.empty() || transition_intent_signer_kid.empty()) throw std::runtime_error(label + " effect transition missing signed intent metadata");
            if (!is_lower_hex_sha256(transition_intent_sha256)) throw std::runtime_error(label + " effect transition has invalid signed intent digest");
            if (!transitioned_effect_keys.insert(effect_idempotency_key).second) throw std::runtime_error(label + " duplicate effect transition detected during read-only verification");
            transitioned_effect_states[effect_idempotency_key] = terminal_state;
            transitioned_effect_digests[effect_idempotency_key] = result_digest_sha256;
            transitioned_effect_sequences[effect_idempotency_key] = sequence;
            if (!transitioned_intent_ids.insert(transition_intent_id).second) throw std::runtime_error(label + " duplicate effect transition intent id detected during read-only verification");
            const std::string expected_hash = compute_effect_transition_hash(sequence, previous_hash, ledger_instance_id, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256);
            if (transition_hash != expected_hash) throw std::runtime_error(label + " effect transition hash mismatch");
            transition_previous = transition_hash;
            expected_transition_sequence++;
            transition_count++;
        }
    }
    {
        Stmt meta(db, "SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1", label + " effect_transition_metadata prepare failed");
        int rc = sqlite3_step(meta.stmt);
        if (rc != SQLITE_ROW) throw std::runtime_error(label + " effect_transition_metadata row is absent");
        const long long meta_count = sqlite3_column_int64(meta.stmt, 0);
        const std::string meta_head = column_text(meta.stmt, 1);
        if (meta_count != transition_count || meta_head != transition_previous) throw std::runtime_error(label + " effect transition metadata does not match verified chain");
    }
    long long outbox_count = 0;
    long long outbox_reserved = 0;
    long long outbox_inflight = 0;
    long long outbox_terminal = 0;
    std::unordered_set<std::string> outbox_keys;
    {
        Stmt stmt(db, "SELECT effect_idempotency_key, prepared_sequence, prepared_entry_hash, outbox_state, dispatch_attempts, worker_claim_id, worker_id, claimed_at_epoch, lease_expires_at_epoch, last_result_digest_sha256, updated_at_sequence FROM effect_outbox ORDER BY prepared_sequence", label + " effect_outbox prepare failed");
        while (true) {
            int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) sqlite_throw(db, label + " effect_outbox step failed");
            const std::string effect_idempotency_key = column_text(stmt.stmt, 0);
            const long long prepared_sequence = sqlite3_column_int64(stmt.stmt, 1);
            const std::string prepared_entry_hash = column_text(stmt.stmt, 2);
            const std::string outbox_state = column_text(stmt.stmt, 3);
            const long long dispatch_attempts = sqlite3_column_int64(stmt.stmt, 4);
            const std::string worker_claim_id = column_text(stmt.stmt, 5);
            const std::string worker_id = column_text(stmt.stmt, 6);
            const long long claimed_at_epoch = sqlite3_column_int64(stmt.stmt, 7);
            const long long lease_expires_at_epoch = sqlite3_column_int64(stmt.stmt, 8);
            const std::string last_result_digest_sha256 = column_text(stmt.stmt, 9);
            const long long updated_at_sequence = sqlite3_column_int64(stmt.stmt, 10);
            if (!is_lower_hex_sha256(effect_idempotency_key)) throw std::runtime_error(label + " effect outbox has invalid effect_idempotency_key");
            auto ref_it = prepared_effect_refs.find(effect_idempotency_key);
            if (ref_it == prepared_effect_refs.end()) throw std::runtime_error(label + " effect outbox references unknown prepared effect");
            if (prepared_sequence != ref_it->second.sequence || prepared_entry_hash != ref_it->second.entry_hash) throw std::runtime_error(label + " effect outbox prepared evidence does not match ledger row");
            if (!outbox_keys.insert(effect_idempotency_key).second) throw std::runtime_error(label + " duplicate effect outbox key detected during read-only verification");
            if (!is_effect_outbox_state(outbox_state)) throw std::runtime_error(label + " effect outbox has unsupported state");
            if (dispatch_attempts < 0) throw std::runtime_error(label + " effect outbox has invalid dispatch attempt count");
            const auto state_it = transitioned_effect_states.find(effect_idempotency_key);
            if (outbox_state == kEffectOutboxReservedState) {
                if (state_it != transitioned_effect_states.end()) throw std::runtime_error(label + " effect outbox remained reserved after terminal transition");
                if (dispatch_attempts != 0) throw std::runtime_error(label + " reserved effect outbox has nonzero dispatch attempts");
                if (!worker_claim_id.empty() || !worker_id.empty() || claimed_at_epoch != 0 || lease_expires_at_epoch != 0) throw std::runtime_error(label + " reserved effect outbox carries worker claim metadata");
                if (!last_result_digest_sha256.empty()) throw std::runtime_error(label + " reserved effect outbox carries terminal result digest");
                if (updated_at_sequence != prepared_sequence) throw std::runtime_error(label + " reserved effect outbox update sequence does not match prepared sequence");
                outbox_reserved++;
            } else if (outbox_state == kEffectOutboxInflightState) {
                if (state_it != transitioned_effect_states.end()) throw std::runtime_error(label + " effect outbox remained inflight after terminal transition");
                if (dispatch_attempts <= 0) throw std::runtime_error(label + " inflight effect outbox has no dispatch attempt");
                if (!is_lower_hex_sha256(worker_claim_id)) throw std::runtime_error(label + " inflight effect outbox has invalid worker claim id");
                if (worker_id.empty() || worker_id.size() > 128 || contains_disallowed_security_control(worker_id)) throw std::runtime_error(label + " inflight effect outbox has invalid worker id");
                if (claimed_at_epoch <= 0 || lease_expires_at_epoch < claimed_at_epoch) throw std::runtime_error(label + " inflight effect outbox has invalid lease timestamps");
                if (!last_result_digest_sha256.empty()) throw std::runtime_error(label + " inflight effect outbox carries terminal result digest");
                if (updated_at_sequence != prepared_sequence) throw std::runtime_error(label + " inflight effect outbox update sequence does not match prepared sequence");
                outbox_inflight++;
            } else {
                if (state_it == transitioned_effect_states.end()) throw std::runtime_error(label + " terminal effect outbox lacks matching transition row");
                if (outbox_state != state_it->second) throw std::runtime_error(label + " terminal effect outbox state does not match transition row");
                if (last_result_digest_sha256 != transitioned_effect_digests[effect_idempotency_key]) throw std::runtime_error(label + " terminal effect outbox result digest does not match transition row");
                if (updated_at_sequence != transitioned_effect_sequences[effect_idempotency_key]) throw std::runtime_error(label + " terminal effect outbox update sequence does not match transition sequence");
                if (!worker_claim_id.empty() && !is_lower_hex_sha256(worker_claim_id)) throw std::runtime_error(label + " terminal effect outbox has invalid worker claim id");
                if (!worker_id.empty() && (worker_id.size() > 128 || contains_disallowed_security_control(worker_id))) throw std::runtime_error(label + " terminal effect outbox has invalid worker id");
                if ((worker_claim_id.empty() || worker_id.empty()) && (claimed_at_epoch != 0 || lease_expires_at_epoch != 0)) throw std::runtime_error(label + " terminal effect outbox has partial worker lease metadata");
                if (!worker_claim_id.empty() && (claimed_at_epoch <= 0 || lease_expires_at_epoch < claimed_at_epoch || dispatch_attempts <= 0)) throw std::runtime_error(label + " terminal effect outbox has invalid preserved worker lease metadata");
                outbox_terminal++;
            }
            outbox_count++;
        }
    }
    if (outbox_count != loaded_entries || static_cast<long long>(outbox_keys.size()) != loaded_entries) throw std::runtime_error(label + " effect outbox does not cover every prepared ledger entry exactly once");
    ReplayLedgerStats st;
    st.backend_name = "sqlite-wal-readonly-snapshot-verifier";
    st.loaded_entries = loaded_entries;
    st.sqlite_integrity_checks = integrity_checks;
    st.sqlite_profile_checks = profile_checks;
    st.sqlite_snapshot_verifications = 1;
    st.durable_line_count = loaded_entries;
    st.durable_head_hash = previous;
    st.effect_terminal_transitions = transition_count;
    st.effect_transition_line_count = transition_count;
    st.effect_transition_head_hash = transition_previous;
    st.effect_outbox_reserved = outbox_reserved;
    st.effect_outbox_inflight = outbox_inflight;
    st.effect_outbox_terminal = outbox_terminal;
    return st;
}

ReplayLedgerStats verify_sqlite_ledger_snapshot_readonly(const std::string& snapshot_path, const std::string& label) {
    if (snapshot_path.empty()) throw std::runtime_error(label + " requires a nonempty snapshot path");
    reject_sqlite_family_symlinks(snapshot_path);
    sqlite3* db = nullptr;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    db = sqlite_open_or_throw(snapshot_path, flags, label + " open read-only failed");
    try {
        ReplayLedgerStats st = verify_open_sqlite_ledger_snapshot_readonly(db, label);
        sqlite_close_or_throw(db, label + " close read-only failed");
        return st;
    } catch (...) {
        sqlite_close_best_effort(db);
        throw;
    }
}

struct PendingEffectReportRow {
    long long sequence = 0;
    std::string entry_hash;
    std::string case_id;
    std::string kind;
    std::string operation_id;
    std::string contract_digest_sha256;
    std::string action;
    std::string cloud_event_source;
    std::string cloud_event_id;
    std::string effect_idempotency_key;
    std::string outbox_state;
    std::string worker_claim_id;
    std::string worker_id;
    long long dispatch_attempts = 0;
    long long claimed_at_epoch = 0;
    long long lease_expires_at_epoch = 0;
};

std::string sqlite_effect_pending_report_json(const std::string& ledger_path) {
    if (ledger_path.empty()) throw std::runtime_error("sqlite-wal effect pending report requires a nonempty ledger path");
    reject_sqlite_family_symlinks(ledger_path);
    sqlite3* db = nullptr;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    db = sqlite_open_or_throw(ledger_path, flags, "sqlite-wal effect pending report open read-only failed");
    try {
        ReplayLedgerStats verified = verify_open_sqlite_ledger_snapshot_readonly(db, "sqlite-wal effect pending report read-only verifier");
        std::vector<PendingEffectReportRow> rows;
        {
            Stmt stmt(db,
                      "SELECT e.sequence, e.entry_hash, e.case_id, e.kind, e.operation_id, e.contract_digest_sha256, e.action, e.cloud_event_source, e.cloud_event_id, e.effect_idempotency_key, o.outbox_state, o.worker_claim_id, o.worker_id, o.dispatch_attempts, o.claimed_at_epoch, o.lease_expires_at_epoch "
                      "FROM ledger_entries e JOIN effect_outbox o ON o.effect_idempotency_key=e.effect_idempotency_key "
                      "LEFT JOIN effect_transitions t ON t.effect_idempotency_key=e.effect_idempotency_key "
                      "WHERE t.effect_idempotency_key IS NULL AND o.outbox_state IN ('reserved','inflight') ORDER BY e.sequence",
                      "sqlite-wal effect pending report query prepare failed");
            while (true) {
                int rc = sqlite3_step(stmt.stmt);
                if (rc == SQLITE_DONE) break;
                if (rc != SQLITE_ROW) sqlite_throw(db, "sqlite-wal effect pending report query step failed");
                PendingEffectReportRow row;
                row.sequence = sqlite3_column_int64(stmt.stmt, 0);
                row.entry_hash = column_text(stmt.stmt, 1);
                row.case_id = column_text(stmt.stmt, 2);
                row.kind = column_text(stmt.stmt, 3);
                row.operation_id = column_text(stmt.stmt, 4);
                row.contract_digest_sha256 = column_text(stmt.stmt, 5);
                row.action = column_text(stmt.stmt, 6);
                row.cloud_event_source = column_text(stmt.stmt, 7);
                row.cloud_event_id = column_text(stmt.stmt, 8);
                row.effect_idempotency_key = column_text(stmt.stmt, 9);
                row.outbox_state = column_text(stmt.stmt, 10);
                row.worker_claim_id = column_text(stmt.stmt, 11);
                row.worker_id = column_text(stmt.stmt, 12);
                row.dispatch_attempts = sqlite3_column_int64(stmt.stmt, 13);
                row.claimed_at_epoch = sqlite3_column_int64(stmt.stmt, 14);
                row.lease_expires_at_epoch = sqlite3_column_int64(stmt.stmt, 15);
                rows.push_back(std::move(row));
            }
        }
        const std::string report_ledger_instance_id = query_ledger_instance_id(db, "sqlite-wal effect pending report");
        sqlite_close_or_throw(db, "sqlite-wal effect pending report close read-only failed");
        std::ostringstream out;
        out << "{\n"
            << "  \"format\": \"anonsync-sqlite-effect-pending-report-v5-outbox-claim\",\n"
            << "  \"backend_name\": \"sqlite-wal\",\n"
            << "  \"revision_id\": \"rev0634\",\n"
            << "  \"ledger_instance_id\": \"" << json_escape(report_ledger_instance_id) << "\",\n"
            << "  \"verification\": \"single-open read-only verifier with schema/hash-chain/effect-transition/outbox checks\",\n"
            << "  \"outbox_format\": \"" << json_escape(kEffectOutboxFormat) << "\",\n"
            << "  \"prepared_effect_count\": " << verified.durable_line_count << ",\n"
            << "  \"terminal_effect_count\": " << verified.effect_transition_line_count << ",\n"
            << "  \"outbox_reserved_count\": " << verified.effect_outbox_reserved << ",\n"
            << "  \"outbox_inflight_count\": " << verified.effect_outbox_inflight << ",\n"
            << "  \"outbox_terminal_count\": " << verified.effect_outbox_terminal << ",\n"
            << "  \"pending_effect_count\": " << rows.size() << ",\n"
            << "  \"decision_head_hash\": \"" << json_escape(verified.durable_head_hash) << "\",\n"
            << "  \"durable_head_hash\": \"" << json_escape(verified.durable_head_hash) << "\",\n"
            << "  \"effect_transition_head_hash\": \"" << json_escape(verified.effect_transition_head_hash) << "\",\n"
            << "  \"pending_effects\": [\n";
        for (size_t i = 0; i < rows.size(); ++i) {
            const auto& row = rows[i];
            out << "    {"
                << "\"sequence\": " << row.sequence
                << ", \"entry_hash\": \"" << json_escape(row.entry_hash) << "\""
                << ", \"case_id\": \"" << json_escape(row.case_id) << "\""
                << ", \"kind\": \"" << json_escape(row.kind) << "\""
                << ", \"operation_id\": \"" << json_escape(row.operation_id) << "\""
                << ", \"contract_digest_sha256\": \"" << json_escape(row.contract_digest_sha256) << "\""
                << ", \"action\": \"" << json_escape(row.action) << "\""
                << ", \"cloud_event_source\": \"" << json_escape(row.cloud_event_source) << "\""
                << ", \"cloud_event_id\": \"" << json_escape(row.cloud_event_id) << "\""
                << ", \"effect_idempotency_key\": \"" << json_escape(row.effect_idempotency_key) << "\""
                << ", \"outbox_state\": \"" << json_escape(row.outbox_state) << "\""
                << ", \"dispatch_attempts\": " << row.dispatch_attempts
                << ", \"worker_claim_id\": \"" << json_escape(row.worker_claim_id) << "\""
                << ", \"worker_id\": \"" << json_escape(row.worker_id) << "\""
                << ", \"claimed_at_epoch\": " << row.claimed_at_epoch
                << ", \"lease_expires_at_epoch\": " << row.lease_expires_at_epoch
                << "}" << (i + 1 == rows.size() ? "\n" : ",\n");
        }
        out << "  ]\n}\n";
        return out.str();
    } catch (...) {
        sqlite_close_best_effort(db);
        throw;
    }
}


class SqliteWalReplayLedger final : public IReplayLedgerBackend {
  public:
    ~SqliteWalReplayLedger() override { close(); }
    void load(const std::string& ledger_path, bool reset, const std::string& mode = "immediate") override;
    bool is_enabled() const override { return enabled_; }
    std::string backend_name() const override { return "sqlite-wal"; }
    ReplayLedgerStats stats() const override;
    bool contains_jti(const std::string& jti) const override;
    bool contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const override;
    bool contains_effect_idempotency_key(const std::string& effect_idempotency_key) const override;
    EffectOutboxClaimResult claim_next_outbox(const std::string& worker_id, long long now_epoch, long long lease_seconds);
    bool mark_effect_terminal(const std::string& effect_idempotency_key, long long prepared_sequence, const std::string& prepared_entry_hash, const std::string& terminal_state, const std::string& result_digest_sha256, const std::string& transition_reason, const std::string& expected_durable_head_hash, const std::string& expected_transition_previous_hash, const std::string& expected_ledger_instance_id, const std::string& transition_intent_id, const std::string& transition_intent_signer_kid, const std::string& transition_intent_sha256, std::string& reason);
    bool stage(const Json& tc, const Json& claims, const std::string& action, std::string& reason) override;
    bool commit(std::string& reason) override;
    bool backup_snapshot(const std::string& snapshot_path, std::string& reason) override;
    void recover() override {}
    void close() override;

  private:
    void create_schema();
    void verify_backend_profile();
    void verify_ledger_identity();
    void run_integrity_check_or_throw(const std::string& label);
    void reload_chain_or_throw();
    void insert_pending_row(sqlite3_stmt* stmt, const PendingSqliteEntry& row);
    bool contains_ingress_sender_replay_nonce(const PendingSqliteEntry& row) const;
    bool run_commit(std::string& reason);

    bool enabled_ = false;
    bool opened_existing_database_ = false;
    sqlite3* db_ = nullptr;
    std::string path_;
    std::string commit_mode_ = "immediate";
    long long loaded_entries_ = 0;
    long long appended_entries_ = 0;
    long long transactions_ = 0;
    long long wal_checkpoints_ = 0;
    long long integrity_checks_ = 0;
    long long profile_checks_ = 0;
    long long corruption_rejections_ = 0;
    long long backup_snapshots_ = 0;
    long long snapshot_verifications_ = 0;
    long long snapshot_restores_ = 0;
    long long batch_flush_commits_ = 0;
    long long batch_pending_entries_peak_ = 0;
    long long durable_line_count_ = 0;
    std::string durable_head_hash_ = "GENESIS";
    std::string ledger_instance_id_;
    std::unordered_set<std::string> committed_jtis_;
    std::unordered_set<std::string> staged_jtis_;
    std::unordered_set<std::string> committed_event_identities_;
    std::unordered_set<std::string> staged_event_identities_;
    std::unordered_set<std::string> committed_effect_idempotency_keys_;
    std::unordered_map<std::string, PreparedEffectReference> prepared_effect_refs_;
    std::unordered_set<std::string> staged_effect_idempotency_keys_;
    std::unordered_set<std::string> staged_ingress_sender_replay_nonce_keys_;
    std::unordered_map<std::string, std::string> terminal_effect_states_;
    long long effect_transition_line_count_ = 0;
    std::string effect_transition_head_hash_ = "GENESIS";
    long long effect_terminal_transitions_ = 0;
    long long effect_transition_rejections_ = 0;
    long long effect_outbox_reserved_ = 0;
    long long effect_outbox_inflight_ = 0;
    long long effect_outbox_terminal_ = 0;
    std::vector<PendingSqliteEntry> pending_;
    std::unique_ptr<SqliteWriteGateLock> write_gate_;
};

void SqliteWalReplayLedger::load(const std::string& ledger_path, bool reset, const std::string& mode) {
    close();
    if (ledger_path.empty()) {
        enabled_ = false;
        return;
    }
    if (mode != "immediate" && mode != "batch") throw std::runtime_error("unsupported replay-ledger commit mode for SQLite/WAL backend: " + mode);
    path_ = ledger_path;
    commit_mode_ = mode;
    reject_sqlite_family_symlinks(path_);
    std::filesystem::path parent = std::filesystem::path(path_).parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
    write_gate_ = std::make_unique<SqliteWriteGateLock>(path_);
    if (reset) unlink_sqlite_family(path_);
    {
        std::error_code size_ec;
        opened_existing_database_ = std::filesystem::exists(path_) && std::filesystem::file_size(path_, size_ec) > 0 && !size_ec;
    }
    int open_flags = sqlite_open_flags_for_ledger();
    if (sqlite3_open_v2(path_.c_str(), &db_, open_flags, nullptr) != SQLITE_OK) sqlite_throw(db_, "sqlite-wal replay ledger open failed");
    enabled_ = true;
    sqlite3_busy_timeout(db_, 1000);
    sqlite_exec_or_throw(db_, "PRAGMA journal_mode=WAL;", "sqlite-wal replay ledger could not enable WAL mode");
    sqlite_exec_or_throw(db_, "PRAGMA synchronous=FULL;", "sqlite-wal replay ledger could not enable FULL synchronous mode");
    sqlite_exec_or_throw(db_, "PRAGMA foreign_keys=ON;", "sqlite-wal replay ledger could not enable foreign keys");
    create_schema();
    verify_backend_profile();
    verify_ledger_identity();
    run_integrity_check_or_throw("load");
    reload_chain_or_throw();
}

void SqliteWalReplayLedger::create_schema() {
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS metadata ("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "line_count INTEGER NOT NULL CHECK(line_count >= 0),"
        "head_hash TEXT NOT NULL CHECK(length(head_hash) > 0));",
        "sqlite-wal replay ledger metadata schema failed");
    if (!opened_existing_database_) {
        sqlite_exec_or_throw(db_, "INSERT OR IGNORE INTO metadata(id,line_count,head_hash) VALUES(1,0,'GENESIS');", "sqlite-wal replay ledger metadata initialization failed");
    }
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS ledger_entries ("
        "sequence INTEGER PRIMARY KEY CHECK(sequence > 0),"
        "previous_hash TEXT NOT NULL CHECK(length(previous_hash) > 0),"
        "entry_hash TEXT NOT NULL UNIQUE CHECK(length(entry_hash) = 64),"
        "case_id TEXT NOT NULL,"
        "kind TEXT NOT NULL CHECK(kind IN ('openapi','asyncapi')),"
        "operation_id TEXT NOT NULL CHECK(length(operation_id) > 0),"
        "contract_digest_sha256 TEXT NOT NULL CHECK(length(contract_digest_sha256) = 64),"
        "jti TEXT NOT NULL UNIQUE CHECK(length(jti) > 0),"
        "action TEXT NOT NULL CHECK(action IN ('allow','accept')),"
        "cloud_event_source TEXT NOT NULL DEFAULT '',"
        "cloud_event_id TEXT NOT NULL DEFAULT '',"
        "effect_idempotency_key TEXT NOT NULL UNIQUE CHECK(length(effect_idempotency_key) = 64),"
        "effect_state TEXT NOT NULL CHECK(effect_state='prepared'));",
        "sqlite-wal replay ledger entry schema failed");
    sqlite_exec_or_throw(db_,
        "CREATE UNIQUE INDEX IF NOT EXISTS ledger_async_event_identity_unique "
        "ON ledger_entries(cloud_event_source, cloud_event_id) "
        "WHERE kind='asyncapi' AND length(cloud_event_source) > 0 AND length(cloud_event_id) > 0;",
        "sqlite-wal replay ledger async event identity unique index failed");
    sqlite_exec_or_throw(db_,
        "CREATE UNIQUE INDEX IF NOT EXISTS ledger_effect_prepared_entry_evidence_unique "
        "ON ledger_entries(sequence, entry_hash, effect_idempotency_key);",
        "sqlite-wal replay ledger prepared-effect evidence unique index failed");
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS ledger_identity ("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "ledger_instance_id TEXT NOT NULL UNIQUE CHECK(length(ledger_instance_id) = 64));",
        "sqlite-wal replay ledger identity schema failed");
    if (!opened_existing_database_) {
        const std::string instance_id = generate_ledger_instance_id(path_);
        Stmt ident(db_, "INSERT OR IGNORE INTO ledger_identity(id,ledger_instance_id) VALUES(1,?)", "sqlite-wal replay ledger identity initialization prepare failed");
        bind_text_or_throw(db_, ident.stmt, 1, instance_id, "sqlite-wal replay ledger identity bind failed");
        if (sqlite3_step(ident.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal replay ledger identity initialization failed");
    }
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS effect_transition_metadata ("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "line_count INTEGER NOT NULL CHECK(line_count >= 0),"
        "head_hash TEXT NOT NULL CHECK(length(head_hash) > 0));",
        "sqlite-wal replay ledger effect transition metadata schema failed");
    if (!opened_existing_database_) {
        sqlite_exec_or_throw(db_, "INSERT OR IGNORE INTO effect_transition_metadata(id,line_count,head_hash) VALUES(1,0,'GENESIS');", "sqlite-wal replay ledger effect transition metadata initialization failed");
    }
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS effect_transitions ("
        "sequence INTEGER PRIMARY KEY CHECK(sequence > 0),"
        "previous_hash TEXT NOT NULL CHECK(length(previous_hash) > 0),"
        "transition_hash TEXT NOT NULL UNIQUE CHECK(length(transition_hash) = 64),"
        "ledger_instance_id TEXT NOT NULL CHECK(length(ledger_instance_id) = 64),"
        "effect_idempotency_key TEXT NOT NULL CHECK(length(effect_idempotency_key) = 64),"
        "prepared_sequence INTEGER NOT NULL CHECK(prepared_sequence > 0),"
        "prepared_entry_hash TEXT NOT NULL CHECK(length(prepared_entry_hash) = 64),"
        "terminal_state TEXT NOT NULL CHECK(terminal_state IN ('applied','failed','compensated')),"
        "result_digest_sha256 TEXT NOT NULL CHECK(length(result_digest_sha256) = 64),"
        "transition_reason TEXT NOT NULL DEFAULT '',"
        "transition_intent_id TEXT NOT NULL CHECK(length(transition_intent_id) > 0),"
        "transition_intent_signer_kid TEXT NOT NULL CHECK(length(transition_intent_signer_kid) > 0),"
        "transition_intent_sha256 TEXT NOT NULL CHECK(length(transition_intent_sha256) = 64),"
        "FOREIGN KEY(ledger_instance_id) REFERENCES ledger_identity(ledger_instance_id),"
        "FOREIGN KEY(effect_idempotency_key) REFERENCES ledger_entries(effect_idempotency_key),"
        "FOREIGN KEY(prepared_sequence, prepared_entry_hash, effect_idempotency_key) REFERENCES ledger_entries(sequence, entry_hash, effect_idempotency_key));",
        "sqlite-wal replay ledger effect transitions schema failed");
    sqlite_exec_or_throw(db_,
        "CREATE UNIQUE INDEX IF NOT EXISTS effect_transitions_key_unique "
        "ON effect_transitions(effect_idempotency_key);",
        "sqlite-wal replay ledger effect transition key unique index failed");
    sqlite_exec_or_throw(db_,
        "CREATE UNIQUE INDEX IF NOT EXISTS effect_transitions_intent_id_unique "
        "ON effect_transitions(transition_intent_id);",
        "sqlite-wal replay ledger effect transition intent id unique index failed");
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS effect_outbox ("
        "effect_idempotency_key TEXT PRIMARY KEY CHECK(length(effect_idempotency_key) = 64),"
        "prepared_sequence INTEGER NOT NULL CHECK(prepared_sequence > 0),"
        "prepared_entry_hash TEXT NOT NULL CHECK(length(prepared_entry_hash) = 64),"
        "outbox_state TEXT NOT NULL CHECK(outbox_state IN ('reserved','inflight','applied','failed','compensated')),"
        "dispatch_attempts INTEGER NOT NULL DEFAULT 0 CHECK(dispatch_attempts >= 0),"
        "worker_claim_id TEXT NOT NULL DEFAULT '' CHECK(length(worker_claim_id) IN (0,64)),"
        "worker_id TEXT NOT NULL DEFAULT '' CHECK(length(worker_id) <= 128),"
        "claimed_at_epoch INTEGER NOT NULL DEFAULT 0 CHECK(claimed_at_epoch >= 0),"
        "lease_expires_at_epoch INTEGER NOT NULL DEFAULT 0 CHECK(lease_expires_at_epoch >= 0),"
        "last_result_digest_sha256 TEXT NOT NULL DEFAULT '' CHECK(length(last_result_digest_sha256) IN (0,64)),"
        "updated_at_sequence INTEGER NOT NULL CHECK(updated_at_sequence >= 0),"
        "FOREIGN KEY(effect_idempotency_key) REFERENCES ledger_entries(effect_idempotency_key),"
        "FOREIGN KEY(prepared_sequence, prepared_entry_hash, effect_idempotency_key) REFERENCES ledger_entries(sequence, entry_hash, effect_idempotency_key));",
        "sqlite-wal replay ledger effect outbox schema failed");
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS ingress_sender_replay_cache ("
        "replay_key_sha256 TEXT PRIMARY KEY CHECK(length(replay_key_sha256) = 64),"
        "format TEXT NOT NULL CHECK(format='anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction'),"
        "service_config_sha256 TEXT NOT NULL CHECK(length(service_config_sha256) = 64),"
        "ingress_profile_sha256 TEXT NOT NULL CHECK(length(ingress_profile_sha256) = 64),"
        "sender_replay_cache_instance_id TEXT NOT NULL CHECK(length(sender_replay_cache_instance_id) > 0),"
        "sender_proof_kid TEXT NOT NULL CHECK(length(sender_proof_kid) > 0),"
        "principal TEXT NOT NULL CHECK(length(principal) > 0),"
        "nonce TEXT NOT NULL CHECK(length(nonce) BETWEEN 16 AND 128),"
        "issued_at_epoch INTEGER NOT NULL CHECK(issued_at_epoch > 0),"
        "observed_at_epoch INTEGER NOT NULL CHECK(observed_at_epoch > 0),"
        "replay_window_seconds INTEGER NOT NULL CHECK(replay_window_seconds BETWEEN 1 AND 86400),"
        "material_sha256 TEXT NOT NULL CHECK(length(material_sha256) = 64),"
        "prepared_sequence INTEGER NOT NULL CHECK(prepared_sequence > 0),"
        "prepared_entry_hash TEXT NOT NULL CHECK(length(prepared_entry_hash) = 64),"
        "effect_idempotency_key TEXT NOT NULL CHECK(length(effect_idempotency_key) = 64),"
        "FOREIGN KEY(prepared_sequence, prepared_entry_hash, effect_idempotency_key) REFERENCES ledger_entries(sequence, entry_hash, effect_idempotency_key));",
        "sqlite-wal ingress sender replay cache schema failed");
    sqlite_exec_or_throw(db_,
        "CREATE UNIQUE INDEX IF NOT EXISTS ingress_sender_replay_nonce_unique "
        "ON ingress_sender_replay_cache(service_config_sha256, ingress_profile_sha256, sender_replay_cache_instance_id, sender_proof_kid, nonce);",
        "sqlite-wal ingress sender replay nonce unique index failed");
    sqlite_exec_or_throw(db_,
        "CREATE INDEX IF NOT EXISTS ingress_sender_replay_expiry ON ingress_sender_replay_cache(issued_at_epoch);",
        "sqlite-wal ingress sender replay expiry index failed");
    sqlite_exec_or_throw(db_,
        "CREATE TABLE IF NOT EXISTS backend_profile ("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "backend_name TEXT NOT NULL CHECK(backend_name='sqlite-wal'),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=10),"
        "hash_algorithm TEXT NOT NULL CHECK(hash_algorithm='sha256'),"
        "entry_material_version TEXT NOT NULL CHECK(entry_material_version='anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent'),"
        "commit_protocol TEXT NOT NULL CHECK(commit_protocol='sqlite-wal-begin-immediate-full-sync'));",
        "sqlite-wal replay ledger backend profile schema failed");
    if (!opened_existing_database_) {
        sqlite_exec_or_throw(db_,
            "INSERT OR IGNORE INTO backend_profile(id,backend_name,schema_version,hash_algorithm,entry_material_version,commit_protocol) "
            "VALUES(1,'sqlite-wal',10,'sha256','anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent','sqlite-wal-begin-immediate-full-sync');",
            "sqlite-wal replay ledger backend profile initialization failed");
    }
}

void SqliteWalReplayLedger::verify_backend_profile() {
    Stmt stmt(db_, "SELECT backend_name, schema_version, hash_algorithm, entry_material_version, commit_protocol FROM backend_profile WHERE id=1", "sqlite-wal backend profile select prepare failed");
    int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw std::runtime_error("sqlite-wal backend profile row is absent");
    std::string backend = column_text(stmt.stmt, 0);
    long long schema_version = sqlite3_column_int64(stmt.stmt, 1);
    std::string hash_algorithm = column_text(stmt.stmt, 2);
    std::string material_version = column_text(stmt.stmt, 3);
    std::string commit_protocol = column_text(stmt.stmt, 4);
    if (backend != "sqlite-wal" || schema_version != kSqliteLedgerSchemaVersion || hash_algorithm != "sha256" || material_version != kSqliteLedgerEntryMaterialVersion || commit_protocol != kSqliteLedgerCommitProtocol) {
        corruption_rejections_++;
        throw std::runtime_error("sqlite-wal backend profile mismatch");
    }
    profile_checks_++;
}

void SqliteWalReplayLedger::verify_ledger_identity() {
    ledger_instance_id_ = query_ledger_instance_id(db_, "sqlite-wal replay ledger");
}

void SqliteWalReplayLedger::run_integrity_check_or_throw(const std::string& label) {
    Stmt stmt(db_, "PRAGMA integrity_check;", "sqlite-wal integrity_check prepare failed");
    int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw std::runtime_error("sqlite-wal integrity_check returned no row during " + label);
    std::string verdict = column_text(stmt.stmt, 0);
    if (verdict != "ok") {
        corruption_rejections_++;
        throw std::runtime_error("sqlite-wal integrity_check failed during " + label + ": " + verdict);
    }
    integrity_checks_++;
}

void SqliteWalReplayLedger::reload_chain_or_throw() {
    committed_jtis_.clear();
    staged_jtis_.clear();
    committed_event_identities_.clear();
    staged_event_identities_.clear();
    committed_effect_idempotency_keys_.clear();
    prepared_effect_refs_.clear();
    staged_effect_idempotency_keys_.clear();
    terminal_effect_states_.clear();
    effect_transition_line_count_ = 0;
    effect_transition_head_hash_ = "GENESIS";
    effect_outbox_reserved_ = 0;
    effect_outbox_inflight_ = 0;
    effect_outbox_terminal_ = 0;
    pending_.clear();
    loaded_entries_ = 0;
    durable_line_count_ = 0;
    durable_head_hash_ = "GENESIS";
    Stmt stmt(db_, "SELECT sequence, previous_hash, entry_hash, case_id, kind, operation_id, contract_digest_sha256, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state FROM ledger_entries ORDER BY sequence", "sqlite-wal replay ledger reload prepare failed");
    long long expected_sequence = 1;
    std::string previous = "GENESIS";
    while (true) {
        int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) sqlite_throw(db_, "sqlite-wal replay ledger reload step failed");
        long long sequence = sqlite3_column_int64(stmt.stmt, 0);
        std::string previous_hash = column_text(stmt.stmt, 1);
        std::string entry_hash = column_text(stmt.stmt, 2);
        std::string case_id = column_text(stmt.stmt, 3);
        std::string kind = column_text(stmt.stmt, 4);
        std::string operation_id = column_text(stmt.stmt, 5);
        std::string contract_digest = column_text(stmt.stmt, 6);
        std::string jti = column_text(stmt.stmt, 7);
        std::string action = column_text(stmt.stmt, 8);
        std::string cloud_event_source = column_text(stmt.stmt, 9);
        std::string cloud_event_id = column_text(stmt.stmt, 10);
        std::string effect_idempotency_key = column_text(stmt.stmt, 11);
        std::string effect_state = column_text(stmt.stmt, 12);
        if (sequence != expected_sequence) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger sequence gap or rollback detected"); }
        if (previous_hash != previous) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger previous hash chain mismatch"); }
        if (operation_id.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger row missing verified operation_id"); }
        if (!is_lower_hex_sha256(contract_digest)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger row has invalid verified contract_digest_sha256"); }
        std::string expected_hash = ReplayLedger::compute_entry_hash(sequence, previous_hash, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state);
        if (entry_hash != expected_hash) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger entry hash mismatch"); }
        if (jti.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger row missing nonempty jti"); }
        if (!committed_jtis_.insert(jti).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger duplicate jti detected during reload"); }
        if (!is_lower_hex_sha256(effect_idempotency_key)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger row missing valid effect_idempotency_key"); }
        if (effect_state != kPreparedEffectState) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger row has unsupported effect_state"); }
        if (!committed_effect_idempotency_keys_.insert(effect_idempotency_key).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger duplicate effect_idempotency_key detected during reload"); }
        prepared_effect_refs_[effect_idempotency_key] = PreparedEffectReference{sequence, entry_hash, effect_idempotency_key};
        if (kind == "asyncapi") {
            const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
            if (event_key.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger async row missing CloudEvents source/id identity"); }
            if (!committed_event_identities_.insert(event_key).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger duplicate CloudEvents source/id identity detected during reload"); }
        }
        previous = entry_hash;
        expected_sequence++;
        loaded_entries_++;
    }
    durable_line_count_ = loaded_entries_;
    durable_head_hash_ = previous;
    Stmt meta(db_, "SELECT line_count, head_hash FROM metadata WHERE id=1", "sqlite-wal replay ledger metadata select prepare failed");
    int rc = sqlite3_step(meta.stmt);
    if (rc != SQLITE_ROW) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger metadata row is absent"); }
    long long meta_count = sqlite3_column_int64(meta.stmt, 0);
    std::string meta_head = column_text(meta.stmt, 1);
    if (meta_count != durable_line_count_ || meta_head != durable_head_hash_) { corruption_rejections_++; throw std::runtime_error("sqlite-wal replay ledger metadata does not match verified chain"); }

    long long expected_transition_sequence = 1;
    std::string transition_previous = "GENESIS";
    std::unordered_set<std::string> committed_transition_intent_ids;
    std::unordered_map<std::string, std::string> transitioned_effect_digests;
    std::unordered_map<std::string, long long> transitioned_effect_sequences;
    {
        Stmt transitions(db_, "SELECT sequence, previous_hash, transition_hash, ledger_instance_id, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256 FROM effect_transitions ORDER BY sequence", "sqlite-wal effect transitions reload prepare failed");
        while (true) {
            int trc = sqlite3_step(transitions.stmt);
            if (trc == SQLITE_DONE) break;
            if (trc != SQLITE_ROW) sqlite_throw(db_, "sqlite-wal effect transitions reload step failed");
            const long long sequence = sqlite3_column_int64(transitions.stmt, 0);
            const std::string previous_hash = column_text(transitions.stmt, 1);
            const std::string transition_hash = column_text(transitions.stmt, 2);
            const std::string transition_ledger_instance_id = column_text(transitions.stmt, 3);
            const std::string effect_idempotency_key = column_text(transitions.stmt, 4);
            const long long prepared_sequence = sqlite3_column_int64(transitions.stmt, 5);
            const std::string prepared_entry_hash = column_text(transitions.stmt, 6);
            const std::string terminal_state = column_text(transitions.stmt, 7);
            const std::string result_digest_sha256 = column_text(transitions.stmt, 8);
            const std::string transition_reason = column_text(transitions.stmt, 9);
            const std::string transition_intent_id = column_text(transitions.stmt, 10);
            const std::string transition_intent_signer_kid = column_text(transitions.stmt, 11);
            const std::string transition_intent_sha256 = column_text(transitions.stmt, 12);
            if (sequence != expected_transition_sequence) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition sequence gap or rollback detected"); }
            if (previous_hash != transition_previous) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition previous hash mismatch"); }
            if (transition_ledger_instance_id != ledger_instance_id_) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition ledger_instance_id does not match ledger identity"); }
            if (!is_lower_hex_sha256(effect_idempotency_key)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition invalid effect_idempotency_key"); }
            auto ref_it = prepared_effect_refs_.find(effect_idempotency_key);
            if (ref_it == prepared_effect_refs_.end()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition references unknown prepared effect"); }
            if (prepared_sequence <= 0 || !is_lower_hex_sha256(prepared_entry_hash)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition invalid prepared-effect evidence binding"); }
            if (ref_it->second.sequence != prepared_sequence || ref_it->second.entry_hash != prepared_entry_hash) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition prepared-effect evidence does not match ledger row"); }
            if (!is_terminal_effect_state(terminal_state)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition has unsupported terminal state"); }
            if (!is_lower_hex_sha256(result_digest_sha256)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition invalid result digest"); }
            if (transition_intent_id.empty() || transition_intent_signer_kid.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition missing signed intent metadata"); }
            if (!is_lower_hex_sha256(transition_intent_sha256)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition invalid signed intent digest"); }
            if (!committed_transition_intent_ids.insert(transition_intent_id).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal duplicate signed transition intent id detected during reload"); }
            const std::string expected_hash = compute_effect_transition_hash(sequence, previous_hash, ledger_instance_id_, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256);
            if (transition_hash != expected_hash) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition hash mismatch"); }
            if (!terminal_effect_states_.emplace(effect_idempotency_key, terminal_state).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal duplicate effect transition detected during reload"); }
            transitioned_effect_digests[effect_idempotency_key] = result_digest_sha256;
            transitioned_effect_sequences[effect_idempotency_key] = sequence;
            transition_previous = transition_hash;
            expected_transition_sequence++;
            effect_transition_line_count_++;
        }
    }
    effect_transition_head_hash_ = transition_previous;
    Stmt transition_meta(db_, "SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1", "sqlite-wal effect transition metadata select prepare failed");
    int trc = sqlite3_step(transition_meta.stmt);
    if (trc != SQLITE_ROW) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition metadata row is absent"); }
    long long transition_meta_count = sqlite3_column_int64(transition_meta.stmt, 0);
    std::string transition_meta_head = column_text(transition_meta.stmt, 1);
    if (transition_meta_count != effect_transition_line_count_ || transition_meta_head != effect_transition_head_hash_) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect transition metadata does not match verified chain"); }

    std::unordered_set<std::string> outbox_keys;
    {
        Stmt outbox(db_, "SELECT effect_idempotency_key, prepared_sequence, prepared_entry_hash, outbox_state, dispatch_attempts, worker_claim_id, worker_id, claimed_at_epoch, lease_expires_at_epoch, last_result_digest_sha256, updated_at_sequence FROM effect_outbox ORDER BY prepared_sequence", "sqlite-wal effect outbox reload prepare failed");
        while (true) {
            int orc = sqlite3_step(outbox.stmt);
            if (orc == SQLITE_DONE) break;
            if (orc != SQLITE_ROW) sqlite_throw(db_, "sqlite-wal effect outbox reload step failed");
            const std::string effect_idempotency_key = column_text(outbox.stmt, 0);
            const long long prepared_sequence = sqlite3_column_int64(outbox.stmt, 1);
            const std::string prepared_entry_hash = column_text(outbox.stmt, 2);
            const std::string outbox_state = column_text(outbox.stmt, 3);
            const long long dispatch_attempts = sqlite3_column_int64(outbox.stmt, 4);
            const std::string worker_claim_id = column_text(outbox.stmt, 5);
            const std::string worker_id = column_text(outbox.stmt, 6);
            const long long claimed_at_epoch = sqlite3_column_int64(outbox.stmt, 7);
            const long long lease_expires_at_epoch = sqlite3_column_int64(outbox.stmt, 8);
            const std::string last_result_digest_sha256 = column_text(outbox.stmt, 9);
            const long long updated_at_sequence = sqlite3_column_int64(outbox.stmt, 10);
            auto ref_it = prepared_effect_refs_.find(effect_idempotency_key);
            if (ref_it == prepared_effect_refs_.end()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox references unknown prepared effect"); }
            if (prepared_sequence != ref_it->second.sequence || prepared_entry_hash != ref_it->second.entry_hash) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox prepared evidence does not match ledger row"); }
            if (!outbox_keys.insert(effect_idempotency_key).second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal duplicate effect outbox key detected during reload"); }
            if (!is_effect_outbox_state(outbox_state)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox has unsupported state"); }
            if (dispatch_attempts < 0) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox has invalid dispatch attempt count"); }
            const auto terminal_it = terminal_effect_states_.find(effect_idempotency_key);
            if (outbox_state == kEffectOutboxReservedState) {
                if (terminal_it != terminal_effect_states_.end()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox remained reserved after terminal transition"); }
                if (dispatch_attempts != 0) { corruption_rejections_++; throw std::runtime_error("sqlite-wal reserved effect outbox has nonzero dispatch attempts"); }
                if (!worker_claim_id.empty() || !worker_id.empty() || claimed_at_epoch != 0 || lease_expires_at_epoch != 0) { corruption_rejections_++; throw std::runtime_error("sqlite-wal reserved effect outbox carries worker claim metadata"); }
                if (!last_result_digest_sha256.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal reserved effect outbox carries terminal result digest"); }
                if (updated_at_sequence != prepared_sequence) { corruption_rejections_++; throw std::runtime_error("sqlite-wal reserved effect outbox update sequence does not match prepared sequence"); }
                effect_outbox_reserved_++;
            } else if (outbox_state == kEffectOutboxInflightState) {
                if (terminal_it != terminal_effect_states_.end()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox remained inflight after terminal transition"); }
                if (dispatch_attempts <= 0) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox has no dispatch attempt"); }
                if (!is_lower_hex_sha256(worker_claim_id)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox has invalid worker claim id"); }
                if (worker_id.empty() || worker_id.size() > 128 || contains_disallowed_security_control(worker_id)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox has invalid worker id"); }
                if (claimed_at_epoch <= 0 || lease_expires_at_epoch < claimed_at_epoch) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox has invalid lease timestamps"); }
                if (!last_result_digest_sha256.empty()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox carries terminal result digest"); }
                if (updated_at_sequence != prepared_sequence) { corruption_rejections_++; throw std::runtime_error("sqlite-wal inflight effect outbox update sequence does not match prepared sequence"); }
                effect_outbox_inflight_++;
            } else {
                if (terminal_it == terminal_effect_states_.end()) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox lacks matching transition row"); }
                if (outbox_state != terminal_it->second) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox state does not match transition row"); }
                if (last_result_digest_sha256 != transitioned_effect_digests[effect_idempotency_key]) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox result digest does not match transition row"); }
                if (updated_at_sequence != transitioned_effect_sequences[effect_idempotency_key]) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox update sequence does not match transition sequence"); }
                if (!worker_claim_id.empty() && !is_lower_hex_sha256(worker_claim_id)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox has invalid worker claim id"); }
                if (!worker_id.empty() && (worker_id.size() > 128 || contains_disallowed_security_control(worker_id))) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox has invalid worker id"); }
                if ((worker_claim_id.empty() || worker_id.empty()) && (claimed_at_epoch != 0 || lease_expires_at_epoch != 0)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox has partial worker lease metadata"); }
                if (!worker_claim_id.empty() && (claimed_at_epoch <= 0 || lease_expires_at_epoch < claimed_at_epoch || dispatch_attempts <= 0)) { corruption_rejections_++; throw std::runtime_error("sqlite-wal terminal effect outbox has invalid preserved worker lease metadata"); }
                effect_outbox_terminal_++;
            }
        }
    }
    if (static_cast<long long>(outbox_keys.size()) != durable_line_count_) { corruption_rejections_++; throw std::runtime_error("sqlite-wal effect outbox does not cover every prepared ledger entry exactly once"); }
}

bool SqliteWalReplayLedger::contains_jti(const std::string& jti) const {
    if (!enabled_ || jti.empty()) return false;
    return committed_jtis_.find(jti) != committed_jtis_.end() || staged_jtis_.find(jti) != staged_jtis_.end();
}

bool SqliteWalReplayLedger::contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const {
    if (!enabled_) return false;
    const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
    return !event_key.empty() && (committed_event_identities_.find(event_key) != committed_event_identities_.end() || staged_event_identities_.find(event_key) != staged_event_identities_.end());
}

bool SqliteWalReplayLedger::contains_effect_idempotency_key(const std::string& effect_idempotency_key) const {
    if (!enabled_ || effect_idempotency_key.empty()) return false;
    return committed_effect_idempotency_keys_.find(effect_idempotency_key) != committed_effect_idempotency_keys_.end() || staged_effect_idempotency_keys_.find(effect_idempotency_key) != staged_effect_idempotency_keys_.end();
}

bool SqliteWalReplayLedger::contains_ingress_sender_replay_nonce(const PendingSqliteEntry& row) const {
    if (!enabled_ || !db_ || !row.ingress_sender_replay_required) return false;
    if (staged_ingress_sender_replay_nonce_keys_.find(ingress_sender_replay_nonce_stage_key(row)) != staged_ingress_sender_replay_nonce_keys_.end()) return true;
    Stmt exists(db_, "SELECT 1 FROM ingress_sender_replay_cache WHERE service_config_sha256=? AND ingress_profile_sha256=? AND sender_replay_cache_instance_id=? AND sender_proof_kid=? AND nonce=? LIMIT 1", "sqlite-wal ingress sender replay lookup prepare failed");
    bind_text_or_throw(db_, exists.stmt, 1, row.ingress_sender_replay_service_config_sha256, "sqlite-wal ingress sender replay lookup bind service config failed");
    bind_text_or_throw(db_, exists.stmt, 2, row.ingress_sender_replay_profile_sha256, "sqlite-wal ingress sender replay lookup bind profile failed");
    bind_text_or_throw(db_, exists.stmt, 3, row.ingress_sender_replay_cache_instance_id, "sqlite-wal ingress sender replay lookup bind instance failed");
    bind_text_or_throw(db_, exists.stmt, 4, row.ingress_sender_replay_proof_kid, "sqlite-wal ingress sender replay lookup bind proof kid failed");
    bind_text_or_throw(db_, exists.stmt, 5, row.ingress_sender_replay_nonce, "sqlite-wal ingress sender replay lookup bind nonce failed");
    const int rc = sqlite3_step(exists.stmt);
    if (rc == SQLITE_ROW) return true;
    if (rc == SQLITE_DONE) return false;
    sqlite_throw(db_, "sqlite-wal ingress sender replay lookup failed");
}

EffectOutboxClaimResult SqliteWalReplayLedger::claim_next_outbox(const std::string& worker_id, long long now_epoch, long long lease_seconds) {
    if (!enabled_ || !db_) throw std::runtime_error("sqlite-wal effect outbox claim requires an enabled backend");
    if (!pending_.empty()) throw std::runtime_error("sqlite-wal effect outbox claim refuses to run while prepared decisions are pending commit");
    validate_outbox_worker_claim_inputs(worker_id, now_epoch, lease_seconds);
    EffectOutboxClaimResult out;
    out.ledger_instance_id = ledger_instance_id_;
    out.decision_head_hash = durable_head_hash_;
    out.effect_transition_head_hash = effect_transition_head_hash_;
    out.worker_id = worker_id;
    out.claimed_at_epoch = now_epoch;
    out.lease_expires_at_epoch = now_epoch + lease_seconds;
    try {
        sqlite_exec_or_throw(db_, "BEGIN IMMEDIATE;", "sqlite-wal effect outbox claim begin-immediate failed");
        {
            Stmt decision_meta(db_, "SELECT line_count, head_hash FROM metadata WHERE id=1", "sqlite-wal effect outbox claim decision metadata check prepare failed");
            if (sqlite3_step(decision_meta.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect outbox claim decision metadata row absent inside transaction");
            const long long meta_count = sqlite3_column_int64(decision_meta.stmt, 0);
            const std::string meta_head = column_text(decision_meta.stmt, 1);
            if (meta_count != durable_line_count_ || meta_head != durable_head_hash_) throw std::runtime_error("sqlite-wal effect outbox claim detected split-brain prepared ledger head and failed closed");
        }
        {
            Stmt meta(db_, "SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1", "sqlite-wal effect outbox claim transition metadata check prepare failed");
            if (sqlite3_step(meta.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect outbox claim transition metadata row absent inside transaction");
            const long long meta_count = sqlite3_column_int64(meta.stmt, 0);
            const std::string meta_head = column_text(meta.stmt, 1);
            if (meta_count != effect_transition_line_count_ || meta_head != effect_transition_head_hash_) throw std::runtime_error("sqlite-wal effect outbox claim detected split-brain transition head and failed closed");
        }
        {
            Stmt claimable(db_,
                "SELECT o.effect_idempotency_key, o.prepared_sequence, o.prepared_entry_hash, o.outbox_state, o.dispatch_attempts, o.worker_claim_id "
                "FROM effect_outbox o "
                "LEFT JOIN effect_transitions t ON t.effect_idempotency_key=o.effect_idempotency_key "
                "WHERE t.effect_idempotency_key IS NULL "
                "AND (o.outbox_state='reserved' OR (o.outbox_state='inflight' AND o.lease_expires_at_epoch <= ?)) "
                "ORDER BY o.prepared_sequence LIMIT 1",
                "sqlite-wal effect outbox claim select prepare failed");
            bind_int64_or_throw(db_, claimable.stmt, 1, now_epoch, "sqlite-wal effect outbox claim bind now failed");
            const int rc = sqlite3_step(claimable.stmt);
            if (rc == SQLITE_DONE) {
                sqlite_exec_or_throw(db_, "COMMIT;", "sqlite-wal effect outbox claim empty commit failed");
                out.claimed = false;
                return out;
            }
            if (rc != SQLITE_ROW) sqlite_throw(db_, "sqlite-wal effect outbox claim select failed");
            out.effect_idempotency_key = column_text(claimable.stmt, 0);
            out.prepared_sequence = sqlite3_column_int64(claimable.stmt, 1);
            out.prepared_entry_hash = column_text(claimable.stmt, 2);
            out.previous_outbox_state = column_text(claimable.stmt, 3);
            const long long previous_attempts = sqlite3_column_int64(claimable.stmt, 4);
            const std::string previous_claim_id = column_text(claimable.stmt, 5);
            out.dispatch_attempts = previous_attempts + 1;
            if (!is_lower_hex_sha256(out.effect_idempotency_key) || out.prepared_sequence <= 0 || !is_lower_hex_sha256(out.prepared_entry_hash)) {
                throw std::runtime_error("sqlite-wal effect outbox claim selected malformed prepared evidence");
            }
            if (!is_nonterminal_effect_outbox_state(out.previous_outbox_state)) {
                throw std::runtime_error("sqlite-wal effect outbox claim selected non-claimable outbox state");
            }
            out.worker_claim_id = compute_outbox_worker_claim_id(ledger_instance_id_,
                                                                 out.effect_idempotency_key,
                                                                 out.prepared_sequence,
                                                                 out.prepared_entry_hash,
                                                                 worker_id,
                                                                 previous_claim_id,
                                                                 out.dispatch_attempts,
                                                                 out.claimed_at_epoch,
                                                                 out.lease_expires_at_epoch,
                                                                 durable_head_hash_,
                                                                 effect_transition_head_hash_);
        }
        {
            Stmt update(db_,
                "UPDATE effect_outbox SET outbox_state='inflight', dispatch_attempts=?, worker_claim_id=?, worker_id=?, claimed_at_epoch=?, lease_expires_at_epoch=? "
                "WHERE effect_idempotency_key=? AND prepared_sequence=? AND prepared_entry_hash=? "
                "AND (outbox_state='reserved' OR (outbox_state='inflight' AND lease_expires_at_epoch <= ?)) "
                "AND NOT EXISTS (SELECT 1 FROM effect_transitions WHERE effect_transitions.effect_idempotency_key=effect_outbox.effect_idempotency_key)",
                "sqlite-wal effect outbox claim update prepare failed");
            bind_int64_or_throw(db_, update.stmt, 1, out.dispatch_attempts, "sqlite-wal effect outbox claim bind attempt failed");
            bind_text_or_throw(db_, update.stmt, 2, out.worker_claim_id, "sqlite-wal effect outbox claim bind claim id failed");
            bind_text_or_throw(db_, update.stmt, 3, worker_id, "sqlite-wal effect outbox claim bind worker id failed");
            bind_int64_or_throw(db_, update.stmt, 4, out.claimed_at_epoch, "sqlite-wal effect outbox claim bind claimed_at failed");
            bind_int64_or_throw(db_, update.stmt, 5, out.lease_expires_at_epoch, "sqlite-wal effect outbox claim bind lease expiration failed");
            bind_text_or_throw(db_, update.stmt, 6, out.effect_idempotency_key, "sqlite-wal effect outbox claim bind effect key failed");
            bind_int64_or_throw(db_, update.stmt, 7, out.prepared_sequence, "sqlite-wal effect outbox claim bind prepared sequence failed");
            bind_text_or_throw(db_, update.stmt, 8, out.prepared_entry_hash, "sqlite-wal effect outbox claim bind prepared hash failed");
            bind_int64_or_throw(db_, update.stmt, 9, now_epoch, "sqlite-wal effect outbox claim bind update now failed");
            if (sqlite3_step(update.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal effect outbox claim update failed");
            if (sqlite3_changes(db_) != 1) throw std::runtime_error("sqlite-wal effect outbox claim could not update exactly one claimable row");
        }
        sqlite_exec_or_throw(db_, "COMMIT;", "sqlite-wal effect outbox claim commit failed");
        transactions_++;
        out.claimed = true;
        if (out.previous_outbox_state == kEffectOutboxReservedState && effect_outbox_reserved_ > 0) effect_outbox_reserved_--;
        if (out.previous_outbox_state == kEffectOutboxInflightState && effect_outbox_inflight_ > 0) effect_outbox_inflight_--;
        effect_outbox_inflight_++;
        return out;
    } catch (...) {
        char* err = nullptr;
        sqlite3_exec(db_, "ROLLBACK;", nullptr, nullptr, &err);
        if (err) sqlite3_free(err);
        throw;
    }
}

bool SqliteWalReplayLedger::mark_effect_terminal(const std::string& effect_idempotency_key,
                                                 long long prepared_sequence,
                                                 const std::string& prepared_entry_hash,
                                                 const std::string& terminal_state,
                                                 const std::string& result_digest_sha256,
                                                 const std::string& transition_reason,
                                                 const std::string& expected_durable_head_hash,
                                                 const std::string& expected_transition_previous_hash,
                                                 const std::string& expected_ledger_instance_id,
                                                 const std::string& transition_intent_id,
                                                 const std::string& transition_intent_signer_kid,
                                                 const std::string& transition_intent_sha256,
                                                 std::string& reason) {
    if (!enabled_ || !db_) { reason = "sqlite-wal effect transition requires an enabled backend"; return false; }
    if (!pending_.empty()) { reason = "sqlite-wal effect transition refuses to run while prepared decisions are pending commit"; effect_transition_rejections_++; return false; }
    if (!is_lower_hex_sha256(effect_idempotency_key)) { reason = "sqlite-wal effect transition refuses invalid effect_idempotency_key"; effect_transition_rejections_++; return false; }
    if (prepared_sequence <= 0) { reason = "sqlite-wal effect transition refuses missing prepared ledger sequence"; effect_transition_rejections_++; return false; }
    if (!is_lower_hex_sha256(prepared_entry_hash)) { reason = "sqlite-wal effect transition refuses invalid prepared entry hash"; effect_transition_rejections_++; return false; }
    if (!is_terminal_effect_state(terminal_state)) { reason = "sqlite-wal effect transition refuses unsupported terminal state"; effect_transition_rejections_++; return false; }
    if (!is_lower_hex_sha256(result_digest_sha256)) { reason = "sqlite-wal effect transition refuses invalid result_digest_sha256"; effect_transition_rejections_++; return false; }
    if (!is_lower_hex_sha256(expected_ledger_instance_id)) { reason = "sqlite-wal effect transition requires signed intent ledger instance id"; effect_transition_rejections_++; return false; }
    if (expected_ledger_instance_id != ledger_instance_id_) { reason = "sqlite-wal effect transition refuses signed intent for different ledger instance"; effect_transition_rejections_++; return false; }
    if (transition_intent_id.empty() || transition_intent_signer_kid.empty() || !is_lower_hex_sha256(transition_intent_sha256)) { reason = "sqlite-wal effect transition refuses missing or invalid signed transition intent metadata"; effect_transition_rejections_++; return false; }
    if (!expected_durable_head_hash.empty() && expected_durable_head_hash != durable_head_hash_) { reason = "sqlite-wal effect transition refuses stale signed intent: prepared ledger head changed"; effect_transition_rejections_++; return false; }
    if (!expected_transition_previous_hash.empty() && expected_transition_previous_hash != effect_transition_head_hash_) { reason = "sqlite-wal effect transition refuses stale signed intent: effect transition head changed"; effect_transition_rejections_++; return false; }
    auto prepared_ref = prepared_effect_refs_.find(effect_idempotency_key);
    if (prepared_ref == prepared_effect_refs_.end()) {
        reason = "sqlite-wal effect transition refuses unknown prepared effect idempotency key";
        effect_transition_rejections_++;
        return false;
    }
    if (prepared_ref->second.sequence != prepared_sequence || prepared_ref->second.entry_hash != prepared_entry_hash) {
        reason = "sqlite-wal effect transition refuses stale or mismatched prepared-effect evidence";
        effect_transition_rejections_++;
        return false;
    }
    if (terminal_effect_states_.find(effect_idempotency_key) != terminal_effect_states_.end()) {
        reason = "sqlite-wal effect transition refuses duplicate terminal effect transition";
        effect_transition_rejections_++;
        return false;
    }
    const long long sequence = effect_transition_line_count_ + 1;
    const std::string previous_hash = effect_transition_head_hash_;
    const std::string transition_hash = compute_effect_transition_hash(sequence, previous_hash, ledger_instance_id_, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256);
    std::string prior_outbox_state;
    try {
        sqlite_exec_or_throw(db_, "BEGIN IMMEDIATE;", "sqlite-wal effect transition begin-immediate failed");
        {
            Stmt decision_meta(db_, "SELECT line_count, head_hash FROM metadata WHERE id=1", "sqlite-wal effect transition decision metadata check prepare failed");
            if (sqlite3_step(decision_meta.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition decision metadata row absent inside transaction");
            const long long meta_count = sqlite3_column_int64(decision_meta.stmt, 0);
            const std::string meta_head = column_text(decision_meta.stmt, 1);
            if (meta_count != durable_line_count_ || meta_head != durable_head_hash_) throw std::runtime_error("sqlite-wal effect transition detected split-brain prepared ledger head and failed closed");
            if (!expected_durable_head_hash.empty() && meta_head != expected_durable_head_hash) throw std::runtime_error("sqlite-wal effect transition signed intent prepared ledger head is stale");
        }
        {
            Stmt meta(db_, "SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1", "sqlite-wal effect transition metadata check prepare failed");
            if (sqlite3_step(meta.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition metadata row absent inside transaction");
            const long long meta_count = sqlite3_column_int64(meta.stmt, 0);
            const std::string meta_head = column_text(meta.stmt, 1);
            if (meta_count != effect_transition_line_count_ || meta_head != effect_transition_head_hash_) {
                throw std::runtime_error("sqlite-wal effect transition detected split-brain transition chain head and failed closed");
            }
            if (!expected_transition_previous_hash.empty() && meta_head != expected_transition_previous_hash) throw std::runtime_error("sqlite-wal effect transition signed intent transition head is stale");
        }
        {
            Stmt prepared(db_, "SELECT sequence, entry_hash FROM ledger_entries WHERE effect_idempotency_key=? LIMIT 1", "sqlite-wal effect transition prepared-effect lookup prepare failed");
            bind_text_or_throw(db_, prepared.stmt, 1, effect_idempotency_key, "sqlite-wal effect transition bind prepared key failed");
            if (sqlite3_step(prepared.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition prepared-effect row disappeared");
            const long long current_prepared_sequence = sqlite3_column_int64(prepared.stmt, 0);
            const std::string current_prepared_hash = column_text(prepared.stmt, 1);
            if (current_prepared_sequence != prepared_sequence || current_prepared_hash != prepared_entry_hash) throw std::runtime_error("sqlite-wal effect transition prepared-effect evidence changed before terminal append");
        }
        {
            Stmt duplicate(db_, "SELECT 1 FROM effect_transitions WHERE effect_idempotency_key=? LIMIT 1", "sqlite-wal effect transition duplicate lookup prepare failed");
            bind_text_or_throw(db_, duplicate.stmt, 1, effect_idempotency_key, "sqlite-wal effect transition bind duplicate key failed");
            if (sqlite3_step(duplicate.stmt) == SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition duplicate terminal row detected");
        }
        {
            Stmt duplicate_intent(db_, "SELECT 1 FROM effect_transitions WHERE transition_intent_id=? LIMIT 1", "sqlite-wal effect transition duplicate intent lookup prepare failed");
            bind_text_or_throw(db_, duplicate_intent.stmt, 1, transition_intent_id, "sqlite-wal effect transition bind duplicate intent id failed");
            if (sqlite3_step(duplicate_intent.stmt) == SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition duplicate signed intent id detected");
        }
        {
            Stmt outbox_state(db_, "SELECT outbox_state FROM effect_outbox WHERE effect_idempotency_key=? AND prepared_sequence=? AND prepared_entry_hash=? LIMIT 1", "sqlite-wal effect transition outbox-state lookup prepare failed");
            bind_text_or_throw(db_, outbox_state.stmt, 1, effect_idempotency_key, "sqlite-wal effect transition bind outbox state key failed");
            bind_int64_or_throw(db_, outbox_state.stmt, 2, prepared_sequence, "sqlite-wal effect transition bind outbox state sequence failed");
            bind_text_or_throw(db_, outbox_state.stmt, 3, prepared_entry_hash, "sqlite-wal effect transition bind outbox state hash failed");
            if (sqlite3_step(outbox_state.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect transition could not find matching outbox row");
            prior_outbox_state = column_text(outbox_state.stmt, 0);
            if (!is_nonterminal_effect_outbox_state(prior_outbox_state)) throw std::runtime_error("sqlite-wal effect transition refuses terminal or malformed outbox state");
        }
        {
            Stmt insert(db_, "INSERT INTO effect_transitions(sequence,previous_hash,transition_hash,ledger_instance_id,effect_idempotency_key,prepared_sequence,prepared_entry_hash,terminal_state,result_digest_sha256,transition_reason,transition_intent_id,transition_intent_signer_kid,transition_intent_sha256) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", "sqlite-wal effect transition insert prepare failed");
            bind_int64_or_throw(db_, insert.stmt, 1, sequence, "sqlite-wal effect transition bind sequence failed");
            bind_text_or_throw(db_, insert.stmt, 2, previous_hash, "sqlite-wal effect transition bind previous hash failed");
            bind_text_or_throw(db_, insert.stmt, 3, transition_hash, "sqlite-wal effect transition bind transition hash failed");
            bind_text_or_throw(db_, insert.stmt, 4, ledger_instance_id_, "sqlite-wal effect transition bind ledger instance id failed");
            bind_text_or_throw(db_, insert.stmt, 5, effect_idempotency_key, "sqlite-wal effect transition bind effect key failed");
            bind_int64_or_throw(db_, insert.stmt, 6, prepared_sequence, "sqlite-wal effect transition bind prepared sequence failed");
            bind_text_or_throw(db_, insert.stmt, 7, prepared_entry_hash, "sqlite-wal effect transition bind prepared entry hash failed");
            bind_text_or_throw(db_, insert.stmt, 8, terminal_state, "sqlite-wal effect transition bind terminal state failed");
            bind_text_or_throw(db_, insert.stmt, 9, result_digest_sha256, "sqlite-wal effect transition bind result digest failed");
            bind_text_or_throw(db_, insert.stmt, 10, transition_reason, "sqlite-wal effect transition bind reason failed");
            bind_text_or_throw(db_, insert.stmt, 11, transition_intent_id, "sqlite-wal effect transition bind signed intent id failed");
            bind_text_or_throw(db_, insert.stmt, 12, transition_intent_signer_kid, "sqlite-wal effect transition bind signed intent signer failed");
            bind_text_or_throw(db_, insert.stmt, 13, transition_intent_sha256, "sqlite-wal effect transition bind signed intent digest failed");
            if (sqlite3_step(insert.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal effect transition insert failed");
        }
        {
            Stmt outbox_update(db_, "UPDATE effect_outbox SET outbox_state=?, last_result_digest_sha256=?, updated_at_sequence=? WHERE effect_idempotency_key=? AND prepared_sequence=? AND prepared_entry_hash=? AND outbox_state IN ('reserved','inflight')", "sqlite-wal effect outbox terminal update prepare failed");
            bind_text_or_throw(db_, outbox_update.stmt, 1, terminal_state, "sqlite-wal effect outbox bind terminal state failed");
            bind_text_or_throw(db_, outbox_update.stmt, 2, result_digest_sha256, "sqlite-wal effect outbox bind result digest failed");
            bind_int64_or_throw(db_, outbox_update.stmt, 3, sequence, "sqlite-wal effect outbox bind transition sequence failed");
            bind_text_or_throw(db_, outbox_update.stmt, 4, effect_idempotency_key, "sqlite-wal effect outbox bind effect key failed");
            bind_int64_or_throw(db_, outbox_update.stmt, 5, prepared_sequence, "sqlite-wal effect outbox bind prepared sequence failed");
            bind_text_or_throw(db_, outbox_update.stmt, 6, prepared_entry_hash, "sqlite-wal effect outbox bind prepared entry hash failed");
            if (sqlite3_step(outbox_update.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal effect outbox terminal update failed");
            if (sqlite3_changes(db_) != 1) throw std::runtime_error("sqlite-wal effect transition could not claim exactly one reserved outbox row");
        }
        {
            Stmt update(db_, "UPDATE effect_transition_metadata SET line_count=?, head_hash=? WHERE id=1", "sqlite-wal effect transition metadata update prepare failed");
            bind_int64_or_throw(db_, update.stmt, 1, sequence, "sqlite-wal effect transition bind metadata count failed");
            bind_text_or_throw(db_, update.stmt, 2, transition_hash, "sqlite-wal effect transition bind metadata head failed");
            if (sqlite3_step(update.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal effect transition metadata update failed");
        }
        sqlite_exec_or_throw(db_, "COMMIT;", "sqlite-wal effect transition commit failed");
        transactions_++;
        effect_transition_line_count_ = sequence;
        effect_transition_head_hash_ = transition_hash;
        terminal_effect_states_[effect_idempotency_key] = terminal_state;
        if (prior_outbox_state == kEffectOutboxReservedState && effect_outbox_reserved_ > 0) effect_outbox_reserved_--;
        if (prior_outbox_state == kEffectOutboxInflightState && effect_outbox_inflight_ > 0) effect_outbox_inflight_--;
        effect_outbox_terminal_++;
        effect_terminal_transitions_++;
        reason = "sqlite-wal effect transition committed append-only terminal state " + terminal_state;
        return true;
    } catch (const std::exception& e) {
        char* err = nullptr;
        sqlite3_exec(db_, "ROLLBACK;", nullptr, nullptr, &err);
        if (err) sqlite3_free(err);
        reason = e.what();
        effect_transition_rejections_++;
        return false;
    }
}

bool SqliteWalReplayLedger::stage(const Json& tc, const Json& claims, const std::string& action, std::string& reason) {
    if (!enabled_) return true;
    const std::string jti = claims.at("jti").str();
    if (jti.empty()) { reason = "sqlite-wal replay ledger refuses empty jti"; return false; }
    PendingSqliteEntry row;
    row.sequence = durable_line_count_ + static_cast<long long>(pending_.size()) + 1;
    row.previous_hash = pending_.empty() ? durable_head_hash_ : pending_.back().entry_hash;
    row.case_id = tc.at("case_id").str();
    row.kind = tc.at("kind").str();
    row.operation_id = claims.at("operation_id").str();
    row.contract_digest = claims.at("contract_digest_sha256").str();
    if (row.operation_id.empty()) { reason = "sqlite-wal replay ledger refuses empty verified operation_id"; return false; }
    if (!is_lower_hex_sha256(row.contract_digest)) { reason = "sqlite-wal replay ledger refuses invalid verified contract_digest_sha256"; return false; }
    row.jti = jti;
    row.action = action;
    row.cloud_event_source = tc.at("cloud_event_source").str();
    row.cloud_event_id = tc.at("cloud_event_id").str();
    row.effect_idempotency_key = effect_idempotency_key_from_case_or_legacy(tc, claims);
    row.effect_state = effect_state_from_case_or_default(tc);
    if (!is_lower_hex_sha256(row.effect_idempotency_key)) { reason = "sqlite-wal replay ledger refuses invalid effect_idempotency_key"; return false; }
    if (row.effect_state != kPreparedEffectState) { reason = "sqlite-wal replay ledger refuses non-prepared effect_state"; return false; }
    if (!populate_ingress_sender_replay_from_case(tc, row, reason)) return false;
    if (contains_ingress_sender_replay_nonce(row)) { reason = "sqlite-wal ingress sender replay nonce was already reserved"; return false; }
    if (contains_jti(jti)) { reason = "durable replay ledger already contains JWT jti"; return false; }
    if (contains_effect_idempotency_key(row.effect_idempotency_key)) { reason = "durable replay ledger already contains prepared effect idempotency key"; return false; }
    const std::string event_key = row.kind == "asyncapi" ? event_identity_key(row.cloud_event_source, row.cloud_event_id) : std::string();
    if (row.kind == "asyncapi") {
        if (event_key.empty()) { reason = "sqlite-wal replay ledger refuses async event without CloudEvents source/id identity"; return false; }
        if (contains_event_identity(row.cloud_event_source, row.cloud_event_id)) { reason = "durable replay ledger already contains CloudEvents source/id identity"; return false; }
    }
    row.entry_hash = ReplayLedger::compute_entry_hash(row.sequence, row.previous_hash, row.case_id, row.kind, row.operation_id, row.contract_digest, row.jti, row.action, row.cloud_event_source, row.cloud_event_id, row.effect_idempotency_key, row.effect_state);
    pending_.push_back(row);
    staged_jtis_.insert(jti);
    if (!event_key.empty()) staged_event_identities_.insert(event_key);
    staged_effect_idempotency_keys_.insert(row.effect_idempotency_key);
    if (row.ingress_sender_replay_required) staged_ingress_sender_replay_nonce_keys_.insert(ingress_sender_replay_nonce_stage_key(row));
    batch_pending_entries_peak_ = std::max<long long>(batch_pending_entries_peak_, static_cast<long long>(pending_.size()));
    if (commit_mode_ == "immediate") return run_commit(reason);
    reason = "sqlite-wal replay ledger staged row for explicit batch commit";
    return true;
}

void SqliteWalReplayLedger::insert_pending_row(sqlite3_stmt* stmt, const PendingSqliteEntry& row) {
    sqlite3_reset(stmt);
    sqlite3_clear_bindings(stmt);
    bind_int64_or_throw(db_, stmt, 1, row.sequence, "sqlite-wal bind sequence failed");
    bind_text_or_throw(db_, stmt, 2, row.previous_hash, "sqlite-wal bind previous hash failed");
    bind_text_or_throw(db_, stmt, 3, row.entry_hash, "sqlite-wal bind entry hash failed");
    bind_text_or_throw(db_, stmt, 4, row.case_id, "sqlite-wal bind case id failed");
    bind_text_or_throw(db_, stmt, 5, row.kind, "sqlite-wal bind kind failed");
    bind_text_or_throw(db_, stmt, 6, row.operation_id, "sqlite-wal bind operation id failed");
    bind_text_or_throw(db_, stmt, 7, row.contract_digest, "sqlite-wal bind contract digest failed");
    bind_text_or_throw(db_, stmt, 8, row.jti, "sqlite-wal bind jti failed");
    bind_text_or_throw(db_, stmt, 9, row.action, "sqlite-wal bind action failed");
    bind_text_or_throw(db_, stmt, 10, row.cloud_event_source, "sqlite-wal bind event source failed");
    bind_text_or_throw(db_, stmt, 11, row.cloud_event_id, "sqlite-wal bind event id failed");
    bind_text_or_throw(db_, stmt, 12, row.effect_idempotency_key, "sqlite-wal bind effect idempotency key failed");
    bind_text_or_throw(db_, stmt, 13, row.effect_state, "sqlite-wal bind effect state failed");
    int rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal replay ledger insert failed");
}

bool SqliteWalReplayLedger::run_commit(std::string& reason) {
    if (!enabled_ || pending_.empty()) return true;
    try {
        const PendingSqliteEntry last = pending_.back();
        {
            sqlite_exec_or_throw(db_, "BEGIN IMMEDIATE;", "sqlite-wal replay ledger begin-immediate failed");
            Stmt meta(db_, "SELECT line_count, head_hash FROM metadata WHERE id=1", "sqlite-wal metadata check prepare failed");
            if (sqlite3_step(meta.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal metadata row absent inside transaction");
            long long meta_count = sqlite3_column_int64(meta.stmt, 0);
            std::string meta_head = column_text(meta.stmt, 1);
            if (meta_count != durable_line_count_ || meta_head != durable_head_hash_) {
                sqlite_exec_or_throw(db_, "ROLLBACK;", "sqlite-wal rollback after split-head failed");
                reason = "sqlite-wal replay ledger detected split-brain chain head and failed closed";
                return false;
            }
            Stmt insert(db_, "INSERT INTO ledger_entries(sequence,previous_hash,entry_hash,case_id,kind,operation_id,contract_digest_sha256,jti,action,cloud_event_source,cloud_event_id,effect_idempotency_key,effect_state) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", "sqlite-wal insert prepare failed");
            Stmt outbox(db_, "INSERT INTO effect_outbox(effect_idempotency_key,prepared_sequence,prepared_entry_hash,outbox_state,dispatch_attempts,last_result_digest_sha256,updated_at_sequence) VALUES(?,?,?,?,0,'',?)", "sqlite-wal effect outbox insert prepare failed");
            Stmt replay_prune(db_, "DELETE FROM ingress_sender_replay_cache WHERE issued_at_epoch < ?", "sqlite-wal ingress sender replay prune prepare failed");
            Stmt sender_replay(db_, "INSERT INTO ingress_sender_replay_cache(replay_key_sha256,format,service_config_sha256,ingress_profile_sha256,sender_replay_cache_instance_id,sender_proof_kid,principal,nonce,issued_at_epoch,observed_at_epoch,replay_window_seconds,material_sha256,prepared_sequence,prepared_entry_hash,effect_idempotency_key) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", "sqlite-wal ingress sender replay insert prepare failed");
            for (const auto& row : pending_) {
                insert_pending_row(insert.stmt, row);
                sqlite3_reset(outbox.stmt);
                sqlite3_clear_bindings(outbox.stmt);
                bind_text_or_throw(db_, outbox.stmt, 1, row.effect_idempotency_key, "sqlite-wal effect outbox bind effect key failed");
                bind_int64_or_throw(db_, outbox.stmt, 2, row.sequence, "sqlite-wal effect outbox bind prepared sequence failed");
                bind_text_or_throw(db_, outbox.stmt, 3, row.entry_hash, "sqlite-wal effect outbox bind prepared entry hash failed");
                bind_text_or_throw(db_, outbox.stmt, 4, kEffectOutboxReservedState, "sqlite-wal effect outbox bind reserved state failed");
                bind_int64_or_throw(db_, outbox.stmt, 5, row.sequence, "sqlite-wal effect outbox bind updated sequence failed");
                if (sqlite3_step(outbox.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal effect outbox insert failed");
                if (row.ingress_sender_replay_required) {
                    sqlite3_reset(replay_prune.stmt);
                    sqlite3_clear_bindings(replay_prune.stmt);
                    bind_int64_or_throw(db_, replay_prune.stmt, 1,
                                        row.ingress_sender_replay_observed_at_epoch - row.ingress_sender_replay_window_seconds,
                                        "sqlite-wal ingress sender replay prune bind cutoff failed");
                    if (sqlite3_step(replay_prune.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal ingress sender replay prune failed");
                    sqlite3_reset(sender_replay.stmt);
                    sqlite3_clear_bindings(sender_replay.stmt);
                    bind_text_or_throw(db_, sender_replay.stmt, 1, row.ingress_sender_replay_key_sha256, "sqlite-wal ingress sender replay bind replay key failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 2, row.ingress_sender_replay_format, "sqlite-wal ingress sender replay bind format failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 3, row.ingress_sender_replay_service_config_sha256, "sqlite-wal ingress sender replay bind service config digest failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 4, row.ingress_sender_replay_profile_sha256, "sqlite-wal ingress sender replay bind profile digest failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 5, row.ingress_sender_replay_cache_instance_id, "sqlite-wal ingress sender replay bind instance id failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 6, row.ingress_sender_replay_proof_kid, "sqlite-wal ingress sender replay bind proof kid failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 7, row.ingress_sender_replay_principal, "sqlite-wal ingress sender replay bind principal failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 8, row.ingress_sender_replay_nonce, "sqlite-wal ingress sender replay bind nonce failed");
                    bind_int64_or_throw(db_, sender_replay.stmt, 9, row.ingress_sender_replay_issued_at_epoch, "sqlite-wal ingress sender replay bind issued-at failed");
                    bind_int64_or_throw(db_, sender_replay.stmt, 10, row.ingress_sender_replay_observed_at_epoch, "sqlite-wal ingress sender replay bind observed-at failed");
                    bind_int64_or_throw(db_, sender_replay.stmt, 11, row.ingress_sender_replay_window_seconds, "sqlite-wal ingress sender replay bind window failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 12, row.ingress_sender_replay_material_sha256, "sqlite-wal ingress sender replay bind material digest failed");
                    bind_int64_or_throw(db_, sender_replay.stmt, 13, row.sequence, "sqlite-wal ingress sender replay bind prepared sequence failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 14, row.entry_hash, "sqlite-wal ingress sender replay bind prepared hash failed");
                    bind_text_or_throw(db_, sender_replay.stmt, 15, row.effect_idempotency_key, "sqlite-wal ingress sender replay bind effect key failed");
                    const int replay_rc = sqlite3_step(sender_replay.stmt);
                    if (replay_rc == SQLITE_CONSTRAINT) {
                        throw std::runtime_error("sqlite-wal ingress sender replay nonce was already reserved; prepared ledger entry and outbox reservation were rolled back in the same transaction");
                    }
                    if (replay_rc != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal ingress sender replay insert failed");
                }
            }
            Stmt update(db_, "UPDATE metadata SET line_count=?, head_hash=? WHERE id=1", "sqlite-wal metadata update prepare failed");
            bind_int64_or_throw(db_, update.stmt, 1, last.sequence, "sqlite-wal bind metadata count failed");
            bind_text_or_throw(db_, update.stmt, 2, last.entry_hash, "sqlite-wal bind metadata head failed");
            if (sqlite3_step(update.stmt) != SQLITE_DONE) sqlite_throw(db_, "sqlite-wal metadata update failed");
            sqlite_exec_or_throw(db_, "COMMIT;", "sqlite-wal replay ledger commit failed");
        }
        transactions_++;
        if (commit_mode_ == "batch") batch_flush_commits_++;
        appended_entries_ += static_cast<long long>(pending_.size());
        durable_line_count_ = last.sequence;
        durable_head_hash_ = last.entry_hash;
        for (const auto& row : pending_) {
            committed_jtis_.insert(row.jti);
            const std::string event_key = row.kind == "asyncapi" ? event_identity_key(row.cloud_event_source, row.cloud_event_id) : std::string();
            if (!event_key.empty()) committed_event_identities_.insert(event_key);
            committed_effect_idempotency_keys_.insert(row.effect_idempotency_key);
            prepared_effect_refs_[row.effect_idempotency_key] = PreparedEffectReference{row.sequence, row.entry_hash, row.effect_idempotency_key};
            effect_outbox_reserved_++;
        }
        pending_.clear();
        staged_jtis_.clear();
        staged_event_identities_.clear();
        staged_effect_idempotency_keys_.clear();
        staged_ingress_sender_replay_nonce_keys_.clear();
        int log_frames = 0;
        int checkpointed_frames = 0;
        int rc = sqlite3_wal_checkpoint_v2(db_, nullptr, SQLITE_CHECKPOINT_PASSIVE, &log_frames, &checkpointed_frames);
        if (rc == SQLITE_OK || rc == SQLITE_BUSY || rc == SQLITE_LOCKED) wal_checkpoints_++;
        else sqlite_throw(db_, "sqlite-wal checkpoint failed");
        reason = "sqlite-wal replay ledger committed staged rows with BEGIN IMMEDIATE and WAL/FULL synchronous profile; integrated ingress sender replay rows, prepared ledger entries, and outbox reservations share the same transaction when supplied";
        return true;
    } catch (const std::exception& e) {
        char* err = nullptr;
        sqlite3_exec(db_, "ROLLBACK;", nullptr, nullptr, &err);
        if (err) sqlite3_free(err);
        pending_.clear();
        staged_jtis_.clear();
        staged_event_identities_.clear();
        staged_effect_idempotency_keys_.clear();
        staged_ingress_sender_replay_nonce_keys_.clear();
        reason = e.what();
        return false;
    }
}

bool SqliteWalReplayLedger::commit(std::string& reason) {
    return run_commit(reason);
}

bool SqliteWalReplayLedger::backup_snapshot(const std::string& snapshot_path, std::string& reason) {
    if (snapshot_path.empty()) return true;
    if (!enabled_ || !db_) { reason = "sqlite-wal replay ledger snapshot requested while backend is disabled"; return false; }
    if (!pending_.empty()) {
        if (!run_commit(reason)) return false;
    }
    try {
        reject_sqlite_family_symlinks(snapshot_path);
        unlink_sqlite_family(snapshot_path);
        std::filesystem::path parent = std::filesystem::path(snapshot_path).parent_path();
        if (!parent.empty()) std::filesystem::create_directories(parent);
        sqlite3* dst = nullptr;
        int flags = sqlite_open_flags_for_ledger();
        dst = sqlite_open_or_throw(snapshot_path, flags, "sqlite-wal snapshot destination open failed");
        sqlite3_backup* backup = sqlite3_backup_init(dst, "main", db_, "main");
        if (!backup) {
            reason = std::string("sqlite-wal backup init failed: ") + sqlite3_errmsg(dst);
            sqlite_close_best_effort(dst);
            return false;
        }
        int rc = sqlite3_backup_step(backup, -1);
        int finish_rc = sqlite3_backup_finish(backup);
        if (finish_rc != SQLITE_OK || (rc != SQLITE_DONE && rc != SQLITE_OK)) {
            reason = std::string("sqlite-wal backup step/finish failed: ") + sqlite3_errmsg(dst);
            sqlite_close_best_effort(dst);
            return false;
        }
        sqlite_close_or_throw(dst, "sqlite-wal snapshot destination close failed");
        // Verify the snapshot with the dedicated read-only verifier so untrusted snapshot bytes are
        // not judged through the mutable backend loader or allowed to create write-gate sidecars.
        ReplayLedgerStats verifier_stats = verify_sqlite_ledger_snapshot_readonly(snapshot_path, "sqlite-wal backup snapshot read-only verifier");
        if (verifier_stats.loaded_entries != durable_line_count_) {
            reason = "sqlite-wal backup snapshot loaded entry count does not match committed ledger";
            return false;
        }
        backup_snapshots_++;
        snapshot_verifications_++;
        reason = "sqlite-wal replay ledger wrote verified sqlite3_backup snapshot with backend-profile/hash-chain verification";
        return true;
    } catch (const std::exception& e) {
        pending_.clear();
        staged_jtis_.clear();
        staged_event_identities_.clear();
        staged_effect_idempotency_keys_.clear();
        staged_ingress_sender_replay_nonce_keys_.clear();
        reason = e.what();
        return false;
    }
}

void SqliteWalReplayLedger::close() {
    if (db_) {
        std::string ignored;
        (void)commit(ignored);
        sqlite3_close(db_);
        db_ = nullptr;
    }
    enabled_ = false;
    write_gate_.reset();
}

ReplayLedgerStats SqliteWalReplayLedger::stats() const {
    ReplayLedgerStats st;
    st.backend_name = backend_name();
    st.loaded_entries = loaded_entries_;
    st.appended_entries = appended_entries_;
    st.sqlite_transactions = transactions_;
    st.sqlite_wal_checkpoints = wal_checkpoints_;
    st.sqlite_integrity_checks = integrity_checks_;
    st.sqlite_profile_checks = profile_checks_;
    st.sqlite_corruption_rejections = corruption_rejections_;
    st.sqlite_backup_snapshots = backup_snapshots_;
    st.sqlite_snapshot_verifications = snapshot_verifications_;
    st.sqlite_snapshot_restores = snapshot_restores_;
    st.sqlite_snapshot_manifest_verifications = 0;
    st.sqlite_restore_rollback_guard_checks = 0;
    st.durable_line_count = durable_line_count_;
    st.durable_head_hash = durable_head_hash_;
    st.batch_flush_commits = batch_flush_commits_;
    st.batch_pending_entries_peak = batch_pending_entries_peak_;
    st.effect_terminal_transitions = effect_terminal_transitions_;
    st.effect_transition_rejections = effect_transition_rejections_;
    st.effect_transition_line_count = effect_transition_line_count_;
    st.effect_transition_head_hash = effect_transition_head_hash_;
    st.effect_outbox_reserved = effect_outbox_reserved_;
    st.effect_outbox_inflight = effect_outbox_inflight_;
    st.effect_outbox_terminal = effect_outbox_terminal_;
    st.backend_factory_selections = 1;
    return st;
}

bool mark_sqlite_effect_terminal_authorized_internal(const std::string& ledger_path,
                                                     const VerifiedEffectTransitionIntent& intent,
                                                     std::string& reason) {
    SqliteWalReplayLedger ledger;
    ledger.load(ledger_path, false, "immediate");
    const bool ok = ledger.mark_effect_terminal(intent.effect_idempotency_key,
                                                intent.prepared_sequence,
                                                intent.prepared_entry_hash,
                                                intent.terminal_state,
                                                intent.result_digest_sha256,
                                                intent.transition_reason,
                                                intent.prepared_ledger_head_hash,
                                                intent.effect_transition_previous_hash,
                                                intent.ledger_instance_id,
                                                intent.intent_id,
                                                intent.signer_kid,
                                                intent.intent_sha256,
                                                reason);
    ledger.close();
    return ok;
}

EffectOutboxClaimResult claim_sqlite_effect_outbox_authorized_internal(const std::string& ledger_path,
                                                                       const std::string& worker_id,
                                                                       long long now_epoch,
                                                                       long long lease_seconds) {
    SqliteWalReplayLedger ledger;
    ledger.load(ledger_path, false, "immediate");
    EffectOutboxClaimResult out = ledger.claim_next_outbox(worker_id, now_epoch, lease_seconds);
    ledger.close();
    return out;
}

std::string sqlite_effect_outbox_claim_report_json(const EffectOutboxClaimResult& claim, long long lease_seconds) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << json_escape(kEffectOutboxClaimFormat) << "\",\n"
        << "  \"backend_name\": \"sqlite-wal\",\n"
        << "  \"revision_id\": \"rev0634\",\n"
        << "  \"claimed\": " << (claim.claimed ? "true" : "false") << ",\n"
        << "  \"ledger_instance_id\": \"" << json_escape(claim.ledger_instance_id) << "\",\n"
        << "  \"decision_head_hash\": \"" << json_escape(claim.decision_head_hash) << "\",\n"
        << "  \"effect_transition_head_hash\": \"" << json_escape(claim.effect_transition_head_hash) << "\",\n"
        << "  \"worker_id\": \"" << json_escape(claim.worker_id) << "\",\n"
        << "  \"lease_seconds\": " << lease_seconds << ",\n"
        << "  \"claim\": {\n"
        << "    \"worker_claim_id\": \"" << json_escape(claim.worker_claim_id) << "\",\n"
        << "    \"effect_idempotency_key\": \"" << json_escape(claim.effect_idempotency_key) << "\",\n"
        << "    \"prepared_sequence\": " << claim.prepared_sequence << ",\n"
        << "    \"prepared_entry_hash\": \"" << json_escape(claim.prepared_entry_hash) << "\",\n"
        << "    \"dispatch_attempts\": " << claim.dispatch_attempts << ",\n"
        << "    \"claimed_at_epoch\": " << claim.claimed_at_epoch << ",\n"
        << "    \"lease_expires_at_epoch\": " << claim.lease_expires_at_epoch << ",\n"
        << "    \"previous_outbox_state\": \"" << json_escape(claim.previous_outbox_state) << "\",\n"
        << "    \"outbox_state\": \"" << (claim.claimed ? kEffectOutboxInflightState : "") << "\"\n"
        << "  }\n"
        << "}\n";
    return out.str();
}


std::string compute_relay_downstream_result_digest(const EffectOutboxClaimResult& claim,
                                                 const std::string& terminal_state,
                                                 const RelayAdapterProvenance& provenance) {
    return sha256_hex(length_prefixed_security_tuple(kEffectRelayResultMaterialVersion, {
        {"store_format", kEffectRelayDownstreamStoreFormat},
        {"effect_idempotency_key", claim.effect_idempotency_key},
        {"prepared_sequence", std::to_string(claim.prepared_sequence)},
        {"prepared_entry_hash", claim.prepared_entry_hash},
        {"terminal_state", terminal_state},
        {"adapter_id", provenance.adapter_id},
        {"adapter_kind", provenance.adapter_kind},
        {"adapter_config_sha256", provenance.adapter_config_sha256},
        {"config_handle", provenance.config_handle},
        {"registry_sha256", provenance.registry_sha256},
    }));
}

bool relay_provenance_matches(const RelayAdapterProvenance& provenance,
                              const std::string& adapter_id,
                              const std::string& adapter_kind,
                              const std::string& adapter_config_sha256,
                              const std::string& config_handle,
                              const std::string& registry_sha256) {
    return provenance.adapter_id == adapter_id &&
           provenance.adapter_kind == adapter_kind &&
           provenance.adapter_config_sha256 == adapter_config_sha256 &&
           provenance.config_handle == config_handle &&
           provenance.registry_sha256 == registry_sha256;
}

void validate_effect_relay_inputs(const std::string& downstream_path,
                                  const std::string& terminal_state,
                                  const std::string& signer_private_key_pem_path,
                                  const std::string& signer_kid,
                                  const std::string& trust_profile_path,
                                  const std::string& trust_profile_sha256,
                                  const std::string& relay_report_path) {
    if (downstream_path.empty()) throw std::runtime_error("sqlite-wal effect relay requires a downstream store path");
    if (!is_terminal_effect_state(terminal_state)) throw std::runtime_error("sqlite-wal effect relay requires terminal_state applied|failed|compensated");
    if (signer_private_key_pem_path.empty()) throw std::runtime_error("sqlite-wal effect relay requires signer private-key PEM path");
    if (signer_kid.empty() || contains_disallowed_security_control(signer_kid)) throw std::runtime_error("sqlite-wal effect relay requires nonempty control-free signer kid");
    if (trust_profile_path.empty() || !is_lower_hex_sha256(trust_profile_sha256)) throw std::runtime_error("sqlite-wal effect relay requires digest-pinned transition trust profile");
    if (relay_report_path.empty()) throw std::runtime_error("sqlite-wal effect relay requires a relay report path");
}


void validate_relay_adapter_label(const std::string& field_name, const std::string& value) {
    if (value.empty()) throw std::runtime_error("sqlite-wal configured effect relay requires nonempty " + field_name);
    if (value.size() > 128) throw std::runtime_error("sqlite-wal configured effect relay refuses oversized " + field_name);
    if (contains_disallowed_security_control(value)) throw std::runtime_error("sqlite-wal configured effect relay refuses control characters in " + field_name);
    for (char c : value) {
        const unsigned char u = static_cast<unsigned char>(c);
        if (u < 0x21 || u > 0x7e) throw std::runtime_error("sqlite-wal configured effect relay requires printable ASCII without spaces in " + field_name);
    }
}

RelayAdapterConfig load_relay_adapter_config_with_digest_pin(const std::string& config_path,
                                                             const std::string& expected_sha256,
                                                             long long now_epoch,
                                                             bool inject_crash_after_downstream) {
    if (config_path.empty()) throw std::runtime_error("sqlite-wal configured effect relay requires a relay adapter config path");
    if (!is_lower_hex_sha256(expected_sha256)) throw std::runtime_error("sqlite-wal configured effect relay requires a lowercase sha256 adapter config pin");
    const std::string text = read_file(config_path);
    const std::string actual_sha256 = sha256_hex(text);
    if (actual_sha256 != expected_sha256) throw std::runtime_error("sqlite-wal configured effect relay adapter config digest pin mismatch");
    Json root = parse_json_text(text);
    RelayAdapterConfig cfg;
    cfg.config_path = config_path;
    cfg.config_sha256 = actual_sha256;
    if (root.at("format").str() != kEffectRelayAdapterConfigFormat) throw std::runtime_error("sqlite-wal configured effect relay adapter config has unsupported format");
    cfg.adapter_id = root.at("adapter_id").str();
    cfg.adapter_kind = root.at("adapter_kind").str();
    cfg.downstream_path = root.at("downstream_store_path").str();
    cfg.worker_id = root.at("worker_id").str();
    cfg.lease_seconds = root.at("lease_seconds").integer(0);
    cfg.terminal_state = root.at("terminal_state").str();
    cfg.signer_private_key_pem_path = root.at("signer_private_key_pem_path").str();
    cfg.signer_kid = root.at("signer_kid").str();
    cfg.trust_profile_path = root.at("transition_trust_profile_path").str();
    cfg.trust_profile_sha256 = root.at("transition_trust_profile_sha256").str();
    cfg.debug_inject_crash_after_downstream_allowed = root.at("debug_inject_crash_after_downstream_allowed").boolean(false);
    validate_relay_adapter_label("adapter_id", cfg.adapter_id);
    if (cfg.adapter_kind != kEffectRelayAdapterKindLocalSqlite) throw std::runtime_error("sqlite-wal configured effect relay adapter_kind is not supported");
    validate_outbox_worker_claim_inputs(cfg.worker_id, now_epoch, cfg.lease_seconds);
    validate_effect_relay_inputs(cfg.downstream_path,
                                 cfg.terminal_state,
                                 cfg.signer_private_key_pem_path,
                                 cfg.signer_kid,
                                 cfg.trust_profile_path,
                                 cfg.trust_profile_sha256,
                                 "configured-relay-report-placeholder");
    if (inject_crash_after_downstream && !cfg.debug_inject_crash_after_downstream_allowed) {
        throw std::runtime_error("sqlite-wal configured effect relay refuses injected crash unless adapter config explicitly enables the test hook");
    }
    return cfg;
}


RelayHandleResolution load_relay_adapter_config_from_registry_with_digest_pin(const std::string& registry_path,
                                                                               const std::string& expected_registry_sha256,
                                                                               const std::string& config_handle,
                                                                               long long now_epoch,
                                                                               bool inject_crash_after_downstream) {
    if (registry_path.empty()) throw std::runtime_error("sqlite-wal handle-bound effect relay requires an adapter registry path");
    if (!is_lower_hex_sha256(expected_registry_sha256)) throw std::runtime_error("sqlite-wal handle-bound effect relay requires a lowercase sha256 adapter registry pin");
    validate_relay_adapter_label("config_handle", config_handle);
    const std::string registry_text = read_file(registry_path);
    const std::string actual_registry_sha256 = sha256_hex(registry_text);
    if (actual_registry_sha256 != expected_registry_sha256) throw std::runtime_error("sqlite-wal handle-bound effect relay registry digest pin mismatch");
    Json root = parse_json_text(registry_text);
    if (root.at("format").str() != kEffectRelayHandleRegistryFormat) throw std::runtime_error("sqlite-wal handle-bound effect relay registry has unsupported format");
    const Json& entries = root.at("entries");
    if (!entries.is_array()) throw std::runtime_error("sqlite-wal handle-bound effect relay registry requires entries array");
    std::set<std::string> seen_handles;
    const Json* selected = nullptr;
    for (const auto& entry : entries.a) {
        if (!entry.is_object()) throw std::runtime_error("sqlite-wal handle-bound effect relay registry entry must be an object");
        const std::string handle = entry.at("handle").str();
        validate_relay_adapter_label("registry entry handle", handle);
        if (!seen_handles.insert(handle).second) throw std::runtime_error("sqlite-wal handle-bound effect relay registry contains duplicate handle");
        if (handle == config_handle) selected = &entry;
    }
    if (selected == nullptr) throw std::runtime_error("sqlite-wal handle-bound effect relay registry does not contain requested handle");
    if (!selected->at("enabled").boolean(false)) throw std::runtime_error("sqlite-wal handle-bound effect relay registry entry is disabled");
    const std::string config_path = selected->at("adapter_config_path").str();
    const std::string config_sha256 = selected->at("adapter_config_sha256").str();
    if (config_path.empty() || !is_lower_hex_sha256(config_sha256)) throw std::runtime_error("sqlite-wal handle-bound effect relay registry entry lacks a digest-pinned adapter config");
    RelayHandleResolution out;
    out.registry_path = registry_path;
    out.registry_sha256 = actual_registry_sha256;
    out.handle = config_handle;
    out.adapter = load_relay_adapter_config_with_digest_pin(config_path, config_sha256, now_epoch, inject_crash_after_downstream);
    if (selected->at("adapter_id").is_string() && !selected->at("adapter_id").str().empty() && selected->at("adapter_id").str() != out.adapter.adapter_id) {
        throw std::runtime_error("sqlite-wal handle-bound effect relay registry adapter_id does not match adapter config");
    }
    if (selected->at("adapter_kind").is_string() && !selected->at("adapter_kind").str().empty() && selected->at("adapter_kind").str() != out.adapter.adapter_kind) {
        throw std::runtime_error("sqlite-wal handle-bound effect relay registry adapter_kind does not match adapter config");
    }
    return out;
}

RelayDownstreamResult apply_relay_downstream_store(const std::string& downstream_path,
                                                   const EffectOutboxClaimResult& claim,
                                                   const std::string& terminal_state,
                                                   long long observed_at_epoch,
                                                   const RelayAdapterProvenance& provenance) {
    if (!claim.claimed) throw std::runtime_error("sqlite-wal effect relay cannot apply downstream without a claimed outbox row");
    if (!is_lower_hex_sha256(claim.effect_idempotency_key) || claim.prepared_sequence <= 0 || !is_lower_hex_sha256(claim.prepared_entry_hash)) {
        throw std::runtime_error("sqlite-wal effect relay refuses malformed claim evidence before downstream apply");
    }
    RelayDownstreamResult out;
    out.touched = true;
    out.terminal_state = terminal_state;
    out.result_material_version = kEffectRelayResultMaterialVersion;
    out.adapter_id = provenance.adapter_id;
    out.adapter_kind = provenance.adapter_kind;
    out.adapter_config_sha256 = provenance.adapter_config_sha256;
    out.config_handle = provenance.config_handle;
    out.registry_sha256 = provenance.registry_sha256;
    out.result_digest_sha256 = compute_relay_downstream_result_digest(claim, terminal_state, provenance);
    reject_sqlite_family_symlinks(downstream_path);
    int downstream_open_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    downstream_open_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    sqlite3* db = sqlite_open_or_throw(downstream_path, downstream_open_flags, "sqlite-wal effect relay downstream open failed");
    try {
        sqlite3_busy_timeout(db, 1000);
        sqlite_exec_or_throw(db, "PRAGMA journal_mode=WAL;", "sqlite-wal effect relay downstream WAL setup failed");
        const std::string downstream_journal = ascii_lower(sqlite_query_single_text(db, "PRAGMA journal_mode;", "sqlite-wal effect relay downstream journal_mode verification"));
        if (downstream_journal != "wal") throw std::runtime_error("sqlite-wal effect relay downstream journal_mode is not WAL");
        sqlite_exec_or_throw(db, "PRAGMA synchronous=FULL;", "sqlite-wal effect relay downstream synchronous setup failed");
        const long long downstream_synchronous = sqlite_query_single_int64(db, "PRAGMA synchronous;", "sqlite-wal effect relay downstream synchronous verification");
        if (downstream_synchronous < 2) throw std::runtime_error("sqlite-wal effect relay downstream synchronous mode is below FULL");
        sqlite_exec_or_throw(db,
            "CREATE TABLE IF NOT EXISTS downstream_profile (id INTEGER PRIMARY KEY CHECK(id=1), store_format TEXT NOT NULL, schema_version INTEGER NOT NULL);"
            "INSERT OR IGNORE INTO downstream_profile(id,store_format,schema_version) VALUES(1,'anonsync-relay-downstream-store-v2-provenance-bound',2);"
            "CREATE TABLE IF NOT EXISTS downstream_effects ("
            "effect_idempotency_key TEXT PRIMARY KEY,"
            "prepared_sequence INTEGER NOT NULL,"
            "prepared_entry_hash TEXT NOT NULL,"
            "terminal_state TEXT NOT NULL CHECK(terminal_state IN ('applied','failed','compensated')),"
            "result_digest_sha256 TEXT NOT NULL,"
            "result_material_version TEXT NOT NULL,"
            "adapter_id TEXT NOT NULL DEFAULT '',"
            "adapter_kind TEXT NOT NULL DEFAULT '',"
            "adapter_config_sha256 TEXT NOT NULL DEFAULT '',"
            "config_handle TEXT NOT NULL DEFAULT '',"
            "registry_sha256 TEXT NOT NULL DEFAULT '',"
            "first_worker_claim_id TEXT NOT NULL,"
            "last_worker_claim_id TEXT NOT NULL,"
            "first_worker_id TEXT NOT NULL,"
            "last_worker_id TEXT NOT NULL,"
            "first_observed_at_epoch INTEGER NOT NULL,"
            "last_observed_at_epoch INTEGER NOT NULL,"
            "observation_count INTEGER NOT NULL CHECK(observation_count>=1)"
            ");",
            "sqlite-wal effect relay downstream schema setup failed");
        {
            Stmt profile(db, "SELECT store_format, schema_version FROM downstream_profile WHERE id=1", "sqlite-wal effect relay downstream profile prepare failed");
            if (sqlite3_step(profile.stmt) != SQLITE_ROW) throw std::runtime_error("sqlite-wal effect relay downstream profile row missing");
            if (column_text(profile.stmt, 0) != kEffectRelayDownstreamStoreFormat || sqlite3_column_int64(profile.stmt, 1) != 2) {
                throw std::runtime_error("sqlite-wal effect relay downstream profile mismatch");
            }
        }
        sqlite_exec_or_throw(db, "BEGIN IMMEDIATE;", "sqlite-wal effect relay downstream begin failed");
        {
            Stmt existing(db, "SELECT prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, result_material_version, adapter_id, adapter_kind, adapter_config_sha256, config_handle, registry_sha256, first_worker_claim_id, observation_count FROM downstream_effects WHERE effect_idempotency_key=?", "sqlite-wal effect relay downstream existing lookup prepare failed");
            bind_text_or_throw(db, existing.stmt, 1, claim.effect_idempotency_key, "sqlite-wal effect relay downstream existing key bind failed");
            const int rc = sqlite3_step(existing.stmt);
            if (rc == SQLITE_ROW) {
                const long long existing_sequence = sqlite3_column_int64(existing.stmt, 0);
                const std::string existing_hash = column_text(existing.stmt, 1);
                const std::string existing_state = column_text(existing.stmt, 2);
                const std::string existing_digest = column_text(existing.stmt, 3);
                const std::string existing_material_version = column_text(existing.stmt, 4);
                const std::string existing_adapter_id = column_text(existing.stmt, 5);
                const std::string existing_adapter_kind = column_text(existing.stmt, 6);
                const std::string existing_adapter_config_sha256 = column_text(existing.stmt, 7);
                const std::string existing_config_handle = column_text(existing.stmt, 8);
                const std::string existing_registry_sha256 = column_text(existing.stmt, 9);
                out.first_worker_claim_id = column_text(existing.stmt, 10);
                out.observation_count = sqlite3_column_int64(existing.stmt, 11) + 1;
                if (existing_sequence != claim.prepared_sequence || existing_hash != claim.prepared_entry_hash) {
                    throw std::runtime_error("sqlite-wal effect relay downstream idempotency key conflicts with different prepared evidence");
                }
                if (!is_terminal_effect_state(existing_state) || !is_lower_hex_sha256(existing_digest) || existing_material_version != kEffectRelayResultMaterialVersion || !is_lower_hex_sha256(out.first_worker_claim_id) || out.observation_count < 2) {
                    throw std::runtime_error("sqlite-wal effect relay downstream existing row is malformed");
                }
                if (!relay_provenance_matches(provenance, existing_adapter_id, existing_adapter_kind, existing_adapter_config_sha256, existing_config_handle, existing_registry_sha256)) {
                    throw std::runtime_error("sqlite-wal effect relay downstream existing row adapter provenance does not match the configured relay boundary");
                }
                const std::string expected_existing_digest = compute_relay_downstream_result_digest(claim, existing_state, provenance);
                if (existing_digest != expected_existing_digest) {
                    throw std::runtime_error("sqlite-wal effect relay downstream existing row result digest does not match prepared evidence and adapter provenance");
                }
                out.replayed_existing = true;
                out.terminal_state = existing_state;
                out.result_digest_sha256 = existing_digest;
                out.result_material_version = existing_material_version;
                out.adapter_id = existing_adapter_id;
                out.adapter_kind = existing_adapter_kind;
                out.adapter_config_sha256 = existing_adapter_config_sha256;
                out.config_handle = existing_config_handle;
                out.registry_sha256 = existing_registry_sha256;
                Stmt update(db, "UPDATE downstream_effects SET last_worker_claim_id=?, last_worker_id=?, last_observed_at_epoch=?, observation_count=observation_count+1 WHERE effect_idempotency_key=?", "sqlite-wal effect relay downstream replay update prepare failed");
                bind_text_or_throw(db, update.stmt, 1, claim.worker_claim_id, "sqlite-wal effect relay downstream replay claim bind failed");
                bind_text_or_throw(db, update.stmt, 2, claim.worker_id, "sqlite-wal effect relay downstream replay worker bind failed");
                bind_int64_or_throw(db, update.stmt, 3, observed_at_epoch, "sqlite-wal effect relay downstream replay observed bind failed");
                bind_text_or_throw(db, update.stmt, 4, claim.effect_idempotency_key, "sqlite-wal effect relay downstream replay key bind failed");
                if (sqlite3_step(update.stmt) != SQLITE_DONE) sqlite_throw(db, "sqlite-wal effect relay downstream replay update failed");
            } else if (rc == SQLITE_DONE) {
                out.inserted = true;
                out.observation_count = 1;
                out.first_worker_claim_id = claim.worker_claim_id;
                Stmt insert(db, "INSERT INTO downstream_effects(effect_idempotency_key,prepared_sequence,prepared_entry_hash,terminal_state,result_digest_sha256,result_material_version,adapter_id,adapter_kind,adapter_config_sha256,config_handle,registry_sha256,first_worker_claim_id,last_worker_claim_id,first_worker_id,last_worker_id,first_observed_at_epoch,last_observed_at_epoch,observation_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)", "sqlite-wal effect relay downstream insert prepare failed");
                bind_text_or_throw(db, insert.stmt, 1, claim.effect_idempotency_key, "sqlite-wal effect relay downstream insert effect bind failed");
                bind_int64_or_throw(db, insert.stmt, 2, claim.prepared_sequence, "sqlite-wal effect relay downstream insert sequence bind failed");
                bind_text_or_throw(db, insert.stmt, 3, claim.prepared_entry_hash, "sqlite-wal effect relay downstream insert hash bind failed");
                bind_text_or_throw(db, insert.stmt, 4, terminal_state, "sqlite-wal effect relay downstream insert state bind failed");
                bind_text_or_throw(db, insert.stmt, 5, out.result_digest_sha256, "sqlite-wal effect relay downstream insert digest bind failed");
                bind_text_or_throw(db, insert.stmt, 6, out.result_material_version, "sqlite-wal effect relay downstream insert result material bind failed");
                bind_text_or_throw(db, insert.stmt, 7, provenance.adapter_id, "sqlite-wal effect relay downstream insert adapter id bind failed");
                bind_text_or_throw(db, insert.stmt, 8, provenance.adapter_kind, "sqlite-wal effect relay downstream insert adapter kind bind failed");
                bind_text_or_throw(db, insert.stmt, 9, provenance.adapter_config_sha256, "sqlite-wal effect relay downstream insert adapter config bind failed");
                bind_text_or_throw(db, insert.stmt, 10, provenance.config_handle, "sqlite-wal effect relay downstream insert config handle bind failed");
                bind_text_or_throw(db, insert.stmt, 11, provenance.registry_sha256, "sqlite-wal effect relay downstream insert registry bind failed");
                bind_text_or_throw(db, insert.stmt, 12, claim.worker_claim_id, "sqlite-wal effect relay downstream insert first claim bind failed");
                bind_text_or_throw(db, insert.stmt, 13, claim.worker_claim_id, "sqlite-wal effect relay downstream insert last claim bind failed");
                bind_text_or_throw(db, insert.stmt, 14, claim.worker_id, "sqlite-wal effect relay downstream insert first worker bind failed");
                bind_text_or_throw(db, insert.stmt, 15, claim.worker_id, "sqlite-wal effect relay downstream insert last worker bind failed");
                bind_int64_or_throw(db, insert.stmt, 16, observed_at_epoch, "sqlite-wal effect relay downstream insert first observed bind failed");
                bind_int64_or_throw(db, insert.stmt, 17, observed_at_epoch, "sqlite-wal effect relay downstream insert last observed bind failed");
                if (sqlite3_step(insert.stmt) != SQLITE_DONE) sqlite_throw(db, "sqlite-wal effect relay downstream insert failed");
            } else {
                sqlite_throw(db, "sqlite-wal effect relay downstream existing lookup failed");
            }
        }
        sqlite_exec_or_throw(db, "COMMIT;", "sqlite-wal effect relay downstream commit failed");
        out.last_worker_claim_id = claim.worker_claim_id;
        sqlite_close_or_throw(db, "sqlite-wal effect relay downstream close failed");
        return out;
    } catch (...) {
        char* err = nullptr;
        sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, &err);
        if (err) sqlite3_free(err);
        sqlite_close_best_effort(db);
        throw;
    }
}

std::string make_effect_transition_intent_json_for_relay(const EffectOutboxClaimResult& claim,
                                                         const RelayDownstreamResult& downstream,
                                                         const std::string& transition_reason,
                                                         const std::string& signer_kid,
                                                         EVP_PKEY* private_key) {
    const std::string issued_at = strict_utc_from_epoch(claim.claimed_at_epoch);
    const std::string intent_id = sha256_hex(length_prefixed_security_tuple("anonsync-effect-relay-transition-intent-v1", {
        {"ledger_instance_id", claim.ledger_instance_id},
        {"decision_head_hash", claim.decision_head_hash},
        {"effect_transition_head_hash", claim.effect_transition_head_hash},
        {"effect_idempotency_key", claim.effect_idempotency_key},
        {"prepared_sequence", std::to_string(claim.prepared_sequence)},
        {"prepared_entry_hash", claim.prepared_entry_hash},
        {"worker_claim_id", claim.worker_claim_id},
        {"result_digest_sha256", downstream.result_digest_sha256},
    }));
    std::ostringstream signing;
    signing << kEffectTransitionIntentFormat << "\n"
            << intent_id << "\n"
            << kEffectTransitionIntentSubject << "\n"
            << issued_at << "\n"
            << "sqlite-wal" << "\n"
            << claim.ledger_instance_id << "\n"
            << claim.decision_head_hash << "\n"
            << claim.effect_transition_head_hash << "\n"
            << claim.effect_idempotency_key << "\n"
            << claim.prepared_sequence << "\n"
            << claim.prepared_entry_hash << "\n"
            << downstream.terminal_state << "\n"
            << downstream.result_digest_sha256 << "\n"
            << transition_reason << "\n";
    const std::string signing_input = signing.str();
    const std::string signature = sign_rs256(private_key, signing_input);
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << json_escape(kEffectTransitionIntentFormat) << "\",\n"
        << "  \"payload\": {\n"
        << "    \"format\": \"" << json_escape(kEffectTransitionIntentPayloadFormat) << "\",\n"
        << "    \"intent_id\": \"" << json_escape(intent_id) << "\",\n"
        << "    \"intent_subject\": \"" << json_escape(kEffectTransitionIntentSubject) << "\",\n"
        << "    \"issued_at\": \"" << json_escape(issued_at) << "\",\n"
        << "    \"ledger_backend\": \"sqlite-wal\",\n"
        << "    \"ledger_instance_id\": \"" << json_escape(claim.ledger_instance_id) << "\",\n"
        << "    \"prepared_ledger_head_hash\": \"" << json_escape(claim.decision_head_hash) << "\",\n"
        << "    \"effect_transition_previous_hash\": \"" << json_escape(claim.effect_transition_head_hash) << "\",\n"
        << "    \"effect_idempotency_key\": \"" << json_escape(claim.effect_idempotency_key) << "\",\n"
        << "    \"prepared_sequence\": " << claim.prepared_sequence << ",\n"
        << "    \"prepared_entry_hash\": \"" << json_escape(claim.prepared_entry_hash) << "\",\n"
        << "    \"terminal_state\": \"" << json_escape(downstream.terminal_state) << "\",\n"
        << "    \"result_digest_sha256\": \"" << json_escape(downstream.result_digest_sha256) << "\",\n"
        << "    \"transition_reason\": \"" << json_escape(transition_reason) << "\"\n"
        << "  },\n"
        << "  \"payload_signing_input_sha256\": \"" << sha256_hex(signing_input) << "\",\n"
        << "  \"signature\": {\n"
        << "    \"alg\": \"RS256\",\n"
        << "    \"kid\": \"" << json_escape(signer_kid) << "\",\n"
        << "    \"signature_b64url\": \"" << signature << "\"\n"
        << "  },\n"
        << "  \"blocked_claim\": \"rev0635 local relay harness intent; not HSM custody, remote delivery proof, or distributed exactly-once semantics.\"\n"
        << "}\n";
    return out.str();
}

RelayTransitionAuthority load_and_preflight_relay_transition_authority(const std::string& signer_private_key_pem_path,
                                                                        const std::string& signer_kid,
                                                                        const std::string& trust_profile_path,
                                                                        const std::string& trust_profile_sha256,
                                                                        const std::string& terminal_state,
                                                                        long long issued_at_epoch) {
    RelayTransitionAuthority out;
    out.signer = pem_private_key_to_pkey(read_file(signer_private_key_pem_path));
    out.trust_profile_text = read_effect_transition_trust_profile_with_digest_pin(trust_profile_path, trust_profile_sha256);
    EffectOutboxClaimResult probe_claim;
    probe_claim.claimed = true;
    probe_claim.ledger_instance_id = std::string(64, '0');
    probe_claim.decision_head_hash = std::string(64, '1');
    probe_claim.effect_transition_head_hash = "GENESIS";
    probe_claim.effect_idempotency_key = std::string(64, '2');
    probe_claim.prepared_sequence = 1;
    probe_claim.prepared_entry_hash = std::string(64, '3');
    probe_claim.worker_claim_id = std::string(64, '4');
    probe_claim.claimed_at_epoch = issued_at_epoch;
    RelayDownstreamResult probe_downstream;
    probe_downstream.terminal_state = terminal_state;
    probe_downstream.result_digest_sha256 = std::string(64, '5');
    const std::string probe_intent = make_effect_transition_intent_json_for_relay(probe_claim,
                                                                                 probe_downstream,
                                                                                 "rev0648 relay transition authority preflight before claim/downstream",
                                                                                 signer_kid,
                                                                                 out.signer.get());
    (void)verify_effect_transition_intent_text_with_trust_profile_text(probe_intent, out.trust_profile_text);
    return out;
}

EffectRelayOnceResult relay_sqlite_effect_once_authorized_internal(const std::string& ledger_path,
                                                                   const std::string& downstream_path,
                                                                   const std::string& worker_id,
                                                                   long long now_epoch,
                                                                   long long lease_seconds,
                                                                   const std::string& terminal_state,
                                                                   const std::string& signer_private_key_pem_path,
                                                                   const std::string& signer_kid,
                                                                   const std::string& trust_profile_path,
                                                                   const std::string& trust_profile_sha256,
                                                                   bool inject_crash_after_downstream,
                                                                   const std::string& adapter_id = "",
                                                                   const std::string& adapter_kind = "",
                                                                   const std::string& adapter_config_sha256 = "",
                                                                   const std::string& config_handle = "",
                                                                   const std::string& registry_sha256 = "") {
    validate_outbox_worker_claim_inputs(worker_id, now_epoch, lease_seconds);
    validate_effect_relay_inputs(downstream_path, terminal_state, signer_private_key_pem_path, signer_kid, trust_profile_path, trust_profile_sha256, "relay-report-placeholder");
    EffectRelayOnceResult out;
    out.signer_kid = signer_kid;
    out.terminal_state = terminal_state;
    out.adapter_config_format = adapter_config_sha256.empty() ? "" : kEffectRelayAdapterConfigFormat;
    out.adapter_config_sha256 = adapter_config_sha256;
    out.adapter_id = adapter_id;
    out.adapter_kind = adapter_kind;
    out.config_handle = config_handle;
    out.registry_format = registry_sha256.empty() ? "" : kEffectRelayHandleRegistryFormat;
    out.registry_sha256 = registry_sha256;
    out.injected_crash_after_downstream = inject_crash_after_downstream;
    RelayTransitionAuthority transition_authority = load_and_preflight_relay_transition_authority(signer_private_key_pem_path,
                                                                                                  signer_kid,
                                                                                                  trust_profile_path,
                                                                                                  trust_profile_sha256,
                                                                                                  terminal_state,
                                                                                                  now_epoch);
    out.transition_authority_preflight_verified = true;
    // Rev0647/0648: fail closed on downstream SQLite symlink-family hazards before
    // mutating the effect outbox claim. Full WAL/FULL verification still occurs
    // inside apply_relay_downstream_store after a successful claim.
    reject_sqlite_family_symlinks(downstream_path);
    out.claim = claim_sqlite_effect_outbox_authorized_internal(ledger_path, worker_id, now_epoch, lease_seconds);
    out.claimed = out.claim.claimed;
    if (!out.claim.claimed) return out;
    const RelayAdapterProvenance provenance{adapter_id, adapter_kind, adapter_config_sha256, config_handle, registry_sha256};
    out.downstream = apply_relay_downstream_store(downstream_path, out.claim, terminal_state, now_epoch, provenance);
    out.downstream_touched = true;
    if (!registry_sha256.empty()) {
        out.transition_reason = "rev0648 handle-bound relay reconciled downstream effect after transition-authority preflight; handle=" + config_handle + "; registry_sha256=" + registry_sha256 + "; adapter=" + adapter_id + "; config_sha256=" + adapter_config_sha256 + "; worker=" + worker_id + "; claim=" + out.claim.worker_claim_id;
    } else if (!adapter_config_sha256.empty()) {
        out.transition_reason = "rev0636 configured relay reconciled downstream effect; adapter=" + adapter_id + "; config_sha256=" + adapter_config_sha256 + "; worker=" + worker_id + "; claim=" + out.claim.worker_claim_id;
    } else {
        out.transition_reason = "rev0635 relay reconciled simulated downstream effect; worker=" + worker_id + "; claim=" + out.claim.worker_claim_id;
    }
    if (inject_crash_after_downstream) {
        out.failure_reason = "injected crash after downstream apply before terminal transition";
        return out;
    }
    const std::string intent_text = make_effect_transition_intent_json_for_relay(out.claim, out.downstream, out.transition_reason, signer_kid, transition_authority.signer.get());
    VerifiedEffectTransitionIntent intent = verify_effect_transition_intent_text_with_trust_profile_text(intent_text, transition_authority.trust_profile_text);
    out.transition_intent_id = intent.intent_id;
    out.transition_intent_sha256 = intent.intent_sha256;
    std::string reason;
    if (!mark_sqlite_effect_terminal_authorized_internal(ledger_path, intent, reason)) {
        out.failure_reason = reason;
        throw std::runtime_error(reason);
    }
    out.transition_closed = true;
    return out;
}

std::string sqlite_effect_relay_report_json_impl(const EffectRelayOnceResult& result, long long lease_seconds, const std::string& format, const std::string& revision_id, bool include_adapter_config, bool include_registry_handle) {
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << json_escape(format) << "\",\n"
        << "  \"backend_name\": \"sqlite-wal\",\n"
        << "  \"revision_id\": \"" << json_escape(revision_id) << "\",\n"
        << "  \"claimed\": " << (result.claimed ? "true" : "false") << ",\n"
        << "  \"downstream_touched\": " << (result.downstream_touched ? "true" : "false") << ",\n"
        << "  \"transition_closed\": " << (result.transition_closed ? "true" : "false") << ",\n"
        << "  \"injected_crash_after_downstream\": " << (result.injected_crash_after_downstream ? "true" : "false") << ",\n"
        << "  \"transition_authority_preflight_verified\": " << (result.transition_authority_preflight_verified ? "true" : "false") << ",\n"
        << "  \"ledger_instance_id\": \"" << json_escape(result.claim.ledger_instance_id) << "\",\n"
        << "  \"decision_head_hash\": \"" << json_escape(result.claim.decision_head_hash) << "\",\n"
        << "  \"effect_transition_head_hash_before\": \"" << json_escape(result.claim.effect_transition_head_hash) << "\",\n"
        << "  \"worker_id\": \"" << json_escape(result.claim.worker_id) << "\",\n"
        << "  \"lease_seconds\": " << lease_seconds << ",\n";
    if (include_registry_handle) {
        out << "  \"relay_config_registry\": {\n"
            << "    \"format\": \"" << json_escape(result.registry_format) << "\",\n"
            << "    \"config_handle\": \"" << json_escape(result.config_handle) << "\",\n"
            << "    \"registry_sha256\": \"" << json_escape(result.registry_sha256) << "\",\n"
            << "    \"digest_pin_verified\": " << (!result.registry_sha256.empty() ? "true" : "false") << "\n"
            << "  },\n";
    }
    if (include_adapter_config) {
        out << "  \"relay_adapter_config\": {\n"
            << "    \"format\": \"" << json_escape(result.adapter_config_format) << "\",\n"
            << "    \"adapter_id\": \"" << json_escape(result.adapter_id) << "\",\n"
            << "    \"adapter_kind\": \"" << json_escape(result.adapter_kind) << "\",\n"
            << "    \"config_sha256\": \"" << json_escape(result.adapter_config_sha256) << "\",\n"
            << "    \"digest_pin_verified\": " << (!result.adapter_config_sha256.empty() ? "true" : "false") << "\n"
            << "  },\n";
    }
    out << "  \"claim\": {\n"
        << "    \"worker_claim_id\": \"" << json_escape(result.claim.worker_claim_id) << "\",\n"
        << "    \"effect_idempotency_key\": \"" << json_escape(result.claim.effect_idempotency_key) << "\",\n"
        << "    \"prepared_sequence\": " << result.claim.prepared_sequence << ",\n"
        << "    \"prepared_entry_hash\": \"" << json_escape(result.claim.prepared_entry_hash) << "\",\n"
        << "    \"dispatch_attempts\": " << result.claim.dispatch_attempts << ",\n"
        << "    \"claimed_at_epoch\": " << result.claim.claimed_at_epoch << ",\n"
        << "    \"lease_expires_at_epoch\": " << result.claim.lease_expires_at_epoch << ",\n"
        << "    \"previous_outbox_state\": \"" << json_escape(result.claim.previous_outbox_state) << "\"\n"
        << "  },\n"
        << "  \"downstream\": {\n"
        << "    \"store_format\": \"" << json_escape(kEffectRelayDownstreamStoreFormat) << "\",\n"
        << "    \"result_material_version\": \"" << json_escape(result.downstream.result_material_version) << "\",\n"
        << "    \"adapter_id\": \"" << json_escape(result.downstream.adapter_id) << "\",\n"
        << "    \"adapter_kind\": \"" << json_escape(result.downstream.adapter_kind) << "\",\n"
        << "    \"adapter_config_sha256\": \"" << json_escape(result.downstream.adapter_config_sha256) << "\",\n"
        << "    \"config_handle\": \"" << json_escape(result.downstream.config_handle) << "\",\n"
        << "    \"registry_sha256\": \"" << json_escape(result.downstream.registry_sha256) << "\",\n"
        << "    \"inserted\": " << (result.downstream.inserted ? "true" : "false") << ",\n"
        << "    \"replayed_existing\": " << (result.downstream.replayed_existing ? "true" : "false") << ",\n"
        << "    \"terminal_state\": \"" << json_escape(result.downstream.terminal_state) << "\",\n"
        << "    \"result_digest_sha256\": \"" << json_escape(result.downstream.result_digest_sha256) << "\",\n"
        << "    \"observation_count\": " << result.downstream.observation_count << ",\n"
        << "    \"first_worker_claim_id\": \"" << json_escape(result.downstream.first_worker_claim_id) << "\",\n"
        << "    \"last_worker_claim_id\": \"" << json_escape(result.downstream.last_worker_claim_id) << "\"\n"
        << "  },\n"
        << "  \"transition\": {\n"
        << "    \"signer_kid\": \"" << json_escape(result.signer_kid) << "\",\n"
        << "    \"terminal_state\": \"" << json_escape(result.terminal_state) << "\",\n"
        << "    \"transition_reason\": \"" << json_escape(result.transition_reason) << "\",\n"
        << "    \"transition_intent_id\": \"" << json_escape(result.transition_intent_id) << "\",\n"
        << "    \"transition_intent_sha256\": \"" << json_escape(result.transition_intent_sha256) << "\"\n"
        << "  }";
    if (!result.failure_reason.empty()) out << ",\n  \"failure_reason\": \"" << json_escape(result.failure_reason) << "\"\n";
    else out << "\n";
    out << "}\n";
    return out.str();
}

std::string sqlite_effect_relay_report_json(const EffectRelayOnceResult& result, long long lease_seconds) {
    return sqlite_effect_relay_report_json_impl(result, lease_seconds, kEffectRelayReportFormat, "rev0635", false, false);
}

std::string sqlite_effect_relay_configured_report_json(const EffectRelayOnceResult& result, long long lease_seconds) {
    return sqlite_effect_relay_report_json_impl(result, lease_seconds, kEffectRelayConfiguredReportFormat, "rev0636", true, false);
}

std::string sqlite_effect_relay_handle_report_json(const EffectRelayOnceResult& result, long long lease_seconds) {
    return sqlite_effect_relay_report_json_impl(result, lease_seconds, kEffectRelayHandleReportFormat, "rev0648", true, true);
}

}  // namespace

std::string read_trust_profile_with_digest_pin(const std::string& trust_profile_path, const std::string& expected_sha256) {
    return read_trust_profile_with_digest_pin_impl(trust_profile_path, expected_sha256);
}

void verify_trust_profile_digest_pin(const std::string& trust_profile_path, const std::string& expected_sha256) {
    (void)read_trust_profile_with_digest_pin_impl(trust_profile_path, expected_sha256);
}

int run_sqlite_effect_transition_command(const std::string& ledger_path,
                                         const std::string& effect_idempotency_key,
                                         long long prepared_sequence,
                                         const std::string& prepared_entry_hash,
                                         const std::string& terminal_state,
                                         const std::string& result_digest_sha256,
                                         const std::string& transition_reason) {
    (void)ledger_path;
    (void)effect_idempotency_key;
    (void)prepared_sequence;
    (void)prepared_entry_hash;
    (void)terminal_state;
    (void)result_digest_sha256;
    (void)transition_reason;
    std::cerr << "raw effect transition API is disabled; use signed transition intent command" << "\n";
    return 64;
}


int run_sqlite_effect_signed_transition_command(const std::string& ledger_path,
                                                const std::string& intent_path,
                                                const std::string& trust_profile_path,
                                                const std::string& trust_profile_sha256) {
    try {
        if (ledger_path.empty() || intent_path.empty() || trust_profile_path.empty() || trust_profile_sha256.empty()) {
            std::cerr << "signed effect transition requires --ledger, --ledger-effect-transition-intent, --ledger-effect-transition-trust-profile, and --ledger-effect-transition-trust-profile-sha256\n";
            return 64;
        }
        const std::string trust_text = read_effect_transition_trust_profile_with_digest_pin(trust_profile_path, trust_profile_sha256);
        const VerifiedEffectTransitionIntent intent = verify_effect_transition_intent_with_trust_profile_text(intent_path, trust_text);
        std::string reason;
        if (!mark_sqlite_effect_terminal_authorized_internal(ledger_path, intent, reason)) {
            std::cerr << reason << "\n";
            return 1;
        }
        std::cout << reason << " via signed transition intent " << intent.intent_id << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sqlite_effect_pending_report_command(const std::string& ledger_path, const std::string& report_path) {
    try {
        if (report_path.empty()) {
            std::cerr << "sqlite-wal effect pending report requires a nonempty report path\n";
            return 64;
        }
        const std::string report = sqlite_effect_pending_report_json(ledger_path);
        write_file(report_path, report);
        std::cout << "sqlite-wal effect pending report wrote " << report_path << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sqlite_effect_outbox_claim_command(const std::string& ledger_path,
                                           const std::string& worker_id,
                                           long long now_epoch,
                                           long long lease_seconds,
                                           const std::string& claim_report_path) {
    try {
        if (ledger_path.empty() || worker_id.empty() || claim_report_path.empty()) {
            std::cerr << "sqlite-wal effect outbox claim requires --ledger, --ledger-effect-outbox-worker-id, --ledger-effect-outbox-claim-now-epoch, --ledger-effect-outbox-lease-seconds, and --ledger-effect-outbox-claim-report\n";
            return 64;
        }
        EffectOutboxClaimResult claim = claim_sqlite_effect_outbox_authorized_internal(ledger_path, worker_id, now_epoch, lease_seconds);
        write_file(claim_report_path, sqlite_effect_outbox_claim_report_json(claim, lease_seconds));
        if (claim.claimed) {
            std::cout << "sqlite-wal effect outbox claimed " << claim.effect_idempotency_key << " for worker " << worker_id << " as " << claim.worker_claim_id << "\n";
        } else {
            std::cout << "sqlite-wal effect outbox claim found no claimable work\n";
        }
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

int run_sqlite_effect_relay_once_command(const std::string& ledger_path,
                                         const std::string& downstream_path,
                                         const std::string& worker_id,
                                         long long now_epoch,
                                         long long lease_seconds,
                                         const std::string& terminal_state,
                                         const std::string& signer_private_key_pem_path,
                                         const std::string& signer_kid,
                                         const std::string& trust_profile_path,
                                         const std::string& trust_profile_sha256,
                                         const std::string& relay_report_path,
                                         bool inject_crash_after_downstream) {
    try {
        if (ledger_path.empty()) {
            std::cerr << "sqlite-wal effect relay requires --ledger\n";
            return 64;
        }
        validate_effect_relay_inputs(downstream_path, terminal_state, signer_private_key_pem_path, signer_kid, trust_profile_path, trust_profile_sha256, relay_report_path);
        EffectRelayOnceResult relay = relay_sqlite_effect_once_authorized_internal(ledger_path,
                                                                                   downstream_path,
                                                                                   worker_id,
                                                                                   now_epoch,
                                                                                   lease_seconds,
                                                                                   terminal_state,
                                                                                   signer_private_key_pem_path,
                                                                                   signer_kid,
                                                                                   trust_profile_path,
                                                                                   trust_profile_sha256,
                                                                                   inject_crash_after_downstream);
        write_file(relay_report_path, sqlite_effect_relay_report_json(relay, lease_seconds));
        if (!relay.claimed) {
            std::cout << "sqlite-wal effect relay found no claimable work\n";
            return 0;
        }
        if (inject_crash_after_downstream) {
            std::cout << "sqlite-wal effect relay injected crash after downstream apply for " << relay.claim.effect_idempotency_key << "\n";
            return 75;
        }
        std::cout << "sqlite-wal effect relay closed " << relay.claim.effect_idempotency_key << " as " << relay.downstream.terminal_state << " via signed transition intent " << relay.transition_intent_id << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}


int run_sqlite_effect_relay_configured_once_command(const std::string& ledger_path,
                                                    const std::string& relay_config_path,
                                                    const std::string& relay_config_sha256,
                                                    long long now_epoch,
                                                    const std::string& relay_report_path,
                                                    bool inject_crash_after_downstream) {
    try {
        if (ledger_path.empty()) {
            std::cerr << "sqlite-wal configured effect relay requires --ledger\n";
            return 64;
        }
        if (relay_report_path.empty()) {
            std::cerr << "sqlite-wal configured effect relay requires --ledger-effect-relay-report\n";
            return 64;
        }
        RelayAdapterConfig cfg = load_relay_adapter_config_with_digest_pin(relay_config_path, relay_config_sha256, now_epoch, inject_crash_after_downstream);
        EffectRelayOnceResult relay = relay_sqlite_effect_once_authorized_internal(ledger_path,
                                                                                   cfg.downstream_path,
                                                                                   cfg.worker_id,
                                                                                   now_epoch,
                                                                                   cfg.lease_seconds,
                                                                                   cfg.terminal_state,
                                                                                   cfg.signer_private_key_pem_path,
                                                                                   cfg.signer_kid,
                                                                                   cfg.trust_profile_path,
                                                                                   cfg.trust_profile_sha256,
                                                                                   inject_crash_after_downstream,
                                                                                   cfg.adapter_id,
                                                                                   cfg.adapter_kind,
                                                                                   cfg.config_sha256);
        write_file(relay_report_path, sqlite_effect_relay_configured_report_json(relay, cfg.lease_seconds));
        if (!relay.claimed) {
            std::cout << "sqlite-wal configured effect relay found no claimable work for adapter " << cfg.adapter_id << "\n";
            return 0;
        }
        if (inject_crash_after_downstream) {
            std::cout << "sqlite-wal configured effect relay injected crash after downstream apply for " << relay.claim.effect_idempotency_key << " using adapter " << cfg.adapter_id << "\n";
            return 75;
        }
        std::cout << "sqlite-wal configured effect relay closed " << relay.claim.effect_idempotency_key << " as " << relay.downstream.terminal_state << " via adapter " << cfg.adapter_id << " and signed transition intent " << relay.transition_intent_id << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}


int run_sqlite_effect_relay_handle_once_command(const std::string& ledger_path,
                                                const std::string& relay_registry_path,
                                                const std::string& relay_registry_sha256,
                                                const std::string& relay_config_handle,
                                                long long now_epoch,
                                                const std::string& relay_report_path,
                                                bool inject_crash_after_downstream) {
    try {
        if (ledger_path.empty()) {
            std::cerr << "sqlite-wal handle-bound effect relay requires --ledger\n";
            return 64;
        }
        if (relay_report_path.empty()) {
            std::cerr << "sqlite-wal handle-bound effect relay requires --ledger-effect-relay-report\n";
            return 64;
        }
        RelayHandleResolution resolved = load_relay_adapter_config_from_registry_with_digest_pin(relay_registry_path,
                                                                                                 relay_registry_sha256,
                                                                                                 relay_config_handle,
                                                                                                 now_epoch,
                                                                                                 inject_crash_after_downstream);
        const RelayAdapterConfig& cfg = resolved.adapter;
        EffectRelayOnceResult relay = relay_sqlite_effect_once_authorized_internal(ledger_path,
                                                                                   cfg.downstream_path,
                                                                                   cfg.worker_id,
                                                                                   now_epoch,
                                                                                   cfg.lease_seconds,
                                                                                   cfg.terminal_state,
                                                                                   cfg.signer_private_key_pem_path,
                                                                                   cfg.signer_kid,
                                                                                   cfg.trust_profile_path,
                                                                                   cfg.trust_profile_sha256,
                                                                                   inject_crash_after_downstream,
                                                                                   cfg.adapter_id,
                                                                                   cfg.adapter_kind,
                                                                                   cfg.config_sha256,
                                                                                   resolved.handle,
                                                                                   resolved.registry_sha256);
        write_file(relay_report_path, sqlite_effect_relay_handle_report_json(relay, cfg.lease_seconds));
        if (!relay.claimed) {
            std::cout << "sqlite-wal handle-bound effect relay found no claimable work for handle " << resolved.handle << "\n";
            return 0;
        }
        if (inject_crash_after_downstream) {
            std::cout << "sqlite-wal handle-bound effect relay injected crash after downstream apply for " << relay.claim.effect_idempotency_key << " using handle " << resolved.handle << "\n";
            return 75;
        }
        std::cout << "sqlite-wal handle-bound effect relay closed " << relay.claim.effect_idempotency_key << " as " << relay.downstream.terminal_state << " via handle " << resolved.handle << " and signed transition intent " << relay.transition_intent_id << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}

SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest_with_trust_profile_text(const std::string& manifest_path, const std::string& trust_profile_text, const std::string& snapshot_path) {
    if (manifest_path.empty()) throw std::runtime_error("SQLite snapshot manifest path is required");
    if (trust_profile_text.empty()) throw std::runtime_error("SQLite snapshot trust profile text is required");
    if (snapshot_path.empty()) throw std::runtime_error("SQLite snapshot path is required for manifest verification");
    Json manifest = load_json(manifest_path);
    Json trust = parse_json_text(trust_profile_text);
    if (manifest.at("format").str() != "anonsync-sqlite-snapshot-manifest-v2") {
        throw std::runtime_error("SQLite snapshot manifest has unsupported format");
    }
    const Json& payload = manifest.at("payload");
    const Json& sig = manifest.at("signature");
    if (!payload.is_object() || !sig.is_object()) throw std::runtime_error("SQLite snapshot manifest missing payload or signature object");
    validate_manifest_payload_profile(payload);
    const std::string alg = sig.at("alg").str();
    const std::string kid = sig.at("kid").str();
    if (alg != "RS256" || kid.empty()) throw std::runtime_error("SQLite snapshot manifest requires RS256 and nonempty kid");
    const Json& signer = trusted_snapshot_signer(trust, manifest, payload, kid, alg);
    const Json& jwk = signer.at("jwk");
    PKeyPtr pkey = jwk_to_pkey(jwk.at("n").str(), jwk.at("e").str());
    std::string verify_reason;
    const std::string signing_input = snapshot_manifest_signing_input(payload);
    if (manifest.at("payload_signing_input_sha256").str() != sha256_hex(signing_input)) {
        throw std::runtime_error("SQLite snapshot manifest signing-input digest mismatch");
    }
    if (!verify_rs256(pkey.get(), signing_input, sig.at("signature_b64url").str(), verify_reason)) {
        throw std::runtime_error("SQLite snapshot manifest signature verification failed: " + verify_reason);
    }
    const std::string snapshot_sha = sha256_hex(read_file(snapshot_path));
    if (payload.at("snapshot_sha256").str() != snapshot_sha) throw std::runtime_error("SQLite snapshot manifest digest does not match snapshot bytes");
    ReplayLedgerStats st = verify_sqlite_ledger_snapshot_readonly(snapshot_path, "SQLite snapshot manifest read-only verifier");
    if (payload.at("line_count").integer() != st.durable_line_count) throw std::runtime_error("SQLite snapshot manifest line_count does not match verified snapshot");
    if (payload.at("head_hash").str() != st.durable_head_hash) throw std::runtime_error("SQLite snapshot manifest head_hash does not match verified snapshot");
    SqliteSnapshotManifestVerification out;
    out.line_count = st.durable_line_count;
    out.head_hash = st.durable_head_hash;
    out.snapshot_sha256 = snapshot_sha;
    out.signer_kid = kid;
    return out;
}

SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest(const std::string& manifest_path, const std::string& trust_profile_path, const std::string& snapshot_path) {
    if (trust_profile_path.empty()) throw std::runtime_error("SQLite snapshot trust profile path is required");
    return verify_sqlite_snapshot_manifest_with_trust_profile_text(manifest_path, read_file(trust_profile_path), snapshot_path);
}

void restore_sqlite_snapshot_into_ledger_internal(const std::string& snapshot_path, const std::string& ledger_path, const SqliteSnapshotManifestVerification* expected_manifest) {
    if (snapshot_path.empty()) throw std::runtime_error("sqlite-wal snapshot restore source path is empty");
    if (ledger_path.empty()) throw std::runtime_error("sqlite-wal snapshot restore destination ledger path is empty");
    reject_sqlite_family_symlinks(snapshot_path);
    reject_sqlite_family_symlinks(ledger_path);
    std::error_code ec;
    auto src_abs = std::filesystem::weakly_canonical(snapshot_path, ec);
    if (ec) throw std::runtime_error("sqlite-wal snapshot restore could not canonicalize source: " + ec.message());
    std::filesystem::path dst_parent = std::filesystem::path(ledger_path).parent_path();
    if (dst_parent.empty()) dst_parent = ".";
    if (!std::filesystem::exists(dst_parent, ec) || ec) {
        std::filesystem::create_directories(dst_parent);
        ec.clear();
    }
    auto dst_abs = std::filesystem::weakly_canonical(dst_parent, ec);
    if (ec) throw std::runtime_error("sqlite-wal snapshot restore could not canonicalize destination parent: " + ec.message());
    auto dst_full = dst_abs / std::filesystem::path(ledger_path).filename();
    if (src_abs == dst_full) throw std::runtime_error("sqlite-wal snapshot restore refuses identical source and destination ledger paths");

    // Serialize restore operations independently of SQLite writer locks.  A restore replaces
    // the main database file, so two restore processes must not both verify against one
    // destination state and then race their staged renames.
    SqliteRestoreLock restore_lock(ledger_path);
    SqliteWriteGateLock write_gate(ledger_path);

    assert_restore_destination_not_writer_locked(ledger_path);

    // Verify the source snapshot with the dedicated read-only verifier before copying anything.
    // When restore is protected by a signed snapshot manifest, bind the source bytes and
    // replay-ledger head/line-count to that manifest inside the restore routine itself.
    // This closes the rev0616 seam where the runner verified a manifest and then called a
    // restore routine that could still restore a different structurally-valid snapshot.
    std::string manifest_bound_snapshot_sha_before;
    ReplayLedgerStats snapshot_stats;
    {
        if (expected_manifest != nullptr) {
            manifest_bound_snapshot_sha_before = sha256_hex(read_file(snapshot_path));
            if (manifest_bound_snapshot_sha_before != expected_manifest->snapshot_sha256) {
                throw std::runtime_error("sqlite-wal signed snapshot restore source digest does not match verified manifest before staging");
            }
        }
        snapshot_stats = verify_sqlite_ledger_snapshot_readonly(snapshot_path, "sqlite-wal snapshot restore source read-only verifier");
        if (snapshot_stats.loaded_entries <= 0) throw std::runtime_error("sqlite-wal snapshot restore refuses empty source snapshot");
        if (expected_manifest != nullptr) {
            if (snapshot_stats.durable_line_count != expected_manifest->line_count) {
                throw std::runtime_error("sqlite-wal signed snapshot restore source line_count does not match verified manifest");
            }
            if (snapshot_stats.durable_head_hash != expected_manifest->head_hash) {
                throw std::runtime_error("sqlite-wal signed snapshot restore source head_hash does not match verified manifest");
            }
        }
    }

    // Do not silently replace an existing active ledger with an older or divergent snapshot.
    // Operators who really want a rollback must remove the destination ledger family first;
    // the compiled restore path should not make that destructive choice implicitly.
    {
        std::error_code exists_ec;
        if (std::filesystem::exists(ledger_path, exists_ec) && !exists_ec) {
            std::error_code size_ec;
            const auto existing_size = std::filesystem::file_size(ledger_path, size_ec);
            if (!size_ec && existing_size > 0) {
                SqliteWalReplayLedger destination;
                destination.load(ledger_path, false, "batch");
                ReplayLedgerStats destination_stats = destination.stats();
                destination.close();
                if (destination_stats.durable_line_count > snapshot_stats.durable_line_count) {
                    throw std::runtime_error("sqlite-wal snapshot restore rollback guard rejected older snapshot line count");
                }
                if (destination_stats.durable_line_count == snapshot_stats.durable_line_count &&
                    destination_stats.durable_head_hash != snapshot_stats.durable_head_hash) {
                    throw std::runtime_error("sqlite-wal snapshot restore rollback guard rejected divergent same-height snapshot head");
                }
                if (destination_stats.durable_line_count > 0 &&
                    snapshot_stats.durable_line_count > destination_stats.durable_line_count) {
                    const std::string snapshot_prefix_hash = sqlite_entry_hash_at_sequence(snapshot_path, destination_stats.durable_line_count);
                    if (snapshot_prefix_hash != destination_stats.durable_head_hash) {
                        throw std::runtime_error("sqlite-wal snapshot restore append-continuity guard rejected non-extending snapshot prefix");
                    }
                }
            }
        }
    }

    // Restore through a same-directory temp SQLite database first.  The active destination is not
    // unlinked or replaced until the temp database has been copied and verified through the dedicated
    // read-only SQLite snapshot verifier.  This avoids the rev0616 direct-copy failure mode where an error
    // or crash during copy could destroy the active ledger family after unlinking it.
    const std::string temp_path = restore_temp_path_for(ledger_path);
    bool renamed_to_final = false;
    reject_sqlite_family_symlinks(temp_path);
    unlink_sqlite_family(temp_path);
    sqlite3* src = nullptr;
    sqlite3* dst = nullptr;
    int src_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    src_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    try {
        src = sqlite_open_or_throw(snapshot_path, src_flags, "sqlite-wal snapshot restore source open failed");
        int dst_flags = sqlite_open_flags_for_ledger();
        dst = sqlite_open_or_throw(temp_path, dst_flags, "sqlite-wal snapshot restore temp destination open failed");
        sqlite3_backup* backup = sqlite3_backup_init(dst, "main", src, "main");
        if (!backup) sqlite_throw(dst, "sqlite-wal snapshot restore backup init failed");
        int rc = sqlite3_backup_step(backup, -1);
        int finish_rc = sqlite3_backup_finish(backup);
        if (finish_rc != SQLITE_OK || (rc != SQLITE_DONE && rc != SQLITE_OK)) sqlite_throw(dst, "sqlite-wal snapshot restore backup copy failed");
        sqlite_close_or_throw(dst, "sqlite-wal snapshot restore temp destination close failed");
        sqlite_close_or_throw(src, "sqlite-wal snapshot restore source close failed");
        if (expected_manifest != nullptr) {
            const std::string snapshot_sha_after_backup = sha256_hex(read_file(snapshot_path));
            if (snapshot_sha_after_backup != expected_manifest->snapshot_sha256 || snapshot_sha_after_backup != manifest_bound_snapshot_sha_before) {
                throw std::runtime_error("sqlite-wal signed snapshot restore source digest changed during staged backup");
            }
        }
        std::remove((temp_path + "-wal").c_str());
        std::remove((temp_path + "-shm").c_str());

        // Verify the staged temp database before touching the destination.
        {
            ReplayLedgerStats staged_stats = verify_sqlite_ledger_snapshot_readonly(temp_path, "sqlite-wal snapshot restore staged temp read-only verifier");
            if (staged_stats.loaded_entries != snapshot_stats.loaded_entries ||
                staged_stats.durable_line_count != snapshot_stats.durable_line_count ||
                staged_stats.durable_head_hash != snapshot_stats.durable_head_hash) {
                throw std::runtime_error("sqlite-wal snapshot restore staged temp verification does not match source snapshot");
            }
        }
        maybe_inject_restore_fault("after-temp-verify-before-replace");

        assert_restore_destination_not_writer_locked(ledger_path);
        checkpoint_destination_before_restore_replace(ledger_path);
        maybe_inject_restore_fault("after-destination-checkpoint-before-replace");

        std::filesystem::rename(temp_path, ledger_path);
        renamed_to_final = true;
        maybe_inject_restore_fault("after-atomic-rename-before-parent-fsync");
        fsync_parent_directory_for_restore(ledger_path);
        maybe_inject_restore_fault("after-parent-fsync-before-final-verify");

        // Verify the restored destination through the dedicated read-only verifier so profile/integrity/hash-chain/metadata checks run without reopening the write path.
        ReplayLedgerStats restored_stats = verify_sqlite_ledger_snapshot_readonly(ledger_path, "sqlite-wal snapshot restore destination read-only verifier");
        if (restored_stats.loaded_entries <= 0) throw std::runtime_error("sqlite-wal snapshot restore destination verified empty after atomic replace");
        if (restored_stats.durable_line_count != snapshot_stats.durable_line_count || restored_stats.durable_head_hash != snapshot_stats.durable_head_hash) {
            throw std::runtime_error("sqlite-wal snapshot restore destination verification does not match source snapshot after atomic replace");
        }
    } catch (...) {
        sqlite_close_best_effort(dst);
        sqlite_close_best_effort(src);
        if (!renamed_to_final) unlink_sqlite_family(temp_path);
        throw;
    }
    unlink_sqlite_family(temp_path);
}

void restore_sqlite_snapshot_into_ledger(const std::string& snapshot_path, const std::string& ledger_path) {
    restore_sqlite_snapshot_into_ledger_internal(snapshot_path, ledger_path, nullptr);
}

void restore_sqlite_snapshot_into_ledger_verified(const std::string& snapshot_path, const std::string& ledger_path, const SqliteSnapshotManifestVerification& expected) {
    restore_sqlite_snapshot_into_ledger_internal(snapshot_path, ledger_path, &expected);
}




int run_ledger_sqlite_readonly_snapshot_verifier_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0625_readonly_snapshot_verifier_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& kind, const std::string& op, const std::string& source, const std::string& id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value(kind);
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("readonly-snapshot-verifier-digest");
        tc.o["cloud_event_source"] = json_string_value(source);
        tc.o["cloud_event_id"] = json_string_value(id);
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("readonly-snapshot-verifier-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string bad_snapshot = "/tmp/" + stem + "_bad_schema.sqlite";
    try {
        cleanup_path(source);
        cleanup_path(snapshot);
        cleanup_path(bad_snapshot);
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, true, "batch");
        if (!backend->stage(make_tc("readonly-openapi", "openapi", "readonlyVerifierOpenapi", "", ""), make_claims("readonly-jti-1", "readonlyVerifierOpenapi"), "allow", reason)) {
            throw std::runtime_error("read-only snapshot verifier selftest openapi stage failed: " + reason);
        }
        if (!backend->stage(make_tc("readonly-async", "asyncapi", "readonlyVerifierAsync", "urn:anonsync:readonly", "event-1"), make_claims("readonly-jti-2", "readonlyVerifierAsync"), "accept", reason)) {
            throw std::runtime_error("read-only snapshot verifier selftest async stage failed: " + reason);
        }
        if (!backend->commit(reason)) throw std::runtime_error("read-only snapshot verifier selftest commit failed: " + reason);
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("read-only snapshot verifier selftest backup failed: " + reason);
        backend->close();

        if (std::filesystem::exists(snapshot + ".write.lock") || std::filesystem::exists(snapshot + ".restore.lock")) {
            failed++; std::cerr << "read-only snapshot verifier created mutable lock sidecars for valid snapshot\n";
        } else passed++;

        try {
            ReplayLedgerStats st = verify_sqlite_ledger_snapshot_readonly(snapshot, "read-only snapshot verifier selftest valid snapshot");
            if (st.durable_line_count == 2 && st.loaded_entries == 2 && st.durable_head_hash != "GENESIS" && st.sqlite_integrity_checks == 1 && st.sqlite_profile_checks == 1) passed++;
            else { failed++; std::cerr << "read-only snapshot verifier valid snapshot stats mismatch\n"; }
        } catch (const std::exception& e) {
            failed++; std::cerr << "read-only snapshot verifier rejected valid snapshot: " << e.what() << "\n";
        }
        if (std::filesystem::exists(snapshot + ".write.lock") || std::filesystem::exists(snapshot + ".restore.lock")) {
            failed++; std::cerr << "read-only snapshot verifier left mutable sidecars after direct verification\n";
        } else passed++;

        std::filesystem::copy_file(snapshot, bad_snapshot, std::filesystem::copy_options::overwrite_existing);
        sqlite3* db = sqlite_open_or_throw(bad_snapshot, sqlite_open_flags_for_ledger(), "read-only snapshot verifier bad-schema open failed");
        sqlite_exec_or_throw(db, "CREATE VIEW anonsync_bad_view AS SELECT 1 AS x;", "read-only snapshot verifier bad-schema injection failed");
        sqlite_close_or_throw(db, "read-only snapshot verifier bad-schema close failed");
        try {
            (void)verify_sqlite_ledger_snapshot_readonly(bad_snapshot, "read-only snapshot verifier selftest bad schema");
            failed++; std::cerr << "read-only snapshot verifier accepted snapshot with unexpected schema view\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("unexpected schema object") != std::string::npos || std::string(e.what()).find("non-table/index schema object") != std::string::npos) passed++;
            else { failed++; std::cerr << "read-only snapshot verifier bad-schema rejection reason mismatch: " << e.what() << "\n"; }
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "read-only snapshot verifier selftest exception: " << e.what() << "\n";
    }
    cleanup_path(source);
    cleanup_path(snapshot);
    cleanup_path(bad_snapshot);
    std::cout << "anonsync_core sqlite read-only snapshot verifier selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_restore_prefix_continuity_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0619_restore_prefix_continuity_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-prefix-continuity-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-prefix-continuity-digest"));
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
                throw std::runtime_error("restore prefix-continuity seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore prefix-continuity seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore prefix-continuity snapshot failed: " + reason);
        backend->close();
    };
    auto stats_for = [&](const std::string& path) {
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, false, "batch");
        ReplayLedgerStats st = backend->stats();
        backend->close();
        return st;
    };
    const std::string good_source = "/tmp/" + stem + "_good_source.sqlite";
    const std::string good_snapshot = "/tmp/" + stem + "_good_snapshot.sqlite";
    const std::string good_dst = "/tmp/" + stem + "_good_dst.sqlite";
    const std::string bad_source = "/tmp/" + stem + "_bad_source.sqlite";
    const std::string bad_snapshot = "/tmp/" + stem + "_bad_snapshot.sqlite";
    const std::string bad_dst = "/tmp/" + stem + "_bad_dst.sqlite";
    const std::string empty_dst = "/tmp/" + stem + "_empty_dst.sqlite";
    const std::string same_source = "/tmp/" + stem + "_same_source.sqlite";
    const std::string same_snapshot = "/tmp/" + stem + "_same_snapshot.sqlite";
    const std::string same_dst = "/tmp/" + stem + "_same_dst.sqlite";
    const std::string divergent_source = "/tmp/" + stem + "_divergent_source.sqlite";
    const std::string divergent_snapshot = "/tmp/" + stem + "_divergent_snapshot.sqlite";
    const std::string divergent_dst = "/tmp/" + stem + "_divergent_dst.sqlite";
    try {
        seed_ledger(good_source, {"prefix-a", "prefix-b", "prefix-c"}, "sqlite-prefix-op");
        seed_ledger(good_dst, {"prefix-a", "prefix-b"}, "sqlite-prefix-op");
        snapshot_from(good_source, good_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(good_snapshot, good_dst);
            ReplayLedgerStats st = stats_for(good_dst);
            if (st.durable_line_count == 3) passed++; else { failed++; std::cerr << "restore prefix-continuity good extension line_count mismatch\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity good extension failed: " << e.what() << "\n"; }

        seed_ledger(bad_source, {"other-a", "other-b", "other-c"}, "sqlite-prefix-op");
        seed_ledger(bad_dst, {"prefix-a", "prefix-b"}, "sqlite-prefix-op");
        snapshot_from(bad_source, bad_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(bad_snapshot, bad_dst);
            failed++; std::cerr << "restore prefix-continuity accepted non-extending newer snapshot\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("append-continuity guard") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore prefix-continuity rejection reason mismatch: " << e.what() << "\n"; }
        }

        try {
            cleanup_path(empty_dst);
            restore_sqlite_snapshot_into_ledger(bad_snapshot, empty_dst);
            ReplayLedgerStats st = stats_for(empty_dst);
            if (st.durable_line_count == 3) passed++; else { failed++; std::cerr << "restore prefix-continuity empty destination line_count mismatch\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity empty destination restore failed: " << e.what() << "\n"; }

        seed_ledger(same_source, {"same-a", "same-b"}, "sqlite-prefix-op");
        seed_ledger(same_dst, {"same-a", "same-b"}, "sqlite-prefix-op");
        snapshot_from(same_source, same_snapshot);
        try { restore_sqlite_snapshot_into_ledger(same_snapshot, same_dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity idempotent same-head restore failed: " << e.what() << "\n"; }

        seed_ledger(divergent_source, {"div-a", "div-b"}, "sqlite-prefix-op");
        seed_ledger(divergent_dst, {"same-a", "same-b"}, "sqlite-prefix-op");
        snapshot_from(divergent_source, divergent_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(divergent_snapshot, divergent_dst);
            failed++; std::cerr << "restore prefix-continuity accepted divergent same-height restore\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("divergent same-height") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore prefix-continuity divergent same-height reason mismatch: " << e.what() << "\n"; }
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore prefix-continuity selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {good_source, good_snapshot, good_dst, bad_source, bad_snapshot, bad_dst, empty_dst, same_source, same_snapshot, same_dst, divergent_source, divergent_snapshot, divergent_dst}) cleanup_path(p);
    std::cout << "anonsync_core ledger sqlite restore prefix-continuity selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_sqlite_write_gate_holder(const std::string& ledger_path, long long seconds) {
    try {
        SqliteWriteGateLock lock(ledger_path);
        std::cout << "anonsync_core sqlite write-gate holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sqlite write-gate holder failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_sqlite_restore_write_gate_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_write_gate_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-write-gate-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-write-gate-digest"));
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
                throw std::runtime_error("restore write-gate seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore write-gate seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore write-gate snapshot failed: " + reason);
        backend->close();
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    const std::string dst_gate_locked = "/tmp/" + stem + "_dst_gate_locked.sqlite";
    const std::string dst_symlink = "/tmp/" + stem + "_dst_symlink.sqlite";
    const std::string dst_stale_gate = "/tmp/" + stem + "_dst_stale_gate.sqlite";
    const std::string target = "/tmp/" + stem + "_target.txt";
    try {
        seed_ledger(source, {"restore-write-gate-jti-1", "restore-write-gate-jti-2"}, "sqlite-restore-write-gate-op");
        snapshot_from(source, snapshot);
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore write-gate valid restore failed: " << e.what() << "\n"; }

        pid_t child = ::fork();
        if (child < 0) throw std::runtime_error("restore write-gate fork failed");
        if (child == 0) {
            int rc = run_sqlite_write_gate_holder(dst_gate_locked, 2);
            _exit(rc == 0 ? 0 : 3);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_gate_locked);
            failed++; std::cerr << "restore write-gate accepted restore while destination write gate was held\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("write-gate lock contention") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore write-gate contention reason mismatch: " << e.what() << "\n"; }
        }
        int status = 0;
        (void)::waitpid(child, &status, 0);
        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) passed++; else { failed++; std::cerr << "restore write-gate holder child failed\n"; }

        write_file(target, "target");
        std::remove((dst_symlink + ".write.lock").c_str());
        if (::symlink(target.c_str(), (dst_symlink + ".write.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_symlink);
                failed++; std::cerr << "restore write-gate accepted symbolic-link write gate sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("write-gate refuses symbolic-link") != std::string::npos || std::string(e.what()).find("refuses symbolic-link ledger or sidecar") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore write-gate symlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore write-gate could not create symlink\n"; }

        write_file(dst_stale_gate + ".write.lock", "stale regular write-gate file\n");
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst_stale_gate); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore write-gate rejected stale regular write-gate file: " << e.what() << "\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore write-gate selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source, snapshot, dst, dst_gate_locked, dst_symlink, dst_stale_gate}) cleanup_path(p);
    std::remove(target.c_str());
    std::cout << "anonsync_core ledger sqlite restore write-gate selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_sqlite_restore_lock_holder(const std::string& ledger_path, long long seconds) {
    try {
        SqliteRestoreLock lock(ledger_path);
        std::cout << "anonsync_core sqlite restore lock holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sqlite restore lock holder failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_sqlite_restore_locking_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_locking_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-lock-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-lock-digest"));
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
                throw std::runtime_error("restore locking seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore locking seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore locking snapshot failed: " + reason);
        backend->close();
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    const std::string dst_locked = "/tmp/" + stem + "_dst_locked.sqlite";
    const std::string dst_symlink = "/tmp/" + stem + "_dst_symlink.sqlite";
    const std::string dst_stale_lock = "/tmp/" + stem + "_dst_stale.sqlite";
    const std::string target = "/tmp/" + stem + "_target.txt";
    try {
        seed_ledger(source, {"restore-lock-jti-1", "restore-lock-jti-2"}, "sqlite-restore-lock-op");
        snapshot_from(source, snapshot);
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore locking valid restore failed: " << e.what() << "\n"; }

        // Use a child process to hold the sidecar flock, because flock semantics are process-oriented.
        pid_t child = ::fork();
        if (child < 0) throw std::runtime_error("restore locking fork failed");
        if (child == 0) {
            int rc = run_sqlite_restore_lock_holder(dst_locked, 2);
            _exit(rc == 0 ? 0 : 3);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_locked);
            failed++; std::cerr << "restore locking accepted concurrent restore while lock holder was active\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("restore lock contention") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore locking contention reason mismatch: " << e.what() << "\n"; }
        }
        int status = 0;
        (void)::waitpid(child, &status, 0);
        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) passed++; else { failed++; std::cerr << "restore locking holder child failed\n"; }

        write_file(target, "target");
        std::remove((dst_symlink + ".restore.lock").c_str());
        if (::symlink(target.c_str(), (dst_symlink + ".restore.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_symlink);
                failed++; std::cerr << "restore locking accepted symbolic-link restore lock sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("restore lock refuses symbolic-link") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore locking symlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore locking could not create lock symlink\n"; }

        write_file(dst_stale_lock + ".restore.lock", "stale regular lock file\n");
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst_stale_lock); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore locking rejected stale regular lock file: " << e.what() << "\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore locking selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source, snapshot, dst, dst_locked, dst_symlink, dst_stale_lock}) cleanup_path(p);
    std::remove(target.c_str());
    std::cout << "anonsync_core ledger sqlite restore locking selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}



int run_ledger_sqlite_restore_manifest_binding_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_manifest_binding_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-manifest-binding-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-manifest-binding-digest"));
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
                throw std::runtime_error("restore manifest binding seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore manifest binding seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, false, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore manifest binding snapshot failed: " + reason);
        backend->close();
    };
    auto stats_for = [&](const std::string& path) {
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, false, "batch");
        ReplayLedgerStats st = backend->stats();
        backend->close();
        return st;
    };
    auto expected_for = [&](const std::string& snapshot) {
        ReplayLedgerStats st = stats_for(snapshot);
        SqliteSnapshotManifestVerification v;
        v.line_count = st.durable_line_count;
        v.head_hash = st.durable_head_hash;
        v.snapshot_sha256 = sha256_hex(read_file(snapshot));
        v.signer_kid = "rev0616-selftest-restore-root";
        return v;
    };
    auto expect_reject = [&](const std::string& label, const std::string& snapshot, const std::string& dst, const SqliteSnapshotManifestVerification& expected) {
        cleanup_path(dst);
        try {
            restore_sqlite_snapshot_into_ledger_verified(snapshot, dst, expected);
            failed++; std::cerr << "restore manifest binding accepted hostile case " << label << "\n";
        } catch (const std::exception&) { passed++; }
    };
    auto expect_accept = [&](const std::string& label, const std::string& snapshot, const std::string& dst, const SqliteSnapshotManifestVerification& expected, long long rows) {
        cleanup_path(dst);
        try {
            restore_sqlite_snapshot_into_ledger_verified(snapshot, dst, expected);
            ReplayLedgerStats st = stats_for(dst);
            if (st.durable_line_count == rows && st.durable_head_hash == expected.head_hash) passed++;
            else { failed++; std::cerr << "restore manifest binding accepted " << label << " but restored wrong state\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore manifest binding rejected valid case " << label << ": " << e.what() << "\n"; }
    };
    const std::string source1 = "/tmp/" + stem + "_source1.sqlite";
    const std::string source2 = "/tmp/" + stem + "_source2.sqlite";
    const std::string snapshot1 = "/tmp/" + stem + "_snapshot1.sqlite";
    const std::string snapshot2 = "/tmp/" + stem + "_snapshot2.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    try {
        seed_ledger(source1, {"restore-manifest-jti-1", "restore-manifest-jti-2"}, "sqlite-restore-manifest-op-a");
        seed_ledger(source2, {"restore-manifest-jti-3", "restore-manifest-jti-4", "restore-manifest-jti-5"}, "sqlite-restore-manifest-op-b");
        snapshot_from(source1, snapshot1);
        snapshot_from(source2, snapshot2);
        SqliteSnapshotManifestVerification expected1 = expected_for(snapshot1);
        SqliteSnapshotManifestVerification expected2 = expected_for(snapshot2);
        expect_accept("valid manifest-bound restore", snapshot1, dst, expected1, 2);

        auto bad_digest = expected1;
        bad_digest.snapshot_sha256 = std::string(64, '0');
        expect_reject("wrong snapshot digest", snapshot1, dst, bad_digest);

        auto bad_head = expected1;
        bad_head.head_hash = std::string(64, '1');
        expect_reject("wrong snapshot head", snapshot1, dst, bad_head);

        auto bad_count = expected1;
        bad_count.line_count = expected1.line_count + 1;
        expect_reject("wrong snapshot line count", snapshot1, dst, bad_count);

        cleanup_path(snapshot1);
        std::filesystem::copy_file(snapshot2, snapshot1, std::filesystem::copy_options::overwrite_existing);
        expect_reject("source path swapped after manifest verification", snapshot1, dst, expected1);
        expect_accept("valid manifest-bound restore after recomputing expected summary", snapshot1, dst, expected2, 3);
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore manifest binding selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source1, source2, snapshot1, snapshot2, dst}) cleanup_path(p);
    std::cout << "anonsync_core ledger sqlite restore manifest binding selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

std::unique_ptr<IReplayLedgerBackend> create_replay_ledger_backend(const std::string& backend_name) {
    if (backend_name.empty() || backend_name == "local-jsonl") return std::make_unique<ReplayLedger>();
    if (backend_name == "sqlite-wal") return std::make_unique<SqliteWalReplayLedger>();
    throw std::runtime_error("unsupported replay-ledger backend: " + backend_name);
}

}  // namespace anonsync
