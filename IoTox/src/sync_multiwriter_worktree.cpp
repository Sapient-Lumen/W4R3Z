#include "iotox/sync_multiwriter_worktree.hpp"

#include "iotox/sync_digest.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <linux/fs.h>
#include <map>
#include <set>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

struct PreserveUnselectedResult {
    std::uint64_t entries{0U};
    std::uint64_t directories{0U};
    std::uint64_t files{0U};
    std::uint64_t bytes{0U};
};

class FileDescriptor {
  public:
    explicit FileDescriptor(int value = -1) noexcept : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    [[nodiscard]] int get() const noexcept { return value_; }
    [[nodiscard]] int release() noexcept { return std::exchange(value_, -1); }

  private:
    int value_{-1};
};

class ProjectionCleanup {
  public:
    explicit ProjectionCleanup(std::filesystem::path path)
        : path_(std::move(path)) {}
    ~ProjectionCleanup() {
        if (!active_) return;
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }
    ProjectionCleanup(const ProjectionCleanup &) = delete;
    ProjectionCleanup &operator=(const ProjectionCleanup &) = delete;
    void release() noexcept { active_ = false; }

  private:
    std::filesystem::path path_;
    bool active_{true};
};

[[nodiscard]] Status system_status(std::string_view operation,
                                   const std::filesystem::path &path,
                                   int error = errno) {
    return Status{ErrorCode::io_error, std::string(operation) + " '" +
                                           path.string() +
                                           "': " + std::strerror(error)};
}

[[nodiscard]] bool same_identity(const struct stat &left,
                                 const struct stat &right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino &&
           left.st_mode == right.st_mode && left.st_nlink == right.st_nlink &&
           left.st_uid == right.st_uid && left.st_size == right.st_size &&
           left.st_mtim.tv_sec == right.st_mtim.tv_sec &&
           left.st_mtim.tv_nsec == right.st_mtim.tv_nsec &&
           left.st_ctim.tv_sec == right.st_ctim.tv_sec &&
           left.st_ctim.tv_nsec == right.st_ctim.tv_nsec;
}

[[nodiscard]] TreeV2SourceDigestCache::FileIdentity
source_file_identity(const struct stat &metadata) noexcept {
    return TreeV2SourceDigestCache::FileIdentity{
        static_cast<std::uint64_t>(metadata.st_dev),
        static_cast<std::uint64_t>(metadata.st_ino),
        static_cast<std::uint64_t>(metadata.st_mode),
        static_cast<std::uint64_t>(metadata.st_nlink),
        static_cast<std::uint64_t>(metadata.st_uid),
        static_cast<std::uint64_t>(metadata.st_size),
        static_cast<std::int64_t>(metadata.st_mtim.tv_sec),
        static_cast<std::int64_t>(metadata.st_mtim.tv_nsec),
        static_cast<std::int64_t>(metadata.st_ctim.tv_sec),
        static_cast<std::int64_t>(metadata.st_ctim.tv_nsec)};
}

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] std::string lower_hex(std::span<const std::uint8_t> bytes) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string result;
    result.reserve(bytes.size() * 2U);
    for (const std::uint8_t byte : bytes) {
        result.push_back(digits[byte >> 4U]);
        result.push_back(digits[byte & 0x0fU]);
    }
    return result;
}

[[nodiscard]] int hex_nibble(char value) noexcept {
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return 10 + value - 'a';
    return -1;
}

[[nodiscard]] Result<Digest> parse_digest(std::string_view value) {
    if (value.size() != Digest{}.size() * 2U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object name has an invalid length"};
    }
    Digest result{};
    for (std::size_t index = 0U; index < result.size(); ++index) {
        const int high = hex_nibble(value[index * 2U]);
        const int low = hex_nibble(value[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 object name is not lowercase hex"};
        }
        result[index] = static_cast<std::uint8_t>((high << 4U) | low);
    }
    return result;
}

[[nodiscard]] bool entry_less(const TreeV2Entry &left,
                              const TreeV2Entry &right) {
    if (left.path != right.path) return left.path < right.path;
    if (left.origin.writer != right.origin.writer)
        return left.origin.writer < right.origin.writer;
    if (left.origin.generation != right.origin.generation)
        return left.origin.generation < right.origin.generation;
    if (left.kind != right.kind) return left.kind < right.kind;
    const auto mode = [](const TreeV2Entry &entry) {
        return entry.kind == TreeV2EntryKind::file
                   ? (entry.owner_mode != 0U
                          ? entry.owner_mode
                          : static_cast<std::uint8_t>(entry.executable ? 7U
                                                                       : 6U))
                   : 0U;
    };
    if (mode(left) != mode(right)) return mode(left) < mode(right);
    if (left.content != right.content) return left.content < right.content;
    return left.content_bytes < right.content_bytes;
}

[[nodiscard]] bool same_payload(const TreeV2Entry &left,
                                const TreeV2Entry &right) noexcept {
    const auto mode = [](const TreeV2Entry &entry) {
        return entry.kind == TreeV2EntryKind::file
                   ? (entry.owner_mode != 0U
                          ? entry.owner_mode
                          : static_cast<std::uint8_t>(entry.executable ? 7U
                                                                       : 6U))
                   : 0U;
    };
    return left.kind == right.kind && left.content == right.content &&
           left.content_bytes == right.content_bytes &&
           mode(left) == mode(right);
}

[[nodiscard]] bool path_prefix(std::string_view prefix,
                               std::string_view path) noexcept {
    return path == prefix ||
           (path.size() > prefix.size() && path.starts_with(prefix) &&
            path[prefix.size()] == '/');
}

[[nodiscard]] std::vector<std::string>
minimal_include_roots(std::span<const std::string> includes) {
    std::vector<std::string> roots;
    for (const std::string &included : includes) {
        if (roots.empty() || !path_prefix(roots.back(), included))
            roots.push_back(included);
    }
    return roots;
}

[[nodiscard]] bool complete_tree_v2_projection(
    const TreeV2ProjectionPolicy &projection) noexcept {
    return projection.includes.empty() && projection.excludes.empty();
}

[[nodiscard]] Status validate_owned_directory(const std::filesystem::path &path,
                                              std::string_view label) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0)
        return system_status("inspect " + std::string(label), path);
    if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " is not an owner-controlled directory"};
    }
    return Status::success();
}

[[nodiscard]] Status
ensure_private_directory(const std::filesystem::path &path) {
    if (::mkdir(path.c_str(), static_cast<mode_t>(0700)) != 0 &&
        errno != EEXIST) {
        return system_status("create tree-v2 directory", path);
    }
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 || !S_ISDIR(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 store directory is not private owner state"};
    }
    return Status::success();
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 directory", path);
    if (::fsync(descriptor.get()) != 0)
        return system_status("fsync tree-v2 directory", path);
    return Status::success();
}

[[nodiscard]] Status sync_filesystem(const std::filesystem::path &path) {
    // Projection staging is still invisible here.  All output descriptors are
    // closed and content-verified before this one Linux filesystem barrier;
    // the later directory exchange cannot expose a partly durable batch.
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 filesystem sync root", path);
    if (::syncfs(descriptor.get()) != 0)
        return Status{errno == ENOSYS ? ErrorCode::unsupported
                                     : ErrorCode::io_error,
                      "sync tree-v2 filesystem at '" + path.string() +
                          "': " + std::strerror(errno)};
    return Status::success();
}

[[nodiscard]] Status remove_owned_tree(const std::filesystem::path &path) {
    const Status controlled =
        validate_owned_directory(path, "tree-v2 old projection");
    if (!controlled.ok()) return controlled;
    std::error_code error;
    const std::uintmax_t removed = std::filesystem::remove_all(path, error);
    if (error || removed == 0U) {
        return Status{ErrorCode::io_error,
                      "unable to remove old tree-v2 projection: " +
                          error.message()};
    }
    return sync_directory(path.parent_path());
}

[[nodiscard]] bool projection_transition_marker_matches(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const TreeV2ProjectionPolicy &previous_projection,
    const std::filesystem::path &destination,
    const security::Sodium &sodium);

[[nodiscard]] Status compare_unselected_trees(
    const NamespacePolicy &policy, const std::filesystem::path &left,
    const std::filesystem::path &right);

[[nodiscard]] Status validate_old_projection(
    const NamespacePolicy &policy,
    const TreeV2Manifest &expected_worktree,
    const TreeV2Manifest *expected_marker,
    const std::filesystem::path &path,
    const std::filesystem::path &preserved_peer,
    const PrincipalId &local_writer,
    const security::Sodium &sodium,
    const TreeV2ProjectionPolicy *previous_projection) {
    auto old_scan = scan_tree_v2_worktree(
        policy, path, expected_worktree, local_writer, 1U,
        previous_projection);
    if (!old_scan) {
        return Status{old_scan.status().code(),
                      "inspect tree-v2 exchanged old projection: " +
                          old_scan.status().message()};
    }
    const bool marker_matches =
        expected_marker == nullptr ||
        tree_v2_projection_marker_matches(policy, *expected_marker, path,
                                          sodium) ||
        (previous_projection != nullptr &&
         projection_transition_marker_matches(
             policy, *expected_marker, *previous_projection, path, sodium));
    if (old_scan.value().changed || !marker_matches) {
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 exchanged old projection changed; preserved for "
            "operator recovery"};
    }
    const Status unselected =
        compare_unselected_trees(policy, path, preserved_peer);
    if (!unselected.ok()) return unselected;
    return Status::success();
}

[[nodiscard]] Status validate_exact_file(const std::filesystem::path &path,
                                         const Digest &expected,
                                         std::uint64_t expected_bytes,
                                         mode_t expected_mode) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0)
        return system_status("inspect tree-v2 object", path);
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) != expected_mode ||
        metadata.st_size < 0 ||
        static_cast<std::uint64_t>(metadata.st_size) != expected_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object is not one exact private regular file"};
    }
    auto digest = hash_sync_file_sha256(path);
    if (!digest) return digest.status();
    if (digest.value() != expected) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 object content does not match its identity"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_object_file(const std::filesystem::path &path,
                                          const Digest &expected,
                                          std::uint64_t expected_bytes) {
    return validate_exact_file(path, expected, expected_bytes,
                               static_cast<mode_t>(0600));
}

[[nodiscard]] Status write_all(int descriptor,
                               std::span<const std::uint8_t> bytes,
                               const std::filesystem::path &path) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count =
            ::write(descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return system_status("write tree-v2 file", path);
    }
    return Status::success();
}

enum class CopyDurability { immediate, filesystem_batch };

[[nodiscard]] Status copy_file_exact(const std::filesystem::path &source,
                                     const std::filesystem::path &destination,
                                     const Digest &expected,
                                     std::uint64_t expected_bytes,
                                     mode_t destination_mode, bool no_replace,
                                     CopyDurability durability =
                                         CopyDurability::immediate) {
    FileDescriptor input(
        ::open(source.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (input.get() < 0) return system_status("open tree-v2 source", source);
    struct stat before {};
    if (::fstat(input.get(), &before) != 0)
        return system_status("inspect tree-v2 source", source);
    if (!S_ISREG(before.st_mode) || before.st_uid != ::geteuid() ||
        before.st_nlink != 1 ||
        (before.st_mode & static_cast<mode_t>(0022)) != 0U ||
        before.st_size < 0 ||
        static_cast<std::uint64_t>(before.st_size) != expected_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 source changed shape before copy"};
    }
    const int create_flags = O_WRONLY | O_CREAT | O_CLOEXEC | O_NOFOLLOW |
                             (no_replace ? O_EXCL : O_TRUNC);
    FileDescriptor output(
        ::open(destination.c_str(), create_flags, destination_mode));
    if (output.get() < 0)
        return system_status("create tree-v2 destination", destination);
    if (::fchmod(output.get(), destination_mode) != 0)
        return system_status("secure tree-v2 destination", destination);
    std::array<std::uint8_t, 256U * 1024U> buffer{};
    std::uint64_t copied = 0U;
    while (true) {
        const ssize_t count = ::read(input.get(), buffer.data(), buffer.size());
        if (count < 0) {
            if (errno == EINTR) continue;
            return system_status("read tree-v2 source", source);
        }
        if (count == 0) break;
        const std::size_t bytes = static_cast<std::size_t>(count);
        if (copied > std::numeric_limits<std::uint64_t>::max() - bytes)
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 copy byte count overflows"};
        copied += bytes;
        const Status written = write_all(
            output.get(), std::span<const std::uint8_t>(buffer.data(), bytes),
            destination);
        if (!written.ok()) return written;
    }
    struct stat after {};
    if (::fstat(input.get(), &after) != 0)
        return system_status("reinspect tree-v2 source", source);
    if (!same_identity(before, after) || copied != expected_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 source changed during copy"};
    }
    if (durability == CopyDurability::immediate &&
        ::fsync(output.get()) != 0)
        return system_status("fsync tree-v2 destination", destination);
    const int output_raw = output.release();
    if (::close(output_raw) != 0)
        return system_status("close tree-v2 destination", destination);
    return validate_exact_file(destination, expected, expected_bytes,
                               destination_mode);
}

[[nodiscard]] Status
ensure_projection_parent(const std::filesystem::path &destination,
                         std::string_view relative) {
    std::filesystem::path current = destination;
    const std::filesystem::path path{std::string(relative)};
    for (const auto &component : path.parent_path()) {
        const std::string name = component.string();
        if (name.empty() || name == "." || name == "..") {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 projection parent is invalid"};
        }
        current /= name;
        const Status prepared = ensure_private_directory(current);
        if (!prepared.ok()) return prepared;
    }
    return Status::success();
}

[[nodiscard]] Status compare_unselected_tree_direction(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::filesystem::path &peer, bool compare_contents) {
    try {
        for (std::filesystem::recursive_directory_iterator iterator(source),
             end;
             iterator != end; ++iterator) {
            const std::filesystem::path relative_path =
                iterator->path().lexically_relative(source);
            const std::string relative = relative_path.generic_string();
            struct stat before {};
            if (::lstat(iterator->path().c_str(), &before) != 0)
                return system_status("inspect preserved tree-v2 entry",
                                     iterator->path());
            if (relative_path.begin() != relative_path.end() &&
                relative_path.begin()->string() == kTreeV2ConflictRoot) {
                if (relative_path ==
                    std::filesystem::path(std::string(kTreeV2ConflictRoot)))
                    iterator.disable_recursion_pending();
                continue;
            }
            const bool directory = S_ISDIR(before.st_mode);
            if (tree_v2_path_selected(policy, relative, directory)) continue;
            const auto changed = []() {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 preserved unselected projection changed; "
                    "preserved for operator recovery"};
            };
            if (!valid_tree_v2_path(relative) ||
                before.st_uid != ::geteuid() ||
                (before.st_mode & static_cast<mode_t>(0022)) != 0U) {
                return changed();
            }
            const std::filesystem::path peer_path = peer / relative_path;
            struct stat peer_before {};
            if (::lstat(peer_path.c_str(), &peer_before) != 0 ||
                peer_before.st_uid != ::geteuid() ||
                (peer_before.st_mode & static_cast<mode_t>(0022)) != 0U ||
                (before.st_mode & static_cast<mode_t>(0700)) !=
                    (peer_before.st_mode & static_cast<mode_t>(0700))) {
                return changed();
            }
            if (directory) {
                if (!S_ISDIR(peer_before.st_mode)) return changed();
                continue;
            }
            if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
                before.st_size < 0 ||
                (before.st_mode & static_cast<mode_t>(S_IRUSR)) == 0U ||
                !S_ISREG(peer_before.st_mode) || peer_before.st_nlink != 1 ||
                peer_before.st_size != before.st_size ||
                (peer_before.st_mode & static_cast<mode_t>(S_IRUSR)) == 0U) {
                return changed();
            }
            if (!compare_contents) continue;
            auto digest = hash_sync_file_sha256(iterator->path());
            auto peer_digest = hash_sync_file_sha256(peer_path);
            if (!digest || !peer_digest || digest.value() != peer_digest.value())
                return changed();
            struct stat after {};
            struct stat peer_after {};
            if (::lstat(iterator->path().c_str(), &after) != 0 ||
                ::lstat(peer_path.c_str(), &peer_after) != 0 ||
                !same_identity(before, after) ||
                !same_identity(peer_before, peer_after)) {
                return changed();
            }
        }
    } catch (const std::filesystem::filesystem_error &) {
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 preserved unselected projection changed; preserved for "
            "operator recovery"};
    }
    return Status::success();
}

[[nodiscard]] Status compare_unselected_trees(
    const NamespacePolicy &policy, const std::filesystem::path &left,
    const std::filesystem::path &right) {
    if (complete_tree_v2_projection(policy.projection))
        return Status::success();
    Status compared =
        compare_unselected_tree_direction(policy, left, right, true);
    if (!compared.ok()) return compared;
    return compare_unselected_tree_direction(policy, right, left, false);
}

[[nodiscard]] Result<PreserveUnselectedResult> preserve_unselected_tree(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::filesystem::path &destination) {
    if (complete_tree_v2_projection(policy.projection)) {
        return PreserveUnselectedResult{};
    }
    PreserveUnselectedResult result;
    std::vector<std::pair<std::filesystem::path, mode_t>> directory_modes;
    try {
        for (std::filesystem::recursive_directory_iterator iterator(source),
             end;
             iterator != end; ++iterator) {
            const std::filesystem::path relative_path =
                iterator->path().lexically_relative(source);
            const std::string relative = relative_path.generic_string();
            struct stat metadata {};
            if (::lstat(iterator->path().c_str(), &metadata) != 0)
                return system_status("inspect unselected tree-v2 entry",
                                     iterator->path());
            if (relative_path.begin() != relative_path.end() &&
                relative_path.begin()->string() == kTreeV2ConflictRoot) {
                if (relative_path ==
                    std::filesystem::path(std::string(kTreeV2ConflictRoot)))
                    iterator.disable_recursion_pending();
                continue;
            }
            const bool directory = S_ISDIR(metadata.st_mode);
            if (tree_v2_path_selected(policy, relative, directory)) continue;
            if (!valid_tree_v2_path(relative) ||
                metadata.st_uid != ::geteuid() ||
                (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
                return Status{ErrorCode::protocol_error,
                              "unselected tree-v2 entry is not owner-controlled"};
            }
            const Status parent =
                ensure_projection_parent(destination, relative);
            if (!parent.ok()) return parent;
            const std::filesystem::path output = destination / relative;
            ++result.entries;
            if (directory) {
                const Status created = ensure_private_directory(output);
                if (!created.ok()) return created;
                directory_modes.emplace_back(
                    output, metadata.st_mode & static_cast<mode_t>(0700));
                ++result.directories;
                continue;
            }
            if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
                metadata.st_size < 0 ||
                (metadata.st_mode & static_cast<mode_t>(S_IRUSR)) == 0U) {
                return Status{ErrorCode::protocol_error,
                              "unselected tree-v2 entry is not a readable regular file"};
            }
            auto digest = hash_sync_file_sha256(iterator->path());
            if (!digest) return digest.status();
            const auto bytes = static_cast<std::uint64_t>(metadata.st_size);
            const mode_t owner_mode = metadata.st_mode &
                                      static_cast<mode_t>(0700);
            Status copied = copy_file_exact(iterator->path(), output,
                                            digest.value(), bytes, owner_mode,
                                            true,
                                            CopyDurability::filesystem_batch);
            if (!copied.ok()) return copied;
            ++result.files;
            if (result.bytes >
                std::numeric_limits<std::uint64_t>::max() - bytes) {
                return Status{ErrorCode::resource_exhausted,
                              "preserved tree-v2 byte count overflows"};
            }
            result.bytes += bytes;
        }
        for (auto iterator = directory_modes.rbegin();
             iterator != directory_modes.rend(); ++iterator) {
            if (::chmod(iterator->first.c_str(), iterator->second) != 0)
                return system_status("preserve unselected directory mode",
                                     iterator->first);
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error,
                      "unable to preserve unselected tree-v2 entries: " +
                          std::string(error.what())};
    }
    const Status durable = sync_filesystem(destination);
    if (!durable.ok()) return durable;
    const Status synced = sync_directory(destination);
    if (!synced.ok()) return synced;
    return result;
}

[[nodiscard]] Status write_marker(const std::filesystem::path &path,
                                  std::string_view text) {
    FileDescriptor descriptor(
        ::open(path.c_str(),
               O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600));
    if (descriptor.get() < 0)
        return system_status("create tree-v2 conflict marker", path);
    const Status written = write_all(
        descriptor.get(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()), text.size()),
        path);
    if (!written.ok()) return written;
    if (::fsync(descriptor.get()) != 0)
        return system_status("fsync tree-v2 conflict marker", path);
    return Status::success();
}

[[nodiscard]] Result<std::string>
projection_marker_text(const NamespacePolicy &policy,
                       const TreeV2Manifest &manifest,
                       const security::Sodium &sodium) {
    auto digest = tree_v2_manifest_digest(policy, manifest, sodium);
    if (!digest) return digest.status();
    std::string result =
        "namespace=" + policy.id +
        "\nmanifest=" + lower_hex(digest.value()) +
        "\nmetadata=" +
        std::string(tree_v2_metadata_mode_name(policy.projection.metadata)) +
        "\nincludes=" + std::to_string(policy.projection.includes.size()) +
        "\n";
    const auto append_rules = [&result](std::string_view kind,
                                        const auto &rules) {
        for (const std::string &rule : rules) {
            result += std::string(kind) + "=" +
                      lower_hex(std::span<const std::uint8_t>{
                          reinterpret_cast<const std::uint8_t *>(rule.data()),
                          rule.size()}) +
                      "\n";
        }
    };
    append_rules("include-hex", policy.projection.includes);
    result += "excludes=" +
              std::to_string(policy.projection.excludes.size()) + "\n";
    append_rules("exclude-hex", policy.projection.excludes);
    return result;
}

[[nodiscard]] Result<std::string> read_projection_marker(
    const std::filesystem::path &destination) {
    const std::filesystem::path marker =
        destination / std::string(kTreeV2ConflictRoot) / ".iotox-projection";
    struct stat before {};
    constexpr std::uint64_t maximum_bytes =
        static_cast<std::uint64_t>(kMaximumNamespaceRecordBytes) * 2U + 1024U;
    if (::lstat(marker.c_str(), &before) != 0 ||
        !S_ISREG(before.st_mode) || before.st_uid != ::geteuid() ||
        before.st_nlink != 1 ||
        (before.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) ||
        before.st_size <= 0 ||
        static_cast<std::uint64_t>(before.st_size) > maximum_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker is not canonical"};
    }
    FileDescriptor descriptor(
        ::open(marker.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 projection marker", marker);
    std::string observed(static_cast<std::size_t>(before.st_size), '\0');
    std::size_t offset = 0U;
    while (offset < observed.size()) {
        const ssize_t count = ::read(descriptor.get(), observed.data() + offset,
                                     observed.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker is not canonical"};
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0 ||
        !same_identity(before, after)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker changed while read"};
    }
    return observed;
}

[[nodiscard]] Result<TreeV2ProjectionPolicy> parse_projection_marker(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const std::filesystem::path &destination,
    const security::Sodium &sodium) {
    auto observed = read_projection_marker(destination);
    if (!observed) return observed.status();
    std::size_t offset = 0U;
    const auto next_line = [&observed, &offset]() -> Result<std::string_view> {
        const std::size_t end = observed.value().find('\n', offset);
        if (end == std::string::npos) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 projection marker is not canonical"};
        }
        const std::string_view line(observed.value().data() + offset,
                                    end - offset);
        offset = end + 1U;
        return line;
    };
    const auto field = [&next_line](std::string_view name)
        -> Result<std::string_view> {
        auto line = next_line();
        if (!line || !line.value().starts_with(name)) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 projection marker is not canonical"};
        }
        return line.value().substr(name.size());
    };
    const auto count = [](std::string_view value) -> Result<std::size_t> {
        std::size_t parsed = 0U;
        const auto converted =
            std::from_chars(value.data(), value.data() + value.size(), parsed);
        if (value.empty() || converted.ec != std::errc{} ||
            converted.ptr != value.data() + value.size() ||
            parsed > kMaximumTreeV2SelectionRules) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 projection marker count is invalid"};
        }
        return parsed;
    };
    const auto rule = [](std::string_view value) -> Result<std::string> {
        if (value.empty() || (value.size() % 2U) != 0U ||
            value.size() / 2U > kTreeV2MaximumPathBytes) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 projection marker rule is invalid"};
        }
        std::string decoded;
        decoded.reserve(value.size() / 2U);
        for (std::size_t index = 0U; index < value.size(); index += 2U) {
            const int high = hex_nibble(value[index]);
            const int low = hex_nibble(value[index + 1U]);
            if (high < 0 || low < 0) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 projection marker rule is invalid"};
            }
            decoded.push_back(static_cast<char>((high << 4U) | low));
        }
        return decoded;
    };

    auto namespace_id = field("namespace=");
    auto manifest_hex = field("manifest=");
    auto metadata = field("metadata=");
    auto includes = field("includes=");
    if (!namespace_id || !manifest_hex || !metadata || !includes ||
        namespace_id.value() != policy.id) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker identity is invalid"};
    }
    auto manifest = parse_digest(manifest_hex.value());
    auto active_digest = tree_v2_manifest_digest(policy, active, sodium);
    auto include_count = count(includes.value());
    if (!manifest || !active_digest || !include_count ||
        manifest.value() != active_digest.value()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker manifest is invalid"};
    }
    TreeV2ProjectionPolicy projection;
    if (metadata.value() == "executable-v1") {
        projection.metadata = TreeV2MetadataMode::executable_v1;
    } else if (metadata.value() == "owner-mode-v2") {
        projection.metadata = TreeV2MetadataMode::owner_mode_v2;
    } else {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker metadata is invalid"};
    }
    for (std::size_t index = 0U; index < include_count.value(); ++index) {
        auto encoded = field("include-hex=");
        if (!encoded) return encoded.status();
        auto decoded = rule(encoded.value());
        if (!decoded) return decoded.status();
        projection.includes.push_back(std::move(decoded).value());
    }
    auto excludes = field("excludes=");
    if (!excludes) return excludes.status();
    auto exclude_count = count(excludes.value());
    if (!exclude_count ||
        include_count.value() > kMaximumTreeV2SelectionRules -
                                    exclude_count.value()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker rules are excessive"};
    }
    for (std::size_t index = 0U; index < exclude_count.value(); ++index) {
        auto encoded = field("exclude-hex=");
        if (!encoded) return encoded.status();
        auto decoded = rule(encoded.value());
        if (!decoded) return decoded.status();
        projection.excludes.push_back(std::move(decoded).value());
    }
    NamespacePolicy previous = policy;
    previous.projection = projection;
    const Status valid = validate_namespace_policy(previous);
    auto canonical = projection_marker_text(previous, active, sodium);
    if (!valid.ok() || !canonical || offset != observed.value().size() ||
        canonical.value() != observed.value()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection marker is not canonical"};
    }
    return projection;
}

[[nodiscard]] bool projection_transition_marker_matches(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const TreeV2ProjectionPolicy &previous_projection,
    const std::filesystem::path &destination,
    const security::Sodium &sodium) {
    auto projection =
        parse_projection_marker(policy, active, destination, sodium);
    return projection && projection.value() == previous_projection &&
           previous_projection != policy.projection;
}

[[nodiscard]] bool projection_marker_matches_impl(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const std::filesystem::path &destination, const security::Sodium &sodium) {
    auto expected = projection_marker_text(policy, manifest, sodium);
    if (!expected) return false;
    const std::filesystem::path marker =
        destination / std::string(kTreeV2ConflictRoot) / ".iotox-projection";
    struct stat metadata {};
    if (::lstat(marker.c_str(), &metadata) != 0 || !S_ISREG(metadata.st_mode) ||
        metadata.st_uid != ::geteuid() || metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) ||
        metadata.st_size < 0 ||
        static_cast<std::size_t>(metadata.st_size) != expected.value().size()) {
        return false;
    }
    FileDescriptor descriptor(
        ::open(marker.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) return false;
    std::string observed(expected.value().size(), '\0');
    std::size_t offset = 0U;
    while (offset < observed.size()) {
        const ssize_t count = ::read(descriptor.get(), observed.data() + offset,
                                     observed.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return false;
    }
    return observed == expected.value();
}

[[nodiscard]] std::filesystem::path conflict_path(const TreeV2Entry &entry) {
    return std::filesystem::path(std::string(kTreeV2ConflictRoot)) /
           "by-origin" / lower_hex(entry.origin.writer) /
           std::to_string(entry.origin.generation) /
           std::string(tree_v2_entry_kind_name(entry.kind)) / entry.path;
}

} // namespace

bool tree_v2_projection_marker_matches(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const std::filesystem::path &destination,
    const security::Sodium &sodium) {
    return projection_marker_matches_impl(policy, manifest, destination,
                                          sodium);
}

Result<std::optional<TreeV2ProjectionPolicy>> tree_v2_projection_transition(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const std::filesystem::path &destination,
    const security::Sodium &sodium) {
    const Status valid = validate_tree_v2_manifest(policy, active);
    if (!valid.ok()) return valid;
    if (tree_v2_projection_marker_matches(policy, active, destination,
                                          sodium))
        return std::optional<TreeV2ProjectionPolicy>{};
    auto previous =
        parse_projection_marker(policy, active, destination, sodium);
    if (!previous) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 established projection marker is invalid: " +
                          previous.status().message()};
    }
    if (previous.value() == policy.projection) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 established projection marker is inconsistent"};
    }
    return std::optional<TreeV2ProjectionPolicy>{previous.value()};
}

Result<TreeV2ScanResult> scan_tree_v2_worktree(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::optional<TreeV2Manifest> &baseline,
    const PrincipalId &local_writer, std::uint64_t next_generation,
    const TreeV2ProjectionPolicy *previous_projection,
    const TreeV2SourceDigestCache *digest_cache,
    TreeV2SourceDigestCache *updated_digest_cache) {
    const Status valid_policy = validate_namespace_policy(policy);
    if (!valid_policy.ok()) return valid_policy;
    std::optional<NamespacePolicy> previous_policy;
    if (previous_projection != nullptr) {
        previous_policy = policy;
        previous_policy->projection = *previous_projection;
        const Status valid_previous =
            validate_namespace_policy(*previous_policy);
        if (!valid_previous.ok() ||
            previous_policy->projection == policy.projection) {
            return Status{
                ErrorCode::invalid_argument,
                "tree-v2 previous projection policy is invalid"};
        }
    }
    if (policy.engine != Engine::tree_v2 || source.empty() ||
        !source.is_absolute() || source.lexically_normal() != source ||
        next_generation == 0U || all_zero(local_writer) ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            local_writer)) {
        return Status{
            ErrorCode::invalid_argument,
            "tree-v2 scan policy, source, writer, or generation is invalid"};
    }
    const Status controlled =
        validate_owned_directory(source, "tree-v2 worktree");
    if (!controlled.ok()) return controlled;
    if (baseline) {
        const Status valid_baseline =
            validate_tree_v2_manifest(policy, *baseline);
        if (!valid_baseline.ok()) return valid_baseline;
    }

    const std::filesystem::path normalized_source = source.lexically_normal();
    const bool cache_compatible =
        digest_cache != nullptr && digest_cache->verified_ &&
        digest_cache->namespace_id_ == policy.id &&
        digest_cache->source_ == normalized_source &&
        digest_cache->projection_ == policy.projection;
    TreeV2SourceDigestCache next_cache;
    if (updated_digest_cache != nullptr) {
        next_cache.namespace_id_ = policy.id;
        next_cache.source_ = normalized_source;
        next_cache.projection_ = policy.projection;
        next_cache.verified_ = true;
    }

    std::vector<TreeV2Entry> observed;
    TreeV2ScanResult result;
    std::set<std::string> observed_paths;
    try {
        const auto observe_entry =
            [&](auto &&self, const std::filesystem::path &absolute,
                const std::string &relative,
                bool recurse_children) -> Result<bool> {
            struct stat metadata {};
            if (::lstat(absolute.c_str(), &metadata) != 0)
                return system_status("inspect tree-v2 worktree entry",
                                     absolute);
            const bool directory = S_ISDIR(metadata.st_mode);
            if (!observed_paths.insert(relative).second) return directory;
            ++result.inspected_entries;

            const std::filesystem::path relative_path{relative};
            if (relative_path.begin() != relative_path.end() &&
                relative_path.begin()->string() == kTreeV2ConflictRoot) {
                if (relative_path ==
                    std::filesystem::path(std::string(kTreeV2ConflictRoot))) {
                    if (!directory || metadata.st_uid != ::geteuid() ||
                        (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
                        return Status{ErrorCode::protocol_error,
                                      "tree-v2 conflict projection is unsafe"};
                    }
                }
                return directory;
            }
            if (!valid_tree_v2_path(relative) ||
                metadata.st_uid != ::geteuid() ||
                (metadata.st_mode & static_cast<mode_t>(0022)) != 0U) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 worktree entry path or ownership is unsafe"};
            }
            if (!tree_v2_path_selected(policy, relative, directory)) {
                if (!directory &&
                    (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
                     metadata.st_size < 0)) {
                    return Status{ErrorCode::protocol_error,
                                  "unselected tree-v2 entry is linked or special"};
                }
                return directory;
            }

            TreeV2Entry entry;
            entry.path = relative;
            entry.origin = TreeV2Version{local_writer, next_generation};
            if (directory) {
                entry.kind = TreeV2EntryKind::directory;
                ++result.directories;
            } else if (S_ISREG(metadata.st_mode) && metadata.st_nlink == 1 &&
                       metadata.st_size >= 0) {
                entry.kind = TreeV2EntryKind::file;
                entry.content_bytes =
                    static_cast<std::uint64_t>(metadata.st_size);
                entry.executable =
                    (metadata.st_mode & static_cast<mode_t>(S_IXUSR)) != 0U;
                if (policy.projection.metadata ==
                    TreeV2MetadataMode::owner_mode_v2) {
                    entry.owner_mode = static_cast<std::uint8_t>(
                        (metadata.st_mode & static_cast<mode_t>(0700)) >> 6U);
                    if (entry.owner_mode < 4U) {
                        return Status{ErrorCode::protocol_error,
                                      "tree-v2 owner-mode file is not owner-readable"};
                    }
                }
                const TreeV2SourceDigestCache::FileIdentity file_identity =
                    source_file_identity(metadata);
                bool reused_digest = false;
                if (cache_compatible) {
                    const auto cached = digest_cache->files_.find(entry.path);
                    if (cached != digest_cache->files_.end() &&
                        cached->second.identity == file_identity &&
                        cached->second.content_bytes == entry.content_bytes) {
                        entry.content = cached->second.content;
                        ++result.reused_file_digests;
                        reused_digest = true;
                    }
                }
                if (!reused_digest) {
                    auto digest = hash_sync_file_sha256(absolute);
                    if (!digest) return digest.status();
                    entry.content = digest.value();
                    ++result.hashed_file_digests;
                }
                if (updated_digest_cache != nullptr) {
                    next_cache.files_.emplace(
                        entry.path,
                        TreeV2SourceDigestCache::Entry{
                            file_identity, entry.content,
                            entry.content_bytes});
                }
                if (result.file_bytes >
                    std::numeric_limits<std::uint64_t>::max() -
                        entry.content_bytes) {
                    return Status{ErrorCode::resource_exhausted,
                                  "tree-v2 worktree byte count overflows"};
                }
                result.file_bytes += entry.content_bytes;
                result.files.push_back(TreeV2ScannedFile{
                    entry.path, entry.content, entry.content_bytes, absolute});
            } else {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 worktree contains a linked or special entry"};
            }
            if (observed.size() >= policy.quotas.maximum_objects ||
                result.file_bytes > policy.quotas.maximum_artifact_bytes) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 worktree exceeds namespace quota"};
            }
            observed.push_back(std::move(entry));

            if (directory && recurse_children) {
                for (const auto &child :
                     std::filesystem::directory_iterator(absolute)) {
                    const std::string child_name =
                        child.path().filename().generic_string();
                    const std::string child_relative =
                        relative + "/" + child_name;
                    auto child_result =
                        self(self, child.path(), child_relative, true);
                    if (!child_result) return child_result.status();
                }
            }
            return directory;
        };

        const auto observe_if_present =
            [&](const std::string &relative,
                bool recurse_children) -> Result<std::optional<bool>> {
            const std::filesystem::path absolute =
                (source / std::filesystem::path(relative)).lexically_normal();
            struct stat metadata {};
            if (::lstat(absolute.c_str(), &metadata) != 0) {
                if (errno == ENOENT)
                    return std::optional<bool>{};
                return system_status("inspect tree-v2 selected worktree entry",
                                     absolute);
            }
            auto observed_directory =
                observe_entry(observe_entry, absolute, relative,
                              recurse_children);
            if (!observed_directory) return observed_directory.status();
            return std::optional<bool>{observed_directory.value()};
        };

        if (policy.projection.includes.empty()) {
            for (const auto &child :
                 std::filesystem::directory_iterator(source)) {
                const std::string relative =
                    child.path().filename().generic_string();
                auto observed_directory =
                    observe_entry(observe_entry, child.path(), relative, true);
                if (!observed_directory) return observed_directory.status();
            }
        } else {
            for (const std::string &root :
                 minimal_include_roots(policy.projection.includes)) {
                bool reachable = true;
                std::size_t separator = root.find('/');
                while (separator != std::string::npos) {
                    const std::string ancestor = root.substr(0U, separator);
                    auto observed_ancestor =
                        observe_if_present(ancestor, false);
                    if (!observed_ancestor) return observed_ancestor.status();
                    if (!observed_ancestor.value().value_or(false)) {
                        reachable = false;
                        break;
                    }
                    separator = root.find('/', separator + 1U);
                }
                if (!reachable) continue;
                auto observed_root = observe_if_present(root, true);
                if (!observed_root) return observed_root.status();
            }
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error, "unable to scan tree-v2 worktree: " +
                                               std::string(error.what())};
    }
    std::sort(observed.begin(), observed.end(), entry_less);
    std::sort(
        result.files.begin(), result.files.end(),
        [](const TreeV2ScannedFile &left, const TreeV2ScannedFile &right) {
            return left.path < right.path;
        });

    std::set<std::string> paths;
    std::map<std::string, const TreeV2Entry *> observed_by_path;
    for (const TreeV2Entry &entry : observed) {
        observed_by_path.emplace(entry.path, &entry);
        paths.insert(entry.path);
    }
    std::map<std::string, std::vector<TreeV2Entry>> prior_by_path;
    if (baseline) {
        for (const TreeV2Entry &entry : baseline->entries) {
            prior_by_path[entry.path].push_back(entry);
            paths.insert(entry.path);
        }
    }
    const std::vector<TreeV2Entry> empty_prior;
    for (const std::string &path : paths) {
        const auto current = observed_by_path.find(path);
        const auto prior_iterator = prior_by_path.find(path);
        const std::vector<TreeV2Entry> &prior =
            prior_iterator == prior_by_path.end() ? empty_prior
                                                  : prior_iterator->second;
        const bool directory =
            current != observed_by_path.end()
                ? current->second->kind == TreeV2EntryKind::directory
                : std::any_of(prior.begin(), prior.end(),
                              [](const TreeV2Entry &entry) {
                                  return entry.kind ==
                                         TreeV2EntryKind::directory;
                              });
        if (!tree_v2_path_selected(policy, path, directory)) {
            result.manifest.entries.insert(result.manifest.entries.end(),
                                           prior.begin(), prior.end());
            continue;
        }
        std::optional<TreeV2Entry> selected;
        if (!prior.empty()) {
            auto choice = select_tree_v2_projection_entry(prior);
            if (!choice) return choice.status();
            selected = choice.value();
        }
        if (current != observed_by_path.end() && selected &&
            same_payload(*current->second, *selected)) {
            result.manifest.entries.insert(result.manifest.entries.end(),
                                           prior.begin(), prior.end());
            continue;
        }
        if (current == observed_by_path.end() && selected &&
            selected->kind == TreeV2EntryKind::tombstone) {
            result.manifest.entries.insert(result.manifest.entries.end(),
                                           prior.begin(), prior.end());
            continue;
        }
        if (current == observed_by_path.end() && previous_policy &&
            !tree_v2_path_selected(*previous_policy, path, directory) &&
            std::any_of(prior.begin(), prior.end(),
                        [](const TreeV2Entry &entry) {
                            return entry.kind != TreeV2EntryKind::tombstone;
                        })) {
            result.manifest.entries.insert(result.manifest.entries.end(),
                                           prior.begin(), prior.end());
            continue;
        }
        if (current != observed_by_path.end()) {
            result.manifest.entries.push_back(*current->second);
        } else if (selected) {
            result.manifest.entries.push_back(
                TreeV2Entry{path,
                            TreeV2EntryKind::tombstone,
                            TreeV2Version{local_writer, next_generation},
                            {},
                            0U,
                            false});
        }
        ++result.new_events;
    }
    std::sort(result.manifest.entries.begin(), result.manifest.entries.end(),
              entry_less);
    const Status valid_manifest =
        validate_tree_v2_manifest(policy, result.manifest);
    if (!valid_manifest.ok()) return valid_manifest;
    result.changed = !baseline || result.manifest != *baseline;
    if (updated_digest_cache != nullptr)
        *updated_digest_cache = std::move(next_cache);
    return result;
}

std::filesystem::path tree_v2_object_path(const NamespacePolicy &policy,
                                          const Digest &digest) {
    const std::string hex = lower_hex(digest);
    return std::filesystem::path(policy.root) / "tree-v2" / "objects" /
           hex.substr(0U, 2U) / hex.substr(2U);
}

Status verify_tree_v2_object_file(const std::filesystem::path &path,
                                  const Digest &digest,
                                  std::uint64_t expected_bytes) {
    return validate_object_file(path, digest, expected_bytes);
}

Result<TreeV2ObjectStoreResult>
store_tree_v2_object_file(const NamespacePolicy &policy, const Digest &digest,
                          std::uint64_t expected_bytes,
                          const std::filesystem::path &source,
                          const SyncNamespaceTransaction &transaction) {
    TreeV2ScanResult scan;
    scan.files.push_back(TreeV2ScannedFile{"", digest, expected_bytes, source});
    return store_tree_v2_scan_objects(policy, scan, transaction);
}

std::filesystem::path
tree_v2_worktree_staging_path(const NamespacePolicy &policy,
                              const std::filesystem::path &destination) {
    return destination.parent_path() / ("." + destination.filename().string() +
                                        ".iotox-" + policy.id + ".stage");
}

Result<TreeV2ObjectInventory>
inspect_tree_v2_object_store(const NamespacePolicy &policy,
                            const SyncNamespaceTransaction &transaction) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    const std::filesystem::path root(policy.root);
    Status prepared = validate_owned_directory(root, "tree-v2 namespace root");
    if (!prepared.ok()) return prepared;
    prepared = ensure_private_directory(root / "tree-v2");
    if (!prepared.ok()) return prepared;
    const std::filesystem::path objects = root / "tree-v2" / "objects";
    prepared = ensure_private_directory(objects);
    if (!prepared.ok()) return prepared;

    TreeV2ObjectInventory inventory;
    inventory.namespace_id_ = policy.id;
    inventory.root_ = root.lexically_normal();
    try {
        for (const auto &fanout :
             std::filesystem::directory_iterator(objects)) {
            const std::string prefix = fanout.path().filename().string();
            if (prefix.size() != 2U || hex_nibble(prefix[0U]) < 0 ||
                hex_nibble(prefix[1U]) < 0) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 object store has an invalid fanout"};
            }
            prepared = ensure_private_directory(fanout.path());
            if (!prepared.ok()) return prepared;
            const std::filesystem::path temporary =
                fanout.path() / ".install.tmp";
            struct stat temporary_metadata {};
            if (::lstat(temporary.c_str(), &temporary_metadata) == 0) {
                if (!S_ISREG(temporary_metadata.st_mode) ||
                    temporary_metadata.st_uid != ::geteuid() ||
                    temporary_metadata.st_nlink != 1 ||
                    (temporary_metadata.st_mode & static_cast<mode_t>(0777)) !=
                        static_cast<mode_t>(0600) ||
                    ::unlink(temporary.c_str()) != 0) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object temporary is unsafe"};
                }
                prepared = sync_directory(fanout.path());
                if (!prepared.ok()) return prepared;
            } else if (errno != ENOENT) {
                return system_status("inspect tree-v2 object temporary",
                                     temporary);
            }
            for (const auto &object :
                 std::filesystem::directory_iterator(fanout.path())) {
                const std::string suffix = object.path().filename().string();
                auto identity = parse_digest(prefix + suffix);
                if (!identity) return identity.status();
                struct stat metadata {};
                if (::lstat(object.path().c_str(), &metadata) != 0 ||
                    !S_ISREG(metadata.st_mode) || metadata.st_size < 0) {
                    return Status{
                        ErrorCode::protocol_error,
                        "tree-v2 object store contains an unsafe entry"};
                }
                const std::uint64_t bytes =
                    static_cast<std::uint64_t>(metadata.st_size);
                prepared = validate_object_file(object.path(), identity.value(),
                                                bytes);
                if (!prepared.ok()) return prepared;
                if (!inventory.objects_.emplace(identity.value(), bytes)
                         .second) {
                    return Status{
                        ErrorCode::protocol_error,
                        "tree-v2 object identity appears more than once"};
                }
                if (inventory.bytes_ >
                    std::numeric_limits<std::uint64_t>::max() - bytes) {
                    return Status{ErrorCode::resource_exhausted,
                                  "tree-v2 object inventory overflows"};
                }
                inventory.bytes_ += bytes;
            }
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect tree-v2 object store: " +
                          std::string(error.what())};
    }

    if (inventory.objects_.size() > policy.quotas.maximum_objects ||
        inventory.bytes_ > policy.quotas.maximum_store_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 object store exceeds namespace quota"};
    }
    inventory.verified_ = true;
    return inventory;
}

Result<TreeV2ObjectStoreResult> revalidate_tree_v2_object_store(
    const NamespacePolicy &policy, const TreeV2ObjectInventory &inventory,
    const SyncNamespaceTransaction &transaction) {
    if (!inventory.verified_ || inventory.namespace_id_ != policy.id ||
        inventory.root_ !=
            std::filesystem::path(policy.root).lexically_normal()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 object inventory does not match namespace"};
    }
    auto observed = inspect_tree_v2_object_store(policy, transaction);
    if (!observed) return observed.status();
    for (const auto &[digest, bytes] : inventory.objects_) {
        const auto current = observed.value().objects_.find(digest);
        if (current == observed.value().objects_.end() ||
            current->second != bytes) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 cached object changed before effect admission"};
        }
    }
    TreeV2ObjectStoreResult result;
    result.inspected_objects = observed.value().objects_.size();
    result.inspected_bytes = observed.value().bytes_;
    return result;
}

Result<TreeV2ObjectStoreResult>
store_tree_v2_scan_objects(const NamespacePolicy &policy,
                           const TreeV2ScanResult &scan,
                           const SyncNamespaceTransaction &transaction) {
    auto inventory = inspect_tree_v2_object_store(policy, transaction);
    if (!inventory) return inventory.status();
    const std::uint64_t inspected_objects = inventory.value().objects();
    const std::uint64_t inspected_bytes = inventory.value().bytes();
    auto stored = store_tree_v2_scan_objects(policy, scan, inventory.value(),
                                             transaction);
    if (!stored) return stored.status();
    stored.value().inspected_objects = inspected_objects;
    stored.value().inspected_bytes = inspected_bytes;
    return stored;
}

Result<TreeV2ObjectStoreResult> store_tree_v2_scan_objects(
    const NamespacePolicy &policy, const TreeV2ScanResult &scan,
    TreeV2ObjectInventory &inventory,
    const SyncNamespaceTransaction &transaction) {
    const Status valid = validate_tree_v2_manifest(policy, scan.manifest);
    if (!valid.ok()) return valid;
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    const std::filesystem::path root(policy.root);
    if (!inventory.verified_ || inventory.namespace_id_ != policy.id ||
        inventory.root_ != root.lexically_normal()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 object inventory does not match namespace"};
    }
    Status prepared = validate_owned_directory(root, "tree-v2 namespace root");
    if (!prepared.ok()) return prepared;
    prepared = ensure_private_directory(root / "tree-v2");
    if (!prepared.ok()) return prepared;
    prepared = ensure_private_directory(root / "tree-v2" / "objects");
    if (!prepared.ok()) return prepared;

    std::map<Digest, TreeV2ScannedFile> requested;
    for (const TreeV2ScannedFile &file : scan.files) {
        const auto inserted = requested.emplace(file.content, file);
        if (!inserted.second &&
            inserted.first->second.content_bytes != file.content_bytes) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 scan gives one digest conflicting sizes"};
        }
    }
    TreeV2ObjectStoreResult result;
    std::uint64_t prospective_objects = inventory.objects_.size();
    std::uint64_t prospective_bytes = inventory.bytes_;
    for (const auto &[digest, file] : requested) {
        const auto existing = inventory.objects_.find(digest);
        if (existing != inventory.objects_.end()) {
            if (existing->second != file.content_bytes) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 existing object size conflicts with scan"};
            }
            prepared = validate_object_file(tree_v2_object_path(policy, digest),
                                            digest, file.content_bytes);
            if (!prepared.ok()) return prepared;
            ++result.reused_objects;
            continue;
        }
        if (prospective_objects == std::numeric_limits<std::uint64_t>::max() ||
            prospective_bytes > std::numeric_limits<std::uint64_t>::max() -
                                    file.content_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 prospective object store overflows"};
        }
        ++prospective_objects;
        prospective_bytes += file.content_bytes;
    }
    if (prospective_objects > policy.quotas.maximum_objects ||
        prospective_bytes > policy.quotas.maximum_store_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 prospective object store exceeds quota"};
    }

    for (const auto &[digest, file] : requested) {
        if (inventory.objects_.contains(digest)) continue;
        const std::filesystem::path destination =
            tree_v2_object_path(policy, digest);
        prepared = ensure_private_directory(destination.parent_path());
        if (!prepared.ok()) return prepared;
        const std::filesystem::path temporary =
            destination.parent_path() / ".install.tmp";
        struct stat prior {};
        if (::lstat(temporary.c_str(), &prior) == 0) {
            if (!S_ISREG(prior.st_mode) || prior.st_uid != ::geteuid() ||
                prior.st_nlink != 1 ||
                (prior.st_mode & static_cast<mode_t>(0777)) !=
                    static_cast<mode_t>(0600) ||
                ::unlink(temporary.c_str()) != 0) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 object install temporary is unsafe"};
            }
        } else if (errno != ENOENT) {
            return system_status("inspect tree-v2 object install temporary",
                                 temporary);
        }
        prepared = copy_file_exact(file.source, temporary, file.content,
                                   file.content_bytes, 0600, true);
        if (!prepared.ok()) {
            static_cast<void>(::unlink(temporary.c_str()));
            return prepared;
        }
        if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                      destination.c_str(), RENAME_NOREPLACE) != 0) {
            const int saved = errno;
            static_cast<void>(::unlink(temporary.c_str()));
            if (saved != EEXIST)
                return Status{saved == ENOSYS ? ErrorCode::unsupported
                                              : ErrorCode::io_error,
                              "install tree-v2 object: " +
                                  std::string(std::strerror(saved))};
            prepared = validate_object_file(destination, file.content,
                                            file.content_bytes);
            if (!prepared.ok()) return prepared;
            const auto inserted =
                inventory.objects_.emplace(digest, file.content_bytes);
            if (inserted.second) inventory.bytes_ += file.content_bytes;
            ++result.reused_objects;
            continue;
        }
        prepared = sync_directory(destination.parent_path());
        if (!prepared.ok()) return prepared;
        inventory.objects_.emplace(digest, file.content_bytes);
        inventory.bytes_ += file.content_bytes;
        ++result.installed_objects;
        result.installed_bytes += file.content_bytes;
    }
    return result;
}

Result<TreeV2ProjectionResult> materialize_tree_v2_merge(
    const NamespacePolicy &policy, const TreeV2MergeResult &merge,
    const std::filesystem::path &destination, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    const Status valid = validate_tree_v2_manifest(policy, merge.manifest);
    if (!valid.ok()) return valid;
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    if (destination.empty() || !destination.is_absolute() ||
        destination.lexically_normal() != destination) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 projection destination is invalid"};
    }
    const Status controlled_parent = validate_owned_directory(
        destination.parent_path(), "tree-v2 projection parent");
    if (!controlled_parent.ok()) return controlled_parent;
    struct stat existing {};
    if (::lstat(destination.c_str(), &existing) == 0 || errno != ENOENT) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 projection destination must be absent"};
    }
    if (::mkdir(destination.c_str(), static_cast<mode_t>(0700)) != 0)
        return system_status("create tree-v2 projection", destination);
    ProjectionCleanup cleanup(destination);

    TreeV2ProjectionResult result;
    for (auto first = merge.manifest.entries.begin();
         first != merge.manifest.entries.end();) {
        const auto last = std::find_if(
            first, merge.manifest.entries.end(),
            [&first](const TreeV2Entry &entry) {
                return entry.path != first->path;
            });
        const std::span<const TreeV2Entry> candidates{
            &*first, static_cast<std::size_t>(last - first)};
        auto selected = select_tree_v2_projection_entry(candidates);
        if (!selected) return selected.status();
        const TreeV2Entry &entry = selected.value();
        if (!tree_v2_path_selected(policy, entry.path,
                                   entry.kind == TreeV2EntryKind::directory)) {
            first = last;
            continue;
        }
        if (entry.kind == TreeV2EntryKind::tombstone) {
            first = last;
            continue;
        }
        const Status parent = ensure_projection_parent(destination, entry.path);
        if (!parent.ok()) return parent;
        const std::filesystem::path output = destination / entry.path;
        if (entry.kind == TreeV2EntryKind::directory) {
            const Status created = ensure_private_directory(output);
            if (!created.ok()) return created;
            ++result.directories;
            first = last;
            continue;
        }
        const std::filesystem::path object =
            tree_v2_object_path(policy, entry.content);
        Status copied =
            validate_object_file(object, entry.content, entry.content_bytes);
        if (!copied.ok()) return copied;
        const mode_t output_mode = entry.owner_mode != 0U
                                       ? static_cast<mode_t>(entry.owner_mode)
                                             << 6U
                                       : entry.executable ? 0700 : 0600;
        copied = copy_file_exact(object, output, entry.content,
                                 entry.content_bytes, output_mode, true,
                                 CopyDurability::filesystem_batch);
        if (!copied.ok()) return copied;
        ++result.files;
        result.bytes += entry.content_bytes;
        first = last;
    }

    for (const TreeV2Conflict &conflict : merge.conflicts) {
        auto selected = select_tree_v2_projection_entry(conflict.candidates);
        if (!selected) return selected.status();
        if (!tree_v2_path_selected(
                policy, conflict.path,
                selected.value().kind == TreeV2EntryKind::directory))
            continue;
        for (const TreeV2Entry &candidate : conflict.candidates) {
            if (candidate == selected.value()) continue;
            const std::filesystem::path relative = conflict_path(candidate);
            const Status parent = ensure_projection_parent(
                destination, relative.generic_string());
            if (!parent.ok()) return parent;
            std::filesystem::path output = destination / relative;
            if (candidate.kind == TreeV2EntryKind::file) {
                const std::filesystem::path object =
                    tree_v2_object_path(policy, candidate.content);
                Status copied = validate_object_file(object, candidate.content,
                                                     candidate.content_bytes);
                if (!copied.ok()) return copied;
                const mode_t output_mode =
                    candidate.owner_mode != 0U
                        ? static_cast<mode_t>(candidate.owner_mode) << 6U
                        : candidate.executable ? 0700 : 0600;
                copied = copy_file_exact(object, output, candidate.content,
                                         candidate.content_bytes, output_mode,
                                         true,
                                         CopyDurability::filesystem_batch);
                if (!copied.ok()) return copied;
                ++result.conflict_files;
                continue;
            }
            if (candidate.kind == TreeV2EntryKind::directory) {
                const Status created = ensure_private_directory(output);
                if (!created.ok()) return created;
                output /= ".iotox-directory";
            } else {
                output += ".iotox-tombstone";
            }
            const std::string marker =
                "writer=" + lower_hex(candidate.origin.writer) + "\n" +
                "generation=" + std::to_string(candidate.origin.generation) +
                "\nkind=" +
                std::string(tree_v2_entry_kind_name(candidate.kind)) + "\n";
            const Status written = write_marker(output, marker);
            if (!written.ok()) return written;
            if (candidate.kind == TreeV2EntryKind::tombstone)
                ++result.conflict_tombstones;
        }
    }
    const std::filesystem::path conflict_root =
        destination / std::string(kTreeV2ConflictRoot);
    const Status conflict_root_ready = ensure_private_directory(conflict_root);
    if (!conflict_root_ready.ok()) return conflict_root_ready;
    auto marker = projection_marker_text(policy, merge.manifest, sodium);
    if (!marker) return marker.status();
    const Status marker_written =
        write_marker(conflict_root / ".iotox-projection", marker.value());
    if (!marker_written.ok()) return marker_written;
    const Status durable = sync_filesystem(destination);
    if (!durable.ok()) return durable;
    const Status synced = sync_directory(destination);
    if (!synced.ok()) return synced;
    const Status parent_synced = sync_directory(destination.parent_path());
    if (!parent_synced.ok()) return parent_synced;
    cleanup.release();
    return result;
}

Result<TreeV2WorktreeUpdateResult> update_tree_v2_worktree(
    const NamespacePolicy &policy, const TreeV2Manifest &expected_worktree,
    const TreeV2MergeResult &target, const std::filesystem::path &destination,
    const PrincipalId &local_writer, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    const TreeV2Manifest *authenticated_active_projection,
    const TreeV2WorktreeSeams &seams) {
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    const Status valid_expected =
        validate_tree_v2_manifest(policy, expected_worktree);
    if (!valid_expected.ok()) return valid_expected;
    const Status valid_target =
        validate_tree_v2_manifest(policy, target.manifest);
    if (!valid_target.ok()) return valid_target;
    if (authenticated_active_projection != nullptr) {
        const Status valid_active = validate_tree_v2_manifest(
            policy, *authenticated_active_projection);
        if (!valid_active.ok()) return valid_active;
    }
    if (destination.empty() || !destination.is_absolute() ||
        destination.lexically_normal() != destination ||
        destination == destination.root_path() ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            local_writer)) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 writable projection identity is invalid"};
    }
    const TreeV2Manifest *marker_manifest =
        authenticated_active_projection != nullptr
            ? authenticated_active_projection
            : &expected_worktree;
    std::optional<TreeV2ProjectionPolicy> previous_projection;
    bool old_marker_authenticated = false;
    if (authenticated_active_projection != nullptr) {
        auto transition = tree_v2_projection_transition(
            policy, *authenticated_active_projection, destination, sodium);
        if (!transition) return transition.status();
        previous_projection = std::move(transition).value();
        old_marker_authenticated = true;
    } else {
        old_marker_authenticated = tree_v2_projection_marker_matches(
            policy, expected_worktree, destination, sodium);
    }
    auto before = scan_tree_v2_worktree(policy, destination, expected_worktree,
                                        local_writer, 1U,
                                        previous_projection
                                            ? &*previous_projection
                                            : nullptr);
    if (!before) return before.status();
    if (before.value().changed) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 worktree changed after its baseline scan"};
    }
    if (expected_worktree == target.manifest &&
        tree_v2_projection_marker_matches(policy, expected_worktree,
                                          destination, sodium)) {
        return TreeV2WorktreeUpdateResult{TreeV2ProjectionResult{}, false};
    }

    const std::string filename = destination.filename().string();
    if (filename.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 writable projection has no filename"};
    }
    const std::filesystem::path staging =
        tree_v2_worktree_staging_path(policy, destination);
    struct stat staging_metadata {};
    if (::lstat(staging.c_str(), &staging_metadata) == 0 || errno != ENOENT) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 projection staging path is occupied"};
    }
    auto projected =
        materialize_tree_v2_merge(policy, target, staging, sodium, transaction);
    if (!projected) return projected.status();
    const auto discard_staging = [&staging]() {
        return remove_owned_tree(staging);
    };

    auto preserved =
        preserve_unselected_tree(policy, destination, staging);
    if (!preserved) {
        const Status discarded = discard_staging();
        if (!discarded.ok()) return discarded;
        return preserved.status();
    }

    auto rechecked = scan_tree_v2_worktree(
        policy, destination, expected_worktree, local_writer, 1U,
        previous_projection ? &*previous_projection : nullptr);
    if (!rechecked || rechecked.value().changed) {
        const Status discarded = discard_staging();
        if (!discarded.ok()) return discarded;
        return rechecked ? Status{ErrorCode::unavailable,
                                  "tree-v2 worktree changed while its target "
                                  "was built"}
                         : rechecked.status();
    }
    if (seams.before_exchange) {
        const Status injected = seams.before_exchange();
        if (!injected.ok()) {
            const Status discarded = discard_staging();
            if (!discarded.ok()) return discarded;
            return injected;
        }
    }
    if (::syscall(SYS_renameat2, AT_FDCWD, destination.c_str(), AT_FDCWD,
                  staging.c_str(), RENAME_EXCHANGE) != 0) {
        const int saved = errno;
        const Status discarded = discard_staging();
        if (!discarded.ok()) return discarded;
        return Status{saved == ENOSYS || saved == EINVAL
                          ? ErrorCode::unsupported
                          : ErrorCode::io_error,
                      "exchange tree-v2 writable projection: " +
                          std::string(std::strerror(saved))};
    }
    const Status parent_synced = sync_directory(destination.parent_path());
    if (!parent_synced.ok()) return parent_synced;
    if (seams.after_exchange) {
        const Status injected = seams.after_exchange();
        if (!injected.ok()) return injected;
    }

    auto visible = scan_tree_v2_worktree(policy, destination, target.manifest,
                                         local_writer, 1U);
    if (!visible) return visible.status();
    if (visible.value().changed) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 exchanged projection does not match its target"};
    }
    if (!tree_v2_projection_marker_matches(policy, target.manifest,
                                           destination, sodium)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 exchanged projection marker does not match"};
    }
    const Status old_valid = validate_old_projection(
        policy, expected_worktree,
        old_marker_authenticated ? marker_manifest : nullptr, staging,
        destination, local_writer, sodium,
        previous_projection ? &*previous_projection : nullptr);
    if (!old_valid.ok()) return old_valid;
    const Status discarded = discard_staging();
    if (!discarded.ok()) return discarded;
    TreeV2WorktreeUpdateResult result{projected.value(), true};
    result.preserved_unselected_entries = preserved.value().entries;
    result.preserved_unselected_directories = preserved.value().directories;
    result.preserved_unselected_files = preserved.value().files;
    result.preserved_unselected_bytes = preserved.value().bytes;
    return result;
}

Result<TreeV2WorktreeUpdateResult> recover_tree_v2_worktree_exchange(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const TreeV2Manifest &expected_worktree, const TreeV2MergeResult &pending,
    const std::filesystem::path &destination, const PrincipalId &local_writer,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    const Status valid_active = validate_tree_v2_manifest(policy, active);
    if (!valid_active.ok()) return valid_active;
    const Status valid_expected =
        validate_tree_v2_manifest(policy, expected_worktree);
    if (!valid_expected.ok()) return valid_expected;
    const Status valid_pending =
        validate_tree_v2_manifest(policy, pending.manifest);
    if (!valid_pending.ok()) return valid_pending;
    if (active == pending.manifest) {
        return Status{
            ErrorCode::invalid_argument,
            "tree-v2 recovery active and pending manifests are equal"};
    }
    auto pending_scan = scan_tree_v2_worktree(
        policy, destination, pending.manifest, local_writer, 1U);
    const bool pending_marker = tree_v2_projection_marker_matches(
        policy, pending.manifest, destination, sodium);
    const bool pending_visible =
        pending_scan && !pending_scan.value().changed && pending_marker;
    // Ordinary applications do not take the namespace transaction. They can
    // edit the newly exchanged directory after rename but before the signed
    // workspace marker is finished. A pending marker plus a structurally
    // valid scan still identifies that side unambiguously; retain those local
    // edits so the caller can publish them as the next forward transition.
    const bool pending_locally_modified =
        pending_scan && pending_scan.value().changed && pending_marker;
    std::optional<TreeV2ProjectionPolicy> source_previous_projection;
    bool source_marker = false;
    if (!pending_marker) {
        auto transition = tree_v2_projection_transition(
            policy, active, destination, sodium);
        if (!transition) return transition.status();
        source_previous_projection = std::move(transition).value();
        source_marker = true;
    }
    auto expected_scan = scan_tree_v2_worktree(
        policy, destination, expected_worktree, local_writer, 1U,
        source_previous_projection ? &*source_previous_projection : nullptr);
    const bool source_visible =
        expected_scan && !expected_scan.value().changed && source_marker;
    if (source_visible == (pending_visible || pending_locally_modified)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 pending exchange has ambiguous visible truth"};
    }

    const std::filesystem::path staging =
        tree_v2_worktree_staging_path(policy, destination);
    struct stat staging_metadata {};
    const bool staging_exists =
        ::lstat(staging.c_str(), &staging_metadata) == 0;
    if (!staging_exists && errno != ENOENT) {
        return system_status("inspect tree-v2 recovery staging", staging);
    }
    if (pending_visible || pending_locally_modified) {
        if (staging_exists) {
            auto transition = tree_v2_projection_transition(
                policy, active, staging, sodium);
            if (!transition) return transition.status();
            auto previous_projection = std::move(transition).value();
            const Status old_valid = validate_old_projection(
                policy, expected_worktree, &active, staging, destination,
                local_writer, sodium,
                previous_projection ? &*previous_projection : nullptr);
            if (!old_valid.ok()) return old_valid;
            const Status removed = remove_owned_tree(staging);
            if (!removed.ok()) return removed;
        }
        return TreeV2WorktreeUpdateResult{TreeV2ProjectionResult{}, true};
    }

    if (staging_exists) {
        const Status removed = remove_owned_tree(staging);
        if (!removed.ok()) return removed;
    }
    return update_tree_v2_worktree(policy, expected_worktree, pending,
                                   destination, local_writer, sodium,
                                   transaction, &active);
}

} // namespace iotox::sync
