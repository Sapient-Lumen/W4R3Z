#include "iotox/security/identity.hpp"
#include "iotox/sync_publication.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <string>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::SignedHeadPublicationRequest;
using iotox::sync::SignedHeadStore;

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

SignedHeadPublicationRequest request(std::uint8_t value) {
  SignedHeadPublicationRequest result;
  result.artifact = digest(value);
  result.manifest = digest(static_cast<std::uint8_t>(value + 64U));
  result.artifact_bytes = 100U + value;
  result.manifest_bytes = 20U + value;
  return result;
}

int run() {
  std::string pattern = "/tmp/iotox-sync-publication-process-XXXXXX";
  std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
  mutable_pattern.push_back('\0');
  char *created = ::mkdtemp(mutable_pattern.data());
  if (created == nullptr)
    return 1;
  const std::filesystem::path temporary{created};
  const auto cleanup = [&]() {
    std::error_code ignored;
    std::filesystem::remove_all(temporary, ignored);
  };

  auto parent_crypto = Sodium::load();
  if (!parent_crypto.ok()) {
    cleanup();
    return 1;
  }
  const std::filesystem::path identity_path = temporary / "writer.identity";
  auto parent_identity = DeviceIdentity::load_or_create(
      identity_path, parent_crypto.value(), true);
  if (!parent_identity.ok()) {
    cleanup();
    return 1;
  }
  const std::filesystem::path root = temporary / "sync";
  NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = root.lexically_normal().string();
  policy.engine = Engine::range_v1;
  policy.writers = {parent_identity.value().public_key()};
  policy.quotas.maximum_artifact_bytes = 4096U;
  policy.quotas.maximum_manifest_bytes = 1024U;

  std::vector<pid_t> children;
  for (std::uint8_t index = 0U; index < 8U; ++index) {
    const pid_t child = ::fork();
    if (child < 0) {
      cleanup();
      return 1;
    }
    if (child == 0) {
      auto crypto = Sodium::load();
      if (!crypto.ok())
        ::_exit(1);
      auto identity = DeviceIdentity::load(identity_path, crypto.value());
      if (!identity.ok())
        ::_exit(1);
      SignedHeadStore store(root);
      auto published = store.publish(
          policy, request(static_cast<std::uint8_t>(64U + index)),
          identity.value(), crypto.value());
      ::_exit(published.ok() ? 0 : 1);
    }
    children.push_back(child);
  }

  bool passed = true;
  for (const pid_t child : children) {
    int status = 0;
    passed = ::waitpid(child, &status, 0) == child && WIFEXITED(status) &&
             WEXITSTATUS(status) == 0 && passed;
  }
  SignedHeadStore store(root);
  auto loaded = store.load(policy, parent_crypto.value());
  passed = passed && loaded.ok() && loaded.value().has_value() &&
           loaded.value()->generation == 8U;
  cleanup();
  return passed ? 0 : 1;
}

} // namespace

int main() {
  const int status = run();
  if (status != 0)
    std::cerr << "cross-process signed HEAD serialization failed\n";
  return status;
}
