#include "sync_linux_process_resources.hpp"

#if !defined(_WIN32)

#include "anonsync_json_parser.hpp"

#include <array>
#include <charconv>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

#include <sys/resource.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

namespace anonsync {
namespace {

constexpr std::size_t kMaximumProcSnapshotBytes = 64U * 1024U;

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    std::string out(label);
    if (!out.empty()) out.append(" ");
    out.append(child);
    return out;
}

[[nodiscard]] std::string system_error_text(int error) {
    return std::strerror(error);
}

[[nodiscard]] std::uint64_t checked_add(
    std::uint64_t left,
    std::uint64_t right,
    std::string_view label) {
    if (left > std::numeric_limits<std::uint64_t>::max() - right) {
        throw std::overflow_error(std::string(label) + " overflow");
    }
    return left + right;
}

[[nodiscard]] std::string read_proc_single_or_throw(
    const char* path,
    std::string_view label) {
    int descriptor = ::open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " open failed: " + system_error_text(error));
    }
    std::array<char, kMaximumProcSnapshotBytes> bytes{};
    ssize_t observed = -1;
    do {
        observed = ::read(descriptor, bytes.data(), bytes.size());
    } while (observed < 0 && errno == EINTR);
    const int read_error = errno;
    const int close_result = ::close(descriptor);
    const int close_error = errno;
    if (observed < 0) {
        throw std::runtime_error(
            std::string(label) + " read failed: " +
            system_error_text(read_error));
    }
    if (close_result != 0) {
        throw std::runtime_error(
            std::string(label) + " close failed: " +
            system_error_text(close_error));
    }
    if (observed == 0) {
        throw std::runtime_error(std::string(label) + " is empty");
    }
    if (static_cast<std::size_t>(observed) == bytes.size()) {
        throw std::runtime_error(
            std::string(label) + " exceeds the bounded single-read frontier");
    }
    return std::string(bytes.data(), static_cast<std::size_t>(observed));
}

[[nodiscard]] std::uint64_t parse_uint64_exact(
    std::string_view text,
    std::string_view label) {
    if (text.empty()) {
        throw std::invalid_argument(std::string(label) + " is empty");
    }
    if (text.size() > 1U && text.front() == '0') {
        throw std::invalid_argument(
            std::string(label) + " is not canonical unsigned decimal");
    }
    std::uint64_t value = 0U;
    const char* const begin = text.data();
    const char* const end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end) {
        throw std::invalid_argument(
            std::string(label) + " is not an unsigned decimal integer");
    }
    return value;
}

[[nodiscard]] std::uint64_t exact_nonnegative_json_uint64_or_throw(
    const Json& value,
    std::string_view label) {
    if (!value.is_number()) {
        throw std::invalid_argument(
            std::string(label) + " is not a JSON number");
    }
    const long long exact = value.integer();
    if (exact < 0) {
        throw std::invalid_argument(
            std::string(label) + " is negative");
    }
    return static_cast<std::uint64_t>(exact);
}

[[nodiscard]] std::uint64_t nonnegative_long_or_throw(
    long value,
    std::string_view label) {
    if (value < 0) {
        throw std::runtime_error(std::string(label) + " is negative");
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::uint64_t process_start_time_clock_ticks_or_throw(
    std::string_view label) {
    const std::string stat = read_proc_single_or_throw(
        "/proc/self/stat", child_label(label, "stat"));
    const std::size_t first_space = stat.find(' ');
    if (first_space == std::string::npos) {
        throw std::runtime_error(std::string(label) + " stat has no pid field");
    }
    const std::uint64_t reported_pid = parse_uint64_exact(
        std::string_view(stat).substr(0U, first_space),
        child_label(label, "stat pid"));
    const pid_t current_pid = ::getpid();
    if (current_pid <= 0 ||
        reported_pid != static_cast<std::uint64_t>(current_pid)) {
        throw std::runtime_error(
            std::string(label) + " stat pid does not match getpid");
    }
    const std::size_t command_end = stat.rfind(") ");
    if (command_end == std::string::npos || command_end + 2U >= stat.size()) {
        throw std::runtime_error(
            std::string(label) + " stat command field is malformed");
    }
    std::string_view tail(stat);
    tail.remove_prefix(command_end + 2U);
    std::array<std::string_view, 20U> fields{};
    std::size_t field_count = 0U;
    while (!tail.empty() && field_count < fields.size()) {
        while (!tail.empty() && tail.front() == ' ') tail.remove_prefix(1U);
        if (tail.empty()) break;
        const std::size_t space = tail.find(' ');
        fields[field_count++] = space == std::string_view::npos
            ? tail
            : tail.substr(0U, space);
        if (space == std::string_view::npos) {
            tail = {};
        } else {
            tail.remove_prefix(space + 1U);
        }
    }
    // tail field zero is proc stat field 3 (state); field 19 is field 22
    // (starttime), expressed in clock ticks after boot.
    if (field_count < fields.size() || fields[0U].size() != 1U) {
        throw std::runtime_error(
            std::string(label) + " stat does not contain field 22");
    }
    const std::uint64_t ticks = parse_uint64_exact(
        fields[19U], child_label(label, "process start ticks"));
    if (ticks == 0U) {
        throw std::runtime_error(
            std::string(label) + " process start ticks are zero");
    }
    return ticks;
}

[[nodiscard]] bool all_decimal_digits(std::string_view text) noexcept {
    if (text.empty()) return false;
    for (const char byte : text) {
        if (byte < '0' || byte > '9') return false;
    }
    return true;
}

[[nodiscard]] std::uint64_t count_numeric_directory_entries_or_throw(
    const char* path,
    bool exclude_directory_descriptor,
    std::string_view label) {
    DIR* directory = ::opendir(path);
    if (directory == nullptr) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " opendir failed: " +
            system_error_text(error));
    }
    const int scanner_descriptor = ::dirfd(directory);
    if (scanner_descriptor < 0) {
        const int error = errno;
        (void)::closedir(directory);
        throw std::runtime_error(
            std::string(label) + " dirfd failed: " +
            system_error_text(error));
    }
    std::uint64_t count = 0U;
    errno = 0;
    while (dirent* entry = ::readdir(directory)) {
        const std::string_view name(entry->d_name);
        if (!all_decimal_digits(name)) continue;
        if (exclude_directory_descriptor) {
            const std::uint64_t numeric = parse_uint64_exact(
                name, child_label(label, "entry"));
            if (numeric == static_cast<std::uint64_t>(scanner_descriptor)) {
                continue;
            }
        }
        count = checked_add(count, 1U, label);
    }
    const int read_error = errno;
    const int close_result = ::closedir(directory);
    const int close_error = errno;
    if (read_error != 0) {
        throw std::runtime_error(
            std::string(label) + " readdir failed: " +
            system_error_text(read_error));
    }
    if (close_result != 0) {
        throw std::runtime_error(
            std::string(label) + " closedir failed: " +
            system_error_text(close_error));
    }
    return count;
}

[[nodiscard]] std::uint64_t positive_sysconf_or_throw(
    int name,
    std::string_view label) {
    errno = 0;
    const long value = ::sysconf(name);
    if (value <= 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " sysconf failed" +
            (error == 0 ? std::string() : ": " + system_error_text(error)));
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::uint64_t monotonic_milliseconds_or_throw(
    std::string_view label) {
    timespec now{};
    if (::clock_gettime(CLOCK_MONOTONIC, &now) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " clock_gettime failed: " +
            system_error_text(error));
    }
    if (now.tv_sec < 0 || now.tv_nsec < 0 || now.tv_nsec >= 1000000000L) {
        throw std::runtime_error(
            std::string(label) + " returned a noncanonical monotonic time");
    }
    constexpr std::uint64_t kMillisecondsPerSecond = 1000U;
    const std::uint64_t seconds = static_cast<std::uint64_t>(now.tv_sec);
    if (seconds > std::numeric_limits<std::uint64_t>::max() /
                      kMillisecondsPerSecond) {
        throw std::overflow_error(
            std::string(label) + " monotonic time overflow");
    }
    return seconds * kMillisecondsPerSecond +
        static_cast<std::uint64_t>(now.tv_nsec / 1000000L);
}

}  // namespace

std::uint64_t SyncLinuxProcessMemorySnapshot::private_resident_kib() const {
    return checked_add(
        private_clean_kib, private_dirty_kib,
        "Linux private resident memory");
}

std::uint64_t SyncLinuxProcessMemorySnapshot::shared_resident_kib() const {
    return checked_add(
        shared_clean_kib, shared_dirty_kib,
        "Linux shared resident memory");
}

SyncLinuxProcessMemorySnapshot parse_sync_linux_smaps_rollup_or_throw(
    std::string_view bytes,
    std::string_view label) {
    if (bytes.empty() || bytes.size() >= kMaximumProcSnapshotBytes) {
        throw std::invalid_argument(
            std::string(label) + " size is outside the bounded frontier");
    }
    using Member = std::uint64_t SyncLinuxProcessMemorySnapshot::*;
    struct Binding final {
        std::string_view name;
        Member member;
        bool seen = false;
    };
    std::array<Binding, 18U> bindings{{
        {"Rss", &SyncLinuxProcessMemorySnapshot::rss_kib, false},
        {"Pss", &SyncLinuxProcessMemorySnapshot::pss_kib, false},
        {"Pss_Dirty", &SyncLinuxProcessMemorySnapshot::pss_dirty_kib, false},
        {"Pss_Anon", &SyncLinuxProcessMemorySnapshot::pss_anon_kib, false},
        {"Pss_File", &SyncLinuxProcessMemorySnapshot::pss_file_kib, false},
        {"Pss_Shmem", &SyncLinuxProcessMemorySnapshot::pss_shmem_kib, false},
        {"Shared_Clean", &SyncLinuxProcessMemorySnapshot::shared_clean_kib, false},
        {"Shared_Dirty", &SyncLinuxProcessMemorySnapshot::shared_dirty_kib, false},
        {"Private_Clean", &SyncLinuxProcessMemorySnapshot::private_clean_kib, false},
        {"Private_Dirty", &SyncLinuxProcessMemorySnapshot::private_dirty_kib, false},
        {"Referenced", &SyncLinuxProcessMemorySnapshot::referenced_kib, false},
        {"Anonymous", &SyncLinuxProcessMemorySnapshot::anonymous_kib, false},
        {"AnonHugePages", &SyncLinuxProcessMemorySnapshot::anonymous_huge_pages_kib, false},
        {"Shared_Hugetlb", &SyncLinuxProcessMemorySnapshot::shared_hugetlb_kib, false},
        {"Private_Hugetlb", &SyncLinuxProcessMemorySnapshot::private_hugetlb_kib, false},
        {"Swap", &SyncLinuxProcessMemorySnapshot::swap_kib, false},
        {"SwapPss", &SyncLinuxProcessMemorySnapshot::swap_pss_kib, false},
        {"Locked", &SyncLinuxProcessMemorySnapshot::locked_kib, false},
    }};

    SyncLinuxProcessMemorySnapshot snapshot;
    while (!bytes.empty()) {
        const std::size_t newline = bytes.find('\n');
        const std::string_view line = newline == std::string_view::npos
            ? bytes
            : bytes.substr(0U, newline);
        if (newline == std::string_view::npos) {
            bytes = {};
        } else {
            bytes.remove_prefix(newline + 1U);
        }
        const std::size_t colon = line.find(':');
        if (colon == std::string_view::npos) continue;
        const std::string_view key = line.substr(0U, colon);
        Binding* selected = nullptr;
        for (Binding& binding : bindings) {
            if (binding.name == key) {
                selected = &binding;
                break;
            }
        }
        if (selected == nullptr) continue;
        if (selected->seen) {
            throw std::invalid_argument(
                std::string(label) + " repeats field " + std::string(key));
        }
        std::string_view value = line.substr(colon + 1U);
        while (!value.empty() && value.front() == ' ') value.remove_prefix(1U);
        constexpr std::string_view suffix = " kB";
        if (!value.ends_with(suffix)) {
            throw std::invalid_argument(
                std::string(label) + " field " + std::string(key) +
                " does not use canonical kB units");
        }
        value.remove_suffix(suffix.size());
        snapshot.*(selected->member) = parse_uint64_exact(
            value, std::string(label) + " field " + std::string(key));
        selected->seen = true;
    }
    for (const Binding& binding : bindings) {
        if (!binding.seen) {
            throw std::invalid_argument(
                std::string(label) + " omits field " +
                std::string(binding.name));
        }
    }
    (void)snapshot.private_resident_kib();
    (void)snapshot.shared_resident_kib();
    return snapshot;
}

SyncLinuxProcessResourceSnapshot
observe_sync_linux_process_resources_or_throw(std::string_view label) {
#if !defined(__linux__)
    throw std::runtime_error(
        std::string(label) + " requires Linux procfs");
#else
    SyncLinuxProcessResourceSnapshot snapshot;
    const pid_t pid = ::getpid();
    if (pid <= 0) {
        throw std::runtime_error(std::string(label) + " getpid failed");
    }
    snapshot.server_pid = static_cast<std::uint64_t>(pid);
    snapshot.process_start_time_clock_ticks =
        process_start_time_clock_ticks_or_throw(label);
    snapshot.clock_ticks_per_second = positive_sysconf_or_throw(
        _SC_CLK_TCK, child_label(label, "clock ticks"));
    snapshot.page_size_bytes = positive_sysconf_or_throw(
        _SC_PAGESIZE, child_label(label, "page size"));
    snapshot.sample_monotonic_milliseconds =
        monotonic_milliseconds_or_throw(label);
    const std::string smaps = read_proc_single_or_throw(
        "/proc/self/smaps_rollup", child_label(label, "smaps_rollup"));
    snapshot.memory = parse_sync_linux_smaps_rollup_or_throw(
        smaps, child_label(label, "smaps_rollup"));

    rusage usage{};
    if (::getrusage(RUSAGE_SELF, &usage) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " getrusage failed: " +
            system_error_text(error));
    }
    snapshot.peak_rss_kib = nonnegative_long_or_throw(
        usage.ru_maxrss, child_label(label, "peak RSS"));
    snapshot.minor_page_faults = nonnegative_long_or_throw(
        usage.ru_minflt, child_label(label, "minor page faults"));
    snapshot.major_page_faults = nonnegative_long_or_throw(
        usage.ru_majflt, child_label(label, "major page faults"));
    snapshot.filesystem_input_operations = nonnegative_long_or_throw(
        usage.ru_inblock, child_label(label, "filesystem input operations"));
    snapshot.filesystem_output_operations = nonnegative_long_or_throw(
        usage.ru_oublock, child_label(label, "filesystem output operations"));
    snapshot.voluntary_context_switches = nonnegative_long_or_throw(
        usage.ru_nvcsw, child_label(label, "voluntary context switches"));
    snapshot.involuntary_context_switches = nonnegative_long_or_throw(
        usage.ru_nivcsw, child_label(label, "involuntary context switches"));
    snapshot.open_file_descriptors = count_numeric_directory_entries_or_throw(
        "/proc/self/fd", true, child_label(label, "file descriptors"));
    snapshot.threads = count_numeric_directory_entries_or_throw(
        "/proc/self/task", false, child_label(label, "threads"));
    if (snapshot.threads == 0U) {
        throw std::runtime_error(std::string(label) + " observed zero threads");
    }
    return snapshot;
#endif
}

std::string render_sync_linux_process_resources_response_json(
    const SyncLinuxProcessResourceSnapshot& snapshot) {
    if (snapshot.server_pid == 0U ||
        snapshot.process_start_time_clock_ticks == 0U ||
        snapshot.clock_ticks_per_second == 0U ||
        snapshot.page_size_bytes == 0U ||
        snapshot.sample_monotonic_milliseconds == 0U ||
        snapshot.threads == 0U) {
        throw std::invalid_argument(
            "Linux process resource snapshot is incomplete");
    }
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output
        << "{\"schema\":\"" << kSyncLinuxProcessResourcesResponseSchema
        << "\",\"command\":\"resources\","
           "\"terminal_class\":\"completed\","
           "\"server_pid\":" << snapshot.server_pid
        << ",\"process_start_time_clock_ticks\":"
        << snapshot.process_start_time_clock_ticks
        << ",\"clock_ticks_per_second\":"
        << snapshot.clock_ticks_per_second
        << ",\"page_size_bytes\":" << snapshot.page_size_bytes
        << ",\"sample_monotonic_milliseconds\":"
        << snapshot.sample_monotonic_milliseconds
        << ",\"memory\":{"
           "\"rss_kib\":" << snapshot.memory.rss_kib
        << ",\"pss_kib\":" << snapshot.memory.pss_kib
        << ",\"pss_dirty_kib\":" << snapshot.memory.pss_dirty_kib
        << ",\"pss_anon_kib\":" << snapshot.memory.pss_anon_kib
        << ",\"pss_file_kib\":" << snapshot.memory.pss_file_kib
        << ",\"pss_shmem_kib\":" << snapshot.memory.pss_shmem_kib
        << ",\"shared_clean_kib\":" << snapshot.memory.shared_clean_kib
        << ",\"shared_dirty_kib\":" << snapshot.memory.shared_dirty_kib
        << ",\"private_clean_kib\":" << snapshot.memory.private_clean_kib
        << ",\"private_dirty_kib\":" << snapshot.memory.private_dirty_kib
        << ",\"private_resident_kib\":"
        << snapshot.memory.private_resident_kib()
        << ",\"shared_resident_kib\":"
        << snapshot.memory.shared_resident_kib()
        << ",\"referenced_kib\":" << snapshot.memory.referenced_kib
        << ",\"anonymous_kib\":" << snapshot.memory.anonymous_kib
        << ",\"anonymous_huge_pages_kib\":"
        << snapshot.memory.anonymous_huge_pages_kib
        << ",\"shared_hugetlb_kib\":"
        << snapshot.memory.shared_hugetlb_kib
        << ",\"private_hugetlb_kib\":"
        << snapshot.memory.private_hugetlb_kib
        << ",\"swap_kib\":" << snapshot.memory.swap_kib
        << ",\"swap_pss_kib\":" << snapshot.memory.swap_pss_kib
        << ",\"locked_kib\":" << snapshot.memory.locked_kib
        << "},\"usage\":{\"peak_rss_kib\":" << snapshot.peak_rss_kib
        << ",\"minor_page_faults\":" << snapshot.minor_page_faults
        << ",\"major_page_faults\":" << snapshot.major_page_faults
        << ",\"filesystem_input_operations\":"
        << snapshot.filesystem_input_operations
        << ",\"filesystem_output_operations\":"
        << snapshot.filesystem_output_operations
        << ",\"voluntary_context_switches\":"
        << snapshot.voluntary_context_switches
        << ",\"involuntary_context_switches\":"
        << snapshot.involuntary_context_switches
        << "},\"open_file_descriptors\":"
        << snapshot.open_file_descriptors
        << ",\"threads\":" << snapshot.threads << '}';
    return output.str();
}

SyncLinuxProcessResourceSnapshot
parse_sync_linux_process_resources_response_json_or_throw(
    std::string_view response_json,
    std::uint64_t expected_server_pid,
    std::string_view label) {
    Json root;
    try {
        root = parse_json_text(std::string(response_json));
    } catch (const std::runtime_error& error) {
        throw std::invalid_argument(
            std::string(label) + " is not valid JSON: " + error.what());
    }
    if (!root.is_object() || root.o.size() != 12U ||
        root.at("schema").str() != kSyncLinuxProcessResourcesResponseSchema ||
        root.at("command").str() != "resources" ||
        root.at("terminal_class").str() != "completed") {
        throw std::invalid_argument(
            std::string(label) + " has an invalid top-level shape");
    }
    SyncLinuxProcessResourceSnapshot snapshot;
    snapshot.server_pid = exact_nonnegative_json_uint64_or_throw(
        root.at("server_pid"), child_label(label, "server_pid"));
    if (snapshot.server_pid == 0U ||
        (expected_server_pid != 0U &&
         snapshot.server_pid != expected_server_pid)) {
        throw std::invalid_argument(
            std::string(label) + " server pid does not match the peer");
    }
    snapshot.process_start_time_clock_ticks =
        exact_nonnegative_json_uint64_or_throw(
            root.at("process_start_time_clock_ticks"),
            child_label(label, "process start ticks"));
    snapshot.clock_ticks_per_second = exact_nonnegative_json_uint64_or_throw(
        root.at("clock_ticks_per_second"),
        child_label(label, "clock ticks per second"));
    snapshot.page_size_bytes = exact_nonnegative_json_uint64_or_throw(
        root.at("page_size_bytes"), child_label(label, "page size"));
    snapshot.sample_monotonic_milliseconds =
        exact_nonnegative_json_uint64_or_throw(
            root.at("sample_monotonic_milliseconds"),
            child_label(label, "sample time"));
    const Json& memory = root.at("memory");
    if (!memory.is_object() || memory.o.size() != 20U) {
        throw std::invalid_argument(
            std::string(label) + " memory object has an invalid shape");
    }
    const auto memory_value = [&](const char* key) {
        return exact_nonnegative_json_uint64_or_throw(
            memory.at(key), child_label(label, key));
    };
    snapshot.memory.rss_kib = memory_value("rss_kib");
    snapshot.memory.pss_kib = memory_value("pss_kib");
    snapshot.memory.pss_dirty_kib = memory_value("pss_dirty_kib");
    snapshot.memory.pss_anon_kib = memory_value("pss_anon_kib");
    snapshot.memory.pss_file_kib = memory_value("pss_file_kib");
    snapshot.memory.pss_shmem_kib = memory_value("pss_shmem_kib");
    snapshot.memory.shared_clean_kib = memory_value("shared_clean_kib");
    snapshot.memory.shared_dirty_kib = memory_value("shared_dirty_kib");
    snapshot.memory.private_clean_kib = memory_value("private_clean_kib");
    snapshot.memory.private_dirty_kib = memory_value("private_dirty_kib");
    snapshot.memory.referenced_kib = memory_value("referenced_kib");
    snapshot.memory.anonymous_kib = memory_value("anonymous_kib");
    snapshot.memory.anonymous_huge_pages_kib =
        memory_value("anonymous_huge_pages_kib");
    snapshot.memory.shared_hugetlb_kib = memory_value("shared_hugetlb_kib");
    snapshot.memory.private_hugetlb_kib = memory_value("private_hugetlb_kib");
    snapshot.memory.swap_kib = memory_value("swap_kib");
    snapshot.memory.swap_pss_kib = memory_value("swap_pss_kib");
    snapshot.memory.locked_kib = memory_value("locked_kib");
    if (memory_value("private_resident_kib") !=
            snapshot.memory.private_resident_kib() ||
        memory_value("shared_resident_kib") !=
            snapshot.memory.shared_resident_kib()) {
        throw std::invalid_argument(
            std::string(label) + " computed resident fields disagree");
    }
    const Json& usage = root.at("usage");
    if (!usage.is_object() || usage.o.size() != 7U) {
        throw std::invalid_argument(
            std::string(label) + " usage object has an invalid shape");
    }
    const auto usage_value = [&](const char* key) {
        return exact_nonnegative_json_uint64_or_throw(
            usage.at(key), child_label(label, key));
    };
    snapshot.peak_rss_kib = usage_value("peak_rss_kib");
    snapshot.minor_page_faults = usage_value("minor_page_faults");
    snapshot.major_page_faults = usage_value("major_page_faults");
    snapshot.filesystem_input_operations =
        usage_value("filesystem_input_operations");
    snapshot.filesystem_output_operations =
        usage_value("filesystem_output_operations");
    snapshot.voluntary_context_switches =
        usage_value("voluntary_context_switches");
    snapshot.involuntary_context_switches =
        usage_value("involuntary_context_switches");
    snapshot.open_file_descriptors = exact_nonnegative_json_uint64_or_throw(
        root.at("open_file_descriptors"),
        child_label(label, "open file descriptors"));
    snapshot.threads = exact_nonnegative_json_uint64_or_throw(
        root.at("threads"), child_label(label, "threads"));
    if (snapshot.process_start_time_clock_ticks == 0U ||
        snapshot.clock_ticks_per_second == 0U ||
        snapshot.page_size_bytes == 0U ||
        snapshot.sample_monotonic_milliseconds == 0U ||
        snapshot.threads == 0U) {
        throw std::invalid_argument(
            std::string(label) + " contains an incomplete snapshot");
    }
    return snapshot;
}

}  // namespace anonsync

#endif
