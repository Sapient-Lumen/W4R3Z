#include "sha256_digest.hpp"
#include "sync_replica_delivery_service.hpp"
#include "sync_replica_delivery_test_channel.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>

#ifdef __linux__
#include <unistd.h>
#endif

namespace {

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

struct TempDatabasePath final {
    std::filesystem::path path;

    explicit TempDatabasePath(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __linux__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        path = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick) + ".sqlite3");
    }

    ~TempDatabasePath() {
        std::error_code ignored;
        std::filesystem::remove(path, ignored);
        std::filesystem::remove(path.string() + "-wal", ignored);
        std::filesystem::remove(path.string() + "-shm", ignored);
        std::filesystem::remove(path.string() + "-journal", ignored);
    }
};

anonsync::SyncSqliteDb open_database(const std::filesystem::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "replica delivery service test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "replica delivery service test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "replica delivery service test durability profile");
    return owner;
}

struct MutableClockState final {
    std::uint64_t epoch = 100U;
};

class MutableClockSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    explicit MutableClockSource(std::shared_ptr<MutableClockState> state)
        : state_(std::move(state)) {}

    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string&) override {
        if (state_->epoch == 0U ||
            state_->epoch > std::numeric_limits<std::uint64_t>::max() /
                                anonsync::kSyncReplicaNanosecondsPerSecond) {
            throw std::runtime_error(
                "replica delivery service test clock epoch is invalid");
        }
        const std::uint64_t nanoseconds =
            state_->epoch * anonsync::kSyncReplicaNanosecondsPerSecond;
        return {
            "test-delivery-clock-v1",
            "01234567-89ab-cdef-0123-456789abcdef",
            std::string(64U, 'c'),
            nanoseconds,
            nanoseconds,
            1U,
            anonsync::SyncReplicaOutboxClockSynchronization::Synchronized,
        };
    }

private:
    std::shared_ptr<MutableClockState> state_;
};

std::unique_ptr<anonsync::SyncReplicaOutboxClockSource> make_clock(
    const std::shared_ptr<MutableClockState>& state) {
    return std::make_unique<MutableClockSource>(state);
}

anonsync::SyncReplicaSqliteOwnerLimits owner_limits(
    std::uint64_t max_operations) {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = max_operations;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_outbox_intents = 64U;
    value.max_outbox_destination_bytes = 4096U;
    return value;
}

anonsync::SyncReplicaDeliveryServiceLimits service_limits() {
    anonsync::SyncReplicaDeliveryServiceLimits value;
    value.wire_operation_limits = owner_limits(64U).model;
    value.max_request_frame_bytes = 512U * 1024U;
    value.max_receipt_frame_bytes = 16U * 1024U;
    return value;
}

using DeliveryAuthority = anonsync::SyncReplicaDeliveryChannelAuthority;

static_assert(!std::is_default_constructible_v<DeliveryAuthority>);
static_assert(!std::is_copy_constructible_v<DeliveryAuthority>);
static_assert(!std::is_copy_assignable_v<DeliveryAuthority>);
static_assert(std::is_nothrow_move_constructible_v<DeliveryAuthority>);
static_assert(std::is_nothrow_move_assignable_v<DeliveryAuthority>);
static_assert(!std::is_constructible_v<
              DeliveryAuthority,
              anonsync::SyncReplicaDeliveryChannelContext>);

DeliveryAuthority sender_channel(
    const anonsync::SyncReplicaActor& receiver,
    std::string_view transcript) {
    return anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
        receiver, transcript);
}

DeliveryAuthority receiver_channel(
    const anonsync::SyncReplicaActor& sender,
    std::string_view transcript) {
    return anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
        sender, transcript);
}

void test_channel_bound_end_to_end_and_capacity_retry() {
    TempDatabasePath sender_file("anonsync-delivery-service-sender");
    TempDatabasePath receiver_file("anonsync-delivery-service-receiver");
    const std::string folder = "folder-delivery-service-capacity";
    const anonsync::SyncReplicaActor sender_actor{
        "device-delivery-service-sender", 8101U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-delivery-service-receiver", 8102U};
    const auto clock_state = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(sender_file.path);
    anonsync::SyncSqliteDb receiver_db = open_database(receiver_file.path);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(8U),
        "delivery service sender", make_clock(clock_state));
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_db.db, folder, receiver_actor, owner_limits(2U),
        "delivery service receiver", make_clock(clock_state));
    anonsync::SyncReplicaDeliveryService sender_service(
        sender, service_limits(), "delivery sender service");
    anonsync::SyncReplicaDeliveryService receiver_service(
        receiver, service_limits(), "delivery receiver service");
    const auto sender_link = sender_channel(receiver_actor, "session-alpha");
    const auto receiver_link = receiver_channel(sender_actor, "session-alpha");

    const std::vector<std::string> destination{receiver_actor.device_id};
    const anonsync::SyncReplicaOperation first =
        sender.create_local_file_or_throw(
            "delivery/first.bin", 5U, anonsync::sha256_hex("first"),
            destination);
    clock_state->epoch = 200U;
    const auto first_outbound = sender_service.claim_next_request_or_throw(
        sender_link, "delivery-worker", 10U);
    require(first_outbound.has_value() &&
                first_outbound->request.operation == first &&
                first_outbound->request.receiver_actor == receiver_actor,
            "service did not bind the first durable claim to the receiver epoch");

    const anonsync::SyncReplicaSqliteSnapshot receiver_empty =
        receiver.snapshot_or_throw();
    anonsync::SyncReplicaActor wrong_sender_actor = sender_actor;
    wrong_sender_actor.epoch += 1U;
    const auto wrong_peer =
        receiver_channel(wrong_sender_actor, "session-alpha");
    require_error(
        [&] {
            (void)receiver_service.receive_request_or_throw(
                wrong_peer, first_outbound->request_frame);
        },
        "does not bind",
        "request crossed an unauthenticated sender epoch");
    require(receiver.snapshot_or_throw() == receiver_empty,
            "peer-epoch rejection mutated receiver evidence");

    std::string tampered_request = first_outbound->request_frame;
    tampered_request[tampered_request.size() / 2U] ^= 0x01;
    require_error(
        [&] {
            (void)receiver_service.receive_request_or_throw(
                receiver_link, tampered_request);
        },
        "digest mismatch",
        "tampered request reached receiver admission");
    require(receiver.snapshot_or_throw() == receiver_empty,
            "tampered request mutated receiver evidence");

    const auto first_inbound = receiver_service.receive_request_or_throw(
        receiver_link, first_outbound->request_frame);
    const anonsync::SyncReplicaSqliteSnapshot first_received =
        receiver.snapshot_or_throw();
    require(first_inbound.admission ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
                first_inbound.receipt.evidence_state ==
                    anonsync::SyncReplicaEvidenceState::Active &&
                first_inbound.receipt.receiver_state_generation ==
                    first_received.state_generation &&
                first_inbound.receipt.receiver_cutpoint_digest ==
                    first_received.cutpoint_digest,
            "receiver did not publish an exact active evidence receipt");

    const anonsync::SyncReplicaSqliteSnapshot sender_claimed =
        sender.snapshot_or_throw();
    auto wrong_channel = sender_channel(receiver_actor, "session-beta");
    require_error(
        [&] {
            (void)sender_service.apply_receipt_or_throw(
                wrong_channel, first_outbound->request,
                first_inbound.receipt_frame);
        },
        "expected request does not bind",
        "receipt replay crossed a different channel binding");
    require(sender.snapshot_or_throw() == sender_claimed,
            "cross-channel receipt rejection mutated sender authority");

    clock_state->epoch = 201U;
    require(
        sender_service.apply_receipt_or_throw(
            sender_link, first_outbound->request,
            first_inbound.receipt_frame) ==
            anonsync::SyncReplicaDeliveryReceiptApplyResult::EvidenceSettled,
        "evidence-terminal receiver receipt did not settle the exact sender attempt");
    const anonsync::SyncReplicaSqliteSnapshot first_settled =
        sender.snapshot_or_throw();
    require(first_settled.outbox.empty() &&
                first_settled.operation_set_digest ==
                    first_received.operation_set_digest &&
                first_settled.evidence_set_digest ==
                    first_received.evidence_set_digest &&
                first_settled.visible_state_digest ==
                    first_received.visible_state_digest,
            "channel-bound delivery did not converge sender and receiver evidence");

    // Fill the receiver with a distinct valid operation while preserving enough
    // per-envelope history budget to parse the sender's second dot. This makes
    // the next rejection true aggregate retention backpressure rather than an
    // invalid operation whose dot counter exceeds the receiver's model limit.
    (void)receiver.create_local_file_or_throw(
        "delivery/receiver-capacity-fill.bin", 4U,
        anonsync::sha256_hex("receiver-capacity-fill"));

    const anonsync::SyncReplicaOperation second =
        sender.create_local_file_or_throw(
            "delivery/second.bin", 6U, anonsync::sha256_hex("second"),
            destination);
    clock_state->epoch = 202U;
    const auto blocked_outbound = sender_service.claim_next_request_or_throw(
        sender_link, "delivery-worker", 10U);
    require(blocked_outbound.has_value() &&
                blocked_outbound->request.operation == second,
            "second operation did not acquire one durable attempt");
    const anonsync::SyncReplicaSqliteSnapshot receiver_before_block =
        receiver.snapshot_or_throw();
    const auto blocked_inbound = receiver_service.receive_request_or_throw(
        receiver_link, blocked_outbound->request_frame);
    require(blocked_inbound.admission ==
                anonsync::SyncReplicaAdmission::CapacityBlocked &&
                !blocked_inbound.receipt.evidence_state.has_value() &&
                blocked_inbound.receipt.receiver_state_generation ==
                    receiver_before_block.state_generation &&
                blocked_inbound.receipt.receiver_cutpoint_digest ==
                    receiver_before_block.cutpoint_digest,
            "receiver capacity block fabricated durable evidence");
    require(receiver.snapshot_or_throw() == receiver_before_block,
            "capacity-blocked request changed receiver cutpoint");
    const anonsync::SyncReplicaSqliteSnapshot sender_before_block_apply =
        sender.snapshot_or_throw();
    require(
        sender_service.apply_receipt_or_throw(
            sender_link, blocked_outbound->request,
            blocked_inbound.receipt_frame) ==
            anonsync::SyncReplicaDeliveryReceiptApplyResult::ReceiverCapacityBlocked,
        "capacity receipt was not reported as a nonterminal sender outcome");
    require(sender.snapshot_or_throw() == sender_before_block_apply,
            "capacity receipt settled or rewrote sender authority");

    anonsync::SyncReplicaSqliteOwnerLimits expanded = owner_limits(3U);
    receiver.replace_limits_or_throw(expanded);
    clock_state->epoch = 203U;
    require(
        sender.release_outbox_for_retry_or_throw(
            receiver_actor.device_id,
            second.operation_id,
            blocked_outbound->request.claim_id,
            0U) == anonsync::SyncReplicaSqliteOutboxReceiptResult::Applied,
        "capacity-blocked attempt could not be explicitly released");
    const auto retry_outbound = sender_service.claim_next_request_or_throw(
        sender_link, "delivery-worker-retry", 10U);
    require(retry_outbound.has_value() &&
                retry_outbound->request.claim_id !=
                    blocked_outbound->request.claim_id &&
                retry_outbound->request.dispatch_attempts == 2U,
            "capacity retry did not mint a fresh attempt identity");
    require(
        sender_service.apply_receipt_or_throw(
            sender_link, blocked_outbound->request,
            blocked_inbound.receipt_frame) ==
            anonsync::SyncReplicaDeliveryReceiptApplyResult::StaleClaim,
        "old capacity receipt remained current after retry claim");

    const auto retry_inbound = receiver_service.receive_request_or_throw(
        receiver_link, retry_outbound->request_frame);
    require(retry_inbound.admission ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "expanded receiver did not admit the retry");
    clock_state->epoch = 204U;
    require(
        sender_service.apply_receipt_or_throw(
            sender_link, retry_outbound->request,
            retry_inbound.receipt_frame) ==
            anonsync::SyncReplicaDeliveryReceiptApplyResult::EvidenceSettled,
        "fresh capacity retry receipt did not settle");
    require(sender.snapshot_or_throw().outbox.empty(),
            "settled capacity retry left an outbox intent");
}


void test_wire_policy_preflight_preserves_unclaimed_intent() {
    TempDatabasePath sender_file("anonsync-delivery-wire-preflight");
    const std::string folder = "folder-delivery-wire-preflight";
    const anonsync::SyncReplicaActor sender_actor{
        "device-delivery-wire-preflight-sender", 8301U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-delivery-wire-preflight-receiver", 8302U};
    const auto clock_state = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(sender_file.path);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(8U),
        "wire preflight sender", make_clock(clock_state));

    // Dot 1 is retained evidence without a destination. Dot 2 is the first
    // ready intent, and therefore cannot be encoded by a wire model whose
    // operation-history bound is only one.
    (void)sender.create_local_file_or_throw(
        "delivery/preflight-history.bin", 3U,
        anonsync::sha256_hex("preflight-history"));
    const std::vector<std::string> destination{receiver_actor.device_id};
    const anonsync::SyncReplicaOperation pending =
        sender.create_local_file_or_throw(
            "delivery/preflight-pending.bin", 4U,
            anonsync::sha256_hex("preflight-pending"), destination);

    anonsync::SyncReplicaDeliveryServiceLimits restrictive = service_limits();
    restrictive.wire_operation_limits.max_operations = 1U;
    anonsync::SyncReplicaDeliveryService restrictive_service(
        sender, restrictive, "wire preflight restrictive service");
    auto channel_source =
        sender_channel(receiver_actor, "session-preflight");
    clock_state->epoch = 400U;
    const anonsync::SyncReplicaSqliteSnapshot before =
        sender.snapshot_or_throw();

    std::string foreign_thread_error;
    std::thread foreign_thread([&] {
        try {
            (void)restrictive_service.claim_next_request_or_throw(
                channel_source, "wire-preflight-foreign-thread", 10U);
        } catch (const std::exception& error) {
            foreign_thread_error = error.what();
        }
    });
    foreign_thread.join();
    require(foreign_thread_error.find("thread") != std::string::npos &&
                sender.snapshot_or_throw() == before,
            "foreign-thread delivery authority reached durable owner work");

    auto channel = std::move(channel_source);
    require_error(
        [&] {
            (void)restrictive_service.claim_next_request_or_throw(
                channel_source, "wire-preflight-moved-from", 10U);
        },
        "empty or moved-from",
        "moved-from delivery authority reached durable owner work");
    require(sender.snapshot_or_throw() == before,
            "moved-from authority rejection changed the owner cutpoint");

    require_error(
        [&] {
            (void)restrictive_service.claim_next_request_or_throw(
                channel, "wire-preflight-worker", 10U);
        },
        "exceeds delivery wire policy before claim",
        "wire-incompatible operation acquired a durable lease");
    const anonsync::SyncReplicaSqliteSnapshot after_rejection =
        sender.snapshot_or_throw();
    require(after_rejection == before &&
                after_rejection.outbox.size() == 1U &&
                after_rejection.outbox.front().operation_id ==
                    pending.operation_id &&
                after_rejection.outbox.front().lease.claim_id.empty() &&
                after_rejection.outbox.front().lease.worker_id.empty() &&
                after_rejection.outbox.front().lease.dispatch_attempts == 0U,
            "wire preflight rejection changed the owner cutpoint or lease");

    anonsync::SyncReplicaDeliveryService compatible_service(
        sender, service_limits(), "wire preflight compatible service");
    const auto claimed = compatible_service.claim_next_request_or_throw(
        channel, "wire-preflight-compatible", 10U);
    require(claimed.has_value() &&
                claimed->request.operation == pending &&
                claimed->request.dispatch_attempts == 1U,
            "compatible wire policy could not claim the preserved intent");
}

void test_ambiguous_receiver_commit_survives_restart_and_stale_receipt() {
    TempDatabasePath sender_file("anonsync-delivery-ambiguous-sender");
    TempDatabasePath receiver_file("anonsync-delivery-ambiguous-receiver");
    const std::string folder = "folder-delivery-service-ambiguous";
    const anonsync::SyncReplicaActor sender_actor{
        "device-delivery-ambiguous-sender", 8201U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-delivery-ambiguous-receiver", 8202U};
    const auto clock_state = std::make_shared<MutableClockState>();
    const auto sender_link = sender_channel(receiver_actor, "session-gamma");
    const auto receiver_link = receiver_channel(sender_actor, "session-gamma");
    anonsync::SyncReplicaOutboundDelivery first_outbound;
    anonsync::SyncReplicaInboundDelivery first_inbound;
    anonsync::SyncReplicaOperation operation;
    anonsync::SyncReplicaSqliteSnapshot receiver_cutpoint;

    {
        anonsync::SyncSqliteDb sender_db = open_database(sender_file.path);
        anonsync::SyncSqliteDb receiver_db = open_database(receiver_file.path);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(8U),
            "ambiguous sender first process", make_clock(clock_state));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(8U),
            "ambiguous receiver first process", make_clock(clock_state));
        anonsync::SyncReplicaDeliveryService sender_service(
            sender, service_limits(), "ambiguous sender service first");
        anonsync::SyncReplicaDeliveryService receiver_service(
            receiver, service_limits(), "ambiguous receiver service first");
        const std::vector<std::string> destination{receiver_actor.device_id};
        operation = sender.create_local_file_or_throw(
            "delivery/ambiguous.bin", 9U,
            anonsync::sha256_hex("ambiguous"), destination);
        clock_state->epoch = 300U;
        const auto claimed = sender_service.claim_next_request_or_throw(
            sender_link, "ambiguous-worker", 10U);
        require(claimed.has_value(),
                "ambiguous first attempt was not claimed");
        first_outbound = *claimed;
        first_inbound = receiver_service.receive_request_or_throw(
            receiver_link, first_outbound.request_frame);
        require(first_inbound.admission ==
                    anonsync::SyncReplicaAdmission::InsertedActive,
                "ambiguous first attempt was not durably received");
        receiver_cutpoint = receiver.snapshot_or_throw();
        require(sender.snapshot_or_throw().outbox.size() == 1U,
                "ambiguous sender intent disappeared before settlement");
        // Both owners now close without applying first_inbound.receipt_frame.
    }

    {
        anonsync::SyncSqliteDb sender_db = open_database(sender_file.path);
        anonsync::SyncSqliteDb receiver_db = open_database(receiver_file.path);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(1U),
            "ambiguous sender restarted", make_clock(clock_state));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(1U),
            "ambiguous receiver restarted", make_clock(clock_state));
        anonsync::SyncReplicaDeliveryService sender_service(
            sender, service_limits(), "ambiguous sender service restarted");
        anonsync::SyncReplicaDeliveryService receiver_service(
            receiver, service_limits(), "ambiguous receiver service restarted");

        clock_state->epoch = 309U;
        require(
            !sender_service.claim_next_request_or_throw(
                 sender_link, "ambiguous-too-early", 10U)
                 .has_value(),
            "unexpired ambiguous attempt was claimed twice");
        clock_state->epoch = 310U;
        const auto retry = sender_service.claim_next_request_or_throw(
            sender_link, "ambiguous-retry", 10U);
        require(retry.has_value() &&
                    retry->request.operation == operation &&
                    retry->request.dispatch_attempts == 2U &&
                    retry->request.claim_id != first_outbound.request.claim_id,
                "expired ambiguous attempt did not mint a fresh request identity");
        const auto duplicate = receiver_service.receive_request_or_throw(
            receiver_link, retry->request_frame);
        require(duplicate.admission ==
                    anonsync::SyncReplicaAdmission::Duplicate &&
                    duplicate.receipt.receiver_state_generation ==
                        receiver_cutpoint.state_generation &&
                    duplicate.receipt.receiver_cutpoint_digest ==
                        receiver_cutpoint.cutpoint_digest &&
                    receiver.snapshot_or_throw() == receiver_cutpoint,
                "ambiguous retry rewrote receiver evidence instead of returning duplicate");

        const anonsync::SyncReplicaSqliteSnapshot sender_retry =
            sender.snapshot_or_throw();
        clock_state->epoch = 311U;
        require(
            sender_service.apply_receipt_or_throw(
                sender_link, first_outbound.request,
                first_inbound.receipt_frame) ==
                anonsync::SyncReplicaDeliveryReceiptApplyResult::StaleClaim,
            "old ambiguous receipt settled the replacement attempt");
        require(sender.snapshot_or_throw() == sender_retry,
                "stale ambiguous receipt mutated sender state");

        require(
            sender_service.apply_receipt_or_throw(
                sender_link, retry->request, duplicate.receipt_frame) ==
                anonsync::SyncReplicaDeliveryReceiptApplyResult::EvidenceSettled,
            "fresh duplicate receipt did not settle ambiguous delivery");
        const anonsync::SyncReplicaSqliteSnapshot settled =
            sender.snapshot_or_throw();
        require(settled.outbox.empty() &&
                    settled.operation_set_digest ==
                        receiver_cutpoint.operation_set_digest &&
                    settled.evidence_set_digest ==
                        receiver_cutpoint.evidence_set_digest &&
                    settled.visible_state_digest ==
                        receiver_cutpoint.visible_state_digest,
                "ambiguous delivery did not converge after fresh settlement");
        require(
            sender_service.apply_receipt_or_throw(
                sender_link, first_outbound.request,
                first_inbound.receipt_frame) ==
                anonsync::SyncReplicaDeliveryReceiptApplyResult::IntentMissing &&
                sender.snapshot_or_throw() == settled,
            "settled ambiguous receipt replay changed sender cutpoint");
    }
}

}  // namespace

int main() {
    try {
        test_channel_bound_end_to_end_and_capacity_retry();
        test_wire_policy_preflight_preserves_unclaimed_intent();
        test_ambiguous_receiver_commit_survives_restart_and_stale_receipt();
        std::cout << "sync replica delivery service tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica delivery service tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
