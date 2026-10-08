#pragma once

#include <cstdint>
#include <string_view>

namespace anonsync {

// One opaque, observational identity for a descriptor-backed Linux byte-stream
// socket lifetime. The descriptor number alone is not authority: close/dup2 can
// recycle it for a different open socket. The proof binds the descriptor,
// SOCK_STREAM type, fstat device/inode, and the nonzero SO_COOKIE that identifies
// the kernel socket object independently of descriptor reuse. Platforms without
// an equivalent lifetime identifier fail closed rather than weaken this contract.
//
// O_NONBLOCK is deliberately not part of lifetime identity. It is mutable I/O
// policy, while this value names the socket object that existed when observed.
// Call require_sync_stream_socket_nonblocking_or_throw() at every readiness
// frontier where nonblocking progress is required. That function exact-reproves
// the lifetime on both sides of the file-status-flag observation.
//
// This value is process-local evidence, not a serializable identifier and not
// ownership. Callers must still serialize descriptor and file-status mutation.
// Only the descriptor accessor is public because event loops need an advisory
// poll target; the identity fields deliberately remain opaque to prevent partial
// comparison.
class SyncSocketLifetimeIdentity final {
public:
    SyncSocketLifetimeIdentity(const SyncSocketLifetimeIdentity&) = default;
    SyncSocketLifetimeIdentity& operator=(
        const SyncSocketLifetimeIdentity&) = default;
    SyncSocketLifetimeIdentity(SyncSocketLifetimeIdentity&&) noexcept = default;
    SyncSocketLifetimeIdentity& operator=(
        SyncSocketLifetimeIdentity&&) noexcept = default;

    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }

    bool operator==(const SyncSocketLifetimeIdentity&) const noexcept = default;

private:
    friend SyncSocketLifetimeIdentity
    observe_sync_stream_socket_lifetime_or_throw(int, std::string_view);

    SyncSocketLifetimeIdentity(
        int descriptor,
        int socket_type,
        std::uint64_t device,
        std::uint64_t inode,
        std::uint64_t linux_socket_cookie) noexcept
        : descriptor_(descriptor),
          socket_type_(socket_type),
          device_(device),
          inode_(inode),
          linux_socket_cookie_(linux_socket_cookie) {}

    int descriptor_ = -1;
    int socket_type_ = 0;
    std::uint64_t device_ = 0U;
    std::uint64_t inode_ = 0U;
    std::uint64_t linux_socket_cookie_ = 0U;
};

[[nodiscard]] SyncSocketLifetimeIdentity
observe_sync_stream_socket_lifetime_or_throw(
    int descriptor,
    std::string_view label = "sync stream socket lifetime");

void reprove_sync_stream_socket_lifetime_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label = "sync stream socket lifetime reproof");

void require_sync_stream_socket_nonblocking_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label = "sync stream socket readiness");

// Requires FD_CLOEXEC on the exact retained socket lifetime. This is process
// inheritance hygiene rather than I/O readiness, so it remains a separate
// mutable policy check and is sandwiched by lifetime reproof just like
// O_NONBLOCK.
void require_sync_stream_socket_close_on_exec_or_throw(
    const SyncSocketLifetimeIdentity& expected,
    std::string_view label = "sync stream socket close-on-exec policy");

}  // namespace anonsync
