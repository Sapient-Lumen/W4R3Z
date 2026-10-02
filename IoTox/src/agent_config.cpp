#include "iotox/agent_config.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <optional>
#include <set>
#include <string_view>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox {
namespace {

constexpr std::string_view kHeader = "iotox-agent-config-v1\n";

class FileDescriptor {
  public:
    explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~FileDescriptor() {
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    [[nodiscard]] int get() const noexcept { return descriptor_; }

  private:
    int descriptor_{-1};
};

[[nodiscard]] Status io_status(std::string_view operation,
                               const std::filesystem::path &path,
                               int error_number = errno) {
    return Status{ErrorCode::io_error,
                  std::string(operation) + " '" + path.string() + "': " +
                      std::strerror(error_number)};
}

[[nodiscard]] bool stable_snapshot(const struct stat &before,
                                   const struct stat &after) noexcept {
    return before.st_dev == after.st_dev && before.st_ino == after.st_ino &&
           before.st_mode == after.st_mode &&
           before.st_nlink == after.st_nlink &&
           before.st_uid == after.st_uid && before.st_size == after.st_size &&
           before.st_mtim.tv_sec == after.st_mtim.tv_sec &&
           before.st_mtim.tv_nsec == after.st_mtim.tv_nsec &&
           before.st_ctim.tv_sec == after.st_ctim.tv_sec &&
           before.st_ctim.tv_nsec == after.st_ctim.tv_nsec;
}

[[nodiscard]] bool valid_argument_text(std::string_view argument) noexcept {
    if (argument.empty() ||
        argument.size() > kMaximumAgentConfigArgumentBytes) {
        return false;
    }
    return std::all_of(argument.begin(), argument.end(), [](char value) {
        const auto byte = static_cast<unsigned char>(value);
        return byte >= 0x20U && byte != 0x7fU;
    });
}

[[nodiscard]] std::string argument_prefix(std::size_t index) {
    std::string result{"argument-0000="};
    for (std::size_t position = 4U; position > 0U; --position) {
        result[9U + position - 1U] =
            static_cast<char>('0' + static_cast<int>(index % 10U));
        index /= 10U;
    }
    return result;
}

[[nodiscard]] bool flag_option(std::string_view option) noexcept {
    static constexpr std::array<std::string_view, 20U> flags{
        "--no-default-bootstrap",
        "--no-default-relays",
        "--native-tcp-only",
        "--trust-wall-clock",
        "--enable-ratox-terminal",
        "--enable-ratox-terminal-client",
        "--enable-route-workers",
        "--enable-private-route-bindings",
        "--enable-sync",
        "--enable-signed-updates",
        "--enable-update-linux-service",
        "--qualify-route-stop-after-cancel",
        "--witness-application-incarnation",
        "--witness-ratox-incarnation",
        "--witness-route-generation",
        "--witness-terminal-policy",
        "--witness-command-effects",
        "--witness-sync-policy",
        "--witness-update-lifecycle",
        "--witness-sync-guarded-state",
    };
    return std::find(flags.begin(), flags.end(), option) != flags.end();
}

[[nodiscard]] bool repeatable_option(std::string_view option) noexcept {
    static constexpr std::array<std::string_view, 5U> repeatable{
        "--bootstrap",
        "--tcp-relay",
        "--route-worker-network",
        "--route-worker-bootstrap",
        "--route-worker-tcp-relay",
    };
    return std::find(repeatable.begin(), repeatable.end(), option) !=
           repeatable.end();
}

struct ArgumentGroup {
    std::string option;
    std::optional<std::string> value;
};

template <typename Range>
[[nodiscard]] Result<std::vector<ArgumentGroup>> group_arguments(
    const Range &arguments, std::string_view source) {
    std::vector<ArgumentGroup> groups;
    std::set<std::string> nonrepeatable;
    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        const std::string_view option = arguments[index];
        if (!option.starts_with("--") || option.size() == 2U ||
            option == "--config") {
            return Status{ErrorCode::invalid_argument,
                          std::string(source) +
                              " contains a non-Agent or reserved option"};
        }
        ArgumentGroup group;
        group.option = option;
        if (!flag_option(option)) {
            if (index + 1U >= arguments.size()) {
                return Status{ErrorCode::invalid_argument,
                              std::string(source) + " option '" +
                                  std::string(option) + "' requires a value"};
            }
            group.value = std::string(arguments[++index]);
        }
        if (!repeatable_option(option) &&
            !nonrepeatable.insert(group.option).second) {
            return Status{ErrorCode::invalid_argument,
                          std::string(source) + " duplicates option '" +
                              group.option + "'"};
        }
        groups.push_back(std::move(group));
    }
    return groups;
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_agent_config_record(
    const AgentConfigRecord &record) {
    if (record.arguments.size() > kMaximumAgentConfigArguments) {
        return Status{ErrorCode::resource_exhausted,
                      "Agent configuration argument bound is exhausted"};
    }
    std::string text{kHeader};
    for (std::size_t index = 0U; index < record.arguments.size(); ++index) {
        if (!valid_argument_text(record.arguments[index])) {
            return Status{ErrorCode::invalid_argument,
                          "Agent configuration argument contains an empty, "
                          "oversized, or control-byte value"};
        }
        text += argument_prefix(index);
        text += record.arguments[index];
        text.push_back('\n');
        if (text.size() > kMaximumAgentConfigBytes) {
            return Status{ErrorCode::resource_exhausted,
                          "Agent configuration byte bound is exhausted"};
        }
    }
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<AgentConfigRecord> decode_agent_config_record(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kHeader.size() ||
        bytes.size() > kMaximumAgentConfigBytes ||
        !std::equal(kHeader.begin(), kHeader.end(), bytes.begin()) ||
        bytes.back() != static_cast<std::uint8_t>('\n')) {
        return Status{ErrorCode::protocol_error,
                      "Agent configuration header, size, or trailing LF is invalid"};
    }
    const std::string_view text{
        reinterpret_cast<const char *>(bytes.data()), bytes.size()};
    AgentConfigRecord record;
    std::size_t offset = kHeader.size();
    while (offset < text.size()) {
        if (record.arguments.size() >= kMaximumAgentConfigArguments) {
            return Status{ErrorCode::resource_exhausted,
                          "Agent configuration argument bound is exhausted"};
        }
        const std::size_t end = text.find('\n', offset);
        if (end == std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "Agent configuration line is not LF terminated"};
        }
        const std::string_view line = text.substr(offset, end - offset);
        const std::string prefix = argument_prefix(record.arguments.size());
        if (!line.starts_with(prefix)) {
            return Status{ErrorCode::protocol_error,
                          "Agent configuration fields are unknown, duplicated, or out of order"};
        }
        const std::string_view argument = line.substr(prefix.size());
        if (!valid_argument_text(argument)) {
            return Status{ErrorCode::protocol_error,
                          "Agent configuration argument is empty, oversized, or contains control bytes"};
        }
        record.arguments.emplace_back(argument);
        offset = end + 1U;
    }
    auto canonical = encode_agent_config_record(record);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "Agent configuration is not canonical"};
    }
    auto grouped = group_arguments(record.arguments, "Agent configuration");
    if (!grouped) return grouped.status();
    return record;
}

Result<AgentConfigRecord> load_agent_config_record(
    const std::filesystem::path &path, std::uint32_t expected_owner_uid) {
    if (path.empty() || !path.is_absolute() || path == path.root_path() ||
        path.lexically_normal() != path) {
        return Status{ErrorCode::invalid_argument,
                      "Agent configuration path must be normalized, non-root, and absolute"};
    }
    int opened = -1;
    do {
        opened = ::open(path.c_str(),
                        O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    } while (opened < 0 && errno == EINTR);
    if (opened < 0) {
        return io_status("unable to open Agent configuration", path);
    }
    FileDescriptor descriptor(opened);
    struct stat before {};
    if (::fstat(descriptor.get(), &before) != 0) {
        return io_status("unable to inspect Agent configuration", path);
    }
    if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
        before.st_uid != static_cast<uid_t>(expected_owner_uid) ||
        (before.st_mode & (S_IRWXG | S_IRWXO)) != 0U ||
        (before.st_mode & S_IRUSR) == 0U || before.st_size < 0 ||
        static_cast<std::uint64_t>(before.st_size) >
            kMaximumAgentConfigBytes) {
        return Status{
            ErrorCode::io_error,
            "Agent configuration must be one single-link owner-readable "
            "regular file with no group/other permissions"};
    }
    std::vector<std::uint8_t> bytes(
        static_cast<std::size_t>(before.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor.get(), bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            return count == 0
                ? Status{ErrorCode::io_error,
                         "Agent configuration ended before its inspected size"}
                : io_status("unable to read Agent configuration", path);
        }
        offset += static_cast<std::size_t>(count);
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0 ||
        !stable_snapshot(before, after)) {
        return Status{ErrorCode::io_error,
                      "Agent configuration changed while it was read"};
    }
    return decode_agent_config_record(bytes);
}

Result<std::vector<std::string>> merge_agent_config_arguments(
    std::span<const std::string> file_arguments,
    std::span<const std::string_view> command_line_arguments) {
    auto file_groups = group_arguments(file_arguments, "Agent configuration");
    if (!file_groups) return file_groups.status();
    auto override_groups =
        group_arguments(command_line_arguments, "Agent command line");
    if (!override_groups) return override_groups.status();

    std::set<std::string> overridden;
    for (const ArgumentGroup &group : override_groups.value()) {
        overridden.insert(group.option);
    }
    std::vector<std::string> merged;
    const auto append = [&merged](const ArgumentGroup &group) {
        merged.push_back(group.option);
        if (group.value) merged.push_back(*group.value);
    };
    for (const ArgumentGroup &group : file_groups.value()) {
        if (!overridden.contains(group.option)) append(group);
    }
    for (const ArgumentGroup &group : override_groups.value()) append(group);
    if (merged.size() > kMaximumAgentConfigArguments) {
        return Status{ErrorCode::resource_exhausted,
                      "merged Agent argument bound is exhausted"};
    }
    return merged;
}

}  // namespace iotox
