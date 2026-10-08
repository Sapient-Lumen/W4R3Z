#include "anonsync_core_internal.hpp"

#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {

// rev0600 translation unit: explicit replay-ledger backend interface, sidecar symlink rejection, and journal-unlink interruption recovery.
// rev0599 compatibility needle: replay-ledger backend adapter with strict journal-v2 recovery and stage/commit backend boundary.
// rev0598 compatibility needle: replay-ledger backend adapter with immediate and explicit batch transaction modes.
// rev0597 compatibility needle: nonblocking lock ownership, write-ahead journal records, semantic journal recovery validation, crash-point fault injection.
// rev0597 compatibility needle: recovered journal previous head semantic journal recovery validation retained through strict v2 prefix/last-entry checks.
// rev0595 compatibility needle: atomic temp-write fsync rename directory-fsync.

namespace {

std::string event_identity_key(const std::string& cloud_event_source, const std::string& cloud_event_id) {
    if (cloud_event_source.empty() || cloud_event_id.empty()) return "";
    return length_prefixed_security_tuple("anonsync-cloud-event-identity-v2", {
        {"source", cloud_event_source},
        {"id", cloud_event_id},
    });
}

const char* kPreparedEffectState = "prepared";

std::string effect_idempotency_key_from_case_or_legacy(const Json& tc, const Json& claims) {
    const std::string supplied = tc.at("effect_idempotency_key").str();
    if (!supplied.empty()) return supplied;
    // Compatibility fallback for older in-process selftests and pre-normalized controls.
    // Normalized request/event envelopes in rev0625 carry a stronger key over method/path/body
    // or CloudEvents source/id/payload; this fallback is never used for the streamed gateway corpus.
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

std::string ledger_parent_dir(const std::string& path) {
    std::filesystem::path p(path);
    std::filesystem::path parent = p.parent_path();
    return parent.empty() ? std::string(".") : parent.string();
}

bool fsync_fd(int fd, std::string& reason, const std::string& label) {
    if (::fsync(fd) != 0) {
        reason = label + " fsync failed: " + std::strerror(errno);
        return false;
    }
    return true;
}

bool write_all_fd(int fd, const std::string& data, std::string& reason) {
    const char* ptr = data.data();
    size_t remaining = data.size();
    while (remaining > 0) {
        ssize_t written = ::write(fd, ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            reason = std::string("durable replay ledger temp write failed: ") + std::strerror(errno);
            return false;
        }
        if (written == 0) {
            reason = "durable replay ledger temp write made no progress";
            return false;
        }
        ptr += written;
        remaining -= static_cast<size_t>(written);
    }
    return true;
}

void reject_existing_symlink(const std::string& path, const std::string& label) {
    if (path.empty()) return;
    struct stat st;
    if (::lstat(path.c_str(), &st) != 0) {
        if (errno == ENOENT) return;
        throw std::runtime_error(label + " lstat failed: " + std::strerror(errno));
    }
    if (S_ISLNK(st.st_mode)) {
        throw std::runtime_error(label + " refuses symbolic-link sidecar or ledger path: " + path);
    }
}

int open_strict_no_symlink(const std::string& path, int flags, mode_t mode, std::string& reason, const std::string& label) {
    reject_existing_symlink(path, label);
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    int fd = ::open(path.c_str(), flags | O_CLOEXEC, mode);
    if (fd < 0) {
        reason = label + " open failed: " + std::strerror(errno);
    }
    return fd;
}

std::string file_payload_or_empty(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return "";
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

struct LedgerPayloadSummary {
    long long line_count = 0;
    std::string head = "GENESIS";
    std::string previous_head = "GENESIS";
    std::vector<std::string> heads_by_line;
};

LedgerPayloadSummary summarize_ledger_payload(const std::string& payload) {
    LedgerPayloadSummary summary;
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

std::string head_from_lines(const std::vector<std::string>& lines) {
    if (lines.empty()) return "GENESIS";
    Json last = parse_json_text(lines.back());
    return last.at("entry_hash").str();
}

std::string previous_hash_of_last_line(const std::vector<std::string>& lines) {
    if (lines.empty()) return "GENESIS";
    Json last = parse_json_text(lines.back());
    return last.at("previous_hash").str();
}

std::string journal_json(const std::string& ledger_path,
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

std::string journal_format(const Json& journal) {
    const std::string fmt = journal.at("format").str();
    if (fmt == "anonsync-replay-ledger-journal-v2") return fmt;
    return "";
}
}  // namespace

std::string ReplayLedger::entry_hash_material(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key, const std::string& effect_state) {
    return std::to_string(sequence) + "\n" + previous_hash + "\n" + case_id + "\n" + kind + "\n" + operation_id + "\n" + contract_digest + "\n" + jti + "\n" + action + "\n" + cloud_event_source + "\n" + cloud_event_id + "\n" + effect_idempotency_key + "\n" + effect_state;
}

std::string ReplayLedger::compute_entry_hash(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key, const std::string& effect_state) {
    return sha256_hex(entry_hash_material(sequence, previous_hash, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state));
}

ReplayLedger::~ReplayLedger() {
    release_lock();
}


ReplayLedgerStats ReplayLedger::stats() const {
    ReplayLedgerStats st;
    st.backend_name = backend_name();
    st.loaded_entries = loaded_entries;
    st.appended_entries = appended_entries;
    st.atomic_rewrite_commits = atomic_rewrite_commits;
    st.directory_fsync_attempts = directory_fsync_attempts;
    st.lock_acquire_attempts = lock_acquire_attempts;
    st.lock_contention_denials = lock_contention_denials;
    st.journal_records_written = journal_records_written;
    st.journal_recovered_after_commit = journal_recovered_after_commit;
    st.journal_rejections = journal_rejections;
    st.batch_flush_commits = ledger_batch_flush_commits;
    st.batch_pending_entries_peak = ledger_batch_pending_entries_peak;
    st.durable_line_count = durable_line_count;
    st.durable_head_hash = durable_head_hash;
    st.effect_terminal_transitions = effect_terminal_transitions;
    st.effect_transition_rejections = effect_transition_rejections;
    st.effect_transition_line_count = effect_transition_line_count;
    st.effect_transition_head_hash = effect_transition_head_hash;
    st.backend_factory_selections = 1;
    return st;
}

void ReplayLedger::release_lock() {
    if (lock_fd >= 0) {
        (void)::flock(lock_fd, LOCK_UN);
        (void)::close(lock_fd);
        lock_fd = -1;
    }
}

std::string ReplayLedger::journal_path() const {
    return path + ".journal";
}

void ReplayLedger::maybe_inject_crash(const std::string& checkpoint) {
    const char* raw = std::getenv("ANONSYNC_LEDGER_FAULT_AT");
    if (!raw) return;
    std::string requested(raw);
    if (requested == checkpoint) {
        throw std::runtime_error("simulated durable replay ledger crash at checkpoint " + checkpoint);
    }
}

void ReplayLedger::acquire_lock() {
    if (path.empty()) return;
    release_lock();
    lock_path = path + ".lock";
    reject_existing_symlink(path, "durable replay ledger");
    reject_existing_symlink(journal_path(), "durable replay ledger journal");
    reject_existing_symlink(lock_path, "durable replay ledger lock");
    lock_acquire_attempts++;
    std::string reason;
    int fd = open_strict_no_symlink(lock_path, O_RDWR | O_CREAT, 0600, reason, "durable replay ledger lock");
    if (fd < 0) throw std::runtime_error(reason);
    if (::flock(fd, LOCK_EX | LOCK_NB) != 0) {
        lock_contention_denials++;
        std::string reason = std::string("durable replay ledger lock contention: ") + std::strerror(errno);
        (void)::close(fd);
        throw std::runtime_error(reason);
    }
    lock_fd = fd;
}

bool ReplayLedger::write_journal_record(const std::string& previous_head,
                                        long long previous_line_count,
                                        const std::string& next_head,
                                        long long next_line_count,
                                        const std::string& last_entry_previous_hash,
                                        const std::string& payload_sha256,
                                        std::string& reason) {
    const std::string jpath = journal_path();
    const std::string body = journal_json(path, previous_head, previous_line_count, next_head, next_line_count, last_entry_previous_hash, payload_sha256);
    int fd = open_strict_no_symlink(jpath, O_WRONLY | O_CREAT | O_TRUNC, 0600, reason, "durable replay ledger journal");
    if (fd < 0) return false;
    bool ok = write_all_fd(fd, body, reason) && fsync_fd(fd, reason, "durable replay ledger journal");
    if (::close(fd) != 0 && ok) {
        reason = std::string("durable replay ledger journal close failed: ") + std::strerror(errno);
        ok = false;
    }
    if (!ok) return false;
    journal_records_written++;
    return true;
}

void ReplayLedger::recover_or_reject_journal() {
    const std::string jpath = journal_path();
    reject_existing_symlink(path, "durable replay ledger");
    reject_existing_symlink(jpath, "durable replay ledger journal");
    if (!std::filesystem::exists(jpath)) return;
    try {
        Json journal = load_json(jpath);
        const std::string fmt = journal_format(journal);
        if (fmt.empty()) {
            journal_rejections++;
            throw std::runtime_error("durable replay ledger journal has unknown format");
        }
        if (journal.at("ledger_path").str() != path) {
            journal_rejections++;
            throw std::runtime_error("durable replay ledger journal path does not match ledger");
        }
        const std::string payload = file_payload_or_empty(path);
        const std::string payload_sha = sha256_hex(payload);
        if (payload_sha == journal.at("payload_sha256").str()) {
            // Crash after rename but before journal unlink: the committed ledger already equals the journal payload.
            // rev0598 supports multi-entry batch commits by validating prefix head and prior line count, rather
            // than assuming the journal's previous_head is the previous hash of the last ledger row.
            LedgerPayloadSummary summary = summarize_ledger_payload(payload);
            if (journal.at("next_line_count").integer(-1) != summary.line_count) {
                journal_rejections++;
                throw std::runtime_error("durable replay ledger recovered journal line count does not match committed ledger");
            }
            if (journal.at("next_head").str() != summary.head) {
                journal_rejections++;
                throw std::runtime_error("durable replay ledger recovered journal head does not match committed ledger");
            }
            const long long previous_line_count = journal.at("previous_line_count").integer(-1);
            if (previous_line_count < 0 || previous_line_count > summary.line_count) {
                journal_rejections++;
                throw std::runtime_error("durable replay ledger recovered journal previous_line_count out of range");
            }
            std::string prefix_head = "GENESIS";
            if (previous_line_count > 0) prefix_head = summary.heads_by_line.at(static_cast<size_t>(previous_line_count - 1));
            if (journal.at("previous_head").str() != prefix_head) {
                journal_rejections++;
                throw std::runtime_error("durable replay ledger recovered journal prefix head does not match committed ledger");
            }
            if (journal.at("last_entry_previous_hash").str() != summary.previous_head) {
                journal_rejections++;
                throw std::runtime_error("durable replay ledger recovered journal last-entry previous head does not match committed ledger");
            }
            if (::unlink(jpath.c_str()) != 0) {
                journal_rejections++;
                throw std::runtime_error(std::string("durable replay ledger could not unlink recovered journal: ") + std::strerror(errno));
            }
            journal_recovered_after_commit++;
            return;
        }
        journal_rejections++;
        throw std::runtime_error("durable replay ledger dirty journal does not match committed ledger payload");
    } catch (const std::runtime_error&) {
        throw;
    } catch (const std::exception& e) {
        journal_rejections++;
        throw std::runtime_error(std::string("durable replay ledger dirty journal parse failure: ") + e.what());
    }
}

bool ReplayLedger::durable_replace_lines(const std::vector<std::string>& next_lines, std::string& reason) {
    if (path.empty()) { reason = "durable replay ledger path is empty"; return false; }
    reject_existing_symlink(path, "durable replay ledger");
    reject_existing_symlink(journal_path(), "durable replay ledger journal");
    const std::string previous_head = durable_head_hash;
    const long long previous_line_count = durable_line_count;
    const std::string next_head = head_from_lines(next_lines);
    const std::string last_previous_hash = previous_hash_of_last_line(next_lines);
    const std::string tmp_path = path + ".tmp." + std::to_string(static_cast<long long>(::getpid())) + "." + std::to_string(loaded_entries + appended_entries + 1);
    std::string payload;
    for (const std::string& line : next_lines) {
        payload += line;
        payload += '\n';
    }
    if (!write_journal_record(previous_head, previous_line_count, next_head, static_cast<long long>(next_lines.size()), last_previous_hash, sha256_hex(payload), reason)) {
        return false;
    }
    maybe_inject_crash("after-journal-fsync");
    int fd = open_strict_no_symlink(tmp_path, O_WRONLY | O_CREAT | O_EXCL, 0600, reason, "durable replay ledger temp file");
    if (fd < 0) return false;
    bool ok = write_all_fd(fd, payload, reason) && fsync_fd(fd, reason, "durable replay ledger temp file");
    if (::close(fd) != 0 && ok) {
        reason = std::string("durable replay ledger temp close failed: ") + std::strerror(errno);
        ok = false;
    }
    if (!ok) {
        ::unlink(tmp_path.c_str());
        return false;
    }
    maybe_inject_crash("after-temp-fsync");
    if (::rename(tmp_path.c_str(), path.c_str()) != 0) {
        reason = std::string("durable replay ledger atomic rename failed: ") + std::strerror(errno);
        ::unlink(tmp_path.c_str());
        return false;
    }
    atomic_rewrite_commits++;
    maybe_inject_crash("after-rename-before-dir-fsync");
    const std::string parent = ledger_parent_dir(path);
    int dfd = ::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dfd >= 0) {
        directory_fsync_attempts++;
        if (::fsync(dfd) != 0) {
            reason = std::string("durable replay ledger parent directory fsync failed after rename: ") + std::strerror(errno);
            ::close(dfd);
            return false;
        }
        ::close(dfd);
        maybe_inject_crash("after-dir-fsync-before-journal-unlink");
    } else {
        reason = std::string("durable replay ledger parent directory open failed after rename: ") + std::strerror(errno);
        return false;
    }
    if (::unlink(journal_path().c_str()) != 0 && errno != ENOENT) {
        reason = std::string("durable replay ledger journal unlink failed after commit: ") + std::strerror(errno);
        return false;
    }
    durable_head_hash = next_head;
    durable_line_count = static_cast<long long>(next_lines.size());
    reason = "durable replay ledger backend commit locked write-ahead-journal fsync temp-write fsync rename directory-fsync journal-unlink committed";
    return true;
}

void ReplayLedger::load(const std::string& ledger_path, bool reset, const std::string& mode) {
    if (ledger_path.empty()) return;
    if (mode != "immediate" && mode != "batch") {
        throw std::runtime_error("unsupported replay ledger commit mode: " + mode);
    }
    enabled = true;
    path = ledger_path;
    commit_mode = mode;
    loaded_entries = 0;
    appended_entries = 0;
    atomic_rewrite_commits = 0;
    directory_fsync_attempts = 0;
    journal_records_written = 0;
    journal_recovered_after_commit = 0;
    journal_rejections = 0;
    ledger_batch_flush_commits = 0;
    ledger_batch_pending_entries_peak = 0;
    batch_dirty = false;
    batch_pending_entries = 0;
    head_hash = "GENESIS";
    durable_head_hash = "GENESIS";
    durable_line_count = 0;
    effect_transition_head_hash = "GENESIS";
    effect_transition_line_count = 0;
    effect_terminal_transitions = 0;
    effect_transition_rejections = 0;
    terminal_effect_states.clear();
    committed_jtis.clear();
    committed_event_identities.clear();
    committed_effect_idempotency_keys.clear();
    canonical_lines.clear();
    acquire_lock();
    if (reset) {
        (void)::unlink(journal_path().c_str());
        std::string reason;
        if (!durable_replace_lines({}, reason)) {
            throw std::runtime_error("could not reset replay ledger path " + path + ": " + reason);
        }
    } else {
        recover_or_reject_journal();
    }
    std::ifstream in(path, std::ios::binary);
    if (!in) return;  // missing ledger starts empty; append creates it.
    std::string line;
    long long expected_sequence = 1;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        Json entry = parse_json_text(line);
        long long seq = entry.at("sequence").integer();
        std::string previous = entry.at("previous_hash").str();
        std::string entry_hash = entry.at("entry_hash").str();
        std::string case_id = entry.at("case_id").str();
        std::string kind = entry.at("kind").str();
        std::string operation_id = entry.at("operation_id").str();
        std::string contract_digest = entry.at("contract_digest_sha256").str();
        std::string jti = entry.at("jti").str();
        std::string action = entry.at("action").str();
        std::string cloud_event_source = entry.at("cloud_event_source").str();
        std::string cloud_event_id = entry.at("cloud_event_id").str();
        std::string effect_idempotency_key = entry.at("effect_idempotency_key").str();
        std::string effect_state = entry.at("effect_state").str();
        if (seq != expected_sequence) throw std::runtime_error("replay ledger sequence gap at line " + std::to_string(expected_sequence));
        if (previous != head_hash) throw std::runtime_error("replay ledger previous_hash does not match local chain head at sequence " + std::to_string(seq));
        if (!is_lowercase_sha256_hex(effect_idempotency_key)) throw std::runtime_error("replay ledger entry missing effect_idempotency_key at sequence " + std::to_string(seq));
        if (effect_state != kPreparedEffectState) throw std::runtime_error("replay ledger entry has unsupported effect_state at sequence " + std::to_string(seq));
        std::string recomputed = compute_entry_hash(seq, previous, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state);
        if (entry_hash != recomputed) throw std::runtime_error("replay ledger entry hash mismatch at sequence " + std::to_string(seq));
        if (jti.empty()) throw std::runtime_error("replay ledger entry missing jti at sequence " + std::to_string(seq));
        if (!committed_effect_idempotency_keys.insert(effect_idempotency_key).second) throw std::runtime_error("replay ledger contains duplicate effect_idempotency_key at sequence " + std::to_string(seq));
        if (!committed_jtis.insert(jti).second) throw std::runtime_error("replay ledger contains duplicate jti at sequence " + std::to_string(seq));
        if (kind == "asyncapi") {
            const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
            if (event_key.empty()) throw std::runtime_error("replay ledger async entry missing CloudEvents source/id identity at sequence " + std::to_string(seq));
            if (!committed_event_identities.insert(event_key).second) throw std::runtime_error("replay ledger contains duplicate CloudEvents source/id identity at sequence " + std::to_string(seq));
        }
        head_hash = entry_hash;
        canonical_lines.push_back(line);
        loaded_entries++;
        expected_sequence++;
    }
    durable_head_hash = head_hash;
    durable_line_count = loaded_entries;
}

bool ReplayLedger::contains_jti(const std::string& jti) const {
    return enabled && committed_jtis.find(jti) != committed_jtis.end();
}

bool ReplayLedger::contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const {
    if (!enabled) return false;
    const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
    return !event_key.empty() && committed_event_identities.find(event_key) != committed_event_identities.end();
}

bool ReplayLedger::contains_effect_idempotency_key(const std::string& effect_idempotency_key) const {
    return enabled && !effect_idempotency_key.empty() && committed_effect_idempotency_keys.find(effect_idempotency_key) != committed_effect_idempotency_keys.end();
}

bool ReplayLedger::append(const Json& tc, const Json& claims, const std::string& action, std::string& reason) {
    return stage(tc, claims, action, reason);
}

bool ReplayLedger::stage(const Json& tc, const Json& claims, const std::string& action, std::string& reason) {
    if (!enabled) return true;
    std::string jti = claims.at("jti").str();
    if (jti.empty()) { reason = "durable replay ledger append refused an empty jti"; return false; }
    if (committed_jtis.find(jti) != committed_jtis.end()) { reason = "durable replay ledger already contains JWT jti"; return false; }
    long long sequence = loaded_entries + appended_entries + 1;
    std::string previous = head_hash;
    std::string case_id = tc.at("case_id").str();
    std::string kind = tc.at("kind").str();
    std::string operation_id = claims.at("operation_id").str();
    std::string contract_digest = claims.at("contract_digest_sha256").str();
    std::string cloud_event_source = tc.at("cloud_event_source").str();
    std::string cloud_event_id = tc.at("cloud_event_id").str();
    const std::string effect_idempotency_key = effect_idempotency_key_from_case_or_legacy(tc, claims);
    const std::string effect_state = effect_state_from_case_or_default(tc);
    if (!is_lowercase_sha256_hex(effect_idempotency_key)) { reason = "durable replay ledger refuses invalid effect_idempotency_key"; return false; }
    if (effect_state != kPreparedEffectState) { reason = "durable replay ledger refuses non-prepared effect_state"; return false; }
    if (committed_effect_idempotency_keys.find(effect_idempotency_key) != committed_effect_idempotency_keys.end()) { reason = "durable replay ledger already contains prepared effect idempotency key"; return false; }
    const std::string event_key = kind == "asyncapi" ? event_identity_key(cloud_event_source, cloud_event_id) : std::string();
    if (kind == "asyncapi") {
        if (event_key.empty()) { reason = "durable replay ledger refuses async event without CloudEvents source/id identity"; return false; }
        if (committed_event_identities.find(event_key) != committed_event_identities.end()) { reason = "durable replay ledger already contains CloudEvents source/id identity"; return false; }
    }
    std::string entry_hash = compute_entry_hash(sequence, previous, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state);
    std::ostringstream line;
    line << "{\"sequence\":" << sequence
         << ",\"previous_hash\":\"" << json_escape(previous) << "\""
         << ",\"entry_hash\":\"" << json_escape(entry_hash) << "\""
         << ",\"case_id\":\"" << json_escape(case_id) << "\""
         << ",\"kind\":\"" << json_escape(kind) << "\""
         << ",\"operation_id\":\"" << json_escape(operation_id) << "\""
         << ",\"contract_digest_sha256\":\"" << json_escape(contract_digest) << "\""
         << ",\"jti\":\"" << json_escape(jti) << "\""
         << ",\"action\":\"" << json_escape(action) << "\""
         << ",\"cloud_event_source\":\"" << json_escape(cloud_event_source) << "\""
         << ",\"cloud_event_id\":\"" << json_escape(cloud_event_id) << "\""
         << ",\"effect_idempotency_key\":\"" << json_escape(effect_idempotency_key) << "\""
         << ",\"effect_state\":\"" << json_escape(effect_state) << "\"}";
    std::vector<std::string> next_lines = canonical_lines;
    next_lines.push_back(line.str());
    if (commit_mode == "batch") {
        canonical_lines = std::move(next_lines);
        committed_jtis.insert(jti);
        if (!event_key.empty()) committed_event_identities.insert(event_key);
        committed_effect_idempotency_keys.insert(effect_idempotency_key);
        head_hash = entry_hash;
        appended_entries++;
        batch_dirty = true;
        batch_pending_entries++;
        ledger_batch_pending_entries_peak = std::max(ledger_batch_pending_entries_peak, batch_pending_entries);
        reason = "durable replay ledger batch append staged hash-chain entry " + std::to_string(sequence) + " pending explicit batch flush";
        return true;
    }
    if (!durable_replace_lines(next_lines, reason)) return false;
    canonical_lines = std::move(next_lines);
    committed_jtis.insert(jti);
    if (!event_key.empty()) committed_event_identities.insert(event_key);
    committed_effect_idempotency_keys.insert(effect_idempotency_key);
    head_hash = entry_hash;
    appended_entries++;
    reason = "durable replay ledger append committed hash-chain entry " + std::to_string(sequence) + " via locked write-ahead-journal fsync temp-write fsync rename directory-fsync journal-unlink";
    return true;
}

bool ReplayLedger::flush(std::string& reason) {
    return commit(reason);
}

bool ReplayLedger::commit(std::string& reason) {
    if (!enabled) return true;
    if (commit_mode != "batch") { reason = "durable replay ledger immediate mode does not require batch flush"; return true; }
    if (!batch_dirty) { reason = "durable replay ledger batch mode has no pending entries"; return true; }
    if (!durable_replace_lines(canonical_lines, reason)) return false;
    ledger_batch_flush_commits++;
    batch_dirty = false;
    batch_pending_entries = 0;
    reason = "durable replay ledger batch flush committed staged hash-chain entries with one atomic replacement";
    return true;
}

bool ReplayLedger::backup_snapshot(const std::string& snapshot_path, std::string& reason) {
    if (snapshot_path.empty()) return true;
    reason = "local-jsonl replay ledger does not support SQLite backup snapshots";
    return false;
}

void ReplayLedger::recover() {
    if (!enabled) return;
    recover_or_reject_journal();
}

void ReplayLedger::close() {
    release_lock();
}

}  // namespace anonsync
