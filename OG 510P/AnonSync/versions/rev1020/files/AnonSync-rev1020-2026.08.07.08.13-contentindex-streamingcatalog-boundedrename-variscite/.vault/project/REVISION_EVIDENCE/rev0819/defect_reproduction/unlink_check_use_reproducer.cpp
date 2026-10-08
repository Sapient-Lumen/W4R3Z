#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"

#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {
namespace fs = std::filesystem;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationCutpoint;
using anonsync::atomic_file_publication_detail::AtomicFilePublicationObservation;

std::atomic<int> g_unlinkat_calls{0};
std::atomic<bool> g_arm{false};
std::atomic<bool> g_replacement_installed{false};
std::atomic<bool> g_foreign_deleted{false};
constexpr const char* kDisplaced = ".anonsync-reproducer-displaced";
constexpr const char* kForeign = "foreign-replacement";

class Injected final : public std::runtime_error {
public:
    Injected() : std::runtime_error("injected after payload") {}
};

void write_file(const fs::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("open failed");
    out.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!out) throw std::runtime_error("write failed");
}

std::string read_file(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return {};
    return std::string(std::istreambuf_iterator<char>(in),
                       std::istreambuf_iterator<char>());
}

bool write_all(int fd, const char* data, std::size_t size) noexcept {
    while (size != 0) {
        const ssize_t n = ::write(fd, data, size);
        if (n < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (n == 0) return false;
        data += n;
        size -= static_cast<std::size_t>(n);
    }
    return true;
}

void fail_after_payload(const AtomicFilePublicationObservation& observation,
                        void*) {
    if (observation.cutpoint == AtomicFilePublicationCutpoint::PayloadWritten) {
        g_arm.store(true, std::memory_order_release);
        throw Injected();
    }
}
}  // namespace

extern "C" int __real_unlinkat(int, const char*, int);
extern "C" int __wrap_unlinkat(int dirfd, const char* path, int flags) {
    g_unlinkat_calls.fetch_add(1, std::memory_order_relaxed);
    if (path != nullptr && g_arm.exchange(false, std::memory_order_acq_rel)) {
        (void)__real_unlinkat(dirfd, kDisplaced, 0);
        if (::renameat(dirfd, path, dirfd, kDisplaced) == 0) {
            int fd;
            do {
                fd = ::openat(dirfd, path, O_WRONLY | O_CREAT | O_EXCL, 0644);
            } while (fd < 0 && errno == EINTR);
            if (fd >= 0) {
                const std::string bytes = kForeign;
                const bool ok = write_all(fd, bytes.data(), bytes.size());
                int rc;
                do {
                    rc = ::close(fd);
                } while (rc != 0 && errno == EINTR);
                if (ok && rc == 0) {
                    g_replacement_installed.store(true,
                                                  std::memory_order_release);
                }
            }
        }
        const int rc = __real_unlinkat(dirfd, path, flags);
        if (rc == 0 && g_replacement_installed.load(std::memory_order_acquire)) {
            struct stat st {};
            if (::fstatat(dirfd, path, &st, AT_SYMLINK_NOFOLLOW) != 0 &&
                errno == ENOENT) {
                g_foreign_deleted.store(true, std::memory_order_release);
            }
        }
        return rc;
    }
    return __real_unlinkat(dirfd, path, flags);
}

int main() {
    namespace fs = std::filesystem;
    const auto seed = static_cast<std::uint64_t>(
        std::chrono::steady_clock::now().time_since_epoch().count());
    const fs::path root = fs::temp_directory_path() /
                          ("anonsync-unlink-reproducer-" +
                           std::to_string(::getpid()) + "-" +
                           std::to_string(seed));
    try {
        fs::create_directory(root);
        const fs::path final_path = root / "report.json";
        const std::string old_payload = "old-generation";
        write_file(final_path, old_payload);
        bool threw = false;
        try {
            anonsync::atomic_file_publication_detail::
                write_sync_json_file_atomically_with_observer_or_throw(
                    final_path, std::string(8193, 'N'), "reproducer",
                    &fail_after_payload, nullptr);
        } catch (...) {
            threw = true;
        }
        g_arm.store(false, std::memory_order_release);
        const bool prior_final_preserved = read_file(final_path) == old_payload;
        const bool vulnerable = threw &&
            g_replacement_installed.load(std::memory_order_acquire) &&
            g_foreign_deleted.load(std::memory_order_acquire);
        std::cout << "{\n"
                  << "  \"threw\": " << (threw ? "true" : "false") << ",\n"
                  << "  \"unlinkat_calls\": "
                  << g_unlinkat_calls.load(std::memory_order_acquire) << ",\n"
                  << "  \"replacement_installed\": "
                  << (g_replacement_installed.load(std::memory_order_acquire)
                          ? "true" : "false") << ",\n"
                  << "  \"foreign_replacement_deleted\": "
                  << (g_foreign_deleted.load(std::memory_order_acquire)
                          ? "true" : "false") << ",\n"
                  << "  \"prior_final_preserved\": "
                  << (prior_final_preserved ? "true" : "false") << ",\n"
                  << "  \"vulnerable\": "
                  << (vulnerable ? "true" : "false") << "\n}\n";
        std::error_code ec;
        fs::remove_all(root, ec);
        return vulnerable ? 1 : 0;
    } catch (const std::exception& error) {
        std::cerr << "fatal: " << error.what() << '\n';
        std::error_code ec;
        fs::remove_all(root, ec);
        return 2;
    }
}
