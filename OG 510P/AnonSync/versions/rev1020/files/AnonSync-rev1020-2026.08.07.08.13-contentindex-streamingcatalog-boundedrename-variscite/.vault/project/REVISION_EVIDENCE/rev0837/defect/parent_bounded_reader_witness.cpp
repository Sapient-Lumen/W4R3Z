#include <cerrno>
#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace fs = std::filesystem;
std::string read_regular_file_bounded_no_symlink_or_throw(const fs::path& path,
                                                          std::uint64_t maximum_bytes,
                                                          const std::string& label) {
    if (maximum_bytes == 0) throw std::runtime_error(label + " maximum bytes must be positive");
#if defined(_WIN32)
    std::error_code ec;
    const fs::file_status status = fs::symlink_status(path, ec);
    if (ec) throw std::runtime_error(label + " could not inspect file: " + ec.message());
    if (!fs::exists(status)) throw std::runtime_error(label + " file is missing");
    if (fs::is_symlink(status)) throw std::runtime_error(label + " file must not be a symlink");
    if (!fs::is_regular_file(status)) throw std::runtime_error(label + " path is not a regular file");
    const auto size = fs::file_size(path, ec);
    if (ec) throw std::runtime_error(label + " size could not be inspected: " + ec.message());
    if (size > maximum_bytes) throw std::runtime_error(label + " exceeds bounded read limit");
    return read_file(path.string());
#else
    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    const std::string native = path.string();
    int fd = ::open(native.c_str(), flags);
    if (fd < 0) throw std::runtime_error(label + " open failed: " + std::strerror(errno));
    int saved_errno = 0;
    std::string out;
    try {
        struct stat st;
        if (::fstat(fd, &st) != 0) throw std::runtime_error(label + " fstat failed: " + std::strerror(errno));
        if (!S_ISREG(st.st_mode)) throw std::runtime_error(label + " path is not a regular file");
        if (st.st_size < 0) throw std::runtime_error(label + " file size is negative");
        if (static_cast<std::uint64_t>(st.st_size) > maximum_bytes) throw std::runtime_error(label + " exceeds bounded read limit");
        out.resize(static_cast<std::size_t>(st.st_size));
        std::size_t offset = 0;
        while (offset < out.size()) {
            const ssize_t got = ::read(fd, out.data() + offset, out.size() - offset);
            if (got < 0) {
                if (errno == EINTR) continue;
                throw std::runtime_error(label + " read failed: " + std::strerror(errno));
            }
            if (got == 0) break;
            offset += static_cast<std::size_t>(got);
        }
        out.resize(offset);
    } catch (...) {
        if (::close(fd) != 0 && saved_errno == 0) saved_errno = errno;
        throw;
    }
    if (::close(fd) != 0 && saved_errno == 0) saved_errno = errno;
    if (saved_errno != 0) throw std::runtime_error(label + " close failed: " + std::strerror(saved_errno));
    return out;
#endif
}

}  // namespace anonsync

namespace {
bool g_prefix_script = false;
int g_read_calls = 0;
constexpr int kFakeFd = 91;
}

extern "C" int __real_open(const char*, int, ...);
extern "C" int __real_fstat(int, struct stat*);
extern "C" ssize_t __real_read(int, void*, size_t);
extern "C" int __real_close(int);

extern "C" int __wrap_open(const char* path, int flags, ...) {
    if (g_prefix_script) return kFakeFd;
    return __real_open(path, flags);
}
extern "C" int __wrap_fstat(int fd, struct stat* value) {
    if (!g_prefix_script) return __real_fstat(fd, value);
    if (fd != kFakeFd || value == nullptr) { errno = EPROTO; return -1; }
    std::memset(value, 0, sizeof(*value));
    value->st_mode = S_IFREG | 0600;
    value->st_size = 3;
    value->st_dev = 7;
    value->st_ino = 9;
    return 0;
}
extern "C" ssize_t __wrap_read(int fd, void* buffer, size_t count) {
    if (!g_prefix_script) return __real_read(fd, buffer, count);
    if (fd != kFakeFd || count != 3 || g_read_calls != 0) {
        errno = EPROTO;
        return -1;
    }
    ++g_read_calls;
    std::memcpy(buffer, "abc", 3);
    return 3;
}
extern "C" int __wrap_close(int fd) {
    if (!g_prefix_script) return __real_close(fd);
    if (fd != kFakeFd) { errno = EPROTO; return -1; }
    return 0;
}

int main(int argc, char** argv) {
    try {
        if (argc == 3 && std::string(argv[1]) == "--fifo") {
            const std::string bytes =
                anonsync::read_regular_file_bounded_no_symlink_or_throw(
                    argv[2], 64, "parent FIFO witness");
            std::cout << "UNEXPECTED_RETURN bytes=" << bytes.size() << "\n";
            return 3;
        }
        if (argc == 2 && std::string(argv[1]) == "--prefix") {
            g_prefix_script = true;
            const std::string bytes =
                anonsync::read_regular_file_bounded_no_symlink_or_throw(
                    "/scripted/growing-file", 3, "parent prefix witness");
            g_prefix_script = false;
            const bool accepted_prefix = bytes == "abc" && g_read_calls == 1;
            std::cout << (accepted_prefix ? "ACCEPTED_PREFIX" : "UNEXPECTED")
                      << " returned_bytes=" << bytes.size()
                      << " read_calls=" << g_read_calls
                      << " simulated_trailing_bytes=1\n";
            return accepted_prefix ? 0 : 4;
        }
        std::cerr << "usage: witness --fifo PATH | --prefix\n";
        return 2;
    } catch (const std::exception& error) {
        g_prefix_script = false;
        std::cerr << "REJECTED: " << error.what() << "\n";
        return 5;
    }
}
