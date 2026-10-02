#pragma once

#include "iotox/network.hpp"
#include "iotox/status.hpp"
#include "iotox/toxcore/abi.hpp"
#include "iotox/toxcore/bootstrap.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <utility>
#include <vector>

namespace iotox {

using FileId = std::array<std::uint8_t, toxcore::abi::kFileIdLength>;
using FileChunkSource = std::function<Result<std::vector<std::uint8_t>>(
    std::uint64_t position, std::size_t length)>;

enum class TransferControl {
    resume,
    pause,
    cancel,
};

enum class PresenceStatus {
    available,
    away,
    busy,
};

enum class TextMessageKind {
    normal,
    action,
};

// Local owner-thread scheduling class. This is not a remotely selectable QoS
// bit and does not change toxcore's wire semantics.
enum class TransportTrafficClass {
    interactive,
    control,
    bulk,
};

enum class TransportEventKind {
    backend_ready,
    self_connection,
    friend_connection,
    friend_request,
    friend_added,
    friend_removed,
    friend_name,
    friend_status_message,
    friend_status,
    friend_typing,
    message_sent,
    friend_message,
    friend_read_receipt,
    lossy_packet,
    lossless_packet,
    file_offer,
    file_control,
    file_chunk_request,
    file_chunk,
    bootstrap,
    tcp_relay,
    diagnostic,
};

struct SelfProfile {
    std::vector<std::uint8_t> name;
    std::vector<std::uint8_t> status_message;
    PresenceStatus status{PresenceStatus::available};

    [[nodiscard]] bool operator==(const SelfProfile &) const = default;
};

struct TransportEvent {
    TransportEvent() = default;
    TransportEvent(
        TransportEventKind event_kind, std::uint32_t event_friend_number,
        int event_connection_status,
        std::vector<std::uint8_t> event_public_key,
        std::vector<std::uint8_t> event_data, std::string event_message)
        : kind(event_kind),
          friend_number(event_friend_number),
          connection_status(event_connection_status),
          public_key(std::move(event_public_key)),
          data(std::move(event_data)),
          message(std::move(event_message)) {}

    TransportEventKind kind{TransportEventKind::diagnostic};
    std::uint32_t friend_number{0};
    int connection_status{0};
    std::vector<std::uint8_t> public_key;
    std::vector<std::uint8_t> data;
    std::string message;
    std::uint64_t dropped_events_before{0U};

    // Text/profile fields. The consumed c-toxcore ABI passes an explicitly
    // bounded byte span and never relies on NUL termination. IoTox preserves
    // those bytes at the adapter boundary, while interoperable Tox human text
    // should satisfy the protocol's UTF-8 contract. Message IDs are per-friend
    // values assigned by c-toxcore; they are transport receipts, not IoTox
    // command IDs.
    TextMessageKind text_kind{TextMessageKind::normal};
    std::uint32_t message_id{0U};
    PresenceStatus presence_status{PresenceStatus::available};
    bool typing{false};

    // File-transfer fields are meaningful only for the corresponding event
    // kinds. File offers are delivered only after the owner thread has left
    // tox_iterate and attempted a stable tox_file_get_file_id lookup.
    std::uint32_t file_number{0U};
    std::uint32_t file_kind{toxcore::abi::kFileKindData};
    std::uint64_t file_size{0U};
    std::uint64_t file_position{0U};
    std::size_t requested_length{0U};
    TransferControl file_control{TransferControl::resume};
    FileId file_id{};
    bool has_file_id{false};
    std::vector<std::uint8_t> filename;

    // A high-level sender may install a source with offer_file. c-toxcore
    // expects each requested chunk to be supplied before its callback
    // returns, so the transport records the inline attempt and result here
    // for asynchronous bookkeeping without asking the manager to send twice.
    bool file_chunk_source_attempted{false};
    bool file_chunk_sent_inline{false};
    Status file_chunk_status{};
};

struct TransportPeer {
    std::uint32_t friend_number{0U};
    std::array<std::uint8_t, toxcore::abi::kPublicKeySize> public_key{};
    int connection_status{static_cast<int>(toxcore::abi::kConnectionNone)};
    std::vector<std::uint8_t> name;
    std::vector<std::uint8_t> status_message;
    PresenceStatus status{PresenceStatus::available};
    bool typing{false};

    [[nodiscard]] bool operator==(const TransportPeer &) const = default;
};

struct TransportTrafficStats {
    std::size_t pending_commands{0U};
    std::uint64_t admitted_commands{0U};
    std::uint64_t executed_commands{0U};
    std::uint64_t total_queue_wait_us{0U};
    std::uint64_t maximum_queue_wait_us{0U};
    // Nearest-rank queue-wait percentiles. Values through 4096 us are exact;
    // larger values are conservative bucket upper bounds and carry exact=false.
    std::uint64_t queue_wait_p50_upper_bound_us{0U};
    std::uint64_t queue_wait_p95_upper_bound_us{0U};
    std::uint64_t queue_wait_p99_upper_bound_us{0U};
    bool queue_wait_p50_exact{true};
    bool queue_wait_p95_exact{true};
    bool queue_wait_p99_exact{true};
    std::uint64_t queue_wait_at_or_above_2000_us{0U};
};

// Coherent lifetime outcomes for validated send_sensitive_lossless() calls.
// Before saturation, a snapshot satisfies calls >= toxcore_attempts >= the
// saturating sum of classified outcomes. The single owner may expose one
// in-flight attempt that has not yet reached a classified outcome.
struct SensitiveLosslessTransportStats {
    std::uint64_t calls{0U};
    std::uint64_t toxcore_attempts{0U};
    std::uint64_t accepted{0U};
    std::uint64_t send_queue_full{0U};
    std::uint64_t peer_not_connected{0U};
    std::uint64_t peer_not_found{0U};
    std::uint64_t contract_rejections{0U};
    std::uint64_t other_failures{0U};
};

struct TransportStats {
    std::size_t pending_commands{0U};
    std::size_t pending_events{0U};
    std::size_t maximum_pending_events{0U};
    std::uint64_t dropped_events{0U};
    std::uint64_t required_event_backpressure_count{0U};
    std::uint64_t required_event_backpressure_total_us{0U};
    std::uint64_t required_event_backpressure_maximum_us{0U};
    std::size_t file_pacing_paused_transfers{0U};
    std::size_t file_pacing_high_watermark{0U};
    std::size_t file_pacing_low_watermark{0U};
    std::uint64_t file_pacing_minimum_hold_us{0U};
    std::size_t file_pacing_resume_batch_limit{0U};
    std::uint64_t file_pacing_pause_count{0U};
    std::uint64_t file_pacing_resume_count{0U};
    std::uint64_t file_pacing_resume_batch_count{0U};
    std::size_t file_pacing_resume_batch_maximum{0U};
    std::uint64_t file_pacing_external_pause_count{0U};
    std::uint64_t file_pacing_pause_failure_count{0U};
    std::uint64_t file_pacing_resume_failure_count{0U};
    std::uint64_t file_pacing_total_hold_us{0U};
    std::uint64_t file_pacing_maximum_hold_us{0U};
    std::uint64_t iteration_count{0U};
    std::uint32_t requested_iteration_interval_ms{0U};
    std::uint32_t effective_iteration_interval_ms{0U};
    TransportTrafficStats interactive{};
    TransportTrafficStats control{};
    TransportTrafficStats bulk{};
    SensitiveLosslessTransportStats sensitive_lossless{};
};

class ToxTransport {
  public:
    struct Config {
        std::filesystem::path toxcore_library;
        std::filesystem::path state_path;
        // When set, startup must load exactly this Tox identity. The check is
        // performed after tox_new() reconstructs savedata but before any
        // bootstrap, relay, or tox_iterate network activity. Route workers use
        // this to make a path-to-savedata mapping fail closed.
        std::optional<std::array<std::uint8_t,
                                 toxcore::abi::kPublicKeySize>>
            expected_public_key;
        NetworkStack network{};
        std::optional<Socks5ProxyEndpoint> socks5_proxy;
        std::vector<toxcore::BootstrapEndpoint> bootstrap_nodes;
        std::vector<toxcore::BootstrapEndpoint> tcp_relays;
        std::chrono::milliseconds bootstrap_retry_interval{std::chrono::seconds(60)};
        std::chrono::milliseconds owner_command_timeout{std::chrono::seconds(5)};
        // tox_iteration_interval() has no network-fd wakeup. Bound the sleep so
        // an idle peer does not add an arbitrary scheduler-sized latency tail.
        std::chrono::milliseconds maximum_iteration_interval{
            std::chrono::milliseconds(20)};
        std::size_t max_pending_commands{128U};
        std::size_t max_owner_commands_per_iteration{16U};
        std::size_t max_pending_events{1024U};
        // File callbacks pause before they can consume the semantic event
        // reserve. Resume requires both low-water drain and this minimum hold,
        // giving interactive owner work and reliable packets a bounded turn.
        // Set both watermarks to zero only in focused queue-contract tests.
        std::size_t file_pacing_high_watermark{64U};
        std::size_t file_pacing_low_watermark{16U};
        std::chrono::microseconds file_pacing_minimum_hold{
            std::chrono::milliseconds(5)};
        // Resume the oldest eligible pauses first and give toxcore one
        // iteration between bounded batches. This prevents a low-water wake
        // from releasing every file producer onto the shared carrier at once.
        std::size_t file_pacing_resume_batch_limit{1U};
        bool native_udp_enabled{true};
        bool save_state_after_mutation{true};
        bool save_state_on_stop{true};
    };

    explicit ToxTransport(Config config);
    ~ToxTransport();

    ToxTransport(const ToxTransport &) = delete;
    ToxTransport &operator=(const ToxTransport &) = delete;
    ToxTransport(ToxTransport &&) = delete;
    ToxTransport &operator=(ToxTransport &&) = delete;

    // Route policy is public so the CLI, Agent, and auxiliary supervisor can
    // reject a leaky topology before creating durable/runtime state.
    [[nodiscard]] static Status validate_route_config(const Config &config);

    [[nodiscard]] Status start();
    void stop();

    // The provider has no network-fd wakeup API. Ratox therefore tightens the
    // ordinary idle cap only while an attachment is latency-sensitive, then
    // restores the configured baseline. This operation is thread-safe and
    // wakes the owner when the new cap is lower than its current sleep.
    [[nodiscard]] Status set_maximum_iteration_interval(
        std::chrono::milliseconds interval);

    // May be tightened exactly once before start(). This exists so the agent
    // can verify its signed route inventory before binding the already-owned
    // primary transport to the inventory's coordinator identity.
    [[nodiscard]] Status expect_public_key(
        const std::array<std::uint8_t, toxcore::abi::kPublicKeySize> &key);

    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] std::string address_hex() const;

    // User-visible Tox profile. These fields are transport presentation only;
    // they are not IoTox identity, ownership, or authorization material.
    [[nodiscard]] Result<SelfProfile> self_profile();
    [[nodiscard]] Status set_self_name(const std::vector<std::uint8_t> &name);
    [[nodiscard]] Status set_self_status_message(
        const std::vector<std::uint8_t> &status_message);
    [[nodiscard]] Status set_self_status(PresenceStatus status);

    // Transport friendship is deliberately separate from IoTox authorization.
    [[nodiscard]] Result<std::uint32_t> request_friend(
        const std::vector<std::uint8_t> &address,
        const std::vector<std::uint8_t> &message);
    [[nodiscard]] Result<std::uint32_t> accept_friend(
        const std::vector<std::uint8_t> &public_key);
    [[nodiscard]] Status remove_friend(std::uint32_t friend_number);
    // Resolve and delete under the same serialized toxcore owner-thread turn.
    // The returned friend number is lifecycle evidence only; callers bind the
    // operation to the 32-byte public key because toxcore may reuse numbers.
    [[nodiscard]] Result<std::uint32_t> remove_friend_by_public_key(
        const std::vector<std::uint8_t> &public_key);
    [[nodiscard]] Result<std::vector<TransportPeer>> list_friends();

    // Ratox-compatible human text lane. IoTox device commands use the framed
    // lossless-packet protocol instead; text delivery receipts do not imply
    // device-command execution.
    [[nodiscard]] Result<std::uint32_t> send_message(
        std::uint32_t friend_number, TextMessageKind kind,
        const std::vector<std::uint8_t> &message);
    [[nodiscard]] Status set_typing(std::uint32_t friend_number, bool typing);

    [[nodiscard]] Status send_lossless(
        std::uint32_t friend_number, const std::vector<std::uint8_t> &packet,
        TransportTrafficClass traffic_class =
            TransportTrafficClass::control);
    // Sensitive application traffic follows the same synchronous owner-thread
    // contract as send_lossless(), but its queued command copy is held by a
    // wiping buffer rather than an ordinary vector capture. This does not
    // change toxcore's own internal SENDQ lifetime; it prevents IoTox's
    // cross-thread command machinery from retaining terminal or command bytes
    // in released heap storage after success, cancellation, or failure.
    [[nodiscard]] Status send_sensitive_lossless(
        std::uint32_t friend_number,
        std::span<const std::uint8_t> packet,
        TransportTrafficClass traffic_class =
            TransportTrafficClass::control);
    [[nodiscard]] Status send_lossy(
        std::uint32_t friend_number, const std::vector<std::uint8_t> &packet,
        TransportTrafficClass traffic_class =
            TransportTrafficClass::interactive);

    // Low-level, exact c-toxcore file-transfer seam. The higher-level safe
    // filesystem policy (authorization, quotas, temporary files, integrity,
    // and atomic publication) intentionally remains above this interface.
    [[nodiscard]] Result<std::uint32_t> offer_file(
        std::uint32_t friend_number, std::uint32_t kind, std::uint64_t file_size,
        const std::optional<FileId> &file_id,
        const std::vector<std::uint8_t> &filename,
        FileChunkSource chunk_source = {});
    [[nodiscard]] Status control_file(
        std::uint32_t friend_number, std::uint32_t file_number,
        TransferControl control);
    [[nodiscard]] Status seek_file(
        std::uint32_t friend_number, std::uint32_t file_number,
        std::uint64_t position);
    [[nodiscard]] Result<FileId> get_file_id(
        std::uint32_t friend_number, std::uint32_t file_number);
    [[nodiscard]] Result<std::uint32_t> find_file(
        std::uint32_t friend_number, const FileId &file_id);
    [[nodiscard]] Status send_file_chunk(
        std::uint32_t friend_number, std::uint32_t file_number,
        std::uint64_t position, const std::vector<std::uint8_t> &data);
    [[nodiscard]] std::optional<TransportEvent> poll_event(
        std::chrono::milliseconds timeout);
    [[nodiscard]] TransportStats stats() const;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] std::string to_string(TransportEventKind kind);
[[nodiscard]] std::string transport_connection_name(int connection_status);
[[nodiscard]] std::string to_string(TransferControl control);
[[nodiscard]] std::string to_string(PresenceStatus status);
[[nodiscard]] std::string to_string(TextMessageKind kind);
[[nodiscard]] std::string to_string(TransportTrafficClass traffic_class);
[[nodiscard]] std::string public_key_hex(
    const std::array<std::uint8_t, toxcore::abi::kPublicKeySize> &key);

}  // namespace iotox
