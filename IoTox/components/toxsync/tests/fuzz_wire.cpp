#include "toxsync/wire.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace {

template <typename Value, typename Decoder, typename Encoder>
void round_trip(std::span<const std::byte> input, Decoder decoder,
                Encoder encoder) noexcept {
  try {
    const Value decoded = decoder(input);
    const auto encoded = encoder(decoded);
    if (encoded.size() != input.size() ||
        !std::equal(encoded.begin(), encoded.end(), input.begin())) {
      __builtin_trap();
    }
  } catch (...) {
  }
}

template <std::size_t Size>
std::array<std::byte, Size>
mutate_canonical(std::array<std::byte, Size> canonical,
                 std::span<const std::byte> input) noexcept {
  if (Size <= 4U || input.empty())
    return canonical;
  for (std::size_t index = 4U; index < Size; ++index) {
    canonical[index] ^= input[(index - 4U) % input.size()];
  }
  return canonical;
}

void exercise(std::span<const std::byte> input) noexcept {
  round_trip<toxsync::MutableHead>(
      input, toxsync::decode_mutable_head,
      [](const auto &value) { return toxsync::encode_mutable_head(value); });
  round_trip<toxsync::HeadSummary>(
      input, toxsync::decode_head_summary,
      [](const auto &value) { return toxsync::encode_head_summary(value); });
  round_trip<toxsync::HeadQuery>(
      input, toxsync::decode_head_query,
      [](const auto &value) { return toxsync::encode_head_query(value); });
  round_trip<toxsync::HeadReceipt>(
      input, toxsync::decode_head_receipt,
      [](const auto &value) { return toxsync::encode_head_receipt(value); });
  round_trip<toxsync::RangeRequest>(
      input, [](auto bytes) { return toxsync::decode_range_request(bytes); },
      [](const auto &value) { return toxsync::encode_range_request(value); });
  round_trip<toxsync::RangeOffer>(
      input, [](auto bytes) { return toxsync::decode_range_offer(bytes); },
      [](const auto &value) { return toxsync::encode_range_offer(value); });
  round_trip<toxsync::RangeCancel>(
      input, toxsync::decode_range_cancel,
      [](const auto &value) { return toxsync::encode_range_cancel(value); });
  round_trip<toxsync::RangeResult>(
      input, toxsync::decode_range_result,
      [](const auto &value) { return toxsync::encode_range_result(value); });
  round_trip<toxsync::InventoryRequest>(
      input, toxsync::decode_inventory_request, [](const auto &value) {
        return toxsync::encode_inventory_request(value);
      });
  round_trip<toxsync::InventoryPage>(
      input, toxsync::decode_inventory_page,
      [](const auto &value) { return toxsync::encode_inventory_page(value); });
  round_trip<toxsync::RangeCapabilities>(
      input, toxsync::decode_range_capabilities, [](const auto &value) {
        return toxsync::encode_range_capabilities(value);
      });
}

} // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data,
                                      std::size_t size) {
  const auto input = std::span<const std::byte>{
      reinterpret_cast<const std::byte *>(data), size};
  exercise(input);

  toxsync::MutableHead head;
  head.namespace_id.bytes[0] = std::byte{1U};
  head.artifact.bytes[0] = std::byte{2U};
  head.index.bytes[0] = std::byte{3U};
  head.index_size = 64U;
  head.block_size = 4096U;
  const auto mutated_head =
      mutate_canonical(toxsync::encode_mutable_head(head), input);
  exercise(mutated_head);

  toxsync::HeadSummary summary;
  summary.namespace_id.bytes[0] = std::byte{1U};
  const auto mutated_summary =
      mutate_canonical(toxsync::encode_head_summary(summary), input);
  exercise(mutated_summary);

  toxsync::RangeRequest request;
  request.request_id = 1U;
  request.artifact.bytes[0] = std::byte{1U};
  request.length = 1U;
  const auto mutated_request =
      mutate_canonical(toxsync::encode_range_request(request), input);
  exercise(mutated_request);

  toxsync::RangeOffer offer;
  offer.request_id = 1U;
  offer.artifact.bytes[0] = std::byte{1U};
  offer.length = 1U;
  offer.file_id[0] = std::byte{1U};
  const auto mutated_offer =
      mutate_canonical(toxsync::encode_range_offer(offer), input);
  exercise(mutated_offer);

  toxsync::InventoryRequest inventory_request;
  inventory_request.request_id = 1U;
  inventory_request.manifest.bytes[0] = std::byte{1U};
  inventory_request.chunk_count = 1U;
  const auto mutated_inventory_request = mutate_canonical(
      toxsync::encode_inventory_request(inventory_request), input);
  exercise(mutated_inventory_request);

  toxsync::InventoryPage page;
  page.request_id = 1U;
  page.manifest.bytes[0] = std::byte{1U};
  page.bit_count = 1U;
  const auto mutated_page =
      mutate_canonical(toxsync::encode_inventory_page(page), input);
  exercise(mutated_page);

  return 0;
}
