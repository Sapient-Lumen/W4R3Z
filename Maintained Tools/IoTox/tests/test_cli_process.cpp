#include <chrono>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <initializer_list>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

namespace {

struct CommandResult {
    int exit_code{0};
    std::string output;
};

#ifndef IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER
#define IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER 1
#endif

static_assert(IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER >= 1);
static_assert(IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER <= 16);

constexpr std::chrono::milliseconds process_test_timeout(
    std::chrono::milliseconds baseline) noexcept {
    return baseline * IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER;
}

std::chrono::steady_clock::time_point process_test_deadline(
    std::chrono::milliseconds baseline) noexcept {
    return std::chrono::steady_clock::now() + process_test_timeout(baseline);
}

std::string read_text(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("unable to read " + path.string());
    }
    std::ostringstream output;
    output << input.rdbuf();
    return output.str();
}

std::size_t count_occurrences(
    std::string_view text, std::string_view needle) {
    if (needle.empty()) {
        return 0U;
    }
    std::size_t count = 0U;
    std::size_t offset = 0U;
    while ((offset = text.find(needle, offset)) != std::string_view::npos) {
        ++count;
        offset += needle.size();
    }
    return count;
}

bool command_record_contains(
    std::string_view snapshot,
    std::initializer_list<std::string_view> required_fields) {
    std::size_t begin = snapshot.find("---\n");
    while (begin != std::string_view::npos) {
        begin += 4U;
        const std::size_t end = snapshot.find("---\n", begin);
        const std::string_view record = snapshot.substr(begin, end - begin);
        bool matches = true;
        for (const std::string_view field : required_fields) {
            if (record.find(field) == std::string_view::npos) {
                matches = false;
                break;
            }
        }
        if (matches) {
            return true;
        }
        begin = end;
    }
    return false;
}

std::vector<char *> make_argv(std::vector<std::string> &arguments) {
    std::vector<char *> argv;
    argv.reserve(arguments.size() + 1U);
    for (std::string &argument : arguments) {
        argv.push_back(argument.data());
    }
    argv.push_back(nullptr);
    return argv;
}

CommandResult run_capture(
    const std::filesystem::path &program, const std::vector<std::string> &extra_arguments) {
    int descriptors[2]{};
    if (::pipe(descriptors) != 0) {
        throw std::runtime_error("pipe failed: " + std::string(std::strerror(errno)));
    }

    const pid_t child = ::fork();
    if (child < 0) {
        static_cast<void>(::close(descriptors[0]));
        static_cast<void>(::close(descriptors[1]));
        throw std::runtime_error("fork failed: " + std::string(std::strerror(errno)));
    }
    if (child == 0) {
        static_cast<void>(::close(descriptors[0]));
        if (::dup2(descriptors[1], STDOUT_FILENO) < 0 ||
            ::dup2(descriptors[1], STDERR_FILENO) < 0) {
            _exit(126);
        }
        static_cast<void>(::close(descriptors[1]));

        std::vector<std::string> arguments;
        arguments.reserve(extra_arguments.size() + 1U);
        arguments.push_back(program.string());
        arguments.insert(arguments.end(), extra_arguments.begin(), extra_arguments.end());
        std::vector<char *> argv = make_argv(arguments);
        ::execv(program.c_str(), argv.data());
        _exit(127);
    }

    static_cast<void>(::close(descriptors[1]));
    std::string output;
    char buffer[4096]{};
    while (true) {
        const ssize_t count = ::read(descriptors[0], buffer, sizeof(buffer));
        if (count > 0) {
            output.append(buffer, static_cast<std::size_t>(count));
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        break;
    }
    static_cast<void>(::close(descriptors[0]));

    int status = 0;
    if (::waitpid(child, &status, 0) != child) {
        throw std::runtime_error("waitpid failed");
    }
    int exit_code = 128;
    if (WIFEXITED(status)) {
        exit_code = WEXITSTATUS(status);
    } else if (WIFSIGNALED(status)) {
        exit_code = 128 + WTERMSIG(status);
    }
    return {exit_code, std::move(output)};
}

CommandResult run_capture_with_input(
    const std::filesystem::path &program,
    const std::vector<std::string> &extra_arguments,
    std::span<const std::uint8_t> input) {
    int output_descriptors[2]{};
    int input_descriptors[2]{};
    if (::pipe(output_descriptors) != 0 || ::pipe(input_descriptors) != 0) {
        const int saved_errno = errno;
        for (const int descriptor : output_descriptors) {
            if (descriptor != 0) {
                static_cast<void>(::close(descriptor));
            }
        }
        for (const int descriptor : input_descriptors) {
            if (descriptor != 0) {
                static_cast<void>(::close(descriptor));
            }
        }
        throw std::runtime_error(
            "pipe failed: " + std::string(std::strerror(saved_errno)));
    }

    // Preload the bounded test input while this process still owns a read end.
    // A post-fork write races fast argument-validation failures and can raise
    // SIGPIPE before the harness can inspect the child's intended exit status.
    // Staying within PIPE_BUF makes the preload atomic and non-blocking on the
    // empty pipe.
    const long pipe_buffer = ::fpathconf(input_descriptors[1], _PC_PIPE_BUF);
    if (pipe_buffer < 0 ||
        input.size() > static_cast<std::size_t>(pipe_buffer)) {
        const int saved_errno = pipe_buffer < 0 ? errno : EOVERFLOW;
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "stdin test input exceeds the atomic pipe preload limit: " +
            std::string(std::strerror(saved_errno)));
    }
    std::size_t written = 0U;
    while (written < input.size()) {
        const ssize_t count = ::write(
            input_descriptors[1], input.data() + written, input.size() - written);
        if (count > 0) {
            written += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        const int saved_errno = errno;
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "stdin pipe preload failed: " +
            std::string(std::strerror(saved_errno)));
    }

    const pid_t child = ::fork();
    if (child < 0) {
        const int saved_errno = errno;
        for (const int descriptor : output_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        for (const int descriptor : input_descriptors) {
            static_cast<void>(::close(descriptor));
        }
        throw std::runtime_error(
            "fork failed: " + std::string(std::strerror(saved_errno)));
    }
    if (child == 0) {
        static_cast<void>(::close(output_descriptors[0]));
        static_cast<void>(::close(input_descriptors[1]));
        if (::dup2(output_descriptors[1], STDOUT_FILENO) < 0 ||
            ::dup2(output_descriptors[1], STDERR_FILENO) < 0 ||
            ::dup2(input_descriptors[0], STDIN_FILENO) < 0) {
            _exit(126);
        }
        static_cast<void>(::close(output_descriptors[1]));
        static_cast<void>(::close(input_descriptors[0]));

        std::vector<std::string> arguments;
        arguments.reserve(extra_arguments.size() + 1U);
        arguments.push_back(program.string());
        arguments.insert(arguments.end(), extra_arguments.begin(), extra_arguments.end());
        std::vector<char *> argv = make_argv(arguments);
        ::execv(program.c_str(), argv.data());
        _exit(127);
    }

    static_cast<void>(::close(output_descriptors[1]));
    static_cast<void>(::close(input_descriptors[0]));
    static_cast<void>(::close(input_descriptors[1]));

    std::string output;
    char buffer[4096]{};
    while (true) {
        const ssize_t count = ::read(output_descriptors[0], buffer, sizeof(buffer));
        if (count > 0) {
            output.append(buffer, static_cast<std::size_t>(count));
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        break;
    }
    static_cast<void>(::close(output_descriptors[0]));

    int status = 0;
    if (::waitpid(child, &status, 0) != child) {
        throw std::runtime_error("waitpid failed");
    }
    int exit_code = 128;
    if (WIFEXITED(status)) {
        exit_code = WEXITSTATUS(status);
    } else if (WIFSIGNALED(status)) {
        exit_code = 128 + WTERMSIG(status);
    }
    return {exit_code, std::move(output)};
}

pid_t spawn_agent(
    const std::filesystem::path &iotox,
    const std::filesystem::path &mock_toxcore,
    const std::filesystem::path &runtime,
    const std::filesystem::path &state,
    const std::filesystem::path &log,
    const std::filesystem::path &capture_sent_file = {},
    std::string incoming_filename = {},
    bool inject_session_sendq = false,
    bool start_friends_offline = false,
    bool trust_wall_clock = false,
    bool emit_profile_status_command = false,
    std::string profile_status_desired = {},
    bool stop_after_self_status_call = false,
    bool file_backed_config = false,
    std::uint32_t mock_address_tag = 0U) {
    const pid_t child = ::fork();
    if (child < 0) {
        throw std::runtime_error("fork failed: " + std::string(std::strerror(errno)));
    }
    if (child == 0) {
        const int descriptor = ::open(log.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (descriptor < 0 || ::dup2(descriptor, STDOUT_FILENO) < 0 ||
            ::dup2(descriptor, STDERR_FILENO) < 0) {
            _exit(126);
        }
        if (descriptor != STDOUT_FILENO && descriptor != STDERR_FILENO) {
            static_cast<void>(::close(descriptor));
        }

        if (!capture_sent_file.empty() &&
            ::setenv("IOTOX_MOCK_CAPTURE_SENT_FILE",
                     capture_sent_file.c_str(), 1) != 0) {
            _exit(126);
        }
        if (!incoming_filename.empty() &&
            ::setenv("IOTOX_MOCK_INCOMING_FILE", incoming_filename.c_str(), 1) != 0) {
            _exit(126);
        }
        const std::filesystem::path authority_audit =
            log.parent_path() / "mock-authority-audit.log";
        if (::setenv("IOTOX_MOCK_AUTHORITY_AUDIT",
                     authority_audit.c_str(), 1) != 0) {
            _exit(126);
        }
        if (inject_session_sendq &&
            (::setenv("IOTOX_MOCK_HELLO_SENDQ_FAILURES", "1", 1) != 0 ||
             ::setenv("IOTOX_MOCK_CONFIRMATION_SENDQ_FAILURES", "1", 1) != 0 ||
             ::setenv("IOTOX_MOCK_AUTHORITY_CHALLENGE_SENDQ_FAILURES",
                      "1", 1) != 0 ||
             ::setenv("IOTOX_MOCK_AUTHORITY_PROOF_SENDQ_FAILURES",
                      "1", 1) != 0 ||
             ::setenv("IOTOX_MOCK_COMMAND_SENDQ_FAILURES",
                      "1", 1) != 0 ||
             ::setenv(
                 "IOTOX_MOCK_COMMAND_RESULT_SENDQ_FAILURES_PER_REQUEST",
                 "1", 1) != 0)) {
            _exit(126);
        }
        if ((inject_session_sendq || emit_profile_status_command) &&
            ::setenv("IOTOX_MOCK_PROFILE_STATUS_COMMAND", "1", 1) != 0) {
            _exit(126);
        }
        if (!profile_status_desired.empty() &&
            ::setenv("IOTOX_MOCK_PROFILE_STATUS_DESIRED",
                     profile_status_desired.c_str(), 1) != 0) {
            _exit(126);
        }
        if (stop_after_self_status_call &&
            ::setenv("IOTOX_MOCK_STOP_AFTER_SELF_STATUS_CALL", "1", 1) != 0) {
            _exit(126);
        }
        if (start_friends_offline &&
            ::setenv("IOTOX_MOCK_START_FRIENDS_OFFLINE", "1", 1) != 0) {
            _exit(126);
        }
        if (mock_address_tag != 0U) {
            const std::string tag = std::to_string(mock_address_tag);
            if (::setenv("IOTOX_MOCK_ADDRESS_TAG", tag.c_str(), 1) != 0) {
                _exit(126);
            }
        }

        const std::string key(
            "000102030405060708090A0B0C0D0E0F"
            "101112131415161718191A1B1C1D1E1F");
        std::vector<std::string> agent_arguments{
            "--library", mock_toxcore.string(),
            "--runtime", runtime.string(),
            "--state", state.string(),
            "--bootstrap", "bootstrap.test:33445:" + key,
            "--tcp-relay", "relay.test:443:" + key,
            "--bootstrap-retry-ms", "100",
        };
        if (trust_wall_clock) {
            agent_arguments.push_back("--trust-wall-clock");
        }
        std::vector<std::string> arguments{iotox.string(), "run"};
        if (file_backed_config) {
            const std::filesystem::path config_path =
                log.string() + ".agent.conf";
            std::ofstream config(
                config_path, std::ios::binary | std::ios::trunc);
            config << "iotox-agent-config-v1\n";
            for (std::size_t index = 0U; index < agent_arguments.size();
                 ++index) {
                config << "argument-" << std::setw(4) << std::setfill('0')
                       << index << '=' << agent_arguments[index] << '\n';
            }
            config.close();
            if (!config.good() || ::chmod(config_path.c_str(), 0600) != 0) {
                _exit(126);
            }
            arguments.push_back("--config");
            arguments.push_back(config_path.string());
        } else {
            arguments.insert(arguments.end(), agent_arguments.begin(),
                             agent_arguments.end());
        }
        // The test requests an orderly stop. Keep the watchdog long enough
        // that loaded sanitizer/matrix hosts cannot kill the agent in the
        // middle of an otherwise valid asynchronous assertion. In the
        // file-backed cell this also proves an explicit CLI override.
        arguments.push_back("--run-ms");
        arguments.push_back(std::to_string(
            process_test_timeout(std::chrono::seconds(60)).count()));
        std::vector<char *> argv = make_argv(arguments);
        ::execv(iotox.c_str(), argv.data());
        _exit(127);
    }
    return child;
}

void require(bool condition, std::string_view message) {
    if (!condition) {
        throw std::runtime_error(std::string(message));
    }
}

struct ProductIdentity {
    std::string version;
    std::string revision;
    std::string revision_number;
};

ProductIdentity read_product_identity(const std::filesystem::path &iotox) {
    const CommandResult result = run_capture(iotox, {"--version"});
    require(result.exit_code == 0,
            "unable to read product identity from the tested IoTox binary");

    std::istringstream input(result.output);
    std::string project;
    ProductIdentity identity;
    std::string trailing;
    require(static_cast<bool>(input >> project >> identity.version >> identity.revision) &&
                !(input >> trailing) && project == "IoTox",
            "tested IoTox binary emitted an invalid --version identity");
    require(identity.revision.size() > 3U &&
                identity.revision.starts_with("rev"),
            "tested IoTox binary emitted an invalid revision token");

    const std::string digits = identity.revision.substr(3U);
    for (const char digit : digits) {
        require(digit >= '0' && digit <= '9',
                "tested IoTox binary emitted a nonnumeric revision token");
    }
    const std::size_t first_nonzero = digits.find_first_not_of('0');
    identity.revision_number =
        first_nonzero == std::string::npos ? "0" : digits.substr(first_nonzero);
    return identity;
}

void write_fifo_record(pid_t agent, const std::filesystem::path &path,
                       std::string_view record) {
    require(!record.empty() && record.size() <= 512U,
            "process test FIFO record must be one small atomic write");

    int descriptor = -1;
    const auto deadline =
        process_test_deadline(std::chrono::seconds(5));
    while (std::chrono::steady_clock::now() < deadline) {
        struct stat metadata {};
        if (::lstat(path.c_str(), &metadata) == 0) {
            require(S_ISFIFO(metadata.st_mode) && !S_ISLNK(metadata.st_mode) &&
                        (metadata.st_mode & 0777U) == 0600U,
                    "ratox-style peer path is not a private FIFO");
            descriptor = ::open(path.c_str(),
                                O_WRONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
            if (descriptor >= 0) {
                break;
            }
            if (errno != ENXIO && errno != ENOENT) {
                throw std::runtime_error(
                    "unable to open ratox-style peer FIFO: " +
                    std::string(std::strerror(errno)));
            }
        } else if (errno != ENOENT) {
            throw std::runtime_error(
                "unable to inspect ratox-style peer FIFO: " +
                std::string(std::strerror(errno)));
        }

        int status = 0;
        const pid_t result = ::waitpid(agent, &status, WNOHANG);
        if (result == agent) {
            throw std::runtime_error(
                "iotox run exited before accepting its ratox-style peer FIFO");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    require(descriptor >= 0,
            "timed out waiting for ratox-style peer FIFO reader");

    ssize_t written = -1;
    do {
        written = ::write(descriptor, record.data(), record.size());
    } while (written < 0 && errno == EINTR);
    const int write_errno = errno;
    const int close_result = ::close(descriptor);
    require(written == static_cast<ssize_t>(record.size()),
            "ratox-style peer FIFO record was not accepted as one atomic write: " +
                std::string(std::strerror(write_errno)));
    require(close_result == 0,
            "unable to close ratox-style peer FIFO writer");
}

void wait_for_socket(pid_t agent, const std::filesystem::path &socket) {
    const auto deadline = process_test_deadline(std::chrono::seconds(5));
    while (std::chrono::steady_clock::now() < deadline) {
        struct stat metadata {};
        if (::lstat(socket.c_str(), &metadata) == 0 && S_ISSOCK(metadata.st_mode)) {
            return;
        }
        int status = 0;
        const pid_t result = ::waitpid(agent, &status, WNOHANG);
        if (result == agent) {
            throw std::runtime_error("iotox run exited before creating its control socket");
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    throw std::runtime_error("timed out waiting for iotox run control socket");
}

bool wait_for_text(
    const std::filesystem::path &path, std::string_view expected,
    std::chrono::milliseconds timeout = std::chrono::seconds(5)) {
    const auto deadline = process_test_deadline(timeout);
    while (std::chrono::steady_clock::now() < deadline) {
        std::ifstream input(path, std::ios::binary);
        if (input) {
            std::ostringstream output;
            output << input.rdbuf();
            if (output.str() == expected) {
                return true;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return false;
}

void terminate_child(pid_t &child) noexcept {
    if (child <= 0) {
        return;
    }

    int status = 0;
    const pid_t already = ::waitpid(child, &status, WNOHANG);
    if (already == child || (already < 0 && errno == ECHILD)) {
        child = -1;
        return;
    }

    static_cast<void>(::kill(child, SIGTERM));
    const auto deadline =
        process_test_deadline(std::chrono::seconds(1));
    while (std::chrono::steady_clock::now() < deadline) {
        const pid_t result = ::waitpid(child, &status, WNOHANG);
        if (result == child || (result < 0 && errno == ECHILD)) {
            child = -1;
            return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    static_cast<void>(::kill(child, SIGKILL));
    while (::waitpid(child, &status, 0) < 0 && errno == EINTR) {
    }
    child = -1;
}

int wait_for_exit(pid_t child, std::chrono::seconds timeout) {
    const auto deadline = process_test_deadline(timeout);
    while (std::chrono::steady_clock::now() < deadline) {
        int status = 0;
        const pid_t result = ::waitpid(child, &status, WNOHANG);
        if (result == child) {
            if (WIFEXITED(status)) {
                return WEXITSTATUS(status);
            }
            if (WIFSIGNALED(status)) {
                return 128 + WTERMSIG(status);
            }
            return 128;
        }
        if (result < 0) {
            throw std::runtime_error("waitpid failed: " + std::string(std::strerror(errno)));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    static_cast<void>(::kill(child, SIGKILL));
    int status = 0;
    static_cast<void>(::waitpid(child, &status, 0));
    throw std::runtime_error("iotox run did not stop after the local shutdown request");
}

int wait_for_stop(pid_t child, std::chrono::seconds timeout) {
    const auto deadline = process_test_deadline(timeout);
    while (std::chrono::steady_clock::now() < deadline) {
        int status = 0;
        const pid_t result = ::waitpid(child, &status, WNOHANG | WUNTRACED);
        if (result == child) {
            if (WIFSTOPPED(status)) {
                return WSTOPSIG(status);
            }
            return 0;
        }
        if (result < 0) {
            throw std::runtime_error(
                "waitpid failed: " + std::string(std::strerror(errno)));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}

CommandResult run_control(
    const std::filesystem::path &iotox,
    const std::filesystem::path &runtime,
    std::vector<std::string> command) {
    std::vector<std::string> arguments{"--runtime", runtime.string(), "--timeout-ms", "5000"};
    arguments.insert(arguments.end(), command.begin(), command.end());
    return run_capture(iotox, arguments);
}

CommandResult run_control_with_input(
    const std::filesystem::path &iotox,
    const std::filesystem::path &runtime,
    std::vector<std::string> command,
    std::span<const std::uint8_t> input) {
    std::vector<std::string> arguments{"--runtime", runtime.string(), "--timeout-ms", "5000"};
    arguments.insert(arguments.end(), command.begin(), command.end());
    return run_capture_with_input(iotox, arguments, input);
}

std::string extract_field(
    std::string_view text, std::string_view field) {
    const std::string prefix = std::string(field) + "=";
    const std::size_t begin = text.find(prefix);
    if (begin == std::string_view::npos) {
        return {};
    }
    const std::size_t value_begin = begin + prefix.size();
    const std::size_t end = text.find('\n', value_begin);
    return std::string(text.substr(value_begin, end - value_begin));
}

std::string extract_address(std::string_view status) {
    return extract_field(status, "address");
}

}  // namespace

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "usage: test_cli_process IOTOX MOCK_TOXCORE\n";
        return 2;
    }

    const std::filesystem::path iotox = argv[1];
    const std::filesystem::path mock_toxcore = argv[2];
    const ProductIdentity product_identity = read_product_identity(iotox);
    const std::filesystem::path directory =
        std::filesystem::temp_directory_path() /
        ("iotox-process-test-" + std::to_string(static_cast<long long>(::getpid())));
    const std::filesystem::path runtime = directory / "run";
    const std::filesystem::path state = directory / "state" / "device.toxsave";
    const std::filesystem::path first_log = directory / "agent-first.log";
    const std::filesystem::path second_log = directory / "agent-second.log";
    const std::filesystem::path mutation_crash_log =
        directory / "agent-mutation-crash.log";
    const std::filesystem::path mutation_recovery_log =
        directory / "agent-mutation-recovery.log";
    const std::filesystem::path invitation_runtime =
        directory / "ir";
    const std::filesystem::path invitation_state =
        directory / "is" / "d.toxsave";
    const std::filesystem::path invitation_log =
        directory / "agent-invitation.log";
    const std::filesystem::path invitation_artifact =
        directory / "founder.iotox-invitation";
    const std::filesystem::path outgoing_source = directory / "send.bin";
    const std::filesystem::path outgoing_capture = directory / "captured.bin";
    const std::filesystem::path incoming_destination = directory / "received.bin";
    const std::filesystem::path authority_audit =
        directory / "mock-authority-audit.log";

    std::error_code ignored;
    std::filesystem::remove_all(directory, ignored);
    pid_t first = -1;
    pid_t second = -1;
    pid_t invitee = -1;
    try {
        require(std::filesystem::create_directories(directory),
                "unable to create process-test directory");
        {
            std::ofstream output(outgoing_source, std::ios::binary | std::ios::trunc);
            output << "BINARY-JUST-WERX";
            require(output.good(), "unable to create outgoing process fixture");
        }

        first = spawn_agent(
            iotox, mock_toxcore, runtime, state, first_log,
            outgoing_capture, "process-incoming.bin", true);
        wait_for_socket(first, runtime / "control.sock");

        const CommandResult ping = run_control(iotox, runtime, {"ping"});
        require(ping.exit_code == 0 && ping.output == "pong\n", "iotox ping failed");

        const CommandResult status = run_control(iotox, runtime, {"status"});
        require(status.exit_code == 0, "iotox status failed");
        require(status.output.find("phase=running") != std::string::npos &&
                    status.output.find("command-store-initialized=1") !=
                        std::string::npos &&
                    status.output.find("command-sender-epoch=0") ==
                        std::string::npos,
                "status did not report the running durable-command core\n--- status ---\n" +
                    status.output);
        const std::string first_address = extract_address(status.output);
        require(first_address.size() == 76U, "status returned an invalid Tox address");

        CommandResult route_health;
        const auto carrier_deadline =
            process_test_deadline(std::chrono::seconds(5));
        do {
            route_health = run_control(iotox, runtime, {"route-health"});
            if (route_health.exit_code == 0 &&
                route_health.output.find("carrier-connection=tcp\n") !=
                    std::string::npos) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        } while (std::chrono::steady_clock::now() < carrier_deadline);
        require(
            route_health.exit_code == 0 &&
                route_health.output.find("network=Tox/native\n") !=
                    std::string::npos &&
                route_health.output.find("carrier-connection=tcp\n") !=
                    std::string::npos &&
                route_health.output.find(
                    "local-boundary=not-applicable\n") !=
                    std::string::npos &&
                route_health.output.find("application=not-sampled\n") !=
                    std::string::npos &&
                route_health.output.find(
                    "semantics=auxiliary-only-no-carrier-or-session-epoch-mutation\n") !=
                    std::string::npos,
            "route-health did not preserve carrier truth and native boundary semantics\n--- route health ---\n" +
                route_health.output);

        const CommandResult native_target_health =
            run_control(iotox, runtime, {"route-target-health"});
        require(
            native_target_health.exit_code != 0 &&
                native_target_health.output.find(
                    "explicit strict routed-Tox TCP relay") !=
                    std::string::npos,
            "route-target-health did not reject the native route\n--- target health ---\n" +
                native_target_health.output);

        const CommandResult routes = run_control(iotox, runtime, {"routes"});
        require(routes.exit_code == 0 &&
                    routes.output ==
                        "mode=single\nroute-set-configured=0\n",
                "default route inventory did not preserve explicit single-route mode");
        const CommandResult routes_watch = run_control(
            iotox, runtime,
            {"--from-start", "--watch-ms", "250", "routes-watch"});
        require(routes_watch.exit_code == 0 &&
                    routes_watch.output == routes.output,
                "routes-watch did not emit one exact initial snapshot");

        const CommandResult identity = run_control(iotox, runtime, {"identity"});
        const std::string device_public_key =
            extract_field(identity.output, "device-public-key");
        require(identity.exit_code == 0 &&
                    identity.output.find("algorithm=Ed25519") != std::string::npos &&
                    device_public_key.size() == 64U,
                "stable IoTox device identity was not exposed");
        const CommandResult invitation_created = run_control(
            iotox, runtime,
            {"peer-invitation-create", invitation_artifact.string(),
             "3600", "founder",
             "interactive.terminal,sync.subscribe"});
        require(
            invitation_created.exit_code == 0 &&
                invitation_created.output.find(
                    "inviter-stable-principal=" + device_public_key + "\n") !=
                    std::string::npos &&
                invitation_created.output.find(
                    "tox-address=" + first_address + "\n") !=
                    std::string::npos &&
                invitation_created.output.find(
                    "requested-capabilities=interactive.terminal,sync.subscribe\n") !=
                    std::string::npos &&
                invitation_created.output.find("authority-granted=0\n") !=
                    std::string::npos,
            "Agent did not create one exact stable-device-signed invitation");
        const CommandResult invitation_inspected = run_control(
            iotox, runtime,
            {"peer-invitation-inspect", invitation_artifact.string()});
        const CommandResult invitation_imported = run_control(
            iotox, runtime,
            {"peer-invitation-import", invitation_artifact.string(),
             device_public_key});
        const CommandResult invitation_wrong_pin = run_control(
            iotox, runtime,
            {"peer-invitation-import", invitation_artifact.string(),
             std::string(64U, 'A')});
        const CommandResult invitation_no_clobber = run_control(
            iotox, runtime,
            {"peer-invitation-create", invitation_artifact.string(),
             "3600", "founder", "-"});
        require(
            invitation_inspected.exit_code == 0 &&
                invitation_inspected.output.find(
                    "inviter-trust=unestablished\n") != std::string::npos &&
                invitation_imported.exit_code == 0 &&
                invitation_imported.output.find(
                    "expected-inviter-match=1\n") != std::string::npos &&
                invitation_imported.output.find(
                    "import-ready=1\nimport-mutated-state=0\n") !=
                    std::string::npos &&
                invitation_wrong_pin.exit_code != 0 &&
                invitation_no_clobber.exit_code != 0,
            "invitation inspect/import pinning or no-clobber output failed");

        invitee = spawn_agent(
            iotox, mock_toxcore, invitation_runtime, invitation_state,
            invitation_log, {}, {}, false, false, false, false, {}, false,
            false, 1U);
        wait_for_socket(invitee, invitation_runtime / "control.sock");
        const CommandResult invitation_accepted = run_control(
            iotox, invitation_runtime,
            {"peer-invitation-accept", invitation_artifact.string(),
             device_public_key});
        const CommandResult invitation_accept_retry = run_control(
            iotox, invitation_runtime,
            {"peer-invitation-accept", invitation_artifact.string(),
             device_public_key});
        const std::string invited_transport_key =
            first_address.substr(0U, 64U);
        const CommandResult invitation_peers = run_control(
            iotox, invitation_runtime, {"peers"});
        const CommandResult invitation_aliases = run_control(
            iotox, invitation_runtime, {"peer-aliases"});
        const CommandResult invitation_authority = run_control(
            iotox, invitation_runtime, {"authority"});
        require(
            invitation_accepted.exit_code == 0 &&
                invitation_accepted.output.find(
                    "friend-number=0\nfriendship-changed=1\n") !=
                    std::string::npos &&
                invitation_accepted.output.find(
                    "alias=founder\nalias-changed=1\n") !=
                    std::string::npos &&
                invitation_accepted.output.find("authority-granted=0\n") !=
                    std::string::npos &&
                invitation_accept_retry.exit_code == 0 &&
                invitation_accept_retry.output.find(
                    "friend-number=0\nfriendship-changed=0\n") !=
                    std::string::npos &&
                invitation_accept_retry.output.find(
                    "alias=founder\nalias-changed=0\n") !=
                    std::string::npos &&
                invitation_peers.output.find(
                    "friend-number=0 public-key=" + invited_transport_key) !=
                    std::string::npos &&
                invitation_aliases.output.find(
                    "alias=founder public-key=" + invited_transport_key +
                    "\n") != std::string::npos &&
                invitation_authority.output.find("initialized=0") !=
                    std::string::npos,
            "signed invitation acceptance was not replay-safe or kept separate from authority");
        const CommandResult invitation_stop = run_control(
            iotox, invitation_runtime, {"stop"});
        require(invitation_stop.exit_code == 0 &&
                    wait_for_exit(invitee, std::chrono::seconds(5)) == 0,
                "invitation acceptor lifecycle failed");
        invitee = -1;
        const CommandResult empty_authority = run_control(iotox, runtime, {"authority"});
        require(empty_authority.exit_code == 0 &&
                    empty_authority.output.find("initialized=0") != std::string::npos &&
                    empty_authority.output.find("record-count=0") != std::string::npos,
                "fresh authority ledger did not begin unclaimed");

        const std::string recall_phrase =
            "abacus abdomen abdominal abide abiding ability ablaze able\n";
        const std::span<const std::uint8_t> recall_bytes(
            reinterpret_cast<const std::uint8_t *>(recall_phrase.data()),
            recall_phrase.size());
        const CommandResult recalled_public = run_control_with_input(
            iotox, runtime, {"recall-owner-public-key-stdin"}, recall_bytes);
        const std::string recalled_public_key =
            extract_field(recalled_public.output, "owner-public-key");
        require(recalled_public.exit_code == 0 &&
                    recalled_public_key.size() == 64U &&
                    recalled_public.output.find(recall_phrase) == std::string::npos,
                "RecallRoot owner public-key derivation failed or exposed its phrase");
        const CommandResult bootstrap_authority = run_control_with_input(
            iotox, runtime, {"authority-bootstrap-recall-stdin"}, recall_bytes);
        const std::string owner_public_key =
            extract_field(bootstrap_authority.output, "owner-public-key");
        require(bootstrap_authority.exit_code == 0 &&
                    owner_public_key.size() == 64U &&
                    owner_public_key == recalled_public_key &&
                    bootstrap_authority.output.find("initialized=1") !=
                        std::string::npos &&
                    bootstrap_authority.output.find("sequence=1") !=
                        std::string::npos,
                "RecallRoot-v1 did not bootstrap the signed owner ledger");
        require(bootstrap_authority.output.find(recall_phrase) == std::string::npos,
                "recall phrase leaked into command output");
        const CommandResult principals = run_control(iotox, runtime, {"principals"});
        require(principals.exit_code == 0 &&
                    principals.output.find("active=1 role=owner") != std::string::npos &&
                    principals.output.find("manage.principals") != std::string::npos,
                "bootstrapped owner was not projected as an active principal");
        require(read_text(runtime / "authority" / "initialized") == "1\n" &&
                    read_text(runtime / "authority" / "record-count") == "1\n",
                "ratox-style authority projection did not commit the bootstrap record");

        const std::string mock_authority_public_key =
            "D75A980182B10AB7D54BFED3C964073A"
            "0EE172F3DAA62325AF021A68F707511A";
        const CommandResult grant_mock = run_control_with_input(
            iotox, runtime,
            {"authority-grant-recall-stdin", mock_authority_public_key,
             "automation", "read.telemetry,write.settings,actuate"},
            recall_bytes);
        require(grant_mock.exit_code == 0 &&
                    grant_mock.output.find("sequence=2") != std::string::npos,
                "owner could not authorize the exact signed mock principal");
        const CommandResult granted_principals =
            run_control(iotox, runtime, {"principals"});
        require(granted_principals.exit_code == 0 &&
                    granted_principals.output.find(
                        "public-key=" + mock_authority_public_key) !=
                        std::string::npos &&
                    granted_principals.output.find(
                        "active=1 role=automation") != std::string::npos &&
                    read_text(runtime / "authority" / "record-count") == "2\n",
                "authorized mock principal was not committed to the ledger");

        const std::string peer_key(64U, '4');
        const CommandResult accepted =
            run_control(iotox, runtime, {"transport-peer-accept", peer_key});
        require(accepted.exit_code == 0 && accepted.output == "friend-number=0\n",
                "transport-peer-accept failed");

        const CommandResult peers = run_control(iotox, runtime, {"peers"});
        require(peers.exit_code == 0 &&
                    peers.output.find("friend-number=0 public-key=" + peer_key) != std::string::npos,
                "peer list did not expose accepted transport peer");
        require(std::filesystem::exists(runtime / "peers" / peer_key / "connection"),
                "ratox-style peer projection was not materialized");
        const CommandResult alias_set = run_control(
            iotox, runtime, {"peer-alias-set", "workstation", peer_key});
        const CommandResult alias_retry = run_control(
            iotox, runtime,
            {"peer-alias-set", "workstation", "key:" + peer_key});
        const CommandResult aliases = run_control(
            iotox, runtime, {"peer-aliases"});
        require(
            alias_set.exit_code == 0 &&
                alias_set.output.find("generation=1\nchanged=1\n") !=
                    std::string::npos &&
                alias_retry.exit_code == 0 &&
                alias_retry.output.find("generation=1\nchanged=0\n") !=
                    std::string::npos &&
                aliases.exit_code == 0 &&
                aliases.output.find(
                    "alias=workstation public-key=" + peer_key + "\n") !=
                    std::string::npos,
            "device-signed peer alias set/idempotence/list failed");

        const std::vector<std::uint8_t> piped_name{
            'I', 'o', 'T', 'o', 'x', ' ', 'P', 'r', 'o', 'c', 'e', 's', 's'};
        const CommandResult set_name = run_control_with_input(
            iotox, runtime, {"profile-name-stdin"}, piped_name);
        require(set_name.exit_code == 0 && set_name.output == "profile-name-updated\n",
                "profile-name-stdin failed");
        const CommandResult binary_status_message = run_control(
            iotox, runtime, {"profile-status-message-hex", "6F6E650062696E617279"});
        require(binary_status_message.exit_code == 0 &&
                    read_text(runtime / "self" / "status-message") ==
                        std::string("one\0binary", 10U),
                "profile-status-message-hex did not preserve embedded NUL bytes");
        const CommandResult set_status_message = run_control(
            iotox, runtime,
            {"profile-status-message", "one", "binary", "just", "werx"});
        require(set_status_message.exit_code == 0 &&
                    set_status_message.output == "profile-status-message-updated\n",
                "profile-status-message failed");
        const CommandResult set_status =
            run_control(iotox, runtime, {"profile-status", "busy"});
        require(set_status.exit_code == 0 &&
                    set_status.output == "profile-status-updated\n",
                "profile-status failed");
        const CommandResult profile = run_control(iotox, runtime, {"profile"});
        require(profile.exit_code == 0 &&
                    profile.output.find("name=IoTox Process") != std::string::npos &&
                    profile.output.find("status-message=one binary just werx") !=
                        std::string::npos &&
                    profile.output.find("status=busy") != std::string::npos,
                "profile mutations were not observable through the one binary");
        require(read_text(runtime / "self" / "name") == "IoTox Process",
                "runtime self-name projection was not updated");

        write_fifo_record(first, runtime / "self" / "name-set", "IoTox FIFO\n");
        write_fifo_record(
            first, runtime / "self" / "status-message-set", "ordinary profile lane\n");
        write_fifo_record(first, runtime / "self" / "status-set", "away\n");
        require(wait_for_text(runtime / "self" / "name", "IoTox FIFO") &&
                    wait_for_text(
                        runtime / "self" / "status-message", "ordinary profile lane") &&
                    wait_for_text(runtime / "self" / "status", "away\n"),
                "ordinary profile FIFOs did not reconcile provider projections");
        const CommandResult fifo_profile =
            run_control(iotox, runtime, {"profile"});
        require(fifo_profile.exit_code == 0 &&
                    fifo_profile.output.find("name=IoTox FIFO") != std::string::npos &&
                    fifo_profile.output.find("status-message=ordinary profile lane") !=
                        std::string::npos &&
                    fifo_profile.output.find("status=away") != std::string::npos,
                "ordinary profile FIFOs did not converge on structured control truth");

        const std::vector<std::uint8_t> piped_action{
            'p', 'r', 'o', 'c', 'e', 's', 's', 0U, 'w', 'a', 'v', 'e', 's', '\n'};
        const CommandResult action = run_control_with_input(
            iotox, runtime, {"action-stdin", "workstation"}, piped_action);
        require(action.exit_code == 0 && action.output == "message-id=0\n",
                "one-binary binary-safe action-stdin failed");
        const CommandResult typing =
            run_control(iotox, runtime, {"typing", "alias:workstation", "on"});
        require(typing.exit_code == 0 && typing.output == "typing-on\n",
                "one-binary typing update failed");

        const std::filesystem::path message_journal =
            runtime / "peers" / peer_key / "messages";
        const auto text_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool saw_text_lifecycle = false;
        while (std::chrono::steady_clock::now() < text_deadline &&
               !saw_text_lifecycle) {
            if (std::filesystem::exists(message_journal)) {
                const std::string messages = read_text(message_journal);
                saw_text_lifecycle =
                    messages.find("direction=outgoing kind=action message-id=0") !=
                        std::string::npos &&
                    messages.find("direction=incoming kind=action") !=
                        std::string::npos &&
                    messages.find("direction=receipt kind=action message-id=0") !=
                        std::string::npos &&
                    messages.find("body=process\\x00waves\\n") != std::string::npos;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(saw_text_lifecycle,
                "Tox text send echo and receipt were not journaled as action messages");
        const CommandResult peer_messages =
            run_control(iotox, runtime, {"peer-messages", peer_key});
        require(peer_messages.exit_code == 0 &&
                    peer_messages.output.find("direction=outgoing kind=action") !=
                        std::string::npos,
                "peer-messages did not expose the private journal");
        const CommandResult peer_watch = run_control(
            iotox, runtime,
            {"--from-start", "--watch-ms", "100", "peer-watch", peer_key});
        require(peer_watch.exit_code == 0 &&
                    peer_watch.output.find("direction=receipt kind=action") !=
                        std::string::npos,
                "peer-watch did not follow the existing journal from byte zero");

        const std::filesystem::path peer_directory =
            runtime / "peers" / peer_key;
        const std::filesystem::path message_fifo = peer_directory / "message";
        const std::filesystem::path message_events =
            peer_directory / "message-events";
        require(read_text(peer_directory / "message.help").find(
                    "message=normal Tox text FIFO") != std::string::npos,
                "ratox-style human text help did not publish its normal lane");
        const std::string fifo_message{"ratox\0lives\r\n", 13U};
        write_fifo_record(first, message_fifo, fifo_message);

        const auto fifo_text_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool saw_fifo_text_lifecycle = false;
        std::string ingress_text;
        while (std::chrono::steady_clock::now() < fifo_text_deadline &&
               !saw_fifo_text_lifecycle) {
            if (std::filesystem::exists(message_events)) {
                ingress_text = read_text(message_events);
            }
            const std::string messages = read_text(message_journal);
            saw_fifo_text_lifecycle =
                ingress_text.find(
                    "ingress-sequence=1 kind=normal disposition=accepted error-code=0 message-id=1") !=
                    std::string::npos &&
                ingress_text.find(
                    "payload-bytes=12 body=ratox\\x00lives\\r") !=
                    std::string::npos &&
                messages.find(
                    "direction=outgoing kind=normal message-id=1") !=
                    std::string::npos &&
                messages.find("direction=incoming kind=normal") !=
                    std::string::npos &&
                messages.find(
                    "direction=receipt kind=normal message-id=1") !=
                    std::string::npos &&
                messages.find("body=ratox\\x00lives\\r") !=
                    std::string::npos;
            if (!saw_fifo_text_lifecycle) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(saw_fifo_text_lifecycle,
                "literal ratox-style message FIFO write did not reach c-toxcore acceptance, echo, and receipt\n--- ingress ---\n" +
                    ingress_text + "\n--- messages ---\n" +
                    read_text(message_journal));
        const CommandResult peer_message_events =
            run_control(iotox, runtime, {"peer-message-events", peer_key});
        require(peer_message_events.exit_code == 0 &&
                    peer_message_events.output.find(
                        "kind=normal disposition=accepted") !=
                        std::string::npos,
                "peer-message-events did not expose local FIFO admission evidence");

        const std::filesystem::path protocol_journal =
            runtime / "peers" / peer_key / "protocol";
        const auto protocol_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool saw_protocol = false;
        while (std::chrono::steady_clock::now() < protocol_deadline &&
               !saw_protocol) {
            if (std::filesystem::exists(protocol_journal)) {
                const std::string protocol = read_text(protocol_journal);
                saw_protocol =
                    protocol.find("direction=outgoing protocol=1.0 type=hello") !=
                        std::string::npos &&
                    protocol.find("direction=incoming protocol=1.0 type=hello") !=
                        std::string::npos &&
                    protocol.find("direction=outgoing protocol=1.0 type=capabilities") !=
                        std::string::npos &&
                    protocol.find("direction=incoming protocol=1.0 type=capabilities") !=
                        std::string::npos &&
                    protocol.find("direction=outgoing protocol=1.0 type=authority-challenge") !=
                        std::string::npos &&
                    protocol.find("direction=incoming protocol=1.0 type=authority-challenge") !=
                        std::string::npos &&
                    protocol.find("direction=outgoing protocol=1.0 type=authority-proof") !=
                        std::string::npos &&
                    protocol.find("direction=incoming protocol=1.0 type=authority-proof") !=
                        std::string::npos &&
                    protocol.find("payload-bytes=64") != std::string::npos &&
                    protocol.find("payload-bytes=160") != std::string::npos &&
                    protocol.find("payload-bytes=256") != std::string::npos;
            }
            if (!saw_protocol) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        const std::string observed_protocol =
            std::filesystem::exists(protocol_journal)
                ? read_text(protocol_journal)
                : std::string{"<protocol journal absent>\n"};
        require(saw_protocol,
                "canonical session and signed directional authority exchange were not journaled\n--- protocol journal ---\n" +
                    observed_protocol);
        const CommandResult peer_protocol =
            run_control(iotox, runtime, {"peer-protocol", peer_key});
        require(peer_protocol.exit_code == 0 &&
                    peer_protocol.output.find("type=hello") != std::string::npos &&
                    peer_protocol.output.find("type=capabilities") != std::string::npos &&
                    peer_protocol.output.find("type=authority-challenge") != std::string::npos &&
                    peer_protocol.output.find("type=authority-proof") != std::string::npos,
                "peer-protocol did not expose the decoded IoTox authority session");
        const CommandResult peer_protocol_watch = run_control(
            iotox, runtime,
            {"--from-start", "--watch-ms", "100", "peer-protocol-watch", peer_key});
        require(peer_protocol_watch.exit_code == 0 &&
                    peer_protocol_watch.output.find("direction=incoming") !=
                        std::string::npos,
                "peer-protocol-watch did not follow the decoded journal");

        const CommandResult sessions = run_control(iotox, runtime, {"sessions"});
        require(sessions.exit_code == 0 &&
                    sessions.output.find("friend-number=0") != std::string::npos &&
                    sessions.output.find("public-key=" + peer_key) != std::string::npos &&
                    sessions.output.find("state=confirmed") != std::string::npos &&
                    sessions.output.find("application-ready=1") != std::string::npos &&
                    sessions.output.find("negotiated-protocol=1.0") != std::string::npos &&
                    sessions.output.find("authorization-ledger-v1") != std::string::npos,
                "sessions did not expose the transcript-confirmed authority-capable session");
        CommandResult session;
        const auto session_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool session_complete = false;
        while (std::chrono::steady_clock::now() < session_deadline &&
               !session_complete) {
            session = run_control(iotox, runtime, {"session", peer_key});
            session_complete =
                session.exit_code == 0 &&
                session.output.find("hello-sent=1") != std::string::npos &&
                session.output.find("hello-received=1") != std::string::npos &&
                session.output.find("confirmation-sent=1") != std::string::npos &&
                session.output.find("confirmation-received=1") != std::string::npos &&
                session.output.find("application-ready=1") != std::string::npos &&
                session.output.find("negotiated-compatible=1") != std::string::npos &&
                session.output.find("online-epoch=1") != std::string::npos &&
                session.output.find("hello-send-attempts=2") != std::string::npos &&
                session.output.find("confirmation-send-attempts=2") !=
                    std::string::npos &&
                session.output.find("last-hello-send-error=") ==
                    std::string::npos &&
                session.output.find("last-confirmation-send-error=") ==
                    std::string::npos &&
                session.output.find("authorization=separate-authority-session") !=
                    std::string::npos;
            if (!session_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(
            session_complete,
            "session did not converge after recovered transport pressure while preserving the separate authority contract\n--- session ---\n" +
                session.output);

        CommandResult authority_session;
        const auto authority_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool authority_complete = false;
        while (std::chrono::steady_clock::now() < authority_deadline &&
               !authority_complete) {
            authority_session = run_control(iotox, runtime, {"authority-session", peer_key});
            authority_complete =
                authority_session.exit_code == 0 &&
                authority_session.output.find("verifier-state=authorized") !=
                    std::string::npos &&
                authority_session.output.find("remote-authorized=1") !=
                    std::string::npos &&
                authority_session.output.find("claimant-state=proof-sent") !=
                    std::string::npos &&
                authority_session.output.find("challenge-send-attempts=2") !=
                    std::string::npos &&
                authority_session.output.find("proof-send-attempts=2") !=
                    std::string::npos &&
                authority_session.output.find("last-proof-send-error=") ==
                    std::string::npos;
            if (!authority_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(authority_complete &&
                    authority_session.output.find(
                        "remote-principal=" + mock_authority_public_key) !=
                        std::string::npos &&
                    authority_session.output.find("remote-role=automation") !=
                        std::string::npos &&
                    authority_session.output.find(
                        "remote-capabilities=read.telemetry,write.settings,actuate") !=
                        std::string::npos &&
                    authority_session.output.find(
                        "local-claimant-principal=" + device_public_key) !=
                        std::string::npos,
                "confirmed peers did not complete both stable-principal authority directions\n--- authority session ---\n" +
                    authority_session.output);
        const CommandResult authority_sessions =
            run_control(iotox, runtime, {"authority-sessions"});
        require(authority_sessions.exit_code == 0 &&
                    authority_sessions.output.find("remote-authorized=1") !=
                        std::string::npos &&
                    authority_sessions.output.find(
                        "local-claimant-principal=" + device_public_key) !=
                        std::string::npos,
                "authority session list did not expose both signed directions");
        const std::filesystem::path peer_authority =
            runtime / "peers" / peer_key / "iotox" / "authority";
        require(read_text(peer_authority / "remote-authorized") == "1\n" &&
                    read_text(peer_authority / "remote-principal") ==
                        mock_authority_public_key + "\n" &&
                    read_text(peer_authority / "remote-role") == "automation\n" &&
                    read_text(peer_authority / "claimant-state") == "proof-sent\n" &&
                    read_text(peer_authority / "local-claimant-principal") ==
                        device_public_key + "\n" &&
                    read_text(peer_authority / "challenge-send-attempts") == "2\n" &&
                    read_text(peer_authority / "proof-send-attempts") == "2\n",
                "ratox-style authority projection did not commit both directions");
        std::string authority_audit_text;
        const auto peer_operation_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool peer_operation_complete = false;
        while (std::chrono::steady_clock::now() < peer_operation_deadline &&
               !peer_operation_complete) {
            if (std::filesystem::exists(authority_audit)) {
                authority_audit_text = read_text(authority_audit);
                peer_operation_complete =
                    authority_audit_text.find(
                        "agent-proof-verified principal=" + device_public_key) !=
                        std::string::npos &&
                    authority_audit_text.find(
                        "preauthority-device-describe-denied") !=
                        std::string::npos &&
                    authority_audit_text.find(
                        "authorized-device-describe-succeeded principal=" +
                        device_public_key + " revision=" +
                        product_identity.revision_number) !=
                        std::string::npos &&
                    authority_audit_text.find(
                        "authorized-device-describe-duplicate-replayed-exact") !=
                        std::string::npos &&
                    authority_audit_text.find(
                        "authorized-profile-status-succeeded desired=away observed=away") !=
                        std::string::npos &&
                    authority_audit_text.find(
                        "authorized-profile-status-duplicate-replayed-exact") !=
                        std::string::npos &&
                    count_occurrences(
                        authority_audit_text,
                        "self-status-set value=1") == 2U &&
                    count_occurrences(
                        authority_audit_text,
                        "command-result-sendq correlation=") >= 2U;
            }
            if (!peer_operation_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(peer_operation_complete,
                "the exact peer did not verify authority, complete read and desired-state commands, and receive exact frozen result replays across SENDQ pressure\n--- authority audit ---\n" +
                    authority_audit_text);
        const CommandResult remotely_mutated_profile =
            run_control(iotox, runtime, {"profile"});
        require(
            remotely_mutated_profile.exit_code == 0 &&
                remotely_mutated_profile.output.find("status=away") !=
                    std::string::npos,
            "authorized profile.status.set did not converge the real provider read-back");

        const std::string command_protocol = read_text(protocol_journal);
        require(
            command_protocol.find(
                "direction=incoming protocol=1.0 type=command") !=
                std::string::npos &&
                command_protocol.find(
                    "direction=outgoing protocol=1.0 type=command-result") !=
                std::string::npos &&
                command_protocol.find("payload-bytes=8") !=
                std::string::npos &&
                command_protocol.find("payload-bytes=80") !=
                std::string::npos,
            "capability-gated device.describe and its frozen result were not committed to the decoded protocol journal");

        const std::filesystem::path command_fifo = peer_directory / "command";
        const std::filesystem::path command_events =
            peer_directory / "command-events";
        require(read_text(peer_directory / "command.help").find(
                    "operation=device.describe") != std::string::npos,
                "ratox-style command help did not publish its executable operation");

        write_fifo_record(first, command_fifo, "device.describe\n");
        std::string command_event_text;
        const auto command_event_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool fifo_command_admitted = false;
        while (std::chrono::steady_clock::now() < command_event_deadline &&
               !fifo_command_admitted) {
            if (std::filesystem::exists(command_events)) {
                command_event_text = read_text(command_events);
                fifo_command_admitted =
                    command_event_text.find("operation=device.describe") !=
                        std::string::npos &&
                    command_event_text.find("disposition=admitted") !=
                        std::string::npos &&
                    command_event_text.find("error-code=0") !=
                        std::string::npos &&
                    command_event_text.find("sender-epoch=0") ==
                        std::string::npos &&
                    command_event_text.find("message-id=0") ==
                        std::string::npos &&
                    command_event_text.find("state=reserved") !=
                        std::string::npos;
            }
            if (!fifo_command_admitted) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(fifo_command_admitted,
                "literal per-peer FIFO write did not enter the delayed durable command path before injected SENDQ pressure\n--- command events ---\n" +
                    command_event_text);

        CommandResult peer_description;
        const auto description_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool description_complete = false;
        while (std::chrono::steady_clock::now() < description_deadline &&
               !description_complete) {
            peer_description =
                run_control(iotox, runtime, {"peer-description", peer_key});
            description_complete =
                peer_description.exit_code == 0 &&
                peer_description.output.find("state=succeeded") !=
                    std::string::npos &&
                peer_description.output.find("send-attempts=2") !=
                    std::string::npos &&
                peer_description.output.find(
                    "device-principal=" + mock_authority_public_key) !=
                    std::string::npos &&
                peer_description.output.find(
                    "version=" + product_identity.version) !=
                    std::string::npos &&
                peer_description.output.find(
                    "revision=" + product_identity.revision) !=
                    std::string::npos &&
                peer_description.output.find("protocol=1.0") !=
                    std::string::npos;
            if (!description_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(description_complete,
                "one-binary device.describe did not complete with exact retry and bound principal\nexit-code=" +
                    std::to_string(peer_description.exit_code) +
                    "\n--- peer description ---\n" + peer_description.output);
        const std::string durable_sender_epoch =
            extract_field(peer_description.output, "sender-epoch");
        const std::string durable_request_message_id =
            extract_field(peer_description.output, "request-message-id");
        require(!durable_sender_epoch.empty() && durable_sender_epoch != "0" &&
                    !durable_request_message_id.empty() &&
                    durable_request_message_id != "0" &&
                    peer_description.output.find("receipt-stage=received") !=
                        std::string::npos,
                "device.describe did not expose its durable identity and receipt");

        const CommandResult summary_issue = run_control(
            iotox, runtime, {"command", peer_key, "system.summary"});
        const std::string summary_sender_epoch =
            extract_field(summary_issue.output, "sender-epoch");
        const std::string summary_message_id =
            extract_field(summary_issue.output, "message-id");
        require(summary_issue.exit_code == 0 &&
                    !summary_sender_epoch.empty() &&
                    summary_sender_epoch != "0" &&
                    !summary_message_id.empty() && summary_message_id != "0" &&
                    summary_issue.output.find("operation=system.summary") !=
                        std::string::npos,
                "one-binary system.summary did not commit a durable outgoing request");
        CommandResult summary_record;
        const auto summary_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool summary_complete = false;
        while (std::chrono::steady_clock::now() < summary_deadline &&
               !summary_complete) {
            summary_record = run_control(
                iotox, runtime,
                {"command-record", "outgoing", peer_key,
                 summary_sender_epoch, summary_message_id});
            summary_complete =
                summary_record.exit_code == 0 &&
                summary_record.output.find("lifecycle=succeeded") !=
                    std::string::npos &&
                summary_record.output.find("operation=system.summary") !=
                    std::string::npos &&
                summary_record.output.find("receipt-delivery=observed") !=
                    std::string::npos &&
                summary_record.output.find("result-delivery=observed") !=
                    std::string::npos &&
                summary_record.output.find("result-bytes=97") !=
                    std::string::npos;
            if (!summary_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(summary_complete,
                "separate-process system.summary did not receive and durably project its exact result\n--- record ---\n" +
                    summary_record.output);

        const CommandResult mutation_issue = run_control(
            iotox, runtime,
            {"command", peer_key, "profile.status.set", "busy", "high"});
        const std::string mutation_sender_epoch =
            extract_field(mutation_issue.output, "sender-epoch");
        const std::string mutation_message_id =
            extract_field(mutation_issue.output, "message-id");
        require(
            mutation_issue.exit_code == 0 &&
                !mutation_sender_epoch.empty() &&
                mutation_sender_epoch != "0" &&
                !mutation_message_id.empty() && mutation_message_id != "0" &&
                mutation_issue.output.find(
                    "operation=profile.status.set") != std::string::npos &&
                mutation_issue.output.find("desired-status=busy") !=
                    std::string::npos &&
                mutation_issue.output.find("priority=high") !=
                    std::string::npos,
            "one-binary profile.status.set did not commit its exact desired state\n--- issue ---\n" +
                mutation_issue.output);
        CommandResult mutation_record;
        const auto mutation_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool mutation_complete = false;
        while (std::chrono::steady_clock::now() < mutation_deadline &&
               !mutation_complete) {
            mutation_record = run_control(
                iotox, runtime,
                {"command-record", "outgoing", peer_key,
                 mutation_sender_epoch, mutation_message_id});
            mutation_complete =
                mutation_record.exit_code == 0 &&
                mutation_record.output.find("lifecycle=succeeded") !=
                    std::string::npos &&
                mutation_record.output.find(
                    "operation=profile.status.set") != std::string::npos &&
                mutation_record.output.find("desired-status=busy") !=
                    std::string::npos &&
                mutation_record.output.find("observed-status=busy") !=
                    std::string::npos &&
                mutation_record.output.find("converged=1") !=
                    std::string::npos &&
                mutation_record.output.find("ownership-epoch=1") !=
                    std::string::npos &&
                mutation_record.output.find("result-bytes=65") !=
                    std::string::npos;
            if (!mutation_complete) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(
            mutation_complete,
            "profile.status.set did not retain exact provider convergence evidence\n--- record ---\n" +
                mutation_record.output);
        require(
            read_text(authority_audit).find(
                "mock-profile-status-set desired=busy applications=1") !=
                std::string::npos,
            "mock provider did not observe exactly one outgoing desired-state application");

        const CommandResult missing_mutation_argument = run_control(
            iotox, runtime,
            {"command", peer_key, "profile.status.set"});
        require(
            missing_mutation_argument.exit_code == 2 &&
                missing_mutation_argument.output.find(
                    "requires available, away, or busy") !=
                    std::string::npos,
            "CLI did not reject profile.status.set without a desired value");
        const CommandResult expiring_mutation = run_control(
            iotox, runtime,
            {"command", peer_key, "profile.status.set", "busy", "normal",
             "500"});
        require(
            expiring_mutation.exit_code == 4 &&
                expiring_mutation.output.find(
                    "mutating commands do not accept expiry") !=
                    std::string::npos,
            "profile.status.set admitted an ambiguous post-start expiry");

        const CommandResult cancellable_issue = run_control(
            iotox, runtime,
            {"command", peer_key, "system.summary", "high"});
        const std::string cancellable_epoch =
            extract_field(cancellable_issue.output, "sender-epoch");
        const std::string cancellable_message =
            extract_field(cancellable_issue.output, "message-id");
        require(cancellable_issue.exit_code == 0 &&
                    cancellable_issue.output.find("lifecycle=reserved") !=
                        std::string::npos &&
                    cancellable_issue.output.find("priority=high") !=
                        std::string::npos &&
                    cancellable_issue.output.find("request-attempts=0") !=
                        std::string::npos,
                "durable command did not expose its pre-send cancellation window\n--- issue ---\n" +
                    cancellable_issue.output);
        const CommandResult cancelled = run_control(
            iotox, runtime,
            {"command-cancel", peer_key, cancellable_epoch,
             cancellable_message});
        require(cancelled.exit_code == 0 &&
                    cancelled.output.find("lifecycle=cancelled") !=
                        std::string::npos &&
                    cancelled.output.find("request-attempts=0") !=
                        std::string::npos,
                "durable command cancellation did not commit before first attempt\n--- cancel ---\n" +
                    cancelled.output);
        const CommandResult untrusted_ttl = run_control(
            iotox, runtime,
            {"command", peer_key, "system.summary", "normal", "5000"});
        require(untrusted_ttl.exit_code != 0 &&
                    untrusted_ttl.output.find("trusted") !=
                        std::string::npos,
                "TTL admission did not fail closed without explicit wall-clock trust");
        const auto summary_projection =
            runtime / "commands" / "outgoing" / peer_key /
            (summary_sender_epoch + "-" + summary_message_id) / "result";
        const auto summary_projection_deadline =
            process_test_deadline(std::chrono::seconds(5));
        while (!std::filesystem::exists(summary_projection) &&
               std::chrono::steady_clock::now() <
                   summary_projection_deadline) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        const std::string summary_text = read_text(summary_projection);
        require(summary_text.find("operation=system.summary") !=
                    std::string::npos &&
                    summary_text.find("outcome=succeeded") !=
                        std::string::npos &&
                    summary_text.find("health=healthy") != std::string::npos &&
                    summary_text.find("uptime-minutes=720") !=
                        std::string::npos &&
                    summary_text.find("memory-total-64mib=64") !=
                        std::string::npos &&
                    summary_text.find("load-milli=300") !=
                        std::string::npos &&
                    summary_text.find("process-count=42") !=
                        std::string::npos,
                "ratox-style system.summary result projection lost typed telemetry");

        const CommandResult command_store =
            run_control(iotox, runtime, {"command-store"});
        const std::string local_sender_epoch =
            extract_field(command_store.output, "local-sender-epoch");
        require(command_store.exit_code == 0 &&
                    command_store.output.find(
                        "format=IoTox-Durable-Commands-v3") !=
                        std::string::npos &&
                    !local_sender_epoch.empty() && local_sender_epoch != "0" &&
                    command_store.output.find("direction=incoming") !=
                        std::string::npos &&
                    command_store.output.find("direction=outgoing") !=
                        std::string::npos &&
                    command_store.output.find("lifecycle=succeeded") !=
                        std::string::npos &&
                    command_store.output.find(
                        "operation=profile.status.set") !=
                        std::string::npos &&
                    command_store.output.find("desired-status=away") !=
                        std::string::npos &&
                    command_store.output.find("observed-status=away") !=
                        std::string::npos &&
                    command_store.output.find("converged=1") !=
                        std::string::npos &&
                    command_store.output.find("lifecycle=failed") !=
                        std::string::npos,
                "one-binary command-store did not expose durable incoming and outgoing history\n--- command store ---\n" +
                    command_store.output);
        const CommandResult command_record = run_control(
            iotox, runtime,
            {"command-record", "outgoing", peer_key, durable_sender_epoch,
             durable_request_message_id});
        require(command_record.exit_code == 0 &&
                    command_record.output.find("peer=" + peer_key) !=
                        std::string::npos &&
                    command_record.output.find("direction=outgoing") !=
                        std::string::npos &&
                    command_record.output.find("lifecycle=succeeded") !=
                        std::string::npos &&
                    command_record.output.find("receipt-delivery=observed") !=
                        std::string::npos &&
                    command_record.output.find("result-delivery=observed") !=
                        std::string::npos &&
                    command_record.output.find("request-bytes=49") !=
                        std::string::npos &&
                    command_record.output.find("receipt-bytes=49") !=
                        std::string::npos &&
                    command_record.output.find("result-bytes=121") !=
                        std::string::npos,
                "one-binary command-record did not retrieve the exact durable request\n--- command record ---\n" +
                    command_record.output);
        const std::filesystem::path command_store_path =
            state.parent_path() / "commands.store";
        struct stat command_store_metadata {};
        require(::stat(command_store_path.c_str(), &command_store_metadata) == 0 &&
                    S_ISREG(command_store_metadata.st_mode) &&
                    (command_store_metadata.st_mode & 077U) == 0U,
                "durable command store was not a private regular file");

        const std::filesystem::path description_directory =
            runtime / "peers" / peer_key / "iotox" / "description";
        require(read_text(description_directory / "state") == "succeeded\n" &&
                    read_text(description_directory / "send-attempts") == "2\n" &&
                    read_text(description_directory / "device-principal") ==
                        mock_authority_public_key + "\n" &&
                    read_text(description_directory / "version") ==
                        product_identity.version + "\n" &&
                    read_text(description_directory / "revision") ==
                        product_identity.revision + "\n" &&
                    read_text(runtime / "peers" / peer_key / "description").find(
                        "state=succeeded") != std::string::npos,
                "ratox-style description projection did not commit the completed operation");
        const std::string completed_audit = read_text(authority_audit);
        require(completed_audit.find(
                    "mock-device-describe-response-sent") !=
                    std::string::npos,
                "the exact peer fixture did not answer the local device.describe request");

        const CommandResult authorized_status =
            run_control(iotox, runtime, {"status"});
        require(authorized_status.exit_code == 0 &&
                    authorized_status.output.find("authority-session-count=1") !=
                        std::string::npos &&
                    authorized_status.output.find("authorized-peer-count=1") !=
                        std::string::npos &&
                    authorized_status.output.find("awaiting-authority-proof-count=0") !=
                        std::string::npos &&
                    authorized_status.output.find("command-fifo-running=1") !=
                        std::string::npos &&
                    authorized_status.output.find("command-fifo-count=1") !=
                        std::string::npos &&
                    authorized_status.output.find("command-fifo-record-count=1") !=
                        std::string::npos &&
                    authorized_status.output.find("command-fifo-rejected-count=0") !=
                        std::string::npos,
                "status did not account for the completed authority session and literal FIFO ingress");

        const CommandResult peer_session =
            run_control(iotox, runtime, {"peer-session", peer_key});
        require(peer_session.exit_code == 0 &&
                    peer_session.output.find("state=confirmed") !=
                        std::string::npos &&
                    peer_session.output.find("application-ready=1") !=
                        std::string::npos,
                "peer-session did not expose the ratox-style runtime projection");
        const std::filesystem::path peer_iotox =
            runtime / "peers" / peer_key / "iotox";
        require(read_text(peer_iotox / "hello-compatible") == "1\n" &&
                    read_text(peer_iotox / "transcript-confirmed") == "1\n" &&
                    read_text(peer_iotox / "established") == "1\n" &&
                    read_text(peer_iotox / "application-ready") == "1\n" &&
                    read_text(peer_iotox / "protocol") == "1.0\n",
                "ratox-style IoTox session files did not publish the confirmed contract");
        const CommandResult session_status = run_control(iotox, runtime, {"status"});
        require(session_status.exit_code == 0 &&
                    session_status.output.find("protocol-session-count=1") !=
                        std::string::npos &&
                    session_status.output.find("compatible-protocol-session-count=1") !=
                        std::string::npos &&
                    session_status.output.find("established-protocol-session-count=1") !=
                        std::string::npos,
                "status did not account for the established IoTox session");

        const CommandResult application_health =
            run_control(iotox, runtime, {"route-health", peer_key});
        require(
            application_health.exit_code == 0 &&
                application_health.output.find("application=responsive\n") !=
                    std::string::npos &&
                application_health.output.find(
                    "application-rtt-us=not-sampled\n") ==
                    std::string::npos &&
                application_health.output.find("application-error=none\n") !=
                    std::string::npos,
            "route-health peer heartbeat did not traverse the one-binary CLI and confirmed session\n--- route health ---\n" +
                application_health.output);

        const CommandResult watched_health = run_control(
            iotox, runtime,
            {"--watch-ms", "650", "--sample-ms", "100",
             "--failure-samples", "3", "--recovery-samples", "2",
             "route-health-watch", peer_key});
        require(
            watched_health.exit_code == 0 &&
                count_occurrences(
                    watched_health.output, "sample-index=") >= 2U &&
                watched_health.output.find(
                    "monitor-local-boundary-state=unknown\n") !=
                    std::string::npos &&
                watched_health.output.find(
                    "monitor-application-state=healthy\n") !=
                    std::string::npos &&
                watched_health.output.find(
                    "monitor-failure-samples=3\n") !=
                    std::string::npos &&
                watched_health.output.find(
                    "monitor-recovery-samples=2\n") !=
                    std::string::npos &&
                watched_health.output.find(
                    "monitor-semantics=observation-only-independent-latches-no-carrier-or-session-mutation\n") !=
                    std::string::npos,
            "route-health-watch did not preserve independent hysteretic application truth\n--- route health watch ---\n" +
                watched_health.output);

        const CommandResult bounded_health = run_control(
            iotox, runtime,
            {"--watch-ms", "150", "--sample-ms", "600000",
             "route-health-watch"});
        require(
            bounded_health.exit_code == 0 &&
                count_occurrences(bounded_health.output, "sample-index=") == 1U,
            "finite route-health-watch slept until its sampling cadence instead of its watch deadline\n--- bounded route health watch ---\n" +
                bounded_health.output);

        // An explicit operator retry remains idempotent and reuses the same frozen
        // epoch records. It is tested only after automatic SENDQ recovery has been
        // observed at exactly two attempts for each handshake record.
        const CommandResult hello =
            run_control(iotox, runtime, {"hello", peer_key});
        require(hello.exit_code == 0 &&
                    hello.output == "canonical-hello-queued\n",
                "canonical IoTox HELLO retry failed");
        const CommandResult confirm =
            run_control(iotox, runtime, {"confirm", peer_key});
        require(confirm.exit_code == 0 &&
                    confirm.output == "transcript-confirmation-queued\n",
                "canonical IoTox transcript confirmation failed exit=" +
                    std::to_string(confirm.exit_code) +
                    "\n--- output ---\n" + confirm.output);
        const CommandResult retried_session =
            run_control(iotox, runtime, {"session", peer_key});
        require(retried_session.exit_code == 0 &&
                    retried_session.output.find("state=confirmed") !=
                        std::string::npos &&
                    retried_session.output.find("hello-send-attempts=3") !=
                        std::string::npos &&
                    retried_session.output.find("confirmation-send-attempts=3") !=
                        std::string::npos,
                "explicit frozen-record retries changed or closed the session");

        const std::filesystem::path file_send_fifo =
            peer_directory / "file-send";
        const std::filesystem::path file_receive_fifo =
            peer_directory / "file-receive";
        const std::filesystem::path file_control_fifo =
            peer_directory / "file-control";
        const std::filesystem::path file_events =
            peer_directory / "file-events";
        const std::string file_help = read_text(peer_directory / "file.help");
        require(file_help.find("FIFO names local paths; file bytes never pass") !=
                    std::string::npos &&
                    file_help.find("pause|resume|cancel") != std::string::npos,
                "ratox-style finite-file contract was not published");

        // Kernel FIFO acceptance is deliberately not semantic success. Prove a
        // malformed path is rejected in the file journal, then submit a real
        // finite regular file through the same ordinary-write surface.
        write_fifo_record(first, file_send_fifo, "relative-send.bin\n");
        const auto bad_file_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool saw_bad_file = false;
        while (std::chrono::steady_clock::now() < bad_file_deadline &&
               !saw_bad_file) {
            if (std::filesystem::exists(file_events)) {
                const std::string journal = read_text(file_events);
                saw_bad_file =
                    journal.find("source=local-fifo") != std::string::npos &&
                    journal.find("operation=file-send disposition=rejected") !=
                        std::string::npos &&
                    journal.find("local file path must be absolute") !=
                        std::string::npos;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(saw_bad_file,
                "file-send FIFO did not distinguish kernel acceptance from semantic rejection");

        write_fifo_record(
            first, file_send_fifo, outgoing_source.string() + "\n");

        const auto transfer_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool sent_bytes = false;
        bool saw_offer = false;
        std::uint32_t incoming_file_number = 0U;
        while (std::chrono::steady_clock::now() < transfer_deadline &&
               (!sent_bytes || !saw_offer)) {
            if (std::filesystem::exists(outgoing_capture)) {
                sent_bytes = read_text(outgoing_capture) == "BINARY-JUST-WERX";
            }
            const CommandResult files = run_control(iotox, runtime, {"files"});
            if (files.exit_code == 0) {
                const std::string marker =
                    "direction=incoming state=offered friend-number=0 file-number=";
                const std::size_t begin = files.output.find(marker);
                if (begin != std::string::npos) {
                    const std::size_t value_begin = begin + marker.size();
                    const std::size_t value_end = files.output.find(' ', value_begin);
                    const std::string value = files.output.substr(
                        value_begin, value_end - value_begin);
                    incoming_file_number = static_cast<std::uint32_t>(std::stoul(value));
                    saw_offer = true;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(sent_bytes, "one-binary outgoing file bytes did not reach toxcore");
        require(saw_offer && incoming_file_number >= (1U << 16U),
                "incoming c-toxcore file handle was not projected with direction encoding");
        const std::filesystem::path incoming_projection =
            runtime / "transfers" /
            ("incoming-0-" + std::to_string(incoming_file_number));
        require(wait_for_text(incoming_projection / "state", "offered\n"),
                "incoming transfer was not atomically projected as offered");

        const std::filesystem::path peer_incoming_projection =
            peer_directory / "files" / "incoming" /
            std::to_string(incoming_file_number);
        require(wait_for_text(peer_incoming_projection / "state", "offered\n"),
                "per-peer finite-file projection did not expose the paused offer");

        const CommandResult structured_offer_pause = run_control(
            iotox, runtime,
            {"file-control", peer_key, std::to_string(incoming_file_number),
             "pause"});
        require(structured_offer_pause.exit_code == 0 &&
                    structured_offer_pause.output.find(
                        "direction=incoming state=offered") != std::string::npos &&
                    structured_offer_pause.output.find("local-paused=1") !=
                        std::string::npos,
                "one-binary structured file-control did not preserve offered admission state");

        // An offer cannot be resumed before IoTox has acquired a private safe
        // destination. The generic file-control FIFO must reject that attempt
        // without losing the offer, then file-receive admits it by path.
        write_fifo_record(
            first, file_control_fifo,
            std::to_string(incoming_file_number) + "\tresume\n");
        const auto unsafe_resume_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool saw_unsafe_resume = false;
        while (std::chrono::steady_clock::now() < unsafe_resume_deadline &&
               !saw_unsafe_resume) {
            const std::string journal = read_text(file_events);
            saw_unsafe_resume =
                journal.find("operation=file-control:resume disposition=rejected") !=
                    std::string::npos &&
                journal.find("use file-receive before RESUME") !=
                    std::string::npos;
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(
            saw_unsafe_resume,
            "file-control FIFO did not reject an incoming offer before a destination was acquired\n--- file-events ---\n" +
                read_text(file_events));
        require(wait_for_text(peer_incoming_projection / "state", "offered\n"),
                "rejected unsafe RESUME destroyed the incoming offer");

        write_fifo_record(
            first, file_receive_fifo,
            std::to_string(incoming_file_number) + "\t" +
                incoming_destination.string() + "\n");

        // Admission occurs after the offer/outgoing-transfer wait above. Give
        // publication its own deadline: reusing transfer_deadline makes a slow
        // but valid offer phase consume the receive budget before RESUME is
        // even issued, which converts scheduling pressure into a false product
        // failure.
        const auto incoming_publication_deadline =
            process_test_deadline(std::chrono::seconds(10));
        bool received_bytes = false;
        while (std::chrono::steady_clock::now() < incoming_publication_deadline &&
               !received_bytes) {
            if (std::filesystem::exists(incoming_destination)) {
                received_bytes = read_text(incoming_destination) == "DATA";
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        if (!received_bytes) {
            const CommandResult failed_status =
                run_control(iotox, runtime, {"status"});
            const CommandResult failed_files =
                run_control(iotox, runtime, {"files"});
            const std::string failed_journal =
                std::filesystem::exists(file_events)
                    ? read_text(file_events)
                    : std::string{"<file-events absent>\n"};
            std::ostringstream nearby;
            nearby << "destination-exists="
                   << (std::filesystem::exists(incoming_destination) ? 1 : 0)
                   << '\n';
            for (const auto &entry : std::filesystem::directory_iterator(directory)) {
                nearby << entry.path().filename().string();
                std::error_code size_error;
                if (entry.is_regular_file(size_error)) {
                    nearby << " bytes=" << entry.file_size(size_error);
                }
                nearby << '\n';
            }
            require(
                false,
                "one-binary incoming file was not safely published\n--- status ---\n" +
                    failed_status.output + "--- files ---\n" +
                    failed_files.output + "--- file-events ---\n" +
                    failed_journal + "--- process directory ---\n" +
                    nearby.str());
        }
        const std::string finite_file_journal = read_text(file_events);
        const CommandResult peer_file_events = run_control(
            iotox, runtime, {"peer-file-events", peer_key});
        // The journal is append-only and provider callbacks remain live while
        // the separate client opens and reads it. Bytes observed directly
        // before the client call must therefore be an exact prefix; requiring
        // equality incorrectly races a legitimate append between the reads.
        require(peer_file_events.exit_code == 0 &&
                    peer_file_events.output.starts_with(finite_file_journal),
                "one-binary peer-file-events did not preserve the exact peer journal prefix");
        require(finite_file_journal.find(
                    "operation=file-send disposition=accepted") !=
                    std::string::npos &&
                    finite_file_journal.find(
                    "operation=file-receive disposition=accepted") !=
                    std::string::npos &&
                    finite_file_journal.find("source=toxcore event=file-offer") !=
                    std::string::npos &&
                    finite_file_journal.find("source=toxcore event=file-chunk") !=
                    std::string::npos,
                "finite-file FIFO admission and toxcore progress were not joined in one peer journal");

        // Incoming publication and toxcore's final outgoing zero-length chunk
        // request are independent asynchronous events. Wait for both transfer
        // directions and the disposable runtime projection to converge instead
        // of assuming that the incoming file becoming visible orders the
        // outgoing completion callback.
        CommandResult finished_files;
        CommandResult transfer_status;
        const auto transfer_convergence_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool transfers_converged = false;
        while (std::chrono::steady_clock::now() < transfer_convergence_deadline &&
               !transfers_converged) {
            finished_files = run_control(iotox, runtime, {"files"});
            transfer_status = run_control(iotox, runtime, {"status"});
            transfers_converged =
                finished_files.exit_code == 0 && finished_files.output.empty() &&
                transfer_status.exit_code == 0 &&
                transfer_status.output.find("incoming-file-offer-count=0") !=
                    std::string::npos &&
                transfer_status.output.find("active-file-transfer-count=0") !=
                    std::string::npos &&
                transfer_status.output.find("file-fifo-running=1") !=
                    std::string::npos &&
                transfer_status.output.find("file-send-fifo-count=1") !=
                    std::string::npos &&
                transfer_status.output.find("file-receive-fifo-count=1") !=
                    std::string::npos &&
                transfer_status.output.find("file-control-fifo-count=1") !=
                    std::string::npos &&
                transfer_status.output.find("file-fifo-record-count=4") !=
                    std::string::npos &&
                transfer_status.output.find("file-fifo-rejected-count=2") !=
                    std::string::npos &&
                std::filesystem::is_empty(runtime / "transfers") &&
                std::filesystem::is_empty(peer_directory / "files" / "incoming") &&
                std::filesystem::is_empty(peer_directory / "files" / "outgoing");
            if (!transfers_converged) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(transfers_converged,
                "status and runtime projection did not converge after both file transfers completed");
        const std::string transfer_events = read_text(runtime / "events");
        require(
            count_occurrences(transfer_events, "kind=file-chunk-request") == 2U,
            "healthy nonterminal file requests were not coalesced while terminal truth was retained");

        const auto event_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool saw_packet = false;
        while (std::chrono::steady_clock::now() < event_deadline && !saw_packet) {
            if (std::filesystem::exists(runtime / "events")) {
                const std::string events = read_text(runtime / "events");
                saw_packet = events.find("kind=lossless-packet") != std::string::npos &&
                             events.find("process-just-werx") == std::string::npos &&
                             events.find("kind=bootstrap") != std::string::npos &&
                             events.find("kind=tcp-relay") != std::string::npos;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(saw_packet,
                "event journal lacked lifecycle events or copied packet payload text");

        // Exercise the process-wide ratox successor entrance after the main
        // peer has consumed all deliberately injected one-shot transport
        // failures. The first complete record is malformed and
        // must journal an explicit keyless rejection. The second is one exact
        // address<TAB>message record and must create a public-key-selected peer
        // through the same owner-thread operation as the typed control path.
        const std::filesystem::path outgoing_request_fifo = runtime / "request";
        require(std::filesystem::is_fifo(outgoing_request_fifo),
                "runtime root did not expose the outgoing request FIFO");
        require(read_text(runtime / "request.help").find(
                    "maximum-record-bytes=998") != std::string::npos,
                "outgoing request help did not freeze the bounded grammar");
        write_fifo_record(first, outgoing_request_fifo, "too-short\n");

        const std::string requested_peer_key(64U, 'C');
        const std::string requested_peer_address =
            requested_peer_key + "010203040206";
        write_fifo_record(
            first, outgoing_request_fifo,
            requested_peer_address + "\tprocess-root-request\n");

        const std::filesystem::path requested_peer_directory =
            runtime / "peers" / requested_peer_key;
        const auto request_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool outgoing_request_committed = false;
        while (std::chrono::steady_clock::now() < request_deadline &&
               !outgoing_request_committed) {
            const std::string lifecycle = read_text(runtime / "friend-events");
            const CommandResult current_status =
                run_control(iotox, runtime, {"status"});
            outgoing_request_committed =
                std::filesystem::exists(requested_peer_directory) &&
                lifecycle.find(
                    "source=local-fifo operation=request-send public-key=" +
                    requested_peer_key + " disposition=requested") !=
                    std::string::npos &&
                lifecycle.find(
                    "source=local-fifo operation=request-send public-key=unknown disposition=rejected") !=
                    std::string::npos &&
                lifecycle.find(
                    "not evidence of remote receipt or acceptance") !=
                    std::string::npos &&
                current_status.exit_code == 0 &&
                current_status.output.find("request-send-fifo-count=1") !=
                    std::string::npos &&
                current_status.output.find(
                    "friendship-fifo-record-count=2") !=
                    std::string::npos &&
                current_status.output.find(
                    "friendship-fifo-rejected-count=1") !=
                    std::string::npos;
            if (!outgoing_request_committed) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(outgoing_request_committed,
                "root request FIFO did not commit exact and malformed lifecycle evidence");

        // Export through the running daemon so this gate crosses the signed
        // recorder, local-control redaction boundary, standalone bundle
        // codec, and no-clobber destination writer. The shareable bytes must
        // not copy either private filesystem coordinates or the Tox address.
        const std::filesystem::path diagnostics_bundle =
            directory / "diagnostics.bundle";
        const CommandResult diagnostics_export = run_control(
            iotox, runtime,
            {"diagnostics-export", diagnostics_bundle.string()});
        require(
            diagnostics_export.exit_code == 0 &&
                diagnostics_export.output.find(
                    "decision=valid-content-free-bundle\n") !=
                    std::string::npos &&
                std::filesystem::is_regular_file(diagnostics_bundle),
            "live diagnostics export did not produce a validated bundle\n--- export ---\n" +
                diagnostics_export.output);
        struct stat diagnostics_metadata {};
        require(
            ::lstat(diagnostics_bundle.c_str(), &diagnostics_metadata) == 0 &&
                S_ISREG(diagnostics_metadata.st_mode) &&
                !S_ISLNK(diagnostics_metadata.st_mode) &&
                diagnostics_metadata.st_nlink == 1 &&
                diagnostics_metadata.st_uid == ::geteuid() &&
                (diagnostics_metadata.st_mode & 0777U) == 0600U,
            "diagnostics export was not one private no-follow regular file");
        const std::string diagnostics_bytes = read_text(diagnostics_bundle);
        require(
            diagnostics_bytes.find(directory.string()) == std::string::npos &&
                diagnostics_bytes.find(runtime.string()) == std::string::npos &&
                diagnostics_bytes.find(state.string()) == std::string::npos &&
                diagnostics_bytes.find(first_address) == std::string::npos &&
                diagnostics_bytes.size() <= 64U * 1024U,
            "shareable diagnostics copied a private coordinate or exceeded its bound");
        const CommandResult diagnostics_inspect = run_capture(
            iotox, {"diagnostics-inspect", diagnostics_bundle.string()});
        require(
            diagnostics_inspect.exit_code == 0 &&
                diagnostics_inspect.output.find(
                    "decision=valid-content-free-bundle\n") !=
                    std::string::npos,
            "standalone diagnostics inspection rejected the live export\n--- inspect ---\n" +
                diagnostics_inspect.output);
        const CommandResult diagnostics_no_clobber = run_control(
            iotox, runtime,
            {"diagnostics-export", diagnostics_bundle.string()});
        require(
            diagnostics_no_clobber.exit_code != 0 &&
                read_text(diagnostics_bundle) == diagnostics_bytes,
            "diagnostics export replaced an existing evidence file");

        const std::filesystem::path requested_peer_remove =
            requested_peer_directory / "remove";
        require(std::filesystem::is_fifo(requested_peer_remove),
                "outgoing request did not project the resulting peer remove FIFO");
        write_fifo_record(first, requested_peer_remove, "remove\n");
        const auto requested_remove_deadline =
            process_test_deadline(std::chrono::seconds(5));
        while (std::filesystem::exists(requested_peer_directory) &&
               std::chrono::steady_clock::now() < requested_remove_deadline) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        require(!std::filesystem::exists(requested_peer_directory),
                "temporary outgoing-request peer was not removed before the main fixture");

        const CommandResult stop = run_control(iotox, runtime, {"stop"});
        require(stop.exit_code == 0 && stop.output == "shutdown-requested\n",
                "iotox stop failed");
        require(wait_for_exit(first, std::chrono::seconds(5)) == 0,
                "first one-binary IoTox lifecycle failed");
        first = -1;
        require(std::filesystem::exists(state) && std::filesystem::file_size(state) > 0U,
                "IoTox did not persist toxcore savedata");

        second = spawn_agent(
            iotox, mock_toxcore, runtime, state, second_log,
            {}, {}, false, true, true, false, {}, false, true);
        wait_for_socket(second, runtime / "control.sock");
        const CommandResult restarted = run_control(iotox, runtime, {"status"});
        require(restarted.exit_code == 0 && extract_address(restarted.output) == first_address,
                "IoTox did not preserve its Tox identity across process restart");
        const CommandResult restored_peers = run_control(iotox, runtime, {"peers"});
        require(restored_peers.exit_code == 0 &&
                    restored_peers.output.find("friend-number=0 public-key=" + peer_key) !=
                        std::string::npos,
                "IoTox did not preserve the Tox friend list across process restart");
        const CommandResult restored_aliases = run_control(
            iotox, runtime, {"peer-aliases"});
        require(
            restored_aliases.exit_code == 0 &&
                restored_aliases.output.find("generation=1\ncount=1\n") !=
                    std::string::npos &&
                restored_aliases.output.find(
                    "alias=workstation public-key=" + peer_key + "\n") !=
                    std::string::npos,
            "peer alias did not survive Agent restart");
        const CommandResult alias_renamed = run_control(
            iotox, runtime,
            {"peer-alias-rename", "workstation", "desktop"});
        const CommandResult alias_rename_retry = run_control(
            iotox, runtime,
            {"peer-alias-rename", "desktop", "desktop"});
        const CommandResult renamed_aliases = run_control(
            iotox, runtime, {"peer-aliases"});
        require(
            alias_renamed.exit_code == 0 &&
                alias_renamed.output.find("generation=2\nchanged=1\n") !=
                    std::string::npos &&
                alias_rename_retry.exit_code == 0 &&
                alias_rename_retry.output.find(
                    "generation=2\nchanged=0\n") != std::string::npos &&
                renamed_aliases.exit_code == 0 &&
                renamed_aliases.output.find(
                    "alias=desktop public-key=" + peer_key + "\n") !=
                    std::string::npos,
            "peer alias rename was not durable and idempotent");
        const CommandResult restored_profile =
            run_control(iotox, runtime, {"profile"});
        require(restored_profile.exit_code == 0 &&
                    restored_profile.output.find("name=IoTox FIFO") !=
                        std::string::npos &&
                    restored_profile.output.find("status-message=ordinary profile lane") !=
                        std::string::npos &&
                    restored_profile.output.find("status=away") != std::string::npos,
                "IoTox did not preserve the FIFO-mutated Tox profile across restart");
        const CommandResult restored_authority =
            run_control(iotox, runtime, {"authority"});
        require(restored_authority.exit_code == 0 &&
                    restored_authority.output.find("initialized=1") !=
                        std::string::npos &&
                    restored_authority.output.find("sequence=2") !=
                        std::string::npos &&
                    restored_authority.output.find("active-owner-count=1") !=
                        std::string::npos,
                "IoTox did not replay the signed owner ledger across restart");

        const CommandResult restored_commands =
            run_control(iotox, runtime, {"command-store"});
        require(restored_commands.exit_code == 0 &&
                    extract_field(restored_commands.output,
                                  "local-sender-epoch") ==
                        local_sender_epoch &&
                    restored_commands.output.find(
                        "sender-epoch=" + durable_sender_epoch) !=
                        std::string::npos &&
                    restored_commands.output.find(
                        "message-id=" + durable_request_message_id) !=
                        std::string::npos &&
                    restored_commands.output.find("direction=outgoing") !=
                        std::string::npos &&
                    restored_commands.output.find("lifecycle=succeeded") !=
                        std::string::npos,
                "signed command history or local sender epoch did not survive restart");
        const CommandResult restored_command_record = run_control(
            iotox, runtime,
            {"command-record", "outgoing", peer_key, durable_sender_epoch,
             durable_request_message_id});
        require(restored_command_record.exit_code == 0 &&
                    restored_command_record.output == command_record.output,
                "exact durable command record changed across restart");
        const CommandResult restored_summary_record = run_control(
            iotox, runtime,
            {"command-record", "outgoing", peer_key,
             summary_sender_epoch, summary_message_id});
        require(restored_summary_record.exit_code == 0 &&
                    restored_summary_record.output == summary_record.output,
                "exact system.summary result record changed across restart");

        const CommandResult offline_sessions = run_control(
            iotox, runtime, {"sessions"});
        require(offline_sessions.exit_code == 0 &&
                    offline_sessions.output.find("connected=0") !=
                        std::string::npos,
                "offline lifecycle fixture unexpectedly connected its restored friend");
        const CommandResult offline_issue = run_control(
            iotox, runtime,
            {"command", peer_key, "system.summary", "high"});
        const std::string offline_epoch =
            extract_field(offline_issue.output, "sender-epoch");
        const std::string offline_message =
            extract_field(offline_issue.output, "message-id");
        require(offline_issue.exit_code == 0 &&
                    offline_issue.output.find("lifecycle=reserved") !=
                        std::string::npos &&
                    offline_issue.output.find("priority=high") !=
                        std::string::npos,
                "offline friend did not admit a key-bound durable command\n--- issue ---\n" +
                    offline_issue.output);
        std::this_thread::sleep_for(std::chrono::milliseconds(1500));
        const CommandResult offline_record = run_control(
            iotox, runtime,
            {"command-record", "outgoing", peer_key, offline_epoch,
             offline_message});
        require(offline_record.exit_code == 0 &&
                    offline_record.output.find("lifecycle=reserved") !=
                        std::string::npos &&
                    offline_record.output.find("request-attempts=0") !=
                        std::string::npos,
                "offline durable command attempted transport without a confirmed session\n--- record ---\n" +
                    offline_record.output);
        const CommandResult offline_cancel = run_control(
            iotox, runtime,
            {"command-cancel", peer_key, offline_epoch, offline_message});
        require(offline_cancel.exit_code == 0 &&
                    offline_cancel.output.find("lifecycle=cancelled") !=
                        std::string::npos,
                "offline durable command could not be safely cancelled before first attempt");
        const CommandResult expiring_issue = run_control(
            iotox, runtime,
            {"command", peer_key, "system.summary", "normal", "500"});
        const std::string expiring_epoch =
            extract_field(expiring_issue.output, "sender-epoch");
        const std::string expiring_message =
            extract_field(expiring_issue.output, "message-id");
        require(expiring_issue.exit_code == 0 &&
                    expiring_issue.output.find(
                        "clock-requirement=trusted-wall") !=
                        std::string::npos,
                "explicit trusted clock did not admit a bounded TTL command");
        std::this_thread::sleep_for(std::chrono::milliseconds(1500));
        const CommandResult expiring_record = run_control(
            iotox, runtime,
            {"command-record", "outgoing", peer_key, expiring_epoch,
             expiring_message});
        require(expiring_record.exit_code == 0 &&
                    expiring_record.output.find("lifecycle=expired") !=
                        std::string::npos &&
                    expiring_record.output.find("request-attempts=0") !=
                        std::string::npos,
                "trusted offline TTL did not settle as unattempted expiry\n--- record ---\n" +
                    expiring_record.output);

        // The first mutable operation has an explicit power-cut contract: a
        // crash after the provider effect but before tox savedata/result
        // persistence leaves STARTED durable state, and restart may reapply
        // only the exact frozen desired value. Stop the offline fixture, then
        // use a provider-local SIGSTOP at precisely that window.
        const CommandResult pre_crash_stop =
            run_control(iotox, runtime, {"stop"});
        require(pre_crash_stop.exit_code == 0,
                "pre-mutation-crash iotox stop failed");
        require(wait_for_exit(second, std::chrono::seconds(5)) == 0,
                "pre-mutation-crash lifecycle failed");
        second = -1;

        const std::string audit_before_crash = read_text(authority_audit);
        const std::size_t busy_effects_before = count_occurrences(
            audit_before_crash, "self-status-set value=2 calls=1");
        const std::size_t crash_markers_before = count_occurrences(
            audit_before_crash,
            "self-status-provider-effect-complete-before-savedata");
        second = spawn_agent(
            iotox, mock_toxcore, runtime, state, mutation_crash_log,
            {}, {}, false, false, true, true, "busy", true);
        require(wait_for_stop(second, std::chrono::seconds(10)) == SIGSTOP,
                "mutable provider failpoint did not stop after its effect");
        require(::kill(second, SIGKILL) == 0,
                "unable to kill the stopped mutable-state daemon");
        int mutation_crash_status = 0;
        while (::waitpid(second, &mutation_crash_status, 0) < 0 &&
               errno == EINTR) {
        }
        require(WIFSIGNALED(mutation_crash_status) &&
                    WTERMSIG(mutation_crash_status) == SIGKILL,
                "mutable-state crash fixture did not terminate by SIGKILL");
        second = -1;

        const std::string audit_after_crash = read_text(authority_audit);
        require(
            count_occurrences(
                audit_after_crash,
                "self-status-provider-effect-complete-before-savedata") ==
                crash_markers_before + 1U &&
                count_occurrences(
                    audit_after_crash,
                    "self-status-set value=2 calls=1") ==
                    busy_effects_before + 1U,
            "mutable crash window did not prove exactly one provider effect");

        second = spawn_agent(
            iotox, mock_toxcore, runtime, state, mutation_recovery_log,
            {}, {}, false, false, true);
        wait_for_socket(second, runtime / "control.sock");
        CommandResult recovered_mutation_store;
        CommandResult recovered_mutation_profile;
        bool mutation_recovered = false;
        const auto mutation_recovery_deadline =
            process_test_deadline(std::chrono::seconds(10));
        while (std::chrono::steady_clock::now() < mutation_recovery_deadline &&
               !mutation_recovered) {
            recovered_mutation_store =
                run_control(iotox, runtime, {"command-store"});
            recovered_mutation_profile =
                run_control(iotox, runtime, {"profile"});
            mutation_recovered =
                recovered_mutation_store.exit_code == 0 &&
                recovered_mutation_profile.exit_code == 0 &&
                recovered_mutation_profile.output.find("status=busy") !=
                    std::string::npos &&
                command_record_contains(
                    recovered_mutation_store.output,
                    {"direction=incoming", "lifecycle=succeeded",
                     "operation=profile.status.set", "desired-status=busy",
                     "observed-status=busy", "converged=1",
                     "ownership-epoch=1", "result-bytes=65"});
            if (!mutation_recovered) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(
            mutation_recovered,
            "STARTED profile.status.set did not converge after process restart\n--- profile ---\n" +
                recovered_mutation_profile.output +
                "--- command store ---\n" + recovered_mutation_store.output);
        const std::string audit_after_recovery = read_text(authority_audit);
        require(
            count_occurrences(
                audit_after_recovery,
                "self-status-set value=2 calls=1") ==
                busy_effects_before + 2U,
            "mutable recovery did not reapply the exact desired value once");

        const std::filesystem::path restored_peer_directory =
            runtime / "peers" / peer_key;
        const std::filesystem::path remove_fifo =
            restored_peer_directory / "remove";
        require(std::filesystem::is_fifo(remove_fifo),
                "restarted peer did not regain its private remove FIFO");

        // Exact token semantics are part of the ratox-successor contract. A
        // visually similar record must be rejected without mutating the
        // friendship, then the exact lowercase token removes the public-key
        // selected peer. The friend number remains evidence, never authority.
        write_fifo_record(second, remove_fifo, "REMOVE\n");
        const auto malformed_remove_deadline =
            process_test_deadline(std::chrono::seconds(5));
        bool malformed_remove_rejected = false;
        while (std::chrono::steady_clock::now() < malformed_remove_deadline &&
               !malformed_remove_rejected) {
            const CommandResult current_peers =
                run_control(iotox, runtime, {"peers"});
            const CommandResult lifecycle =
                run_control(iotox, runtime, {"friend-events"});
            malformed_remove_rejected =
                current_peers.exit_code == 0 &&
                current_peers.output.find("public-key=" + peer_key) !=
                    std::string::npos &&
                lifecycle.exit_code == 0 &&
                lifecycle.output.find(
                    "source=local-fifo operation=remove public-key=" +
                    peer_key + " disposition=rejected") !=
                    std::string::npos &&
                lifecycle.output.find(
                    "peer remove FIFO token must be exactly remove") !=
                    std::string::npos;
            if (!malformed_remove_rejected) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(malformed_remove_rejected,
                "malformed remove token mutated the peer or lacked lifecycle evidence");

        write_fifo_record(second, remove_fifo, "remove\n");
        const auto removal_deadline =
            process_test_deadline(std::chrono::seconds(5));
        CommandResult empty;
        CommandResult friendship;
        bool removal_committed = false;
        while (std::chrono::steady_clock::now() < removal_deadline &&
               !removal_committed) {
            empty = run_control(iotox, runtime, {"peers"});
            friendship = run_control(iotox, runtime, {"friend-events"});
            removal_committed =
                empty.exit_code == 0 && empty.output.empty() &&
                !std::filesystem::exists(restored_peer_directory) &&
                friendship.exit_code == 0 &&
                friendship.output.find(
                    "source=local-fifo operation=peer-remove public-key=" +
                    peer_key + " disposition=removed") !=
                    std::string::npos &&
                friendship.output.find(
                    "IoTox authority is unchanged") !=
                    std::string::npos;
            if (!removal_committed) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        require(empty.exit_code == 0 && empty.output.empty(),
                "removed peer remained in the control projection");
        require(!std::filesystem::exists(restored_peer_directory),
                "removed peer remained in the ratox-style runtime projection");
        require(removal_committed,
                "one-binary friend-events omitted the public-key removal decision");
        const CommandResult retained_alias = run_control(
            iotox, runtime, {"peer-aliases"});
        require(
            retained_alias.exit_code == 0 &&
                retained_alias.output.find(
                    "alias=desktop public-key=" + peer_key + "\n") !=
                    std::string::npos,
            "transport peer removal silently released its remembered alias");
        const CommandResult alias_removed = run_control(
            iotox, runtime, {"peer-alias-remove", "desktop"});
        const CommandResult alias_remove_retry = run_control(
            iotox, runtime, {"peer-alias-remove", "desktop"});
        require(
            alias_removed.exit_code == 0 &&
                alias_removed.output.find("generation=3\nchanged=1\n") !=
                    std::string::npos &&
                alias_remove_retry.exit_code == 0 &&
                alias_remove_retry.output.find(
                    "generation=3\nchanged=0\n") != std::string::npos,
            "explicit peer alias removal was not durable and idempotent");
        const CommandResult friendship_watch = run_control(
            iotox, runtime,
            {"--from-start", "--watch-ms", "100", "friend-events-watch"});
        require(friendship_watch.exit_code == 0 &&
                    friendship_watch.output.rfind(friendship.output, 0U) == 0U,
                "friend-events-watch did not follow the existing lifecycle journal from byte zero");
        const CommandResult friendship_status =
            run_control(iotox, runtime, {"status"});
        require(friendship_status.exit_code == 0 &&
                    friendship_status.output.find(
                        "friendship-fifo-record-count=2") !=
                        std::string::npos &&
                    friendship_status.output.find(
                        "friendship-fifo-rejected-count=1") !=
                        std::string::npos,
                "friendship FIFO counters did not distinguish exact and malformed records");

        const CommandResult second_stop = run_control(iotox, runtime, {"stop"});
        require(second_stop.exit_code == 0, "second iotox stop failed");
        require(wait_for_exit(second, std::chrono::seconds(5)) == 0,
                "second one-binary IoTox lifecycle failed");
        second = -1;

        std::cout << "PASS one iotox binary runs agent and local control over mock toxcore\n";
        std::filesystem::remove_all(directory, ignored);
        return EXIT_SUCCESS;
    } catch (const std::exception &exception) {
        std::cerr << "FAIL process lifecycle: " << exception.what() << '\n';
        if (std::filesystem::exists(first_log)) {
            std::cerr << "--- first agent log ---\n" << read_text(first_log);
        }
        if (std::filesystem::exists(second_log)) {
            std::cerr << "--- second agent log ---\n" << read_text(second_log);
        }
        if (std::filesystem::exists(mutation_crash_log)) {
            std::cerr << "--- mutation crash agent log ---\n"
                      << read_text(mutation_crash_log);
        }
        if (std::filesystem::exists(mutation_recovery_log)) {
            std::cerr << "--- mutation recovery agent log ---\n"
                      << read_text(mutation_recovery_log);
        }
        if (std::filesystem::exists(invitation_log)) {
            std::cerr << "--- invitation agent log ---\n"
                      << read_text(invitation_log);
        }
        terminate_child(invitee);
        terminate_child(second);
        terminate_child(first);
        if (std::getenv("IOTOX_KEEP_FAILED_PROCESS_TEST") == nullptr) {
            std::filesystem::remove_all(directory, ignored);
        } else {
            std::cerr << "preserved-failed-process-test=" << directory << '\n';
        }
        return EXIT_FAILURE;
    }
}
