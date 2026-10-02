#include "test_harness.hpp"

#include "iotox/sync_automation.hpp"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::SyncAutomationActionKind;
using iotox::sync::SyncAutomationActivation;
using iotox::sync::SyncAutomationMode;
using iotox::sync::SyncAutomationPolicy;
using iotox::sync::SyncAutomationScheduler;
using iotox::sync::SyncAutomationSpec;
using iotox::sync::SyncAutomationStore;
using iotox::sync::SyncAutomationStoreDecision;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-automation-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
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
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
  auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

SyncAutomationSpec publisher(std::string namespace_id,
                             const std::filesystem::path &path) {
  SyncAutomationSpec spec;
  spec.namespace_id = std::move(namespace_id);
  spec.mode = SyncAutomationMode::publish;
  spec.source_path = path.lexically_normal().string();
  spec.interval_ms = 2000U;
  spec.retry_initial_ms = 100U;
  spec.retry_maximum_ms = 400U;
  return spec;
}

SyncAutomationSpec follower(std::string namespace_id, std::uint8_t principal,
                            SyncAutomationActivation activation) {
  SyncAutomationSpec spec;
  spec.namespace_id = std::move(namespace_id);
  spec.mode = SyncAutomationMode::follow;
  spec.activation = activation;
  iotox::sync::PrincipalId source{};
  source.fill(principal);
  spec.source_principals = {source};
  spec.interval_ms = 2000U;
  spec.retry_initial_ms = 100U;
  spec.retry_maximum_ms = 400U;
  return spec;
}

SyncAutomationSpec writable(std::string namespace_id,
                            const std::filesystem::path &path,
                            std::uint8_t principal = 0U) {
    SyncAutomationSpec spec;
    spec.namespace_id = std::move(namespace_id);
    spec.mode = principal == 0U ? SyncAutomationMode::writable
                                : SyncAutomationMode::bidirectional;
    spec.source_path = path.lexically_normal().string();
    if (principal != 0U) {
      iotox::sync::PrincipalId source{};
      source.fill(principal);
      spec.source_principals = {source};
    }
    spec.interval_ms = 2000U;
    spec.retry_initial_ms = 100U;
    spec.retry_maximum_ms = 400U;
    return spec;
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return {std::istreambuf_iterator<char>(input),
          std::istreambuf_iterator<char>()};
}

void write_bytes(const std::filesystem::path &path,
                 const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
}

} // namespace

IOTOX_TEST("sync automation policy store signs generations and tombstones") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  SyncAutomationStore store(temporary.path());

  auto created = store.put(
      publisher("photos", temporary.path() / "source"), device, crypto);
  IOTOX_CHECK_MSG(created.ok(), created.status().message());
  IOTOX_CHECK(created.value().decision == SyncAutomationStoreDecision::created);
  IOTOX_CHECK(created.value().policy.generation == 1U);
  IOTOX_CHECK(iotox::sync::verify_sync_automation_policy(
                  created.value().policy, device.public_key(), crypto).ok());

  auto duplicate = store.put(
      publisher("photos", temporary.path() / "source"), device, crypto);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().decision ==
              SyncAutomationStoreDecision::duplicate);
  IOTOX_CHECK(duplicate.value().policy.generation == 1U);

  auto followed = store.put(
      follower("photos", 0x51U, SyncAutomationActivation::verified), device,
      crypto);
  IOTOX_CHECK(followed.ok());
  IOTOX_CHECK(followed.value().decision ==
              SyncAutomationStoreDecision::replaced);
  IOTOX_CHECK(followed.value().policy.generation == 2U);

  auto disabled = store.disable("photos", device, crypto);
  IOTOX_CHECK(disabled.ok());
  IOTOX_CHECK(disabled.value().decision ==
              SyncAutomationStoreDecision::disabled);
  IOTOX_CHECK(disabled.value().policy.generation == 3U);
  IOTOX_CHECK(disabled.value().policy.mode == SyncAutomationMode::disabled);

  auto loaded = store.load(device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value().size() == 1U);
  IOTOX_CHECK(loaded.value().front() == disabled.value().policy);

  auto other = identity(temporary.path() / "other.identity", crypto);
  IOTOX_CHECK(!store.load(other.public_key(), crypto).ok());
}

IOTOX_TEST("sync automation policy refuses tamper and unsafe records") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  SyncAutomationStore store(temporary.path());
  IOTOX_CHECK(!store.put(publisher("bad", "/"), device, crypto).ok());
  auto invalid_follow = follower(
      "bad", 0U, SyncAutomationActivation::verified);
  invalid_follow.source_principals.clear();
  IOTOX_CHECK(!store.put(invalid_follow, device, crypto).ok());

  auto created = store.put(
      publisher("safe", temporary.path() / "source"), device, crypto);
  IOTOX_CHECK(created.ok());
  const auto path = temporary.path() / "automation" / "safe.automation";
  auto bytes = read_bytes(path);
  IOTOX_CHECK(!bytes.empty());
  bytes.back() ^= 0x40U;
  write_bytes(path, bytes);
  IOTOX_CHECK(!store.load(device.public_key(), crypto).ok());

  bytes.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_sync_automation_policy(bytes).ok());
}

IOTOX_TEST("sync automation scheduler bounds retry and fences stale work") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  SyncAutomationStore store(temporary.path());
  auto publishing = store.put(
      publisher("publish", temporary.path() / "source"), device, crypto);
  auto following = store.put(
      follower("follow", 0x61U, SyncAutomationActivation::verified), device,
      crypto);
  IOTOX_CHECK(publishing.ok() && following.ok());

  SyncAutomationScheduler scheduler;
  IOTOX_CHECK(scheduler.replace(
                  {publishing.value().policy, following.value().policy},
                  1000U).ok());
  auto immediate = scheduler.claim_periodic(1000U);
  IOTOX_CHECK(immediate.size() == 2U);
  IOTOX_CHECK(scheduler.claim_periodic(1000U).empty());

  const auto publish_action =
      immediate[0U].kind == SyncAutomationActionKind::publish
          ? immediate[0U]
          : immediate[1U];
  const auto pull_action =
      immediate[0U].kind == SyncAutomationActionKind::pull
          ? immediate[0U]
          : immediate[1U];
  IOTOX_CHECK(scheduler.complete(publish_action, ErrorCode::io_error,
                                 1000U).ok());
  IOTOX_CHECK(scheduler.claim_periodic(1099U).empty());
  auto retry = scheduler.claim_periodic(1100U);
  IOTOX_CHECK(retry.size() == 1U &&
              retry.front().kind == SyncAutomationActionKind::publish);
  IOTOX_CHECK(scheduler.complete(retry.front(), ErrorCode::io_error,
                                 1100U).ok());
  IOTOX_CHECK(scheduler.claim_periodic(1299U).empty());
  retry = scheduler.claim_periodic(1300U);
  IOTOX_CHECK(retry.size() == 1U);
  IOTOX_CHECK(scheduler.complete(retry.front(), ErrorCode::io_error,
                                 1300U).ok());
  IOTOX_CHECK(scheduler.claim_periodic(1699U).empty());
  retry = scheduler.claim_periodic(1700U);
  IOTOX_CHECK(retry.size() == 1U);
  IOTOX_CHECK(scheduler.complete(retry.front(), ErrorCode::ok, 1700U).ok());
  IOTOX_CHECK(scheduler.claim_periodic(3699U).empty());

  auto activation = scheduler.claim_activation("follow", 1000U);
  IOTOX_CHECK(activation.ok());
  IOTOX_CHECK(!scheduler.claim_activation("follow", 1000U).ok());
  IOTOX_CHECK(scheduler.complete(activation.value(), ErrorCode::io_error,
                                 1000U).ok());
  IOTOX_CHECK(!scheduler.claim_activation("follow", 1099U).ok());
  activation = scheduler.claim_activation("follow", 1100U);
  IOTOX_CHECK(activation.ok());
  IOTOX_CHECK(scheduler.complete(activation.value(), ErrorCode::ok,
                                 1100U).ok());

  auto replacement_spec = publisher("publish", temporary.path() / "other");
  auto replacement = store.put(replacement_spec, device, crypto);
  auto follow_replacement = store.put(
      follower("follow", 0x62U, SyncAutomationActivation::verified), device,
      crypto);
  IOTOX_CHECK(replacement.ok() && follow_replacement.ok());
  IOTOX_CHECK(scheduler.replace(
                  {replacement.value().policy,
                   follow_replacement.value().policy},
                  2000U).ok());
  IOTOX_CHECK(scheduler.complete(pull_action, ErrorCode::ok, 2000U).ok());
  const auto snapshot = scheduler.snapshot();
  IOTOX_CHECK(snapshot.size() == 2U);
  IOTOX_CHECK(snapshot[0U].namespace_id == "follow");
  IOTOX_CHECK(!snapshot[0U].periodic_busy);
  IOTOX_CHECK(snapshot[0U].policy_generation == 2U);
  IOTOX_CHECK(snapshot[0U].periodic_attempts == 0U);
  IOTOX_CHECK(snapshot[1U].namespace_id == "publish");
  IOTOX_CHECK(snapshot[1U].policy_generation == 2U);
  IOTOX_CHECK(snapshot[1U].periodic_attempts == 0U);
}

IOTOX_TEST(
    "sync automation freezes writable and multi-peer bidirectional work") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    SyncAutomationStore store(temporary.path());

    auto local = store.put(writable("shared", temporary.path() / "shared-tree"),
                           device, crypto);
    IOTOX_CHECK_MSG(local.ok(), local.status().message());
    IOTOX_CHECK(local.value().policy.mode == SyncAutomationMode::writable);
    auto peer =
        store.put(writable("shared", temporary.path() / "shared-tree", 0x7aU),
                  device, crypto);
    IOTOX_CHECK_MSG(peer.ok(), peer.status().message());
    IOTOX_CHECK(peer.value().decision == SyncAutomationStoreDecision::replaced);
    IOTOX_CHECK(peer.value().policy.mode == SyncAutomationMode::bidirectional);
    IOTOX_CHECK(peer.value().policy.source_principals.size() == 1U);
    IOTOX_CHECK(peer.value().policy.source_principals.front()[0U] == 0x7aU);

    auto multi_spec = writable("shared", temporary.path() / "shared-tree");
    multi_spec.mode = SyncAutomationMode::bidirectional;
    iotox::sync::PrincipalId lower{};
    lower.fill(0x31U);
    iotox::sync::PrincipalId upper{};
    upper.fill(0x7aU);
    multi_spec.source_principals = {lower, upper};
    auto multi = store.put(multi_spec, device, crypto);
    IOTOX_CHECK_MSG(multi.ok(), multi.status().message());
    IOTOX_CHECK(multi.value().policy.record_format ==
                iotox::sync::kCurrentSyncAutomationRecordFormat);
    IOTOX_CHECK(multi.value().policy.generation == 3U);

    auto encoded =
        iotox::sync::encode_sync_automation_policy(multi.value().policy);
    IOTOX_CHECK(encoded.ok());
    IOTOX_CHECK(encoded.value().size() == 4808U);
    auto decoded = iotox::sync::decode_sync_automation_policy(encoded.value());
    IOTOX_CHECK(decoded.ok() && decoded.value() == multi.value().policy);

    SyncAutomationScheduler scheduler;
    IOTOX_CHECK(scheduler.replace({local.value().policy}, 1000U).ok());
    auto actions = scheduler.claim_periodic(1000U);
    IOTOX_CHECK(actions.size() == 1U);
    IOTOX_CHECK(actions.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.replace({multi.value().policy}, 2000U).ok());
    actions = scheduler.claim_periodic(2000U);
    IOTOX_CHECK(actions.size() == 1U);
    IOTOX_CHECK(actions.front().kind == SyncAutomationActionKind::pull);
    IOTOX_CHECK(actions.front().source_principal == lower);
    IOTOX_CHECK(scheduler.claim_periodic(2000U).empty());
    auto forged_action = actions.front();
    forged_action.source_principal.fill(0xeeU);
    IOTOX_CHECK(
        !scheduler.complete(forged_action, ErrorCode::ok, 2000U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(2000U).empty());
    IOTOX_CHECK(scheduler.complete(actions.front(), ErrorCode::unavailable,
                                   2000U).ok());
    actions = scheduler.claim_periodic(2000U);
    IOTOX_CHECK(actions.size() == 1U);
    IOTOX_CHECK(actions.front().source_principal == upper);
    IOTOX_CHECK(scheduler.complete(actions.front(), ErrorCode::ok, 2000U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(2099U).empty());
    actions = scheduler.claim_periodic(2100U);
    IOTOX_CHECK(actions.size() == 1U);
    IOTOX_CHECK(actions.front().source_principal == lower);
    IOTOX_CHECK(scheduler.complete(actions.front(), ErrorCode::ok, 2100U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(3999U).empty());
    actions = scheduler.claim_periodic(4000U);
    IOTOX_CHECK(actions.size() == 1U);
    IOTOX_CHECK(actions.front().source_principal == upper);
    IOTOX_CHECK(scheduler.complete(actions.front(), ErrorCode::ok, 4000U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(4099U).empty());
    const auto multi_runtime = scheduler.snapshot();
    IOTOX_CHECK(multi_runtime.size() == 1U);
    IOTOX_CHECK(multi_runtime.front().periodic_attempts == 4U);
    IOTOX_CHECK(multi_runtime.front().periodic_successes == 3U);
    IOTOX_CHECK(multi_runtime.front().periodic_failures == 1U);
    IOTOX_CHECK(multi_runtime.front().consecutive_periodic_failures == 0U);

    auto invalid_local =
        writable("bad-local", temporary.path() / "tree", 0x33U);
    invalid_local.mode = SyncAutomationMode::writable;
    IOTOX_CHECK(
        !iotox::sync::validate_sync_automation_spec(invalid_local).ok());
    auto invalid_peer = writable("bad-peer", temporary.path() / "tree");
    invalid_peer.mode = SyncAutomationMode::bidirectional;
    IOTOX_CHECK(!iotox::sync::validate_sync_automation_spec(invalid_peer).ok());

    auto noncanonical = multi_spec;
    noncanonical.source_principals = {upper, lower};
    IOTOX_CHECK(
        !iotox::sync::validate_sync_automation_spec(noncanonical).ok());
    noncanonical.source_principals = {lower, lower};
    IOTOX_CHECK(
        !iotox::sync::validate_sync_automation_spec(noncanonical).ok());

    auto bounded = multi_spec;
    bounded.source_principals.clear();
    for (std::uint8_t value = 1U;
         value <= iotox::sync::kMaximumSyncAutomationSourcePrincipals;
         ++value) {
        iotox::sync::PrincipalId principal{};
        principal.fill(value);
        bounded.source_principals.push_back(principal);
    }
    IOTOX_CHECK(iotox::sync::validate_sync_automation_spec(bounded).ok());
    iotox::sync::PrincipalId excess{};
    excess.fill(0xffU);
    bounded.source_principals.push_back(excess);
    IOTOX_CHECK(!iotox::sync::validate_sync_automation_spec(bounded).ok());
}

IOTOX_TEST("sync automation source changes wake local publication") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    SyncAutomationStore store(temporary.path());

    auto local = store.put(writable("local", temporary.path() / "local-tree"),
                           device, crypto);
    auto publishing = store.put(
        publisher("publish", temporary.path() / "publish-tree"), device,
        crypto);
    auto shared_spec = writable("shared", temporary.path() / "shared-tree");
    shared_spec.mode = SyncAutomationMode::bidirectional;
    iotox::sync::PrincipalId first{};
    first.fill(0x21U);
    iotox::sync::PrincipalId second{};
    second.fill(0x41U);
    shared_spec.source_principals = {first, second};
    auto shared = store.put(shared_spec, device, crypto);
    IOTOX_CHECK(local.ok() && publishing.ok() && shared.ok());

    SyncAutomationScheduler scheduler;
    IOTOX_CHECK(
        scheduler
            .replace({local.value().policy, publishing.value().policy,
                      shared.value().policy},
                     1000U)
            .ok());
    auto initial = scheduler.claim_periodic(1000U);
    IOTOX_CHECK(initial.size() == 3U);
    for (const auto &action : initial)
        IOTOX_CHECK(scheduler.complete(action, ErrorCode::ok, 1000U).ok());
    auto second_shared_peer = scheduler.claim_periodic(1000U);
    IOTOX_CHECK(second_shared_peer.size() == 1U);
    IOTOX_CHECK(second_shared_peer.front().policy.namespace_id == "shared");
    IOTOX_CHECK(second_shared_peer.front().kind ==
                SyncAutomationActionKind::pull);
    IOTOX_CHECK(scheduler.complete(second_shared_peer.front(), ErrorCode::ok,
                                   1000U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(1999U).empty());

    IOTOX_CHECK(scheduler.trigger_source_change("publish", 1500U).ok());
    IOTOX_CHECK(scheduler.trigger_source_change("local", 1500U).ok());
    IOTOX_CHECK(scheduler.trigger_source_change("shared", 1500U).ok());
    auto woke = scheduler.claim_periodic(1500U);
    IOTOX_CHECK(woke.size() == 3U);
    const auto shared_action = std::find_if(
        woke.begin(), woke.end(), [](const auto &action) {
          return action.policy.namespace_id == "shared";
        });
    IOTOX_CHECK(shared_action != woke.end());
    IOTOX_CHECK(shared_action->kind == SyncAutomationActionKind::publish);

    for (const auto &action : woke)
        IOTOX_CHECK(scheduler.complete(action, ErrorCode::ok, 1500U).ok());
    auto snapshot = scheduler.snapshot();
    const auto shared_runtime = std::find_if(
        snapshot.begin(), snapshot.end(), [](const auto &runtime) {
          return runtime.namespace_id == "shared";
        });
    IOTOX_CHECK(shared_runtime != snapshot.end());
    IOTOX_CHECK(!shared_runtime->source_publish_pending);

    IOTOX_CHECK(scheduler.trigger_source_change("shared", 1600U).ok());
    woke = scheduler.claim_periodic(1600U);
    IOTOX_CHECK(woke.size() == 1U);
    IOTOX_CHECK(woke.front().policy.namespace_id == "shared");
    IOTOX_CHECK(woke.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(woke.front(), ErrorCode::io_error,
                                   1600U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(1699U).empty());
    woke = scheduler.claim_periodic(1700U);
    IOTOX_CHECK(woke.size() == 1U);
    IOTOX_CHECK(woke.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(woke.front(), ErrorCode::ok, 1700U).ok());

    auto peer_retry = scheduler.claim_periodic(3000U);
    IOTOX_CHECK(peer_retry.size() == 1U);
    IOTOX_CHECK(peer_retry.front().policy.namespace_id == "shared");
    IOTOX_CHECK(peer_retry.front().kind == SyncAutomationActionKind::pull);
    IOTOX_CHECK(scheduler.complete(peer_retry.front(), ErrorCode::io_error,
                                   3000U).ok());
    auto failure_snapshot = scheduler.snapshot();
    auto failed_shared_runtime = std::find_if(
        failure_snapshot.begin(), failure_snapshot.end(), [](const auto &runtime) {
          return runtime.namespace_id == "shared";
        });
    IOTOX_CHECK(failed_shared_runtime != failure_snapshot.end());
    IOTOX_CHECK(failed_shared_runtime->consecutive_periodic_failures == 1U);

    IOTOX_CHECK(scheduler.trigger_source_change("shared", 3050U).ok());
    auto local_publish = scheduler.claim_periodic(3050U);
    IOTOX_CHECK(local_publish.size() == 1U);
    IOTOX_CHECK(local_publish.front().policy.namespace_id == "shared");
    IOTOX_CHECK(local_publish.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(local_publish.front(), ErrorCode::ok,
                                   3050U).ok());
    failure_snapshot = scheduler.snapshot();
    failed_shared_runtime = std::find_if(
        failure_snapshot.begin(), failure_snapshot.end(), [](const auto &runtime) {
          return runtime.namespace_id == "shared";
        });
    IOTOX_CHECK(failed_shared_runtime != failure_snapshot.end());
    IOTOX_CHECK(failed_shared_runtime->consecutive_periodic_failures == 1U);

    IOTOX_CHECK(!scheduler.trigger_source_change("missing", 1700U).ok());
    IOTOX_CHECK(!scheduler.trigger_source_change("follow", 1700U).ok());
}

IOTOX_TEST("sync automation debounces source bursts and preserves busy changes") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    SyncAutomationStore store(temporary.path());

    auto publishing = store.put(
        publisher("publish", temporary.path() / "publish-tree"), device,
        crypto);
    IOTOX_CHECK(publishing.ok());

    SyncAutomationScheduler scheduler;
    IOTOX_CHECK(scheduler.replace({publishing.value().policy}, 1000U).ok());
    auto initial = scheduler.claim_periodic(1000U);
    IOTOX_CHECK(initial.size() == 1U);
    IOTOX_CHECK(scheduler.trigger_source_change("publish", 1010U, 250U).ok());
    auto busy_snapshot = scheduler.snapshot();
    IOTOX_CHECK(busy_snapshot.size() == 1U);
    IOTOX_CHECK(busy_snapshot.front().source_publish_pending);
    IOTOX_CHECK(scheduler.complete(initial.front(), ErrorCode::ok, 1020U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(1259U).empty());
    auto preserved = scheduler.claim_periodic(1260U);
    IOTOX_CHECK(preserved.size() == 1U);
    IOTOX_CHECK(preserved.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(preserved.front(), ErrorCode::ok,
                                   1260U).ok());

    IOTOX_CHECK(scheduler.trigger_source_change("publish", 1300U, 250U).ok());
    IOTOX_CHECK(scheduler.trigger_source_change("publish", 1310U, 250U).ok());
    auto burst_snapshot = scheduler.snapshot();
    IOTOX_CHECK(burst_snapshot.size() == 1U);
    IOTOX_CHECK(burst_snapshot.front().source_publish_pending);
    IOTOX_CHECK(burst_snapshot.front().next_periodic_ms == 1550U);
    IOTOX_CHECK(scheduler.claim_periodic(1549U).empty());
    auto coalesced = scheduler.claim_periodic(1550U);
    IOTOX_CHECK(coalesced.size() == 1U);
    IOTOX_CHECK(coalesced.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(coalesced.front(), ErrorCode::ok,
                                   1550U).ok());
    auto done = scheduler.snapshot();
    IOTOX_CHECK(done.size() == 1U);
    IOTOX_CHECK(!done.front().source_publish_pending);
    IOTOX_CHECK(done.front().next_periodic_ms == 3550U);
}

IOTOX_TEST(
    "sync automation can delay republish after busy source changes") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    SyncAutomationStore store(temporary.path());

    auto publishing = store.put(
        publisher("publish", temporary.path() / "publish-tree"), device,
        crypto);
    IOTOX_CHECK(publishing.ok());

    SyncAutomationScheduler scheduler;
    IOTOX_CHECK(scheduler.replace({publishing.value().policy}, 1000U).ok());
    auto initial = scheduler.claim_periodic(1000U);
    IOTOX_CHECK(initial.size() == 1U);
    IOTOX_CHECK(initial.front().kind == SyncAutomationActionKind::publish);

    IOTOX_CHECK(scheduler.trigger_source_change("publish", 1010U, 250U,
                                                5000U).ok());
    auto busy = scheduler.snapshot();
    IOTOX_CHECK(busy.size() == 1U);
    IOTOX_CHECK(busy.front().source_publish_pending);

    IOTOX_CHECK(scheduler.complete(initial.front(), ErrorCode::ok,
                                   1020U).ok());
    IOTOX_CHECK(scheduler.claim_periodic(6019U).empty());
    auto delayed = scheduler.claim_periodic(6020U);
    IOTOX_CHECK(delayed.size() == 1U);
    IOTOX_CHECK(delayed.front().kind == SyncAutomationActionKind::publish);
    IOTOX_CHECK(scheduler.complete(delayed.front(), ErrorCode::ok,
                                   6020U).ok());

    auto done = scheduler.snapshot();
    IOTOX_CHECK(done.size() == 1U);
    IOTOX_CHECK(!done.front().source_publish_pending);
    IOTOX_CHECK(done.front().next_periodic_ms == 8020U);
}

IOTOX_TEST("sync automation reads v1 and migrates only on explicit mutation") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  SyncAutomationStore store(temporary.path());

  auto spec = writable("legacy", temporary.path() / "legacy-tree", 0x42U);
  auto initial = store.put(spec, device, crypto);
  IOTOX_CHECK(initial.ok());

  SyncAutomationPolicy legacy;
  static_cast<SyncAutomationSpec &>(legacy) = spec;
  legacy.record_format = 1U;
  legacy.generation = 1U;
  legacy.signer = device.public_key();
  auto unsigned_record = iotox::sync::encode_sync_automation_policy(legacy);
  IOTOX_CHECK(unsigned_record.ok());
  IOTOX_CHECK(unsigned_record.value().size() == 4328U);
  const auto body = std::span<const std::uint8_t>{unsigned_record.value()}.first(
      unsigned_record.value().size() - iotox::security::kSignatureBytes);
  auto digest = crypto.hash("iotox-sync-automation-policy-signature-v1", body);
  IOTOX_CHECK(digest.ok());
  auto signature = device.sign(digest.value());
  IOTOX_CHECK(signature.ok());
  legacy.signature = signature.value();
  auto legacy_record = iotox::sync::encode_sync_automation_policy(legacy);
  IOTOX_CHECK(legacy_record.ok());
  write_bytes(temporary.path() / "automation" / "legacy.automation",
              legacy_record.value());

  auto loaded = store.load(device.public_key(), crypto);
  IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
  IOTOX_CHECK(loaded.value().size() == 1U);
  IOTOX_CHECK(loaded.value().front().record_format == 1U);
  IOTOX_CHECK(loaded.value().front().source_principals ==
              spec.source_principals);

  auto duplicate = store.put(spec, device, crypto);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().decision ==
              SyncAutomationStoreDecision::duplicate);
  IOTOX_CHECK(duplicate.value().policy.record_format == 1U);

  iotox::sync::PrincipalId second{};
  second.fill(0x75U);
  spec.source_principals.push_back(second);
  auto migrated = store.put(spec, device, crypto);
  IOTOX_CHECK_MSG(migrated.ok(), migrated.status().message());
  IOTOX_CHECK(migrated.value().decision ==
              SyncAutomationStoreDecision::replaced);
  IOTOX_CHECK(migrated.value().policy.record_format == 2U);
  IOTOX_CHECK(migrated.value().policy.generation == 2U);
}
