#include "sha256_digest.hpp"
#include "sync_replica_reconciliation_compact_manifest.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <new>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

struct AllocationProbe final {
    bool armed = false;
    std::size_t minimum_size = 0U;
    std::size_t count = 0U;
    std::size_t requested_bytes = 0U;
    std::size_t largest_request = 0U;
};

AllocationProbe g_allocations;

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    if (g_allocations.armed && size >= g_allocations.minimum_size) {
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

void arm_allocations(std::size_t minimum_size = 0U) noexcept {
    g_allocations = AllocationProbe{true, minimum_size, 0U, 0U, 0U};
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

template <typename Exception, typename Function>
void require_throws(
    Function&& function,
    std::string_view expected,
    std::string_view message) {
    ++checks;
    try {
        function();
    } catch (const Exception& error) {
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

anonsync::SyncReplicaReconciliationDeltaManifest maximum_manifest() {
    using namespace anonsync;
    constexpr std::uint64_t kChunks =
        kSyncReplicaReconciliationMaximumContentDefinedChunks;
    constexpr std::uint64_t kChunkBytes =
        kSyncReplicaMaximumPayloadExtentBytes / kChunks;
    static_assert(
        kChunkBytes * kChunks == kSyncReplicaMaximumPayloadExtentBytes);

    SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters =
        sync_replica_reconciliation_content_defined_parameters_or_throw(
            kSyncReplicaMaximumPayloadExtentBytes);
    const std::string digest = sha256_hex("compact manifest maximum chunk");
    manifest.chunks.reserve(static_cast<std::size_t>(kChunks));
    for (std::uint64_t index = 0U; index < kChunks; ++index) {
        manifest.chunks.push_back({kChunkBytes, digest});
    }
    return manifest;
}

struct MaximumFrameFixture final {
    anonsync::SyncReplicaReconciliationRequest request;
    anonsync::SyncReplicaReconciliationResponse response;
    std::string range_bytes;
};

anonsync::SyncReplicaReconciliationProtocolLimits maximum_frame_limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.max_payload_extent_bytes =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes;
    return value;
}

MaximumFrameFixture maximum_frame_fixture(
    const anonsync::SyncReplicaReconciliationDeltaManifest& manifest,
    const anonsync::SyncReplicaReconciliationProtocolLimits& limits) {
    using namespace anonsync;
    const std::string folder = "folder-maximum-borrowed-manifest";
    const SyncReplicaActor requester{
        "device-maximum-manifest-requester", 101401U};
    const SyncReplicaActor responder{
        "device-maximum-manifest-responder", 101402U};
    SyncReplicaModel model(folder, responder, limits.model);
    const std::string content_digest =
        sha256_hex("synthetic four-tebibyte logical payload");
    const SyncReplicaOperation operation = model.create_local_file_or_throw(
        "media/four-tebibytes.bin", kSyncReplicaMaximumPayloadExtentBytes,
        content_digest);

    SyncReplicaReconciliationRequest request;
    request.folder_id = folder;
    request.requester_actor = requester;
    request.responder_actor = responder;
    request.channel_binding =
        make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "maximum-borrowed-manifest-transcript");

    SyncReplicaReconciliationResponse response;
    response.folder_id = folder;
    response.requester_actor = requester;
    response.responder_actor = responder;
    response.channel_binding = request.channel_binding;
    response.request_digest =
        sync_replica_reconciliation_request_digest_or_throw(request, limits);
    response.disposition =
        SyncReplicaReconciliationResponseDisposition::Page;
    response.source_state_generation = 1U;
    response.source_evidence_count = 1U;
    response.source_evidence_set_digest = model.evidence_set_digest();
    response.operations.push_back(operation);

    SyncReplicaReconciliationPayload payload;
    payload.content_sha256 = content_digest;
    payload.total_size_bytes = kSyncReplicaMaximumPayloadExtentBytes;
    payload.offset_bytes = 0U;
    payload.delta_manifest_digest =
        sync_replica_reconciliation_delta_manifest_digest_or_throw(
            content_digest, kSyncReplicaMaximumPayloadExtentBytes, manifest);
    payload.delta_chunk_offset_bytes = 0U;
    payload.delta_chunk_size_bytes = manifest.chunks.front().size_bytes;
    response.payloads.push_back(std::move(payload));
    response.has_more = true;
    response.payload_continuation =
        SyncReplicaReconciliationPayloadContinuation{
            operation.operation_id, operation.content_sha256,
            operation.size_bytes, 1U};
    return {std::move(request), std::move(response), "x"};
}

void test_maximum_shape_and_wire_round_trip() {
    using namespace anonsync;
    using CompactChunk = SyncReplicaReconciliationCompactManifestChunk;
    static_assert(sizeof(Sha256DigestValue) == 32U);
    static_assert(sizeof(SyncReplicaReconciliationDeltaChunk) == 40U);
    static_assert(sizeof(CompactChunk) == 40U);

    const SyncReplicaReconciliationDeltaManifest wire = maximum_manifest();
    const std::size_t chunk_count = wire.chunks.size();
    const std::size_t expected_compact_bytes =
        chunk_count * sizeof(CompactChunk);
    const std::size_t expected_wire_vector_bytes =
        chunk_count * sizeof(SyncReplicaReconciliationDeltaChunk);
    const std::size_t expected_offset_bytes =
        (chunk_count + 1U) * sizeof(std::uint64_t);
    constexpr std::uint64_t kChunkBytes =
        kSyncReplicaMaximumPayloadExtentBytes /
        kSyncReplicaReconciliationMaximumContentDefinedChunks;

    arm_allocations();
    SyncReplicaReconciliationDeltaManifest wire_with_offsets = wire;
    std::vector<std::uint64_t> wire_offsets;
    wire_offsets.reserve(chunk_count + 1U);
    wire_offsets.push_back(0U);
    for (const auto& chunk : wire_with_offsets.chunks) {
        wire_offsets.push_back(wire_offsets.back() + chunk.size_bytes);
    }
    const AllocationObservation wire_cache = disarm_allocations();
    require(
        wire_cache.count == 2U &&
            wire_cache.requested_bytes == expected_wire_vector_bytes +
                expected_offset_bytes &&
            wire_cache.largest_request == expected_wire_vector_bytes,
        "fixed-width wire manifest plus separate offsets was not exactly two bounded allocations");
    require(
        wire_offsets.back() == kSyncReplicaMaximumPayloadExtentBytes,
        "wire offset baseline did not cover the maximum payload");

    const std::string parser_digest =
        wire.chunks.front().sha256.lowercase_hex();
    std::vector<SyncReplicaReconciliationDeltaChunk> parsed_shape;
    arm_allocations();
    parsed_shape.reserve(chunk_count);
    for (std::size_t index = 0U; index < chunk_count; ++index) {
        parsed_shape.emplace_back(kChunkBytes, parser_digest);
    }
    const AllocationObservation parser_shape = disarm_allocations();
    require(
        parser_shape.count == 1U &&
            parser_shape.requested_bytes == expected_wire_vector_bytes &&
            parser_shape.largest_request == expected_wire_vector_bytes &&
            parsed_shape == wire.chunks,
        "maximum parser-shaped manifest construction was not one exact vector allocation");

    arm_allocations();
    const SyncReplicaReconciliationCompactManifest compact =
        SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
            kSyncReplicaMaximumPayloadExtentBytes, wire,
            "maximum compact manifest");
    const AllocationObservation construction = disarm_allocations();
    require(
        construction.count == 1U &&
            construction.requested_bytes == expected_compact_bytes &&
            construction.largest_request == expected_compact_bytes,
        "maximum compact manifest construction was not one exact vector allocation");
    require(
        compact.retained_chunk_capacity_bytes() == expected_compact_bytes,
        "compact manifest retained an unexpected chunk-storage capacity");
    require(
        compact.chunk_count() == chunk_count &&
            compact.total_size_bytes() ==
                kSyncReplicaMaximumPayloadExtentBytes &&
            compact.parameters() == wire.parameters,
        "compact manifest changed the maximum source identity");

    arm_allocations();
    const SyncReplicaReconciliationCompactManifest copied = compact;
    const AllocationObservation copy = disarm_allocations();
    require(
        copy.count == 1U && copy.requested_bytes == expected_compact_bytes &&
            copy.largest_request == expected_compact_bytes,
        "maximum compact manifest copy was not one exact vector allocation");
    require(copied == compact, "compact manifest copy changed its records");

    require(
        compact.chunk_index_for_offset_or_throw(0U) == 0U &&
            compact.chunk_index_for_offset_or_throw(kChunkBytes - 1U) == 0U &&
            compact.chunk_index_for_offset_or_throw(kChunkBytes) == 1U &&
            compact.chunk_index_for_offset_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes - 1U) ==
                chunk_count - 1U,
        "compact manifest cumulative lookup changed chunk ownership");
    require(
        compact.chunk_offset_bytes_or_throw(1U) == kChunkBytes &&
            compact.chunk_end_offset_bytes_or_throw(1U) ==
                2U * kChunkBytes &&
            compact.chunk_size_bytes_or_throw(1U) == kChunkBytes &&
            compact.chunk_sha256_hex_or_throw(1U) == wire.chunks[1U].sha256,
        "compact manifest changed a retained chunk extent or digest");

    const std::string retained_lookup_label(192U, 'l');
    std::uint64_t lookup_checksum = 0U;
    arm_allocations();
    for (std::size_t index = 0U; index < chunk_count; ++index) {
        const std::uint64_t offset =
            static_cast<std::uint64_t>(index) * kChunkBytes;
        const std::size_t found =
            compact.chunk_index_for_offset_or_throw(
                offset, retained_lookup_label);
        lookup_checksum +=
            static_cast<std::uint64_t>(found) +
            compact.chunk_offset_bytes_or_throw(
                found, retained_lookup_label) +
            compact.chunk_end_offset_bytes_or_throw(
                found, retained_lookup_label) +
            compact.chunk_size_bytes_or_throw(
                found, retained_lookup_label);
    }
    const AllocationObservation lookup = disarm_allocations();
    require(
        lookup.count == 0U && lookup.requested_bytes == 0U &&
            lookup.largest_request == 0U && lookup_checksum != 0U,
        "maximum compact manifest numeric lookup allocated memory");

    arm_allocations();
    const SyncReplicaReconciliationDeltaManifest materialized =
        compact.materialize_or_throw("maximum wire materialization");
    const AllocationObservation materialization = disarm_allocations();
    require(
        materialization.count == 1U &&
            materialization.requested_bytes == expected_wire_vector_bytes &&
            materialization.largest_request == expected_wire_vector_bytes,
        "wire materialization was not one exact fixed-width vector allocation");
    require(
        materialized == wire,
        "compact manifest materialization changed generation-9 wire semantics");
}

void test_rejections() {
    using namespace anonsync;
    const SyncReplicaReconciliationDeltaManifest maximum = maximum_manifest();

    require_throws<std::invalid_argument>(
        [&] {
            (void)SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
                0U, maximum, "zero payload");
        },
        "payload extent is invalid",
        "zero-sized compact payload was accepted");

    auto empty = maximum;
    empty.chunks.clear();
    require_throws<std::invalid_argument>(
        [&] {
            (void)SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes, empty, "empty manifest");
        },
        "chunk count",
        "empty compact manifest was accepted");

    auto noncanonical = maximum;
    noncanonical.parameters.average_chunk_bytes /= 2U;
    require_throws<std::invalid_argument>(
        [&] {
            (void)SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes, noncanonical,
                "noncanonical manifest");
        },
        "noncanonical",
        "noncanonical compact parameters were accepted");

    auto zero_chunk = maximum;
    zero_chunk.chunks.front().size_bytes = 0U;
    require_throws<std::invalid_argument>(
        [&] {
            (void)SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes, zero_chunk,
                "zero chunk");
        },
        "chunk extent",
        "zero-sized compact chunk was accepted");

    auto malformed_digest = maximum;
    const Sha256DigestValue original_digest =
        malformed_digest.chunks.front().sha256;
    require_throws<std::invalid_argument>(
        [&] {
            malformed_digest.chunks.front().sha256 = std::string(64U, 'g');
        },
        "fixed SHA-256 digest",
        "malformed fixed-width digest assignment was accepted");
    require(
        malformed_digest.chunks.front().sha256 == original_digest,
        "failed fixed-width digest assignment changed the prior value");

    auto incomplete = maximum;
    --incomplete.chunks.back().size_bytes;
    require_throws<std::invalid_argument>(
        [&] {
            (void)SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes, incomplete,
                "incomplete manifest");
        },
        "do not cover",
        "incomplete compact manifest was accepted");

    const SyncReplicaReconciliationCompactManifest compact =
        SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
            kSyncReplicaMaximumPayloadExtentBytes, maximum,
            "lookup rejection fixture");
    require_throws<std::invalid_argument>(
        [&] {
            (void)compact.chunk_index_for_offset_or_throw(
                kSyncReplicaMaximumPayloadExtentBytes, "terminal lookup");
        },
        "outside the payload",
        "terminal compact offset was accepted");
    require_throws<std::invalid_argument>(
        [&] {
            (void)compact.chunk_size_bytes_or_throw(
                compact.chunk_count(), "terminal chunk");
        },
        "outside the retained chunk frontier",
        "terminal compact chunk index was accepted");
}

void test_maximum_manifest_direct_frame_borrows_without_materialization() {
    using namespace anonsync;
    constexpr std::size_t kLargeAllocationThreshold = 256U * 1024U;
    const SyncReplicaReconciliationProtocolLimits limits =
        maximum_frame_limits();
    const SyncReplicaReconciliationDeltaManifest wire = maximum_manifest();
    const SyncReplicaReconciliationCompactManifest compact =
        SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
            kSyncReplicaMaximumPayloadExtentBytes, wire,
            "maximum direct-frame compact manifest");

    MaximumFrameFixture borrowed_fixture =
        maximum_frame_fixture(wire, limits);
    std::vector<std::uint64_t> borrowed_counts{1U};
    std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>> borrowed_views;
    borrowed_views.push_back(compact.borrow_for_direct_frame());

    arm_allocations(kLargeAllocationThreshold);
    SyncReplicaReconciliationResponseFrameAssembly borrowed_assembly =
        begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(borrowed_fixture.response), borrowed_fixture.request,
            std::move(borrowed_counts), std::move(borrowed_views), limits);
    std::span<char> borrowed_destination =
        borrowed_assembly.payload_bytes_or_throw(0U);
    require(
        borrowed_destination.size() == borrowed_fixture.range_bytes.size(),
        "borrowed maximum frame reserved the wrong payload extent");
    std::copy(
        borrowed_fixture.range_bytes.begin(),
        borrowed_fixture.range_bytes.end(), borrowed_destination.begin());
    borrowed_assembly.commit_payload_or_throw(
        0U, sha256_hex(borrowed_fixture.range_bytes));
    SyncReplicaReconciliationDirectFrameResponse borrowed =
        borrowed_assembly.finish_or_throw();
    const AllocationObservation borrowed_allocations = disarm_allocations();
    require(
        borrowed_allocations.count == 1U &&
            borrowed_allocations.largest_request >= 640U * 1024U,
        "direct maximum-manifest publication retained a second large allocation beside the final frame");
    require(
        borrowed.borrowed_delta_manifest_count == 1U &&
            borrowed.borrowed_delta_manifest_chunks ==
                kSyncReplicaReconciliationMaximumContentDefinedChunks &&
            !borrowed.response.payloads.front().delta_manifest.has_value(),
        "direct maximum-manifest publication lost its borrowed cardinality or rebuilt an owning manifest");
    const SyncReplicaReconciliationResponse decoded_borrowed =
        decode_sync_replica_reconciliation_response_or_throw(
            borrowed.frame, limits);
    require(
        decoded_borrowed.payloads.front().delta_manifest.has_value() &&
            decoded_borrowed.payloads.front().delta_manifest->chunks ==
                wire.chunks,
        "borrowed maximum manifest did not survive canonical generation-9 framing");

    MaximumFrameFixture owned_fixture = maximum_frame_fixture(wire, limits);
    std::vector<std::uint64_t> owned_counts{1U};
    arm_allocations(kLargeAllocationThreshold);
    owned_fixture.response.payloads.front().delta_manifest =
        compact.materialize_or_throw(
            "maximum owning direct-frame materialization baseline");
    SyncReplicaReconciliationResponseFrameAssembly owned_assembly =
        begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(owned_fixture.response), owned_fixture.request,
            std::move(owned_counts), limits);
    std::span<char> owned_destination =
        owned_assembly.payload_bytes_or_throw(0U);
    std::copy(
        owned_fixture.range_bytes.begin(), owned_fixture.range_bytes.end(),
        owned_destination.begin());
    owned_assembly.commit_payload_or_throw(
        0U, sha256_hex(owned_fixture.range_bytes));
    SyncReplicaReconciliationDirectFrameResponse owned =
        owned_assembly.finish_or_throw();
    const AllocationObservation owned_allocations = disarm_allocations();
    require(
        owned_allocations.count == 2U &&
            owned_allocations.requested_bytes ==
                borrowed_allocations.requested_bytes +
                    wire.chunks.size() *
                        sizeof(SyncReplicaReconciliationDeltaChunk),
        "owning baseline did not expose the exact eliminated 327,680-byte publication allocation");
    require(
        owned.frame == borrowed.frame &&
            owned.borrowed_delta_manifest_count == 0U &&
            owned.borrowed_delta_manifest_chunks == 0U,
        "borrowed publication changed generation-9 wire bytes or owning accounting");

    auto cached_reference_fixture = [&] {
        MaximumFrameFixture fixture = maximum_frame_fixture(wire, limits);
        const SyncReplicaOperation& operation =
            fixture.response.operations.front();
        fixture.request.expected_source_evidence_set_digest =
            fixture.response.source_evidence_set_digest;
        fixture.request.payload_continuation =
            SyncReplicaReconciliationPayloadContinuation{
                operation.operation_id, operation.content_sha256,
                operation.size_bytes, 1U};
        fixture.request.cached_delta_manifest_digest =
            fixture.response.payloads.front().delta_manifest_digest;
        fixture.response.payloads.front().offset_bytes = 1U;
        fixture.response.payload_continuation->next_offset_bytes = 2U;
        fixture.response.request_digest =
            sync_replica_reconciliation_request_digest_or_throw(
                fixture.request, limits);
        return fixture;
    };

    MaximumFrameFixture legacy_fixture = cached_reference_fixture();
    std::vector<std::uint64_t> legacy_counts{1U};
    arm_allocations();
    SyncReplicaReconciliationResponseFrameAssembly legacy_assembly =
        begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(legacy_fixture.response), legacy_fixture.request,
            std::move(legacy_counts), limits);
    std::copy(
        legacy_fixture.range_bytes.begin(), legacy_fixture.range_bytes.end(),
        legacy_assembly.payload_bytes_or_throw(0U).begin());
    legacy_assembly.commit_payload_or_throw(
        0U, sha256_hex(legacy_fixture.range_bytes));
    SyncReplicaReconciliationDirectFrameResponse legacy =
        legacy_assembly.finish_or_throw();
    const AllocationObservation legacy_allocations = disarm_allocations();

    MaximumFrameFixture explicit_fixture = cached_reference_fixture();
    std::vector<std::uint64_t> explicit_counts{1U};
    arm_allocations();
    using OptionalBorrowedManifest = std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>;
    std::vector<OptionalBorrowedManifest> explicit_absent(1U);
    SyncReplicaReconciliationResponseFrameAssembly explicit_assembly =
        begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(explicit_fixture.response), explicit_fixture.request,
            std::move(explicit_counts), std::move(explicit_absent), limits);
    std::copy(
        explicit_fixture.range_bytes.begin(), explicit_fixture.range_bytes.end(),
        explicit_assembly.payload_bytes_or_throw(0U).begin());
    explicit_assembly.commit_payload_or_throw(
        0U, sha256_hex(explicit_fixture.range_bytes));
    SyncReplicaReconciliationDirectFrameResponse explicit_result =
        explicit_assembly.finish_or_throw();
    const AllocationObservation explicit_allocations = disarm_allocations();
    require(
        legacy.frame == explicit_result.frame &&
            legacy.borrowed_delta_manifest_count == 0U &&
            explicit_result.borrowed_delta_manifest_count == 0U,
        "allocation-cold legacy delegation changed canonical response bytes");
    require(
        explicit_allocations.count == legacy_allocations.count + 1U,
        "legacy direct assembly retained a hidden absent-manifest vector allocation");
    require(
        explicit_allocations.requested_bytes ==
            legacy_allocations.requested_bytes +
                sizeof(OptionalBorrowedManifest),
        "legacy direct assembly did not remove the exact absent-sidecar allocation");

    {
        MaximumFrameFixture fixture = maximum_frame_fixture(wire, limits);
        fixture.response.payloads.front().delta_manifest = wire;
        std::vector<std::uint64_t> counts{1U};
        std::vector<std::optional<
            SyncReplicaReconciliationBorrowedDeltaManifest>> views;
        views.push_back(compact.borrow_for_direct_frame());
        require_throws<std::invalid_argument>(
            [&] {
                (void)begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                    std::move(fixture.response), fixture.request,
                    std::move(counts), std::move(views), limits);
            },
            "both owning and borrowed complete manifests",
            "direct framing accepted two complete-manifest authorities");
    }
    {
        MaximumFrameFixture fixture = maximum_frame_fixture(wire, limits);
        SyncReplicaReconciliationBorrowedDeltaManifest changed_extent =
            compact.borrow_for_direct_frame();
        --changed_extent.total_size_bytes;
        std::vector<std::uint64_t> counts{1U};
        std::vector<std::optional<
            SyncReplicaReconciliationBorrowedDeltaManifest>> views;
        views.push_back(changed_extent);
        require_throws<std::invalid_argument>(
            [&] {
                (void)begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                    std::move(fixture.response), fixture.request,
                    std::move(counts), std::move(views), limits);
            },
            "changed payload extent",
            "direct framing accepted a borrowed manifest for another extent");
    }
    {
        MaximumFrameFixture fixture = maximum_frame_fixture(wire, limits);
        SyncReplicaReconciliationBorrowedDeltaManifest noncanonical =
            compact.borrow_for_direct_frame();
        --noncanonical.parameters.average_chunk_bytes;
        std::vector<std::uint64_t> counts{1U};
        std::vector<std::optional<
            SyncReplicaReconciliationBorrowedDeltaManifest>> views;
        views.push_back(noncanonical);
        require_throws<std::invalid_argument>(
            [&] {
                (void)begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                    std::move(fixture.response), fixture.request,
                    std::move(counts), std::move(views), limits);
            },
            "parameters average chunk size",
            "direct framing accepted noncanonical borrowed parameters");
    }
    {
        MaximumFrameFixture fixture = maximum_frame_fixture(wire, limits);
        const SyncReplicaReconciliationBorrowedDeltaManifest canonical =
            compact.borrow_for_direct_frame();
        std::vector<SyncReplicaReconciliationCumulativeDeltaChunk> malformed(
            canonical.chunks.begin(), canonical.chunks.end());
        malformed[1U].end_offset_bytes = malformed[0U].end_offset_bytes;
        SyncReplicaReconciliationBorrowedDeltaManifest malformed_view =
            canonical;
        malformed_view.chunks = malformed;
        std::vector<std::uint64_t> counts{1U};
        std::vector<std::optional<
            SyncReplicaReconciliationBorrowedDeltaManifest>> views;
        views.push_back(malformed_view);
        require_throws<std::invalid_argument>(
            [&] {
                (void)begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                    std::move(fixture.response), fixture.request,
                    std::move(counts), std::move(views), limits);
            },
            "invalid chunk record",
            "direct framing accepted a non-increasing cumulative manifest");
    }
}

}  // namespace

int main() {
    try {
        test_maximum_shape_and_wire_round_trip();
        test_rejections();
        test_maximum_manifest_direct_frame_borrows_without_materialization();
        std::cout
            << "sync replica reconciliation compact manifest tests passed: "
            << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "sync replica reconciliation compact manifest test failed after "
            << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
