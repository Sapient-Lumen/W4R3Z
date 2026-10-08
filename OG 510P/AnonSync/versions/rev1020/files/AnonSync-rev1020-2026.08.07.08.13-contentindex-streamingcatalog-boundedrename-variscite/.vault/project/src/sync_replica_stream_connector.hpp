#pragma once

#include "sync_socket_readiness_identity.hpp"

#include <chrono>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <stop_token>
#include <variant>

namespace anonsync {

// The application protocol and mutual TLS identity stay identical across every
// route. A route only determines how one reliable byte stream is established.
// In particular, Tor and I2P names are never submitted to the process-global
// resolver: only the locally configured proxy/bridge endpoint is numeric.
enum class SyncReplicaStreamRouteKind {
    DirectTcp,
    TorSocks5,
    I2pSam,
};

[[nodiscard]] std::string_view sync_replica_stream_route_kind_name(
    SyncReplicaStreamRouteKind kind) noexcept;

struct SyncReplicaNumericStreamEndpoint final {
    std::string numeric_address;
    std::uint16_t port = 0U;

    bool operator==(const SyncReplicaNumericStreamEndpoint&) const = default;
};

// Validates the endpoint as numeric and reports whether its address is in the
// IPv4 loopback block or is IPv6 ::1. Tor SOCKS and SAM are intentionally
// loopback-only until AnonSync owns authenticated encryption to a remote proxy.
[[nodiscard]] bool sync_replica_numeric_stream_endpoint_is_loopback_or_throw(
    const SyncReplicaNumericStreamEndpoint& endpoint,
    std::string_view label = "sync replica numeric stream endpoint");

struct SyncReplicaDirectTcpRoute final {
    SyncReplicaNumericStreamEndpoint endpoint;

    bool operator==(const SyncReplicaDirectTcpRoute&) const = default;
};

// Tor v3 onion-only route. The exact 56-character base32 service label is sent
// as a SOCKS5 domain name to the numeric local proxy. Username/password method
// is mandatory so the application can provide Tor's current format-0 strong
// isolation token: username "<torS0X>0", password isolation_token.
struct SyncReplicaTorSocks5Route final {
    SyncReplicaNumericStreamEndpoint proxy;
    std::string onion_service;
    std::uint16_t service_port = 0U;
    std::string isolation_token;

    bool operator==(const SyncReplicaTorSocks5Route&) const = default;
};

// Validates the canonical lowercase checksum-bearing Tor v3 service name used
// by both outbound SOCKS routes and inbound externally published onion-service
// profiles. This performs no network access and grants no ControlPort authority.
void validate_sync_replica_tor_v3_onion_service_or_throw(
    std::string_view onion_service,
    std::string_view label = "sync replica Tor v3 onion service");

// One SAM 3.1 STREAM session is created lazily and retained across every data
// stream opened by this connector. session_id is a recognizable configured
// base, not a literal bridge-global ID: the owning connector appends a bounded
// runtime-unique suffix before issuing SAM commands. This prevents independent
// shares and processes using the same router from colliding on a copied/default
// configuration value. TRANSIENT is suitable for an outbound-only client. A
// caller may instead supply one bounded private destination token loaded from
// protected storage. A TRANSIENT identity explicitly requests Ed25519; a
// persisted destination carries its own signature type and therefore must not
// receive SAM's TRANSIENT-only SIGNATURE_TYPE option. Every session requests
// ECIES-X25519 and explicit tunnel quantities so Java I2P and i2pd do not
// silently use different defaults.
struct SyncReplicaI2pSamRoute final {
    SyncReplicaNumericStreamEndpoint bridge;
    std::string session_id;
    std::string peer_destination;
    std::string session_destination = "TRANSIENT";
    std::uint32_t inbound_quantity = 2U;
    std::uint32_t outbound_quantity = 2U;

    bool operator==(const SyncReplicaI2pSamRoute&) const = default;
};

// Legacy lower-level native inbound route retained for one-shot compatibility.
// session_id has the same configured-base semantics as the outbound route and is
// materialized into a runtime-unique SAM ID by the forwarder owner. One SAM
// STREAM session and one STREAM FORWARD control socket publish a loopback numeric
// endpoint. The retained product service no longer uses this path; its
// SyncReplicaI2pSamAcceptRoute below has no local application listener.
struct SyncReplicaI2pSamForwardRoute final {
    SyncReplicaNumericStreamEndpoint bridge;
    std::string session_id;
    std::string session_destination;
    SyncReplicaNumericStreamEndpoint forward_endpoint;
    std::uint32_t inbound_quantity = 2U;
    std::uint32_t outbound_quantity = 2U;

    bool operator==(const SyncReplicaI2pSamForwardRoute&) const = default;
};

void validate_sync_replica_i2p_sam_forward_route_or_throw(
    const SyncReplicaI2pSamForwardRoute& route,
    std::string_view label = "sync replica I2P SAM forward route");

// Native inbound I2P route whose accepted application stream remains on the
// SAM socket. session_id is a configured base that the acceptor materializes
// into a runtime-unique bridge-global ID. Unlike STREAM FORWARD, STREAM ACCEPT
// does not introduce a local TCP listener that same-host clients can enter
// without traversing I2P. A persisted private destination is mandatory because
// the retained control session is the public service identity, not an
// outbound-only transient route.
struct SyncReplicaI2pSamAcceptRoute final {
    SyncReplicaNumericStreamEndpoint bridge;
    std::string session_id;
    std::string session_destination;
    std::uint32_t inbound_quantity = 2U;
    std::uint32_t outbound_quantity = 2U;

    bool operator==(const SyncReplicaI2pSamAcceptRoute&) const = default;
};

void validate_sync_replica_i2p_sam_accept_route_or_throw(
    const SyncReplicaI2pSamAcceptRoute& route,
    std::string_view label = "sync replica I2P SAM accept route");

using SyncReplicaStreamRoute = std::variant<
    SyncReplicaDirectTcpRoute,
    SyncReplicaTorSocks5Route,
    SyncReplicaI2pSamRoute>;

[[nodiscard]] SyncReplicaStreamRouteKind sync_replica_stream_route_kind(
    const SyncReplicaStreamRoute& route) noexcept;

void validate_sync_replica_stream_route_or_throw(
    const SyncReplicaStreamRoute& route,
    std::string_view label = "sync replica stream route");

enum class SyncReplicaStreamConnectDisposition {
    Connected,
    DeadlineExpired,
    NumericConnectFailed,
    RouteRejected,
    Cancelled,
};

[[nodiscard]] std::string_view
sync_replica_stream_connect_disposition_name(
    SyncReplicaStreamConnectDisposition disposition) noexcept;

enum class SyncReplicaStreamRouteStage {
    NumericConnect,
    TorMethodNegotiation,
    TorAuthentication,
    TorConnect,
    I2pControlHello,
    I2pSessionCreate,
    I2pStreamHello,
    I2pStreamConnect,
    I2pStreamForward,
    I2pStreamAccept,
    I2pStreamPeerDestination,
    Complete,
};

[[nodiscard]] std::string_view sync_replica_stream_route_stage_name(
    SyncReplicaStreamRouteStage stage) noexcept;

enum class SyncReplicaI2pSamResult {
    Ok,
    NoVersion,
    DuplicateId,
    DuplicateDestination,
    InvalidKey,
    InvalidId,
    CantReachPeer,
    KeyNotFound,
    PeerNotFound,
    LeaseSetNotFound,
    Timeout,
    I2pError,
    Unknown,
};

[[nodiscard]] std::string_view sync_replica_i2p_sam_result_name(
    SyncReplicaI2pSamResult result) noexcept;

struct SyncReplicaStreamConnectReport final {
    SyncReplicaStreamRouteKind route_kind =
        SyncReplicaStreamRouteKind::DirectTcp;
    SyncReplicaStreamConnectDisposition disposition =
        SyncReplicaStreamConnectDisposition::DeadlineExpired;
    SyncReplicaStreamRouteStage terminal_stage =
        SyncReplicaStreamRouteStage::NumericConnect;

    bool data_socket_created = false;
    bool data_socket_policy_verified = false;
    bool route_negotiated = false;
    bool control_session_created = false;
    bool control_session_reused = false;
    bool control_session_stale_detected = false;
    bool control_session_recovered = false;

    std::uint64_t numeric_connect_attempts = 0U;
    std::optional<int> numeric_connect_error;
    std::uint64_t route_bytes_written = 0U;
    std::uint64_t route_bytes_received = 0U;
    std::optional<std::uint8_t> socks5_reply;
    std::optional<SyncReplicaI2pSamResult> sam_result;
    std::optional<std::string> sam_peer_destination;

    bool operator==(const SyncReplicaStreamConnectReport&) const = default;
};

// Move-only ownership of the exact nonblocking+CLOEXEC data socket returned by
// a route. For I2P, the connector must outlive this stream because its retained
// SAM control socket owns the destination/session tunnels.
class SyncReplicaConnectedStream final {
public:
    SyncReplicaConnectedStream(const SyncReplicaConnectedStream&) = delete;
    SyncReplicaConnectedStream& operator=(
        const SyncReplicaConnectedStream&) = delete;
    SyncReplicaConnectedStream(SyncReplicaConnectedStream&& other) noexcept;
    SyncReplicaConnectedStream& operator=(
        SyncReplicaConnectedStream&& other) noexcept;
    ~SyncReplicaConnectedStream() noexcept;

    [[nodiscard]] int descriptor() const noexcept;
    [[nodiscard]] const SyncSocketLifetimeIdentity& socket_identity_or_throw(
        std::string_view label = "sync replica connected stream") const;

private:
    SyncReplicaConnectedStream(
        int descriptor,
        SyncSocketLifetimeIdentity identity) noexcept;
    void close_noexcept() noexcept;

    int descriptor_ = -1;
    std::optional<SyncSocketLifetimeIdentity> identity_;

    friend class SyncReplicaStreamConnector;
    friend class SyncReplicaI2pSamAcceptor;
};

struct SyncReplicaStreamConnectOutcome final {
    SyncReplicaStreamConnectReport report;
    std::optional<SyncReplicaConnectedStream> stream;

    SyncReplicaStreamConnectOutcome() = default;
    SyncReplicaStreamConnectOutcome(
        const SyncReplicaStreamConnectOutcome&) = delete;
    SyncReplicaStreamConnectOutcome& operator=(
        const SyncReplicaStreamConnectOutcome&) = delete;
    SyncReplicaStreamConnectOutcome(
        SyncReplicaStreamConnectOutcome&&) noexcept = default;
    SyncReplicaStreamConnectOutcome& operator=(
        SyncReplicaStreamConnectOutcome&&) noexcept = default;
};

// Retained native inbound I2P publication capability. start_until_or_throw()
// performs exactly one caller-authorized setup attempt and returns typed route
// evidence. It never retries, sleeps, or extends the absolute deadline. The
// cancellation overload keeps the same SAM attempt alive until cancellation,
// then closes it exactly once; it exists so a long tunnel build cannot freeze
// unrelated folder and outbound work or make service shutdown wait minutes.
// Once active, require_active_or_throw() checks that both retained SAM sockets
// are still live before another TLS accept is authorized.
class SyncReplicaI2pSamForwarder final {
public:
    explicit SyncReplicaI2pSamForwarder(
        SyncReplicaI2pSamForwardRoute route,
        std::string label = "sync replica I2P SAM forwarder");
    SyncReplicaI2pSamForwarder(const SyncReplicaI2pSamForwarder&) = delete;
    SyncReplicaI2pSamForwarder& operator=(
        const SyncReplicaI2pSamForwarder&) = delete;
    SyncReplicaI2pSamForwarder(SyncReplicaI2pSamForwarder&&) = delete;
    SyncReplicaI2pSamForwarder& operator=(
        SyncReplicaI2pSamForwarder&&) = delete;
    ~SyncReplicaI2pSamForwarder() noexcept;

    [[nodiscard]] SyncReplicaStreamConnectReport start_until_or_throw(
        std::chrono::steady_clock::time_point deadline);
    [[nodiscard]] SyncReplicaStreamConnectReport start_until_or_throw(
        std::chrono::steady_clock::time_point deadline,
        std::stop_token cancellation);
    void require_active_or_throw(
        std::string_view label =
            "sync replica I2P SAM forwarding capability");

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] const SyncReplicaI2pSamForwardRoute& route() const noexcept {
        return route_;
    }

private:
    struct Implementation;

    SyncReplicaI2pSamForwardRoute route_;
    std::string label_;
    std::unique_ptr<Implementation> implementation_;
};

struct SyncReplicaI2pSamAcceptOutcome final {
    SyncReplicaStreamConnectReport report;
    std::optional<SyncReplicaConnectedStream> stream;

    SyncReplicaI2pSamAcceptOutcome() = default;
    SyncReplicaI2pSamAcceptOutcome(
        const SyncReplicaI2pSamAcceptOutcome&) = delete;
    SyncReplicaI2pSamAcceptOutcome& operator=(
        const SyncReplicaI2pSamAcceptOutcome&) = delete;
    SyncReplicaI2pSamAcceptOutcome(
        SyncReplicaI2pSamAcceptOutcome&&) noexcept = default;
    SyncReplicaI2pSamAcceptOutcome& operator=(
        SyncReplicaI2pSamAcceptOutcome&&) noexcept = default;
};

// Retained native inbound I2P service capability. Setup owns one SAM STREAM
// session and arms one SILENT=false STREAM ACCEPT socket. The bridge's remote
// destination line is consumed before the exact remaining socket is handed to
// TLS, so no SAM metadata can be interpreted as a TLS record. An idle absolute
// deadline retains the pending accept and its partial destination line for the
// next bounded service step. No local forwarding listener exists in this path.
class SyncReplicaI2pSamAcceptor final {
public:
    explicit SyncReplicaI2pSamAcceptor(
        SyncReplicaI2pSamAcceptRoute route,
        std::string label = "sync replica I2P SAM acceptor");
    SyncReplicaI2pSamAcceptor(const SyncReplicaI2pSamAcceptor&) = delete;
    SyncReplicaI2pSamAcceptor& operator=(
        const SyncReplicaI2pSamAcceptor&) = delete;
    SyncReplicaI2pSamAcceptor(SyncReplicaI2pSamAcceptor&&) = delete;
    SyncReplicaI2pSamAcceptor& operator=(
        SyncReplicaI2pSamAcceptor&&) = delete;
    ~SyncReplicaI2pSamAcceptor() noexcept;

    // Creates the retained SAM session and arms the first STREAM ACCEPT. One
    // accept socket remains pending after a successful return.
    [[nodiscard]] SyncReplicaStreamConnectReport start_until_or_throw(
        std::chrono::steady_clock::time_point deadline);
    [[nodiscard]] SyncReplicaStreamConnectReport start_until_or_throw(
        std::chrono::steady_clock::time_point deadline,
        std::stop_token cancellation);

    // Returns one bridge-owned application stream, or DeadlineExpired while the
    // same pending accept remains armed. After a successful stream handoff, the
    // next call arms the replacement accept before waiting for another peer.
    [[nodiscard]] SyncReplicaI2pSamAcceptOutcome accept_until_or_throw(
        std::chrono::steady_clock::time_point setup_deadline,
        std::chrono::steady_clock::time_point peer_deadline);
    [[nodiscard]] SyncReplicaI2pSamAcceptOutcome accept_until_or_throw(
        std::chrono::steady_clock::time_point setup_deadline,
        std::chrono::steady_clock::time_point peer_deadline,
        std::stop_token cancellation);

    void require_active_or_throw(
        std::string_view label = "sync replica I2P SAM accept capability");

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool accept_armed() const noexcept;
    [[nodiscard]] const SyncReplicaI2pSamAcceptRoute& route() const noexcept {
        return route_;
    }

private:
    struct Implementation;

    SyncReplicaI2pSamAcceptRoute route_;
    std::string label_;
    std::unique_ptr<Implementation> implementation_;
};

// Process-local connector reused by a bounded sender command. Direct and Tor
// routes own no state between calls. I2P lazily establishes exactly one SAM 3.1
// control session and keeps it alive while later STREAM CONNECT sockets are
// created. No route performs local hostname resolution, retries after a
// terminal protocol response, sleeps, or extends the caller's absolute
// steady-clock deadline.
class SyncReplicaStreamConnector final {
public:
    explicit SyncReplicaStreamConnector(
        SyncReplicaStreamRoute route,
        std::string label = "sync replica stream connector");
    SyncReplicaStreamConnector(const SyncReplicaStreamConnector&) = delete;
    SyncReplicaStreamConnector& operator=(
        const SyncReplicaStreamConnector&) = delete;
    SyncReplicaStreamConnector(SyncReplicaStreamConnector&&) = delete;
    SyncReplicaStreamConnector& operator=(
        SyncReplicaStreamConnector&&) = delete;
    ~SyncReplicaStreamConnector() noexcept;

    [[nodiscard]] SyncReplicaStreamConnectOutcome connect_until_or_throw(
        std::chrono::steady_clock::time_point deadline);

    [[nodiscard]] const SyncReplicaStreamRoute& route() const noexcept {
        return route_;
    }
    [[nodiscard]] SyncReplicaStreamRouteKind route_kind() const noexcept {
        return sync_replica_stream_route_kind(route_);
    }

private:
    struct Implementation;

    SyncReplicaStreamRoute route_;
    std::string label_;
    std::unique_ptr<Implementation> implementation_;
};

}  // namespace anonsync
