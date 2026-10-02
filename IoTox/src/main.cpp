#include "iotox/cli.hpp"
#include "iotox/terminal_posix.hpp"
#include "iotox/update_service.hpp"

#include <cstddef>
#include <span>
#include <string_view>
#include <vector>

int main(int argc, char **argv) {
    if (argc == 2 &&
        std::string_view{argv[1]} ==
            iotox::update::kInternalUpdateServiceChildArgument) {
        return iotox::update::run_internal_update_service_child();
    }
    if (argc == 2 &&
        std::string_view{argv[1]} ==
            iotox::terminal::kInternalTerminalChildArgument) {
        return iotox::terminal::run_internal_terminal_child();
    }

    std::vector<std::string_view> arguments;
    arguments.reserve(static_cast<std::size_t>(argc > 1 ? argc - 1 : 0));
    for (int index = 1; index < argc; ++index) {
        arguments.emplace_back(argv[index]);
    }
    return iotox::run_cli(arguments);
}
