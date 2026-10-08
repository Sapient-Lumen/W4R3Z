#include "sha256_digest.hpp"
#include "sync_replica_delivery_service.hpp"
#include "sync_replica_delivery_test_channel.hpp"
#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {

struct LargeAllocationProbe final {
    bool armed = false;
    std::size_t threshold = 0U;
    std::uint64_t generation = 0U;
    std::size_t count = 0U;
    std::uint64_t bytes = 0U;
    std::size_t largest = 0U;
    std::size_t active_count = 0U;
    std::uint64_t active_bytes = 0U;
    std::size_t peak_active_count = 0U;
    std::uint64_t peak_active_bytes = 0U;
};

struct alignas(std::max_align_t) AllocationHeader final {
    std::size_t size = 0U;
    std::uint64_t probe_generation = 0U;
};

LargeAllocationProbe g_probe;
std::uint64_t g_next_probe_generation = 0U;

void add_probe_bytes_or_abort(std::uint64_t& target, std::size_t size) noexcept {
    if (static_cast<std::uint64_t>(size) >
        std::numeric_limits<std::uint64_t>::max() - target) {
        std::abort();
    }
    target += static_cast<std::uint64_t>(size);
}

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    const std::size_t actual_size = size == 0U ? 1U : size;
    if (actual_size >
        std::numeric_limits<std::size_t>::max() - sizeof(AllocationHeader)) {
        throw std::bad_alloc();
    }
    void* const raw = std::malloc(sizeof(AllocationHeader) + actual_size);
    if (raw == nullptr) throw std::bad_alloc();
    auto* const header = static_cast<AllocationHeader*>(raw);
    header->size = actual_size;
    header->probe_generation = 0U;
    if (g_probe.armed && actual_size >= g_probe.threshold) {
        header->probe_generation = g_probe.generation;
        ++g_probe.count;
        add_probe_bytes_or_abort(g_probe.bytes, actual_size);
        g_probe.largest = std::max(g_probe.largest, actual_size);
        ++g_probe.active_count;
        add_probe_bytes_or_abort(g_probe.active_bytes, actual_size);
        g_probe.peak_active_count =
            std::max(g_probe.peak_active_count, g_probe.active_count);
        g_probe.peak_active_bytes =
            std::max(g_probe.peak_active_bytes, g_probe.active_bytes);
    }
    return header + 1;
}

void release_allocation(void* memory) noexcept {
    if (memory == nullptr) return;
    auto* const header = static_cast<AllocationHeader*>(memory) - 1;
    if (header->probe_generation != 0U &&
        header->probe_generation == g_probe.generation) {
        if (g_probe.active_count == 0U ||
            g_probe.active_bytes < static_cast<std::uint64_t>(header->size)) {
            std::abort();
        }
        --g_probe.active_count;
        g_probe.active_bytes -= static_cast<std::uint64_t>(header->size);
    }
    std::free(header);
}

struct AllocationObservation final {
    std::size_t count = 0U;
    std::uint64_t bytes = 0U;
    std::size_t largest = 0U;
    std::size_t active_count = 0U;
    std::uint64_t active_bytes = 0U;
    std::size_t peak_active_count = 0U;
    std::uint64_t peak_active_bytes = 0U;
};

void arm_large_allocations(std::size_t threshold) noexcept {
    ++g_next_probe_generation;
    if (g_next_probe_generation == 0U) std::abort();
    g_probe = LargeAllocationProbe{
        true, threshold, g_next_probe_generation, 0U, 0U, 0U,
        0U, 0U, 0U, 0U};
}

[[nodiscard]] AllocationObservation disarm_large_allocations() noexcept {
    g_probe.armed = false;
    return {
        g_probe.count,
        g_probe.bytes,
        g_probe.largest,
        g_probe.active_count,
        g_probe.active_bytes,
        g_probe.peak_active_count,
        g_probe.peak_active_bytes};
}

}  // namespace

void* operator new(std::size_t size) {
    return allocate_or_throw(size);
}

void* operator new[](std::size_t size) {
    return allocate_or_throw(size);
}

void operator delete(void* memory) noexcept {
    release_allocation(memory);
}

void operator delete[](void* memory) noexcept {
    release_allocation(memory);
}

void operator delete(void* memory, std::size_t) noexcept {
    release_allocation(memory);
}

void operator delete[](void* memory, std::size_t) noexcept {
    release_allocation(memory);
}

namespace {

namespace fs = std::filesystem;

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

[[nodiscard]] std::string sha256_hex_view(std::string_view bytes) {
    anonsync::Sha256DigestBuilder digest;
    digest.update(bytes);
    return digest.finish_hex();
}

void test_active_source_projection_uses_one_fixed_vector_per_share() {
    using Chunk =
        anonsync::SyncReplicaFilePayloadStoreContentDefinedChunk;
    constexpr std::size_t kChunks = static_cast<std::size_t>(
        anonsync::kSyncReplicaSourceManifestCheckpointMaximumChunks);
    constexpr std::size_t kConcurrentShares = 64U;
    constexpr std::size_t kVectorBytes = kChunks * sizeof(Chunk);
    static_assert(sizeof(Chunk) == 40U);
    static_assert(std::is_trivially_copyable_v<Chunk>);
    static_assert(kVectorBytes == 327680U);

    const std::string digest_text =
        anonsync::sha256_hex("active source projection fixed digest");
    arm_large_allocations(1U);
    anonsync::ResumableSha256 fixed_digest;
    fixed_digest.update("active source projection fixed digest");
    const Chunk direct_chunk(
        1U, anonsync::Sha256DigestValue(fixed_digest.finish_binary_array()));
    const AllocationObservation direct = disarm_large_allocations();
    require(
        direct.count == 0U && direct_chunk.sha256 == digest_text,
        "binary digest completion allocated before fixed chunk publication");

    std::vector<Chunk> one_source;
    one_source.reserve(kChunks);
    arm_large_allocations(1U);
    for (std::size_t index = 0U; index < kChunks; ++index) {
        one_source.emplace_back(1U, digest_text);
    }
    const AllocationObservation construction =
        disarm_large_allocations();
    require(
        construction.count == 0U && one_source.size() == kChunks &&
            one_source.capacity() == kChunks,
        "active source projection allocated once per fixed digest");
    require(
        one_source.front().sha256.lowercase_hex() == digest_text &&
            one_source.back().sha256.lowercase_hex() == digest_text,
        "active source projection changed fixed digest bytes");

    std::vector<std::vector<Chunk>> concurrent_sources;
    concurrent_sources.reserve(kConcurrentShares);
    arm_large_allocations(kVectorBytes);
    for (std::size_t index = 0U; index < kConcurrentShares; ++index) {
        concurrent_sources.push_back(one_source);
    }
    const AllocationObservation copies = disarm_large_allocations();
    const std::uint64_t expected_bytes =
        static_cast<std::uint64_t>(kConcurrentShares) * kVectorBytes;
    require(
        copies.count == kConcurrentShares &&
            copies.peak_active_count == kConcurrentShares &&
            copies.active_count == kConcurrentShares,
        "concurrent active source projections did not retain one vector per share");
    require(
        copies.bytes == expected_bytes &&
            copies.active_bytes == expected_bytes &&
            copies.peak_active_bytes == expected_bytes &&
            copies.largest == kVectorBytes,
        "concurrent active source projection memory was not exact linear fixed-record storage");
    require(
        expected_bytes == 20U * 1024U * 1024U,
        "64-share active source projection fixture changed its exact 20 MiB frontier");
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
                ("anonsync-source-frame-memory-" +
                 std::to_string(static_cast<unsigned long long>(::getpid())) +
                 "-" + std::to_string(tick));
        fs::create_directory(path_);
        if (::chmod(path_.c_str(), 0700) != 0) {
            throw std::runtime_error(
                "could not make source-frame-memory root private");
        }
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] fs::path database_path() const {
        return path_ / "source.sqlite3";
    }

    [[nodiscard]] fs::path payload_root() const {
        const fs::path out = path_ / "payloads";
        fs::create_directory(out);
        if (::chmod(out.c_str(), 0700) != 0) {
            throw std::runtime_error(
                "could not make source-frame-memory payload root private");
        }
        return out;
    }

    [[nodiscard]] fs::path effect_database_path() const {
        return path_ / "effects.sqlite3";
    }

    [[nodiscard]] fs::path effect_root() const {
        const fs::path out = path_ / "effect-root";
        fs::create_directory(out);
        if (::chmod(out.c_str(), 0700) != 0) {
            throw std::runtime_error(
                "could not make source-frame-memory effect root private");
        }
        return out;
    }

private:
    fs::path path_;
};

[[nodiscard]] anonsync::SyncSqliteDb open_database(const fs::path& path) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "source-frame-memory database open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, "source-frame-memory busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        "source-frame-memory durability profile");
    return owner;
}

[[nodiscard]] anonsync::SyncReplicaSqliteOwnerLimits owner_limits() {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = 8U;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 4U * 1024U * 1024U;
    value.model.max_retained_context_entries = 512U;
    value.model.max_retained_predecessor_ids = 512U;
    value.max_outbox_intents = 16U;
    value.max_outbox_destination_bytes = 64U * 1024U;
    return value;
}

[[nodiscard]] anonsync::SyncReplicaReconciliationProtocolLimits
source_limits() {
    constexpr std::uint64_t kPageBytes = 64ULL * 1024ULL * 1024ULL;
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model = owner_limits().model;
    value.max_operations_per_page = 1U;
    value.max_canonical_operation_bytes_per_page = 512U * 1024U;
    value.max_payloads_per_page = 1U;
    value.max_single_payload_bytes = kPageBytes;
    value.max_payload_bytes_per_page = kPageBytes;
    value.max_payload_extent_bytes = kPageBytes;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 96ULL * 1024ULL * 1024ULL;
    return value;
}

void test_shipping_source_fills_one_64_mib_frame_without_range_copy() {
    constexpr std::size_t kPayloadBytes = 64U * 1024U * 1024U;
    constexpr std::size_t kLargeAllocationThreshold = 2U * 1024U * 1024U;
    TemporaryDirectory temporary;
    const std::string folder = "folder-source-frame-memory";
    const anonsync::SyncReplicaActor source_actor{
        "device-source-frame-memory-source", 99801U};
    const anonsync::SyncReplicaActor requester_actor{
        "device-source-frame-memory-requester", 99802U};
    anonsync::SyncSqliteDb database = open_database(temporary.database_path());
    anonsync::SyncReplicaSqliteOwner owner(
        database.db, folder, source_actor, owner_limits(),
        "source-frame-memory replica owner");

    anonsync::SyncReplicaFilePayloadStoreLimits store_limits;
    store_limits.max_entries = 8U;
    store_limits.max_payload_bytes = kPayloadBytes;
    store_limits.max_indexed_bytes = 2ULL * kPayloadBytes;
    store_limits.max_transient_entries = 8U;
    store_limits.max_transient_bytes = kPayloadBytes;
    anonsync::SyncReplicaFilePayloadStore payload_store(
        folder, temporary.payload_root(),
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        store_limits, "source-frame-memory payload store");
    const auto configured = source_limits();
    anonsync::SyncReplicaReconciliationService service(
        owner, payload_store, configured,
        "source-frame-memory reconciliation service");

    std::string payload(kPayloadBytes, 'x');
    for (std::size_t offset = 0U; offset < payload.size(); offset += 4096U) {
        payload[offset] = static_cast<char>((offset / 4096U) & 0x7fU);
    }
    const auto put = payload_store.put_payload_or_throw(payload);
    const anonsync::SyncReplicaOperation operation =
        owner.publish_local_file_or_throw(
            "media/sixty-four-mib.bin", put.size_bytes,
            put.content_sha256);
    std::string().swap(payload);

    const auto channel =
        anonsync::testing::SyncReplicaDeliveryTestChannelFactory::make_or_throw(
            requester_actor, "source-frame-memory-transcript",
            "source-frame-memory-channel");
    anonsync::SyncReplicaReconciliationRequest request;
    request.folder_id = folder;
    request.requester_actor = requester_actor;
    request.responder_actor = source_actor;
    request.channel_binding = channel.context().binding;
    const std::string request_frame =
        anonsync::encode_sync_replica_reconciliation_request_or_throw(
            request, configured);

    auto direct_session = service.make_serve_session_or_throw(channel);
    arm_large_allocations(kLargeAllocationThreshold);
    anonsync::SyncReplicaFramedInboundReconciliation direct =
        service.serve_request_frame_or_throw(
            channel, request_frame, direct_session);
    const AllocationObservation direct_allocations =
        disarm_large_allocations();

    require(
        direct_allocations.count == 1U &&
            direct_allocations.peak_active_count == 1U &&
            direct_allocations.active_count == 1U,
        "shipping source retained a second range-sized allocation beside the final frame");
    require(
        direct_allocations.largest >= kPayloadBytes &&
            direct_allocations.bytes <=
                static_cast<std::uint64_t>(direct.response_frame.size()) +
                    4096U &&
            direct_allocations.peak_active_bytes ==
                direct_allocations.active_bytes,
        "shipping source did not keep exactly one payload-sized final frame live");
    require(
        direct.direct_payload_ranges == 1U &&
            direct.direct_payload_bytes == kPayloadBytes &&
            direct.direct_frame_payload_page_bytes_at_reservation == 0U &&
            direct.direct_frame_maximum_source_staging_bytes == 0U &&
            direct.direct_frame_borrowed_manifest_count == 0U &&
            direct.direct_frame_borrowed_manifest_chunks == 0U &&
            direct.direct_frame_manifest_materialization_bytes == 0U &&
            direct.direct_frame_open_source_descriptors_at_reservation == 1U,
        "shipping source direct-fill accounting lost the 64 MiB payload or its zero-copy frontier");
    require(
        direct.response.operations.size() == 1U &&
            direct.response.operations.front().operation_id ==
                operation.operation_id &&
            direct.response.payloads.size() == 1U &&
            direct.response.payloads.front().bytes.empty() &&
            direct.response.payloads.front().chunk_sha256 ==
                operation.content_sha256,
        "shipping source response metadata retained bytes or lost exact content identity");

    const anonsync::SyncReplicaReconciliationBorrowedResponse borrowed =
        anonsync::decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
            direct.response_frame, request, configured);
    require(
        borrowed.payload_bytes.size() == 1U &&
            borrowed.payload_bytes.front().size() == kPayloadBytes &&
            sha256_hex_view(borrowed.payload_bytes.front()) ==
                operation.content_sha256,
        "shipping source direct frame did not carry the exact 64 MiB payload");

    auto compatibility_session = service.make_serve_session_or_throw(channel);
    arm_large_allocations(kLargeAllocationThreshold);
    anonsync::SyncReplicaInboundReconciliation compatibility =
        service.serve_request_or_throw(
            channel, request_frame, compatibility_session);
    const AllocationObservation compatibility_allocations =
        disarm_large_allocations();
    require(
        compatibility_allocations.count == 2U &&
            compatibility_allocations.peak_active_count == 2U &&
            compatibility_allocations.active_count == 2U &&
            compatibility_allocations.bytes >= 2ULL * kPayloadBytes,
        "compatibility response no longer exposes the simultaneous frame-plus-owned-payload differential");
    require(
        compatibility.response_frame == direct.response_frame &&
            compatibility.response.payloads.size() == 1U &&
            compatibility.response.payloads.front().bytes.size() ==
                kPayloadBytes,
        "compatibility response changed canonical framing or payload ownership semantics");
}

[[nodiscard]] anonsync::SyncReplicaReconciliationProtocolLimits
sparse_extent_limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model.max_operations = 4U;
    value.model.max_context_entries = 32U;
    value.model.max_predecessor_ids = 32U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 4U * 1024U * 1024U;
    value.model.max_retained_context_entries = 128U;
    value.model.max_retained_predecessor_ids = 128U;
    value.max_operations_per_page = 1U;
    value.max_canonical_operation_bytes_per_page = 512U * 1024U;
    value.max_payloads_per_page = 1U;
    value.max_single_payload_bytes = 4U * 1024U * 1024U;
    value.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    value.max_payload_extent_bytes =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 16U * 1024U * 1024U;
    return value;
}

void test_sparse_four_tib_shape_keeps_one_bounded_range_allocation() {
    constexpr std::uint64_t kExtentBytes =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes;
    constexpr std::uint64_t kChunkBytes = 1024ULL * 1024ULL * 1024ULL;
    constexpr std::size_t kRangeBytes = 4U * 1024U * 1024U;
    constexpr std::size_t kLargeAllocationThreshold = 1024U * 1024U;
    static_assert(kExtentBytes % kChunkBytes == 0U);

    const auto configured = sparse_extent_limits();
    const std::string folder = "folder-sparse-four-tib-memory";
    const anonsync::SyncReplicaActor requester{
        "device-sparse-four-tib-requester", 99811U};
    const anonsync::SyncReplicaActor responder{
        "device-sparse-four-tib-responder", 99812U};
    const std::string whole_digest =
        anonsync::sha256_hex("synthetic-four-tib-whole-content");
    anonsync::SyncReplicaModel model(folder, responder, configured.model);
    const anonsync::SyncReplicaOperation operation =
        model.create_local_file_or_throw(
            "media/sparse-four-tib.bin", kExtentBytes, whole_digest);

    anonsync::SyncReplicaReconciliationRequest request;
    request.folder_id = folder;
    request.requester_actor = requester;
    request.responder_actor = responder;
    request.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "sparse-four-tib-transcript");

    anonsync::SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            kExtentBytes);
    const std::size_t chunk_count = static_cast<std::size_t>(
        kExtentBytes / kChunkBytes);
    manifest.chunks.reserve(chunk_count);
    for (std::size_t index = 0U; index < chunk_count; ++index) {
        manifest.chunks.push_back({
            kChunkBytes,
            anonsync::sha256_hex(
                "synthetic-four-tib-chunk-" + std::to_string(index))});
    }

    anonsync::SyncReplicaReconciliationResponse response;
    response.folder_id = folder;
    response.requester_actor = requester;
    response.responder_actor = responder;
    response.channel_binding = request.channel_binding;
    response.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            request, configured);
    response.disposition =
        anonsync::SyncReplicaReconciliationResponseDisposition::Page;
    response.source_state_generation = 1U;
    response.source_evidence_count = model.evidence_count();
    response.source_evidence_set_digest = model.evidence_set_digest();
    response.operations.push_back(operation);
    anonsync::SyncReplicaReconciliationPayload metadata;
    metadata.content_sha256 = whole_digest;
    metadata.total_size_bytes = kExtentBytes;
    metadata.offset_bytes = 0U;
    metadata.delta_manifest_digest =
        anonsync::sync_replica_reconciliation_delta_manifest_digest_or_throw(
            whole_digest, kExtentBytes, manifest);
    metadata.delta_manifest = std::move(manifest);
    metadata.delta_chunk_offset_bytes = 0U;
    metadata.delta_chunk_size_bytes = kChunkBytes;
    response.payloads.push_back(std::move(metadata));
    response.has_more = true;
    response.payload_continuation =
        anonsync::SyncReplicaReconciliationPayloadContinuation{
            operation.operation_id, whole_digest, kExtentBytes, kRangeBytes};

    arm_large_allocations(kLargeAllocationThreshold);
    anonsync::SyncReplicaReconciliationResponseFrameAssembly assembly =
        anonsync::begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(response), request, {kRangeBytes}, configured);
    std::span<char> destination = assembly.payload_bytes_or_throw(0U);
    for (std::size_t offset = 0U; offset < destination.size(); ++offset) {
        destination[offset] = static_cast<char>((offset * 17U) & 0xffU);
    }
    assembly.commit_payload_or_throw(
        0U, sha256_hex_view(std::string_view(
                destination.data(), destination.size())));
    anonsync::SyncReplicaReconciliationDirectFrameResponse direct =
        assembly.finish_or_throw();
    const AllocationObservation allocations = disarm_large_allocations();

    require(
        allocations.count == 1U &&
            allocations.peak_active_count == 1U &&
            allocations.active_count == 1U &&
            allocations.largest >= kRangeBytes &&
            allocations.bytes <=
                static_cast<std::uint64_t>(direct.frame.size()) + 4096U &&
            allocations.peak_active_bytes == allocations.active_bytes,
        "synthetic four-TiB extent allocated more than one live bounded wire frame");
    require(
        direct.payload_bytes == kRangeBytes &&
            direct.response.payloads.size() == 1U &&
            direct.response.payloads.front().total_size_bytes ==
                kExtentBytes &&
            direct.response.payloads.front().bytes.empty(),
        "synthetic four-TiB extent lost its bounded range or retained source bytes");
    const auto borrowed =
        anonsync::decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
            direct.frame, request, configured);
    require(
        borrowed.payload_bytes.size() == 1U &&
            borrowed.payload_bytes.front().size() == kRangeBytes &&
            borrowed.response.payload_continuation.has_value() &&
            borrowed.response.payload_continuation->total_size_bytes ==
                kExtentBytes,
        "synthetic four-TiB direct frame did not preserve extent and continuation semantics");
}


struct HistoryReadFence final {
    std::string_view forbidden_table;
    std::size_t denied_reads = 0U;
};

int deny_history_read_authorizer(
    void* context,
    int action,
    const char* first,
    const char*,
    const char*,
    const char*) noexcept {
    auto& fence = *static_cast<HistoryReadFence*>(context);
    if (action == SQLITE_READ && first != nullptr &&
        fence.forbidden_table == first) {
        ++fence.denied_reads;
        return SQLITE_DENY;
    }
    return SQLITE_OK;
}

class ScopedHistoryReadFence final {
public:
    ScopedHistoryReadFence(
        anonsync::SyncSqliteDbHandleSlot& database,
        HistoryReadFence& fence,
        std::string_view label)
        : database_(database) {
        if (sqlite3_set_authorizer(
                database_.get(), deny_history_read_authorizer, &fence) !=
            SQLITE_OK) {
            throw std::runtime_error(
                std::string(label) + " could not install history-read fence");
        }
    }

    ScopedHistoryReadFence(const ScopedHistoryReadFence&) = delete;
    ScopedHistoryReadFence& operator=(const ScopedHistoryReadFence&) = delete;

    ~ScopedHistoryReadFence() {
        if (sqlite3_set_authorizer(database_.get(), nullptr, nullptr) !=
            SQLITE_OK) {
            std::abort();
        }
    }

private:
    anonsync::SyncSqliteDbHandleSlot& database_;
};

[[nodiscard]] anonsync::SyncReplicaSqliteOwnerLimits startup_owner_limits() {
    anonsync::SyncReplicaSqliteOwnerLimits value;
    value.model.max_operations = 128U;
    value.model.max_context_entries = 512U;
    value.model.max_predecessor_ids = 512U;
    value.model.max_canonical_operation_bytes = 128U * 1024U;
    value.model.max_retained_canonical_bytes = 8U * 1024U * 1024U;
    value.model.max_retained_context_entries = 8192U;
    value.model.max_retained_predecessor_ids = 8192U;
    value.max_outbox_intents = 256U;
    value.max_outbox_destination_bytes = 256U * 1024U;
    return value;
}

[[nodiscard]] anonsync::SyncReplicaReconciliationProtocolLimits
startup_reconciliation_limits() {
    constexpr std::uint64_t kRangeBytes = 1ULL * 1024ULL * 1024ULL;
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model = startup_owner_limits().model;
    value.max_operations_per_page = 8U;
    value.max_canonical_operation_bytes_per_page = 1U * 1024U * 1024U;
    value.max_payloads_per_page = 1U;
    value.max_single_payload_bytes = kRangeBytes;
    value.max_payload_bytes_per_page = kRangeBytes;
    value.max_payload_extent_bytes =
        anonsync::kSyncReplicaDefaultMaximumPayloadExtentBytes;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 4U * 1024U * 1024U;
    return value;
}

[[nodiscard]] anonsync::SyncReplicaFileEffectSqliteOwnerLimits
startup_effect_limits() {
    anonsync::SyncReplicaFileEffectSqliteOwnerLimits value;
    value.model = startup_owner_limits().model;
    value.max_effects = 128U;
    value.max_payload_bytes = 4U * 1024U * 1024U;
    value.max_retained_payload_bytes = 16U * 1024U * 1024U;
    value.max_effects_per_device = 128U;
    value.max_retained_payload_bytes_per_device =
        16U * 1024U * 1024U;
    return value;
}

[[nodiscard]] anonsync::SyncReplicaFileDeliveryServiceLimits
startup_file_delivery_limits() {
    anonsync::SyncReplicaFileDeliveryServiceLimits value;
    value.evidence.wire_operation_limits = startup_owner_limits().model;
    value.max_payload_bytes = 4U * 1024U * 1024U;
    value.max_request_frame_bytes = 16U * 1024U * 1024U;
    value.max_receipt_frame_bytes = 1U * 1024U * 1024U;
    return value;
}

void test_peer_service_startup_is_history_cold_for_four_tib_tree() {
    constexpr std::uint64_t kFiles = 64U;
    constexpr std::uint64_t kFileBytes =
        64ULL * 1024ULL * 1024ULL * 1024ULL;
    constexpr std::uint64_t kLogicalTreeBytes =
        4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;
    static_assert(kFiles * kFileBytes == kLogicalTreeBytes);

    TemporaryDirectory temporary;
    const std::string folder = "folder-history-cold-startup";
    const anonsync::SyncReplicaActor local_actor{
        "device-history-cold-startup", 110001U};

    anonsync::SyncSqliteDb replica_database =
        open_database(temporary.database_path());
    anonsync::SyncReplicaSqliteOwner replica_owner(
        replica_database.db, folder, local_actor, startup_owner_limits(),
        "history-cold startup replica owner");
    for (std::uint64_t index = 0U; index < kFiles; ++index) {
        const std::string path =
            "media/library/shard-" + std::to_string(index) + ".bin";
        (void)replica_owner.publish_local_file_or_throw(
            path, kFileBytes, sha256_hex_view(path));
    }
    const anonsync::SyncReplicaSqliteSnapshot seeded =
        replica_owner.snapshot_or_throw();
    std::uint64_t logical_bytes = 0U;
    for (const anonsync::SyncReplicaOperation& operation :
         seeded.durable.operations) {
        if (operation.kind != anonsync::SyncReplicaValueKind::File) continue;
        if (logical_bytes >
            std::numeric_limits<std::uint64_t>::max() -
                operation.size_bytes) {
            throw std::runtime_error(
                "history-cold logical tree byte count overflowed");
        }
        logical_bytes += operation.size_bytes;
    }
    require(
        seeded.durable.operations.size() == kFiles &&
            logical_bytes == kLogicalTreeBytes,
        "history-cold startup fixture is not the exact logical 4 TiB tree");

    anonsync::SyncReplicaFilePayloadStoreLimits payload_limits;
    payload_limits.max_entries = 128U;
    payload_limits.max_payload_bytes = kFileBytes;
    payload_limits.max_indexed_bytes = kLogicalTreeBytes;
    payload_limits.max_transient_entries = 8U;
    payload_limits.max_transient_bytes = kFileBytes;
    anonsync::SyncReplicaFilePayloadStore payload_store(
        folder, temporary.payload_root(),
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits, "history-cold startup payload store");

    anonsync::SyncSqliteDb effect_database =
        open_database(temporary.effect_database_path());
    anonsync::SyncReplicaFileEffectSqliteOwner effect_owner(
        effect_database.db, folder, temporary.effect_root(),
        startup_effect_limits(), "history-cold startup effect owner");

    HistoryReadFence replica_fence{"sync_replica_operations", 0U};
    HistoryReadFence effect_fence{"sync_replica_file_effects", 0U};
    ScopedHistoryReadFence replica_guard(
        replica_database.db, replica_fence, "replica database");
    ScopedHistoryReadFence effect_guard(
        effect_database.db, effect_fence, "effect database");

    bool replica_control_blocked = false;
    try {
        (void)replica_owner.snapshot_or_throw();
    } catch (const std::exception&) {
        replica_control_blocked = true;
    }
    require(
        replica_control_blocked && replica_fence.denied_reads != 0U,
        "replica history-read fence did not reject the complete snapshot control");
    replica_fence.denied_reads = 0U;

    bool effect_control_blocked = false;
    try {
        (void)effect_owner.snapshot_or_throw();
    } catch (const std::exception&) {
        effect_control_blocked = true;
    }
    require(
        effect_control_blocked && effect_fence.denied_reads != 0U,
        "effect history-read fence did not reject the complete snapshot control");
    effect_fence.denied_reads = 0U;

    anonsync::SyncReplicaDeliveryServiceLimits delivery_limits;
    delivery_limits.wire_operation_limits = startup_owner_limits().model;
    arm_large_allocations(64U * 1024U);
    anonsync::SyncReplicaDeliveryService evidence_service(
        replica_owner, delivery_limits,
        "history-cold startup evidence service");
    anonsync::SyncReplicaReconciliationService reconciliation_service(
        replica_owner, payload_store, startup_reconciliation_limits(),
        "history-cold startup reconciliation service");
    anonsync::SyncReplicaFileDeliveryService file_service(
        replica_owner, &effect_owner, startup_file_delivery_limits(),
        "history-cold startup file service");
    const AllocationObservation startup_allocations =
        disarm_large_allocations();

    require(
        startup_allocations.count == 0U &&
            startup_allocations.bytes == 0U &&
            startup_allocations.largest == 0U &&
            startup_allocations.active_count == 0U &&
            startup_allocations.peak_active_bytes == 0U,
        "peer service construction allocated at least one 64 KiB history-shaped buffer");
    require(
        replica_fence.denied_reads == 0U &&
            effect_fence.denied_reads == 0U,
        "peer service construction attempted to read retained history");
    require(
        evidence_service.folder_id() == folder &&
            evidence_service.local_actor() == local_actor &&
            reconciliation_service.folder_id() == folder &&
            reconciliation_service.local_actor() == local_actor &&
            file_service.folder_id() == folder &&
            file_service.local_actor() == local_actor,
        "history-cold peer services lost their exact owner identity");
}

}  // namespace

int main() {
    try {
        test_active_source_projection_uses_one_fixed_vector_per_share();
        test_shipping_source_fills_one_64_mib_frame_without_range_copy();
        test_sparse_four_tib_shape_keeps_one_bounded_range_allocation();
        test_peer_service_startup_is_history_cold_for_four_tib_tree();
        std::cout
            << "sync replica reconciliation source-frame memory tests passed: "
            << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        g_probe.armed = false;
        std::cerr
            << "sync replica reconciliation source-frame memory tests failed after "
            << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() {
    std::cout
        << "sync replica reconciliation source-frame memory test skipped on Windows\n";
    return 0;
}

#endif
