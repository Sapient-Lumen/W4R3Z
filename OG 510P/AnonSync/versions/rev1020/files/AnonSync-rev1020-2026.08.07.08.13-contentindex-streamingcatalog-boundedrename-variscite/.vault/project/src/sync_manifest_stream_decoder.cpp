#include "sync_manifest_stream_decoder.hpp"

#include "sha256_digest.hpp"

#include <cstddef>
#include <limits>
#include <string>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] SyncValidationResult ok() {
    return {true, {}};
}

[[nodiscard]] SyncValidationResult bad(std::string reason) {
    return {false, std::move(reason)};
}

[[nodiscard]] bool usage_equal(
    const SyncManifestResourceUsage& left,
    const SyncManifestResourceUsage& right) noexcept {
    return left.entries == right.entries &&
           left.chunks == right.chunks &&
           left.lineage_entries == right.lineage_entries &&
           left.path_bytes == right.path_bytes &&
           left.metadata_bytes == right.metadata_bytes;
}

[[nodiscard]] SyncValidationResult validate_header_semantics(
    const SyncManifestEntryStreamHeader& header) {
    if (!sync_id_is_valid(header.folder_id)) {
        return bad("folder_id must be lowercase portable sync id");
    }
    if (!sync_id_is_valid(header.device_id)) {
        return bad("device_id must be lowercase portable sync id");
    }
    const SyncValidationResult path =
        validate_sync_relative_path(header.path);
    if (!path.ok) return path;
    if (!header.conflict_set_id.empty() &&
        !sync_id_is_valid(header.conflict_set_id)) {
        return bad(
            "conflict_set_id must be empty or a lowercase portable sync id");
    }
    if (header.declared_lineage_count == 0U) {
        return bad("manifest entry requires version lineage");
    }

    if (header.kind == SyncManifestEntryKind::Tombstone) {
        if (header.size_bytes != 0U) {
            return bad("tombstone size must be zero");
        }
        if (!header.content_sha256.empty()) {
            return bad("tombstone must not carry content hash");
        }
        if (header.declared_chunk_count != 0U) {
            return bad("tombstone must not carry chunks");
        }
        return ok();
    }
    if (header.kind != SyncManifestEntryKind::File) {
        return bad("manifest entry has unknown kind");
    }
    if (!is_lowercase_sha256_hex(header.content_sha256)) {
        return bad(
            "file manifest entry requires lowercase sha256 content hash");
    }
    if (header.size_bytes == 0U && header.declared_chunk_count != 0U) {
        return bad("zero-byte file must not carry chunks");
    }
    if (header.size_bytes > 0U && header.declared_chunk_count == 0U) {
        return bad("nonempty file requires chunk ranges");
    }
    return ok();
}

}  // namespace

SyncValidationResult SyncManifestEntryStreamDecoder::begin(
    const SyncManifestEntryStreamHeader& header,
    const SyncManifestResourceLimits& limits) {
    if (state_ != State::Empty) return state_failure("begin");

    // All count and byte observations are admitted against locals before this
    // owner retains bytes or permits vector growth.
    SyncManifestResourceBudget proposed_budget(limits);
    SyncValidationResult result = proposed_budget.admit_entry_count(1U);
    if (!result.ok) return fail(std::move(result.reason));
    result = proposed_budget.admit_entry_shape(
        header.declared_chunk_count,
        header.declared_lineage_count,
        header.path.size());
    if (!result.ok) return fail(std::move(result.reason));
    for (const std::size_t bytes : {
             header.folder_id.size(),
             header.device_id.size(),
             header.path.size(),
             header.content_sha256.size(),
             header.conflict_set_id.size(),
             static_cast<std::size_t>(9U)}) {
        result = proposed_budget.admit_metadata_bytes(bytes);
        if (!result.ok) return fail(std::move(result.reason));
    }
    result = validate_header_semantics(header);
    if (!result.ok) return fail(std::move(result.reason));

    SyncManifestEntry proposed;
    proposed.folder_id.assign(header.folder_id);
    proposed.device_id.assign(header.device_id);
    proposed.path.value.assign(header.path);
    proposed.kind = header.kind;
    proposed.size_bytes = header.size_bytes;
    proposed.content_sha256.assign(header.content_sha256);
    proposed.conflict_set_id.assign(header.conflict_set_id);

    limits_ = limits;
    budget_ = proposed_budget;
    candidate_ = std::move(proposed);
    declared_chunk_count_ = header.declared_chunk_count;
    declared_lineage_count_ = header.declared_lineage_count;
    accepted_chunk_count_ = 0;
    accepted_lineage_count_ = 0;
    next_chunk_offset_ = 0;
    failure_reason_.clear();
    state_ = State::Active;
    return ok();
}

SyncValidationResult SyncManifestEntryStreamDecoder::append_chunk(
    std::uint64_t offset,
    std::uint64_t length,
    std::string_view sha256) {
    if (state_ != State::Active) return state_failure("append_chunk");
    if (chunks_accepted() >= declared_chunk_count_) {
        return fail(
            "manifest decoder received more chunk rows than declared");
    }
    if (offset != next_chunk_offset_) {
        return fail("chunk ranges must be contiguous from offset zero");
    }
    if (length == 0U) {
        return fail("chunk range length must be positive");
    }
    if (!is_lowercase_sha256_hex(sha256)) {
        return fail("chunk range requires lowercase sha256 hash");
    }
    if (length >
        std::numeric_limits<std::uint64_t>::max() - next_chunk_offset_) {
        return fail("chunk ranges overflow uint64");
    }

    SyncValidationResult result = budget_.admit_metadata_bytes(sha256.size());
    if (!result.ok) return fail(std::move(result.reason));
    result = budget_.admit_metadata_bytes(16U);
    if (!result.ok) return fail(std::move(result.reason));

    SyncChunkRange chunk;
    chunk.offset = offset;
    chunk.length = length;
    chunk.sha256.assign(sha256);
    candidate_.chunks.push_back(std::move(chunk));
    ++accepted_chunk_count_;
    next_chunk_offset_ += length;
    return ok();
}

SyncValidationResult SyncManifestEntryStreamDecoder::append_lineage(
    std::string_view device_id,
    std::uint64_t counter) {
    if (state_ != State::Active) return state_failure("append_lineage");
    if (lineage_entries_accepted() >= declared_lineage_count_) {
        return fail(
            "manifest decoder received more lineage rows than declared");
    }
    if (!sync_id_is_valid(device_id)) {
        return fail(
            "lineage device_id must be lowercase portable sync id");
    }
    if (counter == 0U) {
        return fail("lineage counter must be positive");
    }
    if (!candidate_.lineage.empty() &&
        device_id.compare(candidate_.lineage.back().device_id) <= 0) {
        return fail(
            "lineage entries must be unique and sorted by device_id");
    }

    SyncValidationResult result =
        budget_.admit_metadata_bytes(device_id.size());
    if (!result.ok) return fail(std::move(result.reason));
    result = budget_.admit_metadata_bytes(8U);
    if (!result.ok) return fail(std::move(result.reason));

    SyncVersionLineageEntry lineage;
    lineage.device_id.assign(device_id);
    lineage.counter = counter;
    candidate_.lineage.push_back(std::move(lineage));
    ++accepted_lineage_count_;
    return ok();
}

SyncValidationResult SyncManifestEntryStreamDecoder::finish(
    SyncManifestEntry& out,
    SyncManifestResourceUsage* usage_out) {
    if (state_ != State::Active) return state_failure("finish");
    if (chunks_accepted() != declared_chunk_count_) {
        return fail(
            "manifest decoder chunk rows do not match declared count");
    }
    if (lineage_entries_accepted() != declared_lineage_count_) {
        return fail(
            "manifest decoder lineage rows do not match declared count");
    }
    if (candidate_.kind == SyncManifestEntryKind::File &&
        next_chunk_offset_ != candidate_.size_bytes) {
        return fail("chunk ranges must cover exactly size_bytes");
    }

    SyncManifestResourceUsage verified_usage;
    const SyncValidationResult validation =
        validate_sync_manifest_entry_with_limits(
            candidate_, limits_, &verified_usage);
    if (!validation.ok) return fail(validation.reason);
    if (!usage_equal(verified_usage, budget_.usage())) {
        return fail(
            "manifest decoder incremental resource accounting mismatch");
    }

    out = std::move(candidate_);
    if (usage_out != nullptr) *usage_out = verified_usage;
    state_ = State::Finished;
    return ok();
}

bool SyncManifestEntryStreamDecoder::active() const noexcept {
    return state_ == State::Active;
}

bool SyncManifestEntryStreamDecoder::failed() const noexcept {
    return state_ == State::Failed;
}

std::uint64_t SyncManifestEntryStreamDecoder::chunks_accepted() const noexcept {
    return accepted_chunk_count_;
}

std::uint64_t
SyncManifestEntryStreamDecoder::lineage_entries_accepted() const noexcept {
    return accepted_lineage_count_;
}

SyncValidationResult SyncManifestEntryStreamDecoder::state_failure(
    std::string_view operation) const {
    if (state_ == State::Failed) {
        return bad(failure_reason_);
    }
    if (state_ == State::Empty) {
        return bad(
            "manifest decoder " + std::string(operation) +
            " requires a successful begin");
    }
    if (state_ == State::Active) {
        return bad(
            "manifest decoder " + std::string(operation) +
            " is not permitted while a stream is already active");
    }
    return bad(
        "manifest decoder " + std::string(operation) +
        " is not permitted after finish");
}

SyncValidationResult SyncManifestEntryStreamDecoder::fail(
    std::string reason) {
    if (state_ != State::Failed) {
        failure_reason_ = std::move(reason);
        candidate_ = SyncManifestEntry{};
        accepted_chunk_count_ = 0;
        accepted_lineage_count_ = 0;
        next_chunk_offset_ = 0;
        state_ = State::Failed;
    }
    return bad(failure_reason_);
}

}  // namespace anonsync
