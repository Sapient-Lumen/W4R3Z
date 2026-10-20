#include "iotox/sync_reconstruction.hpp"

#include "toxsync/apply.hpp"
#include "toxsync/index_file.hpp"
#include "toxsync/planner.hpp"
#include "toxsync/range_source.hpp"

#include <algorithm>
#include <array>
#include <exception>
#include <limits>
#include <optional>
#include <string>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::string_view kRangePlanCommitmentInitialDomain =
    "iotox-sync-range-plan-commitment-initial-v2";
constexpr std::string_view kRangePlanCommitmentChunkDomain =
    "iotox-sync-range-plan-commitment-chunk-v2";
constexpr std::string_view kRangePlanCommitmentFinalDomain =
    "iotox-sync-range-plan-commitment-final-v2";
constexpr std::size_t kRangePlanCommitmentChunkBytes = 32U * 1024U;

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output.push_back(static_cast<std::uint8_t>(
        value >> (56U - static_cast<unsigned>(index) * 8U)));
  }
}

Digest from_toxsync(const toxsync::Digest256 &digest) noexcept {
  Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    result[index] = std::to_integer<std::uint8_t>(digest.bytes[index]);
  }
  return result;
}

toxsync::IndexLimits limits_for(const NamespacePolicy &policy) {
  toxsync::IndexLimits limits;
  limits.max_target_size = policy.quotas.maximum_artifact_bytes;
  const std::uint64_t records =
      policy.quotas.maximum_manifest_bytes <= toxsync::Index::kHeaderBytes
          ? 0U
          : (policy.quotas.maximum_manifest_bytes -
             toxsync::Index::kHeaderBytes) /
                toxsync::Index::kRecordBytes;
  limits.max_blocks = std::max<std::uint64_t>(records, 1U);
  return limits;
}

Status validate_records(const NamespacePolicy &policy,
                        const SyncObjectRecord &target,
                        const SyncObjectRecord &manifest,
                        const SyncObjectRecord &basis) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  if (policy.engine != Engine::range_v1) {
    return Status{ErrorCode::unsupported,
                  "range reconstruction requires a range-v1 namespace"};
  }
  if (target.kind != SyncObjectKind::artifact ||
      manifest.kind != SyncObjectKind::manifest ||
      basis.kind != SyncObjectKind::artifact || target.bytes == 0U ||
      manifest.bytes == 0U || basis.bytes == 0U ||
      target.bytes > policy.quotas.maximum_artifact_bytes ||
      basis.bytes > policy.quotas.maximum_artifact_bytes ||
      manifest.bytes > policy.quotas.maximum_manifest_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "range reconstruction object records are invalid"};
  }
  return Status::success();
}

Result<toxsync::Index> load_index(const NamespacePolicy &policy,
                                 const SyncObjectRecord &target,
                                 const SyncObjectRecord &manifest) {
  try {
    toxsync::Index index = toxsync::Index::read_file(
        sync_object_path(policy, manifest), limits_for(policy));
    if (index.target_size != target.bytes ||
        from_toxsync(index.target_digest) != target.identity ||
        index.encoded_size() != manifest.bytes) {
      return Status{
          ErrorCode::protocol_error,
          "range-v1 manifest is not bound to the requested target artifact"};
    }
    return index;
  } catch (const std::exception &exception) {
    return Status{ErrorCode::protocol_error,
                  "unable to load bounded range-v1 manifest: " +
                      std::string(exception.what())};
  }
}

Status verify_inputs(const NamespacePolicy &policy,
                     const SyncObjectRecord &manifest,
                     const SyncObjectRecord &basis,
                     const SyncNamespaceTransaction &transaction,
                     const SyncInstallSeams &seams) {
  const Status manifest_valid =
      verify_sync_object(policy, manifest, transaction, seams);
  if (!manifest_valid.ok()) return manifest_valid;
  return verify_sync_object(policy, basis, transaction, seams);
}

Result<toxsync::Plan> checked_toxsync_plan(const SyncRangePlan &plan,
                                          const toxsync::Index &index) {
  if (plan.block_bytes != index.block_size ||
      plan.blocks != index.blocks.size() ||
      plan.basis_offsets.size() != index.blocks.size() ||
      plan.basis_bytes != plan.basis.bytes ||
      plan.reused_bytes > plan.target.bytes ||
      plan.missing_bytes > plan.target.bytes ||
      plan.reused_bytes != plan.target.bytes - plan.missing_bytes) {
    return Status{ErrorCode::protocol_error,
                  "range reconstruction plan summary is inconsistent"};
  }

  std::vector<SyncMissingRange> derived;
  std::uint64_t reused = 0U;
  std::uint64_t missing = 0U;
  std::uint64_t target_offset = 0U;
  for (std::size_t block = 0U; block < index.blocks.size(); ++block) {
    const std::uint64_t length = index.blocks[block].length;
    const std::uint64_t basis_offset = plan.basis_offsets[block];
    if (basis_offset == toxsync::kMissingBasisOffset) {
      if (!derived.empty() &&
          derived.back().offset + derived.back().length == target_offset) {
        derived.back().length += length;
      } else {
        derived.push_back({target_offset, length});
      }
      missing += length;
    } else {
      if (basis_offset > plan.basis.bytes ||
          length > plan.basis.bytes - basis_offset) {
        return Status{ErrorCode::protocol_error,
                      "range reconstruction plan escapes its immutable basis"};
      }
      reused += length;
    }
    if (length > plan.target.bytes - target_offset) {
      return Status{ErrorCode::protocol_error,
                    "range reconstruction block layout overflows target"};
    }
    target_offset += length;
  }
  if (target_offset != plan.target.bytes || reused != plan.reused_bytes ||
      missing != plan.missing_bytes || derived != plan.missing_ranges) {
    return Status{ErrorCode::protocol_error,
                  "range reconstruction plan ranges are inconsistent"};
  }

  toxsync::Plan checked;
  checked.basis_offsets = plan.basis_offsets;
  checked.missing_ranges.reserve(plan.missing_ranges.size());
  for (const SyncMissingRange &range : plan.missing_ranges) {
    checked.missing_ranges.push_back({range.offset, range.length});
  }
  checked.stats.basis_size = plan.basis_bytes;
  checked.stats.reused_bytes = plan.reused_bytes;
  checked.stats.missing_bytes = plan.missing_bytes;
  checked.stats.matched_blocks = static_cast<std::uint64_t>(
      std::count_if(plan.basis_offsets.begin(), plan.basis_offsets.end(),
                    [](std::uint64_t offset) {
                      return offset != toxsync::kMissingBasisOffset;
                    }));
  return checked;
}

std::filesystem::path partial_path_for(
    const std::filesystem::path &staging) {
  std::filesystem::path result = staging;
  result += ".toxsync.part";
  return result;
}

Status remove_exact_output(const std::filesystem::path &path) {
  std::error_code error;
  const bool removed = std::filesystem::remove(path, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to remove failed range reconstruction output '" +
                      path.string() + "': " + error.message()};
  }
  static_cast<void>(removed);
  return Status::success();
}

class CallbackRangeSource final : public toxsync::RangeSource {
public:
  CallbackRangeSource(
      const std::function<Result<std::size_t>(
          std::uint64_t, std::span<std::uint8_t>)> *read,
      const std::function<bool()> *cancelled)
      : read_(read), cancelled_(cancelled) {}

  std::size_t read_at(std::uint64_t offset,
                      std::span<std::byte> output) override {
    if (cancelled_ != nullptr && *cancelled_ && (*cancelled_)()) {
      failure_ = Status{ErrorCode::unavailable,
                        "range reconstruction was cancelled"};
      throw std::runtime_error(failure_->message());
    }
    if (read_ == nullptr || !*read_) {
      failure_ = Status{ErrorCode::unavailable,
                        "range reconstruction has no source for missing bytes"};
      throw std::runtime_error(failure_->message());
    }
    auto bytes = std::span<std::uint8_t>(
        reinterpret_cast<std::uint8_t *>(output.data()), output.size());
    auto result = (*read_)(offset, bytes);
    if (!result) {
      failure_ = result.status();
      throw std::runtime_error(failure_->message());
    }
    if (result.value() > output.size()) {
      failure_ = Status{ErrorCode::protocol_error,
                        "range source returned more bytes than requested"};
      throw std::runtime_error(failure_->message());
    }
    if (cancelled_ != nullptr && *cancelled_ && (*cancelled_)()) {
      failure_ = Status{ErrorCode::unavailable,
                        "range reconstruction was cancelled"};
      throw std::runtime_error(failure_->message());
    }
    return result.value();
  }

  [[nodiscard]] const std::optional<Status> &failure() const noexcept {
    return failure_;
  }

private:
  const std::function<Result<std::size_t>(
      std::uint64_t, std::span<std::uint8_t>)> *read_{nullptr};
  const std::function<bool()> *cancelled_{nullptr};
  std::optional<Status> failure_;
};

} // namespace

Result<Digest> sync_range_plan_commitment(
    const SyncRangePlan &plan, const security::Sodium &sodium) {
  if (plan.target.kind != SyncObjectKind::artifact ||
      plan.manifest.kind != SyncObjectKind::manifest ||
      plan.basis.kind != SyncObjectKind::artifact ||
      plan.target.bytes == 0U || plan.manifest.bytes == 0U ||
      plan.basis.bytes == 0U || plan.block_bytes == 0U ||
      plan.blocks == 0U || plan.blocks != plan.basis_offsets.size() ||
      plan.basis_bytes != plan.basis.bytes || plan.missing_bytes == 0U ||
      plan.missing_bytes >= plan.target.bytes ||
      plan.reused_bytes != plan.target.bytes - plan.missing_bytes ||
      plan.missing_ranges.empty()) {
    return Status{ErrorCode::invalid_argument,
                  "sync range plan commitment input is inconsistent"};
  }
  std::uint64_t missing = 0U;
  std::uint64_t prior_end = 0U;
  for (const SyncMissingRange &range : plan.missing_ranges) {
    if (range.length == 0U || range.offset < prior_end ||
        range.offset > plan.target.bytes ||
        range.length > plan.target.bytes - range.offset ||
        range.length > std::numeric_limits<std::uint64_t>::max() - missing) {
      return Status{ErrorCode::invalid_argument,
                    "sync range plan commitment spans are inconsistent"};
    }
    missing += range.length;
    prior_end = range.offset + range.length;
  }
  if (missing != plan.missing_bytes) {
    return Status{ErrorCode::invalid_argument,
                  "sync range plan commitment byte total is inconsistent"};
  }
  if (plan.basis_offsets.size() >
          (std::numeric_limits<std::uint64_t>::max() - 160U) / 8U ||
      plan.missing_ranges.size() >
          (std::numeric_limits<std::uint64_t>::max() - 160U -
           static_cast<std::uint64_t>(plan.basis_offsets.size()) * 8U) /
              16U) {
    return Status{ErrorCode::resource_exhausted,
                  "sync range plan commitment encoding is too large"};
  }

  // Sodium::hash deliberately bounds a single payload at 64 KiB. Range
  // plans can contain one basis offset per small rolling-hash block, so a
  // useful plan may be much larger than that. Commit the canonical encoding
  // as a fixed-size domain-separated hash chain instead of either weakening
  // that primitive bound or allocating a second plan-sized buffer. The chunk
  // index, chunk length, total length, and final chunk count make boundaries
  // part of the commitment.
  auto initial = sodium.hash(kRangePlanCommitmentInitialDomain, {});
  if (!initial) return initial.status();
  Digest state = initial.value();
  std::vector<std::uint8_t> chunk;
  chunk.reserve(kRangePlanCommitmentChunkBytes);
  std::uint64_t chunk_index = 0U;
  std::uint64_t encoded_bytes = 0U;
  Status commitment_status = Status::success();
  const auto flush = [&]() {
    if (!commitment_status.ok() || chunk.empty()) return;
    std::vector<std::uint8_t> payload;
    payload.reserve(state.size() + 16U + chunk.size());
    payload.insert(payload.end(), state.begin(), state.end());
    append_u64(payload, chunk_index);
    append_u64(payload, chunk.size());
    payload.insert(payload.end(), chunk.begin(), chunk.end());
    auto next = sodium.hash(kRangePlanCommitmentChunkDomain, payload);
    if (!next) {
      commitment_status = next.status();
      return;
    }
    state = next.value();
    encoded_bytes += chunk.size();
    ++chunk_index;
    chunk.clear();
  };
  const auto append = [&](std::span<const std::uint8_t> bytes) {
    while (commitment_status.ok() && !bytes.empty()) {
      const std::size_t available =
          kRangePlanCommitmentChunkBytes - chunk.size();
      const std::size_t copied = std::min(available, bytes.size());
      chunk.insert(chunk.end(), bytes.begin(), bytes.begin() +
                                               static_cast<std::ptrdiff_t>(copied));
      bytes = bytes.subspan(copied);
      if (chunk.size() == kRangePlanCommitmentChunkBytes) flush();
    }
  };
  const auto append_u32_chunked = [&](std::uint32_t value) {
    std::array<std::uint8_t, 4U> bytes{};
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
      bytes[index] = static_cast<std::uint8_t>(
          value >> (24U - static_cast<unsigned>(index) * 8U));
    }
    append(bytes);
  };
  const auto append_u64_chunked = [&](std::uint64_t value) {
    std::array<std::uint8_t, 8U> bytes{};
    for (std::size_t index = 0U; index < bytes.size(); ++index) {
      bytes[index] = static_cast<std::uint8_t>(
          value >> (56U - static_cast<unsigned>(index) * 8U));
    }
    append(bytes);
  };
  const auto append_object_chunked = [&](const SyncObjectRecord &object) {
    const std::array<std::uint8_t, 1U> kind{
        static_cast<std::uint8_t>(object.kind)};
    append(kind);
    append(object.identity);
    append_u64_chunked(object.bytes);
  };

  append_object_chunked(plan.target);
  append_object_chunked(plan.manifest);
  append_object_chunked(plan.basis);
  append_u32_chunked(plan.block_bytes);
  append_u64_chunked(plan.blocks);
  append_u64_chunked(plan.basis_bytes);
  append_u64_chunked(plan.reused_bytes);
  append_u64_chunked(plan.missing_bytes);
  append_u64_chunked(plan.basis_offsets.size());
  for (const std::uint64_t offset : plan.basis_offsets) {
    append_u64_chunked(offset);
  }
  append_u64_chunked(plan.missing_ranges.size());
  for (const SyncMissingRange &range : plan.missing_ranges) {
    append_u64_chunked(range.offset);
    append_u64_chunked(range.length);
  }
  flush();
  if (!commitment_status.ok()) return commitment_status;
  std::vector<std::uint8_t> final;
  final.reserve(state.size() + 16U);
  final.insert(final.end(), state.begin(), state.end());
  append_u64(final, encoded_bytes);
  append_u64(final, chunk_index);
  return sodium.hash(kRangePlanCommitmentFinalDomain, final);
}

Result<SyncRangePlan> plan_sync_range_reconstruction(
    const NamespacePolicy &policy, const SyncObjectRecord &target,
    const SyncObjectRecord &manifest, const SyncObjectRecord &basis,
    const SyncNamespaceTransaction &transaction,
    const SyncInstallSeams &seams) {
  const Status records = validate_records(policy, target, manifest, basis);
  if (!records.ok()) return records;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (!seams.hash_file) {
    return Status{ErrorCode::invalid_argument,
                  "range planning requires an injected file hasher"};
  }
  const Status inputs = verify_inputs(
      policy, manifest, basis, transaction, seams);
  if (!inputs.ok()) return inputs;
  auto index = load_index(policy, target, manifest);
  if (!index) return index.status();

  try {
    toxsync::PlannerOptions options;
    options.max_basis_size = policy.quotas.maximum_artifact_bytes;
    const toxsync::Plan planned = toxsync::plan_file(
        index.value(), sync_object_path(policy, basis), options);
    if (planned.stats.reused_bytes > target.bytes ||
        planned.stats.missing_bytes > target.bytes ||
        planned.stats.reused_bytes !=
            target.bytes - planned.stats.missing_bytes ||
        planned.missing_ranges.size() >
            policy.quotas.maximum_outstanding_requests) {
      return Status{ErrorCode::resource_exhausted,
                    "range plan exceeds namespace request bounds"};
    }
    SyncRangePlan result;
    result.target = target;
    result.manifest = manifest;
    result.basis = basis;
    result.block_bytes = index.value().block_size;
    result.blocks = index.value().blocks.size();
    result.basis_bytes = planned.stats.basis_size;
    result.reused_bytes = planned.stats.reused_bytes;
    result.missing_bytes = planned.stats.missing_bytes;
    result.basis_read_calls = planned.stats.basis_read_calls;
    result.temporary_bytes_peak = planned.stats.temporary_bytes_peak;
    result.basis_offsets = planned.basis_offsets;
    result.missing_ranges.reserve(planned.missing_ranges.size());
    for (const toxsync::MissingRange &range : planned.missing_ranges) {
      result.missing_ranges.push_back({range.offset, range.length});
    }
    return result;
  } catch (const std::exception &exception) {
    return Status{ErrorCode::io_error,
                  "unable to plan range-v1 reconstruction: " +
                      std::string(exception.what())};
  }
}

Result<SyncRangeReconstructionResult> reconstruct_sync_range_artifact(
    const NamespacePolicy &policy, const SyncRangePlan &plan,
    std::uint64_t attempt_id,
    const SyncNamespaceTransaction &transaction,
    const SyncRangeReconstructionSeams &seams) {
  const Status records =
      validate_records(policy, plan.target, plan.manifest, plan.basis);
  if (!records.ok()) return records;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok()) return held;
  if (!seams.install.hash_file ||
      (plan.missing_bytes != 0U && !seams.read_range)) {
    return Status{ErrorCode::invalid_argument,
                  "range reconstruction seams are incomplete"};
  }
  if (seams.cancelled && seams.cancelled()) {
    return Status{ErrorCode::unavailable,
                  "range reconstruction was cancelled before staging"};
  }
  const Status inputs = verify_inputs(
      policy, plan.manifest, plan.basis, transaction, seams.install);
  if (!inputs.ok()) return inputs;
  auto index = load_index(policy, plan.target, plan.manifest);
  if (!index) return index.status();
  auto checked = checked_toxsync_plan(plan, index.value());
  if (!checked) return checked.status();
  auto staging = prepare_sync_attempt_staging(
      policy, attempt_id, plan.target, transaction);
  if (!staging) return staging.status();
  const std::filesystem::path partial = partial_path_for(staging.value());
  const Status old_partial = remove_exact_output(partial);
  if (!old_partial.ok()) return old_partial;

  CallbackRangeSource source(&seams.read_range, &seams.cancelled);
  toxsync::ApplyStats applied;
  try {
    toxsync::ApplyOptions options;
    options.resume = false;
    options.fsync_on_commit = true;
    applied = toxsync::apply_file(
        index.value(), checked.value(), sync_object_path(policy, plan.basis),
        source, staging.value(), options);
  } catch (const std::exception &exception) {
    const Status partial_removed = remove_exact_output(partial);
    const Status final_removed = remove_exact_output(staging.value());
    if (!partial_removed.ok()) return partial_removed;
    if (!final_removed.ok()) return final_removed;
    if (source.failure()) return *source.failure();
    return Status{ErrorCode::protocol_error,
                  "range-v1 reconstruction failed: " +
                      std::string(exception.what())};
  }
  if (seams.cancelled && seams.cancelled()) {
    const Status removed = remove_exact_output(staging.value());
    return removed.ok()
               ? Result<SyncRangeReconstructionResult>{Status{
                     ErrorCode::unavailable,
                     "range reconstruction was cancelled before commit"}}
               : Result<SyncRangeReconstructionResult>{removed};
  }
  auto digest = seams.install.hash_file(staging.value());
  if (!digest || digest.value() != plan.target.identity ||
      from_toxsync(applied.output_digest) != plan.target.identity ||
      applied.reused_bytes != plan.reused_bytes ||
      applied.fetched_bytes != plan.missing_bytes) {
    const Status removed = remove_exact_output(staging.value());
    if (!removed.ok()) return removed;
    if (!digest) return digest.status();
    return Status{ErrorCode::protocol_error,
                  "reconstructed staging artifact failed exact verification"};
  }

  SyncRangeReconstructionResult result;
  result.attempt_id = attempt_id;
  result.staging_path = staging.value();
  result.artifact = digest.value();
  result.artifact_bytes = plan.target.bytes;
  result.reused_bytes = applied.reused_bytes;
  result.fetched_bytes = applied.fetched_bytes;
  result.source_read_calls = applied.source_read_calls;
  result.basis_read_calls = applied.basis_read_calls;
  result.output_write_calls = applied.output_write_calls;
  return result;
}

} // namespace iotox::sync
