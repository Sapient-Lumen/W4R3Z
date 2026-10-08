#pragma once

#include "sync_replica_delivery_channel.hpp"

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

#include <openssl/ssl.h>

namespace anonsync {

// A fatal error confined to one authenticated TLS session. The record stream
// is poisoned and must not be reused, but a long-running peer-service owner may
// safely discard that session, account the failure, and continue serving or
// reconnecting. Durable/database failures and internal invariant violations do
// not use this type and must still escape the service loop.
class SyncReplicaTlsSessionIoError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

namespace detail {
class SyncReplicaTlsAuthenticatedState;
class SyncReplicaTlsRecordReadState;
class SyncReplicaTlsRecordWriteState;
}

class SyncReplicaTlsRecordReadContinuation;
class SyncReplicaTlsRecordWriteContinuation;

enum class SyncReplicaTlsRecordReadReadinessPolicy {
    CallerManaged,
    RequireNonblockingSocket,
};

enum class SyncReplicaTlsRecordReadProgress {
    Progress,
    WantRead,
    WantWrite,
    Complete,
    PeerClosed,
};

enum class SyncReplicaTlsRecordWriteProgress {
    Progress,
    WantRead,
    WantWrite,
    Complete,
};

enum class SyncReplicaTlsSocketReadiness {
    Readable,
    Writable,
};

// Advisory event-loop target for one exact pending SSL_read_ex() or
// SSL_write_ex() retry. The descriptor number is not authority: lookup
// re-proves the captured socket lifetime and O_NONBLOCK state, and
// advance_or_throw() proves them again before it re-enters OpenSSL. Raw
// descriptor mutation still must be serialized.
struct SyncReplicaTlsSocketReadinessTarget final {
    int descriptor = -1;
    SyncReplicaTlsSocketReadiness readiness =
        SyncReplicaTlsSocketReadiness::Readable;

    bool operator==(const SyncReplicaTlsSocketReadinessTarget&) const = default;
};

enum class SyncReplicaTlsRecordWriteReadinessPolicy {
    CallerManaged,
    RequireNonblockingSocket,
};

inline constexpr std::string_view kSyncReplicaTlsAlpn =
    "anonsync-replica-delivery-v1";
inline constexpr std::string_view kSyncReplicaTlsExporterLabel =
    "EXPORTER-Channel-Binding";
inline constexpr std::uint64_t kSyncReplicaTlsExporterBytes = 32U;
inline constexpr std::uint64_t kSyncReplicaTlsRecordPrefixBytes = 8U;
inline constexpr std::uint64_t kSyncReplicaTlsRecordReadStepBytes =
    64U * 1024U;
inline constexpr std::uint64_t kSyncReplicaTlsRecordWriteStepBytes =
    64U * 1024U;

static_assert(
    !kSyncReplicaTlsAlpn.empty() && kSyncReplicaTlsAlpn.size() <= 255U);

// Installs the process-wide SIGPIPE disposition required by socket-backed TLS.
// OpenSSL writes through socket BIOs without MSG_NOSIGNAL; a peer closing at an
// unlucky write boundary must become an ordinary TLS/transport result, never
// terminate the C++ service process. Call once before starting network threads
// or exposing listeners. The ignore disposition intentionally lasts for the
// remaining process lifetime.
void install_sync_replica_sigpipe_ignore_policy_or_throw(
    std::string_view label = "sync replica SIGPIPE policy");

// The membership layer supplies an exact actor epoch and a pinned SHA-256 of
// that actor's DER SubjectPublicKeyInfo. The certificate chain remains useful
// for rejecting malformed/untrusted handshakes, while the pin prevents a
// generic trust anchor from silently authorizing the wrong replica identity.
struct SyncReplicaTlsPeerPolicy final {
    SyncReplicaActor actor;
    std::string spki_sha256;

    bool operator==(const SyncReplicaTlsPeerPolicy&) const = default;
};

// Applies the non-negotiable transport profile before SSL objects are created:
// TLS 1.3 only, exact delivery ALPN, peer verification enabled, early data
// disabled, unexpected EOF kept distinct from close_notify, AUTO_RETRY enabled,
// asynchronous-engine retry disabled, read-ahead disabled, and quiet shutdown
// disabled. The server profile also requires a client certificate and disables
// tickets until membership-aware resumption policy exists. Certificate, key,
// trust-store, revocation, and verification-depth configuration remain owned by
// the caller and must be installed on the same context.
void configure_sync_replica_tls13_client_context_or_throw(
    SSL_CTX* context,
    const std::string& label = "sync replica TLS client context");

void configure_sync_replica_tls13_server_context_or_throw(
    SSL_CTX* context,
    const std::string& label = "sync replica TLS server context");

// Returns the lowercase SHA-256 of the verified peer certificate's DER
// SubjectPublicKeyInfo. This value is public identity material, not a secret.
[[nodiscard]] std::string sync_replica_tls_peer_spki_sha256_or_throw(
    SSL* ssl,
    const std::string& label = "sync replica TLS peer SPKI");

// Opaque proof that one live SSL object, on one exact handshake, completed the
// TLS profile and passed the caller-supplied actor/SPKI membership check. The
// shared authenticated state retains one OpenSSL reference, retains both exact BIO objects
// observed at the authentication-time capability frontier, and therefore lets
// the caller release its original SSL reference after authentication. For
// direct socket BIOs, the state also binds each descriptor to one exact Linux
// stream-socket lifetime; a descriptor number is not authority. BIO replacement
// or an in-place BIO descriptor change is rejected before later channel use.
//
// It remains the caller's responsibility not to clear, re-handshake, or race
// the same SSL or BIO objects concurrently. The capability freezes the exact
// authentication-time SSL option mask, mode mask, read-ahead, quiet-shutdown,
// peer-verification mode, and zero shutdown state. Later observable mutation is
// rejected and poisons the capability before record I/O or durable authority;
// transient mutate-and-restore activity cannot be observed without exclusive
// ownership of the raw SSL handle. A retained custom/filter BIO pointer does not
// prove the identity of mutable transport hidden behind that BIO; strict
// nonblocking record mode therefore requires direct socket BIOs.
//
// Both record I/O and delivery-service authority revalidate the exact live peer
// SPKI, exporter binding, authentication-time transport anchor, and record-I/O
// policy before use. Pending WANT target disclosure and exact retry reprove the
// transport and record policy without interposing between I/O and SSL_get_error.
// The state is bound to the creating
// process and exact thread lifetime: use after fork fail-stops, and a foreign
// thread is rejected before OpenSSL or durable owner access. Any partial record
// transfer or invalid peer frame poisons this state permanently because a byte
// stream cannot be safely resynchronized after an uncertain framing cutpoint.
class SyncReplicaTlsAuthenticatedChannel final {
public:
    SyncReplicaTlsAuthenticatedChannel(
        const SyncReplicaTlsAuthenticatedChannel&) = delete;
    SyncReplicaTlsAuthenticatedChannel& operator=(
        const SyncReplicaTlsAuthenticatedChannel&) = delete;
    SyncReplicaTlsAuthenticatedChannel(
        SyncReplicaTlsAuthenticatedChannel&& other) noexcept;
    SyncReplicaTlsAuthenticatedChannel& operator=(
        SyncReplicaTlsAuthenticatedChannel&& other) noexcept;
    ~SyncReplicaTlsAuthenticatedChannel() noexcept;

    [[nodiscard]] const SyncReplicaDeliveryChannelAuthority&
    delivery_authority() const noexcept {
        return delivery_authority_;
    }

    [[nodiscard]] const SyncReplicaDeliveryChannelContext&
    delivery_context() const noexcept {
        return delivery_authority_.context();
    }

private:
    friend SyncReplicaTlsAuthenticatedChannel
    authenticate_sync_replica_tls13_channel_or_throw(
        SSL*, const SyncReplicaTlsPeerPolicy&, const std::string&);
    friend void write_sync_replica_tls_record_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string_view,
        std::uint64_t, const std::string&);
    friend SyncReplicaTlsRecordWriteContinuation
    prepare_sync_replica_tls_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string_view,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);
    friend SyncReplicaTlsRecordWriteContinuation
    prepare_sync_replica_tls_owned_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);
    friend SyncReplicaTlsRecordWriteContinuation
    begin_sync_replica_tls_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string_view,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);
    friend SyncReplicaTlsRecordReadContinuation
    begin_sync_replica_tls_record_read_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::uint64_t,
        SyncReplicaTlsRecordReadReadinessPolicy, const std::string&);
    friend void discard_sync_replica_tls_authenticated_channel_noexcept(
        const SyncReplicaTlsAuthenticatedChannel&) noexcept;

    SyncReplicaTlsAuthenticatedChannel(
        std::shared_ptr<detail::SyncReplicaTlsAuthenticatedState> state,
        SyncReplicaDeliveryChannelContext delivery_context);

    [[nodiscard]] detail::SyncReplicaTlsAuthenticatedState&
    state_or_throw(std::string_view label) const;

    std::shared_ptr<detail::SyncReplicaTlsAuthenticatedState> state_;
    SyncReplicaDeliveryChannelAuthority delivery_authority_;
};

// Move-only ownership of one complete framed TLS record write. The ordinary
// begin... factory below returns this value only after the complete 8-byte
// AnonSync record-length prefix has been accepted. The prepare... factory
// returns the same owner before any application byte is attempted, allowing an
// event-loop owner to retain an exact WANT_READ or WANT_WRITE during the prefix
// as well as the body. Neither state is proof of peer receipt: OpenSSL may still
// buffer ciphertext and any remaining transfer may still fail.
//
// The borrowed factory copies the exact frame into heap-stable private state;
// the owned factory transfers one already-owned string into that same state.
// Both happen after bounds validation and before stream reservation. A caller
// therefore cannot substitute a different length or same-length body across any
// retry or prefix/body cutpoint, and moving this wrapper cannot change the
// pointer or length required by a pending SSL_write_ex() retry. Each advance
// performs at most one bounded prefix or body write request.
//
// The continuation exclusively reserves the channel's record-write stream; a
// second begin, generic record write, or record read is rejected until it is
// complete or abandoned. WantRead and WantWrite are integrated through
// pending_readiness_or_throw() under the same exact socket-lifetime policy as
// the reader. The operation must remain on its creating process and thread.
// Destroying an untouched prepared owner releases its reservation without
// poisoning because no OpenSSL operation or stream progress exists. Abandoning,
// destroying, or move-assigning after any write attempt permanently poisons the
// authenticated stream: even a zero-byte WANT owns one exact pending OpenSSL
// operation that cannot be replaced safely. Foreign-owner cleanup fails stopped
// before it may mutate the shared TLS state.
class SyncReplicaTlsRecordWriteContinuation final {
public:
    SyncReplicaTlsRecordWriteContinuation(
        const SyncReplicaTlsRecordWriteContinuation&) = delete;
    SyncReplicaTlsRecordWriteContinuation& operator=(
        const SyncReplicaTlsRecordWriteContinuation&) = delete;
    SyncReplicaTlsRecordWriteContinuation(
        SyncReplicaTlsRecordWriteContinuation&& other) noexcept;
    SyncReplicaTlsRecordWriteContinuation& operator=(
        SyncReplicaTlsRecordWriteContinuation&& other) noexcept;
    ~SyncReplicaTlsRecordWriteContinuation() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool io_started() const noexcept;
    [[nodiscard]] std::uint64_t prefix_bytes_written() const noexcept;
    [[nodiscard]] bool prefix_complete() const noexcept;
    [[nodiscard]] std::uint64_t frame_bytes() const noexcept;
    [[nodiscard]] std::uint64_t body_bytes_written() const noexcept;

    [[nodiscard]] SyncReplicaTlsRecordWriteProgress advance_or_throw();
    [[nodiscard]] SyncReplicaTlsSocketReadinessTarget
        pending_readiness_or_throw() const;
    void finish_or_throw();

private:
    friend SyncReplicaTlsRecordWriteContinuation
    prepare_sync_replica_tls_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string_view,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);
    friend SyncReplicaTlsRecordWriteContinuation
    prepare_sync_replica_tls_owned_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);
    friend SyncReplicaTlsRecordWriteContinuation
    begin_sync_replica_tls_record_write_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::string_view,
        std::uint64_t, SyncReplicaTlsRecordWriteReadinessPolicy,
        const std::string&);

    explicit SyncReplicaTlsRecordWriteContinuation(
        std::unique_ptr<detail::SyncReplicaTlsRecordWriteState> state) noexcept;

    std::unique_ptr<detail::SyncReplicaTlsRecordWriteState> state_;
};

// Move-only ownership of one incremental SSL_read_ex() operation for a single
// framed AnonSync record. The continuation reserves the channel's entire TLS
// application-data stream until a complete frame, clean pre-frame peer close,
// or terminal failure is observed. Reads and writes cannot overlap on the same
// SSL object, including through the delivery-authority verifier.
//
// The prefix and body storage live in a heap-stable private state. Moving this
// public wrapper therefore cannot change the exact buffer pointer or length
// that OpenSSL requires when SSL_ERROR_WANT_READ or SSL_ERROR_WANT_WRITE makes
// an SSL_read_ex() call retryable. Each advance performs at most one SSL read.
// The caller integrates WantRead/WantWrite with its event loop and must retry on
// the creating process and thread. pending_readiness_or_throw() exposes the
// descriptor/event pair for polling only after a WANT. Lookup fails closed if
// the socket identity is already stale; because the pending OpenSSL operation
// can no longer be resumed, that failure abandons this continuation and poisons
// the channel. The returned integer remains advisory and never substitutes for
// the continuation's retry-frontier identity proof.
//
// Destruction before the first attempted SSL read releases the reservation
// without poisoning because no stream progress is possible.
// Abandonment after any attempted read permanently poisons the channel. That
// includes a retryable WANT result because the pending OpenSSL operation cannot
// be transferred or safely replaced. A clean TLS close before any frame byte is
// a distinct PeerClosed terminal state; a close after partial framing is
// truncation and poisons the channel. Foreign-process or foreign-thread cleanup fails stopped
// before mutating the shared SSL owner.
class SyncReplicaTlsRecordReadContinuation final {
public:
    SyncReplicaTlsRecordReadContinuation(
        const SyncReplicaTlsRecordReadContinuation&) = delete;
    SyncReplicaTlsRecordReadContinuation& operator=(
        const SyncReplicaTlsRecordReadContinuation&) = delete;
    SyncReplicaTlsRecordReadContinuation(
        SyncReplicaTlsRecordReadContinuation&& other) noexcept;
    SyncReplicaTlsRecordReadContinuation& operator=(
        SyncReplicaTlsRecordReadContinuation&& other) noexcept;
    ~SyncReplicaTlsRecordReadContinuation() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool frame_ready() const noexcept;
    [[nodiscard]] bool peer_closed() const noexcept;
    [[nodiscard]] std::uint64_t prefix_bytes_received() const noexcept;
    [[nodiscard]] std::uint64_t frame_bytes() const noexcept;
    [[nodiscard]] std::uint64_t body_bytes_received() const noexcept;

    [[nodiscard]] SyncReplicaTlsRecordReadProgress advance_or_throw();
    [[nodiscard]] SyncReplicaTlsSocketReadinessTarget
        pending_readiness_or_throw() const;
    [[nodiscard]] std::string take_frame_or_throw();

private:
    friend SyncReplicaTlsRecordReadContinuation
    begin_sync_replica_tls_record_read_or_throw(
        const SyncReplicaTlsAuthenticatedChannel&, std::uint64_t,
        SyncReplicaTlsRecordReadReadinessPolicy, const std::string&);

    explicit SyncReplicaTlsRecordReadContinuation(
        std::unique_ptr<detail::SyncReplicaTlsRecordReadState> state) noexcept;

    std::unique_ptr<detail::SyncReplicaTlsRecordReadState> state_;
};

// Requires a completed, successfully verified TLS 1.3 handshake with the
// exact AnonSync delivery ALPN, checks the peer SPKI pin against caller-supplied
// membership authority, and derives an RFC 9266 tls-exporter binding. The
// returned capability is the only public input accepted by delivery record I/O.
[[nodiscard]] SyncReplicaTlsAuthenticatedChannel
    authenticate_sync_replica_tls13_channel_or_throw(
        SSL* ssl,
        const SyncReplicaTlsPeerPolicy& expected_peer,
        const std::string& label = "sync replica TLS channel");

// Permanently invalidates this local authenticated stream capability without
// attempting TLS shutdown or network I/O. This is the fail-closed application
// sequencing operation for a complete request whose response is abandoned: a
// later request cannot silently reuse bytes from the old conversation. Calling
// it on an empty channel is harmless. Process/thread authority remains
// fail-stop, and any outstanding continuation is likewise rendered unusable.
void discard_sync_replica_tls_authenticated_channel_noexcept(
    const SyncReplicaTlsAuthenticatedChannel& channel) noexcept;

// Validates the exact authenticated channel and frame ceiling, freezes the
// complete prefix/body bytes in heap-stable storage, reserves the record-write
// stream, and returns before issuing SSL_write_ex(). This is the bounded
// event-loop entry point for owners that must retain readiness backpressure at
// the first prefix operation. Destruction before advance_or_throw() safely
// releases the idle reservation; destruction after any attempted operation is
// fail-closed as documented on the continuation.
[[nodiscard]] SyncReplicaTlsRecordWriteContinuation
prepare_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label);

// Same record authority as the borrowed factory, but transfers one complete
// caller-owned frame into the continuation instead of copying it. The by-value
// argument makes the ownership cutpoint explicit: callers must pass an rvalue
// when they intend to relinquish a page-sized protocol frame before network
// backpressure begins.
[[nodiscard]] SyncReplicaTlsRecordWriteContinuation
prepare_sync_replica_tls_owned_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label);

// Validates the exact authenticated channel and frame ceiling, writes the
// complete encrypted 8-byte record prefix, then returns the only capability
// that may write the corresponding body.  All potentially-throwing local
// continuation construction happens before the prefix write, so a successful
// prefix cannot be followed by an unreported handoff-allocation failure.
//
// A database or queue owner can therefore retain its own serialization guard
// through this call, commit that guard after the continuation is returned, and
// release it before the potentially large body transfer.  A blocking SSL object
// still requires an application-owned send timeout; the byte count is bounded,
// but this function does not invent a wall-clock deadline.
//
// The policy overload is used by database/transport composition. Requiring a
// nonblocking socket proves that the current read/write BIOs are the exact
// authentication-time BIO objects, that their direct SOCK_STREAM descriptors
// still name the anchored Linux socket lifetimes, and that current O_NONBLOCK
// policy is set immediately before the prefix. The accepted-prefix/body
// frontier repeats transport, readiness, peer, and exporter validation.
// Filtered/custom BIOs, non-socket descriptors, and unsupported exact-lifetime
// platforms fail closed rather than holding a durable writer on uncertain I/O.
[[nodiscard]] SyncReplicaTlsRecordWriteContinuation
begin_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label);

[[nodiscard]] SyncReplicaTlsRecordWriteContinuation
begin_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    const std::string& label = "sync replica TLS record prefix");

// One encrypted stream record is an unsigned big-endian length followed by one
// canonical delivery frame. The prefix itself is inside TLS. A receiver checks
// the advertised size before allocating or reading the body. These helpers are
// intended for blocking SSL objects whose underlying descriptor has an
// application-owned timeout; they fail rather than spin on nonblocking WANT.
void write_sync_replica_tls_record_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    const std::string& label = "sync replica TLS write");

// Reserves one authenticated TLS stream and returns an incremental record
// reader. Requiring a nonblocking socket proves the exact authentication-time
// BIO objects, direct SOCK_STREAM socket lifetimes, and current O_NONBLOCK
// policy before the reservation, at pending poll-target disclosure, before each
// fresh read operation, and before every exact WANT retry. The returned poll
// descriptor remains advisory. The caller-managed overload is retained for
// blocking adapters and tests whose descriptor deadlines are established
// outside this library.
[[nodiscard]] SyncReplicaTlsRecordReadContinuation
begin_sync_replica_tls_record_read_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordReadReadinessPolicy readiness_policy,
    const std::string& label);

[[nodiscard]] SyncReplicaTlsRecordReadContinuation
begin_sync_replica_tls_record_read_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    const std::string& label = "sync replica TLS record read");

[[nodiscard]] std::string read_sync_replica_tls_record_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    const std::string& label = "sync replica TLS read");

}  // namespace anonsync
