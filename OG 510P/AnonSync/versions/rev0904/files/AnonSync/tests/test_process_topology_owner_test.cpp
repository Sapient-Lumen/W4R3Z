#include "test_process_topology_owner.hpp"

#include <cerrno>
#include <csignal>
#include <cstdint>
#include <cstring>
#include <deque>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern "C" int __real_kill(pid_t, int);
extern "C" int __real_waitid(idtype_t, id_t, siginfo_t*, int);
extern "C" pid_t __real_waitpid(pid_t, int*, int);

namespace {

using anonsync::test::detail::TestProcessTopologyOwner;

enum class Operation {
    signal,
    observe,
    reap,
};

struct Action final {
    Operation operation = Operation::signal;
    pid_t identity = -1;
    int flags_or_signal = 0;
    long result = 0;
    int error = 0;
    pid_t observed_identity = 0;
    int wait_status = 0;
};

struct Event final {
    Operation operation = Operation::signal;
    pid_t identity = -1;
    int flags_or_signal = 0;
};

struct ScriptState final {
    bool armed = false;
    std::deque<Action> actions;
    std::vector<Event> events;
    std::string mismatch;
};

ScriptState script_state;

[[nodiscard]] Action signal_action(pid_t identity, int result = 0,
                                   int error = 0) {
    return Action{Operation::signal, identity, SIGKILL, result, error, 0, 0};
}

[[nodiscard]] Action observe_action(pid_t identity, int result,
                                    int error, pid_t observed_identity) {
    return Action{Operation::observe,
                  identity,
                  WEXITED | WNOHANG | WNOWAIT,
                  result,
                  error,
                  observed_identity,
                  0};
}

[[nodiscard]] Action pending_action(pid_t identity) {
    return observe_action(identity, 0, 0, 0);
}

[[nodiscard]] Action terminal_action(pid_t identity) {
    return observe_action(identity, 0, 0, identity);
}

[[nodiscard]] Action reap_action(pid_t identity, pid_t result,
                                 int wait_status = 0, int error = 0) {
    return Action{Operation::reap, identity, 0, result, error, 0, wait_status};
}

void note_mismatch_noexcept(std::string message) noexcept {
    if (script_state.mismatch.empty()) {
        try {
            script_state.mismatch = std::move(message);
        } catch (...) {
            script_state.mismatch = "script mismatch (message allocation failed)";
        }
    }
    errno = EIO;
}

[[nodiscard]] std::optional<Action> consume_action_noexcept(
    Operation operation, pid_t identity, int flags_or_signal) noexcept {
    try {
        script_state.events.push_back(Event{operation, identity,
                                            flags_or_signal});
        if (script_state.actions.empty()) {
            note_mismatch_noexcept("unexpected topology syscall after script exhaustion");
            return std::nullopt;
        }
        const Action action = script_state.actions.front();
        script_state.actions.pop_front();
        if (action.operation != operation || action.identity != identity ||
            action.flags_or_signal != flags_or_signal) {
            note_mismatch_noexcept("topology syscall did not match scripted operation");
            return std::nullopt;
        }
        return action;
    } catch (...) {
        note_mismatch_noexcept("topology syscall recorder failed");
        return std::nullopt;
    }
}

class ScopedScript final {
public:
    explicit ScopedScript(std::initializer_list<Action> actions) {
        if (script_state.armed) {
            throw std::logic_error("nested topology syscall script");
        }
        script_state = ScriptState{};
        script_state.armed = true;
        script_state.actions.assign(actions.begin(), actions.end());
    }

    ScopedScript(const ScopedScript&) = delete;
    ScopedScript& operator=(const ScopedScript&) = delete;

    ~ScopedScript() {
        script_state.armed = false;
        script_state.actions.clear();
    }

    [[nodiscard]] std::size_t event_count() const noexcept {
        return script_state.events.size();
    }

    void require_complete() const {
        if (!script_state.mismatch.empty()) {
            throw std::runtime_error(script_state.mismatch);
        }
        if (!script_state.actions.empty()) {
            throw std::runtime_error(
                "topology owner left scripted syscalls unconsumed");
        }
    }
};

void require(bool condition, std::string_view message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Exception, typename Callable>
[[nodiscard]] bool throws_as(Callable&& callable) {
    try {
        std::forward<Callable>(callable)();
    } catch (const Exception&) {
        return true;
    }
    return false;
}

void test_pending_observation_preserves_authority(std::uint64_t& checks) {
    constexpr pid_t leader = 41001;
    ScopedScript script({
        pending_action(leader),
        signal_action(-leader),
        signal_action(leader),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    const std::optional<int> status =
        owner.try_complete_exit_or_throw("pending owner");
    require(!status.has_value() && owner.active() &&
                owner.leader_process_id() == leader,
            "pending WNOWAIT observation consumed numeric authority", checks);

    owner.terminate_and_reap_or_throw("pending owner cleanup");
    require(!owner.active() && owner.leader_process_id() < 0,
            "explicit cleanup retained pending owner authority", checks);
    script.require_complete();
}

void test_exact_completion_consumes_before_return(std::uint64_t& checks) {
    constexpr pid_t leader = 41002;
    constexpr int expected_status = 7 << 8;
    ScopedScript script({
        terminal_action(leader),
        signal_action(-leader),
        reap_action(leader, leader, expected_status),
    });
    TestProcessTopologyOwner owner(leader, leader);

    const std::optional<int> status =
        owner.try_complete_exit_or_throw("terminal owner");
    require(status == expected_status && !owner.active() &&
                owner.leader_process_id() < 0,
            "exact completion did not consume leader and group authority",
            checks);
    const std::size_t completed_events = script.event_count();
    owner.terminate_and_reap_noexcept();
    require(script.event_count() == completed_events,
            "cleanup after exact reap issued a stale numeric syscall", checks);
    require(throws_as<std::logic_error>([&] {
                (void)owner.try_complete_exit_or_throw("completed owner");
            }),
            "completed owner accepted a second terminal transition", checks);
    require(script.event_count() == completed_events,
            "rejected second transition issued a numeric syscall", checks);
    script.require_complete();
}

void test_no_group_completion_has_no_group_signal(std::uint64_t& checks) {
    constexpr pid_t leader = 41003;
    ScopedScript script({
        terminal_action(leader),
        reap_action(leader, leader, 0),
    });
    TestProcessTopologyOwner owner(leader, -1);

    const std::optional<int> status =
        owner.try_complete_exit_or_throw("leader-only owner");
    require(status == 0 && !owner.active(),
            "leader-only completion retained authority", checks);
    require(script.event_count() == 2,
            "leader-only completion attempted an unowned group signal", checks);
    script.require_complete();
}

void test_interrupted_syscalls_retry_exactly(std::uint64_t& checks) {
    constexpr pid_t leader = 41004;
    constexpr int expected_status = 3 << 8;
    ScopedScript script({
        observe_action(leader, -1, EINTR, 0),
        terminal_action(leader),
        signal_action(-leader, -1, ESRCH),
        reap_action(leader, -1, 0, EINTR),
        reap_action(leader, leader, expected_status),
    });
    TestProcessTopologyOwner owner(leader, leader);

    const std::optional<int> status =
        owner.try_complete_exit_or_throw("interrupted owner");
    require(status == expected_status && !owner.active(),
            "EINTR/ESRCH completion did not converge on exact reap", checks);
    require(script.event_count() == 5,
            "interrupted completion did not follow the reviewed retry trace",
            checks);
    script.require_complete();
}

void test_foreign_observation_fails_closed(std::uint64_t& checks) {
    constexpr pid_t leader = 41005;
    ScopedScript script({
        observe_action(leader, 0, 0, leader + 1),
        signal_action(-leader),
        signal_action(leader),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    require(throws_as<std::runtime_error>([&] {
                (void)owner.try_complete_exit_or_throw("foreign owner");
            }),
            "foreign WNOWAIT identity was accepted", checks);
    require(!owner.active(),
            "foreign WNOWAIT identity retained numeric authority", checks);
    script.require_complete();
}

void test_external_reap_relinquishes_without_signal(std::uint64_t& checks) {
    constexpr pid_t leader = 41006;
    ScopedScript script({
        observe_action(leader, -1, ECHILD, 0),
    });
    TestProcessTopologyOwner owner(leader, leader);

    bool exact_error = false;
    try {
        (void)owner.try_complete_exit_or_throw("externally reaped owner");
    } catch (const std::system_error& error) {
        exact_error = error.code().value() == ECHILD;
    }
    require(exact_error && !owner.active(),
            "ECHILD did not relinquish unprovable numeric authority", checks);
    require(script.event_count() == 1,
            "ECHILD path signaled after exact child ownership was lost", checks);
    script.require_complete();
}

void test_observation_error_cleans_up_owned_topology(std::uint64_t& checks) {
    constexpr pid_t leader = 41007;
    ScopedScript script({
        observe_action(leader, -1, EIO, 0),
        signal_action(-leader),
        signal_action(leader),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    bool exact_error = false;
    try {
        (void)owner.try_complete_exit_or_throw("failed observation owner");
    } catch (const std::system_error& error) {
        exact_error = error.code().value() == EIO;
    }
    require(exact_error && !owner.active(),
            "hard observation failure did not clean up owned topology", checks);
    script.require_complete();
}

void test_group_signal_error_reports_after_cleanup(std::uint64_t& checks) {
    constexpr pid_t leader = 41008;
    ScopedScript script({
        terminal_action(leader),
        signal_action(-leader, -1, EPERM),
        signal_action(-leader),
        signal_action(leader),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    bool exact_error = false;
    try {
        (void)owner.try_complete_exit_or_throw("failed group signal owner");
    } catch (const std::system_error& error) {
        exact_error = error.code().value() == EPERM;
    }
    require(exact_error && !owner.active(),
            "group-signal failure was not reported after bounded cleanup",
            checks);
    script.require_complete();
}

void test_final_echild_relinquishes_without_retry(std::uint64_t& checks) {
    constexpr pid_t leader = 41009;
    ScopedScript script({
        terminal_action(leader),
        signal_action(-leader),
        reap_action(leader, -1, 0, ECHILD),
    });
    TestProcessTopologyOwner owner(leader, leader);

    bool exact_error = false;
    try {
        (void)owner.try_complete_exit_or_throw("raced final reap owner");
    } catch (const std::system_error& error) {
        exact_error = error.code().value() == ECHILD;
    }
    require(exact_error && !owner.active(),
            "final ECHILD retained numeric authority", checks);
    require(script.event_count() == 3,
            "final ECHILD retried a signal after ownership was lost", checks);
    script.require_complete();
}

void test_impossible_wait_result_fails_closed(std::uint64_t& checks) {
    constexpr pid_t leader = 41010;
    ScopedScript script({
        terminal_action(leader),
        signal_action(-leader),
        reap_action(leader, 0),
        signal_action(-leader),
        signal_action(leader),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    require(throws_as<std::runtime_error>([&] {
                (void)owner.try_complete_exit_or_throw(
                    "impossible final wait owner");
            }),
            "blocking waitpid zero result was accepted", checks);
    require(!owner.active(),
            "impossible wait result retained numeric authority", checks);
    script.require_complete();
}

void test_throwing_cleanup_consumes_before_syscalls(std::uint64_t& checks) {
    constexpr pid_t leader = 41011;
    ScopedScript script({
        signal_action(-leader, -1, EPERM),
        signal_action(leader, -1, ESRCH),
        reap_action(leader, -1, 0, EINTR),
        reap_action(leader, leader, SIGKILL),
    });
    TestProcessTopologyOwner owner(leader, leader);

    bool exact_error = false;
    try {
        owner.terminate_and_reap_or_throw("throwing cleanup owner");
    } catch (const std::system_error& error) {
        exact_error = error.code().value() == EPERM;
    }
    require(exact_error && !owner.active(),
            "throwing cleanup did not consume authority before reporting",
            checks);
    const std::size_t completed_events = script.event_count();
    owner.terminate_and_reap_noexcept();
    require(script.event_count() == completed_events,
            "cleanup retry reused numeric authority after reported failure",
            checks);
    script.require_complete();
}

void test_move_transfers_one_topology(std::uint64_t& checks) {
    constexpr pid_t displaced = 41012;
    constexpr pid_t transferred = 41013;
    ScopedScript script({
        signal_action(-displaced),
        signal_action(displaced),
        reap_action(displaced, displaced, SIGKILL),
        signal_action(-transferred),
        signal_action(transferred),
        reap_action(transferred, transferred, SIGKILL),
    });
    TestProcessTopologyOwner destination(displaced, displaced);
    TestProcessTopologyOwner source(transferred, transferred);

    destination = std::move(source);
    require(destination.active() &&
                destination.leader_process_id() == transferred &&
                !source.active(),
            "move assignment duplicated or lost topology authority", checks);
    destination.terminate_and_reap_noexcept();
    require(!destination.active(),
            "moved topology did not terminate exactly once", checks);
    script.require_complete();
}

}  // namespace

extern "C" int __wrap_kill(pid_t identity, int signal_number) {
    if (!script_state.armed) return __real_kill(identity, signal_number);
    const std::optional<Action> action =
        consume_action_noexcept(Operation::signal, identity, signal_number);
    if (!action.has_value()) return -1;
    if (action->result < 0) errno = action->error;
    return static_cast<int>(action->result);
}

extern "C" int __wrap_waitid(idtype_t type, id_t identity,
                              siginfo_t* information, int flags) {
    if (!script_state.armed) {
        return __real_waitid(type, identity, information, flags);
    }
    if (type != P_PID || information == nullptr) {
        note_mismatch_noexcept("waitid did not use one exact P_PID identity");
        return -1;
    }
    const std::optional<Action> action = consume_action_noexcept(
        Operation::observe, static_cast<pid_t>(identity), flags);
    if (!action.has_value()) return -1;
    if (action->result < 0) {
        errno = action->error;
        return -1;
    }
    std::memset(information, 0, sizeof(*information));
    information->si_pid = action->observed_identity;
    return static_cast<int>(action->result);
}

extern "C" pid_t __wrap_waitpid(pid_t identity, int* status, int flags) {
    if (!script_state.armed) return __real_waitpid(identity, status, flags);
    if (status == nullptr) {
        note_mismatch_noexcept("waitpid omitted its exact status destination");
        return -1;
    }
    const std::optional<Action> action =
        consume_action_noexcept(Operation::reap, identity, flags);
    if (!action.has_value()) return -1;
    if (action->result < 0) {
        errno = action->error;
        return -1;
    }
    *status = action->wait_status;
    return static_cast<pid_t>(action->result);
}

int main() {
    std::uint64_t checks = 0;
    try {
        test_pending_observation_preserves_authority(checks);
        test_exact_completion_consumes_before_return(checks);
        test_no_group_completion_has_no_group_signal(checks);
        test_interrupted_syscalls_retry_exactly(checks);
        test_foreign_observation_fails_closed(checks);
        test_external_reap_relinquishes_without_signal(checks);
        test_observation_error_cleans_up_owned_topology(checks);
        test_group_signal_error_reports_after_cleanup(checks);
        test_final_echild_relinquishes_without_retry(checks);
        test_impossible_wait_result_fails_closed(checks);
        test_throwing_cleanup_consumes_before_syscalls(checks);
        test_move_transfers_one_topology(checks);
        std::cout << "anonsync_test_process_topology_owner_test checks="
                  << checks << " failures=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync_test_process_topology_owner_test checks="
                  << checks << " failures=1 reason=" << error.what() << "\n";
        return 1;
    }
}
