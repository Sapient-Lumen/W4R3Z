#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/update_bundle.hpp"
#include "iotox/update_state.hpp"
#include "iotox/update_witness.hpp"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <memory>
#include <mutex>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace {

class TemporaryDirectory {
public:
  TemporaryDirectory() {
    path_ = std::filesystem::temp_directory_path() /
        ("iotox-update-witness-test-" + std::to_string(::getpid()) + "-" +
         std::to_string(
             std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directories(path_);
    std::filesystem::permissions(
        path_, std::filesystem::perms::owner_all,
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
    if (fail_next_query_) {
      fail_next_query_ = false;
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected update witness query loss"};
    }
    return record_;
  }

  iotox::Status compare_exchange(
      const iotox::rollback_witness::Record &expected,
      const iotox::rollback_witness::Record &desired) override {
    std::scoped_lock lock(mutex_);
    ++calls_;
    if (!(record_ == expected)) {
      return iotox::Status{iotox::ErrorCode::protocol_error,
                           "update witness CAS conflict"};
    }
    const iotox::Status valid =
        iotox::rollback_witness::validate_transition(expected, desired);
    if (!valid.ok()) return valid;
    record_ = desired;
    if (lose_reply_after_call_ == calls_) {
      fail_next_query_ = true;
      return iotox::Status{iotox::ErrorCode::unavailable,
                           "injected update witness lost reply"};
    }
    return iotox::Status::success();
  }

  bool independently_controlled() const noexcept override { return false; }

  void set(iotox::rollback_witness::Record record) {
    std::scoped_lock lock(mutex_);
    record_ = std::move(record);
  }

  void lose_reply_after(std::size_t call) {
    std::scoped_lock lock(mutex_);
    lose_reply_after_call_ = call;
  }

  [[nodiscard]] iotox::rollback_witness::Record current() const {
    std::scoped_lock lock(mutex_);
    return record_;
  }

private:
  mutable std::mutex mutex_;
  iotox::rollback_witness::Record record_;
  std::size_t calls_{0U};
  std::size_t lose_reply_after_call_{0U};
  bool fail_next_query_{false};
};

void private_directory(const std::filesystem::path &path) {
  std::filesystem::create_directory(path);
  if (::chmod(path.c_str(), 0700) != 0) {
    throw std::runtime_error("chmod private directory failed");
  }
}

void private_file(const std::filesystem::path &path, std::string_view bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  output.close();
  if (::chmod(path.c_str(), 0600) != 0) {
    throw std::runtime_error("chmod private file failed");
  }
}

struct Fixture {
  TemporaryDirectory temporary;
  iotox::security::Sodium sodium;
  iotox::security::DeviceIdentity device;
  iotox::security::DeviceIdentity release;
  iotox::update::UpdatePolicy policy;
  std::shared_ptr<MemoryBackend> backend;
  std::shared_ptr<iotox::update::LifecycleWitness> witness;
  std::filesystem::path bundle;

  Fixture()
      : sodium(iotox::security::Sodium::load().value()),
        device(iotox::security::DeviceIdentity::load_or_create(
                   temporary.path() / "device.identity", sodium, true).value()),
        release(iotox::security::DeviceIdentity::create_new_release(
                    temporary.path() / "release.identity", sodium).value()),
        backend(std::make_shared<MemoryBackend>()) {
    policy.namespace_id = "witnessed-system-image";
    policy.target = "iotox-test-x86_64";
    policy.root = temporary.path() / "update";
    policy.maximum_payload_bytes = 1024U * 1024U;
    policy.health_timeout_ms = 5000U;
    policy.trusted_signers = {release.public_key()};
    private_directory(policy.root);
    iotox::update::LifecycleWitness::Config config;
    config.backend = backend;
    config.domain[0U] = 0x81U;
    config.domain[15U] = 0x18U;
    config.witness_epoch = 4U;
    config.intent_path = temporary.path() / "update-lifecycle.intent";
    config.allow_non_independent_for_testing = true;
    witness = std::make_shared<iotox::update::LifecycleWitness>(
        std::move(config), policy, device, sodium);
    auto enrollment = witness->enrollment_record(std::nullopt);
    if (!enrollment.ok()) {
      throw std::runtime_error(enrollment.status().message());
    }
    backend->set(enrollment.value());
    const auto payload = temporary.path() / "payload.bin";
    bundle = temporary.path() / "release.iub";
    private_file(payload, "witnessed update payload\n");
    auto created = iotox::update::create_signed_update_bundle(
        policy, payload, bundle, 1U, "1.0.0", release, sodium);
    if (!created.ok()) throw std::runtime_error(created.status().message());
  }
};

} // namespace

IOTOX_TEST("update lifecycle witness rejects a complete local state rollback") {
  Fixture fixture;
  auto store = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 10U, fixture.witness);
  IOTOX_CHECK_MSG(store.ok(), store.status().message());
  auto staged = store.value()->stage(fixture.bundle);
  IOTOX_CHECK_MSG(staged.ok(), staged.status().message());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending.has_value());
  store.value().reset();

  IOTOX_CHECK(::unlink((fixture.policy.root / "state" /
                        "update.state").c_str()) == 0);
  auto replayed = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 11U, fixture.witness);
  IOTOX_CHECK(!replayed.ok());
  IOTOX_CHECK(replayed.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("update lifecycle witness recovers a committed CAS with lost reply") {
  Fixture fixture;
  auto store = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 20U, fixture.witness);
  IOTOX_CHECK(store.ok());
  fixture.backend->lose_reply_after(2U);
  auto staged = store.value()->stage(fixture.bundle);
  IOTOX_CHECK(!staged.ok());
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(std::filesystem::exists(
      fixture.temporary.path() / "update-lifecycle.intent"));
  store.value().reset();

  auto recovered = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 21U, fixture.witness);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value()->snapshot()->phase ==
              iotox::update::UpdatePhase::staged);
  IOTOX_CHECK(!std::filesystem::exists(
      fixture.temporary.path() / "update-lifecycle.intent"));
}

IOTOX_TEST("update lifecycle witness recovers a pending CAS with lost reply") {
  Fixture fixture;
  auto store = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 25U, fixture.witness);
  IOTOX_CHECK(store.ok());
  fixture.backend->lose_reply_after(1U);
  auto staged = store.value()->stage(fixture.bundle);
  IOTOX_CHECK(!staged.ok());
  IOTOX_CHECK(fixture.backend->current().committed.position == 1U);
  IOTOX_CHECK(fixture.backend->current().pending->position == 2U);
  IOTOX_CHECK(!std::filesystem::exists(
      fixture.policy.root / "state" / "update.state"));
  store.value().reset();

  auto recovered = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 26U, fixture.witness);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value()->snapshot()->phase ==
              iotox::update::UpdatePhase::staged);
  IOTOX_CHECK(fixture.backend->current().committed.position == 2U);
  IOTOX_CHECK(!fixture.backend->current().pending.has_value());
}

IOTOX_TEST("witnessed update repairs an interrupted apply pointer forward") {
  Fixture fixture;
  auto store = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 30U, fixture.witness);
  IOTOX_CHECK(store.ok());
  auto staged = store.value()->stage(fixture.bundle);
  IOTOX_CHECK(staged.ok());
  auto applied = store.value()->apply(
      staged.value().state.candidate.manifest_record, 30U);
  IOTOX_CHECK(applied.ok());
  IOTOX_CHECK(::unlink((fixture.policy.root / "current").c_str()) == 0);
  store.value().reset();

  auto recovered = iotox::update::UpdateStore::open(
      fixture.policy, fixture.device, fixture.sodium, 31U, fixture.witness);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value()->startup_result().disposition ==
              iotox::update::StartupDisposition::health_window_opened);
  IOTOX_CHECK(recovered.value()->snapshot()->phase ==
              iotox::update::UpdatePhase::awaiting_health);
  IOTOX_CHECK(fixture.backend->current().committed.position == 4U);
  IOTOX_CHECK(std::filesystem::exists(fixture.policy.root / "current"));
}
