#include "iotox/local/terminal_protocol.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(
    const std::uint8_t *data, std::size_t size) {
    const auto bytes = std::span<const std::uint8_t>{data, size};
    const auto decoded = iotox::local::decode_terminal_packet(bytes);
    if (!decoded) return 0;

    const auto encoded = iotox::local::encode_terminal_packet(decoded.value());
    if (!encoded) __builtin_trap();
    const auto round_trip =
        iotox::local::decode_terminal_packet(encoded.value());
    if (!round_trip || !(round_trip.value() == decoded.value())) {
        __builtin_trap();
    }

    switch (decoded.value().type) {
        case iotox::local::TerminalPacketType::open: {
            const auto payload =
                iotox::local::decode_terminal_open(decoded.value().payload);
            if (!payload) __builtin_trap();
            const auto reencoded = iotox::local::encode_terminal_open(payload.value());
            if (!reencoded || reencoded.value() != decoded.value().payload) {
                __builtin_trap();
            }
            break;
        }
        case iotox::local::TerminalPacketType::opened: {
            const auto payload =
                iotox::local::decode_terminal_opened(decoded.value().payload);
            if (!payload) __builtin_trap();
            const auto reencoded =
                iotox::local::encode_terminal_opened(payload.value());
            if (!reencoded || reencoded.value() != decoded.value().payload) {
                __builtin_trap();
            }
            break;
        }
        case iotox::local::TerminalPacketType::output_gap: {
            const auto payload = iotox::local::decode_terminal_output_gap(
                decoded.value().payload);
            if (!payload) __builtin_trap();
            const auto reencoded =
                iotox::local::encode_terminal_output_gap(payload.value());
            if (!reencoded || reencoded.value() != decoded.value().payload) {
                __builtin_trap();
            }
            break;
        }
        case iotox::local::TerminalPacketType::exit_status: {
            const auto payload = iotox::local::decode_terminal_exit_status(
                decoded.value().payload);
            if (!payload) __builtin_trap();
            const auto reencoded =
                iotox::local::encode_terminal_exit_status(payload.value());
            if (!reencoded || reencoded.value() != decoded.value().payload) {
                __builtin_trap();
            }
            break;
        }
        case iotox::local::TerminalPacketType::input:
        case iotox::local::TerminalPacketType::resize:
        case iotox::local::TerminalPacketType::detach:
        case iotox::local::TerminalPacketType::close:
        case iotox::local::TerminalPacketType::output_ack:
        case iotox::local::TerminalPacketType::ping:
        case iotox::local::TerminalPacketType::output:
        case iotox::local::TerminalPacketType::detached:
        case iotox::local::TerminalPacketType::closed:
        case iotox::local::TerminalPacketType::error:
        case iotox::local::TerminalPacketType::pong:
            break;
    }
    return 0;
}
