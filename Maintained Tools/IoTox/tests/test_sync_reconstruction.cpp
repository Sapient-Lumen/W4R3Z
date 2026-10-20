#include "iotox/sync_digest.hpp"
#include "iotox/sync_manifest.hpp"
#include "iotox/sync_reconstruction.hpp"

#include "test_harness.hpp"

#include <algorithm>
#include <cstdint>
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
    std::string pattern = "/tmp/iotox-sync-reconstruct-XXXXXX";
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
  result.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_store_bytes = 8U * 1024U * 1024U;
  result.quotas.maximum_staging_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_objects = 32U;
  result.quotas.maximum_outstanding_requests = 64U;
  return result;
}

void write_bytes(const std::filesystem::path &path,
                 const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output) throw std::runtime_error("fixture write failed");
  output.close();
  if (::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
    throw std::runtime_error("fixture chmod failed");
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return {std::istreambuf_iterator<char>(input),
          std::istreambuf_iterator<char>()};
}

void prepare_store(const iotox::sync::NamespacePolicy &configured) {
  IOTOX_CHECK(std::filesystem::create_directories(
      std::filesystem::path(configured.root) / "objects"));
  IOTOX_CHECK(::chmod(configured.root.c_str(), static_cast<mode_t>(0700)) == 0);
  IOTOX_CHECK(::chmod((std::filesystem::path(configured.root) / "objects").c_str(),
                      static_cast<mode_t>(0700)) == 0);
}

iotox::sync::SyncObjectRecord install_fixture_object(
    const iotox::sync::NamespacePolicy &configured,
    iotox::sync::SyncObjectKind kind,
    const std::filesystem::path &source) {
  auto digest = iotox::sync::hash_sync_file_sha256(source);
  IOTOX_CHECK_MSG(digest.ok(), digest.status().message());
  const auto bytes = std::filesystem::file_size(source);
  iotox::sync::SyncObjectRecord object{kind, digest.value(), bytes};
  const auto destination = iotox::sync::sync_object_path(configured, object);
  IOTOX_CHECK(std::filesystem::copy_file(source, destination));
  IOTOX_CHECK(::chmod(destination.c_str(), static_cast<mode_t>(0600)) == 0);
  return object;
}

std::vector<std::uint8_t> target_bytes() {
  std::vector<std::uint8_t> result(512U * 1024U);
  for (std::size_t index = 0U; index < result.size(); ++index) {
    result[index] = static_cast<std::uint8_t>(
        (index * 37U + index / 251U + 19U) & 0xffU);
  }
  return result;
}

bool inside_missing(const iotox::sync::SyncRangePlan &plan,
                    std::uint64_t offset, std::size_t bytes) {
  return std::any_of(
      plan.missing_ranges.begin(), plan.missing_ranges.end(),
      [offset, bytes](const iotox::sync::SyncMissingRange &range) {
        return offset >= range.offset && offset <= range.offset + range.length &&
               bytes <= range.offset + range.length - offset;
      });
}

} // namespace

IOTOX_TEST("sync range reconstruction fetches only missing target ranges and commits exact artifact") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  prepare_store(configured);
  auto target = target_bytes();
  auto basis = target;
  std::fill(basis.begin() + 192U * 1024U,
            basis.begin() + 208U * 1024U, 0xD3U);
  const auto target_source = temporary.path() / "target.bin";
  const auto basis_source = temporary.path() / "basis.bin";
  const auto manifest_source = temporary.path() / "target.index";
  write_bytes(target_source, target);
  write_bytes(basis_source, basis);
  auto built = iotox::sync::build_sync_range_manifest(
      configured, target_source, manifest_source);
  IOTOX_CHECK_MSG(built.ok(), built.status().message());
  const auto basis_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::artifact, basis_source);
  const auto manifest_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::manifest, manifest_source);
  const iotox::sync::SyncObjectRecord target_object{
      iotox::sync::SyncObjectKind::artifact, built.value().artifact,
      built.value().artifact_bytes};
  iotox::sync::SyncInstallSeams install;
  install.hash_file = iotox::sync::hash_sync_file_sha256;

  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
  auto plan = iotox::sync::plan_sync_range_reconstruction(
      configured, target_object, manifest_object, basis_object,
      transaction.value(), install);
  IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
  IOTOX_CHECK(plan.value().reused_bytes > 0U);
  IOTOX_CHECK(plan.value().missing_bytes > 0U);
  IOTOX_CHECK(plan.value().missing_bytes < target.size());
  IOTOX_CHECK(plan.value().reused_bytes + plan.value().missing_bytes ==
              target.size());

  std::uint64_t supplied = 0U;
  iotox::sync::SyncRangeReconstructionSeams seams;
  seams.install = install;
  seams.read_range = [&](std::uint64_t offset,
                         std::span<std::uint8_t> output)
      -> iotox::Result<std::size_t> {
    IOTOX_CHECK(inside_missing(plan.value(), offset, output.size()));
    IOTOX_CHECK(offset <= target.size());
    IOTOX_CHECK(output.size() <= target.size() - offset);
    std::copy_n(target.begin() + static_cast<std::ptrdiff_t>(offset),
                output.size(), output.begin());
    supplied += output.size();
    return output.size();
  };
  auto reconstructed = iotox::sync::reconstruct_sync_range_artifact(
      configured, plan.value(), 41U, transaction.value(), seams);
  IOTOX_CHECK_MSG(reconstructed.ok(), reconstructed.status().message());
  IOTOX_CHECK(reconstructed.value().reused_bytes == plan.value().reused_bytes);
  IOTOX_CHECK(reconstructed.value().fetched_bytes == plan.value().missing_bytes);
  IOTOX_CHECK(supplied == plan.value().missing_bytes);
  IOTOX_CHECK(read_bytes(reconstructed.value().staging_path) == target);

  auto committed = iotox::sync::commit_sync_attempt_staging(
      configured, 41U, target_object, transaction.value(), install);
  IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
  IOTOX_CHECK(read_bytes(iotox::sync::sync_object_path(
                  configured, target_object)) == target);
}

IOTOX_TEST("sync range reconstruction rejects corrupt source and removes exact staging") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  prepare_store(configured);
  auto target = target_bytes();
  auto basis = target;
  std::fill(basis.begin() + 64U * 1024U,
            basis.begin() + 96U * 1024U, 0xA7U);
  const auto target_source = temporary.path() / "target.bin";
  const auto basis_source = temporary.path() / "basis.bin";
  const auto manifest_source = temporary.path() / "target.index";
  write_bytes(target_source, target);
  write_bytes(basis_source, basis);
  auto built = iotox::sync::build_sync_range_manifest(
      configured, target_source, manifest_source);
  IOTOX_CHECK(built.ok());
  const auto basis_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::artifact, basis_source);
  const auto manifest_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::manifest, manifest_source);
  const iotox::sync::SyncObjectRecord target_object{
      iotox::sync::SyncObjectKind::artifact, built.value().artifact,
      built.value().artifact_bytes};
  iotox::sync::SyncInstallSeams install;
  install.hash_file = iotox::sync::hash_sync_file_sha256;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto plan = iotox::sync::plan_sync_range_reconstruction(
      configured, target_object, manifest_object, basis_object,
      transaction.value(), install);
  IOTOX_CHECK(plan.ok() && plan.value().missing_bytes > 0U);

  bool corrupted = false;
  iotox::sync::SyncRangeReconstructionSeams seams;
  seams.install = install;
  seams.read_range = [&](std::uint64_t offset,
                         std::span<std::uint8_t> output)
      -> iotox::Result<std::size_t> {
    std::copy_n(target.begin() + static_cast<std::ptrdiff_t>(offset),
                output.size(), output.begin());
    if (!corrupted && !output.empty()) {
      output.front() ^= 0x80U;
      corrupted = true;
    }
    return output.size();
  };
  auto reconstructed = iotox::sync::reconstruct_sync_range_artifact(
      configured, plan.value(), 57U, transaction.value(), seams);
  IOTOX_CHECK(!reconstructed.ok());
  IOTOX_CHECK(reconstructed.status().code() == iotox::ErrorCode::protocol_error);
  const auto staging = std::filesystem::path(configured.root) /
                       "staging" / "0000000000000039.part";
  IOTOX_CHECK(!std::filesystem::exists(staging));
  IOTOX_CHECK(!std::filesystem::exists(
      std::filesystem::path(staging.string() + ".toxsync.part")));
}

IOTOX_TEST("sync range reconstruction revalidates immutable basis and plan before output") {
  TempDirectory temporary;
  const auto configured = policy(temporary.path() / "namespace");
  prepare_store(configured);
  auto target = target_bytes();
  auto basis = target;
  basis[12345U] ^= 0x44U;
  const auto target_source = temporary.path() / "target.bin";
  const auto basis_source = temporary.path() / "basis.bin";
  const auto manifest_source = temporary.path() / "target.index";
  write_bytes(target_source, target);
  write_bytes(basis_source, basis);
  auto built = iotox::sync::build_sync_range_manifest(
      configured, target_source, manifest_source);
  IOTOX_CHECK(built.ok());
  const auto basis_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::artifact, basis_source);
  const auto manifest_object = install_fixture_object(
      configured, iotox::sync::SyncObjectKind::manifest, manifest_source);
  const iotox::sync::SyncObjectRecord target_object{
      iotox::sync::SyncObjectKind::artifact, built.value().artifact,
      built.value().artifact_bytes};
  iotox::sync::SyncInstallSeams install;
  install.hash_file = iotox::sync::hash_sync_file_sha256;
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto plan = iotox::sync::plan_sync_range_reconstruction(
      configured, target_object, manifest_object, basis_object,
      transaction.value(), install);
  IOTOX_CHECK(plan.ok());

  auto malformed = plan.value();
  malformed.missing_bytes += 1U;
  iotox::sync::SyncRangeReconstructionSeams seams;
  seams.install = install;
  seams.read_range = [](std::uint64_t, std::span<std::uint8_t>)
      -> iotox::Result<std::size_t> { return 0U; };
  auto refused = iotox::sync::reconstruct_sync_range_artifact(
      configured, malformed, 71U, transaction.value(), seams);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(!std::filesystem::exists(
      std::filesystem::path(configured.root) / "staging" /
      "0000000000000047.part"));

  auto corrupt_basis = read_bytes(
      iotox::sync::sync_object_path(configured, basis_object));
  corrupt_basis.front() ^= 0x20U;
  write_bytes(iotox::sync::sync_object_path(configured, basis_object),
              corrupt_basis);
  refused = iotox::sync::reconstruct_sync_range_artifact(
      configured, plan.value(), 72U, transaction.value(), seams);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(!std::filesystem::exists(
      std::filesystem::path(configured.root) / "staging" /
      "0000000000000048.part"));
}
