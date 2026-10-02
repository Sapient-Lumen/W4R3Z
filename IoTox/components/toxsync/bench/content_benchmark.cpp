#include "toxsync/content_store.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {
using Clock = std::chrono::steady_clock;

[[nodiscard]] std::uint64_t parse_mib(int argc, char** argv) {
    if (argc == 1) return 128U;
    if (argc != 2) throw std::invalid_argument("usage: toxsync_content_bench [MiB]");
    std::uint64_t value{};
    const std::string_view text(argv[1]);
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() || value == 0U) {
        throw std::invalid_argument("benchmark MiB must be a positive integer");
    }
    return value;
}

void create_pattern_file(const std::filesystem::path& path, std::uint64_t bytes) {
    constexpr std::size_t buffer_bytes = 1024U * 1024U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create benchmark basis");
    std::uint64_t state = 0xcafef00dd15ea5e5ULL;
    std::uint64_t remaining = bytes;
    while (remaining != 0U) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, buffer_bytes));
        for (std::size_t index = 0U; index < count; ++index) {
            state ^= state << 13U;
            state ^= state >> 7U;
            state ^= state << 17U;
            buffer[index] = static_cast<std::byte>(state & 0xffU);
        }
        output.write(reinterpret_cast<const char*>(buffer.get()),
                     static_cast<std::streamsize>(count));
        if (!output) throw std::runtime_error("cannot write benchmark basis");
        remaining -= count;
    }
}

void create_prefixed_target(const std::filesystem::path& basis,
                            const std::filesystem::path& target,
                            std::uint64_t basis_bytes) {
    constexpr std::size_t buffer_bytes = 1024U * 1024U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    std::ifstream input(basis, std::ios::binary);
    std::ofstream output(target, std::ios::binary | std::ios::trunc);
    if (!input || !output) throw std::runtime_error("cannot create benchmark target");
    constexpr std::size_t prefix_bytes = 12345U;
    for (std::size_t index = 0U; index < prefix_bytes; ++index) {
        buffer[index] = static_cast<std::byte>((index * 131U + 17U) & 0xffU);
    }
    output.write(reinterpret_cast<const char*>(buffer.get()),
                 static_cast<std::streamsize>(prefix_bytes));
    std::uint64_t copied{};
    while (copied < basis_bytes) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(basis_bytes - copied, buffer_bytes));
        input.read(reinterpret_cast<char*>(buffer.get()), static_cast<std::streamsize>(count));
        if (static_cast<std::size_t>(input.gcount()) != count) {
            throw std::runtime_error("benchmark basis ended early");
        }
        output.write(reinterpret_cast<const char*>(buffer.get()),
                     static_cast<std::streamsize>(count));
        if (!output) throw std::runtime_error("cannot write benchmark target");
        copied += count;
    }
}

[[nodiscard]] double seconds(Clock::time_point start, Clock::time_point end) {
    return std::chrono::duration<double>(end - start).count();
}

[[nodiscard]] double mib_per_second(std::uint64_t bytes, double elapsed) {
    return elapsed == 0.0 ? 0.0
                          : static_cast<double>(bytes) / (1024.0 * 1024.0) / elapsed;
}

[[nodiscard]] std::uint64_t peak_rss_kib() {
#if defined(__linux__)
    std::ifstream status("/proc/self/status");
    std::string key;
    while (status >> key) {
        if (key == "VmHWM:") {
            std::uint64_t value{};
            std::string unit;
            status >> value >> unit;
            return value;
        }
        std::string rest;
        std::getline(status, rest);
    }
#endif
    return 0U;
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto mib = parse_mib(argc, argv);
        constexpr std::uint64_t unit = 1024U * 1024U;
        if (mib > std::numeric_limits<std::uint64_t>::max() / unit) {
            throw std::overflow_error("benchmark size overflow");
        }
        const auto basis_bytes = mib * unit;
        const auto stamp = Clock::now().time_since_epoch().count();
        const auto root = std::filesystem::temp_directory_path() /
            ("toxsync-content-bench-" + std::to_string(stamp));
        std::filesystem::create_directories(root);
        struct Cleanup {
            std::filesystem::path path;
            ~Cleanup() { std::error_code ignored; std::filesystem::remove_all(path, ignored); }
        } cleanup{root};

        create_pattern_file(root / "basis", basis_bytes);
        create_prefixed_target(root / "basis", root / "target", basis_bytes);
        const auto target_bytes = std::filesystem::file_size(root / "target");

        toxsync::ContentStoreOptions options;
        options.fsync_on_commit = false;
        options.verify_existing_chunks = false;
        toxsync::ContentStoreWorkspace workspace;

        const auto basis_start = Clock::now();
        const auto basis = toxsync::build_content_store(
            root / "basis", root / "store", root / "basis.txc", workspace, options);
        const auto basis_end = Clock::now();
        const auto target_start = Clock::now();
        const auto target = toxsync::build_content_store(
            root / "target", root / "store", root / "target.txc", workspace, options);
        const auto target_end = Clock::now();

        toxsync::ContentReconstructOptions reconstruct_options;
        reconstruct_options.fsync_on_commit = false;
        const auto reconstruct_start = Clock::now();
        const auto reconstructed = toxsync::reconstruct_content_manifest(
            root / "target.txc", root / "store", root / "output", workspace,
            reconstruct_options);
        const auto reconstruct_end = Clock::now();

        const auto basis_seconds = seconds(basis_start, basis_end);
        const auto target_seconds = seconds(target_start, target_end);
        const auto reconstruct_seconds = seconds(reconstruct_start, reconstruct_end);
        const bool valid = reconstructed.metadata.artifact_digest ==
                               target.metadata.artifact_digest &&
                           std::filesystem::file_size(root / "output") == target_bytes;

        std::cout << std::fixed << std::setprecision(3)
                  << "engine=toxsync-content-store-v2-flat\n"
                  << "basis-bytes=" << basis_bytes << '\n'
                  << "target-bytes=" << target_bytes << '\n'
                  << "chunk-min=" << options.chunking.min_bytes << '\n'
                  << "chunk-average=" << options.chunking.average_bytes << '\n'
                  << "chunk-max=" << options.chunking.max_bytes << '\n'
                  << "basis-chunks=" << basis.metadata.chunk_count << '\n'
                  << "target-chunks=" << target.metadata.chunk_count << '\n'
                  << "basis-build-mib-per-second="
                  << mib_per_second(basis_bytes, basis_seconds) << '\n'
                  << "target-build-mib-per-second="
                  << mib_per_second(target_bytes, target_seconds) << '\n'
                  << "reconstruct-mib-per-second="
                  << mib_per_second(target_bytes, reconstruct_seconds) << '\n'
                  << "target-created-bytes=" << target.bytes_created << '\n'
                  << "target-reused-bytes=" << target.bytes_reused << '\n'
                  << "target-reuse-percent="
                  << static_cast<double>(target.bytes_reused) * 100.0 /
                         static_cast<double>(target_bytes) << '\n'
                  << "workspace-resident-bytes=" << workspace.resident_bytes() << '\n'
                  << "peak-rss-kib=" << peak_rss_kib() << '\n'
                  << "verified=" << (valid ? 1 : 0) << '\n';
        return valid ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "toxsync_content_bench: " << error.what() << '\n';
        return 1;
    }
}
