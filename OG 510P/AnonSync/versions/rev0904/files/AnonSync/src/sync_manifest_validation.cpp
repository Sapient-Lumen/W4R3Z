#include "sync_manifest_validation.hpp"

#include "sha256_digest.hpp"

#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] SyncValidationResult valid_result() {
    return {true, {}};
}

[[nodiscard]] SyncValidationResult invalid_result(std::string reason) {
    return {false, std::move(reason)};
}

[[nodiscard]] bool ascii_lower_alnum(char value) noexcept {
    return (value >= 'a' && value <= 'z') ||
           (value >= '0' && value <= '9');
}

[[nodiscard]] char ascii_upper(char value) noexcept {
    if (value >= 'a' && value <= 'z') {
        return static_cast<char>(value - ('a' - 'A'));
    }
    return value;
}

[[nodiscard]] bool ascii_case_equal(
    std::string_view left,
    std::string_view right) noexcept {
    if (left.size() != right.size()) return false;
    for (std::size_t index = 0; index < left.size(); ++index) {
        if (ascii_upper(left[index]) != ascii_upper(right[index])) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool reserved_windows_device_digit(
    std::string_view suffix) noexcept {
    if (suffix.size() == 1U && suffix.front() >= '1' && suffix.front() <= '9') {
        return true;
    }
    // Win32 also recognizes the ISO-8859-1 superscript digits 1, 2, and 3
    // in COM#/LPT# device names. The surrounding path has already passed
    // strict UTF-8 validation, so match their canonical UTF-8 byte spellings.
    return suffix == "\xC2\xB9" ||
           suffix == "\xC2\xB2" ||
           suffix == "\xC2\xB3";
}

[[nodiscard]] bool reserved_windows_device_name(
    std::string_view component) noexcept {
    const std::size_t dot = component.find('.');
    const std::string_view stem = component.substr(0, dot);
    if (ascii_case_equal(stem, "con") ||
        ascii_case_equal(stem, "prn") ||
        ascii_case_equal(stem, "aux") ||
        ascii_case_equal(stem, "nul")) {
        return true;
    }
    return stem.size() >= 4U &&
           (ascii_case_equal(stem.substr(0, 3), "com") ||
            ascii_case_equal(stem.substr(0, 3), "lpt")) &&
           reserved_windows_device_digit(stem.substr(3));
}

[[nodiscard]] bool disallowed_path_byte(unsigned char value) noexcept {
    if (value <= 0x1fU || value == 0x7fU) return true;
    switch (value) {
        case '\\':
        case ':':
        case '*':
        case '?':
        case '"':
        case '<':
        case '>':
        case '|':
            return true;
        default:
            return false;
    }
}

[[nodiscard]] bool valid_utf8(std::string_view input) noexcept {
    std::size_t index = 0;
    while (index < input.size()) {
        const unsigned char first =
            static_cast<unsigned char>(input[index]);
        if (first <= 0x7fU) {
            ++index;
            continue;
        }

        std::size_t continuation_count = 0;
        std::uint32_t codepoint = 0;
        if ((first & 0xe0U) == 0xc0U) {
            if (first < 0xc2U) return false;
            continuation_count = 1;
            codepoint = first & 0x1fU;
        } else if ((first & 0xf0U) == 0xe0U) {
            continuation_count = 2;
            codepoint = first & 0x0fU;
        } else if ((first & 0xf8U) == 0xf0U) {
            continuation_count = 3;
            codepoint = first & 0x07U;
        } else {
            return false;
        }
        if (continuation_count >= input.size() - index) return false;
        for (std::size_t offset = 1;
             offset <= continuation_count;
             ++offset) {
            const unsigned char continuation =
                static_cast<unsigned char>(input[index + offset]);
            if ((continuation & 0xc0U) != 0x80U) return false;
            codepoint = (codepoint << 6U) | (continuation & 0x3fU);
        }
        if (continuation_count == 1U && codepoint < 0x80U) return false;
        if (continuation_count == 2U && codepoint < 0x800U) return false;
        if (continuation_count == 3U && codepoint < 0x10000U) return false;
        if (codepoint > 0x10ffffU) return false;
        if (codepoint >= 0xd800U && codepoint <= 0xdfffU) return false;
        index += continuation_count + 1U;
    }
    return true;
}

[[nodiscard]] SyncValidationResult validate_relative_path_value(
    std::string_view raw_path) {
    if (raw_path.empty()) return invalid_result("sync path is empty");
    if (raw_path.size() > kSyncManifestRelativePathMaxBytes) {
        return invalid_result("sync path exceeds 4096-byte limit");
    }
    if (!valid_utf8(raw_path)) {
        return invalid_result("sync path is not valid UTF-8");
    }
    if (raw_path.front() == '/') {
        return invalid_result("sync path must be relative");
    }
    if (raw_path.back() == '/') {
        return invalid_result(
            "sync path must name an entry, not a directory separator");
    }
    if (raw_path.size() >= 2U && raw_path[1] == ':') {
        return invalid_result("sync path rejects drive-qualified names");
    }

    std::size_t component_begin = 0;
    for (std::size_t index = 0; index <= raw_path.size(); ++index) {
        if (index < raw_path.size()) {
            const unsigned char byte =
                static_cast<unsigned char>(raw_path[index]);
            if (disallowed_path_byte(byte)) {
                return invalid_result(
                    "sync path contains a disallowed portable filename byte");
            }
            if (raw_path[index] != '/') continue;
        }

        const std::string_view component = raw_path.substr(
            component_begin, index - component_begin);
        if (component.empty()) {
            return invalid_result("sync path contains an empty component");
        }
        if (component == "." || component == "..") {
            return invalid_result("sync path contains a dot segment");
        }
        if (component.back() == ' ' || component.back() == '.') {
            return invalid_result(
                "sync path component has nonportable trailing space or dot");
        }
        if (reserved_windows_device_name(component)) {
            return invalid_result(
                "sync path component is a reserved portable device name");
        }
        component_begin = index + 1U;
    }
    return valid_result();
}

[[nodiscard]] bool size_to_u64(
    std::size_t value,
    std::uint64_t& out) noexcept {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > static_cast<std::size_t>(
                        std::numeric_limits<std::uint64_t>::max())) {
            return false;
        }
    }
    out = static_cast<std::uint64_t>(value);
    return true;
}

[[nodiscard]] SyncValidationResult add_bounded(
    std::uint64_t& total,
    std::uint64_t amount,
    std::uint64_t limit,
    std::string_view overflow_reason,
    std::string_view limit_reason) {
    if (amount > std::numeric_limits<std::uint64_t>::max() - total) {
        return invalid_result(std::string(overflow_reason));
    }
    const std::uint64_t proposed = total + amount;
    if (proposed > limit) {
        return invalid_result(std::string(limit_reason));
    }
    total = proposed;
    return valid_result();
}

[[nodiscard]] SyncValidationResult add_size_bounded(
    std::uint64_t& total,
    std::size_t amount,
    std::uint64_t limit,
    std::string_view overflow_reason,
    std::string_view limit_reason) {
    std::uint64_t converted = 0;
    if (!size_to_u64(amount, converted)) {
        return invalid_result(std::string(overflow_reason));
    }
    return add_bounded(
        total, converted, limit, overflow_reason, limit_reason);
}

[[nodiscard]] SyncValidationResult preflight_entry_shape(
    const SyncManifestEntry& entry,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage& usage) {
    SyncManifestResourceBudget budget(limits);
    SyncValidationResult result = budget.admit_entry_count(1U);
    if (!result.ok) return result;

    std::uint64_t chunk_count = 0;
    if (!size_to_u64(entry.chunks.size(), chunk_count)) {
        return invalid_result("manifest chunk count exceeds uint64 range");
    }
    std::uint64_t lineage_count = 0;
    if (!size_to_u64(entry.lineage.size(), lineage_count)) {
        return invalid_result("manifest lineage count exceeds uint64 range");
    }
    result = budget.admit_entry_shape(
        chunk_count, lineage_count, entry.path.value.size());
    if (!result.ok) return result;

    for (const std::size_t bytes : {
             entry.folder_id.size(),
             entry.device_id.size(),
             entry.path.value.size(),
             entry.content_sha256.size(),
             entry.conflict_set_id.size(),
             static_cast<std::size_t>(9U)}) {
        result = budget.admit_metadata_bytes(bytes);
        if (!result.ok) return result;
    }
    for (const SyncChunkRange& chunk : entry.chunks) {
        result = budget.admit_metadata_bytes(chunk.sha256.size());
        if (!result.ok) return result;
        result = budget.admit_metadata_bytes(16U);
        if (!result.ok) return result;
    }
    for (const SyncVersionLineageEntry& lineage : entry.lineage) {
        result = budget.admit_metadata_bytes(lineage.device_id.size());
        if (!result.ok) return result;
        result = budget.admit_metadata_bytes(8U);
        if (!result.ok) return result;
    }
    usage = budget.usage();
    return valid_result();
}

[[nodiscard]] SyncValidationResult preflight_manifest_shape(
    const SyncFolderManifest& manifest,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage& usage) {
    SyncManifestResourceBudget budget(limits);
    std::uint64_t entry_count = 0;
    if (!size_to_u64(manifest.entries.size(), entry_count)) {
        return invalid_result("manifest entry count exceeds uint64 range");
    }
    SyncValidationResult result = budget.admit_entry_count(entry_count);
    if (!result.ok) return result;

    // Phase one observes only vector cardinality and path string lengths. A
    // single oversized nested vector is rejected before any nested element is
    // inspected, hashed, compared, or copied.
    for (const SyncManifestEntry& entry : manifest.entries) {
        std::uint64_t chunk_count = 0;
        if (!size_to_u64(entry.chunks.size(), chunk_count)) {
            return invalid_result("manifest chunk count exceeds uint64 range");
        }
        std::uint64_t lineage_count = 0;
        if (!size_to_u64(entry.lineage.size(), lineage_count)) {
            return invalid_result("manifest lineage count exceeds uint64 range");
        }
        result = budget.admit_entry_shape(
            chunk_count, lineage_count, entry.path.value.size());
        if (!result.ok) return result;
    }

    // Phase two may inspect nested elements only after phase one has bounded
    // their aggregate count. The byte budget includes the typed value's owned
    // strings and stable semantic scalar widths, not allocator overhead.
    result = budget.admit_metadata_bytes(manifest.folder_id.size());
    if (!result.ok) return result;
    result = budget.admit_metadata_bytes(manifest.device_id.size());
    if (!result.ok) return result;
    result = budget.admit_metadata_bytes(8U);
    if (!result.ok) return result;

    for (const SyncManifestEntry& entry : manifest.entries) {
        for (const std::size_t bytes : {
                 entry.folder_id.size(),
                 entry.device_id.size(),
                 entry.path.value.size(),
                 entry.content_sha256.size(),
                 entry.conflict_set_id.size(),
                 static_cast<std::size_t>(9U)}) {
            result = budget.admit_metadata_bytes(bytes);
            if (!result.ok) return result;
        }
        for (const SyncChunkRange& chunk : entry.chunks) {
            result = budget.admit_metadata_bytes(chunk.sha256.size());
            if (!result.ok) return result;
            result = budget.admit_metadata_bytes(16U);
            if (!result.ok) return result;
        }
        for (const SyncVersionLineageEntry& lineage : entry.lineage) {
            result = budget.admit_metadata_bytes(lineage.device_id.size());
            if (!result.ok) return result;
            result = budget.admit_metadata_bytes(8U);
            if (!result.ok) return result;
        }
    }
    usage = budget.usage();
    return valid_result();
}

[[nodiscard]] SyncValidationResult validate_entry_semantics(
    const SyncManifestEntry& entry) {
    if (!sync_id_is_valid(entry.folder_id)) {
        return invalid_result(
            "folder_id must be lowercase portable sync id");
    }
    if (!sync_id_is_valid(entry.device_id)) {
        return invalid_result(
            "device_id must be lowercase portable sync id");
    }

    const SyncValidationResult path_result =
        validate_relative_path_value(entry.path.value);
    if (!path_result.ok) return path_result;

    if (entry.lineage.empty()) {
        return invalid_result("manifest entry requires version lineage");
    }
    std::string_view previous_device;
    for (const SyncVersionLineageEntry& lineage : entry.lineage) {
        if (!sync_id_is_valid(lineage.device_id)) {
            return invalid_result(
                "lineage device_id must be lowercase portable sync id");
        }
        if (lineage.counter == 0U) {
            return invalid_result("lineage counter must be positive");
        }
        if (!previous_device.empty() &&
            lineage.device_id <= previous_device) {
            return invalid_result(
                "lineage entries must be unique and sorted by device_id");
        }
        previous_device = lineage.device_id;
    }

    if (!entry.conflict_set_id.empty() &&
        !sync_id_is_valid(entry.conflict_set_id)) {
        return invalid_result(
            "conflict_set_id must be empty or a lowercase portable sync id");
    }

    if (entry.kind == SyncManifestEntryKind::Tombstone) {
        if (entry.size_bytes != 0U) {
            return invalid_result("tombstone size must be zero");
        }
        if (!entry.content_sha256.empty()) {
            return invalid_result("tombstone must not carry content hash");
        }
        if (!entry.chunks.empty()) {
            return invalid_result("tombstone must not carry chunks");
        }
        return valid_result();
    }

    if (entry.kind != SyncManifestEntryKind::File) {
        return invalid_result("manifest entry has unknown kind");
    }
    if (!is_lowercase_sha256_hex(entry.content_sha256)) {
        return invalid_result(
            "file manifest entry requires lowercase sha256 content hash");
    }
    if (entry.size_bytes == 0U && !entry.chunks.empty()) {
        return invalid_result("zero-byte file must not carry chunks");
    }
    if (entry.size_bytes > 0U && entry.chunks.empty()) {
        return invalid_result("nonempty file requires chunk ranges");
    }

    std::uint64_t expected_offset = 0;
    for (const SyncChunkRange& chunk : entry.chunks) {
        if (chunk.offset != expected_offset) {
            return invalid_result(
                "chunk ranges must be contiguous from offset zero");
        }
        if (chunk.length == 0U) {
            return invalid_result("chunk range length must be positive");
        }
        if (!is_lowercase_sha256_hex(chunk.sha256)) {
            return invalid_result(
                "chunk range requires lowercase sha256 hash");
        }
        if (chunk.length >
            std::numeric_limits<std::uint64_t>::max() - expected_offset) {
            return invalid_result("chunk ranges overflow uint64");
        }
        expected_offset += chunk.length;
    }
    if (expected_offset != entry.size_bytes) {
        return invalid_result(
            "chunk ranges must cover exactly size_bytes");
    }
    return valid_result();
}

}  // namespace

SyncManifestResourceBudget::SyncManifestResourceBudget(
    SyncManifestResourceLimits limits) noexcept
    : limits_(limits) {}

SyncValidationResult SyncManifestResourceBudget::admit_entry_count(
    std::uint64_t count) {
    if (entry_count_admitted_) {
        return invalid_result(
            "manifest resource budget entry count was already admitted");
    }
    entry_count_admitted_ = true;
    if (count > limits_.max_entries) {
        return invalid_result("manifest entry count exceeds resource limit");
    }
    usage_.entries = count;
    return valid_result();
}

SyncValidationResult SyncManifestResourceBudget::admit_entry_shape(
    std::uint64_t chunk_count,
    std::uint64_t lineage_count,
    std::size_t path_bytes) {
    if (!entry_count_admitted_) {
        return invalid_result(
            "manifest resource budget requires entry count first");
    }
    if (chunk_count > limits_.max_chunks_per_entry) {
        return invalid_result(
            "manifest entry chunk count exceeds per-entry resource limit");
    }
    SyncValidationResult result = add_bounded(
        usage_.chunks,
        chunk_count,
        limits_.max_total_chunks,
        "manifest chunk count exceeds uint64 range",
        "manifest chunk count exceeds resource limit");
    if (!result.ok) return result;

    if (lineage_count > limits_.max_lineage_entries_per_entry) {
        return invalid_result(
            "manifest entry lineage count exceeds per-entry resource limit");
    }
    result = add_bounded(
        usage_.lineage_entries,
        lineage_count,
        limits_.max_total_lineage_entries,
        "manifest lineage count exceeds uint64 range",
        "manifest lineage count exceeds resource limit");
    if (!result.ok) return result;

    return add_size_bounded(
        usage_.path_bytes,
        path_bytes,
        limits_.max_total_path_bytes,
        "manifest path bytes exceed uint64 range",
        "manifest path bytes exceed resource limit");
}

SyncValidationResult SyncManifestResourceBudget::admit_metadata_bytes(
    std::size_t bytes) {
    return add_size_bounded(
        usage_.metadata_bytes,
        bytes,
        limits_.max_total_metadata_bytes,
        "manifest metadata bytes exceed uint64 range",
        "manifest metadata bytes exceed resource limit");
}

bool sync_id_is_valid(std::string_view value) noexcept {
    if (value.empty() || value.size() > kSyncManifestIdMaxBytes) return false;
    if (!ascii_lower_alnum(value.front()) ||
        !ascii_lower_alnum(value.back())) {
        return false;
    }
    for (const char byte : value) {
        if (ascii_lower_alnum(byte)) continue;
        if (byte == '.' || byte == '_' || byte == '-') continue;
        return false;
    }
    return true;
}

SyncValidationResult validate_sync_relative_path(
    std::string_view raw_path) {
    return validate_relative_path_value(raw_path);
}

SyncValidationResult validate_sync_relative_path_component_byte_limit(
    std::string_view raw_path,
    std::uint64_t maximum_component_bytes) {
    const SyncValidationResult canonical =
        validate_relative_path_value(raw_path);
    if (!canonical.ok) return canonical;
    if (maximum_component_bytes == 0U) {
        return invalid_result(
            "sync path component byte limit must be positive");
    }

    std::size_t component_begin = 0U;
    for (std::size_t index = 0U; index <= raw_path.size(); ++index) {
        if (index != raw_path.size() && raw_path[index] != '/') continue;
        const std::size_t component_bytes = index - component_begin;
        std::uint64_t converted = 0U;
        if (!size_to_u64(component_bytes, converted) ||
            converted > maximum_component_bytes) {
            return invalid_result(
                "sync path component exceeds local filename byte limit");
        }
        component_begin = index + 1U;
    }
    return valid_result();
}

SyncValidationResult normalize_sync_relative_path(
    const std::string& raw_path,
    NormalizedSyncPath& out) {
    // Validate before touching the output. The public API permits raw_path to
    // alias out.value; clearing output first would erase the observation being
    // validated and turn a valid in-place normalization into a false failure.
    const SyncValidationResult result = validate_relative_path_value(raw_path);
    if (!result.ok) {
        out.value.clear();
        return result;
    }
    out.value = raw_path;
    return valid_result();
}

SyncValidationResult validate_sync_manifest_entry_with_limits(
    const SyncManifestEntry& entry,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage* usage_out) {
    SyncManifestResourceUsage usage;
    SyncValidationResult result = preflight_entry_shape(entry, limits, usage);
    if (!result.ok) return result;
    result = validate_entry_semantics(entry);
    if (!result.ok) return result;
    if (usage_out != nullptr) *usage_out = usage;
    return valid_result();
}

SyncValidationResult validate_sync_folder_manifest_with_limits(
    const SyncFolderManifest& manifest,
    const SyncManifestResourceLimits& limits,
    SyncManifestResourceUsage* usage_out) {
    if (!sync_id_is_valid(manifest.folder_id)) {
        return invalid_result(
            "manifest folder_id must be lowercase portable sync id");
    }
    if (!sync_id_is_valid(manifest.device_id)) {
        return invalid_result(
            "manifest device_id must be lowercase portable sync id");
    }
    if (manifest.manifest_counter == 0U) {
        return invalid_result("manifest_counter must be positive");
    }

    SyncManifestResourceUsage usage;
    SyncValidationResult result =
        preflight_manifest_shape(manifest, limits, usage);
    if (!result.ok) return result;

    std::string_view previous_path;
    for (const SyncManifestEntry& entry : manifest.entries) {
        if (entry.folder_id != manifest.folder_id) {
            return invalid_result(
                "manifest entry folder_id does not match folder manifest");
        }
        if (entry.device_id != manifest.device_id) {
            return invalid_result(
                "manifest entry device_id does not match folder manifest");
        }
        result = validate_entry_semantics(entry);
        if (!result.ok) {
            return invalid_result(
                "manifest entry invalid: " + result.reason);
        }
        if (!previous_path.empty() && entry.path.value <= previous_path) {
            return invalid_result(
                "manifest entries must be sorted by unique canonical path");
        }
        previous_path = entry.path.value;
    }
    if (usage_out != nullptr) *usage_out = usage;
    return valid_result();
}

SyncValidationResult validate_sync_manifest_entry(
    const SyncManifestEntry& entry) {
    return validate_sync_manifest_entry_with_limits(
        entry, sync_manifest_default_resource_limits());
}

SyncValidationResult validate_sync_folder_manifest(
    const SyncFolderManifest& manifest) {
    return validate_sync_folder_manifest_with_limits(
        manifest, sync_manifest_default_resource_limits());
}

}  // namespace anonsync
