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
#include <linux/fs.h>
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
// 0: disabled, 1: replace the final name immediately before displacement,
// 2: recreate the final name immediately after successful displacement.
std::atomic<int> g_rename_race_mode{0};
std::atomic<bool> g_rename_race_injected{false};

constexpr const char* kConditionalVictimName = "conditional-victim.txt";
constexpr const char* kConditionalReplacementName =
    ".conditional-race-replacement";
constexpr const char* kConditionalSavedOriginalName =
    ".conditional-race-saved-original";
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
            if (fs::create_directory(path_, ec)) {
                if (::chmod(path_.c_str(), 0700) != 0) {
                    throw std::runtime_error(
                        "could not protect unlink-authority test directory");
                }
                return;
            }
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

anonsync::SyncPosixRegularFileSnapshotMetadata file_metadata(
    const fs::path& path) {
    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), flags);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        throw std::runtime_error("could not open conditional-removal fixture");
    }
    try {
        const auto metadata =
            anonsync::observe_sync_posix_regular_file_descriptor_or_throw(
                descriptor,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "conditional-removal fixture");
        (void)::close(descriptor);
        return metadata;
    } catch (...) {
        (void)::close(descriptor);
        throw;
    }
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


extern "C" int __real_renameat2(int old_directory_fd,
                                  const char* old_path,
                                  int new_directory_fd,
                                  const char* new_path,
                                  unsigned int flags);

extern "C" int __wrap_renameat2(int old_directory_fd,
                                  const char* old_path,
                                  int new_directory_fd,
                                  const char* new_path,
                                  unsigned int flags) {
    const int mode = g_rename_race_mode.load(std::memory_order_acquire);
    const bool is_target_displacement =
        mode != 0 && old_path != nullptr && new_path != nullptr &&
        std::string(old_path) == kConditionalVictimName &&
        is_publication_temp_name(new_path) &&
        flags == RENAME_NOREPLACE;
    if (!is_target_displacement) {
        return __real_renameat2(
            old_directory_fd, old_path, new_directory_fd, new_path, flags);
    }

    g_rename_race_mode.store(0, std::memory_order_release);
    if (mode == 1) {
        if (::renameat(
                old_directory_fd, kConditionalVictimName,
                old_directory_fd, kConditionalSavedOriginalName) != 0 ||
            ::renameat(
                old_directory_fd, kConditionalReplacementName,
                old_directory_fd, kConditionalVictimName) != 0) {
            errno = EIO;
            return -1;
        }
        g_rename_race_injected.store(true, std::memory_order_release);
        return __real_renameat2(
            old_directory_fd, old_path, new_directory_fd, new_path, flags);
    }

    const int result = __real_renameat2(
        old_directory_fd, old_path, new_directory_fd, new_path, flags);
    if (result == 0) {
        if (::renameat(
                old_directory_fd, kConditionalReplacementName,
                old_directory_fd, kConditionalVictimName) != 0) {
            errno = EIO;
            return -1;
        }
        g_rename_race_injected.store(true, std::memory_order_release);
    }
    return result;
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

        anonsync::SyncDirectoryAuthority root_authority =
            anonsync::SyncDirectoryAuthority::open_or_throw(
                fs::absolute(root.path()), "conditional-removal test root");
        const fs::path victim = root.path() / kConditionalVictimName;
        const fs::path replacement =
            root.path() / kConditionalReplacementName;
        const fs::path saved_original =
            root.path() / kConditionalSavedOriginalName;
        const std::string expected_bytes = "expected deletion target";
        const std::string replacement_bytes = "racing replacement survives";

        g_unlinkat_calls.store(0, std::memory_order_release);
        write_binary(victim, expected_bytes);
        const auto expected_metadata = file_metadata(victim);
        anonsync::remove_sync_file_atomically_if_expected_under_directory_or_throw(
            root_authority, kConditionalVictimName, expected_metadata,
            "conditional-removal success");
        state.check(
            !fs::exists(victim) && publication_temps(root.path()).empty() &&
                g_unlinkat_calls.load(std::memory_order_acquire) == 1,
            "conditional removal unlinks only its atomically displaced private name");

        constexpr std::string_view expected_bytes_sha256 =
            "cedf4accffdf531b694744c47c659475aa678b4ae4bf970874ca0957359e5326";
        g_unlinkat_calls.store(0, std::memory_order_release);
        write_binary(victim, expected_bytes);
        const auto exact_content_metadata = file_metadata(victim);
        anonsync::
            remove_sync_file_atomically_if_expected_content_under_directory_or_throw(
                root_authority, kConditionalVictimName,
                exact_content_metadata, expected_bytes_sha256,
                "content-bound conditional-removal success");
        state.check(
            !fs::exists(victim) && publication_temps(root.path()).empty() &&
                g_unlinkat_calls.load(std::memory_order_acquire) == 1,
            "content-bound removal hashes and unlinks only the exact displaced inode");

        g_unlinkat_calls.store(0, std::memory_order_release);
        write_binary(victim, expected_bytes);
        const auto wrong_digest_metadata = file_metadata(victim);
        bool wrong_digest_rejected = false;
        try {
            anonsync::
                remove_sync_file_atomically_if_expected_content_under_directory_or_throw(
                    root_authority, kConditionalVictimName,
                    wrong_digest_metadata, std::string(64U, '0'),
                    "content-bound conditional-removal mismatch");
        } catch (const std::exception& error) {
            const std::string_view message(error.what());
            wrong_digest_rejected =
                message.find("SHA-256 did not match") !=
                    std::string_view::npos &&
                message.find("restored and not removed") !=
                    std::string_view::npos;
        }
        state.check(
            wrong_digest_rejected && fs::exists(victim) &&
                read_binary(victim) == expected_bytes &&
                publication_temps(root.path()).empty() &&
                g_unlinkat_calls.load(std::memory_order_acquire) == 0,
            "content mismatch restores the exact displaced object without unlink");

        bool invalid_digest_rejected = false;
        const auto invalid_digest_metadata = file_metadata(victim);
        try {
            anonsync::
                remove_sync_file_atomically_if_expected_content_under_directory_or_throw(
                    root_authority, kConditionalVictimName,
                    invalid_digest_metadata, "invalid",
                    "content-bound conditional-removal invalid digest");
        } catch (const std::invalid_argument&) {
            invalid_digest_rejected = true;
        }
        state.check(
            invalid_digest_rejected && fs::exists(victim) &&
                read_binary(victim) == expected_bytes &&
                publication_temps(root.path()).empty(),
            "invalid content authority is rejected before namespace mutation");
        fs::remove(victim);

        write_binary(victim, expected_bytes);
        write_binary(replacement, replacement_bytes);
        const auto before_race_metadata = file_metadata(victim);
        g_rename_race_injected.store(false, std::memory_order_release);
        g_rename_race_mode.store(1, std::memory_order_release);
        bool before_race_rejected = false;
        try {
            anonsync::remove_sync_file_atomically_if_expected_under_directory_or_throw(
                root_authority, kConditionalVictimName,
                before_race_metadata, "conditional-removal before-race");
        } catch (const std::exception& error) {
            before_race_rejected =
                std::string_view(error.what()).find(
                    "restored and not removed") != std::string_view::npos;
        }
        state.check(
            g_rename_race_injected.load(std::memory_order_acquire) &&
                before_race_rejected &&
                read_binary(victim) == replacement_bytes &&
                read_binary(saved_original) == expected_bytes &&
                publication_temps(root.path()).empty(),
            "replacement winning before displacement is restored and never unlinked");
        fs::remove(victim);
        fs::remove(saved_original);

        write_binary(victim, expected_bytes);
        write_binary(replacement, replacement_bytes);
        const auto after_race_metadata = file_metadata(victim);
        g_rename_race_injected.store(false, std::memory_order_release);
        g_rename_race_mode.store(2, std::memory_order_release);
        bool after_race_rejected = false;
        try {
            anonsync::remove_sync_file_atomically_if_expected_under_directory_or_throw(
                root_authority, kConditionalVictimName,
                after_race_metadata, "conditional-removal after-race");
        } catch (const std::exception& error) {
            after_race_rejected =
                std::string_view(error.what()).find(
                    "recreated during removal") != std::string_view::npos;
        }
        state.check(
            g_rename_race_injected.load(std::memory_order_acquire) &&
                after_race_rejected &&
                read_binary(victim) == replacement_bytes &&
                publication_temps(root.path()).empty(),
            "replacement appearing after displacement is preserved and reported");
        fs::remove(victim);
        return state.finish();
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << '\n';
        return 2;
    }
}
