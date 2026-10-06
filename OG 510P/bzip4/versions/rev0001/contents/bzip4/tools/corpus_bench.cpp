#include "bzip4/codec.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <span>
#include <string_view>
#include <vector>

namespace fs = std::filesystem;
using clock_type = std::chrono::steady_clock;

namespace {

std::vector<std::uint8_t> read_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("cannot open input: " + path.string());
    const auto end = input.tellg();
    if (end < 0) throw std::runtime_error("cannot determine input size");
    const auto size = static_cast<std::uintmax_t>(end);
    if (size > std::numeric_limits<std::size_t>::max()) throw std::runtime_error("input is too large for this host");
    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    input.seekg(0);
    if (!data.empty() && !input.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()))) {
        throw std::runtime_error("failed while reading input");
    }
    return data;
}

unsigned parse_unsigned(const char* text, const char* label) {
    unsigned value = 0;
    const std::string_view view(text);
    const auto [end, error] = std::from_chars(view.data(), view.data() + view.size(), value);
    if (error != std::errc{} || end != view.data() + view.size()) {
        throw std::runtime_error(std::string("invalid ") + label + ": " + text);
    }
    return value;
}

double seconds(const clock_type::duration duration) {
    return std::chrono::duration<double>(duration).count();
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2 || argc > 4) {
        std::cerr << "usage: bzip4_bench FILE [BLOCK_MIB=16] [ITERATIONS=3]\n";
        return 2;
    }

    try {
        const fs::path input_path = argv[1];
        const unsigned block_mib = argc >= 3 ? parse_unsigned(argv[2], "block MiB") : 16U;
        const unsigned iterations = argc >= 4 ? parse_unsigned(argv[3], "iteration count") : 3U;
        if (block_mib == 0 || block_mib > 511) throw std::runtime_error("block MiB must be in [1, 511]");
        if (iterations == 0 || iterations > 1000) throw std::runtime_error("iterations must be in [1, 1000]");

        const std::uint64_t block_bytes_u64 = static_cast<std::uint64_t>(block_mib) * 1024U * 1024U;
        if (block_bytes_u64 > static_cast<std::uint64_t>(std::numeric_limits<std::int32_t>::max())) {
            throw std::runtime_error("block size does not fit codec API");
        }
        const auto block_bytes = static_cast<std::size_t>(block_bytes_u64);
        const auto input = read_file(input_path);
        if (input.empty()) throw std::runtime_error("empty files have no block-level benchmark payload");

        double encode_total = 0.0;
        double decode_total = 0.0;
        std::size_t compressed_size = 0;
        std::size_t block_count = 0;

        for (unsigned iteration = 0; iteration < iterations; ++iteration) {
            bzip4::block_codec codec(static_cast<std::int32_t>(block_bytes));
            std::vector<std::vector<std::uint8_t>> encoded_blocks;
            std::vector<std::size_t> original_sizes;
            encoded_blocks.reserve((input.size() + block_bytes - 1) / block_bytes);
            original_sizes.reserve(encoded_blocks.capacity());

            const auto encode_start = clock_type::now();
            for (std::size_t offset = 0; offset < input.size(); offset += block_bytes) {
                const auto count = std::min(block_bytes, input.size() - offset);
                encoded_blocks.push_back(codec.encode(std::span(input).subspan(offset, count)));
                original_sizes.push_back(count);
            }
            const auto encode_end = clock_type::now();

            std::size_t offset = 0;
            const auto decode_start = clock_type::now();
            for (std::size_t index = 0; index < encoded_blocks.size(); ++index) {
                const auto decoded = codec.decode(encoded_blocks[index], original_sizes[index]);
                if (!std::equal(decoded.begin(), decoded.end(), input.begin() + static_cast<std::ptrdiff_t>(offset))) {
                    throw std::runtime_error("verification failed in block " + std::to_string(index));
                }
                offset += decoded.size();
            }
            const auto decode_end = clock_type::now();
            if (offset != input.size()) throw std::runtime_error("decoded byte count mismatch");

            encode_total += seconds(encode_end - encode_start);
            decode_total += seconds(decode_end - decode_start);
            if (iteration == 0) {
                for (const auto& block : encoded_blocks) compressed_size += block.size();
                block_count = encoded_blocks.size();
            }
        }

        constexpr double mib = 1024.0 * 1024.0;
        const double input_mib = static_cast<double>(input.size()) / mib;
        const double average_encode = encode_total / iterations;
        const double average_decode = decode_total / iterations;

        std::cout << std::fixed << std::setprecision(3)
                  << "file=" << input_path.string() << '\n'
                  << "codec_version=" << bzip4::codec_version() << '\n'
                  << "input_bytes=" << input.size() << '\n'
                  << "block_bytes=" << block_bytes << '\n'
                  << "blocks=" << block_count << '\n'
                  << "compressed_block_bytes=" << compressed_size << '\n'
                  << "compressed_over_input=" << (static_cast<double>(compressed_size) / input.size()) << '\n'
                  << "bits_per_input_byte=" << (8.0 * compressed_size / input.size()) << '\n'
                  << "encode_seconds_average=" << average_encode << '\n'
                  << "decode_seconds_average=" << average_decode << '\n'
                  << "encode_mib_per_second=" << (input_mib / average_encode) << '\n'
                  << "decode_mib_per_second=" << (input_mib / average_decode) << '\n'
                  << "iterations=" << iterations << '\n'
                  << "verified=true\n";
    } catch (const std::exception& error) {
        std::cerr << "bzip4_bench: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
