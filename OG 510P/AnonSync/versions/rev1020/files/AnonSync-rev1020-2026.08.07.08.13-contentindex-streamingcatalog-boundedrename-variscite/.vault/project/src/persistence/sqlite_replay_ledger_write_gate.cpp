#include "sqlite_replay_ledger_write_gate.hpp"

#include "sqlite_path_security.hpp"
#include "sync_sqlite_mutex_capability.hpp"
#include "sync_process_incarnation.hpp"

#include <cerrno>
#include <cstring>
#include <filesystem>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <sys/file.h>
#include <unistd.h>

namespace anonsync::persistence {
namespace {

struct HeldWriteGateState final {
    SyncProcessIncarnation process_id;
    std::uint64_t next_scope_token = 1;
    std::unordered_map<std::string, std::vector<std::uint64_t>> scope_stacks;
};

HeldWriteGateState& current_thread_write_gate_state() {
    thread_local HeldWriteGateState state;
    const SyncProcessIncarnation current =
        current_sync_process_incarnation_noexcept();
    if (state.process_id != current) {
        // fork() copies thread-local bytes; inherited recursion evidence is not
        // authority in the child process incarnation. File descriptors remain
        // bound to their original objects and their child destruction fails
        // stopped before they can release the parent's capability.
        state.scope_stacks.clear();
        state.next_scope_token = 1;
        state.process_id = current;
    }
    return state;
}

std::uint64_t allocate_scope_token_or_throw(HeldWriteGateState& state) {
    if (state.next_scope_token == 0 ||
        state.next_scope_token == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "sqlite-wal replay ledger write-gate scope token exhausted");
    }
    return state.next_scope_token++;
}

std::string normalized_gate_key(const std::filesystem::path& path) {
    std::error_code error;
    const std::filesystem::path absolute = std::filesystem::absolute(path, error);
    return error ? path.lexically_normal().string()
                 : absolute.lexically_normal().string();
}

void release_descriptor_noexcept(int& fd) noexcept {
    if (fd < 0) return;
    (void)::flock(fd, LOCK_UN);
    (void)::close(fd);
    fd = -1;
}

void write_owner_marker_or_throw(int fd,
                                 const std::filesystem::path& path) {
    if (fd < 0) {
        throw std::runtime_error(
            "sqlite-wal replay ledger write-gate marker descriptor is invalid");
    }
    if (::ftruncate(fd, 0) != 0) {
        throw std::runtime_error(
            "sqlite-wal replay ledger write-gate marker truncate failed for " +
            path.string() + ": " + std::strerror(errno));
    }
    if (::lseek(fd, 0, SEEK_SET) < 0) {
        throw std::runtime_error(
            "sqlite-wal replay ledger write-gate marker seek failed for " +
            path.string() + ": " + std::strerror(errno));
    }
    const std::string marker =
        "pid=" + std::to_string(static_cast<long long>(::getpid())) + "\n";
    std::size_t written = 0;
    while (written < marker.size()) {
        const ssize_t result =
            ::write(fd, marker.data() + written, marker.size() - written);
        if (result < 0 && errno == EINTR) continue;
        if (result <= 0) {
            const int error = result < 0 ? errno : EIO;
            throw std::runtime_error(
                "sqlite-wal replay ledger write-gate marker write failed for " +
                path.string() + ": " + std::strerror(error));
        }
        written += static_cast<std::size_t>(result);
    }
    if (::fsync(fd) != 0) {
        throw std::runtime_error(
            "sqlite-wal replay ledger write-gate marker sync failed for " +
            path.string() + ": " + std::strerror(errno));
    }
}

}  // namespace

struct SqliteReplayLedgerWriteGate::State final {
    SyncProcessIncarnation process_id;
    SyncSqliteThreadIncarnation thread_incarnation;
    std::filesystem::path path;
    std::string key;
    std::uint64_t scope_token = 0;
    std::unique_ptr<SqlitePathFamilyGuard> path_guard;
    int fd = -1;
    bool nested = false;
    bool owns = false;
};

std::filesystem::path sqlite_replay_ledger_write_gate_path(
    const std::filesystem::path& ledger_path) {
    if (ledger_path.empty()) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger write-gate requires nonempty ledger path");
    }
    return std::filesystem::path(ledger_path.string() + ".write.lock");
}

SqliteReplayLedgerWriteGate::SqliteReplayLedgerWriteGate(
    const std::filesystem::path& ledger_path,
    SqliteReplayLedgerWriteGateNesting nesting,
    SqliteReplayLedgerWriteGateParentPolicy parent_policy)
    : state_(std::make_unique<State>()) {
    state_->process_id = current_sync_process_incarnation_noexcept();
    state_->thread_incarnation =
        current_sync_sqlite_thread_incarnation_noexcept();
    state_->path = sqlite_replay_ledger_write_gate_path(ledger_path);
    state_->key = normalized_gate_key(state_->path);

    HeldWriteGateState& held = current_thread_write_gate_state();
    auto existing = held.scope_stacks.find(state_->key);
    if (existing != held.scope_stacks.end() && !existing->second.empty()) {
        if (nesting == SqliteReplayLedgerWriteGateNesting::RejectSameThread) {
            throw std::runtime_error(
                "sqlite-wal replay ledger write-gate rejects same-thread nested ownership for " +
                state_->path.string());
        }
        state_->scope_token = allocate_scope_token_or_throw(held);
        existing->second.push_back(state_->scope_token);
        state_->nested = true;
        state_->owns = true;
        return;
    }

    state_->path_guard = std::make_unique<SqlitePathFamilyGuard>(
        guard_sqlite_path_family_or_throw(
            state_->path,
            parent_policy ==
                SqliteReplayLedgerWriteGateParentPolicy::CreatePrivateParents,
            {}, "sqlite-wal replay ledger write-gate"));
    state_->fd = state_->path_guard->open_private_lock_file_or_throw(
        "sqlite-wal replay ledger write-gate");
    try {
        if (::flock(state_->fd, LOCK_EX | LOCK_NB) != 0) {
            throw std::runtime_error(
                "sqlite-wal replay ledger write-gate lock contention on " +
                state_->path.string() + ": " + std::strerror(errno));
        }
        write_owner_marker_or_throw(state_->fd, state_->path);
        state_->scope_token = allocate_scope_token_or_throw(held);
        auto [position, inserted] = held.scope_stacks.try_emplace(state_->key);
        if (!inserted && !position->second.empty()) {
            throw std::logic_error(
                "sqlite-wal replay ledger write-gate ownership registry changed during acquisition");
        }
        position->second.push_back(state_->scope_token);
        state_->owns = true;
    } catch (...) {
        release_descriptor_noexcept(state_->fd);
        throw;
    }
}

SqliteReplayLedgerWriteGate::~SqliteReplayLedgerWriteGate() {
    if (!state_) return;
    if (!sync_process_incarnation_is_current(state_->process_id)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    if (!sync_sqlite_thread_incarnation_is_current(
            state_->thread_incarnation)) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }

    HeldWriteGateState& held = current_thread_write_gate_state();
    const auto position = held.scope_stacks.find(state_->key);
    if (!state_->owns || state_->scope_token == 0 ||
        position == held.scope_stacks.end() || position->second.empty() ||
        position->second.back() != state_->scope_token) {
        // Releasing an outer scope while a nested scope is still live would
        // unlock the kernel file while the inner object continued to report
        // authority. Destructors cannot repair that lifetime inversion.
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    position->second.pop_back();
    if (state_->nested) {
        if (position->second.empty()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    } else {
        if (!position->second.empty()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        release_descriptor_noexcept(state_->fd);
        held.scope_stacks.erase(position);
    }
    state_->owns = false;
}

bool SqliteReplayLedgerWriteGate::owns_exclusive_gate() const noexcept {
    if (!state_ || !state_->owns) return false;
    if (!sync_process_incarnation_is_current(state_->process_id)) return false;
    if (!sync_sqlite_thread_incarnation_is_current(
            state_->thread_incarnation)) {
        return false;
    }
    return true;
}

}  // namespace anonsync::persistence
