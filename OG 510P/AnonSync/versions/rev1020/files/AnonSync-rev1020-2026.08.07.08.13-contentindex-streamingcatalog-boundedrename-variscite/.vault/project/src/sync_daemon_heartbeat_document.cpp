#include "sync_daemon_heartbeat_document.hpp"

#include "anonsync_json_value.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::uint64_t kMaximumExactJsonInteger = 9007199254740991ULL;
constexpr std::string_view kFormatV1 =
    "anonsync-sync-daemon-service-heartbeat-v1";
constexpr std::string_view kFormatV2 =
    "anonsync-sync-daemon-service-heartbeat-v2";
constexpr std::string_view kOperation = "sync-daemon-service-heartbeat";
constexpr std::string_view kServiceInstancePrefix =
    "sync-daemon-service-instance:v1:";
constexpr std::string_view kOwnerLockPrefix =
    "sync-resume-daemon-owner-lock:v1:";

[[nodiscard]] bool ascii_lower_alnum(char c) noexcept {
    return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

[[nodiscard]] bool valid_portable_sync_id(const std::string& value) noexcept {
    if (value.empty() || value.size() > 128) return false;
    if (!ascii_lower_alnum(value.front()) ||
        !ascii_lower_alnum(value.back())) {
        return false;
    }
    for (char c : value) {
        if (ascii_lower_alnum(c) || c == '.' || c == '_' || c == '-') {
            continue;
        }
        return false;
    }
    return true;
}

[[nodiscard]] bool lowercase_hex_digest_with_prefix(
    const std::string& value,
    std::string_view prefix) noexcept {
    if (!value.starts_with(prefix) || value.size() != prefix.size() + 64) {
        return false;
    }
    return std::all_of(value.begin() + static_cast<std::ptrdiff_t>(prefix.size()),
                       value.end(),
                       [](char c) {
                           return (c >= '0' && c <= '9') ||
                                  (c >= 'a' && c <= 'f');
                       });
}

[[nodiscard]] bool valid_revision_id(const std::string& value) noexcept {
    return value.size() == 7 && value.starts_with("rev") &&
           std::all_of(value.begin() + 3, value.end(), [](char c) {
               return c >= '0' && c <= '9';
           });
}

[[nodiscard]] bool final_state(const std::string& state) noexcept {
    return state == "completed" || state == "failed" ||
           state == "failed-exception";
}

[[nodiscard]] bool nonfinal_state(const std::string& state) noexcept {
    static constexpr std::array<std::string_view, 16> kStates = {
        "owner-lock-acquired",
        "owner-lock-not-required",
        "terminal-apply-completed",
        "terminal-conflict-apply-completed",
        "terminal-conflict-file-apply-completed",
        "terminal-conflict-file-transfer-staged",
        "startup-sidecar-recovery-completed",
        "startup-sidecar-recovery-incomplete",
        "scheduler-pass",
        "scheduler-pass-started",
        "scheduler-pass-completed",
        "scheduler-pass-terminal-review-fenced",
        "completed-owner-lock-retained",
        "failed-owner-lock-retained",
        "failed-exception-owner-lock-retained",
        "service-running",
    };
    return std::find(kStates.begin(), kStates.end(), state) != kStates.end();
}

void require_exact_json_u64(std::uint64_t value, const std::string& label) {
    if (value > kMaximumExactJsonInteger) {
        throw std::runtime_error(label +
                                 " exceeds the exact interoperable JSON integer range");
    }
}

[[nodiscard]] const Json& require_object_field(const Json& object,
                                               std::string_view key,
                                               std::string_view label) {
    const auto found = object.o.find(std::string(key));
    if (found == object.o.end() || !found->second.is_object()) {
        throw std::runtime_error(std::string(label) +
                                 " must contain object field " +
                                 std::string(key));
    }
    return found->second;
}

[[nodiscard]] std::string require_string_field(const Json& object,
                                               const std::string& key,
                                               const std::string& label,
                                               bool allow_empty = false) {
    const Json& field = object.at(key);
    if (!field.is_string()) {
        throw std::runtime_error(label + " field " + key +
                                 " is missing or not a string");
    }
    if (!allow_empty && field.s.empty()) {
        throw std::runtime_error(label + " field " + key + " is empty");
    }
    return field.s;
}

[[nodiscard]] bool require_bool_field(const Json& object,
                                      const std::string& key,
                                      const std::string& label) {
    const Json& field = object.at(key);
    if (!field.is_bool()) {
        throw std::runtime_error(label + " field " + key +
                                 " is missing or not boolean");
    }
    return field.b;
}

[[nodiscard]] std::uint64_t require_u64_field(const Json& object,
                                              const std::string& key,
                                              const std::string& label) {
    const Json& field = object.at(key);
    if (!field.is_number()) {
        throw std::runtime_error(label + " field " + key +
                                 " is missing or not numeric");
    }
    long long value = -1;
    try {
        value = field.integer(-1);
    } catch (const std::exception& error) {
        throw std::runtime_error(label + " field " + key +
                                 " is not an exact nonnegative integer: " +
                                 error.what());
    }
    if (value < 0) {
        throw std::runtime_error(label + " field " + key +
                                 " must be nonnegative");
    }
    return static_cast<std::uint64_t>(value);
}

void validate_sync_daemon_heartbeat_document_or_throw(
    const SyncDaemonHeartbeatDocument& document) {
    const bool format_v1 = document.format == kFormatV1;
    const bool format_v2 = document.format == kFormatV2;
    if (!format_v1 && !format_v2) {
        throw std::runtime_error("sync daemon heartbeat format marker mismatch");
    }
    if (!valid_revision_id(document.revision_id)) {
        throw std::runtime_error(
            "sync daemon heartbeat revision_id must be rev followed by four digits");
    }
    if (document.operation != kOperation) {
        throw std::runtime_error("sync daemon heartbeat operation marker mismatch");
    }
    if (!lowercase_hex_digest_with_prefix(document.service_instance_id,
                                          kServiceInstancePrefix)) {
        throw std::runtime_error(
            "sync daemon heartbeat service_instance_id is not canonical");
    }
    require_exact_json_u64(document.service_restart_epoch,
                           "sync daemon heartbeat service_restart_epoch");
    if (document.service_restart_epoch == 0) {
        throw std::runtime_error(
            "sync daemon heartbeat service_restart_epoch must be positive");
    }
    if (document.reason.empty()) {
        throw std::runtime_error("sync daemon heartbeat reason is empty");
    }
    if (document.final) {
        if (!final_state(document.state)) {
            throw std::runtime_error(
                "sync daemon heartbeat final flag contradicts its state");
        }
    } else if (!nonfinal_state(document.state)) {
        throw std::runtime_error(
            "sync daemon heartbeat non-final state is not recognized");
    }

    require_exact_json_u64(document.heartbeat_epoch,
                           "sync daemon heartbeat heartbeat_epoch");
    require_exact_json_u64(document.stale_after_seconds,
                           "sync daemon heartbeat stale_after_seconds");
    require_exact_json_u64(document.stale_at_epoch,
                           "sync daemon heartbeat stale_at_epoch");
    require_exact_json_u64(document.process_id,
                           "sync daemon heartbeat process_id");
    if (format_v2) {
        if (!document.process_identity_present) {
            throw std::runtime_error(
                "sync daemon heartbeat v2 requires process_incarnation evidence");
        }
        validate_sync_process_identity_observation_or_throw(
            document.process_identity);
        if (document.process_identity.process_id != document.process_id) {
            throw std::runtime_error(
                "sync daemon heartbeat process_id does not match process_incarnation");
        }
    } else if (document.process_identity_present ||
               !document.process_identity.format.empty() ||
               document.process_identity.process_id != 0 ||
               !document.process_identity.boot_id.empty() ||
               !document.process_identity.start_token.empty()) {
        throw std::runtime_error(
            "sync daemon heartbeat v1 cannot contain process_incarnation fields");
    }
    if (document.heartbeat_epoch == 0) {
        throw std::runtime_error(
            "sync daemon heartbeat heartbeat_epoch must be positive");
    }
    if (document.stale_after_seconds == 0) {
        if (document.stale_at_epoch != 0) {
            throw std::runtime_error(
                "sync daemon heartbeat zero stale_after_seconds requires zero stale_at_epoch");
        }
    } else {
        if (document.heartbeat_epoch >
            kMaximumExactJsonInteger - document.stale_after_seconds) {
            throw std::runtime_error(
                "sync daemon heartbeat stale horizon exceeds exact JSON range");
        }
        if (document.stale_at_epoch !=
            document.heartbeat_epoch + document.stale_after_seconds) {
            throw std::runtime_error(
                "sync daemon heartbeat stale_at_epoch does not equal heartbeat_epoch plus stale_after_seconds");
        }
    }

    if (document.checkpoint_path.empty()) {
        throw std::runtime_error("sync daemon heartbeat checkpoint_path is empty");
    }
    if (document.checkpoint_path.find('\0') != std::string::npos) {
        throw std::runtime_error(
            "sync daemon heartbeat checkpoint_path contains an embedded NUL");
    }
    if (!valid_portable_sync_id(document.session_id) ||
        !valid_portable_sync_id(document.daemon_id) ||
        !valid_portable_sync_id(document.worker_id)) {
        throw std::runtime_error(
            "sync daemon heartbeat session, daemon, and worker identities must be portable sync ids");
    }

    const SyncDaemonHeartbeatOwnerLockDocument& owner = document.owner_lock;
    require_exact_json_u64(owner.owner_lock_epoch,
                           "sync daemon heartbeat owner_lock_epoch");
    require_exact_json_u64(owner.acquired_at_epoch,
                           "sync daemon heartbeat owner acquired_at_epoch");
    require_exact_json_u64(owner.expires_at_epoch,
                           "sync daemon heartbeat owner expires_at_epoch");
    require_exact_json_u64(owner.released_at_epoch,
                           "sync daemon heartbeat owner released_at_epoch");
    if (owner.required) {
        if (!owner.acquired) {
            throw std::runtime_error(
                "sync daemon heartbeat required owner lock was not acquired");
        }
        if (!lowercase_hex_digest_with_prefix(owner.owner_lock_id,
                                              kOwnerLockPrefix)) {
            throw std::runtime_error(
                "sync daemon heartbeat owner_lock_id is not canonical");
        }
        if (owner.owner_lock_epoch == 0 || owner.acquired_at_epoch == 0 ||
            owner.expires_at_epoch <= owner.acquired_at_epoch) {
            throw std::runtime_error(
                "sync daemon heartbeat owner lock epoch geometry is invalid");
        }
        if (document.heartbeat_epoch < owner.acquired_at_epoch) {
            throw std::runtime_error(
                "sync daemon heartbeat predates its owner acquisition");
        }
        if (owner.released) {
            if (owner.released_at_epoch < owner.acquired_at_epoch) {
                throw std::runtime_error(
                    "sync daemon heartbeat owner release predates acquisition");
            }
            if (!document.final) {
                throw std::runtime_error(
                    "sync daemon heartbeat released owner generation must be final");
            }
            if (owner.released_at_epoch != document.heartbeat_epoch) {
                throw std::runtime_error(
                    "sync daemon heartbeat final epoch does not equal owner release epoch");
            }
        } else if (owner.released_at_epoch != 0) {
            throw std::runtime_error(
                "sync daemon heartbeat unreleased owner has a release epoch");
        }
        if (document.final && !owner.released) {
            throw std::runtime_error(
                "sync daemon heartbeat cannot be final while its owner generation remains unreleased");
        }
    } else {
        if (owner.acquired || owner.released || owner.reclaimed_expired ||
            !owner.owner_lock_id.empty() || owner.owner_lock_epoch != 0 ||
            owner.acquired_at_epoch != 0 || owner.expires_at_epoch != 0 ||
            owner.released_at_epoch != 0) {
            throw std::runtime_error(
                "sync daemon heartbeat lockless document contains owner authority residue");
        }
    }
}

[[nodiscard]] std::string bool_json(bool value) {
    return value ? "true" : "false";
}

[[nodiscard]] std::string escape_json(const std::string& value) {
    std::ostringstream out;
    for (unsigned char c : value) {
        switch (c) {
            case '"': out << "\\\""; break;
            case '\\': out << "\\\\"; break;
            case '\b': out << "\\b"; break;
            case '\f': out << "\\f"; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (c < 0x20U) {
                    static constexpr char kHex[] = "0123456789abcdef";
                    out << "\\u00" << kHex[(c >> 4U) & 0x0fU]
                        << kHex[c & 0x0fU];
                } else {
                    out << static_cast<char>(c);
                }
        }
    }
    return out.str();
}

void validate_observational_numbers_or_throw(
    const SyncDaemonHeartbeatPublication& publication) {
    const SyncDaemonHeartbeatLeaseObservation& lease = publication.lease;
    const SyncDaemonHeartbeatProgressObservation& progress =
        publication.progress;
    const std::array<std::pair<std::uint64_t, const char*>, 26> values = {{
        {lease.final_worker_lease_epoch, "final_worker_lease_epoch"},
        {lease.next_worker_lease_epoch, "next_worker_lease_epoch"},
        {lease.next_scheduler_now_epoch, "next_scheduler_now_epoch"},
        {progress.passes_attempted, "passes_attempted"},
        {progress.passes_completed, "passes_completed"},
        {progress.mutating_passes, "mutating_passes"},
        {progress.idle_passes, "idle_passes"},
        {progress.archived_checkpoint_claimed_paths_blocked_by_missing_lineage,
         "archived_checkpoint_claimed_paths_blocked_by_missing_lineage"},
        {progress.terminal_apply_workorders_checked,
         "terminal_apply_workorders_checked"},
        {progress.terminal_apply_workorders_inserted,
         "terminal_apply_workorders_inserted"},
        {progress.terminal_apply_workorders_completed,
         "terminal_apply_workorders_completed"},
        {progress.terminal_apply_workorders_already_completed,
         "terminal_apply_workorders_already_completed"},
        {progress.terminal_apply_tombstone_workorders_completed,
         "terminal_apply_tombstone_workorders_completed"},
        {progress.terminal_apply_tombstone_targets_removed,
         "terminal_apply_tombstone_targets_removed"},
        {progress.terminal_apply_tombstone_targets_already_absent,
         "terminal_apply_tombstone_targets_already_absent"},
        {progress.terminal_apply_conflict_tombstone_workorders_completed,
         "terminal_apply_conflict_tombstone_workorders_completed"},
        {progress.terminal_apply_conflict_file_workorders_completed,
         "terminal_apply_conflict_file_workorders_completed"},
        {progress.terminal_apply_conflict_copies_preserved,
         "terminal_apply_conflict_copies_preserved"},
        {progress.terminal_apply_conflict_copies_reused,
         "terminal_apply_conflict_copies_reused"},
        {progress.terminal_apply_conflict_remote_tombstones_applied,
         "terminal_apply_conflict_remote_tombstones_applied"},
        {progress.terminal_apply_conflict_remote_files_materialized,
         "terminal_apply_conflict_remote_files_materialized"},
        {progress.workorder_rows_claimed, "workorder_rows_claimed"},
        {progress.workorder_rows_reclaimed, "workorder_rows_reclaimed"},
        {progress.workorder_rows_completed, "workorder_rows_completed"},
        {progress.chunks_written, "chunks_written"},
        {progress.bytes_written, "bytes_written"},
    }};
    for (const auto& [value, label] : values) {
        require_exact_json_u64(value,
                               "sync daemon heartbeat observational field " +
                                   std::string(label));
    }
}

}  // namespace

SyncDaemonHeartbeatDocument decode_sync_daemon_heartbeat_document_or_throw(
    const Json& root) {
    if (!root.is_object()) {
        throw std::runtime_error("sync daemon heartbeat JSON root must be an object");
    }
    (void)require_object_field(root, "service_lifecycle",
                               "sync daemon heartbeat");
    const Json& owner_lock = root.at("owner_lock");
    if (!owner_lock.is_object()) {
        throw std::runtime_error(
            "sync daemon heartbeat must contain object field owner_lock");
    }
    (void)require_object_field(root, "lease", "sync daemon heartbeat");
    (void)require_object_field(root, "progress", "sync daemon heartbeat");

    SyncDaemonHeartbeatDocument document;
    document.format = require_string_field(root, "format", "sync daemon heartbeat");
    const bool format_v2 = document.format == kFormatV2;
    if (format_v2) {
        const Json& process_identity = require_object_field(
            root, "process_incarnation", "sync daemon heartbeat");
        document.process_identity_present = true;
        document.process_identity.format = require_string_field(
            process_identity, "format",
            "sync daemon heartbeat process_incarnation");
        document.process_identity.process_id = require_u64_field(
            process_identity, "process_id",
            "sync daemon heartbeat process_incarnation");
        document.process_identity.boot_id = require_string_field(
            process_identity, "boot_id",
            "sync daemon heartbeat process_incarnation", true);
        document.process_identity.start_token = require_string_field(
            process_identity, "start_token",
            "sync daemon heartbeat process_incarnation", true);
    } else if (root.o.contains("process_incarnation")) {
        throw std::runtime_error(
            "sync daemon heartbeat v1 cannot contain process_incarnation fields");
    }
    document.revision_id =
        require_string_field(root, "revision_id", "sync daemon heartbeat");
    document.operation =
        require_string_field(root, "operation", "sync daemon heartbeat");
    document.service_instance_id = require_string_field(
        root, "service_instance_id", "sync daemon heartbeat");
    document.service_restart_epoch = require_u64_field(
        root, "service_restart_epoch", "sync daemon heartbeat");
    document.state = require_string_field(root, "state", "sync daemon heartbeat");
    document.final = require_bool_field(root, "final", "sync daemon heartbeat");
    document.reason = require_string_field(root, "reason", "sync daemon heartbeat");
    document.heartbeat_epoch = require_u64_field(
        root, "heartbeat_epoch", "sync daemon heartbeat");
    document.stale_after_seconds = require_u64_field(
        root, "stale_after_seconds", "sync daemon heartbeat");
    document.stale_at_epoch = require_u64_field(
        root, "stale_at_epoch", "sync daemon heartbeat");
    document.process_id =
        require_u64_field(root, "process_id", "sync daemon heartbeat");
    document.checkpoint_path = require_string_field(
        root, "checkpoint_path", "sync daemon heartbeat");
    document.session_id =
        require_string_field(root, "session_id", "sync daemon heartbeat");
    document.daemon_id =
        require_string_field(root, "daemon_id", "sync daemon heartbeat");
    document.worker_id =
        require_string_field(root, "worker_id", "sync daemon heartbeat");

    document.owner_lock.required = require_bool_field(
        owner_lock, "required", "sync daemon heartbeat owner_lock");
    document.owner_lock.acquired = require_bool_field(
        owner_lock, "acquired", "sync daemon heartbeat owner_lock");
    document.owner_lock.released = require_bool_field(
        owner_lock, "released", "sync daemon heartbeat owner_lock");
    document.owner_lock.reclaimed_expired = require_bool_field(
        owner_lock, "reclaimed_expired", "sync daemon heartbeat owner_lock");
    document.owner_lock.owner_lock_id = require_string_field(
        owner_lock,
        "owner_lock_id",
        "sync daemon heartbeat owner_lock",
        !document.owner_lock.required);
    document.owner_lock.owner_lock_epoch = require_u64_field(
        owner_lock, "owner_lock_epoch", "sync daemon heartbeat owner_lock");
    document.owner_lock.acquired_at_epoch = require_u64_field(
        owner_lock, "acquired_at_epoch", "sync daemon heartbeat owner_lock");
    document.owner_lock.expires_at_epoch = require_u64_field(
        owner_lock, "expires_at_epoch", "sync daemon heartbeat owner_lock");
    document.owner_lock.released_at_epoch = require_u64_field(
        owner_lock, "released_at_epoch", "sync daemon heartbeat owner_lock");

    validate_sync_daemon_heartbeat_document_or_throw(document);
    return document;
}

SyncDaemonHeartbeatLifecycleEvaluation
evaluate_sync_daemon_heartbeat_lifecycle_or_throw(
    const SyncDaemonHeartbeatDocument& document,
    bool scheduler_clock_provided,
    std::uint64_t observed_at_epoch,
    bool durable_owner_live,
    SyncProcessIdentityMatchKind process_match_kind,
    const std::string& process_match_reason) {
    validate_sync_daemon_heartbeat_document_or_throw(document);

    SyncDaemonHeartbeatLifecycleEvaluation out;
    if (document.final) {
        out.service_start_allowed = true;
        out.reason =
            "prior heartbeat is final evidence bound to a retired owner generation";
        return out;
    }
    if (!document.process_identity_present) {
        out.operator_attention_required = true;
        out.reason =
            "non-final legacy heartbeat has only PID process evidence";
        return out;
    }
    if (process_match_kind == SyncProcessIdentityMatchKind::Unsupported ||
        process_match_kind == SyncProcessIdentityMatchKind::Indeterminate ||
        process_match_kind == SyncProcessIdentityMatchKind::Invalid) {
        out.operator_attention_required = true;
        out.reason =
            "non-final heartbeat process incarnation could not be verified";
        if (!process_match_reason.empty()) {
            out.reason += ": " + process_match_reason;
        }
        return out;
    }
    if (document.stale_after_seconds == 0 || document.stale_at_epoch == 0) {
        out.existing_fresh = true;
        out.operator_attention_required = true;
        out.reason =
            "non-final heartbeat has no stale horizon and blocks service re-entry";
        return out;
    }
    if (!scheduler_clock_provided) {
        out.operator_attention_required = true;
        out.reason =
            "scheduler clock is required to classify a non-final heartbeat";
        return out;
    }

    out.existing_stale = observed_at_epoch >= document.stale_at_epoch;
    out.existing_fresh = !out.existing_stale;
    const bool exact_process_live =
        process_match_kind == SyncProcessIdentityMatchKind::Match;
    const bool prior_process_gone_or_reused =
        process_match_kind == SyncProcessIdentityMatchKind::Mismatch ||
        process_match_kind == SyncProcessIdentityMatchKind::NotRunning;

    if (out.existing_fresh) {
        if (durable_owner_live && exact_process_live) {
            out.reason =
                "fresh non-final heartbeat belongs to the exact live process and durable owner generation";
            return out;
        }
        out.operator_attention_required = true;
        if (prior_process_gone_or_reused) {
            out.reason =
                "heartbeat process incarnation is no longer exact before both stale horizon and owner expiry permit re-entry";
        } else {
            out.reason =
                "fresh non-final heartbeat blocks service re-entry until " +
                std::to_string(document.stale_at_epoch);
        }
        return out;
    }

    if (durable_owner_live) {
        out.operator_attention_required = true;
        out.reason =
            "heartbeat is stale while its durable owner generation is still live";
        return out;
    }
    if (exact_process_live) {
        out.operator_attention_required = true;
        out.reason =
            "heartbeat is stale while its exact process incarnation remains live";
        return out;
    }
    if (!prior_process_gone_or_reused) {
        throw std::runtime_error(
            "sync daemon heartbeat lifecycle received an unclassified process outcome");
    }
    out.service_start_allowed = true;
    out.reentry_from_stale_heartbeat = true;
    out.reason =
        "stale non-final heartbeat, expired owner generation, and nonmatching process incarnation permit service re-entry";
    return out;
}

std::string encode_sync_daemon_heartbeat_document_or_throw(
    const SyncDaemonHeartbeatPublication& publication) {
    const SyncDaemonHeartbeatDocument& document = publication.document;
    if (document.format != kFormatV2) {
        throw std::runtime_error(
            "sync daemon heartbeat publication must use the current v2 format");
    }
    validate_sync_daemon_heartbeat_document_or_throw(document);
    validate_observational_numbers_or_throw(publication);

    const SyncDaemonHeartbeatServiceLifecycleObservation& lifecycle =
        publication.service_lifecycle;
    const SyncDaemonHeartbeatLeaseObservation& lease = publication.lease;
    const SyncDaemonHeartbeatProgressObservation& progress =
        publication.progress;

    std::ostringstream out;
    // basic_ios adopts the process-global locale at construction.  JSON's
    // number grammar does not admit locale grouping or alternate separators.
    out.imbue(std::locale::classic());
    out << "{\n"
        << "  \"format\": \"" << escape_json(document.format) << "\",\n"
        << "  \"revision_id\": \"" << escape_json(document.revision_id)
        << "\",\n"
        << "  \"operation\": \"" << escape_json(document.operation)
        << "\",\n"
        << "  \"service_instance_id\": \""
        << escape_json(document.service_instance_id) << "\",\n"
        << "  \"service_restart_epoch\": "
        << document.service_restart_epoch << ",\n"
        << "  \"state\": \"" << escape_json(document.state) << "\",\n"
        << "  \"final\": " << bool_json(document.final) << ",\n"
        << "  \"reason\": \"" << escape_json(document.reason) << "\",\n"
        << "  \"heartbeat_epoch\": " << document.heartbeat_epoch << ",\n"
        << "  \"stale_after_seconds\": "
        << document.stale_after_seconds << ",\n"
        << "  \"stale_at_epoch\": " << document.stale_at_epoch << ",\n"
        << "  \"process_id\": " << document.process_id << ",\n"
        << "  \"process_incarnation\": {\n"
        << "    \"format\": \""
        << escape_json(document.process_identity.format) << "\",\n"
        << "    \"process_id\": " << document.process_identity.process_id
        << ",\n"
        << "    \"boot_id\": \""
        << escape_json(document.process_identity.boot_id) << "\",\n"
        << "    \"start_token\": \""
        << escape_json(document.process_identity.start_token) << "\"\n"
        << "  },\n"
        << "  \"checkpoint_path\": \""
        << escape_json(document.checkpoint_path) << "\",\n"
        << "  \"session_id\": \"" << escape_json(document.session_id)
        << "\",\n"
        << "  \"daemon_id\": \"" << escape_json(document.daemon_id)
        << "\",\n"
        << "  \"worker_id\": \"" << escape_json(document.worker_id)
        << "\",\n"
        << "  \"service_lifecycle\": {\n"
        << "    \"preflight_checked\": "
        << bool_json(lifecycle.preflight_checked) << ",\n"
        << "    \"preflight_passed\": "
        << bool_json(lifecycle.preflight_passed) << ",\n"
        << "    \"live_owner_blocked\": "
        << bool_json(lifecycle.live_owner_blocked) << ",\n"
        << "    \"heartbeat_checked\": "
        << bool_json(lifecycle.heartbeat_checked) << ",\n"
        << "    \"existing_heartbeat_loaded\": "
        << bool_json(lifecycle.existing_heartbeat_loaded) << ",\n"
        << "    \"existing_heartbeat_final\": "
        << bool_json(lifecycle.existing_heartbeat_final) << ",\n"
        << "    \"existing_heartbeat_fresh\": "
        << bool_json(lifecycle.existing_heartbeat_fresh) << ",\n"
        << "    \"existing_heartbeat_stale\": "
        << bool_json(lifecycle.existing_heartbeat_stale) << ",\n"
        << "    \"reentry_from_stale_heartbeat\": "
        << bool_json(lifecycle.reentry_from_stale_heartbeat) << ",\n"
        << "    \"preflight_reason\": \""
        << escape_json(lifecycle.preflight_reason) << "\"\n"
        << "  },\n"
        << "  \"owner_lock\": {\n"
        << "    \"required\": "
        << bool_json(document.owner_lock.required) << ",\n"
        << "    \"acquired\": "
        << bool_json(document.owner_lock.acquired) << ",\n"
        << "    \"released\": "
        << bool_json(document.owner_lock.released) << ",\n"
        << "    \"reclaimed_expired\": "
        << bool_json(document.owner_lock.reclaimed_expired) << ",\n"
        << "    \"owner_lock_id\": \""
        << escape_json(document.owner_lock.owner_lock_id) << "\",\n"
        << "    \"owner_lock_epoch\": "
        << document.owner_lock.owner_lock_epoch << ",\n"
        << "    \"acquired_at_epoch\": "
        << document.owner_lock.acquired_at_epoch << ",\n"
        << "    \"expires_at_epoch\": "
        << document.owner_lock.expires_at_epoch << ",\n"
        << "    \"released_at_epoch\": "
        << document.owner_lock.released_at_epoch << "\n"
        << "  },\n"
        << "  \"lease\": {\n"
        << "    \"worker_lease_id\": \""
        << escape_json(lease.worker_lease_id) << "\",\n"
        << "    \"final_worker_lease_epoch\": "
        << lease.final_worker_lease_epoch << ",\n"
        << "    \"next_worker_lease_epoch\": "
        << lease.next_worker_lease_epoch << ",\n"
        << "    \"next_scheduler_now_epoch\": "
        << lease.next_scheduler_now_epoch << "\n"
        << "  },\n"
        << "  \"progress\": {\n"
        << "    \"passes_attempted\": " << progress.passes_attempted
        << ",\n"
        << "    \"passes_completed\": " << progress.passes_completed
        << ",\n"
        << "    \"mutating_passes\": " << progress.mutating_passes
        << ",\n"
        << "    \"idle_passes\": " << progress.idle_passes << ",\n"
        << "    \"startup_sidecar_recovery_attempted\": "
        << bool_json(progress.startup_sidecar_recovery_attempted) << ",\n"
        << "    \"startup_sidecar_recovery_completed\": "
        << bool_json(progress.startup_sidecar_recovery_completed) << ",\n"
        << "    \"checkpoint_schema_version\": \""
        << escape_json(progress.checkpoint_schema_version) << "\",\n"
        << "    \"archived_checkpoint_migration_backfill_checked\": "
        << bool_json(progress.archived_checkpoint_migration_backfill_checked)
        << ",\n"
        << "    \"archived_checkpoint_exact_startup_hydration_supported\": "
        << bool_json(
               progress.archived_checkpoint_exact_startup_hydration_supported)
        << ",\n"
        << "    \"archived_checkpoint_migration_backfill_required\": "
        << bool_json(progress.archived_checkpoint_migration_backfill_required)
        << ",\n"
        << "    \"archived_checkpoint_migration_backfill_blocked_missing_lineage\": "
        << bool_json(
               progress
                   .archived_checkpoint_migration_backfill_blocked_missing_lineage)
        << ",\n"
        << "    \"archived_checkpoint_claimed_paths_blocked_by_missing_lineage\": "
        << progress
               .archived_checkpoint_claimed_paths_blocked_by_missing_lineage
        << ",\n"
        << "    \"terminal_apply_workorders_checked\": "
        << progress.terminal_apply_workorders_checked << ",\n"
        << "    \"terminal_apply_workorders_inserted\": "
        << progress.terminal_apply_workorders_inserted << ",\n"
        << "    \"terminal_apply_workorders_completed\": "
        << progress.terminal_apply_workorders_completed << ",\n"
        << "    \"terminal_apply_workorders_already_completed\": "
        << progress.terminal_apply_workorders_already_completed << ",\n"
        << "    \"terminal_apply_tombstone_workorders_completed\": "
        << progress.terminal_apply_tombstone_workorders_completed << ",\n"
        << "    \"terminal_apply_tombstone_targets_removed\": "
        << progress.terminal_apply_tombstone_targets_removed << ",\n"
        << "    \"terminal_apply_tombstone_targets_already_absent\": "
        << progress.terminal_apply_tombstone_targets_already_absent << ",\n"
        << "    \"terminal_apply_conflict_tombstone_workorders_completed\": "
        << progress.terminal_apply_conflict_tombstone_workorders_completed
        << ",\n"
        << "    \"terminal_apply_conflict_file_workorders_completed\": "
        << progress.terminal_apply_conflict_file_workorders_completed << ",\n"
        << "    \"terminal_apply_conflict_copies_preserved\": "
        << progress.terminal_apply_conflict_copies_preserved << ",\n"
        << "    \"terminal_apply_conflict_copies_reused\": "
        << progress.terminal_apply_conflict_copies_reused << ",\n"
        << "    \"terminal_apply_conflict_remote_tombstones_applied\": "
        << progress.terminal_apply_conflict_remote_tombstones_applied << ",\n"
        << "    \"terminal_apply_conflict_remote_files_materialized\": "
        << progress.terminal_apply_conflict_remote_files_materialized << ",\n"
        << "    \"workorder_rows_claimed\": "
        << progress.workorder_rows_claimed << ",\n"
        << "    \"workorder_rows_reclaimed\": "
        << progress.workorder_rows_reclaimed << ",\n"
        << "    \"workorder_rows_completed\": "
        << progress.workorder_rows_completed << ",\n"
        << "    \"chunks_written\": " << progress.chunks_written << ",\n"
        << "    \"bytes_written\": " << progress.bytes_written << "\n"
        << "  }\n"
        << "}\n";

    std::string payload = out.str();
    if (payload.size() > kSyncDaemonHeartbeatMaximumJsonBytes) {
        throw std::runtime_error(
            "sync daemon heartbeat serialized document exceeds the reader byte bound");
    }
    return payload;
}

}  // namespace anonsync
