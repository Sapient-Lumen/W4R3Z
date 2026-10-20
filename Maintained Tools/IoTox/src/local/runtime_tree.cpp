#include "iotox/local/runtime_tree.hpp"

#include "iotox/local/control_protocol.hpp"
#include "iotox/version.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <iomanip>
#include <set>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <vector>

namespace iotox::local {
namespace {

Status path_status(std::string operation, const std::filesystem::path &path) {
    return Status{ErrorCode::io_error,
                  std::move(operation) + " '" + path.string() + "': " + std::strerror(errno)};
}

std::string escape_field(std::string_view input) {
    std::string output;
    output.reserve(input.size());
    for (const char raw_value : input) {
        const auto value = static_cast<unsigned char>(raw_value);
        switch (value) {
            case '\\': output += "\\\\"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            case '=': output += "\\="; break;
            default:
                if (value >= 0x20U && value <= 0x7EU) {
                    output.push_back(static_cast<char>(value));
                } else {
                    std::ostringstream encoded;
                    encoded << "\\x" << std::hex << std::uppercase << std::setw(2)
                            << std::setfill('0') << static_cast<unsigned int>(value);
                    output += encoded.str();
                }
                break;
        }
    }
    return output;
}

std::string bytes_hex(std::span<const std::uint8_t> bytes) {
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : bytes) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

bool valid_public_key_hex(std::string_view value) {
    if (value.size() != toxcore::abi::kPublicKeySize * 2U) {
        return false;
    }
    return std::all_of(value.begin(), value.end(), [](char character) {
        return (character >= '0' && character <= '9') ||
               (character >= 'A' && character <= 'F');
    });
}

Status append_all(int descriptor, std::string_view text, const std::filesystem::path &path) {
    std::size_t offset = 0U;
    while (offset < text.size()) {
        const ssize_t count = ::write(descriptor, text.data() + offset, text.size() - offset);
        if (count < 0) {
            if (errno == EINTR) {
                continue;
            }
            return path_status("unable to append runtime journal", path);
        }
        if (count == 0) {
            return Status{ErrorCode::io_error,
                          "unable to append runtime journal '" + path.string() +
                              "': write made no progress"};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Status write_projection_atomic(const std::filesystem::path &path,
                               std::span<const std::uint8_t> bytes) {
    const std::filesystem::path parent = path.parent_path();
    if (parent.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "runtime projection path has no parent: " + path.string()};
    }
    std::string temporary_template =
        (parent / ("." + path.filename().string() + ".XXXXXX")).string();
    std::vector<char> temporary_buffer(
        temporary_template.begin(), temporary_template.end());
    temporary_buffer.push_back('\0');
    int descriptor = ::mkstemp(temporary_buffer.data());
    if (descriptor < 0) {
        return path_status("unable to create runtime projection", path);
    }
    const std::filesystem::path temporary_path(temporary_buffer.data());
    const auto abandon = [&] {
        const int saved_errno = errno;
        static_cast<void>(::close(descriptor));
        static_cast<void>(::unlink(temporary_path.c_str()));
        errno = saved_errno;
    };
    if (::fcntl(descriptor, F_SETFD, FD_CLOEXEC) != 0 ||
        ::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        const Status status = path_status(
            "unable to protect runtime projection", temporary_path);
        abandon();
        return status;
    }
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        ssize_t count = -1;
        do {
            count = ::write(descriptor, bytes.data() + offset,
                            bytes.size() - offset);
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            const Status status = path_status(
                "unable to write runtime projection", temporary_path);
            abandon();
            return status;
        }
        if (count == 0) {
            const Status status{ErrorCode::io_error,
                                "unable to write runtime projection '" +
                                    temporary_path.string() +
                                    "': write made no progress"};
            abandon();
            return status;
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        descriptor = -1;
        const Status status = path_status(
            "unable to close runtime projection", temporary_path);
        static_cast<void>(::unlink(temporary_path.c_str()));
        return status;
    }
    descriptor = -1;
    if (::rename(temporary_path.c_str(), path.c_str()) != 0) {
        const Status status = path_status(
            "unable to publish runtime projection", path);
        static_cast<void>(::unlink(temporary_path.c_str()));
        return status;
    }
    return Status::success();
}

std::filesystem::path home_directory() {
    if (const char *home = std::getenv("HOME"); home != nullptr && home[0] != '\0') {
        return home;
    }
    return ".";
}

Status remove_entry(const std::filesystem::path &path) {
    std::error_code error;
    std::filesystem::remove_all(path, error);
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to remove stale runtime entry '" + path.string() +
                          "': " + error.message()};
    }
    return Status::success();
}

Status clear_directory_children(const std::filesystem::path &path) {
    std::error_code iterator_error;
    for (std::filesystem::directory_iterator iterator(path, iterator_error), end;
         !iterator_error && iterator != end; iterator.increment(iterator_error)) {
        const Status removed = remove_entry(iterator->path());
        if (!removed.ok()) {
            return removed;
        }
    }
    if (iterator_error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate transient runtime projections '" +
                          path.string() + "': " + iterator_error.message()};
    }
    return Status::success();
}

}  // namespace

RuntimeTree::RuntimeTree(Config config) : config_(std::move(config)) {}

Status RuntimeTree::validate_or_create_directory(
    const std::filesystem::path &path, unsigned int mode) const {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        if (errno != ENOENT) {
            return path_status("unable to inspect runtime directory", path);
        }
        if (::mkdir(path.c_str(), static_cast<mode_t>(mode)) != 0) {
            return path_status("unable to create runtime directory", path);
        }
        if (::lstat(path.c_str(), &metadata) != 0) {
            return path_status("unable to verify runtime directory", path);
        }
    }
    if (!S_ISDIR(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "runtime path is not a real directory: " + path.string()};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "runtime directory is owned by another user: " + path.string()};
    }
    if (::chmod(path.c_str(), static_cast<mode_t>(mode)) != 0) {
        return path_status("unable to enforce runtime directory permissions", path);
    }
    return Status::success();
}


Status RuntimeTree::validate_or_create_fifo(
    const std::filesystem::path &path, unsigned int mode) const {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        if (errno != ENOENT) {
            return path_status("unable to inspect runtime FIFO", path);
        }
        if (::mkfifo(path.c_str(), static_cast<mode_t>(mode)) != 0) {
            return path_status("unable to create runtime FIFO", path);
        }
        if (::lstat(path.c_str(), &metadata) != 0) {
            return path_status("unable to verify runtime FIFO", path);
        }
    }
    if (!S_ISFIFO(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "runtime path is not a FIFO: " + path.string()};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "runtime FIFO is owned by another user: " + path.string()};
    }
    if (::chmod(path.c_str(), static_cast<mode_t>(mode)) != 0) {
        return path_status("unable to enforce runtime FIFO permissions", path);
    }
    return Status::success();
}

Status RuntimeTree::validate_or_create_private_file(
    const std::filesystem::path &path) const {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0) {
        if (errno != ENOENT) {
            return path_status("unable to inspect runtime journal", path);
        }
        const int descriptor = ::open(
            path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
            S_IRUSR | S_IWUSR);
        if (descriptor < 0) {
            return path_status("unable to create runtime journal", path);
        }
        Status status = Status::success();
        if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
            status = path_status("unable to protect runtime journal", path);
        }
        if (::close(descriptor) != 0 && status.ok()) {
            status = path_status("unable to close runtime journal", path);
        }
        if (!status.ok()) {
            static_cast<void>(::unlink(path.c_str()));
            return status;
        }
        if (::lstat(path.c_str(), &metadata) != 0) {
            return path_status("unable to verify runtime journal", path);
        }
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "runtime journal is not a regular file: " + path.string()};
    }
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::io_error,
                      "runtime journal is owned by another user: " + path.string()};
    }
    if (::chmod(path.c_str(), S_IRUSR | S_IWUSR) != 0) {
        return path_status("unable to enforce runtime journal permissions", path);
    }
    return Status::success();
}

Status RuntimeTree::prepare() {
    if (config_.root.empty()) {
        return Status{ErrorCode::invalid_argument, "runtime root is empty"};
    }
    if (!config_.root.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "runtime root must be an absolute path: " + config_.root.string()};
    }
    if (config_.event_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime event rotation threshold must be at least 4096 bytes"};
    }
    if (config_.message_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime message rotation threshold must be at least 4096 bytes"};
    }
    if (config_.protocol_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime protocol rotation threshold must be at least 4096 bytes"};
    }
    if (config_.command_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime command rotation threshold must be at least 4096 bytes"};
    }
    if (config_.file_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime file rotation threshold must be at least 4096 bytes"};
    }
    if (config_.friendship_rotation_bytes < 4096U) {
        return Status{ErrorCode::invalid_argument,
                      "runtime friendship rotation threshold must be at least 4096 bytes"};
    }

    const std::filesystem::path parent = config_.root.parent_path();
    if (parent.empty()) {
        return Status{ErrorCode::invalid_argument, "runtime root has no parent"};
    }
    struct stat parent_metadata {};
    if (::lstat(parent.c_str(), &parent_metadata) != 0 || !S_ISDIR(parent_metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "runtime root parent is not an existing directory: " + parent.string()};
    }

    for (const auto &path : {config_.root, config_.root / "self", config_.root / "peers",
                             config_.root / "requests", config_.root / "transfers",
                             config_.root / "authority",
                             config_.root / "authority" / "principals",
                             config_.root / "commands",
                             config_.root / "commands" / "incoming",
                             config_.root / "commands" / "outgoing"}) {
        const Status status = validate_or_create_directory(path, 0700U);
        if (!status.ok()) {
            return status;
        }
    }

    // Peers, incoming requests, and transfers are projections of live toxcore state.
    // They must not survive a crashed process and masquerade as current authority,
    // reachability, or transfer progress.
    for (const auto &path : {config_.root / "peers", config_.root / "requests",
                             config_.root / "transfers", config_.root / "authority",
                             config_.root / "commands"}) {
        const Status cleared = clear_directory_children(path);
        if (!cleared.ok()) {
            return cleared;
        }
    }
    transfer_projection_cache_.clear();
    peer_transfer_projection_cache_.clear();
    const Status authority_principals = validate_or_create_directory(
        config_.root / "authority" / "principals", 0700U);
    if (!authority_principals.ok()) {
        return authority_principals;
    }
    for (const auto &path : {config_.root / "commands" / "incoming",
                             config_.root / "commands" / "outgoing"}) {
        const Status created = validate_or_create_directory(path, 0700U);
        if (!created.ok()) {
            return created;
        }
    }

    const Status friendship_events =
        validate_or_create_private_file(config_.root / "friend-events");
    if (!friendship_events.ok()) {
        return friendship_events;
    }
    const Status ratox_events =
        validate_or_create_private_file(config_.root / "ratox-events");
    if (!ratox_events.ok()) {
        return ratox_events;
    }
    const Status friendship_help = write_text(
        config_.root / "friendship.help",
        "IoTox ratox-successor friendship lifecycle v1\n"
        "outgoing requests are written to the root request FIFO as 76 hex address bytes, one TAB, 1..921 message bytes, then LF\n"
        "incoming requests are projected under requests/<PUBLIC-KEY>/\n"
        "accept and reject are exact-token private FIFOs in each request directory\n"
        "established peers expose an exact-token private remove FIFO\n"
        "friend-events records request arrival and every local lifecycle decision\n"
        "Tox friendship is transport recognition only; it grants no IoTox role or capability\n"
        "accept uses tox_friend_add_norequest; reject only withdraws IoTox's live request record\n"
        "remove uses tox_friend_delete, does not notify the remote peer, and does not revoke the independent authorization ledger\n"
        "friend numbers are transient toxcore handles; filesystem identity is the uppercase public key\n");
    if (!friendship_help.ok()) {
        return friendship_help;
    }
    const Status ratox_help = write_text(
        config_.root / "ratox.help",
        "IoTox Ratox interactive lifecycle projection v1\n"
        "activation=disabled unless the daemon is explicitly configured with a secure local terminal profile store\n"
        "authorization=every inbound record requires a transcript-confirmed online epoch, negotiated feature bit 23, and exact-head interactive.terminal capability\n"
        "ratox-events=content-free lifecycle journal; terminal input, output, argv, environment, cwd, profile IDs, and error strings are never recorded\n"
        "status=aggregate bounded queue, replay, process, attachment, and tombstone counters\n"
        "routing=friend numbers and online epochs are transient handles, never durable identities\n");
    if (!ratox_help.ok()) {
        return ratox_help;
    }

    const Status outgoing_request_fifo =
        validate_or_create_fifo(config_.root / "request", 0600U);
    if (!outgoing_request_fifo.ok()) {
        return outgoing_request_fifo;
    }
    const Status outgoing_request_help = write_text(
        config_.root / "request.help",
        "IoTox ratox-successor outgoing friend request v1\n"
        "record=<76 hexadecimal Tox address bytes><TAB><1..921 message bytes><LF>\n"
        "address=complete 38-byte Tox address: 32-byte public key, 4-byte nospam, 2-byte checksum\n"
        "hex=uppercase or lowercase accepted; projected public keys are uppercase\n"
        "validation=IoTox decodes exact hex; c-toxcore validates address checksum, own key, duplicate state, and nospam\n"
        "separator=one literal horizontal TAB at byte 77\n"
        "message=byte-preserving after TAB; TAB, NUL, CR, and bytes >= 0x80 are data\n"
        "LF=record delimiter and is not part of the Tox request message\n"
        "minimum-record-bytes=78 excluding LF\n"
        "maximum-record-bytes=998 excluding LF\n"
        "producer=write the complete record including LF in one write(2) no larger than PIPE_BUF\n"
        "FIFO write success means only that the kernel accepted bytes\n"
        "friend-events records parse rejection or tox_friend_add disposition\n"
        "tox_friend_add success means local Tox state accepted the request; it does not prove remote receipt or acceptance\n"
        "Tox friendship grants no IoTox role, capability, ownership, or recovery authority\n");
    if (!outgoing_request_help.ok()) {
        return outgoing_request_help;
    }

    for (const auto &path : {
             config_.root / "self" / "name-set",
             config_.root / "self" / "status-message-set",
             config_.root / "self" / "status-set"}) {
        const Status fifo = validate_or_create_fifo(path, 0600U);
        if (!fifo.ok()) {
            return fifo;
        }
    }
    const Status profile_help = write_text(
        config_.root / "self" / "profile.help",
        "IoTox ratox-successor self profile mutation v1\n"
        "name-set=<0..128 bytes><LF>; LF is framing and is not stored\n"
        "status-message-set=<0..1007 bytes><LF>; LF is framing and is not stored\n"
        "status-set=available|away|busy followed by LF\n"
        "producer=write one complete record including LF in one write(2) no larger than PIPE_BUF\n"
        "empty=name and status message may be cleared by writing LF alone\n"
        "projection=name, status-message, and status are provider-confirmed current values\n"
        "persistence=successful provider mutations are committed to Tox savedata before projection\n"
        "security=Tox presentation fields are not IoTox identity, ownership, or authority\n");
    if (!profile_help.ok()) {
        return profile_help;
    }

    const RuntimeSnapshot initial;
    return publish(initial);
}

Status RuntimeTree::write_text(
    const std::filesystem::path &path, const std::string &text) const {
    const std::vector<std::uint8_t> bytes(text.begin(), text.end());
    return write_bytes(path, bytes);
}

Status RuntimeTree::write_bytes(
    const std::filesystem::path &path, std::span<const std::uint8_t> bytes) const {
    return write_projection_atomic(path, bytes);
}

std::string RuntimeTree::render_snapshot(const RuntimeSnapshot &snapshot) {
    std::ostringstream output;
    const auto boolean_value = [](bool value) noexcept { return value ? 1 : 0; };
    output << "project=" << kProjectName << '\n'
           << "version=" << kVersion << '\n'
           << "revision=" << kRevision << '\n'
           << "codename=" << kCodename << '\n'
           << "phase=" << escape_field(snapshot.phase) << '\n'
           << "address=" << escape_field(snapshot.address) << '\n'
           << "network=" << escape_field(snapshot.network) << '\n'
           << "backend=" << escape_field(snapshot.backend) << '\n'
           << "self-connection=" << escape_field(snapshot.self_connection) << '\n'
           << "self-name="
           << escape_field(std::string(snapshot.profile.name.begin(), snapshot.profile.name.end()))
           << '\n'
           << "self-name-bytes=" << snapshot.profile.name.size() << '\n'
           << "self-status-message="
           << escape_field(std::string(
                  snapshot.profile.status_message.begin(),
                  snapshot.profile.status_message.end()))
           << '\n'
           << "self-status-message-bytes=" << snapshot.profile.status_message.size() << '\n'
           << "self-status=" << to_string(snapshot.profile.status) << '\n'
           << "last-event=" << escape_field(snapshot.last_event) << '\n'
           << "event-count=" << snapshot.event_count << '\n'
           << "peer-count=" << snapshot.peer_count << '\n'
           << "protocol-session-count=" << snapshot.protocol_session_count << '\n'
           << "compatible-protocol-session-count="
           << snapshot.compatible_protocol_session_count << '\n'
           << "established-protocol-session-count="
           << snapshot.established_protocol_session_count << '\n'
           << "negotiating-protocol-session-count="
           << snapshot.negotiating_protocol_session_count << '\n'
           << "incompatible-protocol-session-count="
           << snapshot.incompatible_protocol_session_count << '\n'
           << "protocol-error-session-count="
           << snapshot.protocol_error_session_count << '\n'
           << "authority-session-count=" << snapshot.authority_session_count << '\n'
           << "authorized-peer-count=" << snapshot.authorized_peer_count << '\n'
           << "awaiting-authority-proof-count="
           << snapshot.awaiting_authority_proof_count << '\n'
           << "authority-protocol-error-count="
           << snapshot.authority_protocol_error_count << '\n'
           << "ratox-enabled=" << (snapshot.ratox_enabled ? 1 : 0) << '\n'
           << "ratox-configuration-valid="
           << (snapshot.ratox_configuration_valid ? 1 : 0) << '\n'
           << "ratox-latency-mode-active="
           << (snapshot.ratox_latency_mode_active ? 1 : 0) << '\n'
           << "ratox-active-service-interval-ms="
           << snapshot.ratox_active_service_interval_ms << '\n'
           << "ratox-active-transport-iteration-interval-ms="
           << snapshot.ratox_active_transport_iteration_interval_ms << '\n'
           << "ratox-host-incarnation="
           << snapshot.ratox_host_incarnation << '\n'
           << "ratox-incarnation-lease-held="
           << (snapshot.ratox_incarnation_lease_held ? 1 : 0) << '\n'
           << "ratox-cgroup-host-budget-configured="
           << (snapshot.ratox_cgroup_host_budget_configured ? 1 : 0) << '\n'
           << "ratox-cgroup-aggregate-budget-configured="
           << (snapshot.ratox_cgroup_aggregate_budget_configured ? 1 : 0)
           << '\n'
           << "ratox-cgroup-aggregate-pids-configured="
           << (snapshot.ratox_cgroup_aggregate_pids_configured ? 1 : 0)
           << '\n'
           << "ratox-cgroup-aggregate-memory-configured="
           << (snapshot.ratox_cgroup_aggregate_memory_configured ? 1 : 0)
           << '\n'
           << "ratox-cgroup-aggregate-swap-configured="
           << (snapshot.ratox_cgroup_aggregate_swap_configured ? 1 : 0)
           << '\n'
           << "ratox-cgroup-aggregate-cpu-configured="
           << (snapshot.ratox_cgroup_aggregate_cpu_configured ? 1 : 0)
           << '\n'
           << "ratox-cgroup-aggregate-pids-max="
           << snapshot.ratox_cgroup_aggregate_pids_max << '\n'
           << "ratox-cgroup-aggregate-memory-max-bytes="
           << snapshot.ratox_cgroup_aggregate_memory_max_bytes << '\n'
           << "ratox-cgroup-aggregate-swap-max-bytes="
           << snapshot.ratox_cgroup_aggregate_swap_max_bytes << '\n'
           << "ratox-cgroup-aggregate-cpu-quota-max-us="
           << snapshot.ratox_cgroup_aggregate_cpu_quota_max_microseconds
           << '\n'
           << "ratox-cgroup-aggregate-cpu-period-us="
           << snapshot.ratox_cgroup_aggregate_cpu_period_microseconds << '\n'
           << "ratox-cgroup-aggregate-active-reservations="
           << snapshot.ratox_cgroup_aggregate_active_reservations << '\n'
           << "ratox-cgroup-aggregate-peak-active-reservations="
           << snapshot.ratox_cgroup_aggregate_peak_active_reservations << '\n'
           << "ratox-cgroup-aggregate-reserved-processes="
           << snapshot.ratox_cgroup_aggregate_reserved_processes << '\n'
           << "ratox-cgroup-aggregate-reserved-memory-bytes="
           << snapshot.ratox_cgroup_aggregate_reserved_memory_bytes << '\n'
           << "ratox-cgroup-aggregate-reserved-swap-bytes="
           << snapshot.ratox_cgroup_aggregate_reserved_swap_bytes << '\n'
           << "ratox-cgroup-aggregate-reserved-cpu-quota-us="
           << snapshot.ratox_cgroup_aggregate_reserved_cpu_quota_microseconds
           << '\n'
           << "ratox-cgroup-aggregate-peak-reserved-processes="
           << snapshot.ratox_cgroup_aggregate_peak_reserved_processes << '\n'
           << "ratox-cgroup-aggregate-peak-reserved-memory-bytes="
           << snapshot.ratox_cgroup_aggregate_peak_reserved_memory_bytes << '\n'
           << "ratox-cgroup-aggregate-peak-reserved-swap-bytes="
           << snapshot.ratox_cgroup_aggregate_peak_reserved_swap_bytes << '\n'
           << "ratox-cgroup-aggregate-peak-reserved-cpu-quota-us="
           << snapshot
                  .ratox_cgroup_aggregate_peak_reserved_cpu_quota_microseconds
           << '\n'
           << "ratox-cgroup-aggregate-rejected-reservations="
           << snapshot.ratox_cgroup_aggregate_rejected_reservations << '\n'
           << "ratox-cgroup-aggregate-stranded-reservations="
           << snapshot.ratox_cgroup_aggregate_stranded_reservations << '\n'
           << "ratox-cgroup-pressure-admission-configured="
           << boolean_value(
                  snapshot.ratox_cgroup_pressure_admission_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-cpu-some-configured="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_cpu_some_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-memory-full-configured="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_memory_full_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-io-full-configured="
           << boolean_value(
                  snapshot.ratox_cgroup_pressure_admission_io_full_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-cpu-some-avg10-max-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_cpu_some_avg10_max_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-memory-full-avg10-max-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_memory_full_avg10_max_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-io-full-avg10-max-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_io_full_avg10_max_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-hysteresis-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_hysteresis_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-cpu-some-trigger-configured="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_cpu_some_trigger_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-memory-full-trigger-configured="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_memory_full_trigger_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-io-full-trigger-configured="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_io_full_trigger_configured)
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-window-us="
           << snapshot
                  .ratox_cgroup_pressure_admission_trigger_window_microseconds
           << '\n'
           << "ratox-cgroup-pressure-admission-cpu-some-trigger-stall-us="
           << snapshot
                  .ratox_cgroup_pressure_admission_cpu_some_trigger_stall_microseconds
           << '\n'
           << "ratox-cgroup-pressure-admission-memory-full-trigger-stall-us="
           << snapshot
                  .ratox_cgroup_pressure_admission_memory_full_trigger_stall_microseconds
           << '\n'
           << "ratox-cgroup-pressure-admission-io-full-trigger-stall-us="
           << snapshot
                  .ratox_cgroup_pressure_admission_io_full_trigger_stall_microseconds
           << '\n'
           << "ratox-cgroup-pressure-admission-closed="
           << boolean_value(snapshot.ratox_cgroup_pressure_admission_closed)
           << '\n'
           << "ratox-cgroup-pressure-admission-checks="
           << snapshot.ratox_cgroup_pressure_admission_checks << '\n'
           << "ratox-cgroup-pressure-admission-admitted="
           << snapshot.ratox_cgroup_pressure_admission_admitted << '\n'
           << "ratox-cgroup-pressure-admission-rejections="
           << snapshot.ratox_cgroup_pressure_admission_rejections << '\n'
           << "ratox-cgroup-pressure-admission-sampling-failures="
           << snapshot.ratox_cgroup_pressure_admission_sampling_failures
           << '\n'
           << "ratox-cgroup-pressure-admission-closed-transitions="
           << snapshot.ratox_cgroup_pressure_admission_closed_transitions
           << '\n'
           << "ratox-cgroup-pressure-admission-reopened-transitions="
           << snapshot.ratox_cgroup_pressure_admission_reopened_transitions
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-monitor-healthy="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_trigger_monitor_healthy)
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-hold-active="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_trigger_hold_active)
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-hold-remaining-us="
           << snapshot
                  .ratox_cgroup_pressure_admission_trigger_hold_remaining_microseconds
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-monitor-error-code="
           << to_string(
                  snapshot
                      .ratox_cgroup_pressure_admission_trigger_monitor_error_code)
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-events="
           << snapshot.ratox_cgroup_pressure_admission_trigger_events
           << '\n'
           << "ratox-cgroup-pressure-admission-cpu-some-trigger-events="
           << snapshot
                  .ratox_cgroup_pressure_admission_cpu_some_trigger_events
           << '\n'
           << "ratox-cgroup-pressure-admission-memory-full-trigger-events="
           << snapshot
                  .ratox_cgroup_pressure_admission_memory_full_trigger_events
           << '\n'
           << "ratox-cgroup-pressure-admission-io-full-trigger-events="
           << snapshot.ratox_cgroup_pressure_admission_io_full_trigger_events
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-monitor-failures="
           << snapshot
                  .ratox_cgroup_pressure_admission_trigger_monitor_failures
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-closed-transitions="
           << snapshot
                  .ratox_cgroup_pressure_admission_trigger_closed_transitions
           << '\n'
           << "ratox-cgroup-pressure-admission-trigger-hold-rejections="
           << snapshot
                  .ratox_cgroup_pressure_admission_trigger_hold_rejections
           << '\n'
           << "ratox-cgroup-pressure-admission-last-sample-valid="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_last_sample_valid)
           << '\n'
           << "ratox-cgroup-pressure-admission-last-sampling-error-code="
           << to_string(
                  snapshot
                      .ratox_cgroup_pressure_admission_last_sampling_error_code)
           << '\n'
           << "ratox-cgroup-pressure-admission-last-cpu-some-observed="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_last_cpu_some_observed)
           << '\n'
           << "ratox-cgroup-pressure-admission-last-memory-full-observed="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_last_memory_full_observed)
           << '\n'
           << "ratox-cgroup-pressure-admission-last-io-full-observed="
           << boolean_value(
                  snapshot
                      .ratox_cgroup_pressure_admission_last_io_full_observed)
           << '\n'
           << "ratox-cgroup-pressure-admission-last-cpu-some-avg10-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_last_cpu_some_avg10_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-last-memory-full-avg10-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_last_memory_full_avg10_basis_points
           << '\n'
           << "ratox-cgroup-pressure-admission-last-io-full-avg10-bp="
           << snapshot
                  .ratox_cgroup_pressure_admission_last_io_full_avg10_basis_points
           << '\n'
           << "ratox-cgroup-completed-session-outcomes="
           << snapshot.ratox_cgroup_completed_session_outcomes << '\n'
           << "ratox-cgroup-incomplete-session-outcomes="
           << snapshot.ratox_cgroup_incomplete_session_outcomes << '\n'
           << "ratox-cgroup-pids-limit-hits="
           << snapshot.ratox_cgroup_pids_limit_hits << '\n'
           << "ratox-cgroup-memory-high-events="
           << snapshot.ratox_cgroup_memory_high_events << '\n'
           << "ratox-cgroup-memory-max-events="
           << snapshot.ratox_cgroup_memory_max_events << '\n'
           << "ratox-cgroup-memory-oom-events="
           << snapshot.ratox_cgroup_memory_oom_events << '\n'
           << "ratox-cgroup-memory-oom-kills="
           << snapshot.ratox_cgroup_memory_oom_kills << '\n'
           << "ratox-cgroup-memory-oom-group-kills="
           << snapshot.ratox_cgroup_memory_oom_group_kills << '\n'
           << "ratox-cgroup-pids-peak-session-outcomes="
           << snapshot.ratox_cgroup_pids_peak_session_outcomes << '\n'
           << "ratox-cgroup-pids-peak-sum="
           << snapshot.ratox_cgroup_pids_peak_sum << '\n'
           << "ratox-cgroup-pids-peak-max="
           << snapshot.ratox_cgroup_pids_peak_maximum << '\n'
           << "ratox-cgroup-memory-peak-session-outcomes="
           << snapshot.ratox_cgroup_memory_peak_session_outcomes << '\n'
           << "ratox-cgroup-memory-peak-sum-bytes="
           << snapshot.ratox_cgroup_memory_peak_sum_bytes << '\n'
           << "ratox-cgroup-memory-peak-max-bytes="
           << snapshot.ratox_cgroup_memory_peak_maximum_bytes << '\n'
           << "ratox-cgroup-memory-swap-peak-session-outcomes="
           << snapshot.ratox_cgroup_memory_swap_peak_session_outcomes << '\n'
           << "ratox-cgroup-memory-swap-peak-sum-bytes="
           << snapshot.ratox_cgroup_memory_swap_peak_sum_bytes << '\n'
           << "ratox-cgroup-memory-swap-peak-max-bytes="
           << snapshot.ratox_cgroup_memory_swap_peak_maximum_bytes << '\n'
           << "ratox-cgroup-memory-stat-session-outcomes="
           << snapshot.ratox_cgroup_memory_stat_session_outcomes << '\n'
           << "ratox-cgroup-memory-reclaim-stat-session-outcomes="
           << snapshot.ratox_cgroup_memory_reclaim_stat_session_outcomes
           << '\n'
           << "ratox-cgroup-memory-swap-stat-session-outcomes="
           << snapshot.ratox_cgroup_memory_swap_stat_session_outcomes << '\n'
           << "ratox-cgroup-memory-page-faults="
           << snapshot.ratox_cgroup_memory_page_faults << '\n'
           << "ratox-cgroup-memory-major-page-faults="
           << snapshot.ratox_cgroup_memory_major_page_faults << '\n'
           << "ratox-cgroup-memory-pages-scanned="
           << snapshot.ratox_cgroup_memory_pages_scanned << '\n'
           << "ratox-cgroup-memory-pages-reclaimed="
           << snapshot.ratox_cgroup_memory_pages_reclaimed << '\n'
           << "ratox-cgroup-memory-pages-swapped-in="
           << snapshot.ratox_cgroup_memory_pages_swapped_in << '\n'
           << "ratox-cgroup-memory-pages-swapped-out="
           << snapshot.ratox_cgroup_memory_pages_swapped_out << '\n'
           << "ratox-cgroup-memory-swap-events-session-outcomes="
           << snapshot.ratox_cgroup_memory_swap_events_session_outcomes
           << '\n'
           << "ratox-cgroup-memory-swap-high-events="
           << snapshot.ratox_cgroup_memory_swap_high_events << '\n'
           << "ratox-cgroup-memory-swap-max-events="
           << snapshot.ratox_cgroup_memory_swap_max_events << '\n'
           << "ratox-cgroup-memory-swap-fail-events="
           << snapshot.ratox_cgroup_memory_swap_fail_events << '\n'
           << "ratox-cgroup-local-stat-session-outcomes="
           << snapshot.ratox_cgroup_local_stat_session_outcomes << '\n'
           << "ratox-cgroup-frozen-us="
           << snapshot.ratox_cgroup_frozen_microseconds << '\n'
           << "ratox-cgroup-cpu-stat-session-outcomes="
           << snapshot.ratox_cgroup_cpu_stat_session_outcomes << '\n'
           << "ratox-cgroup-cpu-bandwidth-stat-session-outcomes="
           << snapshot.ratox_cgroup_cpu_bandwidth_stat_session_outcomes << '\n'
           << "ratox-cgroup-cpu-burst-stat-session-outcomes="
           << snapshot.ratox_cgroup_cpu_burst_stat_session_outcomes << '\n'
           << "ratox-cgroup-cpu-usage-us="
           << snapshot.ratox_cgroup_cpu_usage_microseconds << '\n'
           << "ratox-cgroup-cpu-user-us="
           << snapshot.ratox_cgroup_cpu_user_microseconds << '\n'
           << "ratox-cgroup-cpu-system-us="
           << snapshot.ratox_cgroup_cpu_system_microseconds << '\n'
           << "ratox-cgroup-cpu-periods="
           << snapshot.ratox_cgroup_cpu_periods << '\n'
           << "ratox-cgroup-cpu-throttled-periods="
           << snapshot.ratox_cgroup_cpu_throttled_periods << '\n'
           << "ratox-cgroup-cpu-throttled-us="
           << snapshot.ratox_cgroup_cpu_throttled_microseconds << '\n'
           << "ratox-cgroup-cpu-burst-periods="
           << snapshot.ratox_cgroup_cpu_burst_periods << '\n'
           << "ratox-cgroup-cpu-burst-us="
           << snapshot.ratox_cgroup_cpu_burst_microseconds << '\n'
           << "ratox-cgroup-io-read-bytes="
           << snapshot.ratox_cgroup_io_read_bytes << '\n'
           << "ratox-cgroup-io-write-bytes="
           << snapshot.ratox_cgroup_io_write_bytes << '\n'
           << "ratox-cgroup-io-read-operations="
           << snapshot.ratox_cgroup_io_read_operations << '\n'
           << "ratox-cgroup-io-write-operations="
           << snapshot.ratox_cgroup_io_write_operations << '\n'
           << "ratox-cgroup-io-discard-bytes="
           << snapshot.ratox_cgroup_io_discard_bytes << '\n'
           << "ratox-cgroup-io-discard-operations="
           << snapshot.ratox_cgroup_io_discard_operations << '\n'
           << "ratox-cgroup-cpu-pressure-session-outcomes="
           << snapshot.ratox_cgroup_cpu_pressure_session_outcomes << '\n'
           << "ratox-cgroup-cpu-pressure-full-session-outcomes="
           << snapshot.ratox_cgroup_cpu_pressure_full_session_outcomes << '\n'
           << "ratox-cgroup-cpu-pressure-some-us="
           << snapshot.ratox_cgroup_cpu_pressure_some_microseconds << '\n'
           << "ratox-cgroup-cpu-pressure-full-us="
           << snapshot.ratox_cgroup_cpu_pressure_full_microseconds << '\n'
           << "ratox-cgroup-memory-pressure-session-outcomes="
           << snapshot.ratox_cgroup_memory_pressure_session_outcomes << '\n'
           << "ratox-cgroup-memory-pressure-full-session-outcomes="
           << snapshot.ratox_cgroup_memory_pressure_full_session_outcomes
           << '\n'
           << "ratox-cgroup-memory-pressure-some-us="
           << snapshot.ratox_cgroup_memory_pressure_some_microseconds << '\n'
           << "ratox-cgroup-memory-pressure-full-us="
           << snapshot.ratox_cgroup_memory_pressure_full_microseconds << '\n'
           << "ratox-cgroup-io-pressure-session-outcomes="
           << snapshot.ratox_cgroup_io_pressure_session_outcomes << '\n'
           << "ratox-cgroup-io-pressure-full-session-outcomes="
           << snapshot.ratox_cgroup_io_pressure_full_session_outcomes << '\n'
           << "ratox-cgroup-io-pressure-some-us="
           << snapshot.ratox_cgroup_io_pressure_some_microseconds << '\n'
           << "ratox-cgroup-io-pressure-full-us="
           << snapshot.ratox_cgroup_io_pressure_full_microseconds << '\n'
           << "ratox-cgroup-irq-pressure-session-outcomes="
           << snapshot.ratox_cgroup_irq_pressure_session_outcomes << '\n'
           << "ratox-cgroup-irq-pressure-full-us="
           << snapshot.ratox_cgroup_irq_pressure_full_microseconds << '\n'
           << "ratox-cgroup-profile-budget-count="
           << snapshot.ratox_cgroup_profile_budget_count << '\n'
           << "ratox-cgroup-preflight-policy-count="
           << snapshot.ratox_cgroup_preflight_policy_count << '\n'
           << "ratox-cgroup-recovery-reserved-names="
           << snapshot.ratox_cgroup_recovery_reserved_names << '\n'
           << "ratox-cgroup-recovery-live-incarnations="
           << snapshot.ratox_cgroup_recovery_live_incarnations << '\n'
           << "ratox-cgroup-recovery-stale-incarnations="
           << snapshot.ratox_cgroup_recovery_stale_incarnations << '\n'
           << "ratox-cgroup-recovery-recovered-incarnations="
           << snapshot.ratox_cgroup_recovery_recovered_incarnations << '\n'
           << "ratox-cgroup-recovery-empty-legacy-removed="
           << snapshot.ratox_cgroup_recovery_empty_legacy_removed << '\n'
           << "ratox-session-count=" << snapshot.ratox_session_count << '\n'
           << "ratox-live-session-count="
           << snapshot.ratox_live_session_count << '\n'
           << "ratox-session-tombstone-count="
           << snapshot.ratox_session_tombstone_count << '\n'
           << "ratox-running-process-count="
           << snapshot.ratox_running_process_count << '\n'
           << "ratox-attached-session-count="
           << snapshot.ratox_attached_session_count << '\n'
           << "ratox-closing-session-count="
           << snapshot.ratox_closing_session_count << '\n'
           << "ratox-admission-replay-count="
           << snapshot.ratox_admission_replay_count << '\n'
           << "ratox-pending-admission-count="
           << snapshot.ratox_pending_admission_count << '\n'
           << "ratox-admission-replay-bytes="
           << snapshot.ratox_admission_replay_bytes << '\n'
           << "ratox-outbound-packet-count="
           << snapshot.ratox_outbound_packet_count << '\n'
           << "ratox-outbound-bytes=" << snapshot.ratox_outbound_bytes << '\n'
           << "ratox-event-count=" << snapshot.ratox_event_count << '\n'
           << "ratox-dropped-event-count="
           << snapshot.ratox_dropped_event_count << '\n'
           << "ratox-controller-retryable-send-rejections="
           << snapshot.ratox_controller_retryable_send_rejections << '\n'
           << "ratox-controller-current-retry-streak="
           << snapshot.ratox_controller_current_retry_streak << '\n'
           << "ratox-controller-maximum-retry-streak="
           << snapshot.ratox_controller_maximum_retry_streak << '\n'
           << "ratox-controller-retry-age-us="
           << snapshot.ratox_controller_retry_age_us << '\n'
           << "ratox-host-retryable-send-rejections="
           << snapshot.ratox_host_retryable_send_rejections << '\n'
           << "ratox-host-current-retry-streak="
           << snapshot.ratox_host_current_retry_streak << '\n'
           << "ratox-host-maximum-retry-streak="
           << snapshot.ratox_host_maximum_retry_streak << '\n'
           << "ratox-host-retry-age-us="
           << snapshot.ratox_host_retry_age_us << '\n'
           << "pending-request-count=" << snapshot.pending_request_count << '\n'
           << "incoming-file-offer-count=" << snapshot.incoming_file_offer_count << '\n'
           << "active-file-transfer-count=" << snapshot.active_file_transfer_count << '\n'
           << "dropped-event-count=" << snapshot.dropped_event_count << '\n'
           << "transport-pending-commands="
           << snapshot.transport_stats.pending_commands << '\n'
           << "transport-pending-events="
           << snapshot.transport_stats.pending_events << '\n'
           << "transport-maximum-pending-events="
           << snapshot.transport_stats.maximum_pending_events << '\n'
           << "transport-required-event-backpressure-count="
           << snapshot.transport_stats.required_event_backpressure_count
           << '\n'
           << "transport-required-event-backpressure-total-us="
           << snapshot.transport_stats.required_event_backpressure_total_us
           << '\n'
           << "transport-required-event-backpressure-maximum-us="
           << snapshot.transport_stats.required_event_backpressure_maximum_us
           << '\n'
           << "transport-file-pacing-paused-transfers="
           << snapshot.transport_stats.file_pacing_paused_transfers << '\n'
           << "transport-file-pacing-high-watermark="
           << snapshot.transport_stats.file_pacing_high_watermark << '\n'
           << "transport-file-pacing-low-watermark="
           << snapshot.transport_stats.file_pacing_low_watermark << '\n'
           << "transport-file-pacing-minimum-hold-us="
           << snapshot.transport_stats.file_pacing_minimum_hold_us << '\n'
           << "transport-file-pacing-resume-batch-limit="
           << snapshot.transport_stats.file_pacing_resume_batch_limit << '\n'
           << "transport-file-pacing-pause-count="
           << snapshot.transport_stats.file_pacing_pause_count << '\n'
           << "transport-file-pacing-resume-count="
           << snapshot.transport_stats.file_pacing_resume_count << '\n'
           << "transport-file-pacing-resume-batch-count="
           << snapshot.transport_stats.file_pacing_resume_batch_count << '\n'
           << "transport-file-pacing-resume-batch-maximum="
           << snapshot.transport_stats.file_pacing_resume_batch_maximum << '\n'
           << "transport-file-pacing-external-pause-count="
           << snapshot.transport_stats.file_pacing_external_pause_count << '\n'
           << "transport-file-pacing-pause-failure-count="
           << snapshot.transport_stats.file_pacing_pause_failure_count << '\n'
           << "transport-file-pacing-resume-failure-count="
           << snapshot.transport_stats.file_pacing_resume_failure_count << '\n'
           << "transport-file-pacing-total-hold-us="
           << snapshot.transport_stats.file_pacing_total_hold_us << '\n'
           << "transport-file-pacing-maximum-hold-us="
           << snapshot.transport_stats.file_pacing_maximum_hold_us << '\n'
           << "file-carrier-window-per-peer="
           << snapshot.file_carrier_stats.window_per_peer << '\n'
           << "file-carrier-rotation-quantum-ms="
           << snapshot.file_carrier_stats.rotation_quantum_ms << '\n'
           << "file-carrier-runnable-receives="
           << snapshot.file_carrier_stats.runnable_receives << '\n'
           << "file-carrier-waiting-receives="
           << snapshot.file_carrier_stats.waiting_receives << '\n'
           << "file-carrier-admission-count="
           << snapshot.file_carrier_stats.admission_count << '\n'
           << "file-carrier-rotation-count="
           << snapshot.file_carrier_stats.rotation_count << '\n'
           << "file-carrier-pause-count="
           << snapshot.file_carrier_stats.pause_count << '\n'
           << "file-carrier-resume-count="
           << snapshot.file_carrier_stats.resume_count << '\n'
           << "file-carrier-control-failure-count="
           << snapshot.file_carrier_stats.control_failure_count << '\n'
           << "file-carrier-total-wait-us="
           << snapshot.file_carrier_stats.total_wait_us << '\n'
           << "file-carrier-maximum-wait-us="
           << snapshot.file_carrier_stats.maximum_wait_us << '\n'
           << "transport-iteration-count="
           << snapshot.transport_stats.iteration_count << '\n'
           << "transport-requested-iteration-ms="
           << snapshot.transport_stats.requested_iteration_interval_ms << '\n'
           << "transport-effective-iteration-ms="
           << snapshot.transport_stats.effective_iteration_interval_ms << '\n'
           << "transport-pending-interactive="
           << snapshot.transport_stats.interactive.pending_commands << '\n'
           << "transport-pending-control="
           << snapshot.transport_stats.control.pending_commands << '\n'
           << "transport-pending-bulk="
           << snapshot.transport_stats.bulk.pending_commands << '\n'
           << "transport-interactive-executed="
           << snapshot.transport_stats.interactive.executed_commands << '\n'
           << "transport-interactive-total-queue-wait-us="
           << snapshot.transport_stats.interactive.total_queue_wait_us << '\n'
           << "transport-control-executed="
           << snapshot.transport_stats.control.executed_commands << '\n'
           << "transport-bulk-executed="
           << snapshot.transport_stats.bulk.executed_commands << '\n'
           << "transport-interactive-max-queue-wait-us="
           << snapshot.transport_stats.interactive.maximum_queue_wait_us << '\n'
           << "transport-interactive-queue-wait-p50-upper-bound-us="
           << snapshot.transport_stats.interactive.queue_wait_p50_upper_bound_us << '\n'
           << "transport-interactive-queue-wait-p50-exact="
           << (snapshot.transport_stats.interactive.queue_wait_p50_exact ? 1 : 0) << '\n'
           << "transport-interactive-queue-wait-p95-upper-bound-us="
           << snapshot.transport_stats.interactive.queue_wait_p95_upper_bound_us << '\n'
           << "transport-interactive-queue-wait-p95-exact="
           << (snapshot.transport_stats.interactive.queue_wait_p95_exact ? 1 : 0) << '\n'
           << "transport-interactive-queue-wait-p99-upper-bound-us="
           << snapshot.transport_stats.interactive.queue_wait_p99_upper_bound_us << '\n'
           << "transport-interactive-queue-wait-p99-exact="
           << (snapshot.transport_stats.interactive.queue_wait_p99_exact ? 1 : 0) << '\n'
           << "transport-interactive-queue-wait-at-or-above-2000-us="
           << snapshot.transport_stats.interactive.queue_wait_at_or_above_2000_us << '\n'
           << "transport-control-max-queue-wait-us="
           << snapshot.transport_stats.control.maximum_queue_wait_us << '\n'
           << "transport-control-queue-wait-p50-upper-bound-us="
           << snapshot.transport_stats.control.queue_wait_p50_upper_bound_us << '\n'
           << "transport-control-queue-wait-p50-exact="
           << (snapshot.transport_stats.control.queue_wait_p50_exact ? 1 : 0) << '\n'
           << "transport-control-queue-wait-p95-upper-bound-us="
           << snapshot.transport_stats.control.queue_wait_p95_upper_bound_us << '\n'
           << "transport-control-queue-wait-p95-exact="
           << (snapshot.transport_stats.control.queue_wait_p95_exact ? 1 : 0) << '\n'
           << "transport-control-queue-wait-p99-upper-bound-us="
           << snapshot.transport_stats.control.queue_wait_p99_upper_bound_us << '\n'
           << "transport-control-queue-wait-p99-exact="
           << (snapshot.transport_stats.control.queue_wait_p99_exact ? 1 : 0) << '\n'
           << "transport-control-queue-wait-at-or-above-2000-us="
           << snapshot.transport_stats.control.queue_wait_at_or_above_2000_us << '\n'
           << "transport-bulk-max-queue-wait-us="
           << snapshot.transport_stats.bulk.maximum_queue_wait_us << '\n'
           << "transport-bulk-queue-wait-p50-upper-bound-us="
           << snapshot.transport_stats.bulk.queue_wait_p50_upper_bound_us << '\n'
           << "transport-bulk-queue-wait-p50-exact="
           << (snapshot.transport_stats.bulk.queue_wait_p50_exact ? 1 : 0) << '\n'
           << "transport-bulk-queue-wait-p95-upper-bound-us="
           << snapshot.transport_stats.bulk.queue_wait_p95_upper_bound_us << '\n'
           << "transport-bulk-queue-wait-p95-exact="
           << (snapshot.transport_stats.bulk.queue_wait_p95_exact ? 1 : 0) << '\n'
           << "transport-bulk-queue-wait-p99-upper-bound-us="
           << snapshot.transport_stats.bulk.queue_wait_p99_upper_bound_us << '\n'
           << "transport-bulk-queue-wait-p99-exact="
           << (snapshot.transport_stats.bulk.queue_wait_p99_exact ? 1 : 0) << '\n'
           << "transport-bulk-queue-wait-at-or-above-2000-us="
           << snapshot.transport_stats.bulk.queue_wait_at_or_above_2000_us << '\n'
           << "transport-sensitive-lossless-calls="
           << snapshot.transport_stats.sensitive_lossless.calls << '\n'
           << "transport-sensitive-lossless-toxcore-attempts="
           << snapshot.transport_stats.sensitive_lossless.toxcore_attempts << '\n'
           << "transport-sensitive-lossless-accepted="
           << snapshot.transport_stats.sensitive_lossless.accepted << '\n'
           << "transport-sensitive-lossless-send-queue-full="
           << snapshot.transport_stats.sensitive_lossless.send_queue_full << '\n'
           << "transport-sensitive-lossless-peer-not-connected="
           << snapshot.transport_stats.sensitive_lossless.peer_not_connected << '\n'
           << "transport-sensitive-lossless-peer-not-found="
           << snapshot.transport_stats.sensitive_lossless.peer_not_found << '\n'
           << "transport-sensitive-lossless-contract-rejections="
           << snapshot.transport_stats.sensitive_lossless.contract_rejections << '\n'
           << "transport-sensitive-lossless-other-failures="
           << snapshot.transport_stats.sensitive_lossless.other_failures << '\n'
           << "sodium-provider=" << escape_field(snapshot.sodium_provider) << '\n'
           << "sodium-version=" << escape_field(snapshot.sodium_version) << '\n'
           << "device-public-key=" << escape_field(snapshot.device_public_key) << '\n'
           << "authority-initialized=" << (snapshot.authority_initialized ? 1 : 0) << '\n'
           << "ownership-epoch=" << snapshot.ownership_epoch << '\n'
           << "authority-sequence=" << snapshot.authority_sequence << '\n'
           << "authority-record-count=" << snapshot.authority_record_count << '\n'
           << "authority-principal-count=" << snapshot.authority_principal_count << '\n'
           << "active-authority-principal-count="
           << snapshot.active_authority_principal_count << '\n'
           << "active-authority-owner-count="
           << snapshot.active_authority_owner_count << '\n'
           << "command-store-initialized="
           << (snapshot.command_store_initialized ? 1 : 0) << '\n'
           << "command-store-generation="
           << snapshot.command_store_generation << '\n'
           << "command-sender-epoch="
           << snapshot.command_sender_epoch << '\n'
           << "durable-command-record-count="
           << snapshot.durable_command_record_count << '\n'
           << "durable-command-incoming-count="
           << snapshot.incoming_command_record_count << '\n'
           << "durable-command-outgoing-count="
           << snapshot.outgoing_command_record_count << '\n'
           << "durable-command-unfinished-count="
           << snapshot.pending_command_record_count << '\n'
           << "command-clock-trusted="
           << (snapshot.command_clock_trusted ? 1 : 0) << '\n'
           << "command-clock-high-water-unix-ms="
           << snapshot.command_clock_high_water_unix_ms << '\n'
           << "due-command-artifact-count="
           << snapshot.due_command_artifact_count << '\n'
           << "held-expiring-command-count="
           << snapshot.held_expiring_command_count << '\n'
           << "command-fifo-running="
           << (snapshot.command_fifo_running ? 1 : 0) << '\n'
           << "command-fifo-count=" << snapshot.command_fifo_count << '\n'
           << "command-fifo-record-count="
           << snapshot.command_fifo_record_count << '\n'
           << "command-fifo-rejected-count="
           << snapshot.command_fifo_rejected_count << '\n'
           << "text-fifo-running="
           << (snapshot.text_fifo_running ? 1 : 0) << '\n'
           << "message-fifo-count=" << snapshot.message_fifo_count << '\n'
           << "action-fifo-count=" << snapshot.action_fifo_count << '\n'
           << "text-fifo-record-count="
           << snapshot.text_fifo_record_count << '\n'
           << "text-fifo-rejected-count="
           << snapshot.text_fifo_rejected_count << '\n'
           << "file-fifo-running="
           << (snapshot.file_fifo_running ? 1 : 0) << '\n'
           << "file-send-fifo-count=" << snapshot.file_send_fifo_count << '\n'
           << "file-receive-fifo-count="
           << snapshot.file_receive_fifo_count << '\n'
           << "file-control-fifo-count="
           << snapshot.file_control_fifo_count << '\n'
           << "file-fifo-record-count="
           << snapshot.file_fifo_record_count << '\n'
           << "file-fifo-rejected-count="
           << snapshot.file_fifo_rejected_count << '\n'
           << "friendship-fifo-running="
           << (snapshot.friendship_fifo_running ? 1 : 0) << '\n'
           << "request-send-fifo-count="
           << snapshot.request_send_fifo_count << '\n'
           << "request-accept-fifo-count="
           << snapshot.request_accept_fifo_count << '\n'
           << "request-reject-fifo-count="
           << snapshot.request_reject_fifo_count << '\n'
           << "peer-remove-fifo-count="
           << snapshot.peer_remove_fifo_count << '\n'
           << "friendship-fifo-record-count="
           << snapshot.friendship_fifo_record_count << '\n'
           << "friendship-fifo-rejected-count="
           << snapshot.friendship_fifo_rejected_count << '\n';
    return output.str();
}

Status RuntimeTree::publish(const RuntimeSnapshot &snapshot) {
    std::scoped_lock lock(surface_mutex_);
    const std::string status = render_snapshot(snapshot);
    for (const auto &[path, value] :
         {std::pair{config_.root / "status", status},
          std::pair{config_.root / "self" / "address", snapshot.address + "\n"},
          std::pair{config_.root / "self" / "connection", snapshot.self_connection + "\n"},
          std::pair{config_.root / "self" / "network", snapshot.network + "\n"},
          std::pair{config_.root / "self" / "name-bytes",
                    std::to_string(snapshot.profile.name.size()) + "\n"},
          std::pair{config_.root / "self" / "status-message-bytes",
                    std::to_string(snapshot.profile.status_message.size()) + "\n"},
          std::pair{config_.root / "self" / "status",
                    to_string(snapshot.profile.status) + "\n"},
          std::pair{config_.root / "self" / "revision", std::string(kRevision) + "\n"}}) {
        const Status written = write_text(path, value);
        if (!written.ok()) {
            return written;
        }
    }
    const Status name = write_bytes(config_.root / "self" / "name", snapshot.profile.name);
    if (!name.ok()) {
        return name;
    }
    const Status status_message = write_bytes(
        config_.root / "self" / "status-message",
        snapshot.profile.status_message);
    if (!status_message.ok()) {
        return status_message;
    }
    return Status::success();
}

Status RuntimeTree::publish_peers(std::span<const TransportPeer> peers) {
    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path peers_root = config_.root / "peers";
    const Status root_status = validate_or_create_directory(peers_root, 0700U);
    if (!root_status.ok()) {
        return root_status;
    }

    std::set<std::string> active;
    for (const TransportPeer &peer : peers) {
        const std::string key = public_key_hex(peer.public_key);
        active.insert(key);
        const std::filesystem::path directory = peers_root / key;
        const Status directory_status = validate_or_create_directory(directory, 0700U);
        if (!directory_status.ok()) {
            return directory_status;
        }
        for (const auto &[path, value] :
             {std::pair{directory / "number", std::to_string(peer.friend_number) + "\n"},
              std::pair{directory / "public-key", key + "\n"},
              std::pair{directory / "connection",
                        transport_connection_name(peer.connection_status) + "\n"},
              std::pair{directory / "online",
                        std::string(peer.connection_status == 0 ? "0\n" : "1\n")},
              std::pair{directory / "name-bytes",
                        std::to_string(peer.name.size()) + "\n"},
              std::pair{directory / "status-message-bytes",
                        std::to_string(peer.status_message.size()) + "\n"},
              std::pair{directory / "status", to_string(peer.status) + "\n"},
              std::pair{directory / "typing",
                        std::string(peer.typing ? "1\n" : "0\n")}}) {
            const Status written = write_text(path, value);
            if (!written.ok()) {
                return written;
            }
        }
        const Status name_status = write_bytes(directory / "name", peer.name);
        if (!name_status.ok()) {
            return name_status;
        }
        const Status status_message_status =
            write_bytes(directory / "status-message", peer.status_message);
        if (!status_message_status.ok()) {
            return status_message_status;
        }

        const Status command_help = write_text(
            directory / "command.help",
            "IoTox ratox-successor command ingress v1\n"
            "write exactly one printable ASCII operation followed by LF\n"
            "maximum-record-bytes=256\n"
            "recommended-write-bytes<=257 including LF (one atomic FIFO write)\n"
            "operation=device.describe\n"
            "operation=system.summary\n"
            "operation=profile.status.set available|away|busy\n"
            "profile.status.set requires write.settings and a durable confirmed session\n"
            "accepted records enter the same signed durable command path as the structured client\n"
            "an existing offline friend may be admitted; transport waits for a confirmed authorized session\n"
            "use the typed command-cancel operation with the emitted durable key before its first attempt\n"
            "ingress admission and rejection are appended to command-events\n"
            "typed terminal results are projected under commands/; device.describe also uses iotox/description\n"
            "FIFO bytes are transient; only an admitted durable command is authoritative\n");
        if (!command_help.ok()) {
            return command_help;
        }
        const Status command_events =
            validate_or_create_private_file(directory / "command-events");
        if (!command_events.ok()) {
            return command_events;
        }
        const Status command_fifo =
            validate_or_create_fifo(directory / "command", 0600U);
        if (!command_fifo.ok()) {
            return command_fifo;
        }

        const Status message_help = write_text(
            directory / "message.help",
            "IoTox ratox-successor human text ingress v1\n"
            "message=normal Tox text FIFO\n"
            "action=Tox action text FIFO\n"
            "write exactly one body followed by LF in one write(2)\n"
            "maximum-body-bytes=1372\n"
            "maximum-write-bytes=1373 including LF\n"
            "LF is the record delimiter and is not sent\n"
            "the local adapter preserves every other byte\n"
            "Tox human-text interoperability expects valid UTF-8\n"
            "arbitrary binary belongs in IoTox packets or file transfer, not this text lane\n"
            "empty bodies are rejected\n"
            "embedded LF cannot be represented here; use message-stdin, action-stdin, message-hex, or action-hex\n"
            "FIFO write success means only that the kernel accepted bytes\n"
            "message-events records local ingress acceptance or rejection\n"
            "messages records c-toxcore accepted sends, incoming text, and read receipts\n"
            "a friend disconnect abandons any still-pending text receipt correlations\n"
            "this lane is live transport, not a durable offline queue and not device authorization\n");
        if (!message_help.ok()) {
            return message_help;
        }
        const Status message_events =
            validate_or_create_private_file(directory / "message-events");
        if (!message_events.ok()) {
            return message_events;
        }
        const Status message_fifo =
            validate_or_create_fifo(directory / "message", 0600U);
        if (!message_fifo.ok()) {
            return message_fifo;
        }
        const Status action_fifo =
            validate_or_create_fifo(directory / "action", 0600U);
        if (!action_fifo.ok()) {
            return action_fifo;
        }

        const Status file_help = write_text(
            directory / "file.help",
            "IoTox ratox-successor finite-file ingress v1\n"
            "file-send=<absolute source path>\n"
            "file-receive=<decimal file number><TAB><absolute destination path>\n"
            "file-control=<decimal file number><TAB><pause|resume|cancel>\n"
            "write exactly one record followed by LF in one atomic write(2)\n"
            "maximum-record-bytes=4095 excluding LF\n"
            "the FIFO names local paths; file bytes never pass through these FIFOs\n"
            "relative paths, NUL, embedded LF, shell expansion, and globbing are rejected or not performed\n"
            "structured file-send/file-receive/file-control remain the escape hatch for records not representable here\n"
            "FIFO write success means only that the kernel accepted bytes\n"
            "file-events records local admission/rejection and later toxcore file callbacks\n"
            "files/incoming and files/outgoing are disposable live projections\n"
            "incoming completion is authoritative only when the requested destination appears atomically\n"
            "friend disconnect purges toxcore transfers; this surface is not an offline file queue\n"
            "all paths are interpreted in the IoTox process mount namespace and privilege context\n");
        if (!file_help.ok()) {
            return file_help;
        }
        const Status file_send_help = write_text(
            directory / "file-send.help",
            "record=<absolute source path>\n"
            "example=/home/alice/archive.tar\n"
            "IoTox opens the named source with no-follow regular-file checks and offers its basename\n"
            "admission assigns a friend-specific toxcore file number visible in file-events and files/outgoing\n");
        if (!file_send_help.ok()) {
            return file_send_help;
        }
        const Status file_receive_help = write_text(
            directory / "file-receive.help",
            "record=<decimal file number><TAB><absolute destination path>\n"
            "example=7<TAB>/home/alice/inbox/report.bin\n"
            "the destination must not exist and its real parent directory must be owned by the IoTox user\n"
            "admission means a private temporary file was acquired and RESUME was accepted; it does not promise continued residency\n");
        if (!file_receive_help.ok()) {
            return file_receive_help;
        }
        const Status file_control_help = write_text(
            directory / "file-control.help",
            "record=<decimal file number><TAB><pause|resume|cancel>\n"
            "example=7<TAB>pause\n"
            "pause and resume control only the local side; transfer proceeds only when neither side is paused\n"
            "an unaccepted incoming offer cannot be resumed here because it has no safe destination; use file-receive first\n"
            "cancel releases IoTox local resources even when the toxcore control packet cannot be queued\n"
            "the file number is scoped to this peer and may be reused after the transfer terminates\n");
        if (!file_control_help.ok()) {
            return file_control_help;
        }
        const Status file_events =
            validate_or_create_private_file(directory / "file-events");
        if (!file_events.ok()) {
            return file_events;
        }
        for (const auto &path : {directory / "files",
                                 directory / "files" / "incoming",
                                 directory / "files" / "outgoing"}) {
            const Status created = validate_or_create_directory(path, 0700U);
            if (!created.ok()) {
                return created;
            }
        }
        for (const auto &path : {directory / "file-send",
                                 directory / "file-receive",
                                 directory / "file-control"}) {
            const Status fifo = validate_or_create_fifo(path, 0600U);
            if (!fifo.ok()) {
                return fifo;
            }
        }

        const Status lifecycle_help = write_text(
            directory / "lifecycle.help",
            "IoTox ratox-successor established friendship lifecycle v1\n"
            "remove=write exactly remove followed by LF in one atomic write(2)\n"
            "maximum-record-bytes=6 excluding LF\n"
            "FIFO write success means only that the kernel accepted bytes\n"
            "a successful decision calls tox_friend_delete and removes the live peer projection\n"
            "toxcore does not notify the remote peer that this local friendship was removed\n"
            "removing Tox friendship does not revoke, erase, or mutate IoTox authorization records\n"
            "friend-events at the runtime root records the attempted decision and its result\n"
            "friend numbers are transient; this directory's public key is the stable transport selector\n");
        if (!lifecycle_help.ok()) {
            return lifecycle_help;
        }
        const Status remove_fifo =
            validate_or_create_fifo(directory / "remove", 0600U);
        if (!remove_fifo.ok()) {
            return remove_fifo;
        }
    }

    std::error_code iterator_error;
    for (std::filesystem::directory_iterator iterator(peers_root, iterator_error), end;
         !iterator_error && iterator != end; iterator.increment(iterator_error)) {
        const std::string name = iterator->path().filename().string();
        if (!active.contains(name)) {
            const Status removed = remove_entry(iterator->path());
            if (!removed.ok()) {
                return removed;
            }
        }
    }
    if (iterator_error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate runtime peers: " + iterator_error.message()};
    }
    return Status::success();
}

std::string RuntimeTree::render_peer_session(
    const protocol::PeerSessionSnapshot &session) {
    const auto version = [](protocol::ProtocolVersion value) {
        return std::to_string(static_cast<unsigned int>(value.major)) + "." +
               std::to_string(static_cast<unsigned int>(value.minor));
    };
    std::ostringstream output;
    output << "friend-number=" << session.friend_number << '\n'
           << "public-key=" << session.public_key << '\n'
           << "state=" << protocol::to_string(session.state) << '\n'
           << "connected=" << (session.connected ? 1 : 0) << '\n'
           << "connection="
           << transport_connection_name(session.connection_status) << '\n'
           << "online-epoch=" << session.online_epoch << '\n'
           << "updated-unix-ms=" << session.updated_unix_ms << '\n'
           << "hello-sent=" << (session.hello_sent ? 1 : 0) << '\n'
           << "hello-received=" << (session.hello_received ? 1 : 0) << '\n'
           << "hello-send-attempts=" << session.hello_send_attempts << '\n'
           << "local-hello-message-id="
           << session.local_hello_message_id << '\n'
           << "peer-hello-message-id="
           << session.peer_hello_message_id << '\n'
           << "local-protocol-min="
           << version(session.local.minimum_protocol) << '\n'
           << "local-protocol-max="
           << version(session.local.maximum_protocol) << '\n'
           << "local-implementation="
           << session.local.implementation_major << '.'
           << session.local.implementation_minor << '.'
           << session.local.implementation_patch << '\n'
           << "local-build-revision=" << session.local.build_revision << '\n'
           << "local-max-frame-payload="
           << session.local.maximum_frame_payload_size << '\n'
           << "local-supported-features="
           << protocol::render_feature_mask(session.local.supported_features)
           << '\n'
           << "local-required-features="
           << protocol::render_feature_mask(session.local.required_features)
           << '\n'
           << "local-max-finite-file-bytes="
           << session.local.maximum_finite_file_bytes << '\n'
           << "local-session-nonce="
           << protocol::nonce_hex(session.local.session_nonce) << '\n';
    if (session.hello_received) {
        output << "peer-protocol-min="
               << version(session.peer.minimum_protocol) << '\n'
               << "peer-protocol-max="
               << version(session.peer.maximum_protocol) << '\n'
               << "peer-implementation="
               << session.peer.implementation_major << '.'
               << session.peer.implementation_minor << '.'
               << session.peer.implementation_patch << '\n'
               << "peer-build-revision=" << session.peer.build_revision << '\n'
               << "peer-max-frame-payload="
               << session.peer.maximum_frame_payload_size << '\n'
               << "peer-supported-features="
               << protocol::render_feature_mask(
                      session.peer.supported_features)
               << '\n'
               << "peer-required-features="
               << protocol::render_feature_mask(
                      session.peer.required_features)
               << '\n'
               << "peer-max-finite-file-bytes="
               << session.peer.maximum_finite_file_bytes << '\n'
               << "peer-session-nonce="
               << protocol::nonce_hex(session.peer.session_nonce) << '\n';
    } else {
        output << "peer-protocol-min=none\n"
               << "peer-protocol-max=none\n"
               << "peer-implementation=none\n"
               << "peer-build-revision=none\n"
               << "peer-max-frame-payload=0\n"
               << "peer-supported-features=0x0000000000000000[none]\n"
               << "peer-required-features=0x0000000000000000[none]\n"
               << "peer-max-finite-file-bytes=0\n"
               << "peer-session-nonce=none\n";
    }
    output << "negotiated-compatible="
           << (session.negotiated.compatible ? 1 : 0) << '\n'
           << "negotiation-failure="
           << protocol::to_string(session.negotiated.failure) << '\n'
           << "negotiated-protocol="
           << (session.negotiated.compatible
                   ? version(session.negotiated.selected)
                   : std::string("none"))
           << '\n'
           << "negotiated-features="
           << protocol::render_feature_mask(
                  session.negotiated.shared_features)
           << '\n'
           << "negotiated-max-frame-payload="
           << session.negotiated.maximum_frame_payload_size << '\n'
           << "negotiated-max-finite-file-bytes="
           << session.negotiated.maximum_finite_file_bytes << '\n'
           << "confirmation-sent="
           << (session.confirmation_sent ? 1 : 0) << '\n'
           << "confirmation-received="
           << (session.confirmation_received ? 1 : 0) << '\n'
           << "confirmation-send-attempts="
           << session.confirmation_send_attempts << '\n'
           << "application-ready="
           << (protocol::is_application_ready(session) ? 1 : 0) << '\n'
           << "local-role="
           << (session.local_role_known
                   ? protocol::to_string(session.local_role)
                   : std::string("unknown"))
           << '\n'
           << "local-confirmation-message-id="
           << session.local_confirmation_message_id << '\n'
           << "peer-confirmation-message-id="
           << session.peer_confirmation_message_id << '\n'
           << "authorization=separate-authority-session\n"
           << "detail=" << escape_field(session.detail) << '\n';
    if (!session.last_hello_send_error.empty()) {
        output << "last-hello-send-error-code="
               << to_string(session.last_hello_send_error_code) << '\n'
               << "last-hello-send-error="
               << escape_field(session.last_hello_send_error) << '\n';
    }
    if (!session.last_confirmation_send_error.empty()) {
        output << "last-confirmation-send-error-code="
               << to_string(session.last_confirmation_send_error_code) << '\n'
               << "last-confirmation-send-error="
               << escape_field(session.last_confirmation_send_error) << '\n';
    }
    return output.str();
}

Status RuntimeTree::publish_peer_session(
    std::string_view public_key, const protocol::PeerSessionSnapshot &session) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session projection requires a 64-character uppercase public key"};
    }
    if (session.public_key != public_key) {
        return Status{ErrorCode::invalid_argument,
                      "peer-session projection public key does not match its snapshot"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path peer_directory =
        config_.root / "peers" / std::string(public_key);
    const Status peer_status = validate_or_create_directory(peer_directory, 0700U);
    if (!peer_status.ok()) {
        return peer_status;
    }
    const std::filesystem::path directory = peer_directory / "iotox";
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }

    const std::string summary = render_peer_session(session);
    const std::string protocol_version = session.negotiated.compatible
        ? std::to_string(static_cast<unsigned int>(
              session.negotiated.selected.major)) + "." +
              std::to_string(static_cast<unsigned int>(
                  session.negotiated.selected.minor)) + "\n"
        : std::string("none\n");
    // The root-level session file is the commit marker for this multi-file
    // projection. Publish every detailed field first, then replace `session`
    // atomically. A ratox-style reader that observes a new session summary can
    // therefore rely on the detailed `iotox/` fields already representing the
    // same or a newer snapshot.
    const std::array fields{
        std::pair{directory / "summary", summary},
        std::pair{directory / "state",
                  protocol::to_string(session.state) + "\n"},
        std::pair{directory / "hello-compatible",
                  std::string(session.negotiated.compatible ? "1\n" : "0\n")},
        std::pair{directory / "transcript-confirmed",
                  std::string(session.confirmation_sent &&
                                      session.confirmation_received
                                  ? "1\n"
                                  : "0\n")},
        std::pair{directory / "established",
                  std::string(
                      protocol::is_application_ready(session)
                          ? "1\n"
                          : "0\n")},
        std::pair{directory / "application-ready",
                  std::string(
                      protocol::is_application_ready(session)
                          ? "1\n"
                          : "0\n")},
        std::pair{directory / "confirmation-sent",
                  std::string(session.confirmation_sent ? "1\n" : "0\n")},
        std::pair{directory / "confirmation-received",
                  std::string(session.confirmation_received ? "1\n" : "0\n")},
        std::pair{directory / "local-role",
                  (session.local_role_known
                       ? protocol::to_string(session.local_role)
                       : std::string("unknown")) + "\n"},
        std::pair{directory / "local-confirmation-message-id",
                  std::to_string(session.local_confirmation_message_id) + "\n"},
        std::pair{directory / "peer-confirmation-message-id",
                  std::to_string(session.peer_confirmation_message_id) + "\n"},
        std::pair{directory / "online-epoch",
                  std::to_string(session.online_epoch) + "\n"},
        std::pair{directory / "protocol", protocol_version},
        std::pair{directory / "features",
                  protocol::render_feature_mask(
                      session.negotiated.shared_features) + "\n"},
        std::pair{directory / "feature-bits",
                  std::to_string(session.negotiated.shared_features) + "\n"},
        std::pair{directory / "max-frame-payload",
                  std::to_string(
                      session.negotiated.maximum_frame_payload_size) + "\n"},
        std::pair{directory / "max-finite-file-bytes",
                  std::to_string(
                      session.negotiated.maximum_finite_file_bytes) + "\n"},
        std::pair{directory / "local-session-nonce",
                  protocol::nonce_hex(session.local.session_nonce) + "\n"},
        std::pair{directory / "peer-session-nonce",
                  (session.hello_received
                       ? protocol::nonce_hex(session.peer.session_nonce)
                       : std::string("none")) + "\n"},
        std::pair{directory / "detail", session.detail + "\n"},
    };
    for (const auto &[path, value] : fields) {
        const Status written = write_text(path, value);
        if (!written.ok()) {
            return written;
        }
    }
    return write_text(peer_directory / "session", summary);
}

std::string RuntimeTree::render_peer_authority(
    const security::PeerAuthoritySnapshot &authority) {
    return security::render_peer_authority(authority);
}

Status RuntimeTree::publish_peer_authority(
    std::string_view public_key,
    const security::PeerAuthoritySnapshot &authority) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer-authority projection requires a 64-character uppercase public key"};
    }
    if (authority.transport_public_key != public_key) {
        return Status{ErrorCode::invalid_argument,
                      "peer-authority projection public key does not match its snapshot"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path peer_directory =
        config_.root / "peers" / std::string(public_key);
    const Status peer_status = validate_or_create_directory(peer_directory, 0700U);
    if (!peer_status.ok()) {
        return peer_status;
    }
    const std::filesystem::path iotox_directory = peer_directory / "iotox";
    const Status iotox_status = validate_or_create_directory(iotox_directory, 0700U);
    if (!iotox_status.ok()) {
        return iotox_status;
    }
    const std::filesystem::path directory = iotox_directory / "authority";
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }

    const std::string summary = render_peer_authority(authority);
    const std::array fields{
        std::pair{directory / "summary", summary},
        std::pair{directory / "verifier-state",
                  security::to_string(authority.verifier_state) + "\n"},
        std::pair{directory / "claimant-state",
                  security::to_string(authority.claimant_state) + "\n"},
        std::pair{directory / "feature-negotiated",
                  std::string(authority.feature_negotiated ? "1\n" : "0\n")},
        std::pair{directory / "authority-v2-negotiated",
                  std::string(authority.authority_v2_negotiated ? "1\n"
                                                                : "0\n")},
        std::pair{directory / "authority-v3-negotiated",
                  std::string(authority.authority_v3_negotiated ? "1\n"
                                                                : "0\n")},
        std::pair{directory / "remote-authorized",
                  std::string(authority.remote_authorized ? "1\n" : "0\n")},
        std::pair{directory / "remote-principal",
                  security::hex(authority.remote_principal) + "\n"},
        std::pair{directory / "remote-role",
                  security::to_string(authority.remote_role) + "\n"},
        std::pair{directory / "remote-capabilities",
                  security::render_capability_set(authority.remote_capabilities) + "\n"},
        std::pair{directory / "remote-capability-mask",
                  std::to_string(authority.remote_capabilities) + "\n"},
        std::pair{directory / "session-transcript-digest",
                  security::hex(authority.session_transcript_digest) + "\n"},
        std::pair{directory / "local-authority-epoch",
                  std::to_string(authority.local_authority_epoch) + "\n"},
        std::pair{directory / "local-authority-sequence",
                  std::to_string(authority.local_authority_sequence) + "\n"},
        std::pair{directory / "local-authority-tail-digest",
                  security::hex(authority.local_authority_tail_digest) + "\n"},
        std::pair{directory / "local-challenge-message-id",
                  std::to_string(authority.local_challenge_message_id) + "\n"},
        std::pair{directory / "challenge-send-attempts",
                  std::to_string(authority.challenge_send_attempts) + "\n"},
        std::pair{directory / "peer-proof-message-id",
                  std::to_string(authority.peer_proof_message_id) + "\n"},
        std::pair{directory / "peer-verifier-device",
                  security::hex(authority.peer_verifier_device) + "\n"},
        std::pair{directory / "peer-authority-epoch",
                  std::to_string(authority.peer_authority_epoch) + "\n"},
        std::pair{directory / "peer-authority-sequence",
                  std::to_string(authority.peer_authority_sequence) + "\n"},
        std::pair{directory / "peer-authority-tail-digest",
                  security::hex(authority.peer_authority_tail_digest) + "\n"},
        std::pair{directory / "peer-challenge-message-id",
                  std::to_string(authority.peer_challenge_message_id) + "\n"},
        std::pair{directory / "local-claimant-principal",
                  security::hex(authority.local_claimant_principal) + "\n"},
        std::pair{directory / "local-proof-message-id",
                  std::to_string(authority.local_proof_message_id) + "\n"},
        std::pair{directory / "proof-send-attempts",
                  std::to_string(authority.proof_send_attempts) + "\n"},
        std::pair{directory / "verifier-detail",
                  authority.verifier_detail + "\n"},
        std::pair{directory / "claimant-detail",
                  authority.claimant_detail + "\n"},
        std::pair{directory / "online-epoch",
                  std::to_string(authority.online_epoch) + "\n"},
    };
    for (const auto &[path, value] : fields) {
        const Status written = write_text(path, value);
        if (!written.ok()) {
            return written;
        }
    }
    // Root `authorization` is the ratox-style commit marker. It is replaced
    // after all detailed fields so readers never mistake a half projection for
    // a newly authorized principal.
    return write_text(peer_directory / "authorization", summary);
}

std::string RuntimeTree::render_peer_description(
    const protocol::PeerDescriptionSnapshot &description) {
    return protocol::render_peer_description(description);
}

Status RuntimeTree::publish_peer_description(
    std::string_view public_key,
    const protocol::PeerDescriptionSnapshot &description) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer-description projection requires a 64-character uppercase public key"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path peer_directory =
        config_.root / "peers" / std::string(public_key);
    const Status peer_status = validate_or_create_directory(peer_directory, 0700U);
    if (!peer_status.ok()) {
        return peer_status;
    }
    const std::filesystem::path iotox_directory = peer_directory / "iotox";
    const Status iotox_status = validate_or_create_directory(iotox_directory, 0700U);
    if (!iotox_status.ok()) {
        return iotox_status;
    }
    const std::filesystem::path directory = iotox_directory / "description";
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }

    const std::string summary = render_peer_description(description);
    std::string device_principal{"\n"};
    std::string product{"\n"};
    std::string version{"\n"};
    std::string revision{"\n"};
    std::string selected_protocol{"\n"};
    std::string supported_features{"\n"};
    std::string offered_operations{"\n"};
    if (description.description) {
        const protocol::DeviceDescription &device = *description.description;
        device_principal = security::hex(device.device_principal) + "\n";
        product = "IoTox\n";
        version = std::to_string(device.version_major) + "." +
                  std::to_string(device.version_minor) + "." +
                  std::to_string(device.version_patch) + "\n";
        std::ostringstream revision_stream;
        revision_stream << "rev" << std::setw(4) << std::setfill('0')
                        << device.revision_number << '\n';
        revision = revision_stream.str();
        selected_protocol =
            std::to_string(device.protocol.major) + "." +
            std::to_string(device.protocol.minor) + "\n";
        supported_features =
            protocol::render_feature_mask(device.supported_features) + "\n";
        offered_operations = "device.describe\n";
    }

    const std::array fields{
        std::pair{directory / "summary", summary},
        std::pair{directory / "friend-number",
                  std::to_string(description.friend_number) + "\n"},
        std::pair{directory / "online-epoch",
                  std::to_string(description.online_epoch) + "\n"},
        std::pair{directory / "state",
                  protocol::to_string(description.state) + "\n"},
        std::pair{directory / "request-message-id",
                  std::to_string(description.request_message_id) + "\n"},
        std::pair{directory / "result-message-id",
                  std::to_string(description.result_message_id) + "\n"},
        std::pair{directory / "outcome",
                  protocol::to_string(description.outcome) + "\n"},
        std::pair{directory / "send-attempts",
                  std::to_string(description.send_attempts) + "\n"},
        std::pair{directory / "last-send-error-code",
                  std::to_string(static_cast<unsigned>(
                      description.last_send_error_code)) + "\n"},
        std::pair{directory / "last-send-error",
                  escape_field(description.last_send_error) + "\n"},
        std::pair{directory / "detail",
                  escape_field(description.detail) + "\n"},
        std::pair{directory / "updated-unix-ms",
                  std::to_string(description.updated_unix_ms) + "\n"},
        std::pair{directory / "device-principal", device_principal},
        std::pair{directory / "product", product},
        std::pair{directory / "version", version},
        std::pair{directory / "revision", revision},
        std::pair{directory / "protocol", selected_protocol},
        std::pair{directory / "supported-features", supported_features},
        std::pair{directory / "offered-operations", offered_operations},
    };
    for (const auto &[path, value] : fields) {
        const Status written = write_text(path, value);
        if (!written.ok()) {
            return written;
        }
    }
    // The peer-root file is the ratox-style commit marker. It is replaced only
    // after every detailed field has reached a self-consistent generation.
    return write_text(peer_directory / "description", summary);
}

Status RuntimeTree::publish_transfers(
    std::span<const FileTransferRecord> transfers) {
    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path transfers_root = config_.root / "transfers";
    const Status root_status = validate_or_create_directory(transfers_root, 0700U);
    if (!root_status.ok()) {
        return root_status;
    }

    std::set<std::string> active;
    for (const FileTransferRecord &transfer : transfers) {
        const std::string entry = to_string(transfer.direction) + "-" +
                                  std::to_string(transfer.friend_number) + "-" +
                                  std::to_string(transfer.file_number);
        active.insert(entry);
        const std::filesystem::path directory = transfers_root / entry;
        struct stat existing {};
        const auto cached = transfer_projection_cache_.find(entry);
        if (cached != transfer_projection_cache_.end() &&
            cached->second == transfer &&
            ::lstat(directory.c_str(), &existing) == 0 &&
            S_ISDIR(existing.st_mode) && !S_ISLNK(existing.st_mode)) {
            continue;
        }

        std::string temporary_template =
            (transfers_root / ".transfer-XXXXXX").string();
        std::vector<char> temporary_buffer(
            temporary_template.begin(), temporary_template.end());
        temporary_buffer.push_back('\0');
        char *created = ::mkdtemp(temporary_buffer.data());
        if (created == nullptr) {
            return path_status(
                "unable to create complete transfer projection", transfers_root);
        }
        const std::filesystem::path temporary_directory{created};
        const auto abandon = [&temporary_directory] {
            std::error_code ignored;
            std::filesystem::remove_all(temporary_directory, ignored);
        };
        if (::chmod(temporary_directory.c_str(), S_IRWXU) != 0) {
            const Status status = path_status(
                "unable to protect transfer projection", temporary_directory);
            abandon();
            return status;
        }

        const std::string file_id = transfer.has_file_id
                                        ? bytes_hex(transfer.file_id)
                                        : std::string("unknown");
        const std::array text_fields{
            std::pair{temporary_directory / "direction",
                      to_string(transfer.direction) + "\n"},
            std::pair{temporary_directory / "state",
                      to_string(transfer.state) + "\n"},
            std::pair{temporary_directory / "friend-number",
                      std::to_string(transfer.friend_number) + "\n"},
            std::pair{temporary_directory / "file-number",
                      std::to_string(transfer.file_number) + "\n"},
            std::pair{temporary_directory / "kind",
                      std::to_string(transfer.file_kind) + "\n"},
            std::pair{temporary_directory / "size",
                      std::to_string(transfer.file_size) + "\n"},
            std::pair{temporary_directory / "position",
                      std::to_string(transfer.position) + "\n"},
            std::pair{temporary_directory / "local-paused",
                      transfer.local_paused ? std::string("1\n")
                                            : std::string("0\n")},
            std::pair{temporary_directory / "peer-paused",
                      transfer.peer_paused ? std::string("1\n")
                                           : std::string("0\n")},
            std::pair{temporary_directory / "file-id", file_id + "\n"},
            std::pair{temporary_directory / "filename-bytes",
                      std::to_string(transfer.filename.size()) + "\n"},
            std::pair{temporary_directory / "local-path",
                      transfer.local_path.empty()
                          ? std::string("\n")
                          : escape_field(transfer.local_path.string()) + "\n"},
            std::pair{temporary_directory / "detail",
                      escape_field(transfer.detail) + "\n"},
        };
        for (const auto &[path, value] : text_fields) {
            const Status written = write_text(path, value);
            if (!written.ok()) {
                abandon();
                return written;
            }
        }
        const Status filename_status =
            write_bytes(temporary_directory / "filename", transfer.filename);
        if (!filename_status.ok()) {
            abandon();
            return filename_status;
        }

        const Status removed = remove_entry(directory);
        if (!removed.ok()) {
            abandon();
            return removed;
        }
        if (::rename(temporary_directory.c_str(), directory.c_str()) != 0) {
            const Status status = path_status(
                "unable to publish complete transfer projection", directory);
            abandon();
            return status;
        }
        transfer_projection_cache_.insert_or_assign(entry, transfer);
    }

    std::error_code iterator_error;
    for (std::filesystem::directory_iterator iterator(transfers_root, iterator_error), end;
         !iterator_error && iterator != end; iterator.increment(iterator_error)) {
        const std::string name = iterator->path().filename().string();
        if (!active.contains(name)) {
            const Status removed = remove_entry(iterator->path());
            if (!removed.ok()) {
                return removed;
            }
        }
    }
    if (iterator_error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate runtime transfers: " +
                          iterator_error.message()};
    }
    std::erase_if(transfer_projection_cache_, [&active](const auto &entry) {
        return !active.contains(entry.first);
    });
    return Status::success();
}

Status RuntimeTree::publish_peer_transfers(
    std::string_view public_key,
    std::span<const FileTransferRecord> transfers) {
    if (!valid_public_key_hex(public_key)) {
        return Status{
            ErrorCode::invalid_argument,
            "peer transfer projection requires an uppercase 64-character public key"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path files_root =
        config_.root / "peers" / std::string(public_key) / "files";
    const std::filesystem::path incoming_root = files_root / "incoming";
    const std::filesystem::path outgoing_root = files_root / "outgoing";
    for (const auto &path : {files_root, incoming_root, outgoing_root}) {
        const Status created = validate_or_create_directory(path, 0700U);
        if (!created.ok()) {
            return created;
        }
    }

    std::set<std::string> active_incoming;
    std::set<std::string> active_outgoing;
    std::set<std::string> active_cache_keys;
    const std::string cache_prefix = std::string(public_key) + "/";
    for (const FileTransferRecord &transfer : transfers) {
        const std::filesystem::path direction_root =
            transfer.direction == FileTransferDirection::incoming
                ? incoming_root
                : outgoing_root;
        std::set<std::string> &active =
            transfer.direction == FileTransferDirection::incoming
                ? active_incoming
                : active_outgoing;
        const std::string entry = std::to_string(transfer.file_number);
        active.insert(entry);
        const std::string cache_key = cache_prefix +
            to_string(transfer.direction) + "/" + entry;
        active_cache_keys.insert(cache_key);
        const std::filesystem::path directory = direction_root / entry;
        struct stat existing {};
        const auto cached = peer_transfer_projection_cache_.find(cache_key);
        if (cached != peer_transfer_projection_cache_.end() &&
            cached->second == transfer &&
            ::lstat(directory.c_str(), &existing) == 0 &&
            S_ISDIR(existing.st_mode) && !S_ISLNK(existing.st_mode)) {
            continue;
        }

        std::string temporary_template =
            (direction_root / ".file-XXXXXX").string();
        std::vector<char> temporary_buffer(
            temporary_template.begin(), temporary_template.end());
        temporary_buffer.push_back('\0');
        char *created = ::mkdtemp(temporary_buffer.data());
        if (created == nullptr) {
            return path_status(
                "unable to create complete peer transfer projection",
                direction_root);
        }
        const std::filesystem::path temporary_directory{created};
        const auto abandon = [&temporary_directory] {
            std::error_code ignored;
            std::filesystem::remove_all(temporary_directory, ignored);
        };
        if (::chmod(temporary_directory.c_str(), S_IRWXU) != 0) {
            const Status status = path_status(
                "unable to protect peer transfer projection",
                temporary_directory);
            abandon();
            return status;
        }

        const std::string file_id = transfer.has_file_id
                                        ? bytes_hex(transfer.file_id)
                                        : std::string("unknown");
        const std::array text_fields{
            std::pair{temporary_directory / "direction",
                      to_string(transfer.direction) + "\n"},
            std::pair{temporary_directory / "state",
                      to_string(transfer.state) + "\n"},
            std::pair{temporary_directory / "friend-number",
                      std::to_string(transfer.friend_number) + "\n"},
            std::pair{temporary_directory / "file-number",
                      std::to_string(transfer.file_number) + "\n"},
            std::pair{temporary_directory / "kind",
                      std::to_string(transfer.file_kind) + "\n"},
            std::pair{temporary_directory / "size",
                      std::to_string(transfer.file_size) + "\n"},
            std::pair{temporary_directory / "position",
                      std::to_string(transfer.position) + "\n"},
            std::pair{temporary_directory / "local-paused",
                      transfer.local_paused ? std::string("1\n")
                                            : std::string("0\n")},
            std::pair{temporary_directory / "peer-paused",
                      transfer.peer_paused ? std::string("1\n")
                                           : std::string("0\n")},
            std::pair{temporary_directory / "file-id", file_id + "\n"},
            std::pair{temporary_directory / "filename-bytes",
                      std::to_string(transfer.filename.size()) + "\n"},
            std::pair{temporary_directory / "local-path",
                      transfer.local_path.empty()
                          ? std::string("\n")
                          : escape_field(transfer.local_path.string()) + "\n"},
            std::pair{temporary_directory / "detail",
                      escape_field(transfer.detail) + "\n"},
        };
        for (const auto &[path, value] : text_fields) {
            const Status written = write_text(path, value);
            if (!written.ok()) {
                abandon();
                return written;
            }
        }
        const Status filename_status =
            write_bytes(temporary_directory / "filename", transfer.filename);
        if (!filename_status.ok()) {
            abandon();
            return filename_status;
        }

        const Status removed = remove_entry(directory);
        if (!removed.ok()) {
            abandon();
            return removed;
        }
        if (::rename(temporary_directory.c_str(), directory.c_str()) != 0) {
            const Status status = path_status(
                "unable to publish complete peer transfer projection",
                directory);
            abandon();
            return status;
        }
        peer_transfer_projection_cache_.insert_or_assign(cache_key, transfer);
    }

    const auto remove_stale = [](const std::filesystem::path &root,
                                 const std::set<std::string> &active) -> Status {
        std::error_code iterator_error;
        for (std::filesystem::directory_iterator iterator(root, iterator_error), end;
             !iterator_error && iterator != end;
             iterator.increment(iterator_error)) {
            const std::string name = iterator->path().filename().string();
            if (!active.contains(name)) {
                const Status removed = remove_entry(iterator->path());
                if (!removed.ok()) {
                    return removed;
                }
            }
        }
        if (iterator_error) {
            return Status{
                ErrorCode::io_error,
                "unable to enumerate peer transfer projections '" +
                    root.string() + "': " + iterator_error.message()};
        }
        return Status::success();
    };

    const Status incoming_removed = remove_stale(incoming_root, active_incoming);
    if (!incoming_removed.ok()) {
        return incoming_removed;
    }
    const Status outgoing_removed = remove_stale(outgoing_root, active_outgoing);
    if (!outgoing_removed.ok()) {
        return outgoing_removed;
    }
    std::erase_if(
        peer_transfer_projection_cache_,
        [&cache_prefix, &active_cache_keys](const auto &entry) {
            return entry.first.starts_with(cache_prefix) &&
                   !active_cache_keys.contains(entry.first);
        });
    return Status::success();
}

Status RuntimeTree::publish_authority(
    const security::AuthoritySnapshot &authority) {
    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path authority_root = config_.root / "authority";
    const std::filesystem::path principals_root = authority_root / "principals";
    for (const auto &path : {authority_root, principals_root}) {
        const Status directory = validate_or_create_directory(path, 0700U);
        if (!directory.ok()) {
            return directory;
        }
    }

    std::size_t active_principals = 0U;
    std::size_t active_owners = 0U;
    for (const security::PrincipalState &principal : authority.principals) {
        if (principal.active) {
            ++active_principals;
            if (principal.role == security::PrincipalRole::owner) {
                ++active_owners;
            }
        }
    }

    for (const auto &[path, value] : {
             std::pair{authority_root / "device-public-key",
                       security::hex(authority.device) + "\n"},
             std::pair{authority_root / "initialized",
                       std::string(authority.initialized ? "1\n" : "0\n")},
             std::pair{authority_root / "ownership-epoch",
                       std::to_string(authority.ownership_epoch) + "\n"},
             std::pair{authority_root / "sequence",
                       std::to_string(authority.sequence) + "\n"},
             std::pair{authority_root / "record-count",
                       std::to_string(authority.record_count) + "\n"},
             std::pair{authority_root / "tail-digest",
                       security::hex(authority.tail_digest) + "\n"},
             std::pair{authority_root / "principal-count",
                       std::to_string(authority.principals.size()) + "\n"},
             std::pair{authority_root / "active-principal-count",
                       std::to_string(active_principals) + "\n"},
             std::pair{authority_root / "active-owner-count",
                       std::to_string(active_owners) + "\n"}}) {
        const Status written = write_text(path, value);
        if (!written.ok()) {
            return written;
        }
    }

    std::set<std::string> present;
    for (const security::PrincipalState &principal : authority.principals) {
        const std::string key = security::hex(principal.public_key);
        present.insert(key);
        const std::filesystem::path directory = principals_root / key;
        const Status directory_status = validate_or_create_directory(directory, 0700U);
        if (!directory_status.ok()) {
            return directory_status;
        }
        for (const auto &[path, value] : {
                 std::pair{directory / "public-key", key + "\n"},
                 std::pair{directory / "active",
                           std::string(principal.active ? "1\n" : "0\n")},
                 std::pair{directory / "role",
                           security::to_string(principal.role) + "\n"},
                 std::pair{directory / "capabilities",
                           security::render_capability_set(principal.capabilities) + "\n"},
                 std::pair{directory / "capability-mask",
                           std::to_string(principal.capabilities) + "\n"},
                 std::pair{directory / "last-sequence",
                           std::to_string(principal.last_sequence) + "\n"}}) {
            const Status written = write_text(path, value);
            if (!written.ok()) {
                return written;
            }
        }
    }

    std::error_code iterator_error;
    for (std::filesystem::directory_iterator iterator(principals_root, iterator_error), end;
         !iterator_error && iterator != end; iterator.increment(iterator_error)) {
        const std::string name = iterator->path().filename().string();
        if (!present.contains(name)) {
            const Status removed = remove_entry(iterator->path());
            if (!removed.ok()) {
                return removed;
            }
        }
    }
    if (iterator_error) {
        return Status{ErrorCode::io_error,
                      "unable to enumerate authority principal projections: " +
                          iterator_error.message()};
    }
    return Status::success();
}

Status RuntimeTree::publish_commands(
    const DurableCommandSnapshot &commands) {
    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path commands_root = config_.root / "commands";
    const Status root_status = validate_or_create_directory(commands_root, 0700U);
    if (!root_status.ok()) {
        return root_status;
    }
    const Status cleared = clear_directory_children(commands_root);
    if (!cleared.ok()) {
        return cleared;
    }
    for (const auto &path : {commands_root / "incoming",
                             commands_root / "outgoing"}) {
        const Status created = validate_or_create_directory(path, 0700U);
        if (!created.ok()) {
            return created;
        }
    }

    std::size_t incoming = 0U;
    std::size_t outgoing = 0U;
    std::size_t unfinished = 0U;
    for (const DurableCommandRecord &record : commands.records) {
        if (record.key.direction == CommandDirection::incoming) {
            ++incoming;
        } else {
            ++outgoing;
        }
        if (command_record_unfinished(record)) {
            ++unfinished;
        }

        const std::string peer = security::hex(record.key.peer_public_key);
        const std::filesystem::path peer_root =
            commands_root /
            (record.key.direction == CommandDirection::incoming
                 ? "incoming"
                 : "outgoing") /
            peer;
        const Status peer_status = validate_or_create_directory(peer_root, 0700U);
        if (!peer_status.ok()) {
            return peer_status;
        }
        const std::string record_name =
            std::to_string(record.key.sender_epoch) + "-" +
            std::to_string(record.key.message_id);
        const std::filesystem::path record_root = peer_root / record_name;
        const Status record_status = validate_or_create_directory(record_root, 0700U);
        if (!record_status.ok()) {
            return record_status;
        }

        for (const auto &[path, value] : {
                 std::pair{record_root / "direction",
                           to_string(record.key.direction) + "\n"},
                 std::pair{record_root / "sender-epoch",
                           std::to_string(record.key.sender_epoch) + "\n"},
                 std::pair{record_root / "message-id",
                           std::to_string(record.key.message_id) + "\n"},
                 std::pair{record_root / "lifecycle",
                           to_string(record.lifecycle) + "\n"},
                 std::pair{record_root / "operation",
                           protocol::to_string(record.operation) + "\n"},
                 std::pair{record_root / "outcome",
                           protocol::to_string(record.outcome) + "\n"},
                 std::pair{record_root / "receipt-delivery",
                           to_string(record.receipt_delivery) + "\n"},
                 std::pair{record_root / "result-delivery",
                           to_string(record.result_delivery) + "\n"},
                 std::pair{record_root / "priority",
                           to_string(record.priority) + "\n"},
                 std::pair{record_root / "clock-requirement",
                           to_string(record.clock_requirement) + "\n"},
                 std::pair{record_root / "expiry-unix-ms",
                           std::to_string(record.expiry_unix_ms) + "\n"},
                 std::pair{record_root / "record",
                           render_command_record(record)}}) {
            const Status written = write_text(path, value);
            if (!written.ok()) {
                return written;
            }
        }
        const Status request_written = write_bytes(
            record_root / "request.frame", record.canonical_request);
        if (!request_written.ok()) {
            return request_written;
        }
        if (!record.canonical_receipt.empty()) {
            const Status receipt_written = write_bytes(
                record_root / "receipt.frame", record.canonical_receipt);
            if (!receipt_written.ok()) {
                return receipt_written;
            }
        }
        if (!record.canonical_result.empty()) {
            const Status result_written = write_bytes(
                record_root / "result.frame", record.canonical_result);
            if (!result_written.ok()) {
                return result_written;
            }
            auto frame = protocol::decode(record.canonical_result);
            if (!frame || frame.value().type !=
                              protocol::MessageType::command_result) {
                return Status{ErrorCode::protocol_error,
                              "durable result projection contains an invalid frame"};
            }
            auto result = protocol::decode_command_result(
                frame.value().payload);
            if (!result) {
                return Status{result.status().code(),
                              "durable result projection contains an invalid payload: " +
                                  result.status().message()};
            }
            std::string rendered =
                "operation=" + protocol::to_string(result.value().operation) +
                "\noutcome=" + protocol::to_string(result.value().outcome) +
                "\n";
            if (result.value().outcome ==
                    protocol::CommandOutcome::succeeded &&
                result.value().operation ==
                    protocol::CommandOperation::device_describe) {
                auto description = protocol::decode_device_description(
                    result.value().body);
                if (!description) {
                    return description.status();
                }
                rendered += protocol::render_device_description(
                    description.value());
            } else if (result.value().outcome ==
                           protocol::CommandOutcome::succeeded &&
                       result.value().operation ==
                           protocol::CommandOperation::system_summary) {
                auto summary = protocol::decode_system_summary(
                    result.value().body);
                if (!summary) {
                    return summary.status();
                }
                rendered += protocol::render_system_summary(summary.value());
            } else if (result.value().outcome ==
                           protocol::CommandOutcome::succeeded &&
                       result.value().operation ==
                           protocol::CommandOperation::profile_status_set) {
                auto evidence = protocol::decode_profile_status_evidence(
                    result.value().body);
                if (!evidence) {
                    return evidence.status();
                }
                rendered += protocol::render_profile_status_evidence(
                    evidence.value());
            }
            const Status rendered_written = write_text(
                record_root / "result", rendered);
            if (!rendered_written.ok()) {
                return rendered_written;
            }
        }
    }

    // `summary` is the projection's commit marker. Readers that observe it
    // know every record and exact canonical frame for that generation has
    // already been written. The signed command store remains authoritative;
    // this tree is a disposable ratox-style view.
    std::ostringstream summary;
    summary << "format=IoTox-Durable-Commands-v3\n"
            << "generation=" << commands.generation << '\n'
            << "local-sender-epoch=" << commands.local_sender_epoch << '\n'
            << "clock-high-water-unix-ms="
            << commands.clock_high_water_unix_ms << '\n'
            << "record-count=" << commands.records.size() << '\n'
            << "incoming-count=" << incoming << '\n'
            << "outgoing-count=" << outgoing << '\n'
            << "unfinished-count=" << unfinished << '\n';
    return write_text(commands_root / "summary", summary.str());
}

Status RuntimeTree::publish_friend_request(
    const TransportEvent &event, std::uint64_t received_unix_ms) {
    if (event.kind != TransportEventKind::friend_request ||
        event.public_key.size() != toxcore::abi::kPublicKeySize ||
        event.data.size() > toxcore::abi::kMaxFriendRequestLength) {
        return Status{ErrorCode::invalid_argument,
                      "friend-request projection requires a 32-byte key and bounded request body"};
    }
    std::scoped_lock lock(surface_mutex_);
    const std::string key = bytes_hex(event.public_key);
    const std::filesystem::path requests_root = config_.root / "requests";
    std::string temporary_template =
        (requests_root / ".incoming-XXXXXX").string();
    std::vector<char> temporary_buffer(
        temporary_template.begin(), temporary_template.end());
    temporary_buffer.push_back('\0');
    char *created = ::mkdtemp(temporary_buffer.data());
    if (created == nullptr) {
        return path_status(
            "unable to create complete incoming-request projection",
            requests_root);
    }
    const std::filesystem::path temporary_directory{created};
    const auto abandon = [&temporary_directory] {
        std::error_code ignored;
        std::filesystem::remove_all(temporary_directory, ignored);
    };
    if (::chmod(temporary_directory.c_str(), S_IRWXU) != 0) {
        const Status status = path_status(
            "unable to protect incoming-request projection",
            temporary_directory);
        abandon();
        return status;
    }

    const Status key_status =
        write_text(temporary_directory / "public-key", key + "\n");
    if (!key_status.ok()) {
        abandon();
        return key_status;
    }
    const Status message_status =
        write_bytes(temporary_directory / "message", event.data);
    if (!message_status.ok()) {
        abandon();
        return message_status;
    }
    const Status size_status = write_text(
        temporary_directory / "message-bytes",
        std::to_string(event.data.size()) + "\n");
    if (!size_status.ok()) {
        abandon();
        return size_status;
    }
    const Status received_status = write_text(
        temporary_directory / "received-unix-ms",
        std::to_string(received_unix_ms) + "\n");
    if (!received_status.ok()) {
        abandon();
        return received_status;
    }
    const Status request_help = write_text(
        temporary_directory / "request.help",
        "IoTox ratox-successor incoming friend request v1\n"
        "accept=write exactly accept followed by LF in one atomic write(2)\n"
        "reject=write exactly reject followed by LF in one atomic write(2)\n"
        "maximum-record-bytes=6 excluding LF\n"
        "FIFO write success means only that the kernel accepted bytes\n"
        "accept calls tox_friend_add_norequest for this public key\n"
        "reject withdraws IoTox's live request record; c-toxcore has no pending-request store to mutate\n"
        "accepting Tox friendship grants no IoTox role, capability, ownership, or recovery authority\n"
        "friend-events at the runtime root records the attempted decision and its result\n");
    if (!request_help.ok()) {
        abandon();
        return request_help;
    }
    for (const auto &path : {temporary_directory / "accept",
                             temporary_directory / "reject"}) {
        const Status fifo = validate_or_create_fifo(path, 0600U);
        if (!fifo.ok()) {
            abandon();
            return fifo;
        }
    }

    const std::filesystem::path directory = requests_root / key;
    const Status removed = remove_entry(directory);
    if (!removed.ok()) {
        abandon();
        return removed;
    }
    if (::rename(temporary_directory.c_str(), directory.c_str()) != 0) {
        const Status status = path_status(
            "unable to publish complete incoming-request projection",
            directory);
        abandon();
        return status;
    }
    return Status::success();
}

Status RuntimeTree::remove_friend_request(std::span<const std::uint8_t> public_key) {
    if (public_key.size() != toxcore::abi::kPublicKeySize) {
        return Status{ErrorCode::invalid_argument,
                      "friend-request removal requires a 32-byte public key"};
    }
    std::scoped_lock lock(surface_mutex_);
    return remove_entry(config_.root / "requests" / bytes_hex(public_key));
}

std::string RuntimeTree::render_event(const TransportEvent &event) {
    std::ostringstream output;
    output << "kind=" << to_string(event.kind)
           << " friend=" << event.friend_number
           << " connection=" << event.connection_status
           << " public-key=" << bytes_hex(event.public_key)
           << " payload-bytes=" << event.data.size()
           << " text-kind=" << to_string(event.text_kind)
           << " message-id=" << event.message_id
           << " presence=" << to_string(event.presence_status)
           << " typing=" << (event.typing ? 1 : 0)
           << " file-number=" << event.file_number
           << " file-kind=" << event.file_kind
           << " file-size=" << event.file_size
           << " file-position=" << event.file_position
           << " requested-length=" << event.requested_length
           << " chunk-source-attempted="
           << (event.file_chunk_source_attempted ? 1 : 0)
           << " chunk-sent-inline="
           << (event.file_chunk_sent_inline ? 1 : 0)
           << " chunk-status-code="
           << static_cast<unsigned int>(event.file_chunk_status.code())
           << " file-control=" << to_string(event.file_control)
           << " file-id="
           << (event.has_file_id ? bytes_hex(event.file_id) : std::string("unknown"))
           << " filename="
           << escape_field(std::string(event.filename.begin(), event.filename.end()))
           << " dropped-events-before=" << event.dropped_events_before
           << " message=" << escape_field(event.message)
           << '\n';
    return output.str();
}

std::string RuntimeTree::render_friend_lifecycle(
    const FriendLifecycleEvent &event) {
    std::ostringstream output;
    output << "unix-ms=" << event.unix_ms
           << " sequence=" << event.sequence
           << " source=" << escape_field(event.source)
           << " operation=" << escape_field(event.operation)
           << " public-key="
           << (event.has_public_key ? escape_field(event.public_key)
                                    : std::string("unknown"))
           << " disposition=" << escape_field(event.disposition)
           << " error-code=" << static_cast<unsigned int>(event.error_code)
           << " friend-number=";
    if (event.has_friend_number) {
        output << event.friend_number;
    } else {
        output << "unassigned";
    }
    output << " detail=" << escape_field(event.detail) << '\n';
    return output.str();
}

std::string RuntimeTree::render_ratox_event(
    const interactive::RatoxServiceEvent &event) {
    const auto milliseconds =
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch());
    std::ostringstream output;
    output << "unix-ms=" << milliseconds.count()
           << " ordinal=" << event.ordinal
           << " steady-us=" << event.steady_time_us
           << " kind=" << interactive::to_string(event.kind)
           << " error-code=" << static_cast<unsigned int>(event.error_code)
           << " friend-number=" << event.friend_number
           << " online-epoch=" << event.online_epoch
           << " session-id=" << bytes_hex(event.session_id)
           << " principal-id=" << bytes_hex(event.principal_id)
           << " frame-type=" << protocol::ratox::to_string(event.frame_type)
           << " incarnation=" << event.incarnation
           << " generation=" << event.generation
           << " message-id=" << event.message_id
           << " sequence=" << event.sequence
           << " next-sequence=" << event.next_sequence
           << " event-bytes=" << event.event_bytes
           << " next-input-sequence=" << event.next_input_sequence
           << " output-base-sequence=" << event.output_base_sequence
           << " output-next-sequence=" << event.output_next_sequence << '\n';
    return output.str();
}

std::string RuntimeTree::render_peer_message(const TransportEvent &event) {
    std::string_view direction;
    std::string_view message_id;
    switch (event.kind) {
        case TransportEventKind::message_sent:
            direction = "outgoing";
            message_id = "assigned";
            break;
        case TransportEventKind::friend_message:
            direction = "incoming";
            message_id = "unavailable";
            break;
        case TransportEventKind::friend_read_receipt:
            direction = "receipt";
            message_id = "assigned";
            break;
        default:
            return {};
    }

    const auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch());
    std::ostringstream output;
    output << "unix-ms=" << milliseconds.count()
           << " direction=" << direction
           << " kind=" << to_string(event.text_kind)
           << " message-id=";
    if (message_id == "assigned") {
        output << event.message_id;
    } else {
        output << message_id;
    }
    output << " payload-bytes=" << event.data.size()
           << " body="
           << escape_field(std::string(event.data.begin(), event.data.end()))
           << " note=" << escape_field(event.message) << '\n';
    return output.str();
}

std::string RuntimeTree::render_peer_protocol(
    std::string_view direction, const protocol::Frame &frame) {
    if (direction != "incoming" && direction != "outgoing") {
        return {};
    }
    const auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch());
    std::ostringstream output;
    output << "unix-ms=" << milliseconds.count()
           << " direction=" << direction
           << " protocol=" << static_cast<unsigned int>(frame.major) << '.'
           << static_cast<unsigned int>(frame.minor)
           << " type=" << protocol::to_string(frame.type)
           << " flags=" << static_cast<unsigned int>(frame.flags)
           << " message-id=" << frame.message_id
           << " correlation-id=" << frame.correlation_id
           << " sequence=" << frame.sequence
           << " expiry-unix-ms=" << frame.expiry_unix_ms
           << " payload-bytes=" << frame.payload.size()
           << " payload="
           << escape_field(std::string(frame.payload.begin(), frame.payload.end()))
           << '\n';
    return output.str();
}


std::string RuntimeTree::render_peer_command_event(
    const PeerCommandEvent &event) {
    std::ostringstream output;
    output << "unix-ms=" << event.unix_ms
           << " ingress-sequence=" << event.ingress_sequence
           << " operation=" << escape_field(event.operation)
           << " disposition=" << escape_field(event.disposition)
           << " error-code=" << static_cast<unsigned int>(event.error_code)
           << " sender-epoch=" << event.sender_epoch
           << " message-id=" << event.message_id
           << " state=" << escape_field(event.state)
           << " detail=" << escape_field(event.detail)
           << '\n';
    return output.str();
}

std::string RuntimeTree::render_peer_message_ingress(
    const PeerMessageIngressEvent &event) {
    std::ostringstream output;
    output << "unix-ms=" << event.unix_ms
           << " ingress-sequence=" << event.ingress_sequence
           << " kind=" << to_string(event.kind)
           << " disposition=" << escape_field(event.disposition)
           << " error-code=" << static_cast<unsigned int>(event.error_code)
           << " message-id=";
    if (event.has_message_id) {
        output << event.message_id;
    } else {
        output << "unassigned";
    }
    output << " payload-bytes=" << event.body.size()
           << " body="
           << escape_field(std::string(event.body.begin(), event.body.end()))
           << " detail=" << escape_field(event.detail)
           << '\n';
    return output.str();
}

std::string RuntimeTree::render_peer_file_ingress(
    const PeerFileIngressEvent &event) {
    std::ostringstream output;
    output << "unix-ms=" << event.unix_ms
           << " source=local-fifo"
           << " ingress-sequence=" << event.ingress_sequence
           << " operation=" << escape_field(event.operation)
           << " disposition=" << escape_field(event.disposition)
           << " error-code=" << static_cast<unsigned int>(event.error_code)
           << " file-number=";
    if (event.has_transfer) {
        output << event.transfer.file_number;
    } else if (event.has_file_number) {
        output << event.file_number;
    } else {
        output << "unassigned";
    }
    output << " direction="
           << (event.has_transfer
                   ? to_string(event.transfer.direction)
                   : std::string("unknown"))
           << " state="
           << (event.has_transfer
                   ? to_string(event.transfer.state)
                   : std::string("not-admitted"))
           << " size="
           << (event.has_transfer ? event.transfer.file_size : 0U)
           << " position="
           << (event.has_transfer ? event.transfer.position : 0U)
           << " local-paused="
           << (event.has_transfer && event.transfer.local_paused ? 1 : 0)
           << " peer-paused="
           << (event.has_transfer && event.transfer.peer_paused ? 1 : 0)
           << " local-path=" << escape_field(event.local_path.string())
           << " detail=" << escape_field(event.detail)
           << '\n';
    return output.str();
}

std::string RuntimeTree::render_peer_file_transport(
    const PeerFileTransportEvent &event) {
    const TransportEvent &transport = event.event;
    std::ostringstream output;
    output << "unix-ms=" << event.unix_ms
           << " source=toxcore"
           << " event=" << to_string(transport.kind)
           << " disposition="
           << (event.manager_status.ok() ? "applied" : "rejected")
           << " error-code="
           << static_cast<unsigned int>(event.manager_status.code())
           << " friend-number=" << transport.friend_number
           << " file-number=" << transport.file_number
           << " file-kind=" << transport.file_kind
           << " file-size=" << transport.file_size
           << " file-position=" << transport.file_position
           << " requested-length=" << transport.requested_length
           << " payload-bytes=" << transport.data.size()
           << " chunk-source-attempted="
           << (transport.file_chunk_source_attempted ? 1 : 0)
           << " chunk-sent-inline="
           << (transport.file_chunk_sent_inline ? 1 : 0)
           << " chunk-status-code="
           << static_cast<unsigned int>(transport.file_chunk_status.code())
           << " file-control=" << to_string(transport.file_control)
           << " file-id="
           << (transport.has_file_id
                   ? bytes_hex(transport.file_id)
                   : std::string("unknown"))
           << " filename="
           << escape_field(std::string(
                  transport.filename.begin(), transport.filename.end()))
           << " state="
           << (event.has_transfer
                   ? to_string(event.transfer.state)
                   : std::string("not-live"))
           << " direction="
           << (event.has_transfer
                   ? to_string(event.transfer.direction)
                   : std::string("unknown"))
           << " local-paused="
           << (event.has_transfer && event.transfer.local_paused ? 1 : 0)
           << " peer-paused="
           << (event.has_transfer && event.transfer.peer_paused ? 1 : 0)
           << " local-path="
           << (event.has_transfer
                   ? escape_field(event.transfer.local_path.string())
                   : std::string())
           << " detail="
           << escape_field(
                  event.manager_status.ok()
                      ? transport.message
                      : event.manager_status.message())
           << '\n';
    return output.str();
}

Status RuntimeTree::rotate_events_if_needed(std::size_t incoming_bytes) {
    const std::filesystem::path current = event_path();
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect runtime event journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "runtime event journal is not a regular file: " + current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.event_rotation_bytes) {
        return Status::success();
    }

    const std::filesystem::path previous = config_.root / "events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous runtime event journal", previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate runtime event journal", current);
    }
    return Status::success();
}

Status RuntimeTree::append_event(const TransportEvent &event) {
    const std::string line = render_event(event);
    std::scoped_lock lock(event_mutex_);
    const Status rotated = rotate_events_if_needed(line.size());
    if (!rotated.ok()) {
        return rotated;
    }

    const std::filesystem::path path = event_path();
    const int descriptor = ::open(path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
                                  S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open runtime event journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status("unable to enforce runtime event journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close runtime event journal", path);
    }
    return status;
}

Status RuntimeTree::rotate_friend_events_if_needed(
    std::size_t incoming_bytes) {
    const std::filesystem::path current = friend_event_path();
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect friendship journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "friendship journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.friendship_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous =
        config_.root / "friend-events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous friendship journal",
                           previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate friendship journal", current);
    }
    return Status::success();
}

Status RuntimeTree::append_friend_lifecycle(
    const FriendLifecycleEvent &event) {
    const bool public_key_valid =
        event.has_public_key ? valid_public_key_hex(event.public_key)
                             : event.public_key.empty();
    if (event.unix_ms == 0U || event.sequence == 0U ||
        event.source.empty() || event.operation.empty() ||
        !public_key_valid || event.disposition.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "friendship event requires time, sequence, source, operation, disposition, and either one uppercase public key or an explicit keyless state"};
    }
    const std::string line = render_friend_lifecycle(event);
    std::scoped_lock lock(friend_event_mutex_);
    const Status rotated = rotate_friend_events_if_needed(line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = friend_event_path();
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open friendship journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status(
            "unable to enforce friendship journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close friendship journal", path);
    }
    return status;
}

Status RuntimeTree::rotate_ratox_events_if_needed(
    std::size_t incoming_bytes) {
    const std::filesystem::path current = ratox_event_path();
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect Ratox lifecycle journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "Ratox lifecycle journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.ratox_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous =
        config_.root / "ratox-events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status(
            "unable to remove previous Ratox lifecycle journal", previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate Ratox lifecycle journal", current);
    }
    return Status::success();
}

Status RuntimeTree::append_ratox_event(
    const interactive::RatoxServiceEvent &event) {
    if (event.ordinal == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox lifecycle event requires a nonzero ordinal"};
    }
    const std::string line = render_ratox_event(event);
    std::scoped_lock lock(ratox_event_mutex_);
    const Status rotated = rotate_ratox_events_if_needed(line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = ratox_event_path();
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open Ratox lifecycle journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status(
            "unable to enforce Ratox lifecycle journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close Ratox lifecycle journal", path);
    }
    return status;
}

Status RuntimeTree::rotate_peer_messages_if_needed(
    const std::filesystem::path &directory, std::size_t incoming_bytes) {
    const std::filesystem::path current = directory / "messages";
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect peer message journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "peer message journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.message_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous = directory / "messages.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous peer message journal", previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate peer message journal", current);
    }
    return Status::success();
}

Status RuntimeTree::rotate_peer_protocol_if_needed(
    const std::filesystem::path &directory, std::size_t incoming_bytes) {
    const std::filesystem::path current = directory / "protocol";
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect peer protocol journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "peer protocol journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.protocol_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous = directory / "protocol.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous peer protocol journal", previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate peer protocol journal", current);
    }
    return Status::success();
}


Status RuntimeTree::rotate_peer_commands_if_needed(
    const std::filesystem::path &directory, std::size_t incoming_bytes) {
    const std::filesystem::path current = directory / "command-events";
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect peer command journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "peer command journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.command_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous =
        directory / "command-events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous peer command journal",
                           previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate peer command journal", current);
    }
    return Status::success();
}

Status RuntimeTree::rotate_peer_message_ingress_if_needed(
    const std::filesystem::path &directory, std::size_t incoming_bytes) {
    const std::filesystem::path current = directory / "message-events";
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect peer message ingress journal",
                           current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "peer message ingress journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.message_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous =
        directory / "message-events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status(
            "unable to remove previous peer message ingress journal",
            previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate peer message ingress journal",
                           current);
    }
    return Status::success();
}

Status RuntimeTree::rotate_peer_files_if_needed(
    const std::filesystem::path &directory, std::size_t incoming_bytes) {
    const std::filesystem::path current = directory / "file-events";
    struct stat metadata {};
    if (::lstat(current.c_str(), &metadata) != 0) {
        if (errno == ENOENT) {
            return Status::success();
        }
        return path_status("unable to inspect peer file journal", current);
    }
    if (!S_ISREG(metadata.st_mode) || S_ISLNK(metadata.st_mode)) {
        return Status{ErrorCode::io_error,
                      "peer file journal is not a regular file: " +
                          current.string()};
    }
    const auto current_size = static_cast<std::uintmax_t>(metadata.st_size);
    if (current_size + incoming_bytes <= config_.file_rotation_bytes) {
        return Status::success();
    }
    const std::filesystem::path previous = directory / "file-events.previous";
    if (::unlink(previous.c_str()) != 0 && errno != ENOENT) {
        return path_status("unable to remove previous peer file journal",
                           previous);
    }
    if (::rename(current.c_str(), previous.c_str()) != 0) {
        return path_status("unable to rotate peer file journal", current);
    }
    return Status::success();
}

Status RuntimeTree::append_peer_message(
    std::string_view public_key, const TransportEvent &event) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer message journal requires an uppercase 64-character public key"};
    }
    const std::string line = render_peer_message(event);
    if (line.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "peer message journal accepts only text-message and receipt events"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated = rotate_peer_messages_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "messages";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer message journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status("unable to enforce peer message journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer message journal", path);
    }
    return status;
}

Status RuntimeTree::append_peer_protocol(
    std::string_view public_key, std::string_view direction,
    const protocol::Frame &frame) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer protocol journal requires an uppercase 64-character public key"};
    }
    const std::string line = render_peer_protocol(direction, frame);
    if (line.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "peer protocol journal direction must be incoming or outgoing"};
    }

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated = rotate_peer_protocol_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "protocol";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer protocol journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status("unable to enforce peer protocol journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer protocol journal", path);
    }
    return status;
}

Status RuntimeTree::append_peer_command_event(
    std::string_view public_key, const PeerCommandEvent &event) {
    if (!valid_public_key_hex(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer command journal requires an uppercase 64-character public key"};
    }
    if (event.ingress_sequence == 0U || event.disposition.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "peer command event requires an ingress sequence and disposition"};
    }
    const std::string line = render_peer_command_event(event);

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status = validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated =
        rotate_peer_commands_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "command-events";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer command journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status("unable to enforce peer command journal permissions",
                             path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer command journal", path);
    }
    return status;
}

Status RuntimeTree::append_peer_message_ingress(
    std::string_view public_key, const PeerMessageIngressEvent &event) {
    if (!valid_public_key_hex(public_key)) {
        return Status{
            ErrorCode::invalid_argument,
            "peer message ingress journal requires an uppercase 64-character public key"};
    }
    if (event.ingress_sequence == 0U || event.disposition.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "peer message ingress event requires an ingress sequence and disposition"};
    }
    const std::string line = render_peer_message_ingress(event);

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status =
        validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated =
        rotate_peer_message_ingress_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "message-events";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer message ingress journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status(
            "unable to enforce peer message ingress journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer message ingress journal", path);
    }
    return status;
}

Status RuntimeTree::append_peer_file_ingress(
    std::string_view public_key, const PeerFileIngressEvent &event) {
    if (!valid_public_key_hex(public_key)) {
        return Status{
            ErrorCode::invalid_argument,
            "peer file ingress journal requires an uppercase 64-character public key"};
    }
    if (event.ingress_sequence == 0U || event.operation.empty() ||
        event.disposition.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "peer file ingress event requires a sequence, operation, and disposition"};
    }
    const std::string line = render_peer_file_ingress(event);

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status =
        validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated = rotate_peer_files_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "file-events";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer file journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status(
            "unable to enforce peer file journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer file journal", path);
    }
    return status;
}

Status RuntimeTree::append_peer_file_transport(
    std::string_view public_key, const PeerFileTransportEvent &event) {
    if (!valid_public_key_hex(public_key)) {
        return Status{
            ErrorCode::invalid_argument,
            "peer file transport journal requires an uppercase 64-character public key"};
    }
    switch (event.event.kind) {
        case TransportEventKind::file_offer:
        case TransportEventKind::file_control:
        case TransportEventKind::file_chunk_request:
        case TransportEventKind::file_chunk:
            break;
        default:
            return Status{
                ErrorCode::invalid_argument,
                "peer file transport journal accepts only toxcore file events"};
    }
    const std::string line = render_peer_file_transport(event);

    std::scoped_lock lock(surface_mutex_);
    const std::filesystem::path directory =
        config_.root / "peers" / std::string(public_key);
    const Status directory_status =
        validate_or_create_directory(directory, 0700U);
    if (!directory_status.ok()) {
        return directory_status;
    }
    const Status rotated = rotate_peer_files_if_needed(directory, line.size());
    if (!rotated.ok()) {
        return rotated;
    }
    const std::filesystem::path path = directory / "file-events";
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC | O_NOFOLLOW,
        S_IRUSR | S_IWUSR);
    if (descriptor < 0) {
        return path_status("unable to open peer file journal", path);
    }
    Status status = Status::success();
    if (::fchmod(descriptor, S_IRUSR | S_IWUSR) != 0) {
        status = path_status(
            "unable to enforce peer file journal permissions", path);
    }
    if (status.ok()) {
        status = append_all(descriptor, line, path);
    }
    if (::close(descriptor) != 0 && status.ok()) {
        status = path_status("unable to close peer file journal", path);
    }
    return status;
}

const std::filesystem::path &RuntimeTree::root() const noexcept { return config_.root; }
std::filesystem::path RuntimeTree::socket_path() const { return config_.root / "control.sock"; }
std::filesystem::path RuntimeTree::event_path() const { return config_.root / "events"; }
std::filesystem::path RuntimeTree::friend_event_path() const {
    return config_.root / "friend-events";
}
std::filesystem::path RuntimeTree::ratox_event_path() const {
    return config_.root / "ratox-events";
}

std::filesystem::path default_runtime_root() {
    if (const char *override_path = std::getenv("IOTOX_RUNTIME_DIR");
        override_path != nullptr && override_path[0] != '\0') {
        return override_path;
    }
    if (const char *xdg_runtime = std::getenv("XDG_RUNTIME_DIR");
        xdg_runtime != nullptr && xdg_runtime[0] != '\0') {
        return std::filesystem::path{xdg_runtime} / "iotox";
    }
    return std::filesystem::path{"/tmp"} /
           ("iotox-" + std::to_string(static_cast<unsigned long long>(::geteuid())));
}

std::filesystem::path default_state_path() {
    return default_state_path(ToxRoute::native);
}

std::filesystem::path default_state_path(ToxRoute route) {
    if (const char *override_path = std::getenv("IOTOX_STATE_PATH");
        override_path != nullptr && override_path[0] != '\0') {
        return override_path;
    }
    std::string filename = "device.toxsave";
    if (route == ToxRoute::tor) {
        filename = "device.tox-tor.toxsave";
    } else if (route == ToxRoute::i2p ||
               route == ToxRoute::i2p_construction) {
        filename = "device.tox-i2p.toxsave";
    }
    if (const char *xdg_state = std::getenv("XDG_STATE_HOME");
        xdg_state != nullptr && xdg_state[0] != '\0') {
        return std::filesystem::path{xdg_state} / "iotox" / filename;
    }
    return home_directory() / ".local" / "state" / "iotox" / filename;
}

}  // namespace iotox::local
