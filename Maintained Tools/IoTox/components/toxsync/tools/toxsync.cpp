#include "toxsync/apply.hpp"
#include "toxsync/content_retention.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"
#include "toxsync/head.hpp"
#include "toxsync/index.hpp"
#include "toxsync/index_file.hpp"
#include "toxsync/planner.hpp"
#include "toxsync/publication.hpp"
#include "toxsync/range_source.hpp"
#include "toxsync/rolling_checksum.hpp"
#include "toxsync/streaming.hpp"
#include "toxsync/treepack.hpp"
#include "toxsync/version.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <exception>
#include <iostream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

[[noreturn]] void usage() {
    std::cerr << "usage:\n"
              << "  toxsync version\n"
              << "  toxsync pack <directory> <artifact>\n"
              << "  toxsync unpack <artifact> <empty-directory>\n"
              << "  toxsync index <target> <index> [auto|block-size] [metadata-budget-MiB]\n"
              << "  toxsync inspect <index>\n"
              << "  toxsync scale <target-bytes> [metadata-budget-MiB]\n"
              << "  toxsync sync <basis> <index> <target-source> <output>\n"
              << "  toxsync plan <basis> <index> [adaptive|rolling|aligned]\n"
              << "  toxsync apply-legacy <basis> <index> <target-source> <output> [adaptive|rolling|aligned]\n"
              << "  toxsync verify <index> <artifact>\n"
              << "  toxsync content-build <artifact> <store> <manifest> [auto [metadata-budget-MiB] | min avg max]\n"
              << "  toxsync content-build-paged <artifact> <store> <root> [auto [root-budget-MiB] | min avg max]\n"
              << "  toxsync content-scale <artifact-bytes> [metadata-budget-MiB]\n"
              << "  toxsync content-scale-paged <artifact-bytes> [root-budget-MiB]\n"
              << "  toxsync content-inspect <manifest>\n"
              << "  toxsync content-scan <manifest> <store> [verify]\n"
              << "  toxsync content-apply <manifest> <store> <output>\n"
              << "  toxsync publish-tree <source> <work> <store> <namespace-sha256> <generation> <private-key> <head-output> [previous-head|none] [snapshot] [retain]\n"
              << "  toxsync activate-tree <treepack> <activation-root> <head-file> <publisher-public-key>\n"
              << "  toxsync pin-set <journal> <namespace-sha256> <generation> <manifest-sha256> <retain-until-unix-seconds> <flags>\n"
              << "  toxsync pin-remove <journal> <namespace-sha256> <generation>\n"
              << "  toxsync pin-list <journal> [now-unix-seconds]\n"
              << "  toxsync content-gc <store> <journal> <maximum-bytes> [target-bytes] [dry-run]\n"
              << "  toxsync head-keygen <private-key> <public-key>\n"
              << "  toxsync head-create <namespace-sha256> <generation> range|content <artifact-sha256> <artifact-bytes> <index-sha256> <index-bytes> <parent-sha256|zero> <private-key> <output> [block-size] [snapshot]\n"
              << "  toxsync head-inspect <head>\n"
              << "  toxsync head-verify <head> <public-key>\n"
              << "  toxsync head-evaluate <candidate> <current|none> <public-key>\n";
    throw std::invalid_argument("invalid command line");
}

std::uint32_t parse_u32(std::string_view text) {
    std::uint32_t value{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        throw std::invalid_argument("invalid unsigned integer: " + std::string(text));
    }
    return value;
}

std::uint64_t parse_u64(std::string_view text) {
    std::uint64_t value{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        throw std::invalid_argument("invalid unsigned integer: " + std::string(text));
    }
    return value;
}

std::uint64_t mib_bytes(std::string_view text) {
    const auto mib = parse_u64(text);
    constexpr std::uint64_t unit = 1024U * 1024U;
    if (mib > std::numeric_limits<std::uint64_t>::max() / unit) {
        throw std::overflow_error("MiB value overflows byte count");
    }
    return mib * unit;
}

toxsync::PlannerSearchMode parse_search_mode(std::string_view text) {
    if (text == "adaptive") return toxsync::PlannerSearchMode::adaptive;
    if (text == "rolling") return toxsync::PlannerSearchMode::exhaustive_rolling;
    if (text == "aligned") return toxsync::PlannerSearchMode::aligned_only;
    throw std::invalid_argument("planner mode must be adaptive, rolling, or aligned");
}

toxsync::PlannerOptions planner_options(int argc, char** argv, int argument) {
    toxsync::PlannerOptions options;
    if (argc > argument) options.search_mode = parse_search_mode(argv[argument]);
    return options;
}

std::vector<std::byte> read_binary_file(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open file: " + path.string());
    input.seekg(0, std::ios::end);
    const auto end = input.tellg();
    if (end < 0) throw std::runtime_error("cannot size file: " + path.string());
    const auto size = static_cast<std::size_t>(end);
    std::vector<std::byte> bytes(size);
    input.seekg(0, std::ios::beg);
    if (size != 0U) {
        input.read(reinterpret_cast<char*>(bytes.data()),
                   static_cast<std::streamsize>(size));
    }
    if (!input) throw std::runtime_error("cannot read file: " + path.string());
    return bytes;
}

void write_binary_file(const std::filesystem::path& path,
                       std::span<const std::byte> bytes,
                       std::filesystem::perms permissions =
                           std::filesystem::perms::owner_read |
                           std::filesystem::perms::owner_write) {
    const auto parent = path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create file: " + path.string());
    if (!bytes.empty()) {
        output.write(reinterpret_cast<const char*>(bytes.data()),
                     static_cast<std::streamsize>(bytes.size()));
    }
    if (!output) throw std::runtime_error("cannot write file: " + path.string());
    output.close();
    std::error_code error;
    std::filesystem::permissions(
        path, permissions, std::filesystem::perm_options::replace, error);
    if (error) {
        throw std::runtime_error("cannot set file permissions: " + path.string() +
                                 ": " + error.message());
    }
}

template <typename Key>
Key read_fixed_key(const std::filesystem::path& path) {
    const auto bytes = read_binary_file(path);
    Key key;
    if (bytes.size() != key.bytes.size()) {
        throw std::runtime_error("key file has the wrong length: " + path.string());
    }
    std::copy(bytes.begin(), bytes.end(), key.bytes.begin());
    return key;
}

toxsync::MutableHead read_head(const std::filesystem::path& path) {
    const auto bytes = read_binary_file(path);
    return toxsync::decode_mutable_head(bytes);
}

void write_binary_file_exclusive(
    const std::filesystem::path& path,
    std::span<const std::byte> bytes,
    std::filesystem::perms permissions) {
    const auto parent = path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
#if defined(__unix__) || defined(__APPLE__)
    const auto has = [&](std::filesystem::perms bit) {
        return (permissions & bit) != std::filesystem::perms::none;
    };
    mode_t mode{};
    if (has(std::filesystem::perms::owner_read)) mode |= S_IRUSR;
    if (has(std::filesystem::perms::owner_write)) mode |= S_IWUSR;
    if (has(std::filesystem::perms::owner_exec)) mode |= S_IXUSR;
    if (has(std::filesystem::perms::group_read)) mode |= S_IRGRP;
    if (has(std::filesystem::perms::group_write)) mode |= S_IWGRP;
    if (has(std::filesystem::perms::group_exec)) mode |= S_IXGRP;
    if (has(std::filesystem::perms::others_read)) mode |= S_IROTH;
    if (has(std::filesystem::perms::others_write)) mode |= S_IWOTH;
    if (has(std::filesystem::perms::others_exec)) mode |= S_IXOTH;
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        mode);
    if (descriptor < 0) {
        throw std::runtime_error(
            "cannot exclusively create key file: " + path.string() + ": " +
            std::string(std::strerror(errno)));
    }
    std::size_t written{};
    while (written < bytes.size()) {
        const auto result = ::write(
            descriptor, bytes.data() + written, bytes.size() - written);
        if (result < 0) {
            if (errno == EINTR) continue;
            const int saved = errno;
            (void)::close(descriptor);
            (void)::unlink(path.c_str());
            throw std::runtime_error(
                "cannot write key file: " + path.string() + ": " +
                std::string(std::strerror(saved)));
        }
        if (result == 0) {
            (void)::close(descriptor);
            (void)::unlink(path.c_str());
            throw std::runtime_error(
                "zero-length write while creating key file: " + path.string());
        }
        written += static_cast<std::size_t>(result);
    }
    if (::fchmod(descriptor, mode) != 0) {
        const int saved = errno;
        (void)::close(descriptor);
        (void)::unlink(path.c_str());
        throw std::runtime_error(
            "cannot set key-file permissions: " + path.string() + ": " +
            std::string(std::strerror(saved)));
    }
    if (::close(descriptor) != 0) {
        const int saved = errno;
        (void)::unlink(path.c_str());
        throw std::runtime_error(
            "cannot close key file: " + path.string() + ": " +
            std::string(std::strerror(saved)));
    }
#else
    std::error_code error;
    const auto status = std::filesystem::symlink_status(path, error);
    if ((!error && std::filesystem::exists(status)) ||
        (error && error != std::errc::no_such_file_or_directory)) {
        throw std::runtime_error(
            "cannot exclusively create key file: " + path.string());
    }
    write_binary_file(path, bytes, permissions);
#endif
}

void write_head(const std::filesystem::path& path,
                const toxsync::MutableHead& head) {
    const auto bytes = toxsync::encode_mutable_head(head);
    write_binary_file(path, bytes);
}

toxsync::Digest256 parse_digest_or_zero(std::string_view text) {
    if (text == "zero" || text == "none" || text == "-") {
        return {};
    }
    return toxsync::Digest256::from_hex(std::string(text));
}

void print_paged_content_metadata(
    const toxsync::PagedContentManifestMetadata& metadata) {
    std::cout << "format=toxsync-content-paged-v"
              << toxsync::PagedContentManifestMetadata::kFormatVersion << '\n'
              << "artifact-bytes=" << metadata.artifact_size << '\n'
              << "chunks=" << metadata.chunk_count << '\n'
              << "pages=" << metadata.page_count << '\n'
              << "entries-per-page=" << metadata.entries_per_page << '\n'
              << "chunk-min=" << metadata.chunking.min_bytes << '\n'
              << "chunk-average=" << metadata.chunking.average_bytes << '\n'
              << "chunk-max=" << metadata.chunking.max_bytes << '\n'
              << "root-bytes=" << metadata.encoded_size() << '\n'
              << "artifact-sha256=" << metadata.artifact_digest.hex() << '\n'
              << "entries-sha256=" << metadata.chunk_entries_digest.hex() << '\n'
              << "page-records-sha256=" << metadata.page_records_digest.hex() << '\n'
              << "root-sha256=" << metadata.root_digest.hex() << '\n';
}

void print_missing_page(void*, const toxsync::PagedContentPageRef& page) {
    std::cout << "missing-page index=" << page.page_index
              << " first-chunk=" << page.first_chunk
              << " chunks=" << page.chunk_count
              << " bytes=" << page.encoded_size
              << " sha256=" << page.digest.hex() << '\n';
}

void print_head(const toxsync::MutableHead& head) {
    std::cout << "engine="
              << (head.engine == toxsync::Engine::range_v1 ? "range-v1"
                                                            : "content-store-v2")
              << '\n'
              << "flags=" << head.flags << '\n'
              << "generation=" << head.generation << '\n'
              << "namespace=" << head.namespace_id.hex() << '\n'
              << "artifact=" << head.artifact.hex() << '\n'
              << "artifact-bytes=" << head.artifact_size << '\n'
              << "index=" << head.index.hex() << '\n'
              << "index-bytes=" << head.index_size << '\n'
              << "parent=" << head.parent.hex() << '\n'
              << "block-size=" << head.block_size << '\n'
              << "record-sha256="
              << toxsync::mutable_head_record_digest(head).hex() << '\n';
}

void print_treepack_stats(const toxsync::TreePackStats& stats) {
    std::cout << "directories=" << stats.directories << '\n'
              << "files=" << stats.files << '\n'
              << "content-bytes=" << stats.content_bytes << '\n'
              << "artifact-bytes=" << stats.artifact_bytes << '\n'
              << "sort-runs=" << stats.sort_runs << '\n'
              << "sort-merge-passes=" << stats.sort_merge_passes << '\n'
              << "peak-sort-buffer-bytes=" << stats.peak_sort_buffer_bytes << '\n';
}


void print_content_metadata(const toxsync::ContentManifestMetadata& metadata) {
    std::cout << "format=toxsync-content-v"
              << toxsync::ContentManifestMetadata::kFormatVersion << '\n'
              << "artifact-bytes=" << metadata.artifact_size << '\n'
              << "chunks=" << metadata.chunk_count << '\n'
              << "chunk-min=" << metadata.chunking.min_bytes << '\n'
              << "chunk-average=" << metadata.chunking.average_bytes << '\n'
              << "chunk-max=" << metadata.chunking.max_bytes << '\n'
              << "manifest-bytes=" << metadata.encoded_size() << '\n'
              << "artifact-sha256=" << metadata.artifact_digest.hex() << '\n'
              << "entries-sha256=" << metadata.entries_digest.hex() << '\n'
              << "manifest-sha256=" << metadata.manifest_digest.hex() << '\n';
}

void print_missing_chunk(void*, const toxsync::ContentChunkRef& chunk) {
    std::cout << "missing index=" << chunk.index
              << " offset=" << chunk.artifact_offset
              << " length=" << chunk.length
              << " sha256=" << chunk.digest.hex() << '\n';
}

void print_plan(const toxsync::Plan& plan) {
    std::cout << "basis-bytes=" << plan.stats.basis_size << '\n'
              << "matched-blocks=" << plan.stats.matched_blocks << '\n'
              << "reused-bytes=" << plan.stats.reused_bytes << '\n'
              << "missing-bytes=" << plan.stats.missing_bytes << '\n'
              << "missing-ranges=" << plan.missing_ranges.size() << '\n'
              << "scanned-windows=" << plan.stats.scanned_windows << '\n'
              << "strong-checks=" << plan.stats.strong_checks << '\n'
              << "aligned-blocks-checked=" << plan.stats.aligned_blocks_checked << '\n'
              << "aligned-blocks-matched=" << plan.stats.aligned_blocks_matched << '\n'
              << "aligned-bytes-examined=" << plan.stats.aligned_bytes_examined << '\n'
              << "aligned-probe-aborted-early=" << (plan.stats.aligned_probe_aborted_early ? 1 : 0) << '\n'
              << "rolling-passes=" << plan.stats.rolling_passes << '\n'
              << "basis-read-calls=" << plan.stats.basis_read_calls << '\n'
              << "plan-resident-bytes=" << plan.resident_bytes() << '\n'
              << "planner-temporary-peak-bytes=" << plan.stats.temporary_bytes_peak << '\n';
    for (const auto& range : plan.missing_ranges) {
        std::cout << "range offset=" << range.offset << " length=" << range.length << '\n';
    }
}

} // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2) usage();
        const std::string_view command(argv[1]);
        if (command == "version") {
            if (argc != 2) usage();
            std::cout << "toxsync " << toxsync::kVersion
                      << " engine=" << toxsync::kEngine
                      << " sha256=" << toxsync::sha256_backend_name()
                      << " rolling=" << toxsync::rolling_checksum_backend_name() << '\n';
            return 0;
        }
        if (command == "pack") {
            if (argc != 4) usage();
            const auto stats = toxsync::pack_tree(argv[2], argv[3]);
            print_treepack_stats(stats);
            return 0;
        }
        if (command == "unpack") {
            if (argc != 4) usage();
            const auto stats = toxsync::unpack_tree(argv[2], argv[3]);
            print_treepack_stats(stats);
            return 0;
        }
        if (command == "index") {
            if (argc < 4 || argc > 6) usage();
            toxsync::IndexFileBuildOptions options;
            if (argc >= 5 && std::string_view(argv[4]) != "auto") {
                options.block_size = parse_u32(argv[4]);
            }
            if (argc == 6) options.auto_block.metadata_budget_bytes = mib_bytes(argv[5]);
            const auto built = toxsync::build_index_file(argv[2], argv[3], options);
            std::cout << "target-bytes=" << built.metadata.target_size
                      << " blocks=" << built.metadata.block_count
                      << " block-size=" << built.metadata.block_size
                      << " metadata-bytes=" << built.metadata.encoded_size()
                      << " working-bytes=" << built.peak_working_bytes()
                      << " sha256=" << built.metadata.target_digest.hex() << '\n';
            return 0;
        }
        if (command == "inspect") {
            if (argc != 3) usage();
            const auto metadata = toxsync::inspect_index_file(argv[2]);
            std::cout << "format=toxsync-index-v" << toxsync::Index::kFormatVersion << '\n'
                      << "target-bytes=" << metadata.target_size << '\n'
                      << "blocks=" << metadata.block_count << '\n'
                      << "block-size=" << metadata.block_size << '\n'
                      << "metadata-bytes=" << metadata.encoded_size() << '\n'
                      << "sha256=" << metadata.target_digest.hex() << '\n';
            return 0;
        }
        if (command == "scale") {
            if (argc != 3 && argc != 4) usage();
            toxsync::AutoBlockSizeOptions options;
            if (argc == 4) options.metadata_budget_bytes = mib_bytes(argv[3]);
            const auto target_bytes = parse_u64(argv[2]);
            const auto block_size = toxsync::choose_block_size(target_bytes, options);
            std::cout << "target-bytes=" << target_bytes << '\n'
                      << "block-size=" << block_size << '\n'
                      << "metadata-bytes="
                      << toxsync::index_metadata_bytes(target_bytes, block_size) << '\n';
            return 0;
        }
        if (command == "sync") {
            if (argc != 6) usage();
            toxsync::FileRangeSource source(argv[4]);
            const auto result = toxsync::sync_file_streaming(
                argv[3], argv[2], source, argv[5]);
            std::cout << "resumed-bytes=" << result.resumed_bytes << '\n'
                      << "discarded-resume-bytes=" << result.discarded_resume_bytes << '\n'
                      << "written-from-basis=" << result.reused_bytes << '\n'
                      << "fetched-from-source=" << result.fetched_bytes << '\n'
                      << "matched-blocks=" << result.matched_blocks << '\n'
                      << "missing-blocks=" << result.missing_blocks << '\n'
                      << "source-batches=" << result.source_batch_calls << '\n'
                      << "source-ranges=" << result.source_ranges << '\n'
                      << "working-bytes=" << result.peak_working_bytes() << '\n'
                      << "output-sha256=" << result.output_digest.hex() << '\n';
            return 0;
        }
        if (command == "plan") {
            if (argc != 4 && argc != 5) usage();
            const auto index = toxsync::Index::read_file(argv[3]);
            print_plan(toxsync::plan_file(index, argv[2], planner_options(argc, argv, 4)));
            return 0;
        }
        if (command == "apply-legacy") {
            if (argc != 6 && argc != 7) usage();
            const auto index = toxsync::Index::read_file(argv[3]);
            const auto plan = toxsync::plan_file(index, argv[2], planner_options(argc, argv, 6));
            toxsync::FileRangeSource source(argv[4]);
            const auto result = toxsync::apply_file(index, plan, argv[2], source, argv[5]);
            print_plan(plan);
            std::cout << "resumed-bytes=" << result.resumed_bytes << '\n'
                      << "written-from-basis=" << result.reused_bytes << '\n'
                      << "fetched-from-source=" << result.fetched_bytes << '\n'
                      << "apply-buffer-bytes=" << result.buffer_bytes << '\n'
                      << "basis-runs=" << result.basis_runs << '\n'
                      << "source-runs=" << result.source_runs << '\n'
                      << "basis-read-calls=" << result.basis_read_calls << '\n'
                      << "source-read-calls=" << result.source_read_calls << '\n'
                      << "output-write-calls=" << result.output_write_calls << '\n'
                      << "output-sha256=" << result.output_digest.hex() << '\n';
            return 0;
        }
        if (command == "verify") {
            if (argc != 4) usage();
            const bool valid = toxsync::verify_indexed_file(argv[2], argv[3]);
            std::cout << (valid ? "valid\n" : "invalid\n");
            return valid ? 0 : 2;
        }
        if (command == "content-build") {
            if (argc != 5 && argc != 6 && argc != 7 && argc != 8) usage();
            toxsync::ContentStoreOptions options;
            if (argc >= 6 && std::string_view(argv[5]) == "auto") {
                if (argc != 6 && argc != 7) usage();
                options.auto_chunking = true;
                if (argc == 7) options.metadata_budget_bytes = mib_bytes(argv[6]);
            } else if (argc == 8) {
                options.chunking.min_bytes = parse_u32(argv[5]);
                options.chunking.average_bytes = parse_u32(argv[6]);
                options.chunking.max_bytes = parse_u32(argv[7]);
            } else if (argc != 5) {
                usage();
            }
            const auto stats = toxsync::build_content_store(
                argv[2], argv[3], argv[4], options);
            print_content_metadata(stats.metadata);
            std::cout << "chunks-created=" << stats.chunks_created << '\n'
                      << "chunks-reused=" << stats.chunks_reused << '\n'
                      << "bytes-created=" << stats.bytes_created << '\n'
                      << "bytes-reused=" << stats.bytes_reused << '\n'
                      << "workspace-bytes=" << stats.workspace_reserved_bytes << '\n';
            return 0;
        }
        if (command == "content-build-paged") {
            if (argc != 5 && argc != 6 && argc != 7 && argc != 8) usage();
            toxsync::PagedContentStoreOptions options;
            if (argc >= 6 && std::string_view(argv[5]) == "auto") {
                if (argc != 6 && argc != 7) usage();
                options.auto_chunking = true;
                if (argc == 7) {
                    options.root_metadata_budget_bytes = mib_bytes(argv[6]);
                }
            } else if (argc == 8) {
                options.chunking.min_bytes = parse_u32(argv[5]);
                options.chunking.average_bytes = parse_u32(argv[6]);
                options.chunking.max_bytes = parse_u32(argv[7]);
            } else if (argc != 5) {
                usage();
            }
            const auto stats = toxsync::build_paged_content_store(
                argv[2], argv[3], argv[4], options);
            print_paged_content_metadata(stats.metadata);
            std::cout << "chunks-created=" << stats.chunks_created << '\n'
                      << "chunks-reused=" << stats.chunks_reused << '\n'
                      << "chunk-bytes-created=" << stats.chunk_bytes_created << '\n'
                      << "chunk-bytes-reused=" << stats.chunk_bytes_reused << '\n'
                      << "pages-created=" << stats.pages_created << '\n'
                      << "pages-reused=" << stats.pages_reused << '\n'
                      << "page-bytes-created=" << stats.page_bytes_created << '\n'
                      << "page-bytes-reused=" << stats.page_bytes_reused << '\n'
                      << "workspace-bytes=" << stats.workspace_reserved_bytes << '\n';
            return 0;
        }
        if (command == "content-scale") {
            if (argc != 3 && argc != 4) usage();
            toxsync::ContentChunkingAutoOptions options;
            if (argc == 4) options.metadata_budget_bytes = mib_bytes(argv[3]);
            const auto estimate = toxsync::estimate_content_scale(
                parse_u64(argv[2]), options);
            std::cout << "artifact-bytes=" << estimate.artifact_size << '\n'
                      << "chunk-min=" << estimate.chunking.min_bytes << '\n'
                      << "chunk-average=" << estimate.chunking.average_bytes << '\n'
                      << "chunk-max=" << estimate.chunking.max_bytes << '\n'
                      << "maximum-chunks=" << estimate.maximum_chunks << '\n'
                      << "maximum-manifest-bytes="
                      << estimate.maximum_manifest_bytes << '\n';
            return 0;
        }
        if (command == "content-scale-paged") {
            if (argc != 3 && argc != 4) usage();
            toxsync::PagedContentStoreOptions options;
            options.auto_chunking = true;
            if (argc == 4) {
                options.root_metadata_budget_bytes = mib_bytes(argv[3]);
            }
            const auto estimate = toxsync::estimate_paged_content_scale(
                parse_u64(argv[2]), options);
            std::cout << "artifact-bytes=" << estimate.artifact_size << '\n'
                      << "chunk-min=" << estimate.chunking.min_bytes << '\n'
                      << "chunk-average=" << estimate.chunking.average_bytes << '\n'
                      << "chunk-max=" << estimate.chunking.max_bytes << '\n'
                      << "entries-per-page=" << estimate.entries_per_page << '\n'
                      << "maximum-chunks=" << estimate.maximum_chunks << '\n'
                      << "maximum-pages=" << estimate.maximum_pages << '\n'
                      << "maximum-root-bytes=" << estimate.maximum_root_bytes << '\n'
                      << "maximum-distributed-metadata-bytes="
                      << estimate.maximum_distributed_metadata_bytes << '\n';
            return 0;
        }
        if (command == "content-inspect") {
            if (argc != 3) usage();
            if (toxsync::detect_content_manifest_format(argv[2]) ==
                toxsync::ContentManifestFormat::paged_v2) {
                print_paged_content_metadata(
                    toxsync::inspect_paged_content_manifest(argv[2]));
            } else {
                print_content_metadata(toxsync::inspect_content_manifest(argv[2]));
            }
            return 0;
        }
        if (command == "content-scan") {
            if (argc != 4 && argc != 5) usage();
            const bool verify = argc == 5;
            if (verify && std::string_view(argv[4]) != "verify") usage();
            if (toxsync::detect_content_manifest_format(argv[2]) ==
                toxsync::ContentManifestFormat::paged_v2) {
                toxsync::PagedContentScanOptions options;
                options.verify_chunk_digests = verify;
                const auto stats = toxsync::scan_missing_paged_content_chunks(
                    argv[2], argv[3], &print_missing_page, nullptr,
                    &print_missing_chunk, nullptr, options);
                print_paged_content_metadata(stats.metadata);
                std::cout << "available-pages=" << stats.available_pages << '\n'
                          << "missing-pages=" << stats.missing_pages << '\n'
                          << "corrupt-pages=" << stats.corrupt_pages << '\n'
                          << "available-chunks=" << stats.available_chunks << '\n'
                          << "missing-chunks=" << stats.missing_chunks << '\n'
                          << "unknown-chunks=" << stats.unknown_chunks << '\n'
                          << "corrupt-chunks=" << stats.corrupt_chunks << '\n'
                          << "available-bytes=" << stats.available_bytes << '\n'
                          << "missing-bytes=" << stats.missing_bytes << '\n'
                          << "unknown-bytes=" << stats.unknown_bytes << '\n';
                return stats.missing_pages == 0U && stats.missing_chunks == 0U &&
                               stats.corrupt_pages == 0U &&
                               stats.corrupt_chunks == 0U
                           ? 0
                           : 2;
            }
            toxsync::ContentStoreScanOptions options;
            options.verify_chunk_digests = verify;
            const auto stats = toxsync::scan_missing_content_chunks(
                argv[2], argv[3], &print_missing_chunk, nullptr, options);
            print_content_metadata(stats.metadata);
            std::cout << "available-chunks=" << stats.available_chunks << '\n'
                      << "missing-chunks=" << stats.missing_chunks << '\n'
                      << "available-bytes=" << stats.available_bytes << '\n'
                      << "missing-bytes=" << stats.missing_bytes << '\n'
                      << "corrupt-chunks=" << stats.corrupt_chunks << '\n';
            return stats.missing_chunks == 0U ? 0 : 2;
        }
        if (command == "content-apply") {
            if (argc != 5) usage();
            const bool paged = toxsync::detect_content_manifest_format(argv[2]) ==
                               toxsync::ContentManifestFormat::paged_v2;
            const auto stats = paged
                ? toxsync::reconstruct_paged_content_manifest(
                      argv[2], argv[3], argv[4])
                : toxsync::reconstruct_content_manifest(
                      argv[2], argv[3], argv[4]);
            if (paged) {
                print_paged_content_metadata(
                    toxsync::inspect_paged_content_manifest(argv[2]));
            } else {
                print_content_metadata(stats.metadata);
            }
            std::cout << "chunks-read=" << stats.chunks_read << '\n'
                      << "bytes-read=" << stats.bytes_read << '\n'
                      << "workspace-bytes=" << stats.workspace_reserved_bytes << '\n';
            return 0;
        }
        if (command == "publish-tree") {
            if (argc < 9 || argc > 12) usage();
            toxsync::DirectoryPublicationRequest request;
            request.source_root = argv[2];
            request.work_root = argv[3];
            request.store_root = argv[4];
            request.namespace_id = toxsync::Digest256::from_hex(argv[5]);
            request.generation = parse_u64(argv[6]);
            request.private_key =
                read_fixed_key<toxsync::Ed25519PrivateKey>(argv[7]);
            request.head_output = argv[8];

            int optional = 9;
            if (argc > optional) {
                const std::string_view previous(argv[optional]);
                if (previous != "none" && previous != "-") {
                    request.previous = read_head(argv[optional]);
                }
                ++optional;
            }

            toxsync::DirectoryPublicationOptions options;
            while (argc > optional) {
                const std::string_view mode(argv[optional++]);
                if (mode == "snapshot") {
                    request.snapshot = true;
                } else if (mode == "retain") {
                    options.retain_treepack = true;
                    options.retain_root_manifest = true;
                } else {
                    throw std::invalid_argument(
                        "publish-tree modes must be snapshot or retain");
                }
            }

            const auto stats = toxsync::publish_directory_revision(
                request, options);
            print_head(stats.head);
            print_treepack_stats(stats.treepack);
            std::cout << "chunks=" << stats.content.metadata.chunk_count << '\n'
                      << "pages=" << stats.content.metadata.page_count << '\n'
                      << "new-chunk-bytes=" << stats.content.chunk_bytes_created << '\n'
                      << "reused-chunk-bytes=" << stats.content.chunk_bytes_reused << '\n'
                      << "root-sha256="
                      << stats.content.metadata.root_digest.hex() << '\n'
                      << "workspace-reserved-bytes="
                      << stats.workspace_reserved_bytes << '\n'
                      << "head-output=" << request.head_output.string() << '\n';
            if (!stats.retained_treepack.empty()) {
                std::cout << "retained-treepack="
                          << stats.retained_treepack.string() << '\n';
            }
            if (!stats.retained_root_manifest.empty()) {
                std::cout << "retained-root-manifest="
                          << stats.retained_root_manifest.string() << '\n';
            }
            return 0;
        }
        if (command == "activate-tree") {
            if (argc != 6) usage();
            const auto head = read_head(argv[4]);
            const auto publisher =
                read_fixed_key<toxsync::Ed25519PublicKey>(argv[5]);
            if (!toxsync::verify_mutable_head(head, publisher)) {
                throw std::runtime_error(
                    "activate-tree HEAD does not verify under the supplied publisher key");
            }
            if ((head.flags & toxsync::kHeadFlagTreepack) == 0U) {
                throw std::invalid_argument(
                    "activate-tree HEAD does not identify a treepack artifact");
            }
            std::error_code error;
            const auto size = std::filesystem::file_size(argv[2], error);
            if (error || size != head.artifact_size ||
                toxsync::sha256_file(argv[2]) != head.artifact) {
                throw std::runtime_error(
                    "activate-tree artifact does not match the signed HEAD");
            }
            const auto stats = toxsync::activate_treepack_revision(
                argv[2], argv[3], head.namespace_id, head.generation,
                toxsync::mutable_head_record_digest(head));
            print_treepack_stats(stats.treepack);
            std::cout << "revision-path=" << stats.revision_path.string() << '\n'
                      << "current-link=" << stats.current_link.string() << '\n'
                      << "previous-target=" << stats.previous_target.string() << '\n';
            return 0;
        }
        if (command == "pin-set") {
            if (argc != 8) usage();
            toxsync::ContentPin pin;
            pin.namespace_id = toxsync::Digest256::from_hex(argv[3]);
            pin.generation = parse_u64(argv[4]);
            pin.manifest = toxsync::Digest256::from_hex(argv[5]);
            pin.retain_until_unix_seconds = parse_u64(argv[6]);
            pin.flags = parse_u32(argv[7]);
            toxsync::ContentPinLedger ledger(argv[2]);
            const auto result = ledger.upsert(pin);
            std::cout << "result=" << static_cast<unsigned int>(result) << '\n'
                      << "active-pins=" << ledger.stats().active_pins << '\n';
            return result == toxsync::ContentPinUpdate::capacity_exhausted ||
                           result == toxsync::ContentPinUpdate::fork_rejected
                       ? 2
                       : 0;
        }
        if (command == "pin-remove") {
            if (argc != 5) usage();
            toxsync::ContentPinLedger ledger(argv[2]);
            const bool removed = ledger.erase(
                toxsync::Digest256::from_hex(argv[3]), parse_u64(argv[4]));
            std::cout << "removed=" << (removed ? 1 : 0) << '\n'
                      << "active-pins=" << ledger.stats().active_pins << '\n';
            return removed ? 0 : 2;
        }
        if (command == "pin-list") {
            if (argc != 3 && argc != 4) usage();
            const std::uint64_t now = argc == 4 ? parse_u64(argv[3]) : 0U;
            toxsync::ContentPinLedger ledger(argv[2]);
            for (const auto& pin : ledger.pins()) {
                const bool active = pin.retain_until_unix_seconds == 0U ||
                                    now == 0U ||
                                    pin.retain_until_unix_seconds >= now;
                std::cout << "namespace=" << pin.namespace_id.hex()
                          << " generation=" << pin.generation
                          << " manifest=" << pin.manifest.hex()
                          << " retain-until=" << pin.retain_until_unix_seconds
                          << " flags=" << pin.flags
                          << " active=" << (active ? 1 : 0) << '\n';
            }
            const auto stats = ledger.stats();
            std::cout << "active-pins=" << stats.active_pins << '\n'
                      << "resident-bytes=" << stats.resident_bytes << '\n'
                      << "journal-bytes=" << stats.journal_bytes << '\n';
            return 0;
        }
        if (command == "content-gc") {
            if (argc < 5 || argc > 7) usage();
            toxsync::ContentGcOptions options;
            options.maximum_store_bytes = parse_u64(argv[4]);
            if (argc >= 6 && std::string_view(argv[5]) != "dry-run") {
                options.target_store_bytes = parse_u64(argv[5]);
            }
            if ((argc == 6 && std::string_view(argv[5]) == "dry-run") ||
                (argc == 7 && std::string_view(argv[6]) == "dry-run")) {
                options.dry_run = true;
            } else if (argc == 7) {
                usage();
            }
            toxsync::ContentPinLedger ledger(argv[3]);
            const auto stats = toxsync::collect_content_store(
                argv[2], ledger, options);
            std::cout << "active-pins=" << stats.active_pins << '\n'
                      << "pinned-manifests=" << stats.pinned_manifests << '\n'
                      << "reachable-pages=" << stats.reachable_page_references << '\n'
                      << "reachable-chunks=" << stats.reachable_chunk_references << '\n'
                      << "scanned-files=" << stats.scanned_files << '\n'
                      << "scanned-bytes=" << stats.scanned_bytes << '\n'
                      << "protected-files=" << stats.protected_files << '\n'
                      << "protected-bytes=" << stats.protected_bytes << '\n'
                      << "candidate-files=" << stats.candidate_files << '\n'
                      << "candidate-bytes=" << stats.candidate_bytes << '\n'
                      << "deleted-files=" << stats.deleted_files << '\n'
                      << "deleted-bytes=" << stats.deleted_bytes << '\n'
                      << "deletion-failures=" << stats.deletion_failures << '\n'
                      << "bytes-after=" << stats.bytes_after << '\n'
                      << "bloom-bytes=" << stats.reachability_filter_bytes << '\n'
                      << "bloom-false-positive-rate="
                      << stats.estimated_false_positive_rate << '\n'
                      << "budget-satisfied=" << (stats.budget_satisfied ? 1 : 0) << '\n'
                      << "dry-run=" << (stats.dry_run ? 1 : 0) << '\n';
            return stats.deletion_failures == 0U ? 0 : 2;
        }
        if (command == "head-keygen") {
            if (argc != 4) usage();
            if (!toxsync::ed25519_backend_available()) {
                throw std::runtime_error(
                    "Ed25519 key generation requires the OpenSSL backend");
            }
            toxsync::Ed25519PrivateKey private_key;
            toxsync::Ed25519PublicKey public_key;
            if (!toxsync::ed25519_generate_key(private_key, public_key)) {
                throw std::runtime_error("Ed25519 key generation failed");
            }
            const auto private_path = std::filesystem::path(argv[2]);
            const auto public_path = std::filesystem::path(argv[3]);
            write_binary_file_exclusive(
                private_path, private_key.bytes,
                std::filesystem::perms::owner_read |
                    std::filesystem::perms::owner_write);
            try {
                write_binary_file_exclusive(
                    public_path, public_key.bytes,
                    std::filesystem::perms::owner_read |
                        std::filesystem::perms::owner_write |
                        std::filesystem::perms::group_read |
                        std::filesystem::perms::others_read);
            } catch (...) {
                std::error_code ignored;
                std::filesystem::remove(private_path, ignored);
                throw;
            }
            std::cout << "private-key=" << argv[2] << '\n'
                      << "public-key=" << argv[3] << '\n';
            return 0;
        }
        if (command == "head-create") {
            if (argc < 12 || argc > 14) usage();
            toxsync::MutableHead head;
            head.namespace_id = toxsync::Digest256::from_hex(argv[2]);
            head.generation = parse_u64(argv[3]);
            const std::string_view engine(argv[4]);
            if (engine == "range") {
                head.engine = toxsync::Engine::range_v1;
            } else if (engine == "content") {
                head.engine = toxsync::Engine::content_store_v2;
            } else {
                throw std::invalid_argument("head engine must be range or content");
            }
            head.artifact = toxsync::Digest256::from_hex(argv[5]);
            head.artifact_size = parse_u64(argv[6]);
            head.index = toxsync::Digest256::from_hex(argv[7]);
            head.index_size = parse_u64(argv[8]);
            head.parent = parse_digest_or_zero(argv[9]);
            const auto private_key =
                read_fixed_key<toxsync::Ed25519PrivateKey>(argv[10]);
            const std::filesystem::path output = argv[11];
            int optional = 12;
            if (head.engine == toxsync::Engine::range_v1) {
                if (argc <= optional) {
                    throw std::invalid_argument(
                        "range heads require a nonzero block size");
                }
                head.block_size = parse_u32(argv[optional++]);
            }
            if (argc > optional) {
                if (std::string_view(argv[optional]) != "snapshot") usage();
                head.flags |= toxsync::kHeadFlagSnapshot;
                ++optional;
            }
            if (argc != optional) usage();
            if (!toxsync::sign_mutable_head(head, private_key)) {
                throw std::runtime_error("mutable HEAD signing failed");
            }
            write_head(output, head);
            print_head(head);
            return 0;
        }
        if (command == "head-inspect") {
            if (argc != 3) usage();
            print_head(read_head(argv[2]));
            return 0;
        }
        if (command == "head-verify") {
            if (argc != 4) usage();
            const auto head = read_head(argv[2]);
            const auto public_key =
                read_fixed_key<toxsync::Ed25519PublicKey>(argv[3]);
            const bool valid = toxsync::verify_mutable_head(head, public_key);
            std::cout << (valid ? "valid\n" : "invalid\n");
            return valid ? 0 : 2;
        }
        if (command == "head-evaluate") {
            if (argc != 5) usage();
            const auto candidate = read_head(argv[2]);
            std::optional<toxsync::MutableHead> current;
            if (std::string_view(argv[3]) != "none" &&
                std::string_view(argv[3]) != "-") {
                current = read_head(argv[3]);
            }
            const auto public_key =
                read_fixed_key<toxsync::Ed25519PublicKey>(argv[4]);
            const auto evaluated = toxsync::evaluate_mutable_head(
                candidate, current, nullptr,
                const_cast<toxsync::Ed25519PublicKey*>(&public_key));
            std::cout << "decision="
                      << toxsync::head_decision_name(evaluated.decision) << '\n'
                      << "accepted=" << (evaluated.accepted() ? 1 : 0) << '\n'
                      << "generation-delta=" << evaluated.generation_delta << '\n'
                      << "candidate-record=" << evaluated.candidate_record.hex() << '\n'
                      << "current-record=" << evaluated.current_record.hex() << '\n';
            return evaluated.accepted() ||
                           evaluated.decision == toxsync::HeadDecision::duplicate
                       ? 0
                       : 2;
        }
        usage();
    } catch (const std::exception& error) {
        std::cerr << "toxsync: " << error.what() << '\n';
        return 1;
    }
}
