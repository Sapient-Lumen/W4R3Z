#pragma once

#include "toxsync/hash.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <stdexcept>

namespace toxsync {

// Preview format for the planned casync/desync-style engine. The format is
// intentionally independent of the v1 range index so v1 remains small and
// byte-stable while v2 evolves.
struct ContentChunking {
    std::uint32_t min_bytes{64U * 1024U};
    std::uint32_t average_bytes{256U * 1024U};
    std::uint32_t max_bytes{1024U * 1024U};
};

struct ContentStoreLimits {
    std::uint64_t max_artifact_size{1ULL << 48U};
    std::uint64_t max_chunks{1ULL << 32U};
    std::uint32_t min_chunk_bytes{1024U};
    std::uint32_t max_chunk_bytes{64U * 1024U * 1024U};
};

struct ContentChunkingAutoOptions {
    // The bound is checked against the worst case implied by min_bytes, not
    // merely the expected average. This prevents a low-entropy or adversarial
    // artifact from silently producing an enormous flat manifest.
    std::uint64_t metadata_budget_bytes{64ULL * 1024ULL * 1024ULL};
    ContentChunking preferred{};
};

struct ContentScaleEstimate {
    std::uint64_t artifact_size{};
    ContentChunking chunking{};
    std::uint64_t maximum_chunks{};
    std::uint64_t maximum_manifest_bytes{};
};

[[nodiscard]] ContentScaleEstimate estimate_content_scale(
    std::uint64_t artifact_size,
    const ContentChunkingAutoOptions& options = {},
    const ContentStoreLimits& limits = {});

[[nodiscard]] ContentChunking choose_content_chunking(
    std::uint64_t artifact_size,
    const ContentChunkingAutoOptions& options = {},
    const ContentStoreLimits& limits = {});

struct ContentManifestMetadata {
    static constexpr std::uint16_t kFormatVersion = 1U;
    static constexpr std::size_t kHeaderBytes = 128U;
    static constexpr std::size_t kEntryBytes = 40U;

    ContentChunking chunking{};
    std::uint64_t artifact_size{};
    std::uint64_t chunk_count{};
    Digest256 artifact_digest{};
    Digest256 entries_digest{};
    Digest256 manifest_digest{};

    [[nodiscard]] std::uint64_t encoded_size() const noexcept;
};

struct ContentStoreOptions {
    ContentChunking chunking{};
    bool auto_chunking{false};
    std::uint64_t metadata_budget_bytes{64ULL * 1024ULL * 1024ULL};
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    bool fsync_on_commit{true};
    bool advise_sequential_io{true};
    bool discard_input_cache{false};
    bool publish_manifest_to_store{true};
    bool verify_existing_chunks{true};
    ContentStoreLimits limits{};
};

// One retained arena is sufficient for build, inventory scanning, and
// reconstruction. Its capacity is bounded by max chunk size + I/O buffer, not
// by artifact or manifest size.
class ContentStoreWorkspace final {
public:
    ContentStoreWorkspace() = default;
    ~ContentStoreWorkspace() = default;
    ContentStoreWorkspace(ContentStoreWorkspace&&) noexcept = default;
    ContentStoreWorkspace& operator=(ContentStoreWorkspace&&) noexcept = default;
    ContentStoreWorkspace(const ContentStoreWorkspace&) = delete;
    ContentStoreWorkspace& operator=(const ContentStoreWorkspace&) = delete;

    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return io_capacity_ + chunk_capacity_ + record_capacity_;
    }
    void release() noexcept {
        io_.reset();
        chunk_.reset();
        records_.reset();
        io_capacity_ = 0U;
        chunk_capacity_ = 0U;
        record_capacity_ = 0U;
    }

private:
    friend struct ContentStoreWorkspaceAccess;
    friend struct PagedContentWorkspaceAccess;
    std::unique_ptr<std::byte[]> io_{};
    std::unique_ptr<std::byte[]> chunk_{};
    std::unique_ptr<std::byte[]> records_{};
    std::size_t io_capacity_{};
    std::size_t chunk_capacity_{};
    std::size_t record_capacity_{};
};

struct ContentStoreBuildStats {
    ContentManifestMetadata metadata{};
    std::uint64_t input_read_calls{};
    std::uint64_t manifest_write_calls{};
    std::uint64_t chunks_created{};
    std::uint64_t chunks_reused{};
    std::uint64_t bytes_created{};
    std::uint64_t bytes_reused{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

struct ContentChunkRef {
    std::uint64_t index{};
    std::uint64_t artifact_offset{};
    std::uint32_t length{};
    Digest256 digest{};
    friend constexpr bool operator==(const ContentChunkRef&,
                                     const ContentChunkRef&) = default;
};

using ContentChunkCallback = void (*)(void* context,
                                      const ContentChunkRef& chunk);
using MissingContentChunkCallback = ContentChunkCallback;

struct ContentManifestWalkOptions {
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct ContentManifestWalkStats {
    ContentManifestMetadata metadata{};
    std::uint64_t chunks_visited{};
    std::uint64_t bytes_visited{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

struct ContentStoreScanOptions {
    bool verify_chunk_digests{false};
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct ContentStoreScanStats {
    ContentManifestMetadata metadata{};
    std::uint64_t available_chunks{};
    std::uint64_t missing_chunks{};
    std::uint64_t available_bytes{};
    std::uint64_t missing_bytes{};
    std::uint64_t corrupt_chunks{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

using ContentCancellationCheck = bool (*)(void* context) noexcept;

class ContentOperationCancelled final : public std::runtime_error {
public:
    ContentOperationCancelled()
        : std::runtime_error("toxsync content operation cancelled") {}
};

struct ContentReconstructOptions {
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    bool fsync_on_commit{true};
    bool advise_sequential_io{true};
    bool discard_chunk_cache{false};
    // Optional allocation-free cooperative cancellation hook. Reconstruction
    // checks it at every bounded I/O iteration and before publication. The
    // context must outlive the reconstruct call.
    ContentCancellationCheck cancellation_check{};
    void* cancellation_context{};
    ContentStoreLimits limits{};

    [[nodiscard]] bool cancellation_requested() const noexcept {
        return cancellation_check != nullptr &&
               cancellation_check(cancellation_context);
    }
};

struct ContentReconstructStats {
    ContentManifestMetadata metadata{};
    std::uint64_t chunks_read{};
    std::uint64_t bytes_read{};
    std::uint64_t chunk_read_calls{};
    std::uint64_t output_write_calls{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

[[nodiscard]] std::filesystem::path content_store_path(
    const std::filesystem::path& store_root,
    const Digest256& digest);

enum class ContentObjectInstallMethod : std::uint8_t {
    reused_existing,
    moved_by_hard_link,
    copied,
};

struct ContentObjectInstallOptions {
    std::size_t io_buffer_bytes{256U * 1024U};
    bool fsync_on_commit{true};
    bool verify_existing_object{true};
    // The source must be a private completed staging file. When enabled,
    // toxsync verifies it, publishes it with hard-link + unlink on the same
    // filesystem, and falls back to a verified copy across filesystems.
    bool consume_source{true};
    bool prefer_hard_link{true};
    // The caller has already authenticated the complete private staging file
    // against expected_digest and expected_size immediately before this call.
    // This permits same-filesystem hard-link publication without reading the
    // payload a second time. The bounded cross-filesystem copy path still
    // hashes while copying, because it must authenticate the bytes that reach
    // the newly created destination. Never enable this for a peer-controlled
    // or otherwise mutable path.
    bool source_preverified{false};
};

struct ContentObjectInstallStats {
    ContentObjectInstallMethod method{ContentObjectInstallMethod::copied};
    std::uint64_t bytes_verified{};
    std::uint64_t bytes_copied{};
    std::uint64_t read_calls{};
    std::uint64_t write_calls{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

// Verifies one completed private staging object and publishes it under its
// SHA-256 identity. Same-filesystem ingest can be zero-copy at the filesystem
// level; cross-filesystem ingest streams through one bounded workspace arena.
[[nodiscard]] ContentObjectInstallStats install_content_object(
    const std::filesystem::path& source_path,
    const std::filesystem::path& store_root,
    const Digest256& expected_digest,
    std::uint64_t expected_size,
    const ContentObjectInstallOptions& options = {});

[[nodiscard]] ContentObjectInstallStats install_content_object(
    const std::filesystem::path& source_path,
    const std::filesystem::path& store_root,
    const Digest256& expected_digest,
    std::uint64_t expected_size,
    ContentStoreWorkspace& workspace,
    const ContentObjectInstallOptions& options = {});

[[nodiscard]] bool content_object_available(
    const std::filesystem::path& store_root,
    const Digest256& digest,
    std::uint64_t expected_size,
    bool verify_digest = false,
    ContentStoreWorkspace* workspace = nullptr,
    std::size_t io_buffer_bytes = 256U * 1024U);

// Streams an artifact through a content-defined chunker, stores immutable
// SHA-256-addressed chunks, and atomically publishes a compact manifest. The
// manifest itself is optionally inserted into the same store, allowing a v2
// mutable head to name it and the existing range service to distribute it.
[[nodiscard]] ContentStoreBuildStats build_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& manifest_path,
    const ContentStoreOptions& options = {});

[[nodiscard]] ContentStoreBuildStats build_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& manifest_path,
    ContentStoreWorkspace& workspace,
    const ContentStoreOptions& options = {});

[[nodiscard]] ContentManifestMetadata inspect_content_manifest(
    const std::filesystem::path& manifest_path,
    const ContentStoreLimits& limits = {});

[[nodiscard]] ContentManifestMetadata inspect_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentStoreWorkspace& workspace,
    const ContentStoreLimits& limits = {});

// Streams every manifest entry in artifact order without materializing a
// chunk-count-sized container. The callback may be null when only validated
// metadata and digest computation are required.
[[nodiscard]] ContentManifestWalkStats walk_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentChunkCallback callback = nullptr,
    void* context = nullptr,
    const ContentManifestWalkOptions& options = {});

[[nodiscard]] ContentManifestWalkStats walk_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentStoreWorkspace& workspace,
    ContentChunkCallback callback = nullptr,
    void* context = nullptr,
    const ContentManifestWalkOptions& options = {});

// Inventory is streamed and bounded. Callbacks receive missing chunks in
// artifact order; no vector proportional to chunk count is constructed.
[[nodiscard]] ContentStoreScanStats scan_missing_content_chunks(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    MissingContentChunkCallback callback = nullptr,
    void* context = nullptr,
    const ContentStoreScanOptions& options = {});

[[nodiscard]] ContentStoreScanStats scan_missing_content_chunks(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    MissingContentChunkCallback callback = nullptr,
    void* context = nullptr,
    const ContentStoreScanOptions& options = {});

// Reconstructs through a private partial file, verifies every chunk and the
// complete artifact, then atomically publishes the result.
[[nodiscard]] ContentReconstructStats reconstruct_content_manifest(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    const ContentReconstructOptions& options = {});

[[nodiscard]] ContentReconstructStats reconstruct_content_manifest(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    ContentStoreWorkspace& workspace,
    const ContentReconstructOptions& options = {});


enum class ContentManifestFormat : std::uint8_t {
    flat_v1,
    paged_v2,
};

[[nodiscard]] ContentManifestFormat detect_content_manifest_format(
    const std::filesystem::path& manifest_path);

struct PagedContentScaleEstimate {
    std::uint64_t artifact_size{};
    ContentChunking chunking{};
    std::uint32_t entries_per_page{};
    std::uint64_t maximum_chunks{};
    std::uint64_t maximum_pages{};
    std::uint64_t maximum_root_bytes{};
    std::uint64_t maximum_distributed_metadata_bytes{};
};

struct PagedContentManifestMetadata {
    static constexpr std::uint16_t kFormatVersion = 1U;
    static constexpr std::size_t kHeaderBytes = 192U;
    static constexpr std::size_t kPageRecordBytes = 80U;
    static constexpr std::size_t kPageHeaderBytes = 96U;
    static constexpr std::size_t kChunkEntryBytes =
        ContentManifestMetadata::kEntryBytes;

    ContentChunking chunking{};
    std::uint32_t entries_per_page{1024U};
    std::uint64_t artifact_size{};
    std::uint64_t chunk_count{};
    std::uint64_t page_count{};
    Digest256 artifact_digest{};
    Digest256 chunk_entries_digest{};
    Digest256 page_records_digest{};
    Digest256 root_digest{};

    [[nodiscard]] std::uint64_t encoded_size() const noexcept;
};

struct PagedContentPageRef {
    std::uint64_t page_index{};
    std::uint64_t first_chunk{};
    std::uint64_t artifact_offset{};
    std::uint64_t artifact_bytes{};
    std::uint32_t chunk_count{};
    std::uint32_t encoded_size{};
    Digest256 digest{};
};

struct PagedContentStoreOptions {
    ContentChunking chunking{};
    bool auto_chunking{false};
    std::uint64_t root_metadata_budget_bytes{64ULL * 1024ULL * 1024ULL};
    std::uint32_t entries_per_page{1024U};
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t root_buffer_bytes{64U * 1024U};
    bool fsync_on_commit{true};
    bool advise_sequential_io{true};
    bool discard_input_cache{false};
    bool publish_root_to_store{true};
    bool verify_existing_objects{true};
    ContentStoreLimits limits{};
};

struct PagedContentStoreBuildStats {
    PagedContentManifestMetadata metadata{};
    std::uint64_t input_read_calls{};
    std::uint64_t root_write_calls{};
    std::uint64_t chunks_created{};
    std::uint64_t chunks_reused{};
    std::uint64_t chunk_bytes_created{};
    std::uint64_t chunk_bytes_reused{};
    std::uint64_t pages_created{};
    std::uint64_t pages_reused{};
    std::uint64_t page_bytes_created{};
    std::uint64_t page_bytes_reused{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

struct PagedContentManifestWalkOptions {
    bool verify_page_digests{true};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

using PagedContentPageCallback = void (*)(void* context,
                                           const PagedContentPageRef& page);

struct PagedContentManifestWalkStats {
    PagedContentManifestMetadata metadata{};
    std::uint64_t pages_visited{};
    std::uint64_t chunks_visited{};
    std::uint64_t artifact_bytes_visited{};
    std::uint64_t distributed_metadata_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

struct PagedContentPageWindowOptions {
    bool verify_root_manifest{false};
    std::size_t root_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct PagedContentPageWindowStats {
    PagedContentManifestMetadata metadata{};
    std::uint64_t first_page{};
    std::uint32_t pages_loaded{};
    std::uint64_t next_page{};
    std::uint64_t distributed_metadata_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};

    [[nodiscard]] bool complete() const noexcept {
        return next_page >= metadata.page_count;
    }
};

// Reads a bounded root-record window without loading any page object. This is
// the bootstrap seam used to fetch missing paged-manifest objects before chunk
// scheduling can begin.
[[nodiscard]] PagedContentPageWindowStats read_paged_content_page_window(
    const std::filesystem::path& root_manifest_path,
    std::uint64_t first_page,
    std::span<PagedContentPageRef> output,
    const PagedContentPageWindowOptions& options = {});

[[nodiscard]] PagedContentPageWindowStats read_paged_content_page_window(
    const std::filesystem::path& root_manifest_path,
    std::uint64_t first_page,
    std::span<PagedContentPageRef> output,
    ContentStoreWorkspace& workspace,
    const PagedContentPageWindowOptions& options = {});

struct PagedContentScanOptions {
    bool verify_page_digests{true};
    bool verify_chunk_digests{false};
    std::size_t io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

using MissingContentPageCallback = PagedContentPageCallback;

struct PagedContentScanStats {
    PagedContentManifestMetadata metadata{};
    std::uint64_t available_pages{};
    std::uint64_t missing_pages{};
    std::uint64_t corrupt_pages{};
    std::uint64_t available_chunks{};
    std::uint64_t missing_chunks{};
    std::uint64_t corrupt_chunks{};
    std::uint64_t unknown_chunks{};
    std::uint64_t available_bytes{};
    std::uint64_t missing_bytes{};
    std::uint64_t unknown_bytes{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};
};

struct ContentAvailabilityStats {
    ContentManifestFormat format{ContentManifestFormat::flat_v1};
    std::uint64_t manifest_chunks{};
    std::uint64_t first_chunk{};
    std::uint32_t bit_count{};
    std::uint32_t available_count{};
    std::uint32_t unknown_count{};
};

struct PagedContentPageAvailabilityStats {
    std::uint64_t manifest_pages{};
    std::uint64_t first_page{};
    std::uint32_t bit_count{};
    std::uint32_t available_count{};
};

struct ContentChunkWindowOptions {
    // The first arbitrary flat-v1 window otherwise requires a prefix scan to
    // recover its artifact offset. Sequential callers should provide the
    // previous window's next_artifact_offset and avoid that scan entirely.
    bool artifact_offset_hint_valid{false};
    std::uint64_t artifact_offset_hint{};
    bool verify_manifest{false};
    bool verify_page_digests{true};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct ContentChunkWindowStats {
    ContentManifestFormat format{ContentManifestFormat::flat_v1};
    std::uint64_t manifest_chunks{};
    std::uint64_t artifact_size{};
    Digest256 artifact_digest{};
    Digest256 manifest_digest{};
    std::uint64_t first_chunk{};
    std::uint32_t chunks_loaded{};
    std::uint64_t first_artifact_offset{};
    std::uint64_t bytes_described{};
    std::uint64_t next_chunk{};
    std::uint64_t next_artifact_offset{};
    std::uint64_t page_objects_read{};
    std::uint64_t prefix_entries_scanned{};
    std::size_t workspace_reserved_bytes{};
    std::uint32_t workspace_growth_events{};

    [[nodiscard]] bool complete() const noexcept {
        return next_chunk >= manifest_chunks;
    }
};

// Reads a caller-bounded contiguous chunk window. Paged manifests seek only to
// intersecting page records and page objects. Flat manifests support the same
// API; sequential users can pass an artifact-offset hint to keep every window
// O(window) instead of rescanning prefix lengths.
[[nodiscard]] ContentChunkWindowStats read_content_chunk_window(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::span<ContentChunkRef> output,
    const ContentChunkWindowOptions& options = {});

[[nodiscard]] ContentChunkWindowStats read_content_chunk_window(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::span<ContentChunkRef> output,
    ContentStoreWorkspace& workspace,
    const ContentChunkWindowOptions& options = {});

[[nodiscard]] PagedContentScaleEstimate estimate_paged_content_scale(
    std::uint64_t artifact_size,
    const PagedContentStoreOptions& options = {});

[[nodiscard]] PagedContentStoreBuildStats build_paged_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& root_manifest_path,
    const PagedContentStoreOptions& options = {});

[[nodiscard]] PagedContentStoreBuildStats build_paged_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& root_manifest_path,
    ContentStoreWorkspace& workspace,
    const PagedContentStoreOptions& options = {});

[[nodiscard]] PagedContentManifestMetadata inspect_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const ContentStoreLimits& limits = {});

[[nodiscard]] PagedContentManifestMetadata inspect_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    ContentStoreWorkspace& workspace,
    const ContentStoreLimits& limits = {});

// Streams every page reference and chunk entry in artifact order. Page objects
// are loaded one at a time from the content store; memory is independent of
// total page and chunk counts.
[[nodiscard]] PagedContentManifestWalkStats walk_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    PagedContentPageCallback page_callback = nullptr,
    void* page_context = nullptr,
    ContentChunkCallback chunk_callback = nullptr,
    void* chunk_context = nullptr,
    const PagedContentManifestWalkOptions& options = {});

[[nodiscard]] PagedContentManifestWalkStats walk_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    PagedContentPageCallback page_callback = nullptr,
    void* page_context = nullptr,
    ContentChunkCallback chunk_callback = nullptr,
    void* chunk_context = nullptr,
    const PagedContentManifestWalkOptions& options = {});

[[nodiscard]] PagedContentScanStats scan_missing_paged_content_chunks(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    MissingContentPageCallback page_callback = nullptr,
    void* page_context = nullptr,
    MissingContentChunkCallback chunk_callback = nullptr,
    void* chunk_context = nullptr,
    const PagedContentScanOptions& options = {});

[[nodiscard]] PagedContentScanStats scan_missing_paged_content_chunks(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    MissingContentPageCallback page_callback = nullptr,
    void* page_context = nullptr,
    MissingContentChunkCallback chunk_callback = nullptr,
    void* chunk_context = nullptr,
    const PagedContentScanOptions& options = {});

[[nodiscard]] ContentReconstructStats reconstruct_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    const ContentReconstructOptions& options = {});

[[nodiscard]] ContentReconstructStats reconstruct_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    ContentStoreWorkspace& workspace,
    const ContentReconstructOptions& options = {});

// Fills one little-endian availability bitmap for either manifest format.
// The caller supplies a zeroable bounded buffer; no per-chunk container is
// allocated. Paged roots load only the page objects intersecting the request.
[[nodiscard]] ContentAvailabilityStats fill_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::uint32_t requested_chunks,
    std::span<std::byte> output_bits,
    bool verify_objects = false,
    ContentStoreWorkspace* workspace = nullptr,
    const ContentStoreLimits& limits = {});

// Fills an exact little-endian bitmap for immutable page objects named by a
// paged root manifest. Work is processed in a fixed internal batch; memory does
// not grow with total page count or the requested window.
[[nodiscard]] PagedContentPageAvailabilityStats
fill_paged_content_page_availability(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_page,
    std::uint32_t requested_pages,
    std::span<std::byte> output_bits,
    bool verify_objects = false,
    ContentStoreWorkspace* workspace = nullptr,
    const ContentStoreLimits& limits = {});

} // namespace toxsync
