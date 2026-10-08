#include "sync_replica_historical_version_inventory_json.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <iomanip>
#include <limits>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <streambuf>
#include <string_view>

namespace anonsync {
namespace {

void append_json_quoted(std::ostream& output, std::string_view value) {
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
}

[[nodiscard]] const char* json_bool(bool value) noexcept {
    return value ? "true" : "false";
}

void append_optional_uint64(
    std::ostream& output,
    const std::optional<std::uint64_t>& value) {
    if (value.has_value()) {
        output << *value;
    } else {
        output << "null";
    }
}

void append_optional_bool(
    std::ostream& output,
    const std::optional<bool>& value) {
    if (value.has_value()) {
        output << json_bool(*value);
    } else {
        output << "null";
    }
}

void append_payload_reachability_class(
    std::ostream& output,
    const SyncReplicaHistoricalVersionPayloadReachabilityClass& value) {
    output
        << "{\"file_operation_count\":" << value.file_operation_count
        << ",\"distinct_content_count\":" << value.distinct_content_count
        << ",\"present_content_count\":" << value.present_content_count
        << ",\"present_content_bytes\":" << value.present_content_bytes
        << ",\"missing_content_count\":" << value.missing_content_count
        << '}';
}

void append_payload_reachability_value(
    std::ostream& output,
    const SyncReplicaHistoricalVersionPayloadReachability& reachability) {
    output
        << "{\"scope\":\"share_retained_file_operations\""
        << ",\"reclaimable_authority\":false"
        << ",\"class_totals_overlap\":true"
        << ",\"payload_entry_count\":"
        << reachability.payload_entry_count
        << ",\"payload_indexed_bytes\":"
        << reachability.payload_indexed_bytes
        << ",\"current_visible\":";
    append_payload_reachability_class(output, reachability.current_visible);
    output << ",\"superseded_active\":";
    append_payload_reachability_class(output, reachability.superseded_active);
    output << ",\"inactive_evidence\":";
    append_payload_reachability_class(output, reachability.inactive_evidence);
    output << ",\"explicit_pins\":";
    append_payload_reachability_class(output, reachability.explicit_pins);
    output << ",\"retained_union\":";
    append_payload_reachability_class(output, reachability.retained_union);
    output
        << ",\"unreferenced_by_retained_file_operations_count\":"
        << reachability.unreferenced_payload_count
        << ",\"unreferenced_by_retained_file_operations_bytes\":"
        << reachability.unreferenced_payload_bytes
        << '}';
}

void append_payload_reachability(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionPayloadReachability>&
        reachability) {
    if (!reachability.has_value()) {
        output << "null";
        return;
    }
    append_payload_reachability_value(output, *reachability);
}

void append_query(
    std::ostream& output,
    const SyncReplicaHistoricalVersionQuery& query) {
    output << "{\"inspection_mode\":";
    append_json_quoted(
        output,
        sync_replica_historical_version_inspection_mode_name(
            query.inspection_mode));
    output << ",\"maximum_entries\":" << query.maximum_entries
           << ",\"canonical_path\":";
    if (query.canonical_path.has_value()) {
        append_json_quoted(output, *query.canonical_path);
    } else {
        output << "null";
    }
    output << ",\"start_after_operation_id\":";
    if (query.start_after_operation_id.has_value()) {
        append_json_quoted(output, *query.start_after_operation_id);
    } else {
        output << "null";
    }
    output << ",\"expected_source_cutpoint\":";
    if (query.expected_source_cutpoint.has_value()) {
        append_json_quoted(
            output,
            encode_sync_replica_historical_version_source_cutpoint_or_throw(
                *query.expected_source_cutpoint,
                "historical-version status query source cutpoint"));
    } else {
        output << "null";
    }
    output << '}';
}

void append_retention_plan_query(
    std::ostream& output,
    const SyncReplicaRetentionPlanQuery& query) {
    output << "{\"maximum_entries\":" << query.maximum_entries
           << ",\"start_after_content_sha256\":";
    if (query.start_after_content_sha256.has_value()) {
        append_json_quoted(output, *query.start_after_content_sha256);
    } else {
        output << "null";
    }
    output << ",\"expected_source_cutpoint\":";
    if (query.expected_source_cutpoint.has_value()) {
        append_json_quoted(
            output,
            encode_sync_replica_historical_version_source_cutpoint_or_throw(
                *query.expected_source_cutpoint,
                "retention-plan status query source cutpoint"));
    } else {
        output << "null";
    }
    output << '}';
}

void append_retention_plan_class(
    std::ostream& output,
    const SyncReplicaRetentionPlanClass& value) {
    output << "{\"payload_count\":" << value.payload_count
           << ",\"payload_bytes\":" << value.payload_bytes << '}';
}

struct RetentionPlanProjection final {
    std::size_t entry_count = 0U;
    bool truncated = false;
    std::optional<std::string_view> next_start_after_content_sha256;
    std::optional<std::uint64_t> status_byte_limit;
    bool status_byte_frontier_reached = false;
};

void append_retention_plan(
    std::ostream& output,
    const SyncReplicaRetentionPlan& plan,
    const RetentionPlanProjection& projection) {
    if (projection.entry_count > plan.entries.size()) {
        throw std::logic_error(
            "retention-plan projection exceeds its entries");
    }
    output << "{\"query\":";
    append_retention_plan_query(output, plan.query);
    output
        << ",\"scope\":\"complete_physical_payload_namespace\""
        << ",\"reclaimable_authority\":false"
        << ",\"quota_policy_applied\":false"
        << ",\"grace_period_applied\":false"
        << ",\"writer_fenced_collection\":false"
        << ",\"durable_mark_persisted\":false"
        << ",\"writer_fenced_observation\":"
        << json_bool(plan.writer_fenced_observation)
        << ",\"cooperating_new_namespace_activity_excluded_during_observation\":"
        << json_bool(
               plan.
                   cooperating_new_namespace_activity_excluded_during_observation)
        << ",\"source_replica_database_incarnation_sha256\":";
    append_json_quoted(
        output, plan.source_replica_database_incarnation_sha256);
    output << ",\"source_replica_database_recovery_epoch\":"
           << plan.source_replica_database_recovery_epoch
           << ",\"source_replica_state_generation\":"
           << plan.source_replica_state_generation
           << ",\"source_operation_set_digest\":";
    append_json_quoted(output, plan.source_operation_set_digest);
    output << ",\"source_evidence_set_digest\":";
    append_json_quoted(output, plan.source_evidence_set_digest);
    output << ",\"source_historical_version_pin_set_digest\":";
    append_json_quoted(
        output, plan.source_historical_version_pin_set_digest);
    output << ",\"historical_version_pin_count\":"
           << plan.historical_version_pin_count
           << ",\"source_visible_state_digest\":";
    append_json_quoted(output, plan.source_visible_state_digest);
    output << ",\"source_payload_snapshot_digest\":";
    append_json_quoted(output, plan.source_payload_snapshot_digest);
    output << ",\"payload_store_transient_namespace_bound\":true"
           << ",\"durable_receiver_restart_obligations_bound\":true"
           << ",\"same_process_store_live_payload_capabilities_bound\":true"
           << ",\"independently_opened_same_process_store_owner_live_payload_capabilities_bound\":true"
           << ",\"independent_store_owner_live_payload_capabilities_bound\":false"
           << ",\"cross_process_live_payload_capabilities_bound\":false"
           << ",\"already_copied_response_bytes_bound\":false"
           << ",\"active_pass_transient_roots_bound\":false"
           << ",\"opened_sender_transient_roots_bound\":false"
           << ",\"mutation_batch_transient_roots_bound\":false"
           << ",\"external_transient_root_model_complete\":false"
           << ",\"source_payload_transient_namespace_digest\":";
    append_json_quoted(
        output, plan.source_payload_transient_namespace_digest);
    output << ",\"payload_transient_entries\":"
           << plan.payload_transient_entry_count
           << ",\"payload_transient_bytes\":"
           << plan.payload_transient_bytes
           << ",\"payload_transient_reserved_bytes\":"
           << plan.payload_transient_reserved_bytes
           << ",\"live_payload_capabilities\":{\"process_store_scope_digest\":";
    append_json_quoted(
        output, plan.live_capability_process_store_scope_digest);
    output << ",\"process_store_scope_incarnation_digest\":";
    append_json_quoted(
        output, plan.live_capability_process_store_scope_incarnation_digest);
    output << ",\"capability_set_digest\":";
    append_json_quoted(output, plan.live_capability_set_digest);
    output << ",\"snapshot_count\":" << plan.live_snapshot_count
           << ",\"opened_payload_count\":"
           << plan.live_opened_payload_count
           << ",\"targeted_access_count\":"
           << plan.live_targeted_access_count
           << ",\"mutation_batch_count\":"
           << plan.live_mutation_batch_count
           << ",\"distinct_opened_payload_root_count\":"
           << plan.distinct_live_opened_payload_root_count
           << ",\"distinct_opened_payload_root_bytes\":"
           << plan.distinct_live_opened_payload_root_bytes
           << ",\"may_reopen_all_current_payloads\":"
           << json_bool(
                  plan.live_capabilities_may_reopen_all_current_payloads)
           << ",\"rooted_physical_payload_count\":"
           << plan.live_capability_rooted_physical_payload_count
           << ",\"rooted_physical_payload_bytes\":"
           << plan.live_capability_rooted_physical_payload_bytes
           << ",\"unreferenced_rooted_payload_count\":"
           << plan.unreferenced_live_capability_rooted_payload_count
           << ",\"unreferenced_rooted_payload_bytes\":"
           << plan.unreferenced_live_capability_rooted_payload_bytes
           << '}';
    output << ",\"writer_fenced_candidate_page_entry_count\":"
           << plan.writer_fenced_candidate_page_entry_count
           << ",\"returned_unreferenced_candidate_count\":"
           << plan.returned_unreferenced_candidate_count
           << ",\"returned_candidate_payload_use_exclusive_available_count\":"
           << plan.
                  returned_candidate_payload_use_exclusive_available_count
           << ",\"returned_candidate_payload_use_busy_count\":"
           << plan.returned_candidate_payload_use_busy_count
           << ",\"writer_fenced_candidate_page_digest\":";
    append_json_quoted(
        output, plan.writer_fenced_candidate_page_digest);
    output << ",\"unreferenced_candidate_set_digest\":";
    append_json_quoted(
        output, plan.unreferenced_candidate_set_digest);
    output << ",\"durable_candidate_witness_digest\":";
    append_json_quoted(
        output, plan.durable_candidate_witness_digest);
    output << ",\"exact_deletion_free_mark_digest\":";
    append_json_quoted(
        output, plan.exact_deletion_free_mark_digest);
    output << ",\"source_cutpoint\":";
    append_json_quoted(
        output,
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            plan.source_cutpoint(), "retention-plan source cutpoint"));
    output
        << ",\"payload_scan_hashed_entries\":"
        << plan.payload_scan_hashed_entry_count
        << ",\"payload_scan_hashed_bytes\":"
        << plan.payload_scan_hashed_bytes
        << ",\"payload_scan_reused_entries\":"
        << plan.payload_scan_reused_entry_count
        << ",\"payload_scan_reused_bytes\":"
        << plan.payload_scan_reused_bytes
        << ",\"retained_payload_reachability\":";
    append_payload_reachability_value(
        output, plan.retained_payload_reachability);
    output << ",\"disposition_totals\":{\"current_or_explicit_pin\":";
    append_retention_plan_class(output, plan.current_or_explicit_pin);
    output << ",\"retained_history_or_evidence\":";
    append_retention_plan_class(output, plan.retained_history_or_evidence);
    output << ",\"unreferenced_by_retained_file_operations\":";
    append_retention_plan_class(output, plan.unreferenced_by_retained_file_operations);
    output
        << "}"
        << ",\"physical_payload_count_after_cursor\":"
        << plan.physical_payload_count_after_cursor
        << ",\"truncated\":" << json_bool(projection.truncated)
        << ",\"entry_limit_frontier_reached\":"
        << json_bool(plan.entry_limit_frontier_reached)
        << ",\"status_byte_limit\":";
    append_optional_uint64(output, projection.status_byte_limit);
    output << ",\"status_byte_frontier_reached\":"
           << json_bool(projection.status_byte_frontier_reached)
           << ",\"next_start_after_content_sha256\":";
    if (projection.next_start_after_content_sha256.has_value()) {
        append_json_quoted(
            output, *projection.next_start_after_content_sha256);
    } else {
        output << "null";
    }
    output << ",\"entry_limit\":" << plan.query.maximum_entries
           << ",\"entries\":[";
    for (std::size_t index = 0U; index < projection.entry_count; ++index) {
        if (index != 0U) output << ',';
        const SyncReplicaRetentionPlanEntry& entry = plan.entries[index];
        output << "{\"content_sha256\":";
        append_json_quoted(output, entry.content_sha256);
        output
            << ",\"size_bytes\":" << entry.size_bytes
            << ",\"current_visible\":" << json_bool(entry.current_visible)
            << ",\"superseded_active\":"
            << json_bool(entry.superseded_active)
            << ",\"inactive_evidence\":"
            << json_bool(entry.inactive_evidence)
            << ",\"explicit_pin\":" << json_bool(entry.explicit_pin)
            << ",\"same_process_store_live_capability\":"
            << json_bool(entry.same_process_store_live_capability)
            << ",\"payload_use_disposition\":";
        append_json_quoted(
            output,
            sync_replica_retention_plan_payload_use_disposition_name(
                entry.payload_use_disposition));
        output
            << ",\"disposition\":";
        append_json_quoted(
            output,
            sync_replica_retention_plan_disposition_name(
                entry.disposition));
        output << '}';
    }
    output << "]}";
}

struct InventoryProjection final {
    std::size_t entry_count = 0U;
    bool truncated = false;
    std::optional<std::string_view> next_start_after_operation_id;
    std::optional<std::uint64_t> status_byte_limit;
    bool status_byte_frontier_reached = false;
};

void append_inventory(
    std::ostream& output,
    const SyncReplicaHistoricalVersionInventory& inventory,
    const InventoryProjection& projection) {
    if (projection.entry_count > inventory.entries.size()) {
        throw std::logic_error(
            "historical-version inventory projection exceeds its entries");
    }
    output << "{\"query\":";
    append_query(output, inventory.query);
    output
        << ",\"source_replica_state_generation\":"
        << inventory.source_replica_state_generation
        << ",\"source_operation_set_digest\":";
    append_json_quoted(output, inventory.source_operation_set_digest);
    output << ",\"source_evidence_set_digest\":";
    if (inventory.source_evidence_set_digest.has_value()) {
        append_json_quoted(output, *inventory.source_evidence_set_digest);
    } else {
        output << "null";
    }
    output << ",\"source_historical_version_pin_set_digest\":";
    append_json_quoted(
        output, inventory.source_historical_version_pin_set_digest);
    output << ",\"historical_version_pin_count\":"
           << inventory.historical_version_pin_count;
    output << ",\"source_visible_state_digest\":";
    append_json_quoted(output, inventory.source_visible_state_digest);
    output << ",\"source_payload_snapshot_digest\":";
    if (inventory.source_payload_snapshot_digest.has_value()) {
        append_json_quoted(
            output, *inventory.source_payload_snapshot_digest);
    } else {
        output << "null";
    }
    output << ",\"source_cutpoint\":";
    append_json_quoted(
        output,
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            inventory.source_cutpoint(),
            "historical-version inventory source cutpoint"));
    output << ",\"payload_scan_hashed_entries\":";
    append_optional_uint64(
        output, inventory.payload_scan_hashed_entry_count);
    output << ",\"payload_scan_hashed_bytes\":";
    append_optional_uint64(output, inventory.payload_scan_hashed_bytes);
    output << ",\"payload_scan_reused_entries\":";
    append_optional_uint64(
        output, inventory.payload_scan_reused_entry_count);
    output << ",\"payload_scan_reused_bytes\":";
    append_optional_uint64(output, inventory.payload_scan_reused_bytes);
    output << ",\"retained_payload_reachability\":";
    append_payload_reachability(
        output, inventory.retained_payload_reachability);
    output
        << ",\"historical_file_operation_count\":"
        << inventory.historical_file_operation_count
        << ",\"historical_file_operation_count_after_cursor\":"
        << inventory.historical_file_operation_count_after_cursor
        << ",\"payload_present_count\":";
    append_optional_uint64(output, inventory.payload_present_count);
    output << ",\"restore_ready_count\":";
    append_optional_uint64(output, inventory.restore_ready_count);
    output
        << ",\"truncated\":" << json_bool(projection.truncated)
        << ",\"entry_limit_frontier_reached\":"
        << json_bool(inventory.entry_limit_frontier_reached)
        << ",\"status_byte_limit\":";
    append_optional_uint64(output, projection.status_byte_limit);
    output << ",\"status_byte_frontier_reached\":"
           << json_bool(projection.status_byte_frontier_reached)
           << ",\"next_start_after_operation_id\":";
    if (projection.next_start_after_operation_id.has_value()) {
        append_json_quoted(
            output, *projection.next_start_after_operation_id);
    } else {
        output << "null";
    }
    output << ",\"entry_limit\":"
           << inventory.query.maximum_entries
           << ",\"entries\":[";
    for (std::size_t index = 0U;
         index < projection.entry_count;
         ++index) {
        if (index != 0U) output << ',';
        const SyncReplicaHistoricalVersionEntry& entry =
            inventory.entries[index];
        output << "{\"operation_id\":";
        append_json_quoted(output, entry.operation_id);
        output << ",\"canonical_path\":";
        append_json_quoted(output, entry.canonical_path);
        output << ",\"size_bytes\":" << entry.size_bytes
               << ",\"content_sha256\":";
        append_json_quoted(output, entry.content_sha256);
        output << ",\"actor_device_id\":";
        append_json_quoted(output, entry.actor.device_id);
        output << ",\"actor_epoch\":" << entry.actor.epoch
               << ",\"counter\":" << entry.counter
               << ",\"visible_head_count\":"
               << entry.visible_head_count
               << ",\"current_primary_operation_id\":";
        append_json_quoted(output, entry.current_primary_operation_id);
        output << ",\"current_primary_kind\":";
        append_json_quoted(
            output,
            entry.current_primary_kind == SyncReplicaValueKind::File
                ? "file"
                : "tombstone");
        output << ",\"payload_present\":";
        append_optional_bool(output, entry.payload_present);
        output << ",\"restore_ready\":";
        append_optional_bool(output, entry.restore_ready);
        output << ",\"pinned\":" << json_bool(entry.pinned);
        output << '}';
    }
    output << "]}";
}

class CountingStreamBuffer final : public std::streambuf {
public:
    [[nodiscard]] std::uint64_t count() const noexcept { return count_; }

protected:
    std::streamsize xsputn(
        const char_type*,
        std::streamsize count) override {
        if (count < 0) {
            throw std::overflow_error(
                "historical-version JSON count is negative");
        }
        add_or_throw(static_cast<std::uint64_t>(count));
        return count;
    }

    int_type overflow(int_type value) override {
        if (!traits_type::eq_int_type(value, traits_type::eof())) {
            add_or_throw(1U);
        }
        return traits_type::not_eof(value);
    }

private:
    void add_or_throw(std::uint64_t amount) {
        if (amount > std::numeric_limits<std::uint64_t>::max() - count_) {
            throw std::overflow_error(
                "historical-version JSON byte count overflows");
        }
        count_ += amount;
    }

    std::uint64_t count_ = 0U;
};

[[nodiscard]] InventoryProjection projection_from_inventory(
    const SyncReplicaHistoricalVersionInventory& inventory) {
    return {
        .entry_count = inventory.entries.size(),
        .truncated = inventory.truncated,
        .next_start_after_operation_id =
            inventory.next_start_after_operation_id.has_value()
                ? std::optional<std::string_view>(
                      *inventory.next_start_after_operation_id)
                : std::nullopt,
        .status_byte_limit = inventory.status_byte_limit,
        .status_byte_frontier_reached =
            inventory.status_byte_frontier_reached,
    };
}

[[nodiscard]] std::uint64_t inventory_size_or_throw(
    const SyncReplicaHistoricalVersionInventory& inventory,
    const InventoryProjection& projection) {
    CountingStreamBuffer buffer;
    std::ostream output(&buffer);
    append_inventory(output, inventory, projection);
    output.flush();
    if (!output.good()) {
        throw std::runtime_error(
            "historical-version JSON byte counting failed");
    }
    return buffer.count();
}

[[nodiscard]] RetentionPlanProjection projection_from_retention_plan(
    const SyncReplicaRetentionPlan& plan) {
    return {
        .entry_count = plan.entries.size(),
        .truncated = plan.truncated,
        .next_start_after_content_sha256 =
            plan.next_start_after_content_sha256.has_value()
                ? std::optional<std::string_view>(
                      *plan.next_start_after_content_sha256)
                : std::nullopt,
        .status_byte_limit = plan.status_byte_limit,
        .status_byte_frontier_reached = plan.status_byte_frontier_reached,
    };
}

[[nodiscard]] std::uint64_t retention_plan_size_or_throw(
    const SyncReplicaRetentionPlan& plan,
    const RetentionPlanProjection& projection) {
    CountingStreamBuffer buffer;
    std::ostream output(&buffer);
    append_retention_plan(output, plan, projection);
    output.flush();
    if (!output.good()) {
        throw std::runtime_error(
            "retention-plan JSON byte counting failed");
    }
    return buffer.count();
}

}  // namespace

void append_sync_replica_historical_version_query_json(
    std::ostream& output,
    const SyncReplicaHistoricalVersionQuery& query) {
    append_query(output, query);
}

void append_sync_replica_historical_version_inventory_json(
    std::ostream& output,
    const std::optional<SyncReplicaHistoricalVersionInventory>& inventory) {
    if (!inventory.has_value()) {
        output << "null";
        return;
    }
    append_inventory(output, *inventory, projection_from_inventory(*inventory));
}

std::string render_sync_replica_historical_version_query_json(
    const SyncReplicaHistoricalVersionQuery& query) {
    std::ostringstream output;
    append_sync_replica_historical_version_query_json(output, query);
    return output.str();
}

std::string render_sync_replica_historical_version_inventory_json(
    const std::optional<SyncReplicaHistoricalVersionInventory>& inventory) {
    std::ostringstream output;
    append_sync_replica_historical_version_inventory_json(output, inventory);
    return output.str();
}

void append_sync_replica_retention_plan_query_json(
    std::ostream& output,
    const SyncReplicaRetentionPlanQuery& query) {
    append_retention_plan_query(output, query);
}

void append_sync_replica_retention_plan_json(
    std::ostream& output,
    const std::optional<SyncReplicaRetentionPlan>& plan) {
    if (!plan.has_value()) {
        output << "null";
        return;
    }
    append_retention_plan(
        output, *plan, projection_from_retention_plan(*plan));
}

std::string render_sync_replica_retention_plan_query_json(
    const SyncReplicaRetentionPlanQuery& query) {
    std::ostringstream output;
    append_sync_replica_retention_plan_query_json(output, query);
    return output.str();
}

std::string render_sync_replica_retention_plan_json(
    const std::optional<SyncReplicaRetentionPlan>& plan) {
    std::ostringstream output;
    append_sync_replica_retention_plan_json(output, plan);
    return output.str();
}

void bound_sync_replica_historical_version_inventory_for_status_or_throw(
    SyncReplicaHistoricalVersionInventory& inventory) {
    inventory.status_byte_limit =
        kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes;
    inventory.status_byte_frontier_reached = false;

    InventoryProjection full = projection_from_inventory(inventory);
    if (inventory_size_or_throw(inventory, full) <=
        kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes) {
        return;
    }
    if (inventory.entries.empty()) {
        throw std::length_error(
            "historical-version status metadata exceeds its byte limit");
    }

    const auto projection_for_prefix =
        [&](std::size_t entry_count) -> InventoryProjection {
        return {
            .entry_count = entry_count,
            .truncated = true,
            .next_start_after_operation_id =
                inventory.entries[entry_count - 1U].operation_id,
            .status_byte_limit =
                kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes,
            .status_byte_frontier_reached = true,
        };
    };

    // A byte frontier is truthful only when it actually omits at least one
    // entry. Merely changing a JSON boolean or cursor field must never claim a
    // transport stop over an otherwise unchanged page.
    if (inventory.entries.size() == 1U ||
        inventory_size_or_throw(inventory, projection_for_prefix(1U)) >
            kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes) {
        throw std::length_error(
            "one historical-version status entry exceeds its byte limit");
    }

    std::size_t accepted = 1U;
    std::size_t rejected = inventory.entries.size();
    while (accepted + 1U < rejected) {
        const std::size_t middle = accepted + (rejected - accepted) / 2U;
        if (inventory_size_or_throw(
                inventory, projection_for_prefix(middle)) <=
            kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes) {
            accepted = middle;
        } else {
            rejected = middle;
        }
    }

    inventory.entries.resize(accepted);
    inventory.truncated = true;
    inventory.status_byte_frontier_reached = true;
    inventory.next_start_after_operation_id =
        inventory.entries.back().operation_id;

    if (inventory_size_or_throw(
            inventory, projection_from_inventory(inventory)) >
        kSyncReplicaHistoricalVersionMaximumStatusInventoryBytes) {
        throw std::logic_error(
            "historical-version status byte frontier did not converge");
    }
}

void bound_sync_replica_retention_plan_for_status_or_throw(
    SyncReplicaRetentionPlan& plan) {
    plan.status_byte_limit = kSyncReplicaRetentionPlanMaximumStatusBytes;
    plan.status_byte_frontier_reached = false;

    RetentionPlanProjection full = projection_from_retention_plan(plan);
    if (retention_plan_size_or_throw(plan, full) <=
        kSyncReplicaRetentionPlanMaximumStatusBytes) {
        return;
    }
    if (plan.entries.empty()) {
        throw std::length_error(
            "retention-plan status metadata exceeds its byte limit");
    }

    const auto projection_for_prefix =
        [&](std::size_t entry_count) -> RetentionPlanProjection {
        return {
            .entry_count = entry_count,
            .truncated = true,
            .next_start_after_content_sha256 =
                plan.entries[entry_count - 1U].content_sha256,
            .status_byte_limit = kSyncReplicaRetentionPlanMaximumStatusBytes,
            .status_byte_frontier_reached = true,
        };
    };

    if (plan.entries.size() == 1U ||
        retention_plan_size_or_throw(plan, projection_for_prefix(1U)) >
            kSyncReplicaRetentionPlanMaximumStatusBytes) {
        throw std::length_error(
            "one retention-plan status entry exceeds its byte limit");
    }

    std::size_t accepted = 1U;
    std::size_t rejected = plan.entries.size();
    while (accepted + 1U < rejected) {
        const std::size_t middle = accepted + (rejected - accepted) / 2U;
        if (retention_plan_size_or_throw(
                plan, projection_for_prefix(middle)) <=
            kSyncReplicaRetentionPlanMaximumStatusBytes) {
            accepted = middle;
        } else {
            rejected = middle;
        }
    }

    plan.entries.resize(accepted);
    plan.truncated = true;
    plan.status_byte_frontier_reached = true;
    plan.next_start_after_content_sha256 =
        plan.entries.back().content_sha256;

    if (retention_plan_size_or_throw(
            plan, projection_from_retention_plan(plan)) >
        kSyncReplicaRetentionPlanMaximumStatusBytes) {
        throw std::logic_error(
            "retention-plan status byte frontier did not converge");
    }
}

}  // namespace anonsync

#endif
