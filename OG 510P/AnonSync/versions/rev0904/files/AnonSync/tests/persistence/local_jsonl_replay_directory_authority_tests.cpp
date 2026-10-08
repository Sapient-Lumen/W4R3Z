#include "local_jsonl_replay_directory_authority.hpp"
#include "sync_process_incarnation.hpp"

#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <thread>
#include <type_traits>
#include <vector>

#if !defined(_WIN32)
#include <cerrno>
#include <cstring>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;

#if !defined(_WIN32)

using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::persistence::LocalJsonlReplayDirectoryAuthority;
using anonsync::test::spawn_inherited_test_process_or_throw;
using namespace std::chrono_literals;

static_assert(
    !std::is_copy_constructible_v<LocalJsonlReplayDirectoryAuthority>);
static_assert(!std::is_copy_assignable_v<LocalJsonlReplayDirectoryAuthority>);
static_assert(std::is_nothrow_move_constructible_v<
              LocalJsonlReplayDirectoryAuthority>);
static_assert(
    std::is_nothrow_move_assignable_v<LocalJsonlReplayDirectoryAuthority>);

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

void set_mode_or_throw(const fs::path& path, mode_t mode) {
    if (::chmod(path.c_str(), mode) != 0) {
        throw std::runtime_error("chmod failed for " + path.generic_string() +
                                 ": " + std::strerror(errno));
    }
}

class TemporaryTree final {
public:
    TemporaryTree() {
        std::string pattern =
            (fs::temp_directory_path() /
             "anonsync-local-jsonl-directory-authority-XXXXXX")
                .string();
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char* const created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) {
            throw std::runtime_error(
                "mkdtemp failed for directory-authority fixture");
        }
        path_ = fs::path(created).lexically_normal();
    }

    ~TemporaryTree() {
        std::error_code ignored;
        fs::permissions(path_, fs::perms::owner_all,
                        fs::perm_options::add, ignored);
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

    [[nodiscard]] fs::path make_directory(const std::string& name,
                                          mode_t mode = 0700) const {
        const fs::path out = path_ / name;
        fs::create_directory(out);
        set_mode_or_throw(out, mode);
        return out;
    }

private:
    fs::path path_;
};

void test_frozen_attestation_and_move(TestState& test) {
    TemporaryTree tree;
    auto authority =
        LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
    const auto frozen = authority.attestation();

    test.require(authority.path() == tree.path().lexically_normal(),
                 "authority retained the normalized directory path");
    test.require(authority.absolute_path() ==
                     tree.path().lexically_normal().generic_string(),
                 "authority retained the exact absolute spelling");
    test.require(frozen.owner_user_id ==
                         static_cast<std::uint64_t>(::geteuid()) &&
                     frozen.effective_user_id ==
                         static_cast<std::uint64_t>(::geteuid()),
                 "attestation binds owner and effective user");
    test.require((frozen.permission_mode & 07777U) == 0700U,
                 "attestation binds exact permission bits");
    test.require(frozen.filesystem_name_maximum > 0U,
                 "attestation carries the filesystem name ceiling");
    test.require(frozen.path_name_maximum == -1 ||
                     frozen.path_name_maximum > 0,
                 "attestation carries a valid descriptor name ceiling");
    const std::string frozen_digest =
        anonsync::sync_directory_attestation_digest_or_throw(frozen);
    test.require(frozen_digest.size() == 64U &&
                     frozen_digest ==
                         anonsync::sync_directory_attestation_digest_or_throw(
                             frozen),
                 "attestation digest is stable canonical SHA-256 evidence");
    auto changed = frozen;
    changed.inode ^= 1U;
    test.require(
        anonsync::sync_directory_attestation_digest_or_throw(changed) !=
            frozen_digest,
        "attestation digest changes when retained directory identity changes");
    authority.verify_or_throw("direct authority fixture");
    test.require(true, "unchanged directory reproof succeeds");

    LocalJsonlReplayDirectoryAuthority moved(std::move(authority));
    moved.verify_or_throw("moved direct authority fixture");
    test.require(moved.attestation().device == frozen.device &&
                     moved.attestation().inode == frozen.inode,
                 "move preserves the frozen directory identity");
    test.require_throws(
        [&] { authority.verify_or_throw("moved-from direct authority"); },
        "not initialized",
        "moved-from authority cannot be reused");
}

void test_initial_permission_policy(TestState& test) {
    TemporaryTree tree;
    const fs::path group_writable = tree.make_directory("group-writable", 0770);
    test.require_throws(
        [&] {
            (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(
                group_writable);
        },
        "group/other-writable directory",
        "group-writable parent is rejected before authority minting");

    const fs::path other_writable = tree.make_directory("other-writable", 0702);
    test.require_throws(
        [&] {
            (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(
                other_writable);
        },
        "group/other-writable directory",
        "other-writable parent is rejected before authority minting");

    const fs::path no_owner_write = tree.make_directory("no-owner-write", 0500);
    test.require_throws(
        [&] {
            (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(
                no_owner_write);
        },
        "owner read/write/search permission is required",
        "owner mutation permission is a stated authority precondition");

    test.require_throws(
        [&] {
            (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(
                fs::path("relative-directory"));
        },
        "must be absolute",
        "relative path cannot mint directory authority");

    test.require_throws(
        [&] {
            (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(
                tree.path() / "untrusted-component" / ".." / "selected");
        },
        "parent traversal component",
        "lexical parent traversal cannot reinterpret directory authority");
}

void test_attestation_change_is_sticky_revocation(TestState& test) {
    {
        TemporaryTree tree;
        auto authority =
            LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
        set_mode_or_throw(tree.path(), 0770);
        test.require_throws(
            [&] { authority.verify_or_throw("widened parent"); },
            "group/other-writable directory",
            "permission widening immediately rejects authority");
        set_mode_or_throw(tree.path(), 0700);
        test.require_throws(
            [&] { authority.verify_or_throw("restored widened parent"); },
            "authority is revoked",
            "restoring visible mode cannot resurrect authority");
    }

    {
        TemporaryTree tree;
        auto authority =
            LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
        set_mode_or_throw(tree.path(), 0750);
        test.require_throws(
            [&] { authority.verify_or_throw("changed parent mode"); },
            "attestation changed",
            "even policy-compatible mode drift revokes frozen authority");
        set_mode_or_throw(tree.path(), 0700);
        test.require_throws(
            [&] { authority.verify_or_throw("restored parent mode"); },
            "authority is revoked",
            "exact-attestation failure remains sticky after restoration");
    }
}

void test_path_topology_reproof(TestState& test) {
    {
        TemporaryTree tree;
        const fs::path selected = tree.make_directory("selected");
        const fs::path displaced = tree.path() / "displaced";
        auto authority =
            LocalJsonlReplayDirectoryAuthority::open_or_throw(selected);
        fs::rename(selected, displaced);
        (void)tree.make_directory("selected");
        test.require_throws(
            [&] { authority.verify_or_throw("rebound parent"); },
            "no longer names the retained directory",
            "rename and replacement cannot redirect retained authority");
        test.require_throws(
            [&] { authority.verify_or_throw("rebound parent retry"); },
            "authority is revoked",
            "path rebinding permanently revokes the authority object");
    }

    {
        TemporaryTree tree;
        const fs::path real = tree.make_directory("real");
        const fs::path alias = tree.path() / "alias";
        if (::symlink(real.c_str(), alias.c_str()) != 0) {
            throw std::runtime_error("could not create directory symlink fixture");
        }
        test.require_throws(
            [&] {
                (void)LocalJsonlReplayDirectoryAuthority::open_or_throw(alias);
            },
            "symbolic-link parent component",
            "symlink traversal cannot mint directory authority");
    }
}

void test_foreign_thread_rejected_without_revocation(TestState& test) {
    TemporaryTree tree;
    auto authority =
        LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
    std::string reason;
    std::thread worker([&] {
        try {
            authority.verify_or_throw("foreign-thread directory authority");
        } catch (const std::exception& error) {
            reason = error.what();
        }
    });
    worker.join();

    test.require(reason.find("originating thread") != std::string::npos,
                 "foreign thread was rejected before directory reproof");
    authority.verify_or_throw("owner-thread directory authority");
    test.require(true,
                 "foreign-thread rejection did not revoke the owner capability");
}

void test_foreign_thread_noexcept_access_fails_stopped(TestState& test) {
    TemporaryTree tree;
    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            auto child_authority =
                LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
            std::thread worker([&] {
                (void)child_authority.absolute_path();
            });
            worker.join();
            return 92;
        },
        "local JSONL directory foreign-thread noexcept access");
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, 5s,
        "local JSONL directory foreign-thread noexcept access");
    test.require(true,
                 "foreign-thread noexcept accessor failed stopped");
}

void test_fork_inheritance_fail_stops(TestState& test) {
    TemporaryTree tree;
    auto authority =
        LocalJsonlReplayDirectoryAuthority::open_or_throw(tree.path());
    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            authority.verify_or_throw("inherited directory authority");
            return 91;
        },
        "local JSONL directory authority inheritance");
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, 5s,
        "local JSONL directory authority inheritance");
    test.require(true,
                 "fork child fail-stopped before inherited authority use");
    authority.verify_or_throw("parent directory authority after hostile child");
    test.require(true, "parent authority remains usable after hostile child");
}

#endif

}  // namespace

int main() {
#if defined(_WIN32)
    std::cout
        << "local JSONL replay directory authority: unavailable on Windows\n";
    return 0;
#else
    try {
        TestState test;
        test_frozen_attestation_and_move(test);
        test_initial_permission_policy(test);
        test_attestation_change_is_sticky_revocation(test);
        test_path_topology_reproof(test);
        test_foreign_thread_rejected_without_revocation(test);
        test_foreign_thread_noexcept_access_fails_stopped(test);
        test_fork_inheritance_fail_stops(test);
        std::cout << "local JSONL replay directory authority: " << test.passed
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "local JSONL replay directory authority: " << error.what()
                  << '\n';
        return 1;
    }
#endif
}
