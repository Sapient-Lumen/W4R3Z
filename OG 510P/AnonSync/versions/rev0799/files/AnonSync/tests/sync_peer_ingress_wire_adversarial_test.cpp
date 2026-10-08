#include "peer_ingress_test_fixture.hpp"
#include "sync_peer_ingress_wire.hpp"

#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using namespace anonsync;
using anonsync::test::PeerIngressFixture;

constexpr std::string_view kWireMagic = "ANONSYNC-PEER-INGRESS";

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

void skip_length_prefixed(const std::string& frame, std::size_t& cursor) {
    if (cursor > frame.size() || frame.size() - cursor < 8) fail("test parser truncated length");
    std::uint64_t length = 0;
    for (int i = 0; i < 8; ++i) {
        length = (length << 8) | static_cast<unsigned char>(frame[cursor++]);
    }
    if (length > static_cast<std::uint64_t>(frame.size() - cursor)) {
        fail("test parser observed invalid length");
    }
    cursor += static_cast<std::size_t>(length);
}

void write_u32_be(std::string& frame, std::size_t cursor, std::uint32_t value) {
    if (cursor > frame.size() || frame.size() - cursor < 4) fail("test uint32 writer out of bounds");
    for (int shift = 24; shift >= 0; shift -= 8) {
        frame[cursor++] = static_cast<char>((value >> shift) & 0xffU);
    }
}

void write_u64_be(std::string& frame, std::size_t cursor, std::uint64_t value) {
    if (cursor > frame.size() || frame.size() - cursor < 8) fail("test uint64 writer out of bounds");
    for (int shift = 56; shift >= 0; shift -= 8) {
        frame[cursor++] = static_cast<char>((value >> shift) & 0xffU);
    }
}

std::size_t body_offset() {
    return kWireMagic.size() + 4 + 8;
}

std::size_t response_count_offset(const std::string& frame) {
    std::size_t cursor = body_offset();
    for (int i = 0; i < 4; ++i) skip_length_prefixed(frame, cursor);
    cursor += 5 * 8;  // transport validity and bounds
    for (int i = 0; i < 11; ++i) skip_length_prefixed(frame, cursor);
    if (cursor > frame.size() || frame.size() - cursor < 16) {
        fail("test parser ran past peer batch counters");
    }
    return cursor;
}

bool output_is_cleared(const PeerTransportIngressWirePayload& out) {
    return out.transport_envelope.transport_instance_id.empty() &&
           out.transport_envelope.peer_batch_envelope.responses.empty() &&
           out.chunk_bytes.empty() && out.payload_digest.empty();
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        const PeerIngressFixture fixture = anonsync::test::make_peer_ingress_fixture();
        PeerTransportIngressWireLimits limits;
        limits.max_frame_bytes = 64 * 1024;
        limits.max_chunk_count = 16;

        std::string frame;
        std::string payload_digest;
        SyncValidationResult encoded = encode_peer_transport_ingress_wire_frame(
            limits, fixture.envelope, fixture.chunks, frame, payload_digest);
        require(encoded.ok, "valid wire evidence did not encode: " + encoded.reason, checks);
        require(!frame.empty(), "valid encoder returned an empty frame", checks);
        require(payload_digest == digest_peer_transport_ingress_payload(
                                      fixture.envelope, fixture.chunks),
                "wire payload digest differs from the domain digest", checks);

        std::string second_frame;
        std::string second_digest;
        require(encode_peer_transport_ingress_wire_frame(
                    limits, fixture.envelope, fixture.chunks, second_frame, second_digest).ok,
                "second deterministic encoding failed", checks);
        require(second_frame == frame && second_digest == payload_digest,
                "same evidence did not produce identical canonical bytes", checks);

        PeerTransportIngressWirePayload decoded;
        SyncValidationResult decoded_result = decode_peer_transport_ingress_wire_frame(
            limits, frame, decoded);
        require(decoded_result.ok, "canonical frame did not decode: " + decoded_result.reason, checks);
        require(anonsync::test::same_peer_ingress_evidence(
                    decoded.transport_envelope, fixture.envelope),
                "decoded envelope differs from encoded evidence", checks);
        require(decoded.chunk_bytes == fixture.chunks,
                "decoded binary chunks differ from encoded bytes", checks);
        require(decoded.payload_digest == payload_digest,
                "decoded payload digest differs from encoded digest", checks);
        require(decoded.chunk_bytes[0].find('\0') != std::string::npos &&
                    !decoded.chunk_bytes[1].empty() && decoded.chunk_bytes[1][0] == '\0',
                "embedded NUL bytes were not preserved", checks);

        std::string round_trip;
        std::string round_trip_digest;
        require(encode_peer_transport_ingress_wire_frame(
                    limits,
                    decoded.transport_envelope,
                    decoded.chunk_bytes,
                    round_trip,
                    round_trip_digest).ok,
                "decoded evidence did not re-encode", checks);
        require(round_trip == frame && round_trip_digest == payload_digest,
                "decode/encode round trip changed canonical evidence", checks);

        for (std::size_t prefix = 0; prefix < frame.size(); ++prefix) {
            PeerTransportIngressWirePayload truncated;
            truncated.payload_digest = "sentinel";
            const SyncValidationResult result = decode_peer_transport_ingress_wire_frame(
                limits, frame.substr(0, prefix), truncated);
            require(!result.ok,
                    "truncated prefix was accepted at byte " + std::to_string(prefix), checks);
            require(output_is_cleared(truncated),
                    "failed truncation decode published partial state at byte " +
                        std::to_string(prefix), checks);
        }

        // The payload digest binds every serialized field and chunk. A single
        // changed byte must therefore be rejected, including mutations inside
        // otherwise syntactically valid metadata.
        for (std::size_t index = 0; index < frame.size(); ++index) {
            std::string mutated = frame;
            mutated[index] ^= static_cast<char>(0x01);
            PeerTransportIngressWirePayload mutation_out;
            const SyncValidationResult result = decode_peer_transport_ingress_wire_frame(
                limits, mutated, mutation_out);
            require(!result.ok,
                    "single-byte mutation was accepted at byte " + std::to_string(index), checks);
            require(output_is_cleared(mutation_out),
                    "single-byte mutation published partial state at byte " +
                        std::to_string(index), checks);
        }

        std::string trailing = frame;
        trailing.push_back('\0');
        PeerTransportIngressWirePayload failure_out;
        require(!decode_peer_transport_ingress_wire_frame(limits, trailing, failure_out).ok,
                "valid-prefix trailing byte was accepted", checks);
        require(output_is_cleared(failure_out),
                "trailing-byte failure published partial state", checks);

        std::string wrong_version = frame;
        write_u32_be(wrong_version, kWireMagic.size(),
                     kPeerTransportIngressWireCodecVersion + 1);
        require(!decode_peer_transport_ingress_wire_frame(
                    limits, wrong_version, failure_out).ok,
                "unknown wire version was accepted", checks);

        std::string wrong_body_length = frame;
        write_u64_be(wrong_body_length, kWireMagic.size() + 4,
                     static_cast<std::uint64_t>(frame.size()));
        require(!decode_peer_transport_ingress_wire_frame(
                    limits, wrong_body_length, failure_out).ok,
                "contradictory body length was accepted", checks);

        std::string forged_metadata_length = frame;
        write_u64_be(forged_metadata_length, body_offset(),
                     std::numeric_limits<std::uint64_t>::max());
        require(!decode_peer_transport_ingress_wire_frame(
                    limits, forged_metadata_length, failure_out).ok,
                "forged metadata length was accepted", checks);

        PeerTransportIngressWireLimits forged_count_limits = limits;
        forged_count_limits.max_chunk_count = 100000000ULL;
        std::string forged_count = frame;
        write_u64_be(forged_count, response_count_offset(forged_count), 100000000ULL);
        const SyncValidationResult forged_result = decode_peer_transport_ingress_wire_frame(
            forged_count_limits, forged_count, failure_out);
        require(!forged_result.ok, "forged response allocation count was accepted", checks);
        require(forged_result.reason.find("impossible") != std::string::npos,
                "forged count was not rejected by a frame-derived bound: " +
                    forged_result.reason, checks);
        require(output_is_cleared(failure_out),
                "forged count failure published partial state", checks);

        PeerTransportIngressWireLimits too_small = limits;
        too_small.max_frame_bytes = static_cast<std::uint64_t>(frame.size() - 1);
        require(!decode_peer_transport_ingress_wire_frame(too_small, frame, failure_out).ok,
                "frame exceeding max_frame_bytes was accepted", checks);

        PeerTransportIngressWireLimits one_chunk = limits;
        one_chunk.max_chunk_count = 1;
        require(!decode_peer_transport_ingress_wire_frame(one_chunk, frame, failure_out).ok,
                "frame exceeding max_chunk_count was accepted", checks);

        PeerTransportIngressWireLimits tiny_metadata = limits;
        tiny_metadata.max_metadata_field_bytes = 3;
        require(!decode_peer_transport_ingress_wire_frame(
                    tiny_metadata, frame, failure_out).ok,
                "frame exceeding metadata-field cap was accepted", checks);

        PeerIngressFixture invalid = fixture;
        invalid.envelope.peer_batch_envelope.responses[0].length += 1;
        std::string rejected_frame = "sentinel";
        std::string rejected_digest = "sentinel";
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted response/chunk length contradiction", checks);
        require(rejected_frame.empty() && rejected_digest.empty(),
                "failed encoder retained stale output", checks);

        invalid = fixture;
        invalid.envelope.peer_batch_envelope.responses[0].chunk_sha256 = sha256_hex("different");
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted response/chunk hash contradiction", checks);

        invalid = fixture;
        invalid.envelope.issued_at_epoch = 0;
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted zero issued_at_epoch", checks);

        invalid = fixture;
        invalid.envelope.expires_at_epoch = invalid.envelope.issued_at_epoch;
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted non-increasing transport validity window", checks);

        invalid = fixture;
        invalid.envelope.max_response_count = 1;
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted response count beyond transport authority", checks);

        invalid = fixture;
        invalid.envelope.peer_batch_envelope.responses[1].offset = 0;
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted overlapping response ranges", checks);

        invalid = fixture;
        invalid.envelope.peer_batch_envelope.schedule_idempotency_key.clear();
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted missing batch identity evidence", checks);

        invalid = fixture;
        invalid.envelope.peer_batch_envelope.responses[0].offset =
            std::numeric_limits<std::uint64_t>::max();
        require(!encode_peer_transport_ingress_wire_frame(
                    limits,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted overflowing response range", checks);

        invalid = fixture;
        invalid.envelope.transport_instance_id = std::string(128, 'a');
        PeerTransportIngressWireLimits short_metadata = limits;
        short_metadata.max_metadata_field_bytes = 64;
        require(!encode_peer_transport_ingress_wire_frame(
                    short_metadata,
                    invalid.envelope,
                    invalid.chunks,
                    rejected_frame,
                    rejected_digest).ok,
                "encoder accepted metadata beyond configured bound", checks);

        std::cout << "anonsync peer ingress wire adversarial checks=" << checks
                  << " frame_bytes=" << frame.size() << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "anonsync peer ingress wire adversarial test failed after "
                  << checks << " checks: " << e.what() << "\n";
        return 1;
    }
}
