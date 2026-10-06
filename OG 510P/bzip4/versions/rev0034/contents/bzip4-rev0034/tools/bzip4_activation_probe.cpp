#include "bzip4/activation.hpp"

#include <charconv>
#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string_view>

namespace {

[[nodiscard]] std::size_t number(std::string_view value, std::string_view field) {
    std::size_t output = 0;
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), output);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        throw std::invalid_argument(std::string(field) + " is not an unsigned integer");
    }
    return output;
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 9) {
        std::cerr << "usage: bzip4_activation_probe BLOCKS BYTES RETAINED MIN_BLOCKS MIN_BYTES MAX_ACTIVE CALLER(0|1) WAKE(active|all)\n";
        return 64;
    }
    try {
        bzip4::ActivationPolicy policy;
        const std::size_t blocks = number(argv[1], "blocks");
        const std::size_t bytes = number(argv[2], "bytes");
        policy.retained_background_workers = number(argv[3], "retained workers");
        policy.minimum_blocks_per_active_lane = number(argv[4], "minimum blocks");
        policy.minimum_bytes_per_active_lane = number(argv[5], "minimum bytes");
        policy.max_active_lanes = number(argv[6], "maximum active lanes");
        const std::size_t caller = number(argv[7], "caller flag");
        if (caller > 1) throw std::invalid_argument("caller flag must be 0 or 1");
        policy.caller_participates = caller == 1;
        const std::string_view wake = argv[8];
        if (wake == "active") policy.wake_mode = bzip4::WakeMode::active_only;
        else if (wake == "all") policy.wake_mode = bzip4::WakeMode::all_retained;
        else throw std::invalid_argument("wake mode must be active or all");

        const bzip4::ActivationPlan plan = bzip4::make_activation_plan(blocks, bytes, policy);
        std::cout << "{\"schema\":\"bzip4.activation-plan.v1\",\"active_lanes\":" << plan.active_lanes
                  << ",\"active_background_workers\":" << plan.active_background_workers
                  << ",\"workers_notified\":" << plan.workers_notified
                  << ",\"blocks\":" << plan.blocks
                  << ",\"logical_bytes\":" << plan.logical_bytes
                  << ",\"caller_participates\":" << (plan.caller_participates ? "true" : "false")
                  << "}\n";
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "error: " << exception.what() << '\n';
        return 1;
    }
}
