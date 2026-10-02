#include "iotox/agent_preflight.hpp"
#include "iotox/protected_state.hpp"

#include "iotox/route_store.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_policy_witness.hpp"
#include "iotox/terminal_profile.hpp"
#include "iotox/toxcore/dynamic_library.hpp"
#include "iotox/update_bundle.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <limits>
#include <optional>
#include <sstream>
#include <string_view>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox {
namespace {

enum class PathKind { regular, directory };

struct PathInspection {
    bool present{false};
    std::string state;
};

[[nodiscard]] Status path_status(std::string_view operation,
                                 const std::filesystem::path &path,
                                 int error_number = errno) {
    return Status{ErrorCode::io_error,
                  std::string(operation) + " '" + path.string() + "': " +
                      std::strerror(error_number)};
}

[[nodiscard]] bool normalized_absolute_nonroot(
    const std::filesystem::path &path) {
    return !path.empty() && path.is_absolute() && path != path.root_path() &&
           path.lexically_normal() == path;
}

[[nodiscard]] Result<PathInspection> inspect_managed_path(
    const std::filesystem::path &path, PathKind kind, bool private_owner,
    bool must_exist, std::string_view label) {
    if (!normalized_absolute_nonroot(path)) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) +
                          " path must be normalized, non-root, and absolute"};
    }
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) == 0) {
        const bool type_valid = kind == PathKind::regular
            ? S_ISREG(metadata.st_mode) && metadata.st_nlink == 1
            : S_ISDIR(metadata.st_mode);
        if (!type_valid ||
            (private_owner &&
             (metadata.st_uid != ::geteuid() ||
              (metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0U))) {
            return Status{
                ErrorCode::io_error,
                std::string(label) +
                    " has the wrong type, link count, ownership, or privacy mode"};
        }
        const int access_mode = kind == PathKind::regular ? R_OK : R_OK | X_OK;
        if (::access(path.c_str(), access_mode) != 0) {
            return path_status("unable to access " + std::string(label), path);
        }
        return PathInspection{true,
                              private_owner ? "present-private" : "present"};
    }
    if (errno != ENOENT) {
        return path_status("unable to inspect " + std::string(label), path);
    }
    if (must_exist) {
        return Status{ErrorCode::not_found,
                      std::string(label) + " does not exist: " + path.string()};
    }

    std::filesystem::path ancestor = path.parent_path();
    while (!ancestor.empty()) {
        struct stat ancestor_metadata {};
        if (::lstat(ancestor.c_str(), &ancestor_metadata) == 0) {
            if (!S_ISDIR(ancestor_metadata.st_mode) ||
                ::access(ancestor.c_str(), W_OK | X_OK) != 0) {
                return Status{
                    ErrorCode::io_error,
                    std::string(label) +
                        " has no writable existing directory ancestor"};
            }
            return PathInspection{false, "absent-will-create"};
        }
        if (errno != ENOENT) {
            return path_status("unable to inspect ancestor for " +
                                   std::string(label),
                               ancestor);
        }
        const std::filesystem::path next = ancestor.parent_path();
        if (next == ancestor) break;
        ancestor = next;
    }
    return Status{ErrorCode::io_error,
                  std::string(label) + " has no existing directory ancestor"};
}

[[nodiscard]] Status inspect_executable(
    const std::filesystem::path &path, std::string_view label) {
    auto inspected = inspect_managed_path(
        path, PathKind::regular, false, true, label);
    if (!inspected) return inspected.status();
    if (::access(path.c_str(), X_OK) != 0) {
        return path_status("configured executable is not executable", path);
    }
    return Status::success();
}

[[nodiscard]] Status inspect_directory(
    const std::filesystem::path &path, std::string_view label) {
    auto inspected = inspect_managed_path(
        path, PathKind::directory, false, true, label);
    return inspected ? Status::success() : inspected.status();
}

[[nodiscard]] Result<bool> path_present(
    const std::filesystem::path &path, std::string_view label) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) == 0) return true;
    if (errno == ENOENT) return false;
    return path_status("unable to inspect " + std::string(label), path);
}

[[nodiscard]] Status inspect_cgroup_root(
    const Agent::InteractiveConfig &config) {
    if (config.delegated_cgroup_root.empty()) return Status::success();
    auto root = inspect_managed_path(
        config.delegated_cgroup_root, PathKind::directory, false, true,
        "Ratox delegated cgroup root");
    if (!root) return root.status();
    struct statfs filesystem {};
    constexpr long kCgroup2Magic = 0x63677270L;
    if (::statfs(config.delegated_cgroup_root.c_str(), &filesystem) != 0 ||
        static_cast<long>(filesystem.f_type) != kCgroup2Magic) {
        return Status{ErrorCode::unsupported,
                      "Ratox delegated cgroup root is not cgroup v2"};
    }
    for (const std::string_view name : {"cgroup.procs",
                                        "cgroup.subtree_control"}) {
        if (::access((config.delegated_cgroup_root / name).c_str(), W_OK) !=
            0) {
            return Status{ErrorCode::io_error,
                          "Ratox cgroup delegation lacks a writable " +
                              std::string(name)};
        }
    }
    const auto require = [&config](std::string_view name, int mode) -> Status {
        const auto path = config.delegated_cgroup_root / name;
        if (::access(path.c_str(), mode) != 0) {
            return Status{ErrorCode::io_error,
                          "Ratox cgroup policy lacks required interface " +
                              std::string(name)};
        }
        return Status::success();
    };
    const auto &limits = config.cgroup_resource_limits;
    const auto &aggregate = config.cgroup_aggregate_limits;
    const auto &pressure = config.cgroup_pressure_admission_limits;
    if (limits.maximum_processes || aggregate.maximum_reserved_processes) {
        const Status status = require("pids.max", W_OK);
        if (!status.ok()) return status;
    }
    if (limits.maximum_memory_high_bytes) {
        const Status status = require("memory.high", W_OK);
        if (!status.ok()) return status;
    }
    if (limits.maximum_memory_bytes || aggregate.maximum_reserved_memory_bytes) {
        const Status status = require("memory.max", W_OK);
        if (!status.ok()) return status;
    }
    if (limits.maximum_swap_bytes || aggregate.maximum_reserved_swap_bytes) {
        const Status status = require("memory.swap.max", W_OK);
        if (!status.ok()) return status;
    }
    if (limits.cpu_quota_microseconds ||
        aggregate.maximum_reserved_cpu_quota_microseconds) {
        const Status status = require("cpu.max", W_OK);
        if (!status.ok()) return status;
    }
    if (limits.io_device) {
        const Status status = require("io.max", W_OK);
        if (!status.ok()) return status;
    }
    struct PressureInterface {
        bool configured;
        bool trigger;
        std::string_view name;
    };
    const std::array pressure_interfaces{
        PressureInterface{
            pressure.maximum_cpu_some_average_10_basis_points.has_value() ||
                pressure.cpu_some_trigger_stall_microseconds.has_value(),
            pressure.cpu_some_trigger_stall_microseconds.has_value(),
            "cpu.pressure"},
        PressureInterface{
            pressure.maximum_memory_full_average_10_basis_points.has_value() ||
                pressure.memory_full_trigger_stall_microseconds.has_value(),
            pressure.memory_full_trigger_stall_microseconds.has_value(),
            "memory.pressure"},
        PressureInterface{
            pressure.maximum_io_full_average_10_basis_points.has_value() ||
                pressure.io_full_trigger_stall_microseconds.has_value(),
            pressure.io_full_trigger_stall_microseconds.has_value(),
            "io.pressure"},
    };
    for (const PressureInterface &interface : pressure_interfaces) {
        if (!interface.configured) continue;
        const int mode = interface.trigger ? R_OK | W_OK : R_OK;
        const Status status = require(interface.name, mode);
        if (!status.ok()) return status;
    }
    return Status::success();
}

}  // namespace

Result<AgentPreflightReport> preflight_agent_config(
    const Agent::Config &config) {
    AgentPreflightReport report;
    report.network = config.transport.network.name();

    auto protected_inspection = protected_state::inspect(config);
    if (!protected_inspection) return protected_inspection.status();
    report.protected_state = protected_inspection.value().enabled
        ? "fscrypt-v2-policy=" +
              protected_inspection.value().policy_identifier +
              ",paths=" + std::to_string(
                  protected_inspection.value().configured_paths) +
              ",inodes=" + std::to_string(
                  protected_inspection.value().verified_inodes) +
              ",runtime=" +
              (protected_inspection.value().runtime_tmpfs
                   ? "tmpfs"
                   : "same-protected-root")
        : "disabled";

    auto toxcore = toxcore::DynamicToxcore::load(
        config.transport.toxcore_library);
    if (!toxcore) {
        return Status{toxcore.status().code(),
                      "unable to load configured c-toxcore provider: " +
                          toxcore.status().message()};
    }
    report.toxcore_provider = toxcore.value().version().str();
    auto sodium = security::Sodium::load(config.security.sodium_library);
    if (!sodium) {
        return Status{sodium.status().code(),
                      "unable to load configured libsodium provider: " +
                          sodium.status().message()};
    }
    report.sodium_provider = sodium.value().version();

    auto runtime = inspect_managed_path(
        config.runtime.root, PathKind::directory, true, false,
        "Agent runtime root");
    if (!runtime) return runtime.status();
    report.runtime = runtime.value().state;
    auto savedata = inspect_managed_path(
        config.transport.state_path, PathKind::regular, true, false,
        "Tox savedata");
    if (!savedata) return savedata.status();
    report.savedata = savedata.value().state;
    auto identity_path = inspect_managed_path(
        config.security.device_identity_path, PathKind::regular, true, false,
        "device identity");
    if (!identity_path) return identity_path.status();
    report.identity = identity_path.value().state;
    auto authority = inspect_managed_path(
        config.security.authority_ledger_path, PathKind::regular, true, false,
        "authority ledger");
    if (!authority) return authority.status();
    report.authority_ledger = authority.value().present
        ? "present-private-runtime-recovery-pending"
        : authority.value().state;
    report.authority_rollback_witness = "disabled";
    if (config.security.authority_rollback_witness &&
        config.security.authority_rollback_witness_service) {
        return Status{ErrorCode::invalid_argument,
                      "authority rollback witness injection and remote service are mutually exclusive"};
    }
    if (config.security.authority_rollback_witness) {
        if (!config.security.authority_rollback_witness
                 ->independently_controlled() &&
            !config.security.allow_non_independent_witness_for_testing) {
            return Status{
                ErrorCode::invalid_argument,
                "configured authority rollback witness is not independently controlled"};
        }
        report.authority_rollback_witness =
            config.security.authority_rollback_witness
                    ->independently_controlled()
                ? "independent-runtime-reconciliation-pending"
                : "test-only-same-domain-runtime-reconciliation-pending";
    } else if (config.security.authority_rollback_witness_service) {
        const auto &remote =
            *config.security.authority_rollback_witness_service;
        if (remote.endpoint.host.empty() || remote.endpoint.service.empty() ||
            remote.endpoint.timeout.count() <= 0 ||
            std::all_of(remote.service_key.begin(), remote.service_key.end(),
                        [](std::uint8_t byte) { return byte == 0U; }) ||
            std::all_of(remote.domain.begin(), remote.domain.end(),
                        [](std::uint8_t byte) { return byte == 0U; }) ||
            remote.domain !=
                config.security.authority_rollback_witness_domain ||
            remote.witness_epoch !=
                config.security.authority_rollback_witness_epoch ||
            remote.lane != rollback_witness::Lane::authority) {
            return Status{ErrorCode::invalid_argument,
                          "authority rollback witness service configuration is incomplete or inconsistent"};
        }
        report.authority_rollback_witness =
            "authenticated-remote-runtime-reconciliation-pending";
    }
    if ((config.security.witness_application_incarnation ||
         config.security.witness_ratox_incarnation ||
         config.security.witness_route_generation ||
         config.security.witness_terminal_policy ||
         config.security.witness_command_effects ||
         config.security.witness_sync_policy ||
         config.security.witness_update_lifecycle ||
         config.security.witness_sync_guarded_state) &&
        !config.security.authority_rollback_witness_service) {
        return Status{ErrorCode::invalid_argument,
                      "additional rollback-witness lanes require the authenticated remote witness service"};
    }
    if (config.security.witness_ratox_incarnation &&
        !config.interactive.enabled) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox incarnation witnessing requires an enabled Ratox host"};
    }
    if (config.security.witness_terminal_policy &&
        !config.interactive.enabled) {
        return Status{ErrorCode::invalid_argument,
                      "terminal-policy witnessing requires an enabled Ratox host"};
    }
    if (config.security.witness_application_incarnation) {
        report.authority_rollback_witness += "+application-incarnation";
    }
    if (config.security.witness_ratox_incarnation) {
        report.authority_rollback_witness += "+ratox-incarnation";
    }
    if (config.security.witness_route_generation) {
        if (config.security.route_set_path.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "route-generation witnessing requires a signed route set"};
        }
        report.authority_rollback_witness += "+route-generation";
    }
    if (config.security.witness_terminal_policy) {
        report.authority_rollback_witness += "+terminal-policy";
    }
    if (config.security.witness_command_effects) {
        report.authority_rollback_witness += "+command-effect";
        auto checkpoint = inspect_managed_path(
            config.security.command_effect_witness_checkpoint_path,
            PathKind::regular, true, false,
            "command effect witness checkpoint");
        if (!checkpoint) return checkpoint.status();
        auto intent = inspect_managed_path(
            config.security.command_effect_witness_intent_path,
            PathKind::regular, true, false,
            "command effect witness intent");
        if (!intent) return intent.status();
    }
    if (config.security.witness_sync_policy) {
        if (!config.sync.enabled || config.sync.policy_store_root.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "sync-policy witnessing requires enabled synchronization"};
        }
        report.authority_rollback_witness += "+sync-policy";
        auto checkpoint = inspect_managed_path(
            config.security.sync_policy_witness_checkpoint_path,
            PathKind::regular, true, false,
            "sync policy witness checkpoint");
        if (!checkpoint) return checkpoint.status();
        auto intent = inspect_managed_path(
            config.security.sync_policy_witness_intent_path,
            PathKind::regular, true, false,
            "sync policy witness intent");
        if (!intent) return intent.status();
    }
    if (config.security.witness_sync_guarded_state) {
        if (!config.security.witness_sync_policy || !config.sync.enabled) {
            return Status{
                ErrorCode::invalid_argument,
                "sync guarded-state witnessing requires witnessed sync policy"};
        }
        report.authority_rollback_witness += "+sync-guarded-state";
    }
    if (config.security.witness_update_lifecycle) {
        if (!config.update.enabled || config.update.policy_path.empty() ||
            config.security.update_lifecycle_witness_intent_path.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "update lifecycle witnessing requires enabled signed updates and an explicit intent path"};
        }
        report.authority_rollback_witness += "+update-lifecycle";
        auto intent = inspect_managed_path(
            config.security.update_lifecycle_witness_intent_path,
            PathKind::regular, true, false,
            "update lifecycle witness intent");
        if (!intent) return intent.status();
    }
    auto commands = inspect_managed_path(
        config.security.command_store_path, PathKind::regular, true, false,
        "durable command store");
    if (!commands) return commands.status();
    report.command_store = commands.value().present
        ? "present-private-runtime-recovery-pending"
        : commands.value().state;
    auto diagnostic_store = inspect_managed_path(
        config.security.diagnostics_store_path, PathKind::regular, true,
        false, "diagnostic flight recorder");
    if (!diagnostic_store) return diagnostic_store.status();
    report.diagnostics_store = diagnostic_store.value().state;
    auto alias_store = inspect_managed_path(
        config.security.peer_alias_store_path, PathKind::regular, true,
        false, "peer alias store");
    if (!alias_store) return alias_store.status();
    report.peer_alias_store = alias_store.value().state;
    auto protocol_incarnation = inspect_managed_path(
        config.security.protocol_incarnation_state_path, PathKind::regular,
        true, false, "application incarnation state");
    if (!protocol_incarnation) return protocol_incarnation.status();
    if (config.security.witness_application_incarnation) {
        auto intent = inspect_managed_path(
            config.security.application_incarnation_witness_intent_path,
            PathKind::regular, true, false,
            "application incarnation witness intent");
        if (!intent) return intent.status();
    }

    std::optional<security::DeviceIdentity> identity;
    if (identity_path.value().present) {
        auto loaded = security::DeviceIdentity::load(
            config.security.device_identity_path, sodium.value());
        if (!loaded) {
            return Status{loaded.status().code(),
                          "unable to verify configured device identity: " +
                              loaded.status().message()};
        }
        identity.emplace(std::move(loaded).value());
        report.identity = "present-private-verified";
    } else if (authority.value().present || commands.value().present ||
               diagnostic_store.value().present ||
               alias_store.value().present ||
               !config.security.route_set_path.empty()) {
        return Status{ErrorCode::not_found,
                      "existing authority, command, diagnostics, aliases, or route state requires an existing device identity"};
    }

    if (diagnostic_store.value().present) {
        diagnostics::Recorder::Config recorder_config;
        recorder_config.path = config.security.diagnostics_store_path;
        recorder_config.maximum_records =
            config.security.maximum_diagnostics_records;
        auto recorder = diagnostics::Recorder::open(
            std::move(recorder_config), *identity, sodium.value());
        if (!recorder) {
            return Status{recorder.status().code(),
                          "unable to verify diagnostic flight recorder: " +
                              recorder.status().message()};
        }
        const auto diagnostic_snapshot = recorder.value()->snapshot();
        report.diagnostics_store = "signed-verified-records=" +
            std::to_string(diagnostic_snapshot.records.size()) +
            ",evicted=" +
            std::to_string(diagnostic_snapshot.evicted_records);
    }

    if (alias_store.value().present) {
        peer_alias::Store::Config alias_config;
        alias_config.path = config.security.peer_alias_store_path;
        auto aliases = peer_alias::Store::open(
            std::move(alias_config), *identity, sodium.value());
        if (!aliases) {
            return Status{aliases.status().code(),
                          "unable to verify peer alias store: " +
                              aliases.status().message()};
        }
        const auto alias_snapshot = aliases.value()->snapshot();
        report.peer_alias_store = "signed-verified-generation=" +
            std::to_string(alias_snapshot.generation) + ",entries=" +
            std::to_string(alias_snapshot.entries.size());
    }

    report.route_inventory = "disabled";
    if (!config.security.route_set_path.empty()) {
        auto artifact = inspect_managed_path(
            config.security.route_set_path, PathKind::regular, true, true,
            "route-set artifact");
        if (!artifact) return artifact.status();
        routes::RouteSetStore::Config route_config;
        route_config.artifact_path = config.security.route_set_path;
        route_config.generation_state_path =
            config.security.route_generation_state_path;
        auto inspected = routes::RouteSetStore::inspect(
            std::move(route_config), *identity, sodium.value());
        if (!inspected) {
            return Status{inspected.status().code(),
                          "unable to verify configured route inventory: " +
                              inspected.status().message()};
        }
        report.route_inventory = "signed-verified-generation=" +
            std::to_string(inspected.value().route_set.generation) +
            ",members=" +
            std::to_string(inspected.value().route_set.members.size());
        if (config.security.witness_route_generation) {
            auto intent = inspect_managed_path(
                config.security.route_generation_witness_intent_path,
                PathKind::regular, true, false,
                "route generation witness intent");
            if (!intent) return intent.status();
            report.route_inventory += ",witness=pending-runtime-reconciliation";
        }
    }
    if (config.security.route_workers_enabled) {
        auto workers = inspect_managed_path(
            config.security.route_worker_state_root, PathKind::directory,
            true, false, "route worker state root");
        if (!workers) return workers.status();
    }

    std::vector<sync::NamespacePolicy> policies;
    report.synchronization = "disabled";
    if (config.sync.enabled) {
        auto root = inspect_managed_path(
            config.sync.policy_store_root, PathKind::directory, true, false,
            "synchronization policy root");
        if (!root) return root.status();
        if (root.value().present) {
            const auto namespace_directory =
                config.sync.policy_store_root / "namespaces";
            auto namespace_present = path_present(
                namespace_directory, "synchronization namespace index");
            if (!namespace_present) return namespace_present.status();
            if (namespace_present.value()) {
                auto loaded = sync::load_namespace_store(
                    config.sync.policy_store_root,
                    static_cast<std::uint32_t>(::geteuid()));
                if (!loaded) {
                    return Status{
                        loaded.status().code(),
                        "unable to inspect synchronization policy store: " +
                            loaded.status().message()};
                }
                policies = std::move(loaded).value();
                report.synchronization = "policy-store-verified";
                if (config.security.witness_sync_policy) {
                    if (!identity) {
                        return Status{ErrorCode::not_found,
                                      "witnessed sync policy requires an existing device identity"};
                    }
                    auto tree = sync::load_sync_policy_tree(
                        config.sync.policy_store_root,
                        static_cast<std::uint32_t>(::geteuid()),
                        identity.value().public_key(), sodium.value());
                    if (!tree) return tree.status();
                    auto digest = sync::sync_policy_tree_digest(
                        tree.value(), sodium.value());
                    if (!digest) return digest.status();
                    report.synchronization +=
                        "-witness-runtime-reconciliation-pending";
                }
                if (config.security.witness_sync_guarded_state) {
                    report.synchronization +=
                        "-guarded-state-runtime-reconciliation-pending";
                }
            } else {
                if (config.security.witness_sync_policy) {
                    return Status{ErrorCode::not_found,
                                  "witnessed sync policy requires an existing namespace index"};
                }
                report.synchronization =
                    "empty-policy-index-will-create";
            }
        } else {
            if (config.security.witness_sync_policy) {
                return Status{ErrorCode::not_found,
                              "witnessed sync policy requires an existing policy store"};
            }
            report.synchronization = "empty-policy-store-will-create";
        }
        report.namespaces = policies.size();
    }

    report.signed_updates = "disabled";
    if (config.update.enabled) {
        auto policy = update::load_update_policy(
            config.update.policy_path,
            static_cast<std::uint32_t>(::geteuid()));
        if (!policy) {
            return Status{policy.status().code(),
                          "unable to inspect signed-update policy: " +
                              policy.status().message()};
        }
        const auto selected = std::find_if(
            policies.begin(), policies.end(), [&](const auto &candidate) {
                return candidate.id == policy.value().namespace_id;
            });
        if (selected == policies.end() ||
            selected->engine != sync::Engine::range_v1) {
            return Status{ErrorCode::invalid_argument,
                          "signed-update policy requires one configured range-v1 namespace"};
        }
        const bool linux_service = policy.value().payload_kind ==
            update::PayloadKind::linux_service_v1;
        if (linux_service != config.update.linux_service_enabled) {
            return Status{ErrorCode::invalid_argument,
                          "signed-update payload kind and Linux service adapter activation differ"};
        }
        if (linux_service) {
            const Status helper = inspect_executable(
                config.update.service_helper_executable,
                "signed-update service helper");
            if (!helper.ok()) return helper;
        }
        report.signed_updates = "policy-verified-runtime-recovery-pending";
    }

    report.ratox = config.interactive.client_enabled
        ? "client-ready"
        : "disabled";
    report.cgroup = "disabled";
    report.kernel_child_confinement = "not-requested";
    if (config.interactive.enabled) {
        const std::uint64_t effective_uid =
            static_cast<std::uint64_t>(::geteuid());
        if (effective_uid > std::numeric_limits<std::uint32_t>::max()) {
            return Status{ErrorCode::unsupported,
                          "effective UID does not fit terminal profile records"};
        }
        const std::uint32_t expected_uid =
            config.interactive.expected_profile_owner_uid.value_or(
                static_cast<std::uint32_t>(effective_uid));
        auto store = terminal::load_profile_store(
            config.interactive.profile_store_root, expected_uid);
        if (!store) {
            return Status{store.status().code(),
                          "unable to inspect Ratox profile store: " +
                              store.status().message()};
        }
        terminal::ProfileRegistry registry;
        const Status installed = registry.replace(store.value());
        if (!installed.ok()) return installed;
        const auto snapshot = registry.snapshot();
        if (snapshot.enabled_profiles == 0U ||
            snapshot.enabled_bindings == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox host requires an enabled profile and binding"};
        }
        const Status helper = inspect_executable(
            config.interactive.helper_executable, "Ratox PTY helper");
        if (!helper.ok()) return helper;
        for (const terminal::Profile &profile : store.value().profiles) {
            if (!profile.enabled) continue;
            const Status executable = inspect_executable(
                std::filesystem::path{profile.arguments.front()},
                "Ratox profile executable");
            if (!executable.ok()) return executable;
            const Status working = inspect_directory(
                std::filesystem::path{profile.working_directory},
                "Ratox profile working directory");
            if (!working.ok()) return working;
            auto effective = terminal::compose_cgroup_resource_limits(
                config.interactive.cgroup_resource_limits,
                profile.cgroup_limits);
            if (!effective) return effective.status();
            const Status aggregate =
                terminal::validate_cgroup_aggregate_reservation(
                    config.interactive.cgroup_aggregate_limits,
                    effective.value());
            if (!aggregate.ok()) return aggregate;
            if (config.interactive.delegated_cgroup_root.empty() &&
                !effective.value().empty()) {
                return Status{ErrorCode::invalid_argument,
                              "enabled Ratox profile requires an explicit cgroup root"};
            }
        }
        const Status cgroup = inspect_cgroup_root(config.interactive);
        if (!cgroup.ok()) return cgroup;
        if (!config.interactive.delegated_cgroup_root.empty()) {
            report.cgroup = "delegation-interfaces-readable-no-probe-leaf";
        }
        auto incarnation = inspect_managed_path(
            config.interactive.incarnation_state_path, PathKind::regular,
            true, false, "Ratox host incarnation state");
        if (!incarnation) return incarnation.status();
        if (config.security.witness_ratox_incarnation) {
            auto intent = inspect_managed_path(
                config.security.ratox_incarnation_witness_intent_path,
                PathKind::regular, true, false,
                "Ratox incarnation witness intent");
            if (!intent) return intent.status();
        }
        if (config.security.witness_terminal_policy) {
            auto checkpoint = inspect_managed_path(
                config.security.terminal_policy_witness_checkpoint_path,
                PathKind::regular, true, false,
                "terminal policy witness checkpoint");
            if (!checkpoint) return checkpoint.status();
            auto intent = inspect_managed_path(
                config.security.terminal_policy_witness_intent_path,
                PathKind::regular, true, false,
                "terminal policy witness intent");
            if (!intent) return intent.status();
            auto digest = terminal::profile_store_digest(
                store.value(), sodium.value());
            if (!digest) return digest.status();
        }
        report.ratox = config.interactive.client_enabled
            ? "host-and-client-policy-verified"
            : "host-policy-verified";
        if (config.security.witness_terminal_policy) {
            report.ratox += "-witness-runtime-reconciliation-pending";
        }
        report.kernel_child_confinement =
            "deferred-to-production-pty-child";
        report.terminal_profiles = snapshot.enabled_profiles;
        report.terminal_bindings = snapshot.enabled_bindings;
    }
    return report;
}

std::string render_agent_preflight_report(
    const AgentPreflightReport &report, bool file_backed) {
    std::ostringstream output;
    output << "iotox-run-check-v1\n"
           << "decision=ready-for-start\n"
           << "source=" << (file_backed ? "config+overrides" : "command-line")
           << '\n'
           << "network=" << report.network << '\n'
           << "toxcore-provider=" << report.toxcore_provider << '\n'
           << "sodium-provider=" << report.sodium_provider << '\n'
           << "runtime=" << report.runtime << '\n'
           << "protected-state=" << report.protected_state << '\n'
           << "savedata=" << report.savedata << '\n'
           << "identity=" << report.identity << '\n'
           << "authority-ledger=" << report.authority_ledger << '\n'
           << "authority-rollback-witness="
           << report.authority_rollback_witness << '\n'
           << "command-store=" << report.command_store << '\n'
           << "diagnostics-store=" << report.diagnostics_store << '\n'
           << "peer-alias-store=" << report.peer_alias_store << '\n'
           << "route-inventory=" << report.route_inventory << '\n'
           << "synchronization=" << report.synchronization << '\n'
           << "namespaces=" << report.namespaces << '\n'
           << "signed-updates=" << report.signed_updates << '\n'
           << "ratox=" << report.ratox << '\n'
           << "terminal-profiles=" << report.terminal_profiles << '\n'
           << "terminal-bindings=" << report.terminal_bindings << '\n'
           << "cgroup=" << report.cgroup << '\n'
           << "kernel-child-confinement="
           << report.kernel_child_confinement << '\n'
           << "durable-recovery=deferred-to-run\n"
           << "mutation=none\n";
    return output.str();
}

}  // namespace iotox
