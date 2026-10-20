#include "iotox/update_witness.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <span>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace iotox::update {
namespace {

constexpr std::array<std::uint8_t, 8U> kIntentMagic = {
    'I', 'O', 'T', 'X', 'U', 'W', 'I', '1'};
constexpr std::uint8_t kIntentVersion = 1U;
constexpr std::size_t kIntentStateOffset = 192U;
constexpr std::size_t kIntentSignedBytes =
    kIntentStateOffset + kSignedUpdateStateBytes;
constexpr std::size_t kIntentBytes =
    kIntentSignedBytes + security::kSignatureBytes;
constexpr std::string_view kIntentSignatureDomain{
    "iotox-update-lifecycle-witness-intent-v1"};
constexpr std::string_view kLifecycleDigestDomain{
    "iotox-update-lifecycle-head-v1"};

struct Intent {
  rollback_witness::DomainId domain{};
  security::SigningPublicKey device{};
  std::uint64_t witness_epoch{0U};
  rollback_witness::Head current{};
  rollback_witness::Head next{};
  rollback_witness::TransactionNonce nonce{};
  SignedUpdateStateBytes state{};
};

void append_u32(std::vector<std::uint8_t> &output, std::uint32_t value) {
  output.push_back(static_cast<std::uint8_t>(value >> 24U));
  output.push_back(static_cast<std::uint8_t>(value >> 16U));
  output.push_back(static_cast<std::uint8_t>(value >> 8U));
  output.push_back(static_cast<std::uint8_t>(value));
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
  for (std::size_t index = 0U; index < 8U; ++index) {
    bytes[offset + index] = static_cast<std::uint8_t>(
        value >> ((7U - index) * 8U));
  }
}

[[nodiscard]] std::uint64_t read_u64(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
  std::uint64_t value = 0U;
  for (std::size_t index = 0U; index < 8U; ++index) {
    value = (value << 8U) | bytes[offset + index];
  }
  return value;
}

[[nodiscard]] Status io_status(std::string operation,
                               const std::filesystem::path &path) {
  return Status{ErrorCode::io_error,
                std::move(operation) + " '" + path.string() + "': " +
                    std::strerror(errno)};
}

[[nodiscard]] Status validate_config(
    const LifecycleWitness::Config &config,
    const security::DeviceIdentity &identity) {
  rollback_witness::Record selector;
  selector.domain = config.domain;
  selector.device = identity.public_key();
  selector.witness_epoch = config.witness_epoch;
  selector.lane = rollback_witness::Lane::update_lifecycle;
  if (!config.backend || config.intent_path.empty() ||
      config.intent_path.filename().empty() ||
      config.intent_path.filename() == "." ||
      config.intent_path.filename() == ".." ||
      !rollback_witness::validate(selector).ok()) {
    return Status{ErrorCode::invalid_argument,
                  "update lifecycle witness configuration is invalid"};
  }
  if (!config.backend->independently_controlled() &&
      !config.allow_non_independent_for_testing) {
    return Status{ErrorCode::unsupported,
                  "update lifecycle witness shares the local failure domain"};
  }
  const std::filesystem::path parent = config.intent_path.parent_path();
  int descriptor = -1;
  do {
    descriptor = ::open(parent.c_str(),
                        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  } while (descriptor < 0 && errno == EINTR);
  if (descriptor < 0) {
    return io_status("unable to open update witness intent parent", parent);
  }
  struct stat metadata {};
  const bool private_parent = ::fstat(descriptor, &metadata) == 0 &&
      S_ISDIR(metadata.st_mode) && metadata.st_uid == ::geteuid() &&
      (metadata.st_mode & static_cast<mode_t>(0777)) == 0700;
  const int closed = ::close(descriptor);
  if (!private_parent) {
    return Status{ErrorCode::io_error,
                  "update witness intent parent must be owner-owned mode-0700"};
  }
  if (closed != 0) {
    return io_status("unable to close update witness intent parent", parent);
  }
  return Status::success();
}

[[nodiscard]] bool same_selector(
    const rollback_witness::Record &record,
    const LifecycleWitness::Config &config,
    const security::DeviceIdentity &identity) {
  return record.domain == config.domain &&
      security::constant_time_equal(record.device, identity.public_key()) &&
      record.witness_epoch == config.witness_epoch &&
      record.lane == rollback_witness::Lane::update_lifecycle;
}

[[nodiscard]] bool same_selector(
    const Intent &intent, const LifecycleWitness::Config &config,
    const security::DeviceIdentity &identity) {
  return intent.domain == config.domain &&
      security::constant_time_equal(intent.device, identity.public_key()) &&
      intent.witness_epoch == config.witness_epoch;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_intent_bytes(
    const std::filesystem::path &path) {
  int descriptor = -1;
  do {
    descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  } while (descriptor < 0 && errno == EINTR);
  if (descriptor < 0) {
    if (errno == ENOENT) {
      return Status{ErrorCode::not_found,
                    "update lifecycle witness intent does not exist"};
    }
    return io_status("unable to open update witness intent", path);
  }
  struct stat metadata {};
  if (::fstat(descriptor, &metadata) != 0) {
    const Status result =
        io_status("unable to inspect update witness intent", path);
    static_cast<void>(::close(descriptor));
    return result;
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
      metadata.st_uid != ::geteuid() ||
      (metadata.st_mode & static_cast<mode_t>(0777)) != 0600 ||
      metadata.st_size != static_cast<off_t>(kIntentBytes)) {
    static_cast<void>(::close(descriptor));
    return Status{ErrorCode::io_error,
                  "update witness intent is not one private canonical file"};
  }
  std::vector<std::uint8_t> bytes(kIntentBytes);
  std::size_t offset = 0U;
  while (offset < bytes.size()) {
    const ssize_t count = ::read(
        descriptor, bytes.data() + offset, bytes.size() - offset);
    if (count < 0 && errno == EINTR) continue;
    if (count <= 0) {
      const Status result = count == 0
          ? Status{ErrorCode::io_error,
                   "update witness intent ended before its inspected size"}
          : io_status("unable to read update witness intent", path);
      static_cast<void>(::close(descriptor));
      return result;
    }
    offset += static_cast<std::size_t>(count);
  }
  if (::close(descriptor) != 0) {
    return io_status("unable to close update witness intent", path);
  }
  return bytes;
}

[[nodiscard]] Result<std::array<std::uint8_t, kIntentBytes>> encode_intent(
    const Intent &intent, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  rollback_witness::Record current;
  current.domain = intent.domain;
  current.device = intent.device;
  current.witness_epoch = intent.witness_epoch;
  current.lane = rollback_witness::Lane::update_lifecycle;
  current.committed = intent.current;
  auto pending = rollback_witness::begin(current, intent.next, intent.nonce);
  if (!pending ||
      !security::constant_time_equal(intent.device, identity.public_key())) {
    return Status{ErrorCode::invalid_argument,
                  "update witness intent transition is invalid"};
  }
  std::array<std::uint8_t, kIntentBytes> bytes{};
  std::copy(kIntentMagic.begin(), kIntentMagic.end(), bytes.begin());
  bytes[8U] = kIntentVersion;
  bytes[9U] = static_cast<std::uint8_t>(
      rollback_witness::Lane::update_lifecycle);
  std::copy(intent.domain.begin(), intent.domain.end(), bytes.begin() + 16U);
  std::copy(intent.device.begin(), intent.device.end(), bytes.begin() + 32U);
  write_u64(bytes, 64U, intent.witness_epoch);
  write_u64(bytes, 72U, intent.current.position);
  std::copy(intent.current.digest.begin(), intent.current.digest.end(),
            bytes.begin() + 80U);
  write_u64(bytes, 112U, intent.next.position);
  std::copy(intent.next.digest.begin(), intent.next.digest.end(),
            bytes.begin() + 120U);
  std::copy(intent.nonce.begin(), intent.nonce.end(), bytes.begin() + 152U);
  bytes[184U] = 1U;
  std::copy(intent.state.begin(), intent.state.end(),
            bytes.begin() + kIntentStateOffset);
  auto digest = sodium.hash(
      kIntentSignatureDomain,
      std::span<const std::uint8_t>{bytes}.first<kIntentSignedBytes>());
  if (!digest) return digest.status();
  auto signature = identity.sign(digest.value());
  if (!signature) return signature.status();
  std::copy(signature.value().begin(), signature.value().end(),
            bytes.begin() + kIntentSignedBytes);
  return bytes;
}

[[nodiscard]] Result<Intent> decode_intent(
    std::span<const std::uint8_t> bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  if (bytes.size() != kIntentBytes ||
      !std::equal(kIntentMagic.begin(), kIntentMagic.end(), bytes.begin()) ||
      bytes[8U] != kIntentVersion ||
      bytes[9U] != static_cast<std::uint8_t>(
          rollback_witness::Lane::update_lifecycle) ||
      !std::all_of(bytes.begin() + 10U, bytes.begin() + 16U,
                   [](std::uint8_t byte) { return byte == 0U; }) ||
      bytes[184U] != 1U ||
      !std::all_of(bytes.begin() + 185U, bytes.begin() + 192U,
                   [](std::uint8_t byte) { return byte == 0U; })) {
    return Status{ErrorCode::protocol_error,
                  "update witness intent header is invalid"};
  }
  Intent result;
  std::copy_n(bytes.begin() + 16U, result.domain.size(), result.domain.begin());
  std::copy_n(bytes.begin() + 32U, result.device.size(), result.device.begin());
  result.witness_epoch = read_u64(bytes, 64U);
  result.current.position = read_u64(bytes, 72U);
  std::copy_n(bytes.begin() + 80U, result.current.digest.size(),
              result.current.digest.begin());
  result.next.position = read_u64(bytes, 112U);
  std::copy_n(bytes.begin() + 120U, result.next.digest.size(),
              result.next.digest.begin());
  std::copy_n(bytes.begin() + 152U, result.nonce.size(), result.nonce.begin());
  std::copy_n(bytes.begin() + kIntentStateOffset, result.state.size(),
              result.state.begin());
  security::Signature signature{};
  std::copy_n(bytes.begin() + kIntentSignedBytes, signature.size(),
              signature.begin());
  auto digest = sodium.hash(kIntentSignatureDomain,
                            bytes.first(kIntentSignedBytes));
  if (!digest) return digest.status();
  const Status verified = sodium.verify_detached(
      signature, digest.value(), identity.public_key());
  if (!verified.ok()) {
    return Status{ErrorCode::protocol_error,
                  "update witness intent signature is invalid"};
  }
  rollback_witness::Record current;
  current.domain = result.domain;
  current.device = result.device;
  current.witness_epoch = result.witness_epoch;
  current.lane = rollback_witness::Lane::update_lifecycle;
  current.committed = result.current;
  if (!rollback_witness::begin(current, result.next, result.nonce) ||
      !security::constant_time_equal(result.device, identity.public_key())) {
    return Status{ErrorCode::protocol_error,
                  "update witness intent identity or transition is invalid"};
  }
  return result;
}

[[nodiscard]] Result<std::optional<Intent>> load_intent(
    const LifecycleWitness::Config &config,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  auto bytes = read_intent_bytes(config.intent_path);
  if (!bytes && bytes.status().code() == ErrorCode::not_found) {
    return std::optional<Intent>{};
  }
  if (!bytes) return bytes.status();
  auto decoded = decode_intent(bytes.value(), identity, sodium);
  if (!decoded) return decoded.status();
  return std::optional<Intent>{std::move(decoded).value()};
}

[[nodiscard]] Status remove_intent(
    const LifecycleWitness::Config &config) {
  if (::unlink(config.intent_path.c_str()) != 0) {
    if (errno == ENOENT) return Status::success();
    return io_status("unable to remove update witness intent",
                     config.intent_path);
  }
  const std::filesystem::path parent = config.intent_path.parent_path();
  int descriptor = -1;
  do {
    descriptor = ::open(parent.c_str(),
                        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  } while (descriptor < 0 && errno == EINTR);
  if (descriptor < 0) {
    return io_status("unable to open update witness intent parent", parent);
  }
  const int synced = ::fsync(descriptor);
  const int closed = ::close(descriptor);
  if (synced != 0 || closed != 0) {
    return io_status("unable to synchronize update witness intent parent",
                     parent);
  }
  return Status::success();
}

[[nodiscard]] Status resolve_cas(
    const LifecycleWitness::Config &config,
    const rollback_witness::Record &expected,
    const rollback_witness::Record &desired, std::string_view label) {
  const Status exchanged = config.backend->compare_exchange(expected, desired);
  if (exchanged.ok()) return exchanged;
  auto observed = config.backend->query();
  if (observed && observed.value() == desired) return Status::success();
  return Status{exchanged.code(),
                std::string(label) + ": " + exchanged.message()};
}

[[nodiscard]] Result<rollback_witness::Head> state_head(
    const UpdatePolicy &policy,
    const std::optional<SignedUpdateStateBytes> &bytes,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
  std::uint64_t position = 1U;
  if (bytes) {
    auto state = decode_signed_update_state(*bytes);
    if (!state) return state.status();
    const Status verified = verify_signed_update_state(
        policy, state.value(), identity.public_key(), sodium);
    if (!verified.ok()) return verified;
    if (state.value().generation == std::numeric_limits<std::uint64_t>::max()) {
      return Status{ErrorCode::resource_exhausted,
                    "update witness position is exhausted"};
    }
    position = state.value().generation + 1U;
  }
  auto digest = update_lifecycle_digest(policy, bytes, sodium);
  if (!digest) return digest.status();
  return rollback_witness::Head{position, digest.value()};
}

struct Reconciled {
  rollback_witness::Record external;
  std::optional<SignedUpdateStateBytes> local;
};

[[nodiscard]] Result<Reconciled> reconcile(
    const LifecycleWitness::Config &config, const UpdatePolicy &policy,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const LifecycleWitness::LoadState &load,
    const LifecycleWitness::InstallState &install) {
  const Status configured = validate_config(config, identity);
  if (!configured.ok()) return configured;
  auto external = config.backend->query();
  if (!external) {
    return Status{external.status().code(),
                  "unable to query update lifecycle witness: " +
                      external.status().message()};
  }
  if (!rollback_witness::validate(external.value()).ok() ||
      !same_selector(external.value(), config, identity) ||
      external.value().committed.position == 0U) {
    return Status{ErrorCode::protocol_error,
                  "update lifecycle witness returned another or invalid lane"};
  }
  auto local = load();
  if (!local) return local.status();
  auto local_head = state_head(policy, local.value(), identity, sodium);
  if (!local_head) return local_head.status();
  auto intent = load_intent(config, identity, sodium);
  if (!intent) return intent.status();

  const auto install_next = [&](const Intent &transaction) -> Status {
    const Status installed = install(transaction.state);
    if (!installed.ok()) return installed;
    auto reread = load();
    if (!reread || !reread.value().has_value() ||
        *reread.value() != transaction.state) {
      return Status{ErrorCode::io_error,
                    "exact witnessed update state did not verify after install"};
    }
    local.value() = transaction.state;
    local_head = state_head(policy, local.value(), identity, sodium);
    return local_head ? Status::success() : local_head.status();
  };

  if (external.value().pending) {
    if (!intent.value()) {
      return Status{ErrorCode::protocol_error,
                    "update witness is pending without its exact signed intent"};
    }
    const Intent &transaction = *intent.value();
    auto next_head = state_head(
        policy, std::optional<SignedUpdateStateBytes>{transaction.state},
        identity, sodium);
    if (!next_head || !same_selector(transaction, config, identity) ||
        transaction.current != external.value().committed ||
        transaction.next != *external.value().pending ||
        transaction.nonce != *external.value().nonce ||
        next_head.value() != transaction.next ||
        (local_head.value() != transaction.current &&
         local_head.value() != transaction.next)) {
      return Status{ErrorCode::protocol_error,
                    "pending update witness, intent, and local state do not join"};
    }
    if (local_head.value() == transaction.current) {
      const Status installed = install_next(transaction);
      if (!installed.ok()) return installed;
    }
    auto committed = rollback_witness::finish(external.value());
    if (!committed) return committed.status();
    const Status finished = resolve_cas(
        config, external.value(), committed.value(),
        "unable to commit recovered update witness transition");
    if (!finished.ok()) return finished;
    external = committed.value();
    const Status removed = remove_intent(config);
    if (!removed.ok()) return removed;
  } else if (intent.value()) {
    const Intent &transaction = *intent.value();
    auto next_head = state_head(
        policy, std::optional<SignedUpdateStateBytes>{transaction.state},
        identity, sodium);
    if (!next_head || !same_selector(transaction, config, identity) ||
        next_head.value() != transaction.next ||
        (local_head.value() != transaction.current &&
         local_head.value() != transaction.next)) {
      return Status{ErrorCode::protocol_error,
                    "prepared update witness intent does not join local state"};
    }
    if (external.value().committed == transaction.current) {
      auto pending = rollback_witness::begin(
          external.value(), transaction.next, transaction.nonce);
      if (!pending) return pending.status();
      const Status began = resolve_cas(
          config, external.value(), pending.value(),
          "unable to resume prepared update witness transition");
      if (!began.ok()) return began;
      if (local_head.value() == transaction.current) {
        const Status installed = install_next(transaction);
        if (!installed.ok()) return installed;
      }
      auto committed = rollback_witness::finish(pending.value());
      if (!committed) return committed.status();
      const Status finished = resolve_cas(
          config, pending.value(), committed.value(),
          "unable to finish resumed update witness transition");
      if (!finished.ok()) return finished;
      external = committed.value();
      const Status removed = remove_intent(config);
      if (!removed.ok()) return removed;
    } else if (external.value().committed == transaction.next) {
      if (local_head.value() == transaction.current) {
        const Status installed = install_next(transaction);
        if (!installed.ok()) return installed;
      }
      const Status removed = remove_intent(config);
      if (!removed.ok()) return removed;
    } else {
      return Status{ErrorCode::protocol_error,
                    "update witness intent does not join external state"};
    }
  }

  auto final_local = load();
  if (!final_local) return final_local.status();
  auto final_head = state_head(policy, final_local.value(), identity, sodium);
  if (!final_head || external.value().pending ||
      final_head.value() != external.value().committed) {
    return Status{ErrorCode::protocol_error,
                  "local update policy/state is not the externally committed head"};
  }
  return Reconciled{external.value(), std::move(final_local).value()};
}

} // namespace

Result<security::Digest> update_lifecycle_digest(
    const UpdatePolicy &policy,
    const std::optional<SignedUpdateStateBytes> &state,
    const security::Sodium &sodium) {
  auto encoded_policy = encode_update_policy(policy);
  if (!encoded_policy) return encoded_policy.status();
  if (encoded_policy.value().size() >
      static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
    return Status{ErrorCode::resource_exhausted,
                  "update policy is too large for lifecycle commitment"};
  }
  constexpr std::string_view header{"iotox-update-lifecycle-head-v1\n"};
  std::vector<std::uint8_t> material(header.begin(), header.end());
  append_u32(material,
             static_cast<std::uint32_t>(encoded_policy.value().size()));
  material.insert(material.end(), encoded_policy.value().begin(),
                  encoded_policy.value().end());
  material.push_back(state.has_value() ? 1U : 0U);
  if (state) material.insert(material.end(), state->begin(), state->end());
  return sodium.hash(kLifecycleDigestDomain, material);
}

LifecycleWitness::LifecycleWitness(
    Config config, UpdatePolicy policy,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium)
    : config_(std::move(config)), policy_(std::move(policy)),
      identity_(&identity), sodium_(&sodium) {}

Result<rollback_witness::Record> LifecycleWitness::enrollment_record(
    const std::optional<SignedUpdateStateBytes> &state) const {
  const Status configured = validate_config(config_, *identity_);
  if (!configured.ok()) return configured;
  auto head = state_head(policy_, state, *identity_, *sodium_);
  if (!head) return head.status();
  rollback_witness::Record record;
  record.domain = config_.domain;
  record.device = identity_->public_key();
  record.witness_epoch = config_.witness_epoch;
  record.lane = rollback_witness::Lane::update_lifecycle;
  record.committed = head.value();
  const Status valid = rollback_witness::validate(record);
  if (!valid.ok()) return valid;
  return record;
}

Result<rollback_witness::Head> LifecycleWitness::verify_and_recover(
    const LoadState &load, const InstallState &install) const {
  auto state = reconcile(
      config_, policy_, *identity_, *sodium_, load, install);
  if (!state) return state.status();
  return state.value().external.committed;
}

Result<rollback_witness::Head> LifecycleWitness::transition(
    const SignedUpdateStateBytes &next, const LoadState &load,
    const InstallState &install) const {
  auto state = reconcile(
      config_, policy_, *identity_, *sodium_, load, install);
  if (!state) return state.status();
  auto next_head = state_head(
      policy_, std::optional<SignedUpdateStateBytes>{next},
      *identity_, *sodium_);
  if (!next_head) return next_head.status();
  const rollback_witness::Head current = state.value().external.committed;
  if (current.position == std::numeric_limits<std::uint64_t>::max() ||
      next_head.value().position != current.position + 1U ||
      next_head.value().digest == current.digest) {
    return Status{ErrorCode::protocol_error,
                  "update lifecycle transition is not one exact generation"};
  }
  rollback_witness::TransactionNonce nonce{};
  const Status random = security::fill_random(nonce);
  if (!random.ok()) return random;
  auto pending = rollback_witness::begin(
      state.value().external, next_head.value(), nonce);
  if (!pending) return pending.status();
  Intent intent;
  intent.domain = config_.domain;
  intent.device = identity_->public_key();
  intent.witness_epoch = config_.witness_epoch;
  intent.current = current;
  intent.next = next_head.value();
  intent.nonce = nonce;
  intent.state = next;
  auto encoded = encode_intent(intent, *identity_, *sodium_);
  if (!encoded) return encoded.status();
  const Status written = StateStore::write_atomic(
      config_.intent_path, encoded.value());
  if (!written.ok()) return written;
  const Status began = resolve_cas(
      config_, state.value().external, pending.value(),
      "unable to begin update lifecycle witness transition");
  if (!began.ok()) return began;
  const Status installed = install(next);
  if (!installed.ok()) return installed;
  auto reread = load();
  if (!reread || !reread.value().has_value() ||
      *reread.value() != next) {
    return Status{ErrorCode::io_error,
                  "exact witnessed update state did not verify after commit"};
  }
  auto committed = rollback_witness::finish(pending.value());
  if (!committed) return committed.status();
  const Status finished = resolve_cas(
      config_, pending.value(), committed.value(),
      "local update state advanced but witness commit is unresolved");
  if (!finished.ok()) return finished;
  const Status removed = remove_intent(config_);
  if (!removed.ok()) return removed;
  return next_head.value();
}

} // namespace iotox::update
