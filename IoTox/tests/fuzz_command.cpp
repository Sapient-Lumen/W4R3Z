#include "iotox/protocol/command.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    const std::span<const std::uint8_t> bytes{data, size};
    static_cast<void>(iotox::protocol::decode_command_request(bytes));
    static_cast<void>(iotox::protocol::decode_command_receipt(bytes));
    auto result = iotox::protocol::decode_command_result(bytes);
    static_cast<void>(iotox::protocol::decode_device_description(bytes));
    static_cast<void>(iotox::protocol::decode_system_summary(bytes));
    static_cast<void>(iotox::protocol::decode_profile_status_evidence(bytes));
    static_cast<void>(iotox::protocol::decode_update_stage_evidence(bytes));
    if (result &&
        result.value().operation ==
            iotox::protocol::CommandOperation::device_describe &&
        result.value().outcome ==
            iotox::protocol::CommandOutcome::succeeded) {
        static_cast<void>(iotox::protocol::decode_device_description(
            result.value().body));
    }
    if (result &&
        result.value().operation ==
            iotox::protocol::CommandOperation::profile_status_set &&
        result.value().outcome ==
            iotox::protocol::CommandOutcome::succeeded) {
        static_cast<void>(iotox::protocol::decode_profile_status_evidence(
            result.value().body));
    }
    if (result &&
        result.value().operation ==
            iotox::protocol::CommandOperation::system_summary &&
        result.value().outcome ==
            iotox::protocol::CommandOutcome::succeeded) {
        static_cast<void>(iotox::protocol::decode_system_summary(
            result.value().body));
    }
    if (result &&
        result.value().operation ==
            iotox::protocol::CommandOperation::update_stage &&
        result.value().outcome ==
            iotox::protocol::CommandOutcome::succeeded) {
        static_cast<void>(iotox::protocol::decode_update_stage_evidence(
            result.value().body));
    }
    return 0;
}
