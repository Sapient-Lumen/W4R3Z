#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/content_store.hpp"

#include <algorithm>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <vector>

namespace {

toxsync::PagedContentStoreOptions paged_options() {
    toxsync::PagedContentStoreOptions options;
    options.chunking = {
        .min_bytes = 4096U,
        .average_bytes = 16384U,
        .max_bytes = 65536U,
    };
    options.entries_per_page = 8U;
    options.io_buffer_bytes = 32768U;
    options.root_buffer_bytes = 4096U;
    options.fsync_on_commit = false;
    return options;
}

struct PageCollector {
    std::vector<toxsync::PagedContentPageRef> pages;
    static void collect(void* context,
                        const toxsync::PagedContentPageRef& page) {
        static_cast<PageCollector*>(context)->pages.push_back(page);
    }
};

struct ChunkCollector {
    std::vector<toxsync::ContentChunkRef> chunks;
    static void collect(void* context,
                        const toxsync::ContentChunkRef& chunk) {
        static_cast<ChunkCollector*>(context)->chunks.push_back(chunk);
    }
};

bool bit(std::span<const std::byte> bytes, std::size_t index) {
    return (std::to_integer<unsigned char>(bytes[index / 8U]) &
            static_cast<unsigned char>(1U << (index % 8U))) != 0U;
}

} // namespace

TOXSYNC_TEST(paged_content_builds_scans_and_reconstructs_without_flat_manifest) {
    test::TempDir temp;
    const auto artifact = test::pattern(3U * 1024U * 1024U + 137U, 0x42U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);
    REQUIRE(built.metadata.artifact_size == artifact.size());
    REQUIRE(built.metadata.page_count > 1U);
    REQUIRE(built.pages_created == built.metadata.page_count);
    REQUIRE(toxsync::detect_content_manifest_format(
                temp.path() / "artifact.txp") ==
            toxsync::ContentManifestFormat::paged_v2);

    const auto inspected = toxsync::inspect_paged_content_manifest(
        temp.path() / "artifact.txp", workspace);
    REQUIRE(inspected.root_digest == built.metadata.root_digest);
    REQUIRE(inspected.chunk_entries_digest ==
            built.metadata.chunk_entries_digest);

    const auto scanned = toxsync::scan_missing_paged_content_chunks(
        temp.path() / "artifact.txp", temp.path() / "store", workspace);
    REQUIRE(scanned.missing_pages == 0U);
    REQUIRE(scanned.missing_chunks == 0U);
    REQUIRE(scanned.available_chunks == built.metadata.chunk_count);
    REQUIRE(scanned.available_bytes == artifact.size());

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.io_buffer_bytes = 32768U;
    reconstruct.manifest_buffer_bytes = 4096U;
    reconstruct.fsync_on_commit = false;
    const auto rebuilt = toxsync::reconstruct_paged_content_manifest(
        temp.path() / "artifact.txp", temp.path() / "store",
        temp.path() / "rebuilt", workspace, reconstruct);
    REQUIRE(rebuilt.chunks_read == built.metadata.chunk_count);
    REQUIRE(test::read_file(temp.path() / "rebuilt") == artifact);
}

TOXSYNC_TEST(paged_content_reports_missing_page_without_allocating_chunk_inventory) {
    test::TempDir temp;
    const auto artifact = test::pattern(2U * 1024U * 1024U + 91U, 0x83U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    options.publish_root_to_store = false;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);

    PageCollector pages;
    const auto empty = toxsync::scan_missing_paged_content_chunks(
        temp.path() / "artifact.txp", temp.path() / "empty", workspace,
        &PageCollector::collect, &pages);
    REQUIRE(empty.missing_pages == built.metadata.page_count);
    REQUIRE(empty.unknown_chunks == built.metadata.chunk_count);
    REQUIRE(pages.pages.size() == built.metadata.page_count);

    const auto removed = toxsync::content_store_path(
        temp.path() / "store", pages.pages.front().digest);
    std::filesystem::remove(removed);
    ChunkCollector chunks;
    pages.pages.clear();
    const auto partial = toxsync::scan_missing_paged_content_chunks(
        temp.path() / "artifact.txp", temp.path() / "store", workspace,
        &PageCollector::collect, &pages,
        &ChunkCollector::collect, &chunks);
    REQUIRE(partial.missing_pages == 1U);
    REQUIRE(partial.unknown_chunks > 0U);
    REQUIRE(pages.pages.size() == 1U);
    REQUIRE(chunks.chunks.empty());
}

TOXSYNC_TEST(paged_content_availability_loads_only_intersecting_pages) {
    test::TempDir temp;
    const auto artifact = test::pattern(1024U * 1024U, 0x128U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);
    REQUIRE(built.metadata.chunk_count > 16U);

    std::vector<std::byte> bits(2U);
    const auto available = toxsync::fill_content_availability(
        temp.path() / "artifact.txp", temp.path() / "store",
        5U, 16U, bits, false, &workspace);
    REQUIRE(available.format == toxsync::ContentManifestFormat::paged_v2);
    REQUIRE(available.bit_count == 16U);
    REQUIRE(available.available_count == 16U);
    REQUIRE(std::all_of(bits.begin(), bits.end(), [](std::byte value) {
        return value == std::byte{0xff};
    }));

    PageCollector pages;
    (void)toxsync::scan_missing_paged_content_chunks(
        temp.path() / "artifact.txp", temp.path() / "empty", workspace,
        &PageCollector::collect, &pages);
    REQUIRE(!pages.pages.empty());
    const auto first_page = pages.pages.front();
    std::filesystem::remove(toxsync::content_store_path(
        temp.path() / "store", first_page.digest));
    std::fill(bits.begin(), bits.end(), std::byte{0xff});
    const auto unknown = toxsync::fill_content_availability(
        temp.path() / "artifact.txp", temp.path() / "store",
        0U, 16U, bits, false, &workspace);
    REQUIRE(unknown.unknown_count > 0U);
    REQUIRE(!bit(bits, 0U));
}

TOXSYNC_TEST(paged_content_page_availability_is_exact_bounded_and_verifiable) {
    test::TempDir temp;
    const auto artifact = test::pattern(3U * 1024U * 1024U + 17U, 0x5150U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    options.entries_per_page = 4U;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);
    REQUIRE(built.metadata.page_count > 8U);

    std::array<std::byte, 2U> bits{};
    auto available = toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact.txp", temp.path() / "store",
        1U, 9U, bits, true, &workspace);
    REQUIRE(available.manifest_pages == built.metadata.page_count);
    REQUIRE(available.first_page == 1U);
    REQUIRE(available.bit_count == 9U);
    REQUIRE(available.available_count == 9U);
    for (std::size_t index = 0U; index < 9U; ++index) {
        REQUIRE(bit(bits, index));
    }
    REQUIRE(!bit(bits, 9U));

    std::array<toxsync::PagedContentPageRef, 1U> page{};
    toxsync::PagedContentPageWindowOptions read_options;
    read_options.verify_root_manifest = true;
    const auto loaded = toxsync::read_paged_content_page_window(
        temp.path() / "artifact.txp", 4U, page, workspace, read_options);
    REQUIRE(loaded.pages_loaded == 1U);
    std::filesystem::remove(toxsync::content_store_path(
        temp.path() / "store", page.front().digest));

    bits.fill(std::byte{0xff});
    available = toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact.txp", temp.path() / "store",
        1U, 9U, bits, false, &workspace);
    REQUIRE(available.bit_count == 9U);
    REQUIRE(available.available_count == 8U);
    REQUIRE(!bit(bits, 3U));
    REQUIRE(!bit(bits, 9U));

    REQUIRE_THROWS(toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact.txp", temp.path() / "store",
        0U, 9U, std::span<std::byte>(bits).first(1U), false, &workspace));
}

TOXSYNC_TEST(paged_content_auto_scaling_bounds_root_metadata_for_sixteen_tib) {
    constexpr std::uint64_t sixteen_tib =
        16ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;
    toxsync::PagedContentStoreOptions options;
    options.auto_chunking = true;
    options.root_metadata_budget_bytes = 64ULL * 1024ULL * 1024ULL;
    const auto estimate = toxsync::estimate_paged_content_scale(
        sixteen_tib, options);
    REQUIRE(estimate.maximum_root_bytes <=
            options.root_metadata_budget_bytes);
    REQUIRE(estimate.maximum_pages <= (1ULL << 32U));
    REQUIRE(estimate.chunking.max_bytes <= options.limits.max_chunk_bytes);
    REQUIRE(std::has_single_bit(estimate.chunking.average_bytes));
    REQUIRE(estimate.maximum_distributed_metadata_bytes >
            estimate.maximum_root_bytes);
}

TOXSYNC_TEST(paged_content_chunk_windows_seek_only_to_intersecting_pages) {
    test::TempDir temp;
    const auto artifact = test::pattern(4U * 1024U * 1024U + 113U, 0x9090U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    options.entries_per_page = 8U;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);

    ChunkCollector expected;
    (void)toxsync::walk_paged_content_manifest(
        temp.path() / "artifact.txp", temp.path() / "store", workspace,
        nullptr, nullptr, &ChunkCollector::collect, &expected);
    std::vector<toxsync::ContentChunkRef> actual;
    actual.reserve(expected.chunks.size());
    std::array<toxsync::ContentChunkRef, 11U> window{};
    std::uint64_t first{};
    std::uint64_t pages_read{};
    while (first < built.metadata.chunk_count) {
        toxsync::ContentChunkWindowOptions window_options;
        window_options.verify_page_digests = true;
        window_options.manifest_buffer_bytes = 80U;
        const auto loaded = toxsync::read_content_chunk_window(
            temp.path() / "artifact.txp", temp.path() / "store", first,
            window, workspace, window_options);
        REQUIRE(loaded.chunks_loaded != 0U);
        REQUIRE(loaded.page_objects_read <= 3U);
        pages_read += loaded.page_objects_read;
        actual.insert(actual.end(), window.begin(),
                      window.begin() + loaded.chunks_loaded);
        first = loaded.next_chunk;
    }
    REQUIRE(actual == expected.chunks);
    REQUIRE(pages_read < built.metadata.page_count * 3U);
}

TOXSYNC_TEST(paged_content_chunk_window_fails_closed_when_required_page_is_missing) {
    test::TempDir temp;
    const auto artifact = test::pattern(1024U * 1024U + 9U, 0x7575U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    toxsync::ContentStoreWorkspace workspace;
    (void)toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);
    PageCollector pages;
    (void)toxsync::scan_missing_paged_content_chunks(
        temp.path() / "artifact.txp", temp.path() / "empty", workspace,
        &PageCollector::collect, &pages);
    REQUIRE(!pages.pages.empty());
    std::filesystem::remove(toxsync::content_store_path(
        temp.path() / "store", pages.pages.front().digest));
    std::array<toxsync::ContentChunkRef, 4U> window{};
    REQUIRE_THROWS(toxsync::read_content_chunk_window(
        temp.path() / "artifact.txp", temp.path() / "store", 0U,
        window, workspace, {}));
}

TOXSYNC_TEST(paged_content_page_windows_bootstrap_without_page_objects) {
    test::TempDir temp;
    const auto artifact = test::pattern(3U * 1024U * 1024U, 0x4242U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    options.entries_per_page = 4U;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);

    std::vector<toxsync::PagedContentPageRef> actual;
    std::array<toxsync::PagedContentPageRef, 3U> window{};
    std::uint64_t first{};
    while (first < built.metadata.page_count) {
        toxsync::PagedContentPageWindowOptions read_options;
        read_options.verify_root_manifest = first == 0U;
        read_options.root_buffer_bytes = 160U;
        const auto loaded = toxsync::read_paged_content_page_window(
            temp.path() / "artifact.txp", first, window, workspace,
            read_options);
        actual.insert(actual.end(), window.begin(),
                      window.begin() + loaded.pages_loaded);
        first = loaded.next_page;
    }
    REQUIRE(actual.size() == built.metadata.page_count);
    REQUIRE(actual.front().first_chunk == 0U);
    REQUIRE(actual.back().artifact_offset + actual.back().artifact_bytes ==
            artifact.size());
}

TOXSYNC_TEST(paged_content_page_availability_bootstraps_in_bounded_batches) {
    test::TempDir temp;
    const auto artifact = test::pattern(5U * 1024U * 1024U + 73U, 0x7a71U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = paged_options();
    options.entries_per_page = 4U;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_paged_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txp", workspace, options);
    REQUIRE(built.metadata.page_count > 8U);

    std::vector<std::byte> bits(
        static_cast<std::size_t>((built.metadata.page_count + 7U) / 8U));
    const auto complete = toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact.txp", temp.path() / "store", 0U,
        static_cast<std::uint32_t>(built.metadata.page_count), bits,
        true, &workspace);
    REQUIRE(complete.manifest_pages == built.metadata.page_count);
    REQUIRE(complete.bit_count == built.metadata.page_count);
    REQUIRE(complete.available_count == built.metadata.page_count);
    for (std::size_t index = 0U; index < complete.bit_count; ++index) {
        REQUIRE(bit(bits, index));
    }

    std::array<toxsync::PagedContentPageRef, 1U> page{};
    const auto first = toxsync::read_paged_content_page_window(
        temp.path() / "artifact.txp", 3U, page, workspace);
    REQUIRE(first.pages_loaded == 1U);
    std::filesystem::remove(toxsync::content_store_path(
        temp.path() / "store", page.front().digest));

    std::fill(bits.begin(), bits.end(), std::byte{0xff});
    const auto partial = toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact.txp", temp.path() / "store", 2U, 5U,
        std::span<std::byte>(bits.data(), 1U), false, &workspace);
    REQUIRE(partial.first_page == 2U);
    REQUIRE(partial.bit_count == 5U);
    REQUIRE(partial.available_count == 4U);
    REQUIRE(bit(bits, 0U));
    REQUIRE(!bit(bits, 1U));
    REQUIRE(bit(bits, 2U));
    REQUIRE(bit(bits, 3U));
    REQUIRE(bit(bits, 4U));
    REQUIRE((std::to_integer<unsigned char>(bits[0U]) & 0xe0U) == 0U);

    REQUIRE_THROWS(toxsync::fill_paged_content_page_availability(
        temp.path() / "artifact", temp.path() / "store", 0U, 1U,
        std::span<std::byte>(bits.data(), 1U), false, &workspace));
}
