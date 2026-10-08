#include "sync_replica_i2p_ingress_worker.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <limits>
#include <mutex>
#include <stdexcept>
#include <stop_token>
#include <thread>
#include <utility>

namespace anonsync {
namespace {

using Clock = std::chrono::steady_clock;
using Milliseconds = std::chrono::milliseconds;

constexpr std::uint64_t kWorkerAcceptPollMilliseconds = 100U;
constexpr std::uint64_t kMaximumSetupTimeoutSeconds = 3600U;
constexpr std::uint64_t kMaximumRetryMilliseconds = 3600000U;

[[nodiscard]] Clock::time_point add_milliseconds_or_throw(
    Clock::time_point base,
    std::uint64_t amount,
    const std::string& label) {
    if (amount > static_cast<std::uint64_t>(
                     std::numeric_limits<Milliseconds::rep>::max())) {
        throw std::overflow_error(label + " duration overflows");
    }
    const Milliseconds duration(
        static_cast<Milliseconds::rep>(amount));
    if (duration.count() > 0 &&
        base > Clock::time_point::max() - duration) {
        throw std::overflow_error(label + " deadline overflows");
    }
    return base + duration;
}

[[nodiscard]] std::uint64_t retry_delay_milliseconds(
    std::uint64_t initial,
    std::uint64_t maximum,
    std::uint64_t consecutive_failures) noexcept {
    if (consecutive_failures == 0U) return 0U;
    std::uint64_t value = initial;
    for (std::uint64_t index = 1U;
         index < consecutive_failures && value < maximum;
         ++index) {
        if (value > maximum / 2U) {
            value = maximum;
        } else {
            value *= 2U;
        }
    }
    return std::min(value, maximum);
}

[[nodiscard]] std::string report_diagnostic(
    const SyncReplicaStreamConnectReport& report) {
    return "SAM ingress ended at " +
        std::string(sync_replica_stream_route_stage_name(
            report.terminal_stage)) +
        " with " +
        std::string(sync_replica_stream_connect_disposition_name(
            report.disposition));
}

}  // namespace

struct SyncReplicaI2pIngressWorker::State final {
    SyncReplicaI2pSamAcceptRoute route;
    std::uint64_t setup_timeout_seconds = 0U;
    std::uint64_t retry_initial_milliseconds = 0U;
    std::uint64_t retry_maximum_milliseconds = 0U;
    std::string label;

    mutable std::mutex mutex;
    std::condition_variable condition;
    SyncReplicaI2pIngressWorkerSnapshot snapshot;
    std::optional<SyncReplicaConnectedStream> pending_stream;
    std::optional<SyncReplicaStreamConnectReport> pending_report;

    // Declared last so destruction requests stop and joins before any state the
    // worker can observe is destroyed.
    std::jthread worker;

    State(
        SyncReplicaI2pSamAcceptRoute selected_route,
        std::uint64_t selected_setup_timeout_seconds,
        std::uint64_t selected_retry_initial_milliseconds,
        std::uint64_t selected_retry_maximum_milliseconds,
        std::string owner_label)
        : route(std::move(selected_route)),
          setup_timeout_seconds(selected_setup_timeout_seconds),
          retry_initial_milliseconds(selected_retry_initial_milliseconds),
          retry_maximum_milliseconds(selected_retry_maximum_milliseconds),
          label(std::move(owner_label)),
          worker([this](std::stop_token cancellation) noexcept {
              run(cancellation);
          }) {}

    ~State() noexcept {
        worker.request_stop();
        condition.notify_all();
    }

    [[nodiscard]] bool wait_until_or_stop(
        std::stop_token cancellation,
        Clock::time_point deadline) {
        std::unique_lock lock(mutex);
        while (!cancellation.stop_requested() && Clock::now() < deadline) {
            const Clock::time_point poll_deadline = std::min(
                deadline,
                add_milliseconds_or_throw(
                    Clock::now(), kWorkerAcceptPollMilliseconds,
                    label + " cancellation poll"));
            condition.wait_until(lock, poll_deadline);
        }
        return !cancellation.stop_requested();
    }

    void begin_setup() {
        std::lock_guard lock(mutex);
        snapshot.setup_in_progress = true;
        snapshot.ready = false;
        snapshot.retry_at = Clock::time_point::min();
        if (snapshot.setup_attempts !=
            std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.setup_attempts;
        }
        condition.notify_all();
    }

    void schedule_retry_locked(Clock::time_point now) {
        if (snapshot.consecutive_failures !=
            std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.consecutive_failures;
        }
        snapshot.retry_at = add_milliseconds_or_throw(
            now,
            retry_delay_milliseconds(
                retry_initial_milliseconds,
                retry_maximum_milliseconds,
                snapshot.consecutive_failures),
            label + " retry");
    }

    void publish_event_locked(
        SyncReplicaI2pIngressWorkerEvent event,
        std::optional<SyncReplicaStreamConnectReport> report,
        std::optional<std::string> diagnostic) {
        if (snapshot.event_generation !=
            std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.event_generation;
        }
        snapshot.event = event;
        snapshot.report = std::move(report);
        snapshot.diagnostic = std::move(diagnostic);
    }

    void publish_connected(SyncReplicaStreamConnectReport report) {
        std::lock_guard lock(mutex);
        snapshot.setup_in_progress = false;
        snapshot.ready = true;
        snapshot.retry_at = Clock::time_point::min();
        snapshot.consecutive_failures = 0U;
        if (snapshot.setup_successes !=
            std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.setup_successes;
        }
        publish_event_locked(
            SyncReplicaI2pIngressWorkerEvent::PublicationConnected,
            std::move(report), std::nullopt);
        condition.notify_all();
    }

    void publish_unavailable(
        std::optional<SyncReplicaStreamConnectReport> report,
        std::optional<std::string> diagnostic) {
        std::lock_guard lock(mutex);
        snapshot.setup_in_progress = false;
        snapshot.ready = false;
        if (snapshot.setup_failures !=
            std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.setup_failures;
        }
        schedule_retry_locked(Clock::now());
        publish_event_locked(
            SyncReplicaI2pIngressWorkerEvent::PublicationUnavailable,
            std::move(report), std::move(diagnostic));
        condition.notify_all();
    }

    void publish_lost(
        std::optional<SyncReplicaStreamConnectReport> report,
        std::optional<std::string> diagnostic) {
        std::lock_guard lock(mutex);
        snapshot.setup_in_progress = false;
        snapshot.ready = false;
        if (snapshot.losses != std::numeric_limits<std::uint64_t>::max()) {
            ++snapshot.losses;
        }
        schedule_retry_locked(Clock::now());
        publish_event_locked(
            SyncReplicaI2pIngressWorkerEvent::PublicationLost,
            std::move(report), std::move(diagnostic));
        condition.notify_all();
    }

    [[nodiscard]] bool stream_pending() const {
        std::lock_guard lock(mutex);
        return pending_stream.has_value();
    }

    void store_stream_or_throw(SyncReplicaI2pSamAcceptOutcome outcome) {
        if (!outcome.stream.has_value()) {
            throw std::logic_error(
                label + " accepted I2P route omitted its stream");
        }
        std::lock_guard lock(mutex);
        if (pending_stream.has_value()) {
            throw std::logic_error(
                label + " exceeded its one-stream handoff bound");
        }
        pending_stream.emplace(std::move(*outcome.stream));
        pending_report.emplace(std::move(outcome.report));
        snapshot.stream_pending = true;
        condition.notify_all();
    }

    void wait_for_stream_handoff_or_loss(
        SyncReplicaI2pSamAcceptor& acceptor,
        std::stop_token cancellation) {
        while (!cancellation.stop_requested() && stream_pending()) {
            const Clock::time_point deadline = add_milliseconds_or_throw(
                Clock::now(), kWorkerAcceptPollMilliseconds,
                label + " pending-stream poll");
            {
                std::unique_lock lock(mutex);
                condition.wait_until(lock, deadline, [&] {
                    return cancellation.stop_requested() ||
                        !pending_stream.has_value();
                });
            }
            if (cancellation.stop_requested() || !stream_pending()) return;
            acceptor.require_active_or_throw(
                label + " retained SAM session while stream is pending");
        }
    }

    void run_session_or_throw(
        SyncReplicaI2pSamAcceptor& acceptor,
        std::stop_token cancellation) {
        while (!cancellation.stop_requested()) {
            if (stream_pending()) {
                wait_for_stream_handoff_or_loss(acceptor, cancellation);
                continue;
            }
            const Clock::time_point started_at = Clock::now();
            const Clock::time_point setup_deadline =
                add_milliseconds_or_throw(
                    started_at, setup_timeout_seconds * 1000U,
                    label + " STREAM ACCEPT setup");
            const Clock::time_point peer_deadline =
                add_milliseconds_or_throw(
                    started_at, kWorkerAcceptPollMilliseconds,
                    label + " remote destination poll");
            SyncReplicaI2pSamAcceptOutcome outcome =
                acceptor.accept_until_or_throw(
                    setup_deadline, peer_deadline, cancellation);
            if (outcome.report.disposition ==
                    SyncReplicaStreamConnectDisposition::Cancelled ||
                cancellation.stop_requested()) {
                return;
            }
            if (outcome.report.disposition ==
                SyncReplicaStreamConnectDisposition::DeadlineExpired) {
                continue;
            }
            if (outcome.report.disposition !=
                SyncReplicaStreamConnectDisposition::Connected) {
                publish_lost(
                    outcome.report, report_diagnostic(outcome.report));
                return;
            }
            store_stream_or_throw(std::move(outcome));
        }
    }

    void run(std::stop_token cancellation) noexcept {
        while (!cancellation.stop_requested()) {
            try {
                const SyncReplicaI2pIngressWorkerSnapshot before = current();
                if (before.retry_at != Clock::time_point::min() &&
                    Clock::now() < before.retry_at &&
                    !wait_until_or_stop(cancellation, before.retry_at)) {
                    break;
                }
                if (cancellation.stop_requested()) break;

                begin_setup();
                SyncReplicaI2pSamAcceptor acceptor(
                    route, label + " SAM acceptor");
                SyncReplicaStreamConnectReport report =
                    acceptor.start_until_or_throw(
                        add_milliseconds_or_throw(
                            Clock::now(), setup_timeout_seconds * 1000U,
                            label + " setup"),
                        cancellation);
                if (report.disposition ==
                        SyncReplicaStreamConnectDisposition::Cancelled ||
                    cancellation.stop_requested()) {
                    break;
                }
                if (report.disposition !=
                    SyncReplicaStreamConnectDisposition::Connected) {
                    publish_unavailable(
                        report, report_diagnostic(report));
                    continue;
                }
                publish_connected(report);
                run_session_or_throw(acceptor, cancellation);
            } catch (const std::exception& error) {
                if (cancellation.stop_requested()) break;
                const bool was_ready = current().ready;
                if (was_ready) {
                    publish_lost(std::nullopt, error.what());
                } else {
                    publish_unavailable(std::nullopt, error.what());
                }
            } catch (...) {
                if (cancellation.stop_requested()) break;
                const bool was_ready = current().ready;
                if (was_ready) {
                    publish_lost(
                        std::nullopt,
                        label + " caught an unknown SAM ingress failure");
                } else {
                    publish_unavailable(
                        std::nullopt,
                        label + " caught an unknown SAM setup failure");
                }
            }
        }

        std::lock_guard lock(mutex);
        snapshot.ready = false;
        snapshot.setup_in_progress = false;
        condition.notify_all();
    }

    [[nodiscard]] SyncReplicaI2pIngressWorkerSnapshot current() const {
        std::lock_guard lock(mutex);
        SyncReplicaI2pIngressWorkerSnapshot value = snapshot;
        value.stream_pending = pending_stream.has_value();
        return value;
    }
};

SyncReplicaI2pIngressWorker::SyncReplicaI2pIngressWorker(
    SyncReplicaI2pSamAcceptRoute route,
    std::uint64_t setup_timeout_seconds,
    std::uint64_t retry_initial_milliseconds,
    std::uint64_t retry_maximum_milliseconds,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P ingress worker label must not be empty");
    }
    validate_sync_replica_i2p_sam_accept_route_or_throw(
        route, label + " route");
    if (setup_timeout_seconds == 0U ||
        setup_timeout_seconds > kMaximumSetupTimeoutSeconds) {
        throw std::invalid_argument(
            label + " setup timeout must be in [1, 3600] seconds");
    }
    if (retry_initial_milliseconds == 0U ||
        retry_initial_milliseconds > kMaximumRetryMilliseconds) {
        throw std::invalid_argument(
            label + " initial retry must be in [1, 3600000] milliseconds");
    }
    if (retry_maximum_milliseconds < retry_initial_milliseconds ||
        retry_maximum_milliseconds > kMaximumRetryMilliseconds) {
        throw std::invalid_argument(
            label + " maximum retry must be in [initial, 3600000] milliseconds");
    }
    state_ = std::make_unique<State>(
        std::move(route), setup_timeout_seconds,
        retry_initial_milliseconds, retry_maximum_milliseconds,
        std::move(label));
}

SyncReplicaI2pIngressWorker::~SyncReplicaI2pIngressWorker() noexcept = default;

SyncReplicaI2pIngressWorkerSnapshot
SyncReplicaI2pIngressWorker::snapshot() const {
    if (!state_) {
        throw std::logic_error(
            "sync replica I2P ingress worker is inactive");
    }
    return state_->current();
}

SyncReplicaI2pIngressStreamHandoff
SyncReplicaI2pIngressWorker::take_stream_until_or_throw(
    Clock::time_point deadline,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica I2P ingress handoff label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(label + " worker is inactive");
    }

    SyncReplicaI2pIngressStreamHandoff handoff;
    std::unique_lock lock(state_->mutex);
    state_->condition.wait_until(lock, deadline, [&] {
        return state_->pending_stream.has_value() ||
            !state_->snapshot.ready;
    });
    if (!state_->pending_stream.has_value()) return handoff;
    handoff.stream.emplace(std::move(*state_->pending_stream));
    state_->pending_stream.reset();
    if (state_->pending_report.has_value()) {
        handoff.report.emplace(std::move(*state_->pending_report));
        state_->pending_report.reset();
    }
    state_->snapshot.stream_pending = false;
    lock.unlock();
    state_->condition.notify_all();
    return handoff;
}

}  // namespace anonsync

#endif
