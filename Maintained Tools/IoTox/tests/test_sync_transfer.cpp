#include "iotox/sync_transfer.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <stdexcept>
#include <string_view>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-transfer-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
  }
  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const { return path_; }
private:
  std::filesystem::path path_;
};

iotox::routes::ToxPublicKey route_key(std::uint8_t value) {
  iotox::routes::ToxPublicKey key{};
  key.fill(value);
  return key;
}

iotox::sync::Digest toy_digest(std::span<const std::uint8_t> bytes) {
  iotox::sync::Digest digest{};
  std::uint8_t value = 0U;
  for (std::uint8_t byte : bytes) {
    value = static_cast<std::uint8_t>((value * 33U) ^ byte);
  }
  digest[0U] = value;
  digest[1U] = static_cast<std::uint8_t>(bytes.size());
  return digest;
}

iotox::sync::Digest toy_digest(std::string_view text) {
  return toy_digest(std::span<const std::uint8_t>(
      reinterpret_cast<const std::uint8_t *>(text.data()), text.size()));
}

iotox::Result<iotox::sync::Digest>
hash_file(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    return iotox::Status{iotox::ErrorCode::io_error,
                         "unable to hash sync transfer fixture"};
  }
  std::vector<std::uint8_t> bytes{
      std::istreambuf_iterator<char>(input),
      std::istreambuf_iterator<char>()};
  return toy_digest(bytes);
}

void write_private(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary);
  output << text;
  IOTOX_CHECK(output.good());
  output.close();
  std::filesystem::permissions(
      path, std::filesystem::perms::owner_read |
                std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
}

iotox::routes::Coordinator ready_coordinator() {
  iotox::routes::RouteSet set;
  set.generation = 1U;
  set.stable_device_principal.fill(0x71U);
  set.coordinator_tox_public_key = route_key(0x11U);
  set.members = {
      {route_key(0x11U), iotox::routes::Role::protected_route,
       iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
      {route_key(0x22U), iotox::routes::Role::bulk,
       iotox::routes::ConnectionClass::tcp, 2U, 1U, 0U},
  };
  auto created = iotox::routes::Coordinator::create(set);
  IOTOX_CHECK(created.ok());
  auto coordinator = std::move(created).value();
  IOTOX_CHECK(coordinator.begin_connecting(route_key(0x22U), 22U).ok());
  iotox::routes::RouteProof proof{
      route_key(0x22U), set.stable_device_principal, 1U,
      iotox::routes::kRouteProtocolVersion,
      iotox::routes::ConnectionClass::tcp, 22U, true};
  IOTOX_CHECK(coordinator.authenticate(proof).ok());
  IOTOX_CHECK(coordinator.mark_ready(route_key(0x22U), 22U).ok());
  return coordinator;
}

iotox::routes::Coordinator ready_two_route_coordinator() {
  iotox::routes::RouteSet set;
  set.generation = 1U;
  set.stable_device_principal.fill(0x71U);
  set.coordinator_tox_public_key = route_key(0x11U);
  set.members = {
      {route_key(0x11U), iotox::routes::Role::protected_route,
       iotox::routes::ConnectionClass::tcp, 1U, 1U, 0U},
      {route_key(0x22U), iotox::routes::Role::bulk,
       iotox::routes::ConnectionClass::tcp, 2U, 1U, 0U},
      {route_key(0x33U), iotox::routes::Role::bulk,
       iotox::routes::ConnectionClass::tcp, 2U, 1U, 0U},
  };
  auto created = iotox::routes::Coordinator::create(set);
  IOTOX_CHECK(created.ok());
  auto coordinator = std::move(created).value();
  for (const auto &[value, worker] :
       {std::pair<std::uint8_t, std::uint64_t>{0x22U, 22U},
        std::pair<std::uint8_t, std::uint64_t>{0x33U, 33U}}) {
    IOTOX_CHECK(coordinator.begin_connecting(route_key(value), worker).ok());
    iotox::routes::RouteProof proof{
        route_key(value), set.stable_device_principal, 1U,
        iotox::routes::kRouteProtocolVersion,
        iotox::routes::ConnectionClass::tcp, worker, true};
    IOTOX_CHECK(coordinator.authenticate(proof).ok());
    IOTOX_CHECK(coordinator.mark_ready(route_key(value), worker).ok());
  }
  return coordinator;
}

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root) {
  iotox::sync::NamespacePolicy policy;
  policy.id = "transfer-test";
  policy.root = root.string();
  iotox::sync::PrincipalId writer{};
  writer.fill(0x31U);
  policy.writers = {writer};
  policy.quotas.maximum_artifact_bytes = 1024U;
  policy.quotas.maximum_manifest_bytes = 1024U;
  policy.quotas.maximum_staging_bytes = 2048U;
  policy.quotas.maximum_store_bytes = 4096U;
  return policy;
}

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity identity(
    const std::filesystem::path &path,
    const iotox::security::Sodium &crypto) {
  auto loaded = iotox::security::DeviceIdentity::load_or_create(
      path, crypto, true);
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

struct Fixture {
  std::vector<iotox::routes::WorkerTransferTerminalEvent> events;
  std::uint64_t cancellations{0U};
  std::uint64_t retirements{0U};
  std::uint64_t admission_deferrals{0U};
  bool corrupt_bytes{false};

  iotox::sync::SyncTransferCoordinator::Seams seams() {
    iotox::sync::SyncTransferCoordinator::Seams seams;
    seams.receive_to_path =
        [this](const iotox::routes::ToxPublicKey &, std::uint64_t,
               std::uint32_t file_number,
               const std::filesystem::path &path)
        -> iotox::Result<iotox::FileTransferRecord> {
      if (admission_deferrals != 0U) {
        --admission_deferrals;
        return iotox::Status{
            iotox::ErrorCode::resource_exhausted,
            "injected Agent receive-ceiling admission deferral"};
      }
      write_private(path, corrupt_bytes ? "xxxxxxx" : "payload");
      iotox::FileTransferRecord record;
      record.direction = iotox::FileTransferDirection::incoming;
      record.state = iotox::FileTransferState::active;
      record.friend_number = 9U;
      record.file_number = file_number;
      record.file_size = 7U;
      record.local_path = path;
      return record;
    };
    seams.cancel_transfer =
        [this](const iotox::routes::ToxPublicKey &, std::uint64_t,
               std::uint32_t) {
      ++cancellations;
      return iotox::Status::success();
    };
    seams.retire_transfer =
        [this](const iotox::routes::ToxPublicKey &, std::uint64_t,
               std::uint32_t) {
      ++retirements;
      return iotox::Status::success();
    };
    seams.take_terminal_events =
        [this](std::size_t maximum)
        -> iotox::Result<std::vector<
            iotox::routes::WorkerTransferTerminalEvent>> {
      const std::size_t count = std::min(maximum, events.size());
      std::vector<iotox::routes::WorkerTransferTerminalEvent> output(
          events.begin(), events.begin() + static_cast<std::ptrdiff_t>(count));
      events.erase(events.begin(),
                   events.begin() + static_cast<std::ptrdiff_t>(count));
      return output;
    };
    seams.install.hash_file = hash_file;
    seams.install.cancel_requested = [] { return false; };
    return seams;
  }
};

struct ResumeFixture {
  std::uint64_t calls{0U};
  std::uint64_t retirements{0U};
  std::vector<std::uint64_t> offsets;

  iotox::sync::SyncTransferCoordinator::Seams seams() {
    iotox::sync::SyncTransferCoordinator::Seams result;
    result.receive_to_path = [](
        const iotox::routes::ToxPublicKey &, std::uint64_t,
        std::uint32_t, const std::filesystem::path &)
        -> iotox::Result<iotox::FileTransferRecord> {
      return iotox::Status{
          iotox::ErrorCode::internal_error,
          "resumable fixture used disposable receive seam"};
    };
    result.receive_to_path_from_offset = [this](
        const iotox::routes::ToxPublicKey &, std::uint64_t,
        std::uint32_t file_number, const std::filesystem::path &path,
        std::uint64_t offset)
        -> iotox::Result<iotox::FileTransferRecord> {
      ++calls;
      offsets.push_back(offset);
      std::ofstream output(path, std::ios::binary | std::ios::app);
      output << (offset == 0U ? "pay" : "load");
      IOTOX_CHECK(output.good());
      output.close();
      iotox::FileTransferRecord record;
      record.direction = iotox::FileTransferDirection::incoming;
      record.state = iotox::FileTransferState::active;
      record.friend_number = 9U;
      record.file_number = file_number;
      record.file_size = 7U;
      record.position = offset;
      record.local_path = path;
      return record;
    };
    result.cancel_transfer = [](
        const iotox::routes::ToxPublicKey &, std::uint64_t,
        std::uint32_t) { return iotox::Status::success(); };
    result.retire_transfer = [this](
        const iotox::routes::ToxPublicKey &, std::uint64_t,
        std::uint32_t) {
      ++retirements;
      return iotox::Status::success();
    };
    result.install.hash_file = hash_file;
    result.install.cancel_requested = [] { return false; };
    return result;
  }
};

} // namespace

IOTOX_TEST("sync transfer coordinator commits one completed immutable object") {
  TempDirectory temporary;
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 5001U;
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok());

  Fixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = policy(temporary.path() / "namespace");
  config.maximum_bindings = 4U;
  config.maximum_events_per_service = 4U;
  config.seams = fixture.seams();
  iotox::sync::SyncTransferCoordinator transfers(scheduler, std::move(config));
  auto binding = transfers.accept_offer(attempt.value().attempt_id, 17U);
  IOTOX_CHECK(binding.ok());
  iotox::routes::WorkerTransferTerminalEvent terminal;
  terminal.route_key = binding.value().route_key;
  terminal.worker_id = binding.value().worker_id;
  terminal.transfer.direction = iotox::FileTransferDirection::incoming;
  terminal.transfer.file_number = binding.value().file_number;
  terminal.transfer.file_size = object.bytes;
  terminal.transfer.local_path = binding.value().staging_path;
  terminal.outcome = iotox::routes::WorkerTransferOutcome::completed;
  terminal.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(transfers.handle_terminal(terminal).ok());
  const auto state = scheduler.snapshot();
  IOTOX_CHECK(state.objects.front().state ==
              iotox::sync::ScheduledObjectState::committed);
  IOTOX_CHECK(state.reserved_staging_bytes == 0U);
  IOTOX_CHECK(transfers.snapshot().committed_objects == 1U);
  auto records = iotox::sync::inspect_sync_object_records(
      policy(temporary.path() / "namespace"));
  IOTOX_CHECK(records.ok() && records.value().size() == 1U);
  IOTOX_CHECK(records.value().front() == object);
}

IOTOX_TEST("sync transfer coordinator resumes a fenced partial on a fresh route attempt") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncAttemptStore attempt_store(configured.root);
  auto coordinator = ready_two_route_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 4U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = [&]() {
    return attempt_store.reserve_attempt_id(
        configured, device, crypto);
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto first = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(first.ok() && first.value().attempt_id == 1U);

  ResumeFixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = configured;
  config.maximum_bindings = 2U;
  config.maximum_events_per_service = 2U;
  config.seams = fixture.seams();
  config.attempt_store = &attempt_store;
  config.identity = &device;
  config.sodium = &crypto;
  iotox::sync::SyncTransferCoordinator transfers(
      scheduler, std::move(config));
  auto initial = transfers.accept_offer(first.value().attempt_id, 41U);
  IOTOX_CHECK(initial.ok() && initial.value().resume_offset == 0U);
  IOTOX_CHECK(std::filesystem::file_size(initial.value().staging_path) == 3U);
  auto journal = attempt_store.load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().attempt_id == 1U);

  auto fenced = transfers.fence_route(
      route_key(0x22U), 22U, false, true);
  IOTOX_CHECK(fenced.ok() && fenced.value() == 1U);
  IOTOX_CHECK(fixture.retirements == 1U);
  auto transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.retained_partials == 1U);
  IOTOX_CHECK(transfer_state.retained_attempts == 1U);
  IOTOX_CHECK(transfer_state.retained_bytes == 3U);
  IOTOX_CHECK(transfer_state.retention_fallbacks == 0U);
  IOTOX_CHECK(std::filesystem::exists(initial.value().staging_path));
  IOTOX_CHECK(scheduler.snapshot().objects.front().state ==
              iotox::sync::ScheduledObjectState::pending);

  auto second = scheduler.assign(
      object.kind, object.identity, route_key(0x33U), 33U);
  IOTOX_CHECK(second.ok() && second.value().attempt_id == 2U);
  auto resumed = transfers.accept_offer(second.value().attempt_id, 42U);
  IOTOX_CHECK(resumed.ok() && resumed.value().resume_offset == 3U);
  IOTOX_CHECK(!std::filesystem::exists(initial.value().staging_path));
  IOTOX_CHECK(std::filesystem::file_size(resumed.value().staging_path) == 7U);
  IOTOX_CHECK(fixture.offsets == std::vector<std::uint64_t>({0U, 3U}));
  transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.retained_partials == 0U);
  IOTOX_CHECK(transfer_state.retained_attempts == 1U);
  IOTOX_CHECK(transfer_state.retained_bytes == 3U);
  IOTOX_CHECK(transfer_state.retention_fallbacks == 0U);
  IOTOX_CHECK(transfer_state.resumed_attempts == 1U);
  IOTOX_CHECK(transfer_state.resumed_bytes == 3U);
  journal = attempt_store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().attempt_id == 2U);
  IOTOX_CHECK(journal.value().active.front().route_key == route_key(0x33U));

  iotox::routes::WorkerTransferTerminalEvent stale;
  stale.route_key = route_key(0x22U);
  stale.worker_id = 22U;
  stale.transfer.direction = iotox::FileTransferDirection::incoming;
  stale.transfer.file_number = 41U;
  stale.transfer.file_size = object.bytes;
  stale.transfer.local_path = initial.value().staging_path;
  stale.outcome = iotox::routes::WorkerTransferOutcome::completed;
  stale.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(transfers.handle_terminal(stale).ok());
  IOTOX_CHECK(transfers.snapshot().stale_terminal_events == 1U);

  iotox::routes::WorkerTransferTerminalEvent completed;
  completed.route_key = resumed.value().route_key;
  completed.worker_id = resumed.value().worker_id;
  completed.transfer.direction = iotox::FileTransferDirection::incoming;
  completed.transfer.file_number = resumed.value().file_number;
  completed.transfer.file_size = object.bytes;
  completed.transfer.position = object.bytes;
  completed.transfer.local_path = resumed.value().staging_path;
  completed.outcome = iotox::routes::WorkerTransferOutcome::completed;
  completed.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(transfers.handle_terminal(std::move(completed)).ok());
  IOTOX_CHECK(scheduler.snapshot().objects.front().state ==
              iotox::sync::ScheduledObjectState::committed);
  transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.committed_objects == 1U);
  IOTOX_CHECK(transfer_state.retained_attempts == 1U);
  IOTOX_CHECK(transfer_state.retained_bytes == 3U);
  IOTOX_CHECK(transfer_state.retention_fallbacks == 0U);
  IOTOX_CHECK(transfer_state.resumed_attempts == 1U);
  IOTOX_CHECK(transfer_state.resumed_bytes == 3U);
  journal = attempt_store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
}

IOTOX_TEST("sync transfer coordinator resumes an exact device-signed prefix after restart recovery") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncAttemptStore attempt_store(configured.root);
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};

  auto prior_id = attempt_store.reserve_attempt_id(
      configured, device, crypto);
  IOTOX_CHECK(prior_id.ok() && prior_id.value() == 1U);
  const iotox::sync::DurableSyncAttempt prior{
      prior_id.value(), object, route_key(0x22U), 22U};
  IOTOX_CHECK(attempt_store.begin(
                  configured, prior, device, crypto).ok());
  std::filesystem::path prior_path;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto partial = iotox::sync::create_sync_attempt_partial(
        configured, prior.attempt_id, prior.object,
        transaction.value());
    IOTOX_CHECK(partial.ok());
    prior_path = partial.value().path;
    write_private(prior_path, "pay");
  }
  iotox::sync::SyncInstallSeams recovery_seams;
  recovery_seams.hash_file = hash_file;
  auto recovered = attempt_store.recover(
      configured, device, crypto, recovery_seams);
  IOTOX_CHECK(recovered.ok() && recovered.value().size() == 1U);
  IOTOX_CHECK(recovered.value().front().disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::retained);
  IOTOX_CHECK(std::filesystem::file_size(prior_path) == 3U);
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto different = object;
    different.identity[0U] ^= 0x80U;
    auto absent = attempt_store.retained_attempt(
        configured, different, device.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(absent.ok() && !absent.value().has_value());
  }

  auto coordinator = ready_two_route_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = [&]() {
    return attempt_store.reserve_attempt_id(
        configured, device, crypto);
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto fresh = scheduler.assign(
      object.kind, object.identity, route_key(0x33U), 33U);
  IOTOX_CHECK(fresh.ok() && fresh.value().attempt_id == 2U);

  ResumeFixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = configured;
  config.maximum_bindings = 1U;
  config.maximum_events_per_service = 1U;
  config.seams = fixture.seams();
  config.attempt_store = &attempt_store;
  config.identity = &device;
  config.sodium = &crypto;
  iotox::sync::SyncTransferCoordinator transfers(
      scheduler, std::move(config));
  auto resumed = transfers.accept_offer(
      fresh.value().attempt_id, 51U);
  IOTOX_CHECK(resumed.ok() && resumed.value().resume_offset == 3U);
  IOTOX_CHECK(!std::filesystem::exists(prior_path));
  IOTOX_CHECK(fixture.offsets == std::vector<std::uint64_t>({3U}));
  auto transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.resumed_attempts == 1U);
  IOTOX_CHECK(transfer_state.resumed_bytes == 3U);
  IOTOX_CHECK(transfer_state.restart_resumed_attempts == 1U);
  IOTOX_CHECK(transfer_state.restart_resumed_bytes == 3U);
  auto journal = attempt_store.load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().attempt_id == 2U);
  IOTOX_CHECK(journal.value().active.front().state ==
              iotox::sync::DurableSyncAttemptState::active);

  iotox::routes::WorkerTransferTerminalEvent terminal;
  terminal.route_key = resumed.value().route_key;
  terminal.worker_id = resumed.value().worker_id;
  terminal.transfer.direction = iotox::FileTransferDirection::incoming;
  terminal.transfer.file_number = resumed.value().file_number;
  terminal.transfer.file_size = object.bytes;
  terminal.transfer.position = object.bytes;
  terminal.transfer.local_path = resumed.value().staging_path;
  terminal.outcome = iotox::routes::WorkerTransferOutcome::completed;
  terminal.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(transfers.handle_terminal(std::move(terminal)).ok());
  IOTOX_CHECK(scheduler.snapshot().objects.front().state ==
              iotox::sync::ScheduledObjectState::committed);
  journal = attempt_store.load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
}

IOTOX_TEST("sync transfer admission deferral preserves the exact attempt") {
  TempDirectory temporary;
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 5101U;
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok() && attempt.value().attempt_id == 5101U);

  Fixture fixture;
  fixture.admission_deferrals = 1U;
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = configured;
  config.maximum_bindings = 1U;
  config.maximum_events_per_service = 1U;
  config.seams = fixture.seams();
  iotox::sync::SyncTransferCoordinator transfers(
      scheduler, std::move(config));

  auto deferred = transfers.accept_offer(attempt.value().attempt_id, 19U);
  IOTOX_CHECK(!deferred.ok());
  IOTOX_CHECK(deferred.status().code() ==
              iotox::ErrorCode::resource_exhausted);
  auto transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.bindings.empty());
  IOTOX_CHECK(transfer_state.deferred_offers == 1U);
  IOTOX_CHECK(transfer_state.failed_attempts == 0U);
  auto scheduler_state = scheduler.snapshot();
  IOTOX_CHECK(scheduler_state.attempts.size() == 1U);
  IOTOX_CHECK(scheduler_state.attempts.front().attempt_id == 5101U);
  IOTOX_CHECK(scheduler_state.attempts.front().state ==
              iotox::sync::TransferAttemptState::active);
  IOTOX_CHECK(scheduler_state.objects.front().current_attempt_id == 5101U);
  IOTOX_CHECK(scheduler_state.reserved_staging_bytes == object.bytes);

  auto accepted = transfers.accept_offer(attempt.value().attempt_id, 19U);
  IOTOX_CHECK(accepted.ok());
  IOTOX_CHECK(accepted.value().attempt_id == 5101U);
  IOTOX_CHECK(accepted.value().file_number == 19U);
  transfer_state = transfers.snapshot();
  IOTOX_CHECK(transfer_state.accepted_offers == 1U);
  IOTOX_CHECK(transfer_state.deferred_offers == 1U);
  IOTOX_CHECK(transfer_state.bindings.size() == 1U);
  IOTOX_CHECK(transfers.close().ok());
}

IOTOX_TEST("sync transfer coordinator fences corrupt completion and rejects replay") {
  TempDirectory temporary;
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 6001U;
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::manifest, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok());

  Fixture fixture;
  fixture.corrupt_bytes = true;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = policy(temporary.path() / "namespace");
  config.maximum_bindings = 4U;
  config.maximum_events_per_service = 4U;
  config.seams = fixture.seams();
  iotox::sync::SyncTransferCoordinator transfers(scheduler, std::move(config));
  auto binding = transfers.accept_offer(attempt.value().attempt_id, 18U);
  IOTOX_CHECK(binding.ok());
  iotox::routes::WorkerTransferTerminalEvent terminal;
  terminal.route_key = binding.value().route_key;
  terminal.worker_id = binding.value().worker_id;
  terminal.transfer.direction = iotox::FileTransferDirection::incoming;
  terminal.transfer.file_number = binding.value().file_number;
  terminal.transfer.file_size = object.bytes;
  terminal.transfer.local_path = binding.value().staging_path;
  terminal.outcome = iotox::routes::WorkerTransferOutcome::completed;
  terminal.failure = iotox::ErrorCode::ok;
  fixture.events.push_back(terminal);
  IOTOX_CHECK(!transfers.service().ok());
  IOTOX_CHECK(scheduler.snapshot().attempts.front().state ==
              iotox::sync::TransferAttemptState::fenced);
  IOTOX_CHECK(!std::filesystem::exists(binding.value().staging_path));
  fixture.events.push_back(terminal);
  IOTOX_CHECK(transfers.service().ok());
  IOTOX_CHECK(transfers.snapshot().stale_terminal_events == 1U);
}

IOTOX_TEST("sync transfer coordinator cannot commit after an external attempt fence") {
  TempDirectory temporary;
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id = []() -> iotox::Result<std::uint64_t> {
    return 7001U;
  };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok());

  Fixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = policy(temporary.path() / "namespace");
  config.maximum_bindings = 4U;
  config.maximum_events_per_service = 4U;
  config.seams = fixture.seams();
  iotox::sync::SyncTransferCoordinator transfers(scheduler, std::move(config));
  auto binding = transfers.accept_offer(attempt.value().attempt_id, 19U);
  IOTOX_CHECK(binding.ok());
  IOTOX_CHECK(scheduler.fence_attempt(attempt.value().attempt_id).ok());

  iotox::routes::WorkerTransferTerminalEvent terminal;
  terminal.route_key = binding.value().route_key;
  terminal.worker_id = binding.value().worker_id;
  terminal.transfer.direction = iotox::FileTransferDirection::incoming;
  terminal.transfer.file_number = binding.value().file_number;
  terminal.transfer.file_size = object.bytes;
  terminal.transfer.local_path = binding.value().staging_path;
  terminal.outcome = iotox::routes::WorkerTransferOutcome::completed;
  terminal.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(!transfers.handle_terminal(terminal).ok());
  IOTOX_CHECK(!std::filesystem::exists(binding.value().staging_path));
  auto records = iotox::sync::inspect_sync_object_records(
      policy(temporary.path() / "namespace"));
  IOTOX_CHECK(records.ok() && records.value().empty());
}

IOTOX_TEST("sync transfer coordinator persists live truth before receive and clears it after commit") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncAttemptStore attempt_store(configured.root);
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id =
      [&attempt_store, &configured, &device, &crypto]() {
        return attempt_store.reserve_attempt_id(
            configured, device, crypto);
      };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok() && attempt.value().attempt_id == 1U);

  Fixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = configured;
  config.maximum_bindings = 4U;
  config.maximum_events_per_service = 4U;
  config.seams = fixture.seams();
  config.attempt_store = &attempt_store;
  config.identity = &device;
  config.sodium = &crypto;
  iotox::sync::SyncTransferCoordinator transfers(scheduler, std::move(config));
  auto binding = transfers.accept_offer(attempt.value().attempt_id, 20U);
  IOTOX_CHECK(binding.ok());
  auto journal = attempt_store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().attempt_id ==
              attempt.value().attempt_id);

  iotox::routes::WorkerTransferTerminalEvent terminal;
  terminal.route_key = binding.value().route_key;
  terminal.worker_id = binding.value().worker_id;
  terminal.transfer.direction = iotox::FileTransferDirection::incoming;
  terminal.transfer.file_number = binding.value().file_number;
  terminal.transfer.file_size = object.bytes;
  terminal.transfer.local_path = binding.value().staging_path;
  terminal.outcome = iotox::routes::WorkerTransferOutcome::completed;
  terminal.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(transfers.handle_terminal(std::move(terminal)).ok());
  journal = iotox::sync::SyncAttemptStore(configured.root)
                .load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
  IOTOX_CHECK(journal.value().high_attempt_id == 1U);
  IOTOX_CHECK(scheduler.snapshot().objects.front().state ==
              iotox::sync::ScheduledObjectState::committed);
}

IOTOX_TEST("sync transfer close cancels transport and clears durable staging truth") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncAttemptStore attempt_store(configured.root);
  auto coordinator = ready_coordinator();
  iotox::sync::SyncObjectScheduler::Config scheduler_config;
  scheduler_config.maximum_objects = 1U;
  scheduler_config.maximum_attempts = 2U;
  scheduler_config.maximum_staging_bytes = 2048U;
  scheduler_config.make_attempt_id =
      [&attempt_store, &configured, &device, &crypto]() {
        return attempt_store.reserve_attempt_id(
            configured, device, crypto);
      };
  iotox::sync::SyncObjectScheduler scheduler(
      coordinator, std::move(scheduler_config));
  const iotox::sync::SyncObjectRecord object{
      iotox::sync::SyncObjectKind::artifact, toy_digest("payload"), 7U};
  IOTOX_CHECK(scheduler.add_object(object).ok());
  auto attempt = scheduler.assign(
      object.kind, object.identity, route_key(0x22U), 22U);
  IOTOX_CHECK(attempt.ok());

  Fixture fixture;
  iotox::sync::SyncTransferCoordinator::Config config;
  config.policy = configured;
  config.maximum_bindings = 1U;
  config.maximum_events_per_service = 1U;
  config.seams = fixture.seams();
  config.attempt_store = &attempt_store;
  config.identity = &device;
  config.sodium = &crypto;
  iotox::sync::SyncTransferCoordinator transfers(
      scheduler, std::move(config));
  auto binding = transfers.accept_offer(attempt.value().attempt_id, 27U);
  IOTOX_CHECK(binding.ok());
  IOTOX_CHECK(std::filesystem::exists(binding.value().staging_path));
  auto journal = attempt_store.load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);

  IOTOX_CHECK(transfers.close().ok());
  IOTOX_CHECK(transfers.close().ok());
  IOTOX_CHECK(fixture.cancellations == 1U);
  IOTOX_CHECK(!std::filesystem::exists(binding.value().staging_path));
  journal = attempt_store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
  IOTOX_CHECK(transfers.snapshot().closed);
  const auto state = scheduler.snapshot();
  IOTOX_CHECK(state.attempts.front().state ==
              iotox::sync::TransferAttemptState::fenced);
  IOTOX_CHECK(state.reserved_staging_bytes == 0U);

  iotox::routes::WorkerTransferTerminalEvent late;
  late.route_key = binding.value().route_key;
  late.worker_id = binding.value().worker_id;
  late.transfer.direction = iotox::FileTransferDirection::incoming;
  late.transfer.file_number = binding.value().file_number;
  late.transfer.file_size = object.bytes;
  late.transfer.local_path = binding.value().staging_path;
  late.outcome = iotox::routes::WorkerTransferOutcome::completed;
  late.failure = iotox::ErrorCode::ok;
  IOTOX_CHECK(!transfers.handle_terminal(std::move(late)).ok());
  auto records = iotox::sync::inspect_sync_object_records(configured);
  IOTOX_CHECK(records.ok() && records.value().empty());
}
