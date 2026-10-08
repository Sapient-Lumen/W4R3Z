#include "sync_peer_transport_digest_bound_frame.hpp"

#include "sha256_digest.hpp"

#include <stdexcept>
#include <utility>

namespace anonsync {

SyncPeerTransportDigestBoundFrame SyncPeerTransportDigestBoundFrame::bind(
    std::string expected_sha256,
    std::string received_bytes,
    std::uint64_t maximum_frame_bytes) {
    if (!is_lowercase_sha256_hex(expected_sha256)) {
        throw std::invalid_argument(
            "transport frame integrity requires a canonical lowercase expected SHA-256");
    }
    if (maximum_frame_bytes == 0) {
        throw std::invalid_argument(
            "transport frame integrity maximum_frame_bytes must be positive");
    }
    if (received_bytes.empty()) {
        throw std::invalid_argument(
            "transport frame integrity requires nonempty received bytes");
    }

    const std::uint64_t byte_count =
        static_cast<std::uint64_t>(received_bytes.size());
    if (static_cast<std::size_t>(byte_count) != received_bytes.size()) {
        throw std::length_error(
            "transport frame integrity received byte count exceeds uint64 range");
    }
    if (byte_count > maximum_frame_bytes) {
        throw std::length_error(
            "transport frame integrity received bytes exceed maximum_frame_bytes");
    }

    std::string observed_sha256 = sha256_hex(received_bytes);
    if (observed_sha256 != expected_sha256) {
        throw std::runtime_error(
            "transport frame integrity digest mismatch: expected=" +
            expected_sha256 + " observed=" + observed_sha256);
    }

    return SyncPeerTransportDigestBoundFrame(
        std::move(expected_sha256),
        std::move(observed_sha256),
        std::move(received_bytes),
        byte_count);
}

SyncPeerTransportDigestBoundFrame::SyncPeerTransportDigestBoundFrame(
    std::string expected_sha256,
    std::string observed_sha256,
    std::string received_bytes,
    std::uint64_t byte_count) noexcept
    : expected_sha256_(std::move(expected_sha256)),
      observed_sha256_(std::move(observed_sha256)),
      received_bytes_(std::move(received_bytes)),
      byte_count_(byte_count) {}

const std::string& SyncPeerTransportDigestBoundFrame::expected_sha256()
    const noexcept {
    return expected_sha256_;
}

const std::string& SyncPeerTransportDigestBoundFrame::observed_sha256()
    const noexcept {
    return observed_sha256_;
}

const std::string& SyncPeerTransportDigestBoundFrame::bytes() const noexcept {
    return received_bytes_;
}

std::uint64_t SyncPeerTransportDigestBoundFrame::byte_count() const noexcept {
    return byte_count_;
}

}  // namespace anonsync
