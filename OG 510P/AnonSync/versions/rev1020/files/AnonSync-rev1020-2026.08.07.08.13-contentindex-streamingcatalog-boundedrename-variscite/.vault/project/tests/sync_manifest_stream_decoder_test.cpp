#include "sync_manifest_stream_decoder.hpp"

#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::SyncManifestEntry;
using anonsync::SyncManifestEntryKind;
using anonsync::SyncManifestEntryStreamDecoder;
using anonsync::SyncManifestEntryStreamHeader;
using anonsync::SyncManifestResourceLimits;
using anonsync::SyncManifestResourceUsage;
using anonsync::SyncValidationResult;

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

void require_rejected(
    const SyncValidationResult& result,
    const std::string& expected_fragment,
    const std::string& message,
    int& checks) {
    require(
        !result.ok && result.reason.find(expected_fragment) != std::string::npos,
        message + ": " + result.reason,
        checks);
}

[[nodiscard]] SyncManifestEntryStreamHeader valid_header() {
    SyncManifestEntryStreamHeader header;
    header.folder_id = "folder-alpha";
    header.device_id = "device-alpha";
    header.path = "docs/file.bin";
    header.kind = SyncManifestEntryKind::File;
    header.size_bytes = 5;
    header.content_sha256 = std::string_view{
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"};
    header.declared_chunk_count = 2;
    header.declared_lineage_count = 2;
    return header;
}

void append_valid_rows(
    SyncManifestEntryStreamDecoder& decoder,
    int& checks) {
    require(
        decoder.append_chunk(
            0, 2,
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
            .ok,
        "first chunk is admitted", checks);
    require(
        decoder.append_chunk(
            2, 3,
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
            .ok,
        "second chunk is admitted", checks);
    require(decoder.append_lineage("device-alpha", 7).ok,
            "first lineage row is admitted", checks);
    require(decoder.append_lineage("device-bravo", 9).ok,
            "second lineage row is admitted", checks);
}

[[nodiscard]] SyncManifestEntry sentinel_entry() {
    SyncManifestEntry entry;
    entry.folder_id = "sentinel";
    entry.path.value = "sentinel";
    return entry;
}

[[nodiscard]] bool is_sentinel(const SyncManifestEntry& entry) {
    return entry.folder_id == "sentinel" && entry.path.value == "sentinel";
}

}  // namespace

int main() {
    int checks = 0;
    try {
        SyncManifestResourceUsage valid_usage;
        {
            SyncManifestEntryStreamDecoder decoder;
            SyncManifestEntry out = sentinel_entry();
            require(!decoder.active() && !decoder.failed(),
                    "new decoder has no active or failed authority", checks);
            require(decoder.begin(valid_header()).ok && decoder.active(),
                    "valid declared shape activates the decoder", checks);
            require(is_sentinel(out),
                    "begin does not publish a partial output", checks);
            append_valid_rows(decoder, checks);
            require(decoder.chunks_accepted() == 2 &&
                        decoder.lineage_entries_accepted() == 2,
                    "accepted-row observations are exact", checks);
            require(decoder.finish(out, &valid_usage).ok,
                    "complete valid event stream publishes", checks);
            require(!decoder.active() && !decoder.failed(),
                    "successful finish consumes active authority", checks);
            require(out.folder_id == "folder-alpha" &&
                        out.device_id == "device-alpha" &&
                        out.path.value == "docs/file.bin" &&
                        out.size_bytes == 5 &&
                        out.chunks.size() == 2 &&
                        out.lineage.size() == 2 &&
                        out.chunks.back().offset == 2 &&
                        out.chunks.back().length == 3 &&
                        out.lineage.back().device_id == "device-bravo",
                    "published value contains the frozen complete stream", checks);
            require(valid_usage.entries == 1 && valid_usage.chunks == 2 &&
                        valid_usage.lineage_entries == 2 &&
                        valid_usage.path_bytes == 13 &&
                        valid_usage.metadata_bytes == 310,
                    "incremental usage has stable exact accounting", checks);
            require_rejected(
                decoder.append_chunk(5, 1, std::string(64, 'd')),
                "after finish",
                "finished decoder rejects additional events", checks);
        }

        {
            std::string folder = "folder-alpha";
            std::string device = "device-alpha";
            std::string path = "docs/file.bin";
            std::string content(64, 'a');
            SyncManifestEntryStreamHeader header = valid_header();
            header.folder_id = folder;
            header.device_id = device;
            header.path = path;
            header.content_sha256 = content;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok,
                    "borrowed header observations are accepted", checks);
            folder.assign("mutated-folder");
            device.assign("mutated-device");
            path.assign("mutated/path");
            content.assign(64, 'f');
            append_valid_rows(decoder, checks);
            SyncManifestEntry out;
            require(decoder.finish(out).ok &&
                        out.folder_id == "folder-alpha" &&
                        out.device_id == "device-alpha" &&
                        out.path.value == "docs/file.bin" &&
                        out.content_sha256 == std::string(64, 'a'),
                    "begin freezes admitted scalar bytes exactly once", checks);
        }

        {
            SyncManifestResourceLimits exact;
            exact.max_entries = valid_usage.entries;
            exact.max_chunks_per_entry = valid_usage.chunks;
            exact.max_lineage_entries_per_entry = valid_usage.lineage_entries;
            exact.max_total_chunks = valid_usage.chunks;
            exact.max_total_lineage_entries = valid_usage.lineage_entries;
            exact.max_total_path_bytes = valid_usage.path_bytes;
            exact.max_total_metadata_bytes = valid_usage.metadata_bytes;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header(), exact).ok,
                    "resource ceilings are inclusive", checks);
            append_valid_rows(decoder, checks);
            SyncManifestEntry out;
            SyncManifestResourceUsage usage;
            require(decoder.finish(out, &usage).ok &&
                        usage.metadata_bytes == valid_usage.metadata_bytes,
                    "exact resource ceiling publishes exact usage", checks);

            --exact.max_total_metadata_bytes;
            SyncManifestEntryStreamDecoder too_small;
            require(too_small.begin(valid_header(), exact).ok,
                    "incremental metadata ceiling admits bounded header", checks);
            require(too_small.append_chunk(
                        0, 2,
                        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb").ok,
                    "incremental metadata ceiling admits first row", checks);
            require(too_small.append_chunk(
                        2, 3,
                        "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc").ok,
                    "incremental metadata ceiling admits second row", checks);
            require(too_small.append_lineage("device-alpha", 7).ok,
                    "incremental metadata ceiling admits penultimate row", checks);
            require_rejected(
                too_small.append_lineage("device-bravo", 9),
                "metadata bytes exceed resource limit",
                "metadata is rejected before the final row is copied", checks);
            require(too_small.failed() && too_small.chunks_accepted() == 0 &&
                        too_small.lineage_entries_accepted() == 0,
                    "failure is sticky and discards retained partial rows", checks);
        }

        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_chunk_count = 3;
            SyncManifestResourceLimits limits;
            limits.max_chunks_per_entry = 2;
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(
                decoder.begin(header, limits),
                "per-entry resource limit",
                "declared chunk count is rejected before allocation", checks);
            require(decoder.failed(),
                    "preallocation count rejection permanently fails owner", checks);
            const std::string first_reason =
                decoder.append_lineage("device-alpha", 1).reason;
            require(first_reason.find("per-entry resource limit") !=
                        std::string::npos,
                    "sticky failure preserves the original cause", checks);
        }

        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.path = "docs/../secret";
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "dot segment",
                             "invalid path is rejected before retention", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.kind = static_cast<SyncManifestEntryKind>(99);
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "unknown kind",
                             "unknown entry kind is rejected", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_lineage_count = 0;
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "requires version lineage",
                             "zero declared lineage is rejected at begin", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.content_sha256 = std::string_view{
                "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"};
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "lowercase sha256",
                             "uppercase content hash is rejected", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.size_bytes = 0;
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "zero-byte file",
                             "zero-byte file cannot declare chunks", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_chunk_count = 0;
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(decoder.begin(header), "nonempty file",
                             "nonempty file must declare chunks", checks);
        }

        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.kind = SyncManifestEntryKind::Tombstone;
            header.size_bytes = 0;
            header.content_sha256 = {};
            header.declared_chunk_count = 0;
            header.declared_lineage_count = 1;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok &&
                        decoder.append_lineage("device-alpha", 11).ok,
                    "valid tombstone stream is admitted", checks);
            SyncManifestEntry out;
            require(decoder.finish(out).ok &&
                        out.kind == SyncManifestEntryKind::Tombstone &&
                        out.chunks.empty(),
                    "valid tombstone publishes without chunks", checks);

            header.declared_chunk_count = 1;
            SyncManifestEntryStreamDecoder bad_tombstone;
            require_rejected(
                bad_tombstone.begin(header), "must not carry chunks",
                "tombstone declared chunks are rejected before allocation",
                checks);
        }

        {
            SyncManifestEntryStreamDecoder decoder;
            require_rejected(
                decoder.append_chunk(0, 1, std::string(64, 'a')),
                "requires a successful begin",
                "row events require active authority", checks);
            require(!decoder.failed(),
                    "invalid state call does not invent a malformed stream",
                    checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "duplicate-begin fixture begins", checks);
            require_rejected(decoder.begin(valid_header()),
                             "already active",
                             "duplicate begin is rejected", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "chunk discontinuity fixture begins", checks);
            require_rejected(
                decoder.append_chunk(1, 2, std::string(64, 'b')),
                "contiguous",
                "nonzero first chunk offset is rejected", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "zero chunk fixture begins", checks);
            require_rejected(
                decoder.append_chunk(0, 0, std::string(64, 'b')),
                "positive",
                "zero-length chunk is rejected", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "bad chunk hash fixture begins", checks);
            require_rejected(decoder.append_chunk(0, 2, "bad"), "sha256",
                             "malformed chunk hash is rejected", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.size_bytes = std::numeric_limits<std::uint64_t>::max();
            header.declared_chunk_count = 1;
            header.declared_lineage_count = 1;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok,
                    "overflow fixture header begins", checks);
            require(
                decoder.append_chunk(
                    0, std::numeric_limits<std::uint64_t>::max(),
                    std::string(64, 'b')).ok,
                "maximum-length first chunk is representable", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.size_bytes = std::numeric_limits<std::uint64_t>::max();
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok,
                    "overflow addition fixture begins", checks);
            require(decoder.append_chunk(0,
                        std::numeric_limits<std::uint64_t>::max() - 1,
                        std::string(64, 'b')).ok,
                    "large first chunk is representable", checks);
            require_rejected(
                decoder.append_chunk(
                    std::numeric_limits<std::uint64_t>::max() - 1, 2,
                    std::string(64, 'c')),
                "overflow", "chunk offset addition cannot wrap", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_chunk_count = 1;
            header.declared_lineage_count = 1;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok &&
                        decoder.append_chunk(0, 5, std::string(64, 'b')).ok &&
                        decoder.append_lineage("device-alpha", 1).ok,
                    "extra-row fixture reaches declared counts", checks);
            require_rejected(
                decoder.append_chunk(5, 1, std::string(64, 'c')),
                "more chunk rows",
                "extra chunk row fails before vector growth", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            SyncManifestEntry out = sentinel_entry();
            require(decoder.begin(valid_header()).ok &&
                        decoder.append_chunk(0, 5, std::string(64, 'b')).ok &&
                        decoder.append_lineage("device-alpha", 1).ok &&
                        decoder.append_lineage("device-bravo", 2).ok,
                    "missing-row fixture accepts available rows", checks);
            require_rejected(decoder.finish(out), "chunk rows",
                             "missing chunk row rejects finish", checks);
            require(is_sentinel(out),
                    "failed finish leaves caller output unchanged", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "lineage validation fixture begins", checks);
            require_rejected(decoder.append_lineage("Bad-Device", 1),
                             "lowercase portable sync id",
                             "invalid lineage identity is rejected", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok,
                    "lineage counter fixture begins", checks);
            require_rejected(decoder.append_lineage("device-alpha", 0),
                             "positive",
                             "zero lineage counter is rejected", checks);
        }
        {
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(valid_header()).ok &&
                        decoder.append_lineage("device-bravo", 1).ok,
                    "lineage ordering fixture accepts first row", checks);
            require_rejected(decoder.append_lineage("device-alpha", 2),
                             "sorted",
                             "descending lineage identity is rejected", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_lineage_count = 1;
            SyncManifestEntryStreamDecoder decoder;
            require(decoder.begin(header).ok &&
                        decoder.append_lineage("device-alpha", 1).ok,
                    "extra lineage fixture reaches declared count", checks);
            require_rejected(decoder.append_lineage("device-bravo", 2),
                             "more lineage rows",
                             "extra lineage row fails before vector growth", checks);
        }
        {
            SyncManifestEntryStreamHeader header = valid_header();
            header.declared_chunk_count = 1;
            header.declared_lineage_count = 1;
            SyncManifestEntryStreamDecoder decoder;
            SyncManifestEntry out = sentinel_entry();
            require(decoder.begin(header).ok &&
                        decoder.append_chunk(0, 4, std::string(64, 'b')).ok &&
                        decoder.append_lineage("device-alpha", 1).ok,
                    "coverage mismatch fixture reaches finish", checks);
            require_rejected(decoder.finish(out), "cover exactly",
                             "chunk coverage must equal file size", checks);
            require(is_sentinel(out),
                    "coverage rejection never publishes partial entry", checks);
        }

        std::cout << "sync manifest stream decoder checks=" << checks << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync manifest stream decoder test failed after "
                  << checks << " checks: " << e.what() << "\n";
        return 1;
    }
}
