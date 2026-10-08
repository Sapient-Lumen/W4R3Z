#include "anonsync_core.hpp"
#include "peer_ingress_test_fixture.hpp"
#include "sync_peer_ingress_wire.hpp"

#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

namespace {

using namespace anonsync;
using anonsync::test::PeerIngressFixture;
namespace fs = std::filesystem;

static_assert(kSyncPeerTransportCanonicalWireVersion ==
              kPeerTransportIngressWireCodecVersion);

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

fs::path unique_database_path() {
#if defined(__unix__) || defined(__APPLE__)
    const auto process_id = static_cast<unsigned long long>(::getpid());
#else
    const auto process_id = 1ULL;
#endif
    return fs::temp_directory_path() /
        ("anonsync-rev0762-canonical-facade-" +
         std::to_string(process_id) + ".sqlite");
}

void remove_sqlite_family(const fs::path& path) {
    std::error_code error;
    fs::remove(path, error);
    fs::remove(path.string() + "-wal", error);
    fs::remove(path.string() + "-shm", error);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path database_path = unique_database_path();
    try {
        const PeerIngressFixture fixture =
            anonsync::test::make_peer_ingress_fixture("canonical-facade");

        SyncPeerTransportCanonicalCodecLimits public_limits;
        public_limits.max_wire_bytes = 64 * 1024;
        public_limits.max_string_bytes = 4096;
        public_limits.max_response_count = 16;
        public_limits.max_total_chunk_bytes = 64 * 1024;
        public_limits.max_chunk_bytes = 32 * 1024;

        PeerTransportIngressWireLimits internal_limits;
        internal_limits.max_frame_bytes = public_limits.max_wire_bytes;
        internal_limits.max_metadata_field_bytes = public_limits.max_string_bytes;
        internal_limits.max_chunk_count = public_limits.max_response_count;

        std::string public_wire = "sentinel";
        const SyncValidationResult encoded =
            encode_sync_peer_transport_canonical_payload(
                public_limits, fixture.envelope, fixture.chunks, public_wire);
        require(encoded.ok,
                "public canonical facade encode failed: " + encoded.reason,
                checks);

        std::string production_wire;
        std::string production_payload_digest;
        const SyncValidationResult production_encoded =
            encode_peer_transport_ingress_wire_frame(
                internal_limits,
                fixture.envelope,
                fixture.chunks,
                production_wire,
                production_payload_digest);
        require(production_encoded.ok,
                "production ingress frame encode failed: " +
                    production_encoded.reason,
                checks);
        require(public_wire == production_wire,
                "public canonical facade and durable ingress produced competing bytes",
                checks);
        require(public_wire.compare(0, std::string("ANONSYNC-PEER-INGRESS").size(),
                                    "ANONSYNC-PEER-INGRESS") == 0,
                "canonical facade did not emit the production ingress magic",
                checks);
        require(production_payload_digest ==
                    digest_peer_transport_ingress_payload(
                        fixture.envelope, fixture.chunks),
                "production wire payload digest disagrees with ingress evidence",
                checks);

        std::string second_wire;
        require(encode_sync_peer_transport_canonical_payload(
                    public_limits,
                    fixture.envelope,
                    fixture.chunks,
                    second_wire)
                    .ok,
                "second canonical facade encode failed",
                checks);
        require(second_wire == public_wire,
                "canonical facade is not deterministic",
                checks);

        SyncPeerTransportCanonicalPayload decoded;
        require(decode_sync_peer_transport_canonical_payload(
                    public_limits, public_wire, decoded)
                    .ok,
                "canonical facade decode failed",
                checks);
        require(anonsync::test::same_peer_ingress_evidence(
                    decoded.transport_envelope, fixture.envelope),
                "canonical facade decode changed envelope evidence",
                checks);
        require(decoded.chunk_bytes == fixture.chunks,
                "canonical facade decode changed binary chunks",
                checks);

        PeerTransportIngressWirePayload production_decoded;
        require(decode_peer_transport_ingress_wire_frame(
                    internal_limits, public_wire, production_decoded)
                    .ok,
                "production decoder rejected bytes emitted by public facade",
                checks);
        require(anonsync::test::same_peer_ingress_evidence(
                    production_decoded.transport_envelope, fixture.envelope) &&
                    production_decoded.chunk_bytes == fixture.chunks,
                "production decoder reconstructed different evidence",
                checks);

        for (std::size_t prefix = 0; prefix < public_wire.size(); ++prefix) {
            SyncPeerTransportCanonicalPayload sentinel;
            sentinel.transport_envelope.transport_instance_id = "sentinel";
            const SyncValidationResult result =
                decode_sync_peer_transport_canonical_payload(
                    public_limits, public_wire.substr(0, prefix), sentinel);
            require(!result.ok,
                    "canonical facade accepted truncation at byte " +
                        std::to_string(prefix),
                    checks);
            require(sentinel.transport_envelope.transport_instance_id == "sentinel",
                    "failed canonical facade decode published partial state",
                    checks);
        }

        std::string corrupt_chunk = public_wire;
        corrupt_chunk.back() ^= static_cast<char>(0x01);
        SyncPeerTransportCanonicalPayload rejected;
        rejected.transport_envelope.transport_instance_id = "sentinel-corrupt";
        require(!decode_sync_peer_transport_canonical_payload(
                    public_limits, corrupt_chunk, rejected)
                     .ok,
                "canonical facade accepted changed chunk bytes",
                checks);
        require(rejected.transport_envelope.transport_instance_id ==
                    "sentinel-corrupt",
                "corrupt decode changed caller output",
                checks);

        SyncPeerTransportCanonicalCodecLimits too_small_total = public_limits;
        too_small_total.max_total_chunk_bytes =
            fixture.envelope.peer_batch_envelope.total_bytes - 1;
        std::string failed_encode_output = "sentinel-encode";
        require(!encode_sync_peer_transport_canonical_payload(
                    too_small_total,
                    fixture.envelope,
                    fixture.chunks,
                    failed_encode_output)
                     .ok,
                "canonical facade ignored max_total_chunk_bytes",
                checks);
        require(failed_encode_output == "sentinel-encode",
                "failed canonical facade encode changed caller output",
                checks);

        SyncPeerTransportCanonicalCodecLimits too_small_chunk = public_limits;
        too_small_chunk.max_chunk_bytes =
            fixture.envelope.peer_batch_envelope.responses.front().length - 1;
        require(!encode_sync_peer_transport_canonical_payload(
                    too_small_chunk,
                    fixture.envelope,
                    fixture.chunks,
                    failed_encode_output)
                     .ok,
                "canonical facade ignored max_chunk_bytes",
                checks);

        SyncPeerTransportCanonicalCodecLimits impossible_limits = public_limits;
        impossible_limits.max_response_count = 100000000ULL;
        SyncPeerTransportCanonicalPayload impossible_output;
        impossible_output.transport_envelope.transport_instance_id =
            "sentinel-impossible";
        const SyncValidationResult impossible =
            decode_sync_peer_transport_canonical_payload(
                impossible_limits, public_wire, impossible_output);
        require(!impossible.ok,
                "canonical facade admitted an impossible response-count limit",
                checks);
        require(impossible.reason.find("impossible") != std::string::npos,
                "canonical facade did not enforce a frame-derived count bound: " +
                    impossible.reason,
                checks);
        require(impossible_output.transport_envelope.transport_instance_id ==
                    "sentinel-impossible",
                "impossible-limit decode changed caller output",
                checks);

        remove_sqlite_family(database_path);
        SyncPeerTransportIngressEnqueueOptions tight_options;
        tight_options.sqlite_path =
            fs::absolute(database_path).lexically_normal().string();
        tight_options.session_id = "session-canonical-facade";
        tight_options.enqueue_now_epoch = 101;
        tight_options.max_frame_bytes = 64 * 1024;
        tight_options.max_canonical_payload_bytes = 1;
        tight_options.max_chunk_count = 16;
        SyncPeerTransportIngressEnqueueResult tight_result;
        const SyncValidationResult tight =
            enqueue_sync_peer_transport_ingress_envelope(
                tight_options, fixture.envelope, fixture.chunks, tight_result);
        require(!tight.ok,
                "max_canonical_payload_bytes alias did not constrain enqueue",
                checks);

        SyncPeerTransportIngressEnqueueOptions enqueue_options = tight_options;
        enqueue_options.max_canonical_payload_bytes = 64 * 1024;
        SyncPeerTransportIngressEnqueueResult enqueued;
        const SyncValidationResult enqueue =
            enqueue_sync_peer_transport_ingress_envelope(
                enqueue_options, fixture.envelope, fixture.chunks, enqueued);
        require(enqueue.ok,
                "canonical facade enqueue failed: " + enqueue.reason,
                checks);
        require(enqueued.row_inserted && enqueued.canonical_payload_encoded &&
                    enqueued.canonical_payload_persisted,
                "enqueue compatibility aliases were not published",
                checks);
        require(enqueued.canonical_payload_codec_version ==
                    enqueued.payload_frame_codec_version &&
                    enqueued.canonical_payload_bytes ==
                        enqueued.payload_frame_bytes &&
                    enqueued.canonical_payload_sha256 ==
                        enqueued.payload_frame_sha256,
                "enqueue aliases contradict canonical frame evidence",
                checks);

        SyncPeerTransportIngressPayloadLoadOptions load_options;
        load_options.sqlite_path = enqueue_options.sqlite_path;
        load_options.session_id = enqueue_options.session_id;
        load_options.transport_envelope_idempotency_key =
            fixture.envelope.transport_envelope_idempotency_key;
        load_options.max_frame_bytes = 64 * 1024;
        load_options.max_canonical_payload_bytes = 64 * 1024;
        load_options.max_chunk_count = 16;
        SyncPeerTransportIngressPayloadLoadResult loaded;
        const SyncValidationResult load =
            load_sync_peer_transport_ingress_payload(load_options, loaded);
        require(load.ok,
                "canonical facade payload load failed: " + load.reason,
                checks);
        require(loaded.durable_payload_present &&
                    loaded.canonical_payload_hash_checked &&
                    loaded.canonical_payload_decoded,
                "load compatibility aliases were not published",
                checks);
        require(loaded.payload.chunk_bytes == fixture.chunks &&
                    anonsync::test::same_peer_ingress_evidence(
                        loaded.payload.transport_envelope, fixture.envelope),
                "load payload alias did not reconstruct evidence",
                checks);
        require(loaded.canonical_payload_codec_version == loaded.codec_version &&
                    loaded.canonical_payload_bytes ==
                        loaded.canonical_frame_bytes &&
                    loaded.canonical_payload_sha256 ==
                        loaded.canonical_frame_sha256,
                "load aliases contradict durable frame evidence",
                checks);

        enqueue_options.enqueue_now_epoch = 102;
        SyncPeerTransportIngressEnqueueResult duplicate;
        const SyncValidationResult duplicate_result =
            enqueue_sync_peer_transport_ingress_envelope(
                enqueue_options, fixture.envelope, fixture.chunks, duplicate);
        require(duplicate_result.ok && duplicate.row_already_present &&
                    duplicate.canonical_payload_persisted &&
                    duplicate.canonical_payload_reused,
                "duplicate aliases did not report durable reuse",
                checks);

        SyncPeerTransportIngressProcessOptions queued_options;
        queued_options.sqlite_path = enqueue_options.sqlite_path;
        queued_options.session_id = enqueue_options.session_id;
        SyncPeerTransportIngressProcessResult queued_result;
        const SyncValidationResult missing_key =
            process_sync_peer_transport_queued_ingress_envelope(
                queued_options,
                {}, {}, {}, {}, {}, {}, {}, {}, {}, queued_result);
        require(!missing_key.ok &&
                    missing_key.reason.find(
                        "transport_envelope_idempotency_key") !=
                        std::string::npos,
                "queued-process compatibility entry point did not fail closed",
                checks);

        remove_sqlite_family(database_path);
        std::cout << "sync peer canonical facade test: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        remove_sqlite_family(database_path);
        std::cerr << "sync peer canonical facade test: " << error.what()
                  << "\n";
        return 1;
    }
}
