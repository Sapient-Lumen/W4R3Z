#include "iotox/sync_multiwriter_maintenance.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"
#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <linux/fs.h>
#include <limits>
#include <map>
#include <set>
#include <string_view>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <tuple>
#include <unistd.h>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic = {'I', 'O', 'T', 'X',
                                                 'T', 'V', 'M', '1'};
constexpr std::size_t kHeaderBytes = 152U;
constexpr std::size_t kCutoffBytes = 72U;
constexpr std::size_t kNamespaceOffset = 88U;
constexpr std::size_t kNamespaceBytes = 64U;
constexpr std::string_view kSignatureDomain =
    "iotox-sync-tree-v2-maintenance-signature-v1";
constexpr std::string_view kRecordDomain =
    "iotox-sync-tree-v2-maintenance-record-v1";

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

void write_u16(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint16_t value) {
    bytes[offset] = static_cast<std::uint8_t>(value >> 8U);
    bytes[offset + 1U] = static_cast<std::uint8_t>(value);
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index)
        bytes[offset + index] =
            static_cast<std::uint8_t>(value >> (56U - index * 8U));
}

[[nodiscard]] std::uint16_t read_u16(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        bytes[offset + 1U]);
}

[[nodiscard]] std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint64_t result = 0U;
    for (std::size_t index = 0U; index < 8U; ++index)
        result = (result << 8U) | bytes[offset + index];
    return result;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> output, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
    std::copy(value.begin(), value.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> input, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset), Size,
                value.begin());
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

[[nodiscard]] Result<Digest> parse_digest(std::string_view value) {
    if (value.size() != 64U) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance digest name has wrong length"};
    }
    Digest result{};
    for (std::size_t index = 0U; index < result.size(); ++index) {
        const int high = hex_nibble(value[index * 2U]);
        const int low = hex_nibble(value[index * 2U + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 maintenance digest name is not lowercase hex"};
        }
        result[index] = static_cast<std::uint8_t>((high << 4U) | low);
    }
    return result;
}

[[nodiscard]] Status validate_state(const TreeV2MaintenanceState &state,
                                    std::uint64_t maximum_pins,
                                    std::uint64_t maximum_cutoffs) {
    if (!valid_namespace_id(state.namespace_id) || state.mutation == 0U ||
        all_zero(state.signer) || state.pins.size() > maximum_pins ||
        state.cutoffs.size() > maximum_cutoffs ||
        (state.mutation == 1U && !all_zero(state.previous)) ||
        (state.mutation > 1U && all_zero(state.previous)) ||
        !std::is_sorted(state.pins.begin(), state.pins.end()) ||
        std::adjacent_find(state.pins.begin(), state.pins.end()) !=
            state.pins.end()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 maintenance identity or bounds are invalid"};
    }
    for (std::size_t index = 0U; index < state.pins.size(); ++index) {
        if (all_zero(state.pins[index])) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 maintenance pin is zero"};
        }
    }
    for (std::size_t index = 0U; index < state.cutoffs.size(); ++index) {
        const TreeV2WriterCutoff &cutoff = state.cutoffs[index];
        if (all_zero(cutoff.writer) || cutoff.generation == 0U ||
            all_zero(cutoff.record) ||
            (index != 0U &&
             !(state.cutoffs[index - 1U].writer < cutoff.writer))) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 writer cutoffs are invalid or noncanonical"};
        }
    }
    return Status::success();
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_body(const TreeV2MaintenanceState &state) {
    const Status valid = validate_state(
        state, std::numeric_limits<std::uint64_t>::max(),
        std::numeric_limits<std::uint64_t>::max());
    if (!valid.ok()) return valid;
    if (state.pins.size() > std::numeric_limits<std::uint16_t>::max() ||
        state.cutoffs.size() > std::numeric_limits<std::uint16_t>::max() ||
        state.pins.size() >
            (std::numeric_limits<std::size_t>::max() - kHeaderBytes) / 32U ||
        state.cutoffs.size() >
            (std::numeric_limits<std::size_t>::max() - kHeaderBytes -
             state.pins.size() * 32U) /
                kCutoffBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 maintenance encoding is too large"};
    }
    std::array<std::uint8_t, kHeaderBytes> header{};
    std::copy(kMagic.begin(), kMagic.end(), header.begin());
    header[8U] = 1U;
    header[9U] = static_cast<std::uint8_t>(state.namespace_id.size());
    write_u16(header, 10U, static_cast<std::uint16_t>(state.pins.size()));
    write_u16(header, 12U, static_cast<std::uint16_t>(state.cutoffs.size()));
    write_u64(header, 16U, state.mutation);
    write_array(header, 24U, state.signer);
    write_array(header, 56U, state.previous);
    std::copy(state.namespace_id.begin(), state.namespace_id.end(),
              header.begin() + static_cast<std::ptrdiff_t>(kNamespaceOffset));
    std::vector<std::uint8_t> output(header.begin(), header.end());
    output.reserve(kHeaderBytes + state.pins.size() * 32U +
                   state.cutoffs.size() * kCutoffBytes);
    for (const Digest &pin : state.pins) {
        output.insert(output.end(), pin.begin(), pin.end());
    }
    for (const TreeV2WriterCutoff &cutoff : state.cutoffs) {
        std::array<std::uint8_t, kCutoffBytes> encoded{};
        write_array(encoded, 0U, cutoff.writer);
        write_u64(encoded, 32U, cutoff.generation);
        write_array(encoded, 40U, cutoff.record);
        output.insert(output.end(), encoded.begin(), encoded.end());
    }
    return output;
}

[[nodiscard]] Result<Digest>
state_record(const TreeV2MaintenanceState &state,
             const security::Sodium &sodium) {
    auto encoded = encode_tree_v2_maintenance_state(state);
    if (!encoded) return encoded.status();
    return sodium.hash(kRecordDomain, encoded.value());
}

[[nodiscard]] Status validate_private_file(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to inspect tree-v2 maintenance state: " +
                          std::string(std::strerror(errno))};
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance state is not one private file"};
    }
    return Status::success();
}

[[nodiscard]] Status ensure_private_directory(
    const std::filesystem::path &path) {
    std::error_code error;
    std::filesystem::create_directories(path, error);
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to create tree-v2 maintenance directory: " +
                          error.message()};
    }
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 ||
        !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance directory is not private"};
    }
    if (::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to secure tree-v2 maintenance directory: " +
                          std::string(std::strerror(errno))};
    }
    return Status::success();
}

[[nodiscard]] Status validate_private_directory(
    const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 ||
        !S_ISDIR(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0700)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance directory is not private"};
    }
    return Status::success();
}

[[nodiscard]] Status sync_directory(const std::filesystem::path &path) {
    const int descriptor =
        ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{ErrorCode::io_error,
                      "unable to open tree-v2 directory for fsync: " +
                          std::string(std::strerror(errno))};
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    static_cast<void>(::close(descriptor));
    if (result != 0) {
        return Status{ErrorCode::io_error,
                      "unable to fsync tree-v2 directory: " +
                          std::string(std::strerror(saved))};
    }
    return Status::success();
}

[[nodiscard]] std::filesystem::path live_path(const NamespacePolicy &policy,
                                              const TreeV2GcObject &object) {
    if (object.kind == TreeV2ObjectKind::branch_record)
        return tree_v2_branch_record_path(policy, object.digest);
    if (object.kind == TreeV2ObjectKind::manifest)
        return tree_v2_manifest_path(policy, object.digest);
    return tree_v2_object_path(policy, object.digest);
}

[[nodiscard]] std::string kind_directory(TreeV2ObjectKind kind) {
    if (kind == TreeV2ObjectKind::branch_record) return "records";
    if (kind == TreeV2ObjectKind::manifest) return "manifests";
    return "objects";
}

[[nodiscard]] std::filesystem::path quarantine_path(
    const NamespacePolicy &policy, const TreeV2GcObject &object) {
    return std::filesystem::path(policy.root) / "tree-v2" / "gc-quarantine" /
           kind_directory(object.kind) / lower_hex(object.digest);
}

[[nodiscard]] bool object_less(const TreeV2GcObject &left,
                               const TreeV2GcObject &right) noexcept {
    return left.kind != right.kind ? left.kind < right.kind
                                   : left.digest < right.digest;
}

[[nodiscard]] Result<std::uint64_t>
private_file_bytes(const std::filesystem::path &path, bool allow_empty) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 ||
        !S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) || metadata.st_size < 0 ||
        (!allow_empty && metadata.st_size == 0)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 immutable object is not one private file"};
    }
    return static_cast<std::uint64_t>(metadata.st_size);
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_private_file(
    const std::filesystem::path &path, std::uint64_t maximum_bytes) {
    const int descriptor =
        ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{ErrorCode::io_error,
                      "unable to open quarantined tree-v2 object: " +
                          std::string(std::strerror(errno))};
    }
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0 ||
        !S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid() ||
        metadata.st_nlink != 1 ||
        (metadata.st_mode & static_cast<mode_t>(0777)) !=
            static_cast<mode_t>(0600) ||
        metadata.st_size <= 0 ||
        static_cast<std::uint64_t>(metadata.st_size) > maximum_bytes) {
        static_cast<void>(::close(descriptor));
        return Status{ErrorCode::protocol_error,
                      "quarantined tree-v2 object is not one bounded private "
                      "file"};
    }
    std::vector<std::uint8_t> bytes(
        static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(descriptor, bytes.data() + offset,
                                     bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        const int saved = errno;
        static_cast<void>(::close(descriptor));
        return Status{ErrorCode::io_error,
                      "unable to read quarantined tree-v2 object: " +
                          std::string(std::strerror(saved))};
    }
    if (::close(descriptor) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close quarantined tree-v2 object: " +
                          std::string(std::strerror(errno))};
    }
    return bytes;
}

[[nodiscard]] Status verify_quarantined_object(
    const NamespacePolicy &policy, const TreeV2GcObject &object,
    const std::filesystem::path &path, const security::Sodium &sodium) {
    if (object.kind == TreeV2ObjectKind::file) {
        return verify_tree_v2_object_file(path, object.digest, object.bytes);
    }
    auto bytes = read_private_file(path, policy.quotas.maximum_manifest_bytes);
    if (!bytes) return bytes.status();
    if (object.kind == TreeV2ObjectKind::branch_record) {
        auto head = decode_tree_v2_branch_head(policy, bytes.value());
        if (!head) return head.status();
        const Status signature =
            verify_tree_v2_branch_head(policy, head.value(), sodium);
        if (!signature.ok()) return signature;
        auto digest =
            tree_v2_branch_record_digest(policy, head.value(), sodium);
        if (!digest) return digest.status();
        if (digest.value() != object.digest) {
            return Status{ErrorCode::protocol_error,
                          "quarantined tree-v2 branch identity changed"};
        }
        return Status::success();
    }
    auto manifest = decode_tree_v2_manifest(policy, bytes.value());
    if (!manifest) return manifest.status();
    auto digest = tree_v2_manifest_digest(policy, manifest.value(), sodium);
    if (!digest) return digest.status();
    if (digest.value() != object.digest) {
        return Status{ErrorCode::protocol_error,
                      "quarantined tree-v2 manifest identity changed"};
    }
    return Status::success();
}

[[nodiscard]] Status add_bytes(std::uint64_t &total, std::uint64_t value) {
    if (value > std::numeric_limits<std::uint64_t>::max() - total) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 maintenance byte count overflows"};
    }
    total += value;
    return Status::success();
}

struct GraphWalk {
    const NamespacePolicy &policy;
    const security::Sodium &sodium;
    const SyncNamespaceTransaction &transaction;
    std::set<std::pair<TreeV2ObjectKind, Digest>> visited;
    std::vector<TreeV2GcObject> objects;
    std::map<Digest, std::uint64_t> file_sizes;
    std::set<Digest> selected_files;
    std::uint64_t bytes{0U};
    std::uint64_t declared_file_bytes{0U};
    std::uint64_t selected_file_bytes{0U};
    std::uint64_t floors{0U};

    GraphWalk(const NamespacePolicy &policy_value,
              const security::Sodium &sodium_value,
              const SyncNamespaceTransaction &transaction_value)
        : policy(policy_value), sodium(sodium_value),
          transaction(transaction_value) {}

    [[nodiscard]] Status add(TreeV2ObjectKind kind, const Digest &digest,
                             std::uint64_t object_bytes) {
        if (!visited.emplace(kind, digest).second) return Status::success();
        if (visited.size() > policy.quotas.maximum_objects) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 reachable graph exceeds object quota"};
        }
        const Status counted = add_bytes(bytes, object_bytes);
        if (!counted.ok()) return counted;
        objects.push_back(TreeV2GcObject{kind, digest, object_bytes});
        return Status::success();
    }

    [[nodiscard]] Status walk_manifest(const Digest &digest) {
        if (visited.contains({TreeV2ObjectKind::manifest, digest}))
            return Status::success();
        auto manifest = load_tree_v2_stored_manifest(policy, digest, sodium,
                                                     transaction);
        if (!manifest) return manifest.status();
        auto object_bytes = private_file_bytes(
            tree_v2_manifest_path(policy, digest), false);
        if (!object_bytes) return object_bytes.status();
        Status added =
            add(TreeV2ObjectKind::manifest, digest, object_bytes.value());
        if (!added.ok()) return added;
        for (const TreeV2Entry &entry : manifest.value().entries) {
            if (entry.kind != TreeV2EntryKind::file) continue;
            const auto [known, inserted] =
                file_sizes.emplace(entry.content, entry.content_bytes);
            if (!inserted && known->second != entry.content_bytes) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 digest has conflicting signed sizes"};
            }
            if (inserted) {
                const Status counted =
                    add_bytes(declared_file_bytes, entry.content_bytes);
                if (!counted.ok()) return counted;
            }
            if (!tree_v2_path_selected(policy, entry.path, false)) {
                const std::size_t metadata =
                    visited.size() - selected_files.size();
                if (metadata > policy.quotas.maximum_objects ||
                    file_sizes.size() >
                        policy.quotas.maximum_objects - metadata) {
                    return Status{
                        ErrorCode::resource_exhausted,
                        "tree-v2 reachable graph exceeds object quota"};
                }
                continue;
            }
            if (!selected_files.insert(entry.content).second) continue;
            const Status verified = verify_tree_v2_object_file(
                tree_v2_object_path(policy, entry.content), entry.content,
                entry.content_bytes);
            if (!verified.ok()) return verified;
            added = add(TreeV2ObjectKind::file, entry.content,
                        entry.content_bytes);
            if (!added.ok()) return added;
            const Status counted =
                add_bytes(selected_file_bytes, entry.content_bytes);
            if (!counted.ok()) return counted;
            const std::size_t metadata =
                visited.size() - selected_files.size();
            if (metadata > policy.quotas.maximum_objects ||
                file_sizes.size() >
                    policy.quotas.maximum_objects - metadata) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 reachable graph exceeds object quota"};
            }
        }
        return Status::success();
    }

    [[nodiscard]] Status walk_record(const Digest &record) {
        if (visited.contains({TreeV2ObjectKind::branch_record, record}))
            return Status::success();
        auto snapshot =
            load_tree_v2_stored_record(policy, record, sodium, transaction);
        if (!snapshot) return snapshot.status();
        auto object_bytes = private_file_bytes(
            tree_v2_branch_record_path(policy, record), false);
        if (!object_bytes) return object_bytes.status();
        Status added =
            add(TreeV2ObjectKind::branch_record, record,
                object_bytes.value());
        if (!added.ok()) return added;
        added = walk_manifest(snapshot.value().head.manifest);
        if (!added.ok()) return added;
        if (snapshot.value().head.checkpoint) {
            ++floors;
            return Status::success();
        }
        if (!all_zero(snapshot.value().head.previous)) {
            added = walk_record(snapshot.value().head.previous);
            if (!added.ok()) return added;
        }
        for (const TreeV2Observation &observation :
             snapshot.value().head.observations) {
            added = walk_record(observation.record);
            if (!added.ok()) return added;
        }
        return Status::success();
    }
};

[[nodiscard]] Result<std::vector<TreeV2GcObject>>
inventory(const NamespacePolicy &policy, const security::Sodium &sodium,
          const SyncNamespaceTransaction &transaction) {
    std::vector<TreeV2GcObject> result;
    const std::filesystem::path tree =
        std::filesystem::path(policy.root) / "tree-v2";
    const std::uint64_t maximum_inventory =
        policy.quotas.maximum_objects >
                std::numeric_limits<std::uint64_t>::max() / 3U
            ? std::numeric_limits<std::uint64_t>::max()
            : policy.quotas.maximum_objects * 3U;
    try {
        for (const auto &[directory, suffix, kind] :
             std::array<std::tuple<std::string_view, std::string_view,
                                   TreeV2ObjectKind>,
                        2U>{{{"records", ".branch",
                              TreeV2ObjectKind::branch_record},
                             {"manifests", ".manifest",
                              TreeV2ObjectKind::manifest}}}) {
            for (const auto &entry :
                 std::filesystem::directory_iterator(tree / directory)) {
                std::string name = entry.path().filename().string();
                if (!name.ends_with(suffix)) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 immutable inventory has an "
                                  "unexpected entry"};
                }
                name.resize(name.size() - suffix.size());
                auto digest = parse_digest(name);
                if (!digest) return digest.status();
                if (kind == TreeV2ObjectKind::branch_record) {
                    auto verified = load_tree_v2_stored_record(
                        policy, digest.value(), sodium, transaction);
                    if (!verified) return verified.status();
                } else {
                    auto verified = load_tree_v2_stored_manifest(
                        policy, digest.value(), sodium, transaction);
                    if (!verified) return verified.status();
                }
                auto bytes = private_file_bytes(entry.path(), false);
                if (!bytes) return bytes.status();
                result.push_back({kind, digest.value(), bytes.value()});
            }
        }
        const std::filesystem::path objects = tree / "objects";
        if (std::filesystem::exists(objects)) {
            const Status private_objects = validate_private_directory(objects);
            if (!private_objects.ok()) return private_objects;
            for (const auto &entry :
                 std::filesystem::recursive_directory_iterator(objects)) {
                const std::filesystem::path relative =
                    entry.path().lexically_relative(objects);
                const auto status = entry.symlink_status();
                if (std::filesystem::is_symlink(status)) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object inventory contains a symlink"};
                }
                if (std::filesystem::is_directory(status)) {
                    if (std::distance(relative.begin(), relative.end()) != 1 ||
                        relative.string().size() != 2U ||
                        !parse_digest(relative.string() +
                                      std::string(62U, '0'))) {
                        return Status{ErrorCode::protocol_error,
                                      "tree-v2 object shard is noncanonical"};
                    }
                    const Status private_directory =
                        validate_private_directory(entry.path());
                    if (!private_directory.ok()) return private_directory;
                    continue;
                }
                if (!std::filesystem::is_regular_file(status)) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object inventory entry is not a file"};
                }
                auto component = relative.begin();
                if (component == relative.end()) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object inventory path is empty"};
                }
                const std::string prefix = component->string();
                ++component;
                if (component == relative.end()) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object inventory is not sharded"};
                }
                const std::string tail = component->string();
                ++component;
                if (component != relative.end() || prefix.size() != 2U ||
                    tail.size() != 62U) {
                    return Status{ErrorCode::protocol_error,
                                  "tree-v2 object inventory path is noncanonical"};
                }
                auto digest = parse_digest(prefix + tail);
                if (!digest) return digest.status();
                auto bytes = private_file_bytes(entry.path(), true);
                if (!bytes) return bytes.status();
                const Status verified = verify_tree_v2_object_file(
                    entry.path(), digest.value(), bytes.value());
                if (!verified.ok()) return verified;
                result.push_back({TreeV2ObjectKind::file, digest.value(),
                                  bytes.value()});
            }
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error,
                      "unable to inventory tree-v2 maintenance objects: " +
                          std::string(error.what())};
    }
    if (result.size() > maximum_inventory) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 maintenance inventory exceeds quota"};
    }
    std::sort(result.begin(), result.end(), object_less);
    if (std::adjacent_find(result.begin(), result.end(),
                           [](const auto &left, const auto &right) {
                               return left.kind == right.kind &&
                                      left.digest == right.digest;
                           }) != result.end()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance inventory duplicates an object"};
    }
    return result;
}

[[nodiscard]] Status move_no_replace(const std::filesystem::path &source,
                                     const std::filesystem::path &destination) {
    if (::syscall(SYS_renameat2, AT_FDCWD, source.c_str(), AT_FDCWD,
                  destination.c_str(), RENAME_NOREPLACE) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to atomically move tree-v2 object: " +
                          std::string(std::strerror(errno))};
    }
    return Status::success();
}

} // namespace

Result<std::vector<std::uint8_t>>
encode_tree_v2_maintenance_state(const TreeV2MaintenanceState &state) {
    auto body = encode_body(state);
    if (!body) return body.status();
    body.value().insert(body.value().end(), state.signature.begin(),
                        state.signature.end());
    return body.value();
}

Result<TreeV2MaintenanceState> decode_tree_v2_maintenance_state(
    std::span<const std::uint8_t> bytes, std::uint64_t maximum_pins,
    std::uint64_t maximum_cutoffs) {
    if (bytes.size() < kHeaderBytes + security::kSignatureBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin()) ||
        bytes[8U] != 1U || bytes[9U] == 0U ||
        bytes[9U] > kNamespaceBytes || !all_zero(bytes.subspan(14U, 2U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance header is invalid"};
    }
    const std::uint64_t pins = read_u16(bytes, 10U);
    const std::uint64_t cutoffs = read_u16(bytes, 12U);
    if (pins > maximum_pins || cutoffs > maximum_cutoffs ||
        bytes.size() != kHeaderBytes + pins * 32U +
                            cutoffs * kCutoffBytes +
                            security::kSignatureBytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance count or size is invalid"};
    }
    const std::size_t namespace_bytes = bytes[9U];
    if (!all_zero(bytes.subspan(kNamespaceOffset + namespace_bytes,
                                kNamespaceBytes - namespace_bytes))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance namespace padding is nonzero"};
    }
    TreeV2MaintenanceState state;
    state.namespace_id.assign(
        reinterpret_cast<const char *>(bytes.data() + kNamespaceOffset),
        namespace_bytes);
    state.mutation = read_u64(bytes, 16U);
    read_array(bytes, 24U, state.signer);
    read_array(bytes, 56U, state.previous);
    std::size_t offset = kHeaderBytes;
    state.pins.resize(static_cast<std::size_t>(pins));
    for (Digest &pin : state.pins) {
        read_array(bytes, offset, pin);
        offset += pin.size();
    }
    state.cutoffs.resize(static_cast<std::size_t>(cutoffs));
    for (TreeV2WriterCutoff &cutoff : state.cutoffs) {
        read_array(bytes, offset, cutoff.writer);
        cutoff.generation = read_u64(bytes, offset + 32U);
        read_array(bytes, offset + 40U, cutoff.record);
        offset += kCutoffBytes;
    }
    read_array(bytes, offset, state.signature);
    const Status valid = validate_state(state, maximum_pins, maximum_cutoffs);
    if (!valid.ok()) {
        return Status{ErrorCode::protocol_error, valid.message()};
    }
    auto canonical = encode_tree_v2_maintenance_state(state);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance state is noncanonical"};
    }
    return state;
}

Status verify_tree_v2_maintenance_state(
    const TreeV2MaintenanceState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    if (state.signer != expected_device || all_zero(expected_device)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance signer is not this device"};
    }
    auto body = encode_body(state);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    return sodium.verify_detached(state.signature, digest.value(),
                                  expected_device);
}

TreeV2MaintenanceStore::TreeV2MaintenanceStore(
    std::filesystem::path namespace_root,
    std::shared_ptr<TreeV2StateWitness> witness)
    : root_(std::move(namespace_root)), witness_(std::move(witness)) {}

Result<TreeV2MaintenanceState> TreeV2MaintenanceStore::load(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    if (root_.lexically_normal().string() != policy.root ||
        policy.engine != Engine::tree_v2) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 maintenance root or engine is invalid"};
    }
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    if (witness_) {
        const Status fresh = witness_->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    const std::filesystem::path path =
        root_ / "tree-v2" / "maintenance.state";
    auto bytes = StateStore::read(path);
    if (!bytes) {
        if (bytes.status().code() == ErrorCode::not_found) {
            TreeV2MaintenanceState absent;
            absent.namespace_id = policy.id;
            absent.signer = expected_device;
            return absent;
        }
        return bytes.status();
    }
    const Status private_state = validate_private_file(path);
    if (!private_state.ok()) return private_state;
    auto decoded = decode_tree_v2_maintenance_state(
        bytes.value(), policy.quotas.maximum_retained_revisions,
        policy.writers.size());
    if (!decoded) return decoded.status();
    if (decoded.value().namespace_id != policy.id) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 maintenance namespace does not match policy"};
    }
    const Status verified = verify_tree_v2_maintenance_state(
        decoded.value(), expected_device, sodium);
    if (!verified.ok()) {
        return Status{verified.code(),
                      "tree-v2 maintenance state authentication failed: " +
                          verified.message()};
    }
    for (const TreeV2WriterCutoff &cutoff : decoded.value().cutoffs) {
        if (!std::binary_search(policy.writers.begin(), policy.writers.end(),
                                cutoff.writer)) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 cutoff writer is outside namespace policy"};
        }
    }
    return decoded.value();
}

Result<TreeV2MaintenanceState> TreeV2MaintenanceStore::commit(
    const NamespacePolicy &policy, TreeV2MaintenanceState state,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    state.namespace_id = policy.id;
    state.signer = identity.public_key();
    auto body = encode_body(state);
    if (!body) return body.status();
    auto digest = sodium.hash(kSignatureDomain, body.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    state.signature = signature.value();
    auto encoded = encode_tree_v2_maintenance_state(state);
    if (!encoded) return encoded.status();
    const auto store = [&]() {
        return StateStore::write_atomic(
            root_ / "tree-v2" / "maintenance.state", encoded.value());
    };
    Status stored;
    if (witness_) {
        stored = witness_->transition(
            policy, transaction,
            [&state](const TreeV2FreshnessState &current) {
                TreeV2FreshnessState next = current;
                next.maintenance = state;
                return Result<TreeV2FreshnessState>{std::move(next)};
            },
            store);
    } else {
        stored = store();
    }
    if (!stored.ok()) return stored;
    return state;
}

Result<TreeV2MaintenanceState> TreeV2MaintenanceStore::pin(
    const NamespacePolicy &policy, const Digest &record,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto snapshot = load_tree_v2_stored_record(policy, record, sodium,
                                               transaction);
    if (!snapshot) return snapshot.status();
    auto state = load(policy, identity.public_key(), sodium, transaction);
    if (!state) return state.status();
    if (std::binary_search(state.value().pins.begin(), state.value().pins.end(),
                           record))
        return state.value();
    if (state.value().pins.size() >=
        policy.quotas.maximum_retained_revisions) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 retention pin bound is exhausted"};
    }
    TreeV2MaintenanceState next = state.value();
    if (next.mutation != 0U) {
        auto prior = state_record(next, sodium);
        if (!prior) return prior.status();
        next.previous = prior.value();
    }
    ++next.mutation;
    next.pins.push_back(record);
    std::sort(next.pins.begin(), next.pins.end());
    return commit(policy, std::move(next), identity, sodium, transaction);
}

Result<TreeV2MaintenanceState> TreeV2MaintenanceStore::unpin(
    const NamespacePolicy &policy, const Digest &record,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto state = load(policy, identity.public_key(), sodium, transaction);
    if (!state) return state.status();
    const auto found = std::lower_bound(state.value().pins.begin(),
                                        state.value().pins.end(), record);
    if (found == state.value().pins.end() || *found != record)
        return state.value();
    TreeV2MaintenanceState next = state.value();
    auto prior = state_record(next, sodium);
    if (!prior) return prior.status();
    next.previous = prior.value();
    ++next.mutation;
    next.pins.erase(std::lower_bound(next.pins.begin(), next.pins.end(),
                                     record));
    return commit(policy, std::move(next), identity, sodium, transaction);
}

Result<TreeV2MaintenanceState> TreeV2MaintenanceStore::set_cutoff(
    const NamespacePolicy &policy, const TreeV2WriterCutoff &cutoff,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) const {
    auto state = load(policy, identity.public_key(), sodium, transaction);
    if (!state) return state.status();
    const auto found = std::lower_bound(
        state.value().cutoffs.begin(), state.value().cutoffs.end(),
        cutoff.writer, [](const TreeV2WriterCutoff &candidate,
                          const PrincipalId &writer) {
            return candidate.writer < writer;
        });
    if (found != state.value().cutoffs.end() &&
        found->writer == cutoff.writer) {
        if (*found == cutoff) return state.value();
        return Status{ErrorCode::protocol_error,
                      "tree-v2 writer already has a different terminal cutoff"};
    }
    if (state.value().cutoffs.size() >= policy.writers.size()) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 writer cutoff bound is exhausted"};
    }
    TreeV2MaintenanceState next = state.value();
    if (next.mutation != 0U) {
        auto prior = state_record(next, sodium);
        if (!prior) return prior.status();
        next.previous = prior.value();
    }
    ++next.mutation;
    next.cutoffs.push_back(cutoff);
    std::sort(next.cutoffs.begin(), next.cutoffs.end(),
              [](const auto &left, const auto &right) {
                  return left.writer < right.writer;
              });
    return commit(policy, std::move(next), identity, sodium, transaction);
}

Status admit_tree_v2_writer_record(
    const NamespacePolicy &policy, const TreeV2BranchHead &head,
    const Digest &record, const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    TreeV2MaintenanceStore store{std::filesystem::path(policy.root)};
    auto state = store.load(policy, expected_device, sodium, transaction);
    if (!state) return state.status();
    const auto cutoff = std::lower_bound(
        state.value().cutoffs.begin(), state.value().cutoffs.end(), head.writer,
        [](const TreeV2WriterCutoff &candidate, const PrincipalId &writer) {
            return candidate.writer < writer;
        });
    if (cutoff == state.value().cutoffs.end() ||
        cutoff->writer != head.writer)
        return Status::success();
    if (cutoff->generation == head.generation && cutoff->record == record)
        return Status::success();
    return Status{ErrorCode::protocol_error,
                  "tree-v2 branch is outside its terminal writer cutoff"};
}

Result<TreeV2GcPlan> plan_tree_v2_gc(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    if (witness) {
        const Status fresh = witness->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    TreeV2BranchStore branches{std::filesystem::path(policy.root)};
    auto frontier = branches.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    GraphWalk walk{policy, sodium, transaction};
    for (const TreeV2Snapshot &snapshot : frontier.value()) {
        auto record = tree_v2_branch_record_digest(policy, snapshot.head,
                                                   sodium);
        if (!record) return record.status();
        const Status walked = walk.walk_record(record.value());
        if (!walked.ok()) return walked;
    }
    TreeV2MaintenanceStore maintenance{std::filesystem::path(policy.root)};
    auto state = maintenance.load(policy, expected_device, sodium, transaction);
    if (!state) return state.status();
    for (const Digest &pin : state.value().pins) {
        const Status walked = walk.walk_record(pin);
        if (!walked.ok()) return walked;
    }
    TreeV2WorkspaceStore workspaces{std::filesystem::path(policy.root)};
    auto workspace = workspaces.load(policy, expected_device, sodium);
    if (!workspace) return workspace.status();
    if (workspace.value()) {
        // A derived merge is deliberately retained without publishing an
        // acknowledgement-only branch. The signed workspace journal is
        // therefore an independent GC root, not merely a cache of branch
        // frontier pointers.
        Status walked =
            walk.walk_manifest(workspace.value()->active_manifest);
        if (!walked.ok()) return walked;
        if (workspace.value()->phase ==
            TreeV2WorkspacePhase::pending_exchange) {
            walked = walk.walk_manifest(workspace.value()->pending_manifest);
            if (!walked.ok()) return walked;
            walked = walk.walk_manifest(
                workspace.value()->pending_worktree_manifest);
            if (!walked.ok()) return walked;
        }
        for (const TreeV2Observation &observation :
             workspace.value()->active_frontier) {
            walked = walk.walk_record(observation.record);
            if (!walked.ok()) return walked;
        }
        for (const TreeV2Observation &observation :
             workspace.value()->pending_frontier) {
            walked = walk.walk_record(observation.record);
            if (!walked.ok()) return walked;
        }
    }
    auto stored = inventory(policy, sodium, transaction);
    if (!stored) return stored.status();
    std::sort(walk.objects.begin(), walk.objects.end(), object_less);
    TreeV2GcPlan plan;
    plan.reachable = walk.objects;
    plan.reachable_bytes = walk.bytes;
    plan.checkpoint_floors = walk.floors;
    plan.pinned_roots = state.value().pins.size();
    plan.manifest_file_objects = walk.file_sizes.size();
    plan.selected_file_objects = walk.selected_files.size();
    plan.skipped_file_objects =
        walk.file_sizes.size() - walk.selected_files.size();
    plan.selected_file_bytes = walk.selected_file_bytes;
    plan.skipped_file_bytes =
        walk.declared_file_bytes - walk.selected_file_bytes;
    plan.custody_complete = policy.projection.includes.empty() &&
                            policy.projection.excludes.empty();
    plan.workspace_authenticated = workspace.value().has_value();
    plan.maintenance_authenticated = state.value().mutation != 0U;
    for (const TreeV2GcObject &object : stored.value()) {
        const auto live = std::lower_bound(plan.reachable.begin(),
                                           plan.reachable.end(), object,
                                           object_less);
        if (live != plan.reachable.end() && live->kind == object.kind &&
            live->digest == object.digest) {
            if (live->bytes != object.bytes) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 reachable object size changed"};
            }
            continue;
        }
        plan.candidates.push_back(object);
        const Status counted = add_bytes(plan.candidate_bytes, object.bytes);
        if (!counted.ok()) return counted;
    }
    return plan;
}

TreeV2GcOutcome quarantine_tree_v2_gc(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    auto planned = plan_tree_v2_gc(policy, expected_device, sodium,
                                   transaction, witness);
    if (!planned)
        return TreeV2GcOutcome{planned.status(), {}, 0U, 0U};
    TreeV2GcOutcome outcome{Status::success(), planned.value(), 0U, 0U};
    const std::filesystem::path quarantine =
        std::filesystem::path(policy.root) / "tree-v2" / "gc-quarantine";
    Status prepared = ensure_private_directory(quarantine);
    if (!prepared.ok()) {
        outcome.status = prepared;
        return outcome;
    }
    for (const char *directory : {"records", "manifests", "objects"}) {
        prepared = ensure_private_directory(quarantine / directory);
        if (!prepared.ok()) {
            outcome.status = prepared;
            return outcome;
        }
    }
    for (const TreeV2GcObject &object : outcome.plan.candidates) {
        const std::filesystem::path source = live_path(policy, object);
        const std::filesystem::path destination =
            quarantine_path(policy, object);
        const Status moved = move_no_replace(source, destination);
        if (!moved.ok()) {
            outcome.status = moved;
            return outcome;
        }
        ++outcome.moved;
        outcome.moved_bytes += object.bytes;
        const Status source_synced = sync_directory(source.parent_path());
        const Status destination_synced =
            sync_directory(destination.parent_path());
        if (!source_synced.ok() || !destination_synced.ok()) {
            outcome.status = !source_synced.ok() ? source_synced
                                                 : destination_synced;
            return outcome;
        }
    }
    return outcome;
}

TreeV2RestoreOutcome restore_tree_v2_quarantine(
    const NamespacePolicy &policy, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return TreeV2RestoreOutcome{held};
    if (witness) {
        const Status fresh = witness->verify_read(policy, transaction);
        if (!fresh.ok()) return TreeV2RestoreOutcome{fresh};
    }
    TreeV2RestoreOutcome outcome{Status::success()};
    const std::filesystem::path quarantine =
        std::filesystem::path(policy.root) / "tree-v2" / "gc-quarantine";
    if (!std::filesystem::exists(quarantine)) return outcome;
    const Status private_quarantine = validate_private_directory(quarantine);
    if (!private_quarantine.ok()) {
        outcome.status = private_quarantine;
        return outcome;
    }
    try {
        for (const auto &[directory, kind] :
             std::array<std::pair<std::string_view, TreeV2ObjectKind>, 3U>{{
                 {"records", TreeV2ObjectKind::branch_record},
                 {"manifests", TreeV2ObjectKind::manifest},
                 {"objects", TreeV2ObjectKind::file}}}) {
            const std::filesystem::path source_directory =
                quarantine / directory;
            if (!std::filesystem::exists(source_directory)) continue;
            const Status private_source =
                validate_private_directory(source_directory);
            if (!private_source.ok()) {
                outcome.status = private_source;
                return outcome;
            }
            for (const auto &entry :
                 std::filesystem::directory_iterator(source_directory)) {
                auto digest = parse_digest(entry.path().filename().string());
                if (!digest) {
                    outcome.status = digest.status();
                    return outcome;
                }
                auto bytes = private_file_bytes(
                    entry.path(), kind == TreeV2ObjectKind::file);
                if (!bytes) {
                    outcome.status = bytes.status();
                    return outcome;
                }
                TreeV2GcObject object{kind, digest.value(), bytes.value()};
                const Status verified = verify_quarantined_object(
                    policy, object, entry.path(), sodium);
                if (!verified.ok()) {
                    outcome.status = verified;
                    return outcome;
                }
                const std::filesystem::path destination =
                    live_path(policy, object);
                if (std::filesystem::exists(destination)) {
                    ++outcome.already_present;
                    continue;
                }
                Status prepared = ensure_private_directory(
                    destination.parent_path());
                if (!prepared.ok()) {
                    outcome.status = prepared;
                    return outcome;
                }
                const Status moved = move_no_replace(entry.path(), destination);
                if (!moved.ok()) {
                    outcome.status = moved;
                    return outcome;
                }
                ++outcome.restored;
                outcome.restored_bytes += bytes.value();
                const Status source_synced =
                    sync_directory(entry.path().parent_path());
                const Status destination_synced =
                    sync_directory(destination.parent_path());
                if (!source_synced.ok() || !destination_synced.ok()) {
                    outcome.status = !source_synced.ok() ? source_synced
                                                         : destination_synced;
                    return outcome;
                }
            }
        }
    } catch (const std::filesystem::filesystem_error &error) {
        outcome.status =
            Status{ErrorCode::io_error,
                   "unable to restore tree-v2 quarantine: " +
                       std::string(error.what())};
        return outcome;
    }
    // Restored immutable records are self-authenticating; validate the whole
    // store before reporting success.
    TreeV2BranchStore store{std::filesystem::path(policy.root)};
    auto frontier = store.load_frontier(policy, sodium, transaction);
    if (!frontier) outcome.status = frontier.status();
    return outcome;
}

Result<TreeV2WriterCutoff> cutoff_tree_v2_writer(
    const NamespacePolicy &policy, const PrincipalId &target,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    if (target == identity.public_key() ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            target)) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 cutoff target is not a remote namespace writer"};
    }
    TreeV2BranchStore branches{std::filesystem::path(policy.root),
                               std::nullopt, witness};
    auto frontier = branches.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    TreeV2MaintenanceStore maintenance{std::filesystem::path(policy.root),
                                       witness};
    auto state = maintenance.load(policy, identity.public_key(), sodium,
                                  transaction);
    if (!state) return state.status();
    const auto existing = std::lower_bound(
        state.value().cutoffs.begin(), state.value().cutoffs.end(), target,
        [](const TreeV2WriterCutoff &candidate, const PrincipalId &writer) {
            return candidate.writer < writer;
        });

    const std::filesystem::path branches_directory =
        std::filesystem::path(policy.root) / "tree-v2" / "branches";
    const std::filesystem::path retired_directory =
        std::filesystem::path(policy.root) / "tree-v2" / "retired-branches";
    const auto retire_pointer = [&](const TreeV2WriterCutoff &cutoff) {
        Status prepared = ensure_private_directory(retired_directory);
        if (!prepared.ok()) return prepared;
        const std::filesystem::path source =
            branches_directory / (lower_hex(target) + ".branch");
        const std::filesystem::path destination =
            retired_directory / (lower_hex(target) + ".branch");
        const bool source_exists = std::filesystem::exists(source);
        const bool destination_exists = std::filesystem::exists(destination);
        if (source_exists && destination_exists) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 live and retired branch both exist"};
        }
        if (destination_exists) {
            auto bytes = private_file_bytes(destination, false);
            if (!bytes) return bytes.status();
            const TreeV2GcObject object{TreeV2ObjectKind::branch_record,
                                        cutoff.record, bytes.value()};
            return verify_quarantined_object(policy, object, destination,
                                             sodium);
        }
        if (!source_exists) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 terminal branch pointer is missing"};
        }
        const auto current = std::find_if(
            frontier.value().begin(), frontier.value().end(),
            [&target](const TreeV2Snapshot &snapshot) {
                return snapshot.head.writer == target;
            });
        if (current == frontier.value().end()) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 terminal branch pointer is not in the "
                          "verified frontier"};
        }
        auto current_record = tree_v2_branch_record_digest(
            policy, current->head, sodium);
        if (!current_record || current->head.generation != cutoff.generation ||
            current_record.value() != cutoff.record) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 terminal branch pointer changed"};
        }
        const auto move = [&]() {
            const Status moved = move_no_replace(source, destination);
            if (!moved.ok()) return moved;
            const Status source_synced = sync_directory(branches_directory);
            if (!source_synced.ok()) return source_synced;
            return sync_directory(retired_directory);
        };
        Status moved;
        if (witness) {
            moved = witness->transition(
                policy, transaction,
                [&target](const TreeV2FreshnessState &current_state)
                    -> Result<TreeV2FreshnessState> {
                    TreeV2FreshnessState next = current_state;
                    const auto found = std::lower_bound(
                        next.frontier.begin(), next.frontier.end(), target,
                        [](const TreeV2Observation &candidate,
                           const PrincipalId &writer) {
                            return candidate.writer < writer;
                        });
                    if (found == next.frontier.end() ||
                        found->writer != target) {
                        return Status{
                            ErrorCode::protocol_error,
                            "tree-v2 cutoff witness cannot find live writer"};
                    }
                    next.frontier.erase(found);
                    return next;
                },
                move);
        } else {
            moved = move();
        }
        if (!moved.ok()) return moved;
        return Status::success();
    };

    if (existing != state.value().cutoffs.end() &&
        existing->writer == target) {
        const Status retired = retire_pointer(*existing);
        if (!retired.ok()) return retired;
        return *existing;
    }
    const auto target_head = std::find_if(
        frontier.value().begin(), frontier.value().end(),
        [&target](const TreeV2Snapshot &snapshot) {
            return snapshot.head.writer == target;
        });
    const auto local = std::find_if(
        frontier.value().begin(), frontier.value().end(),
        [&identity](const TreeV2Snapshot &snapshot) {
            return snapshot.head.writer == identity.public_key();
        });
    if (target_head == frontier.value().end() ||
        local == frontier.value().end() || !local->head.checkpoint) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 cutoff requires target history and a current "
                      "local checkpoint"};
    }
    auto target_record =
        tree_v2_branch_record_digest(policy, target_head->head, sodium);
    if (!target_record) return target_record.status();
    const auto observed = std::find_if(
        local->head.observations.begin(), local->head.observations.end(),
        [&target, &target_record, &target_head](const auto &observation) {
            return observation.writer == target &&
                   observation.generation == target_head->head.generation &&
                   observation.record == target_record.value();
        });
    if (observed == local->head.observations.end()) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 local checkpoint does not subsume the cutoff "
                      "writer"};
    }
    const TreeV2WriterCutoff cutoff{target, target_head->head.generation,
                                    target_record.value()};
    auto committed = maintenance.set_cutoff(policy, cutoff, identity, sodium,
                                            transaction);
    if (!committed) return committed.status();
    const Status retired = retire_pointer(cutoff);
    if (!retired.ok()) return retired;
    return cutoff;
}

} // namespace iotox::sync
