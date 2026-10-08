#include "inherited_test_process.hpp"
#include "resumable_sha256.hpp"
#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_file_payload_terminal_verification_state.hpp"
#include "sync_replica_file_payload_scrub_state.hpp"
#include "sync_replica_file_payload_verification_index.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <array>
#include <chrono>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <memory>
#include <new>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#if defined(__linux__)
#include <sys/inotify.h>
#endif
#include <unistd.h>

namespace {

struct AllocationFaultState final {
    std::size_t attempts = 0U;
    std::size_t fail_at = 0U;
    bool armed = false;
};

AllocationFaultState g_allocation_fault;

[[nodiscard]] bool allocation_should_fail() noexcept {
    if (!g_allocation_fault.armed) return false;
    ++g_allocation_fault.attempts;
    return g_allocation_fault.fail_at != 0U &&
           g_allocation_fault.attempts == g_allocation_fault.fail_at;
}

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    if (allocation_should_fail()) throw std::bad_alloc();
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

}  // namespace

void* operator new(std::size_t size) {
    return allocate_or_throw(size);
}

void* operator new[](std::size_t size) {
    return allocate_or_throw(size);
}

void operator delete(void* memory) noexcept {
    std::free(memory);
}

void operator delete[](void* memory) noexcept {
    std::free(memory);
}

void operator delete(void* memory, std::size_t) noexcept {
    std::free(memory);
}

void operator delete[](void* memory, std::size_t) noexcept {
    std::free(memory);
}

namespace anonsync {

struct SyncReplicaFilePayloadStoreTestAccess final {
    [[nodiscard]] static std::optional<std::uint64_t>
    payload_availability_generation_or_throw(
        const SyncReplicaFilePayloadStore& store,
        std::string_view label) {
        return store.payload_availability_generation_or_throw(label);
    }

    [[nodiscard]] static SyncReplicaFilePayloadStoreLiveCapabilityCutpoint
    live_capability_cutpoint_excluding_snapshot_or_throw(
        const SyncReplicaFilePayloadStore& store,
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view label) {
        return store.live_capability_cutpoint_excluding_snapshot_or_throw(
            snapshot, label);
    }

    [[nodiscard]] static SyncReplicaFilePayloadStoreSnapshot
    writer_fenced_retention_snapshot_or_throw(
        const SyncReplicaFilePayloadStore& store) {
        return store.snapshot_writer_fenced_for_retention_or_throw();
    }

    [[nodiscard]] static bool
    writer_fenced_payload_use_exclusive_available_or_throw(
        const SyncReplicaFilePayloadStore& store,
        const SyncReplicaFilePayloadStoreSnapshot& snapshot,
        std::string_view content_sha256,
        std::uint64_t size_bytes,
        std::string_view label) {
        return store.writer_fenced_payload_use_exclusive_available_or_throw(
            snapshot, content_sha256, size_bytes, label);
    }

    [[nodiscard]] static SyncReplicaFilePayloadRetentionMarkPublication
    publish_retention_mark_or_throw(
        const SyncReplicaFilePayloadStore& store,
        const SyncReplicaFilePayloadStoreSnapshot& writer_fenced_snapshot,
        SyncReplicaFilePayloadRetentionMark mark) {
        return store.publish_retention_mark_or_throw(
            writer_fenced_snapshot, std::move(mark));
    }
};

}  // namespace anonsync

namespace {

namespace fs = std::filesystem;

constexpr std::string_view kStandaloneIdentityCurrent =
    ".anonsync-payload-store-identity-v2-reader-fence-v1";
constexpr std::string_view kStandaloneIdentityLegacyReader =
    ".anonsync-payload-store-identity-v2";
constexpr std::string_view kProductIdentityCurrent =
    ".anonsync-payload-store-identity-v3-reader-fence-v1";
constexpr std::string_view kProductIdentityLegacyReader =
    ".anonsync-payload-store-identity-v3";

std::uint64_t checks = 0U;

class AllocationArm final {
public:
    explicit AllocationArm(std::size_t fail_at) noexcept {
        g_allocation_fault.attempts = 0U;
        g_allocation_fault.fail_at = fail_at;
        g_allocation_fault.armed = true;
    }

    AllocationArm(const AllocationArm&) = delete;
    AllocationArm& operator=(const AllocationArm&) = delete;

    ~AllocationArm() { disarm(); }

    void disarm() noexcept { g_allocation_fault.armed = false; }

    [[nodiscard]] std::size_t attempts() const noexcept {
        return g_allocation_fault.attempts;
    }
};

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename ScannedOwner>
void require_reuse_partition(
    const ScannedOwner& owner,
    std::uint64_t process_entries,
    std::uint64_t process_bytes,
    std::uint64_t durable_entries,
    std::uint64_t durable_bytes,
    const std::string& message) {
    require(
        owner.scan_process_reused_entry_count() == process_entries &&
            owner.scan_process_reused_bytes() == process_bytes &&
            owner.scan_durable_reused_entry_count() == durable_entries &&
            owner.scan_durable_reused_bytes() == durable_bytes &&
            owner.scan_reused_entry_count() ==
                process_entries + durable_entries &&
            owner.scan_reused_bytes() == process_bytes + durable_bytes,
        message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

template <typename Callable>
void require_lease_busy(
    Callable&& callable,
    anonsync::SyncReplicaFilePayloadStoreLeaseMode expected_mode,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const anonsync::SyncReplicaFilePayloadStoreLeaseBusyError& error) {
        if (error.mode() != expected_mode) {
            fail(message + ": typed contention reported the wrong lease mode");
        }
        if (std::string_view(error.what()).find("lease is busy") ==
            std::string_view::npos) {
            fail(message + ": typed contention lost its diagnostic context");
        }
        return;
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

template <typename Callable>
void require_integrity_error(
    Callable&& callable,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256,
    bool expected_failure_persisted,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const anonsync::SyncReplicaFilePayloadStoreIntegrityError& error) {
        if (error.expected_content_sha256() != expected_content_sha256 ||
            error.observed_content_sha256() != observed_content_sha256 ||
            error.failure_persisted() != expected_failure_persisted) {
            fail(
                message + ": typed integrity evidence was not exact; got " +
                error.expected_content_sha256() + "/" +
                error.observed_content_sha256() + "/" +
                (error.failure_persisted() ? "persisted" : "volatile"));
        }
        return;
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
                ("anonsync-payload-store-" +
                 std::to_string(static_cast<unsigned long long>(::getpid())) +
                 "-" + std::to_string(tick));
        fs::create_directory(path_);
        if (::chmod(path_.c_str(), 0700) != 0) {
            fail("could not make payload-store test root private");
        }
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] fs::path make_store_root(std::string_view name) const {
        const fs::path root = path_ / std::string(name);
        fs::create_directory(root);
        if (::chmod(root.c_str(), 0700) != 0) {
            fail("could not make payload-store fixture private");
        }
        return root;
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void close_descriptor_noexcept(int& descriptor) noexcept {
    const int owned = std::exchange(descriptor, -1);
    if (owned >= 0) (void)::close(owned);
}

[[nodiscard]] bool publish_control_byte_noexcept(
    const char* path, char byte) noexcept {
    int descriptor;
    do {
        descriptor = ::open(
            path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) return false;

    ssize_t written;
    do {
        written = ::write(descriptor, &byte, 1U);
    } while (written < 0 && errno == EINTR);
    const int close_result = ::close(descriptor);
    return written == 1 && close_result == 0;
}

[[nodiscard]] char read_control_byte_or_fail(
    const fs::path& path, const std::string& label) {
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) fail(label + " control marker open failed");

    char byte = 0;
    ssize_t result;
    do {
        result = ::read(descriptor, &byte, 1U);
    } while (result < 0 && errno == EINTR);
    const int close_result = ::close(descriptor);
    if (result != 1 || close_result != 0) {
        fail(label + " control marker read failed");
    }
    return byte;
}

[[nodiscard]] bool control_marker_exists_or_throw(
    const fs::path& path, const std::string& label) {
    struct stat status {};
    int result;
    do {
        result = ::lstat(path.c_str(), &status);
    } while (result != 0 && errno == EINTR);
    if (result == 0) {
        if (!S_ISREG(status.st_mode)) {
            fail(label + " control marker is not a regular file");
        }
        // O_CREAT makes the final pathname visible before the child writes its
        // status byte. Existence alone is therefore not publication: under
        // parallel test load the parent can otherwise open the transient empty
        // file and misclassify a healthy child as failed. A one-byte size is the
        // readiness cutpoint for this control protocol.
        if (status.st_size == 0) return false;
        if (status.st_size != 1) {
            fail(label + " control marker has an invalid size");
        }
        return true;
    }
    if (errno == ENOENT) return false;
    fail(label + " control marker observation failed");
}

void remove_control_marker_or_fail(
    const fs::path& path, const std::string& label) {
    std::error_code error;
    (void)fs::remove(path, error);
    if (error) fail(label + " stale control marker removal failed");
}

class ChildHeldFileLock final {
public:
    ChildHeldFileLock(
        const fs::path& path,
        int operation,
        const fs::path& control_directory,
        std::string_view token)
        : ready_path_(control_directory /
                      ("payload-store-lease-" + std::string(token) +
                       "-ready")),
          release_path_(control_directory /
                        ("payload-store-lease-" + std::string(token) +
                         "-release")) {
        remove_control_marker_or_fail(
            ready_path_, "payload-store child readiness");
        remove_control_marker_or_fail(
            release_path_, "payload-store child release");

        const std::string lock_path = path.string();
        const std::string ready_path = ready_path_.string();
        const std::string release_path = release_path_.string();
        auto child_entry = [lock_path, ready_path, release_path,
                            operation]() noexcept -> int {
            int descriptor;
            do {
                descriptor =
                    ::open(lock_path.c_str(), O_RDONLY | O_CLOEXEC);
            } while (descriptor < 0 && errno == EINTR);
            if (descriptor < 0) {
                (void)publish_control_byte_noexcept(ready_path.c_str(), 'O');
                return 111;
            }

            int lock_result;
            do {
                lock_result = ::flock(descriptor, operation | LOCK_NB);
            } while (lock_result != 0 && errno == EINTR);
            if (lock_result != 0) {
                close_descriptor_noexcept(descriptor);
                (void)publish_control_byte_noexcept(ready_path.c_str(), 'L');
                return 112;
            }
            if (!publish_control_byte_noexcept(ready_path.c_str(), 'R')) {
                close_descriptor_noexcept(descriptor);
                return 113;
            }

            const auto release_deadline =
                std::chrono::steady_clock::now() +
                std::chrono::seconds(30);
            while (std::chrono::steady_clock::now() < release_deadline) {
                struct stat status {};
                int result;
                do {
                    result = ::lstat(release_path.c_str(), &status);
                } while (result != 0 && errno == EINTR);
                if (result == 0) {
                    const bool regular = S_ISREG(status.st_mode);
                    close_descriptor_noexcept(descriptor);
                    return regular ? 0 : 114;
                }
                if (errno != ENOENT) {
                    close_descriptor_noexcept(descriptor);
                    return 115;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
            close_descriptor_noexcept(descriptor);
            return 116;
        };
        child_.emplace(
            anonsync::test::spawn_inherited_test_process_or_throw(
                child_entry, "payload-store inherited lease holder"));

        const auto ready_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(5);
        while (!control_marker_exists_or_throw(
            ready_path_, "payload-store child readiness")) {
            if (std::chrono::steady_clock::now() >= ready_deadline) {
                fail("payload-store child lease holder did not become ready");
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        const char status = read_control_byte_or_fail(
            ready_path_, "payload-store child readiness");
        if (status != 'R') {
            const int wait_status = child_->wait_for_exit(
                std::chrono::seconds(5),
                "payload-store failed inherited lease holder");
            child_.reset();
            fail("child could not acquire payload-store fixture lock: status=" +
                 std::string(1U, status) +
                 ", wait_status=" + std::to_string(wait_status));
        }
    }

    ChildHeldFileLock(const ChildHeldFileLock&) = delete;
    ChildHeldFileLock& operator=(const ChildHeldFileLock&) = delete;

    ~ChildHeldFileLock() { finish_noexcept(); }

    void release_and_wait_or_fail() {
        if (!child_) return;
        if (!publish_control_byte_noexcept(release_path_.c_str(), 'X')) {
            fail("payload-store child lease release publication failed");
        }
        child_->wait_for_exact_exit(
            0, std::chrono::seconds(5),
            "payload-store inherited lease holder release");
        child_.reset();
        remove_control_marker_or_fail(
            ready_path_, "payload-store child readiness");
        remove_control_marker_or_fail(
            release_path_, "payload-store child release");
    }

private:
    void finish_noexcept() noexcept {
        if (child_) {
            (void)publish_control_byte_noexcept(release_path_.c_str(), 'X');
            try {
                (void)child_->wait_for_exit(
                    std::chrono::seconds(5),
                    "payload-store inherited lease holder cleanup");
            } catch (...) {
                // The move-only owner terminates and reaps any still-active
                // process group when the optional is reset below.
            }
            child_.reset();
        }
        std::error_code ignored;
        (void)fs::remove(ready_path_, ignored);
        ignored.clear();
        (void)fs::remove(release_path_, ignored);
    }

    fs::path ready_path_;
    fs::path release_path_;
    std::optional<anonsync::test::InheritedTestProcess> child_;
};

// Keeps one descriptor inherited through fork alive after the parent closes its
// copy. This proves that an API-issued payload-use lease is attached to the
// open file description and remains visible to a different process until the
// final inherited descriptor closes.
class ChildHeldInheritedDescriptor final {
public:
    ChildHeldInheritedDescriptor(
        int inherited_descriptor,
        const fs::path& control_directory,
        std::string_view token)
        : ready_path_(control_directory /
                      ("payload-use-inherited-" + std::string(token) +
                       "-ready")),
          release_path_(control_directory /
                        ("payload-use-inherited-" + std::string(token) +
                         "-release")) {
        if (inherited_descriptor < 0) {
            fail("payload-use inherited descriptor is invalid");
        }
        remove_control_marker_or_fail(
            ready_path_, "payload-use inherited readiness");
        remove_control_marker_or_fail(
            release_path_, "payload-use inherited release");

        const std::string ready_path = ready_path_.string();
        const std::string release_path = release_path_.string();
        auto child_entry = [inherited_descriptor, ready_path,
                            release_path]() mutable noexcept -> int {
            if (::fcntl(inherited_descriptor, F_GETFD) < 0) {
                (void)publish_control_byte_noexcept(ready_path.c_str(), 'D');
                return 117;
            }
            if (!publish_control_byte_noexcept(ready_path.c_str(), 'R')) {
                close_descriptor_noexcept(inherited_descriptor);
                return 118;
            }

            const auto release_deadline =
                std::chrono::steady_clock::now() +
                std::chrono::seconds(30);
            while (std::chrono::steady_clock::now() < release_deadline) {
                struct stat status {};
                int result;
                do {
                    result = ::lstat(release_path.c_str(), &status);
                } while (result != 0 && errno == EINTR);
                if (result == 0) {
                    const bool regular = S_ISREG(status.st_mode);
                    close_descriptor_noexcept(inherited_descriptor);
                    return regular ? 0 : 119;
                }
                if (errno != ENOENT) {
                    close_descriptor_noexcept(inherited_descriptor);
                    return 120;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
            close_descriptor_noexcept(inherited_descriptor);
            return 121;
        };
        child_.emplace(
            anonsync::test::spawn_inherited_test_process_or_throw(
                child_entry, "payload-use inherited descriptor holder"));

        const auto ready_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(5);
        while (!control_marker_exists_or_throw(
            ready_path_, "payload-use inherited readiness")) {
            if (std::chrono::steady_clock::now() >= ready_deadline) {
                fail("payload-use inherited descriptor holder did not become ready");
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        const char status = read_control_byte_or_fail(
            ready_path_, "payload-use inherited readiness");
        if (status != 'R') {
            const int wait_status = child_->wait_for_exit(
                std::chrono::seconds(5),
                "failed payload-use inherited descriptor holder");
            child_.reset();
            fail("child did not inherit the payload-use descriptor: status=" +
                 std::string(1U, status) +
                 ", wait_status=" + std::to_string(wait_status));
        }
    }

    ChildHeldInheritedDescriptor(const ChildHeldInheritedDescriptor&) = delete;
    ChildHeldInheritedDescriptor& operator=(
        const ChildHeldInheritedDescriptor&) = delete;

    ~ChildHeldInheritedDescriptor() { finish_noexcept(); }

    void release_and_wait_or_fail() {
        if (!child_) return;
        if (!publish_control_byte_noexcept(release_path_.c_str(), 'X')) {
            fail("payload-use inherited descriptor release publication failed");
        }
        child_->wait_for_exact_exit(
            0, std::chrono::seconds(5),
            "payload-use inherited descriptor release");
        child_.reset();
        remove_control_marker_or_fail(
            ready_path_, "payload-use inherited readiness");
        remove_control_marker_or_fail(
            release_path_, "payload-use inherited release");
    }

private:
    void finish_noexcept() noexcept {
        if (child_) {
            (void)publish_control_byte_noexcept(release_path_.c_str(), 'X');
            try {
                (void)child_->wait_for_exit(
                    std::chrono::seconds(5),
                    "payload-use inherited descriptor cleanup");
            } catch (...) {
            }
            child_.reset();
        }
        std::error_code ignored;
        (void)fs::remove(ready_path_, ignored);
        ignored.clear();
        (void)fs::remove(release_path_, ignored);
    }

    fs::path ready_path_;
    fs::path release_path_;
    std::optional<anonsync::test::InheritedTestProcess> child_;
};

void write_private_file(const fs::path& path, std::string_view bytes) {
    int descriptor;
    do {
        descriptor = ::open(
            path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        fail("could not create private payload-store fixture");
    }
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        ssize_t written;
        do {
            written = ::write(
                descriptor, bytes.data() + offset, bytes.size() - offset);
        } while (written < 0 && errno == EINTR);
        if (written <= 0) {
            (void)::close(descriptor);
            fail("could not write private payload-store fixture");
        }
        offset += static_cast<std::size_t>(written);
    }
    int sync_result;
    do {
        sync_result = ::fsync(descriptor);
    } while (sync_result != 0 && errno == EINTR);
    if (sync_result != 0 || ::close(descriptor) != 0) {
        fail("could not synchronize private payload-store fixture");
    }
}

void overwrite_private_file(const fs::path& path, std::string_view bytes) {
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), O_WRONLY | O_TRUNC | O_CLOEXEC);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        fail("could not open private payload-store overwrite fixture");
    }
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        ssize_t written;
        do {
            written = ::write(
                descriptor, bytes.data() + offset, bytes.size() - offset);
        } while (written < 0 && errno == EINTR);
        if (written <= 0) {
            (void)::close(descriptor);
            fail("could not write private payload-store overwrite fixture");
        }
        offset += static_cast<std::size_t>(written);
    }
    int sync_result;
    do {
        sync_result = ::fsync(descriptor);
    } while (sync_result != 0 && errno == EINTR);
    if (sync_result != 0 || ::close(descriptor) != 0) {
        fail("could not synchronize private payload-store overwrite fixture");
    }
}

[[nodiscard]] std::pair<std::uint64_t, std::uint64_t>
private_file_identity(const fs::path& path) {
    struct stat status {};
    int result;
    do {
        result = ::stat(path.c_str(), &status);
    } while (result != 0 && errno == EINTR);
    if (result != 0 || !S_ISREG(status.st_mode)) {
        fail("could not observe private payload-store fixture identity");
    }
    return {
        static_cast<std::uint64_t>(status.st_dev),
        static_cast<std::uint64_t>(status.st_ino),
    };
}

[[nodiscard]] anonsync::SyncPosixRegularFileSnapshotMetadata
private_file_metadata(const fs::path& path, const std::string& label) {
    struct stat status {};
    int result;
    do {
        result = ::stat(path.c_str(), &status);
    } while (result != 0 && errno == EINTR);
    if (result != 0) fail(label + " stat failed");
    return anonsync::
        sync_posix_regular_file_snapshot_metadata_from_status_or_throw(
            status, anonsync::SyncPosixDescriptorLinkPolicy::exactly_one,
            label);
}


void append_transient_oracle_u64(
    anonsync::Sha256DigestBuilder& digest,
    std::uint64_t value) {
    std::string bytes(8U, '\0');
    for (std::size_t index = bytes.size(); index != 0U; --index) {
        bytes[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(bytes);
}

void append_transient_oracle_string(
    anonsync::Sha256DigestBuilder& digest,
    std::string_view value) {
    append_transient_oracle_u64(
        digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

void append_transient_oracle_metadata(
    anonsync::Sha256DigestBuilder& digest,
    const anonsync::SyncPosixRegularFileSnapshotMetadata& metadata) {
    std::string bytes;
    bytes.reserve(static_cast<std::size_t>(
        anonsync::kSyncPosixRegularFileSnapshotMetadataEncodedBytes));
    anonsync::append_sync_posix_regular_file_snapshot_metadata_binary(
        bytes, metadata);
    require(
        bytes.size() ==
            anonsync::kSyncPosixRegularFileSnapshotMetadataEncodedBytes,
        "transient namespace test oracle metadata width drifted");
    append_transient_oracle_string(digest, bytes);
}

struct ExpectedTransientPrefix final {
    std::string basename;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t committed_prefix_bytes = 0U;
    std::uint64_t actual_size_bytes = 0U;
    anonsync::SyncPosixRegularFileSnapshotMetadata metadata;
};

struct ExpectedTransientAssembly final {
    std::string basename;
    std::uint64_t size_bytes = 0U;
    anonsync::SyncPosixRegularFileSnapshotMetadata metadata;
};

[[nodiscard]] std::string expected_transient_namespace_digest(
    const ExpectedTransientPrefix* prefix,
    const ExpectedTransientAssembly* assembly) {
    anonsync::Sha256DigestBuilder digest;
    append_transient_oracle_string(
        digest,
        "anonsync:sync-replica-file-payload-store-transient-namespace:v2");

    append_transient_oracle_string(digest, "staged_prefix");
    append_transient_oracle_u64(digest, prefix == nullptr ? 0U : 1U);
    if (prefix != nullptr) {
        append_transient_oracle_string(digest, prefix->basename);
        append_transient_oracle_string(digest, prefix->content_sha256);
        append_transient_oracle_u64(digest, prefix->total_size_bytes);
        append_transient_oracle_u64(
            digest, prefix->committed_prefix_bytes);
        append_transient_oracle_u64(digest, prefix->actual_size_bytes);
        append_transient_oracle_metadata(digest, prefix->metadata);
    }

    append_transient_oracle_string(digest, "staged_range");
    append_transient_oracle_u64(digest, 0U);

    append_transient_oracle_string(digest, "assembly_residue");
    append_transient_oracle_u64(digest, assembly == nullptr ? 0U : 1U);
    if (assembly != nullptr) {
        append_transient_oracle_string(digest, assembly->basename);
        append_transient_oracle_u64(digest, assembly->size_bytes);
        append_transient_oracle_metadata(digest, assembly->metadata);
    }

    append_transient_oracle_string(digest, "publication_residue");
    append_transient_oracle_u64(digest, 0U);

    const std::uint64_t count =
        (prefix == nullptr ? 0U : 1U) +
        (assembly == nullptr ? 0U : 1U);
    const std::uint64_t physical_bytes =
        (prefix == nullptr ? 0U : prefix->actual_size_bytes) +
        (assembly == nullptr ? 0U : assembly->size_bytes);
    const std::uint64_t reserved_bytes =
        (prefix == nullptr ? 0U : prefix->total_size_bytes) +
        (assembly == nullptr ? 0U : assembly->size_bytes);
    append_transient_oracle_u64(digest, count);
    append_transient_oracle_u64(digest, physical_bytes);
    append_transient_oracle_u64(digest, reserved_bytes);
    return digest.finish_hex();
}

void replace_private_file(const fs::path& path, std::string_view bytes) {
    fs::path replacement = path;
    replacement += ".replacement";
    std::error_code ignored;
    (void)fs::remove(replacement, ignored);
    write_private_file(replacement, bytes);
    int result;
    do {
        result = ::rename(replacement.c_str(), path.c_str());
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        fail("could not atomically replace private payload-store fixture");
    }
}

void rename_private_file_and_sync_directory(
    const fs::path& source,
    const fs::path& destination,
    const std::string& label) {
    int result;
    do {
        result = ::rename(source.c_str(), destination.c_str());
    } while (result != 0 && errno == EINTR);
    if (result != 0) fail(label + " rename failed");

    int directory_descriptor;
    do {
        directory_descriptor = ::open(
            destination.parent_path().c_str(),
            O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    } while (directory_descriptor < 0 && errno == EINTR);
    if (directory_descriptor < 0) {
        fail(label + " parent directory open failed");
    }
    int sync_result;
    do {
        sync_result = ::fsync(directory_descriptor);
    } while (sync_result != 0 && errno == EINTR);
    const int close_result = ::close(directory_descriptor);
    if (sync_result != 0 || close_result != 0) {
        fail(label + " parent directory synchronization failed");
    }
}

[[nodiscard]] anonsync::SyncReplicaDeploymentIdentity product_identity(
    const TemporaryDirectory& temporary,
    char deployment_byte = 'a',
    char digest_byte = 'b') {
    return {
        .deployment_id = std::string(64U, deployment_byte),
        .manifest_digest = std::string(64U, digest_byte),
        .manifest_path = temporary.path() / "deployment.json",
        .folder_id = "folder-product-bound-payload",
        .local_actor = {"device-product-bound", 17U},
    };
}

[[nodiscard]] std::string framed_marker_field(std::string_view value) {
    return std::to_string(value.size()) + ":" + std::string(value);
}

[[nodiscard]] std::string product_identity_marker_bytes(
    const anonsync::SyncReplicaDeploymentIdentity& identity) {
    return
        "anonsync:sync-replica-file-payload-store-identity:v3\n" +
        framed_marker_field(identity.deployment_id) +
        framed_marker_field(identity.manifest_digest) +
        framed_marker_field(identity.manifest_path.generic_string()) +
        framed_marker_field(identity.folder_id) +
        framed_marker_field(identity.local_actor.device_id) +
        framed_marker_field(std::to_string(identity.local_actor.epoch)) +
        framed_marker_field(
            "anonsync:sync-replica-file-payload-store-flock-lease:v1");
}

[[nodiscard]] std::string read_file_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) fail("could not open payload-store fixture for reading");
    const std::string bytes{
        std::istreambuf_iterator<char>(input),
        std::istreambuf_iterator<char>()};
    if (input.bad()) fail("could not finish reading payload-store fixture");
    return bytes;
}

[[nodiscard]] anonsync::SyncReplicaFilePayloadScrubState
read_scrub_state_or_fail(
    const fs::path& root,
    std::uint64_t max_payload_bytes,
    const std::string& label) {
    return anonsync::parse_sync_replica_file_payload_scrub_state_or_throw(
        read_file_bytes(
            root / std::string(
                       anonsync::kSyncReplicaFilePayloadScrubStateBasename)),
        max_payload_bytes, label);
}

struct MetadataHiddenCorruptionFixture final {
    fs::path root;
    std::string folder;
    std::string expected_digest;
    std::string observed_digest;
    std::uint64_t max_payload_bytes = 0U;
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
};

[[nodiscard]] std::string fixed_width_decimal(std::size_t value) {
    std::string digits = std::to_string(value);
    if (digits.size() > 4U) fail("allocation fixture ordinal overflow");
    return std::string(4U - digits.size(), '0') + digits;
}

[[nodiscard]] MetadataHiddenCorruptionFixture
make_metadata_hidden_corruption_fixture(
    const TemporaryDirectory& temporary,
    std::size_t ordinal) {
    const std::string suffix = fixed_width_decimal(ordinal);
    MetadataHiddenCorruptionFixture fixture;
    fixture.root = temporary.make_store_root(
        "allocation-alarm-cutpoint-" + suffix);
    fixture.folder = "folder-allocation-alarm-cutpoint-" + suffix;
    const std::string good_payload =
        "allocation-alarm-cutpoint-good-payload";
    const std::string corrupt_payload(good_payload.size(), 'X');
    fixture.expected_digest = anonsync::sha256_hex(good_payload);
    fixture.observed_digest = anonsync::sha256_hex(corrupt_payload);
    fixture.max_payload_bytes = 4096U;
    fixture.limits.max_entries = 8U;
    fixture.limits.max_payload_bytes = fixture.max_payload_bytes;
    fixture.limits.max_indexed_bytes = 16384U;
    fixture.limits.max_transient_entries = 8U;
    fixture.limits.max_transient_bytes = 1024U * 1024U;
    fixture.limits.max_scrub_bytes_per_attempt = 4096U;
    fixture.limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            fixture.folder, fixture.root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            fixture.limits, "allocation-alarm publisher");
        require(
            publisher.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "allocation-alarm fixture did not publish its payload");
    }

    const fs::path verification_index_path =
        fixture.root /
        std::string(
            anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path),
            fixture.limits.max_entries, fixture.limits.max_indexed_bytes,
            "allocation-alarm verification-index fixture");
    require(
        forged_index.entries.size() == 1U &&
            forged_index.entries.front().content_sha256 ==
                fixture.expected_digest,
        "allocation-alarm fixture lacks one exact restart record");
    const fs::path payload_path = fixture.root / fixture.expected_digest;
    overwrite_private_file(payload_path, corrupt_payload);
    forged_index.entries.front().metadata = private_file_metadata(
        payload_path, "allocation-alarm forged payload metadata");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, fixture.limits.max_entries,
                fixture.limits.max_indexed_bytes,
                "allocation-alarm forged verification index"));
    return fixture;
}

[[nodiscard]] bool durable_scrub_failure_present(
    const MetadataHiddenCorruptionFixture& fixture) {
    const fs::path state_path =
        fixture.root /
        std::string(anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    if (!fs::exists(state_path)) return false;
    const auto state = read_scrub_state_or_fail(
        fixture.root, fixture.max_payload_bytes,
        "allocation-alarm scrub state");
    return state.disposition ==
           anonsync::SyncReplicaFilePayloadScrubStateDisposition::
               IntegrityFailure;
}

[[nodiscard]] fs::path terminal_verification_path(
    const fs::path& root,
    std::string_view content_sha256) {
    return root /
           (std::string(
                anonsync::
                    kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix) +
            std::string(content_sha256));
}

[[nodiscard]] anonsync::SyncReplicaFilePayloadTerminalVerificationJournal
read_terminal_verification_journal_or_fail(
    const fs::path& root,
    std::string_view content_sha256,
    std::uint64_t max_payload_bytes,
    const std::string& label) {
    const fs::path path = terminal_verification_path(root, content_sha256);
    require(
        anonsync::
            sync_replica_file_payload_store_terminal_verification_basename_is_exact(
                path.filename().string()),
        label + " terminal verification basename was not canonical");
    return anonsync::
        parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
            read_file_bytes(path), max_payload_bytes, label);
}


[[nodiscard]] std::optional<fs::path>
single_staged_prefix_if_present_or_fail(const fs::path& root) {
    std::optional<fs::path> found;
    for (const fs::directory_entry& entry : fs::directory_iterator(root)) {
        if (!anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                entry.path().filename().string())) {
            continue;
        }
        if (found.has_value()) {
            fail("observed competing staged prefix files");
        }
        found = entry.path();
    }
    return found;
}

[[nodiscard]] fs::path single_staged_prefix_or_fail(
    const fs::path& root,
    std::string_view label) {
    std::optional<fs::path> found;
    for (const fs::directory_entry& entry : fs::directory_iterator(root)) {
        const std::string basename = entry.path().filename().string();
        if (!anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                basename)) {
            continue;
        }
        if (found.has_value()) {
            fail(std::string(label) + " observed competing staged prefix files");
        }
        found = entry.path();
    }
    if (!found.has_value()) {
        fail(std::string(label) + " did not find a staged prefix file");
    }
    return *found;
}

void append_uncommitted_prefix_tail_or_fail(
    const fs::path& path,
    std::uint64_t offset_bytes,
    std::string_view bytes) {
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) fail("could not open staged prefix crash-tail fixture");

    std::size_t written = 0U;
    while (written < bytes.size()) {
        ssize_t count;
        do {
            count = ::pwrite(
                descriptor, bytes.data() + written, bytes.size() - written,
                static_cast<off_t>(offset_bytes + written));
        } while (count < 0 && errno == EINTR);
        if (count <= 0) {
            (void)::close(descriptor);
            fail("could not write staged prefix crash-tail fixture");
        }
        written += static_cast<std::size_t>(count);
    }
    int sync_result;
    do {
        sync_result = ::fsync(descriptor);
    } while (sync_result != 0 && errno == EINTR);
    if (sync_result != 0 || ::close(descriptor) != 0) {
        fail("could not synchronize staged prefix crash-tail fixture");
    }
}

anonsync::SyncReplicaOperation file_operation(
    std::string_view folder,
    std::string_view payload) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = std::string(folder);
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(payload.size());
    operation.content_sha256 = anonsync::sha256_hex(std::string(payload));
    return operation;
}

void test_descriptor_streaming_publication_and_selection() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("descriptor-streaming");
    const fs::path source_path = temporary.path() / "descriptor-source.bin";
    const std::string folder = "folder-descriptor-streaming-payload";
    const std::string payload("descriptor\0streaming\0payload", 28U);
    write_private_file(source_path, payload);

    int source_descriptor;
    do {
        source_descriptor =
            ::open(source_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (source_descriptor < 0 && errno == EINTR);
    if (source_descriptor < 0) {
        fail("could not open descriptor-streaming source fixture");
    }
    const auto close_source = [&]() noexcept {
        close_descriptor_noexcept(source_descriptor);
    };

    try {
        const auto source_metadata =
            anonsync::observe_sync_posix_regular_file_descriptor_or_throw(
                source_descriptor,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "descriptor-streaming source observation");
        const std::string digest = anonsync::sha256_hex(payload);
        if (::lseek(source_descriptor, 5, SEEK_SET) != 5) {
            fail("could not position descriptor-streaming source fixture");
        }
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "descriptor-streaming payload store");

        const auto inserted =
            store.put_payload_from_borrowed_descriptor_or_throw(
                source_descriptor, source_metadata, digest);
        require(
            inserted.disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
                inserted.content_sha256 == digest &&
                inserted.size_bytes == payload.size(),
            "descriptor publication did not retain exact payload identity");
        require(
            ::lseek(source_descriptor, 0, SEEK_CUR) == 5,
            "descriptor publication changed the caller file offset");

        anonsync::SyncReplicaOperation operation =
            file_operation(folder, payload);
        auto snapshot = store.snapshot_or_throw();
        {
            auto mutation_batch = store.begin_mutation_batch_or_throw();
            require_lease_busy(
                [&] {
                    (void)snapshot.open_payload_for_operation_or_throw(
                        operation,
                        "descriptor-streaming snapshot reader fence");
                },
                anonsync::SyncReplicaFilePayloadStoreLeaseMode::
                    SharedObservation,
                "a retained complete snapshot reopened payload bytes without the current store reader fence");
            require_lease_busy(
                [&] {
                    (void)snapshot.copy_payload_range_for_operation_or_throw(
                        operation, 0U, 4U,
                        "descriptor-streaming range reader fence");
                },
                anonsync::SyncReplicaFilePayloadStoreLeaseMode::
                    SharedObservation,
                "a retained complete snapshot copied a payload range without the current store reader fence");
        }
        int payload_use_probe = -1;
        {
            auto selected = snapshot.open_payload_for_operation_or_throw(
                operation, "descriptor-streaming selected payload");
            require(
                selected.active() && selected.content_sha256() == digest &&
                    selected.size_bytes() == payload.size(),
                "descriptor selection did not return the exact durable payload");
            if (::lseek(selected.borrowed_descriptor(), 3, SEEK_SET) != 3) {
                fail("could not position selected descriptor before bounded reads");
            }
            const auto selected_range = selected.copy_range_or_throw(
                5U, 7U, "descriptor-streaming selected range");
            require(
                selected_range.content_sha256 == digest &&
                    selected_range.total_size_bytes == payload.size() &&
                    selected_range.offset_bytes == 5U &&
                    selected_range.bytes == payload.substr(5U, 7U) &&
                    selected_range.chunk_sha256 ==
                        anonsync::sha256_hex(payload.substr(5U, 7U)) &&
                    ::lseek(selected.borrowed_descriptor(), 0, SEEK_CUR) == 3,
                "opened payload range copy did not preserve exact bytes, digest, extent, and descriptor position");
            std::string direct_range(7U, '\0');
            const std::string direct_range_sha256 =
                selected.copy_exact_range_into_or_throw(
                    5U, std::span<char>(direct_range.data(), direct_range.size()),
                    "descriptor-streaming direct selected range");
            require(
                direct_range == payload.substr(5U, 7U) &&
                    direct_range_sha256 ==
                        anonsync::sha256_hex(payload.substr(5U, 7U)) &&
                    ::lseek(selected.borrowed_descriptor(), 0, SEEK_CUR) == 3,
                "opened payload direct range fill did not preserve exact bytes, digest, and descriptor position");
            require_error(
                [&] {
                    std::string oversized(payload.size() + 1U, '\0');
                    (void)selected.copy_exact_range_into_or_throw(
                        0U, std::span<char>(oversized.data(), oversized.size()),
                        "descriptor-streaming oversized direct range");
                },
                "does not name retained payload bytes",
                "opened payload direct range fill accepted an oversized destination");
            const auto content_defined =
                selected.content_defined_manifest_or_throw(
                    {4U, 8U, 16U, 16U},
                    "descriptor-streaming content-defined projection");
            std::uint64_t projected_bytes = 0U;
            for (const auto& chunk : content_defined.chunks) {
                projected_bytes += chunk.size_bytes;
                require(
                    anonsync::is_lowercase_sha256_hex(
                        chunk.sha256.lowercase_hex()),
                    "content-defined projection emitted an invalid chunk digest");
                require(
                    chunk.size_bytes <= 16U,
                    "content-defined projection exceeded its maximum chunk size");
            }
            require(
                content_defined.content_sha256 == digest &&
                    content_defined.total_size_bytes == payload.size() &&
                    content_defined.parameters ==
                        anonsync::SyncReplicaContentDefinedChunkingParameters{
                            4U, 8U, 16U, 16U} &&
                    projected_bytes == payload.size() &&
                    !content_defined.chunks.empty() &&
                    ::lseek(selected.borrowed_descriptor(), 0, SEEK_CUR) == 3,
                "opened payload content-defined projection was not exact and position-independent");

            anonsync::SyncReplicaFilePayloadStoreContentDefinedProjection
                bounded_projection;
            require(
                !bounded_projection.active(),
                "fresh bounded content-defined projection was unexpectedly active");
            require_error(
                [&] {
                    (void)selected
                        .advance_content_defined_projection_or_throw(
                            bounded_projection, {4U, 8U, 16U, 16U}, 0U,
                            "descriptor-streaming zero-budget projection");
                },
                "step budget must be positive",
                "bounded content-defined projection accepted a zero-byte step budget");
            std::optional<
                anonsync::SyncReplicaFilePayloadStoreContentDefinedManifest>
                bounded_manifest;
            std::uint64_t bounded_hashed_bytes = 0U;
            std::uint64_t bounded_completed_chunks = 0U;
            std::uint64_t bounded_steps = 0U;
            while (!bounded_manifest.has_value()) {
                auto projection_source =
                    snapshot.open_payload_for_operation_or_throw(
                        operation,
                        "descriptor-streaming bounded projection reopen");
                auto step = projection_source
                    .advance_content_defined_projection_or_throw(
                        bounded_projection, {4U, 8U, 16U, 16U}, 5U,
                        "descriptor-streaming bounded content-defined projection");
                ++bounded_steps;
                bounded_hashed_bytes += step.hashed_bytes;
                bounded_completed_chunks += step.newly_completed_chunk_count;
                require(
                    projection_source.metadata() == selected.metadata() &&
                        step.hashed_bytes > 0U && step.hashed_bytes <= 5U,
                    "bounded content-defined projection exceeded its exact step byte frontier or changed source observation");
                if (step.completed_manifest.has_value()) {
                    bounded_manifest = std::move(*step.completed_manifest);
                    require(
                        !bounded_projection.active() &&
                            bounded_completed_chunks ==
                                bounded_manifest->chunks.size(),
                        "completed bounded content-defined projection retained process progress or lost chunk accounting");
                } else {
                    require(
                        bounded_projection.active() &&
                            bounded_projection.content_sha256() == digest &&
                            bounded_projection.total_size_bytes() ==
                                payload.size() &&
                            bounded_projection.next_offset_bytes() ==
                                bounded_hashed_bytes &&
                            bounded_projection.completed_chunk_bytes() <=
                                bounded_hashed_bytes &&
                            bounded_projection.completed_chunks().size() ==
                                bounded_completed_chunks &&
                            bounded_projection.metadata() ==
                                projection_source.metadata() &&
                            bounded_projection.parameters() ==
                                anonsync::SyncReplicaContentDefinedChunkingParameters{
                                    4U, 8U, 16U, 16U},
                        "bounded content-defined projection did not retain one exact process-local continuation");
                }
            }
            require(
                bounded_steps > 1U && bounded_hashed_bytes == payload.size() &&
                    *bounded_manifest == content_defined &&
                    ::lseek(selected.borrowed_descriptor(), 0, SEEK_CUR) == 3,
                "bounded content-defined projection did not reproduce the complete canonical manifest across independent descriptor reopens");

            anonsync::SyncReplicaFilePayloadStoreContentDefinedProjection
                stale_parameter_projection;
            const auto initial_stale_parameter_step =
                selected.advance_content_defined_projection_or_throw(
                    stale_parameter_projection, {4U, 8U, 16U, 16U}, 5U,
                    "descriptor-streaming stale-parameter projection start");
            require(
                initial_stale_parameter_step.hashed_bytes == 5U &&
                    stale_parameter_projection.active(),
                "bounded projection stale-parameter fixture did not retain initial progress");
            require_error(
                [&] {
                    (void)selected
                        .advance_content_defined_projection_or_throw(
                            stale_parameter_projection, {4U, 8U, 16U, 15U},
                            5U,
                            "descriptor-streaming stale-parameter projection resume");
                },
                "does not bind this exact payload observation",
                "bounded projection resumed through changed chunking parameters");
            require(
                !stale_parameter_projection.active(),
                "bounded projection retained ambiguous progress after a parameter mismatch");
            require_error(
                [&] {
                    (void)selected.content_defined_manifest_or_throw(
                        {4U, 8U, 16U, 1U},
                        "descriptor-streaming undersized content-defined frontier");
                },
                "exceeds its chunk-count frontier",
                "opened payload content-defined projection exceeded its caller-bound count");
            std::string selected_bytes(payload.size(), '\0');
            std::size_t selected_offset = 0U;
            while (selected_offset < selected_bytes.size()) {
                ssize_t selected_count;
                do {
                    selected_count = ::pread(
                        selected.borrowed_descriptor(),
                        selected_bytes.data() + selected_offset,
                        selected_bytes.size() - selected_offset,
                        static_cast<off_t>(selected_offset));
                } while (selected_count < 0 && errno == EINTR);
                if (selected_count <= 0) {
                    fail("selected descriptor ended before exact durable bytes");
                }
                selected_offset += static_cast<std::size_t>(selected_count);
            }
            require(selected_bytes == payload,
                    "selected descriptor did not expose exact durable bytes");

            do {
                payload_use_probe = ::open(
                    (root / digest).c_str(),
                    O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
            } while (payload_use_probe < 0 && errno == EINTR);
            if (payload_use_probe < 0) {
                fail("could not open independent payload-use lease probe");
            }
            int exclusive_result;
            do {
                exclusive_result = ::flock(
                    payload_use_probe, LOCK_EX | LOCK_NB);
            } while (exclusive_result != 0 && errno == EINTR);
            const int busy_error = errno;
            require(
                exclusive_result != 0 &&
                    (busy_error == EWOULDBLOCK || busy_error == EAGAIN),
                "a returned payload descriptor did not retain its shared exact-inode use lease");
        }
        int exclusive_result;
        do {
            exclusive_result = ::flock(
                payload_use_probe, LOCK_EX | LOCK_NB);
        } while (exclusive_result != 0 && errno == EINTR);
        require(
            exclusive_result == 0,
            "closing the returned payload descriptor did not release its exact-inode use lease");
        if (exclusive_result == 0) {
            (void)::flock(payload_use_probe, LOCK_UN);
        }
        close_descriptor_noexcept(payload_use_probe);

        const auto duplicate =
            store.put_payload_from_borrowed_descriptor_or_throw(
                source_descriptor, source_metadata, digest);
        require(
            duplicate.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
            "descriptor duplicate publication did not report already present");
        require(
            ::lseek(source_descriptor, 0, SEEK_CUR) == 5,
            "descriptor duplicate publication changed the caller file offset");

        const char suffix = '!';
        int mutation_descriptor;
        do {
            mutation_descriptor = ::open(
                source_path.c_str(), O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
        } while (mutation_descriptor < 0 && errno == EINTR);
        if (mutation_descriptor < 0) {
            fail("could not open descriptor-streaming mutation fixture");
        }
        ssize_t appended;
        do {
            appended = ::pwrite(
                mutation_descriptor, &suffix, 1U,
                static_cast<off_t>(payload.size()));
        } while (appended < 0 && errno == EINTR);
        const int mutation_close = ::close(mutation_descriptor);
        require(appended == 1 && mutation_close == 0,
                "could not mutate descriptor-streaming source fixture");
        require_error(
            [&] {
                (void)store.put_payload_from_borrowed_descriptor_or_throw(
                    source_descriptor, source_metadata, digest);
            },
            "changed after observation",
            "descriptor publication accepted a source changed after observation");
    } catch (...) {
        close_source();
        throw;
    }
    close_source();
}

void test_mutation_batch_amortizes_store_scan_and_releases_authority() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("mutation-batch");
    const fs::path source_path = temporary.path() / "mutation-batch-source.bin";
    const std::string folder = "folder-payload-mutation-batch";
    const std::string alpha("batch-alpha\0payload", 19U);
    const std::string beta("batch-beta\0descriptor", 21U);
    write_private_file(source_path, beta);

    int source_descriptor;
    do {
        source_descriptor =
            ::open(source_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (source_descriptor < 0 && errno == EINTR);
    if (source_descriptor < 0) {
        fail("could not open mutation-batch source fixture");
    }
    const auto close_source = [&]() noexcept {
        close_descriptor_noexcept(source_descriptor);
    };

    try {
        const auto source_metadata =
            anonsync::observe_sync_posix_regular_file_descriptor_or_throw(
                source_descriptor,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "mutation-batch source observation");
        const std::string beta_digest = anonsync::sha256_hex(beta);
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "mutation-batch payload store");

        anonsync::SyncReplicaFilePayloadStoreMutationBatch inactive;
        require(!inactive.active(),
                "default payload mutation batch unexpectedly retained authority");
        require_error(
            [&] { (void)inactive.full_scan_count(); }, "inactive",
            "inactive payload mutation batch exposed scan accounting");
        require_error(
            [&] { (void)inactive.scan_hashed_entry_count(); }, "inactive",
            "inactive payload mutation batch exposed hashed-entry accounting");
        require_error(
            [&] { (void)inactive.scan_hashed_bytes(); }, "inactive",
            "inactive payload mutation batch exposed hashed-byte accounting");
        require_error(
            [&] { (void)inactive.scan_reused_entry_count(); }, "inactive",
            "inactive payload mutation batch exposed reused-entry accounting");
        require_error(
            [&] { (void)inactive.scan_reused_bytes(); }, "inactive",
            "inactive payload mutation batch exposed reused-byte accounting");
        require_error(
            [&] { (void)inactive.scan_process_reused_entry_count(); },
            "inactive",
            "inactive payload mutation batch exposed process-reused entry accounting");
        require_error(
            [&] { (void)inactive.scan_process_reused_bytes(); }, "inactive",
            "inactive payload mutation batch exposed process-reused byte accounting");
        require_error(
            [&] { (void)inactive.scan_durable_reused_entry_count(); },
            "inactive",
            "inactive payload mutation batch exposed durable-reused entry accounting");
        require_error(
            [&] { (void)inactive.scan_durable_reused_bytes(); }, "inactive",
            "inactive payload mutation batch exposed durable-reused byte accounting");
        require_error(
            [&] { (void)inactive.source_bytes(); }, "inactive",
            "inactive payload mutation batch exposed source-byte accounting");

        {
            auto batch = store.begin_mutation_batch_or_throw();
            require(
                batch.active() && batch.full_scan_count() == 1U &&
                    batch.scan_hashed_entry_count() == 0U &&
                    batch.scan_hashed_bytes() == 0U &&
                    batch.scan_reused_entry_count() == 0U &&
                    batch.scan_reused_bytes() == 0U &&
                    batch.put_count() == 0U && batch.source_bytes() == 0U &&
                    batch.inserted_count() == 0U &&
                    batch.already_present_count() == 0U &&
                    batch.indexed_entry_count() == 0U &&
                    batch.indexed_bytes() == 0U,
                "new payload mutation batch did not freeze one empty-store scan");
            require_reuse_partition(
                batch, 0U, 0U, 0U, 0U,
                "empty payload mutation batch did not report an empty reuse partition");

            const auto alpha_insert = batch.put_payload_or_throw(alpha);
            const auto beta_insert =
                batch.put_payload_from_borrowed_descriptor_or_throw(
                    source_descriptor, source_metadata, beta_digest);
            const auto alpha_duplicate = batch.put_payload_or_throw(alpha);
            require(
                alpha_insert.disposition ==
                        anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
                    beta_insert.disposition ==
                        anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
                    alpha_duplicate.disposition ==
                        anonsync::SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent,
                "payload mutation batch lost exact inserted/duplicate dispositions");
            require(
                batch.full_scan_count() == 1U && batch.put_count() == 3U &&
                    batch.scan_hashed_entry_count() == 0U &&
                    batch.scan_hashed_bytes() == 0U &&
                    batch.scan_reused_entry_count() == 0U &&
                    batch.scan_reused_bytes() == 0U &&
                    batch.source_bytes() ==
                        alpha.size() + beta.size() + alpha.size() &&
                    batch.inserted_count() == 2U &&
                    batch.already_present_count() == 1U &&
                    batch.indexed_entry_count() == 2U &&
                    batch.indexed_bytes() == alpha.size() + beta.size(),
                "payload mutation batch rescanned or miscounted sequential puts");
            batch.preflight_or_throw("mutation-batch retained cutpoint");

            require_lease_busy(
                [&] { (void)store.snapshot_or_throw(); },
                anonsync::SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
                "live payload mutation batch allowed a nested shared snapshot");
            require_lease_busy(
                [&] { (void)store.put_payload_or_throw("competing-payload"); },
                anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
                "live payload mutation batch allowed a competing mutation");

            auto moved = std::move(batch);
            require(moved.active() && !batch.active(),
                    "payload mutation batch move did not transfer lease authority");
            moved.preflight_or_throw("moved payload mutation batch proof");
            require(
                moved.full_scan_count() == 1U && moved.put_count() == 3U &&
                    moved.scan_hashed_entry_count() == 0U &&
                    moved.scan_hashed_bytes() == 0U &&
                    moved.scan_reused_entry_count() == 0U &&
                    moved.scan_reused_bytes() == 0U &&
                    moved.source_bytes() ==
                        alpha.size() + beta.size() + alpha.size() &&
                    moved.indexed_entry_count() == 2U,
                "payload mutation batch move lost exact in-memory index state");
        }

        const auto snapshot = store.snapshot_or_throw();
        require(
            snapshot.entry_count() == 2U &&
                snapshot.indexed_bytes() == alpha.size() + beta.size() &&
                snapshot.scan_hashed_entry_count() == 0U &&
                snapshot.scan_hashed_bytes() == 0U &&
                snapshot.scan_reused_entry_count() == 2U &&
                snapshot.scan_reused_bytes() == alpha.size() + beta.size() &&
                snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, alpha)) == alpha &&
                snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, beta)) == beta,
            "released payload mutation batch did not publish its exact verified index for immediate warm reuse");
        require_reuse_partition(
            snapshot, 2U, alpha.size() + beta.size(), 0U, 0U,
            "immediate warm snapshot did not attribute reuse to the process-local generation");
    } catch (...) {
        close_source();
        throw;
    }
    close_source();
}

void test_payload_availability_generation_tracks_durable_insertions() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("payload-availability-generation");
    anonsync::SyncReplicaFilePayloadStore store(
        "folder-payload-availability-generation", root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "payload availability generation store");

    auto generation = [&]() {
        return anonsync::SyncReplicaFilePayloadStoreTestAccess::
            payload_availability_generation_or_throw(
                store, "payload availability generation test");
    };
    require(
        generation() == std::optional<std::uint64_t>{0U},
        "fresh payload store did not begin at availability generation zero");

    const std::string alpha = "availability-alpha";
    const auto alpha_insert = store.put_payload_or_throw(alpha);
    require(
        alpha_insert.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
            generation() == std::optional<std::uint64_t>{1U},
        "durable payload insertion did not advance availability generation");
    const auto alpha_duplicate = store.put_payload_or_throw(alpha);
    require(
        alpha_duplicate.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::
                    AlreadyPresent &&
            generation() == std::optional<std::uint64_t>{1U},
        "already-present payload unexpectedly advanced availability generation");

    const std::string beta = "availability-beta";
    {
        auto batch = store.begin_mutation_batch_or_throw();
        require(
            batch.put_payload_or_throw(beta).disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
                generation() == std::optional<std::uint64_t>{2U},
            "batched durable insertion did not advance availability generation");
        require(
            batch.put_payload_or_throw(beta).disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::
                        AlreadyPresent &&
                generation() == std::optional<std::uint64_t>{2U},
            "batched duplicate unexpectedly advanced availability generation");
    }

    const std::string gamma = "availability-gamma";
    const auto completed = store.stage_payload_prefix_or_throw(
        anonsync::sha256_hex(gamma), gamma.size(), 0U,
        anonsync::sha256_hex(gamma), gamma);
    require(
        completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted &&
            generation() == std::optional<std::uint64_t>{3U},
        "completed range publication did not advance availability generation");
    const auto replay = store.stage_payload_prefix_or_throw(
        anonsync::sha256_hex(gamma), gamma.size(), 0U,
        anonsync::sha256_hex(gamma), gamma);
    require(
        replay.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedAlreadyPresent &&
            generation() == std::optional<std::uint64_t>{3U},
        "already-present completed range unexpectedly advanced availability generation");
}

void test_mutation_batch_reports_cold_scan_work_and_warms_owner() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("cold-batch-scan");
    const std::string folder = "folder-cold-payload-mutation-batch";
    const std::string retained_payload(
        8192U, 'c');

    {
        anonsync::SyncReplicaFilePayloadStore creator(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "cold mutation-batch creator");
        const auto inserted = creator.put_payload_or_throw(retained_payload);
        require(
            inserted.disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "cold mutation-batch fixture did not publish its retained payload");
    }

    anonsync::SyncReplicaFilePayloadStore reopened(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "cold mutation-batch reopened owner");
    {
        auto batch = reopened.begin_mutation_batch_or_throw();
        require(
            batch.full_scan_count() == 1U &&
                batch.scan_hashed_entry_count() == 0U &&
                batch.scan_hashed_bytes() == 0U &&
                batch.scan_reused_entry_count() == 1U &&
                batch.scan_reused_bytes() == retained_payload.size() &&
                batch.put_count() == 0U && batch.source_bytes() == 0U,
            "restarted payload mutation batch ignored exact durable verification acceleration");
        require_reuse_partition(
            batch, 0U, 0U, 1U, retained_payload.size(),
            "restarted payload mutation batch did not attribute reuse to the durable checkpoint");
    }

    const auto warmed = reopened.snapshot_or_throw();
    require(
        warmed.entry_count() == 1U &&
            warmed.scan_hashed_entry_count() == 0U &&
            warmed.scan_hashed_bytes() == 0U &&
            warmed.scan_reused_entry_count() == 1U &&
            warmed.scan_reused_bytes() == retained_payload.size(),
        "cold payload mutation batch did not publish its exact scan as warm owner state");
    require_reuse_partition(
        warmed, 1U, retained_payload.size(), 0U, 0U,
        "post-batch warm snapshot did not attribute reuse to process-local state");
}

#if defined(__linux__)
void test_complete_scan_restarts_one_stale_payload_observation() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("stale-complete-scan-restart");
    const std::string folder = "folder-stale-complete-scan-restart";
    // ReadOnlyInspect deliberately has no process or durable byte authority.
    // Keep enough remaining bytes after the first pread/IN_ACCESS event that
    // the writer can change and restore the first byte before the scanner's
    // descriptor and pathname cutpoints.
    const std::string payload(32U * 1024U * 1024U, 'q');
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path payload_path = root / digest;
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_payload_bytes = 64ULL * 1024ULL * 1024ULL;
    limits.max_indexed_bytes = 128ULL * 1024ULL * 1024ULL;
    limits.max_transient_bytes = 128ULL * 1024ULL * 1024ULL;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "stale complete-scan fixture publisher");
        const auto inserted = publisher.put_payload_or_throw(payload);
        require(
            inserted.disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::
                        Inserted &&
                fs::is_regular_file(payload_path),
            "stale complete-scan fixture did not publish one exact payload");
    }

    int notification_descriptor =
        ::inotify_init1(IN_CLOEXEC | IN_NONBLOCK);
    if (notification_descriptor < 0) {
        fail("stale complete-scan fixture could not create inotify owner");
    }
    const int watch_descriptor = ::inotify_add_watch(
        notification_descriptor, root.c_str(), IN_ACCESS);
    if (watch_descriptor < 0) {
        (void)::close(notification_descriptor);
        fail("stale complete-scan fixture could not watch its payload root");
    }

    std::string writer_error;
    bool writer_observed_payload_access = false;
    std::thread writer([&] {
        try {
            const auto deadline =
                std::chrono::steady_clock::now() +
                std::chrono::seconds(10);
            alignas(struct inotify_event) char events[4096];
            while (std::chrono::steady_clock::now() < deadline) {
                ssize_t count;
                do {
                    count = ::read(
                        notification_descriptor, events, sizeof(events));
                } while (count < 0 && errno == EINTR);
                if (count < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) {
                        std::this_thread::sleep_for(
                            std::chrono::milliseconds(1));
                        continue;
                    }
                    throw std::runtime_error(
                        "stale complete-scan inotify read failed");
                }

                std::size_t offset = 0U;
                while (offset < static_cast<std::size_t>(count)) {
                    const auto* event = reinterpret_cast<
                        const struct inotify_event*>(events + offset);
                    if ((event->mask & IN_ACCESS) != 0U &&
                        event->len != 0U && digest == event->name) {
                        writer_observed_payload_access = true;
                        int payload_descriptor;
                        do {
                            payload_descriptor = ::open(
                                payload_path.c_str(),
                                O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
                        } while (payload_descriptor < 0 && errno == EINTR);
                        if (payload_descriptor < 0) {
                            throw std::runtime_error(
                                "stale complete-scan payload open failed");
                        }

                        const char original = payload.front();
                        const char changed =
                            static_cast<char>(original ^ 0x5AU);
                        const auto write_byte_without_sync = [&](char value) {
                            ssize_t written;
                            do {
                                written = ::pwrite(
                                    payload_descriptor, &value, 1U, 0);
                            } while (written < 0 && errno == EINTR);
                            if (written != 1) {
                                throw std::runtime_error(
                                    "stale complete-scan payload write failed");
                            }
                        };
                        try {
                            // Keep the transient changed byte inside the first
                            // stale observation. Publishing it through a
                            // durability cutpoint would permit the retry to
                            // reject a genuinely current digest mismatch.
                            write_byte_without_sync(changed);
                            write_byte_without_sync(original);
                            int sync_result;
                            do {
                                sync_result = ::fsync(payload_descriptor);
                            } while (sync_result != 0 && errno == EINTR);
                            if (sync_result != 0) {
                                throw std::runtime_error(
                                    "stale complete-scan payload fsync failed");
                            }
                        } catch (...) {
                            (void)::close(payload_descriptor);
                            throw;
                        }
                        if (::close(payload_descriptor) != 0) {
                            throw std::runtime_error(
                                "stale complete-scan payload close failed");
                        }
                        return;
                    }
                    offset += sizeof(struct inotify_event) + event->len;
                }
            }
            throw std::runtime_error(
                "stale complete-scan payload access was not observed");
        } catch (const std::exception& error) {
            writer_error = error.what();
        }
    });

    try {
        anonsync::SyncReplicaFilePayloadStore inspector(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                ReadOnlyInspect,
            limits, "stale complete-scan read-only inspector");
        const auto snapshot = inspector.snapshot_or_throw();
        writer.join();
        (void)::inotify_rm_watch(
            notification_descriptor, watch_descriptor);
        (void)::close(notification_descriptor);
        require(
            writer_error.empty() && writer_observed_payload_access,
            "stale complete-scan writer did not cross the byte-read cutpoint: " +
                writer_error);
        require(
            snapshot.entry_count() == 1U &&
                snapshot.scan_hashed_entry_count() == 1U &&
                snapshot.scan_hashed_bytes() == payload.size() &&
                snapshot.scan_reused_entry_count() == 0U &&
                read_file_bytes(payload_path) == payload,
            "complete scan did not discard one stale observation and return "
            "fresh exact authority");
    } catch (...) {
        if (writer.joinable()) writer.join();
        (void)::inotify_rm_watch(
            notification_descriptor, watch_descriptor);
        (void)::close(notification_descriptor);
        throw;
    }
}
#endif

void test_foreign_thread_cannot_touch_owner_local_verification_cache() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("owner-local-warm-cache");
    const std::string folder = "folder-owner-local-warm-payload-cache";
    const std::string payload(64U * 1024U, 'o');

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "owner-local warm-cache payload store");
    {
        auto batch = store.begin_mutation_batch_or_throw();
        const auto inserted = batch.put_payload_or_throw(payload);
        require(
            inserted.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "owner-local warm-cache fixture lost exact publication");
    }
    const auto baseline = store.snapshot_or_throw();
    require(
        baseline.entry_count() == 1U &&
            baseline.scan_hashed_entry_count() == 0U &&
            baseline.scan_reused_entry_count() == 1U &&
            baseline.scan_reused_bytes() == payload.size(),
        "owner-local warm-cache baseline was not exact");
    require_reuse_partition(
        baseline, 1U, payload.size(), 0U, 0U,
        "owner-local warm-cache baseline reported the wrong reuse origin");

    std::string foreign_thread_reason;
    std::thread worker([&] {
        try {
            (void)store.snapshot_or_throw();
        } catch (const std::exception& error) {
            foreign_thread_reason = error.what();
        }
    });
    worker.join();
    require(
        foreign_thread_reason.find("originating thread") != std::string::npos,
        "foreign-thread payload snapshot reached owner-local cache authority");

    std::string foreign_status_reason;
    std::thread status_worker([&] {
        try {
            (void)store.scrub_status();
        } catch (const std::exception& error) {
            foreign_status_reason = error.what();
        }
    });
    status_worker.join();
    require(
        foreign_status_reason.find("originating thread") !=
            std::string::npos,
        "foreign-thread scrub status reached mutex-free owner state");

    std::string foreign_snapshot_reason;
    std::thread snapshot_worker([&] {
        try {
            (void)baseline.snapshot_digest();
        } catch (const std::exception& error) {
            foreign_snapshot_reason = error.what();
        }
    });
    snapshot_worker.join();
    require(
        foreign_snapshot_reason.find("originating thread") !=
            std::string::npos,
        "foreign-thread metadata-only snapshot method read the mutex-free "
        "revocation epoch");

    const auto owner_after_rejection = store.snapshot_or_throw();
    require(
        owner_after_rejection.snapshot_digest() == baseline.snapshot_digest() &&
            owner_after_rejection.scan_hashed_entry_count() == 0U &&
            owner_after_rejection.scan_reused_entry_count() == 1U,
        "foreign-thread rejection damaged the originating owner's warm cache");
    require_reuse_partition(
        owner_after_rejection, 1U, payload.size(), 0U, 0U,
        "foreign-thread rejection changed process-local reuse attribution");
}

void test_mutation_batch_safely_outlives_creator_store_handle() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("detached-mutation-batch");
    const std::string folder = "folder-detached-payload-mutation-batch";
    const std::string payload("detached-batch\0payload", 22U);

    anonsync::SyncReplicaFilePayloadStoreMutationBatch detached;
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "detached mutation-batch payload store");
        detached = store.begin_mutation_batch_or_throw();
        require(detached.active() && detached.full_scan_count() == 1U,
                "detached payload mutation batch did not acquire exact authority");
    }

    require(detached.active(),
            "destroying the creator store invalidated its live mutation batch");
    const auto inserted = detached.put_payload_or_throw(payload);
    require(
        inserted.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
            detached.put_count() == 1U &&
            detached.source_bytes() == payload.size() &&
            detached.inserted_count() == 1U &&
            detached.indexed_entry_count() == 1U &&
            detached.indexed_bytes() == payload.size(),
        "payload mutation batch lost safe ownership after creator destruction");
    detached.preflight_or_throw("detached mutation-batch final proof");
    detached = {};
    require(!detached.active(),
            "detached payload mutation batch did not release its authority");

    anonsync::SyncReplicaFilePayloadStore reopened(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "detached mutation-batch payload restart");
    const auto snapshot = reopened.snapshot_or_throw();
    require(
        snapshot.entry_count() == 1U &&
            snapshot.scan_hashed_entry_count() == 0U &&
            snapshot.scan_hashed_bytes() == 0U &&
            snapshot.scan_reused_entry_count() == 1U &&
            snapshot.scan_reused_bytes() == payload.size() &&
            snapshot.copy_payload_for_operation_or_throw(
                file_operation(folder, payload)) == payload,
        "detached payload mutation batch did not checkpoint exact restart acceleration");
}

void test_existing_only_requires_explicit_bootstrap_without_mutation() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-durable-payload-existing-only";
    const fs::path empty_root = temporary.make_store_root("existing-only-empty");

    anonsync::SyncReplicaFilePayloadStore observer(
        folder, empty_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "payload store existing-only observer");
    require_error(
        [&] { (void)observer.snapshot_or_throw(); },
        "requires explicit bootstrap",
        "existing-only observation minted an identity for an empty root");
    require(
        fs::directory_iterator(empty_root) == fs::directory_iterator(),
        "existing-only observation left an artifact in an empty root");
    require_error(
        [&] { (void)observer.put_payload_or_throw("must-not-publish"); },
        "requires explicit bootstrap",
        "existing-only mutation minted an identity for an empty root");
    require(
        fs::directory_iterator(empty_root) == fs::directory_iterator(),
        "existing-only mutation left an artifact in an empty root");

    const fs::path preseeded_root =
        temporary.make_store_root("existing-only-preseeded");
    const std::string payload = "unbound-preseeded-payload";
    const fs::path payload_path =
        preseeded_root / anonsync::sha256_hex(payload);
    write_private_file(payload_path, payload);
    anonsync::SyncReplicaFilePayloadStore unbound_observer(
        folder, preseeded_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "payload store existing-only unbound observer");
    require_error(
        [&] { (void)unbound_observer.snapshot_or_throw(); },
        "requires explicit bootstrap",
        "existing-only observation adopted preseeded bytes");
    require(
        fs::exists(payload_path) &&
            std::distance(fs::directory_iterator(preseeded_root),
                          fs::directory_iterator()) == 1,
        "existing-only observation changed the unbound preseeded namespace");

    anonsync::SyncReplicaFilePayloadStore bootstrap(
        folder, preseeded_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "payload store explicit bootstrap");
    const auto adopted = bootstrap.snapshot_or_throw();
    require(
        adopted.entry_count() == 1U &&
            adopted.copy_payload_for_operation_or_throw(
                file_operation(folder, payload)) == payload,
        "explicit bootstrap did not adopt exact preseeded payload bytes");

    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, preseeded_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "payload store post-bootstrap observer");
    require(
        restarted.snapshot_or_throw().snapshot_digest() ==
            adopted.snapshot_digest(),
        "existing-only restart did not accept the explicit folder binding");

    require_error(
        [&] {
            anonsync::SyncReplicaFilePayloadStore invalid(
                folder, empty_root,
                static_cast<
                    anonsync::SyncReplicaFilePayloadStoreOpenDisposition>(0U));
            (void)invalid;
        },
        "open disposition is invalid",
        "invalid payload-store open disposition entered authority");
}


void test_verification_cache_is_exact_and_durable_across_restart() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("verification-cache");
    const std::string folder = "folder-payload-verification-cache";
    const std::string first(2U * 1024U * 1024U + 31U, 'A');
    const std::string second(384U * 1024U + 17U, 'B');
    const std::string first_digest = anonsync::sha256_hex(first);
    const std::string second_digest = anonsync::sha256_hex(second);
    const std::uint64_t total_bytes =
        static_cast<std::uint64_t>(first.size() + second.size());

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4U * 1024U * 1024U;
    limits.max_indexed_bytes = 16U * 1024U * 1024U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 8U * 1024U * 1024U;

    {
        anonsync::SyncReplicaFilePayloadStore bootstrap(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "verification-cache bootstrap");
        require(
            bootstrap.put_payload_or_throw(first).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "verification-cache fixture did not publish its first payload");
        require(
            bootstrap.put_payload_or_throw(second).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "verification-cache fixture did not publish its second payload");
    }

    const fs::path verification_index =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    require(
        fs::is_regular_file(verification_index),
        "normal payload publication did not checkpoint restart verification metadata");
    require(
        fs::remove(verification_index),
        "could not remove verification index for upgrade-style cold-start proof");

    anonsync::SyncReplicaFilePayloadStore owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache retained owner");
    const auto cold = owner.snapshot_or_throw();
    const std::string canonical_snapshot_digest = cold.snapshot_digest();
    require(
        cold.entry_count() == 2U && cold.indexed_bytes() == total_bytes &&
            cold.scan_hashed_entry_count() == 2U &&
            cold.scan_hashed_bytes() == total_bytes &&
            cold.scan_reused_entry_count() == 0U &&
            cold.scan_reused_bytes() == 0U,
        "a fresh payload-store owner did not completely hash its cold snapshot");
    require_reuse_partition(
        cold, 0U, 0U, 0U, 0U,
        "cold payload-store snapshot reported invented reuse authority");

    require(
        fs::is_regular_file(verification_index),
        "successful cold snapshot did not best-effort checkpoint restart acceleration");

    const auto warm = owner.snapshot_or_throw();
    require(
        warm.snapshot_digest() == canonical_snapshot_digest &&
            warm.scan_hashed_entry_count() == 0U &&
            warm.scan_hashed_bytes() == 0U &&
            warm.scan_reused_entry_count() == 2U &&
            warm.scan_reused_bytes() == total_bytes,
        "an unchanged warm snapshot reread payload bytes or changed durable identity");
    require_reuse_partition(
        warm, 2U, total_bytes, 0U, 0U,
        "unchanged retained-owner snapshot did not attribute reuse to process-local state");

    const auto operator_recheck =
        owner.snapshot_rechecking_current_bytes_or_throw();
    require(
        operator_recheck.snapshot_digest() == canonical_snapshot_digest &&
            operator_recheck.entry_count() == 2U &&
            operator_recheck.indexed_bytes() == total_bytes &&
            operator_recheck.scan_hashed_entry_count() == 2U &&
            operator_recheck.scan_hashed_bytes() == total_bytes &&
            operator_recheck.scan_reused_entry_count() == 0U &&
            operator_recheck.scan_reused_bytes() == 0U,
        "operator recheck did not hash every current payload byte");
    require_reuse_partition(
        operator_recheck, 0U, 0U, 0U, 0U,
        "operator recheck reported prohibited verification reuse");
    const auto post_recheck_warm = owner.snapshot_or_throw();
    require(
        post_recheck_warm.scan_hashed_entry_count() == 0U &&
            post_recheck_warm.scan_reused_entry_count() == 2U &&
            post_recheck_warm.scan_reused_bytes() == total_bytes,
        "successful operator recheck did not publish exact immediate warm state");
    require_reuse_partition(
        post_recheck_warm, 2U, total_bytes, 0U, 0U,
        "post-recheck warm snapshot reported the wrong reuse origin");

    // Same-inode mutation is the harder metadata-cache frontier: identity and
    // extent remain stable while mtime/ctime change. It must fall through to a
    // complete hash, reject wrong bytes, and leave the prior cache intact.
    const auto original_identity = private_file_identity(root / first_digest);
    overwrite_private_file(root / first_digest, std::string(first.size(), 'C'));
    require(
        private_file_identity(root / first_digest) == original_identity,
        "the in-place verification-cache fixture unexpectedly changed inode");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "payload bytes do not match digest basename",
        "an in-place payload mutation escaped complete verification");
    overwrite_private_file(root / first_digest, first);
    require(
        private_file_identity(root / first_digest) == original_identity,
        "the in-place verification-cache repair unexpectedly changed inode");
    const auto repaired_in_place = owner.snapshot_or_throw();
    require(
        repaired_in_place.snapshot_digest() == canonical_snapshot_digest &&
            repaired_in_place.scan_hashed_entry_count() == 1U &&
            repaired_in_place.scan_hashed_bytes() == first.size() &&
            repaired_in_place.scan_reused_entry_count() == 1U &&
            repaired_in_place.scan_reused_bytes() == second.size(),
        "in-place repair did not isolate hashing to the changed observation");
    require_reuse_partition(
        repaired_in_place, 1U, second.size(), 0U, 0U,
        "in-place repair reported the unchanged process-local observation under the wrong origin");
    const auto repaired_in_place_warm = owner.snapshot_or_throw();
    require(
        repaired_in_place_warm.scan_hashed_entry_count() == 0U &&
            repaired_in_place_warm.scan_reused_entry_count() == 2U &&
            repaired_in_place_warm.scan_reused_bytes() == total_bytes,
        "an in-place repaired observation did not become reusable");

    // Atomic replacement must also invalidate reuse. The helper creates the
    // replacement while the original inode remains allocated, so this proof
    // cannot accidentally pass because remove-then-create reused an inode.
    const auto before_replacement = private_file_identity(root / first_digest);
    replace_private_file(root / first_digest, std::string(first.size(), 'D'));
    require(
        private_file_identity(root / first_digest) != before_replacement,
        "the atomic verification-cache replacement retained the old inode");
    require_error(
        [&] { (void)owner.snapshot_or_throw(); },
        "payload bytes do not match digest basename",
        "a replaced payload inode escaped complete verification");

    // A failed scan must not poison or broaden the cache. Restoring exact bytes
    // under another new inode hashes only that entry; the unchanged peer entry
    // remains safely reusable.
    replace_private_file(root / first_digest, first);
    const auto repaired = owner.snapshot_or_throw();
    require(
        repaired.snapshot_digest() == canonical_snapshot_digest &&
            repaired.scan_hashed_entry_count() == 1U &&
            repaired.scan_hashed_bytes() == first.size() &&
            repaired.scan_reused_entry_count() == 1U &&
            repaired.scan_reused_bytes() == second.size(),
        "replacement repair did not isolate hashing to the changed observation");
    const auto repaired_warm = owner.snapshot_or_throw();
    require(
        repaired_warm.scan_hashed_entry_count() == 0U &&
            repaired_warm.scan_reused_entry_count() == 2U &&
            repaired_warm.scan_reused_bytes() == total_bytes,
        "a repaired exact observation did not become reusable after verification");

    // Verification acceleration is also bound to the exact marker inode that
    // carried the cooperative lease. An identical marker replacement therefore
    // forces a cold content pass instead of crossing a split-lock boundary.
    replace_private_file(
        root / std::string(kStandaloneIdentityCurrent),
        "anonsync:sync-replica-file-payload-store-identity:v2\n" +
            folder + "\n" +
            "anonsync:sync-replica-file-payload-store-flock-lease:v1\n");
    const auto rebound_anchor = owner.snapshot_or_throw();
    require(
        rebound_anchor.snapshot_digest() == canonical_snapshot_digest &&
            rebound_anchor.scan_hashed_entry_count() == 2U &&
            rebound_anchor.scan_hashed_bytes() == total_bytes &&
            rebound_anchor.scan_reused_entry_count() == 0U,
        "an identical replacement lease marker retained stale verification acceleration");

    // A fresh cooperative owner may reuse only the checksum-sealed durable
    // observations bound to the exact current marker inode. It still enumerates
    // and re-proves every payload name; ReadOnlyInspect deliberately ignores the
    // acceleration record and always re-establishes content truth from bytes.
    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache restarted owner");
    const auto restart_warm = restarted.snapshot_or_throw();
    require(
        restart_warm.scan_hashed_entry_count() == 0U &&
            restart_warm.scan_hashed_bytes() == 0U &&
            restart_warm.scan_reused_entry_count() == 2U &&
            restart_warm.scan_reused_bytes() == total_bytes,
        "a restarted owner did not reuse exact marker-bound durable observations");
    require_reuse_partition(
        restart_warm, 0U, 0U, 2U, total_bytes,
        "restarted owner did not expose exact durable-checkpoint reuse");

    // Exact payload metadata remains the reuse fence across process restart. A
    // same-inode rewrite of identical bytes must hash only that changed record,
    // preserve reuse for its unchanged peer, and refresh the durable checkpoint.
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(root / first_digest, first);
    anonsync::SyncReplicaFilePayloadStore stale_metadata_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache stale-metadata owner");
    const auto stale_metadata = stale_metadata_owner.snapshot_or_throw();
    require(
        stale_metadata.scan_hashed_entry_count() == 1U &&
            stale_metadata.scan_hashed_bytes() == first.size() &&
            stale_metadata.scan_reused_entry_count() == 1U &&
            stale_metadata.scan_reused_bytes() == second.size(),
        "durable verification index reused a metadata-changed payload");
    require_reuse_partition(
        stale_metadata, 0U, 0U, 1U, second.size(),
        "metadata-change repair did not isolate durable reuse to the unchanged peer");
    anonsync::SyncReplicaFilePayloadStore refreshed_metadata_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache refreshed-metadata owner");
    const auto refreshed_metadata =
        refreshed_metadata_owner.snapshot_or_throw();
    require(
        refreshed_metadata.scan_hashed_entry_count() == 0U &&
            refreshed_metadata.scan_reused_entry_count() == 2U &&
            refreshed_metadata.scan_reused_bytes() == total_bytes,
        "metadata-change repair was not checkpointed for the next owner");
    require_reuse_partition(
        refreshed_metadata, 0U, 0U, 2U, total_bytes,
        "refreshed checkpoint reuse was not attributed to durable evidence");

    // Corrupt acceleration bytes are not namespace authority. They trigger a
    // complete byte proof and are conditionally replaced only after that proof.
    overwrite_private_file(verification_index, "malformed-index");
    anonsync::SyncReplicaFilePayloadStore malformed_index_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache malformed-index owner");
    const auto malformed_index = malformed_index_owner.snapshot_or_throw();
    require(
        malformed_index.scan_hashed_entry_count() == 2U &&
            malformed_index.scan_hashed_bytes() == total_bytes &&
            malformed_index.scan_reused_entry_count() == 0U,
        "malformed durable verification metadata granted payload reuse");
    require_reuse_partition(
        malformed_index, 0U, 0U, 0U, 0U,
        "malformed durable metadata leaked into reuse-origin diagnostics");
    anonsync::SyncReplicaFilePayloadStore repaired_index_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache repaired-index owner");
    const auto repaired_index = repaired_index_owner.snapshot_or_throw();
    require(
        repaired_index.scan_hashed_entry_count() == 0U &&
            repaired_index.scan_reused_entry_count() == 2U &&
            repaired_index.scan_reused_bytes() == total_bytes,
        "malformed durable verification metadata was not repaired after full proof");
    require_reuse_partition(
        repaired_index, 0U, 0U, 2U, total_bytes,
        "repaired verification index did not become durable restart evidence");

    // An oversized but otherwise private checkpoint is the same kind of
    // non-authoritative damage: do not allocate/read it, do not let it block
    // payload availability, and replace it only after hashing the full store.
    const std::uint64_t maximum_verification_index_bytes =
        anonsync::sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
            limits.max_entries, "verification-cache oversized fixture");
    overwrite_private_file(
        verification_index,
        std::string(
            static_cast<std::size_t>(maximum_verification_index_bytes + 1U),
            'X'));
    anonsync::SyncReplicaFilePayloadStore oversized_index_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache oversized-index owner");
    const auto oversized_index = oversized_index_owner.snapshot_or_throw();
    require(
        oversized_index.scan_hashed_entry_count() == 2U &&
            oversized_index.scan_hashed_bytes() == total_bytes &&
            oversized_index.scan_reused_entry_count() == 0U,
        "oversized durable verification metadata blocked or granted payload reuse");
    anonsync::SyncReplicaFilePayloadStore repaired_oversized_index_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache repaired-oversized-index owner");
    const auto repaired_oversized_index =
        repaired_oversized_index_owner.snapshot_or_throw();
    require(
        repaired_oversized_index.scan_hashed_entry_count() == 0U &&
            repaired_oversized_index.scan_reused_entry_count() == 2U &&
            repaired_oversized_index.scan_reused_bytes() == total_bytes,
        "oversized durable verification metadata was not repaired after full proof");

    anonsync::SyncReplicaFilePayloadStore inspector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        limits, "verification-cache forensic inspector");
    const auto first_inspection = inspector.snapshot_or_throw();
    const auto second_inspection = inspector.snapshot_or_throw();
    require(
        first_inspection.scan_hashed_entry_count() == 2U &&
            first_inspection.scan_hashed_bytes() == total_bytes &&
            first_inspection.scan_reused_entry_count() == 0U &&
            second_inspection.scan_hashed_entry_count() == 2U &&
            second_inspection.scan_hashed_bytes() == total_bytes &&
            second_inspection.scan_reused_entry_count() == 0U,
        "read-only forensic observation reused process-local verification state");
    require_reuse_partition(
        first_inspection, 0U, 0U, 0U, 0U,
        "first read-only inspection reported reuse acceleration");
    require_reuse_partition(
        second_inspection, 0U, 0U, 0U, 0U,
        "second read-only inspection reported reuse acceleration");
    require(
        first_inspection.snapshot_digest() == second_inspection.snapshot_digest() &&
            first_inspection.snapshot_digest() == canonical_snapshot_digest,
        "verification work accounting leaked into canonical snapshot identity");
    require(
        owner.snapshot_or_throw().payload_size_or_none(second_digest) ==
            std::optional<std::uint64_t>(second.size()),
        "warm verification cache changed exact digest lookup behavior");
}

void test_process_cache_reverification_refreshes_restart_checkpoint() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("verification-cache-recheckpoint");
    const std::string folder =
        "folder-payload-verification-cache-recheckpoint";
    const std::string payload(768U * 1024U + 29U, 'R');
    const std::string digest = anonsync::sha256_hex(payload);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 2U * 1024U * 1024U;
    limits.max_indexed_bytes = 4U * 1024U * 1024U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 4U * 1024U * 1024U;

    {
        anonsync::SyncReplicaFilePayloadStore bootstrap(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "verification-cache recheckpoint bootstrap");
        require(
            bootstrap.put_payload_or_throw(payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "verification-cache recheckpoint fixture did not publish its payload");
    }

    const fs::path verification_index =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    require(
        fs::is_regular_file(verification_index),
        "verification-cache recheckpoint fixture lacks durable restart metadata");

    anonsync::SyncReplicaFilePayloadStore owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache recheckpoint retained owner");
    const auto durable_warm = owner.snapshot_or_throw();
    require(
        durable_warm.scan_hashed_entry_count() == 0U &&
            durable_warm.scan_durable_reused_entry_count() == 1U &&
            durable_warm.scan_durable_reused_bytes() == payload.size(),
        "verification-cache recheckpoint baseline did not use durable evidence");

    // The payload remains byte-exact but its same-inode metadata observation
    // changes. The retained owner must hash it once and immediately checkpoint
    // the replacement observation; otherwise the next process repeats the same
    // full payload read even though this process already established the bytes.
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(root / digest, payload);
    const auto repaired = owner.snapshot_or_throw();
    require(
        repaired.scan_hashed_entry_count() == 1U &&
            repaired.scan_hashed_bytes() == payload.size() &&
            repaired.scan_reused_entry_count() == 0U,
        "same-process metadata repair did not perform one exact payload proof");

    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "verification-cache recheckpoint restarted owner");
    const auto restart_warm = restarted.snapshot_or_throw();
    require(
        restart_warm.scan_hashed_entry_count() == 0U &&
            restart_warm.scan_durable_reused_entry_count() == 1U &&
            restart_warm.scan_durable_reused_bytes() == payload.size(),
        "same-process exact repair was not checkpointed for the next owner");
}

void test_verification_checkpoint_skips_tight_transient_capacity() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("verification-checkpoint-tight-capacity");
    const std::string folder =
        "folder-payload-verification-checkpoint-tight-capacity";
    const std::string payload = "tiny";
    const fs::path verification_index =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 256U;
    limits.max_transient_entries = 8U;
    // Smaller than even an empty fixed-width v1 checkpoint, while remaining
    // sufficient for the payload writer. Restart acceleration must yield to the
    // shipping protocol's capacity contract rather than widening this fixture.
    limits.max_transient_bytes = 128U;

    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "verification-checkpoint tight-capacity publisher");
        require(
            store.put_payload_or_throw(payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "tight-capacity store did not publish its authoritative payload");
        require(
            !fs::exists(verification_index),
            "non-authoritative checkpoint consumed unavailable transient capacity");
    }
    require(
        !fs::exists(verification_index),
        "graceful close published a checkpoint beyond transient capacity");

    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "verification-checkpoint tight-capacity restart");
        const auto cold = restarted.snapshot_or_throw();
        require(
            cold.entry_count() == 1U &&
                cold.payload_size_or_none(anonsync::sha256_hex(payload)) ==
                    std::optional<std::uint64_t>(payload.size()) &&
                cold.scan_hashed_entry_count() == 1U &&
                cold.scan_hashed_bytes() == payload.size() &&
                cold.scan_reused_entry_count() == 0U,
            "checkpoint omission changed payload truth or claimed warm restart reuse");
        require(
            cold.verification_checkpoint_deferred_by_transient_capacity(),
            "tight-capacity scan did not retain its exact checkpoint deferral");

        const auto repeated = restarted.snapshot_or_throw();
        require(
            repeated.entry_count() == 1U &&
                repeated.scan_hashed_entry_count() == 0U &&
                repeated.scan_process_reused_entry_count() == 1U &&
                repeated.scan_durable_reused_entry_count() == 0U &&
                repeated.verification_checkpoint_deferred_by_transient_capacity(),
            "known-impossible checkpoint publication did not remain deferred on the warm snapshot");
    }
    require(
        !fs::exists(verification_index),
        "restart repair ignored the same tight transient-capacity fence");
}

void test_rotating_scrub_is_bounded_restart_safe_and_cyclic() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("rotating-scrub");
    const std::string folder = "folder-payload-rotating-scrub";
    const std::string payload(37U, 'S');
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 1024U;
    limits.max_indexed_bytes = 4096U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 10U;
    limits.max_scrub_entries_per_attempt = 1U;

    std::string canonical_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore owner(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "rotating scrub bootstrap");
        require(
            owner.put_payload_or_throw(payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "rotating scrub fixture did not publish its payload");
        const auto status_before_snapshot = owner.scrub_status();
        require(
            status_before_snapshot.enabled &&
                status_before_snapshot.max_bytes_per_attempt == 10U &&
                status_before_snapshot.max_entries_per_attempt == 1U &&
                !status_before_snapshot.last_report.has_value() &&
                !status_before_snapshot.last_report_age_milliseconds
                     .has_value() &&
                !status_before_snapshot
                     .last_completed_cycle_age_milliseconds.has_value(),
            "fresh owner scrub status invented process observation history");

        const auto first = owner.snapshot_or_throw();
        canonical_snapshot_digest = first.snapshot_digest();
        require(
            first.entry_count() == 1U &&
                first.transient_entry_count() == 0U &&
                first.transient_bytes() == 0U &&
                first.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        Advanced &&
                first.scrub_report().hashed_bytes == 10U &&
                first.scrub_report().touched_entry_count == 1U &&
                first.scrub_report().completed_entry_count == 0U &&
                !first.scrub_report().reverified_active_completed &&
                first.scrub_report().active_content_sha256 == digest &&
                first.scrub_report().active_offset_bytes == 10U,
            "first rotating scrub attempt exceeded or lost its exact bound");
        const auto first_status = owner.scrub_status();
        require(
            first_status.enabled &&
                first_status.last_report == first.scrub_report() &&
                first_status.last_report_age_milliseconds.has_value() &&
                !first_status.last_completed_cycle_age_milliseconds
                     .has_value(),
            "scrub status did not retain the exact process-observed report");
        const auto first_state = read_scrub_state_or_fail(
            root, limits.max_payload_bytes, "first rotating scrub state");
        require(
            first_state.disposition ==
                    anonsync::SyncReplicaFilePayloadScrubStateDisposition::
                        Progress &&
                first_state.active_content_sha256 == digest &&
                first_state.active_offset_bytes == 10U &&
                first_state.active_hash.total_bytes == 10U,
            "first rotating scrub progress was not durably resumable");

        const std::string state_before_throttle =
            read_file_bytes(scrub_state_path);
        const auto throttled = owner.snapshot_or_throw();
        require(
            throttled.snapshot_digest() == canonical_snapshot_digest &&
                throttled.scan_hashed_entry_count() == 0U &&
                throttled.scan_process_reused_entry_count() == 1U &&
                throttled.scan_durable_reused_entry_count() == 0U &&
                throttled.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        DeferredBySchedule &&
                !throttled.scrub_report().reverified_active_completed &&
                throttled.scrub_report().active_offset_bytes == 10U &&
                read_file_bytes(scrub_state_path) == state_before_throttle,
            "same-owner active-scrub witness did not preserve exact process-cache reuse");
        const auto throttled_status = owner.scrub_status();
        require(
            throttled_status.last_report == throttled.scrub_report() &&
                throttled_status.last_report_age_milliseconds.has_value() &&
                !throttled_status.last_completed_cycle_age_milliseconds
                     .has_value(),
            "scrub status did not advance to the process-local throttle report");
    }

    const auto settle_reverified_active =
        [&](std::uint64_t expected_cycles, const std::string& label) {
            anonsync::SyncReplicaFilePayloadStore restarted(
                folder, root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
                limits, label);
            const auto snapshot = restarted.snapshot_or_throw();
            require(
                snapshot.snapshot_digest() == canonical_snapshot_digest &&
                    snapshot.entry_count() == 1U &&
                    snapshot.transient_entry_count() == 0U &&
                    snapshot.scan_hashed_entry_count() == 1U &&
                    snapshot.scan_hashed_bytes() == payload.size() &&
                    snapshot.scan_durable_reused_entry_count() == 0U &&
                    snapshot.scan_process_reused_entry_count() == 0U &&
                    snapshot.scrub_report().disposition ==
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            Advanced &&
                    snapshot.scrub_report().hashed_bytes == 0U &&
                    snapshot.scrub_report().touched_entry_count == 0U &&
                    snapshot.scrub_report().completed_entry_count == 1U &&
                    snapshot.scrub_report().completed_cycles == expected_cycles &&
                    snapshot.scrub_report().reverified_active_completed &&
                    !snapshot.scrub_report().reverified_failure_cleared &&
                    snapshot.scrub_report().active_content_sha256.empty() &&
                    snapshot.scrub_report().active_offset_bytes == 0U,
                label +
                    " did not settle exact active progress from the stronger complete scan");
            const auto state = read_scrub_state_or_fail(
                root, limits.max_payload_bytes, label + " durable state");
            require(
                state.disposition ==
                        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Idle &&
                    state.cursor_after_content_sha256 == digest &&
                    state.completed_cycles == expected_cycles,
                label + " did not preserve the fair cursor after zero-read settlement");
        };

    const auto begin_next_cycle =
        [&](std::uint64_t expected_cycles, const std::string& label) {
            anonsync::SyncReplicaFilePayloadStore restarted(
                folder, root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
                limits, label);
            const auto snapshot = restarted.snapshot_or_throw();
            require(
                snapshot.snapshot_digest() == canonical_snapshot_digest &&
                    snapshot.entry_count() == 1U &&
                    snapshot.scan_hashed_entry_count() == 0U &&
                    snapshot.scan_durable_reused_entry_count() == 1U &&
                    snapshot.scan_process_reused_entry_count() == 0U &&
                    snapshot.scrub_report().disposition ==
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            Advanced &&
                    snapshot.scrub_report().hashed_bytes == 10U &&
                    snapshot.scrub_report().touched_entry_count == 1U &&
                    snapshot.scrub_report().completed_entry_count == 0U &&
                    snapshot.scrub_report().completed_cycles == expected_cycles &&
                    !snapshot.scrub_report().reverified_active_completed &&
                    snapshot.scrub_report().active_content_sha256 == digest &&
                    snapshot.scrub_report().active_offset_bytes == 10U,
                label + " did not begin the next fair bounded cycle");
        };

    settle_reverified_active(0U, "rotating scrub restart settlement");
    begin_next_cycle(1U, "rotating scrub next cycle");
    settle_reverified_active(1U, "rotating scrub second restart settlement");
    begin_next_cycle(2U, "rotating scrub third cycle");

    const std::string state_before_inspection = read_file_bytes(scrub_state_path);
    anonsync::SyncReplicaFilePayloadStore inspector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        limits, "rotating scrub forensic inspection");
    const auto inspection = inspector.snapshot_or_throw();
    const auto inspection_status = inspector.scrub_status();
    require(
        inspection.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::Disabled &&
            inspection.snapshot_digest() == canonical_snapshot_digest &&
            !inspection_status.enabled &&
            inspection_status.last_report == inspection.scrub_report() &&
            inspection_status.last_report_age_milliseconds.has_value() &&
            !inspection_status.last_completed_cycle_age_milliseconds
                 .has_value() &&
            read_file_bytes(scrub_state_path) == state_before_inspection,
        "read-only inspection misreported or advanced scrub scheduling evidence");
}

void test_scrub_state_damage_and_identity_rebind_are_disposable() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("scrub-state-damage");
    const std::string folder = "folder-payload-scrub-state-damage";
    const std::string payload(29U, 'D');
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 1024U;
    limits.max_indexed_bytes = 4096U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 7U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore bootstrap(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "scrub-state damage bootstrap");
        (void)bootstrap.put_payload_or_throw(payload);
        require(
            bootstrap.snapshot_or_throw()
                    .scrub_report()
                    .active_offset_bytes == 7U,
            "scrub-state damage fixture did not create partial progress");
    }

    overwrite_private_file(
        state_path,
        std::string(
            static_cast<std::size_t>(
                anonsync::sync_replica_file_payload_scrub_state_exact_bytes()),
            'X'));
    {
        anonsync::SyncReplicaFilePayloadStore repaired(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "checksum-damaged scrub-state repair");
        const auto snapshot = repaired.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.transient_entry_count() == 0U &&
                snapshot.scrub_report().state_rebuilt &&
                snapshot.scrub_report().hashed_bytes == 7U &&
                snapshot.scrub_report().active_content_sha256 == digest &&
                snapshot.scrub_report().active_offset_bytes == 7U,
            "checksum-damaged scrub state granted progress or blocked payload truth");
    }

    auto wrong_identity = read_scrub_state_or_fail(
        root, limits.max_payload_bytes, "identity-rebind scrub state fixture");
    wrong_identity.store_identity_sha256 =
        wrong_identity.store_identity_sha256 == std::string(64U, 'f')
            ? std::string(64U, 'e')
            : std::string(64U, 'f');
    overwrite_private_file(
        state_path,
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            wrong_identity, limits.max_payload_bytes,
            "identity-rebind scrub state encoding"));
    {
        anonsync::SyncReplicaFilePayloadStore rebound(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "identity-rebound scrub-state repair");
        const auto snapshot = rebound.snapshot_or_throw();
        require(
            snapshot.scrub_report().state_rebuilt &&
                snapshot.scrub_report().hashed_bytes == 7U &&
                snapshot.scrub_report().active_offset_bytes == 7U,
            "another store identity's scrub progress entered current scheduling authority");
    }

    overwrite_private_file(state_path, "torn");
    {
        anonsync::SyncReplicaFilePayloadStore torn(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "torn scrub-state repair");
        const auto snapshot = torn.snapshot_or_throw();
        require(
            snapshot.scrub_report().state_rebuilt &&
                snapshot.scrub_report().hashed_bytes == 7U &&
                snapshot.scrub_report().active_offset_bytes == 7U &&
                read_scrub_state_or_fail(
                    root, limits.max_payload_bytes,
                    "repaired torn scrub state")
                        .active_content_sha256 == digest,
            "torn scrub progress was not discarded and rebuilt exactly");
    }
}

void test_present_unusable_scrub_state_revokes_restart_acceleration() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("damaged-scrub-restart-fence");
    const std::string folder =
        "folder-payload-damaged-scrub-restart-fence";
    const std::string good_payload =
        "damaged-scrub-restart-fence-good-payload";
    const std::string corrupt_payload(good_payload.size(), 'Q');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest =
        anonsync::sha256_hex(corrupt_payload);
    const fs::path payload_path = root / expected_digest;
    const fs::path verification_index_path =
        root / std::string(
                   anonsync::
                       kSyncReplicaFilePayloadVerificationIndexBasename);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    // A one-byte optional scrub cannot discover this complete payload
    // mismatch. Detection must happen in the authority-producing namespace
    // scan because the damaged write-ahead record revoked restart reuse.
    limits.max_scrub_bytes_per_attempt = 1U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "damaged-scrub restart-fence publisher");
        require(
            publisher.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "damaged-scrub restart-fence fixture did not publish its payload");
        (void)publisher.snapshot_or_throw();
    }
    require(
        fs::is_regular_file(verification_index_path) &&
            fs::is_regular_file(scrub_state_path),
        "damaged-scrub restart-fence fixture lacks restart records");

    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path), limits.max_entries,
            limits.max_indexed_bytes,
            "damaged-scrub restart-fence verification index");
    require(
        forged_index.entries.size() == 1U &&
            forged_index.entries.front().content_sha256 == expected_digest,
        "damaged-scrub restart-fence fixture lacks one indexed payload");

    overwrite_private_file(payload_path, corrupt_payload);
    forged_index.entries.front().metadata = private_file_metadata(
        payload_path,
        "damaged-scrub restart-fence forged payload metadata");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, limits.max_entries, limits.max_indexed_bytes,
                "damaged-scrub restart-fence forged verification index"));

    const std::string damaged_state(
        static_cast<std::size_t>(
            anonsync::sync_replica_file_payload_scrub_state_exact_bytes()),
        'X');
    overwrite_private_file(scrub_state_path, damaged_state);

    {
        anonsync::SyncReplicaFilePayloadStore detector(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "damaged-scrub restart-fence detector");
        require_integrity_error(
            [&] { (void)detector.snapshot_or_throw(); }, expected_digest,
            observed_digest, false,
            "checksum-invalid scrub intent trusted forged restart metadata");
    }
    require(
        read_file_bytes(scrub_state_path) == damaged_state,
        "failed complete-byte reproof rewrote damaged scrub evidence");

    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(payload_path, good_payload);
    {
        anonsync::SyncReplicaFilePayloadStore repaired(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "damaged-scrub restart-fence repair");
        const auto snapshot = repaired.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.scan_hashed_entry_count() == 1U &&
                snapshot.scan_hashed_bytes() == good_payload.size() &&
                snapshot.scan_reused_entry_count() == 0U &&
                snapshot.scan_durable_reused_entry_count() == 0U &&
                snapshot.scrub_report().state_rebuilt &&
                snapshot.scrub_report().hashed_bytes == 1U &&
                snapshot.scrub_report().touched_entry_count == 1U &&
                snapshot.scrub_report().active_content_sha256 ==
                    expected_digest &&
                snapshot.scrub_report().active_offset_bytes == 1U &&
                snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, good_payload)) == good_payload,
            "repair did not reprove all bytes before rebuilding bounded scrub state");
    }
}

void test_disabled_scrub_settles_damaged_restart_fence_once() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("disabled-scrub-damaged-fence");
    const std::string folder =
        "folder-payload-disabled-scrub-damaged-fence";
    const std::string payload =
        "disabled scrub still settles restart intent";
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits enabled;
    enabled.max_entries = 8U;
    enabled.max_payload_bytes = 4096U;
    enabled.max_indexed_bytes = 16384U;
    enabled.max_transient_entries = 8U;
    enabled.max_transient_bytes = 1024U * 1024U;
    enabled.max_scrub_bytes_per_attempt = 1U;
    enabled.max_scrub_entries_per_attempt = 1U;
    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            enabled, "disabled-scrub damaged-fence publisher");
        require(
            publisher.put_payload_or_throw(payload).content_sha256 == digest,
            "disabled-scrub damaged-fence fixture did not publish payload");
        (void)publisher.snapshot_or_throw();
    }

    const std::string damaged_state(
        static_cast<std::size_t>(
            anonsync::sync_replica_file_payload_scrub_state_exact_bytes()),
        'Y');
    overwrite_private_file(state_path, damaged_state);

    auto disabled = enabled;
    disabled.max_scrub_bytes_per_attempt = 0U;
    disabled.max_scrub_entries_per_attempt = 0U;
    {
        anonsync::SyncReplicaFilePayloadStore repair(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            disabled, "disabled-scrub damaged-fence repair");
        const auto snapshot = repair.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.scan_hashed_entry_count() == 1U &&
                snapshot.scan_hashed_bytes() == payload.size() &&
                snapshot.scan_reused_entry_count() == 0U &&
                snapshot.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        Disabled &&
                snapshot.scrub_report().state_rebuilt &&
                snapshot.scrub_report().hashed_bytes == 0U &&
                snapshot.scrub_report().touched_entry_count == 0U,
            "disabled scrub did not settle damaged intent from the complete-byte proof");
    }
    const auto settled = read_scrub_state_or_fail(
        root, disabled.max_payload_bytes,
        "disabled-scrub settled restart fence");
    require(
        settled.disposition ==
                anonsync::SyncReplicaFilePayloadScrubStateDisposition::Idle &&
            settled.active_content_sha256.empty(),
        "disabled scrub did not publish canonical idle restart state");

    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            disabled, "disabled-scrub damaged-fence restart");
        const auto snapshot = restarted.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.scan_hashed_entry_count() == 0U &&
                snapshot.scan_durable_reused_entry_count() == 1U &&
                snapshot.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        Disabled &&
                !snapshot.scrub_report().state_rebuilt &&
                snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, payload)) == payload,
            "disabled scrub repeated the complete restart-fence reproof");
    }
}

void test_scrub_failure_is_reproved_persisted_and_repairable() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("scrub-integrity");
    const std::string folder = "folder-payload-scrub-integrity";
    const std::string good_payload = "scrub-integrity-good-payload";
    const std::string corrupt_payload(good_payload.size(), 'Z');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest = anonsync::sha256_hex(corrupt_payload);
    const fs::path payload_path = root / expected_digest;
    const fs::path verification_index_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 4096U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "scrub-integrity publisher");
        require(
            publisher.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "scrub-integrity fixture did not publish its good payload");
    }

    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path), limits.max_entries,
            limits.max_indexed_bytes,
            "scrub-integrity verification-index fixture");
    require(
        forged_index.entries.size() == 1U &&
            forged_index.entries.front().content_sha256 == expected_digest,
        "scrub-integrity fixture lacks one exact restart record");
    overwrite_private_file(payload_path, corrupt_payload);
    forged_index.entries.front().metadata = private_file_metadata(
        payload_path, "scrub-integrity forged payload metadata");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, limits.max_entries, limits.max_indexed_bytes,
                "scrub-integrity forged verification index"));

    {
        anonsync::SyncReplicaFilePayloadStore detector(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "scrub-integrity bounded detector");
        require_integrity_error(
            [&] { (void)detector.snapshot_or_throw(); }, expected_digest,
            observed_digest, true,
            "bounded scrub did not detect and persist metadata-hidden corruption");
    }
    const auto failure_state = read_scrub_state_or_fail(
        root, limits.max_payload_bytes, "persisted scrub failure");
    require(
        failure_state.disposition ==
                anonsync::SyncReplicaFilePayloadScrubStateDisposition::
                    IntegrityFailure &&
            failure_state.active_content_sha256 == expected_digest &&
            failure_state.active_offset_bytes == corrupt_payload.size() &&
            failure_state.observed_content_sha256 == observed_digest,
        "bounded scrub failure witness did not retain exact current evidence");

    {
        anonsync::SyncReplicaFilePayloadStore repeated(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "scrub-integrity repeated detector");
        require_integrity_error(
            [&] { (void)repeated.snapshot_or_throw(); }, expected_digest,
            observed_digest, true,
            "persisted failure witness granted warm-cache payload authority");
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(payload_path, good_payload);
    {
        anonsync::SyncReplicaFilePayloadStore repaired(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "scrub-integrity repaired payload");
        const auto snapshot = repaired.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.scan_hashed_entry_count() == 1U &&
                snapshot.scan_hashed_bytes() == good_payload.size() &&
                snapshot.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        Advanced &&
                snapshot.scrub_report().hashed_bytes == 0U &&
                snapshot.scrub_report().touched_entry_count == 0U &&
                snapshot.scrub_report().completed_entry_count == 1U &&
                snapshot.scrub_report().reverified_failure_cleared &&
                snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, good_payload)) == good_payload,
            "current full-byte repair proof was not reused to clear failure without a duplicate read");
    }
    const auto repaired_state = read_scrub_state_or_fail(
        root, limits.max_payload_bytes, "repaired scrub state");
    require(
        repaired_state.disposition ==
                anonsync::SyncReplicaFilePayloadScrubStateDisposition::Idle &&
            repaired_state.cursor_after_content_sha256 == expected_digest &&
            repaired_state.observed_content_sha256.empty(),
        "repaired payload did not durably clear stale failure evidence");
}

void test_live_capability_cutpoint_detects_complete_interval_aba() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("live-capability-interval-aba");
    const std::string folder = "folder-live-capability-interval-aba";

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "live-capability interval ABA");
    auto planner_snapshot = store.snapshot_or_throw();
    const auto before = anonsync::SyncReplicaFilePayloadStoreTestAccess::
        live_capability_cutpoint_excluding_snapshot_or_throw(
            store, planner_snapshot, "live-capability interval ABA before");

    {
        auto ephemeral_snapshot = store.snapshot_or_throw();
        require(
            ephemeral_snapshot.active(),
            "ephemeral same-process-store snapshot was not active");
    }

    const auto after = anonsync::SyncReplicaFilePayloadStoreTestAccess::
        live_capability_cutpoint_excluding_snapshot_or_throw(
            store, planner_snapshot, "live-capability interval ABA after");
    require(
        before.process_store_scope_digest ==
                after.process_store_scope_digest &&
            before.process_store_scope_incarnation_digest ==
                after.process_store_scope_incarnation_digest &&
            before.capability_set_digest == after.capability_set_digest &&
            before.snapshot_count == 0U && after.snapshot_count == 0U &&
            before.opened_payload_count == 0U &&
            after.opened_payload_count == 0U &&
            before.targeted_access_count == 0U &&
            after.targeted_access_count == 0U &&
            before.mutation_batch_count == 0U &&
            after.mutation_batch_count == 0U &&
            before.activity_generation < after.activity_generation &&
            before != after,
        "complete create-and-destroy capability interval aliased equal live cutpoints");
}

void test_live_capability_scope_spans_independent_store_owners() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("live-capability-cross-owner");
    const fs::path other_root =
        temporary.make_store_root("live-capability-other-store");
    const std::string folder = "folder-live-capability-cross-owner";

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore first(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "live-capability first independent owner");
    {
        auto bootstrap_snapshot = first.snapshot_or_throw();
        require(
            bootstrap_snapshot.active(),
            "first independent owner did not bootstrap the store identity");
    }
    anonsync::SyncReplicaFilePayloadStore second(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "live-capability second independent owner");
    auto planner_snapshot = second.snapshot_or_throw();
    const auto before = anonsync::SyncReplicaFilePayloadStoreTestAccess::
        live_capability_cutpoint_excluding_snapshot_or_throw(
            second, planner_snapshot,
            "live-capability cross-owner before");
    require(
        anonsync::is_lowercase_sha256_hex(
            before.process_store_scope_digest) &&
            anonsync::is_lowercase_sha256_hex(
                before.process_store_scope_incarnation_digest) &&
            before.snapshot_count == 0U,
        "independent-owner process-store scope began non-canonical");

    {
        auto first_owner_snapshot = first.snapshot_or_throw();
        const auto during = anonsync::SyncReplicaFilePayloadStoreTestAccess::
            live_capability_cutpoint_excluding_snapshot_or_throw(
                second, planner_snapshot,
                "live-capability cross-owner during");
        require(
            during.process_store_scope_digest ==
                    before.process_store_scope_digest &&
                during.process_store_scope_incarnation_digest ==
                    before.process_store_scope_incarnation_digest &&
                during.snapshot_count == 1U &&
                during.capability_set_digest !=
                    before.capability_set_digest &&
                during.activity_generation > before.activity_generation,
            "independently opened owner was invisible to the shared process-store scope");
        require_error(
            [&] {
                (void)anonsync::SyncReplicaFilePayloadStoreTestAccess::
                    live_capability_cutpoint_excluding_snapshot_or_throw(
                        second, first_owner_snapshot,
                        "live-capability foreign snapshot rejection");
            },
            "exact retained store owner",
            "shared live registry accidentally authorized foreign-owner snapshot handoff");
    }

    const auto after = anonsync::SyncReplicaFilePayloadStoreTestAccess::
        live_capability_cutpoint_excluding_snapshot_or_throw(
            second, planner_snapshot,
            "live-capability cross-owner after");
    require(
        after.process_store_scope_digest ==
                before.process_store_scope_digest &&
            after.process_store_scope_incarnation_digest ==
                before.process_store_scope_incarnation_digest &&
            after.capability_set_digest == before.capability_set_digest &&
            after.snapshot_count == 0U &&
            after.activity_generation > before.activity_generation,
        "released independent-owner capability did not restore the canonical set");

    anonsync::SyncReplicaFilePayloadStore other(
        folder, other_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "live-capability different process-store scope");
    auto other_planner_snapshot = other.snapshot_or_throw();
    const auto other_cutpoint =
        anonsync::SyncReplicaFilePayloadStoreTestAccess::
            live_capability_cutpoint_excluding_snapshot_or_throw(
                other, other_planner_snapshot,
                "live-capability different process-store cutpoint");
    require(
        other_cutpoint.process_store_scope_digest !=
                before.process_store_scope_digest &&
            other_cutpoint.process_store_scope_incarnation_digest !=
                before.process_store_scope_incarnation_digest,
        "distinct attested payload stores shared one process-store capability scope");
}

void test_live_capability_scope_recreates_after_final_owner_release() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("live-capability-scope-recreation");
    const std::string folder = "folder-live-capability-scope-recreation";

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    std::string scope_digest;
    std::string first_incarnation;
    {
        anonsync::SyncReplicaFilePayloadStore first(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "live-capability first scope incarnation");
        auto planner_snapshot = first.snapshot_or_throw();
        const auto cutpoint =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                live_capability_cutpoint_excluding_snapshot_or_throw(
                    first, planner_snapshot,
                    "live-capability first scope cutpoint");
        scope_digest = cutpoint.process_store_scope_digest;
        first_incarnation =
            cutpoint.process_store_scope_incarnation_digest;
    }

    anonsync::SyncReplicaFilePayloadStore recreated(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "live-capability recreated scope incarnation");
    auto recreated_snapshot = recreated.snapshot_or_throw();
    const auto recreated_cutpoint =
        anonsync::SyncReplicaFilePayloadStoreTestAccess::
            live_capability_cutpoint_excluding_snapshot_or_throw(
                recreated, recreated_snapshot,
                "live-capability recreated scope cutpoint");
    require(
        recreated_cutpoint.process_store_scope_digest == scope_digest,
        "recreated owner changed the deterministic process-store scope binding");
    require(
        recreated_cutpoint.process_store_scope_incarnation_digest !=
            first_incarnation,
        "process-store capability incarnation survived release of the final owner");
}

void test_writer_fenced_retention_snapshot_excludes_namespace_work_and_probes_inode_use() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("writer-fenced-retention-probe");
    const std::string folder = "folder-writer-fenced-retention-probe";
    const std::string payload =
        "writer-fenced-retention-probe-current-payload";
    const std::string other_payload =
        "writer-fenced-retention-probe-followup-payload";
    const std::string digest = anonsync::sha256_hex(payload);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore first(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "writer-fenced retention first owner");
    require(
        first.put_payload_or_throw(payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "writer-fenced retention fixture did not publish its payload");
    anonsync::SyncReplicaFilePayloadStore second(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "writer-fenced retention second owner");

    {
        const auto ordinary = first.snapshot_or_throw();
        require_error(
            [&] {
                (void)anonsync::SyncReplicaFilePayloadStoreTestAccess::
                    writer_fenced_payload_use_exclusive_available_or_throw(
                        first, ordinary, digest, payload.size(),
                        "ordinary snapshot rejection");
            },
            "does not retain the exact writer fence",
            "ordinary snapshot was accepted as writer-fenced retention authority");
    }

    ChildHeldFileLock cross_process_reader(
        root / digest, LOCK_SH, temporary.path(),
        "writer-fenced-retention-reader");
    {
        const auto writer_fenced =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                writer_fenced_retention_snapshot_or_throw(first);
        require(
            writer_fenced.payload_size_or_none(digest) ==
                std::optional<std::uint64_t>(payload.size()),
            "writer-fenced retention snapshot lost its exact payload");
        require(
            !anonsync::SyncReplicaFilePayloadStoreTestAccess::
                writer_fenced_payload_use_exclusive_available_or_throw(
                    first, writer_fenced, digest, payload.size(),
                    "cross-process reader probe"),
            "writer-fenced probe ignored a cross-process shared inode-use lease");
        require_lease_busy(
            [&] { (void)second.snapshot_or_throw(); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
            "writer-fenced retention snapshot admitted new namespace observation");
        require_lease_busy(
            [&] { (void)first.put_payload_or_throw(other_payload); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            "writer-fenced retention snapshot admitted concurrent namespace mutation");

        cross_process_reader.release_and_wait_or_fail();
        require(
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                writer_fenced_payload_use_exclusive_available_or_throw(
                    first, writer_fenced, digest, payload.size(),
                    "released reader probe"),
            "writer-fenced probe remained busy after the final reader released");
    }

    const auto after_fence = second.snapshot_or_throw();
    require(
        after_fence.payload_size_or_none(digest) ==
                std::optional<std::uint64_t>(payload.size()),
        "writer-fenced snapshot release did not restore namespace observation");
    require(
        first.put_payload_or_throw(other_payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "writer-fenced snapshot release did not restore namespace mutation");
}

void test_live_payload_descriptor_fences_quarantine_inode_mutation() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("payload-use-quarantine-fence");
    const std::string folder = "folder-payload-use-quarantine-fence";
    const std::string good_payload =
        "payload-use-lease-protects-open-descriptor-from-quarantine";
    const std::string corrupt_payload(good_payload.size(), 'X');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest = anonsync::sha256_hex(corrupt_payload);
    const fs::path payload_path = root / expected_digest;
    const fs::path quarantine_path =
        root /
        (std::string(".anonsync-payload-quarantine-v1-") +
         expected_digest + "-" + observed_digest);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "payload-use quarantine fence");
    require(
        store.put_payload_or_throw(good_payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "payload-use quarantine fixture did not publish its payload");

    auto snapshot = store.snapshot_or_throw();
    std::unique_ptr<ChildHeldInheritedDescriptor> inherited_holder;
    {
        auto selected = snapshot.open_payload_for_operation_or_throw(
            file_operation(folder, good_payload),
            "payload-use quarantine retained descriptor");
        overwrite_private_file(payload_path, corrupt_payload);
        require_integrity_error(
            [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
            expected_digest, observed_digest, false,
            "payload-use quarantine fixture did not install its exact integrity fault");

        require_lease_busy(
            [&] {
                (void)store.quarantine_corrupt_payload_or_throw(
                    expected_digest, observed_digest);
            },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            "quarantine renamed a payload inode while an issued descriptor still held shared use authority");
        require(
            fs::is_regular_file(payload_path) && !fs::exists(quarantine_path) &&
                read_file_bytes(payload_path) == corrupt_payload,
            "payload-use lease contention partially mutated the authoritative or quarantine namespace");

        inherited_holder = std::make_unique<ChildHeldInheritedDescriptor>(
            selected.borrowed_descriptor(), temporary.path(),
            "quarantine-fence");
    }
    require_lease_busy(
        [&] {
            (void)store.quarantine_corrupt_payload_or_throw(
                expected_digest, observed_digest);
        },
        anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
        "quarantine ignored a shared payload-use lease retained only by an inherited descriptor in another process");
    inherited_holder->release_and_wait_or_fail();
    inherited_holder.reset();

    const auto quarantined = store.quarantine_corrupt_payload_or_throw(
        expected_digest, observed_digest);
    require(
        quarantined.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    Quarantined &&
            quarantined.quarantine_basename == quarantine_path.filename() &&
            !fs::exists(payload_path) &&
            fs::is_regular_file(quarantine_path) &&
            read_file_bytes(quarantine_path) == corrupt_payload,
        "quarantine did not proceed after the final selected descriptor released its inode lease");
}

void test_exact_corrupt_payload_quarantine_is_bounded_and_recoverable() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("exact-quarantine");
    const std::string folder = "folder-exact-corrupt-payload-quarantine";
    const std::string good_payload =
        "exact-quarantine-good-payload-current-byte-authority";
    const std::string first_corrupt(good_payload.size(), 'Q');
    const std::string second_corrupt(good_payload.size(), 'R');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string first_observed = anonsync::sha256_hex(first_corrupt);
    const std::string second_observed = anonsync::sha256_hex(second_corrupt);
    const std::string unrelated_observed =
        anonsync::sha256_hex("unrelated quarantine request");
    const fs::path payload_path = root / expected_digest;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "exact corrupt payload quarantine");
    require(
        store.put_payload_or_throw(good_payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "exact-quarantine fixture did not publish the good payload");
    overwrite_private_file(payload_path, first_corrupt);
    require_integrity_error(
        [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
        expected_digest, first_observed, false,
        "forced current-byte proof did not install the exact quarantine witness");

    const auto wrong = store.quarantine_corrupt_payload_or_throw(
        expected_digest, unrelated_observed);
    require(
        wrong.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ActiveFaultMismatch &&
            wrong.current_observed_content_sha256 == first_observed &&
            wrong.quarantine_basename.empty() &&
            fs::is_regular_file(payload_path),
        "a stale quarantine request moved bytes or lost the current witness");

    overwrite_private_file(payload_path, second_corrupt);
    const auto changed = store.quarantine_corrupt_payload_or_throw(
        expected_digest, first_observed);
    require(
        changed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ObservedDigestChanged &&
            changed.current_observed_content_sha256 == second_observed &&
            changed.quarantine_basename.empty() &&
            changed.size_bytes == second_corrupt.size() &&
            fs::is_regular_file(payload_path),
        "quarantine accepted a stale observed-byte digest or lost new evidence");
    const auto now_stale = store.quarantine_corrupt_payload_or_throw(
        expected_digest, first_observed);
    require(
        now_stale.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ActiveFaultMismatch &&
            now_stale.current_observed_content_sha256 == second_observed &&
            now_stale.quarantine_basename.empty(),
        "changed corruption did not replace the exact active request pair");

    struct stat source_before{};
    require(
        ::stat(payload_path.c_str(), &source_before) == 0,
        "exact-quarantine fixture could not stat the corrupt source inode");
    const auto quarantined = store.quarantine_corrupt_payload_or_throw(
        expected_digest, second_observed);
    const fs::path quarantine_path = root / quarantined.quarantine_basename;
    struct stat destination_after{};
    require(
        quarantined.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    Quarantined &&
            quarantined.expected_content_sha256 == expected_digest &&
            quarantined.requested_observed_content_sha256 == second_observed &&
            quarantined.current_observed_content_sha256 == second_observed &&
            quarantined.size_bytes == second_corrupt.size() &&
            !fs::exists(payload_path) &&
            ::stat(quarantine_path.c_str(), &destination_after) == 0 &&
            source_before.st_dev == destination_after.st_dev &&
            source_before.st_ino == destination_after.st_ino &&
            read_file_bytes(quarantine_path) == second_corrupt &&
            anonsync::sync_replica_file_payload_store_quarantine_basename_is_exact(
                quarantined.quarantine_basename),
        "exact quarantine did not preserve the same corrupt inode outside authority");

    const auto idempotent = store.quarantine_corrupt_payload_or_throw(
        expected_digest, second_observed);
    require(
        idempotent.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ExactQuarantineAlreadyPresent &&
            idempotent.size_bytes == second_corrupt.size() &&
            read_file_bytes(quarantine_path) == second_corrupt,
        "an exact retained quarantine was not byte-reproved idempotently");

    const auto absent = store.snapshot_rechecking_current_bytes_or_throw();
    require(
        absent.entry_count() == 0U && absent.scan_hashed_entry_count() == 0U &&
            absent.scan_hashed_bytes() == 0U && fs::is_regular_file(quarantine_path),
        "complete absence reproof did not clear authority while retaining evidence");
    require(
        store.put_payload_or_throw(good_payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "ordinary convergence could not re-admit correct bytes after quarantine");
    const auto repaired = store.snapshot_rechecking_current_bytes_or_throw();
    require(
        repaired.entry_count() == 1U &&
            repaired.scan_hashed_entry_count() == 1U &&
            repaired.scan_hashed_bytes() == good_payload.size() &&
            repaired.copy_payload_for_operation_or_throw(
                file_operation(folder, good_payload)) == good_payload &&
            fs::is_regular_file(quarantine_path),
        "re-admission did not restore payload authority alongside retained evidence");

    // The same digest name can later corrupt to the same byte image again.
    // The exact retained destination must make that second explicit action
    // recoverable rather than permanently idempotent-but-stuck: its bytes are
    // re-proved, the duplicate authoritative source is removed, and the
    // original retained inode remains unchanged.
    overwrite_private_file(payload_path, second_corrupt);
    require_integrity_error(
        [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
        expected_digest, second_observed, false,
        "repeated exact corruption did not reinstall quarantine authority");
    struct stat retained_before_repeat{};
    require(
        ::stat(quarantine_path.c_str(), &retained_before_repeat) == 0,
        "repeated exact-quarantine fixture lost its retained destination");
    const auto repeated = store.quarantine_corrupt_payload_or_throw(
        expected_digest, second_observed);
    struct stat retained_after_repeat{};
    require(
        repeated.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ExactQuarantineAlreadyPresent &&
            repeated.quarantine_basename == quarantined.quarantine_basename &&
            !fs::exists(payload_path) &&
            ::stat(quarantine_path.c_str(), &retained_after_repeat) == 0 &&
            retained_before_repeat.st_dev == retained_after_repeat.st_dev &&
            retained_before_repeat.st_ino == retained_after_repeat.st_ino &&
            read_file_bytes(quarantine_path) == second_corrupt,
        "an exact retained quarantine left repeated corrupt authority stuck");
    require(
        store.snapshot_rechecking_current_bytes_or_throw().entry_count() == 0U,
        "repeated exact quarantine did not permit complete absence reproof");
    require(
        store.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
            store.snapshot_rechecking_current_bytes_or_throw().entry_count() ==
                1U,
        "repeated exact quarantine did not permit ordinary byte re-admission");

    anonsync::SyncReplicaFilePayloadStore inspector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        limits, "exact quarantine read-only inspector");
    require_error(
        [&] {
            (void)inspector.quarantine_corrupt_payload_or_throw(
                expected_digest, second_observed);
        },
        "read-only inspection store cannot quarantine",
        "forensic inspection acquired quarantine mutation authority");

    require(
        !anonsync::sync_replica_file_payload_store_quarantine_basename_is_exact(
            ".anonsync-payload-quarantine-v1-not-a-digest") &&
            !anonsync::sync_replica_file_payload_store_quarantine_basename_is_exact(
                quarantined.quarantine_basename + "-tail"),
        "payload quarantine parser accepted a non-canonical retained name");
}

void test_exact_quarantine_release_preserves_unrelated_byte_proof() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("exact-quarantine-release");
    const std::string folder = "folder-exact-quarantine-release";
    const std::string faulted_good = "release-target-current-good-bytes";
    const std::string faulted_bad(faulted_good.size(), 'X');
    const std::string stable = "unrelated-process-proof-must-survive-release";
    const std::string expected_digest = anonsync::sha256_hex(faulted_good);
    const std::string observed_digest = anonsync::sha256_hex(faulted_bad);
    const std::string stable_digest = anonsync::sha256_hex(stable);
    const fs::path payload_path = root / expected_digest;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "exact quarantine release");
    require(
        store.put_payload_or_throw(faulted_good).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
            store.put_payload_or_throw(stable).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "quarantine-release fixture did not publish both payloads");
    const auto warm = store.snapshot_rechecking_current_bytes_or_throw();
    require(
        warm.entry_count() == 2U && warm.scan_hashed_entry_count() == 2U,
        "quarantine-release fixture did not establish complete byte proof");

    overwrite_private_file(payload_path, faulted_bad);
    require_integrity_error(
        [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
        expected_digest, observed_digest, false,
        "quarantine-release fixture did not install its active fault");
    const auto preserved = store.quarantine_corrupt_payload_or_throw(
        expected_digest, observed_digest);
    const fs::path quarantine_path = root / preserved.quarantine_basename;
    require(
        preserved.action ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineAction::Preserve &&
            preserved.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    Quarantined &&
            fs::is_regular_file(quarantine_path) && !fs::exists(payload_path),
        "exact quarantine preserve did not publish typed diagnostic evidence");

    const auto blocked = store.release_quarantined_payload_or_throw(
        expected_digest, observed_digest);
    require(
        blocked.action ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineAction::Release &&
            blocked.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ActiveFaultPresent &&
            blocked.current_observed_content_sha256 == observed_digest &&
            fs::is_regular_file(quarantine_path),
        "release removed evidence before complete recovery reproof");

    const auto absence = store.snapshot_or_throw();
    require(
        absence.entry_count() == 1U &&
            absence.payload_size_or_none(stable_digest) == stable.size() &&
            absence.scan_hashed_entry_count() == 0U &&
            absence.scan_process_reused_entry_count() == 1U &&
            absence.scan_process_reused_bytes() == stable.size(),
        "quarantine forced a whole-store rehash instead of retaining unrelated exact process proof");

    const auto released = store.release_quarantined_payload_or_throw(
        expected_digest, observed_digest);
    require(
        released.action ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineAction::Release &&
            released.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    Released &&
            released.quarantine_basename == preserved.quarantine_basename &&
            released.size_bytes == faulted_bad.size() &&
            !fs::exists(quarantine_path),
        "exact quarantine release did not unlink only the selected evidence");

    const auto after_release = store.snapshot_or_throw();
    require(
        after_release.entry_count() == 1U &&
            after_release.payload_size_or_none(stable_digest) == stable.size() &&
            after_release.scan_hashed_entry_count() == 0U &&
            after_release.scan_process_reused_entry_count() == 1U &&
            after_release.scan_process_reused_bytes() == stable.size(),
        "non-authoritative quarantine release revoked authoritative byte reuse");

    const auto absent = store.release_quarantined_payload_or_throw(
        expected_digest, observed_digest);
    require(
        absent.disposition ==
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    ExactQuarantineAbsent &&
            absent.current_observed_content_sha256.empty() &&
            absent.quarantine_basename.empty() && absent.size_bytes == 0U,
        "second exact quarantine release was not a typed nonmutating absence");

    anonsync::SyncReplicaFilePayloadStore inspector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        limits, "exact quarantine release inspector");
    require_error(
        [&] {
            (void)inspector.release_quarantined_payload_or_throw(
                expected_digest, observed_digest);
        },
        "read-only inspection store cannot release quarantined bytes",
        "forensic inspection acquired quarantine-release mutation authority");
}

void test_quarantine_inventory_is_restart_discoverable_and_exactly_updated() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("quarantine-inventory-status");
    const std::string folder = "folder-quarantine-inventory-status";

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    {
        anonsync::SyncReplicaFilePayloadStore bootstrap(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "quarantine inventory bootstrap");
        const auto unknown = bootstrap.quarantine_inventory_status();
        require(
            !bootstrap.quarantine_inventory_observation_known() &&
                !unknown.observation_known &&
                !unknown.last_observation_age_milliseconds.has_value() &&
                unknown.entry_limit ==
                    anonsync::kSyncReplicaFilePayloadStoreMaxQuarantineEntries &&
                unknown.byte_limit == limits.max_indexed_bytes &&
                unknown.total_bytes == 0U && unknown.entries.empty(),
            "fresh payload-store owner invented a quarantine observation");
        require(
            bootstrap.snapshot_or_throw().entry_count() == 0U,
            "quarantine inventory fixture did not establish an empty store");
        const auto known_empty = bootstrap.quarantine_inventory_status();
        require(
            bootstrap.quarantine_inventory_observation_known() &&
                known_empty.observation_known &&
                known_empty.last_observation_age_milliseconds.has_value() &&
                known_empty.total_bytes == 0U && known_empty.entries.empty(),
            "complete empty scan did not publish an exact empty quarantine inventory");
    }

    struct FixtureEntry final {
        std::string expected;
        std::string observed;
        std::string bytes;
    };
    std::vector<FixtureEntry> fixtures{
        {
            anonsync::sha256_hex("quarantine-inventory-expected-z"),
            anonsync::sha256_hex("quarantine-inventory-observed-z"),
            "retained diagnostic image z",
        },
        {
            anonsync::sha256_hex("quarantine-inventory-expected-a"),
            anonsync::sha256_hex("quarantine-inventory-observed-a"),
            "retained diagnostic image a",
        },
    };
    const auto quarantine_path = [&](const FixtureEntry& entry) {
        return root /
            (std::string(".anonsync-payload-quarantine-v1-") +
             entry.expected + "-" + entry.observed);
    };
    // Publish in the opposite order from the expected canonical projection.
    write_private_file(quarantine_path(fixtures[0]), fixtures[0].bytes);
    write_private_file(quarantine_path(fixtures[1]), fixtures[1].bytes);

    std::sort(
        fixtures.begin(), fixtures.end(),
        [](const FixtureEntry& left, const FixtureEntry& right) {
            if (left.expected != right.expected) {
                return left.expected < right.expected;
            }
            return left.observed < right.observed;
        });
    const std::uint64_t expected_total =
        static_cast<std::uint64_t>(
            fixtures[0].bytes.size() + fixtures[1].bytes.size());

    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "quarantine inventory restarted owner");
        const auto process_cold = restarted.quarantine_inventory_status();
        require(
            !restarted.quarantine_inventory_observation_known() &&
                !process_cold.observation_known && process_cold.entries.empty() &&
                process_cold.total_bytes == 0U,
            "restart borrowed a prior process's quarantine observation");

        require(
            restarted.snapshot_or_throw().entry_count() == 0U,
            "diagnostic quarantine leaked into authoritative payload inventory");
        const auto discovered = restarted.quarantine_inventory_status();
        require(
            restarted.quarantine_inventory_observation_known() &&
                discovered.observation_known &&
                discovered.last_observation_age_milliseconds.has_value() &&
                discovered.entry_limit ==
                    anonsync::kSyncReplicaFilePayloadStoreMaxQuarantineEntries &&
                discovered.byte_limit == limits.max_indexed_bytes &&
                discovered.total_bytes == expected_total &&
                discovered.entries.size() == fixtures.size(),
            "complete restart scan did not publish the bounded exact quarantine inventory");
        for (std::size_t index = 0U; index < fixtures.size(); ++index) {
            const auto& actual = discovered.entries[index];
            const auto& expected = fixtures[index];
            require(
                actual.expected_content_sha256 == expected.expected &&
                    actual.observed_content_sha256 == expected.observed &&
                    actual.size_bytes == expected.bytes.size(),
                "quarantine inventory was not canonical, exact, and size-bound");
        }

        const FixtureEntry released_fixture = fixtures.front();
        const auto released = restarted.release_quarantined_payload_or_throw(
            released_fixture.expected, released_fixture.observed);
        require(
            released.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        Released &&
                !fs::exists(quarantine_path(released_fixture)),
            "exact release did not remove the selected quarantine fixture");
        const auto after_release = restarted.quarantine_inventory_status();
        require(
            restarted.quarantine_inventory_observation_known() &&
                after_release.observation_known &&
                after_release.last_observation_age_milliseconds.has_value() &&
                after_release.entries.size() == 1U &&
                after_release.entries.front().expected_content_sha256 ==
                    fixtures.back().expected &&
                after_release.entries.front().observed_content_sha256 ==
                    fixtures.back().observed &&
                after_release.entries.front().size_bytes ==
                    fixtures.back().bytes.size() &&
                after_release.total_bytes == fixtures.back().bytes.size(),
            "exact release did not publish its exact successor inventory without another scan");

        const auto absent = restarted.release_quarantined_payload_or_throw(
            released_fixture.expected, released_fixture.observed);
        const auto after_absent = restarted.quarantine_inventory_status();
        require(
            absent.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ExactQuarantineAbsent &&
                after_absent.observation_known &&
                after_absent.entries == after_release.entries &&
                after_absent.total_bytes == after_release.total_bytes,
            "nonmutating exact absence changed or forgot the complete inventory");
    }

    {
        anonsync::SyncReplicaFilePayloadStore second_restart(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "quarantine inventory second restart");
        require(
            !second_restart.quarantine_inventory_status().observation_known,
            "second restart borrowed process-local quarantine status");
        require(
            second_restart.snapshot_or_throw().entry_count() == 0U,
            "second restart admitted diagnostic bytes as payload authority");
        const auto rediscovered =
            second_restart.quarantine_inventory_status();
        require(
            rediscovered.observation_known &&
                rediscovered.entries.size() == 1U &&
                rediscovered.entries.front().expected_content_sha256 ==
                    fixtures.back().expected &&
                rediscovered.entries.front().observed_content_sha256 ==
                    fixtures.back().observed &&
                rediscovered.total_bytes == fixtures.back().bytes.size(),
            "ordinary restart scan did not rediscover retained diagnostic evidence");
    }
}

void test_fresh_bootstrap_never_adopts_quarantine_evidence() {
    TemporaryDirectory temporary;
    const fs::path root =
        temporary.make_store_root("quarantine-bootstrap-rejection");
    const std::string folder = "folder-quarantine-bootstrap-rejection";
    const std::string expected = anonsync::sha256_hex("expected-bootstrap");
    const std::string observed = anonsync::sha256_hex("observed-bootstrap");
    const fs::path quarantine_path =
        root / (std::string(".anonsync-payload-quarantine-v1-") + expected +
                "-" + observed);
    write_private_file(quarantine_path, "unbound diagnostic bytes");

    require_error(
        [&] {
            anonsync::SyncReplicaFilePayloadStore owner(
                folder, root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                    CreateIfMissing,
                {}, "standalone quarantine bootstrap rejection");
            (void)owner.snapshot_or_throw();
        },
        "fresh bootstrap refuses pre-existing payload quarantine evidence",
        "standalone adoption silently assigned unbound quarantine evidence to a fresh store identity");

    std::size_t retained_entries = 0U;
    for (const auto& ignored : fs::directory_iterator(root)) {
        (void)ignored;
        ++retained_entries;
    }
    require(
        retained_entries == 1U && fs::is_regular_file(quarantine_path),
        "quarantine bootstrap rejection mutated evidence or published an identity marker");
}

void test_quarantine_bytes_cannot_exceed_active_indexed_byte_budget() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("quarantine-byte-budget");
    const std::string folder = "folder-quarantine-byte-budget";

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 8U;
    limits.max_indexed_bytes = 16U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;

    {
        anonsync::SyncReplicaFilePayloadStore owner(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "quarantine indexed-byte budget bootstrap");
        require(
            owner.snapshot_or_throw().entry_count() == 0U,
            "quarantine indexed-byte budget fixture did not establish an empty identity");
    }

    const auto quarantine_name = [](std::string_view expected_seed,
                                    std::string_view observed_seed) {
        return std::string(".anonsync-payload-quarantine-v1-") +
            anonsync::sha256_hex(std::string(expected_seed)) + "-" +
            anonsync::sha256_hex(std::string(observed_seed));
    };
    write_private_file(
        root / quarantine_name("expected-1", "observed-1"),
        std::string(8U, 'A'));
    write_private_file(
        root / quarantine_name("expected-2", "observed-2"),
        std::string(8U, 'B'));

    {
        anonsync::SyncReplicaFilePayloadStore inspector(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
            limits, "quarantine indexed-byte budget exact frontier");
        require(
            inspector.snapshot_or_throw().entry_count() == 0U,
            "quarantine bytes at the active indexed-byte frontier entered payload authority");
    }

    write_private_file(
        root / quarantine_name("expected-3", "observed-3"), "C");
    anonsync::SyncReplicaFilePayloadStore over_budget(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        limits, "quarantine indexed-byte budget overflow");
    require_error(
        [&] { (void)over_budget.snapshot_or_throw(); },
        "payload quarantine bytes exceed fixed budget",
        "hidden quarantine bytes exceeded the active indexed-byte budget");
}

void test_quarantine_capacity_is_a_typed_nonfatal_result() {
    const auto quarantine_name = [](std::string_view expected_seed,
                                    std::string_view observed_seed) {
        return std::string(".anonsync-payload-quarantine-v1-") +
            anonsync::sha256_hex(std::string(expected_seed)) + "-" +
            anonsync::sha256_hex(std::string(observed_seed));
    };

    {
        TemporaryDirectory temporary;
        const fs::path root =
            temporary.make_store_root("quarantine-entry-capacity");
        const std::string folder = "folder-quarantine-entry-capacity";
        const std::string good_payload =
            "quarantine-entry-capacity-good-payload";
        const std::string corrupt_payload(good_payload.size(), 'E');
        const std::string expected_digest = anonsync::sha256_hex(good_payload);
        const std::string observed_digest =
            anonsync::sha256_hex(corrupt_payload);
        const fs::path payload_path = root / expected_digest;

        anonsync::SyncReplicaFilePayloadStoreLimits limits;
        limits.max_entries = 8U;
        limits.max_payload_bytes = 4096U;
        limits.max_indexed_bytes = 16384U;
        limits.max_transient_entries = 8U;
        limits.max_transient_bytes = 1024U * 1024U;

        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "quarantine entry-capacity typed result");
        require(
            store.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "entry-capacity fixture did not publish its good payload");
        for (std::uint64_t index = 0U;
             index <
                 anonsync::kSyncReplicaFilePayloadStoreMaxQuarantineEntries;
             ++index) {
            const std::string suffix = std::to_string(index);
            write_private_file(
                root / quarantine_name(
                           "entry-expected-" + suffix,
                           "entry-observed-" + suffix),
                "Q");
        }
        overwrite_private_file(payload_path, corrupt_payload);
        require_integrity_error(
            [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
            expected_digest, observed_digest, false,
            "entry-capacity fixture did not install its active fault");

        const auto full = store.quarantine_corrupt_payload_or_throw(
            expected_digest, observed_digest);
        require(
            full.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        EntryCapacityExceeded &&
                full.quarantine_basename.empty() &&
                full.size_bytes == corrupt_payload.size() &&
                fs::is_regular_file(payload_path) &&
                read_file_bytes(payload_path) == corrupt_payload,
            "a full quarantine frontier threw or mutated instead of returning a typed entry-capacity result");
        require_integrity_error(
            [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
            expected_digest, observed_digest, false,
            "entry-capacity completion accidentally cleared the active fault");
    }

    {
        TemporaryDirectory temporary;
        const fs::path root =
            temporary.make_store_root("quarantine-byte-capacity");
        const std::string folder = "folder-quarantine-byte-capacity";
        const std::string good_payload = "GOODBYTE";
        const std::string corrupt_payload = "BADBYTES";
        const std::string expected_digest = anonsync::sha256_hex(good_payload);
        const std::string observed_digest =
            anonsync::sha256_hex(corrupt_payload);
        const fs::path payload_path = root / expected_digest;

        anonsync::SyncReplicaFilePayloadStoreLimits limits;
        limits.max_entries = 8U;
        limits.max_payload_bytes = 8U;
        limits.max_indexed_bytes = 16U;
        limits.max_transient_entries = 8U;
        limits.max_transient_bytes = 1024U * 1024U;

        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "quarantine byte-capacity typed result");
        require(
            store.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "byte-capacity fixture did not publish its good payload");
        write_private_file(
            root / quarantine_name("byte-expected-1", "byte-observed-1"),
            std::string(8U, 'A'));
        write_private_file(
            root / quarantine_name("byte-expected-2", "byte-observed-2"),
            std::string(8U, 'B'));
        overwrite_private_file(payload_path, corrupt_payload);
        require_integrity_error(
            [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
            expected_digest, observed_digest, false,
            "byte-capacity fixture did not install its active fault");

        const auto full = store.quarantine_corrupt_payload_or_throw(
            expected_digest, observed_digest);
        require(
            full.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ByteCapacityExceeded &&
                full.quarantine_basename.empty() &&
                full.size_bytes == corrupt_payload.size() &&
                fs::is_regular_file(payload_path) &&
                read_file_bytes(payload_path) == corrupt_payload,
            "a full quarantine byte budget threw or mutated instead of returning a typed capacity result");
        require_integrity_error(
            [&] { (void)store.snapshot_rechecking_current_bytes_or_throw(); },
            expected_digest, observed_digest, false,
            "byte-capacity completion accidentally cleared the active fault");
    }
}

void test_process_fault_survives_scrub_record_loss_until_reproof() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("process-fault-reproof");
    const std::string folder = "folder-process-fault-reproof";
    const std::string good_payload = "process-fault-reproof-good-payload";
    const std::string corrupt_payload(good_payload.size(), 'Q');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest = anonsync::sha256_hex(corrupt_payload);
    const fs::path payload_path = root / expected_digest;
    const fs::path verification_index_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 4096U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "process-fault publisher");
        require(
            publisher.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "process-fault fixture did not publish its payload");
    }

    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path), limits.max_entries,
            limits.max_indexed_bytes,
            "process-fault verification-index fixture");
    require(
        forged_index.entries.size() == 1U &&
            forged_index.entries.front().content_sha256 == expected_digest,
        "process-fault fixture lacks one exact restart record");
    overwrite_private_file(payload_path, corrupt_payload);
    forged_index.entries.front().metadata = private_file_metadata(
        payload_path, "process-fault forged payload metadata");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, limits.max_entries, limits.max_indexed_bytes,
                "process-fault forged verification index"));

    anonsync::SyncReplicaFilePayloadStore detector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "process-fault live detector");
    require_integrity_error(
        [&] { (void)detector.snapshot_or_throw(); }, expected_digest,
        observed_digest, true,
        "initial rotating scrub did not detect the metadata-hidden mismatch");
    require(
        fs::remove(scrub_state_path) && !fs::exists(scrub_state_path),
        "process-fault fixture did not remove the durable failure record");

    // The first failed attempt already advanced the ordinary process throttle.
    // Without the independent owner-local witness, this call would accept the
    // exact warm metadata generation and return success before another scrub.
    require_integrity_error(
        [&] { (void)detector.snapshot_or_throw(); }, expected_digest,
        observed_digest, false,
        "durable scrub-record loss restored unchanged-metadata authority");
    require_integrity_error(
        [&] { (void)detector.begin_mutation_batch_or_throw(); },
        expected_digest, observed_digest, false,
        "a mutation preflight bypassed the process-local integrity fault");

    overwrite_private_file(payload_path, good_payload);
    const auto repaired = detector.snapshot_or_throw();
    require(
        repaired.entry_count() == 1U &&
            repaired.scan_hashed_entry_count() == 1U &&
            repaired.scan_hashed_bytes() == good_payload.size() &&
            repaired.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredBySchedule &&
            repaired.copy_payload_for_operation_or_throw(
                file_operation(folder, good_payload)) == good_payload,
        "current good bytes did not clear the process-local fault under the complete scan cutpoint");

    const auto warm = detector.snapshot_or_throw();
    require(
        warm.scan_hashed_entry_count() == 0U &&
            warm.scan_process_reused_entry_count() == 1U &&
            warm.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredBySchedule,
        "cleared process-local integrity evidence continued to force duplicate payload hashing");
}

void test_process_fault_permanently_revokes_live_snapshot_authority() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("snapshot-revocation");
    const std::string folder = "folder-snapshot-revocation";
    const std::string good_payload = "snapshot-revocation-good-payload";
    const std::string corrupt_payload =
        "snapshot-revocation-corrupt-payload-with-different-size";
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest = anonsync::sha256_hex(corrupt_payload);
    const fs::path payload_path = root / expected_digest;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 4096U;
    limits.max_scrub_entries_per_attempt = 1U;

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "snapshot-revocation store");
    require(
        store.put_payload_or_throw(good_payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "snapshot-revocation fixture did not publish its payload");
    const auto issued_before_fault = store.snapshot_or_throw();
    const std::string issued_digest = issued_before_fault.snapshot_digest();

    // A size change guarantees that the next complete scan cannot reuse the
    // process-local observation. That scan records the typed owner-local fault
    // before it fails, which must revoke the already issued snapshot even for
    // metadata-only methods that otherwise perform no filesystem reproof.
    overwrite_private_file(payload_path, corrupt_payload);
    require_integrity_error(
        [&] { (void)store.snapshot_or_throw(); }, expected_digest,
        observed_digest, false,
        "current-byte mismatch did not establish the snapshot revocation fence");
    require_integrity_error(
        [&] { (void)issued_before_fault.snapshot_digest(); }, expected_digest,
        observed_digest, false,
        "a live pre-fault snapshot retained digest authority after corruption");
    require_integrity_error(
        [&] {
            issued_before_fault.preflight_or_throw(
                "snapshot-revocation old authority preflight");
        },
        expected_digest, observed_digest, false,
        "a live pre-fault snapshot retained rooted authority after corruption");

    overwrite_private_file(payload_path, good_payload);
    const auto replacement = store.snapshot_or_throw();
    require(
        replacement.snapshot_digest() == issued_digest &&
            replacement.scan_hashed_entry_count() == 1U &&
            replacement.scan_hashed_bytes() == good_payload.size() &&
            replacement.copy_payload_for_operation_or_throw(
                file_operation(folder, good_payload)) == good_payload,
        "current good bytes did not issue replacement snapshot authority");

    // Clearing the active fault must not roll the revocation epoch back. The
    // old point-in-time capability remains dead; only the replacement scan may
    // be used after repair.
    require_integrity_error(
        [&] { (void)issued_before_fault.content_inventory(); }, expected_digest,
        observed_digest, false,
        "repair resurrected a snapshot that was live when corruption was found");
}

void test_process_fault_preserves_original_target_across_second_mismatch() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("process-fault-ordering");
    const std::string folder = "folder-process-fault-ordering";
    const std::string payload_a = "process-fault-ordering-payload-alpha";
    const std::string payload_b = "process-fault-ordering-payload-bravo";
    const std::string digest_a = anonsync::sha256_hex(payload_a);
    const std::string digest_b = anonsync::sha256_hex(payload_b);
    const bool a_is_first = digest_a < digest_b;
    const std::string first_good = a_is_first ? payload_a : payload_b;
    const std::string second_good = a_is_first ? payload_b : payload_a;
    const std::string first_digest = a_is_first ? digest_a : digest_b;
    const std::string second_digest = a_is_first ? digest_b : digest_a;
    const std::string first_corrupt(first_good.size(), 'F');
    const std::string second_corrupt(second_good.size(), 'S');
    const std::string first_observed = anonsync::sha256_hex(first_corrupt);
    const std::string second_observed = anonsync::sha256_hex(second_corrupt);
    const fs::path first_path = root / first_digest;
    const fs::path second_path = root / second_digest;
    const fs::path verification_index_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 4096U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "process-fault ordering publisher");
        require(
            publisher.put_payload_or_throw(payload_a).disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
                publisher.put_payload_or_throw(payload_b).disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "process-fault ordering fixture did not publish both payloads");
    }

    // Seed the fair cursor past the lexicographically first digest so the next
    // fresh owner detects the later digest through bounded scrub.
    {
        anonsync::SyncReplicaFilePayloadStore cursor_seed(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "process-fault ordering cursor seed");
        const auto seeded = cursor_seed.snapshot_or_throw();
        const auto seeded_state = read_scrub_state_or_fail(
            root, limits.max_payload_bytes,
            "process-fault ordering seeded state");
        require(
            seeded.entry_count() == 2U &&
                seeded.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        Advanced &&
                seeded.scrub_report().completed_entry_count == 1U &&
                seeded_state.cursor_after_content_sha256 == first_digest,
            "process-fault ordering fixture did not seed the later scrub target");
    }

    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path), limits.max_entries,
            limits.max_indexed_bytes,
            "process-fault ordering verification-index fixture");
    require(
        forged_index.entries.size() == 2U,
        "process-fault ordering fixture lacks two restart records");
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(second_path, second_corrupt);
    bool forged_second = false;
    for (auto& entry : forged_index.entries) {
        if (entry.content_sha256 == second_digest) {
            entry.metadata = private_file_metadata(
                second_path, "process-fault ordering forged later metadata");
            forged_second = true;
        }
    }
    require(
        forged_second,
        "process-fault ordering fixture could not find the later restart record");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, limits.max_entries, limits.max_indexed_bytes,
                "process-fault ordering forged verification index"));

    anonsync::SyncReplicaFilePayloadStore detector(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "process-fault ordering live detector");
    require_integrity_error(
        [&] { (void)detector.snapshot_or_throw(); }, second_digest,
        second_observed, true,
        "later bounded scrub did not establish the original process fault");
    require(
        fs::remove(scrub_state_path) && !fs::exists(scrub_state_path),
        "process-fault ordering fixture did not remove durable evidence");

    // A changed second path is independently hash-forcing. The complete
    // namespace scanner intentionally follows descriptor-owned readdir order,
    // not digest order, so either mismatch may be the first typed result on a
    // particular filesystem. Whichever one is reported first, repairing only
    // that path must expose the other mismatch; no unresolved witness may be
    // displaced merely because directory enumeration chose another order.
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(first_path, first_corrupt);
    const auto observe_one_of_two_faults = [&](const std::string& message) {
        ++checks;
        try {
            (void)detector.snapshot_or_throw();
        } catch (const anonsync::SyncReplicaFilePayloadStoreIntegrityError&
                     error) {
            if (error.failure_persisted()) {
                fail(message + ": lost durable evidence was invented again");
            }
            if (error.expected_content_sha256() == first_digest &&
                error.observed_content_sha256() == first_observed) {
                return first_digest;
            }
            if (error.expected_content_sha256() == second_digest &&
                error.observed_content_sha256() == second_observed) {
                return second_digest;
            }
            fail(message + ": scanner reported unrelated integrity evidence");
        } catch (const std::exception& error) {
            fail(message + ": wrong exception type: " + error.what());
        }
        fail(message + ": no error was thrown");
    };
    const std::string first_reported = observe_one_of_two_faults(
        "two simultaneous mismatches did not fail the complete scan");

    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    if (first_reported == first_digest) {
        overwrite_private_file(first_path, first_good);
        require_integrity_error(
            [&] { (void)detector.snapshot_or_throw(); }, second_digest,
            second_observed, false,
            "repairing the first-reported mismatch displaced the original unresolved process fault");
    } else {
        overwrite_private_file(second_path, second_good);
        require_integrity_error(
            [&] { (void)detector.snapshot_or_throw(); }, first_digest,
            first_observed, false,
            "repairing the original first-reported mismatch hid the other changed payload");
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    overwrite_private_file(first_path, first_good);
    overwrite_private_file(second_path, second_good);
    const auto repaired = detector.snapshot_or_throw();
    require(
        repaired.entry_count() == 2U &&
            repaired.scan_hashed_entry_count() >= 1U &&
            repaired.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredBySchedule &&
            repaired.copy_payload_for_operation_or_throw(
                file_operation(folder, first_good)) == first_good &&
            repaired.copy_payload_for_operation_or_throw(
                file_operation(folder, second_good)) == second_good,
        "repair of both mismatches did not release the original witness safely");

    const auto warm = detector.snapshot_or_throw();
    require(
        warm.scan_hashed_entry_count() == 0U &&
            warm.scan_process_reused_entry_count() == 2U,
        "multi-fault reproof did not restore exact warm metadata reuse");
}

void test_complete_scan_supersedes_stale_active_scrub_checkpoint() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root(
        "complete-scan-supersedes-stale-scrub-checkpoint");
    const std::string folder =
        "folder-complete-scan-supersedes-stale-scrub-checkpoint";
    const std::string payload =
        "current-good-payload-after-metadata-hidden-repair";
    const std::string digest = anonsync::sha256_hex(payload);
    const std::string stale_prefix(13U, 'X');

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 4096U;
    limits.max_scrub_entries_per_attempt = 1U;

    // Bootstrap without starting a scrub, so the verification index is an
    // exact ordinary restart checkpoint for the good payload.
    auto bootstrap_limits = limits;
    bootstrap_limits.max_scrub_bytes_per_attempt = 0U;
    bootstrap_limits.max_scrub_entries_per_attempt = 0U;
    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            bootstrap_limits, "stale-active-checkpoint publisher");
        require(
            publisher.put_payload_or_throw(payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "stale-active-checkpoint fixture did not publish its payload");
    }

    const fs::path identity_path =
        root / std::string(kStandaloneIdentityCurrent);
    const fs::path payload_path = root / digest;
    const fs::path state_path =
        root /
        std::string(anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    require(
        fs::exists(
            root / std::string(
                       anonsync::
                           kSyncReplicaFilePayloadVerificationIndexBasename)),
        "stale-active-checkpoint fixture lacks restart acceleration");

    auto progress =
        anonsync::initial_sync_replica_file_payload_scrub_state_or_throw(
            anonsync::sha256_hex(read_file_bytes(identity_path)),
            private_file_metadata(
                identity_path, "stale-active-checkpoint identity metadata"),
            "stale-active-checkpoint state");
    progress.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Progress;
    progress.active_content_sha256 = digest;
    progress.active_metadata = private_file_metadata(
        payload_path, "stale-active-checkpoint payload metadata");
    progress.active_offset_bytes = stale_prefix.size();
    anonsync::ResumableSha256 stale_hash;
    stale_hash.update(stale_prefix);
    progress.active_hash = stale_hash.checkpoint();
    progress.observed_content_sha256.clear();
    write_private_file(
        state_path,
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            progress, limits.max_payload_bytes,
            "stale-active-checkpoint serialization"));

    // The active write-ahead state correctly forces a complete current-byte
    // scan on this fresh owner. That full good-byte proof must supersede the
    // older partial SHA checkpoint. Resuming the stale checkpoint would combine
    // the old corrupt prefix with the repaired suffix and raise a false alarm.
    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "stale-active-checkpoint restart");
    const auto snapshot = restarted.snapshot_or_throw();
    require(
        snapshot.entry_count() == 1U &&
            snapshot.scan_hashed_entry_count() == 1U &&
            snapshot.scan_hashed_bytes() == payload.size() &&
            snapshot.scan_durable_reused_entry_count() == 0U &&
            snapshot.scan_process_reused_entry_count() == 0U &&
            snapshot.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::Advanced &&
            snapshot.scrub_report().hashed_bytes == 0U &&
            snapshot.scrub_report().touched_entry_count == 0U &&
            snapshot.scrub_report().completed_entry_count == 1U &&
            snapshot.scrub_report().reverified_active_completed &&
            !snapshot.scrub_report().reverified_failure_cleared &&
            snapshot.scrub_report().active_content_sha256.empty() &&
            snapshot.scrub_report().active_offset_bytes == 0U &&
            snapshot.copy_payload_for_operation_or_throw(
                file_operation(folder, payload)) == payload,
        "complete scan did not supersede stale active scrub progress exactly");

    const auto settled = read_scrub_state_or_fail(
        root, limits.max_payload_bytes,
        "stale-active-checkpoint settled state");
    require(
        settled.disposition ==
                anonsync::SyncReplicaFilePayloadScrubStateDisposition::Idle &&
            settled.cursor_after_content_sha256 == digest &&
            settled.completed_cycles == 0U &&
            settled.active_content_sha256.empty() &&
            settled.active_offset_bytes == 0U,
        "complete-scan handoff did not durably settle stale active progress");
}

void test_minimum_reader_identity_migration_is_cold_atomic_and_inode_preserving() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root(
        "minimum-reader-identity-migration");
    const std::string folder =
        "folder-minimum-reader-identity-migration";
    const std::string good_payload =
        "minimum-reader-fence-current-good-payload";
    const std::string corrupt_payload(good_payload.size(), 'Z');
    const std::string expected_digest = anonsync::sha256_hex(good_payload);
    const std::string observed_digest = anonsync::sha256_hex(corrupt_payload);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 7U;
    limits.max_scrub_entries_per_attempt = 1U;

    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "minimum-reader migration publisher");
        require(
            publisher.put_payload_or_throw(good_payload).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "minimum-reader migration fixture did not publish its payload");
    }

    const fs::path current_identity =
        root / std::string(kStandaloneIdentityCurrent);
    const fs::path legacy_identity =
        root / std::string(kStandaloneIdentityLegacyReader);
    const fs::path payload_path = root / expected_digest;
    const fs::path verification_index_path =
        root / std::string(
                   anonsync::
                       kSyncReplicaFilePayloadVerificationIndexBasename);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    require(
        fs::is_regular_file(current_identity) &&
            !fs::exists(legacy_identity) &&
            fs::is_regular_file(verification_index_path),
        "minimum-reader migration fixture lacks current restart authority");

    auto forged_index = anonsync::
        parse_sync_replica_file_payload_verification_index_or_throw(
            read_file_bytes(verification_index_path), limits.max_entries,
            limits.max_indexed_bytes,
            "minimum-reader migration verification index");
    require(
        forged_index.entries.size() == 1U &&
            forged_index.entries.front().content_sha256 == expected_digest,
        "minimum-reader migration fixture lacks one indexed payload");

    // Model the exact on-disk generation left by rev0958. The basename changes
    // but the identity inode and bytes do not. Reframe the non-authoritative
    // checkpoint against the rename-induced ctime so an old reader would find
    // the marker/index metadata exact.
    rename_private_file_and_sync_directory(
        current_identity, legacy_identity,
        "minimum-reader legacy-generation fixture");
    const auto legacy_identity_inode = private_file_identity(legacy_identity);
    forged_index.store_identity_metadata = private_file_metadata(
        legacy_identity, "minimum-reader legacy identity metadata");

    // Hide corrupt bytes behind exact current metadata in the restart index and
    // publish a valid rev0958 Prepared record. The migration must not interpret
    // either record as content authority.
    overwrite_private_file(payload_path, corrupt_payload);
    forged_index.entries.front().metadata = private_file_metadata(
        payload_path, "minimum-reader forged payload metadata");
    overwrite_private_file(
        verification_index_path,
        anonsync::
            serialize_sync_replica_file_payload_verification_index_or_throw(
                forged_index, limits.max_entries, limits.max_indexed_bytes,
                "minimum-reader forged verification index"));

    auto prepared =
        anonsync::initial_sync_replica_file_payload_scrub_state_or_throw(
            anonsync::sha256_hex(read_file_bytes(legacy_identity)),
            private_file_metadata(
                legacy_identity,
                "minimum-reader Prepared identity metadata"),
            "minimum-reader Prepared state");
    prepared.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Prepared;
    prepared.active_content_sha256 = expected_digest;
    prepared.active_metadata = private_file_metadata(
        payload_path, "minimum-reader Prepared payload metadata");
    prepared.active_offset_bytes = 0U;
    prepared.active_hash = anonsync::ResumableSha256{}.checkpoint();
    prepared.observed_content_sha256.clear();
    write_private_file(
        scrub_state_path,
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            prepared, limits.max_payload_bytes,
            "minimum-reader Prepared serialization"));

    // Forensic observation never mutates an older reader generation. It fails
    // because only the new reader-fenced name can be an observation anchor.
    {
        anonsync::SyncReplicaFilePayloadStore inspector(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                ReadOnlyInspect,
            limits, "minimum-reader read-only inspector");
        require_error(
            [&] { (void)inspector.snapshot_or_throw(); },
            "identity marker is absent",
            "read-only inspection silently migrated the legacy reader marker");
    }
    require(
        fs::is_regular_file(legacy_identity) &&
            !fs::exists(current_identity) &&
            private_file_identity(legacy_identity) == legacy_identity_inode,
        "read-only inspection changed the legacy reader identity namespace");

    // A cooperative reader already holding the old lock inode blocks migration.
    // The new name must not appear before exclusive ownership is proved.
    anonsync::SyncReplicaFilePayloadStore migrator(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "minimum-reader migrator");
    {
        ChildHeldFileLock shared_holder(
            legacy_identity, LOCK_SH, temporary.path(),
            "minimum-reader-migration-contention");
        require_lease_busy(
            [&] { (void)migrator.snapshot_or_throw(); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            "minimum-reader migration crossed a live legacy reader lease");
        require(
            fs::is_regular_file(legacy_identity) &&
                !fs::exists(current_identity),
            "contended minimum-reader migration published the new name");
        shared_holder.release_and_wait_or_fail();
    }

    // Exact stale metadata and a syntactically valid Prepared record still
    // cannot bypass the mandatory pre-rename byte proof. Failure leaves the old
    // name and exact lock inode in place, so repair/retry is deterministic.
    require_integrity_error(
        [&] { (void)migrator.snapshot_or_throw(); }, expected_digest,
        observed_digest, false,
        "minimum-reader migration trusted stale restart metadata");
    require(
        fs::is_regular_file(legacy_identity) &&
            !fs::exists(current_identity) &&
            private_file_identity(legacy_identity) == legacy_identity_inode,
        "failed minimum-reader byte proof changed the identity generation");

    overwrite_private_file(payload_path, good_payload);
    const auto migrated = migrator.snapshot_or_throw();
    require(
        !fs::exists(legacy_identity) && fs::is_regular_file(current_identity) &&
            private_file_identity(current_identity) == legacy_identity_inode,
        "minimum-reader migration did not preserve the exact lock inode");
    require(
        migrated.entry_count() == 1U &&
            migrated.scan_hashed_entry_count() == 0U &&
            migrated.scan_hashed_bytes() == 0U &&
            migrated.scan_process_reused_entry_count() == 1U &&
            migrated.scan_process_reused_bytes() == good_payload.size() &&
            migrated.scan_durable_reused_entry_count() == 0U &&
            migrated.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::Advanced &&
            migrated.scrub_report().hashed_bytes == 0U &&
            migrated.scrub_report().touched_entry_count == 0U &&
            migrated.scrub_report().completed_entry_count == 1U &&
            migrated.scrub_report().reverified_active_completed &&
            migrated.copy_payload_for_operation_or_throw(
                file_operation(folder, good_payload)) == good_payload,
        "post-migration snapshot or scrub repeated or weakened the cold byte proof");

    // The ordinary post-migration checkpoint must be rebound to the renamed
    // identity observation. A fresh owner can then reuse it, while an old reader
    // sees neither its expected lock-anchor name nor a namespace it understands.
    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "minimum-reader restarted owner");
        const auto restart = restarted.snapshot_or_throw();
        require(
            restart.scan_hashed_entry_count() == 0U &&
                restart.scan_process_reused_entry_count() == 0U &&
                restart.scan_durable_reused_entry_count() == 1U &&
                restart.scan_durable_reused_bytes() == good_payload.size(),
            "post-migration durable checkpoint was not rebound to the new identity");
    }
}

void test_minimum_reader_migration_rebuilds_damaged_scrub_state_once() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root(
        "minimum-reader-damaged-state-migration");
    const std::string folder =
        "folder-minimum-reader-damaged-state-migration";
    const std::string payload =
        "minimum reader migration carries damaged-state proof";
    const std::string digest = anonsync::sha256_hex(payload);

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 4096U;
    limits.max_indexed_bytes = 16384U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 1024U * 1024U;
    limits.max_scrub_bytes_per_attempt = 0U;
    limits.max_scrub_entries_per_attempt = 0U;
    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "minimum-reader damaged-state publisher");
        require(
            publisher.put_payload_or_throw(payload).content_sha256 == digest,
            "minimum-reader damaged-state fixture did not publish payload");
    }

    const fs::path current_identity =
        root / std::string(kStandaloneIdentityCurrent);
    const fs::path legacy_identity =
        root / std::string(kStandaloneIdentityLegacyReader);
    const fs::path scrub_state_path =
        root / std::string(
                   anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    rename_private_file_and_sync_directory(
        current_identity, legacy_identity,
        "minimum-reader damaged-state legacy fixture");
    const auto legacy_inode = private_file_identity(legacy_identity);
    write_private_file(
        scrub_state_path,
        std::string(
            static_cast<std::size_t>(
                anonsync::sync_replica_file_payload_scrub_state_exact_bytes()),
            'Z'));

    anonsync::SyncReplicaFilePayloadStore migrator(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "minimum-reader damaged-state migrator");
    const auto migrated = migrator.snapshot_or_throw();
    require(
        fs::is_regular_file(current_identity) &&
            !fs::exists(legacy_identity) &&
            private_file_identity(current_identity) == legacy_inode &&
            migrated.entry_count() == 1U &&
            migrated.scan_hashed_entry_count() == 0U &&
            migrated.scan_process_reused_entry_count() == 1U &&
            migrated.scan_process_reused_bytes() == payload.size() &&
            migrated.scan_durable_reused_entry_count() == 0U &&
            migrated.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    Disabled &&
            !migrated.scrub_report().state_rebuilt &&
            migrated.copy_payload_for_operation_or_throw(
                file_operation(folder, payload)) == payload,
        "minimum-reader migration repeated the cold proof after rebuilding damaged state");
    const auto rebuilt = read_scrub_state_or_fail(
        root, limits.max_payload_bytes,
        "minimum-reader migrated damaged scrub state");
    require(
        rebuilt.disposition ==
                anonsync::SyncReplicaFilePayloadScrubStateDisposition::Idle &&
            rebuilt.active_content_sha256.empty(),
        "minimum-reader migration did not bind canonical state to the renamed identity");
}

void test_prepared_scrub_state_forces_restart_reproof_before_blocked_optional_attempt() {
    TemporaryDirectory temporary;
    const MetadataHiddenCorruptionFixture fixture =
        make_metadata_hidden_corruption_fixture(temporary, 9000U);
    const fs::path identity_path =
        fixture.root / std::string(kStandaloneIdentityCurrent);
    const fs::path state_path =
        fixture.root /
        std::string(anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    const fs::path payload_path = fixture.root / fixture.expected_digest;

    auto prepared =
        anonsync::initial_sync_replica_file_payload_scrub_state_or_throw(
            anonsync::sha256_hex(read_file_bytes(identity_path)),
            private_file_metadata(
                identity_path, "prepared-restart identity metadata"),
            "prepared-restart state");
    prepared.disposition =
        anonsync::SyncReplicaFilePayloadScrubStateDisposition::Prepared;
    prepared.active_content_sha256 = fixture.expected_digest;
    prepared.active_metadata = private_file_metadata(
        payload_path, "prepared-restart payload metadata");
    prepared.active_offset_bytes = 0U;
    prepared.active_hash = anonsync::ResumableSha256{}.checkpoint();
    prepared.observed_content_sha256.clear();
    write_private_file(
        state_path,
        anonsync::serialize_sync_replica_file_payload_scrub_state_or_throw(
            prepared, fixture.limits.max_payload_bytes,
            "prepared-restart state"));

    // Model a detector process that died after its write-ahead publication but
    // before it could publish terminal failure. A cooperative reader holds a
    // shared flock: the fresh owner can complete its ordinary shared scan, but
    // its optional exclusive scrub attempt is mechanically unavailable. The
    // scan itself must therefore reject the forged metadata checkpoint and
    // hash the active payload before returning any authority.
    ChildHeldFileLock shared_holder(
        identity_path, LOCK_SH, temporary.path(),
        "prepared-restart-fence");
    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            fixture.folder, fixture.root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            fixture.limits, "prepared-restart detector");
        require_integrity_error(
            [&] { (void)restarted.snapshot_or_throw(); },
            fixture.expected_digest, fixture.observed_digest, false,
            "durable Prepared intent did not force restart current-byte reproof");
    }
    require(
        read_scrub_state_or_fail(
            fixture.root, fixture.limits.max_payload_bytes,
            "prepared-restart retained state").disposition ==
            anonsync::SyncReplicaFilePayloadScrubStateDisposition::Prepared,
        "restart reproof mutated the write-ahead intent before optional scrub authority was available");
    shared_holder.release_and_wait_or_fail();
}

void test_allocation_failure_after_scrub_mismatch_remains_fail_closed() {
    TemporaryDirectory temporary;

    // First count the exact allocation-bearing successful alarm path for this
    // toolchain and standard library. The fixture hides changed bytes behind a
    // forged but metadata-exact restart record, so only the bounded scrub can
    // discover the mismatch.
    const MetadataHiddenCorruptionFixture baseline =
        make_metadata_hidden_corruption_fixture(temporary, 0U);
    anonsync::SyncReplicaFilePayloadStore baseline_detector(
        baseline.folder, baseline.root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        baseline.limits, "allocation-alarm detector");
    std::size_t successful_alarm_allocations = 0U;
    bool baseline_alarm = false;
    {
        AllocationArm arm(0U);
        try {
            (void)baseline_detector.snapshot_or_throw();
        } catch (
            const anonsync::SyncReplicaFilePayloadStoreIntegrityError& error) {
            baseline_alarm =
                error.expected_content_sha256() == baseline.expected_digest &&
                error.observed_content_sha256() == baseline.observed_digest &&
                error.failure_persisted();
        } catch (...) {
            arm.disarm();
            throw;
        }
        successful_alarm_allocations = arm.attempts();
        arm.disarm();
    }
    require(
        baseline_alarm && durable_scrub_failure_present(baseline),
        "allocation-alarm baseline did not reach the persisted mismatch cutpoint");
    require(
        successful_alarm_allocations >= 8U,
        "allocation-alarm path was unexpectedly allocation-free");

    // Sweep the allocation-bearing tail, which includes failure-record
    // serialization/publication and typed exception construction. A failure
    // before digest comparison may remain an optional deferral. Once current
    // bytes have mismatched, however, the fixed-width process witness must be
    // installed first and every later exception must escape.
    constexpr std::size_t kTailWindow = 48U;
    const std::size_t first_failpoint =
        successful_alarm_allocations > kTailWindow
            ? successful_alarm_allocations - kTailWindow + 1U
            : 1U;
    std::uint64_t post_detection_bad_allocations = 0U;
    std::size_t ordinal = 1U;
    for (std::size_t fail_at = first_failpoint;
         fail_at <= successful_alarm_allocations;
         ++fail_at, ++ordinal) {
        const MetadataHiddenCorruptionFixture fixture =
            make_metadata_hidden_corruption_fixture(temporary, ordinal);
        anonsync::SyncReplicaFilePayloadStore detector(
            fixture.folder, fixture.root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            fixture.limits, "allocation-alarm detector");

        bool returned_snapshot = false;
        bool bad_allocation = false;
        bool typed_alarm = false;
        std::optional<anonsync::SyncReplicaFilePayloadStoreSnapshot> returned;
        {
            AllocationArm arm(fail_at);
            try {
                returned.emplace(detector.snapshot_or_throw());
                returned_snapshot = true;
            } catch (const std::bad_alloc&) {
                bad_allocation = true;
            } catch (
                const anonsync::SyncReplicaFilePayloadStoreIntegrityError&) {
                typed_alarm = true;
            } catch (...) {
                arm.disarm();
                throw;
            }
            arm.disarm();
        }

        const bool durable_failure =
            durable_scrub_failure_present(fixture);
        bool returned_authority_revoked = false;
        if (returned_snapshot) {
            try {
                (void)returned->snapshot_digest();
            } catch (
                const anonsync::SyncReplicaFilePayloadStoreIntegrityError&) {
                returned_authority_revoked = true;
            }
        }
        require(
            !(returned_snapshot &&
              (durable_failure || returned_authority_revoked)),
            "a post-detection allocation failure was downgraded to an optional scrub result");
        if (bad_allocation && durable_failure) {
            ++post_detection_bad_allocations;
        }
        require(
            returned_snapshot || bad_allocation || typed_alarm,
            "allocation-alarm sweep lost its exact outcome");
    }
    require(
        post_detection_bad_allocations != 0U,
        "allocation-alarm sweep did not exercise a failure after the persisted mismatch cutpoint");
}

void test_scrub_defers_under_capacity_and_cooperative_contention() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-payload-scrub-deferral";
    const std::string payload = "scrub-deferral-payload";

    anonsync::SyncReplicaFilePayloadStoreLimits base_limits;
    base_limits.max_entries = 8U;
    base_limits.max_payload_bytes = 1024U;
    base_limits.max_indexed_bytes = 4096U;
    base_limits.max_transient_entries = 8U;
    base_limits.max_transient_bytes = 1024U * 1024U;

    const fs::path capacity_root =
        temporary.make_store_root("scrub-capacity-deferral");
    {
        anonsync::SyncReplicaFilePayloadStore bootstrap(
            folder, capacity_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            base_limits, "scrub-capacity bootstrap");
        (void)bootstrap.put_payload_or_throw(payload);
    }
    anonsync::SyncReplicaFilePayloadStoreLimits tight = base_limits;
    tight.max_transient_bytes =
        anonsync::sync_replica_file_payload_scrub_state_exact_bytes() - 1U;
    tight.max_scrub_bytes_per_attempt = 8U;
    tight.max_scrub_entries_per_attempt = 1U;
    const fs::path capacity_state =
        capacity_root / std::string(
                            anonsync::kSyncReplicaFilePayloadScrubStateBasename);

    anonsync::SyncReplicaFilePayloadStore inspector(
        folder, capacity_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        tight, "scrub-capacity forensic inspector");
    const auto inspected = inspector.snapshot_or_throw();
    require(
        inspected.entry_count() == 1U &&
            inspected.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::Disabled &&
            !fs::exists(capacity_state),
        "read-only inspection created scrub scheduling state");

    anonsync::SyncReplicaFilePayloadStore capacity_owner(
        folder, capacity_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        tight, "scrub-capacity reconciler");
    const auto capacity_snapshot = capacity_owner.snapshot_or_throw();
    require(
        capacity_snapshot.entry_count() == 1U &&
            capacity_snapshot.transient_entry_count() == 0U &&
            capacity_snapshot.scrub_report().disposition ==
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    DeferredTransientCapacity &&
            !fs::exists(capacity_state),
        "scrub state publication crossed the exact transient capacity fence");

    const fs::path lease_root =
        temporary.make_store_root("scrub-lease-deferral");
    anonsync::SyncReplicaFilePayloadStoreLimits enabled = base_limits;
    enabled.max_scrub_bytes_per_attempt = 8U;
    enabled.max_scrub_entries_per_attempt = 1U;
    anonsync::SyncReplicaFilePayloadStore lease_owner(
        folder, lease_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        enabled, "scrub-lease bootstrap");
    (void)lease_owner.put_payload_or_throw(payload);
    const fs::path marker =
        lease_root / std::string(kStandaloneIdentityCurrent);
    {
        ChildHeldFileLock observer(
            marker, LOCK_SH, temporary.path(), "scrub-shared-observer");
        const auto deferred = lease_owner.snapshot_or_throw();
        require(
            deferred.entry_count() == 1U &&
                deferred.scrub_report().disposition ==
                    anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                        DeferredLeaseBusy,
            "cooperative shared observer did not defer the exclusive scrub attempt");
        observer.release_and_wait_or_fail();
    }
    require(
        lease_owner.snapshot_or_throw().scrub_report().disposition ==
            anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                DeferredBySchedule,
        "failed scrub attempt bypassed the same-process retry throttle");
    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, lease_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        enabled, "scrub-lease fresh owner");
    require(
        restarted.snapshot_or_throw().scrub_report().disposition ==
            anonsync::SyncReplicaFilePayloadStoreScrubDisposition::Advanced,
        "fresh owner did not receive one immediate bounded scrub attempt");
}

void test_publication_restart_and_exact_lookup() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("restart");
    const std::string folder = "folder-durable-payload-store";
    const std::string alpha("alpha\0payload", 13U);
    const std::string beta = "beta-payload";

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "payload store restart fixture");
    const auto alpha_insert = store.put_payload_or_throw(alpha);
    require(
        alpha_insert.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted &&
            alpha_insert.content_sha256 == anonsync::sha256_hex(alpha) &&
            alpha_insert.size_bytes == alpha.size(),
        "first payload publication did not return exact inserted identity");
    const auto alpha_duplicate = store.put_payload_or_throw(alpha);
    require(
        alpha_duplicate.disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::
                    AlreadyPresent &&
            alpha_duplicate.content_sha256 == alpha_insert.content_sha256,
        "exact duplicate payload did not reconcile idempotently");
    require(
        store.put_payload_or_throw(beta).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "second distinct payload was not published");

    auto snapshot = store.snapshot_or_throw();
    require(snapshot.active() && snapshot.folder_id() == folder &&
                snapshot.root_path() == root && snapshot.entry_count() == 2U &&
                snapshot.indexed_bytes() == alpha.size() + beta.size() &&
                snapshot.transient_entry_count() == 0U &&
                snapshot.content_inventory().entry_count() == 2U,
            "durable snapshot did not freeze its exact bounded index");
    const std::string first_digest = snapshot.snapshot_digest();
    require(
        snapshot.payload_size_or_none(alpha_insert.content_sha256) ==
            alpha.size(),
        "durable snapshot size index lost an exact digest");
    require(
        snapshot.copy_payload_for_operation_or_throw(
            file_operation(folder, alpha)) == alpha,
        "descriptor-relative lookup did not return exact binary bytes");

    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "payload store restart observer");
    auto restarted_snapshot = restarted.snapshot_or_throw();
    require(restarted_snapshot.snapshot_digest() == first_digest &&
                restarted_snapshot.entry_count() == 2U &&
                restarted_snapshot.copy_payload_for_operation_or_throw(
                    file_operation(folder, beta)) == beta,
            "restart did not reconstruct the same canonical durable index");
    anonsync::SyncReplicaFilePayloadStore wrong_folder(
        "folder-durable-payload-other", root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "payload store wrong-folder observer");
    require_error(
        [&] { (void)wrong_folder.snapshot_or_throw(); },
        "identity marker conflicts with the requested folder",
        "restart configuration relabeled a durably bound payload root");

    auto wrong_size = file_operation(folder, alpha);
    ++wrong_size.size_bytes;
    require_error(
        [&] {
            (void)restarted_snapshot.copy_payload_for_operation_or_throw(
                wrong_size);
        },
        "indexed payload size disagrees",
        "declared-size mismatch escaped the durable index");

    auto moved = std::move(snapshot);
    require(moved.active() && !snapshot.active(),
            "move-only durable snapshot did not transfer exclusive root authority");
    require_error(
        [&] { snapshot.preflight_or_throw("moved snapshot proof"); },
        "inactive",
        "moved-from durable snapshot retained authority");
}

void test_namespace_policy_and_limits() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-durable-payload-policy";

    {
        const fs::path root = temporary.make_store_root("unexpected");
        write_private_file(root / "operator-note", "not payload authority");
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "unexpected payload-root entry",
            "unknown namespace entry was silently treated as payload state");
        require(std::distance(fs::directory_iterator(root),
                              fs::directory_iterator()) == 1,
                "failed bootstrap minted identity into a hostile namespace");
    }
    {
        const fs::path root = temporary.make_store_root("preseeded");
        const std::string payload = "preseeded-valid-payload";
        write_private_file(root / anonsync::sha256_hex(payload), payload);
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        const auto snapshot = store.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U,
            "clean pre-existing content was absent from the adopted index");
        require(
            snapshot.copy_payload_for_operation_or_throw(
                file_operation(folder, payload)) == payload,
            "adopted pre-existing payload bytes were not exactly readable");
        require(
            std::distance(fs::directory_iterator(root),
                          fs::directory_iterator()) == 3,
            "clean pre-existing content did not receive its marker and restart-verification checkpoint");
    }
    {
        const fs::path root = temporary.make_store_root("corrupt");
        const std::string expected = "expected-content";
        write_private_file(root / anonsync::sha256_hex(expected), "different");
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "do not match digest basename",
            "digest filename authorized different bytes");
    }
    {
        const fs::path root = temporary.make_store_root("mode");
        const std::string payload = "wrong-mode";
        const fs::path path = root / anonsync::sha256_hex(payload);
        write_private_file(path, payload);
        if (::chmod(path.c_str(), 0640) != 0) fail("chmod fixture failed");
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "exact mode 0600",
            "group-readable payload file entered immutable authority");
    }
    {
        const fs::path root = temporary.make_store_root("hardlink");
        const std::string payload = "hardlink-payload";
        const fs::path first = root / anonsync::sha256_hex(payload);
        const fs::path second = root / anonsync::sha256_hex("other-name");
        write_private_file(first, payload);
        if (::link(first.c_str(), second.c_str()) != 0) {
            fail("hard-link fixture creation failed");
        }
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "single-link",
            "multiply-linked payload retained alias authority");
    }
    {
        const fs::path root = temporary.make_store_root("symlink");
        const std::string payload = "symlink-payload";
        const std::string digest = anonsync::sha256_hex(payload);
        const fs::path outside = root.parent_path() / "symlink-target";
        write_private_file(outside, payload);
        if (::symlink("../symlink-target", (root / digest).c_str()) != 0) {
            fail("symbolic-link fixture creation failed");
        }
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "symlink",
            "symbolic-link payload entered durable content authority");
    }
    {
        const fs::path root = temporary.make_store_root("residue");
        const std::string residue =
            ".anonsync-publish-v1-0123456789abcdef-"
            "1111111111111111-2222222222222222.tmp";
        require(
            anonsync::sync_atomic_file_publication_temp_basename_is_exact(
                residue) &&
                !anonsync::sync_atomic_file_publication_temp_basename_is_exact(
                    ".anonsync-publish-v1-0123456789abcdeF-"
                    "1111111111111111-2222222222222222.tmp"),
            "payload store and atomic publisher disagreed on private residue names");
        write_private_file(root / residue, "orphaned-private-temp");
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        const auto snapshot = store.snapshot_or_throw();
        require(snapshot.entry_count() == 0U &&
                    snapshot.transient_entry_count() == 1U &&
                    snapshot.transient_bytes() ==
                        std::string("orphaned-private-temp").size(),
                "exact private publication residue was not bounded separately");
    }
    {
        const fs::path root = temporary.make_store_root("residue-symlink");
        const std::string residue =
            ".anonsync-publish-v1-aaaaaaaaaaaaaaaa-"
            "bbbbbbbbbbbbbbbb-cccccccccccccccc.tmp";
        const fs::path outside = root.parent_path() / "residue-target";
        write_private_file(outside, "target");
        if (::symlink("../residue-target", (root / residue).c_str()) != 0) {
            fail("residue symbolic-link fixture creation failed");
        }
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "symlink",
            "publication-shaped symbolic link was ignored as trusted residue");
    }

    anonsync::SyncReplicaFilePayloadStoreLimits invalid{};
    invalid.max_entries = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "entry limit is invalid",
        "zero durable payload entry limit was accepted");
    invalid = {};
    invalid.max_payload_bytes = invalid.max_indexed_bytes + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "byte limits are invalid",
        "inverted durable payload byte limits were accepted");
    invalid = {};
    invalid.max_transient_entries =
        anonsync::kSyncReplicaFilePayloadStoreMaxTransientEntries + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "transient-entry limit is invalid",
        "unbounded publication residue limit was accepted");
    invalid = {};
    invalid.max_transient_bytes = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "transient-byte limit is invalid",
        "zero publication-residue byte limit was accepted");
    invalid = {};
    invalid.max_scrub_bytes_per_attempt = 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "scrub limits are invalid",
        "byte-only scrub scheduling was accepted without an entry bound");
    invalid = {};
    invalid.max_scrub_entries_per_attempt = 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "scrub limits are invalid",
        "entry-only scrub scheduling was accepted without a byte bound");
    invalid = {};
    invalid.max_scrub_bytes_per_attempt = invalid.max_indexed_bytes + 1U;
    invalid.max_scrub_entries_per_attempt = 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "scrub limits are invalid",
        "one scrub attempt crossed the aggregate indexed-byte ceiling");
    invalid = {};
    invalid.max_scrub_bytes_per_attempt = 1U;
    invalid.max_scrub_entries_per_attempt = invalid.max_entries + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "scrub limits are invalid",
        "one scrub attempt crossed the durable entry ceiling");
    invalid = {};
    invalid.max_payload_bytes = anonsync::kSha256MaximumMessageBytes + 1U;
    invalid.max_indexed_bytes = invalid.max_payload_bytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_store_limits_or_throw(
                invalid);
        },
        "byte limits are invalid",
        "payload extent beyond SHA-256's byte-aligned message ceiling was accepted");

    {
        const fs::path root = temporary.make_store_root("residue-byte-budget");
        const std::string residue =
            ".anonsync-publish-v1-dddddddddddddddd-"
            "eeeeeeeeeeeeeeee-ffffffffffffffff.tmp";
        write_private_file(root / residue, "12345");
        anonsync::SyncReplicaFilePayloadStoreLimits limits;
        limits.max_transient_bytes = 4U;
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits);
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "publication residue bytes exceed configured budget",
            "publication residue crossed its aggregate byte budget");
    }
    {
        const fs::path root = temporary.make_store_root("fifo");
        const fs::path fifo = root / std::string(64U, 'a');
        if (::mkfifo(fifo.c_str(), 0600) != 0) {
            fail("FIFO fixture creation failed");
        }
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
        const auto started = std::chrono::steady_clock::now();
        require_error(
            [&] { (void)store.snapshot_or_throw(); },
            "not a regular file",
            "digest-shaped FIFO entered durable content authority");
        const auto elapsed = std::chrono::steady_clock::now() - started;
        require(elapsed < std::chrono::seconds(1),
                "digest-shaped FIFO blocked a bounded namespace scan");
    }
    {
        const fs::path root = temporary.make_store_root("capacity");
        anonsync::SyncReplicaFilePayloadStoreLimits limits;
        limits.max_entries = 1U;
        limits.max_payload_bytes = 4U;
        limits.max_indexed_bytes = 4U;
        limits.max_transient_entries = 1U;
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits);
        require(
            store.put_payload_or_throw("1234").disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "capacity fixture did not fill its exact durable budget");
        require_error(
            [&] { (void)store.put_payload_or_throw("x"); },
            "entry count is at configured capacity",
            "durable payload store crossed its entry capacity");
        require_error(
            [&] { (void)store.put_payload_or_throw("12345"); },
            "exceeds configured byte budget",
            "durable payload store accepted an oversized payload");
    }
}

void test_root_rebind_and_post_index_mutation_fail_closed() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("rebind");
    const fs::path displaced = root.string() + ".displaced";
    const std::string folder = "folder-durable-payload-rebind";
    const std::string payload = "rebind-payload";

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
    (void)store.put_payload_or_throw(payload);
    auto snapshot = store.snapshot_or_throw();
    fs::rename(root, displaced);
    fs::create_directory(root);
    if (::chmod(root.c_str(), 0700) != 0) fail("replacement chmod failed");
    require_error(
        [&] { snapshot.preflight_or_throw("rebound durable payload root"); },
        "no longer names the retained directory",
        "path rebind redirected a retained durable payload snapshot");

    const fs::path mutation_root = temporary.make_store_root("mutation");
    anonsync::SyncReplicaFilePayloadStore mutation_store(
        folder, mutation_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
    const auto result = mutation_store.put_payload_or_throw(payload);
    auto mutation_snapshot = mutation_store.snapshot_or_throw();
    if (::unlink((mutation_root / result.content_sha256).c_str()) != 0) {
        fail("could not remove indexed payload fixture");
    }
    require_error(
        [&] {
            (void)mutation_snapshot.copy_payload_for_operation_or_throw(
                file_operation(folder, payload));
        },
        "inspection failed",
        "post-index deletion returned stale or invented payload bytes");

    const fs::path in_place_root =
        temporary.make_store_root("in-place-mutation");
    anonsync::SyncReplicaFilePayloadStore in_place_store(
        folder, in_place_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing);
    const auto in_place_result = in_place_store.put_payload_or_throw(payload);
    auto in_place_snapshot = in_place_store.snapshot_or_throw();
    int descriptor = ::open(
        (in_place_root / in_place_result.content_sha256).c_str(), O_WRONLY);
    if (descriptor < 0) fail("could not open indexed payload for mutation");
    const char replacement = payload.front() == 'x' ? 'y' : 'x';
    ssize_t written;
    do {
        written = ::pwrite(descriptor, &replacement, 1U, 0);
    } while (written < 0 && errno == EINTR);
    if (written != 1 || ::fsync(descriptor) != 0 || ::close(descriptor) != 0) {
        fail("could not complete indexed payload mutation");
    }
    require_error(
        [&] {
            (void)in_place_snapshot.copy_payload_range_for_operation_or_throw(
                file_operation(folder, payload), 1U, 2U,
                "post-index bounded range");
        },
        "changed after indexing",
        "post-index mutation outside the selected range escaped inode/time reproof");
}

void test_cross_process_store_lease_serializes_capacity() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("writer-lease");
    const std::string folder = "folder-durable-payload-writer-lease";
    const std::string first = "first-lease-payload";
    const std::string second = "second-lease-payload";
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 1U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 64U;
    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "payload store writer lease fixture");

    // The first observation performs clean bootstrap of the exact immutable
    // marker used as the cooperative lock anchor.
    const auto bootstrap = store.snapshot_or_throw();
    const auto repeated = store.snapshot_or_throw();
    require(bootstrap.entry_count() == 0U &&
                repeated.entry_count() == 0U &&
                bootstrap.snapshot_digest() == repeated.snapshot_digest(),
            "repeated scans inherited a consumed directory-stream cursor");
    const fs::path marker =
        root / std::string(kStandaloneIdentityCurrent);
    std::ifstream marker_stream(marker, std::ios::binary);
    const std::string marker_bytes{
        std::istreambuf_iterator<char>(marker_stream),
        std::istreambuf_iterator<char>()};
    require(
        marker_stream.is_open() &&
        marker_bytes ==
            "anonsync:sync-replica-file-payload-store-identity:v2\n" +
                folder + "\n" +
                "anonsync:sync-replica-file-payload-store-flock-lease:v1\n",
        "current identity marker did not bind the exact lease generation");

    {
        ChildHeldFileLock writer(
            marker, LOCK_EX, temporary.path(), "exclusive-writer");
        require_lease_busy(
            [&] { (void)store.snapshot_or_throw(); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::SharedObservation,
            "a cross-process writer did not exclude a concurrent store scan");
        require_lease_busy(
            [&] { (void)store.put_payload_or_throw(first); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            "a cross-process writer did not exclude a second capacity spend");
        require(!fs::exists(root / anonsync::sha256_hex(first)),
                "busy writer authority mutated the payload namespace");
        writer.release_and_wait_or_fail();
    }

    require(
        store.put_payload_or_throw(first).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "released cross-process writer lease did not permit exact publication");

    {
        ChildHeldFileLock observer(
            marker, LOCK_SH, temporary.path(), "shared-observer");
        require(store.snapshot_or_throw().entry_count() == 1U,
                "cooperative shared observations did not coexist");
        require_lease_busy(
            [&] { (void)store.put_payload_or_throw(second); },
            anonsync::SyncReplicaFilePayloadStoreLeaseMode::ExclusiveMutation,
            "a shared observer did not exclude aggregate-budget mutation");
        observer.release_and_wait_or_fail();
    }

    require_error(
        [&] { (void)store.put_payload_or_throw(second); },
        "entry count is at configured capacity",
        "serialized writers crossed the exact aggregate entry budget");
    require(store.snapshot_or_throw().entry_count() == 1U &&
                !fs::exists(root / anonsync::sha256_hex(second)),
            "failed serialized capacity spend left unauthorized payload bytes");
}


void test_staged_prefix_hot_path_accepts_verification_index() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-prefix-verification-index";
    const fs::path receiver_root =
        temporary.make_store_root("prefix-index-receiver");

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 256U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 4096U;

    const std::string checkpoint_seed = "checkpoint-seed";
    const std::string payload = "abcdefgh";
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path verification_index =
        receiver_root /
        std::string(
            anonsync::kSyncReplicaFilePayloadVerificationIndexBasename);
    {
        anonsync::SyncReplicaFilePayloadStore receiver(
            folder, receiver_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            limits, "prefix verification-index receiver");

        require(
            receiver.put_payload_or_throw(checkpoint_seed).disposition ==
                anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
            "prefix verification-index fixture did not publish its seed payload");
        require(
            fs::is_regular_file(verification_index),
            "payload insertion did not publish the durable verification index");

        const std::string first_range = payload.substr(0U, 4U);
        const auto staged = receiver.stage_payload_prefix_or_throw(
            digest, payload.size(), 0U, anonsync::sha256_hex(first_range),
            first_range);
        require(
            staged.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
                staged.next_offset_bytes == first_range.size() &&
                staged.accepted_range_bytes == first_range.size(),
            "staged-prefix hot path rejected or misread the internal verification index");

        const auto snapshot = receiver.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.transient_entry_count() == 1U &&
                snapshot.transient_bytes() == first_range.size(),
            "staged-prefix hot path did not preserve payload and prefix namespace accounting");

        const std::string final_range = payload.substr(first_range.size());
        const auto completed = receiver.stage_payload_prefix_or_throw(
            digest, payload.size(), first_range.size(),
            anonsync::sha256_hex(final_range), final_range);
        require(
            completed.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedInserted &&
                completed.next_offset_bytes == payload.size(),
            "staged-prefix completion did not publish the exact whole payload");
    }

    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, receiver_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "prefix verification-index restarted receiver");
    const auto restart_snapshot = restarted.snapshot_or_throw();
    require(
        restart_snapshot.entry_count() == 2U &&
            restart_snapshot.indexed_bytes() ==
                checkpoint_seed.size() + payload.size() &&
            restart_snapshot.scan_hashed_entry_count() == 0U &&
            restart_snapshot.scan_reused_entry_count() == 2U &&
            restart_snapshot.scan_reused_bytes() ==
                checkpoint_seed.size() + payload.size(),
        "graceful prefix completion did not checkpoint post-rename metadata for restart reuse");
    require_reuse_partition(
        restart_snapshot, 0U, 0U, 2U,
        checkpoint_seed.size() + payload.size(),
        "graceful prefix completion did not expose durable restart-reuse provenance");
}

void test_transient_namespace_digest_binds_restart_obligation_identity() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-transient-namespace-witness";
    const fs::path root =
        temporary.make_store_root("transient-namespace-witness");

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 256U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 128U;

    const std::string first_target = "abcdefgh";
    const std::string first_digest = anonsync::sha256_hex(first_target);
    const std::string prefix_bytes = first_target.substr(0U, 4U);
    std::string first_namespace_digest;
    std::string first_snapshot_digest;
    fs::path first_prefix_path;
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "transient namespace witness store");
        const auto staged = store.stage_payload_prefix_or_throw(
            first_digest, first_target.size(), 0U,
            anonsync::sha256_hex(prefix_bytes), prefix_bytes);
        require(
            staged.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        Progress &&
                staged.next_offset_bytes == prefix_bytes.size(),
            "transient namespace witness fixture did not retain one prefix");

        const auto first = store.snapshot_or_throw();
        first_namespace_digest = first.transient_namespace_digest();
        first_snapshot_digest = first.snapshot_digest();
        require(
            first.transient_entry_count() == 1U &&
                first.transient_bytes() == prefix_bytes.size() &&
                first.transient_reserved_bytes() == first_target.size() &&
                anonsync::is_lowercase_sha256_hex(first_namespace_digest),
            "transient namespace witness omitted exact prefix capacity evidence");

        for (const fs::directory_entry& entry : fs::directory_iterator(root)) {
            const std::string basename = entry.path().filename().string();
            if (basename.starts_with(".anonsync-payload-prefix-v1-")) {
                require(first_prefix_path.empty(),
                        "transient namespace witness fixture found competing prefixes");
                first_prefix_path = entry.path();
            }
        }
        require(!first_prefix_path.empty(),
                "transient namespace witness fixture lost its canonical prefix");
    }

    const ExpectedTransientPrefix first_expected{
        first_prefix_path.filename().string(), first_digest,
        first_target.size(), prefix_bytes.size(), prefix_bytes.size(),
        private_file_metadata(
            first_prefix_path, "first transient prefix metadata")};
    require(
        first_namespace_digest ==
            expected_transient_namespace_digest(&first_expected, nullptr),
        "transient namespace digest did not match its independent canonical prefix framing");

    // Replacing the exact basename with the same bytes preserves every logical
    // field and aggregate. The witness must still change because the rooted
    // restart obligation now names a different inode observation.
    const auto first_identity = private_file_identity(first_prefix_path);
    replace_private_file(first_prefix_path, prefix_bytes);
    const auto replaced_identity = private_file_identity(first_prefix_path);
    require(
        replaced_identity != first_identity,
        "same-name transient replacement fixture did not change inode identity");

    std::string replaced_namespace_digest;
    std::string replaced_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "transient namespace replacement store");
        const auto replaced = reopened.snapshot_or_throw();
        replaced_namespace_digest = replaced.transient_namespace_digest();
        replaced_snapshot_digest = replaced.snapshot_digest();
        require(
            replaced.transient_entry_count() == 1U &&
                replaced.transient_bytes() == prefix_bytes.size() &&
                replaced.transient_reserved_bytes() == first_target.size(),
            "same-name transient replacement changed aggregate accounting");
    }
    const ExpectedTransientPrefix replaced_expected{
        first_prefix_path.filename().string(), first_digest,
        first_target.size(), prefix_bytes.size(), prefix_bytes.size(),
        private_file_metadata(
            first_prefix_path, "replaced transient prefix metadata")};
    require(
        replaced_namespace_digest ==
                expected_transient_namespace_digest(
                    &replaced_expected, nullptr) &&
            replaced_namespace_digest != first_namespace_digest &&
            replaced_snapshot_digest != first_snapshot_digest,
        "same-name same-size transient inode replacement retained stale cutpoint identity");

    // First keep count, physical bytes, committed extent, and whole-payload
    // reservation unchanged while changing only the syntactically admitted
    // target identity. Aggregate count/byte cutpoints cannot distinguish these
    // restart obligations.
    const std::string second_target = "ijklmnop";
    const std::string second_digest = anonsync::sha256_hex(second_target);
    const fs::path second_prefix_path =
        root /
        (".anonsync-payload-prefix-v1-" + second_digest + "-" +
         std::to_string(second_target.size()) + "-" +
         std::to_string(prefix_bytes.size()));
    rename_private_file_and_sync_directory(
        first_prefix_path, second_prefix_path,
        "transient namespace revised target obligation");

    std::string second_namespace_digest;
    std::string second_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "transient namespace target witness store");
        const auto second = reopened.snapshot_or_throw();
        second_namespace_digest = second.transient_namespace_digest();
        second_snapshot_digest = second.snapshot_digest();
        require(
            second.transient_entry_count() == 1U &&
                second.transient_bytes() == prefix_bytes.size() &&
                second.transient_reserved_bytes() == first_target.size(),
            "same-reservation transient target change altered aggregate accounting");
    }
    const ExpectedTransientPrefix second_expected{
        second_prefix_path.filename().string(), second_digest,
        second_target.size(), prefix_bytes.size(), prefix_bytes.size(),
        private_file_metadata(
            second_prefix_path, "second transient prefix metadata")};
    require(
        second_namespace_digest ==
                expected_transient_namespace_digest(&second_expected, nullptr) &&
            second_namespace_digest != replaced_namespace_digest &&
            second_snapshot_digest != replaced_snapshot_digest,
        "same-count same-byte same-reservation obligations still collide at the snapshot cutpoint");

    // Then preserve target digest, physical bytes, and committed extent while
    // changing only the declared completion reservation. A malformed or
    // interrupted restart obligation is still namespace authority that a later
    // collector must bind exactly rather than normalize away.
    constexpr std::uint64_t expanded_reservation = 16U;
    const fs::path expanded_prefix_path =
        root /
        (".anonsync-payload-prefix-v1-" + second_digest + "-" +
         std::to_string(expanded_reservation) + "-" +
         std::to_string(prefix_bytes.size()));
    rename_private_file_and_sync_directory(
        second_prefix_path, expanded_prefix_path,
        "transient namespace revised reservation obligation");

    std::string expanded_namespace_digest;
    std::string expanded_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "transient namespace reservation witness store");
        const auto expanded = reopened.snapshot_or_throw();
        expanded_namespace_digest = expanded.transient_namespace_digest();
        expanded_snapshot_digest = expanded.snapshot_digest();
        require(
            expanded.transient_entry_count() == 1U &&
                expanded.transient_bytes() == prefix_bytes.size() &&
                expanded.transient_reserved_bytes() == expanded_reservation,
            "reservation-only transient change was not reflected in exact capacity accounting");
    }
    const ExpectedTransientPrefix expanded_expected{
        expanded_prefix_path.filename().string(), second_digest,
        expanded_reservation, prefix_bytes.size(), prefix_bytes.size(),
        private_file_metadata(
            expanded_prefix_path, "expanded transient prefix metadata")};
    require(
        expanded_namespace_digest == expected_transient_namespace_digest(
                                         &expanded_expected, nullptr) &&
            expanded_namespace_digest != second_namespace_digest &&
            expanded_snapshot_digest != second_snapshot_digest,
        "reservation-only transient drift retained the stale snapshot cutpoint");

    // Assembly residues use the same canonical one-frame metadata projection.
    // This explicit oracle prevents an accidental duplicate basename or
    // metadata frame from becoming a silently incompatible witness format.
    const std::string assembly_bytes = "assembly";
    const std::string assembly_basename =
        ".anonsync-payload-assemble-v1-" +
        anonsync::sha256_hex(assembly_bytes);
    const fs::path assembly_path = root / assembly_basename;
    write_private_file(assembly_path, assembly_bytes);
    std::string assembly_namespace_digest;
    std::string assembly_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "transient assembly witness store");
        const auto with_assembly = reopened.snapshot_or_throw();
        assembly_namespace_digest = with_assembly.transient_namespace_digest();
        assembly_snapshot_digest = with_assembly.snapshot_digest();
        require(
            with_assembly.transient_entry_count() == 2U &&
                with_assembly.transient_bytes() ==
                    prefix_bytes.size() + assembly_bytes.size() &&
                with_assembly.transient_reserved_bytes() ==
                    expanded_reservation + assembly_bytes.size(),
            "assembly residue was not included in exact transient accounting");
    }
    ExpectedTransientAssembly assembly_expected{
        assembly_basename, assembly_bytes.size(),
        private_file_metadata(assembly_path, "transient assembly metadata")};
    require(
        assembly_namespace_digest == expected_transient_namespace_digest(
                                         &expanded_expected,
                                         &assembly_expected) &&
            assembly_namespace_digest != expanded_namespace_digest &&
            assembly_snapshot_digest != expanded_snapshot_digest,
        "assembly residue did not use one canonical exact metadata frame");

    const auto first_assembly_identity = private_file_identity(assembly_path);
    replace_private_file(assembly_path, assembly_bytes);
    const auto replaced_assembly_identity =
        private_file_identity(assembly_path);
    require(
        replaced_assembly_identity != first_assembly_identity,
        "assembly replacement fixture did not change inode identity");

    std::string final_namespace_digest;
    std::string final_snapshot_digest;
    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "transient replaced assembly witness store");
        const auto final = reopened.snapshot_or_throw();
        final_namespace_digest = final.transient_namespace_digest();
        final_snapshot_digest = final.snapshot_digest();
    }
    assembly_expected.metadata = private_file_metadata(
        assembly_path, "replaced transient assembly metadata");
    require(
        final_namespace_digest == expected_transient_namespace_digest(
                                      &expanded_expected,
                                      &assembly_expected) &&
            final_namespace_digest != assembly_namespace_digest &&
            final_snapshot_digest != assembly_snapshot_digest,
        "same-name same-size assembly replacement retained stale cutpoint identity");

    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "transient namespace witness restarted store");
    const auto restart = restarted.snapshot_or_throw();
    require(
        restart.transient_namespace_digest() == final_namespace_digest &&
            restart.snapshot_digest() == final_snapshot_digest &&
            restart.transient_reserved_bytes() ==
                expanded_reservation + assembly_bytes.size(),
        "transient namespace witness was not canonical across owner restart");
}
void test_bounded_range_copy_durable_resume_and_residue_repair() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-durable-payload-range-resume";
    const fs::path source_root = temporary.make_store_root("range-source");
    const fs::path receiver_root = temporary.make_store_root("range-receiver");
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 256U;
    limits.max_transient_entries = 32U;
    limits.max_transient_bytes = 128U;

    const std::string payload = "abcdefghijklmnopqrstuvwxyz";
    const std::string digest = anonsync::sha256_hex(payload);
    const auto operation = file_operation(folder, payload);

    anonsync::SyncReplicaFilePayloadStore source(
        folder, source_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "range source payload store");
    require(
        source.put_payload_or_throw(payload).disposition ==
            anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
        "range source payload was not published");
    auto source_snapshot = source.snapshot_or_throw();
    const auto range0 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 0U, 7U, "range zero copy");
    const auto range1 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 7U, 7U, "range one copy");
    const auto range2 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 14U, 7U, "range two copy");
    const auto range3 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 21U, 7U, "range three copy");
    require(
        range0.bytes == "abcdefg" && range0.offset_bytes == 0U &&
            range1.bytes == "hijklmn" && range1.offset_bytes == 7U &&
            range2.bytes == "opqrstu" && range2.offset_bytes == 14U &&
            range3.bytes == "vwxyz" && range3.offset_bytes == 21U,
        "bounded range copies did not preserve exact offsets and bytes");
    require(
        range0.content_sha256 == digest &&
            range0.total_size_bytes == payload.size() &&
            range0.chunk_sha256 == anonsync::sha256_hex(range0.bytes) &&
            range3.chunk_sha256 == anonsync::sha256_hex(range3.bytes),
        "bounded range copies lost whole/chunk identity");

    const std::string exact_range_basename =
        ".anonsync-payload-range-v1-" + digest + "-0-" +
        range0.chunk_sha256;
    require(
        anonsync::sync_replica_file_payload_store_range_basename_is_exact(
            exact_range_basename),
        "exact staged range basename was not recognized");
    require(
        !anonsync::sync_replica_file_payload_store_range_basename_is_exact(
            ".anonsync-payload-range-v1-" + digest + "-00-" +
            range0.chunk_sha256),
        "noncanonical staged range offset was accepted");

    anonsync::SyncReplicaFilePayloadStore receiver(
        folder, receiver_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "range receiver payload store");
    require(receiver.snapshot_or_throw().entry_count() == 0U,
            "range receiver did not bootstrap empty");

    const fs::path stale_publication =
        receiver_root /
        ".anonsync-publish-v1-0000000000000001-0000000000000002-0000000000000003.tmp";
    write_private_file(stale_publication, "orphan");
    {
        const auto residue_snapshot = receiver.snapshot_or_throw();
        require(residue_snapshot.transient_entry_count() == 1U &&
                    residue_snapshot.transient_bytes() == 6U,
                "exact stale publication residue was not bounded as transient");
    }

    const auto first = receiver.stage_payload_range_or_throw(
        digest, payload.size(), range0.offset_bytes, range0.chunk_sha256,
        range0.bytes);
    require(
        first.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            first.next_offset_bytes == 7U &&
            first.accepted_range_bytes == 7U,
        "first staged range did not publish exact durable progress");
    require(!fs::exists(stale_publication),
            "exclusive store mutation did not repair exact stale publication residue");
    {
        const auto staged = receiver.snapshot_or_throw();
        require(staged.entry_count() == 0U &&
                    staged.transient_entry_count() == 1U &&
                    staged.transient_bytes() == 7U,
                "first durable range was not the receiver's sole transient state");
    }

    const auto second = receiver.stage_payload_range_or_throw(
        digest, payload.size(), range1.offset_bytes, range1.chunk_sha256,
        range1.bytes);
    require(
        second.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            second.next_offset_bytes == 14U &&
            second.accepted_range_bytes == 7U,
        "second staged range did not extend the exact prefix");

    // Reconstruct the store owner to prove progress is namespace-durable, not
    // an in-memory cursor. Replaying the first source range discovers the full
    // retained prefix and does not spend transient capacity twice.
    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, receiver_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "restarted range receiver payload store");
    const auto replay = restarted.stage_payload_range_or_throw(
        digest, payload.size(), range0.offset_bytes, range0.chunk_sha256,
        range0.bytes);
    require(
        replay.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            replay.next_offset_bytes == 14U &&
            replay.accepted_range_bytes == 0U,
        "restart replay did not recover the longer exact durable prefix");

    require_error(
        [&] {
            (void)restarted.stage_payload_range_or_throw(
                digest, payload.size(), range3.offset_bytes,
                range3.chunk_sha256, range3.bytes);
        },
        "next contiguous offset",
        "out-of-order staged range was accepted");
    const std::string conflict = "ABCDEFG";
    require_error(
        [&] {
            (void)restarted.stage_payload_range_or_throw(
                digest, payload.size(), 0U, anonsync::sha256_hex(conflict),
                conflict);
        },
        "conflicts at one offset",
        "competing staged bytes were accepted at an occupied offset");

    const auto third = restarted.stage_payload_range_or_throw(
        digest, payload.size(), range2.offset_bytes, range2.chunk_sha256,
        range2.bytes);
    require(
        third.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            third.next_offset_bytes == 21U,
        "third staged range did not extend the recovered prefix");
    const auto completed = restarted.stage_payload_range_or_throw(
        digest, payload.size(), range3.offset_bytes, range3.chunk_sha256,
        range3.bytes);
    require(
        completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::CompletedInserted &&
            completed.next_offset_bytes == payload.size() &&
            completed.accepted_range_bytes == range3.bytes.size(),
        "final range did not assemble and publish the whole payload");
    {
        const auto complete_snapshot = restarted.snapshot_or_throw();
        require(complete_snapshot.entry_count() == 1U &&
                    complete_snapshot.indexed_bytes() == payload.size() &&
                    complete_snapshot.transient_entry_count() == 0U &&
                    complete_snapshot.transient_bytes() == 0U,
                "completed staged payload left private range/assembly authority");
        require(
            complete_snapshot.copy_payload_for_operation_or_throw(
                operation, "completed range payload lookup") == payload,
            "completed staged payload bytes differ from the whole content identity");
    }
    const auto duplicate_complete = restarted.stage_payload_range_or_throw(
        digest, payload.size(), range3.offset_bytes, range3.chunk_sha256,
        range3.bytes);
    require(
        duplicate_complete.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedAlreadyPresent &&
            duplicate_complete.next_offset_bytes == payload.size() &&
            duplicate_complete.accepted_range_bytes == 0U,
        "completed payload replay did not converge without staging new bytes");
}

void test_single_prefix_owner_crash_tail_and_legacy_resume() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-durable-payload-prefix-owner";
    const fs::path source_root =
        temporary.make_store_root("prefix-source");
    const fs::path receiver_root =
        temporary.make_store_root("prefix-receiver");
    const fs::path legacy_root =
        temporary.make_store_root("prefix-legacy-receiver");
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 64U;
    limits.max_indexed_bytes = 256U;
    limits.max_transient_entries = 32U;
    limits.max_transient_bytes = 128U;

    const std::string payload = "abcdefghijklmnopqrstuvwxyz";
    const std::string digest = anonsync::sha256_hex(payload);
    const auto operation = file_operation(folder, payload);

    anonsync::SyncReplicaFilePayloadStore source(
        folder, source_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "prefix source payload store");
    (void)source.put_payload_or_throw(payload);
    auto source_snapshot = source.snapshot_or_throw();
    const auto range0 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 0U, 7U, "prefix range zero copy");
    const auto range1 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 7U, 7U, "prefix range one copy");
    const auto range2 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 14U, 7U, "prefix range two copy");
    const auto range3 =
        source_snapshot.copy_payload_range_for_operation_or_throw(
            operation, 21U, 7U, "prefix range three copy");

    const std::string prefix_base =
        ".anonsync-payload-prefix-v1-" + digest + "-";
    require(
        anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
            prefix_base + "26-0") &&
            anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                prefix_base + "26-7"),
        "canonical staged prefix basenames were not recognized");
    require(
        !anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
            prefix_base + "026-7") &&
            !anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                prefix_base + "26-07") &&
            !anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                prefix_base + "0-0") &&
            !anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                prefix_base + "26-27"),
        "noncanonical or impossible staged prefix basename was accepted");

    anonsync::SyncReplicaFilePayloadStore receiver(
        folder, receiver_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "prefix receiver payload store");
    require(receiver.snapshot_or_throw().entry_count() == 0U,
            "prefix receiver did not bootstrap empty");
    const auto first = receiver.stage_payload_prefix_or_throw(
        digest, payload.size(), range0.offset_bytes, range0.chunk_sha256,
        range0.bytes);
    require(
        first.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            first.next_offset_bytes == 7U &&
            first.accepted_range_bytes == 7U,
        "first prefix range did not commit its exact cutpoint");
    fs::path prefix_path = single_staged_prefix_or_fail(
        receiver_root, "first prefix range");
    require(prefix_path.filename() == prefix_base + "26-7" &&
                read_file_bytes(prefix_path) == range0.bytes,
            "first prefix owner did not bind its committed bytes in one file");
    {
        const auto staged = receiver.snapshot_or_throw();
        require(staged.entry_count() == 0U &&
                    staged.transient_entry_count() == 1U &&
                    staged.transient_bytes() == 7U,
                "first prefix range did not expose one physical transient file");
    }

    const auto second = receiver.stage_payload_prefix_or_throw(
        digest, payload.size(), range1.offset_bytes, range1.chunk_sha256,
        range1.bytes);
    require(
        second.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            second.next_offset_bytes == 14U &&
            second.accepted_range_bytes == 7U,
        "second prefix range did not advance its exact cutpoint");
    require(!fs::exists(prefix_path),
            "committed prefix rename left the older authority name behind");
    prefix_path = single_staged_prefix_or_fail(
        receiver_root, "second prefix range");
    require(prefix_path.filename() == prefix_base + "26-14" &&
                read_file_bytes(prefix_path) == range0.bytes + range1.bytes,
            "second range did not remain one exact durable prefix file");

    // Simulate the crash cutpoint after range bytes reached stable storage but
    // before the basename commit rename. The old basename remains the authority;
    // a fresh owner must discard the longer physical tail before any replay.
    append_uncommitted_prefix_tail_or_fail(
        prefix_path, 14U, "XXXXXXX");
    {
        const auto crash_tail = receiver.snapshot_or_throw();
        require(crash_tail.transient_entry_count() == 1U &&
                    crash_tail.transient_bytes() == 21U,
                "snapshot did not bound the physical uncommitted crash tail");
    }
    anonsync::SyncReplicaFilePayloadStore restarted(
        folder, receiver_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "restarted prefix receiver payload store");
    const auto replay = restarted.stage_payload_prefix_or_throw(
        digest, payload.size(), range0.offset_bytes, range0.chunk_sha256,
        range0.bytes);
    require(
        replay.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            replay.next_offset_bytes == 14U &&
            replay.accepted_range_bytes == 0U,
        "restart replay did not recover the basename-committed prefix");
    prefix_path = single_staged_prefix_or_fail(
        receiver_root, "recovered prefix range");
    require(prefix_path.filename() == prefix_base + "26-14" &&
                read_file_bytes(prefix_path) == range0.bytes + range1.bytes,
            "restart recovery retained bytes beyond the committed basename cutpoint");
    {
        const auto recovered = restarted.snapshot_or_throw();
        require(recovered.transient_entry_count() == 1U &&
                    recovered.transient_bytes() == 14U,
                "crash-tail recovery did not restore exact physical accounting");
    }

    require_error(
        [&] {
            (void)restarted.stage_payload_prefix_or_throw(
                digest, payload.size(), range3.offset_bytes,
                range3.chunk_sha256, range3.bytes);
        },
        "next contiguous offset",
        "prefix owner accepted a gap beyond its committed cutpoint");
    const std::string conflicting = "ABCDEFG";
    require_error(
        [&] {
            (void)restarted.stage_payload_prefix_or_throw(
                digest, payload.size(), 0U,
                anonsync::sha256_hex(conflicting), conflicting);
        },
        "conflicts with committed prefix",
        "prefix owner accepted conflicting replay bytes below its cutpoint");

    const auto third = restarted.stage_payload_prefix_or_throw(
        digest, payload.size(), range2.offset_bytes, range2.chunk_sha256,
        range2.bytes);
    require(third.next_offset_bytes == 21U &&
                third.accepted_range_bytes == 7U,
            "third prefix range did not advance after crash-tail recovery");
    const auto completed = restarted.stage_payload_prefix_or_throw(
        digest, payload.size(), range3.offset_bytes, range3.chunk_sha256,
        range3.bytes);
    require(
        completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted &&
            completed.next_offset_bytes == payload.size() &&
            completed.accepted_range_bytes == range3.bytes.size(),
        "complete prefix did not publish directly under the whole digest");
    {
        const auto complete = restarted.snapshot_or_throw();
        require(complete.entry_count() == 1U &&
                    complete.indexed_bytes() == payload.size() &&
                    complete.transient_entry_count() == 0U &&
                    complete.transient_bytes() == 0U &&
                    complete.copy_payload_for_operation_or_throw(
                        operation, "completed prefix payload lookup") == payload,
                "direct prefix publication left staging authority or wrong bytes");
    }
    const auto duplicate = restarted.stage_payload_prefix_or_throw(
        digest, payload.size(), range3.offset_bytes, range3.chunk_sha256,
        range3.bytes);
    require(
        duplicate.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedAlreadyPresent &&
            duplicate.accepted_range_bytes == 0U,
        "completed prefix replay created new transient work");

    // A rev0941 range-file transfer may exist at upgrade. The shipping API must
    // finish that exact durable owner rather than minting a competing prefix.
    anonsync::SyncReplicaFilePayloadStore legacy_receiver(
        folder, legacy_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "legacy range compatibility receiver");
    const auto legacy_first = legacy_receiver.stage_payload_range_or_throw(
        digest, payload.size(), range0.offset_bytes, range0.chunk_sha256,
        range0.bytes);
    const auto legacy_second = legacy_receiver.stage_payload_prefix_or_throw(
        digest, payload.size(), range1.offset_bytes, range1.chunk_sha256,
        range1.bytes);
    require(legacy_first.next_offset_bytes == 7U &&
                legacy_second.next_offset_bytes == 14U &&
                legacy_second.accepted_range_bytes == 7U,
            "shipping prefix API did not resume the rev0941 range owner");
    for (const fs::directory_entry& entry :
         fs::directory_iterator(legacy_root)) {
        require(
            !anonsync::sync_replica_file_payload_store_prefix_basename_is_exact(
                entry.path().filename().string()),
            "legacy resume minted a competing staged prefix owner");
    }
    (void)legacy_receiver.stage_payload_prefix_or_throw(
        digest, payload.size(), range2.offset_bytes, range2.chunk_sha256,
        range2.bytes);
    const auto legacy_completed =
        legacy_receiver.stage_payload_prefix_or_throw(
            digest, payload.size(), range3.offset_bytes, range3.chunk_sha256,
            range3.bytes);
    require(
        legacy_completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted &&
            legacy_receiver.snapshot_or_throw().transient_entry_count() == 0U,
        "rev0941 compatibility owner did not converge through the shipping API");

    // Physical accounting is operator-visible disk use; admission accounting
    // must reserve the whole declared payload so several short prefixes cannot
    // each assume they will later own the same completion capacity.
    const fs::path capacity_root =
        temporary.make_store_root("prefix-reservation-capacity");
    anonsync::SyncReplicaFilePayloadStoreLimits capacity_limits;
    capacity_limits.max_entries = 8U;
    capacity_limits.max_payload_bytes = 10U;
    capacity_limits.max_indexed_bytes = 64U;
    capacity_limits.max_transient_entries = 8U;
    capacity_limits.max_transient_bytes = 10U;
    anonsync::SyncReplicaFilePayloadStore capacity_receiver(
        folder, capacity_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        capacity_limits, "prefix reservation capacity receiver");
    const std::string capacity_payload = "0123456789";
    const std::string capacity_chunk = capacity_payload.substr(0U, 4U);
    const auto reserved = capacity_receiver.stage_payload_prefix_or_throw(
        anonsync::sha256_hex(capacity_payload), capacity_payload.size(), 0U,
        anonsync::sha256_hex(capacity_chunk), capacity_chunk);
    const auto capacity_snapshot = capacity_receiver.snapshot_or_throw();
    require(
        reserved.next_offset_bytes == capacity_chunk.size() &&
            capacity_snapshot.transient_entry_count() == 1U &&
            capacity_snapshot.transient_bytes() == capacity_chunk.size(),
        "prefix reservation test did not expose exact physical bytes");
    const std::string second_payload = "x";
    require_error(
        [&] {
            (void)capacity_receiver.stage_payload_prefix_or_throw(
                anonsync::sha256_hex(second_payload), second_payload.size(),
                0U, anonsync::sha256_hex(second_payload), second_payload);
        },
        "staged prefix reservation exceeds transient capacity",
        "short physical prefix allowed a second transfer to overcommit completion capacity");
}

void test_terminal_verification_journal_bounds_restart_work() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-terminal-verification-journal-restart";
    constexpr std::uint64_t frontier =
        anonsync::kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep;
    constexpr std::uint64_t tail_bytes = 4097U;
    const std::uint64_t total_bytes = frontier + tail_bytes;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = total_bytes + 1024U;
    limits.max_indexed_bytes = (2U * total_bytes) + 4096U;
    limits.max_transient_entries = 32U;
    limits.max_transient_bytes = total_bytes + 4096U;

    std::string payload(static_cast<std::size_t>(total_bytes), '\0');
    for (std::size_t index = 0U; index < payload.size(); ++index) {
        payload[index] = static_cast<char>(
            'a' + static_cast<char>((index * 17U + index / 251U) % 26U));
    }
    const std::string digest = anonsync::sha256_hex(payload);

    const fs::path restart_root =
        temporary.make_store_root("terminal-bounded-restart");
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, restart_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "terminal bounded restart source range");
        require_error(
            [&] {
                (void)store.stage_payload_prefix_or_throw(
                    digest, total_bytes, total_bytes, std::string{},
                    std::string_view{});
            },
            "digest is invalid",
            "public source-range API accepted the terminal sentinel");
        const auto received = store.stage_payload_prefix_or_throw(
            digest, total_bytes, 0U, anonsync::sha256_hex(payload), payload);
        require(
            received.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        Progress &&
                received.next_offset_bytes == total_bytes &&
                received.accepted_range_bytes == total_bytes,
            "complete source range did not stop at the local terminal-verification frontier");
        const auto journal = read_terminal_verification_journal_or_fail(
            restart_root, digest, limits.max_payload_bytes,
            "terminal bounded first step");
        require(
            journal.latest_state.verified_offset_bytes == frontier &&
                journal.latest_state.hash.total_bytes == frontier &&
                journal.latest_state.staged_prefix_metadata.size_bytes ==
                    total_bytes &&
                journal.latest_state.verified_offset_bytes < total_bytes,
            "first terminal step did not persist the exact nonterminal 32 MiB checkpoint");
        const auto snapshot = store.snapshot_or_throw();
        require(
            snapshot.entry_count() == 0U &&
                snapshot.transient_entry_count() == 1U &&
                snapshot.transient_bytes() == total_bytes,
            "terminal journal leaked into semantic transient accounting");
    }
    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, restart_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "terminal bounded restart completion");
        const auto completed =
            restarted.continue_staged_payload_prefix_verification_or_throw(
                digest, total_bytes);
        require(
            completed.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedInserted &&
                completed.next_offset_bytes == total_bytes &&
                completed.accepted_range_bytes == 0U &&
                !fs::exists(terminal_verification_path(restart_root, digest)),
            "fresh owner did not complete only the remaining terminal-verification tail");
        require(
            !single_staged_prefix_if_present_or_fail(restart_root).has_value(),
            "terminal completion retained a staged-prefix owner");
        const auto snapshot = restarted.snapshot_or_throw();
        require(
            snapshot.entry_count() == 1U &&
                snapshot.indexed_bytes() == total_bytes &&
                read_file_bytes(restart_root / digest) == payload,
            "bounded terminal completion published wrong payload bytes");
    }

    // An exact-size but checksum-invalid journal is disposable computational
    // state. The complete staged prefix remains authoritative transfer work;
    // the next owner restarts fixed-memory verification from offset zero.
    const fs::path malformed_root =
        temporary.make_store_root("terminal-malformed-restart");
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, malformed_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "terminal malformed producer");
        const auto received = store.stage_payload_prefix_or_throw(
            digest, total_bytes, 0U, anonsync::sha256_hex(payload), payload);
        require(
            received.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress,
            "malformed-journal fixture did not reach terminal verification");
    }
    overwrite_private_file(
        terminal_verification_path(malformed_root, digest),
        std::string(
            static_cast<std::size_t>(
                anonsync::sync_replica_file_payload_terminal_verification_journal_exact_bytes()),
            '\x5a'));
    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, malformed_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "terminal malformed restart");
        require(
            restarted.snapshot_or_throw().transient_entry_count() == 1U,
            "malformed terminal journal blocked complete store observation");
        const auto first =
            restarted.continue_staged_payload_prefix_verification_or_throw(
                digest, total_bytes);
        require(
            first.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        Progress &&
                first.next_offset_bytes == total_bytes,
            "malformed terminal journal did not restart bounded verification");
        const auto repaired = read_terminal_verification_journal_or_fail(
            malformed_root, digest, limits.max_payload_bytes,
            "terminal malformed repaired state");
        require(
            repaired.latest_state.verified_offset_bytes == frontier &&
                repaired.latest_state.hash.total_bytes == frontier,
            "malformed journal replacement did not publish one bounded checkpoint");
        const auto completed =
            restarted.continue_staged_payload_prefix_verification_or_throw(
                digest, total_bytes);
        require(
            completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted,
            "repaired terminal continuation did not complete normally");
    }

    // A trusted whole-content digest is never replaced by journal authority.
    // Corruption after the first bounded step is discovered by the current
    // process terminal hash, and every staging artifact is removed.
    const fs::path mismatch_root =
        temporary.make_store_root("terminal-digest-mismatch");
    std::string wrong_payload = payload;
    wrong_payload.back() = wrong_payload.back() == 'z' ? 'y' : 'z';
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, mismatch_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "terminal mismatch receiver");
        const auto received = store.stage_payload_prefix_or_throw(
            digest, total_bytes, 0U, anonsync::sha256_hex(wrong_payload),
            wrong_payload);
        require(
            received.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress,
            "wrong whole payload did not reach the bounded terminal cutpoint");
        require_error(
            [&] {
                (void)store.continue_staged_payload_prefix_verification_or_throw(
                    digest, total_bytes);
            },
            "failed whole-file verification",
            "terminal continuation trusted a wrong whole payload");
        require(
            !fs::exists(mismatch_root / digest) &&
                !fs::exists(terminal_verification_path(mismatch_root, digest)) &&
                !single_staged_prefix_if_present_or_fail(mismatch_root).has_value() &&
                store.snapshot_or_throw().transient_entry_count() == 0U,
            "whole-file mismatch retained payload or computational authority");
    }

    // Hidden journal metadata still consumes a fixed count frontier. A source
    // range may remain durably staged when that later local-only reservation
    // fails, but a second journal cannot be minted.
    const fs::path capacity_root =
        temporary.make_store_root("terminal-journal-count-capacity");
    auto capacity_limits = limits;
    capacity_limits.max_transient_entries = 1U;
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, capacity_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            capacity_limits, "terminal journal count bootstrap");
        (void)store.snapshot_or_throw();
        const std::string unrelated = anonsync::sha256_hex("unrelated journal");
        write_private_file(
            terminal_verification_path(capacity_root, unrelated), "torn");
        require_error(
            [&] {
                (void)store.stage_payload_prefix_or_throw(
                    digest, total_bytes, 0U, anonsync::sha256_hex(payload),
                    payload);
            },
            "cannot admit one terminal-verification continuation",
            "terminal journal count frontier admitted hidden unbounded state");
        require(
            !fs::exists(terminal_verification_path(capacity_root, digest)) &&
                single_staged_prefix_if_present_or_fail(capacity_root).has_value(),
            "journal-capacity failure lost accepted bytes or minted another journal");
    }
}

void test_deferred_terminal_verification_preserves_exact_prefix() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-deferred-terminal-verification";
    const std::string payload =
        "AnonSync deferred terminal verification keeps exact durable bytes\n";
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path root =
        temporary.make_store_root("deferred-terminal-verification");

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "deferred terminal receiver");
    const auto deferred = store.
        stage_payload_prefix_deferring_terminal_verification_or_throw(
            digest, payload.size(), 0U, digest, payload);
    require(
        deferred.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            deferred.next_offset_bytes == payload.size() &&
            deferred.accepted_range_bytes == payload.size() &&
            deferred.terminal_verification_steps == 0U &&
            !fs::exists(root / digest) &&
            single_staged_prefix_if_present_or_fail(root).has_value(),
        "deferred terminal staging hashed or published the complete prefix");

    const auto completed =
        store.continue_staged_payload_prefix_verification_or_throw(
            digest, payload.size());
    require(
        completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted &&
            completed.next_offset_bytes == payload.size() &&
            completed.accepted_range_bytes == 0U &&
            completed.terminal_verification_steps == 1U &&
            read_file_bytes(root / digest) == payload,
        "deferred terminal prefix did not complete through the ordinary exact-inode verifier");
}

void test_targeted_terminal_continuation_defers_namespace_reproof() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-targeted-terminal-verification-continuation";
    constexpr std::uint64_t frontier =
        anonsync::kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep;
    constexpr std::uint64_t tail_bytes = 4097U;
    const std::uint64_t total_bytes = (2U * frontier) + tail_bytes;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = total_bytes + 1024U;
    limits.max_indexed_bytes = (2U * total_bytes) + 4096U;
    limits.max_transient_entries = 32U;
    limits.max_transient_bytes = total_bytes + 4096U;

    std::string payload(static_cast<std::size_t>(total_bytes), '\0');
    for (std::size_t index = 0U; index < payload.size(); ++index) {
        payload[index] = static_cast<char>(
            'a' + static_cast<char>((index * 13U + index / 97U) % 26U));
    }
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path root =
        temporary.make_store_root("targeted-terminal-observation");

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "targeted terminal receiver");
    const auto staged = store.stage_payload_prefix_or_throw(
        digest, total_bytes, 0U, anonsync::sha256_hex(payload), payload);
    require(
        staged.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            staged.next_offset_bytes == total_bytes,
        "targeted terminal fixture did not reach its first bounded checkpoint");

    const fs::path unrelated = root / ".unexpected-targeted-terminal-entry";
    write_private_file(unrelated, "unrelated namespace evidence");
    const auto middle =
        store.continue_staged_payload_prefix_verification_or_throw(
            digest, total_bytes);
    require(
        middle.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            middle.next_offset_bytes == total_bytes &&
            middle.accepted_range_bytes == 0U,
        "intermediate exact-inode terminal continuation enumerated or lost its namespace-cold progress");
    const auto middle_journal = read_terminal_verification_journal_or_fail(
        root, digest, limits.max_payload_bytes,
        "targeted terminal middle checkpoint");
    require(
        middle_journal.latest_state.verified_offset_bytes == 2U * frontier,
        "targeted terminal continuation did not advance exactly one bounded SHA frontier");

    require_error(
        [&] {
            (void)store.continue_staged_payload_prefix_verification_or_throw(
                digest, total_bytes);
        },
        "refuses unexpected payload-root entry",
        "terminal completion skipped the mandatory complete namespace reproof");
    require(
        !fs::exists(root / digest) &&
            single_staged_prefix_if_present_or_fail(root).has_value(),
        "failed final namespace reproof published or discarded the staged payload");

    std::error_code remove_error;
    const bool removed = fs::remove(unrelated, remove_error);
    require(
        removed && !remove_error,
        "could not remove the targeted terminal namespace fixture");
    const auto completed =
        store.continue_staged_payload_prefix_verification_or_throw(
            digest, total_bytes);
    require(
        completed.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted &&
            completed.next_offset_bytes == total_bytes &&
            completed.accepted_range_bytes == 0U &&
            read_file_bytes(root / digest) == payload,
        "targeted terminal continuation did not publish after complete namespace repair");
}

void test_receiver_local_terminal_scheduler_is_restart_fair_and_bounded() {
    TemporaryDirectory temporary;
    const std::string folder =
        "folder-receiver-local-terminal-scheduler";
    constexpr std::uint64_t frontier =
        anonsync::kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep;
    constexpr std::uint64_t tail_bytes = 4097U;
    const std::uint64_t total_bytes = (2U * frontier) + tail_bytes;

    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = total_bytes + 1024U;
    limits.max_indexed_bytes = (3U * total_bytes) + 4096U;
    limits.max_transient_entries = 32U;
    limits.max_transient_bytes = (2U * total_bytes) + 4096U;

    auto make_payload = [&](std::uint64_t salt) {
        std::string bytes(static_cast<std::size_t>(total_bytes), '\0');
        for (std::size_t index = 0U; index < bytes.size(); ++index) {
            bytes[index] = static_cast<char>(
                'a' + static_cast<char>(
                    (index * (17U + salt) + index / (97U + salt)) % 26U));
        }
        return bytes;
    };
    const std::string payload_a = make_payload(1U);
    const std::string payload_b = make_payload(3U);
    const std::string digest_a = anonsync::sha256_hex(payload_a);
    const std::string digest_b = anonsync::sha256_hex(payload_b);
    require(
        digest_a != digest_b,
        "receiver-local terminal scheduler fixture collided");
    const std::string first_digest = std::min(digest_a, digest_b);
    const std::string second_digest = std::max(digest_a, digest_b);
    const fs::path root =
        temporary.make_store_root("receiver-local-terminal-scheduler");

    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            limits, "receiver-local terminal scheduler producer");
        const auto cold_status = store.terminal_verification_status();
        const auto cold_step =
            store.continue_one_pending_terminal_verification_or_throw();
        require(
            !cold_status.observation_known &&
                cold_status.pending_entry_count == 0U &&
                cold_step.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            ObservationUnknown,
            "fresh terminal scheduler invented a complete namespace observation");

        for (const auto& [digest, payload] :
             std::array<std::pair<std::string, const std::string*>, 2U>{
                 std::pair{digest_a, &payload_a},
                 std::pair{digest_b, &payload_b}}) {
            const auto deferred = store.
                stage_payload_prefix_deferring_terminal_verification_or_throw(
                    digest, total_bytes, 0U, anonsync::sha256_hex(*payload),
                    *payload);
            require(
                deferred.disposition ==
                        anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                            Progress &&
                    deferred.next_offset_bytes == total_bytes &&
                    deferred.terminal_verification_steps == 0U,
                "receiver-local terminal scheduler fixture was not deferred");
        }
        require(
            !store.terminal_verification_status().observation_known,
            "targeted staging manufactured global terminal-work completeness");

        const auto snapshot = store.snapshot_or_throw();
        const auto known = store.terminal_verification_status();
        require(
            snapshot.entry_count() == 0U &&
                snapshot.transient_entry_count() == 2U &&
                known.observation_known &&
                known.pending_entry_count == 2U &&
                known.pending_total_bytes == 2U * total_bytes &&
                known.pending_verified_bytes == 0U &&
                known.next_work.has_value() &&
                known.next_work->content_sha256 == first_digest &&
                known.next_work->verified_offset_bytes == 0U,
            "complete scan did not discover the bounded fair terminal-work set");

        const auto first =
            store.continue_one_pending_terminal_verification_or_throw();
        const auto second =
            store.continue_one_pending_terminal_verification_or_throw();
        require(
            first.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            Progress &&
                first.work_before.has_value() &&
                first.work_before->content_sha256 == first_digest &&
                first.hashed_bytes == frontier &&
                first.verified_offset_after_bytes == frontier &&
                second.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            Progress &&
                second.work_before.has_value() &&
                second.work_before->content_sha256 == second_digest &&
                second.hashed_bytes == frontier &&
                second.verified_offset_after_bytes == frontier,
            "receiver-local scheduler did not give both zero-frontier targets one bounded pulse");
        const auto tied = store.terminal_verification_status();
        require(
            tied.pending_verified_bytes == 2U * frontier &&
                tied.next_work.has_value() &&
                tied.next_work->content_sha256 == first_digest,
            "equal terminal frontiers were not ordered canonically");

        const fs::path unrelated = root / ".unexpected-local-pulse-entry";
        write_private_file(unrelated, "must remain unenumerated mid-hash");
        const auto middle =
            store.continue_one_pending_terminal_verification_or_throw();
        require(
            middle.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            Progress &&
                middle.work_before.has_value() &&
                middle.work_before->content_sha256 == first_digest &&
                middle.hashed_bytes == frontier &&
                middle.verified_offset_after_bytes == 2U * frontier &&
                middle.terminal_verification_steps == 1U &&
                fs::exists(unrelated),
            "receiver-local pulse enumerated unrelated namespace state or crossed its byte bound");
        const auto after_middle = store.terminal_verification_status();
        require(
            after_middle.pending_entry_count == 2U &&
                after_middle.pending_verified_bytes == 3U * frontier &&
                after_middle.next_work.has_value() &&
                after_middle.next_work->content_sha256 == second_digest &&
                after_middle.next_work->verified_offset_bytes == frontier,
            "terminal scheduler did not rotate to the least-advanced digest");
        std::error_code remove_error;
        require(
            fs::remove(unrelated, remove_error) && !remove_error,
            "could not remove receiver-local pulse namespace fixture");
    }

    {
        anonsync::SyncReplicaFilePayloadStore restarted(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "receiver-local terminal scheduler restart");
        require(
            !restarted.terminal_verification_status().observation_known,
            "fresh owner retained process-local terminal scheduling state");
        (void)restarted.snapshot_or_throw();
        const auto recovered = restarted.terminal_verification_status();
        require(
            recovered.observation_known &&
                recovered.pending_entry_count == 2U &&
                recovered.pending_verified_bytes == 3U * frontier &&
                recovered.next_work.has_value() &&
                recovered.next_work->content_sha256 == second_digest &&
                recovered.next_work->verified_offset_bytes == frontier,
            "restart did not recover exact journal progress and fair ordering");

        const auto second_progress =
            restarted.continue_one_pending_terminal_verification_or_throw();
        require(
            second_progress.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            Progress &&
                second_progress.work_before.has_value() &&
                second_progress.work_before->content_sha256 == second_digest &&
                second_progress.hashed_bytes == frontier &&
                second_progress.verified_offset_after_bytes == 2U * frontier,
            "restart scheduler did not advance the least-proved digest first");
        const auto retied = restarted.terminal_verification_status();
        require(
            retied.pending_verified_bytes == 4U * frontier &&
                retied.next_work.has_value() &&
                retied.next_work->content_sha256 == first_digest,
            "recovered equal terminal frontiers were not ordered canonically");

        const auto first_completed =
            restarted.continue_one_pending_terminal_verification_or_throw();
        require(
            first_completed.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            CompletedInserted &&
                first_completed.work_before.has_value() &&
                first_completed.work_before->content_sha256 == first_digest &&
                first_completed.hashed_bytes == tail_bytes &&
                first_completed.verified_offset_after_bytes == total_bytes,
            "first fair terminal target did not publish through the final full-store fence");
        const auto second_completed =
            restarted.continue_one_pending_terminal_verification_or_throw();
        require(
            second_completed.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            CompletedInserted &&
                second_completed.work_before.has_value() &&
                second_completed.work_before->content_sha256 == second_digest &&
                second_completed.hashed_bytes == tail_bytes,
            "second fair terminal target did not publish independently");
        const auto settled = restarted.terminal_verification_status();
        const auto idle =
            restarted.continue_one_pending_terminal_verification_or_throw();
        const auto final_snapshot = restarted.snapshot_or_throw();
        require(
            settled.observation_known &&
                settled.pending_entry_count == 0U &&
                !settled.next_work.has_value() &&
                idle.disposition ==
                    anonsync::
                        SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                            NoPendingWork &&
                final_snapshot.entry_count() == 2U &&
                final_snapshot.indexed_bytes() == 2U * total_bytes &&
                read_file_bytes(root / digest_a) == payload_a &&
                read_file_bytes(root / digest_b) == payload_b,
            "receiver-local terminal scheduler did not settle both exact payloads");
    }
}

void test_terminal_scheduler_stale_projection_reconciliation_reports_zero_hash() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-terminal-stale-scheduler-projection";
    const std::string payload(4097U, 's');
    const std::string digest = anonsync::sha256_hex(payload);
    const fs::path root = temporary.make_store_root(
        "terminal-stale-scheduler-projection");
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 8192U;
    limits.max_indexed_bytes = 32768U;
    limits.max_transient_entries = 8U;
    limits.max_transient_bytes = 16384U;

    anonsync::SyncReplicaFilePayloadStore stale_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "terminal stale scheduler projection owner");
    const auto deferred = stale_owner.
        stage_payload_prefix_deferring_terminal_verification_or_throw(
            digest, payload.size(), 0U, digest, payload);
    require(
        deferred.disposition ==
                anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
            deferred.terminal_verification_steps == 0U,
        "stale scheduler fixture did not retain deferred terminal work");
    (void)stale_owner.snapshot_or_throw();
    require(
        stale_owner.terminal_verification_status().pending_entry_count == 1U,
        "stale scheduler owner did not retain its discovered obligation");

    anonsync::SyncReplicaFilePayloadStore completing_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        limits, "terminal stale scheduler completing owner");
    (void)completing_owner.snapshot_or_throw();
    const auto completed =
        completing_owner.continue_one_pending_terminal_verification_or_throw();
    require(
        completed.disposition ==
                anonsync::
                    SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                        CompletedInserted &&
            completed.hashed_bytes == payload.size() &&
            completed.terminal_verification_steps == 1U,
        "second owner did not publish the exact deferred payload");

    const auto reconciled =
        stale_owner.continue_one_pending_terminal_verification_or_throw();
    require(
        reconciled.disposition ==
                anonsync::
                    SyncReplicaFilePayloadStoreTerminalVerificationStepDisposition::
                        CompletedAlreadyPresent &&
            reconciled.terminal_verification_steps == 0U &&
            reconciled.hashed_bytes == 0U &&
            reconciled.verified_offset_after_bytes == payload.size() &&
            stale_owner.terminal_verification_status().pending_entry_count == 0U,
        "stale scheduler reconciliation falsely reported unread bytes as hash work");
}

void test_terminal_scheduler_stale_capacity_invalidates_without_postcommit_failure() {
    TemporaryDirectory temporary;
    const std::string folder = "folder-terminal-stale-capacity";
    const fs::path root = temporary.make_store_root("terminal-stale-capacity");
    anonsync::SyncReplicaFilePayloadStoreLimits limits;
    limits.max_entries = 8U;
    limits.max_payload_bytes = 8192U;
    limits.max_indexed_bytes = 65536U;
    limits.max_transient_entries = 4U;
    limits.max_transient_bytes = 32768U;

    const std::array<std::string, 5U> payloads{
        std::string(4097U, 'a'), std::string(4097U, 'b'),
        std::string(4097U, 'c'), std::string(4097U, 'd'),
        std::string(4097U, 'e')};
    std::array<std::string, 5U> digests{};
    for (std::size_t index = 0U; index < payloads.size(); ++index) {
        digests[index] = anonsync::sha256_hex(payloads[index]);
    }

    anonsync::SyncReplicaFilePayloadStore stale_owner(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        limits, "terminal stale-capacity owner");
    for (std::size_t index = 0U; index < 3U; ++index) {
        const auto staged = stale_owner.
            stage_payload_prefix_deferring_terminal_verification_or_throw(
                digests[index], payloads[index].size(), 0U,
                digests[index], payloads[index]);
        require(
            staged.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
                staged.terminal_verification_steps == 0U,
            "stale-capacity fixture did not create exact deferred work");
    }
    (void)stale_owner.snapshot_or_throw();
    const auto stale_projection = stale_owner.terminal_verification_status();
    require(
        stale_projection.observation_known &&
            stale_projection.pending_entry_count == 3U &&
            stale_projection.next_work.has_value(),
        "stale-capacity owner did not establish its complete projection");

    const std::string completed_digest =
        stale_projection.next_work->content_sha256;
    {
        anonsync::SyncReplicaFilePayloadStore completing_owner(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            limits, "terminal stale-capacity completing owner");
        const auto completed =
            completing_owner.continue_staged_payload_prefix_verification_or_throw(
                completed_digest, payloads.front().size());
        require(
            completed.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedInserted &&
                completed.terminal_verification_steps == 1U,
            "external owner did not replace one stale projected prefix with its payload");
    }

    for (std::size_t index = 3U; index < payloads.size(); ++index) {
        const auto staged = stale_owner.
            stage_payload_prefix_deferring_terminal_verification_or_throw(
                digests[index], payloads[index].size(), 0U,
                digests[index], payloads[index]);
        require(
            staged.disposition ==
                    anonsync::SyncReplicaFilePayloadStoreStageDisposition::Progress &&
                staged.terminal_verification_steps == 0U,
            "stale advisory cache turned a valid committed prefix into a reported failure");
    }
    require(
        !stale_owner.terminal_verification_status().observation_known,
        "overfull stale advisory projection was not invalidated conservatively");

    const auto rebuilt_snapshot = stale_owner.snapshot_or_throw();
    const auto rebuilt = stale_owner.terminal_verification_status();
    require(
        rebuilt_snapshot.entry_count() == 1U &&
            rebuilt.observation_known &&
            rebuilt.pending_entry_count == 4U &&
            rebuilt.next_work.has_value(),
        "ordinary complete scan did not rebuild the invalidated scheduler projection");
}

void test_product_bound_identity_and_fresh_adoption_policy() {
    TemporaryDirectory temporary;
    const auto exact_identity = product_identity(temporary);
    const fs::path root = temporary.make_store_root("product-bound");
    const fs::path product_marker =
        root / std::string(kProductIdentityCurrent);
    const fs::path standalone_marker =
        root / std::string(kStandaloneIdentityCurrent);

    anonsync::SyncReplicaFilePayloadStore bootstrap(
        exact_identity, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "product-bound payload bootstrap");
    const auto empty_snapshot = bootstrap.snapshot_or_throw();
    require(empty_snapshot.entry_count() == 0U &&
                fs::exists(product_marker) &&
                !fs::exists(standalone_marker),
            "product bootstrap did not publish exactly the v3 lease anchor");
    require(read_file_bytes(product_marker) ==
                product_identity_marker_bytes(exact_identity),
            "product payload marker did not bind the complete deployment identity");

    anonsync::SyncReplicaFilePayloadStore restarted(
        exact_identity, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "product-bound payload restart");
    require(restarted.snapshot_or_throw().snapshot_digest() ==
                empty_snapshot.snapshot_digest(),
            "the exact deployment identity did not reopen its payload root");

    const fs::path product_legacy_marker =
        root / std::string(kProductIdentityLegacyReader);
    rename_private_file_and_sync_directory(
        product_marker, product_legacy_marker,
        "product minimum-reader legacy fixture");
    const auto product_identity_inode =
        private_file_identity(product_legacy_marker);
    anonsync::SyncReplicaFilePayloadStore product_migrator(
        exact_identity, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "product minimum-reader migrator");
    require(
        product_migrator.snapshot_or_throw().entry_count() == 0U &&
            fs::is_regular_file(product_marker) &&
            !fs::exists(product_legacy_marker) &&
            private_file_identity(product_marker) == product_identity_inode,
        "product-bound minimum-reader migration changed identity or authority");

    auto wrong_deployment = exact_identity;
    wrong_deployment.deployment_id = std::string(64U, 'c');
    anonsync::SyncReplicaFilePayloadStore wrong_deployment_store(
        wrong_deployment, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "product-bound wrong deployment");
    require_error(
        [&] { (void)wrong_deployment_store.snapshot_or_throw(); },
        "identity marker conflicts",
        "another deployment ID reopened the product payload root");

    auto wrong_manifest = exact_identity;
    wrong_manifest.manifest_digest = std::string(64U, 'd');
    anonsync::SyncReplicaFilePayloadStore wrong_manifest_store(
        wrong_manifest, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "product-bound wrong manifest");
    require_error(
        [&] { (void)wrong_manifest_store.snapshot_or_throw(); },
        "identity marker conflicts",
        "another manifest digest reopened the product payload root");

    anonsync::SyncReplicaFilePayloadStore standalone_observer(
        exact_identity.folder_id, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "standalone observer of product root");
    require_error(
        [&] { (void)standalone_observer.snapshot_or_throw(); },
        "incompatible payload-store identity generation",
        "standalone v2 authority adopted a product-bound v3 root");

    const fs::path preseeded =
        temporary.make_store_root("product-preseeded");
    const std::string payload = "preexisting-unbound-product-payload";
    const fs::path payload_path =
        preseeded / anonsync::sha256_hex(payload);
    write_private_file(payload_path, payload);
    anonsync::SyncReplicaFilePayloadStore product_adoption_attempt(
        exact_identity, preseeded,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "product-bound preseeded bootstrap");
    require_error(
        [&] { (void)product_adoption_attempt.snapshot_or_throw(); },
        "refuses adoption of pre-existing payload-root entries",
        "product bootstrap adopted payload bytes lacking deployment identity");
    require(fs::exists(payload_path) &&
                !fs::exists(
                    preseeded / std::string(kProductIdentityCurrent)),
            "failed product adoption preflight mutated the preseeded namespace");

    const fs::path scrub_preseeded =
        temporary.make_store_root("product-preseeded-scrub-state");
    const fs::path scrub_state =
        scrub_preseeded /
        std::string(anonsync::kSyncReplicaFilePayloadScrubStateBasename);
    write_private_file(scrub_state, "unbound-scrub-progress");
    anonsync::SyncReplicaFilePayloadStore scrub_adoption_attempt(
        exact_identity, scrub_preseeded,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "product-bound scrub-state preseeded bootstrap");
    require_error(
        [&] { (void)scrub_adoption_attempt.snapshot_or_throw(); },
        "refuses adoption of pre-existing payload-root entries",
        "product bootstrap treated unbound scrub state as disposable empty space");
    require(
        fs::exists(scrub_state) &&
            !fs::exists(
                scrub_preseeded / std::string(kProductIdentityCurrent)),
        "failed product scrub-state adoption mutated the unbound namespace");

    const fs::path standalone_root =
        temporary.make_store_root("standalone-generation");
    anonsync::SyncReplicaFilePayloadStore standalone_bootstrap(
        exact_identity.folder_id, standalone_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "standalone generation bootstrap");
    (void)standalone_bootstrap.snapshot_or_throw();
    anonsync::SyncReplicaFilePayloadStore product_observer(
        exact_identity, standalone_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "product observer of standalone root");
    require_error(
        [&] { (void)product_observer.snapshot_or_throw(); },
        "incompatible payload-store identity generation",
        "product authority adopted a standalone v2 payload root");
}

anonsync::SyncReplicaFilePayloadRetentionMark
retention_mark_fixture(std::uint64_t marked_at_unix_seconds) {
    anonsync::SyncReplicaFilePayloadRetentionMark mark;
    mark.marked_at_unix_seconds = marked_at_unix_seconds;
    mark.source_replica_state_generation = 41U;
    mark.policy = {
        .minimum_grace_seconds = 86'400U,
        .maximum_candidate_payload_count = 8U,
        .maximum_candidate_payload_bytes = 1'024U,
        .maximum_collection_payload_count = 2U,
        .maximum_collection_payload_bytes = 128U,
    };
    mark.source_operation_set_digest =
        anonsync::sha256_hex("retention operations");
    mark.source_evidence_set_digest =
        anonsync::sha256_hex("retention evidence");
    mark.source_historical_version_pin_set_digest =
        anonsync::sha256_hex("retention pins");
    mark.source_visible_state_digest =
        anonsync::sha256_hex("retention visible");
    mark.source_payload_snapshot_digest =
        anonsync::sha256_hex("retention payload snapshot");
    mark.source_payload_transient_namespace_digest =
        anonsync::sha256_hex("retention transient namespace");
    mark.unreferenced_candidate_set_digest =
        anonsync::sha256_hex("retention candidates");
    mark.durable_candidate_witness_digest =
        anonsync::sha256_hex("retention durable witness");
    mark.unreferenced_candidate_payload_count = 3U;
    mark.unreferenced_candidate_payload_bytes = 256U;
    return mark;
}

void test_retention_mark_is_durable_identity_bound_and_snapshot_cold() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("retention-mark");
    const std::string folder = "folder-payload-retention-mark";
    const fs::path mark_path =
        root / std::string(
            anonsync::kSyncReplicaFilePayloadRetentionMarkBasename);

    std::string empty_snapshot_digest;
    anonsync::SyncReplicaFilePayloadRetentionMark first_mark;
    std::string first_mark_digest;
    {
        anonsync::SyncReplicaFilePayloadStore store(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "retention-mark store");
        {
            const auto before = store.snapshot_or_throw();
            require(
                !before.retention_mark_present() &&
                    before.retention_mark_observation_known() &&
                    !before.retention_mark_usable() &&
                    !before.retention_mark().has_value() &&
                    !before.retention_mark_digest().has_value(),
                "fresh payload store fabricated retention evidence");
            empty_snapshot_digest = before.snapshot_digest();
        }

        anonsync::SyncReplicaFilePayloadRetentionMarkPublication published;
        {
            const auto writer_fenced =
                anonsync::SyncReplicaFilePayloadStoreTestAccess::
                    writer_fenced_retention_snapshot_or_throw(store);
            published =
                anonsync::SyncReplicaFilePayloadStoreTestAccess::
                    publish_retention_mark_or_throw(
                        store, writer_fenced,
                        retention_mark_fixture(1'800'000'000U));
        }
        require(
            published.mark.generation == 1U &&
                !published.replaced_existing_file &&
                !published.replaced_usable_mark &&
                anonsync::is_lowercase_sha256_hex(published.mark_digest),
            "first retention-mark publication reported the wrong cutpoint");
        require(
            published.mark.store_identity_sha256 != std::string(64U, '0') &&
                published.mark.store_identity_metadata.size_bytes != 0U,
            "retention-mark publication did not bind the exact store identity");
        first_mark = published.mark;
        first_mark_digest = published.mark_digest;

        const auto observed = store.snapshot_or_throw();
        require(
            observed.retention_mark_present() &&
                observed.retention_mark_observation_known() &&
                observed.retention_mark_usable() &&
                observed.retention_mark().has_value() &&
                *observed.retention_mark() == first_mark &&
                observed.retention_mark_digest() == first_mark_digest,
            "same-process complete scan did not return the exact durable mark");
        require(
            observed.entry_count() == 0U &&
                observed.indexed_bytes() == 0U &&
                observed.snapshot_digest() == empty_snapshot_digest &&
                observed.transient_entry_count() == 0U &&
                observed.transient_bytes() == 0U,
            "retention metadata contaminated payload or transient accounting");
    }

    {
        anonsync::SyncReplicaFilePayloadStore reopened(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            {}, "retention-mark reopened store");
        const auto restarted = reopened.snapshot_or_throw();
        require(
            restarted.retention_mark_present() &&
                restarted.retention_mark_observation_known() &&
                restarted.retention_mark_usable() &&
                restarted.retention_mark().has_value() &&
                *restarted.retention_mark() == first_mark &&
                restarted.retention_mark_digest() == first_mark_digest &&
                restarted.snapshot_digest() == empty_snapshot_digest,
            "fresh process owner did not rediscover the exact retention mark");

        auto successor = retention_mark_fixture(1'800'000'100U);
        successor.durable_candidate_witness_digest =
            anonsync::sha256_hex("retention successor witness");
        const auto writer_fenced =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                writer_fenced_retention_snapshot_or_throw(reopened);
        const auto replaced =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                publish_retention_mark_or_throw(
                    reopened, writer_fenced, std::move(successor));
        require(
            replaced.mark.generation == 2U &&
                replaced.replaced_existing_file &&
                replaced.replaced_usable_mark &&
                replaced.mark.store_identity_sha256 ==
                    first_mark.store_identity_sha256 &&
                replaced.mark.store_identity_metadata ==
                    first_mark.store_identity_metadata,
            "retention-mark replacement lost generation or identity binding");
    }

    overwrite_private_file(mark_path, "torn retention intent");
    {
        anonsync::SyncReplicaFilePayloadStore damaged(
            folder, root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            {}, "damaged retention-mark store");
        const auto observed = damaged.snapshot_or_throw();
        require(
            observed.retention_mark_present() &&
                observed.retention_mark_observation_known() &&
                !observed.retention_mark_usable() &&
                !observed.retention_mark().has_value() &&
                !observed.retention_mark_digest().has_value() &&
                observed.snapshot_digest() == empty_snapshot_digest,
            "damaged retention evidence was hidden or treated as authority");

        const auto writer_fenced =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                writer_fenced_retention_snapshot_or_throw(damaged);
        const auto repaired =
            anonsync::SyncReplicaFilePayloadStoreTestAccess::
                publish_retention_mark_or_throw(
                    damaged, writer_fenced,
                    retention_mark_fixture(1'800'000'200U));
        require(
            repaired.mark.generation == 1U &&
                repaired.replaced_existing_file &&
                !repaired.replaced_usable_mark,
            "damaged retention evidence was not replaced conservatively");
    }

    anonsync::SyncReplicaFilePayloadStore forensic(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect,
        {}, "retention-mark forensic store");
    const auto forensic_snapshot = forensic.snapshot_or_throw();
    require(
        forensic_snapshot.retention_mark_present() &&
            !forensic_snapshot.retention_mark_observation_known() &&
            !forensic_snapshot.retention_mark_usable() &&
            !forensic_snapshot.retention_mark().has_value(),
        "byte-cold forensic inspection claimed retention-mark authority");
}

void test_legacy_identity_generation_requires_offline_migration() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("legacy-generation");
    const std::string folder = "folder-durable-payload-legacy-generation";
    const fs::path legacy_marker =
        root / ".anonsync-payload-store-identity-v1";
    const fs::path current_marker =
        root / std::string(kStandaloneIdentityCurrent);
    write_private_file(
        legacy_marker,
        "anonsync:sync-replica-file-payload-store-identity:v1\n" +
            folder + "\n");

    anonsync::SyncReplicaFilePayloadStore store(
        folder, root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        {}, "payload store legacy-generation fixture");
    require_error(
        [&] { (void)store.snapshot_or_throw(); },
        "offline migration is required",
        "legacy identity generation entered lease-protected authority");
    require(
        fs::exists(legacy_marker) && !fs::exists(current_marker),
        "failed legacy-generation preflight mutated identity authority");

    const fs::path duplicate_root =
        temporary.make_store_root("coexisting-reader-generations");
    const fs::path duplicate_current =
        duplicate_root / std::string(kStandaloneIdentityCurrent);
    const fs::path duplicate_legacy =
        duplicate_root / std::string(kStandaloneIdentityLegacyReader);
    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, duplicate_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            {}, "coexisting reader-generation publisher");
        (void)publisher.snapshot_or_throw();
    }
    write_private_file(duplicate_legacy, read_file_bytes(duplicate_current));
    anonsync::SyncReplicaFilePayloadStore duplicate_reader(
        folder, duplicate_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "coexisting reader-generation detector");
    require_error(
        [&] { (void)duplicate_reader.snapshot_or_throw(); },
        "coexisting current and legacy-reader",
        "coexisting lock-anchor generations admitted split authority");
    require(
        fs::is_regular_file(duplicate_current) &&
            fs::is_regular_file(duplicate_legacy),
        "coexisting-generation rejection mutated forensic evidence");

    const fs::path cross_family_root =
        temporary.make_store_root("coexisting-cross-family-generations");
    const fs::path standalone_current =
        cross_family_root / std::string(kStandaloneIdentityCurrent);
    const fs::path product_current =
        cross_family_root / std::string(kProductIdentityCurrent);
    {
        anonsync::SyncReplicaFilePayloadStore publisher(
            folder, cross_family_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                CreateIfMissing,
            {}, "cross-family generation publisher");
        (void)publisher.snapshot_or_throw();
    }
    write_private_file(product_current, "incompatible-product-generation");
    anonsync::SyncReplicaFilePayloadStore cross_family_reader(
        folder, cross_family_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        {}, "cross-family generation detector");
    require_error(
        [&] { (void)cross_family_reader.snapshot_or_throw(); },
        "coexisting incompatible payload-store identity marker",
        "cross-family lock anchors admitted split authority before scanning");
    require(
        fs::is_regular_file(standalone_current) &&
            fs::is_regular_file(product_current),
        "cross-family generation rejection mutated forensic evidence");
}

}  // namespace

int main() {
    try {
        require(
            anonsync::sync_replica_file_payload_store_scrub_disposition_name(
                anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                    Disabled) == "disabled" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredBySchedule) ==
                    "deferred_by_schedule" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            Empty) == "empty" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredLeaseBusy) ==
                    "deferred_lease_busy" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredStaleSnapshot) ==
                    "deferred_stale_snapshot" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredTransientCapacity) ==
                    "deferred_transient_capacity" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredPublicationFailure) ==
                    "deferred_publication_failure" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            DeferredAttemptFailure) ==
                    "deferred_attempt_failure" &&
                anonsync::
                    sync_replica_file_payload_store_scrub_disposition_name(
                        anonsync::SyncReplicaFilePayloadStoreScrubDisposition::
                            Advanced) == "advanced",
            "payload scrub disposition names are not stable operator words");
        require(
            anonsync::sync_replica_file_payload_store_quarantine_action_name(
                anonsync::SyncReplicaFilePayloadStoreQuarantineAction::
                    Preserve) == "preserve" &&
                anonsync::sync_replica_file_payload_store_quarantine_action_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineAction::
                        Release) == "release",
            "payload quarantine action names are not stable operator words");
        require(
            anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                    Quarantined) == "quarantined" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ActiveFaultMismatch) == "active_fault_mismatch" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        PayloadAbsent) == "payload_absent" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        PayloadAlreadyRepaired) == "payload_already_repaired" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ObservedDigestChanged) == "observed_digest_changed" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ExactQuarantineAlreadyPresent) ==
                    "exact_quarantine_already_present" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        EntryCapacityExceeded) ==
                    "entry_capacity_exceeded" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ByteCapacityExceeded) ==
                    "byte_capacity_exceeded" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        Released) == "released" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ExactQuarantineAbsent) ==
                    "exact_quarantine_absent" &&
                anonsync::sync_replica_file_payload_store_quarantine_disposition_name(
                    anonsync::SyncReplicaFilePayloadStoreQuarantineDisposition::
                        ActiveFaultPresent) == "active_fault_present" &&
                anonsync::kSyncReplicaFilePayloadUseLeaseProtocol ==
                    "anonsync:sync-replica-file-payload-use-flock-lease:v1",
            "payload quarantine disposition names or payload-use lease protocol are not stable operator words");
        const auto production_limits = anonsync::
            sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
                64ULL * 1024ULL * 1024ULL,
                "payload-store production limit test");
        require(
            production_limits.max_entries ==
                    anonsync::kSyncReplicaFilePayloadStoreProductionMaxEntries &&
                production_limits.max_entries ==
                    anonsync::kSyncReplicaFileContentInventoryMaxEntries &&
                production_limits.max_payload_bytes ==
                    64ULL * 1024ULL * 1024ULL &&
                production_limits.max_indexed_bytes ==
                    anonsync::kSyncReplicaFilePayloadStoreProductionMaxIndexedBytes &&
                production_limits.max_transient_bytes >=
                    128ULL * 1024ULL * 1024ULL &&
                production_limits.max_scrub_bytes_per_attempt ==
                    4ULL * 1024ULL * 1024ULL &&
                production_limits.max_scrub_entries_per_attempt == 4U,
            "production payload limits do not match the admitted folder and assembly capacities");
        const auto multi_terabyte_limits = anonsync::
            sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
                anonsync::kSyncReplicaMaximumPayloadExtentBytes,
                "payload-store multi-terabyte production limit test");
        require(
            multi_terabyte_limits.max_payload_bytes ==
                    4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL &&
                multi_terabyte_limits.max_indexed_bytes ==
                    anonsync::kSyncReplicaFilePayloadStoreProductionMaxIndexedBytes &&
                multi_terabyte_limits.max_indexed_bytes >
                    1024ULL * 1024ULL * 1024ULL * 1024ULL &&
                multi_terabyte_limits.max_transient_bytes ==
                    8ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL,
            "production payload composition does not admit a bounded 4 TiB file inside a multi-terabyte tree without allocation-derived limits");
        test_existing_only_requires_explicit_bootstrap_without_mutation();
        test_descriptor_streaming_publication_and_selection();
        test_mutation_batch_amortizes_store_scan_and_releases_authority();
        test_payload_availability_generation_tracks_durable_insertions();
        test_mutation_batch_reports_cold_scan_work_and_warms_owner();
#if defined(__linux__)
        test_complete_scan_restarts_one_stale_payload_observation();
#endif
        test_foreign_thread_cannot_touch_owner_local_verification_cache();
        test_mutation_batch_safely_outlives_creator_store_handle();
        test_verification_cache_is_exact_and_durable_across_restart();
        test_process_cache_reverification_refreshes_restart_checkpoint();
        test_verification_checkpoint_skips_tight_transient_capacity();
        test_rotating_scrub_is_bounded_restart_safe_and_cyclic();
        test_complete_scan_supersedes_stale_active_scrub_checkpoint();
        test_scrub_state_damage_and_identity_rebind_are_disposable();
        test_present_unusable_scrub_state_revokes_restart_acceleration();
        test_disabled_scrub_settles_damaged_restart_fence_once();
        test_scrub_failure_is_reproved_persisted_and_repairable();
        test_live_capability_cutpoint_detects_complete_interval_aba();
        test_live_capability_scope_spans_independent_store_owners();
        test_live_capability_scope_recreates_after_final_owner_release();
        test_writer_fenced_retention_snapshot_excludes_namespace_work_and_probes_inode_use();
        test_retention_mark_is_durable_identity_bound_and_snapshot_cold();
        test_live_payload_descriptor_fences_quarantine_inode_mutation();
        test_exact_corrupt_payload_quarantine_is_bounded_and_recoverable();
        test_exact_quarantine_release_preserves_unrelated_byte_proof();
        test_quarantine_inventory_is_restart_discoverable_and_exactly_updated();
        test_fresh_bootstrap_never_adopts_quarantine_evidence();
        test_quarantine_bytes_cannot_exceed_active_indexed_byte_budget();
        test_quarantine_capacity_is_a_typed_nonfatal_result();
        test_process_fault_survives_scrub_record_loss_until_reproof();
        test_process_fault_permanently_revokes_live_snapshot_authority();
        test_process_fault_preserves_original_target_across_second_mismatch();
        test_minimum_reader_identity_migration_is_cold_atomic_and_inode_preserving();
        test_minimum_reader_migration_rebuilds_damaged_scrub_state_once();
        test_prepared_scrub_state_forces_restart_reproof_before_blocked_optional_attempt();
        test_allocation_failure_after_scrub_mismatch_remains_fail_closed();
        test_scrub_defers_under_capacity_and_cooperative_contention();
        test_publication_restart_and_exact_lookup();
        test_namespace_policy_and_limits();
        test_root_rebind_and_post_index_mutation_fail_closed();
        test_cross_process_store_lease_serializes_capacity();
        test_staged_prefix_hot_path_accepts_verification_index();
        test_transient_namespace_digest_binds_restart_obligation_identity();
        test_bounded_range_copy_durable_resume_and_residue_repair();
        test_single_prefix_owner_crash_tail_and_legacy_resume();
        test_terminal_verification_journal_bounds_restart_work();
        test_deferred_terminal_verification_preserves_exact_prefix();
        test_targeted_terminal_continuation_defers_namespace_reproof();
        test_receiver_local_terminal_scheduler_is_restart_fair_and_bounded();
        test_terminal_scheduler_stale_projection_reconciliation_reports_zero_hash();
        test_terminal_scheduler_stale_capacity_invalidates_without_postcommit_failure();
        test_product_bound_identity_and_fresh_adoption_policy();
        test_legacy_identity_generation_requires_offline_migration();
        std::cout << "sync replica durable payload-store tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica durable payload-store tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
