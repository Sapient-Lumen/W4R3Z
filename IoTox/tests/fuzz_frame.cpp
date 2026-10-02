#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/session.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    auto frame = iotox::protocol::decode(
        std::span<const std::uint8_t>(data, size));
    if (frame && frame.value().type == iotox::protocol::MessageType::hello) {
        static_cast<void>(
            iotox::protocol::decode_hello_payload(frame.value().payload));
        static_cast<void>(iotox::protocol::validate_hello_frame(frame.value()));
    }
    if (frame &&
        frame.value().type == iotox::protocol::MessageType::capabilities) {
        static_cast<void>(
            iotox::protocol::decode_confirmation_payload(frame.value().payload));
        static_cast<void>(
            iotox::protocol::validate_confirmation_frame(frame.value()));
    }
    return 0;
}
