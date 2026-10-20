#include "test_harness.hpp"

#include "iotox/security/identity.hpp"
#include "iotox/state_store.hpp"
#include "iotox/update_bundle.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::update::SignedUpdateManifest;
using iotox::update::UpdatePolicy;

class TempDirectory {
public:
  TempDirectory() {
    std::string pattern = "/tmp/iotox-update-bundle-XXXXXX";
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

Sodium sodium() {
  auto loaded = Sodium::load();
  if (!loaded.ok()) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

DeviceIdentity release_identity(const std::filesystem::path &path,
                                const Sodium &crypto) {
  auto loaded = DeviceIdentity::create_new_release(path, crypto);
  if (!loaded.ok()) throw std::runtime_error(loaded.status().message());
  return std::move(loaded).value();
}

void write_private(const std::filesystem::path &path, std::string_view text) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output.write(text.data(), static_cast<std::streamsize>(text.size()));
  if (!output) throw std::runtime_error("write fixture failed");
  output.close();
  if (::chmod(path.c_str(), 0600) != 0)
    throw std::runtime_error("chmod fixture failed");
}

UpdatePolicy policy(const TempDirectory &temporary,
                    const DeviceIdentity &signer) {
  UpdatePolicy result;
  result.namespace_id = "system-image";
  result.target = "iotox-sandwurm-x86_64";
  result.root = temporary.path() / "slots";
  result.maximum_payload_bytes = 1024U * 1024U;
  result.health_timeout_ms = 5000U;
  result.trusted_signers = {signer.public_key()};
  return result;
}

std::vector<std::uint8_t> read_all(const std::filesystem::path &path) {
  auto bytes = iotox::StateStore::read(path);
  if (!bytes.ok()) throw std::runtime_error(bytes.status().message());
  return std::move(bytes).value();
}

void write_all(const std::filesystem::path &path,
               const std::vector<std::uint8_t> &bytes) {
  const iotox::Status stored = iotox::StateStore::write_atomic(path, bytes);
  if (!stored.ok()) throw std::runtime_error(stored.message());
}

} // namespace

IOTOX_TEST("signed update manifest codec is canonical and policy bound") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "signer.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  IOTOX_CHECK(iotox::update::validate_update_policy(configured).ok());

  SignedUpdateManifest manifest;
  manifest.release_sequence = 7U;
  manifest.payload_bytes = 4096U;
  manifest.payload_digest[0U] = 1U;
  manifest.signer = signer.public_key();
  manifest.namespace_id = configured.namespace_id;
  manifest.target = configured.target;
  manifest.version = "7.0.0-rc1";
  auto body = iotox::update::encode_update_manifest_body(manifest);
  IOTOX_CHECK(body.ok());
  auto digest = crypto.hash("iotox-update-manifest-signature-v1",
                            body.value());
  IOTOX_CHECK(digest.ok());
  auto signature = signer.sign(digest.value());
  IOTOX_CHECK(signature.ok());
  manifest.signature = signature.value();
  auto encoded = iotox::update::encode_signed_update_manifest(manifest);
  IOTOX_CHECK(encoded.ok());
  IOTOX_CHECK(encoded.value().size() ==
              iotox::update::kSignedUpdateManifestBytes);
  auto decoded =
      iotox::update::decode_signed_update_manifest(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == manifest);
  IOTOX_CHECK(iotox::update::verify_signed_update_manifest(
                  configured, decoded.value(), crypto)
                  .ok());

  auto changed = encoded.value();
  changed[10U] = 1U;
  IOTOX_CHECK(!iotox::update::decode_signed_update_manifest(changed).ok());
  changed = encoded.value();
  changed[159U] = 1U;
  IOTOX_CHECK(!iotox::update::decode_signed_update_manifest(changed).ok());
  changed = encoded.value();
  changed[33U] ^= 1U;
  auto changed_manifest =
      iotox::update::decode_signed_update_manifest(changed);
  IOTOX_CHECK(changed_manifest.ok());
  IOTOX_CHECK(!iotox::update::verify_signed_update_manifest(
                   configured, changed_manifest.value(), crypto)
                   .ok());

  UpdatePolicy wrong_target = configured;
  wrong_target.target = "another-target";
  IOTOX_CHECK(!iotox::update::verify_signed_update_manifest(
                   wrong_target, manifest, crypto)
                   .ok());
}

IOTOX_TEST("signed update policy v2 freezes release signer revocation") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity active =
      release_identity(temporary.path() / "active.identity", crypto);
  DeviceIdentity retired =
      release_identity(temporary.path() / "retired.identity", crypto);
  UpdatePolicy legacy = policy(temporary, retired);
  UpdatePolicy rotated = policy(temporary, active);
  rotated.signer_policy_epoch = 2U;
  rotated.revoked_signers = {retired.public_key()};
  std::sort(rotated.revoked_signers.begin(), rotated.revoked_signers.end());
  IOTOX_CHECK(iotox::update::validate_update_policy(rotated).ok());

  auto encoded = iotox::update::encode_update_policy(rotated);
  IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
  const std::string encoded_text(encoded.value().begin(), encoded.value().end());
  IOTOX_CHECK(encoded_text.starts_with("iotox-update-policy-v2\n"));
  IOTOX_CHECK(encoded_text.find("signer-policy-epoch=2\n") !=
              std::string::npos);
  IOTOX_CHECK(encoded_text.find("revoked-signer=" +
                                iotox::security::hex(retired.public_key()) +
                                "\n") != std::string::npos);
  auto decoded = iotox::update::decode_update_policy(encoded.value());
  IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
  IOTOX_CHECK(decoded.value() == rotated);

  const auto payload = temporary.path() / "payload.bin";
  write_private(payload, "policy v2 payload");
  const auto active_bundle = temporary.path() / "active.iub";
  auto active_created = iotox::update::create_signed_update_bundle(
      rotated, payload, active_bundle, 1U, "1.0.0", active, crypto);
  IOTOX_CHECK_MSG(active_created.ok(), active_created.status().message());
  IOTOX_CHECK(iotox::update::inspect_signed_update_bundle(
                  rotated, active_bundle, crypto)
                  .ok());

  const auto retired_bundle = temporary.path() / "retired.iub";
  auto retired_created = iotox::update::create_signed_update_bundle(
      legacy, payload, retired_bundle, 1U, "1.0.0", retired, crypto);
  IOTOX_CHECK_MSG(retired_created.ok(), retired_created.status().message());
  auto rejected = iotox::update::inspect_signed_update_bundle(
      rotated, retired_bundle, crypto);
  IOTOX_CHECK(!rejected.ok());
  IOTOX_CHECK(rejected.status().code() == iotox::ErrorCode::protocol_error);

  UpdatePolicy overlap = rotated;
  overlap.trusted_signers.push_back(retired.public_key());
  std::sort(overlap.trusted_signers.begin(), overlap.trusted_signers.end());
  IOTOX_CHECK(!iotox::update::validate_update_policy(overlap).ok());

  UpdatePolicy revoked_without_epoch = rotated;
  revoked_without_epoch.signer_policy_epoch = 0U;
  IOTOX_CHECK(!iotox::update::validate_update_policy(revoked_without_epoch)
                   .ok());
}

IOTOX_TEST("signed update policy v3 binds executable service intent") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "service.identity", crypto);
  UpdatePolicy service = policy(temporary, signer);
  service.signer_policy_epoch = 1U;
  service.payload_kind =
      iotox::update::PayloadKind::linux_service_v1;
  auto encoded = iotox::update::encode_update_policy(service);
  IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
  const std::string text(encoded.value().begin(), encoded.value().end());
  IOTOX_CHECK(text.starts_with("iotox-update-policy-v3\n"));
  IOTOX_CHECK(text.find("payload-kind=linux-service-v1\n") !=
              std::string::npos);
  auto decoded = iotox::update::decode_update_policy(encoded.value());
  IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
  IOTOX_CHECK(decoded.value() == service);

  const auto payload = temporary.path() / "service.elf";
  write_private(payload, "ELF fixture bytes");
  const auto bundle = temporary.path() / "service.iub";
  auto created = iotox::update::create_signed_update_bundle(
      service, payload, bundle, 4U, "4.0.0", signer, crypto);
  IOTOX_CHECK_MSG(created.ok(), created.status().message());
  IOTOX_CHECK(
      created.value().manifest.payload_kind ==
      iotox::update::PayloadKind::linux_service_v1);

  UpdatePolicy opaque = service;
  opaque.payload_kind = iotox::update::PayloadKind::opaque_slot_v1;
  IOTOX_CHECK(!iotox::update::inspect_signed_update_bundle(
                   opaque, bundle, crypto).ok());
  UpdatePolicy missing_epoch = service;
  missing_epoch.signer_policy_epoch = 0U;
  IOTOX_CHECK(!iotox::update::validate_update_policy(missing_epoch).ok());
}

IOTOX_TEST("signed update bundle creates no-clobber and verifies exact payload") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "signer.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto payload = temporary.path() / "payload.bin";
  const auto bundle = temporary.path() / "release.iub";
  write_private(payload, "the immutable candidate payload\n");

  auto created = iotox::update::create_signed_update_bundle(
      configured, payload, bundle, 11U, "11.2.0", signer, crypto);
  IOTOX_CHECK(created.ok());
  IOTOX_CHECK(created.value().manifest.release_sequence == 11U);
  IOTOX_CHECK(created.value().manifest.version == "11.2.0");
  IOTOX_CHECK(created.value().manifest.payload_bytes == 32U);
  IOTOX_CHECK(std::filesystem::file_size(bundle) ==
              iotox::update::kSignedUpdateManifestBytes + 32U);
  auto inspected = iotox::update::inspect_signed_update_bundle(
      configured, bundle, crypto);
  IOTOX_CHECK(inspected.ok());
  IOTOX_CHECK(inspected.value() == created.value());

  auto duplicate = iotox::update::create_signed_update_bundle(
      configured, payload, bundle, 11U, "11.2.0", signer, crypto);
  IOTOX_CHECK(!duplicate.ok());
  IOTOX_CHECK(duplicate.status().code() == iotox::ErrorCode::invalid_argument);

  DeviceIdentity foreign =
      release_identity(temporary.path() / "foreign.identity", crypto);
  auto forbidden = iotox::update::create_signed_update_bundle(
      configured, payload, temporary.path() / "foreign.iub", 12U,
      "12.0.0", foreign, crypto);
  IOTOX_CHECK(!forbidden.ok());

  auto device = DeviceIdentity::load_or_create(
      temporary.path() / "device.identity", crypto, true);
  IOTOX_CHECK(device.ok());
  IOTOX_CHECK(!DeviceIdentity::load(
                   temporary.path() / "signer.identity", crypto).ok());
  IOTOX_CHECK(!DeviceIdentity::load_release(
                   temporary.path() / "device.identity", crypto).ok());
  UpdatePolicy confused = configured;
  confused.trusted_signers = {device.value().public_key()};
  auto wrong_role = iotox::update::create_signed_update_bundle(
      confused, payload, temporary.path() / "device-role.iub", 13U,
      "13.0.0", device.value(), crypto);
  IOTOX_CHECK(!wrong_role.ok());
  IOTOX_CHECK(wrong_role.status().code() ==
              iotox::ErrorCode::invalid_argument);
}

IOTOX_TEST("signed update bundle refuses payload and file-shape tampering") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "signer.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  const auto payload = temporary.path() / "payload.bin";
  write_private(payload, "payload-v1");

  const auto corrupt_payload = temporary.path() / "corrupt-payload.iub";
  IOTOX_CHECK(iotox::update::create_signed_update_bundle(
                  configured, payload, corrupt_payload, 1U, "1.0.0", signer,
                  crypto)
                  .ok());
  auto bytes = read_all(corrupt_payload);
  bytes.back() ^= 0x80U;
  write_all(corrupt_payload, bytes);
  IOTOX_CHECK(!iotox::update::inspect_signed_update_bundle(
                   configured, corrupt_payload, crypto)
                   .ok());

  const auto corrupt_manifest = temporary.path() / "corrupt-manifest.iub";
  IOTOX_CHECK(iotox::update::create_signed_update_bundle(
                  configured, payload, corrupt_manifest, 2U, "2.0.0", signer,
                  crypto)
                  .ok());
  bytes = read_all(corrupt_manifest);
  bytes[16U + 7U] ^= 1U;
  write_all(corrupt_manifest, bytes);
  IOTOX_CHECK(!iotox::update::inspect_signed_update_bundle(
                   configured, corrupt_manifest, crypto)
                   .ok());

  const auto linked = temporary.path() / "linked.iub";
  IOTOX_CHECK(iotox::update::create_signed_update_bundle(
                  configured, payload, linked, 3U, "3.0.0", signer, crypto)
                  .ok());
  IOTOX_CHECK(::link(linked.c_str(),
                     (temporary.path() / "second-link").c_str()) == 0);
  IOTOX_CHECK(!iotox::update::inspect_signed_update_bundle(
                   configured, linked, crypto)
                   .ok());

  const auto exposed = temporary.path() / "exposed.iub";
  IOTOX_CHECK(iotox::update::create_signed_update_bundle(
                  configured, payload, exposed, 4U, "4.0.0", signer, crypto)
                  .ok());
  IOTOX_CHECK(::chmod(exposed.c_str(), 0644) == 0);
  IOTOX_CHECK(!iotox::update::inspect_signed_update_bundle(
                   configured, exposed, crypto)
                   .ok());
}

IOTOX_TEST("update policy rejects ambiguous roots signers and bounds") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "signer.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);

  configured.root = "/";
  IOTOX_CHECK(!iotox::update::validate_update_policy(configured).ok());
  configured = policy(temporary, signer);
  configured.trusted_signers.push_back(signer.public_key());
  IOTOX_CHECK(!iotox::update::validate_update_policy(configured).ok());
  configured = policy(temporary, signer);
  configured.health_timeout_ms = 999U;
  IOTOX_CHECK(!iotox::update::validate_update_policy(configured).ok());
  configured = policy(temporary, signer);
  configured.maximum_payload_bytes = 0U;
  IOTOX_CHECK(!iotox::update::validate_update_policy(configured).ok());
}

IOTOX_TEST("update policy record is canonical private and stable") {
  TempDirectory temporary;
  Sodium crypto = sodium();
  DeviceIdentity signer =
      release_identity(temporary.path() / "signer.identity", crypto);
  UpdatePolicy configured = policy(temporary, signer);
  auto encoded = iotox::update::encode_update_policy(configured);
  IOTOX_CHECK(encoded.ok());
  auto decoded = iotox::update::decode_update_policy(encoded.value());
  IOTOX_CHECK(decoded.ok());
  IOTOX_CHECK(decoded.value() == configured);

  const auto record = temporary.path() / "update.policy";
  write_all(record, encoded.value());
  auto loaded = iotox::update::load_update_policy(
      record, static_cast<std::uint32_t>(::geteuid()));
  IOTOX_CHECK(loaded.ok());
  IOTOX_CHECK(loaded.value() == configured);

  auto noncanonical = encoded.value();
  const auto hexadecimal = std::find(noncanonical.begin(), noncanonical.end(),
                                     static_cast<std::uint8_t>('A'));
  if (hexadecimal != noncanonical.end()) {
    *hexadecimal = static_cast<std::uint8_t>('a');
    IOTOX_CHECK(!iotox::update::decode_update_policy(noncanonical).ok());
  }
  IOTOX_CHECK(::chmod(record.c_str(), 0644) == 0);
  IOTOX_CHECK(!iotox::update::load_update_policy(
                   record, static_cast<std::uint32_t>(::geteuid()))
                   .ok());
}
