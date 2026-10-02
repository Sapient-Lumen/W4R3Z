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

toxsync::ContentStoreOptions fast_options() {
    toxsync::ContentStoreOptions options;
    options.chunking = {.min_bytes = 4096U,
                        .average_bytes = 16384U,
                        .max_bytes = 65536U};
    options.io_buffer_bytes = 32768U;
    options.manifest_buffer_bytes = 4096U;
    options.fsync_on_commit = false;
    return options;
}

struct MissingCollector {
    std::vector<toxsync::ContentChunkRef> chunks;

    static void collect(void* context, const toxsync::ContentChunkRef& chunk) {
        static_cast<MissingCollector*>(context)->chunks.push_back(chunk);
    }
};

struct CancellationProbe {
    std::size_t checks{};
    std::size_t cancel_after{};

    static bool check(void* context) noexcept {
        auto& probe = *static_cast<CancellationProbe*>(context);
        ++probe.checks;
        return probe.checks >= probe.cancel_after;
    }
};

} // namespace

TOXSYNC_TEST(content_store_builds_scans_and_reconstructs_exact_artifact) {
    test::TempDir temp;
    const auto artifact = test::pattern(3U * 1024U * 1024U + 719U, 0x0c0ffeeU);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    toxsync::ContentStoreWorkspace workspace;

    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        workspace, options);
    REQUIRE(built.metadata.artifact_size == artifact.size());
    REQUIRE(built.metadata.chunk_count > 1U);
    REQUIRE(built.chunks_created == built.metadata.chunk_count);
    REQUIRE(std::filesystem::exists(toxsync::content_store_path(
        temp.path() / "store", built.metadata.manifest_digest)));

    const auto scanned = toxsync::scan_missing_content_chunks(
        temp.path() / "artifact.txc", temp.path() / "store", workspace);
    REQUIRE(scanned.missing_chunks == 0U);
    REQUIRE(scanned.available_chunks == built.metadata.chunk_count);
    REQUIRE(scanned.available_bytes == artifact.size());

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.io_buffer_bytes = 32768U;
    reconstruct.fsync_on_commit = false;
    const auto rebuilt = toxsync::reconstruct_content_manifest(
        temp.path() / "artifact.txc", temp.path() / "store", temp.path() / "rebuilt",
        workspace, reconstruct);
    REQUIRE(rebuilt.metadata.artifact_digest == built.metadata.artifact_digest);
    REQUIRE(rebuilt.chunks_read == built.metadata.chunk_count);
    REQUIRE(test::read_file(temp.path() / "rebuilt") == artifact);
}

TOXSYNC_TEST(content_reconstruction_cancellation_is_bounded_and_never_publishes) {
    test::TempDir temp;
    const auto artifact = test::pattern(4U * 1024U * 1024U + 17U, 0xca11ce11U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    options.io_buffer_bytes = 4096U;
    toxsync::ContentStoreWorkspace workspace;
    (void)toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txc", workspace, options);

    CancellationProbe probe{.cancel_after = 4U};
    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.io_buffer_bytes = 4096U;
    reconstruct.fsync_on_commit = false;
    reconstruct.cancellation_check = &CancellationProbe::check;
    reconstruct.cancellation_context = &probe;
    bool cancelled{};
    try {
        (void)toxsync::reconstruct_content_manifest(
            temp.path() / "artifact.txc", temp.path() / "store",
            temp.path() / "rebuilt", workspace, reconstruct);
    } catch (const toxsync::ContentOperationCancelled&) {
        cancelled = true;
    }
    REQUIRE(cancelled);
    REQUIRE(probe.checks >= probe.cancel_after);
    REQUIRE(!std::filesystem::exists(temp.path() / "rebuilt"));
    REQUIRE(!std::filesystem::exists(temp.path() / "rebuilt.toxsync.part"));
}

TOXSYNC_TEST(content_store_reuses_chunks_after_prefix_insertion) {
    test::TempDir temp;
    const auto basis = test::pattern(8U * 1024U * 1024U, 0x515151U);
    const auto prefix = test::pattern(12345U, 0xa11ceU);
    std::vector<std::byte> target;
    target.reserve(prefix.size() + basis.size() + 97U);
    target.insert(target.end(), prefix.begin(), prefix.end());
    target.insert(target.end(), basis.begin(), basis.end());
    const auto suffix = test::pattern(97U, 0xbeefU);
    target.insert(target.end(), suffix.begin(), suffix.end());
    test::write_file(temp.path() / "basis", basis);
    test::write_file(temp.path() / "target", target);

    auto options = fast_options();
    toxsync::ContentStoreWorkspace workspace;
    const auto first = toxsync::build_content_store(
        temp.path() / "basis", temp.path() / "store", temp.path() / "basis.txc",
        workspace, options);
    const auto second = toxsync::build_content_store(
        temp.path() / "target", temp.path() / "store", temp.path() / "target.txc",
        workspace, options);

    REQUIRE(first.chunks_created == first.metadata.chunk_count);
    REQUIRE(second.bytes_reused > basis.size() * 9U / 10U);
    REQUIRE(second.chunks_reused > second.chunks_created);
}

TOXSYNC_TEST(content_store_inventory_streams_missing_chunks_without_manifest_vector) {
    test::TempDir temp;
    const auto artifact = test::pattern(1024U * 1024U + 13U, 0x101010U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    options.publish_manifest_to_store = false;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        workspace, options);

    MissingCollector collector;
    const auto first = toxsync::scan_missing_content_chunks(
        temp.path() / "artifact.txc", temp.path() / "empty-store", workspace,
        &MissingCollector::collect, &collector);
    REQUIRE(first.missing_chunks == built.metadata.chunk_count);
    REQUIRE(first.missing_bytes == artifact.size());
    REQUIRE(collector.chunks.size() == built.metadata.chunk_count);
    REQUIRE(collector.chunks.front().artifact_offset == 0U);
}

TOXSYNC_TEST(content_store_rejects_corrupt_chunk_and_never_publishes_output) {
    test::TempDir temp;
    const auto artifact = test::pattern(700000U, 0x777U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        workspace, options);

    MissingCollector collector;
    (void)toxsync::scan_missing_content_chunks(
        temp.path() / "artifact.txc", temp.path() / "empty", workspace,
        &MissingCollector::collect, &collector);
    REQUIRE(!collector.chunks.empty());
    const auto corrupt_path = toxsync::content_store_path(
        temp.path() / "store", collector.chunks.front().digest);
    auto corrupt = test::read_file(corrupt_path);
    corrupt[0] ^= std::byte{0xff};
    test::write_file(corrupt_path, corrupt);

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.fsync_on_commit = false;
    REQUIRE_THROWS(toxsync::reconstruct_content_manifest(
        temp.path() / "artifact.txc", temp.path() / "store", temp.path() / "output",
        workspace, reconstruct));
    REQUIRE(!std::filesystem::exists(temp.path() / "output"));

    toxsync::ContentStoreScanOptions strict_scan;
    strict_scan.verify_chunk_digests = true;
    const auto scanned = toxsync::scan_missing_content_chunks(
        temp.path() / "artifact.txc", temp.path() / "store", workspace,
        nullptr, nullptr, strict_scan);
    REQUIRE(scanned.corrupt_chunks == 1U);
    REQUIRE(scanned.missing_chunks == 1U);
    REQUIRE(scanned.metadata.chunk_count == built.metadata.chunk_count);
}

TOXSYNC_TEST(content_store_workspace_stops_growing_after_warmup) {
    test::TempDir temp;
    const auto first = test::pattern(2U * 1024U * 1024U, 0xabc1U);
    const auto second = test::pattern(first.size(), 0xabc2U);
    test::write_file(temp.path() / "first", first);
    test::write_file(temp.path() / "second", second);
    auto options = fast_options();
    toxsync::ContentStoreWorkspace workspace;

    const auto cold = toxsync::build_content_store(
        temp.path() / "first", temp.path() / "store", temp.path() / "first.txc",
        workspace, options);
    const auto retained = workspace.resident_bytes();
    const auto warm = toxsync::build_content_store(
        temp.path() / "second", temp.path() / "store", temp.path() / "second.txc",
        workspace, options);
    REQUIRE(cold.workspace_growth_events == 3U);
    REQUIRE(warm.workspace_growth_events == 0U);
    REQUIRE(cold.workspace_reserved_bytes == retained);
    REQUIRE(warm.workspace_reserved_bytes == retained);

    workspace.release();
    REQUIRE(workspace.resident_bytes() == 0U);
}

TOXSYNC_TEST(content_manifest_rejects_reserved_header_mutation) {
    test::TempDir temp;
    const auto artifact = test::pattern(100000U, 0x123U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    options.publish_manifest_to_store = false;
    options.fsync_on_commit = false;
    (void)toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        options);
    auto manifest = test::read_file(temp.path() / "artifact.txc");
    manifest[127] = std::byte{1};
    test::write_file(temp.path() / "bad.txc", manifest);
    REQUIRE_THROWS(toxsync::inspect_content_manifest(temp.path() / "bad.txc"));
}

TOXSYNC_TEST(content_auto_chunking_bounds_sixteen_tib_worst_case_manifest) {
    constexpr std::uint64_t sixteen_tib = 16ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;
    toxsync::ContentChunkingAutoOptions options;
    options.metadata_budget_bytes = 64ULL * 1024ULL * 1024ULL;
    const auto estimate = toxsync::estimate_content_scale(sixteen_tib, options);
    REQUIRE(estimate.artifact_size == sixteen_tib);
    REQUIRE(estimate.maximum_manifest_bytes <= options.metadata_budget_bytes);
    REQUIRE(estimate.maximum_chunks <= (1ULL << 32U));
    REQUIRE(estimate.chunking.min_bytes >= 16U * 1024U * 1024U);
    REQUIRE(estimate.chunking.max_bytes <= 64U * 1024U * 1024U);
    REQUIRE(std::has_single_bit(estimate.chunking.average_bytes));
}

TOXSYNC_TEST(content_auto_chunking_is_used_by_streaming_builder) {
    test::TempDir temp;
    const auto artifact = test::pattern(8U * 1024U * 1024U + 17U, 0xa070U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    options.auto_chunking = true;
    options.metadata_budget_bytes = 8192U;
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        workspace, options);
    REQUIRE(built.metadata.encoded_size() <= options.metadata_budget_bytes);
    REQUIRE(built.metadata.chunking.min_bytes > options.chunking.min_bytes);
    REQUIRE(built.metadata.chunking.max_bytes <= options.limits.max_chunk_bytes);
}

TOXSYNC_TEST(content_scan_and_reconstruct_honor_tiny_configured_buffers) {
    test::TempDir temp;
    const auto artifact = test::pattern(400000U, 0x51a7U);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    options.publish_manifest_to_store = false;
    toxsync::ContentStoreWorkspace workspace;
    (void)toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store", temp.path() / "artifact.txc",
        workspace, options);
    workspace.release();

    toxsync::ContentStoreScanOptions scan;
    scan.io_buffer_bytes = 1024U;
    scan.manifest_buffer_bytes = toxsync::ContentManifestMetadata::kEntryBytes;
    const auto scanned = toxsync::scan_missing_content_chunks(
        temp.path() / "artifact.txc", temp.path() / "store", workspace,
        nullptr, nullptr, scan);
    REQUIRE(scanned.missing_chunks == 0U);
    REQUIRE(scanned.workspace_reserved_bytes <= 8192U);

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.io_buffer_bytes = 1024U;
    reconstruct.manifest_buffer_bytes = toxsync::ContentManifestMetadata::kEntryBytes;
    reconstruct.fsync_on_commit = false;
    const auto rebuilt = toxsync::reconstruct_content_manifest(
        temp.path() / "artifact.txc", temp.path() / "store", temp.path() / "rebuilt",
        workspace, reconstruct);
    REQUIRE(rebuilt.workspace_reserved_bytes <= 8192U);
    REQUIRE(test::read_file(temp.path() / "rebuilt") == artifact);
}

TOXSYNC_TEST(content_object_install_consumes_private_staging_file_without_payload_copy) {
    test::TempDir temp;
    const auto payload = test::pattern(512U * 1024U + 31U, 0x1a57a11U);
    const auto digest = toxsync::sha256(payload);
    test::write_file(temp.path() / "incoming.part", payload);

    toxsync::ContentStoreWorkspace workspace;
    toxsync::ContentObjectInstallOptions options;
    options.fsync_on_commit = false;
    options.consume_source = true;
    options.prefer_hard_link = true;
    const auto installed = toxsync::install_content_object(
        temp.path() / "incoming.part", temp.path() / "store", digest,
        payload.size(), workspace, options);
    REQUIRE(installed.method ==
            toxsync::ContentObjectInstallMethod::moved_by_hard_link);
    REQUIRE(installed.bytes_verified == payload.size());
    REQUIRE(installed.bytes_copied == 0U);
    REQUIRE(!std::filesystem::exists(temp.path() / "incoming.part"));
    const auto stored = toxsync::content_store_path(temp.path() / "store", digest);
    REQUIRE(test::read_file(stored) == payload);
    REQUIRE(toxsync::content_object_available(
        temp.path() / "store", digest, payload.size(), true, &workspace, 4096U));

    test::write_file(temp.path() / "duplicate.part", payload);
    const auto reused = toxsync::install_content_object(
        temp.path() / "duplicate.part", temp.path() / "store", digest,
        payload.size(), workspace, options);
    REQUIRE(reused.method ==
            toxsync::ContentObjectInstallMethod::reused_existing);
    REQUIRE(!std::filesystem::exists(temp.path() / "duplicate.part"));
}

TOXSYNC_TEST(content_object_install_rejects_wrong_digest_without_consuming_source) {
    test::TempDir temp;
    const auto payload = test::pattern(65537U, 0xbadU);
    test::write_file(temp.path() / "incoming.part", payload);
    const auto wrong = toxsync::sha256(test::pattern(payload.size(), 0xfeedU));
    toxsync::ContentObjectInstallOptions options;
    options.fsync_on_commit = false;
    REQUIRE_THROWS(toxsync::install_content_object(
        temp.path() / "incoming.part", temp.path() / "store", wrong,
        payload.size(), options));
    REQUIRE(std::filesystem::exists(temp.path() / "incoming.part"));
    REQUIRE(!std::filesystem::exists(
        toxsync::content_store_path(temp.path() / "store", wrong)));
}

TOXSYNC_TEST(content_object_install_can_publish_a_preverified_private_source_without_rereading_it) {
    test::TempDir temp;
    const auto payload = test::pattern(2U * 1024U * 1024U + 17U, 0x51eedU);
    const auto digest = toxsync::sha256(payload);
    const auto incoming = temp.path() / "preverified.part";
    test::write_file(incoming, payload);

    toxsync::ContentStoreWorkspace workspace;
    toxsync::ContentObjectInstallOptions options;
    options.fsync_on_commit = false;
    options.consume_source = true;
    options.prefer_hard_link = true;
    options.source_preverified = true;
    const auto installed = toxsync::install_content_object(
        incoming, temp.path() / "store", digest, payload.size(), workspace,
        options);

    REQUIRE(installed.method ==
            toxsync::ContentObjectInstallMethod::moved_by_hard_link);
    REQUIRE(installed.bytes_verified == payload.size());
    REQUIRE(installed.read_calls == 0U);
    REQUIRE(installed.bytes_copied == 0U);
    REQUIRE(!std::filesystem::exists(incoming));
    REQUIRE(test::read_file(
        toxsync::content_store_path(temp.path() / "store", digest)) == payload);
}

TOXSYNC_TEST(flat_content_chunk_windows_are_bounded_and_sequentially_hintable) {
    test::TempDir temp;
    const auto artifact = test::pattern(2U * 1024U * 1024U + 777U, 0xc001dU);
    test::write_file(temp.path() / "artifact", artifact);
    auto options = fast_options();
    toxsync::ContentStoreWorkspace workspace;
    const auto built = toxsync::build_content_store(
        temp.path() / "artifact", temp.path() / "store",
        temp.path() / "artifact.txc", workspace, options);

    MissingCollector expected;
    (void)toxsync::walk_content_manifest(
        temp.path() / "artifact.txc", workspace,
        &MissingCollector::collect, &expected);
    std::vector<toxsync::ContentChunkRef> actual;
    actual.reserve(expected.chunks.size());
    std::array<toxsync::ContentChunkRef, 7U> window{};
    std::uint64_t first{};
    std::uint64_t offset{};
    bool have_offset{};
    while (first < built.metadata.chunk_count) {
        toxsync::ContentChunkWindowOptions window_options;
        window_options.artifact_offset_hint_valid = have_offset;
        window_options.artifact_offset_hint = offset;
        window_options.manifest_buffer_bytes = 80U;
        const auto loaded = toxsync::read_content_chunk_window(
            temp.path() / "artifact.txc", temp.path() / "store", first,
            window, workspace, window_options);
        REQUIRE(loaded.chunks_loaded != 0U);
        REQUIRE(loaded.prefix_entries_scanned == 0U);
        actual.insert(actual.end(), window.begin(),
                      window.begin() + loaded.chunks_loaded);
        first = loaded.next_chunk;
        offset = loaded.next_artifact_offset;
        have_offset = true;
    }
    REQUIRE(actual == expected.chunks);
    REQUIRE(offset == artifact.size());

    std::array<toxsync::ContentChunkRef, 3U> arbitrary{};
    const auto rescanned = toxsync::read_content_chunk_window(
        temp.path() / "artifact.txc", temp.path() / "store", 5U,
        arbitrary, workspace, {});
    REQUIRE(rescanned.prefix_entries_scanned == 5U);
    REQUIRE(arbitrary.front() == expected.chunks[5U]);
}
