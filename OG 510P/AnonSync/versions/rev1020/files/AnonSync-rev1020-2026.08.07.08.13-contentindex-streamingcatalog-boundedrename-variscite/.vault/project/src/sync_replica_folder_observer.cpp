#include "sync_replica_folder_observer.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_directory_authority_internal.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_posix_directory_resolution.hpp"

#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <dirent.h>
#include <filesystem>
#include <exception>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    explicit ScopedFd(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept
        : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }

private:
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

    int descriptor_ = -1;
};

class ScopedDirectoryStream final {
public:
    explicit ScopedDirectoryStream(int owned_descriptor,
                                   const std::string& label) {
        stream_ = ::fdopendir(owned_descriptor);
        if (stream_ == nullptr) {
            const int error = errno;
            (void)::close(owned_descriptor);
            throw std::runtime_error(
                label + " fdopendir failed: " + std::strerror(error));
        }
    }
    ~ScopedDirectoryStream() {
        if (stream_ != nullptr) (void)::closedir(stream_);
    }
    ScopedDirectoryStream(const ScopedDirectoryStream&) = delete;
    ScopedDirectoryStream& operator=(const ScopedDirectoryStream&) = delete;

    [[nodiscard]] DIR* get() const noexcept { return stream_; }
    [[nodiscard]] int descriptor() const noexcept { return ::dirfd(stream_); }

private:
    DIR* stream_ = nullptr;
};

[[nodiscard]] std::string error_text(int error_number) {
    return std::strerror(error_number);
}

[[nodiscard]] bool same_directory_identity(
    const struct stat& left,
    const struct stat& right) noexcept {
    return S_ISDIR(left.st_mode) && S_ISDIR(right.st_mode) &&
           left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] ScopedFd open_independent_root_or_throw(
    const SyncDirectoryAuthority& authority,
    const std::string& label) {
    using sync_directory_authority_detail::SyncDirectoryAuthorityAccess;
    auto shared = SyncDirectoryAuthorityAccess::
        duplicate_shared_open_description_or_throw(
            authority, label + " retained root");

    int flags = O_RDONLY;
#ifdef O_DIRECTORY
    flags |= O_DIRECTORY;
#endif
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif

    int descriptor;
    do {
        descriptor = ::openat(shared.descriptor(), ".", flags);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " independent root open failed: " + error_text(error));
    }
    ScopedFd owned(descriptor);

#ifndef O_CLOEXEC
    const int old_flags = ::fcntl(owned.get(), F_GETFD);
    if (old_flags < 0 ||
        ::fcntl(owned.get(), F_SETFD, old_flags | FD_CLOEXEC) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " independent root close-on-exec setup failed: " +
            error_text(error));
    }
#endif

    struct stat status {};
    if (::fstat(owned.get(), &status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " independent root fstat failed: " + error_text(error));
    }
    const SyncDirectoryAttestation& expected = authority.attestation();
    if (!S_ISDIR(status.st_mode) ||
        static_cast<std::uint64_t>(status.st_dev) != expected.device ||
        static_cast<std::uint64_t>(status.st_ino) != expected.inode) {
        throw std::runtime_error(
            label + " independent root does not match retained authority");
    }

    sync_posix_verify_directory_resolution_capability_or_throw(
        owned.get(), shared.resolution_capability(),
        label + " independent root resolution capability");
    const SyncPosixMountIdentity observed_mount =
        sync_posix_capture_mount_identity_or_throw(
            owned.get(), shared.resolution_capability(),
            label + " independent root mount identity");
    if (observed_mount != shared.mount_identity()) {
        throw std::runtime_error(
            label + " independent root mount identity changed");
    }
    authority.verify_or_throw(label + " retained root after independent open");
    return owned;
}

[[nodiscard]] std::string child_path(
    std::string_view parent,
    std::string_view component) {
    if (parent.empty()) return std::string(component);
    std::string path;
    path.reserve(parent.size() + 1U + component.size());
    path.append(parent);
    path.push_back('/');
    path.append(component);
    return path;
}

void require_canonical_path_or_throw(
    const std::string& path,
    const SyncReplicaFolderObservationLimits& limits,
    const std::string& label) {
    if (path.size() > limits.maximum_relative_path_bytes) {
        throw std::runtime_error(
            label + " path exceeds configured byte limit: " + path);
    }
    const SyncValidationResult validation = validate_sync_relative_path(path);
    if (!validation.ok) {
        throw std::runtime_error(
            label + " path is not portable: " + path + ": " +
            validation.reason);
    }
}

[[nodiscard]] struct stat lstat_child_or_throw(
    int parent_descriptor,
    const std::string& component,
    const std::string& canonical_path,
    const std::string& label) {
    struct stat status {};
    int result;
    do {
        result = ::fstatat(parent_descriptor, component.c_str(), &status,
                           AT_SYMLINK_NOFOLLOW);
    } while (result != 0 && errno == EINTR);
    if (result != 0) {
        const int error = errno;
        throw std::runtime_error(
            label + " no-follow status failed for " + canonical_path + ": " +
            error_text(error));
    }
    return status;
}

[[nodiscard]] bool traversal_path_less_internal(
    std::string_view left,
    std::string_view right) noexcept {
    std::size_t left_begin = 0U;
    std::size_t right_begin = 0U;
    for (;;) {
        const std::size_t left_end = left.find('/', left_begin);
        const std::size_t right_end = right.find('/', right_begin);
        const std::string_view left_component = left.substr(
            left_begin,
            left_end == std::string_view::npos
                ? std::string_view::npos
                : left_end - left_begin);
        const std::string_view right_component = right.substr(
            right_begin,
            right_end == std::string_view::npos
                ? std::string_view::npos
                : right_end - right_begin);
        const int comparison = left_component.compare(right_component);
        if (comparison != 0) return comparison < 0;

        const bool left_finished = left_end == std::string_view::npos;
        const bool right_finished = right_end == std::string_view::npos;
        if (left_finished || right_finished) {
            return left_finished && !right_finished;
        }
        left_begin = left_end + 1U;
        right_begin = right_end + 1U;
    }
}

enum class WalkDisposition : std::uint8_t {
    Continue = 1,
    StoppedAtAggregateFileByteFrontier = 2,
    StoppedAtRegularFileCountFrontier = 3,
    StoppedAtDirectoryCensusFrontier = 4,
};

struct WalkContext final {
    const SyncDirectoryAuthority& authority;
    const SyncReplicaFolderObservationLimits& limits;
    SyncPosixDirectoryResolutionCapability resolution_capability;
    SyncPosixMountIdentity root_mount;
    std::string label;
    SyncReplicaFolderTraversalSummary summary;
    SyncReplicaFolderObservation* observation = nullptr;
    const SyncReplicaFolderRegularFilePathVisitor* visitor = nullptr;
    SyncReplicaFolderTraversalSegment* segment = nullptr;
    const SyncReplicaFolderTraversalSegmentLimits* segment_limits = nullptr;
    const SyncReplicaSelectiveSyncPolicy* selective_sync_policy = nullptr;
    // Counts every synchronizable regular file classified in this invocation,
    // including the replayed prefix of a resumable walk and the first file that
    // would cross a scheduling frontier. It is deliberately separate from the
    // public delivered-file count in summary and from skipped_regular_file_count.
    std::uint64_t encountered_regular_file_count = 0U;
    // Resumable-only diagnostic accounting for selected basename strings whose
    // storage is currently live. Parent batches are explicitly released before
    // recursive descent, so this should never exceed one bounded batch.
    std::uint64_t currently_buffered_directory_component_count = 0U;
};

struct SortedComponentBatch final {
    std::vector<std::string> components;
    std::uint64_t eligible_component_count = 0U;
    bool has_more = false;
};

[[nodiscard]] WalkDisposition walk_directory_or_throw(
    WalkContext& context,
    int owned_descriptor,
    const std::string& parent_path,
    std::uint64_t depth);

void increment_entry_count_or_throw(WalkContext& context) {
    if (context.summary.visited_entry_count ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::runtime_error(
            context.label + " entry count exceeds uint64 range");
    }
    ++context.summary.visited_entry_count;
    if (context.summary.visited_entry_count >
        context.limits.maximum_entries) {
        throw std::runtime_error(
            context.label + " exceeds configured entry limit");
    }
}

void increment_regular_file_count_or_throw(
    WalkContext& context,
    const std::string& canonical_path) {
    if (context.encountered_regular_file_count ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::runtime_error(
            context.label + " regular-file count exceeds uint64 range");
    }
    ++context.encountered_regular_file_count;
    if (context.encountered_regular_file_count >
        context.limits.maximum_regular_files) {
        throw std::runtime_error(
            context.label + " exceeds configured regular-file limit: " +
            canonical_path);
    }
}

[[nodiscard]] std::uint64_t regular_file_logical_size_or_throw(
    const WalkContext& context,
    const std::string& canonical_path,
    const struct stat& initial_status) {
    if (initial_status.st_size < 0) {
        throw std::runtime_error(
            context.label + " negative file size for " + canonical_path);
    }
    return static_cast<std::uint64_t>(initial_status.st_size);
}

[[nodiscard]] std::uint64_t classified_regular_file_size_or_throw(
    WalkContext& context,
    const std::string& canonical_path,
    const struct stat& initial_status) {
    const std::uint64_t initial_size = regular_file_logical_size_or_throw(
        context, canonical_path, initial_status);
    if (initial_size > context.limits.maximum_file_bytes) {
        throw std::runtime_error(
            context.label + " file exceeds configured byte limit: " +
            canonical_path);
    }
    return initial_size;
}

[[nodiscard]] bool classified_file_fits_aggregate(
    const WalkContext& context,
    std::uint64_t initial_size) noexcept {
    return context.summary.classified_regular_file_bytes <=
               context.limits.maximum_total_file_bytes &&
           initial_size <=
               context.limits.maximum_total_file_bytes -
                   context.summary.classified_regular_file_bytes;
}

void charge_classified_regular_file_or_throw(
    WalkContext& context,
    const std::string& canonical_path,
    const struct stat& initial_status) {
    const std::uint64_t initial_size =
        classified_regular_file_size_or_throw(
            context, canonical_path, initial_status);
    if (!classified_file_fits_aggregate(context, initial_size)) {
        throw std::runtime_error(
            context.label + " exceeds configured total file-byte limit");
    }
    context.summary.classified_regular_file_bytes += initial_size;
    ++context.summary.regular_file_count;
}

void observe_regular_file_or_throw(
    WalkContext& context,
    int parent_descriptor,
    const std::string& component,
    const std::string& canonical_path,
    const struct stat& initial_status) {
    if (context.observation == nullptr) {
        throw std::logic_error(
            context.label + " observation callback has no result owner");
    }
    SyncReplicaFolderObservation& result = *context.observation;
    if (initial_status.st_size < 0) {
        throw std::runtime_error(
            context.label + " negative file size for " + canonical_path);
    }
    const std::uint64_t initial_size =
        static_cast<std::uint64_t>(initial_status.st_size);
    if (initial_size > context.limits.maximum_file_bytes) {
        throw std::runtime_error(
            context.label + " file exceeds configured byte limit: " +
            canonical_path);
    }
    if (result.total_regular_file_bytes >
            context.limits.maximum_total_file_bytes ||
        initial_size > context.limits.maximum_total_file_bytes -
                           result.total_regular_file_bytes) {
        throw std::runtime_error(
            context.label + " exceeds configured total file-byte limit");
    }

    const fs::path display_path = context.authority.path() / canonical_path;
    SyncPosixOpenedRegularFile opened =
        sync_posix_open_regular_file_component_or_throw(
            parent_descriptor, component, display_path,
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            context.resolution_capability, context.root_mount,
            context.label + " regular file");
    ScopedFd descriptor(opened.descriptor);

    const std::uint64_t remaining =
        context.limits.maximum_total_file_bytes -
        result.total_regular_file_bytes;
    const std::uint64_t read_limit =
        std::min(context.limits.maximum_file_bytes,
                 std::max<std::uint64_t>(remaining, 1U));
    auto snapshot = FrozenSyncPosixRegularFileSnapshot::
        freeze_borrowed_descriptor_or_throw(
            descriptor.get(), read_limit,
            SyncPosixDescriptorLinkPolicy::stable_named_object,
            context.label + " regular file " + canonical_path);

    const SyncPosixRegularFileSnapshotMetadata metadata = snapshot.metadata();
    if (metadata.size_bytes > remaining) {
        throw std::runtime_error(
            context.label + " exceeds configured total file-byte limit");
    }
    const std::string digest = sha256_hex(snapshot.bytes());

    // Hash the retained bytes before the final no-follow name check. The
    // namespace cannot be frozen indefinitely, but a rename/replacement that
    // races either the descriptor read or the potentially long digest pass is
    // rejected from this observation batch instead of being mislabeled as an
    // observation of the current pathname.
    SyncPosixOpenedRegularFile rebound =
        sync_posix_open_regular_file_component_or_throw(
            parent_descriptor, component, display_path,
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            context.resolution_capability, context.root_mount,
            context.label + " post-hash regular-file binding");
    ScopedFd rebound_descriptor(rebound.descriptor);
    if (!snapshot.matches_status(rebound.status)) {
        throw std::runtime_error(
            context.label + " path changed while being observed: " +
            canonical_path);
    }

    std::string bytes = std::move(snapshot).take_bytes();
    result.total_regular_file_bytes += metadata.size_bytes;
    result.regular_files.push_back(
        SyncReplicaObservedRegularFile{
            canonical_path, digest, std::move(bytes), metadata});
    ++context.summary.regular_file_count;
}

[[nodiscard]] WalkDisposition handle_regular_file_or_throw(
    WalkContext& context,
    int parent_descriptor,
    const std::string& component,
    const std::string& canonical_path,
    const struct stat& initial_status) {
    if (context.observation != nullptr) {
        observe_regular_file_or_throw(
            context, parent_descriptor, component, canonical_path,
            initial_status);
        return WalkDisposition::Continue;
    }
    if (context.visitor == nullptr) {
        throw std::logic_error(
            context.label + " traversal has no regular-file consumer");
    }
    if (context.segment == nullptr) {
        charge_classified_regular_file_or_throw(
            context, canonical_path, initial_status);
        (*context.visitor)(
            canonical_path,
            static_cast<std::uint64_t>(initial_status.st_size));
        return WalkDisposition::Continue;
    }

    SyncReplicaFolderTraversalSegment& segment = *context.segment;
    if (!segment.resume_after_path.empty() &&
        !traversal_path_less_internal(
            segment.resume_after_path, canonical_path)) {
        if (segment.skipped_regular_file_count ==
            std::numeric_limits<std::uint64_t>::max()) {
            throw std::runtime_error(
                context.label + " skipped file count exceeds uint64 range");
        }
        ++segment.skipped_regular_file_count;
        return WalkDisposition::Continue;
    }

    if (context.segment_limits == nullptr) {
        throw std::logic_error(
            context.label + " resumable traversal has no segment limits");
    }
    if (context.summary.regular_file_count >=
        context.segment_limits->maximum_regular_files) {
        return WalkDisposition::StoppedAtRegularFileCountFrontier;
    }

    const std::uint64_t initial_size =
        classified_regular_file_size_or_throw(
            context, canonical_path, initial_status);
    if (!classified_file_fits_aggregate(context, initial_size)) {
        if (context.summary.regular_file_count == 0U) {
            throw std::runtime_error(
                context.label +
                " cannot fit the next eligible file in an empty traversal "
                "segment: " + canonical_path);
        }
        return WalkDisposition::StoppedAtAggregateFileByteFrontier;
    }

    // The visitor owns all exact-file and durable effects. Advance the in-memory
    // cursor only after it returns, so a thrown callback is replayed on restart.
    (*context.visitor)(canonical_path, initial_size);
    context.summary.classified_regular_file_bytes += initial_size;
    ++context.summary.regular_file_count;
    segment.resume_after_path = canonical_path;
    return WalkDisposition::Continue;
}

void note_directory_enumeration_pass_or_throw(WalkContext& context) {
    if (context.segment == nullptr) return;
    if (context.segment->directory_enumeration_pass_count ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::runtime_error(
            context.label + " directory enumeration pass count exceeds uint64 range");
    }
    ++context.segment->directory_enumeration_pass_count;
}

class ScopedBufferedDirectoryComponentBatch final {
public:
    ScopedBufferedDirectoryComponentBatch(
        WalkContext& context,
        std::size_t count)
        : context_(&context) {
        if (context.segment == nullptr || count == 0U) {
            context_ = nullptr;
            return;
        }
        count_ = static_cast<std::uint64_t>(count);
        if (static_cast<std::size_t>(count_) != count) {
            throw std::runtime_error(
                context.label +
                " buffered directory component count exceeds uint64 range");
        }
        if (context.currently_buffered_directory_component_count != 0U) {
            throw std::logic_error(
                context.label +
                " attempted to overlap resumable directory component batches");
        }
        if (context.currently_buffered_directory_component_count >
            std::numeric_limits<std::uint64_t>::max() - count_) {
            throw std::runtime_error(
                context.label +
                " simultaneous buffered directory component count exceeds uint64 range");
        }
        context.currently_buffered_directory_component_count += count_;
        context.segment->peak_buffered_directory_component_batch_count =
            std::max(
                context.segment->peak_buffered_directory_component_batch_count,
                count_);
        context.segment->
            peak_simultaneously_buffered_directory_component_count = std::max(
                context.segment->
                    peak_simultaneously_buffered_directory_component_count,
                context.currently_buffered_directory_component_count);
    }

    ~ScopedBufferedDirectoryComponentBatch() noexcept { release(); }
    ScopedBufferedDirectoryComponentBatch(
        const ScopedBufferedDirectoryComponentBatch&) = delete;
    ScopedBufferedDirectoryComponentBatch& operator=(
        const ScopedBufferedDirectoryComponentBatch&) = delete;

    void release() noexcept {
        if (context_ == nullptr) return;
        if (context_->currently_buffered_directory_component_count < count_) {
            std::terminate();
        }
        context_->currently_buffered_directory_component_count -= count_;
        context_ = nullptr;
        count_ = 0U;
    }

private:
    WalkContext* context_ = nullptr;
    std::uint64_t count_ = 0U;
};

[[nodiscard]] SortedComponentBatch
read_next_sorted_component_batch_or_throw(
    WalkContext& context,
    ScopedDirectoryStream& directory,
    const std::string& parent_path,
    std::string_view after_component,
    std::size_t maximum_components,
    bool charge_entries) {
    if (context.segment == nullptr) {
        throw std::logic_error(
            context.label + " bounded component batch requires a resumable segment");
    }
    constexpr std::size_t kBatchLimit = static_cast<std::size_t>(
        kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch);
    if (maximum_components == 0U || maximum_components > kBatchLimit) {
        throw std::logic_error(
            context.label + " invalid bounded component batch limit");
    }
    ::rewinddir(directory.get());
    note_directory_enumeration_pass_or_throw(context);

    std::vector<std::string> selected;
    selected.reserve(maximum_components);
    std::uint64_t eligible_count = 0U;
    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(directory.get());
        if (entry == nullptr) {
            const int error = errno;
            if (error != 0) {
                throw std::runtime_error(
                    context.label + " readdir failed" +
                    (parent_path.empty() ? std::string() :
                                           " for " + parent_path) +
                    ": " + error_text(error));
            }
            break;
        }

        const std::string_view component(entry->d_name);
        if (component == "." || component == "..") continue;
        if (charge_entries) increment_entry_count_or_throw(context);
        if (!after_component.empty() && component <= after_component) continue;
        if (eligible_count == std::numeric_limits<std::uint64_t>::max()) {
            throw std::runtime_error(
                context.label + " eligible component count exceeds uint64 range");
        }
        ++eligible_count;
        if (selected.size() < maximum_components) {
            selected.emplace_back(component);
            std::push_heap(selected.begin(), selected.end());
        } else if (component < selected.front()) {
            std::pop_heap(selected.begin(), selected.end());
            selected.back().assign(component.data(), component.size());
            std::push_heap(selected.begin(), selected.end());
        }
    }

    std::sort_heap(selected.begin(), selected.end());
    SortedComponentBatch batch;
    batch.components = std::move(selected);
    batch.eligible_component_count = eligible_count;
    batch.has_more = eligible_count >
                     static_cast<std::uint64_t>(batch.components.size());
    return batch;
}

[[nodiscard]] std::vector<std::string> read_sorted_components_or_throw(
    WalkContext& context,
    ScopedDirectoryStream& directory,
    const std::string& parent_path) {
    std::vector<std::string> components;
    for (;;) {
        errno = 0;
        dirent* entry = ::readdir(directory.get());
        if (entry == nullptr) {
            const int error = errno;
            if (error != 0) {
                throw std::runtime_error(
                    context.label + " readdir failed" +
                    (parent_path.empty() ? std::string() :
                                           " for " + parent_path) +
                    ": " + error_text(error));
            }
            break;
        }

        const std::string_view component(entry->d_name);
        if (component == "." || component == "..") continue;
        increment_entry_count_or_throw(context);
        components.emplace_back(component);
    }
    std::sort(components.begin(), components.end());
    return components;
}

struct PendingDirectoryDescent final {
    bool present = false;
    std::string component;
    std::string canonical_path;
    ScopedFd descriptor;
    struct stat opened_status {};
};

struct ComponentBatchWalkResult final {
    WalkDisposition disposition = WalkDisposition::Continue;
    std::size_t next_component_index = 0U;
    PendingDirectoryDescent directory;
};

[[nodiscard]] ComponentBatchWalkResult
walk_component_batch_until_directory_or_throw(
    WalkContext& context,
    int parent_descriptor,
    const std::string& parent_path,
    std::uint64_t depth,
    const std::vector<std::string>& components,
    std::size_t begin_index) {
    if (begin_index > components.size()) {
        throw std::logic_error(
            context.label + " component batch resume index is out of range");
    }

    ComponentBatchWalkResult result;
    result.next_component_index = begin_index;
    for (std::size_t index = begin_index; index < components.size(); ++index) {
        const std::string& component = components[index];
        result.next_component_index = index + 1U;
        const std::string canonical_path = child_path(parent_path, component);
        const struct stat initial_status = lstat_child_or_throw(
            parent_descriptor, component, canonical_path,
            context.label + " classification");

        // Exact private publication/displacement residues are implementation
        // state, not user files. They still count against maximum_entries, but
        // they must never be published into replica history after a crash.
        if (sync_atomic_file_publication_temp_basename_is_exact(component)) {
            ++context.summary.ignored_internal_artifact_count;
            continue;
        }

        if (S_ISLNK(initial_status.st_mode)) {
            ++context.summary.ignored_symbolic_link_count;
            continue;
        }
        if (!S_ISDIR(initial_status.st_mode) &&
            !S_ISREG(initial_status.st_mode)) {
            ++context.summary.ignored_special_file_count;
            continue;
        }

        require_canonical_path_or_throw(
            canonical_path, context.limits, context.label);
        if (S_ISREG(initial_status.st_mode)) {
            if (context.selective_sync_policy != nullptr &&
                !sync_replica_selective_sync_path_is_materialized(
                    *context.selective_sync_policy, canonical_path)) {
                if (context.summary.metadata_only_regular_file_count ==
                    std::numeric_limits<std::uint64_t>::max()) {
                    throw std::runtime_error(
                        context.label +
                        " metadata-only regular-file count exceeds uint64 range");
                }
                ++context.summary.metadata_only_regular_file_count;
                const std::uint64_t logical_size =
                    regular_file_logical_size_or_throw(
                        context, canonical_path, initial_status);
                if (logical_size >
                    std::numeric_limits<std::uint64_t>::max() -
                        context.summary
                            .metadata_only_regular_file_logical_bytes) {
                    throw std::runtime_error(
                        context.label +
                        " metadata-only regular-file logical bytes exceed "
                        "uint64 range");
                }
                context.summary.metadata_only_regular_file_logical_bytes +=
                    logical_size;
                continue;
            }
            increment_regular_file_count_or_throw(context, canonical_path);
            result.disposition = handle_regular_file_or_throw(
                context, parent_descriptor, component, canonical_path,
                initial_status);
            if (result.disposition != WalkDisposition::Continue) return result;
            continue;
        }

        if (context.selective_sync_policy != nullptr &&
            !sync_replica_selective_sync_directory_may_contain_materialized_path(
                *context.selective_sync_policy, canonical_path)) {
            if (context.summary.metadata_only_pruned_directory_count ==
                std::numeric_limits<std::uint64_t>::max()) {
                throw std::runtime_error(
                    context.label +
                    " metadata-only pruned-directory count exceeds uint64 range");
            }
            ++context.summary.metadata_only_pruned_directory_count;
            continue;
        }

        if (depth >= context.limits.maximum_directory_depth) {
            throw std::runtime_error(
                context.label + " exceeds configured directory depth at " +
                canonical_path);
        }

        // Copy the stable component/path state before opening the child. If an
        // allocation fails, no descriptor has been acquired. Once opened, the
        // aggregate contains no throwing members, so ownership can be handed to
        // the caller without leaking the descriptor.
        result.directory.component = component;
        result.directory.canonical_path = canonical_path;
        const fs::path display_path = context.authority.path() / canonical_path;
        SyncPosixOpenedDirectory opened =
            sync_posix_open_directory_component_or_throw(
                parent_descriptor, component, display_path,
                SyncPosixDirectoryComponentRole::RootedDescendant,
                SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
                context.resolution_capability, context.root_mount,
                context.label + " directory");
        result.directory.opened_status = opened.status;
        result.directory.descriptor = ScopedFd(opened.descriptor);
        result.directory.present = true;
        ++context.summary.visited_directory_count;
        return result;
    }
    return result;
}

[[nodiscard]] WalkDisposition walk_pending_directory_or_throw(
    WalkContext& context,
    int parent_descriptor,
    std::uint64_t depth,
    PendingDirectoryDescent& pending) {
    if (!pending.present || pending.descriptor.get() < 0) {
        throw std::logic_error(
            context.label + " pending directory descent is incomplete");
    }

    const struct stat opened_status = pending.opened_status;
    const fs::path display_path =
        context.authority.path() / pending.canonical_path;
    const WalkDisposition child_disposition = walk_directory_or_throw(
        context, pending.descriptor.release(), pending.canonical_path,
        depth + 1U);

    SyncPosixOpenedDirectory rebound =
        sync_posix_open_directory_component_or_throw(
            parent_descriptor, pending.component, display_path,
            SyncPosixDirectoryComponentRole::RootedDescendant,
            SyncPosixDirectoryMountPolicy::RequireRetainedRootMount,
            context.resolution_capability, context.root_mount,
            context.label + " post-walk directory binding");
    ScopedFd rebound_descriptor(rebound.descriptor);
    if (!same_directory_identity(opened_status, rebound.status)) {
        throw std::runtime_error(
            context.label +
            " directory path changed while being observed: " +
            pending.canonical_path);
    }
    return child_disposition;
}

[[nodiscard]] WalkDisposition walk_complete_component_batch_or_throw(
    WalkContext& context,
    int parent_descriptor,
    const std::string& parent_path,
    std::uint64_t depth,
    const std::vector<std::string>& components) {
    std::size_t next_component_index = 0U;
    while (next_component_index < components.size()) {
        ComponentBatchWalkResult result =
            walk_component_batch_until_directory_or_throw(
                context, parent_descriptor, parent_path, depth, components,
                next_component_index);
        next_component_index = result.next_component_index;
        if (result.disposition != WalkDisposition::Continue) {
            return result.disposition;
        }
        if (!result.directory.present) continue;
        const WalkDisposition child_disposition =
            walk_pending_directory_or_throw(
                context, parent_descriptor, depth, result.directory);
        if (child_disposition != WalkDisposition::Continue) {
            return child_disposition;
        }
    }
    return WalkDisposition::Continue;
}

[[nodiscard]] WalkDisposition walk_directory_or_throw(
    WalkContext& context,
    int owned_descriptor,
    const std::string& parent_path,
    std::uint64_t depth) {
    ScopedDirectoryStream directory(
        owned_descriptor,
        context.label +
            (parent_path.empty() ? " root directory" :
                                   " directory " + parent_path));
    const int parent_descriptor = directory.descriptor();
    if (parent_descriptor < 0) {
        throw std::runtime_error(
            context.label + " directory descriptor became unavailable");
    }

    if (context.segment == nullptr) {
        const std::vector<std::string> components =
            read_sorted_components_or_throw(context, directory, parent_path);
        return walk_complete_component_batch_or_throw(
            context, parent_descriptor, parent_path, depth, components);
    }

    constexpr std::uint64_t kBatchLimit =
        kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch;
    std::string after_component;
    std::uint64_t remaining_first_census_components = 0U;
    bool first_census = true;
    for (;;) {
        const std::uint64_t requested_components = first_census
            ? kBatchLimit
            : std::min(kBatchLimit, remaining_first_census_components);
        if (requested_components == 0U) return WalkDisposition::Continue;
        // This check precedes the selector's vector reservation. The lifetime
        // fence therefore bounds actual selected-name storage rather than only
        // diagnosing overlap after a second batch has already been allocated.
        if (context.currently_buffered_directory_component_count != 0U) {
            throw std::logic_error(
                context.label +
                " retained a resumable directory component batch before selection");
        }
        SortedComponentBatch batch =
            read_next_sorted_component_batch_or_throw(
                context, directory, parent_path, after_component,
                static_cast<std::size_t>(requested_components),
                first_census);
        if (first_census) {
            remaining_first_census_components =
                batch.eligible_component_count;
            first_census = false;
        } else if (batch.eligible_component_count !=
                   remaining_first_census_components) {
            // The first charged census is the finite membership frontier for
            // this directory invocation. Growth, shrinkage, or a rename across
            // the processed component boundary changes the exact suffix
            // cardinality. Do not process that inconsistent rescan and, above
            // all, do not turn it into end-of-namespace or deletion authority.
            return WalkDisposition::StoppedAtDirectoryCensusFrontier;
        }
        if (batch.components.empty()) return WalkDisposition::Continue;
        ScopedBufferedDirectoryComponentBatch buffered_batch(
            context, batch.components.size());
        ComponentBatchWalkResult result =
            walk_component_batch_until_directory_or_throw(
                context, parent_descriptor, parent_path, depth,
                batch.components, 0U);
        const std::uint64_t consumed_components =
            static_cast<std::uint64_t>(result.next_component_index);
        if (static_cast<std::size_t>(consumed_components) !=
                result.next_component_index ||
            consumed_components > remaining_first_census_components) {
            throw std::logic_error(
                context.label + " component batch exceeded first census");
        }
        if (result.disposition != WalkDisposition::Continue) {
            return result.disposition;
        }

        remaining_first_census_components -= consumed_components;
        const bool selected_batch_has_more = batch.has_more;
        if (result.directory.present) {
            // The pending directory owns independent component/path strings and
            // an opened descriptor. Release every selected basename (including
            // vector capacity) before recursive descent. On return, resume this
            // same open parent directory strictly after the processed component.
            std::vector<std::string>().swap(batch.components);
            buffered_batch.release();
            const WalkDisposition child_disposition =
                walk_pending_directory_or_throw(
                    context, parent_descriptor, depth, result.directory);
            if (child_disposition != WalkDisposition::Continue) {
                return child_disposition;
            }
            if (remaining_first_census_components == 0U) {
                return selected_batch_has_more
                    ? WalkDisposition::StoppedAtDirectoryCensusFrontier
                    : WalkDisposition::Continue;
            }
            if (context.segment_limits == nullptr) {
                throw std::logic_error(
                    context.label +
                    " resumable traversal has no segment limits");
            }
            if (context.summary.regular_file_count >=
                context.segment_limits->maximum_regular_files) {
                return WalkDisposition::StoppedAtRegularFileCountFrontier;
            }
            after_component = std::move(result.directory.component);
            continue;
        }

        if (remaining_first_census_components == 0U) {
            // Names observed beyond the first census are bounded work, not
            // end-of-namespace authority. They may also have displaced an
            // original census member from the final selected batch. Preserve
            // the last delivered regular-file cursor and require another
            // segment instead of allowing deletion inference from a moving
            // namespace.
            return selected_batch_has_more
                ? WalkDisposition::StoppedAtDirectoryCensusFrontier
                : WalkDisposition::Continue;
        }
        if (!selected_batch_has_more) return WalkDisposition::Continue;

        if (context.segment_limits == nullptr) {
            throw std::logic_error(
                context.label + " resumable traversal has no segment limits");
        }
        if (context.summary.regular_file_count >=
            context.segment_limits->maximum_regular_files) {
            return WalkDisposition::StoppedAtRegularFileCountFrontier;
        }
        after_component = std::move(batch.components.back());
    }
}

}  // namespace

bool sync_replica_folder_traversal_path_less(
    std::string_view left,
    std::string_view right) noexcept {
    return traversal_path_less_internal(left, right);
}

void validate_sync_replica_folder_observation_limits_or_throw(
    const SyncReplicaFolderObservationLimits& limits,
    std::string label) {
    if (label.empty()) label = "sync replica folder observation limits";
    if (limits.maximum_entries == 0U) {
        throw std::invalid_argument(
            label + " maximum entries must be positive");
    }
    if (limits.maximum_entries >
        kSyncReplicaFolderObservationMaximumEntries) {
        throw std::invalid_argument(
            label + " maximum entries must be at most " +
            std::to_string(
                kSyncReplicaFolderObservationMaximumEntries));
    }
    if (limits.maximum_regular_files == 0U) {
        throw std::invalid_argument(
            label + " maximum regular files must be positive");
    }
    if (limits.maximum_regular_files >
        kSyncReplicaFolderObservationMaximumRegularFiles) {
        throw std::invalid_argument(
            label + " maximum regular files must be at most " +
            std::to_string(
                kSyncReplicaFolderObservationMaximumRegularFiles));
    }
    if (limits.maximum_file_bytes == 0U) {
        throw std::invalid_argument(
            label + " maximum file bytes must be positive");
    }
    if (limits.maximum_total_file_bytes == 0U) {
        throw std::invalid_argument(
            label + " maximum total file bytes must be positive");
    }
    if (limits.maximum_relative_path_bytes == 0U ||
        limits.maximum_relative_path_bytes > 4096U) {
        throw std::invalid_argument(
            label + " maximum relative path bytes must be in [1,4096]");
    }
    if (limits.maximum_directory_depth >
        kSyncReplicaFolderObservationMaximumDirectoryDepth) {
        throw std::invalid_argument(
            label + " maximum directory depth must be at most " +
            std::to_string(
                kSyncReplicaFolderObservationMaximumDirectoryDepth));
    }
}

void validate_sync_replica_folder_traversal_segment_limits_or_throw(
    const SyncReplicaFolderTraversalSegmentLimits& limits,
    std::string label) {
    if (label.empty()) {
        label = "sync replica folder traversal segment limits";
    }
    if (limits.maximum_regular_files == 0U ||
        limits.maximum_regular_files >
            kSyncReplicaFolderObservationMaximumRegularFiles) {
        throw std::invalid_argument(
            label + " maximum regular files must be in [1," +
            std::to_string(
                kSyncReplicaFolderObservationMaximumRegularFiles) +
            "]");
    }
}

namespace {

[[nodiscard]] SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_impl_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaSelectiveSyncPolicy* selective_sync_policy,
    const SyncReplicaFolderObservationLimits& limits,
    const SyncReplicaFolderTraversalSegmentLimits& segment_limits,
    std::string label) {
    if (label.empty()) {
        label = "sync replica folder resumable path traversal";
    }
    if (!visitor) {
        throw std::invalid_argument(
            label + " regular-file visitor must not be empty");
    }
    validate_sync_replica_folder_observation_limits_or_throw(limits, label);
    validate_sync_replica_folder_traversal_segment_limits_or_throw(
        segment_limits, label + " segment limits");
    if (!resume_after_path.empty()) {
        require_canonical_path_or_throw(resume_after_path, limits, label);
    }

    SyncReplicaFolderTraversalSegment segment;
    segment.resume_after_path = std::move(resume_after_path);
    WalkContext context{
        root_authority,
        limits,
        root_authority.resolution_capability(),
        {},
        std::move(label),
        {},
        nullptr,
        &visitor,
        &segment,
        &segment_limits,
        selective_sync_policy};
    if (selective_sync_policy != nullptr) {
        validate_sync_replica_selective_sync_policy_or_throw(
            *selective_sync_policy, context.label + " selective-sync policy");
    }
    ScopedFd root = open_independent_root_or_throw(
        root_authority, context.label + " mount capture");
    context.root_mount = sync_posix_capture_mount_identity_or_throw(
        root.get(), context.resolution_capability,
        context.label + " scan root mount identity");
    root_authority.verify_or_throw(context.label + " root before traversal");
    const WalkDisposition disposition =
        walk_directory_or_throw(context, root.release(), {}, 0U);
    if (context.currently_buffered_directory_component_count != 0U) {
        throw std::logic_error(
            context.label +
            " retained buffered directory components after traversal");
    }
    root_authority.verify_or_throw(context.label + " root after traversal");
    switch (disposition) {
        case WalkDisposition::Continue:
            segment.completed = true;
            segment.stop_reason =
                SyncReplicaFolderTraversalStopReason::EndOfNamespace;
            break;
        case WalkDisposition::StoppedAtAggregateFileByteFrontier:
            segment.completed = false;
            segment.stop_reason = SyncReplicaFolderTraversalStopReason::
                AggregateFileByteFrontier;
            break;
        case WalkDisposition::StoppedAtRegularFileCountFrontier:
            segment.completed = false;
            segment.stop_reason = SyncReplicaFolderTraversalStopReason::
                RegularFileCountFrontier;
            break;
        case WalkDisposition::StoppedAtDirectoryCensusFrontier:
            segment.completed = false;
            segment.stop_reason = SyncReplicaFolderTraversalStopReason::
                DirectoryCensusFrontier;
            break;
    }
    segment.traversal = context.summary;
    return segment;
}

}  // namespace

SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits,
    const SyncReplicaFolderTraversalSegmentLimits& segment_limits,
    std::string label) {
    return visit_sync_replica_folder_regular_file_paths_resumable_impl_or_throw(
        root_authority, std::move(resume_after_path), visitor, nullptr, limits,
        segment_limits, std::move(label));
}

SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaSelectiveSyncPolicy& selective_sync_policy,
    const SyncReplicaFolderObservationLimits& limits,
    const SyncReplicaFolderTraversalSegmentLimits& segment_limits,
    std::string label) {
    return visit_sync_replica_folder_regular_file_paths_resumable_impl_or_throw(
        root_authority, std::move(resume_after_path), visitor,
        &selective_sync_policy, limits, segment_limits, std::move(label));
}

SyncReplicaFolderTraversalSegment
visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
    const SyncDirectoryAuthority& root_authority,
    std::string resume_after_path,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits,
    std::string label) {
    SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = limits.maximum_regular_files;
    return visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
        root_authority, std::move(resume_after_path), visitor, limits,
        segment_limits, std::move(label));
}

SyncReplicaFolderTraversalSummary
visit_sync_replica_folder_regular_file_paths_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFolderRegularFilePathVisitor& visitor,
    const SyncReplicaFolderObservationLimits& limits,
    std::string label) {
    if (label.empty()) label = "sync replica folder path traversal";
    if (!visitor) {
        throw std::invalid_argument(
            label + " regular-file visitor must not be empty");
    }
    validate_sync_replica_folder_observation_limits_or_throw(
        limits, label);

    WalkContext context{
        root_authority,
        limits,
        root_authority.resolution_capability(),
        {},
        std::move(label),
        {},
        nullptr,
        &visitor,
        nullptr,
        nullptr,
        nullptr};
    ScopedFd root = open_independent_root_or_throw(
        root_authority, context.label + " mount capture");
    context.root_mount = sync_posix_capture_mount_identity_or_throw(
        root.get(), context.resolution_capability,
        context.label + " scan root mount identity");
    root_authority.verify_or_throw(context.label + " root before traversal");
    const WalkDisposition disposition =
        walk_directory_or_throw(context, root.release(), {}, 0U);
    if (disposition != WalkDisposition::Continue) {
        throw std::logic_error(
            context.label + " full traversal stopped without an exception");
    }
    root_authority.verify_or_throw(context.label + " root after traversal");
    return context.summary;
}

SyncReplicaFolderObservation observe_sync_replica_folder_or_throw(
    const SyncDirectoryAuthority& root_authority,
    const SyncReplicaFolderObservationLimits& limits,
    std::string label) {
    if (label.empty()) label = "sync replica folder observation";
    validate_sync_replica_folder_observation_limits_or_throw(
        limits, label);

    SyncReplicaFolderObservation result;
    WalkContext context{
        root_authority,
        limits,
        root_authority.resolution_capability(),
        {},
        std::move(label),
        {},
        &result,
        nullptr,
        nullptr,
        nullptr,
        nullptr};
    ScopedFd root = open_independent_root_or_throw(
        root_authority, context.label + " mount capture");
    context.root_mount = sync_posix_capture_mount_identity_or_throw(
        root.get(), context.resolution_capability,
        context.label + " scan root mount identity");
    root_authority.verify_or_throw(context.label + " root before observation");
    const WalkDisposition disposition =
        walk_directory_or_throw(context, root.release(), {}, 0U);
    if (disposition != WalkDisposition::Continue) {
        throw std::logic_error(
            context.label + " full observation stopped without an exception");
    }
    root_authority.verify_or_throw(context.label + " root after observation");

    result.visited_entry_count = context.summary.visited_entry_count;
    result.visited_directory_count = context.summary.visited_directory_count;
    result.ignored_symbolic_link_count =
        context.summary.ignored_symbolic_link_count;
    result.ignored_special_file_count =
        context.summary.ignored_special_file_count;
    result.ignored_internal_artifact_count =
        context.summary.ignored_internal_artifact_count;

    std::sort(
        result.regular_files.begin(), result.regular_files.end(),
        [](const SyncReplicaObservedRegularFile& left,
           const SyncReplicaObservedRegularFile& right) {
            return left.canonical_path < right.canonical_path;
        });
    for (std::size_t index = 1U;
         index < result.regular_files.size(); ++index) {
        if (result.regular_files[index - 1U].canonical_path ==
            result.regular_files[index].canonical_path) {
            throw std::logic_error(
                context.label + " produced a duplicate canonical path");
        }
    }
    return result;
}

}  // namespace anonsync

#endif
