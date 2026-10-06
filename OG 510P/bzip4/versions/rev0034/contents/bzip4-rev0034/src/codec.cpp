#include "bzip4/codec.hpp"

#include "bzip4/libbz3.h"
#include "codec_core.hpp"
#include "frame_envelope.hpp"
#include "frame_source.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <string_view>
#include <utility>

namespace bzip4 {
namespace {

constexpr std::size_t frame_header_size = detail::frame_header_size;
constexpr std::size_t block_header_size = detail::block_header_size;

void write_u32_le(std::byte* data, std::uint32_t value) noexcept {
    data[0] = static_cast<std::byte>(value & 0xffU);
    data[1] = static_cast<std::byte>((value >> 8U) & 0xffU);
    data[2] = static_cast<std::byte>((value >> 16U) & 0xffU);
    data[3] = static_cast<std::byte>((value >> 24U) & 0xffU);
}

[[nodiscard]] std::size_t checked_add(std::size_t lhs, std::size_t rhs) {
    if (rhs > std::numeric_limits<std::size_t>::max() - lhs) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "size arithmetic overflow");
    }
    return lhs + rhs;
}

[[nodiscard]] std::size_t checked_mul(std::size_t lhs, std::size_t rhs) {
    if (lhs != 0 && rhs > std::numeric_limits<std::size_t>::max() / lhs) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "size arithmetic overflow");
    }
    return lhs * rhs;
}

void validate_block_size(std::uint32_t block_size) {
    if (block_size < min_block_size || block_size > max_block_size) {
        throw CodecError(BZ3_ERR_INIT, "block size must be between 65 KiB and 511 MiB");
    }
}

[[nodiscard]] std::uint32_t validated_block_size(std::uint32_t block_size) {
    validate_block_size(block_size);
    return block_size;
}

[[nodiscard]] std::uint32_t effective_block_size(
    std::uint32_t requested,
    std::size_t input_size) {
    std::size_t effective = requested;
    if (effective > input_size) {
        effective = bz3_bound(input_size);
    }
    effective = std::max<std::size_t>(effective, min_block_size);
    if (effective > max_block_size || effective > std::numeric_limits<std::uint32_t>::max()) {
        throw CodecError(BZ3_ERR_INIT, "effective block size is outside the bzip3 range");
    }
    return static_cast<std::uint32_t>(effective);
}

[[nodiscard]] std::string codec_message(int code, const bz3_state* state) {
    if (state != nullptr) {
        // The C API takes a non-const pointer but only reads the error field here.
        return bz3_strerror(const_cast<bz3_state*>(state));
    }
    switch (code) {
        case BZ3_ERR_MALFORMED_HEADER:
            return "malformed BZ3v1 frame";
        case BZ3_ERR_TRUNCATED_DATA:
            return "truncated BZ3v1 frame";
        case BZ3_ERR_DATA_TOO_BIG:
            return "output budget exceeded";
        case BZ3_ERR_INIT:
            return "codec initialization failed";
        case BZ3_ERR_DATA_SIZE_TOO_SMALL:
            return "decoder workspace is too small";
        default:
            return "bzip3 codec error " + std::to_string(code);
    }
}

[[nodiscard]] std::size_t decoder_workspace_bytes(std::uint32_t block_size) {
    const std::size_t codec_state_bytes =
        bz3_min_memory_needed(static_cast<std::int32_t>(block_size));
    if (codec_state_bytes == 0) {
        throw CodecError(BZ3_ERR_INIT, "unable to estimate decoder workspace");
    }
    return checked_add(codec_state_bytes, bz3_bound(block_size));
}

} // namespace

CodecError::CodecError(int code, std::string message)
    : std::runtime_error(std::move(message)), code_(code) {}

class Workspace::Impl final {
public:
    struct StateDeleter {
        void operator()(bz3_state* state) const noexcept {
            if (state != nullptr) {
                bz3_free(state);
            }
        }
    };

    using StatePtr = std::unique_ptr<bz3_state, StateDeleter>;

    static StatePtr make_state(std::uint32_t block_size) {
        StatePtr state(bz3_new(static_cast<std::int32_t>(block_size)));
        if (!state) {
            throw CodecError(BZ3_ERR_INIT, "bz3_new failed");
        }
        return state;
    }

    explicit Impl(std::uint32_t block_size)
        : block_size_(validated_block_size(block_size)),
          state_(make_state(block_size_)),
          scratch_capacity_(bz3_bound(block_size_)),
          scratch_(std::make_unique_for_overwrite<std::byte[]>(scratch_capacity_)) {}

    Impl(const Impl&) = delete;
    Impl& operator=(const Impl&) = delete;

    [[nodiscard]] std::span<const std::byte> encode_loaded(std::size_t input_size) {
        const detail::Bz3BlockView result = detail::bz3_encode_block_view(
            state_.get(),
            reinterpret_cast<std::uint8_t*>(scratch_.get()),
            static_cast<std::int32_t>(input_size));
        const int error = bz3_last_error(state_.get());
        if (error != BZ3_OK || result.size < 0 || result.data == nullptr) {
            throw CodecError(error, codec_message(error, state_.get()));
        }
        const std::size_t encoded = static_cast<std::size_t>(result.size);
        if (encoded > scratch_capacity_ || encoded > bz3_bound(input_size)) {
            throw CodecError(BZ3_ERR_OUT_OF_BOUNDS,
                             "encoder returned a size outside the per-block bound");
        }
        return {reinterpret_cast<const std::byte*>(result.data), encoded};
    }

    [[nodiscard]] std::span<const std::byte> decode_loaded(
        std::size_t encoded_size,
        std::size_t original_size) {
        const detail::Bz3BlockView result = detail::bz3_decode_block_view(
            state_.get(),
            reinterpret_cast<std::uint8_t*>(scratch_.get()),
            scratch_capacity_,
            static_cast<std::int32_t>(encoded_size),
            static_cast<std::int32_t>(original_size));
        const int error = bz3_last_error(state_.get());
        if (error != BZ3_OK || result.size < 0 || result.data == nullptr) {
            throw CodecError(error, codec_message(error, state_.get()));
        }
        if (static_cast<std::size_t>(result.size) != original_size) {
            throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                             "decoded block length disagrees with its frame descriptor");
        }
        return {reinterpret_cast<const std::byte*>(result.data), original_size};
    }

    std::uint32_t block_size_{};
    StatePtr state_;
    std::size_t scratch_capacity_{};
    std::unique_ptr<std::byte[]> scratch_;
};

Workspace::Workspace(std::uint32_t block_size) : impl_(std::make_unique<Impl>(block_size)) {}
Workspace::~Workspace() = default;
Workspace::Workspace(Workspace&&) noexcept = default;
Workspace& Workspace::operator=(Workspace&&) noexcept = default;

std::uint32_t Workspace::block_size() const noexcept {
    return impl_ ? impl_->block_size_ : 0;
}

std::size_t Workspace::scratch_capacity() const noexcept {
    return impl_ ? impl_->scratch_capacity_ : 0;
}

std::span<const std::byte> Workspace::encode_block_view(std::span<const std::byte> input) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    if (input.size() > impl_->block_size_ ||
        input.size() > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "input block exceeds workspace capacity");
    }
    if (!input.empty()) {
        std::memmove(impl_->scratch_.get(), input.data(), input.size());
    }
    return impl_->encode_loaded(input.size());
}

std::span<const std::byte> Workspace::encode_block_from(
    std::size_t input_size,
    std::uint64_t source_offset,
    const RangeReader& reader) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (input_size > impl_->block_size_ ||
        input_size > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "input block exceeds workspace capacity");
    }
    if (input_size != 0) {
        reader(source_offset, std::span<std::byte>{impl_->scratch_.get(), input_size});
    }
    return impl_->encode_loaded(input_size);
}

std::vector<std::byte> Workspace::encode_block(std::span<const std::byte> input) {
    const std::span<const std::byte> view = encode_block_view(input);
    return {view.begin(), view.end()};
}

std::span<const std::byte> Workspace::decode_block_view(
    std::span<const std::byte> encoded,
    std::size_t original_size) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    if (encoded.size() > impl_->scratch_capacity_ ||
        encoded.size() > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max()) ||
        original_size > impl_->block_size_ ||
        original_size > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "block descriptor exceeds workspace capacity");
    }
    if (!encoded.empty()) {
        std::memmove(impl_->scratch_.get(), encoded.data(), encoded.size());
    }
    return impl_->decode_loaded(encoded.size(), original_size);
}

std::span<const std::byte> Workspace::decode_block_from(
    std::size_t encoded_size,
    std::size_t original_size,
    std::uint64_t source_offset,
    const RangeReader& reader) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (encoded_size > impl_->scratch_capacity_ ||
        encoded_size > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max()) ||
        original_size > impl_->block_size_ ||
        original_size > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG, "block descriptor exceeds workspace capacity");
    }
    if (encoded_size != 0) {
        reader(source_offset, std::span<std::byte>{impl_->scratch_.get(), encoded_size});
    }
    return impl_->decode_loaded(encoded_size, original_size);
}

void Workspace::decode_block_into(
    std::span<const std::byte> encoded,
    std::span<std::byte> output) {
    const std::span<const std::byte> decoded = decode_block_view(encoded, output.size());
    if (!decoded.empty()) {
        std::memmove(output.data(), decoded.data(), decoded.size());
    }
}

std::vector<std::byte> Workspace::decode_block(
    std::span<const std::byte> encoded,
    std::size_t original_size) {
    const std::span<const std::byte> view = decode_block_view(encoded, original_size);
    return {view.begin(), view.end()};
}

FrameInfo Workspace::encode_frame_to(
    std::span<const std::byte> input,
    const FrameSink& sink) {
    const RangeReader reader = detail::span_reader(input);
    return encode_frame_from(input.size(), reader, sink);
}

FrameInfo Workspace::encode_frame_from(
    std::size_t input_size,
    const RangeReader& reader,
    const FrameSink& sink) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (!sink) {
        throw std::invalid_argument("frame sink must be callable");
    }

    // Validate all shape arithmetic and BZ3v1 block-count representability
    // before exposing the first byte to a sink.
    (void)frame_bound(input_size, impl_->block_size_);
    const std::size_t block_count_size = input_size == 0
        ? 0
        : 1 + (input_size - 1) / impl_->block_size_;

    FrameInfo info;
    info.block_size = impl_->block_size_;
    info.block_count = static_cast<std::uint32_t>(block_count_size);
    info.original_size = input_size;
    detail::DecoderWorkspaceRequirements decoder_requirements;

    std::array<std::byte, frame_header_size> header{};
    header[0] = std::byte{'B'};
    header[1] = std::byte{'Z'};
    header[2] = std::byte{'3'};
    header[3] = std::byte{'v'};
    header[4] = std::byte{'1'};
    write_u32_le(header.data() + 5, info.block_size);
    write_u32_le(header.data() + 9, info.block_count);
    sink(header);

    std::size_t offset = 0;
    while (offset < input_size) {
        const std::size_t size = std::min<std::size_t>(
            impl_->block_size_, input_size - offset);
        const std::span<const std::byte> encoded = encode_block_from(
            size, detail::source_offset(offset), reader);
        if (encoded.size() > static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max())) {
            throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                             "encoded block cannot be represented in BZ3v1");
        }

        const detail::BlockEnvelopeValidation envelope =
            detail::validate_block_envelope(
                encoded.size(),
                {reinterpret_cast<const std::uint8_t*>(encoded.data()), encoded.size()},
                size, info.block_size);
        if (envelope.error_code != BZ3_OK) {
            throw CodecError(
                envelope.error_code,
                std::string("encoder produced an invalid block envelope: ") +
                    detail::block_envelope_issue_message(envelope.issue));
        }
        detail::merge_decoder_requirements(decoder_requirements, envelope);

        std::array<std::byte, block_header_size> descriptor{};
        write_u32_le(descriptor.data(), static_cast<std::uint32_t>(encoded.size()));
        write_u32_le(descriptor.data() + 4, static_cast<std::uint32_t>(size));
        sink(descriptor);
        sink(encoded);

        info.encoded_block_bytes = checked_add(info.encoded_block_bytes, encoded.size());
        offset = checked_add(offset, size);
    }
    if (info.block_count != 0) {
        info.decoder_block_size = detail::select_decoder_block_size(
            decoder_requirements, info.block_size);
        if (info.decoder_block_size == 0) {
            throw std::logic_error(
                "encoder envelope requirements do not fit its workspace declaration");
        }
        info.decoder_workspace_bytes = decoder_workspace_bytes(
            info.decoder_block_size);
    }
    return info;
}

std::vector<std::byte> Workspace::encode_frame(std::span<const std::byte> input) {
    if (!impl_) {
        throw std::logic_error("operation on a moved-from bzip4 workspace");
    }
    std::vector<std::byte> output;
    output.reserve(frame_bound(input.size(), impl_->block_size_));
    const FrameInfo info = encode_frame_to(input, [&](std::span<const std::byte> bytes) {
        output.insert(output.end(), bytes.begin(), bytes.end());
    });
    const std::size_t expected_size = checked_add(
        checked_add(frame_header_size, checked_mul(info.block_count, block_header_size)),
        info.encoded_block_bytes);
    if (output.size() != expected_size) {
        throw std::logic_error("encoded frame byte accounting mismatch");
    }
    return output;
}

std::uint32_t select_frame_block_size(
    std::uint32_t requested_block_size,
    std::size_t input_size) {
    return effective_block_size(requested_block_size, input_size);
}

std::size_t workspace_memory_bound(std::uint32_t block_size) {
    validate_block_size(block_size);
    return decoder_workspace_bytes(block_size);
}

std::size_t frame_bound(std::size_t input_size, std::uint32_t block_size) {
    validate_block_size(block_size);
    const std::size_t block_count = input_size == 0
        ? 0 : 1 + (input_size - 1) / block_size;
    if (block_count > std::numeric_limits<std::uint32_t>::max()) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                         "frame block count cannot be represented in BZ3v1");
    }
    const std::size_t full_blocks = input_size / block_size;
    const std::size_t remainder = input_size % block_size;
    std::size_t total = frame_header_size;
    const std::size_t full_cost = checked_add(block_header_size, bz3_bound(block_size));
    total = checked_add(total, checked_mul(full_blocks, full_cost));
    if (remainder != 0) {
        total = checked_add(total, checked_add(block_header_size, bz3_bound(remainder)));
    }
    return total;
}

FrameInfo compress_frame_to(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size,
    const FrameSink& sink) {
    const RangeReader reader = detail::span_reader(input);
    return compress_frame_from(input.size(), requested_block_size, reader, sink);
}

FrameInfo compress_frame_from(
    std::size_t input_size,
    std::uint32_t requested_block_size,
    const RangeReader& reader,
    const FrameSink& sink) {
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    const auto block_size = select_frame_block_size(requested_block_size, input_size);
    Workspace workspace(block_size);
    return workspace.encode_frame_from(input_size, reader, sink);
}

std::vector<std::byte> compress_frame(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size) {
    const auto block_size = select_frame_block_size(requested_block_size, input.size());
    Workspace workspace(block_size);
    return workspace.encode_frame(input);
}

FrameInfo inspect_frame(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    const RangeReader reader = detail::span_reader(encoded);
    return inspect_frame_from(
        encoded.size(), reader, max_output_size,
        reject_trailing_bytes, max_workspace_bytes);
}

FrameInfo inspect_frame_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    const detail::FrameSource source{encoded_size, reader};
    return detail::scan_frame_source(
        source, max_output_size, reject_trailing_bytes, max_workspace_bytes);
}

FrameInfo decompress_frame_to(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    const RangeReader reader = detail::span_reader(encoded);
    return decompress_frame_from(
        encoded.size(), reader, max_output_size, sink,
        reject_trailing_bytes, max_workspace_bytes);
}

FrameInfo decompress_frame_from(
    std::size_t encoded_size,
    const RangeReader& reader,
    std::size_t max_output_size,
    const FrameSink& sink,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    if (!reader) {
        throw std::invalid_argument("range reader must be callable");
    }
    if (!sink) {
        throw std::invalid_argument("frame sink must be callable");
    }

    const detail::FrameSource source{encoded_size, reader};
    const FrameInfo info = detail::scan_frame_source(
        source, max_output_size, reject_trailing_bytes, max_workspace_bytes);
    if (info.block_count == 0) {
        return info;
    }

    Workspace workspace(info.decoder_block_size);
    detail::FrameBlockCursor cursor(source, info);
    while (cursor.has_next()) {
        const detail::BlockDescriptor block = cursor.next();
        const std::span<const std::byte> decoded = workspace.decode_block_from(
            block.compressed_size,
            block.original_size,
            detail::source_offset(block.payload_offset),
            reader);
        if (!decoded.empty()) {
            sink(decoded);
        }
    }
    cursor.require_complete();
    return info;
}

std::vector<std::byte> decompress_frame(
    std::span<const std::byte> encoded,
    std::size_t max_output_size,
    bool reject_trailing_bytes,
    std::size_t max_workspace_bytes) {
    const RangeReader reader = detail::span_reader(encoded);
    const detail::FrameSource source{encoded.size(), reader};
    const FrameInfo info = detail::scan_frame_source(
        source, max_output_size, reject_trailing_bytes, max_workspace_bytes);
    if (info.block_count == 0) {
        return {};
    }

    std::vector<std::byte> output;
    output.reserve(info.original_size);
    Workspace workspace(info.decoder_block_size);
    detail::FrameBlockCursor cursor(source, info);
    while (cursor.has_next()) {
        const detail::BlockDescriptor block = cursor.next();
        const std::span<const std::byte> decoded = workspace.decode_block_from(
            block.compressed_size,
            block.original_size,
            detail::source_offset(block.payload_offset),
            reader);
        output.insert(output.end(), decoded.begin(), decoded.end());
    }
    cursor.require_complete();
    if (output.size() != info.original_size) {
        throw CodecError(BZ3_ERR_MALFORMED_HEADER,
                         "decoded frame length disagrees with its validated descriptors");
    }
    return output;
}

std::vector<std::byte> compress_frame_upstream_exact(
    std::span<const std::byte> input,
    std::uint32_t requested_block_size) {
    const auto block_size = effective_block_size(requested_block_size, input.size());
    const std::size_t block_count = input.size() / block_size +
        (input.size() % block_size != 0 ? 1U : 0U);
    if (block_count > std::numeric_limits<std::uint32_t>::max()) {
        throw CodecError(BZ3_ERR_DATA_TOO_BIG,
                         "legacy frame block count cannot be represented in BZ3v1");
    }

    std::vector<std::byte> output;
    output.reserve(frame_bound(input.size(), block_size));
    output.resize(frame_header_size);
    output[0] = std::byte{'B'};
    output[1] = std::byte{'Z'};
    output[2] = std::byte{'3'};
    output[3] = std::byte{'v'};
    output[4] = std::byte{'1'};
    write_u32_le(output.data() + 5, block_size);
    write_u32_le(output.data() + 9, static_cast<std::uint32_t>(block_count));

    Workspace workspace(block_size);
    std::size_t input_offset = 0;
    for (std::size_t index = 0; index < block_count; ++index) {
        std::size_t block_bytes = block_size;
        if (index + 1 == block_count) {
            // Deliberately preserve bzip3 1.5.3's exact-multiple defect only in
            // this explicitly named compatibility witness.
            block_bytes = input.size() % block_size;
        }
        const std::span<const std::byte> encoded = workspace.encode_block_view(
            input.subspan(input_offset, block_bytes));
        const std::size_t descriptor_offset = output.size();
        output.resize(checked_add(descriptor_offset, block_header_size));
        write_u32_le(output.data() + descriptor_offset,
                     static_cast<std::uint32_t>(encoded.size()));
        write_u32_le(output.data() + descriptor_offset + 4,
                     static_cast<std::uint32_t>(block_bytes));
        output.insert(output.end(), encoded.begin(), encoded.end());
        input_offset = checked_add(input_offset, block_bytes);
    }
    return output;
}

const char* translated_codec_version() noexcept { return bz3_version(); }

} // namespace bzip4
