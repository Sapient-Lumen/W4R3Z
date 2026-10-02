#include "iotox/interactive.hpp"

#include <algorithm>
#include <limits>
#include <utility>

namespace iotox::interactive {
namespace {

void wipe_vector(std::vector<std::uint8_t> &bytes) noexcept {
    for (std::uint8_t &byte : bytes) {
        volatile std::uint8_t *slot = &byte;
        *slot = 0U;
    }
    bytes.clear();
}

void wipe_deque(std::deque<std::uint8_t> &bytes) noexcept {
    for (std::uint8_t &byte : bytes) {
        volatile std::uint8_t *slot = &byte;
        *slot = 0U;
    }
    bytes.clear();
}

void wipe_front(std::deque<std::uint8_t> &bytes) noexcept {
    volatile std::uint8_t *slot = &bytes.front();
    *slot = 0U;
    bytes.pop_front();
}

void write_u64_be(std::uint8_t *output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[index] = static_cast<std::uint8_t>(
            value >> static_cast<unsigned>((7U - index) * 8U));
    }
}

std::uint64_t read_u64_be(std::span<const std::uint8_t> bytes) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : bytes) {
        value = (value << 8U) | byte;
    }
    return value;
}

std::uint8_t probe_padding_byte(std::uint64_t nonce, std::size_t index) {
    const unsigned shift = static_cast<unsigned>((index % 8U) * 8U);
    return static_cast<std::uint8_t>(
        (nonce >> shift) ^ static_cast<std::uint64_t>(index * 131U));
}

template <std::size_t Size>
bool all_zero(const std::array<std::uint8_t, Size> &value) {
    return std::all_of(value.begin(), value.end(), [](std::uint8_t byte) {
        return byte == 0U;
    });
}

std::uint64_t saturating_add(std::uint64_t left, std::uint64_t right) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return left + right;
}

std::uint64_t move_fraction_toward(
    std::uint64_t current, std::uint64_t sample,
    std::uint64_t denominator) {
    // Computing (N-1)*current + sample directly can overflow even though the
    // weighted result lies between its inputs. Move by the difference instead.
    return sample >= current
        ? current + (sample - current) / denominator
        : current - (current - sample) / denominator;
}

}  // namespace

Result<std::array<std::uint8_t, kProbePacketSize>> encode_probe(
    const ProbePacket &packet) {
    auto sized = encode_sized_probe(packet, kProbePacketSize);
    if (!sized) {
        return sized.status();
    }
    std::array<std::uint8_t, kProbePacketSize> bytes{};
    std::copy(sized.value().begin(), sized.value().end(), bytes.begin());
    return bytes;
}

Result<std::vector<std::uint8_t>> encode_sized_probe(
    const ProbePacket &packet, std::size_t packet_size) {
    if (packet.carrier != ProbeCarrier::lossless &&
        packet.carrier != ProbeCarrier::lossy) {
        return Status{ErrorCode::invalid_argument,
                      "interactive probe carrier is invalid"};
    }
    if (packet.nonce == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "interactive probe nonce zero is reserved"};
    }
    if (packet.kind != ProbeKind::request && packet.kind != ProbeKind::reply) {
        return Status{ErrorCode::invalid_argument,
                      "interactive probe kind is invalid"};
    }
    if (packet_size < kProbePacketSize ||
        packet_size > kMaximumResearchProbePacketSize) {
        return Status{ErrorCode::invalid_argument,
                      "interactive probe size must be in 10..1200 bytes"};
    }
    std::vector<std::uint8_t> bytes(packet_size);
    bytes[0] = packet.carrier == ProbeCarrier::lossy
        ? kLossyProbePacketId
        : kLosslessProbePacketId;
    bytes[1] = static_cast<std::uint8_t>(packet.kind);
    write_u64_be(bytes.data() + 2U, packet.nonce);
    for (std::size_t index = kProbePacketSize; index < bytes.size(); ++index) {
        bytes[index] = probe_padding_byte(packet.nonce, index);
    }
    return bytes;
}

Result<ProbePacket> decode_probe(
    std::span<const std::uint8_t> bytes, ProbeCarrier carrier) {
    if (bytes.size() != kProbePacketSize) {
        return Status{ErrorCode::protocol_error,
                      "interactive probe packet has the wrong size"};
    }
    return decode_sized_probe(bytes, carrier);
}

Result<ProbePacket> decode_sized_probe(
    std::span<const std::uint8_t> bytes, ProbeCarrier carrier) {
    if (carrier != ProbeCarrier::lossless && carrier != ProbeCarrier::lossy) {
        return Status{ErrorCode::invalid_argument,
                      "interactive probe carrier is invalid"};
    }
    if (bytes.size() < kProbePacketSize ||
        bytes.size() > kMaximumResearchProbePacketSize) {
        return Status{ErrorCode::protocol_error,
                      "interactive probe packet size is outside 10..1200 bytes"};
    }
    const std::uint8_t expected_id = carrier == ProbeCarrier::lossy
        ? kLossyProbePacketId
        : kLosslessProbePacketId;
    if (bytes[0] != expected_id) {
        return Status{ErrorCode::protocol_error,
                      "interactive probe packet uses the wrong carrier ID"};
    }
    if (bytes[1] != static_cast<std::uint8_t>(ProbeKind::request) &&
        bytes[1] != static_cast<std::uint8_t>(ProbeKind::reply)) {
        return Status{ErrorCode::protocol_error,
                      "interactive probe packet kind is invalid"};
    }
    const std::uint64_t nonce = read_u64_be(bytes.subspan(2U, 8U));
    if (nonce == 0U) {
        return Status{ErrorCode::protocol_error,
                      "interactive probe packet nonce zero is reserved"};
    }
    for (std::size_t index = kProbePacketSize; index < bytes.size(); ++index) {
        if (bytes[index] != probe_padding_byte(nonce, index)) {
            return Status{ErrorCode::protocol_error,
                          "interactive probe padding is malformed"};
        }
    }
    return ProbePacket{
        carrier, static_cast<ProbeKind>(bytes[1]), nonce};
}

AttachmentFence::AttachmentFence(
    SessionId session_id, std::uint64_t incarnation,
    std::uint64_t initial_generation)
    : session_id_(session_id), incarnation_(incarnation),
      generation_(initial_generation) {}

Result<AttachmentToken> AttachmentFence::attach(
    PrincipalId principal_id, AttachmentNonce nonce) {
    if (all_zero(session_id_) || incarnation_ == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "attachment fence requires a nonzero session and incarnation"};
    }
    if (all_zero(principal_id)) {
        return Status{ErrorCode::invalid_argument,
                      "attachment principal may not be all zero"};
    }
    if (all_zero(nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "attachment nonce may not be all zero"};
    }
    if (generation_ == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "attachment generation is exhausted"};
    }

    ++generation_;
    current_ = AttachmentToken{
        session_id_, principal_id, nonce, incarnation_, generation_};
    return *current_;
}

Status AttachmentFence::validate(const AttachmentToken &token) const {
    if (!current_) {
        return Status{ErrorCode::unavailable,
                      "interactive session has no current attachment"};
    }
    if (token.session_id != session_id_ ||
        token.incarnation != incarnation_) {
        return Status{ErrorCode::protocol_error,
                      "attachment token names a different session incarnation"};
    }
    if (token.generation != generation_ || token != *current_) {
        return Status{ErrorCode::protocol_error,
                      "attachment token is stale or does not match the controller"};
    }
    return Status::success();
}

Status AttachmentFence::detach(const AttachmentToken &token) {
    const Status accepted = validate(token);
    if (!accepted.ok()) {
        return accepted;
    }
    current_.reset();
    return Status::success();
}

Status AttachmentFence::replace_incarnation() {
    if (all_zero(session_id_) || incarnation_ == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "attachment fence requires a nonzero session and incarnation"};
    }
    if (incarnation_ == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal incarnation is exhausted"};
    }
    ++incarnation_;
    current_.reset();
    return Status::success();
}

void AttachmentFence::invalidate() noexcept { current_.reset(); }

const std::optional<AttachmentToken> &AttachmentFence::current() const noexcept {
    return current_;
}

bool AttachmentFence::attached() const noexcept { return current_.has_value(); }
std::uint64_t AttachmentFence::generation() const noexcept { return generation_; }
const SessionId &AttachmentFence::session_id() const noexcept { return session_id_; }
std::uint64_t AttachmentFence::incarnation() const noexcept { return incarnation_; }

ByteReplayWindow::ByteReplayWindow() : ByteReplayWindow(Config{}) {}

ByteReplayWindow::ByteReplayWindow(Config config)
    : config_(config),
      base_sequence_(config.initial_sequence),
      next_sequence_(config.initial_sequence) {}

ByteReplayWindow::~ByteReplayWindow() { wipe_deque(bytes_); }

ByteReplayWindow &ByteReplayWindow::operator=(
    const ByteReplayWindow &other) {
    if (this == &other) return *this;
    wipe_deque(bytes_);
    config_ = other.config_;
    base_sequence_ = other.base_sequence_;
    next_sequence_ = other.next_sequence_;
    bytes_ = other.bytes_;
    return *this;
}

ByteReplayWindow::ByteReplayWindow(ByteReplayWindow &&other) noexcept
    : config_(other.config_),
      base_sequence_(other.base_sequence_),
      next_sequence_(other.next_sequence_),
      bytes_(std::move(other.bytes_)) {
    wipe_deque(other.bytes_);
    other.base_sequence_ = other.config_.initial_sequence;
    other.next_sequence_ = other.config_.initial_sequence;
}

ByteReplayWindow &ByteReplayWindow::operator=(
    ByteReplayWindow &&other) noexcept {
    if (this == &other) return *this;
    wipe_deque(bytes_);
    config_ = other.config_;
    base_sequence_ = other.base_sequence_;
    next_sequence_ = other.next_sequence_;
    bytes_ = std::move(other.bytes_);
    wipe_deque(other.bytes_);
    other.base_sequence_ = other.config_.initial_sequence;
    other.next_sequence_ = other.config_.initial_sequence;
    return *this;
}

Result<std::uint64_t> ByteReplayWindow::append(
    std::span<const std::uint8_t> bytes) {
    if (config_.maximum_bytes == 0U || config_.initial_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "replay window requires nonzero bounds and initial sequence"};
    }
    if (bytes.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "replay append may not be empty"};
    }
    if (bytes.size() > config_.maximum_bytes - bytes_.size()) {
        return Status{ErrorCode::resource_exhausted,
                      "unacknowledged replay bytes reached the configured limit"};
    }
    if (bytes.size() >
        std::numeric_limits<std::uint64_t>::max() - next_sequence_) {
        return Status{ErrorCode::resource_exhausted,
                      "replay byte sequence is exhausted"};
    }

    const std::uint64_t first = next_sequence_;
    bytes_.insert(bytes_.end(), bytes.begin(), bytes.end());
    next_sequence_ += static_cast<std::uint64_t>(bytes.size());
    return first;
}

Status ByteReplayWindow::acknowledge(
    std::uint64_t next_expected_sequence) {
    if (next_expected_sequence > next_sequence_) {
        return Status{ErrorCode::protocol_error,
                      "replay acknowledgement advances beyond produced input"};
    }
    if (next_expected_sequence <= base_sequence_) {
        return Status::success();
    }

    const std::uint64_t released = next_expected_sequence - base_sequence_;
    if (released > bytes_.size()) {
        return Status{ErrorCode::internal_error,
                      "replay acknowledgement exceeds retained bytes"};
    }
    for (std::uint64_t index = 0U; index < released; ++index) {
        wipe_front(bytes_);
    }
    base_sequence_ = next_expected_sequence;
    return Status::success();
}

Result<ReplaySlice> ByteReplayWindow::replay_from(
    std::uint64_t next_expected_sequence, std::size_t maximum_bytes) const {
    if (maximum_bytes == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "replay slice limit must be positive"};
    }
    if (next_expected_sequence < base_sequence_) {
        return Status{ErrorCode::not_found,
                      "requested replay position predates retained history"};
    }
    if (next_expected_sequence > next_sequence_) {
        return Status{ErrorCode::protocol_error,
                      "requested replay position advances beyond produced input"};
    }

    const std::size_t offset = static_cast<std::size_t>(
        next_expected_sequence - base_sequence_);
    const std::size_t available = bytes_.size() - offset;
    const std::size_t count = std::min(available, maximum_bytes);

    ReplaySlice result;
    result.first_sequence = next_expected_sequence;
    result.next_sequence = next_expected_sequence + count;
    result.complete = count == available;
    result.bytes.reserve(count);
    auto cursor = bytes_.begin() + static_cast<std::ptrdiff_t>(offset);
    result.bytes.insert(
        result.bytes.end(), cursor,
        cursor + static_cast<std::ptrdiff_t>(count));
    return result;
}

ReplaySnapshot ByteReplayWindow::snapshot() const noexcept {
    return ReplaySnapshot{
        base_sequence_, next_sequence_, bytes_.size(), config_.maximum_bytes};
}

InputReceiver::InputReceiver() : InputReceiver(Config{}) {}

InputReceiver::InputReceiver(Config config)
    : config_(config),
      next_expected_sequence_(config.initial_sequence) {}

InputReceiver::~InputReceiver() { wipe_vector(staged_bytes_); }

InputReceiver &InputReceiver::operator=(const InputReceiver &other) {
    if (this == &other) return *this;
    wipe_vector(staged_bytes_);
    config_ = other.config_;
    next_expected_sequence_ = other.next_expected_sequence_;
    staged_sequence_ = other.staged_sequence_;
    staged_bytes_ = other.staged_bytes_;
    consumed_bytes_ = other.consumed_bytes_;
    terminal_failure_ = other.terminal_failure_;
    return *this;
}

InputReceiver::InputReceiver(InputReceiver &&other) noexcept
    : config_(other.config_),
      next_expected_sequence_(other.next_expected_sequence_),
      staged_sequence_(other.staged_sequence_),
      staged_bytes_(std::move(other.staged_bytes_)),
      consumed_bytes_(other.consumed_bytes_),
      terminal_failure_(other.terminal_failure_) {
    wipe_vector(other.staged_bytes_);
    other.next_expected_sequence_ = other.config_.initial_sequence;
    other.staged_sequence_ = 0U;
    other.consumed_bytes_ = 0U;
    other.terminal_failure_ = false;
}

InputReceiver &InputReceiver::operator=(InputReceiver &&other) noexcept {
    if (this == &other) return *this;
    wipe_vector(staged_bytes_);
    config_ = other.config_;
    next_expected_sequence_ = other.next_expected_sequence_;
    staged_sequence_ = other.staged_sequence_;
    staged_bytes_ = std::move(other.staged_bytes_);
    consumed_bytes_ = other.consumed_bytes_;
    terminal_failure_ = other.terminal_failure_;
    wipe_vector(other.staged_bytes_);
    other.next_expected_sequence_ = other.config_.initial_sequence;
    other.staged_sequence_ = 0U;
    other.consumed_bytes_ = 0U;
    other.terminal_failure_ = false;
    return *this;
}

Status InputReceiver::validate_config() const {
    if (config_.maximum_frame_bytes == 0U ||
        config_.initial_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "input receiver requires nonzero bounds and initial sequence"};
    }
    return Status::success();
}

Result<InputOfferResult> InputReceiver::offer(
    std::uint64_t sequence, std::span<const std::uint8_t> bytes) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (terminal_failure_) {
        return Status{ErrorCode::unavailable,
                      "input receiver incarnation is terminal"};
    }
    if (sequence == 0U || bytes.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "input offer requires a nonzero sequence and nonempty bytes"};
    }
    if (bytes.size() > config_.maximum_frame_bytes) {
        return Status{ErrorCode::resource_exhausted,
                      "input offer exceeds the configured frame bound"};
    }
    if (bytes.size() >
        std::numeric_limits<std::uint64_t>::max() - sequence) {
        return Status{ErrorCode::resource_exhausted,
                      "input offer sequence is exhausted"};
    }

    const std::uint64_t end = sequence +
        static_cast<std::uint64_t>(bytes.size());
    if (!staged_bytes_.empty()) {
        if (sequence == staged_sequence_ &&
            bytes.size() == staged_bytes_.size() &&
            std::equal(bytes.begin(), bytes.end(), staged_bytes_.begin())) {
            return InputOfferResult{
                InputDisposition::pending, next_expected_sequence_};
        }
        if (end <= next_expected_sequence_) {
            return InputOfferResult{
                InputDisposition::duplicate, next_expected_sequence_};
        }
        const std::uint64_t staged_end = staged_sequence_ +
            static_cast<std::uint64_t>(staged_bytes_.size());
        if (sequence < staged_end) {
            return Status{ErrorCode::protocol_error,
                          "input offer overlaps the staged frame"};
        }
        return InputOfferResult{
            InputDisposition::future_gap, next_expected_sequence_};
    }

    if (end <= next_expected_sequence_) {
        return InputOfferResult{
            InputDisposition::duplicate, next_expected_sequence_};
    }
    if (sequence < next_expected_sequence_) {
        return Status{ErrorCode::protocol_error,
                      "input offer partially overlaps committed bytes"};
    }
    if (sequence > next_expected_sequence_) {
        return InputOfferResult{
            InputDisposition::future_gap, next_expected_sequence_};
    }

    staged_sequence_ = sequence;
    staged_bytes_.assign(bytes.begin(), bytes.end());
    consumed_bytes_ = 0U;
    return InputOfferResult{
        InputDisposition::staged, next_expected_sequence_};
}

Result<std::vector<std::uint8_t>> InputReceiver::pending_bytes() const {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (terminal_failure_) {
        return Status{ErrorCode::unavailable,
                      "input receiver incarnation is terminal"};
    }
    if (staged_bytes_.empty()) {
        return Status{ErrorCode::unavailable,
                      "input receiver has no staged frame"};
    }
    return std::vector<std::uint8_t>{
        staged_bytes_.begin() + static_cast<std::ptrdiff_t>(consumed_bytes_),
        staged_bytes_.end()};
}

Result<InputConsumeResult> InputReceiver::consume_staged(std::size_t bytes) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (terminal_failure_) {
        return Status{ErrorCode::unavailable,
                      "input receiver incarnation is terminal"};
    }
    if (staged_bytes_.empty()) {
        return Status{ErrorCode::protocol_error,
                      "input receiver has no staged frame to consume"};
    }
    const std::size_t remaining = staged_bytes_.size() - consumed_bytes_;
    if (bytes == 0U || bytes > remaining) {
        return Status{ErrorCode::invalid_argument,
                      "input sink consumption is outside the staged remainder"};
    }

    consumed_bytes_ += bytes;
    if (consumed_bytes_ != staged_bytes_.size()) {
        return InputConsumeResult{
            next_expected_sequence_, staged_bytes_.size() - consumed_bytes_, false};
    }

    next_expected_sequence_ = staged_sequence_ +
        static_cast<std::uint64_t>(staged_bytes_.size());
    staged_sequence_ = 0U;
    wipe_vector(staged_bytes_);
    consumed_bytes_ = 0U;
    return InputConsumeResult{next_expected_sequence_, 0U, true};
}

Status InputReceiver::fail_staged() {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (terminal_failure_) {
        return Status{ErrorCode::unavailable,
                      "input receiver incarnation is already terminal"};
    }
    if (staged_bytes_.empty()) {
        return Status{ErrorCode::protocol_error,
                      "input receiver has no staged frame to fail"};
    }
    terminal_failure_ = true;
    staged_sequence_ = 0U;
    wipe_vector(staged_bytes_);
    consumed_bytes_ = 0U;
    return Status::success();
}

InputReceiverSnapshot InputReceiver::snapshot() const noexcept {
    return InputReceiverSnapshot{
        next_expected_sequence_, staged_sequence_, staged_bytes_.size(),
        consumed_bytes_, config_.maximum_frame_bytes, terminal_failure_};
}

OutputHistory::OutputHistory() : OutputHistory(Config{}) {}

OutputHistory::OutputHistory(Config config)
    : config_(config),
      base_sequence_(config.initial_sequence),
      next_sequence_(config.initial_sequence) {}

OutputHistory::~OutputHistory() { wipe_deque(bytes_); }

OutputHistory &OutputHistory::operator=(const OutputHistory &other) {
    if (this == &other) return *this;
    wipe_deque(bytes_);
    config_ = other.config_;
    base_sequence_ = other.base_sequence_;
    next_sequence_ = other.next_sequence_;
    bytes_ = other.bytes_;
    return *this;
}

OutputHistory::OutputHistory(OutputHistory &&other) noexcept
    : config_(other.config_),
      base_sequence_(other.base_sequence_),
      next_sequence_(other.next_sequence_),
      bytes_(std::move(other.bytes_)) {
    wipe_deque(other.bytes_);
    other.base_sequence_ = other.config_.initial_sequence;
    other.next_sequence_ = other.config_.initial_sequence;
}

OutputHistory &OutputHistory::operator=(OutputHistory &&other) noexcept {
    if (this == &other) return *this;
    wipe_deque(bytes_);
    config_ = other.config_;
    base_sequence_ = other.base_sequence_;
    next_sequence_ = other.next_sequence_;
    bytes_ = std::move(other.bytes_);
    wipe_deque(other.bytes_);
    other.base_sequence_ = other.config_.initial_sequence;
    other.next_sequence_ = other.config_.initial_sequence;
    return *this;
}

Status OutputHistory::validate_config() const {
    if (config_.maximum_bytes == 0U || config_.initial_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "output history requires nonzero bounds and initial sequence"};
    }
    return Status::success();
}

Result<std::uint64_t> OutputHistory::append(
    std::span<const std::uint8_t> bytes) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (bytes.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "output history append may not be empty"};
    }
    if (bytes.size() >
        std::numeric_limits<std::uint64_t>::max() - next_sequence_) {
        return Status{ErrorCode::resource_exhausted,
                      "output history sequence is exhausted"};
    }

    const std::uint64_t first = next_sequence_;
    next_sequence_ += static_cast<std::uint64_t>(bytes.size());
    if (bytes.size() >= config_.maximum_bytes) {
        wipe_deque(bytes_);
        const std::size_t offset = bytes.size() - config_.maximum_bytes;
        bytes_.insert(bytes_.end(), bytes.begin() +
            static_cast<std::ptrdiff_t>(offset), bytes.end());
        base_sequence_ = next_sequence_ -
            static_cast<std::uint64_t>(config_.maximum_bytes);
        return first;
    }

    const std::size_t overflow = bytes.size() >
            config_.maximum_bytes - bytes_.size()
        ? bytes.size() - (config_.maximum_bytes - bytes_.size())
        : 0U;
    for (std::size_t index = 0U; index < overflow; ++index) {
        wipe_front(bytes_);
    }
    base_sequence_ += static_cast<std::uint64_t>(overflow);
    bytes_.insert(bytes_.end(), bytes.begin(), bytes.end());
    return first;
}

Status OutputHistory::acknowledge(
    std::uint64_t next_expected_sequence) {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (next_expected_sequence == 0U ||
        next_expected_sequence > next_sequence_) {
        return Status{ErrorCode::protocol_error,
                      "output acknowledgement is outside produced history"};
    }
    if (next_expected_sequence <= base_sequence_) {
        return Status::success();
    }

    const std::uint64_t released = next_expected_sequence - base_sequence_;
    if (released > bytes_.size()) {
        return Status{ErrorCode::internal_error,
                      "output acknowledgement exceeds retained history"};
    }
    for (std::uint64_t index = 0U; index < released; ++index) {
        wipe_front(bytes_);
    }
    base_sequence_ = next_expected_sequence;
    return Status::success();
}

Result<OutputReadResult> OutputHistory::read_from(
    std::uint64_t next_expected_sequence, std::size_t maximum_bytes) const {
    const Status configured = validate_config();
    if (!configured.ok()) return configured;
    if (next_expected_sequence == 0U || maximum_bytes == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "output read requires a nonzero position and byte limit"};
    }
    if (next_expected_sequence > next_sequence_) {
        return Status{ErrorCode::protocol_error,
                      "output read advances beyond produced history"};
    }
    if (next_expected_sequence < base_sequence_) {
        OutputReadResult result;
        result.kind = OutputReadKind::gap;
        result.requested_sequence = next_expected_sequence;
        result.first_sequence = base_sequence_;
        result.next_sequence = base_sequence_;
        result.produced_next_sequence = next_sequence_;
        return result;
    }

    const std::size_t offset = static_cast<std::size_t>(
        next_expected_sequence - base_sequence_);
    const std::size_t available = bytes_.size() - offset;
    const std::size_t count = std::min(available, maximum_bytes);
    OutputReadResult result;
    result.kind = OutputReadKind::data;
    result.requested_sequence = next_expected_sequence;
    result.first_sequence = next_expected_sequence;
    result.next_sequence = next_expected_sequence + count;
    result.produced_next_sequence = next_sequence_;
    result.complete = count == available;
    result.bytes.reserve(count);
    auto cursor = bytes_.begin() + static_cast<std::ptrdiff_t>(offset);
    result.bytes.insert(
        result.bytes.end(), cursor,
        cursor + static_cast<std::ptrdiff_t>(count));
    return result;
}

OutputHistorySnapshot OutputHistory::snapshot() const noexcept {
    return OutputHistorySnapshot{
        base_sequence_, next_sequence_, bytes_.size(), config_.maximum_bytes};
}

RttEstimator::RttEstimator() : RttEstimator(Config{}) {}

RttEstimator::RttEstimator(Config config) : config_(config) {}

Status RttEstimator::observe(std::chrono::microseconds round_trip) {
    if (config_.minimum_rto <= std::chrono::microseconds::zero() ||
        config_.maximum_rto < config_.minimum_rto) {
        return Status{ErrorCode::invalid_argument,
                      "RTT estimator bounds are invalid"};
    }
    if (round_trip <= std::chrono::microseconds::zero()) {
        return Status{ErrorCode::invalid_argument,
                      "RTT sample must be positive"};
    }

    const std::uint64_t sample =
        static_cast<std::uint64_t>(round_trip.count());
    snapshot_.latest_us = sample;
    if (snapshot_.sample_count == 0U) {
        snapshot_.minimum_us = sample;
        snapshot_.smoothed_us = sample;
        snapshot_.variation_us = sample / 2U;
    } else {
        snapshot_.minimum_us = std::min(snapshot_.minimum_us, sample);
        const std::uint64_t difference =
            snapshot_.smoothed_us > sample
                ? snapshot_.smoothed_us - sample
                : sample - snapshot_.smoothed_us;
        snapshot_.variation_us = move_fraction_toward(
            snapshot_.variation_us, difference, 4U);
        snapshot_.smoothed_us = move_fraction_toward(
            snapshot_.smoothed_us, sample, 8U);
    }
    ++snapshot_.sample_count;

    const std::uint64_t calculated = saturating_add(
        snapshot_.smoothed_us,
        snapshot_.variation_us > std::numeric_limits<std::uint64_t>::max() / 4U
            ? std::numeric_limits<std::uint64_t>::max()
            : 4U * snapshot_.variation_us);
    const std::uint64_t minimum =
        static_cast<std::uint64_t>(config_.minimum_rto.count());
    const std::uint64_t maximum =
        static_cast<std::uint64_t>(config_.maximum_rto.count());
    snapshot_.retransmission_timeout_us =
        std::clamp(calculated, minimum, maximum);
    return Status::success();
}

RttSnapshot RttEstimator::snapshot() const noexcept { return snapshot_; }

}  // namespace iotox::interactive
