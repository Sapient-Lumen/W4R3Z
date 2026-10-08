#include "sync_replica_tls_io_policy.hpp"

#include <cstdint>
#include <exception>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

#include <openssl/ssl.h>

namespace {

using Context = std::unique_ptr<SSL_CTX, decltype(&SSL_CTX_free)>;
using Ssl = std::unique_ptr<SSL, decltype(&SSL_free)>;

static_assert(std::is_trivially_copyable_v<
              anonsync::detail::SyncReplicaTlsIoPolicy>);
static_assert(std::is_nothrow_move_constructible_v<
              anonsync::detail::SyncReplicaTlsIoPolicy>);

struct TestState final {
    std::uint64_t passed = 0U;
    std::uint64_t failed = 0U;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

template <typename Function>
void require_throws_containing(
    TestState& test,
    Function&& function,
    const std::string& expected,
    const std::string& label) {
    try {
        function();
        test.require(false, label + " (no exception)");
    } catch (const std::exception& error) {
        test.require(
            std::string(error.what()).find(expected) != std::string::npos,
            label + " (unexpected exception: " + error.what() + ")");
    }
}

[[nodiscard]] Context make_context() {
    Context context(SSL_CTX_new(TLS_method()), SSL_CTX_free);
    if (!context) {
        throw std::runtime_error("TLS I/O policy test could not create SSL_CTX");
    }
    return context;
}

struct SafeSsl final {
    Context context;
    Ssl ssl;
};

[[nodiscard]] SafeSsl make_safe_ssl(const std::string& label) {
    Context context = make_context();
    anonsync::detail::configure_sync_replica_tls_io_policy_or_throw(
        context.get(), label + " context");
    SSL_CTX_set_verify(context.get(), SSL_VERIFY_PEER, nullptr);
    Ssl ssl(SSL_new(context.get()), SSL_free);
    if (!ssl) {
        throw std::runtime_error(label + " could not create SSL");
    }
    return {std::move(context), std::move(ssl)};
}

void test_context_normalization(TestState& test) {
    Context context = make_context();
    (void)SSL_CTX_set_options(
        context.get(), SSL_OP_IGNORE_UNEXPECTED_EOF);
    (void)SSL_CTX_clear_mode(context.get(), SSL_MODE_AUTO_RETRY);
    (void)SSL_CTX_set_mode(context.get(), SSL_MODE_ASYNC);
    SSL_CTX_set_read_ahead(context.get(), 1);
    SSL_CTX_set_quiet_shutdown(context.get(), 1);

    anonsync::detail::configure_sync_replica_tls_io_policy_or_throw(
        context.get(), "context normalization");
    test.require(
        (SSL_CTX_get_options(context.get()) &
         SSL_OP_IGNORE_UNEXPECTED_EOF) == 0U,
        "context profile restores strict unexpected-EOF semantics");
    test.require(
        (SSL_CTX_get_mode(context.get()) & SSL_MODE_AUTO_RETRY) != 0L,
        "context profile requires AUTO_RETRY");
    test.require(
        (SSL_CTX_get_mode(context.get()) & SSL_MODE_ASYNC) == 0L,
        "context profile rejects asynchronous-engine retry");
    test.require(
        SSL_CTX_get_read_ahead(context.get()) == 0,
        "context profile disables read ahead");
    test.require(
        SSL_CTX_get_quiet_shutdown(context.get()) == 0,
        "context profile disables quiet shutdown");
}

void test_capture_and_exact_reproof(TestState& test) {
    SafeSsl fixture = make_safe_ssl("safe policy");
    const auto policy =
        anonsync::detail::capture_sync_replica_tls_io_policy_or_throw(
            fixture.ssl.get(), "safe policy capture");
    test.require(
        (policy.options & SSL_OP_IGNORE_UNEXPECTED_EOF) == 0U,
        "capture preserves strict unexpected-EOF semantics");
    test.require(
        (policy.modes & SSL_MODE_AUTO_RETRY) != 0L,
        "capture preserves AUTO_RETRY");
    test.require(
        (policy.modes & SSL_MODE_ASYNC) == 0L,
        "capture preserves socket-only readiness semantics");
    test.require(policy.read_ahead == 0, "capture preserves no read ahead");
    test.require(
        policy.quiet_shutdown == 0,
        "capture preserves close_notify evidence requirement");
    test.require(
        (policy.verify_mode & SSL_VERIFY_PEER) != 0,
        "capture preserves peer-verification mode");
    test.require(
        policy.shutdown_state == 0,
        "capture requires a live zero-shutdown frontier");

    anonsync::detail::reprove_sync_replica_tls_io_policy_or_throw(
        fixture.ssl.get(), policy, "unchanged policy");
    test.require(true, "unchanged exact policy reproves");
}

void test_unsafe_capture_rejection(TestState& test) {
    {
        SafeSsl fixture = make_safe_ssl("unexpected EOF rejection");
        (void)SSL_set_options(
            fixture.ssl.get(), SSL_OP_IGNORE_UNEXPECTED_EOF);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "unexpected EOF rejection");
            },
            "SSL_OP_IGNORE_UNEXPECTED_EOF",
            "capture rejects abrupt-close laundering");
    }
    {
        SafeSsl fixture = make_safe_ssl("AUTO_RETRY rejection");
        (void)SSL_clear_mode(fixture.ssl.get(), SSL_MODE_AUTO_RETRY);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "AUTO_RETRY rejection");
            },
            "SSL_MODE_AUTO_RETRY",
            "capture rejects weakened retry semantics");
    }
    {
        SafeSsl fixture = make_safe_ssl("ASYNC rejection");
        (void)SSL_set_mode(fixture.ssl.get(), SSL_MODE_ASYNC);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "ASYNC rejection");
            },
            "SSL_MODE_ASYNC",
            "capture rejects unowned asynchronous-engine readiness");
    }
    {
        SafeSsl fixture = make_safe_ssl("read-ahead rejection");
        SSL_set_read_ahead(fixture.ssl.get(), 1);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "read-ahead rejection");
            },
            "read-ahead",
            "capture rejects read-ahead state expansion");
    }
    {
        SafeSsl fixture = make_safe_ssl("quiet-shutdown rejection");
        SSL_set_quiet_shutdown(fixture.ssl.get(), 1);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "quiet-shutdown rejection");
            },
            "quiet TLS shutdown",
            "capture rejects synthetic clean closure");
    }
    {
        SafeSsl fixture = make_safe_ssl("verification rejection");
        SSL_set_verify(fixture.ssl.get(), SSL_VERIFY_NONE, nullptr);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "verification rejection");
            },
            "verification mode is disabled",
            "capture rejects missing peer verification");
    }
    {
        SafeSsl fixture = make_safe_ssl("shutdown rejection");
        SSL_set_shutdown(fixture.ssl.get(), SSL_SENT_SHUTDOWN);
        require_throws_containing(
            test,
            [&] {
                (void)anonsync::detail::
                    capture_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), "shutdown rejection");
            },
            "shutdown state is already nonzero",
            "capture rejects forged shutdown evidence");
    }
}

void test_post_capture_mutation_rejection(TestState& test) {
    using Mutator = void (*)(SSL*);
    const auto set_option = +[](SSL* ssl) {
        (void)SSL_set_options(ssl, SSL_OP_IGNORE_UNEXPECTED_EOF);
    };
    const auto clear_auto_retry = +[](SSL* ssl) {
        (void)SSL_clear_mode(ssl, SSL_MODE_AUTO_RETRY);
    };
    const auto set_read_ahead = +[](SSL* ssl) {
        SSL_set_read_ahead(ssl, 1);
    };
    const auto set_quiet_shutdown = +[](SSL* ssl) {
        SSL_set_quiet_shutdown(ssl, 1);
    };
    const auto change_verify = +[](SSL* ssl) {
        SSL_set_verify(
            ssl, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, nullptr);
    };
    const auto set_shutdown = +[](SSL* ssl) {
        SSL_set_shutdown(ssl, SSL_RECEIVED_SHUTDOWN);
    };

    struct Case final {
        const char* label;
        Mutator mutate;
        const char* expected;
    };
    const Case cases[] = {
        {"option mask", set_option, "option mask changed"},
        {"mode mask", clear_auto_retry, "mode mask changed"},
        {"read ahead", set_read_ahead, "read-ahead policy changed"},
        {"quiet shutdown", set_quiet_shutdown,
         "quiet-shutdown policy changed"},
        {"verification mode", change_verify,
         "peer-verification mode changed"},
        {"shutdown state", set_shutdown, "shutdown state changed"},
    };

    for (const Case& entry : cases) {
        SafeSsl fixture = make_safe_ssl(entry.label);
        const auto policy =
            anonsync::detail::capture_sync_replica_tls_io_policy_or_throw(
                fixture.ssl.get(), std::string(entry.label) + " capture");
        entry.mutate(fixture.ssl.get());
        require_throws_containing(
            test,
            [&] {
                anonsync::detail::
                    reprove_sync_replica_tls_io_policy_or_throw(
                        fixture.ssl.get(), policy,
                        std::string(entry.label) + " reproof");
            },
            entry.expected,
            std::string("exact reproof rejects ") + entry.label +
                " mutation");
    }
}

void test_null_handles_fail_closed(TestState& test) {
    require_throws_containing(
        test,
        [] {
            anonsync::detail::configure_sync_replica_tls_io_policy_or_throw(
                nullptr, "null context");
        },
        "SSL_CTX handle is null",
        "configuration rejects null context");
    require_throws_containing(
        test,
        [] {
            (void)anonsync::detail::
                capture_sync_replica_tls_io_policy_or_throw(
                    nullptr, "null capture");
        },
        "SSL handle is null",
        "capture rejects null SSL");

    SafeSsl fixture = make_safe_ssl("null reproof");
    const auto policy =
        anonsync::detail::capture_sync_replica_tls_io_policy_or_throw(
            fixture.ssl.get(), "null reproof capture");
    require_throws_containing(
        test,
        [&] {
            anonsync::detail::reprove_sync_replica_tls_io_policy_or_throw(
                nullptr, policy, "null reproof");
        },
        "SSL handle is null",
        "reproof rejects null SSL");
}

}  // namespace

int main() {
    TestState test;
    try {
        test_context_normalization(test);
        test_capture_and_exact_reproof(test);
        test_unsafe_capture_rejection(test);
        test_post_capture_mutation_rejection(test);
        test_null_handles_fail_closed(test);
    } catch (const std::exception& error) {
        std::cerr << "UNCAUGHT: " << error.what() << "\n";
        return 2;
    }

    std::cout << "sync replica TLS I/O policy checks: " << test.passed << "\n";
    return test.failed == 0U ? 0 : 1;
}
