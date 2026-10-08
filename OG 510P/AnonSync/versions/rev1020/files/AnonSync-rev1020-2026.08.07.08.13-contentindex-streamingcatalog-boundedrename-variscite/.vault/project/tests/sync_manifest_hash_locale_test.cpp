#include "anonsync_core.hpp"
#include "sha256_digest.hpp"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>

namespace {

namespace fs = std::filesystem;

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

struct GroupEveryDigit final : std::numpunct<char> {
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\1"; }
};

class GlobalLocaleRestore final {
public:
    GlobalLocaleRestore() : previous_(std::locale()) {}
    ~GlobalLocaleRestore() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

class TempTree final {
public:
    TempTree() {
        const auto ticks = std::chrono::steady_clock::now()
                               .time_since_epoch()
                               .count();
        root_ = fs::temp_directory_path() /
                ("anonsync-manifest-locale-" + std::to_string(ticks));
        source_ = root_ / "source";
        destination_ = root_ / "destination";
        staging_ = root_ / "staging";
        fs::create_directories(source_ / "nested");
        fs::create_directories(destination_);
        fs::create_directories(staging_);
    }

    ~TempTree() {
        std::error_code ec;
        fs::remove_all(root_, ec);
    }

    [[nodiscard]] const fs::path& source() const noexcept { return source_; }
    [[nodiscard]] const fs::path& destination() const noexcept {
        return destination_;
    }
    [[nodiscard]] const fs::path& staging() const noexcept { return staging_; }

private:
    fs::path root_;
    fs::path source_;
    fs::path destination_;
    fs::path staging_;
};

void write_binary(const fs::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("could not create locale test file");
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!out) throw std::runtime_error("could not write locale test file");
}

}  // namespace

int main() {
    try {
        using namespace anonsync;
        int checks = 0;
        TempTree tree;
        const std::string bytes("\x00\xfflocale-sensitive\x7f\x80tail", 24);
        write_binary(tree.source() / "nested" / "payload.bin", bytes);

        SyncFolderScanOptions scan;
        scan.root_path = tree.source().generic_string();
        scan.folder_id = "folder-alpha";
        scan.device_id = "device-alpha";
        scan.manifest_counter = 9;
        scan.lineage_counter = 11;
        scan.chunk_size_bytes = 5;

        SyncFolderManifest classic_manifest;
        const SyncValidationResult classic_result =
            build_sync_folder_manifest_from_directory(scan, classic_manifest);
        require(classic_result.ok, "classic-locale scan must succeed", checks);
        require(classic_manifest.entries.size() == 1,
                "scan must produce one file entry", checks);
        require(classic_manifest.entries.front().content_sha256 ==
                    sha256_hex(bytes),
                "scan content hash must match canonical SHA-256", checks);
        require(classic_manifest.entries.front().chunks.size() == 5,
                "scan must preserve configured chunk boundaries", checks);
        const std::string classic_manifest_digest =
            sync_folder_manifest_digest(classic_manifest);

        {
            GlobalLocaleRestore restore;
            std::locale::global(std::locale(
                std::locale::classic(), new GroupEveryDigit));

            SyncFolderManifest hostile_manifest;
            const SyncValidationResult hostile_result =
                build_sync_folder_manifest_from_directory(scan, hostile_manifest);
            require(hostile_result.ok,
                    "hostile grouping locale must not corrupt digest text: " +
                        hostile_result.reason,
                    checks);
            require(hostile_manifest.entries.front().content_sha256 ==
                        sha256_hex(bytes),
                    "hostile locale content hash must remain canonical", checks);
            require(sync_folder_manifest_digest(hostile_manifest) ==
                        classic_manifest_digest,
                    "hostile locale must not change manifest identity", checks);
            for (const SyncChunkRange& chunk :
                 hostile_manifest.entries.front().chunks) {
                require(is_lowercase_sha256_hex(chunk.sha256),
                        "every hostile-locale chunk hash must remain canonical",
                        checks);
            }

            SyncFakePeerFileFetchSessionOptions options;
            options.source_root_path = tree.source().generic_string();
            options.destination_root_path = tree.destination().generic_string();
            options.staging_root_path = tree.staging().generic_string();
            options.folder_id = "folder-alpha";
            options.source_device_id = "device-alpha";
            options.destination_device_id = "device-bravo";
            options.peer_id = "peer-alpha";
            options.peer_session_id = "session-locale";
            options.source_manifest_counter = 20;
            options.destination_manifest_counter = 21;
            options.source_lineage_counter = 22;
            options.destination_lineage_counter = 23;
            options.chunk_size_bytes = 5;
            options.max_chunks_per_request = 2;
            options.max_bytes_per_request = 10;
            options.max_chunks_per_peer_round = 2;
            options.max_bytes_per_peer_round = 10;
            options.max_transfer_rounds = 16;

            SyncFakePeerFileFetchSessionResult session;
            const SyncValidationResult session_result =
                run_sync_fake_peer_file_fetch_session(options, session);
            require(session_result.ok,
                    "hostile-locale staged transfer must succeed: " +
                        session_result.reason,
                    checks);
            require(session.content_converged && session.files_materialized == 1,
                    "hostile-locale transfer must converge one file", checks);
            require(session.files.size() == 1 &&
                        session.files.front().source_content_sha256 ==
                            sha256_hex(bytes) &&
                        session.files.front().destination_content_sha256 ==
                            sha256_hex(bytes),
                    "staged range and whole-file hashes must remain canonical",
                    checks);
        }

        std::ifstream copied(
            tree.destination() / "nested" / "payload.bin", std::ios::binary);
        const std::string copied_bytes(
            (std::istreambuf_iterator<char>(copied)),
            std::istreambuf_iterator<char>());
        require(copied_bytes == bytes,
                "locale-safe transfer must preserve exact binary bytes", checks);

        std::cout << "sync manifest hash locale tests passed (" << checks
                  << " checks)\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync manifest hash locale tests failed: " << e.what()
                  << '\n';
        return 1;
    }
}
