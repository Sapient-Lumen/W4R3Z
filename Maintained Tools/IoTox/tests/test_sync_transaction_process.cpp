#include "iotox/security/identity.hpp"
#include "iotox/sync_publication.hpp"
#include "iotox/sync_retention.hpp"
#include "iotox/sync_transaction.hpp"

#include <cerrno>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <poll.h>
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
using iotox::sync::SignedHeadPublicationRequest;
using iotox::sync::SignedHeadStore;
using iotox::sync::SyncNamespaceTransaction;

Digest digest(std::uint8_t value) {
  Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

bool write_byte(int descriptor, char value) {
  ssize_t result = -1;
  do {
    result = ::write(descriptor, &value, 1U);
  } while (result < 0 && errno == EINTR);
  return result == 1;
}

bool read_byte(int descriptor, char &value) {
  ssize_t result = -1;
  do {
    result = ::read(descriptor, &value, 1U);
  } while (result < 0 && errno == EINTR);
  return result == 1;
}

int run() {
  std::string pattern = "/tmp/iotox-sync-transaction-process-XXXXXX";
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
  NamespacePolicy policy;
  policy.id = "field-notes";
  policy.root = (temporary / "sync").lexically_normal().string();
  policy.engine = Engine::range_v1;
  policy.writers = {parent_identity.value().public_key()};
  policy.quotas.maximum_artifact_bytes = 4096U;
  policy.quotas.maximum_manifest_bytes = 1024U;

  int start_pipe[2] = {-1, -1};
  int result_pipe[2] = {-1, -1};
  if (::pipe(start_pipe) != 0 || ::pipe(result_pipe) != 0) {
    cleanup();
    return 1;
  }
  const pid_t child = ::fork();
  if (child < 0) {
    cleanup();
    return 1;
  }
  if (child == 0) {
    static_cast<void>(::close(start_pipe[1]));
    static_cast<void>(::close(result_pipe[0]));
    auto crypto = Sodium::load();
    if (!crypto.ok())
      ::_exit(1);
    auto identity = DeviceIdentity::load(identity_path, crypto.value());
    if (!identity.ok() || !write_byte(result_pipe[1], 'R')) {
      ::_exit(1);
    }
    char start = 0;
    if (!read_byte(start_pipe[0], start) || start != 'G')
      ::_exit(1);
    if (!write_byte(result_pipe[1], 'A'))
      ::_exit(1);
    SignedHeadStore publisher(policy.root);
    SignedHeadPublicationRequest request{digest(1U), digest(33U), 101U, 21U};
    auto published =
        publisher.publish(policy, request, identity.value(), crypto.value());
    if (!published.ok())
      ::_exit(1);
    AcceptedHead retained;
    retained.namespace_id = policy.id;
    retained.writer = identity.value().public_key();
    retained.engine = policy.engine;
    retained.generation = published.value().head.generation;
    auto record = iotox::sync::signed_head_record_digest(
        published.value().head, crypto.value());
    if (!record.ok())
      ::_exit(1);
    retained.record = record.value();
    retained.parent = published.value().head.parent;
    retained.artifact = published.value().head.artifact;
    retained.manifest = published.value().head.manifest;
    retained.artifact_bytes = published.value().head.artifact_bytes;
    retained.manifest_bytes = published.value().head.manifest_bytes;
    RetentionStore retention(policy.root);
    auto pinned =
        retention.pin(policy, retained, identity.value(), crypto.value());
    if (!pinned.ok() || !write_byte(result_pipe[1], 'D'))
      ::_exit(1);
    ::_exit(0);
  }

  static_cast<void>(::close(start_pipe[0]));
  static_cast<void>(::close(result_pipe[1]));
  bool passed = true;
  char signal = 0;
  passed = read_byte(result_pipe[0], signal) && signal == 'R';
  if (passed) {
    {
      auto held = SyncNamespaceTransaction::acquire(policy);
      passed = held.ok() && write_byte(start_pipe[1], 'G');
      passed = passed && read_byte(result_pipe[0], signal) && signal == 'A';
      pollfd waiting{result_pipe[0], POLLIN, 0};
      const int early = ::poll(&waiting, 1U, 150);
      passed = passed && early == 0;
    }
    pollfd waiting{result_pipe[0], POLLIN, 0};
    const int completed = ::poll(&waiting, 1U, 5000);
    passed = passed && completed == 1 && (waiting.revents & POLLIN) != 0 &&
             read_byte(result_pipe[0], signal) && signal == 'D';
  }
  static_cast<void>(::close(start_pipe[1]));
  static_cast<void>(::close(result_pipe[0]));
  int status = 0;
  passed = ::waitpid(child, &status, 0) == child && WIFEXITED(status) &&
           WEXITSTATUS(status) == 0 && passed;

  SignedHeadStore publisher(policy.root);
  auto published = publisher.load(policy, parent_crypto.value());
  RetentionStore retention(policy.root);
  auto retained = retention.load(policy, parent_identity.value().public_key(),
                                  parent_crypto.value());
  passed = passed && published.ok() && published.value().has_value() &&
           retained.ok() && retained.value().revisions.size() == 1U;
  {
    auto held = SyncNamespaceTransaction::acquire(policy);
    passed = passed && held.ok();
    const pid_t inherited = held.ok() ? ::fork() : -1;
    if (inherited == 0)
      ::_exit(held.value().matches(policy) ? 1 : 0);
    int inherited_status = 0;
    passed = passed && inherited > 0 &&
             ::waitpid(inherited, &inherited_status, 0) == inherited &&
             WIFEXITED(inherited_status) && WEXITSTATUS(inherited_status) == 0;
  }
  cleanup();
  return passed ? 0 : 1;
}

} // namespace

int main() {
  const int status = run();
  if (status != 0)
    std::cerr << "shared sync transaction exclusion failed\n";
  return status;
}
