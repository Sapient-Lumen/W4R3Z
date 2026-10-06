#include "bzip4/parallel_codec.hpp"

#include "bzip4/libbz3.h"

#include "frame_envelope.hpp"
#include "frame_source.hpp"

#include <algorithm>
#include <array>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <variant>
#include <vector>

namespace bzip4 {
namespace {

constexpr std::size_t frame_header_size = detail::frame_header_size;
constexpr std::size_t block_header_size = detail::block_header_size;
constexpr std::size_t maximum_retained_background_workers = 256;

void write_u32_le(std::byte* output, std::uint32_t value) noexcept {
    output[0] = static_cast<std::byte>(value & 0xffU);
    output[1] = static_cast<std::byte>((value >> 8U) & 0xffU);
    output[2] = static_cast<std::byte>((value >> 16U) & 0xffU);
    output[3] = static_cast<std::byte>((value >> 24U) & 0xffU);
}

[[nodiscard]] std::size_t checked_add(std::size_t left, std::size_t right) {
    if (right > std::numeric_limits<std::size_t>::max() - left) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "parallel frame size arithmetic overflow");
    }
    return left + right;
}

[[nodiscard]] std::size_t checked_mul(std::size_t left, std::size_t right) {
    if (left != 0 && right > std::numeric_limits<std::size_t>::max() / left) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "parallel workspace arithmetic overflow");
    }
    return left * right;
}

[[nodiscard]] std::size_t block_count_for(
    std::size_t input_size,
    std::uint32_t block_size) {
    return input_size == 0 ? 0 : 1 + (input_size - 1) / block_size;
}

[[nodiscard]] FrameInfo emit_empty_frame(
    std::uint32_t block_size,
    const FrameSink& sink) {
    if (!sink) {
        throw std::invalid_argument("frame sink must be callable");
    }
    (void)frame_bound(0, block_size);

    FrameInfo info;
    info.block_size = block_size;

    std::array<std::byte, frame_header_size> header{};
    header[0] = std::byte{'B'};
    header[1] = std::byte{'Z'};
    header[2] = std::byte{'3'};
    header[3] = std::byte{'v'};
    header[4] = std::byte{'1'};
    write_u32_le(header.data() + 5, block_size);
    write_u32_le(header.data() + 9, 0);
    sink(header);
    return info;
}

struct EncodeLaneTask {
    std::size_t input_size{};
    std::uint64_t input_offset{};
    const RangeReader* reader{};
};

struct DecodeLaneTask {
    detail::BlockDescriptor block;
    const RangeReader* reader{};
};

using CodecLaneTask = std::variant<EncodeLaneTask, DecodeLaneTask>;

struct CodecLaneResult {
    std::span<const std::byte> output;
    std::exception_ptr error;
};

[[nodiscard]] std::span<const std::byte> execute_codec_task(
    Workspace& workspace,
    const CodecLaneTask& task) {
    if (const auto* encode = std::get_if<EncodeLaneTask>(&task)) {
        if (encode->reader == nullptr) {
            throw std::logic_error("parallel encode task received a null reader");
        }
        return workspace.encode_block_from(
            encode->input_size, encode->input_offset, *encode->reader);
    }

    const auto& decode = std::get<DecodeLaneTask>(task);
    if (decode.reader == nullptr) {
        throw std::logic_error("parallel decode task received a null reader");
    }
    return workspace.decode_block_from(
        decode.block.compressed_size,
        decode.block.original_size,
        detail::source_offset(decode.block.payload_offset),
        *decode.reader);
}

[[nodiscard]] CodecLaneResult capture_codec_task(
    Workspace& workspace,
    const CodecLaneTask& task) noexcept {
    CodecLaneResult result;
    try {
        result.output = execute_codec_task(workspace, task);
    } catch (...) {
        result.error = std::current_exception();
    }
    return result;
}

/**
 * One retained worker lifecycle shared by the compatible encoder and decoder.
 *
 * The coordinator owns task and callback lifetimes. A generation is not reused
 * until wait() acknowledges it, and an inactive all-retained wake is represented
 * by an empty optional task rather than a second control protocol.
 */
class RetainedCodecLane final {
public:
    explicit RetainedCodecLane(std::uint32_t block_size)
        : workspace_(block_size) {
        // Start only after every synchronization and result field exists.
        thread_ = std::thread([this] { run(); });
    }

    ~RetainedCodecLane() {
        {
            std::lock_guard lock(mutex_);
            stopping_ = true;
        }
        start_.notify_one();
        if (thread_.joinable()) {
            thread_.join();
        }
    }

    RetainedCodecLane(const RetainedCodecLane&) = delete;
    RetainedCodecLane& operator=(const RetainedCodecLane&) = delete;

    void dispatch(std::size_t generation, std::optional<CodecLaneTask> task) {
        {
            std::lock_guard lock(mutex_);
            if (requested_generation_ != completed_generation_) {
                throw std::logic_error(
                    "parallel worker was redispatched before its prior generation completed");
            }
            if (generation <= requested_generation_) {
                throw std::logic_error("parallel worker generation did not advance");
            }
            task_ = std::move(task);
            result_ = {};
            error_ = nullptr;
            requested_generation_ = generation;
        }
        start_.notify_one();
    }

    [[nodiscard]] CodecLaneResult wait(std::size_t generation) {
        std::unique_lock lock(mutex_);
        if (generation != requested_generation_) {
            throw std::logic_error(
                "parallel worker wait does not match its dispatched generation");
        }
        done_.wait(lock, [&] {
            return completed_generation_ == generation;
        });
        return {result_, error_};
    }

private:
    void run() noexcept {
        std::size_t observed_generation = 0;
        for (;;) {
            std::optional<CodecLaneTask> task;
            std::size_t generation = 0;
            {
                std::unique_lock lock(mutex_);
                start_.wait(lock, [&] {
                    return stopping_ || requested_generation_ > observed_generation;
                });
                if (stopping_) {
                    return;
                }
                generation = requested_generation_;
                task = task_;
            }

            CodecLaneResult result;
            if (task) {
                result = capture_codec_task(workspace_, *task);
            }

            {
                std::lock_guard lock(mutex_);
                result_ = result.output;
                error_ = result.error;
                task_.reset();
                completed_generation_ = generation;
                observed_generation = generation;
            }
            done_.notify_one();
        }
    }

    Workspace workspace_;
    std::mutex mutex_;
    std::condition_variable start_;
    std::condition_variable done_;
    std::optional<CodecLaneTask> task_;
    std::span<const std::byte> result_;
    std::exception_ptr error_;
    std::size_t requested_generation_{};
    std::size_t completed_generation_{};
    bool stopping_{};
    std::thread thread_;
};


[[nodiscard]] std::uint32_t validated_decoder_block_size(
    std::uint32_t declared_block_size,
    std::uint32_t decoder_block_size) {
    // Preserve the existing retained-decoder constructor error contract for an
    // invalid declared BZ3v1 block size.
    (void)frame_bound(0, declared_block_size);
    if (decoder_block_size < min_block_size ||
        decoder_block_size > declared_block_size) {
        throw std::invalid_argument(
            "parallel decoder workspace block size is outside the declared range");
    }
    (void)workspace_memory_bound(decoder_block_size);
    return decoder_block_size;
}

struct RetainedPoolShape {
    std::size_t background_workers{};
    std::size_t retained_lanes{};
    std::size_t per_lane_workspace_bytes{};
    std::size_t retained_workspace_bytes{};
    bool caller_participates{};
};

[[nodiscard]] RetainedPoolShape retained_pool_shape(
    std::uint32_t block_size,
    const ParallelFramePolicy& policy) {
    if (policy.activation.retained_background_workers >
        maximum_retained_background_workers) {
        throw std::invalid_argument(
            "retained background worker count exceeds the hard safety limit");
    }

    RetainedPoolShape shape;
    shape.background_workers = policy.activation.retained_background_workers;
    shape.caller_participates = policy.activation.caller_participates;
    const std::size_t caller_lanes = shape.caller_participates ? 1U : 0U;
    shape.retained_lanes = checked_add(shape.background_workers, caller_lanes);
    if (shape.retained_lanes == 0) {
        throw std::invalid_argument(
            "parallel codec requires a caller lane or a retained background worker");
    }

    shape.per_lane_workspace_bytes = workspace_memory_bound(block_size);
    shape.retained_workspace_bytes = checked_mul(
        shape.retained_lanes, shape.per_lane_workspace_bytes);
    if (shape.retained_workspace_bytes > policy.max_workspace_bytes) {
        throw CodecError(
            BZ3_ERR_DATA_TOO_BIG,
            "retained parallel workspaces exceed the configured memory budget");
    }
    return shape;
}

class RetainedLanePool final {
public:
    RetainedLanePool(std::uint32_t block_size, const RetainedPoolShape& shape) {
        // Reserve every coordinator-owned allocation before starting a thread.
        background_.reserve(shape.background_workers);
        if (shape.caller_participates) {
            caller_workspace_ = std::make_unique<Workspace>(block_size);
        }
        for (std::size_t index = 0; index < shape.background_workers; ++index) {
            (void)index;
            background_.push_back(std::make_unique<RetainedCodecLane>(block_size));
        }
    }

    [[nodiscard]] Workspace& caller_workspace() {
        if (!caller_workspace_) {
            throw std::logic_error("parallel caller workspace is not retained");
        }
        return *caller_workspace_;
    }

    [[nodiscard]] RetainedCodecLane& background(std::size_t index) {
        return *background_[index];
    }

    [[nodiscard]] std::size_t background_workers() const noexcept {
        return background_.size();
    }

private:
    std::unique_ptr<Workspace> caller_workspace_;
    std::vector<std::unique_ptr<RetainedCodecLane>> background_;
};

/**
 * Run one bounded generation and establish the common postcondition used by
 * both directions: every notified worker has acknowledged, all active results
 * are retained in coordinator-owned slots, and only then may an exception be
 * propagated or a workspace span be published.
 */
template <class BackgroundTaskFactory>
[[nodiscard]] CodecLaneResult run_retained_batch(
    RetainedLanePool& pool,
    std::size_t generation,
    std::optional<CodecLaneTask> caller_task,
    std::size_t background_tasks,
    std::size_t notified_workers,
    std::span<CodecLaneResult> background_results,
    BackgroundTaskFactory&& make_background_task) {
    if (background_tasks > notified_workers ||
        notified_workers > pool.background_workers() ||
        background_results.size() < background_tasks) {
        throw std::logic_error("invalid retained parallel batch shape");
    }

    for (std::size_t worker = 0; worker < background_tasks; ++worker) {
        background_results[worker] = {};
    }

    std::size_t dispatched = 0;
    try {
        for (std::size_t worker = 0; worker < notified_workers; ++worker) {
            std::optional<CodecLaneTask> task;
            if (worker < background_tasks) {
                task.emplace(make_background_task(worker));
            }
            pool.background(worker).dispatch(generation, std::move(task));
            ++dispatched;
        }
    } catch (...) {
        for (std::size_t worker = 0; worker < dispatched; ++worker) {
            (void)pool.background(worker).wait(generation);
        }
        throw;
    }

    CodecLaneResult caller_result;
    if (caller_task) {
        try {
            caller_result = capture_codec_task(pool.caller_workspace(), *caller_task);
        } catch (...) {
            // A pool-shape invariant failure must still observe the same drain
            // barrier as an ordinary caller-lane codec failure.
            caller_result.error = std::current_exception();
        }
    }

    for (std::size_t worker = 0; worker < notified_workers; ++worker) {
        const CodecLaneResult result = pool.background(worker).wait(generation);
        if (worker < background_tasks) {
            background_results[worker] = result;
        }
    }

    if (caller_result.error) {
        std::rethrow_exception(caller_result.error);
    }
    for (std::size_t worker = 0; worker < background_tasks; ++worker) {
        if (background_results[worker].error) {
            std::rethrow_exception(background_results[worker].error);
        }
    }
    return caller_result;
}

[[nodiscard]] const RangeReader* prepare_parallel_reader(
    bool serialize,
    std::mutex& mutex,
    const RangeReader& reader,
    std::optional<RangeReader>& serialized_reader) {
    if (!serialize) {
        return &reader;
    }
    serialized_reader.emplace(
        [&mutex, &reader](std::uint64_t offset, std::span<std::byte> output) {
            std::lock_guard lock(mutex);
            reader(offset, output);
        });
    return &*serialized_reader;
}

} // namespace

class ParallelFrameEncoder::Impl final {
public:
    Impl(std::uint32_t block_size, ParallelFramePolicy policy)
        : block_size_(block_size),
          policy_(std::move(policy)),
          shape_(retained_pool_shape(block_size_, policy_)),
          background_results_(shape_.background_workers),
          pool_(block_size_, shape_) {}

    [[nodiscard]] FrameInfo encode(
        std::size_t input_size,
        const RangeReader& reader,
        const FrameSink& sink,
        ParallelFrameStats* stats) {
        std::lock_guard call_lock(call_mutex_);
        if (!reader) {
            throw std::invalid_argument("range reader must be callable");
        }
        if (!sink) {
            throw std::invalid_argument("frame sink must be callable");
        }

        (void)frame_bound(input_size, block_size_);
        const std::size_t block_count = block_count_for(input_size, block_size_);
        if (block_count > std::numeric_limits<std::uint32_t>::max()) {
            throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                             "parallel frame block count cannot be represented in BZ3v1");
        }

        ActivationPolicy activation = policy_.activation;
        activation.retained_background_workers = pool_.background_workers();
        const ActivationPlan plan = make_activation_plan(
            block_count, input_size, activation);
        if (block_count != 0 && plan.active_lanes == 0) {
            throw std::invalid_argument("parallel activation policy selected no executor");
        }

        ParallelFrameStats local_stats;
        local_stats.activation = plan;
        local_stats.retained_background_workers = pool_.background_workers();
        local_stats.retained_lanes = shape_.retained_lanes;
        local_stats.per_lane_workspace_bytes = shape_.per_lane_workspace_bytes;
        local_stats.retained_workspace_bytes = shape_.retained_workspace_bytes;
        local_stats.productive_lanes = plan.active_lanes;

        FrameInfo info;
        info.block_size = block_size_;
        info.block_count = static_cast<std::uint32_t>(block_count);
        info.original_size = input_size;
        detail::DecoderWorkspaceRequirements decoder_requirements;

        std::array<std::byte, frame_header_size> header{};
        header[0] = std::byte{'B'};
        header[1] = std::byte{'Z'};
        header[2] = std::byte{'3'};
        header[3] = std::byte{'v'};
        header[4] = std::byte{'1'};
        write_u32_le(header.data() + 5, info.block_size);
        write_u32_le(header.data() + 9, info.block_count);
        sink(header);

        if (block_count == 0) {
            if (stats != nullptr) {
                *stats = local_stats;
            }
            return info;
        }

        std::optional<RangeReader> serialized_reader;
        const RangeReader* active_reader = prepare_parallel_reader(
            policy_.serialize_range_reads, reader_mutex_, reader,
            serialized_reader);
        std::size_t first_block = 0;
        while (first_block < block_count) {
            const std::size_t batch_size = std::min(
                plan.active_lanes, block_count - first_block);
            local_stats.batches = checked_add(local_stats.batches, 1);
            local_stats.peak_blocks_in_flight = std::max(
                local_stats.peak_blocks_in_flight, batch_size);

            const bool caller_active = activation.caller_participates && batch_size != 0;
            const std::size_t caller_tasks = caller_active ? 1U : 0U;
            const std::size_t background_tasks = batch_size - caller_tasks;
            if (background_tasks > pool_.background_workers()) {
                throw std::logic_error("parallel activation exceeds retained workers");
            }

            const std::size_t notified = activation.wake_mode == WakeMode::all_retained
                ? pool_.background_workers() : background_tasks;
            local_stats.background_notifications = checked_add(
                local_stats.background_notifications, notified);
            local_stats.inactive_worker_wakeups = checked_add(
                local_stats.inactive_worker_wakeups, notified - background_tasks);

            const std::size_t generation = checked_add(generation_, 1);
            generation_ = generation;
            local_stats.generation = generation;

            std::optional<CodecLaneTask> caller_task;
            if (caller_active) {
                const std::size_t offset = checked_mul(first_block, block_size_);
                const std::size_t size = std::min<std::size_t>(
                    block_size_, input_size - offset);
                caller_task.emplace(EncodeLaneTask{
                    size, detail::source_offset(offset), active_reader});
            }
            const CodecLaneResult caller_result = run_retained_batch(
                pool_, generation, std::move(caller_task), background_tasks,
                notified, background_results_,
                [&](std::size_t worker) -> CodecLaneTask {
                    const std::size_t block_index = checked_add(
                        first_block, checked_add(caller_tasks, worker));
                    const std::size_t offset = checked_mul(block_index, block_size_);
                    const std::size_t size = std::min<std::size_t>(
                        block_size_, input_size - offset);
                    return EncodeLaneTask{
                        size, detail::source_offset(offset), active_reader};
                });

            for (std::size_t batch_index = 0; batch_index < batch_size; ++batch_index) {
                const std::size_t block_index = checked_add(first_block, batch_index);
                const std::size_t offset = checked_mul(block_index, block_size_);
                const std::size_t original_size = std::min<std::size_t>(
                    block_size_, input_size - offset);
                const std::span<const std::byte> encoded =
                    caller_active && batch_index == 0
                    ? caller_result.output
                    : background_results_[batch_index - caller_tasks].output;
                if (encoded.size() > static_cast<std::size_t>(
                        std::numeric_limits<std::int32_t>::max())) {
                    throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                                     "encoded block cannot be represented in BZ3v1");
                }

                const detail::BlockEnvelopeValidation envelope =
                    detail::validate_block_envelope(
                        encoded.size(),
                        {reinterpret_cast<const std::uint8_t*>(encoded.data()),
                         encoded.size()},
                        original_size, info.block_size);
                if (envelope.error_code != BZ3_OK) {
                    throw CodecError(
                        envelope.error_code,
                        std::string("parallel encoder produced an invalid block envelope: ") +
                            detail::block_envelope_issue_message(envelope.issue));
                }
                detail::merge_decoder_requirements(
                    decoder_requirements, envelope);

                std::array<std::byte, block_header_size> descriptor{};
                write_u32_le(descriptor.data(), static_cast<std::uint32_t>(encoded.size()));
                write_u32_le(descriptor.data() + 4,
                             static_cast<std::uint32_t>(original_size));
                sink(descriptor);
                sink(encoded);
                info.encoded_block_bytes = checked_add(
                    info.encoded_block_bytes, encoded.size());
            }

            local_stats.caller_blocks = checked_add(
                local_stats.caller_blocks, caller_tasks);
            local_stats.background_blocks = checked_add(
                local_stats.background_blocks, background_tasks);
            first_block = checked_add(first_block, batch_size);
        }

        if (checked_add(local_stats.caller_blocks, local_stats.background_blocks) !=
            block_count) {
            throw std::logic_error("parallel block accounting mismatch");
        }
        info.decoder_block_size = detail::select_decoder_block_size(
            decoder_requirements, info.block_size);
        if (info.decoder_block_size == 0) {
            throw std::logic_error(
                "parallel encoder envelope requirements do not fit its workspace declaration");
        }
        info.decoder_workspace_bytes = workspace_memory_bound(
            info.decoder_block_size);
        if (stats != nullptr) {
            *stats = local_stats;
        }
        return info;
    }

    std::uint32_t block_size_{};
    ParallelFramePolicy policy_;
    RetainedPoolShape shape_;
    std::vector<CodecLaneResult> background_results_;
    RetainedLanePool pool_;
    std::mutex call_mutex_;
    std::mutex reader_mutex_;
    std::size_t generation_{};
};

ParallelFrameEncoder::ParallelFrameEncoder(
    std::uint32_t block_size,
    ParallelFramePolicy policy)
    : impl_(std::make_unique<Impl>(block_size, std::move(policy))) {}

ParallelFrameEncoder::~ParallelFrameEncoder() = default;

std::uint32_t ParallelFrameEncoder::block_size() const noexcept {
    return impl_ ? impl_->block_size_ : 0;
}

std::size_t ParallelFrameEncoder::retained_background_workers() const noexcept {
    return impl_ ? impl_->pool_.background_workers() : 0;
}

std::size_t ParallelFrameEncoder::retained_workspace_bytes() const noexcept {
    return impl_ ? impl_->shape_.retained_workspace_bytes : 0;
}

FrameInfo ParallelFrameEncoder::encode_frame_to(
    std::span<const std::byte> input,
    const FrameSink& sink,
    ParallelFrameStats* stats) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from parallel encoder");
    }
    const RangeReader reader = detail::span_reader(input);
    return impl_->encode(input.size(), reader, sink, stats);
}

FrameInfo ParallelFrameEncoder::encode_frame_from(
    std::size_t input_size,
    const RangeReader& reader,
    const FrameSink& sink,
    ParallelFrameStats* stats) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from parallel encoder");
    }
    return impl_->encode(input_size, reader, sink, stats);
}

FrameInfo compress_frame_parallel_to(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    ParallelFrameStats* stats) {
    const RangeReader reader = detail::span_reader(input);
    return compress_frame_parallel_from(
        input.size(), requested_block_size, reader, sink,
        std::move(policy), stats);
}

FrameInfo compress_frame_parallel_from(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    const RangeReader& reader,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    ParallelFrameStats* stats) {
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (!sink) {
        throw std::invalid_argument("frame sink must be callable");
    }
    if (policy.activation.retained_background_workers >
        maximum_retained_background_workers) {
        throw std::invalid_argument(
            "retained background worker count exceeds the hard safety limit");
    }
    const std::uint32_t block_size = select_frame_block_size(
        requested_block_size, input_size);
    const std::size_t blocks = block_count_for(input_size, block_size);
    if (blocks == 0) {
        ParallelFrameStats empty_stats;
        empty_stats.activation = make_activation_plan(0, 0, policy.activation);
        empty_stats.per_lane_workspace_bytes = workspace_memory_bound(block_size);
        // No block codec state, worker, or retained workspace is needed to emit
        // the canonical 13-byte empty frame. Keep the one-shot memory-policy
        // accounting literal rather than silently allocating a scalar workspace.
        const FrameInfo info = emit_empty_frame(block_size, sink);
        if (stats != nullptr) {
            *stats = empty_stats;
        }
        return info;
    }
    if (policy.activation.wake_mode == WakeMode::active_only) {
        // A one-shot active-only pool has no later frame that could use an
        // inactive retained worker. Apply block, maximum-lane, and floor-grain
        // policy before charging workspaces or starting threads. all_retained is
        // an explicit wake-control mode and therefore preserves its configured
        // inactive population (subject to the normal hard and memory limits).
        const ActivationPlan plan = make_activation_plan(
            blocks, input_size, policy.activation);
        policy.activation.retained_background_workers =
            plan.active_background_workers;
    }
    ParallelFrameEncoder encoder(block_size, std::move(policy));
    return encoder.encode_frame_from(input_size, reader, sink, stats);
}


class ParallelFrameDecoder::Impl final {
public:
    Impl(
        std::uint32_t block_size,
        std::uint32_t decoder_block_size,
        ParallelFramePolicy policy)
        : block_size_(block_size),
          decoder_block_size_(validated_decoder_block_size(
              block_size_, decoder_block_size)),
          policy_(std::move(policy)),
          shape_(retained_pool_shape(decoder_block_size_, policy_)),
          background_results_(shape_.background_workers),
          batch_descriptors_(shape_.retained_lanes),
          pool_(decoder_block_size_, shape_) {}

    [[nodiscard]] FrameInfo decode(
        std::size_t encoded_size,
        const RangeReader& reader,
        std::size_t max_output_size,
        const FrameSink& sink,
        bool reject_trailing_bytes,
        ParallelDecodeStats* stats) {
        std::lock_guard call_lock(call_mutex_);
        if (!reader) {
            throw std::invalid_argument("range reader must be callable");
        }
        if (!sink) {
            throw std::invalid_argument("frame sink must be callable");
        }

        std::optional<RangeReader> serialized_reader;
        const RangeReader* active_reader = prepare_parallel_reader(
            policy_.serialize_range_reads, reader_mutex_, reader,
            serialized_reader);
        const detail::FrameSource source{encoded_size, *active_reader};
        const FrameInfo info = detail::scan_frame_source(
            source, max_output_size, reject_trailing_bytes,
            policy_.max_workspace_bytes);
        return decode_validated_locked(source, info, sink, stats);
    }

    [[nodiscard]] FrameInfo decode_validated(
        std::size_t encoded_size,
        const RangeReader& reader,
        const FrameInfo& info,
        const FrameSink& sink,
        ParallelDecodeStats* stats) {
        std::lock_guard call_lock(call_mutex_);
        if (!reader) {
            throw std::invalid_argument("range reader must be callable");
        }
        if (!sink) {
            throw std::invalid_argument("frame sink must be callable");
        }
        std::optional<RangeReader> serialized_reader;
        const RangeReader* active_reader = prepare_parallel_reader(
            policy_.serialize_range_reads, reader_mutex_, reader,
            serialized_reader);
        const detail::FrameSource source{encoded_size, *active_reader};
        return decode_validated_locked(source, info, sink, stats);
    }

    [[nodiscard]] FrameInfo decode_validated_locked(
        const detail::FrameSource& source,
        const FrameInfo& info,
        const FrameSink& sink,
        ParallelDecodeStats* stats) {
        if (info.block_size != block_size_) {
            throw CodecError(
                BZ3_ERR_MALFORMED_HEADER,
                "frame block size does not match the retained parallel decoder");
        }
        if (info.block_count != 0) {
            if (info.decoder_block_size > decoder_block_size_ ||
                info.decoder_workspace_bytes > shape_.per_lane_workspace_bytes) {
                throw CodecError(
                    BZ3_ERR_DATA_TOO_BIG,
                    "validated frame extent exceeds the retained decoder workspace");
            }
            if (shape_.per_lane_workspace_bytes !=
                workspace_memory_bound(decoder_block_size_)) {
                throw std::logic_error(
                    "parallel decoder workspace accounting mismatch");
            }
        }

        ActivationPolicy activation = policy_.activation;
        activation.retained_background_workers = pool_.background_workers();
        const ActivationPlan plan = make_activation_plan(
            info.block_count, info.original_size, activation);
        if (info.block_count != 0 && plan.active_lanes == 0) {
            throw std::invalid_argument("parallel activation policy selected no executor");
        }

        ParallelDecodeStats local_stats;
        local_stats.activation = plan;
        local_stats.retained_background_workers = pool_.background_workers();
        local_stats.retained_lanes = shape_.retained_lanes;
        local_stats.per_lane_workspace_bytes = shape_.per_lane_workspace_bytes;
        local_stats.retained_workspace_bytes = shape_.retained_workspace_bytes;
        local_stats.productive_lanes = plan.active_lanes;

        if (info.block_count == 0) {
            if (stats != nullptr) {
                *stats = local_stats;
            }
            return info;
        }

        detail::FrameBlockCursor cursor(source, info);
        std::size_t decoded_blocks = 0;
        while (cursor.has_next()) {
            const std::size_t remaining =
                static_cast<std::size_t>(info.block_count) - decoded_blocks;
            const std::size_t batch_size = std::min(plan.active_lanes, remaining);
            local_stats.batches = checked_add(local_stats.batches, 1);
            local_stats.peak_blocks_in_flight = std::max(
                local_stats.peak_blocks_in_flight, batch_size);

            for (std::size_t index = 0; index < batch_size; ++index) {
                batch_descriptors_[index] = cursor.next();
                local_stats.descriptor_reads = checked_add(
                    local_stats.descriptor_reads, 1);
            }

            const bool caller_active =
                activation.caller_participates && batch_size != 0;
            const std::size_t caller_tasks = caller_active ? 1U : 0U;
            const std::size_t background_tasks = batch_size - caller_tasks;
            if (background_tasks > pool_.background_workers()) {
                throw std::logic_error("parallel activation exceeds retained workers");
            }

            const std::size_t notified =
                activation.wake_mode == WakeMode::all_retained
                ? pool_.background_workers() : background_tasks;
            local_stats.background_notifications = checked_add(
                local_stats.background_notifications, notified);
            local_stats.inactive_worker_wakeups = checked_add(
                local_stats.inactive_worker_wakeups,
                notified - background_tasks);

            const std::size_t generation = checked_add(generation_, 1);
            generation_ = generation;
            local_stats.generation = generation;

            std::optional<CodecLaneTask> caller_task;
            if (caller_active) {
                caller_task.emplace(DecodeLaneTask{
                    batch_descriptors_[0], &source.reader});
            }
            const CodecLaneResult caller_result = run_retained_batch(
                pool_, generation, std::move(caller_task), background_tasks,
                notified, background_results_,
                [&](std::size_t worker) -> CodecLaneTask {
                    return DecodeLaneTask{
                        batch_descriptors_[caller_tasks + worker],
                        &source.reader};
                });

            for (std::size_t batch_index = 0;
                 batch_index < batch_size; ++batch_index) {
                const std::span<const std::byte> decoded =
                    caller_active && batch_index == 0
                    ? caller_result.output
                    : background_results_[batch_index - caller_tasks].output;
                if (decoded.size() !=
                    batch_descriptors_[batch_index].original_size) {
                    throw CodecError(
                        BZ3_ERR_MALFORMED_HEADER,
                        "parallel decoded block length disagrees with its descriptor");
                }
                if (!decoded.empty()) {
                    sink(decoded);
                }
            }

            local_stats.caller_blocks = checked_add(
                local_stats.caller_blocks, caller_tasks);
            local_stats.background_blocks = checked_add(
                local_stats.background_blocks, background_tasks);
            decoded_blocks = checked_add(decoded_blocks, batch_size);
        }
        cursor.require_complete();

        if (decoded_blocks != info.block_count ||
            checked_add(local_stats.caller_blocks,
                        local_stats.background_blocks) != info.block_count ||
            local_stats.descriptor_reads != info.block_count) {
            throw std::logic_error("parallel decoder block accounting mismatch");
        }
        if (stats != nullptr) {
            *stats = local_stats;
        }
        return info;
    }

    std::uint32_t block_size_{};
    std::uint32_t decoder_block_size_{};
    ParallelFramePolicy policy_;
    RetainedPoolShape shape_;
    std::vector<CodecLaneResult> background_results_;
    std::vector<detail::BlockDescriptor> batch_descriptors_;
    RetainedLanePool pool_;
    std::mutex call_mutex_;
    std::mutex reader_mutex_;
    std::size_t generation_{};
};

ParallelFrameDecoder::ParallelFrameDecoder(
    std::uint32_t block_size,
    ParallelFramePolicy policy)
    : ParallelFrameDecoder(block_size, block_size, std::move(policy)) {}

ParallelFrameDecoder::ParallelFrameDecoder(
    std::uint32_t block_size,
    std::uint32_t decoder_block_size,
    ParallelFramePolicy policy)
    : impl_(std::make_unique<Impl>(
          block_size, decoder_block_size, std::move(policy))) {}

ParallelFrameDecoder::~ParallelFrameDecoder() = default;

std::uint32_t ParallelFrameDecoder::block_size() const noexcept {
    return impl_ ? impl_->block_size_ : 0;
}

std::uint32_t ParallelFrameDecoder::decoder_block_size() const noexcept {
    return impl_ ? impl_->decoder_block_size_ : 0;
}

std::size_t ParallelFrameDecoder::retained_background_workers() const noexcept {
    return impl_ ? impl_->pool_.background_workers() : 0;
}

std::size_t ParallelFrameDecoder::retained_workspace_bytes() const noexcept {
    return impl_ ? impl_->shape_.retained_workspace_bytes : 0;
}

FrameInfo ParallelFrameDecoder::decode_frame_to(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes,
    ParallelDecodeStats* stats) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from parallel decoder");
    }
    const RangeReader reader = detail::span_reader(encoded);
    return impl_->decode(
        encoded.size(), reader, max_output_size, sink,
        reject_trailing_bytes, stats);
}

FrameInfo ParallelFrameDecoder::decode_frame_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes,
    ParallelDecodeStats* stats) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from parallel decoder");
    }
    return impl_->decode(
        encoded_size, reader, max_output_size, sink,
        reject_trailing_bytes, stats);
}

FrameInfo decompress_frame_parallel_to(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    bool reject_trailing_bytes,
    ParallelDecodeStats* stats) {
    const RangeReader reader = detail::span_reader(encoded);
    return decompress_frame_parallel_from(
        encoded.size(), reader, max_output_size, sink,
        std::move(policy), reject_trailing_bytes, stats);
}

FrameInfo decompress_frame_parallel_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    const FrameSink& sink,
    ParallelFramePolicy policy,
    bool reject_trailing_bytes,
    ParallelDecodeStats* stats) {
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (!sink) {
        throw std::invalid_argument("frame sink must be callable");
    }
    if (policy.activation.retained_background_workers >
        maximum_retained_background_workers) {
        throw std::invalid_argument(
            "retained background worker count exceeds the hard safety limit");
    }

    const detail::FrameSource source{encoded_size, reader};
    const FrameInfo info = detail::scan_frame_source(
        source, max_output_size, reject_trailing_bytes,
        policy.max_workspace_bytes);
    if (info.block_count == 0) {
        ParallelDecodeStats empty_stats;
        empty_stats.activation = make_activation_plan(
            0, info.original_size, policy.activation);
        empty_stats.per_lane_workspace_bytes = 0;
        if (stats != nullptr) {
            *stats = empty_stats;
        }
        return info;
    }

    if (policy.activation.wake_mode == WakeMode::active_only) {
        const ActivationPlan plan = make_activation_plan(
            info.block_count, info.original_size, policy.activation);
        policy.activation.retained_background_workers =
            plan.active_background_workers;
    }

    ParallelFrameDecoder decoder(
        info.block_size, info.decoder_block_size, std::move(policy));
    return decoder.impl_->decode_validated(
        encoded_size, reader, info, sink, stats);
}

} // namespace bzip4
