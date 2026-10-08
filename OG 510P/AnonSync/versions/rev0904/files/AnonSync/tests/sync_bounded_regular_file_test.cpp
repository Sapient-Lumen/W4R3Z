#include "sync_bounded_regular_file.hpp"
#if !defined(_WIN32)
#include "sync_posix_descriptor_snapshot.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

#if defined(_WIN32)
#include <process.h>
#else
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using anonsync::read_sync_bounded_regular_file_no_symlink_or_throw;
using anonsync::read_sync_bounded_single_link_regular_file_no_symlink_or_throw;
#if !defined(_WIN32)
using anonsync::FrozenSyncPosixRegularFileSnapshot;
using anonsync::SyncPosixDescriptorLinkPolicy;
#endif

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
#if defined(_WIN32)
        const auto process_id = static_cast<unsigned long long>(::_getpid());
#else
        const auto process_id = static_cast<unsigned long long>(::getpid());
#endif
        const auto nonce = static_cast<unsigned long long>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        path_ = fs::temp_directory_path() /
                ("anonsync-bounded-regular-file-" +
                 std::to_string(process_id) + "-" + std::to_string(nonce));
        fs::create_directory(path_);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void write_bytes(const fs::path& path, std::string_view bytes) {
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    if (!stream) {
        throw std::runtime_error("could not create test file: " + path.string());
    }
    stream.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!stream) {
        throw std::runtime_error("could not write test file: " + path.string());
    }
    stream.close();
    if (!stream) {
        throw std::runtime_error("could not close test file: " + path.string());
    }
}

[[nodiscard]] bool rejects_with(const fs::path& path,
                                std::uint64_t maximum_bytes,
                                std::string_view expected_fragment) {
    try {
        (void)read_sync_bounded_regular_file_no_symlink_or_throw(
            path, maximum_bytes, "focused bounded read");
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(expected_fragment) !=
               std::string_view::npos;
    }
}

[[nodiscard]] bool rejects_single_link_with(
    const fs::path& path,
    std::uint64_t maximum_bytes,
    std::string_view expected_fragment) {
    try {
        (void)read_sync_bounded_single_link_regular_file_no_symlink_or_throw(
            path, maximum_bytes, "focused single-link bounded read");
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(expected_fragment) !=
               std::string_view::npos;
    }
}

void test_basic_contract(TestState& test, const TemporaryDirectory& temporary) {
    const fs::path missing = temporary.path() / "missing.json";
    test.require(rejects_with(missing, 0, "maximum bytes must be positive"),
                 "zero byte ceilings fail before path observation");
    test.require(rejects_with(missing, 32, "open failed"),
                 "missing paths are rejected by the opened-object boundary");

#if defined(_WIN32)
    const fs::path embedded_nul(
        std::wstring(L"bounded-read\0truncated", 22));
#else
    const fs::path embedded_nul(
        std::string("bounded-read\0truncated", 22));
#endif
    test.require(rejects_with(embedded_nul, 32, "embedded NUL"),
                 "embedded NUL path bytes cannot select an unintended prefix");

    const fs::path empty = temporary.path() / "empty.json";
    write_bytes(empty, {});
    test.require(read_sync_bounded_regular_file_no_symlink_or_throw(
                     empty, 1, "empty file")
                     .empty(),
                 "empty regular files are exact observations");

    const fs::path binary = temporary.path() / "binary.json";
    const std::string payload("abc\0def", 7);
    write_bytes(binary, payload);
    test.require(read_sync_bounded_regular_file_no_symlink_or_throw(
                     binary, payload.size(), "binary file") == payload,
                 "embedded NUL bytes and exact ceilings are preserved");
    test.require(rejects_with(binary, payload.size() - 1,
                              "exceeds bounded read limit"),
                 "initial size above the ceiling is rejected");

    const fs::path ceiling = temporary.path() / "ceiling.txt";
    write_bytes(ceiling, "0123456789");
    test.require(read_sync_bounded_regular_file_no_symlink_or_throw(
                     ceiling, 10, "ceiling file") == "0123456789",
                 "a payload exactly at the byte ceiling is accepted");
    test.require(rejects_with(ceiling, 9, "exceeds bounded read limit"),
                 "a payload one byte above the ceiling is rejected");
}

void test_path_types(TestState& test, const TemporaryDirectory& temporary) {
    const fs::path directory = temporary.path() / "directory";
    fs::create_directory(directory);
    test.require(rejects_with(directory, 64, "not a regular file") ||
                     rejects_with(directory, 64, "open failed"),
                 "directories never become regular-file evidence");

    const fs::path target = temporary.path() / "target.txt";
    const fs::path link = temporary.path() / "link.txt";
    write_bytes(target, "target");
    std::error_code symlink_error;
    fs::create_symlink(target.filename(), link, symlink_error);
    if (!symlink_error) {
        test.require(rejects_with(link, 64, "open failed") ||
                         rejects_with(link, 64, "reparse point"),
                     "the final symbolic-link or reparse component is rejected");
    } else {
        std::cout << "SKIP: symbolic-link creation unavailable: "
                  << symlink_error.message() << "\n";
    }

    const fs::path hardlink = temporary.path() / "target-hardlink.txt";
    std::error_code hardlink_error;
    fs::create_hard_link(target, hardlink, hardlink_error);
    if (!hardlink_error) {
        test.require(read_sync_bounded_regular_file_no_symlink_or_throw(
                         hardlink, 64, "ordinary hard-link observation") ==
                         "target",
                     "the general bounded reader retains hard-link compatibility");
        test.require(rejects_single_link_with(
                         hardlink, 64, "single-link regular file"),
                     "the authority reader rejects multiply-linked objects");
        test.require(rejects_single_link_with(
                         target, 64, "single-link regular file"),
                     "every alias of a multiply-linked inode is rejected");
    } else {
        std::cout << "SKIP: hard-link creation unavailable: "
                  << hardlink_error.message() << "\n";
    }

#if !defined(_WIN32)
    const fs::path fifo = temporary.path() / "blocked.fifo";
    if (::mkfifo(fifo.c_str(), 0600) != 0) {
        throw std::runtime_error("mkfifo failed for focused bounded-read test");
    }
    const auto start = std::chrono::steady_clock::now();
    const bool rejected = rejects_with(fifo, 64, "not a regular file");
    const auto elapsed = std::chrono::steady_clock::now() - start;
    test.require(rejected,
                 "FIFO descriptors are rejected after nonblocking open");
    test.require(elapsed < std::chrono::seconds(1),
                 "a FIFO with no writer cannot block the bounded reader");
#endif
}

#if !defined(_WIN32)
[[nodiscard]] bool descriptor_rejects_with(
    int descriptor,
    std::uint64_t maximum_bytes,
    SyncPosixDescriptorLinkPolicy link_policy,
    std::string_view expected_fragment) {
    try {
        (void)FrozenSyncPosixRegularFileSnapshot::
            freeze_borrowed_descriptor_or_throw(
                descriptor, maximum_bytes, link_policy,
                "focused descriptor snapshot");
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(expected_fragment) !=
               std::string_view::npos;
    }
}

void test_borrowed_descriptor_contract(
    TestState& test,
    const TemporaryDirectory& temporary) {
    const fs::path file = temporary.path() / "borrowed-descriptor.txt";
    write_bytes(file, "0123456789");
    const int descriptor = ::open(file.c_str(), O_RDONLY | O_CLOEXEC);
    if (descriptor < 0) {
        throw std::runtime_error("could not open borrowed descriptor witness");
    }
    if (::lseek(descriptor, 4, SEEK_SET) != 4) {
        (void)::close(descriptor);
        throw std::runtime_error("could not position borrowed descriptor witness");
    }

    const auto snapshot = FrozenSyncPosixRegularFileSnapshot::
        freeze_borrowed_descriptor_or_throw(
            descriptor, 10,
            SyncPosixDescriptorLinkPolicy::stable_named_object,
            "focused descriptor snapshot");
    test.require(snapshot.bytes() == "0123456789",
                 "borrowed descriptors are frozen from byte zero");
    test.require(::lseek(descriptor, 0, SEEK_CUR) == 4,
                 "positional reads preserve the caller's shared file offset");
    test.require(::fcntl(descriptor, F_GETFD) >= 0,
                 "successful snapshots preserve caller descriptor ownership");
    test.require(descriptor_rejects_with(
                     descriptor, 9,
                     SyncPosixDescriptorLinkPolicy::stable_named_object,
                     "exceeds bounded read limit"),
                 "borrowed snapshots enforce their own exact byte ceiling");
    test.require(::lseek(descriptor, 0, SEEK_CUR) == 4 &&
                     ::fcntl(descriptor, F_GETFD) >= 0,
                 "rejected snapshots preserve offset and ownership");
    if (::close(descriptor) != 0) {
        throw std::runtime_error("could not close borrowed descriptor witness");
    }

    const fs::path linked = temporary.path() / "borrowed-linked.txt";
    const fs::path alias = temporary.path() / "borrowed-linked-alias.txt";
    write_bytes(linked, "linked");
    std::error_code link_error;
    fs::create_hard_link(linked, alias, link_error);
    if (!link_error) {
        const int linked_fd = ::open(linked.c_str(), O_RDONLY | O_CLOEXEC);
        if (linked_fd < 0) {
            throw std::runtime_error("could not open hard-link descriptor witness");
        }
        const auto compatible = FrozenSyncPosixRegularFileSnapshot::
            freeze_borrowed_descriptor_or_throw(
                linked_fd, 16,
                SyncPosixDescriptorLinkPolicy::stable_named_object,
                "focused descriptor snapshot");
        test.require(compatible.bytes() == "linked",
                     "general descriptor snapshots retain stable hard-link compatibility");
        test.require(descriptor_rejects_with(
                         linked_fd, 16,
                         SyncPosixDescriptorLinkPolicy::exactly_one,
                         "single-link regular file"),
                     "authority snapshots reject multiply-linked descriptors");
        test.require(::fcntl(linked_fd, F_GETFD) >= 0,
                     "link-policy rejection leaves the borrowed descriptor open");
        (void)::close(linked_fd);
    } else {
        std::cout << "SKIP: descriptor hard-link creation unavailable: "
                  << link_error.message() << "\n";
    }

    const fs::path unlinked = temporary.path() / "borrowed-unlinked.txt";
    write_bytes(unlinked, "unlinked");
    const int unlinked_fd = ::open(unlinked.c_str(), O_RDONLY | O_CLOEXEC);
    if (unlinked_fd < 0 || ::unlink(unlinked.c_str()) != 0) {
        if (unlinked_fd >= 0) (void)::close(unlinked_fd);
        throw std::runtime_error("could not create unlinked descriptor witness");
    }
    test.require(descriptor_rejects_with(
                     unlinked_fd, 16,
                     SyncPosixDescriptorLinkPolicy::stable_named_object,
                     "named regular-file object"),
                 "unlinked descriptors cannot mint namespace evidence");
    test.require(::fcntl(unlinked_fd, F_GETFD) >= 0,
                 "unlinked-object rejection preserves caller ownership");
    (void)::close(unlinked_fd);

    test.require(descriptor_rejects_with(
                     -1, 16,
                     SyncPosixDescriptorLinkPolicy::stable_named_object,
                     "initial fstat failed"),
                 "invalid borrowed descriptors fail at initial inspection");
    test.require(descriptor_rejects_with(
                     -1, 0,
                     SyncPosixDescriptorLinkPolicy::stable_named_object,
                     "maximum bytes must be positive"),
                 "descriptor limits fail before kernel observation");
}
#endif

}  // namespace

int main() {
    try {
        TestState test;
        const TemporaryDirectory temporary;
        test_basic_contract(test, temporary);
        test_path_types(test, temporary);
#if !defined(_WIN32)
        test_borrowed_descriptor_contract(test, temporary);
#endif
        std::cout << "sync bounded regular file tests passed: " << test.passed
                  << "/" << (test.passed + test.failed) << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}
