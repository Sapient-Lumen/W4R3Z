#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_peer_ingress_wire.hpp"

#include <cstdint>
#include <limits>
#include <string>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

SyncValidationResult codec_ok() {
    return {true, ""};
}

SyncValidationResult codec_fail(const std::string& reason) {
    return {false, reason};
}

SyncValidationResult make_ingress_wire_limits(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    PeerTransportIngressWireLimits& out) {
    if (limits.max_wire_bytes == 0) {
        return codec_fail("canonical peer transport codec max_wire_bytes must be positive");
    }
    if (limits.max_string_bytes == 0) {
        return codec_fail("canonical peer transport codec max_string_bytes must be positive");
    }
    if (limits.max_response_count == 0) {
        return codec_fail("canonical peer transport codec max_response_count must be positive");
    }
    if (limits.max_total_chunk_bytes == 0) {
        return codec_fail("canonical peer transport codec max_total_chunk_bytes must be positive");
    }
    if (limits.max_chunk_bytes == 0) {
        return codec_fail("canonical peer transport codec max_chunk_bytes must be positive");
    }
    if (limits.max_wire_bytes >
        static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        return codec_fail(
            "canonical peer transport codec max_wire_bytes exceeds addressable size");
    }

    out.max_frame_bytes = limits.max_wire_bytes;
    out.max_chunk_count = limits.max_response_count;
    out.max_metadata_field_bytes = limits.max_string_bytes;
    return codec_ok();
}

SyncValidationResult validate_public_chunk_bounds(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
    const std::vector<std::string>& chunk_bytes,
    const std::string& label) {
    const SyncPeerChunkResponseBatchEnvelope& batch = envelope.peer_batch_envelope;
    SyncValidationResult bounds = sync_internal_validate_peer_transport_envelope_bounds(
        batch,
        limits.max_response_count,
        limits.max_total_chunk_bytes,
        limits.max_chunk_bytes,
        label + " declared bounds");
    if (!bounds.ok) return bounds;

    if (chunk_bytes.size() != batch.responses.size()) {
        return codec_fail(label + " response and chunk counts differ");
    }
    std::uint64_t measured_total = 0;
    for (const std::string& chunk : chunk_bytes) {
        if (chunk.size() > limits.max_chunk_bytes) {
            return codec_fail(label + " chunk exceeds max_chunk_bytes");
        }
        const std::uint64_t chunk_size = static_cast<std::uint64_t>(chunk.size());
        if (chunk_size > std::numeric_limits<std::uint64_t>::max() - measured_total) {
            return codec_fail(label + " total chunk bytes overflow uint64");
        }
        measured_total += chunk_size;
    }
    if (measured_total > limits.max_total_chunk_bytes) {
        return codec_fail(label + " total chunk bytes exceed max_total_chunk_bytes");
    }
    return codec_ok();
}

}  // namespace

SyncValidationResult encode_sync_peer_transport_canonical_payload(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    std::string& out_wire_bytes) {
    PeerTransportIngressWireLimits wire_limits;
    SyncValidationResult mapped = make_ingress_wire_limits(limits, wire_limits);
    if (!mapped.ok) return mapped;

    SyncValidationResult bounded = validate_public_chunk_bounds(
        limits, transport_envelope, chunk_bytes, "canonical peer transport encode");
    if (!bounded.ok) return bounded;

    std::string candidate;
    std::string payload_digest;
    SyncValidationResult encoded = encode_peer_transport_ingress_wire_frame(
        wire_limits, transport_envelope, chunk_bytes, candidate, payload_digest);
    if (!encoded.ok) {
        return codec_fail("canonical peer transport encode failed: " + encoded.reason);
    }
    out_wire_bytes = std::move(candidate);
    return codec_ok();
}

SyncValidationResult decode_sync_peer_transport_canonical_payload(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    const std::string& wire_bytes,
    SyncPeerTransportCanonicalPayload& out) {
    PeerTransportIngressWireLimits wire_limits;
    SyncValidationResult mapped = make_ingress_wire_limits(limits, wire_limits);
    if (!mapped.ok) return mapped;

    PeerTransportIngressWirePayload decoded;
    SyncValidationResult parsed = decode_peer_transport_ingress_wire_frame(
        wire_limits, wire_bytes, decoded);
    if (!parsed.ok) {
        return codec_fail("canonical peer transport decode failed: " + parsed.reason);
    }

    SyncValidationResult bounded = validate_public_chunk_bounds(
        limits,
        decoded.transport_envelope,
        decoded.chunk_bytes,
        "canonical peer transport decode");
    if (!bounded.ok) return bounded;

    SyncPeerTransportCanonicalPayload candidate;
    candidate.transport_envelope = std::move(decoded.transport_envelope);
    candidate.chunk_bytes = std::move(decoded.chunk_bytes);
    out = std::move(candidate);
    return codec_ok();
}

}  // namespace anonsync
