#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_activation.hpp"
#include "iotox/sync_guarded_witness.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/sync_retention.hpp"

#include <chrono>
#include <condition_variable>
#include <filesystem>
#include <future>
#include <memory>
#include <mutex>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace {

class TemporaryDirectory {
public:
  TemporaryDirectory() {
    path_ =
        std::filesystem::temp_directory_path() /
        ("iotox-sync-guarded-witness-test-" + std::to_string(::getpid()) + "-" +
         std::to_string(
             std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directories(path_);
    std::filesystem::permissions(path_, std::filesystem::perms::owner_all,
                                 std::filesystem::perm_options::replace);
  }
  ~TemporaryDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const { return path_; }

private:
  std::filesystem::path path_;
};

class MemoryBackend final : public iotox::rollback_witness::Backend {
public:
  iotox::Result<iotox::rollback_witness::Record> query() override {
    std::scoped_lock lock(mutex_);
    return record_;
  }

  iotox::Status
  compare_exchange(const iotox::rollback_witness::Record &expected,
                   const iotox::rollback_witness::Record &desired) override {
    std::unique_lock lock(mutex_);
    ++calls_;
    if (fail_before_call_ == calls_) {
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected sync witness outage before CAS"};
    }
    if (pause_before_call_ == calls_) {
      paused_ = true;
      condition_.notify_all();
      condition_.wait(lock, [this] { return pause_released_; });
    }
    if (record_ != expected) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "sync witness CAS conflict"};
    }
    const iotox::Status valid =
        iotox::rollback_witness::validate_transition(expected, desired);
    if (!valid.ok())
      return valid;
    record_ = desired;
    if (fail_after_call_ == calls_) {
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected lost reply after sync witness CAS"};
    }
    return iotox::Status::success();
  }

  bool independently_controlled() const noexcept override { return false; }

  void set(iotox::rollback_witness::Record record) {
    std::scoped_lock lock(mutex_);
    record_ = std::move(record);
  }

  void fail_before(std::size_t call) {
    std::scoped_lock lock(mutex_);
    fail_before_call_ = call;
  }

  void fail_after(std::size_t call) {
    std::scoped_lock lock(mutex_);
    fail_after_call_ = call;
  }

  void pause_before(std::size_t call) {
    std::scoped_lock lock(mutex_);
    pause_before_call_ = call;
    pause_released_ = false;
    paused_ = false;
  }

  [[nodiscard]] bool wait_until_paused(
      std::chrono::milliseconds timeout = std::chrono::seconds(2)) {
    std::unique_lock lock(mutex_);
    return condition_.wait_for(lock, timeout, [this] { return paused_; });
  }

  void release_pause() {
    std::scoped_lock lock(mutex_);
    pause_released_ = true;
    condition_.notify_all();
  }

  [[nodiscard]] iotox::rollback_witness::Record current() const {
    std::scoped_lock lock(mutex_);
    return record_;
  }

private:
  mutable std::mutex mutex_;
  std::condition_variable condition_;
  iotox::rollback_witness::Record record_;
  std::size_t calls_{0U};
  std::size_t fail_before_call_{0U};
  std::size_t fail_after_call_{0U};
  std::size_t pause_before_call_{0U};
  bool paused_{false};
  bool pause_released_{false};
};

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest result{};
  result[0U] = value;
  return result;
}

struct Fixture {
  TemporaryDirectory temporary;
  iotox::security::Sodium sodium;
  iotox::security::DeviceIdentity device;
  iotox::sync::NamespacePolicy policy;
  iotox::rollback_witness::DomainId base_domain{};
  std::shared_ptr<MemoryBackend> backend;
  std::shared_ptr<iotox::sync::SyncGuardedStateWitness> witness;

  Fixture()
      : sodium(iotox::security::Sodium::load().value()),
        device(iotox::security::DeviceIdentity::load_or_create(
                   temporary.path() / "device.identity", sodium, true)
                   .value()),
        backend(std::make_shared<MemoryBackend>()) {
    policy.id = "field-notes";
    policy.root = (temporary.path() / "sync").lexically_normal().string();
    policy.engine = iotox::sync::Engine::range_v1;
    policy.writers = {device.public_key()};
    std::filesystem::create_directory(policy.root);
    if (::chmod(policy.root.c_str(), 0700) != 0) {
      throw std::runtime_error("unable to secure sync test root");
    }
    base_domain[0U] = 0x91U;
    base_domain[15U] = 0x19U;
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    if (!transaction)
      throw std::runtime_error(transaction.status().message());
    auto enrollment = iotox::sync::sync_guarded_state_enrollment_record(
        policy, base_domain, 7U, device, sodium, transaction.value());
    if (!enrollment)
      throw std::runtime_error(enrollment.status().message());
    backend->set(enrollment.value());
    auto domain = iotox::sync::derive_sync_guarded_witness_domain(
        base_domain, device.public_key(), policy.id, sodium);
    if (!domain)
      throw std::runtime_error(domain.status().message());
    iotox::sync::SyncGuardedStateWitness::Config config;
    config.backend = backend;
    config.domain = domain.value();
    config.witness_epoch = 7U;
    config.allow_non_independent_for_testing = true;
    witness = std::make_shared<iotox::sync::SyncGuardedStateWitness>(
        std::move(config), policy, device, sodium);
    const iotox::Status reconciled =
        witness->reconcile(policy, transaction.value());
    if (!reconciled.ok())
      throw std::runtime_error(reconciled.message());
  }

  [[nodiscard]] std::shared_ptr<iotox::sync::SyncGuardedStateWitness>
  replacement_witness() const {
    auto domain = iotox::sync::derive_sync_guarded_witness_domain(
                      base_domain, device.public_key(), policy.id, sodium)
                      .value();
    iotox::sync::SyncGuardedStateWitness::Config config;
    config.backend = backend;
    config.domain = domain;
    config.witness_epoch = 7U;
    config.allow_non_independent_for_testing = true;
    return std::make_shared<iotox::sync::SyncGuardedStateWitness>(
        std::move(config), policy, device, sodium);
  }
};

struct PublicationTransition {
  iotox::sync::SyncReachabilityRoots current;
  iotox::sync::SyncReachabilityRoots next;
  iotox::sync::SignedHead head;
  iotox::sync::SignedHeadBytes encoded{};
};

PublicationTransition prepare_publication_transition(
    Fixture &fixture, const iotox::sync::SyncNamespaceTransaction &transaction,
    std::uint8_t marker) {
  auto roots = iotox::sync::load_sync_rollback_roots(
      fixture.policy, fixture.device.public_key(), fixture.sodium, transaction);
  if (!roots)
    throw std::runtime_error(roots.status().message());
  auto head = iotox::sync::create_signed_head(
      fixture.policy,
      {digest(marker), digest(static_cast<std::uint8_t>(marker + 1U)),
       10U + marker, 5U + marker},
      roots.value().published, fixture.device, fixture.sodium);
  if (!head)
    throw std::runtime_error(head.status().message());
  auto encoded = iotox::sync::encode_signed_head(head.value());
  if (!encoded)
    throw std::runtime_error(encoded.status().message());
  PublicationTransition result;
  result.current = roots.value();
  result.next = roots.value();
  result.next.published = head.value();
  result.head = head.value();
  result.encoded = encoded.value();
  return result;
}

iotox::Status write_publication(const Fixture &fixture,
                                const iotox::sync::SignedHeadBytes &encoded) {
  const auto directory =
      std::filesystem::path(fixture.policy.root) / "published-heads";
  std::error_code error;
  std::filesystem::create_directories(directory, error);
  if (error) {
    return iotox::Status{iotox::ErrorCode::io_error,
                         "unable to create publication test directory"};
  }
  std::filesystem::permissions(directory, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace, error);
  if (error) {
    return iotox::Status{iotox::ErrorCode::io_error,
                         "unable to secure publication test directory"};
  }
  return iotox::StateStore::write_atomic(
      directory / (fixture.policy.id + ".signed-head"), encoded);
}

iotox::sync::SyncRollbackGuard load_guard(const Fixture &fixture) {
  iotox::sync::SyncRollbackGuardStore store(fixture.policy.root);
  auto guard =
      store.load(fixture.policy, fixture.device.public_key(), fixture.sodium);
  if (!guard || !guard.value()) {
    throw std::runtime_error(guard ? "sync guarded witness test guard is absent"
                                   : guard.status().message());
  }
  return *guard.value();
}

iotox::rollback_witness::Record
pending_external_for(Fixture &fixture,
                     const iotox::sync::SyncRollbackGuard &guard,
                     bool fork_target = false) {
  auto external = fixture.backend->current();
  auto old_digest = iotox::sync::sync_guarded_state_digest(
      fixture.policy, guard.committed, fixture.sodium);
  auto next_digest = iotox::sync::sync_guarded_state_digest(
      fixture.policy, *guard.pending, fixture.sodium);
  if (!old_digest || !next_digest) {
    throw std::runtime_error(!old_digest ? old_digest.status().message()
                                         : next_digest.status().message());
  }
  if (external.pending || external.committed.digest != old_digest.value()) {
    throw std::runtime_error("external witness is not the guard predecessor");
  }
  if (fork_target)
    next_digest.value()[0U] ^= 0x80U;
  iotox::rollback_witness::TransactionNonce nonce{};
  nonce[0U] = 0xa5U;
  auto pending = iotox::rollback_witness::begin(
      external, {external.committed.position + 1U, next_digest.value()}, nonce);
  if (!pending)
    throw std::runtime_error(pending.status().message());
  return pending.value();
}

std::vector<std::uint8_t> read_state(const std::filesystem::path &path) {
  auto bytes = iotox::StateStore::read(path);
  if (!bytes)
    throw std::runtime_error(bytes.status().message());
  return bytes.value();
}

} // namespace

IOTOX_TEST(
    "sync guarded witness domains and heads bind exact namespace storage") {
  Fixture fixture;
  std::set<iotox::rollback_witness::DomainId> domains;
  for (std::size_t index = 0U; index < 64U; ++index) {
    const std::string id = "namespace-" + std::to_string(index);
    auto domain = iotox::sync::derive_sync_guarded_witness_domain(
        fixture.base_domain, fixture.device.public_key(), id, fixture.sodium);
    IOTOX_CHECK(domain.ok());
    domains.insert(domain.value());
  }
  IOTOX_CHECK(domains.size() == 64U);

  iotox::sync::SyncRollbackHead head;
  auto first = iotox::sync::sync_guarded_state_digest(fixture.policy, head,
                                                      fixture.sodium);
  IOTOX_CHECK(first.ok());
  auto changed = fixture.policy;
  ++changed.quotas.maximum_lanes;
  auto second =
      iotox::sync::sync_guarded_state_digest(changed, head, fixture.sodium);
  IOTOX_CHECK(second.ok());
  IOTOX_CHECK(first.value() != second.value());
  head.accepted = {1U, digest(0x42U)};
  auto third = iotox::sync::sync_guarded_state_digest(fixture.policy, head,
                                                      fixture.sodium);
  IOTOX_CHECK(third.ok());
  IOTOX_CHECK(first.value() != third.value());

  auto tree = fixture.policy;
  tree.engine = iotox::sync::Engine::tree_v2;
  IOTOX_CHECK(
      !iotox::sync::sync_guarded_state_digest(tree, {}, fixture.sodium).ok());
}

IOTOX_TEST(
    "sync guarded witness advances publication and rejects whole rollback") {
  Fixture fixture;
  iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
  auto published =
      store.publish(fixture.policy, {digest(0x11U), digest(0x12U), 10U, 5U},
                    fixture.device, fixture.sodium);
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(
        fixture.witness->verify_read(fixture.policy, transaction.value()).ok());
  }

  IOTOX_CHECK(
      std::filesystem::remove(std::filesystem::path(fixture.policy.root) /
                              "published-heads" / "field-notes.signed-head"));
  IOTOX_CHECK(std::filesystem::remove(
      std::filesystem::path(fixture.policy.root) / "rollback-guards" /
      "field-notes.rollback-guard"));
  auto replacement = fixture.replacement_witness();
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status replayed =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!replayed.ok());
  IOTOX_CHECK(replayed.code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync guarded witness recovers root landed before remote begin") {
  Fixture fixture;
  fixture.backend->fail_before(1U);
  iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
  auto interrupted =
      store.publish(fixture.policy, {digest(0x21U), digest(0x22U), 11U, 6U},
                    fixture.device, fixture.sodium);
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);

  auto replacement = fixture.replacement_witness();
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
  IOTOX_CHECK(
      replacement->verify_read(fixture.policy, transaction.value()).ok());
}

IOTOX_TEST("sync guarded witness advances every four-root store") {
  Fixture fixture;
  iotox::sync::SignedHeadStore published_store(fixture.policy.root,
                                               fixture.witness);
  auto published = published_store.publish(
      fixture.policy, {digest(0x31U), digest(0x32U), 20U, 10U}, fixture.device,
      fixture.sodium);
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);

  auto candidate = iotox::sync::verified_candidate_head(
      fixture.policy, published.value().head, fixture.sodium);
  IOTOX_CHECK(candidate.ok());
  iotox::sync::AcceptedHeadStore accepted_store(fixture.policy.root,
                                                fixture.witness);
  auto accepted = accepted_store.accept(fixture.policy, candidate.value(),
                                        fixture.device, fixture.sodium);
  IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
  IOTOX_CHECK(accepted.value().accepted());
  IOTOX_CHECK(fixture.backend->current().committed.position == 3U);
  auto accepted_head = accepted_store.load(
      fixture.policy, fixture.device.public_key(), fixture.sodium);
  IOTOX_CHECK(accepted_head.ok());
  IOTOX_CHECK(accepted_head.value().has_value());

  const iotox::sync::ActivatedRevision revision{
      fixture.policy.id, accepted_head.value()->generation,
      accepted_head.value()->record, accepted_head.value()->artifact,
      accepted_head.value()->artifact_bytes};
  iotox::sync::ActivatedRevisionStore activated_store(fixture.policy.root,
                                                      fixture.witness);
  const iotox::Status activated = activated_store.store(
      fixture.policy, revision, fixture.device, fixture.sodium);
  IOTOX_CHECK_MSG(activated.ok(), activated.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 4U);

  iotox::sync::RetentionStore retention_store(fixture.policy.root,
                                              fixture.witness);
  auto pinned = retention_store.pin(fixture.policy, *accepted_head.value(),
                                    fixture.device, fixture.sodium);
  IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
  IOTOX_CHECK(pinned.value() == iotox::sync::RetentionUpdate::inserted);
  IOTOX_CHECK(fixture.backend->current().committed.position == 5U);
  auto unpinned =
      retention_store.unpin(fixture.policy, accepted_head.value()->record,
                            fixture.device, fixture.sodium);
  IOTOX_CHECK_MSG(unpinned.ok(), unpinned.status().message());
  IOTOX_CHECK(unpinned.value());
  IOTOX_CHECK(fixture.backend->current().committed.position == 6U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST(
    "sync guarded witness clears a guard when root commit did not land") {
  Fixture fixture;
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const auto transition =
      prepare_publication_transition(fixture, transaction.value(), 0x41U);
  const iotox::Status interrupted = fixture.witness->transition(
      fixture.policy, transition.current, transition.next, transaction.value(),
      [] {
        return iotox::Status{iotox::ErrorCode::unavailable,
                             "injected failure before root replacement"};
      });
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(load_guard(fixture).pending.has_value());

  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  const auto guard = load_guard(fixture);
  IOTOX_CHECK(!guard.pending);
  IOTOX_CHECK(guard.committed.empty());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);
}

IOTOX_TEST("sync guarded witness recovers a root after late commit error") {
  Fixture fixture;
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const auto transition =
      prepare_publication_transition(fixture, transaction.value(), 0x51U);
  const iotox::Status interrupted = fixture.witness->transition(
      fixture.policy, transition.current, transition.next, transaction.value(),
      [&] {
        const iotox::Status written =
            write_publication(fixture, transition.encoded);
        if (!written.ok())
          return written;
        return iotox::Status{iotox::ErrorCode::unavailable,
                             "injected late root synchronization failure"};
      });
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(load_guard(fixture).pending.has_value());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);

  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(!load_guard(fixture).pending);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST("sync guarded witness joins pending local and remote successors") {
  Fixture fixture;
  fixture.backend->fail_before(1U);
  iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
  auto interrupted =
      store.publish(fixture.policy, {digest(0x61U), digest(0x62U), 30U, 15U},
                    fixture.device, fixture.sodium);
  IOTOX_CHECK(!interrupted.ok());
  const auto guard = load_guard(fixture);
  IOTOX_CHECK(guard.pending.has_value());
  fixture.backend->set(pending_external_for(fixture, guard));

  auto replacement = fixture.replacement_witness();
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(!load_guard(fixture).pending);
  IOTOX_CHECK(!fixture.backend->current().pending);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
}

IOTOX_TEST("sync guarded witness rejects remote advance before root commit") {
  Fixture fixture;
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const auto transition =
      prepare_publication_transition(fixture, transaction.value(), 0x71U);
  const iotox::Status interrupted = fixture.witness->transition(
      fixture.policy, transition.current, transition.next, transaction.value(),
      [] {
        return iotox::Status{iotox::ErrorCode::unavailable,
                             "injected pre-root crash"};
      });
  IOTOX_CHECK(!interrupted.ok());
  const auto guard = load_guard(fixture);
  fixture.backend->set(pending_external_for(fixture, guard));

  auto replacement = fixture.replacement_witness();
  const iotox::Status refused =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(load_guard(fixture).pending.has_value());
  IOTOX_CHECK(fixture.backend->current().pending.has_value());
}

IOTOX_TEST("sync guarded witness finishes remote after local guard commit") {
  Fixture fixture;
  fixture.backend->fail_before(2U);
  iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
  auto interrupted =
      store.publish(fixture.policy, {digest(0x81U), digest(0x82U), 40U, 20U},
                    fixture.device, fixture.sodium);
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(!load_guard(fixture).pending);
  IOTOX_CHECK(fixture.backend->current().pending.has_value());

  auto replacement = fixture.replacement_witness();
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(!fixture.backend->current().pending);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
}

IOTOX_TEST("sync guarded witness resolves lost replies on both CAS steps") {
  {
    Fixture fixture;
    fixture.backend->fail_after(1U);
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    auto published =
        store.publish(fixture.policy, {digest(0x91U), digest(0x92U), 50U, 25U},
                      fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK(!fixture.backend->current().pending);
    IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  }
  {
    Fixture fixture;
    fixture.backend->fail_after(2U);
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    auto published =
        store.publish(fixture.policy, {digest(0xa1U), digest(0xa2U), 60U, 30U},
                      fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    IOTOX_CHECK(!fixture.backend->current().pending);
    IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  }
}

IOTOX_TEST("sync guarded witness rejects root and witness forks") {
  {
    Fixture fixture;
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    IOTOX_CHECK(store
                    .publish(fixture.policy,
                             {digest(0xb1U), digest(0xb2U), 70U, 35U},
                             fixture.device, fixture.sodium)
                    .ok());
    auto fork = fixture.backend->current();
    fork.committed.digest[0U] ^= 0x80U;
    fixture.backend->set(fork);
    auto replacement = fixture.replacement_witness();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
  {
    Fixture fixture;
    auto wrong = fixture.backend->current();
    wrong.domain[0U] ^= 0x01U;
    fixture.backend->set(wrong);
    auto replacement = fixture.replacement_witness();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
  {
    Fixture fixture;
    fixture.backend->fail_before(1U);
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    auto interrupted =
        store.publish(fixture.policy, {digest(0xc1U), digest(0xc2U), 80U, 40U},
                      fixture.device, fixture.sodium);
    IOTOX_CHECK(!interrupted.ok());
    const auto guard = load_guard(fixture);
    fixture.backend->set(pending_external_for(fixture, guard, true));
    auto replacement = fixture.replacement_witness();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
  {
    Fixture fixture;
    fixture.backend->fail_before(1U);
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    auto interrupted =
        store.publish(fixture.policy, {digest(0xd1U), digest(0xd2U), 90U, 45U},
                      fixture.device, fixture.sodium);
    IOTOX_CHECK(!interrupted.ok());
    auto first = store.load(fixture.policy, fixture.sodium);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(first.value().has_value());
    auto third = iotox::sync::create_signed_head(
        fixture.policy, {digest(0xd3U), digest(0xd4U), 91U, 46U}, first.value(),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(third.ok());
    auto encoded = iotox::sync::encode_signed_head(third.value());
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(write_publication(fixture, encoded.value()).ok());
    auto replacement = fixture.replacement_witness();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
}

IOTOX_TEST("sync guarded witness refuses rolled-back early-return decisions") {
  Fixture fixture;
  iotox::sync::SignedHeadStore published_store(fixture.policy.root,
                                               fixture.witness);
  auto published = published_store.publish(
      fixture.policy, {digest(0xe1U), digest(0xe2U), 100U, 50U}, fixture.device,
      fixture.sodium);
  IOTOX_CHECK(published.ok());
  const auto guard_path = std::filesystem::path(fixture.policy.root) /
                          "rollback-guards" / "field-notes.rollback-guard";
  const auto published_guard = read_state(guard_path);

  auto candidate = iotox::sync::verified_candidate_head(
      fixture.policy, published.value().head, fixture.sodium);
  IOTOX_CHECK(candidate.ok());
  iotox::sync::AcceptedHeadStore accepted_store(fixture.policy.root,
                                                fixture.witness);
  IOTOX_CHECK(accepted_store
                  .accept(fixture.policy, candidate.value(), fixture.device,
                          fixture.sodium)
                  .ok());
  IOTOX_CHECK(fixture.backend->current().committed.position == 3U);

  const auto accepted_path = std::filesystem::path(fixture.policy.root) /
                             "accepted-heads" / "field-notes.accepted-head";
  IOTOX_CHECK(std::filesystem::remove(accepted_path));
  IOTOX_CHECK(
      iotox::StateStore::write_atomic(guard_path, published_guard).ok());
  auto wrong_namespace = candidate.value();
  wrong_namespace.namespace_id = "other-namespace";
  auto refused = accepted_store.accept(fixture.policy, wrong_namespace,
                                       fixture.device, fixture.sodium);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync guarded witness transaction fences concurrent root reads") {
  Fixture fixture;
  fixture.backend->pause_before(1U);
  auto writer = std::async(std::launch::async, [&fixture] {
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    return store.publish(fixture.policy,
                         {digest(0xf1U), digest(0xf2U), 110U, 55U},
                         fixture.device, fixture.sodium);
  });
  const bool writer_paused = fixture.backend->wait_until_paused();

  std::promise<void> reader_started;
  auto started = reader_started.get_future();
  auto reader = std::async(std::launch::async, [&fixture, &reader_started] {
    reader_started.set_value();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    if (!transaction)
      return false;
    iotox::sync::SignedHeadStore store(fixture.policy.root, fixture.witness);
    auto loaded =
        store.load(fixture.policy, fixture.sodium, transaction.value());
    return loaded.ok() && loaded.value().has_value();
  });
  started.wait();
  const bool reader_blocked = reader.wait_for(std::chrono::milliseconds(75)) ==
                              std::future_status::timeout;
  fixture.backend->release_pause();
  auto published = writer.get();
  const bool reader_saw_committed = reader.get();

  IOTOX_CHECK(writer_paused);
  IOTOX_CHECK(reader_blocked);
  IOTOX_CHECK_MSG(published.ok(), published.status().message());
  IOTOX_CHECK(reader_saw_committed);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}
