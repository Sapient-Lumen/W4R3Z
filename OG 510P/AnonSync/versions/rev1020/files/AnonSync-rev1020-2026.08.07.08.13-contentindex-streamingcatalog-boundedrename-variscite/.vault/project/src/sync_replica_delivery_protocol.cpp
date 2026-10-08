#include "sync_replica_delivery_protocol.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kRequestMagic =
    "ANONSYNC-REPLICA-DELIVERY-REQUEST";
constexpr std::string_view kReceiptMagic =
    "ANONSYNC-REPLICA-DELIVERY-RECEIPT";
constexpr std::string_view kRequestDigestDomain =
    "anonsync-sync-replica-delivery-request-v1";
constexpr std::string_view kReceiptDigestDomain =
    "anonsync-sync-replica-delivery-receipt-v1";
constexpr std::string_view kChannelBindingDigestDomain =
    "anonsync-sync-replica-delivery-channel-binding-v1";
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kFixedFrameTrailerBytes = kDigestTextBytes;

[[nodiscard]] std::string u32_be(std::uint32_t value) {
    std::string out(4U, '\0');
    for (std::size_t index = 0; index < 4U; ++index) {
        out[3U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::string u64_be(std::uint64_t value) {
    std::string out(8U, '\0');
    for (std::size_t index = 0; index < 8U; ++index) {
        out[7U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > static_cast<std::size_t>(
                        std::numeric_limits<std::uint64_t>::max())) {
            throw std::overflow_error(label + " exceeds uint64_t");
        }
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::size_t u64_to_size_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value > static_cast<std::uint64_t>(
                    std::numeric_limits<std::size_t>::max())) {
        throw std::overflow_error(label + " exceeds addressable size");
    }
    return static_cast<std::size_t>(value);
}

void append_u32(std::string& out, std::uint32_t value) {
    out.append(u32_be(value));
}

void append_u64(std::string& out, std::uint64_t value) {
    out.append(u64_be(value));
}

void append_framed(std::string& out, std::string_view bytes) {
    append_u64(
        out,
        size_to_u64_or_throw(
            bytes.size(), "sync replica delivery field length"));
    out.append(bytes);
}

void append_digest_framed(
    Sha256DigestBuilder& digest,
    std::string_view bytes) {
    digest.update(u64_be(size_to_u64_or_throw(
        bytes.size(), "sync replica delivery digest field length")));
    digest.update(bytes);
}

[[nodiscard]] std::uint64_t checked_add_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(label + " exceeds uint64_t");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t fixed_frame_bytes(
    std::string_view magic) {
    std::uint64_t bytes = size_to_u64_or_throw(
        magic.size(), "sync replica delivery magic length");
    bytes = checked_add_u64_or_throw(
        bytes, 4U + 8U + kFixedFrameTrailerBytes,
        "sync replica delivery fixed frame length");
    return bytes;
}

[[nodiscard]] std::uint64_t framed_capacity_or_throw(
    std::uint64_t maximum_payload_bytes,
    const std::string& label) {
    return checked_add_u64_or_throw(8U, maximum_payload_bytes, label);
}

[[nodiscard]] std::uint64_t maximum_request_frame_bytes_or_throw(
    const SyncReplicaModelLimits& model) {
    std::uint64_t bytes = fixed_frame_bytes(kRequestMagic);
    auto add = [&](std::uint64_t value, std::string_view field) {
        bytes = checked_add_u64_or_throw(
            bytes, value,
            "sync replica delivery maximum request " + std::string(field));
    };
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request folder frame"),
        "folder");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request sender frame"),
        "sender");
    add(8U, "sender epoch");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request receiver frame"),
        "receiver");
    add(8U, "receiver epoch");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes, "request claim frame"),
        "claim");
    add(8U, "dispatch attempts");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request binding type frame"),
        "binding type");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes, "request binding digest frame"),
        "binding digest");
    add(framed_capacity_or_throw(
            model.max_canonical_operation_bytes,
            "request canonical operation frame"),
        "canonical operation");
    return bytes;
}

[[nodiscard]] std::uint64_t maximum_receipt_frame_bytes_or_throw() {
    std::uint64_t bytes = fixed_frame_bytes(kReceiptMagic);
    auto add = [&](std::uint64_t value, std::string_view field) {
        bytes = checked_add_u64_or_throw(
            bytes, value,
            "sync replica delivery maximum receipt " + std::string(field));
    };
    for (std::string_view field :
         {"folder", "sender", "receiver", "binding type"}) {
        add(framed_capacity_or_throw(
                kSyncManifestIdMaxBytes,
                "receipt " + std::string(field) + " frame"),
            field);
    }
    add(8U, "sender epoch");
    add(8U, "receiver epoch");
    for (std::string_view field :
         {"operation", "claim", "request digest", "binding digest",
          "receiver cutpoint"}) {
        add(framed_capacity_or_throw(
                kSyncManifestSha256TextBytes,
                "receipt " + std::string(field) + " frame"),
            field);
    }
    add(8U, "dispatch attempts");
    add(4U, "disposition");
    add(4U, "evidence state");
    add(8U, "receiver generation");
    return bytes;
}

void validate_frame_limit_or_throw(
    std::uint64_t limit,
    std::string_view magic,
    const std::string& label) {
    if (limit < fixed_frame_bytes(magic)) {
        throw std::invalid_argument(
            label + " frame limit cannot hold the fixed protocol frame");
    }
    (void)u64_to_size_or_throw(limit, label + " frame limit");
}

void validate_protocol_limits_impl_or_throw(
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_sync_replica_model_limits_or_throw(limits.model);
    validate_frame_limit_or_throw(
        limits.max_request_frame_bytes, kRequestMagic,
        "sync replica delivery request");
    validate_frame_limit_or_throw(
        limits.max_receipt_frame_bytes, kReceiptMagic,
        "sync replica delivery receipt");

    const std::uint64_t required_request =
        maximum_request_frame_bytes_or_throw(limits.model);
    if (limits.max_request_frame_bytes < required_request) {
        throw std::invalid_argument(
            "sync replica delivery request frame limit cannot hold every "
            "operation permitted by the wire model");
    }
    const std::uint64_t required_receipt =
        maximum_receipt_frame_bytes_or_throw();
    if (limits.max_receipt_frame_bytes < required_receipt) {
        throw std::invalid_argument(
            "sync replica delivery receipt frame limit cannot hold every "
            "canonical receipt");
    }
}

void validate_actor_or_throw(
    const SyncReplicaActor& actor,
    const std::string& label) {
    if (!sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(label + " actor identity is invalid");
    }
}

[[nodiscard]] bool disposition_is_known(
    SyncReplicaDeliveryReceiptDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaDeliveryReceiptDisposition::InsertedActive:
        case SyncReplicaDeliveryReceiptDisposition::InsertedPending:
        case SyncReplicaDeliveryReceiptDisposition::InsertedQuarantined:
        case SyncReplicaDeliveryReceiptDisposition::Duplicate:
        case SyncReplicaDeliveryReceiptDisposition::CapacityBlocked:
            return true;
    }
    return false;
}

[[nodiscard]] std::uint32_t evidence_state_code(
    const std::optional<SyncReplicaEvidenceState>& state) {
    if (!state.has_value()) return 0U;
    switch (*state) {
        case SyncReplicaEvidenceState::Active:
            return 1U;
        case SyncReplicaEvidenceState::PendingMissingDependency:
            return 2U;
        case SyncReplicaEvidenceState::QuarantinedDotFork:
            return 3U;
        case SyncReplicaEvidenceState::QuarantinedDependency:
            return 4U;
        case SyncReplicaEvidenceState::QuarantinedCausalEnvelope:
            return 5U;
        case SyncReplicaEvidenceState::QuarantinedDependencyCycle:
            return 6U;
    }
    throw std::logic_error(
        "sync replica delivery receipt has unsupported evidence state");
}

[[nodiscard]] std::optional<SyncReplicaEvidenceState>
parse_evidence_state_or_throw(std::uint32_t code) {
    switch (code) {
        case 0U:
            return std::nullopt;
        case 1U:
            return SyncReplicaEvidenceState::Active;
        case 2U:
            return SyncReplicaEvidenceState::PendingMissingDependency;
        case 3U:
            return SyncReplicaEvidenceState::QuarantinedDotFork;
        case 4U:
            return SyncReplicaEvidenceState::QuarantinedDependency;
        case 5U:
            return SyncReplicaEvidenceState::QuarantinedCausalEnvelope;
        case 6U:
            return SyncReplicaEvidenceState::QuarantinedDependencyCycle;
        default:
            throw std::runtime_error(
                "sync replica delivery receipt evidence-state code is unsupported");
    }
}

[[nodiscard]] SyncReplicaDeliveryReceiptDisposition
parse_disposition_or_throw(std::uint32_t code) {
    switch (code) {
        case 1U:
            return SyncReplicaDeliveryReceiptDisposition::InsertedActive;
        case 2U:
            return SyncReplicaDeliveryReceiptDisposition::InsertedPending;
        case 3U:
            return SyncReplicaDeliveryReceiptDisposition::InsertedQuarantined;
        case 4U:
            return SyncReplicaDeliveryReceiptDisposition::Duplicate;
        case 5U:
            return SyncReplicaDeliveryReceiptDisposition::CapacityBlocked;
        default:
            throw std::runtime_error(
                "sync replica delivery receipt disposition code is unsupported");
    }
}

class FrameReader final {
public:
    FrameReader(std::string_view bytes, std::string label)
        : bytes_(bytes), label_(std::move(label)) {}

    [[nodiscard]] std::uint32_t read_u32() {
        require_remaining(4U, "uint32");
        std::uint32_t value = 0U;
        for (std::size_t index = 0; index < 4U; ++index) {
            value = (value << 8U) |
                    static_cast<unsigned char>(bytes_[position_ + index]);
        }
        position_ += 4U;
        return value;
    }

    [[nodiscard]] std::uint64_t read_u64() {
        require_remaining(8U, "uint64");
        std::uint64_t value = 0U;
        for (std::size_t index = 0; index < 8U; ++index) {
            value = (value << 8U) |
                    static_cast<unsigned char>(bytes_[position_ + index]);
        }
        position_ += 8U;
        return value;
    }

    [[nodiscard]] std::string read_string(
        std::uint64_t max_bytes,
        const std::string& field) {
        const std::uint64_t length = read_u64();
        if (length > max_bytes) {
            throw std::runtime_error(
                label_ + " " + field + " exceeds its byte limit");
        }
        const std::size_t size = u64_to_size_or_throw(
            length, label_ + " " + field + " length");
        require_remaining(size, field);
        std::string value(bytes_.substr(position_, size));
        position_ += size;
        return value;
    }

    void require_consumed() const {
        if (position_ != bytes_.size()) {
            throw std::runtime_error(label_ + " has trailing body bytes");
        }
    }

private:
    void require_remaining(
        std::size_t required,
        const std::string& field) const {
        if (required > bytes_.size() - position_) {
            throw std::runtime_error(
                label_ + " is truncated while reading " + field);
        }
    }

    std::string_view bytes_;
    std::string label_;
    std::size_t position_ = 0U;
};

[[nodiscard]] std::string request_body_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_sync_replica_delivery_request_or_throw(request, limits);
    std::string body;
    append_framed(body, request.folder_id);
    append_framed(body, request.sender_actor.device_id);
    append_u64(body, request.sender_actor.epoch);
    append_framed(body, request.receiver_actor.device_id);
    append_u64(body, request.receiver_actor.epoch);
    append_framed(body, request.claim_id);
    append_u64(body, request.dispatch_attempts);
    append_framed(body, request.channel_binding.type);
    append_framed(body, request.channel_binding.digest);
    append_framed(
        body,
        encode_sync_replica_operation_canonical_or_throw(
            request.operation, limits.model));
    return body;
}

[[nodiscard]] std::string receipt_body_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_sync_replica_delivery_receipt_or_throw(receipt, limits);
    std::string body;
    append_framed(body, receipt.folder_id);
    append_framed(body, receipt.sender_actor.device_id);
    append_u64(body, receipt.sender_actor.epoch);
    append_framed(body, receipt.receiver_actor.device_id);
    append_u64(body, receipt.receiver_actor.epoch);
    append_framed(body, receipt.operation_id);
    append_framed(body, receipt.claim_id);
    append_u64(body, receipt.dispatch_attempts);
    append_framed(body, receipt.request_digest);
    append_framed(body, receipt.channel_binding.type);
    append_framed(body, receipt.channel_binding.digest);
    append_u32(body, static_cast<std::uint32_t>(receipt.disposition));
    append_u32(body, evidence_state_code(receipt.evidence_state));
    append_u64(body, receipt.receiver_state_generation);
    append_framed(body, receipt.receiver_cutpoint_digest);
    return body;
}

[[nodiscard]] std::string body_digest_or_throw(
    std::string_view domain,
    std::string_view body) {
    Sha256DigestBuilder digest;
    digest.update(domain);
    digest.update(u32_be(kSyncReplicaDeliveryProtocolVersion));
    append_digest_framed(digest, body);
    return digest.finish_hex();
}

[[nodiscard]] std::string encode_frame_or_throw(
    std::string_view magic,
    std::string_view domain,
    std::string body,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    const std::uint64_t body_size = size_to_u64_or_throw(
        body.size(), label + " body length");
    const std::uint64_t fixed = fixed_frame_bytes(magic);
    if (body_size > max_frame_bytes - fixed) {
        throw std::length_error(label + " exceeds its frame byte limit");
    }

    std::string frame;
    frame.reserve(u64_to_size_or_throw(
        fixed + body_size, label + " frame length"));
    frame.append(magic);
    append_u32(frame, kSyncReplicaDeliveryProtocolVersion);
    append_u64(frame, body_size);
    frame.append(body);
    frame.append(body_digest_or_throw(domain, body));
    return frame;
}

[[nodiscard]] std::string_view decode_frame_or_throw(
    std::string_view frame,
    std::string_view magic,
    std::string_view domain,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    if (frame.size() > u64_to_size_or_throw(
                           max_frame_bytes, label + " frame limit")) {
        throw std::length_error(label + " exceeds its frame byte limit");
    }
    const std::size_t fixed = u64_to_size_or_throw(
        fixed_frame_bytes(magic), label + " fixed frame length");
    if (frame.size() < fixed) {
        throw std::runtime_error(label + " is shorter than its fixed frame");
    }
    if (!frame.starts_with(magic)) {
        throw std::runtime_error(label + " magic is invalid");
    }

    FrameReader header(
        frame.substr(magic.size(), 12U), label + " header");
    const std::uint32_t version = header.read_u32();
    if (version != kSyncReplicaDeliveryProtocolVersion) {
        throw std::runtime_error(label + " protocol version is unsupported");
    }
    const std::uint64_t body_length = header.read_u64();
    header.require_consumed();
    const std::size_t body_size = u64_to_size_or_throw(
        body_length, label + " body length");
    if (body_size != frame.size() - fixed) {
        throw std::runtime_error(label + " body length is not exact");
    }

    const std::size_t body_begin = magic.size() + 12U;
    const std::string_view body = frame.substr(body_begin, body_size);
    const std::string_view observed_digest =
        frame.substr(body_begin + body_size, kDigestTextBytes);
    if (!is_lowercase_sha256_hex(observed_digest)) {
        throw std::runtime_error(label + " structural digest is invalid");
    }
    const std::string expected_digest = body_digest_or_throw(domain, body);
    if (observed_digest != expected_digest) {
        throw std::runtime_error(label + " structural digest mismatch");
    }
    return body;
}

[[nodiscard]] SyncReplicaDeliveryRequest parse_request_body_or_throw(
    std::string_view body,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    FrameReader reader(body, "sync replica delivery request body");
    SyncReplicaDeliveryRequest request;
    request.folder_id = reader.read_string(
        kSyncManifestIdMaxBytes, "folder_id");
    request.sender_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "sender_device_id");
    request.sender_actor.epoch = reader.read_u64();
    request.receiver_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "receiver_device_id");
    request.receiver_actor.epoch = reader.read_u64();
    request.claim_id = reader.read_string(
        kSyncManifestSha256TextBytes, "claim_id");
    request.dispatch_attempts = reader.read_u64();
    request.channel_binding.type = reader.read_string(
        kSyncManifestIdMaxBytes, "channel_binding_type");
    request.channel_binding.digest = reader.read_string(
        kSyncManifestSha256TextBytes, "channel_binding_digest");
    const std::string operation_bytes = reader.read_string(
        limits.model.max_canonical_operation_bytes,
        "canonical_operation_bytes");
    reader.require_consumed();
    request.operation = decode_sync_replica_operation_canonical_or_throw(
        operation_bytes, limits.model);
    validate_sync_replica_delivery_request_or_throw(request, limits);
    return request;
}

[[nodiscard]] SyncReplicaDeliveryReceipt parse_receipt_body_or_throw(
    std::string_view body,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    FrameReader reader(body, "sync replica delivery receipt body");
    SyncReplicaDeliveryReceipt receipt;
    receipt.folder_id = reader.read_string(
        kSyncManifestIdMaxBytes, "folder_id");
    receipt.sender_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "sender_device_id");
    receipt.sender_actor.epoch = reader.read_u64();
    receipt.receiver_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "receiver_device_id");
    receipt.receiver_actor.epoch = reader.read_u64();
    receipt.operation_id = reader.read_string(
        kSyncManifestSha256TextBytes, "operation_id");
    receipt.claim_id = reader.read_string(
        kSyncManifestSha256TextBytes, "claim_id");
    receipt.dispatch_attempts = reader.read_u64();
    receipt.request_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "request_digest");
    receipt.channel_binding.type = reader.read_string(
        kSyncManifestIdMaxBytes, "channel_binding_type");
    receipt.channel_binding.digest = reader.read_string(
        kSyncManifestSha256TextBytes, "channel_binding_digest");
    receipt.disposition = parse_disposition_or_throw(reader.read_u32());
    receipt.evidence_state = parse_evidence_state_or_throw(reader.read_u32());
    receipt.receiver_state_generation = reader.read_u64();
    receipt.receiver_cutpoint_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "receiver_cutpoint_digest");
    reader.require_consumed();
    validate_sync_replica_delivery_receipt_or_throw(receipt, limits);
    return receipt;
}

}  // namespace

void validate_sync_replica_delivery_protocol_limits_or_throw(
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
}

SyncReplicaDeliveryChannelBinding
make_sync_replica_delivery_channel_binding_or_throw(
    std::string type,
    std::string_view raw_binding_bytes) {
    if (!sync_id_is_valid(type)) {
        throw std::invalid_argument(
            "sync replica delivery channel binding type is invalid");
    }
    if (raw_binding_bytes.empty() ||
        raw_binding_bytes.size() > kSyncReplicaDeliveryMaxChannelBindingBytes) {
        throw std::invalid_argument(
            "sync replica delivery raw channel binding must contain 1..4096 bytes");
    }
    Sha256DigestBuilder digest;
    digest.update(kChannelBindingDigestDomain);
    append_digest_framed(digest, type);
    append_digest_framed(digest, raw_binding_bytes);
    return {std::move(type), digest.finish_hex()};
}

void validate_sync_replica_delivery_channel_binding_or_throw(
    const SyncReplicaDeliveryChannelBinding& binding,
    const std::string& label) {
    if (!sync_id_is_valid(binding.type) ||
        !is_lowercase_sha256_hex(binding.digest)) {
        throw std::invalid_argument(label + " channel binding is invalid");
    }
}

bool sync_replica_delivery_receipt_is_evidence_terminal(
    SyncReplicaDeliveryReceiptDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaDeliveryReceiptDisposition::InsertedActive:
        case SyncReplicaDeliveryReceiptDisposition::InsertedPending:
        case SyncReplicaDeliveryReceiptDisposition::InsertedQuarantined:
        case SyncReplicaDeliveryReceiptDisposition::Duplicate:
            return true;
        case SyncReplicaDeliveryReceiptDisposition::CapacityBlocked:
            return false;
    }
    // Unknown wire values must never acquire terminal authority merely because
    // an enum was cast before validation.
    return false;
}

void validate_sync_replica_delivery_request_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(request.folder_id)) {
        throw std::invalid_argument(
            "sync replica delivery request folder identity is invalid");
    }
    validate_actor_or_throw(
        request.sender_actor, "sync replica delivery request sender");
    validate_actor_or_throw(
        request.receiver_actor, "sync replica delivery request receiver");
    if (request.sender_actor.device_id == request.receiver_actor.device_id) {
        throw std::invalid_argument(
            "sync replica delivery request is self-directed");
    }
    if (!is_lowercase_sha256_hex(request.claim_id) ||
        request.dispatch_attempts == 0U) {
        throw std::invalid_argument(
            "sync replica delivery request attempt identity is invalid");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        request.channel_binding, "sync replica delivery request");
    validate_sync_replica_operation_or_throw(request.operation, limits.model);
    if (request.operation.folder_id != request.folder_id ||
        request.operation.dot.actor != request.sender_actor) {
        throw std::invalid_argument(
            "sync replica delivery request operation authority does not match its envelope");
    }
}

void validate_sync_replica_delivery_receipt_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(receipt.folder_id)) {
        throw std::invalid_argument(
            "sync replica delivery receipt folder identity is invalid");
    }
    validate_actor_or_throw(
        receipt.sender_actor, "sync replica delivery receipt sender");
    validate_actor_or_throw(
        receipt.receiver_actor, "sync replica delivery receipt receiver");
    if (receipt.sender_actor.device_id == receipt.receiver_actor.device_id) {
        throw std::invalid_argument(
            "sync replica delivery receipt is self-directed");
    }
    if (!is_lowercase_sha256_hex(receipt.operation_id) ||
        !is_lowercase_sha256_hex(receipt.claim_id) ||
        receipt.dispatch_attempts == 0U ||
        !is_lowercase_sha256_hex(receipt.request_digest) ||
        !is_lowercase_sha256_hex(receipt.receiver_cutpoint_digest)) {
        throw std::invalid_argument(
            "sync replica delivery receipt identity or cutpoint digest is invalid");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        receipt.channel_binding, "sync replica delivery receipt");
    if (!disposition_is_known(receipt.disposition)) {
        throw std::invalid_argument(
            "sync replica delivery receipt disposition is invalid");
    }

    switch (receipt.disposition) {
        case SyncReplicaDeliveryReceiptDisposition::InsertedActive:
            if (receipt.evidence_state != SyncReplicaEvidenceState::Active) {
                throw std::invalid_argument(
                    "sync replica delivery active receipt has inconsistent evidence state");
            }
            break;
        case SyncReplicaDeliveryReceiptDisposition::InsertedPending:
            if (receipt.evidence_state !=
                SyncReplicaEvidenceState::PendingMissingDependency) {
                throw std::invalid_argument(
                    "sync replica delivery pending receipt has inconsistent evidence state");
            }
            break;
        case SyncReplicaDeliveryReceiptDisposition::InsertedQuarantined:
            if (!receipt.evidence_state.has_value() ||
                !sync_replica_evidence_state_is_quarantined(
                    *receipt.evidence_state)) {
                throw std::invalid_argument(
                    "sync replica delivery quarantine receipt has inconsistent evidence state");
            }
            break;
        case SyncReplicaDeliveryReceiptDisposition::Duplicate:
            if (!receipt.evidence_state.has_value()) {
                throw std::invalid_argument(
                    "sync replica delivery duplicate receipt lacks retained evidence state");
            }
            break;
        case SyncReplicaDeliveryReceiptDisposition::CapacityBlocked:
            if (receipt.evidence_state.has_value()) {
                throw std::invalid_argument(
                    "sync replica delivery capacity receipt fabricates retained evidence state");
            }
            break;
    }
    if (receipt.receiver_state_generation == 0U) {
        throw std::invalid_argument(
            "sync replica delivery receipt has zero receiver generation");
    }
}

std::string encode_sync_replica_delivery_request_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    return encode_frame_or_throw(
        kRequestMagic, kRequestDigestDomain,
        request_body_or_throw(request, limits),
        limits.max_request_frame_bytes,
        "sync replica delivery request");
}

SyncReplicaDeliveryRequest decode_sync_replica_delivery_request_or_throw(
    std::string_view frame,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    const std::string_view body = decode_frame_or_throw(
        frame, kRequestMagic, kRequestDigestDomain,
        limits.max_request_frame_bytes,
        "sync replica delivery request");
    SyncReplicaDeliveryRequest request =
        parse_request_body_or_throw(body, limits);
    const std::string canonical =
        encode_sync_replica_delivery_request_or_throw(request, limits);
    if (canonical != frame) {
        throw std::runtime_error(
            "sync replica delivery request is not canonically encoded");
    }
    return request;
}

std::string sync_replica_delivery_request_digest_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    return body_digest_or_throw(
        kRequestDigestDomain, request_body_or_throw(request, limits));
}

std::string encode_sync_replica_delivery_receipt_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    return encode_frame_or_throw(
        kReceiptMagic, kReceiptDigestDomain,
        receipt_body_or_throw(receipt, limits),
        limits.max_receipt_frame_bytes,
        "sync replica delivery receipt");
}

SyncReplicaDeliveryReceipt decode_sync_replica_delivery_receipt_or_throw(
    std::string_view frame,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    const std::string_view body = decode_frame_or_throw(
        frame, kReceiptMagic, kReceiptDigestDomain,
        limits.max_receipt_frame_bytes,
        "sync replica delivery receipt");
    SyncReplicaDeliveryReceipt receipt =
        parse_receipt_body_or_throw(body, limits);
    const std::string canonical =
        encode_sync_replica_delivery_receipt_or_throw(receipt, limits);
    if (canonical != frame) {
        throw std::runtime_error(
            "sync replica delivery receipt is not canonically encoded");
    }
    return receipt;
}

std::string sync_replica_delivery_receipt_digest_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    return body_digest_or_throw(
        kReceiptDigestDomain, receipt_body_or_throw(receipt, limits));
}

void validate_sync_replica_delivery_receipt_for_request_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits) {
    validate_sync_replica_delivery_request_or_throw(request, limits);
    validate_sync_replica_delivery_receipt_or_throw(receipt, limits);
    if (receipt.folder_id != request.folder_id ||
        receipt.sender_actor != request.sender_actor ||
        receipt.receiver_actor != request.receiver_actor ||
        receipt.operation_id != request.operation.operation_id ||
        receipt.claim_id != request.claim_id ||
        receipt.dispatch_attempts != request.dispatch_attempts ||
        receipt.channel_binding != request.channel_binding ||
        receipt.request_digest !=
            sync_replica_delivery_request_digest_or_throw(request, limits)) {
        throw std::runtime_error(
            "sync replica delivery receipt does not bind the exact request");
    }
}

}  // namespace anonsync
