#pragma once

#include "iotox/status.hpp"
#include "iotox/toxcore/abi.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace iotox::toxcore {

struct LibraryVersion {
    std::uint32_t major{0};
    std::uint32_t minor{0};
    std::uint32_t patch{0};

    [[nodiscard]] std::string str() const;
};

class DynamicToxcore {
  public:
    DynamicToxcore() = default;
    ~DynamicToxcore();

    DynamicToxcore(const DynamicToxcore &) = delete;
    DynamicToxcore &operator=(const DynamicToxcore &) = delete;
    DynamicToxcore(DynamicToxcore &&other) noexcept;
    DynamicToxcore &operator=(DynamicToxcore &&other) noexcept;

    [[nodiscard]] static Result<DynamicToxcore> load(const std::filesystem::path &explicit_path = {});

    [[nodiscard]] const abi::Api &api() const noexcept { return api_; }
    [[nodiscard]] LibraryVersion version() const;
    [[nodiscard]] const std::string &loaded_path() const noexcept { return loaded_path_; }

  private:
    void *handle_{nullptr};
    abi::Api api_{};
    std::string loaded_path_;
};

}  // namespace iotox::toxcore
