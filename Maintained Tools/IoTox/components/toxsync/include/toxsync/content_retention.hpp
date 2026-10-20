#pragma once

#include "toxsync/content_availability.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <span>

namespace toxsync {

inline constexpr std::uint32_t kContentPinCurrent = 1U << 0U;
inline constexpr std::uint32_t kContentPinBaseline = 1U << 1U;
inline constexpr std::uint32_t kContentPinRecent = 1U << 2U;
inline constexpr std::uint32_t kContentPinOperator = 1U << 3U;
inline constexpr std::uint32_t kKnownContentPinFlags =
    kContentPinCurrent | kContentPinBaseline | kContentPinRecent |
    kContentPinOperator;

struct ContentPin {
    Digest256 namespace_id{};
    std::uint64_t generation{};
    Digest256 manifest{};
    // Zero means indefinite retention. Nonzero values are Unix seconds.
    std::uint64_t retain_until_unix_seconds{};
    std::uint32_t flags{kContentPinRecent};
    friend constexpr bool operator==(const ContentPin&, const ContentPin&) = default;
};

enum class ContentPinUpdate : std::uint8_t {
    inserted,
    updated,
    unchanged,
    fork_rejected,
    capacity_exhausted,
};

struct ContentPinLedgerOptions {
    std::size_t max_pins{4096U};
    std::uint64_t max_journal_records{1U << 20U};
    bool fsync_on_commit{true};
    bool repair_truncated_tail{true};
};

struct ContentPinLedgerStats {
    std::size_t active_pins{};
    std::uint64_t records_replayed{};
    std::uint64_t records_appended{};
    std::uint64_t ignored_torn_tail_bytes{};
    std::uint64_t journal_bytes{};
    std::uint64_t next_sequence{};
    std::uint64_t compactions{};
    std::size_t resident_bytes{};
};

// Append-only, checksum-protected retention ledger. A truncated final record is
// treated as a recoverable torn write; corruption of a complete record is a
// hard error. The active pin table is pre-reserved to max_pins.
class ContentPinLedger final {
public:
    explicit ContentPinLedger(
        std::filesystem::path journal_path,
        const ContentPinLedgerOptions& options = {});
    ~ContentPinLedger();
    ContentPinLedger(ContentPinLedger&&) noexcept;
    ContentPinLedger& operator=(ContentPinLedger&&) noexcept;
    ContentPinLedger(const ContentPinLedger&) = delete;
    ContentPinLedger& operator=(const ContentPinLedger&) = delete;

    [[nodiscard]] ContentPinUpdate upsert(const ContentPin& pin);
    [[nodiscard]] bool erase(const Digest256& namespace_id,
                             std::uint64_t generation);
    [[nodiscard]] std::optional<ContentPin> find(
        const Digest256& namespace_id,
        std::uint64_t generation) const noexcept;
    [[nodiscard]] std::span<const ContentPin> pins() const noexcept;
    [[nodiscard]] std::size_t active_count(
        std::uint64_t now_unix_seconds) const noexcept;
    void compact();

    [[nodiscard]] const std::filesystem::path& journal_path() const noexcept;
    [[nodiscard]] ContentPinLedgerStats stats() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

struct ContentGcOptions {
    // Collection begins only when total valid blob bytes exceed this limit.
    std::uint64_t maximum_store_bytes{4ULL * 1024ULL * 1024ULL * 1024ULL};
    // Zero selects 90% of maximum_store_bytes.
    std::uint64_t target_store_bytes{};
    std::uint64_t minimum_unpinned_age_seconds{3600U};
    // Zero uses the current system clock for pin-expiry evaluation.
    std::uint64_t now_unix_seconds{};
    std::size_t reachability_filter_bytes{1024U * 1024U};
    std::uint8_t reachability_hash_functions{7U};
    std::uint64_t reachability_salt{0x747873796e632d67ULL};
    std::size_t manifest_buffer_bytes{64U * 1024U};
    std::uint64_t max_store_files{10'000'000U};
    bool dry_run{false};
    bool remove_empty_prefix_directories{true};
    ContentStoreLimits limits{};
};

struct ContentGcStats {
    std::uint64_t active_pins{};
    std::uint64_t pinned_manifests{};
    std::uint64_t reachable_page_references{};
    std::uint64_t reachable_chunk_references{};
    std::uint64_t scanned_files{};
    std::uint64_t scanned_bytes{};
    std::uint64_t protected_files{};
    std::uint64_t protected_bytes{};
    std::uint64_t young_unpinned_files{};
    std::uint64_t young_unpinned_bytes{};
    std::uint64_t candidate_files{};
    std::uint64_t candidate_bytes{};
    std::uint64_t deleted_files{};
    std::uint64_t deleted_bytes{};
    std::uint64_t deletion_failures{};
    std::uint64_t bytes_after{};
    std::size_t reachability_filter_bytes{};
    double estimated_false_positive_rate{};
    bool budget_satisfied{};
    bool dry_run{};
};

// Conservative bounded-memory collector. It marks pinned manifests and their
// chunks in a Bloom filter, then removes only blobs that are definitely absent.
// False positives retain garbage; they can never delete live content.
[[nodiscard]] ContentGcStats collect_content_store(
    const std::filesystem::path& store_root,
    const ContentPinLedger& ledger,
    const ContentGcOptions& options = {});

[[nodiscard]] ContentGcStats collect_content_store(
    const std::filesystem::path& store_root,
    std::span<const ContentPin> pins,
    ContentStoreWorkspace& workspace,
    const ContentGcOptions& options = {});

} // namespace toxsync
