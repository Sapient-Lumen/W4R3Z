#include "sync_replica_tls_io_policy.hpp"

#include <stdexcept>
#include <string>

namespace anonsync::detail {
namespace {

[[nodiscard]] std::string message(
    std::string_view label,
    std::string_view detail) {
    std::string result(label);
    result.append(detail);
    return result;
}

[[nodiscard]] SyncReplicaTlsIoPolicy observe_tls_io_policy_or_throw(
    SSL* ssl,
    std::string_view label) {
    if (ssl == nullptr) {
        throw std::invalid_argument(message(label, " SSL handle is null"));
    }
    return {
        SSL_get_options(ssl),
        SSL_get_mode(ssl),
        SSL_get_read_ahead(ssl),
        SSL_get_quiet_shutdown(ssl),
        SSL_get_verify_mode(ssl),
        SSL_get_shutdown(ssl),
    };
}

void validate_tls_io_policy_is_safe_or_throw(
    const SyncReplicaTlsIoPolicy& policy,
    std::string_view label) {
    if ((policy.options & SSL_OP_IGNORE_UNEXPECTED_EOF) != 0U) {
        throw std::runtime_error(message(
            label,
            " refuses SSL_OP_IGNORE_UNEXPECTED_EOF because abrupt transport "
            "close is not clean TLS peer closure"));
    }
    if ((policy.modes & SSL_MODE_AUTO_RETRY) == 0L) {
        throw std::runtime_error(message(
            label,
            " requires SSL_MODE_AUTO_RETRY so WANT readiness is not exposed "
            "while OpenSSL still owns processable non-application data"));
    }
    if ((policy.modes & SSL_MODE_ASYNC) != 0L) {
        throw std::runtime_error(message(
            label,
            " refuses SSL_MODE_ASYNC because only socket read/write readiness "
            "is an owned continuation frontier"));
    }
    if (policy.read_ahead != 0) {
        throw std::runtime_error(message(
            label,
            " refuses TLS read-ahead because strict record progress owns one "
            "bounded OpenSSL read frontier at a time"));
    }
    if (policy.quiet_shutdown != 0) {
        throw std::runtime_error(message(
            label,
            " refuses quiet TLS shutdown because clean closure requires peer "
            "close_notify evidence"));
    }
    if ((policy.verify_mode & SSL_VERIFY_PEER) == 0) {
        throw std::runtime_error(message(
            label, " TLS peer verification mode is disabled"));
    }
    if (policy.shutdown_state != 0) {
        throw std::runtime_error(message(
            label,
            " refuses an SSL object whose shutdown state is already nonzero"));
    }
}

}  // namespace

void configure_sync_replica_tls_io_policy_or_throw(
    SSL_CTX* context,
    std::string_view label) {
    if (context == nullptr) {
        throw std::invalid_argument(message(label, " SSL_CTX handle is null"));
    }

    (void)SSL_CTX_clear_options(context, SSL_OP_IGNORE_UNEXPECTED_EOF);
    (void)SSL_CTX_set_mode(context, SSL_MODE_AUTO_RETRY);
    (void)SSL_CTX_clear_mode(context, SSL_MODE_ASYNC);
    SSL_CTX_set_read_ahead(context, 0);
    SSL_CTX_set_quiet_shutdown(context, 0);

    if ((SSL_CTX_get_options(context) & SSL_OP_IGNORE_UNEXPECTED_EOF) != 0U ||
        (SSL_CTX_get_mode(context) & SSL_MODE_AUTO_RETRY) == 0L ||
        (SSL_CTX_get_mode(context) & SSL_MODE_ASYNC) != 0L ||
        SSL_CTX_get_read_ahead(context) != 0 ||
        SSL_CTX_get_quiet_shutdown(context) != 0) {
        throw std::runtime_error(message(
            label, " could not apply the strict TLS record-I/O policy"));
    }
}

SyncReplicaTlsIoPolicy capture_sync_replica_tls_io_policy_or_throw(
    SSL* ssl,
    std::string_view label) {
    const SyncReplicaTlsIoPolicy policy =
        observe_tls_io_policy_or_throw(ssl, label);
    validate_tls_io_policy_is_safe_or_throw(policy, label);
    return policy;
}

void reprove_sync_replica_tls_io_policy_or_throw(
    SSL* ssl,
    const SyncReplicaTlsIoPolicy& expected,
    std::string_view label) {
    const SyncReplicaTlsIoPolicy current =
        observe_tls_io_policy_or_throw(ssl, label);
    if (current.options != expected.options) {
        throw std::runtime_error(message(
            label, " TLS option mask changed after authentication"));
    }
    if (current.modes != expected.modes) {
        throw std::runtime_error(message(
            label, " TLS mode mask changed after authentication"));
    }
    if (current.read_ahead != expected.read_ahead) {
        throw std::runtime_error(message(
            label, " TLS read-ahead policy changed after authentication"));
    }
    if (current.quiet_shutdown != expected.quiet_shutdown) {
        throw std::runtime_error(message(
            label,
            " TLS quiet-shutdown policy changed after authentication"));
    }
    if (current.verify_mode != expected.verify_mode) {
        throw std::runtime_error(message(
            label,
            " TLS peer-verification mode changed after authentication"));
    }
    if (current.shutdown_state != expected.shutdown_state) {
        throw std::runtime_error(message(
            label, " TLS shutdown state changed after authentication"));
    }

    // Exact equality is the authority check. The safety check documents and
    // preserves the invariant if policy construction is later refactored.
    validate_tls_io_policy_is_safe_or_throw(current, label);
}

}  // namespace anonsync::detail
