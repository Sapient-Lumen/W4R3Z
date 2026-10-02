#include "iotox/sync_digest.hpp"
#include "iotox/sync_tree.hpp"

#include <array>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::sync::ActivatedRevision;
using iotox::sync::ActivationMode;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncTreeProjectionPoint;
using iotox::sync::SyncTreeProjectionSeams;

constexpr int kCrashExit = 42;

void thaw_and_remove(const std::filesystem::path &root) {
  std::error_code ignored;
  try {
    for (std::filesystem::recursive_directory_iterator iterator(root), end;
         iterator != end; ++iterator) {
      if (iterator->is_directory(ignored)) {
        static_cast<void>(
            ::chmod(iterator->path().c_str(), static_cast<mode_t>(0700)));
      }
      ignored.clear();
    }
  } catch (const std::filesystem::filesystem_error &) {
  }
  std::filesystem::remove_all(root, ignored);
}

bool secure_directory(const std::filesystem::path &path) {
  std::error_code error;
  std::filesystem::create_directories(path, error);
  return !error &&
         ::chmod(path.c_str(), static_cast<mode_t>(0700)) == 0;
}

bool write_file(const std::filesystem::path &path, std::string_view bytes,
                mode_t mode = 0600) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  output.close();
  return static_cast<bool>(output) && ::chmod(path.c_str(), mode) == 0;
}

bool reserve_file(const std::filesystem::path &path) {
  const int descriptor = ::open(
      path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
      0600);
  if (descriptor < 0)
    return false;
  return ::close(descriptor) == 0;
}

NamespacePolicy policy(const std::filesystem::path &root) {
  PrincipalId writer{};
  writer[0U] = 1U;
  NamespacePolicy result;
  result.id = "crash-tree";
  result.root = root.lexically_normal().string();
  result.engine = Engine::treepack_v1;
  result.activation = ActivationMode::manual;
  result.writers = {writer};
  result.quotas.maximum_artifact_bytes = 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 64U * 1024U;
  result.quotas.maximum_store_bytes = 4U * 1024U * 1024U;
  result.quotas.maximum_staging_bytes = 1024U * 1024U;
  result.quotas.maximum_objects = 64U;
  result.quotas.maximum_retained_revisions = 8U;
  return result;
}

bool make_source(const std::filesystem::path &root, std::string_view value) {
  return secure_directory(root) && secure_directory(root / "data") &&
         write_file(root / "data" / "value.txt", value) &&
         write_file(root / "probe", "#!\n", 0700);
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

bool run_projection(const NamespacePolicy &configured,
                    const ActivatedRevision &revision,
                    const std::filesystem::path &artifact,
                    const SyncTreeProjectionPoint *crash_at) {
  const pid_t child = ::fork();
  if (child < 0)
    return false;
  if (child == 0) {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    if (!transaction.ok())
      ::_exit(2);
    SyncTreeProjectionSeams seams;
    if (crash_at != nullptr) {
      const SyncTreeProjectionPoint selected = *crash_at;
      seams.after_step = [selected](SyncTreeProjectionPoint observed) {
        if (observed == selected)
          ::_exit(kCrashExit);
        return iotox::Status::success();
      };
    }
    const auto projected = iotox::sync::materialize_sync_treepack(
        configured, revision, artifact, transaction.value(), seams);
    ::_exit(projected.ok() ? 0 : 3);
  }

  int status = 0;
  if (::waitpid(child, &status, 0) != child || !WIFEXITED(status))
    return false;
  const int expected = crash_at == nullptr ? 0 : kCrashExit;
  return WEXITSTATUS(status) == expected;
}

std::string read_text(const std::filesystem::path &path) {
  const int descriptor =
      ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0)
    return {};
  std::array<char, 64U> bytes{};
  const ssize_t count = ::read(descriptor, bytes.data(), bytes.size());
  const bool closed = ::close(descriptor) == 0;
  if (count < 0 || !closed)
    return {};
  return std::string(bytes.data(), static_cast<std::size_t>(count));
}

bool pointer_has_successor(const NamespacePolicy &configured,
                           const ActivatedRevision &successor) {
  const auto current = std::filesystem::path(configured.root) /
                       "materialized-trees" / "current";
  std::error_code error;
  const auto target = std::filesystem::read_symlink(current, error);
  const auto expected = std::filesystem::path("revisions") /
                        (std::to_string(successor.generation) + "-" +
                         digest_hex(successor.record));
  return !error && target == expected;
}

bool projection_is_canonical(const NamespacePolicy &configured,
                             const ActivatedRevision &successor) {
  const auto activation = std::filesystem::path(configured.root) /
                          "materialized-trees";
  const auto revisions = activation / "revisions";
  std::error_code error;
  std::size_t activation_entries = 0U;
  for (const auto &entry : std::filesystem::directory_iterator(activation,
                                                               error)) {
    if (error)
      return false;
    const std::string name = entry.path().filename().string();
    if (name != "current" && name != "revisions")
      return false;
    ++activation_entries;
  }
  std::size_t revision_entries = 0U;
  const std::string expected = std::to_string(successor.generation) + "-" +
                               digest_hex(successor.record);
  for (const auto &entry : std::filesystem::directory_iterator(revisions,
                                                               error)) {
    if (error || entry.path().filename() != expected)
      return false;
    ++revision_entries;
  }
  return activation_entries == 2U && revision_entries == 1U &&
         pointer_has_successor(configured, successor) &&
         read_text(activation / "current" / "data" / "value.txt") ==
             "second\n";
}

bool point_commits_pointer(SyncTreeProjectionPoint point) {
  return point == SyncTreeProjectionPoint::pointer_committed ||
         point == SyncTreeProjectionPoint::pointer_synced ||
         point == SyncTreeProjectionPoint::stale_projections_pruned;
}

bool run_case(const std::filesystem::path &temporary,
              SyncTreeProjectionPoint point) {
  const std::string label(
      iotox::sync::sync_tree_projection_point_name(point));
  const auto case_root = temporary / label;
  const auto first_source = case_root / "first-source";
  const auto second_source = case_root / "second-source";
  if (!make_source(first_source, "first\n") ||
      !make_source(second_source, "second\n")) {
    return false;
  }
  const NamespacePolicy configured = policy(case_root / "namespace");
  const auto first_artifact = case_root / "first.treepack";
  const auto second_artifact = case_root / "second.treepack";
  if (!reserve_file(first_artifact) || !reserve_file(second_artifact))
    return false;
  auto first_stats = iotox::sync::build_sync_treepack(
      configured, first_source, first_artifact);
  auto second_stats = iotox::sync::build_sync_treepack(
      configured, second_source, second_artifact);
  auto first_digest = iotox::sync::hash_sync_file_sha256(first_artifact);
  auto second_digest = iotox::sync::hash_sync_file_sha256(second_artifact);
  if (!first_stats.ok() || !second_stats.ok() || !first_digest.ok() ||
      !second_digest.ok()) {
    return false;
  }

  Digest first_record{};
  first_record[0U] = 1U;
  Digest second_record{};
  second_record[0U] = 2U;
  const ActivatedRevision first{
      configured.id, 1U, first_record, first_digest.value(),
      first_stats.value().artifact_bytes};
  const ActivatedRevision second{
      configured.id, 2U, second_record, second_digest.value(),
      second_stats.value().artifact_bytes};
  if (!run_projection(configured, first, first_artifact, nullptr) ||
      !run_projection(configured, second, second_artifact, &point)) {
    return false;
  }

  const auto current = std::filesystem::path(configured.root) /
                       "materialized-trees" / "current";
  const std::string visible = read_text(current / "data" / "value.txt");
  if (visible != (point_commits_pointer(point) ? "second\n" : "first\n"))
    return false;
  return run_projection(configured, second, second_artifact, nullptr) &&
         projection_is_canonical(configured, second);
}

int run() {
  std::string pattern = "/tmp/iotox-sync-tree-process-XXXXXX";
  std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
  mutable_pattern.push_back('\0');
  char *created = ::mkdtemp(mutable_pattern.data());
  if (created == nullptr)
    return 1;
  const std::filesystem::path temporary(created);
  if (::chmod(temporary.c_str(), static_cast<mode_t>(0700)) != 0) {
    thaw_and_remove(temporary);
    return 1;
  }

  constexpr std::array points{
      SyncTreeProjectionPoint::unpacked,
      SyncTreeProjectionPoint::frozen,
      SyncTreeProjectionPoint::revision_committed,
      SyncTreeProjectionPoint::revision_synced,
      SyncTreeProjectionPoint::pointer_prepared,
      SyncTreeProjectionPoint::pointer_committed,
      SyncTreeProjectionPoint::pointer_synced,
      SyncTreeProjectionPoint::stale_projections_pruned,
  };
  bool passed = true;
  for (const SyncTreeProjectionPoint point : points) {
    if (!run_case(temporary, point)) {
      std::cerr << "tree projection crash case failed: "
                << iotox::sync::sync_tree_projection_point_name(point) << '\n';
      passed = false;
      break;
    }
  }
  thaw_and_remove(temporary);
  return passed ? 0 : 1;
}

} // namespace

int main() { return run(); }
