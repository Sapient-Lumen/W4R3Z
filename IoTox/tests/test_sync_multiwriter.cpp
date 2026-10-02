#include "test_harness.hpp"

#include "iotox/sync_multiwriter.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::TreeV2BranchHead;
using iotox::sync::TreeV2Entry;
using iotox::sync::TreeV2EntryKind;
using iotox::sync::TreeV2Manifest;
using iotox::sync::TreeV2Observation;
using iotox::sync::TreeV2Snapshot;
using iotox::sync::TreeV2Version;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-multiwriter-XXXXXX";
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char *created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
        path_ = created;
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

Sodium sodium() {
    auto loaded = Sodium::load();
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
    auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

Digest digest(std::uint8_t value) {
    Digest result{};
    result[0U] = value;
    return result;
}

NamespacePolicy policy_for(const DeviceIdentity &left,
                           const DeviceIdentity &right) {
    NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = "/var/lib/iotox/sync/field-notes";
    policy.engine = Engine::tree_v2;
    policy.writers = {left.public_key(), right.public_key()};
    std::sort(policy.writers.begin(), policy.writers.end());
    return policy;
}

NamespacePolicy policy_for(const DeviceIdentity &left,
                           const DeviceIdentity &middle,
                           const DeviceIdentity &right) {
    NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = "/var/lib/iotox/sync/field-notes";
    policy.engine = Engine::tree_v2;
    policy.writers = {left.public_key(), middle.public_key(),
                      right.public_key()};
    std::sort(policy.writers.begin(), policy.writers.end());
    return policy;
}

TreeV2Entry file(std::string path, const PrincipalId &writer,
                 std::uint64_t generation, std::uint8_t content,
                 bool executable = false) {
    return TreeV2Entry{std::move(path),
                       TreeV2EntryKind::file,
                       TreeV2Version{writer, generation},
                       digest(content),
                       1024U,
                       executable};
}

TreeV2Entry directory(std::string path, const PrincipalId &writer,
                      std::uint64_t generation) {
    return TreeV2Entry{std::move(path),
                       TreeV2EntryKind::directory,
                       TreeV2Version{writer, generation},
                       {},
                       0U,
                       false};
}

TreeV2Entry tombstone(std::string path, const PrincipalId &writer,
                      std::uint64_t generation) {
    return TreeV2Entry{std::move(path),
                       TreeV2EntryKind::tombstone,
                       TreeV2Version{writer, generation},
                       {},
                       0U,
                       false};
}

TreeV2Manifest manifest(std::vector<TreeV2Entry> entries) {
    std::sort(entries.begin(), entries.end(),
              [](const TreeV2Entry &left, const TreeV2Entry &right) {
                  if (left.path != right.path) return left.path < right.path;
                  if (left.origin.writer != right.origin.writer)
                      return left.origin.writer < right.origin.writer;
                  if (left.origin.generation != right.origin.generation)
                      return left.origin.generation < right.origin.generation;
                  return left.kind < right.kind;
              });
    return TreeV2Manifest{std::move(entries)};
}

TreeV2Observation observation(const NamespacePolicy &policy,
                              const TreeV2BranchHead &head,
                              const Sodium &crypto) {
    auto record =
        iotox::sync::tree_v2_branch_record_digest(policy, head, crypto);
    if (!record) throw std::runtime_error(record.status().message());
    return TreeV2Observation{head.writer, head.generation, record.value()};
}

TreeV2BranchHead branch(const NamespacePolicy &policy,
                        const TreeV2Manifest &tree,
                        const std::optional<TreeV2BranchHead> &previous,
                        std::vector<TreeV2Observation> observations,
                        const DeviceIdentity &writer, const Sodium &crypto) {
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, tree, previous, observations, writer, crypto);
    if (!created) throw std::runtime_error(created.status().message());
    return created.value();
}

} // namespace

IOTOX_TEST("tree-v2 manifest and branch records are canonical and signed") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);
    const TreeV2Manifest tree = manifest({
        TreeV2Entry{"docs",
                    TreeV2EntryKind::directory,
                    TreeV2Version{left.public_key(), 1U},
                    {},
                    0U,
                    false},
        file("docs/field.txt", left.public_key(), 1U, 11U),
    });

    IOTOX_CHECK(iotox::sync::validate_tree_v2_manifest(policy, tree).ok());
    auto encoded = iotox::sync::encode_tree_v2_manifest(policy, tree);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    auto legacy_digest =
        crypto.hash("iotox-sync-tree-v2-manifest-v1", encoded.value());
    auto manifest_digest =
        iotox::sync::tree_v2_manifest_digest(policy, tree, crypto);
    IOTOX_CHECK(legacy_digest.ok());
    IOTOX_CHECK(manifest_digest.ok());
    IOTOX_CHECK(manifest_digest.value() == legacy_digest.value());
    auto decoded =
        iotox::sync::decode_tree_v2_manifest(policy, encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == tree);

    const TreeV2BranchHead genesis =
        branch(policy, tree, std::nullopt, {}, left, crypto);
    IOTOX_CHECK(genesis.generation == 1U);
    IOTOX_CHECK(
        iotox::sync::verify_tree_v2_branch_head(policy, genesis, crypto).ok());
    auto encoded_head =
        iotox::sync::encode_tree_v2_branch_head(policy, genesis);
    IOTOX_CHECK_MSG(encoded_head.ok(), encoded_head.status().message());
    auto decoded_head =
        iotox::sync::decode_tree_v2_branch_head(policy, encoded_head.value());
    IOTOX_CHECK_MSG(decoded_head.ok(), decoded_head.status().message());
    IOTOX_CHECK(decoded_head.value() == genesis);
    IOTOX_CHECK(iotox::sync::verify_tree_v2_snapshot(
                    policy, TreeV2Snapshot{genesis, tree}, crypto)
                    .ok());

    encoded.value()[9U] = 1U;
    IOTOX_CHECK(
        !iotox::sync::decode_tree_v2_manifest(policy, encoded.value()).ok());
    encoded_head.value().back() ^= 0x01U;
    auto altered =
        iotox::sync::decode_tree_v2_branch_head(policy, encoded_head.value());
    IOTOX_CHECK(altered.ok());
    IOTOX_CHECK(!iotox::sync::verify_tree_v2_branch_head(
                     policy, altered.value(), crypto)
                     .ok());
}

IOTOX_TEST("tree-v2 manifest v2 preserves exact owner file permissions") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);
    TreeV2Entry read_only =
        file("field.txt", left.public_key(), 1U, 19U, false);
    read_only.owner_mode = 4U;
    TreeV2Entry executable =
        file("tool", right.public_key(), 1U, 20U, true);
    executable.owner_mode = 5U;
    const TreeV2Manifest tree = manifest({read_only, executable});
    auto encoded = iotox::sync::encode_tree_v2_manifest(policy, tree);
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value()[8U] ==
                iotox::sync::kTreeV2OwnerModeManifestVersion);
    auto decoded =
        iotox::sync::decode_tree_v2_manifest(policy, encoded.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == tree);
    IOTOX_CHECK(decoded.value().entries[0U].owner_mode == 4U);
    IOTOX_CHECK(decoded.value().entries[1U].owner_mode == 5U);

    TreeV2Entry invalid = read_only;
    invalid.owner_mode = 3U;
    IOTOX_CHECK(!iotox::sync::validate_tree_v2_manifest(
                     policy, manifest({invalid}))
                     .ok());
    std::vector<std::uint8_t> corrupt = encoded.value();
    corrupt[17U] = 3U;
    IOTOX_CHECK(!iotox::sync::decode_tree_v2_manifest(policy, corrupt).ok());
}

IOTOX_TEST("tree-v2 rejects unsafe paths duplicate events and false ancestry") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);

    IOTOX_CHECK(iotox::sync::valid_tree_v2_path("docs/field.txt"));
    IOTOX_CHECK(!iotox::sync::valid_tree_v2_path("/docs/field.txt"));
    IOTOX_CHECK(!iotox::sync::valid_tree_v2_path("docs/../field.txt"));
    IOTOX_CHECK(!iotox::sync::valid_tree_v2_path(".iotox-conflicts/field.txt"));
    IOTOX_CHECK(!iotox::sync::valid_tree_v2_path("docs//field.txt"));

    TreeV2Manifest duplicate = manifest({
        file("field.txt", left.public_key(), 1U, 1U),
        file("field.txt", left.public_key(), 1U, 2U),
    });
    IOTOX_CHECK(
        !iotox::sync::validate_tree_v2_manifest(policy, duplicate).ok());

    const TreeV2Manifest nested = manifest({
        directory("docs", left.public_key(), 1U),
        directory("docs/reports", left.public_key(), 1U),
        file("docs/reports/field.txt", left.public_key(), 1U, 3U),
    });
    IOTOX_CHECK(iotox::sync::validate_tree_v2_manifest(policy, nested).ok());

    const TreeV2Manifest missing_ancestor = manifest({
        directory("docs/reports", left.public_key(), 1U),
        file("docs/reports/field.txt", left.public_key(), 1U, 3U),
    });
    IOTOX_CHECK(!iotox::sync::validate_tree_v2_manifest(
                     policy, missing_ancestor)
                     .ok());

    const TreeV2Manifest false_ancestor = manifest({
        file("docs", right.public_key(), 1U, 4U),
        file("docs/field.txt", left.public_key(), 1U, 5U),
    });
    IOTOX_CHECK(!iotox::sync::validate_tree_v2_manifest(
                     policy, false_ancestor)
                     .ok());

    const TreeV2Manifest genesis_tree =
        manifest({file("field.txt", left.public_key(), 1U, 1U)});
    const TreeV2BranchHead genesis =
        branch(policy, genesis_tree, std::nullopt, {}, left, crypto);
    const TreeV2Manifest successor_tree =
        manifest({file("field.txt", left.public_key(), 2U, 2U)});
    auto self = observation(policy, genesis, crypto);
    auto invalid = iotox::sync::create_tree_v2_branch_head(
        policy, successor_tree, genesis,
        std::span<const TreeV2Observation>{&self, 1U}, left, crypto);
    IOTOX_CHECK(!invalid.ok());
}

IOTOX_TEST(
    "tree-v2 retains concurrent edits and converges independent of order") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);

    const TreeV2Manifest left_base =
        manifest({file("field.txt", left.public_key(), 1U, 1U)});
    const TreeV2Manifest right_base =
        manifest({file("field.txt", right.public_key(), 1U, 1U)});
    const TreeV2BranchHead left_one =
        branch(policy, left_base, std::nullopt, {}, left, crypto);
    const TreeV2BranchHead right_one =
        branch(policy, right_base, std::nullopt, {}, right, crypto);

    const TreeV2Manifest left_edit =
        manifest({file("field.txt", left.public_key(), 2U, 2U)});
    const TreeV2Manifest right_edit =
        manifest({file("field.txt", right.public_key(), 2U, 3U)});
    const TreeV2BranchHead left_two =
        branch(policy, left_edit, left_one,
               {observation(policy, right_one, crypto)}, left, crypto);
    const TreeV2BranchHead right_two =
        branch(policy, right_edit, right_one,
               {observation(policy, left_one, crypto)}, right, crypto);

    const std::vector<TreeV2Snapshot> forward{{left_two, left_edit},
                                              {right_two, right_edit}};
    const std::vector<TreeV2Snapshot> reverse{{right_two, right_edit},
                                              {left_two, left_edit}};
    auto merged_forward =
        iotox::sync::merge_tree_v2_snapshots(policy, forward, crypto);
    auto merged_reverse =
        iotox::sync::merge_tree_v2_snapshots(policy, reverse, crypto);
    IOTOX_CHECK_MSG(merged_forward.ok(), merged_forward.status().message());
    IOTOX_CHECK_MSG(merged_reverse.ok(), merged_reverse.status().message());
    IOTOX_CHECK(merged_forward.value() == merged_reverse.value());
    IOTOX_CHECK(merged_forward.value().manifest.entries.size() == 2U);
    IOTOX_CHECK(merged_forward.value().conflicts.size() == 1U);
    IOTOX_CHECK(merged_forward.value().conflicts.front().path == "field.txt");
    IOTOX_CHECK(merged_forward.value().live_files == 1U);

    auto selected = iotox::sync::select_tree_v2_projection_entry(
        merged_forward.value().manifest.entries);
    IOTOX_CHECK(selected.ok());
    IOTOX_CHECK(selected.value().kind == TreeV2EntryKind::file);

    const TreeV2Manifest resolved =
        manifest({file("field.txt", left.public_key(), 3U, 4U)});
    const TreeV2BranchHead left_three =
        branch(policy, resolved, left_two,
               {observation(policy, right_two, crypto)}, left, crypto);
    const std::vector<TreeV2Snapshot> after_resolution{{left_three, resolved},
                                                       {right_two, right_edit}};
    auto converged =
        iotox::sync::merge_tree_v2_snapshots(policy, after_resolution, crypto);
    IOTOX_CHECK_MSG(converged.ok(), converged.status().message());
    IOTOX_CHECK(converged.value().manifest == resolved);
    IOTOX_CHECK(converged.value().conflicts.empty());
}

IOTOX_TEST(
    "tree-v2 converges three concurrent writers in every arrival order") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto first = identity(temporary.path() / "first.identity", crypto);
    auto second = identity(temporary.path() / "second.identity", crypto);
    auto third = identity(temporary.path() / "third.identity", crypto);
    const NamespacePolicy policy = policy_for(first, second, third);

    const TreeV2Manifest first_tree =
        manifest({file("field.txt", first.public_key(), 1U, 0x11U)});
    const TreeV2Manifest second_tree =
        manifest({file("field.txt", second.public_key(), 1U, 0x22U)});
    const TreeV2Manifest third_tree =
        manifest({file("field.txt", third.public_key(), 1U, 0x33U)});
    const TreeV2BranchHead first_head =
        branch(policy, first_tree, std::nullopt, {}, first, crypto);
    const TreeV2BranchHead second_head =
        branch(policy, second_tree, std::nullopt, {}, second, crypto);
    const TreeV2BranchHead third_head =
        branch(policy, third_tree, std::nullopt, {}, third, crypto);
    const std::array<TreeV2Snapshot, 3U> frontier{
        TreeV2Snapshot{first_head, first_tree},
        TreeV2Snapshot{second_head, second_tree},
        TreeV2Snapshot{third_head, third_tree}};

    std::array<std::size_t, 3U> order{0U, 1U, 2U};
    std::optional<iotox::sync::TreeV2MergeResult> expected;
    std::size_t permutations = 0U;
    do {
        const std::vector<TreeV2Snapshot> arranged{
            frontier[order[0U]], frontier[order[1U]], frontier[order[2U]]};
        auto merged =
            iotox::sync::merge_tree_v2_snapshots(policy, arranged, crypto);
        IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
        IOTOX_CHECK(merged.value().manifest.entries.size() == 3U);
        IOTOX_CHECK(merged.value().conflicts.size() == 1U);
        IOTOX_CHECK(merged.value().conflicts.front().candidates.size() == 3U);
        if (!expected) {
            expected = merged.value();
        } else {
            IOTOX_CHECK(merged.value() == *expected);
        }
        ++permutations;
    } while (std::next_permutation(order.begin(), order.end()));
    IOTOX_CHECK(permutations == 6U);

    const TreeV2Manifest resolved =
        manifest({file("field.txt", first.public_key(), 2U, 0x44U)});
    const std::array<TreeV2Observation, 2U> observations{
        observation(policy, second_head, crypto),
        observation(policy, third_head, crypto)};
    const TreeV2BranchHead resolved_head = branch(
        policy, resolved, first_head, {observations.begin(), observations.end()},
        first, crypto);
    const std::vector<TreeV2Snapshot> resolved_frontier{
        {third_head, third_tree},
        {resolved_head, resolved},
        {second_head, second_tree}};
    auto converged = iotox::sync::merge_tree_v2_snapshots(
        policy, resolved_frontier, crypto);
    IOTOX_CHECK_MSG(converged.ok(), converged.status().message());
    IOTOX_CHECK(converged.value().manifest == resolved);
    IOTOX_CHECK(converged.value().conflicts.empty());
}

IOTOX_TEST("tree-v2 grouped merge preserves many paths and conflicts") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);

    std::vector<TreeV2Entry> left_entries;
    std::vector<TreeV2Entry> right_entries;
    constexpr std::size_t path_count = 256U;
    left_entries.reserve(path_count + 1U);
    right_entries.reserve(path_count + 1U);
    for (std::size_t index = 0U; index < path_count; ++index) {
        const std::string path = "file-" + std::to_string(index) + ".txt";
        const std::uint8_t content =
            static_cast<std::uint8_t>((index % 250U) + 1U);
        left_entries.push_back(file(path, left.public_key(), 1U, content));
        right_entries.push_back(file(path, right.public_key(), 1U, content));
    }
    left_entries.push_back(file("conflict.txt", left.public_key(), 1U, 0xfeU));
    right_entries.push_back(
        file("conflict.txt", right.public_key(), 1U, 0xfdU));

    const TreeV2Manifest left_tree = manifest(std::move(left_entries));
    const TreeV2Manifest right_tree = manifest(std::move(right_entries));
    const TreeV2BranchHead left_head =
        branch(policy, left_tree, std::nullopt, {}, left, crypto);
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, {}, right, crypto);

    const std::vector<TreeV2Snapshot> frontier{{left_head, left_tree},
                                               {right_head, right_tree}};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, frontier, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().paths == path_count + 1U);
    IOTOX_CHECK(merged.value().manifest.entries.size() == path_count + 2U);
    IOTOX_CHECK(merged.value().conflicts.size() == 1U);
    IOTOX_CHECK(merged.value().conflicts.front().path == "conflict.txt");
    IOTOX_CHECK(merged.value().conflicts.front().candidates.size() == 2U);

    auto summarized =
        iotox::sync::summarize_tree_v2_manifest(policy,
                                                merged.value().manifest);
    IOTOX_CHECK_MSG(summarized.ok(), summarized.status().message());
    IOTOX_CHECK(summarized.value().manifest == merged.value().manifest);
    IOTOX_CHECK(summarized.value().paths == merged.value().paths);
    IOTOX_CHECK(summarized.value().live_files == merged.value().live_files);
    IOTOX_CHECK(summarized.value().conflicts == merged.value().conflicts);
}

IOTOX_TEST("tree-v2 bounds and converges a sixteen-writer conflict storm") {
    TempDirectory temporary;
    auto crypto = sodium();
    constexpr std::size_t writer_count =
        iotox::sync::kTreeV2MaximumValuesPerPath;
    std::vector<DeviceIdentity> identities;
    identities.reserve(writer_count + 1U);
    for (std::size_t index = 0U; index <= writer_count; ++index) {
        identities.push_back(identity(
            temporary.path() / ("writer-" + std::to_string(index) +
                                ".identity"),
            crypto));
    }

    NamespacePolicy policy;
    policy.id = "conflict-storm";
    policy.root = "/var/lib/iotox/sync/conflict-storm";
    policy.engine = Engine::tree_v2;
    policy.quotas.maximum_peers = writer_count;
    for (std::size_t index = 0U; index < writer_count; ++index)
        policy.writers.push_back(identities[index].public_key());
    std::sort(policy.writers.begin(), policy.writers.end());

    std::vector<TreeV2Snapshot> frontier;
    frontier.reserve(writer_count);
    for (std::size_t index = 0U; index < writer_count; ++index) {
        const TreeV2Manifest tree = manifest({file(
            "storm.txt", identities[index].public_key(), 1U,
            static_cast<std::uint8_t>(index + 1U))});
        frontier.push_back(TreeV2Snapshot{
            branch(policy, tree, std::nullopt, {}, identities[index], crypto),
            tree});
    }

    std::vector<std::size_t> order(writer_count);
    std::iota(order.begin(), order.end(), 0U);
    std::mt19937_64 schedule(0x49544f584d3543ULL);
    std::optional<iotox::sync::TreeV2MergeResult> expected;
    for (std::size_t round = 0U; round < 128U; ++round) {
        std::shuffle(order.begin(), order.end(), schedule);
        std::vector<TreeV2Snapshot> arranged;
        arranged.reserve(writer_count);
        for (const std::size_t index : order)
            arranged.push_back(frontier[index]);
        auto merged =
            iotox::sync::merge_tree_v2_snapshots(policy, arranged, crypto);
        IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
        IOTOX_CHECK(merged.value().manifest.entries.size() == writer_count);
        IOTOX_CHECK(merged.value().conflicts.size() == 1U);
        IOTOX_CHECK(merged.value().conflicts.front().candidates.size() ==
                    writer_count);
        if (!expected)
            expected = merged.value();
        else
            IOTOX_CHECK(merged.value() == *expected);
    }

    NamespacePolicy excessive = policy;
    excessive.quotas.maximum_peers = writer_count + 1U;
    excessive.writers.push_back(identities.back().public_key());
    std::sort(excessive.writers.begin(), excessive.writers.end());
    std::vector<TreeV2Entry> amplified = expected->manifest.entries;
    amplified.push_back(file("storm.txt", identities.back().public_key(), 1U,
                             0xffU));
    const TreeV2Manifest excessive_manifest = manifest(std::move(amplified));
    const auto refused =
        iotox::sync::validate_tree_v2_manifest(excessive, excessive_manifest);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.code() == iotox::ErrorCode::resource_exhausted);
}

IOTOX_TEST("tree-v2 preserves concurrent delete versus edit as a conflict") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const NamespacePolicy policy = policy_for(left, right);

    const TreeV2Manifest left_base =
        manifest({file("field.txt", left.public_key(), 1U, 1U)});
    const TreeV2Manifest right_base =
        manifest({file("field.txt", right.public_key(), 1U, 1U)});
    const TreeV2BranchHead left_one =
        branch(policy, left_base, std::nullopt, {}, left, crypto);
    const TreeV2BranchHead right_one =
        branch(policy, right_base, std::nullopt, {}, right, crypto);
    const TreeV2Manifest removed =
        manifest({tombstone("field.txt", left.public_key(), 2U)});
    const TreeV2Manifest edited =
        manifest({file("field.txt", right.public_key(), 2U, 9U)});
    const TreeV2BranchHead left_two =
        branch(policy, removed, left_one,
               {observation(policy, right_one, crypto)}, left, crypto);
    const TreeV2BranchHead right_two =
        branch(policy, edited, right_one,
               {observation(policy, left_one, crypto)}, right, crypto);

    const std::vector<TreeV2Snapshot> frontier{{left_two, removed},
                                               {right_two, edited}};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, frontier, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().conflicts.size() == 1U);
    auto selected = iotox::sync::select_tree_v2_projection_entry(
        merged.value().manifest.entries);
    IOTOX_CHECK(selected.ok());
    IOTOX_CHECK(selected.value().kind == TreeV2EntryKind::file);
    IOTOX_CHECK(selected.value().content == digest(9U));
    IOTOX_CHECK(merged.value().tombstoned_paths == 0U);
}
