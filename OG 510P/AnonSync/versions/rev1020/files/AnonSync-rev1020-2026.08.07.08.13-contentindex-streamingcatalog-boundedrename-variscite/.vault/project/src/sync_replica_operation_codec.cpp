#include "sync_replica_model.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_operation_codec_internal.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kCanonicalMagic =
    "anonsync-sync-replica-operation-v2";
constexpr std::size_t kU64Bytes = 8U;
constexpr std::size_t kKindBytes = 1U;
constexpr std::size_t kSha256HexBytes = 64U;
constexpr std::size_t kMinimumActorBytes = 1U;
constexpr std::size_t kMinimumContextEntryBytes =
    kU64Bytes + kMinimumActorBytes + kU64Bytes + kU64Bytes;
constexpr std::size_t kCanonicalPredecessorBytes =
    kU64Bytes + kSha256HexBytes;

[[nodiscard]] bool kind_is_valid(SyncReplicaValueKind kind) noexcept {
    return kind == SyncReplicaValueKind::File ||
           kind == SyncReplicaValueKind::Tombstone;
}

[[nodiscard]] std::uint8_t kind_code_or_throw(SyncReplicaValueKind kind) {
    switch (kind) {
        case SyncReplicaValueKind::File:
            return 0U;
        case SyncReplicaValueKind::Tombstone:
            return 1U;
    }
    throw std::invalid_argument(
        "sync replica operation has unknown value kind");
}

[[nodiscard]] SyncReplicaValueKind kind_from_code_or_throw(
    std::uint8_t code) {
    switch (code) {
        case 0U:
            return SyncReplicaValueKind::File;
        case 1U:
            return SyncReplicaValueKind::Tombstone;
        default:
            throw std::invalid_argument(
                "sync replica canonical operation has unknown value kind code");
    }
}

void add_size_or_throw(
    std::size_t& total,
    std::size_t amount,
    std::string_view label) {
    if (amount > std::numeric_limits<std::size_t>::max() - total) {
        throw std::overflow_error(
            "sync replica canonical operation size overflow at " +
            std::string(label));
    }
    total += amount;
}

void add_framed_string_size_or_throw(
    std::size_t& total,
    std::string_view value,
    std::string_view label) {
    add_size_or_throw(total, kU64Bytes, label);
    add_size_or_throw(total, value.size(), label);
}

[[nodiscard]] std::size_t canonical_size_after_semantic_validation_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    std::size_t total = kCanonicalMagic.size();
    add_framed_string_size_or_throw(total, operation.folder_id, "folder_id");
    add_framed_string_size_or_throw(
        total, operation.canonical_path, "canonical_path");
    add_size_or_throw(total, kKindBytes, "kind");
    add_size_or_throw(total, kU64Bytes, "size_bytes");
    add_framed_string_size_or_throw(
        total, operation.content_sha256, "content_sha256");
    add_framed_string_size_or_throw(
        total, operation.dot.actor.device_id, "dot actor device_id");
    add_size_or_throw(total, kU64Bytes, "dot actor epoch");
    add_size_or_throw(total, kU64Bytes, "dot counter");
    add_size_or_throw(total, kU64Bytes, "causal context count");
    for (const SyncReplicaClockEntry& entry : operation.causal_context) {
        add_framed_string_size_or_throw(
            total, entry.actor.device_id,
            "causal context actor device_id");
        add_size_or_throw(total, kU64Bytes, "causal context actor epoch");
        add_size_or_throw(total, kU64Bytes, "causal context counter");
    }
    add_size_or_throw(total, kU64Bytes, "predecessor count");
    for (const std::string& predecessor :
         operation.predecessor_operation_ids) {
        add_framed_string_size_or_throw(
            total, predecessor, "predecessor operation_id");
    }

    if (std::cmp_greater(
            total, limits.max_canonical_operation_bytes)) {
        throw std::length_error(
            "sync replica canonical operation exceeds configured byte limit");
    }
    return total;
}

[[nodiscard]] std::size_t validate_operation_semantics_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    detail::validate_sync_replica_model_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(operation.folder_id)) {
        throw std::invalid_argument(
            "sync replica operation folder_id must be a lowercase portable sync id");
    }
    const SyncValidationResult path =
        validate_sync_relative_path(operation.canonical_path);
    if (!path.ok) {
        throw std::invalid_argument(
            "sync replica operation path is not canonical: " + path.reason);
    }
    if (!kind_is_valid(operation.kind)) {
        throw std::invalid_argument(
            "sync replica operation has unknown value kind");
    }
    detail::validate_sync_replica_actor_or_throw(
        operation.dot.actor, "sync replica dot");
    if (operation.dot.counter == 0U) {
        throw std::invalid_argument(
            "sync replica dot counter must be positive");
    }
    if (operation.dot.counter > limits.max_operations) {
        throw std::invalid_argument(
            "sync replica dot counter implies more retained history than the configured model limit");
    }
    if (operation.causal_context.size() >
        limits.max_context_entries) {
        throw std::invalid_argument(
            "sync replica causal context exceeds configured entry limit");
    }
    if (operation.predecessor_operation_ids.size() >
        limits.max_predecessor_ids) {
        throw std::invalid_argument(
            "sync replica predecessor set exceeds configured entry limit");
    }
    if (operation.predecessor_operation_ids.size() >=
        limits.max_operations) {
        throw std::invalid_argument(
            "sync replica operation plus exact predecessors exceeds the configured model limit");
    }

    // Keep only an observer into the already-owned context. Copying the
    // previous actor cloned its device_id on every validation pass, turning an
    // otherwise measurement-only traversal into avoidable heap traffic.
    const SyncReplicaActor* previous_actor = nullptr;
    std::uint64_t implied_past_events = 0;
    for (const SyncReplicaClockEntry& entry : operation.causal_context) {
        detail::validate_sync_replica_actor_or_throw(
            entry.actor, "sync replica causal context");
        if (entry.counter == 0U) {
            throw std::invalid_argument(
                "sync replica causal context omits zero counters instead of encoding them");
        }
        if (entry.counter > limits.max_operations ||
            entry.counter > limits.max_operations - implied_past_events) {
            throw std::invalid_argument(
                "sync replica causal context implies more retained history than the configured model limit");
        }
        implied_past_events += entry.counter;
        if (previous_actor != nullptr &&
            !(*previous_actor < entry.actor)) {
            throw std::invalid_argument(
                "sync replica causal context must be strictly sorted with unique actors");
        }
        previous_actor = &entry.actor;
    }
    if (implied_past_events >= limits.max_operations) {
        throw std::invalid_argument(
            "sync replica operation plus causal past exceeds the configured model limit");
    }

    const std::uint64_t own_past = detail::sync_replica_context_counter(
        operation.causal_context, operation.dot.actor);
    if (own_past == std::numeric_limits<std::uint64_t>::max() ||
        own_past + 1U != operation.dot.counter) {
        throw std::invalid_argument(
            "sync replica dot must be the next event in its single-writer actor epoch");
    }

    std::optional<std::string_view> previous_predecessor;
    for (const std::string& predecessor :
         operation.predecessor_operation_ids) {
        if (!is_lowercase_sha256_hex(predecessor)) {
            throw std::invalid_argument(
                "sync replica predecessor operation_id must be a lowercase SHA-256 digest");
        }
        if (previous_predecessor.has_value() &&
            previous_predecessor.value() >= predecessor) {
            throw std::invalid_argument(
                "sync replica predecessor operation IDs must be strictly sorted and unique");
        }
        previous_predecessor = predecessor;
    }

    if (operation.kind == SyncReplicaValueKind::File) {
        if (!is_lowercase_sha256_hex(operation.content_sha256)) {
            throw std::invalid_argument(
                "sync replica file operation requires a lowercase SHA-256 content digest");
        }
    } else if (operation.size_bytes != 0U ||
               !operation.content_sha256.empty()) {
        throw std::invalid_argument(
            "sync replica tombstone must not carry file size or content digest");
    }

    return canonical_size_after_semantic_validation_or_throw(
        operation, limits);
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

void append_string(std::string& output, std::string_view value) {
    append_u64(output, static_cast<std::uint64_t>(value.size()));
    output.append(value.data(), value.size());
}

[[nodiscard]] std::string encode_after_semantic_validation_or_throw(
    const SyncReplicaOperation& operation,
    std::size_t encoded_size) {
    std::string output;
    output.reserve(encoded_size);
    output.append(kCanonicalMagic.data(), kCanonicalMagic.size());
    append_string(output, operation.folder_id);
    append_string(output, operation.canonical_path);
    output.push_back(static_cast<char>(kind_code_or_throw(operation.kind)));
    append_u64(output, operation.size_bytes);
    append_string(output, operation.content_sha256);
    append_string(output, operation.dot.actor.device_id);
    append_u64(output, operation.dot.actor.epoch);
    append_u64(output, operation.dot.counter);
    append_u64(
        output, static_cast<std::uint64_t>(operation.causal_context.size()));
    for (const SyncReplicaClockEntry& entry : operation.causal_context) {
        append_string(output, entry.actor.device_id);
        append_u64(output, entry.actor.epoch);
        append_u64(output, entry.counter);
    }
    append_u64(
        output,
        static_cast<std::uint64_t>(
            operation.predecessor_operation_ids.size()));
    for (const std::string& predecessor :
         operation.predecessor_operation_ids) {
        append_string(output, predecessor);
    }
    if (output.size() != encoded_size) {
        throw std::logic_error(
            "sync replica canonical operation size preflight disagreed with encoding");
    }
    return output;
}

void validate_operation_id_shape_or_throw(
    const SyncReplicaOperation& operation) {
    if (!is_lowercase_sha256_hex(operation.operation_id)) {
        throw std::invalid_argument(
            "sync replica operation_id must be a lowercase SHA-256 digest");
    }
    if (std::binary_search(
            operation.predecessor_operation_ids.begin(),
            operation.predecessor_operation_ids.end(),
            operation.operation_id)) {
        throw std::invalid_argument(
            "sync replica operation cannot name itself as a predecessor");
    }
}

class CanonicalReader final {
public:
    explicit CanonicalReader(std::string_view input) : input_(input) {}

    void require_magic() {
        if (input_.substr(position_, kCanonicalMagic.size()) !=
            kCanonicalMagic) {
            throw std::invalid_argument(
                "sync replica canonical operation has wrong format/version magic");
        }
        position_ += kCanonicalMagic.size();
    }

    [[nodiscard]] std::uint8_t read_u8(std::string_view label) {
        require_remaining(1U, label);
        return static_cast<std::uint8_t>(
            static_cast<unsigned char>(input_[position_++]));
    }

    [[nodiscard]] std::uint64_t read_u64(std::string_view label) {
        require_remaining(kU64Bytes, label);
        std::uint64_t value = 0;
        for (std::size_t index = 0; index < kU64Bytes; ++index) {
            value = (value << 8U) |
                    static_cast<std::uint8_t>(static_cast<unsigned char>(
                        input_[position_ + index]));
        }
        position_ += kU64Bytes;
        return value;
    }

    [[nodiscard]] std::string read_string(std::string_view label) {
        const std::uint64_t length = read_u64(label);
        if (length > std::numeric_limits<std::size_t>::max()) {
            throw std::length_error(
                "sync replica canonical operation string length exceeds size_t at " +
                std::string(label));
        }
        const std::size_t converted = static_cast<std::size_t>(length);
        require_remaining(converted, label);
        std::string value(input_.substr(position_, converted));
        position_ += converted;
        return value;
    }

    void require_finished() const {
        if (position_ != input_.size()) {
            throw std::invalid_argument(
                "sync replica canonical operation contains trailing bytes");
        }
    }

    [[nodiscard]] std::size_t remaining() const noexcept {
        return input_.size() - position_;
    }

private:
    void require_remaining(std::size_t count, std::string_view label) const {
        if (count > input_.size() - position_) {
            throw std::invalid_argument(
                "sync replica canonical operation is truncated at " +
                std::string(label));
        }
    }

    std::string_view input_;
    std::size_t position_ = 0;
};

[[nodiscard]] std::size_t checked_count_or_throw(
    std::uint64_t count,
    std::uint64_t limit,
    std::string_view label) {
    if (count > limit) {
        throw std::length_error(
            "sync replica canonical operation " + std::string(label) +
            " exceeds configured limit");
    }
    if (count > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            "sync replica canonical operation " + std::string(label) +
            " exceeds size_t");
    }
    return static_cast<std::size_t>(count);
}

void require_count_fits_remaining_or_throw(
    std::size_t count,
    std::size_t minimum_item_bytes,
    std::size_t required_suffix_bytes,
    std::size_t remaining_bytes,
    std::string_view label) {
    if (remaining_bytes < required_suffix_bytes ||
        count > (remaining_bytes - required_suffix_bytes) /
                    minimum_item_bytes) {
        throw std::invalid_argument(
            "sync replica canonical operation " + std::string(label) +
            " cannot fit in the remaining canonical bytes");
    }
}

}  // namespace

namespace detail {

void validate_sync_replica_model_limits_impl_or_throw(
    const SyncReplicaModelLimits& limits) {
    if (limits.max_operations == 0U) {
        throw std::invalid_argument(
            "sync replica model max_operations must be positive");
    }
    if (limits.max_context_entries == 0U) {
        throw std::invalid_argument(
            "sync replica model max_context_entries must be positive");
    }
    if (limits.max_predecessor_ids == 0U) {
        throw std::invalid_argument(
            "sync replica model max_predecessor_ids must be positive");
    }
    if (limits.max_canonical_operation_bytes == 0U) {
        throw std::invalid_argument(
            "sync replica model max_canonical_operation_bytes must be positive");
    }
    if (limits.max_retained_canonical_bytes <
        limits.max_canonical_operation_bytes) {
        throw std::invalid_argument(
            "sync replica model retained canonical-byte budget must admit one maximum-size operation");
    }
    if (limits.max_retained_context_entries <
        limits.max_context_entries) {
        throw std::invalid_argument(
            "sync replica model retained context-entry budget must admit one maximum-size context");
    }
    if (limits.max_retained_predecessor_ids <
        limits.max_predecessor_ids) {
        throw std::invalid_argument(
            "sync replica model retained predecessor-ID budget must admit one maximum-size predecessor set");
    }
}

std::uint64_t validate_sync_replica_operation_and_measure_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    const std::size_t encoded_size =
        validate_operation_semantics_or_throw(operation, limits);
    validate_operation_id_shape_or_throw(operation);
    if (sha256_hex(encode_after_semantic_validation_or_throw(
            operation, encoded_size)) != operation.operation_id) {
        throw std::invalid_argument(
            "sync replica operation_id does not bind the exact canonical operation bytes");
    }
    if (std::cmp_greater(
            encoded_size,
            std::numeric_limits<std::uint64_t>::max())) {
        throw std::overflow_error(
            "sync replica canonical operation size does not fit uint64_t");
    }
    return static_cast<std::uint64_t>(encoded_size);
}

void validate_sync_replica_actor_or_throw(
    const SyncReplicaActor& actor,
    std::string_view label) {
    if (!sync_id_is_valid(actor.device_id)) {
        throw std::invalid_argument(
            std::string(label) +
            " device_id must be a lowercase portable sync id");
    }
    if (actor.epoch == 0U) {
        throw std::invalid_argument(
            std::string(label) + " epoch must be positive");
    }
}

std::uint64_t sync_replica_context_counter(
    const std::vector<SyncReplicaClockEntry>& context,
    const SyncReplicaActor& actor) noexcept {
    const auto found = std::lower_bound(
        context.begin(), context.end(), actor,
        [](const SyncReplicaClockEntry& entry,
           const SyncReplicaActor& target) {
            return entry.actor < target;
        });
    if (found == context.end() || found->actor != actor) return 0;
    return found->counter;
}

}  // namespace detail

void validate_sync_replica_model_limits_or_throw(
    const SyncReplicaModelLimits& limits) {
    detail::validate_sync_replica_model_limits_impl_or_throw(limits);
}

std::uint64_t sync_replica_operation_canonical_size_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    const std::size_t encoded_size =
        validate_operation_semantics_or_throw(operation, limits);
    if (std::cmp_greater(
            encoded_size,
            std::numeric_limits<std::uint64_t>::max())) {
        throw std::overflow_error(
            "sync replica canonical operation size does not fit uint64_t");
    }
    return static_cast<std::uint64_t>(encoded_size);
}

std::string encode_sync_replica_operation_canonical_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    const std::size_t encoded_size =
        validate_operation_semantics_or_throw(operation, limits);
    return encode_after_semantic_validation_or_throw(
        operation, encoded_size);
}

SyncReplicaOperation decode_sync_replica_operation_canonical_or_throw(
    std::string_view canonical_bytes,
    const SyncReplicaModelLimits& limits) {
    detail::validate_sync_replica_model_limits_impl_or_throw(limits);
    if (std::cmp_greater(
            canonical_bytes.size(),
            limits.max_canonical_operation_bytes)) {
        throw std::length_error(
            "sync replica canonical operation exceeds configured byte limit");
    }

    CanonicalReader reader(canonical_bytes);
    reader.require_magic();

    SyncReplicaOperation operation;
    operation.folder_id = reader.read_string("folder_id");
    operation.canonical_path = reader.read_string("canonical_path");
    operation.kind = kind_from_code_or_throw(reader.read_u8("kind"));
    operation.size_bytes = reader.read_u64("size_bytes");
    operation.content_sha256 = reader.read_string("content_sha256");
    operation.dot.actor.device_id = reader.read_string("dot actor device_id");
    operation.dot.actor.epoch = reader.read_u64("dot actor epoch");
    operation.dot.counter = reader.read_u64("dot counter");

    const std::uint64_t max_context_count = std::min(
        limits.max_context_entries, limits.max_operations - 1U);
    const std::size_t context_count = checked_count_or_throw(
        reader.read_u64("causal context count"),
        max_context_count,
        "causal context count");
    require_count_fits_remaining_or_throw(
        context_count,
        kMinimumContextEntryBytes,
        kU64Bytes,
        reader.remaining(),
        "causal context count");
    operation.causal_context.reserve(context_count);
    for (std::size_t index = 0; index < context_count; ++index) {
        SyncReplicaClockEntry entry;
        entry.actor.device_id =
            reader.read_string("causal context actor device_id");
        entry.actor.epoch = reader.read_u64("causal context actor epoch");
        entry.counter = reader.read_u64("causal context counter");
        operation.causal_context.push_back(std::move(entry));
    }

    const std::uint64_t max_predecessor_count = std::min(
        limits.max_predecessor_ids, limits.max_operations - 1U);
    const std::size_t predecessor_count = checked_count_or_throw(
        reader.read_u64("predecessor count"),
        max_predecessor_count,
        "predecessor count");
    require_count_fits_remaining_or_throw(
        predecessor_count,
        kCanonicalPredecessorBytes,
        0U,
        reader.remaining(),
        "predecessor count");
    operation.predecessor_operation_ids.reserve(predecessor_count);
    for (std::size_t index = 0; index < predecessor_count; ++index) {
        operation.predecessor_operation_ids.push_back(
            reader.read_string("predecessor operation_id"));
    }
    reader.require_finished();

    Sha256DigestBuilder exact_bytes_digest;
    exact_bytes_digest.update(canonical_bytes);
    operation.operation_id = exact_bytes_digest.finish_hex();
    const std::size_t encoded_size =
        validate_operation_semantics_or_throw(operation, limits);
    validate_operation_id_shape_or_throw(operation);
    if (encode_after_semantic_validation_or_throw(
            operation, encoded_size) != canonical_bytes) {
        throw std::invalid_argument(
            "sync replica operation bytes are not the canonical encoding of the decoded value");
    }
    return operation;
}

std::string make_sync_replica_operation_id_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    const std::size_t encoded_size =
        validate_operation_semantics_or_throw(operation, limits);
    return sha256_hex(encode_after_semantic_validation_or_throw(
        operation, encoded_size));
}

void validate_sync_replica_operation_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaModelLimits& limits) {
    (void)detail::validate_sync_replica_operation_and_measure_or_throw(
        operation, limits);
}

bool sync_replica_context_covers_dot(
    const std::vector<SyncReplicaClockEntry>& context,
    const SyncReplicaDot& dot) noexcept {
    return detail::sync_replica_context_counter(context, dot.actor) >=
           dot.counter;
}

bool sync_replica_operation_supersedes(
    const SyncReplicaOperation& newer,
    const SyncReplicaOperation& older) noexcept {
    return newer.operation_id != older.operation_id &&
           newer.folder_id == older.folder_id &&
           newer.canonical_path == older.canonical_path &&
           sync_replica_context_covers_dot(
               newer.causal_context, older.dot);
}

}  // namespace anonsync
