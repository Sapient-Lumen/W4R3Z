#include "toxsync/content_availability.hpp"
#include "toxsync/index.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace {

void exercise_index(std::span<const std::byte> input) noexcept {
  try {
    toxsync::IndexLimits limits;
    limits.max_target_size = 64U * 1024U * 1024U;
    limits.max_blocks = 65536U;
    const auto decoded = toxsync::Index::decode(input, limits);
    const auto encoded = decoded.encode();
    if (encoded.size() != input.size() ||
        !std::equal(encoded.begin(), encoded.end(), input.begin())) {
      __builtin_trap();
    }
  } catch (...) {
  }
}

void exercise_availability(std::span<const std::byte> input) noexcept {
  try {
    const auto decoded =
        toxsync::decode_content_availability(input, 64U * 1024U);
    const auto encoded = toxsync::encode_content_availability(decoded);
    if (encoded.size() != input.size() ||
        !std::equal(encoded.begin(), encoded.end(), input.begin())) {
      __builtin_trap();
    }
  } catch (...) {
  }
}

void mutate_after_magic(std::vector<std::byte> &canonical,
                        std::span<const std::byte> input) noexcept {
  if (input.empty())
    return;
  for (std::size_t index = 8U; index < canonical.size(); ++index) {
    canonical[index] ^= input[(index - 8U) % input.size()];
  }
}

} // namespace

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data,
                                      std::size_t size) {
  const auto input = std::span<const std::byte>{
      reinterpret_cast<const std::byte *>(data), size};
  exercise_index(input);
  exercise_availability(input);

  toxsync::Index index;
  index.target_size = 1U;
  index.blocks.push_back(toxsync::BlockRecord{1U, 1U, {}});
  auto canonical_index = index.encode();
  mutate_after_magic(canonical_index, input);
  exercise_index(canonical_index);

  toxsync::ContentAvailabilityConfig config;
  config.filter_bytes = 64U;
  toxsync::ContentAvailabilitySketch sketch(config);
  toxsync::Digest256 manifest;
  manifest.bytes[0] = std::byte{1U};
  sketch.reset(manifest);
  auto canonical_availability = toxsync::encode_content_availability(sketch);
  mutate_after_magic(canonical_availability, input);
  exercise_availability(canonical_availability);
  return 0;
}
