#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::SyncAtomicFilePublicationError;
using anonsync::SyncAtomicFilePublicationOutcome;
using anonsync::SyncAtomicFilePublicationResidue;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationCutpoint;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationObservation;

std::atomic<int> g_unlinkat_calls{0};
std::atomic<bool> g_arm_replacement{false};
std::atomic<bool> g_replacement_installed{false};
std::atomic<bool> g_foreign_replacement_deleted{false};

constexpr const char* kDisplacedOriginalName =
    ".anonsync-unlink-authority-displaced-original";
constexpr const char* kForeignPayload = "foreign-owner-payload";

bool is_publication_temp_name(const std::string& name) {
    return name.rfind(".anonsync-publish-v1-", 0) == 0 &&
           name.size() >= 4 && name.substr(name.size() - 4) == ".tmp";
}

bool write_all_noexcept(int fd, const char* bytes, std::size_t size) noexcept {
    const char* cursor = bytes;
    std::size_t remaining = size;
    while (remaining != 0) {
        const ssize_t written = ::write(fd, cursor, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (written == 0) return false;
        cursor += written;
        remaining -= static_cast<std::size_t>(written);
    }
    return true;
}

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

    int finish() const {
        std::cout << "sync atomic unlink authority: " << passed_ << "/"
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
            path_ = base / ("anonsync-unlink-authority-" +
                            std::to_string(seed) + "-" +
                            std::to_string(attempt));
            std::error_code ec;
            if (fs::create_directory(path_, ec)) return;
        }
        throw std::runtime_error(
            "could not create unlink-authority test directory");
    }

    ~TemporaryDirectory() {
        std::error_code ec;
        fs::remove_all(path_, ec);
    }

    const fs::path& path() const noexcept { return path_; }

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
    if (!in) throw std::runtime_error("could not open test file for read");
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

std::vector<fs::path> publication_temps(const fs::path& directory) {
    std::vector<fs::path> result;
    for (const fs::directory_entry& entry : fs::directory_iterator(directory)) {
        if (is_publication_temp_name(entry.path().filename().string())) {
            result.push_back(entry.path());
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}

bool is_private_empty_regular_file(const fs::path& path) {
    struct stat status_buffer {};
    if (::lstat(path.c_str(), &status_buffer) != 0 ||
        !S_ISREG(status_buffer.st_mode) ||
        (status_buffer.st_mode & 0077) != 0) {
        return false;
    }
    std::error_code ec;
    return fs::file_size(path, ec) == 0 && !ec;
}

class InjectedFailure final : public std::runtime_error {
public:
    InjectedFailure() : std::runtime_error("injected failure after payload") {}
};

void fail_after_payload(const AtomicFilePublicationObservation& observation,
                        void*) {
    if (observation.cutpoint != AtomicFilePublicationCutpoint::PayloadWritten) {
        return;
    }
    g_arm_replacement.store(true, std::memory_order_release);
    throw InjectedFailure();
}

struct NameRebindContext {
    fs::path directory;
    fs::path original_temp_path;
    bool fired = false;
};

void replace_temp_name_then_fail(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    if (observation.cutpoint != AtomicFilePublicationCutpoint::PayloadWritten) {
        return;
    }
    auto& context = *static_cast<NameRebindContext*>(raw_context);
    const std::vector<fs::path> temps = publication_temps(context.directory);
    if (temps.size() != 1) {
        throw std::runtime_error(
            "name rebind expected exactly one publication temp");
    }
    context.original_temp_path = temps.front();
    const fs::path displaced = context.directory / kDisplacedOriginalName;
    fs::rename(context.original_temp_path, displaced);
    write_binary(context.original_temp_path, kForeignPayload);
    if (::chmod(context.original_temp_path.c_str(), 0644) != 0) {
        throw std::runtime_error("name rebind replacement chmod failed");
    }
    context.fired = true;
    throw InjectedFailure();
}

}  // namespace

extern "C" int __real_unlinkat(int directory_fd,
                                const char* pathname,
                                int flags);

extern "C" int __wrap_unlinkat(int directory_fd,
                                const char* pathname,
                                int flags) {
    g_unlinkat_calls.fetch_add(1, std::memory_order_relaxed);
    if (pathname != nullptr &&
        g_arm_replacement.exchange(false, std::memory_order_acq_rel)) {
        (void)__real_unlinkat(directory_fd, kDisplacedOriginalName, 0);
        if (::renameat(directory_fd, pathname, directory_fd,
                       kDisplacedOriginalName) == 0) {
            int replacement_fd;
            do {
                replacement_fd = ::openat(directory_fd, pathname,
                                          O_WRONLY | O_CREAT | O_EXCL, 0644);
            } while (replacement_fd < 0 && errno == EINTR);
            if (replacement_fd >= 0) {
                const std::string foreign = kForeignPayload;
                const bool written = write_all_noexcept(
                    replacement_fd, foreign.data(), foreign.size());
                int close_result;
                do {
                    close_result = ::close(replacement_fd);
                } while (close_result != 0 && errno == EINTR);
                if (written && close_result == 0) {
                    g_replacement_installed.store(true,
                                                  std::memory_order_release);
                }
            }
        }
        const int result = __real_unlinkat(directory_fd, pathname, flags);
        if (result == 0 &&
            g_replacement_installed.load(std::memory_order_acquire)) {
            struct stat status_buffer {};
            if (::fstatat(directory_fd, pathname, &status_buffer,
                          AT_SYMLINK_NOFOLLOW) != 0 && errno == ENOENT) {
                g_foreign_replacement_deleted.store(true,
                                                     std::memory_order_release);
            }
        }
        return result;
    }
    return __real_unlinkat(directory_fd, pathname, flags);
}

int main() {
    try {
        TestState state;
        TemporaryDirectory root;
        const fs::path final_path = root.path() / "report.json";
        const fs::path displaced = root.path() / kDisplacedOriginalName;
        const std::string old_payload = "{\"generation\":\"old\"}\n";
        const std::string new_payload(64 * 1024 + 7, 'N');

        write_binary(final_path, old_payload);
        bool typed_error_caught = false;
        SyncAtomicFilePublicationOutcome outcome =
            SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
        SyncAtomicFilePublicationResidue residue =
            SyncAtomicFilePublicationResidue::None;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    final_path, new_payload, "unlink authority trace",
                    &fail_after_payload, nullptr);
        } catch (const SyncAtomicFilePublicationError& error) {
            typed_error_caught = true;
            outcome = error.outcome();
            residue = error.residue();
        }
        g_arm_replacement.store(false, std::memory_order_release);

        state.check(
            typed_error_caught &&
                outcome == SyncAtomicFilePublicationOutcome::NotPublished &&
                residue ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
            "pre-publication failure reports exact outcome and residue");
        state.check(g_unlinkat_calls.load(std::memory_order_acquire) == 0,
                    "failure handling performs no pathname deletion");
        state.check(
            !g_replacement_installed.load(std::memory_order_acquire) &&
                !g_foreign_replacement_deleted.load(std::memory_order_acquire),
            "no check-use window can delete a foreign replacement");
        state.check(read_binary(final_path) == old_payload,
                    "failure preserves the prior final generation");
        const std::vector<fs::path> residue_temps =
            publication_temps(root.path());
        state.check(residue_temps.size() == 1 &&
                        is_private_empty_regular_file(residue_temps.front()),
                    "exact temp descriptor is sanitized and residue is retained");
        state.check(!fs::exists(displaced),
                    "test wrapper never displaced the writer inode");
        for (const fs::path& temp : residue_temps) fs::remove(temp);

        g_unlinkat_calls.store(0, std::memory_order_release);
        g_arm_replacement.store(false, std::memory_order_release);
        g_replacement_installed.store(false, std::memory_order_release);
        g_foreign_replacement_deleted.store(false,
                                             std::memory_order_release);

        NameRebindContext rebind_context{root.path(), fs::path{}, false};
        bool rebind_typed = false;
        SyncAtomicFilePublicationOutcome rebind_outcome =
            SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
        SyncAtomicFilePublicationResidue rebind_residue =
            SyncAtomicFilePublicationResidue::None;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    final_path, new_payload, "name rebind authority trace",
                    &replace_temp_name_then_fail, &rebind_context);
        } catch (const SyncAtomicFilePublicationError& error) {
            rebind_typed = true;
            rebind_outcome = error.outcome();
            rebind_residue = error.residue();
        }

        state.check(
            rebind_context.fired && rebind_typed &&
                rebind_outcome == SyncAtomicFilePublicationOutcome::NotPublished &&
                rebind_residue ==
                    SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain,
            "name rebind still reports possible residue without cleanup authority");
        state.check(g_unlinkat_calls.load(std::memory_order_acquire) == 0,
                    "name rebind failure still performs no pathname deletion");
        state.check(read_binary(rebind_context.original_temp_path) ==
                        kForeignPayload,
                    "foreign replacement remains byte-exact and unsanitized");
        struct stat replacement_status {};
        state.check(
            ::lstat(rebind_context.original_temp_path.c_str(),
                    &replacement_status) == 0 &&
                (replacement_status.st_mode & 0044) == 0044,
            "descriptor sanitation does not chmod the foreign replacement");
        state.check(is_private_empty_regular_file(displaced),
                    "sanitation follows the exact writer descriptor after name rebind");
        state.check(read_binary(final_path) == old_payload,
                    "name rebind failure preserves the prior final generation");

        std::error_code cleanup_error;
        fs::remove(rebind_context.original_temp_path, cleanup_error);
        cleanup_error.clear();
        fs::remove(displaced, cleanup_error);
        return state.finish();
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        return 2;
    }
}
