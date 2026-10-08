#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif
#include "sync_atomic_file_publication.hpp"
#include "sync_process_incarnation.hpp"

#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
#endif

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
        } else {
            std::cerr << "FAIL: " << label << '\n';
        }
    }

    [[nodiscard]] int finish() const {
        std::cout << "sync prepared immutable publication: " << passed_ << "/"
                  << total_ << " checks passed\n";
        return passed_ == total_ ? 0 : 1;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const fs::path base = fs::temp_directory_path();
        const auto seed = static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        for (std::uint64_t attempt = 0; attempt != 4096; ++attempt) {
            path_ = base / ("anonsync-prepared-publication-" +
                            std::to_string(seed) + "-" +
                            std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(path_, error)) return;
        }
        throw std::runtime_error(
            "could not reserve prepared-publication test directory");
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void write_binary(const fs::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("could not open test file for write");
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!out) throw std::runtime_error("could not write test file");
}

std::string read_binary(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return {};
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

std::size_t publication_temp_count(const fs::path& directory) {
    std::size_t count = 0;
    for (const fs::directory_entry& entry : fs::directory_iterator(directory)) {
        const std::string name = entry.path().filename().string();
        if (name.starts_with(".anonsync-publish-v1-") &&
            name.ends_with(".tmp")) {
            ++count;
        }
    }
    return count;
}

struct TypedFailure final {
    bool caught = false;
    anonsync::SyncAtomicFilePublicationOutcome outcome =
        anonsync::SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
    anonsync::SyncAtomicFilePublicationResidue residue =
        anonsync::SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain;
    std::string message;
};

template <typename Function>
TypedFailure capture_failure(Function&& function) {
    TypedFailure observed;
    try {
        std::forward<Function>(function)();
    } catch (const anonsync::SyncAtomicFilePublicationError& error) {
        observed.caught = true;
        observed.outcome = error.outcome();
        observed.residue = error.residue();
        observed.message = error.what();
    }
    return observed;
}

#if !defined(_WIN32)
std::pair<std::uint64_t, std::uint64_t> inode_identity(const fs::path& path) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        throw std::runtime_error("could not stat test file");
    }
    return {static_cast<std::uint64_t>(status.st_dev),
            static_cast<std::uint64_t>(status.st_ino)};
}
#endif


}  // namespace

int main() {
    try {
        using anonsync::SyncAtomicFilePublicationOutcome;
        using anonsync::SyncAtomicFilePublicationResidue;
        using anonsync::SyncPreparedImmutableJsonPublication;

        TestState state;
        TemporaryDirectory root;

        SyncPreparedImmutableJsonPublication empty;
        state.check(!empty.valid(),
                    "default prepared capability contains no authority");
        const TypedFailure empty_failure =
            capture_failure([&] { empty.publish_or_throw(); });
        state.check(
            empty_failure.caught &&
                empty_failure.outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                empty_failure.residue == SyncAtomicFilePublicationResidue::None,
            "empty capability fails as typed not-published without residue");

        const fs::path normal_parent = root.path() / "normal";
        fs::create_directory(normal_parent);
        const fs::path normal_final = normal_parent / "receipt.json";
        const std::string normal_payload =
            "{\"receipt\":\"pinned-parent-success\"}\n";
        SyncPreparedImmutableJsonPublication normal =
            anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                normal_final, normal_payload, "normal prepared publication");
        state.check(normal.valid(),
                    "preparation returns live publication authority");
        state.check(!fs::exists(normal_final) &&
                        publication_temp_count(normal_parent) == 0,
                    "preparation creates neither final entry nor temp residue");
        SyncPreparedImmutableJsonPublication moved = std::move(normal);
        state.check(!normal.valid() && moved.valid(),
                    "move transfers authority and empties the source");
        moved.publish_or_throw();
        state.check(!moved.valid(),
                    "successful publication consumes authority exactly once");
        state.check(read_binary(normal_final) == normal_payload,
                    "prepared publication preserves exact owned payload bytes");
        state.check(publication_temp_count(normal_parent) == 0,
                    "successful prepared publication leaves no temp residue");
        const TypedFailure reused_failure =
            capture_failure([&] { moved.publish_or_throw(); });
        state.check(
            reused_failure.caught &&
                reused_failure.outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                reused_failure.residue == SyncAtomicFilePublicationResidue::None &&
                reused_failure.message.find("already consumed") !=
                    std::string::npos,
            "consumed capability cannot replay stale authority");
        state.check(read_binary(normal_final) == normal_payload,
                    "rejected capability reuse cannot mutate published bytes");

        const fs::path owned_parent = root.path() / "payload-owner";
        fs::create_directory(owned_parent);
        const fs::path owned_final = owned_parent / "receipt.json";
        std::string caller_payload =
            "{\"receipt\":\"owned-before-transition\"}\n";
        const std::string expected_owned_payload = caller_payload;
        SyncPreparedImmutableJsonPublication owned =
            anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                owned_final, std::move(caller_payload),
                "payload ownership prepared publication");
        caller_payload.assign("caller storage changed after preparation");
        owned.publish_or_throw();
        state.check(read_binary(owned_final) == expected_owned_payload,
                    "capability owns bytes independently of caller storage");

        const fs::path occupied_parent = root.path() / "occupied";
        fs::create_directory(occupied_parent);
        const fs::path occupied_final = occupied_parent / "receipt.json";
        const std::string competing_payload =
            "{\"receipt\":\"competing-authority\"}\n";
        write_binary(occupied_final, competing_payload);
#if !defined(_WIN32)
        const auto occupied_inode_before = inode_identity(occupied_final);
#endif
        const TypedFailure occupied_failure = capture_failure([&] {
            (void)anonsync::
                prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                    occupied_final, "blocked",
                    "occupied prepared publication");
        });
        state.check(
            occupied_failure.caught &&
                occupied_failure.outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                occupied_failure.residue == SyncAtomicFilePublicationResidue::None,
            "occupied destination is denied during preparation");
        state.check(read_binary(occupied_final) == competing_payload,
                    "preparation denial preserves competing bytes");
#if !defined(_WIN32)
        state.check(inode_identity(occupied_final) == occupied_inode_before,
                    "preparation denial preserves competing inode identity");
#else
        state.check(true,
                    "inode identity preservation is not executed on Windows");
#endif
        state.check(publication_temp_count(occupied_parent) == 0,
                    "preparation denial creates no temp residue");

        const fs::path race_parent = root.path() / "late-creator";
        fs::create_directory(race_parent);
        const fs::path race_final = race_parent / "receipt.json";
        SyncPreparedImmutableJsonPublication late_creator =
            anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                race_final, normal_payload,
                "late creator prepared publication");
        write_binary(race_final, competing_payload);
#if !defined(_WIN32)
        const auto race_inode_before = inode_identity(race_final);
#endif
        const TypedFailure race_failure =
            capture_failure([&] { late_creator.publish_or_throw(); });
        state.check(
            race_failure.caught &&
                race_failure.outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                race_failure.residue == SyncAtomicFilePublicationResidue::None,
            "creator arriving after preparation wins without temp reservation");
        state.check(!late_creator.valid(),
                    "failed publication still consumes single-use authority");
        state.check(read_binary(race_final) == competing_payload,
                    "late creator bytes are preserved exactly");
#if !defined(_WIN32)
        state.check(inode_identity(race_final) == race_inode_before,
                    "late creator inode is preserved exactly");
#else
        state.check(true,
                    "late-creator inode identity is not executed on Windows");
#endif
        state.check(publication_temp_count(race_parent) == 0,
                    "late creator denial occurs before temp residue exists");

#if !defined(_WIN32)
        const fs::path intended_parent = root.path() / "intended";
        const fs::path displaced_parent = root.path() / "displaced";
        fs::create_directory(intended_parent);
        const fs::path rebound_final = intended_parent / "receipt.json";
        SyncPreparedImmutableJsonPublication rebound =
            anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                rebound_final, normal_payload,
                "parent rebind prepared publication");
        fs::rename(intended_parent, displaced_parent);
        fs::create_directory(intended_parent);
        const TypedFailure rebound_failure =
            capture_failure([&] { rebound.publish_or_throw(); });
        state.check(
            rebound_failure.caught &&
                rebound_failure.outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                rebound_failure.residue == SyncAtomicFilePublicationResidue::None &&
                rebound_failure.message.find(
                    "no longer names the retained directory identity") !=
                    std::string::npos,
            "parent rebind is denied against retained directory authority");
        state.check(!fs::exists(rebound_final),
                    "replacement parent receives no receipt");
        state.check(!fs::exists(displaced_parent / "receipt.json"),
                    "displaced pinned parent receives no receipt after denial");
        state.check(publication_temp_count(intended_parent) == 0 &&
                        publication_temp_count(displaced_parent) == 0,
                    "rebind denial occurs before any temp reservation");

        const fs::path fork_parent = root.path() / "fork";
        fs::create_directory(fork_parent);
        const fs::path fork_final = fork_parent / "receipt.json";
        SyncPreparedImmutableJsonPublication fork_plan =
            anonsync::prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                fork_final, normal_payload,
                "fork inherited prepared publication");
        // The inherited prepared object is the capability under test.
        // The child performs exactly one production call; any return or C++
        // exception is a failed fail-stop boundary. The shared owner supplies
        // the deadline and kill/reap authority.
        auto child = spawn_inherited_test_process_or_throw(
            [&]() -> int {
                try {
                    fork_plan.publish_or_throw();
                    return 91;
                } catch (...) {
                    return 92;
                }
            },
            "prepared publication inherited-capability probe");
        const int child_status = child.wait_for_exit(
            5s, "prepared publication inherited-capability probe");
        state.check(
            WIFEXITED(child_status) &&
                WEXITSTATUS(child_status) ==
                    anonsync::kSyncProcessCapabilityViolationExitCode,
            "fork child cannot exercise inherited publication authority");
        state.check(fork_plan.valid() && !fs::exists(fork_final) &&
                        publication_temp_count(fork_parent) == 0,
                    "child denial leaves parent capability and namespace untouched");
        fork_plan.publish_or_throw();
        state.check(read_binary(fork_final) == normal_payload,
                    "original process retains and exercises its exact authority");
#else
        state.check(true, "POSIX parent-rebind denial is not executed on Windows");
        state.check(true, "POSIX replacement-parent proof is not executed on Windows");
        state.check(true, "POSIX displaced-parent proof is not executed on Windows");
        state.check(true, "POSIX rebind temp proof is not executed on Windows");
        state.check(true, "fork-incarnation proof is not executed on Windows");
        state.check(true, "fork namespace proof is not executed on Windows");
        state.check(true, "parent-process authority proof is not executed on Windows");
#endif

        return state.finish();
    } catch (const std::exception& error) {
        std::cerr << "prepared immutable publication test failed: "
                  << error.what() << '\n';
        return 1;
    }
}
