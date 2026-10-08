#include "security_tuple_digest.hpp"
#include "sha256_digest.hpp"
#include "sync_manifest_identity.hpp"

#include <array>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <limits>
#include <locale>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Fn>
void require_throws(Fn&& fn, const std::string& message, int& checks) {
    bool threw = false;
    try {
        fn();
    } catch (const std::exception&) {
        threw = true;
    }
    require(threw, message, checks);
}

std::string decimal_u64(std::uint64_t value) {
    std::array<char, 32> bytes{};
    const auto converted = std::to_chars(
        bytes.data(), bytes.data() + bytes.size(), value);
    if (converted.ec != std::errc{}) {
        throw std::runtime_error("test decimal conversion failed");
    }
    return std::string(
        bytes.data(),
        static_cast<std::size_t>(converted.ptr - bytes.data()));
}

std::string legacy_tuple(
    std::string_view domain,
    const std::vector<std::pair<std::string_view, std::string_view>>& fields) {
    std::string out = "anonsync-length-prefixed-tuple-v1";
    const auto append = [&out](std::string_view value) {
        out += decimal_u64(static_cast<std::uint64_t>(value.size()));
        out.push_back(':');
        out.append(value);
    };
    append(domain);
    for (const auto& field : fields) {
        append(field.first);
        append(field.second);
    }
    return out;
}

std::string legacy_chunks_digest(
    const std::vector<anonsync::SyncChunkRange>& chunks) {
    std::string material;
    for (const auto& chunk : chunks) {
        const std::string offset = decimal_u64(chunk.offset);
        const std::string length = decimal_u64(chunk.length);
        material += legacy_tuple(
            "anonsync-sync-chunk-v1",
            {{"offset", offset}, {"length", length}, {"sha256", chunk.sha256}});
    }
    return anonsync::sha256_hex(material);
}

std::string legacy_lineage_digest(
    const std::vector<anonsync::SyncVersionLineageEntry>& lineage) {
    std::string material;
    for (const auto& row : lineage) {
        const std::string counter = decimal_u64(row.counter);
        material += legacy_tuple(
            "anonsync-sync-lineage-v1",
            {{"device_id", row.device_id}, {"counter", counter}});
    }
    return anonsync::sha256_hex(material);
}

std::string kind_text(anonsync::SyncManifestEntryKind kind) {
    switch (kind) {
        case anonsync::SyncManifestEntryKind::File:
            return "file";
        case anonsync::SyncManifestEntryKind::Tombstone:
            return "tombstone";
    }
    throw std::runtime_error("unknown test manifest kind");
}

std::string legacy_entry_digest(
    const anonsync::SyncManifestEntry& entry,
    bool include_device) {
    const std::string size = decimal_u64(entry.size_bytes);
    const std::string chunks = legacy_chunks_digest(entry.chunks);
    const std::string lineage = legacy_lineage_digest(entry.lineage);
    std::vector<std::pair<std::string_view, std::string_view>> fields;
    fields.emplace_back("folder_id", entry.folder_id);
    if (include_device) fields.emplace_back("device_id", entry.device_id);
    fields.emplace_back("path", entry.path.value);
    const std::string kind = kind_text(entry.kind);
    fields.emplace_back("kind", kind);
    fields.emplace_back("size_bytes", size);
    fields.emplace_back("content_sha256", entry.content_sha256);
    fields.emplace_back("chunks_digest", chunks);
    fields.emplace_back("lineage_digest", lineage);
    fields.emplace_back("conflict_set_id", entry.conflict_set_id);
    return anonsync::sha256_hex(legacy_tuple(
        include_device ? "anonsync-sync-manifest-entry-v1"
                       : "anonsync-sync-manifest-entry-version-v1",
        fields));
}

std::string legacy_manifest_digest(
    const anonsync::SyncFolderManifest& manifest) {
    std::string entries_material;
    for (std::size_t index = 0; index < manifest.entries.size(); ++index) {
        const std::string index_text = decimal_u64(index);
        const std::string entry_digest =
            legacy_entry_digest(manifest.entries[index], true);
        entries_material += legacy_tuple(
            "anonsync-sync-folder-manifest-entry-digest-v1",
            {{"entry_index", index_text},
             {"path", manifest.entries[index].path.value},
             {"entry_digest", entry_digest}});
    }
    const std::string entries_digest = anonsync::sha256_hex(entries_material);
    const std::string counter = decimal_u64(manifest.manifest_counter);
    const std::string count = decimal_u64(manifest.entries.size());
    return anonsync::sha256_hex(legacy_tuple(
        "anonsync-sync-folder-manifest-v1",
        {{"folder_id", manifest.folder_id},
         {"device_id", manifest.device_id},
         {"manifest_counter", counter},
         {"entry_count", count},
         {"entries_digest", entries_digest}}));
}

struct GroupEveryDigit final : std::numpunct<char> {
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\1"; }
};

class GlobalLocaleRestore final {
public:
    GlobalLocaleRestore() : previous_(std::locale()) {}
    ~GlobalLocaleRestore() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

anonsync::SyncManifestEntry file_entry() {
    anonsync::SyncManifestEntry entry;
    entry.folder_id = "folder-alpha";
    entry.device_id = "device-alpha";
    entry.path.value = "docs/report.bin";
    entry.kind = anonsync::SyncManifestEntryKind::File;
    entry.size_bytes = 10;
    entry.content_sha256 = anonsync::sha256_hex("abcdefghij");
    entry.chunks = {
        {0, 3, anonsync::sha256_hex("abc")},
        {3, 7, anonsync::sha256_hex("defghij")},
    };
    entry.lineage = {
        {"device-alpha", 17},
        {"device-bravo", std::numeric_limits<std::uint64_t>::max()},
    };
    entry.conflict_set_id = "conflict-0123456789abcdef0123456789abcdef";
    return entry;
}

}  // namespace

int main() {
    try {
        using namespace anonsync;
        int checks = 0;

        const std::string binary_value("a\0b:c", 5);
        const std::string tuple_reference = legacy_tuple(
            "domain:test",
            {{"alpha", binary_value}, {"empty", std::string_view{}}});
        const std::string tuple_digest = sha256_length_prefixed_security_tuple(
            "domain:test",
            {{"alpha", binary_value}, {"empty", std::string_view{}}});
        require(tuple_digest == sha256_hex(tuple_reference),
                "streamed tuple digest must preserve exact binary legacy bytes",
                checks);

        const SyncManifestEntry file = file_entry();
        require(digest_validated_sync_manifest_entry(file) ==
                    legacy_entry_digest(file, true),
                "streamed file entry identity must preserve v1 bytes", checks);
        require(digest_validated_sync_manifest_entry_version(file) ==
                    legacy_entry_digest(file, false),
                "streamed file version identity must preserve v1 bytes", checks);

        SyncManifestEntry tombstone = file;
        tombstone.path.value = "docs/deleted.txt";
        tombstone.kind = SyncManifestEntryKind::Tombstone;
        tombstone.size_bytes = 0;
        tombstone.content_sha256.clear();
        tombstone.chunks.clear();
        tombstone.conflict_set_id.clear();
        require(digest_validated_sync_manifest_entry(tombstone) ==
                    legacy_entry_digest(tombstone, true),
                "streamed tombstone identity must preserve empty aggregate bytes",
                checks);
        require(digest_validated_sync_manifest_entry_version(tombstone) ==
                    legacy_entry_digest(tombstone, false),
                "streamed tombstone version identity must preserve v1 bytes",
                checks);

        SyncFolderManifest manifest;
        manifest.folder_id = "folder-alpha";
        manifest.device_id = "device-alpha";
        manifest.manifest_counter = std::numeric_limits<std::uint64_t>::max();
        manifest.entries = {file, tombstone};
        require(digest_validated_sync_folder_manifest(manifest) ==
                    legacy_manifest_digest(manifest),
                "streamed folder identity must preserve nested v1 bytes", checks);

        const std::string entry_digest =
            digest_validated_sync_manifest_entry(file);
        const std::string expected_mutation = "sync:v1:" + sha256_hex(legacy_tuple(
            "anonsync-sync-mutation-key-v1",
            {{"operation", "record_conflict"},
             {"manifest_entry_digest", entry_digest}}));
        require(digest_validated_sync_mutation_key(
                    "record_conflict", entry_digest) == expected_mutation,
                "streamed mutation identity must preserve v1 bytes", checks);

        SyncManifestEntry republished = file;
        republished.device_id = "device-zulu";
        require(digest_validated_sync_manifest_entry(file) !=
                    digest_validated_sync_manifest_entry(republished),
                "publisher-bound entry identity must bind device id", checks);
        require(digest_validated_sync_manifest_entry_version(file) ==
                    digest_validated_sync_manifest_entry_version(republished),
                "publisher-neutral version identity must omit publisher id",
                checks);

        const std::string baseline_entry =
            digest_validated_sync_manifest_entry(file);
        const std::string baseline_version =
            digest_validated_sync_manifest_entry_version(file);
        const std::string baseline_manifest =
            digest_validated_sync_folder_manifest(manifest);
        {
            GlobalLocaleRestore restore;
            std::locale::global(std::locale(
                std::locale::classic(), new GroupEveryDigit));
            require(digest_validated_sync_manifest_entry(file) == baseline_entry,
                    "entry identity must ignore hostile global numeric locale",
                    checks);
            require(digest_validated_sync_manifest_entry_version(file) ==
                        baseline_version,
                    "version identity must ignore hostile global numeric locale",
                    checks);
            require(digest_validated_sync_folder_manifest(manifest) ==
                        baseline_manifest,
                    "folder identity must ignore hostile global numeric locale",
                    checks);
        }

        SyncManifestEntry changed_chunk = file;
        changed_chunk.chunks[1].sha256 = sha256_hex("different");
        require(digest_validated_sync_manifest_entry_version(changed_chunk) !=
                    baseline_version,
                "version identity must bind every chunk digest", checks);
        SyncManifestEntry changed_lineage = file;
        ++changed_lineage.lineage[0].counter;
        require(digest_validated_sync_manifest_entry_version(changed_lineage) !=
                    baseline_version,
                "version identity must bind every lineage counter", checks);
        SyncManifestEntry changed_conflict = file;
        changed_conflict.conflict_set_id = "conflict-fedcba9876543210fedcba9876543210";
        require(digest_validated_sync_manifest_entry_version(changed_conflict) !=
                    baseline_version,
                "version identity must bind conflict-set provenance", checks);

        SyncFolderManifest reordered = manifest;
        std::swap(reordered.entries[0], reordered.entries[1]);
        require(digest_validated_sync_folder_manifest(reordered) !=
                    baseline_manifest,
                "folder identity must bind entry order and index", checks);

        SyncManifestEntry many_chunks = file;
        many_chunks.size_bytes = 0;
        many_chunks.chunks.clear();
        constexpr std::size_t kChunkCount = 20000;
        many_chunks.chunks.reserve(kChunkCount);
        for (std::size_t index = 0; index < kChunkCount; ++index) {
            many_chunks.chunks.push_back({
                static_cast<std::uint64_t>(index),
                1,
                sha256_hex(decimal_u64(index)),
            });
            ++many_chunks.size_bytes;
        }
        const std::string many_digest =
            digest_validated_sync_manifest_entry_version(many_chunks);
        require(is_lowercase_sha256_hex(many_digest),
                "large chunk aggregate must produce canonical bounded output",
                checks);
        require(many_digest ==
                    digest_validated_sync_manifest_entry_version(many_chunks),
                "large chunk aggregate must be deterministic", checks);

        SyncManifestEntry unknown = file;
        unknown.kind = static_cast<SyncManifestEntryKind>(99);
        require_throws(
            [&] { (void)digest_validated_sync_manifest_entry(unknown); },
            "unknown entry kinds must fail closed in identity leaf", checks);

        std::cout << "sync manifest identity tests passed (" << checks
                  << " checks)\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync manifest identity tests failed: " << e.what()
                  << '\n';
        return 1;
    }
}
