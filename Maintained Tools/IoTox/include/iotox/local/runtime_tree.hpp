#pragma once

#include "iotox/command_store.hpp"
#include "iotox/file_transfer.hpp"
#include "iotox/interactive_service.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/command.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/status.hpp"
#include "iotox/transport.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <map>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::local {

struct RuntimeSnapshot {
    std::string phase{"stopped"};
    std::string address;
    std::string network{"tox/native"};
    std::string backend{"not-loaded"};
    std::string self_connection{"offline"};
    std::string last_event{"none"};
    SelfProfile profile{};
    std::uint64_t event_count{0U};
    std::size_t peer_count{0U};
    std::size_t protocol_session_count{0U};
    std::size_t compatible_protocol_session_count{0U};
    std::size_t established_protocol_session_count{0U};
    std::size_t negotiating_protocol_session_count{0U};
    std::size_t incompatible_protocol_session_count{0U};
    std::size_t protocol_error_session_count{0U};
    std::size_t authority_session_count{0U};
    std::size_t authorized_peer_count{0U};
    std::size_t awaiting_authority_proof_count{0U};
    std::size_t authority_protocol_error_count{0U};
    bool ratox_enabled{false};
    bool ratox_configuration_valid{false};
    bool ratox_latency_mode_active{false};
    std::uint64_t ratox_active_service_interval_ms{0U};
    std::uint64_t ratox_active_transport_iteration_interval_ms{0U};
    std::uint64_t ratox_host_incarnation{0U};
    bool ratox_incarnation_lease_held{false};
    bool ratox_cgroup_host_budget_configured{false};
    bool ratox_cgroup_aggregate_budget_configured{false};
    bool ratox_cgroup_aggregate_pids_configured{false};
    bool ratox_cgroup_aggregate_memory_configured{false};
    bool ratox_cgroup_aggregate_swap_configured{false};
    bool ratox_cgroup_aggregate_cpu_configured{false};
    std::uint64_t ratox_cgroup_aggregate_pids_max{0U};
    std::uint64_t ratox_cgroup_aggregate_memory_max_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_swap_max_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_cpu_quota_max_microseconds{0U};
    std::uint64_t ratox_cgroup_aggregate_cpu_period_microseconds{0U};
    std::size_t ratox_cgroup_aggregate_active_reservations{0U};
    std::size_t ratox_cgroup_aggregate_peak_active_reservations{0U};
    std::uint64_t ratox_cgroup_aggregate_reserved_processes{0U};
    std::uint64_t ratox_cgroup_aggregate_reserved_memory_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_reserved_swap_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_reserved_cpu_quota_microseconds{0U};
    std::uint64_t ratox_cgroup_aggregate_peak_reserved_processes{0U};
    std::uint64_t ratox_cgroup_aggregate_peak_reserved_memory_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_peak_reserved_swap_bytes{0U};
    std::uint64_t ratox_cgroup_aggregate_peak_reserved_cpu_quota_microseconds{0U};
    std::uint64_t ratox_cgroup_aggregate_rejected_reservations{0U};
    std::uint64_t ratox_cgroup_aggregate_stranded_reservations{0U};
    bool ratox_cgroup_pressure_admission_configured{false};
    bool ratox_cgroup_pressure_admission_cpu_some_configured{false};
    bool ratox_cgroup_pressure_admission_memory_full_configured{false};
    bool ratox_cgroup_pressure_admission_io_full_configured{false};
    std::uint64_t ratox_cgroup_pressure_admission_cpu_some_avg10_max_basis_points{0U};
    std::uint64_t ratox_cgroup_pressure_admission_memory_full_avg10_max_basis_points{0U};
    std::uint64_t ratox_cgroup_pressure_admission_io_full_avg10_max_basis_points{0U};
    std::uint64_t ratox_cgroup_pressure_admission_hysteresis_basis_points{0U};
    bool ratox_cgroup_pressure_admission_cpu_some_trigger_configured{false};
    bool ratox_cgroup_pressure_admission_memory_full_trigger_configured{false};
    bool ratox_cgroup_pressure_admission_io_full_trigger_configured{false};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_window_microseconds{0U};
    std::uint64_t ratox_cgroup_pressure_admission_cpu_some_trigger_stall_microseconds{0U};
    std::uint64_t ratox_cgroup_pressure_admission_memory_full_trigger_stall_microseconds{0U};
    std::uint64_t ratox_cgroup_pressure_admission_io_full_trigger_stall_microseconds{0U};
    bool ratox_cgroup_pressure_admission_closed{false};
    std::uint64_t ratox_cgroup_pressure_admission_checks{0U};
    std::uint64_t ratox_cgroup_pressure_admission_admitted{0U};
    std::uint64_t ratox_cgroup_pressure_admission_rejections{0U};
    std::uint64_t ratox_cgroup_pressure_admission_sampling_failures{0U};
    std::uint64_t ratox_cgroup_pressure_admission_closed_transitions{0U};
    std::uint64_t ratox_cgroup_pressure_admission_reopened_transitions{0U};
    bool ratox_cgroup_pressure_admission_trigger_monitor_healthy{true};
    bool ratox_cgroup_pressure_admission_trigger_hold_active{false};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_hold_remaining_microseconds{0U};
    ErrorCode ratox_cgroup_pressure_admission_trigger_monitor_error_code{
        ErrorCode::ok};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_events{0U};
    std::uint64_t ratox_cgroup_pressure_admission_cpu_some_trigger_events{0U};
    std::uint64_t ratox_cgroup_pressure_admission_memory_full_trigger_events{0U};
    std::uint64_t ratox_cgroup_pressure_admission_io_full_trigger_events{0U};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_monitor_failures{0U};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_closed_transitions{0U};
    std::uint64_t ratox_cgroup_pressure_admission_trigger_hold_rejections{0U};
    bool ratox_cgroup_pressure_admission_last_sample_valid{false};
    ErrorCode ratox_cgroup_pressure_admission_last_sampling_error_code{
        ErrorCode::ok};
    bool ratox_cgroup_pressure_admission_last_cpu_some_observed{false};
    bool ratox_cgroup_pressure_admission_last_memory_full_observed{false};
    bool ratox_cgroup_pressure_admission_last_io_full_observed{false};
    std::uint64_t ratox_cgroup_pressure_admission_last_cpu_some_avg10_basis_points{0U};
    std::uint64_t ratox_cgroup_pressure_admission_last_memory_full_avg10_basis_points{0U};
    std::uint64_t ratox_cgroup_pressure_admission_last_io_full_avg10_basis_points{0U};
    std::uint64_t ratox_cgroup_completed_session_outcomes{0U};
    std::uint64_t ratox_cgroup_incomplete_session_outcomes{0U};
    std::uint64_t ratox_cgroup_pids_limit_hits{0U};
    std::uint64_t ratox_cgroup_memory_high_events{0U};
    std::uint64_t ratox_cgroup_memory_max_events{0U};
    std::uint64_t ratox_cgroup_memory_oom_events{0U};
    std::uint64_t ratox_cgroup_memory_oom_kills{0U};
    std::uint64_t ratox_cgroup_memory_oom_group_kills{0U};
    std::uint64_t ratox_cgroup_pids_peak_session_outcomes{0U};
    std::uint64_t ratox_cgroup_pids_peak_sum{0U};
    std::uint64_t ratox_cgroup_pids_peak_maximum{0U};
    std::uint64_t ratox_cgroup_memory_peak_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_peak_sum_bytes{0U};
    std::uint64_t ratox_cgroup_memory_peak_maximum_bytes{0U};
    std::uint64_t ratox_cgroup_memory_swap_peak_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_swap_peak_sum_bytes{0U};
    std::uint64_t ratox_cgroup_memory_swap_peak_maximum_bytes{0U};
    std::uint64_t ratox_cgroup_memory_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_reclaim_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_swap_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_page_faults{0U};
    std::uint64_t ratox_cgroup_memory_major_page_faults{0U};
    std::uint64_t ratox_cgroup_memory_pages_scanned{0U};
    std::uint64_t ratox_cgroup_memory_pages_reclaimed{0U};
    std::uint64_t ratox_cgroup_memory_pages_swapped_in{0U};
    std::uint64_t ratox_cgroup_memory_pages_swapped_out{0U};
    std::uint64_t ratox_cgroup_memory_swap_events_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_swap_high_events{0U};
    std::uint64_t ratox_cgroup_memory_swap_max_events{0U};
    std::uint64_t ratox_cgroup_memory_swap_fail_events{0U};
    std::uint64_t ratox_cgroup_local_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_frozen_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_cpu_bandwidth_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_cpu_burst_stat_session_outcomes{0U};
    std::uint64_t ratox_cgroup_cpu_usage_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_user_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_system_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_periods{0U};
    std::uint64_t ratox_cgroup_cpu_throttled_periods{0U};
    std::uint64_t ratox_cgroup_cpu_throttled_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_burst_periods{0U};
    std::uint64_t ratox_cgroup_cpu_burst_microseconds{0U};
    std::uint64_t ratox_cgroup_io_read_bytes{0U};
    std::uint64_t ratox_cgroup_io_write_bytes{0U};
    std::uint64_t ratox_cgroup_io_read_operations{0U};
    std::uint64_t ratox_cgroup_io_write_operations{0U};
    std::uint64_t ratox_cgroup_io_discard_bytes{0U};
    std::uint64_t ratox_cgroup_io_discard_operations{0U};
    std::uint64_t ratox_cgroup_cpu_pressure_session_outcomes{0U};
    std::uint64_t ratox_cgroup_cpu_pressure_full_session_outcomes{0U};
    std::uint64_t ratox_cgroup_cpu_pressure_some_microseconds{0U};
    std::uint64_t ratox_cgroup_cpu_pressure_full_microseconds{0U};
    std::uint64_t ratox_cgroup_memory_pressure_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_pressure_full_session_outcomes{0U};
    std::uint64_t ratox_cgroup_memory_pressure_some_microseconds{0U};
    std::uint64_t ratox_cgroup_memory_pressure_full_microseconds{0U};
    std::uint64_t ratox_cgroup_io_pressure_session_outcomes{0U};
    std::uint64_t ratox_cgroup_io_pressure_full_session_outcomes{0U};
    std::uint64_t ratox_cgroup_io_pressure_some_microseconds{0U};
    std::uint64_t ratox_cgroup_io_pressure_full_microseconds{0U};
    std::uint64_t ratox_cgroup_irq_pressure_session_outcomes{0U};
    std::uint64_t ratox_cgroup_irq_pressure_full_microseconds{0U};
    std::size_t ratox_cgroup_profile_budget_count{0U};
    std::size_t ratox_cgroup_preflight_policy_count{0U};
    std::size_t ratox_cgroup_recovery_reserved_names{0U};
    std::size_t ratox_cgroup_recovery_live_incarnations{0U};
    std::size_t ratox_cgroup_recovery_stale_incarnations{0U};
    std::size_t ratox_cgroup_recovery_recovered_incarnations{0U};
    std::size_t ratox_cgroup_recovery_empty_legacy_removed{0U};
    std::size_t ratox_session_count{0U};
    std::size_t ratox_live_session_count{0U};
    std::size_t ratox_session_tombstone_count{0U};
    std::size_t ratox_running_process_count{0U};
    std::size_t ratox_attached_session_count{0U};
    std::size_t ratox_closing_session_count{0U};
    std::size_t ratox_admission_replay_count{0U};
    std::size_t ratox_pending_admission_count{0U};
    std::size_t ratox_admission_replay_bytes{0U};
    std::size_t ratox_outbound_packet_count{0U};
    std::size_t ratox_outbound_bytes{0U};
    std::uint64_t ratox_event_count{0U};
    std::uint64_t ratox_dropped_event_count{0U};
    std::uint64_t ratox_controller_retryable_send_rejections{0U};
    std::uint64_t ratox_controller_current_retry_streak{0U};
    std::uint64_t ratox_controller_maximum_retry_streak{0U};
    std::uint64_t ratox_controller_retry_age_us{0U};
    std::uint64_t ratox_host_retryable_send_rejections{0U};
    std::uint64_t ratox_host_current_retry_streak{0U};
    std::uint64_t ratox_host_maximum_retry_streak{0U};
    std::uint64_t ratox_host_retry_age_us{0U};
    std::size_t pending_request_count{0U};
    std::size_t incoming_file_offer_count{0U};
    std::size_t active_file_transfer_count{0U};
    std::uint64_t dropped_event_count{0U};
    TransportStats transport_stats{};
    FileCarrierStats file_carrier_stats{};
    std::string sodium_provider{"not-loaded"};
    std::string sodium_version{"unknown"};
    std::string device_public_key;
    bool authority_initialized{false};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t authority_sequence{0U};
    std::size_t authority_record_count{0U};
    std::size_t authority_principal_count{0U};
    std::size_t active_authority_principal_count{0U};
    std::size_t active_authority_owner_count{0U};
    bool command_store_initialized{false};
    std::uint64_t command_store_generation{0U};
    std::uint64_t command_sender_epoch{0U};
    std::size_t durable_command_record_count{0U};
    std::size_t incoming_command_record_count{0U};
    std::size_t outgoing_command_record_count{0U};
    std::size_t pending_command_record_count{0U};
    bool command_clock_trusted{false};
    std::uint64_t command_clock_high_water_unix_ms{0U};
    std::size_t due_command_artifact_count{0U};
    std::size_t held_expiring_command_count{0U};
    bool command_fifo_running{false};
    std::size_t command_fifo_count{0U};
    std::uint64_t command_fifo_record_count{0U};
    std::uint64_t command_fifo_rejected_count{0U};
    bool text_fifo_running{false};
    std::size_t message_fifo_count{0U};
    std::size_t action_fifo_count{0U};
    std::uint64_t text_fifo_record_count{0U};
    std::uint64_t text_fifo_rejected_count{0U};
    bool file_fifo_running{false};
    std::size_t file_send_fifo_count{0U};
    std::size_t file_receive_fifo_count{0U};
    std::size_t file_control_fifo_count{0U};
    std::uint64_t file_fifo_record_count{0U};
    std::uint64_t file_fifo_rejected_count{0U};
    bool friendship_fifo_running{false};
    std::size_t request_send_fifo_count{0U};
    std::size_t request_accept_fifo_count{0U};
    std::size_t request_reject_fifo_count{0U};
    std::size_t peer_remove_fifo_count{0U};
    std::uint64_t friendship_fifo_record_count{0U};
    std::uint64_t friendship_fifo_rejected_count{0U};
};

struct FriendLifecycleEvent {
    std::uint64_t unix_ms{0U};
    std::uint64_t sequence{0U};
    std::string source;
    std::string operation;
    // Some framing failures occur before a trustworthy public key can be
    // decoded. That absence is represented explicitly rather than by a fake
    // all-zero key or a magic string stored in public_key.
    bool has_public_key{true};
    std::string public_key;
    std::string disposition;
    ErrorCode error_code{ErrorCode::ok};
    bool has_friend_number{false};
    std::uint32_t friend_number{0U};
    std::string detail;
};

struct PeerCommandEvent {
    std::uint64_t unix_ms{0U};
    std::uint64_t ingress_sequence{0U};
    std::string operation;
    std::string disposition;
    ErrorCode error_code{ErrorCode::ok};
    std::uint64_t sender_epoch{0U};
    std::uint64_t message_id{0U};
    std::string state;
    std::string detail;
};

// A message-ingress event records what happened after a process wrote a
// complete record to a peer's ratox-style `message` or `action` FIFO. This is
// intentionally distinct from the `messages` transport journal: FIFO ingress
// can be rejected before c-toxcore allocates a message ID, while the transport
// journal records accepted sends, incoming text, and read receipts.
struct PeerMessageIngressEvent {
    std::uint64_t unix_ms{0U};
    std::uint64_t ingress_sequence{0U};
    TextMessageKind kind{TextMessageKind::normal};
    std::string disposition;
    ErrorCode error_code{ErrorCode::ok};
    bool has_message_id{false};
    std::uint32_t message_id{0U};
    std::vector<std::uint8_t> body;
    std::string detail;
};

// File FIFO ingress deliberately carries names, not file bytes. One event
// records the semantic result after a complete record has crossed the kernel
// FIFO boundary and the Agent has attempted the same finite-file operation as
// the structured local-control client. The optional transfer snapshot is the
// manager's exact admission result; it is not a promise that the transfer will
// still be live by the time a reader observes this journal line.
struct PeerFileIngressEvent {
    std::uint64_t unix_ms{0U};
    std::uint64_t ingress_sequence{0U};
    std::string operation;
    std::string disposition;
    ErrorCode error_code{ErrorCode::ok};
    bool has_transfer{false};
    FileTransferRecord transfer{};
    bool has_file_number{false};
    std::uint32_t file_number{0U};
    std::filesystem::path local_path;
    std::string detail;
};

// Transport file events share the per-peer file journal with local ingress so
// an operator can distinguish "the path request was admitted" from later
// toxcore offer/control/chunk progress. This remains an observational journal;
// live transfer truth is projected separately and completed incoming truth is
// the atomically published destination file.
struct PeerFileTransportEvent {
    std::uint64_t unix_ms{0U};
    TransportEvent event{};
    Status manager_status{};
    bool has_transfer{false};
    FileTransferRecord transfer{};
};

class RuntimeTree {
  public:
    struct Config {
        std::filesystem::path root;
        std::size_t event_rotation_bytes{1024U * 1024U};
        std::size_t message_rotation_bytes{1024U * 1024U};
        std::size_t protocol_rotation_bytes{1024U * 1024U};
        std::size_t command_rotation_bytes{1024U * 1024U};
        std::size_t file_rotation_bytes{1024U * 1024U};
        std::size_t friendship_rotation_bytes{1024U * 1024U};
        std::size_t ratox_rotation_bytes{1024U * 1024U};
    };

    explicit RuntimeTree(Config config);

    [[nodiscard]] Status prepare();
    [[nodiscard]] Status publish(const RuntimeSnapshot &snapshot);
    [[nodiscard]] Status publish_peers(std::span<const TransportPeer> peers);
    [[nodiscard]] Status publish_transfers(
        std::span<const FileTransferRecord> transfers);
    [[nodiscard]] Status publish_peer_transfers(
        std::string_view public_key_hex,
        std::span<const FileTransferRecord> transfers);
    [[nodiscard]] Status publish_authority(
        const security::AuthoritySnapshot &authority);
    [[nodiscard]] Status publish_peer_session(
        std::string_view public_key_hex,
        const protocol::PeerSessionSnapshot &session);
    [[nodiscard]] Status publish_peer_authority(
        std::string_view public_key_hex,
        const security::PeerAuthoritySnapshot &authority);
    [[nodiscard]] Status publish_peer_description(
        std::string_view public_key_hex,
        const protocol::PeerDescriptionSnapshot &description);
    [[nodiscard]] Status publish_commands(
        const DurableCommandSnapshot &commands);
    [[nodiscard]] Status publish_friend_request(
        const TransportEvent &event, std::uint64_t received_unix_ms = 0U);
    [[nodiscard]] Status remove_friend_request(std::span<const std::uint8_t> public_key);
    [[nodiscard]] Status append_event(const TransportEvent &event);
    [[nodiscard]] Status append_friend_lifecycle(
        const FriendLifecycleEvent &event);
    [[nodiscard]] Status append_ratox_event(
        const interactive::RatoxServiceEvent &event);
    [[nodiscard]] Status append_peer_message(
        std::string_view public_key_hex, const TransportEvent &event);
    [[nodiscard]] Status append_peer_protocol(
        std::string_view public_key_hex, std::string_view direction,
        const protocol::Frame &frame);
    [[nodiscard]] Status append_peer_command_event(
        std::string_view public_key_hex, const PeerCommandEvent &event);
    [[nodiscard]] Status append_peer_message_ingress(
        std::string_view public_key_hex,
        const PeerMessageIngressEvent &event);
    [[nodiscard]] Status append_peer_file_ingress(
        std::string_view public_key_hex,
        const PeerFileIngressEvent &event);
    [[nodiscard]] Status append_peer_file_transport(
        std::string_view public_key_hex,
        const PeerFileTransportEvent &event);

    [[nodiscard]] const std::filesystem::path &root() const noexcept;
    [[nodiscard]] std::filesystem::path socket_path() const;
    [[nodiscard]] std::filesystem::path event_path() const;
    [[nodiscard]] std::filesystem::path friend_event_path() const;
    [[nodiscard]] std::filesystem::path ratox_event_path() const;

    [[nodiscard]] static std::string render_snapshot(const RuntimeSnapshot &snapshot);
    [[nodiscard]] static std::string render_event(const TransportEvent &event);
    [[nodiscard]] static std::string render_friend_lifecycle(
        const FriendLifecycleEvent &event);
    [[nodiscard]] static std::string render_ratox_event(
        const interactive::RatoxServiceEvent &event);
    [[nodiscard]] static std::string render_peer_message(const TransportEvent &event);
    [[nodiscard]] static std::string render_peer_protocol(
        std::string_view direction, const protocol::Frame &frame);
    [[nodiscard]] static std::string render_peer_session(
        const protocol::PeerSessionSnapshot &session);
    [[nodiscard]] static std::string render_peer_authority(
        const security::PeerAuthoritySnapshot &authority);
    [[nodiscard]] static std::string render_peer_description(
        const protocol::PeerDescriptionSnapshot &description);
    [[nodiscard]] static std::string render_peer_command_event(
        const PeerCommandEvent &event);
    [[nodiscard]] static std::string render_peer_message_ingress(
        const PeerMessageIngressEvent &event);
    [[nodiscard]] static std::string render_peer_file_ingress(
        const PeerFileIngressEvent &event);
    [[nodiscard]] static std::string render_peer_file_transport(
        const PeerFileTransportEvent &event);

  private:
    [[nodiscard]] Status validate_or_create_directory(
        const std::filesystem::path &path, unsigned int mode) const;
    [[nodiscard]] Status validate_or_create_fifo(
        const std::filesystem::path &path, unsigned int mode) const;
    [[nodiscard]] Status validate_or_create_private_file(
        const std::filesystem::path &path) const;
    [[nodiscard]] Status write_text(
        const std::filesystem::path &path, const std::string &text) const;
    [[nodiscard]] Status write_bytes(
        const std::filesystem::path &path, std::span<const std::uint8_t> bytes) const;
    [[nodiscard]] Status rotate_events_if_needed(std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_friend_events_if_needed(
        std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_ratox_events_if_needed(
        std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_peer_messages_if_needed(
        const std::filesystem::path &directory, std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_peer_protocol_if_needed(
        const std::filesystem::path &directory, std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_peer_commands_if_needed(
        const std::filesystem::path &directory, std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_peer_message_ingress_if_needed(
        const std::filesystem::path &directory, std::size_t incoming_bytes);
    [[nodiscard]] Status rotate_peer_files_if_needed(
        const std::filesystem::path &directory, std::size_t incoming_bytes);

    Config config_;
    mutable std::mutex surface_mutex_;
    mutable std::mutex event_mutex_;
    mutable std::mutex friend_event_mutex_;
    mutable std::mutex ratox_event_mutex_;
    std::map<std::string, FileTransferRecord> transfer_projection_cache_;
    std::map<std::string, FileTransferRecord> peer_transfer_projection_cache_;
};

[[nodiscard]] std::filesystem::path default_runtime_root();
[[nodiscard]] std::filesystem::path default_state_path();
// Keep transport identities in distinct default savedata files across route
// contexts. An explicit IOTOX_STATE_PATH remains an operator-selected
// compatibility override and is therefore returned unchanged.
[[nodiscard]] std::filesystem::path default_state_path(ToxRoute route);

}  // namespace iotox::local
