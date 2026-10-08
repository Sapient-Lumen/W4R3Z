#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"

#include <chrono>
#include <cstddef>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(Callable&& callable,
                   std::string_view expected,
                   const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

class TempTree final {
public:
    explicit TempTree(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
#ifdef __linux__
        const long process = static_cast<long>(::getpid());
#else
        const long process = 0;
#endif
        root = std::filesystem::temp_directory_path() /
               (std::string(stem) + "-" + std::to_string(process) + "-" +
                std::to_string(tick));
        std::filesystem::create_directories(root / "nested");
    }

    ~TempTree() {
        std::error_code ignored;
        std::filesystem::remove_all(root, ignored);
    }

    std::filesystem::path root;
};

std::span<const unsigned char> bytes(const std::string& value) {
    return {reinterpret_cast<const unsigned char*>(value.data()), value.size()};
}

std::string read_binary(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) fail("could not read test file");
    return {std::istreambuf_iterator<char>(input),
            std::istreambuf_iterator<char>()};
}

void write_direct(const std::filesystem::path& path,
                  const std::string& payload) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) fail("could not create direct test file");
    output.write(payload.data(), static_cast<std::streamsize>(payload.size()));
    if (!output) fail("could not write direct test file");
}

void test_absent_publish_exact_and_conflict() {
    TempTree tree("anonsync-immutable-reconcile");
    const std::filesystem::path destination = tree.root / "nested" / "file.bin";
    const std::string payload{"exact\0binary\xffpayload", 20U};

    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "absent immutable reconciliation") ==
            anonsync::SyncImmutableFileReconciliationOutcome::Absent,
        "an absent final name must reconcile as absent");

    anonsync::write_sync_file_atomically_create_new_no_symlink_or_throw(
        destination, bytes(payload), "binary immutable publication");
    require(read_binary(destination) == payload,
            "binary create-new publication must preserve embedded bytes");
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "exact immutable reconciliation") ==
            anonsync::SyncImmutableFileReconciliationOutcome::
                ExactAndDirectorySynced,
        "an exact durable final file must reconcile terminally");

    const std::string same_size_conflict(payload.size(), 'x');
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(same_size_conflict),
            "same-size immutable conflict") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "same-size different bytes must be a conflict");
    const std::string shorter = "short";
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(shorter), "size immutable conflict") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "a size mismatch must be a conflict");

    require_error(
        [&] {
            anonsync::write_sync_file_atomically_create_new_no_symlink_or_throw(
                destination, bytes(same_size_conflict),
                "duplicate immutable publication");
        },
        "already exists",
        "create-new publication must not replace an existing exact effect");
    require(read_binary(destination) == payload,
            "failed duplicate publication must preserve the first effect");
}

struct ThrowAtNamespaceContext final {
    bool observed = false;
};

void throw_after_namespace_publication(
    const anonsync::atomic_file_publication_detail::
        AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<ThrowAtNamespaceContext*>(raw_context);
    if (observation.cutpoint ==
        anonsync::atomic_file_publication_detail::
            AtomicFilePublicationCutpoint::NamespacePublished) {
        context.observed = true;
        throw std::runtime_error("simulated process loss after rename");
    }
}

#if !defined(_WIN32)

class ScopedUmask final {
public:
    explicit ScopedUmask(mode_t mask) noexcept : previous_(::umask(mask)) {}
    ScopedUmask(const ScopedUmask&) = delete;
    ScopedUmask& operator=(const ScopedUmask&) = delete;
    ~ScopedUmask() { (void)::umask(previous_); }

private:
    mode_t previous_;
};

void test_private_single_link_identity_is_required() {
    TempTree tree("anonsync-immutable-reconcile-private");
    const auto destination = tree.root / "nested" / "private-effect";
    const std::string payload = "private-single-link-effect";

    {
        ScopedUmask restrictive(0777);
        anonsync::write_sync_file_atomically_create_new_no_symlink_or_throw(
            destination, bytes(payload), "umask-independent publication");
    }

    struct stat status {};
    require(::stat(destination.c_str(), &status) == 0,
            "published private effect must be stat-able");
    require((status.st_mode & 07777) == (S_IRUSR | S_IWUSR),
            "publication must normalize final mode to 0600 despite umask");
    require(status.st_nlink == 1,
            "newly published immutable effect must have one link");

    require(::chmod(destination.c_str(), 0644) == 0,
            "test must be able to widen immutable effect permissions");
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "permission-widened effect") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "exact bytes with widened permissions must not become terminal effect authority");
    require(::chmod(destination.c_str(), 0600) == 0,
            "test must be able to restore private permissions");
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "permission-restored effect") ==
            anonsync::SyncImmutableFileReconciliationOutcome::
                ExactAndDirectorySynced,
        "restored private identity must reconcile exactly");

    const auto alias = tree.root / "hard-link-alias";
    std::filesystem::create_hard_link(destination, alias);
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "hard-linked effect") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "exact bytes in a multiply linked inode must not become terminal effect authority");
    std::filesystem::remove(alias);
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload), "single-link restored effect") ==
            anonsync::SyncImmutableFileReconciliationOutcome::
                ExactAndDirectorySynced,
        "single-link private identity must reconcile after alias removal");
}

#endif

void test_ambiguous_namespace_publication_is_recoverable() {
    TempTree tree("anonsync-immutable-reconcile-ambiguous");
    const std::filesystem::path destination = tree.root / "nested" / "effect";
    const std::string payload = "published-before-database-mark";
    ThrowAtNamespaceContext context;

    ++checks;
    try {
        anonsync::atomic_file_publication_detail::
            write_sync_file_atomically_create_new_with_observer_or_throw(
                destination, bytes(payload), "ambiguous effect publication",
                throw_after_namespace_publication, &context);
        fail("namespace cutpoint observer did not interrupt publication");
    } catch (const anonsync::SyncAtomicFilePublicationError& error) {
        require(
            error.outcome() ==
                anonsync::SyncAtomicFilePublicationOutcome::
                    PublishedDurabilityIndeterminate,
            "post-rename interruption must report indeterminate durability");
    }
    require(context.observed,
            "the namespace-published frontier must be observable");
    require(read_binary(destination) == payload,
            "the interrupted create-new effect must own the exact final bytes");

    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            destination, bytes(payload),
            "ambiguous effect restart reconciliation") ==
            anonsync::SyncImmutableFileReconciliationOutcome::
                ExactAndDirectorySynced,
        "restart reconciliation must convert an exact ambiguous effect into a durable terminal fact");
}

void test_nonregular_symlink_and_parent_symlink_fail_closed() {
    TempTree tree("anonsync-immutable-reconcile-types");
    const std::string payload = "payload";
    const auto directory_entry = tree.root / "nested" / "directory-entry";
    std::filesystem::create_directory(directory_entry);
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            directory_entry, bytes(payload), "directory conflict") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "a directory at the immutable final name must be a conflict");

#if !defined(_WIN32)
    const auto target = tree.root / "target";
    write_direct(target, payload);
    const auto symlink = tree.root / "nested" / "symlink-entry";
    std::filesystem::create_symlink(target, symlink);
    require(
        anonsync::reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            symlink, bytes(payload), "symlink conflict") ==
            anonsync::SyncImmutableFileReconciliationOutcome::ConflictingEntry,
        "a terminal symlink must never be followed as an exact effect");

    const auto real_parent = tree.root / "real-parent";
    std::filesystem::create_directory(real_parent);
    write_direct(real_parent / "value", payload);
    const auto parent_link = tree.root / "parent-link";
    std::filesystem::create_directory_symlink(real_parent, parent_link);
    require_error(
        [&] {
            (void)anonsync::
                reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
                    parent_link / "value", bytes(payload),
                    "parent symlink reconciliation");
        },
        "symlink",
        "parent-component symlinks must be rejected rather than followed");
#endif
}

void test_names_and_argument_validation() {
    require(
        std::string(anonsync::sync_immutable_file_reconciliation_outcome_name(
            anonsync::SyncImmutableFileReconciliationOutcome::Absent)) ==
            "absent",
        "absence name must be stable");
    require(
        std::string(anonsync::sync_immutable_file_reconciliation_outcome_name(
            anonsync::SyncImmutableFileReconciliationOutcome::
                ExactAndDirectorySynced)) ==
            "exact_and_directory_synced",
        "exact reconciliation name must be stable");
    require(
        std::string(anonsync::sync_immutable_file_reconciliation_outcome_name(
            anonsync::SyncImmutableFileReconciliationOutcome::
                ConflictingEntry)) == "conflicting_entry",
        "conflict name must be stable");

    const std::string payload;
    require_error(
        [&] {
            (void)anonsync::
                reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
                    {}, bytes(payload), "empty path");
        },
        "path is empty", "an empty path must fail before filesystem access");
    require_error(
        [&] {
            (void)anonsync::
                reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
                    "value", bytes(payload), "");
        },
        "label must not be empty",
        "an empty diagnostic label must be rejected");
}

}  // namespace

int main() {
    try {
        test_absent_publish_exact_and_conflict();
#if !defined(_WIN32)
        test_private_single_link_identity_is_required();
#endif
        test_ambiguous_namespace_publication_is_recoverable();
        test_nonregular_symlink_and_parent_symlink_fail_closed();
        test_names_and_argument_validation();
        std::cout << "sync atomic file reconciliation tests passed (" << checks
                  << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync atomic file reconciliation test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
