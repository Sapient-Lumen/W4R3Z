#include "iotox/sync_multiwriter_subscriber.hpp"

#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <deque>
#include <fcntl.h>
#include <iomanip>
#include <iterator>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::size_t kMaximumRetiredTreeOffers = 4096U;

void append_cache_key_part(std::string &key, std::string_view part) {
    key.append(std::to_string(part.size()));
    key.push_back(':');
    key.append(part);
    key.push_back('\n');
}

[[nodiscard]] std::string
source_digest_cache_key(const NamespacePolicy &policy,
                        const std::filesystem::path &worktree) {
    std::string key;
    append_cache_key_part(key, policy.id);
    append_cache_key_part(
        key, std::filesystem::path(policy.root).lexically_normal().string());
    append_cache_key_part(key, worktree.lexically_normal().string());
    return key;
}

class FileDescriptor {
  public:
    explicit FileDescriptor(int value = -1) noexcept : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    [[nodiscard]] int get() const noexcept { return value_; }

  private:
    int value_{-1};
};

struct ObjectKey {
    TreeV2ObjectKind kind{TreeV2ObjectKind::file};
    Digest digest{};

    [[nodiscard]] bool operator==(const ObjectKey &) const = default;
    [[nodiscard]] bool operator<(const ObjectKey &other) const noexcept {
        return kind != other.kind ? static_cast<std::uint8_t>(kind) <
                                        static_cast<std::uint8_t>(other.kind)
                                  : digest < other.digest;
    }
};

struct PendingObject {
    ObjectKey key;
    std::optional<std::uint64_t> expected_bytes;
    std::set<std::uint64_t> attempted_sources;
};

struct ReceivedBranch {
    TreeV2BranchHead head;
    // Immutable record presence is not enough: a power loss may leave this
    // record and its manifest durable before the writer pointer is replaced.
    // True means the record is already represented by the accepted frontier
    // (or by accepted history), not merely reusable from local storage.
    bool incorporated{false};
};

struct ActiveLane {
    PendingObject object;
    std::uint64_t source_id{0U};
    std::uint64_t request_id{0U};
    FileId file_id{};
    std::filesystem::path staging;
    std::optional<std::uint64_t> offered_bytes;
    std::optional<FileTransferRecord> offer;
    bool admitted{false};
    bool transport_complete{false};
};

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] bool same_authority(const SyncPeerContext &left,
                                  const SyncPeerContext &right) noexcept {
    return left.friend_number == right.friend_number &&
           left.online_epoch == right.online_epoch &&
           left.authority_route_key == right.authority_route_key &&
           left.authority.format == right.authority.format &&
           left.authority.ownership_epoch == right.authority.ownership_epoch &&
           left.authority.sequence == right.authority.sequence &&
           left.authority.tail_digest == right.authority.tail_digest &&
           left.peer_authority.remote_principal ==
               right.peer_authority.remote_principal &&
           left.peer_authority.remote_capabilities ==
               right.peer_authority.remote_capabilities &&
           left.transfer_carrier == right.transfer_carrier;
}

[[nodiscard]] std::string request_hex(std::uint64_t value) {
    std::ostringstream output;
    output << std::hex << std::setw(16) << std::setfill('0') << value;
    return output.str();
}

[[nodiscard]] Status system_status(std::string_view operation,
                                   const std::filesystem::path &path,
                                   int error = errno) {
    return Status{ErrorCode::io_error, std::string(operation) + " '" +
                                           path.string() +
                                           "': " + std::strerror(error)};
}

[[nodiscard]] Status
ensure_private_directory(const std::filesystem::path &path) {
    if (::mkdir(path.c_str(), static_cast<mode_t>(0700)) != 0 &&
        errno != EEXIST)
        return system_status("create tree-v2 incoming directory", path);
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0)
        return system_status("inspect tree-v2 incoming directory", path);
    if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 incoming path is not a private directory"};
    }
    return Status::success();
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 incoming directory", path);
    if (::fsync(descriptor.get()) != 0)
        return system_status("fsync tree-v2 incoming directory", path);
    return Status::success();
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
read_private_file(const std::filesystem::path &path,
                  std::uint64_t maximum_bytes) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 incoming object", path);
    struct stat metadata {};
    if (::fstat(descriptor.get(), &metadata) != 0)
        return system_status("inspect tree-v2 incoming object", path);
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 || metadata.st_size < 0 ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U ||
        static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 incoming object is not one bounded private file"};
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor.get(), bytes.data() + offset,
                                     bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return system_status("read tree-v2 incoming object", path);
    }
    return bytes;
}

[[nodiscard]] Status remove_staging(const std::filesystem::path &path,
                                    bool synchronize = true) {
    if (path.empty()) return Status::success();
    if (::unlink(path.c_str()) == 0) {
        return synchronize ? sync_directory(path.parent_path())
                           : Status::success();
    }
    if (errno == ENOENT) return Status::success();
    return system_status("remove tree-v2 incoming object", path);
}

[[nodiscard]] bool is_stale_staging_name(std::string_view name) noexcept {
    constexpr std::string_view prefix = ".receive-";
    constexpr std::string_view suffix = ".part";
    constexpr std::size_t hex_bytes = 16U;
    if (name.size() != prefix.size() + hex_bytes + suffix.size() ||
        !name.starts_with(prefix) || !name.ends_with(suffix))
        return false;
    const auto identity = name.substr(prefix.size(), hex_bytes);
    return std::all_of(identity.begin(), identity.end(), [](char byte) {
        return (byte >= '0' && byte <= '9') || (byte >= 'a' && byte <= 'f');
    });
}

[[nodiscard]] bool
is_stale_transport_staging_name(std::string_view name) noexcept {
    constexpr std::string_view transport_prefix = ".iotox-";
    constexpr std::string_view transport_marker = ".part-";
    constexpr std::size_t random_bytes = 6U;
    if (!name.starts_with(transport_prefix) ||
        name.size() <= transport_prefix.size() + transport_marker.size() +
                           random_bytes) {
        return false;
    }
    name.remove_prefix(transport_prefix.size());
    const std::size_t marker_offset =
        name.size() - transport_marker.size() - random_bytes;
    if (name.substr(marker_offset, transport_marker.size()) !=
            transport_marker ||
        !is_stale_staging_name(name.substr(0U, marker_offset))) {
        return false;
    }
    const std::string_view random =
        name.substr(marker_offset + transport_marker.size(), random_bytes);
    return std::all_of(random.begin(), random.end(), [](char byte) {
        return (byte >= '0' && byte <= '9') ||
               (byte >= 'A' && byte <= 'Z') ||
               (byte >= 'a' && byte <= 'z');
    });
}

[[nodiscard]] Status
remove_stale_staging(const std::filesystem::path &incoming) {
    std::error_code error;
    for (std::filesystem::directory_iterator iterator(incoming, error), end;
         !error && iterator != end; iterator.increment(error)) {
        const std::string name = iterator->path().filename().string();
        if (!is_stale_staging_name(name) &&
            !is_stale_transport_staging_name(name))
            continue;
        const Status removed = remove_staging(iterator->path(), false);
        if (!removed.ok()) return removed;
    }
    if (error)
        return Status{ErrorCode::io_error,
                      "inspect tree-v2 incoming directory '" +
                          incoming.string() + "': " + error.message()};
    // One barrier covers the complete bounded cleanup instead of restoring
    // the old per-object fsync cost to normal file-window commits.
    return sync_directory(incoming);
}

} // namespace

struct TreeV2SubscriberService::Source {
    std::uint64_t source_id{0U};
    SyncPeerContext context;
    bool online{true};
    std::uint64_t requested_objects{0U};
    std::uint64_t offered_objects{0U};
    std::uint64_t absent_objects{0U};
    std::uint64_t unavailable_objects{0U};
    std::uint64_t committed_objects{0U};
    std::uint64_t fetched_bytes{0U};
};

struct TreeV2SubscriberService::PullJob {
    TreeV2PullSnapshot status;
    NamespacePolicy policy;
    SyncPeerContext context;
    std::vector<Source> sources;
    std::deque<PendingObject> queue;
    std::set<ObjectKey> scheduled;
    std::map<Digest, ReceivedBranch> branches;
    std::map<Digest, TreeV2Manifest> manifests;
    std::map<Digest, std::uint64_t> file_sizes;
    std::set<Digest> selected_files;
    std::set<std::pair<std::string, Digest>> selected_paths;
    std::set<std::pair<std::string, Digest>> skipped_paths;
    std::vector<ActiveLane> lanes;
    std::shared_ptr<TreeV2StateWitness> witness;
    std::optional<TreeV2ObjectInventory> object_inventory;
};

std::string_view tree_v2_pull_state_name(TreeV2PullState state) noexcept {
    switch (state) {
    case TreeV2PullState::awaiting_inventory:
        return "awaiting-inventory";
    case TreeV2PullState::awaiting_object:
        return "awaiting-object";
    case TreeV2PullState::complete:
        return "complete";
    case TreeV2PullState::failed:
        return "failed";
    case TreeV2PullState::cancelled:
        return "cancelled";
    }
    return "unknown";
}

TreeV2SubscriberService::TreeV2SubscriberService(
    const NamespaceRegistry &namespaces, TreeV2SubscriberSeams seams,
    Config config)
    : namespaces_(&namespaces), seams_(std::move(seams)), config_(config) {
    if (config_.maximum_jobs > 0U && config_.maximum_jobs <= 1024U)
        jobs_.reserve(config_.maximum_jobs);
}

TreeV2SubscriberService::~TreeV2SubscriberService() = default;

TreeV2SubscriberService::Source *
TreeV2SubscriberService::source_for(PullJob &job,
                                     std::uint64_t source_id) noexcept {
    const auto found = std::find_if(
        job.sources.begin(), job.sources.end(),
        [source_id](const Source &source) {
            return source.source_id == source_id;
        });
    return found == job.sources.end() ? nullptr : &*found;
}

Status TreeV2SubscriberService::validate_config() const {
    if (namespaces_ == nullptr || !seams_.make_message_id ||
        !seams_.make_file_id || !seams_.receive_to_path ||
        !seams_.cancel_transfer || config_.identity == nullptr ||
        config_.sodium == nullptr || config_.maximum_jobs == 0U ||
        config_.maximum_jobs > 1024U ||
        config_.maximum_lanes == 0U ||
        config_.maximum_lanes > std::numeric_limits<std::uint16_t>::max() ||
        jobs_.capacity() < config_.maximum_jobs) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 subscriber configuration is invalid"};
    }
    return Status::success();
}

Status TreeV2SubscriberService::authorize_publish(
    const SyncPeerContext &context, const NamespacePolicy &policy) const {
    const Status valid = validate_sync_peer_context(context);
    if (!valid.ok()) return valid;
    if (!context.tree_transfer_negotiated ||
        context.transfer_carrier.carrier_class != SyncCarrierClass::primary) {
        return Status{
            ErrorCode::unsupported,
            "tree-v2 transfer was not negotiated on the primary lane"};
    }
    const SyncAuthorizationResult authorized =
        evaluate_sync_authorization(SyncOperation::publish, policy,
                                    context.authority, context.peer_authority);
    return authorized.authorized()
               ? Status::success()
               : Status{ErrorCode::unavailable,
                        "tree-v2 publisher authorization failed: " +
                            std::string(sync_authorization_decision_name(
                                authorized.decision))};
}

Result<TreeV2Dispatch>
TreeV2SubscriberService::begin_pull(const SyncPeerContext &context,
                                    std::string_view namespace_id,
                                    const std::filesystem::path &worktree) {
    std::scoped_lock lock(mutex_);
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    const auto terminal = [](const auto &job) {
        return job->status.state == TreeV2PullState::complete ||
               job->status.state == TreeV2PullState::failed ||
               job->status.state == TreeV2PullState::cancelled;
    };
    const std::size_t active_jobs = static_cast<std::size_t>(
        std::count_if(jobs_.begin(), jobs_.end(),
                      [&terminal](const auto &job) { return !terminal(job); }));
    if (active_jobs >= config_.maximum_jobs) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 subscriber job bound is exhausted"};
    }
    while (jobs_.size() >= config_.maximum_jobs) {
        const auto old = std::find_if(jobs_.begin(), jobs_.end(), terminal);
        if (old == jobs_.end()) break;
        jobs_.erase(old);
    }
    if (!worktree.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 worktree must be absolute"};
    }
    auto policy = namespaces_->resolve(namespace_id);
    if (!policy) return policy.status();
    if (policy.value().engine != Engine::tree_v2) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 pull requires a tree-v2 namespace"};
    }
    const Status authorized = authorize_publish(context, policy.value());
    if (!authorized.ok()) return authorized;
    if (!std::binary_search(policy.value().writers.begin(),
                            policy.value().writers.end(),
                            config_.identity->public_key())) {
        return Status{ErrorCode::unavailable,
                      "local stable device is not a tree-v2 writer"};
    }
    const auto duplicate = std::find_if(
        jobs_.begin(), jobs_.end(), [&policy](const auto &candidate) {
            return candidate->policy.id == policy.value().id &&
                   candidate->status.state != TreeV2PullState::complete &&
                   candidate->status.state != TreeV2PullState::failed &&
                   candidate->status.state != TreeV2PullState::cancelled;
        });
    if (duplicate != jobs_.end()) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 namespace already has an active pull"};
    }

    auto transaction = SyncNamespaceTransaction::acquire(policy.value());
    if (!transaction) return transaction.status();
    Result<std::shared_ptr<TreeV2StateWitness>> witness =
        std::shared_ptr<TreeV2StateWitness>{};
    if (config_.state_witness)
        witness = config_.state_witness(policy.value());
    if (!witness) return witness.status();
    if (witness.value()) {
        const Status fresh = witness.value()->verify_read(
            policy.value(), transaction.value());
        if (!fresh.ok()) return fresh;
    }
    TreeV2BranchStore store(std::filesystem::path(policy.value().root),
                            config_.identity->public_key(), witness.value());
    const Status prepared = store.prepare(policy.value(), transaction.value());
    if (!prepared.ok()) return prepared;
    const std::filesystem::path incoming_path =
        std::filesystem::path(policy.value().root) / "tree-v2" / "incoming";
    const Status incoming = ensure_private_directory(incoming_path);
    if (!incoming.ok()) return incoming;
    const Status recovered = remove_stale_staging(incoming_path);
    if (!recovered.ok()) return recovered;
    auto message_id = seams_.make_message_id();
    if (!message_id || message_id.value() == 0U)
        return message_id ? Status{ErrorCode::protocol_error,
                                   "tree-v2 message allocator returned zero"}
                          : message_id.status();
    auto frame = make_tree_v2_inventory_request_frame(
        {std::string(namespace_id)}, message_id.value());
    if (!frame) return frame.status();
    auto job = std::make_unique<PullJob>();
    job->status.job_id = message_id.value();
    job->status.friend_number = context.friend_number;
    job->status.online_epoch = context.online_epoch;
    job->status.namespace_id = std::string(namespace_id);
    job->status.worktree = worktree;
    job->status.custody_complete =
        policy.value().projection.includes.empty() &&
        policy.value().projection.excludes.empty();
    job->status.detail = "awaiting signed tree-v2 branch inventory";
    job->policy = std::move(policy).value();
    job->witness = witness.value();
    job->context = context;
    job->sources.push_back(Source{message_id.value(), context, true, 0U, 0U,
                                  0U, 0U, 0U, 0U});
    job->status.sources = 1U;
    jobs_.push_back(std::move(job));
    return TreeV2Dispatch{context, std::move(frame).value()};
}

Status TreeV2SubscriberService::add_source(
    std::uint64_t job_id, const SyncPeerContext &context) {
    std::scoped_lock lock(mutex_);
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    const auto found = std::find_if(
        jobs_.begin(), jobs_.end(), [job_id](const auto &job) {
            return job->status.job_id == job_id;
        });
    if (found == jobs_.end()) {
        return Status{ErrorCode::not_found,
                      "tree-v2 pull job is absent"};
    }
    PullJob &job = **found;
    if (job.status.state != TreeV2PullState::awaiting_inventory &&
        job.status.state != TreeV2PullState::awaiting_object) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 pull no longer accepts sources"};
    }
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok()) return authorized;
    const auto duplicate = std::find_if(
        job.sources.begin(), job.sources.end(),
        [&context](const Source &source) {
            return source.context.friend_number == context.friend_number &&
                   source.context.online_epoch == context.online_epoch;
        });
    if (duplicate != job.sources.end()) {
        return same_authority(duplicate->context, context)
                   ? Status::success()
                   : Status{ErrorCode::unavailable,
                            "tree-v2 source authority changed within its epoch"};
    }
    if (job.sources.size() >= job.policy.quotas.maximum_peers) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 source bound is exhausted"};
    }
    auto source_id = seams_.make_message_id();
    if (!source_id) return source_id.status();
    if (source_id.value() == 0U ||
        source_for(job, source_id.value()) != nullptr) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 source allocator reused an identity"};
    }
    job.sources.push_back(Source{source_id.value(), context, true, 0U, 0U,
                                 0U, 0U, 0U, 0U});
    job.status.sources = static_cast<std::uint32_t>(job.sources.size());
    job.status.detail =
        "tree-v2 exact-object source added; primary frontier unchanged";
    return Status::success();
}

Result<std::vector<TreeV2Dispatch>>
TreeV2SubscriberService::handle_inventory_result(const SyncPeerContext &context,
                                                 const protocol::Frame &frame) {
    std::scoped_lock lock(mutex_);
    const Status valid = validate_tree_v2_inventory_result_frame(frame);
    if (!valid.ok()) return valid;
    const auto found = std::find_if(
        jobs_.begin(), jobs_.end(), [&context, &frame](const auto &candidate) {
            return candidate->status.job_id == frame.correlation_id &&
                   candidate->status.friend_number == context.friend_number &&
                   candidate->status.online_epoch == context.online_epoch;
        });
    if (found == jobs_.end())
        return Status{ErrorCode::not_found,
                      "tree-v2 inventory result has no active job"};
    PullJob &job = **found;
    if (job.status.state != TreeV2PullState::awaiting_inventory ||
        !same_authority(job.context, context)) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 inventory authority or phase changed"};
    }
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok()) {
        fail(job, authorized.message());
        return authorized;
    }
    auto decoded = decode_tree_v2_inventory_result(frame.payload);
    if (!decoded) return decoded.status();
    if (decoded.value().namespace_id != job.policy.id) {
        fail(job, "tree-v2 inventory changed namespace");
        return Status{ErrorCode::protocol_error,
                      "tree-v2 inventory changed namespace"};
    }
    if (decoded.value().status == TreeV2InventoryStatus::denied ||
        decoded.value().status == TreeV2InventoryStatus::unavailable) {
        fail(job, "tree-v2 publisher refused inventory");
        return Status{ErrorCode::unavailable, job.status.detail};
    }
    for (const TreeV2Observation &observation : decoded.value().frontier) {
        if (!std::binary_search(job.policy.writers.begin(),
                                job.policy.writers.end(), observation.writer)) {
            fail(job, "tree-v2 inventory advertises an unauthorized writer");
            return Status{ErrorCode::protocol_error, job.status.detail};
        }
        ObjectKey key{TreeV2ObjectKind::branch_record, observation.record};
        if (job.scheduled.insert(key).second)
            job.queue.push_back(PendingObject{key, std::nullopt, {}});
    }
    job.status.state = TreeV2PullState::awaiting_object;
    job.status.detail = decoded.value().status == TreeV2InventoryStatus::absent
                            ? "peer tree-v2 frontier is empty"
                            : "walking signed tree-v2 object graph";
    auto next = drive(job);
    if (!next) fail(job, next.status().message());
    return next;
}

Result<std::vector<TreeV2Dispatch>>
TreeV2SubscriberService::drive(PullJob &job) {
    const auto enqueue = [&job](TreeV2ObjectKind kind, const Digest &digest,
                                std::optional<std::uint64_t> bytes) -> Status {
        const ObjectKey key{kind, digest};
        if (kind == TreeV2ObjectKind::file) {
            if (!bytes) {
                return Status{ErrorCode::internal_error,
                              "tree-v2 file object lacks an expected size"};
            }
            const auto size = job.file_sizes.find(digest);
            if (size != job.file_sizes.end() && size->second != *bytes) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 digest is claimed with conflicting sizes"};
            }
            job.file_sizes[digest] = *bytes;
        }
        if (job.scheduled.contains(key)) return Status::success();
        if (job.scheduled.size() >= job.policy.quotas.maximum_objects) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 object graph exceeds namespace quota"};
        }
        job.scheduled.insert(key);
        job.queue.push_back(PendingObject{key, bytes, {}});
        return Status::success();
    };
    const auto expand_branch =
        [&enqueue](const TreeV2BranchHead &head) -> Status {
        if (head.checkpoint) {
            return enqueue(TreeV2ObjectKind::manifest, head.manifest,
                           head.manifest_bytes);
        }
        if (!all_zero(head.previous)) {
            const Status added = enqueue(TreeV2ObjectKind::branch_record,
                                         head.previous, std::nullopt);
            if (!added.ok()) return added;
        }
        for (const TreeV2Observation &observation : head.observations) {
            const Status added = enqueue(TreeV2ObjectKind::branch_record,
                                         observation.record, std::nullopt);
            if (!added.ok()) return added;
        }
        return enqueue(TreeV2ObjectKind::manifest, head.manifest,
                       head.manifest_bytes);
    };
    const auto expand_manifest = [&enqueue, &job](
                                     const TreeV2Manifest &manifest) {
        for (const TreeV2Entry &entry : manifest.entries) {
            if (entry.kind != TreeV2EntryKind::file) continue;
            const auto prior = job.file_sizes.find(entry.content);
            if (prior != job.file_sizes.end() &&
                prior->second != entry.content_bytes) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 digest is claimed with conflicting sizes"};
            }
            job.file_sizes[entry.content] = entry.content_bytes;
            const auto path = std::pair{entry.path, entry.content};
            if (!tree_v2_path_selected(job.policy, entry.path, false)) {
                job.skipped_paths.insert(path);
            } else {
                job.selected_files.insert(entry.content);
                job.selected_paths.insert(path);
                const Status added = enqueue(TreeV2ObjectKind::file,
                                             entry.content,
                                             entry.content_bytes);
                if (!added.ok()) return added;
            }
            const std::size_t unselected =
                job.file_sizes.size() - job.selected_files.size();
            if (job.scheduled.size() > job.policy.quotas.maximum_objects ||
                unselected > job.policy.quotas.maximum_objects -
                                 job.scheduled.size()) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 object graph exceeds namespace quota"};
            }
        }
        job.status.manifest_file_objects = job.file_sizes.size();
        job.status.selected_file_objects = job.selected_files.size();
        job.status.skipped_file_objects =
            job.file_sizes.size() - job.selected_files.size();
        job.status.selected_paths = job.selected_paths.size();
        job.status.skipped_paths = job.skipped_paths.size();
        return Status::success();
    };

    const std::size_t lane_limit = std::min(
        {config_.maximum_lanes,
         static_cast<std::size_t>(job.policy.quotas.maximum_lanes),
         static_cast<std::size_t>(
             job.policy.quotas.maximum_outstanding_requests)});
    std::vector<TreeV2Dispatch> dispatches;
    while (job.lanes.size() < lane_limit && !job.queue.empty()) {
        PendingObject object = job.queue.front();
        job.queue.pop_front();
        auto transaction = SyncNamespaceTransaction::acquire(job.policy);
        if (!transaction) return transaction.status();
        if (object.key.kind == TreeV2ObjectKind::branch_record) {
            auto local = load_tree_v2_stored_record(
                job.policy, object.key.digest, *config_.sodium,
                transaction.value());
            if (local) {
                job.branches[object.key.digest] =
                    ReceivedBranch{local.value().head, false};
                job.manifests[local.value().head.manifest] =
                    local.value().manifest;
                ++job.status.reused_objects;
                const Status branch = expand_branch(local.value().head);
                if (!branch.ok()) return branch;
                const Status manifest = expand_manifest(local.value().manifest);
                if (!manifest.ok()) return manifest;
                continue;
            }
        } else if (object.key.kind == TreeV2ObjectKind::manifest) {
            auto local = load_tree_v2_stored_manifest(
                job.policy, object.key.digest, *config_.sodium,
                transaction.value());
            if (local) {
                job.manifests[object.key.digest] = local.value();
                ++job.status.reused_objects;
                const Status manifest = expand_manifest(local.value());
                if (!manifest.ok()) return manifest;
                continue;
            }
        } else {
            const std::uint64_t bytes = object.expected_bytes.value_or(0U);
            const Status local = verify_tree_v2_object_file(
                tree_v2_object_path(job.policy, object.key.digest),
                object.key.digest, bytes);
            if (local.ok()) {
                ++job.status.reused_objects;
                continue;
            }
        }

        Source *source = nullptr;
        for (Source &candidate : job.sources) {
            if (candidate.online &&
                !object.attempted_sources.contains(candidate.source_id)) {
                source = &candidate;
                break;
            }
        }
        if (source == nullptr) {
            return Status{
                ErrorCode::unavailable,
                "no registered tree-v2 source offered one exact object"};
        }
        object.attempted_sources.insert(source->source_id);
        auto request_id = seams_.make_message_id();
        auto file_id = seams_.make_file_id();
        if (!request_id || !file_id)
            return request_id ? file_id.status() : request_id.status();
        if (request_id.value() == 0U || all_zero(file_id.value())) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 allocator returned a zero identity"};
        }
        const std::filesystem::path staging =
            std::filesystem::path(job.policy.root) / "tree-v2" / "incoming" /
            (".receive-" + request_hex(request_id.value()) + ".part");
        const Status removed = remove_staging(staging);
        if (!removed.ok()) return removed;
        auto frame = make_tree_v2_object_request_frame(
            {job.policy.id, object.key.kind, object.key.digest,
             file_id.value()},
            request_id.value());
        if (!frame) return frame.status();
        job.lanes.push_back(ActiveLane{object,
                                       source->source_id,
                                       request_id.value(),
                                       file_id.value(),
                                       staging,
                                       std::nullopt,
                                       std::nullopt,
                                       false,
                                       false});
        ++job.status.requested_objects;
        ++job.status.availability_requests;
        ++source->requested_objects;
        job.status.detail =
            "probing bounded authenticated sources for exact tree-v2 objects";
        dispatches.push_back(
            TreeV2Dispatch{source->context, std::move(frame).value()});
    }
    if (!job.lanes.empty()) {
        if (job.lanes.size() == 1U && !dispatches.empty()) {
            job.status.detail =
                "probing one authenticated source for an exact tree-v2 object";
        }
        return dispatches;
    }

    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    if (job.object_inventory) {
        auto revalidated = revalidate_tree_v2_object_store(
            job.policy, *job.object_inventory, transaction.value());
        if (!revalidated) return revalidated.status();
        ++job.status.cas_full_inventory_scans;
        job.status.cas_inventory_objects_inspected +=
            revalidated.value().inspected_objects;
        ++statistics_.cas_full_inventory_scans;
        statistics_.cas_inventory_objects_inspected +=
            revalidated.value().inspected_objects;
    }
    TreeV2BranchStore store(std::filesystem::path(job.policy.root),
                            config_.identity->public_key(), job.witness);
    std::set<Digest> incorporated;
    for (const auto &[record, branch] : job.branches) {
        if (branch.incorporated) incorporated.insert(record);
    }
    std::size_t remaining = job.branches.size() - incorporated.size();
    for (std::size_t pass = 0U; remaining != 0U && pass <= job.branches.size();
         ++pass) {
        bool progressed = false;
        auto frontier = store.load_frontier(job.policy, *config_.sodium,
                                            transaction.value());
        if (!frontier) return frontier.status();
        for (auto &[record, branch] : job.branches) {
            if (incorporated.contains(record)) continue;
            const auto manifest = job.manifests.find(branch.head.manifest);
            if (manifest == job.manifests.end())
                return Status{ErrorCode::protocol_error,
                              "tree-v2 branch manifest closure is incomplete"};
            bool dependencies = branch.head.checkpoint ||
                                all_zero(branch.head.previous) ||
                                incorporated.contains(branch.head.previous);
            if (!branch.head.checkpoint) {
                for (const TreeV2Observation &observation :
                     branch.head.observations)
                    dependencies =
                        dependencies &&
                        incorporated.contains(observation.record);
            }
            if (!dependencies) continue;
            const auto current = std::find_if(
                frontier.value().begin(), frontier.value().end(),
                [&branch](const TreeV2Snapshot &candidate) {
                    return candidate.head.writer == branch.head.writer;
                });
            if (current != frontier.value().end() &&
                current->head.generation >= branch.head.generation) {
                auto exact = load_tree_v2_stored_record(
                    job.policy, record, *config_.sodium, transaction.value());
                if (!exact) {
                    return Status{
                        ErrorCode::protocol_error,
                        "tree-v2 peer supplied a stale or forked branch"};
                }
                incorporated.insert(record);
                branch.incorporated = true;
                --remaining;
                progressed = true;
                continue;
            }
            auto accepted = store.accept(
                job.policy, TreeV2Snapshot{branch.head, manifest->second},
                *config_.sodium, transaction.value());
            if (!accepted) return accepted.status();
            incorporated.insert(record);
            branch.incorporated = true;
            --remaining;
            ++job.status.accepted_branches;
            progressed = true;
        }
        if (!progressed && remaining != 0U) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 branch proof graph is cyclic, forked, or incomplete"};
        }
    }
    if (remaining != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch proof graph did not converge"};
    }
    auto &source_digest_cache =
        source_digest_caches_[source_digest_cache_key(job.policy,
                                                      job.status.worktree)];
    auto reconciled = reconcile_tree_v2_workspace(
        job.policy, job.status.worktree, *config_.identity, *config_.sodium,
        transaction.value(), job.witness, &source_digest_cache);
    if (!reconciled) return reconciled.status();
    job.status.reconciliation = reconciled.value();
    job.status.conflicts = reconciled.value().conflicts;
    job.status.state = TreeV2PullState::complete;
    job.status.active_file_id.reset();
    job.status.active_file_number.reset();
    job.status.detail =
        job.status.custody_complete
            ? "tree-v2 metadata frontier and complete content custody reconciled"
            : "tree-v2 metadata frontier and selected content custody reconciled";
    return std::vector<TreeV2Dispatch>{};
}

Result<std::vector<TreeV2Dispatch>>
TreeV2SubscriberService::handle_object_result(
    const SyncPeerContext &context, const protocol::Frame &frame) {
    std::scoped_lock lock(mutex_);
    const Status valid = validate_tree_v2_object_result_frame(frame);
    if (!valid.ok()) return valid;
    PullJob *selected_job = nullptr;
    std::size_t selected_lane = 0U;
    for (const auto &owned : jobs_) {
        PullJob &candidate = *owned;
        for (std::size_t index = 0U; index < candidate.lanes.size();
             ++index) {
            ActiveLane &lane = candidate.lanes[index];
            if (lane.request_id != frame.correlation_id) continue;
            const Source *source = source_for(candidate, lane.source_id);
            if (source != nullptr &&
                source->context.friend_number == context.friend_number &&
                source->context.online_epoch == context.online_epoch) {
                selected_job = &candidate;
                selected_lane = index;
                break;
            }
        }
        if (selected_job != nullptr) break;
    }
    if (selected_job == nullptr)
        return Status{ErrorCode::not_found,
                      "tree-v2 object result has no active lane"};
    PullJob &job = *selected_job;
    ActiveLane &lane = job.lanes[selected_lane];
    Source *source = source_for(job, lane.source_id);
    if (source == nullptr || !same_authority(source->context, context)) {
        fail(job, "tree-v2 object authority changed");
        return Status{ErrorCode::unavailable, job.status.detail};
    }
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok()) {
        fail(job, authorized.message());
        return authorized;
    }
    auto decoded = decode_tree_v2_object_result(frame.payload);
    if (!decoded) {
        fail(job, decoded.status().message());
        return decoded.status();
    }
    if (decoded.value().kind != lane.object.key.kind ||
        decoded.value().object != lane.object.key.digest ||
        decoded.value().transfer_id != lane.file_id) {
        fail(job, "tree-v2 result changed its exact object binding");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    ++job.status.availability_results;
    if (decoded.value().status == TreeV2ObjectStatus::denied) {
        fail(job, "tree-v2 source denied an authorized exact-object probe");
        return Status{ErrorCode::unavailable, job.status.detail};
    }
    if (decoded.value().status == TreeV2ObjectStatus::absent ||
        decoded.value().status == TreeV2ObjectStatus::unavailable) {
        if (decoded.value().status == TreeV2ObjectStatus::absent) {
            ++job.status.absent_results;
            ++source->absent_objects;
        } else {
            ++job.status.unavailable_results;
            ++source->unavailable_objects;
        }
        if (lane.offer) {
            const Status cancelled = seams_.cancel_transfer(
                source->context.transfer_carrier,
                lane.offer->file_number);
            if (!cancelled.ok()) {
                fail(job, cancelled.message());
                return cancelled;
            }
        }
        const Status removed = remove_staging(lane.staging);
        if (!removed.ok()) {
            fail(job, removed.message());
            return removed;
        }
        PendingObject object = std::move(lane.object);
        job.lanes.erase(job.lanes.begin() +
                        static_cast<std::ptrdiff_t>(selected_lane));
        job.queue.push_front(std::move(object));
        job.status.detail =
            "exact object absent at one source; probing the next source";
        auto next = drive(job);
        if (!next) {
            fail(job, next.status().message());
            return next.status();
        }
        return next;
    }
    if (decoded.value().status != TreeV2ObjectStatus::offered) {
        fail(job, "tree-v2 source returned an unknown object disposition");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    ++source->offered_objects;
    if (lane.object.expected_bytes &&
        *lane.object.expected_bytes != decoded.value().object_bytes) {
        fail(job, "tree-v2 object result changed its signed size");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    const std::uint64_t maximum =
        lane.object.key.kind == TreeV2ObjectKind::file
            ? job.policy.quotas.maximum_artifact_bytes
            : job.policy.quotas.maximum_manifest_bytes;
    if (decoded.value().object_bytes > maximum) {
        fail(job, "tree-v2 object result exceeds namespace quota");
        return Status{ErrorCode::resource_exhausted, job.status.detail};
    }
    lane.offered_bytes = decoded.value().object_bytes;
    if (lane.offer) {
        const Status admitted = admit_offer(job, selected_lane);
        if (!admitted.ok()) return admitted;
    }
    return std::vector<TreeV2Dispatch>{};
}

Result<std::size_t>
TreeV2SubscriberService::commit_completed_file_batch(PullJob &job) {
    std::vector<std::size_t> completed;
    completed.reserve(job.lanes.size());
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
        const ActiveLane &lane = job.lanes[index];
        if (lane.object.key.kind != TreeV2ObjectKind::file ||
            !lane.transport_complete) {
            // Keep the verified transport result private until the complete
            // bounded lane window can share one full CAS admission pass.
            return std::size_t{0U};
        }
        completed.push_back(index);
    }
    if (completed.empty()) return std::size_t{0U};

    TreeV2ScanResult batch;
    batch.files.reserve(completed.size());
    for (const std::size_t index : completed) {
        const ActiveLane &lane = job.lanes[index];
        if (!lane.offered_bytes) {
            return Status{ErrorCode::internal_error,
                          "tree-v2 completed file lane has no signed size"};
        }
        batch.files.push_back(TreeV2ScannedFile{
            "", lane.object.key.digest, *lane.offered_bytes, lane.staging});
    }

    auto transaction = SyncNamespaceTransaction::acquire(job.policy);
    if (!transaction) return transaction.status();
    if (!job.object_inventory) {
        auto inspected = inspect_tree_v2_object_store(job.policy,
                                                      transaction.value());
        if (!inspected) return inspected.status();
        ++job.status.cas_full_inventory_scans;
        job.status.cas_inventory_objects_inspected += inspected.value().objects();
        ++statistics_.cas_full_inventory_scans;
        statistics_.cas_inventory_objects_inspected +=
            inspected.value().objects();
        job.object_inventory.emplace(std::move(inspected).value());
    }
    auto stored = store_tree_v2_scan_objects(
        job.policy, batch, *job.object_inventory, transaction.value());
    if (!stored) return stored.status();

    for (const std::size_t index : completed) {
        ActiveLane &lane = job.lanes[index];
        Source *source = source_for(job, lane.source_id);
        if (source == nullptr || !lane.offered_bytes) {
            return Status{ErrorCode::internal_error,
                          "tree-v2 completed file source is absent"};
        }
        const Status removed = remove_staging(lane.staging, false);
        if (!removed.ok()) return removed;
        ++job.status.committed_objects;
        job.status.fetched_bytes += *lane.offered_bytes;
        ++source->committed_objects;
        source->fetched_bytes += *lane.offered_bytes;
    }
    const Status staging_synced = sync_directory(
        std::filesystem::path(job.policy.root) / "tree-v2" / "incoming");
    if (!staging_synced.ok()) return staging_synced;
    job.status.reused_objects += stored.value().reused_objects;
    ++job.status.file_commit_batches;
    job.status.largest_file_commit_batch = std::max(
        job.status.largest_file_commit_batch,
        static_cast<std::uint32_t>(completed.size()));
    ++statistics_.file_commit_batches;
    statistics_.file_objects_committed += completed.size();
    statistics_.largest_file_commit_batch = std::max(
        statistics_.largest_file_commit_batch,
        static_cast<std::uint32_t>(completed.size()));
    job.lanes.clear();
    job.status.staged_file_objects = 0U;
    return completed.size();
}

void TreeV2SubscriberService::retire_unoffered_lane(
    PullJob &job, std::size_t lane_index) noexcept {
    if (lane_index >= job.lanes.size()) return;
    const ActiveLane &lane = job.lanes[lane_index];
    if (lane.offer || lane.transport_complete) return;
    const Source *source = source_for(job, lane.source_id);
    if (source == nullptr) return;
    const auto duplicate = std::find_if(
        retired_offers_.begin(), retired_offers_.end(),
        [&lane, source](const RetiredOffer &retired) {
            return retired.friend_number == source->context.friend_number &&
                   retired.online_epoch == source->context.online_epoch &&
                   retired.stable_principal ==
                       source->context.peer_authority.remote_principal &&
                   retired.carrier == source->context.transfer_carrier &&
                   retired.file_id == lane.file_id;
        });
    if (duplicate != retired_offers_.end()) return;
    if (retired_offers_.size() >= kMaximumRetiredTreeOffers) {
        retired_offers_.pop_front();
        ++statistics_.retired_offer_evictions;
    }
    retired_offers_.push_back(RetiredOffer{
        source->context.friend_number,
        source->context.online_epoch,
        source->context.peer_authority.remote_principal,
        source->context.transfer_carrier,
        lane.file_id});
}

Status TreeV2SubscriberService::admit_offer(PullJob &job,
                                            std::size_t lane_index) {
    if (lane_index >= job.lanes.size()) {
        fail(job, "tree-v2 active lane identity is absent");
        return Status{ErrorCode::internal_error, job.status.detail};
    }
    ActiveLane &lane = job.lanes[lane_index];
    Source *source = source_for(job, lane.source_id);
    if (source == nullptr) {
        fail(job, "tree-v2 active source identity is absent");
        return Status{ErrorCode::internal_error, job.status.detail};
    }
    if (!lane.offer || !lane.offered_bytes || lane.transport_complete) {
        return Status{ErrorCode::internal_error,
                      "tree-v2 offer admission state is incomplete"};
    }
    if (lane.admitted) return Status::success();
    if (lane.offer->file_size != *lane.offered_bytes) {
        fail(job, "tree-v2 file offer changed its declared size");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    auto accepted = seams_.receive_to_path(
        source->context.transfer_carrier, lane.offer->file_number,
        lane.staging);
    if (!accepted &&
        accepted.status().code() == ErrorCode::resource_exhausted) {
        job.status.detail =
            "tree-v2 offer retained behind the local receive ceiling";
        return Status::success();
    }
    if (!accepted) {
        fail(job, accepted.status().message());
        return accepted.status();
    }
    if (accepted.value().direction != FileTransferDirection::incoming ||
        accepted.value().friend_number != lane.offer->friend_number ||
        accepted.value().file_number != lane.offer->file_number ||
        accepted.value().file_size != lane.offer->file_size ||
        accepted.value().local_path != lane.staging) {
        fail(job, "tree-v2 receive admission changed its exact binding");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    lane.admitted = true;
    job.status.active_file_number = lane.offer->file_number;
    job.status.detail = "receiving one verified tree-v2 object";
    return Status::success();
}

Result<bool>
TreeV2SubscriberService::handle_offer(const SyncPeerContext &context,
                                      const FileTransferRecord &offer) {
    std::scoped_lock lock(mutex_);
    if (offer.direction != FileTransferDirection::incoming ||
        !offer.has_file_id)
        return false;
    PullJob *selected_job = nullptr;
    std::size_t selected_lane = 0U;
    for (const auto &owned : jobs_) {
        PullJob &candidate = *owned;
        for (std::size_t index = 0U; index < candidate.lanes.size();
             ++index) {
            ActiveLane &lane = candidate.lanes[index];
            if (lane.file_id != offer.file_id) continue;
            const Source *source = source_for(candidate, lane.source_id);
            if (source != nullptr &&
                source->context.friend_number == context.friend_number &&
                source->context.online_epoch == context.online_epoch) {
                selected_job = &candidate;
                selected_lane = index;
                break;
            }
        }
        if (selected_job != nullptr) break;
    }
    if (selected_job == nullptr) {
        const auto retired = std::find_if(
            retired_offers_.begin(), retired_offers_.end(),
            [&context, &offer](const RetiredOffer &candidate) {
                return candidate.friend_number == context.friend_number &&
                       candidate.online_epoch == context.online_epoch &&
                       candidate.stable_principal ==
                           context.peer_authority.remote_principal &&
                       candidate.carrier == context.transfer_carrier &&
                       candidate.file_id == offer.file_id;
            });
        if (retired == retired_offers_.end()) return false;
        const Status cancelled = seams_.cancel_transfer(
            retired->carrier, offer.file_number);
        if (!cancelled.ok()) return cancelled;
        retired_offers_.erase(retired);
        ++statistics_.late_offers_cancelled;
        return true;
    }
    PullJob &job = *selected_job;
    ActiveLane &lane = job.lanes[selected_lane];
    Source *source = source_for(job, lane.source_id);
    if (source == nullptr || !same_authority(source->context, context)) {
        fail(job, "tree-v2 authority changed before file offer");
        return Status{ErrorCode::unavailable, job.status.detail};
    }
    if (lane.offer && lane.offer->file_number != offer.file_number) {
        fail(job, "tree-v2 FileId was reused by another file number");
        return Status{ErrorCode::protocol_error, job.status.detail};
    }
    lane.offer = offer;
    if (!lane.offered_bytes) return true;
    const Status admitted = admit_offer(job, selected_lane);
    return admitted.ok() ? Result<bool>{true} : Result<bool>{admitted};
}

Result<std::vector<TreeV2Dispatch>> TreeV2SubscriberService::handle_terminal(
    const SyncPeerContext &context, const FileTransferRecord &transfer,
    routes::WorkerTransferOutcome outcome, ErrorCode failure) {
    std::scoped_lock lock(mutex_);
    PullJob *selected_job = nullptr;
    std::size_t selected_lane = 0U;
    for (const auto &owned : jobs_) {
        PullJob &candidate = *owned;
        for (std::size_t index = 0U; index < candidate.lanes.size();
             ++index) {
            ActiveLane &lane = candidate.lanes[index];
            if (!lane.offer ||
                lane.offer->file_number != transfer.file_number) {
                continue;
            }
            const Source *source = source_for(candidate, lane.source_id);
            if (source != nullptr &&
                source->context.friend_number == context.friend_number &&
                source->context.online_epoch == context.online_epoch) {
                selected_job = &candidate;
                selected_lane = index;
                break;
            }
        }
        if (selected_job != nullptr) break;
    }
    if (selected_job == nullptr)
        return Status{ErrorCode::not_found,
                      "tree-v2 terminal has no active lane"};
    PullJob &job = *selected_job;
    ActiveLane &lane = job.lanes[selected_lane];
    Source *source = source_for(job, lane.source_id);
    const auto terminal_failure = [&job, this](Status status) {
        fail(job, status.message());
        return Result<std::vector<TreeV2Dispatch>>{status};
    };
    if (source == nullptr || !same_authority(source->context, context))
        return terminal_failure(
            Status{ErrorCode::unavailable,
                   "tree-v2 authority changed before object commit"});
    const Status authorized = authorize_publish(context, job.policy);
    if (!authorized.ok()) return terminal_failure(authorized);
    if (!lane.admitted || !lane.offer || !lane.offered_bytes ||
        lane.transport_complete ||
        outcome != routes::WorkerTransferOutcome::completed ||
        failure != ErrorCode::ok ||
        transfer.direction != FileTransferDirection::incoming ||
        transfer.friend_number != context.friend_number ||
        transfer.file_number != lane.offer->file_number ||
        transfer.file_size != *lane.offered_bytes ||
        transfer.local_path != lane.staging) {
        return terminal_failure(
            Status{ErrorCode::protocol_error,
                   "tree-v2 file transfer did not complete exactly"});
    }

    const PendingObject object = lane.object;
    const std::uint64_t object_bytes = *lane.offered_bytes;
    if (object.key.kind == TreeV2ObjectKind::branch_record) {
        auto bytes = read_private_file(
            lane.staging, job.policy.quotas.maximum_manifest_bytes);
        if (!bytes) return terminal_failure(bytes.status());
        auto head = decode_tree_v2_branch_head(job.policy, bytes.value());
        if (!head) return terminal_failure(head.status());
        const Status verified = verify_tree_v2_branch_head(
            job.policy, head.value(), *config_.sodium);
        if (!verified.ok()) return terminal_failure(verified);
        auto digest = tree_v2_branch_record_digest(job.policy, head.value(),
                                                   *config_.sodium);
        if (!digest || digest.value() != object.key.digest ||
            (head.value().checkpoint &&
             !job.context.tree_checkpoint_negotiated) ||
            !std::binary_search(job.policy.writers.begin(),
                                job.policy.writers.end(),
                                head.value().writer)) {
            return terminal_failure(
                Status{ErrorCode::protocol_error,
                       "tree-v2 branch identity or writer is unauthorized"});
        }
        job.branches[object.key.digest] =
            ReceivedBranch{std::move(head).value(), false};
    } else if (object.key.kind == TreeV2ObjectKind::manifest) {
        auto bytes = read_private_file(
            lane.staging, job.policy.quotas.maximum_manifest_bytes);
        if (!bytes) return terminal_failure(bytes.status());
        auto manifest = decode_tree_v2_manifest(job.policy, bytes.value());
        if (!manifest) return terminal_failure(manifest.status());
        auto digest = tree_v2_manifest_digest(job.policy, manifest.value(),
                                              *config_.sodium);
        if (!digest || digest.value() != object.key.digest) {
            return terminal_failure(
                Status{ErrorCode::protocol_error,
                       "tree-v2 manifest digest does not match request"});
        }
        job.manifests[object.key.digest] = std::move(manifest).value();
    } else {
        // The transfer binding is exact, but the CAS importer remains the
        // authority for content verification and quota admission. Keep this
        // complete file private until every lane in the current window is
        // complete, then import the window through one store inventory pass.
        lane.transport_complete = true;
        lane.admitted = false;
        job.status.staged_file_objects = static_cast<std::uint32_t>(
            std::count_if(job.lanes.begin(), job.lanes.end(),
                          [](const ActiveLane &candidate) {
                              return candidate.object.key.kind ==
                                         TreeV2ObjectKind::file &&
                                     candidate.transport_complete;
                          }));
        job.status.detail =
            "staging a bounded tree-v2 file window for CAS commit";
        for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
            ActiveLane &pending = job.lanes[index];
            if (pending.transport_complete) continue;
            if (pending.offer && pending.offered_bytes && !pending.admitted) {
                const Status admitted = admit_offer(job, index);
                if (!admitted.ok()) return terminal_failure(admitted);
            }
        }
        auto committed = commit_completed_file_batch(job);
        if (!committed) return terminal_failure(committed.status());
        if (committed.value() == 0U)
            return std::vector<TreeV2Dispatch>{};
        auto next = drive(job);
        if (!next) fail(job, next.status().message());
        return next;
    }
    const Status removed = remove_staging(lane.staging);
    if (!removed.ok()) return terminal_failure(removed);
    ++job.status.committed_objects;
    job.status.fetched_bytes += object_bytes;
    ++source->committed_objects;
    source->fetched_bytes += object_bytes;

    // Expand authenticated graph edges only after the exact object is verified.
    const auto enqueue = [&job](TreeV2ObjectKind kind, const Digest &digest,
                                std::optional<std::uint64_t> bytes) -> Status {
        ObjectKey key{kind, digest};
        if (kind == TreeV2ObjectKind::file) {
            if (!bytes)
                return Status{ErrorCode::internal_error,
                              "tree-v2 file object lacks a signed size"};
            const auto prior = job.file_sizes.find(digest);
            if (prior != job.file_sizes.end() && prior->second != *bytes) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 file digest has conflicting signed sizes"};
            }
            job.file_sizes[digest] = *bytes;
        }
        if (job.scheduled.contains(key)) return Status::success();
        if (job.scheduled.size() >= job.policy.quotas.maximum_objects) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 object graph exceeds namespace quota"};
        }
        job.scheduled.insert(key);
        job.queue.push_back(PendingObject{key, bytes, {}});
        return Status::success();
    };
    if (object.key.kind == TreeV2ObjectKind::branch_record) {
        const TreeV2BranchHead &head = job.branches.at(object.key.digest).head;
        if (!head.checkpoint) {
            if (!all_zero(head.previous)) {
                const Status added = enqueue(TreeV2ObjectKind::branch_record,
                                             head.previous, std::nullopt);
                if (!added.ok()) return terminal_failure(added);
            }
            for (const TreeV2Observation &observation : head.observations) {
                const Status added = enqueue(TreeV2ObjectKind::branch_record,
                                             observation.record, std::nullopt);
                if (!added.ok()) return terminal_failure(added);
            }
        }
        const Status added = enqueue(TreeV2ObjectKind::manifest, head.manifest,
                                     head.manifest_bytes);
        if (!added.ok()) return terminal_failure(added);
    } else if (object.key.kind == TreeV2ObjectKind::manifest) {
        for (const TreeV2Entry &entry :
             job.manifests.at(object.key.digest).entries) {
            if (entry.kind != TreeV2EntryKind::file) continue;
            const auto prior = job.file_sizes.find(entry.content);
            if (prior != job.file_sizes.end() &&
                prior->second != entry.content_bytes) {
                return terminal_failure(Status{
                    ErrorCode::protocol_error,
                    "tree-v2 file digest has conflicting signed sizes"});
            }
            job.file_sizes[entry.content] = entry.content_bytes;
            const auto path = std::pair{entry.path, entry.content};
            if (!tree_v2_path_selected(job.policy, entry.path, false)) {
                job.skipped_paths.insert(path);
            } else {
                job.selected_files.insert(entry.content);
                job.selected_paths.insert(path);
                const Status added = enqueue(TreeV2ObjectKind::file,
                                             entry.content,
                                             entry.content_bytes);
                if (!added.ok()) return terminal_failure(added);
            }
            const std::size_t unselected =
                job.file_sizes.size() - job.selected_files.size();
            if (job.scheduled.size() > job.policy.quotas.maximum_objects ||
                unselected > job.policy.quotas.maximum_objects -
                                 job.scheduled.size()) {
                return terminal_failure(
                    Status{ErrorCode::resource_exhausted,
                           "tree-v2 object graph exceeds namespace quota"});
            }
        }
        job.status.manifest_file_objects = job.file_sizes.size();
        job.status.selected_file_objects = job.selected_files.size();
        job.status.skipped_file_objects =
            job.file_sizes.size() - job.selected_files.size();
        job.status.selected_paths = job.selected_paths.size();
        job.status.skipped_paths = job.skipped_paths.size();
    }
    job.lanes.erase(job.lanes.begin() +
                    static_cast<std::ptrdiff_t>(selected_lane));
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
        ActiveLane &pending = job.lanes[index];
        if (!pending.transport_complete && pending.offer &&
            pending.offered_bytes && !pending.admitted) {
            const Status admitted = admit_offer(job, index);
            if (!admitted.ok()) return terminal_failure(admitted);
        }
    }
    auto next = drive(job);
    if (!next) fail(job, next.status().message());
    return next;
}

Status TreeV2SubscriberService::cancel_pull(std::uint64_t job_id) {
    std::scoped_lock lock(mutex_);
    const auto found = std::find_if(
        jobs_.begin(), jobs_.end(), [job_id](const auto &candidate) {
            return candidate->status.job_id == job_id;
        });
    if (found == jobs_.end())
        return Status{ErrorCode::not_found, "tree-v2 pull job was not found"};
    PullJob &job = **found;
    for (std::size_t lane_index = 0U; lane_index < job.lanes.size();
         ++lane_index) {
        ActiveLane &lane = job.lanes[lane_index];
        Source *source = source_for(job, lane.source_id);
        if (source == nullptr) {
            return Status{ErrorCode::internal_error,
                          "tree-v2 active source identity is absent"};
        }
        retire_unoffered_lane(job, lane_index);
        if (lane.offer && !lane.transport_complete) {
            const Status cancelled = seams_.cancel_transfer(
                source->context.transfer_carrier,
                lane.offer->file_number);
            if (!cancelled.ok()) return cancelled;
        }
        const Status removed = remove_staging(lane.staging, false);
        if (!removed.ok()) return removed;
    }
    const Status staging_synced = sync_directory(
        std::filesystem::path(job.policy.root) / "tree-v2" / "incoming");
    if (!staging_synced.ok()) return staging_synced;
    job.lanes.clear();
    job.status.staged_file_objects = 0U;
    job.status.active_file_id.reset();
    job.status.active_file_number.reset();
    job.status.state = TreeV2PullState::cancelled;
    job.status.detail = "tree-v2 pull cancelled";
    return Status::success();
}

Status TreeV2SubscriberService::namespace_mutation_ready(
    std::string_view namespace_id) const {
    std::scoped_lock lock(mutex_);
    const auto active = std::find_if(
        jobs_.begin(), jobs_.end(), [namespace_id](const auto &job) {
            return job->status.namespace_id == namespace_id &&
                   job->status.state != TreeV2PullState::complete &&
                   job->status.state != TreeV2PullState::failed &&
                   job->status.state != TreeV2PullState::cancelled;
        });
    return active == jobs_.end()
               ? Status::success()
               : Status{ErrorCode::unavailable,
                        "tree-v2 namespace has an active pull"};
}

std::vector<TreeV2Dispatch>
TreeV2SubscriberService::peer_offline(std::uint32_t friend_number,
                                      std::uint64_t online_epoch) {
    std::scoped_lock lock(mutex_);
    std::vector<TreeV2Dispatch> dispatches;
    for (const auto &owned : jobs_) {
        PullJob &job = *owned;
        if (job.status.state == TreeV2PullState::complete ||
            job.status.state == TreeV2PullState::failed ||
            job.status.state == TreeV2PullState::cancelled)
            continue;
        Source *offline = nullptr;
        for (Source &source : job.sources) {
            if (source.context.friend_number == friend_number &&
                source.context.online_epoch == online_epoch) {
                source.online = false;
                offline = &source;
            }
        }
        if (offline == nullptr) continue;
        if (job.status.state == TreeV2PullState::awaiting_inventory &&
            job.status.friend_number == friend_number &&
            job.status.online_epoch == online_epoch) {
            fail(job, "tree-v2 primary frontier source went offline");
            continue;
        }
        bool returned = false;
        for (std::size_t remaining = job.lanes.size(); remaining > 0U;
             --remaining) {
            const std::size_t index = remaining - 1U;
            ActiveLane &lane = job.lanes[index];
            if (lane.source_id != offline->source_id) continue;
            if (lane.transport_complete) continue;
            retire_unoffered_lane(job, index);
            if (lane.offer) {
                static_cast<void>(seams_.cancel_transfer(
                    offline->context.transfer_carrier,
                    lane.offer->file_number));
            }
            static_cast<void>(remove_staging(lane.staging, false));
            PendingObject object = std::move(lane.object);
            job.lanes.erase(job.lanes.begin() +
                            static_cast<std::ptrdiff_t>(index));
            job.queue.push_front(std::move(object));
            returned = true;
        }
        if (!returned) continue;
        const Status staging_synced = sync_directory(
            std::filesystem::path(job.policy.root) / "tree-v2" / "incoming");
        if (!staging_synced.ok()) {
            fail(job, staging_synced.message());
            continue;
        }
        auto committed = commit_completed_file_batch(job);
        if (!committed) {
            fail(job, committed.status().message());
            continue;
        }
        auto next = drive(job);
        if (!next) {
            fail(job, next.status().message());
            continue;
        }
        dispatches.insert(dispatches.end(),
                          std::make_move_iterator(next.value().begin()),
                          std::make_move_iterator(next.value().end()));
    }
    return dispatches;
}

std::vector<TreeV2PullSnapshot> TreeV2SubscriberService::snapshot() const {
    std::scoped_lock lock(mutex_);
    std::vector<TreeV2PullSnapshot> result;
    result.reserve(jobs_.size());
    for (const auto &job : jobs_) {
        TreeV2PullSnapshot observed = job->status;
        observed.active_lanes =
            static_cast<std::uint32_t>(job->lanes.size());
        observed.staged_file_objects = static_cast<std::uint32_t>(
            std::count_if(job->lanes.begin(), job->lanes.end(),
                          [](const ActiveLane &lane) {
                              return lane.object.key.kind ==
                                         TreeV2ObjectKind::file &&
                                     lane.transport_complete;
                          }));
        observed.lane_bindings.clear();
        observed.lane_bindings.reserve(job->lanes.size());
        for (const ActiveLane &lane : job->lanes) {
            observed.lane_bindings.push_back(TreeV2LaneSnapshot{
                lane.request_id,
                lane.source_id,
                lane.object.key.kind,
                lane.offered_bytes.value_or(
                    lane.object.expected_bytes.value_or(0U)),
                lane.file_id,
                lane.offer ? std::optional<std::uint32_t>{
                                 lane.offer->file_number}
                           : std::nullopt,
                lane.admitted});
        }
        if (job->lanes.size() == 1U &&
            !job->lanes.front().transport_complete) {
            observed.active_file_id = job->lanes.front().file_id;
            observed.active_file_number =
                job->lanes.front().offer
                    ? std::optional<std::uint32_t>{
                          job->lanes.front().offer->file_number}
                    : std::nullopt;
        } else {
            observed.active_file_id.reset();
            observed.active_file_number.reset();
        }
        observed.source_snapshots.clear();
        observed.source_snapshots.reserve(job->sources.size());
        for (const Source &source : job->sources) {
            observed.source_snapshots.push_back(TreeV2SourceSnapshot{
                source.source_id,
                source.context.friend_number,
                source.context.online_epoch,
                source.context.peer_authority.remote_principal,
                source.online,
                source.requested_objects,
                source.offered_objects,
                source.absent_objects,
                source.unavailable_objects,
                source.committed_objects,
                source.fetched_bytes});
        }
        result.push_back(std::move(observed));
    }
    return result;
}

TreeV2SubscriberSnapshot TreeV2SubscriberService::statistics() const {
    std::scoped_lock lock(mutex_);
    TreeV2SubscriberSnapshot observed = statistics_;
    observed.retired_offer_ids =
        static_cast<std::uint32_t>(retired_offers_.size());
    return observed;
}

void TreeV2SubscriberService::fail(PullJob &job, std::string detail) noexcept {
    for (std::size_t index = 0U; index < job.lanes.size(); ++index) {
        const ActiveLane &lane = job.lanes[index];
        retire_unoffered_lane(job, index);
        Source *source = source_for(job, lane.source_id);
        if (source != nullptr) {
            if (lane.offer && !lane.transport_complete) {
                static_cast<void>(seams_.cancel_transfer(
                    source->context.transfer_carrier,
                    lane.offer->file_number));
            }
        }
        static_cast<void>(remove_staging(lane.staging, false));
    }
    static_cast<void>(sync_directory(
        std::filesystem::path(job.policy.root) / "tree-v2" / "incoming"));
    job.lanes.clear();
    job.status.staged_file_objects = 0U;
    job.status.state = TreeV2PullState::failed;
    job.status.active_file_id.reset();
    job.status.active_file_number.reset();
    job.status.detail = std::move(detail);
}

} // namespace iotox::sync
