#include "test_harness.hpp"

#include "iotox/sync_head.hpp"
#include "iotox/sync_job.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unistd.h>
#include <vector>

namespace {

using iotox::Result;
using iotox::Status;
using iotox::sync::CandidateHead;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::HeadAcceptanceDecision;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncInstallRequest;
using iotox::sync::SyncInstallSeams;
using iotox::sync::SyncObjectKind;
using iotox::sync::SyncObjectRecord;
using iotox::sync::SyncPublishJobRequest;
using iotox::sync::SignedHeadStore;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-job-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) {
      throw std::runtime_error("mkdtemp failed");
    }
    path_ = created;
  }

  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }

  TempDirectory(const TempDirectory &) = delete;
  TempDirectory &operator=(const TempDirectory &) = delete;

  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

private:
  std::filesystem::path path_;
};

PrincipalId principal(std::uint8_t value) {
  PrincipalId result {};
  result[0U] = value;
  return result;
}

Digest digest(std::uint8_t value) {
  Digest result {};
  result[0U] = value;
  return result;
}

std::vector<std::uint8_t> bytes(std::string_view text) {
  return {reinterpret_cast<const std::uint8_t *>(text.data()),
          reinterpret_cast<const std::uint8_t *>(text.data()) + text.size()};
}

void write_file(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary);
  output << text;
  if (!output) {
    throw std::runtime_error("unable to write fixture: " + path.string());
  }
}

Digest toy_digest(std::span<const std::uint8_t> input) {
  Digest result {};
  std::uint8_t value = 0U;
  for (const std::uint8_t byte : input) {
    value = static_cast<std::uint8_t>((value * 33U) ^ byte);
  }
  result[0U] = value;
  result[1U] = static_cast<std::uint8_t>(input.size());
  return result;
}

std::string hex_encode(const Digest &digest) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(digest.size() * 2U);
  for (const std::uint8_t byte : digest) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

Result<Digest> hash_file(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    return Status{iotox::ErrorCode::io_error,
                  "unable to read hash fixture: " + path.string()};
  }
  std::vector<std::uint8_t> contents(
      (std::istreambuf_iterator<char>(input)),
      std::istreambuf_iterator<char>());
  return toy_digest(contents);
}

SyncInstallSeams seams(bool *cancel = nullptr) {
  SyncInstallSeams result;
  result.hash_file = hash_file;
  result.cancel_requested = [cancel]() {
    return cancel != nullptr && *cancel;
  };
  return result;
}

NamespacePolicy policy(const std::filesystem::path &root) {
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = {principal(1U)};
  result.subscribers = {principal(2U)};
  result.quotas.maximum_artifact_bytes = 128U;
  result.quotas.maximum_manifest_bytes = 32U;
  return result;
}

Sodium sodium() {
  auto loaded = Sodium::load();
  if (!loaded.ok())
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded.value());
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
  auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded.ok())
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded.value());
}

NamespacePolicy publish_policy(const std::filesystem::path &root,
                               const DeviceIdentity &writer) {
  NamespacePolicy result = policy(root);
  result.writers = {writer.public_key()};
  result.quotas.maximum_store_bytes = 1024U;
  result.quotas.maximum_staging_bytes = 256U;
  return result;
}

CandidateHead candidate(const NamespacePolicy &namespace_policy,
                        std::uint64_t generation, std::uint8_t record,
                        Digest parent, std::string_view artifact) {
  CandidateHead result;
  result.namespace_id = namespace_policy.id;
  result.writer = principal(1U);
  result.engine = namespace_policy.engine;
  result.generation = generation;
  result.record = digest(record);
  result.parent = parent;
  result.artifact = toy_digest(bytes(artifact));
  result.manifest = digest(static_cast<std::uint8_t>(record + 64U));
  result.artifact_bytes = artifact.size();
  result.manifest_bytes = 8U;
  return result;
}

} // namespace

IOTOX_TEST("sync attempt staging commits verified bytes by derived identity") {
  TempDirectory temporary;
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root);
  configured.quotas.maximum_store_bytes = 1024U;
  configured.quotas.maximum_staging_bytes = 256U;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  const SyncObjectRecord object{
      SyncObjectKind::artifact, toy_digest(bytes("alpha")), 5U};
  auto staging = iotox::sync::prepare_sync_attempt_staging(
      configured, 0x1234U, object, transaction.value());
  IOTOX_CHECK(staging.ok());
  IOTOX_CHECK(staging.value().filename() == "attempt-0000000000001234.part");
  write_file(staging.value(), "alpha");
  std::filesystem::permissions(
      staging.value(), std::filesystem::perms::owner_read |
                           std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  auto committed = iotox::sync::commit_sync_attempt_staging(
      configured, 0x1234U, object, transaction.value(), seams());
  IOTOX_CHECK(committed.ok());
  IOTOX_CHECK(committed.value().installed);
  IOTOX_CHECK(std::filesystem::exists(committed.value().object_path));
  IOTOX_CHECK(!std::filesystem::exists(staging.value()));
  IOTOX_CHECK(hash_file(committed.value().object_path).value() ==
              object.identity);
}

IOTOX_TEST("sync attempt partial handoff preserves exact private progress without clobber") {
  TempDirectory temporary;
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root);
  configured.quotas.maximum_store_bytes = 1024U;
  configured.quotas.maximum_staging_bytes = 256U;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  const SyncObjectRecord object{
      SyncObjectKind::artifact, toy_digest(bytes("payload")), 7U};
  auto partial = iotox::sync::create_sync_attempt_partial(
      configured, 0x1001U, object, transaction.value());
  IOTOX_CHECK(partial.ok());
  IOTOX_CHECK(partial.value().bytes == 0U);
  write_file(partial.value().path, "pay");
  std::filesystem::permissions(
      partial.value().path, std::filesystem::perms::owner_read |
                                std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  auto inspected = iotox::sync::inspect_sync_attempt_partial(
      configured, 0x1001U, object, transaction.value());
  IOTOX_CHECK(inspected.ok() && inspected.value().bytes == 3U);

  auto moved = iotox::sync::handoff_sync_attempt_partial(
      configured, 0x1001U, 0x1002U, object, transaction.value());
  IOTOX_CHECK(moved.ok() && moved.value().bytes == 3U);
  IOTOX_CHECK(!std::filesystem::exists(partial.value().path));
  IOTOX_CHECK(std::filesystem::exists(moved.value().path));
  IOTOX_CHECK(hash_file(moved.value().path).value() ==
              toy_digest(bytes("pay")));
  auto exact_retry = iotox::sync::handoff_sync_attempt_partial(
      configured, 0x1001U, 0x1002U, object, transaction.value());
  IOTOX_CHECK(exact_retry.ok() && exact_retry.value() == moved.value());

  auto occupied = iotox::sync::create_sync_attempt_partial(
      configured, 0x1003U, object, transaction.value());
  IOTOX_CHECK(occupied.ok());
  IOTOX_CHECK(!iotox::sync::handoff_sync_attempt_partial(
                   configured, 0x1002U, 0x1003U, object,
                   transaction.value()).ok());
  IOTOX_CHECK(std::filesystem::exists(moved.value().path));
  IOTOX_CHECK(std::filesystem::exists(occupied.value().path));
}

IOTOX_TEST("sync attempt staging mismatch cannot enter object store") {
  TempDirectory temporary;
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root);
  configured.quotas.maximum_store_bytes = 1024U;
  configured.quotas.maximum_staging_bytes = 256U;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  const SyncObjectRecord object{
      SyncObjectKind::manifest, toy_digest(bytes("right")), 5U};
  auto staging = iotox::sync::prepare_sync_attempt_staging(
      configured, 77U, object, transaction.value());
  IOTOX_CHECK(staging.ok());
  write_file(staging.value(), "wrong");
  std::filesystem::permissions(
      staging.value(), std::filesystem::perms::owner_read |
                           std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  auto committed = iotox::sync::commit_sync_attempt_staging(
      configured, 77U, object, transaction.value(), seams());
  IOTOX_CHECK(!committed.ok());
  IOTOX_CHECK(committed.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(!std::filesystem::exists(root / "objects"));
  IOTOX_CHECK(iotox::sync::discard_sync_attempt_staging(
                  configured, 77U, transaction.value()).ok());
  IOTOX_CHECK(iotox::sync::discard_sync_attempt_staging(
                  configured, 77U, transaction.value()).ok());
}

IOTOX_TEST("sync attempt discard refuses an unexpected link") {
  TempDirectory temporary;
  const std::filesystem::path root = temporary.path() / "sync";
  NamespacePolicy configured = policy(root);
  configured.quotas.maximum_store_bytes = 1024U;
  configured.quotas.maximum_staging_bytes = 256U;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  const SyncObjectRecord object{
      SyncObjectKind::artifact, toy_digest(bytes("alpha")), 5U};
  auto staging = iotox::sync::prepare_sync_attempt_staging(
      configured, 88U, object, transaction.value());
  IOTOX_CHECK(staging.ok());
  const std::filesystem::path outside = temporary.path() / "outside";
  write_file(outside, "sentinel");
  std::filesystem::create_symlink(outside, staging.value());
  IOTOX_CHECK(!iotox::sync::discard_sync_attempt_staging(
                   configured, 88U, transaction.value()).ok());
  IOTOX_CHECK(std::filesystem::is_symlink(staging.value()));
  IOTOX_CHECK(hash_file(outside).value() == toy_digest(bytes("sentinel")));
}

IOTOX_TEST("sync install stages artifact and commits accepted head last") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path source = temporary.path() / "artifact.bin";
  write_file(source, "alpha");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest request;
  request.policy = namespace_policy;
  request.source_path = source;
  request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");

  auto installed =
      iotox::sync::install_local_artifact(request, writer, crypto, seams());
  IOTOX_CHECK(installed.ok());
  IOTOX_CHECK(installed.value().head.decision ==
              HeadAcceptanceDecision::accept_genesis);
  IOTOX_CHECK(installed.value().installed);
  IOTOX_CHECK(!installed.value().activated);
  IOTOX_CHECK(std::filesystem::exists(installed.value().object_path));
  IOTOX_CHECK(!std::filesystem::exists(root / "current"));

  iotox::sync::AcceptedHeadStore store(root);
  auto loaded = store.load(namespace_policy, writer.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->record == request.candidate.record);
}

IOTOX_TEST("sync install reuses existing staged object after head commit miss") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path source = temporary.path() / "artifact.bin";
  write_file(source, "alpha");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest request;
  request.policy = namespace_policy;
  request.source_path = source;
  request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");

  const std::filesystem::path objects = root / "objects";
  std::filesystem::create_directories(objects);
  const std::filesystem::path object =
      objects / (hex_encode(request.candidate.artifact) + ".artifact");
  write_file(object, "alpha");
  std::filesystem::permissions(
      object, std::filesystem::perms::owner_read |
                  std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);

  auto installed =
      iotox::sync::install_local_artifact(request, writer, crypto, seams());
  IOTOX_CHECK(installed.ok());
  IOTOX_CHECK(installed.value().head.decision ==
              HeadAcceptanceDecision::accept_genesis);
  IOTOX_CHECK(!installed.value().installed);
}

IOTOX_TEST("sync install refuses corrupt existing object before head commit") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path source = temporary.path() / "artifact.bin";
  write_file(source, "alpha");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest request;
  request.policy = namespace_policy;
  request.source_path = source;
  request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");

  const std::filesystem::path objects = root / "objects";
  std::filesystem::create_directories(objects);
  const std::filesystem::path object =
      objects / (hex_encode(request.candidate.artifact) + ".artifact");
  write_file(object, "bravo");
  std::filesystem::permissions(
      object, std::filesystem::perms::owner_read |
                  std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);

  auto installed =
      iotox::sync::install_local_artifact(request, writer, crypto, seams());
  IOTOX_CHECK(!installed.ok());
  IOTOX_CHECK(installed.status().code() == iotox::ErrorCode::protocol_error);
  iotox::sync::AcceptedHeadStore store(root);
  auto loaded = store.load(namespace_policy, writer.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(!loaded.value().has_value());
}

IOTOX_TEST("sync install refuses oversized source before mutation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path source = temporary.path() / "artifact.bin";
  write_file(source, "alpha");

  NamespacePolicy namespace_policy = policy(root);
  namespace_policy.quotas.maximum_artifact_bytes = 4U;
  SyncInstallRequest request;
  request.policy = namespace_policy;
  request.source_path = source;
  request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");

  auto installed =
      iotox::sync::install_local_artifact(request, writer, crypto, seams());
  IOTOX_CHECK(installed.ok());
  IOTOX_CHECK(installed.value().head.decision ==
              HeadAcceptanceDecision::resource_limit);
  IOTOX_CHECK(!std::filesystem::exists(root));
}

IOTOX_TEST("sync install refuses digest mismatch without accepted head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path source = temporary.path() / "artifact.bin";
  write_file(source, "alpha");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest request;
  request.policy = namespace_policy;
  request.source_path = source;
  request.candidate = candidate(namespace_policy, 1U, 1U, {}, "beta");
  request.candidate.artifact_bytes = 5U;

  auto installed =
      iotox::sync::install_local_artifact(request, writer, crypto, seams());
  IOTOX_CHECK(!installed.ok());
  IOTOX_CHECK(installed.status().code() == iotox::ErrorCode::protocol_error);
  iotox::sync::AcceptedHeadStore store(root);
  auto loaded = store.load(namespace_policy, writer.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(!loaded.value().has_value());
}

IOTOX_TEST("sync install cancellation preserves previous accepted head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path first_source = temporary.path() / "first.bin";
  const std::filesystem::path second_source = temporary.path() / "second.bin";
  write_file(first_source, "alpha");
  write_file(second_source, "bravo");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest first_request;
  first_request.policy = namespace_policy;
  first_request.source_path = first_source;
  first_request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  auto first = iotox::sync::install_local_artifact(first_request, writer,
                                                   crypto, seams());
  IOTOX_CHECK(first.ok());

  bool cancel = true;
  SyncInstallRequest second_request;
  second_request.policy = namespace_policy;
  second_request.source_path = second_source;
  second_request.candidate = candidate(namespace_policy, 2U, 2U,
                                       first_request.candidate.record, "bravo");
  auto second = iotox::sync::install_local_artifact(
      second_request, writer, crypto, seams(&cancel));
  IOTOX_CHECK(!second.ok());
  IOTOX_CHECK(second.status().code() == iotox::ErrorCode::unavailable);

  iotox::sync::AcceptedHeadStore store(root);
  auto loaded = store.load(namespace_policy, writer.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->record == first_request.candidate.record);
}

IOTOX_TEST("sync install rejects rollback after local convergence") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "device.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path first_source = temporary.path() / "first.bin";
  const std::filesystem::path second_source = temporary.path() / "second.bin";
  write_file(first_source, "alpha");
  write_file(second_source, "bravo");

  NamespacePolicy namespace_policy = policy(root);
  SyncInstallRequest first_request;
  first_request.policy = namespace_policy;
  first_request.source_path = first_source;
  first_request.candidate = candidate(namespace_policy, 1U, 1U, {}, "alpha");
  auto first = iotox::sync::install_local_artifact(first_request, writer,
                                                   crypto, seams());
  IOTOX_CHECK(first.ok());

  SyncInstallRequest second_request;
  second_request.policy = namespace_policy;
  second_request.source_path = second_source;
  second_request.candidate = candidate(namespace_policy, 2U, 2U,
                                       first_request.candidate.record, "bravo");
  auto second = iotox::sync::install_local_artifact(second_request, writer,
                                                    crypto, seams());
  IOTOX_CHECK(second.ok());

  auto rollback = iotox::sync::install_local_artifact(first_request, writer,
                                                      crypto, seams());
  IOTOX_CHECK(rollback.ok());
  IOTOX_CHECK(rollback.value().head.decision == HeadAcceptanceDecision::stale);
  IOTOX_CHECK(!rollback.value().installed);
}

IOTOX_TEST("sync publish commits artifact and manifest before signed head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  SyncPublishJobRequest request{configured, artifact, manifest};

  auto published = iotox::sync::publish_local_revision(
      request, writer, crypto, store, seams());
  IOTOX_CHECK(published.ok());
  IOTOX_CHECK(published.value().publication.genesis);
  IOTOX_CHECK(published.value().artifact_installed);
  IOTOX_CHECK(published.value().manifest_installed);
  IOTOX_CHECK(std::filesystem::exists(
      published.value().artifact_object_path));
  IOTOX_CHECK(std::filesystem::exists(
      published.value().manifest_object_path));
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->artifact == hash_file(artifact).value());
  IOTOX_CHECK(loaded.value()->manifest == hash_file(manifest).value());
  auto inventory = iotox::sync::inspect_sync_object_store(configured);
  IOTOX_CHECK(inventory.ok());
  IOTOX_CHECK(inventory.value().objects == 2U);
  IOTOX_CHECK(inventory.value().artifacts == 1U);
  IOTOX_CHECK(inventory.value().manifests == 1U);
  IOTOX_CHECK(inventory.value().bytes == 17U);
  auto records = iotox::sync::inspect_sync_object_records(configured);
  IOTOX_CHECK(records.ok());
  IOTOX_CHECK(records.value().size() == 2U);
  IOTOX_CHECK(records.value()[0U].kind ==
              iotox::sync::SyncObjectKind::artifact);
  IOTOX_CHECK(records.value()[0U].identity == loaded.value()->artifact);
  IOTOX_CHECK(records.value()[0U].bytes == 5U);
  IOTOX_CHECK(records.value()[1U].kind ==
              iotox::sync::SyncObjectKind::manifest);
  IOTOX_CHECK(records.value()[1U].identity == loaded.value()->manifest);
  IOTOX_CHECK(records.value()[1U].bytes == 12U);
}

IOTOX_TEST("sync publish exact retry is idempotent and reuses objects") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  SyncPublishJobRequest request{configured, artifact, manifest};
  auto first = iotox::sync::publish_local_revision(
      request, writer, crypto, store, seams());
  IOTOX_CHECK(first.ok());
  auto duplicate = iotox::sync::publish_local_revision(
      request, writer, crypto, store, seams());
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().publication.duplicate);
  IOTOX_CHECK(!duplicate.value().artifact_installed);
  IOTOX_CHECK(!duplicate.value().manifest_installed);
  IOTOX_CHECK(duplicate.value().publication.head.generation == 1U);
}

IOTOX_TEST("sync publish semantic pair refusal precedes objects and head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "wrong-index");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  SyncInstallSeams validation = seams();
  validation.validate_revision_sources =
      [](const std::filesystem::path &, const std::filesystem::path &,
         const Digest &, std::uint64_t, std::uint64_t) {
        return Status{iotox::ErrorCode::protocol_error,
                      "manifest does not bind the artifact"};
      };
  auto refused = iotox::sync::publish_local_revision(
      {configured, artifact, manifest}, writer, crypto, store, validation);
  IOTOX_CHECK(!refused.ok());
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok() && !loaded.value().has_value());
  IOTOX_CHECK(!std::filesystem::exists(root / "objects"));
}

IOTOX_TEST("sync publish advances only after both new objects exist") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  SyncPublishJobRequest request{configured, artifact, manifest};
  IOTOX_CHECK(iotox::sync::publish_local_revision(
                  request, writer, crypto, store, seams())
                  .ok());
  write_file(artifact, "bravo");
  write_file(manifest, "manifest-two");
  auto second = iotox::sync::publish_local_revision(
      request, writer, crypto, store, seams());
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(second.value().publication.head.generation == 2U);
  IOTOX_CHECK(std::filesystem::exists(second.value().artifact_object_path));
  IOTOX_CHECK(std::filesystem::exists(second.value().manifest_object_path));
}

IOTOX_TEST("sync publish quota refusal creates no namespace state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  configured.quotas.maximum_manifest_bytes = 4U;
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(published.status().code() == iotox::ErrorCode::resource_exhausted);
  IOTOX_CHECK(!std::filesystem::exists(root));

  configured = publish_policy(root, writer);
  write_file(manifest, "");
  published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(published.status().code() == iotox::ErrorCode::resource_exhausted);
  IOTOX_CHECK(!std::filesystem::exists(root));

  write_file(manifest, "manifest-one");
  configured.quotas.maximum_artifact_bytes = 5U;
  configured.quotas.maximum_manifest_bytes = 12U;
  configured.quotas.maximum_staging_bytes = 12U;
  configured.quotas.maximum_store_bytes = 12U;
  published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(published.status().code() == iotox::ErrorCode::resource_exhausted);
  IOTOX_CHECK(!std::filesystem::exists(root));
}

IOTOX_TEST("sync publish refuses corrupt existing manifest before head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  const Digest manifest_digest = hash_file(manifest).value();
  const std::filesystem::path corrupt =
      root / "objects" / (hex_encode(manifest_digest) + ".manifest");
  std::filesystem::create_directories(corrupt.parent_path());
  write_file(corrupt, "wrong-bytes!");
  std::filesystem::permissions(
      corrupt, std::filesystem::perms::owner_read |
                   std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(!store.load(configured, crypto).value().has_value());
}

IOTOX_TEST("sync publish refuses public or multiply linked objects") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  const Digest manifest_digest = hash_file(manifest).value();
  const std::filesystem::path object =
      root / "objects" / (hex_encode(manifest_digest) + ".manifest");
  std::filesystem::create_directories(object.parent_path());
  write_file(object, "manifest-one");
  SignedHeadStore store(root);
  const SyncPublishJobRequest request{configured, artifact, manifest};
  IOTOX_CHECK(!iotox::sync::publish_local_revision(
                   request, writer, crypto, store, seams())
                   .ok());

  std::filesystem::permissions(
      object, std::filesystem::perms::owner_read |
                  std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  const std::filesystem::path alias = object.parent_path() / "manifest-alias";
  std::filesystem::create_hard_link(object, alias);
  IOTOX_CHECK(!iotox::sync::publish_local_revision(
                   request, writer, crypto, store, seams())
                   .ok());
  IOTOX_CHECK(!store.load(configured, crypto).value().has_value());
}

IOTOX_TEST("sync publish catches source mutation during object commit") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SyncInstallSeams changing = seams();
  bool changed = false;
  changing.hash_file = [&](const std::filesystem::path &path) -> Result<Digest> {
    auto result = hash_file(path);
    if (!changed && path == artifact) {
      changed = true;
      write_file(artifact, "omega");
    }
    return result;
  };
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, changing);
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(published.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(!store.load(configured, crypto).value().has_value());
}

IOTOX_TEST("sync publish cancellation after objects preserves head") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  bool cancel = false;
  SyncInstallSeams stopping = seams(&cancel);
  stopping.hash_file = [&](const std::filesystem::path &path) -> Result<Digest> {
    auto result = hash_file(path);
    if (path.extension() == ".manifest")
      cancel = true;
    return result;
  };
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, stopping);
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(published.status().code() == iotox::ErrorCode::unavailable);
  IOTOX_CHECK(!store.load(configured, crypto).value().has_value());
  IOTOX_CHECK(std::filesystem::directory_iterator(root / "objects") !=
              std::filesystem::directory_iterator{});
}

IOTOX_TEST("sync publish refuses symlink sources before mutation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path alias = temporary.path() / "artifact-link.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  std::filesystem::create_symlink(artifact.filename(), alias);
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, alias, manifest}, writer, crypto, store,
      seams());
  IOTOX_CHECK(!published.ok());
  IOTOX_CHECK(!std::filesystem::exists(root));
}

IOTOX_TEST("sync publish ignores stale legacy staging debris") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  const std::string artifact_name = hex_encode(hash_file(artifact).value()) +
                                    ".artifact";
  const std::filesystem::path debris =
      root / "staging" /
      ("." + artifact_name + ".tmp." +
       std::to_string(static_cast<long long>(::getpid())));
  std::filesystem::create_directories(debris.parent_path());
  write_file(debris, "stale");
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(published.ok());
  IOTOX_CHECK(published.value().publication.genesis);
  IOTOX_CHECK(std::filesystem::exists(debris));
}

IOTOX_TEST("sync object inventory rejects unexpected or public store state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  IOTOX_CHECK(iotox::sync::publish_local_revision(
                  SyncPublishJobRequest{configured, artifact, manifest}, writer,
                  crypto, store, seams())
                  .ok());
  const std::filesystem::path objects = root / "objects";
  write_file(objects / "unexpected", "junk");
  IOTOX_CHECK(!iotox::sync::inspect_sync_object_store(configured).ok());
  std::filesystem::remove(objects / "unexpected");
  std::filesystem::permissions(objects, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!iotox::sync::inspect_sync_object_store(configured).ok());
  std::filesystem::permissions(objects, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);
  IOTOX_CHECK(iotox::sync::inspect_sync_object_store(configured).ok());
}

IOTOX_TEST("sync object repair quarantines only digest mismatches") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  auto published = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(published.ok());

  const auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value().has_value());
  const SyncObjectRecord artifact_record{
      SyncObjectKind::artifact, loaded.value()->artifact,
      loaded.value()->artifact_bytes};
  const SyncObjectRecord manifest_record{
      SyncObjectKind::manifest, loaded.value()->manifest,
      loaded.value()->manifest_bytes};
  const std::filesystem::path manifest_object =
      iotox::sync::sync_object_path(configured, manifest_record);
  write_file(manifest_object, "wrong-bytes!");
  std::filesystem::permissions(
      manifest_object, std::filesystem::perms::owner_read |
                           std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
  IOTOX_CHECK(!iotox::sync::verify_sync_object(
                   configured, manifest_record,
                   iotox::sync::SyncNamespaceTransaction::acquire(configured)
                       .value(),
                   seams())
                   .ok());

  auto repaired = iotox::sync::repair_sync_object_store(configured, seams());
  IOTOX_CHECK_MSG(repaired.ok(), repaired.status().message());
  IOTOX_CHECK(repaired.value().inspected_objects == 2U);
  IOTOX_CHECK(repaired.value().verified_objects == 1U);
  IOTOX_CHECK(repaired.value().quarantined_objects == 1U);
  IOTOX_CHECK(repaired.value().quarantined_bytes ==
              manifest_record.bytes);
  IOTOX_CHECK(repaired.value().quarantined.size() == 1U);
  IOTOX_CHECK(repaired.value().quarantined.front() == manifest_record);
  IOTOX_CHECK(!std::filesystem::exists(manifest_object));
  IOTOX_CHECK(iotox::sync::verify_sync_object(
                  configured, artifact_record,
                  iotox::sync::SyncNamespaceTransaction::acquire(configured)
                      .value(),
                  seams())
                  .ok());
  IOTOX_CHECK(iotox::sync::verify_sync_object(
                  configured, manifest_record,
                  iotox::sync::SyncNamespaceTransaction::acquire(configured)
                      .value(),
                  seams())
                  .code() == iotox::ErrorCode::not_found);
  std::uint64_t quarantined = 0U;
  for (const auto &entry :
       std::filesystem::directory_iterator(root / "quarantine")) {
    IOTOX_CHECK(entry.path().filename().string().starts_with(
        manifest_object.filename().string() + ".corrupt-"));
    ++quarantined;
  }
  IOTOX_CHECK(quarantined == 1U);

  auto clean = iotox::sync::repair_sync_object_store(configured, seams());
  IOTOX_CHECK(clean.ok());
  IOTOX_CHECK(clean.value().inspected_objects == 1U);
  IOTOX_CHECK(clean.value().verified_objects == 1U);
  IOTOX_CHECK(clean.value().quarantined_objects == 0U);
}

IOTOX_TEST("sync object repair refuses ambiguous store entries") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  SignedHeadStore store(root);
  IOTOX_CHECK(iotox::sync::publish_local_revision(
                  SyncPublishJobRequest{configured, artifact, manifest}, writer,
                  crypto, store, seams())
                  .ok());
  const std::filesystem::path objects = root / "objects";
  write_file(objects / "unexpected", "junk");
  auto repaired = iotox::sync::repair_sync_object_store(configured, seams());
  IOTOX_CHECK(!repaired.ok());
  IOTOX_CHECK(repaired.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(std::filesystem::exists(objects / "unexpected"));
  IOTOX_CHECK(!std::filesystem::exists(root / "quarantine"));
}

IOTOX_TEST("sync publish enforces whole-store object and byte ceilings") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity writer = identity(temporary.path() / "writer.identity", crypto);
  const std::filesystem::path root = temporary.path() / "sync";
  const std::filesystem::path artifact = temporary.path() / "artifact.bin";
  const std::filesystem::path manifest = temporary.path() / "manifest.txt";
  write_file(artifact, "alpha");
  write_file(manifest, "manifest-one");
  NamespacePolicy configured = publish_policy(root, writer);
  configured.quotas.maximum_artifact_bytes = 5U;
  configured.quotas.maximum_manifest_bytes = 12U;
  configured.quotas.maximum_staging_bytes = 12U;
  configured.quotas.maximum_objects = 3U;
  configured.quotas.maximum_retained_revisions = 3U;
  SignedHeadStore store(root);
  const SyncPublishJobRequest request{configured, artifact, manifest};
  IOTOX_CHECK(iotox::sync::publish_local_revision(
                  request, writer, crypto, store, seams())
                  .ok());
  write_file(artifact, "bravo");
  write_file(manifest, "manifest-two");
  auto denied = iotox::sync::publish_local_revision(
      request, writer, crypto, store, seams());
  IOTOX_CHECK(!denied.ok());
  IOTOX_CHECK(denied.status().code() == iotox::ErrorCode::resource_exhausted);

  configured.quotas.maximum_objects = 4096U;
  configured.quotas.maximum_retained_revisions = 4U;
  configured.quotas.maximum_store_bytes = 30U;
  denied = iotox::sync::publish_local_revision(
      SyncPublishJobRequest{configured, artifact, manifest}, writer, crypto,
      store, seams());
  IOTOX_CHECK(!denied.ok());
  IOTOX_CHECK(denied.status().code() == iotox::ErrorCode::resource_exhausted);
  auto loaded = store.load(configured, crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().has_value());
  IOTOX_CHECK(loaded.value()->generation == 1U);
}
