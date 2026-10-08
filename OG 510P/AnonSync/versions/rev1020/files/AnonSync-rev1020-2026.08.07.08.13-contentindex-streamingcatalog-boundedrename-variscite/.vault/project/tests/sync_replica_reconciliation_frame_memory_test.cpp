#include "sha256_digest.hpp"
#include "sync_replica_reconciliation_protocol.hpp"
#include "sync_replica_model.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

struct AllocationMeasurement final {
    std::uint64_t requested_bytes = 0U;
    std::size_t largest_request = 0U;
    std::size_t allocation_count = 0U;
    bool armed = false;
};

AllocationMeasurement g_allocations;

void observe_allocation(std::size_t size) noexcept {
    if (!g_allocations.armed) return;
    ++g_allocations.allocation_count;
    if (size > g_allocations.largest_request) {
        g_allocations.largest_request = size;
    }
    const std::uint64_t converted = static_cast<std::uint64_t>(size);
    if (converted >
        std::numeric_limits<std::uint64_t>::max() -
            g_allocations.requested_bytes) {
        std::abort();
    }
    g_allocations.requested_bytes += converted;
}

void* allocate_or_throw(std::size_t size) {
    observe_allocation(size);
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

class AllocationScope final {
public:
    AllocationScope() noexcept {
        g_allocations.requested_bytes = 0U;
        g_allocations.largest_request = 0U;
        g_allocations.allocation_count = 0U;
        g_allocations.armed = true;
    }

    AllocationScope(const AllocationScope&) = delete;
    AllocationScope& operator=(const AllocationScope&) = delete;

    ~AllocationScope() { g_allocations.armed = false; }

    void disarm() noexcept { g_allocations.armed = false; }
};

std::size_t checks = 0U;

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

anonsync::SyncReplicaReconciliationProtocolLimits limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model.max_operations = 4U;
    value.model.max_context_entries = 16U;
    value.model.max_predecessor_ids = 16U;
    value.model.max_canonical_operation_bytes = 64U * 1024U;
    value.model.max_retained_canonical_bytes = 512U * 1024U;
    value.model.max_retained_context_entries = 64U;
    value.model.max_retained_predecessor_ids = 64U;
    value.max_operations_per_page = 1U;
    value.max_canonical_operation_bytes_per_page = 64U * 1024U;
    value.max_payloads_per_page = 1U;
    value.max_single_payload_bytes = 8U * 1024U * 1024U;
    value.max_payload_bytes_per_page = 8U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 16U * 1024U * 1024U;
    return value;
}

anonsync::SyncReplicaReconciliationResponse large_response(
    const anonsync::SyncReplicaReconciliationProtocolLimits& configured) {
    constexpr std::size_t payload_bytes = 8U * 1024U * 1024U;
    std::string payload(payload_bytes, 'x');
    for (std::size_t offset = 0U; offset < payload.size(); offset += 4096U) {
        payload[offset] = static_cast<char>((offset / 4096U) & 0x7fU);
    }
    const std::string content_sha256 = anonsync::sha256_hex(payload);

    const std::string folder_id = "folder-frame-memory";
    const anonsync::SyncReplicaActor requester{
        "device-frame-memory-requester", 7711U};
    const anonsync::SyncReplicaActor responder{
        "device-frame-memory-responder", 7712U};
    anonsync::SyncReplicaModel model(
        folder_id, responder, configured.model);
    (void)model.create_local_file_or_throw(
        "media/large.bin", static_cast<std::uint64_t>(payload.size()),
        content_sha256);

    anonsync::SyncReplicaReconciliationRequest request;
    request.folder_id = folder_id;
    request.requester_actor = requester;
    request.responder_actor = responder;
    request.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "frame-memory-transcript");

    anonsync::SyncReplicaReconciliationResponse response;
    response.folder_id = folder_id;
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
    response.operations = model.all_evidence_operations();
    std::sort(
        response.operations.begin(), response.operations.end(),
        [](const auto& left, const auto& right) {
            return left.operation_id < right.operation_id;
        });
    response.next_after_operation_id =
        response.operations.back().operation_id;
    response.payloads.emplace_back(content_sha256, std::move(payload));
    return response;
}

void test_response_encoding_has_one_page_sized_allocation() {
    const auto configured = limits();
    const auto response = large_response(configured);
    anonsync::validate_sync_replica_reconciliation_response_or_throw(
        response, configured);

    std::string frame;
    AllocationScope measurement;
    frame = anonsync::encode_sync_replica_reconciliation_response_or_throw(
        response, configured);
    measurement.disarm();

    const std::uint64_t frame_bytes =
        static_cast<std::uint64_t>(frame.size());
    constexpr std::uint64_t auxiliary_budget = 2U * 1024U * 1024U;
    require(
        frame_bytes > 8U * 1024U * 1024U,
        "large response frame did not contain the complete payload page");
    require(
        g_allocations.largest_request >= frame.size(),
        "response encoder did not reserve one complete final frame");
    require(
        g_allocations.largest_request <= frame.size() + 4096U,
        "response encoder made an allocation materially larger than the final frame");
    require(
        g_allocations.requested_bytes <= frame_bytes + auxiliary_budget,
        "response encoder allocated a second page-sized body or frame copy");
    require(
        g_allocations.allocation_count > 0U,
        "response encoder allocation accounting observed no allocation");
    require(
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            frame, configured) == response,
        "single-allocation response frame did not round trip exactly");
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

int main() {
    try {
        test_response_encoding_has_one_page_sized_allocation();
        std::cout
            << "sync replica reconciliation frame memory tests passed: "
            << checks << " checks; frame allocation bytes="
            << g_allocations.requested_bytes << "; largest="
            << g_allocations.largest_request << "; allocations="
            << g_allocations.allocation_count << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "sync replica reconciliation frame memory test failed after "
            << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
