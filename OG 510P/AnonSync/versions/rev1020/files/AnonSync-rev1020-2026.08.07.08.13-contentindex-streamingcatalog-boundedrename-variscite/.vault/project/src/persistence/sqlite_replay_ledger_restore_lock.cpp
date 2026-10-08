#include "sqlite_replay_ledger_restore_lock.hpp"

#include "sqlite_path_security.hpp"

#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <string>
#include <utility>

#include <sys/file.h>
#include <unistd.h>

namespace anonsync::persistence {
namespace {

[[nodiscard]] std::string restore_lock_path_for(
    const std::string& ledger_path) {
    if (ledger_path.empty()) {
        throw std::runtime_error(
            "sqlite-wal snapshot restore lock requires nonempty ledger path");
    }
    return ledger_path + ".restore.lock";
}

void release_flocked_descriptor_noexcept(int& descriptor) noexcept {
    if (descriptor < 0) return;
    (void)::flock(descriptor, LOCK_UN);
    (void)::close(descriptor);
    descriptor = -1;
}

void write_owner_marker_or_throw(int descriptor,
                                 const std::string& path) {
    constexpr const char* label = "sqlite-wal snapshot restore lock";
    if (descriptor < 0) {
        throw std::runtime_error(
            std::string(label) + " marker descriptor is invalid");
    }
    if (::ftruncate(descriptor, 0) != 0) {
        throw std::runtime_error(
            std::string(label) + " marker truncate failed for " + path +
            ": " + std::strerror(errno));
    }
    if (::lseek(descriptor, 0, SEEK_SET) < 0) {
        throw std::runtime_error(
            std::string(label) + " marker seek failed for " + path + ": " +
            std::strerror(errno));
    }

    const std::string marker =
        "pid=" + std::to_string(static_cast<long long>(::getpid())) + "\n";
    std::size_t written = 0;
    while (written < marker.size()) {
        const ssize_t rc = ::write(
            descriptor, marker.data() + written, marker.size() - written);
        if (rc < 0 && errno == EINTR) continue;
        if (rc <= 0) {
            const int write_error = rc < 0 ? errno : EIO;
            throw std::runtime_error(
                std::string(label) + " marker write failed for " + path +
                ": " + std::strerror(write_error));
        }
        written += static_cast<std::size_t>(rc);
    }
    if (::fsync(descriptor) != 0) {
        throw std::runtime_error(
            std::string(label) + " marker sync failed for " + path + ": " +
            std::strerror(errno));
    }
}

}  // namespace

struct SqliteReplayLedgerRestoreLock::State final {
    std::string path;
    SqlitePathFamilyGuard path_guard;
    int descriptor = -1;

    ~State() { release_flocked_descriptor_noexcept(descriptor); }
};

SqliteReplayLedgerRestoreLock::SqliteReplayLedgerRestoreLock(
    const std::string& ledger_path)
    : process_id_(current_sync_process_incarnation_noexcept()),
      state_(std::make_unique<State>()) {
    state_->path = restore_lock_path_for(ledger_path);
    state_->path_guard = guard_sqlite_path_family_or_throw(
        state_->path, true, {}, "sqlite-wal snapshot restore lock");
    state_->descriptor = state_->path_guard.open_private_lock_file_or_throw(
        "sqlite-wal snapshot restore lock");
    try {
        if (::flock(state_->descriptor, LOCK_EX | LOCK_NB) != 0) {
            throw std::runtime_error(
                "sqlite-wal snapshot restore lock contention on " +
                state_->path + ": " + std::strerror(errno));
        }
        write_owner_marker_or_throw(state_->descriptor, state_->path);
    } catch (...) {
        release_flocked_descriptor_noexcept(state_->descriptor);
        throw;
    }
}

SqliteReplayLedgerRestoreLock::~SqliteReplayLedgerRestoreLock() {
    if (!sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    state_.reset();
}

}  // namespace anonsync::persistence
