#include "sha256_digest.hpp"
#include "sync_peer_transport_digest_bound_frame.hpp"

#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

namespace {

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Exception, typename Fn>
void require_throws(Fn&& fn, const std::string& message, int& checks) {
    bool threw_expected = false;
    try {
        fn();
    } catch (const Exception&) {
        threw_expected = true;
    } catch (const std::exception& error) {
        throw std::runtime_error(
            message + ": wrong exception type: " + error.what());
    }
    require(threw_expected, message, checks);
}

}  // namespace

int main() {
    try {
        using namespace anonsync;
        int checks = 0;

        static_assert(!std::is_default_constructible_v<
                      SyncPeerTransportDigestBoundFrame>);
        static_assert(!std::is_copy_constructible_v<
                      SyncPeerTransportDigestBoundFrame>);
        static_assert(!std::is_copy_assignable_v<
                      SyncPeerTransportDigestBoundFrame>);
        static_assert(std::is_nothrow_move_constructible_v<
                      SyncPeerTransportDigestBoundFrame>);
        static_assert(std::is_nothrow_move_assignable_v<
                      SyncPeerTransportDigestBoundFrame>);

        static constexpr char kBinaryFrame[] =
            "frame\0with" "\xff" "binary";
        const std::string binary_frame(
            kBinaryFrame, sizeof(kBinaryFrame) - 1U);
        const std::string expected = sha256_hex(binary_frame);
        SyncPeerTransportDigestBoundFrame bound =
            SyncPeerTransportDigestBoundFrame::bind(
                expected, binary_frame, binary_frame.size());
        require(bound.expected_sha256() == expected,
                "bound frame preserves pre-transmission digest authority",
                checks);
        require(bound.observed_sha256() == expected,
                "bound frame publishes the digest of exact received bytes",
                checks);
        require(bound.bytes() == binary_frame,
                "bound frame preserves binary received bytes exactly",
                checks);
        require(bound.byte_count() == binary_frame.size(),
                "bound frame publishes exact received byte count", checks);

        SyncPeerTransportDigestBoundFrame moved = std::move(bound);
        require(moved.bytes() == binary_frame &&
                    moved.expected_sha256() == expected &&
                    moved.observed_sha256() == expected,
                "move transfers the verified frame capability without loss",
                checks);

        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    std::string(64, 'A'), "frame", 5);
            },
            "uppercase expected digest is not canonical authority", checks);
        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    std::string(63, 'a'), "frame", 5);
            },
            "short expected digest is rejected", checks);
        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    sha256_hex("frame"), "frame", 0);
            },
            "zero frame budget is rejected before hashing", checks);
        require_throws<std::invalid_argument>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    sha256_hex(""), "", 1);
            },
            "empty received observation is rejected", checks);
        require_throws<std::length_error>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    sha256_hex("frame"), "frame", 4);
            },
            "over-budget received bytes are rejected", checks);
        require_throws<std::runtime_error>(
            [&] {
                (void)SyncPeerTransportDigestBoundFrame::bind(
                    sha256_hex("sender-frame"), "received-frame", 64);
            },
            "digest mismatch cannot be promoted to checked authority", checks);

        std::cout << "sync peer transport digest-bound frame tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync peer transport digest-bound frame tests failed: "
                  << error.what() << '\n';
        return 1;
    }
}
