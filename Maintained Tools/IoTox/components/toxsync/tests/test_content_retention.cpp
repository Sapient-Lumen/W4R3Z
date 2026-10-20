#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/content_retention.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <span>
#include <string>
#include <vector>

namespace {

toxsync::Digest256 digest_text(const char* text) {
    return toxsync::sha256(std::as_bytes(std::span(text, std::char_traits<char>::length(text))));
}

} // namespace

TOXSYNC_TEST(content_pin_ledger_replays_repairs_torn_tail_and_rejects_fork) {
    test::TempDir temp;
    const auto journal = temp.path() / "pins.txp";
    const auto namespace_a = digest_text("namespace-a");
    const auto namespace_b = digest_text("namespace-b");
    const auto manifest_a = digest_text("manifest-a");
    const auto manifest_b = digest_text("manifest-b");
    {
        toxsync::ContentPinLedger ledger(journal);
        toxsync::ContentPin first{
            .namespace_id = namespace_a,
            .generation = 1U,
            .manifest = manifest_a,
            .retain_until_unix_seconds = 0U,
            .flags = toxsync::kContentPinCurrent,
        };
        REQUIRE(ledger.upsert(first) == toxsync::ContentPinUpdate::inserted);
        REQUIRE(ledger.upsert(first) == toxsync::ContentPinUpdate::unchanged);
        auto updated = first;
        updated.flags = toxsync::kContentPinCurrent |
                        toxsync::kContentPinBaseline;
        REQUIRE(ledger.upsert(updated) == toxsync::ContentPinUpdate::updated);
        auto fork = updated;
        fork.manifest = manifest_b;
        REQUIRE(ledger.upsert(fork) == toxsync::ContentPinUpdate::fork_rejected);
        REQUIRE(ledger.upsert(toxsync::ContentPin{
                    .namespace_id = namespace_b,
                    .generation = 9U,
                    .manifest = manifest_b,
                    .retain_until_unix_seconds = 0U,
                    .flags = toxsync::kContentPinRecent,
                }) == toxsync::ContentPinUpdate::inserted);
        REQUIRE(ledger.stats().active_pins == 2U);
    }

    {
        std::ofstream output(journal, std::ios::binary | std::ios::app);
        const std::array<char, 17> torn{};
        output.write(torn.data(), static_cast<std::streamsize>(torn.size()));
    }
    {
        toxsync::ContentPinLedger ledger(journal);
        REQUIRE(ledger.stats().ignored_torn_tail_bytes == 17U);
        REQUIRE(ledger.stats().active_pins == 2U);
        REQUIRE(std::filesystem::file_size(journal) % 160U == 0U);
        REQUIRE(ledger.erase(namespace_b, 9U));
        REQUIRE(!ledger.erase(namespace_b, 9U));
        ledger.compact();
        REQUIRE(ledger.stats().journal_bytes == 160U);
    }
    toxsync::ContentPinLedger reopened(journal);
    REQUIRE(reopened.stats().active_pins == 1U);
    const auto found = reopened.find(namespace_a, 1U);
    REQUIRE(found.has_value());
    REQUIRE((found->flags & toxsync::kContentPinBaseline) != 0U);
}

TOXSYNC_TEST(content_gc_conservatively_keeps_pinned_revision_and_removes_garbage) {
    test::TempDir temp;
    const auto store = temp.path() / "store";
    const auto artifact_a = temp.path() / "a.bin";
    const auto artifact_b = temp.path() / "b.bin";
    const auto manifest_a = temp.path() / "a.txc";
    const auto manifest_b = temp.path() / "b.txc";
    const auto output_a = temp.path() / "a.out";
    const auto output_b = temp.path() / "b.out";
    const auto bytes_a = test::pattern(3U * 1024U * 1024U, 0x1111U);
    const auto bytes_b = test::pattern(3U * 1024U * 1024U, 0x9999U);
    test::write_file(artifact_a, bytes_a);
    test::write_file(artifact_b, bytes_b);

    toxsync::ContentStoreOptions build_options;
    build_options.chunking = {.min_bytes = 4096U,
                              .average_bytes = 8192U,
                              .max_bytes = 16384U};
    build_options.fsync_on_commit = false;
    const auto built_a = toxsync::build_content_store(
        artifact_a, store, manifest_a, build_options);
    const auto built_b = toxsync::build_content_store(
        artifact_b, store, manifest_b, build_options);
    REQUIRE(built_a.metadata.manifest_digest != built_b.metadata.manifest_digest);

    toxsync::ContentPinLedgerOptions ledger_options;
    ledger_options.fsync_on_commit = false;
    toxsync::ContentPinLedger ledger(temp.path() / "pins.txp", ledger_options);
    REQUIRE(ledger.upsert(toxsync::ContentPin{
                .namespace_id = digest_text("namespace-a"),
                .generation = 1U,
                .manifest = built_a.metadata.manifest_digest,
                .retain_until_unix_seconds = 0U,
                .flags = toxsync::kContentPinCurrent,
            }) == toxsync::ContentPinUpdate::inserted);

    toxsync::ContentGcOptions gc_options;
    gc_options.maximum_store_bytes = 1U;
    gc_options.target_store_bytes = 1U;
    gc_options.minimum_unpinned_age_seconds = 0U;
    gc_options.reachability_filter_bytes = 16U * 1024U;
    gc_options.dry_run = false;
    const auto collected = toxsync::collect_content_store(
        store, ledger, gc_options);
    REQUIRE(collected.active_pins == 1U);
    REQUIRE(collected.pinned_manifests == 1U);
    REQUIRE(collected.deleted_files > 0U);
    REQUIRE(collected.deleted_bytes > 0U);
    REQUIRE(std::filesystem::exists(toxsync::content_store_path(
        store, built_a.metadata.manifest_digest)));

    toxsync::ContentReconstructOptions reconstruct_options;
    reconstruct_options.fsync_on_commit = false;
    const auto reconstructed = toxsync::reconstruct_content_manifest(
        manifest_a, store, output_a, reconstruct_options);
    REQUIRE(reconstructed.metadata.artifact_digest ==
            built_a.metadata.artifact_digest);
    REQUIRE(test::read_file(output_a) == bytes_a);
    REQUIRE_THROWS(toxsync::reconstruct_content_manifest(
        manifest_b, store, output_b, reconstruct_options));
}

TOXSYNC_TEST(content_gc_dry_run_reports_without_removing_candidates) {
    test::TempDir temp;
    const auto store = temp.path() / "store";
    const auto artifact = temp.path() / "artifact.bin";
    const auto manifest = temp.path() / "artifact.txc";
    test::write_file(artifact, test::pattern(512U * 1024U, 0x55U));
    toxsync::ContentStoreOptions build_options;
    build_options.fsync_on_commit = false;
    (void)toxsync::build_content_store(artifact, store, manifest, build_options);

    toxsync::ContentStoreWorkspace workspace;
    toxsync::ContentGcOptions options;
    options.maximum_store_bytes = 1U;
    options.target_store_bytes = 1U;
    options.minimum_unpinned_age_seconds = 0U;
    options.reachability_filter_bytes = 4096U;
    options.dry_run = true;
    const auto before = std::filesystem::file_size(manifest);
    const auto stats = toxsync::collect_content_store(
        store, std::span<const toxsync::ContentPin>{}, workspace, options);
    REQUIRE(stats.dry_run);
    REQUIRE(stats.deleted_files > 0U);
    REQUIRE(stats.deleted_bytes > 0U);
    REQUIRE(std::filesystem::file_size(manifest) == before);
}

TOXSYNC_TEST(content_gc_marks_paged_roots_pages_and_chunks_before_collection) {
    test::TempDir temp;
    const auto store = temp.path() / "store";
    const auto kept_artifact = temp.path() / "kept.bin";
    const auto garbage_artifact = temp.path() / "garbage.bin";
    const auto kept_root = temp.path() / "kept.txp";
    const auto garbage_root = temp.path() / "garbage.txp";
    const auto kept_bytes = test::pattern(2U * 1024U * 1024U, 0xabcU);
    const auto garbage_bytes = test::pattern(2U * 1024U * 1024U, 0xdefU);
    test::write_file(kept_artifact, kept_bytes);
    test::write_file(garbage_artifact, garbage_bytes);

    toxsync::PagedContentStoreOptions build_options;
    build_options.chunking = {.min_bytes = 4096U,
                              .average_bytes = 8192U,
                              .max_bytes = 32768U};
    build_options.entries_per_page = 8U;
    build_options.fsync_on_commit = false;
    const auto kept = toxsync::build_paged_content_store(
        kept_artifact, store, kept_root, build_options);
    const auto garbage = toxsync::build_paged_content_store(
        garbage_artifact, store, garbage_root, build_options);
    REQUIRE(kept.metadata.root_digest != garbage.metadata.root_digest);

    toxsync::ContentPinLedgerOptions ledger_options;
    ledger_options.fsync_on_commit = false;
    toxsync::ContentPinLedger ledger(temp.path() / "pins.txp", ledger_options);
    REQUIRE(ledger.upsert(toxsync::ContentPin{
                .namespace_id = digest_text("paged-namespace"),
                .generation = 4U,
                .manifest = kept.metadata.root_digest,
                .retain_until_unix_seconds = 0U,
                .flags = toxsync::kContentPinCurrent,
            }) == toxsync::ContentPinUpdate::inserted);

    toxsync::ContentGcOptions gc_options;
    gc_options.maximum_store_bytes = 1U;
    gc_options.target_store_bytes = 1U;
    gc_options.minimum_unpinned_age_seconds = 0U;
    gc_options.reachability_filter_bytes = 64U * 1024U;
    gc_options.manifest_buffer_bytes = 4096U;
    const auto collected = toxsync::collect_content_store(
        store, ledger, gc_options);
    REQUIRE(collected.pinned_manifests == 1U);
    REQUIRE(collected.reachable_page_references == kept.metadata.page_count);
    REQUIRE(collected.reachable_chunk_references == kept.metadata.chunk_count);
    REQUIRE(collected.deleted_files > 0U);
    REQUIRE(std::filesystem::exists(toxsync::content_store_path(
        store, kept.metadata.root_digest)));

    toxsync::ContentReconstructOptions reconstruct;
    reconstruct.fsync_on_commit = false;
    reconstruct.manifest_buffer_bytes = 4096U;
    (void)toxsync::reconstruct_paged_content_manifest(
        kept_root, store, temp.path() / "kept.out", reconstruct);
    REQUIRE(test::read_file(temp.path() / "kept.out") == kept_bytes);
    REQUIRE_THROWS(toxsync::reconstruct_paged_content_manifest(
        garbage_root, store, temp.path() / "garbage.out", reconstruct));
}
