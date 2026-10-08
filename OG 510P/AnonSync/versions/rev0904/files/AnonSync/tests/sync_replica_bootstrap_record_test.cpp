#include "sync_replica_bootstrap_record.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#if !defined(_WIN32)
#include <sys/stat.h>
#endif

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

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
            ("anonsync-bootstrap-record-" + std::to_string(tick));
        fs::create_directory(path_);
#if !defined(_WIN32)
        if (::chmod(path_.c_str(), 0700) != 0) {
            fail("could not make bootstrap-record test root private");
        }
#endif
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

    [[nodiscard]] fs::path make_directory(std::string_view name) const {
        const fs::path result = path_ / std::string(name);
        fs::create_directory(result);
#if !defined(_WIN32)
        if (::chmod(result.c_str(), 0700) != 0) {
            fail("could not make bootstrap-record fixture private");
        }
#endif
        return result;
    }

private:
    fs::path path_;
};

void write_bytes(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) fail("could not create bootstrap-record fixture");
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) fail("could not finish bootstrap-record fixture");
#if !defined(_WIN32)
    if (::chmod(path.c_str(), 0600) != 0) {
        fail("could not make bootstrap-record fixture private");
    }
#endif
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest make_manifest(
    const TemporaryDirectory& temporary,
    const fs::path& manifest_path,
    char deployment_nibble = 'a') {
    anonsync::SyncReplicaDeploymentManifest deployment;
    deployment.deployment_id = std::string(64U, deployment_nibble);
    deployment.manifest_path = manifest_path;
    deployment.replica_db = temporary.path() /
        ("replica-" + std::string(1U, deployment_nibble) + ".sqlite");
    deployment.payload_root = temporary.make_directory(
        "payload-" + std::string(1U, deployment_nibble));
    deployment.folder_id = "folder-alpha";
    deployment.local_actor = {"device-alpha", 3U};
    deployment.max_payload_bytes = 4U * 1024U * 1024U;
    deployment.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            deployment, "bootstrap-record fixture digest");
    return deployment;
}

void test_path_and_exact_round_trip() {
    TemporaryDirectory temporary;
    const fs::path manifest_path = temporary.path() / "deployment.json";
    const auto deployment = make_manifest(temporary, manifest_path);

    const fs::path first =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            manifest_path, "bootstrap-record path fixture");
    const fs::path second =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            manifest_path, "bootstrap-record repeated path fixture");
    require(first == second && first.parent_path() == manifest_path.parent_path(),
            "bootstrap-record pathname derivation is deterministic and adjacent");
    require(first.filename().string().starts_with(
                ".anonsync-replica-bootstrap-") &&
                first.filename().string().ends_with(".json") &&
                first.filename().string().size() == 97U,
            "bootstrap-record basename is fixed-length and recognizable");

    const anonsync::SyncReplicaBootstrapRecord created =
        anonsync::create_sync_replica_bootstrap_record_or_throw(
            deployment, "bootstrap-record create fixture");
    require(created.record_path == first,
            "created record occupies the deterministic path");
    require(created.deployment.deployment_id == deployment.deployment_id &&
                created.deployment.manifest_path == manifest_path &&
                created.deployment.manifest_digest ==
                    deployment.manifest_digest,
            "record decodes the exact final deployment authority");
    require(created.exact_manifest_bytes ==
                anonsync::encode_sync_replica_deployment_manifest_or_throw(
                    deployment, "bootstrap-record exact fixture"),
            "record bytes are exactly the final canonical manifest bytes");
#if !defined(_WIN32)
    struct stat status{};
    if (::stat(first.c_str(), &status) != 0) {
        fail("could not stat created bootstrap record");
    }
    require((status.st_mode & 0777) == 0600,
            "created bootstrap record is private mode 0600");
#endif

    const auto reread = anonsync::read_sync_replica_bootstrap_record_or_throw(
        manifest_path, "bootstrap-record reread fixture");
    require(reread.exact_manifest_bytes == created.exact_manifest_bytes,
            "bounded record reread preserves exact bytes");
    anonsync::attest_sync_replica_bootstrap_record_unchanged_or_throw(
        created, "bootstrap-record unchanged fixture");

    require_error(
        [&] {
            (void)anonsync::create_sync_replica_bootstrap_record_or_throw(
                deployment, "bootstrap-record duplicate fixture");
        },
        "exists",
        "create-new publication refuses to adopt an existing record");
}

void test_copy_tamper_and_namespace_rejections() {
    TemporaryDirectory temporary;
    const fs::path source_manifest = temporary.path() / "source.json";
    const auto source = make_manifest(temporary, source_manifest, 'b');
    const std::string exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            source, "bootstrap-record source exact");

    const fs::path copied_manifest = temporary.path() / "copied.json";
    const fs::path copied_record =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            copied_manifest, "bootstrap-record copied path");
    write_bytes(copied_record, exact);
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_bootstrap_record_or_throw(
                copied_manifest, "bootstrap-record copied fixture");
        },
        "manifest_path does not bind the expected final file name",
        "copying a record cannot redirect its final manifest authority");

    const fs::path tampered_manifest = temporary.path() / "tampered.json";
    auto tampered = make_manifest(temporary, tampered_manifest, 'c');
    std::string tampered_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            tampered, "bootstrap-record tamper source");
    const std::size_t position = tampered_exact.find("folder-alpha");
    if (position == std::string::npos) fail("tamper fixture field missing");
    tampered_exact.replace(position, 12U, "folder-bravo");
    write_bytes(
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            tampered_manifest, "bootstrap-record tampered path"),
        tampered_exact);
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_bootstrap_record_or_throw(
                tampered_manifest, "bootstrap-record tampered fixture");
        },
        "canonical fields, or self-digest conflict",
        "record field tampering without a new self-digest is rejected");

    const fs::path collision_manifest = temporary.path() / "collision.json";
    auto collision = make_manifest(temporary, collision_manifest, 'd');
    collision.replica_db =
        anonsync::sync_replica_bootstrap_record_path_or_throw(
            collision_manifest, "bootstrap-record collision path");
    collision.manifest_digest.clear();
    collision.manifest_digest =
        anonsync::compute_sync_replica_deployment_manifest_digest_or_throw(
            collision, "bootstrap-record collision digest");
    require_error(
        [&] {
            anonsync::validate_sync_replica_bootstrap_record_namespace_or_throw(
                collision, "bootstrap-record collision fixture");
        },
        "collides with replica_db",
        "deterministic record namespace cannot alias a selected database");
}

}  // namespace

int main() {
    try {
        test_path_and_exact_round_trip();
        test_copy_tamper_and_namespace_rejections();
        std::cout << "sync replica bootstrap record tests passed (" << checks
                  << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica bootstrap record test failed after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}
