#include "sync_replica_folder_process.hpp"

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace {

namespace fs = std::filesystem;
std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest manifest() {
    anonsync::SyncReplicaDeploymentManifest value{
        .deployment_id = std::string(64U, 'a'),
        .manifest_path = "/var/lib/anonsync/deployment.json",
        .replica_db = "/var/lib/anonsync/replica.sqlite",
        .payload_root = "/var/lib/anonsync/payload",
        .effect_db = "/var/lib/anonsync/effect.sqlite",
        .files_root = "/srv/anonsync/files",
        .membership_db = std::nullopt,
        .anchor_db = std::nullopt,
        .folder_id = "folder-alpha",
        .local_actor = {"device-alpha", 9U},
        .max_payload_bytes = 16U * 1024U * 1024U,
        .manifest_digest = {},
    };
    value.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            value, "folder-process test manifest");
    return value;
}

void test_deterministic_path_and_bindings() {
    const auto deployment = manifest();
    anonsync::validate_sync_replica_folder_process_deployment_or_throw(
        deployment, "folder-process test");
    const fs::path expected =
        "/var/lib/anonsync/replica.sqlite.folder-catalog.sqlite3";
    require(
        anonsync::sync_replica_folder_catalog_path_or_throw(
            deployment, "folder-process path") == expected,
        "folder catalog path is not deterministic beside replica_db");

    const auto catalog =
        anonsync::sync_replica_folder_catalog_binding_or_throw(
            deployment, "folder-process catalog binding");
    require(
        catalog.role ==
            anonsync::SyncReplicaSqliteDeploymentRole::FolderCatalog &&
            catalog.database_path == expected &&
            catalog.deployment.deployment_id == deployment.deployment_id &&
            catalog.deployment.manifest_digest ==
                deployment.manifest_digest,
        "folder catalog binding does not carry the exact deployment");

    const auto replica =
        anonsync::sync_replica_primary_database_binding_or_throw(
            deployment, "folder-process replica binding");
    require(
        replica.role == anonsync::SyncReplicaSqliteDeploymentRole::Replica &&
            replica.database_path == deployment.replica_db,
        "replica binding does not carry the exact selected role path");

    const auto payload_limits =
        anonsync::sync_replica_folder_payload_store_limits_or_throw(
            deployment, "folder-process payload limits");
    const auto catalog_limits =
        anonsync::sync_replica_folder_catalog_limits_or_throw(
            deployment, "folder-process catalog limits");
    require(
        payload_limits.max_payload_bytes == deployment.max_payload_bytes &&
            catalog_limits.max_payload_bytes == deployment.max_payload_bytes,
        "folder process limits are not bounded by the manifest payload ceiling");
}

void test_required_roles_and_namespace_collision() {
    auto sender = manifest();
    sender.effect_db.reset();
    sender.files_root.reset();
    sender.manifest_digest.clear();
    sender.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            sender, "folder-process sender manifest");
    require_error(
        [&] {
            anonsync::validate_sync_replica_folder_process_deployment_or_throw(
                sender, "folder-process sender rejection");
        },
        "requires files_root",
        "a deployment without a configured folder root was accepted");

    auto receiver = manifest();
    receiver.payload_root.reset();
    receiver.manifest_digest.clear();
    receiver.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            receiver, "folder-process receiver manifest");
    require_error(
        [&] {
            anonsync::validate_sync_replica_folder_process_deployment_or_throw(
                receiver, "folder-process receiver rejection");
        },
        "requires payload_root",
        "a deployment without durable payload authority was accepted");

    auto collision = manifest();
    collision.effect_db =
        fs::path(collision.replica_db.string() +
                 ".folder-catalog.sqlite3");
    collision.manifest_digest.clear();
    collision.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            collision, "folder-process collision manifest");
    require_error(
        [&] {
            (void)anonsync::sync_replica_folder_catalog_path_or_throw(
                collision, "folder-process collision rejection");
        },
        "collides with effect_db",
        "a derived catalog path colliding with a selected store was accepted");
}

}  // namespace

int main() {
    try {
        test_deterministic_path_and_bindings();
        test_required_roles_and_namespace_collision();
        std::cout << "sync replica folder-process tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica folder-process tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
