#include "iotox/sync_digest.hpp"

#include "test_harness.hpp"

#include <filesystem>
#include <fstream>
#include <string>
#include <unistd.h>

namespace {

std::filesystem::path temporary_root() {
  return std::filesystem::temp_directory_path() /
         ("iotox-sync-digest-" + std::to_string(::getpid()));
}

std::string hex(const iotox::sync::Digest &digest) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string output;
  output.reserve(64U);
  for (const std::uint8_t byte : digest) {
    output.push_back(digits[byte >> 4U]);
    output.push_back(digits[byte & 0x0fU]);
  }
  return output;
}

} // namespace

IOTOX_TEST("production sync hasher matches the canonical SHA-256 identity") {
  const auto root = temporary_root();
  std::filesystem::remove_all(root);
  std::filesystem::create_directories(root);
  const auto empty = root / "empty";
  const auto abc = root / "abc";
  std::ofstream(empty, std::ios::binary).close();
  {
    std::ofstream output(abc, std::ios::binary);
    output << "abc";
  }
  auto empty_digest = iotox::sync::hash_sync_file_sha256(empty);
  auto abc_digest = iotox::sync::hash_sync_file_sha256(abc);
  IOTOX_CHECK(empty_digest.ok());
  IOTOX_CHECK(abc_digest.ok());
  IOTOX_CHECK(hex(empty_digest.value()) == "e3b0c44298fc1c149afbf4c8996fb924"
                                           "27ae41e4649b934ca495991b7852b855");
  IOTOX_CHECK(hex(abc_digest.value()) == "ba7816bf8f01cfea414140de5dae2223"
                                         "b00361a396177a9cb410ff61f20015ad");
  std::filesystem::remove_all(root);
}

IOTOX_TEST("production sync hasher rejects paths aliases and non-files") {
  const auto root = temporary_root();
  std::filesystem::remove_all(root);
  std::filesystem::create_directories(root);
  const auto source = root / "source";
  const auto alias = root / "alias";
  {
    std::ofstream output(source, std::ios::binary);
    output << "payload";
  }
  std::filesystem::create_symlink(source, alias);
  IOTOX_CHECK(!iotox::sync::hash_sync_file_sha256("relative").ok());
  IOTOX_CHECK(!iotox::sync::hash_sync_file_sha256(alias).ok());
  IOTOX_CHECK(!iotox::sync::hash_sync_file_sha256(root).ok());
  std::filesystem::remove_all(root);
}
