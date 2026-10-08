#include "sync_bounded_regular_file.hpp"

#include "sync_bounded_regular_file_limits.hpp"
#if !defined(_WIN32)
#include "sync_posix_descriptor_snapshot.hpp"
#endif

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <system_error>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

using sync_bounded_regular_file_detail::checked_maximum_size_or_throw;
using sync_bounded_regular_file_detail::kReadChunkBytes;
using sync_bounded_regular_file_detail::next_read_size;

enum class BoundedRegularFilePolicy : unsigned char {
    ordinary,
    single_link,
    private_owner_mode_0600,
};

[[nodiscard]] bool policy_requires_single_link(
    BoundedRegularFilePolicy policy) noexcept {
    return policy != BoundedRegularFilePolicy::ordinary;
}

#if defined(_WIN32)

[[nodiscard]] std::string windows_error_message(DWORD error) {
    return std::system_category().message(static_cast<int>(error));
}

[[nodiscard]] std::uint64_t windows_file_size(
    const BY_HANDLE_FILE_INFORMATION& information) {
    return (static_cast<std::uint64_t>(information.nFileSizeHigh) << 32U) |
           static_cast<std::uint64_t>(information.nFileSizeLow);
}

[[nodiscard]] bool same_filetime(const FILETIME& left,
                                 const FILETIME& right) {
    return left.dwLowDateTime == right.dwLowDateTime &&
           left.dwHighDateTime == right.dwHighDateTime;
}

[[nodiscard]] bool same_windows_file_identity_and_snapshot(
    const BY_HANDLE_FILE_INFORMATION& before,
    const BY_HANDLE_FILE_INFORMATION& after) {
    return before.dwVolumeSerialNumber == after.dwVolumeSerialNumber &&
           before.nFileIndexHigh == after.nFileIndexHigh &&
           before.nFileIndexLow == after.nFileIndexLow &&
           windows_file_size(before) == windows_file_size(after) &&
           same_filetime(before.ftLastWriteTime, after.ftLastWriteTime) &&
           before.dwFileAttributes == after.dwFileAttributes;
}

void require_windows_regular_file_or_throw(
    HANDLE handle,
    const BY_HANDLE_FILE_INFORMATION& information,
    BoundedRegularFilePolicy policy,
    const std::string& label) {
    const DWORD file_type = ::GetFileType(handle);
    if (file_type != FILE_TYPE_DISK) {
        throw std::runtime_error(label + " path is not a disk file");
    }
    if ((information.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) {
        throw std::runtime_error(label +
                                 " final path component must not be a reparse point");
    }
    if ((information.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0) {
        throw std::runtime_error(label + " path is not a regular file");
    }
    if ((information.dwFileAttributes & FILE_ATTRIBUTE_DEVICE) != 0) {
        throw std::runtime_error(label + " path is a device, not a regular file");
    }
    if (policy_requires_single_link(policy) &&
        information.nNumberOfLinks != 1) {
        throw std::runtime_error(label +
                                 " path is not a single-link regular file");
    }
}

std::string read_windows_file_or_throw(const std::filesystem::path& path,
                                       std::size_t maximum_size,
                                       BoundedRegularFilePolicy policy,
                                       const std::string& label) {
    if (policy == BoundedRegularFilePolicy::private_owner_mode_0600) {
        throw std::runtime_error(
            label +
            " private-file admission requires an owner-only DACL proof that is not implemented on Windows");
    }
    HANDLE handle = ::CreateFileW(
        path.c_str(),
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT |
            FILE_FLAG_SEQUENTIAL_SCAN,
        nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        const DWORD error = ::GetLastError();
        throw std::runtime_error(label + " open failed: " +
                                 windows_error_message(error));
    }

    std::string bytes;
    try {
        BY_HANDLE_FILE_INFORMATION before{};
        if (!::GetFileInformationByHandle(handle, &before)) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " initial handle inspection failed: " +
                                     windows_error_message(error));
        }
        require_windows_regular_file_or_throw(
            handle, before, policy, label);
        const std::uint64_t before_size = windows_file_size(before);
        if (before_size > static_cast<std::uint64_t>(maximum_size)) {
            throw std::runtime_error(label + " exceeds bounded read limit");
        }

        bytes.reserve(static_cast<std::size_t>(before_size));
        std::array<char, kReadChunkBytes> buffer{};
        for (;;) {
            const std::size_t request = next_read_size(bytes.size(), maximum_size);
            DWORD received = 0;
            if (!::ReadFile(handle,
                            buffer.data(),
                            static_cast<DWORD>(request),
                            &received,
                            nullptr)) {
                const DWORD error = ::GetLastError();
                if (error == ERROR_HANDLE_EOF) break;
                throw std::runtime_error(label + " read failed: " +
                                         windows_error_message(error));
            }
            if (received == 0) break;
            if (static_cast<std::size_t>(received) >
                maximum_size - bytes.size()) {
                throw std::runtime_error(label + " exceeds bounded read limit");
            }
            bytes.append(buffer.data(), static_cast<std::size_t>(received));
        }

        BY_HANDLE_FILE_INFORMATION after{};
        if (!::GetFileInformationByHandle(handle, &after)) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " final handle inspection failed: " +
                                     windows_error_message(error));
        }
        require_windows_regular_file_or_throw(
            handle, after, policy, label);
        if (!same_windows_file_identity_and_snapshot(before, after) ||
            windows_file_size(after) !=
                static_cast<std::uint64_t>(bytes.size())) {
            throw std::runtime_error(label +
                                     " changed while its bounded bytes were read");
        }
    } catch (...) {
        (void)::CloseHandle(handle);
        throw;
    }

    if (!::CloseHandle(handle)) {
        const DWORD error = ::GetLastError();
        throw std::runtime_error(label + " close failed: " +
                                 windows_error_message(error));
    }
    return bytes;
}

#else

[[nodiscard]] int posix_open_flags() {
    int flags = O_RDONLY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
#ifdef O_NONBLOCK
    flags |= O_NONBLOCK;
#endif
#ifdef O_NOCTTY
    flags |= O_NOCTTY;
#endif
    return flags;
}

void close_posix_fd_or_throw(int fd, const std::string& label) {
    if (::close(fd) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " close failed: " +
                                 std::strerror(error));
    }
}

void require_private_posix_file_or_throw(
    const struct stat& status,
    const std::string& label,
    bool final_observation) {
    const std::string phase = final_observation ? " stopped being" : " is not";
    if (!S_ISREG(status.st_mode)) {
        throw std::runtime_error(label + phase + " a regular file");
    }
    if (status.st_nlink != 1) {
        throw std::runtime_error(label + phase + " a single-link file");
    }
    if (status.st_uid != ::geteuid()) {
        throw std::runtime_error(label + phase + " owned by the effective user");
    }
    if ((status.st_mode & 07777U) != (S_IRUSR | S_IWUSR)) {
        throw std::runtime_error(label + phase + " exact mode 0600");
    }
}

[[nodiscard]] struct stat observe_private_posix_file_or_throw(
    int fd,
    const std::string& label,
    bool final_observation) {
    struct stat status{};
    if (::fstat(fd, &status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + (final_observation ? " final" : " initial") +
            " private-file fstat failed: " + std::strerror(error));
    }
    require_private_posix_file_or_throw(status, label, final_observation);
    return status;
}

[[nodiscard]] bool same_private_posix_identity_and_policy(
    const struct stat& before,
    const struct stat& after) noexcept {
    return before.st_dev == after.st_dev && before.st_ino == after.st_ino &&
        before.st_uid == after.st_uid && before.st_gid == after.st_gid &&
        before.st_mode == after.st_mode && before.st_nlink == after.st_nlink;
}

std::string read_posix_file_or_throw(const std::filesystem::path& path,
                                     std::size_t maximum_size,
                                     BoundedRegularFilePolicy policy,
                                     const std::string& label) {
#if !defined(O_NOFOLLOW) || !defined(O_NONBLOCK)
    (void)path;
    (void)maximum_size;
    (void)policy;
    throw std::runtime_error(
        label +
        " secure bounded regular-file reads require O_NOFOLLOW and O_NONBLOCK");
#else
    const std::string native = path.string();
    const int fd = ::open(native.c_str(), posix_open_flags());
    if (fd < 0) {
        const int error = errno;
        throw std::runtime_error(label + " open failed: " +
                                 std::strerror(error));
    }

    std::string bytes;
    try {
#ifndef O_CLOEXEC
        const int descriptor_flags = ::fcntl(fd, F_GETFD);
        if (descriptor_flags < 0 ||
            ::fcntl(fd, F_SETFD, descriptor_flags | FD_CLOEXEC) != 0) {
            const int error = errno;
            throw std::runtime_error(label + " close-on-exec setup failed: " +
                                     std::strerror(error));
        }
#endif
        std::optional<struct stat> private_before;
        if (policy == BoundedRegularFilePolicy::private_owner_mode_0600) {
            private_before =
                observe_private_posix_file_or_throw(fd, label, false);
        }
        const auto link_policy = policy_requires_single_link(policy)
            ? SyncPosixDescriptorLinkPolicy::exactly_one
            : SyncPosixDescriptorLinkPolicy::stable_named_object;
        auto snapshot =
            FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
                fd, static_cast<std::uint64_t>(maximum_size), link_policy, label);
        bytes = std::move(snapshot).take_bytes();
        if (private_before.has_value()) {
            const struct stat private_after =
                observe_private_posix_file_or_throw(fd, label, true);
            if (!same_private_posix_identity_and_policy(
                    *private_before, private_after)) {
                throw std::runtime_error(
                    label + " private-file identity or access policy changed while its bytes were read");
            }
        }
    } catch (...) {
        (void)::close(fd);
        throw;
    }

    close_posix_fd_or_throw(fd, label);
    return bytes;
#endif
}
#endif

}  // namespace

static std::string read_sync_bounded_regular_file_impl_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    BoundedRegularFilePolicy policy,
    const std::string& label) {
    const std::size_t maximum_size =
        checked_maximum_size_or_throw(maximum_bytes, label);
    const auto& native_path = path.native();
    if (native_path.find(std::filesystem::path::value_type{}) !=
        std::filesystem::path::string_type::npos) {
        throw std::runtime_error(label + " path contains an embedded NUL");
    }
#if defined(_WIN32)
    return read_windows_file_or_throw(path, maximum_size, policy, label);
#else
    return read_posix_file_or_throw(path, maximum_size, policy, label);
#endif
}

std::string read_sync_bounded_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label) {
    return read_sync_bounded_regular_file_impl_or_throw(
        path, maximum_bytes, BoundedRegularFilePolicy::ordinary, label);
}

std::string read_sync_bounded_single_link_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label) {
    return read_sync_bounded_regular_file_impl_or_throw(
        path, maximum_bytes, BoundedRegularFilePolicy::single_link, label);
}

std::string read_sync_bounded_private_regular_file_no_symlink_or_throw(
    const std::filesystem::path& path,
    std::uint64_t maximum_bytes,
    const std::string& label) {
    return read_sync_bounded_regular_file_impl_or_throw(
        path, maximum_bytes,
        BoundedRegularFilePolicy::private_owner_mode_0600, label);
}

}  // namespace anonsync
