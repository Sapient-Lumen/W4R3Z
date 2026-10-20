#include "test_harness.hpp"

#include "iotox/interactive_incarnation.hpp"
#include "iotox/policy_witness.hpp"
#include "iotox/rollback_witness_service.hpp"
#include "iotox/route_store.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/state_store.hpp"

#include <atomic>
#include <arpa/inet.h>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <memory>
#include <netinet/in.h>
#include <string>
#include <sys/socket.h>
#include <system_error>
#include <thread>
#include <unistd.h>

namespace {

using namespace std::chrono_literals;

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        path_ = std::filesystem::temp_directory_path() /
            ("iotox-witness-service-test-" + std::to_string(::getpid()) +
             "-" + std::to_string(
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

std::filesystem::path private_directory(const std::filesystem::path &parent,
                                        std::string_view name) {
    const std::filesystem::path result = parent / name;
    std::filesystem::create_directory(result);
    std::filesystem::permissions(result, std::filesystem::perms::owner_all,
                                 std::filesystem::perm_options::replace);
    return result;
}

iotox::rollback_witness::Record initial_record(
    const iotox::security::DeviceIdentity &device) {
    iotox::rollback_witness::Record record;
    record.domain[0] = 0x41U;
    record.device = device.public_key();
    record.witness_epoch = 7U;
    return record;
}

iotox::rollback_witness::RemoteBackendConfig remote_config(
    std::uint16_t port,
    const iotox::security::DeviceIdentity &service,
    const iotox::rollback_witness::Record &record) {
    iotox::rollback_witness::RemoteBackendConfig config;
    config.endpoint.host = "127.0.0.1";
    config.endpoint.service = std::to_string(port);
    config.endpoint.timeout = 3s;
    config.service_key = service.public_key();
    config.domain = record.domain;
    config.witness_epoch = record.witness_epoch;
    config.lane = record.lane;
    return config;
}

class FixedCallServer {
  public:
    FixedCallServer(iotox::rollback_witness::ServiceStore &store,
                    std::size_t calls) {
        iotox::rollback_witness::ServiceEndpoint endpoint;
        endpoint.host = "127.0.0.1";
        endpoint.service = "0";
        endpoint.timeout = 3s;
        auto server = iotox::rollback_witness::TcpServiceServer::listen(
            endpoint, store);
        IOTOX_CHECK(server.ok());
        server_ = std::move(server).value();
        worker_ = std::thread([this, calls] {
            for (std::size_t index = 0U; index < calls; ++index) {
                const iotox::Status served = server_->serve_one(5s);
                if (!served.ok()) {
                    failed_.store(true);
                    break;
                }
            }
        });
    }
    ~FixedCallServer() {
        if (worker_.joinable()) worker_.join();
    }
    [[nodiscard]] std::uint16_t port() const { return server_->bound_port(); }
    void join() {
        if (worker_.joinable()) worker_.join();
        IOTOX_CHECK(!failed_.load());
    }

  private:
    std::unique_ptr<iotox::rollback_witness::TcpServiceServer> server_;
    std::thread worker_;
    std::atomic<bool> failed_{false};
};

struct Fixture {
    TemporaryDirectory temporary;
    iotox::security::Sodium sodium;
    std::filesystem::path device_root;
    std::filesystem::path service_root;
    iotox::security::DeviceIdentity device;
    iotox::security::DeviceIdentity service;
    std::unique_ptr<iotox::rollback_witness::ServiceStore> store;
    iotox::rollback_witness::Record initial;

    Fixture()
        : sodium(load_sodium()),
          device_root(private_directory(temporary.path(), "device")),
          service_root(private_directory(temporary.path(), "service")),
          device(load_device()), service(load_service()),
          store(open_store()), initial(initial_record(device)) {
        IOTOX_CHECK(store->enroll(initial).ok());
    }

  private:
    static iotox::security::Sodium load_sodium() {
        auto loaded = iotox::security::Sodium::load();
        IOTOX_CHECK(loaded.ok());
        return std::move(loaded).value();
    }
    iotox::security::DeviceIdentity load_device() {
        auto loaded = iotox::security::DeviceIdentity::load_or_create(
            device_root / "device.identity", sodium, true);
        IOTOX_CHECK(loaded.ok());
        return std::move(loaded).value();
    }
    iotox::security::DeviceIdentity load_service() {
        auto loaded = iotox::security::DeviceIdentity::create_new_witness(
            service_root / "service.identity", sodium);
        IOTOX_CHECK(loaded.ok());
        return std::move(loaded).value();
    }
    std::unique_ptr<iotox::rollback_witness::ServiceStore> open_store() {
        auto opened = iotox::rollback_witness::ServiceStore::open(
            service_root, service, sodium);
        IOTOX_CHECK(opened.ok());
        return std::move(opened).value();
    }
};

void connect_and_close(std::uint16_t port) {
    const int descriptor = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    IOTOX_CHECK(descriptor >= 0);
    struct sockaddr_in address {};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    IOTOX_CHECK(::inet_pton(AF_INET, "127.0.0.1", &address.sin_addr) == 1);
    IOTOX_CHECK(::connect(descriptor,
                          reinterpret_cast<const struct sockaddr *>(&address),
                          sizeof(address)) == 0);
    IOTOX_CHECK(::close(descriptor) == 0);
}

std::filesystem::path only_witness_record(
    const std::filesystem::path &root) {
    std::filesystem::path result;
    for (const auto &entry : std::filesystem::directory_iterator(root)) {
        if (entry.path().extension() != ".witness") continue;
        IOTOX_CHECK(result.empty());
        result = entry.path();
    }
    IOTOX_CHECK(!result.empty());
    return result;
}

iotox::rollback_witness::Record begin_remote_transition(
    Fixture &fixture, const iotox::rollback_witness::Record &current,
    std::uint8_t digest_byte) {
    FixedCallServer server(*fixture.store, 1U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, current),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    iotox::rollback_witness::Head next;
    next.position = current.committed.position + 1U;
    next.digest[0] = digest_byte;
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0] = static_cast<std::uint8_t>(digest_byte ^ 0xa5U);
    auto pending = iotox::rollback_witness::begin(current, next, nonce);
    IOTOX_CHECK(pending.ok());
    IOTOX_CHECK(backend.value()
                    ->compare_exchange(current, pending.value())
                    .ok());
    server.join();
    return pending.value();
}

iotox::rollback_witness::Record finish_remote_transition(
    Fixture &fixture, const iotox::rollback_witness::Record &pending) {
    FixedCallServer server(*fixture.store, 1U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, pending),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    auto committed = iotox::rollback_witness::finish(pending);
    IOTOX_CHECK(committed.ok());
    IOTOX_CHECK(backend.value()
                    ->compare_exchange(pending, committed.value())
                    .ok());
    server.join();
    return committed.value();
}

}  // namespace

IOTOX_TEST("witness service survives a truncated accepted connection") {
    Fixture fixture;
    FixedCallServer server(*fixture.store, 2U);
    connect_and_close(server.port());

    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    auto queried = backend.value()->query();
    IOTOX_CHECK(queried.ok());
    IOTOX_CHECK(queried.value() == fixture.initial);
    server.join();
}

IOTOX_TEST("authenticated witness service persists exact begin and commit") {
    Fixture fixture;
    FixedCallServer server(*fixture.store, 5U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    auto current = backend.value()->query();
    IOTOX_CHECK(current.ok());
    IOTOX_CHECK(current.value() == fixture.initial);

    iotox::rollback_witness::Head next;
    next.position = 1U;
    next.digest[0] = 0x77U;
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0] = 0x55U;
    auto pending = iotox::rollback_witness::begin(current.value(), next, nonce);
    IOTOX_CHECK(pending.ok());
    IOTOX_CHECK(backend.value()
                    ->compare_exchange(current.value(), pending.value())
                    .ok());
    auto observed_pending = backend.value()->query();
    IOTOX_CHECK(observed_pending.ok());
    IOTOX_CHECK(observed_pending.value() == pending.value());
    auto committed = iotox::rollback_witness::finish(pending.value());
    IOTOX_CHECK(committed.ok());
    IOTOX_CHECK(backend.value()
                    ->compare_exchange(pending.value(), committed.value())
                    .ok());
    auto observed_committed = backend.value()->query();
    IOTOX_CHECK(observed_committed.ok());
    IOTOX_CHECK(observed_committed.value() == committed.value());
    server.join();
}

IOTOX_TEST("authenticated witness service exact CAS elects one remote client") {
    Fixture fixture;
    FixedCallServer server(*fixture.store, 2U);
    auto first = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    auto second = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(second.ok());
    iotox::rollback_witness::Head next;
    next.position = 1U;
    next.digest[0] = 9U;
    iotox::rollback_witness::TransactionNonce nonce{};
    nonce[0] = 8U;
    auto pending = iotox::rollback_witness::begin(fixture.initial, next, nonce);
    IOTOX_CHECK(pending.ok());
    std::atomic<unsigned> successes{0U};
    std::thread one([&] {
        if (first.value()
                ->compare_exchange(fixture.initial, pending.value())
                .ok()) {
            ++successes;
        }
    });
    std::thread two([&] {
        if (second.value()
                ->compare_exchange(fixture.initial, pending.value())
                .ok()) {
            ++successes;
        }
    });
    one.join();
    two.join();
    server.join();
    IOTOX_CHECK(successes.load() == 1U);
}

IOTOX_TEST("authenticated witness service rejects wrong pinned signer") {
    Fixture fixture;
    const auto foreign_root = private_directory(fixture.temporary.path(), "foreign");
    auto foreign = iotox::security::DeviceIdentity::create_new_witness(
        foreign_root / "foreign.identity", fixture.sodium);
    IOTOX_CHECK(foreign.ok());
    FixedCallServer server(*fixture.store, 1U);
    auto config = remote_config(server.port(), fixture.service, fixture.initial);
    config.service_key = foreign.value().public_key();
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        config, fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    auto queried = backend.value()->query();
    IOTOX_CHECK(!queried.ok());
    IOTOX_CHECK(queried.status().code() == iotox::ErrorCode::protocol_error);
    server.join();
}

IOTOX_TEST("authenticated witness service detects stored record tampering after restart") {
    Fixture fixture;
    std::filesystem::path record_path;
    for (const auto &entry : std::filesystem::directory_iterator(fixture.service_root)) {
        if (entry.path().extension() == ".witness") record_path = entry.path();
    }
    IOTOX_CHECK(!record_path.empty());
    std::fstream record(record_path, std::ios::in | std::ios::out | std::ios::binary);
    IOTOX_CHECK(record.good());
    record.seekp(100);
    const char altered = '\x5a';
    record.write(&altered, 1);
    record.close();

    fixture.store.reset();
    auto reopened = iotox::rollback_witness::ServiceStore::open(
        fixture.service_root, fixture.service, fixture.sodium);
    IOTOX_CHECK(reopened.ok());
    fixture.store = std::move(reopened).value();
    FixedCallServer server(*fixture.store, 1U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    auto queried = backend.value()->query();
    IOTOX_CHECK(!queried.ok());
    server.join();
}

IOTOX_TEST("witness enrollment binds its exact device and committed head") {
    Fixture fixture;
    auto enrollment = iotox::rollback_witness::create_enrollment(
        fixture.initial, fixture.device);
    IOTOX_CHECK(enrollment.ok());
    auto verified = iotox::rollback_witness::verify_enrollment(
        enrollment.value(), fixture.sodium);
    IOTOX_CHECK(verified.ok());
    IOTOX_CHECK(verified.value() == fixture.initial);
    enrollment.value()[80U] ^= 1U;
    verified = iotox::rollback_witness::verify_enrollment(
        enrollment.value(), fixture.sodium);
    IOTOX_CHECK(!verified.ok());
}

IOTOX_TEST("witness service store excludes a concurrent server process") {
    Fixture fixture;
    auto contender = iotox::rollback_witness::ServiceStore::open(
        fixture.service_root, fixture.service, fixture.sodium);
    IOTOX_CHECK(!contender.ok());
    IOTOX_CHECK(contender.status().code() == iotox::ErrorCode::unavailable);
}

IOTOX_TEST("witness service checkpoint binds complete sorted population") {
    Fixture fixture;
    auto application = fixture.initial;
    application.lane =
        iotox::rollback_witness::Lane::application_incarnation;
    IOTOX_CHECK(fixture.store->enroll(application).ok());

    auto first = fixture.store->checkpoint();
    auto second = fixture.store->checkpoint();
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(second.ok());
    IOTOX_CHECK(first.value() == second.value());
    auto decoded = iotox::rollback_witness::verify_service_checkpoint(
        first.value(), fixture.service.public_key(), fixture.sodium);
    IOTOX_CHECK(decoded.ok());
    IOTOX_CHECK(decoded.value().service_key == fixture.service.public_key());
    IOTOX_CHECK(decoded.value().records.size() == 2U);
    IOTOX_CHECK(decoded.value().records[0].lane ==
                iotox::rollback_witness::Lane::authority);
    IOTOX_CHECK(decoded.value().records[1].lane ==
                iotox::rollback_witness::Lane::application_incarnation);
    IOTOX_CHECK(fixture.store->require_checkpoint(first.value()).ok());

    auto foreign_root = private_directory(fixture.temporary.path(), "foreign");
    auto foreign = iotox::security::DeviceIdentity::create_new_witness(
        foreign_root / "foreign.identity", fixture.sodium);
    IOTOX_CHECK(foreign.ok());
    auto wrong_key = iotox::rollback_witness::verify_service_checkpoint(
        first.value(), foreign.value().public_key(), fixture.sodium);
    IOTOX_CHECK(!wrong_key.ok());
    first.value()[80U] ^= 1U;
    auto tampered = iotox::rollback_witness::verify_service_checkpoint(
        first.value(), fixture.service.public_key(), fixture.sodium);
    IOTOX_CHECK(!tampered.ok());
}

IOTOX_TEST("witness checkpoint floor rejects selective record rollback") {
    Fixture fixture;
    const auto record_path = only_witness_record(fixture.service_root);
    auto old_record = iotox::StateStore::read(record_path);
    auto old_checkpoint = fixture.store->checkpoint();
    IOTOX_CHECK(old_record.ok());
    IOTOX_CHECK(old_checkpoint.ok());

    auto pending = begin_remote_transition(fixture, fixture.initial, 0x61U);
    auto committed = finish_remote_transition(fixture, pending);
    IOTOX_CHECK(committed.committed.position == 1U);
    auto new_checkpoint = fixture.store->checkpoint();
    IOTOX_CHECK(new_checkpoint.ok());
    IOTOX_CHECK(fixture.store->require_checkpoint(old_checkpoint.value()).ok());
    IOTOX_CHECK(fixture.store->require_checkpoint(new_checkpoint.value()).ok());

    fixture.store.reset();
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    record_path, old_record.value()).ok());
    auto reopened = iotox::rollback_witness::ServiceStore::open(
        fixture.service_root, fixture.service, fixture.sodium);
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(!reopened.value()
                     ->require_checkpoint(new_checkpoint.value())
                     .ok());
    IOTOX_CHECK(reopened.value()
                    ->require_checkpoint(old_checkpoint.value())
                    .ok());
}

IOTOX_TEST("witness checkpoint floor rejects missing enrolled selector") {
    Fixture fixture;
    auto application = fixture.initial;
    application.lane =
        iotox::rollback_witness::Lane::application_incarnation;
    IOTOX_CHECK(fixture.store->enroll(application).ok());
    auto checkpoint = fixture.store->checkpoint();
    IOTOX_CHECK(checkpoint.ok());

    std::filesystem::path application_path;
    for (const auto &entry :
         std::filesystem::directory_iterator(fixture.service_root)) {
        if (entry.path().extension() == ".witness" &&
            entry.path().filename().string().ends_with("-2.witness")) {
            application_path = entry.path();
        }
    }
    IOTOX_CHECK(!application_path.empty());
    fixture.store.reset();
    IOTOX_CHECK(std::filesystem::remove(application_path));
    auto reopened = iotox::rollback_witness::ServiceStore::open(
        fixture.service_root, fixture.service, fixture.sodium);
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value()->verify_all().ok());
    IOTOX_CHECK(!reopened.value()
                     ->require_checkpoint(checkpoint.value())
                     .ok());
}

IOTOX_TEST("pending witness checkpoint floor requires exact successor") {
    Fixture fixture;
    const auto record_path = only_witness_record(fixture.service_root);
    auto old_record = iotox::StateStore::read(record_path);
    IOTOX_CHECK(old_record.ok());
    auto pending = begin_remote_transition(fixture, fixture.initial, 0x71U);
    auto pending_checkpoint = fixture.store->checkpoint();
    IOTOX_CHECK(pending_checkpoint.ok());
    IOTOX_CHECK(fixture.store
                    ->require_checkpoint(pending_checkpoint.value())
                    .ok());
    auto committed = finish_remote_transition(fixture, pending);
    IOTOX_CHECK(committed.committed == *pending.pending);
    IOTOX_CHECK(fixture.store
                    ->require_checkpoint(pending_checkpoint.value())
                    .ok());

    fixture.store.reset();
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    record_path, old_record.value()).ok());
    auto reopened = iotox::rollback_witness::ServiceStore::open(
        fixture.service_root, fixture.service, fixture.sodium);
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(!reopened.value()
                     ->require_checkpoint(pending_checkpoint.value())
                     .ok());
}

IOTOX_TEST("authority ledger commits and restarts through remote witness service") {
    Fixture fixture;
    FixedCallServer server(*fixture.store, 6U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, fixture.initial),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    iotox::security::AuthorityLedger::Config config;
    config.path = fixture.device_root / "authority.ledger";
    config.rollback_witness = backend.value();
    config.rollback_witness_domain = fixture.initial.domain;
    config.rollback_witness_epoch = fixture.initial.witness_epoch;
    config.rollback_witness_intent_path =
        fixture.device_root / "authority.witness-intent";
    auto opened = iotox::security::AuthorityLedger::open(
        config, fixture.device.public_key(), fixture.sodium);
    IOTOX_CHECK(opened.ok());
    auto ledger = std::move(opened).value();

    iotox::security::SigningSeed owner_seed{};
    owner_seed[0] = 0x91U;
    auto owner = fixture.sodium.signing_keypair_from_seed(owner_seed);
    IOTOX_CHECK(owner.ok());
    iotox::security::AuthorityPrepareRequest request;
    request.action = iotox::security::AuthorityAction::bootstrap;
    request.role = iotox::security::PrincipalRole::owner;
    request.capabilities = iotox::security::kAllCapabilities;
    request.issuer = owner.value().public_key();
    request.subject = owner.value().public_key();
    auto body = ledger->prepare(request);
    IOTOX_CHECK(body.ok());
    auto record = iotox::security::sign_authority_record_body(
        body.value(), owner.value().secret_key(), fixture.sodium);
    IOTOX_CHECK(record.ok());
    IOTOX_CHECK(ledger->append(record.value()).ok());
    auto witnessed = backend.value()->query();
    IOTOX_CHECK(witnessed.ok());
    IOTOX_CHECK(witnessed.value().committed.position == 1U);
    IOTOX_CHECK(!witnessed.value().pending.has_value());

    ledger.reset();
    auto reopened = iotox::security::AuthorityLedger::open(
        config, fixture.device.public_key(), fixture.sodium);
    IOTOX_CHECK(reopened.ok());
    IOTOX_CHECK(reopened.value()->snapshot().record_count == 1U);
    server.join();
}

IOTOX_TEST("application incarnation advances through authenticated remote witness service") {
    Fixture fixture;
    auto application = fixture.initial;
    application.lane =
        iotox::rollback_witness::Lane::application_incarnation;
    IOTOX_CHECK(fixture.store->enroll(application).ok());
    FixedCallServer server(*fixture.store, 5U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, application),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());

    const auto state = fixture.device_root / "application.incarnation";
    iotox::interactive::IncarnationWitnessConfig witness;
    witness.backend = backend.value();
    witness.domain = application.domain;
    witness.witness_epoch = application.witness_epoch;
    witness.lane = application.lane;
    witness.intent_path = fixture.device_root / "application.witness-intent";
    auto lease = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.device, fixture.sodium, witness);
    IOTOX_CHECK_MSG(lease.ok(), lease.status().message());
    IOTOX_CHECK(lease.value().incarnation() == 1U);
    auto observed = backend.value()->query();
    IOTOX_CHECK(observed.ok());
    IOTOX_CHECK(observed.value().committed.position == 1U);
    IOTOX_CHECK(!observed.value().pending);
    IOTOX_CHECK(!std::filesystem::exists(witness.intent_path));
    server.join();
}

IOTOX_TEST("route generation advances through authenticated remote witness service") {
    Fixture fixture;
    iotox::routes::RouteSet route_set;
    route_set.generation = 1U;
    route_set.stable_device_principal = fixture.device.public_key();
    route_set.coordinator_tox_public_key.fill(0x70U);
    iotox::routes::MemberPolicy first;
    first.tox_public_key.fill(0x71U);
    first.role = iotox::routes::Role::protected_route;
    first.connection_class = iotox::routes::ConnectionClass::tcp;
    first.maximum_active_work = 1U;
    first.restart_budget = 1U;
    iotox::routes::MemberPolicy second = first;
    second.tox_public_key.fill(0x72U);
    second.role = iotox::routes::Role::bulk;
    route_set.members = {first, second};
    auto signed_set = iotox::routes::sign_route_set(route_set, fixture.device);
    IOTOX_CHECK_MSG(signed_set.ok(), signed_set.status().message());
    const auto artifact = fixture.device_root / "routes.signed";
    const auto generation = fixture.device_root / "routes.generation";
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    artifact, signed_set.value()).ok());
    iotox::routes::RouteSetStore::Config local;
    local.artifact_path = artifact;
    local.generation_state_path = generation;
    auto route_record = iotox::routes::RouteSetStore::witness_enrollment(
        local, fixture.device, fixture.sodium, fixture.initial.domain,
        fixture.initial.witness_epoch);
    IOTOX_CHECK_MSG(route_record.ok(), route_record.status().message());
    IOTOX_CHECK(fixture.store->enroll(route_record.value()).ok());
    FixedCallServer server(*fixture.store, 5U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, route_record.value()),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    iotox::routes::RouteWitnessConfig witness;
    witness.backend = backend.value();
    witness.domain = route_record.value().domain;
    witness.witness_epoch = route_record.value().witness_epoch;
    witness.intent_path = fixture.device_root / "route.witness-intent";
    local.witness = witness;
    auto adopted = iotox::routes::RouteSetStore::open(
        local, fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(adopted.ok(), adopted.status().message());
    IOTOX_CHECK(adopted.value().generation_high_water == 1U);

    route_set.generation = 2U;
    signed_set = iotox::routes::sign_route_set(route_set, fixture.device);
    IOTOX_CHECK_MSG(signed_set.ok(), signed_set.status().message());
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    artifact, signed_set.value()).ok());
    auto advanced = iotox::routes::RouteSetStore::open(
        local, fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(advanced.ok(), advanced.status().message());
    IOTOX_CHECK(advanced.value().generation_high_water == 2U);
    auto observed = backend.value()->query();
    IOTOX_CHECK(observed.ok());
    IOTOX_CHECK(observed.value().committed.position == 2U);
    IOTOX_CHECK(!observed.value().pending);
    IOTOX_CHECK(!std::filesystem::exists(witness.intent_path));
    server.join();
}

IOTOX_TEST("terminal policy advances through authenticated remote witness service") {
    Fixture fixture;
    const auto first = fixture.sodium.hash(
        "iotox-test-terminal-policy",
        std::span<const std::uint8_t>{});
    IOTOX_CHECK(first.ok());
    const std::array<std::uint8_t, 1U> changed_bytes{0x42U};
    const auto second = fixture.sodium.hash(
        "iotox-test-terminal-policy", changed_bytes);
    IOTOX_CHECK(second.ok());
    auto terminal_record = iotox::policy_witness::enrollment_record(
        fixture.device_root / "terminal-policy.checkpoint", first.value(),
        fixture.device, fixture.sodium, fixture.initial.domain,
        fixture.initial.witness_epoch,
        iotox::rollback_witness::Lane::terminal_policy);
    IOTOX_CHECK_MSG(terminal_record.ok(), terminal_record.status().message());
    IOTOX_CHECK(fixture.store->enroll(terminal_record.value()).ok());
    FixedCallServer server(*fixture.store, 5U);
    auto backend = iotox::rollback_witness::RemoteBackend::create(
        remote_config(server.port(), fixture.service, terminal_record.value()),
        fixture.device, fixture.sodium);
    IOTOX_CHECK(backend.ok());
    iotox::policy_witness::Config witness;
    witness.backend = backend.value();
    witness.domain = terminal_record.value().domain;
    witness.witness_epoch = terminal_record.value().witness_epoch;
    witness.lane = iotox::rollback_witness::Lane::terminal_policy;
    witness.checkpoint_path =
        fixture.device_root / "terminal-policy.checkpoint";
    witness.intent_path = fixture.device_root / "terminal-policy.intent";
    auto verified = iotox::policy_witness::verify(
        witness, first.value(), fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(verified.ok(), verified.status().message());
    auto committed = iotox::policy_witness::commit(
        witness, second.value(), fixture.device, fixture.sodium);
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    IOTOX_CHECK(committed.value() == 2U);
    auto observed = backend.value()->query();
    IOTOX_CHECK(observed.ok());
    IOTOX_CHECK(observed.value().committed.position == 2U);
    IOTOX_CHECK(observed.value().committed.digest == second.value());
    IOTOX_CHECK(!observed.value().pending);
    server.join();
}
