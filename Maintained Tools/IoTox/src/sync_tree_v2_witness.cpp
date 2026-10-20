#include "iotox/sync_tree_v2_witness.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_multiwriter_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kGuardMagic = {'I', 'O', 'T', 'X',
                                                      'T', 'V', 'G', '1'};
constexpr std::size_t kGuardBodyBytes = 176U;
constexpr std::size_t kGuardBytes = kGuardBodyBytes + security::kSignatureBytes;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::string_view kGuardSignatureDomain =
    "iotox-sync-tree-v2-rollback-guard-signature-v1";
constexpr std::string_view kDomainDerivation =
    "iotox-sync-tree-v2-witness-domain-v1";
constexpr std::string_view kHeadDigestDomain =
    "iotox-sync-tree-v2-state-head-v1";

struct TreeV2Guard {
  std::string namespace_id;
  security::SigningPublicKey signer{};
  security::Digest committed{};
  std::optional<security::Digest> pending;
  security::Signature signature{};
};

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
  return std::all_of(bytes.begin(), bytes.end(),
                     [](std::uint8_t byte) { return byte == 0U; });
}

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
  output.push_back(static_cast<std::uint8_t>(value >> 24U));
  output.push_back(static_cast<std::uint8_t>(value >> 16U));
  output.push_back(static_cast<std::uint8_t>(value >> 8U));
  output.push_back(static_cast<std::uint8_t>(value));
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    output.push_back(static_cast<std::uint8_t>(value >> ((7U - index) * 8U)));
  }
}

void append_bytes(std::vector<std::uint8_t> &output,
                  std::span<const std::uint8_t> value) {
  output.insert(output.end(), value.begin(), value.end());
}

void append_string(std::vector<std::uint8_t> &output, std::string_view value) {
  append_u32(output, static_cast<std::uint32_t>(value.size()));
  output.insert(output.end(), value.begin(), value.end());
}

[[nodiscard]] bool
same_storage_identity(const NamespacePolicy &left,
                      const NamespacePolicy &right) noexcept {
  return left.id == right.id && left.root == right.root &&
         left.engine == right.engine && left.quotas == right.quotas;
}

[[nodiscard]] Status validate_policy(const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.engine != Engine::tree_v2) {
    return Status{ErrorCode::unsupported,
                  "tree-v2 witness requires a tree-v2 namespace"};
  }
  return Status::success();
}

[[nodiscard]] std::filesystem::path guard_path(const NamespacePolicy &policy) {
  return std::filesystem::path(policy.root) / "rollback-guards" /
         (policy.id + ".tree-v2-rollback-guard");
}

[[nodiscard]] Status validate_guard(const TreeV2Guard &guard) {
  if (!valid_namespace_id(guard.namespace_id) || all_zero(guard.signer) ||
      all_zero(guard.committed) ||
      (guard.pending &&
       (all_zero(*guard.pending) || *guard.pending == guard.committed))) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard is invalid"};
  }
  return Status::success();
}

[[nodiscard]] Result<std::array<std::uint8_t, kGuardBodyBytes>>
encode_guard_body(const TreeV2Guard &guard) {
  const Status valid = validate_guard(guard);
  if (!valid.ok())
    return valid;
  std::array<std::uint8_t, kGuardBodyBytes> body{};
  std::copy(kGuardMagic.begin(), kGuardMagic.end(), body.begin());
  body[8U] = 1U;
  body[9U] = guard.pending ? 1U : 0U;
  body[10U] = static_cast<std::uint8_t>(guard.namespace_id.size());
  std::copy(guard.signer.begin(), guard.signer.end(), body.begin() + 16U);
  std::copy(guard.namespace_id.begin(), guard.namespace_id.end(),
            body.begin() + 48U);
  std::copy(guard.committed.begin(), guard.committed.end(),
            body.begin() + 112U);
  if (guard.pending) {
    std::copy(guard.pending->begin(), guard.pending->end(),
              body.begin() + 144U);
  }
  return body;
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_guard(const TreeV2Guard &guard) {
  auto body = encode_guard_body(guard);
  if (!body)
    return body.status();
  std::vector<std::uint8_t> bytes(body.value().begin(), body.value().end());
  bytes.insert(bytes.end(), guard.signature.begin(), guard.signature.end());
  return bytes;
}

[[nodiscard]] Result<TreeV2Guard>
decode_guard(std::span<const std::uint8_t> bytes) {
  if (bytes.size() != kGuardBytes ||
      !std::equal(kGuardMagic.begin(), kGuardMagic.end(), bytes.begin()) ||
      bytes[8U] != 1U || bytes[9U] > 1U || bytes[10U] == 0U ||
      bytes[10U] > kNamespaceBytes || !all_zero(bytes.subspan(11U, 5U)) ||
      !all_zero(
          bytes.subspan(48U + bytes[10U], kNamespaceBytes - bytes[10U]))) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard header is invalid"};
  }
  TreeV2Guard guard;
  std::copy_n(bytes.begin() + 16U, guard.signer.size(), guard.signer.begin());
  guard.namespace_id.assign(reinterpret_cast<const char *>(bytes.data() + 48U),
                            bytes[10U]);
  std::copy_n(bytes.begin() + 112U, guard.committed.size(),
              guard.committed.begin());
  if (bytes[9U] == 1U) {
    security::Digest pending{};
    std::copy_n(bytes.begin() + 144U, pending.size(), pending.begin());
    guard.pending = pending;
  } else if (!all_zero(bytes.subspan(144U, 32U))) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard has unflagged pending bytes"};
  }
  std::copy_n(bytes.begin() + kGuardBodyBytes, guard.signature.size(),
              guard.signature.begin());
  const Status valid = validate_guard(guard);
  if (!valid.ok())
    return valid;
  auto canonical = encode_guard(guard);
  if (!canonical || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard is not canonical"};
  }
  return guard;
}

[[nodiscard]] Status
verify_guard(const NamespacePolicy &policy, const TreeV2Guard &guard,
             const security::SigningPublicKey &expected_device,
             const security::Sodium &sodium) {
  if (guard.namespace_id != policy.id || guard.signer != expected_device ||
      all_zero(expected_device)) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard identity is unexpected"};
  }
  auto body = encode_guard_body(guard);
  if (!body)
    return body.status();
  auto digest = sodium.hash(kGuardSignatureDomain, body.value());
  if (!digest)
    return digest.status();
  return sodium.verify_detached(guard.signature, digest.value(),
                                expected_device);
}

[[nodiscard]] Result<std::optional<TreeV2Guard>>
load_guard(const NamespacePolicy &policy,
           const security::SigningPublicKey &expected_device,
           const security::Sodium &sodium) {
  const std::filesystem::path path = guard_path(policy);
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) {
    if (errno == ENOENT) {
      return std::optional<TreeV2Guard>{};
    }
    return Status{ErrorCode::io_error,
                  "unable to open tree-v2 rollback guard: " +
                      std::string(std::strerror(errno))};
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
      metadata.st_uid != ::geteuid() || metadata.st_nlink != 1 ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size != static_cast<off_t>(kGuardBytes)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::protocol_error,
                  "tree-v2 rollback guard is not one private file"};
  }
  std::vector<std::uint8_t> bytes(kGuardBytes);
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::read(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "unable to read complete tree-v2 rollback guard"};
  }
  if (::close(descriptor) != 0) {
    return Status{ErrorCode::io_error,
                  "unable to close tree-v2 rollback guard"};
  }
  auto guard = decode_guard(bytes);
  if (!guard)
    return guard.status();
  const Status verified =
      verify_guard(policy, guard.value(), expected_device, sodium);
  if (!verified.ok())
    return verified;
  return std::optional<TreeV2Guard>{std::move(guard).value()};
}

[[nodiscard]] Status write_guard(const NamespacePolicy &policy,
                                 TreeV2Guard guard,
                                 const security::DeviceIdentity &identity,
                                 const security::Sodium &sodium) {
  guard.namespace_id = policy.id;
  guard.signer = identity.public_key();
  auto body = encode_guard_body(guard);
  if (!body)
    return body.status();
  auto digest = sodium.hash(kGuardSignatureDomain, body.value());
  if (!digest)
    return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature)
    return signature.status();
  guard.signature = signature.value();
  auto bytes = encode_guard(guard);
  if (!bytes)
    return bytes.status();
  std::error_code error;
  const std::filesystem::path directory =
      std::filesystem::path(policy.root) / "rollback-guards";
  std::filesystem::create_directories(directory, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to create tree-v2 rollback guard directory: " +
                      error.message()};
  }
  std::filesystem::permissions(directory, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return Status{ErrorCode::io_error,
                  "unable to secure tree-v2 rollback guard directory: " +
                      error.message()};
  }
  return StateStore::write_atomic(guard_path(policy), bytes.value());
}

[[nodiscard]] bool
same_selector(const rollback_witness::Record &record,
              const TreeV2StateWitness::Config &config,
              const security::DeviceIdentity &identity) noexcept {
  return record.domain == config.domain &&
         security::constant_time_equal(record.device, identity.public_key()) &&
         record.witness_epoch == config.witness_epoch &&
         record.lane == rollback_witness::Lane::tree_v2_state;
}

[[nodiscard]] Status validate_config(const TreeV2StateWitness::Config &config,
                                     const NamespacePolicy &policy,
                                     const security::DeviceIdentity &identity) {
  const Status valid = validate_policy(policy);
  if (!valid.ok())
    return valid;
  rollback_witness::Record selector;
  selector.domain = config.domain;
  selector.device = identity.public_key();
  selector.witness_epoch = config.witness_epoch;
  selector.lane = rollback_witness::Lane::tree_v2_state;
  if (!config.backend || !rollback_witness::validate(selector).ok()) {
    return Status{ErrorCode::invalid_argument,
                  "tree-v2 witness configuration is invalid"};
  }
  if (!config.backend->independently_controlled() &&
      !config.allow_non_independent_for_testing) {
    return Status{ErrorCode::unsupported,
                  "tree-v2 witness shares the local failure domain"};
  }
  return Status::success();
}

[[nodiscard]] Status resolve_cas(rollback_witness::Backend &backend,
                                 const rollback_witness::Record &expected,
                                 const rollback_witness::Record &desired,
                                 std::string_view label) {
  const Status exchanged = backend.compare_exchange(expected, desired);
  if (exchanged.ok())
    return exchanged;
  auto observed = backend.query();
  if (observed && observed.value() == desired)
    return Status::success();
  return Status{exchanged.code(),
                std::string(label) + ": " + exchanged.message()};
}

[[nodiscard]] std::vector<TreeV2Observation>
observations(const NamespacePolicy &policy,
             std::span<const TreeV2Snapshot> frontier,
             const security::Sodium &sodium, Status &status) {
  std::vector<TreeV2Observation> result;
  result.reserve(frontier.size());
  for (const TreeV2Snapshot &snapshot : frontier) {
    auto record = tree_v2_branch_record_digest(policy, snapshot.head, sodium);
    if (!record) {
      status = record.status();
      return {};
    }
    result.push_back(TreeV2Observation{
        snapshot.head.writer, snapshot.head.generation, record.value()});
  }
  std::sort(result.begin(), result.end(),
            [](const auto &left, const auto &right) {
              return left.writer < right.writer;
            });
  status = Status::success();
  return result;
}

} // namespace

Result<rollback_witness::DomainId>
derive_tree_v2_witness_domain(const rollback_witness::DomainId &base_domain,
                              const security::SigningPublicKey &device,
                              std::string_view namespace_id,
                              const security::Sodium &sodium) {
  if (all_zero(base_domain) || all_zero(device) ||
      !valid_namespace_id(namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "tree-v2 witness domain inputs are invalid"};
  }
  std::vector<std::uint8_t> material;
  material.reserve(base_domain.size() + device.size() + 4U +
                   namespace_id.size());
  append_bytes(material, base_domain);
  append_bytes(material, device);
  append_string(material, namespace_id);
  auto digest = sodium.hash(kDomainDerivation, material);
  if (!digest)
    return digest.status();
  rollback_witness::DomainId result{};
  std::copy_n(digest.value().begin(), result.size(), result.begin());
  if (all_zero(result)) {
    return Status{ErrorCode::protocol_error,
                  "derived tree-v2 witness domain is zero"};
  }
  return result;
}

Result<TreeV2FreshnessState>
load_tree_v2_freshness_state(const NamespacePolicy &policy,
                             const security::SigningPublicKey &expected_device,
                             const security::Sodium &sodium,
                             const SyncNamespaceTransaction &transaction) {
  const Status valid = validate_policy(policy);
  if (!valid.ok())
    return valid;
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  TreeV2BranchStore branches{std::filesystem::path(policy.root)};
  auto frontier = branches.load_frontier(policy, sodium, transaction);
  if (!frontier)
    return frontier.status();
  Status converted;
  auto branch_roots = observations(policy, frontier.value(), sodium, converted);
  if (!converted.ok())
    return converted;
  TreeV2MaintenanceStore maintenance{std::filesystem::path(policy.root)};
  auto maintenance_state =
      maintenance.load(policy, expected_device, sodium, transaction);
  if (!maintenance_state)
    return maintenance_state.status();
  TreeV2WorkspaceStore workspace{std::filesystem::path(policy.root)};
  auto workspace_state = workspace.load(policy, expected_device, sodium);
  if (!workspace_state)
    return workspace_state.status();
  return TreeV2FreshnessState{std::move(branch_roots),
                              std::move(maintenance_state).value(),
                              std::move(workspace_state).value()};
}

Result<security::Digest>
tree_v2_freshness_digest(const NamespacePolicy &policy,
                         const TreeV2FreshnessState &state,
                         const security::Sodium &sodium) {
  const Status valid = validate_policy(policy);
  if (!valid.ok())
    return valid;
  if (policy.id.size() > std::numeric_limits<std::uint32_t>::max() ||
      policy.root.size() > std::numeric_limits<std::uint32_t>::max() ||
      state.frontier.size() > kMaximumNamespacePrincipals ||
      !std::is_sorted(state.frontier.begin(), state.frontier.end(),
                      [](const auto &left, const auto &right) {
                        return left.writer < right.writer;
                      })) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 freshness state is not bounded and canonical"};
  }
  for (std::size_t index = 0U; index < state.frontier.size(); ++index) {
    const TreeV2Observation &root = state.frontier[index];
    if (root.generation == 0U || all_zero(root.writer) ||
        all_zero(root.record) ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            root.writer) ||
        (index != 0U && state.frontier[index - 1U].writer == root.writer)) {
      return Status{ErrorCode::protocol_error,
                    "tree-v2 frontier root is invalid"};
    }
  }
  std::vector<std::uint8_t> material;
  material.reserve(512U + policy.id.size() + policy.root.size() +
                   state.frontier.size() * 72U);
  append_string(material, policy.id);
  append_string(material, policy.root);
  material.push_back(static_cast<std::uint8_t>(policy.engine));
  const std::array<std::uint64_t, 9U> quotas{
      {policy.quotas.maximum_artifact_bytes,
       policy.quotas.maximum_manifest_bytes, policy.quotas.maximum_store_bytes,
       policy.quotas.maximum_staging_bytes, policy.quotas.maximum_objects,
       policy.quotas.maximum_retained_revisions, policy.quotas.maximum_peers,
       policy.quotas.maximum_lanes,
       policy.quotas.maximum_outstanding_requests}};
  for (const std::uint64_t quota : quotas)
    append_u64(material, quota);
  append_u32(material, static_cast<std::uint32_t>(state.frontier.size()));
  for (const TreeV2Observation &root : state.frontier) {
    append_bytes(material, root.writer);
    append_u64(material, root.generation);
    append_bytes(material, root.record);
  }
  if (state.maintenance.mutation == 0U) {
    material.push_back(0U);
  } else {
    auto encoded = encode_tree_v2_maintenance_state(state.maintenance);
    if (!encoded)
      return encoded.status();
    material.push_back(1U);
    append_u32(material, static_cast<std::uint32_t>(encoded.value().size()));
    append_bytes(material, encoded.value());
  }
  if (!state.workspace) {
    material.push_back(0U);
  } else {
    auto encoded = encode_tree_v2_workspace_state(*state.workspace);
    if (!encoded)
      return encoded.status();
    material.push_back(1U);
    append_u32(material, static_cast<std::uint32_t>(encoded.value().size()));
    append_bytes(material, encoded.value());
  }
  return sodium.hash(kHeadDigestDomain, material);
}

Result<rollback_witness::Record> tree_v2_state_enrollment_record(
    const NamespacePolicy &policy,
    const rollback_witness::DomainId &base_domain, std::uint64_t witness_epoch,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
  auto state = load_tree_v2_freshness_state(policy, identity.public_key(),
                                            sodium, transaction);
  if (!state)
    return state.status();
  auto digest = tree_v2_freshness_digest(policy, state.value(), sodium);
  if (!digest)
    return digest.status();
  auto guard = load_guard(policy, identity.public_key(), sodium);
  if (!guard)
    return guard.status();
  if (guard.value() &&
      (guard.value()->pending || guard.value()->committed != digest.value())) {
    return Status{
        ErrorCode::unavailable,
        "tree-v2 witness enrollment requires quiescent reconciled state"};
  }
  auto domain = derive_tree_v2_witness_domain(
      base_domain, identity.public_key(), policy.id, sodium);
  if (!domain)
    return domain.status();
  rollback_witness::Record record;
  record.domain = domain.value();
  record.device = identity.public_key();
  record.witness_epoch = witness_epoch;
  record.lane = rollback_witness::Lane::tree_v2_state;
  record.committed = rollback_witness::Head{1U, digest.value()};
  const Status valid = rollback_witness::validate(record);
  return valid.ok() ? Result<rollback_witness::Record>{record}
                    : Result<rollback_witness::Record>{valid};
}

TreeV2StateWitness::TreeV2StateWitness(Config config, NamespacePolicy policy,
                                       const security::DeviceIdentity &identity,
                                       const security::Sodium &sodium)
    : config_(std::move(config)), policy_(std::move(policy)),
      identity_(&identity), sodium_(&sodium) {}

Status
TreeV2StateWitness::reconcile(const NamespacePolicy &policy,
                              const SyncNamespaceTransaction &transaction) {
  {
    std::scoped_lock lock(state_mutex_);
    verified_head_.reset();
  }
  const Status configured = validate_config(config_, policy_, *identity_);
  if (!configured.ok())
    return configured;
  if (!same_storage_identity(policy_, policy)) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 witness storage identity changed"};
  }
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto state = load_tree_v2_freshness_state(policy, identity_->public_key(),
                                            *sodium_, transaction);
  if (!state)
    return state.status();
  auto digest = tree_v2_freshness_digest(policy, state.value(), *sodium_);
  if (!digest)
    return digest.status();
  auto guard = load_guard(policy, identity_->public_key(), *sodium_);
  if (!guard)
    return guard.status();
  auto external = config_.backend->query();
  if (!external) {
    return Status{external.status().code(),
                  "unable to query tree-v2 witness: " +
                      external.status().message()};
  }
  if (!rollback_witness::validate(external.value()).ok() ||
      !same_selector(external.value(), config_, *identity_) ||
      external.value().committed.position == 0U) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 witness returned another or invalid lane"};
  }

  if (!guard.value()) {
    if (external.value().pending ||
        external.value().committed.digest != digest.value()) {
      return Status{ErrorCode::protocol_error,
                    "tree-v2 state is not its enrolled witness head"};
    }
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }

  TreeV2Guard local = *guard.value();
  if (!local.pending) {
    if (local.committed != digest.value()) {
      return Status{ErrorCode::protocol_error,
                    "tree-v2 state diverges from its local guard"};
    }
    if (external.value().pending) {
      if (external.value().pending->digest != digest.value()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 state does not join the pending witness"};
      }
      auto finished = rollback_witness::finish(external.value());
      if (!finished)
        return finished.status();
      const Status committed =
          resolve_cas(*config_.backend, external.value(), finished.value(),
                      "unable to finish recovered tree-v2 witness");
      if (!committed.ok())
        return committed;
      external = finished.value();
    } else if (external.value().committed.digest != digest.value()) {
      return Status{ErrorCode::protocol_error,
                    "tree-v2 state is not the externally committed head"};
    }
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }

  if (digest.value() == local.committed) {
    if (external.value().pending ||
        external.value().committed.digest != local.committed) {
      return Status{
          ErrorCode::protocol_error,
          "uncommitted tree-v2 root has an impossible external advance"};
    }
    local.pending.reset();
    const Status cleared =
        write_guard(policy, std::move(local), *identity_, *sodium_);
    if (!cleared.ok())
      return cleared;
    std::scoped_lock lock(state_mutex_);
    verified_head_ = external.value().committed;
    return Status::success();
  }
  if (digest.value() != *local.pending) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 state is neither side of its guarded transition"};
  }
  if (external.value().pending) {
    if (external.value().committed.digest != local.committed ||
        external.value().pending->digest != *local.pending) {
      return Status{ErrorCode::protocol_error,
                    "pending tree-v2 witness does not join the local guard"};
    }
  } else {
    if (external.value().committed.digest != local.committed ||
        external.value().committed.position ==
            std::numeric_limits<std::uint64_t>::max()) {
      return Status{ErrorCode::protocol_error,
                    "landed tree-v2 state cannot advance from external state"};
    }
    rollback_witness::TransactionNonce nonce{};
    const Status random = security::fill_random(nonce);
    if (!random.ok())
      return random;
    auto pending = rollback_witness::begin(
        external.value(),
        rollback_witness::Head{external.value().committed.position + 1U,
                               *local.pending},
        nonce);
    if (!pending)
      return pending.status();
    const Status begun =
        resolve_cas(*config_.backend, external.value(), pending.value(),
                    "unable to recover landed tree-v2 state into its witness");
    if (!begun.ok())
      return begun;
    external = pending.value();
  }
  TreeV2Guard committed_guard = local;
  committed_guard.committed = *local.pending;
  committed_guard.pending.reset();
  const Status local_finished =
      write_guard(policy, std::move(committed_guard), *identity_, *sodium_);
  if (!local_finished.ok())
    return local_finished;
  auto committed = rollback_witness::finish(external.value());
  if (!committed)
    return committed.status();
  const Status remote_finished =
      resolve_cas(*config_.backend, external.value(), committed.value(),
                  "unable to finish recovered tree-v2 witness");
  if (!remote_finished.ok())
    return remote_finished;
  std::scoped_lock lock(state_mutex_);
  verified_head_ = committed.value().committed;
  return Status::success();
}

Status
TreeV2StateWitness::verify_read(const NamespacePolicy &policy,
                                const SyncNamespaceTransaction &transaction) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto state = load_tree_v2_freshness_state(policy, identity_->public_key(),
                                            *sodium_, transaction);
  if (!state)
    return state.status();
  auto digest = tree_v2_freshness_digest(policy, state.value(), *sodium_);
  if (!digest)
    return digest.status();
  auto guard = load_guard(policy, identity_->public_key(), *sodium_);
  if (!guard)
    return guard.status();
  if (guard.value() &&
      (guard.value()->pending || guard.value()->committed != digest.value())) {
    return reconcile(policy, transaction);
  }
  std::optional<rollback_witness::Head> verified;
  {
    std::scoped_lock lock(state_mutex_);
    verified = verified_head_;
  }
  if (!verified)
    return reconcile(policy, transaction);
  if (verified->digest != digest.value()) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 read found an uncommitted local head"};
  }
  return Status::success();
}

Status TreeV2StateWitness::transition(
    const NamespacePolicy &policy, const SyncNamespaceTransaction &transaction,
    const TreeV2StateTransform &transform, const TreeV2StateCommit &commit) {
  if (!transform || !commit) {
    return Status{ErrorCode::invalid_argument,
                  "witnessed tree-v2 transition requires transform and commit"};
  }
  const Status reconciled = reconcile(policy, transaction);
  if (!reconciled.ok())
    return reconciled;
  auto current = load_tree_v2_freshness_state(policy, identity_->public_key(),
                                              *sodium_, transaction);
  if (!current)
    return current.status();
  auto next = transform(current.value());
  if (!next)
    return next.status();
  auto current_digest =
      tree_v2_freshness_digest(policy, current.value(), *sodium_);
  auto next_digest = tree_v2_freshness_digest(policy, next.value(), *sodium_);
  if (!current_digest || !next_digest) {
    return !current_digest ? current_digest.status() : next_digest.status();
  }
  if (current_digest.value() == next_digest.value()) {
    return Status{ErrorCode::invalid_argument,
                  "witnessed tree-v2 transition does not change state"};
  }
  auto external = config_.backend->query();
  if (!external || !same_selector(external.value(), config_, *identity_) ||
      external.value().pending ||
      external.value().committed.digest != current_digest.value() ||
      external.value().committed.position ==
          std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::protocol_error,
                  "tree-v2 witness is not ready to advance"};
  }
  {
    std::scoped_lock lock(state_mutex_);
    verified_head_.reset();
  }
  TreeV2Guard guard;
  guard.committed = current_digest.value();
  guard.pending = next_digest.value();
  const Status begun =
      write_guard(policy, std::move(guard), *identity_, *sodium_);
  if (!begun.ok())
    return begun;
  const Status stored = commit();
  if (!stored.ok())
    return stored;
  auto reloaded = load_tree_v2_freshness_state(policy, identity_->public_key(),
                                               *sodium_, transaction);
  if (!reloaded || reloaded.value() != next.value()) {
    return reloaded ? Status{ErrorCode::protocol_error,
                             "tree-v2 committed state did not reload exactly"}
                    : reloaded.status();
  }
  rollback_witness::TransactionNonce nonce{};
  const Status random = security::fill_random(nonce);
  if (!random.ok())
    return random;
  auto pending = rollback_witness::begin(
      external.value(),
      rollback_witness::Head{external.value().committed.position + 1U,
                             next_digest.value()},
      nonce);
  if (!pending)
    return pending.status();
  const Status remote_begun =
      resolve_cas(*config_.backend, external.value(), pending.value(),
                  "unable to begin tree-v2 witness transition");
  if (!remote_begun.ok())
    return remote_begun;
  TreeV2Guard committed_guard;
  committed_guard.committed = next_digest.value();
  const Status local_finished =
      write_guard(policy, std::move(committed_guard), *identity_, *sodium_);
  if (!local_finished.ok())
    return local_finished;
  auto committed = rollback_witness::finish(pending.value());
  if (!committed)
    return committed.status();
  const Status remote_finished = resolve_cas(
      *config_.backend, pending.value(), committed.value(),
      "local tree-v2 state advanced but witness commit is unresolved");
  if (!remote_finished.ok())
    return remote_finished;
  std::scoped_lock lock(state_mutex_);
  verified_head_ = committed.value().committed;
  return Status::success();
}

} // namespace iotox::sync
