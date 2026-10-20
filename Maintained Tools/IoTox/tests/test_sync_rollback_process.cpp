#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_publication.hpp"

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
  return SignedHeadPublicationRequest{
      digest(value), digest(static_cast<std::uint8_t>(value + 64U)),
      100U + value, 20U + value};
}

bool publish_in_fresh_process(const NamespacePolicy &policy,
                              const std::filesystem::path &identity_path,
                              std::uint8_t value, bool expect_success) {
  const pid_t child = ::fork();
  if (child < 0)
    return false;
  if (child == 0) {
    auto crypto = Sodium::load();
    if (!crypto.ok())
      ::_exit(2);
    auto identity = DeviceIdentity::load(identity_path, crypto.value());
    if (!identity.ok())
      ::_exit(2);
    SignedHeadStore store(policy.root);
    auto published =
        store.publish(policy, request(value), identity.value(), crypto.value());
    ::_exit(published.ok() == expect_success ? 0 : 1);
  }
  int status = 0;
  return ::waitpid(child, &status, 0) == child && WIFEXITED(status) &&
         WEXITSTATUS(status) == 0;
}

int run() {
  std::string pattern = "/tmp/iotox-sync-rollback-process-XXXXXX";
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

  auto crypto = Sodium::load();
  if (!crypto.ok()) {
    cleanup();
    return 1;
  }
  const auto identity_path = temporary / "device.identity";
  auto identity =
      DeviceIdentity::load_or_create(identity_path, crypto.value(), true);
  if (!identity.ok()) {
    cleanup();
    return 1;
  }
  NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = (temporary / "sync").lexically_normal().string();
  policy.engine = Engine::range_v1;
  policy.writers = {identity.value().public_key()};
  policy.quotas.maximum_artifact_bytes = 4096U;
  policy.quotas.maximum_manifest_bytes = 1024U;

  bool passed = publish_in_fresh_process(policy, identity_path, 1U, true);
  const auto published_path = std::filesystem::path(policy.root) /
                              "published-heads" /
                              "field-notes.signed-head";
  const auto guard_path = std::filesystem::path(policy.root) /
                          "rollback-guards" /
                          "field-notes.rollback-guard";
  auto first_published = iotox::StateStore::read(published_path);
  auto first_guard = iotox::StateStore::read(guard_path);
  passed = passed && first_published.ok() && first_guard.ok();

  passed = passed &&
           publish_in_fresh_process(policy, identity_path, 2U, true);
  auto second_published = iotox::StateStore::read(published_path);
  auto second_guard = iotox::StateStore::read(guard_path);
  passed = passed && second_published.ok() && second_guard.ok();

  if (passed) {
    passed = iotox::StateStore::write_atomic(published_path,
                                              first_published.value())
                 .ok() &&
             publish_in_fresh_process(policy, identity_path, 3U, false) &&
             iotox::StateStore::write_atomic(published_path,
                                              second_published.value())
                 .ok();
  }
  if (passed) {
    passed =
        iotox::StateStore::write_atomic(guard_path, first_guard.value()).ok() &&
        publish_in_fresh_process(policy, identity_path, 3U, false) &&
        iotox::StateStore::write_atomic(guard_path, second_guard.value()).ok();
  }
  passed = passed &&
           publish_in_fresh_process(policy, identity_path, 3U, true);
  SignedHeadStore store(policy.root);
  auto current = store.load(policy, crypto.value());
  passed = passed && current.ok() && current.value().has_value() &&
           current.value()->generation == 3U;

  cleanup();
  return passed ? 0 : 1;
}

} // namespace

int main() {
  const int status = run();
  if (status != 0)
    std::cerr << "cross-process sync rollback isolation failed\n";
  return status;
}
