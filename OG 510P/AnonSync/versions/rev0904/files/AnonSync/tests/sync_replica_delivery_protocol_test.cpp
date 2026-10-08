#include "sha256_digest.hpp"
#include "sync_replica_delivery_protocol.hpp"
#include "sync_replica_model.hpp"

#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

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
        const unsigned char original =
            static_cast<unsigned char>(mutated[index]);
        mutated[index] = static_cast<char>(original ^ 0x80U);
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
        fail(label + " accepted " + std::to_string(extra) +
             " trailing bytes");
    }
}

anonsync::SyncReplicaDeliveryProtocolLimits limits() {
    anonsync::SyncReplicaDeliveryProtocolLimits value;
    value.model.max_operations = 16U;
    value.model.max_context_entries = 64U;
    value.model.max_predecessor_ids = 64U;
    value.model.max_canonical_operation_bytes = 256U * 1024U;
    value.model.max_retained_canonical_bytes = 4U * 1024U * 1024U;
    value.model.max_retained_context_entries = 4096U;
    value.model.max_retained_predecessor_ids = 4096U;
    value.max_request_frame_bytes = 512U * 1024U;
    value.max_receipt_frame_bytes = 16U * 1024U;
    return value;
}

anonsync::SyncReplicaDeliveryRequest request_fixture() {
    const std::string folder = "folder-delivery-protocol";
    const anonsync::SyncReplicaActor sender{
        "device-delivery-protocol-sender", 7001U};
    const anonsync::SyncReplicaActor receiver{
        "device-delivery-protocol-receiver", 7002U};
    anonsync::SyncReplicaModel model(folder, sender, limits().model);
    anonsync::SyncReplicaOperation operation =
        model.create_local_file_or_throw(
            "protocol/file.bin", 7U, anonsync::sha256_hex("payload"));
    return {
        folder,
        sender,
        receiver,
        anonsync::sha256_hex("claim-1"),
        3U,
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "connection-transcript-a"),
        std::move(operation),
    };
}

anonsync::SyncReplicaDeliveryReceipt receipt_fixture(
    const anonsync::SyncReplicaDeliveryRequest& request) {
    anonsync::SyncReplicaDeliveryReceipt receipt;
    receipt.folder_id = request.folder_id;
    receipt.sender_actor = request.sender_actor;
    receipt.receiver_actor = request.receiver_actor;
    receipt.operation_id = request.operation.operation_id;
    receipt.claim_id = request.claim_id;
    receipt.dispatch_attempts = request.dispatch_attempts;
    receipt.request_digest =
        anonsync::sync_replica_delivery_request_digest_or_throw(
            request, limits());
    receipt.channel_binding = request.channel_binding;
    receipt.disposition =
        anonsync::SyncReplicaDeliveryReceiptDisposition::InsertedActive;
    receipt.evidence_state = anonsync::SyncReplicaEvidenceState::Active;
    receipt.receiver_state_generation = 11U;
    receipt.receiver_cutpoint_digest = anonsync::sha256_hex("cutpoint-11");
    return receipt;
}

void test_channel_binding_domain_and_validation() {
    const auto first =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "tls-exporter", std::string(32U, 'a'));
    const auto repeated =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "tls-exporter", std::string(32U, 'a'));
    const auto different_type =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "noise-h", std::string(32U, 'a'));
    const auto different_bytes =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "tls-exporter", std::string(32U, 'b'));
    require(first == repeated,
            "same channel observation did not derive a stable binding");
    require(first.digest != different_type.digest,
            "channel binding type was not domain separated");
    require(first.digest != different_bytes.digest,
            "channel binding bytes were not committed");
    require_error(
        [] {
            (void)anonsync::make_sync_replica_delivery_channel_binding_or_throw(
                "TLS Exporter", "bytes");
        },
        "type is invalid",
        "noncanonical channel binding type was accepted");
    require_error(
        [] {
            (void)anonsync::make_sync_replica_delivery_channel_binding_or_throw(
                "tls-exporter", "");
        },
        "1..4096",
        "empty channel binding observation was accepted");
}

void test_request_roundtrip_and_exact_identity() {
    const auto request = request_fixture();
    const std::string frame =
        anonsync::encode_sync_replica_delivery_request_or_throw(
            request, limits());
    const auto decoded =
        anonsync::decode_sync_replica_delivery_request_or_throw(
            frame, limits());
    require(decoded == request,
            "delivery request did not round-trip exactly");
    require_frame_adversarial_matrix_rejected(
        frame,
        [](std::string_view candidate) {
            (void)anonsync::decode_sync_replica_delivery_request_or_throw(
                candidate, limits());
        },
        "delivery request decoder");
    require(
        anonsync::encode_sync_replica_delivery_request_or_throw(
            decoded, limits()) == frame,
        "delivery request canonical re-encoding changed bytes");
    require(
        anonsync::sync_replica_delivery_request_digest_or_throw(
            decoded, limits()) == frame.substr(frame.size() - 64U),
        "request identity did not equal the structural frame seal");

    std::string tampered = frame;
    tampered[tampered.size() / 2U] ^= 0x01;
    require_error(
        [&] {
            (void)anonsync::decode_sync_replica_delivery_request_or_throw(
                tampered, limits());
        },
        "digest mismatch",
        "tampered request crossed the structural seal");

    std::string trailing = frame;
    trailing.push_back('\0');
    require_error(
        [&] {
            (void)anonsync::decode_sync_replica_delivery_request_or_throw(
                trailing, limits());
        },
        "body length is not exact",
        "request with trailing bytes was accepted");

    auto wrong_actor = request;
    wrong_actor.sender_actor.epoch += 1U;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_request_or_throw(
                wrong_actor, limits());
        },
        "operation authority",
        "request envelope laundered a different sender epoch");

    auto self_directed = request;
    self_directed.receiver_actor.device_id =
        self_directed.sender_actor.device_id;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_request_or_throw(
                self_directed, limits());
        },
        "self-directed",
        "self-directed request was accepted");
}

void test_receipt_roundtrip_and_request_binding() {
    const auto request = request_fixture();
    const auto receipt = receipt_fixture(request);
    const std::string frame =
        anonsync::encode_sync_replica_delivery_receipt_or_throw(
            receipt, limits());
    const auto decoded =
        anonsync::decode_sync_replica_delivery_receipt_or_throw(
            frame, limits());
    require(decoded == receipt,
            "delivery receipt did not round-trip exactly");
    require_frame_adversarial_matrix_rejected(
        frame,
        [](std::string_view candidate) {
            (void)anonsync::decode_sync_replica_delivery_receipt_or_throw(
                candidate, limits());
        },
        "delivery receipt decoder");
    require(
        anonsync::sync_replica_delivery_receipt_digest_or_throw(
            decoded, limits()) == frame.substr(frame.size() - 64U),
        "receipt identity did not equal the structural frame seal");
    anonsync::validate_sync_replica_delivery_receipt_for_request_or_throw(
        decoded, request, limits());
    ++checks;

    auto wrong_channel = request;
    wrong_channel.channel_binding =
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "connection-transcript-b");
    require_error(
        [&] {
            anonsync::validate_sync_replica_delivery_receipt_for_request_or_throw(
                decoded, wrong_channel, limits());
        },
        "exact request",
        "receipt replayed across a different channel binding");

    auto wrong_epoch = request;
    wrong_epoch.receiver_actor.epoch += 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_delivery_receipt_for_request_or_throw(
                decoded, wrong_epoch, limits());
        },
        "exact request",
        "receipt replayed across a different receiver epoch");

    auto invalid_active = receipt;
    invalid_active.evidence_state =
        anonsync::SyncReplicaEvidenceState::PendingMissingDependency;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_receipt_or_throw(
                invalid_active, limits());
        },
        "inconsistent evidence state",
        "active receipt fabricated a pending receiver state");

    auto capacity = receipt;
    capacity.disposition =
        anonsync::SyncReplicaDeliveryReceiptDisposition::CapacityBlocked;
    capacity.evidence_state.reset();
    const std::string capacity_frame =
        anonsync::encode_sync_replica_delivery_receipt_or_throw(
            capacity, limits());
    require(
        !anonsync::sync_replica_delivery_receipt_is_evidence_terminal(
            anonsync::decode_sync_replica_delivery_receipt_or_throw(
                capacity_frame, limits()).disposition),
        "capacity-blocked receipt was mislabeled evidence-terminal");

    auto zero_generation = capacity;
    zero_generation.receiver_state_generation = 0U;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_receipt_or_throw(
                zero_generation, limits());
        },
        "zero receiver generation",
        "capacity receipt encoded an impossible receiver cutpoint generation");

    capacity.evidence_state = anonsync::SyncReplicaEvidenceState::Active;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_receipt_or_throw(
                capacity, limits());
        },
        "fabricates retained evidence state",
        "capacity receipt fabricated receiver ownership");

    auto unknown = receipt;
    unknown.disposition =
        static_cast<anonsync::SyncReplicaDeliveryReceiptDisposition>(99U);
    require(
        !anonsync::sync_replica_delivery_receipt_is_evidence_terminal(
            unknown.disposition),
        "unknown receipt disposition acquired evidence-terminal authority");
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_receipt_or_throw(
                unknown, limits());
        },
        "disposition is invalid",
        "unknown receipt disposition was encoded");
}

void test_independent_frame_limits() {
    auto invalid_model = limits();
    invalid_model.model.max_operations = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_delivery_protocol_limits_or_throw(
                invalid_model);
        },
        "max_operations must be positive",
        "delivery protocol accepted an unusable wire-model configuration");

    const auto request = request_fixture();
    auto too_small = limits();
    too_small.max_request_frame_bytes =
        too_small.model.max_canonical_operation_bytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_delivery_protocol_limits_or_throw(
                too_small);
        },
        "cannot hold every operation",
        "wire configuration allowed a valid operation to become permanently unsendable");

    const auto receipt = receipt_fixture(request);
    too_small = limits();
    too_small.max_receipt_frame_bytes = 512U;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_delivery_receipt_or_throw(
                receipt, too_small);
        },
        "cannot hold every canonical receipt",
        "wire configuration allowed durable admission without an encodable receipt");
}

}  // namespace

int main() {
    try {
        test_channel_binding_domain_and_validation();
        test_request_roundtrip_and_exact_identity();
        test_receipt_roundtrip_and_request_binding();
        test_independent_frame_limits();
        std::cout << "sync replica delivery protocol tests passed: "
                  << checks << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica delivery protocol tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
