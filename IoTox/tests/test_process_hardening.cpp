#include "test_harness.hpp"

#include "iotox/security/process_hardening.hpp"

#include <cerrno>
#include <csignal>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

IOTOX_TEST("remote terminal host process sealing is idempotent and child-local") {
#if defined(PR_SET_DUMPABLE) && defined(PR_GET_DUMPABLE)
    const int parent_dumpable = ::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0);
    IOTOX_CHECK(parent_dumpable >= 0);
    struct rlimit parent_core {};
    IOTOX_CHECK(::getrlimit(RLIMIT_CORE, &parent_core) == 0);

    const pid_t child = ::fork();
    IOTOX_CHECK(child >= 0);
    if (child == 0) {
        const iotox::Status first =
            iotox::security::seal_remote_terminal_host_process();
        const iotox::Status second =
            iotox::security::seal_remote_terminal_host_process();
        struct rlimit core {};
        const bool sealed = first.ok() && second.ok() &&
                            ::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0) == 0 &&
                            ::getrlimit(RLIMIT_CORE, &core) == 0 &&
                            core.rlim_cur == 0 && core.rlim_max == 0;
        _exit(sealed ? 0 : 1);
    }

    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(child, &status, 0);
    } while (waited < 0 && errno == EINTR);
    IOTOX_CHECK(waited == child);
    IOTOX_CHECK(WIFEXITED(status));
    IOTOX_CHECK(WEXITSTATUS(status) == 0);
    IOTOX_CHECK(::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0) == parent_dumpable);
    struct rlimit verified_parent_core {};
    IOTOX_CHECK(::getrlimit(RLIMIT_CORE, &verified_parent_core) == 0);
    IOTOX_CHECK(verified_parent_core.rlim_cur == parent_core.rlim_cur);
    IOTOX_CHECK(verified_parent_core.rlim_max == parent_core.rlim_max);
#else
    IOTOX_CHECK(
        iotox::security::seal_remote_terminal_host_process().code() ==
        iotox::ErrorCode::unsupported);
#endif
}
