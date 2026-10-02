#include "iotox/protocol/ratox.hpp"

#include <algorithm>
#include <limits>

namespace iotox::protocol::ratox {
namespace {

template <std::size_t Size>
bool all_zero(const std::array<std::uint8_t, Size> &value) {
    return std::all_of(value.begin(), value.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

void write_u16(std::uint8_t *output, std::uint16_t value) {
    output[0] = static_cast<std::uint8_t>(value >> 8U);
    output[1] = static_cast<std::uint8_t>(value);
}

void write_u64(std::uint8_t *output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[index] = static_cast<std::uint8_t>(
            value >> static_cast<unsigned>((7U - index) * 8U));
    }
}

std::uint16_t read_u16(std::span<const std::uint8_t> bytes) {
    return static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(bytes[0]) << 8U |
        static_cast<std::uint16_t>(bytes[1]));
}

std::uint64_t read_u64(std::span<const std::uint8_t> bytes) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : bytes) {
        value = (value << 8U) | byte;
    }
    return value;
}

bool known_type(FrameType type) {
    const auto value = static_cast<std::uint8_t>(type);
    return value >= static_cast<std::uint8_t>(FrameType::open) &&
           value <= static_cast<std::uint8_t>(FrameType::output_gap);
}

bool valid_dimensions(std::span<const std::uint8_t> bytes) {
    const std::uint16_t columns = read_u16(bytes.first(2U));
    const std::uint16_t rows = read_u16(bytes.subspan(2U, 2U));
    return columns >= 1U && columns <= 1000U &&
           rows >= 1U && rows <= 1000U;
}

bool is_result(FrameType type) {
    return type == FrameType::open_result ||
           type == FrameType::attach_result ||
           type == FrameType::pong ||
           type == FrameType::resume_result;
}

Status validate(const Frame &frame, ErrorCode code) {
    const auto reject = [code](const char *message) {
        return Status{code, message};
    };
    if (!known_type(frame.type)) {
        return reject("Ratox frame type is unknown");
    }
    if (frame.message_id == 0U || all_zero(frame.session_id) ||
        all_zero(frame.principal_id) || all_zero(frame.attachment_nonce)) {
        return reject("Ratox frame identity fields must be nonzero");
    }
    if (frame.payload.size() > kMaximumPayloadBytes) {
        return reject("Ratox frame exceeds the 1200-byte packet ceiling");
    }
    if (is_result(frame.type)) {
        if (frame.correlation_id == 0U) {
            return reject("Ratox result frame requires a correlation ID");
        }
    } else if (frame.type != FrameType::exit_status &&
               frame.correlation_id != 0U) {
        return reject("Ratox non-result frame has a correlation ID");
    }

    if (frame.type == FrameType::open) {
        if (frame.incarnation != 0U || frame.generation != 0U) {
            return reject("Ratox OPEN must precede incarnation and attachment generation");
        }
    } else if (frame.type == FrameType::open_result) {
        if ((frame.incarnation == 0U) != (frame.generation == 0U)) {
            return reject("Ratox OPEN_RESULT has a partial attachment identity");
        }
    } else if (frame.type == FrameType::attach) {
        if (frame.incarnation == 0U || frame.generation != 0U) {
            return reject("Ratox ATTACH requires an incarnation and no assigned generation");
        }
    } else if (frame.type == FrameType::attach_result) {
        if (frame.incarnation == 0U) {
            return reject("Ratox ATTACH_RESULT requires an incarnation");
        }
    } else if (frame.incarnation == 0U || frame.generation == 0U) {
        return reject("Ratox attached frame requires incarnation and generation");
    }

    const bool byte_data =
        frame.type == FrameType::input || frame.type == FrameType::output;
    const bool acknowledgement = frame.type == FrameType::input_ack ||
        frame.type == FrameType::output_ack;
    if (byte_data) {
        if (frame.sequence == 0U || frame.payload.empty()) {
            return reject("Ratox byte frame requires a sequence and nonempty payload");
        }
        if (frame.payload.size() >
            std::numeric_limits<std::uint64_t>::max() - frame.sequence) {
            return reject("Ratox byte sequence overflows");
        }
    } else if (acknowledgement) {
        if (frame.sequence != 0U || frame.acknowledgement == 0U ||
            !frame.payload.empty()) {
            return reject("Ratox acknowledgement frame is malformed");
        }
    } else if (frame.type == FrameType::output_gap) {
        if (frame.sequence == 0U || frame.acknowledgement == 0U ||
            frame.sequence > frame.acknowledgement || !frame.payload.empty()) {
            return reject("Ratox output gap bounds are malformed");
        }
    } else if (frame.sequence != 0U || frame.acknowledgement != 0U) {
        return reject("Ratox non-stream frame carries stream positions");
    }

    const std::size_t size = frame.payload.size();
    switch (frame.type) {
        case FrameType::open:
            if (size != 12U) return reject("Ratox OPEN payload must be 12 bytes");
            if (frame.payload[0U] != 1U || frame.payload[1U] != 0U ||
                !valid_dimensions(std::span<const std::uint8_t>{frame.payload}.subspan(2U, 4U)) ||
                !std::all_of(frame.payload.begin() + 6U, frame.payload.end(),
                             [](std::uint8_t byte) { return byte == 0U; })) {
                return reject("Ratox OPEN parameters are invalid or unsupported");
            }
            break;
        case FrameType::open_result: {
            if (size != 12U) return reject("Ratox OPEN_RESULT payload must be 12 bytes");
            const std::uint16_t result = read_u16(
                std::span<const std::uint8_t>{frame.payload}.first(2U));
            if (result > 8U) return reject("Ratox result code is unknown");
            if (result == 0U) {
                if (frame.incarnation == 0U || frame.generation == 0U) {
                    return reject("Ratox successful OPEN_RESULT has no attachment identity");
                }
                if (frame.payload[2U] != 1U || frame.payload[3U] != 0U ||
                    !valid_dimensions(std::span<const std::uint8_t>{frame.payload}.subspan(4U, 4U)) ||
                    !std::all_of(frame.payload.begin() + 8U, frame.payload.end(),
                                 [](std::uint8_t byte) { return byte == 0U; })) {
                    return reject("Ratox successful OPEN_RESULT parameters are invalid");
                }
            } else {
                if (frame.incarnation != 0U || frame.generation != 0U) {
                    return reject("Ratox failed OPEN_RESULT assigned an attachment");
                }
                if (!std::all_of(
                        frame.payload.begin() + 2U, frame.payload.end(),
                        [](std::uint8_t byte) { return byte == 0U; })) {
                    return reject("Ratox failed OPEN_RESULT has accepted parameters");
                }
            }
            break;
        }
        case FrameType::attach:
        case FrameType::resume: {
            if (size != 16U) return reject("Ratox attach/resume payload must be 16 bytes");
            const auto payload = std::span<const std::uint8_t>{frame.payload};
            if (read_u64(payload.first(8U)) == 0U ||
                read_u64(payload.subspan(8U, 8U)) == 0U) {
                return reject("Ratox attach/resume positions must be nonzero");
            }
            break;
        }
        case FrameType::attach_result:
        case FrameType::resume_result: {
            if (size != 28U) return reject("Ratox attach/resume result payload must be 28 bytes");
            const auto payload = std::span<const std::uint8_t>{frame.payload};
            const std::uint16_t result = read_u16(payload.first(2U));
            if (result > 8U || payload[2U] != 0U || payload[3U] != 0U) {
                return reject("Ratox attach/resume result header is invalid");
            }
            if (result == 0U) {
                if (frame.generation == 0U) {
                    return reject("Ratox successful ATTACH_RESULT has no generation");
                }
                const std::uint64_t next_input = read_u64(payload.subspan(4U, 8U));
                const std::uint64_t output_base = read_u64(payload.subspan(12U, 8U));
                const std::uint64_t output_next = read_u64(payload.subspan(20U, 8U));
                if (next_input == 0U || output_base == 0U ||
                    output_base > output_next) {
                    return reject("Ratox successful attach/resume positions are invalid");
                }
            } else {
                if (frame.type == FrameType::attach_result &&
                    frame.generation != 0U) {
                    return reject("Ratox failed ATTACH_RESULT assigned a generation");
                }
                if (!std::all_of(
                        frame.payload.begin() + 4U, frame.payload.end(),
                        [](std::uint8_t byte) { return byte == 0U; })) {
                    return reject("Ratox failed attach/resume result has stream positions");
                }
            }
            break;
        }
        case FrameType::resize:
            if (size != 4U) return reject("Ratox RESIZE payload must be 4 bytes");
            if (!valid_dimensions(frame.payload)) {
                return reject("Ratox RESIZE dimensions are invalid");
            }
            break;
        case FrameType::close:
            if (size != 2U) return reject("Ratox CLOSE payload must be 2 bytes");
            if (read_u16(frame.payload) > 4U) {
                return reject("Ratox CLOSE reason is unknown");
            }
            break;
        case FrameType::exit_status: {
            if (size != 8U) return reject("Ratox EXIT_STATUS payload must be 8 bytes");
            const std::uint8_t kind = frame.payload[0U];
            const std::uint8_t core_dump = frame.payload[1U];
            const std::uint16_t signal = read_u16(
                std::span<const std::uint8_t>{frame.payload}.subspan(2U, 2U));
            if (kind > 2U || core_dump > 1U ||
                (kind == 0U && (core_dump != 0U || signal != 0U)) ||
                (kind == 1U && signal == 0U) ||
                (kind == 2U && !std::all_of(
                    frame.payload.begin() + 1U, frame.payload.end(),
                    [](std::uint8_t byte) { return byte == 0U; }))) {
                return reject("Ratox EXIT_STATUS fields are inconsistent");
            }
            break;
        }
        case FrameType::input:
        case FrameType::output:
            break;
        case FrameType::detach:
        case FrameType::input_ack:
        case FrameType::output_ack:
        case FrameType::ping:
        case FrameType::pong:
        case FrameType::output_gap:
            if (size != 0U) return reject("Ratox control frame payload must be empty");
            break;
    }
    return Status::success();
}

}  // namespace

Result<std::size_t> encode_into(
    const Frame &frame, std::span<std::uint8_t> output) {
    const Status accepted = validate(frame, ErrorCode::invalid_argument);
    if (!accepted.ok()) {
        return accepted;
    }
    const std::size_t required = kHeaderBytes + frame.payload.size();
    if (output.size() < required) {
        return Status{ErrorCode::resource_exhausted,
                      "Ratox output buffer is smaller than the canonical packet"};
    }

    std::fill(output.begin(), output.begin() +
        static_cast<std::ptrdiff_t>(required), 0U);
    output[0U] = kPacketId;
    output[1U] = kMajor;
    output[2U] = kMinor;
    output[3U] = static_cast<std::uint8_t>(frame.type);
    output[4U] = 0U;  // v1 flags: no bits assigned
    output[5U] = static_cast<std::uint8_t>(kHeaderBytes);
    write_u16(output.data() + 6U,
              static_cast<std::uint16_t>(frame.payload.size()));
    write_u64(output.data() + 8U, frame.message_id);
    write_u64(output.data() + 16U, frame.correlation_id);
    std::copy(frame.session_id.begin(), frame.session_id.end(),
              output.begin() + 24U);
    std::copy(frame.principal_id.begin(), frame.principal_id.end(),
              output.begin() + 40U);
    std::copy(frame.attachment_nonce.begin(), frame.attachment_nonce.end(),
              output.begin() + 72U);
    write_u64(output.data() + 88U, frame.incarnation);
    write_u64(output.data() + 96U, frame.generation);
    write_u64(output.data() + 104U, frame.sequence);
    write_u64(output.data() + 112U, frame.acknowledgement);
    // Header bytes 120..123 remain frozen zero-reserved.
    std::copy(frame.payload.begin(), frame.payload.end(),
              output.begin() + static_cast<std::ptrdiff_t>(kHeaderBytes));
    return required;
}

Result<std::vector<std::uint8_t>> encode(const Frame &frame) {
    const Status accepted = validate(frame, ErrorCode::invalid_argument);
    if (!accepted.ok()) {
        return accepted;
    }
    std::vector<std::uint8_t> bytes(kHeaderBytes + frame.payload.size());
    auto encoded = encode_into(frame, bytes);
    if (!encoded.ok()) return encoded.status();
    return bytes;
}

Result<Frame> decode(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kHeaderBytes || bytes.size() > kMaximumPacketBytes) {
        return Status{ErrorCode::protocol_error,
                      "Ratox packet size is outside 124..1200 bytes"};
    }
    if (bytes[0U] != kPacketId || bytes[1U] != kMajor ||
        bytes[2U] != kMinor || bytes[4U] != 0U ||
        bytes[5U] != kHeaderBytes ||
        !std::all_of(bytes.begin() + 120U, bytes.begin() + 124U,
                     [](std::uint8_t byte) { return byte == 0U; })) {
        return Status{ErrorCode::protocol_error,
                      "Ratox fixed header, version, flags, or reserved bytes are invalid"};
    }
    const std::uint16_t payload_size = read_u16(bytes.subspan(6U, 2U));
    if (bytes.size() != kHeaderBytes + payload_size) {
        return Status{ErrorCode::protocol_error,
                      "Ratox payload length does not match the packet"};
    }
    Frame frame;
    frame.type = static_cast<FrameType>(bytes[3U]);
    frame.message_id = read_u64(bytes.subspan(8U, 8U));
    frame.correlation_id = read_u64(bytes.subspan(16U, 8U));
    std::copy_n(bytes.begin() + 24U, frame.session_id.size(), frame.session_id.begin());
    std::copy_n(bytes.begin() + 40U, frame.principal_id.size(), frame.principal_id.begin());
    std::copy_n(bytes.begin() + 72U, frame.attachment_nonce.size(), frame.attachment_nonce.begin());
    frame.incarnation = read_u64(bytes.subspan(88U, 8U));
    frame.generation = read_u64(bytes.subspan(96U, 8U));
    frame.sequence = read_u64(bytes.subspan(104U, 8U));
    frame.acknowledgement = read_u64(bytes.subspan(112U, 8U));
    frame.payload.assign(bytes.begin() + kHeaderBytes, bytes.end());
    const Status accepted = validate(frame, ErrorCode::protocol_error);
    if (!accepted.ok()) {
        return accepted;
    }
    return frame;
}

std::string_view to_string(FrameType type) noexcept {
    switch (type) {
        case FrameType::open: return "OPEN";
        case FrameType::open_result: return "OPEN_RESULT";
        case FrameType::attach: return "ATTACH";
        case FrameType::attach_result: return "ATTACH_RESULT";
        case FrameType::detach: return "DETACH";
        case FrameType::input: return "INPUT";
        case FrameType::input_ack: return "INPUT_ACK";
        case FrameType::output: return "OUTPUT";
        case FrameType::output_ack: return "OUTPUT_ACK";
        case FrameType::resize: return "RESIZE";
        case FrameType::ping: return "PING";
        case FrameType::pong: return "PONG";
        case FrameType::close: return "CLOSE";
        case FrameType::exit_status: return "EXIT_STATUS";
        case FrameType::resume: return "RESUME";
        case FrameType::resume_result: return "RESUME_RESULT";
        case FrameType::output_gap: return "OUTPUT_GAP";
    }
    return "UNKNOWN";
}

AdmissionPacer::AdmissionPacer() : AdmissionPacer(Config{}) {}

AdmissionPacer::AdmissionPacer(Config config)
    : config_(config), interval_(config.base_interval) {}

Status AdmissionPacer::validate_config() const {
    if (config_.base_interval <= std::chrono::microseconds::zero() ||
        config_.maximum_interval < config_.base_interval ||
        config_.maximum_packet_bytes == 0U ||
        config_.maximum_packet_bytes > kMaximumPayloadBytes ||
        config_.maximum_buffered_bytes < config_.maximum_packet_bytes ||
        config_.recovery_accepts == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox admission pacer configuration is invalid"};
    }
    return Status::success();
}

Status AdmissionPacer::enqueue(
    std::span<const std::uint8_t> bytes, Clock::time_point now) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (bytes.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox admission pacer may not enqueue an empty record"};
    }
    if (bytes.size() > config_.maximum_buffered_bytes - bytes_.size()) {
        return Status{ErrorCode::resource_exhausted,
                      "Ratox admission pacer input buffer is full"};
    }
    const bool was_empty = bytes_.empty();
    bytes_.insert(bytes_.end(), bytes.begin(), bytes.end());
    if (was_empty && offered_bytes_ == 0U) {
        next_ready_ = now + interval_;
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>> AdmissionPacer::ready(
    Clock::time_point now) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (bytes_.empty()) {
        return Status{ErrorCode::unavailable,
                      "Ratox admission pacer has no buffered bytes"};
    }
    if (offered_bytes_ == 0U) {
        if (!next_ready_ || now < *next_ready_) {
            return Status{ErrorCode::unavailable,
                          "Ratox admission pacer is coalescing"};
        }
        offered_bytes_ = std::min(bytes_.size(), config_.maximum_packet_bytes);
    }
    std::vector<std::uint8_t> packet;
    packet.reserve(offered_bytes_);
    packet.insert(
        packet.end(), bytes_.begin(),
        bytes_.begin() + static_cast<std::ptrdiff_t>(offered_bytes_));
    return packet;
}

Status AdmissionPacer::accepted(
    std::size_t bytes, Clock::time_point now) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (offered_bytes_ == 0U || bytes != offered_bytes_) {
        return Status{ErrorCode::protocol_error,
                      "Ratox admission acceptance does not match the offered packet"};
    }
    for (std::size_t index = 0U; index < offered_bytes_; ++index) {
        bytes_.pop_front();
    }
    offered_bytes_ = 0U;
    if (consecutive_accepts_ != std::numeric_limits<std::uint32_t>::max()) {
        ++consecutive_accepts_;
    }
    if (interval_ > config_.base_interval &&
        consecutive_accepts_ >= config_.recovery_accepts) {
        interval_ = std::max(config_.base_interval, interval_ / 2);
        consecutive_accepts_ = 0U;
    }
    if (bytes_.empty()) {
        next_ready_.reset();
        interval_ = config_.base_interval;
        consecutive_accepts_ = 0U;
    } else {
        next_ready_ = now + interval_;
    }
    return Status::success();
}

Status AdmissionPacer::rejected(Clock::time_point now) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (offered_bytes_ == 0U) {
        return Status{ErrorCode::protocol_error,
                      "Ratox admission rejection has no offered packet"};
    }
    offered_bytes_ = 0U;
    consecutive_accepts_ = 0U;
    interval_ = interval_ >= config_.maximum_interval / 2
        ? config_.maximum_interval
        : interval_ * 2;
    next_ready_ = now + interval_;
    return Status::success();
}

PacingSnapshot AdmissionPacer::snapshot() const noexcept {
    return PacingSnapshot{
        bytes_.size(), offered_bytes_,
        static_cast<std::uint64_t>(interval_.count()),
        consecutive_accepts_};
}

}  // namespace iotox::protocol::ratox
