#pragma once

#if !defined(_WIN32)

#include <atomic>
#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

// The numeric values are diagnostic only. Linux namespace device/inode pairs
// are live kernel evidence and must never be treated as restart-stable identity.
enum class SyncPosixMountNamespaceCapability : std::uint8_t {
    NotApplicable = 0U,
    LinuxProcfsIdentity = 1U,
};

[[nodiscard]] const char* sync_posix_mount_namespace_capability_name(
    SyncPosixMountNamespaceCapability capability) noexcept;

struct SyncPosixMountNamespaceIdentity final {
    SyncPosixMountNamespaceCapability capability =
        SyncPosixMountNamespaceCapability::NotApplicable;
    std::uint64_t device = 0U;
    std::uint64_t inode = 0U;

    bool operator==(const SyncPosixMountNamespaceIdentity&) const = default;
};

// Move-only live authority over the calling thread's mount namespace. On Linux
// this retains /proc/thread-self/ns/mnt and compares its documented st_dev/st_ino
// identity with a fresh handle on every proof. The retained descriptor pins the
// original namespace while the fresh observation proves the caller has not
// unshared or joined another mount namespace. Any failed reproof permanently
// revokes the object; returning to the original namespace cannot resurrect an
// authority after an observed mismatch. Unsupported non-Linux POSIX systems
// carry an explicit NotApplicable capability rather than inventing an identity.
// Linux inability to observe the namespace fails closed.
class SyncPosixMountNamespaceAuthority final {
public:
    SyncPosixMountNamespaceAuthority() = default;
    ~SyncPosixMountNamespaceAuthority();
    SyncPosixMountNamespaceAuthority(
        const SyncPosixMountNamespaceAuthority&) = delete;
    SyncPosixMountNamespaceAuthority& operator=(
        const SyncPosixMountNamespaceAuthority&) = delete;
    SyncPosixMountNamespaceAuthority(
        SyncPosixMountNamespaceAuthority&& other) noexcept;
    SyncPosixMountNamespaceAuthority& operator=(
        SyncPosixMountNamespaceAuthority&& other) noexcept;

    [[nodiscard]] static SyncPosixMountNamespaceAuthority capture_or_throw(
        const std::string& label = "POSIX mount namespace authority");

    [[nodiscard]] const SyncPosixMountNamespaceIdentity& identity() const
        noexcept {
        return identity_;
    }
    [[nodiscard]] bool initialized() const noexcept { return initialized_; }

    void verify_or_throw(
        std::string_view label = "POSIX mount namespace authority") const;

private:
    void reset_noexcept() noexcept;
    void transfer_from_noexcept(
        SyncPosixMountNamespaceAuthority& other) noexcept;

    int descriptor_ = -1;
    SyncPosixMountNamespaceIdentity identity_;
    bool initialized_ = false;
    // verify_or_throw may be reached concurrently by independent SQLite
    // connections sharing one VFS registration. The identity and descriptor
    // are immutable after capture; only this sticky failure latch is mutable.
    mutable std::atomic<bool> revoked_{false};
};

}  // namespace anonsync

#endif
