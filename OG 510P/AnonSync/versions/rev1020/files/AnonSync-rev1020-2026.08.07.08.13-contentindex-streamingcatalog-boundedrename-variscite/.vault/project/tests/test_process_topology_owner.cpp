#include "test_process_topology_owner.hpp"

#include <cerrno>
#include <csignal>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

#include <sys/wait.h>
#include <unistd.h>

namespace anonsync::test::detail {

TestProcessTopologyOwner::TestProcessTopologyOwner(
    pid_t leader, pid_t process_group) noexcept
    : leader_(leader), process_group_(process_group) {}

TestProcessTopologyOwner::TestProcessTopologyOwner(
    TestProcessTopologyOwner&& other) noexcept
    : leader_(std::exchange(other.leader_, -1)),
      process_group_(std::exchange(other.process_group_, -1)) {}

TestProcessTopologyOwner& TestProcessTopologyOwner::operator=(
    TestProcessTopologyOwner&& other) noexcept {
    if (this != &other) {
        terminate_and_reap_noexcept();
        leader_ = std::exchange(other.leader_, -1);
        process_group_ = std::exchange(other.process_group_, -1);
    }
    return *this;
}

TestProcessTopologyOwner::~TestProcessTopologyOwner() {
    terminate_and_reap_noexcept();
}

bool TestProcessTopologyOwner::active() const noexcept {
    return leader_ > 0 || process_group_ > 0;
}

pid_t TestProcessTopologyOwner::leader_process_id() const noexcept {
    return leader_;
}

std::optional<int> TestProcessTopologyOwner::try_complete_exit_or_throw(
    std::string_view label) {
    if (leader_ <= 0) {
        throw std::logic_error(
            "test-process leader has already been reaped or was never owned");
    }

    for (;;) {
        siginfo_t information{};
        if (::waitid(P_PID, static_cast<id_t>(leader_), &information,
                     WEXITED | WNOHANG | WNOWAIT) == 0) {
            if (information.si_pid == 0) return std::nullopt;
            if (information.si_pid == leader_) break;

            terminate_and_reap_noexcept();
            throw std::runtime_error(
                std::string(label) +
                " waitid(WNOWAIT) returned a non-owned child identity");
        }
        if (errno == EINTR) continue;

        const int wait_error = errno;
        if (wait_error == ECHILD) {
            relinquish_numeric_authority_noexcept();
        } else {
            terminate_and_reap_noexcept();
        }
        throw std::system_error(wait_error, std::generic_category(),
                                std::string(label) +
                                    " waitid(WNOWAIT)");
    }

    // The exact leader is still a waitable zombie here. Its unreaped process
    // identity pins the equal-valued process-group identity while surviving
    // group members are signaled.
    if (process_group_ > 0) {
        errno = 0;
        if (::kill(-process_group_, SIGKILL) != 0 && errno != ESRCH) {
            const int signal_error = errno;
            terminate_and_reap_noexcept();
            throw std::system_error(
                signal_error, std::generic_category(),
                std::string(label) + " remaining process-group kill");
        }
    }

    const pid_t exact_leader = leader_;
    int status = 0;
    for (;;) {
        const pid_t observed = ::waitpid(exact_leader, &status, 0);
        if (observed == exact_leader) {
            relinquish_numeric_authority_noexcept();
            return status;
        }
        if (observed < 0 && errno == EINTR) continue;

        if (observed < 0) {
            const int wait_error = errno;
            if (wait_error == ECHILD) {
                relinquish_numeric_authority_noexcept();
            } else {
                terminate_and_reap_noexcept();
            }
            throw std::system_error(wait_error, std::generic_category(),
                                    std::string(label) +
                                        " final waitpid");
        }

        terminate_and_reap_noexcept();
        throw std::runtime_error(
            std::string(label) +
            " final waitpid returned no owned child");
    }
}

void TestProcessTopologyOwner::terminate_and_reap_or_throw(
    std::string_view label) {
    const pid_t leader = std::exchange(leader_, -1);
    const pid_t process_group = std::exchange(process_group_, -1);
    int first_error = 0;
    std::string_view failed_operation;

    if (process_group > 0) {
        errno = 0;
        if (::kill(-process_group, SIGKILL) != 0 && errno != ESRCH) {
            first_error = errno;
            failed_operation = "process-group kill";
        }
    }
    // This also closes the inherited owner's pre-setpgid race. An unreaped
    // child PID cannot be recycled, so this direct signal cannot target an
    // unrelated task while exact leader authority is retained.
    if (leader > 0) {
        errno = 0;
        if (::kill(leader, SIGKILL) != 0 && errno != ESRCH &&
            first_error == 0) {
            first_error = errno;
            failed_operation = "leader kill";
        }

        int status = 0;
        for (;;) {
            const pid_t observed = ::waitpid(leader, &status, 0);
            if (observed == leader) break;
            if (observed < 0 && errno == EINTR) continue;
            if (observed < 0 && errno == ECHILD) break;
            if (first_error == 0) {
                first_error = observed < 0 ? errno : EIO;
                failed_operation = "leader reap";
            }
            break;
        }
    }

    if (first_error != 0) {
        throw std::system_error(
            first_error, std::generic_category(),
            std::string(label) + " " + std::string(failed_operation));
    }
}

void TestProcessTopologyOwner::terminate_and_reap_noexcept() noexcept {
    const pid_t leader = std::exchange(leader_, -1);
    const pid_t process_group = std::exchange(process_group_, -1);

    if (process_group > 0) {
        if (::kill(-process_group, SIGKILL) != 0 && errno != ESRCH) {
        }
    }
    if (leader > 0) {
        if (::kill(leader, SIGKILL) != 0 && errno != ESRCH) {
        }
        int status = 0;
        while (::waitpid(leader, &status, 0) < 0 && errno == EINTR) {
        }
    }
}

void TestProcessTopologyOwner::relinquish_numeric_authority_noexcept() noexcept {
    leader_ = -1;
    process_group_ = -1;
}

}  // namespace anonsync::test::detail
