#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_health.hpp"

#include <cstdlib>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <unistd.h>

namespace {

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-health-XXXXXX";
        char *created = ::mkdtemp(pattern.data());
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
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

iotox::security::Sodium sodium() {
    const char *library = std::getenv("IOTOX_TEST_SODIUM");
    auto result = iotox::security::Sodium::load(
        library == nullptr ? "" : library);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    return std::move(result).value();
}

iotox::security::DeviceIdentity identity(
    const std::filesystem::path &path, const iotox::security::Sodium &crypto) {
    auto result = iotox::security::DeviceIdentity::load_or_create(
        path, crypto, true);
    IOTOX_CHECK_MSG(result.ok(), result.status().message());
    return std::move(result).value();
}

iotox::sync::NamespacePolicy policy(
    const std::filesystem::path &root,
    const iotox::security::SigningPublicKey &device) {
    iotox::sync::NamespacePolicy result;
    result.id = "health-tree";
    result.root = root.lexically_normal().string();
    result.engine = iotox::sync::Engine::tree_v2;
    result.activation = iotox::sync::ActivationMode::manual;
    result.writers = {device};
    result.subscribers = {device};
    return result;
}

iotox::sync::NamespaceHealthObservation green_observation() {
    iotox::sync::NamespaceHealthObservation result;
    result.observed_unix_ms = 1000U;
    result.namespace_commitment.fill(0x11U);
    result.policy_commitment.fill(0x22U);
    result.flags = iotox::sync::kHealthPolicyVerified |
                   iotox::sync::kHealthMembershipVerified |
                   iotox::sync::kHealthFrontierVerified |
                   iotox::sync::kHealthMaintenanceVerified |
                   iotox::sync::kHealthWorkspacePresent |
                   iotox::sync::kHealthWorkspaceStable |
                   iotox::sync::kHealthWorkspaceCurrent |
                   iotox::sync::kHealthWorktreeClean |
                   iotox::sync::kHealthSelectedCoverageComplete |
                   iotox::sync::kHealthCustodyComplete |
                   iotox::sync::kHealthAutomationConfigured |
                   iotox::sync::kHealthSourceObserved;
    result.frontier_writers = 1U;
    result.namespace_writers = 1U;
    result.subscribers = 1U;
    result.desired_objects = 2U;
    result.verified_objects = 2U;
    result.desired_bytes = 30U;
    result.verified_bytes = 30U;
    result.store_bytes = 400U;
    result.store_limit_bytes = 1000U;
    result.source_count = 2U;
    return result;
}

} // namespace

IOTOX_TEST("namespace health classifies expected sparse custody independently") {
    auto observation = green_observation();
    observation.flags &= ~iotox::sync::kHealthCustodyComplete;
    auto green = iotox::sync::classify_namespace_health(observation);
    IOTOX_CHECK(green.ok());
    IOTOX_CHECK(green.value() == iotox::sync::NamespaceHealthLevel::green);

    observation.conflicts = 1U;
    auto yellow = iotox::sync::classify_namespace_health(observation);
    IOTOX_CHECK(yellow.ok());
    IOTOX_CHECK(yellow.value() ==
                iotox::sync::NamespaceHealthLevel::yellow);
    observation.conflicts = 0U;
    observation.verified_objects = 1U;
    observation.missing_objects = 1U;
    observation.flags &= ~iotox::sync::kHealthSelectedCoverageComplete;
    auto red = iotox::sync::classify_namespace_health(observation);
    IOTOX_CHECK(red.ok());
    IOTOX_CHECK(red.value() == iotox::sync::NamespaceHealthLevel::red);
}

IOTOX_TEST("namespace health record is signed durable and policy aware") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    auto configured = policy(temporary.path() / "namespace", device.public_key());
    auto first = iotox::sync::commit_namespace_health(
        configured, green_observation(), device, crypto);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(first.value().sequence == 1U);
    IOTOX_CHECK(first.value().level ==
                iotox::sync::NamespaceHealthLevel::green);
    IOTOX_CHECK(iotox::sync::namespace_health_policy_current(
        configured, first.value(), crypto));

    auto loaded = iotox::sync::load_namespace_health(
        configured, device.public_key(), crypto);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value() == first.value());

    auto changed = configured;
    changed.quotas.maximum_store_bytes += 1U;
    IOTOX_CHECK(!iotox::sync::namespace_health_policy_current(
        changed, loaded.value(), crypto));
    auto second_observation = green_observation();
    second_observation.observed_unix_ms = 2000U;
    auto second = iotox::sync::commit_namespace_health(
        changed, second_observation, device, crypto);
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().sequence == 2U);
    IOTOX_CHECK(iotox::sync::namespace_health_policy_current(
        changed, second.value(), crypto));

    auto bytes = iotox::StateStore::read(
        iotox::sync::namespace_health_path(changed));
    IOTOX_CHECK(bytes.ok() && !bytes.value().empty());
    bytes.value()[160U] ^= 0x01U;
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    iotox::sync::namespace_health_path(changed),
                    bytes.value())
                    .ok());
    auto tampered = iotox::sync::load_namespace_health(
        changed, device.public_key(), crypto);
    IOTOX_CHECK(!tampered.ok());
    IOTOX_CHECK(tampered.status().code() == iotox::ErrorCode::protocol_error);
}
