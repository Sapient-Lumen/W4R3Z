#include "local_jsonl_replay_namespace.hpp"
#include "sync_process_incarnation.hpp"
#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <thread>
#include <vector>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::persistence::LocalJsonlReplayJournalPublicationState;
using anonsync::persistence::LocalJsonlReplayLockContention;
using anonsync::persistence::LocalJsonlReplayNamespace;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
using namespace std::chrono_literals;
#endif

struct TestState final {
    std::uint64_t passed = 0;

    void require(bool condition, const std::string& label) {
        if (!condition) throw std::runtime_error(label);
        ++passed;
    }

    template <typename Function>
    void require_throws(Function&& operation,
                        const std::string& expected_fragment,
                        const std::string& label) {
        try {
            operation();
        } catch (const std::exception& error) {
            if (!expected_fragment.empty() &&
                std::string(error.what()).find(expected_fragment) ==
                    std::string::npos) {
                throw std::runtime_error(label + ": wrong rejection: " +
                                         error.what());
            }
            ++passed;
            return;
        }
        throw std::runtime_error(label + ": operation succeeded");
    }
};

class TemporaryTree final {
public:
    TemporaryTree() {
#if !defined(_WIN32)
        std::string pattern =
            (fs::temp_directory_path() /
             "anonsync-local-jsonl-namespace-XXXXXX")
                .string();
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char* const created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) {
            throw std::runtime_error(
                "mkdtemp failed for namespace fixture");
        }
        path_ = fs::path(created).lexically_normal();
#else
        path_ = fs::temp_directory_path() / "anonsync-local-jsonl-namespace";
        fs::create_directories(path_);
#endif
    }

    ~TemporaryTree() {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

class CurrentDirectoryGuard final {
public:
    CurrentDirectoryGuard() : previous_(fs::current_path()) {}
    ~CurrentDirectoryGuard() {
        std::error_code error;
        fs::current_path(previous_, error);
    }

private:
    fs::path previous_;
};

void write_bytes(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("could not create fixture: " +
                                 path.generic_string());
    }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) {
        throw std::runtime_error("could not publish fixture: " +
                                 path.generic_string());
    }
}

std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("could not read fixture: " +
                                 path.generic_string());
    }
    return std::string(std::istreambuf_iterator<char>(input),
                       std::istreambuf_iterator<char>());
}

#if !defined(_WIN32)

void test_retained_relative_namespace(TestState& test) {
    TemporaryTree tree;
    test.require_throws(
        [&] {
            (void)LocalJsonlReplayNamespace::open_or_throw(
                tree.path() / "untrusted-component" / ".." /
                "ambiguous-ledger.jsonl");
        },
        "parent traversal component",
        "ledger selection rejects lexical parent traversal ambiguity");
    const fs::path first = tree.path() / "first";
    const fs::path second = tree.path() / "second";
    fs::create_directories(first);
    fs::create_directories(second);

    CurrentDirectoryGuard cwd;
    fs::current_path(first);
    auto authority = LocalJsonlReplayNamespace::open_or_throw("ledger.jsonl");
    test.require(authority.absolute_ledger_path() ==
                     (first / "ledger.jsonl").generic_string(),
                 "relative ledger path froze to the selected absolute name");

    fs::current_path(second);
    authority.acquire_lock_or_throw();

    {
        auto journal =
            authority.create_journal_staging_exclusive_or_throw();
        journal.write_all_or_throw("journal-witness", "journal fixture");
        journal.fsync_or_throw("journal fixture");
        authority.verify_journal_staging_descriptor_bound_or_throw(
            journal.descriptor(), "journal fixture staging binding");
        authority.publish_open_journal_staging_to_journal_or_throw(
            journal.descriptor(), "journal fixture publication");
        journal.close_or_throw("journal fixture");
    }
    test.require(read_bytes(first / "ledger.jsonl.journal") ==
                     "journal-witness",
                 "journal publication stayed in retained directory");
    test.require(!fs::exists(second / "ledger.jsonl.journal"),
                 "cwd change did not redirect journal publication");
    test.require(authority.unlink_journal_if_present_or_throw(),
                 "retained journal was retired");
    authority.fsync_directory_or_throw("namespace test journal retirement");

    const std::string temporary_name = authority.make_temporary_name_or_throw(
        static_cast<std::int64_t>(::getpid()), 1);
    {
        auto temporary = authority.create_temporary_exclusive_or_throw(
            temporary_name);
        temporary.write_all_or_throw("retained-payload\n", "temporary fixture");
        temporary.fsync_or_throw("temporary fixture");
        authority.verify_temporary_descriptor_bound_or_throw(
            temporary_name, temporary.descriptor(),
            "temporary fixture binding");
        authority.rename_open_temporary_over_ledger_or_throw(
            temporary_name, temporary.descriptor());
        temporary.close_or_throw("renamed temporary fixture");
    }
    authority.fsync_directory_or_throw("namespace test ledger publication");
    test.require(authority.read_ledger_or_empty_or_throw(1024) ==
                     "retained-payload\n",
                 "descriptor-relative ledger read returned exact bytes");
    test.require(read_bytes(first / "ledger.jsonl") == "retained-payload\n",
                 "ledger rename stayed in retained directory");
    test.require(!fs::exists(second / "ledger.jsonl") &&
                     !fs::exists(second / "ledger.jsonl.lock"),
                 "cwd change created no second-directory authority artifacts");
}

void test_parent_rebinding_rejected(TestState& test) {
    TemporaryTree tree;
    const fs::path selected = tree.path() / "selected";
    const fs::path displaced = tree.path() / "displaced";
    fs::create_directories(selected);

    auto authority = LocalJsonlReplayNamespace::open_or_throw(
        selected / "ledger.jsonl");
    authority.acquire_lock_or_throw();
    fs::rename(selected, displaced);
    fs::create_directories(selected);

    test.require_throws(
        [&] { (void)authority.ledger_exists_or_throw(); },
        "no longer names the retained directory",
        "parent pathname replacement revoked retained authority");
    test.require(!fs::exists(selected / "ledger.jsonl"),
                 "revoked authority did not touch replacement directory");
}

void test_directory_authority_is_composed_and_sticky(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
    const auto frozen = authority.directory_attestation();

    test.require(authority.absolute_parent_path() ==
                     tree.path().lexically_normal().generic_string(),
                 "namespace exposes the frozen absolute parent path");
    test.require(frozen.owner_user_id ==
                         static_cast<std::uint64_t>(::geteuid()) &&
                     frozen.effective_user_id ==
                         static_cast<std::uint64_t>(::geteuid()),
                 "namespace composes the exact directory owner attestation");

    authority.acquire_lock_or_throw();
    const mode_t original_mode =
        static_cast<mode_t>(frozen.permission_mode & 07777U);
    if (::chmod(tree.path().c_str(), original_mode | S_IWGRP) != 0) {
        throw std::runtime_error(
            "could not widen directory mode for namespace fixture");
    }
    test.require_throws(
        [&] { (void)authority.ledger_exists_or_throw(); },
        "group/other-writable directory",
        "namespace operation rejects widened parent authority");
    if (::chmod(tree.path().c_str(), original_mode) != 0) {
        throw std::runtime_error(
            "could not restore directory mode for namespace fixture");
    }
    test.require_throws(
        [&] { (void)authority.ledger_exists_or_throw(); },
        "authority is revoked",
        "namespace cannot resurrect a restored parent authority");
    test.require(!fs::exists(ledger),
                 "revoked namespace did not create ledger bytes");
}

void test_hostile_path_topology_rejected(TestState& test) {
    {
        TemporaryTree tree;
        const fs::path real = tree.path() / "real";
        const fs::path alias = tree.path() / "alias";
        fs::create_directories(real);
        if (::symlink(real.c_str(), alias.c_str()) != 0) {
            throw std::runtime_error("could not create parent symlink fixture");
        }
        test.require_throws(
            [&] {
                (void)LocalJsonlReplayNamespace::open_or_throw(
                    alias / "ledger.jsonl");
            },
            "symbolic-link parent component",
            "symbolic-link parent was rejected component by component");
    }
    {
        TemporaryTree tree;
        const fs::path target = tree.path() / "target";
        const fs::path ledger = tree.path() / "ledger.jsonl";
        write_bytes(target, "sentinel");
        if (::symlink(target.c_str(), ledger.c_str()) != 0) {
            throw std::runtime_error("could not create ledger symlink fixture");
        }
        auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
        test.require_throws(
            [&] { authority.acquire_lock_or_throw(); },
            "symbolic-link path",
            "symbolic-link ledger member was rejected before lock ownership");
        test.require(read_bytes(target) == "sentinel",
                     "ledger symlink target remained unchanged");
    }
    {
        TemporaryTree tree;
        const fs::path target = tree.path() / "target";
        const fs::path ledger = tree.path() / "ledger.jsonl";
        write_bytes(target, "sentinel");
        if (::link(target.c_str(), ledger.c_str()) != 0) {
            throw std::runtime_error("could not create ledger hard-link fixture");
        }
        auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
        test.require_throws(
            [&] { authority.acquire_lock_or_throw(); },
            "multiply-linked path",
            "multiply-linked ledger member was rejected");
        test.require(read_bytes(target) == "sentinel",
                     "hard-link target remained unchanged");
    }
    {
        TemporaryTree tree;
        const fs::path target = tree.path() / "target";
        const fs::path lock = tree.path() / "ledger.jsonl.lock";
        write_bytes(target, "sentinel");
        if (::symlink(target.c_str(), lock.c_str()) != 0) {
            throw std::runtime_error("could not create lock symlink fixture");
        }
        auto authority = LocalJsonlReplayNamespace::open_or_throw(
            tree.path() / "ledger.jsonl");
        test.require_throws(
            [&] { authority.acquire_lock_or_throw(); },
            "symbolic-link path",
            "symbolic-link lock member was rejected");
        test.require(read_bytes(target) == "sentinel",
                     "lock symlink target remained unchanged");
    }
}

void test_journal_publication_never_overwrites(TestState& test) {
    TemporaryTree tree;
    auto authority = LocalJsonlReplayNamespace::open_or_throw(
        tree.path() / "ledger.jsonl");
    authority.acquire_lock_or_throw();
    auto staging = authority.create_journal_staging_exclusive_or_throw();
    staging.write_all_or_throw("authorized-journal", "journal no-replace fixture");
    staging.fsync_or_throw("journal no-replace fixture");

    const fs::path final_path = tree.path() / "ledger.jsonl.journal";
    write_bytes(final_path, "preexisting-witness");
    test.require_throws(
        [&] {
            authority.publish_open_journal_staging_to_journal_or_throw(
                staging.descriptor(), "journal no-replace fixture");
        },
        "destination already exists",
        "journal publication rejected a preexisting final witness");
    test.require(read_bytes(final_path) == "preexisting-witness",
                 "journal no-replace publication preserved final witness");
    test.require(read_bytes(tree.path() / "ledger.jsonl.journal.stage") ==
                     "authorized-journal",
                 "journal no-replace publication preserved staging evidence");
    staging.close_or_throw("journal no-replace fixture");
}

void test_journal_publication_reuses_reserved_names(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
    authority.acquire_lock_or_throw();

    // Some older Linux/overlayfs combinations retain a stale negative/positive
    // dentry interaction for repeated renameat2(RENAME_NOREPLACE) publication.
    // The link/unlink protocol deliberately uses the same reserved names on
    // every commit, so exercise repeated publication rather than a one-shot
    // happy path.
    for (int iteration = 1; iteration <= 4; ++iteration) {
        const std::string payload =
            "journal-witness-" + std::to_string(iteration);
        auto staging =
            authority.create_journal_staging_exclusive_or_throw();
        staging.write_all_or_throw(payload, "reused journal staging fixture");
        staging.fsync_or_throw("reused journal staging fixture");
        authority.publish_open_journal_staging_to_journal_or_throw(
            staging.descriptor(), "reused journal publication fixture");
        staging.close_or_throw("reused final journal fixture");

        test.require(
            authority.journal_publication_state_or_throw() ==
                LocalJsonlReplayJournalPublicationState::journal_only,
            "reused publication reached the exact final-only topology");
        test.require(read_bytes(ledger.string() + ".journal") == payload,
                     "reused publication retained exact journal bytes");
        test.require(authority.unlink_journal_if_present_or_throw(),
                     "reused publication retired the final journal");
        authority.fsync_directory_or_throw(
            "reused journal publication retirement");
        test.require(
            authority.journal_publication_state_or_throw() ==
                LocalJsonlReplayJournalPublicationState::absent,
            "reused publication returned to the empty journal topology");
    }
}

void test_journal_linked_pair_topology_is_exact(TestState& test) {
    {
        TemporaryTree tree;
        const fs::path ledger = tree.path() / "ledger.jsonl";
        auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
        authority.acquire_lock_or_throw();
        write_bytes(ledger.string() + ".journal", "final");
        write_bytes(ledger.string() + ".journal.stage", "stage");
        test.require_throws(
            [&] { (void)authority.journal_publication_state_or_throw(); },
            "authorized linked pair",
            "two unrelated journal names were not mistaken for publication state");
        test.require(read_bytes(ledger.string() + ".journal") == "final" &&
                         read_bytes(ledger.string() + ".journal.stage") ==
                             "stage",
                     "rejected unrelated journal names remained untouched");
    }
    {
        TemporaryTree tree;
        const fs::path ledger = tree.path() / "ledger.jsonl";
        const fs::path sentinel = tree.path() / "sentinel";
        write_bytes(sentinel, "outside-authority");
        fs::create_hard_link(sentinel, ledger.string() + ".journal");
        auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);
        test.require_throws(
            [&] { authority.acquire_lock_or_throw(); },
            "unauthorized hard links",
            "an external hard link could not masquerade as a final journal");
        test.require(read_bytes(sentinel) == "outside-authority",
                     "rejected external journal hard link preserved its target");
    }
}

void test_exact_temporary_descriptor_binding(TestState& test) {
    TemporaryTree tree;
    auto authority = LocalJsonlReplayNamespace::open_or_throw(
        tree.path() / "ledger.jsonl");
    authority.acquire_lock_or_throw();
    const std::string name = authority.make_temporary_name_or_throw(
        static_cast<std::int64_t>(::getpid()), 1);
    auto temporary = authority.create_temporary_exclusive_or_throw(name);
    temporary.write_all_or_throw("authorized\n", "bound temporary");
    temporary.fsync_or_throw("bound temporary");

    const fs::path displaced = tree.path() / "displaced-temp";
    fs::rename(tree.path() / name, displaced);
    write_bytes(tree.path() / name, "attacker\n");
    test.require_throws(
        [&] {
            authority.rename_open_temporary_over_ledger_or_throw(
                name, temporary.descriptor());
        },
        "changed while it was opened",
        "rename rejected a name no longer bound to the written descriptor");
    test.require(!fs::exists(tree.path() / "ledger.jsonl"),
                 "descriptor mismatch did not publish attacker bytes");
    test.require(read_bytes(tree.path() / name) == "attacker\n",
                 "descriptor mismatch did not mutate replacement temp name");
    temporary.close_or_throw("displaced temporary");
}

void test_lock_name_rebinding_revokes_owner(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    auto owner = LocalJsonlReplayNamespace::open_or_throw(ledger);
    owner.acquire_lock_or_throw();
    const fs::path lock = tree.path() / "ledger.jsonl.lock";
    fs::remove(lock);
    write_bytes(lock, "replacement-lock");

    test.require_throws(
        [&] { (void)owner.ledger_exists_or_throw(); },
        "path changed while it was opened",
        "lock unlink-and-recreate revoked the orphaned flock owner");

    auto replacement_owner = LocalJsonlReplayNamespace::open_or_throw(ledger);
    replacement_owner.acquire_lock_or_throw();
    test.require(true,
                 "replacement lock namespace is independently acquirable");
    replacement_owner.release_lock_noexcept();
    owner.release_lock_noexcept();
}

void test_foreign_thread_rejected_without_consuming_owners(
    TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    auto authority = LocalJsonlReplayNamespace::open_or_throw(ledger);

    std::string namespace_reason;
    std::thread namespace_worker([&] {
        try {
            (void)authority.ledger_exists_or_throw(
                "foreign-thread namespace fixture");
        } catch (const std::exception& error) {
            namespace_reason = error.what();
        }
    });
    namespace_worker.join();
    test.require(namespace_reason.find("originating thread") !=
                     std::string::npos,
                 "foreign thread was rejected before namespace observation");
    test.require(!authority.ledger_exists_or_throw(
                     "owner-thread namespace fixture"),
                 "foreign namespace rejection preserved owner authority");

    authority.acquire_lock_or_throw();
    const std::string temporary_name = authority.make_temporary_name_or_throw(
        static_cast<std::int64_t>(::getpid()), 1);
    auto temporary =
        authority.create_temporary_exclusive_or_throw(temporary_name);
    std::string file_reason;
    std::thread file_worker([&] {
        try {
            temporary.write_all_or_throw(
                "forbidden", "foreign-thread open-file fixture");
        } catch (const std::exception& error) {
            file_reason = error.what();
        }
    });
    file_worker.join();
    test.require(file_reason.find("originating thread") !=
                     std::string::npos,
                 "foreign thread was rejected before descriptor mutation");
    temporary.write_all_or_throw("owner-bytes",
                                 "owner-thread open-file fixture");
    temporary.fsync_or_throw("owner-thread open-file fixture");
    temporary.close_or_throw("owner-thread open-file fixture");
    test.require(read_bytes(tree.path() / temporary_name) == "owner-bytes",
                 "foreign open-file rejection preserved exact owner bytes");
    test.require(authority.unlink_temporary_if_present_or_throw(temporary_name),
                 "owner retired the thread-bound temporary file");
    authority.release_lock_noexcept();
}

void test_foreign_thread_noexcept_release_fails_stopped(
    TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "thread-affine-ledger.jsonl";
    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            auto child_owner =
                LocalJsonlReplayNamespace::open_or_throw(ledger);
            child_owner.acquire_lock_or_throw();
            std::thread worker([&] {
                child_owner.release_lock_noexcept();
            });
            worker.join();
            return 98;
        },
        "local JSONL namespace foreign-thread noexcept release");
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, 5s,
        "local JSONL namespace foreign-thread noexcept release");
    test.require(true,
                 "foreign-thread noexcept lock release failed stopped");
}

void test_fork_child_cannot_unlock_parent(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    auto owner = LocalJsonlReplayNamespace::open_or_throw(ledger);
    owner.acquire_lock_or_throw();

    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            owner.release_lock_noexcept();
            return 99;
        },
        "local JSONL namespace inherited lock misuse");
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, 5s,
        "local JSONL namespace inherited lock misuse");
    test.require(true,
                 "fork child fail-stopped before unlocking inherited flock");

    test.require(!owner.ledger_exists_or_throw(),
                 "parent authority remained usable after hostile child");
    auto contender = LocalJsonlReplayNamespace::open_or_throw(ledger);
    try {
        contender.acquire_lock_or_throw();
        throw std::runtime_error(
            "separate contender acquired lock after child misuse");
    } catch (const LocalJsonlReplayLockContention&) {
        ++test.passed;
    }
    owner.release_lock_noexcept();
    contender.acquire_lock_or_throw();
    test.require(true, "lock became acquirable only after parent release");
}

void test_restored_lock_name_cannot_resurrect_owner(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger = tree.path() / "ledger.jsonl";
    const fs::path lock = tree.path() / "ledger.jsonl.lock";
    const fs::path displaced = tree.path() / "displaced-lock";
    auto owner = LocalJsonlReplayNamespace::open_or_throw(ledger);
    owner.acquire_lock_or_throw();

    fs::rename(lock, displaced);
    write_bytes(lock, "replacement-lock");
    test.require_throws(
        [&] { (void)owner.ledger_exists_or_throw(); },
        "path changed while it was opened",
        "transient lock rebinding revoked the original namespace");

    fs::remove(lock);
    fs::rename(displaced, lock);
    test.require_throws(
        [&] { (void)owner.ledger_exists_or_throw(); },
        "namespace authority is revoked",
        "restoring the exact locked inode cannot resurrect namespace authority");

    auto contender = LocalJsonlReplayNamespace::open_or_throw(ledger);
    try {
        contender.acquire_lock_or_throw();
        throw std::runtime_error(
            "contender acquired restored lock before original release");
    } catch (const LocalJsonlReplayLockContention&) {
        ++test.passed;
    }
    owner.release_lock_noexcept();
    contender.acquire_lock_or_throw();
    test.require(true,
                 "restored lock became acquirable only after revoked owner release");
}

#endif

}  // namespace

int main() {
#if defined(_WIN32)
    std::cout << "local JSONL replay namespace: unavailable on Windows\n";
    return 0;
#else
    try {
        TestState test;
        test_retained_relative_namespace(test);
        test_parent_rebinding_rejected(test);
        test_directory_authority_is_composed_and_sticky(test);
        test_hostile_path_topology_rejected(test);
        test_journal_publication_never_overwrites(test);
        test_journal_publication_reuses_reserved_names(test);
        test_journal_linked_pair_topology_is_exact(test);
        test_exact_temporary_descriptor_binding(test);
        test_lock_name_rebinding_revokes_owner(test);
        test_restored_lock_name_cannot_resurrect_owner(test);
        test_foreign_thread_rejected_without_consuming_owners(test);
        test_foreign_thread_noexcept_release_fails_stopped(test);
        test_fork_child_cannot_unlock_parent(test);
        std::cout << "local JSONL replay namespace: " << test.passed
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "local JSONL replay namespace: " << error.what() << '\n';
        return 1;
    }
#endif
}
