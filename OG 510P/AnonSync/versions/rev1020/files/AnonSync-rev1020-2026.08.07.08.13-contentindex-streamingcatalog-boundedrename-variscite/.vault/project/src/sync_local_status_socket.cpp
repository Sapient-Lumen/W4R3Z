#include "sync_local_status_socket.hpp"

#if !defined(_WIN32)

#include "anonsync_json_parser.hpp"
#include "sha256_digest.hpp"
#include "sync_directory_authority.hpp"
#include "sync_linux_process_resources.hpp"

#include <array>
#include <charconv>
#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <condition_variable>
#include <filesystem>
#include <limits>
#include <mutex>
#include <optional>
#include <poll.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

#include <fcntl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

constexpr std::string_view kStatusRequest = "status\n";
constexpr std::string_view kResourcesRequest = "resources\n";
constexpr std::string_view kStopRequest = "stop\n";
constexpr std::string_view kRecheckRequest = "recheck\n";
constexpr std::string_view kQuarantineRequestPrefix = "quarantine ";
constexpr std::string_view kQuarantineReleaseRequestPrefix =
    "quarantine-release ";
constexpr std::string_view kHistoricalVersionsRequest = "versions\n";
constexpr std::string_view kHistoricalVersionsQueryRequestPrefix =
    "versions-query ";
constexpr std::string_view kRetentionPlanRequestPrefix = "retention-plan ";
constexpr std::string_view kHistoricalVersionRestoreRequestPrefix =
    "restore ";
constexpr std::string_view kHistoricalVersionRestoreExactRequestPrefix =
    "restore-exact ";
constexpr std::string_view kHistoricalVersionPinRequestPrefix =
    "version-pin ";
constexpr std::string_view kHistoricalVersionUnpinRequestPrefix =
    "version-unpin ";
constexpr std::string_view kStopResponseSchema =
    "anonsync.local-stop.response.v1";
constexpr std::string_view kRecheckResponseSchema =
    "anonsync.local-recheck.response.v1";
constexpr std::string_view kQuarantineResponseSchema =
    "anonsync.local-quarantine.response.v1";
constexpr std::string_view kQuarantineReleaseResponseSchema =
    "anonsync.local-quarantine-release.response.v1";
constexpr std::string_view kHistoricalVersionsResponseSchema =
    "anonsync.local-historical-versions.response.v5";
constexpr std::string_view kHistoricalVersionRestoreResponseSchema =
    "anonsync.local-historical-version-restore.response.v1";
constexpr std::string_view kHistoricalVersionRestoreExactResponseSchema =
    "anonsync.local-historical-version-restore.response.v2";
constexpr std::string_view kHistoricalVersionPinResponseSchema =
    "anonsync.local-historical-version-pin.response.v1";
constexpr std::string_view kHistoricalVersionUnpinResponseSchema =
    "anonsync.local-historical-version-unpin.response.v1";
constexpr std::string_view kRetentionPlanResponseSchema =
    "anonsync.local-retention-plan.response.v6";
constexpr std::string_view kUnsupportedResponse =
    "{\"schema\":\"anonsync.local-status.response.v1\","
    "\"ok\":false,\"error\":\"unsupported_request\"}";
// A canonical 4,096-byte relative path expands to 8,192 lowercase hex bytes
// in the strict line protocol. Keep the total request independently bounded
// while preserving arbitrary non-NUL POSIX pathname bytes.
constexpr std::size_t kMaximumRequestBytes = 16U * 1024U;
constexpr std::uint64_t kServerClientTimeoutMilliseconds = 1000U;

struct SocketPathIdentity final {
    dev_t device = 0;
    ino_t inode = 0;
    uid_t owner = 0;
};

struct LocalPeerCredentials final {
    std::optional<pid_t> process_id;
};

struct LocalSocketResponse final {
    std::string json;
    LocalPeerCredentials peer;
};

enum class LocalSocketCompletionPathPolicy : std::uint8_t {
    RequireSameIdentity,
    AllowExactAbsenceAfterResponse,
};

[[nodiscard]] std::string system_error_text(int error) {
    return std::strerror(error);
}

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    constexpr char hex[] = "0123456789abcdef";
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << hex[byte >> 4U]
                           << hex[byte & 0x0fU];
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

[[nodiscard]] std::string lowercase_hex_encode(std::string_view bytes) {
    constexpr std::string_view hex = "0123456789abcdef";
    std::string encoded;
    encoded.reserve(bytes.size() * 2U);
    for (const unsigned char byte : bytes) {
        encoded.push_back(hex[byte >> 4U]);
        encoded.push_back(hex[byte & 0x0fU]);
    }
    return encoded;
}

[[nodiscard]] std::optional<std::string> lowercase_hex_decode(
    std::string_view encoded) {
    if (encoded.empty() || (encoded.size() & 1U) != 0U) {
        return std::nullopt;
    }
    const auto nibble = [](char value) -> std::optional<unsigned char> {
        if (value >= '0' && value <= '9') {
            return static_cast<unsigned char>(value - '0');
        }
        if (value >= 'a' && value <= 'f') {
            return static_cast<unsigned char>(value - 'a' + 10);
        }
        return std::nullopt;
    };
    std::string decoded;
    decoded.reserve(encoded.size() / 2U);
    for (std::size_t offset = 0U; offset < encoded.size(); offset += 2U) {
        const std::optional<unsigned char> high = nibble(encoded[offset]);
        const std::optional<unsigned char> low = nibble(encoded[offset + 1U]);
        if (!high.has_value() || !low.has_value()) return std::nullopt;
        decoded.push_back(static_cast<char>((*high << 4U) | *low));
    }
    return decoded;
}

[[nodiscard]] std::optional<std::uint64_t> parse_decimal_uint64(
    std::string_view text) {
    if (text.empty()) return std::nullopt;
    std::uint64_t value = 0U;
    const char* const begin = text.data();
    const char* const end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end) {
        return std::nullopt;
    }
    return value;
}

[[nodiscard]] std::optional<SyncLocalStatusSocketPayloadQuarantineRequest>
parse_payload_quarantine_request(std::string_view request) {
    constexpr std::size_t kDigestCharacters = 64U;
    SyncLocalStatusSocketPayloadQuarantineOperation operation;
    std::string_view prefix;
    if (request.starts_with(kQuarantineRequestPrefix)) {
        operation = SyncLocalStatusSocketPayloadQuarantineOperation::Preserve;
        prefix = kQuarantineRequestPrefix;
    } else if (request.starts_with(kQuarantineReleaseRequestPrefix)) {
        operation = SyncLocalStatusSocketPayloadQuarantineOperation::Release;
        prefix = kQuarantineReleaseRequestPrefix;
    } else {
        return std::nullopt;
    }
    const std::size_t exact_bytes =
        prefix.size() + kDigestCharacters + 1U + kDigestCharacters + 1U;
    if (request.size() != exact_bytes || request.back() != '\n') {
        return std::nullopt;
    }
    request.remove_prefix(prefix.size());
    request.remove_suffix(1U);
    if (request.size() != kDigestCharacters * 2U + 1U ||
        request[kDigestCharacters] != ' ') {
        return std::nullopt;
    }
    const std::string_view expected = request.substr(0U, kDigestCharacters);
    const std::string_view observed = request.substr(kDigestCharacters + 1U);
    if (!is_lowercase_sha256_hex(expected) ||
        !is_lowercase_sha256_hex(observed) || expected == observed) {
        return std::nullopt;
    }
    SyncLocalStatusSocketPayloadQuarantineRequest parsed;
    parsed.expected_content_sha256 = std::string(expected);
    parsed.observed_content_sha256 = std::string(observed);
    parsed.operation = operation;
    return parsed;
}

[[nodiscard]] std::optional<SyncLocalStatusSocketHistoricalVersionRequest>
parse_historical_version_request(std::string_view request) {
    SyncLocalStatusSocketHistoricalVersionRequest parsed;
    if (request == kHistoricalVersionsRequest) {
        parsed.operation =
            SyncLocalStatusSocketHistoricalVersionOperation::Inspect;
        return parsed;
    }
    if (request.starts_with(kHistoricalVersionsQueryRequestPrefix)) {
        if (request.back() != '\n') return std::nullopt;
        request.remove_prefix(kHistoricalVersionsQueryRequestPrefix.size());
        request.remove_suffix(1U);

        std::array<std::string_view, 5U> fields{};
        std::size_t field_count = 0U;
        while (!request.empty()) {
            if (field_count == fields.size()) return std::nullopt;
            const std::size_t space = request.find(' ');
            const std::string_view field = space == std::string_view::npos
                ? request
                : request.substr(0U, space);
            if (field.empty()) return std::nullopt;
            fields[field_count++] = field;
            if (space == std::string_view::npos) {
                request = {};
            } else {
                request.remove_prefix(space + 1U);
            }
        }
        if (field_count != 3U && field_count != 4U && field_count != 5U) {
            return std::nullopt;
        }

        std::size_t offset = 0U;
        SyncReplicaHistoricalVersionInspectionMode inspection_mode =
            SyncReplicaHistoricalVersionInspectionMode::
                ExactPayloadAvailability;
        if (field_count == 5U) {
            try {
                inspection_mode =
                    sync_replica_historical_version_inspection_mode_from_name_or_throw(
                        fields[0U],
                        "local historical-version inspection mode");
            } catch (const std::invalid_argument&) {
                return std::nullopt;
            }
            offset = 1U;
        }

        const std::string_view maximum_text = fields[offset];
        const std::string_view path_hex = fields[offset + 1U];
        const std::string_view cursor = fields[offset + 2U];
        const std::string_view source_cutpoint =
            field_count == offset + 4U ? fields[offset + 3U]
                                       : std::string_view("-");
        const std::optional<std::uint64_t> maximum =
            parse_decimal_uint64(maximum_text);
        if (!maximum.has_value() ||
            std::to_string(*maximum) != maximum_text) {
            return std::nullopt;
        }

        parsed.operation =
            SyncLocalStatusSocketHistoricalVersionOperation::Inspect;
        parsed.query.inspection_mode = inspection_mode;
        parsed.query.maximum_entries = *maximum;
        if (path_hex != "-") {
            const std::optional<std::string> decoded =
                lowercase_hex_decode(path_hex);
            if (!decoded.has_value()) return std::nullopt;
            parsed.query.canonical_path = std::move(*decoded);
        }
        if (cursor != "-") {
            if (!is_lowercase_sha256_hex(cursor)) return std::nullopt;
            parsed.query.start_after_operation_id = std::string(cursor);
        }
        if (source_cutpoint != "-") {
            try {
                parsed.query.expected_source_cutpoint =
                    decode_sync_replica_historical_version_source_cutpoint_or_throw(
                        source_cutpoint,
                        "local historical-version source cutpoint");
            } catch (const std::invalid_argument&) {
                return std::nullopt;
            }
        }
        try {
            validate_sync_replica_historical_version_query_or_throw(
                parsed.query, "local historical-version query");
        } catch (const std::invalid_argument&) {
            return std::nullopt;
        }
        return parsed;
    }
    if (request.starts_with(kRetentionPlanRequestPrefix)) {
        if (request.back() != '\n') return std::nullopt;
        request.remove_prefix(kRetentionPlanRequestPrefix.size());
        request.remove_suffix(1U);
        std::array<std::string_view, 3U> fields{};
        for (std::size_t index = 0U; index < fields.size(); ++index) {
            const std::size_t space = request.find(' ');
            fields[index] = space == std::string_view::npos
                ? request
                : request.substr(0U, space);
            if (fields[index].empty()) return std::nullopt;
            if (index + 1U == fields.size()) {
                if (space != std::string_view::npos) return std::nullopt;
                request = {};
            } else {
                if (space == std::string_view::npos) return std::nullopt;
                request.remove_prefix(space + 1U);
            }
        }
        const std::optional<std::uint64_t> maximum =
            parse_decimal_uint64(fields[0U]);
        if (!maximum.has_value() ||
            std::to_string(*maximum) != fields[0U]) {
            return std::nullopt;
        }
        parsed.operation =
            SyncLocalStatusSocketHistoricalVersionOperation::RetentionPlan;
        parsed.retention_plan_query.maximum_entries = *maximum;
        if (fields[1U] != "-") {
            if (!is_lowercase_sha256_hex(fields[1U])) return std::nullopt;
            parsed.retention_plan_query.start_after_content_sha256 =
                std::string(fields[1U]);
        }
        if (fields[2U] != "-") {
            try {
                parsed.retention_plan_query.expected_source_cutpoint =
                    decode_sync_replica_historical_version_source_cutpoint_or_throw(
                        fields[2U], "local retention-plan source cutpoint");
            } catch (const std::invalid_argument&) {
                return std::nullopt;
            }
        }
        try {
            validate_sync_replica_retention_plan_query_or_throw(
                parsed.retention_plan_query, "local retention-plan query");
        } catch (const std::invalid_argument&) {
            return std::nullopt;
        }
        return parsed;
    }
    constexpr std::size_t digest_characters = 64U;
    const auto parse_retention_update =
        [&](std::string_view prefix,
            SyncLocalStatusSocketHistoricalVersionOperation operation)
            -> std::optional<SyncLocalStatusSocketHistoricalVersionRequest> {
        if (!request.starts_with(prefix)) return std::nullopt;
        if (request.size() != prefix.size() + digest_characters + 1U ||
            request.back() != '\n') {
            return SyncLocalStatusSocketHistoricalVersionRequest{};
        }
        std::string_view operation_id = request;
        operation_id.remove_prefix(prefix.size());
        operation_id.remove_suffix(1U);
        if (!is_lowercase_sha256_hex(operation_id)) {
            return SyncLocalStatusSocketHistoricalVersionRequest{};
        }
        SyncLocalStatusSocketHistoricalVersionRequest update;
        update.operation = operation;
        update.retention_operation_id = std::string(operation_id);
        return update;
    };
    if (request.starts_with(kHistoricalVersionPinRequestPrefix)) {
        const auto update = parse_retention_update(
            kHistoricalVersionPinRequestPrefix,
            SyncLocalStatusSocketHistoricalVersionOperation::Pin);
        if (!update.has_value() || update->retention_operation_id.empty()) {
            return std::nullopt;
        }
        return update;
    }
    if (request.starts_with(kHistoricalVersionUnpinRequestPrefix)) {
        const auto update = parse_retention_update(
            kHistoricalVersionUnpinRequestPrefix,
            SyncLocalStatusSocketHistoricalVersionOperation::Unpin);
        if (!update.has_value() || update->retention_operation_id.empty()) {
            return std::nullopt;
        }
        return update;
    }
    if (request.starts_with(kHistoricalVersionRestoreExactRequestPrefix)) {
        const std::size_t exact_size =
            kHistoricalVersionRestoreExactRequestPrefix.size() +
            digest_characters + 1U + digest_characters + 1U;
        if (request.size() != exact_size || request.back() != '\n') {
            return std::nullopt;
        }
        request.remove_prefix(
            kHistoricalVersionRestoreExactRequestPrefix.size());
        request.remove_suffix(1U);
        if (request.size() != digest_characters * 2U + 1U ||
            request[digest_characters] != ' ') {
            return std::nullopt;
        }
        parsed.operation =
            SyncLocalStatusSocketHistoricalVersionOperation::Restore;
        parsed.restore_request.operation_id =
            std::string(request.substr(0U, digest_characters));
        parsed.restore_request.expected_current_operation_id =
            std::string(request.substr(digest_characters + 1U));
        try {
            validate_sync_replica_historical_version_restore_request_or_throw(
                parsed.restore_request,
                "local exact historical-version restore");
        } catch (const std::invalid_argument&) {
            return std::nullopt;
        }
        return parsed;
    }
    if (!request.starts_with(kHistoricalVersionRestoreRequestPrefix) ||
        request.size() !=
            kHistoricalVersionRestoreRequestPrefix.size() +
                digest_characters + 1U ||
        request.back() != '\n') {
        return std::nullopt;
    }
    request.remove_prefix(kHistoricalVersionRestoreRequestPrefix.size());
    request.remove_suffix(1U);
    parsed.operation =
        SyncLocalStatusSocketHistoricalVersionOperation::Restore;
    parsed.restore_request.operation_id = std::string(request);
    try {
        validate_sync_replica_historical_version_restore_request_or_throw(
            parsed.restore_request,
            "local historical-version restore");
    } catch (const std::invalid_argument&) {
        return std::nullopt;
    }
    return parsed;
}

[[nodiscard]] LocalPeerCredentials observe_local_peer_or_throw(
    int descriptor,
    std::string_view label) {
#if defined(__linux__)
    struct ucred credentials {};
    socklen_t size = sizeof(credentials);
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PEERCRED, &credentials, &size) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " peer-credential query failed: " +
            system_error_text(error));
    }
    if (size != sizeof(credentials) || credentials.pid <= 0) {
        throw std::runtime_error(
            std::string(label) + " returned invalid peer credentials");
    }
    if (credentials.uid != ::geteuid()) {
        throw std::runtime_error(
            std::string(label) +
            " peer is not owned by the effective user");
    }
    return {credentials.pid};
#else
    // The 0700 parent and 0600 socket remain the portable owner boundary. Linux
    // additionally binds every response to the connected process through
    // SO_PEERCRED; other Unix peer-PID APIs can be added when those platforms
    // enter the qualified product lane.
    (void)descriptor;
    (void)label;
    return {};
#endif
}

void close_noexcept(int& descriptor) noexcept {
    if (descriptor >= 0) {
        (void)::close(descriptor);
        descriptor = -1;
    }
}

void close_or_throw(int& descriptor, std::string_view label) {
    if (descriptor < 0) return;
    const int selected = descriptor;
    descriptor = -1;
    if (::close(selected) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " close failed: " +
            system_error_text(error));
    }
}

[[nodiscard]] Json parse_json_object_or_throw(
    std::string_view bytes,
    std::string_view label) {
    if (bytes.empty() ||
        bytes.size() > kSyncLocalStatusSocketMaximumResponseBytes) {
        throw std::invalid_argument(
            std::string(label) + " JSON size is outside the supported bound");
    }
    Json parsed;
    try {
        parsed = parse_json_text(std::string(bytes));
    } catch (const std::runtime_error& error) {
        throw std::invalid_argument(
            std::string(label) + " is not valid JSON: " + error.what());
    }
    if (!parsed.is_object()) {
        throw std::invalid_argument(
            std::string(label) + " must be a JSON object");
    }
    return parsed;
}

void validate_status_json_or_throw(
    std::string_view bytes,
    std::string_view label) {
    (void)parse_json_object_or_throw(bytes, label);
}

[[nodiscard]] sockaddr_un unix_address_or_throw(
    const fs::path& path,
    std::string_view label) {
    const std::string native = path.string();
    if (native.find('\0') != std::string::npos) {
        throw std::invalid_argument(
            std::string(label) + " path contains an embedded NUL");
    }
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    if (native.size() >= sizeof(address.sun_path)) {
        throw std::invalid_argument(
            std::string(label) + " path exceeds Unix socket sun_path");
    }
    std::memcpy(address.sun_path, native.c_str(), native.size() + 1U);
    return address;
}

[[nodiscard]] SocketPathIdentity socket_path_identity_from_status_or_throw(
    const struct stat& status,
    mode_t required_mode,
    std::string_view label) {
    if (!S_ISSOCK(status.st_mode)) {
        throw std::runtime_error(
            std::string(label) + " is not a Unix socket");
    }
    if (status.st_uid != ::geteuid()) {
        throw std::runtime_error(
            std::string(label) + " is not owned by the effective user");
    }
    if ((status.st_mode & 07777U) != required_mode) {
        throw std::runtime_error(
            std::string(label) + " does not have required mode " +
            std::to_string(static_cast<unsigned int>(required_mode)));
    }
    return {status.st_dev, status.st_ino, status.st_uid};
}

[[nodiscard]] SocketPathIdentity require_socket_path_identity_or_throw(
    const fs::path& path,
    mode_t required_mode,
    std::string_view label) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " lstat failed: " +
            system_error_text(error));
    }
    return socket_path_identity_from_status_or_throw(
        status, required_mode, label);
}

[[nodiscard]] bool same_socket_path_identity_noexcept(
    const fs::path& path,
    const SocketPathIdentity& expected) noexcept {
    struct stat status {};
    return ::lstat(path.c_str(), &status) == 0 &&
        S_ISSOCK(status.st_mode) && status.st_dev == expected.device &&
        status.st_ino == expected.inode && status.st_uid == expected.owner;
}

void require_same_socket_path_identity_or_throw(
    const fs::path& path,
    const SocketPathIdentity& expected,
    mode_t required_mode,
    std::string_view label) {
    const SocketPathIdentity observed = require_socket_path_identity_or_throw(
        path, required_mode, label);
    if (observed.device != expected.device ||
        observed.inode != expected.inode || observed.owner != expected.owner) {
        throw std::runtime_error(
            std::string(label) + " identity changed during the query");
    }
}

void require_completion_socket_path_or_throw(
    const fs::path& path,
    const SocketPathIdentity& expected,
    mode_t required_mode,
    LocalSocketCompletionPathPolicy policy,
    std::string_view label) {
    if (policy == LocalSocketCompletionPathPolicy::RequireSameIdentity) {
        require_same_socket_path_identity_or_throw(
            path, expected, required_mode, label);
        return;
    }

    // A completed stop response is already bound to the connected AF_UNIX
    // peer and to the exact pathname identity re-proved after connect. The
    // service may remove that pathname immediately after replying. Stop alone
    // therefore permits exact ENOENT here; any surviving path must still be
    // the original owner-only socket, and every other command stays strict.
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        const int error = errno;
        if (error == ENOENT) return;
        throw std::runtime_error(
            std::string(label) + " lstat failed: " +
            system_error_text(error));
    }
    const SocketPathIdentity observed =
        socket_path_identity_from_status_or_throw(
            status, required_mode, label);
    if (observed.device != expected.device ||
        observed.inode != expected.inode ||
        observed.owner != expected.owner) {
        throw std::runtime_error(
            std::string(label) +
            " identity changed during the request");
    }
}

void unlink_exact_socket_noexcept(
    const fs::path& path,
    const std::optional<SocketPathIdentity>& expected) noexcept {
    if (!expected.has_value() ||
        !same_socket_path_identity_noexcept(path, *expected)) {
        return;
    }
    (void)::unlink(path.c_str());
}

[[nodiscard]] bool connect_probe_indicates_stale_or_throw(
    const fs::path& path,
    std::string_view label) {
    int descriptor = ::socket(
        AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " stale probe socket failed: " +
            system_error_text(error));
    }
    const sockaddr_un address = unix_address_or_throw(path, label);
    errno = 0;
    const int result = ::connect(
        descriptor, reinterpret_cast<const sockaddr*>(&address),
        sizeof(address));
    const int error = errno;
    close_noexcept(descriptor);
    if (result == 0 || error == EINPROGRESS || error == EALREADY ||
        error == EAGAIN || error == EWOULDBLOCK || error == EISCONN) {
        return false;
    }
    if (error == ECONNREFUSED || error == ENOENT) return true;
    throw std::runtime_error(
        std::string(label) + " existing socket could not be classified: " +
        system_error_text(error));
}

void remove_stale_socket_or_throw(
    const fs::path& path,
    std::string_view label) {
    struct stat initial {};
    if (::lstat(path.c_str(), &initial) != 0) {
        const int error = errno;
        if (error == ENOENT) return;
        throw std::runtime_error(
            std::string(label) + " existing-path lstat failed: " +
            system_error_text(error));
    }
    if (!S_ISSOCK(initial.st_mode) || initial.st_uid != ::geteuid()) {
        throw std::runtime_error(
            std::string(label) +
            " existing path is not an owner-controlled Unix socket");
    }
    if (!connect_probe_indicates_stale_or_throw(path, label)) {
        throw std::runtime_error(
            std::string(label) + " is already served by a live process");
    }
    struct stat selected {};
    if (::lstat(path.c_str(), &selected) != 0 ||
        selected.st_dev != initial.st_dev || selected.st_ino != initial.st_ino ||
        selected.st_uid != initial.st_uid || !S_ISSOCK(selected.st_mode)) {
        throw std::runtime_error(
            std::string(label) +
            " stale socket identity changed before removal");
    }
    if (::unlink(path.c_str()) != 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " stale socket removal failed: " +
            system_error_text(error));
    }
}

[[nodiscard]] Clock::time_point deadline_after_milliseconds_or_throw(
    std::uint64_t milliseconds,
    std::string_view label) {
    if (milliseconds == 0U ||
        milliseconds > kSyncLocalStatusSocketMaximumTimeoutMilliseconds) {
        throw std::invalid_argument(
            std::string(label) + " timeout must be in [1, 60000] milliseconds");
    }
    using Duration = std::chrono::milliseconds;
    if (milliseconds > static_cast<std::uint64_t>(
                           std::numeric_limits<Duration::rep>::max())) {
        throw std::overflow_error(
            std::string(label) + " timeout overflows duration");
    }
    const Duration duration(static_cast<Duration::rep>(milliseconds));
    const Clock::time_point now = Clock::now();
    if (now > Clock::time_point::max() - duration) {
        throw std::overflow_error(
            std::string(label) + " deadline overflows");
    }
    return now + duration;
}

[[nodiscard]] int remaining_poll_milliseconds(
    Clock::time_point deadline) noexcept {
    const Clock::time_point now = Clock::now();
    if (now >= deadline) return 0;
    const auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
        deadline - now);
    const auto count = remaining.count();
    if (count <= 0) return 1;
    if (count > std::numeric_limits<int>::max()) {
        return std::numeric_limits<int>::max();
    }
    return static_cast<int>(count);
}

[[nodiscard]] bool poll_descriptor_until(
    int descriptor,
    short events,
    Clock::time_point deadline,
    std::string_view label) {
    for (;;) {
        pollfd selected{descriptor, events, 0};
        const int timeout = remaining_poll_milliseconds(deadline);
        if (timeout == 0) return false;
        errno = 0;
        const int result = ::poll(&selected, 1U, timeout);
        const int error = errno;
        if (result > 0) {
            if ((selected.revents & (POLLERR | POLLNVAL)) != 0) {
                throw std::runtime_error(
                    std::string(label) + " poll reported socket error");
            }
            return (selected.revents & (events | POLLHUP)) != 0;
        }
        if (result == 0) return false;
        if (error == EINTR) continue;
        throw std::runtime_error(
            std::string(label) + " poll failed: " + system_error_text(error));
    }
}

[[nodiscard]] bool write_all_until(
    int descriptor,
    std::string_view bytes,
    Clock::time_point deadline,
    std::string_view label) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        errno = 0;
        const ssize_t written = ::send(
            descriptor, bytes.data() + offset, bytes.size() - offset,
            MSG_NOSIGNAL);
        const int error = errno;
        if (written > 0) {
            offset += static_cast<std::size_t>(written);
            continue;
        }
        if (written == 0) return false;
        if (error == EINTR) continue;
        if (error == EAGAIN || error == EWOULDBLOCK) {
            if (!poll_descriptor_until(
                    descriptor, POLLOUT, deadline,
                    child_label(label, "write"))) {
                return false;
            }
            continue;
        }
        if (error == EPIPE || error == ECONNRESET || error == ENOTCONN) {
            return false;
        }
        throw std::runtime_error(
            std::string(label) + " send failed: " + system_error_text(error));
    }
    return true;
}

[[nodiscard]] std::optional<std::string> read_request_until(
    int descriptor,
    Clock::time_point deadline,
    std::string_view label) {
    std::string request;
    request.reserve(kMaximumRequestBytes);
    for (;;) {
        std::array<char, kMaximumRequestBytes> buffer{};
        errno = 0;
        const ssize_t received = ::recv(
            descriptor, buffer.data(), buffer.size(), 0);
        const int error = errno;
        if (received > 0) {
            const std::size_t count = static_cast<std::size_t>(received);
            if (request.size() > kMaximumRequestBytes - count) {
                return std::nullopt;
            }
            request.append(buffer.data(), count);
            const std::size_t newline = request.find('\n');
            if (newline != std::string::npos) {
                if (newline + 1U != request.size()) return std::nullopt;
                return request;
            }
            if (request.size() == kMaximumRequestBytes) return std::nullopt;
            continue;
        }
        if (received == 0) return std::nullopt;
        if (error == EINTR) continue;
        if (error == EAGAIN || error == EWOULDBLOCK) {
            if (!poll_descriptor_until(
                    descriptor, POLLIN, deadline,
                    child_label(label, "read"))) {
                return std::nullopt;
            }
            continue;
        }
        if (error == ECONNRESET || error == ENOTCONN) return std::nullopt;
        throw std::runtime_error(
            std::string(label) + " receive failed: " +
            system_error_text(error));
    }
}

[[nodiscard]] SyncDirectoryAuthority
open_status_parent_authority_or_throw(
    const fs::path& path,
    std::string_view label) {
    SyncDirectoryAuthority parent = SyncDirectoryAuthority::open_or_throw(
        path.parent_path(), child_label(label, "parent directory"));
    const SyncDirectoryAttestation& attestation = parent.attestation();
    if (attestation.owner_user_id !=
            static_cast<std::uint64_t>(::geteuid()) ||
        (attestation.permission_mode & 07777U) != 0700U) {
        throw std::invalid_argument(
            std::string(label) +
            " parent directory must be owned by the effective user with exact mode 0700");
    }
    return parent;
}

[[nodiscard]] std::string read_response_until_or_throw(
    int descriptor,
    Clock::time_point deadline,
    std::string_view label) {
    std::string response;
    response.reserve(4096U);
    for (;;) {
        std::array<char, 4096U> buffer{};
        errno = 0;
        const ssize_t received = ::recv(
            descriptor, buffer.data(), buffer.size(), 0);
        const int error = errno;
        if (received > 0) {
            const std::size_t count = static_cast<std::size_t>(received);
            if (response.size() >
                kSyncLocalStatusSocketMaximumResponseBytes - count) {
                throw std::runtime_error(
                    std::string(label) + " response exceeds bounded size");
            }
            response.append(buffer.data(), count);
            const std::size_t newline = response.find('\n');
            if (newline != std::string::npos) {
                if (newline + 1U != response.size()) {
                    throw std::runtime_error(
                        std::string(label) +
                        " response contains trailing bytes after JSON line");
                }
                response.pop_back();
                validate_status_json_or_throw(response, label);
                return response;
            }
            continue;
        }
        if (received == 0) {
            throw std::runtime_error(
                std::string(label) + " peer closed before a complete JSON line");
        }
        if (error == EINTR) continue;
        if (error == EAGAIN || error == EWOULDBLOCK) {
            if (!poll_descriptor_until(
                    descriptor, POLLIN, deadline,
                    child_label(label, "response"))) {
                throw std::runtime_error(
                    std::string(label) + " response deadline expired");
            }
            continue;
        }
        throw std::runtime_error(
            std::string(label) + " response receive failed: " +
            system_error_text(error));
    }
}

[[nodiscard]] LocalSocketResponse request_local_socket_or_throw(
    const fs::path& absolute_socket_path,
    std::string_view request,
    std::uint64_t timeout_milliseconds,
    LocalSocketCompletionPathPolicy completion_path_policy,
    std::string_view label) {
    validate_sync_local_status_socket_path_or_throw(
        absolute_socket_path, child_label(label, "path"));
    SyncDirectoryAuthority parent = open_status_parent_authority_or_throw(
        absolute_socket_path, child_label(label, "path"));
    const SocketPathIdentity expected_identity =
        require_socket_path_identity_or_throw(
            absolute_socket_path, 0600U, child_label(label, "path"));
    parent.verify_or_throw(child_label(label, "parent pre-connect reproof"));
    const Clock::time_point deadline = deadline_after_milliseconds_or_throw(
        timeout_milliseconds, label);
    const sockaddr_un address = unix_address_or_throw(
        absolute_socket_path, child_label(label, "path"));
    int descriptor = ::socket(
        AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (descriptor < 0) {
        const int error = errno;
        throw std::runtime_error(
            std::string(label) + " socket failed: " +
            system_error_text(error));
    }
    try {
        errno = 0;
        const int connected = ::connect(
            descriptor, reinterpret_cast<const sockaddr*>(&address),
            sizeof(address));
        const int connect_error = errno;
        if (connected != 0 && connect_error != EISCONN) {
            if (connect_error != EINPROGRESS && connect_error != EALREADY &&
                connect_error != EAGAIN && connect_error != EWOULDBLOCK) {
                throw std::runtime_error(
                    std::string(label) + " connect failed: " +
                    system_error_text(connect_error));
            }
            if (!poll_descriptor_until(
                    descriptor, POLLOUT, deadline,
                    child_label(label, "connect"))) {
                throw std::runtime_error(
                    std::string(label) + " connect deadline expired");
            }
            int socket_error = 0;
            socklen_t socket_error_bytes = sizeof(socket_error);
            if (::getsockopt(
                    descriptor, SOL_SOCKET, SO_ERROR,
                    &socket_error, &socket_error_bytes) != 0 ||
                socket_error_bytes != sizeof(socket_error) ||
                (socket_error != 0 && socket_error != EISCONN)) {
                if (socket_error == 0) socket_error = errno;
                throw std::runtime_error(
                    std::string(label) + " connect failed: " +
                    system_error_text(socket_error));
            }
        }
        const LocalPeerCredentials peer = observe_local_peer_or_throw(
            descriptor, child_label(label, "server"));
        require_same_socket_path_identity_or_throw(
            absolute_socket_path, expected_identity, 0600U,
            child_label(label, "connected socket path"));
        parent.verify_or_throw(child_label(label, "parent post-connect reproof"));
        if (!write_all_until(
                descriptor, request, deadline,
                child_label(label, "request"))) {
            throw std::runtime_error(
                std::string(label) + " could not send local request");
        }
        std::string response = read_response_until_or_throw(
            descriptor, deadline, label);
        require_completion_socket_path_or_throw(
            absolute_socket_path, expected_identity, 0600U,
            completion_path_policy,
            child_label(label, "completed socket path"));
        parent.verify_or_throw(child_label(label, "parent final reproof"));
        close_or_throw(descriptor, label);
        return {std::move(response), peer};
    } catch (...) {
        close_noexcept(descriptor);
        throw;
    }
}

[[nodiscard]] long long exact_positive_pid_or_throw(
    const Json& value,
    std::string_view label) {
    if (!value.is_number()) {
        throw std::runtime_error(
            std::string(label) + " pid is not a JSON number");
    }
    const long long process_id = value.integer();
    if (process_id <= 0) {
        throw std::runtime_error(
            std::string(label) + " pid is not positive");
    }
    return process_id;
}

void require_optional_status_pid_matches_peer_or_throw(
    std::string_view response,
    const LocalPeerCredentials& peer,
    std::string_view label) {
    const Json parsed = parse_json_object_or_throw(response, label);
    const Json& reported_pid = parsed.at("pid");
    if (reported_pid.is_null()) return;
    const long long process_id = exact_positive_pid_or_throw(
        reported_pid, label);
    if (peer.process_id.has_value() &&
        process_id != static_cast<long long>(*peer.process_id)) {
        throw std::runtime_error(
            std::string(label) +
            " reported pid does not match the connected Unix peer");
    }
}

void validate_stop_response_or_throw(
    std::string_view response,
    const LocalPeerCredentials& peer,
    std::string_view label) {
    const Json parsed = parse_json_object_or_throw(response, label);
    if (parsed.o.size() != 6U ||
        parsed.at("schema").str() != kStopResponseSchema ||
        parsed.at("command").str() != "stop" ||
        parsed.at("terminal_class").str() != "completed" ||
        parsed.at("stop_mode").str() != "drain" ||
        !parsed.at("first_request").is_bool()) {
        throw std::runtime_error(
            std::string(label) + " has an invalid stop-response shape");
    }
    const long long reported_pid = exact_positive_pid_or_throw(
        parsed.at("server_pid"), label);
    if (peer.process_id.has_value() &&
        reported_pid != static_cast<long long>(*peer.process_id)) {
        throw std::runtime_error(
            std::string(label) +
            " server_pid does not match the connected Unix peer");
    }
}

[[nodiscard]] std::uint64_t exact_nonnegative_uint64_or_throw(
    const Json& value,
    std::string_view label) {
    if (!value.is_number()) {
        throw std::runtime_error(
            std::string(label) + " generation is not a JSON number");
    }
    const long long generation = value.integer();
    if (generation < 0) {
        throw std::runtime_error(
            std::string(label) + " generation is negative");
    }
    return static_cast<std::uint64_t>(generation);
}

void validate_recheck_response_or_throw(
    std::string_view response,
    const LocalPeerCredentials& peer,
    std::string_view label) {
    const Json parsed = parse_json_object_or_throw(response, label);
    const std::string terminal_class = parsed.at("terminal_class").str();
    const bool accepted = terminal_class == "accepted";
    const bool rejected = terminal_class == "rejected";
    const std::size_t expected_fields = rejected ? 6U : 5U;
    if ((!accepted && !rejected) || parsed.o.size() != expected_fields ||
        parsed.at("schema").str() != kRecheckResponseSchema ||
        parsed.at("command").str() != "recheck") {
        throw std::runtime_error(
            std::string(label) + " has an invalid recheck-response shape");
    }
    const std::uint64_t generation = exact_nonnegative_uint64_or_throw(
        parsed.at("request_generation"), label);
    if (accepted && generation == 0U) {
        throw std::runtime_error(
            std::string(label) + " accepted generation is zero");
    }
    if (rejected && parsed.at("reason").str() != "drain_requested") {
        throw std::runtime_error(
            std::string(label) + " has an invalid recheck rejection reason");
    }
    const long long reported_pid = exact_positive_pid_or_throw(
        parsed.at("server_pid"), label);
    if (peer.process_id.has_value() &&
        reported_pid != static_cast<long long>(*peer.process_id)) {
        throw std::runtime_error(
            std::string(label) +
            " server_pid does not match the connected Unix peer");
    }
}

void validate_quarantine_response_or_throw(
    std::string_view response,
    const LocalPeerCredentials& peer,
    SyncLocalStatusSocketPayloadQuarantineOperation operation,
    std::string_view expected_content_sha256,
    std::string_view observed_content_sha256,
    std::string_view label) {
    const Json parsed = parse_json_object_or_throw(response, label);
    const std::string terminal_class = parsed.at("terminal_class").str();
    const bool accepted = terminal_class == "accepted";
    const bool rejected = terminal_class == "rejected";
    const std::size_t expected_fields = rejected ? 8U : 7U;
    const std::string_view expected_schema =
        operation == SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
            ? kQuarantineResponseSchema
            : kQuarantineReleaseResponseSchema;
    const std::string_view expected_command =
        operation == SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
            ? "quarantine"
            : "quarantine-release";
    if ((!accepted && !rejected) || parsed.o.size() != expected_fields ||
        parsed.at("schema").str() != expected_schema ||
        parsed.at("command").str() != expected_command ||
        parsed.at("expected_content_sha256").str() !=
            expected_content_sha256 ||
        parsed.at("observed_content_sha256").str() !=
            observed_content_sha256) {
        throw std::runtime_error(
            std::string(label) +
            " has an invalid payload-quarantine response shape");
    }
    const std::uint64_t generation = exact_nonnegative_uint64_or_throw(
        parsed.at("request_generation"), label);
    if (accepted && generation == 0U) {
        throw std::runtime_error(
            std::string(label) + " accepted generation is zero");
    }
    if (rejected) {
        const std::string reason = parsed.at("reason").str();
        if (reason != "drain_requested" &&
            reason != "different_quarantine_pending") {
            throw std::runtime_error(
                std::string(label) +
                " has an invalid payload-quarantine rejection reason");
        }
    }
    const long long reported_pid = exact_positive_pid_or_throw(
        parsed.at("server_pid"), label);
    if (peer.process_id.has_value() &&
        reported_pid != static_cast<long long>(*peer.process_id)) {
        throw std::runtime_error(
            std::string(label) +
            " server_pid does not match the connected Unix peer");
    }
}

void validate_historical_version_response_or_throw(
    std::string_view response,
    const LocalPeerCredentials& peer,
    SyncLocalStatusSocketHistoricalVersionOperation operation,
    const SyncReplicaHistoricalVersionQuery& query,
    const SyncReplicaRetentionPlanQuery& retention_plan_query,
    const SyncReplicaHistoricalVersionRestoreRequest& restore_request,
    std::string_view retention_operation_id,
    std::string_view label) {
    const Json parsed = parse_json_object_or_throw(response, label);
    const std::string terminal_class = parsed.at("terminal_class").str();
    const bool accepted = terminal_class == "accepted";
    const bool rejected = terminal_class == "rejected";
    const bool restoring =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Restore;
    const bool pinning =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Pin;
    const bool unpinning =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Unpin;
    const bool planning =
        operation ==
        SyncLocalStatusSocketHistoricalVersionOperation::RetentionPlan;
    const bool retention_update = pinning || unpinning;
    const bool exact_restore =
        restoring &&
        restore_request.expected_current_operation_id.has_value();
    const std::size_t expected_fields = retention_update
        ? 6U + (rejected ? 1U : 0U)
        : (restoring
               ? (exact_restore ? 7U : 6U) + (rejected ? 1U : 0U)
               : (planning ? 8U : 10U) + (rejected ? 1U : 0U));
    const std::string_view expected_schema = pinning
        ? kHistoricalVersionPinResponseSchema
        : (unpinning
               ? kHistoricalVersionUnpinResponseSchema
               : (restoring
                      ? (exact_restore
                             ? kHistoricalVersionRestoreExactResponseSchema
                             : kHistoricalVersionRestoreResponseSchema)
                      : (planning ? kRetentionPlanResponseSchema
                                  : kHistoricalVersionsResponseSchema)));
    const std::string_view expected_command = pinning
        ? "version-pin"
        : (unpinning
               ? "version-unpin"
               : (restoring
                      ? "restore"
                      : (planning ? "retention-plan" : "versions")));
    if ((!accepted && !rejected) || parsed.o.size() != expected_fields ||
        parsed.at("schema").str() != expected_schema ||
        parsed.at("command").str() != expected_command) {
        throw std::runtime_error(
            std::string(label) +
            " has an invalid historical-version response shape");
    }
    if (retention_update) {
        if (!is_lowercase_sha256_hex(retention_operation_id) ||
            parsed.at("operation_id").str() != retention_operation_id) {
            throw std::runtime_error(
                std::string(label) +
                " changed the requested retention operation ID");
        }
    } else if (restoring) {
        if (parsed.at("operation_id").str() != restore_request.operation_id) {
            throw std::runtime_error(
                std::string(label) +
                " changed the requested historical operation ID");
        }
        if (exact_restore &&
            parsed.at("expected_current_operation_id").str() !=
                *restore_request.expected_current_operation_id) {
            throw std::runtime_error(
                std::string(label) +
                " changed the expected current operation ID");
        }
    } else if (planning) {
        const std::uint64_t returned_limit = exact_nonnegative_uint64_or_throw(
            parsed.at("maximum_entries"), label);
        if (returned_limit != retention_plan_query.maximum_entries) {
            throw std::runtime_error(
                std::string(label) +
                " changed the requested retention-plan entry limit");
        }
        const Json& returned_cursor =
            parsed.at("start_after_content_sha256");
        if (retention_plan_query.start_after_content_sha256.has_value()) {
            if (returned_cursor.is_null() ||
                returned_cursor.str() !=
                    *retention_plan_query.start_after_content_sha256) {
                throw std::runtime_error(
                    std::string(label) +
                    " changed the requested retention-plan cursor");
            }
        } else if (!returned_cursor.is_null()) {
            throw std::runtime_error(
                std::string(label) +
                " invented a requested retention-plan cursor");
        }
        const Json& returned_source_cutpoint =
            parsed.at("expected_source_cutpoint");
        if (retention_plan_query.expected_source_cutpoint.has_value()) {
            const std::string expected =
                encode_sync_replica_historical_version_source_cutpoint_or_throw(
                    *retention_plan_query.expected_source_cutpoint, label);
            if (returned_source_cutpoint.is_null() ||
                returned_source_cutpoint.str() != expected) {
                throw std::runtime_error(
                    std::string(label) +
                    " changed the requested retention-plan source cutpoint");
            }
        } else if (!returned_source_cutpoint.is_null()) {
            throw std::runtime_error(
                std::string(label) +
                " invented a requested retention-plan source cutpoint");
        }
    } else {
        if (parsed.at("inspection_mode").str() !=
            sync_replica_historical_version_inspection_mode_name(
                query.inspection_mode)) {
            throw std::runtime_error(
                std::string(label) +
                " changed the requested historical inspection mode");
        }
        const std::uint64_t returned_limit = exact_nonnegative_uint64_or_throw(
            parsed.at("maximum_entries"), label);
        if (returned_limit != query.maximum_entries) {
            throw std::runtime_error(
                std::string(label) +
                " changed the requested historical entry limit");
        }
        const Json& returned_path = parsed.at("canonical_path");
        if (query.canonical_path.has_value()) {
            if (returned_path.is_null() ||
                returned_path.str() != *query.canonical_path) {
                throw std::runtime_error(
                    std::string(label) +
                    " changed the requested historical path");
            }
        } else if (!returned_path.is_null()) {
            throw std::runtime_error(
                std::string(label) +
                " invented a requested historical path");
        }
        const Json& returned_cursor =
            parsed.at("start_after_operation_id");
        if (query.start_after_operation_id.has_value()) {
            if (returned_cursor.is_null() ||
                returned_cursor.str() != *query.start_after_operation_id) {
                throw std::runtime_error(
                    std::string(label) +
                    " changed the requested historical cursor");
            }
        } else if (!returned_cursor.is_null()) {
            throw std::runtime_error(
                std::string(label) +
                " invented a requested historical cursor");
        }
        const Json& returned_source_cutpoint =
            parsed.at("expected_source_cutpoint");
        if (query.expected_source_cutpoint.has_value()) {
            const std::string expected =
                encode_sync_replica_historical_version_source_cutpoint_or_throw(
                    *query.expected_source_cutpoint, label);
            if (returned_source_cutpoint.is_null() ||
                returned_source_cutpoint.str() != expected) {
                throw std::runtime_error(
                    std::string(label) +
                    " changed the requested historical source cutpoint");
            }
        } else if (!returned_source_cutpoint.is_null()) {
            throw std::runtime_error(
                std::string(label) +
                " invented a requested historical source cutpoint");
        }
    }
    const std::uint64_t generation = exact_nonnegative_uint64_or_throw(
        parsed.at("request_generation"), label);
    if (accepted && generation == 0U) {
        throw std::runtime_error(
            std::string(label) + " accepted generation is zero");
    }
    if (rejected) {
        const std::string reason = parsed.at("reason").str();
        if (reason != "drain_requested" &&
            reason != "different_historical_version_pending") {
            throw std::runtime_error(
                std::string(label) +
                " has an invalid historical-version rejection reason");
        }
    }
    const long long reported_pid = exact_positive_pid_or_throw(
        parsed.at("server_pid"), label);
    if (peer.process_id.has_value() &&
        reported_pid != static_cast<long long>(*peer.process_id)) {
        throw std::runtime_error(
            std::string(label) +
            " server_pid does not match the connected Unix peer");
    }
}

}  // namespace

struct SyncLocalStatusSocketServer::State final {
    fs::path path;
    std::string label;
    SyncDirectoryAuthority parent;
    int listener = -1;
    int stop_read = -1;
    int stop_write = -1;
    std::optional<SocketPathIdentity> path_identity;
    mutable std::mutex mutex;
    std::condition_variable action_condition;
    bool drain_requested = false;
    std::uint64_t recheck_generation = 0U;
    std::uint64_t quarantine_generation = 0U;
    std::uint64_t quarantine_completed_generation = 0U;
    std::optional<SyncLocalStatusSocketPayloadQuarantineRequest>
        quarantine_pending;
    std::uint64_t historical_version_generation = 0U;
    std::uint64_t historical_version_completed_generation = 0U;
    std::optional<SyncLocalStatusSocketHistoricalVersionRequest>
        historical_version_pending;
    std::string snapshot;
    std::optional<std::string> failure;
    std::thread worker;

    State(fs::path selected_path,
          std::string initial_snapshot,
          std::string selected_label)
        : path(std::move(selected_path)),
          label(std::move(selected_label)),
          snapshot(std::move(initial_snapshot)) {
        validate_sync_local_status_socket_path_or_throw(path, label);
        validate_status_json_or_throw(snapshot, child_label(label, "initial status"));

        parent = open_status_parent_authority_or_throw(path, label);
        remove_stale_socket_or_throw(path, label);
        const sockaddr_un address = unix_address_or_throw(path, label);

        listener = ::socket(
            AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
        if (listener < 0) {
            const int error = errno;
            throw std::runtime_error(
                label + " listener socket failed: " + system_error_text(error));
        }
        try {
            if (::bind(
                    listener, reinterpret_cast<const sockaddr*>(&address),
                    sizeof(address)) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " bind failed: " + system_error_text(error));
            }
            if (::chmod(path.c_str(), 0600U) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " chmod failed: " + system_error_text(error));
            }
            path_identity = require_socket_path_identity_or_throw(
                path, 0600U, label);
            parent.verify_or_throw(child_label(label, "parent reproof"));
            if (::listen(listener, 16) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " listen failed: " + system_error_text(error));
            }
            int stop_pipe[2]{-1, -1};
            if (::pipe2(stop_pipe, O_NONBLOCK | O_CLOEXEC) != 0) {
                const int error = errno;
                throw std::runtime_error(
                    label + " stop pipe failed: " + system_error_text(error));
            }
            stop_read = stop_pipe[0];
            stop_write = stop_pipe[1];
            worker = std::thread([this]() noexcept { run_noexcept(); });
        } catch (...) {
            close_noexcept(stop_read);
            close_noexcept(stop_write);
            close_noexcept(listener);
            unlink_exact_socket_noexcept(path, path_identity);
            throw;
        }
    }

    ~State() noexcept {
        if (stop_write >= 0) {
            const char byte = 1;
            (void)::write(stop_write, &byte, 1U);
        }
        if (worker.joinable()) worker.join();
        close_noexcept(stop_read);
        close_noexcept(stop_write);
        close_noexcept(listener);
        unlink_exact_socket_noexcept(path, path_identity);
    }

    void record_failure_noexcept(std::string message) noexcept {
        try {
            std::lock_guard lock(mutex);
            if (!failure.has_value()) failure = std::move(message);
        } catch (...) {
        }
    }

    void require_namespace_healthy_or_throw(
        std::string_view phase) const {
        if (!path_identity.has_value()) {
            throw std::logic_error(
                label + " has no bound status socket identity");
        }
        parent.verify_or_throw(child_label(label, phase));
        require_same_socket_path_identity_or_throw(
            path, *path_identity, 0600U, child_label(label, phase));
        parent.verify_or_throw(
            child_label(label, std::string(phase) + " parent reproof"));
    }

    [[nodiscard]] std::string snapshot_copy() const {
        std::lock_guard lock(mutex);
        return snapshot;
    }

    [[nodiscard]] std::string process_resources_response() const {
        return render_sync_linux_process_resources_response_json(
            observe_sync_linux_process_resources_or_throw(
                child_label(label, "process resources")));
    }

    [[nodiscard]] std::string request_drain_response() {
        bool first_request = false;
        {
            // Stop and recheck are serialized by one mutex. The owner can read
            // one action snapshot and therefore cannot observe drain while
            // omitting an earlier accepted recheck generation.
            std::lock_guard lock(mutex);
            first_request = !drain_requested;
            drain_requested = true;
        }
        // Publish and notify the obligation before response construction can
        // allocate or fail. The waiter checks the same predicate under mutex,
        // so notify-before-wait cannot lose the accepted action.
        action_condition.notify_all();
        std::ostringstream response;
        response
            << "{\"schema\":\"" << kStopResponseSchema
            << "\",\"command\":\"stop\","
               "\"terminal_class\":\"completed\","
               "\"stop_mode\":\"drain\",\"first_request\":"
            << (first_request ? "true" : "false")
            << ",\"server_pid\":" << static_cast<long long>(::getpid())
            << '}';
        return response.str();
    }

    [[nodiscard]] std::string request_recheck_response() {
        bool accepted = false;
        std::uint64_t generation = 0U;
        {
            std::lock_guard lock(mutex);
            generation = recheck_generation;
            if (!drain_requested) {
                if (generation >= static_cast<std::uint64_t>(
                                      std::numeric_limits<long long>::max())) {
                    throw std::overflow_error(
                        label + " recheck request generation is exhausted");
                }
                ++generation;
                recheck_generation = generation;
                accepted = true;
            }
        }
        if (accepted) action_condition.notify_all();
        std::ostringstream response;
        response
            << "{\"schema\":\"" << kRecheckResponseSchema
            << "\",\"command\":\"recheck\","
               "\"terminal_class\":\""
            << (accepted ? "accepted" : "rejected") << "\"";
        if (!accepted) {
            response << ",\"reason\":\"drain_requested\"";
        }
        response
            << ",\"request_generation\":" << generation
            << ",\"server_pid\":" << static_cast<long long>(::getpid())
            << '}';
        return response.str();
    }

    [[nodiscard]] std::string request_payload_quarantine_response(
        SyncLocalStatusSocketPayloadQuarantineOperation operation,
        std::string expected_content_sha256,
        std::string observed_content_sha256) {
        bool accepted = false;
        std::string rejection_reason;
        std::uint64_t generation = 0U;
        SyncLocalStatusSocketPayloadQuarantineRequest new_request{
            0U, expected_content_sha256, observed_content_sha256, operation};
        {
            std::lock_guard lock(mutex);
            generation = quarantine_generation;
            if (drain_requested) {
                rejection_reason = "drain_requested";
            } else if (quarantine_pending.has_value() &&
                       (quarantine_pending->expected_content_sha256 !=
                            expected_content_sha256 ||
                        quarantine_pending->observed_content_sha256 !=
                            observed_content_sha256 ||
                        quarantine_pending->operation != operation)) {
                rejection_reason = "different_quarantine_pending";
            } else {
                if (generation >= static_cast<std::uint64_t>(
                                      std::numeric_limits<long long>::max())) {
                    throw std::overflow_error(
                        label +
                        " payload quarantine request generation is exhausted");
                }
                ++generation;
                quarantine_generation = generation;
                if (quarantine_pending.has_value()) {
                    quarantine_pending->request_generation = generation;
                } else {
                    new_request.request_generation = generation;
                    quarantine_pending.emplace(std::move(new_request));
                }
                accepted = true;
            }
        }
        if (accepted) action_condition.notify_all();
        const std::string_view response_schema =
            operation ==
                    SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
                ? kQuarantineResponseSchema
                : kQuarantineReleaseResponseSchema;
        const std::string_view command =
            operation ==
                    SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
                ? "quarantine"
                : "quarantine-release";
        std::ostringstream response;
        response
            << "{\"schema\":\"" << response_schema
            << "\",\"command\":\"" << command << "\","
               "\"terminal_class\":\""
            << (accepted ? "accepted" : "rejected") << "\"";
        if (!accepted) {
            response << ",\"reason\":\"" << rejection_reason << "\"";
        }
        response
            << ",\"request_generation\":" << generation
            << ",\"expected_content_sha256\":\""
            << expected_content_sha256
            << "\",\"observed_content_sha256\":\""
            << observed_content_sha256
            << "\",\"server_pid\":"
            << static_cast<long long>(::getpid()) << '}';
        return response.str();
    }

    [[nodiscard]] std::string request_historical_version_response(
        SyncLocalStatusSocketHistoricalVersionOperation operation,
        SyncReplicaHistoricalVersionQuery query,
        SyncReplicaRetentionPlanQuery retention_plan_query,
        SyncReplicaHistoricalVersionRestoreRequest restore_request,
        std::string retention_operation_id) {
        const bool restoring =
            operation == SyncLocalStatusSocketHistoricalVersionOperation::Restore;
        const bool pinning =
            operation == SyncLocalStatusSocketHistoricalVersionOperation::Pin;
        const bool unpinning =
            operation == SyncLocalStatusSocketHistoricalVersionOperation::Unpin;
        const bool planning =
            operation ==
            SyncLocalStatusSocketHistoricalVersionOperation::RetentionPlan;
        const bool retention_update = pinning || unpinning;
        if (restoring) {
            if (query != SyncReplicaHistoricalVersionQuery{} ||
                retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
                !retention_operation_id.empty()) {
                throw std::invalid_argument(
                    label + " restore admission carried an inspection query");
            }
            validate_sync_replica_historical_version_restore_request_or_throw(
                restore_request, label + " restore admission");
        } else if (retention_update) {
            if (query != SyncReplicaHistoricalVersionQuery{} ||
                retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
                restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
                !is_lowercase_sha256_hex(retention_operation_id)) {
                throw std::invalid_argument(
                    label + " retention admission is not canonical");
            }
        } else if (planning) {
            if (query != SyncReplicaHistoricalVersionQuery{} ||
                restore_request !=
                    SyncReplicaHistoricalVersionRestoreRequest{} ||
                !retention_operation_id.empty()) {
                throw std::invalid_argument(
                    label + " retention-plan admission is not canonical");
            }
            validate_sync_replica_retention_plan_query_or_throw(
                retention_plan_query, label + " retention-plan query");
        } else {
            if (retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
                restore_request !=
                    SyncReplicaHistoricalVersionRestoreRequest{} ||
                !retention_operation_id.empty()) {
                throw std::invalid_argument(
                    label + " inspection admission carried another request");
            }
            validate_sync_replica_historical_version_query_or_throw(
                query, label + " historical-version query");
        }

        bool accepted = false;
        std::string rejection_reason;
        std::uint64_t generation = 0U;
        SyncLocalStatusSocketHistoricalVersionRequest new_request{
            .request_generation = 0U,
            .operation = operation,
            .query = query,
            .retention_plan_query = retention_plan_query,
            .restore_request = restore_request,
            .retention_operation_id = retention_operation_id,
        };
        {
            std::lock_guard lock(mutex);
            generation = historical_version_generation;
            if (drain_requested) {
                rejection_reason = "drain_requested";
            } else if (
                historical_version_pending.has_value() &&
                (historical_version_pending->operation != operation ||
                 historical_version_pending->query != query ||
                 historical_version_pending->retention_plan_query !=
                     retention_plan_query ||
                 historical_version_pending->restore_request !=
                     restore_request ||
                 historical_version_pending->retention_operation_id !=
                     retention_operation_id)) {
                rejection_reason = "different_historical_version_pending";
            } else {
                if (generation >= static_cast<std::uint64_t>(
                                      std::numeric_limits<long long>::max())) {
                    throw std::overflow_error(
                        label +
                        " historical-version request generation is exhausted");
                }
                ++generation;
                historical_version_generation = generation;
                if (historical_version_pending.has_value()) {
                    historical_version_pending->request_generation = generation;
                } else {
                    new_request.request_generation = generation;
                    historical_version_pending.emplace(std::move(new_request));
                }
                accepted = true;
            }
        }
        if (accepted) action_condition.notify_all();
        std::ostringstream response;
        response
            << "{\"schema\":\""
            << (pinning
                    ? kHistoricalVersionPinResponseSchema
                    : (unpinning
                           ? kHistoricalVersionUnpinResponseSchema
                           : (restoring
                                  ? (restore_request
                                             .expected_current_operation_id
                                             .has_value()
                                         ? kHistoricalVersionRestoreExactResponseSchema
                                         : kHistoricalVersionRestoreResponseSchema)
                                  : (planning
                                         ? kRetentionPlanResponseSchema
                                         : kHistoricalVersionsResponseSchema))))
            << "\",\"command\":\""
            << (pinning
                    ? "version-pin"
                    : (unpinning
                           ? "version-unpin"
                           : (restoring
                                  ? "restore"
                                  : (planning ? "retention-plan"
                                              : "versions"))))
            << "\",\"terminal_class\":\""
            << (accepted ? "accepted" : "rejected") << "\"";
        if (!accepted) {
            response << ",\"reason\":\"" << rejection_reason << "\"";
        }
        response << ",\"request_generation\":" << generation;
        if (retention_update) {
            response << ",\"operation_id\":\""
                     << retention_operation_id << "\"";
        } else if (restoring) {
            response << ",\"operation_id\":\""
                     << restore_request.operation_id << "\"";
            if (restore_request.expected_current_operation_id.has_value()) {
                response << ",\"expected_current_operation_id\":\""
                         << *restore_request.expected_current_operation_id
                         << "\"";
            }
        } else if (planning) {
            response << ",\"maximum_entries\":"
                     << retention_plan_query.maximum_entries
                     << ",\"start_after_content_sha256\":";
            if (retention_plan_query.start_after_content_sha256.has_value()) {
                response << json_quote(
                    *retention_plan_query.start_after_content_sha256);
            } else {
                response << "null";
            }
            response << ",\"expected_source_cutpoint\":";
            if (retention_plan_query.expected_source_cutpoint.has_value()) {
                response << json_quote(
                    encode_sync_replica_historical_version_source_cutpoint_or_throw(
                        *retention_plan_query.expected_source_cutpoint,
                        label + " retention-plan response source cutpoint"));
            } else {
                response << "null";
            }
        } else {
            response << ",\"inspection_mode\":"
                     << json_quote(
                            sync_replica_historical_version_inspection_mode_name(
                                query.inspection_mode))
                     << ",\"maximum_entries\":" << query.maximum_entries
                     << ",\"canonical_path\":";
            if (query.canonical_path.has_value()) {
                response << json_quote(*query.canonical_path);
            } else {
                response << "null";
            }
            response << ",\"start_after_operation_id\":";
            if (query.start_after_operation_id.has_value()) {
                response << json_quote(*query.start_after_operation_id);
            } else {
                response << "null";
            }
            response << ",\"expected_source_cutpoint\":";
            if (query.expected_source_cutpoint.has_value()) {
                response << json_quote(
                    encode_sync_replica_historical_version_source_cutpoint_or_throw(
                        *query.expected_source_cutpoint,
                        label + " historical-version response source cutpoint"));
            } else {
                response << "null";
            }
        }
        response << ",\"server_pid\":"
                 << static_cast<long long>(::getpid()) << '}';
        return response.str();
    }

    void serve_client_noexcept(int descriptor) noexcept {
        try {
            (void)observe_local_peer_or_throw(
                descriptor, child_label(label, "client"));
            const Clock::time_point deadline =
                deadline_after_milliseconds_or_throw(
                    kServerClientTimeoutMilliseconds,
                    child_label(label, "client"));
            const std::optional<std::string> request = read_request_until(
                descriptor, deadline, child_label(label, "client"));
            std::string response;
            if (request.has_value() && *request == kStatusRequest) {
                response = snapshot_copy();
            } else if (request.has_value() && *request == kResourcesRequest) {
                response = process_resources_response();
            } else if (request.has_value() && *request == kStopRequest) {
                response = request_drain_response();
            } else if (request.has_value() && *request == kRecheckRequest) {
                response = request_recheck_response();
            } else if (request.has_value()) {
                const auto quarantine =
                    parse_payload_quarantine_request(*request);
                const auto historical =
                    parse_historical_version_request(*request);
                if (quarantine.has_value()) {
                    response = request_payload_quarantine_response(
                        quarantine->operation,
                        quarantine->expected_content_sha256,
                        quarantine->observed_content_sha256);
                } else if (historical.has_value()) {
                    response = request_historical_version_response(
                        historical->operation, historical->query,
                        historical->retention_plan_query,
                        historical->restore_request,
                        historical->retention_operation_id);
                } else {
                    response = std::string(kUnsupportedResponse);
                }
            } else {
                response = std::string(kUnsupportedResponse);
            }
            response.push_back('\n');
            (void)write_all_until(
                descriptor, response, deadline,
                child_label(label, "client response"));
        } catch (...) {
            // A local client cannot revoke the service status boundary. The
            // listener remains available for the next bounded request.
        }
        (void)::close(descriptor);
    }

    void run_or_throw() {
        for (;;) {
            std::array<pollfd, 2U> selected{{
                {listener, POLLIN, 0},
                {stop_read, POLLIN, 0},
            }};
            errno = 0;
            const int polled = ::poll(selected.data(), selected.size(), -1);
            const int error = errno;
            if (polled < 0) {
                if (error == EINTR) continue;
                throw std::runtime_error(
                    label + " listener poll failed: " +
                    system_error_text(error));
            }
            if ((selected[1].revents & POLLIN) != 0) return;
            if ((selected[1].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0) {
                throw std::runtime_error(label + " stop pipe failed");
            }
            if ((selected[0].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0) {
                throw std::runtime_error(label + " listener poll failed");
            }
            if ((selected[0].revents & POLLIN) == 0) continue;
            for (;;) {
                errno = 0;
                const int client = ::accept4(
                    listener, nullptr, nullptr,
                    SOCK_NONBLOCK | SOCK_CLOEXEC);
                const int accept_error = errno;
                if (client >= 0) {
                    serve_client_noexcept(client);
                    continue;
                }
                if (accept_error == EINTR) continue;
                if (accept_error == EAGAIN || accept_error == EWOULDBLOCK) {
                    break;
                }
                throw std::runtime_error(
                    label + " accept failed: " +
                    system_error_text(accept_error));
            }
        }
    }

    void run_noexcept() noexcept {
        try {
            run_or_throw();
        } catch (const std::exception& error) {
            record_failure_noexcept(error.what());
        } catch (...) {
            record_failure_noexcept(label + " worker failed without detail");
        }
    }
};

void validate_sync_local_status_socket_path_or_throw(
    const fs::path& absolute_socket_path,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument("sync local status socket label is empty");
    }
    if (absolute_socket_path.empty() || !absolute_socket_path.is_absolute() ||
        absolute_socket_path.lexically_normal() != absolute_socket_path ||
        absolute_socket_path.filename().empty() ||
        absolute_socket_path.parent_path().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " path must be a normalized absolute non-root path");
    }
    (void)unix_address_or_throw(absolute_socket_path, label);
}

void preflight_sync_local_status_socket_or_throw(
    const fs::path& absolute_socket_path,
    std::string_view label) {
    validate_sync_local_status_socket_path_or_throw(
        absolute_socket_path, child_label(label, "path"));
    SyncDirectoryAuthority parent = open_status_parent_authority_or_throw(
        absolute_socket_path, label);
    parent.verify_or_throw(child_label(label, "parent reproof"));
}

SyncLocalStatusSocketServer::SyncLocalStatusSocketServer(
    fs::path absolute_socket_path,
    std::string initial_status_json,
    std::string label)
    : state_(std::make_unique<State>(
          std::move(absolute_socket_path),
          std::move(initial_status_json),
          std::move(label))) {}

SyncLocalStatusSocketServer::~SyncLocalStatusSocketServer() noexcept = default;

const fs::path& SyncLocalStatusSocketServer::path() const noexcept {
    return state_->path;
}

void SyncLocalStatusSocketServer::publish_or_throw(std::string status_json) {
    validate_status_json_or_throw(
        status_json, child_label(state_->label, "published status"));
    state_->require_namespace_healthy_or_throw("publish namespace");
    std::lock_guard lock(state_->mutex);
    if (state_->failure.has_value()) {
        throw std::runtime_error(
            state_->label + " worker failed: " + *state_->failure);
    }
    state_->snapshot = std::move(status_json);
}

void SyncLocalStatusSocketServer::require_healthy_or_throw() const {
    state_->require_namespace_healthy_or_throw("health namespace");
    std::lock_guard lock(state_->mutex);
    if (state_->failure.has_value()) {
        throw std::runtime_error(
            state_->label + " worker failed: " + *state_->failure);
    }
}

SyncLocalStatusSocketActionSnapshot
SyncLocalStatusSocketServer::action_snapshot() const {
    std::lock_guard lock(state_->mutex);
    return {
        state_->drain_requested,
        state_->recheck_generation,
        state_->quarantine_pending,
        state_->historical_version_pending,
    };
}

SyncLocalStatusSocketActionSnapshot
SyncLocalStatusSocketServer::seal_actions_for_owner_shutdown() {
    SyncLocalStatusSocketActionSnapshot terminal_actions;
    {
        std::lock_guard lock(state_->mutex);
        state_->drain_requested = true;
        terminal_actions = {
            state_->drain_requested,
            state_->recheck_generation,
            state_->quarantine_pending,
            state_->historical_version_pending,
        };
    }
    state_->action_condition.notify_all();
    return terminal_actions;
}

void SyncLocalStatusSocketServer::
complete_payload_quarantine_request_or_throw(
    std::uint64_t completed_generation) {
    std::lock_guard lock(state_->mutex);
    if (completed_generation < state_->quarantine_completed_generation) {
        throw std::invalid_argument(
            state_->label +
            " payload quarantine completion generation regressed");
    }
    if (completed_generation > state_->quarantine_generation) {
        throw std::invalid_argument(
            state_->label +
            " payload quarantine completion is a future generation");
    }
    if (completed_generation == state_->quarantine_completed_generation) {
        return;
    }
    if (!state_->quarantine_pending.has_value() ||
        completed_generation == 0U) {
        throw std::invalid_argument(
            state_->label +
            " payload quarantine completion lacks a pending request");
    }
    state_->quarantine_completed_generation = completed_generation;
    if (state_->quarantine_pending->request_generation <=
        completed_generation) {
        state_->quarantine_pending.reset();
    }
}

void SyncLocalStatusSocketServer::
complete_historical_version_request_or_throw(
    std::uint64_t completed_generation) {
    std::lock_guard lock(state_->mutex);
    if (completed_generation <
        state_->historical_version_completed_generation) {
        throw std::invalid_argument(
            state_->label +
            " historical-version completion generation regressed");
    }
    if (completed_generation > state_->historical_version_generation) {
        throw std::invalid_argument(
            state_->label +
            " historical-version completion is a future generation");
    }
    if (completed_generation ==
        state_->historical_version_completed_generation) {
        return;
    }
    if (!state_->historical_version_pending.has_value() ||
        completed_generation == 0U) {
        throw std::invalid_argument(
            state_->label +
            " historical-version completion lacks a pending request");
    }
    state_->historical_version_completed_generation = completed_generation;
    if (state_->historical_version_pending->request_generation <=
        completed_generation) {
        state_->historical_version_pending.reset();
    }
}

bool SyncLocalStatusSocketServer::wait_for_action_request_or_timeout(
    const SyncLocalStatusSocketActionSnapshot& observed_actions,
    std::uint64_t timeout_milliseconds) {
    if (timeout_milliseconds >
        kSyncLocalStatusSocketMaximumTimeoutMilliseconds) {
        throw std::invalid_argument(
            state_->label + " action wait exceeds 60000 milliseconds");
    }
    std::unique_lock lock(state_->mutex);
    if (observed_actions.recheck_request_generation >
        state_->recheck_generation) {
        throw std::invalid_argument(
            state_->label + " action wait baseline is a future generation");
    }
    if (observed_actions.payload_quarantine_request.has_value()) {
        const auto& observed =
            *observed_actions.payload_quarantine_request;
        if (observed.request_generation > state_->quarantine_generation) {
            throw std::invalid_argument(
                state_->label +
                " quarantine wait baseline is a future generation");
        }
        if (state_->quarantine_pending.has_value() &&
            state_->quarantine_pending->request_generation ==
                observed.request_generation &&
            (state_->quarantine_pending->expected_content_sha256 !=
                 observed.expected_content_sha256 ||
             state_->quarantine_pending->observed_content_sha256 !=
                 observed.observed_content_sha256 ||
             state_->quarantine_pending->operation != observed.operation)) {
            throw std::invalid_argument(
                state_->label +
                " quarantine wait baseline changed at one generation");
        }
    }
    if (observed_actions.historical_version_request.has_value()) {
        const auto& observed =
            *observed_actions.historical_version_request;
        if (observed.request_generation >
            state_->historical_version_generation) {
            throw std::invalid_argument(
                state_->label +
                " historical-version wait baseline is a future generation");
        }
        if (state_->historical_version_pending.has_value() &&
            state_->historical_version_pending->request_generation ==
                observed.request_generation &&
            (state_->historical_version_pending->operation !=
                 observed.operation ||
             state_->historical_version_pending->query != observed.query ||
             state_->historical_version_pending->retention_plan_query !=
                 observed.retention_plan_query ||
             state_->historical_version_pending->restore_request !=
                 observed.restore_request ||
             state_->historical_version_pending->retention_operation_id !=
                 observed.retention_operation_id)) {
            throw std::invalid_argument(
                state_->label +
                " historical-version wait baseline changed at one generation");
        }
    }
    const auto action_pending = [this, &observed_actions] {
        if (state_->drain_requested) return true;
        if (state_->recheck_generation >
            observed_actions.recheck_request_generation) {
            return true;
        }
        if (state_->quarantine_pending.has_value()) {
            if (!observed_actions.payload_quarantine_request.has_value()) {
                return true;
            }
            if (state_->quarantine_pending->request_generation >
                observed_actions.payload_quarantine_request->request_generation) {
                return true;
            }
        }
        if (!state_->historical_version_pending.has_value()) return false;
        if (!observed_actions.historical_version_request.has_value()) {
            return true;
        }
        return state_->historical_version_pending->request_generation >
            observed_actions.historical_version_request->request_generation;
    };
    if (action_pending() || timeout_milliseconds == 0U) {
        return action_pending();
    }
    return state_->action_condition.wait_for(
        lock, std::chrono::milliseconds(timeout_milliseconds), action_pending);
}

std::string query_sync_local_status_socket_or_throw(
    const fs::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, kStatusRequest, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::RequireSameIdentity, label);
    require_optional_status_pid_matches_peer_or_throw(
        response.json, response.peer, label);
    return std::move(response.json);
}

std::string query_sync_local_process_resources_or_throw(
    const fs::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, kResourcesRequest, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::RequireSameIdentity, label);
    const std::uint64_t expected_pid = response.peer.process_id.has_value()
        ? static_cast<std::uint64_t>(*response.peer.process_id)
        : 0U;
    (void)parse_sync_linux_process_resources_response_json_or_throw(
        response.json, expected_pid, label);
    return std::move(response.json);
}

std::string request_sync_local_status_stop_or_throw(
    const fs::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, kStopRequest, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::AllowExactAbsenceAfterResponse,
        label);
    validate_stop_response_or_throw(response.json, response.peer, label);
    return std::move(response.json);
}

std::string request_sync_local_status_recheck_or_throw(
    const fs::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, kRecheckRequest, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::RequireSameIdentity, label);
    validate_recheck_response_or_throw(response.json, response.peer, label);
    return std::move(response.json);
}

namespace {

[[nodiscard]] std::string request_payload_quarantine_operation_or_throw(
    const fs::path& absolute_socket_path,
    SyncLocalStatusSocketPayloadQuarantineOperation operation,
    std::string expected_content_sha256,
    std::string observed_content_sha256,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    if (!is_lowercase_sha256_hex(expected_content_sha256) ||
        !is_lowercase_sha256_hex(observed_content_sha256) ||
        expected_content_sha256 == observed_content_sha256) {
        throw std::invalid_argument(
            std::string(label) +
            " requires distinct canonical SHA-256 digests");
    }
    const std::string_view prefix =
        operation == SyncLocalStatusSocketPayloadQuarantineOperation::Preserve
            ? kQuarantineRequestPrefix
            : kQuarantineReleaseRequestPrefix;
    std::string request;
    request.reserve(prefix.size() + 64U + 1U + 64U + 1U);
    request.append(prefix);
    request.append(expected_content_sha256);
    request.push_back(' ');
    request.append(observed_content_sha256);
    request.push_back('\n');
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, request, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::RequireSameIdentity, label);
    validate_quarantine_response_or_throw(
        response.json, response.peer, operation, expected_content_sha256,
        observed_content_sha256, label);
    return std::move(response.json);
}

}  // namespace

std::string request_sync_local_status_payload_quarantine_or_throw(
    const fs::path& absolute_socket_path,
    std::string expected_content_sha256,
    std::string observed_content_sha256,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_payload_quarantine_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketPayloadQuarantineOperation::Preserve,
        std::move(expected_content_sha256),
        std::move(observed_content_sha256), timeout_milliseconds, label);
}

std::string request_sync_local_status_payload_quarantine_release_or_throw(
    const fs::path& absolute_socket_path,
    std::string expected_content_sha256,
    std::string observed_content_sha256,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_payload_quarantine_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketPayloadQuarantineOperation::Release,
        std::move(expected_content_sha256),
        std::move(observed_content_sha256), timeout_milliseconds, label);
}


namespace {

[[nodiscard]] std::string request_historical_version_operation_or_throw(
    const fs::path& absolute_socket_path,
    SyncLocalStatusSocketHistoricalVersionOperation operation,
    SyncReplicaHistoricalVersionQuery query,
    SyncReplicaRetentionPlanQuery retention_plan_query,
    SyncReplicaHistoricalVersionRestoreRequest restore_request,
    std::string retention_operation_id,
    bool use_legacy_default_inspection_request,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    const bool restoring =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Restore;
    const bool pinning =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Pin;
    const bool unpinning =
        operation == SyncLocalStatusSocketHistoricalVersionOperation::Unpin;
    const bool planning =
        operation ==
        SyncLocalStatusSocketHistoricalVersionOperation::RetentionPlan;
    const bool retention_update = pinning || unpinning;
    if (restoring) {
        validate_sync_replica_historical_version_restore_request_or_throw(
            restore_request, label);
        if (query != SyncReplicaHistoricalVersionQuery{} ||
            retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
            !retention_operation_id.empty() ||
            use_legacy_default_inspection_request) {
            throw std::invalid_argument(
                std::string(label) + " restore query is not canonical");
        }
    } else if (retention_update) {
        if (query != SyncReplicaHistoricalVersionQuery{} ||
            retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
            restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
            !is_lowercase_sha256_hex(retention_operation_id) ||
            use_legacy_default_inspection_request) {
            throw std::invalid_argument(
                std::string(label) +
                " retention update is not canonical");
        }
    } else if (planning) {
        if (query != SyncReplicaHistoricalVersionQuery{} ||
            restore_request != SyncReplicaHistoricalVersionRestoreRequest{} ||
            !retention_operation_id.empty() ||
            use_legacy_default_inspection_request) {
            throw std::invalid_argument(
                std::string(label) +
                " retention-plan request is not canonical");
        }
        validate_sync_replica_retention_plan_query_or_throw(
            retention_plan_query, label);
    } else {
        if (retention_plan_query != SyncReplicaRetentionPlanQuery{} ||
            restore_request != SyncReplicaHistoricalVersionRestoreRequest{}) {
            throw std::invalid_argument(
                std::string(label) +
                " inspection carried another request");
        }
        if (!retention_operation_id.empty()) {
            throw std::invalid_argument(
                std::string(label) +
                " inspection carried a retention operation ID");
        }
        validate_sync_replica_historical_version_query_or_throw(query, label);
        if (use_legacy_default_inspection_request &&
            query != SyncReplicaHistoricalVersionQuery{}) {
            throw std::invalid_argument(
                std::string(label) +
                " legacy inspection request requires the default query");
        }
    }

    std::string request;
    if (retention_update) {
        const std::string_view prefix = pinning
            ? kHistoricalVersionPinRequestPrefix
            : kHistoricalVersionUnpinRequestPrefix;
        request.reserve(prefix.size() + 64U + 1U);
        request.append(prefix);
        request.append(retention_operation_id);
        request.push_back('\n');
    } else if (restoring) {
        if (restore_request.expected_current_operation_id.has_value()) {
            request.reserve(
                kHistoricalVersionRestoreExactRequestPrefix.size() +
                64U + 1U + 64U + 1U);
            request.append(kHistoricalVersionRestoreExactRequestPrefix);
            request.append(restore_request.operation_id);
            request.push_back(' ');
            request.append(*restore_request.expected_current_operation_id);
            request.push_back('\n');
        } else {
            request.reserve(
                kHistoricalVersionRestoreRequestPrefix.size() + 64U + 1U);
            request.append(kHistoricalVersionRestoreRequestPrefix);
            request.append(restore_request.operation_id);
            request.push_back('\n');
        }
    } else if (planning) {
        const std::string cursor =
            retention_plan_query.start_after_content_sha256.has_value()
                ? *retention_plan_query.start_after_content_sha256
                : "-";
        const std::string source_cutpoint =
            retention_plan_query.expected_source_cutpoint.has_value()
                ? encode_sync_replica_historical_version_source_cutpoint_or_throw(
                      *retention_plan_query.expected_source_cutpoint,
                      std::string(label) +
                          " retention-plan request source cutpoint")
                : "-";
        request.reserve(
            kRetentionPlanRequestPrefix.size() + 24U + 1U + cursor.size() +
            1U + source_cutpoint.size() + 1U);
        request.append(kRetentionPlanRequestPrefix);
        request.append(std::to_string(retention_plan_query.maximum_entries));
        request.push_back(' ');
        request.append(cursor);
        request.push_back(' ');
        request.append(source_cutpoint);
        request.push_back('\n');
    } else if (use_legacy_default_inspection_request) {
        request = std::string(kHistoricalVersionsRequest);
    } else {
        const std::string path_hex = query.canonical_path.has_value()
            ? lowercase_hex_encode(*query.canonical_path)
            : "-";
        const std::string cursor = query.start_after_operation_id.has_value()
            ? *query.start_after_operation_id
            : "-";
        const std::string source_cutpoint =
            query.expected_source_cutpoint.has_value()
                ? encode_sync_replica_historical_version_source_cutpoint_or_throw(
                      *query.expected_source_cutpoint,
                      std::string(label) +
                          " historical-version request source cutpoint")
                : "-";
        const std::string inspection_mode(
            sync_replica_historical_version_inspection_mode_name(
                query.inspection_mode));
        request.reserve(
            kHistoricalVersionsQueryRequestPrefix.size() +
            inspection_mode.size() + 1U + 24U + 1U + path_hex.size() + 1U +
            cursor.size() + 1U + source_cutpoint.size() + 1U);
        request.append(kHistoricalVersionsQueryRequestPrefix);
        request.append(inspection_mode);
        request.push_back(' ');
        request.append(std::to_string(query.maximum_entries));
        request.push_back(' ');
        request.append(path_hex);
        request.push_back(' ');
        request.append(cursor);
        request.push_back(' ');
        request.append(source_cutpoint);
        request.push_back('\n');
    }
    LocalSocketResponse response = request_local_socket_or_throw(
        absolute_socket_path, request, timeout_milliseconds,
        LocalSocketCompletionPathPolicy::RequireSameIdentity, label);
    validate_historical_version_response_or_throw(
        response.json, response.peer, operation, query, retention_plan_query,
        restore_request, retention_operation_id, label);
    return std::move(response.json);
}

}  // namespace

std::string request_sync_local_status_historical_versions_or_throw(
    const fs::path& absolute_socket_path,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Inspect,
        SyncReplicaHistoricalVersionQuery{},
        SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{}, {}, true,
        timeout_milliseconds, label);
}

std::string request_sync_local_status_historical_versions_query_or_throw(
    const fs::path& absolute_socket_path,
    SyncReplicaHistoricalVersionQuery query,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Inspect,
        std::move(query), SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{}, {}, false,
        timeout_milliseconds, label);
}

std::string request_sync_local_status_historical_version_restore_or_throw(
    const fs::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Restore,
        SyncReplicaHistoricalVersionQuery{},
        SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = std::move(operation_id),
            .expected_current_operation_id = std::nullopt,
        },
        {}, false, timeout_milliseconds, label);
}

std::string
request_sync_local_status_historical_version_restore_exact_or_throw(
    const fs::path& absolute_socket_path,
    std::string operation_id,
    std::string expected_current_operation_id,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Restore,
        SyncReplicaHistoricalVersionQuery{},
        SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = std::move(operation_id),
            .expected_current_operation_id =
                std::move(expected_current_operation_id),
        },
        {}, false, timeout_milliseconds, label);
}

std::string request_sync_local_status_retention_plan_or_throw(
    const fs::path& absolute_socket_path,
    SyncReplicaRetentionPlanQuery query,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::RetentionPlan,
        SyncReplicaHistoricalVersionQuery{}, std::move(query),
        SyncReplicaHistoricalVersionRestoreRequest{}, {}, false,
        timeout_milliseconds, label);
}

std::string request_sync_local_status_historical_version_pin_or_throw(
    const fs::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Pin,
        SyncReplicaHistoricalVersionQuery{},
        SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{},
        std::move(operation_id), false, timeout_milliseconds, label);
}

std::string request_sync_local_status_historical_version_unpin_or_throw(
    const fs::path& absolute_socket_path,
    std::string operation_id,
    std::uint64_t timeout_milliseconds,
    std::string_view label) {
    return request_historical_version_operation_or_throw(
        absolute_socket_path,
        SyncLocalStatusSocketHistoricalVersionOperation::Unpin,
        SyncReplicaHistoricalVersionQuery{},
        SyncReplicaRetentionPlanQuery{},
        SyncReplicaHistoricalVersionRestoreRequest{},
        std::move(operation_id), false, timeout_milliseconds, label);
}
}  // namespace anonsync

#endif
