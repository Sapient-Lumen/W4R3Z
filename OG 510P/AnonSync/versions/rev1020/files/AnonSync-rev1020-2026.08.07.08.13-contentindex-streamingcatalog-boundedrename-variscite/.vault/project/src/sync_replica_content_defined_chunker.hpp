#pragma once

#include <cstdint>
#include <string_view>

namespace anonsync {

// Bounded deterministic FastCDC-style gear-hash parameters. The gear hash is
// only a boundary-selection heuristic. SHA-256 remains the authority for every
// emitted chunk and the completed payload.
struct SyncReplicaContentDefinedChunkingParameters final {
    std::uint64_t minimum_chunk_bytes = 0U;
    std::uint64_t average_chunk_bytes = 0U;
    std::uint64_t maximum_chunk_bytes = 0U;
    std::uint64_t maximum_chunk_count = 0U;

    bool operator==(
        const SyncReplicaContentDefinedChunkingParameters&) const = default;
};

void validate_sync_replica_content_defined_chunking_parameters_or_throw(
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    std::string_view label);

// Canonical scalar continuation for the allocation-free boundary detector.
// This is scheduling state, never byte or digest proof. A higher owner must
// bind it to an exact payload observation and resumable whole-file SHA-256.
struct SyncReplicaContentDefinedChunkerCheckpoint final {
    std::uint64_t gear_hash = 0U;
    std::uint64_t pending_chunk_bytes = 0U;
    std::uint64_t completed_chunk_count = 0U;
    bool finished = false;

    bool operator==(
        const SyncReplicaContentDefinedChunkerCheckpoint&) const = default;
};

void validate_sync_replica_content_defined_chunker_checkpoint_or_throw(
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    const SyncReplicaContentDefinedChunkerCheckpoint& checkpoint,
    std::string_view label);

// Allocation-free streaming boundary detector. consume_byte() returns true
// after consuming the byte that ends the current chunk. The caller owns chunk
// hashing and retained manifest storage; this class only owns bounded scalar
// scheduling state.
class SyncReplicaContentDefinedChunker final {
public:
    explicit SyncReplicaContentDefinedChunker(
        SyncReplicaContentDefinedChunkingParameters parameters,
        std::string_view label = "content-defined chunker");
    SyncReplicaContentDefinedChunker(
        SyncReplicaContentDefinedChunkingParameters parameters,
        SyncReplicaContentDefinedChunkerCheckpoint checkpoint,
        std::string_view label = "content-defined chunker checkpoint");

    [[nodiscard]] bool consume_byte(std::uint8_t byte);
    [[nodiscard]] bool has_pending_bytes() const noexcept {
        return pending_chunk_bytes_ != 0U;
    }
    [[nodiscard]] std::uint64_t pending_chunk_bytes() const noexcept {
        return pending_chunk_bytes_;
    }
    [[nodiscard]] std::uint64_t completed_chunk_count() const noexcept {
        return completed_chunk_count_;
    }
    [[nodiscard]] const SyncReplicaContentDefinedChunkingParameters&
    parameters() const noexcept {
        return parameters_;
    }
    [[nodiscard]] SyncReplicaContentDefinedChunkerCheckpoint checkpoint()
        const noexcept {
        return {
            gear_hash_, pending_chunk_bytes_, completed_chunk_count_, finished_};
    }

    // Records the final nonempty EOF chunk. It is an error to call this with no
    // pending bytes or more than once after the stream has ended.
    void finish_pending_chunk_or_throw();

    // Marks end of stream. A pending final chunk is completed; an exact chunk
    // boundary is accepted only after at least one completed chunk.
    void finish_stream_or_throw();

private:
    void complete_chunk_or_throw();

    SyncReplicaContentDefinedChunkingParameters parameters_;
    std::uint64_t boundary_mask_ = 0U;
    std::uint64_t gear_hash_ = 0U;
    std::uint64_t pending_chunk_bytes_ = 0U;
    std::uint64_t completed_chunk_count_ = 0U;
    bool finished_ = false;
};

}  // namespace anonsync
