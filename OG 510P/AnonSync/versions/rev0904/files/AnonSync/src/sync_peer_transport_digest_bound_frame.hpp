#pragma once

#include <cstdint>
#include <string>

namespace anonsync {

// Exact received transport bytes are only an observation until they match the
// digest frozen before transmission. This move-only capability publishes the
// bytes only after canonical digest shape, byte budget, and exact equality have
// all succeeded. It proves local transport integrity; it does not authenticate
// a remote peer or replace a cryptographic channel protocol.
class SyncPeerTransportDigestBoundFrame final {
public:
    [[nodiscard]] static SyncPeerTransportDigestBoundFrame bind(
        std::string expected_sha256,
        std::string received_bytes,
        std::uint64_t maximum_frame_bytes);

    SyncPeerTransportDigestBoundFrame(
        const SyncPeerTransportDigestBoundFrame&) = delete;
    SyncPeerTransportDigestBoundFrame& operator=(
        const SyncPeerTransportDigestBoundFrame&) = delete;
    SyncPeerTransportDigestBoundFrame(
        SyncPeerTransportDigestBoundFrame&&) noexcept = default;
    SyncPeerTransportDigestBoundFrame& operator=(
        SyncPeerTransportDigestBoundFrame&&) noexcept = default;

    [[nodiscard]] const std::string& expected_sha256() const noexcept;
    [[nodiscard]] const std::string& observed_sha256() const noexcept;
    [[nodiscard]] const std::string& bytes() const noexcept;
    [[nodiscard]] std::uint64_t byte_count() const noexcept;

private:
    SyncPeerTransportDigestBoundFrame(
        std::string expected_sha256,
        std::string observed_sha256,
        std::string received_bytes,
        std::uint64_t byte_count) noexcept;

    std::string expected_sha256_;
    std::string observed_sha256_;
    std::string received_bytes_;
    std::uint64_t byte_count_ = 0;
};

}  // namespace anonsync
