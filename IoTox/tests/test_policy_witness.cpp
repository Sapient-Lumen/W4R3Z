#include "test_harness.hpp"

#include "iotox/policy_witness.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"

#include <chrono>
#include <filesystem>
#include <memory>
#include <mutex>
#include <string>
#include <system_error>
#include <unistd.h>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        path_ = std::filesystem::temp_directory_path() /
            ("iotox-policy-witness-test-" + std::to_string(::getpid()) + "-" +
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
    explicit MemoryBackend(iotox::rollback_witness::Record record)
        : record_(std::move(record)) {}

    iotox::Result<iotox::rollback_witness::Record> query() override {
        std::scoped_lock lock(mutex_);
        if (fail_queries_ > 0U) {
            --fail_queries_;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "injected policy witness query failure"};
        }
        return record_;
    }

    iotox::Status compare_exchange(
        const iotox::rollback_witness::Record &expected,
        const iotox::rollback_witness::Record &desired) override {
        std::scoped_lock lock(mutex_);
        ++calls_;
        if (fail_before_call_ == calls_) {
            fail_queries_ = 1U;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "injected policy witness CAS failure"};
        }
        if (!(record_ == expected)) {
            return iotox::Status{iotox::ErrorCode::protocol_error,
                                 "injected policy witness CAS conflict"};
        }
        const iotox::Status valid =
            iotox::rollback_witness::validate_transition(expected, desired);
        if (!valid.ok()) return valid;
        record_ = desired;
        return iotox::Status::success();
    }

    bool independently_controlled() const noexcept override { return false; }

    void fail_before(std::size_t call) {
        std::scoped_lock lock(mutex_);
        fail_before_call_ = call;
    }

    [[nodiscard]] iotox::rollback_witness::Record current() const {
        std::scoped_lock lock(mutex_);
        return record_;
    }

  private:
    mutable std::mutex mutex_;
    iotox::rollback_witness::Record record_;
    std::size_t calls_{0U};
    std::size_t fail_before_call_{0U};
    std::size_t fail_queries_{0U};
};

struct Fixture {
    TemporaryDirectory temporary;
    iotox::security::Sodium sodium;
    iotox::security::DeviceIdentity identity;
    std::filesystem::path checkpoint;
    std::filesystem::path intent;
    iotox::rollback_witness::DomainId domain{};

    Fixture()
        : sodium(iotox::security::Sodium::load().value()),
          identity(iotox::security::DeviceIdentity::load_or_create(
                       temporary.path() / "device.identity", sodium, true)
                       .value()),
          checkpoint(temporary.path() / "terminal-policy.checkpoint"),
          intent(temporary.path() / "terminal-policy.intent") {
        domain[0U] = 0x50U;
        domain[15U] = 0xa1U;
    }

    [[nodiscard]] iotox::security::Digest digest(std::string_view text) const {
        return sodium.hash(
            "iotox-test-policy-digest",
            std::span<const std::uint8_t>{
                reinterpret_cast<const std::uint8_t *>(text.data()),
                text.size()}).value();
    }

    [[nodiscard]] iotox::policy_witness::Config config(
        std::shared_ptr<MemoryBackend> backend) const {
        iotox::policy_witness::Config result;
        result.backend = std::move(backend);
        result.domain = domain;
        result.witness_epoch = 9U;
        result.lane = iotox::rollback_witness::Lane::terminal_policy;
        result.checkpoint_path = checkpoint;
        result.intent_path = intent;
        result.allow_non_independent_for_testing = true;
        return result;
    }
};

}  // namespace

IOTOX_TEST("policy witness requires explicit commit and rejects complete local rollback") {
    Fixture fixture;
    const auto original = fixture.digest("reviewed-terminal-policy-a");
    auto enrollment = iotox::policy_witness::enrollment_record(
        fixture.checkpoint, original, fixture.identity, fixture.sodium,
        fixture.domain, 9U,
        iotox::rollback_witness::Lane::terminal_policy);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    IOTOX_CHECK(enrollment.value().committed.position == 1U);
    auto backend = std::make_shared<MemoryBackend>(enrollment.value());
    const auto config = fixture.config(backend);

    auto verified = iotox::policy_witness::verify(
        config, original, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(verified.ok(), verified.status().message());
    IOTOX_CHECK(verified.value() == 1U);
    auto original_checkpoint = iotox::StateStore::read(fixture.checkpoint);
    IOTOX_CHECK(original_checkpoint.ok());

    const auto changed = fixture.digest("reviewed-terminal-policy-with-sudo");
    auto unreviewed = iotox::policy_witness::verify(
        config, changed, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!unreviewed.ok());
    IOTOX_CHECK(backend->current().committed.position == 1U);

    auto committed = iotox::policy_witness::commit(
        config, changed, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    IOTOX_CHECK(committed.value() == 2U);
    IOTOX_CHECK(backend->current().committed.digest == changed);

    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    fixture.checkpoint, original_checkpoint.value()).ok());
    auto rollback = iotox::policy_witness::verify(
        config, original, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!rollback.ok());
    IOTOX_CHECK(rollback.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(backend->current().committed.position == 2U);
}

IOTOX_TEST("policy witness recovers prepared and pending explicit commits") {
    Fixture fixture;
    const auto first = fixture.digest("policy-one");
    auto enrollment = iotox::policy_witness::enrollment_record(
        fixture.checkpoint, first, fixture.identity, fixture.sodium,
        fixture.domain, 9U,
        iotox::rollback_witness::Lane::terminal_policy);
    IOTOX_CHECK(enrollment.ok());
    auto backend = std::make_shared<MemoryBackend>(enrollment.value());
    const auto config = fixture.config(backend);
    IOTOX_CHECK(iotox::policy_witness::verify(
                    config, first, fixture.identity, fixture.sodium).ok());

    const auto second = fixture.digest("policy-two");
    backend->fail_before(1U);
    auto prepared = iotox::policy_witness::commit(
        config, second, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!prepared.ok());
    IOTOX_CHECK(std::filesystem::exists(fixture.intent));
    IOTOX_CHECK(!backend->current().pending);
    auto resumed = iotox::policy_witness::verify(
        config, second, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(resumed.ok(), resumed.status().message());
    IOTOX_CHECK(resumed.value() == 2U);
    IOTOX_CHECK(!std::filesystem::exists(fixture.intent));

    const auto third = fixture.digest("policy-three");
    backend->fail_before(5U);
    auto pending = iotox::policy_witness::commit(
        config, third, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!pending.ok());
    IOTOX_CHECK(backend->current().pending.has_value());
    resumed = iotox::policy_witness::verify(
        config, third, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(resumed.ok(), resumed.status().message());
    IOTOX_CHECK(resumed.value() == 3U);
    IOTOX_CHECK(!backend->current().pending);
}

IOTOX_TEST("policy witness refuses same-domain test backends outside tests") {
    Fixture fixture;
    const auto digest = fixture.digest("policy");
    auto enrollment = iotox::policy_witness::enrollment_record(
        fixture.checkpoint, digest, fixture.identity, fixture.sodium,
        fixture.domain, 9U,
        iotox::rollback_witness::Lane::terminal_policy);
    IOTOX_CHECK(enrollment.ok());
    auto backend = std::make_shared<MemoryBackend>(enrollment.value());
    auto config = fixture.config(backend);
    config.allow_non_independent_for_testing = false;
    auto refused = iotox::policy_witness::verify(
        config, digest, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::unsupported);
}
