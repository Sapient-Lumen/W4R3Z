#include "iotox/sync_multiwriter_store.hpp"

#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <functional>
#include <limits>
#include <linux/fs.h>
#include <map>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

class FileDescriptor {
  public:
    explicit FileDescriptor(int value = -1) noexcept : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this != &other) {
            if (value_ >= 0) static_cast<void>(::close(value_));
            value_ = std::exchange(other.value_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return value_; }
    [[nodiscard]] int release() noexcept { return std::exchange(value_, -1); }

  private:
    int value_{-1};
};

[[nodiscard]] Status system_status(std::string_view operation,
                                   const std::filesystem::path &path,
                                   int error = errno) {
    return Status{ErrorCode::io_error, std::string(operation) + " '" +
                                           path.string() +
                                           "': " + std::strerror(error)};
}

[[nodiscard]] Status contextual_status(std::string_view context,
                                       const Status &cause) {
    return Status{cause.code(),
                  std::string(context) + ": " + cause.message()};
}

[[nodiscard]] std::string lower_hex(std::span<const std::uint8_t> bytes) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string output;
    output.reserve(bytes.size() * 2U);
    for (const std::uint8_t byte : bytes) {
        output.push_back(digits[byte >> 4U]);
        output.push_back(digits[byte & 0x0fU]);
    }
    return output;
}

[[nodiscard]] int hex_nibble(char value) noexcept {
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return 10 + value - 'a';
    return -1;
}

template <std::size_t Size>
[[nodiscard]] Result<std::array<std::uint8_t, Size>>
parse_hex(std::string_view value, std::string_view label) {
    if (value.size() != Size * 2U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has an invalid length"};
    }
    std::array<std::uint8_t, Size> result{};
    for (std::size_t index = 0U; index < Size; ++index) {
        const int high = hex_nibble(value[index * 2U]);
        const int low = hex_nibble(value[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " is not lowercase hex"};
        }
        result[index] = static_cast<std::uint8_t>((high << 4U) | low);
    }
    return result;
}

[[nodiscard]] Status
validate_private_directory(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0)
        return system_status("inspect tree-v2 directory", path);
    if (!S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0U ||
        (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) !=
            0U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 directory is not private owner state: " +
                          path.string()};
    }
    return Status::success();
}

[[nodiscard]] Result<bool>
ensure_private_directory(const std::filesystem::path &path) {
    bool created = false;
    if (::mkdir(path.c_str(), static_cast<mode_t>(0700)) == 0) {
        created = true;
    } else if (errno != EEXIST) {
        return system_status("create tree-v2 directory", path);
    }
    if (created && ::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0)
        return system_status("secure tree-v2 directory", path);
    const Status valid = validate_private_directory(path);
    if (!valid.ok()) return valid;
    return created;
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0)
        return system_status("open tree-v2 directory", path);
    if (::fsync(descriptor.get()) != 0)
        return system_status("fsync tree-v2 directory", path);
    return Status::success();
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
read_private_file(const std::filesystem::path &path,
                  std::size_t maximum_bytes) {
    FileDescriptor descriptor(
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        return system_status("open tree-v2 state", path);
    }
    struct stat metadata {};
    if (::fstat(descriptor.get(), &metadata) != 0)
        return system_status("inspect tree-v2 state", path);
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) ||
        metadata.st_size <= 0 ||
        static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 state is not one bounded private regular file"};
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor.get(), bytes.data() + offset,
                                     bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return system_status("read tree-v2 state", path);
    }
    return bytes;
}

[[nodiscard]] Status write_all(int descriptor,
                               std::span<const std::uint8_t> bytes,
                               const std::filesystem::path &path) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count =
            ::write(descriptor, bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return system_status("write tree-v2 state", path);
    }
    return Status::success();
}

[[nodiscard]] Status
remove_recovery_temporary(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        if (errno == ENOENT) return Status::success();
        return system_status("inspect tree-v2 temporary", path);
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 recovery temporary is unsafe"};
    }
    if (::unlink(path.c_str()) != 0)
        return system_status("remove tree-v2 recovery temporary", path);
    return sync_directory(path.parent_path());
}

[[nodiscard]] Result<bool>
install_immutable(const std::filesystem::path &destination,
                  std::span<const std::uint8_t> bytes) {
    auto existing = read_private_file(destination, bytes.size());
    if (existing) {
        if (existing.value().size() == bytes.size() &&
            std::equal(existing.value().begin(), existing.value().end(),
                       bytes.begin())) {
            return false;
        }
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 immutable object identity is occupied by different bytes"};
    }
    // Resolve absence directly: errno from the failed open is not a durable API
    // once a Status has been constructed.
    struct stat destination_metadata {};
    if (::lstat(destination.c_str(), &destination_metadata) == 0)
        return existing.status();
    if (errno != ENOENT)
        return system_status("inspect tree-v2 immutable destination",
                             destination);

    const std::filesystem::path temporary =
        destination.parent_path() / ".install.tmp";
    const Status cleaned = remove_recovery_temporary(temporary);
    if (!cleaned.ok()) return cleaned;
    FileDescriptor descriptor(
        ::open(temporary.c_str(),
               O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600));
    if (descriptor.get() < 0)
        return system_status("create tree-v2 immutable temporary", temporary);
    Status written = write_all(descriptor.get(), bytes, temporary);
    if (written.ok() && ::fsync(descriptor.get()) != 0)
        written = system_status("fsync tree-v2 immutable temporary", temporary);
    const int raw = descriptor.release();
    if (::close(raw) != 0 && written.ok())
        written = system_status("close tree-v2 immutable temporary", temporary);
    if (!written.ok()) {
        static_cast<void>(::unlink(temporary.c_str()));
        return written;
    }
    if (::syscall(SYS_renameat2, AT_FDCWD, temporary.c_str(), AT_FDCWD,
                  destination.c_str(), RENAME_NOREPLACE) != 0) {
        const int saved = errno;
        static_cast<void>(::unlink(temporary.c_str()));
        if (saved == EEXIST) {
            auto raced = read_private_file(destination, bytes.size());
            if (raced && raced.value().size() == bytes.size() &&
                std::equal(raced.value().begin(), raced.value().end(),
                           bytes.begin())) {
                return false;
            }
            return Status{ErrorCode::protocol_error,
                          "tree-v2 immutable install raced different bytes"};
        }
        return Status{saved == ENOSYS ? ErrorCode::unsupported
                                      : ErrorCode::io_error,
                      "install tree-v2 immutable state: " +
                          std::string(std::strerror(saved))};
    }
    const Status synced = sync_directory(destination.parent_path());
    if (!synced.ok()) return synced;
    return true;
}

[[nodiscard]] Status replace_branch(const std::filesystem::path &destination,
                                    std::span<const std::uint8_t> bytes) {
    const std::filesystem::path temporary =
        destination.parent_path() / ".update.tmp";
    const Status cleaned = remove_recovery_temporary(temporary);
    if (!cleaned.ok()) return cleaned;
    FileDescriptor descriptor(
        ::open(temporary.c_str(),
               O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600));
    if (descriptor.get() < 0)
        return system_status("create tree-v2 branch temporary", temporary);
    Status written = write_all(descriptor.get(), bytes, temporary);
    if (written.ok() && ::fsync(descriptor.get()) != 0)
        written = system_status("fsync tree-v2 branch temporary", temporary);
    const int raw = descriptor.release();
    if (::close(raw) != 0 && written.ok())
        written = system_status("close tree-v2 branch temporary", temporary);
    if (!written.ok()) {
        static_cast<void>(::unlink(temporary.c_str()));
        return written;
    }
    if (::rename(temporary.c_str(), destination.c_str()) != 0) {
        const Status failed =
            system_status("commit tree-v2 branch", destination);
        static_cast<void>(::unlink(temporary.c_str()));
        return failed;
    }
    return sync_directory(destination.parent_path());
}

[[nodiscard]] Status
retire_terminal_branch_pointer(const std::filesystem::path &live,
                               const std::filesystem::path &retired,
                               std::span<const std::uint8_t> bytes) {
    auto ready = ensure_private_directory(retired.parent_path());
    if (!ready) return ready.status();

    struct stat retired_metadata {};
    if (::lstat(retired.c_str(), &retired_metadata) == 0) {
        auto existing = read_private_file(retired, bytes.size());
        if (!existing) return existing.status();
        if (existing.value().size() != bytes.size() ||
            !std::equal(existing.value().begin(), existing.value().end(),
                        bytes.begin())) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 retired branch pointer changed"};
        }
    } else {
        if (errno != ENOENT)
            return system_status("inspect tree-v2 retired branch", retired);
        const Status installed = replace_branch(retired, bytes);
        if (!installed.ok()) return installed;
    }

    struct stat live_metadata {};
    if (::lstat(live.c_str(), &live_metadata) != 0) {
        if (errno == ENOENT) return Status::success();
        return system_status("inspect tree-v2 live branch", live);
    }
    auto existing = read_private_file(live, bytes.size());
    if (!existing) return existing.status();
    if (existing.value().size() != bytes.size() ||
        !std::equal(existing.value().begin(), existing.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 live branch exceeds terminal writer cutoff"};
    }
    if (::unlink(live.c_str()) != 0)
        return system_status("remove tree-v2 terminal live branch", live);
    return sync_directory(live.parent_path());
}

[[nodiscard]] bool canonical_named_file(std::string_view name,
                                        std::string_view suffix) noexcept {
    if (!name.ends_with(suffix)) return false;
    name.remove_suffix(suffix.size());
    if (name.size() != security::kSigningPublicKeyBytes * 2U) return false;
    return std::all_of(name.begin(), name.end(), [](char byte) {
        return (byte >= '0' && byte <= '9') || (byte >= 'a' && byte <= 'f');
    });
}

using TreeV2PathIndex =
    std::map<std::string, std::vector<TreeV2Entry>, std::less<>>;

[[nodiscard]] TreeV2PathIndex
index_tree_v2_manifest_paths(const TreeV2Manifest &manifest) {
    TreeV2PathIndex result;
    for (auto first = manifest.entries.begin();
         first != manifest.entries.end();) {
        const auto last = std::find_if(
            first, manifest.entries.end(), [&first](const TreeV2Entry &entry) {
                return entry.path != first->path;
            });
        auto &group = result[first->path];
        group.insert(group.end(), first, last);
        first = last;
    }
    return result;
}

[[nodiscard]] bool path_index_contains(const TreeV2PathIndex &index,
                                       const TreeV2Entry &entry) {
    const auto values = index.find(entry.path);
    return values != index.end() &&
           std::find(values->second.begin(), values->second.end(), entry) !=
               values->second.end();
}

[[nodiscard]] Result<TreeV2Snapshot> load_record_snapshot(
    const std::filesystem::path &root, const NamespacePolicy &policy,
    const Digest &expected_record, const security::Sodium &sodium) {
    const std::filesystem::path record_path =
        root / "tree-v2" / "records" / (lower_hex(expected_record) + ".branch");
    auto branch_bytes = read_private_file(
        record_path,
        192U + kMaximumNamespacePrincipals * 72U + security::kSignatureBytes);
    if (!branch_bytes) {
        return contextual_status("tree-v2 immutable branch record",
                                 branch_bytes.status());
    }
    auto head = decode_tree_v2_branch_head(policy, branch_bytes.value());
    if (!head) {
        return contextual_status("tree-v2 immutable branch record",
                                 head.status());
    }
    auto actual_record =
        tree_v2_branch_record_digest(policy, head.value(), sodium);
    if (!actual_record || actual_record.value() != expected_record) {
        return Status{
            ErrorCode::protocol_error,
            "tree-v2 immutable branch record identity does not match"};
    }
    const std::filesystem::path manifest_path =
        root / "tree-v2" / "manifests" /
        (lower_hex(head.value().manifest) + ".manifest");
    auto manifest_bytes = read_private_file(
        manifest_path,
        static_cast<std::size_t>(policy.quotas.maximum_manifest_bytes));
    if (!manifest_bytes) {
        return contextual_status("tree-v2 referenced manifest",
                                 manifest_bytes.status());
    }
    auto manifest = decode_tree_v2_manifest(policy, manifest_bytes.value());
    if (!manifest) {
        return contextual_status("tree-v2 referenced manifest",
                                 manifest.status());
    }
    TreeV2Snapshot snapshot{head.value(), manifest.value()};
    const Status verified = verify_tree_v2_snapshot(policy, snapshot, sodium);
    if (!verified.ok()) {
        return contextual_status("tree-v2 immutable branch record", verified);
    }
    return snapshot;
}

[[nodiscard]] Status
validate_successor_transition(const NamespacePolicy &policy,
                              std::span<const TreeV2Snapshot> current_frontier,
                              const TreeV2Snapshot &successor,
                              const security::Sodium &sodium) {
    std::vector<TreeV2PathIndex> proof_indexes;
    proof_indexes.reserve(successor.head.observations.size());
    for (const TreeV2Observation &observation : successor.head.observations) {
        auto observed =
            load_record_snapshot(std::filesystem::path(policy.root), policy,
                                 observation.record, sodium);
        if (!observed) return observed.status();
        if (observed.value().head.writer != observation.writer ||
            observed.value().head.generation != observation.generation) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 observation does not name its exact signed branch"};
        }
        proof_indexes.push_back(
            index_tree_v2_manifest_paths(observed.value().manifest));
    }

    std::optional<TreeV2Manifest> baseline;
    if (!current_frontier.empty()) {
        auto merged = merge_tree_v2_snapshots(policy, current_frontier, sodium);
        if (!merged) return merged.status();
        baseline = std::move(merged).value().manifest;
    }
    std::optional<TreeV2PathIndex> baseline_index;
    if (baseline) baseline_index = index_tree_v2_manifest_paths(*baseline);
    const TreeV2PathIndex successor_index =
        index_tree_v2_manifest_paths(successor.manifest);
    for (const TreeV2Entry &entry : successor.manifest.entries) {
        const bool new_local =
            entry.origin.writer == successor.head.writer &&
            entry.origin.generation == successor.head.generation;
        if (new_local) continue;
        const bool in_baseline =
            baseline_index && path_index_contains(*baseline_index, entry);
        const bool in_proof = std::any_of(
            proof_indexes.begin(), proof_indexes.end(),
            [&entry](const TreeV2PathIndex &proof) {
                return path_index_contains(proof, entry);
            });
        if (!in_baseline && !in_proof) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 branch introduces an unauthenticated "
                          "historical value"};
        }
    }
    if (!baseline) return Status::success();

    for (const auto &[path, prior] : *baseline_index) {
        const auto proposed_iterator = successor_index.find(path);
        if (proposed_iterator == successor_index.end()) continue;
        const std::vector<TreeV2Entry> &proposed =
            proposed_iterator->second;
        const bool replaces = std::any_of(
            proposed.begin(), proposed.end(),
            [&successor](const TreeV2Entry &entry) {
                return entry.origin.writer == successor.head.writer &&
                       entry.origin.generation == successor.head.generation;
            });
        for (const TreeV2Entry &entry : prior) {
            if (std::find(proposed.begin(), proposed.end(), entry) ==
                    proposed.end() &&
                tree_v2_head_observes(successor.head, entry.origin) &&
                !replaces) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 branch drops a value without a new local event"};
            }
        }
    }
    return Status::success();
}

} // namespace

std::string_view tree_v2_branch_store_decision_name(
    TreeV2BranchStoreDecision decision) noexcept {
    switch (decision) {
    case TreeV2BranchStoreDecision::accepted_genesis:
        return "accepted-genesis";
    case TreeV2BranchStoreDecision::accepted_advance:
        return "accepted-advance";
    case TreeV2BranchStoreDecision::duplicate:
        return "duplicate";
    case TreeV2BranchStoreDecision::retired_terminal:
        return "retired-terminal";
    }
    return "unknown";
}

Result<TreeV2Manifest>
load_tree_v2_stored_manifest(const NamespacePolicy &policy,
                             const Digest &digest,
                             const security::Sodium &sodium,
                             const SyncNamespaceTransaction &transaction) {
    TreeV2BranchStore store{std::filesystem::path(policy.root)};
    const Status prepared = store.prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    const std::filesystem::path path = std::filesystem::path(policy.root) /
                                       "tree-v2" / "manifests" /
                                       (lower_hex(digest) + ".manifest");
    auto bytes = read_private_file(
        path, static_cast<std::size_t>(policy.quotas.maximum_manifest_bytes));
    if (!bytes) return bytes.status();
    auto manifest = decode_tree_v2_manifest(policy, bytes.value());
    if (!manifest) return manifest.status();
    auto actual = tree_v2_manifest_digest(policy, manifest.value(), sodium);
    if (!actual || actual.value() != digest) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 stored manifest identity does not match"};
    }
    return manifest.value();
}

Result<TreeV2Snapshot>
load_tree_v2_stored_record(const NamespacePolicy &policy, const Digest &record,
                           const security::Sodium &sodium,
                           const SyncNamespaceTransaction &transaction) {
    TreeV2BranchStore store{std::filesystem::path(policy.root)};
    const Status prepared = store.prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    return load_record_snapshot(std::filesystem::path(policy.root), policy,
                                record, sodium);
}

std::filesystem::path tree_v2_manifest_path(const NamespacePolicy &policy,
                                            const Digest &digest) {
    return std::filesystem::path(policy.root) / "tree-v2" / "manifests" /
           (lower_hex(digest) + ".manifest");
}

std::filesystem::path tree_v2_branch_record_path(const NamespacePolicy &policy,
                                                 const Digest &record) {
    return std::filesystem::path(policy.root) / "tree-v2" / "records" /
           (lower_hex(record) + ".branch");
}

TreeV2BranchStore::TreeV2BranchStore(
    std::filesystem::path namespace_root,
    std::optional<security::SigningPublicKey> local_device,
    std::shared_ptr<TreeV2StateWitness> witness)
    : root_(std::move(namespace_root)),
      local_device_(std::move(local_device)), witness_(std::move(witness)) {}

std::filesystem::path
TreeV2BranchStore::manifest_path(const Digest &digest) const {
    return root_ / "tree-v2" / "manifests" / (lower_hex(digest) + ".manifest");
}

std::filesystem::path
TreeV2BranchStore::branch_path(const PrincipalId &writer) const {
    return root_ / "tree-v2" / "branches" / (lower_hex(writer) + ".branch");
}

std::filesystem::path
TreeV2BranchStore::record_path(const Digest &record) const {
    return root_ / "tree-v2" / "records" / (lower_hex(record) + ".branch");
}

Status
TreeV2BranchStore::prepare(const NamespacePolicy &policy,
                           const SyncNamespaceTransaction &transaction) const {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    if (policy.engine != Engine::tree_v2 ||
        root_.lexically_normal().string() != policy.root) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 store root or namespace engine is invalid"};
    }
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    Status prepared = validate_private_directory(root_);
    if (!prepared.ok()) return prepared;
    const std::filesystem::path tree = root_ / "tree-v2";
    auto tree_ready = ensure_private_directory(tree);
    if (!tree_ready) return tree_ready.status();
    const std::array children{tree / "manifests", tree / "branches",
                              tree / "records"};
    bool child_created = false;
    for (const auto &child : children) {
        auto child_ready = ensure_private_directory(child);
        if (!child_ready) return child_ready.status();
        if (!child_ready.value()) continue;
        child_created = true;
        prepared = sync_directory(child);
        if (!prepared.ok()) return prepared;
    }
    // Persist only structural mutations. Re-fsyncing every directory on every
    // frontier read provides no additional ordering and serializes steady-state
    // metadata handling behind unrelated storage barriers.
    if (tree_ready.value() || child_created) {
        prepared = sync_directory(tree);
        if (!prepared.ok()) return prepared;
    }
    if (tree_ready.value()) {
        prepared = sync_directory(root_);
        if (!prepared.ok()) return prepared;
    }
    return Status::success();
}

Result<std::vector<TreeV2Snapshot>> TreeV2BranchStore::load_frontier(
    const NamespacePolicy &policy, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    if (witness_) {
        const Status fresh = witness_->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    const Status prepared = prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    const std::filesystem::path branches = root_ / "tree-v2" / "branches";
    const std::filesystem::path manifests = root_ / "tree-v2" / "manifests";
    const std::filesystem::path records = root_ / "tree-v2" / "records";
    Status cleaned = remove_recovery_temporary(branches / ".update.tmp");
    if (!cleaned.ok()) return cleaned;
    cleaned = remove_recovery_temporary(manifests / ".install.tmp");
    if (!cleaned.ok()) return cleaned;
    cleaned = remove_recovery_temporary(records / ".install.tmp");
    if (!cleaned.ok()) return cleaned;

    std::vector<TreeV2Snapshot> result;
    try {
        for (const auto &entry :
             std::filesystem::directory_iterator(branches)) {
            const std::string name = entry.path().filename().string();
            if (!canonical_named_file(name, ".branch")) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 branch directory contains an unexpected entry"};
            }
            if (result.size() >= policy.quotas.maximum_peers ||
                result.size() >= kMaximumNamespacePrincipals) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 branch frontier exceeds quota"};
            }
            auto branch_bytes = read_private_file(
                entry.path(), 192U + kMaximumNamespacePrincipals * 72U +
                                  security::kSignatureBytes);
            if (!branch_bytes) {
                return contextual_status("tree-v2 branch pointer",
                                         branch_bytes.status());
            }
            auto head =
                decode_tree_v2_branch_head(policy, branch_bytes.value());
            if (!head) {
                return contextual_status("tree-v2 branch pointer",
                                         head.status());
            }
            std::string writer_name = name;
            writer_name.resize(writer_name.size() -
                               std::string_view(".branch").size());
            auto named_writer = parse_hex<security::kSigningPublicKeyBytes>(
                writer_name, "tree-v2 branch filename");
            if (!named_writer || named_writer.value() != head.value().writer) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 branch filename does not match its writer"};
            }
            const Status verified =
                verify_tree_v2_branch_head(policy, head.value(), sodium);
            if (!verified.ok()) {
                return contextual_status("tree-v2 branch pointer", verified);
            }
            auto manifest_bytes = read_private_file(
                manifest_path(head.value().manifest),
                static_cast<std::size_t>(policy.quotas.maximum_manifest_bytes));
            if (!manifest_bytes) {
                return contextual_status("tree-v2 current manifest",
                                         manifest_bytes.status());
            }
            auto manifest =
                decode_tree_v2_manifest(policy, manifest_bytes.value());
            if (!manifest) {
                return contextual_status("tree-v2 current manifest",
                                         manifest.status());
            }
            TreeV2Snapshot snapshot{head.value(), manifest.value()};
            const Status complete =
                verify_tree_v2_snapshot(policy, snapshot, sodium);
            if (!complete.ok()) {
                return contextual_status("tree-v2 current manifest", complete);
            }
            auto current_record =
                tree_v2_branch_record_digest(policy, snapshot.head, sodium);
            if (!current_record) return current_record.status();
            auto immutable = load_record_snapshot(
                root_, policy, current_record.value(), sodium);
            if (!immutable) return immutable.status();
            if (immutable.value() != snapshot) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 current branch lacks its exact immutable record"};
            }
            result.push_back(std::move(snapshot));
        }
        std::size_t manifest_count = 0U;
        for (const auto &entry :
             std::filesystem::directory_iterator(manifests)) {
            const std::string name = entry.path().filename().string();
            if (!canonical_named_file(name, ".manifest")) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 manifest directory contains an unexpected entry"};
            }
            if (++manifest_count > policy.quotas.maximum_objects) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 manifest population exceeds quota"};
            }
            auto bytes = read_private_file(
                entry.path(),
                static_cast<std::size_t>(policy.quotas.maximum_manifest_bytes));
            if (!bytes) {
                return contextual_status("tree-v2 immutable manifest",
                                         bytes.status());
            }
            auto decoded = decode_tree_v2_manifest(policy, bytes.value());
            if (!decoded) {
                return contextual_status("tree-v2 immutable manifest",
                                         decoded.status());
            }
            auto digest =
                tree_v2_manifest_digest(policy, decoded.value(), sodium);
            std::string digest_name = name;
            digest_name.resize(digest_name.size() -
                               std::string_view(".manifest").size());
            auto named_digest =
                parse_hex<32U>(digest_name, "tree-v2 manifest filename");
            if (!digest || !named_digest ||
                named_digest.value() != digest.value()) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 manifest filename does not match its content"};
            }
        }
        std::size_t record_count = 0U;
        for (const auto &entry : std::filesystem::directory_iterator(records)) {
            const std::string name = entry.path().filename().string();
            if (!canonical_named_file(name, ".branch")) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 record directory contains an unexpected entry"};
            }
            if (++record_count > policy.quotas.maximum_objects) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 immutable branch history exceeds quota"};
            }
            std::string digest_name = name;
            digest_name.resize(digest_name.size() -
                               std::string_view(".branch").size());
            auto named_record =
                parse_hex<32U>(digest_name, "tree-v2 record filename");
            if (!named_record) return named_record.status();
            auto stored = load_record_snapshot(root_, policy,
                                               named_record.value(), sodium);
            if (!stored) return stored.status();
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate tree-v2 store: " +
                          std::string(error.what())};
    }
    std::sort(result.begin(), result.end(),
              [](const TreeV2Snapshot &left, const TreeV2Snapshot &right) {
                  return left.head.writer < right.head.writer;
              });
    return result;
}

Result<TreeV2BranchStoreResult>
TreeV2BranchStore::accept(const NamespacePolicy &policy,
                          const TreeV2Snapshot &snapshot,
                          const security::Sodium &sodium,
                          const SyncNamespaceTransaction &transaction) const {
    const Status verified = verify_tree_v2_snapshot(policy, snapshot, sodium);
    if (!verified.ok()) return verified;
    auto frontier = load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    auto record = tree_v2_branch_record_digest(policy, snapshot.head, sodium);
    if (!record) return record.status();
    bool terminal_cutoff = false;
    if (local_device_) {
        TreeV2MaintenanceStore maintenance{root_};
        auto state = maintenance.load(policy, *local_device_, sodium,
                                      transaction);
        if (!state) return state.status();
        const auto cutoff = std::lower_bound(
            state.value().cutoffs.begin(), state.value().cutoffs.end(),
            snapshot.head.writer,
            [](const TreeV2WriterCutoff &candidate,
               const PrincipalId &writer) { return candidate.writer < writer; });
        if (cutoff != state.value().cutoffs.end() &&
            cutoff->writer == snapshot.head.writer) {
            if (cutoff->generation != snapshot.head.generation ||
                cutoff->record != record.value()) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 branch is outside its terminal writer cutoff"};
            }
            terminal_cutoff = true;
        }
    }
    const auto current =
        std::find_if(frontier.value().begin(), frontier.value().end(),
                     [&snapshot](const TreeV2Snapshot &candidate) {
                         return candidate.head.writer == snapshot.head.writer;
                     });
    TreeV2BranchStoreDecision decision =
        TreeV2BranchStoreDecision::accepted_genesis;
    if (current != frontier.value().end()) {
        auto current_record =
            tree_v2_branch_record_digest(policy, current->head, sodium);
        if (!current_record) return current_record.status();
        if (current_record.value() == record.value()) {
            if (!terminal_cutoff) {
                return TreeV2BranchStoreResult{
                    TreeV2BranchStoreDecision::duplicate, *current,
                    record.value(), false};
            }
            decision = TreeV2BranchStoreDecision::retired_terminal;
        } else if (terminal_cutoff) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 live branch exceeds terminal writer cutoff"};
        } else {
            const bool checkpoint_successor =
                snapshot.head.checkpoint &&
                snapshot.head.generation == current->head.generation + 1U &&
                std::any_of(
                    snapshot.head.observations.begin(),
                    snapshot.head.observations.end(),
                    [&snapshot, &current_record](const auto &observation) {
                        return observation.writer == snapshot.head.writer &&
                               observation.generation + 1U ==
                                   snapshot.head.generation &&
                               observation.record == current_record.value();
                    });
            if ((!snapshot.head.checkpoint &&
                 (snapshot.head.generation != current->head.generation + 1U ||
                  snapshot.head.previous != current_record.value())) ||
                (snapshot.head.checkpoint && !checkpoint_successor)) {
                return Status{
                    ErrorCode::protocol_error,
                    "tree-v2 branch is stale, forked, or skips a generation"};
            }
            decision = TreeV2BranchStoreDecision::accepted_advance;
        }
    } else if (!terminal_cutoff && !snapshot.head.checkpoint &&
               snapshot.head.generation != 1U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch genesis is missing"};
    }

    if (!terminal_cutoff && !snapshot.head.checkpoint) {
        const Status coherent = validate_successor_transition(
            policy, frontier.value(), snapshot, sodium);
        if (!coherent.ok()) return coherent;
    }

    auto manifest_bytes = encode_tree_v2_manifest(policy, snapshot.manifest);
    if (!manifest_bytes) return manifest_bytes.status();
    auto installed = install_immutable(manifest_path(snapshot.head.manifest),
                                       manifest_bytes.value());
    if (!installed) return installed.status();
    auto branch_bytes = encode_tree_v2_branch_head(policy, snapshot.head);
    if (!branch_bytes) return branch_bytes.status();
    auto record_installed =
        install_immutable(record_path(record.value()), branch_bytes.value());
    if (!record_installed) return record_installed.status();
    if (terminal_cutoff) {
        const auto commit = [&]() {
            return retire_terminal_branch_pointer(
                branch_path(snapshot.head.writer),
                root_ / "tree-v2" / "retired-branches" /
                    (lower_hex(snapshot.head.writer) + ".branch"),
                branch_bytes.value());
        };
        Status retired;
        if (witness_) {
            const PrincipalId writer = snapshot.head.writer;
            retired = witness_->transition(
                policy, transaction,
                [&writer](const TreeV2FreshnessState &current_state)
                    -> Result<TreeV2FreshnessState> {
                    TreeV2FreshnessState next = current_state;
                    const auto found = std::lower_bound(
                        next.frontier.begin(), next.frontier.end(), writer,
                        [](const TreeV2Observation &candidate,
                           const PrincipalId &candidate_writer) {
                            return candidate.writer < candidate_writer;
                        });
                    if (found != next.frontier.end() &&
                        found->writer == writer) {
                        next.frontier.erase(found);
                    }
                    return next;
                },
                commit);
        } else {
            retired = commit();
        }
        if (!retired.ok()) return retired;
        return TreeV2BranchStoreResult{
            TreeV2BranchStoreDecision::retired_terminal, snapshot,
            record.value(), installed.value()};
    }
    const auto commit = [&]() {
        return replace_branch(branch_path(snapshot.head.writer),
                              branch_bytes.value());
    };
    Status committed;
    if (witness_) {
        const TreeV2Observation successor{snapshot.head.writer,
                                          snapshot.head.generation,
                                          record.value()};
        committed = witness_->transition(
            policy, transaction,
            [&successor](const TreeV2FreshnessState &current_state)
                -> Result<TreeV2FreshnessState> {
                TreeV2FreshnessState next = current_state;
                const auto found = std::lower_bound(
                    next.frontier.begin(), next.frontier.end(),
                    successor.writer,
                    [](const TreeV2Observation &candidate,
                       const PrincipalId &writer) {
                        return candidate.writer < writer;
                    });
                if (found != next.frontier.end() &&
                    found->writer == successor.writer) {
                    *found = successor;
                } else {
                    next.frontier.insert(found, successor);
                }
                return next;
            },
            commit);
    } else {
        committed = commit();
    }
    if (!committed.ok()) return committed;

    auto reloaded = load_frontier(policy, sodium, transaction);
    if (!reloaded) return reloaded.status();
    const auto durable =
        std::find_if(reloaded.value().begin(), reloaded.value().end(),
                     [&snapshot](const TreeV2Snapshot &candidate) {
                         return candidate.head.writer == snapshot.head.writer;
                     });
    if (durable == reloaded.value().end() || durable->head != snapshot.head ||
        durable->manifest != snapshot.manifest) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch commit did not reload exactly"};
    }
    return TreeV2BranchStoreResult{decision, *durable, record.value(),
                                   installed.value()};
}

Result<TreeV2BranchStoreResult> TreeV2BranchStore::publish_local(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto frontier = load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    const auto prior_snapshot =
        std::find_if(frontier.value().begin(), frontier.value().end(),
                     [&identity](const TreeV2Snapshot &snapshot) {
                         return snapshot.head.writer == identity.public_key();
                     });
    std::optional<TreeV2BranchHead> previous =
        prior_snapshot == frontier.value().end()
            ? std::optional<TreeV2BranchHead>{}
            : std::optional<TreeV2BranchHead>{prior_snapshot->head};
    std::vector<TreeV2Observation> observations;
    observations.reserve(frontier.value().size());
    bool frontier_already_observed = true;
    for (const TreeV2Snapshot &snapshot : frontier.value()) {
        auto record =
            tree_v2_branch_record_digest(policy, snapshot.head, sodium);
        if (!record) return record.status();
        if (snapshot.head.writer == identity.public_key()) {
            continue;
        }
        observations.push_back(TreeV2Observation{
            snapshot.head.writer, snapshot.head.generation, record.value()});
        if (!previous ||
            !tree_v2_head_observes(*previous,
                                   TreeV2Version{snapshot.head.writer,
                                                 snapshot.head.generation})) {
            frontier_already_observed = false;
        }
    }
    TreeV2Manifest publication_manifest = manifest;
    if (prior_snapshot != frontier.value().end() &&
        prior_snapshot->manifest == manifest && !frontier_already_observed) {
        auto merged = merge_tree_v2_snapshots(policy, frontier.value(), sodium);
        if (!merged) return merged.status();
        publication_manifest = std::move(merged).value().manifest;
    }
    if (prior_snapshot != frontier.value().end() &&
        prior_snapshot->manifest == publication_manifest &&
        frontier_already_observed) {
        auto record =
            tree_v2_branch_record_digest(policy, prior_snapshot->head, sodium);
        if (!record) return record.status();
        return TreeV2BranchStoreResult{TreeV2BranchStoreDecision::duplicate,
                                       *prior_snapshot, record.value(), false};
    }
    auto head = create_tree_v2_branch_head(
        policy, publication_manifest, previous, observations, identity, sodium);
    if (!head) return head.status();
    return accept(policy,
                  TreeV2Snapshot{head.value(), std::move(publication_manifest)},
                  sodium, transaction);
}

Result<Digest> TreeV2BranchStore::retain_manifest(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    if (witness_) {
        const Status fresh = witness_->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    const Status valid = validate_tree_v2_manifest(policy, manifest);
    if (!valid.ok()) return valid;
    const Status prepared = prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    auto digest = tree_v2_manifest_digest(policy, manifest, sodium);
    if (!digest) return digest.status();
    auto bytes = encode_tree_v2_manifest(policy, manifest);
    if (!bytes) return bytes.status();
    auto installed = install_immutable(manifest_path(digest.value()),
                                       bytes.value());
    if (!installed) return installed.status();
    auto reloaded = load_tree_v2_stored_manifest(policy, digest.value(), sodium,
                                                 transaction);
    if (!reloaded) return reloaded.status();
    if (reloaded.value() != manifest) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 retained manifest did not reload exactly"};
    }
    return digest.value();
}

Result<TreeV2BranchStoreResult> TreeV2BranchStore::publish_local_from_frontier(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    std::span<const TreeV2Observation> visible_frontier,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto frontier = load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    const auto prior =
        std::find_if(frontier.value().begin(), frontier.value().end(),
                     [&identity](const TreeV2Snapshot &snapshot) {
                         return snapshot.head.writer == identity.public_key();
                     });
    if (prior == frontier.value().end()) {
        if (!visible_frontier.empty()) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 genesis has a spurious visible frontier"};
        }
        auto head = create_tree_v2_branch_head(policy, manifest, std::nullopt,
                                               {}, identity, sodium);
        if (!head) return head.status();
        return accept(policy, TreeV2Snapshot{head.value(), manifest}, sodium,
                      transaction);
    }
    std::vector<TreeV2Observation> causal(visible_frontier.begin(),
                                          visible_frontier.end());
    if (!std::is_sorted(
            causal.begin(), causal.end(),
            [](const TreeV2Observation &left, const TreeV2Observation &right) {
                return left.writer < right.writer;
            }) ||
        std::adjacent_find(
            causal.begin(), causal.end(),
            [](const TreeV2Observation &left, const TreeV2Observation &right) {
                return left.writer == right.writer;
            }) != causal.end()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 visible frontier is not canonical"};
    }
    const auto visible_self = std::lower_bound(
        causal.begin(), causal.end(), identity.public_key(),
        [](const TreeV2Observation &observation, const PrincipalId &writer) {
            return observation.writer < writer;
        });
    auto prior_record =
        tree_v2_branch_record_digest(policy, prior->head, sodium);
    if (!prior_record) return prior_record.status();
    if (visible_self == causal.end() ||
        visible_self->writer != identity.public_key() ||
        visible_self->generation != prior->head.generation ||
        visible_self->record != prior_record.value()) {
        return Status{
            ErrorCode::unavailable,
            "tree-v2 workspace does not expose the current local branch"};
    }
    causal.erase(visible_self);
    for (const TreeV2Observation &observation : causal) {
        auto proof = load_tree_v2_stored_record(policy, observation.record,
                                                sodium, transaction);
        if (!proof || proof.value().head.writer != observation.writer ||
            proof.value().head.generation != observation.generation) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 visible frontier proof is unavailable"};
        }
    }

    std::vector<TreeV2Observation> prior_causal;
    for (const TreeV2Observation &observation : prior->head.observations) {
        if (observation.writer != identity.public_key())
            prior_causal.push_back(observation);
    }
    if (prior->manifest == manifest && prior_causal == causal) {
        return TreeV2BranchStoreResult{TreeV2BranchStoreDecision::duplicate,
                                       *prior, prior_record.value(), false};
    }
    auto head = create_tree_v2_branch_head(policy, manifest, prior->head,
                                           causal, identity, sodium);
    if (!head) return head.status();
    return accept(policy, TreeV2Snapshot{head.value(), manifest}, sodium,
                  transaction);
}

Result<TreeV2BranchStoreResult> TreeV2BranchStore::checkpoint_local(
    const NamespacePolicy &policy, const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto frontier = load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    auto checkpoint = create_tree_v2_checkpoint(policy, frontier.value(),
                                                identity, sodium);
    if (!checkpoint) return checkpoint.status();
    return accept(policy, checkpoint.value(), sodium, transaction);
}

} // namespace iotox::sync
