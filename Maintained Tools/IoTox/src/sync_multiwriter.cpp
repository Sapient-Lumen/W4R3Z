#include "iotox/sync_multiwriter.hpp"

#include <algorithm>
#include <array>
#include <functional>
#include <limits>
#include <map>
#include <set>
#include <utility>

namespace iotox::sync {
namespace {

constexpr std::array<std::uint8_t, 8U> kManifestMagic = {'I', 'O', 'T', 'X',
                                                         'T', 'V', 'M', '1'};
constexpr std::array<std::uint8_t, 8U> kBranchMagic = {'I', 'O', 'T', 'X',
                                                       'T', 'V', 'B', '1'};
constexpr std::size_t kManifestHeaderBytes = 16U;
constexpr std::size_t kManifestEntryFixedBytes = 84U;
constexpr std::size_t kBranchBodyFixedBytes = 192U;
constexpr std::size_t kBranchObservationBytes = 72U;
constexpr std::size_t kBranchNamespaceBytes = 64U;
constexpr std::string_view kManifestDigestDomain =
    "iotox-sync-tree-v2-manifest-v1";
constexpr std::string_view kManifestChunkDigestDomain =
    "iotox-sync-tree-v2-manifest-chunk-v1";
constexpr std::string_view kManifestChunkRootDomain =
    "iotox-sync-tree-v2-manifest-chunk-root-v1";
constexpr std::size_t kManifestDigestChunkBytes = 60U * 1024U;
constexpr std::string_view kBranchSignatureDomain =
    "iotox-sync-tree-v2-branch-signature-v1";
constexpr std::string_view kBranchRecordDomain =
    "iotox-sync-tree-v2-branch-record-v1";
constexpr std::string_view kCheckpointSignatureDomain =
    "iotox-sync-tree-v2-checkpoint-signature-v2";
constexpr std::string_view kCheckpointRecordDomain =
    "iotox-sync-tree-v2-checkpoint-record-v2";

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

[[nodiscard]] std::uint8_t
canonical_owner_mode(const TreeV2Entry &entry) noexcept {
    if (entry.kind != TreeV2EntryKind::file) return 0U;
    return entry.owner_mode != 0U
               ? entry.owner_mode
               : static_cast<std::uint8_t>(entry.executable ? 7U : 6U);
}

[[nodiscard]] bool writer_allowed(const NamespacePolicy &policy,
                                  const PrincipalId &writer) {
    return std::binary_search(policy.writers.begin(), policy.writers.end(),
                              writer);
}

void write_u16(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint16_t value) {
    bytes[offset] = static_cast<std::uint8_t>(value >> 8U);
    bytes[offset + 1U] = static_cast<std::uint8_t>(value);
}

void write_u32(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint32_t value) {
    for (std::size_t index = 0U; index < 4U; ++index) {
        bytes[offset + index] =
            static_cast<std::uint8_t>(value >> (24U - index * 8U));
    }
}

void write_u64(std::span<std::uint8_t> bytes, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        bytes[offset + index] =
            static_cast<std::uint8_t>(value >> (56U - index * 8U));
    }
}

[[nodiscard]] std::uint16_t read_u16(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) | bytes[offset + 1U]);
}

[[nodiscard]] std::uint32_t read_u32(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index)
        value = (value << 8U) | bytes[offset + index];
    return value;
}

[[nodiscard]] std::uint64_t read_u64(std::span<const std::uint8_t> bytes,
                                     std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index)
        value = (value << 8U) | bytes[offset + index];
    return value;
}

template <std::size_t Size>
void write_array(std::span<std::uint8_t> bytes, std::size_t offset,
                 const std::array<std::uint8_t, Size> &value) {
    std::copy(value.begin(), value.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(offset));
}

template <std::size_t Size>
void read_array(std::span<const std::uint8_t> bytes, std::size_t offset,
                std::array<std::uint8_t, Size> &value) {
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), Size,
                value.begin());
}

[[nodiscard]] bool entry_less(const TreeV2Entry &left,
                              const TreeV2Entry &right) {
    if (left.path != right.path) return left.path < right.path;
    if (left.origin.writer != right.origin.writer)
        return left.origin.writer < right.origin.writer;
    if (left.origin.generation != right.origin.generation)
        return left.origin.generation < right.origin.generation;
    if (left.kind != right.kind) return left.kind < right.kind;
    if (canonical_owner_mode(left) != canonical_owner_mode(right))
        return canonical_owner_mode(left) < canonical_owner_mode(right);
    if (left.content != right.content) return left.content < right.content;
    return left.content_bytes < right.content_bytes;
}

[[nodiscard]] bool same_path_origin(const TreeV2Entry &left,
                                    const TreeV2Entry &right) {
    return left.path == right.path && left.origin == right.origin;
}

[[nodiscard]] bool same_payload(const TreeV2Entry &left,
                                const TreeV2Entry &right) noexcept {
    return left.kind == right.kind && left.content == right.content &&
           left.content_bytes == right.content_bytes &&
           canonical_owner_mode(left) == canonical_owner_mode(right);
}

[[nodiscard]] bool observation_less(const TreeV2Observation &left,
                                    const TreeV2Observation &right) {
    return left.writer < right.writer;
}

[[nodiscard]] bool valid_kind(TreeV2EntryKind kind) noexcept {
    return kind == TreeV2EntryKind::directory ||
           kind == TreeV2EntryKind::file || kind == TreeV2EntryKind::tombstone;
}

[[nodiscard]] Result<security::Digest>
branch_signing_digest(const NamespacePolicy &policy,
                      const TreeV2BranchHead &head,
                      const security::Sodium &sodium) {
    auto body = encode_tree_v2_branch_body(policy, head);
    if (!body) return body.status();
    return sodium.hash(head.checkpoint ? kCheckpointSignatureDomain
                                       : kBranchSignatureDomain,
                       body.value());
}

[[nodiscard]] int projection_rank(TreeV2EntryKind kind) noexcept {
    switch (kind) {
    case TreeV2EntryKind::directory:
        return 0;
    case TreeV2EntryKind::file:
        return 1;
    case TreeV2EntryKind::tombstone:
        return 2;
    }
    return 3;
}

using TreeV2PathIndex = std::map<std::string, std::vector<TreeV2Entry>>;

[[nodiscard]] TreeV2PathIndex
index_tree_v2_manifest_paths(const TreeV2Manifest &manifest,
                             std::set<std::string> *paths = nullptr) {
    TreeV2PathIndex result;
    for (auto first = manifest.entries.begin();
         first != manifest.entries.end();) {
        const auto last = std::find_if(
            first, manifest.entries.end(), [&first](const TreeV2Entry &entry) {
                return entry.path != first->path;
            });
        auto &group = result[first->path];
        group.insert(group.end(), first, last);
        if (paths != nullptr) paths->insert(first->path);
        first = last;
    }
    return result;
}

} // namespace

bool TreeV2Entry::operator==(const TreeV2Entry &other) const noexcept {
    return path == other.path && kind == other.kind && origin == other.origin &&
           content == other.content && content_bytes == other.content_bytes &&
           canonical_owner_mode(*this) == canonical_owner_mode(other);
}

std::string_view tree_v2_entry_kind_name(TreeV2EntryKind kind) noexcept {
    switch (kind) {
    case TreeV2EntryKind::directory:
        return "directory";
    case TreeV2EntryKind::file:
        return "file";
    case TreeV2EntryKind::tombstone:
        return "tombstone";
    }
    return "unknown";
}

bool valid_tree_v2_path(std::string_view path) noexcept {
    if (path.empty() || path.size() > kTreeV2MaximumPathBytes ||
        path.front() == '/' || path.back() == '/') {
        return false;
    }
    std::size_t offset = 0U;
    bool first = true;
    while (offset < path.size()) {
        const std::size_t end = path.find('/', offset);
        const std::size_t count =
            end == std::string_view::npos ? path.size() - offset : end - offset;
        if (count == 0U) return false;
        const std::string_view component = path.substr(offset, count);
        if (component == "." || component == ".." ||
            (first && component == kTreeV2ConflictRoot)) {
            return false;
        }
        for (const char raw_byte : component) {
            const auto byte = static_cast<unsigned char>(raw_byte);
            if (byte == 0U || byte == '\r' || byte == '\n' || byte == 0x7fU)
                return false;
        }
        first = false;
        if (end == std::string_view::npos) break;
        offset = end + 1U;
    }
    return true;
}

Status validate_tree_v2_manifest(const NamespacePolicy &policy,
                                 const TreeV2Manifest &manifest) {
    const Status valid_policy = validate_namespace_policy(policy);
    if (!valid_policy.ok()) return valid_policy;
    if (policy.engine != Engine::tree_v2) {
        return Status{ErrorCode::unsupported,
                      "tree-v2 manifest requires a tree-v2 namespace"};
    }
    if (manifest.entries.size() > policy.quotas.maximum_objects) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 manifest entry population exceeds quota"};
    }
    std::uint64_t content_bytes = 0U;
    std::uint64_t encoded_bytes = kManifestHeaderBytes;
    std::set<std::string, std::less<>> directory_paths;
    for (std::size_t index = 0U; index < manifest.entries.size(); ++index) {
        const TreeV2Entry &entry = manifest.entries[index];
        if (!valid_tree_v2_path(entry.path) || !valid_kind(entry.kind) ||
            entry.origin.generation == 0U || all_zero(entry.origin.writer) ||
            !writer_allowed(policy, entry.origin.writer)) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 manifest entry identity is invalid"};
        }
        if (entry.kind == TreeV2EntryKind::file) {
            if (all_zero(entry.content) ||
                entry.content_bytes > policy.quotas.maximum_artifact_bytes) {
                return Status{
                    ErrorCode::invalid_argument,
                    "tree-v2 file content identity or size is invalid"};
            }
            if (entry.content_bytes >
                std::numeric_limits<std::uint64_t>::max() - content_bytes) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 content byte population overflows"};
            }
            content_bytes += entry.content_bytes;
            if (entry.owner_mode != 0U &&
                (entry.owner_mode < 4U || entry.owner_mode > 7U ||
                 entry.executable != ((entry.owner_mode & 1U) != 0U))) {
                return Status{ErrorCode::invalid_argument,
                              "tree-v2 file owner mode is invalid"};
            }
        } else if (!all_zero(entry.content) || entry.content_bytes != 0U ||
                   entry.executable || entry.owner_mode != 0U) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 directory or tombstone carries file state"};
        }
        if (entry.kind == TreeV2EntryKind::directory)
            directory_paths.insert(entry.path);
        if (content_bytes > policy.quotas.maximum_artifact_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 live and conflict content exceeds quota"};
        }
        if (entry.path.size() > std::numeric_limits<std::uint64_t>::max() -
                                    kManifestEntryFixedBytes - encoded_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 manifest byte population overflows"};
        }
        encoded_bytes += kManifestEntryFixedBytes + entry.path.size();
        if (encoded_bytes > policy.quotas.maximum_manifest_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 manifest exceeds its byte quota"};
        }
        if (index != 0U) {
            const TreeV2Entry &previous = manifest.entries[index - 1U];
            if (!entry_less(previous, entry) ||
                same_path_origin(previous, entry)) {
                return Status{ErrorCode::invalid_argument,
                              "tree-v2 manifest entries are not canonical"};
            }
        }
    }
    std::string_view candidate_path;
    std::vector<PrincipalId> candidate_writers;
    for (const TreeV2Entry &entry : manifest.entries) {
        if (candidate_path != entry.path) {
            candidate_path = entry.path;
            candidate_writers.clear();
        }
        if (candidate_writers.size() >= kTreeV2MaximumValuesPerPath ||
            std::find(candidate_writers.begin(), candidate_writers.end(),
                      entry.origin.writer) != candidate_writers.end()) {
            return Status{
                ErrorCode::resource_exhausted,
                "tree-v2 path has duplicated-writer or excessive candidates"};
        }
        candidate_writers.push_back(entry.origin.writer);
        if (entry.kind == TreeV2EntryKind::tombstone) continue;
        std::size_t separator = entry.path.find('/');
        while (separator != std::string::npos) {
            const std::string_view parent(entry.path.data(), separator);
            if (directory_paths.find(parent) == directory_paths.end()) {
                return Status{ErrorCode::invalid_argument,
                              "tree-v2 live entry lacks a directory ancestor"};
            }
            separator = entry.path.find('/', separator + 1U);
        }
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_manifest(const NamespacePolicy &policy,
                        const TreeV2Manifest &manifest) {
    const Status valid = validate_tree_v2_manifest(policy, manifest);
    if (!valid.ok()) return valid;
    std::array<std::uint8_t, kManifestHeaderBytes> header{};
    std::copy(kManifestMagic.begin(), kManifestMagic.end(), header.begin());
    const bool owner_mode = std::any_of(
        manifest.entries.begin(), manifest.entries.end(),
        [](const TreeV2Entry &entry) { return entry.owner_mode != 0U; });
    header[8U] = owner_mode ? kTreeV2OwnerModeManifestVersion
                            : kTreeV2ManifestVersion;
    write_u32(header, 12U, static_cast<std::uint32_t>(manifest.entries.size()));
    std::vector<std::uint8_t> output(header.begin(), header.end());
    output.reserve(static_cast<std::size_t>(
        std::min<std::uint64_t>(policy.quotas.maximum_manifest_bytes,
                                std::numeric_limits<std::size_t>::max())));
    for (const TreeV2Entry &entry : manifest.entries) {
        std::array<std::uint8_t, kManifestEntryFixedBytes> record{};
        record[0U] = static_cast<std::uint8_t>(entry.kind);
        record[1U] = owner_mode && entry.kind == TreeV2EntryKind::file
                         ? (entry.owner_mode != 0U
                                ? entry.owner_mode
                                : static_cast<std::uint8_t>(
                                      entry.executable ? 7U : 6U))
                         : static_cast<std::uint8_t>(entry.executable ? 1U
                                                                      : 0U);
        write_u16(record, 2U, static_cast<std::uint16_t>(entry.path.size()));
        write_u64(record, 4U, entry.origin.generation);
        write_array(record, 12U, entry.origin.writer);
        write_array(record, 44U, entry.content);
        write_u64(record, 76U, entry.content_bytes);
        output.insert(output.end(), record.begin(), record.end());
        output.insert(output.end(), entry.path.begin(), entry.path.end());
    }
    return output;
}

Result<TreeV2Manifest>
decode_tree_v2_manifest(const NamespacePolicy &policy,
                        std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kManifestHeaderBytes ||
        bytes.size() > policy.quotas.maximum_manifest_bytes ||
        !std::equal(kManifestMagic.begin(), kManifestMagic.end(),
                    bytes.begin()) ||
        (bytes[8U] != kTreeV2ManifestVersion &&
         bytes[8U] != kTreeV2OwnerModeManifestVersion) ||
        !all_zero(bytes.subspan(9U, 3U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 manifest header or size is invalid"};
    }
    const bool owner_mode = bytes[8U] == kTreeV2OwnerModeManifestVersion;
    const std::uint32_t count = read_u32(bytes, 12U);
    if (count > policy.quotas.maximum_objects) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 manifest entry population exceeds quota"};
    }
    TreeV2Manifest manifest;
    manifest.entries.reserve(count);
    std::size_t offset = kManifestHeaderBytes;
    for (std::uint32_t index = 0U; index < count; ++index) {
        if (offset > bytes.size() ||
            bytes.size() - offset < kManifestEntryFixedBytes) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 manifest entry is truncated"};
        }
        const std::size_t path_bytes = read_u16(bytes, offset + 2U);
        if (path_bytes == 0U || path_bytes > kTreeV2MaximumPathBytes ||
            path_bytes > bytes.size() - offset - kManifestEntryFixedBytes) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 manifest path length is invalid"};
        }
        TreeV2Entry entry;
        entry.kind = static_cast<TreeV2EntryKind>(bytes[offset]);
        const std::uint8_t encoded_mode = bytes[offset + 1U];
        if ((!owner_mode && encoded_mode > 1U) ||
            (owner_mode &&
             ((entry.kind == TreeV2EntryKind::file &&
               (encoded_mode < 4U || encoded_mode > 7U)) ||
              (entry.kind != TreeV2EntryKind::file && encoded_mode != 0U)))) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 manifest metadata mode is invalid"};
        }
        entry.owner_mode = owner_mode ? encoded_mode : 0U;
        entry.executable = owner_mode ? (encoded_mode & 1U) != 0U
                                      : encoded_mode == 1U;
        entry.origin.generation = read_u64(bytes, offset + 4U);
        read_array(bytes, offset + 12U, entry.origin.writer);
        read_array(bytes, offset + 44U, entry.content);
        entry.content_bytes = read_u64(bytes, offset + 76U);
        entry.path.assign(reinterpret_cast<const char *>(
                              bytes.data() + offset + kManifestEntryFixedBytes),
                          path_bytes);
        manifest.entries.push_back(std::move(entry));
        offset += kManifestEntryFixedBytes + path_bytes;
    }
    if (offset != bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 manifest has trailing bytes"};
    }
    const Status valid = validate_tree_v2_manifest(policy, manifest);
    if (!valid.ok()) return valid;
    auto canonical = encode_tree_v2_manifest(policy, manifest);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 manifest is not canonical"};
    }
    return manifest;
}

Result<Digest> tree_v2_manifest_digest(const NamespacePolicy &policy,
                                       const TreeV2Manifest &manifest,
                                       const security::Sodium &sodium) {
    auto encoded = encode_tree_v2_manifest(policy, manifest);
    if (!encoded) return encoded.status();
    auto direct = sodium.hash(kManifestDigestDomain, encoded.value());
    if (direct) return direct;
    if (direct.status().code() != ErrorCode::invalid_argument) {
        return direct.status();
    }

    // The original digest remains byte-for-byte authoritative whenever the
    // complete manifest fits Sodium::hash. Larger manifests were previously
    // admitted by namespace quotas but impossible to identify. Commit them as
    // bounded indexed chunks under distinct domains, then commit the ordered
    // leaf vector. No formerly publishable manifest changes identity.
    const std::size_t chunk_count =
        (encoded.value().size() + kManifestDigestChunkBytes - 1U) /
        kManifestDigestChunkBytes;
    if (chunk_count == 0U ||
        chunk_count > std::numeric_limits<std::uint32_t>::max() ||
        encoded.value().size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 chunked manifest identity is excessive"};
    }
    std::vector<Digest> leaves;
    leaves.reserve(chunk_count);
    for (std::size_t index = 0U; index < chunk_count; ++index) {
        const std::size_t offset = index * kManifestDigestChunkBytes;
        const std::size_t bytes = std::min(
            kManifestDigestChunkBytes, encoded.value().size() - offset);
        std::vector<std::uint8_t> leaf(16U + bytes, 0U);
        write_u32(leaf, 0U, static_cast<std::uint32_t>(index));
        write_u32(leaf, 4U, static_cast<std::uint32_t>(chunk_count));
        write_u64(leaf, 8U, encoded.value().size());
        std::copy_n(encoded.value().begin() +
                        static_cast<std::ptrdiff_t>(offset),
                    bytes, leaf.begin() + 16);
        auto digest = sodium.hash(kManifestChunkDigestDomain, leaf);
        if (!digest) return digest.status();
        leaves.push_back(digest.value());
    }
    constexpr std::array<std::uint8_t, 8U> root_magic = {
        'I', 'O', 'T', 'X', 'T', 'M', 'H', '1'};
    std::vector<std::uint8_t> root(16U + leaves.size() * Digest{}.size(), 0U);
    std::copy(root_magic.begin(), root_magic.end(), root.begin());
    write_u32(root, 8U, static_cast<std::uint32_t>(leaves.size()));
    write_u32(root, 12U, static_cast<std::uint32_t>(encoded.value().size()));
    std::size_t offset = 16U;
    for (const Digest &leaf : leaves) {
        std::copy(leaf.begin(), leaf.end(),
                  root.begin() + static_cast<std::ptrdiff_t>(offset));
        offset += leaf.size();
    }
    return sodium.hash(kManifestChunkRootDomain, root);
}

Status validate_tree_v2_branch_head(const NamespacePolicy &policy,
                                    const TreeV2BranchHead &head) {
    const Status valid_policy = validate_namespace_policy(policy);
    if (!valid_policy.ok()) return valid_policy;
    if (policy.engine != Engine::tree_v2) {
        return Status{ErrorCode::unsupported,
                      "tree-v2 branch requires a tree-v2 namespace"};
    }
    if (head.namespace_id != policy.id ||
        !valid_namespace_id(head.namespace_id) ||
        head.namespace_id.size() > kBranchNamespaceBytes ||
        head.generation == 0U || all_zero(head.writer) ||
        !writer_allowed(policy, head.writer) || all_zero(head.manifest) ||
        head.manifest_bytes < kManifestHeaderBytes ||
        head.manifest_bytes > policy.quotas.maximum_manifest_bytes ||
        head.observations.size() > policy.quotas.maximum_peers ||
        head.observations.size() > kMaximumNamespacePrincipals) {
        return Status{
            ErrorCode::invalid_argument,
            "tree-v2 branch identity, manifest, or frontier is invalid"};
    }
    const bool genesis = head.generation == 1U;
    if ((!head.checkpoint &&
         ((genesis && !all_zero(head.previous)) ||
          (!genesis && all_zero(head.previous)))) ||
        (head.checkpoint && !all_zero(head.previous))) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 branch generation and predecessor disagree"};
    }
    bool self_observation = false;
    for (std::size_t index = 0U; index < head.observations.size(); ++index) {
        const TreeV2Observation &observation = head.observations[index];
        if (all_zero(observation.writer) || observation.generation == 0U ||
            all_zero(observation.record) ||
            !writer_allowed(policy, observation.writer)) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 branch observation is invalid"};
        }
        if (index != 0U &&
            !observation_less(head.observations[index - 1U], observation)) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 branch observations are not canonical"};
        }
        if (observation.writer == head.writer) {
            const bool ordinary_predecessor =
                !head.checkpoint && !genesis &&
                observation.generation == head.generation - 1U &&
                observation.record == head.previous;
            const bool checkpoint_floor =
                head.checkpoint && !genesis &&
                observation.generation == head.generation - 1U;
            if (!ordinary_predecessor && !checkpoint_floor) {
                return Status{ErrorCode::invalid_argument,
                              "tree-v2 branch self observation is not its "
                              "exact predecessor or checkpoint floor"};
            }
            self_observation = true;
        }
    }
    if (genesis == self_observation) {
        return Status{
            ErrorCode::invalid_argument,
            "tree-v2 branch predecessor observation is missing or spurious"};
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_branch_body(const NamespacePolicy &policy,
                           const TreeV2BranchHead &head) {
    const Status valid = validate_tree_v2_branch_head(policy, head);
    if (!valid.ok()) return valid;
    std::array<std::uint8_t, kBranchBodyFixedBytes> fixed{};
    std::copy(kBranchMagic.begin(), kBranchMagic.end(), fixed.begin());
    fixed[8U] = head.checkpoint ? kTreeV2CheckpointBranchVersion
                                : kTreeV2BranchVersion;
    fixed[9U] = static_cast<std::uint8_t>(Engine::tree_v2);
    fixed[10U] = static_cast<std::uint8_t>(head.namespace_id.size());
    fixed[11U] = static_cast<std::uint8_t>(head.observations.size());
    write_u64(fixed, 16U, head.generation);
    write_u64(fixed, 24U, head.manifest_bytes);
    write_array(fixed, 32U, head.writer);
    write_array(fixed, 64U, head.previous);
    write_array(fixed, 96U, head.manifest);
    std::copy(head.namespace_id.begin(), head.namespace_id.end(),
              fixed.begin() + 128);
    std::vector<std::uint8_t> output(fixed.begin(), fixed.end());
    output.reserve(kBranchBodyFixedBytes +
                   head.observations.size() * kBranchObservationBytes);
    for (const TreeV2Observation &observation : head.observations) {
        std::array<std::uint8_t, kBranchObservationBytes> record{};
        write_array(record, 0U, observation.writer);
        write_u64(record, 32U, observation.generation);
        write_array(record, 40U, observation.record);
        output.insert(output.end(), record.begin(), record.end());
    }
    return output;
}

Result<std::vector<std::uint8_t>>
encode_tree_v2_branch_head(const NamespacePolicy &policy,
                           const TreeV2BranchHead &head) {
    auto body = encode_tree_v2_branch_body(policy, head);
    if (!body) return body.status();
    body.value().insert(body.value().end(), head.signature.begin(),
                        head.signature.end());
    return body.value();
}

Result<TreeV2BranchHead>
decode_tree_v2_branch_head(const NamespacePolicy &policy,
                           std::span<const std::uint8_t> bytes) {
    const std::size_t minimum =
        kBranchBodyFixedBytes + security::kSignatureBytes;
    if (bytes.size() < minimum ||
        !std::equal(kBranchMagic.begin(), kBranchMagic.end(), bytes.begin()) ||
        (bytes[8U] != kTreeV2BranchVersion &&
         bytes[8U] != kTreeV2CheckpointBranchVersion) ||
        bytes[9U] != static_cast<std::uint8_t>(Engine::tree_v2) ||
        bytes[10U] == 0U || bytes[10U] > kBranchNamespaceBytes ||
        !all_zero(bytes.subspan(12U, 4U))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch header or size is invalid"};
    }
    const std::size_t observations = bytes[11U];
    if (observations > kMaximumNamespacePrincipals ||
        bytes.size() != minimum + observations * kBranchObservationBytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch frontier length is invalid"};
    }
    const std::size_t namespace_bytes = bytes[10U];
    if (!all_zero(bytes.subspan(128U + namespace_bytes,
                                kBranchNamespaceBytes - namespace_bytes))) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch namespace padding is nonzero"};
    }
    TreeV2BranchHead head;
    head.checkpoint = bytes[8U] == kTreeV2CheckpointBranchVersion;
    head.namespace_id.assign(
        reinterpret_cast<const char *>(bytes.data() + 128U), namespace_bytes);
    head.generation = read_u64(bytes, 16U);
    head.manifest_bytes = read_u64(bytes, 24U);
    read_array(bytes, 32U, head.writer);
    read_array(bytes, 64U, head.previous);
    read_array(bytes, 96U, head.manifest);
    std::size_t offset = kBranchBodyFixedBytes;
    head.observations.reserve(observations);
    for (std::size_t index = 0U; index < observations; ++index) {
        TreeV2Observation observation;
        read_array(bytes, offset, observation.writer);
        observation.generation = read_u64(bytes, offset + 32U);
        read_array(bytes, offset + 40U, observation.record);
        head.observations.push_back(observation);
        offset += kBranchObservationBytes;
    }
    read_array(bytes, offset, head.signature);
    const Status valid = validate_tree_v2_branch_head(policy, head);
    if (!valid.ok()) return valid;
    auto canonical = encode_tree_v2_branch_head(policy, head);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch record is not canonical"};
    }
    return head;
}

Status verify_tree_v2_branch_head(const NamespacePolicy &policy,
                                  const TreeV2BranchHead &head,
                                  const security::Sodium &sodium) {
    const Status valid = validate_tree_v2_branch_head(policy, head);
    if (!valid.ok()) return valid;
    auto digest = branch_signing_digest(policy, head, sodium);
    if (!digest) return digest.status();
    return sodium.verify_detached(head.signature, digest.value(), head.writer);
}

Result<Digest> tree_v2_branch_record_digest(const NamespacePolicy &policy,
                                            const TreeV2BranchHead &head,
                                            const security::Sodium &sodium) {
    auto encoded = encode_tree_v2_branch_head(policy, head);
    if (!encoded) return encoded.status();
    return sodium.hash(head.checkpoint ? kCheckpointRecordDomain
                                       : kBranchRecordDomain,
                       encoded.value());
}

Result<TreeV2BranchHead> create_tree_v2_branch_head(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const std::optional<TreeV2BranchHead> &previous,
    std::span<const TreeV2Observation> observations,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
    if (!writer_allowed(policy, identity.public_key())) {
        return Status{ErrorCode::protocol_error,
                      "local device is not a tree-v2 namespace writer"};
    }
    auto encoded_manifest = encode_tree_v2_manifest(policy, manifest);
    if (!encoded_manifest) return encoded_manifest.status();
    auto manifest_digest = tree_v2_manifest_digest(policy, manifest, sodium);
    if (!manifest_digest) return manifest_digest.status();

    TreeV2BranchHead head;
    head.namespace_id = policy.id;
    head.writer = identity.public_key();
    head.manifest = manifest_digest.value();
    head.manifest_bytes = encoded_manifest.value().size();
    head.observations.assign(observations.begin(), observations.end());
    if (std::any_of(head.observations.begin(), head.observations.end(),
                    [&head](const TreeV2Observation &observation) {
                        return observation.writer == head.writer;
                    })) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 caller supplied a self observation"};
    }
    if (previous) {
        const Status verified =
            verify_tree_v2_branch_head(policy, *previous, sodium);
        if (!verified.ok()) return verified;
        if (previous->writer != identity.public_key() ||
            previous->generation == std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 predecessor belongs to another writer or is "
                          "exhausted"};
        }
        auto record = tree_v2_branch_record_digest(policy, *previous, sodium);
        if (!record) return record.status();
        head.generation = previous->generation + 1U;
        head.previous = record.value();
        head.observations.push_back(TreeV2Observation{
            head.writer, previous->generation, record.value()});
    } else {
        head.generation = 1U;
    }
    std::sort(head.observations.begin(), head.observations.end(),
              observation_less);
    for (std::size_t index = 1U; index < head.observations.size(); ++index) {
        if (head.observations[index - 1U].writer ==
            head.observations[index].writer) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 frontier contains duplicate writers"};
        }
    }
    auto signing = branch_signing_digest(policy, head, sodium);
    if (!signing) return signing.status();
    auto signature = identity.sign(signing.value());
    if (!signature) return signature.status();
    head.signature = signature.value();
    const Status verified = verify_tree_v2_branch_head(policy, head, sodium);
    if (!verified.ok()) return verified;
    return head;
}

Result<TreeV2Snapshot> create_tree_v2_checkpoint(
    const NamespacePolicy &policy,
    std::span<const TreeV2Snapshot> frontier,
    const security::DeviceIdentity &identity, const security::Sodium &sodium) {
    if (frontier.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 checkpoint requires a non-empty frontier"};
    }
    if (!writer_allowed(policy, identity.public_key())) {
        return Status{ErrorCode::protocol_error,
                      "local device is not a tree-v2 namespace writer"};
    }
    auto merged = merge_tree_v2_snapshots(policy, frontier, sodium);
    if (!merged) return merged.status();
    if (!merged.value().conflicts.empty()) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 checkpoint refuses unresolved conflicts"};
    }

    std::uint64_t generation = 1U;
    const auto prior = std::find_if(
        frontier.begin(), frontier.end(), [&identity](const auto &snapshot) {
            return snapshot.head.writer == identity.public_key();
        });
    if (prior != frontier.end()) {
        if (prior->head.generation == std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 checkpoint generation is exhausted"};
        }
        generation = prior->head.generation + 1U;
    }

    TreeV2Manifest normalized = std::move(merged).value().manifest;
    for (TreeV2Entry &entry : normalized.entries)
        entry.origin = TreeV2Version{identity.public_key(), generation};
    auto encoded_manifest = encode_tree_v2_manifest(policy, normalized);
    if (!encoded_manifest) return encoded_manifest.status();
    auto manifest_digest =
        tree_v2_manifest_digest(policy, normalized, sodium);
    if (!manifest_digest) return manifest_digest.status();

    TreeV2BranchHead head;
    head.namespace_id = policy.id;
    head.writer = identity.public_key();
    head.generation = generation;
    head.manifest = manifest_digest.value();
    head.manifest_bytes = encoded_manifest.value().size();
    head.checkpoint = true;
    head.observations.reserve(frontier.size());
    for (const TreeV2Snapshot &snapshot : frontier) {
        auto record = tree_v2_branch_record_digest(policy, snapshot.head,
                                                   sodium);
        if (!record) return record.status();
        head.observations.push_back(TreeV2Observation{
            snapshot.head.writer, snapshot.head.generation, record.value()});
    }
    std::sort(head.observations.begin(), head.observations.end(),
              observation_less);
    auto signing = branch_signing_digest(policy, head, sodium);
    if (!signing) return signing.status();
    auto signature = identity.sign(signing.value());
    if (!signature) return signature.status();
    head.signature = signature.value();
    TreeV2Snapshot result{head, std::move(normalized)};
    const Status verified = verify_tree_v2_snapshot(policy, result, sodium);
    if (!verified.ok()) return verified;
    return result;
}

Status verify_tree_v2_snapshot(const NamespacePolicy &policy,
                               const TreeV2Snapshot &snapshot,
                               const security::Sodium &sodium) {
    const Status verified =
        verify_tree_v2_branch_head(policy, snapshot.head, sodium);
    if (!verified.ok()) return verified;
    auto encoded = encode_tree_v2_manifest(policy, snapshot.manifest);
    if (!encoded) return encoded.status();
    if (encoded.value().size() != snapshot.head.manifest_bytes) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch manifest size does not match"};
    }
    auto digest =
        tree_v2_manifest_digest(policy, snapshot.manifest, sodium);
    if (!digest) return digest.status();
    if (digest.value() != snapshot.head.manifest) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 branch manifest digest does not match"};
    }
    for (const TreeV2Entry &entry : snapshot.manifest.entries) {
        if (!tree_v2_head_observes(snapshot.head, entry.origin)) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 branch manifest contains an unobserved future value"};
        }
    }
    return Status::success();
}

bool tree_v2_head_observes(const TreeV2BranchHead &head,
                           const TreeV2Version &version) noexcept {
    if (head.writer == version.writer)
        return head.generation >= version.generation;
    const auto found = std::lower_bound(
        head.observations.begin(), head.observations.end(), version.writer,
        [](const TreeV2Observation &observation, const PrincipalId &writer) {
            return observation.writer < writer;
        });
    return found != head.observations.end() &&
           found->writer == version.writer &&
           found->generation >= version.generation;
}

Result<TreeV2Entry>
select_tree_v2_projection_entry(std::span<const TreeV2Entry> candidates) {
    if (candidates.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 projection candidate set is empty"};
    }
    const auto selected =
        std::min_element(candidates.begin(), candidates.end(),
                         [](const TreeV2Entry &left, const TreeV2Entry &right) {
                             const int left_rank = projection_rank(left.kind);
                             const int right_rank = projection_rank(right.kind);
                             return left_rank != right_rank
                                        ? left_rank < right_rank
                                        : entry_less(left, right);
                         });
    return *selected;
}

Result<TreeV2MergeResult>
summarize_tree_v2_manifest(const NamespacePolicy &policy,
                           const TreeV2Manifest &manifest) {
    const Status valid = validate_tree_v2_manifest(policy, manifest);
    if (!valid.ok()) return valid;
    TreeV2MergeResult result;
    result.manifest = manifest;
    for (auto first = manifest.entries.begin();
         first != manifest.entries.end();) {
        const auto last = std::find_if(
            first, manifest.entries.end(), [&first](const TreeV2Entry &entry) {
                return entry.path != first->path;
            });
        const std::size_t candidate_count =
            static_cast<std::size_t>(last - first);
        const std::span<const TreeV2Entry> candidates{&*first,
                                                      candidate_count};
        if (candidate_count > 1U) {
            result.conflicts.push_back(TreeV2Conflict{
                first->path, std::vector<TreeV2Entry>(first, last)});
        }
        auto selected = select_tree_v2_projection_entry(candidates);
        if (!selected) return selected.status();
        ++result.paths;
        switch (selected.value().kind) {
        case TreeV2EntryKind::directory:
            ++result.live_directories;
            break;
        case TreeV2EntryKind::file:
            ++result.live_files;
            break;
        case TreeV2EntryKind::tombstone:
            ++result.tombstoned_paths;
            break;
        }
        first = last;
    }
    return result;
}

Result<TreeV2MergeResult>
merge_tree_v2_snapshots(const NamespacePolicy &policy,
                        std::span<const TreeV2Snapshot> snapshots,
                        const security::Sodium &sodium) {
    if (snapshots.empty() || snapshots.size() > policy.quotas.maximum_peers ||
        snapshots.size() > kMaximumNamespacePrincipals) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 merge frontier is empty or excessive"};
    }
    std::set<PrincipalId> writers;
    std::set<std::string> paths;
    std::vector<TreeV2PathIndex> snapshot_entries;
    snapshot_entries.reserve(snapshots.size());
    for (const TreeV2Snapshot &snapshot : snapshots) {
        const Status verified =
            verify_tree_v2_snapshot(policy, snapshot, sodium);
        if (!verified.ok()) return verified;
        if (!writers.insert(snapshot.head.writer).second) {
            return Status{ErrorCode::invalid_argument,
                          "tree-v2 merge frontier repeats a writer"};
        }
        snapshot_entries.push_back(
            index_tree_v2_manifest_paths(snapshot.manifest, &paths));
    }

    TreeV2MergeResult result;
    for (const std::string &path : paths) {
        std::vector<TreeV2Entry> candidates;
        for (const TreeV2PathIndex &index : snapshot_entries) {
            const auto values = index.find(path);
            if (values == index.end()) continue;
            candidates.insert(candidates.end(), values->second.begin(),
                              values->second.end());
        }
        std::sort(candidates.begin(), candidates.end(), entry_less);
        candidates.erase(std::unique(candidates.begin(), candidates.end()),
                         candidates.end());

        std::vector<TreeV2Entry> survivors;
        for (const TreeV2Entry &candidate : candidates) {
            bool dominated = false;
            for (std::size_t index = 0U; index < snapshots.size(); ++index) {
                const TreeV2Snapshot &snapshot = snapshots[index];
                if (!tree_v2_head_observes(snapshot.head, candidate.origin))
                    continue;
                const auto values = snapshot_entries[index].find(path);
                if (values == snapshot_entries[index].end() ||
                    std::find(values->second.begin(), values->second.end(),
                              candidate) != values->second.end()) {
                    continue;
                }
                dominated = true;
                break;
            }
            if (!dominated) survivors.push_back(candidate);
        }
        if (survivors.empty()) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 merge removed every value for a path"};
        }
        std::sort(survivors.begin(), survivors.end(), entry_less);

        // Concurrent identical outcomes do not need a conflict copy. Keep the
        // canonical lowest origin as the provenance representative.
        std::vector<TreeV2Entry> distinct;
        for (const TreeV2Entry &candidate : survivors) {
            const auto equivalent =
                std::find_if(distinct.begin(), distinct.end(),
                             [&candidate](const TreeV2Entry &value) {
                                 return same_payload(value, candidate);
                             });
            if (equivalent == distinct.end()) distinct.push_back(candidate);
        }
        std::sort(distinct.begin(), distinct.end(), entry_less);
        result.manifest.entries.insert(result.manifest.entries.end(),
                                       distinct.begin(), distinct.end());
        if (distinct.size() > 1U)
            result.conflicts.push_back(TreeV2Conflict{path, distinct});
        auto selected = select_tree_v2_projection_entry(distinct);
        if (!selected) return selected.status();
        ++result.paths;
        switch (selected.value().kind) {
        case TreeV2EntryKind::directory:
            ++result.live_directories;
            break;
        case TreeV2EntryKind::file:
            ++result.live_files;
            break;
        case TreeV2EntryKind::tombstone:
            ++result.tombstoned_paths;
            break;
        }
    }
    std::sort(result.manifest.entries.begin(), result.manifest.entries.end(),
              entry_less);
    const Status valid = validate_tree_v2_manifest(policy, result.manifest);
    if (!valid.ok()) return valid;
    return result;
}

} // namespace iotox::sync
