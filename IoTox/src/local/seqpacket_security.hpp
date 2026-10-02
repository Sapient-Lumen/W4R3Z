#pragma once

#include "iotox/local/control_socket.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>

namespace iotox::local::detail {

class OwnedDescriptor {
  public:
    OwnedDescriptor() = default;
    explicit OwnedDescriptor(int descriptor) noexcept;
    ~OwnedDescriptor();

    OwnedDescriptor(const OwnedDescriptor &) = delete;
    OwnedDescriptor &operator=(const OwnedDescriptor &) = delete;
    OwnedDescriptor(OwnedDescriptor &&other) noexcept;
    OwnedDescriptor &operator=(OwnedDescriptor &&other) noexcept;

    [[nodiscard]] int get() const noexcept;
    [[nodiscard]] explicit operator bool() const noexcept;
    int release() noexcept;
    void reset(int descriptor = -1) noexcept;

  private:
    int descriptor_{-1};
};

struct ReceivedSeqpacket {
    std::vector<std::uint8_t> payload;
    PeerCredentials credentials{};
    bool credentials_present{false};
    OwnedDescriptor sender_pidfd;
};

// Enables kernel-generated credentials on every subsequently received record.
// Linux 6.5+ pidfd delivery is enabled when both the build headers and running
// kernel support it. The boolean value reports whether SCM_PIDFD is required.
[[nodiscard]] Result<bool> enable_record_credentials(
    int descriptor,
    std::string_view surface);

// Accepted sockets must inherit the options from the listener. Verifying the
// inherited state is essential because a record can be queued before accept().
[[nodiscard]] Status verify_record_credentials(
    int descriptor,
    bool require_pidfd,
    std::string_view surface);

[[nodiscard]] Result<PeerCredentials> connected_peer_credentials(
    int descriptor,
    std::string_view surface);

// Linux 6.5+ can return a pidfd for the process that established a connected
// Unix-domain socket. Unlike reopening SO_PEERCRED's numeric PID, this pins the
// connection-time process identity without a PID-reuse window. An empty
// successful descriptor means the build headers or running kernel do not
// provide SO_PEERPIDFD.
[[nodiscard]] Result<OwnedDescriptor> connected_peer_pidfd(
    int descriptor,
    std::string_view surface);

// Receives one bounded SOCK_SEQPACKET record and closes every injected
// SCM_RIGHTS descriptor before returning. Control truncation, duplicate or
// malformed credential records, and every unexpected ancillary type fail
// closed. MSG_CMSG_CLOEXEC seals descriptors installed by the kernel.
[[nodiscard]] Result<ReceivedSeqpacket> receive_seqpacket(
    int descriptor,
    std::size_t maximum_payload,
    bool require_credentials,
    bool require_pidfd,
    int receive_flags,
    std::string_view surface);

[[nodiscard]] bool same_peer_credentials(
    const PeerCredentials &left,
    const PeerCredentials &right) noexcept;

// pidfd_open is a liveness fallback for kernels predating SCM_PIDFD. An empty
// successful descriptor means the running kernel lacks pidfd_open.
[[nodiscard]] Result<OwnedDescriptor> open_process_pidfd(
    std::int64_t process_id,
    std::string_view surface);

[[nodiscard]] Result<bool> pidfd_has_exited(
    int descriptor,
    std::string_view surface);

}  // namespace iotox::local::detail
