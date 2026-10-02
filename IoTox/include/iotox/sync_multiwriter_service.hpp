#pragma once

#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_wire.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"
#include "iotox/sync_service.hpp"

#include <cstddef>
#include <cstdint>
#include <deque>
#include <filesystem>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

struct TreeV2PublisherSeams {
    std::function<Result<FileTransferRecord>(const SyncTransferCarrier &carrier,
                                             const std::filesystem::path &path,
                                             const FileId &file_id)>
        send_object;
    std::function<Result<std::uint64_t>()> make_message_id;
};

struct TreeV2PublisherResult {
    protocol::Frame response;
    SyncAuthorizationDecision authorization{
        SyncAuthorizationDecision::invalid_operation};
    bool replayed{false};
    bool file_offered{false};
};

struct TreeV2PublisherSnapshot {
    std::size_t retained_replays{0U};
    std::uint64_t inventory_requests{0U};
    std::uint64_t object_requests{0U};
    std::uint64_t denials{0U};
    std::uint64_t replay_hits{0U};
    std::uint64_t replay_conflicts{0U};
    std::uint64_t replay_evictions{0U};
    std::uint64_t file_offers{0U};
};

// Serves only immutable tree-v2 records/manifests/file objects. The caller's
// exact v3 authority proof and namespace subscriber membership are checked
// before any filesystem lookup or Tox file offer.
class TreeV2PublisherService final {
  public:
    struct Config {
        std::size_t maximum_replays{256U};
        const security::Sodium *sodium{nullptr};
        std::function<Result<std::shared_ptr<TreeV2StateWitness>>(
            const NamespacePolicy &)>
            state_witness;
    };

    TreeV2PublisherService(const NamespaceRegistry &namespaces,
                           TreeV2PublisherSeams seams, Config config);

    [[nodiscard]] Result<TreeV2PublisherResult>
    handle(const SyncPeerContext &context, const protocol::Frame &request);
    void peer_offline(std::uint32_t friend_number, std::uint64_t online_epoch);
    // Replay-cache retention is distinct from transfer lifetime. An additive
    // namespace membership change may retire these entries while its caller
    // holds the Agent authority/effect fence; a repeated request is then
    // re-authorized against the successor policy. This neither cancels a
    // transfer nor acts as a revocation/drain primitive.
    [[nodiscard]] std::size_t
    retire_namespace_replays_for_additive_share(std::string_view namespace_id);
    [[nodiscard]] TreeV2PublisherSnapshot snapshot() const;

  private:
    struct ReplayEntry {
        std::uint32_t friend_number{0U};
        std::uint64_t online_epoch{0U};
        std::uint64_t message_id{0U};
        security::AuthorityLedgerFormat authority_format{
            security::AuthorityLedgerFormat::v1};
        std::uint64_t authority_epoch{0U};
        std::uint64_t authority_sequence{0U};
        security::Digest authority_tail{};
        security::SigningPublicKey remote_principal{};
        std::uint64_t remote_capabilities{0U};
        std::string namespace_id;
        std::vector<std::uint8_t> request;
        TreeV2PublisherResult result;
    };

    [[nodiscard]] Status validate_config() const;
    [[nodiscard]] Result<std::uint64_t> next_message_id() const;

    const NamespaceRegistry *namespaces_{nullptr};
    TreeV2PublisherSeams seams_;
    Config config_;
    mutable std::mutex mutex_;
    std::deque<ReplayEntry> replays_;
    TreeV2PublisherSnapshot statistics_;
};

} // namespace iotox::sync
