#include "iotox/sync_digest.hpp"
#include "iotox/sync_tree.hpp"

#include "test_harness.hpp"

#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::sync::ActivatedRevision;
using iotox::sync::ActivationMode;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncNamespaceTransaction;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-tree-XXXXXX";
    std::vector<char> storage(pattern.begin(), pattern.end());
    storage.push_back('\0');
    char *created = ::mkdtemp(storage.data());
    if (created == nullptr)
      throw std::runtime_error("mkdtemp failed");
    path_ = created;
    secure_directory(path_);
  }
  ~TempDirectory() {
    std::error_code ignored;
    try {
      for (std::filesystem::recursive_directory_iterator iterator(path_), end;
           iterator != end; ++iterator) {
        if (iterator->is_directory(ignored)) {
          static_cast<void>(::chmod(iterator->path().c_str(),
                                    static_cast<mode_t>(0700)));
        }
        ignored.clear();
      }
    } catch (const std::filesystem::filesystem_error &) {
    }
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const noexcept {
    return path_;
  }

  static void secure_directory(const std::filesystem::path &path) {
    if (::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0)
      throw std::runtime_error("chmod directory failed");
  }

private:
  std::filesystem::path path_;
};

NamespacePolicy policy(const std::filesystem::path &root) {
  PrincipalId writer{};
  writer[0U] = 1U;
  NamespacePolicy result;
  result.id = "site-tree";
  result.root = root.lexically_normal().string();
  result.engine = Engine::treepack_v1;
  result.activation = ActivationMode::manual;
  result.writers = {writer};
  result.quotas.maximum_artifact_bytes = 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 64U * 1024U;
  result.quotas.maximum_store_bytes = 4U * 1024U * 1024U;
  result.quotas.maximum_staging_bytes = 1024U * 1024U;
  result.quotas.maximum_objects = 64U;
  return result;
}

void make_directory(const std::filesystem::path &path) {
  std::filesystem::create_directories(path);
  TempDirectory::secure_directory(path);
}

void write_file(const std::filesystem::path &path, std::string_view bytes,
                mode_t mode = 0600) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("fixture write failed");
  output.close();
  if (::chmod(path.c_str(), mode) != 0)
    throw std::runtime_error("fixture chmod failed");
}

void reserve_file(const std::filesystem::path &path) {
  const int descriptor = ::open(
      path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
      0600);
  if (descriptor < 0)
    throw std::runtime_error("reserve fixture failed: " +
                             std::string(std::strerror(errno)));
  if (::close(descriptor) != 0)
    throw std::runtime_error("close fixture failed");
}

void make_tree(const std::filesystem::path &root, bool reverse_order) {
  make_directory(root);
  if (reverse_order) {
    make_directory(root / "data");
    write_file(root / "data" / "notes.txt", "field-notes\n");
    make_directory(root / "empty");
    make_directory(root / "bin");
    write_file(root / "bin" / "probe", "#!\n", 0700);
  } else {
    make_directory(root / "bin");
    write_file(root / "bin" / "probe", "#!\n", 0700);
    make_directory(root / "empty");
    make_directory(root / "data");
    write_file(root / "data" / "notes.txt", "field-notes\n");
  }
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input)
    throw std::runtime_error("fixture read failed");
  return {std::istreambuf_iterator<char>(input),
          std::istreambuf_iterator<char>()};
}

mode_t permissions(const std::filesystem::path &path) {
  struct stat metadata {};
  if (::lstat(path.c_str(), &metadata) != 0)
    throw std::runtime_error("fixture stat failed");
  return metadata.st_mode & static_cast<mode_t>(0777);
}

std::string digest_hex(const Digest &digest) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(digest.size() * 2U);
  for (const std::uint8_t byte : digest) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

} // namespace

IOTOX_TEST("sync treepack is deterministic private and atomically projected") {
  TempDirectory temporary;
  const NamespacePolicy configured = policy(temporary.path() / "namespace");
  const auto first_source = temporary.path() / "first";
  const auto second_source = temporary.path() / "second";
  make_tree(first_source, false);
  make_tree(second_source, true);
  const auto first_artifact = temporary.path() / "first.treepack";
  const auto second_artifact = temporary.path() / "second.treepack";
  reserve_file(first_artifact);
  reserve_file(second_artifact);

  auto first = iotox::sync::build_sync_treepack(
      configured, first_source, first_artifact);
  auto second = iotox::sync::build_sync_treepack(
      configured, second_source, second_artifact);
  IOTOX_CHECK_MSG(first.ok(), first.status().message());
  IOTOX_CHECK_MSG(second.ok(), second.status().message());
  IOTOX_CHECK(first.value() == second.value());
  IOTOX_CHECK(first.value().directories == 3U);
  IOTOX_CHECK(first.value().files == 2U);
  IOTOX_CHECK(first.value().content_bytes == 15U);
  IOTOX_CHECK(read_bytes(first_artifact) == read_bytes(second_artifact));
  IOTOX_CHECK(permissions(first_artifact) == 0600);

  auto artifact_digest = iotox::sync::hash_sync_file_sha256(first_artifact);
  IOTOX_CHECK(artifact_digest.ok());
  Digest record{};
  record[0U] = 7U;
  const ActivatedRevision revision{
      configured.id, 1U, record, artifact_digest.value(),
      first.value().artifact_bytes};
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto activated = iotox::sync::materialize_sync_treepack(
      configured, revision, first_artifact, transaction.value());
  IOTOX_CHECK_MSG(activated.ok(), activated.status().message());
  IOTOX_CHECK(activated.value().materialized);
  IOTOX_CHECK(!activated.value().already_current);
  IOTOX_CHECK(activated.value().tree == first.value());

  const auto activation = std::filesystem::path(configured.root) /
                          "materialized-trees";
  const auto expected = std::filesystem::path("revisions") /
                        ("1-" + digest_hex(record));
  IOTOX_CHECK(std::filesystem::read_symlink(activation / "current") ==
              expected);
  const auto current = activation / "current";
  IOTOX_CHECK(read_bytes(current / "data" / "notes.txt") ==
              read_bytes(first_source / "data" / "notes.txt"));
  IOTOX_CHECK(permissions(current / "data" / "notes.txt") == 0400);
  IOTOX_CHECK(permissions(current / "bin" / "probe") == 0500);
  IOTOX_CHECK(permissions(current / "empty") == 0500);

  const auto abandoned = activation / "revisions" /
      ("." + expected.filename().string() + ".part.999.1");
  make_directory(abandoned);
  write_file(abandoned / "partial", "partial");
  const auto abandoned_pointer = activation / ".current.part.999.1";
  IOTOX_CHECK(
      ::symlink(expected.c_str(), abandoned_pointer.c_str()) == 0);
  auto duplicate = iotox::sync::materialize_sync_treepack(
      configured, revision, first_artifact, transaction.value());
  IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
  IOTOX_CHECK(!duplicate.value().materialized);
  IOTOX_CHECK(duplicate.value().already_current);
  IOTOX_CHECK(duplicate.value().recovered_staging_trees == 1U);
  IOTOX_CHECK(duplicate.value().recovered_pointer_temporaries == 1U);
  IOTOX_CHECK(!std::filesystem::exists(abandoned));
  IOTOX_CHECK(!std::filesystem::exists(abandoned_pointer));

  const auto tampered = current / "data" / "notes.txt";
  IOTOX_CHECK(::chmod(tampered.c_str(), static_cast<mode_t>(0600)) == 0);
  write_file(tampered, "wrong-content\n");
  auto rejected = iotox::sync::materialize_sync_treepack(
      configured, revision, first_artifact, transaction.value());
  IOTOX_CHECK(!rejected.ok());
  IOTOX_CHECK(std::filesystem::read_symlink(activation / "current") ==
              expected);
}

IOTOX_TEST("sync tree activation retains only the atomic current projection") {
  TempDirectory temporary;
  const NamespacePolicy configured = policy(temporary.path() / "namespace");
  const auto source = temporary.path() / "source";
  make_tree(source, false);
  const auto first_artifact = temporary.path() / "first.treepack";
  reserve_file(first_artifact);
  auto first = iotox::sync::build_sync_treepack(
      configured, source, first_artifact);
  IOTOX_CHECK_MSG(first.ok(), first.status().message());
  auto first_digest = iotox::sync::hash_sync_file_sha256(first_artifact);
  IOTOX_CHECK(first_digest.ok());
  Digest first_record{};
  first_record[0U] = 1U;
  const ActivatedRevision first_revision{
      configured.id, 1U, first_record, first_digest.value(),
      first.value().artifact_bytes};
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto activated = iotox::sync::materialize_sync_treepack(
      configured, first_revision, first_artifact, transaction.value());
  IOTOX_CHECK_MSG(activated.ok(), activated.status().message());

  const auto activation = std::filesystem::path(configured.root) /
                          "materialized-trees";
  const auto first_name = "1-" + digest_hex(first_record);
  const auto abandoned = activation / "revisions" /
      ("." + first_name + ".part.777.1");
  make_directory(abandoned);
  write_file(abandoned / "partial", "partial");
  make_directory(activation / "revisions" / "ambiguous");
  auto refused_cleanup = iotox::sync::materialize_sync_treepack(
      configured, first_revision, first_artifact, transaction.value());
  IOTOX_CHECK(!refused_cleanup.ok());
  IOTOX_CHECK(std::filesystem::is_directory(abandoned));
  IOTOX_CHECK(std::filesystem::remove(activation / "revisions" / "ambiguous"));
  auto recovered = iotox::sync::materialize_sync_treepack(
      configured, first_revision, first_artifact, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value().recovered_staging_trees == 1U);

  write_file(source / "data" / "notes.txt", "successor\n");
  const auto second_artifact = temporary.path() / "second.treepack";
  reserve_file(second_artifact);
  auto second = iotox::sync::build_sync_treepack(
      configured, source, second_artifact);
  IOTOX_CHECK_MSG(second.ok(), second.status().message());
  auto second_digest = iotox::sync::hash_sync_file_sha256(second_artifact);
  IOTOX_CHECK(second_digest.ok());
  Digest second_record{};
  second_record[0U] = 2U;
  const ActivatedRevision second_revision{
      configured.id, 2U, second_record, second_digest.value(),
      second.value().artifact_bytes};
  activated = iotox::sync::materialize_sync_treepack(
      configured, second_revision, second_artifact, transaction.value());
  IOTOX_CHECK_MSG(activated.ok(), activated.status().message());
  IOTOX_CHECK(activated.value().materialized);
  IOTOX_CHECK(activated.value().pruned_revision_trees == 1U);

  const auto first_path = activation / "revisions" /
                          ("1-" + digest_hex(first_record));
  const auto second_path = activation / "revisions" /
                           ("2-" + digest_hex(second_record));
  IOTOX_CHECK(!std::filesystem::exists(first_path));
  IOTOX_CHECK(std::filesystem::is_directory(second_path));
  IOTOX_CHECK(read_bytes(activation / "current" / "data" / "notes.txt") ==
              read_bytes(source / "data" / "notes.txt"));
}

IOTOX_TEST("sync tree pointer recovery refuses ambiguity before mutation") {
  TempDirectory temporary;
  const NamespacePolicy configured = policy(temporary.path() / "namespace");
  const auto source = temporary.path() / "source";
  make_tree(source, false);
  const auto artifact = temporary.path() / "tree.treepack";
  reserve_file(artifact);
  auto packed =
      iotox::sync::build_sync_treepack(configured, source, artifact);
  IOTOX_CHECK_MSG(packed.ok(), packed.status().message());
  auto artifact_digest = iotox::sync::hash_sync_file_sha256(artifact);
  IOTOX_CHECK(artifact_digest.ok());
  Digest record{};
  record[0U] = 4U;
  const ActivatedRevision revision{
      configured.id, 1U, record, artifact_digest.value(),
      packed.value().artifact_bytes};
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto activated = iotox::sync::materialize_sync_treepack(
      configured, revision, artifact, transaction.value());
  IOTOX_CHECK_MSG(activated.ok(), activated.status().message());

  const auto activation = std::filesystem::path(configured.root) /
                          "materialized-trees";
  const auto target = std::filesystem::path("revisions") /
                      ("1-" + digest_hex(record));
  const auto abandoned = activation / ".current.part.888.1";
  IOTOX_CHECK(::symlink(target.c_str(), abandoned.c_str()) == 0);
  make_directory(activation / "ambiguous");
  auto refused = iotox::sync::materialize_sync_treepack(
      configured, revision, artifact, transaction.value());
  IOTOX_CHECK(!refused.ok());
  IOTOX_CHECK(std::filesystem::is_symlink(abandoned));

  IOTOX_CHECK(std::filesystem::remove(activation / "ambiguous"));
  auto recovered = iotox::sync::materialize_sync_treepack(
      configured, revision, artifact, transaction.value());
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value().already_current);
  IOTOX_CHECK(recovered.value().recovered_pointer_temporaries == 1U);
  IOTOX_CHECK(!std::filesystem::exists(abandoned));

  NamespacePolicy bounded = configured;
  bounded.quotas.maximum_objects = 2U;
  bounded.quotas.maximum_retained_revisions = 2U;
  std::vector<std::filesystem::path> excess;
  for (std::uint64_t index = 1U; index <= 3U; ++index) {
    const auto path = activation /
                      (".current.part.777." + std::to_string(index));
    IOTOX_CHECK(::symlink(target.c_str(), path.c_str()) == 0);
    excess.push_back(path);
  }
  auto exhausted = iotox::sync::materialize_sync_treepack(
      bounded, revision, artifact, transaction.value());
  IOTOX_CHECK(!exhausted.ok());
  IOTOX_CHECK(exhausted.status().code() ==
              iotox::ErrorCode::resource_exhausted);
  for (const auto &path : excess) {
    IOTOX_CHECK(std::filesystem::is_symlink(path));
    IOTOX_CHECK(std::filesystem::remove(path));
  }
}

IOTOX_TEST("sync treepack rejects unsafe trees and complete artifact overflow") {
  TempDirectory temporary;
  const NamespacePolicy configured = policy(temporary.path() / "namespace");

  const auto linked = temporary.path() / "linked";
  make_directory(linked);
  write_file(linked / "source", "one");
  std::filesystem::create_hard_link(linked / "source", linked / "alias");
  const auto linked_artifact = temporary.path() / "linked.treepack";
  reserve_file(linked_artifact);
  IOTOX_CHECK(!iotox::sync::build_sync_treepack(
                   configured, linked, linked_artifact)
                   .ok());

  const auto symbolic = temporary.path() / "symbolic";
  make_directory(symbolic);
  write_file(symbolic / "source", "one");
  std::filesystem::create_symlink("source", symbolic / "alias");
  const auto symbolic_artifact = temporary.path() / "symbolic.treepack";
  reserve_file(symbolic_artifact);
  IOTOX_CHECK(!iotox::sync::build_sync_treepack(
                   configured, symbolic, symbolic_artifact)
                   .ok());

  const auto writable = temporary.path() / "writable";
  make_directory(writable);
  write_file(writable / "entry", "one", 0620);
  const auto writable_artifact = temporary.path() / "writable.treepack";
  reserve_file(writable_artifact);
  IOTOX_CHECK(!iotox::sync::build_sync_treepack(
                   configured, writable, writable_artifact)
                   .ok());

  auto bounded = configured;
  bounded.quotas.maximum_artifact_bytes = 128U;
  bounded.quotas.maximum_manifest_bytes = 128U;
  bounded.quotas.maximum_staging_bytes = 16U * 1024U;
  bounded.quotas.maximum_store_bytes = 32U * 1024U;
  bounded.quotas.maximum_objects = 2U;
  bounded.quotas.maximum_retained_revisions = 2U;
  const auto oversized = temporary.path() / "oversized";
  make_directory(oversized);
  write_file(oversized / "entry", std::string(512U, 'x'));
  const auto oversized_artifact = temporary.path() / "oversized.treepack";
  reserve_file(oversized_artifact);
  IOTOX_CHECK(!iotox::sync::build_sync_treepack(
                   bounded, oversized, oversized_artifact)
                   .ok());
}
