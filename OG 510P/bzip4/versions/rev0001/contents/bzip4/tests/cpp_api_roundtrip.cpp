#include "bzip4/codec.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <span>
#include <string>
#include <utility>
#include <vector>

namespace {

std::vector<std::uint8_t> as_bytes(const std::string& text) {
    return {text.begin(), text.end()};
}

void round_trip(bzip4::block_codec& codec, const std::vector<std::uint8_t>& input, const char* label) {
    const auto encoded = codec.encode(input);
    const auto decoded = codec.decode(encoded, input.size());
    if (decoded != input) {
        std::cerr << "round-trip mismatch: " << label << '\n';
        std::exit(1);
    }
    std::cout << label << ": " << input.size() << " -> " << encoded.size() << " bytes\n";
}

void frame_round_trip(const std::vector<std::uint8_t>& input, const std::uint32_t block_size, const char* label) {
    std::vector<std::uint8_t> encoded(bz3_bound(input.size()) + 4096U);
    std::size_t encoded_size = encoded.size();
    const int encode_result = bz3_compress(block_size, input.data(), encoded.data(), input.size(), &encoded_size);
    if (encode_result != BZ3_OK) {
        std::cerr << "frame encode failed: " << label << " code=" << encode_result << '\n';
        std::exit(1);
    }
    encoded.resize(encoded_size);

    std::vector<std::uint8_t> decoded(input.size());
    std::size_t decoded_size = decoded.size();
    const int decode_result = bz3_decompress(encoded.data(), decoded.data(), encoded.size(), &decoded_size);
    if (decode_result != BZ3_OK || decoded_size != input.size() || decoded != input) {
        std::cerr << "frame round-trip mismatch: " << label << " code=" << decode_result
                  << " decoded_size=" << decoded_size << '\n';
        std::exit(1);
    }
    std::cout << label << ": " << input.size() << " -> " << encoded.size() << " frame bytes\n";
}

} // namespace

int main() {
    try {
        bzip4::block_codec codec(1024 * 1024);

        std::string source_like;
        source_like.reserve(600000);
        for (int i = 0; i < 6000; ++i) {
            source_like += "template<class T> constexpr T clamp_" + std::to_string(i % 17) +
                           "(T v,T lo,T hi){return v<lo?lo:v>hi?hi:v;} // repeated source corpus\n";
        }
        round_trip(codec, as_bytes(source_like), "source-like");

        std::vector<std::uint8_t> all_bytes;
        all_bytes.reserve(256 * 1024);
        for (int repeat = 0; repeat < 1024; ++repeat) {
            for (int value = 0; value < 256; ++value) {
                all_bytes.push_back(static_cast<std::uint8_t>(value));
            }
        }
        round_trip(codec, all_bytes, "all-byte-values");

        std::mt19937 generator(0xB2140001U);
        std::uniform_int_distribution<unsigned> distribution(0, 255);
        std::vector<std::uint8_t> random_data(300000);
        std::generate(random_data.begin(), random_data.end(), [&] {
            return static_cast<std::uint8_t>(distribution(generator));
        });
        round_trip(codec, random_data, "deterministic-random");

        std::vector<std::uint8_t> exact_block_random(1024U * 1024U);
        std::generate(exact_block_random.begin(), exact_block_random.end(), [&] {
            return static_cast<std::uint8_t>(distribution(generator));
        });
        frame_round_trip(exact_block_random, 1024U * 1024U, "frame-exact-block-random");

        std::vector<std::uint8_t> exact_block_repeated(1024U * 1024U, static_cast<std::uint8_t>('R'));
        frame_round_trip(exact_block_repeated, 1024U * 1024U, "frame-exact-block-repeated");

        bzip4::block_codec moved(std::move(codec));
        const auto tiny = as_bytes("move semantics remain usable");
        round_trip(moved, tiny, "moved-codec");

        if (std::string_view(bzip4::codec_version()) != "1.5.3") {
            std::cerr << "unexpected codec version: " << bzip4::codec_version() << '\n';
            return 1;
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
