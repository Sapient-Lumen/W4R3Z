#include "test_harness.hpp"

#include "iotox/sync_doctor.hpp"
#include "iotox/sync_multiwriter_reconcile.hpp"
#include "iotox/sync_transaction.hpp"

#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/xattr.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
public:
  TemporaryDirectory() {
    std::string pattern = "/tmp/iotox-sync-doctor-XXXXXX";
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

IOTOX_TEST("sync doctor inventories one-writer trees without writing state") {
  TemporaryDirectory temporary;
  IOTOX_CHECK(!temporary.root().empty());
  const auto source = temporary.root() / "source";
  make_directory(source);
  make_directory(source / "docs");
  write_file(source / "docs" / "a", "abc");
  write_file(source / "b", "hello", 0700);

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  auto report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().source == source);
  IOTOX_CHECK(report.value().engine == iotox::sync::Engine::treepack_v1);
  IOTOX_CHECK(report.value().directories == 1U);
  IOTOX_CHECK(report.value().files == 2U);
  IOTOX_CHECK(report.value().entries == 3U);
  IOTOX_CHECK(report.value().content_bytes == 8U);
  IOTOX_CHECK(report.value().artifact_bytes == 115U);
  IOTOX_CHECK(report.value().estimated_objects == 1U);
  IOTOX_CHECK(report.value().minimum_staging_bytes >
              report.value().artifact_bytes);
  IOTOX_CHECK(std::filesystem::exists(source / "docs" / "a"));
  IOTOX_CHECK(std::filesystem::exists(source / "b"));
  IOTOX_CHECK(std::distance(std::filesystem::directory_iterator(source),
                            std::filesystem::directory_iterator{}) == 2);

  const std::string rendered =
      iotox::sync::render_sync_doctor_report(report.value());
  IOTOX_CHECK(rendered.starts_with("iotox-sync-doctor-v3\ndecision=ready\n"));
  IOTOX_CHECK(rendered.find("engine=treepack-v1\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("managed-storage-headroom=not-probed\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("backup=not-assessed\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("filesystem-contract=ready\n") !=
              std::string::npos);
  IOTOX_CHECK(
      rendered.find("path-model=byte-exact-case-sensitive-required\n") !=
      std::string::npos);
  IOTOX_CHECK(rendered.find("acl-xattrs=refused\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("sparse-layout=refused\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("timestamps=not-preserved\n") != std::string::npos);
}

IOTOX_TEST("sync doctor shares writable selection and metadata semantics") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "source";
  make_directory(source);
  make_directory(source / "docs");
  make_directory(source / "docs" / "cache");
  write_file(source / "docs" / "keep", "kept", 0600);
  write_file(source / "docs" / "cache" / "ignored", "ignored", 0600);

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.access = iotox::sync::SyncDoctorAccess::read_write;
  options.projection.metadata = iotox::sync::TreeV2MetadataMode::owner_mode_v2;
  options.projection.includes = {"docs"};
  options.projection.excludes = {"docs/cache"};
  auto report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().engine == iotox::sync::Engine::tree_v2);
  IOTOX_CHECK(report.value().directories == 1U);
  IOTOX_CHECK(report.value().files == 1U);
  IOTOX_CHECK(report.value().entries == 2U);
  IOTOX_CHECK(report.value().content_bytes == 4U);
  IOTOX_CHECK(report.value().manifest_bytes > 0U);
  IOTOX_CHECK(report.value().estimated_objects == 2U);

  std::error_code error;
  std::filesystem::create_symlink(source / "docs" / "keep", source / "unsafe",
                                  error);
  IOTOX_CHECK(!error);
  auto refused = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync doctor bounds and hashes one regular content source") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "artifact";
  write_file(source, "iotox-doctor");

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.interval_seconds = 17U;
  auto report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().engine == iotox::sync::Engine::content_v2);
  IOTOX_CHECK(report.value().files == 1U);
  IOTOX_CHECK(report.value().content_bytes == 12U);
  IOTOX_CHECK(report.value().interval_seconds == 17U);
  IOTOX_CHECK(report.value().manifest_bytes > 0U);

  write_file(source, "");
  auto empty = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!empty.ok());
  IOTOX_CHECK(empty.status().code() == iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("sync doctor refuses filesystem metadata it cannot preserve") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "source";
  make_directory(source);
  const auto ordinary = source / "ordinary";
  write_file(ordinary, "ordinary");

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.access = iotox::sync::SyncDoctorAccess::read_write;

  constexpr char xattr_value[] = "present";
  IOTOX_CHECK(::setxattr(ordinary.c_str(), "user.iotox-doctor-test",
                         xattr_value, sizeof(xattr_value) - 1U, 0) == 0);
  auto extended = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!extended.ok());
  IOTOX_CHECK(extended.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(::removexattr(ordinary.c_str(), "user.iotox-doctor-test") == 0);

  const auto sparse = source / "sparse";
  const int sparse_fd =
      ::open(sparse.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
  IOTOX_CHECK(sparse_fd >= 0);
  IOTOX_CHECK(::ftruncate(sparse_fd, static_cast<off_t>(1024U * 1024U)) == 0);
  IOTOX_CHECK(::close(sparse_fd) == 0);
  auto sparse_result = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!sparse_result.ok());
  IOTOX_CHECK(sparse_result.status().code() ==
              iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(std::filesystem::remove(sparse));

  const auto linked = source / "linked";
  std::filesystem::create_hard_link(ordinary, linked);
  auto hard_link = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!hard_link.ok());
  IOTOX_CHECK(hard_link.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(std::filesystem::remove(linked));

  const auto fifo = source / "fifo";
  IOTOX_CHECK(::mkfifo(fifo.c_str(), static_cast<mode_t>(0600)) == 0);
  auto special = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!special.ok());
  IOTOX_CHECK(special.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("sync doctor refuses ASCII case-fold collisions") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "source";
  make_directory(source);
  write_file(source / "Readme", "upper");
  write_file(source / "README", "lower");

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.access = iotox::sync::SyncDoctorAccess::read_write;
  auto report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK(!report.ok());
  IOTOX_CHECK(report.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST(
    "configured sync doctor proves managed quota and filesystem headroom") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "artifact";
  write_file(source, "configured-doctor");
  const auto managed = temporary.root() / "managed";
  make_directory(managed);

  iotox::sync::NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = managed.string();
  policy.engine = iotox::sync::Engine::content_v2;
  policy.activation = iotox::sync::ActivationMode::manual;
  iotox::sync::PrincipalId device{};
  device.front() = 1U;
  policy.writers = {device};
  IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());

  // A configured namespace has already been initialized by the Agent. The
  // doctor must consume, rather than create, its transaction boundary.
  {
    auto initialized = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
  }
  make_directory(managed / "staging");
  write_file(managed / "staging" / "partial", "pending");

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.quotas = policy.quotas;
  auto source_report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(source_report.ok(), source_report.status().message());
  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  auto report = iotox::sync::inspect_sync_managed_storage(
      source_report.value(), policy, device, sodium.value(), 7U, 1750U);
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().managed_storage_probed);
  IOTOX_CHECK(report.value().configured_namespace == "field-notes");
  IOTOX_CHECK(report.value().automation_generation == 7U);
  IOTOX_CHECK(report.value().automation_interval_ms == 1750U);
  IOTOX_CHECK(report.value().managed_store_objects == 0U);
  IOTOX_CHECK(report.value().managed_store_bytes == 0U);
  IOTOX_CHECK(report.value().managed_staging_bytes == 7U);
  IOTOX_CHECK(report.value().managed_store_headroom_bytes ==
              policy.quotas.maximum_store_bytes);
  IOTOX_CHECK(report.value().managed_staging_headroom_bytes ==
              policy.quotas.maximum_staging_bytes - 7U);
  IOTOX_CHECK(report.value().managed_filesystem_available_bytes > 0U);
  IOTOX_CHECK(report.value().managed_filesystem_required_bytes ==
              report.value().minimum_store_bytes +
                  report.value().minimum_staging_bytes);

  const std::string rendered =
      iotox::sync::render_sync_doctor_report(report.value());
  IOTOX_CHECK(rendered.find("configured-namespace=field-notes\n") !=
              std::string::npos);
  IOTOX_CHECK(rendered.find("managed-staging-bytes=7\n") != std::string::npos);
  IOTOX_CHECK(rendered.find("managed-storage-headroom=ready\n") !=
              std::string::npos);

  IOTOX_CHECK(::chmod((managed / "staging" / "partial").c_str(), 0644) == 0);
  auto unsafe = iotox::sync::inspect_sync_managed_storage(
      source_report.value(), policy, device, sodium.value(), 7U, 1750U);
  IOTOX_CHECK(!unsafe.ok());
  IOTOX_CHECK(unsafe.status().code() == iotox::ErrorCode::protocol_error);
  IOTOX_CHECK(::chmod((managed / "staging" / "partial").c_str(), 0600) == 0);

  auto impossible = source_report.value();
  impossible.minimum_store_bytes = policy.quotas.maximum_store_bytes + 1U;
  auto refused = iotox::sync::inspect_sync_managed_storage(
      std::move(impossible), policy, device, sodium.value(), 7U, 1750U);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::resource_exhausted);
}

IOTOX_TEST(
    "configured sync doctor refuses an uninitialized transaction boundary") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "artifact";
  write_file(source, "not-initialized");
  const auto managed = temporary.root() / "managed";
  make_directory(managed);
  iotox::sync::NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = managed.string();
  policy.engine = iotox::sync::Engine::content_v2;
  policy.activation = iotox::sync::ActivationMode::manual;
  iotox::sync::PrincipalId device{};
  device.front() = 1U;
  policy.writers = {device};
  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  auto source_report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(source_report.ok(), source_report.status().message());
  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  auto refused = iotox::sync::inspect_sync_managed_storage(
      source_report.value(), policy, device, sodium.value(), 1U, 30000U);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::not_found);
  IOTOX_CHECK(!std::filesystem::exists(managed / "transactions"));
}

IOTOX_TEST("configured sync doctor inventories a live writable tree-v2 store") {
  TemporaryDirectory temporary;
  const auto source = temporary.root() / "worktree";
  make_directory(source);
  constexpr std::string_view source_contents = "writable-state";
  write_file(source / "note", std::string(source_contents));
  const auto managed = temporary.root() / "managed";
  make_directory(managed);
  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
  auto identity = iotox::security::DeviceIdentity::load_or_create(
      temporary.root() / "device.identity", sodium.value(), true);
  IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

  iotox::sync::NamespacePolicy policy;
  policy.id = "writable";
  policy.root = managed.string();
  policy.engine = iotox::sync::Engine::tree_v2;
  policy.activation = iotox::sync::ActivationMode::manual;
  policy.writers = {identity.value().public_key()};
  {
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    auto reconciled = iotox::sync::reconcile_tree_v2_workspace(
        policy, source, identity.value(), sodium.value(), transaction.value());
    IOTOX_CHECK_MSG(reconciled.ok(), reconciled.status().message());
  }
  if (!std::filesystem::exists(managed / "tree-v2" / "incoming"))
    make_directory(managed / "tree-v2" / "incoming");
  write_file(managed / "tree-v2" / "incoming" / "partial", "incoming");

  iotox::sync::SyncDoctorOptions options;
  options.source = source;
  options.access = iotox::sync::SyncDoctorAccess::read_write;
  options.projection = policy.projection;
  options.quotas = policy.quotas;
  auto source_report = iotox::sync::inspect_sync_source(options);
  IOTOX_CHECK_MSG(source_report.ok(), source_report.status().message());
  auto report = iotox::sync::inspect_sync_managed_storage(
      source_report.value(), policy, identity.value().public_key(),
      sodium.value(), 1U, 30000U);
  IOTOX_CHECK_MSG(report.ok(), report.status().message());
  IOTOX_CHECK(report.value().managed_store_objects >= 3U);
  IOTOX_CHECK(report.value().managed_store_bytes > source_contents.size());
  IOTOX_CHECK(report.value().managed_staging_bytes == 8U);
  IOTOX_CHECK(report.value().source_filesystem_required_bytes ==
              source_contents.size());
  IOTOX_CHECK(report.value().managed_filesystem_required_bytes ==
              report.value().minimum_store_bytes +
                  report.value().minimum_staging_bytes +
                  source_contents.size());
}
