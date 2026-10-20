#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/treepack.hpp"

#include <fstream>
#include <iomanip>
#include <sstream>
#include <sys/stat.h>

TOXSYNC_TEST(treepack_is_deterministic_and_round_trips) {
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source / "empty");
    std::filesystem::create_directories(source / "nested");
    test::write_file(source / "alpha.bin", test::pattern(1000U, 1U));
    test::write_file(source / "nested" / "beta.bin", test::pattern(7777U, 2U));
    const auto first = temp.path() / "first.txtree";
    const auto second = temp.path() / "second.txtree";
    const auto first_stats = toxsync::pack_tree(source, first);
    const auto second_stats = toxsync::pack_tree(source, second);
    REQUIRE(test::read_file(first) == test::read_file(second));
    REQUIRE(first_stats.files == 2U);
    REQUIRE(first_stats.directories == 2U);
    REQUIRE(first_stats.artifact_bytes == second_stats.artifact_bytes);

    const auto destination = temp.path() / "unpacked";
    const auto unpacked = toxsync::unpack_tree(first, destination);
    REQUIRE(unpacked.files == 2U);
    REQUIRE(test::read_file(destination / "alpha.bin") == test::read_file(source / "alpha.bin"));
    REQUIRE(test::read_file(destination / "nested" / "beta.bin") == test::read_file(source / "nested" / "beta.bin"));
    REQUIRE(std::filesystem::is_directory(destination / "empty"));
}

TOXSYNC_TEST(treepack_requires_fresh_or_empty_destination) {
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "current", test::pattern(10U, 3U));
    const auto artifact = temp.path() / "tree";
    static_cast<void>(toxsync::pack_tree(source, artifact));
    const auto destination = temp.path() / "destination";
    std::filesystem::create_directories(destination);
    test::write_file(destination / "stale", test::pattern(4U, 4U));
    REQUIRE_THROWS(toxsync::unpack_tree(artifact, destination));
}

TOXSYNC_TEST(treepack_rejects_corruption_and_trailing_data) {
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "file", test::pattern(20U, 9U));
    const auto artifact = temp.path() / "tree";
    static_cast<void>(toxsync::pack_tree(source, artifact));
    auto bytes = test::read_file(artifact);
    bytes[0] ^= std::byte{1};
    test::write_file(temp.path() / "bad-magic", bytes);
    REQUIRE_THROWS(toxsync::unpack_tree(temp.path() / "bad-magic", temp.path() / "out1"));

    bytes = test::read_file(artifact);
    bytes.push_back(std::byte{0});
    test::write_file(temp.path() / "trailing", bytes);
    REQUIRE_THROWS(toxsync::unpack_tree(temp.path() / "trailing", temp.path() / "out2"));
}

TOXSYNC_TEST(treepack_rejects_symlinks_when_supported) {
#if defined(__unix__) || defined(__APPLE__)
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "real", test::pattern(10U, 1U));
    std::filesystem::create_symlink("real", source / "link");
    REQUIRE_THROWS(toxsync::pack_tree(source, temp.path() / "tree"));
#endif
}

TOXSYNC_TEST(treepack_external_sort_bounds_file_count_memory_and_is_byte_identical) {
    test::TempDir temp;
    const auto source = temp.path() / "many-files";
    std::filesystem::create_directories(source);
    for (std::uint32_t index = 0; index < 240U; ++index) {
        std::ostringstream name;
        name << "entry-" << std::setw(4) << std::setfill('0') << index
             << ".bin";
        test::write_file(source / name.str(), test::pattern(17U, index + 1U));
    }

    const auto ordinary = temp.path() / "ordinary.txtree";
    const auto spilled = temp.path() / "spilled.txtree";
    const auto ordinary_stats = toxsync::pack_tree(source, ordinary);

    toxsync::TreePackLimits limits;
    limits.sort_memory_bytes = 256U;
    limits.max_open_sort_runs = 3U;
    const auto spilled_stats = toxsync::pack_tree(source, spilled, limits);
    REQUIRE(spilled_stats.sort_runs > limits.max_open_sort_runs);
    REQUIRE(spilled_stats.sort_merge_passes > 0U);
    REQUIRE(spilled_stats.peak_sort_buffer_bytes < 1024U);
    REQUIRE(spilled_stats.files == ordinary_stats.files);
    REQUIRE(test::read_file(spilled) == test::read_file(ordinary));

    const auto output = temp.path() / "external-sort-output";
    const auto unpacked = toxsync::unpack_tree(spilled, output);
    REQUIRE(unpacked.files == 240U);
    REQUIRE(test::read_file(output / "entry-0239.bin") ==
            test::read_file(source / "entry-0239.bin"));
}

TOXSYNC_TEST(treepack_bounds_complete_artifacts_before_unpacking) {
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "payload", test::pattern(1024U, 1U));
    toxsync::TreePackLimits bounded;
    bounded.max_artifact_bytes = 128U;
    REQUIRE_THROWS(toxsync::pack_tree(
        source, temp.path() / "oversized.txtree", bounded));

    const auto artifact = temp.path() / "ordinary.txtree";
    static_cast<void>(toxsync::pack_tree(source, artifact));
    REQUIRE_THROWS(toxsync::unpack_tree(
        artifact, temp.path() / "rejected", bounded));
}

TOXSYNC_TEST(treepack_unpacks_owner_only_modes) {
#if defined(__unix__) || defined(__APPLE__)
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source / "nested");
    test::write_file(source / "plain", test::pattern(8U, 1U));
    test::write_file(source / "nested" / "executable", test::pattern(8U, 2U));
    std::filesystem::permissions(
        source / "nested" / "executable",
        std::filesystem::perms::owner_all,
        std::filesystem::perm_options::replace);
    const auto artifact = temp.path() / "tree.txtree";
    static_cast<void>(toxsync::pack_tree(source, artifact));
    const auto destination = temp.path() / "destination";
    static_cast<void>(toxsync::unpack_tree(artifact, destination));

    struct stat metadata {};
    REQUIRE(::lstat(destination.c_str(), &metadata) == 0);
    REQUIRE((metadata.st_mode & 0777U) == 0700U);
    REQUIRE(::lstat((destination / "plain").c_str(), &metadata) == 0);
    REQUIRE((metadata.st_mode & 0777U) == 0600U);
    REQUIRE(::lstat(
        (destination / "nested" / "executable").c_str(), &metadata) == 0);
    REQUIRE((metadata.st_mode & 0777U) == 0700U);
#endif
}
