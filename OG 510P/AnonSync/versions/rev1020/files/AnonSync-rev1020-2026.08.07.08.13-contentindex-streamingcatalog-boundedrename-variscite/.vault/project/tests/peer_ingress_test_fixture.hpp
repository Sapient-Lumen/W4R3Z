#pragma once

#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace anonsync::test {

struct PeerIngressFixture {
    SyncPeerTransportBoundChunkResponseBatchEnvelope envelope;
    std::vector<std::string> chunks;
};

inline PeerIngressFixture make_peer_ingress_fixture(const std::string& key_seed = "wire-fixture-envelope") {
    PeerIngressFixture fixture;
    fixture.chunks.emplace_back(std::string("alpha\0omega", 11));
    fixture.chunks.emplace_back(std::string("\x00\x01\x02\x7f\xff", 5));

    auto& envelope = fixture.envelope;
    auto& batch = envelope.peer_batch_envelope;
    batch.path.value = "docs/wire-fixture.bin";
    batch.request_idempotency_key = "request-evidence-v1";
    batch.schedule_idempotency_key = "schedule-evidence-v1";
    batch.peer_id = "peer-a";
    batch.peer_session_id = "peer-session-a";
    batch.peer_request_idempotency_key = "peer-request-evidence-v1";
    batch.peer_response_batch_idempotency_key = "peer-response-batch-evidence-v1";
    batch.batch_idempotency_key = "batch-evidence-v1";
    batch.remote_entry_digest = sha256_hex("remote-entry");
    batch.remote_version_digest = sha256_hex("remote-version");
    batch.apply_entry_idempotency_key = "apply-entry-evidence-v1";
    batch.response_count = static_cast<std::uint64_t>(fixture.chunks.size());
    batch.total_bytes = 0;

    std::uint64_t offset = 0;
    for (std::size_t i = 0; i < fixture.chunks.size(); ++i) {
        SyncChunkResponseEnvelope response;
        response.path = batch.path;
        response.request_idempotency_key = batch.request_idempotency_key;
        response.response_idempotency_key = "response-evidence-" + std::to_string(i + 1);
        response.remote_entry_digest = batch.remote_entry_digest;
        response.remote_version_digest = batch.remote_version_digest;
        response.apply_entry_idempotency_key = batch.apply_entry_idempotency_key;
        response.offset = offset;
        response.length = static_cast<std::uint64_t>(fixture.chunks[i].size());
        response.chunk_sha256 = sha256_hex(fixture.chunks[i]);
        batch.responses.push_back(response);
        offset += response.length;
        batch.total_bytes += response.length;
    }

    envelope.transport_instance_id = "transport-a";
    envelope.transport_key_id = "transport-key-a";
    envelope.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:" + sha256_hex(key_seed);
    envelope.transport_mac_sha256 = sha256_hex("wire-fixture-mac");
    envelope.issued_at_epoch = 100;
    envelope.expires_at_epoch = 200;
    envelope.max_response_count = 8;
    envelope.max_total_bytes = 4096;
    envelope.max_chunk_bytes = 2048;
    return fixture;
}

inline bool same_peer_ingress_evidence(
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& left,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& right) {
    const auto& lb = left.peer_batch_envelope;
    const auto& rb = right.peer_batch_envelope;
    if (left.transport_instance_id != right.transport_instance_id ||
        left.transport_key_id != right.transport_key_id ||
        left.transport_envelope_idempotency_key != right.transport_envelope_idempotency_key ||
        left.transport_mac_sha256 != right.transport_mac_sha256 ||
        left.issued_at_epoch != right.issued_at_epoch ||
        left.expires_at_epoch != right.expires_at_epoch ||
        left.max_response_count != right.max_response_count ||
        left.max_total_bytes != right.max_total_bytes ||
        left.max_chunk_bytes != right.max_chunk_bytes ||
        lb.path.value != rb.path.value ||
        lb.request_idempotency_key != rb.request_idempotency_key ||
        lb.schedule_idempotency_key != rb.schedule_idempotency_key ||
        lb.peer_id != rb.peer_id ||
        lb.peer_session_id != rb.peer_session_id ||
        lb.peer_request_idempotency_key != rb.peer_request_idempotency_key ||
        lb.peer_response_batch_idempotency_key != rb.peer_response_batch_idempotency_key ||
        lb.batch_idempotency_key != rb.batch_idempotency_key ||
        lb.remote_entry_digest != rb.remote_entry_digest ||
        lb.remote_version_digest != rb.remote_version_digest ||
        lb.apply_entry_idempotency_key != rb.apply_entry_idempotency_key ||
        lb.response_count != rb.response_count ||
        lb.total_bytes != rb.total_bytes ||
        lb.responses.size() != rb.responses.size()) {
        return false;
    }
    for (std::size_t i = 0; i < lb.responses.size(); ++i) {
        const auto& l = lb.responses[i];
        const auto& r = rb.responses[i];
        if (l.path.value != r.path.value ||
            l.request_idempotency_key != r.request_idempotency_key ||
            l.response_idempotency_key != r.response_idempotency_key ||
            l.remote_entry_digest != r.remote_entry_digest ||
            l.remote_version_digest != r.remote_version_digest ||
            l.apply_entry_idempotency_key != r.apply_entry_idempotency_key ||
            l.offset != r.offset || l.length != r.length ||
            l.chunk_sha256 != r.chunk_sha256) {
            return false;
        }
    }
    return true;
}

inline void refresh_fixture_chunk_evidence(PeerIngressFixture& fixture) {
    auto& batch = fixture.envelope.peer_batch_envelope;
    batch.total_bytes = 0;
    std::uint64_t offset = 0;
    for (std::size_t i = 0; i < fixture.chunks.size(); ++i) {
        auto& response = batch.responses.at(i);
        response.offset = offset;
        response.length = static_cast<std::uint64_t>(fixture.chunks[i].size());
        response.chunk_sha256 = sha256_hex(fixture.chunks[i]);
        offset += response.length;
        batch.total_bytes += response.length;
    }
}

}  // namespace anonsync::test
