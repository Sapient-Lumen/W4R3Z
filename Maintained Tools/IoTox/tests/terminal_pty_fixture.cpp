#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "iotox/terminal_seccomp_policy.hpp"

#include <array>
#include <atomic>
#include <cerrno>
#include <charconv>
#include <climits>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <linux/capability.h>
#include <linux/securebits.h>
#include <sched.h>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>
#include <netinet/in.h>

namespace {

[[nodiscard]] bool write_all(std::span<const std::uint8_t> bytes) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::write(
            STDOUT_FILENO, bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return false;
    }
    return true;
}

[[nodiscard]] bool write_text(std::string_view text) {
    return write_all(std::span<const std::uint8_t>{
        reinterpret_cast<const std::uint8_t *>(text.data()), text.size()});
}

[[nodiscard]] bool make_raw() {
    termios attributes {};
    if (::tcgetattr(STDIN_FILENO, &attributes) != 0) return false;
    ::cfmakeraw(&attributes);
    attributes.c_cc[VMIN] = 1;
    attributes.c_cc[VTIME] = 0;
    return ::tcsetattr(STDIN_FILENO, TCSANOW, &attributes) == 0;
}

[[nodiscard]] std::string environment_value(const char *name) {
    const char *value = ::getenv(name);
    return value != nullptr ? std::string(value) : std::string{"<unset>"};
}

[[nodiscard]] std::string signal_disposition(int signal_number) {
    struct sigaction action {};
    if (::sigaction(signal_number, nullptr, &action) != 0) return "error";
    if (action.sa_handler == SIG_DFL) return "default";
    if (action.sa_handler == SIG_IGN) return "ignored";
    return "handler";
}

[[nodiscard]] int runtime_last_capability() {
#if defined(PR_CAPBSET_READ)
    for (int capability = 0; capability <= 1024; ++capability) {
        errno = 0;
        if (::prctl(PR_CAPBSET_READ, capability, 0, 0, 0) >= 0) continue;
        if (errno == EINVAL && capability > 0) return capability - 1;
        return -1;
    }
#endif
    return -1;
}

[[nodiscard]] int ambient_capability_count() {
#if defined(PR_CAP_AMBIENT) && defined(PR_CAP_AMBIENT_IS_SET)
    const int last = runtime_last_capability();
    if (last < 0) return -1;
    int count = 0;
    for (int capability = 0; capability <= last; ++capability) {
        const int configured = ::prctl(
            PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, capability, 0, 0);
        if (configured < 0) return -1;
        count += configured;
    }
    return count;
#else
    return -1;
#endif
}

[[nodiscard]] int bounding_capability_count() {
#if defined(PR_CAPBSET_READ)
    const int last = runtime_last_capability();
    if (last < 0) return -1;
    int count = 0;
    for (int capability = 0; capability <= last; ++capability) {
        const int configured = ::prctl(PR_CAPBSET_READ, capability, 0, 0, 0);
        if (configured < 0) return -1;
        count += configured;
    }
    return count;
#else
    return -1;
#endif
}

struct CapabilityCounts {
    int effective{-1};
    int permitted{-1};
    int inheritable{-1};
};

[[nodiscard]] int count_bits(std::uint32_t value) noexcept {
    int count = 0;
    while (value != 0U) {
        value &= value - 1U;
        ++count;
    }
    return count;
}

[[nodiscard]] CapabilityCounts capability_counts() {
#if defined(SYS_capget)
    __user_cap_header_struct header{};
    header.version = _LINUX_CAPABILITY_VERSION_3;
    header.pid = 0;
    std::array<__user_cap_data_struct, _LINUX_CAPABILITY_U32S_3> words{};
    if (::syscall(SYS_capget, &header, words.data()) != 0) return {};
    CapabilityCounts counts{0, 0, 0};
    for (const auto &word : words) {
        counts.effective += count_bits(word.effective);
        counts.permitted += count_bits(word.permitted);
        counts.inheritable += count_bits(word.inheritable);
    }
    return counts;
#else
    return {};
#endif
}

[[nodiscard]] bool securebits_are_sealed() {
#if defined(PR_GET_SECUREBITS) && defined(SECBIT_NOROOT) && \
    defined(SECBIT_NOROOT_LOCKED) && defined(SECBIT_NO_SETUID_FIXUP) && \
    defined(SECBIT_NO_SETUID_FIXUP_LOCKED) && defined(SECBIT_KEEP_CAPS) && \
    defined(SECBIT_KEEP_CAPS_LOCKED) && defined(SECBIT_NO_CAP_AMBIENT_RAISE) && \
    defined(SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED)
    const int configured = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (configured < 0) return false;
    constexpr int required_set =
        SECBIT_NOROOT | SECBIT_NOROOT_LOCKED |
        SECBIT_NO_SETUID_FIXUP_LOCKED | SECBIT_KEEP_CAPS_LOCKED |
        SECBIT_NO_CAP_AMBIENT_RAISE |
        SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED;
    constexpr int required_clear =
        SECBIT_NO_SETUID_FIXUP | SECBIT_KEEP_CAPS;
    return (configured & required_set) == required_set &&
           (configured & required_clear) == 0;
#else
    return false;
#endif
}

[[nodiscard]] bool baseline_syscall_is_denied() {
#ifdef SYS_personality
    errno = 0;
    const long result = ::syscall(SYS_personality, ~0UL);
    return result < 0 && errno == EPERM;
#else
    return false;
#endif
}

struct ProcessHandleProbe {
    bool denied{true};
    unsigned int available_syscalls{0U};
};

[[nodiscard]] ProcessHandleProbe process_handle_syscalls_are_denied() {
    ProcessHandleProbe probe;
#ifdef SYS_pidfd_open
    ++probe.available_syscalls;
    errno = 0;
    const long opened = ::syscall(SYS_pidfd_open, ::getpid(), 0U);
    const int open_error = errno;
    if (opened >= 0) static_cast<void>(::close(static_cast<int>(opened)));
    probe.denied = probe.denied && opened < 0 && open_error == EPERM;
#else
    probe.denied = false;
#endif
#ifdef SYS_pidfd_send_signal
    ++probe.available_syscalls;
    errno = 0;
    const long signaled =
        ::syscall(SYS_pidfd_send_signal, -1, 0, nullptr, 0U);
    probe.denied = probe.denied && signaled < 0 && errno == EPERM;
#else
    probe.denied = false;
#endif
#ifdef SYS_process_madvise
    ++probe.available_syscalls;
    errno = 0;
    const long advised =
        ::syscall(SYS_process_madvise, -1, nullptr, 0U, 0, 0U);
    probe.denied = probe.denied && advised < 0 && errno == EPERM;
#endif
#ifdef SYS_process_mrelease
    ++probe.available_syscalls;
    errno = 0;
    const long released = ::syscall(SYS_process_mrelease, -1, 0U);
    probe.denied = probe.denied && released < 0 && errno == EPERM;
#endif
    return probe;
}

[[nodiscard]] bool ioctl_request_is_denied(unsigned long request) {
#ifdef SYS_ioctl
    char byte = 'x';
    errno = 0;
    const long result = ::syscall(SYS_ioctl, -1, request, &byte);
    return result < 0 && errno == EPERM;
#else
    static_cast<void>(request);
    return false;
#endif
}

[[nodiscard]] bool terminal_injection_ioctl_is_denied() {
#ifdef TIOCSTI
    return ioctl_request_is_denied(static_cast<unsigned long>(TIOCSTI));
#else
    return false;
#endif
}

[[nodiscard]] bool terminal_mutation_ioctl_set_is_denied() {
    bool denied = true;
    for (const std::uint32_t request :
         iotox::terminal::detail::kDeniedTerminalIoctlRequests) {
        denied = denied && ioctl_request_is_denied(request);
    }
    return denied;
}

[[nodiscard]] bool ordinary_ioctl_reaches_kernel_validation() {
#ifdef SYS_ioctl
    winsize window{};
    errno = 0;
    const long result = ::syscall(SYS_ioctl, -1, TIOCGWINSZ, &window);
    return result < 0 && errno == EBADF;
#else
    return false;
#endif
}

[[nodiscard]] long raw_clone_with_flags(unsigned long flags) {
#ifdef SYS_clone
#if defined(__s390x__)
    return ::syscall(SYS_clone, nullptr, flags, nullptr, nullptr, 0UL);
#else
    return ::syscall(SYS_clone, flags, nullptr, nullptr, nullptr, 0UL);
#endif
#else
    static_cast<void>(flags);
    errno = ENOSYS;
    return -1;
#endif
}

[[nodiscard]] bool namespace_clone_is_argument_denied() {
#if defined(SYS_clone) && defined(CLONE_FS)
    unsigned long namespace_flag = 0UL;
#ifdef CLONE_NEWUSER
    namespace_flag = static_cast<unsigned long>(CLONE_NEWUSER);
#elif defined(CLONE_NEWNS)
    namespace_flag = static_cast<unsigned long>(CLONE_NEWNS);
#else
    return false;
#endif
    // CLONE_FS is incompatible with both selected namespace flags. Without
    // the seccomp argument fence the kernel rejects this shape with EINVAL;
    // EPERM therefore proves that the filter inspected the clone flag word.
    errno = 0;
    const long result = raw_clone_with_flags(
        namespace_flag | static_cast<unsigned long>(CLONE_FS) |
        static_cast<unsigned long>(SIGCHLD));
    if (result == 0) _exit(126);
    if (result > 0) {
        static_cast<void>(::kill(static_cast<pid_t>(result), SIGKILL));
        int status = 0;
        while (::waitpid(static_cast<pid_t>(result), &status, 0) < 0 &&
               errno == EINTR) {
        }
        return false;
    }
    return errno == EPERM;
#else
    return false;
#endif
}

[[nodiscard]] bool ordinary_clone_reaches_kernel_validation() {
#if defined(SYS_clone) && defined(CLONE_SIGHAND)
    // CLONE_SIGHAND without CLONE_VM is invalid but contains no namespace
    // creation bit, so EINVAL proves ordinary process/thread creation reaches
    // the kernel rather than being denied wholesale.
    errno = 0;
    const long result = raw_clone_with_flags(
        static_cast<unsigned long>(CLONE_SIGHAND) |
        static_cast<unsigned long>(SIGCHLD));
    if (result == 0) _exit(127);
    if (result > 0) {
        static_cast<void>(::kill(static_cast<pid_t>(result), SIGKILL));
        int status = 0;
        while (::waitpid(static_cast<pid_t>(result), &status, 0) < 0 &&
               errno == EINTR) {
        }
        return false;
    }
    return errno == EINVAL;
#else
    return false;
#endif
}

[[nodiscard]] bool clone3_requests_legacy_fallback() {
#ifdef SYS_clone3
    errno = 0;
    const long result = ::syscall(SYS_clone3, nullptr, 0U);
    return result < 0 && errno == ENOSYS;
#else
    return false;
#endif
}

[[nodiscard]] bool thread_creation_survives_clone3_fallback() {
    std::atomic<bool> ran{false};
    try {
        std::thread worker([&ran]() { ran.store(true); });
        worker.join();
    } catch (...) {
        return false;
    }
    return ran.load();
}

[[nodiscard]] std::string report() {
    std::array<char, PATH_MAX> cwd{};
    const char *directory = ::getcwd(cwd.data(), cwd.size());
    winsize window {};
    const bool window_ok = ::ioctl(STDIN_FILENO, TIOCGWINSZ, &window) == 0;
    struct rlimit core {};
    const bool core_ok = ::getrlimit(RLIMIT_CORE, &core) == 0;
    struct rlimit open_files {};
    const bool open_files_ok = ::getrlimit(RLIMIT_NOFILE, &open_files) == 0;
    const int no_new_privileges = ::prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0);
    const int seccomp_mode = ::prctl(PR_GET_SECCOMP, 0, 0, 0, 0);
    const int dumpable = ::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0);
#ifdef PR_GET_MDWE
    const int mdwe = ::prctl(PR_GET_MDWE, 0, 0, 0, 0);
#else
    const int mdwe = -1;
#endif
    const CapabilityCounts capabilities = capability_counts();
    const ProcessHandleProbe process_handles =
        process_handle_syscalls_are_denied();
    int parent_death_signal = 0;
    const bool parent_death_ok =
        ::prctl(PR_GET_PDEATHSIG, &parent_death_signal, 0, 0, 0) == 0;
    const pid_t process = ::getpid();
    const pid_t session = ::getsid(0);
    const pid_t group = ::getpgrp();
    const pid_t foreground = ::tcgetpgrp(STDIN_FILENO);

    std::string text;
    text += "cwd=" + std::string(directory != nullptr ? directory : "<error>") + "\n";
    text += "TERM=" + environment_value("TERM") + "\n";
    text += "ALPHA=" + environment_value("ALPHA") + "\n";
    text += "PATH=" + environment_value("PATH") + "\n";
    text += "LD_PRELOAD=" + environment_value("LD_PRELOAD") + "\n";
    text += "IOTOX_INTERNAL_TERMINAL_CHILD=" +
            environment_value("IOTOX_INTERNAL_TERMINAL_CHILD") + "\n";
    text += "winsize=" + std::to_string(window_ok ? window.ws_col : 0U) + "x" +
            std::to_string(window_ok ? window.ws_row : 0U) + "\n";
    text += "no-new-privs=" + std::to_string(no_new_privileges) + "\n";
    text += "ambient-capabilities=" +
            std::to_string(ambient_capability_count()) + "\n";
    text += "effective-capabilities=" +
            std::to_string(capabilities.effective) + "\n";
    text += "permitted-capabilities=" +
            std::to_string(capabilities.permitted) + "\n";
    text += "inheritable-capabilities=" +
            std::to_string(capabilities.inheritable) + "\n";
    text += "bounding-capabilities=" +
            std::to_string(bounding_capability_count()) + "\n";
    text += "securebits-sealed=" +
            std::to_string(securebits_are_sealed() ? 1 : 0) + "\n";
    text += "seccomp-mode=" + std::to_string(seccomp_mode) + "\n";
    text += "baseline-syscall-denied=" +
            std::to_string(baseline_syscall_is_denied() ? 1 : 0) + "\n";
    text += "process-handle-syscalls-denied=" +
            std::to_string(process_handles.denied ? 1 : 0) + "\n";
    text += "process-handle-syscall-count=" +
            std::to_string(process_handles.available_syscalls) + "\n";
    text += "terminal-injection-ioctl-denied=" +
            std::to_string(terminal_injection_ioctl_is_denied() ? 1 : 0) +
            "\n";
    text += "terminal-mutation-ioctl-set-denied=" +
            std::to_string(terminal_mutation_ioctl_set_is_denied() ? 1 : 0) +
            "\n";
    text += "terminal-mutation-ioctl-count=" +
            std::to_string(
                iotox::terminal::detail::kDeniedTerminalIoctlRequests.size()) +
            "\n";
    text += "ordinary-ioctl-kernel-validation=" +
            std::to_string(
                ordinary_ioctl_reaches_kernel_validation() ? 1 : 0) +
            "\n";
    text += "namespace-clone-argument-denied=" +
            std::to_string(namespace_clone_is_argument_denied() ? 1 : 0) +
            "\n";
    text += "ordinary-clone-kernel-validation=" +
            std::to_string(ordinary_clone_reaches_kernel_validation() ? 1 : 0) +
            "\n";
    text += "clone3-legacy-fallback=" +
            std::to_string(clone3_requests_legacy_fallback() ? 1 : 0) +
            "\n";
    text += "thread-clone-fallback-operational=" +
            std::to_string(
                thread_creation_survives_clone3_fallback() ? 1 : 0) +
            "\n";
    text += "dumpable-after-exec=" + std::to_string(dumpable) + "\n";
    text += "mdwe=" + std::to_string(mdwe) + "\n";
    text += "parent-death-signal=" +
            std::to_string(parent_death_ok ? parent_death_signal : 0) + "\n";
    text += "signal-pipe=" + signal_disposition(SIGPIPE) + "\n";
    text += "signal-xfsz=" + signal_disposition(SIGXFSZ) + "\n";
    text += "uid=" + std::to_string(static_cast<std::uint64_t>(::getuid())) + "\n";
    text += "euid=" + std::to_string(static_cast<std::uint64_t>(::geteuid())) + "\n";
    text += "gid=" + std::to_string(static_cast<std::uint64_t>(::getgid())) + "\n";
    text += "egid=" + std::to_string(static_cast<std::uint64_t>(::getegid())) + "\n";
    const int supplementary_groups = ::getgroups(0, nullptr);
    text += "supplementary-groups=" +
            std::to_string(supplementary_groups >= 0 ? supplementary_groups : -1) +
            "\n";
    text += "core-soft=" +
            std::to_string(core_ok ? static_cast<std::uint64_t>(core.rlim_cur) : 1U) +
            "\n";
    text += "core-hard=" +
            std::to_string(core_ok ? static_cast<std::uint64_t>(core.rlim_max) : 1U) +
            "\n";
    text += "nofile-soft=" +
            std::to_string(
                open_files_ok
                    ? static_cast<std::uint64_t>(open_files.rlim_cur)
                    : 0U) +
            "\n";
    text += "sid-equals-pid=" + std::to_string(session == process ? 1 : 0) + "\n";
    text += "pgrp-equals-pid=" + std::to_string(group == process ? 1 : 0) + "\n";
    text += "foreground=" + std::to_string(foreground == group ? 1 : 0) + "\n";
    for (int descriptor = 3; descriptor <= 16; ++descriptor) {
        errno = 0;
        const bool closed = ::fcntl(descriptor, F_GETFD) < 0 && errno == EBADF;
        text += "fd" + std::to_string(descriptor) + "=" +
                (closed ? "closed" : "open") + "\n";
    }
    return text;
}

[[nodiscard]] int run_echo() {
    if (!make_raw() || !write_text("READY\n")) return 74;
    std::array<std::uint8_t, 4096U> buffer{};
    while (true) {
        const ssize_t count = ::read(STDIN_FILENO, buffer.data(), buffer.size());
        if (count > 0) {
            if (!write_all(std::span<const std::uint8_t>{
                    buffer.data(), static_cast<std::size_t>(count)})) {
                return 74;
            }
            continue;
        }
        if (count == 0) return 0;
        if (errno == EINTR) continue;
        return 74;
    }
}

[[nodiscard]] int run_ignore() {
    if (::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
        ::signal(SIGTERM, SIG_IGN) == SIG_ERR ||
        !make_raw() || !write_text("READY\n")) {
        return 74;
    }
    std::array<std::uint8_t, 64U> buffer{};
    while (true) {
        const ssize_t count = ::read(STDIN_FILENO, buffer.data(), buffer.size());
        if (count > 0) continue;
        if (count == 0) return 0;
        if (errno == EINTR) continue;
        return 74;
    }
}

[[nodiscard]] bool ordinary_fork_succeeds() {
    const pid_t child = ::fork();
    if (child < 0) return false;
    if (child == 0) _exit(0);
    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(child, &status, 0);
    } while (waited < 0 && errno == EINTR);
    return waited == child && WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

[[nodiscard]] bool descendant_setsid_is_denied() {
#ifdef SYS_setsid
    const pid_t child = ::fork();
    if (child < 0) return false;
    if (child == 0) {
        errno = 0;
        const long result = ::syscall(SYS_setsid);
        _exit(result < 0 && errno == EPERM ? 0 : 1);
    }
    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(child, &status, 0);
    } while (waited < 0 && errno == EINTR);
    return waited == child && WIFEXITED(status) && WEXITSTATUS(status) == 0;
#else
    return false;
#endif
}

[[nodiscard]] bool terminal_detach_is_denied() {
#if defined(SYS_ioctl) && defined(TIOCNOTTY)
    errno = 0;
    const long result = ::syscall(SYS_ioctl, STDIN_FILENO, TIOCNOTTY, 0UL);
    return result < 0 && errno == EPERM;
#else
    return false;
#endif
}

[[nodiscard]] bool parent_death_change_is_denied() {
#if defined(PR_GET_PDEATHSIG) && defined(PR_SET_PDEATHSIG)
    int before = 0;
    if (::prctl(PR_GET_PDEATHSIG, &before, 0, 0, 0) != 0 ||
        before != SIGKILL) {
        return false;
    }
    errno = 0;
    const int changed = ::prctl(PR_SET_PDEATHSIG, 0, 0, 0, 0);
    const int change_error = errno;
    int after = 0;
    return changed < 0 && change_error == EPERM &&
           ::prctl(PR_GET_PDEATHSIG, &after, 0, 0, 0) == 0 &&
           after == SIGKILL;
#else
    return false;
#endif
}

[[nodiscard]] int run_baseline_fence_probe() {
    const bool ordinary_fork = ordinary_fork_succeeds();
    const bool ordinary_thread = thread_creation_survives_clone3_fallback();
    const bool namespace_clone = namespace_clone_is_argument_denied();
    const bool clone3 = clone3_requests_legacy_fallback();
    const bool setsid_denied = descendant_setsid_is_denied();
    const bool detach_denied = terminal_detach_is_denied();
    const bool parent_death_denied = parent_death_change_is_denied();
    const ProcessHandleProbe process_handles =
        process_handle_syscalls_are_denied();

    std::string text;
    text += "ordinary-fork-allowed=" +
            std::to_string(ordinary_fork ? 1 : 0) + "\n";
    text += "ordinary-thread-allowed=" +
            std::to_string(ordinary_thread ? 1 : 0) + "\n";
    text += "namespace-clone-denied=" +
            std::to_string(namespace_clone ? 1 : 0) + "\n";
    text += "clone3-unavailable=" + std::to_string(clone3 ? 1 : 0) + "\n";
    text += "descendant-setsid-denied=" +
            std::to_string(setsid_denied ? 1 : 0) + "\n";
    text += "terminal-detach-denied=" +
            std::to_string(detach_denied ? 1 : 0) + "\n";
    text += "parent-death-change-denied=" +
            std::to_string(parent_death_denied ? 1 : 0) + "\n";
    text += "process-handle-syscalls-denied=" +
            std::to_string(process_handles.denied ? 1 : 0) + "\n";
    text += "process-handle-syscall-count=" +
            std::to_string(process_handles.available_syscalls) + "\n";
    if (!write_text(text)) return 74;
    return ordinary_fork && ordinary_thread && namespace_clone && clone3 &&
                   setsid_denied && detach_denied && parent_death_denied &&
                   process_handles.denied &&
                   process_handles.available_syscalls >= 2U
               ? 0
               : 70;
}

[[nodiscard]] int run_fd_probe(std::string_view descriptor_text) {
    int descriptor = -1;
    const auto parsed = std::from_chars(
        descriptor_text.data(), descriptor_text.data() + descriptor_text.size(),
        descriptor);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != descriptor_text.data() + descriptor_text.size() ||
        descriptor < 0) {
        return 64;
    }
    errno = 0;
    const bool closed = ::fcntl(descriptor, F_GETFD) < 0 && errno == EBADF;
    const std::string text =
        "inherited-high-fd-closed=" + std::to_string(closed ? 1 : 0) + "\n";
    if (!write_text(text)) return 74;
    return closed ? 0 : 70;
}

[[nodiscard]] bool configure_session_descendant() {
    return ::setpgid(0, 0) == 0 &&
           ::signal(SIGHUP, SIG_IGN) != SIG_ERR &&
           ::signal(SIGTERM, SIG_IGN) != SIG_ERR;
}

[[nodiscard]] int run_session_tree(bool natural_leader_exit) {
    int readiness[2]{-1, -1};
    if (::pipe2(readiness, O_CLOEXEC) != 0) return 74;
    const pid_t child = ::fork();
    if (child < 0) {
        static_cast<void>(::close(readiness[0]));
        static_cast<void>(::close(readiness[1]));
        return 74;
    }
    if (child == 0) {
        static_cast<void>(::close(readiness[0]));
        const bool configured = configure_session_descendant();
        const std::uint8_t ready = configured ? 1U : 0U;
        const ssize_t written = ::write(readiness[1], &ready, sizeof(ready));
        static_cast<void>(::close(readiness[1]));
        if (!configured || written != static_cast<ssize_t>(sizeof(ready))) {
            _exit(70);
        }
        while (true) {
            errno = 0;
            if (::pause() < 0 && errno == EINTR) continue;
            _exit(74);
        }
    }

    static_cast<void>(::close(readiness[1]));
    std::uint8_t ready = 0U;
    ssize_t count = -1;
    do {
        count = ::read(readiness[0], &ready, sizeof(ready));
    } while (count < 0 && errno == EINTR);
    static_cast<void>(::close(readiness[0]));
    const bool separate =
        count == static_cast<ssize_t>(sizeof(ready)) && ready == 1U &&
        ::getpgid(child) == child;
    if (!separate) {
        static_cast<void>(::kill(child, SIGKILL));
        int status = 0;
        while (::waitpid(child, &status, 0) < 0 && errno == EINTR) {
        }
        return 70;
    }

    if (!natural_leader_exit &&
        (::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
         ::signal(SIGTERM, SIG_IGN) == SIG_ERR)) {
        static_cast<void>(::kill(child, SIGKILL));
        return 74;
    }
    std::string text;
    text += "leader-pid=" +
            std::to_string(static_cast<std::uint64_t>(::getpid())) + "\n";
    text += "child-pid=" +
            std::to_string(static_cast<std::uint64_t>(child)) + "\n";
    text += "child-separate-pgrp=1\nREADY\n";
    if (!write_text(text)) {
        static_cast<void>(::kill(child, SIGKILL));
        return 74;
    }
    if (natural_leader_exit) return 0;
    while (true) {
        errno = 0;
        if (::pause() < 0 && errno == EINTR) continue;
        return 74;
    }
}

[[nodiscard]] bool append_process_id(int descriptor, pid_t process) {
    const std::string record =
        std::to_string(static_cast<std::uint64_t>(process)) + "\n";
    std::size_t offset = 0U;
    while (offset < record.size()) {
        const ssize_t written = ::write(
            descriptor, record.data() + offset, record.size() - offset);
        if (written > 0) {
            offset += static_cast<std::size_t>(written);
            continue;
        }
        if (written < 0 && errno == EINTR) continue;
        return false;
    }
    return true;
}

[[nodiscard]] int run_session_fork_churn(std::string_view record_path) {
    const int records = ::open(
        std::string(record_path).c_str(),
        O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC,
        static_cast<mode_t>(0600));
    if (records < 0) return 74;
    int readiness[2]{-1, -1};
    if (::pipe2(readiness, O_CLOEXEC) != 0) {
        static_cast<void>(::close(records));
        return 74;
    }
    const pid_t churner = ::fork();
    if (churner < 0) {
        static_cast<void>(::close(records));
        static_cast<void>(::close(readiness[0]));
        static_cast<void>(::close(readiness[1]));
        return 74;
    }
    if (churner == 0) {
        static_cast<void>(::close(readiness[0]));
        if (::setpgid(0, 0) != 0 ||
            ::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
            ::signal(SIGTERM, SIG_IGN) == SIG_ERR ||
            !append_process_id(records, ::getpid())) {
            _exit(70);
        }
        bool announced = false;
        for (unsigned int index = 0U; index < 48U; ++index) {
            const pid_t descendant = ::fork();
            if (descendant == 0) {
                static_cast<void>(::close(readiness[1]));
                static_cast<void>(::close(records));
                if (::setpgid(0, 0) != 0 ||
                    ::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
                    ::signal(SIGTERM, SIG_IGN) == SIG_ERR) {
                    _exit(70);
                }
                while (true) {
                    errno = 0;
                    if (::pause() < 0 && errno == EINTR) continue;
                    _exit(74);
                }
            }
            if (descendant > 0) {
                if (!append_process_id(records, descendant)) _exit(74);
                if (!announced) {
                    const std::uint8_t ready = 1U;
                    if (::write(readiness[1], &ready, sizeof(ready)) !=
                        static_cast<ssize_t>(sizeof(ready))) {
                        _exit(74);
                    }
                    announced = true;
                }
            } else if (errno != EAGAIN && errno != ENOMEM) {
                _exit(74);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds{1});
        }
        static_cast<void>(::close(readiness[1]));
        static_cast<void>(::close(records));
        while (true) {
            errno = 0;
            if (::pause() < 0 && errno == EINTR) continue;
            _exit(74);
        }
    }

    static_cast<void>(::close(readiness[1]));
    static_cast<void>(::close(records));
    std::uint8_t ready = 0U;
    ssize_t count = -1;
    do {
        count = ::read(readiness[0], &ready, sizeof(ready));
    } while (count < 0 && errno == EINTR);
    static_cast<void>(::close(readiness[0]));
    if (count != static_cast<ssize_t>(sizeof(ready)) || ready != 1U) {
        static_cast<void>(::kill(churner, SIGKILL));
        return 70;
    }
    if (::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
        ::signal(SIGTERM, SIG_IGN) == SIG_ERR) {
        static_cast<void>(::kill(churner, SIGKILL));
        return 74;
    }
    const std::string text =
        "leader-pid=" +
        std::to_string(static_cast<std::uint64_t>(::getpid())) + "\n" +
        "churner-pid=" +
        std::to_string(static_cast<std::uint64_t>(churner)) +
        "\nREADY\n";
    if (!write_text(text)) {
        static_cast<void>(::kill(churner, SIGKILL));
        return 74;
    }
    while (true) {
        errno = 0;
        if (::pause() < 0 && errno == EINTR) continue;
        return 74;
    }
}

[[nodiscard]] bool open_write_denied(std::string_view path) {
    errno = 0;
    const int descriptor = ::open(
        std::string(path).c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
        static_cast<mode_t>(0600));
    if (descriptor >= 0) {
        static_cast<void>(::close(descriptor));
        return false;
    }
    return errno == EACCES;
}

[[nodiscard]] bool tcp_connect_denied() {
    const int descriptor = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(9U);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    errno = 0;
    const int result = ::connect(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool tcp_bind_denied() {
    const int descriptor = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(0U);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    errno = 0;
    const int result = ::bind(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool udp_bind_denied() {
    const int descriptor = ::socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(0U);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    errno = 0;
    const int result = ::bind(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool udp_connect_denied() {
    const int descriptor = ::socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(9U);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    errno = 0;
    const int result = ::connect(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool udp_send_denied() {
    const int descriptor = ::socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(9U);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    const std::uint8_t byte = 0U;
    errno = 0;
    const ssize_t result = ::sendto(
        descriptor, &byte, sizeof(byte), 0,
        reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool pathname_unix_connect_denied(std::string_view path) {
    if (path.size() >= sizeof(sockaddr_un::sun_path)) return false;
    const int descriptor = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, path.data(), path.size());
    address.sun_path[path.size()] = '\0';
    errno = 0;
    const int result = ::connect(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        static_cast<socklen_t>(sizeof(address)));
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool abstract_unix_connect_denied(std::string_view name) {
    if (name.empty() || name.size() + 1U > sizeof(sockaddr_un::sun_path)) {
        return false;
    }
    const int descriptor = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    address.sun_path[0] = '\0';
    std::memcpy(address.sun_path + 1, name.data(), name.size());
    const socklen_t address_length = static_cast<socklen_t>(
        offsetof(sockaddr_un, sun_path) + 1U + name.size());
    errno = 0;
    const int result = ::connect(
        descriptor, reinterpret_cast<const sockaddr *>(&address),
        address_length);
    const int saved_errno = errno;
    static_cast<void>(::close(descriptor));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] bool inside_pathname_unix_bind_succeeds() {
    constexpr std::string_view path{"strict-inside.sock"};
    const int descriptor = ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (descriptor < 0) return false;
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, path.data(), path.size());
    address.sun_path[path.size()] = '\0';
    const socklen_t address_length = static_cast<socklen_t>(
        offsetof(sockaddr_un, sun_path) + path.size() + 1U);
    const bool bound = ::bind(
                           descriptor,
                           reinterpret_cast<const sockaddr *>(&address),
                           address_length) == 0;
    static_cast<void>(::close(descriptor));
    const bool removed = !bound || ::unlink(std::string(path).c_str()) == 0;
    return bound && removed;
}

[[nodiscard]] bool inside_cross_directory_rename_succeeds() {
    constexpr const char *source_directory = "strict-source";
    constexpr const char *target_directory = "strict-target";
    constexpr const char *source_file = "strict-source/item";
    constexpr const char *target_file = "strict-target/item";
    if (::mkdir(source_directory, static_cast<mode_t>(0700)) != 0 ||
        ::mkdir(target_directory, static_cast<mode_t>(0700)) != 0) {
        return false;
    }
    const int descriptor = ::open(
        source_file, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
        static_cast<mode_t>(0600));
    if (descriptor < 0) return false;
    static_cast<void>(::close(descriptor));
    if (::rename(source_file, target_file) != 0) return false;
    if (::truncate(target_file, 0) != 0) return false;
    if (::unlink(target_file) != 0) return false;
    if (::rmdir(source_directory) != 0 || ::rmdir(target_directory) != 0) {
        return false;
    }
    return true;
}

[[nodiscard]] bool outside_truncate_denied(std::string_view path) {
    errno = 0;
    const int descriptor = ::open(
        std::string(path).c_str(), O_RDONLY | O_TRUNC | O_CLOEXEC);
    if (descriptor >= 0) {
        static_cast<void>(::close(descriptor));
        return false;
    }
    return errno == EACCES;
}

[[nodiscard]] bool outside_unlink_denied(std::string_view path) {
    errno = 0;
    return ::unlink(std::string(path).c_str()) != 0 && errno == EACCES;
}

[[nodiscard]] bool signal_scope_denied() {
    errno = 0;
    const int result = ::kill(::getppid(), 0);
    return result < 0 && errno == EPERM;
}

[[nodiscard]] bool executable_gain_denied() {
    void *mapping = ::mmap(
        nullptr, 4096U, PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (mapping == MAP_FAILED) return false;
    errno = 0;
    const int result = ::mprotect(mapping, 4096U, PROT_READ | PROT_EXEC);
    const int saved_errno = errno;
    static_cast<void>(::munmap(mapping, 4096U));
    return result < 0 && saved_errno == EACCES;
}

[[nodiscard]] int run_strict_probe(
    std::string_view outside_path, std::string_view outside_existing_path,
    std::string_view unix_socket_path, std::string_view abstract_socket_name) {
    const int inside = ::open(
        "strict-inside.txt", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,
        static_cast<mode_t>(0600));
    const bool inside_write = inside >= 0;
    if (inside >= 0) static_cast<void>(::close(inside));
    const bool inside_rename = inside_cross_directory_rename_succeeds();
    const bool inside_unix_bind = inside_pathname_unix_bind_succeeds();
    const bool outside_write = open_write_denied(outside_path);
    const bool outside_truncate = outside_truncate_denied(outside_existing_path);
    const bool outside_unlink = outside_unlink_denied(outside_existing_path);
    const bool tcp_connect = tcp_connect_denied();
    const bool tcp_bind = tcp_bind_denied();
    const bool udp_send = udp_send_denied();
    const bool udp_connect = udp_connect_denied();
    const bool udp_bind = udp_bind_denied();
    const bool pathname_unix = pathname_unix_connect_denied(unix_socket_path);
    const bool abstract_unix =
        abstract_unix_connect_denied(abstract_socket_name);
    const bool signal = signal_scope_denied();
    const bool mdwe = executable_gain_denied();
    const bool seccomp = baseline_syscall_is_denied();

    std::string text;
    text += "inside-write=" + std::to_string(inside_write ? 1 : 0) + "\n";
    text += "inside-rename=" + std::to_string(inside_rename ? 1 : 0) + "\n";
    text += "inside-unix-bind=" +
            std::to_string(inside_unix_bind ? 1 : 0) + "\n";
    text += "outside-write-denied=" + std::to_string(outside_write ? 1 : 0) + "\n";
    text += "outside-truncate-denied=" +
            std::to_string(outside_truncate ? 1 : 0) + "\n";
    text += "outside-unlink-denied=" +
            std::to_string(outside_unlink ? 1 : 0) + "\n";
    text += "tcp-connect-denied=" +
            std::to_string(tcp_connect ? 1 : 0) + "\n";
    text += "tcp-bind-denied=" + std::to_string(tcp_bind ? 1 : 0) + "\n";
    text += "udp-send-denied=" + std::to_string(udp_send ? 1 : 0) + "\n";
    text += "udp-connect-denied=" +
            std::to_string(udp_connect ? 1 : 0) + "\n";
    text += "udp-bind-denied=" + std::to_string(udp_bind ? 1 : 0) + "\n";
    text += "pathname-unix-denied=" +
            std::to_string(pathname_unix ? 1 : 0) + "\n";
    text += "abstract-unix-denied=" +
            std::to_string(abstract_unix ? 1 : 0) + "\n";
    text += "signal-scope-denied=" + std::to_string(signal ? 1 : 0) + "\n";
    text += "mdwe-denied=" + std::to_string(mdwe ? 1 : 0) + "\n";
    text += "seccomp-denied=" + std::to_string(seccomp ? 1 : 0) + "\n";
    if (!write_text(text)) return 74;
    return inside_write && inside_rename && inside_unix_bind && outside_write &&
                   outside_truncate && outside_unlink && tcp_connect &&
                   tcp_bind && udp_send && udp_connect && udp_bind &&
                   pathname_unix && abstract_unix && signal && mdwe && seccomp
               ? 0
               : 70;
}

[[nodiscard]] int run_hold() {
    if (::signal(SIGHUP, SIG_IGN) == SIG_ERR ||
        ::signal(SIGTERM, SIG_IGN) == SIG_ERR || !make_raw()) {
        return 74;
    }
    const std::string ready =
        "pid=" +
        std::to_string(static_cast<std::uint64_t>(::getpid())) +
        "\nREADY\n";
    if (!write_text(ready)) return 74;
    while (true) {
        errno = 0;
        if (::pause() < 0 && errno == EINTR) continue;
        return 74;
    }
}

[[nodiscard]] int run_quiescence_probe() {
    if (!make_raw()) return 74;
    const std::string ready =
        "leader-pid=" +
        std::to_string(static_cast<std::uint64_t>(::getpid())) +
        "\nREADY\n";
    if (!write_text(ready)) return 74;
    std::uint8_t release = 0U;
    ssize_t count = -1;
    do {
        count = ::read(STDIN_FILENO, &release, sizeof(release));
    } while (count < 0 && errno == EINTR);
    return count == static_cast<ssize_t>(sizeof(release)) ? 0 : 74;
}

[[nodiscard]] int run_sudo_probe(
    std::string_view sudo_path, std::string_view id_path) {
    if (!write_text(
            "pre-sudo-euid=" +
            std::to_string(static_cast<std::uint64_t>(::geteuid())) +
            "\n")) {
        return 74;
    }
    const pid_t child = ::fork();
    if (child < 0) return 74;
    if (child == 0) {
        const std::string sudo_executable(sudo_path);
        const std::string id_executable(id_path);
        ::execl(
            sudo_executable.c_str(), "sudo", "--non-interactive", "--",
            id_executable.c_str(), "-u", nullptr);
        _exit(127);
    }
    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(child, &status, 0);
    } while (waited < 0 && errno == EINTR);
    if (waited != child) return 74;
    const int exit_status = WIFEXITED(status) ? WEXITSTATUS(status) : 255;
    if (!write_text(
            "sudo-exit=" + std::to_string(exit_status) +
            " post-sudo-euid=" +
            std::to_string(static_cast<std::uint64_t>(::geteuid())) +
            "\n")) {
        return 74;
    }
    return exit_status;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 6 && std::string_view(argv[1]) == "strict-probe") {
        return run_strict_probe(argv[2], argv[3], argv[4], argv[5]);
    }
    if (argc == 3 && std::string_view(argv[1]) == "fd-probe") {
        return run_fd_probe(argv[2]);
    }
    if (argc == 3 && std::string_view(argv[1]) == "session-fork-churn") {
        return run_session_fork_churn(argv[2]);
    }
    if (argc == 4 && std::string_view(argv[1]) == "sudo-probe") {
        return run_sudo_probe(argv[2], argv[3]);
    }
    if (argc != 2) return 64;
    const std::string_view mode{argv[1]};
    if (mode == "report") return write_text(report()) ? 0 : 74;
    if (mode == "echo") return run_echo();
    if (mode == "ignore") return run_ignore();
    if (mode == "hold") return run_hold();
    if (mode == "quiescence-probe") return run_quiescence_probe();
    if (mode == "baseline-fence-probe") return run_baseline_fence_probe();
    if (mode == "session-tree") return run_session_tree(false);
    if (mode == "session-orphan") return run_session_tree(true);
    return 64;
}
