#include "sha256_digest.hpp"
#include "sync_replica_file_delivery_protocol.hpp"
#include "sync_replica_file_effect_identity.hpp"
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
void require_error(Callable&& callable,
                   std::string_view expected,
                   const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

template <typename Decoder>
void require_adversarial_frame_rejected(std::string_view canonical,
                                        Decoder&& decoder,
                                        const std::string& label) {
    for (std::size_t size = 0U; size < canonical.size(); ++size) {
        ++checks;
        try {
            decoder(canonical.substr(0U, size));
        } catch (const std::exception&) {
            continue;
        }
        fail(label + " accepted truncated prefix " + std::to_string(size));
    }
    for (std::size_t index = 0U; index < canonical.size(); ++index) {
        std::string mutated(canonical);
        mutated[index] = static_cast<char>(
            static_cast<unsigned char>(mutated[index]) ^ 0x80U);
        ++checks;
        try {
            decoder(mutated);
        } catch (const std::exception&) {
            continue;
        }
        fail(label + " accepted mutation at " + std::to_string(index));
    }
    for (std::size_t extra = 1U; extra <= 4U; ++extra) {
        std::string extended(canonical);
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

anonsync::SyncReplicaFileDeliveryProtocolLimits limits() {
    anonsync::SyncReplicaFileDeliveryProtocolLimits value;
    value.evidence.model.max_operations = 16U;
    value.evidence.model.max_context_entries = 64U;
    value.evidence.model.max_predecessor_ids = 64U;
    value.evidence.model.max_canonical_operation_bytes = 64U * 1024U;
    value.evidence.model.max_retained_canonical_bytes = 1024U * 1024U;
    value.evidence.model.max_retained_context_entries = 1024U;
    value.evidence.model.max_retained_predecessor_ids = 1024U;
    value.evidence.max_request_frame_bytes = 128U * 1024U;
    value.evidence.max_receipt_frame_bytes = 16U * 1024U;
    value.max_payload_bytes = 1024U;
    value.max_request_frame_bytes = 132U * 1024U;
    value.max_receipt_frame_bytes = 24U * 1024U;
    return value;
}

struct Fixture final {
    std::string payload{"binary\0payload\xff", 15U};
    anonsync::SyncReplicaFileDeliveryRequest request;
};

Fixture request_fixture() {
    const std::string folder = "folder-file-delivery-protocol";
    const anonsync::SyncReplicaActor sender{
        "device-file-delivery-protocol-sender", 9201U};
    const anonsync::SyncReplicaActor receiver{
        "device-file-delivery-protocol-receiver", 9202U};
    anonsync::SyncReplicaModel model(folder, sender, limits().evidence.model);
    Fixture fixture;
    const anonsync::SyncReplicaOperation operation =
        model.create_local_file_or_throw(
            "nested/file.bin",
            static_cast<std::uint64_t>(fixture.payload.size()),
            anonsync::sha256_hex(fixture.payload));
    fixture.request.evidence_request = {
        folder,
        sender,
        receiver,
        anonsync::sha256_hex("file-delivery-claim"),
        4U,
        anonsync::make_sync_replica_delivery_channel_binding_or_throw(
            "test-channel", "file-delivery-transcript"),
        operation,
    };
    fixture.request.payload = fixture.payload;
    return fixture;
}

anonsync::SyncReplicaDeliveryReceipt evidence_receipt_fixture(
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
            request, limits().evidence);
    receipt.channel_binding = request.channel_binding;
    receipt.disposition =
        anonsync::SyncReplicaDeliveryReceiptDisposition::InsertedActive;
    receipt.evidence_state = anonsync::SyncReplicaEvidenceState::Active;
    receipt.receiver_state_generation = 3U;
    receipt.receiver_cutpoint_digest =
        anonsync::sha256_hex("receiver-evidence-cutpoint");
    return receipt;
}

anonsync::SyncReplicaFileDeliveryReceipt published_receipt_fixture(
    const anonsync::SyncReplicaFileDeliveryRequest& request) {
    anonsync::SyncReplicaFileDeliveryReceipt receipt;
    receipt.folder_id = request.evidence_request.folder_id;
    receipt.sender_actor = request.evidence_request.sender_actor;
    receipt.receiver_actor = request.evidence_request.receiver_actor;
    receipt.operation_id = request.evidence_request.operation.operation_id;
    receipt.claim_id = request.evidence_request.claim_id;
    receipt.dispatch_attempts = request.evidence_request.dispatch_attempts;
    receipt.request_digest =
        anonsync::sync_replica_file_delivery_request_digest_or_throw(
            request, limits());
    receipt.channel_binding = request.evidence_request.channel_binding;
    receipt.disposition =
        anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published;
    receipt.evidence_receipt =
        evidence_receipt_fixture(request.evidence_request);
    receipt.effect_id =
        anonsync::make_sync_replica_file_effect_id_or_throw(
            request.evidence_request.operation);
    receipt.receiver_effect_generation = 7U;
    receipt.receiver_effect_cutpoint_digest =
        anonsync::sha256_hex("receiver-effect-cutpoint");
    return receipt;
}

void test_request_roundtrip_and_payload_authority() {
    const Fixture fixture = request_fixture();
    const std::string frame =
        anonsync::encode_sync_replica_file_delivery_request_or_throw(
            fixture.request, limits());
    constexpr std::string_view request_magic =
        "ANONSYNC-REPLICA-FILE-DELIVERY-REQUEST";
    require(frame.size() > request_magic.size() + 3U &&
                static_cast<unsigned char>(
                    frame[request_magic.size() + 3U]) ==
                    anonsync::kSyncReplicaFileDeliveryProtocolVersion &&
                anonsync::kSyncReplicaFileDeliveryProtocolVersion == 2U,
            "file request did not advertise explicit protocol v2");
    std::string legacy_version(frame);
    legacy_version[request_magic.size() + 3U] = 1;
    require_error(
        [&] {
            (void)anonsync::decode_sync_replica_file_delivery_request_or_throw(
                legacy_version, limits());
        },
        "protocol version is unsupported",
        "file-delivery v1 frame was accepted after typed v2 receipt expansion");
    const auto decoded =
        anonsync::decode_sync_replica_file_delivery_request_or_throw(
            frame, limits());
    require(decoded == fixture.request,
            "file request did not round-trip exact binary payload bytes");
    require(
        anonsync::encode_sync_replica_file_delivery_request_or_throw(
            decoded, limits()) == frame,
        "file request canonical re-encoding changed bytes");
    require(
        anonsync::sync_replica_file_delivery_request_digest_or_throw(
            decoded, limits()) == frame.substr(frame.size() - 64U),
        "file request digest did not equal its frame seal");
    require_adversarial_frame_rejected(
        frame,
        [](std::string_view candidate) {
            (void)anonsync::decode_sync_replica_file_delivery_request_or_throw(
                candidate, limits());
        },
        "file request decoder");

    auto wrong_bytes = fixture.request;
    wrong_bytes.payload[0] ^= 0x01;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_request_or_throw(
                wrong_bytes, limits());
        },
        "digest does not match",
        "payload bytes not owned by the operation digest were accepted");

    auto wrong_size = fixture.request;
    wrong_size.payload.push_back('x');
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_request_or_throw(
                wrong_size, limits());
        },
        "size does not match",
        "payload bytes not owned by the operation size were accepted");

    auto tombstone = fixture.request;
    anonsync::SyncReplicaModel model(
        tombstone.evidence_request.folder_id,
        tombstone.evidence_request.sender_actor,
        limits().evidence.model);
    tombstone.evidence_request.operation =
        model.create_local_tombstone_or_throw("nested/deleted.bin");
    tombstone.payload.clear();
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_request_or_throw(
                tombstone, limits());
        },
        "requires a file operation",
        "file-only protocol accepted a tombstone effect");
}

void test_receipt_roundtrip_terminality_and_cross_binding() {
    const Fixture fixture = request_fixture();
    const auto receipt = published_receipt_fixture(fixture.request);
    const std::string frame =
        anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
            receipt, limits());
    const auto decoded =
        anonsync::decode_sync_replica_file_delivery_receipt_or_throw(
            frame, limits());
    require(decoded == receipt,
            "file receipt did not round-trip exact effect authority");
    require(
        anonsync::sync_replica_file_delivery_receipt_digest_or_throw(
            decoded, limits()) == frame.substr(frame.size() - 64U),
        "file receipt digest did not equal its frame seal");
    anonsync::validate_sync_replica_file_delivery_receipt_for_request_or_throw(
        decoded, fixture.request, limits());
    ++checks;
    require_adversarial_frame_rejected(
        frame,
        [](std::string_view candidate) {
            (void)anonsync::decode_sync_replica_file_delivery_receipt_or_throw(
                candidate, limits());
        },
        "file receipt decoder");

    require(
        anonsync::sync_replica_file_delivery_receipt_is_effect_terminal(
            anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published) &&
        anonsync::sync_replica_file_delivery_receipt_is_effect_terminal(
            anonsync::SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished) &&
        !anonsync::sync_replica_file_delivery_receipt_is_effect_terminal(
            anonsync::SyncReplicaFileDeliveryReceiptDisposition::EvidencePending) &&
        !anonsync::sync_replica_file_delivery_receipt_is_effect_terminal(
            anonsync::SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict) &&
        !anonsync::sync_replica_file_delivery_receipt_is_effect_terminal(
            anonsync::SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked),
        "effect-terminal classifier did not preserve sender intent boundaries");

    auto wrong_effect = receipt;
    wrong_effect.effect_id = anonsync::sha256_hex("different-effect");
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_delivery_receipt_for_request_or_throw(
                wrong_effect, fixture.request, limits());
        },
        "effect id does not bind",
        "receipt replayed a different effect identity");

    auto wrong_request = fixture.request;
    wrong_request.evidence_request.claim_id =
        anonsync::sha256_hex("different-claim");
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_delivery_receipt_for_request_or_throw(
                receipt, wrong_request, limits());
        },
        "exact request attempt",
        "receipt replayed across a different dispatch claim");

    auto false_terminal = receipt;
    false_terminal.disposition =
        anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published;
    false_terminal.evidence_receipt->evidence_state =
        anonsync::SyncReplicaEvidenceState::PendingMissingDependency;
    false_terminal.evidence_receipt->disposition =
        anonsync::SyncReplicaDeliveryReceiptDisposition::InsertedPending;
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
                false_terminal, limits());
        },
        "requires active evidence authority",
        "terminal file receipt was minted from pending evidence");
}

void test_pre_effect_receipts_have_no_laundered_authority() {
    const Fixture fixture = request_fixture();
    anonsync::SyncReplicaFileDeliveryReceipt receipt;
    receipt.folder_id = fixture.request.evidence_request.folder_id;
    receipt.sender_actor = fixture.request.evidence_request.sender_actor;
    receipt.receiver_actor = fixture.request.evidence_request.receiver_actor;
    receipt.operation_id =
        fixture.request.evidence_request.operation.operation_id;
    receipt.claim_id = fixture.request.evidence_request.claim_id;
    receipt.dispatch_attempts =
        fixture.request.evidence_request.dispatch_attempts;
    receipt.request_digest =
        anonsync::sync_replica_file_delivery_request_digest_or_throw(
            fixture.request, limits());
    receipt.channel_binding =
        fixture.request.evidence_request.channel_binding;
    receipt.disposition =
        anonsync::SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked;
    receipt.receiver_effect_generation = 0U;
    receipt.receiver_effect_cutpoint_digest =
        anonsync::sha256_hex("unchanged-effect-cutpoint");

    const std::string frame =
        anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
            receipt, limits());
    const auto decoded =
        anonsync::decode_sync_replica_file_delivery_receipt_or_throw(
            frame, limits());
    require(decoded == receipt && !decoded.evidence_receipt.has_value() &&
                decoded.effect_id.empty(),
            "effect-capacity receipt claimed staged evidence authority");
    anonsync::validate_sync_replica_file_delivery_receipt_for_request_or_throw(
        decoded, fixture.request, limits());
    ++checks;
    require(
        anonsync::sync_replica_file_delivery_receipt_precedes_effect_authority(
            decoded.disposition) &&
            !anonsync::sync_replica_file_delivery_receipt_precedes_effect_authority(
                anonsync::SyncReplicaFileDeliveryReceiptDisposition::Published),
        "pre-effect classifier did not isolate authority-free denials");

    auto path_blocked = receipt;
    path_blocked.disposition =
        anonsync::SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked;
    path_blocked.receiver_effect_cutpoint_digest =
        anonsync::sha256_hex("path-blocked-unchanged-effect-cutpoint");
    const std::string path_frame =
        anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
            path_blocked, limits());
    const auto path_decoded =
        anonsync::decode_sync_replica_file_delivery_receipt_or_throw(
            path_frame, limits());
    require(path_decoded == path_blocked &&
                !path_decoded.evidence_receipt.has_value() &&
                path_decoded.effect_id.empty() &&
                anonsync::sync_replica_file_delivery_receipt_precedes_effect_authority(
                    path_decoded.disposition),
            "path-policy receipt claimed effect or evidence authority");
    anonsync::validate_sync_replica_file_delivery_receipt_for_request_or_throw(
        path_decoded, fixture.request, limits());
    ++checks;

    auto laundered = receipt;
    laundered.effect_id = anonsync::sha256_hex("invented-effect");
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
                laundered, limits());
        },
        "must not claim",
        "effect-capacity receipt laundered an effect identity");

    auto invented_evidence = receipt;
    invented_evidence.evidence_receipt =
        evidence_receipt_fixture(fixture.request.evidence_request);
    require_error(
        [&] {
            (void)anonsync::encode_sync_replica_file_delivery_receipt_or_throw(
                invented_evidence, limits());
        },
        "must not claim",
        "effect-capacity receipt laundered evidence admission");
}

void test_limits_are_joint_not_independent() {
    auto invalid = limits();
    invalid.max_request_frame_bytes =
        invalid.evidence.max_request_frame_bytes +
        invalid.max_payload_bytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_delivery_protocol_limits_or_throw(
                invalid);
        },
        "cannot hold every permitted payload",
        "outer request limit ignored embedded evidence and framing overhead");

    invalid = limits();
    invalid.max_receipt_frame_bytes =
        invalid.evidence.max_receipt_frame_bytes;
    require_error(
        [&] {
            anonsync::validate_sync_replica_file_delivery_protocol_limits_or_throw(
                invalid);
        },
        "cannot hold every canonical receipt",
        "outer receipt limit ignored embedded receipt and effect authority");
}

}  // namespace

int main() {
    try {
        test_request_roundtrip_and_payload_authority();
        test_receipt_roundtrip_terminality_and_cross_binding();
        test_pre_effect_receipts_have_no_laundered_authority();
        test_limits_are_joint_not_independent();
        std::cout << "sync replica file-delivery protocol tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica file-delivery protocol tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
