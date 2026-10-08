#include "sha256_digest.hpp"
#include "sync_replica_source_manifest_checkpoint.hpp"

#if !defined(_WIN32)

#include <sys/stat.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

struct AllocationProbe final {
    bool armed = false;
    std::size_t count = 0U;
    std::size_t requested_bytes = 0U;
    std::size_t largest_request = 0U;
};

AllocationProbe g_allocations;

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    if (g_allocations.armed) {
        ++g_allocations.count;
        g_allocations.requested_bytes += size;
        g_allocations.largest_request =
            std::max(g_allocations.largest_request, size);
    }
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

struct AllocationObservation final {
    std::size_t count = 0U;
    std::size_t requested_bytes = 0U;
    std::size_t largest_request = 0U;
};

void arm_allocations() noexcept {
    g_allocations = AllocationProbe{true, 0U, 0U, 0U};
}

[[nodiscard]] AllocationObservation disarm_allocations() noexcept {
    g_allocations.armed = false;
    return {
        g_allocations.count,
        g_allocations.requested_bytes,
        g_allocations.largest_request};
}

}  // namespace

void* operator new(std::size_t size) {
    return allocate_or_throw(size);
}

void* operator new[](std::size_t size) {
    return allocate_or_throw(size);
}

void operator delete(void* memory) noexcept { std::free(memory); }
void operator delete[](void* memory) noexcept { std::free(memory); }
void operator delete(void* memory, std::size_t) noexcept { std::free(memory); }
void operator delete[](void* memory, std::size_t) noexcept {
    std::free(memory);
}

namespace {

std::uint64_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_invalid(
    Function&& function,
    std::string_view expected,
    std::string_view message) {
    ++checks;
    try {
        function();
    } catch (const std::invalid_argument& error) {
        if (std::string_view(error.what()).find(expected) ==
            std::string_view::npos) {
            throw std::runtime_error(
                std::string(message) + ": unexpected diagnostic: " +
                error.what());
        }
        return;
    }
    throw std::runtime_error(std::string(message) + ": no error was thrown");
}

anonsync::SyncPosixRegularFileSnapshotMetadata metadata(
    std::uint64_t inode,
    std::uint64_t size) {
    return {
        17U,
        inode,
        size,
        1U,
        1000U,
        1000U,
        static_cast<std::uint32_t>(S_IFREG | S_IRUSR | S_IWUSR),
        9000,
        123456789U,
        9001,
        987654321U};
}

anonsync::ResumableSha256Checkpoint hash_checkpoint(
    std::string_view bytes) {
    anonsync::ResumableSha256 hash;
    hash.update(bytes);
    return hash.checkpoint();
}

anonsync::SyncReplicaContentDefinedChunkerCheckpoint rolling_checkpoint(
    const anonsync::SyncReplicaContentDefinedChunkingParameters& parameters,
    std::uint64_t completed_chunks,
    std::string_view pending_bytes) {
    anonsync::SyncReplicaContentDefinedChunker chunker(
        parameters, {0U, 0U, completed_chunks, false},
        "checkpoint fixture rolling state");
    for (const unsigned char byte : pending_bytes) {
        if (chunker.consume_byte(byte)) {
            throw std::runtime_error(
                "fixture pending bytes unexpectedly completed a chunk");
        }
    }
    return chunker.checkpoint();
}

anonsync::SyncReplicaSourceManifestCheckpoint active_fixture() {
    const std::string bytes = "abcde";
    anonsync::SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.store_identity_sha256 = anonsync::sha256_hex("store identity");
    checkpoint.store_identity_metadata = metadata(211U, 128U);
    checkpoint.generation = 7U;
    checkpoint.operation_id = anonsync::sha256_hex("operation");
    checkpoint.canonical_path = "media/example.bin";
    checkpoint.content_sha256 = anonsync::sha256_hex(std::string(64U, 'x'));
    checkpoint.total_size_bytes = 64U;
    checkpoint.payload_metadata = metadata(212U, 64U);
    checkpoint.parameters = {8U, 16U, 32U, 8192U};
    checkpoint.disposition =
        anonsync::SyncReplicaSourceManifestCheckpointDisposition::
            ActiveProjection;
    checkpoint.next_offset_bytes = bytes.size();
    checkpoint.completed_chunk_bytes = 0U;
    checkpoint.whole_hash = hash_checkpoint(bytes);
    checkpoint.current_chunk_hash = hash_checkpoint(bytes);
    checkpoint.chunker = rolling_checkpoint(
        checkpoint.parameters, 0U, bytes);
    return checkpoint;
}

anonsync::SyncReplicaSourceManifestCheckpoint complete_fixture() {
    const std::string first = "0123456789abcdef";
    const std::string second = "ABCDEFGHIJKLMNOPQRSTUVWX";
    const std::string bytes = first + second;
    anonsync::SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.store_identity_sha256 = anonsync::sha256_hex("store identity");
    checkpoint.store_identity_metadata = metadata(211U, 128U);
    checkpoint.generation = 8U;
    checkpoint.operation_id = anonsync::sha256_hex("operation complete");
    checkpoint.canonical_path = "media/complete.bin";
    checkpoint.content_sha256 = anonsync::sha256_hex(bytes);
    checkpoint.total_size_bytes = bytes.size();
    checkpoint.payload_metadata = metadata(213U, bytes.size());
    checkpoint.parameters = {8U, 16U, 32U, 8192U};
    checkpoint.disposition =
        anonsync::SyncReplicaSourceManifestCheckpointDisposition::
            CompleteManifest;
    checkpoint.next_offset_bytes = bytes.size();
    checkpoint.completed_chunk_bytes = bytes.size();
    checkpoint.whole_hash = hash_checkpoint(bytes);
    checkpoint.current_chunk_hash =
        anonsync::ResumableSha256{}.checkpoint();
    checkpoint.chunker = {0U, 0U, 2U, true};
    checkpoint.chunks = {
        {static_cast<std::uint64_t>(first.size()), anonsync::sha256_hex(first)},
        {static_cast<std::uint64_t>(second.size()), anonsync::sha256_hex(second)},
    };
    checkpoint.manifest_digest = anonsync::sha256_hex("protocol manifest");
    return checkpoint;
}

void test_fixed_width_chunk_memory_shape() {
    using Chunk = anonsync::SyncReplicaSourceManifestCheckpointChunk;
    constexpr std::size_t kChunks =
        static_cast<std::size_t>(
            anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks);
    static_assert(sizeof(Chunk) == 40U);

    const std::string digest = anonsync::sha256_hex("fixed chunk digest");
    std::vector<Chunk> chunks;
    chunks.reserve(kChunks);

    arm_allocations();
    for (std::size_t index = 0U; index < kChunks; ++index) {
        chunks.emplace_back(1U, digest);
    }
    const AllocationObservation construction = disarm_allocations();
    require(
        construction.count == 0U,
        "fixed-width checkpoint chunk construction allocated per digest");
    require(
        chunks.size() == kChunks && chunks.front().sha256_hex() == digest &&
            chunks.back().sha256_hex() == digest,
        "fixed-width checkpoint chunk construction changed digest bytes");

    arm_allocations();
    const std::vector<Chunk> copied = chunks;
    const AllocationObservation copy = disarm_allocations();
    const std::size_t expected_vector_bytes = kChunks * sizeof(Chunk);
    require(
        copy.count == 1U &&
            copy.requested_bytes == expected_vector_bytes &&
            copy.largest_request == expected_vector_bytes,
        "maximum checkpoint chunk copy was not one contiguous allocation");
    require(
        copied == chunks,
        "maximum checkpoint chunk copy changed fixed digest records");

    require_invalid(
        [&] {
            (void)Chunk{1U, std::string(64U, 'g')};
        },
        "fixed SHA-256 digest",
        "nonhex checkpoint chunk digest was accepted");
}

void test_round_trip() {
    const auto active = active_fixture();
    const std::string active_bytes =
        anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
            active, 1024U, 8192U, "active fixture");
    require(
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            active_bytes, 1024U, 8192U, "active fixture") == active,
        "active checkpoint round trip changed fields");
    require(
        active_bytes.size() == 845U &&
            anonsync::sha256_hex(active_bytes) ==
                "7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f",
        "active checkpoint changed the sealed rev1010 wire image");

    const auto complete = complete_fixture();
    const std::string complete_bytes =
        anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
            complete, 1024U, 8192U, "complete fixture");
    require(
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            complete_bytes, 1024U, 8192U, "complete fixture") == complete,
        "complete checkpoint round trip changed fields");
    require(
        complete_bytes.size() == 990U &&
            anonsync::sha256_hex(complete_bytes) ==
                "cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2",
        "complete checkpoint changed the sealed rev1010 wire image");
    require(
        complete_bytes.size() <=
            anonsync::sync_replica_source_manifest_checkpoint_maximum_bytes(),
        "complete checkpoint crossed its fixed byte frontier");
    require(
        anonsync::kSyncReplicaSourceManifestCheckpointBasename ==
            ".anonsync-payload-source-manifest-checkpoint-v1",
        "source manifest checkpoint basename drifted");
}

void test_bounded_maximum_shape() {
    constexpr std::uint64_t kChunks = 8192U;
    const std::string bytes(static_cast<std::size_t>(kChunks), 'z');
    anonsync::SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.store_identity_sha256 = anonsync::sha256_hex("large identity");
    checkpoint.store_identity_metadata = metadata(301U, 128U);
    checkpoint.generation = 1U;
    checkpoint.operation_id = anonsync::sha256_hex("large operation");
    checkpoint.canonical_path = "large.bin";
    checkpoint.content_sha256 = anonsync::sha256_hex(bytes);
    checkpoint.total_size_bytes = kChunks;
    checkpoint.payload_metadata = metadata(302U, kChunks);
    checkpoint.parameters = {1U, 1U, 1U, kChunks};
    checkpoint.disposition =
        anonsync::SyncReplicaSourceManifestCheckpointDisposition::
            CompleteManifest;
    checkpoint.next_offset_bytes = kChunks;
    checkpoint.completed_chunk_bytes = kChunks;
    checkpoint.whole_hash = hash_checkpoint(bytes);
    checkpoint.current_chunk_hash =
        anonsync::ResumableSha256{}.checkpoint();
    checkpoint.chunker = {0U, 0U, kChunks, true};
    checkpoint.chunks.reserve(static_cast<std::size_t>(kChunks));
    const std::string chunk_digest = anonsync::sha256_hex("z");
    for (std::uint64_t index = 0U; index < kChunks; ++index) {
        checkpoint.chunks.push_back({1U, chunk_digest});
    }
    checkpoint.manifest_digest = anonsync::sha256_hex("large manifest");

    const std::string encoded =
        anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
            checkpoint, kChunks, kChunks, "maximum fixture");
    require(
        encoded.size() == 328581U &&
            anonsync::sha256_hex(encoded) ==
                "c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106",
        "8,192-chunk checkpoint changed the sealed rev1010 wire image");
    require(
        encoded.size() < 384U * 1024U,
        "8,192-chunk checkpoint exceeded the 384 KiB memory frontier");
    require(
        encoded.size() <=
            anonsync::sync_replica_source_manifest_checkpoint_maximum_bytes(
                kChunks),
        "8,192-chunk checkpoint exceeded the computed fixed frontier");
    arm_allocations();
    const auto parsed =
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            encoded, kChunks, kChunks, "maximum fixture");
    const AllocationObservation parsing = disarm_allocations();
    require(
        parsed == checkpoint,
        "8,192-chunk checkpoint did not round trip");
    require(
        parsing.count < 128U,
        "maximum checkpoint parse allocated once per chunk digest");
    require(
        parsing.largest_request >= kChunks *
            sizeof(anonsync::SyncReplicaSourceManifestCheckpointChunk),
        "maximum checkpoint parse did not retain one bounded chunk vector");
    require(
        anonsync::sync_replica_source_manifest_checkpoint_maximum_bytes(
            kChunks + 1U) == 0U,
        "unsupported chunk frontier did not fail closed");
}

void test_four_tebibyte_early_frontier_is_payload_extent_independent() {
    constexpr std::uint64_t kMebibyte = 1024ULL * 1024ULL;
    constexpr std::uint64_t kGibibyte = 1024ULL * kMebibyte;
    constexpr std::uint64_t kTebibyte = 1024ULL * kGibibyte;
    constexpr std::uint64_t kPayloadBytes = 4ULL * kTebibyte;
    const std::string pulse(static_cast<std::size_t>(kMebibyte), '\0');

    anonsync::SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.store_identity_sha256 = anonsync::sha256_hex("4 TiB identity");
    checkpoint.store_identity_metadata = metadata(401U, 128U);
    checkpoint.generation = 19U;
    checkpoint.operation_id = anonsync::sha256_hex("4 TiB operation");
    checkpoint.canonical_path = "media/four-tebibytes.img";
    checkpoint.content_sha256 = anonsync::sha256_hex("synthetic 4 TiB content");
    checkpoint.total_size_bytes = kPayloadBytes;
    checkpoint.payload_metadata = metadata(402U, kPayloadBytes);
    checkpoint.parameters = {
        512ULL * kMebibyte,
        1ULL * kGibibyte,
        2ULL * kGibibyte,
        8192U,
    };
    checkpoint.disposition =
        anonsync::SyncReplicaSourceManifestCheckpointDisposition::
            ActiveProjection;
    checkpoint.next_offset_bytes = kMebibyte;
    checkpoint.completed_chunk_bytes = 0U;
    checkpoint.whole_hash = hash_checkpoint(pulse);
    checkpoint.current_chunk_hash = hash_checkpoint(pulse);
    checkpoint.chunker = rolling_checkpoint(
        checkpoint.parameters, 0U, pulse);

    const std::string encoded =
        anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
            checkpoint, kPayloadBytes, 8192U, "4 TiB active fixture");
    require(
        encoded.size() < 8192U,
        "4 TiB early checkpoint grew with the unprocessed payload extent");
    require(
        anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
            encoded, kPayloadBytes, 8192U, "4 TiB active fixture") ==
            checkpoint,
        "4 TiB active checkpoint did not round trip exactly");
}

void test_rejection() {
    const std::string encoded =
        anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
            active_fixture(), 1024U, 8192U, "corruption fixture");
    std::string corrupted = encoded;
    corrupted[101U] = static_cast<char>(corrupted[101U] ^ 0x01);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                corrupted, 1024U, 8192U, "corruption fixture");
        },
        "checksum",
        "checksum-corrupt checkpoint was accepted");
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_source_manifest_checkpoint_or_throw(
                std::string_view(encoded).substr(0U, encoded.size() - 1U),
                1024U, 8192U, "truncated fixture");
        },
        "checksum",
        "truncated checkpoint was accepted");

    auto invalid = active_fixture();
    invalid.canonical_path = "../escape";
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "path fixture");
        },
        "canonical path",
        "invalid canonical path was accepted");

    invalid = active_fixture();
    invalid.next_offset_bytes = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "zero frontier fixture");
        },
        "whole-hash continuation",
        "zero active frontier was accepted");

    invalid = active_fixture();
    invalid.current_chunk_hash =
        anonsync::ResumableSha256{}.checkpoint();
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "current hash fixture");
        },
        "current-chunk hash",
        "inconsistent current chunk hash was accepted");

    invalid = active_fixture();
    invalid.chunker.pending_chunk_bytes -= 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "rolling extent fixture");
        },
        "current-chunk hash",
        "inconsistent rolling extent was accepted");

    invalid = complete_fixture();
    invalid.chunks.front().size_bytes = 15U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "extent fixture");
        },
        "chunk extents",
        "inconsistent completed chunk extent was accepted");

    invalid = complete_fixture();
    invalid.content_sha256 = anonsync::sha256_hex("wrong complete bytes");
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "whole digest fixture");
        },
        "whole digest",
        "complete checkpoint with the wrong whole digest was accepted");


    invalid = active_fixture();
    invalid.parameters = {1U, 1U, 1U, 1U};
    invalid.total_size_bytes = 2U;
    invalid.payload_metadata = metadata(212U, 2U);
    invalid.next_offset_bytes = 1U;
    invalid.completed_chunk_bytes = 1U;
    invalid.whole_hash = hash_checkpoint("a");
    invalid.current_chunk_hash = anonsync::ResumableSha256{}.checkpoint();
    invalid.chunker = {0U, 0U, 1U, false};
    invalid.chunks = {{1U, anonsync::sha256_hex("a")}};
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 1U, "exhausted active frontier fixture");
        },
        "exhausted its chunk-count frontier",
        "active checkpoint exhausted its chunk frontier before EOF");

    invalid = complete_fixture();
    invalid.parameters.maximum_chunk_count = 4096U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_source_manifest_checkpoint_or_throw(
                invalid, 1024U, 8192U, "frontier fixture");
        },
        "chunk-count parameter",
        "checkpoint with a divergent chunk frontier was accepted");
}

}  // namespace

int main() {
    try {
        test_fixed_width_chunk_memory_shape();
        test_round_trip();
        test_bounded_maximum_shape();
        test_four_tebibyte_early_frontier_is_payload_extent_independent();
        test_rejection();
        std::cout << "sync replica source manifest checkpoint tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica source manifest checkpoint test failure: "
                  << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
