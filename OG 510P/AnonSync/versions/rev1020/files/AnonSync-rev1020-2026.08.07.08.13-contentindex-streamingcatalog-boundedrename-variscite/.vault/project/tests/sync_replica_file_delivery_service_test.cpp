#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_delivery_test_channel.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <chrono>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <sys/statvfs.h>
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
void require_error(Callable&& callable,
                   std::string_view expected,
                   const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

struct TempWorkspace final {
    std::filesystem::path root;
    std::filesystem::path sender_db;
    std::filesystem::path receiver_db;
    std::filesystem::path effect_db;
    std::filesystem::path files;

    explicit TempWorkspace(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __linux__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        root = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick));
        files = root / "files";
        std::filesystem::create_directories(files);
        sender_db = root / "sender.sqlite3";
        receiver_db = root / "receiver.sqlite3";
        effect_db = root / "effects.sqlite3";
    }

    ~TempWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
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
            owner.db, "file delivery service test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "file delivery service test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "file delivery service test durability profile");
    return owner;
}

#if !defined(_WIN32)
std::uint64_t observed_component_byte_limit(
    const std::filesystem::path& directory) {
    struct statvfs filesystem {};
    if (::statvfs(directory.c_str(), &filesystem) != 0) {
        fail("could not observe delivery-test filesystem filename limit");
    }
    std::uint64_t limit = static_cast<std::uint64_t>(filesystem.f_namemax);
    errno = 0;
    const long path_limit = ::pathconf(directory.c_str(), _PC_NAME_MAX);
    if (path_limit < 0 && errno != 0) {
        fail("could not observe delivery-test path filename limit");
    }
    if (path_limit > 0) {
        const auto converted = static_cast<std::uint64_t>(path_limit);
        limit = limit == 0U ? converted : std::min(limit, converted);
    }
    if (limit == 0U) fail("delivery-test filesystem reported no filename limit");
    return limit;
}
#endif

struct MutableClockState final {
    std::uint64_t epoch = 100U;
    std::vector<std::uint64_t> scripted_epochs;
    std::size_t scripted_index = 0U;
};

class MutableClockSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    explicit MutableClockSource(std::shared_ptr<MutableClockState> state)
        : state_(std::move(state)) {}

    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string&) override {
        if (!state_->scripted_epochs.empty()) {
            if (state_->scripted_index >= state_->scripted_epochs.size()) {
                throw std::runtime_error(
                    "file delivery service test scripted clock is exhausted");
            }
            state_->epoch = state_->scripted_epochs[state_->scripted_index++];
        }
        if (state_->epoch == 0U ||
            state_->epoch > std::numeric_limits<std::uint64_t>::max() /
                                anonsync::kSyncReplicaNanosecondsPerSecond) {
            throw std::runtime_error(
                "file delivery service test clock epoch is invalid");
        }
        const std::uint64_t nanoseconds =
            state_->epoch * anonsync::kSyncReplicaNanosecondsPerSecond;
        return {
            "test-file-delivery-clock-v1",
            "01234567-89ab-cdef-0123-456789abcdef",
            std::string(64U, 'd'),
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
    std::uint64_t max_operations = 64U) {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = max_operations;
    value.model.max_context_entries = 128U;
    value.model.max_predecessor_ids = 128U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    value.model.max_retained_context_entries = 8192U;
    value.model.max_retained_predecessor_ids = 8192U;
    value.max_outbox_intents = 128U;
    value.max_outbox_destination_bytes = 8192U;
    return value;
}

anonsync::SyncReplicaFileEffectSqliteOwnerLimits effect_limits(
    std::uint64_t max_effects = 64U) {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits value;
    value.model = owner_limits().model;
    value.max_effects = max_effects;
    value.max_payload_bytes = 256U * 1024U;
    value.max_retained_payload_bytes = 8U * 1024U * 1024U;
    // Most service fixtures want the aggregate and device boundaries to move
    // together. Tests exercising device isolation override only the device
    // limit while leaving the folder budget deliberately roomy.
    value.max_effects_per_device = max_effects;
    value.max_retained_payload_bytes_per_device =
        value.max_retained_payload_bytes;
    return value;
}

anonsync::SyncReplicaFileDeliveryServiceLimits service_limits() {
    anonsync::SyncReplicaFileDeliveryServiceLimits value;
    value.evidence.wire_operation_limits = owner_limits().model;
    value.evidence.max_request_frame_bytes = 512U * 1024U;
    value.evidence.max_receipt_frame_bytes = 32U * 1024U;
    value.retry.pre_dispatch_failure_delay_seconds = 2U;
    value.retry.effect_capacity_blocked_delay_seconds = 5U;
    value.retry.effect_path_blocked_delay_seconds = 60U;
    value.retry.evidence_capacity_blocked_delay_seconds = 5U;
    value.retry.evidence_pending_delay_seconds = 1U;
    value.retry.evidence_quarantined_delay_seconds = 60U;
    value.retry.projection_blocked_delay_seconds = 2U;
    value.retry.destination_conflict_delay_seconds = 60U;
    value.max_payload_bytes = 256U * 1024U;
    value.max_request_frame_bytes = 1024U * 1024U;
    value.max_receipt_frame_bytes = 64U * 1024U;
    return value;
}

anonsync::SyncReplicaFilePayloadSnapshot payload_snapshot(
    const std::string& folder,
    std::vector<std::string> payloads) {
    return anonsync::SyncReplicaFilePayloadSnapshot(
        folder, std::move(payloads), {}, "file delivery test payload snapshot");
}

anonsync::SyncReplicaFilePayloadSnapshot payload_snapshot(
    const std::string& folder,
    const std::string& payload) {
    return payload_snapshot(folder, std::vector<std::string>{payload});
}

void require_exact_retry_release(
    const anonsync::SyncReplicaSqliteSnapshot& before,
    const anonsync::SyncReplicaSqliteSnapshot& after,
    const std::string& operation_id,
    std::uint64_t dispatch_attempts,
    std::uint64_t released_at_epoch,
    std::uint64_t retry_not_before_epoch,
    const std::string& message) {
    const bool exact =
        after.state_generation == before.state_generation + 1U &&
            after.policy_generation == before.policy_generation &&
            after.durable == before.durable &&
            after.local_operation_digest == before.local_operation_digest &&
            after.operation_set_digest == before.operation_set_digest &&
            after.evidence_set_digest == before.evidence_set_digest &&
            after.visible_state_digest == before.visible_state_digest &&
            after.outbox_digest != before.outbox_digest &&
            after.cutpoint_digest != before.cutpoint_digest &&
            after.outbox.size() == 1U &&
            before.outbox.size() == 1U &&
            after.outbox.front().destination_device_id ==
                before.outbox.front().destination_device_id &&
            after.outbox.front().operation_id == operation_id &&
            after.outbox.front().enqueued_generation ==
                before.outbox.front().enqueued_generation &&
            after.outbox.front().lease.dispatch_attempts == dispatch_attempts &&
            after.outbox.front().lease.claim_id.empty() &&
            after.outbox.front().lease.worker_id.empty() &&
            after.outbox.front().lease.claimed_at_epoch == 0U &&
            after.outbox.front().lease.lease_expires_at_epoch == 0U &&
            after.outbox.front().lease.retry_released_at_epoch ==
                released_at_epoch &&
            after.outbox.front().lease.retry_not_before_epoch ==
                retry_not_before_epoch &&
            after.outbox.front().lease.retry_release_provenance ==
                anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact;
    if (!exact) {
        std::cerr << "retry-release diagnostic: before-state="
                  << before.state_generation << " after-state="
                  << after.state_generation << " before-policy="
                  << before.policy_generation << " after-policy="
                  << after.policy_generation << " before-outbox="
                  << before.outbox.size() << " after-outbox="
                  << after.outbox.size();
        if (!after.outbox.empty()) {
            const auto& lease = after.outbox.front().lease;
            std::cerr << " attempts=" << lease.dispatch_attempts
                      << " claim='" << lease.claim_id << "' worker='"
                      << lease.worker_id << "' claimed="
                      << lease.claimed_at_epoch << " expires="
                      << lease.lease_expires_at_epoch << " released="
                      << lease.retry_released_at_epoch << " retry="
                      << lease.retry_not_before_epoch << " provenance="
                      << static_cast<int>(lease.retry_release_provenance);
        }
        std::cerr << '\n';
    }
    require(exact, message);
}

using DeliveryAuthority = anonsync::SyncReplicaDeliveryChannelAuthority;

static_assert(!std::is_default_constructible_v<DeliveryAuthority>);
static_assert(!std::is_copy_constructible_v<DeliveryAuthority>);
static_assert(!std::is_copy_assignable_v<DeliveryAuthority>);
static_assert(std::is_nothrow_move_constructible_v<DeliveryAuthority>);
static_assert(std::is_nothrow_move_assignable_v<DeliveryAuthority>);

DeliveryAuthority sender_channel(
    const anonsync::SyncReplicaActor& receiver,
    std::string_view transcript) {
    return anonsync::testing::SyncReplicaDeliveryTestChannelFactory::
        make_or_throw(receiver, transcript);
}

DeliveryAuthority receiver_channel(
    const anonsync::SyncReplicaActor& sender,
    std::string_view transcript) {
    return anonsync::testing::SyncReplicaDeliveryTestChannelFactory::
        make_or_throw(sender, transcript);
}

std::string read_binary(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) fail("could not read materialized file");
    return {std::istreambuf_iterator<char>(input),
            std::istreambuf_iterator<char>()};
}

std::span<const unsigned char> bytes(const std::string& value) {
    return {reinterpret_cast<const unsigned char*>(value.data()), value.size()};
}

void test_effect_terminal_delivery_duplicate_and_create_new_boundary() {
    TempWorkspace workspace("anonsync-file-delivery-terminal");
    const std::string folder = "folder-file-delivery-terminal";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-terminal-sender", 9301U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-file-delivery-terminal-receiver", 9302U};
    const auto clock = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
    anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
    anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "file delivery terminal sender", make_clock(clock));
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_db.db, folder, receiver_actor, owner_limits(),
        "file delivery terminal receiver", make_clock(clock));
    anonsync::SyncReplicaFileEffectSqliteOwner effect(
        effect_db.db, folder, workspace.files, effect_limits(),
        "file delivery terminal effects");
    anonsync::SyncReplicaFileDeliveryService sender_service(
        sender, nullptr, service_limits(), "file delivery terminal sender service");
    anonsync::SyncReplicaFileDeliveryService receiver_service(
        receiver, &effect, service_limits(),
        "file delivery terminal receiver service");
    const auto sender_link = sender_channel(receiver_actor, "terminal-session");
    const auto receiver_link = receiver_channel(sender_actor, "terminal-session");
    const std::vector<std::string> destinations{receiver_actor.device_id};

    const std::string payload{"first\0payload\xff", 15U};
    const auto operation = sender.create_local_file_or_throw(
        "visible.bin", static_cast<std::uint64_t>(payload.size()),
        anonsync::sha256_hex(payload), destinations);
    clock->epoch = 200U;
    const auto outbound = sender_service.claim_next_request_or_throw(
        sender_link, "file-worker", 10U,
        payload_snapshot(folder, payload));
    require(outbound.has_value() &&
                outbound->request.evidence_request.operation == operation &&
                outbound->request.payload == payload,
            "sender did not bind exact payload bytes to its durable claim");

    const auto receiver_before = receiver.snapshot_or_throw();
    const auto effect_before = effect.snapshot_or_throw();
    std::string tampered = outbound->request_frame;
    tampered[tampered.size() / 2U] ^= 0x01;
    require_error(
        [&] {
            (void)receiver_service.receive_request_or_throw(
                receiver_link, tampered);
        },
        "digest mismatch",
        "tampered outer request reached payload staging");
    require(receiver.snapshot_or_throw() == receiver_before &&
                effect.snapshot_or_throw() == effect_before,
            "tampered request changed evidence or payload authority");

    const auto inbound = receiver_service.receive_request_or_throw(
        receiver_link, outbound->request_frame);
    require(inbound.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                inbound.evidence_delivery.has_value() &&
                inbound.evidence_delivery->admission ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                inbound.materialize_result ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::Published &&
                inbound.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published,
            "receiver did not compose stage, active evidence, and durable publication");
    require(read_binary(workspace.files / "visible.bin") == payload,
            "terminal receipt did not correspond to exact visible bytes");
    const auto receiver_published = receiver.snapshot_or_throw();
    const auto effect_published = effect.snapshot_or_throw();
    require(effect_published.effects.size() == 1U &&
                effect_published.effects.front().state ==
                    anonsync::SyncReplicaFileEffectState::Published &&
                inbound.receipt.receiver_effect_generation ==
                    effect_published.state_generation &&
                inbound.receipt.receiver_effect_cutpoint_digest ==
                    effect_published.cutpoint_digest,
            "terminal receipt did not bind the deciding effect cutpoint");

    auto wrong_sender_link = sender_channel(receiver_actor, "other-session");
    const auto sender_claimed = sender.snapshot_or_throw();
    require_error(
        [&] {
            (void)sender_service.apply_receipt_or_throw(
                wrong_sender_link, outbound->request,
                inbound.receipt_frame);
        },
        "expected request does not bind",
        "terminal receipt crossed a different authenticated channel");
    require(sender.snapshot_or_throw() == sender_claimed,
            "cross-channel receipt rejection changed sender authority");

    clock->epoch = 201U;
    require(sender_service.apply_receipt_or_throw(
                sender_link, outbound->request, inbound.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled,
            "durable publication receipt did not retire the exact sender intent");
    require(sender.snapshot_or_throw().outbox.empty(),
            "effect-terminal settlement left the sender intent live");

    const auto duplicate = receiver_service.receive_request_or_throw(
        receiver_link, outbound->request_frame);
    require(duplicate.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::Duplicate &&
                duplicate.evidence_delivery.has_value() &&
                duplicate.evidence_delivery->admission ==
                    anonsync::SyncReplicaAdmission::Duplicate &&
                duplicate.materialize_result ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::AlreadyPublished &&
                duplicate.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished,
            "exact duplicate did not reconcile all three receiver authorities");
    require(receiver.snapshot_or_throw() == receiver_published &&
                effect.snapshot_or_throw() == effect_published,
            "exact duplicate rewrote receiver evidence or effect cutpoint");
    require(sender_service.apply_receipt_or_throw(
                sender_link, outbound->request, duplicate.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::IntentMissing,
            "duplicate terminal receipt recreated or settled a missing intent");

    const std::string replacement = "replacement-payload";
    const auto update = sender.create_local_file_or_throw(
        "visible.bin", static_cast<std::uint64_t>(replacement.size()),
        anonsync::sha256_hex(replacement), destinations);
    clock->epoch = 202U;
    const auto update_outbound = sender_service.claim_next_request_or_throw(
        sender_link, "file-worker-update", 10U,
        payload_snapshot(folder, replacement));
    require(update_outbound.has_value(),
            "same-path update did not acquire an outbox attempt");
    const auto update_inbound = receiver_service.receive_request_or_throw(
        receiver_link, update_outbound->request_frame);
    require(update_inbound.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                update_inbound.evidence_delivery->receipt.evidence_state ==
                    anonsync::SyncReplicaEvidenceState::Active &&
                update_inbound.materialize_result ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::DestinationConflict &&
                update_inbound.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict,
            "create-new v1 boundary did not surface a same-path replacement conflict");
    require(read_binary(workspace.files / "visible.bin") == payload,
            "create-new v1 replaced an existing visible file");
    const auto sender_before_conflict = sender.snapshot_or_throw();
    require(sender_service.apply_receipt_or_throw(
                sender_link, update_outbound->request,
                update_inbound.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::ReceiverDestinationConflict,
            "same-path create-new conflict was misclassified as terminal");
    require_exact_retry_release(
        sender_before_conflict, sender.snapshot_or_throw(),
        update.operation_id, 1U, 202U, 262U,
        "destination conflict did not release the exact attempt onto local backoff");
}

void test_pending_dependency_stages_once_then_publishes_on_retry() {
    TempWorkspace workspace("anonsync-file-delivery-pending");
    const std::string folder = "folder-file-delivery-pending";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-pending-sender", 9401U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-file-delivery-pending-receiver", 9402U};
    const auto clock = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
    anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
    anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "pending sender", make_clock(clock));
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_db.db, folder, receiver_actor, owner_limits(),
        "pending receiver", make_clock(clock));
    anonsync::SyncReplicaFileEffectSqliteOwner effect(
        effect_db.db, folder, workspace.files, effect_limits(),
        "pending effects");
    anonsync::SyncReplicaFileDeliveryService sender_service(
        sender, nullptr, service_limits(), "pending sender service");
    anonsync::SyncReplicaFileDeliveryService receiver_service(
        receiver, &effect, service_limits(), "pending receiver service");
    const auto sender_link = sender_channel(receiver_actor, "pending-session");
    const auto receiver_link = receiver_channel(sender_actor, "pending-session");
    const std::vector<std::string> destinations{receiver_actor.device_id};

    const auto predecessor = sender.publish_local_file_or_throw(
        "predecessor.bin", 3U, anonsync::sha256_hex("pre"));
    const std::string payload = "dependent-payload";
    const auto dependent = sender.create_local_file_or_throw(
        "dependent.bin", static_cast<std::uint64_t>(payload.size()),
        anonsync::sha256_hex(payload), destinations);
    clock->epoch = 300U;
    const auto first = sender_service.claim_next_request_or_throw(
        sender_link, "pending-worker", 10U,
        payload_snapshot(folder, payload));
    require(first.has_value() &&
                first->request.evidence_request.operation == dependent,
            "dependent operation did not acquire its first attempt");
    const auto pending = receiver_service.receive_request_or_throw(
        receiver_link, first->request_frame);
    require(pending.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                pending.evidence_delivery->admission ==
                    anonsync::SyncReplicaAdmission::InsertedPending &&
                !pending.materialize_result.has_value() &&
                pending.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::EvidencePending,
            "missing dependency did not retain payload and pending evidence without publication");
    require(!std::filesystem::exists(workspace.files / "dependent.bin") &&
                effect.snapshot_or_throw().effects.front().state ==
                    anonsync::SyncReplicaFileEffectState::Staged,
            "pending evidence became a visible or terminal effect");
    const auto sender_pending = sender.snapshot_or_throw();
    require(sender_service.apply_receipt_or_throw(
                sender_link, first->request, pending.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::ReceiverEvidencePending,
            "pending receipt was not reported as nonterminal");
    require_exact_retry_release(
        sender_pending, sender.snapshot_or_throw(), dependent.operation_id,
        1U, 300U, 301U,
        "pending receipt did not release exact attempt onto immediate local retry policy");
    const auto sender_released = sender.snapshot_or_throw();
    require(sender_service.apply_receipt_or_throw(
                sender_link, first->request, pending.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::StaleClaim &&
                sender.snapshot_or_throw() == sender_released,
            "replayed pending receipt changed released retry authority");
    require(!sender_service.claim_next_request_or_throw(
                 sender_link, "pending-worker-too-early", 10U,
                 payload_snapshot(folder, payload))
                 .has_value(),
            "pending retry became claimable before its exact local deadline");

    require(receiver.accept_remote_or_throw(predecessor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "missing predecessor was not admitted");
    const auto receiver_after_predecessor = receiver.snapshot_or_throw();
    const auto receiver_model = anonsync::SyncReplicaModel::restore_or_throw(
        receiver_after_predecessor.durable,
        receiver_after_predecessor.limits.model);
    require(receiver_model.evidence_state(dependent.operation_id) ==
                anonsync::SyncReplicaEvidenceState::Active,
            "predecessor admission did not promote dependent evidence");
    clock->epoch = 301U;
    const auto retry = sender_service.claim_next_request_or_throw(
        sender_link, "pending-worker-retry", 10U,
        payload_snapshot(folder, payload));
    require(retry.has_value() &&
                retry->request.evidence_request.dispatch_attempts == 2U &&
                retry->request.evidence_request.claim_id !=
                    first->request.evidence_request.claim_id,
            "pending retry did not mint fresh attempt authority");
    const auto published = receiver_service.receive_request_or_throw(
        receiver_link, retry->request_frame);
    require(published.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::Duplicate &&
                published.evidence_delivery->admission ==
                    anonsync::SyncReplicaAdmission::Duplicate &&
                published.evidence_delivery->receipt.evidence_state ==
                    anonsync::SyncReplicaEvidenceState::Active &&
                published.materialize_result ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::Published &&
                published.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published,
            "promoted duplicate did not publish the once-staged payload");
    require(read_binary(workspace.files / "dependent.bin") == payload,
            "promoted retry published different bytes");
    clock->epoch = 302U;
    require(sender_service.apply_receipt_or_throw(
                sender_link, retry->request, published.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled &&
                sender.snapshot_or_throw().outbox.empty(),
            "published retry did not settle the dependent intent");
}

void test_ambiguous_publication_survives_three_owner_restart() {
    TempWorkspace workspace("anonsync-file-delivery-restart");
    const std::string folder = "folder-file-delivery-restart";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-restart-sender", 9501U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-file-delivery-restart-receiver", 9502U};
    const auto clock = std::make_shared<MutableClockState>();
    const auto sender_link = sender_channel(receiver_actor, "restart-session");
    const auto receiver_link = receiver_channel(sender_actor, "restart-session");
    const std::string payload{"restart\0payload", 15U};
    anonsync::SyncReplicaOutboundFileDelivery first_outbound;
    anonsync::SyncReplicaInboundFileDelivery first_inbound;
    anonsync::SyncReplicaOperation operation;
    anonsync::SyncReplicaSqliteSnapshot receiver_cutpoint;
    anonsync::SyncReplicaFileEffectSqliteSnapshot effect_cutpoint;

    {
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "restart sender first", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(),
            "restart receiver first", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_db.db, folder, workspace.files, effect_limits(),
            "restart effect first");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, service_limits(), "restart sender service first");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, service_limits(), "restart receiver service first");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        operation = sender.create_local_file_or_throw(
            "restart.bin", static_cast<std::uint64_t>(payload.size()),
            anonsync::sha256_hex(payload), destinations);
        clock->epoch = 400U;
        const auto claimed = sender_service.claim_next_request_or_throw(
            sender_link, "restart-worker", 10U,
            payload_snapshot(folder, payload));
        require(claimed.has_value(),
                "ambiguous publication first attempt was not claimed");
        first_outbound = *claimed;
        first_inbound = receiver_service.receive_request_or_throw(
            receiver_link, first_outbound.request_frame);
        require(first_inbound.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published &&
                    read_binary(workspace.files / "restart.bin") == payload,
                "receiver did not durably publish before simulated response loss");
        receiver_cutpoint = receiver.snapshot_or_throw();
        effect_cutpoint = effect.snapshot_or_throw();
        require(sender.snapshot_or_throw().outbox.size() == 1U,
                "sender intent vanished before publication receipt settlement");
        // All three owners close without applying first_inbound.receipt_frame.
    }

    {
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(1U),
            "restart sender second", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(1U),
            "restart receiver second", make_clock(clock));
        auto changed_effect_defaults = effect_limits(1U);
        changed_effect_defaults.max_payload_bytes = 1U;
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_db.db, folder, workspace.files, changed_effect_defaults,
            "restart effect second");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, service_limits(), "restart sender service second");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, service_limits(), "restart receiver service second");
        require(receiver.snapshot_or_throw() == receiver_cutpoint &&
                    effect.snapshot_or_throw() == effect_cutpoint,
                "restart changed receiver evidence or effect authority");

        clock->epoch = 409U;
        require(!sender_service.claim_next_request_or_throw(
                     sender_link, "restart-too-early", 10U,
                     payload_snapshot(folder, payload))
                     .has_value(),
                "unexpired ambiguous file attempt was claimed twice");
        clock->epoch = 410U;
        const auto retry = sender_service.claim_next_request_or_throw(
            sender_link, "restart-retry", 10U,
            payload_snapshot(folder, payload));
        require(retry.has_value() &&
                    retry->request.evidence_request.operation == operation &&
                    retry->request.evidence_request.dispatch_attempts == 2U &&
                    retry->request.evidence_request.claim_id !=
                        first_outbound.request.evidence_request.claim_id,
                "expired ambiguous file attempt did not mint a fresh claim");
        const auto duplicate = receiver_service.receive_request_or_throw(
            receiver_link, retry->request_frame);
        require(duplicate.stage_result ==
                    anonsync::SyncReplicaFileEffectStageResult::Duplicate &&
                    duplicate.evidence_delivery->admission ==
                        anonsync::SyncReplicaAdmission::Duplicate &&
                    duplicate.materialize_result ==
                        anonsync::SyncReplicaFileEffectMaterializeResult::AlreadyPublished &&
                    duplicate.receipt.disposition ==
                        anonsync::SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished &&
                    receiver.snapshot_or_throw() == receiver_cutpoint &&
                    effect.snapshot_or_throw() == effect_cutpoint,
                "ambiguous retry did not reconcile exact receiver cutpoints");

        const auto sender_retry = sender.snapshot_or_throw();
        clock->epoch = 411U;
        require(sender_service.apply_receipt_or_throw(
                    sender_link, first_outbound.request,
                    first_inbound.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::StaleClaim,
                "stale publication receipt settled replacement attempt");
        require(sender.snapshot_or_throw() == sender_retry,
                "stale publication receipt changed sender authority");
        require(sender_service.apply_receipt_or_throw(
                    sender_link, retry->request,
                    duplicate.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled,
                "fresh already-published receipt did not settle retry");
        const auto settled = sender.snapshot_or_throw();
        require(settled.outbox.empty(),
                "ambiguous publication retry left sender intent live");
        require(sender_service.apply_receipt_or_throw(
                    sender_link, first_outbound.request,
                    first_inbound.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::IntentMissing &&
                    sender.snapshot_or_throw() == settled,
                "old receipt replay changed a settled sender cutpoint");
    }
}

void test_live_authority_and_payload_snapshot_preflight_precede_claim_mutation() {
    {
        TempWorkspace workspace("anonsync-file-delivery-payload-preflight");
        const std::string folder = "folder-file-delivery-payload-preflight";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-payload-sender", 9751U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-payload-receiver", 9752U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "payload preflight sender", make_clock(clock));
        const auto limits = service_limits();
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, limits, "payload preflight service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const auto operation = sender.create_local_file_or_throw(
            "oversize.bin", limits.max_payload_bytes + 1U,
            anonsync::sha256_hex("declared-oversize-payload"), destinations);
        auto channel = sender_channel(receiver_actor, "payload-preflight-session");
        clock->epoch = 700U;
        const auto before = sender.snapshot_or_throw();
        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    channel, "payload-preflight-worker", 10U,
                    payload_snapshot(folder, std::vector<std::string>{}));
            },
            "exceeds delivery payload policy before claim",
            "oversized committed payload acquired a durable lease");
        const auto after = sender.snapshot_or_throw();
        require(after == before && after.outbox.size() == 1U &&
                    after.outbox.front().operation_id == operation.operation_id &&
                    after.outbox.front().lease ==
                        anonsync::SyncReplicaOutboxLeaseState{},
                "payload preflight rejection changed attempt or cutpoint authority");
    }

    {
        TempWorkspace workspace("anonsync-file-delivery-payload-snapshot-scope");
        const std::string folder = "folder-file-delivery-payload-snapshot-scope";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-snapshot-sender", 9761U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-snapshot-receiver", 9762U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "payload snapshot sender", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, service_limits(), "payload snapshot service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        std::string source_payload = "immutable-payload-snapshot";
        const std::string expected_payload = source_payload;
        const auto operation = sender.create_local_file_or_throw(
            "snapshot.bin", source_payload.size(),
            anonsync::sha256_hex(source_payload), destinations);
        auto payloads = payload_snapshot(
            folder, std::vector<std::string>{source_payload, "unrelated-content"});
        source_payload.assign(source_payload.size(), 'x');
        require(payloads.entry_count() == 2U &&
                    payloads.retained_bytes() ==
                        expected_payload.size() + std::string_view("unrelated-content").size() &&
                    anonsync::is_lowercase_sha256_hex(payloads.snapshot_digest()),
                "payload snapshot did not retain bounded immutable identity");

        auto moved_from_channel = sender_channel(
            receiver_actor, "payload-snapshot-scope-session");
        auto live_channel = std::move(moved_from_channel);
        clock->epoch = 710U;
        const auto before = sender.snapshot_or_throw();
        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    moved_from_channel, "moved-authority-worker", 10U,
                    payloads);
            },
            "empty or moved-from",
            "moved-from file-delivery authority reached durable owner work");
        require(sender.snapshot_or_throw() == before,
                "moved-from authority rejection changed claim authority");

        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    live_channel, "wrong-folder-payload-worker", 10U,
                    payload_snapshot("different-folder", expected_payload));
            },
            "does not match service folder identity",
            "cross-folder payload snapshot reached durable owner work");
        require(sender.snapshot_or_throw() == before,
                "cross-folder payload snapshot rejection changed authority");

        auto inactive_payloads = payload_snapshot(folder, expected_payload);
        auto active_payloads = std::move(inactive_payloads);
        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    live_channel, "inactive-payload-worker", 10U,
                    inactive_payloads);
            },
            "payload snapshot is inactive",
            "moved-from payload snapshot reached durable owner work");
        require(sender.snapshot_or_throw() == before,
                "inactive payload snapshot rejection changed authority");

        const auto outbound = service.claim_next_request_or_throw(
            live_channel, "live-snapshot-worker", 10U,
            std::move(active_payloads));
        require(outbound.has_value() &&
                    outbound->request.evidence_request.operation == operation &&
                    outbound->request.payload == expected_payload,
                "immutable payload snapshot did not select exact content authority");
    }
}

void test_payload_snapshot_validation_selection_and_exact_mismatch_release() {
    const std::string folder = "folder-file-payload-snapshot-validation";
    const std::string alpha = "alpha-payload";
    const std::string beta{"beta\0payload", 12U};
    const std::string empty;
    const auto ordered = payload_snapshot(
        folder, std::vector<std::string>{alpha, beta, empty});
    const auto reordered = payload_snapshot(
        folder, std::vector<std::string>{empty, beta, alpha});
    require(ordered.snapshot_digest() == reordered.snapshot_digest() &&
                ordered.entry_count() == 3U &&
                ordered.retained_bytes() == alpha.size() + beta.size(),
            "payload snapshot digest depends on caller insertion order");
    const anonsync::SyncReplicaFileContentInventory content_inventory =
        ordered.content_inventory();
    const std::span<const std::string> content_sha256s =
        content_inventory.content_sha256s();
    require(content_sha256s.size() == 3U &&
                std::is_sorted(content_sha256s.begin(), content_sha256s.end()) &&
                std::adjacent_find(
                    content_sha256s.begin(), content_sha256s.end()) ==
                    content_sha256s.end() &&
                std::binary_search(
                    content_sha256s.begin(), content_sha256s.end(),
                    anonsync::sha256_hex(alpha)) &&
                std::binary_search(
                    content_sha256s.begin(), content_sha256s.end(),
                    anonsync::sha256_hex(beta)) &&
                std::binary_search(
                    content_sha256s.begin(), content_sha256s.end(),
                    anonsync::sha256_hex(empty)),
            "payload snapshot did not expose one canonical immutable digest inventory");

    anonsync::SyncReplicaOperation beta_operation;
    beta_operation.kind = anonsync::SyncReplicaValueKind::File;
    beta_operation.size_bytes = beta.size();
    beta_operation.content_sha256 = anonsync::sha256_hex(beta);
    require(ordered.copy_payload_for_operation_or_throw(beta_operation) == beta,
            "payload snapshot lookup did not return exact binary bytes");
    const std::string detached_payload =
        payload_snapshot(folder, std::vector<std::string>{beta})
            .copy_payload_for_operation_or_throw(beta_operation);
    require(detached_payload == beta,
            "payload snapshot lookup returned a lifetime-sensitive borrowed view");

    auto invalid_operation = beta_operation;
    invalid_operation.kind = anonsync::SyncReplicaValueKind::Tombstone;
    require_error(
        [&] { (void)ordered.copy_payload_for_operation_or_throw(invalid_operation); },
        "requires a file operation",
        "payload snapshot authorized a non-file operation");
    invalid_operation = beta_operation;
    invalid_operation.content_sha256 = "not-a-digest";
    require_error(
        [&] { (void)ordered.copy_payload_for_operation_or_throw(invalid_operation); },
        "operation content digest is invalid",
        "payload snapshot accepted malformed content identity");
    invalid_operation = beta_operation;
    invalid_operation.size_bytes += 1U;
    require_error(
        [&] { (void)ordered.copy_payload_for_operation_or_throw(invalid_operation); },
        "payload size disagrees with the claimed operation",
        "payload snapshot ignored declared-size disagreement");
    require_error(
        [&] { ordered.require_folder_or_throw("Bad/Folder", "invalid scope"); },
        "service folder_id is invalid",
        "payload snapshot accepted malformed service scope");
    auto copied = ordered;
    auto moved = std::move(copied);
    require(moved.snapshot_digest() == ordered.snapshot_digest(),
            "payload snapshot copy/move changed structural identity");
    require_error(
        [&] { (void)copied.entry_count(); },
        "payload snapshot is inactive",
        "moved-from payload snapshot remained active");
    require_error(
        [&] {
            (void)payload_snapshot(
                folder, std::vector<std::string>{alpha, alpha});
        },
        "duplicate content authority",
        "payload snapshot accepted duplicate digest authority");

    anonsync::SyncReplicaFilePayloadSnapshotLimits invalid_limits;
    invalid_limits.max_entries = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_snapshot_limits_or_throw(
                invalid_limits);
        },
        "entry limit is invalid",
        "payload snapshot accepted a zero entry budget");
    invalid_limits = {};
    invalid_limits.max_entries =
        anonsync::kSyncReplicaFilePayloadSnapshotMaxEntries + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_snapshot_limits_or_throw(
                invalid_limits);
        },
        "entry limit is invalid",
        "payload snapshot accepted an entry limit above its hard ceiling");
    invalid_limits = {};
    invalid_limits.max_payload_bytes = 5U;
    invalid_limits.max_retained_bytes = 4U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_payload_snapshot_limits_or_throw(
                invalid_limits);
        },
        "byte limits are invalid",
        "payload snapshot accepted inverted byte budgets");

    anonsync::SyncReplicaFilePayloadSnapshotLimits small_limits;
    small_limits.max_entries = 2U;
    small_limits.max_payload_bytes = 4U;
    small_limits.max_retained_bytes = 7U;
    require_error(
        [&] {
            (void)anonsync::SyncReplicaFilePayloadSnapshot(
                folder, std::vector<std::string>{"1", "2", "3"},
                small_limits);
        },
        "entry count exceeds its configured budget",
        "payload snapshot crossed its configured entry budget");
    require_error(
        [&] {
            (void)anonsync::SyncReplicaFilePayloadSnapshot(
                folder, std::vector<std::string>{"12345"}, small_limits);
        },
        "payload exceeds its configured byte budget",
        "payload snapshot retained an oversized entry");
    require_error(
        [&] {
            (void)anonsync::SyncReplicaFilePayloadSnapshot(
                folder, std::vector<std::string>{"1234", "5678"},
                small_limits);
        },
        "aggregate payload bytes exceed their configured budget",
        "payload snapshot crossed its aggregate byte budget");

    {
        TempWorkspace workspace("anonsync-file-delivery-payload-selection");
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-selection-sender", 9771U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-selection-receiver", 9772U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "payload selection sender", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, service_limits(), "payload selection service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string first_payload = "payload-selection-first";
        const std::string second_payload = "payload-selection-second";
        const auto first_operation = sender.create_local_file_or_throw(
            "selection-first.bin", first_payload.size(),
            anonsync::sha256_hex(first_payload), destinations);
        const auto second_operation = sender.create_local_file_or_throw(
            "selection-second.bin", second_payload.size(),
            anonsync::sha256_hex(second_payload), destinations);
        const auto before = sender.snapshot_or_throw();
        require(before.outbox.size() == 2U,
                "payload selection seed did not retain two canonical intents");

        const std::string& available_operation_id =
            before.outbox.back().operation_id;
        const bool first_is_available =
            available_operation_id == first_operation.operation_id;
        const std::string& available_payload =
            first_is_available ? first_payload : second_payload;
        const std::string& unavailable_operation_id =
            before.outbox.front().operation_id;
        require(unavailable_operation_id != available_operation_id,
                "payload selection seed did not establish canonical head-of-line order");

        auto channel = sender_channel(receiver_actor, "payload-selection-session");
        clock->epoch = 720U;
        const auto outbound = service.claim_next_request_or_throw(
            channel, "payload-selection-worker", 10U,
            payload_snapshot(folder, available_payload));
        require(outbound.has_value() &&
                    outbound->claim.operation.operation_id ==
                        available_operation_id &&
                    outbound->request.payload == available_payload &&
                    outbound->request.evidence_request.dispatch_attempts == 1U,
                "immutable payload inventory did not select the first available canonical intent");
        const auto selected = sender.snapshot_or_throw();
        const auto unavailable = std::find_if(
            selected.outbox.begin(), selected.outbox.end(),
            [&](const anonsync::SyncReplicaSqliteOutboxIntent& intent) {
                return intent.operation_id == unavailable_operation_id;
            });
        const auto available = std::find_if(
            selected.outbox.begin(), selected.outbox.end(),
            [&](const anonsync::SyncReplicaSqliteOutboxIntent& intent) {
                return intent.operation_id == available_operation_id;
            });
        require(unavailable != selected.outbox.end() &&
                    unavailable->lease ==
                        anonsync::SyncReplicaOutboxLeaseState{} &&
                    available != selected.outbox.end() &&
                    available->lease.dispatch_attempts == 1U &&
                    !available->lease.claim_id.empty(),
                "unavailable head-of-line payload consumed attempt or retry authority");
    }

    {
        TempWorkspace workspace("anonsync-file-delivery-payload-size-mismatch");
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-mismatch-sender", 9773U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-mismatch-receiver", 9774U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "payload mismatch sender", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, service_limits(), "payload mismatch service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string payload = "digest-present-size-mismatch";
        const auto operation = sender.create_local_file_or_throw(
            "mismatch.bin", payload.size() + 1U,
            anonsync::sha256_hex(payload), destinations);
        auto channel = sender_channel(receiver_actor, "payload-mismatch-session");
        clock->epoch = 730U;
        const auto before = sender.snapshot_or_throw();
        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    channel, "payload-mismatch-worker", 10U,
                    payload_snapshot(folder, payload));
            },
            "payload size disagrees with the claimed operation",
            "digest-selected size mismatch escaped as an outbound frame");
        const auto released = sender.snapshot_or_throw();
        require(released.state_generation == before.state_generation + 2U &&
                    released.policy_generation == before.policy_generation &&
                    released.durable == before.durable &&
                    released.outbox.size() == 1U &&
                    released.outbox.front().operation_id ==
                        operation.operation_id &&
                    released.outbox.front().lease.dispatch_attempts == 1U &&
                    released.outbox.front().lease.claim_id.empty() &&
                    released.outbox.front().lease.worker_id.empty() &&
                    released.outbox.front().lease.retry_released_at_epoch ==
                        730U &&
                    released.outbox.front().lease.retry_not_before_epoch ==
                        732U &&
                    released.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "post-selection size mismatch did not exact-release its bounded live attempt");
    }
}


#if !defined(_WIN32)
void test_durable_payload_store_selection_and_exact_release() {
    {
        TempWorkspace workspace("anonsync-file-delivery-durable-selection");
        const std::string folder = "folder-file-delivery-durable-selection";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-durable-sender", 9781U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-durable-receiver", 9782U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "durable payload selection sender", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, service_limits(),
            "durable payload selection service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string first_payload = "durable-selection-first";
        const std::string second_payload = "durable-selection-second";
        const auto first_operation = sender.create_local_file_or_throw(
            "durable-first.bin", first_payload.size(),
            anonsync::sha256_hex(first_payload), destinations);
        const auto second_operation = sender.create_local_file_or_throw(
            "durable-second.bin", second_payload.size(),
            anonsync::sha256_hex(second_payload), destinations);
        const auto before = sender.snapshot_or_throw();
        require(before.outbox.size() == 2U,
                "durable payload selection seed lost an outbox intent");

        const std::string& available_operation_id =
            before.outbox.back().operation_id;
        const bool first_is_available =
            available_operation_id == first_operation.operation_id;
        const std::string& available_payload =
            first_is_available ? first_payload : second_payload;
        const std::string& unavailable_operation_id =
            before.outbox.front().operation_id;
        require(unavailable_operation_id != available_operation_id &&
                    (available_operation_id == first_operation.operation_id ||
                     available_operation_id == second_operation.operation_id),
                "durable selection seed did not establish canonical ordering");

        const std::filesystem::path payload_root = workspace.root / "payloads";
        std::filesystem::create_directory(payload_root);
        if (::chmod(payload_root.c_str(), 0700) != 0) {
            fail("could not make durable selection payload root private");
        }
        anonsync::SyncReplicaFilePayloadStore payload_store(
            folder, payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "durable selection payload store");
        (void)payload_store.put_payload_or_throw(available_payload);
        auto durable_snapshot = payload_store.snapshot_or_throw();

        auto channel = sender_channel(
            receiver_actor, "durable-payload-selection-session");
        clock->epoch = 740U;
        const auto outbound = service.claim_next_request_or_throw(
            channel, "durable-payload-selection-worker", 10U,
            durable_snapshot);
        require(outbound.has_value() &&
                    outbound->claim.operation.operation_id ==
                        available_operation_id &&
                    outbound->request.payload == available_payload &&
                    outbound->request.evidence_request.dispatch_attempts == 1U,
                "durable digest inventory did not select exact available intent");
        const auto selected = sender.snapshot_or_throw();
        const auto unavailable = std::find_if(
            selected.outbox.begin(), selected.outbox.end(),
            [&](const anonsync::SyncReplicaSqliteOutboxIntent& intent) {
                return intent.operation_id == unavailable_operation_id;
            });
        const auto available = std::find_if(
            selected.outbox.begin(), selected.outbox.end(),
            [&](const anonsync::SyncReplicaSqliteOutboxIntent& intent) {
                return intent.operation_id == available_operation_id;
            });
        require(unavailable != selected.outbox.end() &&
                    unavailable->lease ==
                        anonsync::SyncReplicaOutboxLeaseState{} &&
                    available != selected.outbox.end() &&
                    available->lease.dispatch_attempts == 1U &&
                    !available->lease.claim_id.empty(),
                "unavailable durable head consumed attempt or retry authority");
    }

    {
        TempWorkspace workspace("anonsync-file-delivery-durable-release");
        const std::string folder = "folder-file-delivery-durable-release";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-durable-release-sender", 9791U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-durable-release-receiver", 9792U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "durable payload release sender", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            sender, nullptr, service_limits(),
            "durable payload release service");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string payload = "durable-post-index-removal";
        const auto operation = sender.create_local_file_or_throw(
            "durable-release.bin", payload.size(),
            anonsync::sha256_hex(payload), destinations);

        const std::filesystem::path payload_root = workspace.root / "payloads";
        std::filesystem::create_directory(payload_root);
        if (::chmod(payload_root.c_str(), 0700) != 0) {
            fail("could not make durable release payload root private");
        }
        anonsync::SyncReplicaFilePayloadStore payload_store(
            folder, payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
            {}, "durable release payload store");
        const auto put = payload_store.put_payload_or_throw(payload);
        auto durable_snapshot = payload_store.snapshot_or_throw();
        if (::unlink((payload_root / put.content_sha256).c_str()) != 0) {
            fail("could not remove durable selected-payload fixture");
        }

        auto channel = sender_channel(
            receiver_actor, "durable-payload-release-session");
        clock->epoch = 750U;
        const auto before = sender.snapshot_or_throw();
        require_error(
            [&] {
                (void)service.claim_next_request_or_throw(
                    channel, "durable-payload-release-worker", 10U,
                    durable_snapshot);
            },
            "inspection failed",
            "post-index deletion escaped as an outbound request");
        const auto released = sender.snapshot_or_throw();
        require(
            released.state_generation == before.state_generation + 2U &&
                released.policy_generation == before.policy_generation &&
                released.durable == before.durable &&
                released.local_operation_digest ==
                    before.local_operation_digest &&
                released.operation_set_digest == before.operation_set_digest &&
                released.evidence_set_digest == before.evidence_set_digest &&
                released.visible_state_digest == before.visible_state_digest &&
                released.outbox.size() == 1U &&
                released.outbox.front().operation_id == operation.operation_id &&
                released.outbox.front().lease.dispatch_attempts == 1U &&
                released.outbox.front().lease.claim_id.empty() &&
                released.outbox.front().lease.worker_id.empty() &&
                released.outbox.front().lease.retry_released_at_epoch == 750U &&
                released.outbox.front().lease.retry_not_before_epoch == 752U &&
                released.outbox.front().lease.retry_release_provenance ==
                    anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
            "post-index durable read failure did not exact-release its claim");

        const auto replaced = payload_store.put_payload_or_throw(payload);
        require(replaced.disposition ==
                    anonsync::SyncReplicaFilePayloadStorePutDisposition::Inserted,
                "exact bytes were not republished after external deletion");
        clock->epoch = 752U;
        const auto retry = service.claim_next_request_or_throw(
            channel, "durable-payload-retry-worker", 10U,
            durable_snapshot);
        require(retry.has_value() &&
                    retry->claim.operation.operation_id ==
                        operation.operation_id &&
                    retry->request.payload == payload &&
                    retry->request.evidence_request.dispatch_attempts == 2U,
                "reusable durable snapshot did not reconcile exact republished bytes");
    }
}
#endif

void test_retry_policy_validation_precedes_durable_authority() {
    TempWorkspace workspace("anonsync-file-delivery-retry-policy");
    const std::string folder = "folder-file-delivery-retry-policy";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-retry-policy-sender", 9801U};
    anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "retry-policy sender");
    const auto before = sender.snapshot_or_throw();

    auto limits = service_limits();
    limits.retry.pre_dispatch_failure_delay_seconds =
        anonsync::kSyncReplicaOutboxMaxRetryDelaySeconds + 1U;
    require_error(
        [&] {
            anonsync::SyncReplicaFileDeliveryService invalid(
                sender, nullptr, limits, "invalid retry-policy service");
        },
        "must be positive and within the fixed outbox retry-delay budget",
        "oversized retry policy reached service authority");
    require(sender.snapshot_or_throw() == before,
            "oversized retry-policy validation changed durable sender state");

    limits = service_limits();
    limits.retry.evidence_pending_delay_seconds = 0U;
    require_error(
        [&] {
            anonsync::SyncReplicaFileDeliveryService invalid(
                sender, nullptr, limits, "zero retry-policy service");
        },
        "must be positive and within the fixed outbox retry-delay budget",
        "zero retry delay reached service authority");
    require(sender.snapshot_or_throw() == before,
            "zero retry-policy validation changed durable sender state");
}

void test_post_snapshot_dispatch_guard_closes_clock_expiry() {
    TempWorkspace workspace("anonsync-file-delivery-snapshot-expiry");
    const std::string folder = "folder-file-delivery-snapshot-expiry";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-snapshot-expiry-sender", 9781U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-file-delivery-snapshot-expiry-receiver", 9782U};
    const auto clock = std::make_shared<MutableClockState>();
    clock->scripted_epochs = {770U, 772U};
    anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "snapshot expiry sender", make_clock(clock));
    anonsync::SyncReplicaFileDeliveryService service(
        sender, nullptr, service_limits(), "snapshot expiry service");
    const std::string payload = "snapshot-expiry-payload";
    const std::vector<std::string> destinations{receiver_actor.device_id};
    const auto operation = sender.create_local_file_or_throw(
        "snapshot-expiry.bin", payload.size(), anonsync::sha256_hex(payload),
        destinations);
    auto channel = sender_channel(receiver_actor, "snapshot-expiry-session");
    require_error(
        [&] {
            (void)service.claim_next_request_or_throw(
                channel, "snapshot-expiry-worker", 2U,
                payload_snapshot(folder, payload));
        },
        "post-payload-lookup dispatch attestation found its exact claim expired",
        "claim expiring after payload lookup escaped as an outbound frame");
    const auto expired = sender.snapshot_or_throw();
    require(expired.outbox.size() == 1U &&
                expired.outbox.front().operation_id == operation.operation_id &&
                expired.outbox.front().lease.dispatch_attempts == 1U &&
                !expired.outbox.front().lease.claim_id.empty() &&
                expired.outbox.front().lease.claimed_at_epoch == 770U &&
                expired.outbox.front().lease.lease_expires_at_epoch == 772U &&
                expired.outbox.front().lease.retry_release_provenance ==
                    anonsync::SyncReplicaOutboxRetryReleaseProvenance::None &&
                expired.outbox_time_high_water_epoch == 772U,
            "dispatch guard did not durably retain exact expired authority");

    clock->scripted_epochs.clear();
    clock->scripted_index = 0U;
    clock->epoch = 772U;
    const auto replacement = service.claim_next_request_or_throw(
        channel, "snapshot-expiry-replacement", 10U,
        payload_snapshot(folder, payload));
    require(replacement.has_value() &&
                replacement->request.evidence_request.dispatch_attempts == 2U &&
                replacement->request.evidence_request.claim_id !=
                    expired.outbox.front().lease.claim_id,
            "dispatch-expired snapshot claim did not require fresh attempt identity");
}

#if !defined(_WIN32)
void test_effect_path_policy_precedes_effect_and_evidence() {
    TempWorkspace workspace("anonsync-file-delivery-path-policy");
    const std::string folder = "folder-file-delivery-path-policy";
    const anonsync::SyncReplicaActor sender_actor{
        "device-file-delivery-path-sender", 9551U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-file-delivery-path-receiver", 9552U};
    const auto clock = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
    anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
    anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "path-policy sender", make_clock(clock));
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_db.db, folder, receiver_actor, owner_limits(),
        "path-policy receiver", make_clock(clock));
    anonsync::SyncReplicaFileEffectSqliteOwner effect(
        effect_db.db, folder, workspace.files, effect_limits(),
        "path-policy effects");
    anonsync::SyncReplicaFileDeliveryService sender_service(
        sender, nullptr, service_limits(), "path-policy sender service");
    anonsync::SyncReplicaFileDeliveryService receiver_service(
        receiver, &effect, service_limits(), "path-policy receiver service");
    const auto sender_link = sender_channel(receiver_actor, "path-policy-session");
    const auto receiver_link = receiver_channel(sender_actor, "path-policy-session");

    const std::uint64_t component_limit =
        observed_component_byte_limit(workspace.files);
    require(component_limit + 1U <=
                anonsync::kSyncManifestRelativePathMaxBytes,
            "delivery-test filename ceiling exceeds canonical path corpus");
    const std::string blocked_component(
        static_cast<std::size_t>(component_limit + 1U), 'p');
    const std::string payload = "path-policy-payload";
    const std::vector<std::string> destinations{receiver_actor.device_id};
    const auto operation = sender.create_local_file_or_throw(
        blocked_component, payload.size(), anonsync::sha256_hex(payload),
        destinations);
    clock->epoch = 450U;
    const auto outbound = sender_service.claim_next_request_or_throw(
        sender_link, "path-policy-worker", 10U,
        payload_snapshot(folder, payload));
    require(outbound.has_value(),
            "path-policy operation did not acquire sender attempt authority");

    const auto receiver_before = receiver.snapshot_or_throw();
    const auto effect_before = effect.snapshot_or_throw();
    const auto blocked = receiver_service.receive_request_or_throw(
        receiver_link, outbound->request_frame);
    require(blocked.stage_result ==
                anonsync::SyncReplicaFileEffectStageResult::
                    DestinationPathBlocked &&
                !blocked.evidence_delivery.has_value() &&
                !blocked.materialize_result.has_value() &&
                blocked.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::
                        EffectPathBlocked &&
                blocked.receipt.effect_id.empty() &&
                !blocked.receipt.evidence_receipt.has_value() &&
                blocked.receipt.receiver_effect_generation ==
                    effect_before.state_generation &&
                blocked.receipt.receiver_effect_cutpoint_digest ==
                    effect_before.cutpoint_digest,
            "local path denial fabricated effect, evidence, or changed-cutpoint authority");
    require(receiver.snapshot_or_throw() == receiver_before &&
                effect.snapshot_or_throw() == effect_before,
            "local path denial changed receiver evidence or effect state");
    require(std::filesystem::is_empty(workspace.files),
            "local path denial attempted visible namespace mutation");

    const auto duplicate_block = receiver_service.receive_request_or_throw(
        receiver_link, outbound->request_frame);
    require(duplicate_block.receipt_frame == blocked.receipt_frame &&
                duplicate_block.receipt_digest == blocked.receipt_digest &&
                duplicate_block.stage_result ==
                    anonsync::SyncReplicaFileEffectStageResult::
                        DestinationPathBlocked,
            "an exact retry did not reproduce the same no-mutation path-policy receipt");
    require(receiver.snapshot_or_throw() == receiver_before &&
                effect.snapshot_or_throw() == effect_before,
            "repeated local path denial accumulated durable receiver state");

    const auto sender_before = sender.snapshot_or_throw();
    require(sender_service.apply_receipt_or_throw(
                sender_link, outbound->request, blocked.receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::
                    ReceiverEffectPathBlocked,
            "sender did not classify the typed receiver path-policy denial");
    const auto sender_after = sender.snapshot_or_throw();
    require_exact_retry_release(
        sender_before, sender_after, operation.operation_id, 1U,
        450U, 510U,
        "path-policy receipt did not retain intent under exact local backoff");
}
#endif

void test_effect_capacity_precedes_evidence_and_kind_filter_skips_tombstone() {
    {
        TempWorkspace workspace("anonsync-file-delivery-capacity");
        const std::string folder = "folder-file-delivery-capacity";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-capacity-sender", 9601U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-capacity-receiver", 9602U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "capacity sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(),
            "capacity receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_db.db, folder, workspace.files, effect_limits(1U),
            "capacity effects");
        anonsync::SyncReplicaModel filler_model(
            folder, {"device-file-delivery-capacity-filler", 9603U},
            owner_limits().model);
        const std::string filler_payload = "fill";
        const auto filler = filler_model.create_local_file_or_throw(
            "fill.bin", filler_payload.size(),
            anonsync::sha256_hex(filler_payload));
        require(effect.stage_or_throw(filler, bytes(filler_payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
                "could not fill effect capacity for boundary test");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, service_limits(), "capacity sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, service_limits(), "capacity receiver service");
        const auto sender_link = sender_channel(receiver_actor, "capacity-session");
        const auto receiver_link = receiver_channel(sender_actor, "capacity-session");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string payload = "blocked";
        const auto operation = sender.create_local_file_or_throw(
            "blocked.bin", payload.size(), anonsync::sha256_hex(payload),
            destinations);
        clock->epoch = 500U;
        const auto outbound = sender_service.claim_next_request_or_throw(
            sender_link, "capacity-worker", 10U,
            payload_snapshot(folder, payload));
        require(outbound.has_value(),
                "effect-capacity operation did not acquire sender claim");
        const auto receiver_before = receiver.snapshot_or_throw();
        const auto effect_before = effect.snapshot_or_throw();
        const auto blocked = receiver_service.receive_request_or_throw(
            receiver_link, outbound->request_frame);
        require(blocked.stage_result ==
                    anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                    blocked.capacity_block.has_value() &&
                    !blocked.evidence_delivery.has_value() &&
                    !blocked.materialize_result.has_value() &&
                    blocked.receipt.disposition ==
                        anonsync::SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked &&
                    blocked.receipt.effect_id.empty() &&
                    !blocked.receipt.evidence_receipt.has_value(),
                "effect capacity block fabricated downstream authority");
        require(
            blocked.capacity_block->constraint ==
                    anonsync::SyncReplicaFileEffectCapacityConstraint::
                        FolderEffectCount &&
                blocked.capacity_block->state_generation ==
                    effect_before.state_generation &&
                blocked.capacity_block->cutpoint_digest ==
                    effect_before.cutpoint_digest &&
                blocked.capacity_block->effects ==
                    anonsync::SyncReplicaResourceBudget{1U, 1U, 1U} &&
                blocked.capacity_block->effects.would_exceed() &&
                !blocked.capacity_block->retained_payload_bytes.would_exceed() &&
                blocked.capacity_block->actor_usage.actor == sender_actor &&
                blocked.capacity_block->actor_usage.retained_effects == 0U &&
                blocked.capacity_block->device_usage.device_id ==
                    sender_actor.device_id &&
                blocked.capacity_block->device_usage.retained_effects == 0U,
            "receiver-local capacity diagnostic was not bound to the exact pre-evidence effect cutpoint");
        require(receiver.snapshot_or_throw() == receiver_before &&
                    effect.snapshot_or_throw() == effect_before,
                "effect capacity block changed evidence or effect cutpoint");
        const auto sender_before = sender.snapshot_or_throw();
        require(sender_service.apply_receipt_or_throw(
                    sender_link, outbound->request, blocked.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::ReceiverEffectCapacityBlocked,
                "effect capacity receipt was not classified as nonterminal");
        require_exact_retry_release(
            sender_before, sender.snapshot_or_throw(), operation.operation_id,
            1U, 500U, 505U,
            "effect-capacity receipt did not retain intent under exact local backoff");
    }

    {
        TempWorkspace workspace("anonsync-file-delivery-device-capacity");
        const std::string folder =
            "folder-file-delivery-device-capacity";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-device-capacity-sender", 9651U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-device-capacity-receiver", 9652U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "device capacity sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(),
            "device capacity receiver", make_clock(clock));
        auto isolated_limits = effect_limits(64U);
        isolated_limits.max_effects_per_device = 1U;
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_db.db, folder, workspace.files, isolated_limits,
            "device capacity effects");

        // Fill only this sender device's quota through an older actor epoch.
        // The folder remains nearly empty, proving that the rejection is not
        // an aggregate-capacity alias and that actor rotation cannot evade it.
        anonsync::SyncReplicaModel older_epoch_model(
            folder, {sender_actor.device_id, 9650U}, owner_limits().model);
        const std::string filler_payload = "older-epoch";
        const auto filler = older_epoch_model.create_local_file_or_throw(
            "older-epoch.bin", filler_payload.size(),
            anonsync::sha256_hex(filler_payload));
        require(effect.stage_or_throw(filler, bytes(filler_payload)) ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted,
                "could not fill the sender device quota through an older epoch");

        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, service_limits(),
            "device capacity sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, service_limits(),
            "device capacity receiver service");
        const auto sender_link =
            sender_channel(receiver_actor, "device-capacity-session");
        const auto receiver_link =
            receiver_channel(sender_actor, "device-capacity-session");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string payload = "isolated-block";
        const auto operation = sender.create_local_file_or_throw(
            "isolated.bin", payload.size(), anonsync::sha256_hex(payload),
            destinations);
        clock->epoch = 550U;
        const auto outbound = sender_service.claim_next_request_or_throw(
            sender_link, "device-capacity-worker", 10U,
            payload_snapshot(folder, payload));
        require(outbound.has_value(),
                "device-capacity operation did not acquire sender claim");
        const auto receiver_before = receiver.snapshot_or_throw();
        const auto effect_before = effect.snapshot_or_throw();
        const auto blocked = receiver_service.receive_request_or_throw(
            receiver_link, outbound->request_frame);
        require(
            blocked.stage_result ==
                    anonsync::SyncReplicaFileEffectStageResult::CapacityBlocked &&
                blocked.capacity_block.has_value() &&
                blocked.capacity_block->constraint ==
                    anonsync::SyncReplicaFileEffectCapacityConstraint::
                        DeviceEffectCount &&
                !blocked.capacity_block->effects.would_exceed() &&
                blocked.capacity_block->effects ==
                    anonsync::SyncReplicaResourceBudget{1U, 1U, 64U} &&
                blocked.capacity_block->device_effects ==
                    anonsync::SyncReplicaResourceBudget{1U, 1U, 1U} &&
                blocked.capacity_block->device_effects.would_exceed() &&
                blocked.capacity_block->actor_usage.actor == sender_actor &&
                blocked.capacity_block->actor_usage.retained_effects == 0U &&
                blocked.capacity_block->device_usage.device_id ==
                    sender_actor.device_id &&
                blocked.capacity_block->device_usage.actor_epochs == 1U &&
                blocked.capacity_block->device_usage.retained_effects == 1U,
            "device-local quota did not aggregate actor epochs independently of folder capacity");
        require(
            !blocked.evidence_delivery.has_value() &&
                !blocked.materialize_result.has_value() &&
                blocked.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::
                        EffectCapacityBlocked &&
                blocked.receipt.effect_id.empty() &&
                !blocked.receipt.evidence_receipt.has_value(),
            "device-local detail escaped into downstream evidence or effect authority");
        require(receiver.snapshot_or_throw() == receiver_before &&
                    effect.snapshot_or_throw() == effect_before,
                "device-capacity block changed receiver authority");
        const auto sender_before = sender.snapshot_or_throw();
        require(sender_service.apply_receipt_or_throw(
                    sender_link, outbound->request, blocked.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::
                        ReceiverEffectCapacityBlocked,
                "generic wire receipt did not classify device isolation as nonterminal");
        require_exact_retry_release(
            sender_before, sender.snapshot_or_throw(), operation.operation_id,
            1U, 550U, 555U,
            "device-capacity receipt did not release the exact attempt under local policy");
    }

    {
        TempWorkspace workspace("anonsync-file-delivery-kind-filter");
        const std::string folder = "folder-file-delivery-kind-filter";
        const anonsync::SyncReplicaActor sender_actor{
            "device-file-delivery-kind-sender", 9701U};
        const anonsync::SyncReplicaActor receiver_actor{
            "device-file-delivery-kind-receiver", 9702U};
        const auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb sender_db = open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_db = open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_db = open_database(workspace.effect_db);
        anonsync::SyncReplicaSqliteOwner sender(
            sender_db.db, folder, sender_actor, owner_limits(),
            "kind sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_db.db, folder, receiver_actor, owner_limits(),
            "kind receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_db.db, folder, workspace.files, effect_limits(),
            "kind effects");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, service_limits(), "kind sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, service_limits(), "kind receiver service");
        const auto sender_link = sender_channel(receiver_actor, "kind-session");
        const auto receiver_link = receiver_channel(sender_actor, "kind-session");
        const std::vector<std::string> destinations{receiver_actor.device_id};
        const std::string payload = "file-before-tombstone";
        const auto file = sender.create_local_file_or_throw(
            "kept.bin", payload.size(), anonsync::sha256_hex(payload),
            destinations);
        const auto tombstone = sender.create_local_tombstone_or_throw(
            "deleted.bin", destinations);
        clock->epoch = 600U;
        const auto outbound = sender_service.claim_next_request_or_throw(
            sender_link, "kind-worker", 10U,
            payload_snapshot(folder, payload));
        require(outbound.has_value() &&
                    outbound->request.evidence_request.operation == file,
                "file-only claimant leased an unsupported tombstone");
        const auto inbound = receiver_service.receive_request_or_throw(
            receiver_link, outbound->request_frame);
        clock->epoch = 601U;
        require(sender_service.apply_receipt_or_throw(
                    sender_link, outbound->request, inbound.receipt_frame) ==
                    anonsync::SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled,
                "kind-filtered file did not settle");
        const auto remaining = sender.snapshot_or_throw();
        require(remaining.outbox.size() == 1U &&
                    remaining.outbox.front().operation_id == tombstone.operation_id,
                "file-only settlement consumed or lost the tombstone intent");
        require(!sender_service.claim_next_request_or_throw(
                     sender_link, "kind-worker-none", 10U,
                     payload_snapshot(folder, payload))
                     .has_value(),
                "file-only claimant returned a tombstone after files were exhausted");
    }
}

}  // namespace

int main() {
    try {
        test_effect_terminal_delivery_duplicate_and_create_new_boundary();
        test_pending_dependency_stages_once_then_publishes_on_retry();
        test_ambiguous_publication_survives_three_owner_restart();
        test_live_authority_and_payload_snapshot_preflight_precede_claim_mutation();
        test_payload_snapshot_validation_selection_and_exact_mismatch_release();
#if !defined(_WIN32)
        test_durable_payload_store_selection_and_exact_release();
#endif
        test_retry_policy_validation_precedes_durable_authority();
        test_post_snapshot_dispatch_guard_closes_clock_expiry();
#if !defined(_WIN32)
        test_effect_path_policy_precedes_effect_and_evidence();
#endif
        test_effect_capacity_precedes_evidence_and_kind_filter_skips_tombstone();
        std::cout << "sync replica file-delivery service tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica file-delivery service tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
