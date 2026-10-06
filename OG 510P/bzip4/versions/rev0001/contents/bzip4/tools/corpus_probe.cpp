#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace fs = std::filesystem;

namespace {

struct fingerprint {
    std::uint64_t first;
    std::uint64_t second;
    std::uint32_t length;

    bool operator==(const fingerprint&) const = default;
};

struct fingerprint_hash {
    std::size_t operator()(const fingerprint& value) const noexcept {
        std::uint64_t x = value.first ^ (value.second + 0x9e3779b97f4a7c15ULL + (value.first << 6U) + (value.first >> 2U));
        x ^= static_cast<std::uint64_t>(value.length) * 0x94d049bb133111ebULL;
        return static_cast<std::size_t>(x ^ (x >> 32U));
    }
};

struct seen_record {
    std::size_t count = 0;
    std::size_t first_offset = 0;
    std::size_t last_offset = 0;
};

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

fingerprint make_fingerprint(const std::span<const std::uint8_t> bytes) noexcept {
    std::uint64_t h1 = 1469598103934665603ULL;
    std::uint64_t h2 = 0x243f6a8885a308d3ULL;
    for (const std::uint8_t byte : bytes) {
        h1 ^= byte;
        h1 *= 1099511628211ULL;
        h2 ^= static_cast<std::uint64_t>(byte) + 0x9e3779b97f4a7c15ULL + (h2 << 6U) + (h2 >> 2U);
        h2 *= 0xbf58476d1ce4e5b9ULL;
    }
    return {h1, h2, static_cast<std::uint32_t>(bytes.size())};
}

bool textish(const std::span<const std::uint8_t> bytes) noexcept {
    if (bytes.empty()) return false;
    std::size_t accepted = 0;
    for (const auto byte : bytes) {
        if (byte == '\n' || byte == '\r' || byte == '\t' || (byte >= 0x20 && byte <= 0x7e)) ++accepted;
    }
    return static_cast<double>(accepted) / bytes.size() >= 0.85;
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: bzip4_probe FILE\n";
        return 2;
    }

    try {
        constexpr std::size_t chunk_size = 4096;
        const fs::path path = argv[1];
        const auto data = read_file(path);
        std::array<std::uint64_t, 256> frequencies{};
        for (const auto byte : data) ++frequencies[byte];

        double entropy = 0.0;
        if (!data.empty()) {
            for (const auto count : frequencies) {
                if (count == 0) continue;
                const double probability = static_cast<double>(count) / data.size();
                entropy -= probability * std::log2(probability);
            }
        }

        std::unordered_map<fingerprint, seen_record, fingerprint_hash> chunks;
        chunks.reserve((data.size() + chunk_size - 1) / chunk_size);
        std::size_t duplicate_chunks = 0;
        std::size_t duplicate_chunk_bytes = 0;
        std::size_t maximum_duplicate_distance = 0;
        for (std::size_t offset = 0; offset < data.size(); offset += chunk_size) {
            const auto count = std::min(chunk_size, data.size() - offset);
            const auto key = make_fingerprint(std::span(data).subspan(offset, count));
            auto [it, inserted] = chunks.try_emplace(key, seen_record{1, offset, offset});
            if (!inserted) {
                ++duplicate_chunks;
                duplicate_chunk_bytes += count;
                maximum_duplicate_distance = std::max(maximum_duplicate_distance, offset - it->second.last_offset);
                ++it->second.count;
                it->second.last_offset = offset;
            }
        }

        std::size_t line_count = 0;
        std::size_t duplicate_lines = 0;
        std::size_t duplicate_line_bytes = 0;
        const bool looks_textual = textish(data);
        if (looks_textual) {
            std::unordered_map<fingerprint, std::size_t, fingerprint_hash> lines;
            std::size_t start = 0;
            for (std::size_t index = 0; index <= data.size(); ++index) {
                if (index != data.size() && data[index] != '\n') continue;
                const auto count = index - start + (index < data.size() ? 1U : 0U);
                const auto key = make_fingerprint(std::span(data).subspan(start, count));
                auto [it, inserted] = lines.try_emplace(key, 1U);
                if (!inserted) {
                    ++duplicate_lines;
                    duplicate_line_bytes += count;
                    ++it->second;
                }
                ++line_count;
                start = index + 1;
            }
        }

        const std::size_t total_chunks = (data.size() + chunk_size - 1) / chunk_size;
        std::cout << std::fixed << std::setprecision(6)
                  << "file=" << path.string() << '\n'
                  << "input_bytes=" << data.size() << '\n'
                  << "shannon_entropy_bits_per_byte=" << entropy << '\n'
                  << "textish=" << (looks_textual ? "true" : "false") << '\n'
                  << "fixed_chunk_bytes=" << chunk_size << '\n'
                  << "fixed_chunks=" << total_chunks << '\n'
                  << "duplicate_fixed_chunks=" << duplicate_chunks << '\n'
                  << "duplicate_fixed_chunk_bytes=" << duplicate_chunk_bytes << '\n'
                  << "duplicate_fixed_chunk_fraction="
                  << (data.empty() ? 0.0 : static_cast<double>(duplicate_chunk_bytes) / data.size()) << '\n'
                  << "max_duplicate_chunk_gap_bytes=" << maximum_duplicate_distance << '\n'
                  << "lines=" << line_count << '\n'
                  << "duplicate_lines=" << duplicate_lines << '\n'
                  << "duplicate_line_bytes=" << duplicate_line_bytes << '\n'
                  << "duplicate_line_fraction="
                  << (data.empty() ? 0.0 : static_cast<double>(duplicate_line_bytes) / data.size()) << '\n'
                  << "fingerprint_collision_model=dual-64-bit-probabilistic\n";
    } catch (const std::exception& error) {
        std::cerr << "bzip4_probe: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
