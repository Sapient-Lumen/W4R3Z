#pragma once

#if !defined(_WIN32)

#include "sync_replica_stream_connector.hpp"

#include <chrono>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

// Route-only transitions produced by the native I2P ingress worker. These are
// observations for the single service owner; they never authorize folder,
// SQLite, TLS-membership, or scheduling effects on the worker thread.
enum class SyncReplicaI2pIngressWorkerEvent : std::uint8_t {
    None = 0U,
    PublicationConnected = 1U,
    PublicationUnavailable = 2U,
    PublicationLost = 3U,
};

struct SyncReplicaI2pIngressWorkerSnapshot final {
    std::uint64_t event_generation = 0U;
    SyncReplicaI2pIngressWorkerEvent event =
        SyncReplicaI2pIngressWorkerEvent::None;
    bool ready = false;
    bool setup_in_progress = false;
    bool stream_pending = false;
    std::chrono::steady_clock::time_point retry_at =
        std::chrono::steady_clock::time_point::min();
    std::uint64_t consecutive_failures = 0U;
    std::uint64_t setup_attempts = 0U;
    std::uint64_t setup_successes = 0U;
    std::uint64_t setup_failures = 0U;
    std::uint64_t losses = 0U;
    std::optional<SyncReplicaStreamConnectReport> report;
    std::optional<std::string> diagnostic;

    bool operator==(
        const SyncReplicaI2pIngressWorkerSnapshot&) const = default;
};

struct SyncReplicaI2pIngressStreamHandoff final {
    std::optional<SyncReplicaConnectedStream> stream;
    std::optional<SyncReplicaStreamConnectReport> report;

    SyncReplicaI2pIngressStreamHandoff() = default;
    SyncReplicaI2pIngressStreamHandoff(
        const SyncReplicaI2pIngressStreamHandoff&) = delete;
    SyncReplicaI2pIngressStreamHandoff& operator=(
        const SyncReplicaI2pIngressStreamHandoff&) = delete;
    SyncReplicaI2pIngressStreamHandoff(
        SyncReplicaI2pIngressStreamHandoff&&) noexcept = default;
    SyncReplicaI2pIngressStreamHandoff& operator=(
        SyncReplicaI2pIngressStreamHandoff&&) noexcept = default;
};

// Native I2P publication and accept owner isolated from the sync execution
// thread. The worker may create and retain SAM sockets and one accepted stream;
// it receives no folder, database, TLS context, membership, or application
// capability. A long SESSION CREATE therefore cannot freeze local scanning,
// outbound reconciliation, status publication, or service shutdown. At most one
// accepted stream is buffered while the service owner is busy.
class SyncReplicaI2pIngressWorker final {
public:
    SyncReplicaI2pIngressWorker(
        SyncReplicaI2pSamAcceptRoute route,
        std::uint64_t setup_timeout_seconds,
        std::uint64_t retry_initial_milliseconds,
        std::uint64_t retry_maximum_milliseconds,
        std::string label = "sync replica I2P ingress worker");
    ~SyncReplicaI2pIngressWorker() noexcept;

    SyncReplicaI2pIngressWorker(
        const SyncReplicaI2pIngressWorker&) = delete;
    SyncReplicaI2pIngressWorker& operator=(
        const SyncReplicaI2pIngressWorker&) = delete;
    SyncReplicaI2pIngressWorker(
        SyncReplicaI2pIngressWorker&&) = delete;
    SyncReplicaI2pIngressWorker& operator=(
        SyncReplicaI2pIngressWorker&&) = delete;

    [[nodiscard]] SyncReplicaI2pIngressWorkerSnapshot snapshot() const;

    // Waits only until the caller's absolute deadline. A returned stream is the
    // exact bridge-owned application socket after the SAM peer-destination line
    // has been consumed. Moving it out wakes the worker so it can arm the next
    // accept while the service owner performs TLS/application work.
    [[nodiscard]] SyncReplicaI2pIngressStreamHandoff
    take_stream_until_or_throw(
        std::chrono::steady_clock::time_point deadline,
        std::string_view label = "sync replica I2P ingress handoff");

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
