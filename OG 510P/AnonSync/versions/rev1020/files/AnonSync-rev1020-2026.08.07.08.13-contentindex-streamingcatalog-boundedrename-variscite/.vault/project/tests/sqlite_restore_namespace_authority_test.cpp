#include "anonsync_core_internal.hpp"

#include <cstdint>
#include <cstdio>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void write_binary(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("could not create fixture: " + path.string());
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) throw std::runtime_error("could not write fixture: " + path.string());
}

std::string read_binary(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("could not read fixture: " + path.string());
    return std::string(std::istreambuf_iterator<char>(input),
                       std::istreambuf_iterator<char>());
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {
             "", "-wal", "-shm", "-journal", ".restore.lock", ".write.lock"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

anonsync::Json make_case(const std::string& case_id) {
    anonsync::Json value;
    value.type = anonsync::Json::Type::Object;
    value.o["case_id"] = anonsync::json_string_value(case_id);
    value.o["kind"] = anonsync::json_string_value("openapi");
    value.o["operation_id"] =
        anonsync::json_string_value("restoreNamespaceAuthority");
    value.o["contract_digest_sha256"] =
        anonsync::json_string_value("restore-namespace-authority-contract");
    value.o["cloud_event_source"] = anonsync::json_string_value("");
    value.o["cloud_event_id"] = anonsync::json_string_value("");
    return value;
}

anonsync::Json make_claims(const std::string& jti) {
    anonsync::Json value;
    value.type = anonsync::Json::Type::Object;
    value.o["operation_id"] =
        anonsync::json_string_value("restoreNamespaceAuthority");
    value.o["contract_digest_sha256"] = anonsync::json_string_value(
        anonsync::sha256_hex("restore-namespace-authority-contract"));
    value.o["jti"] = anonsync::json_string_value(jti);
    return value;
}

void create_snapshot(const fs::path& ledger, const fs::path& snapshot) {
    cleanup_sqlite_family(ledger);
    cleanup_sqlite_family(snapshot);
    std::string reason;
    auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
    backend->load(ledger.string(), "batch");
    if (!backend->stage(make_case("namespace-authority-case"),
                        make_claims("namespace-authority-jti"),
                        "allow", reason)) {
        throw std::runtime_error("could not stage snapshot fixture: " + reason);
    }
    if (!backend->commit(reason)) {
        throw std::runtime_error("could not commit snapshot fixture: " + reason);
    }
    if (!backend->backup_snapshot(snapshot.string(), reason)) {
        throw std::runtime_error("could not create snapshot fixture: " + reason);
    }
    backend->close();
}

bool has_atomic_publication_temp(const fs::path& root) {
    for (const auto& entry : fs::directory_iterator(root)) {
        const std::string name = entry.path().filename().string();
        if (name.rfind(".anonsync-publish-v1-", 0) == 0) return true;
    }
    return false;
}

void expect_sidecar_rejection(const fs::path& snapshot,
                              const fs::path& destination,
                              std::string_view suffix,
                              std::uint64_t& checks) {
    cleanup_sqlite_family(destination);
    write_binary(destination, "");
    const fs::path sidecar(destination.string() + std::string(suffix));
    const std::string foreign_bytes =
        "foreign-sidecar-authority:" + std::string(suffix) +
        std::string("\0tail", 5);
    write_binary(sidecar, foreign_bytes);

    bool rejected = false;
    std::string reason;
    try {
        anonsync::restore_sqlite_snapshot_into_ledger(
            snapshot.string(), destination.string());
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected, "restore accepted an authority-free sidecar " +
                          std::string(suffix), checks);
    require(reason.find("snapshot sidecar " + std::string(suffix)) !=
                std::string::npos,
            "restore sidecar rejection reason mismatch: " + reason, checks);
    require(fs::exists(destination) && fs::file_size(destination) == 0,
            "sidecar rejection replaced the empty destination main file", checks);
    require(fs::exists(sidecar) && read_binary(sidecar) == foreign_bytes,
            "sidecar rejection deleted or changed foreign sidecar bytes", checks);
    require(!has_atomic_publication_temp(destination.parent_path()),
            "sidecar rejection left an atomic publication temp", checks);
    cleanup_sqlite_family(destination);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root = fs::path("/tmp") /
        ("anonsync-r0821-restore-namespace-" +
         std::to_string(static_cast<long long>(::getpid())) + "-" +
         std::to_string(static_cast<long long>(std::time(nullptr))));
    const fs::path source = root / "source.sqlite";
    const fs::path snapshot = root / "snapshot.sqlite";
    const fs::path destination = root / "destination.sqlite";

    try {
        fs::create_directory(root);
        if (::chmod(root.c_str(), 0700) != 0) {
            throw std::runtime_error("could not make test directory private");
        }
        create_snapshot(source, snapshot);

        std::map<fs::path, std::string> foreign_predictable_names;
        const std::time_t now = std::time(nullptr);
        for (long long offset = -4; offset <= 4; ++offset) {
            const fs::path candidate = root /
                ("." + destination.filename().string() + ".restore-tmp-" +
                 std::to_string(static_cast<long long>(::getpid())) + "-" +
                 std::to_string(static_cast<long long>(now) + offset) +
                 ".sqlite");
            const std::string bytes =
                "foreign-predictable-temp:" + std::to_string(offset) +
                std::string("\0tail", 5);
            write_binary(candidate, bytes);
            foreign_predictable_names.emplace(candidate, bytes);
        }

        anonsync::restore_sqlite_snapshot_into_ledger(
            snapshot.string(), destination.string());
        require(fs::exists(destination) && fs::file_size(destination) > 0,
                "valid restore did not publish a destination", checks);
        for (const auto& [path, bytes] : foreign_predictable_names) {
            require(fs::exists(path) && read_binary(path) == bytes,
                    "restore consumed or changed a predictable foreign temp name: " +
                        path.filename().string(), checks);
        }
        require(!has_atomic_publication_temp(root),
                "successful restore left an atomic publication temp", checks);
        require(!fs::exists(fs::path(destination.string() + "-wal")) &&
                    !fs::exists(fs::path(destination.string() + "-shm")) &&
                    !fs::exists(fs::path(destination.string() + "-journal")),
                "successful sealed-byte restore manufactured sidecars", checks);

        expect_sidecar_rejection(snapshot, root / "foreign-wal.sqlite", "-wal",
                                 checks);
        expect_sidecar_rejection(snapshot, root / "foreign-shm.sqlite", "-shm",
                                 checks);
        expect_sidecar_rejection(snapshot, root / "foreign-journal.sqlite",
                                 "-journal", checks);

        cleanup_sqlite_family(source);
        cleanup_sqlite_family(snapshot);
        cleanup_sqlite_family(destination);
        std::error_code ignored;
        fs::remove_all(root, ignored);
        std::cout << "anonsync sqlite restore namespace authority test passed="
                  << checks << " failed=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        std::error_code ignored;
        fs::remove_all(root, ignored);
        return 2;
    }
}
