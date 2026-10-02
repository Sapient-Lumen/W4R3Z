#include "iotox/sync_multiwriter_service.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_subscriber.hpp"
#include "iotox/sync_digest.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-tree-v2-service-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        char *created = ::mkdtemp(bytes.data());
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0)
            throw std::runtime_error("chmod failed");
    }
    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

iotox::security::Sodium sodium() {
    auto loaded = iotox::security::Sodium::load();
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

iotox::security::DeviceIdentity
identity(const std::filesystem::path &path,
         const iotox::security::Sodium &crypto) {
    auto loaded =
        iotox::security::DeviceIdentity::load_or_create(path, crypto, true);
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

void make_directory(const std::filesystem::path &path) {
    if (!std::filesystem::create_directory(path) ||
        ::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0)
        throw std::runtime_error("private directory creation failed");
}

void write_file(const std::filesystem::path &path, std::string_view text) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("private file write failed");
}

std::string read_file(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    std::string result;
    std::getline(input, result, '\0');
    return result;
}

std::size_t regular_files_below(const std::filesystem::path &path) {
    std::error_code error;
    if (!std::filesystem::exists(path, error) || error) return 0U;
    std::size_t result = 0U;
    for (std::filesystem::recursive_directory_iterator iterator(path, error),
         end;
         !error && iterator != end; iterator.increment(error)) {
        if (iterator->is_regular_file(error) && !error) ++result;
    }
    if (error) throw std::runtime_error("recursive tree inspection failed");
    return result;
}

iotox::sync::NamespacePolicy
policy(const std::filesystem::path &root,
       const iotox::security::SigningPublicKey &left,
       const iotox::security::SigningPublicKey &right,
       std::uint64_t maximum_lanes = 1U) {
    iotox::sync::NamespacePolicy result;
    result.id = "field-notes";
    result.root = root.string();
    result.engine = iotox::sync::Engine::tree_v2;
    result.quotas.maximum_artifact_bytes = 1024U * 1024U;
    result.quotas.maximum_manifest_bytes = 256U * 1024U;
    result.quotas.maximum_store_bytes = 16U * 1024U * 1024U;
    result.quotas.maximum_staging_bytes = 2U * 1024U * 1024U;
    result.quotas.maximum_objects = 256U;
    result.quotas.maximum_retained_revisions = 8U;
    result.quotas.maximum_peers = 4U;
    result.quotas.maximum_lanes = maximum_lanes;
    result.quotas.maximum_outstanding_requests = 16U;
    result.writers = {left, right};
    result.subscribers = {left, right};
    std::sort(result.writers.begin(), result.writers.end());
    std::sort(result.subscribers.begin(), result.subscribers.end());
    return result;
}

iotox::sync::SyncPeerContext
context(const iotox::security::SigningPublicKey &remote,
        iotox::security::Capability capability) {
    iotox::sync::SyncPeerContext result;
    result.friend_number = 7U;
    result.online_epoch = 11U;
    result.authority_route_key.fill(0x61U);
    result.authority.initialized = true;
    result.authority.format = iotox::security::AuthorityLedgerFormat::v3;
    result.authority.ownership_epoch = 3U;
    result.authority.sequence = 5U;
    result.authority.tail_digest.fill(0x71U);
    result.peer_authority.friend_number = result.friend_number;
    result.peer_authority.online_epoch = result.online_epoch;
    result.peer_authority.connected = true;
    result.peer_authority.feature_negotiated = true;
    result.peer_authority.authority_v2_negotiated = true;
    result.peer_authority.authority_v3_negotiated = true;
    result.peer_authority.verifier_state =
        iotox::security::AuthorityVerifierState::authorized;
    result.peer_authority.remote_authorized = true;
    result.peer_authority.remote_principal = remote;
    result.peer_authority.remote_capabilities =
        static_cast<std::uint64_t>(capability);
    result.peer_authority.local_authority_format = result.authority.format;
    result.peer_authority.local_authority_epoch =
        result.authority.ownership_epoch;
    result.peer_authority.local_authority_sequence = result.authority.sequence;
    result.peer_authority.local_authority_tail_digest =
        result.authority.tail_digest;
    result.transfer_carrier.route_key = result.authority_route_key;
    result.transfer_carrier.worker_id = result.online_epoch;
    result.transfer_carrier.friend_number = result.friend_number;
    result.transfer_carrier.online_epoch = result.online_epoch;
    result.tree_transfer_negotiated = true;
    return result;
}

iotox::sync::SyncPeerContext numbered_context(
    const iotox::security::SigningPublicKey &remote,
    iotox::security::Capability capability, std::uint32_t friend_number,
    std::uint64_t online_epoch, std::uint8_t route_byte) {
    auto result = context(remote, capability);
    result.friend_number = friend_number;
    result.online_epoch = online_epoch;
    result.authority_route_key.fill(route_byte);
    result.peer_authority.friend_number = friend_number;
    result.peer_authority.online_epoch = online_epoch;
    result.transfer_carrier.route_key = result.authority_route_key;
    result.transfer_carrier.worker_id = online_epoch;
    result.transfer_carrier.friend_number = friend_number;
    result.transfer_carrier.online_epoch = online_epoch;
    return result;
}

class TransferBridge final {
  public:
    struct Pending {
        iotox::FileId file_id{};
        std::filesystem::path source;
        std::filesystem::path destination;
        std::uint32_t file_number{0U};
        std::uint64_t bytes{0U};
    };

    iotox::Result<iotox::FileTransferRecord>
    send(const iotox::sync::SyncTransferCarrier &carrier,
         const std::filesystem::path &source, const iotox::FileId &file_id) {
        std::error_code error;
        const std::uintmax_t size = std::filesystem::file_size(source, error);
        if (error || size > std::numeric_limits<std::uint64_t>::max())
            return iotox::Status{iotox::ErrorCode::io_error,
                                 "bridge source size failed"};
        Pending pending{file_id,
                        source,
                        {},
                        next_file_number_++,
                        static_cast<std::uint64_t>(size)};
        pending_.push_back(pending);
        iotox::FileTransferRecord record;
        record.direction = iotox::FileTransferDirection::outgoing;
        record.state = iotox::FileTransferState::offered;
        record.friend_number = carrier.friend_number;
        record.file_number = pending.file_number;
        record.file_size = pending.bytes;
        record.file_id = file_id;
        record.has_file_id = true;
        record.local_path = source;
        return record;
    }

    iotox::Result<iotox::FileTransferRecord>
    offer(const iotox::FileId &file_id, std::uint32_t friend_number) const {
        const auto found = std::find_if(pending_.begin(), pending_.end(),
                                        [&file_id](const Pending &entry) {
                                            return entry.file_id == file_id;
                                        });
        if (found == pending_.end())
            return iotox::Status{iotox::ErrorCode::not_found, "offer absent"};
        iotox::FileTransferRecord record;
        record.direction = iotox::FileTransferDirection::incoming;
        record.state = iotox::FileTransferState::offered;
        record.friend_number = friend_number;
        record.file_number = found->file_number;
        record.file_size = found->bytes;
        record.file_id = file_id;
        record.has_file_id = true;
        return record;
    }

    iotox::Result<iotox::FileTransferRecord>
    receive(const iotox::sync::SyncTransferCarrier &carrier,
            std::uint32_t file_number,
            const std::filesystem::path &destination) {
        auto found = find(file_number);
        if (found == pending_.end())
            return iotox::Status{iotox::ErrorCode::not_found, "receive absent"};
        std::error_code error;
        const bool copied =
            std::filesystem::copy_file(found->source, destination, error);
        if (!copied || error ||
            ::chmod(destination.c_str(), static_cast<mode_t>(0600)) != 0) {
            return iotox::Status{iotox::ErrorCode::io_error,
                                 "receive copy failed"};
        }
        found->destination = destination;
        iotox::FileTransferRecord record;
        record.direction = iotox::FileTransferDirection::incoming;
        record.state = iotox::FileTransferState::active;
        record.friend_number = carrier.friend_number;
        record.file_number = file_number;
        record.file_size = found->bytes;
        record.file_id = found->file_id;
        record.has_file_id = true;
        record.local_path = destination;
        return record;
    }

    iotox::Result<iotox::FileTransferRecord>
    terminal(std::uint32_t file_number, std::uint32_t friend_number) const {
        const auto found =
            std::find_if(pending_.begin(), pending_.end(),
                         [file_number](const Pending &entry) {
                             return entry.file_number == file_number;
                         });
        if (found == pending_.end() || found->destination.empty())
            return iotox::Status{iotox::ErrorCode::not_found,
                                 "terminal absent"};
        iotox::FileTransferRecord record;
        record.direction = iotox::FileTransferDirection::incoming;
        record.state = iotox::FileTransferState::completed;
        record.friend_number = friend_number;
        record.file_number = file_number;
        record.file_size = found->bytes;
        record.position = found->bytes;
        record.file_id = found->file_id;
        record.has_file_id = true;
        record.local_path = found->destination;
        return record;
    }

    iotox::Status cancel(std::uint32_t file_number) {
        const auto found = find(file_number);
        if (found != pending_.end()) pending_.erase(found);
        ++cancellations_;
        return iotox::Status::success();
    }

    [[nodiscard]] std::uint64_t cancellations() const noexcept {
        return cancellations_;
    }

  private:
    std::vector<Pending>::iterator find(std::uint32_t file_number) {
        return std::find_if(pending_.begin(), pending_.end(),
                            [file_number](const Pending &entry) {
                                return entry.file_number == file_number;
                            });
    }

    std::vector<Pending> pending_;
    std::uint32_t next_file_number_{41U};
    std::uint64_t cancellations_{0U};
};

iotox::FileId numbered_file_id(std::uint64_t value) {
    iotox::FileId result{};
    for (std::size_t index = 0U; index < sizeof(value); ++index) {
        result[index] = static_cast<std::uint8_t>(value & 0xffU);
        value >>= 8U;
    }
    return result;
}

struct PeerServices {
    std::unique_ptr<iotox::sync::TreeV2PublisherService> publisher;
    std::unique_ptr<iotox::sync::TreeV2SubscriberService> subscriber;
};

PeerServices services(iotox::sync::NamespaceRegistry &registry,
                      TransferBridge &bridge,
                      const iotox::security::DeviceIdentity &local,
                      const iotox::security::Sodium &crypto,
                      std::uint64_t &next_message, std::uint64_t &next_file,
                      std::size_t maximum_lanes = 1U) {
    iotox::sync::TreeV2PublisherSeams publisher_seams;
    publisher_seams.send_object =
        [&bridge](const auto &carrier, const auto &path, const auto &file_id) {
            return bridge.send(carrier, path, file_id);
        };
    publisher_seams.make_message_id =
        [&next_message]() -> iotox::Result<std::uint64_t> {
        return next_message++;
    };
    iotox::sync::TreeV2PublisherService::Config publisher_config;
    publisher_config.maximum_replays = 1U;
    publisher_config.sodium = &crypto;

    iotox::sync::TreeV2SubscriberSeams subscriber_seams;
    subscriber_seams.make_message_id =
        [&next_message]() -> iotox::Result<std::uint64_t> {
        return next_message++;
    };
    subscriber_seams.make_file_id =
        [&next_file]() -> iotox::Result<iotox::FileId> {
        return numbered_file_id(next_file++);
    };
    subscriber_seams.receive_to_path = [&bridge](const auto &carrier,
                                                 std::uint32_t file_number,
                                                 const auto &path) {
        return bridge.receive(carrier, file_number, path);
    };
    subscriber_seams.cancel_transfer = [&bridge](const auto &,
                                                 std::uint32_t file_number) {
        return bridge.cancel(file_number);
    };
    iotox::sync::TreeV2SubscriberService::Config subscriber_config;
    subscriber_config.maximum_lanes = maximum_lanes;
    subscriber_config.identity = &local;
    subscriber_config.sodium = &crypto;
    return {std::make_unique<iotox::sync::TreeV2PublisherService>(
                registry, std::move(publisher_seams), publisher_config),
            std::make_unique<iotox::sync::TreeV2SubscriberService>(
                registry, std::move(subscriber_seams), subscriber_config)};
}

iotox::sync::TreeV2PullSnapshot
transfer_frontier(iotox::sync::TreeV2PublisherService &publisher,
                  iotox::sync::TreeV2SubscriberService &subscriber,
                  TransferBridge &bridge,
                  const iotox::sync::SyncPeerContext &publisher_context,
                  const iotox::sync::SyncPeerContext &subscriber_context,
                  const std::filesystem::path &worktree) {
    auto inventory =
        subscriber.begin_pull(publisher_context, "field-notes", worktree);
    IOTOX_CHECK_MSG(inventory.ok(), inventory.status().message());
    auto served_inventory =
        publisher.handle(subscriber_context, inventory.value().frame);
    IOTOX_CHECK_MSG(served_inventory.ok(), served_inventory.status().message());
    auto requests = subscriber.handle_inventory_result(
        publisher_context, served_inventory.value().response);
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    for (std::size_t step = 0U; step < 1024U && !requests.value().empty();
         ++step) {
        IOTOX_CHECK(requests.value().size() == 1U);
        const auto request = requests.value().front().frame;
        auto body = iotox::sync::decode_tree_v2_object_request(request.payload);
        IOTOX_CHECK(body.ok());
        auto served = publisher.handle(subscriber_context, request);
        IOTOX_CHECK_MSG(served.ok(), served.status().message());
        IOTOX_CHECK(served.value().file_offered);
        auto offer = bridge.offer(body.value().transfer_id,
                                  publisher_context.friend_number);
        IOTOX_CHECK(offer.ok());
        const auto result = subscriber.handle_object_result(
            publisher_context, served.value().response);
        IOTOX_CHECK_MSG(result.ok(), result.status().message());
        IOTOX_CHECK(result.value().empty());
        auto admitted =
            subscriber.handle_offer(publisher_context, offer.value());
        IOTOX_CHECK_MSG(admitted.ok() && admitted.value(),
                        admitted.status().message());
        auto terminal = bridge.terminal(offer.value().file_number,
                                        publisher_context.friend_number);
        IOTOX_CHECK(terminal.ok());
        requests = subscriber.handle_terminal(
            publisher_context, terminal.value(),
            iotox::routes::WorkerTransferOutcome::completed,
            iotox::ErrorCode::ok);
        IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    }
    IOTOX_CHECK(requests.ok() && requests.value().empty());
    const auto snapshots = subscriber.snapshot();
    IOTOX_CHECK(!snapshots.empty());
    IOTOX_CHECK(snapshots.back().state ==
                iotox::sync::TreeV2PullState::complete);
    return snapshots.back();
}

} // namespace

IOTOX_TEST("tree-v2 subscriber pipelines bounded exact object lanes") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const auto left_root = temporary.path() / "left-root";
    const auto right_root = temporary.path() / "right-root";
    const auto left_tree = temporary.path() / "left-tree";
    const auto right_tree = temporary.path() / "right-tree";
    make_directory(left_root);
    make_directory(right_root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "a.txt", "alpha");
    write_file(left_tree / "b.txt", "bravo");
    write_file(left_tree / "c.txt", "charlie");
    write_file(left_tree / "d.txt", "delta");
    const auto left_policy =
        policy(left_root, left.public_key(), right.public_key(), 4U);
    const auto right_policy =
        policy(right_root, left.public_key(), right.public_key(), 4U);
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }

    iotox::sync::NamespaceRegistry left_registry;
    iotox::sync::NamespaceRegistry right_registry;
    IOTOX_CHECK(left_registry.replace({left_policy}).ok());
    IOTOX_CHECK(right_registry.replace({right_policy}).ok());
    TransferBridge bridge;
    std::uint64_t left_message = 1000U;
    std::uint64_t right_message = 2000U;
    std::uint64_t left_file = 10U;
    std::uint64_t right_file = 100U;
    auto left_services =
        services(left_registry, bridge, left, crypto, left_message, left_file,
                 4U);
    auto right_services = services(right_registry, bridge, right, crypto,
                                   right_message, right_file, 4U);
    const auto left_as_publisher =
        context(left.public_key(), iotox::security::Capability::sync_publish);
    const auto right_as_subscriber = context(
        right.public_key(), iotox::security::Capability::sync_subscribe);

    auto inventory = right_services.subscriber->begin_pull(
        left_as_publisher, "field-notes", right_tree);
    IOTOX_CHECK_MSG(inventory.ok(), inventory.status().message());
    auto served_inventory =
        left_services.publisher->handle(right_as_subscriber,
                                        inventory.value().frame);
    IOTOX_CHECK_MSG(served_inventory.ok(),
                    served_inventory.status().message());
    auto requests = right_services.subscriber->handle_inventory_result(
        left_as_publisher, served_inventory.value().response);
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    IOTOX_CHECK(requests.value().size() == 1U);

    const auto serve_one =
        [&](const iotox::sync::TreeV2Dispatch &dispatch)
        -> iotox::Result<std::vector<iotox::sync::TreeV2Dispatch>> {
        auto body =
            iotox::sync::decode_tree_v2_object_request(dispatch.frame.payload);
        if (!body) return body.status();
        auto served = left_services.publisher->handle(right_as_subscriber,
                                                      dispatch.frame);
        if (!served) return served.status();
        if (!served.value().file_offered) {
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test publisher did not offer a file"};
        }
        auto offer = bridge.offer(body.value().transfer_id,
                                  left_as_publisher.friend_number);
        if (!offer) return offer.status();
        auto result = right_services.subscriber->handle_object_result(
            left_as_publisher, served.value().response);
        if (!result) return result.status();
        auto admitted =
            right_services.subscriber->handle_offer(left_as_publisher,
                                                    offer.value());
        if (!admitted) return admitted.status();
        if (!admitted.value()) {
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test offer was not admitted"};
        }
        auto terminal = bridge.terminal(offer.value().file_number,
                                        left_as_publisher.friend_number);
        if (!terminal) return terminal.status();
        return right_services.subscriber->handle_terminal(
            left_as_publisher, terminal.value(),
            iotox::routes::WorkerTransferOutcome::completed,
            iotox::ErrorCode::ok);
    };

    requests = serve_one(requests.value().front());
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    IOTOX_CHECK(requests.value().size() == 1U);
    requests = serve_one(requests.value().front());
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    IOTOX_CHECK(requests.value().size() == 4U);
    {
        const auto snapshots = right_services.subscriber->snapshot();
        IOTOX_CHECK(!snapshots.empty());
        const auto &snapshot = snapshots.back();
        IOTOX_CHECK(snapshot.active_lanes == 4U);
        IOTOX_CHECK(snapshot.lane_bindings.size() == 4U);
        IOTOX_CHECK(!snapshot.active_file_id);
        IOTOX_CHECK(!snapshot.active_file_number);
        IOTOX_CHECK(snapshot.requested_objects == 6U);
    }

    const auto file_requests = requests.value();
    for (std::size_t index = 0U; index < file_requests.size(); ++index) {
        requests = serve_one(file_requests[index]);
        IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
        IOTOX_CHECK(requests.value().empty());
        if (index + 1U < file_requests.size()) {
            const auto staged = right_services.subscriber->snapshot();
            IOTOX_CHECK(!staged.empty());
            IOTOX_CHECK(staged.back().staged_file_objects == index + 1U);
            IOTOX_CHECK(staged.back().file_commit_batches == 0U);
            IOTOX_CHECK(staged.back().largest_file_commit_batch == 0U);
            IOTOX_CHECK(staged.back().committed_objects == 2U);
        }
    }
    const auto complete = right_services.subscriber->snapshot();
    IOTOX_CHECK(!complete.empty());
    IOTOX_CHECK(complete.back().state ==
                iotox::sync::TreeV2PullState::complete);
    IOTOX_CHECK(complete.back().staged_file_objects == 0U);
    IOTOX_CHECK(complete.back().file_commit_batches == 1U);
    IOTOX_CHECK(complete.back().largest_file_commit_batch == 4U);
    IOTOX_CHECK(complete.back().cas_full_inventory_scans == 2U);
    IOTOX_CHECK(complete.back().cas_inventory_objects_inspected == 4U);
    IOTOX_CHECK(complete.back().committed_objects == 6U);
    IOTOX_CHECK(complete.back().reconciliation.projection_files == 4U);
    IOTOX_CHECK(complete.back().reconciliation.projection_bytes == 22U);
    IOTOX_CHECK(complete.back().reconciliation.projection_conflict_files ==
                0U);
    IOTOX_CHECK(complete.back()
                    .reconciliation.projection_conflict_tombstones == 0U);
    const auto batch_statistics = right_services.subscriber->statistics();
    IOTOX_CHECK(batch_statistics.file_commit_batches == 1U);
    IOTOX_CHECK(batch_statistics.file_objects_committed == 4U);
    IOTOX_CHECK(batch_statistics.largest_file_commit_batch == 4U);
    IOTOX_CHECK(batch_statistics.cas_full_inventory_scans == 2U);
    IOTOX_CHECK(batch_statistics.cas_inventory_objects_inspected == 4U);
    IOTOX_CHECK(batch_statistics.retired_offer_evictions == 0U);
    IOTOX_CHECK(read_file(right_tree / "a.txt") == "alpha");
    IOTOX_CHECK(read_file(right_tree / "b.txt") == "bravo");
    IOTOX_CHECK(read_file(right_tree / "c.txt") == "charlie");
    IOTOX_CHECK(read_file(right_tree / "d.txt") == "delta");

    // The first unchanged pull after a projection exchange warms the
    // subscriber-owned source digest cache. The next unchanged pull should
    // keep observing the source tree, but reuse unchanged file identities
    // instead of hashing every file again.
    const auto warmed = transfer_frontier(
        *left_services.publisher, *right_services.subscriber, bridge,
        left_as_publisher, right_as_subscriber, right_tree);
    IOTOX_CHECK(warmed.reconciliation.source_hashed_file_digests == 4U);
    IOTOX_CHECK(warmed.reconciliation.source_reused_file_digests == 0U);
    const auto reused = transfer_frontier(
        *left_services.publisher, *right_services.subscriber, bridge,
        left_as_publisher, right_as_subscriber, right_tree);
    IOTOX_CHECK(reused.reconciliation.source_hashed_file_digests == 0U);
    IOTOX_CHECK(reused.reconciliation.source_reused_file_digests == 4U);

    // A cancellation can overtake a Tox file-offer callback. Retain the exact
    // FileId long enough to claim and cancel that late transport offer instead
    // of leaking it into the generic user-visible file lane.
    auto missing = iotox::sync::hash_sync_file_sha256(right_tree / "a.txt");
    IOTOX_CHECK(missing.ok());
    IOTOX_CHECK(std::filesystem::remove(
        iotox::sync::tree_v2_object_path(right_policy, missing.value())));
    auto cancelled_inventory = right_services.subscriber->begin_pull(
        left_as_publisher, "field-notes", right_tree);
    IOTOX_CHECK(cancelled_inventory.ok());
    const std::uint64_t cancelled_job =
        cancelled_inventory.value().frame.message_id;
    auto cancelled_served = left_services.publisher->handle(
        right_as_subscriber, cancelled_inventory.value().frame);
    IOTOX_CHECK(cancelled_served.ok());
    auto cancelled_requests = right_services.subscriber->handle_inventory_result(
        left_as_publisher, cancelled_served.value().response);
    IOTOX_CHECK(cancelled_requests.ok());
    IOTOX_CHECK(cancelled_requests.value().size() == 1U);
    auto late_body = iotox::sync::decode_tree_v2_object_request(
        cancelled_requests.value().front().frame.payload);
    IOTOX_CHECK(late_body.ok());
    auto late_served = left_services.publisher->handle(
        right_as_subscriber, cancelled_requests.value().front().frame);
    IOTOX_CHECK(late_served.ok() && late_served.value().file_offered);
    auto late_offer = bridge.offer(late_body.value().transfer_id,
                                   left_as_publisher.friend_number);
    IOTOX_CHECK(late_offer.ok());
    IOTOX_CHECK(right_services.subscriber->cancel_pull(cancelled_job).ok());
    IOTOX_CHECK(
        right_services.subscriber->statistics().retired_offer_ids == 1U);
    const std::uint64_t cancelled_before = bridge.cancellations();
    auto late_claimed = right_services.subscriber->handle_offer(
        left_as_publisher, late_offer.value());
    IOTOX_CHECK(late_claimed.ok() && late_claimed.value());
    const auto late_statistics = right_services.subscriber->statistics();
    IOTOX_CHECK(late_statistics.late_offers_cancelled == 1U);
    IOTOX_CHECK(late_statistics.retired_offer_ids == 0U);
    IOTOX_CHECK(bridge.cancellations() == cancelled_before + 1U);
}

IOTOX_TEST(
    "tree-v2 peer services converge writable changes in both directions") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const auto left_root = temporary.path() / "left-root";
    const auto right_root = temporary.path() / "right-root";
    const auto left_tree = temporary.path() / "left-tree";
    const auto right_tree = temporary.path() / "right-tree";
    make_directory(left_root);
    make_directory(right_root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "note.txt", "left generation one");
    const auto left_policy =
        policy(left_root, left.public_key(), right.public_key());
    const auto right_policy =
        policy(right_root, left.public_key(), right.public_key());
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }

    iotox::sync::NamespaceRegistry left_registry;
    iotox::sync::NamespaceRegistry right_registry;
    IOTOX_CHECK(left_registry.replace({left_policy}).ok());
    IOTOX_CHECK(right_registry.replace({right_policy}).ok());
    TransferBridge bridge;
    std::uint64_t left_message = 1000U;
    std::uint64_t right_message = 2000U;
    std::uint64_t left_file = 10U;
    std::uint64_t right_file = 100U;
    auto left_services =
        services(left_registry, bridge, left, crypto, left_message, left_file);
    auto right_services = services(right_registry, bridge, right, crypto,
                                   right_message, right_file);
    const auto left_as_publisher =
        context(left.public_key(), iotox::security::Capability::sync_publish);
    const auto right_as_subscriber = context(
        right.public_key(), iotox::security::Capability::sync_subscribe);
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(left_services.publisher->snapshot().replay_evictions > 0U);
    IOTOX_CHECK(read_file(right_tree / "note.txt") == "left generation one");
    IOTOX_CHECK(left_services.publisher
                    ->retire_namespace_replays_for_additive_share("other") ==
                0U);
    IOTOX_CHECK(left_services.publisher
                    ->retire_namespace_replays_for_additive_share(
                        left_policy.id) == 1U);
    IOTOX_CHECK(left_services.publisher->snapshot().retained_replays == 0U);

    // A process crash can leave only canonically named private staging files.
    // The next namespace transaction removes those files without touching
    // unrelated entries in the private incoming directory.
    const auto incoming = right_root / "tree-v2" / "incoming";
    write_file(incoming / ".receive-0000000000000001.part", "stale");
    write_file(incoming /
                   ".iotox-.receive-0000000000000002.part.part-Ab3xY9",
               "interrupted transport");
    write_file(incoming / "operator-note", "preserve");
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(
        !std::filesystem::exists(incoming / ".receive-0000000000000001.part"));
    IOTOX_CHECK(!std::filesystem::exists(
        incoming / ".iotox-.receive-0000000000000002.part.part-Ab3xY9"));
    IOTOX_CHECK(read_file(incoming / "operator-note") == "preserve");

    write_file(right_tree / "note.txt", "right writes back");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(right_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            right_policy, right_tree, right, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }
    const auto right_as_publisher =
        context(right.public_key(), iotox::security::Capability::sync_publish);
    const auto left_as_subscriber =
        context(left.public_key(), iotox::security::Capability::sync_subscribe);
    transfer_frontier(*right_services.publisher, *left_services.subscriber,
                      bridge, right_as_publisher, left_as_subscriber,
                      left_tree);
    IOTOX_CHECK(read_file(left_tree / "note.txt") == "right writes back");

    // Give the right side the latest visible left frontier, disconnect both
    // sides conceptually, and create unequal writes without either observing
    // the other's new branch.
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    write_file(left_tree / "note.txt", "concurrent left");
    write_file(right_tree / "note.txt", "concurrent right");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto resolved = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(resolved.ok(), resolved.status().message());
    }
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(right_policy);
        IOTOX_CHECK(transaction.ok());
        IOTOX_CHECK(
            iotox::sync::reconcile_tree_v2_workspace(
                right_policy, right_tree, right, crypto, transaction.value())
                .ok());
    }
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    transfer_frontier(*right_services.publisher, *left_services.subscriber,
                      bridge, right_as_publisher, left_as_subscriber,
                      left_tree);
    IOTOX_CHECK(read_file(left_tree / "note.txt") ==
                read_file(right_tree / "note.txt"));
    IOTOX_CHECK(regular_files_below(left_tree / ".iotox-conflicts" /
                                    "by-origin") >= 1U);
    IOTOX_CHECK(regular_files_below(right_tree / ".iotox-conflicts" /
                                    "by-origin") >= 1U);

    // One ordinary edit made after both candidates are visible causally
    // resolves the conflict. A subsequent deletion and empty file travel
    // independently.
    write_file(left_tree / "note.txt", "resolved after both were visible");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto resolved = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(resolved.ok(), resolved.status().message());
    }
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(read_file(right_tree / "note.txt") ==
                "resolved after both were visible");
    IOTOX_CHECK(regular_files_below(right_tree / ".iotox-conflicts" /
                                    "by-origin") == 0U);

    IOTOX_CHECK(std::filesystem::remove(left_tree / "note.txt"));
    write_file(left_tree / "empty.bin", "");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        IOTOX_CHECK(
            iotox::sync::reconcile_tree_v2_workspace(
                left_policy, left_tree, left, crypto, transaction.value())
                .ok());
    }
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(!std::filesystem::exists(right_tree / "note.txt"));
    IOTOX_CHECK(std::filesystem::file_size(right_tree / "empty.bin") == 0U);
}

IOTOX_TEST(
    "tree-v2 sparse pull retains full metadata and widens custody on demand") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const auto left_root = temporary.path() / "left-root";
    const auto right_root = temporary.path() / "right-root";
    const auto left_tree = temporary.path() / "left-tree";
    const auto right_tree = temporary.path() / "right-tree";
    make_directory(left_root);
    make_directory(right_root);
    make_directory(left_tree);
    make_directory(right_tree);
    make_directory(left_tree / "kept");
    make_directory(left_tree / "omitted");
    make_directory(right_tree / "omitted");
    write_file(left_tree / "kept" / "note.txt", "selected bytes");
    write_file(left_tree / "omitted" / "secret.txt", "deferred bytes");
    write_file(right_tree / "omitted" / "local.txt", "preserved local");
    auto deferred_digest =
        iotox::sync::hash_sync_file_sha256(left_tree / "omitted" /
                                           "secret.txt");
    IOTOX_CHECK(deferred_digest.ok());

    const auto left_policy =
        policy(left_root, left.public_key(), right.public_key());
    auto right_policy =
        policy(right_root, left.public_key(), right.public_key());
    right_policy.projection.includes = {"kept"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(right_policy).ok());
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }

    iotox::sync::NamespaceRegistry left_registry;
    iotox::sync::NamespaceRegistry right_registry;
    IOTOX_CHECK(left_registry.replace({left_policy}).ok());
    IOTOX_CHECK(right_registry.replace({right_policy}).ok());
    TransferBridge bridge;
    std::uint64_t left_message = 2500U;
    std::uint64_t right_message = 2600U;
    std::uint64_t left_file = 250U;
    std::uint64_t right_file = 260U;
    auto left_services =
        services(left_registry, bridge, left, crypto, left_message, left_file);
    auto right_services = services(right_registry, bridge, right, crypto,
                                   right_message, right_file);
    const auto left_as_publisher =
        context(left.public_key(), iotox::security::Capability::sync_publish);
    const auto right_as_subscriber = context(
        right.public_key(), iotox::security::Capability::sync_subscribe);

    const auto sparse = transfer_frontier(
        *left_services.publisher, *right_services.subscriber, bridge,
        left_as_publisher, right_as_subscriber, right_tree);
    IOTOX_CHECK(!sparse.custody_complete);
    IOTOX_CHECK(sparse.manifest_file_objects == 2U);
    IOTOX_CHECK(sparse.selected_file_objects == 1U);
    IOTOX_CHECK(sparse.skipped_file_objects == 1U);
    IOTOX_CHECK(read_file(right_tree / "kept" / "note.txt") ==
                "selected bytes");
    IOTOX_CHECK(!std::filesystem::exists(right_tree / "omitted" /
                                         "secret.txt"));
    IOTOX_CHECK(read_file(right_tree / "omitted" / "local.txt") ==
                "preserved local");
    IOTOX_CHECK(!std::filesystem::exists(iotox::sync::tree_v2_object_path(
        right_policy, deferred_digest.value())));

    auto complete_policy = right_policy;
    complete_policy.projection.includes.clear();
    IOTOX_CHECK(right_registry.replace({complete_policy}).ok());
    const auto widened = transfer_frontier(
        *left_services.publisher, *right_services.subscriber, bridge,
        left_as_publisher, right_as_subscriber, right_tree);
    IOTOX_CHECK(widened.custody_complete);
    IOTOX_CHECK(widened.manifest_file_objects == 2U);
    IOTOX_CHECK(widened.selected_file_objects == 2U);
    IOTOX_CHECK(widened.skipped_file_objects == 0U);
    IOTOX_CHECK(read_file(right_tree / "omitted" / "secret.txt") ==
                "deferred bytes");
    IOTOX_CHECK(read_file(right_tree / "omitted" / "local.txt") ==
                "preserved local");
    IOTOX_CHECK(std::filesystem::exists(iotox::sync::tree_v2_object_path(
        complete_policy, deferred_digest.value())));
}

IOTOX_TEST(
    "tree-v2 exact probes recover one frozen frontier from complementary sources") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto primary = identity(temporary.path() / "primary.identity", crypto);
    auto receiver = identity(temporary.path() / "receiver.identity", crypto);
    auto complement =
        identity(temporary.path() / "complement.identity", crypto);
    const auto primary_root = temporary.path() / "primary-root";
    const auto receiver_root = temporary.path() / "receiver-root";
    const auto complement_root = temporary.path() / "complement-root";
    const auto primary_tree = temporary.path() / "primary-tree";
    const auto receiver_tree = temporary.path() / "receiver-tree";
    const auto complement_tree = temporary.path() / "complement-tree";
    make_directory(primary_root);
    make_directory(receiver_root);
    make_directory(complement_root);
    make_directory(primary_tree);
    make_directory(receiver_tree);
    make_directory(complement_tree);
    write_file(primary_tree / "kept.txt", "primary bytes");
    write_file(primary_tree / "recovered.txt", "complementary bytes");
    write_file(complement_tree / "copy.txt", "complementary bytes");

    const auto add_complement = [&complement](auto policy) {
        policy.writers.push_back(complement.public_key());
        policy.subscribers.push_back(complement.public_key());
        std::sort(policy.writers.begin(), policy.writers.end());
        std::sort(policy.subscribers.begin(), policy.subscribers.end());
        return policy;
    };
    const auto primary_policy = add_complement(policy(
        primary_root, primary.public_key(), receiver.public_key()));
    const auto receiver_policy = add_complement(policy(
        receiver_root, primary.public_key(), receiver.public_key()));
    const auto complement_policy = add_complement(policy(
        complement_root, primary.public_key(), receiver.public_key()));
    auto recovered_digest = iotox::sync::hash_sync_file_sha256(
        primary_tree / "recovered.txt");
    IOTOX_CHECK(recovered_digest.ok());
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(primary_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            primary_policy, primary_tree, primary, crypto,
            transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }
    {
        auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(
            complement_policy);
        IOTOX_CHECK(transaction.ok());
        auto scan = iotox::sync::scan_tree_v2_worktree(
            complement_policy, complement_tree, std::nullopt,
            complement.public_key(), 1U);
        IOTOX_CHECK_MSG(scan.ok(), scan.status().message());
        auto stored = iotox::sync::store_tree_v2_scan_objects(
            complement_policy, scan.value(), transaction.value());
        IOTOX_CHECK_MSG(stored.ok(), stored.status().message());
    }
    IOTOX_CHECK(std::filesystem::remove(
        iotox::sync::tree_v2_object_path(primary_policy,
                                         recovered_digest.value())));

    iotox::sync::NamespaceRegistry primary_registry;
    iotox::sync::NamespaceRegistry receiver_registry;
    iotox::sync::NamespaceRegistry complement_registry;
    IOTOX_CHECK(primary_registry.replace({primary_policy}).ok());
    IOTOX_CHECK(receiver_registry.replace({receiver_policy}).ok());
    IOTOX_CHECK(complement_registry.replace({complement_policy}).ok());
    TransferBridge bridge;
    std::uint64_t primary_message = 3000U;
    std::uint64_t receiver_message = 4000U;
    std::uint64_t complement_message = 5000U;
    std::uint64_t primary_file = 300U;
    std::uint64_t receiver_file = 400U;
    std::uint64_t complement_file = 500U;
    auto primary_services = services(primary_registry, bridge, primary,
                                     crypto, primary_message, primary_file);
    auto receiver_services = services(receiver_registry, bridge, receiver,
                                      crypto, receiver_message, receiver_file);
    auto complement_services = services(
        complement_registry, bridge, complement, crypto, complement_message,
        complement_file);
    const auto primary_source = numbered_context(
        primary.public_key(), iotox::security::Capability::sync_publish,
        7U, 11U, 0x61U);
    const auto complement_source = numbered_context(
        complement.public_key(), iotox::security::Capability::sync_publish,
        8U, 12U, 0x62U);
    const auto receiver_for_primary = numbered_context(
        receiver.public_key(), iotox::security::Capability::sync_subscribe,
        7U, 11U, 0x61U);
    const auto receiver_for_complement = numbered_context(
        receiver.public_key(), iotox::security::Capability::sync_subscribe,
        8U, 12U, 0x62U);

    auto inventory = receiver_services.subscriber->begin_pull(
        primary_source, "field-notes", receiver_tree);
    IOTOX_CHECK_MSG(inventory.ok(), inventory.status().message());
    const std::uint64_t job_id = inventory.value().frame.message_id;
    IOTOX_CHECK(receiver_services.subscriber
                    ->add_source(job_id, complement_source)
                    .ok());
    IOTOX_CHECK(receiver_services.subscriber
                    ->add_source(job_id, complement_source)
                    .ok());
    auto changed_source = complement_source;
    changed_source.authority.tail_digest[0U] ^= 0x01U;
    IOTOX_CHECK(!receiver_services.subscriber
                     ->add_source(job_id, changed_source)
                     .ok());
    auto served_inventory = primary_services.publisher->handle(
        receiver_for_primary, inventory.value().frame);
    IOTOX_CHECK_MSG(served_inventory.ok(),
                    served_inventory.status().message());
    auto requests = receiver_services.subscriber->handle_inventory_result(
        primary_source, served_inventory.value().response);
    IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    for (std::size_t step = 0U;
         step < 1024U && !requests.value().empty(); ++step) {
        IOTOX_CHECK(requests.value().size() == 1U);
        const auto dispatch = requests.value().front();
        const bool from_primary =
            dispatch.context.friend_number == primary_source.friend_number;
        auto &publisher = from_primary ? *primary_services.publisher
                                       : *complement_services.publisher;
        const auto &subscriber_context =
            from_primary ? receiver_for_primary : receiver_for_complement;
        auto body = iotox::sync::decode_tree_v2_object_request(
            dispatch.frame.payload);
        IOTOX_CHECK(body.ok());
        auto served = publisher.handle(subscriber_context, dispatch.frame);
        IOTOX_CHECK_MSG(served.ok(), served.status().message());
        auto after_result =
            receiver_services.subscriber->handle_object_result(
                dispatch.context, served.value().response);
        IOTOX_CHECK_MSG(after_result.ok(),
                        after_result.status().message());
        if (!served.value().file_offered) {
            requests = std::move(after_result);
            continue;
        }
        IOTOX_CHECK(after_result.value().empty());
        auto offer = bridge.offer(body.value().transfer_id,
                                  dispatch.context.friend_number);
        IOTOX_CHECK(offer.ok());
        auto admitted = receiver_services.subscriber->handle_offer(
            dispatch.context, offer.value());
        IOTOX_CHECK_MSG(admitted.ok() && admitted.value(),
                        admitted.status().message());
        auto terminal = bridge.terminal(offer.value().file_number,
                                        dispatch.context.friend_number);
        IOTOX_CHECK(terminal.ok());
        requests = receiver_services.subscriber->handle_terminal(
            dispatch.context, terminal.value(),
            iotox::routes::WorkerTransferOutcome::completed,
            iotox::ErrorCode::ok);
        IOTOX_CHECK_MSG(requests.ok(), requests.status().message());
    }
    IOTOX_CHECK(requests.ok() && requests.value().empty());
    const auto snapshots = receiver_services.subscriber->snapshot();
    IOTOX_CHECK(!snapshots.empty());
    const auto &snapshot = snapshots.back();
    IOTOX_CHECK(snapshot.state == iotox::sync::TreeV2PullState::complete);
    IOTOX_CHECK(snapshot.sources == 2U);
    IOTOX_CHECK(snapshot.absent_results == 1U);
    IOTOX_CHECK(snapshot.source_snapshots.size() == 2U);
    IOTOX_CHECK(snapshot.source_snapshots.front().absent_objects == 1U);
    IOTOX_CHECK(snapshot.source_snapshots.back().committed_objects == 1U);
    IOTOX_CHECK(read_file(receiver_tree / "recovered.txt") ==
                "complementary bytes");

    IOTOX_CHECK(std::filesystem::remove(
        iotox::sync::tree_v2_object_path(receiver_policy,
                                         recovered_digest.value())));
    IOTOX_CHECK(std::filesystem::remove(
        iotox::sync::tree_v2_object_path(complement_policy,
                                         recovered_digest.value())));
    auto exhausted_inventory = receiver_services.subscriber->begin_pull(
        primary_source, "field-notes", receiver_tree);
    IOTOX_CHECK(exhausted_inventory.ok());
    const std::uint64_t exhausted_job =
        exhausted_inventory.value().frame.message_id;
    IOTOX_CHECK(receiver_services.subscriber
                    ->add_source(exhausted_job, complement_source)
                    .ok());
    auto exhausted_frontier = primary_services.publisher->handle(
        receiver_for_primary, exhausted_inventory.value().frame);
    IOTOX_CHECK(exhausted_frontier.ok());
    auto exhausted_request =
        receiver_services.subscriber->handle_inventory_result(
            primary_source, exhausted_frontier.value().response);
    IOTOX_CHECK(exhausted_request.ok());
    IOTOX_CHECK(exhausted_request.value().size() == 1U);
    auto primary_absent = primary_services.publisher->handle(
        receiver_for_primary, exhausted_request.value().front().frame);
    IOTOX_CHECK(primary_absent.ok() && !primary_absent.value().file_offered);
    auto complementary_request =
        receiver_services.subscriber->handle_object_result(
            primary_source, primary_absent.value().response);
    IOTOX_CHECK(complementary_request.ok());
    IOTOX_CHECK(complementary_request.value().size() == 1U);
    auto complement_absent = complement_services.publisher->handle(
        receiver_for_complement,
        complementary_request.value().front().frame);
    IOTOX_CHECK(complement_absent.ok() &&
                !complement_absent.value().file_offered);
    auto exhausted = receiver_services.subscriber->handle_object_result(
        complement_source, complement_absent.value().response);
    IOTOX_CHECK(!exhausted.ok());
    IOTOX_CHECK(exhausted.status().code() ==
                iotox::ErrorCode::unavailable);
    const auto final_snapshots = receiver_services.subscriber->snapshot();
    IOTOX_CHECK(final_snapshots.back().state ==
                iotox::sync::TreeV2PullState::failed);
    IOTOX_CHECK(final_snapshots.back().absent_results == 2U);
}

IOTOX_TEST(
    "tree-v2 checkpoint transfer requires explicit feature negotiation") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const auto left_root = temporary.path() / "left-root";
    const auto right_root = temporary.path() / "right-root";
    const auto left_tree = temporary.path() / "left-tree";
    const auto right_tree = temporary.path() / "right-tree";
    make_directory(left_root);
    make_directory(right_root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "checkpoint.txt", "bounded history");
    const auto left_policy =
        policy(left_root, left.public_key(), right.public_key());
    const auto right_policy =
        policy(right_root, left.public_key(), right.public_key());
    iotox::sync::Digest checkpoint_record{};
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto checkpoint = iotox::sync::checkpoint_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(checkpoint.ok(), checkpoint.status().message());
        checkpoint_record = checkpoint.value().checkpoint.record;
    }
    // The current branch is ordinary format 1 again, but its predecessor
    // closure still crosses a format-2 floor. Compatibility must inspect the
    // lineage rather than only the current record.
    write_file(left_tree / "successor.txt", "after checkpoint");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto successor = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
        IOTOX_CHECK(successor.value().branch_advances == 1U);
    }

    iotox::sync::NamespaceRegistry left_registry;
    iotox::sync::NamespaceRegistry right_registry;
    IOTOX_CHECK(left_registry.replace({left_policy}).ok());
    IOTOX_CHECK(right_registry.replace({right_policy}).ok());
    TransferBridge bridge;
    std::uint64_t left_message = 3000U;
    std::uint64_t right_message = 4000U;
    std::uint64_t left_file = 300U;
    std::uint64_t right_file = 400U;
    auto left_services =
        services(left_registry, bridge, left, crypto, left_message, left_file);
    auto right_services = services(right_registry, bridge, right, crypto,
                                   right_message, right_file);
    auto left_as_publisher =
        context(left.public_key(), iotox::security::Capability::sync_publish);
    auto right_as_subscriber = context(
        right.public_key(), iotox::security::Capability::sync_subscribe);

    auto request = iotox::sync::make_tree_v2_inventory_request_frame(
        iotox::sync::TreeV2InventoryRequest{"field-notes"}, 99U);
    IOTOX_CHECK(request.ok());
    auto refused =
        left_services.publisher->handle(right_as_subscriber, request.value());
    IOTOX_CHECK(refused.ok());
    auto refused_inventory = iotox::sync::decode_tree_v2_inventory_result(
        refused.value().response.payload);
    IOTOX_CHECK(refused_inventory.ok());
    IOTOX_CHECK(refused_inventory.value().status ==
                iotox::sync::TreeV2InventoryStatus::unavailable);

    iotox::FileId checkpoint_file_id{};
    checkpoint_file_id.fill(0x91U);
    auto checkpoint_request = iotox::sync::make_tree_v2_object_request_frame(
        {"field-notes", iotox::sync::TreeV2ObjectKind::branch_record,
         checkpoint_record, checkpoint_file_id},
        100U);
    IOTOX_CHECK(checkpoint_request.ok());
    auto refused_object = left_services.publisher->handle(
        right_as_subscriber, checkpoint_request.value());
    IOTOX_CHECK(refused_object.ok());
    auto refused_checkpoint = iotox::sync::decode_tree_v2_object_result(
        refused_object.value().response.payload);
    IOTOX_CHECK(refused_checkpoint.ok());
    IOTOX_CHECK(refused_checkpoint.value().status ==
                iotox::sync::TreeV2ObjectStatus::unavailable);

    left_as_publisher.tree_checkpoint_negotiated = true;
    right_as_subscriber.tree_checkpoint_negotiated = true;
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(read_file(right_tree / "checkpoint.txt") == "bounded history");
    IOTOX_CHECK(read_file(right_tree / "successor.txt") ==
                "after checkpoint");
}

IOTOX_TEST(
    "tree-v2 subscriber replays an immutable successor left before pointer commit") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const auto left_root = temporary.path() / "left-root";
    const auto right_root = temporary.path() / "right-root";
    const auto left_tree = temporary.path() / "left-tree";
    const auto right_tree = temporary.path() / "right-tree";
    make_directory(left_root);
    make_directory(right_root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "note.txt", "generation one");
    const auto left_policy =
        policy(left_root, left.public_key(), right.public_key());
    const auto right_policy =
        policy(right_root, left.public_key(), right.public_key());
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
    }

    iotox::sync::NamespaceRegistry left_registry;
    iotox::sync::NamespaceRegistry right_registry;
    IOTOX_CHECK(left_registry.replace({left_policy}).ok());
    IOTOX_CHECK(right_registry.replace({right_policy}).ok());
    TransferBridge bridge;
    std::uint64_t left_message = 5000U;
    std::uint64_t right_message = 6000U;
    std::uint64_t left_file = 500U;
    std::uint64_t right_file = 600U;
    auto left_services =
        services(left_registry, bridge, left, crypto, left_message, left_file);
    auto right_services = services(right_registry, bridge, right, crypto,
                                   right_message, right_file);
    const auto left_as_publisher =
        context(left.public_key(), iotox::security::Capability::sync_publish);
    const auto right_as_subscriber = context(
        right.public_key(), iotox::security::Capability::sync_subscribe);
    transfer_frontier(*left_services.publisher, *right_services.subscriber,
                      bridge, left_as_publisher, right_as_subscriber,
                      right_tree);
    IOTOX_CHECK(read_file(right_tree / "note.txt") == "generation one");

    write_file(left_tree / "note.txt", "generation two");
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        auto published = iotox::sync::reconcile_tree_v2_workspace(
            left_policy, left_tree, left, crypto, transaction.value());
        IOTOX_CHECK_MSG(published.ok(), published.status().message());
        IOTOX_CHECK(published.value().branch_advances == 1U);
    }

    iotox::sync::TreeV2Snapshot successor;
    iotox::sync::Digest successor_record{};
    {
        auto transaction =
            iotox::sync::SyncNamespaceTransaction::acquire(left_policy);
        IOTOX_CHECK(transaction.ok());
        iotox::sync::TreeV2BranchStore store(left_root);
        auto frontier = store.load_frontier(left_policy, crypto,
                                            transaction.value());
        IOTOX_CHECK_MSG(frontier.ok(), frontier.status().message());
        const auto found = std::find_if(
            frontier.value().begin(), frontier.value().end(),
            [&left](const auto &snapshot) {
                return snapshot.head.writer == left.public_key();
            });
        IOTOX_CHECK(found != frontier.value().end());
        successor = *found;
        auto record = iotox::sync::tree_v2_branch_record_digest(
            left_policy, successor.head, crypto);
        IOTOX_CHECK_MSG(record.ok(), record.status().message());
        successor_record = record.value();
    }

    // Model a crash after both immutable installs and before the mutable branch
    // pointer rename. Content is also already in CAS, so recovery must require
    // no transfer: the peer's signed inventory is the authority to replay the
    // orphan successor through normal branch acceptance.
    const auto copy_private = [](const std::filesystem::path &source,
                                 const std::filesystem::path &destination) {
        std::error_code error;
        std::filesystem::create_directories(destination.parent_path(), error);
        IOTOX_CHECK(!error);
        IOTOX_CHECK(::chmod(destination.parent_path().c_str(),
                            static_cast<mode_t>(0700)) == 0);
        IOTOX_CHECK(std::filesystem::copy_file(
            source, destination,
            std::filesystem::copy_options::overwrite_existing, error));
        IOTOX_CHECK(!error);
        IOTOX_CHECK(::chmod(destination.c_str(), static_cast<mode_t>(0600)) ==
                    0);
    };
    copy_private(iotox::sync::tree_v2_manifest_path(left_policy,
                                                     successor.head.manifest),
                 iotox::sync::tree_v2_manifest_path(right_policy,
                                                     successor.head.manifest));
    copy_private(iotox::sync::tree_v2_branch_record_path(left_policy,
                                                          successor_record),
                 iotox::sync::tree_v2_branch_record_path(right_policy,
                                                          successor_record));
    for (const auto &entry : successor.manifest.entries) {
        if (entry.kind != iotox::sync::TreeV2EntryKind::file) continue;
        copy_private(iotox::sync::tree_v2_object_path(left_policy,
                                                       entry.content),
                     iotox::sync::tree_v2_object_path(right_policy,
                                                       entry.content));
    }

    const auto recovered = transfer_frontier(
        *left_services.publisher, *right_services.subscriber, bridge,
        left_as_publisher, right_as_subscriber, right_tree);
    IOTOX_CHECK(recovered.requested_objects == 0U);
    IOTOX_CHECK(recovered.accepted_branches == 1U);
    IOTOX_CHECK(recovered.reused_objects >= 3U);
    IOTOX_CHECK(read_file(right_tree / "note.txt") == "generation two");

    auto right_transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(right_policy);
    IOTOX_CHECK(right_transaction.ok());
    iotox::sync::TreeV2BranchStore right_store(right_root);
    auto right_frontier = right_store.load_frontier(
        right_policy, crypto, right_transaction.value());
    IOTOX_CHECK_MSG(right_frontier.ok(), right_frontier.status().message());
    const auto recovered_head = std::find_if(
        right_frontier.value().begin(), right_frontier.value().end(),
        [&left](const auto &snapshot) {
            return snapshot.head.writer == left.public_key();
        });
    IOTOX_CHECK(recovered_head != right_frontier.value().end());
    IOTOX_CHECK(recovered_head->head.generation == successor.head.generation);
}
