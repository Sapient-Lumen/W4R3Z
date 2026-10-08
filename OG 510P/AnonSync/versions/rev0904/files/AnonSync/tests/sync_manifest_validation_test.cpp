#include "sync_manifest_validation.hpp"

#include <cstdint>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using anonsync::NormalizedSyncPath;
using anonsync::SyncChunkRange;
using anonsync::SyncFolderManifest;
using anonsync::SyncManifestEntry;
using anonsync::SyncManifestEntryKind;
using anonsync::SyncManifestResourceLimits;
using anonsync::SyncManifestResourceUsage;
using anonsync::SyncValidationResult;
using anonsync::SyncVersionLineageEntry;

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Fn>
void require_reason(
    Fn&& fn,
    const std::string& expected,
    const std::string& message,
    int& checks) {
    const SyncValidationResult result = fn();
    require(!result.ok && result.reason == expected, message, checks);
}


[[nodiscard]] bool reference_valid_utf8(const std::string& input) {
    std::size_t index = 0;
    while (index < input.size()) {
        const unsigned char first =
            static_cast<unsigned char>(input[index]);
        if (first <= 0x7fU) {
            ++index;
            continue;
        }
        std::size_t need = 0;
        std::uint32_t codepoint = 0;
        if ((first & 0xe0U) == 0xc0U) {
            if (first < 0xc2U) return false;
            need = 1;
            codepoint = first & 0x1fU;
        } else if ((first & 0xf0U) == 0xe0U) {
            need = 2;
            codepoint = first & 0x0fU;
        } else if ((first & 0xf8U) == 0xf0U) {
            need = 3;
            codepoint = first & 0x07U;
        } else {
            return false;
        }
        if (index + need >= input.size()) return false;
        for (std::size_t offset = 1; offset <= need; ++offset) {
            const unsigned char continuation =
                static_cast<unsigned char>(input[index + offset]);
            if ((continuation & 0xc0U) != 0x80U) return false;
            codepoint = (codepoint << 6U) | (continuation & 0x3fU);
        }
        if (need == 1U && codepoint < 0x80U) return false;
        if (need == 2U && codepoint < 0x800U) return false;
        if (need == 3U && codepoint < 0x10000U) return false;
        if (codepoint > 0x10ffffU) return false;
        if (codepoint >= 0xd800U && codepoint <= 0xdfffU) return false;
        index += need + 1U;
    }
    return true;
}

[[nodiscard]] char reference_ascii_upper(char value) {
    return value >= 'a' && value <= 'z'
        ? static_cast<char>(value - ('a' - 'A'))
        : value;
}

[[nodiscard]] bool reference_reserved_device_digit(
    const std::string& suffix) {
    return (suffix.size() == 1U &&
            suffix.front() >= '1' && suffix.front() <= '9') ||
           suffix == "\xC2\xB9" ||
           suffix == "\xC2\xB2" ||
           suffix == "\xC2\xB3";
}

[[nodiscard]] bool reference_reserved_device_name(
    const std::string& component) {
    std::string stem;
    for (const char value : component) {
        if (value == '.') break;
        stem.push_back(reference_ascii_upper(value));
    }
    if (stem == "CON" || stem == "PRN" ||
        stem == "AUX" || stem == "NUL") {
        return true;
    }
    return stem.size() >= 4U &&
        (stem.rfind("COM", 0) == 0 || stem.rfind("LPT", 0) == 0) &&
        reference_reserved_device_digit(stem.substr(3));
}

[[nodiscard]] bool reference_path_accepts(const std::string& raw_path) {
    if (raw_path.empty() || raw_path.size() > 4096U ||
        !reference_valid_utf8(raw_path) || raw_path.front() == '/' ||
        raw_path.back() == '/' ||
        (raw_path.size() >= 2U && raw_path[1] == ':')) {
        return false;
    }
    std::vector<std::string> components;
    std::string current;
    for (const char raw : raw_path) {
        const unsigned char value = static_cast<unsigned char>(raw);
        if (value <= 0x1fU || value == 0x7fU ||
            raw == '\\' || raw == ':' || raw == '*' || raw == '?' ||
            raw == '"' || raw == '<' || raw == '>' || raw == '|') {
            return false;
        }
        if (raw == '/') {
            components.push_back(current);
            current.clear();
        } else {
            current.push_back(raw);
        }
    }
    components.push_back(current);
    for (const std::string& component : components) {
        if (component.empty() || component == "." || component == ".." ||
            component.back() == ' ' || component.back() == '.' ||
            reference_reserved_device_name(component)) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] std::string bytes_hex(const std::string& value) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (const unsigned char byte : value) {
        out << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return out.str();
}

SyncManifestEntry file_entry(
    const std::string& path,
    std::uint64_t counter = 1) {
    SyncManifestEntry entry;
    entry.folder_id = "folder-alpha";
    entry.device_id = "device-alpha";
    entry.path.value = path;
    entry.kind = SyncManifestEntryKind::File;
    entry.size_bytes = 3;
    entry.content_sha256 = std::string(64, 'a');
    entry.chunks = {{0, 3, std::string(64, 'b')}};
    entry.lineage = {{"device-alpha", counter}};
    return entry;
}

SyncManifestEntry tombstone_entry(
    const std::string& path,
    std::uint64_t counter = 2) {
    SyncManifestEntry entry;
    entry.folder_id = "folder-alpha";
    entry.device_id = "device-alpha";
    entry.path.value = path;
    entry.kind = SyncManifestEntryKind::Tombstone;
    entry.lineage = {{"device-alpha", counter}};
    return entry;
}

SyncFolderManifest two_entry_manifest() {
    SyncFolderManifest manifest;
    manifest.folder_id = "folder-alpha";
    manifest.device_id = "device-alpha";
    manifest.manifest_counter = 7;
    manifest.entries = {
        file_entry("docs/file.txt"),
        tombstone_entry("docs/gone.txt"),
    };
    return manifest;
}

}  // namespace

int main() {
    using anonsync::normalize_sync_relative_path;
    using anonsync::sync_id_is_valid;
    using anonsync::sync_manifest_default_resource_limits;
    using anonsync::validate_sync_folder_manifest;
    using anonsync::validate_sync_folder_manifest_with_limits;
    using anonsync::validate_sync_manifest_entry;
    using anonsync::validate_sync_manifest_entry_with_limits;
    using anonsync::validate_sync_relative_path_component_byte_limit;

    int checks = 0;
    try {
        require(sync_id_is_valid("device-alpha_7.test") &&
                    !sync_id_is_valid("") &&
                    !sync_id_is_valid("Device-alpha") &&
                    !sync_id_is_valid("device/alpha") &&
                    !sync_id_is_valid(std::string(129, 'a')),
                "portable sync identifiers require exact bounded ASCII syntax",
                checks);

        NormalizedSyncPath path;
        require(normalize_sync_relative_path("docs/report.txt", path).ok &&
                    path.value == "docs/report.txt",
                "canonical path normalization preserves exact bytes",
                checks);
        const std::string unicode_path = "résumé/資料.txt";
        require(normalize_sync_relative_path(
                    unicode_path, path).ok &&
                    path.value == unicode_path,
                "canonical path normalization accepts valid UTF-8 without locale conversion",
                checks);
        require(
            validate_sync_relative_path_component_byte_limit(
                "ab/cd", 2U).ok,
            "local component-byte preflight accepts the exact inclusive boundary",
            checks);
        require_reason(
            [&] {
                return validate_sync_relative_path_component_byte_limit(
                    "ab/cde", 2U);
            },
            "sync path component exceeds local filename byte limit",
            "local component-byte preflight rejects one over the boundary",
            checks);
        const std::string two_multibyte_codepoints =
            std::string("\xC3\xA9") + "\xC3\xA9";
        require(
            validate_sync_relative_path_component_byte_limit(
                two_multibyte_codepoints, 4U).ok &&
                !validate_sync_relative_path_component_byte_limit(
                    two_multibyte_codepoints, 3U).ok,
            "local component policy counts encoded bytes rather than displayed characters",
            checks);
        require_reason(
            [&] {
                return validate_sync_relative_path_component_byte_limit(
                    "component", 0U);
            },
            "sync path component byte limit must be positive",
            "a zero local filename ceiling cannot silently authorize a path",
            checks);
        require_reason(
            [&] {
                return validate_sync_relative_path_component_byte_limit(
                    "folder/../escape.txt", 255U);
            },
            "sync path contains a dot segment",
            "local policy never launders an invalid canonical path into a limit result",
            checks);

        std::uint64_t random_state = 0x8f2c91d75b3a6401ULL;
        auto next_random = [&]() {
            random_state ^= random_state << 13U;
            random_state ^= random_state >> 7U;
            random_state ^= random_state << 17U;
            return random_state;
        };
        for (std::size_t sample = 0; sample < 50000U; ++sample) {
            const std::size_t length =
                static_cast<std::size_t>(next_random() % 32U);
            std::string generated;
            generated.reserve(length);
            for (std::size_t index = 0; index < length; ++index) {
                generated.push_back(static_cast<char>(next_random() & 0xffU));
            }
            NormalizedSyncPath generated_out;
            const bool actual =
                normalize_sync_relative_path(generated, generated_out).ok;
            const bool expected = reference_path_accepts(generated);
            if (actual != expected) {
                throw std::runtime_error(
                    "single-pass path compatibility mismatch sample=" +
                    std::to_string(sample) + " hex=" + bytes_hex(generated));
            }
        }
        require(true,
                "50,000 generated byte strings match an independent portable-path oracle",
                checks);

        path.value = "docs/in-place.txt";
        const SyncValidationResult alias_ok =
            normalize_sync_relative_path(path.value, path);
        require(alias_ok.ok && path.value == "docs/in-place.txt",
                "normalization freezes aliased input before output mutation",
                checks);
        path.value = "../in-place.txt";
        const SyncValidationResult alias_bad =
            normalize_sync_relative_path(path.value, path);
        require(!alias_bad.ok && path.value.empty(),
                "invalid aliased input is rejected and output is cleared",
                checks);

        const std::vector<std::string> invalid_paths{
            "/absolute.txt",
            "folder/../escape.txt",
            "folder//empty.txt",
            "folder/name:.txt",
            "folder/trailing. ",
            "CoN.txt",
            "folder/lPt9.any",
            std::string("folder/COM") + "\xC2\xB9",
            std::string("folder/com") + "\xC2\xB2.txt",
            std::string("LPT") + "\xC2\xB3.tar.gz",
            std::string("folder/") + std::string("\xc0\xaf", 2),
        };
        for (const std::string& invalid : invalid_paths) {
            NormalizedSyncPath rejected;
            require(!normalize_sync_relative_path(invalid, rejected).ok &&
                        rejected.value.empty(),
                    "invalid portable path is rejected: " + invalid,
                    checks);
        }

        const SyncManifestEntry file = file_entry("docs/file.txt");
        const SyncManifestEntry tombstone =
            tombstone_entry("docs/gone.txt");
        require(validate_sync_manifest_entry(file).ok &&
                    validate_sync_manifest_entry(tombstone).ok,
                "default entry validator accepts bounded file and tombstone values",
                checks);

        SyncManifestResourceUsage entry_usage;
        require(validate_sync_manifest_entry_with_limits(
                    file,
                    sync_manifest_default_resource_limits(),
                    &entry_usage).ok &&
                    entry_usage.entries == 1U &&
                    entry_usage.chunks == 1U &&
                    entry_usage.lineage_entries == 1U &&
                    entry_usage.path_bytes == 13U &&
                    entry_usage.metadata_bytes == 210U,
                "entry resource accounting is exact and deterministic",
                checks);

        SyncFolderManifest manifest = two_entry_manifest();
        SyncManifestResourceUsage usage;
        require(validate_sync_folder_manifest_with_limits(
                    manifest,
                    sync_manifest_default_resource_limits(),
                    &usage).ok &&
                    usage.entries == 2U &&
                    usage.chunks == 1U &&
                    usage.lineage_entries == 2U &&
                    usage.path_bytes == 26U &&
                    usage.metadata_bytes == 308U,
                "folder resource accounting covers every nested semantic byte",
                checks);
        require(validate_sync_folder_manifest(manifest).ok,
                "public folder validator delegates to the bounded owner",
                checks);
        SyncManifestResourceLimits exact_limits{};
        exact_limits.max_entries = usage.entries;
        exact_limits.max_chunks_per_entry = usage.chunks;
        exact_limits.max_lineage_entries_per_entry = usage.lineage_entries;
        exact_limits.max_total_chunks = usage.chunks;
        exact_limits.max_total_lineage_entries = usage.lineage_entries;
        exact_limits.max_total_path_bytes = usage.path_bytes;
        exact_limits.max_total_metadata_bytes = usage.metadata_bytes;
        require(validate_sync_folder_manifest_with_limits(
                    manifest, exact_limits).ok,
                "resource ceilings are inclusive at the exact measured boundary",
                checks);

        SyncManifestEntry many_chunks = file;
        many_chunks.size_bytes = 20000U;
        many_chunks.chunks.clear();
        many_chunks.chunks.reserve(20000U);
        for (std::uint64_t offset = 0; offset < 20000U; ++offset) {
            many_chunks.chunks.push_back(
                SyncChunkRange{offset, 1U, std::string(64, 'b')});
        }
        SyncManifestResourceUsage many_usage;
        require(validate_sync_manifest_entry_with_limits(
                    many_chunks,
                    sync_manifest_default_resource_limits(),
                    &many_usage).ok &&
                    many_usage.chunks == 20000U,
                "default validation accepts the established 20,000-chunk streaming corpus",
                checks);


        SyncManifestResourceLimits limits =
            sync_manifest_default_resource_limits();
        limits.max_entries = 1;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    manifest, limits);
            },
            "manifest entry count exceeds resource limit",
            "entry cardinality budget fails closed",
            checks);

        limits = sync_manifest_default_resource_limits();
        limits.max_total_chunks = 0;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    manifest, limits);
            },
            "manifest chunk count exceeds resource limit",
            "aggregate chunk budget fails closed",
            checks);

        limits = sync_manifest_default_resource_limits();
        limits.max_chunks_per_entry = 0;
        require_reason(
            [&] {
                return validate_sync_manifest_entry_with_limits(file, limits);
            },
            "manifest entry chunk count exceeds per-entry resource limit",
            "per-entry chunk budget fails closed",
            checks);

        SyncManifestEntry two_lineages = file;
        two_lineages.lineage.push_back({"device-bravo", 1});
        limits = sync_manifest_default_resource_limits();
        limits.max_lineage_entries_per_entry = 1;
        require_reason(
            [&] {
                return validate_sync_manifest_entry_with_limits(
                    two_lineages, limits);
            },
            "manifest entry lineage count exceeds per-entry resource limit",
            "per-entry lineage budget fails closed",
            checks);

        limits = sync_manifest_default_resource_limits();
        limits.max_total_lineage_entries = 1;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    manifest, limits);
            },
            "manifest lineage count exceeds resource limit",
            "aggregate lineage budget fails closed",
            checks);

        limits = sync_manifest_default_resource_limits();
        limits.max_total_path_bytes = 25;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    manifest, limits);
            },
            "manifest path bytes exceed resource limit",
            "aggregate path-byte budget fails closed",
            checks);

        limits = sync_manifest_default_resource_limits();
        limits.max_total_metadata_bytes = 307;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    manifest, limits);
            },
            "manifest metadata bytes exceed resource limit",
            "aggregate metadata-byte budget fails closed",
            checks);

        SyncFolderManifest preflight_priority = manifest;
        preflight_priority.entries.front().path.value = "../invalid.txt";
        limits = sync_manifest_default_resource_limits();
        limits.max_total_chunks = 0;
        require_reason(
            [&] {
                return validate_sync_folder_manifest_with_limits(
                    preflight_priority, limits);
            },
            "manifest chunk count exceeds resource limit",
            "shape preflight rejects nested cardinality before semantic traversal",
            checks);

        SyncManifestResourceUsage untouched{
            9U, 9U, 9U, 9U, 9U};
        limits = sync_manifest_default_resource_limits();
        limits.max_entries = 1;
        const SyncValidationResult failed_with_output =
            validate_sync_folder_manifest_with_limits(
                manifest, limits, &untouched);
        require(!failed_with_output.ok &&
                    untouched.entries == 9U &&
                    untouched.chunks == 9U &&
                    untouched.lineage_entries == 9U &&
                    untouched.path_bytes == 9U &&
                    untouched.metadata_bytes == 9U,
                "failed validation never publishes partial resource evidence",
                checks);

        SyncManifestEntry unknown = file;
        unknown.kind = static_cast<SyncManifestEntryKind>(77);
        require_reason(
            [&] { return validate_sync_manifest_entry(unknown); },
            "manifest entry has unknown kind",
            "unknown manifest entry kinds fail closed",
            checks);

        SyncFolderManifest duplicate = manifest;
        duplicate.entries[1].path = duplicate.entries[0].path;
        require_reason(
            [&] { return validate_sync_folder_manifest(duplicate); },
            "manifest entries must be sorted by unique canonical path",
            "folder validation retains unique sorted path semantics",
            checks);

        std::cout << "sync manifest validation checks passed: "
                  << checks << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync manifest validation test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
