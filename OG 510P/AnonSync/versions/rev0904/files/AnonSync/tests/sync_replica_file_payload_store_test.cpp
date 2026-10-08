#include "inherited_test_process.hpp"
#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_replica_file_payload_store.hpp"

#if !defined(_WIN32)

#include <chrono>
#include <cerrno>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
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
                          fs::directory_iterator()) == 2,
            "clean pre-existing content did not receive exactly one durable folder marker");
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
        root / ".anonsync-payload-store-identity-v2";
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

void test_product_bound_identity_and_fresh_adoption_policy() {
    TemporaryDirectory temporary;
    const auto exact_identity = product_identity(temporary);
    const fs::path root = temporary.make_store_root("product-bound");
    const fs::path product_marker =
        root / ".anonsync-payload-store-identity-v3";
    const fs::path standalone_marker =
        root / ".anonsync-payload-store-identity-v2";

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
                    preseeded / ".anonsync-payload-store-identity-v3"),
            "failed product adoption preflight mutated the preseeded namespace");

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

void test_legacy_identity_generation_requires_offline_migration() {
    TemporaryDirectory temporary;
    const fs::path root = temporary.make_store_root("legacy-generation");
    const std::string folder = "folder-durable-payload-legacy-generation";
    const fs::path legacy_marker =
        root / ".anonsync-payload-store-identity-v1";
    const fs::path current_marker =
        root / ".anonsync-payload-store-identity-v2";
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
}

}  // namespace

int main() {
    try {
        test_existing_only_requires_explicit_bootstrap_without_mutation();
        test_publication_restart_and_exact_lookup();
        test_namespace_policy_and_limits();
        test_root_rebind_and_post_index_mutation_fail_closed();
        test_cross_process_store_lease_serializes_capacity();
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
