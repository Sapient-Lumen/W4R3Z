#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_namespace.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <sys/types.h>
#include <thread>

namespace iotox::sync {

// Move-only proof that this process holds the namespace's exclusive local
// transaction lock. Nested sync operations must receive this same token rather
// than opening and flocking the lock again; inherited-process and cross-thread
// token reuse are rejected.
class SyncNamespaceTransaction {
public:
  ~SyncNamespaceTransaction();

  SyncNamespaceTransaction(const SyncNamespaceTransaction &) = delete;
  SyncNamespaceTransaction &operator=(const SyncNamespaceTransaction &) = delete;
  SyncNamespaceTransaction(SyncNamespaceTransaction &&other) noexcept;
  SyncNamespaceTransaction &
  operator=(SyncNamespaceTransaction &&other) noexcept;

  [[nodiscard]] static Result<SyncNamespaceTransaction>
  acquire(const NamespacePolicy &policy);
  [[nodiscard]] bool matches(const NamespacePolicy &policy) const noexcept;
  [[nodiscard]] bool pins_root(std::uint64_t device,
                               std::uint64_t inode) const noexcept;

private:
  SyncNamespaceTransaction(std::filesystem::path root,
                           std::string namespace_id, int descriptor,
                           int root_descriptor, std::uint64_t root_device,
                           std::uint64_t root_inode);

  std::filesystem::path root_;
  std::string namespace_id_;
  pid_t owner_process_{-1};
  std::thread::id owner_thread_;
  int descriptor_{-1};
  int root_descriptor_{-1};
  std::uint64_t root_device_{0U};
  std::uint64_t root_inode_{0U};
};

[[nodiscard]] Status require_sync_transaction(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction);

} // namespace iotox::sync
