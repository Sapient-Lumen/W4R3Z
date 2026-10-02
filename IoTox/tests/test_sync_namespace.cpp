#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/sync_namespace.hpp"
#include "iotox/sync_policy_witness.hpp"

#include <algorithm>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::sync::ActivationMode;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::NamespaceRegistry;
using iotox::sync::PrincipalId;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern =
        (std::filesystem::temp_directory_path() / "iotox-sync-policy-XXXXXX")
            .string();
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) {
      throw std::runtime_error("mkdtemp failed: " +
                               std::string(std::strerror(errno)));
    }
    path_ = created;
    if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0) {
      throw std::runtime_error("chmod failed: " +
                               std::string(std::strerror(errno)));
    }
  }

  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }

  TempDirectory(const TempDirectory &) = delete;
  TempDirectory &operator=(const TempDirectory &) = delete;

  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

private:
  std::filesystem::path path_;
};

PrincipalId principal(std::uint8_t first) {
  PrincipalId result{};
  result[0U] = first;
  return result;
}

NamespacePolicy sample_policy() {
  NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = "/var/lib/iotox/sync/field-notes";
  policy.engine = Engine::range_v1;
  policy.activation = ActivationMode::manual;
  policy.writers = {principal(1U), principal(2U)};
  policy.subscribers = {principal(3U)};
  return policy;
}

void make_directory(const std::filesystem::path &path, mode_t mode = 0700) {
  if (::mkdir(path.c_str(), mode) != 0) {
    throw std::runtime_error("mkdir failed: " +
                             std::string(std::strerror(errno)));
  }
}

void write_record(const std::filesystem::path &path,
                  const std::vector<std::uint8_t> &bytes, mode_t mode = 0600) {
  const int descriptor =
      ::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, mode);
  if (descriptor < 0) {
    throw std::runtime_error("open failed: " +
                             std::string(std::strerror(errno)));
  }
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count =
        ::write(descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    throw std::runtime_error("write failed: " +
                             std::string(std::strerror(saved)));
  }
  if (::close(descriptor) != 0) {
    throw std::runtime_error("close failed: " +
                             std::string(std::strerror(errno)));
  }
}

} // namespace

IOTOX_TEST("sync namespace policy round trips canonical bounded records") {
  NamespacePolicy policy = sample_policy();
  IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());
  auto encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());
  const std::string text(encoded.value().begin(), encoded.value().end());
  IOTOX_CHECK(text.starts_with("iotox-sync-namespace-v1\n"));
  IOTOX_CHECK(text.find("engine=range-v1\n") != std::string::npos);
  IOTOX_CHECK(text.find("activation=manual\n") != std::string::npos);
  auto decoded = iotox::sync::decode_namespace_policy(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == policy);

  policy.engine = Engine::content_v2;
  policy.activation = ActivationMode::disabled;
  encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());
  decoded = iotox::sync::decode_namespace_policy(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == policy);

  policy.engine = Engine::treepack_v1;
  encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());
  const std::string tree_text(encoded.value().begin(), encoded.value().end());
  IOTOX_CHECK(tree_text.find("engine=treepack-v1\n") != std::string::npos);
  decoded = iotox::sync::decode_namespace_policy(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == policy);

  policy.engine = Engine::tree_v2;
  encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());
  const std::string tree_v2_text(encoded.value().begin(),
                                 encoded.value().end());
  IOTOX_CHECK(tree_v2_text.find("engine=tree-v2\n") != std::string::npos);
  decoded = iotox::sync::decode_namespace_policy(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == policy);
}

IOTOX_TEST("sync policy witness commits exact namespace and automation tree") {
  TempDirectory temporary;
  auto sodium = iotox::security::Sodium::load();
  IOTOX_CHECK(sodium.ok());
  auto identity = iotox::security::DeviceIdentity::load_or_create(
      temporary.path() / "device.identity", sodium.value(), true);
  IOTOX_CHECK(identity.ok());
  const auto root = temporary.path() / "policy";
  make_directory(root);
  IOTOX_CHECK(iotox::sync::prepare_namespace_store(
                  root, static_cast<std::uint32_t>(::geteuid()))
                  .ok());

  auto empty = iotox::sync::load_sync_policy_tree(
      root, static_cast<std::uint32_t>(::geteuid()),
      identity.value().public_key(), sodium.value());
  IOTOX_CHECK(empty.ok());
  auto empty_digest = iotox::sync::sync_policy_tree_digest(
      empty.value(), sodium.value());
  IOTOX_CHECK(empty_digest.ok());

  NamespacePolicy policy = sample_policy();
  policy.root = temporary.path() / "namespace";
  policy.writers = {identity.value().public_key()};
  auto installed = iotox::sync::install_namespace_policy(
      root, policy, static_cast<std::uint32_t>(::geteuid()));
  IOTOX_CHECK(installed.ok());
  auto with_namespace = iotox::sync::load_sync_policy_tree(
      root, static_cast<std::uint32_t>(::geteuid()),
      identity.value().public_key(), sodium.value());
  IOTOX_CHECK(with_namespace.ok());
  auto namespace_digest = iotox::sync::sync_policy_tree_digest(
      with_namespace.value(), sodium.value());
  IOTOX_CHECK(namespace_digest.ok());
  IOTOX_CHECK(namespace_digest.value() != empty_digest.value());

  iotox::sync::SyncAutomationSpec automation;
  automation.namespace_id = policy.id;
  automation.mode = iotox::sync::SyncAutomationMode::disabled;
  iotox::sync::SyncAutomationStore automation_store(root);
  IOTOX_CHECK(automation_store.put(
                  automation, identity.value(), sodium.value())
                  .ok());
  auto complete = iotox::sync::load_sync_policy_tree(
      root, static_cast<std::uint32_t>(::geteuid()),
      identity.value().public_key(), sodium.value());
  IOTOX_CHECK(complete.ok());
  auto complete_digest = iotox::sync::sync_policy_tree_digest(
      complete.value(), sodium.value());
  IOTOX_CHECK(complete_digest.ok());
  IOTOX_CHECK(complete_digest.value() != namespace_digest.value());
  auto repeated = iotox::sync::sync_policy_tree_digest(
      complete.value(), sodium.value());
  IOTOX_CHECK(repeated.ok() &&
              repeated.value() == complete_digest.value());

  auto duplicate = complete.value();
  duplicate.namespaces.push_back(policy);
  IOTOX_CHECK(!iotox::sync::sync_policy_tree_digest(
                   duplicate, sodium.value())
                   .ok());
}

IOTOX_TEST(
    "sync namespace policy rejects ambiguous roots quotas and principals") {
  NamespacePolicy policy = sample_policy();
  policy.root = "/var/lib/iotox/../escape";
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(policy).ok());
  policy = sample_policy();
  policy.quotas.maximum_staging_bytes =
      policy.quotas.maximum_artifact_bytes - 1U;
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(policy).ok());
  policy = sample_policy();
  policy.writers = {principal(2U), principal(1U)};
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(policy).ok());
  policy = sample_policy();
  policy.writers.push_back(principal(2U));
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(policy).ok());
  policy = sample_policy();
  policy.writers.clear();
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(policy).ok());
}

IOTOX_TEST("sync namespace v2 freezes selective paths and metadata policy") {
  NamespacePolicy policy = sample_policy();
  policy.engine = Engine::tree_v2;
  policy.projection.metadata =
      iotox::sync::TreeV2MetadataMode::owner_mode_v2;
  policy.projection.includes = {"docs", "media/current"};
  policy.projection.excludes = {"docs/cache", "docs/private"};
  IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());
  auto encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
  const std::string text(encoded.value().begin(), encoded.value().end());
  IOTOX_CHECK(text.starts_with("iotox-sync-namespace-v2\n"));
  IOTOX_CHECK(text.find("tree-metadata=owner-mode-v2\n") !=
              std::string::npos);
  auto decoded = iotox::sync::decode_namespace_policy(encoded.value());
  IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
  IOTOX_CHECK(decoded.value() == policy);

  IOTOX_CHECK(iotox::sync::tree_v2_path_selected(policy, "docs", true));
  IOTOX_CHECK(iotox::sync::tree_v2_path_selected(policy, "docs/readme", false));
  IOTOX_CHECK(!iotox::sync::tree_v2_path_selected(policy, "docs/cache", true));
  IOTOX_CHECK(!iotox::sync::tree_v2_path_selected(
      policy, "docs/cache/object", false));
  IOTOX_CHECK(iotox::sync::tree_v2_path_selected(policy, "media", true));
  IOTOX_CHECK(!iotox::sync::tree_v2_path_selected(policy, "media", false));
  IOTOX_CHECK(!iotox::sync::tree_v2_path_selected(policy, "other", true));

  NamespacePolicy noncanonical = policy;
  noncanonical.projection.includes = {"media/current", "docs"};
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(noncanonical).ok());
  NamespacePolicy hidden = policy;
  hidden.projection.includes = {"docs/cache/selected"};
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(hidden).ok());
  NamespacePolicy wrong_engine = policy;
  wrong_engine.engine = Engine::treepack_v1;
  IOTOX_CHECK(!iotox::sync::validate_namespace_policy(wrong_engine).ok());
}

IOTOX_TEST("sync namespace managed roots are private deterministic data children") {
  TempDirectory temporary;
  const std::filesystem::path policy_root = temporary.path() / "sync-policy";
  make_directory(policy_root);
  make_directory(policy_root / "namespaces");
  const std::uint32_t owner = static_cast<std::uint32_t>(::geteuid());

  auto expected = iotox::sync::managed_namespace_root(
      policy_root, "field-notes");
  IOTOX_CHECK(expected.ok());
  IOTOX_CHECK(expected.value() ==
              policy_root / "data" / "field-notes");
  auto prepared = iotox::sync::prepare_managed_namespace_root(
      policy_root, "field-notes", owner);
  IOTOX_CHECK_MSG(prepared.ok(), prepared.status().message());
  IOTOX_CHECK(prepared.value() == expected.value());
  auto duplicate = iotox::sync::prepare_managed_namespace_root(
      policy_root, "field-notes", owner);
  IOTOX_CHECK(duplicate.ok() && duplicate.value() == expected.value());

  struct stat metadata {};
  IOTOX_CHECK(::lstat((policy_root / "data").c_str(),
                      &metadata) == 0);
  IOTOX_CHECK(S_ISDIR(metadata.st_mode));
  IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
              static_cast<mode_t>(0700));
  IOTOX_CHECK(::lstat(expected.value().c_str(), &metadata) == 0);
  IOTOX_CHECK(S_ISDIR(metadata.st_mode));
  IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
              static_cast<mode_t>(0700));

  IOTOX_CHECK(!iotox::sync::managed_namespace_root(
                   policy_root, "Invalid").ok());
  IOTOX_CHECK(!iotox::sync::managed_namespace_root(
                   std::filesystem::path{"relative"}, "valid").ok());
}

IOTOX_TEST("sync namespace decoder rejects noncanonical and unknown records") {
  auto encoded = iotox::sync::encode_namespace_policy(sample_policy());
  IOTOX_CHECK(encoded.ok());
  std::vector<std::uint8_t> changed = encoded.value();
  changed.insert(changed.end() - 1,
                 {'u', 'n', 'k', 'n', 'o', 'w', 'n', '=', '1', '\n'});
  IOTOX_CHECK(!iotox::sync::decode_namespace_policy(changed).ok());

  changed = encoded.value();
  const std::string needle = "maximum-peers=8";
  const auto found =
      std::search(changed.begin(), changed.end(), needle.begin(), needle.end());
  IOTOX_CHECK(found != changed.end());
  changed.insert(found + static_cast<std::ptrdiff_t>(needle.size() - 1U), '0');
  IOTOX_CHECK(!iotox::sync::decode_namespace_policy(changed).ok());

  changed = encoded.value();
  changed.pop_back();
  IOTOX_CHECK(!iotox::sync::decode_namespace_policy(changed).ok());
}

IOTOX_TEST("sync namespace store loads only owner-only exact records") {
  TempDirectory temporary;
  const auto namespaces = temporary.path() / "namespaces";
  make_directory(namespaces);
  const NamespacePolicy policy = sample_policy();
  auto encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());
  write_record(namespaces / "field-notes.namespace", encoded.value());

  auto loaded = iotox::sync::load_namespace_store(
      temporary.path(), static_cast<std::uint32_t>(::getuid()));
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == std::vector<NamespacePolicy>{policy});

  NamespaceRegistry registry;
  IOTOX_CHECK(registry.replace(loaded.value()).ok());
  IOTOX_CHECK(registry.snapshot().generation == 1U);
  IOTOX_CHECK(registry.snapshot().enabled_namespaces == 1U);
  auto resolved = registry.resolve("field-notes");
  IOTOX_CHECK(resolved.ok());
  IOTOX_CHECK(resolved.value() == policy);
  IOTOX_CHECK(registry.list() == std::vector<NamespacePolicy>{policy});
  IOTOX_CHECK(!registry.resolve("missing").ok());
}

IOTOX_TEST("sync namespace store securely prepares an empty live root") {
    TempDirectory temporary;
    const std::uint32_t owner = static_cast<std::uint32_t>(::geteuid());
    IOTOX_CHECK(
        iotox::sync::prepare_namespace_store(temporary.path(), owner).ok());
    IOTOX_CHECK(
        iotox::sync::prepare_namespace_store(temporary.path(), owner).ok());
    const auto namespaces = temporary.path() / "namespaces";
    struct stat metadata {};
    IOTOX_CHECK(::lstat(namespaces.c_str(), &metadata) == 0);
    IOTOX_CHECK(S_ISDIR(metadata.st_mode));
    IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
                static_cast<mode_t>(0700));
    auto loaded = iotox::sync::load_namespace_store(temporary.path(), owner);
    IOTOX_CHECK(loaded.ok());
    IOTOX_CHECK(loaded.value().empty());

    TempDirectory unsafe;
    make_directory(unsafe.path() / "namespaces", 0755);
    IOTOX_CHECK(
        !iotox::sync::prepare_namespace_store(unsafe.path(), owner).ok());
}

IOTOX_TEST(
    "sync namespace install is durable no-clobber and exact-retry safe") {
  TempDirectory temporary;
  const auto namespaces = temporary.path() / "namespaces";
  make_directory(namespaces);
  const std::uint32_t owner = static_cast<std::uint32_t>(::geteuid());
  const NamespacePolicy policy = sample_policy();

  auto installed =
      iotox::sync::install_namespace_policy(temporary.path(), policy, owner);
  IOTOX_CHECK(installed.ok());
  IOTOX_CHECK(installed.value().disposition ==
              iotox::sync::NamespaceInstallDisposition::installed);
  auto loaded = iotox::sync::load_namespace_store(temporary.path(), owner);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == std::vector<NamespacePolicy>{policy});
  struct stat metadata {};
  IOTOX_CHECK(
      ::lstat((namespaces / "field-notes.namespace").c_str(), &metadata) == 0);
  IOTOX_CHECK(S_ISREG(metadata.st_mode));
  IOTOX_CHECK(metadata.st_nlink == 1U);
  IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
              static_cast<mode_t>(0600));

  auto duplicate = iotox::sync::install_namespace_policy(
      temporary.path(), policy, owner);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().disposition ==
              iotox::sync::NamespaceInstallDisposition::duplicate);
  NamespacePolicy conflict = policy;
  conflict.activation = ActivationMode::disabled;
  auto refused = iotox::sync::install_namespace_policy(
      temporary.path(), conflict, owner);
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::unavailable);
  loaded = iotox::sync::load_namespace_store(temporary.path(), owner);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == std::vector<NamespacePolicy>{policy});
  IOTOX_CHECK(std::distance(
                  std::filesystem::directory_iterator(namespaces),
                  std::filesystem::directory_iterator{}) == 1);
}

IOTOX_TEST(
    "sync namespace update and removal are atomic bounded policy effects") {
  TempDirectory temporary;
  const auto namespaces = temporary.path() / "namespaces";
  make_directory(namespaces);
  const std::uint32_t owner = static_cast<std::uint32_t>(::geteuid());
  const NamespacePolicy original = sample_policy();
  IOTOX_CHECK(iotox::sync::install_namespace_policy(
                  temporary.path(), original, owner)
                  .ok());

  NamespacePolicy updated = original;
  updated.activation = ActivationMode::disabled;
  updated.writers = {principal(2U)};
  updated.subscribers = {principal(3U), principal(4U)};
  auto changed = iotox::sync::update_namespace_policy(
      temporary.path(), updated, owner);
  IOTOX_CHECK(changed.ok());
  IOTOX_CHECK(changed.value().disposition ==
              iotox::sync::NamespaceUpdateDisposition::updated);
  auto loaded = iotox::sync::load_namespace_store(
      temporary.path(), owner);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == std::vector<NamespacePolicy>{updated});

  auto duplicate = iotox::sync::update_namespace_policy(
      temporary.path(), updated, owner);
  IOTOX_CHECK(duplicate.ok());
  IOTOX_CHECK(duplicate.value().disposition ==
              iotox::sync::NamespaceUpdateDisposition::duplicate);
  NamespacePolicy widened = updated;
  ++widened.quotas.maximum_store_bytes;
  IOTOX_CHECK(!iotox::sync::update_namespace_policy(
                   temporary.path(), widened, owner)
                   .ok());
  NamespacePolicy moved = updated;
  moved.root += "-other";
  IOTOX_CHECK(!iotox::sync::update_namespace_policy(
                   temporary.path(), moved, owner)
                   .ok());

  auto encoded = iotox::sync::encode_namespace_policy(updated);
  IOTOX_CHECK(encoded.ok());
  const auto staged = namespaces / ".field-notes.namespace.update";
  write_record(staged, encoded.value());
  IOTOX_CHECK(iotox::sync::cleanup_namespace_policy_temporaries(
                  temporary.path(), owner)
                  .ok());
  IOTOX_CHECK(!std::filesystem::exists(staged));
  loaded = iotox::sync::load_namespace_store(temporary.path(), owner);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == std::vector<NamespacePolicy>{updated});

  const auto unknown = namespaces / ".unexpected";
  write_record(unknown, encoded.value());
  IOTOX_CHECK(!iotox::sync::cleanup_namespace_policy_temporaries(
                   temporary.path(), owner)
                   .ok());
  IOTOX_CHECK(std::filesystem::exists(unknown));
  IOTOX_CHECK(std::filesystem::remove(unknown));

  const auto malformed = namespaces / ".field-notes.namespace.update";
  write_record(malformed, std::vector<std::uint8_t>{'n', 'o', 't', '\n'});
  IOTOX_CHECK(!iotox::sync::cleanup_namespace_policy_temporaries(
                   temporary.path(), owner)
                   .ok());
  IOTOX_CHECK(std::filesystem::exists(malformed));
  IOTOX_CHECK(std::filesystem::remove(malformed));

  auto removed = iotox::sync::remove_namespace_policy(
      temporary.path(), updated.id, owner);
  IOTOX_CHECK(removed.ok());
  IOTOX_CHECK(removed.value().disposition ==
              iotox::sync::NamespaceRemoveDisposition::removed);
  auto absent = iotox::sync::remove_namespace_policy(
      temporary.path(), updated.id, owner);
  IOTOX_CHECK(absent.ok());
  IOTOX_CHECK(absent.value().disposition ==
              iotox::sync::NamespaceRemoveDisposition::absent);
  auto absent_update = iotox::sync::update_namespace_policy(
      temporary.path(), updated, owner);
  IOTOX_CHECK(!absent_update.ok());
  IOTOX_CHECK(absent_update.status().code() == iotox::ErrorCode::not_found);
  loaded = iotox::sync::load_namespace_store(temporary.path(), owner);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().empty());
}

IOTOX_TEST(
    "sync namespace store refuses aliases permissions and unexpected entries") {
  NamespacePolicy policy = sample_policy();
  auto encoded = iotox::sync::encode_namespace_policy(policy);
  IOTOX_CHECK(encoded.ok());

  {
    TempDirectory temporary;
    const auto namespaces = temporary.path() / "namespaces";
    make_directory(namespaces);
    write_record(namespaces / "different.namespace", encoded.value());
    IOTOX_CHECK(!iotox::sync::load_namespace_store(
                     temporary.path(), static_cast<std::uint32_t>(::getuid()))
                     .ok());
  }
  {
    TempDirectory temporary;
    const auto namespaces = temporary.path() / "namespaces";
    make_directory(namespaces);
    write_record(namespaces / "field-notes.namespace", encoded.value(), 0640);
    IOTOX_CHECK(!iotox::sync::load_namespace_store(
                     temporary.path(), static_cast<std::uint32_t>(::getuid()))
                     .ok());
  }
  {
    TempDirectory temporary;
    make_directory(temporary.path() / "namespaces");
    make_directory(temporary.path() / "surprise");
    IOTOX_CHECK(!iotox::sync::load_namespace_store(
                     temporary.path(), static_cast<std::uint32_t>(::getuid()))
                     .ok());
  }
}

IOTOX_TEST("sync namespace registry replacement is atomic") {
  NamespaceRegistry registry;
  NamespacePolicy policy = sample_policy();
  IOTOX_CHECK(registry.replace({policy}).ok());
  const auto before = registry.snapshot();
  policy.writers.clear();
  IOTOX_CHECK(!registry.replace({policy}).ok());
  IOTOX_CHECK(registry.snapshot() == before);
  IOTOX_CHECK(registry.resolve("field-notes").ok());
  registry.fail_closed();
  IOTOX_CHECK(!registry.resolve("field-notes").ok());
  IOTOX_CHECK(registry.snapshot().generation == before.generation);
  IOTOX_CHECK(registry.snapshot().namespaces == 0U);
}
