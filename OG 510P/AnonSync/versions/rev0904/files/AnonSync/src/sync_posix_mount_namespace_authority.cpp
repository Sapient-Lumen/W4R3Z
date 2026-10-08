#include "sync_posix_mount_namespace_authority.hpp"

#if !defined(_WIN32)

#include <cerrno>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>
#include <utility>

#if defined(__linux__)
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

#if defined(__linux__)
inline constexpr const char* kThreadMountNamespacePath =
    "/proc/thread-self/ns/mnt";

class ScopedFd final {
public:
    explicit ScopedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~ScopedFd() {
        if (descriptor_ >= 0) (void)::close(descriptor_);
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (descriptor_ >= 0) (void)::close(descriptor_);
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }

private:
    int descriptor_ = -1;
};

[[noreturn]] void throw_errno(const std::string& label,
                              const std::string& operation,
                              int error_number = errno) {
    throw std::runtime_error(label + " " + operation + " failed for " +
                             kThreadMountNamespacePath + ": " +
                             std::strerror(error_number));
}

[[nodiscard]] int namespace_open_flags() noexcept {
    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
    return flags;
}

[[nodiscard]] ScopedFd open_current_mount_namespace_or_throw(
    const std::string& label) {
    int descriptor;
    do {
        descriptor = ::open(kThreadMountNamespacePath,
                            namespace_open_flags());
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        throw_errno(label, "mount namespace open");
    }
#ifndef O_CLOEXEC
    const int existing = ::fcntl(descriptor, F_GETFD);
    if (existing < 0 ||
        ::fcntl(descriptor, F_SETFD, existing | FD_CLOEXEC) != 0) {
        const int error_number = errno;
        (void)::close(descriptor);
        throw_errno(label, "mount namespace close-on-exec", error_number);
    }
#endif
    return ScopedFd(descriptor);
}

[[nodiscard]] SyncPosixMountNamespaceIdentity identity_from_descriptor_or_throw(
    int descriptor,
    const std::string& label,
    const std::string& operation) {
    struct stat status {};
    if (::fstat(descriptor, &status) != 0) {
        throw_errno(label, operation);
    }
    SyncPosixMountNamespaceIdentity out;
    out.capability =
        SyncPosixMountNamespaceCapability::LinuxProcfsIdentity;
    out.device = static_cast<std::uint64_t>(status.st_dev);
    out.inode = static_cast<std::uint64_t>(status.st_ino);
    if (out.inode == 0U) {
        throw std::runtime_error(
            label + " mount namespace identity has a zero inode");
    }
    return out;
}
#endif

}  // namespace

const char* sync_posix_mount_namespace_capability_name(
    SyncPosixMountNamespaceCapability capability) noexcept {
    switch (capability) {
        case SyncPosixMountNamespaceCapability::NotApplicable:
            return "not-applicable";
        case SyncPosixMountNamespaceCapability::LinuxProcfsIdentity:
            return "linux-procfs-st-dev-st-ino";
    }
    return "unknown-mount-namespace-capability";
}

SyncPosixMountNamespaceAuthority::~SyncPosixMountNamespaceAuthority() {
    reset_noexcept();
}

SyncPosixMountNamespaceAuthority::SyncPosixMountNamespaceAuthority(
    SyncPosixMountNamespaceAuthority&& other) noexcept {
    transfer_from_noexcept(other);
}

SyncPosixMountNamespaceAuthority&
SyncPosixMountNamespaceAuthority::operator=(
    SyncPosixMountNamespaceAuthority&& other) noexcept {
    if (this != &other) {
        reset_noexcept();
        transfer_from_noexcept(other);
    }
    return *this;
}

SyncPosixMountNamespaceAuthority
SyncPosixMountNamespaceAuthority::capture_or_throw(
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "POSIX mount namespace authority label must not be empty");
    }

    SyncPosixMountNamespaceAuthority out;
#if defined(__linux__)
    ScopedFd descriptor = open_current_mount_namespace_or_throw(label);
    out.identity_ = identity_from_descriptor_or_throw(
        descriptor.get(), label, "retained mount namespace fstat");
    out.descriptor_ = descriptor.release();
#else
    out.identity_.capability =
        SyncPosixMountNamespaceCapability::NotApplicable;
#endif
    out.initialized_ = true;
    out.verify_or_throw(label + " initial proof");
    return out;
}

void SyncPosixMountNamespaceAuthority::verify_or_throw(
    std::string_view label_view) const {
    const std::string label(label_view);
    if (revoked_.load(std::memory_order_acquire)) {
        throw std::runtime_error(
            label + " mount namespace authority is revoked");
    }
    try {
        if (!initialized_) {
            throw std::logic_error(
                label + " mount namespace authority is not initialized");
        }
#if defined(__linux__)
        if (descriptor_ < 0 ||
            identity_.capability !=
                SyncPosixMountNamespaceCapability::LinuxProcfsIdentity) {
            throw std::logic_error(
                label + " retained Linux mount namespace identity is absent");
        }
        const SyncPosixMountNamespaceIdentity retained =
            identity_from_descriptor_or_throw(
                descriptor_, label, "retained mount namespace fstat");
        if (retained != identity_) {
            throw std::runtime_error(
                label + " retained mount namespace identity changed");
        }
        ScopedFd current = open_current_mount_namespace_or_throw(label);
        const SyncPosixMountNamespaceIdentity observed =
            identity_from_descriptor_or_throw(
                current.get(), label, "current mount namespace fstat");
        if (observed != identity_) {
            throw std::runtime_error(label + " mount namespace changed");
        }
#else
        if (descriptor_ >= 0 ||
            identity_.capability !=
                SyncPosixMountNamespaceCapability::NotApplicable ||
            identity_.device != 0U || identity_.inode != 0U) {
            throw std::logic_error(
                label + " non-Linux mount namespace state is invalid");
        }
#endif
    } catch (...) {
        revoked_.store(true, std::memory_order_release);
        throw;
    }
}

void SyncPosixMountNamespaceAuthority::reset_noexcept() noexcept {
#if defined(__linux__)
    if (descriptor_ >= 0) (void)::close(descriptor_);
#endif
    descriptor_ = -1;
    identity_ = {};
    initialized_ = false;
    revoked_.store(false, std::memory_order_relaxed);
}

void SyncPosixMountNamespaceAuthority::transfer_from_noexcept(
    SyncPosixMountNamespaceAuthority& other) noexcept {
    descriptor_ = std::exchange(other.descriptor_, -1);
    identity_ = other.identity_;
    initialized_ = other.initialized_;
    revoked_.store(
        other.revoked_.exchange(false, std::memory_order_acq_rel),
        std::memory_order_relaxed);
    other.identity_ = {};
    other.initialized_ = false;
}

}  // namespace anonsync

#endif
