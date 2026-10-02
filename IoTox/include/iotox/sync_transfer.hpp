#pragma once

#include "iotox/route_worker.hpp"
#include "iotox/sync_attempt_store.hpp"
#include "iotox/sync_scheduler.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <optional>
#include <vector>

namespace iotox::sync {

struct SyncTransferBindingSnapshot {
  std::uint64_t attempt_id{0U};
  SyncObjectRecord object;
  routes::ToxPublicKey route_key{};
  std::uint64_t worker_id{0U};
  std::uint32_t file_number{0U};
  std::filesystem::path staging_path;
  std::uint64_t resume_offset{0U};
  bool admitted{false};
};

struct SyncTransferCoordinatorSnapshot {
  std::vector<SyncTransferBindingSnapshot> bindings;
  std::uint64_t accepted_offers{0U};
  std::uint64_t deferred_offers{0U};
  std::uint64_t committed_objects{0U};
  std::uint64_t failed_attempts{0U};
  std::uint64_t stale_terminal_events{0U};
  std::uint64_t retained_partials{0U};
  std::uint64_t retained_attempts{0U};
  std::uint64_t retained_bytes{0U};
  std::uint64_t retention_fallbacks{0U};
  std::uint64_t resumed_attempts{0U};
  std::uint64_t resumed_bytes{0U};
  std::uint64_t restart_resumed_attempts{0U};
  std::uint64_t restart_resumed_bytes{0U};
  bool closed{false};
};

class SyncTransferCoordinator {
public:
  struct Seams {
    std::function<Result<FileTransferRecord>(
        const routes::ToxPublicKey &, std::uint64_t, std::uint32_t,
        const std::filesystem::path &)> receive_to_path;
    std::function<Result<FileTransferRecord>(
        const routes::ToxPublicKey &, std::uint64_t, std::uint32_t,
        const std::filesystem::path &, std::uint64_t)>
        receive_to_path_from_offset;
    std::function<Status(const routes::ToxPublicKey &, std::uint64_t,
                         std::uint32_t)> cancel_transfer;
    std::function<Status(const routes::ToxPublicKey &, std::uint64_t,
                         std::uint32_t)> retire_transfer;
    std::function<Result<std::vector<routes::WorkerTransferTerminalEvent>>(
        std::size_t)> take_terminal_events;
    SyncInstallSeams install;
  };

  struct Config {
    NamespacePolicy policy;
    std::size_t maximum_bindings{256U};
    std::size_t maximum_events_per_service{64U};
    std::uint64_t copy_chunk_bytes{64U * 1024U};
    Seams seams;
    // All three persistence pointers are configured together. Scheduler
    // attempt IDs must come from this store's reserve_attempt_id entrance.
    SyncAttemptStore *attempt_store{nullptr};
    const security::DeviceIdentity *identity{nullptr};
    const security::Sodium *sodium{nullptr};
  };

  SyncTransferCoordinator(SyncObjectScheduler &scheduler, Config config);
  ~SyncTransferCoordinator() noexcept;

  SyncTransferCoordinator(const SyncTransferCoordinator &) = delete;
  SyncTransferCoordinator &operator=(const SyncTransferCoordinator &) = delete;

  [[nodiscard]] Result<SyncTransferBindingSnapshot>
  accept_offer(std::uint64_t attempt_id, std::uint32_t file_number);
  // Parent dispatchers should drain the supervisor once and route each event
  // here when more than one namespace coordinator is active.
  [[nodiscard]] Status handle_terminal(
      routes::WorkerTransferTerminalEvent event);
  // Cancel and clean every binding on one exact carrier incarnation, then
  // fence any assigned-but-not-yet-bound scheduler attempts on that route.
  // The object records return to pending and can be assigned afresh.
  [[nodiscard]] Result<std::size_t> fence_route(
      const routes::ToxPublicKey &route_key, std::uint64_t worker_id,
      bool cancel_transport = true,
      bool retain_incomplete_partials = false);
  // Convenience pump for a sole coordinator that owns the configured drain.
  [[nodiscard]] Status service();
  [[nodiscard]] Status close();
  [[nodiscard]] SyncTransferCoordinatorSnapshot snapshot() const;

private:
  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Result<TransferAttemptSnapshot>
  active_attempt(std::uint64_t attempt_id) const;
  [[nodiscard]] Status fail_binding(std::size_t index,
                                    bool cancel_transport);
  [[nodiscard]] Status retain_binding(std::size_t index,
                                      bool cancel_transport);
  [[nodiscard]] Status discard_retained_partial(std::size_t index);
  [[nodiscard]] Status apply_pending(std::size_t index);
  [[nodiscard]] DurableSyncAttempt durable_attempt(
      const SyncTransferBindingSnapshot &binding) const;

  struct BindingState {
    SyncTransferBindingSnapshot binding;
    std::optional<routes::WorkerTransferTerminalEvent> terminal;
  };

  struct RetainedPartialState {
    SyncTransferBindingSnapshot binding;
    std::uint64_t bytes{0U};
  };

  SyncObjectScheduler *scheduler_{nullptr};
  Config config_;
  std::vector<BindingState> bindings_;
  std::vector<RetainedPartialState> retained_partials_;
  std::uint64_t accepted_offers_{0U};
  std::uint64_t deferred_offers_{0U};
  std::uint64_t committed_objects_{0U};
  std::uint64_t failed_attempts_{0U};
  std::uint64_t stale_terminal_events_{0U};
  std::uint64_t retained_attempts_{0U};
  std::uint64_t retained_bytes_{0U};
  std::uint64_t retention_fallbacks_{0U};
  std::uint64_t resumed_attempts_{0U};
  std::uint64_t resumed_bytes_{0U};
  std::uint64_t restart_resumed_attempts_{0U};
  std::uint64_t restart_resumed_bytes_{0U};
  bool closed_{false};
};

} // namespace iotox::sync
