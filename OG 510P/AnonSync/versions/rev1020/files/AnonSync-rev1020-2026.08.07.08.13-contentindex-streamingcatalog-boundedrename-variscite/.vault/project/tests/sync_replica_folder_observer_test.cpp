#include "sync_replica_folder_observer.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

class TestState final {
public:
    void require(bool condition, std::string_view message) {
        if (!condition) {
            ++failed;
            std::cerr << "FAIL: " << message << "\n";
            return;
        }
        ++passed;
    }

    int passed = 0;
    int failed = 0;
};

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        root_ = fs::temp_directory_path() /
                ("anonsync-folder-observer-" +
                 std::to_string(static_cast<long long>(::getpid())) + "-" +
                 std::to_string(static_cast<long long>(tick)));
        fs::create_directories(root_);
        if (::chmod(root_.c_str(), 0700) != 0) {
            throw std::runtime_error("could not protect temporary scan root");
        }
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(root_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return root_; }

private:
    fs::path root_;
};

void write_bytes(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("could not open folder-observer fixture");
    }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) {
        throw std::runtime_error("could not write folder-observer fixture");
    }
}

void create_sparse_file(const fs::path& path, std::uint64_t logical_bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error(
            "could not create sparse folder-observer fixture");
    }
    output.close();
    if (!output) {
        throw std::runtime_error(
            "could not close sparse folder-observer fixture");
    }
    std::error_code error;
    fs::resize_file(path, logical_bytes, error);
    if (error) {
        throw std::runtime_error(
            "could not size sparse folder-observer fixture: " +
            error.message());
    }
}

template <typename Function>
[[nodiscard]] bool throws_with(Function&& function,
                               std::string_view fragment) {
    try {
        function();
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(fragment) !=
               std::string_view::npos;
    }
}

[[nodiscard]] const anonsync::SyncReplicaObservedRegularFile* find_file(
    const anonsync::SyncReplicaFolderObservation& observation,
    std::string_view path) {
    for (const auto& file : observation.regular_files) {
        if (file.canonical_path == path) return &file;
    }
    throw std::runtime_error(
        "observed file is absent: " + std::string(path));
}

void require_metadata_matches_path(
    TestState& test,
    const anonsync::SyncReplicaObservedRegularFile& observed,
    const fs::path& path) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        throw std::runtime_error("could not inspect observed fixture metadata");
    }
    test.require(observed.metadata.device ==
                     static_cast<std::uint64_t>(status.st_dev) &&
                     observed.metadata.inode ==
                         static_cast<std::uint64_t>(status.st_ino),
                 "observation retains exact descriptor identity");
    test.require(observed.metadata.size_bytes == observed.content_bytes.size() &&
                     observed.metadata.size_bytes ==
                         static_cast<std::uint64_t>(status.st_size),
                 "observation binds descriptor size to retained bytes");
    test.require(observed.metadata.link_count ==
                     static_cast<std::uint64_t>(status.st_nlink),
                 "observation retains stable link topology");
    test.require(observed.metadata.owner_user_id ==
                     static_cast<std::uint64_t>(status.st_uid) &&
                     observed.metadata.owner_group_id ==
                         static_cast<std::uint64_t>(status.st_gid),
                 "observation retains file ownership metadata");
    test.require(observed.metadata.mode ==
                     static_cast<std::uint32_t>(status.st_mode),
                 "observation retains the exact regular-file mode");
}

void test_bounded_descriptor_rooted_scan(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    fs::create_directory(root / "nested");
    write_bytes(root / "z-last.txt", "last");
    write_bytes(root / "a-first.txt", "alpha");
    const std::string binary("b\0eta", 5);
    write_bytes(root / "nested" / "binary.dat", binary);

    std::error_code symlink_error;
    fs::create_symlink("a-first.txt", root / "ignored-link", symlink_error);
    if (symlink_error) {
        throw std::runtime_error(
            "symbolic-link fixture unavailable: " + symlink_error.message());
    }
    if (::mkfifo((root / "ignored-fifo").c_str(), 0600) != 0) {
        throw std::runtime_error("FIFO fixture unavailable");
    }

    bool hard_link_created = false;
    std::error_code hard_link_error;
    fs::create_hard_link(root / "a-first.txt", root / "a-alias.txt",
                         hard_link_error);
    hard_link_created = !hard_link_error;

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-observer test root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 32;
    limits.maximum_file_bytes = 64;
    limits.maximum_total_file_bytes = 256;
    limits.maximum_directory_depth = 4;

    const auto first = anonsync::observe_sync_replica_folder_or_throw(
        authority, limits, "folder-observer first scan");
    const auto second = anonsync::observe_sync_replica_folder_or_throw(
        authority, limits, "folder-observer repeated scan");
    test.require(first == second,
                 "repeated scans use an independent directory cursor and remain deterministic");

    const std::vector<std::string> expected = hard_link_created
        ? std::vector<std::string>{"a-alias.txt", "a-first.txt",
                                   "nested/binary.dat", "z-last.txt"}
        : std::vector<std::string>{"a-first.txt", "nested/binary.dat",
                                   "z-last.txt"};
    std::vector<std::string> observed_paths;
    for (const auto& file : first.regular_files) {
        observed_paths.push_back(file.canonical_path);
    }
    test.require(observed_paths == expected,
                 "regular files are returned in canonical path order");
    test.require(first.visited_directory_count == 1,
                 "nested directory traversal is counted exactly once");
    test.require(first.ignored_symbolic_link_count == 1,
                 "symbolic links are counted without being followed");
    test.require(first.ignored_special_file_count == 1,
                 "special files are counted without blocking or publication");
    test.require(first.visited_entry_count ==
                     static_cast<std::uint64_t>(expected.size() + 3U),
                 "every non-dot directory entry spends the scan entry budget");

    const auto& alpha = *find_file(first, "a-first.txt");
    const auto& nested = *find_file(first, "nested/binary.dat");
    test.require(alpha.content_bytes == "alpha" &&
                     alpha.content_sha256 == anonsync::sha256_hex("alpha"),
                 "folder observation retains and hashes the same alpha bytes");
    test.require(nested.content_bytes == binary &&
                     nested.content_sha256 == anonsync::sha256_hex(binary),
                 "folder observation is binary-safe");
    require_metadata_matches_path(test, alpha, root / "a-first.txt");
    require_metadata_matches_path(test, nested, root / "nested" / "binary.dat");

    std::uint64_t expected_bytes = 5U + 5U + 4U;
    if (hard_link_created) expected_bytes += 5U;
    test.require(first.total_regular_file_bytes == expected_bytes,
                 "total retained bytes count every synchronized pathname");
    if (hard_link_created) {
        const auto& alias = *find_file(first, "a-alias.txt");
        test.require(alias.metadata.device == alpha.metadata.device &&
                         alias.metadata.inode == alpha.metadata.inode &&
                         alias.content_sha256 == alpha.content_sha256,
                     "hard-linked names retain shared identity without collapsing paths");
    }
    authority.verify_or_throw("folder-observer authority after repeated scans");
}


void test_internal_publication_artifacts_are_reserved(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const std::string exact_name =
        ".anonsync-publish-v1-0000000000000001-0000000000000002-"
        "0000000000000003.tmp";
    const std::string near_name =
        ".anonsync-publish-v1-0000000000000001-0000000000000002-"
        "0000000000000003.tmp-visible";
    write_bytes(root / exact_name, "private crash residue");
    write_bytes(root / near_name, "ordinary near-match");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-observer internal-artifact root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 8U;
    limits.maximum_file_bytes = 64U;
    limits.maximum_total_file_bytes = 128U;

    const auto observation =
        anonsync::observe_sync_replica_folder_or_throw(
            authority, limits, "folder-observer internal-artifact scan");
    test.require(
        observation.regular_files.size() == 1U &&
            observation.regular_files.front().canonical_path == near_name &&
            observation.ignored_internal_artifact_count == 1U &&
            observation.visited_entry_count == 2U,
        "exact private publication artifacts are bounded and hidden while near-matches remain user files");

    std::vector<std::string> paths;
    const auto traversal =
        anonsync::visit_sync_replica_folder_regular_file_paths_or_throw(
            authority,
            [&](const std::string& path, std::uint64_t) {
                paths.push_back(path);
            },
            limits, "folder-observer internal-artifact traversal");
    test.require(
        paths == std::vector<std::string>{near_name} &&
            traversal.regular_file_count == 1U &&
            traversal.ignored_internal_artifact_count == 1U &&
            traversal.visited_entry_count == 2U,
        "streaming traversal cannot publish exact private recovery names");
}

void test_streaming_path_visitor(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    fs::create_directory(root / "nested");
    write_bytes(root / "z-last.txt", "last");
    write_bytes(root / "a-first.txt", "alpha");
    write_bytes(root / "nested" / "middle.txt", "middle");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-visitor test root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 16U;
    limits.maximum_file_bytes = 16U;
    limits.maximum_total_file_bytes = 32U;
    limits.maximum_directory_depth = 4U;

    std::vector<std::string> paths;
    std::vector<std::uint64_t> classified_sizes;
    const auto summary =
        anonsync::visit_sync_replica_folder_regular_file_paths_or_throw(
            authority,
            [&](const std::string& path, std::uint64_t size_bytes) {
                paths.push_back(path);
                classified_sizes.push_back(size_bytes);
            },
            limits, "folder-visitor first pass");
    test.require(
        paths == std::vector<std::string>{
                     "a-first.txt", "nested/middle.txt", "z-last.txt"},
        "streaming traversal processes sorted names without retaining a whole-tree payload batch");
    test.require(
        classified_sizes == std::vector<std::uint64_t>{5U, 6U, 4U},
        "streaming traversal exposes bounded classification sizes");
    test.require(
        summary.visited_entry_count == 4U &&
            summary.visited_directory_count == 1U &&
            summary.regular_file_count == 3U &&
            summary.classified_regular_file_bytes == 15U,
        "streaming traversal reports its exact namespace classification work");

    std::vector<std::string> repeated_paths;
    const auto repeated =
        anonsync::visit_sync_replica_folder_regular_file_paths_or_throw(
            authority,
            [&](const std::string& path, std::uint64_t) {
                repeated_paths.push_back(path);
            },
            limits, "folder-visitor repeated pass");
    test.require(
        repeated == summary && repeated_paths == paths,
        "stable namespaces produce stable streaming callback order and counts");
    authority.verify_or_throw("folder-visitor authority after repeated passes");
}

void test_resumable_component_order_and_progress(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    fs::create_directory(root / "a");
    write_bytes(root / "a" / "one.bin", "1111");
    write_bytes(root / "a" / "two.bin", "2222");
    write_bytes(root / "a.txt", "3333");
    write_bytes(root / "z.bin", "4444");

    test.require(
        anonsync::sync_replica_folder_traversal_path_less(
            "a/two.bin", "a.txt") &&
            !anonsync::sync_replica_folder_traversal_path_less(
                "a.txt", "a/two.bin"),
        "component-wise preorder keeps a directory subtree before its next sibling");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-resumable test root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 16U;
    limits.maximum_file_bytes = 4U;
    limits.maximum_total_file_bytes = 4U;
    limits.maximum_directory_depth = 4U;

    std::string cursor;
    std::vector<std::string> delivered;
    std::vector<std::string> all_delivered;
    std::vector<anonsync::SyncReplicaFolderTraversalSegment> segments;
    for (std::size_t invocation = 0U; invocation < 4U; ++invocation) {
        delivered.clear();
        auto segment =
            anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                authority, cursor,
                [&](const std::string& path, std::uint64_t size_bytes) {
                    delivered.push_back(path);
                    test.require(
                        size_bytes == 4U,
                        "resumable traversal preserves classification size");
                },
                limits, "folder-resumable segment");
        test.require(
            delivered.size() == 1U &&
                segment.traversal.regular_file_count == 1U &&
                segment.traversal.classified_regular_file_bytes == 4U,
            "each bounded segment makes exactly one eligible-file step");
        all_delivered.insert(
            all_delivered.end(), delivered.begin(), delivered.end());
        cursor = segment.resume_after_path;
        segments.push_back(std::move(segment));
    }

    test.require(
        all_delivered == std::vector<std::string>{
            "a/one.bin", "a/two.bin", "a.txt", "z.bin"},
        "persisted resumable cursors eventually reach the deterministic suffix without repeats");
    test.require(
        !segments[0].completed && !segments[1].completed &&
            !segments[2].completed && segments[3].completed &&
            segments[0].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    AggregateFileByteFrontier &&
            segments[1].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    AggregateFileByteFrontier &&
            segments[2].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    AggregateFileByteFrontier &&
            segments[3].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    EndOfNamespace,
        "resumable traversal distinguishes aggregate-byte continuation from namespace completion");
    test.require(
        segments[0].resume_after_path == "a/one.bin" &&
            segments[1].resume_after_path == "a/two.bin" &&
            segments[2].resume_after_path == "a.txt" &&
            segments[3].resume_after_path == "z.bin",
        "each segment returns the last successfully delivered durable cursor");
    test.require(
        segments[0].skipped_regular_file_count == 0U &&
            segments[1].skipped_regular_file_count == 1U &&
            segments[2].skipped_regular_file_count == 2U &&
            segments[3].skipped_regular_file_count == 3U,
        "resumed walks skip but do not recharge the deterministic prefix");

    anonsync::SyncReplicaFolderObservationLimits impossible = limits;
    impossible.maximum_file_bytes = 4U;
    impossible.maximum_total_file_bytes = 3U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                    authority, {},
                    [](const std::string&, std::uint64_t) {}, impossible,
                    "folder-resumable impossible segment");
            },
            "cannot fit the next eligible file"),
        "a resumable walk rejects an empty segment that cannot make one-file progress");
    authority.verify_or_throw(
        "folder-resumable authority after continuation segments");
}

void test_resumable_count_frontier_and_rooted_reproof(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    for (const std::string_view path :
         {"a.txt", "b.txt", "c.txt", "d.txt", "e.txt"}) {
        write_bytes(root / std::string(path), {});
    }

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-count-frontier test root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 16U;
    limits.maximum_file_bytes = 1U;
    limits.maximum_total_file_bytes = 1U;
    anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = 2U;

    std::string cursor;
    std::vector<std::string> all_delivered;
    const std::vector<std::size_t> expected_counts{2U, 2U, 1U};
    const std::vector<std::uint64_t> expected_skipped{0U, 2U, 4U};
    const std::vector<std::string> expected_cursors{
        "b.txt", "d.txt", "e.txt"};
    for (std::size_t invocation = 0U;
         invocation < expected_counts.size(); ++invocation) {
        std::vector<std::string> delivered;
        const auto segment =
            anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                authority, cursor,
                [&](const std::string& path, std::uint64_t size_bytes) {
                    test.require(
                        size_bytes == 0U,
                        "count-bounded traversal retains zero-byte classification");
                    delivered.push_back(path);
                },
                limits, segment_limits,
                "folder-count-frontier segment");
        test.require(
            delivered.size() == expected_counts[invocation] &&
                segment.traversal.regular_file_count ==
                    expected_counts[invocation] &&
                segment.traversal.classified_regular_file_bytes == 0U,
            "delivered-file frontier bounds a zero-byte namespace segment");
        test.require(
            segment.completed ==
                    (invocation + 1U == expected_counts.size()) &&
                segment.stop_reason ==
                    (invocation + 1U == expected_counts.size()
                         ? anonsync::SyncReplicaFolderTraversalStopReason::
                               EndOfNamespace
                         : anonsync::SyncReplicaFolderTraversalStopReason::
                               RegularFileCountFrontier) &&
                segment.skipped_regular_file_count ==
                    expected_skipped[invocation] &&
                segment.resume_after_path == expected_cursors[invocation],
            "count-bounded continuation reports exact stop reason, prefix, and cursor state");
        all_delivered.insert(
            all_delivered.end(), delivered.begin(), delivered.end());
        cursor = segment.resume_after_path;
    }
    test.require(
        all_delivered == std::vector<std::string>{
            "a.txt", "b.txt", "c.txt", "d.txt", "e.txt"},
        "count-bounded continuation reaches every zero-byte path exactly once");

    auto four_file_capacity = limits;
    four_file_capacity.maximum_regular_files = 4U;
    std::vector<std::string> capacity_delivered;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                    authority, "b.txt",
                    [&](const std::string& path, std::uint64_t) {
                        capacity_delivered.push_back(path);
                    },
                    four_file_capacity, segment_limits,
                    "folder-count-frontier total regular-file capacity");
            },
            "regular-file limit: e.txt"),
        "a persisted cursor cannot bypass the whole-folder regular-file capacity");
    test.require(
        capacity_delivered == std::vector<std::string>{"c.txt", "d.txt"},
        "the whole-folder capacity counts skipped prefix files before rejecting the first excess suffix file");

    auto invalid_segment_limits = segment_limits;
    invalid_segment_limits.maximum_regular_files = 0U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                    authority, {},
                    [](const std::string&, std::uint64_t) {}, limits,
                    invalid_segment_limits,
                    "folder-count-frontier invalid segment");
            },
            "maximum regular files must be in"),
        "resumable traversal rejects a zero delivered-file frontier");
    authority.verify_or_throw(
        "folder-count-frontier authority after continuation segments");

    TemporaryDirectory race_temporary;
    const fs::path race_root = race_temporary.path();
    fs::create_directory(race_root / "nested");
    write_bytes(race_root / "nested" / "a.txt", {});
    write_bytes(race_root / "nested" / "b.txt", {});
    anonsync::SyncDirectoryAuthority race_authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(race_root),
            "folder-count-frontier reproof root");
    auto one_file = segment_limits;
    one_file.maximum_regular_files = 1U;
    bool substituted = false;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                    race_authority, {},
                    [&](const std::string& path, std::uint64_t) {
                        if (path != "nested/a.txt" || substituted) return;
                        fs::rename(
                            race_root / "nested",
                            race_root / "displaced-nested");
                        fs::create_directory(race_root / "nested");
                        substituted = true;
                    },
                    limits, one_file,
                    "folder-count-frontier rooted reproof");
            },
            "directory path changed while being observed: nested"),
        "count frontier refuses success after a visited directory binding is substituted");
    test.require(
        substituted,
        "count-frontier reproof fixture crossed the callback mutation cutpoint");
    race_authority.verify_or_throw(
        "folder-count-frontier authority after rejected substitution");
}

[[nodiscard]] std::string flat_file_name(
    std::uint64_t index,
    char prefix = 'f') {
    std::ostringstream name;
    name << prefix << std::setw(5) << std::setfill('0') << index << ".dat";
    return name.str();
}

void test_resumable_flat_directory_component_buffer(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const std::uint64_t file_count =
        anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch +
        17U;
    for (std::uint64_t index = 0U; index < file_count; ++index) {
        write_bytes(root / flat_file_name(index), {});
    }

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-flat-buffer root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = file_count;
    limits.maximum_regular_files = file_count;
    limits.maximum_file_bytes = 1U;
    limits.maximum_total_file_bytes = 1U;

    std::vector<std::string> delivered;
    bool all_classified_sizes_zero = true;
    std::string cursor;
    const std::vector<std::uint64_t> frontiers{
        1U,
        anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch,
        anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch};
    std::vector<anonsync::SyncReplicaFolderTraversalSegment> segments;
    for (const std::uint64_t frontier : frontiers) {
        anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
        segment_limits.maximum_regular_files = frontier;
        auto segment =
            anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
                authority, cursor,
                [&](const std::string& path, std::uint64_t size_bytes) {
                    all_classified_sizes_zero =
                        all_classified_sizes_zero && size_bytes == 0U;
                    delivered.push_back(path);
                },
                limits, segment_limits,
                "folder-flat-buffer traversal");
        cursor = segment.resume_after_path;
        segments.push_back(std::move(segment));
    }

    test.require(
        all_classified_sizes_zero && delivered.size() == file_count &&
            delivered.front() == flat_file_name(0U) &&
            delivered.back() == flat_file_name(file_count - 1U) &&
            std::is_sorted(delivered.begin(), delivered.end()) &&
            std::adjacent_find(delivered.begin(), delivered.end()) ==
                delivered.end(),
        "bounded component batches preserve exact flat-directory order and reach every file once");
    test.require(
        !segments[0].completed && !segments[1].completed &&
            segments[2].completed &&
            segments[0].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            segments[1].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            segments[2].stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::EndOfNamespace,
        "flat-directory continuation retains exact count-frontier and completion semantics");
    test.require(
        segments[0].peak_buffered_directory_component_batch_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch &&
            segments[1].peak_buffered_directory_component_batch_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch &&
            segments[2].peak_buffered_directory_component_batch_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch &&
            segments[0].peak_simultaneously_buffered_directory_component_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch &&
            segments[1].peak_simultaneously_buffered_directory_component_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch &&
            segments[2].peak_simultaneously_buffered_directory_component_count ==
                anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch,
        "every resumable flat-directory pass obeys both the individual and simultaneous basename-buffer ceiling");
    test.require(
        segments[0].directory_enumeration_pass_count == 1U &&
            segments[1].directory_enumeration_pass_count == 2U &&
            segments[2].directory_enumeration_pass_count == 2U,
        "resumable flat-directory work rescans only when one bounded "
        "component batch cannot finish the segment");
    test.require(
        segments[0].traversal.visited_entry_count == file_count &&
            segments[1].traversal.visited_entry_count == file_count &&
            segments[2].traversal.visited_entry_count == file_count,
        "directory rescans do not double-charge the namespace entry ceiling");
    authority.verify_or_throw(
        "folder-flat-buffer authority after bounded continuation");
}

void test_resumable_recursive_walk_releases_ancestor_component_batches(
    TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const fs::path first_child = root / "000-child";
    const fs::path second_child = first_child / "000-child";
    fs::create_directories(second_child);

    const std::uint64_t batch_limit =
        anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch;
    const std::uint64_t sibling_file_count = batch_limit - 1U;
    for (std::uint64_t index = 0U; index < sibling_file_count; ++index) {
        const std::string name = flat_file_name(index);
        write_bytes(root / name, {});
        write_bytes(first_child / name, {});
    }
    write_bytes(second_child / "leaf.dat", {});

    const std::uint64_t regular_file_count = sibling_file_count * 2U + 1U;
    const std::uint64_t entry_count = regular_file_count + 2U;
    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-recursive-buffer root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = entry_count;
    limits.maximum_regular_files = regular_file_count;
    limits.maximum_file_bytes = 1U;
    limits.maximum_total_file_bytes = 1U;
    limits.maximum_directory_depth = 4U;
    anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = regular_file_count;

    std::uint64_t delivered_count = 0U;
    bool strict_component_order = true;
    std::string first_path;
    std::string previous_path;
    std::string last_path;
    const auto segment =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, {},
            [&](const std::string& path, std::uint64_t size_bytes) {
                strict_component_order = strict_component_order &&
                    size_bytes == 0U &&
                    (previous_path.empty() ||
                     anonsync::sync_replica_folder_traversal_path_less(
                         previous_path, path));
                if (first_path.empty()) first_path = path;
                previous_path = path;
                last_path = path;
                ++delivered_count;
            },
            limits, segment_limits,
            "folder-recursive-buffer traversal");

    test.require(
        segment.completed &&
            segment.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::EndOfNamespace &&
            delivered_count == regular_file_count && strict_component_order &&
            first_path == "000-child/000-child/leaf.dat" &&
            last_path == flat_file_name(sibling_file_count - 1U),
        "recursive component batches preserve exact preorder while delivering every regular file once");
    test.require(
        segment.traversal.visited_entry_count == entry_count &&
            segment.traversal.visited_directory_count == 2U &&
            segment.traversal.regular_file_count == regular_file_count,
        "release-before-descent rescans do not double-charge namespace or file capacity");
    test.require(
        segment.peak_buffered_directory_component_batch_count == batch_limit &&
            segment.peak_simultaneously_buffered_directory_component_count ==
                batch_limit,
        "full ancestor batches are released before child selection so simultaneous selected basenames never multiply by depth");
    test.require(
        segment.directory_enumeration_pass_count == 5U,
        "release-before-descent resumes each full ancestor from its exact directory component boundary");
    authority.verify_or_throw(
        "folder-recursive-buffer authority after bounded traversal");
}

void test_resumable_parent_census_rejects_cross_boundary_rename(
    TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const fs::path child = root / "m-child";
    fs::create_directory(child);
    write_bytes(child / "leaf.dat", {});
    write_bytes(root / "z-later.dat", {});

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-parent-census-drift root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 3U;
    limits.maximum_regular_files = 2U;
    limits.maximum_file_bytes = 1U;
    limits.maximum_total_file_bytes = 1U;
    limits.maximum_directory_depth = 2U;
    anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = 2U;

    std::vector<std::string> first_delivered;
    bool renamed = false;
    const auto first =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, {},
            [&](const std::string& path, std::uint64_t size_bytes) {
                first_delivered.push_back(path);
                if (!renamed && path == "m-child/leaf.dat") {
                    fs::rename(root / "z-later.dat", root / "a-moved.dat");
                    renamed = true;
                }
                test.require(
                    size_bytes == 0U,
                    "parent-census drift fixture retains zero-byte files");
            },
            limits, segment_limits,
            "folder-parent-census-drift traversal");

    test.require(
        renamed && !first.completed &&
            first.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    DirectoryCensusFrontier &&
            first_delivered ==
                std::vector<std::string>{"m-child/leaf.dat"},
        "a rename across the released parent boundary cannot manufacture namespace completion");
    test.require(
        first.directory_enumeration_pass_count == 3U &&
            first.peak_simultaneously_buffered_directory_component_count == 2U,
        "parent resumption detects exact suffix-cardinality drift without retaining the ancestor batch");

    std::vector<std::string> fresh_delivered;
    const auto fresh =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, {},
            [&](const std::string& path, std::uint64_t size_bytes) {
                fresh_delivered.push_back(path);
                test.require(
                    size_bytes == 0U,
                    "fresh parent-census traversal retains zero-byte files");
            },
            limits, segment_limits,
            "folder-parent-census-drift fresh traversal");
    test.require(
        fresh.completed &&
            fresh.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::EndOfNamespace &&
            fresh_delivered == std::vector<std::string>{
                "a-moved.dat", "m-child/leaf.dat"},
        "a fresh epoch discovers the cross-boundary rename in exact preorder");
    authority.verify_or_throw(
        "folder-parent-census-drift authority after traversals");
}

void test_resumable_directory_does_not_chase_post_census_insertions(
    TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    const std::uint64_t batch_limit =
        anonsync::kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch;
    const std::uint64_t initial_file_count = batch_limit + 1U;
    const std::uint64_t inserted_file_count = 17U;
    for (std::uint64_t index = 0U; index < initial_file_count; ++index) {
        write_bytes(root / flat_file_name(index, 'a'), {});
    }
    const std::string boundary_name = flat_file_name(batch_limit - 1U, 'a');
    const std::string displaced_initial_name = flat_file_name(batch_limit, 'a');
    std::string interleaved_name = boundary_name;
    interleaved_name.insert(interleaved_name.find(".dat"), "x");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-census-fence root");
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = initial_file_count + inserted_file_count;
    limits.maximum_regular_files = initial_file_count + inserted_file_count;
    limits.maximum_file_bytes = 1U;
    limits.maximum_total_file_bytes = 1U;
    anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = limits.maximum_regular_files;

    bool inserted = false;
    std::vector<std::string> first_delivered;
    const auto first =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, {},
            [&](const std::string& path, std::uint64_t) {
                first_delivered.push_back(path);
                if (inserted) return;
                inserted = true;
                // This name sorts between the first batch boundary and the one
                // original first-census member that remained. It therefore
                // proves a concurrent insertion cannot steal the final census
                // slot and still manufacture end-of-namespace authority.
                write_bytes(root / interleaved_name, {});
                for (std::uint64_t index = 0U;
                     index + 1U < inserted_file_count; ++index) {
                    write_bytes(root / flat_file_name(index, 'z'), {});
                }
            },
            limits, segment_limits,
            "folder-census-fence first traversal");

    test.require(
        inserted && !first.completed &&
            first.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    DirectoryCensusFrontier &&
            first_delivered.size() == batch_limit &&
            first_delivered.front() == flat_file_name(0U, 'a') &&
            first_delivered.back() == boundary_name &&
            std::find(
                first_delivered.begin(), first_delivered.end(),
                interleaved_name) == first_delivered.end() &&
            std::find(
                first_delivered.begin(), first_delivered.end(),
                displaced_initial_name) == first_delivered.end() &&
            first.resume_after_path == boundary_name &&
            first.traversal.visited_entry_count == initial_file_count &&
            first.directory_enumeration_pass_count == 2U,
        "post-census growth stops without end-of-namespace authority even "
        "when a new name displaces an original census member");

    std::vector<std::string> second_delivered;
    const auto second =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, first.resume_after_path,
            [&](const std::string& path, std::uint64_t) {
                second_delivered.push_back(path);
            },
            limits, segment_limits,
            "folder-census-fence continuation traversal");
    std::vector<std::string> combined = first_delivered;
    combined.insert(
        combined.end(), second_delivered.begin(), second_delivered.end());
    test.require(
        second.completed &&
            second.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::EndOfNamespace &&
            second_delivered.size() == inserted_file_count + 1U &&
            second_delivered.front() == interleaved_name &&
            second_delivered[1] == displaced_initial_name &&
            second_delivered.back() ==
                flat_file_name(inserted_file_count - 2U, 'z') &&
            second.skipped_regular_file_count == batch_limit &&
            second.traversal.visited_entry_count ==
                initial_file_count + inserted_file_count &&
            combined.size() == initial_file_count + inserted_file_count &&
            std::is_sorted(combined.begin(), combined.end()) &&
            std::adjacent_find(combined.begin(), combined.end()) ==
                combined.end(),
        "the persisted cursor resumes at the displaced original member and "
        "then discovers every post-census name exactly once");
    authority.verify_or_throw(
        "folder-census-fence authority after continuation sweep");
}

void test_selective_sparse_logical_bytes_and_bounded_batch(
    TestState& test) {
    constexpr std::uint64_t tebibyte =
        1024ULL * 1024ULL * 1024ULL * 1024ULL;
    constexpr std::uint64_t first_logical = 2ULL * tebibyte + 17U;
    constexpr std::uint64_t second_logical = 2ULL * tebibyte + 19U;

    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    create_sparse_file(root / "cold-first.bin", first_logical);
    create_sparse_file(root / "cold-second.bin", second_logical);
    fs::create_directory(root / "cold-subtree");
    create_sparse_file(root / "cold-subtree" / "unvisited.bin",
                       tebibyte + 23U);
    write_bytes(root / "keep.bin", "hot");

    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "selective sparse observer root");
    const anonsync::SyncReplicaSelectiveSyncPolicy policy =
        anonsync::make_sync_replica_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly,
            {anonsync::SyncReplicaSelectiveSyncRule{
                "keep.bin",
                anonsync::SyncReplicaSelectiveSyncMode::Materialize}},
            1U);
    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 8U;
    limits.maximum_regular_files = 1U;
    limits.maximum_file_bytes = 8U;
    limits.maximum_total_file_bytes = 8U;
    limits.maximum_directory_depth = 4U;
    anonsync::SyncReplicaFolderTraversalSegmentLimits segment_limits;
    segment_limits.maximum_regular_files = 1U;

    std::vector<std::pair<std::string, std::uint64_t>> delivered;
    const anonsync::SyncReplicaFolderTraversalSegment segment =
        anonsync::visit_sync_replica_folder_regular_file_paths_resumable_or_throw(
            authority, {},
            [&](const std::string& canonical_path,
                std::uint64_t classified_size) {
                delivered.emplace_back(canonical_path, classified_size);
            },
            policy, limits, segment_limits,
            "selective sparse logical-byte traversal");

    test.require(
        segment.completed &&
            segment.stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::EndOfNamespace,
        "selective sparse traversal reaches the selected namespace end");
    test.require(
        delivered ==
            std::vector<std::pair<std::string, std::uint64_t>>{{"keep.bin", 3U}},
        "only the selected bounded regular file reaches the visitor");
    test.require(
        segment.traversal.metadata_only_regular_file_count == 2U,
        "individually classified metadata-only files are counted");
    test.require(
        segment.traversal.metadata_only_regular_file_logical_bytes ==
            first_logical + second_logical,
        "metadata-only sparse logical bytes cross four tebibytes exactly");
    test.require(
        segment.traversal.metadata_only_pruned_directory_count == 1U,
        "a metadata-only subtree is pruned before its sparse child is observed");
    test.require(
        segment.traversal.regular_file_count == 1U &&
            segment.traversal.classified_regular_file_bytes == 3U,
        "metadata-only logical size does not spend selected byte frontiers");
    test.require(
        segment.directory_enumeration_pass_count == 1U &&
            segment.peak_buffered_directory_component_batch_count <= 4096U &&
            segment.peak_simultaneously_buffered_directory_component_count <=
                4096U,
        "selective logical accounting preserves the bounded component batch");
}

void test_limits_and_portable_paths(TestState& test) {
    TemporaryDirectory temporary;
    const fs::path root = temporary.path();
    fs::create_directory(root / "deep");
    write_bytes(root / "one.txt", "1234");
    write_bytes(root / "two.txt", "5678");
    write_bytes(root / "deep" / "three.txt", "90");
    anonsync::SyncDirectoryAuthority authority =
        anonsync::SyncDirectoryAuthority::open_or_throw(
            fs::absolute(root), "folder-observer limits root");

    anonsync::SyncReplicaFolderObservationLimits limits;
    limits.maximum_entries = 2;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "entry-bound scan");
            },
            "entry limit"),
        "the total directory-entry bound includes directories and files");

    limits = {};
    limits.maximum_entries = 4U;
    limits.maximum_regular_files = 3U;
    const auto independently_bounded =
        anonsync::observe_sync_replica_folder_or_throw(
            authority, limits, "independent namespace/file capacity scan");
    test.require(
        independently_bounded.visited_entry_count == 4U &&
            independently_bounded.regular_files.size() == 3U &&
            independently_bounded.visited_directory_count == 1U,
        "one directory spends namespace capacity without consuming regular-file capacity");

    limits.maximum_regular_files = 2U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "regular-file-capacity scan");
            },
            "regular-file limit"),
        "the regular-file ceiling is independent from the larger namespace-entry ceiling");

    limits = {};
    limits.maximum_file_bytes = 3;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "file-byte-bound scan");
            },
            "file exceeds configured byte limit"),
        "per-file byte limits reject before unbounded retention");

    limits = {};
    limits.maximum_total_file_bytes = 7;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "total-byte-bound scan");
            },
            "total file-byte limit"),
        "aggregate byte limits bind the complete returned batch");

    limits = {};
    limits.maximum_directory_depth = 0;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "depth-bound scan");
            },
            "directory depth"),
        "zero directory depth permits only root-level regular files");

    limits = {};
    limits.maximum_relative_path_bytes = 6;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "path-byte-bound scan");
            },
            "path exceeds configured byte limit"),
        "canonical relative paths have an explicit byte ceiling");

    write_bytes(root / "bad:name", "bad");
    limits = {};
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "portable-path scan");
            },
            "path is not portable"),
        "a POSIX-valid but cross-platform-invalid regular filename aborts the batch");

    limits = {};
    limits.maximum_entries = 0;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "invalid-limit scan");
            },
            "maximum entries must be positive"),
        "invalid scan policy fails before touching the folder");

    limits = {};
    limits.maximum_regular_files = 0U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "invalid-regular-file-limit scan");
            },
            "maximum regular files must be positive"),
        "a zero whole-folder regular-file capacity fails before traversal");

    limits = {};
    limits.maximum_entries =
        anonsync::kSyncReplicaFolderObservationMaximumEntries + 1U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "entry-hard-cap scan");
            },
            "maximum entries must be at most"),
        "sorted per-directory buffering has a public hard entry ceiling");

    limits = {};
    limits.maximum_regular_files =
        anonsync::kSyncReplicaFolderObservationMaximumRegularFiles + 1U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "regular-file-hard-cap scan");
            },
            "maximum regular files must be at most"),
        "whole-folder regular-file policy has its own public hard ceiling");

    limits = {};
    limits.maximum_directory_depth =
        anonsync::kSyncReplicaFolderObservationMaximumDirectoryDepth + 1U;
    test.require(
        throws_with(
            [&] {
                (void)anonsync::observe_sync_replica_folder_or_throw(
                    authority, limits, "depth-hard-cap scan");
            },
            "maximum directory depth must be at most"),
        "recursive traversal rejects stack-amplifying configured depth");
    authority.verify_or_throw("folder-observer limits authority remains valid");
}

}  // namespace

int main() {
    try {
        TestState test;
        test_bounded_descriptor_rooted_scan(test);
        test_internal_publication_artifacts_are_reserved(test);
        test_streaming_path_visitor(test);
        test_resumable_component_order_and_progress(test);
        test_resumable_count_frontier_and_rooted_reproof(test);
        test_resumable_flat_directory_component_buffer(test);
        test_resumable_recursive_walk_releases_ancestor_component_batches(test);
        test_resumable_parent_census_rejects_cross_boundary_rename(test);
        test_resumable_directory_does_not_chase_post_census_insertions(test);
        test_selective_sparse_logical_bytes_and_bounded_batch(test);
        test_limits_and_portable_paths(test);
        std::cout << "sync replica folder observer checks: " << test.passed
                  << "/" << (test.passed + test.failed) << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}

#else

#include <iostream>

int main() {
    std::cout << "sync replica folder observer unavailable on Windows\n";
    return 0;
}

#endif
