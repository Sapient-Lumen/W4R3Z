#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_rollback.hpp"

#include <filesystem>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncNamespaceTransaction;
using iotox::sync::SyncRollbackGuardStore;
using iotox::sync::SyncRollbackHead;
using iotox::sync::SyncRollbackReconcile;
using iotox::sync::SyncRollbackRoot;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-rollback-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr)
      throw std::runtime_error("mkdtemp failed");
    path_ = created;
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

NamespacePolicy policy(const std::filesystem::path &root) {
  PrincipalId writer{};
  writer[0U] = 1U;
  NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = {writer};
  return result;
}

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  return result;
}

SyncRollbackHead accepted_head(std::uint64_t generation,
                               std::uint8_t record) {
  SyncRollbackHead head;
  head.accepted = SyncRollbackRoot{generation, digest(record)};
  return head;
}

} // namespace

IOTOX_TEST("sync rollback head binds every authenticated root class") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  configured.writers = {device.public_key()};
  iotox::sync::SignedHeadStore publisher(configured.root);
  iotox::sync::SignedHeadPublicationRequest request{digest(1U), digest(2U),
                                                    10U, 5U};
  auto published = publisher.publish(configured, request, device, crypto);
  IOTOX_CHECK(published.ok());
  auto candidate = iotox::sync::verified_candidate_head(
      configured, published.value().head, crypto);
  IOTOX_CHECK(candidate.ok());
  iotox::sync::AcceptedHead accepted{
      candidate.value().namespace_id, candidate.value().writer,
      candidate.value().engine,       candidate.value().generation,
      candidate.value().record,       candidate.value().parent,
      candidate.value().artifact,     candidate.value().manifest,
      candidate.value().artifact_bytes,
      candidate.value().manifest_bytes};
  iotox::sync::RetentionStore retention(configured.root);
  IOTOX_CHECK(retention.pin(configured, accepted, device, crypto).ok());
  auto retained = retention.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(retained.ok());
  iotox::sync::SyncReachabilityRoots roots;
  roots.published = published.value().head;
  roots.accepted = accepted;
  roots.activated = iotox::sync::ActivatedRevision{
      configured.id, accepted.generation, accepted.record, accepted.artifact,
      accepted.artifact_bytes};
  roots.retained = retained.value();

  auto head = iotox::sync::make_sync_rollback_head(
      configured, device.public_key(), roots, crypto);
  IOTOX_CHECK(head.ok());
  IOTOX_CHECK(head.value().published.counter == 1U);
  IOTOX_CHECK(head.value().published.record == published.value().record);
  IOTOX_CHECK((head.value().accepted ==
               SyncRollbackRoot{1U, accepted.record}));
  IOTOX_CHECK((head.value().activated ==
               SyncRollbackRoot{1U, accepted.record}));
  IOTOX_CHECK(head.value().retained.counter == 1U);
  IOTOX_CHECK(head.value().retained.present());
}

IOTOX_TEST("sync rollback guard commits one signed root-head transition") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  SyncRollbackGuardStore store(configured.root);
  const SyncRollbackHead empty;
  const SyncRollbackHead next = accepted_head(1U, 1U);

  IOTOX_CHECK(store.begin(configured, empty, next, device, crypto,
                          transaction.value())
                  .ok());
  auto pending = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(pending.ok());
  IOTOX_CHECK(pending.value().has_value());
  IOTOX_CHECK(pending.value()->committed == empty);
  IOTOX_CHECK(pending.value()->pending == next);
  IOTOX_CHECK(store.finish(configured, next, device, crypto,
                           transaction.value())
                  .ok());
  auto committed = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(committed.ok());
  IOTOX_CHECK(committed.value()->committed == next);
  IOTOX_CHECK(!committed.value()->pending.has_value());
}

IOTOX_TEST("sync rollback guard recovers both power-cut transition sides") {
  TempDirectory before_directory;
  Sodium crypto = sodium();
  DeviceIdentity before_device =
      identity(before_directory.path() / "device.identity", crypto);
  NamespacePolicy before_policy = policy(before_directory.path() / "sync");
  auto before_transaction = SyncNamespaceTransaction::acquire(before_policy);
  IOTOX_CHECK(before_transaction.ok());
  SyncRollbackGuardStore before_store(before_policy.root);
  const SyncRollbackHead empty;
  const SyncRollbackHead next = accepted_head(1U, 1U);
  IOTOX_CHECK(before_store
                  .begin(before_policy, empty, next, before_device, crypto,
                         before_transaction.value())
                  .ok());
  auto before_check = before_store.check(
      before_policy, empty, before_device.public_key(), crypto,
      before_transaction.value());
  IOTOX_CHECK(before_check.ok());
  IOTOX_CHECK(before_check.value() ==
              SyncRollbackReconcile::recovered_before_state_commit);
  auto before_pending =
      before_store.load(before_policy, before_device.public_key(), crypto);
  IOTOX_CHECK(before_pending.ok());
  IOTOX_CHECK(before_pending.value()->pending == next);
  auto before = before_store.reconcile(
      before_policy, empty, before_device, crypto, before_transaction.value());
  IOTOX_CHECK(before.ok());
  IOTOX_CHECK(before.value() ==
              SyncRollbackReconcile::recovered_before_state_commit);

  TempDirectory after_directory;
  DeviceIdentity after_device =
      identity(after_directory.path() / "device.identity", crypto);
  NamespacePolicy after_policy = policy(after_directory.path() / "sync");
  auto after_transaction = SyncNamespaceTransaction::acquire(after_policy);
  IOTOX_CHECK(after_transaction.ok());
  SyncRollbackGuardStore after_store(after_policy.root);
  IOTOX_CHECK(after_store
                  .begin(after_policy, empty, next, after_device, crypto,
                         after_transaction.value())
                  .ok());
  auto after_check = after_store.check(
      after_policy, next, after_device.public_key(), crypto,
      after_transaction.value());
  IOTOX_CHECK(after_check.ok());
  IOTOX_CHECK(after_check.value() ==
              SyncRollbackReconcile::recovered_after_state_commit);
  auto after_pending =
      after_store.load(after_policy, after_device.public_key(), crypto);
  IOTOX_CHECK(after_pending.ok());
  IOTOX_CHECK(after_pending.value()->pending == next);
  auto after = after_store.reconcile(after_policy, next, after_device, crypto,
                                     after_transaction.value());
  IOTOX_CHECK(after.ok());
  IOTOX_CHECK(after.value() ==
              SyncRollbackReconcile::recovered_after_state_commit);
}

IOTOX_TEST("guarded sync mutation retries reconcile both commit failure sides") {
  Sodium crypto = sodium();
  for (const bool commit_landed : {false, true}) {
    TempDirectory temporary;
    DeviceIdentity device =
        identity(temporary.path() / "device.identity", crypto);
    NamespacePolicy configured = policy(temporary.path() / "sync");
    configured.writers = {device.public_key()};
    IOTOX_CHECK(::mkdir(configured.root.c_str(), 0700) == 0);
    const auto published_directory =
        std::filesystem::path(configured.root) / "published-heads";
    IOTOX_CHECK(::mkdir(published_directory.c_str(), 0700) == 0);
    iotox::sync::SignedHeadPublicationRequest request{digest(1U), digest(2U),
                                                      10U, 5U};
    auto head = iotox::sync::create_signed_head(
        configured, request, std::nullopt, device, crypto);
    IOTOX_CHECK(head.ok());
    auto encoded = iotox::sync::encode_signed_head(head.value());
    IOTOX_CHECK(encoded.ok());

    iotox::sync::SyncReachabilityRoots current;
    current.retained = iotox::sync::RetentionSnapshot{
        configured.id, {}, device.public_key()};
    iotox::sync::SyncReachabilityRoots next = current;
    next.published = head.value();
    auto current_head = iotox::sync::make_sync_rollback_head(
        configured, device.public_key(), current, crypto);
    auto next_head = iotox::sync::make_sync_rollback_head(
        configured, device.public_key(), next, crypto);
    IOTOX_CHECK(current_head.ok());
    IOTOX_CHECK(next_head.ok());
    const auto state_path =
        published_directory / "field-notes.signed-head";
    SyncRollbackGuardStore guard(configured.root);
    {
      auto transaction = SyncNamespaceTransaction::acquire(configured);
      IOTOX_CHECK(transaction.ok());
      const iotox::Status injected =
          iotox::sync::guarded_sync_root_transition(
              configured, current, next, device, crypto, transaction.value(),
              [&]() {
                if (commit_landed) {
                  const iotox::Status stored =
                      iotox::StateStore::write_atomic(state_path,
                                                       encoded.value());
                  if (!stored.ok())
                    return stored;
                }
                return iotox::Status{iotox::ErrorCode::io_error,
                                     "injected late root commit failure"};
              });
      IOTOX_CHECK(!injected.ok());
      const SyncRollbackHead &actual =
          commit_landed ? next_head.value() : current_head.value();
      auto observed = guard.check(configured, actual, device.public_key(),
                                  crypto, transaction.value());
      IOTOX_CHECK(observed.ok());
      IOTOX_CHECK(
          observed.value() ==
          (commit_landed
               ? SyncRollbackReconcile::recovered_after_state_commit
               : SyncRollbackReconcile::recovered_before_state_commit));
    }
    iotox::sync::SignedHeadStore store(configured.root);
    auto retry = store.publish(configured, request, device, crypto);
    IOTOX_CHECK(retry.ok());
    IOTOX_CHECK(retry.value().duplicate == commit_landed);
    auto committed = guard.load(configured, device.public_key(), crypto);
    IOTOX_CHECK(committed.ok());
    IOTOX_CHECK(committed.value().has_value());
    IOTOX_CHECK(!committed.value()->pending.has_value());
  }
}

IOTOX_TEST("sync rollback guard rejects missing rollback and forked heads") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  SyncRollbackGuardStore store(configured.root);
  const SyncRollbackHead first = accepted_head(1U, 1U);
  IOTOX_CHECK(!store.reconcile(configured, first, device, crypto,
                               transaction.value())
                   .ok());
  const SyncRollbackHead empty;
  IOTOX_CHECK(store.begin(configured, empty, first, device, crypto,
                          transaction.value())
                  .ok());
  IOTOX_CHECK(store.finish(configured, first, device, crypto,
                           transaction.value())
                  .ok());
  IOTOX_CHECK(!store.reconcile(configured, accepted_head(1U, 9U), device,
                               crypto, transaction.value())
                   .ok());
  IOTOX_CHECK(!store.reconcile(configured, empty, device, crypto,
                               transaction.value())
                   .ok());
}

IOTOX_TEST("sync rollback guard rejects foreign tampered and linked state") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity device = identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity foreign =
      identity(temporary.path() / "foreign.identity", crypto);
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  SyncRollbackGuardStore store(configured.root);
  const SyncRollbackHead empty;
  const SyncRollbackHead next = accepted_head(1U, 1U);
  IOTOX_CHECK(store.begin(configured, empty, next, device, crypto,
                          transaction.value())
                  .ok());
  IOTOX_CHECK(!store.load(configured, foreign.public_key(), crypto).ok());

  const auto path = std::filesystem::path(configured.root) /
                    "rollback-guards" / "field-notes.rollback-guard";
  auto bytes = iotox::StateStore::read(path);
  IOTOX_CHECK(bytes.ok());
  const std::vector<std::uint8_t> original = bytes.value();
  bytes.value()[120U] ^= 0x01U;
  IOTOX_CHECK(iotox::StateStore::write_atomic(path, bytes.value()).ok());
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());

  IOTOX_CHECK(iotox::StateStore::write_atomic(path, original).ok());
  const auto linked = path.parent_path() / "linked.rollback-guard";
  IOTOX_CHECK(::link(path.c_str(), linked.c_str()) == 0);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());

  IOTOX_CHECK(std::filesystem::remove(linked));
  IOTOX_CHECK(std::filesystem::remove(path));
  IOTOX_CHECK(std::filesystem::remove(path.parent_path()));
  const auto external = temporary.path() / "external";
  std::filesystem::create_directory(external);
  IOTOX_CHECK(::symlink(external.c_str(), path.parent_path().c_str()) == 0);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
}
