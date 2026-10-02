#include "iotox/update_bundle.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
  const std::span<const std::uint8_t> input(data, size);

  const auto manifest =
      iotox::update::decode_signed_update_manifest(input);
  if (manifest.ok()) {
    const auto encoded =
        iotox::update::encode_signed_update_manifest(manifest.value());
    if (!encoded.ok() || encoded.value().size() != input.size() ||
        !std::equal(encoded.value().begin(), encoded.value().end(),
                    input.begin())) {
      __builtin_trap();
    }
  }

  const auto policy = iotox::update::decode_update_policy(input);
  if (policy.ok()) {
    const auto encoded = iotox::update::encode_update_policy(policy.value());
    if (!encoded.ok() || encoded.value().size() != input.size() ||
        !std::equal(encoded.value().begin(), encoded.value().end(),
                    input.begin())) {
      __builtin_trap();
    }
  }
  return 0;
}
