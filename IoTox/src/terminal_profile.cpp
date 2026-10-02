#include "iotox/terminal_profile.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <charconv>
#include <climits>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <limits>
#include <locale>
#include <mutex>
#include <numeric>
#include <optional>
#include <shared_mutex>
#include <sstream>
#include <string_view>
#include <sys/stat.h>
#include <sys/file.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

namespace iotox::terminal {
namespace {

constexpr std::string_view kProfileHeaderV1 = "iotox-terminal-profile-v1";
constexpr std::string_view kProfileHeaderV2 = "iotox-terminal-profile-v2";
constexpr std::string_view kProfileHeaderV3 = "iotox-terminal-profile-v3";
constexpr std::string_view kProfileHeaderV4 = "iotox-terminal-profile-v4";
constexpr std::string_view kProfileHeaderV5 = "iotox-terminal-profile-v5";
constexpr std::string_view kProfileHeaderV6 = "iotox-terminal-profile-v6";
constexpr std::string_view kProfileHeaderV7 = "iotox-terminal-profile-v7";
constexpr std::size_t kMaximumSupplementaryGroups = 256U;
constexpr std::string_view kBindingHeader = "iotox-terminal-binding-v1";
constexpr std::size_t kMaximumProfileIdBytes = 64U;
constexpr std::size_t kMaximumPathBytes = 4096U;
constexpr std::size_t kMaximumTerminalTypeBytes = 64U;
constexpr std::size_t kMaximumEnvironmentNameBytes = 64U;
constexpr std::uint64_t kMaximumLimitValue = (1ULL << 60U);
constexpr std::chrono::milliseconds kMaximumGrace{60'000};

class FileDescriptor {
  public:
    FileDescriptor() = default;
    explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~FileDescriptor() {
        if (descriptor_ >= 0) {
            static_cast<void>(::close(descriptor_));
        }
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this != &other) {
            if (descriptor_ >= 0) {
                static_cast<void>(::close(descriptor_));
            }
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }

  private:
    int descriptor_{-1};
};

[[nodiscard]] Status error_status(
    ErrorCode code, std::string_view operation, int error_number = errno) {
    return Status{
        code,
        std::string(operation) + ": " + std::strerror(error_number)};
}

[[nodiscard]] bool contains_nul(std::string_view value) {
    return value.find('\0') != std::string_view::npos;
}

[[nodiscard]] bool valid_profile_id(std::string_view value) {
    if (value.empty() || value.size() > kMaximumProfileIdBytes) {
        return false;
    }
    for (std::size_t index = 0U; index < value.size(); ++index) {
        const unsigned char byte = static_cast<unsigned char>(value[index]);
        const bool alpha = byte >= static_cast<unsigned char>('a') &&
                           byte <= static_cast<unsigned char>('z');
        const bool digit = byte >= static_cast<unsigned char>('0') &&
                           byte <= static_cast<unsigned char>('9');
        const bool punctuation = byte == static_cast<unsigned char>('.') ||
                                 byte == static_cast<unsigned char>('_') ||
                                 byte == static_cast<unsigned char>('-');
        if (!(alpha || digit || (index != 0U && punctuation))) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool valid_absolute_path(
    std::string_view value, bool allow_root) {
    if (value.empty() || value.size() > kMaximumPathBytes ||
        contains_nul(value) || value.front() != '/') {
        return false;
    }
    if (!allow_root && value == "/") {
        return false;
    }
    const std::filesystem::path path{std::string(value)};
    if (!path.is_absolute() || path.lexically_normal().generic_string() != value) {
        return false;
    }
    for (const auto &component : path) {
        const std::string text = component.generic_string();
        if (text == "." || text == ".." || text.empty()) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool valid_environment_name(std::string_view value) {
    if (value.empty() || value.size() > kMaximumEnvironmentNameBytes) {
        return false;
    }
    const auto first = static_cast<unsigned char>(value.front());
    const bool first_ok =
        (first >= static_cast<unsigned char>('A') &&
         first <= static_cast<unsigned char>('Z')) ||
        (first >= static_cast<unsigned char>('a') &&
         first <= static_cast<unsigned char>('z')) ||
        first == static_cast<unsigned char>('_');
    if (!first_ok) {
        return false;
    }
    for (const char character : value.substr(1U)) {
        const auto byte = static_cast<unsigned char>(character);
        const bool alpha =
            (byte >= static_cast<unsigned char>('A') &&
             byte <= static_cast<unsigned char>('Z')) ||
            (byte >= static_cast<unsigned char>('a') &&
             byte <= static_cast<unsigned char>('z'));
        const bool digit = byte >= static_cast<unsigned char>('0') &&
                           byte <= static_cast<unsigned char>('9');
        if (!(alpha || digit || byte == static_cast<unsigned char>('_'))) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] bool hazardous_environment_name(std::string_view name) {
    static constexpr std::array exact{
        std::string_view{"TERM"},
        std::string_view{"IFS"},
        std::string_view{"ENV"},
        std::string_view{"BASH_ENV"},
        std::string_view{"SHELLOPTS"},
        std::string_view{"PS4"},
        std::string_view{"GCONV_PATH"},
        std::string_view{"LOCPATH"},
        std::string_view{"NLSPATH"},
        std::string_view{"GLIBC_TUNABLES"},
    };
    if (std::find(exact.begin(), exact.end(), name) != exact.end()) {
        return true;
    }
    static constexpr std::array prefixes{
        std::string_view{"LD_"},
        std::string_view{"DYLD_"},
        std::string_view{"MALLOC_"},
    };
    return std::any_of(prefixes.begin(), prefixes.end(), [&](std::string_view prefix) {
        return name.starts_with(prefix);
    });
}

[[nodiscard]] bool safe_inherited_environment_name(std::string_view name) {
    static constexpr std::array exact{
        std::string_view{"LANG"},
        std::string_view{"TZ"},
        std::string_view{"HOME"},
        std::string_view{"USER"},
        std::string_view{"LOGNAME"},
        std::string_view{"SHELL"},
        std::string_view{"PATH"},
    };
    return std::find(exact.begin(), exact.end(), name) != exact.end() ||
           name.starts_with("LC_");
}

[[nodiscard]] bool valid_terminal_type(std::string_view value) {
    if (value.empty() || value.size() > kMaximumTerminalTypeBytes) {
        return false;
    }
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        const bool alpha =
            (byte >= static_cast<unsigned char>('A') &&
             byte <= static_cast<unsigned char>('Z')) ||
            (byte >= static_cast<unsigned char>('a') &&
             byte <= static_cast<unsigned char>('z'));
        const bool digit = byte >= static_cast<unsigned char>('0') &&
                           byte <= static_cast<unsigned char>('9');
        const bool punctuation = byte == static_cast<unsigned char>('-') ||
                                 byte == static_cast<unsigned char>('_') ||
                                 byte == static_cast<unsigned char>('.') ||
                                 byte == static_cast<unsigned char>('+');
        if (!(alpha || digit || punctuation)) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] Status validate_dimension_policy(const DimensionPolicy &policy) {
    const Status minimum = validate_dimensions(policy.minimum);
    if (!minimum.ok()) return minimum;
    const Status initial = validate_dimensions(policy.initial);
    if (!initial.ok()) return initial;
    const Status maximum = validate_dimensions(policy.maximum);
    if (!maximum.ok()) return maximum;
    if (policy.minimum.columns > policy.initial.columns ||
        policy.initial.columns > policy.maximum.columns ||
        policy.minimum.rows > policy.initial.rows ||
        policy.initial.rows > policy.maximum.rows) {
        return Status{ErrorCode::invalid_argument,
                      "terminal dimension policy is not ordered"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_resource_limits(const ResourceLimits &limits) {
    const std::array values{
        limits.cpu_seconds,
        limits.address_space_bytes,
        limits.file_size_bytes,
        limits.open_files,
        limits.processes,
    };
    if (std::any_of(values.begin(), values.end(), [](std::uint64_t value) {
            return value > kMaximumLimitValue;
        })) {
        return Status{ErrorCode::invalid_argument,
                      "terminal resource limit exceeds the v1 bound"};
    }
    if (limits.open_files != 0U && limits.open_files < 3U) {
        return Status{ErrorCode::invalid_argument,
                      "terminal open-file limit must retain standard descriptors"};
    }
    return Status::success();
}

// Exact comparison of two positive rational values without floating point or
// overflowing cross-products. Continued-fraction terms alternate order when
// the reciprocal step is taken, hence the `inverted` direction flag.
[[nodiscard]] int compare_positive_fractions(
    std::uint64_t left_numerator, std::uint64_t left_denominator,
    std::uint64_t right_numerator, std::uint64_t right_denominator) noexcept {
    bool inverted = false;
    while (true) {
        const std::uint64_t left_integer =
            left_numerator / left_denominator;
        const std::uint64_t right_integer =
            right_numerator / right_denominator;
        if (left_integer != right_integer) {
            const int comparison = left_integer < right_integer ? -1 : 1;
            return inverted ? -comparison : comparison;
        }

        const std::uint64_t left_remainder =
            left_numerator % left_denominator;
        const std::uint64_t right_remainder =
            right_numerator % right_denominator;
        if (left_remainder == 0U || right_remainder == 0U) {
            int comparison = 0;
            if (left_remainder != right_remainder) {
                comparison = left_remainder == 0U ? -1 : 1;
            }
            return inverted ? -comparison : comparison;
        }

        left_numerator = left_denominator;
        left_denominator = left_remainder;
        right_numerator = right_denominator;
        right_denominator = right_remainder;
        inverted = !inverted;
    }
}

template <typename Value>
[[nodiscard]] std::optional<Value> stricter_optional_maximum(
    const std::optional<Value> &host,
    const std::optional<Value> &profile) {
    if (!host.has_value()) return profile;
    if (!profile.has_value()) return host;
    return std::min(*host, *profile);
}

[[nodiscard]] Status validate_grace(
    std::chrono::milliseconds value, std::string_view label) {
    if (value.count() < 0 || value > kMaximumGrace) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " is outside the v1 bound"};
    }
    return Status::success();
}

[[nodiscard]] std::string hex_encode(std::string_view value) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string output;
    output.reserve(value.size() * 2U);
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        output.push_back(digits[byte >> 4U]);
        output.push_back(digits[byte & 0x0FU]);
    }
    return output;
}

[[nodiscard]] std::string hex_encode(std::span<const std::uint8_t> value) {
    return hex_encode(std::string_view{
        reinterpret_cast<const char *>(value.data()), value.size()});
}

[[nodiscard]] int hex_nibble(char character) {
    if (character >= '0' && character <= '9') return character - '0';
    if (character >= 'a' && character <= 'f') return 10 + character - 'a';
    return -1;
}

[[nodiscard]] Result<std::string> hex_decode_string(
    std::string_view value, std::size_t maximum, std::string_view label) {
    if ((value.size() % 2U) != 0U || value.size() / 2U > maximum) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " hexadecimal length is invalid"};
    }
    std::string output;
    output.reserve(value.size() / 2U);
    for (std::size_t index = 0U; index < value.size(); index += 2U) {
        const int high = hex_nibble(value[index]);
        const int low = hex_nibble(value[index + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " is not lowercase hexadecimal"};
        }
        output.push_back(static_cast<char>((high << 4U) | low));
    }
    return output;
}

[[nodiscard]] Result<std::uint64_t> parse_u64(
    std::string_view value, std::string_view label) {
    if (value.empty() || value.front() == '+' || value.front() == '-') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not an unsigned integer"};
    }
    std::uint64_t parsed = 0U;
    const auto result = std::from_chars(
        value.data(), value.data() + value.size(), parsed, 10);
    if (result.ec != std::errc{} ||
        result.ptr != value.data() + value.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not an unsigned integer"};
    }
    return parsed;
}

[[nodiscard]] Result<std::uint32_t> parse_u32(
    std::string_view value, std::string_view label) {
    auto parsed = parse_u64(value, label);
    if (!parsed.ok()) return parsed.status();
    if (parsed.value() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " exceeds u32"};
    }
    return static_cast<std::uint32_t>(parsed.value());
}

[[nodiscard]] Result<CgroupIoDevice> parse_cgroup_io_device(
    std::string_view value, std::string_view label) {
    const std::size_t separator = value.find(':');
    if (separator == std::string_view::npos || separator == 0U ||
        separator + 1U >= value.size() ||
        value.find(':', separator + 1U) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical MAJOR:MINOR"};
    }
    const std::string_view major_text = value.substr(0U, separator);
    const std::string_view minor_text = value.substr(separator + 1U);
    if ((major_text.size() > 1U && major_text.front() == '0') ||
        (minor_text.size() > 1U && minor_text.front() == '0')) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is not canonical MAJOR:MINOR"};
    }
    auto major = parse_u32(major_text, label);
    if (!major.ok()) return major.status();
    auto minor = parse_u32(minor_text, label);
    if (!minor.ok()) return minor.status();
    return CgroupIoDevice{major.value(), minor.value()};
}

[[nodiscard]] bool has_cgroup_io_limits(
    const CgroupResourceLimits &limits) noexcept {
    return limits.maximum_io_read_bytes_per_second.has_value() ||
           limits.maximum_io_write_bytes_per_second.has_value() ||
           limits.maximum_io_read_operations_per_second.has_value() ||
           limits.maximum_io_write_operations_per_second.has_value();
}

[[nodiscard]] Result<std::uint16_t> parse_u16(
    std::string_view value, std::string_view label) {
    auto parsed = parse_u64(value, label);
    if (!parsed.ok()) return parsed.status();
    if (parsed.value() > std::numeric_limits<std::uint16_t>::max()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " exceeds u16"};
    }
    return static_cast<std::uint16_t>(parsed.value());
}

[[nodiscard]] Result<std::vector<std::string_view>> split_record(
    std::span<const std::uint8_t> bytes, std::size_t maximum,
    std::string_view label) {
    if (bytes.empty() || bytes.size() > maximum || bytes.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " must have one bounded LF-terminated record"};
    }
    for (const std::uint8_t byte : bytes) {
        if (byte == 0U || byte == static_cast<std::uint8_t>('\r')) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " contains a forbidden byte"};
        }
    }
    const std::string_view text{
        reinterpret_cast<const char *>(bytes.data()), bytes.size() - 1U};
    if (text.empty() || text.back() == '\n') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains an empty trailing line"};
    }
    std::vector<std::string_view> lines;
    std::size_t offset = 0U;
    while (offset <= text.size()) {
        const std::size_t end = text.find('\n', offset);
        const std::size_t length =
            end == std::string_view::npos ? text.size() - offset : end - offset;
        if (length == 0U) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " contains an empty line"};
        }
        lines.push_back(text.substr(offset, length));
        if (end == std::string_view::npos) break;
        offset = end + 1U;
    }
    return lines;
}

[[nodiscard]] Result<std::string_view> field_value(
    std::string_view line, std::string_view key) {
    if (!line.starts_with(key)) {
        return Status{ErrorCode::protocol_error,
                      "terminal policy field order or name is invalid"};
    }
    return line.substr(key.size());
}

[[nodiscard]] Result<std::array<std::string_view, 3U>> split_three(
    std::string_view value, char delimiter, std::string_view label) {
    const std::size_t first = value.find(delimiter);
    const std::size_t second =
        first == std::string_view::npos ? std::string_view::npos
                                        : value.find(delimiter, first + 1U);
    if (first == std::string_view::npos || second == std::string_view::npos ||
        value.find(delimiter, second + 1U) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " requires exactly three fields"};
    }
    return std::array{
        value.substr(0U, first),
        value.substr(first + 1U, second - first - 1U),
        value.substr(second + 1U)};
}

[[nodiscard]] Result<Dimensions> parse_dimension_pair(
    std::string_view value, std::string_view label) {
    const std::size_t separator = value.find(':');
    if (separator == std::string_view::npos ||
        value.find(':', separator + 1U) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " requires columns:rows"};
    }
    auto columns = parse_u16(value.substr(0U, separator), label);
    if (!columns.ok()) return columns.status();
    auto rows = parse_u16(value.substr(separator + 1U), label);
    if (!rows.ok()) return rows.status();
    return Dimensions{columns.value(), rows.value()};
}

[[nodiscard]] std::string principal_hex(const PrincipalId &principal_id) {
    return hex_encode(std::span<const std::uint8_t>{principal_id});
}

[[nodiscard]] Result<PrincipalId> parse_principal(std::string_view value) {
    auto decoded = hex_decode_string(value, 32U, "principal");
    if (!decoded.ok() || decoded.value().size() != 32U) {
        return Status{ErrorCode::protocol_error,
                      "terminal binding principal must be 64 lowercase hex characters"};
    }
    PrincipalId principal{};
    std::copy(decoded.value().begin(), decoded.value().end(), principal.begin());
    return principal;
}

[[nodiscard]] bool principal_less(const PrincipalId &left, const PrincipalId &right) {
    return std::lexicographical_compare(
        left.begin(), left.end(), right.begin(), right.end());
}

[[nodiscard]] Result<FileDescriptor> open_absolute_directory_without_symlinks(
    const std::filesystem::path &path) {
    if (path.empty() || !path.is_absolute() || path.lexically_normal() != path) {
        return Status{ErrorCode::invalid_argument,
                      "terminal policy root must be a normalized absolute path"};
    }
    FileDescriptor current(
        ::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (current.get() < 0) {
        return error_status(ErrorCode::io_error, "open terminal policy filesystem root");
    }
    if (path == "/") return current;
    for (const auto &component : path.relative_path()) {
        const std::string text = component.string();
        if (text.empty() || text == "." || text == ".." ||
            text.find('/') != std::string::npos ||
            text.find('\0') != std::string::npos) {
            return Status{ErrorCode::invalid_argument,
                          "terminal policy root has an invalid path component"};
        }
        FileDescriptor next(::openat(
            current.get(), text.c_str(),
            O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
        if (next.get() < 0) {
            return error_status(
                ErrorCode::io_error,
                "open terminal policy root path component");
        }
        current = std::move(next);
    }
    return current;
}

[[nodiscard]] Status validate_owner_only_directory(
    int descriptor, std::uint32_t expected_uid, std::string_view label) {
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return error_status(ErrorCode::io_error, "fstat terminal policy directory");
    }
    if (!S_ISDIR(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      std::string(label) + " is not a directory"};
    }
    if (metadata.st_uid != static_cast<uid_t>(expected_uid)) {
        return Status{ErrorCode::io_error,
                      std::string(label) + " owner is not the configured daemon uid"};
    }
    if ((metadata.st_mode & static_cast<mode_t>(0077)) != 0 ||
        (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) != 0) {
        return Status{ErrorCode::io_error,
                      std::string(label) + " is not owner-only"};
    }
    return Status::success();
}

[[nodiscard]] Result<std::vector<std::string>> list_directory(
    int descriptor, std::size_t maximum, std::string_view label) {
    const int duplicate = ::fcntl(descriptor, F_DUPFD_CLOEXEC, 3);
    if (duplicate < 0) {
        return error_status(ErrorCode::io_error, "duplicate terminal policy directory");
    }
    DIR *directory = ::fdopendir(duplicate);
    if (directory == nullptr) {
        const int saved_errno = errno;
        static_cast<void>(::close(duplicate));
        return error_status(ErrorCode::io_error, "fdopendir terminal policy", saved_errno);
    }
    std::vector<std::string> names;
    errno = 0;
    while (dirent *entry = ::readdir(directory)) {
        const std::string_view name(entry->d_name);
        if (name == "." || name == "..") continue;
        if (name.empty() || name.front() == '.') {
            static_cast<void>(::closedir(directory));
            return Status{ErrorCode::io_error,
                          std::string(label) + " contains a hidden or empty entry"};
        }
        if (names.size() >= maximum) {
            static_cast<void>(::closedir(directory));
            return Status{ErrorCode::resource_exhausted,
                          std::string(label) + " exceeds the v1 entry bound"};
        }
        names.emplace_back(name);
        errno = 0;
    }
    const int read_error = errno;
    if (::closedir(directory) != 0 && read_error == 0) {
        return error_status(ErrorCode::io_error, "close terminal policy directory");
    }
    if (read_error != 0) {
        return error_status(ErrorCode::io_error, "read terminal policy directory", read_error);
    }
    std::sort(names.begin(), names.end());
    return names;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_record_file(
    int directory_fd, std::string_view name, std::uint32_t expected_uid) {
    const std::string owned_name(name);
    FileDescriptor descriptor(::openat(
        directory_fd, owned_name.c_str(),
        O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK));
    if (descriptor.get() < 0) {
        return error_status(ErrorCode::io_error, "open terminal policy record");
    }
    struct stat before {};
    if (::fstat(descriptor.get(), &before) != 0) {
        return error_status(ErrorCode::io_error, "fstat terminal policy record");
    }
    if (!S_ISREG(before.st_mode) || before.st_nlink != 1 ||
        before.st_uid != static_cast<uid_t>(expected_uid) ||
        (before.st_mode & static_cast<mode_t>(0077)) != 0 ||
        (before.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) != 0) {
        return Status{ErrorCode::io_error,
                      "terminal policy record is not a single-link owner-only regular file"};
    }
    if (before.st_size < 0 ||
        static_cast<std::uint64_t>(before.st_size) > kMaximumProfileFileBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal policy record exceeds the v1 byte bound"};
    }
    std::vector<std::uint8_t> bytes;
    bytes.reserve(static_cast<std::size_t>(before.st_size));
    std::array<std::uint8_t, 4096U> buffer{};
    while (true) {
        const ssize_t count = ::read(descriptor.get(), buffer.data(), buffer.size());
        if (count > 0) {
            const std::size_t amount = static_cast<std::size_t>(count);
            if (bytes.size() > kMaximumProfileFileBytes - amount) {
                return Status{ErrorCode::resource_exhausted,
                              "terminal policy record grew beyond the v1 byte bound"};
            }
            bytes.insert(bytes.end(), buffer.begin(), buffer.begin() + static_cast<std::ptrdiff_t>(amount));
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) {
            return error_status(ErrorCode::io_error, "read terminal policy record");
        }
        break;
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0) {
        return error_status(ErrorCode::io_error, "refstat terminal policy record");
    }
    if (before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
        before.st_size != after.st_size || before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
        before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
        before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
        before.st_ctim.tv_nsec != after.st_ctim.tv_nsec ||
        bytes.size() != static_cast<std::size_t>(after.st_size)) {
        return Status{ErrorCode::io_error,
                      "terminal policy record changed while it was read"};
    }
    return bytes;
}

[[nodiscard]] bool ends_with(std::string_view text, std::string_view suffix) {
    return text.size() >= suffix.size() &&
           text.substr(text.size() - suffix.size()) == suffix;
}

}  // namespace

Status validate_dimensions(const Dimensions &dimensions) {
    if (dimensions.columns == 0U || dimensions.rows == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "terminal dimensions must be nonzero"};
    }
    return Status::success();
}

Status validate_cgroup_resource_limits(const CgroupResourceLimits &limits) {
    if (limits.maximum_processes.has_value() &&
        (*limits.maximum_processes == 0U ||
         *limits.maximum_processes > static_cast<std::uint64_t>(
                                         std::numeric_limits<pid_t>::max()))) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pids.max must be in the host pid_t range"};
    }
    if (limits.cpu_period_microseconds.has_value() &&
        !limits.cpu_quota_microseconds.has_value()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup cpu period requires an explicit cpu quota"};
    }
    if (limits.cpu_quota_microseconds.has_value() &&
        (*limits.cpu_quota_microseconds < kCgroupMinimumCpuBandwidthMicroseconds ||
         *limits.cpu_quota_microseconds > static_cast<std::uint64_t>(
                                                std::numeric_limits<std::int64_t>::max()))) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup cpu quota must be in 1000..INT64_MAX microseconds"};
    }
    if (limits.cpu_period_microseconds.has_value() &&
        (*limits.cpu_period_microseconds < kCgroupMinimumCpuBandwidthMicroseconds ||
         *limits.cpu_period_microseconds > kCgroupMaximumCpuPeriodMicroseconds)) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup cpu period must be in 1000..1000000 microseconds"};
    }
    const bool has_io_limits = has_cgroup_io_limits(limits);
    if (limits.io_device.has_value() != has_io_limits) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup I/O policy requires one device and at least one ceiling"};
    }
    if (limits.io_device.has_value() && limits.io_device->major == 0U &&
        limits.io_device->minor == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox cgroup I/O device 0:0 is invalid"};
    }
    const auto validate_io_ceiling = [](
                                         const std::optional<std::uint64_t> &value,
                                         std::string_view label) -> Status {
        if (value.has_value() &&
            (*value == 0U ||
             *value > static_cast<std::uint64_t>(
                          std::numeric_limits<std::int64_t>::max()))) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup " + std::string(label) +
                    " must be in 1..INT64_MAX"};
        }
        return Status::success();
    };
    for (const auto &[value, label] : std::array{
             std::pair{&limits.maximum_io_read_bytes_per_second,
                       std::string_view{"I/O rbps"}},
             std::pair{&limits.maximum_io_write_bytes_per_second,
                       std::string_view{"I/O wbps"}},
             std::pair{&limits.maximum_io_read_operations_per_second,
                       std::string_view{"I/O riops"}},
             std::pair{&limits.maximum_io_write_operations_per_second,
                       std::string_view{"I/O wiops"}},
         }) {
        const Status valid = validate_io_ceiling(*value, label);
        if (!valid.ok()) return valid;
    }
    if (!limits.maximum_memory_high_bytes.has_value() &&
        !limits.maximum_memory_bytes.has_value() &&
        !limits.maximum_swap_bytes.has_value()) {
        return Status::success();
    }

    errno = 0;
    const long page_size = ::sysconf(_SC_PAGESIZE);
    if (page_size <= 0) {
        return Status{
            ErrorCode::unsupported,
            "unable to discover the host page size for Ratox cgroup policy: " +
                std::string(std::strerror(errno == 0 ? EINVAL : errno))};
    }
    const auto page = static_cast<std::uint64_t>(page_size);
    if (limits.maximum_memory_high_bytes.has_value() &&
        (*limits.maximum_memory_high_bytes == 0U ||
         (*limits.maximum_memory_high_bytes % page) != 0U)) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup memory.high must be positive and page aligned"};
    }
    if (limits.maximum_memory_bytes.has_value() &&
        (*limits.maximum_memory_bytes == 0U ||
         (*limits.maximum_memory_bytes % page) != 0U)) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup memory.max must be positive and page aligned"};
    }
    if (limits.maximum_swap_bytes.has_value() &&
        (*limits.maximum_swap_bytes % page) != 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup memory.swap.max must be page aligned"};
    }
    if (limits.maximum_memory_high_bytes.has_value() &&
        limits.maximum_memory_bytes.has_value() &&
        *limits.maximum_memory_high_bytes > *limits.maximum_memory_bytes) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup memory.high must not exceed memory.max"};
    }
    return Status::success();
}

Status validate_cgroup_aggregate_limits(
    const CgroupAggregateLimits &limits) {
    CgroupResourceLimits equivalent;
    equivalent.maximum_processes = limits.maximum_reserved_processes;
    // memory.high is a runtime throttle and is not an aggregate reservation
    // dimension; aggregate memory remains charged against the hard maximum.
    equivalent.maximum_memory_bytes = limits.maximum_reserved_memory_bytes;
    equivalent.maximum_swap_bytes = limits.maximum_reserved_swap_bytes;
    equivalent.cpu_quota_microseconds =
        limits.maximum_reserved_cpu_quota_microseconds;
    equivalent.cpu_period_microseconds = limits.cpu_period_microseconds;
    const Status valid = validate_cgroup_resource_limits(equivalent);
    if (!valid.ok()) {
        return Status{
            valid.code(),
            "invalid Ratox aggregate cgroup reservation ceiling: " +
                valid.message()};
    }
    return Status::success();
}

Status validate_cgroup_pressure_admission_limits(
    const CgroupPressureAdmissionLimits &limits) {
    const auto validate_threshold = [&limits](
                                        const std::optional<std::uint16_t> &value,
                                        std::string_view label) -> Status {
        if (!value.has_value()) return Status::success();
        if (*value > kCgroupMaximumPressureBasisPoints) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup pressure admission " + std::string(label) +
                    " must be in 0..10000 basis points"};
        }
        if (limits.hysteresis_basis_points > *value) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup pressure admission hysteresis must not exceed " +
                    std::string(label)};
        }
        return Status::success();
    };

    if (limits.hysteresis_basis_points > kCgroupMaximumPressureBasisPoints) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure admission hysteresis must be in 0..10000 basis points"};
    }
    if (limits.empty() && limits.hysteresis_basis_points != 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure admission hysteresis requires at least one threshold"};
    }
    for (const auto &[threshold, label] : std::array{
             std::pair{
                 &limits.maximum_cpu_some_average_10_basis_points,
                 std::string_view{"CPU some avg10 maximum"}},
             std::pair{
                 &limits.maximum_memory_full_average_10_basis_points,
                 std::string_view{"memory full avg10 maximum"}},
             std::pair{
                 &limits.maximum_io_full_average_10_basis_points,
                 std::string_view{"I/O full avg10 maximum"}},
         }) {
        const Status valid = validate_threshold(*threshold, label);
        if (!valid.ok()) return valid;
    }

    const bool triggers_configured = !limits.triggers_empty();
    if (triggers_configured != limits.trigger_window_microseconds.has_value()) {
        return Status{
            ErrorCode::invalid_argument,
            triggers_configured
                ? "Ratox cgroup PSI triggers require one common tracking window"
                : "Ratox cgroup pressure trigger window requires at least one trigger"};
    }
    if (!triggers_configured) return Status::success();

    const std::uint64_t window = *limits.trigger_window_microseconds;
    if (window < kCgroupMinimumPressureTriggerWindowMicroseconds ||
        window > kCgroupMaximumPressureTriggerWindowMicroseconds) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure trigger window must be in 2000000..10000000 microseconds"};
    }
    if (window % kCgroupPressureTriggerWindowQuantumMicroseconds != 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure trigger window must be a multiple of 2000000 microseconds"};
    }

    const auto validate_trigger = [window](
                                      const std::optional<std::uint64_t> &stall,
                                      const auto &matching_average,
                                      std::string_view label) -> Status {
        if (!stall.has_value()) return Status::success();
        if (!matching_average.has_value()) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup pressure " + std::string(label) +
                    " trigger requires its matching avg10 threshold"};
        }
        if (*stall == 0U || *stall > window) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup pressure " + std::string(label) +
                    " trigger stall time must be in 1..window microseconds"};
        }
        return Status::success();
    };

    Status valid = validate_trigger(
        limits.cpu_some_trigger_stall_microseconds,
        limits.maximum_cpu_some_average_10_basis_points,
        "CPU some");
    if (!valid.ok()) return valid;
    valid = validate_trigger(
        limits.memory_full_trigger_stall_microseconds,
        limits.maximum_memory_full_average_10_basis_points,
        "memory full");
    if (!valid.ok()) return valid;
    return validate_trigger(
        limits.io_full_trigger_stall_microseconds,
        limits.maximum_io_full_average_10_basis_points,
        "I/O full");
}

Result<CgroupAggregateCharge> resolve_cgroup_aggregate_charge(
    const CgroupAggregateLimits &aggregate_limits,
    const CgroupResourceLimits &session_limits) {
    const Status aggregate_valid =
        validate_cgroup_aggregate_limits(aggregate_limits);
    if (!aggregate_valid.ok()) return aggregate_valid;
    const Status session_valid = validate_cgroup_resource_limits(session_limits);
    if (!session_valid.ok()) return session_valid;

    CgroupAggregateCharge charge;
    const auto resolve_dimension = [](
        const std::optional<std::uint64_t> &aggregate,
        const std::optional<std::uint64_t> &session,
        std::string_view name,
        std::uint64_t &resolved) -> Status {
        if (!aggregate.has_value()) return Status::success();
        if (!session.has_value()) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox aggregate " + std::string(name) +
                    " reservation requires a finite per-session cgroup limit"};
        }
        if (*session > *aggregate) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox per-session " + std::string(name) +
                    " reservation exceeds the aggregate host ceiling"};
        }
        resolved = *session;
        return Status::success();
    };

    Status valid = resolve_dimension(
        aggregate_limits.maximum_reserved_processes,
        session_limits.maximum_processes, "process",
        charge.reserved_processes);
    if (!valid.ok()) return valid;
    valid = resolve_dimension(
        aggregate_limits.maximum_reserved_memory_bytes,
        session_limits.maximum_memory_bytes, "memory",
        charge.reserved_memory_bytes);
    if (!valid.ok()) return valid;
    valid = resolve_dimension(
        aggregate_limits.maximum_reserved_swap_bytes,
        session_limits.maximum_swap_bytes, "swap",
        charge.reserved_swap_bytes);
    if (!valid.ok()) return valid;

    if (!aggregate_limits.maximum_reserved_cpu_quota_microseconds.has_value()) {
        return charge;
    }
    if (!session_limits.cpu_quota_microseconds.has_value()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox aggregate CPU reservation requires a finite per-session cpu.max quota"};
    }

    const std::uint64_t aggregate_period =
        aggregate_limits.cpu_period_microseconds.value_or(
            kCgroupDefaultCpuPeriodMicroseconds);
    const std::uint64_t session_period =
        session_limits.cpu_period_microseconds.value_or(
            kCgroupDefaultCpuPeriodMicroseconds);
    // Validation currently constrains both periods to a positive range. Keep
    // the denominator precondition explicit at its first arithmetic use so a
    // future validation regression still fails closed instead of dividing by
    // zero in the exact rational comparator.
    if (aggregate_period == 0U || session_period == 0U) {
        return Status{
            ErrorCode::internal_error,
            "validated Ratox CPU periods became zero during aggregate normalization"};
    }
    if (compare_positive_fractions(
            *session_limits.cpu_quota_microseconds, session_period,
            *aggregate_limits.maximum_reserved_cpu_quota_microseconds,
            aggregate_period) > 0) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox per-session CPU reservation exceeds the aggregate host ceiling"};
    }

    const std::uint64_t common_period =
        std::gcd(session_period, aggregate_period);
    // Both periods are validated as positive above, so std::gcd must return a
    // positive common divisor no larger than either operand. Reassert that
    // arithmetic invariant at the division boundary: this keeps future
    // validator changes fail closed and makes the exact-normalization proof
    // local rather than implicit.
    if (common_period == 0U || common_period > session_period ||
        common_period > aggregate_period) {
        return Status{
            ErrorCode::internal_error,
            "Ratox CPU reservation normalization produced an invalid common period"};
    }
    const std::uint64_t source_divisor = session_period / common_period;
    const std::uint64_t target_multiplier = aggregate_period / common_period;
    if (source_divisor == 0U || target_multiplier == 0U) {
        return Status{
            ErrorCode::internal_error,
            "Ratox CPU reservation normalization produced a zero scale"};
    }
    if ((*session_limits.cpu_quota_microseconds % source_divisor) != 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox per-session CPU reservation is not exactly representable at the aggregate accounting period"};
    }
    const std::uint64_t reduced_quota =
        *session_limits.cpu_quota_microseconds / source_divisor;
    if (reduced_quota >
        std::numeric_limits<std::uint64_t>::max() / target_multiplier) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox per-session CPU reservation overflows exact aggregate normalization"};
    }
    charge.reserved_cpu_quota_microseconds =
        reduced_quota * target_multiplier;
    if (charge.reserved_cpu_quota_microseconds >
        *aggregate_limits.maximum_reserved_cpu_quota_microseconds) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox per-session CPU reservation exceeds the aggregate host ceiling"};
    }
    return charge;
}

Status validate_cgroup_aggregate_reservation(
    const CgroupAggregateLimits &aggregate_limits,
    const CgroupResourceLimits &session_limits) {
    auto charge = resolve_cgroup_aggregate_charge(
        aggregate_limits, session_limits);
    return charge.ok() ? Status::success() : charge.status();
}

Result<CgroupResourceLimits> compose_cgroup_resource_limits(
    const CgroupResourceLimits &host_limits,
    const CgroupResourceLimits &profile_limits) {
    const Status host_valid = validate_cgroup_resource_limits(host_limits);
    if (!host_valid.ok()) return host_valid;
    const Status profile_valid = validate_cgroup_resource_limits(profile_limits);
    if (!profile_valid.ok()) return profile_valid;

    CgroupResourceLimits effective;
    effective.maximum_processes = stricter_optional_maximum(
        host_limits.maximum_processes,
        profile_limits.maximum_processes);
    effective.maximum_memory_high_bytes = stricter_optional_maximum(
        host_limits.maximum_memory_high_bytes,
        profile_limits.maximum_memory_high_bytes);
    effective.maximum_memory_bytes = stricter_optional_maximum(
        host_limits.maximum_memory_bytes,
        profile_limits.maximum_memory_bytes);
    effective.maximum_swap_bytes = stricter_optional_maximum(
        host_limits.maximum_swap_bytes,
        profile_limits.maximum_swap_bytes);
    if (host_limits.io_device.has_value() &&
        profile_limits.io_device.has_value() &&
        *host_limits.io_device != *profile_limits.io_device) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox host and profile cgroup I/O devices do not match"};
    }
    effective.io_device = host_limits.io_device.has_value()
                              ? host_limits.io_device
                              : profile_limits.io_device;
    effective.maximum_io_read_bytes_per_second = stricter_optional_maximum(
        host_limits.maximum_io_read_bytes_per_second,
        profile_limits.maximum_io_read_bytes_per_second);
    effective.maximum_io_write_bytes_per_second = stricter_optional_maximum(
        host_limits.maximum_io_write_bytes_per_second,
        profile_limits.maximum_io_write_bytes_per_second);
    effective.maximum_io_read_operations_per_second = stricter_optional_maximum(
        host_limits.maximum_io_read_operations_per_second,
        profile_limits.maximum_io_read_operations_per_second);
    effective.maximum_io_write_operations_per_second = stricter_optional_maximum(
        host_limits.maximum_io_write_operations_per_second,
        profile_limits.maximum_io_write_operations_per_second);
    if (effective.maximum_memory_high_bytes.has_value() &&
        effective.maximum_memory_bytes.has_value()) {
        effective.maximum_memory_high_bytes = std::min(
            *effective.maximum_memory_high_bytes,
            *effective.maximum_memory_bytes);
    }

    if (!host_limits.cpu_quota_microseconds.has_value()) {
        effective.cpu_quota_microseconds =
            profile_limits.cpu_quota_microseconds;
        effective.cpu_period_microseconds =
            profile_limits.cpu_period_microseconds;
    } else if (!profile_limits.cpu_quota_microseconds.has_value()) {
        effective.cpu_quota_microseconds =
            host_limits.cpu_quota_microseconds;
        effective.cpu_period_microseconds =
            host_limits.cpu_period_microseconds;
    } else {
        const std::uint64_t host_period =
            host_limits.cpu_period_microseconds.value_or(
                kCgroupDefaultCpuPeriodMicroseconds);
        const std::uint64_t profile_period =
            profile_limits.cpu_period_microseconds.value_or(
                kCgroupDefaultCpuPeriodMicroseconds);
        const int comparison = compare_positive_fractions(
            *host_limits.cpu_quota_microseconds, host_period,
            *profile_limits.cpu_quota_microseconds, profile_period);
        if (comparison <= 0) {
            effective.cpu_quota_microseconds =
                host_limits.cpu_quota_microseconds;
            effective.cpu_period_microseconds =
                host_limits.cpu_period_microseconds;
        } else {
            effective.cpu_quota_microseconds =
                profile_limits.cpu_quota_microseconds;
            effective.cpu_period_microseconds =
                profile_limits.cpu_period_microseconds;
        }
    }

    const Status effective_valid = validate_cgroup_resource_limits(effective);
    if (!effective_valid.ok()) return effective_valid;
    return effective;
}

Status validate_profile(const Profile &profile) {
    if (!valid_profile_id(profile.id)) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile id is not a lowercase v1 slug"};
    }
    if (profile.arguments.empty() ||
        profile.arguments.size() > kMaximumArguments) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile argument count is outside the v1 bound"};
    }
    std::size_t argument_bytes = 0U;
    for (const std::string &argument : profile.arguments) {
        if (argument.empty() || argument.size() > kMaximumArgumentBytes ||
            contains_nul(argument)) {
            return Status{ErrorCode::invalid_argument,
                          "terminal profile contains an invalid argument"};
        }
        if (argument_bytes > kMaximumResolvedEnvironmentBytes - argument.size()) {
            return Status{ErrorCode::resource_exhausted,
                          "terminal profile argument bytes exceed the v1 bound"};
        }
        argument_bytes += argument.size();
    }
    if (!valid_absolute_path(profile.arguments.front(), false)) {
        return Status{ErrorCode::invalid_argument,
                      "terminal executable must be an absolute normalized path"};
    }
    if (!valid_absolute_path(profile.working_directory, true)) {
        return Status{ErrorCode::invalid_argument,
                      "terminal working directory must be an absolute normalized path"};
    }
    if (!valid_terminal_type(profile.terminal_type)) {
        return Status{ErrorCode::invalid_argument,
                      "terminal type is outside the v1 token grammar"};
    }
    if (profile.inherited_environment.size() > kMaximumEnvironmentEntries ||
        profile.environment.size() > kMaximumEnvironmentEntries ||
        profile.inherited_environment.size() + profile.environment.size() + 1U >
            kMaximumEnvironmentEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal environment entry count exceeds the v1 bound"};
    }
    std::vector<std::string> environment_names;
    environment_names.reserve(
        profile.inherited_environment.size() + profile.environment.size() + 1U);
    for (const std::string &name : profile.inherited_environment) {
        if (!valid_environment_name(name) ||
            !safe_inherited_environment_name(name) ||
            hazardous_environment_name(name)) {
            return Status{ErrorCode::invalid_argument,
                          "terminal inherited environment name is not on the v1 safe list"};
        }
        environment_names.push_back(name);
    }
    for (const EnvironmentEntry &entry : profile.environment) {
        if (!valid_environment_name(entry.name) ||
            hazardous_environment_name(entry.name) ||
            entry.value.size() > kMaximumEnvironmentValueBytes ||
            contains_nul(entry.value)) {
            return Status{ErrorCode::invalid_argument,
                          "terminal fixed environment entry is invalid"};
        }
        environment_names.push_back(entry.name);
    }
    if (profile.toolbox_sha256.has_value()) {
        const auto toolbox = std::find_if(
            profile.environment.begin(), profile.environment.end(),
            [](const EnvironmentEntry &entry) {
                return entry.name == "IOTOX_RESCUE_TOOLBOX";
            });
        if (!profile.executable_sha256.has_value() ||
            toolbox == profile.environment.end() ||
            !valid_absolute_path(toolbox->value, false)) {
            return Status{
                ErrorCode::invalid_argument,
                "terminal toolbox digest requires executable digest and one absolute IOTOX_RESCUE_TOOLBOX directory"};
        }
    }
    environment_names.push_back("TERM");
    std::sort(environment_names.begin(), environment_names.end());
    if (std::adjacent_find(environment_names.begin(), environment_names.end()) !=
        environment_names.end()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal environment names must be unique"};
    }
    if (profile.identity.mode != IdentityMode::inherit &&
        profile.identity.mode != IdentityMode::exact &&
        profile.identity.mode != IdentityMode::account) {
        return Status{ErrorCode::invalid_argument,
                      "terminal identity policy is unassigned"};
    }
    if (profile.identity.mode == IdentityMode::inherit &&
        (profile.identity.uid != 0U || profile.identity.gid != 0U ||
         !profile.identity.clear_supplementary_groups ||
         !profile.identity.supplementary_groups.empty())) {
        return Status{ErrorCode::invalid_argument,
                      "inherited terminal identity must use the canonical zero fields"};
    }
    if (profile.identity.mode == IdentityMode::exact &&
        (!profile.identity.clear_supplementary_groups ||
         !profile.identity.supplementary_groups.empty())) {
        return Status{ErrorCode::invalid_argument,
                      "exact terminal identity must clear supplementary groups"};
    }
    if (profile.identity.mode == IdentityMode::account) {
        if (profile.identity.clear_supplementary_groups) {
            return Status{
                ErrorCode::invalid_argument,
                "account terminal identity must use its frozen supplementary groups"};
        }
        if (profile.identity.supplementary_groups.size() >
                kMaximumSupplementaryGroups ||
            !std::is_sorted(
                profile.identity.supplementary_groups.begin(),
                profile.identity.supplementary_groups.end()) ||
            std::adjacent_find(
                profile.identity.supplementary_groups.begin(),
                profile.identity.supplementary_groups.end()) !=
                profile.identity.supplementary_groups.end() ||
            std::binary_search(
                profile.identity.supplementary_groups.begin(),
                profile.identity.supplementary_groups.end(),
                profile.identity.gid)) {
            return Status{
                ErrorCode::invalid_argument,
                "account terminal supplementary groups must be sorted, unique, bounded, and exclude the primary gid"};
        }
    }
    if (profile.confinement != ConfinementMode::compatibility &&
        profile.confinement != ConfinementMode::baseline &&
        profile.confinement != ConfinementMode::strict) {
        return Status{ErrorCode::invalid_argument,
                      "terminal confinement policy is unassigned"};
    }
    if (profile.confinement == ConfinementMode::strict &&
        profile.working_directory == "/") {
        return Status{ErrorCode::invalid_argument,
                      "strict terminal confinement requires a non-root working directory"};
    }
    if (profile.allow_privilege_escalation &&
        profile.confinement != ConfinementMode::compatibility) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal privilege escalation requires compatibility confinement"};
    }
    if (profile.allow_privilege_escalation &&
        profile.identity.mode != IdentityMode::inherit &&
        profile.identity.uid == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal privilege escalation must start from a non-root identity"};
    }
    const Status dimensions = validate_dimension_policy(profile.dimensions);
    if (!dimensions.ok()) return dimensions;
    const Status limits = validate_resource_limits(profile.limits);
    if (!limits.ok()) return limits;
    const Status cgroup_limits =
        validate_cgroup_resource_limits(profile.cgroup_limits);
    if (!cgroup_limits.ok()) return cgroup_limits;
    const Status hangup = validate_grace(profile.hangup_grace, "terminal hangup grace");
    if (!hangup.ok()) return hangup;
    const Status terminate =
        validate_grace(profile.terminate_grace, "terminal terminate grace");
    if (!terminate.ok()) return terminate;
    const Status kill = validate_grace(profile.kill_reap_grace, "terminal kill grace");
    if (!kill.ok()) return kill;
    return Status::success();
}

Status validate_binding(const Binding &binding) {
    if (std::all_of(binding.principal_id.begin(), binding.principal_id.end(),
                    [](std::uint8_t value) { return value == 0U; })) {
        return Status{ErrorCode::invalid_argument,
                      "terminal binding principal must be nonzero"};
    }
    if (!valid_profile_id(binding.profile_id)) {
        return Status{ErrorCode::invalid_argument,
                      "terminal binding profile id is invalid"};
    }
    return Status::success();
}

Result<Dimensions> accept_dimensions(
    const DimensionPolicy &policy, const Dimensions &requested) {
    const Status valid_policy = validate_dimension_policy(policy);
    if (!valid_policy.ok()) return valid_policy;
    const Status valid_request = validate_dimensions(requested);
    if (!valid_request.ok()) return valid_request;
    Dimensions accepted{
        std::clamp(
            requested.columns, policy.minimum.columns, policy.maximum.columns),
        std::clamp(requested.rows, policy.minimum.rows, policy.maximum.rows)};
    return accepted;
}

Result<std::vector<EnvironmentEntry>> resolve_environment(
    const Profile &profile, std::span<const EnvironmentEntry> ambient_environment) {
    const Status valid = validate_profile(profile);
    if (!valid.ok()) return valid;
    if (ambient_environment.size() > kMaximumEnvironmentEntries * 4U) {
        return Status{ErrorCode::resource_exhausted,
                      "ambient environment exceeds the resolver scan bound"};
    }
    std::vector<EnvironmentEntry> ambient(
        ambient_environment.begin(), ambient_environment.end());
    for (const EnvironmentEntry &entry : ambient) {
        if (!valid_environment_name(entry.name) || contains_nul(entry.value) ||
            entry.value.size() > kMaximumEnvironmentValueBytes) {
            return Status{ErrorCode::invalid_argument,
                          "ambient environment entry is invalid"};
        }
    }
    std::sort(ambient.begin(), ambient.end(), [](const auto &left, const auto &right) {
        return left.name < right.name;
    });
    if (std::adjacent_find(
            ambient.begin(), ambient.end(), [](const auto &left, const auto &right) {
                return left.name == right.name;
            }) != ambient.end()) {
        return Status{ErrorCode::invalid_argument,
                      "ambient environment contains duplicate names"};
    }

    std::vector<EnvironmentEntry> resolved = profile.environment;
    for (const std::string &name : profile.inherited_environment) {
        const auto found = std::lower_bound(
            ambient.begin(), ambient.end(), name,
            [](const EnvironmentEntry &entry, std::string_view key) {
                return entry.name < key;
            });
        if (found != ambient.end() && found->name == name) {
            resolved.push_back(*found);
        }
    }
    resolved.push_back(EnvironmentEntry{"TERM", profile.terminal_type});
    std::sort(resolved.begin(), resolved.end(), [](const auto &left, const auto &right) {
        return left.name < right.name;
    });
    std::size_t bytes = 0U;
    for (const EnvironmentEntry &entry : resolved) {
        const std::size_t name_bytes = entry.name.size() + 1U;
        if (name_bytes > kMaximumResolvedEnvironmentBytes ||
            entry.value.size() > kMaximumResolvedEnvironmentBytes - name_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "resolved terminal environment exceeds the v1 byte bound"};
        }
        const std::size_t entry_bytes = name_bytes + entry.value.size();
        if (bytes > kMaximumResolvedEnvironmentBytes - entry_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "resolved terminal environment exceeds the v1 byte bound"};
        }
        bytes += entry_bytes;
    }
    return resolved;
}

Status validate_resolved_profile(const ResolvedProfile &resolved) {
    const Status valid = validate_profile(resolved.profile);
    if (!valid.ok()) return valid;
    if (!resolved.profile.enabled || resolved.policy_generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "resolved terminal profile is not enabled or generation-bound"};
    }
    auto accepted = accept_dimensions(
        resolved.profile.dimensions, resolved.accepted_dimensions);
    if (!accepted.ok()) return accepted.status();
    if (accepted.value() != resolved.accepted_dimensions) {
        return Status{ErrorCode::invalid_argument,
                      "resolved terminal dimensions are outside the profile policy"};
    }
    if (resolved.environment.empty() ||
        resolved.environment.size() > kMaximumEnvironmentEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "resolved terminal environment count is outside the v1 bound"};
    }

    bool saw_term = false;
    std::vector<bool> saw_fixed(resolved.profile.environment.size(), false);
    std::string_view previous;
    std::size_t total_bytes = 0U;
    for (const EnvironmentEntry &entry : resolved.environment) {
        if (!valid_environment_name(entry.name) || contains_nul(entry.value) ||
            entry.value.size() > kMaximumEnvironmentValueBytes) {
            return Status{ErrorCode::invalid_argument,
                          "resolved terminal environment entry is invalid"};
        }
        if (!previous.empty() && previous >= entry.name) {
            return Status{ErrorCode::invalid_argument,
                          "resolved terminal environment is not strictly sorted"};
        }
        previous = entry.name;

        bool admitted = false;
        if (entry.name == "TERM") {
            if (entry.value != resolved.profile.terminal_type) {
                return Status{ErrorCode::invalid_argument,
                              "resolved TERM differs from the frozen profile"};
            }
            saw_term = true;
            admitted = true;
        } else {
            for (std::size_t index = 0U;
                 index < resolved.profile.environment.size(); ++index) {
                const EnvironmentEntry &fixed = resolved.profile.environment[index];
                if (fixed.name == entry.name) {
                    if (fixed.value != entry.value) {
                        return Status{ErrorCode::invalid_argument,
                                      "resolved fixed environment value changed"};
                    }
                    saw_fixed[index] = true;
                    admitted = true;
                    break;
                }
            }
            if (!admitted && std::find(
                    resolved.profile.inherited_environment.begin(),
                    resolved.profile.inherited_environment.end(),
                    entry.name) != resolved.profile.inherited_environment.end()) {
                admitted = true;
            }
        }
        if (!admitted || (entry.name != "TERM" && hazardous_environment_name(entry.name))) {
            return Status{ErrorCode::invalid_argument,
                          "resolved terminal environment contains an unbound name"};
        }
        const std::size_t name_bytes = entry.name.size() + 1U;
        if (entry.value.size() > kMaximumResolvedEnvironmentBytes - name_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "resolved terminal environment exceeds the v1 byte bound"};
        }
        const std::size_t entry_bytes = name_bytes + entry.value.size();
        if (total_bytes > kMaximumResolvedEnvironmentBytes - entry_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "resolved terminal environment exceeds the v1 byte bound"};
        }
        total_bytes += entry_bytes;
    }
    if (!saw_term || std::find(saw_fixed.begin(), saw_fixed.end(), false) !=
                         saw_fixed.end()) {
        return Status{ErrorCode::invalid_argument,
                      "resolved terminal environment omitted a required frozen entry"};
    }
    return Status::success();
}

namespace {

enum class ProfileRecordVersion : std::uint8_t {
    v1 = 1U,
    v2 = 2U,
    v3 = 3U,
    v4 = 4U,
    v5 = 5U,
    v6 = 6U,
    v7 = 7U,
};

[[nodiscard]] std::string_view confinement_name(ConfinementMode mode) {
    switch (mode) {
        case ConfinementMode::compatibility: return "compatibility";
        case ConfinementMode::baseline: return "baseline";
        case ConfinementMode::strict: return "strict";
    }
    return "unassigned";
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_profile_record_version(
    const Profile &profile, ProfileRecordVersion version) {
    const Status valid = validate_profile(profile);
    if (!valid.ok()) return valid;
    if (version == ProfileRecordVersion::v1 &&
        profile.confinement != ConfinementMode::compatibility) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile v1 cannot encode a confinement policy"};
    }
    if (version != ProfileRecordVersion::v3 &&
        version != ProfileRecordVersion::v4 &&
        version != ProfileRecordVersion::v5 &&
        version != ProfileRecordVersion::v6 &&
        version != ProfileRecordVersion::v7 &&
        !profile.cgroup_limits.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile v1/v2 cannot encode a cgroup budget"};
    }
    if (version == ProfileRecordVersion::v3 &&
        profile.cgroup_limits.maximum_memory_high_bytes.has_value()) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal profile v3 cannot encode a memory.high throttle"};
    }
    if (version != ProfileRecordVersion::v5 &&
        version != ProfileRecordVersion::v6 &&
        version != ProfileRecordVersion::v7 &&
        (profile.cgroup_limits.io_device.has_value() ||
         has_cgroup_io_limits(profile.cgroup_limits))) {
        return Status{
            ErrorCode::invalid_argument,
                      "terminal profile v1-v4 cannot encode a cgroup I/O policy"};
    }
    if (version != ProfileRecordVersion::v6 &&
        version != ProfileRecordVersion::v7 &&
        profile.allow_privilege_escalation) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal profile v1-v5 cannot encode privilege escalation policy"};
    }
    if (version != ProfileRecordVersion::v6 &&
        version != ProfileRecordVersion::v7 &&
        profile.identity.mode == IdentityMode::account) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal profile v1-v5 cannot encode an account identity"};
    }
    if (version != ProfileRecordVersion::v7 &&
        (profile.executable_sha256.has_value() ||
         profile.toolbox_sha256.has_value())) {
        return Status{
            ErrorCode::invalid_argument,
            "terminal profile v1-v6 cannot encode executable digest policy"};
    }
    std::vector<std::string> inherited = profile.inherited_environment;
    std::sort(inherited.begin(), inherited.end());
    std::vector<EnvironmentEntry> fixed = profile.environment;
    std::sort(fixed.begin(), fixed.end(), [](const auto &left, const auto &right) {
        return left.name < right.name;
    });

    std::ostringstream output;
    output.imbue(std::locale::classic());
    std::string_view header{};
    switch (version) {
        case ProfileRecordVersion::v1: header = kProfileHeaderV1; break;
        case ProfileRecordVersion::v2: header = kProfileHeaderV2; break;
        case ProfileRecordVersion::v3: header = kProfileHeaderV3; break;
        case ProfileRecordVersion::v4: header = kProfileHeaderV4; break;
        case ProfileRecordVersion::v5: header = kProfileHeaderV5; break;
        case ProfileRecordVersion::v6: header = kProfileHeaderV6; break;
        case ProfileRecordVersion::v7: header = kProfileHeaderV7; break;
    }
    output << header
           << '\n'
           << "id=" << profile.id << '\n'
           << "enabled=" << (profile.enabled ? 1 : 0) << '\n';
    for (const std::string &argument : profile.arguments) {
        output << "argument-hex=" << hex_encode(argument) << '\n';
    }
    if (version == ProfileRecordVersion::v7) {
        output << "executable-sha256=";
        if (profile.executable_sha256.has_value()) {
            output << hex_encode(std::span<const std::uint8_t>{
                *profile.executable_sha256});
        } else {
            output << "none";
        }
        output << '\n' << "toolbox-sha256=";
        if (profile.toolbox_sha256.has_value()) {
            output << hex_encode(std::span<const std::uint8_t>{
                *profile.toolbox_sha256});
        } else {
            output << "none";
        }
        output << '\n';
    }
    output << "working-directory-hex=" << hex_encode(profile.working_directory) << '\n'
           << "terminal-type=" << profile.terminal_type << '\n';
    for (const std::string &name : inherited) {
        output << "inherit-environment=" << name << '\n';
    }
    for (const EnvironmentEntry &entry : fixed) {
        output << "environment-hex=" << entry.name << ':' << hex_encode(entry.value) << '\n';
    }
    if (profile.identity.mode == IdentityMode::inherit) {
        output << "identity=inherit\n";
    } else if (profile.identity.mode == IdentityMode::exact) {
        output << "identity=exact:" << profile.identity.uid << ':'
               << profile.identity.gid << ':'
               << (profile.identity.clear_supplementary_groups ? 1 : 0) << '\n';
    } else {
        output << "identity=account:" << profile.identity.uid << ':'
               << profile.identity.gid << '\n';
        for (const std::uint32_t group :
             profile.identity.supplementary_groups) {
            output << "supplementary-group=" << group << '\n';
        }
    }
    if (version != ProfileRecordVersion::v1) {
        output << "confinement=" << confinement_name(profile.confinement) << '\n';
    }
    if (version == ProfileRecordVersion::v6 ||
        version == ProfileRecordVersion::v7) {
        output << "allow-privilege-escalation="
               << (profile.allow_privilege_escalation ? 1 : 0) << '\n';
    }
    if (version == ProfileRecordVersion::v3 ||
        version == ProfileRecordVersion::v4 ||
        version == ProfileRecordVersion::v5 ||
        version == ProfileRecordVersion::v6 ||
        version == ProfileRecordVersion::v7) {
        const auto emit_optional = [&](
                                       std::string_view key,
                                       const std::optional<std::uint64_t> &value) {
            output << key;
            if (value.has_value()) {
                output << *value;
            } else {
                output << "none";
            }
            output << '\n';
        };
        emit_optional("cgroup-pids-max=", profile.cgroup_limits.maximum_processes);
        if (version == ProfileRecordVersion::v4 ||
            version == ProfileRecordVersion::v5 ||
            version == ProfileRecordVersion::v6 ||
            version == ProfileRecordVersion::v7) {
            emit_optional(
                "cgroup-memory-high-bytes=",
                profile.cgroup_limits.maximum_memory_high_bytes);
        }
        emit_optional(
            "cgroup-memory-max-bytes=",
            profile.cgroup_limits.maximum_memory_bytes);
        emit_optional(
            "cgroup-swap-max-bytes=",
            profile.cgroup_limits.maximum_swap_bytes);
        emit_optional(
            "cgroup-cpu-quota-us=",
            profile.cgroup_limits.cpu_quota_microseconds);
        emit_optional(
            "cgroup-cpu-period-us=",
            profile.cgroup_limits.cpu_period_microseconds);
        if (version == ProfileRecordVersion::v5 ||
            version == ProfileRecordVersion::v6 ||
            version == ProfileRecordVersion::v7) {
            output << "cgroup-io-device=";
            if (profile.cgroup_limits.io_device.has_value()) {
                output << profile.cgroup_limits.io_device->major << ':'
                       << profile.cgroup_limits.io_device->minor;
            } else {
                output << "none";
            }
            output << '\n';
            emit_optional(
                "cgroup-io-rbps=",
                profile.cgroup_limits.maximum_io_read_bytes_per_second);
            emit_optional(
                "cgroup-io-wbps=",
                profile.cgroup_limits.maximum_io_write_bytes_per_second);
            emit_optional(
                "cgroup-io-riops=",
                profile.cgroup_limits.maximum_io_read_operations_per_second);
            emit_optional(
                "cgroup-io-wiops=",
                profile.cgroup_limits.maximum_io_write_operations_per_second);
        }
    }
    output << "minimum-dimensions=" << profile.dimensions.minimum.columns << ':'
           << profile.dimensions.minimum.rows << '\n'
           << "initial-dimensions=" << profile.dimensions.initial.columns << ':'
           << profile.dimensions.initial.rows << '\n'
           << "maximum-dimensions=" << profile.dimensions.maximum.columns << ':'
           << profile.dimensions.maximum.rows << '\n'
           << "allow-resize=" << (profile.dimensions.allow_resize ? 1 : 0) << '\n'
           << "limit-cpu-seconds=" << profile.limits.cpu_seconds << '\n'
           << "limit-address-space-bytes=" << profile.limits.address_space_bytes << '\n'
           << "limit-file-size-bytes=" << profile.limits.file_size_bytes << '\n'
           << "limit-open-files=" << profile.limits.open_files << '\n'
           << "limit-processes=" << profile.limits.processes << '\n'
           << "hangup-grace-ms=" << profile.hangup_grace.count() << '\n'
           << "terminate-grace-ms=" << profile.terminate_grace.count() << '\n'
           << "kill-reap-grace-ms=" << profile.kill_reap_grace.count() << '\n';
    const std::string text = output.str();
    if (text.size() > kMaximumProfileFileBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "encoded terminal profile exceeds the local record byte bound"};
    }
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

}  // namespace

Result<std::vector<std::uint8_t>> encode_profile_record(const Profile &profile) {
    return encode_profile_record_version(profile, ProfileRecordVersion::v7);
}

Result<Profile> decode_profile_record(std::span<const std::uint8_t> bytes) {
    auto split = split_record(bytes, kMaximumProfileFileBytes, "terminal profile");
    if (!split.ok()) return split.status();
    const auto &lines = split.value();
    std::size_t index = 0U;
    if (lines.empty()) {
        return Status{ErrorCode::protocol_error,
                      "terminal profile header is invalid"};
    }
    ProfileRecordVersion record_version{};
    if (lines[index] == kProfileHeaderV1) {
        record_version = ProfileRecordVersion::v1;
    } else if (lines[index] == kProfileHeaderV2) {
        record_version = ProfileRecordVersion::v2;
    } else if (lines[index] == kProfileHeaderV3) {
        record_version = ProfileRecordVersion::v3;
    } else if (lines[index] == kProfileHeaderV4) {
        record_version = ProfileRecordVersion::v4;
    } else if (lines[index] == kProfileHeaderV5) {
        record_version = ProfileRecordVersion::v5;
    } else if (lines[index] == kProfileHeaderV6) {
        record_version = ProfileRecordVersion::v6;
    } else if (lines[index] == kProfileHeaderV7) {
        record_version = ProfileRecordVersion::v7;
    } else {
        return Status{ErrorCode::protocol_error,
                      "terminal profile header is invalid"};
    }
    ++index;
    Profile profile;
    profile.confinement = ConfinementMode::compatibility;
    if (index >= lines.size()) return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
    auto id = field_value(lines[index++], "id=");
    if (!id.ok()) return id.status();
    profile.id = std::string(id.value());
    if (index >= lines.size()) return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
    auto enabled = field_value(lines[index++], "enabled=");
    if (!enabled.ok() || (enabled.value() != "0" && enabled.value() != "1")) {
        return Status{ErrorCode::protocol_error,
                      "terminal profile enabled field is invalid"};
    }
    profile.enabled = enabled.value() == "1";

    while (index < lines.size() && lines[index].starts_with("argument-hex=")) {
        auto encoded = field_value(lines[index++], "argument-hex=");
        if (!encoded.ok()) return encoded.status();
        auto argument = hex_decode_string(
            encoded.value(), kMaximumArgumentBytes, "terminal argument");
        if (!argument.ok()) return argument.status();
        profile.arguments.push_back(std::move(argument.value()));
        if (profile.arguments.size() > kMaximumArguments) {
            return Status{ErrorCode::resource_exhausted,
                          "terminal profile has too many arguments"};
        }
    }
    if (record_version == ProfileRecordVersion::v7) {
        const auto parse_digest = [&](
                                      std::string_view key,
                                      std::optional<ExecutableDigest> &target)
            -> Status {
            if (index >= lines.size()) {
                return Status{ErrorCode::protocol_error,
                              "terminal profile is truncated"};
            }
            auto text = field_value(lines[index++], key);
            if (!text.ok()) return text.status();
            if (text.value() == "none") {
                target.reset();
                return Status::success();
            }
            auto decoded = hex_decode_string(
                text.value(), ExecutableDigest{}.size(), key);
            if (!decoded.ok() ||
                decoded.value().size() != ExecutableDigest{}.size()) {
                return Status{
                    ErrorCode::protocol_error,
                    std::string(key) + " must be exactly 32 lowercase-hex bytes"};
            }
            ExecutableDigest digest{};
            for (std::size_t byte = 0U; byte < digest.size(); ++byte) {
                digest[byte] = static_cast<std::uint8_t>(
                    static_cast<unsigned char>(decoded.value()[byte]));
            }
            target = digest;
            return Status::success();
        };
        Status parsed_digest = parse_digest(
            "executable-sha256=", profile.executable_sha256);
        if (!parsed_digest.ok()) return parsed_digest;
        parsed_digest = parse_digest(
            "toolbox-sha256=", profile.toolbox_sha256);
        if (!parsed_digest.ok()) return parsed_digest;
    }
    if (index >= lines.size()) return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
    auto cwd_encoded = field_value(lines[index++], "working-directory-hex=");
    if (!cwd_encoded.ok()) return cwd_encoded.status();
    auto cwd = hex_decode_string(cwd_encoded.value(), kMaximumPathBytes, "terminal working directory");
    if (!cwd.ok()) return cwd.status();
    profile.working_directory = std::move(cwd.value());

    if (index >= lines.size()) return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
    auto terminal_type = field_value(lines[index++], "terminal-type=");
    if (!terminal_type.ok()) return terminal_type.status();
    profile.terminal_type = std::string(terminal_type.value());

    while (index < lines.size() && lines[index].starts_with("inherit-environment=")) {
        auto name = field_value(lines[index++], "inherit-environment=");
        if (!name.ok()) return name.status();
        profile.inherited_environment.emplace_back(name.value());
    }
    while (index < lines.size() && lines[index].starts_with("environment-hex=")) {
        auto encoded = field_value(lines[index++], "environment-hex=");
        if (!encoded.ok()) return encoded.status();
        const std::size_t separator = encoded.value().find(':');
        if (separator == std::string_view::npos || separator == 0U ||
            encoded.value().find(':', separator + 1U) != std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "terminal environment record is invalid"};
        }
        auto value = hex_decode_string(
            encoded.value().substr(separator + 1U),
            kMaximumEnvironmentValueBytes, "terminal environment value");
        if (!value.ok()) return value.status();
        profile.environment.push_back(EnvironmentEntry{
            std::string(encoded.value().substr(0U, separator)),
            std::move(value.value())});
    }

    if (index >= lines.size()) return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
    auto identity = field_value(lines[index++], "identity=");
    if (!identity.ok()) return identity.status();
    if (identity.value() == "inherit") {
        profile.identity = IdentityPolicy{};
    } else if (identity.value().starts_with("exact:")) {
        auto fields = split_three(identity.value().substr(6U), ':', "terminal exact identity");
        if (!fields.ok()) return fields.status();
        auto uid = parse_u32(fields.value()[0U], "terminal uid");
        if (!uid.ok()) return uid.status();
        auto gid = parse_u32(fields.value()[1U], "terminal gid");
        if (!gid.ok()) return gid.status();
        if (fields.value()[2U] != "0" && fields.value()[2U] != "1") {
            return Status{ErrorCode::protocol_error,
                          "terminal supplementary-group policy is invalid"};
        }
        profile.identity = IdentityPolicy{
            IdentityMode::exact,
            uid.value(),
            gid.value(),
            fields.value()[2U] == "1",
            {}};
    } else if ((record_version == ProfileRecordVersion::v6 ||
                record_version == ProfileRecordVersion::v7) &&
               identity.value().starts_with("account:")) {
        const std::string_view fields = identity.value().substr(8U);
        const std::size_t separator = fields.find(':');
        if (separator == std::string_view::npos || separator == 0U ||
            fields.find(':', separator + 1U) != std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "terminal account identity is invalid"};
        }
        auto uid = parse_u32(fields.substr(0U, separator), "terminal uid");
        if (!uid.ok()) return uid.status();
        auto gid = parse_u32(fields.substr(separator + 1U), "terminal gid");
        if (!gid.ok()) return gid.status();
        profile.identity.mode = IdentityMode::account;
        profile.identity.uid = uid.value();
        profile.identity.gid = gid.value();
        profile.identity.clear_supplementary_groups = false;
        while (index < lines.size() &&
               lines[index].starts_with("supplementary-group=")) {
            auto group = field_value(lines[index++], "supplementary-group=");
            if (!group.ok()) return group.status();
            auto value = parse_u32(group.value(), "terminal supplementary group");
            if (!value.ok()) return value.status();
            profile.identity.supplementary_groups.push_back(value.value());
            if (profile.identity.supplementary_groups.size() >
                kMaximumSupplementaryGroups) {
                return Status{
                    ErrorCode::resource_exhausted,
                    "terminal account identity has too many supplementary groups"};
            }
        }
    } else {
        return Status{ErrorCode::protocol_error,
                      "terminal identity field is invalid"};
    }

    if (record_version != ProfileRecordVersion::v1) {
        if (index >= lines.size()) {
            return Status{ErrorCode::protocol_error,
                          "terminal profile is truncated"};
        }
        auto confinement = field_value(lines[index++], "confinement=");
        if (!confinement.ok()) return confinement.status();
        if (confinement.value() == "compatibility") {
            profile.confinement = ConfinementMode::compatibility;
        } else if (confinement.value() == "baseline") {
            profile.confinement = ConfinementMode::baseline;
        } else if (confinement.value() == "strict") {
            profile.confinement = ConfinementMode::strict;
        } else {
            return Status{ErrorCode::protocol_error,
                          "terminal confinement field is invalid"};
        }
    }

    if (record_version == ProfileRecordVersion::v6 ||
        record_version == ProfileRecordVersion::v7) {
        if (index >= lines.size()) {
            return Status{ErrorCode::protocol_error,
                          "terminal profile is truncated"};
        }
        auto privilege = field_value(
            lines[index++], "allow-privilege-escalation=");
        if (!privilege.ok() ||
            (privilege.value() != "0" && privilege.value() != "1")) {
            return Status{
                ErrorCode::protocol_error,
                "terminal privilege-escalation field is invalid"};
        }
        profile.allow_privilege_escalation = privilege.value() == "1";
    }

    const auto require_line = [&](std::string_view key) -> Result<std::string_view> {
        if (index >= lines.size()) {
            return Status{ErrorCode::protocol_error, "terminal profile is truncated"};
        }
        return field_value(lines[index++], key);
    };
    if (record_version == ProfileRecordVersion::v3 ||
        record_version == ProfileRecordVersion::v4 ||
        record_version == ProfileRecordVersion::v5 ||
        record_version == ProfileRecordVersion::v6 ||
        record_version == ProfileRecordVersion::v7) {
        const auto parse_optional = [&](
                                        std::string_view key,
                                        std::optional<std::uint64_t> &destination)
            -> Status {
            auto text = require_line(key);
            if (!text.ok()) return text.status();
            if (text.value() == "none") {
                destination.reset();
                return Status::success();
            }
            auto value = parse_u64(text.value(), key);
            if (!value.ok()) return value.status();
            destination = value.value();
            return Status::success();
        };
        Status parsed_cgroup = parse_optional(
            "cgroup-pids-max=",
            profile.cgroup_limits.maximum_processes);
        if (!parsed_cgroup.ok()) return parsed_cgroup;
        if (record_version == ProfileRecordVersion::v4 ||
            record_version == ProfileRecordVersion::v5 ||
            record_version == ProfileRecordVersion::v6 ||
            record_version == ProfileRecordVersion::v7) {
            parsed_cgroup = parse_optional(
                "cgroup-memory-high-bytes=",
                profile.cgroup_limits.maximum_memory_high_bytes);
            if (!parsed_cgroup.ok()) return parsed_cgroup;
        }
        parsed_cgroup = parse_optional(
            "cgroup-memory-max-bytes=",
            profile.cgroup_limits.maximum_memory_bytes);
        if (!parsed_cgroup.ok()) return parsed_cgroup;
        parsed_cgroup = parse_optional(
            "cgroup-swap-max-bytes=",
            profile.cgroup_limits.maximum_swap_bytes);
        if (!parsed_cgroup.ok()) return parsed_cgroup;
        parsed_cgroup = parse_optional(
            "cgroup-cpu-quota-us=",
            profile.cgroup_limits.cpu_quota_microseconds);
        if (!parsed_cgroup.ok()) return parsed_cgroup;
        parsed_cgroup = parse_optional(
            "cgroup-cpu-period-us=",
            profile.cgroup_limits.cpu_period_microseconds);
        if (!parsed_cgroup.ok()) return parsed_cgroup;
        if (record_version == ProfileRecordVersion::v5 ||
            record_version == ProfileRecordVersion::v6 ||
            record_version == ProfileRecordVersion::v7) {
            auto device_text = require_line("cgroup-io-device=");
            if (!device_text.ok()) return device_text.status();
            if (device_text.value() == "none") {
                profile.cgroup_limits.io_device.reset();
            } else {
                auto device = parse_cgroup_io_device(
                    device_text.value(), "cgroup-io-device");
                if (!device.ok()) return device.status();
                profile.cgroup_limits.io_device = device.value();
            }
            parsed_cgroup = parse_optional(
                "cgroup-io-rbps=",
                profile.cgroup_limits.maximum_io_read_bytes_per_second);
            if (!parsed_cgroup.ok()) return parsed_cgroup;
            parsed_cgroup = parse_optional(
                "cgroup-io-wbps=",
                profile.cgroup_limits.maximum_io_write_bytes_per_second);
            if (!parsed_cgroup.ok()) return parsed_cgroup;
            parsed_cgroup = parse_optional(
                "cgroup-io-riops=",
                profile.cgroup_limits.maximum_io_read_operations_per_second);
            if (!parsed_cgroup.ok()) return parsed_cgroup;
            parsed_cgroup = parse_optional(
                "cgroup-io-wiops=",
                profile.cgroup_limits.maximum_io_write_operations_per_second);
            if (!parsed_cgroup.ok()) return parsed_cgroup;
        }
    }
    auto minimum_text = require_line("minimum-dimensions=");
    if (!minimum_text.ok()) return minimum_text.status();
    auto minimum = parse_dimension_pair(minimum_text.value(), "minimum dimensions");
    if (!minimum.ok()) return minimum.status();
    profile.dimensions.minimum = minimum.value();
    auto initial_text = require_line("initial-dimensions=");
    if (!initial_text.ok()) return initial_text.status();
    auto initial = parse_dimension_pair(initial_text.value(), "initial dimensions");
    if (!initial.ok()) return initial.status();
    profile.dimensions.initial = initial.value();
    auto maximum_text = require_line("maximum-dimensions=");
    if (!maximum_text.ok()) return maximum_text.status();
    auto maximum = parse_dimension_pair(maximum_text.value(), "maximum dimensions");
    if (!maximum.ok()) return maximum.status();
    profile.dimensions.maximum = maximum.value();
    auto resize = require_line("allow-resize=");
    if (!resize.ok() || (resize.value() != "0" && resize.value() != "1")) {
        return Status{ErrorCode::protocol_error,
                      "terminal resize policy is invalid"};
    }
    profile.dimensions.allow_resize = resize.value() == "1";

    const auto parse_limit = [&](std::string_view key, std::uint64_t &destination) -> Status {
        auto text = require_line(key);
        if (!text.ok()) return text.status();
        auto parsed = parse_u64(text.value(), key);
        if (!parsed.ok()) return parsed.status();
        destination = parsed.value();
        return Status::success();
    };
    Status parsed = parse_limit("limit-cpu-seconds=", profile.limits.cpu_seconds);
    if (!parsed.ok()) return parsed;
    parsed = parse_limit("limit-address-space-bytes=", profile.limits.address_space_bytes);
    if (!parsed.ok()) return parsed;
    parsed = parse_limit("limit-file-size-bytes=", profile.limits.file_size_bytes);
    if (!parsed.ok()) return parsed;
    parsed = parse_limit("limit-open-files=", profile.limits.open_files);
    if (!parsed.ok()) return parsed;
    parsed = parse_limit("limit-processes=", profile.limits.processes);
    if (!parsed.ok()) return parsed;

    std::uint64_t grace = 0U;
    parsed = parse_limit("hangup-grace-ms=", grace);
    if (!parsed.ok() || grace > static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
        return parsed.ok() ? Status{ErrorCode::protocol_error, "terminal hangup grace overflows"} : parsed;
    }
    profile.hangup_grace = std::chrono::milliseconds(static_cast<std::int64_t>(grace));
    parsed = parse_limit("terminate-grace-ms=", grace);
    if (!parsed.ok() || grace > static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
        return parsed.ok() ? Status{ErrorCode::protocol_error, "terminal terminate grace overflows"} : parsed;
    }
    profile.terminate_grace = std::chrono::milliseconds(static_cast<std::int64_t>(grace));
    parsed = parse_limit("kill-reap-grace-ms=", grace);
    if (!parsed.ok() || grace > static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
        return parsed.ok() ? Status{ErrorCode::protocol_error, "terminal kill grace overflows"} : parsed;
    }
    profile.kill_reap_grace = std::chrono::milliseconds(static_cast<std::int64_t>(grace));
    if (index != lines.size()) {
        return Status{ErrorCode::protocol_error,
                      "terminal profile has trailing or unknown fields"};
    }
    const Status valid = validate_profile(profile);
    if (!valid.ok()) return valid;
    auto canonical = encode_profile_record_version(profile, record_version);
    if (!canonical.ok() || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "terminal profile record is not canonical"};
    }
    return profile;
}

Result<std::vector<std::uint8_t>> encode_binding_record(const Binding &binding) {
    const Status valid = validate_binding(binding);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << kBindingHeader << '\n'
           << "principal=" << principal_hex(binding.principal_id) << '\n'
           << "profile=" << binding.profile_id << '\n'
           << "enabled=" << (binding.enabled ? 1 : 0) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<Binding> decode_binding_record(std::span<const std::uint8_t> bytes) {
    auto split = split_record(bytes, 1024U, "terminal binding");
    if (!split.ok()) return split.status();
    const auto &lines = split.value();
    if (lines.size() != 4U || lines[0U] != kBindingHeader) {
        return Status{ErrorCode::protocol_error,
                      "terminal binding structure is invalid"};
    }
    auto principal_text = field_value(lines[1U], "principal=");
    if (!principal_text.ok()) return principal_text.status();
    auto principal = parse_principal(principal_text.value());
    if (!principal.ok()) return principal.status();
    auto profile = field_value(lines[2U], "profile=");
    if (!profile.ok()) return profile.status();
    auto enabled = field_value(lines[3U], "enabled=");
    if (!enabled.ok() || (enabled.value() != "0" && enabled.value() != "1")) {
        return Status{ErrorCode::protocol_error,
                      "terminal binding enabled field is invalid"};
    }
    Binding binding{principal.value(), std::string(profile.value()), enabled.value() == "1"};
    const Status valid = validate_binding(binding);
    if (!valid.ok()) return valid;
    auto canonical = encode_binding_record(binding);
    if (!canonical.ok() || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "terminal binding record is not canonical"};
    }
    return binding;
}

Result<ProfileStoreData> load_profile_store(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid) {
    auto opened_root = open_absolute_directory_without_symlinks(root);
    if (!opened_root.ok()) return opened_root.status();
    FileDescriptor root_fd = std::move(opened_root.value());
    Status secure = validate_owner_only_directory(
        root_fd.get(), expected_owner_uid, "terminal policy root");
    if (!secure.ok()) return secure;

    FileDescriptor profiles_fd(::openat(
        root_fd.get(), "profiles",
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (profiles_fd.get() < 0) {
        return error_status(ErrorCode::io_error, "open terminal profile directory");
    }
    secure = validate_owner_only_directory(
        profiles_fd.get(), expected_owner_uid, "terminal profile directory");
    if (!secure.ok()) return secure;
    FileDescriptor bindings_fd(::openat(
        root_fd.get(), "bindings",
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (bindings_fd.get() < 0) {
        return error_status(ErrorCode::io_error, "open terminal binding directory");
    }
    secure = validate_owner_only_directory(
        bindings_fd.get(), expected_owner_uid, "terminal binding directory");
    if (!secure.ok()) return secure;

    auto root_entries = list_directory(root_fd.get(), 2U, "terminal policy root");
    if (!root_entries.ok()) return root_entries.status();
    const std::vector<std::string> expected_root{"bindings", "profiles"};
    if (root_entries.value() != expected_root) {
        return Status{ErrorCode::io_error,
                      "terminal policy root contains an unexpected entry"};
    }

    auto profile_names = list_directory(
        profiles_fd.get(), kMaximumProfiles, "terminal profile directory");
    if (!profile_names.ok()) return profile_names.status();
    auto binding_names = list_directory(
        bindings_fd.get(), kMaximumBindings, "terminal binding directory");
    if (!binding_names.ok()) return binding_names.status();

    ProfileStoreData data;
    data.profiles.reserve(profile_names.value().size());
    data.bindings.reserve(binding_names.value().size());
    constexpr std::string_view profile_suffix = ".profile";
    for (const std::string &name : profile_names.value()) {
        if (!ends_with(name, profile_suffix)) {
            return Status{ErrorCode::io_error,
                          "terminal profile directory contains an unexpected filename"};
        }
        const std::string_view stem(name.data(), name.size() - profile_suffix.size());
        if (!valid_profile_id(stem)) {
            return Status{ErrorCode::io_error,
                          "terminal profile filename has an invalid id"};
        }
        auto bytes = read_record_file(profiles_fd.get(), name, expected_owner_uid);
        if (!bytes.ok()) return bytes.status();
        auto profile = decode_profile_record(bytes.value());
        if (!profile.ok()) return profile.status();
        if (profile.value().id != stem) {
            return Status{ErrorCode::protocol_error,
                          "terminal profile filename and record content id differ"};
        }
        data.profiles.push_back(std::move(profile.value()));
    }

    constexpr std::string_view binding_suffix = ".binding";
    for (const std::string &name : binding_names.value()) {
        if (!ends_with(name, binding_suffix)) {
            return Status{ErrorCode::io_error,
                          "terminal binding directory contains an unexpected filename"};
        }
        const std::string_view stem(name.data(), name.size() - binding_suffix.size());
        if (stem.size() != 64U ||
            std::any_of(stem.begin(), stem.end(), [](char character) {
                return hex_nibble(character) < 0;
            })) {
            return Status{ErrorCode::io_error,
                          "terminal binding filename is not a lowercase principal"};
        }
        auto bytes = read_record_file(bindings_fd.get(), name, expected_owner_uid);
        if (!bytes.ok()) return bytes.status();
        auto binding = decode_binding_record(bytes.value());
        if (!binding.ok()) return binding.status();
        if (principal_hex(binding.value().principal_id) != stem) {
            return Status{ErrorCode::protocol_error,
                          "terminal binding filename and content principal differ"};
        }
        data.bindings.push_back(std::move(binding.value()));
    }
    return data;
}

Result<security::Digest> profile_store_digest(
    ProfileStoreData data, const security::Sodium &sodium) {
    ProfileRegistry validation;
    const Status valid = validation.replace(data);
    if (!valid.ok()) return valid;
    std::sort(data.profiles.begin(), data.profiles.end(),
              [](const Profile &left, const Profile &right) {
                  return left.id < right.id;
              });
    std::sort(data.bindings.begin(), data.bindings.end(),
              [](const Binding &left, const Binding &right) {
                  if (left.principal_id == right.principal_id) {
                      return left.profile_id < right.profile_id;
                  }
                  return principal_less(left.principal_id,
                                        right.principal_id);
              });
    std::vector<std::uint8_t> material;
    constexpr std::string_view header{"iotox-terminal-policy-tree-v1\n"};
    material.insert(material.end(), header.begin(), header.end());
    const auto append_u32 = [&](std::uint32_t value) {
        material.push_back(static_cast<std::uint8_t>(value >> 24U));
        material.push_back(static_cast<std::uint8_t>(value >> 16U));
        material.push_back(static_cast<std::uint8_t>(value >> 8U));
        material.push_back(static_cast<std::uint8_t>(value));
    };
    append_u32(static_cast<std::uint32_t>(data.profiles.size()));
    for (const Profile &profile : data.profiles) {
        auto encoded = encode_profile_record(profile);
        if (!encoded) return encoded.status();
        if (encoded.value().size() >
            static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
            return Status{ErrorCode::resource_exhausted,
                          "terminal profile canonical record is too large to commit"};
        }
        append_u32(static_cast<std::uint32_t>(encoded.value().size()));
        material.insert(material.end(), encoded.value().begin(),
                        encoded.value().end());
    }
    append_u32(static_cast<std::uint32_t>(data.bindings.size()));
    for (const Binding &binding : data.bindings) {
        auto encoded = encode_binding_record(binding);
        if (!encoded) return encoded.status();
        append_u32(static_cast<std::uint32_t>(encoded.value().size()));
        material.insert(material.end(), encoded.value().begin(),
                        encoded.value().end());
    }
    return sodium.hash("iotox-terminal-policy-tree-v1", material);
}

namespace {

[[nodiscard]] Result<FileDescriptor> open_store_child_for_mutation(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    std::string_view child) {
    auto opened_root = open_absolute_directory_without_symlinks(root);
    if (!opened_root) return opened_root.status();
    Status secure = validate_owner_only_directory(
        opened_root.value().get(), expected_owner_uid,
        "terminal policy root");
    if (!secure.ok()) return secure;
    const std::string child_name(child);
    FileDescriptor directory(::openat(
        opened_root.value().get(), child_name.c_str(),
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (directory.get() < 0) {
        return error_status(
            ErrorCode::io_error, "open terminal policy mutation directory");
    }
    secure = validate_owner_only_directory(
        directory.get(), expected_owner_uid,
        "terminal policy mutation directory");
    if (!secure.ok()) return secure;
    return directory;
}

[[nodiscard]] Result<FileDescriptor> lock_store_for_mutation(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid) {
    auto opened = open_absolute_directory_without_symlinks(root);
    if (!opened) return opened.status();
    const Status secure = validate_owner_only_directory(
        opened.value().get(), expected_owner_uid, "terminal policy root");
    if (!secure.ok()) return secure;
    if (::flock(opened.value().get(), LOCK_EX) != 0) {
        return error_status(
            ErrorCode::io_error, "lock terminal policy root for mutation");
    }
    return opened;
}

[[nodiscard]] Status validate_complete_store(ProfileStoreData data) {
    ProfileRegistry registry;
    return registry.replace(std::move(data));
}

[[nodiscard]] Status validate_replace_target(
    int directory, std::string_view name,
    std::uint32_t expected_owner_uid) {
    const std::string owned_name(name);
    struct stat metadata {};
    if (::fstatat(
            directory, owned_name.c_str(), &metadata,
            AT_SYMLINK_NOFOLLOW) != 0) {
        if (errno == ENOENT) return Status::success();
        return error_status(
            ErrorCode::io_error, "inspect terminal policy mutation target");
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
        metadata.st_uid != static_cast<uid_t>(expected_owner_uid) ||
        (metadata.st_mode & static_cast<mode_t>(0077)) != 0 ||
        (metadata.st_mode &
         static_cast<mode_t>(S_ISUID | S_ISGID | S_ISVTX)) != 0) {
        return Status{
            ErrorCode::io_error,
            "terminal policy mutation target is not a single-link owner-only regular file"};
    }
    return Status::success();
}

[[nodiscard]] Status write_store_record_atomic(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    std::string_view child, std::string_view name,
    std::span<const std::uint8_t> bytes) {
    if (bytes.empty() || bytes.size() > kMaximumProfileFileBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal policy mutation record exceeds its byte bound"};
    }
    auto opened = open_store_child_for_mutation(
        root, expected_owner_uid, child);
    if (!opened) return opened.status();
    const Status target = validate_replace_target(
        opened.value().get(), name, expected_owner_uid);
    if (!target.ok()) return target;

    static std::atomic<std::uint64_t> sequence{0U};
    const std::uint64_t ordinal =
        sequence.fetch_add(1U, std::memory_order_relaxed);
    const std::string temporary =
        ".iotox-policy-tmp-" +
        std::to_string(static_cast<unsigned long long>(::getpid())) + "-" +
        std::to_string(static_cast<unsigned long long>(ordinal));
    FileDescriptor descriptor(::openat(
        opened.value().get(), temporary.c_str(),
        O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR));
    if (descriptor.get() < 0) {
        return error_status(
            ErrorCode::io_error,
            "create private terminal policy temporary record");
    }
    Status result = Status::success();
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::write(
            descriptor.get(), bytes.data() + offset, bytes.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        result = error_status(
            ErrorCode::io_error, "write terminal policy temporary record");
        break;
    }
    if (result.ok() && ::fsync(descriptor.get()) != 0) {
        result = error_status(
            ErrorCode::io_error, "sync terminal policy temporary record");
    }
    if (result.ok()) {
        const std::string destination(name);
        if (::renameat(
                opened.value().get(), temporary.c_str(),
                opened.value().get(), destination.c_str()) != 0) {
            result = error_status(
                ErrorCode::io_error,
                "atomically replace terminal policy record");
        }
    }
    if (!result.ok()) {
        static_cast<void>(::unlinkat(
            opened.value().get(), temporary.c_str(), 0));
        return result;
    }
    if (::fsync(opened.value().get()) != 0) {
        return error_status(
            ErrorCode::io_error, "sync terminal policy directory");
    }
    return Status::success();
}

[[nodiscard]] Status remove_store_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    std::string_view child, std::string_view name) {
    auto opened = open_store_child_for_mutation(
        root, expected_owner_uid, child);
    if (!opened) return opened.status();
    const Status target = validate_replace_target(
        opened.value().get(), name, expected_owner_uid);
    if (!target.ok()) return target;
    const std::string owned_name(name);
    if (::unlinkat(opened.value().get(), owned_name.c_str(), 0) != 0) {
        return Status{
            errno == ENOENT ? ErrorCode::not_found : ErrorCode::io_error,
            "unable to remove terminal policy record: " +
                std::string(std::strerror(errno))};
    }
    if (::fsync(opened.value().get()) != 0) {
        return error_status(
            ErrorCode::io_error, "sync terminal policy directory");
    }
    return Status::success();
}

}  // namespace

Status install_profile_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const Profile &profile) {
    auto locked = lock_store_for_mutation(root, expected_owner_uid);
    if (!locked) return locked.status();
    auto loaded = load_profile_store(root, expected_owner_uid);
    if (!loaded) return loaded.status();
    auto existing = std::find_if(
        loaded.value().profiles.begin(), loaded.value().profiles.end(),
        [&](const Profile &candidate) { return candidate.id == profile.id; });
    if (existing == loaded.value().profiles.end()) {
        loaded.value().profiles.push_back(profile);
    } else {
        *existing = profile;
    }
    const Status complete = validate_complete_store(loaded.value());
    if (!complete.ok()) return complete;
    auto encoded = encode_profile_record(profile);
    if (!encoded) return encoded.status();
    return write_store_record_atomic(
        root, expected_owner_uid, "profiles", profile.id + ".profile",
        encoded.value());
}

Status remove_profile_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    std::string_view profile_id) {
    Profile probe;
    probe.id = std::string(profile_id);
    probe.enabled = false;
    probe.arguments = {"/bin/false"};
    probe.working_directory = "/";
    const Status valid = validate_profile(probe);
    if (!valid.ok()) return valid;
    auto locked = lock_store_for_mutation(root, expected_owner_uid);
    if (!locked) return locked.status();
    auto loaded = load_profile_store(root, expected_owner_uid);
    if (!loaded) return loaded.status();
    const auto existing = std::find_if(
        loaded.value().profiles.begin(), loaded.value().profiles.end(),
        [&](const Profile &profile) { return profile.id == profile_id; });
    if (existing == loaded.value().profiles.end()) {
        return Status{ErrorCode::not_found,
                      "terminal profile is not installed"};
    }
    if (std::any_of(
            loaded.value().bindings.begin(), loaded.value().bindings.end(),
            [&](const Binding &binding) {
                return binding.profile_id == profile_id;
            })) {
        return Status{ErrorCode::unavailable,
                      "terminal profile remains referenced by a binding"};
    }
    loaded.value().profiles.erase(existing);
    const Status complete = validate_complete_store(loaded.value());
    if (!complete.ok()) return complete;
    return remove_store_record(
        root, expected_owner_uid, "profiles",
        std::string(profile_id) + ".profile");
}

Status install_binding_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const Binding &binding) {
    auto locked = lock_store_for_mutation(root, expected_owner_uid);
    if (!locked) return locked.status();
    auto loaded = load_profile_store(root, expected_owner_uid);
    if (!loaded) return loaded.status();
    auto existing = std::find_if(
        loaded.value().bindings.begin(), loaded.value().bindings.end(),
        [&](const Binding &candidate) {
            return candidate.principal_id == binding.principal_id;
        });
    if (existing == loaded.value().bindings.end()) {
        loaded.value().bindings.push_back(binding);
    } else {
        *existing = binding;
    }
    const Status complete = validate_complete_store(loaded.value());
    if (!complete.ok()) return complete;
    auto encoded = encode_binding_record(binding);
    if (!encoded) return encoded.status();
    return write_store_record_atomic(
        root, expected_owner_uid, "bindings",
        principal_hex(binding.principal_id) + ".binding", encoded.value());
}

Status remove_binding_record(
    const std::filesystem::path &root, std::uint32_t expected_owner_uid,
    const PrincipalId &principal_id) {
    Binding probe{principal_id, "validation", true};
    const Status valid = validate_binding(probe);
    if (!valid.ok()) return valid;
    auto locked = lock_store_for_mutation(root, expected_owner_uid);
    if (!locked) return locked.status();
    auto loaded = load_profile_store(root, expected_owner_uid);
    if (!loaded) return loaded.status();
    const auto existing = std::find_if(
        loaded.value().bindings.begin(), loaded.value().bindings.end(),
        [&](const Binding &binding) {
            return binding.principal_id == principal_id;
        });
    if (existing == loaded.value().bindings.end()) {
        return Status{ErrorCode::not_found,
                      "terminal principal is not bound"};
    }
    loaded.value().bindings.erase(existing);
    const Status complete = validate_complete_store(loaded.value());
    if (!complete.ok()) return complete;
    return remove_store_record(
        root, expected_owner_uid, "bindings",
        principal_hex(principal_id) + ".binding");
}

Status ProfileRegistry::replace(ProfileStoreData data) {
    if (data.profiles.size() > kMaximumProfiles ||
        data.bindings.size() > kMaximumBindings) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal policy replacement exceeds the v1 entry bounds"};
    }
    for (const Profile &profile : data.profiles) {
        const Status valid = validate_profile(profile);
        if (!valid.ok()) return valid;
    }
    for (const Binding &binding : data.bindings) {
        const Status valid = validate_binding(binding);
        if (!valid.ok()) return valid;
    }
    std::sort(data.profiles.begin(), data.profiles.end(), [](const auto &left, const auto &right) {
        return left.id < right.id;
    });
    if (std::adjacent_find(
            data.profiles.begin(), data.profiles.end(), [](const auto &left, const auto &right) {
                return left.id == right.id;
            }) != data.profiles.end()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal policy contains duplicate profile ids"};
    }
    std::sort(data.bindings.begin(), data.bindings.end(), [](const auto &left, const auto &right) {
        if (left.principal_id == right.principal_id) {
            return left.profile_id < right.profile_id;
        }
        return principal_less(left.principal_id, right.principal_id);
    });
    if (std::adjacent_find(
            data.bindings.begin(), data.bindings.end(), [](const auto &left, const auto &right) {
                return left.principal_id == right.principal_id;
            }) != data.bindings.end()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal policy contains an ambiguous principal binding"};
    }
    for (const Binding &binding : data.bindings) {
        const auto profile = std::lower_bound(
            data.profiles.begin(), data.profiles.end(), binding.profile_id,
            [](const Profile &candidate, std::string_view id) {
                return candidate.id < id;
            });
        if (profile == data.profiles.end() || profile->id != binding.profile_id) {
            return Status{ErrorCode::invalid_argument,
                          "terminal binding names a missing profile"};
        }
    }
    std::unique_lock lock(mutex_);
    if (generation_ == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal policy generation is exhausted"};
    }
    profiles_ = std::move(data.profiles);
    bindings_ = std::move(data.bindings);
    ++generation_;
    return Status::success();
}

Result<ResolvedProfile> ProfileRegistry::resolve(
    const PrincipalId &principal_id, const Dimensions &requested,
    std::span<const EnvironmentEntry> ambient_environment) const {
    Profile frozen_profile;
    std::uint64_t frozen_generation = 0U;
    {
        std::shared_lock lock(mutex_);
        if (generation_ == 0U) {
            return Status{ErrorCode::unavailable,
                          "terminal policy has not been loaded"};
        }
        const auto binding = std::lower_bound(
            bindings_.begin(), bindings_.end(), principal_id,
            [](const Binding &candidate, const PrincipalId &principal) {
                return principal_less(candidate.principal_id, principal);
            });
        if (binding == bindings_.end() || binding->principal_id != principal_id) {
            return Status{ErrorCode::not_found,
                          "no local terminal profile is bound to this principal"};
        }
        if (!binding->enabled) {
            return Status{ErrorCode::unavailable,
                          "the local terminal binding is disabled"};
        }
        const auto profile = std::lower_bound(
            profiles_.begin(), profiles_.end(), binding->profile_id,
            [](const Profile &candidate, std::string_view id) {
                return candidate.id < id;
            });
        if (profile == profiles_.end() || profile->id != binding->profile_id) {
            return Status{ErrorCode::internal_error,
                          "terminal registry lost a validated profile"};
        }
        if (!profile->enabled) {
            return Status{ErrorCode::unavailable,
                          "the local terminal profile is disabled"};
        }
        frozen_profile = *profile;
        frozen_generation = generation_;
    }
    auto dimensions = accept_dimensions(frozen_profile.dimensions, requested);
    if (!dimensions.ok()) return dimensions.status();
    auto environment = resolve_environment(frozen_profile, ambient_environment);
    if (!environment.ok()) return environment.status();
    return ResolvedProfile{
        std::move(frozen_profile),
        std::move(environment.value()),
        dimensions.value(),
        frozen_generation};
}

RegistrySnapshot ProfileRegistry::snapshot() const {
    std::shared_lock lock(mutex_);
    const std::size_t enabled_profiles = static_cast<std::size_t>(std::count_if(
        profiles_.begin(), profiles_.end(), [](const Profile &profile) {
            return profile.enabled;
        }));
    const std::size_t enabled_bindings = static_cast<std::size_t>(std::count_if(
        bindings_.begin(), bindings_.end(), [](const Binding &binding) {
            return binding.enabled;
        }));
    return RegistrySnapshot{
        generation_,
        profiles_.size(),
        enabled_profiles,
        bindings_.size(),
        enabled_bindings};
}

}  // namespace iotox::terminal
