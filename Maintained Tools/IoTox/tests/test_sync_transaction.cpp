#include "test_harness.hpp"

#include "iotox/sync_transaction.hpp"

#include <atomic>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace {

using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::PrincipalId;
using iotox::sync::SyncNamespaceTransaction;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-transaction-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr)
      throw std::runtime_error("mkdtemp failed");
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

NamespacePolicy policy(const std::filesystem::path &root,
                       std::string id = "field-notes") {
  PrincipalId writer{};
  writer[0U] = 1U;
  NamespacePolicy result;
  result.id = std::move(id);
  result.root = root.lexically_normal().string();
  result.engine = Engine::range_v1;
  result.writers = {writer};
  return result;
}

} // namespace

IOTOX_TEST("sync transaction is private persistent and namespace bound") {
  TempDirectory temporary;
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto transaction = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(transaction.value().matches(configured));
  NamespacePolicy wrong = configured;
  wrong.id = "other";
  IOTOX_CHECK(!transaction.value().matches(wrong));
  IOTOX_CHECK(!iotox::sync::require_sync_transaction(
                   wrong, transaction.value())
                   .ok());

  const auto lock = std::filesystem::path(configured.root) / "transactions" /
                    "field-notes.transaction.lock";
  struct stat metadata {};
  IOTOX_CHECK(::lstat(lock.c_str(), &metadata) == 0);
  IOTOX_CHECK(S_ISREG(metadata.st_mode));
  IOTOX_CHECK(metadata.st_nlink == 1);
  IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0777)) ==
              static_cast<mode_t>(0600));
  struct stat root_metadata {};
  IOTOX_CHECK(::lstat(configured.root.c_str(), &root_metadata) == 0);
  IOTOX_CHECK(transaction.value().pins_root(
      static_cast<std::uint64_t>(root_metadata.st_dev),
      static_cast<std::uint64_t>(root_metadata.st_ino)));
}

IOTOX_TEST("sync transaction move preserves the exact lock proof") {
  TempDirectory temporary;
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto acquired = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(acquired.ok());
  SyncNamespaceTransaction moved = std::move(acquired.value());
  IOTOX_CHECK(moved.matches(configured));
  IOTOX_CHECK(!acquired.value().matches(configured));
}

IOTOX_TEST("sync transaction token cannot be reused by another thread") {
  TempDirectory temporary;
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto acquired = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(acquired.ok());
  std::atomic<bool> matched{true};
  std::thread contender([&]() {
    matched.store(acquired.value().matches(configured),
                  std::memory_order_release);
  });
  contender.join();
  IOTOX_CHECK(!matched.load(std::memory_order_acquire));
  IOTOX_CHECK(acquired.value().matches(configured));
}

IOTOX_TEST("sync transaction refuses a substituted namespace root") {
  TempDirectory temporary;
  NamespacePolicy configured = policy(temporary.path() / "sync");
  auto acquired = SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(acquired.ok());
  const std::filesystem::path original{configured.root};
  const std::filesystem::path parked = temporary.path() / "parked-sync";
  std::filesystem::rename(original, parked);
  std::filesystem::create_directory(original);
  std::filesystem::permissions(original, std::filesystem::perms::owner_all,
                               std::filesystem::perm_options::replace);
  struct stat replacement {};
  IOTOX_CHECK(::lstat(original.c_str(), &replacement) == 0);
  IOTOX_CHECK(!acquired.value().pins_root(
      static_cast<std::uint64_t>(replacement.st_dev),
      static_cast<std::uint64_t>(replacement.st_ino)));
  IOTOX_CHECK(!acquired.value().matches(configured));
  IOTOX_CHECK(
      !iotox::sync::require_sync_transaction(configured, acquired.value())
           .ok());
}

IOTOX_TEST("sync transaction refuses weak linked and symlink lock state") {
  TempDirectory temporary;
  NamespacePolicy configured = policy(temporary.path() / "sync");
  {
    auto acquired = SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(acquired.ok());
  }
  const auto lock = std::filesystem::path(configured.root) / "transactions" /
                    "field-notes.transaction.lock";
  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::add);
  IOTOX_CHECK(!SyncNamespaceTransaction::acquire(configured).ok());
  std::filesystem::permissions(lock, std::filesystem::perms::group_read,
                               std::filesystem::perm_options::remove);

  const auto alias = lock.parent_path() / "alias";
  std::filesystem::create_hard_link(lock, alias);
  IOTOX_CHECK(!SyncNamespaceTransaction::acquire(configured).ok());
  std::filesystem::remove(alias);

  const auto backing = lock.parent_path() / "backing";
  std::filesystem::rename(lock, backing);
  std::filesystem::create_symlink(backing.filename(), lock);
  IOTOX_CHECK(!SyncNamespaceTransaction::acquire(configured).ok());
}
