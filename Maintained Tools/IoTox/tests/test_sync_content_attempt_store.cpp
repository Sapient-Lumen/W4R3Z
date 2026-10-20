#include "iotox/sync_content_attempt_store.hpp"
#include "iotox/sync_digest.hpp"

#include "test_harness.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-content-attempt-XXXXXX";
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

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity
identity(const std::filesystem::path &path,
         const iotox::security::Sodium &crypto) {
  auto loaded =
      iotox::security::DeviceIdentity::load_or_create(path, crypto, true);
  if (!loaded)
    throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

iotox::sync::PrincipalId principal(std::uint8_t value) {
  iotox::sync::PrincipalId result{};
  result[0U] = value;
  return result;
}

iotox::routes::ToxPublicKey route(std::uint8_t value) {
  iotox::routes::ToxPublicKey result{};
  result.fill(value);
  return result;
}

iotox::FileId file_id(std::uint8_t value) {
  iotox::FileId result{};
  result.fill(value);
  return result;
}

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root) {
  iotox::sync::NamespacePolicy result;
  result.id = "content-attempt-test";
  result.root = root.lexically_normal().string();
  result.engine = iotox::sync::Engine::content_v2;
  result.activation = iotox::sync::ActivationMode::manual;
  result.quotas.maximum_artifact_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_manifest_bytes = 128U * 1024U;
  result.quotas.maximum_staging_bytes = 2U * 1024U * 1024U;
  result.quotas.maximum_store_bytes = 8U * 1024U * 1024U;
  result.quotas.maximum_objects = 128U;
  result.quotas.maximum_outstanding_requests = 4U;
  result.writers = {principal(1U)};
  result.subscribers = {principal(2U)};
  return result;
}

iotox::sync::DurableSyncContentAttempt
attempt(std::uint64_t id, std::uint8_t value, const iotox::sync::Digest &object,
        std::uint64_t object_bytes) {
  iotox::sync::DurableSyncContentAttempt result;
  result.attempt_id = id;
  result.request_id = 1000U + id;
  result.source_id = 2000U + id;
  result.head_record = digest(static_cast<std::uint8_t>(0x40U + value));
  result.kind = iotox::sync::SyncContentObjectKind::artifact_chunk;
  result.logical_index = id - 1U;
  result.object = object;
  result.object_bytes = object_bytes;
  result.file_id = file_id(static_cast<std::uint8_t>(0x50U + value));
  result.carrier.carrier_class = iotox::sync::SyncCarrierClass::primary;
  result.carrier.route_key = route(static_cast<std::uint8_t>(0x60U + value));
  result.carrier.worker_id = 3000U + id;
  result.carrier.friend_number = static_cast<std::uint32_t>(10U + id);
  result.carrier.online_epoch = result.carrier.worker_id;
  result.source_principal = principal(static_cast<std::uint8_t>(0x70U + value));
  return result;
}

void write_private(const std::filesystem::path &path, std::string_view bytes) {
  std::filesystem::create_directories(path.parent_path());
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("content staging write failed");
  output.close();
  if (::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0) {
    throw std::runtime_error("content staging chmod failed");
  }
}

std::vector<std::uint8_t> read_all(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return std::vector<std::uint8_t>(std::istreambuf_iterator<char>(input),
                                   std::istreambuf_iterator<char>());
}

void overwrite(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output)
    throw std::runtime_error("journal overwrite failed");
}

} // namespace

IOTOX_TEST("content attempt journal freezes one canonical signed binding") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncContentAttemptJournal journal;
  journal.namespace_id = configured.id;
  journal.high_attempt_id = 2U;
  journal.active = {attempt(1U, 1U, digest(1U), 4096U),
                    attempt(2U, 2U, digest(2U), 8192U)};
  journal.signer = device.public_key();
  journal.mutation = 1U;
  auto unsigned_record =
      iotox::sync::encode_sync_content_attempt_journal(journal);
  IOTOX_CHECK(unsigned_record.ok());
  auto signing_digest =
      crypto.hash("iotox-sync-content-attempt-signature-v1",
                  std::span<const std::uint8_t>(unsigned_record.value())
                      .first(unsigned_record.value().size() -
                             iotox::security::kSignatureBytes));
  IOTOX_CHECK(signing_digest.ok());
  auto signature = device.sign(signing_digest.value());
  IOTOX_CHECK(signature.ok());
  journal.signature = signature.value();
  auto encoded = iotox::sync::encode_sync_content_attempt_journal(journal);
  IOTOX_CHECK(encoded.ok() && encoded.value().size() == 832U);
  auto decoded =
      iotox::sync::decode_sync_content_attempt_journal(encoded.value(), 2U);
  IOTOX_CHECK(decoded.ok() && decoded.value() == journal);
  IOTOX_CHECK(iotox::sync::verify_sync_content_attempt_journal(
                  decoded.value(), device.public_key(), configured, crypto, 2U)
                  .ok());
  auto malformed = encoded.value();
  malformed[192U + 10U] = 1U;
  IOTOX_CHECK(
      !iotox::sync::decode_sync_content_attempt_journal(malformed, 2U).ok());
  auto changed = journal;
  changed.active[0U].file_id[0U] ^= 1U;
  IOTOX_CHECK(!iotox::sync::verify_sync_content_attempt_journal(
                   changed, device.public_key(), configured, crypto, 2U)
                   .ok());
}

IOTOX_TEST("content attempt store burns ids deduplicates and refuses aliases") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  iotox::sync::SyncContentAttemptStore::Config limits;
  limits.maximum_active_attempts = 2U;
  iotox::sync::SyncContentAttemptStore store(configured.root, limits);
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  auto first_id =
      store.reserve_attempt_id(configured, device, crypto, transaction.value());
  auto second_id =
      store.reserve_attempt_id(configured, device, crypto, transaction.value());
  auto third_id =
      store.reserve_attempt_id(configured, device, crypto, transaction.value());
  IOTOX_CHECK(first_id.ok() && first_id.value() == 1U);
  IOTOX_CHECK(second_id.ok() && second_id.value() == 2U);
  IOTOX_CHECK(third_id.ok() && third_id.value() == 3U);
  const auto first = attempt(1U, 1U, digest(1U), 4096U);
  auto second = attempt(2U, 2U, digest(2U), 4096U);
  const auto third = attempt(3U, 3U, digest(3U), 4096U);
  auto begun =
      store.begin(configured, first, device, crypto, transaction.value());
  IOTOX_CHECK(begun.ok() &&
              begun.value() == iotox::sync::SyncContentAttemptBegin::inserted);
  begun = store.begin(configured, first, device, crypto, transaction.value());
  IOTOX_CHECK(begun.ok() &&
              begun.value() == iotox::sync::SyncContentAttemptBegin::duplicate);
  auto conflict = first;
  conflict.file_id[0U] ^= 1U;
  IOTOX_CHECK(
      !store.begin(configured, conflict, device, crypto, transaction.value())
           .ok());
  second.request_id = first.request_id;
  IOTOX_CHECK(
      !store.begin(configured, second, device, crypto, transaction.value())
           .ok());
  second = attempt(2U, 2U, digest(2U), 4096U);
  second.file_id = first.file_id;
  IOTOX_CHECK(
      !store.begin(configured, second, device, crypto, transaction.value())
           .ok());
  second = attempt(2U, 2U, digest(2U), 4096U);
  second.head_record = first.head_record;
  second.logical_index = first.logical_index;
  IOTOX_CHECK(
      !store.begin(configured, second, device, crypto, transaction.value())
           .ok());
  second = attempt(2U, 2U, digest(2U), 4096U);
  IOTOX_CHECK(
      store.begin(configured, second, device, crypto, transaction.value())
          .ok());
  auto capacity =
      store.begin(configured, third, device, crypto, transaction.value());
  IOTOX_CHECK(capacity.status().code() == iotox::ErrorCode::resource_exhausted);
  auto finished =
      store.finish(configured, first, device, crypto, transaction.value());
  IOTOX_CHECK(finished.ok() && finished.value());
  finished =
      store.finish(configured, first, device, crypto, transaction.value());
  IOTOX_CHECK(finished.ok() && !finished.value());
  auto loaded = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value().high_attempt_id == 3U);
  IOTOX_CHECK(loaded.value().active.size() == 1U &&
              loaded.value().active.front() == second);

  const auto journal_path = std::filesystem::path(configured.root) /
                            "content-attempts" /
                            (configured.id + ".active-content-attempts");
  auto bytes = read_all(journal_path);
  bytes[48U] ^= 1U;
  overwrite(journal_path, bytes);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
}

IOTOX_TEST(
    "content attempt staging path matches the frozen coordinator grammar") {
  const auto configured = policy("/tmp/iotox-content-attempt-path");
  const auto object = digest(0x91U);
  const auto path = iotox::sync::sync_content_attempt_staging_path(
      configured, object, 12345U);
  IOTOX_CHECK(path.parent_path().parent_path() ==
              iotox::sync::sync_content_staging_root(configured) / "objects");
  IOTOX_CHECK(path.filename().string().ends_with(".12345.part"));
  IOTOX_CHECK(path.filename().string().size() == 62U + 1U + 5U + 5U);
}

IOTOX_TEST(
    "content attempt recovery commits complete bytes and fences partial work") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  const auto complete_source = temporary.path() / "complete.bin";
  write_private(complete_source, "complete-content-object");
  auto complete_digest = iotox::sync::hash_sync_file_sha256(complete_source);
  IOTOX_CHECK(complete_digest.ok());
  const auto complete = attempt(1U, 1U, complete_digest.value(),
                                std::filesystem::file_size(complete_source));
  const auto partial = attempt(2U, 2U, digest(0xa2U), 64U);
  const auto absent = attempt(3U, 3U, digest(0xa3U), 64U);
  iotox::sync::SyncContentAttemptStore store(configured.root);
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  for (std::uint64_t expected = 1U; expected <= 3U; ++expected) {
    auto reserved = store.reserve_attempt_id(configured, device, crypto,
                                             transaction.value());
    IOTOX_CHECK(reserved.ok() && reserved.value() == expected);
  }
  IOTOX_CHECK(
      store.begin(configured, complete, device, crypto, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.begin(configured, partial, device, crypto, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.begin(configured, absent, device, crypto, transaction.value())
          .ok());
  const auto complete_staging = iotox::sync::sync_content_attempt_staging_path(
      configured, complete.object, complete.request_id);
  auto prepared = iotox::sync::prepare_sync_content_attempt_staging(
      configured, complete.object, complete.request_id, transaction.value());
  IOTOX_CHECK(prepared.ok() && prepared.value() == complete_staging);
  std::filesystem::copy_file(complete_source, complete_staging);
  IOTOX_CHECK(::chmod(complete_staging.c_str(), static_cast<mode_t>(0600)) ==
              0);
  const auto partial_staging = iotox::sync::sync_content_attempt_staging_path(
      configured, partial.object, partial.request_id);
  prepared = iotox::sync::prepare_sync_content_attempt_staging(
      configured, partial.object, partial.request_id, transaction.value());
  IOTOX_CHECK(prepared.ok() && prepared.value() == partial_staging);
  write_private(partial_staging, "partial");
  const auto transport_temporary =
      complete_staging.parent_path() /
      (".iotox-" + complete_staging.filename().string() + ".part-Ab12z9");
  write_private(transport_temporary, "transport-prefix");
  iotox::sync::SyncContentCommitConfig commit_config;
  commit_config.io_buffer_bytes = 4096U;
  commit_config.fsync_on_commit = false;
  auto recovered = store.recover(configured, device, crypto,
                                 transaction.value(), commit_config);
  IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
  IOTOX_CHECK(recovered.value().size() == 3U);
  IOTOX_CHECK(recovered.value()[0U].disposition ==
              iotox::sync::SyncContentAttemptRecoveryDisposition::committed);
  IOTOX_CHECK(recovered.value()[1U].disposition ==
              iotox::sync::SyncContentAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(recovered.value()[2U].disposition ==
              iotox::sync::SyncContentAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(!std::filesystem::exists(complete_staging));
  IOTOX_CHECK(!std::filesystem::exists(partial_staging));
  IOTOX_CHECK(!std::filesystem::exists(transport_temporary));
  auto inventory = iotox::sync::inspect_sync_content_store(
      configured, transaction.value(), true);
  IOTOX_CHECK(inventory.ok() && inventory.value().objects == 1U);
  IOTOX_CHECK(inventory.value().records.front().object == complete.object);
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
  IOTOX_CHECK(journal.value().high_attempt_id == 3U);
  auto repeated = store.recover(configured, device, crypto, transaction.value(),
                                commit_config);
  IOTOX_CHECK(repeated.ok() && repeated.value().empty());
}

IOTOX_TEST(
    "content attempt recovery rejects unsafe transport temporary shape") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  const auto active = attempt(1U, 1U, digest(0xa4U), 64U);
  iotox::sync::SyncContentAttemptStore store(configured.root);
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.reserve_attempt_id(configured, device, crypto, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.begin(configured, active, device, crypto, transaction.value())
          .ok());
  const auto staging = iotox::sync::sync_content_attempt_staging_path(
      configured, active.object, active.request_id);
  auto prepared = iotox::sync::prepare_sync_content_attempt_staging(
      configured, active.object, active.request_id, transaction.value());
  IOTOX_CHECK(prepared.ok() && prepared.value() == staging);
  const auto transport_temporary =
      staging.parent_path() /
      (".iotox-" + staging.filename().string() + ".part-0aZ9xQ");
  write_private(transport_temporary, "private-prefix");
  IOTOX_CHECK(::chmod(transport_temporary.c_str(), static_cast<mode_t>(0644)) ==
              0);
  iotox::sync::SyncContentCommitConfig commit_config;
  commit_config.fsync_on_commit = false;
  auto recovered = store.recover(configured, device, crypto,
                                 transaction.value(), commit_config);
  IOTOX_CHECK(!recovered.ok());
  IOTOX_CHECK(std::filesystem::exists(transport_temporary));
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);

  IOTOX_CHECK(::chmod(transport_temporary.c_str(), static_cast<mode_t>(0600)) ==
              0);
  recovered = store.recover(configured, device, crypto, transaction.value(),
                            commit_config);
  IOTOX_CHECK(recovered.ok() && recovered.value().size() == 1U);
  IOTOX_CHECK(recovered.value().front().disposition ==
              iotox::sync::SyncContentAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(!std::filesystem::exists(transport_temporary));
  journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
}

IOTOX_TEST("content attempt recovery refuses ambiguous complete staging") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "namespace");
  const auto active = attempt(1U, 1U, digest(0xb1U), 8U);
  iotox::sync::SyncContentAttemptStore store(configured.root);
  auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(configured);
  IOTOX_CHECK(transaction.ok());
  IOTOX_CHECK(
      iotox::sync::prepare_sync_content_staging(configured, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.reserve_attempt_id(configured, device, crypto, transaction.value())
          .ok());
  IOTOX_CHECK(
      store.begin(configured, active, device, crypto, transaction.value())
          .ok());
  const auto staging = iotox::sync::sync_content_attempt_staging_path(
      configured, active.object, active.request_id);
  write_private(staging, "12345678");
  const auto alias = temporary.path() / "linked";
  std::filesystem::create_hard_link(staging, alias);
  iotox::sync::SyncContentCommitConfig commit_config;
  commit_config.fsync_on_commit = false;
  auto recovered = store.recover(configured, device, crypto,
                                 transaction.value(), commit_config);
  IOTOX_CHECK(!recovered.ok());
  IOTOX_CHECK(std::filesystem::exists(staging));
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  std::filesystem::remove(alias);
  recovered = store.recover(configured, device, crypto, transaction.value(),
                            commit_config);
  IOTOX_CHECK(!recovered.ok());
  IOTOX_CHECK(std::filesystem::exists(staging));
  journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
}
