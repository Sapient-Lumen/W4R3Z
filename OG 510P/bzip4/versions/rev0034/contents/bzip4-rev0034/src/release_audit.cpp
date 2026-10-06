#include "bzip4/release_audit.hpp"

#include "bzip4/sha256.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <fstream>
#include <iomanip>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string_view>
#include <system_error>
#include <utility>

namespace bzip4 {
namespace {

constexpr auto required_paths = std::to_array<std::string_view>({
    "CMakeLists.txt",
    "README.md",
    "RELEASE_SUMMARY.md",
    "LICENSE",
    "bin/README.md",
    "bin/linux-x86_64/bzip4_activation_probe",
    "bin/linux-x86_64/bzip4_codec",
    "bin/linux-x86_64/bzip4_cube_preflight",
    "bin/linux-x86_64/bzip4_release_audit",
    "include/bzip4/activation.hpp",
    "include/bzip4/atomic_file.hpp",
    "include/bzip4/codec.hpp",
    "include/bzip4/libbz3.h",
    "include/bzip4/pinned_file.hpp",
    "include/bzip4/parallel_codec.hpp",
    "include/bzip4/profile.hpp",
    "include/bzip4/release_audit.hpp",
    "include/bzip4/resource_plan.hpp",
    "include/bzip4/sha256.hpp",
    "include/bzip4/zip_preflight.hpp",
    "src/activation.cpp",
    "src/atomic_file.cpp",
    "src/codec.cpp",
    "src/codec_core.hpp",
    "src/frame_envelope.cpp",
    "src/frame_envelope.hpp",
    "src/frame_source.cpp",
    "src/frame_source.hpp",
    "src/common.h",
    "src/libbz3.cpp",
    "src/libsais.h",
    "src/parallel_codec.cpp",
    "src/pinned_file.cpp",
    "src/profile.cpp",
    "src/release_audit.cpp",
    "src/resource_plan.cpp",
    "src/sha256.cpp",
    "src/zip_preflight.cpp",
    "tools/bzip4_activation_probe.cpp",
    "tools/bzip4_codec.cpp",
    "tools/bzip4_cube_preflight.cpp",
    "tools/bzip4_release_audit.cpp",
    "tests/oracle_api.hpp",
    "tests/test_main.cpp",
    "scripts/make_manifest.sh",
    "scripts/validate.sh",
    "docs/ACTIVATION_AUDIT.md",
    "docs/ATOMIC_OUTPUT_AUDIT.md",
    "docs/BLOCK_DECODER_AUDIT.md",
    "docs/BLOCK_WORKSPACE_AUDIT.md",
    "docs/BINARY_DISTRIBUTION.md",
    "docs/CHECKSUM_FUSION_AUDIT.md",
    "docs/CODEC_ALLOCATION_AUDIT.md",
    "docs/ENTROPY_HOT_LOOP_AUDIT.md",
    "docs/ENTROPY_TRANSFORM_AUDIT.md",
    "docs/EFFECTIVENESS_SCORECARD.md",
    "docs/CUBE_PREFLIGHT.md",
    "docs/COMPILER_AND_LIBSAIS_AUDIT.md",
    "docs/DATACUBE_WELDPOINT_ANALYSIS.md",
    "docs/FRAME_STREAMING_AUDIT.md",
    "docs/FRAME_SOURCE_REFACTOR_AUDIT.md",
    "docs/FRAME_WORKSPACE_CONTRACTION_AUDIT.md",
    "docs/HIGH_LEVEL_C_API_AUDIT.md",
    "docs/LIBSAIS_UB_AUDIT.md",
    "docs/LINEAGE.md",
    "docs/PINNED_INPUT_AUDIT.md",
    "docs/PREDICTION_REGISTER.md",
    "docs/PROFILE_POLICY.md",
    "docs/PARALLEL_FRAME_ENCODER_AUDIT.md",
    "docs/PARALLEL_FRAME_DECODER_AUDIT.md",
    "docs/RETAINED_LANE_CORE_AUDIT.md",
    "docs/SPEED_FIRST_BLOCK_POLICY.md",
    "docs/RANGE_BACKED_INPUT_AUDIT.md",
    "docs/RESOURCE_FIT_AUDIT.md",
    "docs/UPSTREAM_FRAME_AUDIT.md",
    "docs/ZIP_CENTRAL_STREAM_AUDIT.md",
    "docs/ZIP_EXTRA_FIELD_AUDIT.md",
    "docs/ZIP_ENTRY_TYPE_AUDIT.md",
    "docs/ZIP64_BOUNDARY_AUDIT.md",
    "docs/ZIP_METADATA_ARENA_AUDIT.md",
    "docs/ZIP_PAYLOAD_NOMINATION_AUDIT.md",
    "evidence/compiler-fair-matrix.json",
    "evidence/current-session-block-size-frontier.json",
    "evidence/datacube-capsule-speed-frontier.json",
    "evidence/datacube-weldpoint-observation.json",
    "evidence/ipo-witness.json",
    "evidence/libsais-compaction-decrement-regression.json",
    "evidence/prediction-register.json",
    "evidence/profile-policy-regression.json",
    "evidence/resource-fit-regression.json",
    "evidence/static-binary-witness.json",
    "evidence/zip64-boundary-regression.json",
    "evidence/zip-metadata-arena-regression.json",
    "evidence/zip-payload-nomination-regression.json",
    "evidence/representative-payload-nomination.json",
    "docs/ROADMAP.md",
    "upstream/PROVENANCE.md",
    "upstream/bzip3-1.5.3-53984ef/include/common.h",
    "upstream/bzip3-1.5.3-53984ef/include/libbz3.h",
    "upstream/bzip3-1.5.3-53984ef/include/libsais.h",
    "upstream/bzip3-1.5.3-53984ef/src/libbz3.c",
});

void issue(AuditReport& report, std::string code, std::string message,
           std::filesystem::path path = {}) {
    report.issues.push_back({std::move(code), std::move(message), std::move(path)});
}

[[nodiscard]] std::string json_escape(std::string_view value) {
    std::ostringstream output;
    for (const char raw : value) {
        const auto byte = static_cast<unsigned char>(raw);
        switch (byte) {
        case '"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (byte < 0x20U) {
                output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                       << static_cast<unsigned>(byte) << std::dec;
            } else {
                output << static_cast<char>(byte);
            }
        }
    }
    return output.str();
}

[[nodiscard]] bool hex_digest(std::string_view value) {
    return value.size() == 64 && std::all_of(value.begin(), value.end(), [](unsigned char byte) {
        return std::isxdigit(byte) != 0 && (std::isdigit(byte) != 0 || std::islower(byte) != 0);
    });
}

[[nodiscard]] bool unsafe_relative_path(const std::filesystem::path& path) {
    if (path.empty() || path.is_absolute()) return true;
    for (const auto& component : path) {
        if (component == ".." || component == ".") return true;
    }
    return false;
}

[[nodiscard]] bool build_junk(const std::filesystem::path& relative) {
    const auto first = relative.begin();
    if (first != relative.end()) {
        const std::string top_level = first->string();
        if (top_level == "build" || top_level.starts_with("build-") ||
            top_level.starts_with("cmake-build-")) {
            return true;
        }
    }

    for (const auto& component : relative) {
        const std::string value = component.string();
        if (value == ".git" || value == ".svn" || value == "CMakeFiles" ||
            value == "__pycache__" || value == ".pytest_cache") {
            return true;
        }
    }
    const std::string filename = relative.filename().string();
    return filename.ends_with(".o") || filename.ends_with(".a") || filename.ends_with(".so") ||
        filename.ends_with(".pyc") || filename == "CMakeCache.txt";
}

} // namespace

std::span<const std::string_view> required_release_paths() noexcept {
    return required_paths;
}

AuditReport audit_release_tree(const std::filesystem::path& root) {
    AuditReport report;
    report.root = root;
    std::error_code error;
    const auto root_status = std::filesystem::symlink_status(root, error);
    if (error || !std::filesystem::is_directory(root_status) || std::filesystem::is_symlink(root_status)) {
        issue(report, "root_invalid", "release root must be a real directory", root);
        return report;
    }

    for (const std::string_view required : required_release_paths()) {
        const std::filesystem::path path = root / required;
        const auto status = std::filesystem::symlink_status(path, error);
        if (error || !std::filesystem::is_regular_file(status) || std::filesystem::is_symlink(status)) {
            issue(report, "required_missing", "required source-closure file is missing", required);
            error.clear();
        }
    }

    std::set<std::string> regular_paths;
    std::filesystem::recursive_directory_iterator iterator(
        root, std::filesystem::directory_options::none, error);
    if (error) {
        issue(report, "walk_failed", "unable to start release-tree walk", root);
        return report;
    }
    const std::filesystem::recursive_directory_iterator end;
    while (iterator != end) {
        const std::filesystem::directory_entry entry = *iterator;
        const std::filesystem::path relative = entry.path().lexically_relative(root);
        const auto status = entry.symlink_status(error);
        if (error) {
            issue(report, "status_failed", "unable to inspect release entry", relative);
            error.clear();
            iterator.increment(error);
            continue;
        }
        if (std::filesystem::is_symlink(status)) {
            issue(report, "symlink_forbidden", "symlinks are forbidden in the release tree", relative);
            iterator.disable_recursion_pending();
        } else if (std::filesystem::is_directory(status)) {
            if (build_junk(relative)) {
                issue(report, "build_junk", "build/cache directory is forbidden", relative);
                iterator.disable_recursion_pending();
            }
        } else if (std::filesystem::is_regular_file(status)) {
            ++report.regular_files;
            const std::string generic = relative.generic_string();
            regular_paths.insert(generic);
            if (build_junk(relative)) {
                issue(report, "build_junk", "compiled/cache artifact is forbidden", relative);
            }
        } else {
            issue(report, "special_file", "only directories and regular files are allowed", relative);
        }
        iterator.increment(error);
        if (error) {
            issue(report, "walk_failed", "release-tree walk failed", relative);
            error.clear();
        }
    }

    const std::filesystem::path manifest_path = root / "MANIFEST.sha256";
    std::ifstream manifest(manifest_path);
    if (!manifest) {
        issue(report, "manifest_missing", "MANIFEST.sha256 is missing", "MANIFEST.sha256");
        return report;
    }

    std::map<std::string, std::string> expected;
    std::string line;
    std::size_t line_number = 0;
    while (std::getline(manifest, line)) {
        ++line_number;
        if (line.empty()) continue;
        if (line.size() < 67 || line[64] != ' ' || line[65] != ' ') {
            issue(report, "manifest_syntax", "invalid manifest line " + std::to_string(line_number),
                  "MANIFEST.sha256");
            continue;
        }
        const std::string digest = line.substr(0, 64);
        const std::string name = line.substr(66);
        if (!hex_digest(digest)) {
            issue(report, "manifest_digest", "invalid lowercase SHA-256 on line " +
                  std::to_string(line_number), "MANIFEST.sha256");
            continue;
        }
        const std::filesystem::path relative(name);
        if (unsafe_relative_path(relative) || relative.generic_string() != name || name == "MANIFEST.sha256") {
            issue(report, "manifest_path", "unsafe or noncanonical path on line " +
                  std::to_string(line_number), name);
            continue;
        }
        if (!expected.emplace(name, digest).second) {
            issue(report, "manifest_duplicate", "duplicate manifest path", name);
        }
    }
    if (!manifest.eof()) {
        issue(report, "manifest_read", "failed while reading MANIFEST.sha256", "MANIFEST.sha256");
    }
    report.manifest_entries = expected.size();

    regular_paths.erase("MANIFEST.sha256");
    for (const std::string& path : regular_paths) {
        const auto found = expected.find(path);
        if (found == expected.end()) {
            issue(report, "manifest_uncovered", "regular file is absent from manifest", path);
            continue;
        }
        try {
            const std::string actual = hex_sha256_file(root / path);
            if (actual != found->second) {
                issue(report, "hash_mismatch", "manifest digest does not match file bytes", path);
            }
        } catch (const std::exception& exception) {
            issue(report, "hash_failed", exception.what(), path);
        }
    }
    for (const auto& [path, digest] : expected) {
        (void)digest;
        if (!regular_paths.contains(path)) {
            issue(report, "manifest_stale", "manifest path is absent or not a regular file", path);
        }
    }
    return report;
}

std::string audit_report_json(const AuditReport& report, bool pretty) {
    const std::string newline = pretty ? "\n" : "";
    const std::string indent1 = pretty ? "  " : "";
    const std::string indent2 = pretty ? "    " : "";
    std::ostringstream output;
    output << '{' << newline
           << indent1 << "\"schema\":\"bzip4.release-audit.v1\"," << newline
           << indent1 << "\"root\":\"" << json_escape(report.root.string()) << "\"," << newline
           << indent1 << "\"ok\":" << (report.ok() ? "true" : "false") << ',' << newline
           << indent1 << "\"regular_files\":" << report.regular_files << ',' << newline
           << indent1 << "\"manifest_entries\":" << report.manifest_entries << ',' << newline
           << indent1 << "\"issues\":[";
    if (pretty && !report.issues.empty()) output << newline;
    for (std::size_t index = 0; index < report.issues.size(); ++index) {
        const AuditIssue& value = report.issues[index];
        output << indent2 << "{\"code\":\"" << json_escape(value.code)
               << "\",\"message\":\"" << json_escape(value.message)
               << "\",\"path\":\"" << json_escape(value.path.generic_string()) << "\"}";
        if (index + 1 != report.issues.size()) output << ',';
        if (pretty) output << newline;
    }
    output << indent1 << ']' << newline << '}' << newline;
    return output.str();
}

} // namespace bzip4
