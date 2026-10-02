#include "iotox/sync_attempt_store.hpp"
#include "iotox/sync_reconstruction.hpp"

#include "test_harness.hpp"

#include <filesystem>
#include <fstream>
#include <iterator>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-sync-attempt-store-XXXXXX";
    std::vector<char> bytes(pattern.begin(), pattern.end());
    bytes.push_back('\0');
    char *created = ::mkdtemp(bytes.data());
    if (created == nullptr) throw std::runtime_error("mkdtemp failed");
    path_ = created;
  }
  ~TempDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path_, ignored);
  }
  [[nodiscard]] const std::filesystem::path &path() const { return path_; }

private:
  std::filesystem::path path_;
};

iotox::security::Sodium sodium() {
  auto loaded = iotox::security::Sodium::load();
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::security::DeviceIdentity identity(
    const std::filesystem::path &path,
    const iotox::security::Sodium &crypto) {
  auto loaded = iotox::security::DeviceIdentity::load_or_create(
      path, crypto, true);
  if (!loaded) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

iotox::sync::Digest digest(std::uint8_t value) {
  iotox::sync::Digest result{};
  result[0U] = value;
  result[31U] = static_cast<std::uint8_t>(value ^ 0xa5U);
  return result;
}

iotox::routes::ToxPublicKey route(std::uint8_t value) {
  iotox::routes::ToxPublicKey result{};
  result.fill(value);
  return result;
}

iotox::sync::PrincipalId principal(std::uint8_t value) {
  iotox::sync::PrincipalId result{};
  result[0U] = value;
  return result;
}

iotox::sync::NamespacePolicy policy(const std::filesystem::path &root) {
  iotox::sync::NamespacePolicy result;
  result.id = "attempt-test";
  result.root = root.lexically_normal().string();
  result.writers = {principal(1U)};
  result.quotas.maximum_artifact_bytes = 4096U;
  result.quotas.maximum_manifest_bytes = 1024U;
  result.quotas.maximum_store_bytes = 8192U;
  result.quotas.maximum_staging_bytes = 4096U;
  result.quotas.maximum_outstanding_requests = 4U;
  return result;
}

iotox::sync::DurableSyncAttempt attempt(std::uint64_t id,
                                        std::uint8_t value) {
  return iotox::sync::DurableSyncAttempt{
      id,
      {value % 2U == 0U ? iotox::sync::SyncObjectKind::manifest
                        : iotox::sync::SyncObjectKind::artifact,
       digest(value), 100U + value},
      route(static_cast<std::uint8_t>(0x20U + value)),
      1000U + value};
}

void overwrite(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(reinterpret_cast<const char *>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
  if (!output) throw std::runtime_error("unable to overwrite attempt state");
}

std::vector<std::uint8_t> read_all(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return std::vector<std::uint8_t>(std::istreambuf_iterator<char>(input),
                                   std::istreambuf_iterator<char>());
}

iotox::Result<iotox::sync::Digest>
hash_fixture(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    return iotox::Status{iotox::ErrorCode::io_error,
                         "unable to hash attempt fixture"};
  }
  std::string bytes;
  std::getline(input, bytes, '\0');
  if (!input.eof()) {
    return iotox::Status{iotox::ErrorCode::io_error,
                         "unable to read attempt fixture"};
  }
  if (bytes == "payload") return digest(0x41U);
  if (bytes == "another") return digest(0x42U);
  return digest(0xeeU);
}

iotox::sync::SyncInstallSeams install_seams() {
  iotox::sync::SyncInstallSeams result;
  result.hash_file = hash_fixture;
  result.cancel_requested = [] { return false; };
  return result;
}

void write_private(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary);
  output << text;
  if (!output) throw std::runtime_error("unable to write attempt fixture");
  output.close();
  std::filesystem::permissions(
      path, std::filesystem::perms::owner_read |
                std::filesystem::perms::owner_write,
      std::filesystem::perm_options::replace);
}

} // namespace

IOTOX_TEST("sync attempt journal has one canonical bounded signed encoding") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  iotox::sync::SyncAttemptJournal journal;
  journal.namespace_id = "attempt-test";
  journal.high_attempt_id = 2U;
  journal.active = {attempt(1U, 1U), attempt(2U, 2U)};
  journal.signer = device.public_key();
  journal.mutation = 1U;
  auto unsigned_record = iotox::sync::encode_sync_attempt_journal(journal);
  IOTOX_CHECK(unsigned_record.ok());
  auto signing_digest = crypto.hash(
      "iotox-sync-attempt-journal-signature-v1",
      std::span<const std::uint8_t>(unsigned_record.value())
          .first(unsigned_record.value().size() -
                 iotox::security::kSignatureBytes));
  IOTOX_CHECK(signing_digest.ok());
  auto signature = device.sign(signing_digest.value());
  IOTOX_CHECK(signature.ok());
  journal.signature = signature.value();
  auto encoded = iotox::sync::encode_sync_attempt_journal(journal);
  IOTOX_CHECK(encoded.ok() && encoded.value().size() == 448U);
  auto decoded =
      iotox::sync::decode_sync_attempt_journal(encoded.value(), 2U);
  IOTOX_CHECK(decoded.ok() && decoded.value() == journal);
  IOTOX_CHECK(iotox::sync::verify_sync_attempt_journal(
                  decoded.value(), device.public_key(),
                  policy(temporary.path() / "sync"), crypto, 2U)
                  .ok());
  auto changed = encoded.value();
  changed[9U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_attempt_journal(changed, 2U).ok());
  changed = encoded.value();
  changed[203U] = 1U;
  IOTOX_CHECK(!iotox::sync::decode_sync_attempt_journal(changed, 2U).ok());
  IOTOX_CHECK(
      !iotox::sync::decode_sync_attempt_journal(encoded.value(), 1U).ok());
}

IOTOX_TEST("sync attempt store burns ids and retains only exact active work") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  const auto configured = policy(temporary.path() / "sync");
  iotox::sync::SyncAttemptStore store(configured.root);
  auto first_id = store.reserve_attempt_id(configured, device, crypto);
  auto second_id = store.reserve_attempt_id(configured, device, crypto);
  IOTOX_CHECK(first_id.ok() && first_id.value() == 1U);
  IOTOX_CHECK(second_id.ok() && second_id.value() == 2U);
  const auto first = attempt(first_id.value(), 1U);
  const auto second = attempt(second_id.value(), 2U);
  auto begun = store.begin(configured, first, device, crypto);
  IOTOX_CHECK(begun.ok() &&
              begun.value() == iotox::sync::SyncAttemptBegin::inserted);
  begun = store.begin(configured, first, device, crypto);
  IOTOX_CHECK(begun.ok() &&
              begun.value() == iotox::sync::SyncAttemptBegin::duplicate);
  IOTOX_CHECK(store.begin(configured, second, device, crypto).ok());
  auto loaded = iotox::sync::SyncAttemptStore(configured.root).load(
      configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value().high_attempt_id == 2U);
  const std::vector<iotox::sync::DurableSyncAttempt> expected{first, second};
  IOTOX_CHECK(loaded.value().active == expected);
  auto finished = store.finish(configured, first, device, crypto);
  IOTOX_CHECK(finished.ok() && finished.value());
  finished = store.finish(configured, first, device, crypto);
  IOTOX_CHECK(finished.ok() && !finished.value());
  loaded = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(loaded.ok() && loaded.value().active.size() == 1U);
  IOTOX_CHECK(loaded.value().active.front() == second);
  auto third_id = iotox::sync::SyncAttemptStore(configured.root)
                      .reserve_attempt_id(configured, device, crypto);
  IOTOX_CHECK(third_id.ok() && third_id.value() == 3U);
  IOTOX_CHECK(!store.begin(configured, attempt(4U, 4U), device, crypto).ok());
}

IOTOX_TEST("sync attempt store refuses conflicts capacity tampering and foreign devices") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto foreign = identity(temporary.path() / "foreign.identity", crypto);
  auto configured = policy(temporary.path() / "sync");
  iotox::sync::SyncAttemptStore::Config bounds;
  bounds.maximum_active_attempts = 1U;
  iotox::sync::SyncAttemptStore store(configured.root, bounds);
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  auto first = attempt(1U, 1U);
  IOTOX_CHECK(store.begin(configured, first, device, crypto).ok());
  auto conflict = first;
  conflict.worker_id += 1U;
  IOTOX_CHECK(!store.begin(configured, conflict, device, crypto).ok());
  IOTOX_CHECK(!store.begin(configured, attempt(2U, 2U), device, crypto).ok());
  IOTOX_CHECK(!store.load(configured, foreign.public_key(), crypto).ok());

  const auto path = std::filesystem::path(configured.root) / "attempts" /
                    "attempt-test.active-attempts";
  auto bytes = read_all(path);
  bytes[48U] ^= 1U;
  overwrite(path, bytes);
  IOTOX_CHECK(!store.load(configured, device.public_key(), crypto).ok());
  IOTOX_CHECK(!store.reserve_attempt_id(configured, device, crypto).ok());
}

IOTOX_TEST("sync attempt recovery commits complete staging retains a positive prefix and fences debris") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto configured = policy(temporary.path() / "sync");
  iotox::sync::SyncAttemptStore store(configured.root);
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  auto complete = attempt(1U, 1U);
  complete.object = {iotox::sync::SyncObjectKind::artifact,
                     digest(0x41U), 7U};
  auto absent = attempt(2U, 2U);
  absent.object = {iotox::sync::SyncObjectKind::manifest,
                   digest(0x42U), 7U};
  auto corrupt = attempt(3U, 3U);
  corrupt.object = {iotox::sync::SyncObjectKind::artifact,
                    digest(0x43U), 7U};
  auto retained = attempt(4U, 4U);
  retained.object = {iotox::sync::SyncObjectKind::manifest,
                     digest(0x44U), 7U};
  IOTOX_CHECK(store.begin(configured, complete, device, crypto).ok());
  IOTOX_CHECK(store.begin(configured, absent, device, crypto).ok());
  IOTOX_CHECK(store.begin(configured, corrupt, device, crypto).ok());
  IOTOX_CHECK(store.begin(configured, retained, device, crypto).ok());
  std::filesystem::path complete_staging;
  std::filesystem::path corrupt_staging;
  std::filesystem::path absent_transport_staging;
  std::filesystem::path retained_staging;
  std::filesystem::path inactive_staging;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto complete_path = iotox::sync::prepare_sync_attempt_staging(
        configured, complete.attempt_id, complete.object,
        transaction.value());
    auto corrupt_path = iotox::sync::prepare_sync_attempt_staging(
        configured, corrupt.attempt_id, corrupt.object,
        transaction.value());
    IOTOX_CHECK(complete_path.ok() && corrupt_path.ok());
    complete_staging = complete_path.value();
    corrupt_staging = corrupt_path.value();
    absent_transport_staging =
        std::filesystem::path(configured.root) / "staging" /
        ".iotox-attempt-0000000000000002.part.part-Ab12Cd";
    write_private(complete_staging, "payload");
    write_private(corrupt_staging, "xxxxxxx");
    write_private(absent_transport_staging, "partial");
    auto retained_path = iotox::sync::create_sync_attempt_partial(
        configured, retained.attempt_id, retained.object,
        transaction.value());
    IOTOX_CHECK(retained_path.ok());
    retained_staging = retained_path.value().path;
    write_private(retained_staging, "part");
    auto inactive = iotox::sync::create_sync_attempt_partial(
        configured, 5U, attempt(5U, 5U).object,
        transaction.value());
    IOTOX_CHECK(inactive.ok());
    inactive_staging = inactive.value().path;
    write_private(inactive_staging, "orphan");
  }
  auto recovered = iotox::sync::SyncAttemptStore(configured.root).recover(
      configured, device, crypto, install_seams());
  IOTOX_CHECK(recovered.ok() && recovered.value().size() == 4U);
  IOTOX_CHECK(recovered.value()[0U].disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::committed);
  IOTOX_CHECK(recovered.value()[1U].disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(recovered.value()[2U].disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(recovered.value()[3U].disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::retained);
  IOTOX_CHECK(!std::filesystem::exists(complete_staging));
  IOTOX_CHECK(!std::filesystem::exists(corrupt_staging));
  IOTOX_CHECK(!std::filesystem::exists(absent_transport_staging));
  IOTOX_CHECK(std::filesystem::exists(retained_staging));
  IOTOX_CHECK(std::filesystem::file_size(retained_staging) == 4U);
  IOTOX_CHECK(!std::filesystem::exists(inactive_staging));
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().attempt_id == 4U);
  IOTOX_CHECK(journal.value().active.front().state ==
              iotox::sync::DurableSyncAttemptState::restart_retained);
  auto records = iotox::sync::inspect_sync_object_records(configured);
  IOTOX_CHECK(records.ok() && records.value().size() == 1U);
  IOTOX_CHECK(records.value().front() == complete.object);
  auto duplicate = store.recover(
      configured, device, crypto, install_seams());
  IOTOX_CHECK(duplicate.ok() && duplicate.value().size() == 1U);
  IOTOX_CHECK(duplicate.value().front().disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::retained);
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto fenced = store.fence_retained_except(
        configured, std::span<const iotox::sync::SyncObjectRecord>{},
        device, crypto, transaction.value());
    IOTOX_CHECK(fenced.ok() && fenced.value() == 1U);
  }
  IOTOX_CHECK(!std::filesystem::exists(retained_staging));
  journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
}

IOTOX_TEST("sync attempt recovery refuses linked transport temporaries") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto configured = policy(temporary.path() / "sync");
  iotox::sync::SyncAttemptStore store(configured.root);
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  const auto active = attempt(1U, 1U);
  IOTOX_CHECK(store.begin(configured, active, device, crypto).ok());
  const auto staging = std::filesystem::path(configured.root) / "staging";
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::prepare_sync_attempt_staging(
                    configured, active.attempt_id, active.object,
                    transaction.value())
                    .ok());
  }
  const auto transport =
      staging / ".iotox-attempt-0000000000000001.part.part-aB3xY9";
  const auto linked = staging / "linked-transport-part";
  write_private(transport, "partial");
  std::filesystem::create_hard_link(transport, linked);
  auto recovered = store.recover(
      configured, device, crypto, install_seams());
  IOTOX_CHECK(!recovered.ok());
  IOTOX_CHECK(std::filesystem::exists(transport));
  IOTOX_CHECK(std::filesystem::exists(linked));
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
}

IOTOX_TEST("sync attempt recovery retains only an exact plan-bound range prefix") {
  TempDirectory temporary;
  auto crypto = sodium();
  auto device = identity(temporary.path() / "device.identity", crypto);
  auto configured = policy(temporary.path() / "sync");
  iotox::sync::SyncAttemptStore store(configured.root);
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  IOTOX_CHECK(store.reserve_attempt_id(configured, device, crypto).ok());
  iotox::sync::SyncRangePlan plan;
  plan.target = {iotox::sync::SyncObjectKind::artifact,
                 digest(0x61U), 7U};
  plan.manifest = {iotox::sync::SyncObjectKind::manifest,
                   digest(0x62U), 64U};
  plan.basis = {iotox::sync::SyncObjectKind::artifact,
                digest(0x63U), 7U};
  plan.block_bytes = 7U;
  plan.blocks = 1U;
  plan.basis_bytes = 7U;
  plan.reused_bytes = 3U;
  plan.missing_bytes = 4U;
  plan.basis_offsets = {0U};
  plan.missing_ranges = {{3U, 4U}};
  auto made = iotox::sync::make_durable_range_attempt(
      1U, plan, iotox::sync::DurableSyncAttemptState::active, crypto);
  IOTOX_CHECK(made.ok());
  const auto range = made.value();
  IOTOX_CHECK(store.begin(configured, range, device, crypto).ok());
  auto legacy_range = attempt(2U, 2U);
  legacy_range.object = {iotox::sync::SyncObjectKind::artifact,
                         digest(0x64U), 7U};
  legacy_range.mode = iotox::sync::DurableSyncAttemptMode::range_bundle;
  IOTOX_CHECK(store.begin(
                  configured, legacy_range, device, crypto).ok());
  std::filesystem::path staging;
  std::filesystem::path legacy_staging;
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto partial = iotox::sync::create_sync_attempt_partial(
        configured, range.attempt_id, range.object,
        transaction.value());
    IOTOX_CHECK(partial.ok());
    staging = partial.value().path;
    write_private(staging, "pay");
    auto legacy_partial = iotox::sync::create_sync_attempt_partial(
        configured, legacy_range.attempt_id, legacy_range.object,
        transaction.value());
    IOTOX_CHECK(legacy_partial.ok());
    legacy_staging = legacy_partial.value().path;
    write_private(legacy_staging, "old");
  }
  auto recovered = store.recover(
      configured, device, crypto, install_seams());
  IOTOX_CHECK(recovered.ok() && recovered.value().size() == 2U);
  IOTOX_CHECK(recovered.value().front().disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::retained);
  IOTOX_CHECK(recovered.value().back().disposition ==
              iotox::sync::SyncAttemptRecoveryDisposition::fenced);
  IOTOX_CHECK(std::filesystem::exists(staging));
  IOTOX_CHECK(!std::filesystem::exists(legacy_staging));
  auto journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.size() == 1U);
  IOTOX_CHECK(journal.value().active.front().state ==
              iotox::sync::DurableSyncAttemptState::restart_retained);
  auto commitment = iotox::sync::sync_range_plan_commitment(plan, crypto);
  IOTOX_CHECK(commitment.ok());
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto exact = store.retained_range_attempt(
        configured, plan.target, commitment.value(), plan.missing_bytes,
        device.public_key(), crypto, transaction.value());
    IOTOX_CHECK(exact.ok() && exact.value().has_value());
  }

  auto changed = plan;
  changed.basis.identity[0U] ^= 0x80U;
  auto changed_commitment =
      iotox::sync::sync_range_plan_commitment(changed, crypto);
  IOTOX_CHECK(changed_commitment.ok());
  IOTOX_CHECK(changed_commitment.value() != commitment.value());
  {
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(configured);
    IOTOX_CHECK(transaction.ok());
    auto fenced = store.fence_retained_ranges_except(
        configured, plan.target, changed_commitment.value(),
        changed.missing_bytes, device, crypto, transaction.value());
    IOTOX_CHECK(fenced.ok() && fenced.value() == 1U);
  }
  IOTOX_CHECK(!std::filesystem::exists(staging));
  journal = store.load(configured, device.public_key(), crypto);
  IOTOX_CHECK(journal.ok() && journal.value().active.empty());
}

IOTOX_TEST("sync range plan commitment is bounded and exact beyond one hash payload") {
  auto crypto = sodium();
  iotox::sync::SyncRangePlan plan;
  plan.target = {iotox::sync::SyncObjectKind::artifact,
                 digest(0x71U), 65536U};
  plan.manifest = {iotox::sync::SyncObjectKind::manifest,
                   digest(0x72U), 65536U};
  plan.basis = {iotox::sync::SyncObjectKind::artifact,
                digest(0x73U), 65536U};
  plan.block_bytes = 8U;
  plan.blocks = 8192U;
  plan.basis_bytes = 65536U;
  plan.reused_bytes = 65535U;
  plan.missing_bytes = 1U;
  plan.basis_offsets.resize(8192U);
  for (std::size_t index = 0U; index < plan.basis_offsets.size(); ++index) {
    plan.basis_offsets[index] = index * 8U;
  }
  plan.basis_offsets.back() = std::numeric_limits<std::uint64_t>::max();
  plan.missing_ranges = {{65535U, 1U}};

  auto commitment = iotox::sync::sync_range_plan_commitment(plan, crypto);
  IOTOX_CHECK_MSG(commitment.ok(), commitment.status().message());
  auto repeated = iotox::sync::sync_range_plan_commitment(plan, crypto);
  IOTOX_CHECK(repeated.ok() && repeated.value() == commitment.value());

  auto changed = plan;
  changed.basis_offsets[4096U] ^= 1U;
  auto changed_commitment =
      iotox::sync::sync_range_plan_commitment(changed, crypto);
  IOTOX_CHECK(changed_commitment.ok());
  IOTOX_CHECK(changed_commitment.value() != commitment.value());
}
