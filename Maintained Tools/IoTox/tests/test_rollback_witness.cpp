#include "test_harness.hpp"

#include "iotox/rollback_witness.hpp"
#include "iotox/security/authority.hpp"

#include <chrono>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <memory>
#include <mutex>
#include <span>
#include <string>
#include <system_error>
#include <thread>
#include <unistd.h>

namespace {

class MemoryWitness final : public iotox::rollback_witness::Backend {
  public:
    explicit MemoryWitness(iotox::rollback_witness::Record record,
                           bool independent = false)
        : record_(std::move(record)), independent_(independent) {}

    iotox::Result<iotox::rollback_witness::Record> query() override {
        std::scoped_lock lock(mutex_);
        if (unavailable_ || unavailable_queries_ > 0U) {
            if (unavailable_queries_ > 0U) --unavailable_queries_;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test witness unavailable"};
        }
        return record_;
    }

    iotox::Status compare_exchange(
        const iotox::rollback_witness::Record &expected,
        const iotox::rollback_witness::Record &desired) override {
        std::scoped_lock lock(mutex_);
        ++cas_calls_;
        if (unavailable_) {
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test witness CAS unavailable"};
        }
        if (fail_before_cas_call_ == cas_calls_) {
            unavailable_queries_ = 1U;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test witness failed before CAS"};
        }
        if (!(record_ == expected)) {
            return iotox::Status{iotox::ErrorCode::protocol_error,
                                 "test witness CAS conflict"};
        }
        record_ = desired;
        if (lose_reply_cas_call_ == cas_calls_) {
            lose_reply_cas_call_ = 0U;
            unavailable_queries_ = 1U;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "test witness lost CAS reply"};
        }
        return iotox::Status::success();
    }

    bool independently_controlled() const noexcept override {
        return independent_;
    }
    void unavailable(bool value) {
        std::scoped_lock lock(mutex_);
        unavailable_ = value;
    }
    void lose_next_cas_reply() {
        std::scoped_lock lock(mutex_);
        lose_reply_cas_call_ = cas_calls_ + 1U;
    }
    void lose_cas_reply_after(std::size_t successful_calls) {
        std::scoped_lock lock(mutex_);
        lose_reply_cas_call_ = cas_calls_ + successful_calls + 1U;
    }
    void fail_cas_before_apply_after(std::size_t successful_calls) {
        std::scoped_lock lock(mutex_);
        fail_before_cas_call_ = cas_calls_ + successful_calls + 1U;
    }

  private:
    mutable std::mutex mutex_;
    iotox::rollback_witness::Record record_;
    bool independent_{false};
    bool unavailable_{false};
    std::size_t cas_calls_{0U};
    std::size_t lose_reply_cas_call_{0U};
    std::size_t fail_before_cas_call_{0U};
    std::size_t unavailable_queries_{0U};
};

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        const auto ticks =
            std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
            ("iotox-witness-test-" + std::to_string(::getpid()) + "-" +
             std::to_string(ticks));
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

iotox::rollback_witness::Record initial_record() {
    iotox::rollback_witness::Record record;
    record.domain[0] = 1U;
    record.device[0] = 2U;
    record.witness_epoch = 1U;
    return record;
}

iotox::security::AuthorityRecordBytes prepare_bootstrap(
    iotox::security::AuthorityLedger &ledger,
    const iotox::security::SigningKeyPair &owner,
    const iotox::security::Sodium &sodium) {
    iotox::security::AuthorityPrepareRequest request;
    request.action = iotox::security::AuthorityAction::bootstrap;
    request.role = iotox::security::PrincipalRole::owner;
    request.capabilities = iotox::security::kAllCapabilities;
    request.issuer = owner.public_key();
    request.subject = owner.public_key();
    auto body = ledger.prepare(request);
    IOTOX_CHECK(body.ok());
    auto record = iotox::security::sign_authority_record_body(
        body.value(), owner.secret_key(), sodium);
    IOTOX_CHECK(record.ok());
    return record.value();
}

iotox::security::AuthorityLedger::Config witnessed_config(
    const std::filesystem::path &path,
    const std::shared_ptr<MemoryWitness> &backend,
    const iotox::rollback_witness::DomainId &domain) {
    iotox::security::AuthorityLedger::Config config;
    config.path = path;
    config.rollback_witness = backend;
    config.rollback_witness_domain = domain;
    config.rollback_witness_epoch = 1U;
    config.allow_non_independent_witness_for_testing = true;
    return config;
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    IOTOX_CHECK(input.good());
    return std::vector<std::uint8_t>{
        std::istreambuf_iterator<char>{input},
        std::istreambuf_iterator<char>{}};
}

void write_private(const std::filesystem::path &path,
                   std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    IOTOX_CHECK(output.good());
    output.write(reinterpret_cast<const char *>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    IOTOX_CHECK(output.good());
    std::filesystem::permissions(
        path,
        std::filesystem::perms::owner_read |
            std::filesystem::perms::owner_write,
        std::filesystem::perm_options::replace);
}

}  // namespace

IOTOX_TEST("rollback witness accepts only exact one-step pending commit") {
    auto record = initial_record();
    IOTOX_CHECK(iotox::rollback_witness::validate(record).ok());
    iotox::rollback_witness::Head next;
    next.position = 1U;
    next.digest[0] = 3U;
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0] = 4U;
    auto pending = iotox::rollback_witness::begin(record, next, nonce);
    IOTOX_CHECK(pending.ok());
    IOTOX_CHECK(pending.value().pending == next);
    auto committed = iotox::rollback_witness::finish(pending.value());
    IOTOX_CHECK(committed.ok());
    IOTOX_CHECK(committed.value().committed == next);
    IOTOX_CHECK(!committed.value().pending);

    auto skipped = next;
    skipped.position = 2U;
    IOTOX_CHECK(!iotox::rollback_witness::begin(record, skipped, nonce).ok());
    auto incomplete = record;
    incomplete.committed.position = 1U;
    IOTOX_CHECK(!iotox::rollback_witness::validate(incomplete).ok());
    auto unknown_lane = record;
    unknown_lane.lane =
        static_cast<iotox::rollback_witness::Lane>(0xffU);
    IOTOX_CHECK(!iotox::rollback_witness::validate(unknown_lane).ok());
    nonce = {};
    IOTOX_CHECK(!iotox::rollback_witness::begin(record, next, nonce).ok());
}

IOTOX_TEST("rollback witness exact CAS elects one concurrent clone") {
    auto initial = initial_record();
    iotox::rollback_witness::Head next;
    next.position = 1U;
    next.digest[0] = 9U;
    iotox::rollback_witness::TransactionNonce first_nonce{};
    first_nonce[0] = 1U;
    iotox::rollback_witness::TransactionNonce second_nonce{};
    second_nonce[0] = 2U;
    auto first = iotox::rollback_witness::begin(initial, next, first_nonce);
    auto second = iotox::rollback_witness::begin(initial, next, second_nonce);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(second.ok());
    MemoryWitness backend(initial);
    std::atomic<unsigned int> winners{0U};
    std::atomic<unsigned int> conflicts{0U};
    std::jthread first_clone([&] {
        const auto result = backend.compare_exchange(initial, first.value());
        if (result.ok()) ++winners;
        else if (result.code() == iotox::ErrorCode::protocol_error) ++conflicts;
    });
    std::jthread second_clone([&] {
        const auto result = backend.compare_exchange(initial, second.value());
        if (result.ok()) ++winners;
        else if (result.code() == iotox::ErrorCode::protocol_error) ++conflicts;
    });
    first_clone.join();
    second_clone.join();
    IOTOX_CHECK(winners.load() == 1U);
    IOTOX_CHECK(conflicts.load() == 1U);
    auto observed = backend.query();
    IOTOX_CHECK(observed.ok());
    IOTOX_CHECK(observed.value() == first.value() ||
                observed.value() == second.value());
    IOTOX_CHECK(!backend.independently_controlled());

    backend.unavailable(true);
    IOTOX_CHECK(!backend.query().ok());
    IOTOX_CHECK(!backend.compare_exchange(observed.value(), initial).ok());
}

IOTOX_TEST("authority witness commits exact signed mutation and rejects whole-state rollback") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 11U;
    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 12U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    TemporaryDirectory directory;

    auto witness_record = initial_record();
    witness_record.domain[0] = 21U;
    witness_record.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(witness_record, true);
    const auto ledger_path = directory.path() / "authority.ledger";
    auto config = witnessed_config(
        ledger_path, backend, witness_record.domain);
    config.allow_non_independent_witness_for_testing = false;
    auto ledger = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(ledger.ok(), ledger.status().message());
    const auto bootstrap = prepare_bootstrap(
        *ledger.value(), owner.value(), sodium.value());
    const iotox::Status appended = ledger.value()->append(bootstrap);
    IOTOX_CHECK_MSG(appended.ok(), appended.message());
    auto advanced = backend->query();
    IOTOX_CHECK(advanced.ok());
    IOTOX_CHECK(advanced.value().committed.position == 1U);
    IOTOX_CHECK(!advanced.value().pending);
    auto intent_path = ledger_path;
    intent_path += ".witness-intent";
    IOTOX_CHECK(!std::filesystem::exists(intent_path));

    ledger.value().reset();
    std::filesystem::remove(ledger_path);
    auto guard_path = ledger_path;
    guard_path += ".guard";
    std::filesystem::remove(guard_path);
    auto rolled_back = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!rolled_back.ok());
    IOTOX_CHECK(rolled_back.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("authority witness recovers a committed pending CAS with lost reply") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 31U;
    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 32U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    TemporaryDirectory directory;

    auto witness_record = initial_record();
    witness_record.domain[0] = 41U;
    witness_record.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(witness_record);
    const auto ledger_path = directory.path() / "authority.ledger";
    auto config = witnessed_config(
        ledger_path, backend, witness_record.domain);
    auto ledger = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());
    const auto bootstrap = prepare_bootstrap(
        *ledger.value(), owner.value(), sodium.value());
    backend->lose_next_cas_reply();
    const iotox::Status interrupted = ledger.value()->append(bootstrap);
    IOTOX_CHECK(!interrupted.ok());
    ledger.value().reset();

    auto recovered = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value()->snapshot().record_count == 1U);
    IOTOX_CHECK(recovered.value()->snapshot().tail_digest ==
                backend->query().value().committed.digest);
    IOTOX_CHECK(!backend->query().value().pending);
    auto intent_path = ledger_path;
    intent_path += ".witness-intent";
    IOTOX_CHECK(!std::filesystem::exists(intent_path));
}

IOTOX_TEST("authority witness refuses a same-domain backend without the test exception") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 51U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    IOTOX_CHECK(device.ok());
    TemporaryDirectory directory;

    auto witness_record = initial_record();
    witness_record.domain[0] = 52U;
    witness_record.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(witness_record);
    auto config = witnessed_config(
        directory.path() / "authority.ledger", backend,
        witness_record.domain);
    config.allow_non_independent_witness_for_testing = false;
    auto refused = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("authority witness refuses a pending transition without exact durable intent") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 61U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    IOTOX_CHECK(device.ok());
    TemporaryDirectory directory;

    auto initial = initial_record();
    initial.domain[0] = 62U;
    initial.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(initial);
    iotox::rollback_witness::Head next;
    next.position = 1U;
    next.digest[0] = 63U;
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0] = 64U;
    auto pending = iotox::rollback_witness::begin(initial, next, nonce);
    IOTOX_CHECK(pending.ok());
    IOTOX_CHECK(backend->compare_exchange(initial, pending.value()).ok());

    const auto config = witnessed_config(
        directory.path() / "authority.ledger", backend, initial.domain);
    auto refused = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("authority witness recovers committed final CAS after its reply is lost") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 71U;
    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 72U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    TemporaryDirectory directory;

    auto initial = initial_record();
    initial.domain[0] = 73U;
    initial.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(initial);
    const auto ledger_path = directory.path() / "authority.ledger";
    const auto config = witnessed_config(ledger_path, backend, initial.domain);
    auto ledger = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());
    const auto bootstrap = prepare_bootstrap(
        *ledger.value(), owner.value(), sodium.value());
    backend->lose_cas_reply_after(1U);
    const auto interrupted = ledger.value()->append(bootstrap);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(backend->query().value().committed.position == 1U);
    ledger.value().reset();

    auto recovered = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value()->snapshot().record_count == 1U);
    auto intent_path = ledger_path;
    intent_path += ".witness-intent";
    IOTOX_CHECK(!std::filesystem::exists(intent_path));
}

IOTOX_TEST("authority witness completes pending transition when local ledger is already new") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 81U;
    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 82U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    TemporaryDirectory directory;

    auto initial = initial_record();
    initial.domain[0] = 83U;
    initial.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(initial);
    const auto ledger_path = directory.path() / "authority.ledger";
    const auto config = witnessed_config(ledger_path, backend, initial.domain);
    auto ledger = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());
    const auto bootstrap = prepare_bootstrap(
        *ledger.value(), owner.value(), sodium.value());
    backend->fail_cas_before_apply_after(1U);
    const auto interrupted = ledger.value()->append(bootstrap);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(ledger.value()->snapshot().record_count == 1U);
    auto pending = backend->query();
    IOTOX_CHECK(pending.ok() && pending.value().pending.has_value());
    ledger.value().reset();

    auto recovered = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value()->snapshot().record_count == 1U);
    IOTOX_CHECK(!backend->query().value().pending.has_value());
}

IOTOX_TEST("authority witness discards intent when initial CAS never applied") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK(sodium.ok());
    iotox::security::SigningSeed device_seed{};
    device_seed[0] = 91U;
    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 92U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(device.ok() && owner.ok());
    TemporaryDirectory directory;

    auto initial = initial_record();
    initial.domain[0] = 93U;
    initial.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(initial);
    const auto ledger_path = directory.path() / "authority.ledger";
    const auto config = witnessed_config(ledger_path, backend, initial.domain);
    auto ledger = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());
    const auto bootstrap = prepare_bootstrap(
        *ledger.value(), owner.value(), sodium.value());
    backend->fail_cas_before_apply_after(0U);
    const auto interrupted = ledger.value()->append(bootstrap);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(ledger.value()->snapshot().record_count == 0U);
    IOTOX_CHECK(backend->query().value().committed.position == 0U);
    ledger.value().reset();

    auto recovered = iotox::security::AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value()->snapshot().record_count == 0U);
    auto intent_path = ledger_path;
    intent_path += ".witness-intent";
    IOTOX_CHECK(!std::filesystem::exists(intent_path));
}

IOTOX_TEST("authority witness rejects a disk snapshot taken before principal revocation") {
    using namespace iotox::security;
    auto sodium = Sodium::load();
    IOTOX_CHECK(sodium.ok());
    SigningSeed device_seed{};
    device_seed[0] = 101U;
    SigningSeed owner_seed{};
    owner_seed[0] = 102U;
    SigningSeed operator_seed{};
    operator_seed[0] = 103U;
    auto device = sodium.value().signing_keypair_from_seed(device_seed);
    auto owner = sodium.value().signing_keypair_from_seed(owner_seed);
    auto operator_keys = sodium.value().signing_keypair_from_seed(operator_seed);
    IOTOX_CHECK(device.ok() && owner.ok() && operator_keys.ok());
    TemporaryDirectory directory;

    auto initial = initial_record();
    initial.domain[0] = 104U;
    initial.device = device.value().public_key();
    auto backend = std::make_shared<MemoryWitness>(initial);
    const auto ledger_path = directory.path() / "authority.ledger";
    const auto config = witnessed_config(ledger_path, backend, initial.domain);
    auto ledger = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(ledger.ok());
    IOTOX_CHECK(ledger.value()->append(
        prepare_bootstrap(*ledger.value(), owner.value(), sodium.value())).ok());

    AuthorityPrepareRequest grant;
    grant.action = AuthorityAction::grant;
    grant.role = PrincipalRole::operator_role;
    grant.capabilities = static_cast<std::uint64_t>(Capability::actuate);
    grant.issuer = owner.value().public_key();
    grant.subject = operator_keys.value().public_key();
    auto grant_body = ledger.value()->prepare(grant);
    IOTOX_CHECK(grant_body.ok());
    auto grant_record = sign_authority_record_body(
        grant_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(grant_record.ok());
    IOTOX_CHECK(ledger.value()->append(grant_record.value()).ok());
    IOTOX_CHECK(ledger.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::actuate)));

    auto guard_path = ledger_path;
    guard_path += ".guard";
    const auto old_ledger = read_bytes(ledger_path);
    const auto old_guard = read_bytes(guard_path);

    AuthorityPrepareRequest revoke;
    revoke.action = AuthorityAction::revoke;
    revoke.role = PrincipalRole::none;
    revoke.issuer = owner.value().public_key();
    revoke.subject = operator_keys.value().public_key();
    auto revoke_body = ledger.value()->prepare(revoke);
    IOTOX_CHECK(revoke_body.ok());
    auto revoke_record = sign_authority_record_body(
        revoke_body.value(), owner.value().secret_key(), sodium.value());
    IOTOX_CHECK(revoke_record.ok());
    IOTOX_CHECK(ledger.value()->append(revoke_record.value()).ok());
    IOTOX_CHECK(!ledger.value()->authorized(
        operator_keys.value().public_key(),
        static_cast<std::uint64_t>(Capability::actuate)));
    IOTOX_CHECK(backend->query().value().committed.position == 3U);
    ledger.value().reset();

    write_private(ledger_path, old_ledger);
    write_private(guard_path, old_guard);
    auto restored = AuthorityLedger::open(
        config, device.value().public_key(), sodium.value());
    IOTOX_CHECK(!restored.ok());
    IOTOX_CHECK(restored.status().code() == iotox::ErrorCode::protocol_error);
}
