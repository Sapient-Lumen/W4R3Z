#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"
#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <filesystem>
#include <future>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace {

class TemporaryDirectory {
public:
  TemporaryDirectory() {
    path_ = std::filesystem::temp_directory_path() /
            ("iotox-tree-v2-witness-test-" + std::to_string(::getpid()) + "-" +
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
    if (pause_before_ == calls_) {
      paused_ = true;
      condition_.notify_all();
      condition_.wait(lock, [this] { return pause_released_; });
    }
    if (fail_before_ == calls_) {
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected tree-v2 witness outage"};
    }
    if (record_ != expected) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "tree-v2 witness CAS conflict"};
    }
    const iotox::Status valid =
        iotox::rollback_witness::validate_transition(expected, desired);
    if (!valid.ok())
      return valid;
    record_ = desired;
    if (fail_after_ == calls_) {
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected tree-v2 witness lost reply"};
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
    fail_before_ = call;
  }

  void fail_after(std::size_t call) {
    std::scoped_lock lock(mutex_);
    fail_after_ = call;
  }

  void pause_before(std::size_t call) {
    std::scoped_lock lock(mutex_);
    pause_before_ = call;
  }

  void wait_until_paused() {
    std::unique_lock lock(mutex_);
    condition_.wait(lock, [this] { return paused_; });
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
  iotox::rollback_witness::Record record_;
  std::size_t calls_{0U};
  std::size_t fail_before_{0U};
  std::size_t fail_after_{0U};
  std::size_t pause_before_{0U};
  bool paused_{false};
  bool pause_released_{false};
  std::condition_variable condition_;
};

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest result{};
  result[0U] = value;
  return result;
}

[[nodiscard]] std::string lower_hex(std::span<const std::uint8_t> bytes) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result;
  result.reserve(bytes.size() * 2U);
  for (const std::uint8_t byte : bytes) {
    result.push_back(digits[byte >> 4U]);
    result.push_back(digits[byte & 0x0fU]);
  }
  return result;
}

[[nodiscard]] std::filesystem::path guard_path(
    const iotox::sync::NamespacePolicy &policy) {
  return std::filesystem::path(policy.root) / "rollback-guards" /
         (policy.id + ".tree-v2-rollback-guard");
}

[[nodiscard]] std::vector<std::uint8_t>
read_exact(const std::filesystem::path &path) {
  auto bytes = iotox::StateStore::read(path);
  if (!bytes)
    throw std::runtime_error(bytes.status().message());
  return std::move(bytes).value();
}

void write_exact(const std::filesystem::path &path,
                 std::span<const std::uint8_t> bytes) {
  const iotox::Status stored = iotox::StateStore::write_atomic(path, bytes);
  if (!stored.ok())
    throw std::runtime_error(stored.message());
}

struct Fixture {
  TemporaryDirectory temporary;
  iotox::security::Sodium sodium;
  iotox::security::DeviceIdentity device;
  iotox::sync::NamespacePolicy policy;
  iotox::rollback_witness::DomainId base_domain{};
  std::shared_ptr<MemoryBackend> backend;
  std::shared_ptr<iotox::sync::TreeV2StateWitness> witness;

  Fixture()
      : sodium(iotox::security::Sodium::load().value()),
        device(iotox::security::DeviceIdentity::load_or_create(
                   temporary.path() / "device.identity", sodium, true)
                   .value()),
        backend(std::make_shared<MemoryBackend>()) {
    const auto root = temporary.path() / "sync";
    std::filesystem::create_directory(root);
    if (::chmod(root.c_str(), static_cast<mode_t>(0700)) != 0)
      throw std::runtime_error("unable to secure tree-v2 test root");
    policy.id = "field-notes";
    policy.root = root.string();
    policy.engine = iotox::sync::Engine::tree_v2;
    policy.writers = {device.public_key()};
    base_domain[0U] = 0xa1U;
    base_domain[15U] = 0x1aU;
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    if (!transaction)
      throw std::runtime_error(transaction.status().message());
    auto enrollment = iotox::sync::tree_v2_state_enrollment_record(
        policy, base_domain, 11U, device, sodium, transaction.value());
    if (!enrollment)
      throw std::runtime_error(enrollment.status().message());
    backend->set(enrollment.value());
    witness = replacement_witness();
    const iotox::Status reconciled =
        witness->reconcile(policy, transaction.value());
    if (!reconciled.ok())
      throw std::runtime_error(reconciled.message());
  }

  [[nodiscard]] std::shared_ptr<iotox::sync::TreeV2StateWitness>
  replacement_witness() const {
    auto domain = iotox::sync::derive_tree_v2_witness_domain(
        base_domain, device.public_key(), policy.id, sodium);
    if (!domain)
      throw std::runtime_error(domain.status().message());
    iotox::sync::TreeV2StateWitness::Config config;
    config.backend = backend;
    config.domain = domain.value();
    config.witness_epoch = 11U;
    config.allow_non_independent_for_testing = true;
    return std::make_shared<iotox::sync::TreeV2StateWitness>(
        std::move(config), policy, device, sodium);
  }

  [[nodiscard]] iotox::sync::TreeV2Manifest manifest(std::uint64_t generation,
                                                     std::uint8_t value) const {
    return iotox::sync::TreeV2Manifest{{iotox::sync::TreeV2Entry{
        "field.txt", iotox::sync::TreeV2EntryKind::file,
        iotox::sync::TreeV2Version{device.public_key(), generation},
        digest(value), 32U, false}}};
  }

  [[nodiscard]] iotox::sync::TreeV2BranchStoreResult
  publish(std::uint64_t generation, std::uint8_t value) {
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    if (!transaction)
      throw std::runtime_error(transaction.status().message());
    iotox::sync::TreeV2BranchStore store(policy.root, device.public_key(),
                                         witness);
    auto result = store.publish_local(policy, manifest(generation, value),
                                      device, sodium, transaction.value());
    if (!result)
      throw std::runtime_error(result.status().message());
    return result.value();
  }
};

} // namespace

IOTOX_TEST("tree-v2 witness domains and digest bind all semantic roots") {
  Fixture fixture;
  std::vector<iotox::rollback_witness::DomainId> domains;
  for (std::size_t index = 0U; index < 64U; ++index) {
    auto domain = iotox::sync::derive_tree_v2_witness_domain(
        fixture.base_domain, fixture.device.public_key(),
        "namespace-" + std::to_string(index), fixture.sodium);
    IOTOX_CHECK(domain.ok());
    domains.push_back(domain.value());
  }
  const auto namespace_zero = domains.front();
  std::sort(domains.begin(), domains.end());
  IOTOX_CHECK(std::adjacent_find(domains.begin(), domains.end()) ==
              domains.end());
  auto changed_base = fixture.base_domain;
  changed_base[0U] ^= 1U;
  auto base_separated = iotox::sync::derive_tree_v2_witness_domain(
      changed_base, fixture.device.public_key(), "namespace-0", fixture.sodium);
  IOTOX_CHECK(base_separated.ok());
  IOTOX_CHECK(base_separated.value() != namespace_zero);
  auto second_device = iotox::security::DeviceIdentity::load_or_create(
      fixture.temporary.path() / "second.identity", fixture.sodium, true);
  IOTOX_CHECK(second_device.ok());
  auto device_separated = iotox::sync::derive_tree_v2_witness_domain(
      fixture.base_domain, second_device.value().public_key(), "namespace-0",
      fixture.sodium);
  IOTOX_CHECK(device_separated.ok());
  IOTOX_CHECK(device_separated.value() != namespace_zero);

  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  auto state = iotox::sync::load_tree_v2_freshness_state(
      fixture.policy, fixture.device.public_key(), fixture.sodium,
      transaction.value());
  IOTOX_CHECK(state.ok());
  auto initial = iotox::sync::tree_v2_freshness_digest(
      fixture.policy, state.value(), fixture.sodium);
  IOTOX_CHECK(initial.ok());
  auto changed = fixture.policy;
  ++changed.quotas.maximum_objects;
  auto quota = iotox::sync::tree_v2_freshness_digest(changed, state.value(),
                                                     fixture.sodium);
  IOTOX_CHECK(quota.ok());
  IOTOX_CHECK(initial.value() != quota.value());
}

IOTOX_TEST("tree-v2 witness advances branch workspace and maintenance roots") {
  Fixture fixture;
  const auto published = fixture.publish(1U, 0x21U);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const std::filesystem::path worktree = fixture.temporary.path() / "work";
  IOTOX_CHECK(std::filesystem::create_directory(worktree));
  IOTOX_CHECK(::chmod(worktree.c_str(), static_cast<mode_t>(0700)) == 0);
  auto manifest = iotox::sync::tree_v2_manifest_digest(
      fixture.policy, published.snapshot.manifest, fixture.sodium);
  IOTOX_CHECK(manifest.ok());
  const std::vector<iotox::sync::TreeV2Observation> frontier{
      {published.snapshot.head.writer, published.snapshot.head.generation,
       published.record}};
  iotox::sync::TreeV2WorkspaceStore workspace(fixture.policy.root,
                                              fixture.witness);
  auto initialized = workspace.initialize(
      fixture.policy, worktree, manifest.value(), frontier, fixture.device,
      fixture.sodium, &transaction.value());
  IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 3U);
  iotox::sync::TreeV2MaintenanceStore maintenance(fixture.policy.root,
                                                  fixture.witness);
  auto pinned =
      maintenance.pin(fixture.policy, published.record, fixture.device,
                      fixture.sodium, transaction.value());
  IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 4U);
  auto unpinned =
      maintenance.unpin(fixture.policy, published.record, fixture.device,
                        fixture.sodium, transaction.value());
  IOTOX_CHECK_MSG(unpinned.ok(), unpinned.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 5U);
  const auto pending_manifest = digest(0x7aU);
  auto begun = workspace.begin_exchange(
      fixture.policy, manifest.value(), pending_manifest, manifest.value(),
      frontier, fixture.device, fixture.sodium, &transaction.value());
  IOTOX_CHECK_MSG(begun.ok(), begun.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 6U);
  auto finished = workspace.finish_exchange(fixture.policy, pending_manifest,
                                            fixture.device, fixture.sodium,
                                            &transaction.value());
  IOTOX_CHECK_MSG(finished.ok(), finished.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 7U);
  IOTOX_CHECK(
      fixture.witness->verify_read(fixture.policy, transaction.value()).ok());
  auto reanchor = iotox::sync::tree_v2_state_enrollment_record(
      fixture.policy, fixture.base_domain, 12U, fixture.device, fixture.sodium,
      transaction.value());
  IOTOX_CHECK(reanchor.ok());
  IOTOX_CHECK(reanchor.value().committed.position == 1U);
  IOTOX_CHECK(reanchor.value().committed.digest ==
              fixture.backend->current().committed.digest);
}

IOTOX_TEST("tree-v2 witness rejects complete semantic-root rollback") {
  Fixture fixture;
  static_cast<void>(fixture.publish(1U, 0x31U));
  const auto branch_directory =
      std::filesystem::path(fixture.policy.root) / "tree-v2" / "branches";
  for (const auto &entry :
       std::filesystem::directory_iterator(branch_directory)) {
    IOTOX_CHECK(std::filesystem::remove(entry.path()));
  }
  IOTOX_CHECK(std::filesystem::remove(
      std::filesystem::path(fixture.policy.root) / "rollback-guards" /
      "field-notes.tree-v2-rollback-guard"));
  auto replacement = fixture.replacement_witness();
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status replayed =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!replayed.ok());
  IOTOX_CHECK(replayed.code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST(
    "tree-v2 witness rejects a valid-old branch pointer and matching guard") {
  Fixture fixture;
  const auto first = fixture.publish(1U, 0x32U);
  const std::filesystem::path pointer =
      std::filesystem::path(fixture.policy.root) / "tree-v2" / "branches" /
      (lower_hex(fixture.device.public_key()) + ".branch");
  const std::filesystem::path guard = guard_path(fixture.policy);
  const auto old_pointer = read_exact(pointer);
  const auto old_guard = read_exact(guard);

  const auto second = fixture.publish(2U, 0x33U);
  IOTOX_CHECK(second.snapshot.head.generation ==
              first.snapshot.head.generation + 1U);
  const auto current_pointer = read_exact(pointer);
  const auto current_guard = read_exact(guard);
  const auto external_head = fixture.backend->current();
  IOTOX_CHECK(old_pointer != current_pointer);
  IOTOX_CHECK(old_guard != current_guard);

  write_exact(pointer, old_pointer);
  write_exact(guard, old_guard);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const auto live =
      fixture.witness->verify_read(fixture.policy, transaction.value());
  IOTOX_CHECK(!live.ok());
  IOTOX_CHECK(live.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(pointer) == old_pointer);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  auto cold = fixture.replacement_witness();
  const auto restarted = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!restarted.ok());
  IOTOX_CHECK(restarted.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(pointer) == old_pointer);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  write_exact(pointer, current_pointer);
  write_exact(guard, current_guard);
  const auto restored = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(restored.ok(), restored.message());
  IOTOX_CHECK(read_exact(pointer) == current_pointer);
  IOTOX_CHECK(read_exact(guard) == current_guard);
}

IOTOX_TEST(
    "tree-v2 witness rejects a valid-old workspace and matching guard") {
  Fixture fixture;
  const auto published = fixture.publish(1U, 0x34U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const std::filesystem::path worktree = fixture.temporary.path() / "work-old";
  IOTOX_CHECK(std::filesystem::create_directory(worktree));
  IOTOX_CHECK(::chmod(worktree.c_str(), static_cast<mode_t>(0700)) == 0);
  auto active = iotox::sync::tree_v2_manifest_digest(
      fixture.policy, published.snapshot.manifest, fixture.sodium);
  IOTOX_CHECK(active.ok());
  const std::vector<iotox::sync::TreeV2Observation> frontier{
      {published.snapshot.head.writer, published.snapshot.head.generation,
       published.record}};
  iotox::sync::TreeV2WorkspaceStore workspace(fixture.policy.root,
                                              fixture.witness);
  auto initialized = workspace.initialize(
      fixture.policy, worktree, active.value(), frontier, fixture.device,
      fixture.sodium, &transaction.value());
  IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());

  const std::filesystem::path record =
      std::filesystem::path(fixture.policy.root) / "tree-v2" /
      "workspace.state";
  const std::filesystem::path guard = guard_path(fixture.policy);
  const auto old_record = read_exact(record);
  const auto old_guard = read_exact(guard);
  auto pending_manifest = fixture.manifest(1U, 0x35U);
  iotox::sync::TreeV2BranchStore branches(fixture.policy.root);
  auto retained = branches.retain_manifest(
      fixture.policy, pending_manifest, fixture.sodium, transaction.value());
  IOTOX_CHECK_MSG(retained.ok(), retained.status().message());
  auto begun = workspace.begin_exchange(
      fixture.policy, active.value(), retained.value(), active.value(),
      frontier, fixture.device, fixture.sodium, &transaction.value());
  IOTOX_CHECK_MSG(begun.ok(), begun.status().message());
  const auto current_record = read_exact(record);
  const auto current_guard = read_exact(guard);
  const auto external_head = fixture.backend->current();
  IOTOX_CHECK(old_record != current_record);
  IOTOX_CHECK(old_guard != current_guard);

  write_exact(record, old_record);
  write_exact(guard, old_guard);
  const auto live =
      fixture.witness->verify_read(fixture.policy, transaction.value());
  IOTOX_CHECK(!live.ok());
  IOTOX_CHECK(live.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(record) == old_record);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  auto cold = fixture.replacement_witness();
  const auto restarted = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!restarted.ok());
  IOTOX_CHECK(restarted.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(record) == old_record);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  write_exact(record, current_record);
  write_exact(guard, current_guard);
  const auto restored = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(restored.ok(), restored.message());
  IOTOX_CHECK(read_exact(record) == current_record);
  IOTOX_CHECK(read_exact(guard) == current_guard);
}

IOTOX_TEST(
    "tree-v2 witness rejects valid-old maintenance and matching guard") {
  Fixture fixture;
  const auto published = fixture.publish(1U, 0x36U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2MaintenanceStore maintenance(fixture.policy.root,
                                                  fixture.witness);

  const std::filesystem::path record =
      std::filesystem::path(fixture.policy.root) / "tree-v2" /
      "maintenance.state";
  const std::filesystem::path guard = guard_path(fixture.policy);
  auto pinned = maintenance.pin(fixture.policy, published.record,
                                fixture.device, fixture.sodium,
                                transaction.value());
  IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
  IOTOX_CHECK(pinned.value().pins.size() == 1U);
  const auto old_record = read_exact(record);
  const auto old_guard = read_exact(guard);
  auto unpinned = maintenance.unpin(fixture.policy, published.record,
                                    fixture.device, fixture.sodium,
                                    transaction.value());
  IOTOX_CHECK_MSG(unpinned.ok(), unpinned.status().message());
  IOTOX_CHECK(unpinned.value().pins.empty());
  const auto current_record = read_exact(record);
  const auto current_guard = read_exact(guard);
  const auto external_head = fixture.backend->current();
  IOTOX_CHECK(old_record != current_record);
  IOTOX_CHECK(old_guard != current_guard);

  write_exact(record, old_record);
  write_exact(guard, old_guard);
  const auto live =
      fixture.witness->verify_read(fixture.policy, transaction.value());
  IOTOX_CHECK(!live.ok());
  IOTOX_CHECK(live.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(record) == old_record);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  auto cold = fixture.replacement_witness();
  const auto restarted = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!restarted.ok());
  IOTOX_CHECK(restarted.code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(read_exact(record) == old_record);
  IOTOX_CHECK(read_exact(guard) == old_guard);
  IOTOX_CHECK(fixture.backend->current() == external_head);

  write_exact(record, current_record);
  write_exact(guard, current_guard);
  const auto restored = cold->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(restored.ok(), restored.message());
  IOTOX_CHECK(read_exact(record) == current_record);
  IOTOX_CHECK(read_exact(guard) == current_guard);
}

IOTOX_TEST("tree-v2 witness recovers a landed branch before remote begin") {
  Fixture fixture;
  fixture.backend->fail_before(1U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2BranchStore store(
      fixture.policy.root, fixture.device.public_key(), fixture.witness);
  auto interrupted =
      store.publish_local(fixture.policy, fixture.manifest(1U, 0x41U),
                          fixture.device, fixture.sodium, transaction.value());
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);
  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST("tree-v2 witness resolves lost replies and fences stale reads") {
  Fixture fixture;
  fixture.backend->fail_after(1U);
  const auto published = fixture.publish(1U, 0x51U);
  IOTOX_CHECK(published.record != iotox::sync::Digest{});
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);

  const auto branch_directory =
      std::filesystem::path(fixture.policy.root) / "tree-v2" / "branches";
  for (const auto &entry :
       std::filesystem::directory_iterator(branch_directory)) {
    IOTOX_CHECK(std::filesystem::remove(entry.path()));
  }
  IOTOX_CHECK(std::filesystem::remove(
      std::filesystem::path(fixture.policy.root) / "rollback-guards" /
      "field-notes.tree-v2-rollback-guard"));
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2BranchStore stale(
      fixture.policy.root, fixture.device.public_key(), fixture.witness);
  auto refused =
      stale.publish_local(fixture.policy, fixture.manifest(1U, 0x51U),
                          fixture.device, fixture.sodium, transaction.value());
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("tree-v2 witness clears a guard when the root did not land") {
  Fixture fixture;
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  const iotox::Status interrupted = fixture.witness->transition(
      fixture.policy, transaction.value(),
      [&fixture](const iotox::sync::TreeV2FreshnessState &current) {
        auto next = current;
        next.frontier.push_back(iotox::sync::TreeV2Observation{
            fixture.device.public_key(), 1U, digest(0x61U)});
        return iotox::Result<iotox::sync::TreeV2FreshnessState>{
            std::move(next)};
      },
      [] {
        return iotox::Status{iotox::ErrorCode::unavailable,
                             "injected pre-root failure"};
      });
  IOTOX_CHECK(!interrupted.ok());
  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST("tree-v2 witness rejects remote advance before root commit") {
  Fixture fixture;
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2FreshnessState successor;
  auto current = iotox::sync::load_tree_v2_freshness_state(
      fixture.policy, fixture.device.public_key(), fixture.sodium,
      transaction.value());
  IOTOX_CHECK(current.ok());
  successor = current.value();
  successor.frontier.push_back(iotox::sync::TreeV2Observation{
      fixture.device.public_key(), 1U, digest(0x62U)});
  const iotox::Status interrupted = fixture.witness->transition(
      fixture.policy, transaction.value(),
      [&successor](const auto &) {
        return iotox::Result<iotox::sync::TreeV2FreshnessState>{successor};
      },
      [] {
        return iotox::Status{iotox::ErrorCode::unavailable,
                             "injected pre-root failure"};
      });
  IOTOX_CHECK(!interrupted.ok());
  auto successor_digest = iotox::sync::tree_v2_freshness_digest(
      fixture.policy, successor, fixture.sodium);
  IOTOX_CHECK(successor_digest.ok());
  iotox::rollback_witness::TransactionNonce nonce{};
  nonce[0U] = 1U;
  auto pending = iotox::rollback_witness::begin(
      fixture.backend->current(), {2U, successor_digest.value()}, nonce);
  IOTOX_CHECK(pending.ok());
  fixture.backend->set(pending.value());
  auto replacement = fixture.replacement_witness();
  const iotox::Status refused =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("tree-v2 witness joins pending local and remote successors") {
  Fixture fixture;
  fixture.backend->fail_before(1U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2BranchStore store(
      fixture.policy.root, fixture.device.public_key(), fixture.witness);
  auto interrupted =
      store.publish_local(fixture.policy, fixture.manifest(1U, 0x63U),
                          fixture.device, fixture.sodium, transaction.value());
  IOTOX_CHECK(!interrupted.ok());
  auto state = iotox::sync::load_tree_v2_freshness_state(
      fixture.policy, fixture.device.public_key(), fixture.sodium,
      transaction.value());
  IOTOX_CHECK(state.ok());
  auto successor = iotox::sync::tree_v2_freshness_digest(
      fixture.policy, state.value(), fixture.sodium);
  IOTOX_CHECK(successor.ok());
  iotox::rollback_witness::TransactionNonce nonce{};
  nonce[0U] = 2U;
  auto pending = iotox::rollback_witness::begin(fixture.backend->current(),
                                                {2U, successor.value()}, nonce);
  IOTOX_CHECK(pending.ok());
  fixture.backend->set(pending.value());
  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST("tree-v2 witness finishes remote after local guard commit") {
  Fixture fixture;
  fixture.backend->fail_before(2U);
  auto transaction =
      iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
  IOTOX_CHECK(transaction.ok());
  iotox::sync::TreeV2BranchStore store(
      fixture.policy.root, fixture.device.public_key(), fixture.witness);
  auto interrupted =
      store.publish_local(fixture.policy, fixture.manifest(1U, 0x64U),
                          fixture.device, fixture.sodium, transaction.value());
  IOTOX_CHECK(!interrupted.ok());
  IOTOX_CHECK(fixture.backend->current().pending.has_value());
  auto replacement = fixture.replacement_witness();
  const iotox::Status recovered =
      replacement->reconcile(fixture.policy, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending);
}

IOTOX_TEST("tree-v2 witness resolves lost replies on both CAS steps") {
  {
    Fixture fixture;
    fixture.backend->fail_after(1U);
    IOTOX_CHECK(fixture.publish(1U, 0x65U).record != iotox::sync::Digest{});
    IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
    IOTOX_CHECK(!fixture.backend->current().pending);
  }
  {
    Fixture fixture;
    fixture.backend->fail_after(2U);
    IOTOX_CHECK(fixture.publish(1U, 0x66U).record != iotox::sync::Digest{});
    IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
    IOTOX_CHECK(!fixture.backend->current().pending);
  }
}

IOTOX_TEST("tree-v2 witness rejects selector root and pending forks") {
  {
    Fixture fixture;
    static_cast<void>(fixture.publish(1U, 0x67U));
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
    wrong.domain[0U] ^= 1U;
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
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    iotox::sync::TreeV2BranchStore witnessed(
        fixture.policy.root, fixture.device.public_key(), fixture.witness);
    IOTOX_CHECK(!witnessed
                     .publish_local(fixture.policy, fixture.manifest(1U, 0x68U),
                                    fixture.device, fixture.sodium,
                                    transaction.value())
                     .ok());
    auto state = iotox::sync::load_tree_v2_freshness_state(
        fixture.policy, fixture.device.public_key(), fixture.sodium,
        transaction.value());
    IOTOX_CHECK(state.ok());
    auto successor = iotox::sync::tree_v2_freshness_digest(
        fixture.policy, state.value(), fixture.sodium);
    IOTOX_CHECK(successor.ok());
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0U] = 3U;
    auto pending = iotox::rollback_witness::begin(
        fixture.backend->current(), {2U, successor.value()}, nonce);
    IOTOX_CHECK(pending.ok());
    pending.value().pending->digest[0U] ^= 0x40U;
    fixture.backend->set(pending.value());
    auto replacement = fixture.replacement_witness();
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
  {
    Fixture fixture;
    fixture.backend->fail_before(1U);
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    iotox::sync::TreeV2BranchStore witnessed(
        fixture.policy.root, fixture.device.public_key(), fixture.witness);
    IOTOX_CHECK(!witnessed
                     .publish_local(fixture.policy, fixture.manifest(1U, 0x69U),
                                    fixture.device, fixture.sodium,
                                    transaction.value())
                     .ok());
    iotox::sync::TreeV2BranchStore raw(fixture.policy.root,
                                       fixture.device.public_key());
    IOTOX_CHECK(raw.publish_local(fixture.policy, fixture.manifest(2U, 0x6aU),
                                  fixture.device, fixture.sodium,
                                  transaction.value())
                    .ok());
    auto replacement = fixture.replacement_witness();
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::protocol_error);
  }
}

IOTOX_TEST("tree-v2 witness refuses guard tampering and multiple links") {
  const auto guard_path = [](const Fixture &fixture) {
    return std::filesystem::path(fixture.policy.root) / "rollback-guards" /
           "field-notes.tree-v2-rollback-guard";
  };
  {
    Fixture fixture;
    static_cast<void>(fixture.publish(1U, 0x6cU));
    auto bytes = iotox::StateStore::read(guard_path(fixture));
    IOTOX_CHECK(bytes.ok());
    bytes.value()[112U] ^= 1U;
    IOTOX_CHECK(
        iotox::StateStore::write_atomic(guard_path(fixture), bytes.value())
            .ok());
    auto replacement = fixture.replacement_witness();
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    IOTOX_CHECK(transaction.ok());
    const auto refused =
        replacement->reconcile(fixture.policy, transaction.value());
    IOTOX_CHECK(!refused.ok());
  }
  {
    Fixture fixture;
    static_cast<void>(fixture.publish(1U, 0x6dU));
    std::filesystem::create_hard_link(
        guard_path(fixture), fixture.temporary.path() / "linked-guard");
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

IOTOX_TEST("tree-v2 witness transaction fences concurrent root readers") {
  Fixture fixture;
  fixture.backend->pause_before(1U);
  auto published = std::async(std::launch::async, [&fixture] {
    return fixture.publish(1U, 0x6bU).record;
  });
  fixture.backend->wait_until_paused();
  auto read = std::async(std::launch::async, [&fixture] {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(fixture.policy);
    if (!transaction)
      return false;
    iotox::sync::TreeV2BranchStore store(
        fixture.policy.root, fixture.device.public_key(), fixture.witness);
    auto frontier = store.load_frontier(fixture.policy, fixture.sodium,
                                        transaction.value());
    return frontier && frontier.value().size() == 1U;
  });
  IOTOX_CHECK(read.wait_for(std::chrono::milliseconds(100)) ==
              std::future_status::timeout);
  fixture.backend->release_pause();
  IOTOX_CHECK(published.get() != iotox::sync::Digest{});
  IOTOX_CHECK(read.get());
}
