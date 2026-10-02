#include "toxsync/publication.hpp"

#include "toxsync/hash.hpp"
#include "toxsync/wire.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <cstring>
#include <fstream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <system_error>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace toxsync {
namespace {
std::atomic<std::uint64_t> g_publication_sequence{1U};

void fsync_directory(const std::filesystem::path& directory);


constexpr std::array<std::byte, 8U> kActivationMarkerMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'A'}, std::byte{'C'},
    std::byte{'T'}, std::byte{'V'}, std::byte{'0'}, std::byte{'1'},
};
constexpr std::uint16_t kActivationMarkerVersion = 1U;
constexpr std::size_t kActivationMarkerBodyBytes = 84U;
constexpr std::size_t kActivationMarkerBytes = 116U;

void marker_write_u16(std::span<std::byte> output, std::size_t offset,
                      std::uint16_t value) noexcept {
    output[offset] = static_cast<std::byte>(value & 0xffU);
    output[offset + 1U] = static_cast<std::byte>((value >> 8U) & 0xffU);
}

void marker_write_u64(std::span<std::byte> output, std::size_t offset,
                      std::uint64_t value) noexcept {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[offset + index] = static_cast<std::byte>(
            (value >> (index * 8U)) & 0xffU);
    }
}

[[nodiscard]] std::uint16_t marker_read_u16(
    std::span<const std::byte> input, std::size_t offset) noexcept {
    return static_cast<std::uint16_t>(
        std::to_integer<std::uint8_t>(input[offset]) |
        (static_cast<std::uint16_t>(
             std::to_integer<std::uint8_t>(input[offset + 1U])) << 8U));
}

[[nodiscard]] std::uint64_t marker_read_u64(
    std::span<const std::byte> input, std::size_t offset) noexcept {
    std::uint64_t value{};
    for (std::size_t index = 0U; index < 8U; ++index) {
        value |= static_cast<std::uint64_t>(
            std::to_integer<std::uint8_t>(input[offset + index]))
            << (index * 8U);
    }
    return value;
}

[[nodiscard]] std::array<std::byte, kActivationMarkerBytes>
encode_activation_marker(const Digest256& namespace_id,
                         std::uint64_t generation,
                         const Digest256& head_record) {
    std::array<std::byte, kActivationMarkerBytes> bytes{};
    std::copy(kActivationMarkerMagic.begin(), kActivationMarkerMagic.end(),
              bytes.begin());
    marker_write_u16(bytes, 8U, kActivationMarkerVersion);
    marker_write_u16(bytes, 10U, 0U);
    marker_write_u64(bytes, 12U, generation);
    std::copy(namespace_id.bytes.begin(), namespace_id.bytes.end(),
              bytes.begin() + 20);
    std::copy(head_record.bytes.begin(), head_record.bytes.end(),
              bytes.begin() + 52);
    const auto checksum = sha256(std::span<const std::byte>(
        bytes.data(), kActivationMarkerBodyBytes));
    std::copy(checksum.bytes.begin(), checksum.bytes.end(),
              bytes.begin() + kActivationMarkerBodyBytes);
    return bytes;
}

void write_private_blob_atomic(const std::filesystem::path& destination,
                               std::span<const std::byte> bytes,
                               bool sync) {
    auto parent = destination.parent_path();
    if (parent.empty()) parent = std::filesystem::current_path();
    std::filesystem::create_directories(parent);
    const auto sequence = g_publication_sequence.fetch_add(1U);
    auto temporary = destination;
    temporary += ".part." + std::to_string(sequence);
#if defined(__unix__) || defined(__APPLE__)
    const int descriptor = ::open(
        temporary.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        throw std::runtime_error("cannot create temporary activation receipt: " +
                                 std::string(std::strerror(errno)));
    }
    std::size_t written{};
    while (written < bytes.size()) {
        const auto result = ::write(
            descriptor, bytes.data() + written, bytes.size() - written);
        if (result < 0) {
            if (errno == EINTR) continue;
            const int saved = errno;
            (void)::close(descriptor);
            (void)::unlink(temporary.c_str());
            throw std::runtime_error("cannot write activation receipt: " +
                                     std::string(std::strerror(saved)));
        }
        if (result == 0) {
            (void)::close(descriptor);
            (void)::unlink(temporary.c_str());
            throw std::runtime_error(
                "zero-length write while publishing activation receipt");
        }
        written += static_cast<std::size_t>(result);
    }
    if (sync && ::fsync(descriptor) != 0) {
        const int saved = errno;
        (void)::close(descriptor);
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot fsync activation receipt: " +
                                 std::string(std::strerror(saved)));
    }
    if (::close(descriptor) != 0) {
        const int saved = errno;
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot close activation receipt: " +
                                 std::string(std::strerror(saved)));
    }
    if (::rename(temporary.c_str(), destination.c_str()) != 0) {
        const int saved = errno;
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot publish activation receipt: " +
                                 std::string(std::strerror(saved)));
    }
#else
    std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create activation receipt");
    output.write(reinterpret_cast<const char*>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("cannot write activation receipt");
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(temporary, destination, error);
    if (error) {
        std::filesystem::remove(temporary, error);
        throw std::runtime_error("cannot publish activation receipt");
    }
#endif
    if (sync) fsync_directory(parent);
}

[[nodiscard]] bool activation_marker_matches(
    const std::filesystem::path& path,
    const Digest256& namespace_id,
    std::uint64_t generation,
    const Digest256& head_record) {
    std::error_code error;
    const auto status = std::filesystem::symlink_status(path, error);
    if (error || !std::filesystem::is_regular_file(status) ||
        std::filesystem::is_symlink(status) ||
        std::filesystem::file_size(path, error) != kActivationMarkerBytes ||
        error) {
        return false;
    }
    std::array<std::byte, kActivationMarkerBytes> bytes{};
    std::ifstream input(path, std::ios::binary);
    if (!input) return false;
    input.read(reinterpret_cast<char*>(bytes.data()),
               static_cast<std::streamsize>(bytes.size()));
    if (!input ||
        !std::equal(kActivationMarkerMagic.begin(),
                    kActivationMarkerMagic.end(), bytes.begin()) ||
        marker_read_u16(bytes, 8U) != kActivationMarkerVersion ||
        marker_read_u16(bytes, 10U) != 0U ||
        marker_read_u64(bytes, 12U) != generation ||
        !std::equal(namespace_id.bytes.begin(), namespace_id.bytes.end(),
                    bytes.begin() + 20) ||
        !std::equal(head_record.bytes.begin(), head_record.bytes.end(),
                    bytes.begin() + 52)) {
        return false;
    }
    const auto checksum = sha256(std::span<const std::byte>(
        bytes.data(), kActivationMarkerBodyBytes));
    return std::equal(
        checksum.bytes.begin(), checksum.bytes.end(),
        bytes.begin() + kActivationMarkerBodyBytes);
}

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

void fsync_directory(const std::filesystem::path& directory) {
#if defined(__unix__) || defined(__APPLE__)
    const int descriptor = ::open(directory.c_str(), O_RDONLY | O_CLOEXEC);
    if (descriptor < 0) {
        throw std::runtime_error("cannot open directory for fsync: " +
                                 std::string(std::strerror(errno)));
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    (void)::close(descriptor);
    if (result != 0) {
        throw std::runtime_error("cannot fsync directory: " +
                                 std::string(std::strerror(saved)));
    }
#else
    (void)directory;
#endif
}

void write_head_atomic(const std::filesystem::path& destination,
                       const MutableHead& head,
                       bool sync) {
    const auto bytes = encode_mutable_head(head);
    auto parent = destination.parent_path();
    if (parent.empty()) parent = std::filesystem::current_path();
    std::filesystem::create_directories(parent);
    const auto sequence = g_publication_sequence.fetch_add(1U);
    auto temporary = destination;
    temporary += ".part." + std::to_string(sequence);
#if defined(__unix__) || defined(__APPLE__)
    const int descriptor = ::open(
        temporary.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        throw std::runtime_error("cannot create temporary signed HEAD: " +
                                 std::string(std::strerror(errno)));
    }
    std::size_t written{};
    while (written < bytes.size()) {
        const auto result = ::write(
            descriptor, bytes.data() + written, bytes.size() - written);
        if (result < 0) {
            if (errno == EINTR) continue;
            const int saved = errno;
            (void)::close(descriptor);
            (void)::unlink(temporary.c_str());
            throw std::runtime_error("cannot write temporary signed HEAD: " +
                                     std::string(std::strerror(saved)));
        }
        if (result == 0) {
            (void)::close(descriptor);
            (void)::unlink(temporary.c_str());
            throw std::runtime_error(
                "zero-length write while publishing signed HEAD");
        }
        written += static_cast<std::size_t>(result);
    }
    if (sync && ::fsync(descriptor) != 0) {
        const int saved = errno;
        (void)::close(descriptor);
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot fsync temporary signed HEAD: " +
                                 std::string(std::strerror(saved)));
    }
    if (::close(descriptor) != 0) {
        const int saved = errno;
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot close temporary signed HEAD: " +
                                 std::string(std::strerror(saved)));
    }
    if (::rename(temporary.c_str(), destination.c_str()) != 0) {
        const int saved = errno;
        (void)::unlink(temporary.c_str());
        throw std::runtime_error("cannot publish signed HEAD: " +
                                 std::string(std::strerror(saved)));
    }
#else
    std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create temporary signed HEAD");
    output.write(reinterpret_cast<const char*>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("cannot write temporary signed HEAD");
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(temporary, destination, error);
    if (error) {
        std::filesystem::remove(temporary, error);
        throw std::runtime_error("cannot publish signed HEAD");
    }
#endif
    if (sync) fsync_directory(parent);
}

class PrivateWorkDirectory final {
  public:
    explicit PrivateWorkDirectory(const std::filesystem::path& root) {
        if (root.empty()) {
            throw std::invalid_argument("publication work root is empty");
        }
        std::filesystem::create_directories(root);
        for (std::size_t attempt = 0U; attempt < 1024U; ++attempt) {
            const auto sequence = g_publication_sequence.fetch_add(1U);
            const auto candidate =
                root / ("publish-" + std::to_string(sequence) + ".part");
            std::error_code create_error;
            if (std::filesystem::create_directory(candidate, create_error)) {
                path_ = candidate;
                break;
            }
            if (create_error) {
                throw std::runtime_error(
                    "cannot create private publication workspace: " +
                    create_error.message());
            }
        }
        if (path_.empty()) {
            throw std::runtime_error(
                "cannot allocate a unique private publication workspace");
        }
        std::error_code error;
        std::filesystem::permissions(
            path_, std::filesystem::perms::owner_all,
            std::filesystem::perm_options::replace, error);
        if (error) {
            std::filesystem::remove_all(path_, error);
            throw std::runtime_error("cannot make publication workspace private");
        }
    }

    ~PrivateWorkDirectory() {
        if (!path_.empty()) {
            std::error_code ignored;
            std::filesystem::remove_all(path_, ignored);
        }
    }

    const std::filesystem::path& path() const noexcept { return path_; }
    void disarm() noexcept { path_.clear(); }

  private:
    std::filesystem::path path_;
};

void validate_publication(const DirectoryPublicationRequest& request) {
    if (!std::filesystem::is_directory(request.source_root)) {
        throw std::invalid_argument("publication source root is not a directory");
    }
    if (request.store_root.empty() || request.head_output.empty() ||
        all_zero(request.namespace_id.bytes) || request.generation == 0U) {
        throw std::invalid_argument("publication request is incomplete");
    }
    if (request.previous) {
        Ed25519PublicKey public_key;
        if (!ed25519_public_key(request.private_key, public_key) ||
            !verify_mutable_head(*request.previous, public_key)) {
            throw std::invalid_argument(
                "publication previous HEAD is not signed by this publisher");
        }
        if (request.previous->namespace_id != request.namespace_id) {
            throw std::invalid_argument("publication previous HEAD namespace differs");
        }
        if (request.generation <= request.previous->generation) {
            throw std::invalid_argument("publication generation does not advance");
        }
        if (!request.snapshot &&
            request.generation != request.previous->generation + 1U) {
            throw std::invalid_argument(
                "linked publication generation must advance by exactly one");
        }
    } else if (request.generation != 1U && !request.snapshot) {
        throw std::invalid_argument(
            "non-snapshot publication without a parent must be generation one");
    }
}

[[nodiscard]] std::string revision_name(std::uint64_t generation,
                                        const Digest256& record) {
    return std::to_string(generation) + "-" + record.hex();
}

void use_retained_revision(
    const std::filesystem::path& revision_root,
    const MutableHead& head,
    const DirectoryPublicationOptions& options,
    DirectoryPublicationStats& stats) {
    std::error_code error;
    const auto status = std::filesystem::symlink_status(revision_root, error);
    if (error || !std::filesystem::is_directory(status) ||
        std::filesystem::is_symlink(status)) {
        throw std::runtime_error(
            "publication revision workspace is not a real directory");
    }

    const auto treepack = revision_root / "revision.txtree";
    const auto root_manifest = revision_root / "revision.txroot";
    std::uint64_t expected_entries{};
    if (options.retain_treepack) {
        ++expected_entries;
        const auto tree_status = std::filesystem::symlink_status(treepack, error);
        if (error || !std::filesystem::is_regular_file(tree_status) ||
            std::filesystem::is_symlink(tree_status) ||
            std::filesystem::file_size(treepack, error) != head.artifact_size ||
            error || sha256_file(treepack.string()) != head.artifact) {
            throw std::runtime_error(
                "retained publication treepack does not match the signed HEAD");
        }
        stats.retained_treepack = treepack;
    }
    if (options.retain_root_manifest) {
        ++expected_entries;
        const auto root_status =
            std::filesystem::symlink_status(root_manifest, error);
        if (error || !std::filesystem::is_regular_file(root_status) ||
            std::filesystem::is_symlink(root_status) ||
            std::filesystem::file_size(root_manifest, error) != head.index_size ||
            error || sha256_file(root_manifest.string()) != head.index) {
            throw std::runtime_error(
                "retained publication root does not match the signed HEAD");
        }
        stats.retained_root_manifest = root_manifest;
    }

    std::uint64_t observed_entries{};
    for (std::filesystem::directory_iterator iterator(revision_root), end;
         iterator != end; ++iterator) {
        const auto name = iterator->path().filename();
        if ((options.retain_treepack && name == treepack.filename()) ||
            (options.retain_root_manifest &&
             name == root_manifest.filename())) {
            ++observed_entries;
            continue;
        }
        throw std::runtime_error(
            "retained publication workspace contains an unexpected entry");
    }
    if (observed_entries != expected_entries) {
        throw std::runtime_error(
            "retained publication workspace is incomplete");
    }
}

} // namespace

DirectoryPublicationStats publish_directory_revision(
    const DirectoryPublicationRequest& request,
    const DirectoryPublicationOptions& options) {
    ContentStoreWorkspace workspace;
    return publish_directory_revision(request, workspace, options);
}

DirectoryPublicationStats publish_directory_revision(
    const DirectoryPublicationRequest& request,
    ContentStoreWorkspace& workspace,
    const DirectoryPublicationOptions& options) {
    validate_publication(request);
    if (!ed25519_backend_available()) {
        throw std::runtime_error(
            "directory publication requires an Ed25519 backend");
    }

    PrivateWorkDirectory work(request.work_root);
    const auto artifact = work.path() / "revision.txtree";
    const auto root_manifest = work.path() / "revision.txroot";

    DirectoryPublicationStats stats;
    stats.treepack = pack_tree(
        request.source_root, artifact, options.treepack_limits);
    auto content_options = options.content_options;
    content_options.publish_root_to_store = true;
    stats.content = build_paged_content_store(
        artifact, request.store_root, root_manifest, workspace, content_options);
    stats.workspace_reserved_bytes = workspace.resident_bytes();

    if (stats.treepack.artifact_bytes != stats.content.metadata.artifact_size) {
        throw std::runtime_error(
            "treepack size changed while building the content revision");
    }

    MutableHead head;
    head.engine = Engine::content_store_v2;
    head.flags = kHeadFlagTreepack |
                 (request.snapshot ? kHeadFlagSnapshot : 0U);
    head.generation = request.generation;
    head.namespace_id = request.namespace_id;
    head.artifact = stats.content.metadata.artifact_digest;
    head.index = stats.content.metadata.root_digest;
    head.parent = request.previous
        ? mutable_head_record_digest(*request.previous)
        : Digest256{};
    head.artifact_size = stats.content.metadata.artifact_size;
    head.index_size = stats.content.metadata.encoded_size();
    head.block_size = 0U;
    if (!sign_mutable_head(head, request.private_key)) {
        throw std::runtime_error("cannot sign directory publication HEAD");
    }
    stats.head = head;

    const auto record = mutable_head_record_digest(head);
    if (options.retain_treepack || options.retain_root_manifest) {
        const auto revisions = request.work_root / "revisions";
        const auto revision_root =
            revisions / revision_name(head.generation, record);
        if (std::filesystem::exists(revision_root)) {
            // A crash may land the complete retained directory immediately
            // before the HEAD-last mutation. Exact retry is safe only after
            // revalidating its complete requested shape and both identities.
            use_retained_revision(revision_root, head, options, stats);
        } else {
            std::filesystem::create_directories(revisions);
            PrivateWorkDirectory retained(revisions);
            if (options.retain_treepack) {
                std::filesystem::rename(
                    artifact, retained.path() / "revision.txtree");
            }
            if (options.retain_root_manifest) {
                std::filesystem::rename(
                    root_manifest, retained.path() / "revision.txroot");
            }
            if (options.fsync_head_on_commit) {
                fsync_directory(retained.path());
            }
            std::filesystem::rename(retained.path(), revision_root);
            retained.disarm();
            if (options.fsync_head_on_commit) fsync_directory(revisions);
            use_retained_revision(revision_root, head, options, stats);
        }
    }

    // The HEAD is the sole mutable publication point and is committed last.
    write_head_atomic(
        request.head_output, head, options.fsync_head_on_commit);
    return stats;
}

TreeActivationStats activate_treepack_revision(
    const std::filesystem::path& treepack_artifact,
    const std::filesystem::path& activation_root,
    const Digest256& namespace_id,
    std::uint64_t generation,
    const Digest256& head_record,
    const TreeActivationOptions& options) {
    if (activation_root.empty() || generation == 0U ||
        all_zero(namespace_id.bytes) || all_zero(head_record.bytes)) {
        throw std::invalid_argument("tree activation request is incomplete");
    }
    std::filesystem::create_directories(activation_root);
    std::error_code error;
    const auto root_status = std::filesystem::symlink_status(
        activation_root, error);
    if (error || !std::filesystem::is_directory(root_status) ||
        std::filesystem::is_symlink(root_status)) {
        throw std::runtime_error(
            "tree activation root must be a real directory");
    }
    const auto revisions = activation_root / "revisions";
    const auto receipts = activation_root / ".toxsync" / "activations";
    std::filesystem::create_directories(revisions);
    std::filesystem::create_directories(receipts);
    const auto name = namespace_id.hex().substr(0U, 16U) + "-" +
                      revision_name(generation, head_record);
    const auto final = revisions / name;
    const auto receipt = receipts / (name + ".commit");
    const auto relative_target = std::filesystem::path("revisions") / name;

    TreeActivationStats stats;
    stats.revision_path = final;
    stats.current_link = activation_root / "current";

    const auto read_current_target = [&]() -> std::filesystem::path {
        std::error_code current_error;
        const auto current_status = std::filesystem::symlink_status(
            stats.current_link, current_error);
        if (!current_error && std::filesystem::exists(current_status)) {
            if (!std::filesystem::is_symlink(current_status)) {
                throw std::runtime_error(
                    "tree activation current pointer is not a symlink");
            }
            return std::filesystem::read_symlink(stats.current_link);
        }
        if (current_error &&
            current_error != std::errc::no_such_file_or_directory) {
            throw std::runtime_error(
                "cannot inspect tree activation current pointer: " +
                current_error.message());
        }
        return {};
    };

    const auto switch_current = [&](std::uint64_t sequence) {
#if defined(__unix__) || defined(__APPLE__)
        const auto temporary_link = activation_root /
            (".current.part." + std::to_string(sequence));
        std::filesystem::create_symlink(relative_target, temporary_link);
        if (::rename(temporary_link.c_str(), stats.current_link.c_str()) != 0) {
            const int saved = errno;
            (void)::unlink(temporary_link.c_str());
            throw std::runtime_error("cannot publish tree activation pointer: " +
                                     std::string(std::strerror(saved)));
        }
#else
        (void)sequence;
        throw std::runtime_error(
            "atomic directory activation currently requires POSIX symlinks");
#endif
    };

    const auto final_status = std::filesystem::symlink_status(final, error);
    if (!error && std::filesystem::exists(final_status)) {
        if (!options.resume_committed_revision ||
            !std::filesystem::is_directory(final_status) ||
            std::filesystem::is_symlink(final_status) ||
            !activation_marker_matches(
                receipt, namespace_id, generation, head_record)) {
            throw std::runtime_error("tree activation revision already exists");
        }
        stats.resumed_existing_revision = true;
        stats.previous_target = read_current_target();
        if (stats.previous_target == relative_target) {
            stats.already_active = true;
            return stats;
        }
        const auto sequence = g_publication_sequence.fetch_add(1U);
        switch_current(sequence);
        if (options.fsync_on_commit) {
            fsync_directory(revisions);
            fsync_directory(activation_root);
        }
        return stats;
    }
    if (error && error != std::errc::no_such_file_or_directory) {
        throw std::runtime_error(
            "cannot inspect tree activation revision: " + error.message());
    }
    error.clear();

    const auto sequence = g_publication_sequence.fetch_add(1U);
    const auto staging = revisions /
        ("." + name + ".part." + std::to_string(sequence));
    try {
        stats.treepack = unpack_tree(
            treepack_artifact, staging, options.treepack_limits);
        const auto marker = encode_activation_marker(
            namespace_id, generation, head_record);
        write_private_blob_atomic(receipt, marker, options.fsync_on_commit);
        std::filesystem::rename(staging, final);
    } catch (...) {
        std::error_code ignored;
        std::filesystem::remove_all(staging, ignored);
        throw;
    }

    stats.previous_target = read_current_target();
    switch_current(sequence);
    if (options.fsync_on_commit) {
        fsync_directory(revisions);
        fsync_directory(activation_root);
    }
    return stats;
}

} // namespace toxsync
