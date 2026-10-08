#include "sync_replica_file_delivery_protocol.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_effect_identity.hpp"

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
    "ANONSYNC-REPLICA-FILE-DELIVERY-REQUEST";
constexpr std::string_view kReceiptMagic =
    "ANONSYNC-REPLICA-FILE-DELIVERY-RECEIPT";
constexpr std::string_view kRequestDigestDomain =
    "anonsync-sync-replica-file-delivery-request-v2";
constexpr std::string_view kReceiptDigestDomain =
    "anonsync-sync-replica-file-delivery-receipt-v2";
constexpr std::uint64_t kDigestTextBytes = 64U;

[[nodiscard]] std::string u32_be(std::uint32_t value) {
    std::string out(4U, '\0');
    for (std::size_t index = 0U; index < 4U; ++index) {
        out[3U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::string u64_be(std::uint64_t value) {
    std::string out(8U, '\0');
    for (std::size_t index = 0U; index < 8U; ++index) {
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

[[nodiscard]] std::uint64_t checked_add_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(label + " exceeds uint64_t");
    }
    return left + right;
}

void append_u32(std::string& out, std::uint32_t value) {
    out.append(u32_be(value));
}

void append_u64(std::string& out, std::uint64_t value) {
    out.append(u64_be(value));
}

void append_framed(std::string& out, std::string_view bytes) {
    append_u64(out, size_to_u64_or_throw(
                        bytes.size(), "file delivery field length"));
    out.append(bytes);
}

void append_digest_framed(Sha256DigestBuilder& digest,
                          std::string_view bytes) {
    digest.update(u64_be(size_to_u64_or_throw(
        bytes.size(), "file delivery digest field length")));
    digest.update(bytes);
}

[[nodiscard]] std::uint64_t fixed_frame_bytes(std::string_view magic) {
    return checked_add_or_throw(
        size_to_u64_or_throw(magic.size(), "file delivery magic length"),
        4U + 8U + kDigestTextBytes,
        "file delivery fixed frame length");
}

[[nodiscard]] std::uint64_t framed_capacity_or_throw(
    std::uint64_t payload,
    const std::string& label) {
    return checked_add_or_throw(8U, payload, label);
}

void validate_frame_limit_or_throw(std::uint64_t limit,
                                   std::string_view magic,
                                   const std::string& label) {
    if (limit < fixed_frame_bytes(magic)) {
        throw std::invalid_argument(
            label + " frame limit cannot hold its fixed frame");
    }
    (void)u64_to_size_or_throw(limit, label + " frame limit");
}

void validate_actor_or_throw(const SyncReplicaActor& actor,
                             const std::string& label) {
    if (!sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(label + " actor identity is invalid");
    }
}

[[nodiscard]] bool disposition_known(
    SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFileDeliveryReceiptDisposition::Published:
        case SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished:
        case SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked:
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceCapacityBlocked:
        case SyncReplicaFileDeliveryReceiptDisposition::EvidencePending:
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceQuarantined:
        case SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked:
        case SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict:
        case SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked:
            return true;
    }
    return false;
}

[[nodiscard]] SyncReplicaFileDeliveryReceiptDisposition
parse_disposition_or_throw(std::uint32_t value) {
    switch (value) {
        case 1U:
            return SyncReplicaFileDeliveryReceiptDisposition::Published;
        case 2U:
            return SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished;
        case 3U:
            return SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked;
        case 4U:
            return SyncReplicaFileDeliveryReceiptDisposition::EvidenceCapacityBlocked;
        case 5U:
            return SyncReplicaFileDeliveryReceiptDisposition::EvidencePending;
        case 6U:
            return SyncReplicaFileDeliveryReceiptDisposition::EvidenceQuarantined;
        case 7U:
            return SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked;
        case 8U:
            return SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict;
        case 9U:
            return SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked;
        default:
            throw std::runtime_error(
                "sync replica file-delivery receipt disposition is unsupported");
    }
}

class FrameReader final {
public:
    FrameReader(std::string_view bytes, std::string label)
        : bytes_(bytes), label_(std::move(label)) {}

    [[nodiscard]] std::uint32_t read_u32() {
        require_remaining(4U, "uint32");
        std::uint32_t value = 0U;
        for (std::size_t index = 0U; index < 4U; ++index) {
            value = (value << 8U) |
                    static_cast<unsigned char>(bytes_[position_ + index]);
        }
        position_ += 4U;
        return value;
    }

    [[nodiscard]] std::uint64_t read_u64() {
        require_remaining(8U, "uint64");
        std::uint64_t value = 0U;
        for (std::size_t index = 0U; index < 8U; ++index) {
            value = (value << 8U) |
                    static_cast<unsigned char>(bytes_[position_ + index]);
        }
        position_ += 8U;
        return value;
    }

    [[nodiscard]] std::string read_string(
        std::uint64_t maximum,
        const std::string& field) {
        const std::uint64_t length = read_u64();
        if (length > maximum) {
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
    void require_remaining(std::size_t required,
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

[[nodiscard]] std::string body_digest_or_throw(
    std::string_view domain,
    std::string_view body) {
    Sha256DigestBuilder digest;
    digest.update(domain);
    digest.update(u32_be(kSyncReplicaFileDeliveryProtocolVersion));
    append_digest_framed(digest, body);
    return digest.finish_hex();
}

[[nodiscard]] std::string encode_frame_or_throw(
    std::string_view magic,
    std::string_view domain,
    std::string body,
    std::uint64_t maximum,
    const std::string& label) {
    const std::uint64_t body_size = size_to_u64_or_throw(
        body.size(), label + " body length");
    const std::uint64_t fixed = fixed_frame_bytes(magic);
    if (body_size > maximum - fixed) {
        throw std::length_error(label + " exceeds its frame byte limit");
    }
    std::string frame;
    frame.reserve(u64_to_size_or_throw(
        fixed + body_size, label + " frame length"));
    frame.append(magic);
    append_u32(frame, kSyncReplicaFileDeliveryProtocolVersion);
    append_u64(frame, body_size);
    frame.append(body);
    frame.append(body_digest_or_throw(domain, body));
    return frame;
}

[[nodiscard]] std::string_view decode_frame_or_throw(
    std::string_view frame,
    std::string_view magic,
    std::string_view domain,
    std::uint64_t maximum,
    const std::string& label) {
    if (frame.size() > u64_to_size_or_throw(maximum, label + " limit")) {
        throw std::length_error(label + " exceeds its frame byte limit");
    }
    const std::size_t fixed = u64_to_size_or_throw(
        fixed_frame_bytes(magic), label + " fixed length");
    if (frame.size() < fixed) {
        throw std::runtime_error(label + " is shorter than its fixed frame");
    }
    if (!frame.starts_with(magic)) {
        throw std::runtime_error(label + " magic is invalid");
    }
    FrameReader header(frame.substr(magic.size(), 12U), label + " header");
    if (header.read_u32() != kSyncReplicaFileDeliveryProtocolVersion) {
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
    const std::string_view observed =
        frame.substr(body_begin + body_size, kDigestTextBytes);
    if (!is_lowercase_sha256_hex(observed)) {
        throw std::runtime_error(label + " structural digest is invalid");
    }
    if (observed != body_digest_or_throw(domain, body)) {
        throw std::runtime_error(label + " structural digest mismatch");
    }
    return body;
}

[[nodiscard]] std::uint64_t maximum_receipt_body_bytes_or_throw(
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    std::uint64_t bytes = 0U;
    auto add = [&](std::uint64_t value, std::string_view field) {
        bytes = checked_add_or_throw(
            bytes, value,
            "sync replica file delivery receipt " + std::string(field));
    };
    for (std::string_view field :
         {"folder", "sender", "receiver", "binding type"}) {
        add(framed_capacity_or_throw(kSyncManifestIdMaxBytes,
                                    "receipt identity frame"),
            field);
    }
    add(8U, "sender epoch");
    add(8U, "receiver epoch");
    for (std::string_view field :
         {"operation", "claim", "request digest", "binding digest",
          "effect id", "effect cutpoint"}) {
        add(framed_capacity_or_throw(kSyncManifestSha256TextBytes,
                                    "receipt digest frame"),
            field);
    }
    add(8U, "dispatch attempts");
    add(4U, "disposition");
    add(4U, "evidence presence");
    add(framed_capacity_or_throw(
            limits.evidence.max_receipt_frame_bytes,
            "embedded evidence receipt frame"),
        "evidence receipt");
    add(8U, "effect generation");
    return bytes;
}

[[nodiscard]] std::string request_body_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_request_or_throw(request, limits);
    std::string body;
    append_framed(
        body, encode_sync_replica_delivery_request_or_throw(
                  request.evidence_request, limits.evidence));
    append_framed(body, request.payload);
    return body;
}

[[nodiscard]] std::string receipt_body_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_receipt_or_throw(receipt, limits);
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
    append_u32(body, receipt.evidence_receipt.has_value() ? 1U : 0U);
    append_framed(
        body,
        receipt.evidence_receipt.has_value()
            ? encode_sync_replica_delivery_receipt_or_throw(
                  *receipt.evidence_receipt, limits.evidence)
            : std::string{});
    append_framed(body, receipt.effect_id);
    append_u64(body, receipt.receiver_effect_generation);
    append_framed(body, receipt.receiver_effect_cutpoint_digest);
    return body;
}

[[nodiscard]] SyncReplicaFileDeliveryRequest parse_request_body_or_throw(
    std::string_view body,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    FrameReader reader(body, "sync replica file-delivery request body");
    const std::string evidence_frame = reader.read_string(
        limits.evidence.max_request_frame_bytes, "evidence request frame");
    SyncReplicaFileDeliveryRequest request;
    request.evidence_request =
        decode_sync_replica_delivery_request_or_throw(
            evidence_frame, limits.evidence);
    request.payload = reader.read_string(
        limits.max_payload_bytes, "payload");
    reader.require_consumed();
    validate_sync_replica_file_delivery_request_or_throw(request, limits);
    return request;
}

[[nodiscard]] SyncReplicaFileDeliveryReceipt parse_receipt_body_or_throw(
    std::string_view body,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    FrameReader reader(body, "sync replica file-delivery receipt body");
    SyncReplicaFileDeliveryReceipt receipt;
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
    const std::uint32_t has_evidence = reader.read_u32();
    if (has_evidence > 1U) {
        throw std::runtime_error(
            "sync replica file-delivery receipt evidence presence is invalid");
    }
    const std::string evidence_frame = reader.read_string(
        limits.evidence.max_receipt_frame_bytes,
        "evidence receipt frame");
    if (has_evidence == 1U) {
        if (evidence_frame.empty()) {
            throw std::runtime_error(
                "sync replica file-delivery receipt omits present evidence bytes");
        }
        receipt.evidence_receipt =
            decode_sync_replica_delivery_receipt_or_throw(
                evidence_frame, limits.evidence);
    } else if (!evidence_frame.empty()) {
        throw std::runtime_error(
            "sync replica file-delivery receipt has unowned evidence bytes");
    }
    receipt.effect_id = reader.read_string(
        kSyncManifestSha256TextBytes, "effect_id");
    receipt.receiver_effect_generation = reader.read_u64();
    receipt.receiver_effect_cutpoint_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "effect_cutpoint_digest");
    reader.require_consumed();
    validate_sync_replica_file_delivery_receipt_or_throw(receipt, limits);
    return receipt;
}

[[nodiscard]] bool evidence_state_active(
    const SyncReplicaDeliveryReceipt& receipt) noexcept {
    return receipt.evidence_state == SyncReplicaEvidenceState::Active;
}

[[nodiscard]] bool evidence_state_pending(
    const SyncReplicaDeliveryReceipt& receipt) noexcept {
    return receipt.evidence_state ==
           SyncReplicaEvidenceState::PendingMissingDependency;
}

[[nodiscard]] bool evidence_state_quarantined(
    const SyncReplicaDeliveryReceipt& receipt) noexcept {
    return receipt.evidence_state.has_value() &&
           sync_replica_evidence_state_is_quarantined(
               *receipt.evidence_state);
}

}  // namespace

bool sync_replica_file_delivery_receipt_is_effect_terminal(
    SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept {
    return disposition == SyncReplicaFileDeliveryReceiptDisposition::Published ||
           disposition ==
               SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished;
}

bool sync_replica_file_delivery_receipt_precedes_effect_authority(
    SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept {
    return disposition ==
               SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked ||
           disposition ==
               SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked;
}

void validate_sync_replica_file_delivery_protocol_limits_or_throw(
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_delivery_protocol_limits_or_throw(limits.evidence);
    if (limits.max_payload_bytes == 0U) {
        throw std::invalid_argument(
            "sync replica file delivery max payload bytes must be positive");
    }
    (void)u64_to_size_or_throw(
        limits.max_payload_bytes,
        "sync replica file delivery payload limit");
    validate_frame_limit_or_throw(
        limits.max_request_frame_bytes, kRequestMagic,
        "sync replica file delivery request");
    validate_frame_limit_or_throw(
        limits.max_receipt_frame_bytes, kReceiptMagic,
        "sync replica file delivery receipt");

    std::uint64_t request_required = fixed_frame_bytes(kRequestMagic);
    request_required = checked_add_or_throw(
        request_required,
        framed_capacity_or_throw(limits.evidence.max_request_frame_bytes,
                                 "embedded request capacity"),
        "sync replica file delivery maximum request");
    request_required = checked_add_or_throw(
        request_required,
        framed_capacity_or_throw(limits.max_payload_bytes,
                                 "payload capacity"),
        "sync replica file delivery maximum request");
    if (limits.max_request_frame_bytes < request_required) {
        throw std::invalid_argument(
            "sync replica file delivery request frame limit cannot hold every permitted payload and evidence request");
    }
    const std::uint64_t receipt_required = checked_add_or_throw(
        fixed_frame_bytes(kReceiptMagic),
        maximum_receipt_body_bytes_or_throw(limits),
        "sync replica file delivery maximum receipt");
    if (limits.max_receipt_frame_bytes < receipt_required) {
        throw std::invalid_argument(
            "sync replica file delivery receipt frame limit cannot hold every canonical receipt");
    }
}

void validate_sync_replica_file_delivery_request_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_protocol_limits_or_throw(limits);
    validate_sync_replica_delivery_request_or_throw(
        request.evidence_request, limits.evidence);
    const SyncReplicaOperation& operation = request.evidence_request.operation;
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            "sync replica file delivery request requires a file operation");
    }
    if (request.payload.size() > limits.max_payload_bytes ||
        operation.size_bytes != request.payload.size()) {
        throw std::invalid_argument(
            "sync replica file delivery payload size does not match operation");
    }
    if (sha256_hex(request.payload) != operation.content_sha256) {
        throw std::invalid_argument(
            "sync replica file delivery payload digest does not match operation");
    }
}

void validate_sync_replica_file_delivery_receipt_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_protocol_limits_or_throw(limits);
    if (!sync_id_is_valid(receipt.folder_id)) {
        throw std::invalid_argument(
            "sync replica file delivery receipt folder id is invalid");
    }
    validate_actor_or_throw(receipt.sender_actor,
                            "sync replica file delivery receipt sender");
    validate_actor_or_throw(receipt.receiver_actor,
                            "sync replica file delivery receipt receiver");
    if (receipt.sender_actor.device_id ==
        receipt.receiver_actor.device_id) {
        throw std::invalid_argument(
            "sync replica file delivery receipt actors must differ");
    }
    if (!is_lowercase_sha256_hex(receipt.operation_id) ||
        !is_lowercase_sha256_hex(receipt.claim_id) ||
        !is_lowercase_sha256_hex(receipt.request_digest) ||
        receipt.dispatch_attempts == 0U) {
        throw std::invalid_argument(
            "sync replica file delivery receipt attempt identity is invalid");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        receipt.channel_binding,
        "sync replica file delivery receipt channel binding");
    if (!disposition_known(receipt.disposition)) {
        throw std::invalid_argument(
            "sync replica file delivery receipt disposition is unknown");
    }
    if (!is_lowercase_sha256_hex(
            receipt.receiver_effect_cutpoint_digest)) {
        throw std::invalid_argument(
            "sync replica file delivery receipt effect cutpoint is invalid");
    }

    if (sync_replica_file_delivery_receipt_precedes_effect_authority(
            receipt.disposition)) {
        if (receipt.evidence_receipt.has_value() ||
            !receipt.effect_id.empty()) {
            throw std::invalid_argument(
                "pre-effect receipt must not claim staged evidence or effect identity");
        }
        return;
    }

    if (!receipt.evidence_receipt.has_value() ||
        !is_lowercase_sha256_hex(receipt.effect_id) ||
        receipt.receiver_effect_generation == 0U) {
        throw std::invalid_argument(
            "sync replica file delivery receipt lacks staged effect authority");
    }
    const SyncReplicaDeliveryReceipt& evidence =
        *receipt.evidence_receipt;
    validate_sync_replica_delivery_receipt_or_throw(
        evidence, limits.evidence);
    if (evidence.folder_id != receipt.folder_id ||
        evidence.sender_actor != receipt.sender_actor ||
        evidence.receiver_actor != receipt.receiver_actor ||
        evidence.operation_id != receipt.operation_id ||
        evidence.claim_id != receipt.claim_id ||
        evidence.dispatch_attempts != receipt.dispatch_attempts ||
        evidence.channel_binding != receipt.channel_binding) {
        throw std::invalid_argument(
            "sync replica file delivery receipt and evidence receipt identities differ");
    }

    switch (receipt.disposition) {
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceCapacityBlocked:
            if (evidence.disposition !=
                    SyncReplicaDeliveryReceiptDisposition::CapacityBlocked ||
                evidence.evidence_state.has_value()) {
                throw std::invalid_argument(
                    "evidence-capacity receipt has incompatible evidence state");
            }
            break;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidencePending:
            if (!sync_replica_delivery_receipt_is_evidence_terminal(
                    evidence.disposition) ||
                !evidence_state_pending(evidence)) {
                throw std::invalid_argument(
                    "evidence-pending receipt has incompatible evidence state");
            }
            break;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceQuarantined:
            if (!sync_replica_delivery_receipt_is_evidence_terminal(
                    evidence.disposition) ||
                !evidence_state_quarantined(evidence)) {
                throw std::invalid_argument(
                    "evidence-quarantined receipt has incompatible evidence state");
            }
            break;
        case SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked:
        case SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict:
        case SyncReplicaFileDeliveryReceiptDisposition::Published:
        case SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished:
            if (!sync_replica_delivery_receipt_is_evidence_terminal(
                    evidence.disposition) ||
                !evidence_state_active(evidence)) {
                throw std::invalid_argument(
                    "file-effect receipt requires active evidence authority");
            }
            break;
        case SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked:
        case SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked:
            throw std::logic_error(
                "pre-effect receipt escaped its dedicated validation branch");
    }
}

std::string encode_sync_replica_file_delivery_request_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    return encode_frame_or_throw(
        kRequestMagic, kRequestDigestDomain,
        request_body_or_throw(request, limits),
        limits.max_request_frame_bytes,
        "sync replica file delivery request");
}

SyncReplicaFileDeliveryRequest
    decode_sync_replica_file_delivery_request_or_throw(
        std::string_view frame,
        const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_protocol_limits_or_throw(limits);
    return parse_request_body_or_throw(
        decode_frame_or_throw(
            frame, kRequestMagic, kRequestDigestDomain,
            limits.max_request_frame_bytes,
            "sync replica file delivery request"),
        limits);
}

std::string sync_replica_file_delivery_request_digest_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    return body_digest_or_throw(
        kRequestDigestDomain, request_body_or_throw(request, limits));
}

std::string encode_sync_replica_file_delivery_receipt_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    return encode_frame_or_throw(
        kReceiptMagic, kReceiptDigestDomain,
        receipt_body_or_throw(receipt, limits),
        limits.max_receipt_frame_bytes,
        "sync replica file delivery receipt");
}

SyncReplicaFileDeliveryReceipt
    decode_sync_replica_file_delivery_receipt_or_throw(
        std::string_view frame,
        const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_protocol_limits_or_throw(limits);
    return parse_receipt_body_or_throw(
        decode_frame_or_throw(
            frame, kReceiptMagic, kReceiptDigestDomain,
            limits.max_receipt_frame_bytes,
            "sync replica file delivery receipt"),
        limits);
}

std::string sync_replica_file_delivery_receipt_digest_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    return body_digest_or_throw(
        kReceiptDigestDomain, receipt_body_or_throw(receipt, limits));
}

void validate_sync_replica_file_delivery_receipt_for_request_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits) {
    validate_sync_replica_file_delivery_request_or_throw(request, limits);
    validate_sync_replica_file_delivery_receipt_or_throw(receipt, limits);
    const SyncReplicaDeliveryRequest& evidence_request =
        request.evidence_request;
    if (receipt.folder_id != evidence_request.folder_id ||
        receipt.sender_actor != evidence_request.sender_actor ||
        receipt.receiver_actor != evidence_request.receiver_actor ||
        receipt.operation_id != evidence_request.operation.operation_id ||
        receipt.claim_id != evidence_request.claim_id ||
        receipt.dispatch_attempts != evidence_request.dispatch_attempts ||
        receipt.channel_binding != evidence_request.channel_binding ||
        receipt.request_digest !=
            sync_replica_file_delivery_request_digest_or_throw(
                request, limits)) {
        throw std::runtime_error(
            "sync replica file delivery receipt does not bind the exact request attempt");
    }
    if (receipt.evidence_receipt.has_value()) {
        validate_sync_replica_delivery_receipt_for_request_or_throw(
            *receipt.evidence_receipt, evidence_request, limits.evidence);
        const std::string expected_effect_id =
            make_sync_replica_file_effect_id_or_throw(
                evidence_request.operation);
        if (receipt.effect_id != expected_effect_id) {
            throw std::runtime_error(
                "sync replica file delivery receipt effect id does not bind the request operation");
        }
    }
}

}  // namespace anonsync
