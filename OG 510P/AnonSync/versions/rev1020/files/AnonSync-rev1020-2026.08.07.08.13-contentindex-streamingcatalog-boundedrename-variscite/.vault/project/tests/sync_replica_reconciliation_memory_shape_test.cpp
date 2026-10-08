#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_reconciliation_protocol.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

struct LargeAllocationProbe final {
    bool armed = false;
    std::size_t threshold = 0U;
    std::size_t count = 0U;
    std::size_t bytes = 0U;
    std::size_t largest = 0U;
};

LargeAllocationProbe g_probe;

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    if (g_probe.armed && size >= g_probe.threshold) {
        ++g_probe.count;
        g_probe.bytes += size;
        g_probe.largest = std::max(g_probe.largest, size);
    }
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

struct AllocationObservation final {
    std::size_t count = 0U;
    std::size_t bytes = 0U;
    std::size_t largest = 0U;
};

void arm_large_allocations(std::size_t threshold) noexcept {
    g_probe = LargeAllocationProbe{true, threshold, 0U, 0U, 0U};
}

[[nodiscard]] AllocationObservation disarm_large_allocations() noexcept {
    g_probe.armed = false;
    return {g_probe.count, g_probe.bytes, g_probe.largest};
}

}  // namespace

void* operator new(std::size_t size) {
    return allocate_or_throw(size);
}

void* operator new[](std::size_t size) {
    return allocate_or_throw(size);
}

void operator delete(void* memory) noexcept {
    std::free(memory);
}

void operator delete[](void* memory) noexcept {
    std::free(memory);
}

void operator delete(void* memory, std::size_t) noexcept {
    std::free(memory);
}

void operator delete[](void* memory, std::size_t) noexcept {
    std::free(memory);
}

namespace {

void require(bool condition, std::string_view message, std::size_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

anonsync::SyncReplicaReconciliationProtocolLimits limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model.max_operations = 64U;
    value.model.max_context_entries = 128U;
    value.model.max_predecessor_ids = 128U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    value.model.max_retained_context_entries = 8192U;
    value.model.max_retained_predecessor_ids = 8192U;
    value.max_operations_per_page = 32U;
    value.max_canonical_operation_bytes_per_page = 4U * 1024U * 1024U;
    value.max_payloads_per_page = 16U;
    value.max_single_payload_bytes = 1024U * 1024U;
    value.max_payload_bytes_per_page = 16U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 24U * 1024U * 1024U;
    return value;
}

struct Fixture final {
    anonsync::SyncReplicaReconciliationRequest request;
    anonsync::SyncReplicaReconciliationResponse response;
    std::uint64_t payload_bytes = 0U;
};

Fixture fixture() {
    constexpr std::size_t kPayloadCount = 16U;
    constexpr std::size_t kPayloadBytes = 1024U * 1024U;
    const auto configured = limits();
    const std::string folder = "folder-reconciliation-memory-shape";
    const anonsync::SyncReplicaActor requester{
        "device-memory-shape-requester", 990701U};
    const anonsync::SyncReplicaActor responder{
        "device-memory-shape-responder", 990702U};
    anonsync::SyncReplicaModel model(folder, responder, configured.model);

    std::map<std::string, std::string> payloads_by_digest;
    for (std::size_t index = 0U; index < kPayloadCount; ++index) {
        std::string payload(kPayloadBytes, static_cast<char>('A' + index));
        const std::string digest = anonsync::sha256_hex(payload);
        (void)model.create_local_file_or_throw(
            "memory-shape/file-" + std::to_string(index) + ".bin",
            static_cast<std::uint64_t>(payload.size()), digest);
        payloads_by_digest.emplace(digest, std::move(payload));
    }

    Fixture out;
    out.request.folder_id = folder;
    out.request.requester_actor = requester;
    out.request.responder_actor = responder;
    out.request.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "memory-shape-transcript");

    out.response.folder_id = folder;
    out.response.requester_actor = requester;
    out.response.responder_actor = responder;
    out.response.channel_binding = out.request.channel_binding;
    out.response.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            out.request, configured);
    out.response.disposition =
        anonsync::SyncReplicaReconciliationResponseDisposition::Page;
    out.response.source_state_generation = 9907U;
    out.response.source_evidence_count = model.evidence_count();
    out.response.source_evidence_set_digest = model.evidence_set_digest();
    out.response.operations = model.all_evidence_operations();
    std::sort(
        out.response.operations.begin(), out.response.operations.end(),
        [](const auto& left, const auto& right) {
            return left.operation_id < right.operation_id;
        });
    for (auto& [digest, payload] : payloads_by_digest) {
        out.payload_bytes += static_cast<std::uint64_t>(payload.size());
        out.response.payloads.emplace_back(digest, std::move(payload));
    }
    out.response.next_after_operation_id =
        out.response.operations.back().operation_id;
    return out;
}

}  // namespace

int main() {
    using namespace anonsync;

    try {
        std::size_t checks = 0U;
        constexpr std::size_t kLargeAllocationThreshold = 512U * 1024U;
        const SyncReplicaReconciliationProtocolLimits configured = limits();
        const Fixture value = fixture();

        arm_large_allocations(kLargeAllocationThreshold);
        const SyncReplicaReconciliationEncodedResponse encoded =
            encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw(
                value.response, value.request, configured);
        const AllocationObservation encode_allocations =
            disarm_large_allocations();
        require(
            encode_allocations.count == 1U,
            "direct response encoding retained more than one page-sized allocation",
            checks);
        require(
            encode_allocations.largest >= value.payload_bytes &&
                encoded.payload_bytes == value.payload_bytes,
            "direct response encoding did not reserve one exact aggregate frame",
            checks);
        require(
            encoded.frame ==
                encode_sync_replica_reconciliation_response_or_throw(
                    value.response, configured),
            "direct response encoding changed canonical generation-9 framing",
            checks);
        require(
            encoded.response_digest ==
                sync_replica_reconciliation_response_digest_or_throw(
                    value.response, configured),
            "direct response encoding changed the semantic digest",
            checks);

        arm_large_allocations(kLargeAllocationThreshold);
        const SyncReplicaReconciliationBorrowedResponse borrowed =
            decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
                encoded.frame, value.request, configured);
        const AllocationObservation borrowed_allocations =
            disarm_large_allocations();
        require(
            borrowed_allocations.count == 0U,
            "borrowed response decode allocated another page-sized payload aggregate",
            checks);
        require(
            borrowed.payload_bytes.size() == value.response.payloads.size(),
            "borrowed response decode lost payload cardinality",
            checks);

        const std::uintptr_t frame_begin =
            reinterpret_cast<std::uintptr_t>(encoded.frame.data());
        const std::uintptr_t frame_end = frame_begin + encoded.frame.size();
        std::uint64_t borrowed_bytes = 0U;
        for (std::size_t index = 0U; index < borrowed.payload_bytes.size(); ++index) {
            const std::string_view payload = borrowed.payload_bytes[index];
            const std::uintptr_t payload_begin =
                reinterpret_cast<std::uintptr_t>(payload.data());
            borrowed_bytes += static_cast<std::uint64_t>(payload.size());
            require(
                borrowed.response.payloads[index].bytes.empty() &&
                    payload_begin >= frame_begin &&
                    payload_begin + payload.size() <= frame_end,
                "borrowed payload did not remain an exact view into the retained frame",
                checks);
        }
        require(
            borrowed_bytes == value.payload_bytes,
            "borrowed response decode changed aggregate payload bytes",
            checks);

        arm_large_allocations(kLargeAllocationThreshold);
        const SyncReplicaReconciliationResponse owned =
            decode_sync_replica_reconciliation_response_or_throw(
                encoded.frame, configured);
        const AllocationObservation owned_allocations =
            disarm_large_allocations();
        require(
            owned == value.response,
            "owned compatibility decode changed canonical response semantics",
            checks);
        require(
            owned_allocations.count >= value.response.payloads.size(),
            "owned compatibility decode did not expose the aggregate payload-copy differential",
            checks);

        std::cout << "sync replica reconciliation memory-shape tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        g_probe.armed = false;
        std::cerr << "sync replica reconciliation memory-shape tests failed: "
                  << error.what() << '\n';
        return 1;
    }
}
