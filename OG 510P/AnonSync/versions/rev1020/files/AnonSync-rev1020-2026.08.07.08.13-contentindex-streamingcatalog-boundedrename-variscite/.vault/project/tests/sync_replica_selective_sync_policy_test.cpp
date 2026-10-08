#include "sync_replica_selective_sync_policy.hpp"

#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

std::uint64_t checks = 0U;

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

template <typename Function>
void require_throws(Function&& function, const std::string& message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (...) {
        return;
    }
    throw std::runtime_error(message);
}


void prove_materialization_expansion_classifier_exhaustively() {
    using namespace anonsync;
    constexpr std::array<std::string_view, 5U> rule_paths{
        "archive", "media", "media/keep", "media/keep/private",
        "projects/current"};
    constexpr std::array<std::string_view, 12U> representative_paths{
        "outside/file", "archive", "archive/child", "media",
        "media/child", "media/keep", "media/keep/child",
        "media/keep/private", "media/keep/private/child", "projects",
        "projects/current", "projects/current/child"};

    std::vector<SyncReplicaSelectiveSyncPolicy> policies;
    policies.reserve(486U);
    for (const SyncReplicaSelectiveSyncMode default_mode : {
             SyncReplicaSelectiveSyncMode::Materialize,
             SyncReplicaSelectiveSyncMode::MetadataOnly}) {
        for (std::uint64_t encoded = 0U; encoded < 243U; ++encoded) {
            std::uint64_t digits = encoded;
            std::vector<SyncReplicaSelectiveSyncRule> rules;
            for (const std::string_view path : rule_paths) {
                const std::uint64_t digit = digits % 3U;
                digits /= 3U;
                if (digit == 0U) continue;
                rules.push_back(SyncReplicaSelectiveSyncRule{
                    std::string(path),
                    digit == 1U
                        ? SyncReplicaSelectiveSyncMode::Materialize
                        : SyncReplicaSelectiveSyncMode::MetadataOnly});
            }
            policies.push_back(
                make_sync_replica_selective_sync_policy_or_throw(
                    default_mode, std::move(rules), 1U));
        }
    }

    std::uint64_t compared_pairs = 0U;
    for (std::size_t before_index = 0U;
         before_index < policies.size(); ++before_index) {
        for (std::size_t after_index = 0U;
             after_index < policies.size(); ++after_index) {
            bool expected = false;
            for (const std::string_view path : representative_paths) {
                if (!sync_replica_selective_sync_path_is_materialized(
                        policies[before_index], path) &&
                    sync_replica_selective_sync_path_is_materialized(
                        policies[after_index], path)) {
                    expected = true;
                    break;
                }
            }
            const bool observed =
                sync_replica_selective_sync_policy_materializes_new_paths(
                    policies[before_index], policies[after_index]);
            if (observed != expected) {
                throw std::runtime_error(
                    "materialization expansion classifier disagreed at policy pair " +
                    std::to_string(before_index) + "/" +
                    std::to_string(after_index));
            }
            ++compared_pairs;
        }
    }
    require(
        policies.size() == 486U &&
            compared_pairs == 486U * 486U,
        "exhaustive bounded materialization classifier oracle was incomplete");
}

}  // namespace

int main() {
    using namespace anonsync;
    try {
        prove_materialization_expansion_classifier_exhaustively();

        const SyncReplicaSelectiveSyncPolicy all =
            sync_replica_default_selective_sync_policy();
        require(all.generation == 1U, "default generation mismatch");
        require(all.rules.empty(), "default rules are not empty");
        require(
            sync_replica_selective_sync_path_is_materialized(all, "media/a.mkv"),
            "default policy did not materialize a file");
        require(
            sync_replica_selective_sync_directory_may_contain_materialized_path(
                all, "media"),
            "default policy pruned a materialized directory");

        SyncReplicaSelectiveSyncPolicy policy =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::MetadataOnly,
                {{"media/private", SyncReplicaSelectiveSyncMode::MetadataOnly},
                 {"media", SyncReplicaSelectiveSyncMode::Materialize},
                 {"media/private/keep.mkv",
                  SyncReplicaSelectiveSyncMode::Materialize},
                 {"docs", SyncReplicaSelectiveSyncMode::MetadataOnly}},
                7U);
        require(policy.rules.front().canonical_path == "docs", "rules not sorted");
        require(policy.generation == 7U, "policy generation mismatch");
        validate_sync_replica_selective_sync_policy_or_throw(policy);
        require(
            sync_replica_selective_sync_path_is_materialized(
                policy, "media/movie.mkv"),
            "include prefix did not materialize child");
        require(
            !sync_replica_selective_sync_path_is_materialized(
                policy, "media/private/secret.mkv"),
            "deeper exclusion did not win");
        require(
            sync_replica_selective_sync_path_is_materialized(
                policy, "media/private/keep.mkv"),
            "exact deeper inclusion did not win");
        require(
            !sync_replica_selective_sync_path_is_materialized(
                policy, "other/file"),
            "default metadata-only mode was ignored");
        require(
            sync_replica_selective_sync_directory_may_contain_materialized_path(
                policy, "media/private"),
            "directory with deeper include was pruned");
        require(
            !sync_replica_selective_sync_directory_may_contain_materialized_path(
                policy, "docs"),
            "fully excluded directory was not prunable");
        require(
            sync_replica_selective_sync_directory_may_contain_materialized_path(
                policy, ""),
            "root with includes was pruned");

        const SyncReplicaSelectiveSyncPolicy adversarial_order =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::MetadataOnly,
                {{"a-archive", SyncReplicaSelectiveSyncMode::MetadataOnly},
                 {"a/keep", SyncReplicaSelectiveSyncMode::Materialize}},
                12U);
        require(
            sync_replica_selective_sync_directory_may_contain_materialized_path(
                adversarial_order, "a"),
            "lexically earlier sibling hid a deeper materialized descendant");

        const SyncReplicaSelectiveSyncPolicy semantically_same =
            make_sync_replica_selective_sync_policy_or_throw(
                policy.default_mode, policy.rules, 99U);
        require(
            sync_replica_selective_sync_policy_semantically_equal(
                policy, semantically_same),
            "semantic equality depended on generation");
        require(
            policy.policy_digest != semantically_same.policy_digest,
            "policy digest did not bind generation");
        require(
            !sync_replica_selective_sync_policy_materializes_new_paths(
                policy, semantically_same),
            "generation-only policy change was misclassified as expansion");

        const SyncReplicaSelectiveSyncPolicy narrowed =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::Materialize,
                {{"media", SyncReplicaSelectiveSyncMode::MetadataOnly}},
                8U);
        require(
            !sync_replica_selective_sync_policy_materializes_new_paths(
                all, narrowed),
            "pure selective-sync narrowing was classified as expansion");
        require(
            sync_replica_selective_sync_policy_materializes_new_paths(
                narrowed, all),
            "removing an exclusion did not classify materialization expansion");

        const SyncReplicaSelectiveSyncPolicy include_one =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::MetadataOnly,
                {{"media/keep",
                  SyncReplicaSelectiveSyncMode::Materialize}},
                9U);
        const SyncReplicaSelectiveSyncPolicy include_two =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::MetadataOnly,
                {{"docs", SyncReplicaSelectiveSyncMode::Materialize},
                 {"media/keep",
                  SyncReplicaSelectiveSyncMode::Materialize}},
                10U);
        require(
            sync_replica_selective_sync_policy_materializes_new_paths(
                include_one, include_two),
            "new materialized prefix was not classified as expansion");
        require(
            !sync_replica_selective_sync_policy_materializes_new_paths(
                include_two, include_one),
            "removed materialized prefix was classified as expansion");

        const SyncReplicaSelectiveSyncPolicy moved_boundary =
            make_sync_replica_selective_sync_policy_or_throw(
                SyncReplicaSelectiveSyncMode::Materialize,
                {{"media/private",
                  SyncReplicaSelectiveSyncMode::MetadataOnly}},
                11U);
        require(
            sync_replica_selective_sync_policy_materializes_new_paths(
                narrowed, moved_boundary),
            "moving an exclusion below its old boundary hid an expansion");

        require_throws(
            [] {
                (void)make_sync_replica_selective_sync_policy_or_throw(
                    SyncReplicaSelectiveSyncMode::Materialize,
                    {{"bad//path", SyncReplicaSelectiveSyncMode::MetadataOnly}});
            },
            "noncanonical rule was accepted");
        require_throws(
            [] {
                (void)make_sync_replica_selective_sync_policy_or_throw(
                    SyncReplicaSelectiveSyncMode::Materialize,
                    {{"same", SyncReplicaSelectiveSyncMode::Materialize},
                     {"same", SyncReplicaSelectiveSyncMode::MetadataOnly}});
            },
            "duplicate rule was accepted");
        require_throws(
            [] {
                std::vector<SyncReplicaSelectiveSyncRule> rules;
                rules.reserve(
                    static_cast<std::size_t>(
                        kSyncReplicaSelectiveSyncMaximumRules + 1U));
                for (std::uint64_t index = 0U;
                     index <= kSyncReplicaSelectiveSyncMaximumRules; ++index) {
                    rules.push_back(
                        {"x" + std::to_string(index),
                         SyncReplicaSelectiveSyncMode::Materialize});
                }
                (void)make_sync_replica_selective_sync_policy_or_throw(
                    SyncReplicaSelectiveSyncMode::MetadataOnly,
                    std::move(rules));
            },
            "rule-count overflow was accepted");

        std::cout << "sync replica selective-sync policy checks passed: "
                  << checks << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica selective-sync policy test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
