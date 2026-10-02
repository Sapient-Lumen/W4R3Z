#include "iotox/route_store.hpp"

#include "iotox/state_store.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <filesystem>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>

namespace {

using namespace iotox;

security::SigningSeed signing_seed(std::uint8_t value) {
    security::SigningSeed result{};
    result.fill(value);
    return result;
}

routes::ToxPublicKey route_key(std::uint8_t value) {
    routes::ToxPublicKey result{};
    result.fill(value);
    return result;
}

class MemoryRouteWitness final : public rollback_witness::Backend {
  public:
    explicit MemoryRouteWitness(rollback_witness::Record record)
        : record_(std::move(record)) {}

    Result<rollback_witness::Record> query() override {
        std::scoped_lock lock(mutex_);
        if (unavailable_queries_ > 0U) {
            --unavailable_queries_;
            return Status{ErrorCode::unavailable,
                          "injected route witness query failure"};
        }
        return record_;
    }

    Status compare_exchange(const rollback_witness::Record &expected,
                            const rollback_witness::Record &desired) override {
        std::scoped_lock lock(mutex_);
        ++cas_calls_;
        if (fail_before_cas_call_ == cas_calls_) {
            unavailable_queries_ = 1U;
            return Status{ErrorCode::unavailable,
                          "injected route witness CAS failure"};
        }
        if (!(record_ == expected)) {
            return Status{ErrorCode::protocol_error,
                          "injected route witness CAS conflict"};
        }
        const Status valid = rollback_witness::validate_transition(
            expected, desired);
        if (!valid.ok()) return valid;
        record_ = desired;
        return Status::success();
    }

    bool independently_controlled() const noexcept override { return false; }

    void fail_before_cas(std::size_t call) {
        std::scoped_lock lock(mutex_);
        fail_before_cas_call_ = call;
    }

    rollback_witness::Record current() const {
        std::scoped_lock lock(mutex_);
        return record_;
    }

  private:
    mutable std::mutex mutex_;
    rollback_witness::Record record_;
    std::size_t cas_calls_{0U};
    std::size_t fail_before_cas_call_{0U};
    std::size_t unavailable_queries_{0U};
};

rollback_witness::DomainId witness_domain() {
    rollback_witness::DomainId domain{};
    domain[0U] = 0x72U;
    domain[15U] = 0xa4U;
    return domain;
}

struct StoreFixture {
    security::Sodium sodium;
    security::DeviceIdentity identity;
    std::filesystem::path root;
    std::filesystem::path artifact;
    std::filesystem::path generation;

    StoreFixture() {
        auto loaded = security::Sodium::load();
        if (!loaded) throw std::runtime_error(loaded.status().message());
        sodium = std::move(loaded).value();
        root = std::filesystem::temp_directory_path() /
               ("iotox-route-store-" + std::to_string(::getpid()));
        std::filesystem::remove_all(root);
        std::filesystem::create_directories(root);
        if (::chmod(root.c_str(), 0700) != 0) {
            throw std::runtime_error("unable to privatize route-store fixture");
        }
        artifact = root / "routes.signed";
        generation = root / "routes.generation";

        auto keys = sodium.signing_keypair_from_seed(signing_seed(0x62U));
        if (!keys) throw std::runtime_error(keys.status().message());
        std::array<std::uint8_t, security::kDeviceIdentityFileBytes> bytes{};
        const std::array<std::uint8_t, 8U> magic = {
            'I', 'O', 'T', 'O', 'X', 'I', 'D', '1'};
        std::copy(magic.begin(), magic.end(), bytes.begin());
        bytes[8U] = 1U;
        bytes[9U] = 1U;
        const auto seed = signing_seed(0x62U);
        std::copy(seed.begin(), seed.end(), bytes.begin() + 16U);
        std::copy(keys.value().public_key().begin(),
                  keys.value().public_key().end(), bytes.begin() + 48U);
        const Status stored =
            StateStore::write_atomic(root / "device.identity", bytes);
        if (!stored.ok()) throw std::runtime_error(stored.message());
        auto opened = security::DeviceIdentity::load(
            root / "device.identity", sodium);
        if (!opened) throw std::runtime_error(opened.status().message());
        identity = std::move(opened).value();
    }

    ~StoreFixture() { std::filesystem::remove_all(root); }

    routes::RouteSet route_set(std::uint64_t generation_value) const {
        routes::RouteSet set;
        set.generation = generation_value;
        set.stable_device_principal = identity.public_key();
        set.coordinator_tox_public_key = route_key(0x70U);
        set.members = {
            {route_key(0x10U), routes::Role::protected_route,
             routes::ConnectionClass::tcp, 1U, 1U, 0U},
            {route_key(0x20U), routes::Role::bulk,
             routes::ConnectionClass::tcp, 8U, 2U, 0U},
        };
        return set;
    }

    std::vector<std::uint8_t> install(std::uint64_t generation_value) {
        auto signed_set = routes::sign_route_set(
            route_set(generation_value), identity);
        if (!signed_set) {
            throw std::runtime_error(signed_set.status().message());
        }
        const Status written = StateStore::write_atomic(artifact, signed_set.value());
        if (!written.ok()) throw std::runtime_error(written.message());
        return std::move(signed_set).value();
    }

    routes::RouteSetStore::Config config() const {
        routes::RouteSetStore::Config result;
        result.artifact_path = artifact;
        result.generation_state_path = generation;
        return result;
    }

    routes::RouteSetStore::Config witnessed_config(
        std::shared_ptr<MemoryRouteWitness> backend) const {
        auto result = config();
        routes::RouteWitnessConfig witness;
        witness.backend = std::move(backend);
        witness.domain = witness_domain();
        witness.witness_epoch = 3U;
        witness.intent_path = generation.string() + ".witness-intent";
        witness.allow_non_independent_for_testing = true;
        result.witness = std::move(witness);
        return result;
    }
};

}  // namespace

IOTOX_TEST("route store checkpoints advances and rejects rollback") {
    StoreFixture fixture;
    const auto generation_seven = fixture.install(7U);
    auto opened = routes::RouteSetStore::open(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(opened.ok(), opened.status().message());
    IOTOX_CHECK(opened.value().route_set.generation == 7U);
    IOTOX_CHECK(opened.value().generation_high_water == 7U);
    IOTOX_CHECK(std::filesystem::file_size(fixture.generation) == 152U);

    fixture.install(8U);
    opened = routes::RouteSetStore::open(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK(opened.ok());
    IOTOX_CHECK(opened.value().generation_high_water == 8U);

    IOTOX_CHECK(StateStore::write_atomic(
                    fixture.artifact, generation_seven).ok());
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
}

IOTOX_TEST("route store inspection verifies without checkpoint mutation") {
    StoreFixture fixture;
    fixture.install(6U);
    IOTOX_CHECK(!std::filesystem::exists(fixture.generation));
    auto inspected = routes::RouteSetStore::inspect(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(inspected.ok(), inspected.status().message());
    IOTOX_CHECK(inspected.value().route_set.generation == 6U);
    IOTOX_CHECK(inspected.value().generation_high_water == 0U);
    IOTOX_CHECK(!std::filesystem::exists(fixture.generation));

    auto opened = routes::RouteSetStore::open(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK(opened.ok());
    inspected = routes::RouteSetStore::inspect(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK(inspected.ok());
    IOTOX_CHECK(inspected.value().generation_high_water == 6U);
}

IOTOX_TEST("route store rejects same-generation fork and corrupt checkpoint") {
    StoreFixture fixture;
    fixture.install(4U);
    IOTOX_CHECK(routes::RouteSetStore::open(
                    fixture.config(), fixture.identity, fixture.sodium).ok());

    auto fork = fixture.route_set(4U);
    fork.members[1U].maximum_active_work = 7U;
    auto signed_fork = routes::sign_route_set(fork, fixture.identity);
    IOTOX_CHECK(signed_fork.ok());
    IOTOX_CHECK(StateStore::write_atomic(
                    fixture.artifact, signed_fork.value()).ok());
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());

    auto checkpoint = StateStore::read(fixture.generation);
    IOTOX_CHECK(checkpoint.ok());
    checkpoint.value()[30U] ^= 0x80U;
    IOTOX_CHECK(StateStore::write_atomic(
                    fixture.generation, checkpoint.value()).ok());
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
}

IOTOX_TEST("route store refuses weak linked and symlink policy state") {
    StoreFixture fixture;
    fixture.install(2U);
    IOTOX_CHECK(::chmod(fixture.artifact.c_str(), 0644) == 0);
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
    IOTOX_CHECK(::chmod(fixture.artifact.c_str(), 0600) == 0);

    const auto alias = fixture.root / "artifact.alias";
    IOTOX_CHECK(::link(fixture.artifact.c_str(), alias.c_str()) == 0);
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
    std::filesystem::remove(alias);

    const auto real_artifact = fixture.root / "artifact.real";
    std::filesystem::rename(fixture.artifact, real_artifact);
    std::filesystem::create_symlink(real_artifact, fixture.artifact);
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
}

IOTOX_TEST("route store refuses a replaceable policy directory") {
    StoreFixture fixture;
    fixture.install(2U);
    IOTOX_CHECK(::chmod(fixture.root.c_str(), 0750) == 0);
    IOTOX_CHECK(!routes::RouteSetStore::open(
                     fixture.config(), fixture.identity, fixture.sodium).ok());
}

IOTOX_TEST("route store serializes concurrent generation acceptance") {
    StoreFixture fixture;
    fixture.install(9U);
    std::array<bool, 8U> accepted{};
    std::vector<std::thread> threads;
    for (std::size_t index = 0U; index < accepted.size(); ++index) {
        threads.emplace_back([&, index] {
            accepted[index] = routes::RouteSetStore::open(
                fixture.config(), fixture.identity, fixture.sodium).ok();
        });
    }
    for (auto &thread : threads) thread.join();
    IOTOX_CHECK(std::all_of(accepted.begin(), accepted.end(),
                            [](bool value) { return value; }));
    auto final = routes::RouteSetStore::open(
        fixture.config(), fixture.identity, fixture.sodium);
    IOTOX_CHECK(final.ok());
    IOTOX_CHECK(final.value().generation_high_water == 9U);
}

IOTOX_TEST("route witness enrolls exact policy and rejects complete local rollback") {
    StoreFixture fixture;
    fixture.install(6U);
    IOTOX_CHECK(routes::RouteSetStore::open(
                    fixture.config(), fixture.identity, fixture.sodium).ok());
    const auto generation_seven = fixture.install(7U);
    auto enrollment = routes::RouteSetStore::witness_enrollment(
        fixture.config(), fixture.identity, fixture.sodium,
        witness_domain(), 3U);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    IOTOX_CHECK(enrollment.value().lane ==
                rollback_witness::Lane::route_generation);
    IOTOX_CHECK(enrollment.value().committed.position == 7U);
    auto backend = std::make_shared<MemoryRouteWitness>(enrollment.value());
    const auto config = fixture.witnessed_config(backend);

    auto adopted = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(adopted.ok(), adopted.status().message());
    IOTOX_CHECK(adopted.value().generation_high_water == 7U);
    const auto local_seven = StateStore::read(fixture.generation);
    IOTOX_CHECK(local_seven.ok());

    fixture.install(8U);
    auto advanced = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(advanced.ok(), advanced.status().message());
    IOTOX_CHECK(advanced.value().generation_high_water == 8U);
    IOTOX_CHECK(backend->current().committed.position == 8U);
    IOTOX_CHECK(!backend->current().pending);

    IOTOX_CHECK(StateStore::write_atomic(
                    fixture.artifact, generation_seven).ok());
    IOTOX_CHECK(StateStore::write_atomic(
                    fixture.generation, local_seven.value()).ok());
    auto rolled_back = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!rolled_back.ok());
    IOTOX_CHECK(rolled_back.status().code() == ErrorCode::protocol_error);
    IOTOX_CHECK(backend->current().committed.position == 8U);
}

IOTOX_TEST("route witness recovers exact pending adoption and refuses generation skips") {
    StoreFixture fixture;
    fixture.install(4U);
    auto enrollment = routes::RouteSetStore::witness_enrollment(
        fixture.config(), fixture.identity, fixture.sodium,
        witness_domain(), 3U);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    auto backend = std::make_shared<MemoryRouteWitness>(enrollment.value());
    const auto config = fixture.witnessed_config(backend);
    IOTOX_CHECK(routes::RouteSetStore::open(
                    config, fixture.identity, fixture.sodium).ok());

    fixture.install(5U);
    backend->fail_before_cas(2U);
    auto interrupted = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(interrupted.status().code() == ErrorCode::unavailable);
    IOTOX_CHECK(backend->current().pending.has_value());
    IOTOX_CHECK(std::filesystem::exists(
        config.witness->intent_path));

    auto recovered = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value().generation_high_water == 5U);
    IOTOX_CHECK(backend->current().committed.position == 5U);
    IOTOX_CHECK(!backend->current().pending);
    IOTOX_CHECK(!std::filesystem::exists(
        config.witness->intent_path));

    fixture.install(7U);
    auto skipped = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!skipped.ok());
    IOTOX_CHECK(skipped.status().code() == ErrorCode::protocol_error);
    IOTOX_CHECK(backend->current().committed.position == 5U);
}

IOTOX_TEST("route witness refuses a same-domain backend outside tests") {
    StoreFixture fixture;
    fixture.install(2U);
    auto enrollment = routes::RouteSetStore::witness_enrollment(
        fixture.config(), fixture.identity, fixture.sodium,
        witness_domain(), 3U);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    auto backend = std::make_shared<MemoryRouteWitness>(enrollment.value());
    auto config = fixture.witnessed_config(backend);
    config.witness->allow_non_independent_for_testing = false;
    auto refused = routes::RouteSetStore::open(
        config, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == ErrorCode::invalid_argument);
}
