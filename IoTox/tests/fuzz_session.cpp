#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/session.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *data, std::size_t size) {
    const std::span<const std::uint8_t> input(data, size);
    static_cast<void>(iotox::protocol::decode_hello_payload(input));
    static_cast<void>(iotox::protocol::decode_confirmation_payload(input));
    auto frame = iotox::protocol::decode(input);
    if (frame && frame.value().type == iotox::protocol::MessageType::hello) {
        static_cast<void>(iotox::protocol::validate_hello_frame(frame.value()));
    }
    if (frame &&
        frame.value().type == iotox::protocol::MessageType::capabilities) {
        static_cast<void>(
            iotox::protocol::validate_confirmation_frame(frame.value()));
    }
    return 0;
}
