#include "test_harness.hpp"

#include "iotox/sync_source_watch.hpp"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-source-watch-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
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

void write_text(const std::filesystem::path &path, std::string text) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output << text;
  output.close();
  if (!output)
    throw std::runtime_error("write failed");
}

std::vector<std::string>
wait_for_dirty(iotox::sync::SyncSourceWatchSet &watch) {
  for (int attempt = 0; attempt < 50; ++attempt) {
    auto dirty = watch.drain();
    IOTOX_CHECK_MSG(dirty.ok(), dirty.status().message());
    if (!dirty.value().empty())
      return dirty.value();
    ::usleep(10000);
  }
  return {};
}

} // namespace

IOTOX_TEST("sync source watch observes recursive source changes") {
  TempDirectory temporary;
  const std::filesystem::path root = temporary.path() / "source";
  const std::filesystem::path nested = root / "nested";
  std::filesystem::create_directories(nested);

  iotox::sync::SyncSourceWatchSet watch;
  const std::vector<iotox::sync::SyncSourceWatchRoot> roots{
      iotox::sync::SyncSourceWatchRoot{"alpha", root}};
  auto replaced = watch.replace(roots);
  IOTOX_CHECK_MSG(replaced.ok(), replaced.message());
  auto snapshot = watch.snapshot();
  IOTOX_CHECK(snapshot.configured_roots == 1U);
  IOTOX_CHECK(snapshot.active_watches >= 2U);

  write_text(nested / "first.txt", "one");
  auto dirty = wait_for_dirty(watch);
  IOTOX_CHECK(dirty.size() == 1U);
  IOTOX_CHECK(dirty.front() == "alpha");
  dirty = watch.drain().value();
  IOTOX_CHECK(dirty.empty());

  const std::filesystem::path created = root / "created";
  std::filesystem::create_directories(created);
  dirty = wait_for_dirty(watch);
  IOTOX_CHECK(dirty.size() == 1U);
  IOTOX_CHECK(dirty.front() == "alpha");

  write_text(created / "second.txt", "two");
  dirty = wait_for_dirty(watch);
  IOTOX_CHECK(dirty.size() == 1U);
  IOTOX_CHECK(dirty.front() == "alpha");

  IOTOX_CHECK(watch.replace({}).ok());
  write_text(created / "third.txt", "three");
  dirty = watch.drain().value();
  IOTOX_CHECK(dirty.empty());
}

IOTOX_TEST("sync source watch rejects malformed roots") {
  iotox::sync::SyncSourceWatchSet watch;
  const std::vector<iotox::sync::SyncSourceWatchRoot> bad_namespace{
      iotox::sync::SyncSourceWatchRoot{"not ok", "/tmp/source"}};
  IOTOX_CHECK(!watch.replace(bad_namespace).ok());
  const std::vector<iotox::sync::SyncSourceWatchRoot> bad_path{
      iotox::sync::SyncSourceWatchRoot{"alpha", "relative"}};
  IOTOX_CHECK(!watch.replace(bad_path).ok());
}
