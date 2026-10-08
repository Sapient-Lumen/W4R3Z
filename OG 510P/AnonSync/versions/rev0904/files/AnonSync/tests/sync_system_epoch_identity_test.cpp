#include "sync_system_epoch_identity.hpp"

#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
            return;
        }
        std::cerr << "FAIL: " << label << '\n';
    }

    [[nodiscard]] int finish() const {
        std::cout << "sync system epoch identity: " << passed_ << "/"
                  << total_ << " checks passed\n";
        return passed_ == total_ ? EXIT_SUCCESS : EXIT_FAILURE;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

template <typename Function>
[[nodiscard]] bool throws_with(Function&& function,
                               const std::string& needle) {
    try {
        std::forward<Function>(function)();
    } catch (const std::exception& error) {
        return std::string(error.what()).find(needle) != std::string::npos;
    }
    return false;
}

constexpr const char* kBootId = "01234567-89ab-cdef-0123-456789abcdef";

void exercise_probe_classifier(TestState& state) {
    using anonsync::SyncSystemBootIdentityProbeDisposition;
    using anonsync::sync_system_classify_boot_identity_open_result;

    state.check(sync_system_classify_boot_identity_open_result(7, EIO) ==
                    SyncSystemBootIdentityProbeDisposition::Available,
                "successful descriptor is available regardless of stale errno");
    state.check(sync_system_classify_boot_identity_open_result(-1, ENOENT) ==
                    SyncSystemBootIdentityProbeDisposition::Missing,
                "ENOENT is a typed missing boot source");
    state.check(sync_system_classify_boot_identity_open_result(-1, EACCES) ==
                    SyncSystemBootIdentityProbeDisposition::PermissionDenied,
                "EACCES is typed permission-hidden evidence");
    state.check(sync_system_classify_boot_identity_open_result(-1, EPERM) ==
                    SyncSystemBootIdentityProbeDisposition::PermissionDenied,
                "EPERM is typed permission-hidden evidence");
    state.check(sync_system_classify_boot_identity_open_result(-1, EIO) ==
                    SyncSystemBootIdentityProbeDisposition::Fatal,
                "unexpected boot source failure is fatal");
    state.check(sync_system_classify_boot_identity_open_result(-1, ELOOP) ==
                    SyncSystemBootIdentityProbeDisposition::Fatal,
                "symlinked boot source cannot silently downgrade authority");
}

void exercise_boot_text_parser(TestState& state) {
    using anonsync::sync_system_boot_id_is_canonical;
    using anonsync::sync_system_parse_boot_id_text_or_throw;

    state.check(sync_system_boot_id_is_canonical(kBootId),
                "lowercase UUID is canonical");
    state.check(!sync_system_boot_id_is_canonical(
                    "01234567-89AB-cdef-0123-456789abcdef"),
                "uppercase UUID is not canonical");
    state.check(!sync_system_boot_id_is_canonical(
                    "0123456789ab-cdef-0123-456789abcdef"),
                "misplaced separator is not canonical");
    state.check(sync_system_parse_boot_id_text_or_throw(kBootId) == kBootId,
                "unframed canonical UUID parses exactly");
    state.check(sync_system_parse_boot_id_text_or_throw(
                    std::string(kBootId) + "\n") == kBootId,
                "one LF terminator parses exactly");
    state.check(sync_system_parse_boot_id_text_or_throw(
                    std::string(kBootId) + "\r\n") == kBootId,
                "one CRLF terminator parses exactly");
    state.check(throws_with(
                    [] {
                        (void)sync_system_parse_boot_id_text_or_throw(
                            std::string(kBootId) + "\n\n", "double LF");
                    },
                    "exactly one UUID line"),
                "repeated newline is not normalized into evidence");
    state.check(throws_with(
                    [] {
                        (void)sync_system_parse_boot_id_text_or_throw(
                            std::string(" ") + kBootId, "leading space");
                    },
                    "exactly one UUID line"),
                "leading whitespace is not trimmed into evidence");
    state.check(throws_with(
                    [] {
                        std::string value(kBootId);
                        value.push_back('\0');
                        (void)sync_system_parse_boot_id_text_or_throw(
                            value, "NUL UUID");
                    },
                    "NUL"),
                "embedded NUL is rejected");
}

void exercise_names_and_validation(TestState& state) {
    using anonsync::SyncSystemBootIdentityKind;
    using anonsync::SyncSystemBootIdentityObservation;
    using anonsync::sync_system_boot_identity_kind_from_name_or_throw;
    using anonsync::sync_system_boot_identity_kind_name;
    using anonsync::validate_sync_system_boot_identity_observation_or_throw;

    const SyncSystemBootIdentityKind boot_kinds[] = {
        SyncSystemBootIdentityKind::Unsupported,
        SyncSystemBootIdentityKind::LinuxProcBootId,
        SyncSystemBootIdentityKind::LinuxProcBootIdMissing,
        SyncSystemBootIdentityKind::LinuxProcBootIdPermissionDenied,
    };
    for (const auto kind : boot_kinds) {
        const std::string name = sync_system_boot_identity_kind_name(kind);
        state.check(sync_system_boot_identity_kind_from_name_or_throw(
                        name, "boot source roundtrip") == kind,
                    "boot identity source name roundtrips: " + name);
    }

    validate_sync_system_boot_identity_observation_or_throw(
        {SyncSystemBootIdentityKind::LinuxProcBootId, kBootId});
    state.check(true, "concrete canonical boot observation validates");
    state.check(throws_with(
                    [&] {
                        validate_sync_system_boot_identity_observation_or_throw(
                            {SyncSystemBootIdentityKind::LinuxProcBootIdMissing,
                             kBootId},
                            "missing observation");
                    },
                    "residue"),
                "unavailable boot source cannot carry identity residue");
    state.check(throws_with(
                    [] {
                        (void)sync_system_boot_identity_kind_from_name_or_throw(
                            "future-unreviewed-source", "unknown source");
                    },
                    "unknown"),
                "unknown boot source fails closed");
}

void exercise_live_observation(TestState& state) {
    using anonsync::SyncSystemBootIdentityKind;
    using anonsync::observe_sync_system_boot_identity_or_throw;
    using anonsync::sync_system_boot_id_is_canonical;
    using anonsync::validate_sync_system_boot_identity_observation_or_throw;

    const auto first = observe_sync_system_boot_identity_or_throw(
        "first live boot observation");
    const auto second = observe_sync_system_boot_identity_or_throw(
        "second live boot observation");
    validate_sync_system_boot_identity_observation_or_throw(first);
    state.check(true, "live boot observation is typed and valid");
    state.check(first == second,
                "two immediate live observations identify one system epoch");
#if defined(__linux__)
    state.check(first.kind == SyncSystemBootIdentityKind::LinuxProcBootId ||
                    first.kind ==
                        SyncSystemBootIdentityKind::LinuxProcBootIdMissing ||
                    first.kind == SyncSystemBootIdentityKind::
                                      LinuxProcBootIdPermissionDenied,
                "Linux reports concrete, missing, or permission-hidden boot evidence");
    state.check(first.kind != SyncSystemBootIdentityKind::LinuxProcBootId ||
                    sync_system_boot_id_is_canonical(first.boot_id),
                "available Linux boot UUID is canonical");
#else
    state.check(first.kind == SyncSystemBootIdentityKind::Unsupported,
                "non-Linux boot observation is explicitly unsupported");
#endif
}

}  // namespace

int main() {
    TestState state;
    try {
        exercise_probe_classifier(state);
        exercise_boot_text_parser(state);
        exercise_names_and_validation(state);
        exercise_live_observation(state);
    } catch (const std::exception& error) {
        std::cerr << "unexpected exception: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
    return state.finish();
}
