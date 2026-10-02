#pragma once

#include <span>
#include <string_view>

namespace iotox {

// Runs the complete IoTox product surface. The same executable is both the
// foreground device agent (`iotox run`) and its local controller.
int run_cli(std::span<const std::string_view> arguments);

}  // namespace iotox
