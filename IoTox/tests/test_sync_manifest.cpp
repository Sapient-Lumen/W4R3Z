#include "iotox/sync_digest.hpp"
#include "iotox/sync_manifest.hpp"

#include "test_harness.hpp"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-manifest-XXXXXX";
    std::vector<char> storage(pattern.begin(), pattern.end());
    storage.push_back('\0');
    char *created = ::mkdtemp(storage.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
  }
  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

private:
  std::filesystem::path path_;
};

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root) {
  iotox::sync::NamespacePolicy result;
  result.id = "field-notes";
  result.root = root.lexically_normal().string();
  iotox::sync::PrincipalId principal{};
  principal[0U] = 1U;
  result.writers = {principal};
  result.quotas.maximum_artifact_bytes = 8192U;
  result.quotas.maximum_manifest_bytes = 4096U;
  result.quotas.maximum_store_bytes = 16384U;
  result.quotas.maximum_staging_bytes = 8192U;
  return result;
}

void write_file(const std::filesystem::path &path, std::string_view bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  if (!output) throw std::runtime_error("fixture write failed");
  output.close();
  if (::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
    throw std::runtime_error("fixture chmod failed");
}

} // namespace

IOTOX_TEST("sync range manifest builds and verifies exact immutable artifact") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact";
  const auto manifest = temporary.path() / "artifact.index";
  write_file(artifact, "range-v1 immutable payload");
  auto built = iotox::sync::build_sync_range_manifest(
      configured, artifact, manifest);
  IOTOX_CHECK_MSG(built.ok(), built.status().message());
  IOTOX_CHECK(built.value().artifact_bytes == 26U);
  IOTOX_CHECK(built.value().manifest_bytes == 88U);
  IOTOX_CHECK(built.value().blocks == 1U);
  auto digest = iotox::sync::hash_sync_file_sha256(artifact);
  IOTOX_CHECK(digest.ok());
  IOTOX_CHECK(built.value().artifact == digest.value());
  IOTOX_CHECK(iotox::sync::verify_sync_range_manifest(
      configured, artifact, manifest, digest.value(),
      built.value().artifact_bytes, built.value().manifest_bytes).ok());

  auto wrong = digest.value();
  wrong[0U] ^= 0x80U;
  IOTOX_CHECK(!iotox::sync::verify_sync_range_manifest(
      configured, artifact, manifest, wrong,
      built.value().artifact_bytes, built.value().manifest_bytes).ok());
}

IOTOX_TEST("sync range manifest refuses corrupt metadata and impossible quota") {
  TempDirectory temporary;
  auto configured = policy(temporary.path() / "namespace");
  const auto artifact = temporary.path() / "artifact";
  const auto manifest = temporary.path() / "artifact.index";
  write_file(artifact, "range-v1 immutable payload");
  auto built = iotox::sync::build_sync_range_manifest(
      configured, artifact, manifest);
  IOTOX_CHECK(built.ok());
  auto digest = iotox::sync::hash_sync_file_sha256(artifact);
  IOTOX_CHECK(digest.ok());
  std::fstream changed(manifest,
                       std::ios::binary | std::ios::in | std::ios::out);
  changed.seekp(0);
  changed.put('X');
  changed.close();
  IOTOX_CHECK(!iotox::sync::verify_sync_range_manifest(
      configured, artifact, manifest, digest.value(),
      built.value().artifact_bytes, built.value().manifest_bytes).ok());

  configured.quotas.maximum_manifest_bytes = 65U;
  const auto too_small = temporary.path() / "too-small.index";
  IOTOX_CHECK(!iotox::sync::build_sync_range_manifest(
      configured, artifact, too_small).ok());
}
