#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace bzip4 {

struct ZipIssue {
    std::string code;
    std::string message;
    std::string entry;
    bool fatal{true};
};

struct ZipMethodCount {
    std::uint16_t method{};
    std::size_t entries{};
    std::uint64_t compressed_bytes{};
    std::uint64_t uncompressed_bytes{};
};

struct ZipReport {
    std::filesystem::path path;
    std::uint64_t file_size{};
    std::size_t entries{};
    std::uint64_t compressed_bytes{};
    std::uint64_t uncompressed_bytes{};
    std::uint64_t central_directory_offset{};
    std::uint64_t central_directory_size{};
    std::uint64_t central_name_bytes{};
    std::size_t central_parser_peak_read_bytes{};
    std::size_t duplicate_names{};
    std::size_t unsafe_paths{};
    std::size_t encrypted_entries{};
    std::size_t data_descriptor_entries{};
    std::size_t issue_limit{};
    std::size_t suppressed_issues{};
    std::size_t suppressed_fatal_issues{};
    bool zip64{};
    std::vector<ZipMethodCount> methods;
    std::vector<ZipIssue> issues;

    // Appended in rev0029 so existing positional aggregate initializers retain
    // the ordering of every pre-existing report member.
    std::size_t regular_file_entries{};
    std::size_t directory_entries{};
    std::size_t symlink_entries{};
    std::size_t special_file_entries{};
    std::size_t unclassified_type_entries{};
    std::size_t entry_type_mismatches{};

    // ZIP64 representation telemetry is separate from logical size totals so
    // callers never have to infer on-disk form from member size alone.
    std::uint64_t zip64_eocd_offset{};
    std::uint64_t zip64_eocd_size{};
    std::size_t zip64_entries{};
    std::size_t zip64_data_descriptor_entries{};

    // Core retained-memory telemetry for the streamed central-directory
    // parser. These values exclude allocator bookkeeping, issue strings, and
    // the per-method map; they make entry-layout and name-arena changes
    // observable without changing admission policy.
    std::uint64_t central_entry_descriptor_bytes{};
    std::uint64_t central_entry_storage_bytes{};
    std::uint64_t central_name_storage_bytes{};
    std::uint64_t central_parser_peak_retained_bytes{};

    // Optional, non-extracting duplicate-payload nomination. A CRC/size tuple
    // is only a nomination; verified groups additionally require identical
    // compressed representations, SHA-256 agreement, and exact byte-by-byte
    // range comparison. Repeated-byte totals are gross evidence before any
    // future reference metadata or stream-layout overhead.
    bool payload_probe_enabled{};
    bool payload_probe_budget_exhausted{};
    std::size_t content_nomination_groups{};
    std::size_t content_nomination_entries{};
    std::uint64_t content_nomination_repeated_uncompressed_bytes{};
    std::size_t payload_candidate_groups{};
    std::size_t payload_candidate_entries{};
    std::uint64_t payload_candidate_compressed_bytes{};
    std::size_t payload_hashed_groups{};
    std::size_t payload_hashed_entries{};
    std::uint64_t payload_probe_read_bytes{};
    std::size_t verified_payload_groups{};
    std::size_t verified_payload_entries{};
    std::size_t verified_duplicate_entries{};
    std::uint64_t verified_repeated_compressed_bytes{};
    std::uint64_t verified_repeated_uncompressed_bytes{};
    std::size_t payload_probe_skipped_groups{};
    std::size_t payload_probe_skipped_entries{};
    std::uint64_t payload_probe_skipped_compressed_bytes{};
    std::size_t payload_digest_collision_groups{};
    std::uint64_t payload_probe_peak_scratch_bytes{};

    [[nodiscard]] bool ok() const noexcept;
};

struct ZipLimits {
    std::size_t max_entries{1'000'000};
    std::uint64_t max_central_directory_bytes{512ULL * 1024ULL * 1024ULL};
    std::size_t max_name_bytes{65'535};
    std::uint64_t max_total_name_bytes{256ULL * 1024ULL * 1024ULL};
    std::size_t max_issues{1024};
    bool reject_encryption{true};
    bool reject_symlinks{true};
    bool reject_special_files{true};
    bool reject_entry_type_mismatches{true};
    std::uint64_t max_zip64_eocd_bytes{1024ULL * 1024ULL};

    // Duplicate-payload nomination is opt-in so ordinary structural preflight
    // retains its metadata-only I/O profile. The read budget includes hashing
    // and exact verification reads. Groups are admitted atomically against a
    // conservative worst-case cost so a report never presents a partially
    // verified group as exact evidence.
    bool probe_exact_payload_duplicates{false};
    std::uint64_t max_payload_probe_read_bytes{512ULL * 1024ULL * 1024ULL};
    std::size_t max_payload_probe_group_entries{100'000};
    std::size_t payload_probe_chunk_bytes{64U * 1024U};
    std::uint64_t min_payload_probe_bytes{1};
};

/** Bounded, non-extracting ZIP structure validation. */
[[nodiscard]] ZipReport preflight_zip(
    const std::filesystem::path& path,
    const ZipLimits& limits = {});

[[nodiscard]] std::string zip_report_json(const ZipReport& report, bool pretty = true);

} // namespace bzip4
