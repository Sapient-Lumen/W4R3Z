#pragma once

#include "toxsync/content_store.hpp"
#include "toxsync/multisource.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <span>

namespace toxsync {

enum class ContentFabricPhase : std::uint8_t {
    unprepared,
    manifest_pages,
    artifact_chunks,
    complete,
};

enum class ContentFabricObjectKind : std::uint8_t {
    manifest_page,
    artifact_chunk,
};

struct ContentFabricConfig {
    std::size_t chunk_window_objects{4096U};
    std::size_t page_window_objects{256U};
    MultiSourceSchedulerLimits scheduler{};
    bool verify_manifest{true};
    bool verify_page_digests{true};
    bool verify_local_objects{false};
    bool fsync_on_commit{true};
    bool prefer_hard_link_ingest{true};
    std::size_t object_io_buffer_bytes{256U * 1024U};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    ContentStoreLimits limits{};
};

struct ContentFabricWindow {
    ContentFabricObjectKind kind{ContentFabricObjectKind::artifact_chunk};
    std::uint64_t first_object{};
    std::uint32_t object_count{};
    std::uint64_t bytes_described{};
};

struct ContentFabricAssignment {
    std::uint64_t request_id{};
    SourcePeerId peer_id{};
    ContentFabricObjectKind kind{ContentFabricObjectKind::artifact_chunk};
    Digest256 object{};
    std::uint64_t object_size{};
    std::uint64_t logical_index{};
    // For artifact chunks this is the final artifact offset. Manifest pages are
    // independent content objects and always report zero here.
    std::uint64_t artifact_offset{};
    std::uint16_t attempt{};
    std::filesystem::path staging_path;
};

struct ContentFabricCommitStats {
    ContentFabricObjectKind kind{ContentFabricObjectKind::artifact_chunk};
    std::uint64_t logical_index{};
    Digest256 object{};
    ContentObjectInstallStats install{};
};

struct ContentFabricStats {
    ContentFabricPhase phase{ContentFabricPhase::unprepared};
    ContentManifestFormat format{ContentManifestFormat::flat_v1};
    std::uint64_t artifact_size{};
    std::uint64_t manifest_chunks{};
    std::uint64_t manifest_pages{};
    Digest256 artifact_digest{};
    Digest256 manifest_digest{};
    ContentFabricWindow window{};
    MultiSourceSchedulerStats scheduler{};
    std::uint64_t windows_completed{};
    std::uint64_t page_objects_reused{};
    std::uint64_t page_objects_fetched{};
    std::uint64_t page_bytes_reused{};
    std::uint64_t page_bytes_fetched{};
    std::uint64_t chunk_objects_reused{};
    std::uint64_t chunk_objects_fetched{};
    std::uint64_t chunk_bytes_reused{};
    std::uint64_t chunk_bytes_fetched{};
    std::uint64_t requests_issued{};
    std::uint64_t request_failures{};
    std::uint64_t verification_failures{};
    std::uint64_t hard_link_ingests{};
    std::uint64_t copied_ingests{};
    std::uint64_t existing_ingests{};
    std::size_t workspace_reserved_bytes{};
    std::size_t resident_bytes{};
};

// A bounded, transport-neutral receiver coordinator for content-store v2.
//
// The caller first acquires the root/flat manifest named by a signed HEAD, then
// creates this session. Paged roots are bootstrapped page-object windows first;
// artifact chunks follow in bounded windows with exact peer inventories and a
// rarest-first scheduler. Completed private staging files are verified and
// atomically promoted into the content store. Restart recovery needs no large
// journal: immutable objects already present in the store are rediscovered on
// the next prepare() scan.
class ContentFabricSession final {
public:
    ContentFabricSession(std::filesystem::path manifest_path,
                         std::filesystem::path store_root,
                         std::filesystem::path staging_root,
                         ContentFabricConfig config = {});
    ~ContentFabricSession();
    ContentFabricSession(ContentFabricSession&&) noexcept;
    ContentFabricSession& operator=(ContentFabricSession&&) noexcept;
    ContentFabricSession(const ContentFabricSession&) = delete;
    ContentFabricSession& operator=(const ContentFabricSession&) = delete;

    void prepare();

    // Exact availability pages use little-endian bits, matching InventoryPage.
    // For manifest-page windows, a source that advertises the signed root can
    // usually be marked with update_peer_complete_window().
    void update_peer(const SourcePeerUpdate& peer,
                     std::uint64_t first_object,
                     std::uint32_t bit_count,
                     std::span<const std::byte> availability_bits);
    void update_peer_complete_window(const SourcePeerUpdate& peer);
    void remove_peer(SourcePeerId peer_id) noexcept;

    [[nodiscard]] std::optional<ContentFabricAssignment> next(
        std::uint64_t request_id);
    [[nodiscard]] std::optional<ContentFabricAssignment> assignment(
        std::uint64_t request_id) const;
    [[nodiscard]] ContentFabricCommitStats commit(
        std::uint64_t request_id,
        const std::filesystem::path& completed_staging_path = {},
        bool source_preverified = false);
    [[nodiscard]] bool fail(
        std::uint64_t request_id,
        SourceFailureDisposition disposition =
            SourceFailureDisposition::retry_source) noexcept;

    [[nodiscard]] bool ready_to_advance() const noexcept;
    // Returns true after loading another window or entering the complete phase;
    // returns false when the current window is not yet complete.
    [[nodiscard]] bool advance_window();
    [[nodiscard]] bool complete() const noexcept;

    [[nodiscard]] ContentReconstructStats reconstruct(
        const std::filesystem::path& output_path,
        const ContentReconstructOptions& options = {});

    [[nodiscard]] ContentFabricPhase phase() const noexcept;
    [[nodiscard]] ContentManifestFormat format() const noexcept;
    [[nodiscard]] ContentFabricWindow window() const noexcept;
    [[nodiscard]] ContentFabricStats stats() const noexcept;
    [[nodiscard]] std::size_t resident_bytes() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] const char* content_fabric_phase_name(
    ContentFabricPhase phase) noexcept;
[[nodiscard]] const char* content_fabric_object_kind_name(
    ContentFabricObjectKind kind) noexcept;

} // namespace toxsync
