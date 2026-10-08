#if !defined(_WIN32)

#include "inherited_test_process.hpp"
#include "sync_directory_authority.hpp"
#include "sync_posix_directory_resolution.hpp"

#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

#if defined(__linux__)
#include <sched.h>
#include <sys/wait.h>
#endif

namespace {

namespace fs = std::filesystem;

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
            return;
        }
        std::cerr << "FAIL: " << label << '\n';
    }

    [[nodiscard]] int finish() const {
        std::cout << "sync POSIX directory resolution: " << passed_ << "/"
                  << total_ << " checks passed\n";
        return passed_ == total_ ? 0 : 1;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

class OwnedFd final {
public:
    explicit OwnedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~OwnedFd() {
        if (descriptor_ >= 0) (void)::close(descriptor_);
    }
    OwnedFd(const OwnedFd&) = delete;
    OwnedFd& operator=(const OwnedFd&) = delete;
    OwnedFd(OwnedFd&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    OwnedFd& operator=(OwnedFd&& other) noexcept {
        if (this != &other) {
            if (descriptor_ >= 0) (void)::close(descriptor_);
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }

private:
    int descriptor_ = -1;
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const fs::path base = fs::temp_directory_path();
        const auto seed = static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        for (std::uint64_t attempt = 0; attempt != 4096U; ++attempt) {
            path_ = base / ("anonsync-posix-directory-resolution-test-" +
                            std::to_string(static_cast<std::uint64_t>(
                                ::getpid())) +
                            "-" + std::to_string(seed) + "-" +
                            std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(path_, error)) {
                fs::permissions(path_, fs::perms::owner_all,
                                fs::perm_options::replace);
                return;
            }
            if (error && error != std::errc::file_exists) {
                throw std::runtime_error(
                    "temporary directory create failed: " + error.message());
            }
        }
        throw std::runtime_error("could not reserve a test directory");
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }
    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

[[nodiscard]] int directory_open_flags() noexcept {
    int flags = O_RDONLY;
#ifdef O_DIRECTORY
    flags |= O_DIRECTORY;
#endif
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    return flags;
}

[[nodiscard]] OwnedFd open_directory_or_throw(const fs::path& path) {
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), directory_open_flags());
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        throw std::system_error(errno, std::generic_category(),
                                "directory open failed for " + path.string());
    }
    return OwnedFd(descriptor);
}

template <typename Function>
[[nodiscard]] bool throws_with(Function&& function,
                               const std::string& needle) {
    try {
        std::forward<Function>(function)();
    } catch (const std::exception& error) {
        return std::string(error.what()).find(needle) != std::string::npos;
    }
    return false;
}

void exercise_probe_classifiers(TestState& state) {
    using anonsync::SyncPosixKernelProbeDisposition;
    using anonsync::sync_posix_classify_openat2_probe_result;
    using anonsync::sync_posix_classify_statx_mount_id_probe_result;

    state.check(sync_posix_classify_openat2_probe_result(7, 0) ==
                    SyncPosixKernelProbeDisposition::Available,
                "successful openat2 probe is available");
    state.check(sync_posix_classify_openat2_probe_result(-1, ENOSYS) ==
                    SyncPosixKernelProbeDisposition::ReportedUnavailable,
                "ENOSYS openat2 probe is explicitly unavailable");
    state.check(sync_posix_classify_openat2_probe_result(-1, EINVAL) ==
                    SyncPosixKernelProbeDisposition::Fatal,
                "EINVAL openat2 probe cannot silently downgrade policy");
    state.check(sync_posix_classify_openat2_probe_result(-1, EPERM) ==
                    SyncPosixKernelProbeDisposition::Fatal,
                "permission-hidden openat2 cannot silently downgrade policy");
    state.check(sync_posix_classify_openat2_probe_result(-1, EIO) ==
                    SyncPosixKernelProbeDisposition::Fatal,
                "unexpected openat2 failure is fatal");

    state.check(sync_posix_classify_statx_mount_id_probe_result(0, 0, true) ==
                    SyncPosixKernelProbeDisposition::Available,
                "statx mount-id mask proves availability");
    state.check(sync_posix_classify_statx_mount_id_probe_result(0, 0, false) ==
                    SyncPosixKernelProbeDisposition::ReportedUnavailable,
                "successful statx without mount-id mask is unavailable");
    state.check(sync_posix_classify_statx_mount_id_probe_result(-1, ENOSYS,
                                                                 false) ==
                    SyncPosixKernelProbeDisposition::ReportedUnavailable,
                "ENOSYS statx probe is explicitly unavailable");
    state.check(sync_posix_classify_statx_mount_id_probe_result(-1, EINVAL,
                                                                 false) ==
                    SyncPosixKernelProbeDisposition::Fatal,
                "unexpected statx failure cannot silently downgrade policy");
}

void exercise_component_resolution(TestState& state) {
    TemporaryDirectory temporary;
    const fs::path child = temporary.path() / "child";
    const fs::path payload = temporary.path() / "payload";
    fs::create_directory(child);
    fs::permissions(child, fs::perms::owner_all, fs::perm_options::replace);
    fs::create_directory_symlink("child", temporary.path() / "child-link");
    {
        int descriptor;
        do {
            descriptor = ::open(payload.c_str(), O_WRONLY | O_CREAT | O_EXCL,
                                S_IRUSR | S_IWUSR);
        } while (descriptor < 0 && errno == EINTR);
        if (descriptor < 0) {
            throw std::system_error(
                errno, std::generic_category(),
                "regular-file fixture create failed for " + payload.string());
        }
        OwnedFd owned_payload(descriptor);
        constexpr char bytes[] = "payload";
        ssize_t written;
        do {
            written = ::write(owned_payload.get(), bytes, sizeof(bytes) - 1U);
        } while (written < 0 && errno == EINTR);
        if (written != static_cast<ssize_t>(sizeof(bytes) - 1U)) {
            throw std::runtime_error("regular-file fixture write failed");
        }
    }
    fs::create_symlink("payload", temporary.path() / "payload-link");

    OwnedFd root = open_directory_or_throw(temporary.path());
    const auto capability =
        anonsync::sync_posix_probe_directory_resolution_capability_or_throw(
            root.get(), "test root capability");
    const auto mount_identity =
        anonsync::sync_posix_capture_mount_identity_or_throw(
            root.get(), capability, "test root mount identity");
    anonsync::sync_posix_verify_directory_resolution_capability_or_throw(
        root.get(), capability, "test stable capability");
    state.check(
        std::string(anonsync::sync_posix_directory_resolution_capability_name(
            capability)) != "unknown-directory-resolution-capability",
        "observed resolution capability has a canonical name");
    state.check(
        !anonsync::sync_posix_directory_resolution_uses_statx_mount_id(
            capability) ||
            mount_identity.available,
        "statx-capable resolution freezes a mount identity");
    const auto repeated_mount_identity =
        anonsync::sync_posix_capture_mount_identity_or_throw(
            root.get(), capability, "test repeated root mount identity");
    state.check(
        repeated_mount_identity == mount_identity,
        "repeated live mount observation preserves value and identity kind");

    if (anonsync::sync_posix_directory_resolution_uses_statx_mount_id(
            capability)) {
        const auto same_mount =
            anonsync::sync_posix_observe_relative_mount_noexcept(
                root.get(), "child", capability, mount_identity);
        state.check(
            same_mount.disposition ==
                anonsync::SyncPosixRelativeMountDisposition::RetainedMount,
            "allocation-free relative mount observation accepts a same-mount member");
        const auto absent =
            anonsync::sync_posix_observe_relative_mount_noexcept(
                root.get(), "absent", capability, mount_identity);
        state.check(
            absent.disposition ==
                    anonsync::SyncPosixRelativeMountDisposition::Absent &&
                absent.error_number == ENOENT,
            "allocation-free relative mount observation distinguishes absence");
    } else {
        state.check(
            anonsync::sync_posix_observe_relative_mount_noexcept(
                root.get(), "child", capability, mount_identity)
                    .disposition ==
                anonsync::SyncPosixRelativeMountDisposition::ProbeFailed,
            "relative mount observation fails closed without statx authority");
        state.check(true, "absence classification requires statx authority");
    }

    const auto opened = anonsync::sync_posix_open_directory_component_or_throw(
        root.get(), "child", "child",
        anonsync::SyncPosixDirectoryComponentRole::RootedDescendant,
        anonsync::SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
        capability, mount_identity, "ordinary child traversal");
    OwnedFd opened_child(opened.descriptor);
    state.check(S_ISDIR(opened.status.st_mode),
                "ordinary same-mount child opens as a directory");
    state.check(
        throws_with(
            [&] {
                (void)anonsync::sync_posix_open_directory_component_or_throw(
                    root.get(), "child-link", "child-link",
                    anonsync::SyncPosixDirectoryComponentRole::RootedDescendant,
                    anonsync::SyncPosixDirectoryMountPolicy::
                        RequireRetainedRootMount,
                    capability, mount_identity, "symlink child traversal");
            },
            "symlink"),
        "symbolic-link child is rejected before authority can advance");
    state.check(
        throws_with(
            [&] {
                (void)anonsync::sync_posix_open_directory_component_or_throw(
                    root.get(), "..", "..",
                    anonsync::SyncPosixDirectoryComponentRole::RootedDescendant,
                    anonsync::SyncPosixDirectoryMountPolicy::
                        RequireRetainedRootMount,
                    capability, mount_identity, "parent escape traversal");
            },
            "unsafe"),
        "parent escape component is rejected");

    const auto optional_payload =
        anonsync::sync_posix_open_optional_regular_file_component_or_throw(
            root.get(), "payload", "payload",
            anonsync::SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            capability, mount_identity, "optional regular-file traversal");
    state.check(optional_payload.has_value() &&
                    S_ISREG(optional_payload->status.st_mode),
                "optional regular-file traversal returns a present regular file");
    OwnedFd opened_payload(
        optional_payload.has_value() ? optional_payload->descriptor : -1);
    const auto absent_payload =
        anonsync::sync_posix_open_optional_regular_file_component_or_throw(
            root.get(), "absent-payload", "absent-payload",
            anonsync::SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            capability, mount_identity, "optional absent regular file");
    state.check(!absent_payload.has_value(),
                "optional regular-file traversal distinguishes exact absence");
    state.check(
        throws_with(
            [&] {
                (void)anonsync::
                    sync_posix_open_optional_regular_file_component_or_throw(
                        root.get(), "payload-link", "payload-link",
                        anonsync::SyncPosixDirectoryMountPolicy::
                            RequireRetainedRootMount,
                        capability, mount_identity,
                        "optional symlink regular file");
            },
            "symlink"),
        "optional regular-file traversal does not classify a symlink as absent");
    state.check(
        throws_with(
            [&] {
                (void)anonsync::
                    sync_posix_open_optional_regular_file_component_or_throw(
                        root.get(), "child", "child",
                        anonsync::SyncPosixDirectoryMountPolicy::
                            RequireRetainedRootMount,
                        capability, mount_identity,
                        "optional non-regular file");
            },
            "not a regular file"),
        "optional regular-file traversal rejects an existing directory");
    state.check(
        throws_with(
            [&] {
                (void)anonsync::sync_posix_open_regular_file_component_or_throw(
                    root.get(), "absent-payload", "absent-payload",
                    anonsync::SyncPosixDirectoryMountPolicy::
                        RequireRetainedRootMount,
                    capability, mount_identity,
                    "required absent regular file");
            },
            "inspection failed"),
        "required regular-file traversal preserves the absence error contract");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            temporary.path(), "test retained root");
    state.check(authority.resolution_capability() == capability,
                "retained authority freezes the observed live capability");
#if defined(__linux__)
    state.check(
        authority.mount_namespace_identity().capability ==
                anonsync::SyncPosixMountNamespaceCapability::
                    LinuxProcfsIdentity &&
            authority.mount_namespace_identity().inode != 0U,
        "retained authority freezes the calling thread mount namespace");
#else
    state.check(
        authority.mount_namespace_identity().capability ==
            anonsync::SyncPosixMountNamespaceCapability::NotApplicable,
        "non-Linux authority records mount namespace non-applicability");
#endif
    const auto namespace_identity = authority.mount_namespace_identity();
    authority.verify_or_throw("test retained root reproof");
    anonsync::SyncDirectoryAuthority moved = std::move(authority);
    state.check(moved.resolution_capability() == capability,
                "move transfers the frozen resolution capability");
    state.check(moved.mount_namespace_identity() == namespace_identity,
                "move transfers the frozen mount namespace identity");
    moved.verify_or_throw("test moved retained root reproof");
    state.check(true, "retained authority reproof survives move ownership");
}

void exercise_mount_namespace_revocation(TestState& state) {
#if defined(__linux__)
    TemporaryDirectory temporary;
    auto child = anonsync::test::spawn_inherited_test_process_or_throw(
        [&]() -> int {
            try {
                anonsync::SyncDirectoryAuthority authority =
                    anonsync::SyncDirectoryAuthority::open_or_throw(
                        temporary.path(), "mount namespace child authority");
                anonsync::SyncPosixMountNamespaceAuthority
                    namespace_authority =
                        anonsync::SyncPosixMountNamespaceAuthority::
                            capture_or_throw(
                                "mount namespace child primitive");
                const auto before = authority.mount_namespace_identity();
                if (before.capability !=
                        anonsync::SyncPosixMountNamespaceCapability::
                            LinuxProcfsIdentity ||
                    before.inode == 0U) {
                    return 22;
                }
                if (::unshare(CLONE_NEWUSER | CLONE_NEWNS) != 0) {
                    if (errno == EPERM || errno == EINVAL ||
                        errno == ENOSYS) {
                        return 77;
                    }
                    return 23;
                }
                struct stat current {};
                if (::stat("/proc/thread-self/ns/mnt", &current) != 0) {
                    return 24;
                }
                if (before.device ==
                        static_cast<std::uint64_t>(current.st_dev) &&
                    before.inode ==
                        static_cast<std::uint64_t>(current.st_ino)) {
                    return 25;
                }
                if (!throws_with(
                        [&] {
                            namespace_authority.verify_or_throw(
                                "mount namespace primitive changed proof");
                        },
                        "mount namespace changed")) {
                    return 26;
                }
                if (!throws_with(
                        [&] {
                            namespace_authority.verify_or_throw(
                                "mount namespace primitive sticky proof");
                        },
                        "mount namespace authority is revoked")) {
                    return 27;
                }
                if (!throws_with(
                        [&] {
                            authority.verify_or_throw(
                                "mount namespace child changed proof");
                        },
                        "mount namespace changed")) {
                    return 28;
                }
                if (!throws_with(
                        [&] {
                            authority.verify_or_throw(
                                "mount namespace child sticky proof");
                        },
                        "directory authority is revoked")) {
                    return 29;
                }
                return 0;
            } catch (...) {
                return 21;
            }
        },
        "mount namespace transition witness");

    const int status = child.wait_for_exit(
        std::chrono::seconds(10), "mount namespace transition witness");
    if (WIFEXITED(status) && WEXITSTATUS(status) == 77) {
        std::cout << "SKIP: host denies user+mount namespace unshare witness\n";
        state.check(true,
                    "host denies user+mount namespace unshare witness");
        return;
    }
    state.check(WIFEXITED(status) && WEXITSTATUS(status) == 0,
                "mount namespace transition revokes retained directory authority");
#else
    state.check(true, "mount namespace transition is not applicable");
#endif
}

void exercise_same_device_mount_boundary(TestState& state) {
#if defined(__linux__)
    std::error_code error;
    if (!fs::is_directory("/proc", error) || error ||
        !fs::is_directory("/proc/bus", error) || error) {
        std::cout << "SKIP: host has no /proc/bus directory mount witness\n";
        state.check(true,
                    "host has no /proc/bus directory mount witness");
        return;
    }

    OwnedFd proc = open_directory_or_throw("/proc");
    const auto capability =
        anonsync::sync_posix_probe_directory_resolution_capability_or_throw(
            proc.get(), "proc mount capability");
    const auto proc_mount =
        anonsync::sync_posix_capture_mount_identity_or_throw(
            proc.get(), capability, "proc mount identity");
    if (!anonsync::sync_posix_directory_resolution_uses_statx_mount_id(
            capability)) {
        std::cout << "SKIP: host lacks statx evidence for /proc/bus\n";
        state.check(true,
                    "host lacks statx evidence for the /proc/bus mount witness");
        return;
    }
    OwnedFd proc_bus = open_directory_or_throw("/proc/bus");
    const auto proc_bus_mount =
        anonsync::sync_posix_capture_mount_identity_or_throw(
            proc_bus.get(), capability, "proc bus mount identity");

    struct stat parent_status {};
    struct stat child_status {};
    if (::fstat(proc.get(), &parent_status) != 0 ||
        ::fstat(proc_bus.get(), &child_status) != 0) {
        std::cout << "SKIP: host /proc/bus witness could not be inspected\n";
        state.check(true, "host /proc/bus witness could not be inspected");
        return;
    }

    const bool same_device = parent_status.st_dev == child_status.st_dev;
    const bool distinct_mount = proc_mount.available && proc_bus_mount.available &&
                                proc_mount != proc_bus_mount;
    if (!same_device || !distinct_mount) {
        std::cout
            << "SKIP: host lacks independently observed same-device mount "
               "identity\n";
        state.check(true,
                    "host lacks an independently observed same-device mount witness");
        return;
    }

    std::cout
        << "OBSERVED: capability="
        << anonsync::sync_posix_directory_resolution_capability_name(capability)
        << " parent-mount=" << proc_mount.value
        << " child-mount=" << proc_bus_mount.value
        << " unique=" << (proc_mount.unique && proc_bus_mount.unique ? "yes" : "no")
        << " same-st_dev=yes\n";

    const auto relative_mount =
        anonsync::sync_posix_observe_relative_mount_noexcept(
            proc.get(), "bus", capability, proc_mount);
    state.check(
        relative_mount.disposition ==
            anonsync::SyncPosixRelativeMountDisposition::DifferentMount,
        "allocation-free relative observer detects the same-st_dev /proc/bus mount crossing");
    state.check(
        throws_with(
            [&] {
                const auto opened =
                    anonsync::sync_posix_open_directory_component_or_throw(
                        proc.get(), "bus", "/proc/bus",
                        anonsync::SyncPosixDirectoryComponentRole::
                            RootedDescendant,
                        anonsync::SyncPosixDirectoryMountPolicy::
                            RequireRetainedRootMount,
                        capability, proc_mount,
                        "same-device proc mount traversal");
                OwnedFd unexpected(opened.descriptor);
            },
            "mount"),
        "same-st_dev /proc/bus mount crossing is rejected");
#else
    state.check(true, "same-device Linux mount witness is not applicable");
#endif
}

}  // namespace

int main() {
    TestState state;
    try {
        exercise_probe_classifiers(state);
        exercise_component_resolution(state);
        exercise_mount_namespace_revocation(state);
        exercise_same_device_mount_boundary(state);
    } catch (const std::exception& error) {
        std::cerr << "unexpected exception: " << error.what() << '\n';
        return 1;
    }
    return state.finish();
}

#else

#include <iostream>

int main() {
    std::cout << "sync POSIX directory resolution: 1/1 checks passed\n";
    return 0;
}

#endif
