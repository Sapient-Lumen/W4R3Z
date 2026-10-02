#include "iotox/update_service.hpp"

#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <string_view>
#include <thread>
#include <unistd.h>

int main() {
  const char *ready_fd = ::getenv("IOTOX_SERVICE_READY_FD");
  const char *sequence_text = ::getenv("IOTOX_UPDATE_SEQUENCE");
  const char *version_text = ::getenv("IOTOX_UPDATE_VERSION");
  if (ready_fd == nullptr || std::string_view(ready_fd) != "3" ||
      sequence_text == nullptr || version_text == nullptr) {
    return 125;
  }
  if (std::string_view(version_text) == "exit-before-ready") {
    return 23;
  }
  if (std::string_view(version_text) == "delayed-ready") {
    std::this_thread::sleep_for(std::chrono::milliseconds(1500));
  }
  const std::string_view sequence_view(sequence_text);
  std::uint64_t sequence = 0U;
  const auto parsed = std::from_chars(
      sequence_view.data(),
      sequence_view.data() + sequence_view.size(), sequence);
  if (parsed.ec != std::errc{} ||
      parsed.ptr != sequence_view.data() + sequence_view.size() ||
      sequence == 0U) {
    return 125;
  }
  const auto record =
      iotox::update::encode_update_service_ready_record(sequence);
  const ssize_t written = ::write(
      iotox::update::kUpdateServiceReadyDescriptor,
      record.data(), record.size());
  if (written != static_cast<ssize_t>(record.size())) return 125;
  static_cast<void>(::close(
      iotox::update::kUpdateServiceReadyDescriptor));
  while (true) ::pause();
}
