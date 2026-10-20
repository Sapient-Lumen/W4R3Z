#pragma once

#include "iotox/status.hpp"
#include "iotox/update_state.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <mutex>
#include <string>
#include <string_view>

namespace iotox::update {

inline constexpr std::string_view kInternalUpdateServiceChildArgument =
    "__iotox-update-service-child-v1";
inline constexpr int kUpdateServiceReadyDescriptor = 3;
inline constexpr std::size_t kUpdateServiceReadyRecordBytes = 16U;
using UpdateServiceReadyRecord =
    std::array<std::uint8_t, kUpdateServiceReadyRecordBytes>;

[[nodiscard]] UpdateServiceReadyRecord encode_update_service_ready_record(
    std::uint64_t release_sequence) noexcept;

enum class LinuxServicePhase : std::uint8_t {
  starting = 1U,
  ready = 2U,
  exited = 3U,
  failed = 4U,
  stopped = 5U,
};

[[nodiscard]] std::string_view linux_service_phase_name(
    LinuxServicePhase phase) noexcept;

struct LinuxServiceConfig {
  // The exact IoTox executable used for the internal pre-exec helper. The
  // helper exists so a multithreaded Agent never forks into C++ runtime code.
  std::filesystem::path helper_executable;
  std::chrono::milliseconds helper_startup_timeout{3000};
  std::chrono::milliseconds readiness_timeout{30'000};
  std::chrono::milliseconds shutdown_timeout{3000};
};

struct LinuxServiceSnapshot {
  LinuxServicePhase phase{LinuxServicePhase::failed};
  std::int64_t process_id{-1};
  std::uint64_t release_sequence{0U};
  std::uint64_t payload_bytes{0U};
  bool candidate{false};
  bool image_sealed{false};
  bool readiness_record_complete{false};
  int exit_status{0};
  int terminating_signal{0};
  std::string detail;
};

// Linux-service-v1 executes only a state-selected linux-service-v1 slot. It
// rehashes the stable mode-0400 file while copying it into an anonymous memfd,
// seals the image against mutation, and delegates final fexecve to a tiny
// no-new-privileges helper. The payload receives only standard descriptors
// plus descriptor 3 for one exact readiness record.
class LinuxServiceAdapter {
public:
  LinuxServiceAdapter(const LinuxServiceAdapter &) = delete;
  LinuxServiceAdapter &operator=(const LinuxServiceAdapter &) = delete;
  LinuxServiceAdapter(LinuxServiceAdapter &&) = delete;
  LinuxServiceAdapter &operator=(LinuxServiceAdapter &&) = delete;
  ~LinuxServiceAdapter();

  [[nodiscard]] static Result<std::unique_ptr<LinuxServiceAdapter>> start(
      LinuxServiceConfig config, const UpdateSelectedSlot &slot);

  // Nonblocking lifecycle service. A timeout or malformed readiness stream
  // fails and terminates the child. Exact readiness remains valid only while
  // that same child is live.
  [[nodiscard]] Status poll();
  [[nodiscard]] Status stop();
  [[nodiscard]] Status mark_confirmed();
  [[nodiscard]] bool healthy() const;
  [[nodiscard]] LinuxServiceSnapshot snapshot() const;

private:
  LinuxServiceAdapter(LinuxServiceConfig config, UpdateSelectedSlot slot);
  [[nodiscard]] Status launch();
  [[nodiscard]] Status poll_locked();
  [[nodiscard]] Status terminate_locked(bool requested);

  LinuxServiceConfig config_;
  UpdateSelectedSlot slot_;
  mutable std::mutex mutex_;
  LinuxServiceSnapshot snapshot_;
  int ready_descriptor_{-1};
  std::int64_t child_{-1};
  std::array<std::uint8_t, kUpdateServiceReadyRecordBytes>
      ready_record_{};
  std::size_t ready_record_bytes_{0U};
  std::chrono::steady_clock::time_point readiness_deadline_{};
};

// Internal implementation entrance intercepted by main. It validates the
// descriptor contract, arms parent-death/no-new-privileges, closes ambient
// descriptors, and fexecve()s the sealed service image. Never a public CLI.
[[nodiscard]] int run_internal_update_service_child() noexcept;

} // namespace iotox::update
