#pragma once

#include "iotox/route_inventory.hpp"
#include "iotox/sync_job.hpp"

#include <cstdint>
#include <functional>
#include <vector>

namespace iotox::sync {

enum class ScheduledObjectState : std::uint8_t {
  pending = 1U,
  assigned = 2U,
  verified = 3U,
  committed = 4U,
};

enum class TransferAttemptState : std::uint8_t {
  active = 1U,
  fenced = 2U,
  verified = 3U,
  committed = 4U,
};

struct ScheduledObjectSnapshot {
  SyncObjectRecord object;
  ScheduledObjectState state{ScheduledObjectState::pending};
  std::uint64_t current_attempt_id{0U};
};

struct TransferAttemptSnapshot {
  std::uint64_t attempt_id{0U};
  SyncObjectRecord object;
  routes::ToxPublicKey route_key{};
  std::uint64_t worker_id{0U};
  TransferAttemptState state{TransferAttemptState::active};
  bool route_capacity_reserved{false};
  bool staging_bytes_reserved{false};
};

struct SyncSchedulerSnapshot {
  std::vector<ScheduledObjectSnapshot> objects;
  std::vector<TransferAttemptSnapshot> attempts;
  std::uint64_t assignments{0U};
  std::uint64_t fences{0U};
  std::uint64_t late_completions{0U};
  std::uint64_t verification_failures{0U};
  std::uint64_t commits{0U};
  std::uint64_t reserved_staging_bytes{0U};
  bool closed{false};
};

// Transport-neutral immutable-object assignment. A capacity adapter is the
// only transport-capacity entrance. Fenced attempt records remain retained so
// a late toxcore completion cannot target a replacement attempt or commit an
// object. The caller may commit only after independently verifying staged
// bytes against the exact object record.
// Any state referenced by capacity callbacks must outlive the scheduler.
class SyncObjectScheduler {
public:
  struct CapacitySeams {
    std::function<Status(const routes::ToxPublicKey &, std::uint64_t)> admit;
    std::function<Status(const routes::ToxPublicKey &, std::uint64_t)> release;
    // Authentication loss can atomically withdraw capacity before the
    // scheduler observes the route terminal. This seam may report that the
    // exact incarnation is already closed and fully released.
    std::function<Result<bool>(const routes::ToxPublicKey &, std::uint64_t)>
        already_released;
  };

  struct Config {
    std::size_t maximum_objects{256U};
    std::size_t maximum_attempts{1024U};
    // A scheduler is namespace-scoped; product construction supplies the
    // namespace policy's maximum_staging_bytes here.
    std::uint64_t maximum_staging_bytes{128U * 1024U * 1024U};
    std::function<Result<std::uint64_t>()> make_attempt_id;
  };

  explicit SyncObjectScheduler(routes::Coordinator &coordinator);
  SyncObjectScheduler(routes::Coordinator &coordinator, Config config);
  SyncObjectScheduler(CapacitySeams capacity, Config config);
  ~SyncObjectScheduler() noexcept;

  SyncObjectScheduler(const SyncObjectScheduler &) = delete;
  SyncObjectScheduler &operator=(const SyncObjectScheduler &) = delete;

  [[nodiscard]] Status add_object(const SyncObjectRecord &object);
  [[nodiscard]] Result<TransferAttemptSnapshot> assign(
      SyncObjectKind kind, const Digest &identity,
      const routes::ToxPublicKey &route_key, std::uint64_t worker_id);
  [[nodiscard]] Result<std::size_t> fence_route(
      const routes::ToxPublicKey &route_key, std::uint64_t worker_id);
  [[nodiscard]] Status fence_attempt(std::uint64_t attempt_id);
  [[nodiscard]] Status complete(
      std::uint64_t attempt_id, const Digest &observed_identity,
      std::uint64_t observed_bytes);
  [[nodiscard]] Status commit(std::uint64_t attempt_id);
  [[nodiscard]] Status close();
  [[nodiscard]] SyncSchedulerSnapshot snapshot() const;

private:
  [[nodiscard]] Status validate_config() const;
  [[nodiscard]] Result<std::size_t> object_index(
      SyncObjectKind kind, const Digest &identity) const;
  [[nodiscard]] Result<std::size_t> attempt_index(
      std::uint64_t attempt_id) const;
  [[nodiscard]] Status release_reservations(TransferAttemptSnapshot &attempt);

  CapacitySeams capacity_;
  Config config_;
  std::vector<ScheduledObjectSnapshot> objects_;
  std::vector<TransferAttemptSnapshot> attempts_;
  std::uint64_t assignments_{0U};
  std::uint64_t fences_{0U};
  std::uint64_t late_completions_{0U};
  std::uint64_t verification_failures_{0U};
  std::uint64_t commits_{0U};
  std::uint64_t reserved_staging_bytes_{0U};
  bool closed_{false};
};

} // namespace iotox::sync
