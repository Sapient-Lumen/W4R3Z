#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"
#include "sync_atomic_file_publication_state.hpp"
#include "sync_directory_authority_internal.hpp"
#include "sync_process_incarnation.hpp"

#if !defined(_WIN32)
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_posix_directory_resolution.hpp"
#endif

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iomanip>
#include <limits>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <fcntl.h>
#if defined(__linux__)
#include <linux/fs.h>
#include <stdio.h>
#endif
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

namespace fs = std::filesystem;

using atomic_file_publication_detail::AtomicFilePublicationCutpoint;
using atomic_file_publication_detail::AtomicFilePublicationDisposition;
using atomic_file_publication_detail::AtomicFilePublicationObservation;
using atomic_file_publication_detail::AtomicFilePublicationObserver;
using atomic_file_publication_detail::AtomicFilePublicationProgress;

constexpr std::size_t kMaximumTempCreateAttempts = 4096;
constexpr std::string_view kPublicationTempPrefix =
    ".anonsync-publish-v1-";
constexpr std::string_view kPublicationTempSuffix = ".tmp";
constexpr std::uint64_t kFnvOffsetBasis = UINT64_C(14695981039346656037);
constexpr std::uint64_t kFnvPrime = UINT64_C(1099511628211);

std::atomic<std::uint64_t> g_publication_nonce{1};

void observe_publication_frontier(
    AtomicFilePublicationObserver observer,
    void* observer_context,
    AtomicFilePublicationCutpoint cutpoint,
    const AtomicFilePublicationProgress& progress) {
    if (observer == nullptr) return;
    observer(AtomicFilePublicationObservation{
                 cutpoint,
                 progress.outcome(),
                 progress.residue()},
             observer_context);
}

std::string publication_failure_message(
    const std::string& label,
    SyncAtomicFilePublicationOutcome outcome,
    SyncAtomicFilePublicationResidue residue,
    const std::string& detail) {
    const std::string residue_notice =
        residue == SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain
            ? "; a temporary artifact may remain; no pathname cleanup authority is implied"
            : "";
    switch (outcome) {
        case SyncAtomicFilePublicationOutcome::NotPublished:
            return label +
                   " failed before this attempt published the final directory entry: " +
                   detail + residue_notice;
        case SyncAtomicFilePublicationOutcome::PublishedDurabilityIndeterminate:
            return label +
                   " published the final directory entry, but parent-directory durability is indeterminate: " +
                   detail + residue_notice;
        case SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced:
            return label +
                   " published and directory-synced the final entry, but finalization failed: " +
                   detail + residue_notice;
    }
    return label + " publication failed: " + detail + residue_notice;
}

[[noreturn]] void rethrow_publication_failure(
    const std::string& label,
    const AtomicFilePublicationProgress& progress) {
    const SyncAtomicFilePublicationOutcome outcome = progress.outcome();
    const SyncAtomicFilePublicationResidue residue = progress.residue();
    try {
        throw;
    } catch (const std::exception& error) {
        std::throw_with_nested(SyncAtomicFilePublicationError(
            outcome, residue,
            publication_failure_message(label, outcome, residue, error.what())));
    } catch (...) {
        std::throw_with_nested(SyncAtomicFilePublicationError(
            outcome, residue,
            publication_failure_message(label, outcome, residue,
                                        "non-standard exception")));
    }
}

std::string system_error_text(int error) {
    return std::error_code(error, std::generic_category()).message();
}

std::uint64_t fnv1a_64(const std::string& value) noexcept {
    std::uint64_t digest = kFnvOffsetBasis;
    for (unsigned char byte : value) {
        digest ^= static_cast<std::uint64_t>(byte);
        digest *= kFnvPrime;
    }
    return digest;
}

std::string hex_u64(std::uint64_t value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0') << std::setw(16) << value;
    return out.str();
}

std::uint64_t current_process_id() noexcept {
#if defined(_WIN32)
    return static_cast<std::uint64_t>(::GetCurrentProcessId());
#else
    return static_cast<std::uint64_t>(::getpid());
#endif
}

[[nodiscard]] bool is_lowercase_hex(std::string_view value) noexcept {
    for (const char byte : value) {
        if (!((byte >= '0' && byte <= '9') ||
              (byte >= 'a' && byte <= 'f'))) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool publication_temp_basename_is_exact(
    std::string_view basename) noexcept {
    if (!basename.starts_with(kPublicationTempPrefix) ||
        !basename.ends_with(kPublicationTempSuffix)) {
        return false;
    }
    const std::size_t body_begin = kPublicationTempPrefix.size();
    const std::size_t body_size =
        basename.size() - body_begin - kPublicationTempSuffix.size();
    if (body_size != 50U) return false;
    const std::string_view body = basename.substr(body_begin, body_size);
    return body[16U] == '-' && body[33U] == '-' &&
           is_lowercase_hex(body.substr(0U, 16U)) &&
           is_lowercase_hex(body.substr(17U, 16U)) &&
           is_lowercase_hex(body.substr(34U, 16U));
}

std::string next_temp_basename(const std::string& final_basename) {
    const std::uint64_t nonce =
        g_publication_nonce.fetch_add(1, std::memory_order_relaxed);
    return std::string(kPublicationTempPrefix) +
           hex_u64(fnv1a_64(final_basename)) + "-" +
           hex_u64(current_process_id()) + "-" + hex_u64(nonce) +
           std::string(kPublicationTempSuffix);
}

std::span<const unsigned char> byte_span(const std::string& payload) noexcept {
    return {reinterpret_cast<const unsigned char*>(payload.data()),
            payload.size()};
}

bool bytes_equal(std::string_view observed,
                 std::span<const unsigned char> expected) noexcept {
    if (observed.size() != expected.size()) return false;
    return std::equal(
        observed.begin(), observed.end(), expected.begin(),
        [](char left, unsigned char right) {
            return static_cast<unsigned char>(left) == right;
        });
}

fs::path absolute_lexically_normal_path_or_throw(
    const fs::path& raw_path,
    const std::string& label) {
    if (raw_path.empty()) throw std::invalid_argument(label + " is empty");
    std::error_code ec;
    fs::path absolute = fs::absolute(raw_path, ec);
    if (ec) {
        throw std::invalid_argument(label + " could not be resolved: " +
                                    ec.message());
    }
    return absolute.lexically_normal();
}

std::string final_basename_or_throw(const fs::path& final_path,
                                    const std::string& label) {
    const fs::path filename = final_path.filename();
    const std::string basename = filename.string();
    if (basename.empty() || basename == "." || basename == "..") {
        throw std::runtime_error(label + " must name a file");
    }
    if (basename.find('\0') != std::string::npos ||
        basename.find('/') != std::string::npos ||
        basename.find('\\') != std::string::npos) {
        throw std::runtime_error(label + " filename is not one path component");
    }
    return basename;
}

#if defined(_WIN32)

std::string windows_error_text(DWORD error) {
    char* message = nullptr;
    const DWORD length = ::FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
            FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        error,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        reinterpret_cast<char*>(&message),
        0,
        nullptr);
    std::string out = length != 0 && message != nullptr
                          ? std::string(message, length)
                          : "Windows error " + std::to_string(error);
    if (message != nullptr) ::LocalFree(message);
    while (!out.empty() && (out.back() == '\r' || out.back() == '\n')) {
        out.pop_back();
    }
    return out;
}

class OwnedHandle final {
public:
    OwnedHandle() = default;
    explicit OwnedHandle(HANDLE handle) noexcept : handle_(handle) {}
    OwnedHandle(const OwnedHandle&) = delete;
    OwnedHandle& operator=(const OwnedHandle&) = delete;
    OwnedHandle(OwnedHandle&& other) noexcept
        : handle_(std::exchange(other.handle_, INVALID_HANDLE_VALUE)) {}
    OwnedHandle& operator=(OwnedHandle&& other) noexcept {
        if (this != &other) {
            reset();
            handle_ = std::exchange(other.handle_, INVALID_HANDLE_VALUE);
        }
        return *this;
    }
    ~OwnedHandle() { reset(); }

    [[nodiscard]] HANDLE get() const noexcept { return handle_; }
    [[nodiscard]] bool valid() const noexcept {
        return handle_ != INVALID_HANDLE_VALUE;
    }

    void close_or_throw(const std::string& label) {
        if (!valid()) return;
        const HANDLE handle = std::exchange(handle_, INVALID_HANDLE_VALUE);
        if (::CloseHandle(handle) == 0) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " close failed: " +
                                     windows_error_text(error));
        }
    }

private:
    void reset() noexcept {
        if (valid()) {
            ::CloseHandle(handle_);
            handle_ = INVALID_HANDLE_VALUE;
        }
    }

    HANDLE handle_ = INVALID_HANDLE_VALUE;
};

void inspect_final_path_or_throw(
    const fs::path& final_path,
    const std::string& label,
    AtomicFilePublicationDisposition disposition) {
    std::error_code ec;
    const fs::file_status status = fs::symlink_status(final_path, ec);
    if (ec) {
        if (ec == std::errc::no_such_file_or_directory) return;
        throw std::runtime_error(label +
                                 " final path could not be inspected: " +
                                 ec.message());
    }
    if (!fs::exists(status)) return;
    if (fs::is_symlink(status)) {
        throw std::runtime_error(label +
                                 " final path must not be a symlink");
    }
    if (!fs::is_regular_file(status)) {
        throw std::runtime_error(
            label + " final path must be absent or a regular file");
    }
    if (disposition == AtomicFilePublicationDisposition::CreateNew) {
        throw std::runtime_error(
            label + " immutable create-new final path already exists");
    }
}

void write_windows_handle_all_or_throw(HANDLE handle,
                                       std::span<const unsigned char> payload,
                                       const std::string& label) {
    const unsigned char* cursor = payload.data();
    std::size_t remaining = payload.size();
    while (remaining != 0) {
        const DWORD requested = static_cast<DWORD>(
            std::min<std::size_t>(remaining,
                                  std::numeric_limits<DWORD>::max()));
        DWORD written = 0;
        if (::WriteFile(handle, cursor, requested, &written, nullptr) == 0) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " write failed: " +
                                     windows_error_text(error));
        }
        if (written == 0) {
            throw std::runtime_error(label + " write made no progress");
        }
        cursor += written;
        remaining -= written;
    }
}

void sanitize_windows_temp_handle_noexcept(HANDLE handle) noexcept {
    if (handle == INVALID_HANDLE_VALUE) return;
    LARGE_INTEGER zero{};
    if (::SetFilePointerEx(handle, zero, nullptr, FILE_BEGIN) == 0) return;
    if (::SetEndOfFile(handle) == 0) return;
    (void)::FlushFileBuffers(handle);
}

void publish_windows_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationDisposition disposition,
    AtomicFilePublicationObserver observer,
    void* observer_context,
    AtomicFilePublicationProgress& progress) {
    const fs::path parent = final_path.parent_path();
    const std::string final_basename =
        final_basename_or_throw(final_path, label + " path");
    if (parent.empty()) {
        throw std::runtime_error(label + " parent directory is empty");
    }
    std::error_code parent_ec;
    const fs::file_status parent_status = fs::symlink_status(parent, parent_ec);
    if (parent_ec || !fs::is_directory(parent_status) ||
        fs::is_symlink(parent_status)) {
        throw std::runtime_error(label +
                                 " parent must be an existing non-symlink directory");
    }
    inspect_final_path_or_throw(final_path, label, disposition);

    fs::path temp_path;
    OwnedHandle temp;
    for (std::size_t attempt = 0; attempt < kMaximumTempCreateAttempts;
         ++attempt) {
        temp_path = parent / next_temp_basename(final_basename);
        HANDLE handle = ::CreateFileW(
            temp_path.c_str(),
            GENERIC_WRITE,
            0,
            nullptr,
            CREATE_NEW,
            FILE_ATTRIBUTE_TEMPORARY | FILE_FLAG_WRITE_THROUGH |
                FILE_FLAG_OPEN_REPARSE_POINT,
            nullptr);
        if (handle != INVALID_HANDLE_VALUE) {
            temp = OwnedHandle(handle);
            break;
        }
        const DWORD error = ::GetLastError();
        if (error != ERROR_FILE_EXISTS && error != ERROR_ALREADY_EXISTS) {
            throw std::runtime_error(label + " temp create failed: " +
                                     windows_error_text(error));
        }
    }
    if (!temp.valid()) {
        throw std::runtime_error(label +
                                 " could not reserve a unique temp file");
    }
    progress.mark_temp_reserved();

    try {
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempReserved,
                                     progress);
        write_windows_handle_all_or_throw(temp.get(), payload,
                                          label + " temp file");
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::PayloadWritten,
                                     progress);
        if (::FlushFileBuffers(temp.get()) == 0) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " temp file flush failed: " +
                                     windows_error_text(error));
        }
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempFileSynced,
                                     progress);
        temp.close_or_throw(label + " temp file");
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempDescriptorClosed,
                                     progress);
        inspect_final_path_or_throw(final_path, label, disposition);
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::FinalEntryRevalidated,
                                     progress);
        DWORD move_flags = MOVEFILE_WRITE_THROUGH;
        if (disposition == AtomicFilePublicationDisposition::ReplaceExisting) {
            move_flags |= MOVEFILE_REPLACE_EXISTING;
        }
        if (::MoveFileExW(temp_path.c_str(), final_path.c_str(), move_flags) == 0) {
            const DWORD error = ::GetLastError();
            const std::string operation =
                disposition == AtomicFilePublicationDisposition::CreateNew
                    ? " atomic create-new publication failed: "
                    : " atomic replace failed: ";
            throw std::runtime_error(label + operation +
                                     windows_error_text(error));
        }
        progress.mark_namespace_published();
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::NamespacePublished,
                                     progress);
    } catch (...) {
        if (progress.residue() ==
                SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain &&
            temp.valid()) {
            sanitize_windows_temp_handle_noexcept(temp.get());
        }
        // Windows pathname identity cannot be re-proven after the handle is
        // closed for MoveFileExW. Leaving a writer-owned residue is safer than
        // deleting a path that another principal may have replaced.
        throw;
    }
}

#else

class OwnedFd final {
public:
    OwnedFd() = default;
    explicit OwnedFd(int fd) noexcept : fd_(fd) {}
    OwnedFd(const OwnedFd&) = delete;
    OwnedFd& operator=(const OwnedFd&) = delete;
    OwnedFd(OwnedFd&& other) noexcept
        : fd_(std::exchange(other.fd_, -1)) {}
    OwnedFd& operator=(OwnedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }
    ~OwnedFd() { reset(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void close_or_throw(const std::string& label) {
        if (!valid()) return;
        const int fd = std::exchange(fd_, -1);
        if (::close(fd) != 0) {
            const int error = errno;
            throw std::runtime_error(label + " close failed: " +
                                     system_error_text(error));
        }
    }

private:
    void reset() noexcept {
        if (valid()) {
            const int fd = std::exchange(fd_, -1);
            (void)::close(fd);
        }
    }

    int fd_ = -1;
};


bool same_inode(const struct stat& left, const struct stat& right) noexcept;

struct RootedRelativeDestination final {
    fs::path parent;
    std::string basename;
};

[[nodiscard]] RootedRelativeDestination rooted_relative_destination_or_throw(
    const fs::path& relative_path,
    const std::string& label) {
    if (relative_path.empty() || relative_path.is_absolute() ||
        relative_path.has_root_name() || relative_path.has_root_directory()) {
        throw std::runtime_error(
            label + " must be a nonempty relative path");
    }
    for (const fs::path& component_path : relative_path) {
        const std::string component = component_path.string();
        if (component.empty() || component == "." || component == ".." ||
            component.find('/') != std::string::npos ||
            component.find('\\') != std::string::npos ||
            component.find('\0') != std::string::npos) {
            throw std::runtime_error(
                label + " contains an unsafe path component");
        }
    }
    if (relative_path.lexically_normal() != relative_path) {
        throw std::runtime_error(
            label + " must already be lexically canonical");
    }
    RootedRelativeDestination out;
    out.parent = relative_path.parent_path();
    out.basename = final_basename_or_throw(relative_path, label);
    return out;
}

struct RootTraversalLease final {
    OwnedFd directory;
    SyncPosixDirectoryResolutionCapability resolution_capability =
        SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly;
    SyncPosixMountIdentity mount_identity;
};

[[nodiscard]] RootTraversalLease duplicate_root_directory_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const std::string& label) {
    auto lease = sync_directory_authority_detail::
        SyncDirectoryAuthorityAccess::
            duplicate_shared_open_description_or_throw(root_authority, label);
    return RootTraversalLease{
        OwnedFd(lease.release_descriptor()), lease.resolution_capability(),
        lease.mount_identity()};
}

[[nodiscard]] std::uint64_t posix_device_value(
    const struct stat& status) noexcept {
    return static_cast<std::uint64_t>(
        static_cast<unsigned long long>(status.st_dev));
}

[[nodiscard]] std::uint64_t posix_uid_value(uid_t value) noexcept {
    return static_cast<std::uint64_t>(
        static_cast<unsigned long long>(value));
}

void require_owner_controlled_descendant_directory_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const struct stat& status,
    const fs::path& relative_path,
    const std::string& label) {
    const SyncDirectoryAttestation& root = root_authority.attestation();
    if (posix_device_value(status) != root.device) {
        throw std::runtime_error(
            label +
            " descendant directory crosses the retained root device: " +
            relative_path.generic_string());
    }
    if (posix_uid_value(status.st_uid) != root.effective_user_id) {
        throw std::runtime_error(
            label +
            " descendant directory is not owned by the retained root "
            "effective user: " +
            relative_path.generic_string());
    }
    const auto mode = static_cast<mode_t>(status.st_mode);
    if ((mode & (S_IRUSR | S_IWUSR | S_IXUSR)) !=
        (S_IRUSR | S_IWUSR | S_IXUSR)) {
        throw std::runtime_error(
            label +
            " descendant directory requires owner read/write/search "
            "permission: " +
            relative_path.generic_string());
    }
    if ((mode & (S_IWGRP | S_IWOTH)) != 0) {
        throw std::runtime_error(
            label +
            " refuses a group/other-writable descendant directory: " +
            relative_path.generic_string());
    }
}

[[nodiscard]] OwnedFd open_relative_directory_from_root_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const fs::path& relative_directory,
    const std::string& label) {
    RootTraversalLease lease =
        duplicate_root_directory_or_throw(root_authority, label);
    OwnedFd current = std::move(lease.directory);
    fs::path walked;
    for (const fs::path& component_path : relative_directory) {
        const std::string component = component_path.string();
        if (component.empty() || component == "." || component == ".." ||
            component.find('/') != std::string::npos ||
            component.find('\\') != std::string::npos ||
            component.find('\0') != std::string::npos) {
            throw std::runtime_error(
                label + " contains an unsafe relative directory component");
        }
        walked /= component_path;

        SyncPosixOpenedDirectory opened =
            sync_posix_open_directory_component_or_throw(
                current.get(), component, walked,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                lease.resolution_capability, lease.mount_identity, label);
        OwnedFd next(opened.descriptor);
        require_owner_controlled_descendant_directory_or_throw(
            root_authority, opened.status, walked, label);
        current = std::move(next);
    }
    root_authority.verify_or_throw(
        label + " root authority after relative traversal");
    return current;
}

void verify_relative_directory_identity_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const fs::path& relative_directory,
    int expected_directory_fd,
    const std::string& label) {
    root_authority.verify_or_throw(label + " root authority");
    OwnedFd observed = open_relative_directory_from_root_or_throw(
        root_authority, relative_directory, label + " relative traversal");
    struct stat expected_identity {};
    struct stat observed_identity {};
    if (::fstat(expected_directory_fd, &expected_identity) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " retained relative directory fstat failed: " +
            system_error_text(error));
    }
    if (::fstat(observed.get(), &observed_identity) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " re-opened relative directory fstat failed: " +
            system_error_text(error));
    }
    if (!same_inode(expected_identity, observed_identity)) {
        throw std::runtime_error(
            label +
            " no longer names the retained relative directory identity");
    }
}

bool same_inode(const struct stat& left, const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

void inspect_final_entry_at_or_throw(
    int directory_fd,
    const std::string& final_basename,
    const std::string& label,
    AtomicFilePublicationDisposition disposition) {
    struct stat status {};
    if (::fstatat(directory_fd, final_basename.c_str(), &status,
                  AT_SYMLINK_NOFOLLOW) == 0) {
        if (S_ISLNK(status.st_mode)) {
            throw std::runtime_error(label +
                                     " final path must not be a symlink");
        }
        if (!S_ISREG(status.st_mode)) {
            throw std::runtime_error(
                label + " final path must be absent or a regular file");
        }
        if (disposition == AtomicFilePublicationDisposition::CreateNew) {
            throw std::runtime_error(
                label + " immutable create-new final path already exists");
        }
        return;
    }
    const int error = errno;
    if (error == ENOENT) return;
    throw std::runtime_error(label +
                             " final path could not be inspected: " +
                             system_error_text(error));
}

void write_fd_all_or_throw(int fd,
                           std::span<const unsigned char> payload,
                           const std::string& label) {
    const unsigned char* cursor = payload.data();
    std::size_t remaining = payload.size();
    while (remaining != 0) {
        const ssize_t written = ::write(fd, cursor, remaining);
        if (written < 0) {
            const int error = errno;
            if (error == EINTR) continue;
            throw std::runtime_error(label + " write failed: " +
                                     system_error_text(error));
        }
        if (written == 0) {
            throw std::runtime_error(label + " write made no progress");
        }
        cursor += written;
        remaining -= static_cast<std::size_t>(written);
    }
}

void fsync_fd_or_throw(int fd, const std::string& label) {
    for (;;) {
        if (::fsync(fd) == 0) return;
        const int error = errno;
        if (error == EINTR) continue;
        throw std::runtime_error(label + " fsync failed: " +
                                 system_error_text(error));
    }
}

void set_fd_private_mode_or_throw(int fd, const std::string& label) {
    int result;
    do {
        result = ::fchmod(fd, S_IRUSR | S_IWUSR);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(label + " private-mode fchmod failed: " +
                                 system_error_text(error));
    }
}

[[nodiscard]] bool is_private_single_link_owned_regular_file(
    const struct stat& status) noexcept {
    return S_ISREG(status.st_mode) && status.st_nlink == 1 &&
           (status.st_mode & 07777) == (S_IRUSR | S_IWUSR) &&
           status.st_uid == ::geteuid();
}

bool temp_name_is_private_single_link_inode(
    int directory_fd,
    const std::string& temp_basename,
    const struct stat& expected) noexcept {
    struct stat observed {};
    if (::fstatat(directory_fd, temp_basename.c_str(), &observed,
                  AT_SYMLINK_NOFOLLOW) != 0) {
        return false;
    }
    return is_private_single_link_owned_regular_file(observed) &&
           same_inode(observed, expected);
}

void sanitize_unpublished_temp_fd_noexcept(int fd) noexcept {
    if (fd < 0) return;

    // The descriptor is durable identity evidence for the exact inode this
    // attempt created. Pathname deletion is deliberately absent: POSIX has no
    // compare-and-unlink primitive, so fstatat(name) followed by unlinkat(name)
    // can delete a replacement installed between those two calls.
    int chmod_rc;
    do {
        chmod_rc = ::fchmod(fd, S_IRUSR | S_IWUSR);
    } while (chmod_rc != 0 && errno == EINTR);

    int truncate_rc;
    do {
        truncate_rc = ::ftruncate(fd, 0);
    } while (truncate_rc != 0 && errno == EINTR);
    if (truncate_rc != 0) return;

    int sync_rc;
    do {
        sync_rc = ::fsync(fd);
    } while (sync_rc != 0 && errno == EINTR);
    (void)sync_rc;
    (void)chmod_rc;
}

bool temp_residue_may_remain(
    const AtomicFilePublicationProgress& progress) noexcept {
    return progress.residue() ==
           SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain;
}

void sanitize_unpublished_temp_noexcept(
    const AtomicFilePublicationProgress& progress,
    const OwnedFd& temp) noexcept {
    if (temp_residue_may_remain(progress) && temp.valid()) {
        sanitize_unpublished_temp_fd_noexcept(temp.get());
    }
}

OwnedFd open_parent_directory_or_throw(const fs::path& parent,
                                       const std::string& label) {
    if (!parent.is_absolute()) {
        throw std::runtime_error(
            label + " internal path traversal requires an absolute path");
    }

    SyncPosixOpenedDirectory root =
        sync_posix_open_filesystem_root_directory_or_throw(label);
    OwnedFd current(root.descriptor);

    fs::path walked = "/";
    for (const fs::path& component_path : parent.relative_path()) {
        const std::string component = component_path.string();
        if (component.empty() || component == ".") continue;
        if (component == ".." || component.find('/') != std::string::npos ||
            component.find('\0') != std::string::npos) {
            throw std::runtime_error(label +
                                     " contains an unsafe path component");
        }
        walked /= component_path;

        SyncPosixOpenedDirectory opened =
            sync_posix_open_directory_component_or_throw(
                current.get(), component, walked,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::AllowMountCrossing,
                SyncPosixDirectoryResolutionCapability::DeviceIdentityOnly,
                {}, label);
        OwnedFd next(opened.descriptor);
        current = std::move(next);
    }
    return current;
}

void verify_parent_directory_identity_or_throw(
    const fs::path& parent,
    int expected_directory_fd,
    const std::string& label) {
    OwnedFd observed = open_parent_directory_or_throw(parent, label);
    struct stat expected_identity {};
    struct stat observed_identity {};
    if (::fstat(expected_directory_fd, &expected_identity) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " retained directory fstat failed: " +
                                 system_error_text(error));
    }
    if (::fstat(observed.get(), &observed_identity) != 0) {
        const int error = errno;
        throw std::runtime_error(label + " re-opened directory fstat failed: " +
                                 system_error_text(error));
    }
    if (!same_inode(expected_identity, observed_identity)) {
        throw std::runtime_error(
            label + " no longer names the retained directory identity");
    }
}

std::pair<OwnedFd, std::string> create_unique_temp_at_or_throw(
    int directory_fd,
    const std::string& final_basename,
    const std::string& label) {
    for (std::size_t attempt = 0; attempt < kMaximumTempCreateAttempts;
         ++attempt) {
        std::string temp_basename = next_temp_basename(final_basename);
        int flags = O_WRONLY | O_CREAT | O_EXCL;
#ifdef O_CLOEXEC
        flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
        flags |= O_NOFOLLOW;
#endif
        int fd;
        do {
            fd = ::openat(directory_fd, temp_basename.c_str(), flags, 0600);
        } while (fd < 0 && errno == EINTR);
        if (fd >= 0) {
            return {OwnedFd(fd), std::move(temp_basename)};
        }
        const int error = errno;
        if (error != EEXIST) {
            throw std::runtime_error(label + " temp create failed: " +
                                     system_error_text(error));
        }
    }
    throw std::runtime_error(label +
                             " could not reserve a unique temp file");
}

void publish_temp_name_or_throw(
    int directory_fd,
    const std::string& temp_basename,
    const std::string& final_basename,
    const std::string& label,
    AtomicFilePublicationDisposition disposition) {
    if (disposition == AtomicFilePublicationDisposition::ReplaceExisting) {
        if (::renameat(directory_fd, temp_basename.c_str(), directory_fd,
                       final_basename.c_str()) != 0) {
            const int error = errno;
            throw std::runtime_error(label + " atomic replace failed: " +
                                     system_error_text(error));
        }
        return;
    }
#if defined(__linux__) && defined(RENAME_NOREPLACE)
    int result;
    do {
        result = ::renameat2(directory_fd, temp_basename.c_str(),
                            directory_fd, final_basename.c_str(),
                            RENAME_NOREPLACE);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " atomic create-new publication failed: " +
            system_error_text(error));
    }
#else
    (void)directory_fd;
    (void)temp_basename;
    (void)final_basename;
    throw std::runtime_error(
        label +
        " atomic create-new publication requires a no-replace rename primitive on this platform");
#endif
}

template <typename VerifyDirectory>
void publish_posix_from_retained_directory_or_throw(
    const std::string& final_basename,
    OwnedFd& directory,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationDisposition disposition,
    AtomicFilePublicationObserver observer,
    void* observer_context,
    AtomicFilePublicationProgress& progress,
    VerifyDirectory&& verify_directory) {
    if (!directory.valid()) {
        throw std::logic_error(
            label + " retained parent-directory capability is empty");
    }
    verify_directory(
        directory.get(),
        label + " retained parent directory before temp reservation");
    inspect_final_entry_at_or_throw(directory.get(), final_basename, label,
                                    disposition);

    auto [temp, temp_basename] = create_unique_temp_at_or_throw(
        directory.get(), final_basename, label);
    struct stat temp_identity {};
    progress.mark_temp_reserved();
    try {
        set_fd_private_mode_or_throw(temp.get(), label + " temp file");
        if (::fstat(temp.get(), &temp_identity) != 0) {
            const int error = errno;
            throw std::runtime_error(label + " temp file fstat failed: " +
                                     system_error_text(error));
        }
        if (!is_private_single_link_owned_regular_file(temp_identity)) {
            throw std::runtime_error(
                label + " newly created temp object is not one private, same-owner, singly linked regular file");
        }
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempReserved,
                                     progress);
        write_fd_all_or_throw(temp.get(), payload, label + " temp file");
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::PayloadWritten,
                                     progress);
        fsync_fd_or_throw(temp.get(), label + " temp file");
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempFileSynced,
                                     progress);
        if (!temp_name_is_private_single_link_inode(
                directory.get(), temp_basename, temp_identity)) {
            throw std::runtime_error(
                label +
                " temp pathname no longer names one private singly linked writer-owned inode");
        }
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempNameRevalidated,
                                     progress);
        verify_directory(
            directory.get(), label + " parent directory revalidation");
        observe_publication_frontier(
            observer, observer_context,
            AtomicFilePublicationCutpoint::ParentDirectoryRevalidated,
            progress);
        inspect_final_entry_at_or_throw(directory.get(), final_basename, label,
                                        disposition);
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::FinalEntryRevalidated,
                                     progress);
        publish_temp_name_or_throw(
            directory.get(), temp_basename, final_basename, label,
            disposition);
        progress.mark_namespace_published();
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::NamespacePublished,
                                     progress);
        fsync_fd_or_throw(directory.get(),
                          label + " parent directory after publication");
        progress.mark_directory_synced();
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::DirectorySynced,
                                     progress);
        verify_directory(
            directory.get(), label + " parent directory after publication");
        observe_publication_frontier(
            observer, observer_context,
            AtomicFilePublicationCutpoint::ParentDirectoryPostpublicationRevalidated,
            progress);
        temp.close_or_throw(label + " published file descriptor");
        observe_publication_frontier(observer, observer_context,
                                     AtomicFilePublicationCutpoint::TempDescriptorClosed,
                                     progress);
        directory.close_or_throw(label + " parent directory");
        observe_publication_frontier(
            observer, observer_context,
            AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed,
            progress);
    } catch (...) {
        sanitize_unpublished_temp_noexcept(progress, temp);
        throw;
    }
}

void publish_posix_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationDisposition disposition,
    AtomicFilePublicationObserver observer,
    void* observer_context,
    AtomicFilePublicationProgress& progress) {
    const fs::path parent = final_path.parent_path();
    if (parent.empty()) {
        throw std::runtime_error(label + " parent directory is empty");
    }
    const std::string final_basename =
        final_basename_or_throw(final_path, label + " path");
    OwnedFd directory = open_parent_directory_or_throw(
        parent, label + " parent directory");
    const auto verify_directory = [&parent](int directory_fd,
                                               const std::string& proof_label) {
        verify_parent_directory_identity_or_throw(
            parent, directory_fd, proof_label);
    };
    publish_posix_from_retained_directory_or_throw(
        final_basename, directory, payload, label, disposition,
        observer, observer_context, progress, verify_directory);
}


template <typename VerifyDirectory>
SyncImmutableFileReconciliationOutcome
reconcile_posix_immutable_file_from_retained_directory_or_throw(
    const std::string& final_basename,
    OwnedFd& directory,
    std::span<const unsigned char> expected_payload,
    const std::string& label,
    VerifyDirectory&& verify_directory) {
    if (!directory.valid()) {
        throw std::logic_error(
            label + " retained reconciliation directory capability is empty");
    }

    struct stat named_before {};
    int inspect_result;
    do {
        inspect_result = ::fstatat(
            directory.get(), final_basename.c_str(), &named_before,
            AT_SYMLINK_NOFOLLOW);
    } while (inspect_result != 0 && errno == EINTR);
    if (inspect_result != 0) {
        const int error = errno;
        if (error == ENOENT) {
            verify_directory(
                directory.get(),
                label + " absent reconciliation parent identity");
            return SyncImmutableFileReconciliationOutcome::Absent;
        }
        throw std::runtime_error(
            label + " final entry inspection failed: " +
            system_error_text(error));
    }

    if (S_ISLNK(named_before.st_mode) ||
        !is_private_single_link_owned_regular_file(named_before) ||
        named_before.st_size < 0 ||
        static_cast<std::uint64_t>(named_before.st_size) !=
            static_cast<std::uint64_t>(expected_payload.size())) {
        verify_directory(
            directory.get(),
            label + " conflicting reconciliation parent identity");
        return SyncImmutableFileReconciliationOutcome::ConflictingEntry;
    }

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
    int file_fd;
    do {
        file_fd = ::openat(directory.get(), final_basename.c_str(), flags);
    } while (file_fd < 0 && errno == EINTR);
    if (file_fd < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " final entry open failed: " +
            system_error_text(error));
    }
    OwnedFd file(file_fd);

    struct stat opened_before {};
    if (::fstat(file.get(), &opened_before) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " opened final entry fstat failed: " +
            system_error_text(error));
    }
    if (!is_private_single_link_owned_regular_file(opened_before) ||
        !same_inode(named_before, opened_before)) {
        throw std::runtime_error(
            label + " final entry changed identity while opening");
    }

    FrozenSyncPosixRegularFileSnapshot frozen =
        FrozenSyncPosixRegularFileSnapshot::
            freeze_borrowed_descriptor_or_throw(
                file.get(),
                static_cast<std::uint64_t>(expected_payload.size()),
                SyncPosixDescriptorLinkPolicy::exactly_one,
                label + " immutable final entry");
    if (!bytes_equal(frozen.bytes(), expected_payload)) {
        struct stat named_mismatch {};
        if (::fstatat(directory.get(), final_basename.c_str(),
                      &named_mismatch, AT_SYMLINK_NOFOLLOW) != 0 ||
            !is_private_single_link_owned_regular_file(named_mismatch) ||
            !same_inode(opened_before, named_mismatch)) {
            throw std::runtime_error(
                label + " conflicting final entry changed during reconciliation");
        }
        verify_directory(
            directory.get(),
            label + " conflicting reconciliation parent identity");
        return SyncImmutableFileReconciliationOutcome::ConflictingEntry;
    }

    struct stat named_exact_before_sync {};
    if (::fstatat(directory.get(), final_basename.c_str(),
                  &named_exact_before_sync, AT_SYMLINK_NOFOLLOW) != 0 ||
        !is_private_single_link_owned_regular_file(
            named_exact_before_sync) ||
        !same_inode(opened_before, named_exact_before_sync)) {
        throw std::runtime_error(
            label + " exact final entry changed before durability synchronization");
    }
    fsync_fd_or_throw(file.get(), label + " exact final file");
    fsync_fd_or_throw(directory.get(),
                      label + " exact final parent directory");
    verify_directory(
        directory.get(), label + " exact reconciliation parent identity");

    struct stat opened_after {};
    struct stat named_after {};
    if (::fstat(file.get(), &opened_after) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " exact final entry post-sync fstat failed: " +
            system_error_text(error));
    }
    if (::fstatat(directory.get(), final_basename.c_str(), &named_after,
                  AT_SYMLINK_NOFOLLOW) != 0 ||
        !is_private_single_link_owned_regular_file(opened_after) ||
        !is_private_single_link_owned_regular_file(named_after) ||
        !same_inode(opened_before, opened_after) ||
        !same_inode(opened_after, named_after) ||
        opened_after.st_size < 0 ||
        static_cast<std::uint64_t>(opened_after.st_size) !=
            static_cast<std::uint64_t>(expected_payload.size())) {
        throw std::runtime_error(
            label + " exact final entry changed after durability synchronization");
    }

    file.close_or_throw(label + " reconciled final file");
    directory.close_or_throw(label + " reconciliation parent directory");
    return SyncImmutableFileReconciliationOutcome::
        ExactAndDirectorySynced;
}

SyncImmutableFileReconciliationOutcome
reconcile_posix_immutable_file_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> expected_payload,
    const std::string& label) {
    const fs::path parent = final_path.parent_path();
    if (parent.empty()) {
        throw std::runtime_error(label + " parent directory is empty");
    }
    const std::string final_basename =
        final_basename_or_throw(final_path, label + " path");
    OwnedFd directory = open_parent_directory_or_throw(
        parent, label + " reconciliation parent directory");
    const auto verify_directory = [&parent](int directory_fd,
                                               const std::string& proof_label) {
        verify_parent_directory_identity_or_throw(
            parent, directory_fd, proof_label);
    };
    return reconcile_posix_immutable_file_from_retained_directory_or_throw(
        final_basename, directory, expected_payload, label, verify_directory);
}

#endif

}  // namespace

bool sync_atomic_file_publication_temp_basename_is_exact(
    std::string_view basename) noexcept {
    return publication_temp_basename_is_exact(basename);
}

class SyncPreparedImmutableJsonPublication::Impl final {
public:
    std::filesystem::path final_path;
    std::filesystem::path parent;
    std::string final_basename;
    std::string payload;
    std::string label;
    SyncProcessIncarnation owner_process_incarnation;
    atomic_file_publication_detail::AtomicFilePublicationProgress progress;
#if !defined(_WIN32)
    OwnedFd directory;
#endif
};

SyncPreparedImmutableJsonPublication::
    SyncPreparedImmutableJsonPublication() noexcept = default;

SyncPreparedImmutableJsonPublication::SyncPreparedImmutableJsonPublication(
    std::unique_ptr<Impl> implementation) noexcept
    : implementation_(std::move(implementation)) {}

SyncPreparedImmutableJsonPublication::SyncPreparedImmutableJsonPublication(
    SyncPreparedImmutableJsonPublication&&) noexcept = default;

SyncPreparedImmutableJsonPublication&
SyncPreparedImmutableJsonPublication::operator=(
    SyncPreparedImmutableJsonPublication&&) noexcept = default;

SyncPreparedImmutableJsonPublication::~SyncPreparedImmutableJsonPublication() =
    default;

bool SyncPreparedImmutableJsonPublication::valid() const noexcept {
    return implementation_ != nullptr;
}

void SyncPreparedImmutableJsonPublication::publish_or_throw() {
    atomic_file_publication_detail::
        PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(
            *this, nullptr, nullptr);
}

void atomic_file_publication_detail::
    PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(
        SyncPreparedImmutableJsonPublication& publication,
        AtomicFilePublicationObserver observer,
        void* observer_context) {
    if (publication.implementation_ == nullptr) {
        throw SyncAtomicFilePublicationError(
            SyncAtomicFilePublicationOutcome::NotPublished,
            SyncAtomicFilePublicationResidue::None,
            "prepared immutable JSON publication capability is empty or already consumed");
    }

    // Move first so every success or failure consumes the exact authority once.
    std::unique_ptr<SyncPreparedImmutableJsonPublication::Impl> implementation =
        std::move(publication.implementation_);
    try {
        require_sync_process_incarnation_or_fail_stop(
            implementation->owner_process_incarnation,
            "prepared immutable JSON publication destination authority");
#if defined(_WIN32)
        publish_windows_or_throw(
            implementation->final_path, byte_span(implementation->payload),
            implementation->label,
            AtomicFilePublicationDisposition::CreateNew, observer,
            observer_context, implementation->progress);
#else
        const auto verify_directory = [&implementation](
                                          int directory_fd,
                                          const std::string& proof_label) {
            verify_parent_directory_identity_or_throw(
                implementation->parent, directory_fd, proof_label);
        };
        publish_posix_from_retained_directory_or_throw(
            implementation->final_basename, implementation->directory,
            byte_span(implementation->payload), implementation->label,
            AtomicFilePublicationDisposition::CreateNew, observer,
            observer_context, implementation->progress, verify_directory);
#endif
    } catch (...) {
        rethrow_publication_failure(implementation->label,
                                    implementation->progress);
    }
}

SyncPreparedImmutableJsonPublication
prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
    const std::filesystem::path& final_path,
    std::string payload,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "atomic file publication label must not be empty");
    }

    AtomicFilePublicationProgress progress;
    try {
        if (final_path.empty()) {
            throw std::runtime_error(label + " path is empty");
        }
        const std::filesystem::path normalized_path =
            absolute_lexically_normal_path_or_throw(final_path, label + " path");
        const std::filesystem::path parent = normalized_path.parent_path();
        if (parent.empty()) {
            throw std::runtime_error(label + " parent directory is empty");
        }
        const std::string final_basename =
            final_basename_or_throw(normalized_path, label + " path");

        auto implementation = std::make_unique<
            SyncPreparedImmutableJsonPublication::Impl>();
        implementation->final_path = normalized_path;
        implementation->parent = parent;
        implementation->final_basename = final_basename;
        implementation->payload = std::move(payload);
        implementation->label = label;
        implementation->owner_process_incarnation =
            current_sync_process_incarnation_noexcept();
#if defined(_WIN32)
        std::error_code parent_error;
        const std::filesystem::file_status parent_status =
            std::filesystem::symlink_status(parent, parent_error);
        if (parent_error || !std::filesystem::is_directory(parent_status) ||
            std::filesystem::is_symlink(parent_status)) {
            throw std::runtime_error(
                label + " parent must be an existing non-symlink directory");
        }
        inspect_final_path_or_throw(
            normalized_path, label,
            AtomicFilePublicationDisposition::CreateNew);
#else
        implementation->directory = open_parent_directory_or_throw(
            parent, label + " prepared parent directory");
        inspect_final_entry_at_or_throw(
            implementation->directory.get(), final_basename, label,
            AtomicFilePublicationDisposition::CreateNew);
        verify_parent_directory_identity_or_throw(
            parent, implementation->directory.get(),
            label + " prepared parent directory identity");
#endif
        return SyncPreparedImmutableJsonPublication(std::move(implementation));
    } catch (...) {
        rethrow_publication_failure(label, progress);
    }
}

namespace atomic_file_publication_detail {

const char* atomic_file_publication_cutpoint_name(
    AtomicFilePublicationCutpoint cutpoint) noexcept {
    switch (cutpoint) {
        case AtomicFilePublicationCutpoint::TempReserved:
            return "temp_reserved";
        case AtomicFilePublicationCutpoint::PayloadWritten:
            return "payload_written";
        case AtomicFilePublicationCutpoint::TempFileSynced:
            return "temp_file_synced";
        case AtomicFilePublicationCutpoint::TempNameRevalidated:
            return "temp_name_revalidated";
        case AtomicFilePublicationCutpoint::ParentDirectoryRevalidated:
            return "parent_directory_revalidated";
        case AtomicFilePublicationCutpoint::TempDescriptorClosed:
            return "temp_descriptor_closed";
        case AtomicFilePublicationCutpoint::FinalEntryRevalidated:
            return "final_entry_revalidated";
        case AtomicFilePublicationCutpoint::NamespacePublished:
            return "namespace_published";
        case AtomicFilePublicationCutpoint::DirectorySynced:
            return "directory_synced";
        case AtomicFilePublicationCutpoint::ParentDirectoryPostpublicationRevalidated:
            return "parent_directory_postpublication_revalidated";
        case AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed:
            return "parent_directory_descriptor_closed";
    }
    return "unknown";
}

void write_sync_file_atomically_with_disposition_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationDisposition disposition,
    AtomicFilePublicationObserver observer,
    void* observer_context) {
    if (label.empty()) {
        throw std::invalid_argument(
            "atomic file publication label must not be empty");
    }

    AtomicFilePublicationProgress progress;
    try {
        if (final_path.empty()) {
            throw std::runtime_error(label + " path is empty");
        }
        const fs::path normalized_path = absolute_lexically_normal_path_or_throw(
            final_path, label + " path");
#if defined(_WIN32)
        publish_windows_or_throw(normalized_path, payload, label, disposition,
                                 observer, observer_context, progress);
#else
        publish_posix_or_throw(normalized_path, payload, label, disposition,
                               observer, observer_context, progress);
#endif
    } catch (...) {
        rethrow_publication_failure(label, progress);
    }
}

void preflight_create_new_destination_or_throw(
    const fs::path& final_path,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "atomic file publication label must not be empty");
    }

    AtomicFilePublicationProgress progress;
    try {
        if (final_path.empty()) {
            throw std::runtime_error(label + " path is empty");
        }
        const fs::path normalized_path = absolute_lexically_normal_path_or_throw(
            final_path, label + " path");
        const fs::path parent = normalized_path.parent_path();
        if (parent.empty()) {
            throw std::runtime_error(label + " parent directory is empty");
        }
        const std::string final_basename =
            final_basename_or_throw(normalized_path, label + " path");
#if defined(_WIN32)
        std::error_code parent_ec;
        const fs::file_status parent_status =
            fs::symlink_status(parent, parent_ec);
        if (parent_ec || !fs::is_directory(parent_status) ||
            fs::is_symlink(parent_status)) {
            throw std::runtime_error(
                label + " parent must be an existing non-symlink directory");
        }
        inspect_final_path_or_throw(
            normalized_path, label, AtomicFilePublicationDisposition::CreateNew);
#else
        OwnedFd directory = open_parent_directory_or_throw(
            parent, label + " parent directory");
        inspect_final_entry_at_or_throw(
            directory.get(), final_basename, label,
            AtomicFilePublicationDisposition::CreateNew);
        verify_parent_directory_identity_or_throw(
            parent, directory.get(), label + " parent directory preflight");
#endif
    } catch (...) {
        rethrow_publication_failure(label, progress);
    }
}

void write_sync_json_file_atomically_with_observer_or_throw(
    const fs::path& final_path,
    const std::string& payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context) {
    write_sync_file_atomically_with_disposition_or_throw(
        final_path, byte_span(payload), label,
        AtomicFilePublicationDisposition::ReplaceExisting, observer,
        observer_context);
}

void write_sync_json_file_atomically_create_new_with_observer_or_throw(
    const fs::path& final_path,
    const std::string& payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context) {
    write_sync_file_atomically_with_disposition_or_throw(
        final_path, byte_span(payload), label,
        AtomicFilePublicationDisposition::CreateNew, observer,
        observer_context);
}

void write_sync_file_atomically_with_observer_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context) {
    write_sync_file_atomically_with_disposition_or_throw(
        final_path, payload, label,
        AtomicFilePublicationDisposition::ReplaceExisting, observer,
        observer_context);
}

void write_sync_file_atomically_create_new_with_observer_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label,
    AtomicFilePublicationObserver observer,
    void* observer_context) {
    write_sync_file_atomically_with_disposition_or_throw(
        final_path, payload, label,
        AtomicFilePublicationDisposition::CreateNew, observer,
        observer_context);
}

}  // namespace atomic_file_publication_detail

void write_sync_json_file_atomically_no_symlink_or_throw(
    const fs::path& final_path,
    const std::string& payload,
    const std::string& label) {
    atomic_file_publication_detail::
        write_sync_json_file_atomically_with_observer_or_throw(
            final_path, payload, label, nullptr, nullptr);
}

void write_sync_file_atomically_no_symlink_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label) {
    atomic_file_publication_detail::
        write_sync_file_atomically_with_observer_or_throw(
            final_path, payload, label, nullptr, nullptr);
}

void write_sync_file_atomically_create_new_no_symlink_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> payload,
    const std::string& label) {
    atomic_file_publication_detail::
        write_sync_file_atomically_create_new_with_observer_or_throw(
            final_path, payload, label, nullptr, nullptr);
}

#if !defined(_WIN32)
void write_sync_file_atomically_create_new_under_directory_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const fs::path& canonical_relative_path,
    std::span<const unsigned char> payload,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "rooted atomic file publication label must not be empty");
    }
    AtomicFilePublicationProgress progress;
    try {
        const RootedRelativeDestination destination =
            rooted_relative_destination_or_throw(
                canonical_relative_path, label + " relative path");
        OwnedFd directory = open_relative_directory_from_root_or_throw(
            root_authority, destination.parent,
            label + " rooted parent directory");
        const auto verify_directory =
            [&root_authority, &destination](
                int directory_fd, const std::string& proof_label) {
                verify_relative_directory_identity_or_throw(
                    root_authority, destination.parent, directory_fd,
                    proof_label);
            };
        publish_posix_from_retained_directory_or_throw(
            destination.basename, directory, payload, label,
            AtomicFilePublicationDisposition::CreateNew, nullptr, nullptr,
            progress, verify_directory);
    } catch (...) {
        rethrow_publication_failure(label, progress);
    }
}
#endif

const char* sync_immutable_file_reconciliation_outcome_name(
    SyncImmutableFileReconciliationOutcome outcome) noexcept {
    switch (outcome) {
        case SyncImmutableFileReconciliationOutcome::Absent:
            return "absent";
        case SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced:
            return "exact_and_directory_synced";
        case SyncImmutableFileReconciliationOutcome::ConflictingEntry:
            return "conflicting_entry";
    }
    return "unknown";
}

SyncImmutableFileReconciliationOutcome
reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
    const fs::path& final_path,
    std::span<const unsigned char> expected_payload,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "immutable file reconciliation label must not be empty");
    }
    if (final_path.empty()) {
        throw std::invalid_argument(label + " path is empty");
    }
    const fs::path normalized_path = absolute_lexically_normal_path_or_throw(
        final_path, label + " path");
#if defined(_WIN32)
    // Windows uses the same no-reparse terminal open and exact-byte proof, but
    // its parent-directory durability primitive differs from POSIX. Keep this
    // branch explicit rather than silently following a reparse point.
    const fs::path parent = normalized_path.parent_path();
    if (parent.empty()) {
        throw std::runtime_error(label + " parent directory is empty");
    }
    std::error_code parent_error;
    const fs::file_status parent_status = fs::symlink_status(parent, parent_error);
    if (parent_error || !fs::is_directory(parent_status) ||
        fs::is_symlink(parent_status)) {
        throw std::runtime_error(
            label + " parent must be an existing non-symlink directory");
    }
    HANDLE raw = ::CreateFileW(
        normalized_path.c_str(), GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ, nullptr, OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT |
            FILE_FLAG_WRITE_THROUGH,
        nullptr);
    if (raw == INVALID_HANDLE_VALUE) {
        const DWORD error = ::GetLastError();
        if (error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND) {
            return SyncImmutableFileReconciliationOutcome::Absent;
        }
        throw std::runtime_error(label + " final entry open failed: " +
                                 windows_error_text(error));
    }
    OwnedHandle file(raw);
    BY_HANDLE_FILE_INFORMATION information {};
    if (::GetFileInformationByHandle(file.get(), &information) == 0) {
        const DWORD error = ::GetLastError();
        throw std::runtime_error(label + " final entry inspection failed: " +
                                 windows_error_text(error));
    }
    if ((information.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0 ||
        (information.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0) {
        return SyncImmutableFileReconciliationOutcome::ConflictingEntry;
    }
    const std::uint64_t size =
        (static_cast<std::uint64_t>(information.nFileSizeHigh) << 32U) |
        information.nFileSizeLow;
    if (size != expected_payload.size()) {
        return SyncImmutableFileReconciliationOutcome::ConflictingEntry;
    }
    LARGE_INTEGER zero {};
    if (::SetFilePointerEx(file.get(), zero, nullptr, FILE_BEGIN) == 0) {
        const DWORD error = ::GetLastError();
        throw std::runtime_error(label + " final entry seek failed: " +
                                 windows_error_text(error));
    }
    std::string observed(expected_payload.size(), '\0');
    std::size_t offset = 0U;
    while (offset < observed.size()) {
        const DWORD requested = static_cast<DWORD>(std::min<std::size_t>(
            observed.size() - offset, std::numeric_limits<DWORD>::max()));
        DWORD received = 0U;
        if (::ReadFile(file.get(), observed.data() + offset, requested,
                       &received, nullptr) == 0) {
            const DWORD error = ::GetLastError();
            throw std::runtime_error(label + " final entry read failed: " +
                                     windows_error_text(error));
        }
        if (received == 0U) {
            throw std::runtime_error(
                label + " final entry changed while being read");
        }
        offset += received;
    }
    if (!bytes_equal(observed, expected_payload)) {
        return SyncImmutableFileReconciliationOutcome::ConflictingEntry;
    }
    if (::FlushFileBuffers(file.get()) == 0) {
        const DWORD error = ::GetLastError();
        throw std::runtime_error(label + " final entry flush failed: " +
                                 windows_error_text(error));
    }
    file.close_or_throw(label + " reconciled final file");
    throw std::runtime_error(
        label +
        " exact file is synchronized but parent-directory durability is not implemented on Windows");
#else
    return reconcile_posix_immutable_file_or_throw(
        normalized_path, expected_payload, label);
#endif
}

#if !defined(_WIN32)
SyncImmutableFileReconciliationOutcome
reconcile_sync_immutable_file_create_new_under_directory_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const fs::path& canonical_relative_path,
    std::span<const unsigned char> expected_payload,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "rooted immutable file reconciliation label must not be empty");
    }
    const RootedRelativeDestination destination =
        rooted_relative_destination_or_throw(
            canonical_relative_path, label + " relative path");
    OwnedFd directory = open_relative_directory_from_root_or_throw(
        root_authority, destination.parent,
        label + " rooted reconciliation parent directory");
    const auto verify_directory =
        [&root_authority, &destination](
            int directory_fd, const std::string& proof_label) {
            verify_relative_directory_identity_or_throw(
                root_authority, destination.parent, directory_fd,
                proof_label);
        };
    return reconcile_posix_immutable_file_from_retained_directory_or_throw(
        destination.basename, directory, expected_payload, label,
        verify_directory);
}
#endif

void preflight_sync_file_create_new_no_symlink_or_throw(
    const fs::path& final_path,
    const std::string& label) {
    atomic_file_publication_detail::preflight_create_new_destination_or_throw(
        final_path, label);
}

void write_sync_json_file_atomically_create_new_no_symlink_or_throw(
    const fs::path& final_path,
    const std::string& payload,
    const std::string& label) {
    atomic_file_publication_detail::
        write_sync_json_file_atomically_create_new_with_observer_or_throw(
            final_path, payload, label, nullptr, nullptr);
}

void write_sync_cli_report_json_or_throw(const std::string& report_path,
                                         const std::string& payload,
                                         const std::string& label) {
    write_sync_json_file_atomically_no_symlink_or_throw(
        fs::path(report_path), payload, label);
}

SyncPreparedImmutableJsonPublication
prepare_sync_cli_immutable_json_create_new_or_throw(
    const std::string& output_path,
    std::string payload,
    const std::string& label) {
    return prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
        fs::path(output_path), std::move(payload), label);
}

void preflight_sync_cli_file_create_new_no_symlink_or_throw(
    const std::string& output_path,
    const std::string& label) {
    preflight_sync_file_create_new_no_symlink_or_throw(
        fs::path(output_path), label);
}

void write_sync_cli_immutable_json_create_new_or_throw(
    const std::string& output_path,
    const std::string& payload,
    const std::string& label) {
    write_sync_json_file_atomically_create_new_no_symlink_or_throw(
        fs::path(output_path), payload, label);
}

}  // namespace anonsync
