#include "iotox/security/identity.hpp"
#include "iotox/sync_retention.hpp"

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
using iotox::sync::AcceptedHead;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::RetentionStore;

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

AcceptedHead head(std::uint64_t generation, std::uint8_t value,
                  const iotox::sync::PrincipalId &writer) {
  AcceptedHead result;
  result.namespace_id = "field-notes";
  result.writer = writer;
  result.engine = Engine::range_v1;
  result.generation = generation;
  result.record = digest(value);
  result.parent = generation == 1U ? Digest{} : digest(200U);
  result.artifact = digest(static_cast<std::uint8_t>(value + 32U));
  result.manifest = digest(static_cast<std::uint8_t>(value + 64U));
  result.artifact_bytes = 100U + value;
  result.manifest_bytes = 20U + value;
  return result;
}

int run() {
  std::string pattern = "/tmp/iotox-sync-retention-process-XXXXXX";
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
  const std::filesystem::path identity_path = temporary / "device.identity";
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
  policy.quotas.maximum_objects = 8U;
  policy.quotas.maximum_retained_revisions = 8U;

  std::vector<pid_t> children;
  for (std::uint8_t index = 0U; index < 8U; ++index) {
    const pid_t child = ::fork();
    if (child < 0) {
      for (const pid_t existing : children) {
        int ignored = 0;
        static_cast<void>(::waitpid(existing, &ignored, 0));
      }
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
      RetentionStore store(root);
      auto pinned = store.pin(
          policy,
          head(static_cast<std::uint64_t>(index) + 1U,
               static_cast<std::uint8_t>(index + 1U),
               identity.value().public_key()),
          identity.value(), crypto.value());
      ::_exit(pinned.ok() ? 0 : 1);
    }
    children.push_back(child);
  }

  bool passed = true;
  for (const pid_t child : children) {
    int status = 0;
    passed = ::waitpid(child, &status, 0) == child && WIFEXITED(status) &&
             WEXITSTATUS(status) == 0 && passed;
  }
  RetentionStore store(root);
  auto loaded = store.load(policy, parent_identity.value().public_key(),
                           parent_crypto.value());
  passed = passed && loaded.ok() && loaded.value().mutation == 8U &&
           loaded.value().revisions.size() == 8U;
  if (passed) {
    for (std::size_t index = 0U; index < 8U; ++index) {
      passed = loaded.value().revisions[index].generation == index + 1U &&
               passed;
    }
  }
  cleanup();
  return passed ? 0 : 1;
}

} // namespace

int main() {
  const int status = run();
  if (status != 0)
    std::cerr << "cross-process signed retention serialization failed\n";
  return status;
}
