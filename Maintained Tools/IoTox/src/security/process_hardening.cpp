#include "iotox/security/process_hardening.hpp"

#include <cerrno>
#include <cstring>
#include <string>
#include <string_view>
#include <sys/prctl.h>
#include <sys/resource.h>

namespace iotox::security {
namespace {

[[nodiscard]] Status errno_status(
    ErrorCode code, std::string_view operation, int error_number = errno) {
    return Status{
        code, std::string(operation) + ": " + std::strerror(error_number)};
}

}  // namespace

Status seal_remote_terminal_host_process() {
#if defined(PR_SET_DUMPABLE) && defined(PR_GET_DUMPABLE)
    if (::prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "make remote-terminal host process non-dumpable");
    }
    const int dumpable = ::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0);
    if (dumpable < 0) {
        return errno_status(
            ErrorCode::io_error,
            "verify remote-terminal host dumpability seal");
    }
    if (dumpable != 0) {
        return Status{
            ErrorCode::unavailable,
            "remote-terminal host dumpability seal did not remain active"};
    }

    struct rlimit core_limit {};
    core_limit.rlim_cur = 0;
    core_limit.rlim_max = 0;
    if (::setrlimit(RLIMIT_CORE, &core_limit) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "disable remote-terminal host core dumps");
    }
    struct rlimit verified {};
    if (::getrlimit(RLIMIT_CORE, &verified) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "verify remote-terminal host core-dump limit");
    }
    if (verified.rlim_cur != 0 || verified.rlim_max != 0) {
        return Status{
            ErrorCode::unavailable,
            "remote-terminal host core-dump limit did not remain sealed"};
    }
    return Status::success();
#else
    return Status{
        ErrorCode::unsupported,
        "remote-terminal host process sealing is unavailable"};
#endif
}

}  // namespace iotox::security
