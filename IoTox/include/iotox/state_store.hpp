#pragma once

#include "iotox/status.hpp"

#include <cstdint>
#include <filesystem>
#include <span>
#include <vector>

namespace iotox {

class StateStore {
  public:
    [[nodiscard]] static Result<std::vector<std::uint8_t>> read(const std::filesystem::path &path);
    [[nodiscard]] static Status write_atomic(
        const std::filesystem::path &path, std::span<const std::uint8_t> bytes);
};

}  // namespace iotox
