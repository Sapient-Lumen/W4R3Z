#pragma once

#include "anonsync_core.hpp"

#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace anonsync {

inline constexpr std::uint32_t kPeerTransportIngressWireCodecVersion = 1;
inline constexpr std::uint64_t kPeerTransportIngressWireMaxMetadataFieldBytes = 64 * 1024;

struct PeerTransportIngressWireLimits {
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    std::uint64_t max_metadata_field_bytes = kPeerTransportIngressWireMaxMetadataFieldBytes;
};

// A successfully decoded value is self-contained: no sender-side envelope or
// transport object is needed to interpret or admit the received bytes.
struct PeerTransportIngressWirePayload {
    SyncPeerTransportBoundChunkResponseBatchEnvelope transport_envelope;
    std::vector<std::string> chunk_bytes;
    std::string payload_digest;
};

SyncValidationResult validate_peer_transport_ingress_wire_payload(
    const PeerTransportIngressWireLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    const std::string& label);

SyncValidationResult encode_peer_transport_ingress_wire_frame(
    const PeerTransportIngressWireLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    std::string& frame,
    std::string& payload_digest);

// Fail-closed and transactional: out is cleared before work and populated only
// after structural validation, digest checks, and canonical re-encoding pass.
SyncValidationResult decode_peer_transport_ingress_wire_frame(
    const PeerTransportIngressWireLimits& limits,
    const std::string& frame,
    PeerTransportIngressWirePayload& out);

void run_peer_transport_ingress_wire_codec_selftests(
    const std::function<void(bool, const std::string&)>& require);

}  // namespace anonsync
