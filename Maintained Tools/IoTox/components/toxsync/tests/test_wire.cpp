#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/hash.hpp"
#include "toxsync/wire.hpp"

TOXSYNC_TEST(range_request_round_trip) {
    toxsync::RangeRequest request;
    request.request_id = 0x1122334455667788ULL;
    request.artifact = toxsync::sha256(test::pattern(100U, 5U));
    request.offset = 0x0102030405060708ULL;
    request.length = 65536U;
    request.flags = toxsync::kKnownRangeRequestFlags;
    REQUIRE(toxsync::decode_range_request(toxsync::encode_range_request(request)) == request);
}

TOXSYNC_TEST(range_request_rejects_bad_magic_reserved_and_policy) {
    toxsync::RangeRequest request;
    request.request_id = 1U;
    request.artifact = toxsync::sha256(test::pattern(10U, 6U));
    request.length = 1024U;
    auto bytes = toxsync::encode_range_request(request);
    bytes[0] ^= std::byte{1};
    REQUIRE_THROWS(toxsync::decode_range_request(bytes));

    bytes = toxsync::encode_range_request(request);
    bytes.back() = std::byte{1};
    REQUIRE_THROWS(toxsync::decode_range_request(bytes));

    bytes = toxsync::encode_range_request(request);
    REQUIRE_THROWS(toxsync::decode_range_request(bytes, 100U));

    request.request_id = 0U;
    REQUIRE_THROWS(toxsync::encode_range_request(request));

    request.request_id = 1U;
    bytes = toxsync::encode_range_request(request);
    bytes[6U] = std::byte{0x80};
    REQUIRE_THROWS(toxsync::decode_range_request(bytes));
}

TOXSYNC_TEST(mutable_head_round_trip_preserves_canonical_signing_body) {
    toxsync::MutableHead head;
    head.engine = toxsync::Engine::range_v1;
    head.flags = toxsync::kHeadFlagTreepack | toxsync::kHeadFlagSnapshot;
    head.generation = 77U;
    head.namespace_id = toxsync::sha256(test::pattern(41U, 0x8101U));
    head.artifact = toxsync::sha256(test::pattern(42U, 0x8102U));
    head.index = toxsync::sha256(test::pattern(43U, 0x8103U));
    head.parent = toxsync::sha256(test::pattern(44U, 0x8104U));
    head.artifact_size = 9U * 1024U * 1024U;
    head.index_size = 12345U;
    head.block_size = 4096U;
    for (std::size_t i = 0; i < head.signature.size(); ++i) {
        head.signature[i] = static_cast<std::byte>(i);
    }

    const auto signing = toxsync::encode_mutable_head_signing(head);
    const auto encoded = toxsync::encode_mutable_head(head);
    REQUIRE(signing.size() == toxsync::kMutableHeadSigningBytes);
    REQUIRE(encoded.size() == toxsync::kMutableHeadBytes);
    REQUIRE(std::equal(signing.begin(), signing.end(), encoded.begin()));
    REQUIRE(toxsync::decode_mutable_head(encoded) == head);
}

TOXSYNC_TEST(mutable_head_rejects_reserved_bits_and_engine_mismatch) {
    toxsync::MutableHead head;
    head.namespace_id = toxsync::sha256(test::pattern(10U, 0x8201U));
    head.artifact = toxsync::sha256(test::pattern(11U, 0x8202U));
    head.index = toxsync::sha256(test::pattern(12U, 0x8203U));
    head.index_size = 64U;
    head.block_size = 4096U;
    auto bytes = toxsync::encode_mutable_head(head);
    bytes[toxsync::kMutableHeadSigningBytes - 1U] = std::byte{1};
    REQUIRE_THROWS(toxsync::decode_mutable_head(bytes));

    head.engine = toxsync::Engine::content_store_v2;
    REQUIRE_THROWS(toxsync::encode_mutable_head(head));

    head.block_size = 0U;
    REQUIRE(toxsync::decode_mutable_head(
                toxsync::encode_mutable_head(head)) == head);
}

TOXSYNC_TEST(head_anti_entropy_messages_round_trip_and_reject_incomplete_identity) {
    const auto namespace_id = toxsync::sha256(test::pattern(73U, 0x8251U));
    const auto record = toxsync::sha256(test::pattern(79U, 0x8252U));

    toxsync::HeadSummary summary;
    summary.flags = toxsync::kHeadSummaryFlagHasHead;
    summary.generation = 42U;
    summary.namespace_id = namespace_id;
    summary.record = record;
    REQUIRE(toxsync::decode_head_summary(
                toxsync::encode_head_summary(summary)) == summary);

    toxsync::HeadQuery query;
    query.flags = toxsync::kHeadQueryFlagHasHead;
    query.generation = summary.generation;
    query.namespace_id = namespace_id;
    query.record = record;
    REQUIRE(toxsync::decode_head_query(
                toxsync::encode_head_query(query)) == query);

    toxsync::HeadReceipt receipt;
    receipt.status = toxsync::HeadReceiptStatus::accepted;
    receipt.generation = summary.generation;
    receipt.namespace_id = namespace_id;
    receipt.record = record;
    REQUIRE(toxsync::decode_head_receipt(
                toxsync::encode_head_receipt(receipt)) == receipt);

    summary.flags = 0U;
    summary.generation = 0U;
    summary.record = {};
    REQUIRE(toxsync::decode_head_summary(
                toxsync::encode_head_summary(summary)) == summary);

    summary.generation = 1U;
    REQUIRE_THROWS(toxsync::encode_head_summary(summary));
    summary.generation = 0U;
    summary.namespace_id = {};
    REQUIRE_THROWS(toxsync::encode_head_summary(summary));

    query.namespace_id = namespace_id;
    query.flags = 0U;
    query.generation = 1U;
    query.record = {};
    REQUIRE_THROWS(toxsync::encode_head_query(query));

    receipt.namespace_id = namespace_id;
    receipt.generation = 1U;
    receipt.record = {};
    REQUIRE_THROWS(toxsync::encode_head_receipt(receipt));
    receipt.generation = 0U;
    receipt.flags = 1U;
    REQUIRE_THROWS(toxsync::encode_head_receipt(receipt));
}

TOXSYNC_TEST(range_offer_cancel_and_result_round_trip) {
    toxsync::RangeOffer offer;
    offer.status = toxsync::RangeOfferStatus::accepted;
    offer.request_id = 99U;
    offer.artifact = toxsync::sha256(test::pattern(19U, 0x8301U));
    offer.offset = 4096U;
    offer.length = 65536U;
    offer.retry_after_ms = 0U;
    const auto file_id = toxsync::sha256(test::pattern(23U, 0x8302U));
    offer.file_id = file_id.bytes;
    REQUIRE(toxsync::decode_range_offer(toxsync::encode_range_offer(offer)) == offer);

    toxsync::RangeCancel cancel;
    cancel.reason = toxsync::RangeCancelReason::superseded;
    cancel.flags = 3U;
    cancel.request_id = offer.request_id;
    REQUIRE(toxsync::decode_range_cancel(toxsync::encode_range_cancel(cancel)) == cancel);

    toxsync::RangeResult result;
    result.status = toxsync::RangeResultStatus::completed;
    result.flags = 7U;
    result.request_id = offer.request_id;
    result.bytes_received = offer.length;
    result.range_digest = toxsync::sha256(test::pattern(offer.length, 0x8303U));
    REQUIRE(toxsync::decode_range_result(toxsync::encode_range_result(result)) == result);
}

TOXSYNC_TEST(rejected_range_offer_carries_retry_without_transfer_identity) {
    toxsync::RangeOffer offer;
    offer.status = toxsync::RangeOfferStatus::busy;
    offer.request_id = 100U;
    offer.retry_after_ms = 250U;
    REQUIRE(toxsync::decode_range_offer(toxsync::encode_range_offer(offer)) == offer);
    offer.length = 1U;
    REQUIRE_THROWS(toxsync::encode_range_offer(offer));
}

TOXSYNC_TEST(range_capabilities_round_trip_without_arbitrary_lane_ceiling) {
    toxsync::RangeCapabilities capabilities;
    capabilities.flags = toxsync::kCapabilityRangeV1 |
                         toxsync::kCapabilityContentStoreV2Preview;
    capabilities.max_range_length = 4U * 1024U * 1024U;
    capabilities.max_lanes = 4U;
    capabilities.max_inflight = 16U;
    capabilities.max_engine = toxsync::Engine::content_store_v2;
    capabilities.max_index_format = 1U;
    capabilities.workspace_budget_bytes = 16U * 1024U * 1024U;
    REQUIRE(toxsync::decode_range_capabilities(
                toxsync::encode_range_capabilities(capabilities)) == capabilities);

    capabilities.max_lanes = 4096U;
    capabilities.max_inflight = 512U;
    REQUIRE(toxsync::decode_range_capabilities(
                toxsync::encode_range_capabilities(capabilities)) == capabilities);

    capabilities.max_lanes = 4U;
    capabilities.max_inflight = 16U;
    capabilities.workspace_budget_bytes = 0U;
    REQUIRE_THROWS(toxsync::encode_range_capabilities(capabilities));

    capabilities.workspace_budget_bytes = 1U;
    capabilities.flags = toxsync::kCapabilityRangeV1;
    capabilities.max_engine = toxsync::Engine::content_store_v2;
    REQUIRE_THROWS(toxsync::encode_range_capabilities(capabilities));
}

TOXSYNC_TEST(inventory_request_and_page_round_trip_validate_exact_bits) {
    toxsync::InventoryRequest request;
    request.request_id = 0xabcdefU;
    request.manifest = toxsync::sha256(test::pattern(177U, 0x9101U));
    request.first_chunk = 4096U;
    request.chunk_count = 37U;
    request.flags = toxsync::kInventoryRequestFlagVerifyObjects |
                    toxsync::kInventoryRequestFlagManifestPages;
    REQUIRE(toxsync::decode_inventory_request(
                toxsync::encode_inventory_request(request)) == request);

    toxsync::InventoryPage page;
    page.status = toxsync::InventoryStatus::available;
    page.request_id = request.request_id;
    page.manifest = request.manifest;
    page.first_chunk = request.first_chunk;
    page.flags = request.flags;
    page.bit_count = request.chunk_count;
    page.retry_after_ms = 0U;
    page.flags = request.flags;
    toxsync::set_inventory_bit(page, 0U, true);
    toxsync::set_inventory_bit(page, 3U, true);
    toxsync::set_inventory_bit(page, 36U, true);
    page.available_count = 3U;
    const auto decoded = toxsync::decode_inventory_page(
        toxsync::encode_inventory_page(page));
    REQUIRE(decoded == page);
    REQUIRE(toxsync::inventory_bit(decoded, 0U));
    REQUIRE(toxsync::inventory_bit(decoded, 3U));
    REQUIRE(toxsync::inventory_bit(decoded, 36U));
    REQUIRE(!toxsync::inventory_bit(decoded, 35U));
    REQUIRE(!toxsync::inventory_bit(decoded, 37U));

    auto corrupt = toxsync::encode_inventory_page(page);
    corrupt.back() = std::byte{1U};
    REQUIRE_THROWS(toxsync::decode_inventory_page(corrupt));

    page.available_count = 2U;
    REQUIRE_THROWS(toxsync::encode_inventory_page(page));

    page.available_count = 3U;
    page.flags = 0x8000U;
    REQUIRE_THROWS(toxsync::encode_inventory_page(page));
}

TOXSYNC_TEST(inventory_error_page_is_bounded_and_carries_retry_only) {
    toxsync::InventoryPage page;
    page.status = toxsync::InventoryStatus::busy;
    page.request_id = 22U;
    page.manifest = toxsync::sha256(test::pattern(73U, 0x9102U));
    page.retry_after_ms = 500U;
    REQUIRE(toxsync::decode_inventory_page(
                toxsync::encode_inventory_page(page)) == page);

    page.bit_count = 1U;
    REQUIRE_THROWS(toxsync::encode_inventory_page(page));
}
