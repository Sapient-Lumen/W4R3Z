#include "test_harness.hpp"
#include "test_support.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/head.hpp"
#include "toxsync/publication.hpp"
#include "toxsync/wire.hpp"

#include <fstream>
#include <iterator>
#include <vector>

namespace {

toxsync::MutableHead read_wire_head(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    std::vector<char> chars{std::istreambuf_iterator<char>(input),
                            std::istreambuf_iterator<char>()};
    std::vector<std::byte> bytes(chars.size());
    std::transform(chars.begin(), chars.end(), bytes.begin(), [](char value) {
        return static_cast<std::byte>(static_cast<unsigned char>(value));
    });
    return toxsync::decode_mutable_head(bytes);
}

} // namespace

TOXSYNC_TEST(directory_publication_closes_pack_store_sign_reconstruct_and_activate) {
    if (!toxsync::ed25519_backend_available()) return;
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source / "nested");
    test::write_file(source / "alpha", test::pattern(8192U, 0x5511U));
    test::write_file(source / "nested" / "beta",
                     test::pattern(33333U, 0x5512U));

    toxsync::Ed25519PrivateKey private_key;
    toxsync::Ed25519PublicKey public_key;
    REQUIRE(toxsync::ed25519_generate_key(private_key, public_key));
    const auto namespace_id = toxsync::sha256(test::pattern(41U, 0x5513U));

    toxsync::DirectoryPublicationRequest request;
    request.source_root = source;
    request.work_root = temp.path() / "publisher";
    request.store_root = temp.path() / "store";
    request.head_output = temp.path() / "current.head";
    request.namespace_id = namespace_id;
    request.generation = 1U;
    request.private_key = private_key;

    toxsync::DirectoryPublicationOptions options;
    options.fsync_head_on_commit = false;
    options.retain_treepack = true;
    options.retain_root_manifest = true;
    // The three canonical source paths occupy just under 128 bytes with the
    // project-owned accounting model. Force a spill independent of the host
    // standard library's std::string representation.
    options.treepack_limits.sort_memory_bytes = 64U;
    options.treepack_limits.max_open_sort_runs = 2U;
    options.content_options.fsync_on_commit = false;
    options.content_options.auto_chunking = false;
    options.content_options.chunking = {
        .min_bytes = 1024U,
        .average_bytes = 4096U,
        .max_bytes = 16384U,
    };
    options.content_options.entries_per_page = 4U;

    toxsync::ContentStoreWorkspace workspace;
    const auto published = toxsync::publish_directory_revision(
        request, workspace, options);
    REQUIRE(published.head.generation == 1U);
    REQUIRE(published.head.engine == toxsync::Engine::content_store_v2);
    REQUIRE((published.head.flags & toxsync::kHeadFlagTreepack) != 0U);
    REQUIRE(toxsync::verify_mutable_head(published.head, public_key));
    REQUIRE(read_wire_head(request.head_output) == published.head);
    REQUIRE(!published.retained_treepack.empty());
    REQUIRE(!published.retained_root_manifest.empty());
    REQUIRE(std::filesystem::exists(published.retained_treepack));
    REQUIRE(std::filesystem::exists(published.retained_root_manifest));
    REQUIRE(published.treepack.sort_runs > 0U);

    // Repeating the exact transaction models a crash after the retained
    // revision directory landed but before the HEAD-last commit returned.
    const auto resumed_publication = toxsync::publish_directory_revision(
        request, workspace, options);
    REQUIRE(resumed_publication.head == published.head);
    REQUIRE(resumed_publication.retained_treepack ==
            published.retained_treepack);
    REQUIRE(resumed_publication.retained_root_manifest ==
            published.retained_root_manifest);

    const auto stored_root = toxsync::content_store_path(
        request.store_root, published.head.index);
    REQUIRE(std::filesystem::exists(stored_root));
    const auto reconstructed = temp.path() / "reconstructed.txtree";
    toxsync::ContentReconstructOptions reconstruct_options;
    reconstruct_options.fsync_on_commit = false;
    const auto reconstructed_stats = toxsync::reconstruct_paged_content_manifest(
        stored_root, request.store_root, reconstructed, workspace,
        reconstruct_options);
    REQUIRE(reconstructed_stats.metadata.artifact_digest ==
            published.head.artifact);
    REQUIRE(test::read_file(reconstructed) ==
            test::read_file(published.retained_treepack));

    toxsync::TreeActivationOptions activation_options;
    activation_options.fsync_on_commit = false;
    const auto activated = toxsync::activate_treepack_revision(
        reconstructed, temp.path() / "active", namespace_id,
        published.head.generation,
        toxsync::mutable_head_record_digest(published.head),
        activation_options);
    REQUIRE(std::filesystem::is_symlink(activated.current_link));
    REQUIRE(test::read_file(activated.current_link / "alpha") ==
            test::read_file(source / "alpha"));
    REQUIRE(test::read_file(activated.current_link / "nested" / "beta") ==
            test::read_file(source / "nested" / "beta"));

    test::write_file(source / "nested" / "gamma",
                     test::pattern(7000U, 0x5514U));
    request.previous = published.head;
    request.generation = 2U;
    request.head_output = temp.path() / "next.head";
    const auto advanced = toxsync::publish_directory_revision(
        request, workspace, options);
    REQUIRE(advanced.head.parent ==
            toxsync::mutable_head_record_digest(published.head));
    REQUIRE(toxsync::verify_mutable_head(advanced.head, public_key));
    REQUIRE(advanced.content.chunks_reused > 0U);
}

TOXSYNC_TEST(directory_publication_rejects_unlinked_generation_and_resumes_committed_activation) {
    if (!toxsync::ed25519_backend_available()) return;
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "file", test::pattern(100U, 0x5521U));

    toxsync::Ed25519PrivateKey private_key;
    toxsync::Ed25519PublicKey public_key;
    REQUIRE(toxsync::ed25519_generate_key(private_key, public_key));
    (void)public_key;
    toxsync::DirectoryPublicationRequest request;
    request.source_root = source;
    request.work_root = temp.path() / "work";
    request.store_root = temp.path() / "store";
    request.head_output = temp.path() / "head";
    request.namespace_id = toxsync::sha256(test::pattern(20U, 0x5522U));
    request.generation = 2U;
    request.private_key = private_key;
    toxsync::DirectoryPublicationOptions options;
    options.fsync_head_on_commit = false;
    options.content_options.fsync_on_commit = false;
    REQUIRE_THROWS(toxsync::publish_directory_revision(request, options));

    request.generation = 1U;
    options.retain_treepack = true;
    const auto published = toxsync::publish_directory_revision(request, options);
    toxsync::TreeActivationOptions activation_options;
    activation_options.fsync_on_commit = false;
    const auto record = toxsync::mutable_head_record_digest(published.head);
    const auto activation_root = temp.path() / "active";
    const auto first = toxsync::activate_treepack_revision(
        published.retained_treepack, activation_root,
        request.namespace_id, 1U, record, activation_options);
    const auto duplicate = toxsync::activate_treepack_revision(
        published.retained_treepack, activation_root,
        request.namespace_id, 1U, record, activation_options);
    REQUIRE(duplicate.resumed_existing_revision);
    REQUIRE(duplicate.already_active);
    REQUIRE(duplicate.revision_path == first.revision_path);

    const auto other = activation_root / "revisions" / "other";
    std::filesystem::create_directories(other);
    std::filesystem::remove(activation_root / "current");
    std::filesystem::create_symlink(
        std::filesystem::path("revisions") / "other",
        activation_root / "current");
    const auto resumed = toxsync::activate_treepack_revision(
        published.retained_treepack, activation_root,
        request.namespace_id, 1U, record, activation_options);
    REQUIRE(resumed.resumed_existing_revision);
    REQUIRE(!resumed.already_active);
    REQUIRE(std::filesystem::read_symlink(activation_root / "current") ==
            std::filesystem::path("revisions") /
                first.revision_path.filename());

    activation_options.resume_committed_revision = false;
    REQUIRE_THROWS(toxsync::activate_treepack_revision(
        published.retained_treepack, activation_root,
        request.namespace_id, 1U, record, activation_options));
}

TOXSYNC_TEST(directory_publication_rejects_a_corrupt_retained_retry) {
    if (!toxsync::ed25519_backend_available()) return;
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "file", test::pattern(4096U, 0x5525U));

    toxsync::Ed25519PrivateKey private_key;
    toxsync::Ed25519PublicKey public_key;
    REQUIRE(toxsync::ed25519_generate_key(private_key, public_key));
    (void)public_key;
    toxsync::DirectoryPublicationRequest request;
    request.source_root = source;
    request.work_root = temp.path() / "work";
    request.store_root = temp.path() / "store";
    request.head_output = temp.path() / "head";
    request.namespace_id = toxsync::sha256(test::pattern(20U, 0x5526U));
    request.generation = 1U;
    request.private_key = private_key;
    toxsync::DirectoryPublicationOptions options;
    options.fsync_head_on_commit = false;
    options.content_options.fsync_on_commit = false;
    options.retain_treepack = true;
    options.retain_root_manifest = true;

    const auto published = toxsync::publish_directory_revision(request, options);
    auto corrupt = test::read_file(published.retained_treepack);
    REQUIRE(!corrupt.empty());
    corrupt.front() ^= std::byte{0xff};
    test::write_file(published.retained_treepack, corrupt);

    // An exact retry must never bless pre-existing retained bytes merely
    // because their deterministic revision directory already exists.
    REQUIRE_THROWS(toxsync::publish_directory_revision(request, options));
}

TOXSYNC_TEST(directory_publication_rejects_a_parent_from_another_publisher) {
    if (!toxsync::ed25519_backend_available()) return;
    test::TempDir temp;
    const auto source = temp.path() / "source";
    std::filesystem::create_directories(source);
    test::write_file(source / "file", test::pattern(2048U, 0x5531U));

    toxsync::Ed25519PrivateKey first_private;
    toxsync::Ed25519PublicKey first_public;
    toxsync::Ed25519PrivateKey second_private;
    toxsync::Ed25519PublicKey second_public;
    REQUIRE(toxsync::ed25519_generate_key(first_private, first_public));
    REQUIRE(toxsync::ed25519_generate_key(second_private, second_public));
    (void)first_public;
    (void)second_public;

    toxsync::DirectoryPublicationRequest request;
    request.source_root = source;
    request.work_root = temp.path() / "work";
    request.store_root = temp.path() / "store";
    request.head_output = temp.path() / "head-1";
    request.namespace_id = toxsync::sha256(test::pattern(20U, 0x5532U));
    request.generation = 1U;
    request.private_key = first_private;
    toxsync::DirectoryPublicationOptions options;
    options.fsync_head_on_commit = false;
    options.content_options.fsync_on_commit = false;
    const auto first = toxsync::publish_directory_revision(request, options);

    request.previous = first.head;
    request.generation = 2U;
    request.private_key = second_private;
    request.head_output = temp.path() / "head-2";
    REQUIRE_THROWS(toxsync::publish_directory_revision(request, options));
}
