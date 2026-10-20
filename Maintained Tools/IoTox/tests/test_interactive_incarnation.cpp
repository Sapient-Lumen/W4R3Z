#include "iotox/interactive_incarnation.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "test_harness.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <system_error>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        const auto ticks =
            std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
                ("iotox-incarnation-test-" + std::to_string(::getpid()) + "-" +
                 std::to_string(ticks));
        std::filesystem::create_directories(path_);
        IOTOX_CHECK(::chmod(path_.c_str(), 0700) == 0);
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

struct Fixture {
    TemporaryDirectory temporary;
    iotox::security::Sodium sodium;
    iotox::security::DeviceIdentity identity;

    Fixture()
        : sodium(load_sodium()),
          identity(load_identity(
              temporary.path() / "device.identity", sodium)) {}

  private:
    static iotox::security::Sodium load_sodium() {
        auto loaded = iotox::security::Sodium::load();
        IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
        return std::move(loaded).value();
    }

    static iotox::security::DeviceIdentity load_identity(
        const std::filesystem::path &path,
        const iotox::security::Sodium &sodium) {
        auto loaded = iotox::security::DeviceIdentity::load_or_create(
            path, sodium, true);
        IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
        return std::move(loaded).value();
    }
};

class MemoryIncarnationWitness final
    : public iotox::rollback_witness::Backend {
  public:
    explicit MemoryIncarnationWitness(iotox::rollback_witness::Record record)
        : record_(std::move(record)) {}

    iotox::Result<iotox::rollback_witness::Record> query() override {
        std::scoped_lock lock(mutex_);
        if (unavailable_queries_ > 0U) {
            --unavailable_queries_;
            return iotox::Status{
                iotox::ErrorCode::unavailable,
                "injected incarnation witness query failure"};
        }
        return record_;
    }

    iotox::Status compare_exchange(
        const iotox::rollback_witness::Record &expected,
        const iotox::rollback_witness::Record &desired) override {
        std::scoped_lock lock(mutex_);
        ++cas_calls_;
        if (fail_before_cas_call_ == cas_calls_) {
            unavailable_queries_ = 1U;
            return iotox::Status{
                iotox::ErrorCode::unavailable,
                "injected incarnation witness CAS failure"};
        }
        if (!(record_ == expected)) {
            return iotox::Status{
                iotox::ErrorCode::protocol_error,
                "injected incarnation witness CAS conflict"};
        }
        const auto transition =
            iotox::rollback_witness::validate_transition(expected, desired);
        if (!transition.ok()) return transition;
        record_ = desired;
        return iotox::Status::success();
    }

    [[nodiscard]] bool independently_controlled() const noexcept override {
        return false;
    }

    void fail_before_cas(std::size_t call) {
        std::scoped_lock lock(mutex_);
        fail_before_cas_call_ = call;
    }

    [[nodiscard]] iotox::rollback_witness::Record current() const {
        std::scoped_lock lock(mutex_);
        return record_;
    }

  private:
    mutable std::mutex mutex_;
    iotox::rollback_witness::Record record_;
    std::size_t cas_calls_{0U};
    std::size_t fail_before_cas_call_{0U};
    std::size_t unavailable_queries_{0U};
};

iotox::rollback_witness::DomainId witness_domain() {
    iotox::rollback_witness::DomainId domain{};
    domain[0U] = 0xa5U;
    domain[15U] = 0x5aU;
    return domain;
}

iotox::interactive::IncarnationWitnessConfig witnessed_config(
    const std::filesystem::path &state,
    std::shared_ptr<MemoryIncarnationWitness> backend,
    iotox::rollback_witness::Lane lane) {
    iotox::interactive::IncarnationWitnessConfig config;
    config.backend = std::move(backend);
    config.domain = witness_domain();
    config.witness_epoch = 7U;
    config.lane = lane;
    config.intent_path = state.string() + ".witness-intent";
    config.allow_non_independent_for_testing = true;
    return config;
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    IOTOX_CHECK(input.good());
    return std::vector<std::uint8_t>{
        std::istreambuf_iterator<char>{input},
        std::istreambuf_iterator<char>{}};
}

void write_private(
    const std::filesystem::path &path,
    std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    IOTOX_CHECK(output.good());
    output.write(
        reinterpret_cast<const char *>(bytes.data()),
        static_cast<std::streamsize>(bytes.size()));
    output.close();
    IOTOX_CHECK(output.good());
    IOTOX_CHECK(::chmod(path.c_str(), 0600) == 0);
}

std::array<std::uint8_t, 128U> signed_record(
    std::uint64_t incarnation,
    const iotox::security::DeviceIdentity &identity) {
    std::array<std::uint8_t, 128U> bytes{};
    const std::array<std::uint8_t, 8U> magic = {
        'I', 'O', 'T', 'X', 'R', 'I', 'N', '1'};
    std::copy(magic.begin(), magic.end(), bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = 1U;
    std::copy(
        identity.public_key().begin(), identity.public_key().end(),
        bytes.begin() + 16);
    const auto write_u64 = [&bytes](std::size_t offset, std::uint64_t value) {
        for (std::size_t index = 0U; index < 8U; ++index) {
            const unsigned int shift =
                static_cast<unsigned int>((7U - index) * 8U);
            bytes[offset + index] =
                static_cast<std::uint8_t>((value >> shift) & 0xffU);
        }
    };
    write_u64(48U, incarnation);
    write_u64(56U, ~incarnation);
    auto signature = identity.sign(
        std::span<const std::uint8_t>(bytes.data(), 64U));
    IOTOX_CHECK_MSG(signature.ok(), signature.status().message());
    std::copy(signature.value().begin(), signature.value().end(), bytes.begin() + 64);
    return bytes;
}

mode_t exact_mode(const std::filesystem::path &path) {
    struct stat metadata {};
    IOTOX_CHECK(::lstat(path.c_str(), &metadata) == 0);
    return metadata.st_mode & 07777U;
}

}  // namespace

IOTOX_TEST("Ratox incarnation lease advances and excludes same-process contenders") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";

    auto first = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(first.value().valid());
    IOTOX_CHECK(first.value().incarnation() != 0U);
    IOTOX_CHECK(std::filesystem::file_size(state) == 128U);
    IOTOX_CHECK(exact_mode(state) == 0600U);
    IOTOX_CHECK(exact_mode(state.string() + ".lock") == 0600U);
    IOTOX_CHECK(exact_mode(lane) == 0700U);

    auto blocked = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!blocked.ok());
    IOTOX_CHECK(blocked.status().code() == iotox::ErrorCode::resource_exhausted);

    const std::uint64_t first_value = first.value().incarnation();
    first.value().reset();
    auto second = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().incarnation() == first_value + 1U);
}

IOTOX_TEST("Ratox incarnation lease excludes a distinct process") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";

    int ready_pipe[2] = {-1, -1};
    int release_pipe[2] = {-1, -1};
    IOTOX_CHECK(::pipe(ready_pipe) == 0);
    IOTOX_CHECK(::pipe(release_pipe) == 0);
    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        static_cast<void>(::close(ready_pipe[0]));
        static_cast<void>(::close(release_pipe[1]));
        auto held = iotox::interactive::RatoxIncarnationLease::acquire(
            state, fixture.identity, fixture.sodium);
        const char ready = held.ok() ? '1' : '0';
        if (::write(ready_pipe[1], &ready, 1U) != 1) {
            _exit(1);
        }
        char release = 0;
        if (::read(release_pipe[0], &release, 1U) != 1) {
            _exit(1);
        }
        _exit(held.ok() && release == 'x' ? 0 : 1);
    }
    static_cast<void>(::close(ready_pipe[1]));
    static_cast<void>(::close(release_pipe[0]));
    char ready = 0;
    IOTOX_CHECK(::read(ready_pipe[0], &ready, 1U) == 1);
    IOTOX_CHECK(ready == '1');

    auto blocked = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!blocked.ok());
    IOTOX_CHECK(blocked.status().code() == iotox::ErrorCode::resource_exhausted);

    const char release = 'x';
    IOTOX_CHECK(::write(release_pipe[1], &release, 1U) == 1);
    static_cast<void>(::close(ready_pipe[0]));
    static_cast<void>(::close(release_pipe[1]));
    int status = 0;
    IOTOX_CHECK(::waitpid(child, &status, 0) == child);
    IOTOX_CHECK(WIFEXITED(status));
    IOTOX_CHECK(WEXITSTATUS(status) == 0);
}

IOTOX_TEST("Ratox incarnation state is identity-bound and tamper-evident") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";
    {
        auto lease = iotox::interactive::RatoxIncarnationLease::acquire(
            state, fixture.identity, fixture.sodium);
        IOTOX_CHECK_MSG(lease.ok(), lease.status().message());
    }

    auto bytes = read_bytes(state);
    IOTOX_CHECK(bytes.size() == 128U);
    bytes[50U] ^= 0x20U;
    write_private(state, bytes);
    auto tampered = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!tampered.ok());
    IOTOX_CHECK(tampered.status().code() == iotox::ErrorCode::protocol_error);

    write_private(state, signed_record(9U, fixture.identity));
    auto foreign = iotox::security::DeviceIdentity::load_or_create(
        fixture.temporary.path() / "foreign.identity", fixture.sodium, true);
    IOTOX_CHECK_MSG(foreign.ok(), foreign.status().message());
    auto wrong_identity = iotox::interactive::RatoxIncarnationLease::acquire(
        state, foreign.value(), fixture.sodium);
    IOTOX_CHECK(!wrong_identity.ok());
    IOTOX_CHECK(
        wrong_identity.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("Ratox incarnation lock refuses symlink substitution") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";
    const auto target = fixture.temporary.path() / "lock-target";
    write_private(target, {});
    IOTOX_CHECK(::symlink(
        target.c_str(), (state.string() + ".lock").c_str()) == 0);

    auto lease = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!lease.ok());
    IOTOX_CHECK(lease.status().code() == iotox::ErrorCode::io_error);
}

IOTOX_TEST("Ratox incarnation lane rejects noncanonical owner permission bits") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";
    {
        auto lease = iotox::interactive::RatoxIncarnationLease::acquire(
            state, fixture.identity, fixture.sodium);
        IOTOX_CHECK_MSG(lease.ok(), lease.status().message());
    }

    IOTOX_CHECK(::chmod(state.c_str(), 0700) == 0);
    auto executable_state = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!executable_state.ok());
    IOTOX_CHECK(::chmod(state.c_str(), 0600) == 0);

    const std::filesystem::path lock = state.string() + ".lock";
    IOTOX_CHECK(::chmod(lock.c_str(), 0700) == 0);
    auto executable_lock = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!executable_lock.ok());
    IOTOX_CHECK(::chmod(lock.c_str(), 0600) == 0);

    IOTOX_CHECK(::chmod(lane.c_str(), 01700) == 0);
    auto sticky_parent = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!sticky_parent.ok());
}

IOTOX_TEST("Ratox incarnation state refuses symlink and shared parent lanes") {
    Fixture fixture;
    const auto actual = fixture.temporary.path() / "actual";
    IOTOX_CHECK(std::filesystem::create_directory(actual));
    IOTOX_CHECK(::chmod(actual.c_str(), 0700) == 0);
    const auto alias = fixture.temporary.path() / "alias";
    IOTOX_CHECK(::symlink(actual.c_str(), alias.c_str()) == 0);
    auto through_symlink = iotox::interactive::RatoxIncarnationLease::acquire(
        alias / "incarnation.state", fixture.identity, fixture.sodium);
    IOTOX_CHECK(!through_symlink.ok());

    const auto shared = fixture.temporary.path() / "shared";
    IOTOX_CHECK(std::filesystem::create_directory(shared));
    IOTOX_CHECK(::chmod(shared.c_str(), 0750) == 0);
    auto shared_parent = iotox::interactive::RatoxIncarnationLease::acquire(
        shared / "incarnation.state", fixture.identity, fixture.sodium);
    IOTOX_CHECK(!shared_parent.ok());
}

IOTOX_TEST("Ratox incarnation lane creates nested private directories without following links") {
    Fixture fixture;
    const auto state =
        fixture.temporary.path() / "ratox" / "host" / "incarnation.state";
    auto lease = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK_MSG(lease.ok(), lease.status().message());
    IOTOX_CHECK(exact_mode(fixture.temporary.path() / "ratox") == 0700U);
    IOTOX_CHECK(exact_mode(fixture.temporary.path() / "ratox" / "host") == 0700U);
    IOTOX_CHECK(exact_mode(state) == 0600U);
}

IOTOX_TEST("Ratox incarnation lane rejects wraparound and state symlinks") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";
    write_private(
        state,
        signed_record(
            std::numeric_limits<std::uint64_t>::max(), fixture.identity));
    auto exhausted = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!exhausted.ok());
    IOTOX_CHECK(exhausted.status().code() == iotox::ErrorCode::resource_exhausted);

    std::filesystem::remove(state);
    const auto target = fixture.temporary.path() / "state-target";
    write_private(target, signed_record(5U, fixture.identity));
    IOTOX_CHECK(::symlink(target.c_str(), state.c_str()) == 0);
    auto symlink = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!symlink.ok());
}

IOTOX_TEST("Ratox incarnation state rejects hard links and malformed file shapes") {
    Fixture fixture;
    const auto lane = fixture.temporary.path() / "ratox";
    IOTOX_CHECK(std::filesystem::create_directory(lane));
    IOTOX_CHECK(::chmod(lane.c_str(), 0700) == 0);
    const auto state = lane / "incarnation.state";
    const auto alias = lane / "incarnation.alias";

    write_private(state, signed_record(7U, fixture.identity));
    IOTOX_CHECK(::link(state.c_str(), alias.c_str()) == 0);
    auto hard_linked = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!hard_linked.ok());
    IOTOX_CHECK(hard_linked.status().code() == iotox::ErrorCode::io_error);
    IOTOX_CHECK(std::filesystem::remove(alias));

    write_private(
        state,
        std::span<const std::uint8_t>(
            signed_record(8U, fixture.identity).data(), 127U));
    auto short_record = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!short_record.ok());
    IOTOX_CHECK(
        short_record.status().code() == iotox::ErrorCode::protocol_error);

    IOTOX_CHECK(std::filesystem::remove(state));
    IOTOX_CHECK(std::filesystem::create_directory(state));
    IOTOX_CHECK(::chmod(state.c_str(), 0600) == 0);
    auto directory_state = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium);
    IOTOX_CHECK(!directory_state.ok());
    IOTOX_CHECK(directory_state.status().code() == iotox::ErrorCode::io_error);
}

IOTOX_TEST("Ratox incarnation default path uses a dedicated savedata sibling lane") {
    const std::filesystem::path savedata = "/var/lib/iotox/device.toxsave";
    IOTOX_CHECK(
        iotox::interactive::default_ratox_incarnation_state_path(savedata) ==
        std::filesystem::path{"/var/lib/iotox/ratox/incarnation.state"});
    IOTOX_CHECK(
        iotox::interactive::default_ratox_incarnation_state_path("device.toxsave") ==
        std::filesystem::path{"./ratox/incarnation.state"});
    IOTOX_CHECK(
        iotox::interactive::default_ratox_incarnation_state_path({}).empty());
}

IOTOX_TEST("witnessed application and Ratox incarnations advance exact startup lanes") {
    Fixture fixture;
    for (const auto lane : {
             iotox::rollback_witness::Lane::application_incarnation,
             iotox::rollback_witness::Lane::ratox_incarnation}) {
        const std::string lane_name{
            iotox::rollback_witness::lane_name(lane)};
        const auto state = fixture.temporary.path() / lane_name /
            "incarnation.state";
        auto enrollment =
            iotox::interactive::incarnation_witness_enrollment_record(
                state, fixture.identity, fixture.sodium, witness_domain(),
                7U, lane);
        IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
        IOTOX_CHECK(enrollment.value().committed.position == 0U);
        IOTOX_CHECK(!enrollment.value().pending);
        auto backend = std::make_shared<MemoryIncarnationWitness>(
            enrollment.value());
        auto config = witnessed_config(state, backend, lane);

        auto first = iotox::interactive::RatoxIncarnationLease::acquire(
            state, fixture.identity, fixture.sodium, config);
        IOTOX_CHECK_MSG(first.ok(), first.status().message());
        IOTOX_CHECK(first.value().incarnation() == 1U);
        IOTOX_CHECK(backend->current().committed.position == 1U);
        IOTOX_CHECK(!backend->current().pending);
        IOTOX_CHECK(!std::filesystem::exists(config.intent_path));

        first.value().reset();
        auto second = iotox::interactive::RatoxIncarnationLease::acquire(
            state, fixture.identity, fixture.sodium, config);
        IOTOX_CHECK_MSG(second.ok(), second.status().message());
        IOTOX_CHECK(second.value().incarnation() == 2U);
        IOTOX_CHECK(backend->current().committed.position == 2U);
        IOTOX_CHECK(!backend->current().pending);
        IOTOX_CHECK(!std::filesystem::exists(config.intent_path));
    }
}

IOTOX_TEST("witnessed incarnation rejects a complete signed local rollback") {
    Fixture fixture;
    const auto state = fixture.temporary.path() / "application" /
        "incarnation.state";
    auto enrollment = iotox::interactive::incarnation_witness_enrollment_record(
        state, fixture.identity, fixture.sodium, witness_domain(), 7U,
        iotox::rollback_witness::Lane::application_incarnation);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    auto backend =
        std::make_shared<MemoryIncarnationWitness>(enrollment.value());
    auto config = witnessed_config(
        state, backend,
        iotox::rollback_witness::Lane::application_incarnation);

    auto first = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    const auto first_bytes = read_bytes(state);
    first.value().reset();
    auto second = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().incarnation() == 2U);
    second.value().reset();

    write_private(state, first_bytes);
    auto rolled_back = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK(!rolled_back.ok());
    IOTOX_CHECK(
        rolled_back.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(backend->current().committed.position == 2U);
    IOTOX_CHECK(!backend->current().pending);
}

IOTOX_TEST("witnessed incarnation completes an interrupted pending transition") {
    Fixture fixture;
    const auto state = fixture.temporary.path() / "ratox" /
        "incarnation.state";
    auto enrollment = iotox::interactive::incarnation_witness_enrollment_record(
        state, fixture.identity, fixture.sodium, witness_domain(), 7U,
        iotox::rollback_witness::Lane::ratox_incarnation);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    auto backend =
        std::make_shared<MemoryIncarnationWitness>(enrollment.value());
    auto config = witnessed_config(
        state, backend, iotox::rollback_witness::Lane::ratox_incarnation);

    // The first CAS installs pending. The second is the external final commit;
    // fail it and its resolving query after the local record is durable.
    backend->fail_before_cas(2U);
    auto interrupted = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(
        interrupted.status().code() == iotox::ErrorCode::unavailable);
    IOTOX_CHECK(backend->current().committed.position == 0U);
    IOTOX_CHECK(backend->current().pending.has_value());
    IOTOX_CHECK(backend->current().pending->position == 1U);
    IOTOX_CHECK(std::filesystem::exists(config.intent_path));

    auto recovered = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    // Recovery finishes position one, then this fresh process start consumes
    // the next namespace before exposing a lease.
    IOTOX_CHECK(recovered.value().incarnation() == 2U);
    IOTOX_CHECK(backend->current().committed.position == 2U);
    IOTOX_CHECK(!backend->current().pending);
    IOTOX_CHECK(!std::filesystem::exists(config.intent_path));
}

IOTOX_TEST("incarnation witness refuses a same-host backend outside tests") {
    Fixture fixture;
    const auto state = fixture.temporary.path() / "application" /
        "incarnation.state";
    auto enrollment = iotox::interactive::incarnation_witness_enrollment_record(
        state, fixture.identity, fixture.sodium, witness_domain(), 7U,
        iotox::rollback_witness::Lane::application_incarnation);
    IOTOX_CHECK_MSG(enrollment.ok(), enrollment.status().message());
    auto backend =
        std::make_shared<MemoryIncarnationWitness>(enrollment.value());
    auto config = witnessed_config(
        state, backend,
        iotox::rollback_witness::Lane::application_incarnation);
    config.allow_non_independent_for_testing = false;
    auto refused = iotox::interactive::RatoxIncarnationLease::acquire(
        state, fixture.identity, fixture.sodium, config);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(
        refused.status().code() == iotox::ErrorCode::invalid_argument);
    IOTOX_CHECK(!std::filesystem::exists(state));
}
