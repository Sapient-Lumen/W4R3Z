#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/update_bundle.hpp"
#include "iotox/update_state.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::update::HealthToken;
using iotox::update::StartupDisposition;
using iotox::update::UpdatePhase;
using iotox::update::UpdatePolicy;
using iotox::update::UpdateRetentionMode;
using iotox::update::UpdateStore;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-update-state-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
    if (::chmod(path_.c_str(), 0700) != 0)
      throw std::runtime_error("chmod temp failed");
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

Sodium sodium() {
  auto loaded = Sodium::load();
  if (!loaded.ok()) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
  auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded.ok()) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

DeviceIdentity release_identity(const std::filesystem::path &path,
                                const Sodium &crypto) {
  auto loaded = DeviceIdentity::create_new_release(path, crypto);
  if (!loaded.ok()) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

void make_private_directory(const std::filesystem::path &path) {
  if (!std::filesystem::create_directory(path))
    throw std::runtime_error("create directory failed");
  if (::chmod(path.c_str(), 0700) != 0)
    throw std::runtime_error("chmod directory failed");
}

void write_private(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(text.data(), static_cast<std::streamsize>(text.size()));
  if (!output) throw std::runtime_error("write fixture failed");
  output.close();
  if (::chmod(path.c_str(), 0600) != 0)
    throw std::runtime_error("chmod fixture failed");
}

std::vector<std::uint8_t> read_all(const std::filesystem::path &path) {
  auto bytes = iotox::StateStore::read(path);
  if (!bytes.ok()) throw std::runtime_error(bytes.status().message());
  return std::move(bytes).value();
}

void write_all(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  const iotox::Status stored = iotox::StateStore::write_atomic(path, bytes);
  if (!stored.ok()) throw std::runtime_error(stored.message());
}

UpdatePolicy policy(const TempDirectory &temporary,
                    const DeviceIdentity &signer) {
  UpdatePolicy result;
  result.namespace_id = "system-image";
  result.target = "iotox-sandwurm-x86_64";
  result.root = temporary.path() / "update";
  result.maximum_payload_bytes = 1024U * 1024U;
  result.health_timeout_ms = 5000U;
  result.trusted_signers = {signer.public_key()};
  make_private_directory(result.root);
  return result;
}

std::filesystem::path bundle(
    const TempDirectory &temporary, const UpdatePolicy &configured,
    const DeviceIdentity &signer, const Sodium &crypto,
    std::uint64_t sequence, std::string_view payload) {
  const auto payload_path = temporary.path() /
      ("payload-" + std::to_string(sequence) + ".bin");
  const auto bundle_path = temporary.path() /
      ("release-" + std::to_string(sequence) + ".iub");
  write_private(payload_path, payload);
  auto created = iotox::update::create_signed_update_bundle(
      configured, payload_path, bundle_path, sequence,
      std::to_string(sequence) + ".0.0", signer, crypto);
  if (!created.ok()) throw std::runtime_error(created.status().message());
  return bundle_path;
}

std::filesystem::path current_target(const UpdatePolicy &configured) {
  std::error_code error;
  auto result = std::filesystem::read_symlink(
      configured.root / "current", error);
  if (error) throw std::runtime_error("read current pointer failed");
  return result;
}

} // namespace

IOTOX_TEST("update state survives restart confirmation and automatic rollback") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release1 = bundle(
      temporary, configured, signer, crypto, 1U, "slot payload one\n");
  const auto release2 = bundle(
      temporary, configured, signer, crypto, 2U, "slot payload two\n");
  const auto release3 = bundle(
      temporary, configured, signer, crypto, 3U, "slot payload three\n");

  auto first = UpdateStore::open(configured, device, crypto, 10U);
  IOTOX_CHECK(first.ok());
  IOTOX_CHECK(first.value()->startup_result().disposition ==
              StartupDisposition::empty);
  auto staged1 = first.value()->stage(release1);
  IOTOX_CHECK(staged1.ok());
  IOTOX_CHECK(staged1.value().state.phase == UpdatePhase::staged);
  auto duplicate1 = first.value()->stage(release1);
  IOTOX_CHECK(duplicate1.ok());
  IOTOX_CHECK(duplicate1.value().duplicate);
  auto applied1 = first.value()->apply(
      staged1.value().state.candidate.manifest_record, 10U);
  IOTOX_CHECK_MSG(applied1.ok(), applied1.status().message());
  IOTOX_CHECK(applied1.value().state.phase == UpdatePhase::pending_restart);
  IOTOX_CHECK(!first.value()->confirm(applied1.value().health_token, 10U).ok());
  const HealthToken token1 = applied1.value().health_token;
  first.value().reset();

  auto boot1 = UpdateStore::open(configured, device, crypto, 11U);
  IOTOX_CHECK(boot1.ok());
  IOTOX_CHECK(boot1.value()->startup_result().disposition ==
              StartupDisposition::health_window_opened);
  HealthToken wrong_token = token1;
  wrong_token[0U] ^= 1U;
  IOTOX_CHECK(!boot1.value()->confirm(wrong_token, 11U).ok());
  auto confirmed1 = boot1.value()->confirm(token1, 11U);
  IOTOX_CHECK(confirmed1.ok());
  IOTOX_CHECK(confirmed1.value().phase == UpdatePhase::confirmed);
  IOTOX_CHECK(confirmed1.value().confirmed.sequence == 1U);
  IOTOX_CHECK(!confirmed1.value().candidate.present());
  const auto confirmed1_target = current_target(configured);

  auto staged2 = boot1.value()->stage(release2);
  IOTOX_CHECK(staged2.ok());
  auto applied2 = boot1.value()->apply(
      staged2.value().state.candidate.manifest_record, 11U);
  IOTOX_CHECK(applied2.ok());
  boot1.value().reset();
  auto boot2 = UpdateStore::open(configured, device, crypto, 12U);
  IOTOX_CHECK(boot2.ok());
  IOTOX_CHECK(boot2.value()->startup_result().disposition ==
              StartupDisposition::health_window_opened);
  boot2.value().reset();

  auto rollback = UpdateStore::open(configured, device, crypto, 13U);
  IOTOX_CHECK(rollback.ok());
  IOTOX_CHECK(rollback.value()->startup_result().disposition ==
              StartupDisposition::unconfirmed_restart_rolled_back);
  auto rolled_state = rollback.value()->snapshot();
  IOTOX_CHECK(rolled_state.has_value());
  IOTOX_CHECK(rolled_state->phase == UpdatePhase::confirmed);
  IOTOX_CHECK(rolled_state->confirmed.sequence == 1U);
  IOTOX_CHECK(rolled_state->last_failed_sequence == 2U);
  IOTOX_CHECK(rolled_state->rollback_count == 1U);
  IOTOX_CHECK(current_target(configured) == confirmed1_target);

  auto staged3 = rollback.value()->stage(release3);
  IOTOX_CHECK(staged3.ok());
  auto applied3 = rollback.value()->apply(
      staged3.value().state.candidate.manifest_record, 13U);
  IOTOX_CHECK(applied3.ok());
  const HealthToken token3 = applied3.value().health_token;
  rollback.value().reset();
  auto boot3 = UpdateStore::open(configured, device, crypto, 14U);
  IOTOX_CHECK(boot3.ok());
  auto confirmed3 = boot3.value()->confirm(token3, 14U);
  IOTOX_CHECK(confirmed3.ok());
  IOTOX_CHECK(confirmed3.value().confirmed.sequence == 3U);
  IOTOX_CHECK(confirmed3.value().rollback_count == 1U);
  IOTOX_CHECK(current_target(configured).filename().string().starts_with("3-"));

  auto stale = boot3.value()->stage(release2);
  IOTOX_CHECK(!stale.ok());
  IOTOX_CHECK(stale.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("update health expiry rolls back the first candidate to empty") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release = bundle(
      temporary, configured, signer, crypto, 7U, "first candidate\n");

  auto initial = UpdateStore::open(configured, device, crypto, 20U);
  IOTOX_CHECK(initial.ok());
  auto staged = initial.value()->stage(release);
  IOTOX_CHECK(staged.ok());
  auto applied = initial.value()->apply(
      staged.value().state.candidate.manifest_record, 20U);
  IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
  initial.value().reset();
  auto boot = UpdateStore::open(configured, device, crypto, 21U);
  IOTOX_CHECK(boot.ok());
  auto expired = boot.value()->expire_health(21U);
  IOTOX_CHECK(expired.ok());
  IOTOX_CHECK(expired.value().phase == UpdatePhase::idle_after_rollback);
  IOTOX_CHECK(expired.value().rollback_count == 1U);
  IOTOX_CHECK(expired.value().last_failed_sequence == 7U);
  IOTOX_CHECK(!std::filesystem::exists(configured.root / "current"));
  IOTOX_CHECK(!boot.value()->confirm(applied.value().health_token, 21U).ok());

  boot.value().reset();
  auto restarted = UpdateStore::open(configured, device, crypto, 22U);
  IOTOX_CHECK(restarted.ok());
  IOTOX_CHECK(restarted.value()->startup_result().disposition ==
              StartupDisposition::unchanged);
}

IOTOX_TEST("update recovery rolls back a state-first interrupted apply") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release = bundle(
      temporary, configured, signer, crypto, 1U, "interrupted candidate\n");

  auto initial = UpdateStore::open(configured, device, crypto, 30U);
  IOTOX_CHECK(initial.ok());
  auto staged = initial.value()->stage(release);
  IOTOX_CHECK(staged.ok());
  auto applied = initial.value()->apply(
      staged.value().state.candidate.manifest_record, 30U);
  IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
  IOTOX_CHECK(::unlink((configured.root / "current").c_str()) == 0);
  initial.value().reset();

  auto recovered = UpdateStore::open(configured, device, crypto, 31U);
  IOTOX_CHECK(recovered.ok());
  IOTOX_CHECK(recovered.value()->startup_result().disposition ==
              StartupDisposition::incomplete_apply_rolled_back);
  auto state = recovered.value()->snapshot();
  IOTOX_CHECK(state.has_value());
  IOTOX_CHECK(state->phase == UpdatePhase::idle_after_rollback);
  IOTOX_CHECK(state->last_failed_sequence == 1U);
}

IOTOX_TEST("update recovery completes a pointer-first interrupted rollback") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release1 = bundle(
      temporary, configured, signer, crypto, 1U, "confirmed payload\n");
  const auto release2 = bundle(
      temporary, configured, signer, crypto, 2U, "failed payload\n");

  auto initial = UpdateStore::open(configured, device, crypto, 60U);
  IOTOX_CHECK(initial.ok());
  auto staged1 = initial.value()->stage(release1);
  IOTOX_CHECK(staged1.ok());
  auto applied1 = initial.value()->apply(
      staged1.value().state.candidate.manifest_record, 60U);
  IOTOX_CHECK(applied1.ok());
  initial.value().reset();
  auto boot1 = UpdateStore::open(configured, device, crypto, 61U);
  IOTOX_CHECK(boot1.ok());
  IOTOX_CHECK(boot1.value()->confirm(
                  applied1.value().health_token, 61U).ok());
  const auto confirmed_target = current_target(configured);

  auto staged2 = boot1.value()->stage(release2);
  IOTOX_CHECK(staged2.ok());
  auto applied2 = boot1.value()->apply(
      staged2.value().state.candidate.manifest_record, 61U);
  IOTOX_CHECK(applied2.ok());
  boot1.value().reset();
  auto boot2 = UpdateStore::open(configured, device, crypto, 62U);
  IOTOX_CHECK(boot2.ok());
  IOTOX_CHECK(boot2.value()->startup_result().disposition ==
              StartupDisposition::health_window_opened);

  // Model a crash after rollback changed the pointer but before it replaced
  // the signed awaiting-health state. Restart must finish the monotonic
  // rollback instead of treating this safe intermediate point as corruption.
  IOTOX_CHECK(::unlink((configured.root / "current").c_str()) == 0);
  IOTOX_CHECK(::symlink(confirmed_target.c_str(),
                        (configured.root / "current").c_str()) == 0);
  boot2.value().reset();
  auto recovered = UpdateStore::open(configured, device, crypto, 62U);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value()->startup_result().disposition ==
              StartupDisposition::unconfirmed_restart_rolled_back);
  auto state = recovered.value()->snapshot();
  IOTOX_CHECK(state.has_value());
  IOTOX_CHECK(state->phase == UpdatePhase::confirmed);
  IOTOX_CHECK(state->confirmed.sequence == 1U);
  IOTOX_CHECK(state->last_failed_sequence == 2U);
  IOTOX_CHECK(state->rollback_count == 1U);
  IOTOX_CHECK(current_target(configured) == confirmed_target);
}

IOTOX_TEST("update state survives abrupt stage and apply process exits") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release = bundle(
      temporary, configured, signer, crypto, 5U, "abrupt process payload\n");

  pid_t child = ::fork();
  IOTOX_CHECK(child >= 0);
  if (child == 0) {
    auto store = UpdateStore::open(configured, device, crypto, 50U);
    if (!store.ok()) ::_exit(10);
    auto staged = store.value()->stage(release);
    ::_exit(staged.ok() ? 0 : 11);
  }
  int child_status = 0;
  IOTOX_CHECK(::waitpid(child, &child_status, 0) == child);
  IOTOX_CHECK(WIFEXITED(child_status));
  IOTOX_CHECK(WEXITSTATUS(child_status) == 0);

  auto after_stage = UpdateStore::open(configured, device, crypto, 51U);
  IOTOX_CHECK_MSG(after_stage.ok(), after_stage.status().message());
  auto staged_state = after_stage.value()->snapshot();
  IOTOX_CHECK(staged_state.has_value());
  IOTOX_CHECK(staged_state->phase == UpdatePhase::staged);
  const auto manifest_record = staged_state->candidate.manifest_record;
  after_stage.value().reset();

  child = ::fork();
  IOTOX_CHECK(child >= 0);
  if (child == 0) {
    auto store = UpdateStore::open(configured, device, crypto, 52U);
    if (!store.ok()) ::_exit(12);
    auto applied = store.value()->apply(manifest_record, 52U);
    ::_exit(applied.ok() ? 0 : 13);
  }
  child_status = 0;
  IOTOX_CHECK(::waitpid(child, &child_status, 0) == child);
  IOTOX_CHECK(WIFEXITED(child_status));
  IOTOX_CHECK(WEXITSTATUS(child_status) == 0);

  auto after_apply = UpdateStore::open(configured, device, crypto, 53U);
  IOTOX_CHECK_MSG(after_apply.ok(), after_apply.status().message());
  IOTOX_CHECK(after_apply.value()->startup_result().disposition ==
              StartupDisposition::health_window_opened);
  auto applied_state = after_apply.value()->snapshot();
  IOTOX_CHECK(applied_state.has_value());
  IOTOX_CHECK(applied_state->phase == UpdatePhase::awaiting_health);
  IOTOX_CHECK(applied_state->candidate.sequence == 5U);
  IOTOX_CHECK(current_target(configured).filename().string().starts_with("5-"));
}

IOTOX_TEST("signed update state and slots fail closed on tampering") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  DeviceIdentity foreign =
      identity(temporary.path() / "foreign.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto release = bundle(
      temporary, configured, signer, crypto, 9U, "tamper target\n");

  auto store = UpdateStore::open(configured, device, crypto, 40U);
  IOTOX_CHECK(store.ok());
  auto staged = store.value()->stage(release);
  IOTOX_CHECK(staged.ok());
  auto encoded = iotox::update::encode_signed_update_state(staged.value().state);
  IOTOX_CHECK(encoded.ok());
  auto decoded = iotox::update::decode_signed_update_state(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == staged.value().state);
  IOTOX_CHECK(iotox::update::verify_signed_update_state(
                  configured, decoded.value(), device.public_key(), crypto)
                  .ok());
  IOTOX_CHECK(!iotox::update::verify_signed_update_state(
                   configured, decoded.value(), foreign.public_key(), crypto)
                   .ok());
  store.value().reset();

  const auto state_path = configured.root / "state" / "update.state";
  auto state_bytes = read_all(state_path);
  state_bytes.back() ^= 1U;
  write_all(state_path, state_bytes);
  auto corrupt_state = UpdateStore::open(configured, device, crypto, 41U);
  IOTOX_CHECK(!corrupt_state.ok());

  write_all(state_path, std::vector<std::uint8_t>(
                            encoded.value().begin(), encoded.value().end()));
  IOTOX_CHECK(::chmod(staged.value().slot_path.c_str(), 0600) == 0);
  auto corrupt_slot = UpdateStore::open(configured, device, crypto, 41U);
  IOTOX_CHECK(!corrupt_slot.ok());
}

IOTOX_TEST("live update staging refuses a ninth retained slot") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);

  std::uint64_t incarnation = 100U;
  auto store = UpdateStore::open(configured, device, crypto, incarnation);
  IOTOX_CHECK(store.ok());
  for (std::uint64_t sequence = 1U; sequence <= 8U; ++sequence) {
    const auto release = bundle(
        temporary, configured, signer, crypto, sequence,
        "retained slot " + std::to_string(sequence) + "\n");
    auto staged = store.value()->stage(release);
    IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
    auto applied = store.value()->apply(
        staged.value().state.candidate.manifest_record, incarnation);
    IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
    const HealthToken token = applied.value().health_token;
    store.value().reset();
    ++incarnation;
    store = UpdateStore::open(configured, device, crypto, incarnation);
    IOTOX_CHECK_MSG(store.ok(), store.status().message());
    auto confirmed = store.value()->confirm(token, incarnation);
    IOTOX_CHECK_MSG(confirmed.ok(), confirmed.status().message());
    IOTOX_CHECK(confirmed.value().confirmed.sequence == sequence);
  }

  const auto ninth = bundle(
      temporary, configured, signer, crypto, 9U, "refused ninth slot\n");
  auto refused = store.value()->stage(ninth);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() ==
              iotox::ErrorCode::resource_exhausted);
  auto state = store.value()->snapshot();
  IOTOX_CHECK(state.has_value());
  IOTOX_CHECK(state->phase == UpdatePhase::confirmed);
  IOTOX_CHECK(state->confirmed.sequence == 8U);
  IOTOX_CHECK(!state->candidate.present());

  auto planned = store.value()->retain_slots(UpdateRetentionMode::dry_run);
  IOTOX_CHECK_MSG(planned.ok(), planned.status().message());
  IOTOX_CHECK(planned.value().active_slots == 8U);
  IOTOX_CHECK(planned.value().protected_slots == 1U);
  IOTOX_CHECK(planned.value().eligible_slots == 7U);
  IOTOX_CHECK(planned.value().quarantined_slots == 0U);
  IOTOX_CHECK(planned.value().prior_quarantine_slots == 0U);
  auto quarantined_result =
      store.value()->retain_slots(UpdateRetentionMode::quarantine);
  IOTOX_CHECK_MSG(quarantined_result.ok(),
                  quarantined_result.status().message());
  IOTOX_CHECK(quarantined_result.value().eligible_slots == 7U);
  IOTOX_CHECK(quarantined_result.value().quarantined_slots == 7U);
  IOTOX_CHECK(quarantined_result.value().eligible_bytes ==
              quarantined_result.value().quarantined_bytes);

  std::size_t active_count = 0U;
  for (const auto &entry :
       std::filesystem::directory_iterator(configured.root / "slots")) {
    IOTOX_CHECK(entry.is_regular_file());
    ++active_count;
  }
  IOTOX_CHECK(active_count == 1U);
  std::size_t quarantined = 0U;
  for (const auto &entry : std::filesystem::directory_iterator(
           configured.root / "quarantine")) {
    IOTOX_CHECK(entry.is_regular_file());
    ++quarantined;
  }
  IOTOX_CHECK(quarantined == 7U);
  auto admitted_ninth = store.value()->stage(ninth);
  IOTOX_CHECK_MSG(admitted_ninth.ok(),
                  admitted_ninth.status().message());
  IOTOX_CHECK(admitted_ninth.value().state.confirmed.sequence == 8U);
  IOTOX_CHECK(admitted_ninth.value().state.candidate.sequence == 9U);
  store.value().reset();
  auto restarted =
      UpdateStore::open(configured, device, crypto, incarnation + 1U);
  IOTOX_CHECK_MSG(restarted.ok(), restarted.status().message());
  IOTOX_CHECK(restarted.value()->snapshot()->confirmed.sequence == 8U);
  IOTOX_CHECK(restarted.value()->snapshot()->candidate.sequence == 9U);
}

IOTOX_TEST("update retention resumes safely after a partial quarantine") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);

  std::vector<std::filesystem::path> slots;
  std::uint64_t incarnation = 300U;
  auto store = UpdateStore::open(configured, device, crypto, incarnation);
  IOTOX_CHECK(store.ok());
  for (std::uint64_t sequence = 1U; sequence <= 3U; ++sequence) {
    const auto release = bundle(
        temporary, configured, signer, crypto, sequence,
        "partial quarantine slot " + std::to_string(sequence) + "\n");
    auto staged = store.value()->stage(release);
    IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
    slots.push_back(staged.value().slot_path);
    auto applied = store.value()->apply(
        staged.value().state.candidate.manifest_record, incarnation);
    IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
    const HealthToken token = applied.value().health_token;
    store.value().reset();
    ++incarnation;
    store = UpdateStore::open(configured, device, crypto, incarnation);
    IOTOX_CHECK_MSG(store.ok(), store.status().message());
    IOTOX_CHECK(store.value()->confirm(token, incarnation).ok());
  }
  const std::uint64_t generation = store.value()->snapshot()->generation;
  const auto interrupted_destination = configured.root / "quarantine" /
      (slots.front().filename().string() + ".q." +
       std::to_string(generation));
  IOTOX_CHECK(::rename(slots.front().c_str(),
                       interrupted_destination.c_str()) == 0);
  store.value().reset();

  auto recovered =
      UpdateStore::open(configured, device, crypto, incarnation + 1U);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  auto plan =
      recovered.value()->retain_slots(UpdateRetentionMode::dry_run);
  IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
  IOTOX_CHECK(plan.value().active_slots == 2U);
  IOTOX_CHECK(plan.value().protected_slots == 1U);
  IOTOX_CHECK(plan.value().eligible_slots == 1U);
  IOTOX_CHECK(plan.value().prior_quarantine_slots == 1U);
  auto finished =
      recovered.value()->retain_slots(UpdateRetentionMode::quarantine);
  IOTOX_CHECK_MSG(finished.ok(), finished.status().message());
  IOTOX_CHECK(finished.value().quarantined_slots == 1U);
  IOTOX_CHECK(finished.value().prior_quarantine_slots == 1U);
  IOTOX_CHECK(current_target(configured).filename().string().starts_with(
      "3-"));

  recovered.value().reset();
  write_private(configured.root / "quarantine" / "surprise", "unsafe\n");
  IOTOX_CHECK(!UpdateStore::open(
                   configured, device, crypto, incarnation + 2U).ok());
}

IOTOX_TEST("update state binds linux service kind against reinterpretation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  configured.signer_policy_epoch = 1U;
  configured.payload_kind =
      iotox::update::PayloadKind::linux_service_v1;
  const auto release = bundle(
      temporary, configured, signer, crypto, 1U,
      "native service image fixture");
  auto store = UpdateStore::open(configured, device, crypto, 40U);
  IOTOX_CHECK_MSG(store.ok(), store.status().message());
  auto staged = store.value()->stage(release);
  IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
  IOTOX_CHECK(
      staged.value().state.candidate.payload_kind ==
      iotox::update::PayloadKind::linux_service_v1);
  iotox::update::UpdateState noncanonical_absent =
      staged.value().state;
  noncanonical_absent.confirmed.payload_kind =
      iotox::update::PayloadKind::linux_service_v1;
  IOTOX_CHECK(!iotox::update::encode_update_state_body(
                   noncanonical_absent).ok());
  IOTOX_CHECK(!store.value()->selected_slot().value().has_value());
  auto applied = store.value()->apply(
      staged.value().state.candidate.manifest_record, 40U);
  IOTOX_CHECK_MSG(applied.ok(), applied.status().message());
  auto selected = store.value()->selected_slot();
  IOTOX_CHECK_MSG(selected.ok(), selected.status().message());
  IOTOX_CHECK(selected.value().has_value());
  IOTOX_CHECK(selected.value()->candidate);
  IOTOX_CHECK(
      selected.value()->revision.payload_kind ==
      iotox::update::PayloadKind::linux_service_v1);
  store.value().reset();

  UpdatePolicy reinterpreted = configured;
  reinterpreted.payload_kind =
      iotox::update::PayloadKind::opaque_slot_v1;
  IOTOX_CHECK(!UpdateStore::open(
                   reinterpreted, device, crypto, 41U).ok());
  auto restarted = UpdateStore::open(
      configured, device, crypto, 41U);
  IOTOX_CHECK_MSG(restarted.ok(), restarted.status().message());
  IOTOX_CHECK(
      restarted.value()->snapshot()->candidate.payload_kind ==
      iotox::update::PayloadKind::linux_service_v1);
}

IOTOX_TEST("update store refuses unsafe root and ambiguous entries") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "release.identity", crypto);
  DeviceIdentity device =
      identity(temporary.path() / "device.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  IOTOX_CHECK(::chmod(configured.root.c_str(), 0755) == 0);
  IOTOX_CHECK(!UpdateStore::open(configured, device, crypto, 1U).ok());
  IOTOX_CHECK(::chmod(configured.root.c_str(), 0700) == 0);
  write_private(configured.root / "surprise", "ambiguous");
  IOTOX_CHECK(!UpdateStore::open(configured, device, crypto, 1U).ok());
}
