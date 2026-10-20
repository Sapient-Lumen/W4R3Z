#include "iotox/sync_gc.hpp"

#include "iotox/sync_guarded_witness.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <limits>
#include <linux/openat2.h>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

class UniqueFd {
public:
  UniqueFd() = default;
  explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
  ~UniqueFd() { reset(); }
  UniqueFd(const UniqueFd &) = delete;
  UniqueFd &operator=(const UniqueFd &) = delete;
  UniqueFd(UniqueFd &&other) noexcept
      : descriptor_(std::exchange(other.descriptor_, -1)) {}
  UniqueFd &operator=(UniqueFd &&other) noexcept {
    if (this != &other) {
      reset();
      descriptor_ = std::exchange(other.descriptor_, -1);
    }
    return *this;
  }
  [[nodiscard]] int get() const noexcept { return descriptor_; }
  [[nodiscard]] explicit operator bool() const noexcept {
    return descriptor_ >= 0;
  }
  void reset(int descriptor = -1) noexcept {
    if (descriptor_ >= 0) {
      int result = -1;
      do {
        result = ::close(descriptor_);
      } while (result != 0 && errno == EINTR);
    }
    descriptor_ = descriptor;
  }

private:
  int descriptor_{-1};
};

struct DescriptorInventory {
  UniqueFd root;
  UniqueFd objects;
  struct stat root_metadata {};
  struct stat objects_metadata {};
  std::vector<SyncGcObjectIdentity> entries;
  bool objects_present{false};
};

[[nodiscard]] Status system_status(ErrorCode code, std::string message) {
  message += ": ";
  message += std::strerror(errno);
  return Status{code, std::move(message)};
}

[[nodiscard]] bool valid_object_name(std::string_view name,
                                     std::string_view suffix) noexcept {
  if (name.size() != 64U + suffix.size() || !name.ends_with(suffix))
    return false;
  return std::all_of(name.begin(), name.begin() + 64U, [](char value) {
    return (value >= '0' && value <= '9') || (value >= 'a' && value <= 'f');
  });
}

[[nodiscard]] int hex_nibble(char value) noexcept {
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return 10 + value - 'a';
  return -1;
}

[[nodiscard]] Digest object_name_digest(std::string_view name) noexcept {
  Digest result{};
  for (std::size_t index = 0U; index < result.size(); ++index) {
    const int high = hex_nibble(name[index * 2U]);
    const int low = hex_nibble(name[index * 2U + 1U]);
    result[index] = static_cast<std::uint8_t>((high << 4U) | low);
  }
  return result;
}

[[nodiscard]] bool object_less(const SyncObjectRecord &left,
                               const SyncObjectRecord &right) noexcept {
  if (left.kind != right.kind)
    return left.kind < right.kind;
  return left.identity < right.identity;
}

[[nodiscard]] bool identity_less(const SyncGcObjectIdentity &left,
                                 const SyncGcObjectIdentity &right) noexcept {
  return object_less(left.object, right.object);
}

[[nodiscard]] std::string object_name(const SyncObjectRecord &object) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result;
  result.reserve(73U);
  for (const std::uint8_t byte : object.identity) {
    result.push_back(digits[byte >> 4U]);
    result.push_back(digits[byte & 0x0fU]);
  }
  result += object.kind == SyncObjectKind::artifact ? ".artifact" : ".manifest";
  return result;
}

[[nodiscard]] int open_beneath(int parent, const char *name, int flags) {
  struct open_how how {};
  how.flags =
      static_cast<decltype(how.flags)>(static_cast<unsigned int>(flags));
  how.resolve = RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS | RESOLVE_NO_SYMLINKS |
                RESOLVE_NO_XDEV;
  return static_cast<int>(
      ::syscall(SYS_openat2, parent, name, &how, sizeof(how)));
}

[[nodiscard]] bool private_directory(const struct stat &metadata) noexcept {
  return S_ISDIR(metadata.st_mode) && metadata.st_uid == ::geteuid() &&
         (metadata.st_mode & static_cast<mode_t>(0777)) ==
             static_cast<mode_t>(0700);
}

[[nodiscard]] Result<SyncGcObjectIdentity>
identity_from_metadata(const NamespacePolicy &policy, std::string_view name,
                       const struct stat &metadata) {
  const bool artifact = valid_object_name(name, ".artifact");
  const bool manifest = valid_object_name(name, ".manifest");
  if (!artifact && !manifest) {
    return Status{ErrorCode::protocol_error,
                  "sync GC object directory contains an unexpected entry"};
  }
  if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
      metadata.st_nlink != 1 ||
      (metadata.st_mode & static_cast<mode_t>(0777)) !=
          static_cast<mode_t>(0600) ||
      metadata.st_size <= 0) {
    return Status{ErrorCode::protocol_error,
                  "sync GC object is not one private owner file"};
  }
  const std::uint64_t bytes = static_cast<std::uint64_t>(metadata.st_size);
  if ((artifact && bytes > policy.quotas.maximum_artifact_bytes) ||
      (manifest && bytes > policy.quotas.maximum_manifest_bytes)) {
    return Status{ErrorCode::resource_exhausted,
                  "sync GC object exceeds its kind quota"};
  }
  return SyncGcObjectIdentity{SyncObjectRecord{artifact
                                                   ? SyncObjectKind::artifact
                                                   : SyncObjectKind::manifest,
                                               object_name_digest(name), bytes},
                              static_cast<std::uint64_t>(metadata.st_dev),
                              static_cast<std::uint64_t>(metadata.st_ino),
                              static_cast<std::uint64_t>(metadata.st_uid),
                              static_cast<std::uint64_t>(metadata.st_gid),
                              static_cast<std::uint64_t>(metadata.st_nlink),
                              static_cast<std::uint32_t>(metadata.st_mode)};
}

[[nodiscard]] bool same_directory(const struct stat &metadata,
                                  std::uint64_t device,
                                  std::uint64_t inode) noexcept {
  return static_cast<std::uint64_t>(metadata.st_dev) == device &&
         static_cast<std::uint64_t>(metadata.st_ino) == inode;
}

[[nodiscard]] bool
same_identity(const struct stat &metadata,
              const SyncGcObjectIdentity &identity) noexcept {
  return static_cast<std::uint64_t>(metadata.st_dev) == identity.device &&
         static_cast<std::uint64_t>(metadata.st_ino) == identity.inode &&
         static_cast<std::uint64_t>(metadata.st_uid) == identity.owner &&
         static_cast<std::uint64_t>(metadata.st_gid) == identity.group &&
         static_cast<std::uint64_t>(metadata.st_nlink) == identity.links &&
         static_cast<std::uint32_t>(metadata.st_mode) == identity.mode &&
         metadata.st_size >= 0 &&
         static_cast<std::uint64_t>(metadata.st_size) == identity.object.bytes;
}

[[nodiscard]] Result<DescriptorInventory>
capture_inventory(const NamespacePolicy &policy) {
  DescriptorInventory result;
  result.root.reset(::open(policy.root.c_str(),
                           O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
  if (!result.root) {
    return system_status(ErrorCode::io_error,
                         "unable to open descriptor-pinned sync root");
  }
  if (::fstat(result.root.get(), &result.root_metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect descriptor-pinned sync root");
  }
  if (!private_directory(result.root_metadata)) {
    return Status{ErrorCode::protocol_error,
                  "sync GC root is not private and owner-owned"};
  }

  result.objects.reset(open_beneath(result.root.get(), "objects",
                                    O_RDONLY | O_DIRECTORY | O_CLOEXEC));
  if (!result.objects) {
    if (errno == ENOENT)
      return result;
    if (errno == ENOSYS) {
      return Status{ErrorCode::unsupported,
                    "sync GC requires Linux openat2 containment"};
    }
    return system_status(ErrorCode::protocol_error,
                         "unable to open contained sync object directory");
  }
  result.objects_present = true;
  if (::fstat(result.objects.get(), &result.objects_metadata) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to inspect contained sync object directory");
  }
  if (!private_directory(result.objects_metadata) ||
      result.objects_metadata.st_dev != result.root_metadata.st_dev) {
    return Status{ErrorCode::protocol_error,
                  "sync GC object directory crosses its private root"};
  }

  const int duplicate = ::dup(result.objects.get());
  if (duplicate < 0) {
    return system_status(ErrorCode::io_error,
                         "unable to duplicate sync object directory");
  }
  DIR *directory = ::fdopendir(duplicate);
  if (directory == nullptr) {
    const int saved = errno;
    static_cast<void>(::close(duplicate));
    errno = saved;
    return system_status(ErrorCode::io_error,
                         "unable to enumerate sync object directory");
  }
  errno = 0;
  while (dirent *entry = ::readdir(directory)) {
    const std::string_view name{entry->d_name};
    if (name == "." || name == "..")
      continue;
    UniqueFd object(open_beneath(result.objects.get(), entry->d_name,
                                 O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (!object) {
      const int saved = errno;
      static_cast<void>(::closedir(directory));
      errno = saved;
      return system_status(ErrorCode::protocol_error,
                           "unable to open contained sync object");
    }
    struct stat metadata {};
    if (::fstat(object.get(), &metadata) != 0) {
      const int saved = errno;
      static_cast<void>(::closedir(directory));
      errno = saved;
      return system_status(ErrorCode::io_error,
                           "unable to inspect contained sync object");
    }
    auto identity = identity_from_metadata(policy, name, metadata);
    if (!identity.ok()) {
      static_cast<void>(::closedir(directory));
      return identity.status();
    }
    if (result.entries.size() >= policy.quotas.maximum_objects) {
      static_cast<void>(::closedir(directory));
      return Status{ErrorCode::resource_exhausted,
                    "sync GC inventory exceeds the object quota"};
    }
    result.entries.push_back(std::move(identity.value()));
    errno = 0;
  }
  const int enumeration_error = errno;
  static_cast<void>(::closedir(directory));
  if (enumeration_error != 0) {
    errno = enumeration_error;
    return system_status(ErrorCode::io_error,
                         "unable to enumerate sync object directory");
  }
  std::sort(result.entries.begin(), result.entries.end(), identity_less);
  std::uint64_t total_bytes = 0U;
  for (const SyncGcObjectIdentity &entry : result.entries) {
    if (total_bytes >
        std::numeric_limits<std::uint64_t>::max() - entry.object.bytes) {
      return Status{ErrorCode::resource_exhausted,
                    "sync GC inventory byte count overflows"};
    }
    total_bytes += entry.object.bytes;
  }
  if (total_bytes > policy.quotas.maximum_store_bytes) {
    return Status{ErrorCode::resource_exhausted,
                  "sync GC inventory exceeds the store quota"};
  }
  return result;
}

[[nodiscard]] Result<SyncGcPlan>
plan_with_transaction(const NamespacePolicy &policy,
                      const security::SigningPublicKey &expected_device,
                      const security::Sodium &sodium,
                      const SyncNamespaceTransaction &transaction,
                      std::shared_ptr<SyncGuardedStateWitness> witness) {
  const Status held = require_sync_transaction(policy, transaction);
  if (!held.ok())
    return held;
  auto captured = capture_inventory(policy);
  if (!captured.ok())
    return captured.status();
  if (!transaction.pins_root(
          static_cast<std::uint64_t>(captured.value().root_metadata.st_dev),
          static_cast<std::uint64_t>(captured.value().root_metadata.st_ino))) {
    return Status{ErrorCode::protocol_error,
                  "sync GC transaction does not pin the captured root"};
  }
  std::vector<SyncObjectRecord> records;
  records.reserve(captured.value().entries.size());
  for (const SyncGcObjectIdentity &entry : captured.value().entries)
    records.push_back(entry.object);
  auto reachability = plan_sync_reachability_in_transaction(
      policy, expected_device, std::move(records), sodium, transaction,
      std::move(witness));
  if (!reachability.ok())
    return reachability.status();

  struct stat current_root {};
  if (::lstat(policy.root.c_str(), &current_root) != 0) {
    return system_status(ErrorCode::io_error,
                         "unable to revalidate sync GC root path");
  }
  if (!same_directory(
          current_root,
          static_cast<std::uint64_t>(captured.value().root_metadata.st_dev),
          static_cast<std::uint64_t>(captured.value().root_metadata.st_ino))) {
    return Status{ErrorCode::protocol_error,
                  "sync GC root changed during planning"};
  }
  if (captured.value().objects_present) {
    struct stat current_objects {};
    if (::fstatat(captured.value().root.get(), "objects", &current_objects,
                  AT_SYMLINK_NOFOLLOW) != 0 ||
        !same_directory(current_objects,
                        static_cast<std::uint64_t>(
                            captured.value().objects_metadata.st_dev),
                        static_cast<std::uint64_t>(
                            captured.value().objects_metadata.st_ino))) {
      return Status{ErrorCode::protocol_error,
                    "sync GC object directory changed during planning"};
    }
  }

  SyncGcPlan plan;
  plan.reachability = std::move(reachability.value());
  plan.inventory = std::move(captured.value().entries);
  plan.root_device =
      static_cast<std::uint64_t>(captured.value().root_metadata.st_dev);
  plan.root_inode =
      static_cast<std::uint64_t>(captured.value().root_metadata.st_ino);
  plan.objects_present = captured.value().objects_present;
  if (plan.objects_present) {
    plan.objects_device =
        static_cast<std::uint64_t>(captured.value().objects_metadata.st_dev);
    plan.objects_inode =
        static_cast<std::uint64_t>(captured.value().objects_metadata.st_ino);
  }
  for (const SyncObjectRecord &candidate : plan.reachability.unreferenced) {
    auto found = std::lower_bound(
        plan.inventory.begin(), plan.inventory.end(), candidate,
        [](const SyncGcObjectIdentity &left, const SyncObjectRecord &right) {
          return object_less(left.object, right);
        });
    if (found == plan.inventory.end() || found->object != candidate) {
      return Status{ErrorCode::internal_error,
                    "sync GC planner lost an inventory identity"};
    }
    plan.candidates.push_back(*found);
  }
  plan.descriptor_pinned = true;
  return plan;
}

[[nodiscard]] Status default_sync_directory(int descriptor) {
  int result = -1;
  do {
    result = ::fsync(descriptor);
  } while (result != 0 && errno == EINTR);
  if (result != 0)
    return system_status(ErrorCode::io_error,
                         "unable to synchronize sync GC directory");
  return Status::success();
}

[[nodiscard]] bool cancelled(const SyncGcSeams &seams) {
  return seams.cancel_requested && seams.cancel_requested();
}

[[nodiscard]] Status sync_directory(const SyncGcSeams &seams, int descriptor) {
  return seams.sync_directory ? seams.sync_directory(descriptor)
                              : default_sync_directory(descriptor);
}

} // namespace

Result<SyncGcPlan>
plan_sync_gc_quarantine(const NamespacePolicy &policy,
                        const security::SigningPublicKey &expected_device,
                        const security::Sodium &sodium,
                        std::shared_ptr<SyncGuardedStateWitness> witness) {
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok())
    return transaction.status();
  return plan_with_transaction(policy, expected_device, sodium,
                               transaction.value(), std::move(witness));
}

SyncGcQuarantineOutcome quarantine_unreferenced_sync_objects(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium, const SyncGcSeams &seams,
    std::shared_ptr<SyncGuardedStateWitness> witness) {
  SyncGcQuarantineOutcome outcome;
  auto transaction = SyncNamespaceTransaction::acquire(policy);
  if (!transaction.ok()) {
    outcome.status = transaction.status();
    return outcome;
  }
  auto planned = plan_with_transaction(policy, expected_device, sodium,
                                       transaction.value(), std::move(witness));
  if (!planned.ok()) {
    outcome.status = planned.status();
    return outcome;
  }
  outcome.plan = std::move(planned.value());
  if (!outcome.plan->reachability.consistent() ||
      !outcome.plan->reachability.transaction_stable ||
      !outcome.plan->reachability.rollback_guard_consistent ||
      !outcome.plan->descriptor_pinned) {
    outcome.status = Status{
        ErrorCode::protocol_error,
        "sync GC refuses quarantine while live-root evidence is inconsistent"};
    return outcome;
  }
  if (outcome.plan->candidates.empty())
    return outcome;
  if (cancelled(seams)) {
    outcome.cancelled = true;
    outcome.status = Status{ErrorCode::unavailable,
                            "sync GC quarantine cancelled before mutation"};
    return outcome;
  }

  auto current = capture_inventory(policy);
  if (!current.ok()) {
    outcome.status = current.status();
    return outcome;
  }
  if (!same_directory(current.value().root_metadata, outcome.plan->root_device,
                      outcome.plan->root_inode) ||
      !current.value().objects_present ||
      !same_directory(current.value().objects_metadata,
                      outcome.plan->objects_device,
                      outcome.plan->objects_inode) ||
      current.value().entries != outcome.plan->inventory) {
    outcome.status =
        Status{ErrorCode::protocol_error,
               "sync GC inventory changed between planning and quarantine"};
    return outcome;
  }

  if (::mkdirat(current.value().root.get(), "gc-quarantine", 0700) == 0) {
    outcome.quarantine_created = true;
  } else if (errno != EEXIST) {
    outcome.status = system_status(
        ErrorCode::io_error, "unable to create contained sync GC quarantine");
    return outcome;
  }
  UniqueFd quarantine(open_beneath(current.value().root.get(), "gc-quarantine",
                                   O_RDONLY | O_DIRECTORY | O_CLOEXEC));
  if (!quarantine) {
    outcome.status =
        errno == ENOSYS
            ? Status{ErrorCode::unsupported,
                     "sync GC requires Linux openat2 containment"}
            : system_status(ErrorCode::protocol_error,
                            "unable to open contained sync GC quarantine");
    return outcome;
  }
  struct stat quarantine_metadata {};
  if (::fstat(quarantine.get(), &quarantine_metadata) != 0) {
    outcome.status = system_status(ErrorCode::io_error,
                                   "unable to inspect sync GC quarantine");
    return outcome;
  }
  if (!private_directory(quarantine_metadata) ||
      quarantine_metadata.st_dev != current.value().root_metadata.st_dev) {
    outcome.status = Status{ErrorCode::protocol_error,
                            "sync GC quarantine crosses its private root"};
    return outcome;
  }

  for (const SyncGcObjectIdentity &candidate : outcome.plan->candidates) {
    const std::string name = object_name(candidate.object);
    struct stat existing {};
    if (::fstatat(quarantine.get(), name.c_str(), &existing,
                  AT_SYMLINK_NOFOLLOW) == 0 ||
        errno != ENOENT) {
      outcome.status =
          Status{ErrorCode::protocol_error,
                 "sync GC quarantine destination is not exclusively absent"};
      return outcome;
    }
  }
  if (outcome.quarantine_created) {
    const Status synced = sync_directory(seams, current.value().root.get());
    if (!synced.ok()) {
      outcome.status = synced;
      return outcome;
    }
  }

  for (std::size_t index = 0U; index < outcome.plan->candidates.size();
       ++index) {
    const SyncGcObjectIdentity &candidate = outcome.plan->candidates[index];
    if (cancelled(seams)) {
      outcome.cancelled = true;
      outcome.status =
          Status{ErrorCode::unavailable, "sync GC quarantine cancelled"};
      return outcome;
    }
    if (seams.before_move) {
      const Status injected = seams.before_move(index, candidate);
      if (!injected.ok()) {
        outcome.status = injected;
        return outcome;
      }
    }
    const std::string name = object_name(candidate.object);
    UniqueFd source(open_beneath(current.value().objects.get(), name.c_str(),
                                 O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    struct stat source_metadata {};
    if (!source || ::fstat(source.get(), &source_metadata) != 0 ||
        !same_identity(source_metadata, candidate)) {
      outcome.status = Status{ErrorCode::protocol_error,
                              "sync GC candidate changed before quarantine"};
      return outcome;
    }
    if (::syscall(SYS_renameat2, current.value().objects.get(), name.c_str(),
                  quarantine.get(), name.c_str(), RENAME_NOREPLACE) != 0) {
      outcome.status =
          errno == ENOSYS
              ? Status{ErrorCode::unsupported,
                       "sync GC requires Linux renameat2 no-replace"}
              : system_status(ErrorCode::io_error,
                              "unable to quarantine exact sync GC candidate");
      return outcome;
    }
    struct stat destination_metadata {};
    if (::fstatat(quarantine.get(), name.c_str(), &destination_metadata,
                  AT_SYMLINK_NOFOLLOW) != 0 ||
        !same_identity(destination_metadata, candidate)) {
      outcome.status = Status{
          ErrorCode::protocol_error,
          "sync GC quarantined identity does not match the frozen candidate"};
      return outcome;
    }
    outcome.moved.push_back(candidate.object);
    outcome.moved_bytes += candidate.object.bytes;
    const Status source_synced =
        sync_directory(seams, current.value().objects.get());
    const Status quarantine_synced = sync_directory(seams, quarantine.get());
    if (!source_synced.ok() || !quarantine_synced.ok()) {
      outcome.status = !source_synced.ok() ? source_synced : quarantine_synced;
      return outcome;
    }
    ++outcome.durable_objects;
    outcome.durable_bytes += candidate.object.bytes;
  }
  return outcome;
}

} // namespace iotox::sync
