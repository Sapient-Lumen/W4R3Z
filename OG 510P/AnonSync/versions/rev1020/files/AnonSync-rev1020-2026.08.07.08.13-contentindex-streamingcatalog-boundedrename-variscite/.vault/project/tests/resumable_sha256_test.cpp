#include "resumable_sha256.hpp"
#include "sha256_digest.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Exception, typename Callable>
void require_throws(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const Exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected diagnostic: " + error.what());
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

std::string deterministic_bytes(std::size_t count) {
    std::string bytes(count, '\0');
    std::uint64_t state = 0xd1b54a32d192ed03ULL;
    for (char& byte : bytes) {
        state ^= state >> 12U;
        state ^= state << 25U;
        state ^= state >> 27U;
        state *= 0x2545f4914f6cdd1dULL;
        byte = static_cast<char>((state >> 37U) & 0xffU);
    }
    return bytes;
}

void require_digest(
    std::string_view bytes,
    std::string_view expected,
    const std::string& label) {
    anonsync::ResumableSha256 digest;
    digest.update(bytes);
    require(digest.finish_hex() == expected, label + " digest changed");
}

void test_standard_vectors() {
    require_digest(
        "",
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855",
        "empty SHA-256 vector");
    require_digest(
        "abc",
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad",
        "abc SHA-256 vector");
    require_digest(
        "abcdbcdecdefdefgefghfghighijhijk"
        "ijkljklmklmnlmnomnopnopq",
        "248d6a61d20638b8e5c026930c3e6039"
        "a33ce45964ff2167f6ecedd419db06c1",
        "multi-block SHA-256 vector");

    std::string million_a(1000000U, 'a');
    require_digest(
        million_a,
        "cdc76e5c9914fb9281a1c7e284d73e67"
        "f1809a48a497200e046d39ccc7112cd0",
        "million-a SHA-256 vector");
}

void test_chunking_and_provider_oracle() {
    const std::string bytes = deterministic_bytes(8193U);
    const std::string oracle = anonsync::sha256_hex(bytes);

    for (const std::size_t chunk :
         std::array<std::size_t, 15U>{
             1U, 2U, 3U, 7U, 31U, 55U, 56U, 63U,
             64U, 65U, 127U, 1024U, 4095U, 4096U, 8193U}) {
        anonsync::ResumableSha256 digest;
        for (std::size_t offset = 0U; offset < bytes.size();) {
            const std::size_t count =
                std::min(chunk, bytes.size() - offset);
            digest.update(std::string_view(bytes).substr(offset, count));
            offset += count;
        }
        require(
            digest.finish_hex() == oracle,
            "chunked resumable SHA-256 diverged at chunk " +
                std::to_string(chunk));
    }

    for (const std::size_t split :
         std::array<std::size_t, 17U>{
             0U, 1U, 2U, 54U, 55U, 56U, 57U, 62U, 63U,
             64U, 65U, 119U, 120U, 127U, 128U, 4096U, 8193U}) {
        anonsync::ResumableSha256 first;
        first.update(std::string_view(bytes).substr(0U, split));
        const auto checkpoint = first.checkpoint();
        require(
            checkpoint.total_bytes == split,
            "checkpoint total byte count changed at split " +
                std::to_string(split));
        require(
            checkpoint.buffered_bytes == split % 64U,
            "checkpoint buffered byte count changed at split " +
                std::to_string(split));

        anonsync::ResumableSha256 resumed(checkpoint);
        resumed.update(std::string_view(bytes).substr(split));
        require(
            resumed.finish_hex() == oracle,
            "resumed SHA-256 diverged at split " + std::to_string(split));
    }
}


void test_fixed_width_terminal_form() {
    static constexpr std::string_view kExpected =
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad";

    anonsync::ResumableSha256 binary_digest;
    binary_digest.update("abc");
    const std::array<std::uint8_t, 32U> binary =
        binary_digest.finish_binary_array();
    require(
        anonsync::Sha256DigestValue(binary).equals_lowercase_hex(kExpected),
        "fixed-width binary SHA-256 terminal form changed");
    require_throws<std::logic_error>(
        [&] { (void)binary_digest.finish_binary_array(); },
        "already finished",
        "fixed-width binary digest finalized twice");

    anonsync::ResumableSha256 hex_digest;
    hex_digest.update("abc");
    const std::array<char, 64U> fixed = hex_digest.finish_hex_array();
    require(
        std::string_view(fixed.data(), fixed.size()) == kExpected,
        "fixed-width SHA-256 terminal form changed");
    require_throws<std::logic_error>(
        [&] { (void)hex_digest.finish_hex_array(); },
        "already finished",
        "fixed-width hexadecimal digest finalized twice");
}

void test_checkpoint_validation_and_single_use() {
    anonsync::ResumableSha256 fresh;
    const auto initial = fresh.checkpoint();
    require(initial.total_bytes == 0U, "initial checkpoint has bytes");
    require(initial.buffered_bytes == 0U, "initial checkpoint has a tail");
    require(
        std::all_of(
            initial.buffered_block.begin(), initial.buffered_block.end(),
            [](std::uint8_t byte) { return byte == 0U; }),
        "initial checkpoint has noncanonical buffer bytes");

    auto invalid_count = initial;
    invalid_count.buffered_bytes = 64U;
    require_throws<std::invalid_argument>(
        [&] {
            anonsync::ResumableSha256 rejected(invalid_count, "bad count");
            (void)rejected;
        },
        "buffered-byte count",
        "64-byte tail was accepted");

    auto invalid_modulo = initial;
    invalid_modulo.total_bytes = 1U;
    require_throws<std::invalid_argument>(
        [&] {
            anonsync::ResumableSha256 rejected(invalid_modulo, "bad modulo");
            (void)rejected;
        },
        "does not match",
        "inconsistent total/tail checkpoint was accepted");

    auto invalid_unused = initial;
    invalid_unused.buffered_block[63U] = 1U;
    require_throws<std::invalid_argument>(
        [&] {
            anonsync::ResumableSha256 rejected(invalid_unused, "bad unused");
            (void)rejected;
        },
        "noncanonical",
        "noncanonical unused buffer byte was accepted");

    auto maximum = initial;
    maximum.total_bytes = anonsync::kSha256MaximumMessageBytes;
    maximum.buffered_bytes = 63U;
    std::fill_n(maximum.buffered_block.begin(), 63U, 0x5aU);
    anonsync::ResumableSha256 at_maximum(maximum, "maximum checkpoint");
    require_throws<std::length_error>(
        [&] { at_maximum.update("x"); },
        "ceiling",
        "message-length overflow was accepted");

    anonsync::ResumableSha256 finished;
    finished.update("abc");
    require(
        finished.finish_hex() == anonsync::sha256_hex("abc"),
        "single-use fixture digest changed");
    require_throws<std::logic_error>(
        [&] { finished.update("x"); },
        "already finished",
        "finished digest accepted another update");
    require_throws<std::logic_error>(
        [&] { (void)finished.checkpoint(); },
        "already finished",
        "finished digest exposed a checkpoint");
    require_throws<std::logic_error>(
        [&] { (void)finished.finish_hex(); },
        "already finished",
        "finished digest finalized twice");

    require_throws<std::invalid_argument>(
        [&] {
            anonsync::validate_resumable_sha256_checkpoint_or_throw(
                initial, "");
        },
        "label",
        "empty checkpoint label was accepted");
}

}  // namespace

int main() {
    try {
        test_standard_vectors();
        test_chunking_and_provider_oracle();
        test_fixed_width_terminal_form();
        test_checkpoint_validation_and_single_use();
        std::cout << "resumable SHA-256 checks: " << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "resumable SHA-256 test failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}
