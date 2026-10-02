#include "iotox/sync_multiwriter_service.hpp"

#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <set>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

class FileDescriptor {
  public:
    explicit FileDescriptor(int value) noexcept : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;

    [[nodiscard]] int get() const noexcept { return value_; }

  private:
    int value_{-1};
};

[[nodiscard]] Result<std::uint64_t>
private_file_bytes(const std::filesystem::path &path, std::uint64_t maximum) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        return Status{errno == ENOENT ? ErrorCode::not_found
                                      : ErrorCode::io_error,
                      "open tree-v2 object '" + path.string() +
                          "': " + std::strerror(errno)};
    }
    struct stat metadata {};
    if (::fstat(descriptor.get(), &metadata) != 0) {
        return Status{ErrorCode::io_error, "inspect tree-v2 object '" +
                                               path.string() +
                                               "': " + std::strerror(errno)};
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 || metadata.st_size < 0 ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U ||
        static_cast<std::uint64_t>(metadata.st_size) > maximum) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object is not one bounded private regular file"};
    }
    return static_cast<std::uint64_t>(metadata.st_size);
}

[[nodiscard]] Result<bool> frontier_uses_checkpoint(
    const NamespacePolicy &policy, std::span<const TreeV2Snapshot> frontier,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    std::vector<Digest> pending;
    std::set<Digest> visited;
    pending.reserve(frontier.size());
    for (const TreeV2Snapshot &snapshot : frontier) {
        auto record = tree_v2_branch_record_digest(policy, snapshot.head,
                                                   sodium);
        if (!record) return record.status();
        pending.push_back(record.value());
    }
    while (!pending.empty()) {
        const Digest record = pending.back();
        pending.pop_back();
        if (!visited.insert(record).second) continue;
        if (visited.size() > policy.quotas.maximum_objects) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 checkpoint compatibility walk exceeds "
                          "object quota"};
        }
        auto snapshot = load_tree_v2_stored_record(policy, record, sodium,
                                                   transaction);
        if (!snapshot) return snapshot.status();
        if (snapshot.value().head.checkpoint) return true;
        if (!std::all_of(snapshot.value().head.previous.begin(),
                         snapshot.value().head.previous.end(),
                         [](std::uint8_t byte) { return byte == 0U; })) {
            pending.push_back(snapshot.value().head.previous);
        }
        for (const TreeV2Observation &observation :
             snapshot.value().head.observations) {
            pending.push_back(observation.record);
        }
    }
    return false;
}

} // namespace

TreeV2PublisherService::TreeV2PublisherService(
    const NamespaceRegistry &namespaces, TreeV2PublisherSeams seams,
    Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {}

Status TreeV2PublisherService::validate_config() const {
    if (namespaces_ == nullptr || !seams_.send_object ||
        !seams_.make_message_id || config_.sodium == nullptr ||
        config_.maximum_replays == 0U || config_.maximum_replays > 65536U) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 publisher configuration is invalid"};
    }
    return Status::success();
}

Result<std::uint64_t> TreeV2PublisherService::next_message_id() const {
    auto result = seams_.make_message_id();
    if (!result) return result.status();
    if (result.value() == 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 message allocator returned zero"};
    }
    return result;
}

Result<TreeV2PublisherResult>
TreeV2PublisherService::handle(const SyncPeerContext &context,
                               const protocol::Frame &request) {
    std::scoped_lock lock(mutex_);
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    const Status context_valid = validate_sync_peer_context(context);
    if (!context_valid.ok()) return context_valid;
    if (!context.tree_transfer_negotiated ||
        context.transfer_carrier.carrier_class != SyncCarrierClass::primary) {
        return Status{
            ErrorCode::unsupported,
            "tree-v2 transfer was not negotiated on the primary lane"};
    }
    if (request.type != protocol::MessageType::sync_tree_inventory_request &&
        request.type != protocol::MessageType::sync_tree_object_request) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 publisher received a non-request frame"};
    }
    const Status valid_frame =
        request.type == protocol::MessageType::sync_tree_inventory_request
            ? validate_tree_v2_inventory_request_frame(request)
            : validate_tree_v2_object_request_frame(request);
    if (!valid_frame.ok()) return valid_frame;
    auto canonical = protocol::encode(request);
    if (!canonical) return canonical.status();
    const auto replay =
        std::find_if(replays_.begin(), replays_.end(),
                     [&context, &request](const ReplayEntry &entry) {
                         return entry.friend_number == context.friend_number &&
                                entry.online_epoch == context.online_epoch &&
                                entry.message_id == request.message_id;
                     });
    if (replay != replays_.end()) {
        if (replay->request != canonical.value()) {
            ++statistics_.replay_conflicts;
            return Status{ErrorCode::protocol_error,
                          "tree-v2 request id conflicts within online epoch"};
        }
        if (replay->authority_format != context.authority.format ||
            replay->authority_epoch != context.authority.ownership_epoch ||
            replay->authority_sequence != context.authority.sequence ||
            replay->authority_tail != context.authority.tail_digest ||
            replay->remote_principal !=
                context.peer_authority.remote_principal ||
            replay->remote_capabilities !=
                context.peer_authority.remote_capabilities ||
            context.peer_authority.verifier_state !=
                security::AuthorityVerifierState::authorized ||
            !context.peer_authority.remote_authorized) {
            return Status{
                ErrorCode::unavailable,
                "tree-v2 replay authority changed within online epoch"};
        }
        ++statistics_.replay_hits;
        TreeV2PublisherResult result = replay->result;
        result.replayed = true;
        result.file_offered = false;
        return result;
    }
    std::string namespace_id;
    std::optional<TreeV2ObjectRequest> object_request;
    if (request.type == protocol::MessageType::sync_tree_inventory_request) {
        auto decoded = decode_tree_v2_inventory_request(request.payload);
        if (!decoded) return decoded.status();
        namespace_id = decoded.value().namespace_id;
        ++statistics_.inventory_requests;
    } else {
        auto decoded = decode_tree_v2_object_request(request.payload);
        if (!decoded) return decoded.status();
        namespace_id = decoded.value().namespace_id;
        object_request = std::move(decoded).value();
        ++statistics_.object_requests;
    }

    SyncAuthorizationDecision decision =
        SyncAuthorizationDecision::invalid_policy;
    std::optional<std::filesystem::path> offered_path;
    TreeV2InventoryResult inventory{
        TreeV2InventoryStatus::denied, namespace_id, {}};
    TreeV2ObjectResult object{
        TreeV2ObjectStatus::denied,
        object_request ? object_request->kind : TreeV2ObjectKind::file,
        object_request ? object_request->object : Digest{},
        object_request ? object_request->transfer_id : FileId{}, 0U};

    auto policy = namespaces_->resolve(namespace_id);
    if (policy && policy.value().engine == Engine::tree_v2) {
        const SyncAuthorizationResult authorization =
            evaluate_sync_authorization(SyncOperation::subscribe,
                                        policy.value(), context.authority,
                                        context.peer_authority);
        decision = authorization.decision;
        if (authorization.authorized()) {
            auto transaction =
                SyncNamespaceTransaction::acquire(policy.value());
            std::shared_ptr<TreeV2StateWitness> witness;
            Status freshness = Status::success();
            if (transaction && config_.state_witness) {
                auto selected = config_.state_witness(policy.value());
                if (!selected) {
                    freshness = selected.status();
                } else {
                    witness = selected.value();
                    if (witness) {
                        freshness = witness->verify_read(
                            policy.value(), transaction.value());
                    }
                }
            }
            if (!transaction) {
                if (object_request)
                    object.status = TreeV2ObjectStatus::unavailable;
                else inventory.status = TreeV2InventoryStatus::unavailable;
            } else if (!freshness.ok()) {
                if (object_request)
                    object.status = TreeV2ObjectStatus::unavailable;
                else inventory.status = TreeV2InventoryStatus::unavailable;
            } else if (!object_request) {
                TreeV2BranchStore store(
                    std::filesystem::path(policy.value().root), std::nullopt,
                    witness);
                auto frontier = store.load_frontier(
                    policy.value(), *config_.sodium, transaction.value());
                if (!frontier) {
                    inventory.status = TreeV2InventoryStatus::unavailable;
                } else if (frontier.value().empty()) {
                    inventory.status = TreeV2InventoryStatus::absent;
                } else if (frontier.value().size() >
                           kTreeV2WireMaximumWriters) {
                    inventory.status = TreeV2InventoryStatus::unavailable;
                } else {
                    Result<bool> checkpoint_lineage = false;
                    if (!context.tree_checkpoint_negotiated) {
                        checkpoint_lineage = frontier_uses_checkpoint(
                            policy.value(), frontier.value(), *config_.sodium,
                            transaction.value());
                    }
                    if (!checkpoint_lineage || checkpoint_lineage.value()) {
                        inventory.status =
                            TreeV2InventoryStatus::unavailable;
                    } else {
                        inventory.status = TreeV2InventoryStatus::available;
                        for (const TreeV2Snapshot &snapshot :
                             frontier.value()) {
                            auto record = tree_v2_branch_record_digest(
                                policy.value(), snapshot.head,
                                *config_.sodium);
                            if (!record) return record.status();
                            inventory.frontier.push_back(TreeV2Observation{
                                snapshot.head.writer,
                                snapshot.head.generation, record.value()});
                        }
                        std::sort(inventory.frontier.begin(),
                                  inventory.frontier.end(),
                                  [](const TreeV2Observation &left,
                                     const TreeV2Observation &right) {
                                      return left.writer < right.writer;
                                  });
                    }
                }
            } else {
                std::filesystem::path path;
                Result<std::uint64_t> bytes =
                    Status{ErrorCode::not_found, "tree-v2 object is absent"};
                if (object_request->kind == TreeV2ObjectKind::branch_record) {
                    auto snapshot = load_tree_v2_stored_record(
                        policy.value(), object_request->object, *config_.sodium,
                        transaction.value());
                    path = tree_v2_branch_record_path(policy.value(),
                                                      object_request->object);
                    if (snapshot && snapshot.value().head.checkpoint &&
                        !context.tree_checkpoint_negotiated) {
                        bytes = Status{
                            ErrorCode::unsupported,
                            "tree-v2 checkpoint object was not negotiated"};
                    } else if (snapshot) {
                        bytes = private_file_bytes(
                            path, policy.value().quotas.maximum_manifest_bytes);
                    }
                } else if (object_request->kind == TreeV2ObjectKind::manifest) {
                    auto manifest = load_tree_v2_stored_manifest(
                        policy.value(), object_request->object, *config_.sodium,
                        transaction.value());
                    path = tree_v2_manifest_path(policy.value(),
                                                 object_request->object);
                    if (manifest)
                        bytes = private_file_bytes(
                            path, policy.value().quotas.maximum_manifest_bytes);
                } else {
                    path = tree_v2_object_path(policy.value(),
                                               object_request->object);
                    bytes = private_file_bytes(
                        path, policy.value().quotas.maximum_artifact_bytes);
                    if (bytes) {
                        const Status verified = verify_tree_v2_object_file(
                            path, object_request->object, bytes.value());
                        if (!verified.ok()) bytes = verified;
                    }
                }
                if (!bytes) {
                    object.status =
                        bytes.status().code() == ErrorCode::not_found
                            ? TreeV2ObjectStatus::absent
                            : TreeV2ObjectStatus::unavailable;
                } else {
                    object.status = TreeV2ObjectStatus::offered;
                    object.object_bytes = bytes.value();
                    offered_path = std::move(path);
                }
            }
        } else {
            ++statistics_.denials;
        }
    } else {
        ++statistics_.denials;
    }

    auto message_id = next_message_id();
    if (!message_id) return message_id.status();
    Result<protocol::Frame> response =
        object_request
            ? make_tree_v2_object_result_frame(object, message_id.value(),
                                               request.message_id)
            : make_tree_v2_inventory_result_frame(inventory, message_id.value(),
                                                  request.message_id);
    if (!response) return response.status();
    TreeV2PublisherResult result{std::move(response).value(), decision, false,
                                 false};
    if (replays_.size() >= config_.maximum_replays) {
        replays_.pop_front();
        ++statistics_.replay_evictions;
    }
    replays_.push_back(ReplayEntry{
        context.friend_number, context.online_epoch, request.message_id,
        context.authority.format, context.authority.ownership_epoch,
        context.authority.sequence, context.authority.tail_digest,
        context.peer_authority.remote_principal,
        context.peer_authority.remote_capabilities,
        namespace_id,
        std::move(canonical).value(), std::move(result)});
    ReplayEntry &retained = replays_.back();
    if (offered_path) {
        auto sent = seams_.send_object(context.transfer_carrier, *offered_path,
                                       object_request->transfer_id);
        if (sent) {
            retained.result.file_offered = true;
            ++statistics_.file_offers;
        } else {
            object.status = TreeV2ObjectStatus::unavailable;
            object.object_bytes = 0U;
            auto unavailable = make_tree_v2_object_result_frame(
                object, message_id.value(), request.message_id);
            if (!unavailable) return unavailable.status();
            retained.result.response = std::move(unavailable).value();
        }
    }
    statistics_.retained_replays = replays_.size();
    return retained.result;
}

void TreeV2PublisherService::peer_offline(std::uint32_t friend_number,
                                          std::uint64_t online_epoch) {
    std::scoped_lock lock(mutex_);
    std::erase_if(replays_,
                  [friend_number, online_epoch](const ReplayEntry &entry) {
                      return entry.friend_number == friend_number &&
                             entry.online_epoch == online_epoch;
                  });
    statistics_.retained_replays = replays_.size();
}

std::size_t
TreeV2PublisherService::retire_namespace_replays_for_additive_share(
    std::string_view namespace_id) {
    std::scoped_lock lock(mutex_);
    const std::size_t before = replays_.size();
    std::erase_if(replays_, [namespace_id](const ReplayEntry &entry) {
        return entry.namespace_id == namespace_id;
    });
    statistics_.retained_replays = replays_.size();
    return before - replays_.size();
}

TreeV2PublisherSnapshot TreeV2PublisherService::snapshot() const {
    std::scoped_lock lock(mutex_);
    return statistics_;
}

} // namespace iotox::sync
