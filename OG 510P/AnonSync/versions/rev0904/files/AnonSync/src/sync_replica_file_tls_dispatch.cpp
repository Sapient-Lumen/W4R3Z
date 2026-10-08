#include "sync_replica_file_tls_dispatch.hpp"

#include <exception>
#include <memory>
#include <optional>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace anonsync {
namespace {

void validate_frozen_outbound_or_throw(
    const SyncReplicaActor& local_actor,
    const SyncReplicaFileDeliveryProtocolLimits& protocol_limits,
    const SyncReplicaDeliveryChannelContext& channel_context,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label) {
    const SyncReplicaDeliveryRequest expected_evidence_request =
        make_sync_replica_delivery_request_from_claim_or_throw(
            outbound.claim, local_actor, channel_context,
            SyncReplicaValueKind::File, label + " frozen claim");
    if (outbound.request.evidence_request != expected_evidence_request) {
        throw std::invalid_argument(
            label +
            " request evidence differs from its exact claim and channel");
    }

    validate_sync_replica_file_delivery_request_or_throw(
        outbound.request, protocol_limits);
    const std::string canonical_frame =
        encode_sync_replica_file_delivery_request_or_throw(
            outbound.request, protocol_limits);
    if (canonical_frame != outbound.request_frame) {
        throw std::invalid_argument(
            label + " frame is not the canonical encoding of its request");
    }
    const std::string canonical_digest =
        sync_replica_file_delivery_request_digest_or_throw(
            outbound.request, protocol_limits);
    if (canonical_digest != outbound.request_digest) {
        throw std::invalid_argument(
            label + " digest does not bind its canonical request");
    }
}

}  // namespace

class detail::SyncReplicaFileTlsDispatchState final {
public:
    enum class Terminal {
        Writing,
        Complete,
        Failed,
    };

    SyncReplicaFileTlsDispatchState(
        const SyncReplicaOutboundFileDelivery& outbound_value,
        std::string label_value)
        : outbound(outbound_value), label(std::move(label_value)) {}

    SyncReplicaOutboundFileDelivery outbound;
    std::string label;
    std::uint64_t body_bytes_written = 0U;
    Terminal terminal = Terminal::Writing;
};

SyncReplicaFileTlsDispatchContinuation::
    SyncReplicaFileTlsDispatchContinuation(
        std::unique_ptr<detail::SyncReplicaFileTlsDispatchState> state,
        SyncReplicaTlsRecordWriteContinuation transport) noexcept
    : state_(std::move(state)), transport_(std::move(transport)) {}

SyncReplicaFileTlsDispatchContinuation::
    SyncReplicaFileTlsDispatchContinuation(
        SyncReplicaFileTlsDispatchContinuation&& other) noexcept = default;

SyncReplicaFileTlsDispatchContinuation&
SyncReplicaFileTlsDispatchContinuation::operator=(
    SyncReplicaFileTlsDispatchContinuation&& other) noexcept {
    if (this != &other) {
        // Destroying or replacing an active transport continuation must poison
        // its accepted-prefix stream before its exact frozen attempt metadata is
        // released. The nested move assignment owns that no-throw cleanup.
        transport_ = std::move(other.transport_);
        state_ = std::move(other.state_);
    }
    return *this;
}

SyncReplicaFileTlsDispatchContinuation::~SyncReplicaFileTlsDispatchContinuation()
    noexcept = default;

bool SyncReplicaFileTlsDispatchContinuation::active() const noexcept {
    return state_ != nullptr &&
           state_->terminal ==
               detail::SyncReplicaFileTlsDispatchState::Terminal::Writing &&
           transport_.active();
}

bool SyncReplicaFileTlsDispatchContinuation::complete() const noexcept {
    return state_ != nullptr &&
           state_->terminal ==
               detail::SyncReplicaFileTlsDispatchState::Terminal::Complete;
}

std::uint64_t
SyncReplicaFileTlsDispatchContinuation::frame_bytes() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->outbound.request_frame.size());
}

std::uint64_t
SyncReplicaFileTlsDispatchContinuation::body_bytes_written() const noexcept {
    return state_ == nullptr ? 0U : state_->body_bytes_written;
}

const SyncReplicaOutboundFileDelivery&
SyncReplicaFileTlsDispatchContinuation::outbound_or_throw() const {
    if (!state_) {
        throw std::logic_error(
            "sync replica file TLS dispatch continuation is empty or moved-from");
    }
    return state_->outbound;
}

SyncReplicaTlsRecordWriteProgress
SyncReplicaFileTlsDispatchContinuation::advance_or_throw() {
    if (!active()) {
        throw std::logic_error(
            (state_ ? state_->label : "sync replica file TLS dispatch") +
            " continuation is not active");
    }
    try {
        const SyncReplicaTlsRecordWriteProgress progress =
            transport_.advance_or_throw();
        if (progress == SyncReplicaTlsRecordWriteProgress::Complete) {
            state_->body_bytes_written = frame_bytes();
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Complete;
        } else {
            state_->body_bytes_written = transport_.body_bytes_written();
        }
        return progress;
    } catch (...) {
        state_->body_bytes_written = transport_.body_bytes_written();
        if (!transport_.active()) {
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Failed;
        }
        throw;
    }
}

SyncReplicaTlsSocketReadinessTarget
SyncReplicaFileTlsDispatchContinuation::pending_readiness_or_throw() const {
    if (!active()) {
        throw std::logic_error(
            (state_ ? state_->label : "sync replica file TLS dispatch") +
            " continuation is not active");
    }
    try {
        return transport_.pending_readiness_or_throw();
    } catch (...) {
        state_->body_bytes_written = transport_.body_bytes_written();
        // Asking for a readiness target before OpenSSL has returned WANT is
        // caller misuse, not a transport failure. Only an underlying fail-stop
        // that surrendered stream ownership may terminalize this wrapper.
        if (!transport_.active()) {
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Failed;
        }
        throw;
    }
}

SyncReplicaTlsRecordWritePollProgress
SyncReplicaFileTlsDispatchContinuation::poll_and_advance_or_throw(
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
    if (!active()) {
        throw std::logic_error(
            (state_ ? state_->label : "sync replica file TLS dispatch") +
            " continuation is not active");
    }
    try {
        const SyncReplicaTlsRecordWritePollProgress progress =
            poll_and_advance_sync_replica_tls_record_write_or_throw(
                transport_, deadline, label);
        if (progress == SyncReplicaTlsRecordWritePollProgress::Complete) {
            state_->body_bytes_written = frame_bytes();
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Complete;
        } else {
            state_->body_bytes_written = transport_.body_bytes_written();
        }
        return progress;
    } catch (...) {
        state_->body_bytes_written = transport_.body_bytes_written();
        if (!transport_.active()) {
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Failed;
        }
        throw;
    }
}

void SyncReplicaFileTlsDispatchContinuation::finish_or_throw() {
    if (!active()) {
        throw std::logic_error(
            (state_ ? state_->label : "sync replica file TLS dispatch") +
            " continuation is not active");
    }
    try {
        transport_.finish_or_throw();
        state_->body_bytes_written = frame_bytes();
        state_->terminal =
            detail::SyncReplicaFileTlsDispatchState::Terminal::Complete;
    } catch (...) {
        state_->body_bytes_written = transport_.body_bytes_written();
        if (!transport_.active()) {
            state_->terminal =
                detail::SyncReplicaFileTlsDispatchState::Terminal::Failed;
        }
        throw;
    }
}

SyncReplicaFileTlsDispatchContinuation
begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label) {
    // Allocate and copy every outer continuation field before acquiring SQLite
    // or accepting a prefix. After begin_sync_replica_tls_record_write returns,
    // the only handoff is a no-throw move of pre-existing unique ownership.
    std::unique_ptr<detail::SyncReplicaFileTlsDispatchState> dispatch_state;
    std::optional<SyncReplicaDeliveryChannelContext> channel_context;
    try {
        dispatch_state =
            std::make_unique<detail::SyncReplicaFileTlsDispatchState>(
                outbound, label);
        channel_context.emplace(channel.delivery_context());
        service.validate_channel_or_throw(
            channel.delivery_authority(), label + " preflight channel");
        validate_frozen_outbound_or_throw(
            service.local_actor_, service.protocol_limits_, *channel_context,
            dispatch_state->outbound, label + " preflight");
    } catch (...) {
        const SyncReplicaSqliteOutboxClaim& claim = dispatch_state
            ? dispatch_state->outbound.claim
            : outbound.claim;
        service.release_claim_after_pre_dispatch_failure_or_throw(
            claim, std::current_exception(), label + " pre-prefix preflight");
    }

    SyncReplicaSqliteOutboxDispatchGuardResult dispatch_result;
    try {
        dispatch_result =
            service.replica_owner_.guard_outbox_claim_for_dispatch_or_throw(
                dispatch_state->outbound.claim);
    } catch (...) {
        service.release_claim_after_pre_dispatch_failure_or_throw(
            dispatch_state->outbound.claim, std::current_exception(),
            label + " pre-prefix guard acquisition");
    }
    if (dispatch_result.disposition !=
            SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired ||
        dispatch_result.guard == nullptr) {
        service.throw_dispatch_attestation_failure_or_throw(
            dispatch_result.disposition, label + " first-prefix");
    }

    std::unique_ptr<SyncReplicaSqliteOutboxDispatchGuard> dispatch_guard =
        std::move(dispatch_result.guard);
    bool prefix_accepted = false;
    try {
        // The owner guard freezes exact operation/claim authority. Re-prove the
        // live TLS capability inside that serialization frontier and permit only
        // a bounded heartbeat renewal to have changed the row.
        service.validate_channel_or_throw(
            channel.delivery_authority(), label + " guarded channel");
        const SyncReplicaDeliveryRequest current_evidence_request =
            make_sync_replica_delivery_request_from_claim_or_throw(
                dispatch_guard->claim(), service.local_actor_, *channel_context,
                SyncReplicaValueKind::File, label + " guarded claim");
        if (current_evidence_request !=
            dispatch_state->outbound.request.evidence_request) {
            throw std::runtime_error(
                label +
                " guarded claim no longer owns the frozen canonical request");
        }

        static_assert(std::is_nothrow_move_constructible_v<
                      SyncReplicaTlsRecordWriteContinuation>);
        static_assert(std::is_nothrow_move_constructible_v<
                      SyncReplicaFileTlsDispatchContinuation>);
        static_assert(std::is_nothrow_move_assignable_v<
                      SyncReplicaFileTlsDispatchContinuation>);
        SyncReplicaTlsRecordWriteContinuation transport =
            begin_sync_replica_tls_record_write_or_throw(
                channel,
                dispatch_state->outbound.request_frame,
                service.protocol_limits_.max_request_frame_bytes,
                SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                label + " first-prefix");
        // All outer storage already exists. This bit and the final no-throw
        // ownership moves cannot strand an accepted prefix through allocation.
        prefix_accepted = true;

        // Prefix acceptance makes the attempt ambiguous. Commit the exact clock
        // observation and release SQLite before returning body ownership to the
        // event-loop caller. No local write completion settles the outbox.
        dispatch_guard->commit_or_throw();
        dispatch_guard.reset();
        return SyncReplicaFileTlsDispatchContinuation(
            std::move(dispatch_state), std::move(transport));
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        // Rollback must precede any retry release. An unfinished transport
        // continuation poisons the stream during stack unwinding.
        dispatch_guard.reset();
        if (!prefix_accepted) {
            service.release_claim_after_pre_dispatch_failure_or_throw(
                dispatch_state->outbound.claim, original,
                label + " pre-prefix dispatch");
        }
        std::rethrow_exception(original);
    }
}

void dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label) {
    SyncReplicaFileTlsDispatchContinuation continuation =
        begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
            service, channel, outbound, label);
    continuation.finish_or_throw();
}

namespace {

template <typename PayloadSource>
std::optional<SyncReplicaFileTlsDispatchContinuation>
claim_and_begin_from_payload_source_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    PayloadSource&& payload_source,
    const std::string& label) {
    std::optional<SyncReplicaOutboundFileDelivery> outbound =
        service.claim_next_request_or_throw(
            channel.delivery_authority(), std::move(worker_id), lease_seconds,
            std::forward<PayloadSource>(payload_source));
    if (!outbound.has_value()) return std::nullopt;

    static_assert(std::is_nothrow_move_constructible_v<
                  SyncReplicaFileTlsDispatchContinuation>);
    static_assert(std::is_nothrow_constructible_v<
                  std::optional<SyncReplicaFileTlsDispatchContinuation>,
                  SyncReplicaFileTlsDispatchContinuation&&>);
    SyncReplicaFileTlsDispatchContinuation continuation =
        begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
            service, channel, *outbound, label);
    return std::optional<SyncReplicaFileTlsDispatchContinuation>(
        std::move(continuation));
}

template <typename PayloadSource>
std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_from_payload_source_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    PayloadSource&& payload_source,
    const std::string& label) {
    std::optional<SyncReplicaOutboundFileDelivery> outbound =
        service.claim_next_request_or_throw(
            channel.delivery_authority(), std::move(worker_id), lease_seconds,
            std::forward<PayloadSource>(payload_source));
    if (!outbound.has_value()) return std::nullopt;

    dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
        service, channel, *outbound, label);
    return outbound;
}

}  // namespace

std::optional<SyncReplicaFileTlsDispatchContinuation>
claim_and_begin_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot,
    const std::string& label) {
    return claim_and_begin_from_payload_source_or_throw(
        service, channel, std::move(worker_id), lease_seconds,
        std::move(payload_snapshot), label);
}

#if !defined(_WIN32)
std::optional<SyncReplicaFileTlsDispatchContinuation>
claim_and_begin_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    const std::string& label) {
    return claim_and_begin_from_payload_source_or_throw(
        service, channel, std::move(worker_id), lease_seconds,
        payload_snapshot, label);
}
#endif

std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot,
    const std::string& label) {
    return claim_and_dispatch_from_payload_source_or_throw(
        service, channel, std::move(worker_id), lease_seconds,
        std::move(payload_snapshot), label);
}

#if !defined(_WIN32)
std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    const std::string& label) {
    return claim_and_dispatch_from_payload_source_or_throw(
        service, channel, std::move(worker_id), lease_seconds,
        payload_snapshot, label);
}
#endif

}  // namespace anonsync
