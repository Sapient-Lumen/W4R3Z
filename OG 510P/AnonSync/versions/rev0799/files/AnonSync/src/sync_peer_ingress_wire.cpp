#include "sync_peer_ingress_wire.hpp"

#include "anonsync_core_internal.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

constexpr std::string_view kWireMagic = "ANONSYNC-PEER-INGRESS";
constexpr std::size_t kWireHeaderBytes = kWireMagic.size() + 4 + 8;
constexpr std::string_view kTransportEnvelopeKeyPrefix =
    "sync-peer-transport-envelope:v1:";

// A response contains seven length-prefixed strings and two fixed-width
// integers. A corresponding chunk always contributes at least its eight-byte
// length prefix. These exact structural minima let the decoder reject an
// attacker-controlled vector count before reserve() can allocate memory that
// the received frame could never contain.
constexpr std::uint64_t kMinimumEncodedResponseBytes = 7U * 8U + 2U * 8U;
constexpr std::uint64_t kMinimumEncodedResponseAndChunkBytes =
    kMinimumEncodedResponseBytes + 8U;

SyncValidationResult wire_ok() {
    return {true, ""};
}

SyncValidationResult wire_fail(const std::string& reason) {
    return {false, reason};
}

bool add_u64_checked(std::uint64_t& total, std::uint64_t value) noexcept {
    if (value > std::numeric_limits<std::uint64_t>::max() - total) return false;
    total += value;
    return true;
}

bool size_fits_u64(std::size_t value) noexcept {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        return value <= static_cast<std::size_t>(std::numeric_limits<std::uint64_t>::max());
    }
    return true;
}

bool has_exact_namespaced_sha256(const std::string& value,
                                 std::string_view prefix) noexcept {
    if (value.size() != prefix.size() + 64U ||
        value.compare(0, prefix.size(), prefix) != 0) {
        return false;
    }
    for (std::size_t i = prefix.size(); i < value.size(); ++i) {
        const unsigned char c = static_cast<unsigned char>(value[i]);
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

void append_u32_be(std::string& out, std::uint32_t value) {
    for (int shift = 24; shift >= 0; shift -= 8) {
        out.push_back(static_cast<char>((value >> shift) & 0xffU));
    }
}

void append_u64_be(std::string& out, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(static_cast<char>((value >> shift) & 0xffU));
    }
}

void append_length_prefixed(std::string& out, const std::string& value) {
    if (!size_fits_u64(value.size())) throw std::runtime_error("wire field length exceeds uint64 range");
    append_u64_be(out, static_cast<std::uint64_t>(value.size()));
    out.append(value);
}

// Measure before allocating. The encoder accepts attacker-influenced metadata,
// so discovering the frame limit only after concatenation would allow a valid
// collection of individually bounded fields to trigger an allocation far above
// max_frame_bytes.
bool add_encoded_size_bounded(std::uint64_t& total,
                              std::uint64_t bytes,
                              std::uint64_t limit) noexcept {
    if (!add_u64_checked(total, bytes)) return false;
    return total <= limit;
}

bool add_length_prefixed_encoded_size_bounded(std::uint64_t& total,
                                              const std::string& value,
                                              std::uint64_t limit) noexcept {
    if (!size_fits_u64(value.size())) return false;
    return add_encoded_size_bounded(total, 8, limit) &&
           add_encoded_size_bounded(total, static_cast<std::uint64_t>(value.size()), limit);
}

class WireReader final {
public:
    explicit WireReader(const std::string& bytes) : bytes_(bytes) {}

    std::size_t cursor() const noexcept { return cursor_; }
    std::size_t remaining() const noexcept { return bytes_.size() - cursor_; }

    bool read_exact(std::string_view expected, std::string& reason) {
        if (remaining() < expected.size()) {
            reason = "peer ingress wire frame ended inside fixed header";
            return false;
        }
        if (!std::equal(expected.begin(), expected.end(), bytes_.begin() + static_cast<std::ptrdiff_t>(cursor_))) {
            reason = "peer ingress wire frame magic mismatch";
            return false;
        }
        cursor_ += expected.size();
        return true;
    }

    bool read_u32(std::uint32_t& value, std::string& reason) {
        if (remaining() < 4) {
            reason = "peer ingress wire frame ended while reading uint32";
            return false;
        }
        value = 0;
        for (int i = 0; i < 4; ++i) {
            value = (value << 8) | static_cast<unsigned char>(bytes_[cursor_++]);
        }
        return true;
    }

    bool read_u64(std::uint64_t& value, std::string& reason) {
        if (remaining() < 8) {
            reason = "peer ingress wire frame ended while reading uint64";
            return false;
        }
        value = 0;
        for (int i = 0; i < 8; ++i) {
            value = (value << 8) | static_cast<unsigned char>(bytes_[cursor_++]);
        }
        return true;
    }

    bool read_metadata(std::uint64_t max_bytes, std::string& value, std::string& reason) {
        return read_length_prefixed(max_bytes, "metadata field", value, reason);
    }

    bool read_chunk(std::uint64_t exact_length, std::string& value, std::string& reason) {
        std::uint64_t encoded_length = 0;
        if (!read_u64(encoded_length, reason)) return false;
        if (encoded_length != exact_length) {
            reason = "peer ingress wire frame chunk length differs from response evidence";
            return false;
        }
        if (encoded_length > static_cast<std::uint64_t>(remaining())) {
            reason = "peer ingress wire frame ended inside chunk bytes";
            return false;
        }
        if (encoded_length > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
            reason = "peer ingress wire frame chunk length exceeds addressable size";
            return false;
        }
        value.assign(bytes_.data() + cursor_, static_cast<std::size_t>(encoded_length));
        cursor_ += static_cast<std::size_t>(encoded_length);
        return true;
    }

private:
    bool read_length_prefixed(std::uint64_t max_bytes,
                              const std::string& field_kind,
                              std::string& value,
                              std::string& reason) {
        std::uint64_t length = 0;
        if (!read_u64(length, reason)) return false;
        if (length > max_bytes) {
            reason = "peer ingress wire frame " + field_kind + " exceeds configured bound";
            return false;
        }
        if (length > static_cast<std::uint64_t>(remaining())) {
            reason = "peer ingress wire frame ended inside length-prefixed " + field_kind;
            return false;
        }
        if (length > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
            reason = "peer ingress wire frame " + field_kind + " exceeds addressable size";
            return false;
        }
        value.assign(bytes_.data() + cursor_, static_cast<std::size_t>(length));
        cursor_ += static_cast<std::size_t>(length);
        return true;
    }

    const std::string& bytes_;
    std::size_t cursor_ = 0;
};

bool metadata_field_within_limit(const std::string& value,
                                 std::uint64_t max_bytes,
                                 const std::string& field,
                                 std::string& reason) {
    if (value.size() > max_bytes) {
        reason = "peer ingress wire " + field + " exceeds metadata field bound";
        return false;
    }
    return true;
}

bool required_metadata_field(const std::string& value,
                             std::uint64_t max_bytes,
                             const std::string& field,
                             std::string& reason) {
    if (value.empty()) {
        reason = "peer ingress wire " + field + " is required";
        return false;
    }
    return metadata_field_within_limit(value, max_bytes, field, reason);
}

SyncValidationResult validate_limits(const PeerTransportIngressWireLimits& limits) {
    if (limits.max_frame_bytes < kWireHeaderBytes) {
        return wire_fail("peer ingress wire max_frame_bytes is smaller than the fixed header");
    }
    if (limits.max_chunk_count == 0) {
        return wire_fail("peer ingress wire max_chunk_count must be positive");
    }
    if (limits.max_metadata_field_bytes == 0) {
        return wire_fail("peer ingress wire max_metadata_field_bytes must be positive");
    }
    if (limits.max_frame_bytes > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        return wire_fail("peer ingress wire max_frame_bytes exceeds addressable size");
    }
    const std::uint64_t body_bytes =
        limits.max_frame_bytes - static_cast<std::uint64_t>(kWireHeaderBytes);
    if (limits.max_chunk_count >
        body_bytes / kMinimumEncodedResponseAndChunkBytes) {
        return wire_fail(
            "peer ingress wire max_chunk_count is impossible for max_frame_bytes");
    }
    return wire_ok();
}

void append_response(std::string& body, const SyncChunkResponseEnvelope& response) {
    append_length_prefixed(body, response.path.value);
    append_length_prefixed(body, response.request_idempotency_key);
    append_length_prefixed(body, response.response_idempotency_key);
    append_length_prefixed(body, response.remote_entry_digest);
    append_length_prefixed(body, response.remote_version_digest);
    append_length_prefixed(body, response.apply_entry_idempotency_key);
    append_u64_be(body, response.offset);
    append_u64_be(body, response.length);
    append_length_prefixed(body, response.chunk_sha256);
}

bool measure_response_encoded_size_bounded(std::uint64_t& total,
                                           const SyncChunkResponseEnvelope& response,
                                           std::uint64_t limit) noexcept {
    return add_length_prefixed_encoded_size_bounded(total, response.path.value, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.request_idempotency_key, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.response_idempotency_key, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.remote_entry_digest, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.remote_version_digest, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.apply_entry_idempotency_key, limit) &&
           add_encoded_size_bounded(total, 16, limit) &&
           add_length_prefixed_encoded_size_bounded(total, response.chunk_sha256, limit);
}

bool measure_envelope_encoded_size_bounded(
    std::uint64_t& total,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
    std::uint64_t limit) noexcept {
    if (!add_length_prefixed_encoded_size_bounded(total, envelope.transport_instance_id, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, envelope.transport_key_id, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, envelope.transport_envelope_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, envelope.transport_mac_sha256, limit) ||
        !add_encoded_size_bounded(total, 40, limit)) {
        return false;
    }

    const auto& batch = envelope.peer_batch_envelope;
    if (!add_length_prefixed_encoded_size_bounded(total, batch.path.value, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.request_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.schedule_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.peer_id, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.peer_session_id, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.peer_request_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.peer_response_batch_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.batch_idempotency_key, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.remote_entry_digest, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.remote_version_digest, limit) ||
        !add_length_prefixed_encoded_size_bounded(total, batch.apply_entry_idempotency_key, limit) ||
        !add_encoded_size_bounded(total, 16, limit)) {
        return false;
    }
    for (const auto& response : batch.responses) {
        if (!measure_response_encoded_size_bounded(total, response, limit)) return false;
    }
    return true;
}

bool measure_payload_body_encoded_size_bounded(
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
    const std::vector<std::string>& chunk_bytes,
    const std::string& payload_digest,
    std::uint64_t limit,
    std::uint64_t& measured) noexcept {
    measured = 0;
    if (!measure_envelope_encoded_size_bounded(measured, envelope, limit) ||
        !add_length_prefixed_encoded_size_bounded(measured, payload_digest, limit) ||
        !add_encoded_size_bounded(measured, 16, limit)) {
        return false;
    }
    for (const auto& chunk : chunk_bytes) {
        if (!add_length_prefixed_encoded_size_bounded(measured, chunk, limit)) return false;
    }
    return true;
}

void append_envelope(std::string& body,
                     const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope) {
    append_length_prefixed(body, envelope.transport_instance_id);
    append_length_prefixed(body, envelope.transport_key_id);
    append_length_prefixed(body, envelope.transport_envelope_idempotency_key);
    append_length_prefixed(body, envelope.transport_mac_sha256);
    append_u64_be(body, envelope.issued_at_epoch);
    append_u64_be(body, envelope.expires_at_epoch);
    append_u64_be(body, envelope.max_response_count);
    append_u64_be(body, envelope.max_total_bytes);
    append_u64_be(body, envelope.max_chunk_bytes);

    const auto& batch = envelope.peer_batch_envelope;
    append_length_prefixed(body, batch.path.value);
    append_length_prefixed(body, batch.request_idempotency_key);
    append_length_prefixed(body, batch.schedule_idempotency_key);
    append_length_prefixed(body, batch.peer_id);
    append_length_prefixed(body, batch.peer_session_id);
    append_length_prefixed(body, batch.peer_request_idempotency_key);
    append_length_prefixed(body, batch.peer_response_batch_idempotency_key);
    append_length_prefixed(body, batch.batch_idempotency_key);
    append_length_prefixed(body, batch.remote_entry_digest);
    append_length_prefixed(body, batch.remote_version_digest);
    append_length_prefixed(body, batch.apply_entry_idempotency_key);
    append_u64_be(body, batch.response_count);
    append_u64_be(body, batch.total_bytes);
    for (const auto& response : batch.responses) append_response(body, response);
}

SyncValidationResult encode_validated_payload(
    const PeerTransportIngressWireLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
    const std::vector<std::string>& chunk_bytes,
    const std::string& payload_digest,
    std::string& frame) {
    try {
        const std::uint64_t body_limit =
            limits.max_frame_bytes - static_cast<std::uint64_t>(kWireHeaderBytes);
        std::uint64_t measured_body_bytes = 0;
        if (!measure_payload_body_encoded_size_bounded(
                envelope, chunk_bytes, payload_digest, body_limit, measured_body_bytes)) {
            return wire_fail("peer ingress wire frame exceeds max_frame_bytes before allocation");
        }

        std::string body;
        body.reserve(static_cast<std::size_t>(measured_body_bytes));
        append_envelope(body, envelope);
        append_length_prefixed(body, payload_digest);
        append_u64_be(body, static_cast<std::uint64_t>(chunk_bytes.size()));
        append_u64_be(body, envelope.peer_batch_envelope.total_bytes);
        for (const auto& chunk : chunk_bytes) append_length_prefixed(body, chunk);
        if (body.size() != static_cast<std::size_t>(measured_body_bytes)) {
            throw std::runtime_error("wire encoder measured size differs from canonical body bytes");
        }

        std::string candidate;
        candidate.reserve(kWireHeaderBytes + body.size());
        candidate.append(kWireMagic.data(), kWireMagic.size());
        append_u32_be(candidate, kPeerTransportIngressWireCodecVersion);
        append_u64_be(candidate, static_cast<std::uint64_t>(body.size()));
        candidate.append(body);
        frame = std::move(candidate);
        return wire_ok();
    } catch (const std::bad_alloc&) {
        return wire_fail("peer ingress wire encoder allocation failed");
    } catch (const std::exception& e) {
        return wire_fail(std::string("peer ingress wire encode failed: ") + e.what());
    }
}

bool read_response(WireReader& reader,
                   std::uint64_t metadata_limit,
                   SyncChunkResponseEnvelope& response,
                   std::string& reason) {
    return reader.read_metadata(metadata_limit, response.path.value, reason) &&
           reader.read_metadata(metadata_limit, response.request_idempotency_key, reason) &&
           reader.read_metadata(metadata_limit, response.response_idempotency_key, reason) &&
           reader.read_metadata(metadata_limit, response.remote_entry_digest, reason) &&
           reader.read_metadata(metadata_limit, response.remote_version_digest, reason) &&
           reader.read_metadata(metadata_limit, response.apply_entry_idempotency_key, reason) &&
           reader.read_u64(response.offset, reason) &&
           reader.read_u64(response.length, reason) &&
           reader.read_metadata(metadata_limit, response.chunk_sha256, reason);
}

bool read_envelope(WireReader& reader,
                   const PeerTransportIngressWireLimits& limits,
                   SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
                   std::string& reason) {
    if (!reader.read_metadata(limits.max_metadata_field_bytes, envelope.transport_instance_id, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, envelope.transport_key_id, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, envelope.transport_envelope_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, envelope.transport_mac_sha256, reason) ||
        !reader.read_u64(envelope.issued_at_epoch, reason) ||
        !reader.read_u64(envelope.expires_at_epoch, reason) ||
        !reader.read_u64(envelope.max_response_count, reason) ||
        !reader.read_u64(envelope.max_total_bytes, reason) ||
        !reader.read_u64(envelope.max_chunk_bytes, reason)) {
        return false;
    }

    auto& batch = envelope.peer_batch_envelope;
    if (!reader.read_metadata(limits.max_metadata_field_bytes, batch.path.value, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.request_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.schedule_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.peer_id, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.peer_session_id, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.peer_request_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.peer_response_batch_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.batch_idempotency_key, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.remote_entry_digest, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.remote_version_digest, reason) ||
        !reader.read_metadata(limits.max_metadata_field_bytes, batch.apply_entry_idempotency_key, reason) ||
        !reader.read_u64(batch.response_count, reason) ||
        !reader.read_u64(batch.total_bytes, reason)) {
        return false;
    }
    if (batch.response_count == 0) {
        reason = "peer ingress wire frame requires at least one response";
        return false;
    }
    if (batch.response_count > limits.max_chunk_count) {
        reason = "peer ingress wire response count exceeds max_chunk_count";
        return false;
    }
    if (batch.response_count > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        reason = "peer ingress wire response count exceeds addressable size";
        return false;
    }
    // Seven response length prefixes, two fixed integers, and one later chunk
    // length prefix are present for every pair even when all encoded values are
    // empty. The remaining frame must be able to encode both vectors before a
    // forged response count is allowed to reach reserve().
    if (batch.response_count >
        static_cast<std::uint64_t>(reader.remaining()) /
            kMinimumEncodedResponseAndChunkBytes) {
        reason = "peer ingress wire response count is impossible for remaining frame bytes";
        return false;
    }
    try {
        batch.responses.reserve(static_cast<std::size_t>(batch.response_count));
        for (std::uint64_t i = 0; i < batch.response_count; ++i) {
            SyncChunkResponseEnvelope response;
            if (!read_response(reader, limits.max_metadata_field_bytes, response, reason)) return false;
            batch.responses.push_back(std::move(response));
        }
    } catch (const std::bad_alloc&) {
        reason = "peer ingress wire response allocation failed";
        return false;
    }
    return true;
}

std::size_t codec_version_offset() noexcept {
    return kWireMagic.size();
}

void skip_length_prefixed_for_selftest(const std::string& frame,
                                       std::size_t& cursor) {
    if (cursor > frame.size() || frame.size() - cursor < 8) {
        throw std::runtime_error("wire selftest parser ended inside field length");
    }
    std::uint64_t length = 0;
    for (int i = 0; i < 8; ++i) {
        length = (length << 8) |
                 static_cast<unsigned char>(frame[cursor++]);
    }
    if (length > static_cast<std::uint64_t>(frame.size() - cursor)) {
        throw std::runtime_error("wire selftest parser found impossible field length");
    }
    cursor += static_cast<std::size_t>(length);
}

std::size_t response_count_offset_for_selftest(const std::string& frame) {
    std::size_t cursor = kWireHeaderBytes;
    for (int i = 0; i < 4; ++i) skip_length_prefixed_for_selftest(frame, cursor);
    if (cursor > frame.size() || frame.size() - cursor < 5U * 8U) {
        throw std::runtime_error("wire selftest parser ended inside transport integers");
    }
    cursor += 5U * 8U;
    for (int i = 0; i < 11; ++i) skip_length_prefixed_for_selftest(frame, cursor);
    if (cursor > frame.size() || frame.size() - cursor < 8) {
        throw std::runtime_error("wire selftest parser did not reach response count");
    }
    return cursor;
}

void overwrite_u64_be_for_selftest(std::string& frame,
                                   std::size_t cursor,
                                   std::uint64_t value) {
    if (cursor > frame.size() || frame.size() - cursor < 8) {
        throw std::runtime_error("wire selftest writer is out of bounds");
    }
    for (int shift = 56; shift >= 0; shift -= 8) {
        frame[cursor++] = static_cast<char>((value >> shift) & 0xffU);
    }
}

}  // namespace

SyncValidationResult validate_peer_transport_ingress_wire_payload(
    const PeerTransportIngressWireLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    const std::string& label) {
    SyncValidationResult limits_result = validate_limits(limits);
    if (!limits_result.ok) return limits_result;

    const auto fail = [&](const std::string& detail) {
        return wire_fail(label + ": " + detail);
    };
    const auto& batch = transport_envelope.peer_batch_envelope;
    std::string reason;

    const std::array<std::pair<const std::string*, const char*>, 15> required_fields{{
        {&transport_envelope.transport_instance_id, "transport_instance_id"},
        {&transport_envelope.transport_key_id, "transport_key_id"},
        {&transport_envelope.transport_envelope_idempotency_key, "transport_envelope_idempotency_key"},
        {&transport_envelope.transport_mac_sha256, "transport_mac_sha256"},
        {&batch.path.value, "peer batch path"},
        {&batch.request_idempotency_key, "request_idempotency_key"},
        {&batch.schedule_idempotency_key, "schedule_idempotency_key"},
        {&batch.peer_id, "peer_id"},
        {&batch.peer_session_id, "peer_session_id"},
        {&batch.peer_request_idempotency_key, "peer_request_idempotency_key"},
        {&batch.peer_response_batch_idempotency_key, "peer_response_batch_idempotency_key"},
        {&batch.batch_idempotency_key, "batch_idempotency_key"},
        {&batch.remote_entry_digest, "remote_entry_digest"},
        {&batch.remote_version_digest, "remote_version_digest"},
        {&batch.apply_entry_idempotency_key, "apply_entry_idempotency_key"}
    }};
    for (const auto& [field, name] : required_fields) {
        if (!required_metadata_field(*field, limits.max_metadata_field_bytes, name, reason)) return fail(reason);
    }
    if (!sync_internal_valid_sync_id(transport_envelope.transport_instance_id) ||
        !sync_internal_valid_sync_id(transport_envelope.transport_key_id)) {
        return fail("transport identity fields are not lowercase portable sync ids");
    }
    if (!sync_internal_valid_sync_id(batch.peer_id) || !sync_internal_valid_sync_id(batch.peer_session_id)) {
        return fail("peer identity fields are not lowercase portable sync ids");
    }
    if (!has_exact_namespaced_sha256(
            transport_envelope.transport_envelope_idempotency_key,
            kTransportEnvelopeKeyPrefix)) {
        return fail(
            "transport envelope idempotency key is not an exact namespaced SHA-256 identity");
    }
    if (!is_lowercase_sha256_hex(transport_envelope.transport_mac_sha256)) {
        return fail("transport_mac_sha256 is not lowercase SHA-256 evidence");
    }
    if (!is_lowercase_sha256_hex(batch.remote_entry_digest) ||
        !is_lowercase_sha256_hex(batch.remote_version_digest)) {
        return fail("peer batch remote entry/version evidence is not lowercase SHA-256");
    }
    NormalizedSyncPath normalized_path;
    SyncValidationResult path_result = normalize_sync_relative_path(batch.path.value, normalized_path);
    if (!path_result.ok || normalized_path.value != batch.path.value) {
        return fail("peer batch path is not a canonical normalized sync path");
    }
    if (transport_envelope.issued_at_epoch == 0 ||
        transport_envelope.expires_at_epoch <= transport_envelope.issued_at_epoch) {
        return fail("transport validity window is invalid");
    }
    if (transport_envelope.max_response_count == 0 ||
        transport_envelope.max_total_bytes == 0 ||
        transport_envelope.max_chunk_bytes == 0) {
        return fail("transport envelope carries an unbounded limit");
    }
    if (batch.response_count > limits.max_chunk_count) {
        return fail("response count exceeds codec max_chunk_count");
    }

    SyncValidationResult bounds = sync_internal_validate_peer_transport_envelope_bounds(
        batch,
        transport_envelope.max_response_count,
        transport_envelope.max_total_bytes,
        transport_envelope.max_chunk_bytes,
        label);
    if (!bounds.ok) return bounds;
    if (batch.responses.size() != chunk_bytes.size()) {
        return fail("chunk byte count does not match response evidence count");
    }

    std::uint64_t measured_total = 0;
    std::uint64_t previous_end = 0;
    bool have_previous = false;
    for (std::size_t i = 0; i < batch.responses.size(); ++i) {
        const auto& response = batch.responses[i];
        const auto& chunk = chunk_bytes[i];
        const std::array<std::pair<const std::string*, const char*>, 7> response_fields{{
            {&response.path.value, "response path"},
            {&response.request_idempotency_key, "response request_idempotency_key"},
            {&response.response_idempotency_key, "response_idempotency_key"},
            {&response.remote_entry_digest, "response remote_entry_digest"},
            {&response.remote_version_digest, "response remote_version_digest"},
            {&response.apply_entry_idempotency_key, "response apply_entry_idempotency_key"},
            {&response.chunk_sha256, "response chunk_sha256"}
        }};
        for (const auto& [field, name] : response_fields) {
            if (!required_metadata_field(*field, limits.max_metadata_field_bytes, name, reason)) return fail(reason);
        }
        if (response.path.value != batch.path.value ||
            response.request_idempotency_key != batch.request_idempotency_key ||
            response.remote_entry_digest != batch.remote_entry_digest ||
            response.remote_version_digest != batch.remote_version_digest ||
            response.apply_entry_idempotency_key != batch.apply_entry_idempotency_key) {
            return fail("response evidence does not inherit the enclosing peer batch identity");
        }
        if (!is_lowercase_sha256_hex(response.chunk_sha256)) {
            return fail("response chunk_sha256 is not lowercase SHA-256 evidence");
        }
        if (!is_lowercase_sha256_hex(response.remote_entry_digest) ||
            !is_lowercase_sha256_hex(response.remote_version_digest)) {
            return fail("response remote entry/version evidence is not lowercase SHA-256");
        }
        if (response.length != static_cast<std::uint64_t>(chunk.size())) {
            return fail("received chunk length differs from response evidence");
        }
        if (sha256_hex(chunk) != response.chunk_sha256) {
            return fail("received chunk hash differs from response evidence");
        }
        if (response.offset > std::numeric_limits<std::uint64_t>::max() - response.length) {
            return fail("response chunk range overflows uint64");
        }
        const std::uint64_t response_end = response.offset + response.length;
        if (have_previous && response.offset < previous_end) {
            return fail("response chunks are not ordered and non-overlapping");
        }
        previous_end = response_end;
        have_previous = true;
        if (!add_u64_checked(measured_total, static_cast<std::uint64_t>(chunk.size()))) {
            return fail("received chunk byte total overflows uint64");
        }
    }
    if (measured_total != batch.total_bytes) {
        return fail("received chunk byte total differs from peer batch total_bytes");
    }
    return wire_ok();
}

SyncValidationResult encode_peer_transport_ingress_wire_frame(
    const PeerTransportIngressWireLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    std::string& frame,
    std::string& payload_digest) {
    frame.clear();
    payload_digest.clear();
    SyncValidationResult valid = validate_peer_transport_ingress_wire_payload(
        limits, transport_envelope, chunk_bytes, "peer ingress wire encode");
    if (!valid.ok) return valid;
    try {
        const std::string digest = digest_peer_transport_ingress_payload(transport_envelope, chunk_bytes);
        std::string candidate;
        SyncValidationResult encoded = encode_validated_payload(
            limits, transport_envelope, chunk_bytes, digest, candidate);
        if (!encoded.ok) return encoded;
        frame = std::move(candidate);
        payload_digest = digest;
        return wire_ok();
    } catch (const std::bad_alloc&) {
        return wire_fail("peer ingress wire encoder allocation failed");
    } catch (const std::exception& e) {
        return wire_fail(std::string("peer ingress wire encode failed: ") + e.what());
    }
}

SyncValidationResult decode_peer_transport_ingress_wire_frame(
    const PeerTransportIngressWireLimits& limits,
    const std::string& frame,
    PeerTransportIngressWirePayload& out) {
    out = PeerTransportIngressWirePayload{};
    SyncValidationResult limits_result = validate_limits(limits);
    if (!limits_result.ok) return limits_result;
    if (frame.empty()) return wire_fail("peer ingress wire frame is empty");
    if (frame.size() > limits.max_frame_bytes) {
        return wire_fail("peer ingress wire frame exceeds max_frame_bytes");
    }
    if (frame.size() < kWireHeaderBytes) {
        return wire_fail("peer ingress wire frame is shorter than the fixed header");
    }

    try {
        WireReader reader(frame);
        std::string reason;
        if (!reader.read_exact(kWireMagic, reason)) return wire_fail(reason);
        std::uint32_t version = 0;
        if (!reader.read_u32(version, reason)) return wire_fail(reason);
        if (version != kPeerTransportIngressWireCodecVersion) {
            return wire_fail("peer ingress wire frame codec version is unsupported");
        }
        std::uint64_t declared_body_bytes = 0;
        if (!reader.read_u64(declared_body_bytes, reason)) return wire_fail(reason);
        if (declared_body_bytes != static_cast<std::uint64_t>(reader.remaining())) {
            return wire_fail("peer ingress wire frame body length does not match received bytes");
        }

        PeerTransportIngressWirePayload candidate;
        if (!read_envelope(reader, limits, candidate.transport_envelope, reason)) {
            return wire_fail(reason);
        }
        if (!reader.read_metadata(limits.max_metadata_field_bytes, candidate.payload_digest, reason)) {
            return wire_fail(reason);
        }
        if (!is_lowercase_sha256_hex(candidate.payload_digest)) {
            return wire_fail("peer ingress wire frame payload_digest is not lowercase SHA-256 evidence");
        }

        std::uint64_t chunk_count = 0;
        std::uint64_t declared_chunk_bytes = 0;
        if (!reader.read_u64(chunk_count, reason) || !reader.read_u64(declared_chunk_bytes, reason)) {
            return wire_fail(reason);
        }
        if (chunk_count != candidate.transport_envelope.peer_batch_envelope.response_count) {
            return wire_fail("peer ingress wire frame chunk count differs from response count");
        }
        if (chunk_count > limits.max_chunk_count) {
            return wire_fail("peer ingress wire frame chunk count exceeds max_chunk_count");
        }
        if (declared_chunk_bytes != candidate.transport_envelope.peer_batch_envelope.total_bytes) {
            return wire_fail("peer ingress wire frame declared chunk bytes differ from peer batch total_bytes");
        }
        if (chunk_count > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
            return wire_fail("peer ingress wire frame chunk count exceeds addressable size");
        }
        // Every chunk has an eight-byte length prefix. This frame-derived
        // bound is independent of configured caps and prevents a forged count
        // from reaching vector::reserve with an impossible allocation size.
        if (chunk_count > static_cast<std::uint64_t>(reader.remaining()) / 8) {
            return wire_fail(
                "peer ingress wire frame chunk count is impossible for the remaining frame bytes");
        }
        candidate.chunk_bytes.reserve(static_cast<std::size_t>(chunk_count));
        std::uint64_t measured_chunk_bytes = 0;
        for (std::uint64_t i = 0; i < chunk_count; ++i) {
            const std::uint64_t expected_length =
                candidate.transport_envelope.peer_batch_envelope.responses[static_cast<std::size_t>(i)].length;
            std::string chunk;
            if (!reader.read_chunk(expected_length, chunk, reason)) return wire_fail(reason);
            if (!add_u64_checked(measured_chunk_bytes, expected_length)) {
                return wire_fail("peer ingress wire frame chunk byte total overflows uint64");
            }
            candidate.chunk_bytes.push_back(std::move(chunk));
        }
        if (measured_chunk_bytes != declared_chunk_bytes) {
            return wire_fail("peer ingress wire frame measured chunk bytes differ from declaration");
        }
        if (reader.cursor() != frame.size()) {
            return wire_fail("peer ingress wire frame has trailing bytes");
        }

        SyncValidationResult valid = validate_peer_transport_ingress_wire_payload(
            limits,
            candidate.transport_envelope,
            candidate.chunk_bytes,
            "peer ingress wire decode");
        if (!valid.ok) return valid;
        const std::string computed_payload_digest = digest_peer_transport_ingress_payload(
            candidate.transport_envelope, candidate.chunk_bytes);
        if (computed_payload_digest != candidate.payload_digest) {
            return wire_fail("peer ingress wire frame payload digest does not match decoded evidence");
        }

        std::string canonical_frame;
        SyncValidationResult canonical = encode_validated_payload(
            limits,
            candidate.transport_envelope,
            candidate.chunk_bytes,
            candidate.payload_digest,
            canonical_frame);
        if (!canonical.ok) return canonical;
        if (canonical_frame != frame) {
            return wire_fail("peer ingress wire frame is not the canonical encoding of its decoded evidence");
        }

        out = std::move(candidate);
        return wire_ok();
    } catch (const std::bad_alloc&) {
        out = PeerTransportIngressWirePayload{};
        return wire_fail("peer ingress wire decoder allocation failed");
    } catch (const std::exception& e) {
        out = PeerTransportIngressWirePayload{};
        return wire_fail(std::string("peer ingress wire decode failed: ") + e.what());
    }
}

void run_peer_transport_ingress_wire_codec_selftests(
    const std::function<void(bool, const std::string&)>& require) {
    PeerTransportIngressWireLimits limits;
    limits.max_frame_bytes = 64 * 1024;
    limits.max_chunk_count = 4;

    const std::string chunk("A\0B\xff", 4);
    SyncChunkResponseEnvelope response;
    response.path.value = "docs/wire.bin";
    response.request_idempotency_key = "request:v1:test";
    response.response_idempotency_key = "response:v1:test";
    response.remote_entry_digest = sha256_hex("wire-selftest-remote-entry");
    response.remote_version_digest = sha256_hex("wire-selftest-remote-version");
    response.apply_entry_idempotency_key = "apply:v1:test";
    response.offset = 0;
    response.length = static_cast<std::uint64_t>(chunk.size());
    response.chunk_sha256 = sha256_hex(chunk);

    SyncPeerChunkResponseBatchEnvelope batch;
    batch.path = response.path;
    batch.request_idempotency_key = response.request_idempotency_key;
    batch.schedule_idempotency_key = "schedule:v1:test";
    batch.peer_id = "peer-alpha";
    batch.peer_session_id = "session-alpha";
    batch.peer_request_idempotency_key = "peer-request:v1:test";
    batch.peer_response_batch_idempotency_key = "peer-batch:v1:test";
    batch.batch_idempotency_key = "batch:v1:test";
    batch.remote_entry_digest = response.remote_entry_digest;
    batch.remote_version_digest = response.remote_version_digest;
    batch.apply_entry_idempotency_key = response.apply_entry_idempotency_key;
    batch.response_count = 1;
    batch.total_bytes = response.length;
    batch.responses = {response};

    SyncPeerTransportBoundChunkResponseBatchEnvelope envelope;
    envelope.peer_batch_envelope = batch;
    envelope.transport_instance_id = "transport-alpha";
    envelope.transport_key_id = "transport-key-alpha";
    envelope.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:" + sha256_hex("wire-selftest-envelope");
    envelope.transport_mac_sha256 = sha256_hex("wire-selftest-mac-shape");
    envelope.issued_at_epoch = 10;
    envelope.expires_at_epoch = 20;
    envelope.max_response_count = 1;
    envelope.max_total_bytes = response.length;
    envelope.max_chunk_bytes = response.length;

    std::string frame;
    std::string payload_digest;
    require(encode_peer_transport_ingress_wire_frame(limits, envelope, {chunk}, frame, payload_digest).ok &&
                !frame.empty() && is_lowercase_sha256_hex(payload_digest),
            "peer ingress wire codec encodes one complete canonical evidence object");

    std::string second_frame;
    std::string second_payload_digest;
    require(encode_peer_transport_ingress_wire_frame(
                limits, envelope, {chunk}, second_frame, second_payload_digest).ok &&
                second_frame == frame && second_payload_digest == payload_digest,
            "peer ingress wire codec deterministically reproduces canonical bytes");

    PeerTransportIngressWirePayload decoded;
    require(decode_peer_transport_ingress_wire_frame(limits, frame, decoded).ok &&
                decoded.payload_digest == payload_digest &&
                decoded.transport_envelope.transport_envelope_idempotency_key ==
                    envelope.transport_envelope_idempotency_key &&
                decoded.chunk_bytes.size() == 1 && decoded.chunk_bytes[0] == chunk,
            "peer ingress wire codec round-trips exact binary bytes without ambient sender state");

    bool every_truncation_rejected = true;
    for (std::size_t size = 0; size < frame.size(); ++size) {
        PeerTransportIngressWirePayload truncated_out;
        if (decode_peer_transport_ingress_wire_frame(limits, frame.substr(0, size), truncated_out).ok ||
            !truncated_out.chunk_bytes.empty() ||
            !truncated_out.transport_envelope.transport_instance_id.empty()) {
            every_truncation_rejected = false;
            break;
        }
    }
    require(every_truncation_rejected,
            "peer ingress wire codec rejects every one-byte truncation without publishing partial state");

    std::string trailing = frame;
    trailing.push_back('\0');
    PeerTransportIngressWirePayload trailing_out;
    require(!decode_peer_transport_ingress_wire_frame(limits, trailing, trailing_out).ok,
            "peer ingress wire codec rejects valid-prefix trailing bytes");

    std::string unknown_version = frame;
    unknown_version[codec_version_offset() + 3] = static_cast<char>(2);
    PeerTransportIngressWirePayload unknown_version_out;
    require(!decode_peer_transport_ingress_wire_frame(limits, unknown_version, unknown_version_out).ok,
            "peer ingress wire codec rejects unknown versions");

    std::string corrupt_chunk = frame;
    corrupt_chunk.back() = corrupt_chunk.back() == 'x' ? 'y' : 'x';
    PeerTransportIngressWirePayload corrupt_chunk_out;
    require(!decode_peer_transport_ingress_wire_frame(limits, corrupt_chunk, corrupt_chunk_out).ok,
            "peer ingress wire codec rejects chunk corruption against response evidence");

    PeerTransportIngressWireLimits forged_count_limits = limits;
    forged_count_limits.max_chunk_count = 800;
    std::string forged_count = frame;
    overwrite_u64_be_for_selftest(
        forged_count,
        response_count_offset_for_selftest(forged_count),
        800);
    PeerTransportIngressWirePayload forged_count_out;
    const SyncValidationResult forged_count_result =
        decode_peer_transport_ingress_wire_frame(
            forged_count_limits, forged_count, forged_count_out);
    require(!forged_count_result.ok &&
                forged_count_result.reason.find("impossible for remaining frame bytes") !=
                    std::string::npos,
            "peer ingress wire codec rejects impossible response counts before allocation");

    auto wrong_length_envelope = envelope;
    wrong_length_envelope.peer_batch_envelope.responses[0].length += 1;
    wrong_length_envelope.peer_batch_envelope.total_bytes += 1;
    std::string rejected_frame;
    std::string rejected_digest;
    require(!encode_peer_transport_ingress_wire_frame(
                limits, wrong_length_envelope, {chunk}, rejected_frame, rejected_digest).ok,
            "peer ingress wire codec refuses to encode declared and actual chunk-length disagreement");

    PeerTransportIngressWireLimits tiny_limits = limits;
    tiny_limits.max_frame_bytes = static_cast<std::uint64_t>(frame.size() - 1);
    std::string oversized_frame;
    std::string oversized_digest;
    require(!encode_peer_transport_ingress_wire_frame(
                tiny_limits, envelope, {chunk}, oversized_frame, oversized_digest).ok,
            "peer ingress wire codec applies the total frame bound after metadata overhead");

    PeerTransportIngressWireLimits impossible_limits = limits;
    impossible_limits.max_chunk_count =
        (impossible_limits.max_frame_bytes -
         static_cast<std::uint64_t>(kWireHeaderBytes)) /
            kMinimumEncodedResponseAndChunkBytes +
        1;
    require(!validate_peer_transport_ingress_wire_payload(
                 impossible_limits, envelope, {chunk}, "wire selftest limits").ok,
            "peer ingress wire codec rejects physically impossible limit profiles");

    auto malformed_key = envelope;
    malformed_key.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:not-a-digest";
    require(!encode_peer_transport_ingress_wire_frame(
                 limits, malformed_key, {chunk}, rejected_frame, rejected_digest).ok,
            "peer ingress wire codec rejects malformed transport envelope identities");

    auto malformed_remote_digest = envelope;
    malformed_remote_digest.peer_batch_envelope.remote_version_digest =
        "not-a-digest";
    malformed_remote_digest.peer_batch_envelope.responses[0].remote_version_digest =
        "not-a-digest";
    require(!encode_peer_transport_ingress_wire_frame(
                 limits, malformed_remote_digest, {chunk}, rejected_frame,
                 rejected_digest).ok,
            "peer ingress wire codec rejects malformed remote-version evidence");

    auto overflowing_range = envelope;
    overflowing_range.peer_batch_envelope.responses[0].offset =
        std::numeric_limits<std::uint64_t>::max();
    require(!encode_peer_transport_ingress_wire_frame(
                 limits, overflowing_range, {chunk}, rejected_frame,
                 rejected_digest).ok,
            "peer ingress wire codec rejects overflowing response byte ranges");

    auto unbounded_envelope = envelope;
    unbounded_envelope.max_chunk_bytes = 0;
    require(!encode_peer_transport_ingress_wire_frame(
                 limits, unbounded_envelope, {chunk}, rejected_frame,
                 rejected_digest).ok,
            "peer ingress wire codec rejects unbounded transport limits");
}

}  // namespace anonsync
