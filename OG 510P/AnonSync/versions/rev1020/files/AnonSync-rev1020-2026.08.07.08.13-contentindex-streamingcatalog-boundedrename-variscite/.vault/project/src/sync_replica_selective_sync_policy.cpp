#include "sync_replica_selective_sync_policy.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kPolicyDigestDomain =
    "anonsync:sync-replica-selective-sync-policy:v1";

[[nodiscard]] bool mode_is_known(SyncReplicaSelectiveSyncMode mode) noexcept {
    return mode == SyncReplicaSelectiveSyncMode::Materialize ||
           mode == SyncReplicaSelectiveSyncMode::MetadataOnly;
}

void append_u64(std::string& output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
    }
}

void append_framed(std::string& output, std::string_view value) {
    append_u64(output, static_cast<std::uint64_t>(value.size()));
    output.append(value);
}

[[nodiscard]] std::string policy_digest_or_throw(
    std::uint64_t generation,
    SyncReplicaSelectiveSyncMode default_mode,
    const std::vector<SyncReplicaSelectiveSyncRule>& rules,
    std::uint64_t path_bytes) {
    std::string canonical;
    canonical.reserve(
        kPolicyDigestDomain.size() + 1U + 8U + 8U + 8U +
        static_cast<std::size_t>(path_bytes) + rules.size() * 16U);
    canonical.append(kPolicyDigestDomain);
    canonical.push_back('\0');
    append_u64(canonical, generation);
    append_u64(canonical, static_cast<std::uint64_t>(default_mode));
    append_u64(canonical, static_cast<std::uint64_t>(rules.size()));
    append_u64(canonical, path_bytes);
    for (const SyncReplicaSelectiveSyncRule& rule : rules) {
        append_framed(canonical, rule.canonical_path);
        append_u64(canonical, static_cast<std::uint64_t>(rule.mode));
    }
    return sha256_hex(canonical);
}

[[nodiscard]] bool path_has_component_prefix(
    std::string_view path,
    std::string_view prefix) noexcept {
    return path == prefix ||
           (path.size() > prefix.size() && path.starts_with(prefix) &&
            path[prefix.size()] == '/');
}

// Compare one rule path with the virtual key `directory/` without allocating
// that slash-suffixed string. This keeps unrelated lexical siblings from
// hiding a real descendant rule in lower_bound.
[[nodiscard]] bool path_is_less_than_descendant_prefix(
    std::string_view path,
    std::string_view canonical_directory) noexcept {
    const std::size_t common = std::min(
        path.size(), canonical_directory.size());
    const int prefix_compare = path.compare(
        0U, common, canonical_directory, 0U, common);
    if (prefix_compare != 0) return prefix_compare < 0;
    if (path.size() <= canonical_directory.size()) return true;
    return static_cast<unsigned char>(path[canonical_directory.size()]) <
           static_cast<unsigned char>('/');
}

[[nodiscard]] const SyncReplicaSelectiveSyncRule* exact_rule_or_none(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view path) noexcept {
    const auto found = std::lower_bound(
        policy.rules.begin(), policy.rules.end(), path,
        [](const SyncReplicaSelectiveSyncRule& rule, std::string_view value) {
            return rule.canonical_path < value;
        });
    if (found == policy.rules.end() || found->canonical_path != path) {
        return nullptr;
    }
    return &*found;
}

[[nodiscard]] SyncReplicaSelectiveSyncMode mode_for_valid_path(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_path) noexcept {
    std::string_view candidate = canonical_path;
    for (;;) {
        if (const SyncReplicaSelectiveSyncRule* rule =
                exact_rule_or_none(policy, candidate);
            rule != nullptr) {
            return rule->mode;
        }
        const std::size_t separator = candidate.rfind('/');
        if (separator == std::string_view::npos) break;
        candidate = candidate.substr(0U, separator);
    }
    return policy.default_mode;
}

void validate_canonical_rule_path_or_throw(
    std::string_view path,
    std::string_view label) {
    const SyncValidationResult validated = validate_sync_relative_path(path);
    if (!validated.ok) {
        throw std::invalid_argument(
            std::string(label) + " rule path is not canonical: " +
            validated.reason);
    }
}

}  // namespace

SyncReplicaSelectiveSyncMode
sync_replica_selective_sync_mode_from_name_or_throw(std::string_view name) {
    if (name == "materialize") {
        return SyncReplicaSelectiveSyncMode::Materialize;
    }
    if (name == "metadata_only") {
        return SyncReplicaSelectiveSyncMode::MetadataOnly;
    }
    throw std::invalid_argument(
        "selective-sync mode must be materialize or metadata_only");
}

SyncReplicaSelectiveSyncPolicy
make_sync_replica_selective_sync_policy_or_throw(
    SyncReplicaSelectiveSyncMode default_mode,
    std::vector<SyncReplicaSelectiveSyncRule> rules,
    std::uint64_t generation) {
    if (generation == 0U) {
        throw std::invalid_argument(
            "sync replica selective-sync policy generation must be positive");
    }
    if (!mode_is_known(default_mode)) {
        throw std::invalid_argument(
            "sync replica selective-sync policy default mode is unknown");
    }
    if (rules.size() > kSyncReplicaSelectiveSyncMaximumRules) {
        throw std::length_error(
            "sync replica selective-sync policy exceeds the rule limit");
    }
    for (const SyncReplicaSelectiveSyncRule& rule : rules) {
        validate_canonical_rule_path_or_throw(
            rule.canonical_path, "sync replica selective-sync policy");
        if (!mode_is_known(rule.mode)) {
            throw std::invalid_argument(
                "sync replica selective-sync policy rule mode is unknown");
        }
    }
    std::sort(
        rules.begin(), rules.end(),
        [](const SyncReplicaSelectiveSyncRule& left,
           const SyncReplicaSelectiveSyncRule& right) {
            return left.canonical_path < right.canonical_path;
        });
    std::uint64_t path_bytes = 0U;
    std::string_view previous;
    for (const SyncReplicaSelectiveSyncRule& rule : rules) {
        if (!previous.empty() && rule.canonical_path == previous) {
            throw std::invalid_argument(
                "sync replica selective-sync policy contains duplicate rule paths");
        }
        if (rule.canonical_path.size() >
            kSyncReplicaSelectiveSyncMaximumRulePathBytes - path_bytes) {
            throw std::length_error(
                "sync replica selective-sync policy exceeds the rule-path byte limit");
        }
        path_bytes += static_cast<std::uint64_t>(rule.canonical_path.size());
        previous = rule.canonical_path;
    }

    SyncReplicaSelectiveSyncPolicy policy;
    policy.generation = generation;
    policy.default_mode = default_mode;
    policy.rules = std::move(rules);
    policy.rule_path_bytes = path_bytes;
    policy.policy_digest = policy_digest_or_throw(
        policy.generation, policy.default_mode, policy.rules,
        policy.rule_path_bytes);
    return policy;
}

SyncReplicaSelectiveSyncPolicy sync_replica_default_selective_sync_policy() {
    return make_sync_replica_selective_sync_policy_or_throw(
        SyncReplicaSelectiveSyncMode::Materialize, {}, 1U);
}

void validate_sync_replica_selective_sync_policy_or_throw(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view label_view) {
    const std::string label = label_view.empty()
        ? "sync replica selective-sync policy"
        : std::string(label_view);
    if (policy.generation == 0U) {
        throw std::invalid_argument(label + " generation must be positive");
    }
    if (!mode_is_known(policy.default_mode)) {
        throw std::invalid_argument(label + " default mode is unknown");
    }
    if (policy.rules.size() > kSyncReplicaSelectiveSyncMaximumRules) {
        throw std::length_error(label + " exceeds the rule limit");
    }
    std::uint64_t path_bytes = 0U;
    std::string_view previous;
    for (const SyncReplicaSelectiveSyncRule& rule : policy.rules) {
        validate_canonical_rule_path_or_throw(rule.canonical_path, label);
        if (!mode_is_known(rule.mode)) {
            throw std::invalid_argument(label + " rule mode is unknown");
        }
        if (!previous.empty() && rule.canonical_path <= previous) {
            throw std::invalid_argument(
                label + " rules are not strictly sorted and unique");
        }
        if (rule.canonical_path.size() >
            kSyncReplicaSelectiveSyncMaximumRulePathBytes - path_bytes) {
            throw std::length_error(label + " exceeds the rule-path byte limit");
        }
        path_bytes += static_cast<std::uint64_t>(rule.canonical_path.size());
        previous = rule.canonical_path;
    }
    if (path_bytes != policy.rule_path_bytes) {
        throw std::invalid_argument(label + " rule-path byte count is not exact");
    }
    if (!is_lowercase_sha256_hex(policy.policy_digest) ||
        policy.policy_digest != policy_digest_or_throw(
            policy.generation, policy.default_mode, policy.rules,
            policy.rule_path_bytes)) {
        throw std::invalid_argument(label + " digest is invalid");
    }
}

bool sync_replica_selective_sync_policy_semantically_equal(
    const SyncReplicaSelectiveSyncPolicy& left,
    const SyncReplicaSelectiveSyncPolicy& right) noexcept {
    return left.default_mode == right.default_mode &&
           left.rules == right.rules;
}

bool sync_replica_selective_sync_policy_materializes_new_paths(
    const SyncReplicaSelectiveSyncPolicy& before,
    const SyncReplicaSelectiveSyncPolicy& after) {
    validate_sync_replica_selective_sync_policy_or_throw(
        before, "selective-sync prior policy");
    validate_sync_replica_selective_sync_policy_or_throw(
        after, "selective-sync successor policy");

    // Longest-prefix policies are piecewise constant. Outside every explicit
    // rule boundary, only the default applies; every other semantic transition
    // starts at a rule path from one of the two policies. Comparing the finite union
    // is therefore complete without enumerating any catalog or tree path.
    if (before.default_mode == SyncReplicaSelectiveSyncMode::MetadataOnly &&
        after.default_mode == SyncReplicaSelectiveSyncMode::Materialize) {
        return true;
    }

    std::size_t before_index = 0U;
    std::size_t after_index = 0U;
    while (before_index < before.rules.size() ||
           after_index < after.rules.size()) {
        std::string_view boundary;
        if (after_index >= after.rules.size() ||
            (before_index < before.rules.size() &&
             before.rules[before_index].canonical_path <
                 after.rules[after_index].canonical_path)) {
            boundary = before.rules[before_index++].canonical_path;
        } else if (
            before_index >= before.rules.size() ||
            after.rules[after_index].canonical_path <
                before.rules[before_index].canonical_path) {
            boundary = after.rules[after_index++].canonical_path;
        } else {
            boundary = before.rules[before_index].canonical_path;
            ++before_index;
            ++after_index;
        }

        if (mode_for_valid_path(before, boundary) ==
                SyncReplicaSelectiveSyncMode::MetadataOnly &&
            mode_for_valid_path(after, boundary) ==
                SyncReplicaSelectiveSyncMode::Materialize) {
            return true;
        }
    }
    return false;
}

SyncReplicaSelectiveSyncMode sync_replica_selective_sync_mode_for_path(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_path) {
    const SyncValidationResult validated =
        validate_sync_relative_path(canonical_path);
    if (!validated.ok) {
        throw std::invalid_argument(
            "selective-sync path is not canonical: " + validated.reason);
    }

    return mode_for_valid_path(policy, canonical_path);
}

bool sync_replica_selective_sync_path_is_materialized(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_path) {
    return sync_replica_selective_sync_mode_for_path(policy, canonical_path) ==
           SyncReplicaSelectiveSyncMode::Materialize;
}

bool sync_replica_selective_sync_directory_may_contain_materialized_path(
    const SyncReplicaSelectiveSyncPolicy& policy,
    std::string_view canonical_directory) {
    if (!canonical_directory.empty()) {
        const SyncValidationResult validated =
            validate_sync_relative_path(canonical_directory);
        if (!validated.ok) {
            throw std::invalid_argument(
                "selective-sync directory is not canonical: " +
                validated.reason);
        }
        if (sync_replica_selective_sync_path_is_materialized(
                policy, canonical_directory)) {
            return true;
        }
    } else if (policy.default_mode ==
               SyncReplicaSelectiveSyncMode::Materialize) {
        return true;
    }

    auto found = canonical_directory.empty()
        ? policy.rules.begin()
        : std::lower_bound(
              policy.rules.begin(), policy.rules.end(), canonical_directory,
              [](const SyncReplicaSelectiveSyncRule& rule,
                 std::string_view directory) {
                  return path_is_less_than_descendant_prefix(
                      rule.canonical_path, directory);
              });
    for (; found != policy.rules.end(); ++found) {
        if (!canonical_directory.empty() &&
            !path_has_component_prefix(
                found->canonical_path, canonical_directory)) {
            break;
        }
        if (found->mode == SyncReplicaSelectiveSyncMode::Materialize &&
            (canonical_directory.empty() ||
             path_has_component_prefix(
                 found->canonical_path, canonical_directory))) {
            return true;
        }
    }
    return false;
}

}  // namespace anonsync
