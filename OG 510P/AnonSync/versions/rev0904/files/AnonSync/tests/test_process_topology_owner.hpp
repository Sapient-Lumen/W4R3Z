#pragma once

#include <optional>
#include <string_view>

#include <sys/types.h>

namespace anonsync::test::detail {

// Test-only authority owner for one exact child leader and, when positive, the
// top-level process group whose identifier is that leader's PID. Numeric
// process and group identifiers are usable only while this object retains the
// corresponding authority. Every terminal transition consumes both together.
//
// try_complete_exit_or_throw() keeps terminal observation and completion in
// one owner: waitid(..., WNOWAIT) first proves the exact leader is waitable;
// the still-pinned process group is then signaled; and the exact leader is
// reaped. Both numeric identifiers are cleared before a completed status is
// returned, so later output-drain failures cannot signal a stale group number.
class TestProcessTopologyOwner final {
public:
    TestProcessTopologyOwner() noexcept = default;
    TestProcessTopologyOwner(pid_t leader, pid_t process_group) noexcept;

    TestProcessTopologyOwner(const TestProcessTopologyOwner&) = delete;
    TestProcessTopologyOwner& operator=(const TestProcessTopologyOwner&) = delete;

    TestProcessTopologyOwner(TestProcessTopologyOwner&& other) noexcept;
    TestProcessTopologyOwner& operator=(
        TestProcessTopologyOwner&& other) noexcept;

    ~TestProcessTopologyOwner();

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] pid_t leader_process_id() const noexcept;

    // Returns nullopt while the exact leader is still running. A returned wait
    // status proves that WNOWAIT observed the exact leader, surviving members
    // of its owned process group were signaled, and the exact leader was reaped.
    [[nodiscard]] std::optional<int> try_complete_exit_or_throw(
        std::string_view label);

    // Destructive cleanup consumes numeric authority before the first syscall.
    // This prevents any later exception path from retrying with stale PID/PGID
    // values. The throwing form reports the first cleanup failure after making
    // a bounded best effort to signal and reap the exact leader.
    void terminate_and_reap_or_throw(std::string_view label);
    void terminate_and_reap_noexcept() noexcept;

private:
    void relinquish_numeric_authority_noexcept() noexcept;

    pid_t leader_ = -1;
    pid_t process_group_ = -1;
};

}  // namespace anonsync::test::detail
