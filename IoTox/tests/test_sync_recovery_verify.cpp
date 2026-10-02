#include "test_harness.hpp"

#include "iotox/security/sodium.hpp"
#include "iotox/sync_recovery_verify.hpp"

#include <filesystem>
#include <fstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
public:
  TemporaryDirectory() {
    std::string pattern = "/tmp/iotox-sync-recovery-verify-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
    if (created != nullptr)
      root_ = created;
  }
  ~TemporaryDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(root_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &root() const { return root_; }

private:
  std::filesystem::path root_;
};

void make_directory(const std::filesystem::path &path) {
  std::filesystem::create_directory(path);
  IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0700)) == 0);
}

void write_file(const std::filesystem::path &path, std::string_view content,
                mode_t mode = 0600) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(content.data(), static_cast<std::streamsize>(content.size()));
  output.close();
  IOTOX_CHECK(output.good());
  IOTOX_CHECK(::chmod(path.c_str(), mode) == 0);
}

} // namespace

IOTOX_TEST("sync recovery verifier accepts one exact external restore") {
  TemporaryDirectory temporary;
  IOTOX_CHECK(!temporary.root().empty());
  const auto backup = temporary.root() / "backup";
  const auto restored = temporary.root() / "restored";
  make_directory(backup);
  make_directory(restored);
  make_directory(backup / "docs");
  make_directory(restored / "docs");
  write_file(backup / "docs" / "note", "recovered", 0400);
  write_file(restored / "docs" / "note", "recovered", 0400);
  write_file(backup / "run", "#!/bin/sh\n", 0700);
  write_file(restored / "run", "#!/bin/sh\n", 0700);

  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  iotox::sync::SyncRecoveryVerifyOptions options;
  options.backup_root = backup;
  options.restored_root = restored;
  auto report =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().matches);
  IOTOX_CHECK(report.value().backup_manifest ==
              report.value().restored_manifest);
  IOTOX_CHECK(report.value().backup_directories == 1U);
  IOTOX_CHECK(report.value().backup_files == 2U);
  IOTOX_CHECK(report.value().backup_entries == 3U);
  IOTOX_CHECK(report.value().backup_bytes == 19U);
  const std::string rendered =
      iotox::sync::render_sync_recovery_verify_report(report.value());
  IOTOX_CHECK(
      rendered.starts_with("iotox-sync-recovery-verify-v1\ndecision=match\n"));
  IOTOX_CHECK(rendered.find("filesystem-contract=ready\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("stable-double-scan=ready\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("iotox-live-state-read=0\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("root-devices-differ=") != std::string::npos);
  IOTOX_CHECK(rendered.find("operator-provenance=absent\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup-independence=not-assessed\n") !=
              std::string::npos);
}

IOTOX_TEST("sync recovery verifier retains optional operator provenance") {
  TemporaryDirectory temporary;
  const auto backup = temporary.root() / "backup";
  const auto restored = temporary.root() / "restored";
  make_directory(backup);
  make_directory(restored);
  write_file(backup / "note", "recovered", 0600);
  write_file(restored / "note", "recovered", 0600);

  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  iotox::sync::SyncRecoveryVerifyOptions options;
  options.backup_root = backup;
  options.restored_root = restored;
  options.backup_system = "restic";
  options.backup_generation = "snapshot-001";
  options.backup_failure_domain = "desktop-usb-disk";
  options.restore_provenance = "manual-restore-2026-09-10";
  auto report =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().matches);
  IOTOX_CHECK(report.value().operator_provenance_present);
  const std::string rendered =
      iotox::sync::render_sync_recovery_verify_report(report.value());
  IOTOX_CHECK(rendered.find("operator-provenance=present\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup-system-hex=726573746963\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup-generation-hex=736E617073686F742D303031\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup-failure-domain-hex=6465736B746F702D7573622D6469736B\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("restore-provenance-hex=6D616E75616C2D726573746F72652D323032362D30392D3130\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup-independence=not-assessed\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("restore-provenance=not-assessed\n") !=
              std::string::npos);
}

IOTOX_TEST("sync recovery verifier reports content and mode mismatch") {
  TemporaryDirectory temporary;
  const auto backup = temporary.root() / "backup";
  const auto restored = temporary.root() / "restored";
  make_directory(backup);
  make_directory(restored);
  write_file(backup / "note", "expected", 0600);
  write_file(restored / "note", "different", 0700);

  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  iotox::sync::SyncRecoveryVerifyOptions options;
  options.backup_root = backup;
  options.restored_root = restored;
  auto report =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(!report.value().matches);
  IOTOX_CHECK(report.value().backup_manifest !=
              report.value().restored_manifest);
  IOTOX_CHECK(
      iotox::sync::render_sync_recovery_verify_report(report.value())
          .starts_with("iotox-sync-recovery-verify-v1\ndecision=mismatch\n"));
}

IOTOX_TEST("sync recovery verifier refuses aliased nested or conflict roots") {
  TemporaryDirectory temporary;
  const auto backup = temporary.root() / "backup";
  const auto restored = temporary.root() / "restored";
  make_directory(backup);
  make_directory(backup / "nested");
  make_directory(restored);
  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());

  iotox::sync::SyncRecoveryVerifyOptions options;
  options.backup_root = backup;
  options.restored_root = backup;
  auto same = iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK(!same.ok());
  IOTOX_CHECK(same.status().code() == iotox::ErrorCode::invalid_argument);

  options.restored_root = backup / "nested";
  auto nested =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK(!nested.ok());
  IOTOX_CHECK(nested.status().code() == iotox::ErrorCode::invalid_argument);

  options.restored_root = restored;
  options.maximum_bytes = (std::uint64_t{1U} << 60U) + 1U;
  auto unbounded =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK(!unbounded.ok());
  IOTOX_CHECK(unbounded.status().code() == iotox::ErrorCode::invalid_argument);

  options.maximum_bytes = 64U * 1024U * 1024U;
  options.backup_system = "restic";
  auto partial_provenance =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK(!partial_provenance.ok());
  IOTOX_CHECK(partial_provenance.status().code() ==
              iotox::ErrorCode::invalid_argument);
  options.backup_system.reset();

  make_directory(backup / ".iotox-conflicts");
  auto conflicts =
      iotox::sync::verify_sync_recovery_trees(options, sodium.value());
  IOTOX_CHECK(!conflicts.ok());
  IOTOX_CHECK(conflicts.status().code() == iotox::ErrorCode::protocol_error);
}
