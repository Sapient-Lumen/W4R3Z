#include "iotox/sync_multiwriter_workspace.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <sys/stat.h>
#include <unistd.h>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {'I', 'O', 'T', 'X',
                                                 'T', 'W', 'S', '1'};
constexpr std::uint8_t kFormat = 1U;
constexpr std::size_t kNamespaceOffset = 120U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::size_t kPathOffset = kNamespaceOffset + kNamespaceBytes;
constexpr std::size_t kObservationBytes = 72U;
constexpr std::size_t kPendingWorktreeManifestOffset =
    kPathOffset + kTreeV2WorkspacePathBytes;
constexpr std::size_t kActiveFrontierOffset =
    kPendingWorktreeManifestOffset + 32U;
constexpr std::size_t kPendingFrontierOffset =
    kActiveFrontierOffset + kMaximumNamespacePrincipals * kObservationBytes;
constexpr std::size_t kBodyBytes =
    kPendingFrontierOffset + kMaximumNamespacePrincipals * kObservationBytes;
constexpr std::size_t kRecordBytes = kBodyBytes + security::kSignatureBytes;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-tree-v2-workspace-signature-v1";

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

void write_u16(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint16_t value) {
    bytes[offset] = static_cast<std::uint8_t>(value >> 8U);
    bytes[offset + 1U] = static_cast<std::uint8_t>(value);
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index)
        bytes[offset + index] =
            static_cast<std::uint8_t>(value >> ((7U - index) * 8U));
}

[[nodiscard]] std::uint16_t read_u16(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) | bytes[offset + 1U]);
}

[[nodiscard]] std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index)
        value = (value << 8U) | bytes[offset + index];
    return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> bytes, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
    std::copy(value.begin(), value.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> bytes, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), Size,
                value.begin());
}

[[nodiscard]] bool canonical_worktree(const std::filesystem::path &path) {
    const std::string text = path.string();
    return !text.empty() && text.size() <= kTreeV2WorkspacePathBytes &&
           text.find('\0') == std::string::npos && path.is_absolute() &&
           path != path.root_path() && path.lexically_normal() == path;
}

[[nodiscard]] Status
validate_frontier(std::span<const TreeV2Observation> frontier, bool required) {
    if ((required && frontier.empty()) ||
        frontier.size() > kMaximumNamespacePrincipals) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 workspace frontier population is invalid"};
    }
    for (std::size_t index = 0U; index < frontier.size(); ++index) {
        const TreeV2Observation &observation = frontier[index];
        if (all_zero(observation.writer) || observation.generation == 0U ||
            all_zero(observation.record) ||
            (index != 0U &&
             !(frontier[index - 1U].writer < observation.writer))) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 workspace frontier is not canonical"};
        }
    }
    return Status::success();
}

void write_observation(std::span<std::uint8_t> bytes, std::size_t offset,
                       const TreeV2Observation &observation) {
    write_array(bytes, offset, observation.writer);
    write_u64(bytes, offset + 32U, observation.generation);
    write_array(bytes, offset + 40U, observation.record);
}

TreeV2Observation read_observation(std::span<const std::uint8_t> bytes,
                                   std::size_t offset) {
    TreeV2Observation observation;
    read_array(bytes, offset, observation.writer);
    observation.generation = read_u64(bytes, offset + 32U);
    read_array(bytes, offset + 40U, observation.record);
    return observation;
}

[[nodiscard]] Status
inspect_private_directory(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace state directory is not private"};
    }
    return Status::success();
}

[[nodiscard]] Status inspect_owned_worktree(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 worktree is not an owner-controlled directory"};
    }
    return Status::success();
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
read_state(const std::filesystem::path &path) {
    const int descriptor =
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{errno == ENOENT ? ErrorCode::not_found
                                      : ErrorCode::io_error,
                      "unable to open tree-v2 workspace state: " +
                          std::string(std::strerror(errno))};
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() || metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) ||
        metadata.st_size != static_cast<off_t>(kRecordBytes)) {
        static_cast<void>(::close(descriptor));
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace state is not one exact private file"};
    }
    std::vector<std::uint8_t> bytes(kRecordBytes);
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count =
            ::read(descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        static_cast<void>(::close(descriptor));
        return Status{ErrorCode::io_error,
                      "unable to read complete tree-v2 workspace state"};
    }
    if (::close(descriptor) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close tree-v2 workspace state"};
    }
    return bytes;
}

[[nodiscard]] Result<std::array<std::uint8_t, kBodyBytes>>
encode_body(const TreeV2WorkspaceState &state) {
    const Status valid = validate_tree_v2_workspace_state(state);
    if (!valid.ok()) return valid;
    const std::string path = state.worktree.string();
    std::array<std::uint8_t, kBodyBytes> body{};
    std::copy(kMagic.begin(), kMagic.end(), body.begin());
    body[8U] = kFormat;
    body[9U] = static_cast<std::uint8_t>(state.phase);
    body[10U] = static_cast<std::uint8_t>(state.namespace_id.size());
    body[11U] = static_cast<std::uint8_t>(state.active_frontier.size());
    body[12U] = static_cast<std::uint8_t>(state.pending_frontier.size());
    write_u16(body, 14U, static_cast<std::uint16_t>(path.size()));
    write_u64(body, 16U, state.generation);
    write_array(body, 24U, state.active_manifest);
    write_array(body, 56U, state.pending_manifest);
    write_array(body, 88U, state.signer);
    std::copy(state.namespace_id.begin(), state.namespace_id.end(),
              body.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
    std::copy(path.begin(), path.end(),
              body.begin() + static_cast<std::ptrdiff_t>(kPathOffset));
    write_array(body, kPendingWorktreeManifestOffset,
                state.pending_worktree_manifest);
    for (std::size_t index = 0U; index < state.active_frontier.size();
         ++index) {
        write_observation(body,
                          kActiveFrontierOffset + index * kObservationBytes,
                          state.active_frontier[index]);
    }
    for (std::size_t index = 0U; index < state.pending_frontier.size();
         ++index) {
        write_observation(body,
                          kPendingFrontierOffset + index * kObservationBytes,
                          state.pending_frontier[index]);
    }
    return body;
}

} // namespace

std::string_view
tree_v2_workspace_phase_name(TreeV2WorkspacePhase phase) noexcept {
    switch (phase) {
    case TreeV2WorkspacePhase::stable:
        return "stable";
    case TreeV2WorkspacePhase::pending_exchange:
        return "pending-exchange";
    }
    return "unknown";
}

std::string_view
tree_v2_workspace_decision_name(TreeV2WorkspaceDecision decision) noexcept {
    switch (decision) {
    case TreeV2WorkspaceDecision::initialized:
        return "initialized";
    case TreeV2WorkspaceDecision::begun:
        return "begun";
    case TreeV2WorkspaceDecision::finished:
        return "finished";
    case TreeV2WorkspaceDecision::duplicate:
        return "duplicate";
    }
    return "unknown";
}

Status validate_tree_v2_workspace_state(const TreeV2WorkspaceState &state) {
    const Status active_frontier =
        validate_frontier(state.active_frontier, true);
    if (!active_frontier.ok()) return active_frontier;
    const Status pending_frontier = validate_frontier(
        state.pending_frontier,
        state.phase == TreeV2WorkspacePhase::pending_exchange);
    if (!pending_frontier.ok()) return pending_frontier;
    if (!valid_namespace_id(state.namespace_id) ||
        state.namespace_id.size() > kNamespaceBytes ||
        !canonical_worktree(state.worktree) || state.generation == 0U ||
        all_zero(state.active_manifest) || all_zero(state.signer)) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 workspace identity is invalid"};
    }
    if (state.phase == TreeV2WorkspacePhase::stable) {
        if (!all_zero(state.pending_manifest) ||
            !all_zero(state.pending_worktree_manifest) ||
            !state.pending_frontier.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "stable tree-v2 workspace retains a pending target"};
        }
    } else if (state.phase == TreeV2WorkspacePhase::pending_exchange) {
        if (all_zero(state.pending_manifest) ||
            all_zero(state.pending_worktree_manifest) ||
            (state.pending_manifest == state.active_manifest &&
             state.pending_frontier == state.active_frontier)) {
            return Status{ErrorCode::invalid_argument,
                          "pending tree-v2 workspace target is invalid"};
        }
    } else {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 workspace phase is invalid"};
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_workspace_state(const TreeV2WorkspaceState &state) {
    auto body = encode_body(state);
    if (!body) return body.status();
    std::vector<std::uint8_t> output(body.value().begin(), body.value().end());
    output.insert(output.end(), state.signature.begin(), state.signature.end());
    return output;
}

Result<TreeV2WorkspaceState>
decode_tree_v2_workspace_state(std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kRecordBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[8U] != kFormat || bytes[10U] == 0U ||
        bytes[10U] > kNamespaceBytes || bytes[11U] == 0U ||
        bytes[11U] > kMaximumNamespacePrincipals ||
        bytes[12U] > kMaximumNamespacePrincipals || bytes[13U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace record header is invalid"};
    }
    const std::size_t namespace_bytes = bytes[10U];
    const std::size_t active_frontier = bytes[11U];
    const std::size_t pending_frontier = bytes[12U];
    const std::size_t path_bytes = read_u16(bytes, 14U);
    if (path_bytes == 0U || path_bytes > kTreeV2WorkspacePathBytes ||
        !all_zero(bytes.subspan(kNamespaceOffset + namespace_bytes,
                                kNamespaceBytes - namespace_bytes)) ||
        !all_zero(bytes.subspan(kPathOffset + path_bytes,
                                kTreeV2WorkspacePathBytes - path_bytes)) ||
        !all_zero(bytes.subspan(
            kActiveFrontierOffset + active_frontier * kObservationBytes,
            (kMaximumNamespacePrincipals - active_frontier) *
                kObservationBytes)) ||
        !all_zero(bytes.subspan(
            kPendingFrontierOffset + pending_frontier * kObservationBytes,
            (kMaximumNamespacePrincipals - pending_frontier) *
                kObservationBytes))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace record padding is invalid"};
    }
    TreeV2WorkspaceState state;
    state.phase = static_cast<TreeV2WorkspacePhase>(bytes[9U]);
    state.generation = read_u64(bytes, 16U);
    read_array(bytes, 24U, state.active_manifest);
    read_array(bytes, 56U, state.pending_manifest);
    read_array(bytes, 88U, state.signer);
    read_array(bytes, kPendingWorktreeManifestOffset,
               state.pending_worktree_manifest);
    state.namespace_id.assign(
        reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
        namespace_bytes);
    state.worktree = std::string(
        reinterpret_cast<const char *>(bytes.data() + kPathOffset), path_bytes);
    state.active_frontier.reserve(active_frontier);
    for (std::size_t index = 0U; index < active_frontier; ++index) {
        state.active_frontier.push_back(read_observation(
            bytes, kActiveFrontierOffset + index * kObservationBytes));
    }
    state.pending_frontier.reserve(pending_frontier);
    for (std::size_t index = 0U; index < pending_frontier; ++index) {
        state.pending_frontier.push_back(read_observation(
            bytes, kPendingFrontierOffset + index * kObservationBytes));
    }
    read_array(bytes, kBodyBytes, state.signature);
    auto canonical = encode_tree_v2_workspace_state(state);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace record is not canonical"};
    }
    return state;
}

Status verify_tree_v2_workspace_state(
    const TreeV2WorkspaceState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    if (all_zero(expected_device) || state.signer != expected_device) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace signer is not this device"};
    }
    auto body = encode_body(state);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    return sodium.verify_detached(state.signature, digest.value(),
                                  state.signer);
}

TreeV2WorkspaceStore::TreeV2WorkspaceStore(
    std::filesystem::path namespace_root,
    std::shared_ptr<TreeV2StateWitness> witness)
    : root_(std::move(namespace_root)), witness_(std::move(witness)) {}

Result<std::optional<TreeV2WorkspaceState>>
TreeV2WorkspaceStore::load(const NamespacePolicy &policy,
                           const security::SigningPublicKey &expected_device,
                           const security::Sodium &sodium,
                           const SyncNamespaceTransaction *transaction) const {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    if (policy.engine != Engine::tree_v2 ||
        root_.lexically_normal().string() != policy.root) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 workspace store policy is invalid"};
    }
    if (witness_) {
        if (transaction == nullptr) {
            return Status{ErrorCode::invalid_argument,
                          "witnessed tree-v2 workspace read requires its namespace transaction"};
        }
        const Status fresh = witness_->verify_read(policy, *transaction);
        if (!fresh.ok()) return fresh;
    }
    const Status private_root = inspect_private_directory(root_ / "tree-v2");
    if (!private_root.ok()) return private_root;
    auto bytes = read_state(root_ / "tree-v2" / "workspace.state");
    if (!bytes) {
        if (bytes.status().code() == ErrorCode::not_found)
            return std::optional<TreeV2WorkspaceState>{};
        return bytes.status();
    }
    auto state = decode_tree_v2_workspace_state(bytes.value());
    if (!state) return state.status();
    const auto allowed = [&policy](const TreeV2Observation &observation) {
        return std::binary_search(policy.writers.begin(), policy.writers.end(),
                                  observation.writer);
    };
    if (!std::all_of(state.value().active_frontier.begin(),
                     state.value().active_frontier.end(), allowed) ||
        !std::all_of(state.value().pending_frontier.begin(),
                     state.value().pending_frontier.end(), allowed)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace frontier contains a non-writer"};
    }
    const Status verified =
        verify_tree_v2_workspace_state(state.value(), expected_device, sodium);
    if (!verified.ok()) {
        return Status{verified.code(),
                      "tree-v2 workspace state authentication failed: " +
                          verified.message()};
    }
    if (state.value().namespace_id != policy.id) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace namespace does not match policy"};
    }
    return std::optional<TreeV2WorkspaceState>{state.value()};
}

Result<TreeV2WorkspaceStoreResult>
TreeV2WorkspaceStore::commit(const NamespacePolicy &policy,
                             TreeV2WorkspaceState state,
                             TreeV2WorkspaceDecision decision,
                             const security::DeviceIdentity &identity,
                             const security::Sodium &sodium,
                             const SyncNamespaceTransaction *transaction) const {
    state.signer = identity.public_key();
    auto body = encode_body(state);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    state.signature = signature.value();
    const Status verified =
        verify_tree_v2_workspace_state(state, identity.public_key(), sodium);
    if (!verified.ok()) return verified;
    auto encoded = encode_tree_v2_workspace_state(state);
    if (!encoded) return encoded.status();
    const auto store = [&]() {
        return StateStore::write_atomic(
            root_ / "tree-v2" / "workspace.state", encoded.value());
    };
    Status stored;
    if (witness_) {
        if (transaction == nullptr) {
            return Status{ErrorCode::invalid_argument,
                          "witnessed tree-v2 workspace transition requires its namespace transaction"};
        }
        stored = witness_->transition(
            policy, *transaction,
            [&state](const TreeV2FreshnessState &current) {
                TreeV2FreshnessState next = current;
                next.workspace = state;
                return Result<TreeV2FreshnessState>{std::move(next)};
            },
            store);
    } else {
        stored = store();
    }
    if (!stored.ok()) return stored;
    return TreeV2WorkspaceStoreResult{decision, std::move(state)};
}

Result<TreeV2WorkspaceStoreResult> TreeV2WorkspaceStore::initialize(
    const NamespacePolicy &policy, const std::filesystem::path &worktree,
    const Digest &active_manifest,
    std::span<const TreeV2Observation> active_frontier,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction *transaction) const {
    const Status controlled = inspect_owned_worktree(worktree);
    if (!controlled.ok()) return controlled;
    if (!std::all_of(active_frontier.begin(), active_frontier.end(),
                     [&policy](const TreeV2Observation &observation) {
                         return std::binary_search(policy.writers.begin(),
                                                   policy.writers.end(),
                                                   observation.writer);
                     })) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 workspace frontier contains a non-writer"};
    }
    auto current = load(policy, identity.public_key(), sodium, transaction);
    if (!current) return current.status();
    if (current.value()) {
        if (current.value()->worktree == worktree &&
            current.value()->phase == TreeV2WorkspacePhase::stable &&
            current.value()->active_manifest == active_manifest &&
            current.value()->active_frontier ==
                std::vector<TreeV2Observation>(active_frontier.begin(),
                                               active_frontier.end())) {
            return TreeV2WorkspaceStoreResult{
                TreeV2WorkspaceDecision::duplicate, *current.value()};
        }
        return Status{ErrorCode::unavailable,
                      "tree-v2 workspace is already initialized differently"};
    }
    TreeV2WorkspaceState state;
    state.namespace_id = policy.id;
    state.worktree = worktree;
    state.generation = 1U;
    state.active_manifest = active_manifest;
    state.active_frontier.assign(active_frontier.begin(),
                                 active_frontier.end());
    return commit(policy, std::move(state),
                  TreeV2WorkspaceDecision::initialized, identity, sodium,
                  transaction);
}

Result<TreeV2WorkspaceStoreResult> TreeV2WorkspaceStore::begin_exchange(
    const NamespacePolicy &policy, const Digest &expected_active,
    const Digest &pending_manifest, const Digest &worktree_manifest,
    std::span<const TreeV2Observation> pending_frontier,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction *transaction) const {
    if (!std::all_of(pending_frontier.begin(), pending_frontier.end(),
                     [&policy](const TreeV2Observation &observation) {
                         return std::binary_search(policy.writers.begin(),
                                                   policy.writers.end(),
                                                   observation.writer);
                     })) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 pending frontier contains a non-writer"};
    }
    auto current = load(policy, identity.public_key(), sodium, transaction);
    if (!current) return current.status();
    if (!current.value()) {
        return Status{ErrorCode::not_found,
                      "tree-v2 workspace is not initialized"};
    }
    TreeV2WorkspaceState state = *current.value();
    if (state.phase == TreeV2WorkspacePhase::pending_exchange &&
        state.active_manifest == expected_active &&
        state.pending_manifest == pending_manifest &&
        state.pending_worktree_manifest == worktree_manifest &&
        state.pending_frontier ==
            std::vector<TreeV2Observation>(pending_frontier.begin(),
                                           pending_frontier.end())) {
        return TreeV2WorkspaceStoreResult{TreeV2WorkspaceDecision::duplicate,
                                          std::move(state)};
    }
    if (state.phase != TreeV2WorkspacePhase::stable ||
        state.active_manifest != expected_active ||
        (pending_manifest == expected_active &&
         state.active_frontier ==
             std::vector<TreeV2Observation>(pending_frontier.begin(),
                                            pending_frontier.end())) ||
        all_zero(pending_manifest) || all_zero(worktree_manifest) ||
        pending_frontier.empty() ||
        state.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 workspace begin transition is stale or invalid"};
    }
    ++state.generation;
    state.phase = TreeV2WorkspacePhase::pending_exchange;
    state.pending_manifest = pending_manifest;
    state.pending_worktree_manifest = worktree_manifest;
    state.pending_frontier.assign(pending_frontier.begin(),
                                  pending_frontier.end());
    return commit(policy, std::move(state), TreeV2WorkspaceDecision::begun,
                  identity, sodium, transaction);
}

Result<TreeV2WorkspaceStoreResult>
TreeV2WorkspaceStore::finish_exchange(const NamespacePolicy &policy,
                                      const Digest &pending_manifest,
                                      const security::DeviceIdentity &identity,
                                      const security::Sodium &sodium,
                                      const SyncNamespaceTransaction *transaction) const {
    auto current = load(policy, identity.public_key(), sodium, transaction);
    if (!current) return current.status();
    if (!current.value()) {
        return Status{ErrorCode::not_found,
                      "tree-v2 workspace is not initialized"};
    }
    TreeV2WorkspaceState state = *current.value();
    if (state.phase == TreeV2WorkspacePhase::stable &&
        state.active_manifest == pending_manifest) {
        return TreeV2WorkspaceStoreResult{TreeV2WorkspaceDecision::duplicate,
                                          std::move(state)};
    }
    if (state.phase != TreeV2WorkspacePhase::pending_exchange ||
        state.pending_manifest != pending_manifest ||
        state.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 workspace finish transition is stale or invalid"};
    }
    ++state.generation;
    state.phase = TreeV2WorkspacePhase::stable;
    state.active_manifest = pending_manifest;
    state.pending_manifest = {};
    state.pending_worktree_manifest = {};
    state.active_frontier = std::move(state.pending_frontier);
    state.pending_frontier.clear();
    return commit(policy, std::move(state), TreeV2WorkspaceDecision::finished,
                  identity, sodium, transaction);
}

} // namespace iotox::sync
