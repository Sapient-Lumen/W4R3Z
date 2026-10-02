#include "toxsync/content_scheduler.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <utility>

namespace toxsync {
namespace {

[[nodiscard]] constexpr std::uint64_t saturating_add(
    std::uint64_t left, std::uint64_t right) noexcept {
    return left > std::numeric_limits<std::uint64_t>::max() - right
        ? std::numeric_limits<std::uint64_t>::max()
        : left + right;
}

[[nodiscard]] constexpr std::uint64_t saturating_multiply(
    std::uint64_t left, std::uint64_t right) noexcept {
    if (left == 0U || right == 0U) return 0U;
    return left > std::numeric_limits<std::uint64_t>::max() / right
        ? std::numeric_limits<std::uint64_t>::max()
        : left * right;
}

[[nodiscard]] constexpr std::uint64_t bounded_backoff(
    std::uint64_t base, std::uint64_t maximum, std::uint8_t attempt) noexcept {
    const auto shift = std::min<unsigned>(attempt == 0U ? 0U : attempt - 1U, 20U);
    const auto multiplier = std::uint64_t{1U} << shift;
    return std::min(maximum, saturating_multiply(base, multiplier));
}

} // namespace

class ContentScheduler::Impl final {
public:
    explicit Impl(ContentSchedulerConfig config) : config_(config) {
        if (config_.max_sources == 0U || config_.max_pending_chunks == 0U ||
            config_.max_inflight == 0U ||
            config_.max_inflight_per_source == 0U ||
            config_.max_inflight_per_source > config_.max_inflight ||
            config_.retry_budget == 0U || config_.lease_timeout_ms == 0U ||
            config_.base_backoff_ms == 0U ||
            config_.maximum_backoff_ms < config_.base_backoff_ms ||
            config_.initial_goodput_bytes_per_second == 0U ||
            config_.max_sources >
                static_cast<std::size_t>(std::numeric_limits<std::uint16_t>::max()) ||
            config_.max_inflight >
                static_cast<std::size_t>(std::numeric_limits<std::uint16_t>::max()) ||
            config_.max_pending_chunks >
                static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
            throw std::invalid_argument("invalid content scheduler limits");
        }
        sources_ = std::make_unique<Source[]>(config_.max_sources);
        tasks_ = std::make_unique<Task[]>(config_.max_pending_chunks);
    }

    struct Source {
        bool used{};
        bool online{};
        std::uint32_t id{};
        std::uint16_t inflight{};
        std::uint64_t inflight_bytes{};
        std::uint64_t goodput{};
        std::uint64_t rtt_us{};
        std::uint64_t backoff_until_ms{};
        std::uint64_t completed{};
        std::uint64_t failed{};
    };

    enum class TaskState : std::uint8_t { empty, pending, inflight };

    struct Task {
        TaskState state{TaskState::empty};
        ContentChunkRef chunk{};
        std::uint64_t lease_id{};
        std::uint64_t deadline_ms{};
        std::uint64_t not_before_ms{};
        std::uint32_t source_id{};
        std::uint32_t last_failed_source{};
        std::uint8_t attempts{};
        bool has_last_failed_source{};
        ContentAvailabilityAnswer availability{ContentAvailabilityAnswer::unknown};
    };

    [[nodiscard]] Source* find_source(std::uint32_t id) noexcept {
        for (std::size_t index = 0U; index < config_.max_sources; ++index) {
            if (sources_[index].used && sources_[index].id == id) {
                return &sources_[index];
            }
        }
        return nullptr;
    }

    [[nodiscard]] const Source* find_source(std::uint32_t id) const noexcept {
        for (std::size_t index = 0U; index < config_.max_sources; ++index) {
            if (sources_[index].used && sources_[index].id == id) {
                return &sources_[index];
            }
        }
        return nullptr;
    }

    [[nodiscard]] Task* find_lease(std::uint64_t lease_id) noexcept {
        for (std::size_t index = 0U; index < config_.max_pending_chunks; ++index) {
            auto& task = tasks_[index];
            if (task.state == TaskState::inflight && task.lease_id == lease_id) {
                return &task;
            }
        }
        return nullptr;
    }

    [[nodiscard]] ContentAvailabilityAnswer answer(
        ContentAvailabilityQuery query, void* context,
        std::uint32_t source_id, const Digest256& digest) const noexcept {
        return query == nullptr
            ? ContentAvailabilityAnswer::unknown
            : query(context, source_id, digest);
    }

    [[nodiscard]] bool source_eligible(const Source& source,
                                       std::uint64_t now_ms) const noexcept {
        return source.used && source.online &&
               source.inflight < config_.max_inflight_per_source &&
               now_ms >= source.backoff_until_ms;
    }

    [[nodiscard]] std::uint64_t source_score(
        const Source& source, std::uint32_t bytes,
        ContentAvailabilityAnswer availability) const noexcept {
        const auto goodput = std::max<std::uint64_t>(1U, source.goodput);
        const auto queued = saturating_add(source.inflight_bytes, bytes);
        const auto service_us = saturating_multiply(queued, 1'000'000U) / goodput;
        const auto failure_penalty = saturating_multiply(
            std::min<std::uint64_t>(source.failed, 1024U), 10'000U);
        const auto uncertainty_penalty =
            availability == ContentAvailabilityAnswer::unknown ? 250'000U : 0U;
        return saturating_add(
            saturating_add(service_us, source.rtt_us),
            saturating_add(failure_penalty, uncertainty_penalty));
    }

    void release_source_for(Task& task) noexcept {
        if (auto* source = find_source(task.source_id); source != nullptr) {
            if (source->inflight != 0U) --source->inflight;
            source->inflight_bytes = source->inflight_bytes >= task.chunk.length
                ? source->inflight_bytes - task.chunk.length
                : 0U;
        }
    }

    [[nodiscard]] ContentLeaseUpdate fail_task(
        Task& task, ContentLeaseFailure failure,
        std::uint64_t now_ms, std::uint64_t retry_after_ms) noexcept {
        auto* source = find_source(task.source_id);
        release_source_for(task);
        if (source != nullptr) {
            ++source->failed;
            auto backoff = retry_after_ms;
            if (backoff == 0U) {
                backoff = bounded_backoff(config_.base_backoff_ms,
                                          config_.maximum_backoff_ms,
                                          task.attempts);
            }
            if (failure == ContentLeaseFailure::verification_failed ||
                failure == ContentLeaseFailure::protocol_error) {
                backoff = std::max(backoff, config_.maximum_backoff_ms);
            }
            source->backoff_until_ms =
                saturating_add(now_ms, std::min(backoff,
                                                config_.maximum_backoff_ms));
        }
        task.last_failed_source = task.source_id;
        task.has_last_failed_source = true;
        task.lease_id = 0U;
        task.deadline_ms = 0U;
        task.source_id = 0U;

        const bool terminal = failure == ContentLeaseFailure::cancelled ||
                              task.attempts >= config_.retry_budget;
        if (terminal) {
            task = Task{};
            --stats_.inflight_chunks;
            ++stats_.chunks_terminally_failed;
            return ContentLeaseUpdate::terminal_failure;
        }
        task.state = TaskState::pending;
        task.not_before_ms = saturating_add(
            now_ms, bounded_backoff(config_.base_backoff_ms,
                                    config_.maximum_backoff_ms,
                                    task.attempts));
        --stats_.inflight_chunks;
        ++stats_.pending_chunks;
        ++stats_.retries_scheduled;
        return ContentLeaseUpdate::retry_scheduled;
    }

    ContentSchedulerConfig config_{};
    std::unique_ptr<Source[]> sources_{};
    std::unique_ptr<Task[]> tasks_{};
    std::uint64_t next_lease_id_{1U};
    ContentSchedulerStats stats_{};
};

ContentScheduler::ContentScheduler(const ContentSchedulerConfig& config)
    : impl_(std::make_unique<Impl>(config)) {}

ContentScheduler::~ContentScheduler() = default;
ContentScheduler::ContentScheduler(ContentScheduler&&) noexcept = default;
ContentScheduler& ContentScheduler::operator=(ContentScheduler&&) noexcept = default;

bool ContentScheduler::add_source(std::uint32_t source_id,
                                  std::uint64_t goodput_bytes_per_second,
                                  std::uint64_t round_trip_microseconds) {
    if (auto* existing = impl_->find_source(source_id); existing != nullptr) {
        if (!existing->online) {
            ++impl_->stats_.online_sources;
        }
        existing->online = true;
        if (goodput_bytes_per_second != 0U) {
            existing->goodput = goodput_bytes_per_second;
        }
        existing->rtt_us = round_trip_microseconds;
        return true;
    }
    for (std::size_t index = 0U; index < impl_->config_.max_sources; ++index) {
        auto& source = impl_->sources_[index];
        if (source.used) continue;
        source.used = true;
        source.online = true;
        source.id = source_id;
        source.goodput = goodput_bytes_per_second == 0U
            ? impl_->config_.initial_goodput_bytes_per_second
            : goodput_bytes_per_second;
        source.rtt_us = round_trip_microseconds;
        ++impl_->stats_.sources;
        ++impl_->stats_.online_sources;
        return true;
    }
    return false;
}

bool ContentScheduler::remove_source(std::uint32_t source_id,
                                     std::uint64_t now_ms) noexcept {
    auto* source = impl_->find_source(source_id);
    if (source == nullptr) return false;
    for (std::size_t index = 0U; index < impl_->config_.max_pending_chunks; ++index) {
        auto& task = impl_->tasks_[index];
        if (task.state == Impl::TaskState::inflight &&
            task.source_id == source_id) {
            (void)impl_->fail_task(task, ContentLeaseFailure::unavailable,
                                   now_ms, 0U);
        }
    }
    if (source->online && impl_->stats_.online_sources != 0U) {
        --impl_->stats_.online_sources;
    }
    *source = Impl::Source{};
    if (impl_->stats_.sources != 0U) --impl_->stats_.sources;
    return true;
}

bool ContentScheduler::set_source_online(std::uint32_t source_id,
                                         bool online,
                                         std::uint64_t now_ms) noexcept {
    auto* source = impl_->find_source(source_id);
    if (source == nullptr) return false;
    if (source->online == online) return true;
    source->online = online;
    if (online) {
        ++impl_->stats_.online_sources;
        source->backoff_until_ms = std::min(source->backoff_until_ms, now_ms);
    } else {
        if (impl_->stats_.online_sources != 0U) --impl_->stats_.online_sources;
        for (std::size_t index = 0U; index < impl_->config_.max_pending_chunks; ++index) {
            auto& task = impl_->tasks_[index];
            if (task.state == Impl::TaskState::inflight &&
                task.source_id == source_id) {
                (void)impl_->fail_task(task, ContentLeaseFailure::unavailable,
                                       now_ms, 0U);
            }
        }
    }
    return true;
}

bool ContentScheduler::update_source_hint(
    std::uint32_t source_id,
    std::uint64_t goodput_bytes_per_second,
    std::uint64_t round_trip_microseconds) noexcept {
    auto* source = impl_->find_source(source_id);
    if (source == nullptr || goodput_bytes_per_second == 0U) return false;
    source->goodput = goodput_bytes_per_second;
    source->rtt_us = round_trip_microseconds;
    return true;
}

bool ContentScheduler::enqueue(const ContentChunkRef& chunk) noexcept {
    if (chunk.length == 0U) return false;
    Impl::Task* empty = nullptr;
    for (std::size_t index = 0U; index < impl_->config_.max_pending_chunks; ++index) {
        auto& task = impl_->tasks_[index];
        if (task.state == Impl::TaskState::empty) {
            if (empty == nullptr) empty = &task;
        } else if (task.chunk.digest == chunk.digest) {
            ++impl_->stats_.duplicate_chunks;
            return true;
        }
    }
    if (empty == nullptr) {
        ++impl_->stats_.queue_full_events;
        return false;
    }
    empty->state = Impl::TaskState::pending;
    empty->chunk = chunk;
    ++impl_->stats_.pending_chunks;
    ++impl_->stats_.chunks_enqueued;
    return true;
}

std::optional<ContentChunkLease> ContentScheduler::next(
    std::uint64_t now_ms,
    ContentAvailabilityQuery availability,
    void* availability_context) noexcept {
    if (impl_->stats_.inflight_chunks >= impl_->config_.max_inflight) {
        return std::nullopt;
    }

    Impl::Task* selected_task = nullptr;
    Impl::Source* selected_source = nullptr;
    ContentAvailabilityAnswer selected_answer =
        ContentAvailabilityAnswer::unknown;
    std::size_t selected_rarity = std::numeric_limits<std::size_t>::max();
    std::uint64_t selected_source_score =
        std::numeric_limits<std::uint64_t>::max();

    for (std::size_t task_index = 0U;
         task_index < impl_->config_.max_pending_chunks; ++task_index) {
        auto& task = impl_->tasks_[task_index];
        if (task.state != Impl::TaskState::pending ||
            now_ms < task.not_before_ms) {
            continue;
        }

        std::size_t rarity{};
        Impl::Source* task_source = nullptr;
        ContentAvailabilityAnswer task_answer =
            ContentAvailabilityAnswer::unknown;
        std::uint64_t task_source_score =
            std::numeric_limits<std::uint64_t>::max();
        bool alternative_to_last_failure{};

        for (std::size_t source_index = 0U;
             source_index < impl_->config_.max_sources; ++source_index) {
            auto& source = impl_->sources_[source_index];
            if (!impl_->source_eligible(source, now_ms)) continue;
            const auto answer = impl_->answer(
                availability, availability_context, source.id, task.chunk.digest);
            if (answer == ContentAvailabilityAnswer::definitely_missing) continue;
            ++rarity;
            const bool is_alternative = !task.has_last_failed_source ||
                                        source.id != task.last_failed_source;
            const auto score = impl_->source_score(source, task.chunk.length, answer);
            if (task_source == nullptr ||
                (is_alternative && !alternative_to_last_failure) ||
                (is_alternative == alternative_to_last_failure &&
                 (answer < task_answer ||
                  (answer == task_answer && score < task_source_score)))) {
                task_source = &source;
                task_answer = answer;
                task_source_score = score;
                alternative_to_last_failure = is_alternative;
            }
        }
        if (task_source == nullptr) continue;

        const bool choose = selected_task == nullptr ||
                            rarity < selected_rarity ||
                            (rarity == selected_rarity &&
                             (task.attempts > selected_task->attempts ||
                              (task.attempts == selected_task->attempts &&
                               (task_source_score < selected_source_score ||
                                (task_source_score == selected_source_score &&
                                 task.chunk.length > selected_task->chunk.length)))));
        if (choose) {
            selected_task = &task;
            selected_source = task_source;
            selected_answer = task_answer;
            selected_rarity = rarity;
            selected_source_score = task_source_score;
        }
    }

    if (selected_task == nullptr || selected_source == nullptr) {
        return std::nullopt;
    }
    auto lease_id = impl_->next_lease_id_++;
    if (lease_id == 0U) lease_id = impl_->next_lease_id_++;
    selected_task->state = Impl::TaskState::inflight;
    selected_task->lease_id = lease_id;
    selected_task->source_id = selected_source->id;
    selected_task->deadline_ms =
        saturating_add(now_ms, impl_->config_.lease_timeout_ms);
    selected_task->availability = selected_answer;
    ++selected_task->attempts;
    ++selected_source->inflight;
    selected_source->inflight_bytes = saturating_add(
        selected_source->inflight_bytes, selected_task->chunk.length);
    --impl_->stats_.pending_chunks;
    ++impl_->stats_.inflight_chunks;
    ++impl_->stats_.leases_issued;

    return ContentChunkLease{
        .lease_id = lease_id,
        .source_id = selected_source->id,
        .chunk = selected_task->chunk,
        .deadline_ms = selected_task->deadline_ms,
        .attempt = selected_task->attempts,
        .availability = selected_answer,
    };
}

ContentLeaseUpdate ContentScheduler::complete(
    std::uint64_t lease_id,
    std::uint64_t bytes_received,
    std::uint64_t elapsed_microseconds,
    std::uint64_t now_ms,
    bool digest_verified) noexcept {
    auto* task = impl_->find_lease(lease_id);
    if (task == nullptr) {
        ++impl_->stats_.late_results;
        return ContentLeaseUpdate::late_or_unknown;
    }
    if (!digest_verified || bytes_received != task->chunk.length) {
        return impl_->fail_task(
            *task,
            digest_verified ? ContentLeaseFailure::protocol_error
                            : ContentLeaseFailure::verification_failed,
            now_ms, 0U);
    }
    auto* source = impl_->find_source(task->source_id);
    impl_->release_source_for(*task);
    if (source != nullptr) {
        ++source->completed;
        if (elapsed_microseconds != 0U) {
            const auto sample = saturating_multiply(bytes_received, 1'000'000U) /
                                elapsed_microseconds;
            source->goodput = source->completed == 1U
                ? std::max<std::uint64_t>(1U, sample)
                : saturating_add(saturating_multiply(source->goodput, 7U),
                                 sample) / 8U;
            source->backoff_until_ms = std::min(source->backoff_until_ms, now_ms);
        }
    }
    *task = Impl::Task{};
    --impl_->stats_.inflight_chunks;
    ++impl_->stats_.chunks_completed;
    impl_->stats_.completed_bytes = saturating_add(
        impl_->stats_.completed_bytes, bytes_received);
    return ContentLeaseUpdate::completed;
}

ContentLeaseUpdate ContentScheduler::fail(
    std::uint64_t lease_id,
    ContentLeaseFailure failure,
    std::uint64_t now_ms,
    std::uint64_t retry_after_ms) noexcept {
    auto* task = impl_->find_lease(lease_id);
    if (task == nullptr) {
        ++impl_->stats_.late_results;
        return ContentLeaseUpdate::late_or_unknown;
    }
    return impl_->fail_task(*task, failure, now_ms, retry_after_ms);
}

std::size_t ContentScheduler::expire(std::uint64_t now_ms) noexcept {
    std::size_t expired{};
    for (std::size_t index = 0U;
         index < impl_->config_.max_pending_chunks; ++index) {
        auto& task = impl_->tasks_[index];
        if (task.state == Impl::TaskState::inflight &&
            now_ms >= task.deadline_ms) {
            (void)impl_->fail_task(task, ContentLeaseFailure::timeout,
                                   now_ms, 0U);
            ++impl_->stats_.leases_timed_out;
            ++expired;
        }
    }
    return expired;
}

void ContentScheduler::cancel_all(std::uint64_t now_ms) noexcept {
    for (std::size_t index = 0U;
         index < impl_->config_.max_pending_chunks; ++index) {
        auto& task = impl_->tasks_[index];
        if (task.state == Impl::TaskState::inflight) {
            (void)impl_->fail_task(task, ContentLeaseFailure::cancelled,
                                   now_ms, 0U);
        } else if (task.state == Impl::TaskState::pending) {
            task = Impl::Task{};
            --impl_->stats_.pending_chunks;
            ++impl_->stats_.chunks_terminally_failed;
        }
    }
}

bool ContentScheduler::empty() const noexcept {
    return impl_->stats_.pending_chunks == 0U &&
           impl_->stats_.inflight_chunks == 0U;
}

bool ContentScheduler::has_capacity() const noexcept {
    return impl_->stats_.pending_chunks + impl_->stats_.inflight_chunks <
           impl_->config_.max_pending_chunks;
}

ContentSchedulerStats ContentScheduler::stats() const noexcept {
    return impl_->stats_;
}

std::optional<ContentSourceSnapshot> ContentScheduler::source(
    std::uint32_t source_id) const noexcept {
    const auto* source = impl_->find_source(source_id);
    if (source == nullptr) return std::nullopt;
    return ContentSourceSnapshot{
        .source_id = source->id,
        .online = source->online,
        .inflight = source->inflight,
        .inflight_bytes = source->inflight_bytes,
        .goodput_bytes_per_second = source->goodput,
        .round_trip_microseconds = source->rtt_us,
        .backoff_until_ms = source->backoff_until_ms,
        .completed_chunks = source->completed,
        .failed_chunks = source->failed,
    };
}

std::size_t ContentScheduler::resident_bytes() const noexcept {
    return sizeof(Impl) +
           impl_->config_.max_sources * sizeof(Impl::Source) +
           impl_->config_.max_pending_chunks * sizeof(Impl::Task);
}

} // namespace toxsync
