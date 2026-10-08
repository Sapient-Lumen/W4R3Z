#include "sha256_digest.hpp"
#include "sync_replica_reconciliation_protocol.hpp"
#include "sync_replica_model.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

template <typename Decoder>
void require_frame_adversarial_matrix_rejected(
    std::string_view canonical_frame,
    Decoder&& decoder,
    const std::string& label) {
    for (std::size_t size = 0U; size < canonical_frame.size(); ++size) {
        ++checks;
        try {
            decoder(canonical_frame.substr(0U, size));
        } catch (const std::exception&) {
            continue;
        }
        fail(label + " accepted truncated prefix length " +
             std::to_string(size));
    }

    for (std::size_t index = 0U; index < canonical_frame.size(); ++index) {
        std::string mutated(canonical_frame);
        mutated[index] = static_cast<char>(
            static_cast<unsigned char>(mutated[index]) ^ 0x80U);
        ++checks;
        try {
            decoder(mutated);
        } catch (const std::exception&) {
            continue;
        }
        fail(label + " accepted single-byte mutation at offset " +
             std::to_string(index));
    }

    for (std::size_t extra = 1U; extra <= 8U; ++extra) {
        std::string extended(canonical_frame);
        extended.append(extra, static_cast<char>(0xa5));
        ++checks;
        try {
            decoder(extended);
        } catch (const std::exception&) {
            continue;
        }
        fail(label + " accepted trailing bytes");
    }
}

anonsync::SyncReplicaReconciliationProtocolLimits limits() {
    anonsync::SyncReplicaReconciliationProtocolLimits value;
    value.model.max_operations = 32U;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 8U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_operations_per_page = 8U;
    value.max_canonical_operation_bytes_per_page = 1024U * 1024U;
    value.max_payloads_per_page = 8U;
    value.max_single_payload_bytes = 1024U * 1024U;
    value.max_payload_bytes_per_page = 4U * 1024U * 1024U;
    value.max_request_frame_bytes = 64U * 1024U;
    value.max_response_frame_bytes = 8U * 1024U * 1024U;
    return value;
}

struct Fixtures final {
    anonsync::SyncReplicaReconciliationRequest request;
    anonsync::SyncReplicaReconciliationResponse response;
};

anonsync::SyncReplicaReconciliationDeltaManifest delta_manifest_for(
    std::string_view payload) {
    anonsync::SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            static_cast<std::uint64_t>(payload.size()));
    anonsync::SyncReplicaContentDefinedChunker chunker(
        manifest.parameters, "protocol test chunker");
    std::size_t chunk_begin = 0U;
    for (std::size_t index = 0U; index < payload.size(); ++index) {
        if (!chunker.consume_byte(static_cast<std::uint8_t>(
                static_cast<unsigned char>(payload[index])))) {
            continue;
        }
        const std::size_t size = index + 1U - chunk_begin;
        manifest.chunks.push_back({
            static_cast<std::uint64_t>(size),
            anonsync::sha256_hex(std::string(payload.substr(chunk_begin, size))),
        });
        chunk_begin = index + 1U;
    }
    if (chunk_begin != payload.size()) {
        chunker.finish_pending_chunk_or_throw();
        const std::size_t size = payload.size() - chunk_begin;
        manifest.chunks.push_back({
            static_cast<std::uint64_t>(size),
            anonsync::sha256_hex(std::string(payload.substr(chunk_begin))),
        });
    }
    return manifest;
}

Fixtures fixtures() {
    const auto configured = limits();
    const std::string folder = "folder-reconciliation-protocol";
    const anonsync::SyncReplicaActor requester{
        "device-reconciliation-requester", 9101U};
    const anonsync::SyncReplicaActor responder{
        "device-reconciliation-responder", 9102U};
    anonsync::SyncReplicaModel model(folder, responder, configured.model);

    const std::map<std::string, std::string> payload_by_path{
        {"protocol/alpha.bin", "alpha-payload"},
        {"protocol/beta.bin", "beta-payload"},
    };
    for (const auto& [path, payload] : payload_by_path) {
        (void)model.create_local_file_or_throw(
            path, payload.size(), anonsync::sha256_hex(payload));
    }
    (void)model.create_local_tombstone_or_throw("protocol/deleted.bin");

    anonsync::SyncReplicaReconciliationRequest request;
    request.folder_id = folder;
    request.requester_actor = requester;
    request.responder_actor = responder;
    request.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "reconciliation-transcript-alpha");

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
    response.source_state_generation = 17U;
    response.source_evidence_count = model.evidence_count();
    response.source_evidence_set_digest = model.evidence_set_digest();
    response.operations = model.all_evidence_operations();
    std::sort(
        response.operations.begin(), response.operations.end(),
        [](const auto& left, const auto& right) {
            return left.operation_id < right.operation_id;
        });

    std::map<std::string, std::string> payload_by_digest;
    for (const auto& [path, payload] : payload_by_path) {
        (void)path;
        payload_by_digest.emplace(anonsync::sha256_hex(payload), payload);
    }
    for (const auto& [digest, payload] : payload_by_digest) {
        response.payloads.push_back({digest, payload});
    }
    response.next_after_operation_id =
        response.operations.back().operation_id;
    return {std::move(request), std::move(response)};
}

void test_round_trip_and_exact_request_binding() {
    require(
        anonsync::kSyncReplicaReconciliationProtocolVersion == 9U,
        "shipping reconciliation protocol did not advance to generation 9");
    const auto configured = limits();
    const Fixtures value = fixtures();
    const std::string request_frame =
        anonsync::encode_sync_replica_reconciliation_request_or_throw(
            value.request, configured);
    const anonsync::SyncReplicaReconciliationEncodedResponse encoded =
        anonsync::encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw(
            value.response, value.request, configured);
    const std::string& response_frame = encoded.frame;

    require(
        anonsync::sha256_hex(request_frame) ==
            "1e6ae4e901d86679e4219ad764dbb290d1fcb4a2f7520490f8a75b6045efab51",
        "fixed-width digest representation changed the sealed rev1012 request frame");
    require(
        anonsync::sha256_hex(response_frame) ==
            "29304b77ca55367bbcd259c9119cdc916a2ca918fe0ae5836560a6a673fa8119",
        "fixed-width digest representation changed the sealed rev1012 response frame");

    require(
        anonsync::decode_sync_replica_reconciliation_request_or_throw(
            request_frame, configured) == value.request,
        "request did not survive canonical round trip");
    require(
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            response_frame, configured) == value.response,
        "response did not survive canonical round trip");
    require(
        encoded.frame ==
            anonsync::encode_sync_replica_reconciliation_response_or_throw(
                value.response, configured),
        "single-frame response encoder changed generation-9 wire bytes");
    require(
        encoded.response_digest ==
            anonsync::sync_replica_reconciliation_response_digest_or_throw(
                value.response, configured),
        "single-frame response encoder changed the semantic response digest");
    std::uint64_t expected_payload_bytes = 0U;
    for (const auto& payload : value.response.payloads) {
        expected_payload_bytes +=
            static_cast<std::uint64_t>(payload.bytes.size());
    }
    require(
        encoded.payload_bytes == expected_payload_bytes &&
            encoded.canonical_body_bytes < encoded.frame.size(),
        "single-frame response encoder did not report its exact bounded body and payload totals");

    const anonsync::SyncReplicaReconciliationBorrowedResponse borrowed =
        anonsync::decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
            response_frame, value.request, configured);
    require(
        borrowed.response.payloads.size() == borrowed.payload_bytes.size(),
        "borrowed response decoder lost payload cardinality");
    anonsync::SyncReplicaReconciliationResponse borrowed_owned =
        borrowed.response;
    const std::uintptr_t frame_begin =
        reinterpret_cast<std::uintptr_t>(response_frame.data());
    const std::uintptr_t frame_end = frame_begin + response_frame.size();
    for (std::size_t index = 0U; index < borrowed.payload_bytes.size(); ++index) {
        const std::string_view bytes = borrowed.payload_bytes[index];
        const std::uintptr_t bytes_begin =
            reinterpret_cast<std::uintptr_t>(bytes.data());
        require(
            borrowed.response.payloads[index].bytes.empty() &&
                bytes_begin >= frame_begin &&
                bytes_begin + bytes.size() <= frame_end,
            "borrowed response decoder copied or detached a payload byte field");
        borrowed_owned.payloads[index].bytes.assign(bytes);
    }
    require(
        borrowed_owned == value.response,
        "borrowed response metadata and frame-backed payload views did not reconstruct the canonical response");
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        value.response, value.request, configured);
    require(
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            value.request, configured) == value.response.request_digest,
        "response did not bind the canonical request digest");
    require(
        anonsync::sync_replica_reconciliation_response_digest_or_throw(
            value.response, configured) ==
            anonsync::sync_replica_reconciliation_response_digest_or_throw(
                anonsync::decode_sync_replica_reconciliation_response_or_throw(
                    response_frame, configured),
                configured),
        "response semantic digest changed across canonical framing");

    require_frame_adversarial_matrix_rejected(
        request_frame,
        [&](std::string_view frame) {
            (void)anonsync::decode_sync_replica_reconciliation_request_or_throw(
                frame, configured);
        },
        "reconciliation request frame");
    require_frame_adversarial_matrix_rejected(
        response_frame,
        [&](std::string_view frame) {
            (void)anonsync::decode_sync_replica_reconciliation_response_or_throw(
                frame, configured);
        },
        "reconciliation response frame");
}

void test_direct_response_frame_assembly_lifecycle() {
    const auto configured = limits();
    const Fixtures value = fixtures();
    const std::string canonical =
        anonsync::encode_sync_replica_reconciliation_response_for_request_or_throw(
            value.response, value.request, configured);

    anonsync::SyncReplicaReconciliationResponse metadata = value.response;
    std::vector<std::string> source_payloads;
    std::vector<std::uint64_t> payload_byte_counts;
    source_payloads.reserve(metadata.payloads.size());
    payload_byte_counts.reserve(metadata.payloads.size());
    for (auto& payload : metadata.payloads) {
        payload_byte_counts.push_back(
            static_cast<std::uint64_t>(payload.bytes.size()));
        source_payloads.push_back(std::move(payload.bytes));
        payload.bytes.clear();
        payload.chunk_sha256.clear();
    }

    anonsync::SyncReplicaReconciliationResponseFrameAssembly assembly =
        anonsync::begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(metadata), value.request, payload_byte_counts,
            configured);
    require(
        assembly.active() &&
            assembly.payload_count() == source_payloads.size(),
        "direct response frame assembly did not retain its exact payload frontier");
    require_error(
        [&] { (void)assembly.payload_bytes_or_throw(source_payloads.size()); },
        "out of range",
        "direct response frame assembly accepted out-of-range payload access");
    require_error(
        [&] { assembly.commit_payload_or_throw(source_payloads.size(),
                                               std::string(64U, '0')); },
        "out of range",
        "direct response frame assembly accepted out-of-range payload commit");
    require_error(
        [&] { (void)assembly.finish_or_throw(); },
        "uncommitted",
        "direct response frame assembly finished before payload commit");
    require_error(
        [&] { assembly.commit_payload_or_throw(0U, "not-a-digest"); },
        "lowercase SHA-256",
        "direct response frame assembly accepted malformed chunk identity");

    for (std::size_t index = 0U; index < source_payloads.size(); ++index) {
        std::span<char> destination = assembly.payload_bytes_or_throw(index);
        require(
            destination.size() == source_payloads[index].size(),
            "direct response frame assembly changed a declared payload range");
        std::copy(
            source_payloads[index].begin(), source_payloads[index].end(),
            destination.begin());
        assembly.commit_payload_or_throw(
            index, anonsync::sha256_hex(source_payloads[index]));
        require_error(
            [&] { (void)assembly.payload_bytes_or_throw(index); },
            "already committed",
            "direct response frame assembly exposed a committed payload slot");
        require_error(
            [&] {
                assembly.commit_payload_or_throw(
                    index, anonsync::sha256_hex(source_payloads[index]));
            },
            "committed twice",
            "direct response frame assembly accepted a duplicate payload commit");
    }

    anonsync::SyncReplicaReconciliationDirectFrameResponse direct =
        assembly.finish_or_throw();
    require(
        !assembly.active() && assembly.payload_count() == 0U,
        "finished direct response frame assembly retained mutable authority");
    require(
        direct.frame == canonical,
        "direct response frame assembly changed canonical generation-9 bytes");
    require(
        direct.response.payloads.size() == source_payloads.size() &&
            direct.payload_bytes ==
                static_cast<std::uint64_t>(
                    source_payloads[0U].size() + source_payloads[1U].size()),
        "direct response frame assembly changed its payload accounting");
    for (std::size_t index = 0U; index < direct.response.payloads.size();
         ++index) {
        require(
            direct.response.payloads[index].bytes.empty() &&
                direct.response.payloads[index].chunk_sha256 ==
                    anonsync::sha256_hex(source_payloads[index]),
            "direct response frame assembly retained source bytes or lost the exact range digest");
    }
    require_error(
        [&] { (void)assembly.finish_or_throw(); },
        "inactive",
        "finished direct response frame assembly permitted a second finish");

    auto already_owned = value.response;
    std::vector<std::uint64_t> already_owned_counts;
    for (const auto& payload : already_owned.payloads) {
        already_owned_counts.push_back(
            static_cast<std::uint64_t>(payload.bytes.size()));
    }
    require_error(
        [&] {
            (void)anonsync::begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                already_owned, value.request, already_owned_counts,
                configured);
        },
        "already owns payload bytes",
        "direct response frame assembly accepted a second payload owner");

    auto count_mismatch = value.response;
    for (auto& payload : count_mismatch.payloads) {
        payload.bytes.clear();
        payload.chunk_sha256.clear();
    }
    require_error(
        [&] {
            (void)anonsync::begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
                count_mismatch, value.request, {1U}, configured);
        },
        "payload count",
        "direct response frame assembly accepted a mismatched source-range frontier");
}

void test_cursor_source_binding_and_source_change() {
    const auto configured = limits();
    Fixtures value = fixtures();
    value.request.after_operation_id =
        value.response.operations.front().operation_id;
    value.request.expected_source_evidence_set_digest =
        value.response.source_evidence_set_digest;
    value.response.operations.erase(value.response.operations.begin());
    value.response.payloads.erase(
        std::remove_if(
            value.response.payloads.begin(), value.response.payloads.end(),
            [&](const auto& payload) {
                return std::none_of(
                    value.response.operations.begin(),
                    value.response.operations.end(),
                    [&](const auto& operation) {
                        return operation.kind ==
                                   anonsync::SyncReplicaValueKind::File &&
                               operation.content_sha256 ==
                                   payload.content_sha256;
                    });
            }),
        value.response.payloads.end());
    value.response.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            value.request, configured);
    value.response.next_after_operation_id =
        value.response.operations.back().operation_id;
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        value.response, value.request, configured);

    auto unpaired = value.request;
    unpaired.expected_source_evidence_set_digest.reset();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                unpaired, configured);
        },
        "source digest",
        "cursor without source digest was accepted");

    anonsync::SyncReplicaReconciliationResponse changed;
    changed.folder_id = value.request.folder_id;
    changed.requester_actor = value.request.requester_actor;
    changed.responder_actor = value.request.responder_actor;
    changed.channel_binding = value.request.channel_binding;
    changed.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            value.request, configured);
    changed.disposition =
        anonsync::SyncReplicaReconciliationResponseDisposition::SourceChanged;
    changed.source_state_generation = 18U;
    changed.source_evidence_count = 4U;
    changed.source_evidence_set_digest = anonsync::sha256_hex("changed-source");
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        changed, value.request, configured);

    auto unchanged = changed;
    unchanged.source_evidence_set_digest =
        *value.request.expected_source_evidence_set_digest;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                unchanged, value.request, configured);
        },
        "does not prove",
        "source-changed response accepted the unchanged source digest");

    auto initial = value.request;
    initial.after_operation_id.reset();
    initial.expected_source_evidence_set_digest.reset();
    changed.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            initial, configured);
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                changed, initial, configured);
        },
        "changed continued source",
        "initial request accepted a source-changed disposition");
}


void test_bounded_payload_continuation_round_trip() {
    auto configured = limits();
    configured.max_single_payload_bytes = 4U;
    configured.max_payload_bytes_per_page = 8U;
    configured.max_payload_extent_bytes = 16U;
    anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
        configured);

    const std::string folder = "folder-reconciliation-range-protocol";
    const anonsync::SyncReplicaActor requester{
        "device-reconciliation-range-requester", 9201U};
    const anonsync::SyncReplicaActor responder{
        "device-reconciliation-range-responder", 9202U};
    const std::string payload = "abcdefghij";
    anonsync::SyncReplicaModel model(folder, responder, configured.model);
    (void)model.create_local_file_or_throw(
        "protocol/large.bin", payload.size(), anonsync::sha256_hex(payload));
    const auto operations = model.all_evidence_operations();
    require(operations.size() == 1U,
            "range fixture did not create one source operation");
    const auto& operation = operations.front();
    const auto manifest = delta_manifest_for(payload);
    const std::string manifest_digest =
        anonsync::sync_replica_reconciliation_delta_manifest_digest_or_throw(
            operation.content_sha256, operation.size_bytes, manifest);

    anonsync::SyncReplicaReconciliationRequest initial;
    initial.folder_id = folder;
    initial.requester_actor = requester;
    initial.responder_actor = responder;
    initial.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "reconciliation-range-transcript");

    auto response_for = [&](
                            const anonsync::SyncReplicaReconciliationRequest& request,
                            std::vector<std::pair<std::uint64_t, std::string>> ranges,
                            std::optional<std::uint64_t> next_offset,
                            bool has_more) {
        anonsync::SyncReplicaReconciliationResponse response;
        response.folder_id = folder;
        response.requester_actor = requester;
        response.responder_actor = responder;
        response.channel_binding = initial.channel_binding;
        response.request_digest =
            anonsync::sync_replica_reconciliation_request_digest_or_throw(
                request, configured);
        response.disposition =
            anonsync::SyncReplicaReconciliationResponseDisposition::Page;
        response.source_state_generation = 23U;
        response.source_evidence_count = 1U;
        response.source_evidence_set_digest = model.evidence_set_digest();
        response.operations.push_back(operation);
        bool first_range = true;
        for (auto& [offset, bytes] : ranges) {
            if (!request.cached_delta_manifest_digest.has_value() &&
                first_range) {
                response.payloads.emplace_back(
                    operation.content_sha256, operation.size_bytes, offset,
                    anonsync::sha256_hex(bytes), std::move(bytes), manifest,
                    0U, operation.size_bytes);
            } else {
                response.payloads.emplace_back(
                    operation.content_sha256, operation.size_bytes, offset,
                    anonsync::sha256_hex(bytes), std::move(bytes),
                    request.cached_delta_manifest_digest.value_or(
                        manifest_digest),
                    0U, operation.size_bytes);
            }
            first_range = false;
        }
        response.has_more = has_more;
        if (next_offset.has_value()) {
            response.payload_continuation =
                anonsync::SyncReplicaReconciliationPayloadContinuation{
                    operation.operation_id, operation.content_sha256,
                    operation.size_bytes, *next_offset};
        } else {
            response.next_after_operation_id = operation.operation_id;
        }
        return response;
    };

    const auto first = response_for(
        initial, {{0U, "abcd"}, {4U, "efgh"}}, 8U, true);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        first, initial, configured);
    const std::string first_frame =
        anonsync::encode_sync_replica_reconciliation_response_or_throw(
            first, configured);
    require(
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            first_frame, configured) == first,
        "initial bounded multi-range response did not survive canonical framing");
    require(
        first.payloads.size() == 2U &&
            first.payloads[0].offset_bytes == 0U &&
            first.payloads[0].bytes == "abcd" &&
            first.payloads[0].delta_manifest.has_value() &&
            first.payloads[0].delta_manifest_digest ==
                std::optional<std::string>(manifest_digest) &&
            first.payloads[0].delta_manifest->parameters ==
                anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
                    payload.size()) &&
            first.payloads[0].delta_manifest->chunks ==
                std::vector<anonsync::SyncReplicaReconciliationDeltaChunk>{{
                    payload.size(), anonsync::sha256_hex(payload)}} &&
            first.payloads[0].delta_chunk_offset_bytes == 0U &&
            first.payloads[0].delta_chunk_size_bytes == payload.size() &&
            first.payloads[1].offset_bytes == 4U &&
            first.payloads[1].bytes == "efgh" &&
            first.payloads[1].delta_manifest_digest ==
                std::optional<std::string>(manifest_digest) &&
            !first.payloads[1].delta_manifest.has_value(),
        "bounded multi-range response did not publish one manifest then one exact reference");

    anonsync::SyncReplicaReconciliationRequest continued = initial;
    continued.expected_source_evidence_set_digest = model.evidence_set_digest();
    continued.payload_continuation = first.payload_continuation;
    continued.cached_delta_manifest_digest = manifest_digest;
    const std::string continued_frame =
        anonsync::encode_sync_replica_reconciliation_request_or_throw(
            continued, configured);
    require(
        anonsync::decode_sync_replica_reconciliation_request_or_throw(
            continued_frame, configured) == continued,
        "payload continuation request did not survive canonical framing");

    const auto final_response =
        response_for(continued, {{8U, "ij"}}, std::nullopt, false);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        final_response, continued, configured);
    require(
        final_response.payloads.size() == 1U &&
            final_response.payloads.front().delta_manifest_digest ==
                std::optional<std::string>(manifest_digest) &&
            !final_response.payloads.front().delta_manifest.has_value() &&
            final_response.next_after_operation_id ==
                std::optional<std::string>(operation.operation_id) &&
            !final_response.payload_continuation.has_value(),
        "legacy final bounded range group did not reference the manifest and complete the operation cursor");

    const auto final_handoff =
        response_for(continued, {{8U, "ij"}}, payload.size(), true);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        final_handoff, continued, configured);
    require(
        final_handoff.payloads.size() == 1U &&
            final_handoff.payloads.front().delta_manifest_digest ==
                std::optional<std::string>(manifest_digest) &&
            !final_handoff.payloads.front().delta_manifest.has_value() &&
            final_handoff.payload_continuation ==
                std::optional<anonsync::
                    SyncReplicaReconciliationPayloadContinuation>(
                    anonsync::SyncReplicaReconciliationPayloadContinuation{
                        operation.operation_id, operation.content_sha256,
                        operation.size_bytes, operation.size_bytes}) &&
            final_handoff.next_after_operation_id ==
                continued.after_operation_id &&
            final_handoff.has_more,
        "generation-9 final range did not hand off exact local terminal verification");

    anonsync::SyncReplicaReconciliationRequest terminal = continued;
    terminal.payload_continuation = final_handoff.payload_continuation;
    terminal.cached_delta_manifest_digest.reset();
    const std::string terminal_frame =
        anonsync::encode_sync_replica_reconciliation_request_or_throw(
            terminal, configured);
    require(
        anonsync::decode_sync_replica_reconciliation_request_or_throw(
            terminal_frame, configured) == terminal,
        "terminal payload verification request did not survive canonical generation-9 framing");
    const auto terminal_response = response_for(
        terminal, {}, operation.size_bytes, true);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        terminal_response, terminal, configured);
    const std::string terminal_response_frame =
        anonsync::encode_sync_replica_reconciliation_response_or_throw(
            terminal_response, configured);
    require(
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            terminal_response_frame, configured) == terminal_response &&
            terminal_response.operations ==
                std::vector<anonsync::SyncReplicaOperation>{operation} &&
            terminal_response.payloads.empty() &&
            terminal_response.payload_continuation ==
                terminal.payload_continuation &&
            terminal_response.next_after_operation_id ==
                terminal.after_operation_id &&
            terminal_response.has_more,
        "terminal payload verification response did not remain exact and payload-cold");

    auto terminal_with_cache = terminal;
    terminal_with_cache.cached_delta_manifest_digest = manifest_digest;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                terminal_with_cache, configured);
        },
        "terminal verification continuation cannot carry",
        "terminal payload verification request retained an obsolete manifest cache");

    auto terminal_past_end = terminal;
    ++terminal_past_end.payload_continuation->next_offset_bytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                terminal_past_end, configured);
        },
        "byte extent",
        "terminal payload verification continuation crossed its exact extent");

    auto terminal_with_payload = terminal_response;
    terminal_with_payload.payloads = final_handoff.payloads;
    terminal_with_payload.payloads.front().delta_manifest = manifest;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                terminal_with_payload, terminal, configured);
        },
        "one exact payload-cold operation",
        "terminal payload verification response carried source payload bytes");

    auto terminal_advanced_cursor = terminal_response;
    terminal_advanced_cursor.next_after_operation_id = operation.operation_id;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                terminal_advanced_cursor, terminal, configured);
        },
        "prior cursor",
        "terminal payload verification response advanced source operation authority");

    auto terminal_without_continuation = terminal_response;
    terminal_without_continuation.payload_continuation.reset();
    terminal_without_continuation.has_more = false;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                terminal_without_continuation, terminal, configured);
        },
        "size-bound range group",
        "terminal payload verification response omitted its continuation authority");

    auto terminal_not_nonterminal = terminal_response;
    terminal_not_nonterminal.has_more = false;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                terminal_not_nonterminal, terminal, configured);
        },
        "not marked nonterminal",
        "terminal payload verification response falsely claimed terminal source progress");

    auto continuation_without_source = continued;
    continuation_without_source.expected_source_evidence_set_digest.reset();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                continuation_without_source, configured);
        },
        "source digest",
        "payload continuation without a pinned source was accepted");

    auto zero_progress = continued;
    zero_progress.payload_continuation->next_offset_bytes = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                zero_progress, configured);
        },
        "byte extent",
        "zero-offset payload continuation was accepted");

    auto oversized_extent = continued;
    oversized_extent.payload_continuation->total_size_bytes =
        configured.max_payload_extent_bytes + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                oversized_extent, configured);
        },
        "byte extent",
        "payload continuation exceeded the complete-file extent");

    auto skipped = first;
    skipped.payload_continuation->next_offset_bytes = 9U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                skipped, configured);
        },
        "contiguous range group",
        "response continuation skipped a payload byte after a multi-range window");

    auto gapped = first;
    gapped.payloads[1].offset_bytes = 5U;
    gapped.payload_continuation->next_offset_bytes = 9U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                gapped, configured);
        },
        "not exactly contiguous",
        "multi-range response accepted a gap between adjacent records");

    auto overlapping = first;
    overlapping.payloads[1].offset_bytes = 3U;
    overlapping.payload_continuation->next_offset_bytes = 7U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                overlapping, configured);
        },
        "not exactly contiguous",
        "multi-range response accepted an overlap between adjacent records");

    auto repeated_manifest = first;
    repeated_manifest.payloads[1].delta_manifest = manifest;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                repeated_manifest, configured);
        },
        "confined to the first range",
        "multi-range response repeated its complete manifest");

    auto mismatched_group_manifest = first;
    mismatched_group_manifest.payloads[1].delta_manifest_digest =
        anonsync::sha256_hex("another-manifest");
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                mismatched_group_manifest, configured);
        },
        "disagree about their content-defined manifest",
        "multi-range response mixed manifest identities within one payload group");

    auto missing_manifest = first;
    missing_manifest.payloads.front().delta_manifest.reset();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                missing_manifest, initial, configured);
        },
        "omitted the complete content-defined manifest",
        "ranged payload omitted its complete manifest without receiver cache authority");

    auto noncanonical_manifest = first;
    noncanonical_manifest.payloads.front()
        .delta_manifest->parameters.average_chunk_bytes *= 2U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                noncanonical_manifest, configured);
        },
        "noncanonical content-defined parameters",
        "ranged payload accepted noncanonical content-defined parameters");

    auto missing_block = first;
    missing_block.payloads.front().delta_manifest->chunks.clear();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                missing_block, configured);
        },
        "chunk count is outside",
        "ranged payload accepted an incomplete content-defined manifest");

    auto invalid_block_digest = first;
    const auto original_block_digest = invalid_block_digest.payloads.front()
        .delta_manifest->chunks.front().sha256;
    require_error(
        [&] {
            invalid_block_digest.payloads.front()
                .delta_manifest->chunks.front().sha256 = "not-a-digest";
        },
        "fixed SHA-256 digest",
        "typed ranged manifest accepted an invalid content-defined chunk digest");
    require(
        invalid_block_digest.payloads.front()
                .delta_manifest->chunks.front().sha256 ==
            original_block_digest,
        "failed fixed digest assignment changed the retained manifest");

    auto corrupt_chunk = final_response;
    corrupt_chunk.payloads.front().chunk_sha256 =
        anonsync::sha256_hex("xx");
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                corrupt_chunk, configured);
        },
        "chunk digest",
        "ranged payload bytes were accepted under another chunk digest");

    auto replayed_first = first;
    replayed_first.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            continued, configured);
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                replayed_first, continued, configured);
        },
        "cached content-defined manifest reference",
        "continued request accepted a full-manifest replay instead of its exact reference");

    auto nonzero_initial =
        response_for(initial, {{4U, "efgh"}}, 8U, true);
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                nonzero_initial, initial, configured);
        },
        "nonzero offset",
        "initial request accepted a nonzero payload range group");

    auto wrong_reference = final_response;
    wrong_reference.payloads.front().delta_manifest_digest =
        anonsync::sha256_hex("another-manifest");
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                wrong_reference, continued, configured);
        },
        "cached content-defined manifest reference",
        "continued request accepted a different manifest reference");

    auto cached_without_continuation = initial;
    cached_without_continuation.cached_delta_manifest_digest =
        manifest_digest;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_request_or_throw(
                cached_without_continuation, configured);
        },
        "has no payload continuation",
        "initial request advertised an unbound manifest cache");

    auto incomplete_final = final_response;
    incomplete_final.next_after_operation_id.reset();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                incomplete_final, configured);
        },
        "last completed operation",
        "final payload range group did not have to advance its operation cursor");
}

void test_maximum_extent_manifest_reference_has_constant_wire_shape() {
    auto configured = limits();
    configured.max_single_payload_bytes =
        anonsync::kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes;
    configured.max_payload_bytes_per_page =
        configured.max_single_payload_bytes;
    configured.max_payload_extent_bytes =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes;
    anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
        configured);

    const std::string folder = "folder-reconciliation-maximum-manifest";
    const anonsync::SyncReplicaActor requester{
        "device-reconciliation-maximum-requester", 9251U};
    const anonsync::SyncReplicaActor responder{
        "device-reconciliation-maximum-responder", 9252U};
    const std::uint64_t total_size =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes;
    const std::string content_digest =
        anonsync::sha256_hex("logical-four-tib-payload");

    anonsync::SyncReplicaModel model(folder, responder, configured.model);
    const anonsync::SyncReplicaOperation operation =
        model.create_local_file_or_throw(
            "media/four-tib-shape.bin", total_size, content_digest);

    anonsync::SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters =
        anonsync::sync_replica_reconciliation_content_defined_parameters_or_throw(
            total_size);
    manifest.chunks.reserve(static_cast<std::size_t>(
        anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks));
    for (std::uint64_t index = 0U;
         index <
             anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks;
         ++index) {
        manifest.chunks.push_back({
            manifest.parameters.minimum_chunk_bytes,
            anonsync::sha256_hex(
                "logical-content-defined-chunk-" + std::to_string(index)),
        });
    }
    const std::string manifest_digest =
        anonsync::sync_replica_reconciliation_delta_manifest_digest_or_throw(
            content_digest, total_size, manifest);
    require(
        manifest.parameters.average_chunk_bytes ==
                anonsync::kSyncReplicaReconciliationMaximumAverageChunkBytes &&
            manifest.parameters.minimum_chunk_bytes *
                    manifest.chunks.size() ==
                total_size &&
            manifest.chunks.size() ==
                anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks,
        "maximum payload extent did not produce the canonical 8,192-chunk manifest frontier");

    anonsync::SyncReplicaReconciliationRequest initial;
    initial.folder_id = folder;
    initial.requester_actor = requester;
    initial.responder_actor = responder;
    initial.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "reconciliation-maximum-manifest");

    anonsync::SyncReplicaReconciliationResponse full;
    full.folder_id = folder;
    full.requester_actor = requester;
    full.responder_actor = responder;
    full.channel_binding = initial.channel_binding;
    full.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            initial, configured);
    full.source_state_generation = 29U;
    full.source_evidence_count = 1U;
    full.source_evidence_set_digest = model.evidence_set_digest();
    full.operations.push_back(operation);
    full.payloads.emplace_back(
        content_digest, total_size, 0U, anonsync::sha256_hex("x"), "x",
        manifest, 0U, manifest.parameters.minimum_chunk_bytes);
    full.has_more = true;
    full.payload_continuation =
        anonsync::SyncReplicaReconciliationPayloadContinuation{
            operation.operation_id, content_digest, total_size, 1U};
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        full, initial, configured);
    const std::string full_frame =
        anonsync::encode_sync_replica_reconciliation_response_or_throw(
            full, configured);

    anonsync::SyncReplicaReconciliationRequest continued = initial;
    continued.expected_source_evidence_set_digest =
        model.evidence_set_digest();
    continued.payload_continuation = full.payload_continuation;
    continued.cached_delta_manifest_digest = manifest_digest;

    anonsync::SyncReplicaReconciliationResponse referenced = full;
    referenced.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            continued, configured);
    referenced.payloads.clear();
    referenced.payloads.emplace_back(
        content_digest, total_size, 1U, anonsync::sha256_hex("y"), "y",
        manifest_digest, 0U, manifest.parameters.minimum_chunk_bytes);
    referenced.payload_continuation->next_offset_bytes = 2U;
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        referenced, continued, configured);
    const std::string referenced_frame =
        anonsync::encode_sync_replica_reconciliation_response_or_throw(
            referenced, configured);

    constexpr std::uint64_t chunk_wire_bytes = 8U + 8U + 64U;
    const std::uint64_t minimum_manifest_bytes =
        anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks *
        chunk_wire_bytes;
    require(
        full_frame.size() > referenced_frame.size() &&
            static_cast<std::uint64_t>(
                full_frame.size() - referenced_frame.size()) >=
                minimum_manifest_bytes,
        "maximum manifest reference did not remove the complete chunk vector from the continued frame");

    const std::uint64_t four_mib_ranges =
        total_size /
        anonsync::kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes;
    const std::uint64_t avoided_repeated_bytes =
        static_cast<std::uint64_t>(
            full_frame.size() - referenced_frame.size()) *
        (four_mib_ranges - 1U);
    require(
        four_mib_ranges == 1'048'576U &&
            avoided_repeated_bytes > 256ULL * 1024ULL * 1024ULL * 1024ULL,
        "maximum-extent framing proof did not remove more than 256 GiB of repeated manifest bytes");

    const std::uint64_t redundant_prefix_additions =
        anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks *
        four_mib_ranges;
    const std::uint64_t avoidable_offset_vector_bytes =
        (anonsync::kSyncReplicaReconciliationMaximumContentDefinedChunks + 1U) *
        static_cast<std::uint64_t>(sizeof(std::uint64_t)) *
        four_mib_ranges;
    require(
        redundant_prefix_additions == 8'589'934'592ULL &&
            avoidable_offset_vector_bytes == 68'727'865'344ULL &&
            avoidable_offset_vector_bytes >
                64ULL * 1024ULL * 1024ULL * 1024ULL,
        "maximum-extent scale proof did not expose the repeated cumulative-index multiplier removed by source-session index retention");

    const std::uint64_t ranges_per_default_window =
        anonsync::kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage /
        anonsync::kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes;
    const std::uint64_t bounded_window_turns =
        (four_mib_ranges + ranges_per_default_window - 1U) /
        ranges_per_default_window;
    require(
        ranges_per_default_window == 16U &&
            bounded_window_turns == 65'536U &&
            four_mib_ranges - bounded_window_turns == 983'040U,
        "maximum-extent scale proof did not collapse sixteen canonical ranges into each default bounded response window");
}

void test_response_invariant_rejections() {
    const auto configured = limits();
    const Fixtures value = fixtures();

    auto unsorted = value.response;
    std::swap(unsorted.operations[0], unsorted.operations[1]);
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                unsorted, configured);
        },
        "strictly sorted",
        "unsorted operation page was accepted");

    auto missing_payload = value.response;
    missing_payload.payloads.pop_back();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                missing_payload, configured);
        },
        "range",
        "file operation without its payload was accepted");

    auto extra_payload = value.response;
    extra_payload.payloads.push_back(
        {anonsync::sha256_hex("orphan"), "orphan"});
    std::sort(
        extra_payload.payloads.begin(), extra_payload.payloads.end(),
        [](const auto& left, const auto& right) {
            return left.content_sha256 < right.content_sha256;
        });
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                extra_payload, configured);
        },
        "unreferenced",
        "unreferenced payload was accepted");

    auto corrupt_payload = value.response;
    corrupt_payload.payloads.front().bytes.front() ^= 0x01;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                corrupt_payload, configured);
        },
        "digest",
        "payload bytes not bound to their digest were accepted");

    auto wrong_cursor = value.response;
    wrong_cursor.next_after_operation_id =
        wrong_cursor.operations.front().operation_id;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                wrong_cursor, configured);
        },
        "last completed operation",
        "page cursor did not identify the exact last operation");

    auto stalled = value.response;
    stalled.operations.clear();
    stalled.payloads.clear();
    stalled.next_after_operation_id.reset();
    stalled.has_more = true;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                stalled, configured);
        },
        "no cursor progress",
        "nonterminal empty page was accepted");

    auto payload_unavailable = value.response;
    const std::string blocked =
        payload_unavailable.operations.back().operation_id;
    const std::string blocked_digest =
        payload_unavailable.operations.back().content_sha256;
    payload_unavailable.operations.pop_back();
    payload_unavailable.payloads.erase(
        std::remove_if(
            payload_unavailable.payloads.begin(),
            payload_unavailable.payloads.end(),
            [&](const auto& payload) {
                return payload.content_sha256 == blocked_digest;
            }),
        payload_unavailable.payloads.end());
    payload_unavailable.disposition =
        anonsync::SyncReplicaReconciliationResponseDisposition::PayloadUnavailable;
    payload_unavailable.has_more = true;
    payload_unavailable.blocked_operation_id = blocked;
    payload_unavailable.next_after_operation_id =
        payload_unavailable.operations.back().operation_id;
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        payload_unavailable, value.request, configured);

    auto source_preparing = payload_unavailable;
    source_preparing.disposition =
        anonsync::SyncReplicaReconciliationResponseDisposition::
            SourcePayloadPreparing;
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        source_preparing, value.request, configured);
    const std::string source_preparing_frame =
        anonsync::encode_sync_replica_reconciliation_response_for_request_or_throw(
            source_preparing, value.request, configured);
    const auto decoded_source_preparing =
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            source_preparing_frame, configured);
    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        decoded_source_preparing, value.request, configured);
    require(
        decoded_source_preparing == source_preparing,
        "bounded source-preparing response did not survive canonical generation-9 framing");

    auto malformed_source_preparing = source_preparing;
    malformed_source_preparing.blocked_operation_id.reset();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                malformed_source_preparing, configured);
        },
        "source-preparing",
        "source-preparing response without exact blocked operation was accepted");

    auto wrong_binding = value.response;
    wrong_binding.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "another-transcript");
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                wrong_binding, value.request, configured);
        },
        "does not bind",
        "response crossed an unrelated authenticated channel");
}


void test_metadata_only_operation_set_is_explicit_and_policy_bound() {
    const auto configured = limits();
    const Fixtures value = fixtures();
    auto request = value.request;
    request.selective_sync_policy =
        anonsync::make_sync_replica_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"protocol/alpha.bin",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}},
            9U);

    auto response = value.response;
    response.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            request, configured);
    const auto selected = std::find_if(
        response.operations.begin(), response.operations.end(),
        [](const anonsync::SyncReplicaOperation& operation) {
            return operation.canonical_path == "protocol/alpha.bin";
        });
    require(
        selected != response.operations.end() &&
            selected->kind == anonsync::SyncReplicaValueKind::File,
        "metadata-only protocol fixture lacks its selected file");
    response.metadata_only_file_operation_ids = {selected->operation_id};
    response.payloads.erase(
        std::remove_if(
            response.payloads.begin(), response.payloads.end(),
            [&](const anonsync::SyncReplicaReconciliationPayload& payload) {
                return payload.content_sha256 == selected->content_sha256;
            }),
        response.payloads.end());

    anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
        response, request, configured);
    const std::string frame =
        anonsync::encode_sync_replica_reconciliation_response_or_throw(
            response, configured);
    require(
        anonsync::decode_sync_replica_reconciliation_response_or_throw(
            frame, configured) == response,
        "metadata-only operation set did not survive canonical framing");

    auto omitted = response;
    omitted.metadata_only_file_operation_ids.clear();
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                omitted, configured);
        },
        "range",
        "payload omission without explicit metadata-only evidence was accepted");

    auto extra = response;
    const auto tombstone = std::find_if(
        extra.operations.begin(), extra.operations.end(),
        [](const anonsync::SyncReplicaOperation& operation) {
            return operation.kind == anonsync::SyncReplicaValueKind::Tombstone;
        });
    require(tombstone != extra.operations.end(),
            "metadata-only protocol fixture lacks its tombstone");
    extra.metadata_only_file_operation_ids.push_back(tombstone->operation_id);
    std::sort(
        extra.metadata_only_file_operation_ids.begin(),
        extra.metadata_only_file_operation_ids.end());
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_or_throw(
                extra, configured);
        },
        "does not name a returned file operation",
        "metadata-only marker for a tombstone was accepted");

    auto all_materialize_request = value.request;
    auto policy_mismatch = response;
    policy_mismatch.request_digest =
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            all_materialize_request, configured);
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_response_for_request_or_throw(
                policy_mismatch, all_materialize_request, configured);
        },
        "exact requester policy",
        "metadata-only omission crossed an all-materialize request boundary");
    require(
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            request, configured) !=
        anonsync::sync_replica_reconciliation_request_digest_or_throw(
            all_materialize_request, configured),
        "selective-sync policy did not change the canonical request digest");
}

void test_limits_fail_closed() {
    auto configured = limits();
    configured.max_canonical_operation_bytes_per_page =
        configured.model.max_canonical_operation_bytes - 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "cannot hold one maximum",
        "canonical page budget smaller than one wire operation was accepted");

    configured = limits();
    configured.max_payload_bytes_per_page =
        configured.max_single_payload_bytes - 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "cannot hold one maximum payload",
        "payload page budget smaller than one payload was accepted");

    configured = limits();
    configured.max_payload_extent_bytes =
        configured.max_single_payload_bytes - 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "complete payload extent cannot hold one maximum range",
        "complete-file extent smaller than one range was accepted");

    configured = limits();
    configured.max_payload_extent_bytes =
        anonsync::kSyncReplicaMaximumPayloadExtentBytes + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "content-defined manifest frontier",
        "complete-file extent beyond the bounded manifest frontier was accepted");

    configured = limits();
    configured.max_payloads_per_page =
        anonsync::kSyncReplicaReconciliationMaximumPayloadsPerPage + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "fixed product memory and descriptor frontier",
        "payload descriptor fanout beyond the fixed product frontier was accepted");

    configured = limits();
    configured.max_payload_bytes_per_page =
        anonsync::kSyncReplicaReconciliationMaximumPayloadBytesPerPage + 1U;
    configured.max_single_payload_bytes =
        anonsync::kSyncReplicaReconciliationMaximumSinglePayloadBytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "fixed product memory and descriptor frontier",
        "payload page bytes beyond the fixed product frontier were accepted");

    configured = limits();
    configured.max_response_frame_bytes =
        anonsync::kSyncReplicaReconciliationMaximumResponseFrameBytes + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "fixed product memory and descriptor frontier",
        "response frame bytes beyond the fixed product frontier were accepted");

    configured = limits();
    configured.max_response_frame_bytes = 1024U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_reconciliation_protocol_limits_or_throw(
                configured);
        },
        "cannot hold every configured page",
        "undersized response frame budget was accepted");
}

}  // namespace

int main() {
    try {
        test_round_trip_and_exact_request_binding();
        test_direct_response_frame_assembly_lifecycle();
        test_cursor_source_binding_and_source_change();
        test_bounded_payload_continuation_round_trip();
        test_maximum_extent_manifest_reference_has_constant_wire_shape();
        test_response_invariant_rejections();
        test_metadata_only_operation_set_is_explicit_and_policy_bound();
        test_limits_fail_closed();
        std::cout << "sync replica reconciliation protocol tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica reconciliation protocol test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
