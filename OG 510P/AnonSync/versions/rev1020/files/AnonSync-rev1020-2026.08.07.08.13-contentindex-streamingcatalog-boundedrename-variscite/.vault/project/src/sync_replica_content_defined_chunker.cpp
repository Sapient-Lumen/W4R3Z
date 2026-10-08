#include "sync_replica_content_defined_chunker.hpp"

#include <array>
#include <limits>
#include <stdexcept>
#include <string>

namespace anonsync {
namespace {

[[nodiscard]] constexpr std::uint64_t splitmix64(std::uint64_t value) {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31U);
}

[[nodiscard]] constexpr std::array<std::uint64_t, 256U> make_gear_table() {
    std::array<std::uint64_t, 256U> table{};
    for (std::size_t index = 0U; index < table.size(); ++index) {
        table[index] = splitmix64(
            0x416e6f6e53796e63ULL + static_cast<std::uint64_t>(index));
    }
    return table;
}

inline constexpr auto kGearTable = make_gear_table();

[[nodiscard]] constexpr bool is_power_of_two(std::uint64_t value) noexcept {
    return value != 0U && (value & (value - 1U)) == 0U;
}

}  // namespace

void validate_sync_replica_content_defined_chunking_parameters_or_throw(
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    std::string_view label_view) {
    const auto invalid = [label_view](std::string_view reason) {
        throw std::invalid_argument(
            std::string(label_view) + " " + std::string(reason));
    };
    if (parameters.minimum_chunk_bytes == 0U ||
        parameters.average_chunk_bytes == 0U ||
        parameters.maximum_chunk_bytes == 0U ||
        parameters.maximum_chunk_count == 0U) {
        invalid("requires positive chunk limits");
    }
    if (!is_power_of_two(parameters.average_chunk_bytes)) {
        invalid("average chunk size must be a power of two");
    }
    if (parameters.minimum_chunk_bytes > parameters.average_chunk_bytes ||
        parameters.average_chunk_bytes > parameters.maximum_chunk_bytes) {
        invalid("requires minimum <= average <= maximum chunk size");
    }
    if (parameters.maximum_chunk_bytes >
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
        invalid("maximum chunk size exceeds signed file offsets");
    }
}

void validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    const SyncReplicaContentDefinedChunkerCheckpoint& checkpoint,
    std::string_view label_view) {
    const std::string label(label_view);
    validate_sync_replica_content_defined_chunking_parameters_or_throw(
        parameters, label + " parameters");
    if (checkpoint.completed_chunk_count > parameters.maximum_chunk_count) {
        throw std::invalid_argument(
            label + " completed chunk count exceeds its frontier");
    }
    if (checkpoint.pending_chunk_bytes >= parameters.maximum_chunk_bytes) {
        throw std::invalid_argument(
            label + " pending chunk extent is not a resumable interior state");
    }
    if ((checkpoint.finished || checkpoint.pending_chunk_bytes == 0U) &&
        checkpoint.gear_hash != 0U) {
        throw std::invalid_argument(
            label + " empty chunk state carries a nonzero gear hash");
    }
    if (checkpoint.finished && checkpoint.pending_chunk_bytes != 0U) {
        throw std::invalid_argument(
            label + " finished state carries pending bytes");
    }
    if (!checkpoint.finished &&
        checkpoint.completed_chunk_count == parameters.maximum_chunk_count &&
        checkpoint.pending_chunk_bytes != 0U) {
        throw std::invalid_argument(
            label + " exhausted chunk count carries pending bytes");
    }
}

SyncReplicaContentDefinedChunker::SyncReplicaContentDefinedChunker(
    SyncReplicaContentDefinedChunkingParameters parameters,
    std::string_view label)
    : parameters_(parameters),
      boundary_mask_(parameters.average_chunk_bytes - 1U) {
    validate_sync_replica_content_defined_chunking_parameters_or_throw(
        parameters_, label);
}

SyncReplicaContentDefinedChunker::SyncReplicaContentDefinedChunker(
    SyncReplicaContentDefinedChunkingParameters parameters,
    SyncReplicaContentDefinedChunkerCheckpoint checkpoint,
    std::string_view label)
    : parameters_(parameters),
      boundary_mask_(parameters.average_chunk_bytes - 1U),
      gear_hash_(checkpoint.gear_hash),
      pending_chunk_bytes_(checkpoint.pending_chunk_bytes),
      completed_chunk_count_(checkpoint.completed_chunk_count),
      finished_(checkpoint.finished) {
    validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
        parameters_, checkpoint, label);
}

void SyncReplicaContentDefinedChunker::complete_chunk_or_throw() {
    if (completed_chunk_count_ == parameters_.maximum_chunk_count) {
        throw std::length_error(
            "content-defined chunk stream exceeds its chunk-count frontier");
    }
    ++completed_chunk_count_;
    gear_hash_ = 0U;
    pending_chunk_bytes_ = 0U;
}

bool SyncReplicaContentDefinedChunker::consume_byte(std::uint8_t byte) {
    if (finished_) {
        throw std::logic_error(
            "content-defined chunker consumed bytes after end of stream");
    }
    if (pending_chunk_bytes_ ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "content-defined chunk byte counter overflow");
    }
    gear_hash_ = (gear_hash_ << 1U) + kGearTable[byte];
    ++pending_chunk_bytes_;

    const bool reached_maximum =
        pending_chunk_bytes_ >= parameters_.maximum_chunk_bytes;
    const bool matched_boundary =
        pending_chunk_bytes_ >= parameters_.minimum_chunk_bytes &&
        (gear_hash_ & boundary_mask_) == 0U;
    if (!reached_maximum && !matched_boundary) return false;
    complete_chunk_or_throw();
    return true;
}

void SyncReplicaContentDefinedChunker::finish_pending_chunk_or_throw() {
    if (finished_) {
        throw std::logic_error(
            "content-defined chunker was finalized more than once");
    }
    if (pending_chunk_bytes_ == 0U) {
        throw std::logic_error(
            "content-defined chunker has no pending EOF chunk");
    }
    complete_chunk_or_throw();
    finished_ = true;
}

void SyncReplicaContentDefinedChunker::finish_stream_or_throw() {
    if (finished_) {
        throw std::logic_error(
            "content-defined chunker was finalized more than once");
    }
    if (pending_chunk_bytes_ != 0U) {
        complete_chunk_or_throw();
    } else if (completed_chunk_count_ == 0U) {
        throw std::logic_error(
            "content-defined chunker cannot finalize an empty stream");
    }
    finished_ = true;
}

}  // namespace anonsync
