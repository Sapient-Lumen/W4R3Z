#pragma once

#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace bzip4 {

struct AuditIssue {
    std::string code;
    std::string message;
    std::filesystem::path path;
};

struct AuditReport {
    std::filesystem::path root;
    std::size_t regular_files{};
    std::size_t manifest_entries{};
    std::vector<AuditIssue> issues;

    [[nodiscard]] bool ok() const noexcept { return issues.empty(); }
};

/** Canonical source-closure paths enforced by audit_release_tree(). */
[[nodiscard]] std::span<const std::string_view> required_release_paths() noexcept;

/** Verify source closure, manifest coverage, hashes, and package hygiene. */
[[nodiscard]] AuditReport audit_release_tree(const std::filesystem::path& root);
[[nodiscard]] std::string audit_report_json(const AuditReport& report, bool pretty = true);

} // namespace bzip4
