#include "iotox/terminal_profile.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <iostream>
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
#include <fcntl.h>

namespace {

using namespace std::chrono_literals;

void require(bool condition, std::string_view message) {
    if (!condition) {
        throw std::runtime_error(std::string(message));
    }
}

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern =
            (std::filesystem::temp_directory_path() /
             "ir-XXXXXX")
                .string();
        std::vector<char> writable(pattern.begin(), pattern.end());
        writable.push_back('\0');
        char *created = ::mkdtemp(writable.data());
        if (created == nullptr) {
            throw std::runtime_error(
                "mkdtemp failed: " + std::string(std::strerror(errno)));
        }
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0) {
            const int saved_errno = errno;
            std::error_code ignored;
            std::filesystem::remove_all(path_, ignored);
            throw std::runtime_error(
                "chmod temp directory failed: " +
                std::string(std::strerror(saved_errno)));
        }
    }

    TempDirectory(const TempDirectory &) = delete;
    TempDirectory &operator=(const TempDirectory &) = delete;

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path &path() const { return path_; }

  private:
    std::filesystem::path path_;
};

void make_private_directory(const std::filesystem::path &path) {
    require(std::filesystem::create_directory(path),
            "unable to create private test directory");
    require(::chmod(path.c_str(), static_cast<mode_t>(0700)) == 0,
            "unable to protect private test directory");
}

void write_all(int descriptor, std::span<const std::uint8_t> bytes) {
    std::size_t written = 0U;
    while (written < bytes.size()) {
        const ssize_t count = ::write(
            descriptor, bytes.data() + written, bytes.size() - written);
        if (count > 0) {
            written += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        throw std::runtime_error(
            "profile record write failed: " +
            std::string(std::strerror(errno)));
    }
}

void write_private_record(
    const std::filesystem::path &path,
    const std::vector<std::uint8_t> &bytes) {
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        0600);
    if (descriptor < 0) {
        throw std::runtime_error(
            "unable to create private profile record: " +
            std::string(std::strerror(errno)));
    }
    try {
        write_all(descriptor, bytes);
        require(::fsync(descriptor) == 0,
                "unable to synchronize private profile record");
    } catch (...) {
        static_cast<void>(::close(descriptor));
        throw;
    }
    require(::close(descriptor) == 0,
            "unable to close private profile record");
}

std::string lowercase_principal_hex(
    const iotox::terminal::PrincipalId &principal) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(principal.size() * 2U);
    for (const std::uint8_t byte : principal) {
        encoded.push_back(digits[byte >> 4U]);
        encoded.push_back(digits[byte & 0x0FU]);
    }
    return encoded;
}

std::filesystem::path create_profile_store(
    const std::filesystem::path &parent,
    const std::filesystem::path &profile_executable) {
    const std::filesystem::path root = parent / "profiles-store";
    make_private_directory(root);
    make_private_directory(root / "profiles");
    make_private_directory(root / "bindings");

    iotox::terminal::Profile profile;
    profile.id = "restart-fence";
    profile.enabled = true;
    profile.arguments = {profile_executable.string(), "restart-fence"};
    profile.working_directory = "/tmp";

    iotox::terminal::PrincipalId principal{};
    principal.fill(0x33U);
    iotox::terminal::Binding binding;
    binding.principal_id = principal;
    binding.profile_id = profile.id;
    binding.enabled = true;

    auto profile_bytes = iotox::terminal::encode_profile_record(profile);
    require(profile_bytes.ok(), profile_bytes.status().message());
    auto binding_bytes = iotox::terminal::encode_binding_record(binding);
    require(binding_bytes.ok(), binding_bytes.status().message());
    write_private_record(
        root / "profiles" / (profile.id + ".profile"),
        profile_bytes.value());
    write_private_record(
        root / "bindings" /
            (lowercase_principal_hex(principal) + ".binding"),
        binding_bytes.value());
    return root;
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

struct AgentPaths {
    std::filesystem::path runtime;
    std::filesystem::path state;
    std::filesystem::path command_store;
    std::filesystem::path log;
};

pid_t spawn_agent(
    const std::filesystem::path &iotox,
    const std::filesystem::path &mock_toxcore,
    const std::filesystem::path &profile_store,
    const std::filesystem::path &identity,
    const std::filesystem::path &authority_ledger,
    const std::filesystem::path &incarnation_state,
    const AgentPaths &paths) {
    const pid_t child = ::fork();
    if (child < 0) {
        throw std::runtime_error(
            "fork failed: " + std::string(std::strerror(errno)));
    }
    if (child == 0) {
        const int descriptor = ::open(
            paths.log.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC,
            0600);
        if (descriptor < 0 || ::dup2(descriptor, STDOUT_FILENO) < 0 ||
            ::dup2(descriptor, STDERR_FILENO) < 0) {
            _exit(126);
        }
        if (descriptor != STDOUT_FILENO && descriptor != STDERR_FILENO) {
            static_cast<void>(::close(descriptor));
        }

        std::vector<std::string> arguments{
            iotox.string(),
            "run",
            "--library", mock_toxcore.string(),
            "--runtime", paths.runtime.string(),
            "--state", paths.state.string(),
            "--identity", identity.string(),
            "--authority-ledger", authority_ledger.string(),
            "--command-store", paths.command_store.string(),
            "--no-default-bootstrap",
            "--no-default-relays",
            "--enable-ratox-terminal",
            "--ratox-profile-store", profile_store.string(),
            "--ratox-incarnation-state", incarnation_state.string(),
            "--ratox-helper", iotox.string(),
            "--ratox-profile-owner-uid",
            std::to_string(static_cast<unsigned long long>(::geteuid())),
            "--run-ms", "60000",
        };
        std::vector<char *> argv = make_argv(arguments);
        ::execv(iotox.c_str(), argv.data());
        _exit(127);
    }
    return child;
}

std::string read_text(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input.good()) {
        return {};
    }
    std::ostringstream output;
    output << input.rdbuf();
    return output.str();
}

std::string field_value(std::string_view text, std::string_view field) {
    const std::string prefix = std::string(field) + "=";
    std::size_t begin = 0U;
    while (begin < text.size()) {
        const std::size_t end = text.find('\n', begin);
        const std::string_view line = text.substr(
            begin, end == std::string_view::npos ? text.size() - begin
                                                : end - begin);
        if (line.starts_with(prefix)) {
            return std::string(line.substr(prefix.size()));
        }
        if (end == std::string_view::npos) {
            break;
        }
        begin = end + 1U;
    }
    return {};
}

std::uint64_t parse_u64_field(
    std::string_view text, std::string_view field) {
    const std::string value = field_value(text, field);
    require(!value.empty(), "runtime status omitted required numeric field");
    std::size_t consumed = 0U;
    unsigned long long parsed = 0U;
    try {
        parsed = std::stoull(value, &consumed, 10);
    } catch (const std::exception &) {
        throw std::runtime_error("runtime status numeric field is invalid");
    }
    require(consumed == value.size(),
            "runtime status numeric field has trailing bytes");
    require(parsed <= std::numeric_limits<std::uint64_t>::max(),
            "runtime status numeric field exceeds uint64");
    return static_cast<std::uint64_t>(parsed);
}

bool process_exited(pid_t child, int *status) {
    for (;;) {
        const pid_t result = ::waitpid(child, status, WNOHANG);
        if (result == child) {
            return true;
        }
        if (result == 0) {
            return false;
        }
        if (result < 0 && errno == EINTR) {
            continue;
        }
        throw std::runtime_error(
            "waitpid failed: " + std::string(std::strerror(errno)));
    }
}

std::string wait_for_runtime(
    pid_t child,
    const AgentPaths &paths,
    std::string_view phase,
    std::string_view lease,
    std::chrono::seconds timeout = 10s) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
        const std::string status = read_text(paths.runtime / "status");
        if (field_value(status, "phase") == phase &&
            field_value(status, "ratox-incarnation-lease-held") == lease) {
            return status;
        }
        int child_status = 0;
        if (process_exited(child, &child_status)) {
            std::ostringstream message;
            message << "iotox process exited before runtime state " << phase
                    << "/lease=" << lease << "; log: " << read_text(paths.log);
            throw std::runtime_error(message.str());
        }
        std::this_thread::sleep_for(10ms);
    }
    throw std::runtime_error(
        "timed out waiting for runtime state; log: " + read_text(paths.log) +
        "; status: " + read_text(paths.runtime / "status"));
}

int wait_for_exit(pid_t child, std::chrono::seconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
        int status = 0;
        if (process_exited(child, &status)) {
            if (WIFEXITED(status)) {
                return WEXITSTATUS(status);
            }
            if (WIFSIGNALED(status)) {
                return 128 + WTERMSIG(status);
            }
            return 128;
        }
        std::this_thread::sleep_for(10ms);
    }
    throw std::runtime_error("timed out waiting for iotox process exit");
}

void terminate_cleanly(pid_t child, const AgentPaths &paths) {
    require(::kill(child, SIGTERM) == 0,
            "unable to send SIGTERM to iotox process");
    const int exit_code = wait_for_exit(child, 10s);
    require(exit_code == 0,
            "iotox process did not stop cleanly after SIGTERM; log: " +
                read_text(paths.log));
}

std::uint64_t read_be64(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    require(bytes.size() >= offset + 8U,
            "restart record is shorter than its incarnation field");
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

std::vector<std::uint8_t> read_binary(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    require(input.good(), "unable to open signed restart record");
    return std::vector<std::uint8_t>(
        std::istreambuf_iterator<char>(input),
        std::istreambuf_iterator<char>());
}

}  // namespace

int main(int argc, char **argv) {
    pid_t first = -1;
    pid_t contender = -1;
    pid_t successor = -1;
    try {
        require(argc == 3, "usage: test-ratox-restart-process IOTOX MOCK_TOXCORE");
        const std::filesystem::path iotox =
            std::filesystem::absolute(argv[1]).lexically_normal();
        const std::filesystem::path mock_toxcore =
            std::filesystem::absolute(argv[2]).lexically_normal();
        TempDirectory temporary;
        const std::filesystem::path shared = temporary.path() / "shared";
        make_private_directory(shared);
        const std::filesystem::path profile_store =
            create_profile_store(temporary.path(), iotox);
        const std::filesystem::path identity = shared / "device.identity";
        const std::filesystem::path authority_ledger = shared / "authority.ledger";
        const std::filesystem::path incarnation_state =
            shared / "ratox" / "incarnation.state";

        const AgentPaths first_paths{
            temporary.path() / "runtime-first",
            temporary.path() / "state-first.toxsave",
            temporary.path() / "commands-first.journal",
            temporary.path() / "first.log",
        };
        first = spawn_agent(
            iotox, mock_toxcore, profile_store, identity, authority_ledger,
            incarnation_state, first_paths);
        const std::string first_status = wait_for_runtime(
            first, first_paths, "running", "1");
        const std::uint64_t first_incarnation = parse_u64_field(
            first_status, "ratox-host-incarnation");
        require(first_incarnation != 0U,
                "first process published a zero Ratox incarnation");

        const std::vector<std::uint8_t> first_record =
            read_binary(incarnation_state);
        require(first_record.size() == 128U,
                "signed restart record is not exactly 128 bytes");
        require(std::equal(
                    first_record.begin(), first_record.begin() + 8,
                    std::string_view("IOTXRIN1").begin()),
                "signed restart record has the wrong frozen magic");
        require(read_be64(first_record, 48U) == first_incarnation,
                "signed restart record disagrees with runtime status");
        require(read_be64(first_record, 56U) == ~first_incarnation,
                "signed restart record complement is invalid");

        const AgentPaths contender_paths{
            temporary.path() / "runtime-contender",
            temporary.path() / "state-contender.toxsave",
            temporary.path() / "commands-contender.journal",
            temporary.path() / "contender.log",
        };
        contender = spawn_agent(
            iotox, mock_toxcore, profile_store, identity, authority_ledger,
            incarnation_state, contender_paths);
        const int contender_exit = wait_for_exit(contender, 10s);
        contender = -1;
        require(contender_exit == 3,
                "concurrent Ratox host did not fail at startup");
        const std::string contender_log = read_text(contender_paths.log);
        require(
            contender_log.find("another IoTox host already owns") !=
                std::string::npos,
            "concurrent Ratox host failure did not identify lease contention: " +
                contender_log);
        const std::string contender_status =
            read_text(contender_paths.runtime / "status");
        require(field_value(contender_status, "phase") == "failed",
                "contender did not publish failed runtime state");
        require(
            field_value(contender_status, "ratox-incarnation-lease-held") == "0",
            "contender falsely published a held Ratox incarnation lease");
        require(read_be64(read_binary(incarnation_state), 48U) ==
                    first_incarnation,
                "failed contender advanced the signed incarnation record");

        terminate_cleanly(first, first_paths);
        first = -1;
        const std::string stopped_status =
            read_text(first_paths.runtime / "status");
        require(field_value(stopped_status, "phase") == "stopped",
                "first process did not publish stopped runtime state");
        require(
            field_value(stopped_status, "ratox-incarnation-lease-held") == "0",
            "first process retained its Ratox lease after shutdown");

        const AgentPaths successor_paths{
            temporary.path() / "runtime-successor",
            temporary.path() / "state-successor.toxsave",
            temporary.path() / "commands-successor.journal",
            temporary.path() / "successor.log",
        };
        successor = spawn_agent(
            iotox, mock_toxcore, profile_store, identity, authority_ledger,
            incarnation_state, successor_paths);
        const std::string successor_status = wait_for_runtime(
            successor, successor_paths, "running", "1");
        const std::uint64_t successor_incarnation = parse_u64_field(
            successor_status, "ratox-host-incarnation");
        require(first_incarnation != std::numeric_limits<std::uint64_t>::max(),
                "test fixture unexpectedly selected the terminal incarnation");
        require(successor_incarnation == first_incarnation + 1U,
                "successor did not publish exactly the next Ratox incarnation");
        require(read_be64(read_binary(incarnation_state), 48U) ==
                    successor_incarnation,
                "successor runtime status disagrees with signed restart record");

        terminate_cleanly(successor, successor_paths);
        successor = -1;
        std::cout << "PASS shipped IoTox binary enforces the Ratox restart fence\n";
        return 0;
    } catch (const std::exception &exception) {
        for (const pid_t child : {successor, contender, first}) {
            if (child > 0) {
                static_cast<void>(::kill(child, SIGKILL));
                int ignored = 0;
                while (::waitpid(child, &ignored, 0) < 0 && errno == EINTR) {
                }
            }
        }
        std::cerr << "FAIL Ratox restart process contract: "
                  << exception.what() << '\n';
        return 1;
    }
}
