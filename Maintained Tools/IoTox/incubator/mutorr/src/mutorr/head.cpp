#include "iotox/mutorr/head.hpp"

#include <algorithm>

namespace iotox::mutorr {
namespace {

void append_id(std::vector<std::uint8_t> &output, const Id256 &identifier) {
    output.insert(output.end(), identifier.bytes.begin(), identifier.bytes.end());
}

void append_u32_be(std::vector<std::uint8_t> &output, std::uint32_t value) {
    for (int shift = 24; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

void append_u64_be(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & 0xFFU));
    }
}

Id256 read_id(std::span<const std::uint8_t> bytes, std::size_t offset) {
    Id256 identifier;
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), kIdSize, identifier.bytes.begin());
    return identifier;
}

std::uint32_t read_u32_be(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>((value << 8U) | bytes[offset + index]);
    }
    return value;
}

std::uint64_t read_u64_be(std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

}  // namespace

Status validate_head(const HeadRecord &head) {
    if (head.wire_version != kHeadWireVersion) {
        return Status{ErrorCode::protocol_error, "unsupported mutable-head wire version"};
    }
    if (head.namespace_id.is_zero()) {
        return Status{ErrorCode::protocol_error, "mutable head has an empty namespace identifier"};
    }
    if (head.writer_key.is_zero()) {
        return Status{ErrorCode::protocol_error, "mutable head has an empty writer key"};
    }
    if (head.root.is_zero()) {
        return Status{ErrorCode::protocol_error, "mutable head has an empty root digest"};
    }
    if (head.generation == 0U) {
        return Status{ErrorCode::protocol_error, "mutable head generation must start at one"};
    }
    if (head.generation == 1U && !head.previous.is_zero()) {
        return Status{ErrorCode::protocol_error, "generation one must not name a previous root"};
    }
    if (head.generation > 1U && head.previous.is_zero()) {
        return Status{ErrorCode::protocol_error, "later generations must name a previous root"};
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>> head_signing_bytes(const HeadRecord &head) {
    const Status valid = validate_head(head);
    if (!valid.ok()) {
        return valid;
    }

    std::vector<std::uint8_t> output;
    output.reserve(kHeadSigningSize);
    output.push_back(head.wire_version);
    append_id(output, head.namespace_id);
    append_id(output, head.writer_key);
    append_u64_be(output, head.generation);
    append_id(output, head.root);
    append_id(output, head.previous);
    append_u64_be(output, head.created_unix_ms);
    append_u64_be(output, head.content_bytes);
    append_u32_be(output, head.object_count);
    return output;
}

Result<std::vector<std::uint8_t>> encode_head(const HeadRecord &head) {
    auto output = head_signing_bytes(head);
    if (!output) {
        return output.status();
    }
    output.value().insert(output.value().end(), head.signature.begin(), head.signature.end());
    return std::move(output).value();
}

Result<HeadRecord> decode_head(std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kHeadWireSize) {
        return Status{ErrorCode::protocol_error, "mutable-head payload has the wrong fixed size"};
    }

    HeadRecord head;
    std::size_t offset = 0U;
    head.wire_version = bytes[offset++];
    head.namespace_id = read_id(bytes, offset);
    offset += kIdSize;
    head.writer_key = read_id(bytes, offset);
    offset += kIdSize;
    head.generation = read_u64_be(bytes, offset);
    offset += 8U;
    head.root = read_id(bytes, offset);
    offset += kIdSize;
    head.previous = read_id(bytes, offset);
    offset += kIdSize;
    head.created_unix_ms = read_u64_be(bytes, offset);
    offset += 8U;
    head.content_bytes = read_u64_be(bytes, offset);
    offset += 8U;
    head.object_count = read_u32_be(bytes, offset);
    offset += 4U;
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), kSignatureSize, head.signature.begin());

    const Status valid = validate_head(head);
    if (!valid.ok()) {
        return valid;
    }
    return head;
}

HeadDecision evaluate_head(const HeadRecord *current, const HeadRecord &candidate) {
    if (!validate_head(candidate).ok()) {
        return HeadDecision::invalid;
    }

    if (current == nullptr) {
        return candidate.generation == 1U ? HeadDecision::accept_initial : HeadDecision::requires_history;
    }
    if (!validate_head(*current).ok()) {
        return HeadDecision::invalid;
    }
    if (current->namespace_id != candidate.namespace_id || current->writer_key != candidate.writer_key) {
        return HeadDecision::different_stream;
    }
    if (candidate.generation < current->generation) {
        return HeadDecision::stale;
    }
    if (candidate.generation == current->generation) {
        return candidate == *current ? HeadDecision::duplicate : HeadDecision::conflict;
    }
    if (candidate.previous == current->root) {
        return HeadDecision::accept_advance;
    }
    return HeadDecision::requires_history;
}

const char *to_string(HeadDecision decision) noexcept {
    switch (decision) {
        case HeadDecision::accept_initial:
            return "accept-initial";
        case HeadDecision::accept_advance:
            return "accept-advance";
        case HeadDecision::duplicate:
            return "duplicate";
        case HeadDecision::stale:
            return "stale";
        case HeadDecision::conflict:
            return "conflict";
        case HeadDecision::requires_history:
            return "requires-history";
        case HeadDecision::different_stream:
            return "different-stream";
        case HeadDecision::invalid:
            return "invalid";
    }
    return "unknown";
}

}  // namespace iotox::mutorr
