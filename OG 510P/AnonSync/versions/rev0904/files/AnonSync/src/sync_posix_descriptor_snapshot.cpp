#include "sync_posix_descriptor_snapshot.hpp"

#if !defined(_WIN32)

#include "sync_bounded_regular_file_limits.hpp"

#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>

#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

using sync_bounded_regular_file_detail::checked_maximum_size_or_throw;
using sync_bounded_regular_file_detail::kReadChunkBytes;
using sync_bounded_regular_file_detail::next_read_size;

[[nodiscard]] bool same_timespec(const timespec& left,
                                 const timespec& right) noexcept {
    return left.tv_sec == right.tv_sec && left.tv_nsec == right.tv_nsec;
}

[[nodiscard]] bool same_modification_snapshot(const struct stat& before,
                                              const struct stat& after) {
#if defined(__APPLE__)
    return same_timespec(before.st_mtimespec, after.st_mtimespec) &&
           same_timespec(before.st_ctimespec, after.st_ctimespec);
#elif defined(__linux__) || defined(__FreeBSD__) || defined(__NetBSD__) || \
    defined(__OpenBSD__)
    return same_timespec(before.st_mtim, after.st_mtim) &&
           same_timespec(before.st_ctim, after.st_ctim);
#else
    return before.st_mtime == after.st_mtime &&
           before.st_ctime == after.st_ctime;
#endif
}

void require_link_policy_or_throw(
    const struct stat& status,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label,
    bool final_observation) {
    const char* phase = final_observation ? " stopped being" : " is not";
    if (status.st_nlink == 0) {
        throw std::runtime_error(
            label + phase + " a named regular-file object");
    }
    if (link_policy == SyncPosixDescriptorLinkPolicy::exactly_one &&
        status.st_nlink != 1) {
        throw std::runtime_error(
            label + phase + " a single-link regular file");
    }
}

void require_regular_snapshot_or_throw(
    const struct stat& status,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label,
    bool final_observation) {
    if (!S_ISREG(status.st_mode)) {
        if (final_observation) {
            throw std::runtime_error(
                label + " stopped being an observable regular file");
        }
        throw std::runtime_error(label + " path is not a regular file");
    }
    if (status.st_size < 0) {
        if (final_observation) {
            throw std::runtime_error(
                label + " stopped being an observable regular file");
        }
        throw std::runtime_error(label + " file size is negative");
    }
    require_link_policy_or_throw(status, link_policy, label,
                                 final_observation);
}

}  // namespace

FrozenSyncPosixRegularFileSnapshot
FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw(
    int descriptor,
    std::uint64_t maximum_bytes,
    SyncPosixDescriptorLinkPolicy link_policy,
    const std::string& label) {
    const std::size_t maximum_size =
        checked_maximum_size_or_throw(maximum_bytes, label);

    struct stat before {};
    if (::fstat(descriptor, &before) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " initial fstat failed: " +
                                 std::strerror(error));
    }
    require_regular_snapshot_or_throw(before, link_policy, label, false);
    if (static_cast<std::uint64_t>(before.st_size) > maximum_bytes) {
        throw std::runtime_error(label + " exceeds bounded read limit");
    }

    std::string bytes;
    bytes.reserve(static_cast<std::size_t>(before.st_size));
    std::array<char, kReadChunkBytes> buffer {};
    for (;;) {
        const std::size_t request =
            next_read_size(bytes.size(), maximum_size);
        const off_t offset = static_cast<off_t>(bytes.size());
        ssize_t received = -1;
        do {
            received = ::pread(descriptor, buffer.data(), request, offset);
        } while (received < 0 && errno == EINTR);
        if (received < 0) {
            const int error = errno;
            throw std::runtime_error(label + " positional read failed: " +
                                     std::strerror(error));
        }
        if (received == 0) break;
        const std::size_t received_size =
            static_cast<std::size_t>(received);
        if (received_size > maximum_size - bytes.size()) {
            throw std::runtime_error(label + " exceeds bounded read limit");
        }
        bytes.append(buffer.data(), received_size);
    }

    struct stat after {};
    if (::fstat(descriptor, &after) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " final fstat failed: " +
                                 std::strerror(error));
    }
    require_regular_snapshot_or_throw(after, link_policy, label, true);

    const bool identity_stable = before.st_dev == after.st_dev &&
                                 before.st_ino == after.st_ino;
    const bool size_stable = before.st_size == after.st_size &&
                             static_cast<std::uint64_t>(after.st_size) ==
                                 static_cast<std::uint64_t>(bytes.size());
    const bool topology_stable = before.st_nlink == after.st_nlink;
    if (!identity_stable || !size_stable || !topology_stable ||
        !same_modification_snapshot(before, after)) {
        throw std::runtime_error(
            label + " changed while its bounded bytes were read");
    }

    return FrozenSyncPosixRegularFileSnapshot(std::move(bytes));
}

}  // namespace anonsync

#endif
