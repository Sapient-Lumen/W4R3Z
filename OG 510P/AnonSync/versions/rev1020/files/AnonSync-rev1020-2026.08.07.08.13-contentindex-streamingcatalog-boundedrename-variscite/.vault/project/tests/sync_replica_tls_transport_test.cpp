#include "sha256_digest.hpp"
#include "sync_replica_delivery_service.hpp"
#include "sync_replica_file_tls_dispatch.hpp"
#include "sync_replica_file_tls_exchange.hpp"
#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_peer_tls_exchange.hpp"
#include "sync_replica_reconciliation_tls_exchange.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_replica_tls_transport.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner_test.hpp"
#include "sync_replica_tls_membership_sqlite_owner_test.hpp"
#include "sync_replica_tls_poll.hpp"
#include "sync_sqlite_support.hpp"

#ifdef __unix__
#include "inherited_test_process.hpp"
#endif

#include <algorithm>
#include <array>
#include <cerrno>
#include <csignal>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <fstream>
#include <future>
#include <iostream>
#include <iterator>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/ssl.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <sqlite3.h>

#ifdef __unix__
#include <fcntl.h>
#include <pthread.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#endif
#ifdef __linux__
#include <arpa/inet.h>
#include <netinet/in.h>
#endif

namespace {

static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaFileTlsServerContext>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFileTlsServerContext>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaFileTlsServerContext>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsServerContext>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaFileTlsServerContext>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaFileTlsClientContext>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFileTlsClientContext>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaFileTlsClientContext>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsClientContext>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaFileTlsClientContext>);

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_any_error(Callable&& callable, const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception&) {
        return;
    }
    fail(message + ": no error was thrown");
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

template <typename Callable>
void require_session_io_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const anonsync::SyncReplicaTlsSessionIoError& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected session error: " + error.what());
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

void test_sigpipe_ignore_policy() {
#ifdef __unix__
    struct sigaction default_action {};
    default_action.sa_handler = SIG_DFL;
    require(
        ::sigemptyset(&default_action.sa_mask) == 0,
        "SIGPIPE test could not initialize the default signal mask");
    require(
        ::sigaction(SIGPIPE, &default_action, nullptr) == 0,
        "SIGPIPE test could not restore the default disposition");

    require_error(
        [] {
            anonsync::install_sync_replica_sigpipe_ignore_policy_or_throw("");
        },
        "label must not be empty",
        "SIGPIPE policy accepted an unlabelled process-wide mutation");

    anonsync::install_sync_replica_sigpipe_ignore_policy_or_throw(
        "TLS transport test SIGPIPE policy");
    anonsync::install_sync_replica_sigpipe_ignore_policy_or_throw(
        "TLS transport test repeated SIGPIPE policy");

    struct sigaction observed_action {};
    require(
        ::sigaction(SIGPIPE, nullptr, &observed_action) == 0,
        "SIGPIPE test could not inspect the installed disposition");
    require(
        observed_action.sa_handler == SIG_IGN,
        "TLS transport policy did not leave SIGPIPE ignored");

    int descriptors[2]{-1, -1};
    require(
        ::socketpair(AF_UNIX, SOCK_STREAM, 0, descriptors) == 0,
        "SIGPIPE test could not create a connected socket pair");
    require(
        ::close(descriptors[1]) == 0,
        "SIGPIPE test could not close the peer socket");
    descriptors[1] = -1;

    errno = 0;
    const char byte = 'x';
    const ssize_t written = ::send(descriptors[0], &byte, 1U, 0);
    const int write_error = errno;
    require(
        written == -1 && write_error == EPIPE,
        "ignored SIGPIPE did not surface the closed peer as EPIPE");
    require(
        ::close(descriptors[0]) == 0,
        "SIGPIPE test could not close the local socket");
#endif
}

[[nodiscard]] std::string openssl_errors() {
    std::string output;
    for (unsigned long code = ERR_get_error(); code != 0UL;
         code = ERR_get_error()) {
        std::array<char, 256U> text{};
        ERR_error_string_n(code, text.data(), text.size());
        if (!output.empty()) output += "; ";
        output += text.data();
    }
    return output.empty() ? "no OpenSSL detail" : output;
}

[[noreturn]] void fail_openssl(const std::string& message) {
    fail(message + ": " + openssl_errors());
}

using PkeyPtr = std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)>;
using PkeyContextPtr =
    std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)>;
using CertificatePtr = std::unique_ptr<X509, decltype(&X509_free)>;
using SslContextPtr = std::unique_ptr<SSL_CTX, decltype(&SSL_CTX_free)>;
using SslPtr = std::unique_ptr<SSL, decltype(&SSL_free)>;
using BioChainPtr = std::unique_ptr<BIO, decltype(&BIO_free_all)>;
using ExtensionPtr =
    std::unique_ptr<X509_EXTENSION, decltype(&X509_EXTENSION_free)>;

long observe_bio_free(
    BIO* bio,
    int operation,
    const char* argument,
    std::size_t argument_bytes,
    int integer_argument,
    long long_argument,
    int result,
    std::size_t* processed) noexcept {
    (void)argument;
    (void)argument_bytes;
    (void)integer_argument;
    (void)long_argument;
    (void)processed;
    if (operation == BIO_CB_FREE) {
        auto* const count = reinterpret_cast<std::size_t*>(
            BIO_get_callback_arg(bio));
        if (count != nullptr) ++*count;
    }
    return result;
}

void install_counted_filter_bio_chain_or_fail(
    SSL* ssl,
    int descriptor,
    std::size_t& filter_frees,
    std::size_t& socket_frees) {
    BioChainPtr socket_bio(
        BIO_new_socket(descriptor, BIO_NOCLOSE), BIO_free_all);
    BioChainPtr filter_bio(BIO_new(BIO_f_null()), BIO_free_all);
    if (!socket_bio || !filter_bio) {
        fail_openssl("TLS transport test could not allocate a filter BIO chain");
    }
    BIO_set_callback_ex(filter_bio.get(), observe_bio_free);
    BIO_set_callback_arg(
        filter_bio.get(), reinterpret_cast<char*>(&filter_frees));
    BIO_set_callback_ex(socket_bio.get(), observe_bio_free);
    BIO_set_callback_arg(
        socket_bio.get(), reinterpret_cast<char*>(&socket_frees));
    if (BIO_push(filter_bio.get(), socket_bio.release()) != filter_bio.get()) {
        fail_openssl("TLS transport test could not compose a filter BIO chain");
    }
    SSL_set_bio(ssl, filter_bio.get(), filter_bio.get());
    (void)filter_bio.release();
}

static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaTlsAuthenticatedChannel>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaTlsAuthenticatedChannel>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaTlsAuthenticatedChannel>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaTlsAuthenticatedChannel>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaTlsAuthenticatedChannel>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaTlsRecordWriteContinuation>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaTlsRecordWriteContinuation>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaTlsRecordWriteContinuation>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaTlsRecordWriteContinuation>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaTlsRecordWriteContinuation>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaTlsRecordReadContinuation>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaTlsRecordReadContinuation>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaTlsRecordReadContinuation>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaTlsRecordReadContinuation>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaTlsRecordReadContinuation>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaFileTlsDispatchContinuation>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFileTlsDispatchContinuation>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaFileTlsDispatchContinuation>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsDispatchContinuation>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaFileTlsDispatchContinuation>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsReceiveResult>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(!std::is_copy_assignable_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(std::is_nothrow_destructible_v<
              anonsync::SyncReplicaFileTlsReceiverSession>);
static_assert(!std::is_default_constructible_v<
              anonsync::SyncReplicaFileTlsServerListener>);
static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaFileTlsServerListener>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::SyncReplicaFileTlsServerListener>);
static_assert(std::is_nothrow_move_assignable_v<
              anonsync::SyncReplicaFileTlsServerListener>);
static_assert(std::is_trivially_copyable_v<
              anonsync::SyncReplicaTlsSocketReadinessTarget>);
static_assert(anonsync::kSyncReplicaTlsRecordReadStepBytes == 64U * 1024U);
static_assert(anonsync::kSyncReplicaTlsRecordWriteStepBytes == 64U * 1024U);

[[nodiscard]] PkeyPtr make_ed25519_key() {
    PkeyContextPtr context(
        EVP_PKEY_CTX_new_id(EVP_PKEY_ED25519, nullptr),
        EVP_PKEY_CTX_free);
    if (!context || EVP_PKEY_keygen_init(context.get()) <= 0) {
        fail_openssl("TLS transport test could not initialize Ed25519 keygen");
    }
    EVP_PKEY* raw = nullptr;
    if (EVP_PKEY_keygen(context.get(), &raw) <= 0 || raw == nullptr) {
        fail_openssl("TLS transport test could not generate Ed25519 key");
    }
    return PkeyPtr(raw, EVP_PKEY_free);
}

void add_extension_or_throw(
    X509* certificate,
    X509* issuer,
    int nid,
    const char* value) {
    X509V3_CTX context{};
    X509V3_set_ctx(&context, issuer, certificate, nullptr, nullptr, 0);
    ExtensionPtr extension(
        X509V3_EXT_conf_nid(
            nullptr, &context, nid, const_cast<char*>(value)),
        X509_EXTENSION_free);
    if (!extension || X509_add_ext(certificate, extension.get(), -1) != 1) {
        fail_openssl("TLS transport test could not add X.509 extension");
    }
}

[[nodiscard]] CertificatePtr make_certificate(
    EVP_PKEY* subject_key,
    std::string_view common_name,
    long serial,
    X509* issuer_certificate,
    EVP_PKEY* issuer_key,
    bool is_ca) {
    CertificatePtr certificate(X509_new(), X509_free);
    if (!certificate ||
        X509_set_version(certificate.get(), 2L) != 1 ||
        ASN1_INTEGER_set(
            X509_get_serialNumber(certificate.get()), serial) != 1 ||
        X509_gmtime_adj(X509_getm_notBefore(certificate.get()), -60L) ==
            nullptr ||
        X509_gmtime_adj(
            X509_getm_notAfter(certificate.get()), 24L * 60L * 60L) ==
            nullptr ||
        X509_set_pubkey(certificate.get(), subject_key) != 1) {
        fail_openssl("TLS transport test could not initialize certificate");
    }

    X509_NAME* subject = X509_get_subject_name(certificate.get());
    if (subject == nullptr ||
        X509_NAME_add_entry_by_txt(
            subject, "CN", MBSTRING_ASC,
            reinterpret_cast<const unsigned char*>(common_name.data()),
            static_cast<int>(common_name.size()), -1, 0) != 1) {
        fail_openssl("TLS transport test could not set certificate subject");
    }
    X509_NAME* issuer_name = issuer_certificate == nullptr
        ? subject
        : X509_get_subject_name(issuer_certificate);
    if (issuer_name == nullptr ||
        X509_set_issuer_name(certificate.get(), issuer_name) != 1) {
        fail_openssl("TLS transport test could not set certificate issuer");
    }

    if (is_ca) {
        add_extension_or_throw(
            certificate.get(), certificate.get(), NID_basic_constraints,
            "critical,CA:TRUE");
        add_extension_or_throw(
            certificate.get(), certificate.get(), NID_key_usage,
            "critical,keyCertSign,cRLSign");
    } else {
        add_extension_or_throw(
            certificate.get(), issuer_certificate, NID_basic_constraints,
            "critical,CA:FALSE");
        add_extension_or_throw(
            certificate.get(), issuer_certificate, NID_key_usage,
            "critical,digitalSignature");
        add_extension_or_throw(
            certificate.get(), issuer_certificate, NID_ext_key_usage,
            "serverAuth,clientAuth");
    }

    EVP_PKEY* signer = issuer_key == nullptr ? subject_key : issuer_key;
    if (X509_sign(certificate.get(), signer, nullptr) <= 0) {
        fail_openssl("TLS transport test could not sign certificate");
    }
    return certificate;
}

[[nodiscard]] std::string certificate_spki_sha256(X509* certificate) {
    X509_PUBKEY* public_key = X509_get_X509_PUBKEY(certificate);
    if (public_key == nullptr) {
        fail("TLS transport test certificate has no SubjectPublicKeyInfo");
    }
    const int bytes = i2d_X509_PUBKEY(public_key, nullptr);
    if (bytes <= 0) {
        fail_openssl("TLS transport test could not size SubjectPublicKeyInfo");
    }
    std::string encoded(static_cast<std::size_t>(bytes), '\0');
    unsigned char* output = reinterpret_cast<unsigned char*>(encoded.data());
    if (i2d_X509_PUBKEY(public_key, &output) != bytes) {
        fail_openssl("TLS transport test could not encode SubjectPublicKeyInfo");
    }
    return anonsync::sha256_hex(encoded);
}

[[nodiscard]] SslContextPtr make_tls_context(
    X509* certificate,
    EVP_PKEY* private_key,
    X509* trust_anchor,
    bool server,
    bool configure_alpn = true) {
    SslContextPtr context(SSL_CTX_new(TLS_method()), SSL_CTX_free);
    if (!context ||
        SSL_CTX_use_certificate(context.get(), certificate) != 1 ||
        SSL_CTX_use_PrivateKey(context.get(), private_key) != 1 ||
        SSL_CTX_check_private_key(context.get()) != 1) {
        fail_openssl("TLS transport test could not configure TLS identity");
    }
    if (configure_alpn) {
        if (server) {
            anonsync::configure_sync_replica_tls13_server_context_or_throw(
                context.get(), "TLS transport test server profile");
        } else {
            anonsync::configure_sync_replica_tls13_client_context_or_throw(
                context.get(), "TLS transport test client profile");
        }
    } else {
        if (SSL_CTX_set_min_proto_version(
                context.get(), TLS1_3_VERSION) != 1 ||
            SSL_CTX_set_max_proto_version(
                context.get(), TLS1_3_VERSION) != 1 ||
            SSL_CTX_set_max_early_data(context.get(), 0U) != 1) {
            fail_openssl(
                "TLS transport test could not configure no-ALPN TLS profile");
        }
        SSL_CTX_set_verify(
            context.get(),
            SSL_VERIFY_PEER |
                (server ? SSL_VERIFY_FAIL_IF_NO_PEER_CERT : 0),
            nullptr);
    }
    if (X509_STORE_add_cert(
            SSL_CTX_get_cert_store(context.get()), trust_anchor) != 1) {
        fail_openssl("TLS transport test could not install trust anchor");
    }
    SSL_CTX_set_verify_depth(context.get(), 2);
    if (!configure_alpn && server &&
        SSL_CTX_set_num_tickets(context.get(), 0U) != 1) {
        fail_openssl("TLS transport test could not disable session tickets");
    }
    return context;
}

#ifdef __unix__
volatile std::sig_atomic_t tls_poll_signal_count = 0;

extern "C" void tls_poll_signal_handler(int) noexcept {
    tls_poll_signal_count = 1;
}

class FileDescriptor final {
public:
    FileDescriptor() = default;
    explicit FileDescriptor(int value) : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) (void)::close(value_);
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (value_ >= 0) (void)::close(value_);
            value_ = std::exchange(other.value_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return value_; }

private:
    int value_ = -1;
};

#ifdef __linux__
struct LoopbackListener final {
    FileDescriptor descriptor;
    std::uint16_t port = 0U;
};

[[nodiscard]] LoopbackListener make_loopback_listener_fixture() {
    const int raw = ::socket(
        AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (raw < 0) {
        fail("TLS server test could not create loopback listener");
    }
    LoopbackListener listener{FileDescriptor(raw), 0U};
    int one = 1;
    if (::setsockopt(
            listener.descriptor.get(), SOL_SOCKET, SO_REUSEADDR,
            &one, sizeof(one)) != 0) {
        fail("TLS server test could not set SO_REUSEADDR");
    }
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(0U);
    if (::bind(
            listener.descriptor.get(),
            reinterpret_cast<sockaddr*>(&address), sizeof(address)) != 0 ||
        ::listen(listener.descriptor.get(), 8) != 0) {
        fail("TLS server test could not bind/listen on loopback");
    }
    socklen_t address_bytes = sizeof(address);
    if (::getsockname(
            listener.descriptor.get(),
            reinterpret_cast<sockaddr*>(&address), &address_bytes) != 0 ||
        address_bytes != sizeof(address)) {
        fail("TLS server test could not observe loopback port");
    }
    listener.port = ntohs(address.sin_port);
    if (listener.port == 0U) {
        fail("TLS server test observed an invalid loopback port");
    }
    return listener;
}

void set_descriptor_close_on_exec(int descriptor, bool enabled) {
    const int flags = ::fcntl(descriptor, F_GETFD, 0);
    if (flags < 0 ||
        ::fcntl(
            descriptor, F_SETFD,
            enabled ? flags | FD_CLOEXEC : flags & ~FD_CLOEXEC) != 0) {
        fail("TLS server test could not change FD_CLOEXEC");
    }
}

[[nodiscard]] FileDescriptor connect_loopback_client_fixture(
    std::uint16_t port) {
    const int raw = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (raw < 0) fail("TLS server test could not create client socket");
    FileDescriptor client(raw);
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(port);
    if (::connect(
            client.get(), reinterpret_cast<sockaddr*>(&address),
            sizeof(address)) != 0) {
        fail("TLS server test could not connect loopback client");
    }
    return client;
}

[[nodiscard]] SslPtr connect_tls_client_fixture(
    SSL_CTX* context,
    int descriptor,
    const std::string& label) {
    SslPtr ssl(SSL_new(context), SSL_free);
    if (!ssl) fail_openssl(label + " could not allocate client SSL");
    if (SSL_set_fd(ssl.get(), descriptor) != 1) {
        fail_openssl(label + " could not bind client SSL");
    }
    SSL_set_connect_state(ssl.get());
    ERR_clear_error();
    const int handshake = SSL_connect(ssl.get());
    if (handshake != 1) {
        const int ssl_error = SSL_get_error(ssl.get(), handshake);
        fail_openssl(
            label + " client handshake failed with SSL error " +
            std::to_string(ssl_error));
    }
    return ssl;
}
#endif

void configure_socket_timeout(int descriptor) {
    const timeval timeout{5, 0};
    if (::setsockopt(
            descriptor, SOL_SOCKET, SO_RCVTIMEO,
            &timeout, sizeof(timeout)) != 0 ||
        ::setsockopt(
            descriptor, SOL_SOCKET, SO_SNDTIMEO,
            &timeout, sizeof(timeout)) != 0) {
        fail("TLS transport test could not configure socket timeout");
    }
}

struct TlsConnectionPair final {
    FileDescriptor client_fd;
    FileDescriptor server_fd;
    SslPtr client{nullptr, SSL_free};
    SslPtr server{nullptr, SSL_free};
};

void complete_tls_handshake(TlsConnectionPair& pair) {
    std::exception_ptr server_failure;
    std::thread server_handshake([&] {
        try {
            ERR_clear_error();
            const int result = SSL_accept(pair.server.get());
            if (result != 1) {
                fail_openssl(
                    "TLS transport test server handshake failed with SSL error " +
                    std::to_string(SSL_get_error(pair.server.get(), result)));
            }
        } catch (...) {
            server_failure = std::current_exception();
        }
    });
    std::exception_ptr client_failure;
    try {
        ERR_clear_error();
        const int result = SSL_connect(pair.client.get());
        if (result != 1) {
            fail_openssl(
                "TLS transport test client handshake failed with SSL error " +
                std::to_string(SSL_get_error(pair.client.get(), result)));
        }
    } catch (...) {
        client_failure = std::current_exception();
    }
    server_handshake.join();
    if (client_failure) std::rethrow_exception(client_failure);
    if (server_failure) std::rethrow_exception(server_failure);
}

[[nodiscard]] TlsConnectionPair make_tls_connection_pair(
    SSL_CTX* client_context,
    SSL_CTX* server_context) {
    std::array<int, 2U> descriptors{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0,
            descriptors.data()) != 0) {
        fail("TLS transport test could not create socketpair");
    }
    TlsConnectionPair pair{
        FileDescriptor(descriptors[0]), FileDescriptor(descriptors[1]),
        SslPtr(SSL_new(client_context), SSL_free),
        SslPtr(SSL_new(server_context), SSL_free)};
    if (!pair.client || !pair.server) {
        fail_openssl("TLS transport test could not allocate SSL objects");
    }
    configure_socket_timeout(pair.client_fd.get());
    configure_socket_timeout(pair.server_fd.get());
    if (SSL_set_fd(pair.client.get(), pair.client_fd.get()) != 1 ||
        SSL_set_fd(pair.server.get(), pair.server_fd.get()) != 1) {
        fail_openssl("TLS transport test could not bind SSL objects to sockets");
    }
    SSL_set_connect_state(pair.client.get());
    SSL_set_accept_state(pair.server.get());
    complete_tls_handshake(pair);
    return pair;
}

struct AuthenticatedTlsPair final {
    TlsConnectionPair connection;
    anonsync::SyncReplicaTlsAuthenticatedChannel sender_channel;
    anonsync::SyncReplicaTlsAuthenticatedChannel receiver_channel;
};

[[nodiscard]] AuthenticatedTlsPair make_authenticated_tls_pair(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin,
    const std::string& label) {
    TlsConnectionPair connection =
        make_tls_connection_pair(client_context, server_context);
    auto sender_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.client.get(), {receiver_actor, receiver_pin},
            label + " sender");
    auto receiver_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.server.get(), {sender_actor, sender_pin},
            label + " receiver");
    return {
        std::move(connection), std::move(sender_channel),
        std::move(receiver_channel)};
}

void require_socket_has_no_pending_bytes(
    int descriptor, const std::string& message) {
    unsigned char byte = 0U;
    errno = 0;
    const ssize_t result = ::recv(
        descriptor, &byte, 1U, MSG_PEEK | MSG_DONTWAIT);
    require(
        result == -1 && (errno == EAGAIN || errno == EWOULDBLOCK),
        message + " (recv result=" + std::to_string(result) +
            ", errno=" + std::to_string(errno) + ")");
}

[[nodiscard]] int pending_socket_bytes_or_fail(
    int descriptor, const std::string& label) {
    int pending = -1;
    if (::ioctl(descriptor, FIONREAD, &pending) != 0 || pending < 0) {
        fail(label + " could not observe pending socket bytes");
    }
    return pending;
}

void make_socket_nonblocking(int descriptor) {
    const int flags = ::fcntl(descriptor, F_GETFL, 0);
    if (flags < 0 || ::fcntl(descriptor, F_SETFL, flags | O_NONBLOCK) != 0) {
        fail("TLS transport test could not make socket nonblocking");
    }
}

void make_socket_blocking(int descriptor) {
    const int flags = ::fcntl(descriptor, F_GETFL, 0);
    if (flags < 0 ||
        ::fcntl(descriptor, F_SETFL, flags & ~O_NONBLOCK) != 0) {
        fail("TLS transport test could not make socket blocking");
    }
}

void make_socket_nonblocking_with_small_send_buffer(int descriptor) {
    make_socket_nonblocking(descriptor);
    const int bytes = 1024;
    if (::setsockopt(
            descriptor, SOL_SOCKET, SO_SNDBUF, &bytes, sizeof(bytes)) != 0) {
        fail("TLS transport test could not constrain socket send buffer");
    }
}

[[nodiscard]] std::size_t saturate_raw_socket_send_path_or_fail(
    int descriptor,
    const std::string& label) {
    std::array<unsigned char, 16U * 1024U> bytes{};
    bytes.fill(0xa5U);
    std::size_t total = 0U;
    std::size_t consecutive_eagain = 0U;
    constexpr std::size_t kRequiredStableEagain = 16U;
    for (std::size_t attempt = 0U; attempt < 131072U; ++attempt) {
        errno = 0;
        const ssize_t written = ::send(
            descriptor, bytes.data(), bytes.size(),
            MSG_DONTWAIT | MSG_NOSIGNAL);
        if (written > 0) {
            total += static_cast<std::size_t>(written);
            consecutive_eagain = 0U;
            continue;
        }
        if (written < 0 &&
            (errno == EAGAIN || errno == EWOULDBLOCK)) {
            if (total == 0U) {
                fail(label + " reached EAGAIN before filling any bytes");
            }
            ++consecutive_eagain;
            if (consecutive_eagain == kRequiredStableEagain) return total;
            // A single EAGAIN can mean only that the local queue filled before
            // queued bytes reached the peer. Give the kernel a scheduling
            // opportunity, refill any reopened capacity, and require a stable
            // zero-capacity frontier before relying on first-prefix WANT.
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            continue;
        }
        fail(label + " could not saturate the raw socket send path");
    }
    fail(label + " did not reach a bounded stable-EAGAIN frontier");
}

struct NonblockingSocketPair final {
    FileDescriptor left;
    FileDescriptor right;
};

[[nodiscard]] NonblockingSocketPair make_nonblocking_socket_pair_fixture() {
    std::array<int, 2U> descriptors{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0,
            descriptors.data()) != 0) {
        fail("TLS transport test could not create replacement socketpair");
    }
    return {
        FileDescriptor(descriptors[0]),
        FileDescriptor(descriptors[1]),
    };
}

void replace_descriptor_lifetime_or_fail(
    int descriptor,
    const NonblockingSocketPair& replacement,
    const std::string& label) {
    if (::dup2(replacement.left.get(), descriptor) != descriptor) {
        fail(label + " could not replace the descriptor lifetime");
    }
}

[[nodiscard]] std::array<unsigned char, 8U> encode_u64_be_fixture(
    std::uint64_t value) noexcept {
    std::array<unsigned char, 8U> output{};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        const std::size_t shift = (output.size() - 1U - index) * 8U;
        output[index] = static_cast<unsigned char>(value >> shift);
    }
    return output;
}

void write_tls_fixture_bytes(
    SSL* ssl,
    const unsigned char* data,
    std::size_t bytes,
    const std::string& label) {
    std::size_t offset = 0U;
    while (offset < bytes) {
        std::size_t written = 0U;
        ERR_clear_error();
        const int result = SSL_write_ex(
            ssl, data + offset, bytes - offset, &written);
        const int ssl_error =
            result == 1 ? SSL_ERROR_NONE : SSL_get_error(ssl, result);
        if (result != 1) {
            fail_openssl(
                label + " SSL_write_ex failed with SSL error " +
                std::to_string(ssl_error));
        }
        if (written == 0U || written > bytes - offset) {
            fail(label + " SSL_write_ex made invalid progress");
        }
        offset += written;
    }
}

void write_tls_fixture_bytes(
    SSL* ssl,
    std::string_view bytes,
    const std::string& label) {
    write_tls_fixture_bytes(
        ssl,
        reinterpret_cast<const unsigned char*>(bytes.data()),
        bytes.size(), label);
}

void send_tls_close_notify(SSL* ssl, const std::string& label) {
    ERR_clear_error();
    const int result = SSL_shutdown(ssl);
    const int ssl_error =
        result >= 0 ? SSL_ERROR_NONE : SSL_get_error(ssl, result);
    if (result < 0) {
        fail_openssl(
            label + " SSL_shutdown failed with SSL error " +
            std::to_string(ssl_error));
    }
}

[[nodiscard]] bool is_tls_read_want(
    anonsync::SyncReplicaTlsRecordReadProgress progress) noexcept {
    return progress == anonsync::SyncReplicaTlsRecordReadProgress::WantRead ||
           progress == anonsync::SyncReplicaTlsRecordReadProgress::WantWrite;
}

[[nodiscard]] bool is_tls_write_want(
    anonsync::SyncReplicaTlsRecordWriteProgress progress) noexcept {
    return progress == anonsync::SyncReplicaTlsRecordWriteProgress::WantRead ||
           progress == anonsync::SyncReplicaTlsRecordWriteProgress::WantWrite;
}

template <typename WriteContinuation>
[[nodiscard]] anonsync::SyncReplicaTlsRecordWriteProgress
advance_tls_write_until_want(
    WriteContinuation& continuation,
    const std::string& label) {
    for (std::size_t iteration = 0U; iteration < 4096U; ++iteration) {
        const auto progress = continuation.advance_or_throw();
        if (is_tls_write_want(progress)) return progress;
        if (progress ==
            anonsync::SyncReplicaTlsRecordWriteProgress::Complete) {
            fail(label + " completed before reaching transport backpressure");
        }
        if (progress !=
            anonsync::SyncReplicaTlsRecordWriteProgress::Progress) {
            fail(label + " reached an unknown write progress state");
        }
    }
    fail(label + " did not reach transport backpressure");
}

[[nodiscard]] std::string finish_tls_record_read(
    anonsync::SyncReplicaTlsRecordReadContinuation& continuation,
    const std::string& label) {
    for (std::size_t iteration = 0U; iteration < 4096U; ++iteration) {
        const auto progress = continuation.advance_or_throw();
        if (progress ==
            anonsync::SyncReplicaTlsRecordReadProgress::Complete) {
            return continuation.take_frame_or_throw();
        }
        if (progress ==
            anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed) {
            fail(label + " observed peer close instead of a complete frame");
        }
        if (is_tls_read_want(progress)) std::this_thread::yield();
    }
    fail(label + " did not reach a terminal frame state");
}

struct TlsWriteTransferResult final {
    std::string frame;
    std::size_t write_poll_operations = 0U;
    std::size_t max_write_step = 0U;
};

[[nodiscard]] anonsync::SyncReplicaTlsRecordWritePollProgress
poll_tls_writer_or_throw(
    anonsync::SyncReplicaTlsRecordWriteContinuation& writer,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    return anonsync::poll_and_advance_sync_replica_tls_record_write_or_throw(
        writer, deadline, label);
}

[[nodiscard]] anonsync::SyncReplicaTlsRecordWritePollProgress
poll_tls_writer_or_throw(
    anonsync::SyncReplicaFileTlsDispatchContinuation& writer,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    return writer.poll_and_advance_or_throw(deadline, label);
}

template <typename Writer>
[[nodiscard]] TlsWriteTransferResult
finish_tls_write_with_nonblocking_reader(
    Writer& writer,
    const anonsync::SyncReplicaTlsAuthenticatedChannel& receiver_channel,
    std::uint64_t max_frame_bytes,
    bool writer_waiting,
    const std::string& label) {
    auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
        receiver_channel, max_frame_bytes,
        anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
            RequireNonblockingSocket,
        label + " reader");
    const std::size_t total_frame_bytes =
        static_cast<std::size_t>(writer.frame_bytes());
    if (total_frame_bytes == 0U) {
        fail(label + " started with an empty TLS writer");
    }
    bool reader_waiting = false;
    bool writer_complete = false;
    std::optional<std::string> received;
    TlsWriteTransferResult result;

    for (std::size_t iteration = 0U;
         iteration < 65536U &&
         (!writer_complete || !received.has_value());
         ++iteration) {
        if (!received.has_value()) {
            anonsync::SyncReplicaTlsRecordReadProgress progress{};
            bool have_progress = false;
            if (reader_waiting) {
                const auto polled = anonsync::
                    poll_and_advance_sync_replica_tls_record_read_or_throw(
                        reader,
                        std::chrono::steady_clock::now() +
                            std::chrono::milliseconds(2),
                        label + " read poll");
                switch (polled) {
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        DeadlineExpired:
                        break;
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        Progress:
                        progress = anonsync::
                            SyncReplicaTlsRecordReadProgress::Progress;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        WantRead:
                        progress = anonsync::
                            SyncReplicaTlsRecordReadProgress::WantRead;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        WantWrite:
                        progress = anonsync::
                            SyncReplicaTlsRecordReadProgress::WantWrite;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        Complete:
                        progress = anonsync::
                            SyncReplicaTlsRecordReadProgress::Complete;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordReadPollProgress::
                        PeerClosed:
                        progress = anonsync::
                            SyncReplicaTlsRecordReadProgress::PeerClosed;
                        have_progress = true;
                        break;
                }
            } else {
                progress = reader.advance_or_throw();
                have_progress = true;
            }
            if (have_progress) {
                reader_waiting = is_tls_read_want(progress);
                if (progress ==
                    anonsync::SyncReplicaTlsRecordReadProgress::Complete) {
                    received.emplace(reader.take_frame_or_throw());
                } else if (
                    progress ==
                    anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed) {
                    fail(label + " observed peer close before frame receipt");
                }
            }
        }

        if (!writer_complete) {
            const std::size_t before = static_cast<std::size_t>(
                writer.body_bytes_written());
            anonsync::SyncReplicaTlsRecordWriteProgress progress{};
            bool have_progress = false;
            bool used_poll = false;
            if (writer_waiting) {
                used_poll = true;
                const auto polled = poll_tls_writer_or_throw(
                    writer,
                    std::chrono::steady_clock::now() +
                        std::chrono::milliseconds(2),
                    label + " write poll");
                switch (polled) {
                    case anonsync::SyncReplicaTlsRecordWritePollProgress::
                        DeadlineExpired:
                        break;
                    case anonsync::SyncReplicaTlsRecordWritePollProgress::
                        Progress:
                        progress = anonsync::
                            SyncReplicaTlsRecordWriteProgress::Progress;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordWritePollProgress::
                        WantRead:
                        progress = anonsync::
                            SyncReplicaTlsRecordWriteProgress::WantRead;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordWritePollProgress::
                        WantWrite:
                        progress = anonsync::
                            SyncReplicaTlsRecordWriteProgress::WantWrite;
                        have_progress = true;
                        break;
                    case anonsync::SyncReplicaTlsRecordWritePollProgress::
                        Complete:
                        progress = anonsync::
                            SyncReplicaTlsRecordWriteProgress::Complete;
                        have_progress = true;
                        break;
                }
            } else {
                progress = writer.advance_or_throw();
                have_progress = true;
            }
            if (have_progress) {
                const std::size_t after =
                    progress ==
                            anonsync::SyncReplicaTlsRecordWriteProgress::Complete
                        ? total_frame_bytes
                        : static_cast<std::size_t>(
                              writer.body_bytes_written());
                require(after >= before,
                        label + " moved the TLS write cutpoint backward");
                if (used_poll) {
                    ++result.write_poll_operations;
                    result.max_write_step = std::max(
                        result.max_write_step, after - before);
                }
                writer_waiting = is_tls_write_want(progress);
                writer_complete =
                    progress ==
                    anonsync::SyncReplicaTlsRecordWriteProgress::Complete;
            }
        }
        std::this_thread::yield();
    }

    if (!writer_complete || !received.has_value()) {
        fail(label + " did not complete its cooperative TLS transfer");
    }
    result.frame = std::move(*received);
    return result;
}

[[nodiscard]] TlsWriteTransferResult
complete_pending_tls_write_with_reader(
    anonsync::SyncReplicaTlsRecordWriteContinuation& writer,
    const anonsync::SyncReplicaTlsAuthenticatedChannel& receiver_channel,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    return finish_tls_write_with_nonblocking_reader(
        writer, receiver_channel, max_frame_bytes, true, label);
}

using FileTlsDispatchTransferResult = TlsWriteTransferResult;

[[nodiscard]] FileTlsDispatchTransferResult
finish_file_tls_dispatch_with_nonblocking_reader(
    anonsync::SyncReplicaFileTlsDispatchContinuation& writer,
    const anonsync::SyncReplicaTlsAuthenticatedChannel& receiver_channel,
    std::uint64_t max_frame_bytes,
    bool writer_waiting,
    const std::string& label) {
    return finish_tls_write_with_nonblocking_reader(
        writer, receiver_channel, max_frame_bytes, writer_waiting, label);
}

void replace_tls_stream_and_rehandshake(TlsConnectionPair& pair) {
    if (SSL_clear(pair.client.get()) != 1 ||
        SSL_clear(pair.server.get()) != 1 ||
        SSL_set_session(pair.client.get(), nullptr) != 1) {
        fail_openssl(
            "TLS transport test could not reset SSL objects for a fresh session");
    }

    std::array<int, 2U> descriptors{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0,
            descriptors.data()) != 0) {
        fail("TLS transport test could not replace socketpair");
    }
    pair.client_fd = FileDescriptor(descriptors[0]);
    pair.server_fd = FileDescriptor(descriptors[1]);
    configure_socket_timeout(pair.client_fd.get());
    configure_socket_timeout(pair.server_fd.get());
    if (SSL_set_fd(pair.client.get(), pair.client_fd.get()) != 1 ||
        SSL_set_fd(pair.server.get(), pair.server_fd.get()) != 1) {
        fail_openssl(
            "TLS transport test could not bind reset SSL objects to sockets");
    }
    SSL_set_connect_state(pair.client.get());
    SSL_set_accept_state(pair.server.get());
    complete_tls_handshake(pair);
}
#endif

struct TempDatabasePath final {
    std::filesystem::path path;

    explicit TempDatabasePath(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __unix__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        path = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick) + ".sqlite3");
    }

    ~TempDatabasePath() {
        std::error_code ignored;
        std::filesystem::remove(path, ignored);
        std::filesystem::remove(path.string() + "-wal", ignored);
        std::filesystem::remove(path.string() + "-shm", ignored);
        std::filesystem::remove(path.string() + "-journal", ignored);
    }
};

struct TempFileDeliveryWorkspace final {
    std::filesystem::path root;
    std::filesystem::path sender_db;
    std::filesystem::path receiver_db;
    std::filesystem::path effect_db;
    std::filesystem::path files;

    explicit TempFileDeliveryWorkspace(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __unix__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        root = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick));
        files = root / "files";
        std::filesystem::create_directories(files);
        sender_db = root / "sender.sqlite3";
        receiver_db = root / "receiver.sqlite3";
        effect_db = root / "effects.sqlite3";
    }

    ~TempFileDeliveryWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
    }
};

struct TempReconciliationWorkspace final {
    std::filesystem::path root;
    std::filesystem::path source_db;
    std::filesystem::path requester_db;
    std::filesystem::path source_payloads;
    std::filesystem::path requester_payloads;

    explicit TempReconciliationWorkspace(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __unix__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        root = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick));
        source_payloads = root / "source-payloads";
        requester_payloads = root / "requester-payloads";
        std::filesystem::create_directories(source_payloads);
        std::filesystem::create_directory(requester_payloads);
        std::error_code permission_error;
        std::filesystem::permissions(
            root, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace, permission_error);
        if (permission_error) {
            fail("TLS reconciliation test could not make its root private");
        }
        std::filesystem::permissions(
            source_payloads, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace, permission_error);
        if (permission_error) {
            fail("TLS reconciliation test could not make source payloads private");
        }
        std::filesystem::permissions(
            requester_payloads, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace, permission_error);
        if (permission_error) {
            fail("TLS reconciliation test could not make requester payloads private");
        }
        source_db = root / "source.sqlite3";
        requester_db = root / "requester.sqlite3";
    }

    ~TempReconciliationWorkspace() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
    }
};

anonsync::SyncSqliteDb open_database(const std::filesystem::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "replica TLS transport test open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "replica TLS transport test busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "replica TLS transport test durability profile");
    return owner;
}

struct MutableClockState final {
    std::uint64_t epoch = 100U;
};

class MutableClockSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    explicit MutableClockSource(std::shared_ptr<MutableClockState> state)
        : state_(std::move(state)) {}

    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string&) override {
        if (state_->epoch == 0U ||
            state_->epoch > std::numeric_limits<std::uint64_t>::max() /
                                anonsync::kSyncReplicaNanosecondsPerSecond) {
            fail("replica TLS transport test clock epoch is invalid");
        }
        const std::uint64_t nanoseconds =
            state_->epoch * anonsync::kSyncReplicaNanosecondsPerSecond;
        return {
            "test-tls-delivery-clock-v1",
            "01234567-89ab-cdef-0123-456789abcdef",
            std::string(64U, 'd'),
            nanoseconds,
            nanoseconds,
            1U,
            anonsync::SyncReplicaOutboxClockSynchronization::Synchronized,
        };
    }

private:
    std::shared_ptr<MutableClockState> state_;
};

std::unique_ptr<anonsync::SyncReplicaOutboxClockSource> make_clock(
    const std::shared_ptr<MutableClockState>& state) {
    return std::make_unique<MutableClockSource>(state);
}

anonsync::SyncReplicaSqliteOwnerLimits owner_limits() {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = 64U;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_outbox_intents = 64U;
    value.max_outbox_destination_bytes = 4096U;
    return value;
}

anonsync::SyncReplicaDeliveryServiceLimits service_limits() {
    anonsync::SyncReplicaDeliveryServiceLimits value;
    value.wire_operation_limits = owner_limits().model;
    value.max_request_frame_bytes = 512U * 1024U;
    value.max_receipt_frame_bytes = 16U * 1024U;
    return value;
}

anonsync::SyncReplicaFileDeliveryServiceLimits file_service_limits() {
    anonsync::SyncReplicaFileDeliveryServiceLimits value;
    value.evidence = service_limits();
    value.retry.pre_dispatch_failure_delay_seconds = 3U;
    value.max_payload_bytes = 2U * 1024U * 1024U;
    value.max_request_frame_bytes = 3U * 1024U * 1024U;
    value.max_receipt_frame_bytes = 64U * 1024U;
    return value;
}

anonsync::SyncReplicaFilePayloadStoreLimits reconciliation_payload_limits() {
    anonsync::SyncReplicaFilePayloadStoreLimits value;
    value.max_entries = 64U;
    value.max_payload_bytes = 2U * 1024U * 1024U;
    value.max_indexed_bytes = 32U * 1024U * 1024U;
    value.max_transient_entries = 64U;
    value.max_transient_bytes = 8U * 1024U * 1024U;
    return value;
}

anonsync::SyncReplicaReconciliationProtocolLimits
reconciliation_protocol_limits(
    std::uint64_t operations_per_page = 1U) {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model = owner_limits().model;
    value.max_operations_per_page = operations_per_page;
    value.max_canonical_operation_bytes_per_page = 2U * 1024U * 1024U;
    value.max_payloads_per_page = 8U;
    value.max_single_payload_bytes = 2U * 1024U * 1024U;
    value.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 8U * 1024U * 1024U;
    return value;
}

anonsync::SyncReplicaFilePayloadSnapshot payload_snapshot(
    const std::string& folder,
    std::vector<std::string> payloads) {
    return anonsync::SyncReplicaFilePayloadSnapshot(
        folder, std::move(payloads), {}, "TLS transport test payload snapshot");
}

anonsync::SyncReplicaFilePayloadSnapshot payload_snapshot(
    const std::string& folder,
    const std::string& payload) {
    return payload_snapshot(folder, std::vector<std::string>{payload});
}

anonsync::SyncReplicaFileEffectSqliteOwnerLimits file_effect_limits() {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits value;
    value.model = owner_limits().model;
    value.max_effects = 64U;
    value.max_payload_bytes = 2U * 1024U * 1024U;
    value.max_retained_payload_bytes = 16U * 1024U * 1024U;
    return value;
}

std::string read_binary_file(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) fail("TLS file dispatch test could not read visible file");
    return {std::istreambuf_iterator<char>(input),
            std::istreambuf_iterator<char>()};
}

void test_tls_record_write_continuation(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS continuation success");
        const std::string frame = "prefix-continuation-frame";
        auto continuation =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, 1024U,
                "TLS continuation success");
        require(continuation.active() &&
                    continuation.frame_bytes() == frame.size(),
                "TLS prefix did not return one exact active continuation");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, "lock", 1024U,
                    "TLS overlapping continuation");
            },
            "unfinished record write",
            "TLS stream admitted two overlapping record prefixes");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "race", 1024U,
                    "TLS generic write during continuation");
            },
            "unfinished record write",
            "generic TLS writer bypassed continuation exclusivity");
        require_error(
            [&] {
                (void)anonsync::read_sync_replica_tls_record_or_throw(
                    pair.sender_channel, 1024U,
                    "TLS read during continuation");
            },
            "unfinished record write",
            "TLS reader entered OpenSSL during an unfinished record write");
        require(continuation.active(),
                "rejected overlapping I/O poisoned the original continuation");
        continuation.finish_or_throw();
        require(!continuation.active() && continuation.frame_bytes() == 0U,
                "successful TLS continuation retained stream authority");
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, 1024U,
                "TLS continuation success read") == frame,
            "TLS continuation changed the framed application bytes");
        require_error(
            [&] { continuation.finish_or_throw(); },
            "empty or already finished",
            "finished TLS continuation remained reusable");
    }

    // A prepared record write reserves exact stream ownership before the first
    // prefix operation. Untouched destruction releases that idle reservation
    // without emitting ciphertext or poisoning the authenticated channel. Once
    // advanced, the stable prefix and body bytes remain privately owned.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS prepared prefix ownership");
        {
            auto untouched =
                anonsync::prepare_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, "untouched", 1024U,
                    anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                        CallerManaged,
                    "TLS untouched prepared prefix");
            require(
                untouched.active() && !untouched.io_started() &&
                    untouched.prefix_bytes_written() == 0U &&
                    !untouched.prefix_complete() &&
                    untouched.body_bytes_written() == 0U,
                "untouched TLS preparation invented prefix progress");
        }
        require_socket_has_no_pending_bytes(
            pair.connection.server_fd.get(),
            "untouched TLS preparation emitted ciphertext");

        std::string frame = "prepared-prefix-owned-frame";
        const std::string expected = frame;
        auto prepared =
            anonsync::prepare_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, 1024U,
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    CallerManaged,
                "TLS prepared prefix ownership");
        frame.assign(frame.size(), 'x');
        require(
            prepared.advance_or_throw() ==
                    anonsync::SyncReplicaTlsRecordWriteProgress::Progress &&
                prepared.io_started() && prepared.prefix_complete() &&
                prepared.prefix_bytes_written() ==
                    anonsync::kSyncReplicaTlsRecordPrefixBytes &&
                prepared.body_bytes_written() == 0U,
            "one prepared TLS step did not expose the exact prefix cutpoint");
        prepared.finish_or_throw();
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, 1024U,
                "TLS prepared prefix ownership read") == expected,
            "prepared TLS write borrowed mutated caller bytes");
    }

    // A genuine first-prefix WANT retains the exact stable prefix arguments and
    // advisory readiness target. Abandonment after that zero-byte OpenSSL
    // attempt poisons the stream because the pending operation cannot be
    // replaced by a new record, even though no prefix byte was accepted.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS first-prefix WANT");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        const int receive_bytes = 1024;
        if (::setsockopt(
                pair.connection.server_fd.get(), SOL_SOCKET, SO_RCVBUF,
                &receive_bytes, sizeof(receive_bytes)) != 0) {
            fail("TLS first-prefix WANT could not constrain peer receive buffer");
        }
        const std::size_t saturated = saturate_raw_socket_send_path_or_fail(
            pair.connection.client_fd.get(), "TLS first-prefix WANT");
        require(saturated > 0U,
                "TLS first-prefix WANT did not fill the socket path");
        {
            auto prepared =
                anonsync::prepare_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, "prefix-want-frame", 1024U,
                    anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                        RequireNonblockingSocket,
                    "TLS first-prefix WANT");
            const auto progress = prepared.advance_or_throw();
            require(
                progress ==
                        anonsync::SyncReplicaTlsRecordWriteProgress::WantWrite &&
                    prepared.active() && prepared.io_started() &&
                    prepared.prefix_bytes_written() == 0U &&
                    !prepared.prefix_complete() &&
                    prepared.body_bytes_written() == 0U,
                "first-prefix backpressure was not retained as an exact WANT_WRITE");
            const auto target = prepared.pending_readiness_or_throw();
            require(
                target.descriptor == pair.connection.client_fd.get() &&
                    target.readiness ==
                        anonsync::SyncReplicaTlsSocketReadiness::Writable,
                "first-prefix WANT exposed the wrong socket lifetime or event");
            auto moved = std::move(prepared);
            require(
                !prepared.active() && moved.active() &&
                    moved.pending_readiness_or_throw() == target &&
                    moved.prefix_bytes_written() == 0U,
                "moving a first-prefix WANT changed its retry frontier");
        }
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS first-prefix WANT reuse");
            },
            "poisoned",
            "abandoned first-prefix WANT left the TLS stream reusable");
    }

    // Authentication retains the exact read/write BIO objects. Replacing them
    // after the handshake but before the first application record cannot borrow
    // the old peer/exporter authority merely because the SSL session survives.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS post-auth BIO replacement");
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        if (SSL_set_fd(
                pair.connection.client.get(), replacement.left.get()) != 1) {
            fail_openssl(
                "TLS post-auth BIO replacement could not install replacement BIO");
        }
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "bio-replacement", 1024U,
                    "TLS post-auth BIO replacement");
            },
            "BIO changed after authentication",
            "post-auth SSL_set_fd inherited authenticated channel authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS post-auth BIO replacement poisoned reuse");
            },
            "poisoned",
            "post-auth BIO replacement left the old capability reusable");
    }

    // A caller-managed top-level BIO can own a complete filter chain. The
    // authenticated anchor retains the exact top BIO across replacement, and
    // its final release must traverse the whole old chain rather than freeing
    // only the head and leaking the downstream socket BIO.
    {
        TlsConnectionPair connection =
            make_tls_connection_pair(client_context, server_context);
        std::size_t filter_frees = 0U;
        std::size_t socket_frees = 0U;
        install_counted_filter_bio_chain_or_fail(
            connection.client.get(), connection.client_fd.get(),
            filter_frees, socket_frees);
        require(
            BIO_method_type(SSL_get_rbio(connection.client.get())) !=
                BIO_TYPE_SOCKET &&
                SSL_get_rbio(connection.client.get()) ==
                    SSL_get_wbio(connection.client.get()),
            "filter-chain fixture did not expose one caller-managed top BIO");
        {
            auto channel =
                anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                    connection.client.get(), {receiver_actor, receiver_pin},
                    "TLS retained filter BIO chain");
            const NonblockingSocketPair replacement =
                make_nonblocking_socket_pair_fixture();
            if (SSL_set_fd(
                    connection.client.get(), replacement.left.get()) != 1) {
                fail_openssl(
                    "TLS retained filter BIO chain could not replace its BIO");
            }
            require(
                filter_frees == 0U && socket_frees == 0U,
                "SSL replacement destroyed a BIO still retained by the channel");
            require_error(
                [&] {
                    anonsync::write_sync_replica_tls_record_or_throw(
                        channel, "filter-chain", 1024U,
                        "TLS retained filter BIO chain");
                },
                "BIO changed after authentication",
                "filter BIO replacement inherited authenticated authority");
        }
        require(
            filter_frees == 1U && socket_frees == 1U,
            "authenticated anchor did not release the complete retained BIO chain");
    }

    // Retaining the BIO object is not enough: BIO_set_fd mutates a socket BIO
    // in place and preserves its pointer. The authentication-time kernel socket
    // lifetime independently detects that transport substitution.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS post-auth BIO fd mutation");
        BIO* const read_bio = SSL_get_rbio(pair.connection.client.get());
        BIO* const write_bio = SSL_get_wbio(pair.connection.client.get());
        require(
            read_bio != nullptr && read_bio == write_bio,
            "BIO fd mutation fixture did not expose one direct duplex BIO");
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        if (BIO_set_fd(read_bio, replacement.left.get(), BIO_NOCLOSE) <= 0) {
            fail_openssl(
                "TLS post-auth BIO fd mutation could not change descriptor");
        }
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "bio-fd-mutation", 1024U,
                    "TLS post-auth BIO fd mutation");
            },
            "socket descriptor changed after authentication",
            "in-place BIO_set_fd inherited authenticated socket authority");
        require_error(
            [&] {
                (void)pair.sender_channel.delivery_authority().context();
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS post-auth BIO fd mutation poisoned reuse");
            },
            "poisoned",
            "in-place BIO descriptor mutation left the channel reusable");
    }

    // Exact body bytes become private continuation state before the prefix can
    // be accepted. Mutating a same-length caller buffer afterwards cannot
    // substitute a different canonical frame across the framing cutpoint.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS continuation exact byte ownership");
        std::string frame = "owned-body";
        const std::string expected = frame;
        auto continuation =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, 1024U,
                "TLS continuation exact byte ownership");
        frame.assign(frame.size(), 'x');
        continuation.finish_or_throw();
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, 1024U,
                "TLS continuation exact byte ownership read") == expected,
            "caller mutation substituted bytes after TLS prefix acceptance");
        require_error(
            [&] { continuation.finish_or_throw(); },
            "empty or already finished",
            "completed owned-byte continuation remained reusable");
    }

    // Routine socket backpressure is a retryable transport state after prefix
    // acceptance, not a reason to destroy an otherwise valid authenticated
    // channel. The exact private body buffer and one bounded request survive a
    // wrapper move while a single SSL_write_ex operation is pending.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS incremental write resume");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        make_socket_nonblocking(pair.connection.server_fd.get());
        const std::string frame(2U * 1024U * 1024U, 'w');
        auto writer =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, frame.size(),
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS incremental write resume");
        require(
            writer.active() && writer.frame_bytes() == frame.size() &&
                writer.body_bytes_written() == 0U,
            "fresh TLS writer did not own one exact empty body cutpoint");
        require_error(
            [&] { (void)writer.pending_readiness_or_throw(); },
            "no pending readiness request",
            "fresh TLS writer invented an event-loop target before WANT");
        require(writer.active(),
                "pre-WANT target rejection poisoned the active writer");

        const auto first_want = advance_tls_write_until_want(
            writer, "TLS incremental write resume");
        const auto first_target = writer.pending_readiness_or_throw();
        require(
            first_target.descriptor == pair.connection.client_fd.get() &&
                first_target.readiness ==
                    (first_want ==
                             anonsync::SyncReplicaTlsRecordWriteProgress::WantRead
                         ? anonsync::SyncReplicaTlsSocketReadiness::Readable
                         : anonsync::SyncReplicaTlsSocketReadiness::Writable),
            "TLS write WANT did not expose its exact advisory target");

        auto moved_writer = std::move(writer);
        require(
            !writer.active() && moved_writer.active() &&
                moved_writer.pending_readiness_or_throw() == first_target,
            "moving TLS writer duplicated, lost, or retargeted the pending operation");
        auto reader =
            anonsync::begin_sync_replica_tls_record_read_or_throw(
                pair.receiver_channel, frame.size(),
                anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS incremental write resume reader");

        bool writer_complete = false;
        bool readiness_targets_valid = true;
        std::size_t max_body_step = 0U;
        std::optional<std::string> received;
        for (std::size_t iteration = 0U;
             iteration < 65536U &&
             (!writer_complete || !received.has_value());
             ++iteration) {
            if (!writer_complete) {
                const std::size_t before = static_cast<std::size_t>(
                    moved_writer.body_bytes_written());
                const auto progress = moved_writer.advance_or_throw();
                const std::size_t after =
                    progress ==
                            anonsync::SyncReplicaTlsRecordWriteProgress::Complete
                        ? frame.size()
                        : static_cast<std::size_t>(
                              moved_writer.body_bytes_written());
                if (after < before) {
                    fail("TLS incremental writer moved its body cutpoint backward");
                }
                max_body_step = std::max(max_body_step, after - before);
                if (is_tls_write_want(progress)) {
                    const auto target =
                        moved_writer.pending_readiness_or_throw();
                    readiness_targets_valid =
                        readiness_targets_valid &&
                        target.descriptor ==
                            pair.connection.client_fd.get() &&
                        target.readiness ==
                            (progress ==
                                     anonsync::SyncReplicaTlsRecordWriteProgress::
                                         WantRead
                                 ? anonsync::SyncReplicaTlsSocketReadiness::
                                       Readable
                                 : anonsync::SyncReplicaTlsSocketReadiness::
                                       Writable);
                } else if (progress ==
                           anonsync::SyncReplicaTlsRecordWriteProgress::Complete) {
                    writer_complete = true;
                }
            }

            if (!received.has_value()) {
                const auto progress = reader.advance_or_throw();
                if (is_tls_read_want(progress)) {
                    const auto target = reader.pending_readiness_or_throw();
                    readiness_targets_valid =
                        readiness_targets_valid &&
                        target.descriptor ==
                            pair.connection.server_fd.get();
                } else if (progress ==
                           anonsync::SyncReplicaTlsRecordReadProgress::Complete) {
                    received.emplace(reader.take_frame_or_throw());
                } else if (progress ==
                           anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed) {
                    fail("TLS incremental writer unexpectedly closed its peer");
                }
            }
            std::this_thread::yield();
        }
        require(
            writer_complete && !moved_writer.active() &&
                moved_writer.frame_bytes() == 0U,
            "resumable TLS writer did not release completed stream authority");
        require(
            received.has_value() && *received == frame,
            "resumable TLS writer changed its exact application bytes");
        require(
            max_body_step <= anonsync::kSyncReplicaTlsRecordWriteStepBytes,
            "one TLS write step exceeded the public body budget");
        require(readiness_targets_valid,
                "resumable TLS writer or reader exposed a stale readiness target");
    }

    // Caller-managed mode exposes typed WANT progress but cannot fabricate a
    // library-owned descriptor capability. Rejecting that optional lookup does
    // not itself poison the still-resumable continuation.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS caller-managed write target");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        {
            const std::string frame(2U * 1024U * 1024U, 'c');
            auto writer =
                anonsync::begin_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, frame, frame.size(),
                    "TLS caller-managed write target");
            (void)advance_tls_write_until_want(
                writer, "TLS caller-managed write target");
            require_error(
                [&] { (void)writer.pending_readiness_or_throw(); },
                "caller-managed TLS write has no library-owned poll target",
                "caller-managed writer invented a strict readiness capability");
            require(writer.active(),
                    "rejected caller-managed target lookup poisoned the writer");
        }
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS abandoned caller-managed write reuse");
            },
            "poisoned",
            "abandoned pending writer left an uncertain stream reusable");
    }

    // A readiness target is only advisory. Descriptor-number reuse after WANT
    // is rejected again at target disclosure, and losing O_NONBLOCK is rejected
    // again at the direct exact-operation retry even when polling is skipped.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending write descriptor ABA");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        const std::string frame(2U * 1024U * 1024U, 'a');
        auto writer =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, frame.size(),
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS pending write descriptor ABA");
        (void)advance_tls_write_until_want(
            writer, "TLS pending write descriptor ABA");
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        replace_descriptor_lifetime_or_fail(
            pair.connection.client_fd.get(), replacement,
            "TLS pending write descriptor ABA");
        require_error(
            [&] { (void)writer.pending_readiness_or_throw(); },
            "no longer names the exact observed socket lifetime",
            "pending TLS writer disclosed a target after descriptor ABA");
        require(!writer.active(),
                "write poll-target ABA retained continuation authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS pending write descriptor ABA reuse");
            },
            "poisoned",
            "write poll-target ABA left the stream reusable");
    }

    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending write nonblocking reproof");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        const std::string frame(2U * 1024U * 1024U, 'n');
        auto writer =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, frame.size(),
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS pending write nonblocking reproof");
        (void)advance_tls_write_until_want(
            writer, "TLS pending write nonblocking reproof");
        make_socket_blocking(pair.connection.client_fd.get());
        require_error(
            [&] { (void)writer.advance_or_throw(); },
            "is not nonblocking",
            "direct TLS write retry ignored lost O_NONBLOCK authority");
        require(!writer.active(),
                "failed write readiness reproof retained continuation authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS pending write nonblocking reuse");
            },
            "poisoned",
            "write readiness loss after WANT left the stream reusable");
    }

    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS continuation abandonment");
        {
            auto first =
                anonsync::begin_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, "abandoned", 1024U,
                    "TLS continuation abandonment");
            auto owner = std::move(first);
            require(!first.active() && owner.active(),
                    "TLS continuation move duplicated prefix authority");
        }
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS abandoned continuation reuse");
            },
            "poisoned",
            "abandoned TLS continuation left its stream reusable");
    }

    {
        // The continuation is a shared-state capability, not merely a movable
        // value. Its no-throw destructor must enforce the same process/thread
        // fence as ordinary record I/O before poisoning that shared state.
        TlsConnectionPair connection = make_tls_connection_pair(
            client_context, server_context);
        auto foreign_thread_abandonment =
            anonsync::test::spawn_inherited_test_process_or_throw(
                [&]() -> int {
                    auto sender_channel =
                        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                            connection.client.get(),
                            {receiver_actor, receiver_pin},
                            "TLS foreign-thread continuation abandonment");
                    auto continuation =
                        anonsync::begin_sync_replica_tls_record_write_or_throw(
                            sender_channel, "abandoned", 1024U,
                            "TLS foreign-thread continuation abandonment");
                    std::thread foreign_thread(
                        [owned = std::move(continuation)]() mutable {});
                    foreign_thread.join();
                    return 98;
                },
                "TLS foreign-thread continuation abandonment");
        foreign_thread_abandonment.wait_for_exact_exit(
            anonsync::kSyncProcessCapabilityViolationExitCode,
            std::chrono::seconds(5),
            "TLS foreign-thread continuation abandonment");
        require(
            !foreign_thread_abandonment.active(),
            "foreign-thread TLS continuation abandonment retained process authority");
    }

    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS continuation body failure");
        const std::string frame(2U * 1024U * 1024U, 'b');
        auto continuation =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, frame.size(),
                "TLS continuation body failure");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        require_any_error(
            [&] { continuation.finish_or_throw(); },
            "TLS continuation body failure unexpectedly completed without a reader");
        require(!continuation.active(),
                "failed TLS body retained continuation authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS failed-body reuse");
            },
            "poisoned",
            "failed TLS body left an uncertain stream reusable");
    }

    // A prefix accepted on one authenticated BIO cannot be followed by a body
    // on a replacement BIO, even when both sockets are valid and nonblocking.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS write BIO replacement frontier");
        make_socket_nonblocking(pair.connection.client_fd.get());
        const std::string frame = "bio-replacement-body";
        auto continuation =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, 1024U,
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS write BIO replacement frontier");
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        if (SSL_set_fd(
                pair.connection.client.get(), replacement.left.get()) != 1) {
            fail_openssl(
                "TLS write BIO replacement frontier could not replace BIO");
        }
        require_error(
            [&] { continuation.finish_or_throw(); },
            "BIO changed after authentication",
            "accepted TLS prefix transferred body authority to a replacement BIO");
        require(!continuation.active(),
                "BIO replacement retained accepted-prefix continuation authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS write BIO replacement poisoned reuse");
            },
            "poisoned",
            "prefix/body BIO replacement left an uncertain stream reusable");
    }

    // A strict write binds the socket lifetime before the prefix. Reusing the
    // same descriptor number for a different socket before the body must poison
    // rather than redirecting one accepted record prefix to another stream.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS write descriptor ABA");
        make_socket_nonblocking(pair.connection.client_fd.get());
        const std::string frame = "descriptor-aba-body";
        auto continuation =
            anonsync::begin_sync_replica_tls_record_write_or_throw(
                pair.sender_channel, frame, 1024U,
                anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS write descriptor ABA");

        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        replace_descriptor_lifetime_or_fail(
            pair.connection.client_fd.get(), replacement,
            "TLS write descriptor ABA");
        require_error(
            [&] { continuation.finish_or_throw(); },
            "no longer names the exact observed socket lifetime",
            "strict TLS write accepted descriptor-number ABA after its prefix");
        require(
            !continuation.active(),
            "write descriptor ABA retained continuation authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "TLS write descriptor ABA poisoned reuse");
            },
            "poisoned",
            "write descriptor ABA left an uncertain TLS stream reusable");
    }

    // SSL_get_rfd()/SSL_get_wfd() alone prove only descriptor visibility. A
    // descriptor BIO over a non-socket device must not satisfy the SQLite
    // composition's stronger readiness contract even with O_NONBLOCK present.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS non-socket descriptor policy");
        FileDescriptor device_descriptor(
            ::open("/dev/null", O_RDWR | O_CLOEXEC | O_NONBLOCK));
        if (device_descriptor.get() < 0) {
            fail("TLS transport test could not open a non-socket descriptor");
        }
        if (SSL_set_fd(
                pair.connection.client.get(), device_descriptor.get()) != 1) {
            fail_openssl(
                "TLS transport test could not install a non-socket descriptor BIO");
        }
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_write_or_throw(
                    pair.sender_channel, "12345678", 1024U,
                    anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                        RequireNonblockingSocket,
                    "TLS non-socket descriptor policy");
            },
            "BIO changed after authentication",
            "replacement non-socket BIO bypassed the authentication anchor");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_tls_record_read_continuation(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    // A retryable empty read survives wrapper movement because its exact prefix
    // buffer lives in heap-stable private state.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS incremental read move after WANT");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto continuation =
            anonsync::begin_sync_replica_tls_record_read_or_throw(
                pair.receiver_channel, 1024U,
                anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS incremental read move after WANT");
        require(
            continuation.active() && !continuation.frame_ready() &&
                !continuation.peer_closed() &&
                continuation.prefix_bytes_received() == 0U &&
                continuation.frame_bytes() == 0U &&
                continuation.body_bytes_received() == 0U,
            "fresh TLS reader did not expose one empty active cutpoint");
        require_error(
            [&] { (void)continuation.pending_readiness_or_throw(); },
            "no pending readiness request",
            "fresh TLS reader invented an event-loop target before WANT");
        const auto initial = continuation.advance_or_throw();
        require(
            is_tls_read_want(initial),
            "empty nonblocking TLS reader did not expose retryable readiness");
        const auto pending_target =
            continuation.pending_readiness_or_throw();
        require(
            pending_target.descriptor == pair.connection.server_fd.get() &&
                pending_target.readiness ==
                    (initial ==
                             anonsync::SyncReplicaTlsRecordReadProgress::WantRead
                         ? anonsync::SyncReplicaTlsSocketReadiness::Readable
                         : anonsync::SyncReplicaTlsSocketReadiness::Writable),
            "TLS WANT did not expose its exact advisory socket/event target");
        auto moved = std::move(continuation);
        require(
            !continuation.active() && moved.active() &&
                moved.pending_readiness_or_throw() == pending_target,
            "moving TLS reader duplicated, lost, or retargeted the pending read operation");
        const std::string frame = "heap-stable-read-after-want";
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, frame, 1024U,
            "TLS incremental read move fixture write");
        require(
            finish_tls_record_read(moved, "TLS incremental moved reader") ==
                frame,
            "moved TLS reader changed application bytes after WANT");
        require(
            !moved.active() && !moved.frame_ready() &&
                moved.prefix_bytes_received() == 0U,
            "taken TLS frame retained continuation state");
    }

    // Caller-managed mode may use its own reactor around a nonblocking socket.
    // It receives typed WANT progress, but the library must neither disclose a
    // poll target it did not prove nor poison the still-valid continuation when
    // that optional convenience method is rejected.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS caller-managed poll target");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            "TLS caller-managed poll target");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "caller-managed reader did not expose WANT on an empty socket");
        require_error(
            [&] { (void)reader.pending_readiness_or_throw(); },
            "caller-managed TLS read has no library-owned poll target",
            "caller-managed reader invented a strict readiness capability");
        require(reader.active(),
                "rejected caller-managed poll lookup poisoned the reader");
        const std::string frame = "caller-managed-read-remains-live";
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, frame, 1024U,
            "TLS caller-managed poll target fixture write");
        require(
            finish_tls_record_read(
                reader, "TLS caller-managed reader after target rejection") ==
                frame,
            "caller-managed target rejection changed later record bytes");
    }

    // Prefix and body progress are separately resumable. Moving after WANT in
    // either phase must preserve the exact OpenSSL retry arguments.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS incremental fragmented record");
        make_socket_nonblocking(pair.connection.server_fd.get());
        const std::string frame = "fragmented-record-body";
        const auto prefix = encode_u64_be_fixture(frame.size());
        auto continuation =
            anonsync::begin_sync_replica_tls_record_read_or_throw(
                pair.receiver_channel, 1024U,
                anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS incremental fragmented record");

        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), 3U,
            "TLS fragmented prefix first record");
        require(
            continuation.advance_or_throw() ==
                    anonsync::SyncReplicaTlsRecordReadProgress::Progress &&
                continuation.prefix_bytes_received() == 3U &&
                continuation.frame_bytes() == 0U,
            "TLS reader did not preserve a partial three-byte prefix");
        require(
            is_tls_read_want(continuation.advance_or_throw()),
            "partial TLS prefix did not become retryable without more bytes");
        auto prefix_retry = std::move(continuation);
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data() + 3U,
            prefix.size() - 3U,
            "TLS fragmented prefix second record");
        for (std::size_t iteration = 0U;
             prefix_retry.prefix_bytes_received() != prefix.size() &&
             iteration < 128U;
             ++iteration) {
            const auto progress = prefix_retry.advance_or_throw();
            require(
                progress ==
                        anonsync::SyncReplicaTlsRecordReadProgress::Progress ||
                    is_tls_read_want(progress),
                "TLS prefix retry reached an unexpected terminal state");
        }
        require(
            prefix_retry.prefix_bytes_received() == prefix.size() &&
                prefix_retry.frame_bytes() == frame.size() &&
                prefix_retry.body_bytes_received() == 0U,
            "TLS reader did not validate the complete prefix before body allocation");

        write_tls_fixture_bytes(
            pair.connection.client.get(),
            std::string_view(frame.data(), 2U),
            "TLS fragmented body first record");
        require(
            prefix_retry.advance_or_throw() ==
                    anonsync::SyncReplicaTlsRecordReadProgress::Progress &&
                prefix_retry.body_bytes_received() == 2U,
            "TLS reader did not retain partial body progress");
        require(
            is_tls_read_want(prefix_retry.advance_or_throw()),
            "partial TLS body did not become retryable without more bytes");
        auto body_retry = std::move(prefix_retry);
        write_tls_fixture_bytes(
            pair.connection.client.get(),
            std::string_view(frame.data() + 2U, frame.size() - 2U),
            "TLS fragmented body second record");
        require(
            finish_tls_record_read(body_retry, "TLS fragmented body retry") ==
                frame,
            "TLS body retry changed bytes after moving a pending read");
    }

    // Reserving and abandoning before the first SSL_read_ex call performs no
    // stream work and therefore releases cleanly.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS clean read abandonment");
        make_socket_nonblocking(pair.connection.server_fd.get());
        {
            auto abandoned =
                anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                        RequireNonblockingSocket,
                    "TLS clean read abandonment");
            require(
                abandoned.active(),
                "fresh TLS read reservation was not active before abandonment");
        }
        const std::string frame = "channel-survives-pre-io-abandonment";
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, frame, 1024U,
            "TLS post-abandonment fixture write");
        auto replacement =
            anonsync::begin_sync_replica_tls_record_read_or_throw(
                pair.receiver_channel, 1024U,
                anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                    RequireNonblockingSocket,
                "TLS replacement after clean abandonment");
        require(
            finish_tls_record_read(
                replacement, "TLS replacement after clean abandonment") ==
                frame,
            "pre-I/O abandonment poisoned an untouched TLS stream");
    }

    // Any attempted read, even one that consumes no application byte and only
    // returns WANT, owns pending OpenSSL state. Abandonment is fail-closed.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending read abandonment");
        make_socket_nonblocking(pair.connection.server_fd.get());
        {
            auto abandoned =
                anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                        RequireNonblockingSocket,
                    "TLS pending read abandonment");
            require(
                is_tls_read_want(abandoned.advance_or_throw()),
                "pending read abandonment fixture did not enter WANT");
        }
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS reuse after pending read abandonment");
            },
            "poisoned",
            "abandoned WANT operation left the TLS stream reusable");
    }

    // One reservation serializes both directions and blocks a verifier from
    // re-entering the SSL object while a read operation is pending.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS duplex read reservation");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS duplex read reservation");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS overlapping read reservation");
            },
            "unfinished record read",
            "TLS state admitted two overlapping readers");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "overlap", 1024U,
                    "TLS write during read reservation");
            },
            "unfinished record read",
            "TLS writer bypassed the active read reservation");
        const std::string frame = "original-reader-remains-authoritative";
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, frame, 1024U,
            "TLS duplex reservation fixture write");
        require(
            finish_tls_record_read(reader, "TLS authoritative reader") == frame,
            "rejected overlap poisoned or replaced the original reader");
    }

    // The strict policy is re-proved at every retry. Losing O_NONBLOCK after a
    // WANT is an ambiguous operation and therefore poisons the stream.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS read readiness reproof");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS read readiness reproof");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "read readiness reproof fixture did not enter WANT");
        make_socket_blocking(pair.connection.server_fd.get());
        require_error(
            [&] { (void)reader.advance_or_throw(); },
            "is not nonblocking",
            "TLS read retry ignored lost O_NONBLOCK authority");
        require(
            !reader.active(),
            "failed TLS readiness reproof retained read authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS reuse after readiness loss");
            },
            "poisoned",
            "readiness loss after WANT left the stream reusable");
    }

    // A pending WANT is bound to the exact authenticated BIO object as well as
    // its socket lifetime. Keeping the old fd alive cannot authorize a retry on
    // a fresh BIO installed into the same SSL object.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending WANT BIO replacement");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS pending WANT BIO replacement");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "pending WANT BIO replacement fixture did not enter WANT");
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        if (SSL_set_fd(
                pair.connection.server.get(), replacement.left.get()) != 1) {
            fail_openssl(
                "TLS pending WANT BIO replacement could not install replacement BIO");
        }
        require_error(
            [&] { (void)reader.pending_readiness_or_throw(); },
            "BIO changed after authentication",
            "pending poll target inherited authority across SSL_set_fd");
        require(!reader.active(),
                "failed pending BIO reproof retained read continuation authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS pending WANT BIO replacement poisoned reuse");
            },
            "poisoned",
            "pending WANT BIO replacement left the channel reusable");
    }

    // Direct retry performs the same BIO-object proof even when a caller skips
    // a second poll-target lookup after readiness notification.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending retry BIO fd mutation");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS pending retry BIO fd mutation");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "pending retry BIO fd mutation fixture did not enter WANT");
        BIO* const read_bio = SSL_get_rbio(pair.connection.server.get());
        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        if (BIO_set_fd(read_bio, replacement.left.get(), BIO_NOCLOSE) <= 0) {
            fail_openssl(
                "TLS pending retry BIO fd mutation could not change descriptor");
        }
        require_error(
            [&] { (void)reader.advance_or_throw(); },
            "socket descriptor changed after authentication",
            "exact WANT retry crossed an in-place BIO descriptor mutation");
        require(!reader.active(),
                "failed pending descriptor reproof retained continuation authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS pending retry BIO fd mutation poisoned reuse");
            },
            "poisoned",
            "pending BIO descriptor mutation left the channel reusable");
    }

    // A poll target is advisory, but lookup must not hand an event loop an fd
    // number that has already been recycled. The shared readiness owner re-proves
    // the socket before disclosure and abandons the unresumable read on failure.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS poll target descriptor ABA");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS poll target descriptor ABA");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "poll target descriptor ABA fixture did not reach WANT");
        const auto advisory = reader.pending_readiness_or_throw();
        require(
            advisory.descriptor == pair.connection.server_fd.get(),
            "poll target fixture did not expose the TLS descriptor");

        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        replace_descriptor_lifetime_or_fail(
            pair.connection.server_fd.get(), replacement,
            "TLS poll target descriptor ABA");
        require_error(
            [&] { (void)reader.pending_readiness_or_throw(); },
            "no longer names the exact observed socket lifetime",
            "poll target lookup exposed descriptor-number ABA substitution");
        require(!reader.active(),
                "stale poll target retained continuation authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS poll target descriptor ABA poisoned reuse");
            },
            "poisoned",
            "stale poll target left an uncertain TLS stream reusable");
    }

    // A caller may poll a previously returned target and then resume directly.
    // advance_or_throw() therefore repeats the system-only proof immediately
    // before retrying the exact SSL_read_ex operation.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS read descriptor ABA");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS read descriptor ABA");
        require(
            is_tls_read_want(reader.advance_or_throw()),
            "read descriptor ABA fixture did not reach WANT");

        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        replace_descriptor_lifetime_or_fail(
            pair.connection.server_fd.get(), replacement,
            "TLS read descriptor ABA");
        require_error(
            [&] { (void)reader.advance_or_throw(); },
            "no longer names the exact observed socket lifetime",
            "pending TLS read accepted descriptor-number ABA substitution");
        require(!reader.active(),
                "read descriptor ABA retained continuation authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS read descriptor ABA poisoned reuse");
            },
            "poisoned",
            "read descriptor ABA left an uncertain TLS stream reusable");
    }

    // A successful partial read ends the prior OpenSSL operation. The next
    // fresh step must re-attest both the TLS session and the exact BIO/socket
    // lifetime rather than treating all later calls as WANT continuations.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS fresh-step descriptor ABA");
        make_socket_nonblocking(pair.connection.server_fd.get());
        const auto prefix = encode_u64_be_fixture(17U);
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS fresh-step descriptor ABA");
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), 3U,
            "TLS fresh-step descriptor ABA prefix");
        require(
            reader.advance_or_throw() ==
                    anonsync::SyncReplicaTlsRecordReadProgress::Progress &&
                reader.prefix_bytes_received() == 3U,
            "fresh-step ABA fixture did not complete one partial read operation");

        const NonblockingSocketPair replacement =
            make_nonblocking_socket_pair_fixture();
        replace_descriptor_lifetime_or_fail(
            pair.connection.server_fd.get(), replacement,
            "TLS fresh-step descriptor ABA");
        require_error(
            [&] { (void)reader.advance_or_throw(); },
            "no longer names the exact observed socket lifetime",
            "fresh TLS read step accepted descriptor-number ABA after progress");
        require(!reader.active(),
                "fresh-step descriptor ABA retained continuation authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS fresh-step descriptor ABA poisoned reuse");
            },
            "poisoned",
            "fresh-step descriptor ABA left the stream reusable");
    }

    // Each body call is bounded independently of the peer-advertised frame.
    // This keeps one event-loop turn finite even when the total accepted frame
    // is much larger than the per-step transport budget.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS bounded read step");
        make_socket_nonblocking(pair.connection.server_fd.get());
        const std::string frame(
            static_cast<std::size_t>(
                anonsync::kSyncReplicaTlsRecordReadStepBytes + 32U * 1024U),
            's');
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, frame,
            static_cast<std::uint64_t>(frame.size()),
            "TLS bounded read step fixture write");
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel,
            static_cast<std::uint64_t>(frame.size()),
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS bounded read step");
        std::size_t previous_body = 0U;
        bool complete = false;
        for (std::size_t iteration = 0U; iteration < 4096U; ++iteration) {
            const auto step = reader.advance_or_throw();
            const std::size_t current_body = static_cast<std::size_t>(
                reader.body_bytes_received());
            require(
                current_body >= previous_body &&
                    current_body - previous_body <=
                        anonsync::kSyncReplicaTlsRecordReadStepBytes,
                "one TLS read step exceeded the public body budget");
            previous_body = current_body;
            if (step == anonsync::SyncReplicaTlsRecordReadProgress::Complete) {
                complete = true;
                break;
            }
            require(
                step == anonsync::SyncReplicaTlsRecordReadProgress::Progress ||
                    is_tls_read_want(step),
                "bounded TLS read reached an unexpected terminal state");
        }
        require(complete && reader.take_frame_or_throw() == frame,
                "bounded TLS body steps did not preserve the complete frame");
    }

    // A close_notify before any application byte is a terminal connection
    // event, not an invalid frame. It closes the channel without inventing
    // poisoning or a zero-length record.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS clean peer close before frame");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS clean peer close before frame");
        send_tls_close_notify(
            pair.connection.client.get(),
            "TLS clean peer close before frame");
        anonsync::SyncReplicaTlsRecordReadProgress terminal =
            anonsync::SyncReplicaTlsRecordReadProgress::Progress;
        for (std::size_t iteration = 0U; iteration < 128U; ++iteration) {
            terminal = reader.advance_or_throw();
            if (terminal ==
                anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed) {
                break;
            }
            require(
                is_tls_read_want(terminal),
                "pre-frame close reported application progress");
        }
        require(
            terminal ==
                    anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed &&
                !reader.active() && reader.peer_closed() &&
                !reader.frame_ready() &&
                reader.prefix_bytes_received() == 0U,
            "clean pre-frame TLS close was not a distinct terminal state");
        require_error(
            [&] { (void)reader.take_frame_or_throw(); },
            "no complete frame",
            "clean peer close fabricated a readable frame");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS read after clean peer close");
            },
            "closed by its peer",
            "clean peer close left the authenticated channel open");
    }

    // A close after an accepted prefix is truncation. The record cannot be
    // resynchronized and the channel is poisoned.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS truncated body close");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS truncated body close");
        const auto prefix = encode_u64_be_fixture(5U);
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), prefix.size(),
            "TLS truncated body prefix");
        for (std::size_t iteration = 0U;
             reader.prefix_bytes_received() != prefix.size() &&
             iteration < 128U;
             ++iteration) {
            const auto progress = reader.advance_or_throw();
            require(
                progress ==
                        anonsync::SyncReplicaTlsRecordReadProgress::Progress ||
                    is_tls_read_want(progress),
                "truncated-body prefix reached an unexpected terminal state");
        }
        require(
            reader.prefix_bytes_received() == prefix.size() &&
                reader.frame_bytes() == 5U,
            "truncated-body fixture did not establish a valid prefix");
        send_tls_close_notify(
            pair.connection.client.get(), "TLS truncated body close");
        require_session_io_error(
            [&] {
                for (std::size_t iteration = 0U; iteration < 128U;
                     ++iteration) {
                    const auto progress = reader.advance_or_throw();
                    if (!is_tls_read_want(progress)) {
                        fail("truncated TLS body did not reject peer close");
                    }
                }
                fail("truncated TLS body did not observe peer close");
            },
            "before the complete record",
            "TLS reader accepted a close after framing progress");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "reuse", 1024U,
                    "TLS truncated-body channel reuse");
            },
            "poisoned",
            "truncated TLS record left the stream reusable");
    }

    // The advertised length is validated before any body allocation or read.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS incremental over-limit prefix");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 16U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS incremental over-limit prefix");
        const auto prefix = encode_u64_be_fixture(4096U);
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), prefix.size(),
            "TLS incremental over-limit prefix");
        require_error(
            [&] {
                for (std::size_t iteration = 0U; iteration < 128U;
                     ++iteration) {
                    const auto progress = reader.advance_or_throw();
                    if (is_tls_read_want(progress)) continue;
                    if (progress ==
                        anonsync::SyncReplicaTlsRecordReadProgress::Progress) {
                        continue;
                    }
                    fail("over-limit TLS prefix reached an unexpected terminal state");
                }
                fail("over-limit TLS prefix was not rejected");
            },
            "above the configured limit",
            "TLS reader accepted an over-limit advertised body");
        require(
            !reader.active() && reader.body_bytes_received() == 0U,
            "over-limit prefix allocated or retained body progress");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 16U,
                    "TLS over-limit channel reuse");
            },
            "poisoned",
            "over-limit peer frame left the TLS stream reusable");
    }

    // Direct socket provenance is required by the strict event-loop policy.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS read non-socket descriptor policy");
        FileDescriptor device_descriptor(
            ::open("/dev/null", O_RDWR | O_CLOEXEC | O_NONBLOCK));
        if (device_descriptor.get() < 0) {
            fail("TLS read test could not open a non-socket descriptor");
        }
        if (SSL_set_fd(
                pair.connection.server.get(), device_descriptor.get()) != 1) {
            fail_openssl(
                "TLS read test could not install a non-socket descriptor BIO");
        }
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                        RequireNonblockingSocket,
                    "TLS read non-socket descriptor policy");
            },
            "BIO changed after authentication",
            "replacement non-socket BIO bypassed strict receive authority");
    }

    // No-throw cleanup remains process/thread-affine even when no byte has yet
    // been attempted and same-thread cleanup would otherwise be clean.
    {
        TlsConnectionPair connection = make_tls_connection_pair(
            client_context, server_context);
        auto foreign_thread_abandonment =
            anonsync::test::spawn_inherited_test_process_or_throw(
                [&]() -> int {
                    auto receiver_channel =
                        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                            connection.server.get(),
                            {sender_actor, sender_pin},
                            "TLS foreign-thread read abandonment");
                    make_socket_nonblocking(connection.server_fd.get());
                    auto continuation =
                        anonsync::begin_sync_replica_tls_record_read_or_throw(
                            receiver_channel, 1024U,
                            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                                RequireNonblockingSocket,
                            "TLS foreign-thread read abandonment");
                    std::thread foreign_thread(
                        [owned = std::move(continuation)]() mutable {});
                    foreign_thread.join();
                    return 97;
                },
                "TLS foreign-thread read abandonment");
        foreign_thread_abandonment.wait_for_exact_exit(
            anonsync::kSyncProcessCapabilityViolationExitCode,
            std::chrono::seconds(5),
            "TLS foreign-thread read abandonment");
        require(
            !foreign_thread_abandonment.active(),
            "foreign-thread TLS reader cleanup retained process authority");
    }

    // The blocking compatibility wrapper delegates to the same state machine.
    // On a nonblocking WANT it throws and its active continuation poisons.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS legacy read WANT delegation");
        make_socket_nonblocking(pair.connection.server_fd.get());
        require_error(
            [&] {
                (void)anonsync::read_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS legacy read WANT delegation");
            },
            "nonblocking TLS readiness loss",
            "legacy TLS reader did not delegate WANT handling");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "TLS legacy read WANT channel reuse");
            },
            "poisoned",
            "legacy WANT failure left a pending SSL read reusable");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}


void test_tls_record_duplex_poll_owner(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    // The owner accepts only a strict continuation at one exact WANT frontier.
    // Deadline expiry is a nonterminal scheduling result and must preserve that
    // exact retry target without entering OpenSSL.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS duplex poll read frontier");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS duplex poll read frontier");
        require_error(
            [&] {
                (void)anonsync::
                    poll_and_advance_sync_replica_tls_record_read_or_throw(
                        reader, std::chrono::steady_clock::now(),
                        "TLS poll before read WANT");
            },
            "no pending readiness request",
            "read poll owner accepted a continuation before WANT");
        require(reader.active(),
                "pre-WANT read poll rejection consumed the continuation");
        require(is_tls_read_want(reader.advance_or_throw()),
                "read poll fixture did not enter an exact WANT frontier");
        const auto exact_target = reader.pending_readiness_or_throw();

        require(
            anonsync::poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader, std::chrono::steady_clock::now(),
                "TLS already-expired read poll") ==
                anonsync::SyncReplicaTlsRecordReadPollProgress::DeadlineExpired,
            "already-expired read poll did not report policy expiry");
        require(reader.active() &&
                    reader.pending_readiness_or_throw() == exact_target,
                "expired read poll changed the exact pending capability");
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader,
                std::chrono::steady_clock::now() +
                    std::chrono::milliseconds(12),
                "TLS bounded idle read poll") ==
                anonsync::SyncReplicaTlsRecordReadPollProgress::DeadlineExpired,
            "idle read poll did not expire without transport progress");
        require(reader.active() &&
                    reader.pending_readiness_or_throw() == exact_target,
                "idle read timeout consumed or retargeted the pending retry");

        const std::string frame = "duplex-poll-frame";
        const auto prefix = encode_u64_be_fixture(frame.size());
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), prefix.size(),
            "TLS duplex poll prefix");
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader,
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(1),
                "TLS bounded prefix read poll") ==
                anonsync::SyncReplicaTlsRecordReadPollProgress::Progress,
            "one readable wakeup did not perform one prefix operation");
        require(reader.prefix_bytes_received() == prefix.size() &&
                    reader.body_bytes_received() == 0U,
                "one read poll step crossed the prefix/body cutpoint");
        require(is_tls_read_want(reader.advance_or_throw()),
                "post-prefix fixture did not establish one body WANT");
        write_tls_fixture_bytes(
            pair.connection.client.get(), frame,
            "TLS duplex poll body");
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader,
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(1),
                "TLS bounded body read poll") ==
                anonsync::SyncReplicaTlsRecordReadPollProgress::Complete,
            "body readiness did not complete the exact pending record");
        require(reader.take_frame_or_throw() == frame,
                "read poll owner changed exact TLS record bytes");
    }

    // A raw hangup bit is only a wakeup. OpenSSL remains the owner of clean
    // close_notify versus truncation classification.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS duplex poll clean close");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS duplex poll clean close");
        require(is_tls_read_want(reader.advance_or_throw()),
                "clean-close poll fixture did not enter WANT");
        send_tls_close_notify(
            pair.connection.client.get(), "TLS duplex poll close notify");
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader,
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(1),
                "TLS duplex poll clean close") ==
                anonsync::SyncReplicaTlsRecordReadPollProgress::PeerClosed,
            "poll owner promoted raw readiness over OpenSSL close semantics");
        require(reader.peer_closed() && !reader.active(),
                "clean close did not release the read reservation");
    }

    // A real signal arrives while poll owns the thread. EINTR cannot renew the
    // caller's budget or retain a stale pollfd; the exact WANT survives expiry.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS duplex poll EINTR");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS duplex poll EINTR");
        require(is_tls_read_want(reader.advance_or_throw()),
                "EINTR poll fixture did not enter WANT");
        const auto target = reader.pending_readiness_or_throw();

        struct sigaction action {};
        action.sa_handler = tls_poll_signal_handler;
        sigemptyset(&action.sa_mask);
        action.sa_flags = 0;
        struct sigaction previous {};
        if (::sigaction(SIGUSR1, &action, &previous) != 0) {
            fail("TLS poll test could not install SIGUSR1 handler");
        }
        tls_poll_signal_count = 0;
        const pthread_t owner_thread = ::pthread_self();
        std::thread interrupter([owner_thread] {
            std::this_thread::sleep_for(std::chrono::milliseconds(4));
            (void)::pthread_kill(owner_thread, SIGUSR1);
        });

        std::optional<anonsync::SyncReplicaTlsRecordReadPollProgress> progress;
        std::exception_ptr failure;
        try {
            progress = anonsync::
                poll_and_advance_sync_replica_tls_record_read_or_throw(
                    reader,
                    std::chrono::steady_clock::now() +
                        std::chrono::milliseconds(30),
                    "TLS duplex poll EINTR");
        } catch (...) {
            failure = std::current_exception();
        }
        interrupter.join();
        if (::sigaction(SIGUSR1, &previous, nullptr) != 0) {
            fail("TLS poll test could not restore SIGUSR1 handler");
        }
        if (failure) std::rethrow_exception(failure);

        require(tls_poll_signal_count > 0,
                "signal was not delivered during bounded poll exercise");
        require(progress.has_value() &&
                    *progress == anonsync::
                        SyncReplicaTlsRecordReadPollProgress::DeadlineExpired,
                "interrupted poll did not honor its original absolute deadline");
        require(reader.active() &&
                    reader.pending_readiness_or_throw() == target,
                "interrupted poll changed the exact pending retry");
    }

    // The same owner drives write WANT without hiding a body-progress loop. A
    // saturated sender first proves timeout retention; cooperative read/write
    // steps then deliver the exact large frame, and every write wakeup advances
    // by at most the public 64 KiB operation budget.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS duplex poll write frontier");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        make_socket_nonblocking(pair.connection.server_fd.get());
        const std::string frame(2U * 1024U * 1024U, 'p');
        auto writer = anonsync::begin_sync_replica_tls_record_write_or_throw(
            pair.sender_channel, frame, frame.size(),
            anonsync::SyncReplicaTlsRecordWriteReadinessPolicy::
                RequireNonblockingSocket,
            "TLS duplex poll write frontier");
        require_error(
            [&] {
                (void)anonsync::
                    poll_and_advance_sync_replica_tls_record_write_or_throw(
                        writer, std::chrono::steady_clock::now(),
                        "TLS poll before write WANT");
            },
            "no pending readiness request",
            "write poll owner accepted a continuation before WANT");
        require(writer.active(),
                "pre-WANT write poll rejection consumed the continuation");
        (void)advance_tls_write_until_want(
            writer, "TLS duplex poll write frontier");
        const auto exact_target = writer.pending_readiness_or_throw();
        const auto exact_cutpoint = writer.body_bytes_written();
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_write_or_throw(
                writer, std::chrono::steady_clock::now(),
                "TLS already-expired write poll") ==
                anonsync::SyncReplicaTlsRecordWritePollProgress::DeadlineExpired,
            "already-expired write poll did not report policy expiry");
        require(writer.active() &&
                    writer.body_bytes_written() == exact_cutpoint &&
                    writer.pending_readiness_or_throw() == exact_target,
                "expired write poll consumed or retargeted the exact retry");
        require(
            anonsync::poll_and_advance_sync_replica_tls_record_write_or_throw(
                writer,
                std::chrono::steady_clock::now() +
                    std::chrono::milliseconds(12),
                "TLS bounded idle write poll") ==
                anonsync::SyncReplicaTlsRecordWritePollProgress::DeadlineExpired,
            "saturated write poll did not expire without peer progress");
        require(writer.active() &&
                    writer.body_bytes_written() == exact_cutpoint &&
                    writer.pending_readiness_or_throw() == exact_target,
                "idle write timeout changed the exact pending operation");

        const auto transfer = complete_pending_tls_write_with_reader(
            writer, pair.receiver_channel, frame.size(),
            "TLS duplex cooperative transfer");
        require(transfer.frame == frame,
                "duplex poll owner changed the exact large record bytes");
        require(transfer.write_poll_operations > 0U,
                "cooperative transfer never exercised a write poll operation");
        require(transfer.max_write_step <=
                    anonsync::kSyncReplicaTlsRecordWriteStepBytes,
                "cooperative transfer hid an unbounded TLS write step");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_file_tls_receiver_exchange(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    const std::vector<std::string> destination{receiver_actor.device_id};
    const auto limits = file_service_limits();

    // Receiver configuration and live-channel authority must be proved before
    // even an already-buffered request prefix is consumed. A failed session
    // construction preserves the caller's capability because ownership has not
    // transferred; invoking the borrowed one-shot exchange then fails closed
    // without draining any ciphertext or touching durable state.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver preflight");
        TempDatabasePath receiver_path("anonsync-file-tls-preflight");
        auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb receiver_database =
            open_database(receiver_path.path);
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, "folder-file-tls-preflight", receiver_actor,
            owner_limits(), "file TLS preflight receiver", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService sender_only_service(
            receiver, nullptr, limits, "file TLS sender-only receiver service");
        const auto before_receiver = receiver.snapshot_or_throw();

        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, "request-must-remain-buffered", 1024U,
            "file TLS preflight buffered request");
        make_socket_nonblocking(pair.connection.server_fd.get());
        const int pending_before = pending_socket_bytes_or_fail(
            pair.connection.server_fd.get(), "file TLS preflight");
        require(pending_before > 0,
                "file TLS preflight fixture did not buffer request ciphertext");

        const auto request_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        const auto receipt_deadline =
            std::chrono::steady_clock::now() + std::chrono::seconds(2);
        require_error(
            [&] {
                anonsync::SyncReplicaFileTlsReceiverSession rejected(
                    sender_only_service, std::move(pair.receiver_channel),
                    request_deadline, receipt_deadline,
                    "file TLS rejected receiver session");
            },
            "requires a receiver file-effect owner",
            "receiver session consumed a channel before configuration preflight");
        require(
            pending_socket_bytes_or_fail(
                pair.connection.server_fd.get(),
                "file TLS session-construction preflight") == pending_before,
            "session-construction preflight consumed buffered application bytes");

        require_error(
            [&] {
                (void)anonsync::
                    receive_one_sync_replica_file_delivery_over_tls_or_throw(
                        sender_only_service, pair.receiver_channel,
                        request_deadline, receipt_deadline,
                        "file TLS borrowed preflight rejection");
            },
            "requires a receiver file-effect owner",
            "borrowed receiver exchange read before proving effect authority");
        require(
            pending_socket_bytes_or_fail(
                pair.connection.server_fd.get(),
                "file TLS borrowed preflight") == pending_before &&
                receiver.snapshot_or_throw() == before_receiver,
            "receiver preflight consumed ciphertext or changed durable evidence");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 1024U,
                    "file TLS rejected preflight reuse");
            },
            "poisoned",
            "failed borrowed preflight left the one-shot channel reusable");
        require_socket_has_no_pending_bytes(
            pair.connection.client_fd.get(),
            "receiver preflight emitted response ciphertext");
    }

    // One production owner must consume the complete request before durable
    // authority, publish the exact file, re-attest the live channel at the
    // response frontier, and return the terminal receipt that settles only the
    // exact sender attempt.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver exchange success");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-receiver-success");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 800U;
        anonsync::SyncSqliteDb sender_database =
            open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-receiver-success";
        anonsync::SyncReplicaSqliteOwner sender(
            sender_database.db, folder, sender_actor, owner_limits(),
            "file TLS receiver success sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS receiver success receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS receiver success effects");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, limits,
            "file TLS receiver success sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits,
            "file TLS receiver success receiver service");

        const std::string payload = "receiver-exchange-terminal-payload";
        const auto operation = sender.create_local_file_or_throw(
            "receiver-success.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = sender_service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(),
            "receiver-success-worker", 30U,
            payload_snapshot(folder, payload));
        require(outbound.has_value(),
                "receiver exchange did not claim its success request");
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, outbound->request_frame,
            limits.max_request_frame_bytes,
            "file TLS receiver success request write");
        make_socket_nonblocking(pair.connection.server_fd.get());

        anonsync::SyncReplicaFileTlsReceiverSession receiver_session(
            receiver_service, std::move(pair.receiver_channel),
            std::chrono::steady_clock::now() + std::chrono::seconds(2),
            std::chrono::steady_clock::now() + std::chrono::seconds(2),
            "file TLS receiver success session");
        require(receiver_session.active(),
                "receiver session did not take exclusive channel ownership");
        anonsync::SyncReplicaFileTlsReceiverSession moved_session(
            std::move(receiver_session));
        require(!receiver_session.active() && moved_session.active(),
                "receiver session move left two apparent channel owners");
        const auto result = moved_session.run_or_throw();
        require(!moved_session.active(),
                "completed receiver session retained application authority");
        require_error(
            [&] { (void)moved_session.run_or_throw(); },
            "not active",
            "receiver session accepted a second application request");
        require(
            result.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::ReceiptSent &&
                result.inbound.has_value() &&
                result.inbound->receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published &&
                result.request_prefix_bytes_received ==
                    anonsync::kSyncReplicaTlsRecordPrefixBytes &&
                result.request_frame_bytes == outbound->request_frame.size() &&
                result.request_body_bytes_received ==
                    outbound->request_frame.size() &&
                result.receipt_write_started &&
                result.receipt_prefix_bytes_written ==
                    anonsync::kSyncReplicaTlsRecordPrefixBytes &&
                result.receipt_prefix_accepted &&
                result.receipt_frame_bytes ==
                    result.inbound->receipt_frame.size() &&
                result.receipt_body_bytes_written ==
                    result.inbound->receipt_frame.size(),
            "receiver exchange did not preserve its request/effect/receipt cutpoints");
        require(
            read_binary_file(workspace.files / "receiver-success.bin") ==
                payload,
            "receiver exchange receipt preceded exact visible file publication");

        const std::string receipt_frame =
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.sender_channel, limits.max_receipt_frame_bytes,
                "file TLS receiver success receipt read");
        require(receipt_frame == result.inbound->receipt_frame,
                "receiver exchange changed the exact terminal receipt frame");
        clock->epoch = 801U;
        require(
            sender_service.apply_receipt_or_throw(
                pair.sender_channel.delivery_authority(), outbound->request,
                receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::
                    EffectSettled,
            "receiver exchange terminal receipt did not settle the exact claim");
        const auto sender_snapshot = sender.snapshot_or_throw();
        const auto receiver_snapshot = receiver.snapshot_or_throw();
        require(sender_snapshot.outbox.empty() &&
                    sender_snapshot.operation_set_digest ==
                        receiver_snapshot.operation_set_digest &&
                    sender_snapshot.evidence_set_digest ==
                        receiver_snapshot.evidence_set_digest &&
                    sender_snapshot.visible_state_digest ==
                        receiver_snapshot.visible_state_digest,
                "receiver exchange did not converge canonical replica evidence");
    }

    // A response budget that is already exhausted after the complete request
    // must not write even one receipt prefix. The durable effect survives, the
    // old stream is discarded, and a fresh exact attempt reconciles to the same
    // effect through receiver idempotency.
    {
        auto first_pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver receipt timeout");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-receiver-timeout");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 900U;
        anonsync::SyncSqliteDb sender_database =
            open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-receiver-timeout";
        anonsync::SyncReplicaSqliteOwner sender(
            sender_database.db, folder, sender_actor, owner_limits(),
            "file TLS timeout sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS timeout receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS timeout effects");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, limits, "file TLS timeout sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits, "file TLS timeout receiver service");

        const std::string payload = "receipt-timeout-idempotent-payload";
        const auto operation = sender.create_local_file_or_throw(
            "receiver-timeout.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto first = sender_service.claim_next_request_or_throw(
            first_pair.sender_channel.delivery_authority(),
            "receipt-timeout-first", 1U,
            payload_snapshot(folder, payload));
        require(first.has_value(),
                "receipt-timeout fixture did not claim attempt 1");
        anonsync::write_sync_replica_tls_record_or_throw(
            first_pair.sender_channel, first->request_frame,
            limits.max_request_frame_bytes,
            "file TLS receipt-timeout request write");
        make_socket_nonblocking(first_pair.connection.server_fd.get());

        const auto expired =
            anonsync::receive_one_sync_replica_file_delivery_over_tls_or_throw(
                receiver_service, first_pair.receiver_channel,
                std::chrono::steady_clock::now() + std::chrono::seconds(2),
                std::chrono::steady_clock::now(),
                "file TLS receipt-timeout exchange");
        require(
            expired.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::
                        ReceiptDeadlineExpired &&
                expired.inbound.has_value() &&
                expired.inbound->receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published &&
                !expired.receipt_write_started &&
                expired.receipt_prefix_bytes_written == 0U &&
                !expired.receipt_prefix_accepted &&
                expired.receipt_body_bytes_written == 0U,
            "expired receipt budget rolled back effect or emitted a response prefix");
        require_socket_has_no_pending_bytes(
            first_pair.connection.client_fd.get(),
            "expired receiver exchange emitted receipt ciphertext");
        require(
            read_binary_file(workspace.files / "receiver-timeout.bin") ==
                payload,
            "receipt timeout lost the durable visible effect");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    first_pair.receiver_channel, "reuse", 64U,
                    "file TLS receipt-timeout server reuse");
            },
            "poisoned",
            "receipt timeout left the old application stream reusable");
        const auto live_after_timeout = sender.snapshot_or_throw();
        require(live_after_timeout.outbox.size() == 1U &&
                    live_after_timeout.outbox.front().lease.claim_id ==
                        first->claim.intent.lease.claim_id,
                "receiver response timeout settled or released the sender claim");

        clock->epoch = 902U;
        auto retry_pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver exact retry");
        const auto retry = sender_service.claim_next_request_or_throw(
            retry_pair.sender_channel.delivery_authority(),
            "receipt-timeout-retry", 30U,
            payload_snapshot(folder, payload));
        require(retry.has_value() &&
                    retry->claim.intent.lease.claim_id !=
                        first->claim.intent.lease.claim_id &&
                    retry->claim.intent.lease.dispatch_attempts ==
                        first->claim.intent.lease.dispatch_attempts + 1U,
                "receipt timeout did not mint one fresh exact retry attempt");
        anonsync::write_sync_replica_tls_record_or_throw(
            retry_pair.sender_channel, retry->request_frame,
            limits.max_request_frame_bytes,
            "file TLS exact-retry request write");
        make_socket_nonblocking(retry_pair.connection.server_fd.get());
        const auto retried =
            anonsync::receive_one_sync_replica_file_delivery_over_tls_or_throw(
                receiver_service, retry_pair.receiver_channel,
                std::chrono::steady_clock::now() + std::chrono::seconds(2),
                std::chrono::steady_clock::now() + std::chrono::seconds(2),
                "file TLS exact-retry exchange");
        require(
            retried.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::ReceiptSent &&
                retried.inbound.has_value() &&
                retried.inbound->receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::
                        AlreadyPublished,
            "exact retry repeated or lost the receiver's durable effect");
        const std::string retry_receipt =
            anonsync::read_sync_replica_tls_record_or_throw(
                retry_pair.sender_channel, limits.max_receipt_frame_bytes,
                "file TLS exact-retry receipt read");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    retry_pair.receiver_channel, 64U,
                    "file TLS completed receiver reuse");
            },
            "poisoned",
            "completed borrowed receiver exchange permitted a second record");
        clock->epoch = 903U;
        require(
            sender_service.apply_receipt_or_throw(
                retry_pair.sender_channel.delivery_authority(), retry->request,
                retry_receipt) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::
                    EffectSettled &&
                sender.snapshot_or_throw().outbox.empty(),
            "idempotent retry receipt did not settle the fresh exact attempt");
        const auto effect_snapshot = effect.snapshot_or_throw();
        require(effect_snapshot.effects.size() == 1U &&
                    effect_snapshot.effects.front().state ==
                        anonsync::SyncReplicaFileEffectState::Published &&
                    read_binary_file(
                        workspace.files / "receiver-timeout.bin") == payload,
                "idempotent retry created a second or changed receiver effect");
    }

    // Receipt-prefix backpressure is now a retained post-effect continuation,
    // not an exception-only hole. A saturated receiver send path forces the
    // first SSL_write_ex to return WANT_WRITE with zero accepted prefix bytes.
    // Deadline expiry preserves the durable effect, reports the exact attempted
    // cutpoint, and discards the application stream for fresh-channel retry.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin,
            "file TLS receiver receipt-prefix WANT");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-receipt-prefix-want");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 950U;
        anonsync::SyncSqliteDb sender_database =
            open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-receipt-prefix-want";
        anonsync::SyncReplicaSqliteOwner sender(
            sender_database.db, folder, sender_actor, owner_limits(),
            "file TLS receipt-prefix WANT sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS receipt-prefix WANT receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS receipt-prefix WANT effects");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, limits,
            "file TLS receipt-prefix WANT sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits,
            "file TLS receipt-prefix WANT receiver service");

        const std::string payload = "receipt-prefix-want-payload";
        const auto operation = sender.create_local_file_or_throw(
            "receiver-prefix-want.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = sender_service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(),
            "receipt-prefix-want-worker", 30U,
            payload_snapshot(folder, payload));
        require(outbound.has_value(),
                "receipt-prefix WANT fixture did not claim its request");
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, outbound->request_frame,
            limits.max_request_frame_bytes,
            "file TLS receipt-prefix WANT request write");

        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.server_fd.get());
        const int receive_bytes = 1024;
        if (::setsockopt(
                pair.connection.client_fd.get(), SOL_SOCKET, SO_RCVBUF,
                &receive_bytes, sizeof(receive_bytes)) != 0) {
            fail("receipt-prefix WANT could not constrain sender receive buffer");
        }
        const std::size_t saturated = saturate_raw_socket_send_path_or_fail(
            pair.connection.server_fd.get(),
            "file TLS receipt-prefix WANT");
        require(saturated > 0U,
                "receipt-prefix WANT did not saturate the response path");

        const auto expired =
            anonsync::receive_one_sync_replica_file_delivery_over_tls_or_throw(
                receiver_service, pair.receiver_channel,
                std::chrono::steady_clock::now() + std::chrono::seconds(2),
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(2),
                "file TLS receipt-prefix WANT exchange");
        require(
            expired.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::
                        ReceiptDeadlineExpired &&
                expired.inbound.has_value() &&
                expired.inbound->receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::
                        Published &&
                expired.receipt_write_started &&
                expired.receipt_prefix_bytes_written == 0U &&
                !expired.receipt_prefix_accepted &&
                expired.receipt_body_bytes_written == 0U,
            "receipt-prefix WANT was not retained as an exact post-effect timeout"
            " (disposition=" +
                std::to_string(static_cast<int>(expired.disposition)) +
                ", started=" + std::to_string(expired.receipt_write_started) +
                ", prefix=" +
                std::to_string(expired.receipt_prefix_bytes_written) +
                ", prefix_complete=" +
                std::to_string(expired.receipt_prefix_accepted) +
                ", body=" +
                std::to_string(expired.receipt_body_bytes_written) + ")");
        require(
            read_binary_file(workspace.files / "receiver-prefix-want.bin") ==
                    payload &&
                effect.snapshot_or_throw().effects.size() == 1U,
            "receipt-prefix WANT lost or repeated the durable visible effect");
        require(
            sender.snapshot_or_throw().outbox.size() == 1U,
            "receipt-prefix WANT locally settled the sender without a receipt");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "reuse", 64U,
                    "file TLS receipt-prefix WANT server reuse");
            },
            "poisoned",
            "receipt-prefix WANT timeout left the old stream reusable");
    }

    // A genuine nonblocking WANT after an authenticated prefix and partial
    // body retains exact local progress until the absolute request cutpoint.
    // Timeout still cannot invoke the file/evidence service, and unwinding the
    // pending SSL_read_ex retry poisons the incomplete stream.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver partial timeout");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-partial-timeout");
        auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-partial-timeout";
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS partial-timeout receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS partial-timeout effects");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits,
            "file TLS partial-timeout receiver service");
        const auto before_receiver = receiver.snapshot_or_throw();
        const auto before_effect = effect.snapshot_or_throw();
        constexpr std::uint64_t advertised_bytes = 4096U;
        const auto prefix = encode_u64_be_fixture(advertised_bytes);
        const std::string partial_body = "partial-canonical-request";
        write_tls_fixture_bytes(
            pair.connection.client.get(), prefix.data(), prefix.size(),
            "file TLS partial-timeout prefix");
        write_tls_fixture_bytes(
            pair.connection.client.get(), partial_body,
            "file TLS partial-timeout body");
        make_socket_nonblocking(pair.connection.server_fd.get());

        const auto expired =
            anonsync::receive_one_sync_replica_file_delivery_over_tls_or_throw(
                receiver_service, pair.receiver_channel,
                std::chrono::steady_clock::now() +
                    std::chrono::milliseconds(20),
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(2),
                "file TLS partial-timeout exchange");
        require(
            expired.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::
                        RequestDeadlineExpired &&
                !expired.inbound.has_value() &&
                expired.request_prefix_bytes_received ==
                    anonsync::kSyncReplicaTlsRecordPrefixBytes &&
                expired.request_frame_bytes == advertised_bytes &&
                expired.request_body_bytes_received == partial_body.size() &&
                !expired.receipt_write_started &&
                expired.receipt_prefix_bytes_written == 0U &&
                !expired.receipt_prefix_accepted,
            "partial request timeout lost its exact local framing cutpoint");
        require(receiver.snapshot_or_throw() == before_receiver &&
                    effect.snapshot_or_throw() == before_effect,
                "partial request timeout invoked durable receiver authority");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 64U,
                    "file TLS partial-timeout reuse");
            },
            "poisoned",
            "partial request timeout left its pending TLS retry reusable");
    }

    // An already-expired request budget performs no TLS operation and invokes
    // no durable owner. The one-shot channel is discarded so later bytes cannot
    // be interpreted under a conversation whose policy owner has returned.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver request timeout");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-request-timeout");
        auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-request-timeout";
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS request-timeout receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS request-timeout effects");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits,
            "file TLS request-timeout receiver service");
        const auto before_receiver = receiver.snapshot_or_throw();
        const auto before_effect = effect.snapshot_or_throw();
        make_socket_nonblocking(pair.connection.server_fd.get());

        const auto expired =
            anonsync::receive_one_sync_replica_file_delivery_over_tls_or_throw(
                receiver_service, pair.receiver_channel,
                std::chrono::steady_clock::now(),
                std::chrono::steady_clock::now() + std::chrono::seconds(2),
                "file TLS request-timeout exchange");
        require(
            expired.disposition ==
                    anonsync::SyncReplicaFileTlsReceiveDisposition::
                        RequestDeadlineExpired &&
                !expired.inbound.has_value() &&
                expired.request_prefix_bytes_received == 0U &&
                expired.request_frame_bytes == 0U &&
                expired.request_body_bytes_received == 0U &&
                !expired.receipt_write_started &&
                expired.receipt_prefix_bytes_written == 0U &&
                !expired.receipt_prefix_accepted,
            "request timeout crossed TLS or durable authority");
        require(receiver.snapshot_or_throw() == before_receiver &&
                    effect.snapshot_or_throw() == before_effect,
                "expired request budget mutated receiver evidence or effects");
        require_error(
            [&] {
                (void)anonsync::begin_sync_replica_tls_record_read_or_throw(
                    pair.receiver_channel, 64U,
                    "file TLS request-timeout reuse");
            },
            "poisoned",
            "expired one-shot request left the TLS conversation reusable");
    }

    // A complete but malformed application record is a terminal conversation
    // error: no file/evidence mutation and no opportunity to reinterpret a
    // following record as the missing request or receipt.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS receiver malformed request");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-malformed-request");
        auto clock = std::make_shared<MutableClockState>();
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-malformed-request";
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS malformed receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS malformed effects");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits, "file TLS malformed service");
        const auto before_receiver = receiver.snapshot_or_throw();
        const auto before_effect = effect.snapshot_or_throw();
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, "not-a-canonical-file-delivery-request", 1024U,
            "file TLS malformed request write");
        make_socket_nonblocking(pair.connection.server_fd.get());

        require_any_error(
            [&] {
                (void)anonsync::
                    receive_one_sync_replica_file_delivery_over_tls_or_throw(
                        receiver_service, pair.receiver_channel,
                        std::chrono::steady_clock::now() +
                            std::chrono::seconds(2),
                        std::chrono::steady_clock::now() +
                            std::chrono::seconds(2),
                        "file TLS malformed request exchange");
            },
            "malformed file request was accepted by receiver exchange");
        require(receiver.snapshot_or_throw() == before_receiver &&
                    effect.snapshot_or_throw() == before_effect,
                "malformed request changed receiver evidence or effects");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "reuse", 64U,
                    "file TLS malformed receiver reuse");
            },
            "poisoned",
            "malformed complete request left the application stream reusable");
        require_socket_has_no_pending_bytes(
            pair.connection.client_fd.get(),
            "malformed request emitted a receipt before rejection");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_reconciliation_tls_exchange(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& requester_actor,
    const anonsync::SyncReplicaActor& source_actor,
    const std::string& requester_pin,
    const std::string& source_pin) {
#ifdef __unix__
    struct SourceTruth final {
        std::uint64_t evidence_count = 0U;
        std::string operation_set_digest;
        std::string evidence_set_digest;
        std::string visible_state_digest;
    };
    struct SessionObservation final {
        anonsync::SyncReplicaReconciliationTlsPullResult pull;
        anonsync::SyncReplicaReconciliationTlsServeResult serve;
        SourceTruth source;
    };

    TempReconciliationWorkspace workspace(
        "anonsync-reconciliation-tls-exchange");
    const std::string folder = "folder-reconciliation-tls-exchange";
    const auto wire_limits = reconciliation_protocol_limits(1U);
    const auto payload_limits = reconciliation_payload_limits();

    anonsync::SyncSqliteDb requester_database =
        open_database(workspace.requester_db);
    anonsync::SyncReplicaSqliteOwner requester(
        requester_database.db, folder, requester_actor, owner_limits(),
        "TLS reconciliation requester");
    anonsync::SyncReplicaFilePayloadStore requester_payload_store(
        folder, workspace.requester_payloads,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits, "TLS reconciliation requester payload store");
    const anonsync::SyncReplicaSelectiveSyncPolicy requester_policy =
        anonsync::make_sync_replica_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"tree/beta.txt",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}},
            1U);
    anonsync::SyncReplicaReconciliationService requester_service(
        requester, requester_payload_store, wire_limits,
        "TLS reconciliation requester service", requester_policy);

    const auto run_session = [&]
        (bool initialize_source,
         std::uint64_t max_round_trips,
         std::optional<std::string> after_operation_id = std::nullopt,
         std::optional<std::string> source_evidence_set_digest =
             std::nullopt,
         bool dispatch_first_request = false) {
        TlsConnectionPair connection = make_tls_connection_pair(
            client_context, server_context);
        make_socket_nonblocking(connection.client_fd.get());
        make_socket_nonblocking(connection.server_fd.get());

        auto requester_channel =
            anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                connection.client.get(), {source_actor, source_pin},
                "TLS reconciliation requester channel");

        std::promise<void> source_ready_promise;
        std::future<void> source_ready = source_ready_promise.get_future();
        std::exception_ptr source_failure;
        SourceTruth source_truth;
        anonsync::SyncReplicaReconciliationTlsServeResult serve_result;
        std::thread source_thread([&] {
            bool ready_completed = false;
            try {
                auto source_channel =
                    anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                        connection.server.get(),
                        {requester_actor, requester_pin},
                        "TLS reconciliation source channel");
                anonsync::SyncSqliteDb source_database =
                    open_database(workspace.source_db);
                anonsync::SyncReplicaSqliteOwner source(
                    source_database.db, folder, source_actor, owner_limits(),
                    "TLS reconciliation source");
                anonsync::SyncReplicaFilePayloadStore source_payload_store(
                    folder, workspace.source_payloads,
                    initialize_source
                        ? anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                              CreateIfMissing
                        : anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                              ExistingOnly,
                    payload_limits, "TLS reconciliation source payload store");
                anonsync::SyncReplicaReconciliationService source_service(
                    source, source_payload_store, wire_limits,
                    "TLS reconciliation source service");

                if (initialize_source) {
                    const std::string alpha_bytes =
                        "TLS reconciliation alpha payload";
                    const std::string beta_bytes =
                        "TLS reconciliation beta payload";
                    const auto alpha =
                        source_payload_store.put_payload_or_throw(alpha_bytes);
                    const auto beta =
                        source_payload_store.put_payload_or_throw(beta_bytes);
                    (void)source.publish_local_file_or_throw(
                        "tree/alpha.txt", alpha.size_bytes,
                        alpha.content_sha256);
                    (void)source.publish_local_file_or_throw(
                        "tree/beta.txt", beta.size_bytes,
                        beta.content_sha256);
                    (void)source.publish_local_tombstone_or_throw(
                        "tree/obsolete.txt");
                }

                const auto snapshot = source.snapshot_or_throw();
                source_truth = {
                    static_cast<std::uint64_t>(
                        snapshot.durable.operations.size()),
                    snapshot.operation_set_digest,
                    snapshot.evidence_set_digest,
                    snapshot.visible_state_digest,
                };
                source_ready_promise.set_value();
                ready_completed = true;

                const auto deadline = std::chrono::steady_clock::now() +
                                      std::chrono::seconds(5);
                if (dispatch_first_request) {
                    anonsync::SyncReplicaFileDeliveryService file_service(
                        source, nullptr, file_service_limits(),
                        "TLS reconciliation dispatcher file service");
                    const auto dispatched = anonsync::
                        serve_one_sync_replica_peer_application_over_tls_or_throw(
                            file_service, source_service, source_channel,
                            {
                                deadline,
                                deadline,
                                {max_round_trips, deadline},
                            },
                            "TLS reconciliation production first-frame dispatch");
                    require(
                        dispatched.disposition == anonsync::
                                SyncReplicaPeerTlsServeDisposition::Reconciliation &&
                            dispatched.reconciliation.has_value() &&
                            !dispatched.file_delivery.has_value() &&
                            dispatched.first_request_prefix_bytes_received ==
                                anonsync::kSyncReplicaTlsRecordPrefixBytes &&
                            dispatched.first_request_frame_bytes > 0U &&
                            dispatched.first_request_body_bytes_received ==
                                dispatched.first_request_frame_bytes,
                        "TLS reconciliation production dispatcher did not select exactly one application owner");
                    serve_result = *dispatched.reconciliation;
                } else {
                    serve_result = anonsync::
                        serve_sync_replica_reconciliation_over_tls_or_throw(
                            source_service, source_channel,
                            {max_round_trips, deadline},
                            "TLS reconciliation source exchange");
                }
            } catch (...) {
                source_failure = std::current_exception();
                if (!ready_completed) {
                    try {
                        source_ready_promise.set_exception(source_failure);
                    } catch (...) {
                    }
                }
            }
        });

        anonsync::SyncReplicaReconciliationTlsPullResult pull_result;
        try {
            source_ready.get();
            anonsync::SyncReplicaReconciliationTlsPullOptions pull_options;
            pull_options.max_round_trips = max_round_trips;
            pull_options.max_source_resets = 2U;
            pull_options.after_operation_id =
                std::move(after_operation_id);
            pull_options.expected_source_evidence_set_digest =
                std::move(source_evidence_set_digest);
            pull_options.deadline = std::chrono::steady_clock::now() +
                                    std::chrono::seconds(5);
            pull_result = anonsync::
                pull_sync_replica_reconciliation_over_tls_or_throw(
                    requester_service, requester_channel,
                    std::move(pull_options),
                    "TLS reconciliation requester exchange");
            source_thread.join();
        } catch (...) {
            if (source_thread.joinable()) source_thread.join();
            throw;
        }
        if (source_failure) std::rethrow_exception(source_failure);
        return SessionObservation{
            std::move(pull_result), std::move(serve_result),
            std::move(source_truth)};
    };

    const SessionObservation first = run_session(true, 2U);
    require(
        first.pull.disposition ==
                anonsync::SyncReplicaReconciliationTlsPullDisposition::
                    RoundTripLimitReached &&
            first.pull.round_trips == 2U &&
            first.pull.pages_applied == 2U &&
            first.pull.source_resets == 0U &&
            first.pull.inserted_active + first.pull.inserted_pending +
                    first.pull.inserted_quarantined ==
                2U &&
            first.pull.duplicate_operations == 0U &&
            first.pull.metadata_only_file_operations <= 1U &&
            first.pull.inserted_payloads <= 1U &&
            first.pull.existing_payloads == 0U && first.pull.has_more &&
            first.pull.next_after_operation_id.has_value() &&
            !first.pull.source_evidence_set_digest.empty(),
        "bounded multi-record TLS reconciliation did not stop on an exact resumable cursor");
    require(
        first.serve.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::
                    RoundTripLimitReached &&
            first.serve.requests_received == 2U &&
            first.serve.responses_written == 2U &&
            first.serve.pages_served == 2U &&
            first.serve.source_changed_responses == 0U &&
            first.serve.payload_unavailable_responses == 0U &&
            first.serve.has_more,
        "TLS reconciliation source did not stop at the same bounded page frontier");
    require(
        first.pull.request_frame_bytes_written > 0U &&
            first.pull.response_frame_bytes_received > 0U &&
            first.serve.request_frame_bytes_received ==
                first.pull.request_frame_bytes_written &&
            first.serve.response_frame_bytes_written ==
                first.pull.response_frame_bytes_received &&
            first.serve.response_direct_source_frames ==
                first.serve.responses_written &&
            first.serve
                    .response_direct_source_frame_payload_page_bytes_at_reservation ==
                0U &&
            first.serve
                    .response_direct_source_frame_maximum_staging_bytes ==
                0U &&
            first.serve
                    .response_direct_source_frame_maximum_open_descriptors <=
                8U &&
            first.serve.response_frame_owned_handoffs ==
                first.serve.responses_written,
        "TLS reconciliation did not preserve exact record accounting and zero-copy direct source framing");

    const SessionObservation resumed = run_session(
        false, 8U, first.pull.next_after_operation_id,
        first.pull.source_evidence_set_digest, true);
    require(
        resumed.pull.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::Complete &&
            resumed.pull.round_trips == 1U &&
            resumed.pull.pages_applied == 1U &&
            resumed.pull.inserted_active + resumed.pull.inserted_pending +
                    resumed.pull.inserted_quarantined ==
                1U &&
            resumed.pull.duplicate_operations == 0U &&
            first.pull.metadata_only_file_operations +
                    resumed.pull.metadata_only_file_operations ==
                1U &&
            first.pull.inserted_payloads + resumed.pull.inserted_payloads ==
                1U &&
            !resumed.pull.has_more,
        "fresh TLS session did not resume the exact pinned source walk");
    require(
        resumed.serve.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::Complete &&
            resumed.serve.requests_received == 1U &&
            resumed.serve.responses_written == 1U &&
            resumed.serve.pages_served == 1U && !resumed.serve.has_more,
        "source did not complete the resumed one-page TLS conversation");

    const auto requester_after_resume = requester.snapshot_or_throw();
    require(
        first.source.evidence_count == 3U &&
            requester_after_resume.operation_set_digest ==
                first.source.operation_set_digest &&
            requester_after_resume.evidence_set_digest ==
                first.source.evidence_set_digest &&
            requester_after_resume.visible_state_digest ==
                first.source.visible_state_digest &&
            requester_after_resume.outbox.empty(),
        "resumed live TLS reconciliation did not converge exact share evidence without outbox state");
    const auto requester_payloads_after_first =
        requester_payload_store.snapshot_or_throw();
    require(
        requester_payloads_after_first.entry_count() == 1U &&
            !requester_payloads_after_first.payload_size_or_none(
                anonsync::sha256_hex(
                    "TLS reconciliation beta payload")).has_value(),
        "live TLS reconciliation downloaded a metadata-only source payload");

    const auto durable_before_repeat = requester.snapshot_or_throw();
    const std::string payload_digest_before_repeat =
        requester_payloads_after_first.snapshot_digest();
    const SessionObservation repeated = run_session(false, 8U);
    require(
        repeated.pull.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::Complete &&
            repeated.pull.round_trips == 3U &&
            repeated.pull.pages_applied == 3U &&
            repeated.pull.inserted_active == 0U &&
            repeated.pull.inserted_pending == 0U &&
            repeated.pull.inserted_quarantined == 0U &&
            repeated.pull.duplicate_operations == 3U &&
            repeated.pull.metadata_only_file_operations == 1U &&
            repeated.pull.inserted_payloads == 0U &&
            repeated.pull.existing_payloads == 1U,
        "fresh TLS session did not make repeated catch-up an idempotent no-op");
    require(
        repeated.serve.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::Complete &&
            repeated.serve.requests_received == 3U &&
            repeated.serve.responses_written == 3U &&
            repeated.serve.pages_served == 3U,
        "restarted source did not serve the same complete bounded evidence walk");
    require(
        requester.snapshot_or_throw() == durable_before_repeat &&
            requester_payload_store.snapshot_or_throw().snapshot_digest() ==
                payload_digest_before_repeat,
        "repeated TLS catch-up changed the requester durable or payload cutpoint");
#else
    (void)client_context;
    (void)server_context;
    (void)requester_actor;
    (void)source_actor;
    (void)requester_pin;
    (void)source_pin;
#endif
}


void test_reconciliation_tls_source_manifest_preparing(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& requester_actor,
    const anonsync::SyncReplicaActor& source_actor,
    const std::string& requester_pin,
    const std::string& source_pin) {
#ifdef __unix__
    TempReconciliationWorkspace workspace(
        "anonsync-reconciliation-tls-source-preparing");
    const std::string folder =
        "folder-reconciliation-tls-source-preparing";
    auto wire_limits = reconciliation_protocol_limits(1U);
    wire_limits.max_single_payload_bytes = 4U;
    wire_limits.max_payload_bytes_per_page = 8U;
    const auto payload_limits = reconciliation_payload_limits();
    const std::uint64_t projection_budget = 512U * 1024U;
    const std::string bytes(
        static_cast<std::size_t>(2U * projection_budget + 17U), 'p');

    anonsync::SyncSqliteDb requester_database =
        open_database(workspace.requester_db);
    anonsync::SyncReplicaSqliteOwner requester(
        requester_database.db, folder, requester_actor, owner_limits(),
        "TLS source-preparing requester");
    anonsync::SyncReplicaFilePayloadStore requester_payload_store(
        folder, workspace.requester_payloads,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits, "TLS source-preparing requester payload store");
    anonsync::SyncReplicaReconciliationService requester_service(
        requester, requester_payload_store, wire_limits,
        "TLS source-preparing requester service");

    TlsConnectionPair connection = make_tls_connection_pair(
        client_context, server_context);
    make_socket_nonblocking(connection.client_fd.get());
    make_socket_nonblocking(connection.server_fd.get());
    auto requester_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.client.get(), {source_actor, source_pin},
            "TLS source-preparing requester channel");

    std::promise<void> source_ready_promise;
    std::future<void> source_ready = source_ready_promise.get_future();
    std::exception_ptr source_failure;
    anonsync::SyncReplicaReconciliationTlsServeResult serve_result;
    std::optional<anonsync::SyncReplicaOperation> source_operation;
    std::thread source_thread([&] {
        bool ready_completed = false;
        try {
            auto source_channel =
                anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                    connection.server.get(),
                    {requester_actor, requester_pin},
                    "TLS source-preparing source channel");
            anonsync::SyncSqliteDb source_database =
                open_database(workspace.source_db);
            anonsync::SyncReplicaSqliteOwner source(
                source_database.db, folder, source_actor, owner_limits(),
                "TLS source-preparing source");
            anonsync::SyncReplicaFilePayloadStore source_payload_store(
                folder, workspace.source_payloads,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                    CreateIfMissing,
                payload_limits,
                "TLS source-preparing source payload store");
            anonsync::SyncReplicaReconciliationService source_service(
                source, source_payload_store, wire_limits,
                "TLS source-preparing source service",
                anonsync::sync_replica_default_selective_sync_policy(),
                anonsync::
                    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
                anonsync::
                    kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
                projection_budget);
            const auto payload =
                source_payload_store.put_payload_or_throw(bytes);
            source_operation = source.publish_local_file_or_throw(
                "large/preparing.bin", payload.size_bytes,
                payload.content_sha256);
            source_ready_promise.set_value();
            ready_completed = true;
            serve_result = anonsync::
                serve_sync_replica_reconciliation_over_tls_or_throw(
                    source_service, source_channel,
                    {3U, std::chrono::steady_clock::now() +
                             std::chrono::seconds(5)},
                    "TLS source-preparing source exchange");
        } catch (...) {
            source_failure = std::current_exception();
            if (!ready_completed) {
                try {
                    source_ready_promise.set_exception(source_failure);
                } catch (...) {
                }
            }
        }
    });

    anonsync::SyncReplicaReconciliationTlsPullResult pull_result;
    try {
        source_ready.get();
        anonsync::SyncReplicaReconciliationTlsPullOptions options;
        options.max_round_trips = 3U;
        options.max_source_resets = 1U;
        options.deadline = std::chrono::steady_clock::now() +
                           std::chrono::seconds(5);
        pull_result = anonsync::
            pull_sync_replica_reconciliation_over_tls_or_throw(
                requester_service, requester_channel, std::move(options),
                "TLS source-preparing requester exchange");
        source_thread.join();
    } catch (...) {
        if (source_thread.joinable()) source_thread.join();
        throw;
    }
    if (source_failure) std::rethrow_exception(source_failure);

    require(
        source_operation.has_value() &&
            pull_result.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::
                    RoundTripLimitReached &&
            pull_result.round_trips == 3U &&
            pull_result.source_payload_preparing_responses == 2U &&
            pull_result.pages_applied == 0U &&
            pull_result.inserted_active == 0U &&
            pull_result.staged_payload_ranges == 2U &&
            pull_result.staged_payload_bytes == 8U &&
            pull_result.has_more &&
            !pull_result.next_after_operation_id.has_value() &&
            pull_result.payload_continuation.has_value() &&
            pull_result.payload_continuation->operation_id ==
                source_operation->operation_id &&
            pull_result.payload_continuation->next_offset_bytes == 8U,
        "TLS pull did not collapse bounded source preparation into later wire progress");
    require(
        serve_result.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::
                    RoundTripLimitReached &&
            serve_result.requests_received == 3U &&
            serve_result.responses_written == 3U &&
            serve_result.pages_served == 1U &&
            serve_result.source_payload_preparing_responses == 2U &&
            serve_result.content_defined_manifest_projection_steps == 3U &&
            serve_result.content_defined_manifest_projection_restarts == 0U &&
            serve_result.content_defined_manifest_hashed_bytes ==
                bytes.size() &&
            serve_result.content_defined_manifest_scans == 1U &&
            serve_result.content_defined_chunk_index_builds == 1U &&
            serve_result.content_defined_chunk_index_lookups == 1U &&
            serve_result.ranged_payload_windows == 1U &&
            serve_result.ranged_payload_ranges == 2U &&
            serve_result.ranged_payload_bytes == 8U &&
            !serve_result.blocked_operation_id.has_value(),
        "TLS serve did not collapse two bounded source-manifest pulses before one ranged response");
    require(
        requester.snapshot_or_throw().durable.operations.empty() &&
            requester_payload_store.snapshot_or_throw().entry_count() == 0U &&
            requester_payload_store.snapshot_or_throw()
                    .transient_entry_count() == 1U,
        "TLS collapsed source preparation did not stop at one durable ranged prefix");
#else
    (void)client_context;
    (void)server_context;
    (void)requester_actor;
    (void)source_actor;
    (void)requester_pin;
    (void)source_pin;
#endif
}

void test_reconciliation_tls_range_resume(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& requester_actor,
    const anonsync::SyncReplicaActor& source_actor,
    const std::string& requester_pin,
    const std::string& source_pin) {
#ifdef __unix__
    struct SessionObservation final {
        anonsync::SyncReplicaReconciliationTlsPullResult pull;
        anonsync::SyncReplicaReconciliationTlsServeResult serve;
    };

    TempReconciliationWorkspace workspace(
        "anonsync-reconciliation-tls-range-resume");
    const std::string folder = "folder-reconciliation-tls-range-resume";
    auto wire_limits = reconciliation_protocol_limits(1U);
    wire_limits.max_single_payload_bytes = 4U;
    const auto payload_limits = reconciliation_payload_limits();
    // Carry two contiguous ranges in the first authenticated response. This
    // proves that grouped service framing survives encode, TLS transport,
    // decode, durable staging, process-level cursor loss, and exact replay.
    wire_limits.max_payload_bytes_per_page = 8U;
    const std::string bytes = "abcdefghij";

    anonsync::SyncSqliteDb requester_database =
        open_database(workspace.requester_db);
    anonsync::SyncReplicaSqliteOwner requester(
        requester_database.db, folder, requester_actor, owner_limits(),
        "TLS ranged reconciliation requester");
    anonsync::SyncReplicaFilePayloadStore requester_payload_store(
        folder, workspace.requester_payloads,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits, "TLS ranged reconciliation requester payload store");
    anonsync::SyncReplicaReconciliationService requester_service(
        requester, requester_payload_store, wire_limits,
        "TLS ranged reconciliation requester service");

    std::optional<anonsync::SyncReplicaOperation> source_operation;
    const auto run_session = [&]
        (bool initialize_source,
         anonsync::SyncReplicaReconciliationTlsPullOptions pull_options) {
        const std::uint64_t max_round_trips = pull_options.max_round_trips;
        TlsConnectionPair connection = make_tls_connection_pair(
            client_context, server_context);
        make_socket_nonblocking(connection.client_fd.get());
        make_socket_nonblocking(connection.server_fd.get());
        auto requester_channel =
            anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                connection.client.get(), {source_actor, source_pin},
                "TLS ranged reconciliation requester channel");

        std::promise<void> source_ready_promise;
        std::future<void> source_ready = source_ready_promise.get_future();
        std::exception_ptr source_failure;
        anonsync::SyncReplicaReconciliationTlsServeResult serve_result;
        std::thread source_thread([&] {
            bool ready_completed = false;
            try {
                auto source_channel =
                    anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                        connection.server.get(),
                        {requester_actor, requester_pin},
                        "TLS ranged reconciliation source channel");
                anonsync::SyncSqliteDb source_database =
                    open_database(workspace.source_db);
                anonsync::SyncReplicaSqliteOwner source(
                    source_database.db, folder, source_actor, owner_limits(),
                    "TLS ranged reconciliation source");
                anonsync::SyncReplicaFilePayloadStore source_payload_store(
                    folder, workspace.source_payloads,
                    initialize_source
                        ? anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                              CreateIfMissing
                        : anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                              ExistingOnly,
                    payload_limits,
                    "TLS ranged reconciliation source payload store");
                anonsync::SyncReplicaReconciliationService source_service(
                    source, source_payload_store, wire_limits,
                    "TLS ranged reconciliation source service");
                if (initialize_source) {
                    const auto payload =
                        source_payload_store.put_payload_or_throw(bytes);
                    source_operation = source.publish_local_file_or_throw(
                        "large/ranged.bin", payload.size_bytes,
                        payload.content_sha256);
                }
                source_ready_promise.set_value();
                ready_completed = true;
                const auto deadline = std::chrono::steady_clock::now() +
                                      std::chrono::seconds(5);
                serve_result = anonsync::
                    serve_sync_replica_reconciliation_over_tls_or_throw(
                        source_service, source_channel,
                        {max_round_trips, deadline},
                        "TLS ranged reconciliation source exchange");
            } catch (...) {
                source_failure = std::current_exception();
                if (!ready_completed) {
                    try {
                        source_ready_promise.set_exception(source_failure);
                    } catch (...) {
                    }
                }
            }
        });

        anonsync::SyncReplicaReconciliationTlsPullResult pull_result;
        try {
            source_ready.get();
            pull_options.deadline = std::chrono::steady_clock::now() +
                                    std::chrono::seconds(5);
            pull_result = anonsync::
                pull_sync_replica_reconciliation_over_tls_or_throw(
                    requester_service, requester_channel,
                    std::move(pull_options),
                    "TLS ranged reconciliation requester exchange");
            source_thread.join();
        } catch (...) {
            if (source_thread.joinable()) source_thread.join();
            throw;
        }
        if (source_failure) std::rethrow_exception(source_failure);
        return SessionObservation{
            std::move(pull_result), std::move(serve_result)};
    };

    anonsync::SyncReplicaReconciliationTlsPullOptions first_options;
    first_options.max_round_trips = 1U;
    first_options.max_source_resets = 1U;
    const SessionObservation first =
        run_session(true, std::move(first_options));
    require(
        first.pull.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::
                    RoundTripLimitReached &&
            first.pull.round_trips == 1U && first.pull.pages_applied == 0U &&
            first.pull.inserted_active == 0U &&
            first.pull.duplicate_operations == 0U &&
            first.pull.metadata_only_file_operations == 0U &&
            first.pull.staged_payload_ranges == 2U &&
            first.pull.staged_payload_bytes == 8U &&
            first.pull.reused_payload_chunks == 0U &&
            first.pull.reused_payload_ranges == 0U &&
            first.pull.reused_payload_bytes == 0U &&
            first.pull.delta_predecessor_manifest_scans == 0U &&
            first.pull.delta_predecessor_manifest_reuses == 0U &&
            first.pull.delta_predecessor_manifest_hashed_bytes == 0U &&
            first.pull.target_content_defined_manifest_publications == 1U &&
            first.pull.target_content_defined_manifest_reuses == 1U &&
            first.pull.delta_predecessor_index_builds == 0U &&
            first.pull.delta_predecessor_index_reuses == 0U &&
            first.pull.has_more &&
            !first.pull.next_after_operation_id.has_value() &&
            first.pull.payload_continuation.has_value() &&
            first.pull.payload_continuation->next_offset_bytes == 8U &&
            !first.pull.source_evidence_set_digest.empty(),
        "bounded TLS ranged pull did not retain its exact first prefix");
    require(
        requester.snapshot_or_throw().durable.operations.empty(),
        "bounded TLS ranged pull admitted file evidence before payload completion");
    require(
        first.serve.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::
                    RoundTripLimitReached &&
            first.serve.requests_received == 1U &&
            first.serve.responses_written == 1U &&
            first.serve.payload_targeted_access_births == 1U &&
            first.serve.payload_targeted_open_attempts == 1U &&
            first.serve.payload_targeted_opens == 1U &&
            first.serve.content_defined_manifest_scans == 1U &&
            first.serve.content_defined_manifest_reuses == 0U &&
            first.serve.content_defined_manifest_hashed_bytes == bytes.size() &&
            first.serve.content_defined_manifest_publications == 1U &&
            first.serve.content_defined_manifest_references == 1U &&
            first.serve.content_defined_chunk_index_builds == 1U &&
            first.serve.content_defined_chunk_index_reuses == 0U &&
            first.serve.content_defined_chunk_index_lookups == 1U &&
            first.serve.ranged_payload_windows == 1U &&
            first.serve.ranged_payload_ranges == 2U &&
            first.serve.ranged_payload_bytes == 8U &&
            first.serve.response_direct_source_frames == 1U &&
            first.serve.response_direct_source_frame_payload_bytes == 8U &&
            first.serve
                    .response_direct_source_frame_maximum_staging_bytes ==
                0U &&
            first.serve
                    .response_direct_source_frame_payload_page_bytes_at_reservation ==
                0U &&
            first.serve
                    .response_direct_source_frame_maximum_open_descriptors ==
                1U &&
            first.serve.payload_continuation.has_value() &&
            first.serve.payload_continuation->next_offset_bytes == 8U,
        "bounded TLS source did not carry two contiguous ranges in one authenticated round trip");

    // Simulate process-level loss of every in-memory cursor. Replaying range
    // zero must discover the longer durable prefix and return offset eight;
    // it must not consume another four bytes of transient capacity.
    anonsync::SyncReplicaReconciliationTlsPullOptions replay_options;
    replay_options.max_round_trips = 1U;
    replay_options.max_source_resets = 1U;
    const SessionObservation replayed =
        run_session(false, std::move(replay_options));
    require(
        replayed.pull.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::
                    RoundTripLimitReached &&
            replayed.pull.round_trips == 1U &&
            replayed.pull.inserted_active == 0U &&
            replayed.pull.duplicate_operations == 0U &&
            replayed.pull.staged_payload_ranges == 1U &&
            replayed.pull.staged_payload_bytes == 0U &&
            replayed.pull.target_content_defined_manifest_publications == 1U &&
            replayed.pull.target_content_defined_manifest_reuses == 1U &&
            replayed.pull.payload_continuation.has_value() &&
            replayed.pull.payload_continuation->next_offset_bytes == 8U &&
            !replayed.pull.next_after_operation_id.has_value(),
        "cursorless TLS restart did not recover the durable ranged prefix");
    require(
        replayed.serve.content_defined_manifest_publications == 1U &&
            replayed.serve.content_defined_manifest_references == 1U &&
            replayed.serve.content_defined_manifest_scans == 0U &&
            replayed.serve.content_defined_manifest_reuses == 1U &&
            replayed.serve.content_defined_manifest_projection_steps == 0U &&
            replayed.serve.content_defined_manifest_hashed_bytes == 0U &&
            replayed.serve.content_defined_chunk_index_builds == 0U &&
            replayed.serve.content_defined_chunk_index_reuses == 1U &&
            replayed.serve.content_defined_chunk_index_lookups == 1U &&
            replayed.serve.ranged_payload_windows == 1U &&
            replayed.serve.ranged_payload_ranges == 2U &&
            replayed.serve.ranged_payload_bytes == 8U,
        "cache-cold TLS replay did not restore the complete source manifest without hashing");
    require(
        requester.snapshot_or_throw().durable.operations.empty(),
        "cursorless TLS restart admitted incomplete file evidence");

    anonsync::SyncReplicaReconciliationTlsPullOptions final_options;
    // Generation 8 keeps the final byte-bearing response nonterminal so the
    // source cursor cannot advance before receiver-local terminal verification.
    // This small fixture completes verification in that first turn; a second
    // payload-cold request then proves the source page is exhausted.
    final_options.max_round_trips = 2U;
    final_options.max_source_resets = 1U;
    final_options.after_operation_id =
        replayed.pull.next_after_operation_id;
    final_options.expected_source_evidence_set_digest =
        replayed.pull.source_evidence_set_digest;
    final_options.payload_continuation =
        replayed.pull.payload_continuation;
    const SessionObservation completed =
        run_session(false, std::move(final_options));
    require(
        completed.pull.disposition == anonsync::
                SyncReplicaReconciliationTlsPullDisposition::Complete &&
            completed.pull.round_trips == 2U &&
            completed.pull.pages_applied == 2U &&
            completed.pull.inserted_active == 1U &&
            completed.pull.duplicate_operations == 0U &&
            completed.pull.inserted_payloads == 1U &&
            completed.pull.staged_payload_ranges == 1U &&
            completed.pull.staged_payload_bytes == 2U &&
            completed.pull.target_content_defined_manifest_publications == 0U &&
            completed.pull.target_content_defined_manifest_reuses == 1U &&
            !completed.pull.has_more &&
            !completed.pull.payload_continuation.has_value() &&
            source_operation.has_value() &&
            completed.pull.next_after_operation_id ==
                std::optional<std::string>(
                    source_operation->operation_id),
        "generation-9 TLS final range and payload-cold source completion did not preserve terminal admission");
    require(
        completed.serve.disposition == anonsync::
                SyncReplicaReconciliationTlsServeDisposition::Complete &&
            completed.serve.requests_received == 2U &&
            completed.serve.responses_written == 2U &&
            completed.serve.content_defined_manifest_publications == 0U &&
            completed.serve.content_defined_manifest_references == 1U &&
            completed.serve.content_defined_manifest_scans == 0U &&
            completed.serve.content_defined_manifest_reuses == 1U &&
            completed.serve.content_defined_manifest_projection_steps == 0U &&
            completed.serve.content_defined_manifest_hashed_bytes == 0U &&
            completed.serve.content_defined_chunk_index_builds == 0U &&
            completed.serve.content_defined_chunk_index_reuses == 1U &&
            completed.serve.content_defined_chunk_index_lookups == 1U &&
            completed.serve.ranged_payload_windows == 1U &&
            completed.serve.ranged_payload_ranges == 1U &&
            completed.serve.ranged_payload_bytes == 2U &&
            !completed.serve.payload_continuation.has_value(),
        "restart-warm TLS source did not complete one exact indexed final range followed by a payload-cold terminal page");

    const auto requester_payloads =
        requester_payload_store.snapshot_or_throw();
    require(
        requester_payloads.entry_count() == 1U &&
            requester_payloads.transient_entry_count() == 0U &&
            requester_payloads.transient_bytes() == 0U &&
            requester_payloads.copy_payload_for_operation_or_throw(
                *source_operation,
                "TLS ranged reconciliation completed payload") == bytes,
        "TLS ranged reconciliation did not publish exact whole bytes or clean staging");
    const auto requester_snapshot = requester.snapshot_or_throw();
    require(
        requester_snapshot.durable.operations.size() == 1U &&
            requester_snapshot.durable.operations.front() ==
                *source_operation,
        "TLS ranged reconciliation did not retain the exact source operation");
#else
    (void)client_context;
    (void)server_context;
    (void)requester_actor;
    (void)source_actor;
    (void)requester_pin;
    (void)source_pin;
#endif
}

void test_file_tls_dispatch_frontier(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    const std::vector<std::string> destination{receiver_actor.device_id};
    const auto limits = file_service_limits();

    // A frame prepared under attempt 1 must not leak after an exact release and
    // attempt-2 replacement. The stale guard decision happens before TLS I/O.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS stale-frame frontier");
        TempDatabasePath database_path("anonsync-file-tls-stale-frame");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 500U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-stale", sender_actor,
            owner_limits(), "file TLS stale-frame owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS stale-frame service");
        const std::string payload = "stale-frame-payload";
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/stale.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto first = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "first-worker", 30U,
            payload_snapshot("folder-file-tls-stale", payload));
        require(first.has_value(),
                "file TLS service did not prepare attempt 1");
        clock->epoch = 501U;
        require(
            owner.release_outbox_for_retry_or_throw(
                receiver_actor.device_id, operation.operation_id,
                first->claim.intent.lease.claim_id, 1U) ==
                anonsync::SyncReplicaSqliteOutboxReceiptResult::Applied,
            "file TLS fixture could not release attempt 1");
        require_error(
            [&] {
                (void)anonsync::
                    dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
                    service, pair.sender_channel, *first,
                    "file TLS stale attempt dispatch");
            },
            "lost exact claim identity",
            "stale file frame reached the TLS first-prefix frontier");
        require_socket_has_no_pending_bytes(
            pair.connection.server_fd.get(),
            "stale file frame emitted ciphertext before claim attestation");

        clock->epoch = 502U;
        make_socket_nonblocking(pair.connection.client_fd.get());
        auto second =
            anonsync::claim_and_begin_next_file_delivery_over_tls_or_throw(
                service, pair.sender_channel, "second-worker", 30U,
                payload_snapshot("folder-file-tls-stale", payload),
                "file TLS fresh attempt dispatch");
        require(second.has_value() &&
                    second->outbound_or_throw().claim.intent.lease.claim_id !=
                        first->claim.intent.lease.claim_id &&
                    second->outbound_or_throw().claim.intent.lease.dispatch_attempts ==
                        first->claim.intent.lease.dispatch_attempts + 1U &&
                    second->active(),
                "file TLS retry did not mint one fresh resumable attempt");
        auto second_dispatch = std::move(*second);
        require(!second->active() && second_dispatch.active(),
                "claimed dispatch did not transfer exclusive write ownership");
        require_error(
            [&] { (void)second->outbound_or_throw(); },
            "empty or moved-from",
            "claimed dispatch duplicated its move-only attempt evidence");
        second_dispatch.finish_or_throw();
        const std::string received =
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, limits.max_request_frame_bytes,
                "file TLS fresh attempt read");
        require(received == second_dispatch.outbound_or_throw().request_frame,
                "file TLS dispatch did not preserve the fresh canonical frame");
        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().lease.claim_id ==
                        second_dispatch.outbound_or_throw()
                            .claim.intent.lease.claim_id,
                "successful file TLS send released an attempt before receipt");
    }

    // The SQLite/TLS composition refuses an unbounded blocking BIO before
    // writing a prefix. The exact claim is released and the untouched channel
    // remains usable by the generic caller-managed transport API.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS blocking policy");
        TempDatabasePath database_path("anonsync-file-tls-blocking-policy");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 550U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-blocking", sender_actor,
            owner_limits(), "file TLS blocking owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS blocking service");
        const std::string payload = "blocking-policy-payload";
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/blocking.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "blocking-worker", 30U,
            payload_snapshot("folder-file-tls-blocking", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare blocking-policy fixture");
        require_error(
            [&] {
                (void)anonsync::
                    dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
                    service, pair.sender_channel, *outbound,
                    "file TLS blocking policy dispatch");
            },
            "is not nonblocking",
            "file TLS dispatch held writer authority over a blocking socket");
        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().operation_id ==
                        operation.operation_id &&
                    snapshot.outbox.front().lease.claim_id.empty() &&
                    snapshot.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "blocking-policy rejection did not exact-release the attempt");
        require_socket_has_no_pending_bytes(
            pair.connection.server_fd.get(),
            "blocking-policy rejection wrote TLS bytes before readiness proof");
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, "caller-managed", 1024U,
            "file TLS blocking generic reuse");
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, 1024U,
                "file TLS blocking generic reuse read") == "caller-managed",
            "blocking-policy rejection poisoned an untouched TLS channel");
    }

    // Caller-tampered local bytes fail before stream mutation and release the
    // exact attempt through the owner-clock retry policy.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS preflight release");
        TempDatabasePath database_path("anonsync-file-tls-preflight");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 600U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-preflight", sender_actor,
            owner_limits(), "file TLS preflight owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS preflight service");
        const std::string payload = "preflight-payload";
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/preflight.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "preflight-worker", 30U,
            payload_snapshot("folder-file-tls-preflight", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare preflight fixture");
        outbound->request_frame.push_back('x');
        require_error(
            [&] {
                (void)anonsync::
                    dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
                    service, pair.sender_channel, *outbound,
                    "file TLS tampered preflight");
            },
            "not the canonical encoding",
            "file TLS dispatch accepted caller-tampered canonical bytes");
        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().lease.claim_id.empty() &&
                    snapshot.outbox.front().lease.retry_released_at_epoch ==
                        clock->epoch &&
                    snapshot.outbox.front().lease.retry_not_before_epoch ==
                        clock->epoch +
                            limits.retry.pre_dispatch_failure_delay_seconds &&
                    snapshot.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "file TLS preflight failure did not persist exact retry provenance");
        require_socket_has_no_pending_bytes(
            pair.connection.server_fd.get(),
            "tampered local frame mutated TLS before canonical preflight");
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.sender_channel, "still-live", 1024U,
            "file TLS preflight channel reuse");
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, 1024U,
                "file TLS preflight channel reuse read") == "still-live",
            "local preflight rejection poisoned an untouched TLS stream");
        (void)operation;
    }

    // A socket failure before the complete prefix is accepted poisons only the
    // channel and returns the exact attempt to a durable retry schedule.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS prefix failure");
        TempDatabasePath database_path("anonsync-file-tls-prefix-failure");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 700U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-prefix-failure", sender_actor,
            owner_limits(), "file TLS prefix-failure owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS prefix-failure service");
        const std::string payload = "prefix-failure-payload";
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/prefix-failure.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "prefix-worker", 30U,
            payload_snapshot("folder-file-tls-prefix-failure", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare prefix-failure fixture");
        make_socket_nonblocking(pair.connection.client_fd.get());
        if (::shutdown(pair.connection.client_fd.get(), SHUT_RDWR) != 0) {
            fail("file TLS test could not shut down sender socket");
        }
        require_any_error(
            [&] {
                (void)anonsync::
                    dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
                    service, pair.sender_channel, *outbound,
                    "file TLS prefix failure dispatch");
            },
            "file TLS dispatch ignored a failed prefix write");
        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().operation_id ==
                        operation.operation_id &&
                    snapshot.outbox.front().lease.claim_id.empty() &&
                    snapshot.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::Exact,
                "pre-prefix TLS failure left the exact attempt live or unproven");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "file TLS failed-prefix reuse");
            },
            "poisoned",
            "failed prefix left the TLS stream reusable");
    }

    // The production composition seam must retain ordinary nonblocking WANT
    // after the guarded prefix cutpoint rather than collapsing it into a
    // poisoned stream. One exact move-only dispatch crosses timeout, resumes
    // against a live reader, reaches durable receiver publication, returns an
    // authenticated terminal effect receipt, and only then settles the sender.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS resumable effect terminal");
        TempFileDeliveryWorkspace workspace(
            "anonsync-file-tls-resumable-terminal");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 725U;
        anonsync::SyncSqliteDb sender_database =
            open_database(workspace.sender_db);
        anonsync::SyncSqliteDb receiver_database =
            open_database(workspace.receiver_db);
        anonsync::SyncSqliteDb effect_database =
            open_database(workspace.effect_db);
        const std::string folder = "folder-file-tls-resumable-terminal";
        anonsync::SyncReplicaSqliteOwner sender(
            sender_database.db, folder, sender_actor, owner_limits(),
            "file TLS resumable sender", make_clock(clock));
        anonsync::SyncReplicaSqliteOwner receiver(
            receiver_database.db, folder, receiver_actor, owner_limits(),
            "file TLS resumable receiver", make_clock(clock));
        anonsync::SyncReplicaFileEffectSqliteOwner effect(
            effect_database.db, folder, workspace.files,
            file_effect_limits(), "file TLS resumable effects");
        anonsync::SyncReplicaFileDeliveryService sender_service(
            sender, nullptr, limits, "file TLS resumable sender service");
        anonsync::SyncReplicaFileDeliveryService receiver_service(
            receiver, &effect, limits,
            "file TLS resumable receiver service");

        const std::string payload(limits.max_payload_bytes, 'r');
        const auto operation = sender.create_local_file_or_throw(
            "resumable-terminal.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto pending_dispatch =
            anonsync::claim_and_begin_next_file_delivery_over_tls_or_throw(
                sender_service, pair.sender_channel,
                "resumable-terminal-worker", 30U,
                payload_snapshot(folder, payload),
                "file TLS resumable dispatch");
        require(pending_dispatch.has_value(),
                "file TLS service did not begin resumable fixture");
        auto dispatch = std::move(*pending_dispatch);
        pending_dispatch.reset();
        const std::string claim_id =
            dispatch.outbound_or_throw().claim.intent.lease.claim_id;
        const std::string request_digest =
            dispatch.outbound_or_throw().request_digest;
        require(dispatch.active() && !dispatch.complete() &&
                    dispatch.frame_bytes() ==
                        dispatch.outbound_or_throw().request_frame.size() &&
                    dispatch.body_bytes_written() == 0U &&
                    dispatch.outbound_or_throw().request.evidence_request.operation ==
                        operation &&
                    dispatch.outbound_or_throw().request.payload == payload,
                "resumable file dispatch did not retain its exact frozen attempt");
        require_error(
            [&] {
                (void)dispatch.poll_and_advance_or_throw(
                    std::chrono::steady_clock::now(),
                    "file TLS pre-WANT composite poll");
            },
            "no pending readiness request",
            "file dispatch poll accepted a continuation before WANT");
        require(dispatch.active() && dispatch.body_bytes_written() == 0U &&
                    dispatch.outbound_or_throw().request_digest ==
                        request_digest &&
                    dispatch.outbound_or_throw().claim.intent.lease.claim_id ==
                        claim_id,
                "pre-WANT composite poll rejection consumed dispatch authority");

        anonsync::SyncReplicaTlsRecordWriteProgress write_progress{};
        bool reached_want = false;
        for (std::size_t iteration = 0U; iteration < 4096U; ++iteration) {
            write_progress = dispatch.advance_or_throw();
            if (is_tls_write_want(write_progress)) {
                reached_want = true;
                break;
            }
            if (write_progress ==
                anonsync::SyncReplicaTlsRecordWriteProgress::Complete) {
                fail("resumable file dispatch completed before backpressure");
            }
            require(
                write_progress ==
                    anonsync::SyncReplicaTlsRecordWriteProgress::Progress,
                "resumable file dispatch reached unknown write progress");
        }
        require(reached_want,
                "resumable file dispatch never reached transport backpressure");
        const auto exact_target = dispatch.pending_readiness_or_throw();
        const std::uint64_t exact_cutpoint = dispatch.body_bytes_written();

        auto moved_dispatch = std::move(dispatch);
        require(!dispatch.active() && !dispatch.complete() &&
                    dispatch.frame_bytes() == 0U &&
                    dispatch.body_bytes_written() == 0U,
                "moved-from file dispatch retained transport authority");
        require_error(
            [&] { (void)dispatch.outbound_or_throw(); },
            "empty or moved-from",
            "moved-from file dispatch retained frozen attempt authority");
        require(moved_dispatch.active() &&
                    moved_dispatch.body_bytes_written() == exact_cutpoint &&
                    moved_dispatch.pending_readiness_or_throw() == exact_target &&
                    moved_dispatch.outbound_or_throw().request_digest ==
                        request_digest &&
                    moved_dispatch.outbound_or_throw().claim.intent.lease.claim_id ==
                        claim_id,
                "moving file dispatch changed its WANT retry or exact attempt");

        const auto before_timeout = sender.snapshot_or_throw();
        require(
            moved_dispatch.poll_and_advance_or_throw(
                std::chrono::steady_clock::now(),
                "file TLS expired composite poll") ==
                anonsync::SyncReplicaTlsRecordWritePollProgress::
                    DeadlineExpired,
            "expired composite poll did not preserve policy timeout");
        require(moved_dispatch.active() &&
                    moved_dispatch.body_bytes_written() == exact_cutpoint &&
                    moved_dispatch.pending_readiness_or_throw() == exact_target &&
                    moved_dispatch.outbound_or_throw().request_digest ==
                        request_digest &&
                    moved_dispatch.outbound_or_throw().claim.intent.lease.claim_id ==
                        claim_id &&
                    sender.snapshot_or_throw() == before_timeout,
                "expired composite poll changed TLS or durable attempt authority");

        const FileTlsDispatchTransferResult transfer =
            finish_file_tls_dispatch_with_nonblocking_reader(
                moved_dispatch, pair.receiver_channel,
                limits.max_request_frame_bytes, true,
                "file TLS resumable cooperative transfer");
        require(moved_dispatch.complete() && !moved_dispatch.active() &&
                    moved_dispatch.body_bytes_written() ==
                        moved_dispatch.frame_bytes() &&
                    moved_dispatch.outbound_or_throw().request_digest ==
                        request_digest &&
                    moved_dispatch.outbound_or_throw().claim.intent.lease.claim_id ==
                        claim_id,
                "completed file dispatch lost terminal cutpoint or attempt evidence");
        require(
            transfer.frame == moved_dispatch.outbound_or_throw().request_frame,
                "resumable file dispatch changed canonical request bytes");
        require(transfer.write_poll_operations > 0U &&
                    transfer.max_write_step <=
                        anonsync::kSyncReplicaTlsRecordWriteStepBytes,
                "resumable file dispatch hid or skipped bounded poll progress");
        const auto sent_snapshot = sender.snapshot_or_throw();
        require(sent_snapshot.outbox.size() == 1U &&
                    sent_snapshot.outbox.front().lease.claim_id ==
                        claim_id,
                "local TLS completion settled or released the durable attempt");

        const auto inbound = receiver_service.receive_request_or_throw(
            pair.receiver_channel.delivery_authority(), transfer.frame);
        require(
            inbound.stage_result ==
                    anonsync::SyncReplicaFileEffectStageResult::Inserted &&
                inbound.evidence_delivery.has_value() &&
                inbound.evidence_delivery->admission ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                inbound.materialize_result ==
                    anonsync::SyncReplicaFileEffectMaterializeResult::Published &&
                inbound.receipt.disposition ==
                    anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published,
            "resumable TLS request did not reach durable terminal publication");
        require(
            read_binary_file(
                workspace.files / "resumable-terminal.bin") ==
                payload,
            "terminal effect receipt did not correspond to exact visible bytes");
        const auto effect_snapshot = effect.snapshot_or_throw();
        require(effect_snapshot.effects.size() == 1U &&
                    effect_snapshot.effects.front().state ==
                        anonsync::SyncReplicaFileEffectState::Published &&
                    inbound.receipt.receiver_effect_cutpoint_digest ==
                        effect_snapshot.cutpoint_digest,
                "terminal receipt did not bind the published effect cutpoint");

        make_socket_blocking(pair.connection.client_fd.get());
        make_socket_blocking(pair.connection.server_fd.get());
        anonsync::write_sync_replica_tls_record_or_throw(
            pair.receiver_channel, inbound.receipt_frame,
            limits.max_receipt_frame_bytes,
            "file TLS resumable terminal receipt write");
        const std::string receipt_frame =
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.sender_channel, limits.max_receipt_frame_bytes,
                "file TLS resumable terminal receipt read");
        require(receipt_frame == inbound.receipt_frame,
                "terminal receipt changed across authenticated TLS framing");
        clock->epoch = 726U;
        require(
            sender_service.apply_receipt_or_throw(
                pair.sender_channel.delivery_authority(),
                moved_dispatch.outbound_or_throw().request, receipt_frame) ==
                anonsync::SyncReplicaFileDeliveryReceiptApplyResult::
                    EffectSettled,
            "terminal effect receipt did not settle the exact sender attempt");
        const auto settled_sender = sender.snapshot_or_throw();
        const auto published_receiver = receiver.snapshot_or_throw();
        require(settled_sender.outbox.empty() &&
                    settled_sender.operation_set_digest ==
                        published_receiver.operation_set_digest &&
                    settled_sender.evidence_set_digest ==
                        published_receiver.evidence_set_digest &&
                    settled_sender.visible_state_digest ==
                        published_receiver.visible_state_digest,
                "resumable TLS effect delivery did not converge canonical evidence");
    }

    // Once the complete prefix is accepted, body backpressure is an
    // ambiguous response. The exact claim must remain live rather than becoming
    // immediately claimable while the peer may hold a partial canonical frame.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS resumable body handoff");
        TempDatabasePath database_path("anonsync-file-tls-resumable-body");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 750U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-resumable-body", sender_actor,
            owner_limits(), "file TLS resumable-body owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS resumable-body service");
        const std::string payload(limits.max_payload_bytes, 'q');
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/resumable-body.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "body-worker", 30U,
            payload_snapshot("folder-file-tls-resumable-body", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare resumable-body fixture");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        make_socket_nonblocking(pair.connection.server_fd.get());

        auto writer = anonsync::
            begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
                service, pair.sender_channel, *outbound,
                "file TLS resumable body dispatch");
        require(writer.active() && writer.body_bytes_written() == 0U,
                "dispatch consumed body bytes before event-loop handoff");

        // A second SQLite write on the same owner proves the prefix guard was
        // committed and destroyed before the continuation escaped.
        clock->epoch = 751U;
        require(
            owner.renew_outbox_lease_or_throw(
                receiver_actor.device_id, operation.operation_id,
                outbound->claim.intent.lease.claim_id, 30U) ==
                anonsync::SyncReplicaSqliteOutboxReceiptResult::Applied,
            "resumable dispatch retained SQLite writer authority");

        (void)advance_tls_write_until_want(
            writer, "file TLS resumable body dispatch");
        const auto pending_cutpoint = writer.body_bytes_written();
        require(pending_cutpoint < outbound->request_frame.size(),
                "resumable dispatch lost its incomplete body cutpoint");
        (void)writer.pending_readiness_or_throw();
        const auto pending_snapshot = owner.snapshot_or_throw();
        require(pending_snapshot.outbox.size() == 1U &&
                    pending_snapshot.outbox.front().lease.claim_id ==
                        outbound->claim.intent.lease.claim_id &&
                    pending_snapshot.outbox.front().lease.retry_released_at_epoch ==
                        0U &&
                    pending_snapshot.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::None,
                "body backpressure released or replaced an ambiguous attempt");

        const auto transfer =
            finish_file_tls_dispatch_with_nonblocking_reader(
                writer, pair.receiver_channel,
                limits.max_request_frame_bytes, true,
                "file TLS resumable body transfer");
        require(transfer.frame == outbound->request_frame,
                "resumed file dispatch changed the canonical frame bytes");
        require(transfer.write_poll_operations > 0U &&
                    transfer.max_write_step <=
                        anonsync::kSyncReplicaTlsRecordWriteStepBytes,
                "resumed file dispatch hid an unbounded write loop");
        const auto final_snapshot = owner.snapshot_or_throw();
        require(final_snapshot.outbox.size() == 1U &&
                    final_snapshot.outbox.front().lease.claim_id ==
                        outbound->claim.intent.lease.claim_id,
                "local TLS completion retired sender intent without receipt");
    }

    // Abandoning the exact continuation after prefix acceptance poisons the
    // stream but keeps the durable attempt live. The peer may already hold a
    // partial canonical frame, so automatic exact release would duplicate
    // authority rather than merely recover liveness.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS post-prefix abandonment");
        TempDatabasePath database_path("anonsync-file-tls-body-abandonment");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 775U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-body-abandonment", sender_actor,
            owner_limits(), "file TLS body-abandonment owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS body-abandonment service");
        const std::string payload(limits.max_payload_bytes, 'a');
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/body-abandonment.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "abandon-worker", 30U,
            payload_snapshot("folder-file-tls-body-abandonment", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare abandonment fixture");
        make_socket_nonblocking_with_small_send_buffer(
            pair.connection.client_fd.get());
        {
            auto writer = anonsync::
                begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
                    service, pair.sender_channel, *outbound,
                    "file TLS post-prefix abandonment");
            (void)advance_tls_write_until_want(
                writer, "file TLS post-prefix abandonment");
            require(writer.active(),
                    "post-prefix writer was not live at abandonment frontier");
        }

        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().operation_id ==
                        operation.operation_id &&
                    snapshot.outbox.front().lease.claim_id ==
                        outbound->claim.intent.lease.claim_id &&
                    snapshot.outbox.front().lease.retry_released_at_epoch == 0U &&
                    snapshot.outbox.front().lease.retry_release_provenance ==
                        anonsync::SyncReplicaOutboxRetryReleaseProvenance::None,
                "post-prefix abandonment released or replaced an ambiguous attempt");
        unsigned char byte = 0U;
        errno = 0;
        const ssize_t pending = ::recv(
            pair.connection.server_fd.get(), &byte, 1U,
            MSG_PEEK | MSG_DONTWAIT);
        require(pending == 1,
                "post-prefix abandonment produced no observable stream progress");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.sender_channel, "reuse", 1024U,
                    "file TLS abandoned-body channel reuse");
            },
            "poisoned",
            "post-prefix abandonment left the uncertain stream reusable");
    }

    // Bounded lease renewal changes only the durable deadline; the original
    // prepared frame and claim identity remain dispatchable under re-attestation.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "file TLS renewal tolerance");
        TempDatabasePath database_path("anonsync-file-tls-renewal");
        auto clock = std::make_shared<MutableClockState>();
        clock->epoch = 800U;
        anonsync::SyncSqliteDb database = open_database(database_path.path);
        anonsync::SyncReplicaSqliteOwner owner(
            database.db, "folder-file-tls-renewal", sender_actor,
            owner_limits(), "file TLS renewal owner", make_clock(clock));
        anonsync::SyncReplicaFileDeliveryService service(
            owner, nullptr, limits, "file TLS renewal service");
        const std::string payload = "renewed-claim-payload";
        const auto operation = owner.create_local_file_or_throw(
            "dispatch/renewed.bin", payload.size(),
            anonsync::sha256_hex(payload), destination);
        const auto outbound = service.claim_next_request_or_throw(
            pair.sender_channel.delivery_authority(), "renew-worker", 10U,
            payload_snapshot("folder-file-tls-renewal", payload));
        require(outbound.has_value(),
                "file TLS service did not prepare renewal fixture");
        const std::uint64_t old_deadline =
            outbound->claim.intent.lease.lease_expires_at_epoch;
        clock->epoch = 805U;
        require(
            owner.renew_outbox_lease_or_throw(
                receiver_actor.device_id, operation.operation_id,
                outbound->claim.intent.lease.claim_id, 30U) ==
                anonsync::SyncReplicaSqliteOutboxReceiptResult::Applied,
            "file TLS fixture could not renew the exact attempt");
        make_socket_nonblocking(pair.connection.client_fd.get());
        auto renewed_writer = anonsync::
            begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
                service, pair.sender_channel, *outbound,
                "file TLS renewed attempt dispatch");
        renewed_writer.finish_or_throw();
        require(
            anonsync::read_sync_replica_tls_record_or_throw(
                pair.receiver_channel, limits.max_request_frame_bytes,
                "file TLS renewed attempt read") == outbound->request_frame,
            "bounded renewal changed the canonical TLS frame");
        const auto snapshot = owner.snapshot_or_throw();
        require(snapshot.outbox.size() == 1U &&
                    snapshot.outbox.front().lease.claim_id ==
                        outbound->claim.intent.lease.claim_id &&
                    snapshot.outbox.front().lease.lease_expires_at_epoch >
                        old_deadline,
                "TLS dispatch rejected or rewrote a bounded lease renewal");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_tls_io_policy_profile_and_mutation_fences(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    // The context helper is authoritative even when a caller presents an
    // already-mutated context. It removes truncation laundering and unsupported
    // retry semantics before any SSL object can inherit them.
    {
        SslContextPtr context(SSL_CTX_new(TLS_method()), SSL_CTX_free);
        if (!context) {
            fail_openssl("TLS I/O policy test could not allocate a context");
        }
        (void)SSL_CTX_set_options(
            context.get(), SSL_OP_IGNORE_UNEXPECTED_EOF);
        (void)SSL_CTX_clear_mode(context.get(), SSL_MODE_AUTO_RETRY);
        (void)SSL_CTX_set_mode(context.get(), SSL_MODE_ASYNC);
        SSL_CTX_set_read_ahead(context.get(), 1);
        SSL_CTX_set_quiet_shutdown(context.get(), 1);
        anonsync::configure_sync_replica_tls13_client_context_or_throw(
            context.get(), "TLS I/O policy context normalization");
        require(
            (SSL_CTX_get_options(context.get()) &
             SSL_OP_IGNORE_UNEXPECTED_EOF) == 0U &&
                (SSL_CTX_get_mode(context.get()) & SSL_MODE_AUTO_RETRY) !=
                    0L &&
                (SSL_CTX_get_mode(context.get()) & SSL_MODE_ASYNC) == 0L &&
                SSL_CTX_get_read_ahead(context.get()) == 0 &&
                SSL_CTX_get_quiet_shutdown(context.get()) == 0,
            "TLS context profile did not normalize strict record-I/O semantics");
    }

    const auto require_authentication_rejection =
        [&](std::string_view label,
            std::string_view expected_fragment,
            auto&& mutate) {
            TlsConnectionPair pair = make_tls_connection_pair(
                client_context, server_context);
            std::forward<decltype(mutate)>(mutate)(pair.client.get());
            require_error(
                [&] {
                    (void)anonsync::
                        authenticate_sync_replica_tls13_channel_or_throw(
                            pair.client.get(),
                            {receiver_actor, receiver_pin},
                            std::string(label));
                },
                expected_fragment,
                std::string(label) +
                    " inherited authenticated authority under an unsafe SSL policy");
        };

    require_authentication_rejection(
        "TLS authentication unexpected-EOF policy",
        "SSL_OP_IGNORE_UNEXPECTED_EOF",
        [](SSL* ssl) {
            (void)SSL_set_options(ssl, SSL_OP_IGNORE_UNEXPECTED_EOF);
        });
    require_authentication_rejection(
        "TLS authentication AUTO_RETRY policy",
        "SSL_MODE_AUTO_RETRY",
        [](SSL* ssl) {
            (void)SSL_clear_mode(ssl, SSL_MODE_AUTO_RETRY);
        });
    require_authentication_rejection(
        "TLS authentication asynchronous mode policy",
        "SSL_MODE_ASYNC",
        [](SSL* ssl) { (void)SSL_set_mode(ssl, SSL_MODE_ASYNC); });
    require_authentication_rejection(
        "TLS authentication read-ahead policy",
        "read-ahead",
        [](SSL* ssl) { SSL_set_read_ahead(ssl, 1); });
    require_authentication_rejection(
        "TLS authentication quiet-shutdown policy",
        "quiet TLS shutdown",
        [](SSL* ssl) { SSL_set_quiet_shutdown(ssl, 1); });
    require_authentication_rejection(
        "TLS authentication preclosed policy",
        "shutdown state is already nonzero",
        [](SSL* ssl) { SSL_set_shutdown(ssl, SSL_RECEIVED_SHUTDOWN); });

    const auto require_live_mutation_rejection =
        [&](std::string_view label,
            std::string_view expected_fragment,
            auto&& mutate) {
            auto pair = make_authenticated_tls_pair(
                client_context, server_context, sender_actor, receiver_actor,
                sender_pin, receiver_pin, std::string(label));
            std::forward<decltype(mutate)>(mutate)(
                pair.connection.client.get());
            require_socket_has_no_pending_bytes(
                pair.connection.server_fd.get(),
                std::string(label) + " mutated transport before reproof");
            require_error(
                [&] {
                    anonsync::write_sync_replica_tls_record_or_throw(
                        pair.sender_channel, "policy-probe", 64U,
                        std::string(label));
                },
                expected_fragment,
                std::string(label) +
                    " reused authenticated authority after SSL policy mutation");
            require_socket_has_no_pending_bytes(
                pair.connection.server_fd.get(),
                std::string(label) +
                    " wrote bytes before rejecting SSL policy mutation");
            require_error(
                [&] {
                    anonsync::write_sync_replica_tls_record_or_throw(
                        pair.sender_channel, "poison-probe", 64U,
                        std::string(label) + " poisoned reuse");
                },
                "poisoned",
                std::string(label) +
                    " left a contradicted authenticated capability reusable");
        };

    require_live_mutation_rejection(
        "TLS live option-mask mutation",
        "option mask changed after authentication",
        [](SSL* ssl) {
            (void)SSL_set_options(ssl, SSL_OP_IGNORE_UNEXPECTED_EOF);
        });
    require_live_mutation_rejection(
        "TLS live mode-mask mutation",
        "mode mask changed after authentication",
        [](SSL* ssl) {
            (void)SSL_clear_mode(ssl, SSL_MODE_AUTO_RETRY);
        });
    require_live_mutation_rejection(
        "TLS live read-ahead mutation",
        "read-ahead policy changed after authentication",
        [](SSL* ssl) { SSL_set_read_ahead(ssl, 1); });
    require_live_mutation_rejection(
        "TLS live quiet-shutdown mutation",
        "quiet-shutdown policy changed after authentication",
        [](SSL* ssl) { SSL_set_quiet_shutdown(ssl, 1); });
    require_live_mutation_rejection(
        "TLS live verifier mutation",
        "peer-verification mode changed after authentication",
        [](SSL* ssl) { SSL_set_verify(ssl, SSL_VERIFY_NONE, nullptr); });
    require_live_mutation_rejection(
        "TLS live shutdown-state mutation",
        "shutdown state changed after authentication",
        [](SSL* ssl) { SSL_set_shutdown(ssl, SSL_RECEIVED_SHUTDOWN); });

    // Pending WANT target disclosure must not hand an event loop a descriptor
    // after the exact SSL retry semantics have changed.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending-target policy mutation");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS pending-target policy mutation");
        require(
            reader.advance_or_throw() ==
                anonsync::SyncReplicaTlsRecordReadProgress::WantRead,
            "TLS pending-target fixture did not establish WANT_READ");
        (void)SSL_set_options(
            pair.connection.server.get(), SSL_OP_IGNORE_UNEXPECTED_EOF);
        require_error(
            [&] { (void)reader.pending_readiness_or_throw(); },
            "option mask changed after authentication",
            "pending TLS poll target escaped after option mutation");
        require(!reader.active(),
                "failed pending-target policy reproof retained read authority");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "reuse", 64U,
                    "TLS pending-target policy mutation reuse");
            },
            "poisoned",
            "pending-target policy contradiction left the stream reusable");
    }

    // The exact retry itself repeats the policy proof even when the caller skips
    // advisory target lookup and calls advance directly.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS pending-retry policy mutation");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS pending-retry policy mutation");
        require(
            reader.advance_or_throw() ==
                anonsync::SyncReplicaTlsRecordReadProgress::WantRead,
            "TLS pending-retry fixture did not establish WANT_READ");
        (void)SSL_clear_mode(
            pair.connection.server.get(), SSL_MODE_AUTO_RETRY);
        require_error(
            [&] { (void)reader.advance_or_throw(); },
            "mode mask changed after authentication",
            "pending TLS retry entered OpenSSL after mode mutation");
        require(!reader.active(),
                "failed pending-retry policy reproof retained read authority");
    }

    // Abrupt transport EOF remains a truncation/error signal. It must never be
    // converted into the PeerClosed state reserved for authenticated
    // close_notify evidence.
    {
        auto pair = make_authenticated_tls_pair(
            client_context, server_context, sender_actor, receiver_actor,
            sender_pin, receiver_pin, "TLS abrupt EOF classification");
        make_socket_nonblocking(pair.connection.server_fd.get());
        auto reader = anonsync::begin_sync_replica_tls_record_read_or_throw(
            pair.receiver_channel, 1024U,
            anonsync::SyncReplicaTlsRecordReadReadinessPolicy::
                RequireNonblockingSocket,
            "TLS abrupt EOF classification");
        if (::shutdown(pair.connection.client_fd.get(), SHUT_RDWR) != 0) {
            fail("TLS abrupt EOF test could not shut down the peer transport");
        }
        require_error(
            [&] {
                for (std::size_t iteration = 0U; iteration < 128U;
                     ++iteration) {
                    const auto progress = reader.advance_or_throw();
                    if (progress ==
                        anonsync::SyncReplicaTlsRecordReadProgress::PeerClosed) {
                        fail("abrupt TLS EOF was laundered into clean peer close");
                    }
                    if (progress ==
                        anonsync::SyncReplicaTlsRecordReadProgress::Complete) {
                        fail("abrupt TLS EOF fabricated a complete record");
                    }
                }
                fail("abrupt TLS EOF did not reach a terminal error");
            },
            "failed with SSL error",
            "abrupt TLS EOF was not retained as truncation/error evidence");
        require_error(
            [&] {
                anonsync::write_sync_replica_tls_record_or_throw(
                    pair.receiver_channel, "reuse", 64U,
                    "TLS abrupt EOF classification reuse");
            },
            "poisoned",
            "abrupt TLS EOF left the record stream reusable");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_tls_channel_retains_ssl_and_fences_affinity(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __unix__
    TlsConnectionPair retained = make_tls_connection_pair(
        client_context, server_context);
    auto retained_sender =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            retained.client.get(), {receiver_actor, receiver_pin},
            "TLS retained sender channel");
    auto retained_receiver =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            retained.server.get(), {sender_actor, sender_pin},
            "TLS retained receiver channel");

    std::string foreign_thread_error;
    std::thread foreign_thread([&] {
        try {
            anonsync::write_sync_replica_tls_record_or_throw(
                retained_sender, "foreign-thread", 64U,
                "TLS foreign-thread capability use");
        } catch (const std::exception& error) {
            foreign_thread_error = error.what();
        }
    });
    foreign_thread.join();
    require(foreign_thread_error.find("thread") != std::string::npos,
            "TLS channel touched OpenSSL from a foreign thread");

    auto inherited_probe =
        anonsync::test::spawn_inherited_test_process_or_throw(
            [&retained_sender]() -> int {
                anonsync::write_sync_replica_tls_record_or_throw(
                    retained_sender, "fork-child", 64U,
                    "TLS fork-inherited capability use");
                return 99;
            },
            "TLS fork-inherited capability probe");
    inherited_probe.wait_for_exact_exit(
        anonsync::kSyncProcessCapabilityViolationExitCode,
        std::chrono::seconds(5),
        "TLS fork-inherited capability probe");
    require(!inherited_probe.active(),
            "fork-inherited TLS capability probe retained process authority");

    // Authentication retains one reference on each SSL object. Releasing the
    // caller's original references must not invalidate the channels.
    retained.client.reset();
    retained.server.reset();
    anonsync::write_sync_replica_tls_record_or_throw(
        retained_sender, "retained-reference", 64U,
        "TLS retained-reference write");
    const std::string received =
        anonsync::read_sync_replica_tls_record_or_throw(
            retained_receiver, 64U, "TLS retained-reference read");
    require(received == "retained-reference",
            "TLS channel borrowed a caller-owned SSL lifetime");
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
#endif
}

void test_tls_membership_snapshot_value_authority(
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin) {
    const std::string folder = "folder-tls-membership-snapshot";
    const anonsync::SyncReplicaActor second_peer{
        "device-tls-membership-second-peer", 9303U};
    const std::string rotation_pin =
        anonsync::sha256_hex("membership rotation overlap key");
    const std::string second_peer_pin =
        anonsync::sha256_hex("membership independent peer key");
    const std::string unknown_pin =
        anonsync::sha256_hex("membership unknown key");

    const std::vector<anonsync::SyncReplicaTlsMembershipEntry> entries{
        {second_peer_pin, second_peer},
        {sender_pin, sender_actor},
        {rotation_pin, sender_actor},
    };
    const anonsync::SyncReplicaTlsMembershipSnapshot snapshot(
        folder, receiver_actor, 41U, entries,
        "TLS membership canonical snapshot");
    const anonsync::SyncReplicaTlsMembershipSnapshot reordered(
        folder, receiver_actor, 41U,
        {
            {rotation_pin, sender_actor},
            {second_peer_pin, second_peer},
            {sender_pin, sender_actor},
        },
        "TLS membership reordered snapshot");

    require(
        snapshot.active() && snapshot.folder_id() == folder &&
            snapshot.local_actor() == receiver_actor &&
            snapshot.policy_epoch() == 41U && snapshot.entry_count() == 3U &&
            anonsync::is_lowercase_sha256_hex(snapshot.snapshot_digest()),
        "immutable TLS membership snapshot lost canonical identity metadata");
    require(
        snapshot.snapshot_digest() == reordered.snapshot_digest(),
        "immutable TLS membership digest depended on caller entry order");
    require(
        snapshot.resolve_peer_or_throw(sender_pin) == sender_actor &&
            snapshot.resolve_peer_or_throw(rotation_pin) == sender_actor &&
            snapshot.resolve_peer_or_throw(second_peer_pin) == second_peer &&
            !snapshot.resolve_peer_or_throw(unknown_pin).has_value(),
        "immutable TLS membership lookup lost exact SPKI-to-actor authority");

    const anonsync::SyncReplicaTlsMembershipSnapshot newer_policy(
        folder, receiver_actor, 42U, entries,
        "TLS membership newer policy snapshot");
    require(
        newer_policy.snapshot_digest() != snapshot.snapshot_digest(),
        "immutable TLS membership digest omitted policy epoch");

    auto copied = snapshot;
    auto moved = std::move(copied);
    require(
        !copied.active() && moved.active() &&
            moved.snapshot_digest() == snapshot.snapshot_digest(),
        "immutable TLS membership move duplicated or lost snapshot authority");
    require_error(
        [&] { (void)copied.entry_count(); }, "inactive",
        "moved-from TLS membership snapshot remained usable");

    require_error(
        [&] {
            (void)anonsync::SyncReplicaTlsMembershipSnapshot(
                folder, receiver_actor, 0U, entries,
                "TLS membership zero policy epoch");
        },
        "policy_epoch must be positive",
        "TLS membership snapshot accepted an unversioned policy");
    require_error(
        [&] {
            std::vector<anonsync::SyncReplicaTlsMembershipEntry> oversized(
                static_cast<std::size_t>(
                    anonsync::kSyncReplicaTlsMembershipMaxEntries + 1U));
            (void)anonsync::SyncReplicaTlsMembershipSnapshot(
                folder, receiver_actor, 43U, std::move(oversized),
                "TLS membership oversized snapshot");
        },
        "entry count exceeds the configured hard ceiling",
        "TLS membership snapshot accepted an unbounded entry set");
    require_error(
        [&] {
            std::string uppercase_pin = sender_pin;
            uppercase_pin.front() = 'A';
            (void)anonsync::SyncReplicaTlsMembershipSnapshot(
                folder, receiver_actor, 43U,
                {{uppercase_pin, sender_actor}},
                "TLS membership uppercase SPKI");
        },
        "not lowercase SHA-256",
        "TLS membership snapshot normalized a noncanonical SPKI pin");
    require_error(
        [&] {
            (void)anonsync::SyncReplicaTlsMembershipSnapshot(
                folder, receiver_actor, 43U,
                {{sender_pin, sender_actor}, {sender_pin, second_peer}},
                "TLS membership duplicate SPKI");
        },
        "duplicate SPKI membership authority",
        "TLS membership snapshot admitted conflicting duplicate SPKI authority");
    require_error(
        [&] {
            (void)anonsync::SyncReplicaTlsMembershipSnapshot(
                folder, receiver_actor, 43U,
                {{sender_pin,
                  {receiver_actor.device_id, receiver_actor.epoch + 1U}}},
                "TLS membership reflected local device");
        },
        "receiver's own device_id",
        "TLS membership snapshot authorized the receiver as its own peer");
    require_error(
        [&] {
            (void)snapshot.resolve_peer_or_throw(
                "not-a-pin", "TLS membership malformed lookup");
        },
        "not lowercase SHA-256",
        "TLS membership lookup normalized malformed authenticated evidence");
    require_error(
        [&] {
            snapshot.require_service_identity_or_throw(
                "folder-tls-membership-wrong", receiver_actor,
                "TLS membership wrong folder");
        },
        "does not match receiver service identity",
        "TLS membership snapshot crossed folder authority");
    require_error(
        [&] {
            snapshot.require_service_identity_or_throw(
                folder, second_peer, "TLS membership wrong local actor");
        },
        "does not match receiver service identity",
        "TLS membership snapshot crossed local actor authority");
}


struct TlsMembershipEvidence final {
    std::uint64_t state_generation = 0U;
    std::uint64_t policy_epoch = 0U;
    std::uint64_t entry_count = 0U;
    std::string snapshot_digest;
    std::string previous_chain_digest;
    std::string chain_digest;
    std::uint64_t durable_anchor_state_generation = 0U;
    std::string durable_anchor_chain_digest;
    std::uint64_t durable_anchor_transition_sequence = 0U;
    std::string durable_anchor_transition_digest;
};

[[nodiscard]] TlsMembershipEvidence capture_membership_evidence(
    const anonsync::SyncReplicaTlsAnchoredMembershipAuthority& authority) {
    const auto& snapshot = authority.snapshot();
    return {
        authority.state_generation(),
        snapshot.policy_epoch(),
        snapshot.entry_count(),
        snapshot.snapshot_digest(),
        authority.previous_chain_digest(),
        authority.chain_digest(),
        authority.durable_anchor().state_generation,
        authority.durable_anchor().chain_digest,
        authority.durable_transition_sequence(),
        authority.durable_transition_digest(),
    };
}

[[nodiscard]] bool result_binds_membership(
    const anonsync::SyncReplicaFileTlsServerResult& result,
    const TlsMembershipEvidence& membership) {
    return result.membership_state_generation ==
               membership.state_generation &&
           result.membership_policy_epoch == membership.policy_epoch &&
           result.membership_entry_count == membership.entry_count &&
           result.membership_snapshot_digest == membership.snapshot_digest &&
           result.membership_previous_chain_digest ==
               membership.previous_chain_digest &&
           result.membership_chain_digest == membership.chain_digest &&
           result.membership_durable_anchor_state_generation ==
               membership.durable_anchor_state_generation &&
           result.membership_durable_anchor_chain_digest ==
               membership.durable_anchor_chain_digest &&
           result.membership_durable_anchor_transition_sequence ==
               membership.durable_anchor_transition_sequence &&
           result.membership_durable_anchor_transition_digest ==
               membership.durable_anchor_transition_digest;
}

void test_file_tls_server_session_owner(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __linux__
    // Listener authority is an observed capability, not an integer. Mutable
    // readiness/inheritance policy and SO_ACCEPTCONN are all required before a
    // one-shot session can spend accept authority.
    {
        LoopbackListener policy_listener = make_loopback_listener_fixture();
        make_socket_blocking(policy_listener.descriptor.get());
        require_error(
            [&] {
                (void)anonsync::
                    observe_sync_replica_file_tls_server_listener_or_throw(
                        policy_listener.descriptor.get(),
                        "TLS server blocking listener");
            },
            "is not nonblocking",
            "TLS server listener accepted blocking accept authority");
        make_socket_nonblocking(policy_listener.descriptor.get());

        set_descriptor_close_on_exec(
            policy_listener.descriptor.get(), false);
        require_error(
            [&] {
                (void)anonsync::
                    observe_sync_replica_file_tls_server_listener_or_throw(
                        policy_listener.descriptor.get(),
                        "TLS server inheritable listener");
            },
            "inheritable across exec",
            "TLS server listener accepted exec-inheritable authority");
        set_descriptor_close_on_exec(
            policy_listener.descriptor.get(), true);

        FileDescriptor nonlistener(::socket(
            AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0));
        if (nonlistener.get() < 0) {
            fail("TLS server test could not create nonlistener socket");
        }
        require_error(
            [&] {
                (void)anonsync::
                    observe_sync_replica_file_tls_server_listener_or_throw(
                        nonlistener.get(), "TLS server nonlistener");
            },
            "is not a listening socket",
            "TLS server listener accepted a non-listening stream socket");

        auto listener_capability = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                policy_listener.descriptor.get(),
                "TLS server move-only listener");
        auto moved_capability = std::move(listener_capability);
        require(!listener_capability.active() && moved_capability.active() &&
                    moved_capability.descriptor() ==
                        policy_listener.descriptor.get(),
                "TLS server listener move duplicated or lost accept authority");
    }

    TempFileDeliveryWorkspace workspace("anonsync-file-tls-server-owner");
    const std::string folder = "folder-file-tls-server-owner";
    auto receiver_clock = std::make_shared<MutableClockState>();
    receiver_clock->epoch = 1200U;
    anonsync::SyncSqliteDb receiver_database =
        open_database(workspace.receiver_db);
    anonsync::SyncSqliteDb effect_database =
        open_database(workspace.effect_db);
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_database.db, folder, receiver_actor, owner_limits(),
        "file TLS server receiver", make_clock(receiver_clock));
    anonsync::SyncReplicaFileEffectSqliteOwner effect(
        effect_database.db, folder, workspace.files, file_effect_limits(),
        "file TLS server effects");
    const auto limits = file_service_limits();
    anonsync::SyncReplicaFileDeliveryService receiver_service(
        receiver, &effect, limits, "file TLS server receiver service");
    const auto baseline_receiver = receiver.snapshot_or_throw();
    const auto baseline_effect = effect.snapshot_or_throw();

    TempDatabasePath membership_path(
        "anonsync-file-tls-server-membership");
    anonsync::SyncSqliteDb membership_database =
        open_database(membership_path.path);
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, folder, receiver_actor,
        "TLS server durable membership owner");
    TempDatabasePath membership_anchor_path(
        "anonsync-file-tls-server-membership-anchor");
    anonsync::SyncSqliteDb membership_anchor_database =
        open_database(membership_anchor_path.path);
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner membership_anchor_owner(
        membership_anchor_database.db, folder, receiver_actor,
        "TLS server durable membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner anchored_membership_owner(
        membership_owner, membership_anchor_owner,
        "TLS server anchored membership coordinator");
    auto sender_membership_authority = anchored_membership_owner.publish_or_throw(
        membership_owner.snapshot_or_throw().anchor(), 1201U,
        {{sender_pin, sender_actor}});
    TlsMembershipEvidence sender_membership =
        capture_membership_evidence(sender_membership_authority);
    anonsync::SyncReplicaTlsMembershipAnchor current_membership_anchor =
        sender_membership_authority.anchor();

    const auto retained_server_context = [&] {
        return anonsync::
            retain_sync_replica_file_tls_server_context_or_throw(
                server_context, "TLS server retained context");
    };
    require_error(
        [&] {
            (void)anonsync::
                retain_sync_replica_file_tls_server_context_or_throw(
                    nullptr, "TLS server null retained context");
        },
        "SSL context is null",
        "TLS server retained a null OpenSSL context");
    auto retained_context = retained_server_context();
    auto moved_context = std::move(retained_context);
    require(
        !retained_context.active() && moved_context.active(),
        "TLS server context move duplicated or lost retained lifetime");

    // The retained reference is real lifetime ownership, not a precondition
    // check on a raw pointer. Destroy the caller's original SSL_CTX reference
    // before the one-shot server allocates its SSL object; an accept timeout
    // must still complete normally through the retained generation.
    {
        SslContextPtr released_original(
            SSL_CTX_new(TLS_method()), SSL_CTX_free);
        require(
            released_original != nullptr,
            "TLS server retention fixture could not allocate SSL context");
        auto retained_after_release = anonsync::
            retain_sync_replica_file_tls_server_context_or_throw(
                released_original.get(),
                "TLS server context surviving original release");
        released_original.reset();

        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server retained-only context listener");
        const auto now = std::chrono::steady_clock::now();
        const auto result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener, std::move(retained_after_release),
                anchored_membership_owner.current_authority_or_throw(),
                {
                    now + std::chrono::milliseconds(25),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                },
                "TLS server retained-only context session");
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::
                        AcceptDeadlineExpired &&
                !retained_after_release.active() &&
                result_binds_membership(result, sender_membership),
            "TLS server context did not survive release of the original reference");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server retained-only context reached durable receiver authority");
    }

    // Service identity is checked against owner-emitted durable authority before
    // accept authority is spent. Both mismatches leave the same listener usable
    // by the correct authority, proving this is a pre-accept cutpoint.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server membership preaccept listener");
        TempDatabasePath wrong_folder_path(
            "anonsync-file-tls-server-wrong-folder-membership");
        anonsync::SyncSqliteDb wrong_folder_database =
            open_database(wrong_folder_path.path);
        anonsync::SyncReplicaTlsMembershipSqliteOwner wrong_folder_owner(
            wrong_folder_database.db, "folder-file-tls-server-wrong",
            receiver_actor, "TLS server wrong-folder durable membership");
        TempDatabasePath wrong_folder_anchor_path(
            "anonsync-file-tls-server-wrong-folder-anchor");
        anonsync::SyncSqliteDb wrong_folder_anchor_database =
            open_database(wrong_folder_anchor_path.path);
        anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner
            wrong_folder_anchor_owner(
                wrong_folder_anchor_database.db,
                "folder-file-tls-server-wrong", receiver_actor,
                "TLS server wrong-folder durable anchor");
        anonsync::SyncReplicaTlsMembershipAnchoredOwner
            wrong_folder_coordinator(
                wrong_folder_owner, wrong_folder_anchor_owner,
                "TLS server wrong-folder anchored membership");
        auto wrong_folder = wrong_folder_coordinator.publish_or_throw(
            wrong_folder_owner.snapshot_or_throw().anchor(), 1203U,
            {{sender_pin, sender_actor}});

        const anonsync::SyncReplicaActor wrong_local_actor{
            "device-file-tls-server-wrong-local", 1204U};
        TempDatabasePath wrong_local_path(
            "anonsync-file-tls-server-wrong-local-membership");
        anonsync::SyncSqliteDb wrong_local_database =
            open_database(wrong_local_path.path);
        anonsync::SyncReplicaTlsMembershipSqliteOwner wrong_local_owner(
            wrong_local_database.db, folder, wrong_local_actor,
            "TLS server wrong-local durable membership");
        TempDatabasePath wrong_local_anchor_path(
            "anonsync-file-tls-server-wrong-local-anchor");
        anonsync::SyncSqliteDb wrong_local_anchor_database =
            open_database(wrong_local_anchor_path.path);
        anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner
            wrong_local_anchor_owner(
                wrong_local_anchor_database.db, folder, wrong_local_actor,
                "TLS server wrong-local durable anchor");
        anonsync::SyncReplicaTlsMembershipAnchoredOwner
            wrong_local_coordinator(
                wrong_local_owner, wrong_local_anchor_owner,
                "TLS server wrong-local anchored membership");
        auto wrong_local = wrong_local_coordinator.publish_or_throw(
            wrong_local_owner.snapshot_or_throw().anchor(), 1204U,
            {{sender_pin, sender_actor}});
        const auto now = std::chrono::steady_clock::now();
        const anonsync::SyncReplicaFileTlsServerDeadlines deadlines{
            now + std::chrono::milliseconds(25),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
        };
        require_error(
            [&] {
                (void)anonsync::
                    serve_one_sync_replica_file_delivery_tls_session_or_throw(
                        receiver_service, listener, retained_server_context(),
                        std::move(wrong_folder), deadlines,
                        "TLS server wrong-folder preaccept");
            },
            "does not match receiver service identity",
            "TLS server accepted cross-folder membership authority");
        require_error(
            [&] {
                (void)anonsync::
                    serve_one_sync_replica_file_delivery_tls_session_or_throw(
                        receiver_service, listener, retained_server_context(),
                        std::move(wrong_local), deadlines,
                        "TLS server wrong-local preaccept");
            },
            "does not match receiver service identity",
            "TLS server accepted cross-actor membership authority");
        const auto result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener, retained_server_context(),
                anchored_membership_owner.current_authority_or_throw(), deadlines,
                "TLS server valid membership after mismatch");
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::
                        AcceptDeadlineExpired &&
                result_binds_membership(result, sender_membership),
            "TLS membership mismatch spent or replaced listener authority");
        require(
            receiver.snapshot_or_throw() == baseline_receiver &&
                effect.snapshot_or_throw() == baseline_effect,
            "TLS membership preaccept mismatch reached durable authority");
    }

    // Capability use re-proves mutable listener policy, and an ordinary
    // moved-from wrapper is rejected before the process fail-stop guard. Neither
    // local misuse can reach accept or durable receiver authority.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(), "TLS server live-policy listener");
        const auto now = std::chrono::steady_clock::now();
        const anonsync::SyncReplicaFileTlsServerDeadlines deadlines{
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
        };

        set_descriptor_close_on_exec(socket.descriptor.get(), false);
        require_error(
            [&] {
                (void)anonsync::
                    serve_one_sync_replica_file_delivery_tls_session_or_throw(
                        receiver_service, listener, retained_server_context(),
                        anchored_membership_owner.current_authority_or_throw(), deadlines,
                        "TLS server post-mint inheritable listener");
            },
            "inheritable across exec",
            "TLS server spent a listener after FD_CLOEXEC mutation");
        set_descriptor_close_on_exec(socket.descriptor.get(), true);

        make_socket_blocking(socket.descriptor.get());
        require_error(
            [&] {
                (void)anonsync::
                    serve_one_sync_replica_file_delivery_tls_session_or_throw(
                        receiver_service, listener, retained_server_context(),
                        anchored_membership_owner.current_authority_or_throw(), deadlines,
                        "TLS server post-mint blocking listener");
            },
            "is not nonblocking",
            "TLS server spent a listener after O_NONBLOCK mutation");
        make_socket_nonblocking(socket.descriptor.get());

        auto live_listener = std::move(listener);
        require_error(
            [&] {
                (void)anonsync::
                    serve_one_sync_replica_file_delivery_tls_session_or_throw(
                        receiver_service, listener, retained_server_context(),
                        anchored_membership_owner.current_authority_or_throw(), deadlines,
                        "TLS server moved-from listener use");
            },
            "listener capability is inactive",
            "TLS server moved-from listener reached process fail-stop authority");
        require(live_listener.active(),
                "TLS server moved-from rejection consumed live listener authority");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server local listener misuse reached durable receiver authority");
    }

    // An already-expired absolute accept cutpoint returns without fabricating an
    // accept4() attempt. Membership evidence is still bound before the result is
    // emitted, but no child socket, TLS session, or durable callback can exist.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server preexpired-accept listener");
        auto membership =
            anchored_membership_owner.current_authority_or_throw();
        const auto now = std::chrono::steady_clock::now();
        const auto result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener, retained_server_context(),
                std::move(membership),
                {
                    now - std::chrono::milliseconds(1),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                    now + std::chrono::seconds(1),
                },
                "TLS server preexpired-accept session");
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::
                        AcceptDeadlineExpired &&
                result.accept_attempts == 0U && !result.accepted &&
                !result.handshake_complete && !result.receive.has_value() &&
                result.shutdown_disposition == anonsync::
                    SyncReplicaFileTlsServerShutdownDisposition::NotAttempted &&
                result_binds_membership(result, sender_membership),
            "TLS server preexpired accept fabricated syscall or session authority");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server preexpired accept reached durable receiver authority");
    }

    // No queued peer: accept expiry destroys the prepared connection-local SSL
    // owner, owns no accepted descriptor, and invokes no durable callback. The
    // absolute deadline may expire before or after the first accept4() depending
    // on scheduling, so the attempt counter is deliberately not a correctness
    // predicate here.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(), "TLS server accept-timeout listener");
        auto membership =
            anchored_membership_owner.current_authority_or_throw();
        const auto now = std::chrono::steady_clock::now();
        const anonsync::SyncReplicaFileTlsServerDeadlines deadlines{
            now + std::chrono::milliseconds(25),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
            now + std::chrono::seconds(1),
        };
        const auto result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener, retained_server_context(),
                std::move(membership), deadlines,
                "TLS server accept-timeout session");
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::
                        AcceptDeadlineExpired,
            "TLS server no-peer accept did not terminate at its absolute cutpoint");
        require(
            !result.accepted && !result.handshake_complete &&
                !result.receive.has_value() &&
                result.shutdown_disposition == anonsync::
                    SyncReplicaFileTlsServerShutdownDisposition::NotAttempted &&
                result_binds_membership(result, sender_membership),
            "TLS server accept timeout fabricated session or membership progress");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server accept timeout reached durable receiver authority");
    }

    // A connected peer that sends no ClientHello is bounded by the independent
    // handshake cutpoint. Atomic accept policy is still observed, then the child
    // is closed without request parsing or durable state. The absolute cutpoint
    // may expire after accepted-socket policy proof but before the first
    // SSL_accept() under instrumentation or scheduler pressure, so the attempt
    // counter remains diagnostic rather than part of the authority predicate.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server slow-handshake listener");
        std::exception_ptr client_failure;
        std::thread client([&] {
            try {
                FileDescriptor descriptor =
                    connect_loopback_client_fixture(socket.port);
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            } catch (...) {
                client_failure = std::current_exception();
            }
        });
        const auto now = std::chrono::steady_clock::now();
        anonsync::SyncReplicaFileTlsServerResult result;
        std::exception_ptr server_failure;
        try {
            result = anonsync::
                serve_one_sync_replica_file_delivery_tls_session_or_throw(
                    receiver_service, listener, retained_server_context(),
                    anchored_membership_owner.current_authority_or_throw(),
                    {
                        now + std::chrono::seconds(1),
                        now + std::chrono::milliseconds(30),
                        now + std::chrono::seconds(1),
                        now + std::chrono::seconds(1),
                        now + std::chrono::seconds(1),
                    },
                    "TLS server slow-handshake session");
        } catch (...) {
            server_failure = std::current_exception();
        }
        client.join();
        if (client_failure) std::rethrow_exception(client_failure);
        if (server_failure) std::rethrow_exception(server_failure);
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::
                        HandshakeDeadlineExpired &&
                result.accepted && result.accepted_socket_policy_verified &&
                !result.handshake_complete &&
                !result.peer_spki_sha256.has_value() &&
                !result.receive.has_value(),
            "TLS server slow handshake crossed authentication authority");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server handshake timeout reached durable receiver authority");
    }

    // Plaintext on the TLS port is a typed handshake rejection. It cannot be
    // mistaken for a request, and no durable callback runs.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server plaintext-rejection listener");
        std::exception_ptr client_failure;
        std::thread client([&] {
            try {
                FileDescriptor descriptor =
                    connect_loopback_client_fixture(socket.port);
                constexpr std::string_view plaintext =
                    "GET /not-tls HTTP/1.0\r\n\r\n";
                std::size_t offset = 0U;
                while (offset < plaintext.size()) {
                    const ssize_t written = ::send(
                        descriptor.get(), plaintext.data() + offset,
                        plaintext.size() - offset, MSG_NOSIGNAL);
                    if (written <= 0) {
                        fail("TLS server plaintext client could not write fixture");
                    }
                    offset += static_cast<std::size_t>(written);
                }
                (void)::shutdown(descriptor.get(), SHUT_WR);
            } catch (...) {
                client_failure = std::current_exception();
            }
        });
        const auto now = std::chrono::steady_clock::now();
        anonsync::SyncReplicaFileTlsServerResult result;
        std::exception_ptr server_failure;
        try {
            result = anonsync::
                serve_one_sync_replica_file_delivery_tls_session_or_throw(
                    receiver_service, listener, retained_server_context(),
                    anchored_membership_owner.current_authority_or_throw(),
                    {
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                    },
                    "TLS server plaintext-rejection session");
        } catch (...) {
            server_failure = std::current_exception();
        }
        client.join();
        if (server_failure) std::rethrow_exception(server_failure);
        if (client_failure) std::rethrow_exception(client_failure);
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::HandshakeRejected &&
                result.accepted && result.accepted_socket_policy_verified &&
                !result.handshake_complete && result.handshake_attempts > 0U &&
                result.handshake_ssl_error.has_value() &&
                !result.peer_spki_sha256.has_value() &&
                !result.receive.has_value(),
            "TLS server plaintext was not retained as handshake rejection");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server rejected plaintext reached durable receiver authority");
    }

    // Rotate the same durable history to an explicit empty policy before the
    // unauthorized-peer scenario. The prior single-use capabilities have been
    // consumed; this committed generation is the exact authorization cutpoint.
    auto empty_membership_authority = anchored_membership_owner.publish_or_throw(
        current_membership_anchor, 1202U, {});
    const TlsMembershipEvidence empty_membership =
        capture_membership_evidence(empty_membership_authority);
    current_membership_anchor = empty_membership_authority.anchor();

    // A cryptographically valid peer remains unauthorized until the exact
    // current durable SPKI membership policy supplies an actor epoch.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(),
                "TLS server unauthorized listener");
        std::exception_ptr client_failure;
        std::thread client([&] {
            try {
                FileDescriptor descriptor =
                    connect_loopback_client_fixture(socket.port);
                configure_socket_timeout(descriptor.get());
                SslPtr ssl = connect_tls_client_fixture(
                    client_context, descriptor.get(),
                    "TLS server unauthorized client");
            } catch (...) {
                client_failure = std::current_exception();
            }
        });
        const auto now = std::chrono::steady_clock::now();
        anonsync::SyncReplicaFileTlsServerResult result;
        std::exception_ptr server_failure;
        try {
            result = anonsync::
                serve_one_sync_replica_file_delivery_tls_session_or_throw(
                    receiver_service, listener, retained_server_context(),
                    anchored_membership_owner.current_authority_or_throw(),
                    {
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                        now + std::chrono::seconds(2),
                    },
                    "TLS server unauthorized session");
        } catch (...) {
            server_failure = std::current_exception();
        }
        client.join();
        if (client_failure) std::rethrow_exception(client_failure);
        if (server_failure) std::rethrow_exception(server_failure);
        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::PeerUnauthorized &&
                result.accepted && result.accepted_socket_policy_verified &&
                result.handshake_complete &&
                result.peer_spki_sha256 == sender_pin &&
                !result.peer_actor.has_value() &&
                !result.receive.has_value() &&
                result.shutdown_disposition == anonsync::
                    SyncReplicaFileTlsServerShutdownDisposition::NotAttempted &&
                result_binds_membership(result, empty_membership),
            "TLS server authorized or misattributed a certificate-valid unmapped peer");
        require(receiver.snapshot_or_throw() == baseline_receiver &&
                    effect.snapshot_or_throw() == baseline_effect,
                "TLS server unauthorized peer reached durable receiver authority");
    }

    // Reauthorize the sender in the same append-only history. The successful
    // session must bind this newer generation rather than either prior policy.
    auto reauthorized_membership_authority = anchored_membership_owner.publish_or_throw(
        current_membership_anchor, 1203U, {{sender_pin, sender_actor}});
    sender_membership =
        capture_membership_evidence(reauthorized_membership_authority);
    current_membership_anchor = reauthorized_membership_authority.anchor();

    // The complete path composes real TCP accept, mutual TLS, exact membership,
    // one canonical file request, durable evidence/effect publication, exact
    // receipt, sender settlement, and a terminal one-shot close notification.
    {
        LoopbackListener socket = make_loopback_listener_fixture();
        auto listener = anonsync::
            observe_sync_replica_file_tls_server_listener_or_throw(
                socket.descriptor.get(), "TLS server success listener");
        const std::string payload = "accepted-session-terminal-payload";
        const std::string relative_path = "accepted-session.bin";
        bool sender_settled = false;
        std::string sender_operation_digest;
        std::string sender_evidence_digest;
        std::string sender_visible_digest;
        std::exception_ptr client_failure;
        std::thread client([&] {
            try {
                FileDescriptor descriptor =
                    connect_loopback_client_fixture(socket.port);
                configure_socket_timeout(descriptor.get());
                SslPtr ssl = connect_tls_client_fixture(
                    client_context, descriptor.get(),
                    "TLS server success client");
                auto sender_channel = anonsync::
                    authenticate_sync_replica_tls13_channel_or_throw(
                        ssl.get(), {receiver_actor, receiver_pin},
                        "TLS server success sender channel");

                auto sender_clock = std::make_shared<MutableClockState>();
                sender_clock->epoch = 1300U;
                anonsync::SyncSqliteDb sender_database =
                    open_database(workspace.sender_db);
                anonsync::SyncReplicaSqliteOwner sender(
                    sender_database.db, folder, sender_actor, owner_limits(),
                    "file TLS server sender", make_clock(sender_clock));
                anonsync::SyncReplicaFileDeliveryService sender_service(
                    sender, nullptr, limits,
                    "file TLS server sender service");
                const std::vector<std::string> destination{
                    receiver_actor.device_id};
                const auto operation = sender.create_local_file_or_throw(
                    relative_path, payload.size(), anonsync::sha256_hex(payload),
                    destination);
                const auto outbound =
                    sender_service.claim_next_request_or_throw(
                        sender_channel.delivery_authority(),
                        "accepted-session-worker", 30U,
                        payload_snapshot(folder, payload));
                require(outbound.has_value(),
                        "TLS server sender did not claim one file request");
                anonsync::write_sync_replica_tls_record_or_throw(
                    sender_channel, outbound->request_frame,
                    limits.max_request_frame_bytes,
                    "TLS server success request write");
                const std::string receipt =
                    anonsync::read_sync_replica_tls_record_or_throw(
                        sender_channel, limits.max_receipt_frame_bytes,
                        "TLS server success receipt read");
                sender_clock->epoch = 1301U;
                require(
                    sender_service.apply_receipt_or_throw(
                        sender_channel.delivery_authority(), outbound->request,
                        receipt) == anonsync::
                            SyncReplicaFileDeliveryReceiptApplyResult::
                                EffectSettled,
                    "TLS server terminal receipt did not settle sender");
                const auto snapshot = sender.snapshot_or_throw();
                sender_settled = snapshot.outbox.empty();
                sender_operation_digest = snapshot.operation_set_digest;
                sender_evidence_digest = snapshot.evidence_set_digest;
                sender_visible_digest = snapshot.visible_state_digest;
            } catch (...) {
                client_failure = std::current_exception();
            }
        });

        const auto now = std::chrono::steady_clock::now();
        anonsync::SyncReplicaFileTlsServerResult result;
        std::exception_ptr server_failure;
        try {
            result = anonsync::
                serve_one_sync_replica_file_delivery_tls_session_or_throw(
                    receiver_service, listener, retained_server_context(),
                    anchored_membership_owner.current_authority_or_throw(),
                    {
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                    },
                    "TLS server success session");
        } catch (...) {
            server_failure = std::current_exception();
        }
        client.join();
        if (server_failure) std::rethrow_exception(server_failure);
        if (client_failure) std::rethrow_exception(client_failure);

        require(
            result.disposition == anonsync::
                    SyncReplicaFileTlsServerDisposition::ReceiptSent &&
                result.accepted && result.accepted_socket_policy_verified &&
                result.handshake_complete && result.handshake_attempts > 0U &&
                result.peer_spki_sha256 == sender_pin &&
                result.peer_actor == sender_actor &&
                result.receive.has_value() &&
                result.receive->disposition == anonsync::
                    SyncReplicaFileTlsReceiveDisposition::ReceiptSent &&
                result.receive->inbound.has_value() &&
                result.receive->inbound->receipt.disposition == anonsync::
                    SyncReplicaFileDeliveryReceiptDisposition::Published &&
                (result.shutdown_disposition == anonsync::
                     SyncReplicaFileTlsServerShutdownDisposition::
                         CloseNotifySent ||
                 result.shutdown_disposition == anonsync::
                     SyncReplicaFileTlsServerShutdownDisposition::Complete) &&
                result.shutdown_attempts > 0U &&
                result_binds_membership(result, sender_membership),
            "TLS server did not preserve accepted-session terminal cutpoints and membership evidence");
        require(
            sender_settled &&
                read_binary_file(workspace.files / relative_path) == payload,
            "TLS server receipt preceded publication or failed sender settlement");
        const auto receiver_snapshot = receiver.snapshot_or_throw();
        require(
            receiver_snapshot.operation_set_digest ==
                    sender_operation_digest &&
                receiver_snapshot.evidence_set_digest ==
                    sender_evidence_digest &&
                receiver_snapshot.visible_state_digest ==
                    sender_visible_digest,
            "TLS server accepted session did not converge canonical evidence");
        const auto effect_snapshot = effect.snapshot_or_throw();
        require(
            effect_snapshot.effects.size() == 1U &&
                effect_snapshot.effects.front().state == anonsync::
                    SyncReplicaFileEffectState::Published,
            "TLS server accepted session created no unique published effect");
    }
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
    require(true, "accepted TLS server session owner requires Linux");
#endif
}


void test_file_tls_client_session_owner(
    SSL_CTX* client_context,
    SSL_CTX* server_context,
    const anonsync::SyncReplicaActor& sender_actor,
    const anonsync::SyncReplicaActor& receiver_actor,
    const std::string& sender_pin,
    const std::string& receiver_pin) {
#ifdef __linux__
    require_error(
        [&] {
            (void)anonsync::
                retain_sync_replica_file_tls_client_context_or_throw(
                    nullptr, "TLS client null retained context");
        },
        "SSL context is null",
        "TLS client retained a null OpenSSL context");
    auto retained_client_context = [&] {
        return anonsync::
            retain_sync_replica_file_tls_client_context_or_throw(
                client_context, "TLS client retained context");
    };
    auto retained = retained_client_context();
    auto moved = std::move(retained);
    require(!retained.active() && moved.active(),
            "TLS client context move duplicated or lost retained lifetime");

    TempFileDeliveryWorkspace workspace("anonsync-file-tls-client-owner");
    const std::filesystem::path payload_root = workspace.root / "payloads";
    std::filesystem::create_directory(payload_root);
    std::error_code permission_error;
    std::filesystem::permissions(
        payload_root, std::filesystem::perms::owner_all,
        std::filesystem::perm_options::replace, permission_error);
    if (permission_error) {
        fail("TLS client test could not make payload root private");
    }

    const std::string folder = "folder-file-tls-client-owner";
    const std::string payload = "production-client-owned-durable-payload";
    const std::string relative_path = "product-spine-client.bin";
    const auto limits = file_service_limits();

    auto receiver_clock = std::make_shared<MutableClockState>();
    receiver_clock->epoch = 1400U;
    anonsync::SyncSqliteDb receiver_database =
        open_database(workspace.receiver_db);
    anonsync::SyncSqliteDb effect_database =
        open_database(workspace.effect_db);
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_database.db, folder, receiver_actor, owner_limits(),
        "file TLS client receiver", make_clock(receiver_clock));
    anonsync::SyncReplicaFileEffectSqliteOwner effect(
        effect_database.db, folder, workspace.files, file_effect_limits(),
        "file TLS client effects");
    anonsync::SyncReplicaFileDeliveryService receiver_service(
        receiver, &effect, limits, "file TLS client receiver service");

    TempDatabasePath membership_path(
        "anonsync-file-tls-client-membership");
    anonsync::SyncSqliteDb membership_database =
        open_database(membership_path.path);
    anonsync::SyncReplicaTlsMembershipSqliteOwner membership_owner(
        membership_database.db, folder, receiver_actor,
        "TLS client durable membership owner");
    TempDatabasePath membership_anchor_path(
        "anonsync-file-tls-client-membership-anchor");
    anonsync::SyncSqliteDb membership_anchor_database =
        open_database(membership_anchor_path.path);
    anonsync::SyncReplicaTlsMembershipAnchorSqliteOwner
        membership_anchor_owner(
            membership_anchor_database.db, folder, receiver_actor,
            "TLS client durable membership anchor owner");
    anonsync::SyncReplicaTlsMembershipAnchoredOwner
        anchored_membership_owner(
            membership_owner, membership_anchor_owner,
            "TLS client anchored membership coordinator");
    (void)anchored_membership_owner.publish_or_throw(
        membership_owner.snapshot_or_throw().anchor(), 1401U,
        {{sender_pin, sender_actor}});

    LoopbackListener socket = make_loopback_listener_fixture();
    auto listener = anonsync::
        observe_sync_replica_file_tls_server_listener_or_throw(
            socket.descriptor.get(), "TLS client success listener");

    anonsync::SyncReplicaFileTlsClientResult client_result;
    anonsync::SyncReplicaFileTlsClientResult dispatch_expired_result;
    anonsync::SyncReplicaFileTlsClientResult expired_result;
    bool sender_settled = false;
    bool dispatch_expired_ready_intent_remained_unclaimed = false;
    std::string sender_operation_digest;
    std::string sender_evidence_digest;
    std::string sender_visible_digest;
    std::exception_ptr client_failure;
    std::thread client([&] {
        try {
            auto sender_clock = std::make_shared<MutableClockState>();
            sender_clock->epoch = 1500U;
            anonsync::SyncSqliteDb sender_database =
                open_database(workspace.sender_db);
            anonsync::SyncReplicaSqliteOwner sender(
                sender_database.db, folder, sender_actor, owner_limits(),
                "file TLS production client sender", make_clock(sender_clock));
            anonsync::SyncReplicaFileDeliveryService sender_service(
                sender, nullptr, limits,
                "file TLS production client sender service");
            anonsync::SyncReplicaFilePayloadStore payload_store(
                folder, payload_root,
                anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
                {}, "file TLS production client payload store");
            const auto put = payload_store.put_payload_or_throw(payload);
            require(
                put.content_sha256 == anonsync::sha256_hex(payload) &&
                    put.size_bytes == payload.size(),
                "TLS production client did not durably publish exact payload");
            auto payload_authority = payload_store.snapshot_or_throw();

            const std::vector<std::string> destination{
                receiver_actor.device_id};
            const auto operation = sender.create_local_file_or_throw(
                relative_path, payload.size(), anonsync::sha256_hex(payload),
                destination);

            const auto now = std::chrono::steady_clock::now();
            client_result = anonsync::
                send_one_sync_replica_file_delivery_tls_session_or_throw(
                    sender_service, payload_authority,
                    retained_client_context(),
                    {"127.0.0.1", socket.port},
                    {receiver_actor, receiver_pin},
                    "production-client-worker", 30U,
                    {
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                        now + std::chrono::seconds(5),
                    },
                    "TLS production client success session");

            const auto snapshot = sender.snapshot_or_throw();
            sender_settled = snapshot.outbox.empty();
            sender_operation_digest = snapshot.operation_set_digest;
            sender_evidence_digest = snapshot.evidence_set_digest;
            sender_visible_digest = snapshot.visible_state_digest;
            require(
                client_result.operation_id == operation.operation_id,
                "TLS production client result lost exact operation identity");

            const std::string dispatch_expired_path =
                "product-spine-client-dispatch-deadline.bin";
            const auto dispatch_expired_operation =
                sender.create_local_file_or_throw(
                    dispatch_expired_path, payload.size(),
                    anonsync::sha256_hex(payload), destination);
            const auto dispatch_expired_at =
                std::chrono::steady_clock::now();
            dispatch_expired_result = anonsync::
                send_one_sync_replica_file_delivery_tls_session_or_throw(
                    sender_service, payload_authority,
                    retained_client_context(),
                    {"127.0.0.1", socket.port},
                    {receiver_actor, receiver_pin},
                    "production-client-dispatch-expired", 30U,
                    {
                        dispatch_expired_at + std::chrono::seconds(5),
                        dispatch_expired_at + std::chrono::seconds(5),
                        dispatch_expired_at - std::chrono::milliseconds(1),
                        dispatch_expired_at + std::chrono::seconds(5),
                        dispatch_expired_at + std::chrono::seconds(5),
                    },
                    "TLS production client dispatch expiry");
            const auto after_dispatch_expiry = sender.snapshot_or_throw();
            dispatch_expired_ready_intent_remained_unclaimed =
                after_dispatch_expiry.outbox.size() == 1U &&
                after_dispatch_expiry.outbox.front().operation_id ==
                    dispatch_expired_operation.operation_id &&
                after_dispatch_expiry.outbox.front().lease.claim_id.empty() &&
                after_dispatch_expiry.outbox.front().lease.worker_id.empty() &&
                after_dispatch_expiry.outbox.front().lease.dispatch_attempts ==
                    0U;

            const auto expired =
                std::chrono::steady_clock::now() -
                std::chrono::milliseconds(1);
            expired_result = anonsync::
                send_one_sync_replica_file_delivery_tls_session_or_throw(
                    sender_service, payload_authority,
                    retained_client_context(),
                    {"127.0.0.1", socket.port},
                    {receiver_actor, receiver_pin},
                    "production-client-expired", 30U,
                    {expired, expired, expired, expired, expired},
                    "TLS production client pre-connect expiry");
        } catch (...) {
            client_failure = std::current_exception();
        }
    });

    const auto now = std::chrono::steady_clock::now();
    anonsync::SyncReplicaFileTlsServerResult server_result;
    anonsync::SyncReplicaFileTlsServerResult dispatch_expired_server_result;
    std::exception_ptr server_failure;
    try {
        server_result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener,
                anonsync::
                    retain_sync_replica_file_tls_server_context_or_throw(
                        server_context,
                        "TLS production client server context"),
                anchored_membership_owner.current_authority_or_throw(),
                {
                    now + std::chrono::seconds(5),
                    now + std::chrono::seconds(5),
                    now + std::chrono::seconds(5),
                    now + std::chrono::seconds(5),
                    now + std::chrono::seconds(5),
                },
                "TLS production client server session");

        const auto dispatch_server_now = std::chrono::steady_clock::now();
        dispatch_expired_server_result = anonsync::
            serve_one_sync_replica_file_delivery_tls_session_or_throw(
                receiver_service, listener,
                anonsync::
                    retain_sync_replica_file_tls_server_context_or_throw(
                        server_context,
                        "TLS production client dispatch-expiry server context"),
                anchored_membership_owner.current_authority_or_throw(),
                {
                    dispatch_server_now + std::chrono::seconds(5),
                    dispatch_server_now + std::chrono::seconds(5),
                    dispatch_server_now + std::chrono::seconds(5),
                    dispatch_server_now + std::chrono::seconds(5),
                    dispatch_server_now + std::chrono::seconds(5),
                },
                "TLS production client dispatch-expiry server session");
    } catch (...) {
        server_failure = std::current_exception();
    }
    client.join();
    if (server_failure) std::rethrow_exception(server_failure);
    if (client_failure) std::rethrow_exception(client_failure);

    require(
        client_result.disposition == anonsync::
                SyncReplicaFileTlsClientDisposition::ReceiptApplied &&
            client_result.socket_created &&
            client_result.socket_policy_verified &&
            client_result.connected && client_result.handshake_complete &&
            client_result.peer_authenticated &&
            client_result.connect_attempts == 1U &&
            client_result.handshake_attempts > 0U &&
            client_result.peer_spki_sha256 == receiver_pin &&
            client_result.peer_actor == receiver_actor &&
            client_result.claim_id.has_value() &&
            client_result.request_digest.has_value() &&
            client_result.request_prefix_bytes_written ==
                anonsync::kSyncReplicaTlsRecordPrefixBytes &&
            client_result.request_frame_bytes > payload.size() &&
            client_result.request_body_bytes_written ==
                client_result.request_frame_bytes &&
            client_result.receipt_prefix_bytes_received ==
                anonsync::kSyncReplicaTlsRecordPrefixBytes &&
            client_result.receipt_frame_bytes > 0U &&
            client_result.receipt_body_bytes_received ==
                client_result.receipt_frame_bytes &&
            client_result.receipt_apply_result == anonsync::
                SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled &&
            (client_result.shutdown_disposition == anonsync::
                 SyncReplicaFileTlsClientShutdownDisposition::
                     CloseNotifySent ||
             client_result.shutdown_disposition == anonsync::
                 SyncReplicaFileTlsClientShutdownDisposition::Complete) &&
            client_result.shutdown_attempts > 0U,
        "TLS production client did not preserve bounded sender terminal cutpoints");
    require(
        server_result.disposition == anonsync::
                SyncReplicaFileTlsServerDisposition::ReceiptSent &&
            server_result.peer_actor == sender_actor &&
            server_result.peer_spki_sha256 == sender_pin &&
            server_result.receive.has_value() &&
            server_result.receive->inbound.has_value(),
        "TLS production client did not compose with the accepted-session owner");
    require(
        sender_settled &&
            read_binary_file(workspace.files / relative_path) == payload,
        "TLS production client receipt preceded effect publication or settlement");
    require(
        dispatch_expired_result.disposition == anonsync::
                SyncReplicaFileTlsClientDisposition::
                    DispatchDeadlineExpired &&
            dispatch_expired_result.socket_created &&
            dispatch_expired_result.socket_policy_verified &&
            dispatch_expired_result.connected &&
            dispatch_expired_result.handshake_complete &&
            dispatch_expired_result.peer_authenticated &&
            dispatch_expired_result.peer_spki_sha256 == receiver_pin &&
            dispatch_expired_result.peer_actor == receiver_actor &&
            !dispatch_expired_result.operation_id.has_value() &&
            !dispatch_expired_result.claim_id.has_value() &&
            !dispatch_expired_result.request_digest.has_value() &&
            dispatch_expired_result.request_prefix_bytes_written == 0U &&
            dispatch_expired_result.request_frame_bytes == 0U &&
            dispatch_expired_result.request_body_bytes_written == 0U &&
            dispatch_expired_result.receipt_prefix_bytes_received == 0U &&
            dispatch_expired_result.receipt_frame_bytes == 0U &&
            dispatch_expired_result.receipt_body_bytes_received == 0U &&
            !dispatch_expired_result.receipt_apply_result.has_value() &&
            dispatch_expired_ready_intent_remained_unclaimed,
        "expired post-authentication request-admission cutpoint spent claim or "
        "application-byte authority");
    require(
        dispatch_expired_server_result.disposition == anonsync::
                SyncReplicaFileTlsServerDisposition::PeerClosed &&
            dispatch_expired_server_result.accepted &&
            dispatch_expired_server_result.accepted_socket_policy_verified &&
            dispatch_expired_server_result.handshake_complete &&
            dispatch_expired_server_result.peer_actor == sender_actor &&
            dispatch_expired_server_result.peer_spki_sha256 == sender_pin &&
            dispatch_expired_server_result.receive.has_value() &&
            dispatch_expired_server_result.receive->disposition == anonsync::
                SyncReplicaFileTlsReceiveDisposition::PeerClosed &&
            !dispatch_expired_server_result.receive->inbound.has_value() &&
            dispatch_expired_server_result.receive
                    ->request_prefix_bytes_received == 0U &&
            dispatch_expired_server_result.receive->request_frame_bytes == 0U &&
            dispatch_expired_server_result.receive
                    ->request_body_bytes_received == 0U &&
            !dispatch_expired_server_result.receive->receipt_write_started,
        "receiver did not observe the dispatch-expired authenticated client as "
        "an exact zero-application-byte close");
    const auto receiver_snapshot = receiver.snapshot_or_throw();
    require(
        receiver_snapshot.operation_set_digest == sender_operation_digest &&
            receiver_snapshot.evidence_set_digest == sender_evidence_digest &&
            receiver_snapshot.visible_state_digest == sender_visible_digest,
        "TLS production client path did not converge canonical replica evidence");
    require(
        expired_result.disposition == anonsync::
                SyncReplicaFileTlsClientDisposition::
                    ConnectDeadlineExpired &&
            !expired_result.socket_created &&
            expired_result.connect_attempts == 0U &&
            !expired_result.connected &&
            !expired_result.handshake_complete &&
            !expired_result.operation_id.has_value(),
        "TLS production client spent socket or claim authority after an expired connect cutpoint");
#else
    (void)client_context;
    (void)server_context;
    (void)sender_actor;
    (void)receiver_actor;
    (void)sender_pin;
    (void)receiver_pin;
    require(true, "bounded TLS production client owner requires Linux");
#endif
}

void test_mutual_tls13_delivery() {
#ifndef __unix__
    require(true, "TLS socketpair integration is not available on this platform");
#else
    const PkeyPtr ca_key = make_ed25519_key();
    const CertificatePtr ca_certificate = make_certificate(
        ca_key.get(), "anonsync-test-ca", 1L, nullptr, nullptr, true);
    const PkeyPtr sender_key = make_ed25519_key();
    const PkeyPtr receiver_key = make_ed25519_key();
    const CertificatePtr sender_certificate = make_certificate(
        sender_key.get(), "anonsync-test-sender", 2L,
        ca_certificate.get(), ca_key.get(), false);
    const CertificatePtr receiver_certificate = make_certificate(
        receiver_key.get(), "anonsync-test-receiver", 3L,
        ca_certificate.get(), ca_key.get(), false);
    const SslContextPtr client_context = make_tls_context(
        sender_certificate.get(), sender_key.get(), ca_certificate.get(), false);
    const SslContextPtr server_context = make_tls_context(
        receiver_certificate.get(), receiver_key.get(), ca_certificate.get(), true);
    TlsConnectionPair connection = make_tls_connection_pair(
        client_context.get(), server_context.get());

    const anonsync::SyncReplicaActor sender_actor{
        "device-tls-delivery-sender", 9101U};
    const anonsync::SyncReplicaActor receiver_actor{
        "device-tls-delivery-receiver", 9102U};
    const std::string sender_pin =
        certificate_spki_sha256(sender_certificate.get());
    const std::string receiver_pin =
        certificate_spki_sha256(receiver_certificate.get());

    test_tls_io_policy_profile_and_mutation_fences(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_tls_channel_retains_ssl_and_fences_affinity(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);

    test_tls_record_write_continuation(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_tls_record_read_continuation(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_tls_record_duplex_poll_owner(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_file_tls_dispatch_frontier(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_file_tls_receiver_exchange(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_reconciliation_tls_exchange(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_reconciliation_tls_source_manifest_preparing(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_reconciliation_tls_range_resume(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);

    test_tls_membership_snapshot_value_authority(
        sender_actor, receiver_actor, sender_pin);
    test_file_tls_server_session_owner(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);
    test_file_tls_client_session_owner(
        client_context.get(), server_context.get(), sender_actor,
        receiver_actor, sender_pin, receiver_pin);

    const SslContextPtr no_alpn_client_context = make_tls_context(
        sender_certificate.get(), sender_key.get(), ca_certificate.get(),
        false, false);
    const SslContextPtr no_alpn_server_context = make_tls_context(
        receiver_certificate.get(), receiver_key.get(), ca_certificate.get(),
        true, false);
    TlsConnectionPair no_alpn_connection = make_tls_connection_pair(
        no_alpn_client_context.get(), no_alpn_server_context.get());
    require_error(
        [&] {
            (void)anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                no_alpn_connection.client.get(),
                {receiver_actor, receiver_pin},
                "TLS transport missing ALPN");
        },
        "delivery ALPN",
        "TLS adapter accepted a certificate-valid connection for an unspecified application protocol");

    require(SSL_version(connection.client.get()) == TLS1_3_VERSION &&
                SSL_version(connection.server.get()) == TLS1_3_VERSION &&
                SSL_session_reused(connection.client.get()) == 0 &&
                SSL_session_reused(connection.server.get()) == 0,
            "test connection did not negotiate one fresh TLS 1.3 session");
    require(
        anonsync::sync_replica_tls_peer_spki_sha256_or_throw(
            connection.client.get()) == receiver_pin &&
        anonsync::sync_replica_tls_peer_spki_sha256_or_throw(
            connection.server.get()) == sender_pin,
        "TLS adapter did not observe the exact peer SPKI identities");

    SSL_set_verify(connection.client.get(), SSL_VERIFY_NONE, nullptr);
    require_error(
        [&] {
            (void)anonsync::sync_replica_tls_peer_spki_sha256_or_throw(
                connection.client.get(), "TLS transport disabled verifier");
        },
        "verification mode is disabled",
        "TLS adapter treated an unverified handshake result as authenticated");
    SSL_set_verify(connection.client.get(), SSL_VERIFY_PEER, nullptr);

    auto wrong_policy = anonsync::SyncReplicaTlsPeerPolicy{
        receiver_actor, std::string(64U, '0')};
    require_error(
        [&] {
            (void)anonsync::authenticate_sync_replica_tls13_channel_or_throw(
                connection.client.get(), wrong_policy,
                "TLS transport wrong pin");
        },
        "pin mismatch",
        "TLS adapter authorized a peer under the wrong membership pin");

    auto sender_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.client.get(), {receiver_actor, receiver_pin},
            "TLS transport sender channel");
    const auto receiver_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.server.get(), {sender_actor, sender_pin},
            "TLS transport receiver channel");
    require(sender_channel.delivery_context().peer_actor == receiver_actor &&
                receiver_channel.delivery_context().peer_actor == sender_actor &&
                sender_channel.delivery_context().binding ==
                    receiver_channel.delivery_context().binding &&
                sender_channel.delivery_context().binding.type == "tls-exporter",
            "TLS peers did not derive one role-independent RFC 9266 channel binding");

    SSL_set_verify(connection.client.get(), SSL_VERIFY_NONE, nullptr);
    require_error(
        [&] {
            anonsync::write_sync_replica_tls_record_or_throw(
                sender_channel, "verifier-probe", 64U,
                "TLS authenticated capability verifier recheck");
        },
        "peer-verification mode changed after authentication",
        "authenticated TLS capability stopped rechecking the live SSL security state");
    SSL_set_verify(connection.client.get(), SSL_VERIFY_PEER, nullptr);
    sender_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.client.get(), {receiver_actor, receiver_pin},
            "TLS transport replacement sender channel");

    TempDatabasePath sender_file("anonsync-tls-delivery-sender");
    TempDatabasePath receiver_file("anonsync-tls-delivery-receiver");
    const std::string folder = "folder-tls-delivery";
    const auto clock_state = std::make_shared<MutableClockState>();
    anonsync::SyncSqliteDb sender_db = open_database(sender_file.path);
    anonsync::SyncSqliteDb receiver_db = open_database(receiver_file.path);
    anonsync::SyncReplicaSqliteOwner sender(
        sender_db.db, folder, sender_actor, owner_limits(),
        "TLS delivery sender", make_clock(clock_state));
    anonsync::SyncReplicaSqliteOwner receiver(
        receiver_db.db, folder, receiver_actor, owner_limits(),
        "TLS delivery receiver", make_clock(clock_state));
    const auto limits = service_limits();
    anonsync::SyncReplicaDeliveryService sender_service(
        sender, limits, "TLS sender service");
    anonsync::SyncReplicaDeliveryService receiver_service(
        receiver, limits, "TLS receiver service");

    const std::vector<std::string> destination{
        receiver_actor.device_id};
    const auto operation = sender.create_local_file_or_throw(
        "tls/transport.bin", 17U,
        anonsync::sha256_hex("tls transport payload identity"),
        destination);
    clock_state->epoch = 200U;
    const auto outbound = sender_service.claim_next_request_or_throw(
        sender_channel.delivery_authority(), "tls-delivery-worker", 30U);
    require(outbound.has_value() && outbound->request.operation == operation,
            "TLS delivery service did not claim the canonical operation");

    anonsync::write_sync_replica_tls_record_or_throw(
        sender_channel, outbound->request_frame,
        limits.max_request_frame_bytes, "TLS request write");
    const std::string received_request =
        anonsync::read_sync_replica_tls_record_or_throw(
            receiver_channel, limits.max_request_frame_bytes,
            "TLS request read");
    require(received_request == outbound->request_frame,
            "TLS request framing did not preserve exact canonical bytes");
    const auto inbound = receiver_service.receive_request_or_throw(
        receiver_channel.delivery_authority(), received_request);
    require(inbound.admission == anonsync::SyncReplicaAdmission::InsertedActive,
            "TLS-bound request was not durably admitted by the receiver");

    anonsync::write_sync_replica_tls_record_or_throw(
        receiver_channel, inbound.receipt_frame,
        limits.max_receipt_frame_bytes, "TLS receipt write");
    const std::string received_receipt =
        anonsync::read_sync_replica_tls_record_or_throw(
            sender_channel, limits.max_receipt_frame_bytes,
            "TLS receipt read");
    require(received_receipt == inbound.receipt_frame,
            "TLS receipt framing did not preserve exact canonical bytes");
    clock_state->epoch = 201U;
    require(
        sender_service.apply_receipt_or_throw(
            sender_channel.delivery_authority(), outbound->request,
            received_receipt) ==
            anonsync::SyncReplicaDeliveryReceiptApplyResult::EvidenceSettled,
        "TLS-bound receiver receipt did not settle the exact sender attempt");

    const auto sender_snapshot = sender.snapshot_or_throw();
    const auto receiver_snapshot = receiver.snapshot_or_throw();
    require(sender_snapshot.outbox.empty() &&
                sender_snapshot.operation_set_digest ==
                    receiver_snapshot.operation_set_digest &&
                sender_snapshot.evidence_set_digest ==
                    receiver_snapshot.evidence_set_digest &&
                sender_snapshot.visible_state_digest ==
                    receiver_snapshot.visible_state_digest,
            "mutual TLS delivery did not converge canonical replica evidence");

    const auto original_binding =
        sender_channel.delivery_context().binding;
    replace_tls_stream_and_rehandshake(connection);
    require(SSL_session_reused(connection.client.get()) == 0 &&
                SSL_session_reused(connection.server.get()) == 0,
            "reset SSL objects did not complete a fresh TLS session");

    const auto post_handshake_operation = sender.create_local_file_or_throw(
        "tls/post-handshake.bin", 19U,
        anonsync::sha256_hex("post handshake payload identity"), destination);
    const auto before_stale_claim = sender.snapshot_or_throw();
    clock_state->epoch = 202U;
    require_error(
        [&] {
            (void)sender_service.claim_next_request_or_throw(
                sender_channel.delivery_authority(),
                "tls-stale-channel-worker", 30U);
        },
        "BIO changed after authentication",
        "stale TLS authority reached the durable outbox owner");
    require(sender.snapshot_or_throw() == before_stale_claim,
            "stale TLS authority changed the sender cutpoint or lease");
    require_error(
        [&] {
            anonsync::write_sync_replica_tls_record_or_throw(
                sender_channel, "stale-session", 64U,
                "TLS poisoned authenticated capability");
        },
        "poisoned",
        "failed live-session validation did not poison the old TLS capability");
    const auto refreshed_sender_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.client.get(), {receiver_actor, receiver_pin},
            "TLS transport refreshed sender channel");
    const auto refreshed_receiver_channel =
        anonsync::authenticate_sync_replica_tls13_channel_or_throw(
            connection.server.get(), {sender_actor, sender_pin},
            "TLS transport refreshed receiver channel");
    require(refreshed_sender_channel.delivery_context().binding ==
                refreshed_receiver_channel.delivery_context().binding &&
                refreshed_sender_channel.delivery_context().binding !=
                    original_binding,
            "fresh TLS handshake did not mint one new role-independent channel binding");
    clock_state->epoch = 203U;
    const auto post_handshake_claim =
        sender_service.claim_next_request_or_throw(
            refreshed_sender_channel.delivery_authority(),
            "tls-refreshed-channel-worker", 30U);
    require(post_handshake_claim.has_value() &&
                post_handshake_claim->request.operation ==
                    post_handshake_operation,
            "fresh TLS authority could not claim the intent preserved by stale-session rejection");

    anonsync::write_sync_replica_tls_record_or_throw(
        refreshed_sender_channel, "oversize", 64U,
        "TLS oversize fixture write");
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_tls_record_or_throw(
                refreshed_receiver_channel, 4U,
                "TLS oversize fixture read");
        },
        "above the configured limit",
        "TLS reader allocated or consumed an advertised over-limit frame");
    require_error(
        [&] {
            (void)anonsync::read_sync_replica_tls_record_or_throw(
                refreshed_receiver_channel, 64U,
                "TLS poisoned reader reuse");
        },
        "poisoned",
        "over-limit peer frame left the TLS byte stream reusable");
    require_error(
        [&] {
            anonsync::write_sync_replica_tls_record_or_throw(
                refreshed_sender_channel, {}, 64U,
                "TLS empty fixture write");
        },
        "must not be empty",
        "TLS writer accepted an empty delivery record");
#endif
}

}  // namespace

int main() {
    try {
        test_sigpipe_ignore_policy();
        checks += anonsync::test::
            run_sync_replica_tls_membership_sqlite_owner_tests();
        checks += anonsync::test::
            run_sync_replica_tls_membership_anchor_sqlite_owner_tests();
        test_mutual_tls13_delivery();
        std::cout << "sync replica TLS transport checks: " << checks << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica TLS transport test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
