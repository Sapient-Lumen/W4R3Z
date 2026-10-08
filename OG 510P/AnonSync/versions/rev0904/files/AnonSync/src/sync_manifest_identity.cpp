#include "sync_manifest_identity.hpp"

#include "security_tuple_digest.hpp"
#include "sha256_digest.hpp"

#include <array>
#include <charconv>
#include <cstdint>
#include <stdexcept>
#include <string_view>
#include <system_error>

namespace anonsync {
namespace {

class DecimalU64 final {
public:
    explicit DecimalU64(std::uint64_t value) {
        const auto converted = std::to_chars(
            bytes_.data(), bytes_.data() + bytes_.size(), value);
        if (converted.ec != std::errc{}) {
            throw std::runtime_error(
                "sync manifest identity integer formatting failed");
        }
        size_ = static_cast<std::size_t>(converted.ptr - bytes_.data());
    }

    [[nodiscard]] std::string_view view() const noexcept {
        return std::string_view(bytes_.data(), size_);
    }

private:
    std::array<char, 32> bytes_{};
    std::size_t size_ = 0;
};

[[nodiscard]] std::string_view manifest_kind_text_or_throw(
    SyncManifestEntryKind kind) {
    switch (kind) {
        case SyncManifestEntryKind::File:
            return "file";
        case SyncManifestEntryKind::Tombstone:
            return "tombstone";
    }
    throw std::invalid_argument(
        "sync manifest identity requires a known entry kind");
}

[[nodiscard]] std::string digest_chunks_impl(
    const std::vector<SyncChunkRange>& chunks) {
    Sha256DigestBuilder digest;
    for (const SyncChunkRange& chunk : chunks) {
        const DecimalU64 offset(chunk.offset);
        const DecimalU64 length(chunk.length);
        update_sha256_with_length_prefixed_security_tuple(
            digest,
            "anonsync-sync-chunk-v1",
            {
                {"offset", offset.view()},
                {"length", length.view()},
                {"sha256", chunk.sha256},
            });
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string digest_lineage(
    const std::vector<SyncVersionLineageEntry>& lineage) {
    Sha256DigestBuilder digest;
    for (const SyncVersionLineageEntry& entry : lineage) {
        const DecimalU64 counter(entry.counter);
        update_sha256_with_length_prefixed_security_tuple(
            digest,
            "anonsync-sync-lineage-v1",
            {
                {"device_id", entry.device_id},
                {"counter", counter.view()},
            });
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string digest_manifest_entries(
    const std::vector<SyncManifestEntry>& entries) {
    Sha256DigestBuilder digest;
    std::uint64_t index = 0;
    for (const SyncManifestEntry& entry : entries) {
        const DecimalU64 entry_index(index);
        const std::string entry_digest =
            digest_validated_sync_manifest_entry(entry);
        update_sha256_with_length_prefixed_security_tuple(
            digest,
            "anonsync-sync-folder-manifest-entry-digest-v1",
            {
                {"entry_index", entry_index.view()},
                {"path", entry.path.value},
                {"entry_digest", entry_digest},
            });
        ++index;
    }
    return digest.finish_hex();
}

}  // namespace

std::string digest_sync_chunk_vector(
    const std::vector<SyncChunkRange>& chunks) {
    return digest_chunks_impl(chunks);
}

std::string digest_validated_sync_manifest_entry(
    const SyncManifestEntry& entry) {
    const DecimalU64 size_bytes(entry.size_bytes);
    const std::string chunks_digest = digest_chunks_impl(entry.chunks);
    const std::string lineage_digest = digest_lineage(entry.lineage);
    return sha256_length_prefixed_security_tuple(
        "anonsync-sync-manifest-entry-v1",
        {
            {"folder_id", entry.folder_id},
            {"device_id", entry.device_id},
            {"path", entry.path.value},
            {"kind", manifest_kind_text_or_throw(entry.kind)},
            {"size_bytes", size_bytes.view()},
            {"content_sha256", entry.content_sha256},
            {"chunks_digest", chunks_digest},
            {"lineage_digest", lineage_digest},
            {"conflict_set_id", entry.conflict_set_id},
        });
}

std::string digest_validated_sync_manifest_entry_version(
    const SyncManifestEntry& entry) {
    const DecimalU64 size_bytes(entry.size_bytes);
    const std::string chunks_digest = digest_chunks_impl(entry.chunks);
    const std::string lineage_digest = digest_lineage(entry.lineage);
    return sha256_length_prefixed_security_tuple(
        "anonsync-sync-manifest-entry-version-v1",
        {
            {"folder_id", entry.folder_id},
            {"path", entry.path.value},
            {"kind", manifest_kind_text_or_throw(entry.kind)},
            {"size_bytes", size_bytes.view()},
            {"content_sha256", entry.content_sha256},
            {"chunks_digest", chunks_digest},
            {"lineage_digest", lineage_digest},
            {"conflict_set_id", entry.conflict_set_id},
        });
}

std::string digest_validated_sync_folder_manifest(
    const SyncFolderManifest& manifest) {
    const DecimalU64 manifest_counter(manifest.manifest_counter);
    const DecimalU64 entry_count(
        static_cast<std::uint64_t>(manifest.entries.size()));
    const std::string entries_digest = digest_manifest_entries(manifest.entries);
    return sha256_length_prefixed_security_tuple(
        "anonsync-sync-folder-manifest-v1",
        {
            {"folder_id", manifest.folder_id},
            {"device_id", manifest.device_id},
            {"manifest_counter", manifest_counter.view()},
            {"entry_count", entry_count.view()},
            {"entries_digest", entries_digest},
        });
}

std::string digest_validated_sync_mutation_key(
    std::string_view operation,
    std::string_view manifest_entry_digest) {
    return "sync:v1:" + sha256_length_prefixed_security_tuple(
        "anonsync-sync-mutation-key-v1",
        {
            {"operation", operation},
            {"manifest_entry_digest", manifest_entry_digest},
        });
}

}  // namespace anonsync
