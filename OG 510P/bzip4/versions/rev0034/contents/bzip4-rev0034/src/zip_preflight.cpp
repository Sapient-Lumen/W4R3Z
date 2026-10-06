#include "bzip4/zip_preflight.hpp"

#include "bzip4/pinned_file.hpp"
#include "bzip4/sha256.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <map>
#include <optional>
#include <numeric>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

namespace bzip4 {
namespace {

constexpr std::uint32_t local_signature = 0x04034b50U;
constexpr std::uint32_t central_signature = 0x02014b50U;
constexpr std::uint32_t eocd_signature = 0x06054b50U;
constexpr std::uint32_t zip64_eocd_signature = 0x06064b50U;
constexpr std::uint32_t zip64_locator_signature = 0x07064b50U;
constexpr std::uint32_t descriptor_signature = 0x08074b50U;
constexpr std::size_t eocd_fixed_size = 22;
constexpr std::size_t zip64_locator_size = 20;
constexpr std::size_t zip64_eocd_minimum_size = 56;
constexpr std::uint64_t zip64_eocd_minimum_payload_size = 44;
constexpr std::size_t central_fixed_size = 46;
constexpr std::size_t local_fixed_size = 30;

[[nodiscard]] std::uint16_t u16(const std::byte* data) noexcept {
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(data[0]) |
        (std::to_integer<std::uint16_t>(data[1]) << 8U));
}

[[nodiscard]] std::uint32_t u32(const std::byte* data) noexcept {
    return std::to_integer<std::uint32_t>(data[0]) |
        (std::to_integer<std::uint32_t>(data[1]) << 8U) |
        (std::to_integer<std::uint32_t>(data[2]) << 16U) |
        (std::to_integer<std::uint32_t>(data[3]) << 24U);
}

[[nodiscard]] std::uint64_t u64(const std::byte* data) noexcept {
    return static_cast<std::uint64_t>(u32(data)) |
        (static_cast<std::uint64_t>(u32(data + 4)) << 32U);
}

[[nodiscard]] bool checked_add(std::uint64_t left, std::uint64_t right, std::uint64_t& result) noexcept {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        return false;
    }
    result = left + right;
    return true;
}

[[nodiscard]] bool checked_add_assign(std::uint64_t& target, std::uint64_t value) noexcept {
    std::uint64_t result = 0;
    if (!checked_add(target, value, result)) {
        return false;
    }
    target = result;
    return true;
}

[[nodiscard]] bool checked_multiply(
    std::uint64_t left,
    std::uint64_t right,
    std::uint64_t& result) noexcept {
    if (left != 0U && right > std::numeric_limits<std::uint64_t>::max() / left) {
        return false;
    }
    result = left * right;
    return true;
}

void issue(ZipReport& report, std::string code, std::string message,
           std::string_view entry = {}, bool fatal = true) {
    if (report.issues.size() < report.issue_limit) {
        report.issues.push_back({
            std::move(code), std::move(message), std::string(entry), fatal});
        return;
    }
    if (report.suppressed_issues != std::numeric_limits<std::size_t>::max()) {
        ++report.suppressed_issues;
    }
    if (fatal &&
        report.suppressed_fatal_issues != std::numeric_limits<std::size_t>::max()) {
        ++report.suppressed_fatal_issues;
    }
}

[[nodiscard]] std::string json_escape(std::string_view value) {
    std::ostringstream output;
    for (const char raw : value) {
        const auto byte = static_cast<unsigned char>(raw);
        switch (byte) {
        case '"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\b': output << "\\b"; break;
        case '\f': output << "\\f"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (byte < 0x20U || byte >= 0x7fU) {
                // Entry names are untrusted byte strings, not guaranteed UTF-8.
                // ASCII-only escapes keep the report valid JSON for every byte.
                output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                       << static_cast<unsigned>(byte) << std::dec;
            } else {
                output << static_cast<char>(byte);
            }
        }
    }
    return output.str();
}

[[nodiscard]] bool path_unsafe(std::string_view name, std::string& reason) {
    if (name.empty()) {
        reason = "empty entry name";
        return true;
    }
    if (name.find('\0') != std::string_view::npos) {
        reason = "NUL byte in entry name";
        return true;
    }
    if (name.front() == '/' || name.front() == '\\') {
        reason = "absolute entry path";
        return true;
    }
    if (name.size() >= 2 && std::isalpha(static_cast<unsigned char>(name[0])) != 0 && name[1] == ':') {
        reason = "drive-qualified entry path";
        return true;
    }
    if (name.find('\\') != std::string_view::npos) {
        reason = "backslash path separator";
        return true;
    }
    std::size_t start = 0;
    while (start <= name.size()) {
        const std::size_t slash = name.find('/', start);
        const std::size_t end = slash == std::string_view::npos ? name.size() : slash;
        const std::string_view component = name.substr(start, end - start);
        const bool terminal_directory_marker = component.empty() &&
            slash == std::string_view::npos && start == name.size() && name.back() == '/';
        if (component == "..") {
            reason = "parent traversal component";
            return true;
        }
        if (component == ".") {
            reason = "noncanonical dot component";
            return true;
        }
        if (component.empty() && !terminal_directory_marker) {
            reason = "empty interior path component";
            return true;
        }
        if (slash == std::string_view::npos) {
            break;
        }
        start = slash + 1;
    }
    return false;
}

enum Zip64EntryState : std::uint8_t {
    zip64_sizes = 1U << 0U,
    zip64_offset = 1U << 1U,
    zip64_disk = 1U << 2U,
    zip64_descriptor = 1U << 3U,
    zip64_entry = 1U << 4U,
    zip64_counted = 1U << 5U,
};

struct CentralEntry {
    std::uint64_t compressed_size{};
    std::uint64_t uncompressed_size{};
    std::uint64_t local_offset{};
    std::size_t name_offset{};
    std::uint32_t crc{};
    std::uint32_t external_attributes{};
    std::uint32_t start_disk{};
    std::uint16_t version_made_by{};
    std::uint16_t version_needed{};
    std::uint16_t flags{};
    std::uint16_t method{};
    std::uint16_t name_length{};
    std::uint8_t zip64_state{};
};

static_assert(std::is_trivially_copyable_v<CentralEntry>);
static_assert(sizeof(CentralEntry) <= 64U);

[[nodiscard]] bool has_zip64_state(
    const CentralEntry& entry,
    Zip64EntryState state) noexcept {
    return (entry.zip64_state & static_cast<std::uint8_t>(state)) != 0U;
}

void set_zip64_state(CentralEntry& entry, Zip64EntryState state) noexcept {
    entry.zip64_state = static_cast<std::uint8_t>(
        entry.zip64_state | static_cast<std::uint8_t>(state));
}

[[nodiscard]] std::string_view entry_name(
    const CentralEntry& entry,
    const std::vector<char>& names) noexcept {
    if (entry.name_length == 0U) {
        return {};
    }
    return {
        names.data() + entry.name_offset,
        entry.name_length,
    };
}

template <class Value>
[[nodiscard]] std::uint64_t vector_storage_bytes(
    const std::vector<Value>& values) noexcept {
    constexpr std::uint64_t element_bytes = sizeof(Value);
    if (values.capacity() >
        std::numeric_limits<std::uint64_t>::max() / element_bytes) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return static_cast<std::uint64_t>(values.capacity()) * element_bytes;
}

template <class... ScratchVectors>
void observe_parser_storage(
    ZipReport& report,
    const std::vector<CentralEntry>& entries,
    const std::vector<char>& names,
    const ScratchVectors&... scratch) noexcept {
    report.central_entry_storage_bytes = vector_storage_bytes(entries);
    report.central_name_storage_bytes = vector_storage_bytes(names);
    std::uint64_t total = 0;
    const auto add = [&](std::uint64_t value) {
        if (value > std::numeric_limits<std::uint64_t>::max() - total) {
            total = std::numeric_limits<std::uint64_t>::max();
        } else {
            total += value;
        }
    };
    add(report.central_entry_storage_bytes);
    add(report.central_name_storage_bytes);
    (add(vector_storage_bytes(scratch)), ...);
    report.central_parser_peak_retained_bytes = std::max(
        report.central_parser_peak_retained_bytes, total);
}

enum class EntryKind : std::uint8_t {
    unclassified,
    regular_file,
    directory,
    symlink,
    special_file,
};

void audit_entry_type(
    const CentralEntry& entry,
    std::string_view name,
    const ZipLimits& limits,
    ZipReport& report) {
    constexpr std::uint16_t file_type_mask = 0170000U;
    constexpr std::uint16_t regular_type = 0100000U;
    constexpr std::uint16_t directory_type = 0040000U;
    constexpr std::uint16_t symlink_type = 0120000U;

    const std::uint8_t host_system = static_cast<std::uint8_t>(
        entry.version_made_by >> 8U);
    const bool posix_attributes = host_system == 3U || host_system == 19U;
    const std::uint16_t unix_mode = static_cast<std::uint16_t>(
        entry.external_attributes >> 16U);
    const std::uint16_t unix_type = static_cast<std::uint16_t>(
        unix_mode & file_type_mask);
    const bool name_directory = !name.empty() && name.back() == '/';
    const bool dos_directory = (entry.external_attributes & 0x10U) != 0U;

    EntryKind kind = EntryKind::unclassified;
    bool explicit_type = false;
    if (posix_attributes && unix_type != 0U) {
        explicit_type = true;
        if (unix_type == regular_type) {
            kind = EntryKind::regular_file;
        } else if (unix_type == directory_type) {
            kind = EntryKind::directory;
        } else if (unix_type == symlink_type) {
            kind = EntryKind::symlink;
        } else {
            kind = EntryKind::special_file;
        }
    } else if (name_directory || dos_directory) {
        kind = EntryKind::directory;
    }

    bool mismatch = false;
    std::string mismatch_message;
    if (explicit_type) {
        const bool explicit_directory = kind == EntryKind::directory;
        if (explicit_directory != name_directory) {
            mismatch = true;
            mismatch_message = explicit_directory
                ? "directory mode is missing the trailing-slash name marker"
                : "non-directory mode conflicts with a trailing-slash name";
        } else if (dos_directory && !explicit_directory) {
            mismatch = true;
            mismatch_message =
                "non-directory POSIX mode conflicts with the DOS directory attribute";
        }
    } else if (dos_directory && !name_directory) {
        mismatch = true;
        mismatch_message =
            "DOS directory attribute is missing the trailing-slash name marker";
    }

    switch (kind) {
    case EntryKind::regular_file:
        ++report.regular_file_entries;
        break;
    case EntryKind::directory:
        ++report.directory_entries;
        break;
    case EntryKind::symlink:
        ++report.symlink_entries;
        issue(report, "symlink_entry",
              "symbolic-link ZIP entries require an extraction policy outside preflight",
              name, limits.reject_symlinks);
        break;
    case EntryKind::special_file:
        ++report.special_file_entries;
        issue(report, "special_file_entry",
              "device, FIFO, socket, or unknown POSIX file type is not extractable by default",
              name, limits.reject_special_files);
        break;
    case EntryKind::unclassified:
        ++report.unclassified_type_entries;
        break;
    }

    if (mismatch) {
        ++report.entry_type_mismatches;
        issue(report, "entry_type_mismatch", std::move(mismatch_message),
              name, limits.reject_entry_type_mismatches);
    }
}

struct Span {
    std::uint64_t start{};
    std::uint64_t end{};
    std::uint32_t payload_delta{};
    std::uint32_t entry_index{};
};

static_assert(sizeof(Span) == 24U);

template <class Visitor>
[[nodiscard]] bool visit_extra_fields(
    std::span<const std::byte> bytes,
    std::string_view scope,
    std::string_view entry,
    ZipReport& report,
    Visitor&& visitor) {
    std::size_t cursor = 0;
    while (cursor < bytes.size()) {
        if (bytes.size() - cursor < 4) {
            issue(
                report,
                std::string(scope) + "_extra_truncated",
                std::string(scope) + " extra field ends inside its four-byte header",
                std::string(entry));
            return false;
        }
        const std::uint16_t identifier = u16(bytes.data() + static_cast<std::ptrdiff_t>(cursor));
        const std::uint16_t length = u16(bytes.data() + static_cast<std::ptrdiff_t>(cursor + 2));
        cursor += 4;
        if (length > bytes.size() - cursor) {
            issue(
                report,
                std::string(scope) + "_extra_range",
                std::string(scope) + " extra field payload exceeds its declared area",
                std::string(entry));
            return false;
        }
        visitor(identifier, bytes.subspan(cursor, length));
        cursor += length;
    }
    return true;
}

struct EndDirectory {
    std::uint64_t entries{};
    std::uint64_t central_size{};
    std::uint64_t central_offset{};
    std::uint64_t central_end_anchor{};
};

[[nodiscard]] bool eocd_field_matches(
    std::uint64_t resolved,
    std::uint64_t legacy,
    std::uint64_t sentinel) noexcept {
    return legacy == sentinel || legacy == resolved;
}

[[nodiscard]] std::optional<EndDirectory> resolve_end_directory(
    const PinnedFile& file,
    std::uint64_t eocd_offset,
    const std::byte* eocd,
    const ZipLimits& limits,
    ZipReport& report) {
    const std::uint16_t disk16 = u16(eocd + 4);
    const std::uint16_t central_disk16 = u16(eocd + 6);
    const std::uint16_t disk_entries16 = u16(eocd + 8);
    const std::uint16_t total_entries16 = u16(eocd + 10);
    const std::uint32_t central_size32 = u32(eocd + 12);
    const std::uint32_t central_offset32 = u32(eocd + 16);

    const bool sentinel_present =
        disk16 == 0xffffU || central_disk16 == 0xffffU ||
        disk_entries16 == 0xffffU || total_entries16 == 0xffffU ||
        central_size32 == 0xffffffffU || central_offset32 == 0xffffffffU;

    const auto legacy_directory = [&]() -> EndDirectory {
        if (disk16 != 0 || central_disk16 != 0 ||
            disk_entries16 != total_entries16) {
            issue(report, "multidisk_unsupported",
                  "multi-disk ZIP archives are unsupported");
        }
        return {
            total_entries16,
            central_size32,
            central_offset32,
            eocd_offset,
        };
    };

    std::array<std::byte, zip64_locator_size> locator{};
    std::uint64_t locator_offset = 0;
    bool locator_signature_present = false;
    if (eocd_offset >= zip64_locator_size) {
        locator_offset = eocd_offset - zip64_locator_size;
        locator_signature_present = file.read_exact(locator_offset, locator) &&
            u32(locator.data()) == zip64_locator_signature;
    }
    if (!locator_signature_present) {
        if (sentinel_present) {
            report.zip64 = true;
            issue(report, "zip64_locator_missing",
                  "legacy end record contains ZIP64 sentinels without an adjacent locator");
            return std::nullopt;
        }
        return legacy_directory();
    }

    const std::uint32_t locator_disk = u32(locator.data() + 4);
    const std::uint64_t zip64_offset = u64(locator.data() + 8);
    const std::uint32_t total_disks = u32(locator.data() + 16);
    std::array<std::byte, 12> prefix{};
    const bool prefix_present = file.read_exact(zip64_offset, prefix) &&
        u32(prefix.data()) == zip64_eocd_signature;

    // The locator signature can occur naturally in the final 20 bytes of an
    // ordinary central-directory comment. Without legacy ZIP64 sentinels,
    // commit to ZIP64 only after the referenced record is structurally
    // plausible and ends exactly at the adjacent locator.
    if (!prefix_present) {
        if (!sentinel_present) {
            return legacy_directory();
        }
        report.zip64 = true;
        issue(report, "zip64_eocd_missing",
              "ZIP64 locator does not reference a readable ZIP64 end record");
        return std::nullopt;
    }

    const std::uint64_t record_payload_size = u64(prefix.data() + 4);
    std::uint64_t record_size = 0;
    std::uint64_t record_end = 0;
    const bool plausible_record =
        record_payload_size >= zip64_eocd_minimum_payload_size &&
        checked_add(record_payload_size, 12, record_size) &&
        checked_add(zip64_offset, record_size, record_end) &&
        record_end <= file.size() && record_end == locator_offset &&
        locator_disk == 0 && total_disks == 1;
    if (!plausible_record && !sentinel_present) {
        return legacy_directory();
    }

    report.zip64 = true;
    if (locator_disk != 0 || total_disks != 1) {
        issue(report, "multidisk_unsupported",
              "ZIP64 locator describes a split or spanned archive");
    }
    if (record_payload_size < zip64_eocd_minimum_payload_size) {
        issue(report, "zip64_eocd_short",
              "ZIP64 end record is shorter than its fixed version-1 fields");
        return std::nullopt;
    }
    if (!checked_add(record_payload_size, 12, record_size)) {
        issue(report, "zip64_eocd_range",
              "ZIP64 end record size overflows 64-bit range accounting");
        return std::nullopt;
    }
    if (record_size > limits.max_zip64_eocd_bytes) {
        issue(report, "zip64_eocd_limit",
              "ZIP64 end record exceeds the configured byte limit");
        return std::nullopt;
    }
    if (!checked_add(zip64_offset, record_size, record_end) ||
        record_end > file.size()) {
        issue(report, "zip64_eocd_range",
              "ZIP64 end record range is outside the archive");
        return std::nullopt;
    }
    if (record_end != locator_offset) {
        issue(report, "zip64_locator_gap",
              "ZIP64 end record does not end immediately before its locator");
        return std::nullopt;
    }

    std::array<std::byte, zip64_eocd_minimum_size> fixed{};
    if (!file.read_exact(zip64_offset, fixed)) {
        issue(report, "zip64_eocd_truncated",
              "ZIP64 end record fixed fields are truncated");
        return std::nullopt;
    }
    const std::uint16_t version_needed = u16(fixed.data() + 14);
    const std::uint32_t disk = u32(fixed.data() + 16);
    const std::uint32_t central_disk = u32(fixed.data() + 20);
    const std::uint64_t disk_entries = u64(fixed.data() + 24);
    const std::uint64_t total_entries = u64(fixed.data() + 32);
    const std::uint64_t central_size = u64(fixed.data() + 40);
    const std::uint64_t central_offset = u64(fixed.data() + 48);

    report.zip64_eocd_offset = zip64_offset;
    report.zip64_eocd_size = record_size;
    if (version_needed < 45U) {
        issue(report, "zip64_version_needed",
              "ZIP64 end record declares a version-needed value below 4.5");
    }
    if (disk != 0 || central_disk != 0 || disk_entries != total_entries) {
        issue(report, "multidisk_unsupported",
              "ZIP64 end record describes a split or spanned archive");
    }
    if (!eocd_field_matches(disk, disk16, 0xffffU) ||
        !eocd_field_matches(central_disk, central_disk16, 0xffffU) ||
        !eocd_field_matches(disk_entries, disk_entries16, 0xffffU) ||
        !eocd_field_matches(total_entries, total_entries16, 0xffffU) ||
        !eocd_field_matches(central_size, central_size32, 0xffffffffU) ||
        !eocd_field_matches(central_offset, central_offset32, 0xffffffffU)) {
        issue(report, "zip64_eocd_mismatch",
              "legacy and ZIP64 end records disagree on archive metadata");
    }

    return EndDirectory{
        total_entries,
        central_size,
        central_offset,
        zip64_offset,
    };
}

struct Zip64ExtraResult {
    std::size_t fields{};
    bool complete{true};
    bool exact{true};
};

[[nodiscard]] bool take_u64(
    std::span<const std::byte> payload,
    std::size_t& cursor,
    std::uint64_t& value) noexcept {
    if (cursor > payload.size() || payload.size() - cursor < 8) {
        return false;
    }
    value = u64(payload.data() + static_cast<std::ptrdiff_t>(cursor));
    cursor += 8;
    return true;
}

[[nodiscard]] bool take_u32(
    std::span<const std::byte> payload,
    std::size_t& cursor,
    std::uint32_t& value) noexcept {
    if (cursor > payload.size() || payload.size() - cursor < 4) {
        return false;
    }
    value = u32(payload.data() + static_cast<std::ptrdiff_t>(cursor));
    cursor += 4;
    return true;
}

void resolve_central_zip64(
    std::span<const std::byte> payload,
    bool need_uncompressed,
    bool need_compressed,
    bool need_offset,
    bool need_disk,
    CentralEntry& entry,
    Zip64ExtraResult& result) noexcept {
    std::size_t cursor = 0;
    if (need_uncompressed && !take_u64(payload, cursor, entry.uncompressed_size)) {
        result.complete = false;
        return;
    }
    if (need_compressed && !take_u64(payload, cursor, entry.compressed_size)) {
        result.complete = false;
        return;
    }
    if (need_offset && !take_u64(payload, cursor, entry.local_offset)) {
        result.complete = false;
        return;
    }
    if (need_disk && !take_u32(payload, cursor, entry.start_disk)) {
        result.complete = false;
        return;
    }
    result.exact = cursor == payload.size();
}

void resolve_local_zip64(
    std::span<const std::byte> payload,
    std::uint64_t& uncompressed_size,
    std::uint64_t& compressed_size,
    Zip64ExtraResult& result) noexcept {
    std::size_t cursor = 0;
    // APPNOTE requires a local ZIP64 extra field to carry both sizes whenever
    // either 32-bit local size field is a placeholder. Parsing only the
    // placeholder-corresponding value accepts malformed one-value fields and
    // rejects valid one-sentinel/two-value records.
    if (!take_u64(payload, cursor, uncompressed_size)) {
        result.complete = false;
        return;
    }
    if (!take_u64(payload, cursor, compressed_size)) {
        result.complete = false;
        return;
    }
    result.exact = cursor == payload.size();
}

[[nodiscard]] std::size_t descriptor_size(
    const PinnedFile& file,
    std::uint64_t offset,
    const CentralEntry& entry,
    std::string_view name,
    ZipReport& report) {
    std::array<std::byte, 24> bytes{};
    const std::uint64_t available = file.size() >= offset ? file.size() - offset : 0;
    const std::size_t wanted = static_cast<std::size_t>(
        std::min<std::uint64_t>(bytes.size(), available));
    const bool wide = has_zip64_state(entry, zip64_descriptor);
    const std::size_t unsigned_size = wide ? 20U : 12U;
    const std::size_t signed_size = wide ? 24U : 16U;
    if (wanted < unsigned_size ||
        !file.read_exact(offset, std::span<std::byte>(bytes).first(wanted))) {
        issue(report, "descriptor_truncated", "data descriptor is truncated", name);
        return 0;
    }

    const std::uint32_t first = u32(bytes.data());
    bool unsigned_valid = false;
    bool signed_valid = false;
    if (wide) {
        unsigned_valid = first == entry.crc &&
            u64(bytes.data() + 4) == entry.compressed_size &&
            u64(bytes.data() + 12) == entry.uncompressed_size;
        if (wanted >= signed_size) {
            signed_valid = first == descriptor_signature &&
                u32(bytes.data() + 4) == entry.crc &&
                u64(bytes.data() + 8) == entry.compressed_size &&
                u64(bytes.data() + 16) == entry.uncompressed_size;
        }
    } else {
        unsigned_valid = first == entry.crc &&
            u32(bytes.data() + 4) == entry.compressed_size &&
            u32(bytes.data() + 8) == entry.uncompressed_size;
        if (wanted >= signed_size) {
            signed_valid = first == descriptor_signature &&
                u32(bytes.data() + 4) == entry.crc &&
                u32(bytes.data() + 8) == entry.compressed_size &&
                u32(bytes.data() + 12) == entry.uncompressed_size;
        }
    }

    if (unsigned_valid && signed_valid) {
        issue(report, "descriptor_signature_ambiguity",
              "descriptor is valid both unsigned and signed; selected the unsigned form",
              name, false);
        return unsigned_size;
    }
    if (unsigned_valid) {
        return unsigned_size;
    }
    if (signed_valid) {
        return signed_size;
    }
    issue(report, "descriptor_mismatch",
          "data descriptor does not match central metadata", name);
    return 0;
}

struct PayloadDigest {
    std::array<std::byte, 32> digest{};
    std::uint32_t span_index{};
};

static_assert(std::is_trivially_copyable_v<PayloadDigest>);

[[nodiscard]] std::uint64_t payload_offset(const Span& span) noexcept {
    return span.start + span.payload_delta;
}

template <class... ScratchVectors>
void observe_payload_probe_scratch(
    ZipReport& report,
    const ScratchVectors&... scratch) noexcept {
    std::uint64_t total = 0;
    const auto add = [&](std::uint64_t value) {
        if (value > std::numeric_limits<std::uint64_t>::max() - total) {
            total = std::numeric_limits<std::uint64_t>::max();
        } else {
            total += value;
        }
    };
    (add(vector_storage_bytes(scratch)), ...);
    report.payload_probe_peak_scratch_bytes = std::max(
        report.payload_probe_peak_scratch_bytes, total);
}

[[nodiscard]] bool payload_probe_eligible(
    const CentralEntry& entry,
    const ZipLimits& limits) noexcept {
    return (entry.flags & 0x0001U) == 0U &&
        entry.compressed_size != 0U &&
        entry.uncompressed_size != 0U &&
        entry.compressed_size >= limits.min_payload_probe_bytes;
}

[[nodiscard]] bool add_probe_read_bytes(
    ZipReport& report,
    std::uint64_t value) noexcept {
    return checked_add_assign(report.payload_probe_read_bytes, value);
}

[[nodiscard]] std::optional<std::array<std::byte, 32>> hash_payload_range(
    const PinnedFile& file,
    const Span& span,
    std::uint64_t size,
    std::vector<std::byte>& buffer,
    ZipReport& report) {
    Sha256 hash;
    std::uint64_t done = 0;
    while (done < size) {
        const std::size_t request = static_cast<std::size_t>(
            std::min<std::uint64_t>(size - done, buffer.size()));
        std::uint64_t position = 0;
        if (request == 0U ||
            !checked_add(payload_offset(span), done, position) ||
            !file.read_exact(position, std::span<std::byte>(buffer).first(request)) ||
            !add_probe_read_bytes(report, request)) {
            issue(report, "payload_probe_read",
                  "unable to read a validated payload range during duplicate nomination");
            return std::nullopt;
        }
        hash.update(std::span<const std::byte>(buffer).first(request));
        done += request;
    }
    return hash.finish();
}

[[nodiscard]] std::optional<bool> payload_ranges_equal(
    const PinnedFile& file,
    const Span& left,
    const Span& right,
    std::uint64_t size,
    std::vector<std::byte>& left_buffer,
    std::vector<std::byte>& right_buffer,
    ZipReport& report) {
    std::uint64_t done = 0;
    while (done < size) {
        const std::size_t request = static_cast<std::size_t>(
            std::min<std::uint64_t>(size - done, left_buffer.size()));
        std::uint64_t left_position = 0;
        std::uint64_t right_position = 0;
        std::uint64_t read_bytes = 0;
        if (request == 0U ||
            !checked_add(payload_offset(left), done, left_position) ||
            !checked_add(payload_offset(right), done, right_position) ||
            !file.read_exact(
                left_position, std::span<std::byte>(left_buffer).first(request)) ||
            !file.read_exact(
                right_position, std::span<std::byte>(right_buffer).first(request)) ||
            !checked_multiply(request, 2U, read_bytes) ||
            !add_probe_read_bytes(report, read_bytes)) {
            issue(report, "payload_probe_read",
                  "unable to compare validated payload ranges during duplicate nomination");
            return std::nullopt;
        }
        if (!std::equal(
                left_buffer.begin(),
                left_buffer.begin() + static_cast<std::ptrdiff_t>(request),
                right_buffer.begin())) {
            return false;
        }
        done += request;
    }
    return true;
}

[[nodiscard]] bool same_content_nomination(
    const CentralEntry& left,
    const CentralEntry& right) noexcept {
    return left.uncompressed_size == right.uncompressed_size &&
        left.crc == right.crc;
}

[[nodiscard]] bool same_payload_candidate(
    const CentralEntry& left,
    const CentralEntry& right) noexcept {
    return same_content_nomination(left, right) &&
        left.method == right.method &&
        left.compressed_size == right.compressed_size;
}

[[nodiscard]] bool add_probe_product(
    ZipReport& report,
    std::uint64_t factor,
    std::uint64_t size,
    std::uint64_t& target,
    std::string_view description) {
    std::uint64_t product = 0;
    if (!checked_multiply(factor, size, product) ||
        !checked_add_assign(target, product)) {
        issue(report, "payload_probe_accounting_overflow",
              std::string(description) + " exceeds 64-bit accounting");
        return false;
    }
    return true;
}

void probe_payload_duplicates(
    const PinnedFile& file,
    const ZipLimits& limits,
    const std::vector<CentralEntry>& entries,
    const std::vector<char>& names,
    std::vector<Span>& spans,
    ZipReport& report) {
    report.payload_probe_enabled = true;
    if (limits.payload_probe_chunk_bytes == 0U) {
        issue(report, "payload_probe_configuration",
              "payload duplicate nomination requires a nonzero chunk size");
        return;
    }
    if (spans.size() > std::numeric_limits<std::uint32_t>::max()) {
        issue(report, "payload_probe_configuration",
              "payload duplicate nomination cannot index this many local spans");
        return;
    }

    // Largest logical candidates are considered first. Within each CRC/size
    // nomination, equal method/representation sizes remain contiguous so the
    // exact-payload proof does not require another global allocation.
    std::sort(spans.begin(), spans.end(), [&](const Span& left, const Span& right) {
        const CentralEntry& a = entries[left.entry_index];
        const CentralEntry& b = entries[right.entry_index];
        const bool a_eligible = payload_probe_eligible(a, limits);
        const bool b_eligible = payload_probe_eligible(b, limits);
        if (a_eligible != b_eligible) return a_eligible;
        if (a.uncompressed_size != b.uncompressed_size) {
            return a.uncompressed_size > b.uncompressed_size;
        }
        if (a.crc != b.crc) return a.crc < b.crc;
        if (a.method != b.method) return a.method < b.method;
        if (a.compressed_size != b.compressed_size) {
            return a.compressed_size > b.compressed_size;
        }
        return left.entry_index < right.entry_index;
    });

    std::vector<std::byte> hash_buffer;
    std::vector<std::byte> compare_buffer;
    std::vector<PayloadDigest> digests;
    std::size_t content_begin = 0;
    while (content_begin < spans.size()) {
        const CentralEntry& first_content = entries[spans[content_begin].entry_index];
        if (!payload_probe_eligible(first_content, limits)) break;

        std::size_t content_end = content_begin + 1U;
        while (content_end < spans.size() &&
               same_content_nomination(
                   first_content, entries[spans[content_end].entry_index])) {
            ++content_end;
        }
        const std::size_t content_count = content_end - content_begin;
        if (content_count >= 2U) {
            ++report.content_nomination_groups;
            report.content_nomination_entries += content_count;
            if (!add_probe_product(
                    report,
                    static_cast<std::uint64_t>(content_count - 1U),
                    first_content.uncompressed_size,
                    report.content_nomination_repeated_uncompressed_bytes,
                    "content-nomination repeated logical bytes")) {
                return;
            }
        }

        std::size_t payload_begin = content_begin;
        while (payload_begin < content_end) {
            const CentralEntry& first_payload = entries[spans[payload_begin].entry_index];
            std::size_t payload_end = payload_begin + 1U;
            while (payload_end < content_end &&
                   same_payload_candidate(
                       first_payload, entries[spans[payload_end].entry_index])) {
                ++payload_end;
            }
            const std::size_t payload_count = payload_end - payload_begin;
            if (payload_count < 2U) {
                payload_begin = payload_end;
                continue;
            }

            ++report.payload_candidate_groups;
            report.payload_candidate_entries += payload_count;
            if (!add_probe_product(
                    report,
                    static_cast<std::uint64_t>(payload_count),
                    first_payload.compressed_size,
                    report.payload_candidate_compressed_bytes,
                    "payload-candidate compressed bytes")) {
                return;
            }

            std::uint64_t worst_factor = 0;
            std::uint64_t worst_read_bytes = 0;
            const std::uint64_t count64 = static_cast<std::uint64_t>(payload_count);
            if (!checked_multiply(count64, 3U, worst_factor) ||
                worst_factor < 2U ||
                !checked_multiply(
                    worst_factor - 2U,
                    first_payload.compressed_size,
                    worst_read_bytes)) {
                issue(report, "payload_probe_accounting_overflow",
                      "payload-group proof cost exceeds 64-bit accounting");
                return;
            }
            const bool group_limit =
                payload_count > limits.max_payload_probe_group_entries;
            const bool read_limit =
                report.payload_probe_read_bytes > limits.max_payload_probe_read_bytes ||
                worst_read_bytes >
                    limits.max_payload_probe_read_bytes - report.payload_probe_read_bytes;
            if (group_limit || read_limit) {
                if (read_limit) report.payload_probe_budget_exhausted = true;
                ++report.payload_probe_skipped_groups;
                report.payload_probe_skipped_entries += payload_count;
                if (!add_probe_product(
                        report,
                        count64,
                        first_payload.compressed_size,
                        report.payload_probe_skipped_compressed_bytes,
                        "skipped payload-candidate bytes")) {
                    return;
                }
                payload_begin = payload_end;
                continue;
            }

            const std::size_t chunk = static_cast<std::size_t>(
                std::min<std::uint64_t>(
                    first_payload.compressed_size,
                    limits.payload_probe_chunk_bytes));
            hash_buffer.resize(chunk);
            digests.clear();
            digests.reserve(payload_count);
            observe_payload_probe_scratch(
                report, hash_buffer, compare_buffer, digests);
            for (std::size_t index = payload_begin; index < payload_end; ++index) {
                const auto digest = hash_payload_range(
                    file,
                    spans[index],
                    first_payload.compressed_size,
                    hash_buffer,
                    report);
                if (!digest) return;
                digests.push_back({
                    *digest,
                    static_cast<std::uint32_t>(index),
                });
                observe_payload_probe_scratch(
                    report, hash_buffer, compare_buffer, digests);
            }
            ++report.payload_hashed_groups;
            report.payload_hashed_entries += payload_count;

            std::sort(digests.begin(), digests.end(), [](const auto& left, const auto& right) {
                if (left.digest != right.digest) {
                    return std::lexicographical_compare(
                        left.digest.begin(), left.digest.end(),
                        right.digest.begin(), right.digest.end());
                }
                return left.span_index < right.span_index;
            });
            std::size_t digest_begin = 0;
            while (digest_begin < digests.size()) {
                std::size_t digest_end = digest_begin + 1U;
                while (digest_end < digests.size() &&
                       digests[digest_end].digest == digests[digest_begin].digest) {
                    ++digest_end;
                }
                if (digest_end - digest_begin >= 2U) {
                    compare_buffer.resize(chunk);
                    observe_payload_probe_scratch(
                        report, hash_buffer, compare_buffer, digests);
                    const Span& representative = spans[digests[digest_begin].span_index];
                    std::size_t matching = 1U;
                    bool collision = false;
                    for (std::size_t index = digest_begin + 1U;
                         index < digest_end; ++index) {
                        const auto equal = payload_ranges_equal(
                            file,
                            representative,
                            spans[digests[index].span_index],
                            first_payload.compressed_size,
                            hash_buffer,
                            compare_buffer,
                            report);
                        if (!equal) return;
                        if (*equal) {
                            ++matching;
                        } else {
                            collision = true;
                        }
                    }
                    if (matching >= 2U) {
                        ++report.verified_payload_groups;
                        report.verified_payload_entries += matching;
                        report.verified_duplicate_entries += matching - 1U;
                        if (!add_probe_product(
                                report,
                                static_cast<std::uint64_t>(matching - 1U),
                                first_payload.compressed_size,
                                report.verified_repeated_compressed_bytes,
                                "verified repeated compressed bytes") ||
                            !add_probe_product(
                                report,
                                static_cast<std::uint64_t>(matching - 1U),
                                first_payload.uncompressed_size,
                                report.verified_repeated_uncompressed_bytes,
                                "verified repeated logical bytes")) {
                            return;
                        }
                    }
                    if (collision) {
                        ++report.payload_digest_collision_groups;
                        issue(
                            report,
                            "payload_digest_collision",
                            "equal SHA-256 payload digests failed exact byte verification",
                            entry_name(
                                entries[representative.entry_index], names),
                            false);
                    }
                }
                digest_begin = digest_end;
            }
            payload_begin = payload_end;
        }
        content_begin = content_end;
    }
}

} // namespace

bool ZipReport::ok() const noexcept {
    return suppressed_fatal_issues == 0 &&
        std::none_of(issues.begin(), issues.end(), [](const ZipIssue& value) {
            return value.fatal;
        });
}

namespace {

ZipReport preflight_zip_snapshot(
    const std::filesystem::path& path,
    const ZipLimits& limits,
    const PinnedFile& file) {
    ZipReport report;
    report.path = path;
    report.file_size = file.size();
    report.issue_limit = limits.max_issues;
    report.payload_probe_enabled = limits.probe_exact_payload_duplicates;
    if (file.size() < eocd_fixed_size) {
        issue(report, "eocd_missing", "file is too small to contain a ZIP end record");
        return report;
    }

    const std::uint64_t tail_size_u64 = std::min<std::uint64_t>(
        file.size(), 65535U + eocd_fixed_size);
    const std::size_t tail_size = static_cast<std::size_t>(tail_size_u64);
    const std::uint64_t tail_offset = file.size() - tail_size_u64;
    const std::vector<std::byte> tail = file.read(tail_offset, tail_size);
    std::optional<std::size_t> eocd_at;
    for (std::size_t position = tail.size() - eocd_fixed_size + 1; position-- > 0;) {
        if (u32(tail.data() + static_cast<std::ptrdiff_t>(position)) != eocd_signature) {
            continue;
        }
        const std::uint16_t comment_length = u16(
            tail.data() + static_cast<std::ptrdiff_t>(position + 20));
        if (position + eocd_fixed_size + comment_length == tail.size()) {
            eocd_at = position;
            break;
        }
    }
    if (!eocd_at) {
        issue(report, "eocd_missing", "no terminal ZIP end-of-central-directory record found");
        return report;
    }

    const std::byte* eocd = tail.data() + static_cast<std::ptrdiff_t>(*eocd_at);
    const std::uint64_t eocd_absolute = tail_offset + *eocd_at;
    const std::optional<EndDirectory> directory = resolve_end_directory(
        file, eocd_absolute, eocd, limits, report);
    if (!directory) {
        return report;
    }
    if (directory->entries > limits.max_entries ||
        directory->entries > std::numeric_limits<std::size_t>::max() ||
        directory->entries > std::numeric_limits<std::uint32_t>::max()) {
        issue(report, "entry_limit", "entry count exceeds configured or addressable limit");
        return report;
    }
    if (directory->central_size > limits.max_central_directory_bytes) {
        issue(report, "central_limit", "central directory exceeds configured byte limit");
        return report;
    }
    // Reject an impossible record count before reserving entry metadata. Every
    // central record consumes at least its 46-byte fixed header, so this is a
    // structural proof as well as an allocation bound. Without it, a hostile
    // but configured-as-allowed EOCD count could force a large reserve before
    // the first central signature is examined.
    if (directory->entries > directory->central_size / central_fixed_size) {
        issue(report, "central_entry_count_range",
              "central-directory byte size cannot contain the declared entry count");
        return report;
    }

    report.entries = static_cast<std::size_t>(directory->entries);
    report.central_directory_size = directory->central_size;
    report.central_directory_offset = directory->central_offset;
    std::uint64_t central_end = 0;
    if (!checked_add(
            report.central_directory_offset,
            report.central_directory_size,
            central_end) ||
        central_end > file.size()) {
        issue(report, "central_range", "central directory range is outside the file");
        return report;
    }
    if (central_end != directory->central_end_anchor) {
        issue(report, "central_end_gap",
              "central directory does not end immediately before its terminal record");
    }

    std::vector<CentralEntry> entries;
    entries.reserve(report.entries);
    std::vector<char> central_names;
    // A small bounded reserve avoids geometric name-arena growth on the
    // ordinary datacube shape, where almost every variable central byte is a
    // name. The cap prevents a hostile extra/comment-heavy directory from
    // forcing a large speculative allocation before those records are parsed.
    constexpr std::uint64_t eager_name_reserve_limit = 1024ULL * 1024ULL;
    const std::uint64_t fixed_central_bytes =
        static_cast<std::uint64_t>(report.entries) * central_fixed_size;
    if (report.central_directory_size >= fixed_central_bytes) {
        const std::uint64_t reserve_hint = std::min({
            report.central_directory_size - fixed_central_bytes,
            limits.max_total_name_bytes,
            eager_name_reserve_limit,
            static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max()),
        });
        central_names.reserve(static_cast<std::size_t>(reserve_hint));
    }
    report.central_entry_descriptor_bytes = sizeof(CentralEntry);
    report.central_entry_storage_bytes = vector_storage_bytes(entries);
    observe_parser_storage(report, entries, central_names);
    std::map<std::uint16_t, ZipMethodCount> method_counts;
    std::uint64_t central_cursor = report.central_directory_offset;
    std::uint64_t central_remaining = report.central_directory_size;
    {
        // The extra-field scratch lifetime ends with the central stream. It is
        // not retained while duplicate-name sorting and local-record auditing
        // allocate their own bounded work vectors.
        std::vector<std::byte> central_extra_buffer;
        for (std::size_t index = 0; index < report.entries; ++index) {
            (void)index;
            if (central_remaining < central_fixed_size) {
                issue(report, "central_entry_malformed",
                      "central directory entry is truncated");
                return report;
            }

            std::array<std::byte, central_fixed_size> fixed{};
            if (!file.read_exact(central_cursor, fixed) ||
                u32(fixed.data()) != central_signature) {
                issue(report, "central_entry_malformed",
                      "central directory entry has a bad signature or is unreadable");
                return report;
            }
            const std::byte* header = fixed.data();
            CentralEntry entry;
            entry.version_made_by = u16(header + 4);
            entry.version_needed = u16(header + 6);
            entry.flags = u16(header + 8);
            entry.method = u16(header + 10);
            entry.crc = u32(header + 16);
            const std::uint32_t compressed32 = u32(header + 20);
            const std::uint32_t uncompressed32 = u32(header + 24);
            entry.compressed_size = compressed32;
            entry.uncompressed_size = uncompressed32;
            const std::uint16_t name_length = u16(header + 28);
            const std::uint16_t extra_length = u16(header + 30);
            const std::uint16_t comment_length = u16(header + 32);
            const std::uint16_t start_disk16 = u16(header + 34);
            entry.start_disk = start_disk16;
            entry.external_attributes = u32(header + 38);
            const std::uint32_t local_offset32 = u32(header + 42);
            entry.local_offset = local_offset32;
            if (compressed32 == 0xffffffffU || uncompressed32 == 0xffffffffU) {
                set_zip64_state(entry, zip64_sizes);
                set_zip64_state(entry, zip64_descriptor);
            }
            if (local_offset32 == 0xffffffffU) {
                set_zip64_state(entry, zip64_offset);
            }
            if (start_disk16 == 0xffffU) {
                set_zip64_state(entry, zip64_disk);
            }

            std::uint64_t entry_size = central_fixed_size;
            if (!checked_add(entry_size, name_length, entry_size) ||
                !checked_add(entry_size, extra_length, entry_size) ||
                !checked_add(entry_size, comment_length, entry_size) ||
                entry_size > central_remaining) {
                issue(report, "central_entry_range",
                      "central directory entry lengths exceed the directory");
                return report;
            }
            if (name_length > limits.max_name_bytes) {
                issue(report, "name_limit", "entry name exceeds configured byte limit");
                return report;
            }
            std::uint64_t next_name_bytes = 0;
            if (!checked_add(report.central_name_bytes, name_length, next_name_bytes) ||
                next_name_bytes > limits.max_total_name_bytes ||
                next_name_bytes > central_names.max_size()) {
                issue(report, "name_storage_limit",
                      "aggregate central-directory name bytes exceed configured or addressable limit");
                return report;
            }
            const std::size_t name_offset = central_names.size();
            entry.name_offset = name_offset;
            entry.name_length = name_length;
            central_names.resize(static_cast<std::size_t>(next_name_bytes));
            report.central_name_bytes = next_name_bytes;

            report.central_parser_peak_read_bytes = std::max({
                report.central_parser_peak_read_bytes,
                central_fixed_size,
                static_cast<std::size_t>(name_length),
                static_cast<std::size_t>(extra_length),
            });
            if (name_length != 0U) {
                file.read_into(
                    central_cursor + central_fixed_size,
                    std::as_writable_bytes(std::span<char>(
                        central_names.data() + name_offset,
                        name_length)));
            }
            const std::string_view name = entry_name(entry, central_names);
            central_extra_buffer.resize(extra_length);
            if (extra_length != 0U) {
                file.read_into(
                    central_cursor + central_fixed_size + name_length,
                    central_extra_buffer);
            }
            observe_parser_storage(
                report, entries, central_names, central_extra_buffer);

            const std::span<const std::byte> central_extra(central_extra_buffer);
            Zip64ExtraResult central_zip64;
            const bool central_zip64_required =
                has_zip64_state(entry, zip64_sizes) ||
                has_zip64_state(entry, zip64_offset) ||
                has_zip64_state(entry, zip64_disk);
            const bool central_extra_valid = visit_extra_fields(
                central_extra, "central", name, report,
                [&](std::uint16_t identifier, std::span<const std::byte> payload) {
                    if (identifier != 0x0001U) {
                        return;
                    }
                    ++central_zip64.fields;
                    report.zip64 = true;
                    set_zip64_state(entry, zip64_entry);
                    // APPNOTE selects 64-bit data-descriptor sizes whenever the
                    // ZIP64 extended-information field is present for the file,
                    // even when all resolved sizes fit in the legacy fields.
                    set_zip64_state(entry, zip64_descriptor);
                    if (central_zip64.fields == 1U && central_zip64_required) {
                        resolve_central_zip64(
                            payload,
                            uncompressed32 == 0xffffffffU,
                            compressed32 == 0xffffffffU,
                            local_offset32 == 0xffffffffU,
                            start_disk16 == 0xffffU,
                            entry,
                            central_zip64);
                    } else if (central_zip64.fields == 1U) {
                        central_zip64.exact = payload.empty();
                    }
                });
            if (central_zip64.fields > 1U) {
                issue(report, "central_zip64_duplicate",
                      "central entry contains more than one ZIP64 extra field", name);
            }
            if (central_zip64.fields != 0U && entry.version_needed < 45U) {
                issue(report, "zip64_version_needed",
                      "ZIP64 entry declares a version-needed value below 4.5", name);
            }
            if (central_zip64_required) {
                report.zip64 = true;
                set_zip64_state(entry, zip64_entry);
                if (!central_extra_valid || central_zip64.fields == 0U ||
                    !central_zip64.complete) {
                    issue(report, "central_zip64_missing",
                          "central ZIP64 placeholders lack a complete ZIP64 extra field",
                          name);
                    return report;
                }
                if (!central_zip64.exact) {
                    issue(report, "central_zip64_payload",
                          "central ZIP64 extra field contains unexpected trailing values",
                          name);
                }
            } else if (central_zip64.fields == 1U) {
                issue(report, "central_zip64_unneeded",
                      "central ZIP64 extra field is present without placeholder fields",
                      name, false);
            }
            if (entry.start_disk != 0U) {
                issue(report, "entry_multidisk", "entry starts on a nonzero disk", name);
            }
            if (has_zip64_state(entry, zip64_entry)) {
                ++report.zip64_entries;
                set_zip64_state(entry, zip64_counted);
            }
            if ((entry.flags & 0x0001U) != 0U) {
                ++report.encrypted_entries;
                issue(report, "encrypted_entry", "encrypted ZIP entries are unsupported",
                      name, limits.reject_encryption);
            }
            if ((entry.flags & 0x0008U) != 0U) {
                ++report.data_descriptor_entries;
            }
            std::string path_reason;
            if (path_unsafe(name, path_reason)) {
                ++report.unsafe_paths;
                issue(report, "unsafe_path", path_reason, name);
            }
            audit_entry_type(entry, name, limits, report);

            entries.push_back(entry);
            observe_parser_storage(
                report, entries, central_names, central_extra_buffer);
            const std::string_view stored_name = entry_name(entries.back(), central_names);
            if (!checked_add_assign(
                    report.compressed_bytes, entries.back().compressed_size) ||
                !checked_add_assign(
                    report.uncompressed_bytes, entries.back().uncompressed_size)) {
                issue(report, "aggregate_size_overflow",
                      "aggregate central-directory sizes exceed 64-bit accounting",
                      stored_name);
                return report;
            }
            auto [method_it, inserted] = method_counts.try_emplace(entries.back().method);
            if (inserted) {
                method_it->second.method = entries.back().method;
            }
            ++method_it->second.entries;
            if (!checked_add_assign(
                    method_it->second.compressed_bytes,
                    entries.back().compressed_size) ||
                !checked_add_assign(
                    method_it->second.uncompressed_bytes,
                    entries.back().uncompressed_size)) {
                issue(report, "method_size_overflow",
                      "per-method sizes exceed 64-bit accounting", stored_name);
                return report;
            }

            if (!checked_add(central_cursor, entry_size, central_cursor)) {
                issue(report, "central_entry_range",
                      "central directory cursor overflows 64-bit accounting");
                return report;
            }
            central_remaining -= entry_size;
        }
    }
    report.central_entry_storage_bytes = vector_storage_bytes(entries);
    report.central_name_storage_bytes = vector_storage_bytes(central_names);
    if (central_remaining != 0 || central_cursor != central_end) {
        issue(report, "central_trailing",
              "unparsed bytes remain in the central directory");
    }

    // Detect duplicate names without retaining a second copy of each name or
    // relying on string_view stability inside the entry vector.
    {
        std::vector<std::size_t> name_order(entries.size());
        observe_parser_storage(report, entries, central_names, name_order);
        std::iota(name_order.begin(), name_order.end(), 0);
        std::sort(name_order.begin(), name_order.end(), [&](std::size_t left, std::size_t right) {
            return entry_name(entries[left], central_names) <
                entry_name(entries[right], central_names);
        });
        for (std::size_t index = 1; index < name_order.size(); ++index) {
            const CentralEntry& prior = entries[name_order[index - 1]];
            const CentralEntry& current = entries[name_order[index]];
            if (entry_name(prior, central_names) == entry_name(current, central_names)) {
                ++report.duplicate_names;
                issue(report, "duplicate_name",
                      "duplicate central-directory entry name",
                      entry_name(current, central_names));
            }
        }
    }

    std::vector<Span> spans;
    spans.reserve(entries.size());
    std::vector<std::byte> local_name_buffer;
    std::vector<std::byte> local_extra_buffer;
    observe_parser_storage(
        report, entries, central_names, spans,
        local_name_buffer, local_extra_buffer);
    for (std::size_t entry_index = 0; entry_index < entries.size(); ++entry_index) {
        CentralEntry& entry = entries[entry_index];
        const std::string_view central_name = entry_name(entry, central_names);
        std::array<std::byte, local_fixed_size> local{};
        if (!file.read_exact(entry.local_offset, local)) {
            issue(report, "local_header_range", "local header is outside the file", central_name);
            continue;
        }
        if (u32(local.data()) != local_signature) {
            issue(report, "local_signature", "bad local-header signature", central_name);
            continue;
        }
        const std::uint16_t local_version_needed = u16(local.data() + 4);
        const std::uint16_t flags = u16(local.data() + 6);
        const std::uint16_t method = u16(local.data() + 8);
        const std::uint32_t crc = u32(local.data() + 14);
        const std::uint32_t compressed = u32(local.data() + 18);
        const std::uint32_t uncompressed = u32(local.data() + 22);
        const std::uint16_t name_length = u16(local.data() + 26);
        const std::uint16_t extra_length = u16(local.data() + 28);
        std::uint64_t data_offset = entry.local_offset;
        if (!checked_add(data_offset, local_fixed_size, data_offset) ||
            !checked_add(data_offset, name_length, data_offset) ||
            !checked_add(data_offset, extra_length, data_offset) ||
            data_offset > file.size()) {
            issue(report, "local_header_lengths", "local header lengths exceed the file", central_name);
            continue;
        }
        local_name_buffer.resize(name_length);
        if (name_length != 0) {
            file.read_into(entry.local_offset + local_fixed_size, local_name_buffer);
        }
        local_extra_buffer.resize(extra_length);
        if (extra_length != 0) {
            file.read_into(
                entry.local_offset + local_fixed_size + name_length,
                local_extra_buffer);
        }
        observe_parser_storage(
            report, entries, central_names, spans,
            local_name_buffer, local_extra_buffer);
        const std::string_view local_name = local_name_buffer.empty()
            ? std::string_view{}
            : std::string_view(
                reinterpret_cast<const char*>(local_name_buffer.data()),
                local_name_buffer.size());
        if (local_name != central_name) {
            issue(report, "local_name_mismatch", "local and central entry names differ", central_name);
        }
        if (flags != entry.flags) {
            issue(report, "local_flags_mismatch", "local and central flags differ", central_name);
        }
        if (method != entry.method) {
            issue(report, "local_method_mismatch",
                  "local and central compression methods differ", central_name);
        }
        std::uint64_t resolved_compressed = compressed;
        std::uint64_t resolved_uncompressed = uncompressed;
        const bool local_zip64_required =
            compressed == 0xffffffffU || uncompressed == 0xffffffffU;
        bool local_zip64_redundant_mismatch = false;
        bool local_zip64_descriptor_payload = false;
        Zip64ExtraResult local_zip64;
        const bool local_extra_valid = visit_extra_fields(
            local_extra_buffer, "local", central_name, report,
            [&](std::uint16_t identifier, std::span<const std::byte> payload) {
                if (identifier != 0x0001U) {
                    return;
                }
                ++local_zip64.fields;
                report.zip64 = true;
                set_zip64_state(entry, zip64_entry);
                // Presence, rather than a 32-bit sentinel alone, selects the
                // ZIP64 data-descriptor width for this member.
                set_zip64_state(entry, zip64_descriptor);
                if (local_zip64.fields == 1U &&
                    (local_zip64_required || (flags & 0x0008U) != 0U)) {
                    std::uint64_t zip64_uncompressed = 0;
                    std::uint64_t zip64_compressed = 0;
                    resolve_local_zip64(
                        payload,
                        zip64_uncompressed,
                        zip64_compressed,
                        local_zip64);
                    if (local_zip64.complete && local_zip64.exact) {
                        if (local_zip64_required) {
                            local_zip64_redundant_mismatch =
                                (uncompressed != 0xffffffffU &&
                                 zip64_uncompressed != uncompressed) ||
                                (compressed != 0xffffffffU &&
                                 zip64_compressed != compressed);
                            resolved_uncompressed = zip64_uncompressed;
                            resolved_compressed = zip64_compressed;
                        } else {
                            // A streamed small member may use a complete local
                            // ZIP64 size pair solely to select a 64-bit data
                            // descriptor. The descriptor and central metadata
                            // remain authoritative, so these early values are
                            // structurally checked but not trusted.
                            local_zip64_descriptor_payload = true;
                        }
                    }
                } else if (local_zip64.fields == 1U) {
                    local_zip64.exact = payload.empty();
                }
            });
        if (local_zip64.fields > 1U) {
            issue(report, "local_zip64_duplicate",
                  "local entry contains more than one ZIP64 extra field", central_name);
        }
        if (local_zip64.fields != 0U && local_version_needed < 45U) {
            issue(report, "zip64_version_needed",
                  "local ZIP64 entry declares a version-needed value below 4.5",
                  central_name);
        }
        if (local_zip64_required) {
            report.zip64 = true;
            set_zip64_state(entry, zip64_entry);
            if ((entry.flags & 0x0008U) != 0U) {
                set_zip64_state(entry, zip64_descriptor);
            }
            if (!local_extra_valid || local_zip64.fields == 0U ||
                !local_zip64.complete) {
                issue(report, "local_zip64_missing",
                      "local ZIP64 size placeholders lack the required two-value ZIP64 extra field",
                      central_name);
            }
            if (!local_zip64.exact) {
                issue(report, "local_zip64_payload",
                      "local ZIP64 extra field contains unexpected trailing values",
                      central_name);
            }
            if (local_zip64_redundant_mismatch) {
                issue(report, "local_zip64_redundant_mismatch",
                      "local ZIP64 size pair disagrees with a non-placeholder 32-bit local size",
                      central_name);
            }
        } else if (local_zip64.fields == 1U) {
            if ((flags & 0x0008U) != 0U &&
                (!local_zip64.complete || !local_zip64.exact ||
                 !local_zip64_descriptor_payload)) {
                issue(report, "local_zip64_payload",
                      "ZIP64 descriptor representation lacks one exact local uncompressed/compressed size pair",
                      central_name);
            }
            issue(report, "local_zip64_unneeded",
                  "local ZIP64 extra field is present without placeholder fields",
                  central_name, false);
        }
        if (has_zip64_state(entry, zip64_entry) &&
            !has_zip64_state(entry, zip64_counted)) {
            ++report.zip64_entries;
            set_zip64_state(entry, zip64_counted);
        }
        if ((entry.flags & 0x0008U) != 0U &&
            has_zip64_state(entry, zip64_descriptor)) {
            ++report.zip64_data_descriptor_entries;
        }
        const bool local_zip64_resolved = !local_zip64_required ||
            (local_extra_valid && local_zip64.fields == 1U &&
             local_zip64.complete && local_zip64.exact &&
             !local_zip64_redundant_mismatch);
        if ((entry.flags & 0x0008U) == 0U &&
            (crc != entry.crc || !local_zip64_resolved ||
             resolved_compressed != entry.compressed_size ||
             resolved_uncompressed != entry.uncompressed_size)) {
            issue(report, "local_size_mismatch",
                  "local CRC or sizes differ from central metadata", central_name);
        }

        std::uint64_t record_end = 0;
        if (!checked_add(data_offset, entry.compressed_size, record_end) ||
            record_end > file.size()) {
            issue(report, "entry_data_range", "compressed entry data is outside the file", central_name);
            continue;
        }
        if ((entry.flags & 0x0008U) != 0U) {
            const std::size_t descriptor = descriptor_size(
                file, record_end, entry, central_name, report);
            if (descriptor == 0 ||
                !checked_add(record_end, descriptor, record_end) ||
                record_end > file.size()) {
                continue;
            }
        }
        if (record_end > report.central_directory_offset) {
            issue(report, "entry_central_overlap",
                  "local entry record overlaps the central directory", central_name);
        }
        const std::uint64_t payload_delta = data_offset - entry.local_offset;
        if (payload_delta > std::numeric_limits<std::uint32_t>::max()) {
            issue(report, "local_header_lengths",
                  "local header prefix exceeds compact span accounting", central_name);
            continue;
        }
        spans.push_back({
            entry.local_offset,
            record_end,
            static_cast<std::uint32_t>(payload_delta),
            static_cast<std::uint32_t>(entry_index),
        });
        observe_parser_storage(
            report, entries, central_names, spans,
            local_name_buffer, local_extra_buffer);
    }

    std::sort(spans.begin(), spans.end(), [](const Span& left, const Span& right) {
        return left.start < right.start || (left.start == right.start && left.end < right.end);
    });
    // Compare each start against the furthest end of every preceding span, not
    // merely the immediately preceding span. The latter misses a later record
    // nested inside a long outer record when a short nested record sits between
    // them in start order.
    std::uint64_t covered_until = spans.empty() ? 0 : spans.front().end;
    for (std::size_t index = 1; index < spans.size(); ++index) {
        if (spans[index].start < covered_until) {
            issue(report, "entry_overlap", "local entry records overlap",
                  entry_name(entries[spans[index].entry_index], central_names));
        }
        covered_until = std::max(covered_until, spans[index].end);
    }

    // Payload nomination is deliberately downstream of every central/local,
    // range, descriptor, and overlap gate. It never tries to rescue or reason
    // about a structurally invalid archive.
    if (limits.probe_exact_payload_duplicates && report.ok()) {
        probe_payload_duplicates(
            file, limits, entries, central_names, spans, report);
    }

    for (const auto& [method, count] : method_counts) {
        (void)method;
        report.methods.push_back(count);
    }
    return report;
}
} // namespace

ZipReport preflight_zip(const std::filesystem::path& path, const ZipLimits& limits) {
    PinnedFile file(path);
    ZipReport report = preflight_zip_snapshot(path, limits, file);
    if (!file.unchanged()) {
        issue(report, "source_changed",
              "archive identity or content timestamp changed during preflight");
    }
    return report;
}

std::string zip_report_json(const ZipReport& report, bool pretty) {
    const std::string newline = pretty ? "\n" : "";
    const std::string indent1 = pretty ? "  " : "";
    const std::string indent2 = pretty ? "    " : "";
    std::ostringstream output;
    output << '{' << newline
           << indent1 << "\"schema\":\"bzip4.zip-preflight.v7\"," << newline
           << indent1 << "\"path\":\"" << json_escape(report.path.string()) << "\"," << newline
           << indent1 << "\"ok\":" << (report.ok() ? "true" : "false") << ',' << newline
           << indent1 << "\"file_size\":" << report.file_size << ',' << newline
           << indent1 << "\"entries\":" << report.entries << ',' << newline
           << indent1 << "\"compressed_bytes\":" << report.compressed_bytes << ',' << newline
           << indent1 << "\"uncompressed_bytes\":" << report.uncompressed_bytes << ',' << newline
           << indent1 << "\"central_directory_offset\":" << report.central_directory_offset << ',' << newline
           << indent1 << "\"central_directory_size\":" << report.central_directory_size << ',' << newline
           << indent1 << "\"central_name_bytes\":" << report.central_name_bytes << ',' << newline
           << indent1 << "\"central_parser_peak_read_bytes\":"
           << report.central_parser_peak_read_bytes << ',' << newline
           << indent1 << "\"duplicate_names\":" << report.duplicate_names << ',' << newline
           << indent1 << "\"unsafe_paths\":" << report.unsafe_paths << ',' << newline
           << indent1 << "\"encrypted_entries\":" << report.encrypted_entries << ',' << newline
           << indent1 << "\"data_descriptor_entries\":" << report.data_descriptor_entries << ',' << newline
           << indent1 << "\"regular_file_entries\":" << report.regular_file_entries << ',' << newline
           << indent1 << "\"directory_entries\":" << report.directory_entries << ',' << newline
           << indent1 << "\"symlink_entries\":" << report.symlink_entries << ',' << newline
           << indent1 << "\"special_file_entries\":" << report.special_file_entries << ',' << newline
           << indent1 << "\"unclassified_type_entries\":"
           << report.unclassified_type_entries << ',' << newline
           << indent1 << "\"entry_type_mismatches\":"
           << report.entry_type_mismatches << ',' << newline
           << indent1 << "\"issue_limit\":" << report.issue_limit << ',' << newline
           << indent1 << "\"suppressed_issues\":" << report.suppressed_issues << ',' << newline
           << indent1 << "\"suppressed_fatal_issues\":"
           << report.suppressed_fatal_issues << ',' << newline
           << indent1 << "\"zip64\":" << (report.zip64 ? "true" : "false") << ',' << newline
           << indent1 << "\"zip64_eocd_offset\":" << report.zip64_eocd_offset << ',' << newline
           << indent1 << "\"zip64_eocd_size\":" << report.zip64_eocd_size << ',' << newline
           << indent1 << "\"zip64_entries\":" << report.zip64_entries << ',' << newline
           << indent1 << "\"zip64_data_descriptor_entries\":"
           << report.zip64_data_descriptor_entries << ',' << newline
           << indent1 << "\"central_entry_descriptor_bytes\":"
           << report.central_entry_descriptor_bytes << ',' << newline
           << indent1 << "\"central_entry_storage_bytes\":"
           << report.central_entry_storage_bytes << ',' << newline
           << indent1 << "\"central_name_storage_bytes\":"
           << report.central_name_storage_bytes << ',' << newline
           << indent1 << "\"central_parser_peak_retained_bytes\":"
           << report.central_parser_peak_retained_bytes << ',' << newline
           << indent1 << "\"payload_probe_enabled\":"
           << (report.payload_probe_enabled ? "true" : "false") << ',' << newline
           << indent1 << "\"payload_probe_budget_exhausted\":"
           << (report.payload_probe_budget_exhausted ? "true" : "false") << ',' << newline
           << indent1 << "\"content_nomination_groups\":"
           << report.content_nomination_groups << ',' << newline
           << indent1 << "\"content_nomination_entries\":"
           << report.content_nomination_entries << ',' << newline
           << indent1 << "\"content_nomination_repeated_uncompressed_bytes\":"
           << report.content_nomination_repeated_uncompressed_bytes << ',' << newline
           << indent1 << "\"payload_candidate_groups\":"
           << report.payload_candidate_groups << ',' << newline
           << indent1 << "\"payload_candidate_entries\":"
           << report.payload_candidate_entries << ',' << newline
           << indent1 << "\"payload_candidate_compressed_bytes\":"
           << report.payload_candidate_compressed_bytes << ',' << newline
           << indent1 << "\"payload_hashed_groups\":"
           << report.payload_hashed_groups << ',' << newline
           << indent1 << "\"payload_hashed_entries\":"
           << report.payload_hashed_entries << ',' << newline
           << indent1 << "\"payload_probe_read_bytes\":"
           << report.payload_probe_read_bytes << ',' << newline
           << indent1 << "\"verified_payload_groups\":"
           << report.verified_payload_groups << ',' << newline
           << indent1 << "\"verified_payload_entries\":"
           << report.verified_payload_entries << ',' << newline
           << indent1 << "\"verified_duplicate_entries\":"
           << report.verified_duplicate_entries << ',' << newline
           << indent1 << "\"verified_repeated_compressed_bytes\":"
           << report.verified_repeated_compressed_bytes << ',' << newline
           << indent1 << "\"verified_repeated_uncompressed_bytes\":"
           << report.verified_repeated_uncompressed_bytes << ',' << newline
           << indent1 << "\"payload_probe_skipped_groups\":"
           << report.payload_probe_skipped_groups << ',' << newline
           << indent1 << "\"payload_probe_skipped_entries\":"
           << report.payload_probe_skipped_entries << ',' << newline
           << indent1 << "\"payload_probe_skipped_compressed_bytes\":"
           << report.payload_probe_skipped_compressed_bytes << ',' << newline
           << indent1 << "\"payload_digest_collision_groups\":"
           << report.payload_digest_collision_groups << ',' << newline
           << indent1 << "\"payload_probe_peak_scratch_bytes\":"
           << report.payload_probe_peak_scratch_bytes << ',' << newline
           << indent1 << "\"methods\":[";
    if (pretty && !report.methods.empty()) output << newline;
    for (std::size_t index = 0; index < report.methods.size(); ++index) {
        const ZipMethodCount& method = report.methods[index];
        output << indent2 << "{\"method\":" << method.method
               << ",\"entries\":" << method.entries
               << ",\"compressed_bytes\":" << method.compressed_bytes
               << ",\"uncompressed_bytes\":" << method.uncompressed_bytes << '}';
        if (index + 1 != report.methods.size()) output << ',';
        if (pretty) output << newline;
    }
    output << indent1 << "]," << newline << indent1 << "\"issues\":[";
    if (pretty && !report.issues.empty()) output << newline;
    for (std::size_t index = 0; index < report.issues.size(); ++index) {
        const ZipIssue& value = report.issues[index];
        output << indent2 << "{\"code\":\"" << json_escape(value.code)
               << "\",\"message\":\"" << json_escape(value.message)
               << "\",\"entry\":\"" << json_escape(value.entry)
               << "\",\"fatal\":" << (value.fatal ? "true" : "false") << '}';
        if (index + 1 != report.issues.size()) output << ',';
        if (pretty) output << newline;
    }
    output << indent1 << ']' << newline << '}' << newline;
    return output.str();
}

} // namespace bzip4
