#include "test_harness.hpp"

#include "iotox/mutorr/head.hpp"
#include "iotox/protocol/frame.hpp"

#include <algorithm>
#include <cstdint>
#include <vector>

namespace {

iotox::mutorr::HeadRecord make_head(std::uint64_t generation) {
    iotox::mutorr::HeadRecord head;
    head.namespace_id = iotox::mutorr::synthetic_id(1U, 0x4E414D45U);
    head.writer_key = iotox::mutorr::synthetic_id(7U, 0x57524954U);
    head.generation = generation;
    head.root = iotox::mutorr::synthetic_id(generation, 0x524F4F54U);
    if (generation > 1U) {
        head.previous = iotox::mutorr::synthetic_id(generation - 1U, 0x524F4F54U);
    }
    head.created_unix_ms = 1000U + generation;
    head.content_bytes = 4096U * generation;
    head.object_count = static_cast<std::uint32_t>(generation * 3U);
    std::fill(head.signature.begin(), head.signature.end(), static_cast<std::uint8_t>(generation));
    return head;
}

}  // namespace

IOTOX_TEST("mutable head has fixed signing and wire encodings") {
    const auto original = make_head(2U);
    auto signing = iotox::mutorr::head_signing_bytes(original);
    IOTOX_CHECK(signing);
    IOTOX_CHECK(signing.value().size() == iotox::mutorr::kHeadSigningSize);

    auto encoded = iotox::mutorr::encode_head(original);
    IOTOX_CHECK(encoded);
    IOTOX_CHECK(encoded.value().size() == iotox::mutorr::kHeadWireSize);

    auto decoded = iotox::mutorr::decode_head(encoded.value());
    IOTOX_CHECK(decoded);
    IOTOX_CHECK(decoded.value() == original);
}

IOTOX_TEST("mutable head progression detects duplicates stale heads and forks") {
    const auto first = make_head(1U);
    const auto second = make_head(2U);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(nullptr, first) ==
                iotox::mutorr::HeadDecision::accept_initial);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(&first, first) ==
                iotox::mutorr::HeadDecision::duplicate);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(&first, second) ==
                iotox::mutorr::HeadDecision::accept_advance);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(&second, first) ==
                iotox::mutorr::HeadDecision::stale);

    auto conflict = first;
    conflict.root = iotox::mutorr::synthetic_id(999U, 0x524F4F54U);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(&first, conflict) ==
                iotox::mutorr::HeadDecision::conflict);

    auto gap = make_head(4U);
    IOTOX_CHECK(iotox::mutorr::evaluate_head(&second, gap) ==
                iotox::mutorr::HeadDecision::requires_history);
}

IOTOX_TEST("mutable head validation rejects broken linked revisions") {
    auto invalid = make_head(1U);
    invalid.previous = iotox::mutorr::synthetic_id(1U, 55U);
    IOTOX_CHECK(!iotox::mutorr::validate_head(invalid).ok());
    IOTOX_CHECK(!iotox::mutorr::encode_head(invalid));

    auto encoded = iotox::mutorr::encode_head(make_head(2U));
    IOTOX_CHECK(encoded);
    encoded.value().pop_back();
    IOTOX_CHECK(!iotox::mutorr::decode_head(encoded.value()));
}

IOTOX_TEST("mutable head fits inside the IoTox lossless control frame") {
    auto encoded_head = iotox::mutorr::encode_head(make_head(1U));
    IOTOX_CHECK(encoded_head);

    iotox::protocol::Frame frame;
    frame.type = iotox::protocol::MessageType::mutorr_head;
    frame.message_id = 17U;
    frame.sequence = 1U;
    frame.payload = encoded_head.value();

    auto packet = iotox::protocol::encode(frame);
    IOTOX_CHECK(packet);
    IOTOX_CHECK(packet.value().size() < iotox::protocol::kToxMaxCustomPacketSize);

    auto decoded_frame = iotox::protocol::decode(packet.value());
    IOTOX_CHECK(decoded_frame);
    auto decoded_head = iotox::mutorr::decode_head(decoded_frame.value().payload);
    IOTOX_CHECK(decoded_head);
    IOTOX_CHECK(decoded_head.value() == make_head(1U));
}
