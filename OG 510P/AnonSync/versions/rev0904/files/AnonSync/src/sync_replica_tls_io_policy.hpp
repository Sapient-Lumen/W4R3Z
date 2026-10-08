#pragma once

#include <cstdint>
#include <string_view>

#include <openssl/ssl.h>

namespace anonsync::detail {

// Exact application-mutable SSL record semantics captured at authentication.
// Peer identity, exporter binding, BIO identity, and kernel socket lifetime do
// not bind these switches, even though they change EOF, shutdown, and retry
// behavior. Equality is therefore an authority check, not configuration trivia.
struct SyncReplicaTlsIoPolicy final {
    std::uint64_t options = 0U;
    long modes = 0L;
    int read_ahead = 0;
    int quiet_shutdown = 0;
    int verify_mode = 0;
    int shutdown_state = 0;

    bool operator==(const SyncReplicaTlsIoPolicy&) const = default;
};

// Normalizes the context defaults inherited by subsequently created SSL
// objects. Per-SSL overrides remain possible and are rejected by capture and
// reproof below.
void configure_sync_replica_tls_io_policy_or_throw(
    SSL_CTX* context,
    std::string_view label);

// Captures one safe, exact record-I/O policy after the handshake. Unsafe EOF,
// retry, asynchronous-engine, read-ahead, quiet-shutdown, verification, or
// shutdown-state semantics are rejected before a capability can be published.
[[nodiscard]] SyncReplicaTlsIoPolicy
capture_sync_replica_tls_io_policy_or_throw(
    SSL* ssl,
    std::string_view label);

// Requires exact equality with the authentication-time policy and then
// rechecks the semantic safety invariant. Observable mutation is authority
// loss even when the new value appears independently safe.
void reprove_sync_replica_tls_io_policy_or_throw(
    SSL* ssl,
    const SyncReplicaTlsIoPolicy& expected,
    std::string_view label);

}  // namespace anonsync::detail
