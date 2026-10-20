#include "test_harness.hpp"

#include "iotox/sync_digest.hpp"
#include "iotox/update_service.hpp"

#include <chrono>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

#ifndef IOTOX_UPDATE_SERVICE_FIXTURE_PATH
#error "IOTOX_UPDATE_SERVICE_FIXTURE_PATH is required"
#endif

using namespace std::chrono_literals;
using iotox::update::LinuxServiceAdapter;
using iotox::update::LinuxServiceConfig;
using iotox::update::LinuxServicePhase;
using iotox::update::PayloadKind;
using iotox::update::UpdateSelectedSlot;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-update-service-XXXXXX";
    std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
    mutable_pattern.push_back('\0');
    char *created = ::mkdtemp(mutable_pattern.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
    if (::chmod(path_.c_str(), 0700) != 0)
      throw std::runtime_error("chmod temp failed");
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

std::filesystem::path self_executable() {
  std::vector<char> buffer(4096U);
  const ssize_t count =
      ::readlink("/proc/self/exe", buffer.data(), buffer.size() - 1U);
  if (count <= 0) throw std::runtime_error("read /proc/self/exe failed");
  return std::string(buffer.data(), static_cast<std::size_t>(count));
}

std::filesystem::path service_fixture() {
  return IOTOX_UPDATE_SERVICE_FIXTURE_PATH;
}

UpdateSelectedSlot selected_fixture(
    const TempDirectory &temporary,
    const std::filesystem::path &source,
    std::uint64_t sequence = 7U) {
  const auto slot = temporary.path() / "service.payload";
  std::filesystem::copy_file(
      source, slot, std::filesystem::copy_options::none);
  if (::chmod(slot.c_str(), 0400) != 0)
    throw std::runtime_error("chmod service slot failed");
  auto digest = iotox::sync::hash_sync_file_sha256(slot);
  if (!digest.ok()) throw std::runtime_error(digest.status().message());
  UpdateSelectedSlot result;
  result.revision.payload_kind = PayloadKind::linux_service_v1;
  result.revision.sequence = sequence;
  result.revision.payload_bytes = std::filesystem::file_size(slot);
  result.revision.payload_digest = digest.value();
  result.revision.manifest_record[0U] = 1U;
  result.revision.version = "service-test";
  result.path = slot;
  result.candidate = true;
  return result;
}

LinuxServiceConfig config() {
  LinuxServiceConfig result;
  result.helper_executable = self_executable();
  result.helper_startup_timeout = 3s;
  result.readiness_timeout = 3s;
  result.shutdown_timeout = 1s;
  return result;
}

} // namespace

IOTOX_TEST("linux service adapter seals reverified image and admits readiness") {
  TempDirectory temporary;
  const UpdateSelectedSlot slot =
      selected_fixture(temporary, service_fixture());
  auto adapter = LinuxServiceAdapter::start(config(), slot);
  IOTOX_CHECK_MSG(adapter.ok(), adapter.status().message());
  for (std::size_t attempt = 0U; attempt < 300U &&
       !adapter.value()->healthy(); ++attempt) {
    IOTOX_CHECK_MSG(
        adapter.value()->poll().ok(),
        adapter.value()->snapshot().detail);
    std::this_thread::sleep_for(10ms);
  }
  IOTOX_CHECK(adapter.value()->healthy());
  const auto ready = adapter.value()->snapshot();
  IOTOX_CHECK(ready.phase == LinuxServicePhase::ready);
  IOTOX_CHECK(ready.release_sequence == 7U);
  IOTOX_CHECK(ready.candidate);
  IOTOX_CHECK(ready.image_sealed);
  IOTOX_CHECK(ready.readiness_record_complete);
  IOTOX_CHECK(ready.process_id > 1);
  IOTOX_CHECK(adapter.value()->stop().ok());
  IOTOX_CHECK(
      adapter.value()->snapshot().phase == LinuxServicePhase::stopped);
}

IOTOX_TEST("linux service adapter refuses helper kind digest and mutable slot drift") {
  TempDirectory temporary;
  UpdateSelectedSlot slot =
      selected_fixture(temporary, service_fixture());
  LinuxServiceConfig foreign_helper = config();
  foreign_helper.helper_executable = service_fixture();
  IOTOX_CHECK(!LinuxServiceAdapter::start(foreign_helper, slot).ok());
  slot.revision.payload_kind = PayloadKind::opaque_slot_v1;
  IOTOX_CHECK(!LinuxServiceAdapter::start(config(), slot).ok());
  slot.revision.payload_kind = PayloadKind::linux_service_v1;
  slot.revision.payload_digest[0U] ^= 1U;
  IOTOX_CHECK(!LinuxServiceAdapter::start(config(), slot).ok());
  slot.revision.payload_digest[0U] ^= 1U;
  IOTOX_CHECK(::chmod(slot.path.c_str(), 0500) == 0);
  IOTOX_CHECK(!LinuxServiceAdapter::start(config(), slot).ok());
}

IOTOX_TEST("linux service adapter observes exit before readiness") {
  TempDirectory temporary;
  UpdateSelectedSlot slot =
      selected_fixture(temporary, service_fixture(), 9U);
  slot.revision.version = "exit-before-ready";
  auto adapter = LinuxServiceAdapter::start(config(), slot);
  IOTOX_CHECK_MSG(adapter.ok(), adapter.status().message());
  for (std::size_t attempt = 0U; attempt < 300U; ++attempt) {
    IOTOX_CHECK(adapter.value()->poll().ok());
    if (adapter.value()->snapshot().phase ==
        LinuxServicePhase::exited) {
      break;
    }
    std::this_thread::sleep_for(10ms);
  }
  const auto exited = adapter.value()->snapshot();
  IOTOX_CHECK(
      exited.phase == LinuxServicePhase::failed ||
      exited.phase == LinuxServicePhase::exited);
  IOTOX_CHECK(!adapter.value()->healthy());
}
