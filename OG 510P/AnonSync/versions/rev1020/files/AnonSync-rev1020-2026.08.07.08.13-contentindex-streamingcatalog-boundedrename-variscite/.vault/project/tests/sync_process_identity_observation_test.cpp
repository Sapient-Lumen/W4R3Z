#include "sync_process_identity_observation.hpp"
#include "sync_process_identity_observation_internal.hpp"

#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using anonsync::SyncProcessIdentityMatchKind;
using anonsync::SyncProcessIdentityObservation;
using anonsync::check_sync_process_identity_observation_noexcept;
using anonsync::current_sync_process_identity_observation_or_throw;
using anonsync::validate_sync_process_identity_observation_or_throw;

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

bool rejects(const SyncProcessIdentityObservation& observation,
             std::string_view fragment) {
    try {
        validate_sync_process_identity_observation_or_throw(observation);
        return false;
    } catch (const std::exception& error) {
        return std::string_view(error.what()).find(fragment) !=
               std::string_view::npos;
    }
}

void test_pure_linux_stat_parser(TestState& test) {
    const std::string stat =
        "123 (worker ) name) S "
        "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 987654 20 21\n";
    const anonsync::detail::LinuxProcStatIdentity parsed =
        anonsync::detail::parse_linux_proc_pid_stat_identity_or_throw(stat, 123);
    test.require(parsed.process_id == 123 && parsed.state == 'S' &&
                     parsed.starttime_ticks == 987654,
                 "Linux stat parser uses the final comm delimiter and exact field 22");

    bool wrong_pid = false;
    try {
        (void)anonsync::detail::parse_linux_proc_pid_stat_identity_or_throw(
            stat, 124);
    } catch (const std::exception& error) {
        wrong_pid = std::string_view(error.what()).find("does not match") !=
                    std::string_view::npos;
    }
    test.require(wrong_pid,
                 "Linux stat parser binds field 1 to the requested PID");

    bool short_record = false;
    try {
        (void)anonsync::detail::parse_linux_proc_pid_stat_identity_or_throw(
            "123 (x) S 1 2 3", 123);
    } catch (const std::exception& error) {
        short_record = std::string_view(error.what()).find("before starttime") !=
                       std::string_view::npos;
    }
    test.require(short_record,
                 "Linux stat parser rejects records ending before field 22");
}

void test_canonical_validation(TestState& test) {
    SyncProcessIdentityObservation linux{
        "linux-proc-starttime-v1",
        41,
        "01234567-89ab-cdef-0123-456789abcdef",
        "987654",
    };
    validate_sync_process_identity_observation_or_throw(linux);
    test.require(true, "canonical Linux observation validates");

    SyncProcessIdentityObservation uppercase = linux;
    uppercase.boot_id[0] = 'A';
    test.require(rejects(uppercase, "canonical lowercase UUID"),
                 "uppercase Linux boot IDs are rejected");

    SyncProcessIdentityObservation leading_zero = linux;
    leading_zero.start_token = "0987654";
    test.require(rejects(leading_zero, "canonical positive decimal"),
                 "ambiguous decimal start tokens are rejected");

    SyncProcessIdentityObservation zero_pid = linux;
    zero_pid.process_id = 0;
    test.require(rejects(zero_pid, "supported range"),
                 "zero Linux PIDs are rejected");

    SyncProcessIdentityObservation unavailable{
        "process-incarnation-unavailable-v1", 0, "", ""};
    validate_sync_process_identity_observation_or_throw(unavailable);
    test.require(true, "unavailable platform state is explicit and residue-free");

    unavailable.process_id = 1;
    test.require(rejects(unavailable, "must not contain identity residue"),
                 "unavailable observations cannot smuggle PID-only evidence");
}

void test_live_observation(TestState& test) {
    const SyncProcessIdentityObservation current =
        current_sync_process_identity_observation_or_throw();
    validate_sync_process_identity_observation_or_throw(current);
    test.require(!current.format.empty(),
                 "current process observation has an explicit format");

#if defined(__linux__)
    test.require(current.format == "linux-proc-starttime-v1" &&
                     current.process_id != 0 && !current.boot_id.empty() &&
                     !current.start_token.empty(),
                 "Linux current observation binds PID, boot UUID, and starttime");
    const auto exact =
        check_sync_process_identity_observation_noexcept(current);
    test.require(exact.kind == SyncProcessIdentityMatchKind::Match &&
                     exact.verification_available && exact.process_live &&
                     exact.exact_match,
                 "current Linux process re-observes as one exact live incarnation");

    SyncProcessIdentityObservation different_start = current;
    different_start.start_token =
        different_start.start_token == "1" ? "2" : "1";
    const auto mismatch =
        check_sync_process_identity_observation_noexcept(different_start);
    test.require(mismatch.kind == SyncProcessIdentityMatchKind::Mismatch &&
                     mismatch.verification_available && mismatch.process_live &&
                     !mismatch.exact_match,
                 "same Linux PID with a different starttime is PID reuse evidence");

    SyncProcessIdentityObservation different_boot = current;
    different_boot.boot_id[0] = different_boot.boot_id[0] == '0' ? '1' : '0';
    const auto reboot =
        check_sync_process_identity_observation_noexcept(different_boot);
    test.require(reboot.kind == SyncProcessIdentityMatchKind::Mismatch &&
                     reboot.process_live && !reboot.exact_match,
                 "same Linux PID with a different boot UUID is reboot evidence");
#else
    test.require(current.format == "windows-creation-filetime-v1" ||
                     current.format == "process-incarnation-unavailable-v1",
                 "non-Linux current observation is explicit");
#endif
}

void test_invalid_check_is_typed(TestState& test) {
    const SyncProcessIdentityObservation invalid{
        "linux-proc-starttime-v1", 0, "", ""};
    const auto result =
        check_sync_process_identity_observation_noexcept(invalid);
    test.require(result.kind == SyncProcessIdentityMatchKind::Invalid &&
                     !result.exact_match && !result.reason.empty(),
                 "invalid document evidence returns a typed nonthrowing result");
}

}  // namespace

int main() {
    TestState test;
    try {
        test_pure_linux_stat_parser(test);
        test_canonical_validation(test);
        test_live_observation(test);
        test_invalid_check_is_typed(test);
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "FAIL: unexpected exception: " << error.what() << "\n";
    }
    std::cout << "anonsync process identity observation checks=" << test.passed
              << " failed=" << test.failed << "\n";
    return test.failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
