#include "bzip4/activation.hpp"
#include "bzip4/atomic_file.hpp"
#include "bzip4/codec.hpp"
#include "bzip4/libbz3.h"
#include "bzip4/pinned_file.hpp"
#include "bzip4/parallel_codec.hpp"
#include "bzip4/profile.hpp"
#include "bzip4/release_audit.hpp"
#include "bzip4/resource_plan.hpp"
#include "bzip4/sha256.hpp"
#include "bzip4/zip_preflight.hpp"
#include "oracle_api.hpp"
#include "codec_core.hpp"
#include "frame_envelope.hpp"

#include <algorithm>
#include <atomic>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace {

struct Failure final : std::runtime_error {
    using std::runtime_error::runtime_error;
};

#define CHECK(expression) do { \
    if (!(expression)) throw Failure(std::string("CHECK failed: ") + #expression + \
        " at " + __FILE__ + ":" + std::to_string(__LINE__)); \
} while (false)

template <class Exception, class Function>
void check_throws(Function&& function) {
    bool threw = false;
    try {
        std::forward<Function>(function)();
    } catch (const Exception&) {
        threw = true;
    }
    CHECK(threw);
}

template <class Function>
void check_codec_error(int expected, Function&& function) {
    bool threw = false;
    try {
        std::forward<Function>(function)();
    } catch (const bzip4::CodecError& error) {
        threw = true;
        CHECK(error.code() == expected);
    }
    CHECK(threw);
}

[[nodiscard]] std::span<const std::byte> as_bytes(std::string_view value) noexcept {
    return {reinterpret_cast<const std::byte*>(value.data()), value.size()};
}

[[nodiscard]] std::vector<std::byte> pattern(std::size_t size) {
    std::vector<std::byte> output(size);
    std::uint32_t state = 0x13579bdfU;
    for (std::size_t index = 0; index < size; ++index) {
        state = state * 1664525U + 1013904223U;
        const std::uint8_t mixed = static_cast<std::uint8_t>(
            ((state >> 24U) ^ (index % 251U) ^ ((index / 97U) & 0xffU)) & 0xffU);
        output[index] = static_cast<std::byte>(mixed);
    }
    return output;
}

[[nodiscard]] std::vector<std::byte> repeated_text(
    std::size_t size,
    std::uint32_t variant) {
    const std::string line =
        "revision=" + std::to_string(variant) +
        " path=src/datacube.cpp status=validated owner=worker "
        "payload=the_quick_brown_fox_jumps_over_the_lazy_dog\n";
    std::vector<std::byte> output;
    output.reserve(size);
    while (output.size() < size) {
        const std::size_t remaining = size - output.size();
        const std::size_t count = std::min(remaining, line.size());
        const auto* first = reinterpret_cast<const std::byte*>(line.data());
        output.insert(output.end(), first, first + static_cast<std::ptrdiff_t>(count));
    }
    return output;
}

[[nodiscard]] std::vector<std::byte> random_runs(
    std::size_t size,
    std::size_t run_length,
    std::uint32_t seed) {
    CHECK(run_length != 0);
    std::vector<std::byte> output(size);
    std::uint32_t state = seed;
    std::uint8_t previous = 0;
    std::size_t offset = 0;
    while (offset < size) {
        state = state * 1664525U + 1013904223U;
        std::uint8_t value = static_cast<std::uint8_t>(state >> 24U);
        if (offset != 0 && value == previous) {
            value = static_cast<std::uint8_t>(value + 1U);
        }
        previous = value;
        const std::size_t count = std::min(run_length, size - offset);
        std::fill_n(
            output.begin() + static_cast<std::ptrdiff_t>(offset),
            static_cast<std::ptrdiff_t>(count),
            static_cast<std::byte>(value));
        offset += count;
    }
    return output;
}

[[nodiscard]] std::uint8_t block_model(std::span<const std::uint8_t> encoded) {
    CHECK(encoded.size() >= 9);
    const std::uint32_t raw_bwt = static_cast<std::uint32_t>(encoded[4]) |
        (static_cast<std::uint32_t>(encoded[5]) << 8U) |
        (static_cast<std::uint32_t>(encoded[6]) << 16U) |
        (static_cast<std::uint32_t>(encoded[7]) << 24U);
    CHECK(raw_bwt != std::numeric_limits<std::uint32_t>::max());
    return encoded[8];
}

[[nodiscard]] std::uint32_t bzip_crc(std::span<const std::byte> input) noexcept {
    std::uint32_t crc = 1;
    for (const std::byte value : input) {
        crc ^= std::to_integer<std::uint8_t>(value);
        for (unsigned bit = 0; bit < 8U; ++bit) {
            const std::uint32_t mask = 0U - (crc & 1U);
            crc = (crc >> 1U) ^ (0x82f63b78U & mask);
        }
    }
    return crc;
}

[[nodiscard]] std::uint32_t read_u32(std::span<const std::byte> input, std::size_t offset) {
    CHECK(offset <= input.size());
    CHECK(input.size() - offset >= 4);
    return std::to_integer<std::uint32_t>(input[offset]) |
        (std::to_integer<std::uint32_t>(input[offset + 1]) << 8U) |
        (std::to_integer<std::uint32_t>(input[offset + 2]) << 16U) |
        (std::to_integer<std::uint32_t>(input[offset + 3]) << 24U);
}

void write_u32(std::span<std::byte> output, std::size_t offset, std::uint32_t value) {
    CHECK(offset <= output.size());
    CHECK(output.size() - offset >= 4);
    output[offset] = static_cast<std::byte>(value & 0xffU);
    output[offset + 1] = static_cast<std::byte>((value >> 8U) & 0xffU);
    output[offset + 2] = static_cast<std::byte>((value >> 16U) & 0xffU);
    output[offset + 3] = static_cast<std::byte>((value >> 24U) & 0xffU);
}

void append_u16(std::vector<std::byte>& output, std::uint16_t value) {
    output.push_back(static_cast<std::byte>(value & 0xffU));
    output.push_back(static_cast<std::byte>((value >> 8U) & 0xffU));
}

void append_u32(std::vector<std::byte>& output, std::uint32_t value) {
    output.push_back(static_cast<std::byte>(value & 0xffU));
    output.push_back(static_cast<std::byte>((value >> 8U) & 0xffU));
    output.push_back(static_cast<std::byte>((value >> 16U) & 0xffU));
    output.push_back(static_cast<std::byte>((value >> 24U) & 0xffU));
}

void append_u64(std::vector<std::byte>& output, std::uint64_t value) {
    append_u32(output, static_cast<std::uint32_t>(value & 0xffffffffULL));
    append_u32(output, static_cast<std::uint32_t>(value >> 32U));
}

void write_u16(std::span<std::byte> output, std::size_t offset, std::uint16_t value) {
    CHECK(offset <= output.size());
    CHECK(output.size() - offset >= 2);
    output[offset] = static_cast<std::byte>(value & 0xffU);
    output[offset + 1] = static_cast<std::byte>((value >> 8U) & 0xffU);
}

void write_u64(std::span<std::byte> output, std::size_t offset, std::uint64_t value) {
    CHECK(offset <= output.size());
    CHECK(output.size() - offset >= 8);
    write_u32(output, offset, static_cast<std::uint32_t>(value & 0xffffffffULL));
    write_u32(output, offset + 4, static_cast<std::uint32_t>(value >> 32U));
}

void append_text(std::vector<std::byte>& output, std::string_view value) {
    for (const char byte : value) {
        output.push_back(static_cast<std::byte>(static_cast<unsigned char>(byte)));
    }
}

[[nodiscard]] std::size_t block_payload_offset(
    std::span<const std::byte> frame,
    std::uint32_t wanted_index) {
    CHECK(frame.size() >= 13);
    const std::uint32_t count = read_u32(frame, 9);
    CHECK(wanted_index < count);
    std::size_t cursor = 13;
    for (std::uint32_t index = 0; index < count; ++index) {
        CHECK(frame.size() - cursor >= 8);
        const std::size_t compressed = read_u32(frame, cursor);
        cursor += 8;
        CHECK(compressed <= frame.size() - cursor);
        if (index == wanted_index) return cursor;
        cursor += compressed;
    }
    throw Failure("block payload was not found");
}

[[nodiscard]] std::vector<std::byte> make_empty_block_frame(
    std::uint32_t block_size,
    std::uint32_t block_count) {
    std::vector<std::byte> frame;
    frame.reserve(13U + static_cast<std::size_t>(block_count) * 16U);
    append_text(frame, "BZ3v1");
    append_u32(frame, block_size);
    append_u32(frame, block_count);
    for (std::uint32_t index = 0; index < block_count; ++index) {
        (void)index;
        append_u32(frame, 8);
        append_u32(frame, 0);
        append_u32(frame, 1); // CRC state for an empty input.
        append_u32(frame, std::numeric_limits<std::uint32_t>::max()); // BWT index -1.
    }
    return frame;
}

class TempDirectory final {
public:
    TempDirectory() {
        std::string writable =
            (std::filesystem::temp_directory_path() / "bzip4-tests-XXXXXX").string();
        writable.push_back('\0');
        char* result = ::mkdtemp(writable.data());
        if (result == nullptr) throw std::system_error(errno, std::generic_category(), "mkdtemp");
        path_ = result;
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    TempDirectory(const TempDirectory&) = delete;
    TempDirectory& operator=(const TempDirectory&) = delete;

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

private:
    std::filesystem::path path_;
};

void write_file(const std::filesystem::path& path, std::span<const std::byte> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("unable to create fixture: " + path.string());
    if (!bytes.empty()) {
        output.write(reinterpret_cast<const char*>(bytes.data()),
                     static_cast<std::streamsize>(bytes.size()));
    }
    if (!output) throw std::runtime_error("unable to write fixture: " + path.string());
}

[[nodiscard]] std::vector<std::byte> read_file(const std::filesystem::path& path) {
    const std::uintmax_t length = std::filesystem::file_size(path);
    CHECK(length <= std::numeric_limits<std::size_t>::max());
    std::vector<std::byte> bytes(static_cast<std::size_t>(length));
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("unable to read fixture: " + path.string());
    if (!bytes.empty()) {
        input.read(reinterpret_cast<char*>(bytes.data()),
                   static_cast<std::streamsize>(bytes.size()));
    }
    if (!input) throw std::runtime_error("short fixture read: " + path.string());
    return bytes;
}

[[nodiscard]] std::size_t temporary_output_count(const std::filesystem::path& directory) {
    std::size_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator(directory)) {
        if (entry.path().filename().string().starts_with(".bzip4-tmp-")) ++count;
    }
    return count;
}

void write_text_file(const std::filesystem::path& path, std::string_view text) {
    std::filesystem::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("unable to create text fixture: " + path.string());
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    if (!output) throw std::runtime_error("unable to write text fixture: " + path.string());
}

void write_fixture_manifest(const std::filesystem::path& root) {
    std::vector<std::string> paths;
    for (const auto& entry : std::filesystem::recursive_directory_iterator(root)) {
        if (!entry.is_regular_file()) continue;
        const std::string relative = entry.path().lexically_relative(root).generic_string();
        if (relative != "MANIFEST.sha256") paths.push_back(relative);
    }
    std::sort(paths.begin(), paths.end());
    std::ofstream output(root / "MANIFEST.sha256", std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("unable to create fixture manifest");
    for (const std::string& relative : paths) {
        output << bzip4::hex_sha256_file(root / relative) << "  " << relative << '\n';
    }
    if (!output) throw std::runtime_error("unable to write fixture manifest");
}

struct ZipSpec {
    std::string local_name;
    std::string central_name;
    std::string payload;
    std::uint16_t flags{};
    std::uint32_t crc{0x12345678U};
    bool signed_descriptor{};
    bool local_zip64{};
    std::string local_extra;
    std::string central_extra;
    std::uint16_t version_made_by{20};
    std::uint32_t external_attributes{};

    ZipSpec(
        std::string local_name_value,
        std::string central_name_value,
        std::string payload_value,
        std::uint16_t flags_value = 0,
        std::uint32_t crc_value = 0x12345678U,
        bool signed_descriptor_value = false,
        bool local_zip64_value = false,
        std::string local_extra_value = {},
        std::string central_extra_value = {},
        std::uint16_t version_made_by_value = 20,
        std::uint32_t external_attributes_value = 0)
        : local_name(std::move(local_name_value)),
          central_name(std::move(central_name_value)),
          payload(std::move(payload_value)),
          flags(flags_value),
          crc(crc_value),
          signed_descriptor(signed_descriptor_value),
          local_zip64(local_zip64_value),
          local_extra(std::move(local_extra_value)),
          central_extra(std::move(central_extra_value)),
          version_made_by(version_made_by_value),
          external_attributes(external_attributes_value) {}
};

[[nodiscard]] std::vector<std::byte> make_zip(const std::vector<ZipSpec>& specs) {
    struct EntryMeta { std::uint32_t offset{}; const ZipSpec* spec{}; };
    std::vector<std::byte> output;
    std::vector<EntryMeta> metadata;
    for (const ZipSpec& spec : specs) {
        const std::size_t local_extra_size =
            (spec.local_zip64 ? 20U : 0U) + spec.local_extra.size();
        CHECK(local_extra_size <= std::numeric_limits<std::uint16_t>::max());
        CHECK(output.size() <= std::numeric_limits<std::uint32_t>::max());
        metadata.push_back({static_cast<std::uint32_t>(output.size()), &spec});
        append_u32(output, 0x04034b50U);
        append_u16(output, spec.local_zip64 ? 45 : 20);
        append_u16(output, spec.flags);
        append_u16(output, 0);
        append_u16(output, 0);
        append_u16(output, 0);
        append_u32(output, (spec.flags & 8U) != 0U ? 0U : spec.crc);
        append_u32(output, (spec.flags & 8U) != 0U ? 0U :
            (spec.local_zip64 ? 0xffffffffU : static_cast<std::uint32_t>(spec.payload.size())));
        append_u32(output, (spec.flags & 8U) != 0U ? 0U :
            (spec.local_zip64 ? 0xffffffffU : static_cast<std::uint32_t>(spec.payload.size())));
        append_u16(output, static_cast<std::uint16_t>(spec.local_name.size()));
        append_u16(output, static_cast<std::uint16_t>(local_extra_size));
        append_text(output, spec.local_name);
        if (spec.local_zip64) {
            append_u16(output, 0x0001U);
            append_u16(output, 16);
            append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
            append_u32(output, 0);
            append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
            append_u32(output, 0);
        }
        append_text(output, spec.local_extra);
        append_text(output, spec.payload);
        if ((spec.flags & 8U) != 0U) {
            if (spec.signed_descriptor) append_u32(output, 0x08074b50U);
            append_u32(output, spec.crc);
            if (spec.local_zip64) {
                append_u64(output, spec.payload.size());
                append_u64(output, spec.payload.size());
            } else {
                append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
                append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
            }
        }
    }
    CHECK(output.size() <= std::numeric_limits<std::uint32_t>::max());
    const std::uint32_t central_offset = static_cast<std::uint32_t>(output.size());
    for (const EntryMeta& meta : metadata) {
        const ZipSpec& spec = *meta.spec;
        CHECK(spec.central_extra.size() <= std::numeric_limits<std::uint16_t>::max());
        append_u32(output, 0x02014b50U);
        append_u16(output, spec.version_made_by);
        append_u16(output, spec.local_zip64 ? 45 : 20);
        append_u16(output, spec.flags);
        append_u16(output, 0);
        append_u16(output, 0);
        append_u16(output, 0);
        append_u32(output, spec.crc);
        append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
        append_u32(output, static_cast<std::uint32_t>(spec.payload.size()));
        append_u16(output, static_cast<std::uint16_t>(spec.central_name.size()));
        append_u16(output, static_cast<std::uint16_t>(spec.central_extra.size()));
        append_u16(output, 0);
        append_u16(output, 0);
        append_u16(output, 0);
        append_u32(output, spec.external_attributes);
        append_u32(output, meta.offset);
        append_text(output, spec.central_name);
        append_text(output, spec.central_extra);
    }
    CHECK(output.size() - central_offset <= std::numeric_limits<std::uint32_t>::max());
    const std::uint32_t central_size = static_cast<std::uint32_t>(output.size() - central_offset);
    append_u32(output, 0x06054b50U);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u16(output, static_cast<std::uint16_t>(specs.size()));
    append_u16(output, static_cast<std::uint16_t>(specs.size()));
    append_u32(output, central_size);
    append_u32(output, central_offset);
    append_u16(output, 0);
    return output;
}

struct Zip64Fixture {
    std::vector<std::byte> bytes;
    std::size_t local_extra_identifier_offset{};
    std::size_t descriptor_offset{};
    std::size_t central_offset{};
    std::size_t central_extra_identifier_offset{};
    std::size_t zip64_eocd_offset{};
    std::size_t locator_offset{};
    std::size_t eocd_offset{};
};

[[nodiscard]] Zip64Fixture make_zip64(
    bool data_descriptor,
    bool signed_descriptor,
    bool offset_only = false) {
    constexpr std::uint32_t crc = 0xeb8eba67U;
    constexpr std::string_view name = "z64.bin";
    constexpr std::string_view payload = "xyz";
    constexpr std::uint16_t flags_with_descriptor = 0x0008U;
    constexpr std::uint16_t version_20 = 20U;
    constexpr std::uint16_t version_45 = 45U;
    constexpr std::uint16_t unix_version_45 =
        static_cast<std::uint16_t>((3U << 8U) | version_45);
    constexpr std::uint32_t regular_mode =
        static_cast<std::uint32_t>(0100644U) << 16U;

    CHECK(!offset_only || !data_descriptor);
    Zip64Fixture fixture;
    auto& output = fixture.bytes;
    const std::uint16_t flags = data_descriptor ? flags_with_descriptor : 0U;

    append_u32(output, 0x04034b50U);
    append_u16(output, offset_only ? version_20 : version_45);
    append_u16(output, flags);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u32(output, data_descriptor ? 0U : crc);
    append_u32(output, offset_only
        ? static_cast<std::uint32_t>(payload.size()) : 0xffffffffU);
    append_u32(output, offset_only
        ? static_cast<std::uint32_t>(payload.size()) : 0xffffffffU);
    append_u16(output, static_cast<std::uint16_t>(name.size()));
    append_u16(output, offset_only ? 0U : 20U);
    append_text(output, name);
    if (!offset_only) {
        fixture.local_extra_identifier_offset = output.size();
        append_u16(output, 0x0001U);
        append_u16(output, 16U);
        append_u64(output, payload.size());
        append_u64(output, payload.size());
    }
    append_text(output, payload);

    if (data_descriptor) {
        fixture.descriptor_offset = output.size();
        if (signed_descriptor) append_u32(output, 0x08074b50U);
        append_u32(output, crc);
        append_u64(output, payload.size());
        append_u64(output, payload.size());
    }

    fixture.central_offset = output.size();
    append_u32(output, 0x02014b50U);
    append_u16(output, unix_version_45);
    append_u16(output, version_45);
    append_u16(output, flags);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u32(output, crc);
    append_u32(output, offset_only
        ? static_cast<std::uint32_t>(payload.size()) : 0xffffffffU);
    append_u32(output, offset_only
        ? static_cast<std::uint32_t>(payload.size()) : 0xffffffffU);
    append_u16(output, static_cast<std::uint16_t>(name.size()));
    append_u16(output, offset_only ? 12U : 28U);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u16(output, 0);
    append_u32(output, regular_mode);
    append_u32(output, 0xffffffffU);
    append_text(output, name);
    fixture.central_extra_identifier_offset = output.size();
    append_u16(output, 0x0001U);
    append_u16(output, offset_only ? 8U : 24U);
    if (!offset_only) {
        append_u64(output, payload.size());
        append_u64(output, payload.size());
    }
    append_u64(output, 0U);

    const std::uint64_t central_size = output.size() - fixture.central_offset;
    fixture.zip64_eocd_offset = output.size();
    append_u32(output, 0x06064b50U);
    append_u64(output, 44U);
    append_u16(output, unix_version_45);
    append_u16(output, version_45);
    append_u32(output, 0U);
    append_u32(output, 0U);
    append_u64(output, 1U);
    append_u64(output, 1U);
    append_u64(output, central_size);
    append_u64(output, fixture.central_offset);

    fixture.locator_offset = output.size();
    append_u32(output, 0x07064b50U);
    append_u32(output, 0U);
    append_u64(output, fixture.zip64_eocd_offset);
    append_u32(output, 1U);

    fixture.eocd_offset = output.size();
    append_u32(output, 0x06054b50U);
    append_u16(output, 0U);
    append_u16(output, 0U);
    append_u16(output, 0xffffU);
    append_u16(output, 0xffffU);
    append_u32(output, 0xffffffffU);
    append_u32(output, 0xffffffffU);
    append_u16(output, 0U);
    return fixture;
}

class TempFile final {
public:
    explicit TempFile(std::span<const std::byte> bytes) {
        const auto base = std::filesystem::temp_directory_path() / "bzip4-test-XXXXXX";
        std::string writable = base.string();
        writable.push_back('\0');
        const int fd = ::mkstemp(writable.data());
        if (fd < 0) throw std::system_error(errno, std::generic_category(), "mkstemp");
        path_ = writable.c_str();
        std::size_t offset = 0;
        while (offset < bytes.size()) {
            const ssize_t count = ::write(
                fd, bytes.data() + static_cast<std::ptrdiff_t>(offset), bytes.size() - offset);
            if (count < 0 && errno == EINTR) continue;
            if (count <= 0) {
                const int saved = errno;
                (void)::close(fd);
                throw std::system_error(saved, std::generic_category(), "write fixture");
            }
            offset += static_cast<std::size_t>(count);
        }
        if (::close(fd) != 0) throw std::system_error(errno, std::generic_category(), "close fixture");
    }

    ~TempFile() {
        std::error_code ignored;
        std::filesystem::remove(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

private:
    std::filesystem::path path_;
};

void test_sha256() {
    const std::array<std::byte, 0> empty{};
    CHECK(bzip4::hex_sha256(empty) ==
          "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    const std::string abc = "abc";
    const auto abc_bytes = as_bytes(abc);
    CHECK(bzip4::hex_sha256(abc_bytes) ==
          "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    bzip4::Sha256 streaming;
    streaming.update(abc_bytes.first(1));
    streaming.update(abc_bytes.subspan(1));
    const auto digest = streaming.finish();
    CHECK(digest.size() == 32);
    check_throws<std::logic_error>([&] { (void)streaming.finish(); });
}

void test_activation() {
    bzip4::ActivationPolicy policy;
    policy.retained_background_workers = 15;
    policy.minimum_blocks_per_active_lane = 4;
    policy.minimum_bytes_per_active_lane = 1;
    policy.caller_participates = true;
    auto plan = bzip4::make_activation_plan(5, 500, policy);
    CHECK(plan.active_lanes == 1);
    CHECK(plan.active_background_workers == 0);
    CHECK(plan.workers_notified == 0);

    policy.minimum_blocks_per_active_lane = 1;
    policy.minimum_bytes_per_active_lane = 200;
    plan = bzip4::make_activation_plan(8, 799, policy);
    CHECK(plan.active_lanes == 3);
    CHECK(plan.active_background_workers == 2);
    policy.wake_mode = bzip4::WakeMode::all_retained;
    plan = bzip4::make_activation_plan(8, 799, policy);
    CHECK(plan.workers_notified == 15);

    plan = bzip4::make_activation_plan(0, 0, policy);
    CHECK(plan.active_lanes == 0);
    CHECK(plan.workers_notified == 0);

    policy.caller_participates = false;
    policy.retained_background_workers = 0;
    policy.wake_mode = bzip4::WakeMode::active_only;
    plan = bzip4::make_activation_plan(1, 100, policy);
    CHECK(plan.active_lanes == 0);
    CHECK(plan.active_background_workers == 0);

    policy.caller_participates = true;
    policy.retained_background_workers = std::numeric_limits<std::size_t>::max();
    policy.minimum_blocks_per_active_lane = 1;
    policy.minimum_bytes_per_active_lane = 1;
    policy.max_active_lanes = 2;
    plan = bzip4::make_activation_plan(2, 200, policy);
    CHECK(plan.active_lanes == 2);
    CHECK(plan.active_background_workers == 1);
}

void test_codec_roundtrip_and_oracle() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const auto ordinary = pattern(static_cast<std::size_t>(block) + 123U);
    const auto safe = bzip4::compress_frame(ordinary, block);
    const auto upstream = bzip4::compress_frame_upstream_exact(ordinary, block);
    CHECK(safe == upstream);
    CHECK(bzip4::decompress_frame(safe, ordinary.size()) == ordinary);
    const auto info = bzip4::inspect_frame(safe, ordinary.size());
    CHECK(info.block_count == 2);
    CHECK(info.original_size == ordinary.size());
    CHECK(safe.size() <= bzip4::frame_bound(ordinary.size(), block));

    const auto exact = pattern(static_cast<std::size_t>(block) * 2U);
    const auto broken = bzip4::compress_frame_upstream_exact(exact, block);
    const auto broken_info = bzip4::inspect_frame(broken, exact.size());
    CHECK(broken_info.block_count == 2);
    CHECK(broken_info.original_size == block);
    const auto broken_decoded = bzip4::decompress_frame(broken, exact.size());
    CHECK(broken_decoded.size() == block);
    CHECK(std::equal(broken_decoded.begin(), broken_decoded.end(), exact.begin()));

    const auto corrected = bzip4::compress_frame(exact, block);
    const auto corrected_info = bzip4::inspect_frame(corrected, exact.size());
    CHECK(corrected_info.original_size == exact.size());
    CHECK(bzip4::decompress_frame(corrected, exact.size()) == exact);

    std::vector<std::uint8_t> oracle_output(bzip4::frame_bound(ordinary.size(), block));
    std::size_t oracle_size = oracle_output.size();
    const int result = oracle_bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(ordinary.data()), oracle_output.data(),
        ordinary.size(), &oracle_size);
    CHECK(result == BZ3_OK);
    CHECK(oracle_size == upstream.size());
    CHECK(std::memcmp(oracle_output.data(), upstream.data(), oracle_size) == 0);
}

void test_block_decoder_contract() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    bzip4::Workspace workspace(block);
    CHECK(workspace.block_size() == block);
    CHECK(workspace.scratch_capacity() >= block);

    for (const std::size_t size : {std::size_t{0}, std::size_t{1}, std::size_t{63},
                                   std::size_t{64}, std::size_t{65}, std::size_t{4096}}) {
        const auto input = pattern(size);
        const auto encoded = workspace.encode_block(input);
        const auto decoded = workspace.decode_block(encoded, input.size());
        CHECK(decoded == input);
        std::vector<std::byte> destination(input.size());
        workspace.decode_block_into(encoded, destination);
        CHECK(destination == input);
    }

    const auto first_input = pattern(3000);
    const auto first_copy = workspace.encode_block(first_input);
    const auto view = workspace.encode_block_view(first_input);
    CHECK(std::equal(view.begin(), view.end(), first_copy.begin(), first_copy.end()));

    bzip4::Workspace moved(std::move(workspace));
    CHECK(workspace.block_size() == 0);
    check_throws<std::logic_error>([&] { (void)workspace.encode_block(first_input); });
    CHECK(moved.decode_block(first_copy, first_input.size()) == first_input);

    auto raw = moved.encode_block(pattern(3));
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)moved.decode_block(raw, 2);
    });

    auto regular = moved.encode_block(pattern(4096));
    CHECK(regular.size() >= 13);
    regular[8] |= std::byte{0x80};
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)moved.decode_block(regular, 4096);
    });

    regular = moved.encode_block(pattern(4096));
    write_u32(regular, 4, 0xfffffffeU);
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)moved.decode_block(regular, 4096);
    });
}

void test_low_level_c_api_hardening() {
    constexpr std::int32_t block = static_cast<std::int32_t>(bzip4::min_block_size);
    using State = std::unique_ptr<bz3_state, decltype(&bz3_free)>;
    State state(bz3_new(block), &bz3_free);
    CHECK(state != nullptr);
    bz3_free(nullptr);

    const std::size_t capacity = bz3_bound(static_cast<std::size_t>(block));
    std::vector<std::uint8_t> buffer(capacity);
    const auto small = pattern(7);
    std::memcpy(buffer.data(), small.data(), small.size());

    CHECK(bz3_encode_block(state.get(), buffer.data(), block + 1) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_DATA_TOO_BIG);

    const std::int32_t raw_size = bz3_encode_block(
        state.get(), buffer.data(), static_cast<std::int32_t>(small.size()));
    CHECK(raw_size == static_cast<std::int32_t>(small.size() + 8));
    CHECK(bz3_last_error(state.get()) == BZ3_OK);
    const std::vector<std::uint8_t> raw(buffer.begin(), buffer.begin() + raw_size);

    CHECK(bz3_decode_block(state.get(), buffer.data(), capacity, 7, 7) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);
    std::copy(raw.begin(), raw.end(), buffer.begin());
    const std::int32_t decoded = bz3_decode_block(
        state.get(), buffer.data(), capacity, raw_size, static_cast<std::int32_t>(small.size()));
    CHECK(decoded == static_cast<std::int32_t>(small.size()));
    CHECK(bz3_last_error(state.get()) == BZ3_OK);
    CHECK(std::memcmp(buffer.data(), small.data(), small.size()) == 0);

    std::copy(raw.begin(), raw.end(), buffer.begin());
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, raw_size,
        static_cast<std::int32_t>(small.size() - 1)) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);
    CHECK(bz3_orig_size_sufficient_for_decode(
        raw.data(), raw.size(), static_cast<std::int32_t>(small.size())) == 1);
    CHECK(bz3_orig_size_sufficient_for_decode(
        raw.data(), raw.size(), static_cast<std::int32_t>(small.size() - 1)) == -1);

    const auto historical_literal = pattern(64);
    std::vector<std::uint8_t> historical_raw(72);
    const std::uint32_t historical_crc = bzip_crc(historical_literal);
    historical_raw[0] = static_cast<std::uint8_t>(historical_crc & 0xffU);
    historical_raw[1] = static_cast<std::uint8_t>((historical_crc >> 8U) & 0xffU);
    historical_raw[2] = static_cast<std::uint8_t>((historical_crc >> 16U) & 0xffU);
    historical_raw[3] = static_cast<std::uint8_t>((historical_crc >> 24U) & 0xffU);
    historical_raw[4] = 0xffU;
    historical_raw[5] = 0xffU;
    historical_raw[6] = 0xffU;
    historical_raw[7] = 0xffU;
    std::memcpy(historical_raw.data() + 8, historical_literal.data(), historical_literal.size());
    std::copy(historical_raw.begin(), historical_raw.end(), buffer.begin());
    CHECK(bz3_decode_block(state.get(), buffer.data(), capacity, 72, 64) == 64);
    CHECK(bz3_last_error(state.get()) == BZ3_OK);
    CHECK(std::memcmp(buffer.data(), historical_literal.data(), historical_literal.size()) == 0);

    const auto ordinary = pattern(4096);
    std::memcpy(buffer.data(), ordinary.data(), ordinary.size());
    const std::int32_t regular_size = bz3_encode_block(
        state.get(), buffer.data(), static_cast<std::int32_t>(ordinary.size()));
    CHECK(regular_size > 0);
    const std::vector<std::uint8_t> regular(buffer.begin(), buffer.begin() + regular_size);

    std::copy(regular.begin(), regular.end(), buffer.begin());
    buffer[8] = static_cast<std::uint8_t>(buffer[8] | 0x80U);
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, regular_size,
        static_cast<std::int32_t>(ordinary.size())) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);

    std::copy(regular.begin(), regular.end(), buffer.begin());
    buffer[4] = 0xfeU;
    buffer[5] = 0xffU;
    buffer[6] = 0xffU;
    buffer[7] = 0xffU;
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, regular_size,
        static_cast<std::int32_t>(ordinary.size())) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);

    std::copy(regular.begin(), regular.end(), buffer.begin());
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, regular_size - 1,
        static_cast<std::int32_t>(ordinary.size())) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_TRUNCATED_DATA);

    CHECK(bz3_decode_block(state.get(), buffer.data(), 8, 9, 1) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_DATA_SIZE_TOO_SMALL);
    CHECK(bz3_decode_block(state.get(), buffer.data(), capacity, -1, 1) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);

    const auto high_input = pattern(static_cast<std::size_t>(block));
    const auto high_frame = bzip4::compress_frame(high_input, static_cast<std::uint32_t>(block));
    CHECK(read_u32(high_frame, 13) > static_cast<std::uint32_t>(block));
    std::vector<std::uint8_t> high_output(high_input.size());
    std::size_t high_output_size = high_output.size();
    const int high_result = bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(high_frame.data()), high_output.data(),
        high_frame.size(), &high_output_size);
    CHECK(high_result == BZ3_OK);
    CHECK(high_output_size == high_input.size());
    CHECK(std::memcmp(high_output.data(), high_input.data(), high_input.size()) == 0);

    auto bad_frame = bzip4::compress_frame(pattern(3), bzip4::min_block_size);
    write_u32(bad_frame, 17, 2); // Original size in the first frame descriptor.
    std::array<std::uint8_t, 3> bad_output{};
    std::size_t bad_output_size = bad_output.size();
    CHECK(bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(bad_frame.data()), bad_output.data(),
        bad_frame.size(), &bad_output_size) == BZ3_ERR_MALFORMED_HEADER);
}


void test_entropy_and_transform_terminal_contract() {
    constexpr std::int32_t block = static_cast<std::int32_t>(bzip4::min_block_size);
    using State = std::unique_ptr<bz3_state, decltype(&bz3_free)>;
    State state(bz3_new(block), &bz3_free);
    CHECK(state != nullptr);

    CHECK(bz3_last_error(nullptr) == BZ3_ERR_INIT);
    CHECK(std::string_view(bz3_strerror(nullptr)).find("null") != std::string_view::npos);
    CHECK(bz3_encode_block(nullptr, nullptr, 0) == -1);
    CHECK(bz3_decode_block(nullptr, nullptr, 0, 0, 0) == -1);
    CHECK(bz3_orig_size_sufficient_for_decode(nullptr, 8, 0) == -1);
    CHECK(bz3_encode_block(state.get(), nullptr, 0) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_INIT);
    CHECK(bz3_decode_block(state.get(), nullptr, 0, 0, 0) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_INIT);

    const std::size_t capacity = bz3_bound(static_cast<std::size_t>(block));
    std::vector<std::uint8_t> buffer(capacity, 0);

    // Exercise the exact inverse-transform cores directly. These tests make
    // terminal consumption, run termination, and output bounds independent of
    // the entropy/BWT layers that normally feed the transforms.
    {
        constexpr std::size_t dictionary_entries = 1U << 18U;
        std::vector<std::int32_t> dictionary(dictionary_entries);

        const std::array<std::uint8_t, 6> literals{1U, 2U, 3U, 4U, 5U, 6U};
        std::array<std::uint8_t, 8> output{};
        std::fill(output.begin(), output.end(), 0xa5U);
        std::uint32_t crc = 0;
        CHECK(bzip4::detail::bz3_decode_lzp_exact(
            literals, std::span<std::uint8_t>(output.data(), literals.size()),
            dictionary, &crc) == BZ3_OK);
        CHECK(std::equal(literals.begin(), literals.end(), output.begin()));
        CHECK(output[6] == 0xa5U && output[7] == 0xa5U);
        CHECK(crc == bzip_crc({
            reinterpret_cast<const std::byte*>(literals.data()), literals.size()}));

        std::fill(output.begin(), output.end(), 0x5aU);
        CHECK(bzip4::detail::bz3_decode_lzp_exact(
            literals, std::span<std::uint8_t>(output.data(), literals.size() - 1U),
            dictionary, nullptr) == BZ3_ERR_MALFORMED_HEADER);
        CHECK(output[5] == 0x5aU && output[6] == 0x5aU && output[7] == 0x5aU);

        const std::array<std::uint8_t, 7> overlap_match{
            0x41U, 0x41U, 0x41U, 0x41U, 0x41U, 0xf2U, 0U};
        std::array<std::uint8_t, 47> match_output{};
        std::fill(match_output.begin(), match_output.end(), 0xccU);
        CHECK(bzip4::detail::bz3_decode_lzp_exact(
            overlap_match,
            std::span<std::uint8_t>(match_output.data(), 45U),
            dictionary, nullptr) == BZ3_OK);
        CHECK(std::all_of(
            match_output.begin(), match_output.begin() + 45,
            [](std::uint8_t value) { return value == 0x41U; }));
        CHECK(match_output[45] == 0xccU && match_output[46] == 0xccU);

        std::fill(match_output.begin(), match_output.end(), 0x3cU);
        CHECK(bzip4::detail::bz3_decode_lzp_exact(
            overlap_match,
            std::span<std::uint8_t>(match_output.data(), 44U),
            dictionary, nullptr) == BZ3_ERR_MALFORMED_HEADER);
        CHECK(match_output[44] == 0x3cU && match_output[45] == 0x3cU &&
              match_output[46] == 0x3cU);

        const std::array<std::uint8_t, 8> invalid_length_component{
            0x41U, 0x41U, 0x41U, 0x41U, 0x41U, 0xf2U, 254U, 255U};
        std::vector<std::uint8_t> long_output(400U, 0x69U);
        CHECK(bzip4::detail::bz3_decode_lzp_exact(
            invalid_length_component, long_output,
            dictionary, nullptr) == BZ3_ERR_MALFORMED_HEADER);
    }

    {
        std::array<std::uint8_t, 35> literal_stream{};
        literal_stream[32] = 7U;
        literal_stream[33] = 8U;
        literal_stream[34] = 9U;
        std::array<std::uint8_t, 5> output{};
        std::fill(output.begin(), output.end(), 0xa7U);
        std::uint32_t crc = 0;
        CHECK(bzip4::detail::bz3_decode_mrle_exact(
            literal_stream,
            std::span<std::uint8_t>(output.data(), 3U),
            &crc) == BZ3_OK);
        CHECK(output[0] == 7U && output[1] == 8U && output[2] == 9U);
        CHECK(output[3] == 0xa7U && output[4] == 0xa7U);
        CHECK(crc == bzip_crc({
            reinterpret_cast<const std::byte*>(literal_stream.data() + 32), 3U}));

        std::fill(output.begin(), output.end(), 0x7aU);
        CHECK(bzip4::detail::bz3_decode_mrle_exact(
            literal_stream,
            std::span<std::uint8_t>(output.data(), 2U),
            &crc) == BZ3_ERR_MALFORMED_HEADER);
        CHECK(output[2] == 0x7aU && output[3] == 0x7aU && output[4] == 0x7aU);

        std::array<std::uint8_t, 34> selected_run{};
        selected_run[8] = 0x02U; // Select byte 0x41 for run coding.
        selected_run[32] = 0x41U;
        selected_run[33] = 4U; // Five output bytes.
        std::array<std::uint8_t, 7> run_output{};
        std::fill(run_output.begin(), run_output.end(), 0x42U);
        CHECK(bzip4::detail::bz3_decode_mrle_exact(
            selected_run,
            std::span<std::uint8_t>(run_output.data(), 5U),
            &crc) == BZ3_OK);
        CHECK(std::all_of(
            run_output.begin(), run_output.begin() + 5,
            [](std::uint8_t value) { return value == 0x41U; }));
        CHECK(run_output[5] == 0x42U && run_output[6] == 0x42U);

        std::fill(run_output.begin(), run_output.end(), 0x24U);
        CHECK(bzip4::detail::bz3_decode_mrle_exact(
            selected_run,
            std::span<std::uint8_t>(run_output.data(), 4U),
            &crc) == BZ3_ERR_MALFORMED_HEADER);
        CHECK(run_output[4] == 0x24U && run_output[5] == 0x24U &&
              run_output[6] == 0x24U);

        selected_run[33] = 255U; // Continuation without a terminating component.
        std::vector<std::uint8_t> unterminated_output(300U, 0x81U);
        CHECK(bzip4::detail::bz3_decode_mrle_exact(
            selected_run, unterminated_output,
            &crc) == BZ3_ERR_MALFORMED_HEADER);
    }

    // Four arithmetic bytes are structurally sufficient to enter a regular
    // block, but not to produce this declared output. The decoder must stop at
    // the first missing byte instead of synthesizing 0xff for every remaining
    // output symbol.
    std::array<std::uint8_t, 13> four_byte_entropy{};
    four_byte_entropy[4] = 1; // BWT primary index.
    four_byte_entropy[8] = 0; // No LZP or mRLE.
    for (const std::int32_t original : {block, block / 2}) {
        std::fill(buffer.begin(), buffer.end(), 0);
        std::copy(four_byte_entropy.begin(), four_byte_entropy.end(), buffer.begin());
        CHECK(bz3_decode_block(
            state.get(), buffer.data(), capacity,
            static_cast<std::int32_t>(four_byte_entropy.size()), original) == -1);
        CHECK(bz3_last_error(state.get()) == BZ3_ERR_TRUNCATED_DATA);
        const auto stats = bzip4::detail::bz3_entropy_decode_stats(state.get());
        CHECK(stats.truncated);
        CHECK(stats.input_bytes_read == 4);
        CHECK(stats.output_symbols == 0);
    }

    CHECK(bz3_decode_block(state.get(), buffer.data(), capacity, -1, 1) == -1);
    const auto reset_stats = bzip4::detail::bz3_entropy_decode_stats(state.get());
    CHECK(!reset_stats.truncated);
    CHECK(reset_stats.input_bytes_read == 0);
    CHECK(reset_stats.output_symbols == 0);

    const auto ordinary = pattern(4096);
    std::memcpy(buffer.data(), ordinary.data(), ordinary.size());
    const std::int32_t ordinary_encoded = bz3_encode_block(
        state.get(), buffer.data(), static_cast<std::int32_t>(ordinary.size()));
    CHECK(ordinary_encoded > 0);
    const std::vector<std::uint8_t> ordinary_block(
        buffer.begin(), buffer.begin() + ordinary_encoded);
    std::copy(ordinary_block.begin(), ordinary_block.end(), buffer.begin());
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, ordinary_encoded,
        static_cast<std::int32_t>(ordinary.size())) ==
          static_cast<std::int32_t>(ordinary.size()));
    const auto valid_stats = bzip4::detail::bz3_entropy_decode_stats(state.get());
    CHECK(!valid_stats.truncated);
    CHECK(valid_stats.output_symbols == static_cast<std::int32_t>(ordinary.size()));

    std::copy(ordinary_block.begin(), ordinary_block.end(), buffer.begin());
    buffer[4] = 0U;
    buffer[5] = 0U;
    buffer[6] = 0U;
    buffer[7] = 0U;
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, ordinary_encoded,
        static_cast<std::int32_t>(ordinary.size())) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);
    CHECK(bz3_orig_size_sufficient_for_decode(
        buffer.data(), static_cast<std::size_t>(ordinary_encoded),
        static_cast<std::int32_t>(ordinary.size())) == -1);

    // A model-4 block used to accept a smaller frame descriptor when its CRC
    // was changed to the corresponding output prefix: the mRLE loop clipped a
    // run at orig_size and ignored the rest of its transform stream. Exact
    // terminal consumption must reject this descriptor/header rewrite.
    const auto runs = random_runs(
        static_cast<std::size_t>(block) - 31U, 8U, 108U);
    std::memcpy(buffer.data(), runs.data(), runs.size());
    const std::int32_t run_encoded = bz3_encode_block(
        state.get(), buffer.data(), static_cast<std::int32_t>(runs.size()));
    CHECK(run_encoded > 0);
    CHECK(buffer[8] == 4U);
    const std::vector<std::uint8_t> run_block(
        buffer.begin(), buffer.begin() + run_encoded);
    const std::size_t prefix_size = runs.size() / 2U;
    std::copy(run_block.begin(), run_block.end(), buffer.begin());
    write_u32(
        {reinterpret_cast<std::byte*>(buffer.data()), buffer.size()}, 0,
        bzip_crc({runs.data(), prefix_size}));
    CHECK(bz3_decode_block(
        state.get(), buffer.data(), capacity, run_encoded,
        static_cast<std::int32_t>(prefix_size)) == -1);
    CHECK(bz3_last_error(state.get()) == BZ3_ERR_MALFORMED_HEADER);

    auto rewritten_frame = bzip4::compress_frame(
        runs, static_cast<std::uint32_t>(block));
    CHECK(read_u32(rewritten_frame, 9) == 1U);
    const std::size_t payload_offset = block_payload_offset(rewritten_frame, 0);
    const std::size_t payload_size = read_u32(rewritten_frame, 13);
    CHECK(block_model({
        reinterpret_cast<const std::uint8_t*>(rewritten_frame.data() +
            static_cast<std::ptrdiff_t>(payload_offset)), payload_size}) == 4U);
    write_u32(rewritten_frame, 17, static_cast<std::uint32_t>(prefix_size));
    write_u32(rewritten_frame, payload_offset, bzip_crc({runs.data(), prefix_size}));
    const auto rewritten_info = bzip4::inspect_frame(rewritten_frame, runs.size());
    CHECK(rewritten_info.original_size == prefix_size);
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::decompress_frame(rewritten_frame, runs.size());
    });

    const auto invalid_intermediate_frame = [](std::uint8_t model,
                                               std::uint32_t intermediate) {
        std::vector<std::byte> frame;
        append_text(frame, "BZ3v1");
        append_u32(frame, bzip4::min_block_size);
        append_u32(frame, 1);
        append_u32(frame, 17); // 13-byte model header plus four arithmetic bytes.
        append_u32(frame, 100);
        append_u32(frame, 0); // CRC is irrelevant: preflight must reject first.
        append_u32(frame, 1); // BWT primary index.
        frame.push_back(static_cast<std::byte>(model));
        append_u32(frame, intermediate);
        append_u32(frame, 0);
        return frame;
    };
    for (const auto& frame : {
             invalid_intermediate_frame(2U, 3U),
             invalid_intermediate_frame(4U, 31U)}) {
        check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
            (void)bzip4::inspect_frame(frame, 100);
        });
    }
}

void test_high_level_c_api_contract() {
    constexpr std::uint32_t block = bzip4::min_block_size;

    CHECK(bz3_bound(std::numeric_limits<std::size_t>::max()) ==
          std::numeric_limits<std::size_t>::max());
    CHECK(bz3_frame_bound(
        bzip4::max_block_size + 1U,
        static_cast<std::size_t>(bzip4::max_block_size) + 2U) == 0);
    CHECK(bz3_frame_bound(block, std::numeric_limits<std::size_t>::max()) == 0);

    const auto ordinary = pattern(static_cast<std::size_t>(block) + 123U);
    const std::size_t ordinary_bound = bz3_frame_bound(block, ordinary.size());
    CHECK(ordinary_bound == bzip4::frame_bound(ordinary.size(), block));
    std::vector<std::uint8_t> ordinary_frame(ordinary_bound);
    std::size_t ordinary_size = ordinary_frame.size();
    CHECK(bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(ordinary.data()),
        ordinary_frame.data(), ordinary.size(), &ordinary_size) == BZ3_OK);
    ordinary_frame.resize(ordinary_size);

    std::vector<std::uint8_t> oracle_frame(ordinary_bound);
    std::size_t oracle_size = oracle_frame.size();
    CHECK(oracle_bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(ordinary.data()),
        oracle_frame.data(), ordinary.size(), &oracle_size) == BZ3_OK);
    CHECK(ordinary_size == oracle_size);
    CHECK(std::memcmp(ordinary_frame.data(), oracle_frame.data(), ordinary_size) == 0);

    const auto exact = pattern(static_cast<std::size_t>(block) * 2U);
    const std::size_t exact_bound = bz3_frame_bound(block, exact.size());
    CHECK(exact_bound == bzip4::frame_bound(exact.size(), block));
    std::vector<std::uint8_t> exact_frame(exact_bound);
    std::size_t exact_size = exact_frame.size();
    CHECK(bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(exact.data()),
        exact_frame.data(), exact.size(), &exact_size) == BZ3_OK);
    exact_frame.resize(exact_size);
    const auto safe_frame = bzip4::compress_frame(exact, block);
    CHECK(exact_frame.size() == safe_frame.size());
    CHECK(std::memcmp(exact_frame.data(), safe_frame.data(), safe_frame.size()) == 0);

    std::vector<std::uint8_t> restored(exact.size());
    std::size_t restored_size = restored.size();
    CHECK(bz3_decompress(
        exact_frame.data(), restored.data(), exact_frame.size(), &restored_size) == BZ3_OK);
    CHECK(restored_size == exact.size());
    CHECK(std::memcmp(restored.data(), exact.data(), exact.size()) == 0);

    std::vector<std::uint8_t> oracle_exact(exact_bound);
    std::size_t oracle_exact_size = oracle_exact.size();
    CHECK(oracle_bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(exact.data()),
        oracle_exact.data(), exact.size(), &oracle_exact_size) == BZ3_OK);
    CHECK(oracle_exact_size != exact_size);
    const auto legacy_exact = bzip4::compress_frame_upstream_exact(exact, block);
    CHECK(legacy_exact.size() == oracle_exact_size);
    CHECK(std::memcmp(legacy_exact.data(), oracle_exact.data(), oracle_exact_size) == 0);

    CHECK(exact_size > 1U);
    constexpr std::size_t guard_size = 64;
    const std::size_t short_capacity = exact_size - 1U;
    std::vector<std::uint8_t> guarded(short_capacity + guard_size, 0xa5U);
    std::size_t guarded_size = short_capacity;
    CHECK(bz3_compress(
        block, reinterpret_cast<const std::uint8_t*>(exact.data()),
        guarded.data(), exact.size(), &guarded_size) == BZ3_ERR_DATA_TOO_BIG);
    CHECK(guarded_size <= short_capacity);
    CHECK(std::all_of(
        guarded.begin() + static_cast<std::ptrdiff_t>(short_capacity), guarded.end(),
        [](std::uint8_t value) { return value == 0xa5U; }));

    std::vector<std::uint8_t> guarded_output(exact.size() - 1U + guard_size, 0x5aU);
    std::size_t guarded_output_size = exact.size() - 1U;
    CHECK(bz3_decompress(
        exact_frame.data(), guarded_output.data(), exact_frame.size(),
        &guarded_output_size) == BZ3_ERR_DATA_TOO_BIG);
    CHECK(guarded_output_size == 0);
    CHECK(std::all_of(guarded_output.begin(), guarded_output.end(),
                      [](std::uint8_t value) { return value == 0x5aU; }));

    auto truncated = exact_frame;
    truncated.pop_back();
    std::vector<std::uint8_t> preflight_untouched(exact.size(), 0x6dU);
    std::size_t preflight_untouched_size = preflight_untouched.size();
    CHECK(bz3_decompress(
        truncated.data(), preflight_untouched.data(), truncated.size(),
        &preflight_untouched_size) == BZ3_ERR_TRUNCATED_DATA);
    CHECK(preflight_untouched_size == 0);
    CHECK(std::all_of(preflight_untouched.begin(), preflight_untouched.end(),
                      [](std::uint8_t value) { return value == 0x6dU; }));

    CHECK(bz3_frame_bound(block, 0) == 13U);
    std::array<std::uint8_t, 13> empty_frame{};
    std::size_t empty_frame_size = empty_frame.size();
    CHECK(bz3_compress(block, nullptr, empty_frame.data(), 0, &empty_frame_size) == BZ3_OK);
    CHECK(empty_frame_size == empty_frame.size());
    std::size_t empty_output_size = 0;
    CHECK(bz3_decompress(
        empty_frame.data(), nullptr, empty_frame.size(), &empty_output_size) == BZ3_OK);
    CHECK(empty_output_size == 0);

    std::vector<std::byte> maximum_declared_empty;
    append_text(maximum_declared_empty, "BZ3v1");
    append_u32(maximum_declared_empty, bzip4::max_block_size);
    append_u32(maximum_declared_empty, 0);
    std::size_t maximum_declared_empty_size = 0;
    CHECK(bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(maximum_declared_empty.data()), nullptr,
        maximum_declared_empty.size(), &maximum_declared_empty_size) == BZ3_OK);

    constexpr std::byte literal{0x42};
    std::vector<std::byte> maximum_declared_literal;
    append_text(maximum_declared_literal, "BZ3v1");
    append_u32(maximum_declared_literal, bzip4::max_block_size);
    append_u32(maximum_declared_literal, 1);
    append_u32(maximum_declared_literal, 9);
    append_u32(maximum_declared_literal, 1);
    append_u32(maximum_declared_literal, bzip_crc({&literal, 1}));
    append_u32(maximum_declared_literal, 0xffffffffU);
    maximum_declared_literal.push_back(literal);
    std::array<std::uint8_t, 1> maximum_declared_output{};
    std::size_t maximum_declared_output_size = maximum_declared_output.size();
    CHECK(bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(maximum_declared_literal.data()),
        maximum_declared_output.data(), maximum_declared_literal.size(),
        &maximum_declared_output_size) == BZ3_OK);
    CHECK(maximum_declared_output_size == 1);
    CHECK(maximum_declared_output[0] == std::to_integer<std::uint8_t>(literal));

    auto impossible_count = maximum_declared_empty;
    write_u32(impossible_count, 9, std::numeric_limits<std::uint32_t>::max());
    std::size_t impossible_output_size = 0;
    CHECK(bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(impossible_count.data()), nullptr,
        impossible_count.size(), &impossible_output_size) == BZ3_ERR_MALFORMED_HEADER);

    CHECK(bz3_compress(block, nullptr, nullptr, 0, nullptr) == BZ3_ERR_INIT);
    CHECK(bz3_decompress(nullptr, nullptr, 0, nullptr) == BZ3_ERR_INIT);
}

void test_checksum_fusion_paths() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const std::size_t size = static_cast<std::size_t>(block) - 31U;
    const std::array<std::pair<std::vector<std::byte>, std::uint8_t>, 4> cases{{
        {pattern(size), 0U},
        {repeated_text(size, 7U), 2U},
        {random_runs(size, 8U, 108U), 4U},
        {std::vector<std::byte>(size, std::byte{0}), 6U},
    }};

    bzip4::Workspace workspace(block);
    for (const auto& [input, expected_model] : cases) {
        const auto encoded = workspace.encode_block(input);
        CHECK(block_model({
            reinterpret_cast<const std::uint8_t*>(encoded.data()), encoded.size()}) ==
              expected_model);
        CHECK(workspace.decode_block(encoded, input.size()) == input);

        auto bad_crc = encoded;
        bad_crc[0] ^= std::byte{1};
        check_codec_error(BZ3_ERR_CRC, [&] {
            (void)workspace.decode_block(bad_crc, input.size());
        });
    }
}

void test_entropy_model_row_aliasing() {
    constexpr std::int32_t block = static_cast<std::int32_t>(bzip4::min_block_size);
    const std::size_t capacity = bz3_bound(static_cast<std::size_t>(block));
    // This size keeps all four transform-model fixtures and reaches libsais's
    // 32-bit 4k LMS gather marker path under UBSan without bloating TSan cost.
    const std::size_t input_size = 32U * 1024U - 257U;
    using ActiveState = std::unique_ptr<bz3_state, decltype(&bz3_free)>;
    using OracleState = std::unique_ptr<bz3_state, decltype(&oracle_bz3_free)>;

    std::vector<std::byte> paired_noise(input_size);
    const auto noise = pattern((input_size + 1U) / 2U);
    for (std::size_t index = 0; index < paired_noise.size(); ++index) {
        paired_noise[index] = noise[index / 2U];
    }

    std::vector<std::byte> context_churn(input_size);
    std::uint32_t state = 0x28c0ffeeU;
    for (std::size_t index = 0; index < context_churn.size(); ++index) {
        state = state * 1103515245U + 12345U;
        const std::uint8_t fresh = static_cast<std::uint8_t>(state >> 24U);
        const std::uint8_t value = index % 7U < 3U && index != 0
            ? std::to_integer<std::uint8_t>(context_churn[index - 1U])
            : fresh;
        context_churn[index] = static_cast<std::byte>(value);
    }

    const std::array<std::vector<std::byte>, 6> cases{{
        pattern(input_size),
        repeated_text(input_size, 28U),
        random_runs(input_size, 8U, 108U),
        std::vector<std::byte>(input_size, std::byte{0}),
        std::move(paired_noise),
        std::move(context_churn),
    }};
    constexpr std::array<std::uint8_t, 4> expected_models{{0U, 2U, 4U, 6U}};

    ActiveState active_encoder(bz3_new(block), &bz3_free);
    ActiveState active_decoder(bz3_new(block), &bz3_free);
    OracleState oracle_encoder(oracle_bz3_new(block), &oracle_bz3_free);
    OracleState oracle_decoder(oracle_bz3_new(block), &oracle_bz3_free);
    CHECK(active_encoder && active_decoder && oracle_encoder && oracle_decoder);

    std::vector<std::uint8_t> active_buffer(capacity);
    std::vector<std::uint8_t> oracle_buffer(capacity);
    std::vector<std::uint8_t> active_decoded(capacity);
    std::vector<std::uint8_t> oracle_decoded(capacity);

    // Reuse all four states and reverse case order on the second pass. This
    // exercises model reset, equal-history row aliasing, differing-history rows,
    // run-context transitions, and all four transform-model neighborhoods while
    // retaining the pristine C implementation as the byte-for-byte oracle.
    for (std::size_t pass = 0; pass < 2U; ++pass) {
        for (std::size_t ordinal = 0; ordinal < cases.size(); ++ordinal) {
            const std::size_t case_index = pass % 2U == 0
                ? ordinal
                : cases.size() - 1U - ordinal;
            const auto& input = cases[case_index];
            const auto size = static_cast<std::int32_t>(input.size());
            std::memcpy(active_buffer.data(), input.data(), input.size());
            std::memcpy(oracle_buffer.data(), input.data(), input.size());

            const std::int32_t active_size = bz3_encode_block(
                active_encoder.get(), active_buffer.data(), size);
            const std::int32_t oracle_size = oracle_bz3_encode_block(
                oracle_encoder.get(), oracle_buffer.data(), size);
            CHECK(active_size > 0);
            CHECK(active_size == oracle_size);
            if (case_index < expected_models.size()) {
                CHECK(block_model({active_buffer.data(),
                                   static_cast<std::size_t>(active_size)}) ==
                      expected_models[case_index]);
            }
            CHECK(std::memcmp(
                active_buffer.data(), oracle_buffer.data(),
                static_cast<std::size_t>(active_size)) == 0);

            std::memcpy(
                active_decoded.data(), active_buffer.data(),
                static_cast<std::size_t>(active_size));
            std::memcpy(
                oracle_decoded.data(), oracle_buffer.data(),
                static_cast<std::size_t>(oracle_size));
            CHECK(bz3_decode_block(
                active_decoder.get(), active_decoded.data(), capacity,
                active_size, size) == size);
            CHECK(oracle_bz3_decode_block(
                oracle_decoder.get(), oracle_decoded.data(), capacity,
                oracle_size, size) == size);
            CHECK(std::memcmp(active_decoded.data(), input.data(), input.size()) == 0);
            CHECK(std::memcmp(oracle_decoded.data(), input.data(), input.size()) == 0);
        }
    }
}

void test_borrowed_block_views_and_public_api() {
    constexpr std::int32_t block = static_cast<std::int32_t>(bzip4::min_block_size);
    const std::size_t capacity = bz3_bound(static_cast<std::size_t>(block));
    using ActiveState = std::unique_ptr<bz3_state, decltype(&bz3_free)>;
    using OracleState = std::unique_ptr<bz3_state, decltype(&oracle_bz3_free)>;

    const auto exercise_view = [&](const std::vector<std::byte>& input,
                                   std::uint8_t expected_model) {
        CHECK(input.size() <= static_cast<std::size_t>(block));
        CHECK(input.size() <= static_cast<std::size_t>(std::numeric_limits<std::int32_t>::max()));
        const std::int32_t input_size = static_cast<std::int32_t>(input.size());
        const bool expected_borrow = expected_model == 2U || expected_model == 4U;

        ActiveState internal_encoder(bz3_new(block), &bz3_free);
        ActiveState public_encoder(bz3_new(block), &bz3_free);
        OracleState oracle_encoder(oracle_bz3_new(block), &oracle_bz3_free);
        ActiveState internal_decoder(bz3_new(block), &bz3_free);
        ActiveState public_decoder(bz3_new(block), &bz3_free);
        OracleState oracle_decoder(oracle_bz3_new(block), &oracle_bz3_free);
        CHECK(internal_encoder && public_encoder && oracle_encoder);
        CHECK(internal_decoder && public_decoder && oracle_decoder);

        std::vector<std::uint8_t> internal_buffer(capacity);
        std::vector<std::uint8_t> public_buffer(capacity);
        std::vector<std::uint8_t> oracle_buffer(oracle_bz3_bound(
            static_cast<std::size_t>(block)));
        CHECK(oracle_buffer.size() == capacity);
        std::memcpy(internal_buffer.data(), input.data(), input.size());
        std::memcpy(public_buffer.data(), input.data(), input.size());
        std::memcpy(oracle_buffer.data(), input.data(), input.size());

        const bzip4::detail::Bz3BlockView encoded_view =
            bzip4::detail::bz3_encode_block_view(
                internal_encoder.get(), internal_buffer.data(), input_size);
        CHECK(encoded_view.size > 0);
        CHECK(bz3_last_error(internal_encoder.get()) == BZ3_OK);
        CHECK(encoded_view.data != nullptr);
        CHECK(block_model({encoded_view.data, static_cast<std::size_t>(encoded_view.size)}) ==
              expected_model);
        CHECK((encoded_view.data != internal_buffer.data()) == expected_borrow);
        const std::vector<std::uint8_t> encoded(
            encoded_view.data, encoded_view.data + encoded_view.size);

        const std::int32_t public_encoded_size = bz3_encode_block(
            public_encoder.get(), public_buffer.data(), input_size);
        const std::int32_t oracle_encoded_size = oracle_bz3_encode_block(
            oracle_encoder.get(), oracle_buffer.data(), input_size);
        CHECK(public_encoded_size == encoded_view.size);
        CHECK(oracle_encoded_size == encoded_view.size);
        CHECK(std::equal(encoded.begin(), encoded.end(), public_buffer.begin()));
        CHECK(std::equal(encoded.begin(), encoded.end(), oracle_buffer.begin()));

        std::copy(encoded.begin(), encoded.end(), internal_buffer.begin());
        const bzip4::detail::Bz3BlockView decoded_view =
            bzip4::detail::bz3_decode_block_view(
                internal_decoder.get(), internal_buffer.data(), capacity,
                encoded_view.size, input_size);
        CHECK(decoded_view.size == input_size);
        CHECK(bz3_last_error(internal_decoder.get()) == BZ3_OK);
        CHECK(decoded_view.data != nullptr);
        CHECK((decoded_view.data != internal_buffer.data()) == expected_borrow);
        CHECK(std::memcmp(decoded_view.data, input.data(), input.size()) == 0);

        std::copy(encoded.begin(), encoded.end(), public_buffer.begin());
        std::copy(encoded.begin(), encoded.end(), oracle_buffer.begin());
        const std::int32_t public_decoded_size = bz3_decode_block(
            public_decoder.get(), public_buffer.data(), capacity,
            public_encoded_size, input_size);
        const std::int32_t oracle_decoded_size = oracle_bz3_decode_block(
            oracle_decoder.get(), oracle_buffer.data(), oracle_buffer.size(),
            oracle_encoded_size, input_size);
        CHECK(public_decoded_size == input_size);
        CHECK(oracle_decoded_size == input_size);
        CHECK(std::memcmp(public_buffer.data(), input.data(), input.size()) == 0);
        CHECK(std::memcmp(oracle_buffer.data(), input.data(), input.size()) == 0);
    };

    const std::size_t ordinary_size = static_cast<std::size_t>(block) - 31U;
    exercise_view(pattern(ordinary_size), 0U);
    exercise_view(repeated_text(ordinary_size, 7U), 2U);
    exercise_view(random_runs(ordinary_size, 8U, 108U), 4U);
    exercise_view(std::vector<std::byte>(ordinary_size, std::byte{0}), 6U);

    // Reuse one encoder and one decoder across all transform models. The
    // internal caller copies a borrowed encoded result before the next encoder
    // operation, while the decoded view is consumed before the next decoder
    // operation. Every stream remains byte-identical to the independently
    // compiled pristine C oracle on every pass.
    ActiveState active_encoder(bz3_new(block), &bz3_free);
    OracleState oracle_encoder(oracle_bz3_new(block), &oracle_bz3_free);
    ActiveState active_decoder(bz3_new(block), &bz3_free);
    OracleState oracle_decoder(oracle_bz3_new(block), &oracle_bz3_free);
    CHECK(active_encoder && oracle_encoder && active_decoder && oracle_decoder);
    std::vector<std::uint8_t> active_buffer(capacity);
    std::vector<std::uint8_t> oracle_buffer(capacity);
    std::vector<std::uint8_t> active_decode_buffer(capacity);
    std::vector<std::uint8_t> oracle_decode_buffer(capacity);

    const std::array<std::pair<std::vector<std::byte>, std::uint8_t>, 4> reuse_cases{{
        {pattern(ordinary_size), 0U},
        {repeated_text(ordinary_size, 7U), 2U},
        {random_runs(ordinary_size, 8U, 108U), 4U},
        {std::vector<std::byte>(ordinary_size, std::byte{0}), 6U},
    }};
    for (std::size_t pass = 0; pass < 3U; ++pass) {
        for (const auto& [input, expected_model] : reuse_cases) {
            const std::int32_t input_size = static_cast<std::int32_t>(input.size());
            std::memcpy(active_buffer.data(), input.data(), input.size());
            std::memcpy(oracle_buffer.data(), input.data(), input.size());
            const bzip4::detail::Bz3BlockView result =
                bzip4::detail::bz3_encode_block_view(
                    active_encoder.get(), active_buffer.data(), input_size);
            const std::int32_t oracle_size = oracle_bz3_encode_block(
                oracle_encoder.get(), oracle_buffer.data(), input_size);
            CHECK(result.size > 0);
            CHECK(result.size == oracle_size);
            CHECK(block_model({result.data, static_cast<std::size_t>(result.size)}) ==
                  expected_model);
            CHECK(std::memcmp(
                result.data, oracle_buffer.data(),
                static_cast<std::size_t>(result.size)) == 0);

            std::memcpy(
                active_decode_buffer.data(), result.data,
                static_cast<std::size_t>(result.size));
            std::memcpy(
                oracle_decode_buffer.data(), oracle_buffer.data(),
                static_cast<std::size_t>(oracle_size));
            const bzip4::detail::Bz3BlockView decoded =
                bzip4::detail::bz3_decode_block_view(
                    active_decoder.get(), active_decode_buffer.data(), capacity,
                    result.size, input_size);
            const std::int32_t oracle_decoded = oracle_bz3_decode_block(
                oracle_decoder.get(), oracle_decode_buffer.data(), capacity,
                oracle_size, input_size);
            CHECK(decoded.size == input_size);
            CHECK(oracle_decoded == input_size);
            CHECK((decoded.data != active_decode_buffer.data()) ==
                  (expected_model == 2U || expected_model == 4U));
            CHECK(std::memcmp(decoded.data, input.data(), input.size()) == 0);
            CHECK(std::memcmp(
                oracle_decode_buffer.data(), input.data(), input.size()) == 0);
        }
    }
}

void test_frame_streaming_and_envelope() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const auto input = pattern(static_cast<std::size_t>(block) * 2U + 17U);
    const auto materialized = bzip4::compress_frame(input, block);

    std::vector<std::byte> streamed;
    std::size_t encode_callbacks = 0;
    const bzip4::FrameInfo encoded_info = bzip4::compress_frame_to(
        input, block, [&](std::span<const std::byte> bytes) {
            ++encode_callbacks;
            streamed.insert(streamed.end(), bytes.begin(), bytes.end());
        });
    CHECK(streamed == materialized);
    CHECK(encoded_info.block_count == 3);
    CHECK(encode_callbacks == 1U + 2U * encoded_info.block_count);

    std::vector<std::byte> decoded;
    std::size_t decode_callbacks = 0;
    const bzip4::FrameInfo decoded_info = bzip4::decompress_frame_to(
        streamed, input.size(), [&](std::span<const std::byte> bytes) {
            ++decode_callbacks;
            CHECK(bytes.size() <= block);
            decoded.insert(decoded.end(), bytes.begin(), bytes.end());
        });
    CHECK(decoded == input);
    CHECK(decoded_info.original_size == input.size());
    CHECK(decoded_info.decoder_block_size == encoded_info.decoder_block_size);
    CHECK(decoded_info.decoder_workspace_bytes ==
          encoded_info.decoder_workspace_bytes);
    CHECK(decode_callbacks == decoded_info.block_count);

    check_throws<std::invalid_argument>([&] {
        const bzip4::FrameSink sink;
        (void)bzip4::compress_frame_to(input, block, sink);
    });
    check_throws<std::invalid_argument>([&] {
        const bzip4::FrameSink sink;
        (void)bzip4::decompress_frame_to(streamed, input.size(), sink);
    });

    auto bad_descriptor = streamed;
    const std::size_t second_descriptor = block_payload_offset(bad_descriptor, 1) - 8;
    write_u32(bad_descriptor, second_descriptor + 4, 0xffffffffU);
    std::size_t callbacks = 0;
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::decompress_frame_to(
            bad_descriptor, input.size(),
            [&](std::span<const std::byte>) { ++callbacks; });
    });
    CHECK(callbacks == 0); // Entire envelope is checked before publication.

    const auto many_empty = make_empty_block_frame(block, 4096);
    const auto empty_info = bzip4::inspect_frame(many_empty, 0);
    CHECK(empty_info.block_count == 4096);
    CHECK(empty_info.original_size == 0);
    CHECK(empty_info.decoder_workspace_bytes > 0);
    std::size_t empty_callbacks = 0;
    (void)bzip4::decompress_frame_to(
        many_empty, 0, [&](std::span<const std::byte>) { ++empty_callbacks; });
    CHECK(empty_callbacks == 0);
}

void test_range_backed_frames() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const auto input = pattern(static_cast<std::size_t>(block) * 2U + 37U);
    const auto materialized = bzip4::compress_frame(input, block);

    std::size_t input_reads = 0;
    std::size_t input_bytes = 0;
    std::size_t largest_input_read = 0;
    const bzip4::RangeReader input_reader = [&](std::uint64_t offset,
                                                 std::span<std::byte> output) {
        CHECK(offset <= input.size());
        CHECK(output.size() <= input.size() - static_cast<std::size_t>(offset));
        ++input_reads;
        input_bytes += output.size();
        largest_input_read = std::max(largest_input_read, output.size());
        if (!output.empty()) {
            std::memcpy(
                output.data(),
                input.data() + static_cast<std::ptrdiff_t>(offset),
                output.size());
        }
    };

    std::vector<std::byte> ranged_frame;
    const bzip4::FrameInfo ranged_info = bzip4::compress_frame_from(
        input.size(), block, input_reader,
        [&](std::span<const std::byte> bytes) {
            ranged_frame.insert(ranged_frame.end(), bytes.begin(), bytes.end());
        });
    CHECK(ranged_frame == materialized);
    CHECK(ranged_info.block_count == 3);
    CHECK(input_reads == ranged_info.block_count);
    CHECK(input_bytes == input.size());
    CHECK(largest_input_read == block);

    std::size_t inspect_reads = 0;
    std::size_t inspect_bytes = 0;
    std::size_t largest_inspect_read = 0;
    const bzip4::RangeReader frame_reader = [&](std::uint64_t offset,
                                                 std::span<std::byte> output) {
        CHECK(offset <= ranged_frame.size());
        CHECK(output.size() <= ranged_frame.size() - static_cast<std::size_t>(offset));
        ++inspect_reads;
        inspect_bytes += output.size();
        largest_inspect_read = std::max(largest_inspect_read, output.size());
        if (!output.empty()) {
            std::memcpy(
                output.data(),
                ranged_frame.data() + static_cast<std::ptrdiff_t>(offset),
                output.size());
        }
    };
    const bzip4::FrameInfo inspected = bzip4::inspect_frame_from(
        ranged_frame.size(), frame_reader, input.size());
    CHECK(inspected.block_count == ranged_info.block_count);
    CHECK(inspected.original_size == input.size());
    CHECK(inspect_reads == 1U + inspected.block_count);
    CHECK(largest_inspect_read <= 25);
    CHECK(inspect_bytes <= 13U + inspected.block_count * 25U);
    CHECK(inspect_bytes < ranged_frame.size());

    std::size_t decode_reads = 0;
    std::size_t largest_decode_read = 0;
    const bzip4::RangeReader decode_reader = [&](std::uint64_t offset,
                                                  std::span<std::byte> output) {
        CHECK(offset <= ranged_frame.size());
        CHECK(output.size() <= ranged_frame.size() - static_cast<std::size_t>(offset));
        ++decode_reads;
        largest_decode_read = std::max(largest_decode_read, output.size());
        if (!output.empty()) {
            std::memcpy(
                output.data(),
                ranged_frame.data() + static_cast<std::ptrdiff_t>(offset),
                output.size());
        }
    };
    std::vector<std::byte> decoded;
    const bzip4::FrameInfo decoded_info = bzip4::decompress_frame_from(
        ranged_frame.size(), decode_reader, input.size(),
        [&](std::span<const std::byte> bytes) {
            decoded.insert(decoded.end(), bytes.begin(), bytes.end());
        });
    CHECK(decoded == input);
    CHECK(decoded_info.original_size == input.size());
    CHECK(decode_reads == 1U + 3U * decoded_info.block_count);
    CHECK(largest_decode_read <= bzip4::frame_bound(block, block));
    CHECK(largest_decode_read < ranged_frame.size());

    // A shape-breaking descriptor change is rejected before that block's
    // payload is used. One decoded prefix may already reach a non-atomic sink.
    const std::size_t second_descriptor = block_payload_offset(ranged_frame, 1) - 8;
    const bzip4::RangeReader changing_reader = [&](std::uint64_t offset,
                                                    std::span<std::byte> output) {
        CHECK(offset <= ranged_frame.size());
        CHECK(output.size() <= ranged_frame.size() - static_cast<std::size_t>(offset));
        if (!output.empty()) {
            std::memcpy(
                output.data(),
                ranged_frame.data() + static_cast<std::ptrdiff_t>(offset),
                output.size());
        }
        // The validation pass reads descriptor + model prefix in one probe;
        // the second pass rereads the descriptor alone immediately before use.
        if (offset == second_descriptor && output.size() == 8) {
            write_u32(output, 4, 0xffffffffU);
        }
    };
    std::size_t changed_callbacks = 0;
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::decompress_frame_from(
            ranged_frame.size(), changing_reader, input.size(),
            [&](std::span<const std::byte>) { ++changed_callbacks; });
    });
    CHECK(changed_callbacks == 1);

    check_throws<std::invalid_argument>([&] {
        const bzip4::RangeReader reader;
        (void)bzip4::compress_frame_from(input.size(), block, reader, [](auto) {});
    });
    check_throws<std::invalid_argument>([&] {
        const bzip4::RangeReader reader;
        (void)bzip4::inspect_frame_from(ranged_frame.size(), reader, input.size());
    });

    std::size_t empty_source_reads = 0;
    std::vector<std::byte> empty_frame;
    const bzip4::FrameInfo empty_info = bzip4::compress_frame_from(
        0, block,
        [&](std::uint64_t, std::span<std::byte>) { ++empty_source_reads; },
        [&](std::span<const std::byte> bytes) {
            empty_frame.insert(empty_frame.end(), bytes.begin(), bytes.end());
        });
    CHECK(empty_source_reads == 0);
    CHECK(empty_info.block_count == 0);
    CHECK(empty_frame.size() == 13);

    // Descriptor pinning plus a final fingerprint check prevents a mixed source
    // snapshot from being published, even though encoding itself is streaming.
    TempDirectory directory;
    const auto source_path = directory.path() / "source.bin";
    const auto destination = directory.path() / "destination.bz3";
    const auto sentinel = pattern(91);
    write_file(source_path, input);
    write_file(destination, sentinel);
    bzip4::PinnedFile pinned(source_path);
    const int mutation_fd = ::open(source_path.c_str(), O_WRONLY | O_CLOEXEC);
    if (mutation_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open range mutation target");
    }
    {
        bzip4::AtomicFileWriter output(destination);
        std::size_t reads = 0;
        (void)bzip4::compress_frame_from(
            input.size(), block,
            [&](std::uint64_t offset, std::span<std::byte> bytes) {
                pinned.read_into(offset, bytes);
                ++reads;
                if (reads == 1) {
                    const std::byte replacement = std::byte{0x7f};
                    const ssize_t count = ::pwrite(mutation_fd, &replacement, 1, 0);
                    if (count != 1) {
                        throw std::system_error(
                            errno, std::generic_category(), "mutate range source");
                    }
                    if (::fsync(mutation_fd) != 0) {
                        throw std::system_error(
                            errno, std::generic_category(), "fsync range mutation");
                    }
                }
            },
            [&](std::span<const std::byte> bytes) { output.write(bytes); });
        CHECK(reads == ranged_info.block_count);
        check_throws<std::runtime_error>([&] { pinned.require_unchanged(); });
    }
    if (::close(mutation_fd) != 0) {
        throw std::system_error(errno, std::generic_category(), "close range mutation target");
    }
    CHECK(read_file(destination) == sentinel);
    CHECK(temporary_output_count(directory.path()) == 0);
}


void test_parallel_frame_encoder() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const auto input = pattern(static_cast<std::size_t>(block) * 7U + 137U);
    const auto scalar = bzip4::compress_frame(input, block);
    const std::size_t per_lane = bzip4::workspace_memory_bound(block);
    CHECK(per_lane > block);
    CHECK(bzip4::select_frame_block_size(block, input.size()) == block);

    bzip4::ParallelFramePolicy policy;
    policy.activation.retained_background_workers = 3;
    policy.activation.caller_participates = true;
    policy.activation.minimum_blocks_per_active_lane = 1;
    policy.activation.minimum_bytes_per_active_lane = 1;
    policy.max_workspace_bytes = per_lane * 4U;

    bzip4::ParallelFrameEncoder encoder(block, policy);
    CHECK(encoder.block_size() == block);
    CHECK(encoder.retained_background_workers() == 3);
    CHECK(encoder.retained_workspace_bytes() == per_lane * 4U);

    std::vector<std::byte> parallel;
    bzip4::ParallelFrameStats stats;
    const bzip4::FrameInfo info = encoder.encode_frame_to(
        input,
        [&](std::span<const std::byte> bytes) {
            parallel.insert(parallel.end(), bytes.begin(), bytes.end());
        },
        &stats);
    CHECK(parallel == scalar);
    CHECK(info.block_count == 8);
    CHECK(stats.activation.active_lanes == 4);
    CHECK(stats.productive_lanes == 4);
    CHECK(stats.batches == 2);
    CHECK(stats.peak_blocks_in_flight == 4);
    CHECK(stats.caller_blocks == 2);
    CHECK(stats.background_blocks == 6);
    CHECK(stats.background_notifications == 6);
    CHECK(stats.inactive_worker_wakeups == 0);
    const std::size_t first_generation = stats.generation;

    // The retained workspaces and threads remain reusable across calls.
    const auto second_input = pattern(static_cast<std::size_t>(block) * 2U + 19U);
    const auto second_scalar = bzip4::compress_frame(second_input, block);
    std::vector<std::byte> second_parallel;
    const bzip4::FrameInfo second_info = encoder.encode_frame_to(
        second_input,
        [&](std::span<const std::byte> bytes) {
            second_parallel.insert(second_parallel.end(), bytes.begin(), bytes.end());
        },
        &stats);
    CHECK(second_parallel == second_scalar);
    CHECK(second_info.block_count == 3);
    CHECK(stats.generation > first_generation);
    CHECK(stats.batches == 1);

    // Concurrent callers are serialized at the encoder boundary; retained
    // workspaces are never shared by two active calls.
    std::vector<std::byte> concurrent_first;
    std::vector<std::byte> concurrent_second;
    std::exception_ptr concurrent_error_first;
    std::exception_ptr concurrent_error_second;
    std::thread first_call([&] {
        try {
            (void)encoder.encode_frame_to(
                input,
                [&](std::span<const std::byte> bytes) {
                    concurrent_first.insert(
                        concurrent_first.end(), bytes.begin(), bytes.end());
                });
        } catch (...) {
            concurrent_error_first = std::current_exception();
        }
    });
    std::thread second_call([&] {
        try {
            (void)encoder.encode_frame_to(
                second_input,
                [&](std::span<const std::byte> bytes) {
                    concurrent_second.insert(
                        concurrent_second.end(), bytes.begin(), bytes.end());
                });
        } catch (...) {
            concurrent_error_second = std::current_exception();
        }
    });
    first_call.join();
    second_call.join();
    if (concurrent_error_first) std::rethrow_exception(concurrent_error_first);
    if (concurrent_error_second) std::rethrow_exception(concurrent_error_second);
    CHECK(concurrent_first == scalar);
    CHECK(concurrent_second == second_scalar);

    // A true floor grain can collapse a retained pool to one caller lane.
    bzip4::ParallelFramePolicy coarse = policy;
    coarse.activation.minimum_blocks_per_active_lane = 4;
    const auto five_blocks = pattern(static_cast<std::size_t>(block) * 4U + 1U);
    const auto five_scalar = bzip4::compress_frame(five_blocks, block);
    std::vector<std::byte> five_parallel;
    bzip4::ParallelFrameStats coarse_stats;
    bzip4::ParallelFrameEncoder coarse_encoder(block, coarse);
    (void)coarse_encoder.encode_frame_to(
        five_blocks,
        [&](std::span<const std::byte> bytes) {
            five_parallel.insert(five_parallel.end(), bytes.begin(), bytes.end());
        },
        &coarse_stats);
    CHECK(five_parallel == five_scalar);
    CHECK(coarse_stats.activation.active_lanes == 1);
    CHECK(coarse_stats.caller_blocks == 5);
    CHECK(coarse_stats.background_blocks == 0);
    CHECK(coarse_stats.background_notifications == 0);

    // all_retained is a deliberate wake-control experiment, not productive work.
    bzip4::ParallelFramePolicy broadcast = policy;
    broadcast.activation.max_active_lanes = 2;
    broadcast.activation.wake_mode = bzip4::WakeMode::all_retained;
    std::vector<std::byte> broadcast_frame;
    bzip4::ParallelFrameStats broadcast_stats;
    bzip4::ParallelFrameEncoder broadcast_encoder(block, broadcast);
    (void)broadcast_encoder.encode_frame_to(
        five_blocks,
        [&](std::span<const std::byte> bytes) {
            broadcast_frame.insert(broadcast_frame.end(), bytes.begin(), bytes.end());
        },
        &broadcast_stats);
    CHECK(broadcast_frame == five_scalar);
    CHECK(broadcast_stats.activation.active_lanes == 2);
    CHECK(broadcast_stats.batches == 3);
    CHECK(broadcast_stats.background_notifications == 9);
    CHECK(broadcast_stats.inactive_worker_wakeups == 7);

    // The guarded-reader profile guarantees that an otherwise non-thread-safe
    // callback is never entered concurrently while codec work still overlaps.
    bzip4::ParallelFramePolicy serialized = policy;
    serialized.serialize_range_reads = true;
    bzip4::ParallelFrameEncoder serialized_encoder(block, serialized);
    std::atomic<int> active_reads{0};
    std::atomic<int> maximum_reads{0};
    const bzip4::RangeReader serialized_reader = [&](std::uint64_t offset,
                                                       std::span<std::byte> output) {
        const int active = active_reads.fetch_add(1) + 1;
        int maximum = maximum_reads.load();
        while (active > maximum &&
               !maximum_reads.compare_exchange_weak(maximum, active)) {}
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        CHECK(offset <= input.size());
        CHECK(output.size() <= input.size() - static_cast<std::size_t>(offset));
        if (!output.empty()) {
            std::memcpy(output.data(),
                        input.data() + static_cast<std::ptrdiff_t>(offset),
                        output.size());
        }
        active_reads.fetch_sub(1);
    };
    std::vector<std::byte> serialized_frame;
    (void)serialized_encoder.encode_frame_from(
        input.size(), serialized_reader,
        [&](std::span<const std::byte> bytes) {
            serialized_frame.insert(serialized_frame.end(), bytes.begin(), bytes.end());
        });
    CHECK(serialized_frame == scalar);
    CHECK(maximum_reads.load() == 1);

    // A failed reader drains the batch and leaves the retained encoder usable.
    const bzip4::RangeReader failing_reader = [&](std::uint64_t offset,
                                                   std::span<std::byte> output) {
        if (offset == block) {
            throw std::runtime_error("intentional parallel reader failure");
        }
        CHECK(output.size() <= input.size() - static_cast<std::size_t>(offset));
        if (!output.empty()) {
            std::memcpy(output.data(),
                        input.data() + static_cast<std::ptrdiff_t>(offset),
                        output.size());
        }
    };
    std::vector<std::byte> failed_prefix;
    check_throws<std::runtime_error>([&] {
        (void)encoder.encode_frame_from(
            input.size(), failing_reader,
            [&](std::span<const std::byte> bytes) {
                failed_prefix.insert(failed_prefix.end(), bytes.begin(), bytes.end());
            });
    });
    CHECK(failed_prefix.size() == 13); // No result from the failed batch escaped.
    std::vector<std::byte> recovered;
    (void)encoder.encode_frame_to(
        input,
        [&](std::span<const std::byte> bytes) {
            recovered.insert(recovered.end(), bytes.begin(), bytes.end());
        });
    CHECK(recovered == scalar);

    // Sink failures happen only after workers are drained, so reuse is safe.
    std::size_t sink_calls = 0;
    check_throws<std::runtime_error>([&] {
        (void)encoder.encode_frame_to(
            input,
            [&](std::span<const std::byte>) {
                if (++sink_calls == 3) {
                    throw std::runtime_error("intentional parallel sink failure");
                }
            });
    });
    recovered.clear();
    (void)encoder.encode_frame_to(
        input,
        [&](std::span<const std::byte> bytes) {
            recovered.insert(recovered.end(), bytes.begin(), bytes.end());
        });
    CHECK(recovered == scalar);

    // Background-only execution remains ordered and byte-identical.
    bzip4::ParallelFramePolicy background_only = policy;
    background_only.activation.caller_participates = false;
    background_only.activation.retained_background_workers = 2;
    background_only.max_workspace_bytes = per_lane * 2U;
    bzip4::ParallelFrameEncoder background_encoder(block, background_only);
    std::vector<std::byte> background_frame;
    bzip4::ParallelFrameStats background_stats;
    (void)background_encoder.encode_frame_to(
        second_input,
        [&](std::span<const std::byte> bytes) {
            background_frame.insert(background_frame.end(), bytes.begin(), bytes.end());
        },
        &background_stats);
    CHECK(background_frame == second_scalar);
    CHECK(background_stats.caller_blocks == 0);
    CHECK(background_stats.background_blocks == second_info.block_count);

    check_throws<bzip4::CodecError>([&] {
        bzip4::ParallelFrameEncoder invalid_block(0, policy);
        (void)invalid_block;
    });
    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFramePolicy excessive = policy;
        excessive.activation.retained_background_workers = 257;
        excessive.max_workspace_bytes = std::numeric_limits<std::size_t>::max();
        bzip4::ParallelFrameEncoder rejected(block, excessive);
        (void)rejected;
    });

    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        bzip4::ParallelFramePolicy too_small = policy;
        too_small.max_workspace_bytes = per_lane * 4U - 1U;
        bzip4::ParallelFrameEncoder rejected(block, too_small);
        (void)rejected;
    });

    check_codec_error(BZ3_ERR_INIT, [&] {
        bzip4::ParallelFrameEncoder rejected(block - 1U, policy);
        (void)rejected;
    });
    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFramePolicy too_many = policy;
        too_many.activation.retained_background_workers = 257;
        too_many.max_workspace_bytes = std::numeric_limits<std::size_t>::max();
        bzip4::ParallelFrameEncoder rejected(block, too_many);
        (void)rejected;
    });

    // One-shot range-backed use caps retained workers that cannot be productive.
    bzip4::ParallelFramePolicy one_shot = policy;
    one_shot.activation.retained_background_workers = 31;
    one_shot.max_workspace_bytes = per_lane * 4U;
    std::vector<std::byte> one_shot_frame;
    bzip4::ParallelFrameStats one_shot_stats;
    (void)bzip4::compress_frame_parallel_to(
        second_input, block,
        [&](std::span<const std::byte> bytes) {
            one_shot_frame.insert(one_shot_frame.end(), bytes.begin(), bytes.end());
        },
        one_shot,
        &one_shot_stats);
    CHECK(one_shot_frame == second_scalar);
    CHECK(one_shot_stats.retained_background_workers == 2);

    // One-shot active-only use also applies max-lane/floor-grain policy before
    // charging workspaces, rather than retaining threads that this call cannot use.
    bzip4::ParallelFramePolicy activation_capped = policy;
    activation_capped.activation.retained_background_workers = 31;
    activation_capped.activation.max_active_lanes = 1;
    activation_capped.max_workspace_bytes = per_lane;
    std::vector<std::byte> activation_capped_frame;
    bzip4::ParallelFrameStats activation_capped_stats;
    (void)bzip4::compress_frame_parallel_to(
        input, block,
        [&](std::span<const std::byte> bytes) {
            activation_capped_frame.insert(
                activation_capped_frame.end(), bytes.begin(), bytes.end());
        },
        activation_capped,
        &activation_capped_stats);
    CHECK(activation_capped_frame == scalar);
    CHECK(activation_capped_stats.activation.active_lanes == 1);
    CHECK(activation_capped_stats.retained_background_workers == 0);
    CHECK(activation_capped_stats.retained_workspace_bytes == per_lane);

    // all_retained is an explicit one-shot wake-control experiment. Unlike
    // active_only, it preserves configured inactive workers so the control is
    // not silently rewritten before construction.
    bzip4::ParallelFramePolicy one_shot_broadcast = policy;
    one_shot_broadcast.activation.retained_background_workers = 3;
    one_shot_broadcast.activation.max_active_lanes = 2;
    one_shot_broadcast.activation.wake_mode = bzip4::WakeMode::all_retained;
    one_shot_broadcast.max_workspace_bytes = per_lane * 4U;
    std::vector<std::byte> one_shot_broadcast_frame;
    bzip4::ParallelFrameStats one_shot_broadcast_stats;
    (void)bzip4::compress_frame_parallel_to(
        five_blocks, block,
        [&](std::span<const std::byte> bytes) {
            one_shot_broadcast_frame.insert(
                one_shot_broadcast_frame.end(), bytes.begin(), bytes.end());
        },
        one_shot_broadcast,
        &one_shot_broadcast_stats);
    CHECK(one_shot_broadcast_frame == five_scalar);
    CHECK(one_shot_broadcast_stats.retained_background_workers == 3);
    CHECK(one_shot_broadcast_stats.background_notifications == 9);
    CHECK(one_shot_broadcast_stats.inactive_worker_wakeups == 7);

    // A one-shot empty frame needs no codec state or thread pool. A zero
    // workspace budget therefore remains valid, while a null reader is still
    // rejected as an invalid API argument.
    bzip4::ParallelFramePolicy empty_one_shot = policy;
    empty_one_shot.activation.retained_background_workers = 31;
    empty_one_shot.max_workspace_bytes = 0;
    std::size_t empty_one_shot_reads = 0;
    std::vector<std::byte> empty_one_shot_frame;
    bzip4::ParallelFrameStats empty_one_shot_stats;
    const bzip4::FrameInfo empty_one_shot_info =
        bzip4::compress_frame_parallel_from(
            0, block,
            [&](std::uint64_t, std::span<std::byte>) {
                ++empty_one_shot_reads;
            },
            [&](std::span<const std::byte> bytes) {
                empty_one_shot_frame.insert(
                    empty_one_shot_frame.end(), bytes.begin(), bytes.end());
            },
            empty_one_shot,
            &empty_one_shot_stats);
    CHECK(empty_one_shot_reads == 0);
    CHECK(empty_one_shot_info.block_count == 0);
    CHECK(empty_one_shot_frame.size() == 13);
    CHECK(empty_one_shot_frame == bzip4::compress_frame({}, block));
    CHECK(empty_one_shot_stats.retained_background_workers == 0);
    CHECK(empty_one_shot_stats.retained_lanes == 0);
    CHECK(empty_one_shot_stats.retained_workspace_bytes == 0);
    check_throws<std::invalid_argument>([&] {
        const bzip4::RangeReader null_reader;
        (void)bzip4::compress_frame_parallel_from(
            0, block, null_reader, [](std::span<const std::byte>) {}, empty_one_shot);
    });

    std::vector<std::byte> empty;
    bzip4::ParallelFrameStats empty_stats;
    (void)encoder.encode_frame_to(
        {},
        [&](std::span<const std::byte> bytes) {
            empty.insert(empty.end(), bytes.begin(), bytes.end());
        },
        &empty_stats);
    CHECK(empty.size() == 13);
    CHECK(empty_stats.activation.active_lanes == 0);
    CHECK(empty_stats.batches == 0);
}


void test_parallel_frame_decoder() {
    constexpr std::uint32_t block = bzip4::min_block_size;
    const std::size_t per_lane = bzip4::workspace_memory_bound(block);
    const auto input = pattern(static_cast<std::size_t>(block) * 7U + 137U);
    const auto encoded = bzip4::compress_frame(input, block);

    bzip4::ParallelFramePolicy policy;
    policy.activation.retained_background_workers = 3;
    policy.activation.max_active_lanes = 4;
    policy.activation.caller_participates = true;
    policy.activation.wake_mode = bzip4::WakeMode::active_only;
    policy.max_workspace_bytes = per_lane * 4U;

    bzip4::ParallelFrameDecoder decoder(block, policy);
    CHECK(decoder.block_size() == block);
    CHECK(decoder.retained_background_workers() == 3);
    CHECK(decoder.retained_workspace_bytes() == per_lane * 4U);

    std::vector<std::byte> output;
    bzip4::ParallelDecodeStats stats;
    const bzip4::FrameInfo info = decoder.decode_frame_to(
        encoded, input.size(),
        [&](std::span<const std::byte> bytes) {
            output.insert(output.end(), bytes.begin(), bytes.end());
        },
        true, &stats);
    CHECK(output == input);
    CHECK(info.block_count == 8);
    CHECK(stats.activation.active_lanes == 4);
    CHECK(stats.activation.active_background_workers == 3);
    CHECK(stats.retained_background_workers == 3);
    CHECK(stats.retained_lanes == 4);
    CHECK(stats.per_lane_workspace_bytes == per_lane);
    CHECK(stats.retained_workspace_bytes == per_lane * 4U);
    CHECK(stats.productive_lanes == 4);
    CHECK(stats.batches == 2);
    CHECK(stats.peak_blocks_in_flight == 4);
    CHECK(stats.background_notifications == 6);
    CHECK(stats.caller_blocks == 2);
    CHECK(stats.background_blocks == 6);
    CHECK(stats.inactive_worker_wakeups == 0);
    CHECK(stats.descriptor_reads == 8);
    CHECK(stats.generation == 2);

    // Retained decoder state and workers survive across frames of the same block size.
    const auto second_input = pattern(static_cast<std::size_t>(block) * 2U + 19U);
    const auto second_encoded = bzip4::compress_frame(second_input, block);
    std::vector<std::byte> second_output;
    bzip4::ParallelDecodeStats second_stats;
    (void)decoder.decode_frame_to(
        second_encoded, second_input.size(),
        [&](std::span<const std::byte> bytes) {
            second_output.insert(second_output.end(), bytes.begin(), bytes.end());
        },
        true, &second_stats);
    CHECK(second_output == second_input);
    CHECK(second_stats.batches == 1);
    CHECK(second_stats.caller_blocks == 1);
    CHECK(second_stats.background_blocks == 2);
    CHECK(second_stats.background_notifications == 2);
    CHECK(second_stats.descriptor_reads == 3);
    CHECK(second_stats.generation == 3);

    // Concurrent calls on one retained decoder serialize around shared arenas and
    // preserve each caller's independent publication order.
    const auto concurrent_a = pattern(static_cast<std::size_t>(block) + 31U);
    const auto concurrent_b = pattern(static_cast<std::size_t>(block) * 3U + 7U);
    const auto encoded_a = bzip4::compress_frame(concurrent_a, block);
    const auto encoded_b = bzip4::compress_frame(concurrent_b, block);
    std::vector<std::byte> output_a;
    std::vector<std::byte> output_b;
    std::exception_ptr error_a;
    std::exception_ptr error_b;
    std::thread thread_a([&] {
        try {
            (void)decoder.decode_frame_to(
                encoded_a, concurrent_a.size(),
                [&](std::span<const std::byte> bytes) {
                    output_a.insert(output_a.end(), bytes.begin(), bytes.end());
                });
        } catch (...) {
            error_a = std::current_exception();
        }
    });
    std::thread thread_b([&] {
        try {
            (void)decoder.decode_frame_to(
                encoded_b, concurrent_b.size(),
                [&](std::span<const std::byte> bytes) {
                    output_b.insert(output_b.end(), bytes.begin(), bytes.end());
                });
        } catch (...) {
            error_b = std::current_exception();
        }
    });
    thread_a.join();
    thread_b.join();
    if (error_a) std::rethrow_exception(error_a);
    if (error_b) std::rethrow_exception(error_b);
    CHECK(output_a == concurrent_a);
    CHECK(output_b == concurrent_b);

    // Decoder activation obeys the same true floor-grain contract as encoding.
    const auto five_input = pattern(static_cast<std::size_t>(block) * 4U + 1U);
    const auto five_encoded = bzip4::compress_frame(five_input, block);
    bzip4::ParallelFramePolicy floor_policy = policy;
    floor_policy.activation.minimum_blocks_per_active_lane = 4;
    bzip4::ParallelFrameDecoder floor_decoder(block, floor_policy);
    std::vector<std::byte> floor_output;
    bzip4::ParallelDecodeStats floor_stats;
    (void)floor_decoder.decode_frame_to(
        five_encoded, five_input.size(),
        [&](std::span<const std::byte> bytes) {
            floor_output.insert(floor_output.end(), bytes.begin(), bytes.end());
        },
        true, &floor_stats);
    CHECK(floor_output == five_input);
    CHECK(floor_stats.activation.active_lanes == 1);
    CHECK(floor_stats.background_notifications == 0);
    CHECK(floor_stats.caller_blocks == 5);
    CHECK(floor_stats.background_blocks == 0);
    CHECK(floor_stats.batches == 5);

    // all_retained is still a measurable broadcast control rather than an alias
    // for productive-only wakeups.
    bzip4::ParallelFramePolicy broadcast_policy = policy;
    broadcast_policy.activation.wake_mode = bzip4::WakeMode::all_retained;
    bzip4::ParallelFrameDecoder broadcast_decoder(block, broadcast_policy);
    std::vector<std::byte> broadcast_output;
    bzip4::ParallelDecodeStats broadcast_stats;
    (void)broadcast_decoder.decode_frame_to(
        second_encoded, second_input.size(),
        [&](std::span<const std::byte> bytes) {
            broadcast_output.insert(broadcast_output.end(), bytes.begin(), bytes.end());
        },
        true, &broadcast_stats);
    CHECK(broadcast_output == second_input);
    CHECK(broadcast_stats.background_notifications == 3);
    CHECK(broadcast_stats.inactive_worker_wakeups == 1);

    // Range-backed payload reads overlap when permitted and are serialized when
    // the policy wraps a source that cannot tolerate concurrent callbacks.
    auto concurrency_reader = [&](std::atomic<int>& active,
                                  std::atomic<int>& peak) -> bzip4::RangeReader {
        return [&](std::uint64_t offset, std::span<std::byte> bytes) {
            const std::size_t position = static_cast<std::size_t>(offset);
            if (static_cast<std::uint64_t>(position) != offset ||
                position > encoded.size() || bytes.size() > encoded.size() - position) {
                throw std::out_of_range("parallel decoder test range outside frame");
            }
            if (bytes.size() > 25) {
                const int now = active.fetch_add(1) + 1;
                int observed = peak.load();
                while (observed < now &&
                       !peak.compare_exchange_weak(observed, now)) {}
                std::this_thread::sleep_for(std::chrono::milliseconds(4));
                std::memmove(bytes.data(),
                             encoded.data() + static_cast<std::ptrdiff_t>(position),
                             bytes.size());
                (void)active.fetch_sub(1);
            } else if (!bytes.empty()) {
                std::memmove(bytes.data(),
                             encoded.data() + static_cast<std::ptrdiff_t>(position),
                             bytes.size());
            }
        };
    };

    std::atomic<int> active_reads{0};
    std::atomic<int> peak_reads{0};
    std::vector<std::byte> concurrent_output;
    const bzip4::RangeReader concurrent_reader =
        concurrency_reader(active_reads, peak_reads);
    (void)decoder.decode_frame_from(
        encoded.size(), concurrent_reader, input.size(),
        [&](std::span<const std::byte> bytes) {
            concurrent_output.insert(concurrent_output.end(), bytes.begin(), bytes.end());
        });
    CHECK(concurrent_output == input);
    CHECK(peak_reads.load() >= 2);

    bzip4::ParallelFramePolicy serialized_policy = policy;
    serialized_policy.serialize_range_reads = true;
    bzip4::ParallelFrameDecoder serialized_decoder(block, serialized_policy);
    active_reads.store(0);
    peak_reads.store(0);
    std::vector<std::byte> serialized_output;
    const bzip4::RangeReader serialized_source =
        concurrency_reader(active_reads, peak_reads);
    (void)serialized_decoder.decode_frame_from(
        encoded.size(), serialized_source, input.size(),
        [&](std::span<const std::byte> bytes) {
            serialized_output.insert(serialized_output.end(), bytes.begin(), bytes.end());
        });
    CHECK(serialized_output == input);
    CHECK(peak_reads.load() == 1);

    // A background-only profile remains useful when the coordinating caller
    // should be reserved solely for ordered publication.
    bzip4::ParallelFramePolicy background_only = policy;
    background_only.activation.retained_background_workers = 4;
    background_only.activation.caller_participates = false;
    background_only.max_workspace_bytes = per_lane * 4U;
    bzip4::ParallelFrameDecoder background_decoder(block, background_only);
    std::vector<std::byte> background_output;
    bzip4::ParallelDecodeStats background_stats;
    (void)background_decoder.decode_frame_to(
        encoded, input.size(),
        [&](std::span<const std::byte> bytes) {
            background_output.insert(background_output.end(), bytes.begin(), bytes.end());
        },
        true, &background_stats);
    CHECK(background_output == input);
    CHECK(background_stats.caller_blocks == 0);
    CHECK(background_stats.background_blocks == 8);
    CHECK(background_stats.background_notifications == 8);

    // A worker-side reader failure drains the entire batch before rethrowing and
    // leaves the retained decoder reusable.
    const std::size_t failing_payload = block_payload_offset(encoded, 1);
    const bzip4::RangeReader failing_reader =
        [&](std::uint64_t offset, std::span<std::byte> bytes) {
            const std::size_t position = static_cast<std::size_t>(offset);
            if (position == failing_payload && bytes.size() > 25) {
                throw std::runtime_error("intentional parallel decode read failure");
            }
            CHECK(static_cast<std::uint64_t>(position) == offset);
            CHECK(position <= encoded.size());
            CHECK(bytes.size() <= encoded.size() - position);
            if (!bytes.empty()) {
                std::memmove(bytes.data(),
                             encoded.data() + static_cast<std::ptrdiff_t>(position),
                             bytes.size());
            }
        };
    check_throws<std::runtime_error>([&] {
        (void)decoder.decode_frame_from(
            encoded.size(), failing_reader, input.size(),
            [](std::span<const std::byte>) {});
    });
    std::vector<std::byte> after_reader_failure;
    (void)decoder.decode_frame_to(
        second_encoded, second_input.size(),
        [&](std::span<const std::byte> bytes) {
            after_reader_failure.insert(
                after_reader_failure.end(), bytes.begin(), bytes.end());
        });
    CHECK(after_reader_failure == second_input);

    // Corrupt payload and sink failures are also fully drained before the pool is
    // reused. The sink sees no workspace span after its callback returns.
    auto corrupt = encoded;
    corrupt[block_payload_offset(corrupt, 2)] ^= std::byte{0x40};
    check_throws<bzip4::CodecError>([&] {
        (void)decoder.decode_frame_to(
            corrupt, input.size(), [](std::span<const std::byte>) {});
    });
    std::size_t sink_calls = 0;
    check_throws<std::runtime_error>([&] {
        (void)decoder.decode_frame_to(
            encoded, input.size(),
            [&](std::span<const std::byte>) {
                ++sink_calls;
                throw std::runtime_error("intentional parallel decode sink failure");
            });
    });
    CHECK(sink_calls == 1);
    std::vector<std::byte> after_sink_failure;
    (void)decoder.decode_frame_to(
        second_encoded, second_input.size(),
        [&](std::span<const std::byte> bytes) {
            after_sink_failure.insert(
                after_sink_failure.end(), bytes.begin(), bytes.end());
        });
    CHECK(after_sink_failure == second_input);

    // One-shot active-only decoding trims workers before charging retained state.
    bzip4::ParallelFramePolicy one_lane_policy = policy;
    one_lane_policy.activation.retained_background_workers = 31;
    one_lane_policy.activation.max_active_lanes = 1;
    one_lane_policy.max_workspace_bytes = per_lane;
    std::vector<std::byte> one_lane_output;
    bzip4::ParallelDecodeStats one_lane_stats;
    (void)bzip4::decompress_frame_parallel_to(
        second_encoded, second_input.size(),
        [&](std::span<const std::byte> bytes) {
            one_lane_output.insert(one_lane_output.end(), bytes.begin(), bytes.end());
        },
        one_lane_policy, true, &one_lane_stats);
    CHECK(one_lane_output == second_input);
    CHECK(one_lane_stats.retained_background_workers == 0);
    CHECK(one_lane_stats.retained_lanes == 1);
    CHECK(one_lane_stats.retained_workspace_bytes == per_lane);

    // Empty one-shot frames need no worker or codec state, even at a zero budget.
    const auto empty_frame = bzip4::compress_frame({}, block);
    bzip4::ParallelFramePolicy empty_policy = policy;
    empty_policy.activation.retained_background_workers = 31;
    empty_policy.max_workspace_bytes = 0;
    std::size_t empty_callbacks = 0;
    bzip4::ParallelDecodeStats empty_stats;
    const bzip4::FrameInfo empty_info = bzip4::decompress_frame_parallel_to(
        empty_frame, 0,
        [&](std::span<const std::byte>) { ++empty_callbacks; },
        empty_policy, true, &empty_stats);
    CHECK(empty_info.block_count == 0);
    CHECK(empty_callbacks == 0);
    CHECK(empty_stats.activation.active_lanes == 0);
    CHECK(empty_stats.retained_background_workers == 0);
    CHECK(empty_stats.retained_lanes == 0);
    CHECK(empty_stats.retained_workspace_bytes == 0);

    // The bounded descriptor cursor catches a changed post-scan descriptor before
    // dispatching the batch or publishing decoded output.
    std::size_t cursor_reads = 0;
    std::size_t changed_callbacks = 0;
    const std::size_t second_descriptor =
        block_payload_offset(encoded, 1) - 8U;
    const bzip4::RangeReader changing_reader =
        [&](std::uint64_t offset, std::span<std::byte> bytes) {
            const std::size_t position = static_cast<std::size_t>(offset);
            CHECK(static_cast<std::uint64_t>(position) == offset);
            CHECK(position <= encoded.size());
            CHECK(bytes.size() <= encoded.size() - position);
            if (!bytes.empty()) {
                std::memmove(bytes.data(),
                             encoded.data() + static_cast<std::ptrdiff_t>(position),
                             bytes.size());
            }
            if (position == second_descriptor) {
                ++cursor_reads;
                if (cursor_reads == 2 && bytes.size() >= 4) {
                    write_u32(bytes, 0, 0x7fffffffU);
                }
            }
        };
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::decompress_frame_parallel_from(
            encoded.size(), changing_reader, input.size(),
            [&](std::span<const std::byte>) { ++changed_callbacks; },
            policy);
    });
    CHECK(changed_callbacks == 0);

    // Output and trailing-byte policies are enforced by the complete envelope
    // pass before the first decoded callback.
    std::size_t budget_callbacks = 0;
    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        (void)decoder.decode_frame_to(
            encoded, input.size() - 1U,
            [&](std::span<const std::byte>) { ++budget_callbacks; });
    });
    CHECK(budget_callbacks == 0);

    auto trailing_frame = encoded;
    trailing_frame.push_back(std::byte{0x7f});
    std::size_t trailing_callbacks = 0;
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)decoder.decode_frame_to(
            trailing_frame, input.size(),
            [&](std::span<const std::byte>) { ++trailing_callbacks; });
    });
    CHECK(trailing_callbacks == 0);
    std::vector<std::byte> trailing_output;
    const bzip4::FrameInfo trailing_info = decoder.decode_frame_to(
        trailing_frame, input.size(),
        [&](std::span<const std::byte> bytes) {
            trailing_output.insert(trailing_output.end(), bytes.begin(), bytes.end());
        },
        false);
    CHECK(trailing_info.trailing_bytes == 1);
    CHECK(trailing_output == input);

    // A retained decoder is intentionally fixed to one block-size workspace.
    const auto larger_input = pattern(static_cast<std::size_t>(block) * 3U + 9U);
    const auto larger_block_frame = bzip4::compress_frame(larger_input, block * 2U);
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)decoder.decode_frame_to(
            larger_block_frame, larger_input.size(),
            [](std::span<const std::byte>) {});
    });

    check_codec_error(BZ3_ERR_INIT, [&] {
        bzip4::ParallelFrameDecoder invalid(bzip4::min_block_size - 1U, policy);
        (void)invalid;
    });
    bzip4::ParallelFramePolicy tight = policy;
    tight.max_workspace_bytes = per_lane * 4U - 1U;
    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        bzip4::ParallelFrameDecoder invalid(block, tight);
        (void)invalid;
    });
    bzip4::ParallelFramePolicy excessive = policy;
    excessive.activation.retained_background_workers = 257;
    excessive.max_workspace_bytes = std::numeric_limits<std::size_t>::max();
    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFrameDecoder invalid(block, excessive);
        (void)invalid;
    });
    check_throws<std::invalid_argument>([&] {
        (void)bzip4::decompress_frame_parallel_to(
            empty_frame, 0, [](std::span<const std::byte>) {}, excessive);
    });
    bzip4::ParallelFramePolicy executorless;
    executorless.activation.caller_participates = false;
    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFrameDecoder invalid(block, executorless);
        (void)invalid;
    });
    const bzip4::RangeReader null_reader;
    check_throws<std::invalid_argument>([&] {
        (void)decoder.decode_frame_from(
            encoded.size(), null_reader, input.size(),
            [](std::span<const std::byte>) {});
    });
    const bzip4::FrameSink null_sink;
    check_throws<std::invalid_argument>([&] {
        (void)decoder.decode_frame_to(encoded, input.size(), null_sink);
    });
}

void test_frame_workspace_contraction() {
    // The buffer bound, not the raw payload/intermediate byte count, determines
    // the smallest state size. Exercise the exact inverse-bound boundary and
    // prove invalid requirements are never silently clamped.
    bzip4::detail::DecoderWorkspaceRequirements inverse_requirements{
        bzip4::min_block_size,
        bz3_bound(bzip4::min_block_size) + 1U,
    };
    const std::uint32_t inverse_selected =
        bzip4::detail::select_decoder_block_size(
            inverse_requirements, bzip4::min_block_size + 4096U);
    CHECK(inverse_selected > bzip4::min_block_size);
    CHECK(bz3_bound(inverse_selected) >= inverse_requirements.bound_extent);
    CHECK(bz3_bound(inverse_selected - 1U) < inverse_requirements.bound_extent);
    CHECK(inverse_selected < inverse_requirements.bound_extent);

    bzip4::detail::DecoderWorkspaceRequirements invalid_direct{
        static_cast<std::size_t>(bzip4::min_block_size) + 1U, 0U};
    CHECK(bzip4::detail::select_decoder_block_size(
        invalid_direct, bzip4::min_block_size) == 0U);
    bzip4::detail::DecoderWorkspaceRequirements invalid_bound{
        0U, bz3_bound(bzip4::min_block_size) + 1U};
    CHECK(bzip4::detail::select_decoder_block_size(
        invalid_bound, bzip4::min_block_size) == 0U);

    // Every transform model must produce the same compact planning result in
    // the encoder, shared inspector, scalar decoder, and low-level decoder.
    constexpr std::uint32_t model_block_size = 70000U;
    const std::size_t model_input_size = model_block_size - 31U;
    const std::array<std::pair<std::vector<std::byte>, std::uint8_t>, 4> model_cases{{
        {pattern(model_input_size), 0U},
        {repeated_text(model_input_size, 27U), 2U},
        {random_runs(model_input_size, 8U, 127U), 4U},
        {std::vector<std::byte>(model_input_size, std::byte{0}), 6U},
    }};
    bzip4::Workspace model_encoder(model_block_size);
    for (const auto& [model_input, expected_model] : model_cases) {
        const std::span<const std::byte> encoded_view =
            model_encoder.encode_block_view(model_input);
        CHECK(block_model({
            reinterpret_cast<const std::uint8_t*>(encoded_view.data()),
            encoded_view.size()}) == expected_model);
        const std::vector<std::byte> encoded_block(
            encoded_view.begin(), encoded_view.end());

        std::vector<std::byte> model_frame;
        append_text(model_frame, "BZ3v1");
        append_u32(model_frame, bzip4::max_block_size);
        append_u32(model_frame, 1U);
        append_u32(model_frame, static_cast<std::uint32_t>(encoded_block.size()));
        append_u32(model_frame, static_cast<std::uint32_t>(model_input.size()));
        model_frame.insert(
            model_frame.end(), encoded_block.begin(), encoded_block.end());

        const bzip4::detail::BlockEnvelopeValidation envelope =
            bzip4::detail::validate_block_envelope(
                encoded_block.size(),
                {reinterpret_cast<const std::uint8_t*>(encoded_block.data()),
                 encoded_block.size()},
                model_input.size(), bzip4::max_block_size);
        CHECK(envelope.error_code == BZ3_OK);
        bzip4::detail::DecoderWorkspaceRequirements model_requirements;
        bzip4::detail::merge_decoder_requirements(
            model_requirements, envelope);
        const std::uint32_t selected =
            bzip4::detail::select_decoder_block_size(
                model_requirements, bzip4::max_block_size);
        CHECK(selected >= model_input.size());
        CHECK(selected < bzip4::max_block_size);
        CHECK(bz3_bound(selected) >= model_requirements.bound_extent);

        const bzip4::FrameInfo model_info =
            bzip4::inspect_frame(model_frame, model_input.size());
        CHECK(model_info.decoder_block_size == selected);
        CHECK(model_info.decoder_workspace_bytes ==
              bzip4::workspace_memory_bound(selected));
        CHECK(bzip4::decompress_frame(model_frame, model_input.size()) ==
              model_input);
    }

    constexpr std::uint32_t encoded_block_size = 100000U;
    const auto input = pattern(350000U);
    auto frame = bzip4::compress_frame(input, encoded_block_size);
    CHECK(read_u32(frame, 5) == encoded_block_size);
    CHECK(read_u32(frame, 9) == 4U);

    // A BZ3v1 declaration is an upper bound. Inflate it without changing any
    // block payload or descriptor; the shared envelope planner must derive the
    // smallest legal decoder state from the actual validated extents.
    write_u32(frame, 5, bzip4::max_block_size);
    const bzip4::FrameInfo info = bzip4::inspect_frame(frame, input.size());
    CHECK(info.block_size == bzip4::max_block_size);
    CHECK(info.decoder_block_size >= bzip4::min_block_size);
    CHECK(info.decoder_block_size < bzip4::max_block_size);
    CHECK(info.decoder_workspace_bytes ==
          bzip4::workspace_memory_bound(info.decoder_block_size));

    bzip4::detail::DecoderWorkspaceRequirements expected_requirements;
    std::size_t cursor = 13;
    for (std::uint32_t index = 0; index < info.block_count; ++index) {
        const std::size_t compressed = read_u32(frame, cursor);
        const std::size_t original = read_u32(frame, cursor + 4U);
        cursor += 8U;
        CHECK(compressed <= frame.size() - cursor);
        const auto* payload = reinterpret_cast<const std::uint8_t*>(
            frame.data() + static_cast<std::ptrdiff_t>(cursor));
        const bzip4::detail::BlockEnvelopeValidation envelope =
            bzip4::detail::validate_block_envelope(
                compressed, {payload, compressed}, original,
                bzip4::max_block_size);
        CHECK(envelope.error_code == BZ3_OK);
        bzip4::detail::merge_decoder_requirements(
            expected_requirements, envelope);
        cursor += compressed;
    }
    CHECK(cursor == frame.size());
    CHECK(info.decoder_block_size == bzip4::detail::select_decoder_block_size(
        expected_requirements, bzip4::max_block_size));

    CHECK(bzip4::decompress_frame(frame, input.size()) == input);
    std::vector<std::uint8_t> c_output(input.size());
    std::size_t c_output_size = c_output.size();
    CHECK(bz3_decompress(
        reinterpret_cast<const std::uint8_t*>(frame.data()), c_output.data(),
        frame.size(), &c_output_size) == BZ3_OK);
    CHECK(c_output_size == input.size());
    CHECK(std::memcmp(c_output.data(), input.data(), input.size()) == 0);

    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        (void)bzip4::inspect_frame(
            frame, input.size(), true, info.decoder_workspace_bytes - 1U);
    });

    bzip4::ParallelFramePolicy policy;
    policy.activation.retained_background_workers = 3;
    policy.activation.max_active_lanes = 4;
    policy.activation.caller_participates = true;
    policy.activation.wake_mode = bzip4::WakeMode::active_only;
    policy.max_workspace_bytes = info.decoder_workspace_bytes * 4U;

    std::vector<std::byte> one_shot_output;
    bzip4::ParallelDecodeStats one_shot_stats;
    const bzip4::FrameInfo one_shot_info = bzip4::decompress_frame_parallel_to(
        frame, input.size(),
        [&](std::span<const std::byte> bytes) {
            one_shot_output.insert(one_shot_output.end(), bytes.begin(), bytes.end());
        },
        policy, true, &one_shot_stats);
    CHECK(one_shot_output == input);
    CHECK(one_shot_info.decoder_block_size == info.decoder_block_size);
    CHECK(one_shot_stats.retained_lanes == 4U);
    CHECK(one_shot_stats.per_lane_workspace_bytes == info.decoder_workspace_bytes);
    CHECK(one_shot_stats.retained_workspace_bytes ==
          info.decoder_workspace_bytes * 4U);

    bzip4::ParallelFrameDecoder compact(
        bzip4::max_block_size, info.decoder_block_size, policy);
    CHECK(compact.block_size() == bzip4::max_block_size);
    CHECK(compact.decoder_block_size() == info.decoder_block_size);
    CHECK(compact.retained_workspace_bytes() ==
          info.decoder_workspace_bytes * 4U);
    std::vector<std::byte> compact_output;
    (void)compact.decode_frame_to(
        frame, input.size(),
        [&](std::span<const std::byte> bytes) {
            compact_output.insert(compact_output.end(), bytes.begin(), bytes.end());
        });
    CHECK(compact_output == input);

    bzip4::ParallelFramePolicy undersized_policy = policy;
    const std::size_t undersized_per_lane =
        bzip4::workspace_memory_bound(bzip4::min_block_size);
    undersized_policy.max_workspace_bytes = undersized_per_lane * 4U;
    bzip4::ParallelFrameDecoder undersized(
        bzip4::max_block_size, bzip4::min_block_size, undersized_policy);
    std::size_t callbacks = 0;
    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        (void)undersized.decode_frame_to(
            frame, input.size(),
            [&](std::span<const std::byte>) { ++callbacks; });
    });
    CHECK(callbacks == 0);

    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFrameDecoder invalid(
            encoded_block_size, encoded_block_size + 1U, policy);
        (void)invalid;
    });
    check_throws<std::invalid_argument>([&] {
        bzip4::ParallelFrameDecoder invalid(
            encoded_block_size, bzip4::min_block_size - 1U, policy);
        (void)invalid;
    });
    check_codec_error(BZ3_ERR_INIT, [&] {
        bzip4::ParallelFrameDecoder invalid(
            bzip4::min_block_size - 1U, bzip4::min_block_size, policy);
        (void)invalid;
    });
}


void test_resource_planning() {
    constexpr std::uint32_t block_size = 4U * 1024U * 1024U;
    const std::size_t per_lane = bzip4::workspace_memory_bound(block_size);

    const auto empty = bzip4::plan_parallel_compression(
        0, block_size, 8, 0);
    CHECK(empty.input_bytes == 0);
    CHECK(empty.effective_block_size == bzip4::min_block_size);
    CHECK(empty.parallel.block_count == 0);
    CHECK(empty.parallel.selected_lanes == 0);
    CHECK(empty.parallel.selected_workspace_bytes == 0);
    CHECK(empty.parallel.fits);

    constexpr std::size_t input_size = 10U * 1024U * 1024U;
    const auto strict = bzip4::plan_parallel_compression(
        input_size, block_size, 8, per_lane * 8U);
    CHECK(strict.effective_block_size == block_size);
    CHECK(strict.parallel.block_count == 3);
    CHECK(strict.parallel.work_limited_lanes == 3);
    CHECK(strict.parallel.selected_lanes == 3);
    CHECK(strict.parallel.strict_workspace_bytes == per_lane * 3U);
    CHECK(strict.parallel.selected_workspace_bytes == per_lane * 3U);
    CHECK(strict.parallel.limited_by_work);
    CHECK(!strict.parallel.limited_by_workspace);
    CHECK(strict.parallel.fits);

    const auto fitted = bzip4::plan_parallel_compression(
        input_size, block_size, 8, per_lane * 2U);
    CHECK(fitted.parallel.selected_lanes == 2);
    CHECK(fitted.parallel.workspace_lane_capacity == 2);
    CHECK(fitted.parallel.selected_workspace_bytes == per_lane * 2U);
    CHECK(fitted.parallel.limited_by_workspace);
    CHECK(fitted.parallel.fits);

    const auto impossible = bzip4::plan_parallel_compression(
        input_size, block_size, 8, per_lane - 1U);
    CHECK(impossible.parallel.selected_lanes == 0);
    CHECK(impossible.parallel.limited_by_workspace);
    CHECK(!impossible.parallel.fits);

    check_throws<std::invalid_argument>([&] {
        (void)bzip4::plan_parallel_compression(input_size, block_size, 0, per_lane);
    });
    check_throws<std::invalid_argument>([&] {
        (void)bzip4::plan_parallel_compression(
            input_size, block_size, bzip4::maximum_parallel_lanes + 1U, per_lane);
    });

    const auto plain = repeated_text(3U * 1024U * 1024U + 137U, 33);
    const auto encoded = bzip4::compress_frame(plain, 1024U * 1024U);
    CHECK(encoded == bzip4::compress_frame_upstream_exact(plain, 1024U * 1024U));
    CHECK(bzip4::decompress_frame(encoded, plain.size()) == plain);
    const auto info = bzip4::inspect_frame(encoded, plain.size());
    const std::size_t decoder_lane = bzip4::workspace_memory_bound(info.decoder_block_size);
    const auto decode = bzip4::plan_parallel_decompression(
        info, 8, decoder_lane * 2U);
    CHECK(decode.block_count == info.block_count);
    CHECK(decode.selected_lanes == std::min<std::size_t>(2U, info.block_count));
    CHECK(decode.selected_workspace_bytes == decoder_lane * decode.selected_lanes);
    CHECK(decode.fits);

    auto inconsistent = info;
    ++inconsistent.decoder_workspace_bytes;
    check_throws<std::invalid_argument>([&] {
        (void)bzip4::plan_parallel_decompression(inconsistent, 1, decoder_lane);
    });
}

void test_codec_profiles() {
    const auto profiles = bzip4::codec_profiles();
    CHECK(profiles.size() == 3U);
    CHECK(profiles[0].id == "datacube-capsule-speed-v1");
    CHECK(profiles[0].requested_block_size == 256U * 1024U);
    CHECK(profiles[1].id == "cloudtainer-speed-v1");
    CHECK(profiles[1].requested_block_size == 1024U * 1024U);
    CHECK(profiles[2].id == "cloudtainer-balanced-v1");
    CHECK(profiles[2].requested_block_size == 2U * 1024U * 1024U);

    for (const bzip4::CodecProfile& profile : profiles) {
        CHECK(&bzip4::codec_profile(profile.id) == &profile);
        CHECK(profile.requested_lanes == 8U);
        CHECK(profile.default_workspace_bytes ==
              bzip4::profile_default_workspace_bytes);
        CHECK(profile.requested_block_size >= bzip4::min_block_size);
        CHECK(profile.requested_block_size <= bzip4::max_block_size);
    }
    check_throws<std::invalid_argument>([] {
        (void)bzip4::codec_profile("not-a-profile");
    });

    const bzip4::CodecProfile& speed =
        bzip4::codec_profile("cloudtainer-speed-v1");
    CHECK(bzip4::profile_effective_block_size(speed, 0) == bzip4::min_block_size);
    CHECK(bzip4::profile_effective_block_size(speed, 100U) == bzip4::min_block_size);
    CHECK(bzip4::profile_effective_block_size(speed, 131072U) ==
          static_cast<std::uint32_t>(bz3_bound(131072U)));
    CHECK(bzip4::profile_effective_block_size(speed, 400000U) ==
          static_cast<std::uint32_t>(bz3_bound(400000U)));
    CHECK(bzip4::profile_effective_block_size(speed, 4U * 1024U * 1024U) ==
          1024U * 1024U);

    const auto input = repeated_text(3U * 1024U * 1024U + 101U, 340);
    const auto speed_frame = bzip4::compress_frame(input, speed.requested_block_size);
    const auto speed_info = bzip4::inspect_frame(speed_frame, input.size());
    CHECK(bzip4::frame_is_compatible_with_profile(speed_info, speed));
    CHECK(!bzip4::frame_is_compatible_with_profile(speed_info, profiles[0]));
    CHECK(!bzip4::frame_is_compatible_with_profile(speed_info, profiles[2]));
    CHECK(bzip4::decompress_frame(speed_frame, input.size()) == input);

    const auto plan = bzip4::plan_parallel_compression(
        input.size(), speed.requested_block_size, speed.requested_lanes,
        speed.default_workspace_bytes);
    CHECK(plan.parallel.fits);
    CHECK(plan.parallel.selected_lanes == 4U);
    CHECK(plan.parallel.selected_workspace_bytes < speed.default_workspace_bytes);
}

void test_atomic_output() {
    TempDirectory directory;
    const auto destination = directory.path() / "result.bin";
    const auto sentinel = pattern(97);
    write_file(destination, sentinel);

    {
        bzip4::AtomicFileWriter output(destination);
        output.write(as_bytes("uncommitted replacement"));
        CHECK(output.bytes_written() == 23);
        CHECK(!output.published());
    }
    CHECK(read_file(destination) == sentinel);
    CHECK(temporary_output_count(directory.path()) == 0);

    {
        bzip4::AtomicFileWriter output(destination);
        output.write(as_bytes("committed "));
        output.write(as_bytes("replacement"));
        CHECK(output.bytes_written() == 21);
        output.commit();
        CHECK(output.published());
        CHECK(output.durable());
        check_throws<std::logic_error>([&] { output.write(as_bytes("x")); });
        check_throws<std::logic_error>([&] { output.commit(); });
    }
    CHECK(read_file(destination) ==
          std::vector<std::byte>(as_bytes("committed replacement").begin(),
                                 as_bytes("committed replacement").end()));
    CHECK(temporary_output_count(directory.path()) == 0);

    constexpr std::uint32_t block = bzip4::min_block_size;
    const auto input = pattern(static_cast<std::size_t>(block) + 100U);
    write_file(destination, sentinel);
    std::size_t compression_callbacks = 0;
    {
        bzip4::AtomicFileWriter output(destination);
        check_throws<std::runtime_error>([&] {
            (void)bzip4::compress_frame_to(
                input, block, [&](std::span<const std::byte> bytes) {
                    output.write(bytes);
                    ++compression_callbacks;
                    if (compression_callbacks == 4) {
                        throw std::runtime_error("injected compression sink failure");
                    }
                });
        });
    }
    CHECK(compression_callbacks == 4);
    CHECK(read_file(destination) == sentinel);
    CHECK(temporary_output_count(directory.path()) == 0);

    auto corrupted = bzip4::compress_frame(input, block);
    const std::size_t second_payload = block_payload_offset(corrupted, 1);
    corrupted[second_payload] ^= std::byte{0x01}; // Late second-block CRC mismatch.
    write_file(destination, sentinel);
    std::size_t decoded_callbacks = 0;
    {
        bzip4::AtomicFileWriter output(destination);
        check_codec_error(BZ3_ERR_CRC, [&] {
            (void)bzip4::decompress_frame_to(
                corrupted, input.size(), [&](std::span<const std::byte> bytes) {
                    ++decoded_callbacks;
                    output.write(bytes);
                });
        });
    }
    CHECK(decoded_callbacks == 1);
    CHECK(read_file(destination) == sentinel);
    CHECK(temporary_output_count(directory.path()) == 0);
}

void test_pinned_input() {
    TempDirectory directory;
    const auto target = directory.path() / "input.bin";
    const auto original = pattern(1024);
    write_file(target, original);

    {
        bzip4::PinnedFile pinned(target);
        CHECK(pinned.size() == original.size());
        const auto range = pinned.read(100, 200);
        CHECK(std::equal(range.begin(), range.end(), original.begin() + 100));
        std::array<std::byte, 200> direct{};
        pinned.read_into(100, direct);
        CHECK(std::equal(direct.begin(), direct.end(), original.begin() + 100));
        check_throws<std::out_of_range>([&] { pinned.read_into(900, direct); });
        CHECK(pinned.read_all() == original);
        CHECK(pinned.unchanged());
    }

    {
        bzip4::PinnedFile pinned(target);
        const int descriptor = ::open(target.c_str(), O_WRONLY | O_CLOEXEC);
        if (descriptor < 0) throw std::system_error(errno, std::generic_category(), "open mutation target");
        const std::byte changed = std::byte{0x5a};
        const ssize_t count = ::pwrite(descriptor, &changed, 1, 17);
        const int saved = errno;
        (void)::fsync(descriptor);
        (void)::close(descriptor);
        if (count != 1) throw std::system_error(saved, std::generic_category(), "pwrite mutation");
        CHECK(!pinned.unchanged());
        check_throws<std::runtime_error>([&] { pinned.require_unchanged(); });
    }

    write_file(target, original);
    {
        bzip4::PinnedFile pinned(target);
        const auto replacement = directory.path() / "replacement.bin";
        const auto replacement_bytes = pattern(333);
        write_file(replacement, replacement_bytes);
        std::filesystem::rename(replacement, target);
        CHECK(pinned.read_all() == original); // Reads remain on the opened inode.
        CHECK(read_file(target) == replacement_bytes);
        CHECK(pinned.unchanged());
    }

    const auto symlink = directory.path() / "input-link";
    std::filesystem::create_symlink(target.filename(), symlink);
    check_throws<std::system_error>([&] {
        bzip4::PinnedFile forbidden(symlink);
        (void)forbidden;
    });

    write_file(target, original);
    bzip4::PinnedFile truncated(target);
    CHECK(::truncate(target.c_str(), 10) == 0);
    std::array<std::byte, 20> too_much{};
    CHECK(!truncated.read_exact(0, too_much));
    CHECK(!truncated.unchanged());
}

void test_codec_guards() {
    check_throws<bzip4::CodecError>([] {
        bzip4::Workspace invalid(std::numeric_limits<std::uint32_t>::max());
        (void)invalid;
    });
    for (const std::size_t size : {std::size_t{0}, std::size_t{1}, std::size_t{63},
                                   std::size_t{64}, std::size_t{65},
                                   static_cast<std::size_t>(bzip4::min_block_size)}) {
        const auto boundary = pattern(size);
        const auto frame = bzip4::compress_frame(boundary, bzip4::min_block_size);
        CHECK(bzip4::decompress_frame(frame, boundary.size()) == boundary);
    }
    check_throws<bzip4::CodecError>([] {
        (void)bzip4::frame_bound(std::numeric_limits<std::size_t>::max(), bzip4::min_block_size);
    });

    const auto oversized_workspace = make_empty_block_frame(bzip4::max_block_size, 1);
    const auto large_info = bzip4::inspect_frame(oversized_workspace, 0);
    CHECK(large_info.block_size == bzip4::max_block_size);
    CHECK(large_info.decoder_block_size == bzip4::min_block_size);
    CHECK(large_info.decoder_workspace_bytes ==
          bzip4::workspace_memory_bound(bzip4::min_block_size));
    CHECK(bzip4::decompress_frame(oversized_workspace, 0).empty());
    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        (void)bzip4::inspect_frame(
            oversized_workspace, 0, true,
            large_info.decoder_workspace_bytes - 1U);
    });

    std::vector<std::byte> empty_large;
    append_text(empty_large, "BZ3v1");
    append_u32(empty_large, bzip4::max_block_size);
    append_u32(empty_large, 0);
    const auto empty_large_info = bzip4::inspect_frame(empty_large, 0);
    CHECK(empty_large_info.decoder_workspace_bytes == 0);
    CHECK(bzip4::decompress_frame(empty_large, 0).empty());

    const auto input = pattern(2000);
    auto encoded = bzip4::compress_frame(input, bzip4::min_block_size);
    check_codec_error(BZ3_ERR_DATA_TOO_BIG, [&] {
        (void)bzip4::decompress_frame(encoded, input.size() - 1);
    });
    encoded.push_back(std::byte{0});
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::inspect_frame(encoded, input.size(), true);
    });
    CHECK(bzip4::inspect_frame(encoded, input.size(), false).trailing_bytes == 1);
    encoded[0] = std::byte{'X'};
    check_codec_error(BZ3_ERR_MALFORMED_HEADER, [&] {
        (void)bzip4::decompress_frame(encoded, input.size(), false);
    });

    const auto valid = bzip4::compress_frame(input, bzip4::min_block_size);
    for (std::size_t cut = 0; cut < valid.size(); cut += 17) {
        try {
            (void)bzip4::decompress_frame(
                std::span<const std::byte>(valid).first(cut), input.size());
        } catch (const bzip4::CodecError&) {
        }
    }
    for (std::size_t index = 0; index < std::min<std::size_t>(valid.size(), 128); ++index) {
        auto mutated = valid;
        mutated[index] ^= std::byte{0x5a};
        try {
            (void)bzip4::decompress_frame(mutated, input.size());
        } catch (const bzip4::CodecError&) {
        }
    }
}

void test_release_tree_audit() {
    TempDirectory directory;
    const auto root = directory.path() / "release";
    const std::span<const std::string_view> required = bzip4::required_release_paths();
    CHECK(required.size() == 101);
    CHECK(std::none_of(required.begin(), required.end(), [](std::string_view path) {
        return path.empty();
    }));
    std::vector<std::string_view> required_sorted(required.begin(), required.end());
    std::sort(required_sorted.begin(), required_sorted.end());
    CHECK(std::adjacent_find(required_sorted.begin(), required_sorted.end()) ==
          required_sorted.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("include/bzip4/parallel_codec.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("include/bzip4/profile.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("include/bzip4/resource_plan.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/resource_plan.cpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/profile.cpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/SPEED_FIRST_BLOCK_POLICY.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/RESOURCE_FIT_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/DATACUBE_WELDPOINT_ANALYSIS.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/EFFECTIVENESS_SCORECARD.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/COMPILER_AND_LIBSAIS_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/PROFILE_POLICY.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/PREDICTION_REGISTER.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/compiler-fair-matrix.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/profile-policy-regression.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/prediction-register.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("bin/linux-x86_64/bzip4_codec")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/parallel_codec.cpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/codec_core.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("tests/oracle_api.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/frame_source.cpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/frame_source.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/frame_envelope.cpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("src/frame_envelope.hpp")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/PARALLEL_FRAME_ENCODER_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/PARALLEL_FRAME_DECODER_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/FRAME_SOURCE_REFACTOR_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/RETAINED_LANE_CORE_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/BLOCK_WORKSPACE_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/CHECKSUM_FUSION_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ENTROPY_HOT_LOOP_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ENTROPY_TRANSFORM_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/HIGH_LEVEL_C_API_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/FRAME_WORKSPACE_CONTRACTION_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ZIP_ENTRY_TYPE_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ZIP64_BOUNDARY_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/zip64-boundary-regression.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ZIP_METADATA_ARENA_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/zip-metadata-arena-regression.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ZIP_PAYLOAD_NOMINATION_AUDIT.md")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/zip-payload-nomination-regression.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("evidence/representative-payload-nomination.json")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("scripts/validate.sh")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("upstream/bzip3-1.5.3-53984ef/include/libsais.h")) != required.end());
    CHECK(std::find(required.begin(), required.end(),
                    std::string_view("docs/ZIP_CENTRAL_STREAM_AUDIT.md")) != required.end());
    for (const std::string_view relative : required) {
        write_text_file(root / relative, "fixture\n");
    }

    // `build-aux` is upstream Autotools source closure, not an out-of-tree build.
    write_text_file(
        root / "upstream/bzip3-1.5.3-53984ef/build-aux/install-sh", "fixture\n");
    write_fixture_manifest(root);
    const auto clean = bzip4::audit_release_tree(root);
    CHECK(clean.ok());

    // Generated build roots remain forbidden at the release-tree boundary.
    write_text_file(root / "build-scratch/generated.o", "fixture\n");
    const auto dirty = bzip4::audit_release_tree(root);
    CHECK(!dirty.ok());
    CHECK(std::any_of(dirty.issues.begin(), dirty.issues.end(), [](const bzip4::AuditIssue& issue) {
        return issue.code == "build_junk" && issue.path == std::filesystem::path("build-scratch");
    }));
}

void test_zip_payload_nomination() {
    constexpr std::uint32_t nominated_crc = 0x55667788U;
    const auto bytes = make_zip({
        {"one.bin", "one.bin", "repeat-me", 0, nominated_crc, false},
        {"two.bin", "two.bin", "repeat-me", 0, nominated_crc, false},
        {"three.bin", "three.bin", "other-one", 0, nominated_crc, false},
        {"unique.bin", "unique.bin", "unique!!!", 0, 0x11223344U, false},
    });
    TempFile file(bytes);

    {
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(!report.payload_probe_enabled);
        CHECK(report.content_nomination_groups == 0);
        CHECK(report.payload_candidate_groups == 0);
        CHECK(report.payload_probe_read_bytes == 0);
    }
    {
        bzip4::ZipLimits limits;
        limits.probe_exact_payload_duplicates = true;
        limits.payload_probe_chunk_bytes = 3;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(report.ok());
        CHECK(report.payload_probe_enabled);
        CHECK(!report.payload_probe_budget_exhausted);
        CHECK(report.content_nomination_groups == 1);
        CHECK(report.content_nomination_entries == 3);
        CHECK(report.content_nomination_repeated_uncompressed_bytes == 18);
        CHECK(report.payload_candidate_groups == 1);
        CHECK(report.payload_candidate_entries == 3);
        CHECK(report.payload_candidate_compressed_bytes == 27);
        CHECK(report.payload_hashed_groups == 1);
        CHECK(report.payload_hashed_entries == 3);
        CHECK(report.payload_probe_read_bytes == 45);
        CHECK(report.verified_payload_groups == 1);
        CHECK(report.verified_payload_entries == 2);
        CHECK(report.verified_duplicate_entries == 1);
        CHECK(report.verified_repeated_compressed_bytes == 9);
        CHECK(report.verified_repeated_uncompressed_bytes == 9);
        CHECK(report.payload_probe_skipped_groups == 0);
        CHECK(report.payload_digest_collision_groups == 0);
        CHECK(report.payload_probe_peak_scratch_bytes != 0);
        const std::string json = bzip4::zip_report_json(report, false);
        CHECK(json.find("bzip4.zip-preflight.v7") != std::string::npos);
        CHECK(json.find("\"verified_duplicate_entries\":1") != std::string::npos);
        CHECK(json.find("\"payload_probe_read_bytes\":45") != std::string::npos);
    }
    {
        bzip4::ZipLimits limits;
        limits.probe_exact_payload_duplicates = true;
        // A three-entry, nine-byte group is admitted against the conservative
        // (3n-2)*size = 63-byte hash-and-compare upper bound.
        limits.max_payload_probe_read_bytes = 62;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(report.ok());
        CHECK(report.payload_probe_budget_exhausted);
        CHECK(report.payload_candidate_groups == 1);
        CHECK(report.payload_hashed_groups == 0);
        CHECK(report.payload_probe_read_bytes == 0);
        CHECK(report.payload_probe_skipped_groups == 1);
        CHECK(report.payload_probe_skipped_entries == 3);
        CHECK(report.payload_probe_skipped_compressed_bytes == 27);
    }
    {
        bzip4::ZipLimits limits;
        limits.probe_exact_payload_duplicates = true;
        limits.max_payload_probe_group_entries = 2;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(report.ok());
        CHECK(!report.payload_probe_budget_exhausted);
        CHECK(report.payload_probe_skipped_groups == 1);
        CHECK(report.payload_hashed_groups == 0);
    }
    {
        bzip4::ZipLimits limits;
        limits.probe_exact_payload_duplicates = true;
        limits.payload_probe_chunk_bytes = 0;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "payload_probe_configuration";
        }));
    }
}

void test_zip_preflight() {
    constexpr std::uint16_t unix_version_20 =
        static_cast<std::uint16_t>((3U << 8U) | 20U);
    const auto unix_attributes = [](std::uint16_t mode, std::uint32_t dos = 0) {
        return (static_cast<std::uint32_t>(mode) << 16U) | dos;
    };

    {
        TempFile file(make_zip({{"a.txt", "a.txt", "abc", 0, 0x12345678U, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.entries == 1);
        CHECK(report.unsafe_paths == 0);
        CHECK(report.central_name_bytes == 5);
        CHECK(report.central_parser_peak_read_bytes == 46);
        CHECK(report.central_entry_descriptor_bytes != 0);
        CHECK(report.central_entry_descriptor_bytes <= 64);
        CHECK(report.central_entry_storage_bytes >= report.central_entry_descriptor_bytes);
        CHECK(report.central_name_storage_bytes >= report.central_name_bytes);
        CHECK(report.central_parser_peak_retained_bytes >=
              report.central_entry_storage_bytes + report.central_name_storage_bytes);
        const std::string json = bzip4::zip_report_json(report, false);
        CHECK(json.find("bzip4.zip-preflight.v7") != std::string::npos);
        CHECK(json.find("central_parser_peak_read_bytes") != std::string::npos);
        CHECK(json.find("central_parser_peak_retained_bytes") != std::string::npos);
        CHECK(report.unclassified_type_entries == 1);
        CHECK(json.find("unclassified_type_entries") != std::string::npos);
    }
    {
        // The EOCD count must be feasible from the central-directory byte
        // budget before any per-entry metadata reserve occurs.
        auto bytes = make_zip({{"one", "one", "x", 0, 1, false}});
        const std::size_t eocd = bytes.size() - 22U;
        write_u16(bytes, eocd + 8U, 2U);
        write_u16(bytes, eocd + 10U, 2U);
        TempFile file(bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "central_entry_count_range";
        }));
        CHECK(report.central_entry_storage_bytes == 0U);
        CHECK(report.central_name_storage_bytes == 0U);
    }
    {
        TempFile file(make_zip({ZipSpec(
            "regular", "regular", "x", 0, 1, false, false, {}, {},
            unix_version_20, unix_attributes(0100644U))}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.regular_file_entries == 1);
        CHECK(report.unclassified_type_entries == 0);
    }
    {
        TempFile file(make_zip({ZipSpec(
            "directory/", "directory/", "", 0, 1, false, false, {}, {},
            unix_version_20, unix_attributes(0040755U, 0x10U))}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.directory_entries == 1);
        CHECK(report.entry_type_mismatches == 0);
    }
    {
        TempFile file(make_zip({ZipSpec(
            "dos-directory", "dos-directory", "", 0, 1, false, false,
            {}, {}, 20, 0x10U)}));
        const auto rejected = bzip4::preflight_zip(file.path());
        CHECK(!rejected.ok());
        CHECK(rejected.directory_entries == 1);
        CHECK(rejected.entry_type_mismatches == 1);
        CHECK(std::any_of(rejected.issues.begin(), rejected.issues.end(), [](const auto& value) {
            return value.code == "entry_type_mismatch" &&
                value.message.find("DOS directory attribute") != std::string::npos;
        }));
    }
    {
        TempFile file(make_zip({ZipSpec(
            "regular-dos-conflict", "regular-dos-conflict", "x", 0, 1,
            false, false, {}, {}, unix_version_20,
            unix_attributes(0100644U, 0x10U))}));
        const auto rejected = bzip4::preflight_zip(file.path());
        CHECK(!rejected.ok());
        CHECK(rejected.regular_file_entries == 1);
        CHECK(rejected.entry_type_mismatches == 1);
        CHECK(std::any_of(rejected.issues.begin(), rejected.issues.end(), [](const auto& value) {
            return value.code == "entry_type_mismatch" &&
                value.message.find("non-directory POSIX mode") != std::string::npos;
        }));
    }
    {
        TempFile file(make_zip({ZipSpec(
            "link", "link", "target", 0, 1, false, false, {}, {},
            unix_version_20, unix_attributes(0120777U))}));
        const auto rejected = bzip4::preflight_zip(file.path());
        CHECK(!rejected.ok());
        CHECK(rejected.symlink_entries == 1);
        CHECK(std::any_of(rejected.issues.begin(), rejected.issues.end(), [](const auto& value) {
            return value.code == "symlink_entry" && value.fatal;
        }));

        bzip4::ZipLimits limits;
        limits.reject_symlinks = false;
        const auto reported = bzip4::preflight_zip(file.path(), limits);
        CHECK(reported.ok());
        CHECK(reported.symlink_entries == 1);
        CHECK(std::any_of(reported.issues.begin(), reported.issues.end(), [](const auto& value) {
            return value.code == "symlink_entry" && !value.fatal;
        }));
    }
    {
        TempFile file(make_zip({ZipSpec(
            "fifo", "fifo", "", 0, 1, false, false, {}, {},
            unix_version_20, unix_attributes(0010644U))}));
        const auto rejected = bzip4::preflight_zip(file.path());
        CHECK(!rejected.ok());
        CHECK(rejected.special_file_entries == 1);

        bzip4::ZipLimits limits;
        limits.reject_special_files = false;
        const auto reported = bzip4::preflight_zip(file.path(), limits);
        CHECK(reported.ok());
        CHECK(reported.special_file_entries == 1);
    }
    {
        TempFile file(make_zip({ZipSpec(
            "not-a-directory/", "not-a-directory/", "x", 0, 1, false, false,
            {}, {}, unix_version_20, unix_attributes(0100644U))}));
        const auto rejected = bzip4::preflight_zip(file.path());
        CHECK(!rejected.ok());
        CHECK(rejected.entry_type_mismatches == 1);
        CHECK(std::any_of(rejected.issues.begin(), rejected.issues.end(), [](const auto& value) {
            return value.code == "entry_type_mismatch";
        }));

        bzip4::ZipLimits limits;
        limits.reject_entry_type_mismatches = false;
        const auto reported = bzip4::preflight_zip(file.path(), limits);
        CHECK(reported.ok());
        CHECK(reported.entry_type_mismatches == 1);
    }
    {
        std::string long_name(80, 'n');
        std::string central_extra(100, 'x');
        central_extra[0] = static_cast<char>(0x34);
        central_extra[1] = static_cast<char>(0x12);
        central_extra[2] = static_cast<char>(96);
        central_extra[3] = 0;
        TempFile file(make_zip({{
            long_name, long_name, "x", 0, 1, false, false,
            {}, central_extra}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.central_name_bytes == long_name.size());
        // Name and extra are read separately, not as one combined allocation.
        CHECK(report.central_parser_peak_read_bytes == central_extra.size());
    }
    {
        std::vector<ZipSpec> specs;
        for (std::size_t index = 0; index < 128; ++index) {
            const std::string name = "entry-" + std::to_string(index) + ".txt";
            specs.emplace_back(name, name, "x", 0, static_cast<std::uint32_t>(index + 1));
        }
        TempFile file(make_zip(specs));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.entries == specs.size());
        CHECK(report.central_directory_size > report.central_parser_peak_read_bytes);
        CHECK(report.central_parser_peak_read_bytes == 46);
        std::uint64_t expected_name_bytes = 0;
        for (const ZipSpec& spec : specs) expected_name_bytes += spec.central_name.size();
        CHECK(report.central_name_bytes == expected_name_bytes);
    }
    {
        TempFile file(make_zip({{"limit-name", "limit-name", "x", 0, 1, false}}));
        bzip4::ZipLimits limits;
        limits.max_total_name_bytes = 3;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "name_storage_limit";
        }));
    }
    {
        TempFile file(make_zip({{"long-name", "long-name", "x", 0, 1, false}}));
        bzip4::ZipLimits limits;
        limits.max_name_bytes = 3;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(!report.ok());
        CHECK(report.central_name_bytes == 0);
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "name_limit";
        }));
    }
    {
        TempFile file(make_zip({
            {"../a", "../a", "x", 0, 1, false},
            {"../b", "../b", "x", 0, 2, false},
            {"../c", "../c", "x", 0, 3, false},
        }));
        bzip4::ZipLimits limits;
        limits.max_issues = 1;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(!report.ok());
        CHECK(report.unsafe_paths == 3);
        CHECK(report.issue_limit == 1);
        CHECK(report.issues.size() == 1);
        CHECK(report.suppressed_issues == 2);
        CHECK(report.suppressed_fatal_issues == 2);
        const std::string json = bzip4::zip_report_json(report, false);
        CHECK(json.find("suppressed_fatal_issues") != std::string::npos);
    }
    {
        const std::string valid_extra("\x34\x12\x01\x00Z", 5);
        TempFile file(make_zip({{
            "extra", "extra", "abc", 0, 0x12345678U, false, false,
            valid_extra, valid_extra}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
    }
    {
        const std::string truncated_extra("\x01\x00", 2);
        TempFile file(make_zip({{
            "local-extra", "local-extra", "abc", 0, 0x12345678U, false, false,
            truncated_extra, {}}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_extra_truncated";
        }));
    }
    {
        const std::string truncated_extra("\x01\x00", 2);
        TempFile file(make_zip({{
            "central-extra", "central-extra", "abc", 0, 0x12345678U, false, false,
            {}, truncated_extra}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "central_extra_truncated";
        }));
    }
    {
        const std::string overrun_extra("\x34\x12\x04\x00Z", 5);
        TempFile file(make_zip({{
            "local-extra-range", "local-extra-range", "abc",
            0, 0x12345678U, false, false, overrun_extra, {}}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_extra_range";
        }));
    }
    {
        const std::string overrun_extra("\x34\x12\x04\x00Z", 5);
        TempFile file(make_zip({{
            "central-extra-range", "central-extra-range", "abc",
            0, 0x12345678U, false, false, {}, overrun_extra}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "central_extra_range";
        }));
    }
    {
        const std::string duplicate_zip64("\x01\x00\x00\x00", 4);
        TempFile file(make_zip({{
            "duplicate-z64", "duplicate-z64", "abc", 0, 0x12345678U, false, true,
            duplicate_zip64, {}}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_zip64_duplicate";
        }));
    }
    {
        const std::string duplicate_zip64("\x01\x00\x00\x00\x01\x00\x00\x00", 8);
        TempFile file(make_zip({{
            "central-duplicate-z64", "central-duplicate-z64", "abc",
            0, 0x12345678U, false, false, {}, duplicate_zip64}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "central_zip64_duplicate";
        }));
    }
    {
        TempFile file(make_zip({{"", "", "x", 0, 1, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.unsafe_paths == 1);
        CHECK(report.central_name_bytes == 0);
    }
    {
        const std::string byte_name("\xff" "name", 5);
        TempFile file(make_zip({{byte_name, byte_name, "x", 1, 1, false}}));
        bzip4::ZipLimits limits;
        limits.reject_encryption = false;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(report.ok());
        CHECK(report.encrypted_entries == 1);
        const std::string json = bzip4::zip_report_json(report, false);
        CHECK(json.find("\\u00ffname") != std::string::npos);
        CHECK(json.find(std::string(1, static_cast<char>(0xff))) == std::string::npos);
    }
    {
        TempFile file(make_zip({{"../escape", "../escape", "x", 0, 1, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.unsafe_paths == 1);
    }
    {
        TempFile file(make_zip({{"a/./b", "a/./b", "x", 0, 1, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.unsafe_paths == 1);
    }
    {
        TempFile file(make_zip({{"a//b", "a//b", "x", 0, 1, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.unsafe_paths == 1);
    }
    {
        TempFile file(make_zip({
            {"same", "same", "a", 0, 1, false},
            {"same", "same", "b", 0, 2, false},
        }));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.duplicate_names == 1);
    }
    {
        // The first central record claims a long span containing both later
        // local records. Comparing only adjacent span ends detects the middle
        // record but misses the inner record after the short middle span.
        auto bytes = make_zip({
            {"outer", "outer", "a", 0, 1, false},
            {"middle", "middle", "b", 0, 2, false},
            {"inner", "inner", "c", 0, 3, false},
        });
        const std::size_t eocd = bytes.size() - 22;
        const std::uint32_t central_offset = read_u32(bytes, eocd + 16);
        constexpr std::size_t outer_data_offset = 30U + 5U;
        CHECK(central_offset > outer_data_offset + 1U);
        const std::uint32_t outer_compressed = static_cast<std::uint32_t>(
            central_offset - 1U - outer_data_offset);
        write_u32(bytes, central_offset + 20U, outer_compressed);
        TempFile file(bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::count_if(
            report.issues.begin(), report.issues.end(), [](const auto& value) {
                return value.code == "entry_overlap";
            }) == 2);
    }
    {
        TempFile file(make_zip({{"local", "central", "x", 0, 1, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
    }
    {
        TempFile file(make_zip({{"d", "d", "xyz", 8, 0x08074b50U, false}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.data_descriptor_entries == 1);
    }
    {
        TempFile file(make_zip({{"d", "d", "xyz", 8, 0xabcdef12U, true}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
    }
    for (const bool signed_descriptor : {false, true}) {
        // APPNOTE selects 64-bit descriptor sizes from ZIP64 extra-field
        // presence, even when the central sizes fit in 32 bits and carry no
        // sentinels. This exercises that representation independently of a
        // ZIP64 end-of-central-directory record.
        TempFile file(make_zip({{
            "z64d", "z64d", "xyz", 8, 0xabcdef12U,
            signed_descriptor, true}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64);
        CHECK(report.zip64_entries == 1);
        CHECK(report.data_descriptor_entries == 1);
        CHECK(report.zip64_data_descriptor_entries == 1);
    }
    {
        TempFile file(make_zip({{"z", "z", "xyz", 0, 0x1234U, false, true}}));
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64);
        CHECK(report.zip64_entries == 1);
        CHECK(report.zip64_eocd_size == 0);
    }
    {
        const Zip64Fixture fixture = make_zip64(false, false);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64);
        CHECK(report.entries == 1);
        CHECK(report.zip64_entries == 1);
        CHECK(report.zip64_data_descriptor_entries == 0);
        CHECK(report.zip64_eocd_offset == fixture.zip64_eocd_offset);
        CHECK(report.zip64_eocd_size == 56);
        CHECK(report.central_directory_offset == fixture.central_offset);
        CHECK(report.regular_file_entries == 1);
        const std::string json = bzip4::zip_report_json(report, false);
        CHECK(json.find("bzip4.zip-preflight.v7") != std::string::npos);
        CHECK(json.find("\"zip64_entries\":1") != std::string::npos);
        CHECK(json.find("\"zip64_eocd_size\":56") != std::string::npos);
    }
    for (const std::size_t ordinary_local_size_offset : {18U, 22U}) {
        // A local ZIP64 field carries both 64-bit sizes whenever either legacy
        // size is a placeholder. The other 32-bit field remains populated and
        // must agree with its redundant value in the ZIP64 pair.
        Zip64Fixture fixture = make_zip64(false, false);
        write_u32(fixture.bytes, ordinary_local_size_offset, 3U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64_entries == 1);
    }
    {
        // The old placeholder-only parser accepted this malformed one-value
        // local field when exactly one legacy size was a sentinel. The local
        // contract requires both uncompressed and compressed 64-bit values.
        Zip64Fixture fixture = make_zip64(false, false);
        write_u32(fixture.bytes, 18U, 3U);
        write_u16(
            fixture.bytes,
            fixture.local_extra_identifier_offset + 2U,
            8U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_zip64_missing";
        }));
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u32(fixture.bytes, 18U, 4U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_zip64_redundant_mismatch";
        }));
    }
    {
        auto bytes = make_zip({{
            "z64d", "z64d", "xyz", 8, 0xabcdef12U,
            false, true}});
        constexpr std::size_t local_extra = 30U + 4U;
        write_u16(bytes, local_extra + 2U, 8U);
        TempFile file(bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_zip64_payload";
        }));
    }
    {
        // The reserved extensible data sector is included in the ZIP64 end
        // record's declared payload and remains bounded by the same limit.
        Zip64Fixture fixture = make_zip64(false, false);
        constexpr std::size_t extension_size = 32U;
        fixture.bytes.insert(
            fixture.bytes.begin() + static_cast<std::ptrdiff_t>(fixture.locator_offset),
            extension_size, std::byte{0xa5});
        write_u64(
            fixture.bytes, fixture.zip64_eocd_offset + 4U,
            44U + extension_size);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64_eocd_size == 56U + extension_size);
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u16(fixture.bytes, fixture.zip64_eocd_offset + 14U, 44U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "zip64_version_needed";
        }));
    }
    {
        const Zip64Fixture fixture = make_zip64(false, false);
        for (std::size_t size = 0; size < fixture.bytes.size(); ++size) {
            TempFile file(std::span<const std::byte>(fixture.bytes).first(size));
            CHECK(!bzip4::preflight_zip(file.path()).ok());
        }
    }
    {
        // A central relative-offset sentinel can require ZIP64 even when the
        // local header itself remains an ordinary version-2.0 record.
        const Zip64Fixture fixture = make_zip64(false, false, true);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.zip64);
        CHECK(report.zip64_entries == 1);
        CHECK(report.zip64_data_descriptor_entries == 0);
    }
    for (const bool signed_descriptor : {false, true}) {
        const Zip64Fixture fixture = make_zip64(true, signed_descriptor);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(report.data_descriptor_entries == 1);
        CHECK(report.zip64_data_descriptor_entries == 1);
        CHECK(report.zip64_entries == 1);
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u16(fixture.bytes, fixture.central_extra_identifier_offset, 0x7777U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "central_zip64_missing";
        }));
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u16(fixture.bytes, fixture.local_extra_identifier_offset, 0x7777U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "local_zip64_missing";
        }));
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u16(fixture.bytes, fixture.eocd_offset + 10U, 2U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "zip64_eocd_mismatch";
        }));
    }
    {
        const Zip64Fixture fixture = make_zip64(false, false);
        TempFile file(fixture.bytes);
        bzip4::ZipLimits limits;
        limits.max_zip64_eocd_bytes = 55;
        const auto report = bzip4::preflight_zip(file.path(), limits);
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "zip64_eocd_limit";
        }));
    }
    {
        Zip64Fixture fixture = make_zip64(false, false);
        write_u64(
            fixture.bytes, fixture.locator_offset + 8U,
            static_cast<std::uint64_t>(fixture.bytes.size()) + 4096U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "zip64_eocd_missing";
        }));
    }
    {
        Zip64Fixture fixture = make_zip64(true, false);
        write_u64(fixture.bytes, fixture.descriptor_offset + 4U, 4U);
        TempFile file(fixture.bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "descriptor_mismatch";
        }));
    }
    {
        // An ordinary central-entry comment may begin with the locator magic
        // in the exact 20 bytes preceding the classic EOCD. Without sentinels
        // or a referenced ZIP64 end record, it must remain a classic archive.
        auto bytes = make_zip({{"x", "x", "x", 0, 1, false}});
        const std::size_t old_eocd = bytes.size() - 22U;
        const std::uint32_t central_offset = read_u32(bytes, old_eocd + 16U);
        const std::uint32_t central_size = read_u32(bytes, old_eocd + 12U);
        std::vector<std::byte> fake_locator;
        append_u32(fake_locator, 0x07064b50U);
        append_u32(fake_locator, 0U);
        append_u64(fake_locator, 0U);
        append_u32(fake_locator, 1U);
        CHECK(fake_locator.size() == 20U);
        bytes.insert(
            bytes.begin() + static_cast<std::ptrdiff_t>(old_eocd),
            fake_locator.begin(), fake_locator.end());
        write_u16(bytes, static_cast<std::size_t>(central_offset) + 32U, 20U);
        const std::size_t new_eocd = old_eocd + fake_locator.size();
        write_u32(bytes, new_eocd + 12U, central_size + 20U);
        TempFile file(bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(report.ok());
        CHECK(!report.zip64);
    }
    {
        auto bytes = make_zip({{"x", "x", "x", 0, 1, false}});
        CHECK(bytes.size() >= 22);
        const std::size_t eocd = bytes.size() - 22;
        bytes[eocd + 8] = std::byte{0xff};
        bytes[eocd + 9] = std::byte{0xff};
        bytes[eocd + 10] = std::byte{0xff};
        bytes[eocd + 11] = std::byte{0xff};
        TempFile file(bytes);
        const auto report = bzip4::preflight_zip(file.path());
        CHECK(!report.ok());
        CHECK(report.zip64);
        CHECK(std::any_of(report.issues.begin(), report.issues.end(), [](const auto& value) {
            return value.code == "zip64_locator_missing";
        }));
    }
}

} // namespace

int main() {
    const std::vector<std::pair<std::string, std::function<void()>>> tests{
        {"sha256", test_sha256},
        {"activation", test_activation},
        {"codec_roundtrip_and_oracle", test_codec_roundtrip_and_oracle},
        {"block_decoder_contract", test_block_decoder_contract},
        {"low_level_c_api_hardening", test_low_level_c_api_hardening},
        {"entropy_and_transform_terminal_contract",
         test_entropy_and_transform_terminal_contract},
        {"high_level_c_api_contract", test_high_level_c_api_contract},
        {"checksum_fusion_paths", test_checksum_fusion_paths},
        {"entropy_model_row_aliasing", test_entropy_model_row_aliasing},
        {"borrowed_block_views_and_public_api", test_borrowed_block_views_and_public_api},
        {"frame_streaming_and_envelope", test_frame_streaming_and_envelope},
        {"range_backed_frames", test_range_backed_frames},
        {"parallel_frame_encoder", test_parallel_frame_encoder},
        {"parallel_frame_decoder", test_parallel_frame_decoder},
        {"frame_workspace_contraction", test_frame_workspace_contraction},
        {"resource_planning", test_resource_planning},
        {"codec_profiles", test_codec_profiles},
        {"atomic_output", test_atomic_output},
        {"pinned_input", test_pinned_input},
        {"codec_guards", test_codec_guards},
        {"release_tree_audit", test_release_tree_audit},
        {"zip_payload_nomination", test_zip_payload_nomination},
        {"zip_preflight", test_zip_preflight},
    };
    std::size_t passed = 0;
    for (const auto& [name, test] : tests) {
        try {
            test();
            ++passed;
            std::cout << "PASS " << name << '\n';
        } catch (const std::exception& exception) {
            std::cerr << "FAIL " << name << ": " << exception.what() << '\n';
            return 1;
        }
    }
    std::cout << "passed=" << passed << " total=" << tests.size() << '\n';
    return 0;
}
