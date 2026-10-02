#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "iotox/sync_namespace.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <limits>
#include <locale>
#include <mutex>
#include <optional>
#include <sstream>
#include <string_view>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::string_view kHeaderV1 = "iotox-sync-namespace-v1";
constexpr std::string_view kHeaderV2 = "iotox-sync-namespace-v2";
constexpr std::size_t kMaximumIdBytes = 64U;
constexpr std::size_t kMaximumPathBytes = 4096U;
constexpr std::uint64_t kMaximumByteQuota = 1ULL << 60U;
constexpr std::uint64_t kMaximumCountQuota = 1ULL << 32U;

class FileDescriptor {
public:
  FileDescriptor() = default;
  explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
  ~FileDescriptor() {
    if (descriptor_ >= 0)
      static_cast<void>(::close(descriptor_));
  }
  FileDescriptor(const FileDescriptor &) = delete;
  FileDescriptor &operator=(const FileDescriptor &) = delete;
  FileDescriptor(FileDescriptor &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  FileDescriptor &operator=(FileDescriptor &&other) noexcept {
    if (this != &other) {
      if (descriptor_ >= 0)
        static_cast<void>(::close(descriptor_));
      descriptor_ = std::exchange(other.descriptor_, -1);
    }
    return *this;
  }
  [[nodiscard]] int get() const noexcept { return descriptor_; }

private:
  int descriptor_{-1};
};

[[nodiscard]] Status system_error(std::string_view operation,
                                  int error_number = errno) {
  return Status{ErrorCode::io_error,
                std::string(operation) + ": " + std::strerror(error_number)};
}

[[nodiscard]] bool valid_id(std::string_view value) noexcept {
  if (value.empty() || value.size() > kMaximumIdBytes)
    return false;
  for (std::size_t index = 0U; index < value.size(); ++index) {
    const unsigned char byte = static_cast<unsigned char>(value[index]);
    const bool alpha = byte >= static_cast<unsigned char>('a') &&
                       byte <= static_cast<unsigned char>('z');
    const bool digit = byte >= static_cast<unsigned char>('0') &&
                       byte <= static_cast<unsigned char>('9');
    const bool punctuation = byte == static_cast<unsigned char>('.') ||
                             byte == static_cast<unsigned char>('_') ||
                             byte == static_cast<unsigned char>('-');
    if (!(alpha || digit || (index != 0U && punctuation)))
      return false;
  }
  return true;
}

[[nodiscard]] bool valid_root(std::string_view value) {
  if (value.empty() || value.size() > kMaximumPathBytes ||
      value.find('\0') != std::string_view::npos || value.front() != '/') {
    return false;
  }
  const std::filesystem::path path{std::string(value)};
  if (path == "/" || !path.is_absolute() ||
      path.lexically_normal().generic_string() != value) {
    return false;
  }
  for (const auto &component : path) {
    const std::string text = component.generic_string();
    if (text.empty() || text == "." || text == "..")
      return false;
  }
  return true;
}

[[nodiscard]] bool path_prefix(std::string_view prefix,
                               std::string_view path) noexcept {
  return path == prefix ||
         (path.size() > prefix.size() && path.starts_with(prefix) &&
          path[prefix.size()] == '/');
}

[[nodiscard]] bool selection_rules_canonical(
    const std::vector<std::string> &values) {
  return values.size() <= kMaximumTreeV2SelectionRules &&
         std::is_sorted(values.begin(), values.end()) &&
         std::adjacent_find(values.begin(), values.end()) == values.end() &&
         std::all_of(values.begin(), values.end(),
                     [](const std::string &value) {
                       return valid_tree_v2_selection_path(value);
                     });
}

[[nodiscard]] bool principal_less(const PrincipalId &left,
                                  const PrincipalId &right) {
  return std::lexicographical_compare(left.begin(), left.end(), right.begin(),
                                      right.end());
}

[[nodiscard]] bool
principals_canonical(const std::vector<PrincipalId> &values) {
  return std::is_sorted(values.begin(), values.end(), principal_less) &&
         std::adjacent_find(values.begin(), values.end()) == values.end();
}

[[nodiscard]] std::string hex_encode(std::string_view value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(value.size() * 2U);
  for (const char character : value) {
    const auto byte = static_cast<unsigned char>(character);
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

[[nodiscard]] std::string principal_hex(const PrincipalId &principal) {
  return hex_encode(std::string_view{
      reinterpret_cast<const char *>(principal.data()), principal.size()});
}

[[nodiscard]] int hex_nibble(char character) {
  if (character >= '0' && character <= '9')
    return character - '0';
  if (character >= 'a' && character <= 'f')
    return 10 + character - 'a';
  return -1;
}

[[nodiscard]] Result<std::string> hex_decode(std::string_view value,
                                             std::size_t maximum,
                                             std::string_view label) {
  if ((value.size() % 2U) != 0U || value.size() / 2U > maximum) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " hexadecimal length is invalid"};
  }
  std::string output;
  output.reserve(value.size() / 2U);
  for (std::size_t index = 0U; index < value.size(); index += 2U) {
    const int high = hex_nibble(value[index]);
    const int low = hex_nibble(value[index + 1U]);
    if (high < 0 || low < 0) {
      return Status{ErrorCode::protocol_error,
                    std::string(label) + " is not lowercase hexadecimal"};
    }
    output.push_back(static_cast<char>((high << 4U) | low));
  }
  return output;
}

[[nodiscard]] Result<PrincipalId> parse_principal(std::string_view value) {
  auto decoded = hex_decode(value, 32U, "sync principal");
  if (!decoded.ok() || decoded.value().size() != 32U) {
    return Status{ErrorCode::protocol_error,
                  "sync principal must be 64 lowercase hex characters"};
  }
  PrincipalId principal{};
  std::copy(decoded.value().begin(), decoded.value().end(), principal.begin());
  return principal;
}

[[nodiscard]] Result<std::uint64_t> parse_u64(std::string_view value,
                                              std::string_view label) {
  if (value.empty() || value.front() == '+' || value.front() == '-') {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not an unsigned integer"};
  }
  std::uint64_t parsed = 0U;
  const auto result =
      std::from_chars(value.data(), value.data() + value.size(), parsed, 10);
  if (result.ec != std::errc{} || result.ptr != value.data() + value.size()) {
    return Status{ErrorCode::protocol_error,
                  std::string(label) + " is not an unsigned integer"};
  }
  return parsed;
}

[[nodiscard]] Result<std::vector<std::string_view>>
split_record(std::span<const std::uint8_t> bytes) {
  if (bytes.empty() || bytes.size() > kMaximumNamespaceRecordBytes ||
      bytes.back() != static_cast<std::uint8_t>('\n')) {
    return Status{ErrorCode::protocol_error,
                  "sync namespace record size or final LF is invalid"};
  }
  const std::string_view text{reinterpret_cast<const char *>(bytes.data()),
                              bytes.size()};
  if (text.find('\0') != std::string_view::npos ||
      text.find('\r') != std::string_view::npos || text.ends_with("\n\n")) {
    return Status{
        ErrorCode::protocol_error,
        "sync namespace record contains a forbidden byte or blank line"};
  }
  std::vector<std::string_view> lines;
  std::size_t offset = 0U;
  while (offset < text.size()) {
    const std::size_t end = text.find('\n', offset);
    if (end == std::string_view::npos)
      break;
    lines.push_back(text.substr(offset, end - offset));
    offset = end + 1U;
  }
  return lines;
}

[[nodiscard]] Result<std::string_view>
field(const std::vector<std::string_view> &lines, std::size_t &index,
      std::string_view key) {
  if (index >= lines.size() || !lines[index].starts_with(key)) {
    return Status{ErrorCode::protocol_error,
                  "sync namespace field order or name is invalid"};
  }
  return lines[index++].substr(key.size());
}

[[nodiscard]] Result<FileDescriptor>
open_absolute_directory(const std::filesystem::path &path) {
  if (path.empty() || !path.is_absolute() || path.lexically_normal() != path) {
    return Status{ErrorCode::invalid_argument,
                  "sync policy root must be a normalized absolute path"};
  }
  FileDescriptor current(
      ::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (current.get() < 0)
    return system_error("open filesystem root");
  if (path == "/")
    return current;
  for (const auto &component : path.relative_path()) {
    const std::string name = component.string();
    if (name.empty() || name == "." || name == ".." ||
        name.find('/') != std::string::npos ||
        name.find('\0') != std::string::npos) {
      return Status{ErrorCode::invalid_argument,
                    "sync policy root has an invalid path component"};
    }
    FileDescriptor next(
        ::openat(current.get(), name.c_str(),
                 O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (next.get() < 0)
      return system_error("open sync policy path component");
    current = std::move(next);
  }
  return current;
}

[[nodiscard]] Status validate_directory(int descriptor,
                                        std::uint32_t expected_uid,
                                        std::string_view label) {
  struct stat metadata{};
  if (::fstat(descriptor, &metadata) != 0)
    return system_error("fstat sync policy directory");
  if (!S_ISDIR(metadata.st_mode) ||
      metadata.st_uid != static_cast<uid_t>(expected_uid) ||
      (metadata.st_mode & static_cast<mode_t>(0077)) != 0 ||
      (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0) {
    return Status{ErrorCode::io_error,
                  std::string(label) + " is not an owner-only directory"};
  }
  return Status::success();
}

[[nodiscard]] Result<std::vector<std::string>>
list_directory(int descriptor, std::size_t maximum) {
  const int duplicate = ::fcntl(descriptor, F_DUPFD_CLOEXEC, 3);
  if (duplicate < 0)
    return system_error("duplicate sync namespace directory");
  DIR *directory = ::fdopendir(duplicate);
  if (directory == nullptr) {
    const int saved = errno;
    static_cast<void>(::close(duplicate));
    return system_error("fdopendir sync namespace directory", saved);
  }
  std::vector<std::string> names;
  errno = 0;
  while (dirent *entry = ::readdir(directory)) {
    const std::string_view name(entry->d_name);
    if (name == "." || name == "..")
      continue;
    if (name.empty() || name.front() == '.' || names.size() >= maximum) {
      static_cast<void>(::closedir(directory));
      return Status{
          names.size() >= maximum ? ErrorCode::resource_exhausted
                                  : ErrorCode::io_error,
          "sync namespace directory has an invalid entry count or name"};
    }
    names.emplace_back(name);
    errno = 0;
  }
  const int read_error = errno;
  if (::closedir(directory) != 0 && read_error == 0) {
    return system_error("close sync namespace directory");
  }
  if (read_error != 0)
    return system_error("read sync namespace directory", read_error);
  std::sort(names.begin(), names.end());
  return names;
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
read_record(int directory, const std::string &name,
            std::uint32_t expected_uid) {
  FileDescriptor file(::openat(directory, name.c_str(),
                               O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
  if (file.get() < 0)
    return system_error("open sync namespace record");
  struct stat before{};
  if (::fstat(file.get(), &before) != 0)
    return system_error("fstat sync namespace record");
  if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
      before.st_uid != static_cast<uid_t>(expected_uid) ||
      (before.st_mode & static_cast<mode_t>(0077)) != 0 ||
      (before.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
          0) {
    return Status{
        ErrorCode::io_error,
        "sync namespace record is not a single-link owner-only regular file"};
  }
  if (before.st_size < 0 || static_cast<std::uint64_t>(before.st_size) >
                                kMaximumNamespaceRecordBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync namespace record exceeds its byte bound"};
  }
  std::vector<std::uint8_t> bytes;
  bytes.reserve(static_cast<std::size_t>(before.st_size));
  std::array<std::uint8_t, 4096U> buffer{};
  while (true) {
    const ssize_t count = ::read(file.get(), buffer.data(), buffer.size());
    if (count > 0) {
      const std::size_t amount = static_cast<std::size_t>(count);
      if (bytes.size() > kMaximumNamespaceRecordBytes - amount) {
        return Status{ErrorCode::resource_exhausted,
                      "sync namespace record grew beyond its byte bound"};
      }
      bytes.insert(bytes.end(), buffer.begin(),
                   buffer.begin() + static_cast<std::ptrdiff_t>(amount));
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    if (count < 0)
      return system_error("read sync namespace record");
    break;
  }
  struct stat after{};
  if (::fstat(file.get(), &after) != 0)
    return system_error("refstat sync namespace record");
  if (before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
      before.st_size != after.st_size ||
      before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
      before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
      before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
      before.st_ctim.tv_nsec != after.st_ctim.tv_nsec ||
      bytes.size() != static_cast<std::size_t>(after.st_size)) {
    return Status{ErrorCode::io_error,
                  "sync namespace record changed while it was read"};
  }
  return bytes;
}

[[nodiscard]] std::string update_temporary_name(
    std::string_view namespace_id) {
  return "." + std::string(namespace_id) + ".namespace.update";
}

[[nodiscard]] std::optional<std::string_view>
update_temporary_namespace(std::string_view name) {
  constexpr std::string_view suffix = ".namespace.update";
  if (name.size() <= 1U + suffix.size() || name.front() != '.' ||
      !name.ends_with(suffix)) {
    return std::nullopt;
  }
  const std::string_view namespace_id =
      name.substr(1U, name.size() - 1U - suffix.size());
  if (!valid_id(namespace_id)) return std::nullopt;
  return namespace_id;
}

[[nodiscard]] Status cleanup_update_temporaries(
    int namespaces_fd, std::uint32_t expected_owner_uid) {
  const int duplicate = ::fcntl(namespaces_fd, F_DUPFD_CLOEXEC, 3);
  if (duplicate < 0)
    return system_error("duplicate sync namespace directory");
  DIR *directory = ::fdopendir(duplicate);
  if (directory == nullptr) {
    const int saved = errno;
    static_cast<void>(::close(duplicate));
    return system_error("fdopendir sync namespace directory", saved);
  }
  std::vector<std::string> temporaries;
  errno = 0;
  while (dirent *entry = ::readdir(directory)) {
    const std::string_view name(entry->d_name);
    if (name == "." || name == "..") continue;
    if (name.front() != '.') {
      errno = 0;
      continue;
    }
    auto namespace_id = update_temporary_namespace(name);
    if (!namespace_id) {
      static_cast<void>(::closedir(directory));
      return Status{ErrorCode::io_error,
                    "sync namespace directory contains an unknown private entry"};
    }
    if (temporaries.size() >= kMaximumNamespaces) {
      static_cast<void>(::closedir(directory));
      return Status{ErrorCode::resource_exhausted,
                    "sync namespace update temporary bound is exhausted"};
    }
    temporaries.emplace_back(name);
    errno = 0;
  }
  const int read_error = errno;
  if (::closedir(directory) != 0 && read_error == 0) {
    return system_error("close sync namespace directory");
  }
  if (read_error != 0)
    return system_error("read sync namespace directory", read_error);

  for (const std::string &name : temporaries) {
    auto namespace_id = update_temporary_namespace(name);
    if (!namespace_id) {
      return Status{ErrorCode::internal_error,
                    "validated sync update temporary changed identity"};
    }
    auto bytes = read_record(namespaces_fd, name, expected_owner_uid);
    if (!bytes.ok()) return bytes.status();
    auto policy = decode_namespace_policy(bytes.value());
    if (!policy.ok()) return policy.status();
    if (policy.value().id != *namespace_id) {
      return Status{ErrorCode::protocol_error,
                    "sync update temporary and record id differ"};
    }
  }
  for (const std::string &name : temporaries) {
    if (::unlinkat(namespaces_fd, name.c_str(), 0) != 0) {
      return system_error("remove stale sync namespace update temporary");
    }
  }
  if (!temporaries.empty() && ::fsync(namespaces_fd) != 0) {
    return system_error("fsync cleaned sync namespace directory");
  }
  return Status::success();
}

[[nodiscard]] Result<FileDescriptor> write_policy_temporary(
    int namespaces_fd, std::span<const std::uint8_t> encoded) {
  FileDescriptor temporary(
      ::openat(namespaces_fd, ".", O_WRONLY | O_CLOEXEC | O_TMPFILE,
               static_cast<mode_t>(0600)));
  if (temporary.get() < 0) {
    return system_error("create unnamed synchronization namespace record");
  }
  if (::fchmod(temporary.get(), static_cast<mode_t>(0600)) != 0) {
    return system_error("set synchronization namespace record permissions");
  }
  std::size_t offset = 0U;
  while (offset < encoded.size()) {
    const ssize_t count = ::write(temporary.get(), encoded.data() + offset,
                                  encoded.size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR) continue;
    return system_error("write synchronization namespace record");
  }
  if (::fsync(temporary.get()) != 0)
    return system_error("fsync synchronization namespace record");
  return temporary;
}

} // namespace

bool valid_namespace_id(std::string_view value) noexcept {
  return valid_id(value);
}

std::string_view engine_name(Engine engine) noexcept {
  switch (engine) {
  case Engine::range_v1:
    return "range-v1";
  case Engine::content_v2:
    return "content-v2";
  case Engine::treepack_v1:
    return "treepack-v1";
  case Engine::tree_v2:
      return "tree-v2";
  }
  return "unknown";
}

std::string_view
tree_v2_metadata_mode_name(TreeV2MetadataMode mode) noexcept {
  switch (mode) {
  case TreeV2MetadataMode::executable_v1:
    return "executable-v1";
  case TreeV2MetadataMode::owner_mode_v2:
    return "owner-mode-v2";
  }
  return "unknown";
}

bool valid_tree_v2_selection_path(std::string_view path) noexcept {
  if (path.empty() || path.size() > 4096U || path.front() == '/' ||
      path.back() == '/') {
    return false;
  }
  std::size_t offset = 0U;
  bool first = true;
  while (offset < path.size()) {
    const std::size_t end = path.find('/', offset);
    const std::size_t count = end == std::string_view::npos
                                  ? path.size() - offset
                                  : end - offset;
    if (count == 0U) return false;
    const std::string_view component = path.substr(offset, count);
    if (component == "." || component == ".." ||
        (first && component == ".iotox-conflicts")) {
      return false;
    }
    for (const char raw : component) {
      const auto byte = static_cast<unsigned char>(raw);
      if (byte == 0U || byte == '\r' || byte == '\n' || byte == 0x7fU)
        return false;
    }
    first = false;
    if (end == std::string_view::npos) break;
    offset = end + 1U;
  }
  return true;
}

bool tree_v2_path_selected(const NamespacePolicy &policy,
                           std::string_view path, bool directory) noexcept {
  if (!valid_tree_v2_selection_path(path)) return false;
  for (const std::string &excluded : policy.projection.excludes) {
    if (path_prefix(excluded, path)) return false;
  }
  if (policy.projection.includes.empty()) return true;
  for (const std::string &included : policy.projection.includes) {
    if (path_prefix(included, path) ||
        (directory && path_prefix(path, included))) {
      return true;
    }
  }
  return false;
}

Status prepare_namespace_store(const std::filesystem::path &root,
                               std::uint32_t expected_owner_uid) {
    auto opened = open_absolute_directory(root);
    if (!opened.ok()) return opened.status();
    FileDescriptor root_fd = std::move(opened.value());
    Status secure = validate_directory(root_fd.get(), expected_owner_uid,
                                       "sync policy root");
    if (!secure.ok()) return secure;

    bool created = false;
    if (::mkdirat(root_fd.get(), "namespaces", static_cast<mode_t>(0700)) ==
        0) {
        created = true;
    } else if (errno != EEXIST) {
        return system_error("create sync namespace directory");
    }
    FileDescriptor namespaces_fd(
        ::openat(root_fd.get(), "namespaces",
                 O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (namespaces_fd.get() < 0)
        return system_error("open sync namespace directory");
    if (created &&
        ::fchmod(namespaces_fd.get(), static_cast<mode_t>(0700)) != 0) {
        return system_error("set sync namespace directory permissions");
    }
    secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                                "sync namespace directory");
    if (!secure.ok()) return secure;
    if (created && ::fsync(namespaces_fd.get()) != 0)
        return system_error("fsync new sync namespace directory");
    if (created && ::fsync(root_fd.get()) != 0)
        return system_error("fsync sync policy root");
    return Status::success();
}

Result<std::filesystem::path> managed_namespace_root(
    const std::filesystem::path &policy_store_root,
    std::string_view namespace_id) {
  if (!valid_id(namespace_id) || policy_store_root.empty() ||
      !policy_store_root.is_absolute() ||
      policy_store_root.lexically_normal() != policy_store_root ||
      policy_store_root == policy_store_root.root_path()) {
    return Status{ErrorCode::invalid_argument,
                  "managed sync namespace policy root or id is invalid"};
  }
  const std::filesystem::path result =
      (policy_store_root / "data" / std::string(namespace_id))
          .lexically_normal();
  if (!valid_root(result.generic_string())) {
    return Status{ErrorCode::invalid_argument,
                  "managed sync namespace root exceeds the path contract"};
  }
  return result;
}

Result<std::filesystem::path> prepare_managed_namespace_root(
    const std::filesystem::path &policy_store_root,
    std::string_view namespace_id, std::uint32_t expected_owner_uid) {
  auto target = managed_namespace_root(policy_store_root, namespace_id);
  if (!target.ok())
    return target.status();
  auto opened_policy = open_absolute_directory(policy_store_root);
  if (!opened_policy.ok())
    return opened_policy.status();
  FileDescriptor policy = std::move(opened_policy).value();
  Status secure = validate_directory(policy.get(), expected_owner_uid,
                                     "sync policy root");
  if (!secure.ok())
    return secure;

  bool data_created = false;
  if (::mkdirat(policy.get(), "data",
                static_cast<mode_t>(0700)) == 0) {
    data_created = true;
  } else if (errno != EEXIST) {
    return system_error("create managed sync data root");
  }
  FileDescriptor data(
      ::openat(policy.get(), "data",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (data.get() < 0)
    return system_error("open managed sync data root");
  secure = validate_directory(data.get(), expected_owner_uid,
                              "managed sync data root");
  if (!secure.ok())
    return secure;

  const std::string namespace_name(namespace_id);
  bool namespace_created = false;
  if (::mkdirat(data.get(), namespace_name.c_str(),
                static_cast<mode_t>(0700)) == 0) {
    namespace_created = true;
  } else if (errno != EEXIST) {
    return system_error("create managed sync namespace root");
  }
  FileDescriptor namespace_directory(
      ::openat(data.get(), namespace_name.c_str(),
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespace_directory.get() < 0)
    return system_error("open managed sync namespace root");
  secure = validate_directory(namespace_directory.get(), expected_owner_uid,
                              "managed sync namespace root");
  if (!secure.ok())
    return secure;
  if (namespace_created && ::fsync(data.get()) != 0)
    return system_error("fsync managed sync data root");
  if (data_created && ::fsync(policy.get()) != 0)
    return system_error("fsync sync policy root");
  return target.value();
}

Status validate_namespace_policy(const NamespacePolicy &policy) {
  if (!valid_id(policy.id)) {
    return Status{ErrorCode::invalid_argument, "sync namespace id is invalid"};
  }
  if (!valid_root(policy.root)) {
    return Status{
        ErrorCode::invalid_argument,
        "sync namespace root must be a normalized absolute non-root path"};
  }
  if (policy.engine != Engine::range_v1 &&
      policy.engine != Engine::content_v2 &&
      policy.engine != Engine::treepack_v1 &&
      policy.engine != Engine::tree_v2) {
      return Status{ErrorCode::invalid_argument,
                    "sync namespace engine is invalid"};
  }
  if (policy.activation != ActivationMode::disabled &&
      policy.activation != ActivationMode::manual) {
    return Status{ErrorCode::invalid_argument,
                  "sync namespace activation is invalid"};
  }
  const Quotas &q = policy.quotas;
  const std::array byte_quotas{q.maximum_artifact_bytes,
                               q.maximum_manifest_bytes, q.maximum_store_bytes,
                               q.maximum_staging_bytes};
  if (std::any_of(byte_quotas.begin(), byte_quotas.end(),
                  [](std::uint64_t value) {
                    return value == 0U || value > kMaximumByteQuota;
                  }) ||
      q.maximum_artifact_bytes > q.maximum_staging_bytes ||
      q.maximum_manifest_bytes > q.maximum_staging_bytes ||
      q.maximum_staging_bytes > q.maximum_store_bytes) {
    return Status{
        ErrorCode::invalid_argument,
        "sync namespace byte quotas are zero, excessive, or unordered"};
  }
  const std::array count_quotas{q.maximum_objects, q.maximum_retained_revisions,
                                q.maximum_peers, q.maximum_lanes,
                                q.maximum_outstanding_requests};
  if (std::any_of(count_quotas.begin(), count_quotas.end(),
                  [](std::uint64_t value) {
                    return value == 0U || value > kMaximumCountQuota;
                  }) ||
      q.maximum_retained_revisions > q.maximum_objects ||
      q.maximum_lanes > q.maximum_outstanding_requests) {
    return Status{
        ErrorCode::invalid_argument,
        "sync namespace count quotas are zero, excessive, or unordered"};
  }
  if (policy.writers.empty() ||
      policy.writers.size() > kMaximumNamespacePrincipals ||
      policy.subscribers.size() > kMaximumNamespacePrincipals ||
      !principals_canonical(policy.writers) ||
      !principals_canonical(policy.subscribers)) {
    return Status{ErrorCode::invalid_argument,
                  "sync namespace principals are empty, excessive, unsorted, "
                  "or duplicated"};
  }
  if ((policy.projection.metadata != TreeV2MetadataMode::executable_v1 &&
       policy.projection.metadata != TreeV2MetadataMode::owner_mode_v2) ||
      !selection_rules_canonical(policy.projection.includes) ||
      !selection_rules_canonical(policy.projection.excludes) ||
      (policy.engine != Engine::tree_v2 &&
       policy.projection != TreeV2ProjectionPolicy{})) {
    return Status{ErrorCode::invalid_argument,
                  "sync namespace tree-v2 projection policy is invalid"};
  }
  for (const std::string &included : policy.projection.includes) {
    if (std::any_of(policy.projection.excludes.begin(),
                    policy.projection.excludes.end(),
                    [&included](const std::string &excluded) {
                      return path_prefix(excluded, included);
                    })) {
      return Status{ErrorCode::invalid_argument,
                    "sync namespace include is hidden by an exclude"};
    }
  }
  return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_namespace_policy(const NamespacePolicy &policy) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  std::ostringstream output;
  output.imbue(std::locale::classic());
  const bool version_two = policy.projection != TreeV2ProjectionPolicy{};
  output << (version_two ? kHeaderV2 : kHeaderV1) << '\n'
         << "id=" << policy.id << '\n'
         << "root-hex=" << hex_encode(policy.root) << '\n'
         << "engine=" << engine_name(policy.engine) << '\n'
         << "activation="
         << (policy.activation == ActivationMode::disabled ? "disabled"
                                                           : "manual")
         << '\n';
  if (version_two) {
    output << "tree-metadata="
           << tree_v2_metadata_mode_name(policy.projection.metadata) << '\n';
    for (const std::string &include : policy.projection.includes)
      output << "include-hex=" << hex_encode(include) << '\n';
    for (const std::string &exclude : policy.projection.excludes)
      output << "exclude-hex=" << hex_encode(exclude) << '\n';
  }
  output << "maximum-artifact-bytes=" << policy.quotas.maximum_artifact_bytes
         << '\n'
         << "maximum-manifest-bytes=" << policy.quotas.maximum_manifest_bytes
         << '\n'
         << "maximum-store-bytes=" << policy.quotas.maximum_store_bytes << '\n'
         << "maximum-staging-bytes=" << policy.quotas.maximum_staging_bytes
         << '\n'
         << "maximum-objects=" << policy.quotas.maximum_objects << '\n'
         << "maximum-retained-revisions="
         << policy.quotas.maximum_retained_revisions << '\n'
         << "maximum-peers=" << policy.quotas.maximum_peers << '\n'
         << "maximum-lanes=" << policy.quotas.maximum_lanes << '\n'
         << "maximum-outstanding-requests="
         << policy.quotas.maximum_outstanding_requests << '\n';
  for (const PrincipalId &writer : policy.writers) {
    output << "writer=" << principal_hex(writer) << '\n';
  }
  for (const PrincipalId &subscriber : policy.subscribers) {
    output << "subscriber=" << principal_hex(subscriber) << '\n';
  }
  const std::string text = output.str();
  if (text.size() > kMaximumNamespaceRecordBytes) {
    return Status{ErrorCode::resource_exhausted,
                  "encoded sync namespace exceeds its byte bound"};
  }
  return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<NamespacePolicy>
decode_namespace_policy(std::span<const std::uint8_t> bytes) {
  auto split = split_record(bytes);
  if (!split.ok())
    return split.status();
  const auto &lines = split.value();
  if (lines.empty() ||
      (lines.front() != kHeaderV1 && lines.front() != kHeaderV2)) {
    return Status{ErrorCode::protocol_error,
                  "sync namespace header is invalid"};
  }
  const bool version_two = lines.front() == kHeaderV2;
  std::size_t index = 1U;
  NamespacePolicy policy;
  auto id = field(lines, index, "id=");
  if (!id.ok())
    return id.status();
  policy.id = std::string(id.value());
  auto root_text = field(lines, index, "root-hex=");
  if (!root_text.ok())
    return root_text.status();
  auto root =
      hex_decode(root_text.value(), kMaximumPathBytes, "sync namespace root");
  if (!root.ok())
    return root.status();
  policy.root = std::move(root.value());
  auto engine = field(lines, index, "engine=");
  if (!engine.ok())
    return engine.status();
  if (engine.value() == "range-v1")
    policy.engine = Engine::range_v1;
  else if (engine.value() == "content-v2")
    policy.engine = Engine::content_v2;
  else if (engine.value() == "treepack-v1")
    policy.engine = Engine::treepack_v1;
  else if (engine.value() == "tree-v2") policy.engine = Engine::tree_v2;
  else
    return Status{ErrorCode::protocol_error,
                  "sync namespace engine is invalid"};
  auto activation = field(lines, index, "activation=");
  if (!activation.ok())
    return activation.status();
  if (activation.value() == "disabled")
    policy.activation = ActivationMode::disabled;
  else if (activation.value() == "manual")
    policy.activation = ActivationMode::manual;
  else
    return Status{ErrorCode::protocol_error,
                  "sync namespace activation is invalid"};
  if (version_two) {
    auto metadata = field(lines, index, "tree-metadata=");
    if (!metadata.ok()) return metadata.status();
    if (metadata.value() == "executable-v1")
      policy.projection.metadata = TreeV2MetadataMode::executable_v1;
    else if (metadata.value() == "owner-mode-v2")
      policy.projection.metadata = TreeV2MetadataMode::owner_mode_v2;
    else
      return Status{ErrorCode::protocol_error,
                    "sync namespace tree metadata mode is invalid"};
    while (index < lines.size() && lines[index].starts_with("include-hex=")) {
      auto encoded = field(lines, index, "include-hex=");
      if (!encoded.ok()) return encoded.status();
      auto decoded = hex_decode(encoded.value(), 4096U,
                                "sync namespace include path");
      if (!decoded.ok()) return decoded.status();
      policy.projection.includes.push_back(std::move(decoded.value()));
      if (policy.projection.includes.size() >
          kMaximumTreeV2SelectionRules) {
        return Status{ErrorCode::resource_exhausted,
                      "too many sync namespace include rules"};
      }
    }
    while (index < lines.size() && lines[index].starts_with("exclude-hex=")) {
      auto encoded = field(lines, index, "exclude-hex=");
      if (!encoded.ok()) return encoded.status();
      auto decoded = hex_decode(encoded.value(), 4096U,
                                "sync namespace exclude path");
      if (!decoded.ok()) return decoded.status();
      policy.projection.excludes.push_back(std::move(decoded.value()));
      if (policy.projection.excludes.size() >
          kMaximumTreeV2SelectionRules) {
        return Status{ErrorCode::resource_exhausted,
                      "too many sync namespace exclude rules"};
      }
    }
  }
  const auto quota = [&](std::string_view key,
                         std::uint64_t &destination) -> Status {
    auto value = field(lines, index, key);
    if (!value.ok())
      return value.status();
    auto parsed = parse_u64(value.value(), key);
    if (!parsed.ok())
      return parsed.status();
    destination = parsed.value();
    return Status::success();
  };
  for (const auto &[key, destination] :
       std::array{std::pair{"maximum-artifact-bytes=",
                            &policy.quotas.maximum_artifact_bytes},
                  std::pair{"maximum-manifest-bytes=",
                            &policy.quotas.maximum_manifest_bytes},
                  std::pair{"maximum-store-bytes=",
                            &policy.quotas.maximum_store_bytes},
                  std::pair{"maximum-staging-bytes=",
                            &policy.quotas.maximum_staging_bytes},
                  std::pair{"maximum-objects=", &policy.quotas.maximum_objects},
                  std::pair{"maximum-retained-revisions=",
                            &policy.quotas.maximum_retained_revisions},
                  std::pair{"maximum-peers=", &policy.quotas.maximum_peers},
                  std::pair{"maximum-lanes=", &policy.quotas.maximum_lanes},
                  std::pair{"maximum-outstanding-requests=",
                            &policy.quotas.maximum_outstanding_requests}}) {
    const Status parsed = quota(key, *destination);
    if (!parsed.ok())
      return parsed;
  }
  while (index < lines.size() && lines[index].starts_with("writer=")) {
    auto value = field(lines, index, "writer=");
    if (!value.ok())
      return value.status();
    auto principal = parse_principal(value.value());
    if (!principal.ok())
      return principal.status();
    policy.writers.push_back(principal.value());
    if (policy.writers.size() > kMaximumNamespacePrincipals) {
      return Status{ErrorCode::resource_exhausted,
                    "too many sync namespace writers"};
    }
  }
  while (index < lines.size() && lines[index].starts_with("subscriber=")) {
    auto value = field(lines, index, "subscriber=");
    if (!value.ok())
      return value.status();
    auto principal = parse_principal(value.value());
    if (!principal.ok())
      return principal.status();
    policy.subscribers.push_back(principal.value());
    if (policy.subscribers.size() > kMaximumNamespacePrincipals) {
      return Status{ErrorCode::resource_exhausted,
                    "too many sync namespace subscribers"};
    }
  }
  if (index != lines.size()) {
    return Status{ErrorCode::protocol_error,
                  "sync namespace has trailing or unknown fields"};
  }
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  auto canonical = encode_namespace_policy(policy);
  if (!canonical.ok() || canonical.value().size() != bytes.size() ||
      !std::equal(canonical.value().begin(), canonical.value().end(),
                  bytes.begin())) {
    return Status{ErrorCode::protocol_error,
                  "sync namespace record is not canonical"};
  }
  return policy;
}

Result<std::vector<NamespacePolicy>>
load_namespace_store(const std::filesystem::path &root,
                     std::uint32_t expected_owner_uid) {
  auto opened = open_absolute_directory(root);
  if (!opened.ok())
    return opened.status();
  FileDescriptor root_fd = std::move(opened.value());
  Status secure =
      validate_directory(root_fd.get(), expected_owner_uid, "sync policy root");
  if (!secure.ok())
    return secure;
  FileDescriptor namespaces_fd(
      ::openat(root_fd.get(), "namespaces",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespaces_fd.get() < 0)
    return system_error("open sync namespace directory");
  secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                              "sync namespace directory");
  if (!secure.ok())
    return secure;
  auto root_entries = list_directory(root_fd.get(), 3U);
  if (!root_entries.ok())
    return root_entries.status();
  const std::vector<std::string> namespaces_only{"namespaces"};
  const std::vector<std::string> with_automation{"automation", "namespaces"};
  const std::vector<std::string> with_data{"data", "namespaces"};
  const std::vector<std::string> with_automation_and_data{
      "automation", "data", "namespaces"};
  if (root_entries.value() != namespaces_only &&
      root_entries.value() != with_automation &&
      root_entries.value() != with_data &&
      root_entries.value() != with_automation_and_data) {
    return Status{ErrorCode::io_error,
                  "sync policy root contains an unexpected entry"};
  }
  if (root_entries.value() == with_automation ||
      root_entries.value() == with_automation_and_data) {
    FileDescriptor automation_fd(
        ::openat(root_fd.get(), "automation",
                 O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (automation_fd.get() < 0)
      return system_error("open sync automation directory");
    secure = validate_directory(automation_fd.get(), expected_owner_uid,
                                "sync automation directory");
    if (!secure.ok())
      return secure;
  }
  if (root_entries.value() == with_data ||
      root_entries.value() == with_automation_and_data) {
    FileDescriptor data_fd(
        ::openat(root_fd.get(), "data",
                 O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (data_fd.get() < 0)
      return system_error("open managed sync data directory");
    secure = validate_directory(data_fd.get(), expected_owner_uid,
                                "managed sync data directory");
    if (!secure.ok())
      return secure;
  }
  auto names = list_directory(namespaces_fd.get(), kMaximumNamespaces + 1U);
  if (!names.ok())
    return names.status();
  if (names.value().size() > kMaximumNamespaces) {
    return Status{ErrorCode::resource_exhausted,
                  "sync namespace store exceeds its entry bound"};
  }
  constexpr std::string_view suffix = ".namespace";
  std::vector<NamespacePolicy> policies;
  policies.reserve(names.value().size());
  for (const std::string &name : names.value()) {
    if (!std::string_view(name).ends_with(suffix)) {
      return Status{ErrorCode::io_error,
                    "sync namespace directory contains an unexpected filename"};
    }
    const std::string_view stem{name.data(), name.size() - suffix.size()};
    if (!valid_id(stem)) {
      return Status{ErrorCode::io_error,
                    "sync namespace filename has an invalid id"};
    }
    auto bytes = read_record(namespaces_fd.get(), name, expected_owner_uid);
    if (!bytes.ok())
      return bytes.status();
    auto policy = decode_namespace_policy(bytes.value());
    if (!policy.ok())
      return policy.status();
    if (policy.value().id != stem) {
      return Status{ErrorCode::protocol_error,
                    "sync namespace filename and record id differ"};
    }
    policies.push_back(std::move(policy.value()));
  }
  return policies;
}

Result<NamespaceInstallResult>
install_namespace_policy(const std::filesystem::path &root,
                         const NamespacePolicy &policy,
                         std::uint32_t expected_owner_uid) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok())
    return valid;
  auto encoded = encode_namespace_policy(policy);
  if (!encoded.ok())
    return encoded.status();

  auto opened = open_absolute_directory(root);
  if (!opened.ok())
    return opened.status();
  FileDescriptor root_fd = std::move(opened.value());
  Status secure =
      validate_directory(root_fd.get(), expected_owner_uid,
                         "sync policy root");
  if (!secure.ok())
    return secure;
  FileDescriptor namespaces_fd(
      ::openat(root_fd.get(), "namespaces",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespaces_fd.get() < 0)
    return system_error("open sync namespace directory");
  secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                              "sync namespace directory");
  if (!secure.ok())
    return secure;
  while (::flock(namespaces_fd.get(), LOCK_EX) != 0) {
    if (errno == EINTR)
      continue;
    return system_error("lock sync namespace directory");
  }
  const Status cleaned = cleanup_update_temporaries(
      namespaces_fd.get(), expected_owner_uid);
  if (!cleaned.ok()) return cleaned;

  auto existing = load_namespace_store(root, expected_owner_uid);
  if (!existing.ok())
    return existing.status();
  const auto found = std::find_if(
      existing.value().begin(), existing.value().end(),
      [&policy](const NamespacePolicy &candidate) {
        return candidate.id == policy.id;
      });
  if (found != existing.value().end()) {
    if (*found == policy) {
      return NamespaceInstallResult{
          NamespaceInstallDisposition::duplicate, policy};
    }
    return Status{ErrorCode::unavailable,
                  "sync namespace replacement is not implemented"};
  }
  if (existing.value().size() >= kMaximumNamespaces) {
    return Status{ErrorCode::resource_exhausted,
                  "sync namespace store is full"};
  }

  FileDescriptor temporary(
      ::openat(namespaces_fd.get(), ".",
               O_WRONLY | O_CLOEXEC | O_TMPFILE,
               static_cast<mode_t>(0600)));
  if (temporary.get() < 0) {
    return system_error(
        "create unnamed synchronization namespace record");
  }
  if (::fchmod(temporary.get(), static_cast<mode_t>(0600)) != 0) {
    return system_error(
        "set synchronization namespace record permissions");
  }
  std::size_t offset = 0U;
  while (offset < encoded.value().size()) {
    const ssize_t count = ::write(
        temporary.get(), encoded.value().data() + offset,
        encoded.value().size() - offset);
    if (count > 0) {
      offset += static_cast<std::size_t>(count);
      continue;
    }
    if (count < 0 && errno == EINTR)
      continue;
    return system_error("write synchronization namespace record");
  }
  if (::fsync(temporary.get()) != 0)
    return system_error("fsync synchronization namespace record");

  const std::string filename = policy.id + ".namespace";
  if (::linkat(temporary.get(), "", namespaces_fd.get(), filename.c_str(),
               AT_EMPTY_PATH) != 0) {
    const int saved = errno;
    if (saved == EEXIST) {
      auto raced = load_namespace_store(root, expected_owner_uid);
      if (!raced.ok())
        return raced.status();
      const auto winner = std::find_if(
          raced.value().begin(), raced.value().end(),
          [&policy](const NamespacePolicy &candidate) {
            return candidate.id == policy.id;
          });
      if (winner != raced.value().end() && *winner == policy) {
        return NamespaceInstallResult{
            NamespaceInstallDisposition::duplicate, policy};
      }
      return Status{ErrorCode::unavailable,
                    "sync namespace was concurrently installed differently"};
    }
    return system_error("publish synchronization namespace record", saved);
  }
  if (::fsync(namespaces_fd.get()) != 0) {
    return system_error("fsync synchronization namespace directory");
  }
  return NamespaceInstallResult{
      NamespaceInstallDisposition::installed, policy};
}

Status cleanup_namespace_policy_temporaries(
    const std::filesystem::path &root,
    std::uint32_t expected_owner_uid) {
  auto opened = open_absolute_directory(root);
  if (!opened.ok()) return opened.status();
  FileDescriptor root_fd = std::move(opened.value());
  Status secure = validate_directory(root_fd.get(), expected_owner_uid,
                                     "sync policy root");
  if (!secure.ok()) return secure;
  FileDescriptor namespaces_fd(
      ::openat(root_fd.get(), "namespaces",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespaces_fd.get() < 0)
    return system_error("open sync namespace directory");
  secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                              "sync namespace directory");
  if (!secure.ok()) return secure;
  while (::flock(namespaces_fd.get(), LOCK_EX) != 0) {
    if (errno == EINTR) continue;
    return system_error("lock sync namespace directory");
  }
  return cleanup_update_temporaries(namespaces_fd.get(),
                                    expected_owner_uid);
}

Result<NamespaceUpdateResult>
update_namespace_policy(const std::filesystem::path &root,
                        const NamespacePolicy &policy,
                        std::uint32_t expected_owner_uid) {
  const Status valid = validate_namespace_policy(policy);
  if (!valid.ok()) return valid;
  auto encoded = encode_namespace_policy(policy);
  if (!encoded.ok()) return encoded.status();

  auto opened = open_absolute_directory(root);
  if (!opened.ok()) return opened.status();
  FileDescriptor root_fd = std::move(opened.value());
  Status secure = validate_directory(root_fd.get(), expected_owner_uid,
                                     "sync policy root");
  if (!secure.ok()) return secure;
  FileDescriptor namespaces_fd(
      ::openat(root_fd.get(), "namespaces",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespaces_fd.get() < 0)
    return system_error("open sync namespace directory");
  secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                              "sync namespace directory");
  if (!secure.ok()) return secure;
  while (::flock(namespaces_fd.get(), LOCK_EX) != 0) {
    if (errno == EINTR) continue;
    return system_error("lock sync namespace directory");
  }
  const Status cleaned = cleanup_update_temporaries(
      namespaces_fd.get(), expected_owner_uid);
  if (!cleaned.ok()) return cleaned;

  auto existing = load_namespace_store(root, expected_owner_uid);
  if (!existing.ok()) return existing.status();
  const auto found = std::find_if(
      existing.value().begin(), existing.value().end(),
      [&policy](const NamespacePolicy &candidate) {
        return candidate.id == policy.id;
      });
  if (found == existing.value().end()) {
    return Status{ErrorCode::not_found,
                  "sync namespace update target is absent"};
  }
  if (*found == policy) {
    if (::fsync(namespaces_fd.get()) != 0)
      return system_error("fsync duplicate sync namespace update");
    return NamespaceUpdateResult{
        NamespaceUpdateDisposition::duplicate, policy};
  }
  if (found->root != policy.root || found->engine != policy.engine ||
      found->quotas != policy.quotas) {
    return Status{
        ErrorCode::invalid_argument,
        "sync namespace update cannot change id, root, engine, or quotas"};
  }

  auto temporary = write_policy_temporary(namespaces_fd.get(),
                                          encoded.value());
  if (!temporary.ok()) return temporary.status();
  const std::string temporary_name = update_temporary_name(policy.id);
  if (::linkat(temporary.value().get(), "", namespaces_fd.get(),
               temporary_name.c_str(), AT_EMPTY_PATH) != 0) {
    return system_error("stage synchronization namespace update");
  }
  const std::string filename = policy.id + ".namespace";
  if (::renameat(namespaces_fd.get(), temporary_name.c_str(),
                 namespaces_fd.get(), filename.c_str()) != 0) {
    const int saved = errno;
    static_cast<void>(
        ::unlinkat(namespaces_fd.get(), temporary_name.c_str(), 0));
    return system_error("replace synchronization namespace record", saved);
  }
  if (::fsync(namespaces_fd.get()) != 0)
    return system_error("fsync synchronization namespace directory");
  return NamespaceUpdateResult{
      NamespaceUpdateDisposition::updated, policy};
}

Result<NamespaceRemoveResult>
remove_namespace_policy(const std::filesystem::path &root,
                        std::string_view namespace_id,
                        std::uint32_t expected_owner_uid) {
  if (!valid_id(namespace_id)) {
    return Status{ErrorCode::invalid_argument,
                  "sync namespace id is invalid"};
  }
  auto opened = open_absolute_directory(root);
  if (!opened.ok()) return opened.status();
  FileDescriptor root_fd = std::move(opened.value());
  Status secure = validate_directory(root_fd.get(), expected_owner_uid,
                                     "sync policy root");
  if (!secure.ok()) return secure;
  FileDescriptor namespaces_fd(
      ::openat(root_fd.get(), "namespaces",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (namespaces_fd.get() < 0)
    return system_error("open sync namespace directory");
  secure = validate_directory(namespaces_fd.get(), expected_owner_uid,
                              "sync namespace directory");
  if (!secure.ok()) return secure;
  while (::flock(namespaces_fd.get(), LOCK_EX) != 0) {
    if (errno == EINTR) continue;
    return system_error("lock sync namespace directory");
  }
  const Status cleaned = cleanup_update_temporaries(
      namespaces_fd.get(), expected_owner_uid);
  if (!cleaned.ok()) return cleaned;

  auto existing = load_namespace_store(root, expected_owner_uid);
  if (!existing.ok()) return existing.status();
  const auto found = std::find_if(
      existing.value().begin(), existing.value().end(),
      [namespace_id](const NamespacePolicy &candidate) {
        return candidate.id == namespace_id;
      });
  if (found == existing.value().end()) {
    if (::fsync(namespaces_fd.get()) != 0)
      return system_error("fsync absent sync namespace removal");
    return NamespaceRemoveResult{
        NamespaceRemoveDisposition::absent, std::string(namespace_id)};
  }
  const std::string filename = std::string(namespace_id) + ".namespace";
  if (::unlinkat(namespaces_fd.get(), filename.c_str(), 0) != 0) {
    return system_error("remove synchronization namespace record");
  }
  if (::fsync(namespaces_fd.get()) != 0)
    return system_error("fsync synchronization namespace directory");
  return NamespaceRemoveResult{
      NamespaceRemoveDisposition::removed, std::string(namespace_id)};
}

Status NamespaceRegistry::replace(std::vector<NamespacePolicy> policies) {
  if (policies.size() > kMaximumNamespaces) {
    return Status{ErrorCode::resource_exhausted,
                  "sync namespace replacement exceeds its entry bound"};
  }
  for (const NamespacePolicy &policy : policies) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok())
      return valid;
  }
  std::sort(
      policies.begin(), policies.end(),
      [](const auto &left, const auto &right) { return left.id < right.id; });
  if (std::adjacent_find(policies.begin(), policies.end(),
                         [](const auto &left, const auto &right) {
                           return left.id == right.id;
                         }) != policies.end()) {
    return Status{ErrorCode::invalid_argument, "duplicate sync namespace id"};
  }
  std::unique_lock lock(mutex_);
  if (generation_ == std::numeric_limits<std::uint64_t>::max()) {
    return Status{ErrorCode::resource_exhausted,
                  "sync namespace registry generation is exhausted"};
  }
  policies_ = std::move(policies);
  ++generation_;
  return Status::success();
}

void NamespaceRegistry::fail_closed() noexcept {
  std::unique_lock lock(mutex_);
  policies_.clear();
}

Result<NamespacePolicy> NamespaceRegistry::resolve(std::string_view id) const {
  std::shared_lock lock(mutex_);
  const auto found = std::lower_bound(
      policies_.begin(), policies_.end(), id,
      [](const NamespacePolicy &policy, std::string_view candidate) {
        return policy.id < candidate;
      });
  if (found == policies_.end() || found->id != id) {
    return Status{ErrorCode::not_found, "sync namespace is not configured"};
  }
  return *found;
}

std::vector<NamespacePolicy> NamespaceRegistry::list() const {
  std::shared_lock lock(mutex_);
  return policies_;
}

RegistrySnapshot NamespaceRegistry::snapshot() const {
  std::shared_lock lock(mutex_);
  return RegistrySnapshot{
      generation_, policies_.size(),
      static_cast<std::size_t>(std::count_if(policies_.begin(), policies_.end(),
                                             [](const NamespacePolicy &policy) {
                                               return policy.activation !=
                                                      ActivationMode::disabled;
                                             }))};
}

} // namespace iotox::sync
