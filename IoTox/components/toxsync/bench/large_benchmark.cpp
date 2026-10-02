#include "toxsync/index_file.hpp"
#include "toxsync/range_source.hpp"
#include "toxsync/streaming.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

[[nodiscard]] std::uint64_t parse_mib(int argc, char** argv) {
    if (argc == 1) return 256U;
    if (argc != 2) throw std::invalid_argument("usage: toxsync_large_bench [MiB]");
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
    if (!output) throw std::runtime_error("cannot create benchmark target");
    std::uint64_t state = 0x9e3779b97f4a7c15ULL;
    std::uint64_t remaining = bytes;
    while (remaining != 0U) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, buffer_bytes));
        for (std::size_t i = 0; i < count; ++i) {
            state ^= state << 13U;
            state ^= state >> 7U;
            state ^= state << 17U;
            buffer[i] = static_cast<std::byte>(state & 0xffU);
        }
        output.write(reinterpret_cast<const char*>(buffer.get()),
                     static_cast<std::streamsize>(count));
        if (!output) throw std::runtime_error("cannot write benchmark target");
        remaining -= count;
    }
}

void mutate_basis(const std::filesystem::path& path, std::uint64_t bytes) {
    std::fstream file(path, std::ios::binary | std::ios::in | std::ios::out);
    if (!file) throw std::runtime_error("cannot open benchmark basis");
    constexpr std::uint64_t stride = 4ULL * 1024ULL * 1024ULL;
    for (std::uint64_t offset = 4096U; offset < bytes; offset += stride) {
        file.seekp(static_cast<std::streamoff>(offset), std::ios::beg);
        const char value = static_cast<char>(0xa5);
        file.write(&value, 1);
        if (!file) throw std::runtime_error("cannot mutate benchmark basis");
    }
}

[[nodiscard]] double seconds(std::chrono::steady_clock::time_point begin,
                             std::chrono::steady_clock::time_point end) {
    return std::chrono::duration<double>(end - begin).count();
}

[[nodiscard]] double mib_per_second(std::uint64_t bytes, double elapsed) {
    return static_cast<double>(bytes) / (1024.0 * 1024.0) / elapsed;
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto mib = parse_mib(argc, argv);
        if (mib > std::numeric_limits<std::uint64_t>::max() / (1024U * 1024U)) {
            throw std::overflow_error("benchmark size overflow");
        }
        const auto bytes = mib * 1024U * 1024U;
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        const auto root = std::filesystem::temp_directory_path() /
            ("toxsync-large-bench-" + std::to_string(stamp));
        std::filesystem::create_directories(root);
        struct Cleanup {
            std::filesystem::path path;
            ~Cleanup() { std::error_code ignored; std::filesystem::remove_all(path, ignored); }
        } cleanup{root};

        create_pattern_file(root / "target", bytes);
        std::filesystem::copy_file(root / "target", root / "basis");
        mutate_basis(root / "basis", bytes);

        toxsync::IndexFileBuildOptions build_options;
        build_options.fsync_on_commit = false;
        const auto build_begin = std::chrono::steady_clock::now();
        const auto build = toxsync::build_index_file(
            root / "target", root / "target.txi", build_options);
        const auto build_end = std::chrono::steady_clock::now();

        toxsync::FileRangeSource source(root / "target");
        toxsync::StreamingSyncOptions sync_options;
        sync_options.fsync_on_commit = false;
        const auto sync_begin = std::chrono::steady_clock::now();
        const auto sync = toxsync::sync_file_streaming(
            root / "target.txi", root / "basis", source, root / "output", sync_options);
        const auto sync_end = std::chrono::steady_clock::now();

        constexpr std::uint64_t sixteen_tib =
            16ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;
        const auto scale_block = toxsync::choose_block_size(sixteen_tib);
        const auto scale_index = toxsync::index_metadata_bytes(sixteen_tib, scale_block);

        std::cout << "artifact-bytes=" << bytes << '\n'
                  << "block-size=" << build.metadata.block_size << '\n'
                  << "index-bytes=" << build.metadata.encoded_size() << '\n'
                  << "index-working-bytes=" << build.peak_working_bytes() << '\n'
                  << "index-mib-per-second="
                  << mib_per_second(bytes, seconds(build_begin, build_end)) << '\n'
                  << "sync-working-bytes=" << sync.peak_working_bytes() << '\n'
                  << "sync-reused-bytes=" << sync.reused_bytes << '\n'
                  << "sync-fetched-bytes=" << sync.fetched_bytes << '\n'
                  << "sync-source-ranges=" << sync.source_ranges << '\n'
                  << "sync-mib-per-second="
                  << mib_per_second(bytes, seconds(sync_begin, sync_end)) << '\n'
                  << "scale-16tib-block-size=" << scale_block << '\n'
                  << "scale-16tib-index-bytes=" << scale_index << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "toxsync_large_bench: " << error.what() << '\n';
        return 1;
    }
}
