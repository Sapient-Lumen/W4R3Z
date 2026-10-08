#include "sync_replica_tls_transport.hpp"

#include "sha256_digest.hpp"
#include "sync_replica_tls_io_policy.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_socket_readiness_identity.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <signal.h>

#include <openssl/crypto.h>
#include <openssl/err.h>
#include <openssl/x509.h>

namespace anonsync {

void install_sync_replica_sigpipe_ignore_policy_or_throw(
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica SIGPIPE policy label must not be empty");
    }
#if defined(SIGPIPE)
    struct sigaction ignored_action {};
    ignored_action.sa_handler = SIG_IGN;
    if (::sigemptyset(&ignored_action.sa_mask) != 0) {
        const int error_number = errno;
        throw std::runtime_error(
            label + " could not initialize the SIGPIPE signal mask: " +
            std::to_string(error_number));
    }
    ignored_action.sa_flags = 0;
    if (::sigaction(SIGPIPE, &ignored_action, nullptr) != 0) {
        const int error_number = errno;
        throw std::runtime_error(
            label + " could not install the SIGPIPE ignore disposition: " +
            std::to_string(error_number));
    }

    struct sigaction observed_action {};
    if (::sigaction(SIGPIPE, nullptr, &observed_action) != 0) {
        const int error_number = errno;
        throw std::runtime_error(
            label + " could not re-observe the SIGPIPE disposition: " +
            std::to_string(error_number));
    }
    if (observed_action.sa_handler != SIG_IGN) {
        throw std::runtime_error(
            label + " SIGPIPE ignore disposition did not remain installed");
    }
#else
    // Platforms without SIGPIPE do not need the POSIX socket-write policy.
    (void)label;
#endif
}

namespace {

using PeerCertificate = std::unique_ptr<X509, decltype(&X509_free)>;
// A retained top-level BIO can also be the head of a caller-managed filter
// chain. SSL releases owned BIOs with BIO_free_all(); the independent anchor
// must do the same when its final retained reference reaches zero, otherwise
// BIO_free() would destroy only the head and leak every downstream BIO.
using BioReference = std::unique_ptr<BIO, decltype(&BIO_free_all)>;

// The authenticated capability retains both exact BIO objects so a later
// SSL_set_fd/SSL_set_bio cannot free and recycle an old pointer into apparent
// continuity. Direct socket BIOs additionally carry immutable kernel lifetime
// evidence captured during authentication; O_NONBLOCK remains a separately
// re-proved readiness policy.
struct SyncReplicaTlsTransportAnchor final {
    SyncReplicaTlsTransportAnchor(
        BioReference read_bio_value,
        BioReference write_bio_value,
        std::optional<SyncSocketLifetimeIdentity> read_socket_value,
        std::optional<SyncSocketLifetimeIdentity> write_socket_value) noexcept
        : read_bio(std::move(read_bio_value)),
          write_bio(std::move(write_bio_value)),
          read_socket(std::move(read_socket_value)),
          write_socket(std::move(write_socket_value)) {}

    SyncReplicaTlsTransportAnchor(const SyncReplicaTlsTransportAnchor&) = delete;
    SyncReplicaTlsTransportAnchor& operator=(
        const SyncReplicaTlsTransportAnchor&) = delete;
    SyncReplicaTlsTransportAnchor(
        SyncReplicaTlsTransportAnchor&&) noexcept = default;
    SyncReplicaTlsTransportAnchor& operator=(
        SyncReplicaTlsTransportAnchor&&) noexcept = default;

    BioReference read_bio;
    BioReference write_bio;
    std::optional<SyncSocketLifetimeIdentity> read_socket;
    std::optional<SyncSocketLifetimeIdentity> write_socket;
};

[[nodiscard]] std::string openssl_error_suffix() {
    const unsigned long code = ERR_get_error();
    if (code == 0UL) return {};
    std::array<char, 256U> buffer{};
    ERR_error_string_n(code, buffer.data(), buffer.size());
    return std::string(": ") + buffer.data();
}

[[nodiscard]] std::string delivery_alpn_wire_or_throw(
    const std::string& label) {
    if (kSyncReplicaTlsAlpn.empty() || kSyncReplicaTlsAlpn.size() > 255U) {
        throw std::logic_error(label + " delivery ALPN length is invalid");
    }
    std::string wire(
        1U, static_cast<char>(kSyncReplicaTlsAlpn.size()));
    wire.append(kSyncReplicaTlsAlpn);
    return wire;
}

int select_delivery_alpn(
    SSL*,
    const unsigned char** selected,
    unsigned char* selected_bytes,
    const unsigned char* offered,
    unsigned int offered_bytes,
    void*) noexcept {
    if (selected == nullptr || selected_bytes == nullptr ||
        offered == nullptr) {
        return SSL_TLSEXT_ERR_ALERT_FATAL;
    }
    std::size_t position = 0U;
    while (position < offered_bytes) {
        const std::size_t length = offered[position++];
        if (length == 0U || length > offered_bytes - position) {
            return SSL_TLSEXT_ERR_ALERT_FATAL;
        }
        if (length == kSyncReplicaTlsAlpn.size() &&
            CRYPTO_memcmp(
                offered + position, kSyncReplicaTlsAlpn.data(),
                length) == 0) {
            *selected = offered + position;
            *selected_bytes = static_cast<unsigned char>(length);
            return SSL_TLSEXT_ERR_OK;
        }
        position += length;
    }
    return SSL_TLSEXT_ERR_ALERT_FATAL;
}

void configure_context_common_or_throw(
    SSL_CTX* context,
    bool server,
    const std::string& label) {
    if (context == nullptr) {
        throw std::invalid_argument(label + " SSL_CTX handle is null");
    }
    ERR_clear_error();
    if (SSL_CTX_set_min_proto_version(context, TLS1_3_VERSION) != 1 ||
        SSL_CTX_set_max_proto_version(context, TLS1_3_VERSION) != 1 ||
        SSL_CTX_set_max_early_data(context, 0U) != 1) {
        throw std::runtime_error(
            label + " could not apply the TLS 1.3 profile" +
            openssl_error_suffix());
    }
    // Normalize record-I/O semantics inherited by subsequently created SSL
    // objects. Authentication captures and every authority use re-proves the
    // exact per-SSL result, so a later override cannot inherit old authority.
    detail::configure_sync_replica_tls_io_policy_or_throw(context, label);

    SSL_CTX_set_verify(
        context,
        SSL_VERIFY_PEER |
            (server ? SSL_VERIFY_FAIL_IF_NO_PEER_CERT : 0),
        nullptr);
    if (server) {
        if (SSL_CTX_set_num_tickets(context, 0U) != 1) {
            throw std::runtime_error(
                label + " could not disable TLS session tickets" +
                openssl_error_suffix());
        }
        SSL_CTX_set_alpn_select_cb(context, select_delivery_alpn, nullptr);
        return;
    }

    const std::string wire = delivery_alpn_wire_or_throw(label);
    if (SSL_CTX_set_alpn_protos(
            context,
            reinterpret_cast<const unsigned char*>(wire.data()),
            static_cast<unsigned int>(wire.size())) != 0) {
        throw std::runtime_error(
            label + " could not configure the delivery ALPN" +
            openssl_error_suffix());
    }
}

void validate_ssl_ready_or_throw(SSL* ssl, const std::string& label) {
    if (ssl == nullptr) {
        throw std::invalid_argument(label + " SSL handle is null");
    }
    if (SSL_is_init_finished(ssl) != 1) {
        throw std::invalid_argument(
            label + " TLS handshake is not complete");
    }
    if (SSL_version(ssl) != TLS1_3_VERSION) {
        throw std::invalid_argument(label + " requires TLS 1.3");
    }
    if (SSL_session_reused(ssl) != 0) {
        throw std::runtime_error(
            label + " refuses TLS session resumption before membership-aware policy exists");
    }
    if (SSL_get_early_data_status(ssl) != SSL_EARLY_DATA_NOT_SENT) {
        throw std::runtime_error(
            label + " refuses a TLS connection that attempted early data");
    }
}

void validate_peer_verification_or_throw(
    SSL* ssl,
    const std::string& label) {
    validate_ssl_ready_or_throw(ssl, label);
    if ((SSL_get_verify_mode(ssl) & SSL_VERIFY_PEER) == 0) {
        throw std::runtime_error(
            label + " TLS peer verification mode is disabled");
    }
    if (SSL_get_verify_result(ssl) != X509_V_OK) {
        throw std::runtime_error(
            label + " peer certificate verification did not succeed");
    }
}

void validate_delivery_alpn_or_throw(
    SSL* ssl,
    const std::string& label) {
    const unsigned char* selected = nullptr;
    unsigned int selected_bytes = 0U;
    SSL_get0_alpn_selected(ssl, &selected, &selected_bytes);
    if (selected == nullptr ||
        selected_bytes != kSyncReplicaTlsAlpn.size() ||
        CRYPTO_memcmp(
            selected, kSyncReplicaTlsAlpn.data(), selected_bytes) != 0) {
        throw std::runtime_error(
            label + " did not negotiate the exact AnonSync delivery ALPN");
    }
}

void validate_delivery_tls_or_throw(
    SSL* ssl,
    const std::string& label) {
    validate_peer_verification_or_throw(ssl, label);
    validate_delivery_alpn_or_throw(ssl, label);
}

void validate_peer_policy_or_throw(
    const SyncReplicaTlsPeerPolicy& policy,
    const std::string& label) {
    if (!sync_id_is_valid(policy.actor.device_id) || policy.actor.epoch == 0U) {
        throw std::invalid_argument(
            label + " expected peer actor identity is invalid");
    }
    if (!is_lowercase_sha256_hex(policy.spki_sha256)) {
        throw std::invalid_argument(
            label + " expected peer SPKI pin is not lowercase SHA-256");
    }
}

[[nodiscard]] std::array<unsigned char, 32U> hex_to_sha256_bytes_or_throw(
    std::string_view value,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(value)) {
        throw std::invalid_argument(label + " is not lowercase SHA-256");
    }
    std::array<unsigned char, 32U> output{};
    const auto nibble = [](char character) -> unsigned char {
        if (character >= '0' && character <= '9') {
            return static_cast<unsigned char>(character - '0');
        }
        return static_cast<unsigned char>(character - 'a' + 10);
    };
    for (std::size_t index = 0U; index < output.size(); ++index) {
        output[index] = static_cast<unsigned char>(
            (nibble(value[index * 2U]) << 4U) |
            nibble(value[index * 2U + 1U]));
    }
    return output;
}

[[nodiscard]] std::string peer_spki_sha256_after_profile_or_throw(
    SSL* ssl,
    const std::string& label) {
    PeerCertificate certificate(
        SSL_get1_peer_certificate(ssl), X509_free);
    if (!certificate) {
        throw std::runtime_error(label + " peer certificate is absent");
    }
    X509_PUBKEY* public_key = X509_get_X509_PUBKEY(certificate.get());
    if (public_key == nullptr) {
        throw std::runtime_error(
            label + " peer SubjectPublicKeyInfo is absent");
    }

    const int encoded_bytes = i2d_X509_PUBKEY(public_key, nullptr);
    if (encoded_bytes <= 0) {
        throw std::runtime_error(
            label + " could not size peer SubjectPublicKeyInfo" +
            openssl_error_suffix());
    }
    std::string encoded(static_cast<std::size_t>(encoded_bytes), '\0');
    unsigned char* output = reinterpret_cast<unsigned char*>(encoded.data());
    const int written = i2d_X509_PUBKEY(public_key, &output);
    if (written != encoded_bytes) {
        throw std::runtime_error(
            label + " could not encode peer SubjectPublicKeyInfo" +
            openssl_error_suffix());
    }
    return sha256_hex(encoded);
}

[[nodiscard]] SyncReplicaDeliveryChannelBinding
tls_exporter_binding_after_profile_or_throw(
    SSL* ssl,
    const std::string& label) {
    std::array<unsigned char, kSyncReplicaTlsExporterBytes> exporter{};
    ERR_clear_error();
    if (SSL_export_keying_material(
            ssl,
            exporter.data(), exporter.size(),
            kSyncReplicaTlsExporterLabel.data(),
            kSyncReplicaTlsExporterLabel.size(),
            nullptr, 0U, 0) != 1) {
        throw std::runtime_error(
            label + " could not derive RFC 9266 tls-exporter binding" +
            openssl_error_suffix());
    }
    return make_sync_replica_delivery_channel_binding_or_throw(
        "tls-exporter",
        std::string_view(
            reinterpret_cast<const char*>(exporter.data()),
            exporter.size()));
}

void validate_authenticated_session_or_throw(
    SSL* ssl,
    std::string_view expected_peer_spki_sha256,
    const SyncReplicaDeliveryChannelBinding& expected_binding,
    const std::string& label) {
    validate_delivery_tls_or_throw(ssl, label);
    const auto expected_spki = hex_to_sha256_bytes_or_throw(
        expected_peer_spki_sha256, label + " authenticated peer SPKI");
    const auto actual_spki = hex_to_sha256_bytes_or_throw(
        peer_spki_sha256_after_profile_or_throw(
            ssl, label + " live peer SPKI"),
        label + " live peer SPKI");
    if (CRYPTO_memcmp(
            expected_spki.data(), actual_spki.data(),
            expected_spki.size()) != 0) {
        throw std::runtime_error(
            label + " live peer SPKI changed after authentication");
    }
    if (tls_exporter_binding_after_profile_or_throw(
            ssl, label + " live session") != expected_binding) {
        throw std::runtime_error(
            label + " TLS session binding changed after authentication");
    }
}

[[nodiscard]] std::uint64_t checked_size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(label + " does not fit uint64_t");
        }
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::size_t checked_u64_to_size_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value > std::numeric_limits<std::size_t>::max()) {
        throw std::overflow_error(label + " does not fit size_t");
    }
    return static_cast<std::size_t>(value);
}

[[nodiscard]] BioReference retain_tls_bio_reference_or_throw(
    BIO* bio,
    std::string_view label,
    std::string_view direction) {
    if (bio == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " TLS " + std::string(direction) +
            " BIO is absent");
    }
    ERR_clear_error();
    if (BIO_up_ref(bio) != 1) {
        throw std::runtime_error(
            std::string(label) + " could not retain its TLS " +
            std::string(direction) + " BIO" + openssl_error_suffix());
    }
    return BioReference(bio, BIO_free_all);
}

[[nodiscard]] std::optional<SyncSocketLifetimeIdentity>
observe_direct_tls_stream_socket_lifetime_or_throw(
    BIO* bio,
    std::string_view label,
    std::string_view direction) {
    if (BIO_method_type(bio) != BIO_TYPE_SOCKET) return std::nullopt;
#ifdef __linux__
    const int descriptor = BIO_get_fd(bio, nullptr);
    if (descriptor < 0) {
        throw std::invalid_argument(
            std::string(label) + " direct socket TLS " +
            std::string(direction) + " BIO has no observable descriptor");
    }
    return observe_sync_stream_socket_lifetime_or_throw(
        descriptor,
        std::string(label) + " TLS " + std::string(direction) +
            " socket lifetime");
#else
    // BIO object identity is still retained everywhere. Strict nonblocking
    // readiness remains unavailable until a platform supplies an equivalent
    // kernel socket-lifetime observer.
    (void)label;
    (void)direction;
    return std::nullopt;
#endif
}

void validate_tls_transport_anchor_direction_or_throw(
    BIO* current_bio,
    BIO* expected_bio,
    const std::optional<SyncSocketLifetimeIdentity>& expected_socket,
    std::string_view label,
    std::string_view direction) {
    if (current_bio != expected_bio) {
        throw std::runtime_error(
            std::string(label) + " TLS " + std::string(direction) +
            " BIO changed after authentication");
    }
    if (!expected_socket.has_value()) return;
    if (BIO_method_type(current_bio) != BIO_TYPE_SOCKET) {
        throw std::runtime_error(
            std::string(label) + " TLS " + std::string(direction) +
            " BIO lost its direct socket method after authentication");
    }
    const int descriptor = BIO_get_fd(current_bio, nullptr);
    if (descriptor != expected_socket->descriptor()) {
        throw std::runtime_error(
            std::string(label) + " TLS " + std::string(direction) +
            " socket descriptor changed after authentication");
    }
    reprove_sync_stream_socket_lifetime_or_throw(
        *expected_socket,
        std::string(label) + " TLS " + std::string(direction) +
            " socket lifetime");
}

void validate_tls_transport_anchor_or_throw(
    SSL* ssl,
    const SyncReplicaTlsTransportAnchor& expected,
    std::string_view label) {
    BIO* const current_read_bio = SSL_get_rbio(ssl);
    BIO* const current_write_bio = SSL_get_wbio(ssl);
    validate_tls_transport_anchor_direction_or_throw(
        current_read_bio, expected.read_bio.get(), expected.read_socket,
        label, "read");
    validate_tls_transport_anchor_direction_or_throw(
        current_write_bio, expected.write_bio.get(), expected.write_socket,
        label, "write");
}

void require_tls_transport_anchor_nonblocking_or_throw(
    const SyncReplicaTlsTransportAnchor& expected,
    std::string_view label) {
    if (!expected.read_socket.has_value() ||
        !expected.write_socket.has_value()) {
        throw std::invalid_argument(
            std::string(label) +
            " requires authentication-anchored direct socket TLS read and write BIOs for bounded readiness");
    }
    require_sync_stream_socket_nonblocking_or_throw(
        *expected.read_socket,
        std::string(label) + " TLS read socket readiness");
    require_sync_stream_socket_nonblocking_or_throw(
        *expected.write_socket,
        std::string(label) + " TLS write socket readiness");
}

[[nodiscard]] SyncReplicaTlsTransportAnchor
capture_tls_transport_anchor_or_throw(
    SSL* ssl,
    std::string_view label) {
    BIO* const read_bio = SSL_get_rbio(ssl);
    BIO* const write_bio = SSL_get_wbio(ssl);
    if (read_bio == nullptr || write_bio == nullptr) {
        throw std::invalid_argument(
            std::string(label) +
            " requires observable TLS read and write BIOs at authentication");
    }

    BioReference retained_read = retain_tls_bio_reference_or_throw(
        read_bio, label, "read");
    BioReference retained_write = retain_tls_bio_reference_or_throw(
        write_bio, label, "write");
    std::optional<SyncSocketLifetimeIdentity> read_socket =
        observe_direct_tls_stream_socket_lifetime_or_throw(
            read_bio, label, "read");
    std::optional<SyncSocketLifetimeIdentity> write_socket;
    if (write_bio == read_bio && read_socket.has_value()) {
        write_socket = read_socket;
    } else {
        write_socket = observe_direct_tls_stream_socket_lifetime_or_throw(
            write_bio, label, "write");
    }

    SyncReplicaTlsTransportAnchor anchor(
        std::move(retained_read), std::move(retained_write),
        std::move(read_socket), std::move(write_socket));
    validate_tls_transport_anchor_or_throw(
        ssl, anchor,
        std::string(label) + " authentication transport capture");
    return anchor;
}

void validate_record_limit_or_throw(
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    if (max_frame_bytes == 0U) {
        throw std::invalid_argument(label + " maximum frame bytes must be positive");
    }
    (void)checked_u64_to_size_or_throw(
        max_frame_bytes, label + " maximum frame bytes");
}

[[nodiscard]] std::array<unsigned char, 8U> encode_u64_be(
    std::uint64_t value) noexcept {
    std::array<unsigned char, 8U> output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        const std::size_t shift = (output.size() - 1U - index) * 8U;
        output[index] = static_cast<unsigned char>(value >> shift);
    }
    return output;
}

[[nodiscard]] std::uint64_t decode_u64_be(
    const std::array<unsigned char, 8U>& bytes) noexcept {
    std::uint64_t value = 0U;
    for (const unsigned char byte : bytes) {
        value = (value << 8U) | static_cast<std::uint64_t>(byte);
    }
    return value;
}

}  // namespace

namespace detail {

enum class SyncReplicaTlsRecordReservation {
    Idle,
    Read,
    Write,
};

enum class SyncReplicaTlsPendingReadiness {
    None,
    Readable,
    Writable,
};

}  // namespace detail

class detail::SyncReplicaTlsAuthenticatedState final
    : public detail::SyncReplicaDeliveryChannelVerifier {
public:
    SyncReplicaTlsAuthenticatedState(
        SSL* ssl,
        std::string peer_spki_sha256,
        SyncReplicaDeliveryChannelBinding binding,
        SyncReplicaTlsTransportAnchor transport_anchor,
        detail::SyncReplicaTlsIoPolicy io_policy)
        : peer_spki_sha256_(std::move(peer_spki_sha256)),
          binding_(std::move(binding)),
          transport_anchor_(std::move(transport_anchor)),
          io_policy_(io_policy),
          owner_process_(current_sync_process_incarnation_noexcept()),
          owner_thread_(current_sync_thread_incarnation_noexcept()) {
        if (ssl == nullptr) {
            throw std::invalid_argument(
                "sync replica authenticated TLS state SSL handle is null");
        }
        if (!is_lowercase_sha256_hex(peer_spki_sha256_)) {
            throw std::invalid_argument(
                "sync replica authenticated TLS state peer SPKI is invalid");
        }
        validate_sync_replica_delivery_channel_binding_or_throw(
            binding_, "sync replica authenticated TLS state");
        if (!owner_process_.valid() || !owner_thread_.valid()) {
            throw std::logic_error(
                "sync replica authenticated TLS state could not bind live process/thread authority");
        }
        validate_tls_transport_anchor_or_throw(
            ssl, transport_anchor_,
            "sync replica authenticated TLS state transport anchor");
        detail::reprove_sync_replica_tls_io_policy_or_throw(
            ssl, io_policy_,
            "sync replica authenticated TLS state record-I/O policy");
        ERR_clear_error();
        if (SSL_up_ref(ssl) != 1) {
            throw std::runtime_error(
                "sync replica authenticated TLS state could not retain its SSL object" +
                openssl_error_suffix());
        }
        // No operation below this point may throw: the state now owns one SSL
        // reference in addition to its independently retained BIO references.
        ssl_ = ssl;
    }

    SyncReplicaTlsAuthenticatedState(
        const SyncReplicaTlsAuthenticatedState&) = delete;
    SyncReplicaTlsAuthenticatedState& operator=(
        const SyncReplicaTlsAuthenticatedState&) = delete;

    ~SyncReplicaTlsAuthenticatedState() override {
        release_ssl_noexcept();
    }

    void validate_or_throw(std::string_view label) const override {
        require_current_or_throw(label);
        require_usable_or_throw(label);
        require_record_idle_or_throw(label);
        validate_authenticated_channel_and_poison_or_throw(label);
    }

    [[nodiscard]] SSL* begin_record_write_or_throw(
        std::string_view label,
        bool require_nonblocking_socket) const {
        validate_or_throw(label);
        if (require_nonblocking_socket) {
            require_nonblocking_transport_policy_or_throw(label, false);
        }
        record_reservation_ = SyncReplicaTlsRecordReservation::Write;
        return ssl_;
    }

    void begin_record_read_or_throw(
        std::string_view label,
        bool require_nonblocking_socket) const {
        validate_or_throw(label);
        if (require_nonblocking_socket) {
            require_nonblocking_transport_policy_or_throw(label, false);
        }
        record_reservation_ = SyncReplicaTlsRecordReservation::Read;
    }

    void require_record_owner_or_throw(
        SyncReplicaTlsRecordReservation expected,
        std::string_view label) const {
        require_current_or_throw(label);
        require_usable_or_throw(label);
        if (record_reservation_ != expected) {
            const std::string_view direction =
                expected == SyncReplicaTlsRecordReservation::Write
                    ? "write"
                    : "read";
            throw std::logic_error(
                std::string(label) +
                " authenticated TLS stream lost its record-" +
                std::string(direction) + " reservation");
        }
    }

    [[nodiscard]] SSL* active_record_io_or_throw(
        SyncReplicaTlsRecordReservation expected,
        std::string_view label,
        bool require_nonblocking_socket,
        bool retry_pending) const {
        require_record_owner_or_throw(expected, label);
        if (retry_pending) {
            // One exact OpenSSL I/O operation is still pending. Read-only BIO
            // and descriptor lookup is necessary for event-loop integration,
            // but peer/session queries are deferred until the operation has
            // completed. The retained BIO pointers, authenticated socket
            // lifetimes, and current O_NONBLOCK policy are re-proved before the
            // exact retry.
            if (require_nonblocking_socket) {
                // The strict policy helper includes one exact BIO/socket-anchor
                // proof before checking both current O_NONBLOCK flags. Avoid a
                // redundant preceding anchor walk at every retry.
                require_nonblocking_transport_policy_or_throw(label, true);
            } else {
                validate_transport_anchor_and_poison_or_throw(label);
            }
            validate_io_policy_and_poison_or_throw(label);
            return ssl_;
        }

        // A successful SSL_read_ex or SSL_write_ex call completed the previous
        // OpenSSL operation. A fresh step re-attests peer/session identity and
        // the authentication-time BIO/socket anchor before entering OpenSSL.
        validate_authenticated_channel_and_poison_or_throw(label);
        if (require_nonblocking_socket) {
            require_nonblocking_transport_policy_or_throw(label, true);
        }
        return ssl_;
    }

    [[nodiscard]] SyncReplicaTlsSocketReadinessTarget
    pending_readiness_target_or_throw(
        SyncReplicaTlsRecordReservation expected,
        SyncReplicaTlsPendingReadiness pending,
        std::string_view label) const {
        require_record_owner_or_throw(expected, label);

        bool writable = false;
        SyncReplicaTlsSocketReadiness public_readiness =
            SyncReplicaTlsSocketReadiness::Readable;
        switch (pending) {
            case SyncReplicaTlsPendingReadiness::Readable:
                break;
            case SyncReplicaTlsPendingReadiness::Writable:
                writable = true;
                public_readiness = SyncReplicaTlsSocketReadiness::Writable;
                break;
            case SyncReplicaTlsPendingReadiness::None:
                throw std::logic_error(
                    std::string(label) +
                    " TLS record operation has no pending readiness request");
        }

        // This helper already re-proves the exact BIO/socket anchor before
        // checking both current readiness flags; one walk is sufficient at
        // advisory target disclosure.
        require_nonblocking_transport_policy_or_throw(label, true);
        validate_io_policy_and_poison_or_throw(label);

        const auto& socket = writable
            ? transport_anchor_.write_socket
            : transport_anchor_.read_socket;
        if (!socket.has_value()) {
            poisoned_ = true;
            const std::string_view direction =
                expected == SyncReplicaTlsRecordReservation::Write
                    ? "write"
                    : "read";
            throw std::logic_error(
                std::string(label) +
                " strict TLS " + std::string(direction) +
                " lost its authentication socket anchor");
        }
        return {socket->descriptor(), public_readiness};
    }

    void complete_record_write_noexcept() const noexcept {
        require_owner_or_fail_stop_noexcept();
        if (record_reservation_ != SyncReplicaTlsRecordReservation::Write) {
            poisoned_ = true;
            record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
            return;
        }
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
    }

    void abandon_record_write_noexcept(bool io_started) const noexcept {
        require_owner_or_fail_stop_noexcept();
        if (record_reservation_ != SyncReplicaTlsRecordReservation::Write) {
            poisoned_ = true;
            record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
            return;
        }
        if (io_started) poisoned_ = true;
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
    }

    void complete_record_read_noexcept() const noexcept {
        require_owner_or_fail_stop_noexcept();
        if (record_reservation_ != SyncReplicaTlsRecordReservation::Read) {
            poisoned_ = true;
            record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
            return;
        }
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
    }

    void abandon_record_read_noexcept(bool io_started) const noexcept {
        require_owner_or_fail_stop_noexcept();
        if (record_reservation_ != SyncReplicaTlsRecordReservation::Read) {
            poisoned_ = true;
            record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
            return;
        }
        if (io_started) poisoned_ = true;
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
    }

    void close_record_read_noexcept() const noexcept {
        require_owner_or_fail_stop_noexcept();
        if (record_reservation_ != SyncReplicaTlsRecordReservation::Read) {
            poisoned_ = true;
            record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
            return;
        }
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
        closed_ = true;
    }

    void poison_noexcept() const noexcept {
        require_owner_or_fail_stop_noexcept();
        poisoned_ = true;
        record_reservation_ = SyncReplicaTlsRecordReservation::Idle;
    }

private:
    void require_current_or_throw(std::string_view label) const {
        if (ssl_ == nullptr) {
            throw std::logic_error(
                std::string(label) +
                " authenticated TLS state has no SSL object");
        }
        require_sync_process_incarnation_or_fail_stop(owner_process_, label);
        require_sync_thread_incarnation_or_throw(owner_thread_, label);
    }

    void require_usable_or_throw(std::string_view label) const {
        if (poisoned_) {
            throw std::runtime_error(
                std::string(label) +
                " authenticated TLS stream is poisoned and must be discarded");
        }
        if (closed_) {
            throw std::runtime_error(
                std::string(label) +
                " authenticated TLS stream is closed by its peer and must be discarded");
        }
    }

    void require_record_idle_or_throw(std::string_view label) const {
        switch (record_reservation_) {
            case SyncReplicaTlsRecordReservation::Idle:
                return;
            case SyncReplicaTlsRecordReservation::Read:
                throw std::logic_error(
                    std::string(label) +
                    " authenticated TLS stream already owns an unfinished record read");
            case SyncReplicaTlsRecordReservation::Write:
                throw std::logic_error(
                    std::string(label) +
                    " authenticated TLS stream already owns an unfinished record write");
        }
        throw std::logic_error(
            std::string(label) +
            " authenticated TLS stream has an unknown record reservation");
    }

    void validate_transport_anchor_and_poison_or_throw(
        std::string_view label) const {
        try {
            validate_tls_transport_anchor_or_throw(
                ssl_, transport_anchor_, label);
        } catch (...) {
            poisoned_ = true;
            throw;
        }
    }

    void require_nonblocking_transport_policy_or_throw(
        std::string_view label,
        bool poison_on_failure) const {
        validate_transport_anchor_and_poison_or_throw(label);
        try {
            require_tls_transport_anchor_nonblocking_or_throw(
                transport_anchor_, label);
        } catch (...) {
            if (poison_on_failure) poisoned_ = true;
            throw;
        }
    }

    void validate_io_policy_and_poison_or_throw(
        std::string_view label) const {
        try {
            detail::reprove_sync_replica_tls_io_policy_or_throw(ssl_, io_policy_, label);
        } catch (...) {
            poisoned_ = true;
            throw;
        }
    }

    void validate_authenticated_channel_and_poison_or_throw(
        std::string_view label) const {
        try {
            validate_tls_transport_anchor_or_throw(
                ssl_, transport_anchor_, label);
            detail::reprove_sync_replica_tls_io_policy_or_throw(
                ssl_, io_policy_, label);
            validate_authenticated_session_or_throw(
                ssl_, peer_spki_sha256_, binding_, std::string(label));
        } catch (...) {
            poisoned_ = true;
            throw;
        }
    }

    void require_owner_or_fail_stop_noexcept() const noexcept {
        if (!sync_process_incarnation_is_current(owner_process_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (!sync_thread_incarnation_is_current(owner_thread_)) {
            fail_stop_on_sync_thread_capability_violation_noexcept();
        }
    }

    void release_ssl_noexcept() noexcept {
        if (ssl_ == nullptr) return;
        require_owner_or_fail_stop_noexcept();
        SSL_free(std::exchange(ssl_, nullptr));
    }

    SSL* ssl_ = nullptr;
    std::string peer_spki_sha256_;
    SyncReplicaDeliveryChannelBinding binding_;
    SyncReplicaTlsTransportAnchor transport_anchor_;
    detail::SyncReplicaTlsIoPolicy io_policy_;
    SyncProcessIncarnation owner_process_;
    SyncThreadIncarnation owner_thread_;
    mutable bool poisoned_ = false;
    mutable bool closed_ = false;
    mutable SyncReplicaTlsRecordReservation record_reservation_ =
        SyncReplicaTlsRecordReservation::Idle;
};

class detail::SyncReplicaTlsRecordWriteState final {
public:
    enum class Terminal {
        Writing,
        Complete,
    };

    SyncReplicaTlsRecordWriteState(
        std::shared_ptr<SyncReplicaTlsAuthenticatedState> authenticated_state_value,
        std::string frame_value,
        bool require_nonblocking_socket_value,
        std::string label_value)
        : authenticated_state(std::move(authenticated_state_value)),
          frame(std::move(frame_value)),
          prefix(encode_u64_be(static_cast<std::uint64_t>(frame.size()))),
          require_nonblocking_socket(require_nonblocking_socket_value),
          label(std::move(label_value)) {}

    SyncReplicaTlsRecordWriteState(
        const SyncReplicaTlsRecordWriteState&) = delete;
    SyncReplicaTlsRecordWriteState& operator=(
        const SyncReplicaTlsRecordWriteState&) = delete;

    ~SyncReplicaTlsRecordWriteState() noexcept {
        abandon_noexcept();
    }

    void abandon_noexcept() noexcept {
        if (reservation_active && authenticated_state) {
            authenticated_state->abandon_record_write_noexcept(io_started);
        }
        reservation_active = false;
        authenticated_state.reset();
    }

    std::shared_ptr<SyncReplicaTlsAuthenticatedState> authenticated_state;
    std::string frame;
    std::array<unsigned char, kSyncReplicaTlsRecordPrefixBytes> prefix{};
    bool require_nonblocking_socket = false;
    std::string label;
    std::size_t prefix_offset = 0U;
    std::size_t body_offset = 0U;
    std::size_t pending_offset = 0U;
    std::size_t pending_bytes = 0U;
    bool pending_prefix = true;
    bool reservation_active = false;
    bool io_started = false;
    bool retry_pending = false;
    SyncReplicaTlsPendingReadiness pending_readiness =
        SyncReplicaTlsPendingReadiness::None;
    Terminal terminal = Terminal::Writing;
};

class detail::SyncReplicaTlsRecordReadState final {
public:
    enum class Terminal {
        Reading,
        Complete,
        PeerClosed,
    };

    SyncReplicaTlsRecordReadState(
        std::shared_ptr<SyncReplicaTlsAuthenticatedState> authenticated_state_value,
        std::uint64_t max_frame_bytes_value,
        bool require_nonblocking_socket_value,
        std::string label_value)
        : authenticated_state(std::move(authenticated_state_value)),
          max_frame_bytes(max_frame_bytes_value),
          require_nonblocking_socket(require_nonblocking_socket_value),
          label(std::move(label_value)) {}

    SyncReplicaTlsRecordReadState(const SyncReplicaTlsRecordReadState&) = delete;
    SyncReplicaTlsRecordReadState& operator=(
        const SyncReplicaTlsRecordReadState&) = delete;

    ~SyncReplicaTlsRecordReadState() noexcept {
        abandon_noexcept();
    }

    void abandon_noexcept() noexcept {
        if (reservation_active && authenticated_state) {
            authenticated_state->abandon_record_read_noexcept(io_started);
        }
        reservation_active = false;
        authenticated_state.reset();
    }

    std::shared_ptr<SyncReplicaTlsAuthenticatedState> authenticated_state;
    std::uint64_t max_frame_bytes = 0U;
    bool require_nonblocking_socket = false;
    std::string label;
    std::array<unsigned char, kSyncReplicaTlsRecordPrefixBytes> prefix{};
    std::size_t prefix_offset = 0U;
    std::uint64_t frame_bytes = 0U;
    std::string frame;
    std::size_t body_offset = 0U;
    bool reservation_active = false;
    bool io_started = false;
    bool retry_pending = false;
    SyncReplicaTlsPendingReadiness pending_readiness =
        SyncReplicaTlsPendingReadiness::None;
    Terminal terminal = Terminal::Reading;
};

SyncReplicaTlsAuthenticatedChannel::SyncReplicaTlsAuthenticatedChannel(
    std::shared_ptr<detail::SyncReplicaTlsAuthenticatedState> state,
    SyncReplicaDeliveryChannelContext delivery_context)
    : state_(std::move(state)),
      delivery_authority_(
          std::move(delivery_context), state_,
          "sync replica authenticated TLS delivery channel") {
    if (!state_) {
        throw std::invalid_argument(
            "sync replica authenticated TLS channel state is null");
    }
}

SyncReplicaTlsAuthenticatedChannel::SyncReplicaTlsAuthenticatedChannel(
    SyncReplicaTlsAuthenticatedChannel&& other) noexcept
    : state_(std::move(other.state_)),
      delivery_authority_(std::move(other.delivery_authority_)) {}

SyncReplicaTlsAuthenticatedChannel&
SyncReplicaTlsAuthenticatedChannel::operator=(
    SyncReplicaTlsAuthenticatedChannel&& other) noexcept {
    if (this != &other) {
        state_ = std::move(other.state_);
        delivery_authority_ = std::move(other.delivery_authority_);
    }
    return *this;
}

SyncReplicaTlsAuthenticatedChannel::~SyncReplicaTlsAuthenticatedChannel()
    noexcept = default;

detail::SyncReplicaTlsAuthenticatedState&
SyncReplicaTlsAuthenticatedChannel::state_or_throw(
    std::string_view label) const {
    if (!state_) {
        throw std::logic_error(
            std::string(label) +
            " authenticated TLS channel is empty or moved-from");
    }
    return *state_;
}

SyncReplicaTlsRecordWriteContinuation::
    SyncReplicaTlsRecordWriteContinuation(
        std::unique_ptr<detail::SyncReplicaTlsRecordWriteState> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaTlsRecordWriteContinuation::
    SyncReplicaTlsRecordWriteContinuation(
        SyncReplicaTlsRecordWriteContinuation&& other) noexcept = default;

SyncReplicaTlsRecordWriteContinuation&
SyncReplicaTlsRecordWriteContinuation::operator=(
    SyncReplicaTlsRecordWriteContinuation&& other) noexcept = default;

SyncReplicaTlsRecordWriteContinuation::~SyncReplicaTlsRecordWriteContinuation()
    noexcept = default;

bool SyncReplicaTlsRecordWriteContinuation::active() const noexcept {
    return state_ != nullptr && state_->reservation_active &&
           state_->terminal ==
               detail::SyncReplicaTlsRecordWriteState::Terminal::Writing;
}

bool SyncReplicaTlsRecordWriteContinuation::io_started() const noexcept {
    return state_ != nullptr && state_->io_started;
}

std::uint64_t
SyncReplicaTlsRecordWriteContinuation::prefix_bytes_written() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->prefix_offset);
}

bool SyncReplicaTlsRecordWriteContinuation::prefix_complete() const noexcept {
    return state_ != nullptr &&
           state_->prefix_offset == state_->prefix.size();
}

std::uint64_t
SyncReplicaTlsRecordWriteContinuation::frame_bytes() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->frame.size());
}

std::uint64_t
SyncReplicaTlsRecordWriteContinuation::body_bytes_written() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->body_offset);
}

SyncReplicaTlsRecordWriteProgress
SyncReplicaTlsRecordWriteContinuation::advance_or_throw() {
    if (!active()) {
        throw std::logic_error(
            "sync replica TLS record write continuation is not active");
    }

    try {
        if (state_->frame.empty() ||
            state_->prefix_offset > state_->prefix.size() ||
            state_->body_offset > state_->frame.size() ||
            (state_->prefix_offset != state_->prefix.size() &&
             state_->body_offset != 0U) ||
            (state_->prefix_offset == state_->prefix.size() &&
             state_->body_offset == state_->frame.size())) {
            throw std::logic_error(
                state_->label +
                " TLS record write state is internally invalid");
        }

        const bool writing_prefix =
            state_->prefix_offset != state_->prefix.size();
        const std::size_t current_offset = writing_prefix
            ? state_->prefix_offset
            : state_->body_offset;
        const std::size_t current_bytes = writing_prefix
            ? state_->prefix.size()
            : state_->frame.size();
        if (!state_->retry_pending) {
            state_->pending_prefix = writing_prefix;
            state_->pending_offset = current_offset;
            state_->pending_bytes = std::min(
                current_bytes - current_offset,
                static_cast<std::size_t>(
                    kSyncReplicaTlsRecordWriteStepBytes));
        }
        if (state_->pending_bytes == 0U ||
            state_->pending_prefix != writing_prefix ||
            state_->pending_offset != current_offset ||
            state_->pending_offset > current_bytes ||
            state_->pending_bytes >
                current_bytes - state_->pending_offset) {
            throw std::logic_error(
                state_->label +
                " TLS record write retry state is internally invalid");
        }

        SSL* const ssl = state_->authenticated_state->active_record_io_or_throw(
            detail::SyncReplicaTlsRecordReservation::Write,
            state_->label,
            state_->require_nonblocking_socket,
            state_->retry_pending);

        const void* const input = state_->pending_prefix
            ? static_cast<const void*>(
                  state_->prefix.data() + state_->pending_offset)
            : static_cast<const void*>(
                  state_->frame.data() + state_->pending_offset);
        std::size_t bytes_written = 0U;
        state_->io_started = true;
        ERR_clear_error();
        const int result = SSL_write_ex(
            ssl, input, state_->pending_bytes, &bytes_written);
        const int ssl_error =
            result == 1 ? SSL_ERROR_NONE : SSL_get_error(ssl, result);

        if (result != 1) {
            if (bytes_written != 0U) {
                throw std::runtime_error(
                    state_->label +
                    " SSL_write_ex reported failure with application bytes");
            }
            if (ssl_error == SSL_ERROR_WANT_READ) {
                state_->retry_pending = true;
                state_->pending_readiness =
                    detail::SyncReplicaTlsPendingReadiness::Readable;
                return SyncReplicaTlsRecordWriteProgress::WantRead;
            }
            if (ssl_error == SSL_ERROR_WANT_WRITE) {
                state_->retry_pending = true;
                state_->pending_readiness =
                    detail::SyncReplicaTlsPendingReadiness::Writable;
                return SyncReplicaTlsRecordWriteProgress::WantWrite;
            }
            state_->retry_pending = false;
            state_->pending_readiness =
                detail::SyncReplicaTlsPendingReadiness::None;
            throw SyncReplicaTlsSessionIoError(
                state_->label + " failed with SSL error " +
                std::to_string(ssl_error) + openssl_error_suffix());
        }

        state_->retry_pending = false;
        state_->pending_readiness =
            detail::SyncReplicaTlsPendingReadiness::None;
        if (bytes_written == 0U || bytes_written > state_->pending_bytes) {
            throw std::runtime_error(
                state_->label + " SSL_write_ex made invalid progress");
        }
        if (state_->pending_prefix) {
            state_->prefix_offset += bytes_written;
        } else {
            state_->body_offset += bytes_written;
        }
        state_->pending_offset = 0U;
        state_->pending_bytes = 0U;

        // Prefix completion is an explicit progress frontier. Do not issue a
        // body write in the same advance call: guarded dispatch can commit its
        // exact durable cutpoint, and bounded event loops can observe the
        // transition without hidden extra OpenSSL work.
        if (state_->pending_prefix) {
            return SyncReplicaTlsRecordWriteProgress::Progress;
        }
        if (state_->body_offset != state_->frame.size()) {
            return SyncReplicaTlsRecordWriteProgress::Progress;
        }

        state_->authenticated_state->complete_record_write_noexcept();
        state_->reservation_active = false;
        state_->authenticated_state.reset();
        state_->terminal =
            detail::SyncReplicaTlsRecordWriteState::Terminal::Complete;
        state_.reset();
        return SyncReplicaTlsRecordWriteProgress::Complete;
    } catch (...) {
        state_->abandon_noexcept();
        throw;
    }
}

SyncReplicaTlsSocketReadinessTarget
SyncReplicaTlsRecordWriteContinuation::pending_readiness_or_throw() const {
    if (!active()) {
        throw std::logic_error(
            "sync replica TLS record write continuation is not active");
    }
    if (!state_->require_nonblocking_socket) {
        throw std::logic_error(
            state_->label +
            " caller-managed TLS write has no library-owned poll target");
    }
    if (state_->pending_readiness ==
        detail::SyncReplicaTlsPendingReadiness::None) {
        throw std::logic_error(
            state_->label +
            " TLS record write has no pending readiness request");
    }

    try {
        return state_->authenticated_state->pending_readiness_target_or_throw(
            detail::SyncReplicaTlsRecordReservation::Write,
            state_->pending_readiness,
            state_->label + " pending write readiness target");
    } catch (...) {
        // A stale poll target means the exact pending SSL_write_ex operation
        // can no longer be resumed. Any attempted prefix or body write,
        // including a zero-byte WANT, owns one exact retry operation, so
        // abandonment permanently poisons the stream.
        state_->abandon_noexcept();
        throw;
    }
}

void SyncReplicaTlsRecordWriteContinuation::finish_or_throw() {
    if (!active()) {
        throw std::logic_error(
            "sync replica TLS record write continuation is empty or already finished");
    }
    try {
        for (;;) {
            switch (advance_or_throw()) {
                case SyncReplicaTlsRecordWriteProgress::Progress:
                    continue;
                case SyncReplicaTlsRecordWriteProgress::Complete:
                    return;
                case SyncReplicaTlsRecordWriteProgress::WantRead:
                case SyncReplicaTlsRecordWriteProgress::WantWrite:
                    throw std::runtime_error(
                        state_->label +
                        " reached nonblocking TLS readiness loss; this channel must be discarded");
            }
            throw std::logic_error(
                "sync replica TLS record write progress is unknown");
        }
    } catch (...) {
        if (state_) state_->abandon_noexcept();
        throw;
    }
}

SyncReplicaTlsRecordReadContinuation::
    SyncReplicaTlsRecordReadContinuation(
        std::unique_ptr<detail::SyncReplicaTlsRecordReadState> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaTlsRecordReadContinuation::
    SyncReplicaTlsRecordReadContinuation(
        SyncReplicaTlsRecordReadContinuation&& other) noexcept = default;

SyncReplicaTlsRecordReadContinuation&
SyncReplicaTlsRecordReadContinuation::operator=(
    SyncReplicaTlsRecordReadContinuation&& other) noexcept = default;

SyncReplicaTlsRecordReadContinuation::~SyncReplicaTlsRecordReadContinuation()
    noexcept = default;

bool SyncReplicaTlsRecordReadContinuation::active() const noexcept {
    return state_ != nullptr && state_->reservation_active;
}

bool SyncReplicaTlsRecordReadContinuation::frame_ready() const noexcept {
    return state_ != nullptr &&
           state_->terminal ==
               detail::SyncReplicaTlsRecordReadState::Terminal::Complete;
}

bool SyncReplicaTlsRecordReadContinuation::peer_closed() const noexcept {
    return state_ != nullptr &&
           state_->terminal ==
               detail::SyncReplicaTlsRecordReadState::Terminal::PeerClosed;
}

std::uint64_t
SyncReplicaTlsRecordReadContinuation::prefix_bytes_received() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->prefix_offset);
}

std::uint64_t
SyncReplicaTlsRecordReadContinuation::frame_bytes() const noexcept {
    return state_ == nullptr ? 0U : state_->frame_bytes;
}

std::uint64_t
SyncReplicaTlsRecordReadContinuation::body_bytes_received() const noexcept {
    return state_ == nullptr
        ? 0U
        : static_cast<std::uint64_t>(state_->body_offset);
}

SyncReplicaTlsRecordReadProgress
SyncReplicaTlsRecordReadContinuation::advance_or_throw() {
    if (!state_ || !state_->reservation_active ||
        state_->terminal !=
            detail::SyncReplicaTlsRecordReadState::Terminal::Reading) {
        throw std::logic_error(
            "sync replica TLS record read continuation is not active");
    }

    try {
        const bool reading_prefix =
            state_->prefix_offset < state_->prefix.size();
        if (!reading_prefix &&
            (state_->frame_bytes == 0U || state_->frame.empty() ||
             state_->body_offset >= state_->frame.size())) {
            throw std::logic_error(
                state_->label + " TLS record read state is internally invalid");
        }

        unsigned char* const output = reading_prefix
            ? state_->prefix.data() + state_->prefix_offset
            : reinterpret_cast<unsigned char*>(state_->frame.data()) +
                  state_->body_offset;
        const std::size_t remaining = reading_prefix
            ? state_->prefix.size() - state_->prefix_offset
            : state_->frame.size() - state_->body_offset;
        const std::size_t requested = reading_prefix
            ? remaining
            : std::min(
                  remaining,
                  static_cast<std::size_t>(
                      kSyncReplicaTlsRecordReadStepBytes));

        SSL* const ssl = state_->authenticated_state
            ->active_record_io_or_throw(
                detail::SyncReplicaTlsRecordReservation::Read,
                state_->label,
                state_->require_nonblocking_socket,
                state_->retry_pending);

        // The flag is set before entering OpenSSL. Even a retryable WANT may
        // leave one exact SSL_read_ex operation that must be resumed with the
        // same buffer and length, so later abandonment cannot release cleanly.
        state_->io_started = true;
        std::size_t bytes_read = 0U;
        ERR_clear_error();
        const int result = SSL_read_ex(
            ssl, output, requested, &bytes_read);
        const int ssl_error =
            result == 1 ? SSL_ERROR_NONE : SSL_get_error(ssl, result);

        if (result != 1) {
            if (bytes_read != 0U) {
                throw std::runtime_error(
                    state_->label +
                    " SSL_read_ex reported failure with application bytes");
            }
            if (ssl_error == SSL_ERROR_WANT_READ) {
                state_->retry_pending = true;
                state_->pending_readiness =
                    detail::SyncReplicaTlsPendingReadiness::Readable;
                return SyncReplicaTlsRecordReadProgress::WantRead;
            }
            if (ssl_error == SSL_ERROR_WANT_WRITE) {
                state_->retry_pending = true;
                state_->pending_readiness =
                    detail::SyncReplicaTlsPendingReadiness::Writable;
                return SyncReplicaTlsRecordReadProgress::WantWrite;
            }
            state_->retry_pending = false;
            state_->pending_readiness =
                detail::SyncReplicaTlsPendingReadiness::None;
            if (ssl_error == SSL_ERROR_ZERO_RETURN) {
                if (state_->prefix_offset == 0U &&
                    state_->frame_bytes == 0U &&
                    state_->body_offset == 0U) {
                    state_->authenticated_state->close_record_read_noexcept();
                    state_->reservation_active = false;
                    state_->authenticated_state.reset();
                    state_->terminal = detail::SyncReplicaTlsRecordReadState::
                        Terminal::PeerClosed;
                    return SyncReplicaTlsRecordReadProgress::PeerClosed;
                }
                throw SyncReplicaTlsSessionIoError(
                    state_->label +
                    " peer closed TLS before the complete record");
            }
            throw SyncReplicaTlsSessionIoError(
                state_->label + " failed with SSL error " +
                std::to_string(ssl_error) + openssl_error_suffix());
        }

        state_->retry_pending = false;
        state_->pending_readiness =
            detail::SyncReplicaTlsPendingReadiness::None;
        if (bytes_read == 0U || bytes_read > requested) {
            throw std::runtime_error(
                state_->label + " SSL_read_ex made invalid progress");
        }

        if (reading_prefix) {
            state_->prefix_offset += bytes_read;
            if (state_->prefix_offset == state_->prefix.size()) {
                state_->frame_bytes = decode_u64_be(state_->prefix);
                if (state_->frame_bytes == 0U) {
                    throw std::invalid_argument(
                        state_->label + " peer advertised an empty frame");
                }
                if (state_->frame_bytes > state_->max_frame_bytes) {
                    throw std::length_error(
                        state_->label +
                        " peer advertised a frame above the configured limit");
                }
                const std::size_t allocation = checked_u64_to_size_or_throw(
                    state_->frame_bytes,
                    state_->label + " peer frame size");
                state_->frame.assign(allocation, '\0');
            }
            return SyncReplicaTlsRecordReadProgress::Progress;
        }

        state_->body_offset += bytes_read;
        if (state_->body_offset != state_->frame.size()) {
            return SyncReplicaTlsRecordReadProgress::Progress;
        }

        state_->authenticated_state->complete_record_read_noexcept();
        state_->reservation_active = false;
        state_->authenticated_state.reset();
        state_->terminal =
            detail::SyncReplicaTlsRecordReadState::Terminal::Complete;
        return SyncReplicaTlsRecordReadProgress::Complete;
    } catch (...) {
        state_->abandon_noexcept();
        throw;
    }
}

SyncReplicaTlsSocketReadinessTarget
SyncReplicaTlsRecordReadContinuation::pending_readiness_or_throw() const {
    if (!state_ || !state_->reservation_active ||
        state_->terminal !=
            detail::SyncReplicaTlsRecordReadState::Terminal::Reading) {
        throw std::logic_error(
            "sync replica TLS record read continuation is not active");
    }
    if (!state_->require_nonblocking_socket) {
        throw std::logic_error(
            state_->label +
            " caller-managed TLS read has no library-owned poll target");
    }
    if (state_->pending_readiness ==
        detail::SyncReplicaTlsPendingReadiness::None) {
        throw std::logic_error(
            state_->label +
            " TLS record read has no pending readiness request");
    }

    try {
        return state_->authenticated_state->pending_readiness_target_or_throw(
            detail::SyncReplicaTlsRecordReservation::Read,
            state_->pending_readiness,
            state_->label + " pending read readiness target");
    } catch (...) {
        // A stale poll target means the exact pending SSL_read_ex operation can
        // no longer be resumed. io_started keeps the shared stream poisoned.
        state_->abandon_noexcept();
        throw;
    }
}


std::string SyncReplicaTlsRecordReadContinuation::take_frame_or_throw() {
    if (!state_ ||
        state_->terminal !=
            detail::SyncReplicaTlsRecordReadState::Terminal::Complete) {
        throw std::logic_error(
            "sync replica TLS record read continuation has no complete frame");
    }
    std::string frame = std::move(state_->frame);
    state_.reset();
    return frame;
}

void configure_sync_replica_tls13_client_context_or_throw(
    SSL_CTX* context,
    const std::string& label) {
    configure_context_common_or_throw(context, false, label);
}

void configure_sync_replica_tls13_server_context_or_throw(
    SSL_CTX* context,
    const std::string& label) {
    configure_context_common_or_throw(context, true, label);
}

std::string sync_replica_tls_peer_spki_sha256_or_throw(
    SSL* ssl,
    const std::string& label) {
    validate_delivery_tls_or_throw(ssl, label);
    return peer_spki_sha256_after_profile_or_throw(ssl, label);
}

SyncReplicaTlsAuthenticatedChannel
authenticate_sync_replica_tls13_channel_or_throw(
    SSL* ssl,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    const std::string& label) {
    validate_ssl_ready_or_throw(ssl, label);
    validate_peer_policy_or_throw(expected_peer, label);
    validate_delivery_tls_or_throw(ssl, label);

    // Retain the exact BIO objects and, for direct socket BIOs, their kernel
    // lifetimes before deriving the final channel binding. The retained refs
    // make pointer equality resistant to allocator-address reuse if a caller
    // later invokes SSL_set_fd/SSL_set_bio.
    SyncReplicaTlsTransportAnchor transport_anchor =
        capture_tls_transport_anchor_or_throw(
            ssl, label + " authenticated transport");
    const detail::SyncReplicaTlsIoPolicy io_policy =
        detail::capture_sync_replica_tls_io_policy_or_throw(
            ssl, label + " authenticated record-I/O policy");

    const std::string actual_spki =
        peer_spki_sha256_after_profile_or_throw(
            ssl, label + " peer SPKI");
    const auto expected_bytes = hex_to_sha256_bytes_or_throw(
        expected_peer.spki_sha256, label + " expected peer SPKI pin");
    const auto actual_bytes = hex_to_sha256_bytes_or_throw(
        actual_spki, label + " actual peer SPKI pin");
    if (CRYPTO_memcmp(
            expected_bytes.data(), actual_bytes.data(),
            expected_bytes.size()) != 0) {
        throw std::runtime_error(
            label + " peer SubjectPublicKeyInfo pin mismatch");
    }

    SyncReplicaDeliveryChannelBinding binding =
        tls_exporter_binding_after_profile_or_throw(
            ssl, label + " session");
    validate_tls_transport_anchor_or_throw(
        ssl, transport_anchor,
        label + " authenticated transport final reproof");
    detail::reprove_sync_replica_tls_io_policy_or_throw(
        ssl, io_policy,
        label + " authenticated record-I/O policy final reproof");
    SyncReplicaDeliveryChannelContext delivery_context{
        expected_peer.actor,
        binding,
    };
    auto state =
        std::make_shared<detail::SyncReplicaTlsAuthenticatedState>(
            ssl, actual_spki, std::move(binding),
            std::move(transport_anchor), io_policy);
    return SyncReplicaTlsAuthenticatedChannel(
        std::move(state), std::move(delivery_context));
}

void discard_sync_replica_tls_authenticated_channel_noexcept(
    const SyncReplicaTlsAuthenticatedChannel& channel) noexcept {
    if (channel.state_) channel.state_->poison_noexcept();
}

SyncReplicaTlsRecordWriteContinuation
prepare_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label) {
    validate_record_limit_or_throw(max_frame_bytes, label);
    const std::uint64_t frame_bytes = checked_size_to_u64_or_throw(
        frame.size(), label + " frame size");
    if (frame_bytes == 0U) {
        throw std::invalid_argument(label + " frame must not be empty");
    }
    if (frame_bytes > max_frame_bytes) {
        throw std::length_error(label + " frame exceeds configured limit");
    }
    // The only body copy occurs after the public ceiling is enforced and before
    // stream reservation. Prefix bytes, retry metadata, and diagnostics are all
    // heap-stable before an SSL_write_ex operation may begin.
    std::string owned_frame(frame);

    bool require_nonblocking_socket = false;
    switch (readiness_policy) {
        case SyncReplicaTlsRecordWriteReadinessPolicy::CallerManaged:
            break;
        case SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket:
            require_nonblocking_socket = true;
            break;
        default:
            throw std::invalid_argument(
                label + " record-write readiness policy is unknown");
    }

    detail::SyncReplicaTlsAuthenticatedState& authenticated_state =
        channel.state_or_throw(label);
    auto write_state =
        std::make_unique<detail::SyncReplicaTlsRecordWriteState>(
            channel.state_, std::move(owned_frame), require_nonblocking_socket,
            label);
    (void)authenticated_state.begin_record_write_or_throw(
        label, require_nonblocking_socket);
    write_state->reservation_active = true;
    return SyncReplicaTlsRecordWriteContinuation(std::move(write_state));
}

SyncReplicaTlsRecordWriteContinuation
prepare_sync_replica_tls_owned_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label) {
    validate_record_limit_or_throw(max_frame_bytes, label);
    const std::uint64_t frame_bytes = checked_size_to_u64_or_throw(
        frame.size(), label + " frame size");
    if (frame_bytes == 0U) {
        throw std::invalid_argument(label + " frame must not be empty");
    }
    if (frame_bytes > max_frame_bytes) {
        throw std::length_error(label + " frame exceeds configured limit");
    }

    bool require_nonblocking_socket = false;
    switch (readiness_policy) {
        case SyncReplicaTlsRecordWriteReadinessPolicy::CallerManaged:
            break;
        case SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket:
            require_nonblocking_socket = true;
            break;
        default:
            throw std::invalid_argument(
                label + " record-write readiness policy is unknown");
    }

    detail::SyncReplicaTlsAuthenticatedState& authenticated_state =
        channel.state_or_throw(label);
    auto write_state =
        std::make_unique<detail::SyncReplicaTlsRecordWriteState>(
            channel.state_, std::move(frame), require_nonblocking_socket,
            label);
    (void)authenticated_state.begin_record_write_or_throw(
        label, require_nonblocking_socket);
    write_state->reservation_active = true;
    return SyncReplicaTlsRecordWriteContinuation(std::move(write_state));
}

SyncReplicaTlsRecordWriteContinuation
begin_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordWriteReadinessPolicy readiness_policy,
    const std::string& label) {
    SyncReplicaTlsRecordWriteContinuation continuation =
        prepare_sync_replica_tls_record_write_or_throw(
            channel, frame, max_frame_bytes, readiness_policy, label);
    for (;;) {
        const SyncReplicaTlsRecordWriteProgress progress =
            continuation.advance_or_throw();
        if (continuation.prefix_complete()) return continuation;
        switch (progress) {
            case SyncReplicaTlsRecordWriteProgress::Progress:
                break;
            case SyncReplicaTlsRecordWriteProgress::WantRead:
            case SyncReplicaTlsRecordWriteProgress::WantWrite:
                throw std::runtime_error(
                    label +
                    " length prefix reached nonblocking TLS readiness loss; this channel must be discarded");
            case SyncReplicaTlsRecordWriteProgress::Complete:
                throw std::logic_error(
                    label +
                    " completed a framed TLS record before its prefix frontier");
        }
    }
}

SyncReplicaTlsRecordWriteContinuation
begin_sync_replica_tls_record_write_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    return begin_sync_replica_tls_record_write_or_throw(
        channel, frame, max_frame_bytes,
        SyncReplicaTlsRecordWriteReadinessPolicy::CallerManaged, label);
}

void write_sync_replica_tls_record_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    SyncReplicaTlsRecordWriteContinuation continuation =
        begin_sync_replica_tls_record_write_or_throw(
            channel, frame, max_frame_bytes, label);
    continuation.finish_or_throw();
}


SyncReplicaTlsRecordReadContinuation
begin_sync_replica_tls_record_read_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    SyncReplicaTlsRecordReadReadinessPolicy readiness_policy,
    const std::string& label) {
    validate_record_limit_or_throw(max_frame_bytes, label);

    bool require_nonblocking_socket = false;
    switch (readiness_policy) {
        case SyncReplicaTlsRecordReadReadinessPolicy::CallerManaged:
            break;
        case SyncReplicaTlsRecordReadReadinessPolicy::RequireNonblockingSocket:
            require_nonblocking_socket = true;
            break;
        default:
            throw std::invalid_argument(
                label + " record-read readiness policy is unknown");
    }

    detail::SyncReplicaTlsAuthenticatedState& authenticated_state =
        channel.state_or_throw(label);
    // Heap allocation, shared ownership, and diagnostic copying all precede the
    // stream reservation. Once reserved, constructing and returning the public
    // wrapper is a no-throw unique_ptr move.
    auto read_state =
        std::make_unique<detail::SyncReplicaTlsRecordReadState>(
            channel.state_, max_frame_bytes, require_nonblocking_socket, label);
    authenticated_state.begin_record_read_or_throw(
        label, require_nonblocking_socket);
    read_state->reservation_active = true;
    return SyncReplicaTlsRecordReadContinuation(std::move(read_state));
}

SyncReplicaTlsRecordReadContinuation
begin_sync_replica_tls_record_read_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    return begin_sync_replica_tls_record_read_or_throw(
        channel, max_frame_bytes,
        SyncReplicaTlsRecordReadReadinessPolicy::CallerManaged, label);
}

std::string read_sync_replica_tls_record_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    SyncReplicaTlsRecordReadContinuation continuation =
        begin_sync_replica_tls_record_read_or_throw(
            channel, max_frame_bytes,
            SyncReplicaTlsRecordReadReadinessPolicy::CallerManaged, label);
    for (;;) {
        switch (continuation.advance_or_throw()) {
            case SyncReplicaTlsRecordReadProgress::Progress:
                break;
            case SyncReplicaTlsRecordReadProgress::Complete:
                return continuation.take_frame_or_throw();
            case SyncReplicaTlsRecordReadProgress::PeerClosed:
                throw std::runtime_error(
                    label + " peer closed TLS before the complete record");
            case SyncReplicaTlsRecordReadProgress::WantRead:
            case SyncReplicaTlsRecordReadProgress::WantWrite:
                throw std::runtime_error(
                    label +
                    " reached nonblocking TLS readiness loss; this channel must be discarded");
        }
    }
}

}  // namespace anonsync
