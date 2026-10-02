#pragma once

#include "iotox/route_worker.hpp"
#include "iotox/sync_multiwriter_reconcile.hpp"
#include "iotox/sync_multiwriter_service.hpp"

#include <cstddef>
#include <cstdint>
#include <deque>
#include <filesystem>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

// One independently authenticated exact-object source. The primary source
// alone supplies the signed frontier; every registered source may satisfy an
// immutable digest from that frozen graph.
struct TreeV2SourceSnapshot {
    std::uint64_t source_id{0U};
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    security::SigningPublicKey stable_principal{};
    bool online{true};
    std::uint64_t requested_objects{0U};
    std::uint64_t offered_objects{0U};
    std::uint64_t absent_objects{0U};
    std::uint64_t unavailable_objects{0U};
    std::uint64_t committed_objects{0U};
    std::uint64_t fetched_bytes{0U};
};

// One owner-private, content-free binding for an active tree-v2 immutable
// object receive. Multiple lanes may belong to the same exact source session;
// request/FileId identity keeps transport and durable effects separate.
struct TreeV2LaneSnapshot {
    std::uint64_t request_id{0U};
    std::uint64_t source_id{0U};
    TreeV2ObjectKind kind{TreeV2ObjectKind::file};
    std::uint64_t object_bytes{0U};
    FileId file_id{};
    std::optional<std::uint32_t> file_number;
    bool transport_admitted{false};
};

enum class TreeV2PullState : std::uint8_t {
    awaiting_inventory = 1U,
    awaiting_object = 2U,
    complete = 3U,
    failed = 4U,
    cancelled = 5U,
};

struct TreeV2PullSnapshot {
    std::uint64_t job_id{0U};
    std::uint32_t friend_number{0U};
    std::uint64_t online_epoch{0U};
    std::string namespace_id;
    std::filesystem::path worktree;
    TreeV2PullState state{TreeV2PullState::awaiting_inventory};
    std::uint64_t requested_objects{0U};
    std::uint64_t committed_objects{0U};
    std::uint64_t reused_objects{0U};
    std::uint64_t fetched_bytes{0U};
    std::uint64_t accepted_branches{0U};
    std::uint64_t conflicts{0U};
    TreeV2ReconcileResult reconciliation;
    std::uint64_t manifest_file_objects{0U};
    std::uint64_t selected_file_objects{0U};
    std::uint64_t skipped_file_objects{0U};
    std::uint64_t selected_paths{0U};
    std::uint64_t skipped_paths{0U};
    bool custody_complete{true};
    std::uint32_t sources{0U};
    std::uint64_t availability_requests{0U};
    std::uint64_t availability_results{0U};
    std::uint64_t absent_results{0U};
    std::uint64_t unavailable_results{0U};
    std::uint32_t active_lanes{0U};
    std::uint32_t staged_file_objects{0U};
    std::uint64_t file_commit_batches{0U};
    std::uint32_t largest_file_commit_batch{0U};
    std::uint64_t cas_full_inventory_scans{0U};
    std::uint64_t cas_inventory_objects_inspected{0U};
    std::vector<TreeV2LaneSnapshot> lane_bindings;
    std::vector<TreeV2SourceSnapshot> source_snapshots;
    // Compatibility projection for the unambiguous zero/one-lane case. A
    // multi-lane job exposes every exact binding above and leaves these empty.
    std::optional<FileId> active_file_id;
    std::optional<std::uint32_t> active_file_number;
    std::string detail;
};

struct TreeV2Dispatch {
    SyncPeerContext context;
    protocol::Frame frame;
};

struct TreeV2SubscriberSnapshot {
    std::uint64_t file_commit_batches{0U};
    std::uint64_t file_objects_committed{0U};
    std::uint32_t largest_file_commit_batch{0U};
    std::uint64_t cas_full_inventory_scans{0U};
    std::uint64_t cas_inventory_objects_inspected{0U};
    std::uint64_t late_offers_cancelled{0U};
    std::uint64_t retired_offer_evictions{0U};
    std::uint32_t retired_offer_ids{0U};
};

struct TreeV2SubscriberSeams {
    std::function<Result<std::uint64_t>()> make_message_id;
    std::function<Result<FileId>()> make_file_id;
    std::function<Result<FileTransferRecord>(
        const SyncTransferCarrier &carrier, std::uint32_t file_number,
        const std::filesystem::path &destination)>
        receive_to_path;
    std::function<Status(const SyncTransferCarrier &carrier,
                         std::uint32_t file_number)>
        cancel_transfer;
};

// One bounded, serial tree-v2 graph receiver. The primary source freezes the
// signed frontier; complementary authenticated primary-lane sources may
// satisfy its exact immutable objects. File content commits to CAS before
// branch metadata, branch proofs commit before current pointers, and workspace
// reconciliation is the final effect.
class TreeV2SubscriberService final {
  public:
    struct Config {
        std::size_t maximum_jobs{4U};
        // Process ceiling for simultaneous exact object receives in one
        // tree-v2 pull. Namespace maximum-lanes and outstanding-request quotas
        // can only tighten this ceiling.
        std::size_t maximum_lanes{1U};
        const security::DeviceIdentity *identity{nullptr};
        const security::Sodium *sodium{nullptr};
        std::function<Result<std::shared_ptr<TreeV2StateWitness>>(
            const NamespacePolicy &)>
            state_witness;
    };

    TreeV2SubscriberService(const NamespaceRegistry &namespaces,
                            TreeV2SubscriberSeams seams, Config config);
    ~TreeV2SubscriberService();
    TreeV2SubscriberService(const TreeV2SubscriberService &) = delete;
    TreeV2SubscriberService &
    operator=(const TreeV2SubscriberService &) = delete;

    [[nodiscard]] Result<TreeV2Dispatch>
    begin_pull(const SyncPeerContext &context, std::string_view namespace_id,
               const std::filesystem::path &worktree);
    [[nodiscard]] Status add_source(std::uint64_t job_id,
                                    const SyncPeerContext &context);
    [[nodiscard]] Result<std::vector<TreeV2Dispatch>>
    handle_inventory_result(const SyncPeerContext &context,
                            const protocol::Frame &frame);
    [[nodiscard]] Result<std::vector<TreeV2Dispatch>>
    handle_object_result(const SyncPeerContext &context,
                         const protocol::Frame &frame);
    [[nodiscard]] Result<bool> handle_offer(const SyncPeerContext &context,
                                            const FileTransferRecord &offer);
    [[nodiscard]] Result<std::vector<TreeV2Dispatch>>
    handle_terminal(const SyncPeerContext &context,
                    const FileTransferRecord &transfer,
                    routes::WorkerTransferOutcome outcome, ErrorCode failure);
    [[nodiscard]] Status cancel_pull(std::uint64_t job_id);
    [[nodiscard]] Status
    namespace_mutation_ready(std::string_view namespace_id) const;
    [[nodiscard]] std::vector<TreeV2Dispatch>
    peer_offline(std::uint32_t friend_number, std::uint64_t online_epoch);
    [[nodiscard]] std::vector<TreeV2PullSnapshot> snapshot() const;
    [[nodiscard]] TreeV2SubscriberSnapshot statistics() const;

  private:
    struct PullJob;
    struct Source;
    struct RetiredOffer {
        std::uint32_t friend_number{0U};
        std::uint64_t online_epoch{0U};
        security::SigningPublicKey stable_principal{};
        SyncTransferCarrier carrier;
        FileId file_id{};
    };

    [[nodiscard]] Status validate_config() const;
    [[nodiscard]] Status authorize_publish(const SyncPeerContext &context,
                                           const NamespacePolicy &policy) const;
    [[nodiscard]] Result<std::vector<TreeV2Dispatch>> drive(PullJob &job);
    [[nodiscard]] Source *source_for(PullJob &job,
                                     std::uint64_t source_id) noexcept;
    [[nodiscard]] Result<std::size_t>
    commit_completed_file_batch(PullJob &job);
    void retire_unoffered_lane(PullJob &job,
                               std::size_t lane_index) noexcept;
    [[nodiscard]] Status admit_offer(PullJob &job, std::size_t lane_index);
    void fail(PullJob &job, std::string detail) noexcept;

    const NamespaceRegistry *namespaces_{nullptr};
    TreeV2SubscriberSeams seams_;
    Config config_;
    mutable std::mutex mutex_;
    std::vector<std::unique_ptr<PullJob>> jobs_;
    std::deque<RetiredOffer> retired_offers_;
    TreeV2SubscriberSnapshot statistics_;
    std::map<std::string, TreeV2SourceDigestCache> source_digest_caches_;
};

[[nodiscard]] std::string_view
tree_v2_pull_state_name(TreeV2PullState state) noexcept;

} // namespace iotox::sync
