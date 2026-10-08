#include "sync_replica_deployment_manifest.hpp"

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
            ("anonsync-deployment-manifest-" + std::to_string(tick));
        fs::create_directory(path_);
#if !defined(_WIN32)
        if (::chmod(path_.c_str(), 0700) != 0) {
            fail("could not make deployment-manifest test root private");
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
            fail("could not make deployment-manifest fixture private");
        }
#endif
        return result;
    }

private:
    fs::path path_;
};

void write_bytes(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) fail("could not create deployment-manifest fixture");
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) fail("could not finish deployment-manifest fixture");
#if !defined(_WIN32)
    if (::chmod(path.c_str(), 0600) != 0) {
        fail("could not make deployment-manifest fixture private");
    }
#endif
}

[[nodiscard]] std::string replace_once(
    std::string text,
    std::string_view before,
    std::string_view after) {
    const std::size_t position = text.find(before);
    if (position == std::string::npos ||
        text.find(before, position + before.size()) != std::string::npos) {
        fail("deployment-manifest fixture replacement is not unique");
    }
    text.replace(position, before.size(), after);
    return text;
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest sender_manifest(
    const TemporaryDirectory& temporary,
    const fs::path& manifest_path) {
    anonsync::SyncReplicaDeploymentManifest manifest;
    manifest.deployment_id = std::string(64U, 'a');
    manifest.manifest_path = manifest_path;
    manifest.replica_db = temporary.path() / "sender-replica.sqlite";
    manifest.payload_root = temporary.make_directory("sender-payloads");
    manifest.folder_id = "folder-alpha";
    manifest.local_actor = {"sender-alpha", 7U};
    manifest.max_payload_bytes = 4U * 1024U * 1024U;
    return manifest;
}

[[nodiscard]] anonsync::SyncReplicaDeploymentManifest receiver_manifest(
    const TemporaryDirectory& temporary,
    const fs::path& manifest_path) {
    anonsync::SyncReplicaDeploymentManifest manifest;
    manifest.deployment_id = std::string(64U, 'b');
    manifest.manifest_path = manifest_path;
    manifest.replica_db = temporary.path() / "receiver-replica.sqlite";
    manifest.effect_db = temporary.path() / "receiver-effect.sqlite";
    manifest.files_root = temporary.make_directory("receiver-files");
    manifest.membership_db =
        temporary.path() / "receiver-membership.sqlite";
    manifest.anchor_db = temporary.path() / "receiver-anchor.sqlite";
    manifest.folder_id = "folder-alpha";
    manifest.local_actor = {"receiver-alpha", 9U};
    manifest.max_payload_bytes = 8U * 1024U * 1024U;
    return manifest;
}

void test_round_trip(const TemporaryDirectory& temporary) {
    const fs::path path = temporary.path() / "sender.json";
    const auto manifest = sender_manifest(temporary, path);
    const std::string exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            manifest, "sender fixture");
    write_bytes(path, exact);

    const auto decoded =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            path, "sender fixture");
    require(decoded.deployment_id == manifest.deployment_id &&
                decoded.manifest_path == path &&
                decoded.replica_db == manifest.replica_db &&
                decoded.payload_root == manifest.payload_root &&
                decoded.folder_id == manifest.folder_id &&
                decoded.local_actor == manifest.local_actor &&
                decoded.max_payload_bytes == manifest.max_payload_bytes,
            "exact decoding preserves the complete sender authority");
    require(decoded.manifest_digest.size() == 64U,
            "exact decoding publishes the manifest self-digest");
    const auto identity =
        anonsync::sync_replica_deployment_identity_or_throw(
            decoded, "sender decoded identity");
    require(identity.deployment_id == decoded.deployment_id &&
                identity.manifest_digest == decoded.manifest_digest &&
                identity.manifest_path == decoded.manifest_path,
            "decoded manifest derives one exact store-set identity");
    require(anonsync::encode_sync_replica_deployment_manifest_or_throw(
                decoded, "sender round trip") == exact,
            "decoded authority re-encodes to byte-identical canonical JSON");
    require(std::string(anonsync::sync_replica_deployment_profile_name(
                decoded)) == "sender" &&
                anonsync::sync_replica_deployment_authority_resource_count(
                    decoded) == 2U,
            "sender profile and selected-resource accounting are exact");
}

void test_exact_byte_decoder(const TemporaryDirectory& temporary) {
    const fs::path final_path = temporary.path() / "staged-final.json";
    const auto manifest = sender_manifest(temporary, final_path);
    const std::string exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            manifest, "staged decoder source");

    const auto decoded =
        anonsync::decode_sync_replica_deployment_manifest_or_throw(
            exact, final_path, "staged decoder fixture");
    require(decoded.manifest_path == final_path &&
                decoded.deployment_id == manifest.deployment_id &&
                decoded.manifest_digest.size() == 64U,
            "exact bytes can be decoded against their selected final pathname");

    require_error(
        [&] {
            (void)anonsync::decode_sync_replica_deployment_manifest_or_throw(
                exact, temporary.path() / "different-final.json",
                "staged decoder copied fixture");
        },
        "manifest_path does not bind the expected final file name",
        "the byte decoder cannot redirect staged authority to another final name");

    require_error(
        [&] {
            (void)anonsync::decode_sync_replica_deployment_manifest_or_throw(
                std::string(
                    static_cast<std::size_t>(
                        anonsync::kSyncReplicaDeploymentManifestMaxBytes + 1U),
                    'x'),
                final_path, "staged decoder oversized fixture");
        },
        "exceed the deployment-manifest read ceiling",
        "direct staged bytes retain the operational manifest size ceiling");
}

void test_receiver_profile(const TemporaryDirectory& temporary) {
    const fs::path path = temporary.path() / "receiver.json";
    const auto manifest = receiver_manifest(temporary, path);
    require(std::string(anonsync::sync_replica_deployment_profile_name(
                manifest)) == "receiver" &&
                anonsync::sync_replica_deployment_authority_resource_count(
                    manifest) == 5U,
            "receiver profile counts replica, effect pair, and membership pair");
    const std::string exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            manifest, "receiver fixture");
    write_bytes(path, exact);
    const auto decoded =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            path, "receiver fixture");
    require(decoded.effect_db == manifest.effect_db &&
                decoded.files_root == manifest.files_root &&
                decoded.membership_db == manifest.membership_db &&
                decoded.anchor_db == manifest.anchor_db,
            "receiver capability pairs survive exact decoding");
}

void test_exact_document_rejections(const TemporaryDirectory& temporary) {
    const fs::path source_path = temporary.path() / "copy-source.json";
    const auto source_manifest = sender_manifest(temporary, source_path);
    const std::string source_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            source_manifest, "copy source");
    write_bytes(source_path, source_exact);

    const fs::path copied_path = temporary.path() / "copied.json";
    write_bytes(copied_path, source_exact);
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                copied_path, "copied manifest");
        },
        "manifest_path does not bind the opened file name",
        "copying exact bytes to another pathname cannot duplicate authority");

    const fs::path tampered_path = temporary.path() / "tampered.json";
    auto tampered_manifest = sender_manifest(temporary, tampered_path);
    const std::string tampered_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            tampered_manifest, "tampered source");
    write_bytes(
        tampered_path,
        replace_once(tampered_exact, "folder-alpha", "folder-bravo"));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                tampered_path, "tampered manifest");
        },
        "canonical fields, or self-digest conflict",
        "field mutation without recomputing the digest is rejected");

    const fs::path unknown_path = temporary.path() / "unknown.json";
    auto unknown_manifest = sender_manifest(temporary, unknown_path);
    const std::string unknown_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            unknown_manifest, "unknown source");
    write_bytes(
        unknown_path,
        replace_once(
            unknown_exact,
            ",\"manifest_digest\":",
            ",\"unexpected\":true,\"manifest_digest\":"));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                unknown_path, "unknown field manifest");
        },
        "unknown field unexpected",
        "unknown fields cannot acquire future authority by parser tolerance");

    const fs::path missing_path = temporary.path() / "missing.json";
    auto missing_manifest = sender_manifest(temporary, missing_path);
    const std::string missing_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            missing_manifest, "missing source");
    write_bytes(
        missing_path,
        replace_once(
            missing_exact,
            ",\"cross_resource_atomicity\":false",
            ""));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                missing_path, "missing field manifest");
        },
        "missing field cross_resource_atomicity",
        "every authority-policy field is mandatory");

    const fs::path policy_path = temporary.path() / "policy.json";
    auto policy_manifest = sender_manifest(temporary, policy_path);
    const std::string policy_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            policy_manifest, "policy source");
    write_bytes(
        policy_path,
        replace_once(
            policy_exact,
            "\"operational_database_open_policy\":\"existing-only\"",
            "\"operational_database_open_policy\":\"create-if-missing\""));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                policy_path, "unsupported policy manifest");
        },
        "unsupported authority policy",
        "a manifest cannot opt operational code back into creation authority");

    const fs::path whitespace_path = temporary.path() / "whitespace.json";
    auto whitespace_manifest = sender_manifest(temporary, whitespace_path);
    const std::string whitespace_exact =
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            whitespace_manifest, "whitespace source");
    write_bytes(
        whitespace_path,
        replace_once(whitespace_exact, "{\"format\"", "{ \"format\""));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                whitespace_path, "noncanonical manifest");
        },
        "exact bytes, canonical fields, or self-digest conflict",
        "semantically equivalent noncanonical bytes are not the same authority");
}

void test_path_and_bound_rejections(const TemporaryDirectory& temporary) {
    const fs::path payload_root = temporary.make_directory("overlap-payloads");
    anonsync::SyncReplicaDeploymentManifest overlap;
    overlap.deployment_id = std::string(64U, 'c');
    overlap.manifest_path = payload_root / "manifest.json";
    overlap.replica_db = temporary.path() / "overlap.sqlite";
    overlap.payload_root = payload_root;
    overlap.folder_id = "folder-alpha";
    overlap.local_actor = {"sender-alpha", 1U};
    overlap.max_payload_bytes = 4096U;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                overlap, "overlap manifest");
        },
        "manifest_path must not be inside payload_root",
        "the commit marker cannot live inside a mutable selected root");

    auto sidecar_database_collision = overlap;
    sidecar_database_collision.manifest_path =
        temporary.path() / "sidecar-database-collision.json";
    sidecar_database_collision.payload_root.reset();
    sidecar_database_collision.effect_db = fs::path(
        sidecar_database_collision.replica_db.generic_string() + "-wal");
    sidecar_database_collision.files_root =
        temporary.path() / "sidecar-collision-files";
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                sidecar_database_collision,
                "sidecar database collision manifest");
        },
        "collide in a SQLite main/sidecar path family",
        "a database cannot occupy another selected database's WAL name");

    auto sidecar_manifest_collision = overlap;
    sidecar_manifest_collision.payload_root.reset();
    sidecar_manifest_collision.manifest_path = fs::path(
        sidecar_manifest_collision.replica_db.generic_string() + "-shm");
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                sidecar_manifest_collision,
                "sidecar manifest collision manifest");
        },
        "collide in a SQLite main/sidecar path family",
        "the commit marker cannot occupy a selected database's SHM name");

    auto sidecar_root_collision = overlap;
    sidecar_root_collision.manifest_path =
        temporary.path() / "sidecar-root-collision.json";
    sidecar_root_collision.payload_root = fs::path(
        sidecar_root_collision.replica_db.generic_string() + "-journal");
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                sidecar_root_collision, "sidecar root collision manifest");
        },
        "SQLite sidecar -journal must not be inside payload_root",
        "a mutable root cannot occupy a selected database's journal name");

#if !defined(_WIN32)
    auto embedded_nul = overlap;
    embedded_nul.manifest_path = temporary.path() / "embedded-nul.json";
    embedded_nul.payload_root.reset();
    std::string nul_path = temporary.path().generic_string() + "/replica";
    nul_path.push_back('\0');
    nul_path += "-shadow.sqlite";
    embedded_nul.replica_db = fs::path(nul_path);
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                embedded_nul, "embedded NUL manifest");
        },
        "replica_db must not contain NUL",
        "a path cannot validate beyond the name seen by filesystem APIs");
#endif

    auto invalid_deployment_id = overlap;
    invalid_deployment_id.manifest_path =
        temporary.path() / "invalid-deployment-id.json";
    invalid_deployment_id.payload_root.reset();
    invalid_deployment_id.deployment_id = std::string(63U, 'd');
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                invalid_deployment_id, "invalid deployment ID manifest");
        },
        "deployment_id must be 64 lowercase hexadecimal characters",
        "store-set identity has one exact random-ID encoding");

    auto unsafe_epoch = overlap;
    unsafe_epoch.manifest_path = temporary.path() / "unsafe-epoch.json";
    unsafe_epoch.payload_root.reset();
    unsafe_epoch.local_actor.epoch = 9007199254740992ULL;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                unsafe_epoch, "unsafe epoch manifest");
        },
        "exceeds exact JSON integer range",
        "epochs outside interoperable exact JSON range are rejected");

    auto oversized_output = unsafe_epoch;
    oversized_output.local_actor.epoch = 1U;
    oversized_output.manifest_path = temporary.path() / "oversized-output.json";
    oversized_output.replica_db = temporary.path() /
        std::string(
            static_cast<std::size_t>(
                anonsync::kSyncReplicaDeploymentManifestMaxBytes),
            'r');
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                oversized_output, "oversized output manifest");
        },
        "encoded bytes exceed the deployment-manifest read ceiling",
        "bootstrap cannot publish a manifest operational code cannot read");

#if !defined(_WIN32)
    auto malformed_utf8 = unsafe_epoch;
    malformed_utf8.local_actor.epoch = 1U;
    malformed_utf8.manifest_path = temporary.path() / "malformed-utf8.json";
    std::string malformed_path = temporary.path().generic_string() + "/";
    malformed_path.append("\xC0\xAF", 2U);
    malformed_utf8.replica_db = fs::path(malformed_path);
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_deployment_manifest_or_throw(
                malformed_utf8, "malformed UTF-8 manifest");
        },
        "cannot be encoded as strict UTF-8 JSON",
        "bootstrap rejects path bytes the operational JSON reader rejects");
#endif

    const fs::path oversized_path = temporary.path() / "oversized.json";
    write_bytes(
        oversized_path,
        std::string(
            static_cast<std::size_t>(
                anonsync::kSyncReplicaDeploymentManifestMaxBytes + 1U),
            'x'));
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                oversized_path, "oversized manifest");
        },
        "exceeds bounded read limit",
        "manifest input is bounded before JSON allocation");

    const fs::path target_path = temporary.path() / "symlink-target.json";
    auto target_manifest = sender_manifest(temporary, target_path);
    write_bytes(
        target_path,
        anonsync::encode_sync_replica_deployment_manifest_or_throw(
            target_manifest, "symlink source"));
    const fs::path link_path = temporary.path() / "symlink.json";
    std::error_code link_error;
    fs::create_symlink(target_path.filename(), link_path, link_error);
    if (!link_error) {
        require_error(
            [&] {
                (void)anonsync::read_sync_replica_deployment_manifest_or_throw(
                    link_path, "symlink manifest");
            },
            "open failed",
            "the final manifest path cannot be a symbolic link");
    } else {
        std::cout << "SKIP: symbolic-link creation unavailable: "
                  << link_error.message() << "\n";
    }
}

}  // namespace

int main() {
    try {
        TemporaryDirectory temporary;
        test_round_trip(temporary);
        test_exact_byte_decoder(temporary);
        test_receiver_profile(temporary);
        test_exact_document_rejections(temporary);
        test_path_and_bound_rejections(temporary);
        std::cout << "PASS: sync replica deployment manifest checks="
                  << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << "\n";
        return 1;
    }
}
