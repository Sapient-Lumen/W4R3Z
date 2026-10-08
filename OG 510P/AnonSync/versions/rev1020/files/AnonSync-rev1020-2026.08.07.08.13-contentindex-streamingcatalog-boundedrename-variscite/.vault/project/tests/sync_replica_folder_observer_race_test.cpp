#include "sync_replica_folder_observer.hpp"

#if defined(__linux__)

#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <openssl/evp.h>

namespace {

namespace fs = std::filesystem;

enum class MutationMode : unsigned char {
    None,
    ReplaceFileName,
    ReplaceDirectoryName,
};

enum class MutationTrigger : unsigned char {
    None,
    PositionalRead,
    DigestUpdate,
};

std::atomic<bool> mutation_armed{false};
std::atomic<int> mutation_error{0};
MutationMode mutation_mode = MutationMode::None;
MutationTrigger mutation_trigger = MutationTrigger::None;
std::size_t expected_digest_update_size = 0;
std::string mutation_primary;
std::string mutation_backup;
std::string mutation_replacement;

void perform_mutation_noexcept() noexcept {
    int error = 0;
    if (mutation_mode == MutationMode::ReplaceFileName) {
        if (::rename(mutation_primary.c_str(), mutation_backup.c_str()) != 0) {
            error = errno;
        } else if (::rename(
                       mutation_replacement.c_str(),
                       mutation_primary.c_str()) != 0) {
            error = errno;
        }
    } else if (mutation_mode == MutationMode::ReplaceDirectoryName) {
        if (::rename(mutation_primary.c_str(), mutation_backup.c_str()) != 0) {
            error = errno;
        } else if (::mkdir(mutation_primary.c_str(), 0700) != 0) {
            error = errno;
        }
    }
    mutation_error.store(error, std::memory_order_release);
}

class MutationArm final {
public:
    MutationArm(
        MutationMode mode,
        MutationTrigger trigger,
        fs::path primary,
        fs::path backup,
        fs::path replacement = {},
        std::size_t digest_update_size = 0U) {
        mutation_mode = mode;
        mutation_trigger = trigger;
        expected_digest_update_size = digest_update_size;
        mutation_primary = primary.string();
        mutation_backup = backup.string();
        mutation_replacement = replacement.string();
        mutation_error.store(0, std::memory_order_release);
        mutation_armed.store(true, std::memory_order_release);
    }

    ~MutationArm() {
        mutation_armed.store(false, std::memory_order_release);
        mutation_mode = MutationMode::None;
        mutation_trigger = MutationTrigger::None;
        expected_digest_update_size = 0U;
        mutation_primary.clear();
        mutation_backup.clear();
        mutation_replacement.clear();
    }

    MutationArm(const MutationArm&) = delete;
    MutationArm& operator=(const MutationArm&) = delete;
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        root_ = fs::temp_directory_path() /
                ("anonsync-folder-observer-race-" +
                 std::to_string(static_cast<long long>(::getpid())) + "-" +
                 std::to_string(static_cast<long long>(tick)));
        fs::create_directories(root_);
        if (::chmod(root_.c_str(), 0700) != 0) {
            throw std::runtime_error("could not protect race-test root");
        }
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(root_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return root_; }

private:
    fs::path root_;
};

void write_bytes(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("could not open race fixture");
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("could not write race fixture");
}

class TestState final {
public:
    void require(bool condition, const std::string& message) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << message << "\n";
    }

    std::size_t passed = 0;
    std::size_t failed = 0;
};

[[nodiscard]] std::string observe_error(
    const anonsync::SyncDirectoryAuthority& authority,
    const std::string& label) {
    try {
        (void)anonsync::observe_sync_replica_folder_or_throw(
            authority, {}, label);
    } catch (const std::exception& error) {
        return error.what();
    }
    return {};
}

void test_file_name_substitution(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path outer = temporary.path();
    const fs::path root = outer / "scan";
    fs::create_directory(root);
    if (::chmod(root.c_str(), 0700) != 0) {
        throw std::runtime_error("could not protect file-race scan root");
    }
    const fs::path primary = root / "victim.txt";
    const fs::path backup = root / "victim-old.txt";
    // Keep the replacement outside the observed root so the deterministic hook
    // cannot accidentally fire while scanning its staging pathname.
    const fs::path replacement = outer / "replacement.txt";
    std::string payload(1024U * 1024U + 17U, 'x');
    payload[0] = 'A';
    payload[payload.size() / 2U] = 'B';
    payload.back() = 'C';
    write_bytes(primary, payload);
    write_bytes(replacement, payload);

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "observer file-race root");
    std::string error;
    {
        MutationArm arm(
            MutationMode::ReplaceFileName,
            MutationTrigger::DigestUpdate,
            primary,
            backup,
            replacement,
            payload.size());
        error = observe_error(authority, "observer file-race scan");
        test.require(
            !mutation_armed.load(std::memory_order_acquire),
            "the file race consumed the deterministic digest hook");
        test.require(
            mutation_error.load(std::memory_order_acquire) == 0,
            "the file-name substitution fixture completed without syscall failure");
    }
    const bool rejected_by_frozen_metadata =
        error.find("changed while its bounded bytes were read") !=
        std::string::npos;
    const bool rejected_by_name_rebinding =
        error.find("path changed while being observed") != std::string::npos;
    test.require(
        rejected_by_frozen_metadata || rejected_by_name_rebinding,
        "equal replacement bytes cannot escape descriptor or post-read name re-attestation; observed: " + error);
    authority.verify_or_throw("observer file-race authority after rejection");
}

void test_directory_name_substitution(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const fs::path primary = root / "nested";
    const fs::path backup = root / "nested-old";
    fs::create_directory(primary);
    write_bytes(primary / "inside.txt", "inside");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "observer directory-race root");
    std::string error;
    {
        MutationArm arm(
            MutationMode::ReplaceDirectoryName,
            MutationTrigger::PositionalRead,
            primary,
            backup);
        error = observe_error(authority, "observer directory-race scan");
        test.require(
            !mutation_armed.load(std::memory_order_acquire),
            "the directory race consumed the deterministic pread hook");
        test.require(
            mutation_error.load(std::memory_order_acquire) == 0,
            "the directory-name substitution fixture completed without syscall failure");
    }
    test.require(
        error.find("directory path changed while being observed") !=
            std::string::npos,
        "a replacement directory cannot inherit observations from the retained old descriptor");
    authority.verify_or_throw(
        "observer directory-race authority after rejection");
}

}  // namespace

void consume_mutation_if_armed(MutationTrigger trigger) noexcept {
    if (mutation_trigger != trigger) return;
    bool expected = true;
    if (mutation_armed.compare_exchange_strong(
            expected, false, std::memory_order_acq_rel)) {
        perform_mutation_noexcept();
    }
}

extern "C" ssize_t __real_pread(
    int descriptor,
    void* buffer,
    size_t count,
    off_t offset);

extern "C" ssize_t __wrap_pread(
    int descriptor,
    void* buffer,
    size_t count,
    off_t offset) {
    const ssize_t result = __real_pread(descriptor, buffer, count, offset);
    if (result >= 0) {
        consume_mutation_if_armed(MutationTrigger::PositionalRead);
    }
    return result;
}

extern "C" int __real_EVP_DigestUpdate(
    EVP_MD_CTX* context,
    const void* bytes,
    size_t byte_count);

extern "C" int __wrap_EVP_DigestUpdate(
    EVP_MD_CTX* context,
    const void* bytes,
    size_t byte_count) {
    const int result = __real_EVP_DigestUpdate(context, bytes, byte_count);
    if (result == 1 &&
        mutation_trigger == MutationTrigger::DigestUpdate &&
        byte_count == expected_digest_update_size) {
        consume_mutation_if_armed(MutationTrigger::DigestUpdate);
    }
    return result;
}

int main() {
    try {
        TestState test;
        test_file_name_substitution(test);
        test_directory_name_substitution(test);
        std::cout << "sync replica folder observer race checks: "
                  << test.passed << "/" << (test.passed + test.failed)
                  << "\n";
        return test.failed == 0U ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}

#else

#include <iostream>

int main() {
    std::cout << "sync replica folder observer race test unavailable\n";
    return 0;
}

#endif
