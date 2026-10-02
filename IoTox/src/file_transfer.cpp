#include "iotox/file_transfer.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <deque>
#include <fcntl.h>
#include <iomanip>
#include <limits>
#include <map>
#include <mutex>
#include <optional>
#include <set>
#include <span>
#include <sstream>
#include <string_view>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

namespace iotox {
namespace {

class UniqueFd {
  public:
    UniqueFd() = default;
    explicit UniqueFd(int descriptor) : descriptor_(descriptor) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd &) = delete;
    UniqueFd &operator=(const UniqueFd &) = delete;

    UniqueFd(UniqueFd &&other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    UniqueFd &operator=(UniqueFd &&other) noexcept {
        if (this != &other) {
            reset();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] explicit operator bool() const noexcept { return descriptor_ >= 0; }

    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) {
            int result = -1;
            do {
                result = ::close(descriptor_);
            } while (result != 0 && errno == EINTR);
        }
        descriptor_ = descriptor;
    }

  private:
    int descriptor_{-1};
};

struct TransferKey {
    std::uint32_t friend_number{0U};
    std::uint32_t file_number{0U};

    [[nodiscard]] auto operator<=>(const TransferKey &) const = default;
};

Status errno_status(
    ErrorCode code, std::string_view operation,
    const std::filesystem::path &path = {}) {
    std::string message(operation);
    if (!path.empty()) {
        message += " '" + path.string() + "'";
    }
    message += ": ";
    message += std::strerror(errno);
    return Status{code, std::move(message)};
}

std::string bytes_hex(std::span<const std::uint8_t> bytes) {
    std::ostringstream output;
    output << std::hex << std::uppercase << std::setfill('0');
    for (const std::uint8_t byte : bytes) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

std::string escape_bytes(std::span<const std::uint8_t> bytes) {
    std::string output;
    output.reserve(bytes.size());
    for (const std::uint8_t byte : bytes) {
        if (byte >= 0x20U && byte <= 0x7EU && byte != '\\') {
            output.push_back(static_cast<char>(byte));
        } else if (byte == '\\') {
            output += "\\\\";
        } else {
            std::ostringstream escaped;
            escaped << "\\x" << std::hex << std::uppercase << std::setw(2)
                    << std::setfill('0') << static_cast<unsigned int>(byte);
            output += escaped.str();
        }
    }
    return output;
}


std::string escape_text(std::string_view text) {
    return escape_bytes(std::span<const std::uint8_t>(
        reinterpret_cast<const std::uint8_t *>(text.data()), text.size()));
}

bool same_timespec(const timespec &left, const timespec &right) {
    return left.tv_sec == right.tv_sec && left.tv_nsec == right.tv_nsec;
}

Status pread_exact(
    int descriptor, std::uint64_t position, std::span<std::uint8_t> output,
    const std::filesystem::path &path) {
    if (position > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "requested file position is not representable by this platform"};
    }
    std::size_t offset = 0U;
    while (offset < output.size()) {
        const std::uint64_t absolute = position + offset;
        if (absolute > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
            return Status{ErrorCode::invalid_argument,
                          "requested file range is not representable by this platform"};
        }
        const ssize_t count = ::pread(
            descriptor, output.data() + offset, output.size() - offset,
            static_cast<off_t>(absolute));
        if (count < 0) {
            if (errno == EINTR) {
                continue;
            }
            return errno_status(ErrorCode::io_error, "unable to read outgoing file", path);
        }
        if (count == 0) {
            return Status{ErrorCode::io_error,
                          "outgoing file ended before the exact toxcore chunk request was satisfied: " +
                              path.string()};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Status pwrite_exact(
    int descriptor, std::uint64_t position, std::span<const std::uint8_t> input,
    const std::filesystem::path &path) {
    if (position > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "received file position is not representable by this platform"};
    }
    std::size_t offset = 0U;
    while (offset < input.size()) {
        const std::uint64_t absolute = position + offset;
        if (absolute > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
            return Status{ErrorCode::invalid_argument,
                          "received file range is not representable by this platform"};
        }
        const ssize_t count = ::pwrite(
            descriptor, input.data() + offset, input.size() - offset,
            static_cast<off_t>(absolute));
        if (count < 0) {
            if (errno == EINTR) {
                continue;
            }
            return errno_status(ErrorCode::io_error, "unable to write incoming file", path);
        }
        if (count == 0) {
            return Status{ErrorCode::io_error,
                          "incoming file write made no progress: " + path.string()};
        }
        offset += static_cast<std::size_t>(count);
    }
    return Status::success();
}

Status fsync_directory(const std::filesystem::path &directory) {
    UniqueFd descriptor(::open(directory.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC));
    if (!descriptor) {
        return errno_status(ErrorCode::io_error, "unable to open destination directory", directory);
    }
    if (::fsync(descriptor.get()) != 0) {
        return errno_status(ErrorCode::io_error, "unable to sync destination directory", directory);
    }
    return Status::success();
}

std::vector<std::uint8_t> filename_bytes(const std::filesystem::path &path) {
    const std::string native = path.filename().native();
    return {native.begin(), native.end()};
}

bool is_absolute_clean_path(const std::filesystem::path &path) {
    return path.is_absolute() && !path.empty() && path.filename() != "." &&
           path.filename() != "..";
}

void saturating_increment(std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) {
        ++value;
    }
}

void saturating_add(std::uint64_t &value, std::uint64_t delta) noexcept {
    if (delta > std::numeric_limits<std::uint64_t>::max() - value) {
        value = std::numeric_limits<std::uint64_t>::max();
    } else {
        value += delta;
    }
}

}  // namespace

class FileTransferManager::Impl {
  public:
    Impl(ToxTransport &transport, Config config)
        : transport_(transport), config_(config) {}

    ~Impl() { stop(); }

    Result<FileTransferRecord> send_path(
        std::uint32_t friend_number, const std::filesystem::path &path,
        const std::optional<FileId> &requested_file_id,
        std::span<const FileByteRange> requested_ranges = {}) {
        if (requested_file_id &&
            std::all_of(requested_file_id->begin(), requested_file_id->end(),
                        [](std::uint8_t byte) { return byte == 0U; })) {
            return Status{ErrorCode::invalid_argument,
                          "explicit outgoing file ID must be nonzero"};
        }
        if (!is_absolute_clean_path(path)) {
            return Status{ErrorCode::invalid_argument,
                          "outgoing file path must be an absolute file path"};
        }
        {
            std::scoped_lock lock(mutex_);
            if (stopped_) {
                return Status{ErrorCode::unavailable, "file-transfer manager is stopped"};
            }
            if (outgoing_.size() + send_reservations_ >= config_.max_active_sends) {
                return Status{ErrorCode::resource_exhausted,
                              "outgoing file-transfer limit reached"};
            }
            ++send_reservations_;
        }

        struct ReservationGuard {
            Impl *owner;
            bool active{true};
            ~ReservationGuard() {
                if (active) {
                    std::scoped_lock lock(owner->mutex_);
                    --owner->send_reservations_;
                }
            }
        } reservation{this};

        UniqueFd descriptor(::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
        if (!descriptor) {
            return errno_status(ErrorCode::io_error, "unable to open outgoing file", path);
        }
        struct stat metadata {};
        if (::fstat(descriptor.get(), &metadata) != 0) {
            return errno_status(ErrorCode::io_error, "unable to inspect outgoing file", path);
        }
        if (!S_ISREG(metadata.st_mode) || metadata.st_size < 0) {
            return Status{ErrorCode::invalid_argument,
                          "outgoing path is not a finite regular file: " + path.string()};
        }
        const auto source_file_size =
            static_cast<std::uint64_t>(metadata.st_size);
        std::vector<FileByteRange> ranges;
        std::uint64_t file_size = source_file_size;
        if (!requested_ranges.empty()) {
            ranges.assign(requested_ranges.begin(), requested_ranges.end());
            file_size = 0U;
            std::uint64_t previous_end = 0U;
            bool first = true;
            for (const FileByteRange &range : ranges) {
                if (range.length == 0U || range.offset > source_file_size ||
                    range.length > source_file_size - range.offset ||
                    (!first && range.offset <= previous_end) ||
                    range.length >
                        std::numeric_limits<std::uint64_t>::max() - file_size) {
                    return Status{
                        ErrorCode::invalid_argument,
                        "outgoing file ranges must be bounded canonical disjoint ranges"};
                }
                previous_end = range.offset + range.length;
                file_size += range.length;
                first = false;
            }
        }
        if (file_size > config_.max_file_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "outgoing file exceeds configured transfer limit of " +
                              std::to_string(config_.max_file_bytes) + " bytes"};
        }
        std::vector<std::uint8_t> filename = filename_bytes(path);
        if (filename.empty() || filename.size() > toxcore::abi::kMaxFilenameLength) {
            return Status{ErrorCode::invalid_argument,
                          "outgoing filename must contain 1.." +
                              std::to_string(toxcore::abi::kMaxFilenameLength) + " bytes"};
        }

        auto source = std::make_shared<OutgoingSource>();
        source->descriptor = std::move(descriptor);
        source->path = path;
        source->device = metadata.st_dev;
        source->inode = metadata.st_ino;
        source->modified = metadata.st_mtim;
        source->source_file_size = source_file_size;
        source->offered_file_size = file_size;
        source->ranges = std::move(ranges);
        const std::size_t max_chunk_bytes = config_.max_chunk_bytes;

        auto offered = transport_.offer_file(
            friend_number, toxcore::abi::kFileKindData, file_size,
            requested_file_id,
            filename,
            [source, max_chunk_bytes](std::uint64_t position,
                                      std::size_t length) {
                return read_outgoing_chunk(
                    *source, position, length, max_chunk_bytes);
            });
        if (!offered) {
            return offered.status();
        }
        const std::uint32_t file_number = offered.value();
        const TransferKey key{friend_number, file_number};
        auto file_id = transport_.get_file_id(friend_number, file_number);
        if (!file_id) {
            {
                std::scoped_lock lock(mutex_);
                early_chunk_requests_.erase(key);
            }
            static_cast<void>(transport_.control_file(
                friend_number, file_number, TransferControl::cancel));
            return file_id.status();
        }
        if (requested_file_id && file_id.value() != *requested_file_id) {
            {
                std::scoped_lock lock(mutex_);
                early_chunk_requests_.erase(key);
            }
            static_cast<void>(transport_.control_file(
                friend_number, file_number, TransferControl::cancel));
            return Status{ErrorCode::protocol_error,
                          "transport changed the explicit outgoing file ID"};
        }

        Outgoing outgoing;
        outgoing.record.direction = FileTransferDirection::outgoing;
        outgoing.record.state = FileTransferState::active;
        outgoing.record.friend_number = friend_number;
        outgoing.record.file_number = file_number;
        outgoing.record.file_kind = toxcore::abi::kFileKindData;
        outgoing.record.file_size = file_size;
        outgoing.record.local_paused = false;
        outgoing.record.peer_paused = false;
        outgoing.record.file_id = file_id.value();
        outgoing.record.has_file_id = true;
        outgoing.record.filename = filename;
        outgoing.record.local_path = path;
        outgoing.record.detail = "waiting-for-chunk-request";
        outgoing.source = std::move(source);

        std::optional<TransportEvent> early_request;
        FileTransferRecord offered_record = outgoing.record;
        bool stopped_after_offer = false;
        {
            std::scoped_lock lock(mutex_);
            --send_reservations_;
            reservation.active = false;
            if (stopped_) {
                stopped_after_offer = true;
            } else {
                outgoing_.emplace(key, std::move(outgoing));
                const auto pending = early_chunk_requests_.find(key);
                if (pending != early_chunk_requests_.end()) {
                    early_request = std::move(pending->second);
                    early_chunk_requests_.erase(pending);
                }
            }
        }
        if (stopped_after_offer) {
            static_cast<void>(transport_.control_file(
                friend_number, file_number, TransferControl::cancel));
            return Status{ErrorCode::unavailable,
                          "file-transfer manager stopped during offer"};
        }

        if (early_request) {
            const Status answered = answer_chunk_request(*early_request);
            if (!answered.ok()) {
                return answered;
            }
            if (early_request->requested_length == 0U) {
                offered_record.state = FileTransferState::completed;
                offered_record.position = offered_record.file_size;
                offered_record.detail = "completed";
                return offered_record;
            }
        }
        return record_for(key, FileTransferDirection::outgoing);
    }

    Result<FileTransferRecord> receive_to_path(
        std::uint32_t friend_number, std::uint32_t file_number,
        const std::filesystem::path &destination,
        std::uint64_t resume_offset = 0U,
        bool resume_in_place = false) {
        const Status carrier_config = validate_carrier_config();
        if (!carrier_config.ok()) {
            return carrier_config;
        }
        if (!is_absolute_clean_path(destination)) {
            return Status{ErrorCode::invalid_argument,
                          "incoming destination must be an absolute file path"};
        }
        const std::filesystem::path parent = destination.parent_path();
        struct stat parent_metadata {};
        if (::lstat(parent.c_str(), &parent_metadata) != 0 ||
            !S_ISDIR(parent_metadata.st_mode) || S_ISLNK(parent_metadata.st_mode)) {
            return Status{ErrorCode::invalid_argument,
                          "incoming destination parent must be an existing real directory: " +
                              parent.string()};
        }
        if (parent_metadata.st_uid != ::geteuid()) {
            return Status{ErrorCode::invalid_argument,
                          "incoming destination directory is not owned by the IoTox user: " +
                              parent.string()};
        }
        struct stat existing {};
        const bool destination_exists =
            ::lstat(destination.c_str(), &existing) == 0;
        if (!destination_exists && errno != ENOENT) {
            return errno_status(
                ErrorCode::io_error, "unable to inspect incoming destination", destination);
        }
        if ((!resume_in_place && destination_exists) ||
            (resume_in_place && !destination_exists)) {
            return Status{
                ErrorCode::invalid_argument,
                !resume_in_place
                    ? "incoming destination already exists: " + destination.string()
                    : "incoming resume destination is absent: " + destination.string()};
        }

        const TransferKey key{friend_number, file_number};
        FileTransferRecord offer;
        {
            std::scoped_lock lock(mutex_);
            if (stopped_) {
                return Status{ErrorCode::unavailable, "file-transfer manager is stopped"};
            }
            const auto found = incoming_offers_.find(key);
            if (found == incoming_offers_.end()) {
                return Status{ErrorCode::not_found,
                              "no paused incoming file offer matches friend/file"};
            }
            if (incoming_.contains(key)) {
                return Status{ErrorCode::invalid_argument,
                              "incoming file transfer is already active"};
            }
            if (incoming_.size() >= config_.max_active_receives) {
                return Status{ErrorCode::resource_exhausted,
                              "incoming file-transfer limit reached"};
            }
            offer = found->second;
        }
        if (offer.file_kind != toxcore::abi::kFileKindData) {
            return Status{ErrorCode::unsupported,
                          "this revision accepts only TOX_FILE_KIND_DATA offers"};
        }
        if (offer.file_size == std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::unsupported,
                          "unknown-size Tox streams are not accepted by the safe path receiver"};
        }
        if (offer.file_size > config_.max_file_bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "incoming offer exceeds configured transfer limit of " +
                              std::to_string(config_.max_file_bytes) + " bytes"};
        }

        if (resume_in_place && resume_offset >= offer.file_size) {
            return Status{ErrorCode::invalid_argument,
                          "incoming resume offset must be below the offered file size"};
        }

        UniqueFd descriptor;
        std::filesystem::path temporary;
        if (resume_in_place) {
            descriptor.reset(::open(
                destination.c_str(), O_RDWR | O_CLOEXEC | O_NOFOLLOW));
            if (!descriptor) {
                return errno_status(
                    ErrorCode::io_error,
                    "unable to open incoming resume destination", destination);
            }
            struct stat opened {};
            if (::fstat(descriptor.get(), &opened) != 0) {
                return errno_status(
                    ErrorCode::io_error,
                    "unable to inspect incoming resume destination", destination);
            }
            if (!S_ISREG(existing.st_mode) || !S_ISREG(opened.st_mode) ||
                existing.st_dev != opened.st_dev ||
                existing.st_ino != opened.st_ino || opened.st_nlink != 1U ||
                opened.st_uid != ::geteuid() ||
                (opened.st_mode & static_cast<mode_t>(0777)) !=
                    static_cast<mode_t>(0600) || opened.st_size < 0 ||
                static_cast<std::uint64_t>(opened.st_size) != resume_offset) {
                return Status{
                    ErrorCode::invalid_argument,
                    "incoming resume destination must be the exact owner-owned mode-0600 single-link prefix"};
            }
            temporary = destination;
        } else {
            std::string temporary_template =
                (parent / (".iotox-" + destination.filename().string() +
                           ".part-XXXXXX"))
                    .string();
            std::vector<char> mutable_template(
                temporary_template.begin(), temporary_template.end());
            mutable_template.push_back('\0');
            descriptor.reset(::mkstemp(mutable_template.data()));
            if (!descriptor) {
                return errno_status(
                    ErrorCode::io_error,
                    "unable to create incoming temporary file", parent);
            }
            temporary = mutable_template.data();
            if (::fcntl(descriptor.get(), F_SETFD, FD_CLOEXEC) != 0 ||
                ::fchmod(descriptor.get(), 0600) != 0) {
                const Status failed = errno_status(
                    ErrorCode::io_error,
                    "unable to secure incoming temporary file", temporary);
                static_cast<void>(::unlink(temporary.c_str()));
                return failed;
            }
        }

        Incoming incoming;
        incoming.record = offer;
        incoming.record.state = FileTransferState::paused;
        incoming.record.local_paused = true;
        incoming.record.local_path = destination;
        incoming.record.position = resume_offset;
        incoming.record.detail = resume_in_place
            ? "resuming-from=" + std::to_string(resume_offset)
            : "temporary=" + temporary.string();
        incoming.descriptor = std::move(descriptor);
        incoming.temporary_path = temporary;
        incoming.final_path = destination;
        incoming.resume_in_place = resume_in_place;
        incoming.carrier_waiting_since = std::chrono::steady_clock::now();
        FileTransferRecord accepted_record;
        std::scoped_lock carrier_lock(carrier_mutex_);
        bool admit_now = false;
        {
            std::scoped_lock lock(mutex_);
            if (stopped_ || incoming_.contains(key) ||
                !incoming_offers_.contains(key)) {
                if (!resume_in_place) {
                    static_cast<void>(::unlink(temporary.c_str()));
                }
                return Status{ErrorCode::unavailable,
                              "incoming transfer changed before it could be accepted"};
            }
            saturating_increment(carrier_next_ticket_);
            incoming.carrier_ticket = carrier_next_ticket_;
            const std::size_t runnable_for_peer = static_cast<std::size_t>(
                std::count_if(
                    incoming_.begin(), incoming_.end(),
                    [friend_number](const auto &entry) {
                        return entry.first.friend_number == friend_number &&
                            entry.second.carrier_runnable;
                    }));
            admit_now = runnable_for_peer <
                config_.carrier_window_per_peer;
            if (!admit_now) {
                incoming.record.detail = "carrier-window-waiting";
            }
            incoming_.emplace(key, std::move(incoming));
            accepted_record = incoming_.at(key).record;
        }

        if (resume_in_place && resume_offset != 0U) {
            const Status sought = transport_.seek_file(
                friend_number, file_number, resume_offset);
            if (!sought.ok()) {
                fail_and_remove_incoming(key, sought.message());
                static_cast<void>(transport_.control_file(
                    friend_number, file_number, TransferControl::cancel));
                return sought;
            }
        }

        // A new incoming Tox transfer already begins at offset zero. Calling
        // tox_file_seek(0) is unnecessary and is invalid for an empty file,
        // because c-toxcore requires a seek position strictly below file_size.
        if (admit_now) {
            const Status resumed = transport_.control_file(
                friend_number, file_number, TransferControl::resume);
            if (!resumed.ok()) {
                fail_and_remove_incoming(key, resumed.message());
                static_cast<void>(transport_.control_file(
                    friend_number, file_number, TransferControl::cancel));
                return resumed;
            }
            const auto now = std::chrono::steady_clock::now();
            std::scoped_lock lock(mutex_);
            const auto found = incoming_.find(key);
            if (found != incoming_.end()) {
                // The owner thread may iterate immediately after the RESUME
                // command returns, and the event pump may apply one or more
                // chunks before this caller reacquires the manager lock. Never
                // replace the live record with the pre-RESUME snapshot: doing
                // so can roll a fast transfer's position backward and make its
                // terminal callback look incomplete. Commit only the local
                // admission facts, preserving all callback-owned progress.
                found->second.carrier_runnable = true;
                found->second.carrier_admitted_at = now;
                found->second.record.local_paused = false;
                refresh_pause_state(found->second.record);
                if (found->second.record.position == 0U) {
                    found->second.record.detail = "receiving";
                }
                record_carrier_resume_locked(found->second, now, true);
                accepted_record = found->second.record;
            }
        }

        // Local admission is complete once the private destination exists and
        // the transfer is either resumed or retained in the bounded carrier
        // window. An actual RESUME may let the event pump publish a tiny file
        // before this control call returns; requiring a second map lookup would
        // turn that valid completion into a spurious NOT_FOUND response.
        // Return the accepted snapshot. Later progress or failure remains
        // observable through events, projections, and the destination path.
        return accepted_record;
    }

    Result<FileTransferRecord> control(
        std::uint32_t friend_number, std::uint32_t file_number,
        TransferControl control) {
        std::scoped_lock carrier_lock(carrier_mutex_);
        const TransferKey key{friend_number, file_number};
        FileTransferRecord before;
        bool is_offer = false;
        bool is_incoming = false;
        {
            std::scoped_lock lock(mutex_);
            if (const auto outgoing = outgoing_.find(key);
                outgoing != outgoing_.end()) {
                before = outgoing->second.record;
            } else if (const auto incoming = incoming_.find(key);
                       incoming != incoming_.end()) {
                before = incoming->second.record;
                is_incoming = true;
            } else if (const auto offer = incoming_offers_.find(key);
                       offer != incoming_offers_.end()) {
                before = offer->second;
                is_offer = true;
            } else {
                return Status{ErrorCode::not_found,
                              "no local file-transfer state matches friend/file"};
            }
        }

        if (control == TransferControl::resume && is_offer) {
            return Status{
                ErrorCode::invalid_argument,
                "incoming offer has no admitted destination; use file-receive before RESUME"};
        }

        if (is_incoming && control != TransferControl::cancel) {
            if (control == TransferControl::pause) {
                bool send_pause = false;
                {
                    std::scoped_lock lock(mutex_);
                    const auto found = incoming_.find(key);
                    if (found == incoming_.end()) {
                        return before;
                    }
                    send_pause = found->second.carrier_runnable;
                    if (!send_pause) {
                        found->second.carrier_manual_pause = true;
                        found->second.record.local_paused = true;
                        refresh_pause_state(found->second.record);
                        found->second.record.detail =
                            "already-paused-locally; carrier ownership transferred to caller";
                        return found->second.record;
                    }
                }
                const Status sent = transport_.control_file(
                    friend_number, file_number, TransferControl::pause);
                if (!sent.ok()) {
                    return sent;
                }
                const auto now = std::chrono::steady_clock::now();
                std::scoped_lock lock(mutex_);
                const auto found = incoming_.find(key);
                if (found == incoming_.end()) {
                    FileTransferRecord accepted = before;
                    accepted.local_paused = true;
                    refresh_pause_state(accepted);
                    accepted.detail = "local-pause";
                    return accepted;
                }
                found->second.carrier_runnable = false;
                found->second.carrier_manual_pause = true;
                found->second.carrier_waiting_since = now;
                found->second.record.local_paused = true;
                refresh_pause_state(found->second.record);
                found->second.record.detail = "local-pause";
                saturating_increment(file_carrier_stats_.pause_count);
                return found->second.record;
            }

            bool admit_now = false;
            {
                std::scoped_lock lock(mutex_);
                const auto found = incoming_.find(key);
                if (found == incoming_.end()) {
                    return before;
                }
                if (found->second.carrier_runnable) {
                    return Status{ErrorCode::invalid_argument,
                                  "local side has not paused this transfer"};
                }
                if (!found->second.carrier_manual_pause) {
                    found->second.record.detail = "carrier-window-waiting";
                    return found->second.record;
                }
                found->second.carrier_manual_pause = false;
                found->second.carrier_waiting_since =
                    std::chrono::steady_clock::now();
                saturating_increment(carrier_next_ticket_);
                found->second.carrier_ticket = carrier_next_ticket_;
                const std::size_t runnable_for_peer = static_cast<std::size_t>(
                    std::count_if(
                        incoming_.begin(), incoming_.end(),
                        [friend_number](const auto &entry) {
                            return entry.first.friend_number == friend_number &&
                                entry.second.carrier_runnable;
                        }));
                admit_now = runnable_for_peer <
                    config_.carrier_window_per_peer;
                if (!admit_now) {
                    found->second.record.detail = "carrier-window-waiting";
                    return found->second.record;
                }
            }
            const Status sent = transport_.control_file(
                friend_number, file_number, TransferControl::resume);
            if (!sent.ok()) {
                std::scoped_lock lock(mutex_);
                const auto found = incoming_.find(key);
                if (found != incoming_.end()) {
                    found->second.carrier_manual_pause = true;
                    found->second.record.detail = "local-resume-failed";
                }
                return sent;
            }
            const auto now = std::chrono::steady_clock::now();
            std::scoped_lock lock(mutex_);
            const auto found = incoming_.find(key);
            if (found == incoming_.end()) {
                FileTransferRecord accepted = before;
                accepted.local_paused = false;
                refresh_pause_state(accepted);
                accepted.detail = "local-resume";
                return accepted;
            }
            found->second.carrier_runnable = true;
            found->second.carrier_admitted_at = now;
            found->second.record.local_paused = false;
            refresh_pause_state(found->second.record);
            found->second.record.detail = "local-resume";
            record_carrier_resume_locked(found->second, now, true);
            return found->second.record;
        }

        if (control == TransferControl::cancel &&
            before.direction == FileTransferDirection::incoming) {
            FileTransferRecord cancelled = before;
            cancelled.state = FileTransferState::cancelled;
            cancelled.detail = "cancelled-locally";
            // Close and unlink the incoming destination before waiting for the
            // owner-thread control. Required chunks already queued in the
            // Agent can then observe only the bounded cancellation tombstone;
            // none can race the accepted local resource decision into disk.
            remove_transfer(
                key, FileTransferState::cancelled, cancelled.detail, true);
            const Status sent = transport_.control_file(
                friend_number, file_number, TransferControl::cancel);
            if (!sent.ok()) {
                cancelled.detail = "cancelled-locally-control-send-failed";
                return sent;
            }
            return cancelled;
        }

        if (control == TransferControl::pause && before.local_paused) {
            // Pending incoming offers begin locally paused, but "offered" is
            // the more important lifecycle state. A redundant local PAUSE must
            // not mislabel an unadmitted offer as an active paused transfer.
            before.detail = is_offer
                ? "already-paused-locally-while-offered"
                : "already-paused-locally";
            return before;
        }
        if (control == TransferControl::resume && !before.local_paused) {
            return Status{ErrorCode::invalid_argument,
                          "local side has not paused this transfer"};
        }

        const Status sent = transport_.control_file(
            friend_number, file_number, control);
        if (control == TransferControl::cancel) {
            FileTransferRecord cancelled = before;
            cancelled.state = FileTransferState::cancelled;
            cancelled.detail = sent.ok() ? "cancelled-locally"
                                         : "cancelled-locally-control-send-failed";
            // Cancellation is also a local resource decision. Once requested,
            // descriptors and temporary files are released even when the
            // control packet itself could not be queued.
            remove_transfer(key, FileTransferState::cancelled, cancelled.detail);
            if (!sent.ok()) {
                return sent;
            }
            return cancelled;
        }
        if (!sent.ok()) {
            return sent;
        }

        FileTransferRecord accepted = before;
        accepted.local_paused = control == TransferControl::pause;
        refresh_pause_state(accepted);
        accepted.detail = "local-" + to_string(control);

        std::scoped_lock lock(mutex_);
        FileTransferRecord *record = nullptr;
        if (const auto outgoing = outgoing_.find(key);
            outgoing != outgoing_.end()) {
            record = &outgoing->second.record;
        } else if (const auto incoming = incoming_.find(key);
                   incoming != incoming_.end()) {
            record = &incoming->second.record;
        }
        if (record == nullptr) {
            // The toxcore control call is the local admission boundary. A tiny
            // transfer may complete, cancel, or otherwise become terminal on
            // the owner thread before this caller reacquires the manager lock.
            // That race must not turn an accepted control into a false failure.
            // Return the frozen admission snapshot; journals and the absence of
            // a live projection carry the later terminal truth.
            return accepted;
        }
        record->local_paused = accepted.local_paused;
        refresh_pause_state(*record);
        record->detail = accepted.detail;
        return *record;
    }

    Status cancel(std::uint32_t friend_number, std::uint32_t file_number) {
        auto cancelled = control(
            friend_number, file_number, TransferControl::cancel);
        return cancelled ? Status::success() : cancelled.status();
    }

    Status retire_incoming(std::uint32_t friend_number,
                           std::uint32_t file_number) {
        std::scoped_lock carrier_lock(carrier_mutex_);
        std::scoped_lock lock(mutex_);
        const TransferKey key{friend_number, file_number};
        remember_cancelled_incoming_locked(key);
        const auto incoming = incoming_.find(key);
        if (incoming != incoming_.end()) {
            incoming->second.descriptor.reset();
            if (!incoming->second.resume_in_place &&
                !incoming->second.temporary_path.empty()) {
                static_cast<void>(
                    ::unlink(incoming->second.temporary_path.c_str()));
            }
            incoming_.erase(incoming);
        }
        incoming_offers_.erase(key);
        early_chunk_requests_.erase(key);
        last_failure_ = "incoming-retired-after-carrier-loss";
        return Status::success();
    }

    Status handle_event(const TransportEvent &event) {
        switch (event.kind) {
            case TransportEventKind::file_offer:
                return remember_offer(event);
            case TransportEventKind::file_chunk_request:
                return answer_chunk_request(event);
            case TransportEventKind::file_chunk:
                return receive_chunk(event);
            case TransportEventKind::file_control:
                return apply_remote_control(event);
            case TransportEventKind::friend_connection:
                if (event.connection_status == 0) {
                    remove_friend(event.friend_number, "friend-went-offline");
                }
                return Status::success();
            case TransportEventKind::friend_removed:
                remove_friend(event.friend_number, "friend-removed");
                return Status::success();
            case TransportEventKind::backend_ready:
            case TransportEventKind::self_connection:
            case TransportEventKind::friend_request:
            case TransportEventKind::friend_added:
            case TransportEventKind::friend_name:
            case TransportEventKind::friend_status_message:
            case TransportEventKind::friend_status:
            case TransportEventKind::friend_typing:
            case TransportEventKind::message_sent:
            case TransportEventKind::friend_message:
            case TransportEventKind::friend_read_receipt:
            case TransportEventKind::lossy_packet:
            case TransportEventKind::lossless_packet:
            case TransportEventKind::bootstrap:
            case TransportEventKind::tcp_relay:
            case TransportEventKind::diagnostic:
                return Status::success();
        }
        return Status{ErrorCode::internal_error, "unknown transport event kind"};
    }

    Status service_carrier() {
        const Status carrier_config = validate_carrier_config();
        if (!carrier_config.ok()) {
            return carrier_config;
        }
        std::scoped_lock carrier_lock(carrier_mutex_);
        std::vector<std::uint32_t> friends;
        {
            std::scoped_lock lock(mutex_);
            if (stopped_) {
                return Status{ErrorCode::unavailable,
                              "file-transfer manager is stopped"};
            }
            for (const auto &[key, incoming] : incoming_) {
                static_cast<void>(incoming);
                if (friends.empty() || friends.back() != key.friend_number) {
                    friends.push_back(key.friend_number);
                }
            }
        }

        Status first_failure = Status::success();
        for (const std::uint32_t friend_number : friends) {
            const auto now = std::chrono::steady_clock::now();
            std::optional<TransferKey> waiting;
            std::optional<TransferKey> active;
            std::size_t runnable = 0U;
            {
                std::scoped_lock lock(mutex_);
                for (const auto &[key, incoming] : incoming_) {
                    if (key.friend_number != friend_number) {
                        continue;
                    }
                    if (incoming.carrier_runnable) {
                        ++runnable;
                        if (!active ||
                            incoming.carrier_admitted_at <
                                incoming_.at(*active).carrier_admitted_at ||
                            (incoming.carrier_admitted_at ==
                                 incoming_.at(*active).carrier_admitted_at &&
                             key < *active)) {
                            active = key;
                        }
                    } else if (!incoming.carrier_manual_pause &&
                               (!waiting ||
                                incoming.carrier_ticket <
                                    incoming_.at(*waiting).carrier_ticket ||
                                (incoming.carrier_ticket ==
                                     incoming_.at(*waiting).carrier_ticket &&
                                 key < *waiting))) {
                        waiting = key;
                    }
                }
                if (!waiting) {
                    continue;
                }
                if (runnable >= config_.carrier_window_per_peer) {
                    if (!active ||
                        now - incoming_.at(*active).carrier_admitted_at <
                            config_.carrier_rotation_quantum) {
                        continue;
                    }
                } else {
                    active.reset();
                }
            }

            if (active) {
                const Status paused = transport_.control_file(
                    active->friend_number, active->file_number,
                    TransferControl::pause);
                if (!paused.ok()) {
                    std::scoped_lock lock(mutex_);
                    // Completion/cancellation can remove the transfer while
                    // the owner command is in flight. That terminal truth is
                    // not a scheduler control failure.
                    if (incoming_.contains(*active)) {
                        saturating_increment(
                            file_carrier_stats_.control_failure_count);
                        if (first_failure.ok()) {
                            first_failure = paused;
                        }
                    }
                    continue;
                }
                std::scoped_lock lock(mutex_);
                const auto found = incoming_.find(*active);
                if (found != incoming_.end()) {
                    found->second.carrier_runnable = false;
                    found->second.carrier_waiting_since = now;
                    saturating_increment(carrier_next_ticket_);
                    found->second.carrier_ticket = carrier_next_ticket_;
                    found->second.record.local_paused = true;
                    refresh_pause_state(found->second.record);
                    found->second.record.detail = "carrier-window-waiting";
                    saturating_increment(file_carrier_stats_.pause_count);
                }
            }

            const Status resumed = transport_.control_file(
                waiting->friend_number, waiting->file_number,
                TransferControl::resume);
            if (!resumed.ok()) {
                bool waiting_live = false;
                {
                    std::scoped_lock lock(mutex_);
                    waiting_live = incoming_.contains(*waiting);
                    if (waiting_live) {
                        saturating_increment(
                            file_carrier_stats_.control_failure_count);
                    }
                }
                if (waiting_live && first_failure.ok()) {
                    first_failure = resumed;
                }
                if (active) {
                    const Status rollback = transport_.control_file(
                        active->friend_number, active->file_number,
                        TransferControl::resume);
                    const auto rollback_now =
                        std::chrono::steady_clock::now();
                    std::scoped_lock lock(mutex_);
                    if (!rollback.ok() && incoming_.contains(*active)) {
                        saturating_increment(
                            file_carrier_stats_.control_failure_count);
                        if (first_failure.ok()) {
                            first_failure = rollback;
                        }
                    } else if (const auto found = incoming_.find(*active);
                               found != incoming_.end()) {
                        found->second.carrier_runnable = true;
                        found->second.carrier_admitted_at = rollback_now;
                        found->second.record.local_paused = false;
                        refresh_pause_state(found->second.record);
                        found->second.record.detail = "receiving";
                        record_carrier_resume_locked(
                            found->second, rollback_now, true);
                    }
                }
                continue;
            }

            const auto resumed_at = std::chrono::steady_clock::now();
            std::scoped_lock lock(mutex_);
            const auto found = incoming_.find(*waiting);
            if (found != incoming_.end()) {
                found->second.carrier_runnable = true;
                found->second.carrier_admitted_at = resumed_at;
                found->second.record.local_paused = false;
                refresh_pause_state(found->second.record);
                found->second.record.detail = "receiving";
                record_carrier_resume_locked(
                    found->second, resumed_at, true);
                if (active) {
                    saturating_increment(file_carrier_stats_.rotation_count);
                }
            }
        }
        return first_failure;
    }

    std::vector<FileTransferRecord> list() const {
        std::vector<FileTransferRecord> records;
        std::scoped_lock lock(mutex_);
        records.reserve(incoming_offers_.size() + incoming_.size() + outgoing_.size());
        for (const auto &[key, offer] : incoming_offers_) {
            if (!incoming_.contains(key)) {
                records.push_back(offer);
            }
        }
        for (const auto &[key, transfer] : incoming_) {
            static_cast<void>(key);
            records.push_back(transfer.record);
        }
        for (const auto &[key, transfer] : outgoing_) {
            static_cast<void>(key);
            records.push_back(transfer.record);
        }
        std::sort(records.begin(), records.end(), [](const auto &left, const auto &right) {
            if (left.direction != right.direction) {
                return left.direction < right.direction;
            }
            if (left.friend_number != right.friend_number) {
                return left.friend_number < right.friend_number;
            }
            return left.file_number < right.file_number;
        });
        return records;
    }

    FileCarrierStats stats() const {
        FileCarrierStats result;
        std::scoped_lock lock(mutex_);
        result = file_carrier_stats_;
        result.window_per_peer = config_.carrier_window_per_peer;
        result.rotation_quantum_ms = static_cast<std::uint64_t>(
            config_.carrier_rotation_quantum.count());
        for (const auto &[key, incoming] : incoming_) {
            static_cast<void>(key);
            if (incoming.carrier_runnable) {
                ++result.runnable_receives;
            } else if (!incoming.carrier_manual_pause) {
                ++result.waiting_receives;
            }
        }
        return result;
    }

    void stop() noexcept {
        std::scoped_lock carrier_lock(carrier_mutex_);
        std::scoped_lock lock(mutex_);
        if (stopped_) {
            return;
        }
        stopped_ = true;
        for (auto &[key, incoming] : incoming_) {
            static_cast<void>(key);
            incoming.descriptor.reset();
            if (!incoming.resume_in_place &&
                !incoming.temporary_path.empty()) {
                static_cast<void>(::unlink(incoming.temporary_path.c_str()));
            }
        }
        incoming_.clear();
        outgoing_.clear();
        incoming_offers_.clear();
        cancelled_incoming_order_.clear();
        cancelled_incoming_.clear();
        early_chunk_requests_.clear();
    }

  private:
    [[nodiscard]] Status validate_carrier_config() const {
        if (config_.carrier_window_per_peer == 0U ||
            config_.carrier_window_per_peer >
                config_.max_active_receives ||
            config_.carrier_window_per_peer > 256U ||
            config_.carrier_rotation_quantum <
                std::chrono::milliseconds(5) ||
            config_.carrier_rotation_quantum >
                std::chrono::milliseconds(1000)) {
            return Status{
                ErrorCode::invalid_argument,
                "file carrier window must be in 1..min(active receives, 256) and quantum in 5..1000 ms"};
        }
        return Status::success();
    }

    struct OutgoingSource {
        UniqueFd descriptor;
        std::filesystem::path path;
        dev_t device{};
        ino_t inode{};
        timespec modified{};
        std::uint64_t source_file_size{0U};
        std::uint64_t offered_file_size{0U};
        std::vector<FileByteRange> ranges;
    };

    struct Outgoing {
        FileTransferRecord record;
        std::shared_ptr<OutgoingSource> source;
    };

    struct Incoming {
        FileTransferRecord record;
        UniqueFd descriptor;
        std::filesystem::path temporary_path;
        std::filesystem::path final_path;
        bool resume_in_place{false};
        bool carrier_runnable{false};
        bool carrier_manual_pause{false};
        std::uint64_t carrier_ticket{0U};
        std::chrono::steady_clock::time_point carrier_waiting_since{};
        std::chrono::steady_clock::time_point carrier_admitted_at{};
    };

    void record_carrier_resume_locked(
        Incoming &incoming, std::chrono::steady_clock::time_point now,
        bool admission) noexcept {
        const auto waited = std::chrono::duration_cast<std::chrono::microseconds>(
            now - incoming.carrier_waiting_since);
        const std::uint64_t waited_us = waited.count() <= 0
            ? 0U
            : static_cast<std::uint64_t>(waited.count());
        saturating_increment(file_carrier_stats_.resume_count);
        if (admission) {
            saturating_increment(file_carrier_stats_.admission_count);
        }
        saturating_add(file_carrier_stats_.total_wait_us, waited_us);
        file_carrier_stats_.maximum_wait_us = std::max(
            file_carrier_stats_.maximum_wait_us, waited_us);
    }

    static Result<std::vector<std::uint8_t>> read_outgoing_chunk(
        const OutgoingSource &source, std::uint64_t position,
        std::size_t length, std::size_t max_chunk_bytes) {
        if (length == 0U) {
            return std::vector<std::uint8_t>{};
        }
        if (length > max_chunk_bytes) {
            return Status{
                ErrorCode::resource_exhausted,
                "toxcore requested a file chunk above the configured safety limit"};
        }
        if (position > source.offered_file_size ||
            length > source.offered_file_size - position) {
            return Status{ErrorCode::io_error,
                          "toxcore requested bytes beyond the offered file size"};
        }

        struct stat before_read {};
        if (::fstat(source.descriptor.get(), &before_read) != 0) {
            return errno_status(
                ErrorCode::io_error, "unable to re-inspect outgoing file",
                source.path);
        }
        if (!S_ISREG(before_read.st_mode) ||
            before_read.st_dev != source.device ||
            before_read.st_ino != source.inode || before_read.st_size < 0 ||
            static_cast<std::uint64_t>(before_read.st_size) !=
                source.source_file_size ||
            !same_timespec(before_read.st_mtim, source.modified)) {
            return Status{ErrorCode::io_error,
                          "outgoing file changed while the transfer was active"};
        }

        std::vector<std::uint8_t> data(length);
        if (source.ranges.empty()) {
            const Status read = pread_exact(
                source.descriptor.get(), position, data, source.path);
            if (!read.ok()) return read;
        } else {
            std::uint64_t virtual_begin = 0U;
            std::uint64_t cursor = position;
            std::size_t filled = 0U;
            for (const FileByteRange &range : source.ranges) {
                const std::uint64_t virtual_end = virtual_begin + range.length;
                if (cursor >= virtual_end) {
                    virtual_begin = virtual_end;
                    continue;
                }
                const std::uint64_t within = cursor - virtual_begin;
                const std::size_t count = static_cast<std::size_t>(
                    std::min<std::uint64_t>(
                        length - filled, range.length - within));
                const Status read = pread_exact(
                    source.descriptor.get(), range.offset + within,
                    std::span<std::uint8_t>(data).subspan(filled, count),
                    source.path);
                if (!read.ok()) return read;
                filled += count;
                cursor += count;
                virtual_begin = virtual_end;
                if (filled == length) break;
            }
            if (filled != length) {
                return Status{ErrorCode::internal_error,
                              "outgoing range map did not cover the offered chunk"};
            }
        }

        struct stat after_read {};
        if (::fstat(source.descriptor.get(), &after_read) != 0) {
            return errno_status(
                ErrorCode::io_error,
                "unable to verify outgoing file after reading", source.path);
        }
        if (!S_ISREG(after_read.st_mode) ||
            after_read.st_dev != source.device ||
            after_read.st_ino != source.inode || after_read.st_size < 0 ||
            static_cast<std::uint64_t>(after_read.st_size) !=
                source.source_file_size ||
            !same_timespec(after_read.st_mtim, source.modified)) {
            return Status{ErrorCode::io_error,
                          "outgoing file changed while a chunk was read"};
        }
        return data;
    }

    Result<FileTransferRecord> record_for(
        const TransferKey &key, FileTransferDirection direction) const {
        std::scoped_lock lock(mutex_);
        if (direction == FileTransferDirection::outgoing) {
            const auto found = outgoing_.find(key);
            if (found != outgoing_.end()) {
                return found->second.record;
            }
        } else {
            const auto active = incoming_.find(key);
            if (active != incoming_.end()) {
                return active->second.record;
            }
            const auto offered = incoming_offers_.find(key);
            if (offered != incoming_offers_.end()) {
                return offered->second;
            }
        }
        return Status{ErrorCode::not_found, "file-transfer record disappeared"};
    }

    Status remember_offer(const TransportEvent &event) {
        if (event.file_size != std::numeric_limits<std::uint64_t>::max() &&
            event.file_size > config_.max_file_bytes) {
            const Status cancelled = transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel);
            if (!cancelled.ok()) {
                return cancelled;
            }
            return Status{ErrorCode::resource_exhausted,
                          "incoming file offer exceeded configured size and was rejected"};
        }
        const TransferKey key{event.friend_number, event.file_number};
        FileTransferRecord record;
        record.direction = FileTransferDirection::incoming;
        record.state = FileTransferState::offered;
        record.friend_number = event.friend_number;
        record.file_number = event.file_number;
        record.file_kind = event.file_kind;
        record.file_size = event.file_size;
        record.local_paused = true;
        record.peer_paused = false;
        record.file_id = event.file_id;
        record.has_file_id = event.has_file_id;
        record.filename = event.filename;
        record.detail = "paused-awaiting-local-destination";

        bool reject_for_capacity = false;
        {
            std::scoped_lock lock(mutex_);
            // Tox file numbers may be reused after terminal state. A fresh
            // offer is authoritative and ends any local-cancellation grace
            // classification retained for the old incarnation.
            cancelled_incoming_.erase(key);
            if (stopped_) {
                return Status{ErrorCode::unavailable, "file-transfer manager is stopped"};
            }
            if (incoming_.contains(key)) {
                return Status{ErrorCode::protocol_error,
                              "incoming Tox offer reused an active incoming file number"};
            }
            const bool is_new = !incoming_offers_.contains(key);
            reject_for_capacity =
                is_new && incoming_offers_.size() >= config_.max_pending_offers;
            if (!reject_for_capacity) {
                incoming_offers_.insert_or_assign(key, std::move(record));
            }
        }
        if (reject_for_capacity) {
            const Status cancelled = transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel);
            if (!cancelled.ok()) {
                return cancelled;
            }
            return Status{ErrorCode::resource_exhausted,
                          "incoming file-offer queue is full; offer was rejected"};
        }
        return Status::success();
    }

    Status answer_chunk_request(const TransportEvent &event) {
        const TransferKey key{event.friend_number, event.file_number};
        if (event.requested_length > config_.max_chunk_bytes) {
            remove_transfer(key, FileTransferState::failed, "chunk-request-too-large");
            static_cast<void>(transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel));
            return Status{ErrorCode::resource_exhausted,
                          "toxcore requested a file chunk above the configured safety limit"};
        }
        if (event.requested_length == 0U) {
            std::scoped_lock lock(mutex_);
            const auto found = outgoing_.find(key);
            if (found == outgoing_.end()) {
                if (early_chunk_requests_.size() >= config_.max_active_sends) {
                    return Status{ErrorCode::resource_exhausted,
                                  "unmatched file chunk-request cache is full"};
                }
                early_chunk_requests_.insert_or_assign(key, event);
                return Status::success();
            }
            outgoing_.erase(found);
            return Status::success();
        }

        if (event.file_chunk_source_attempted) {
            std::scoped_lock lock(mutex_);
            const auto found = outgoing_.find(key);
            if (!event.file_chunk_sent_inline ||
                !event.file_chunk_status.ok()) {
                if (found == outgoing_.end()) {
                    if (early_chunk_requests_.size() >=
                        config_.max_active_sends) {
                        return Status{
                            ErrorCode::resource_exhausted,
                            "unmatched file chunk-request cache is full"};
                    }
                    early_chunk_requests_.insert_or_assign(key, event);
                } else {
                    outgoing_.erase(found);
                }
                last_failure_ = event.file_chunk_status.message();
                return event.file_chunk_status.ok()
                           ? Status{ErrorCode::library_error,
                                    "inline file chunk send failed without a status"}
                           : event.file_chunk_status;
            }
            if (found == outgoing_.end()) {
                if (early_chunk_requests_.size() >= config_.max_active_sends) {
                    return Status{ErrorCode::resource_exhausted,
                                  "unmatched file chunk-request cache is full"};
                }
                const auto pending = early_chunk_requests_.find(key);
                if (pending == early_chunk_requests_.end() ||
                    pending->second.file_position +
                            pending->second.requested_length <
                        event.file_position + event.requested_length) {
                    early_chunk_requests_.insert_or_assign(key, event);
                }
                return Status::success();
            }
            found->second.record.position =
                std::max(found->second.record.position,
                         event.file_position + event.requested_length);
            found->second.record.detail = "sent-chunk-inline";
            return Status::success();
        }

        std::shared_ptr<OutgoingSource> source;
        {
            std::scoped_lock lock(mutex_);
            const auto found = outgoing_.find(key);
            if (found == outgoing_.end()) {
                if (early_chunk_requests_.size() >= config_.max_active_sends) {
                    return Status{ErrorCode::resource_exhausted,
                                  "unmatched file chunk-request cache is full"};
                }
                early_chunk_requests_.insert_or_assign(key, event);
                return Status::success();
            }
            source = found->second.source;
        }
        auto data = read_outgoing_chunk(
            *source, event.file_position, event.requested_length,
            config_.max_chunk_bytes);
        if (!data) {
            remove_transfer(
                key, FileTransferState::failed, data.status().message());
            static_cast<void>(transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel));
            return data.status();
        }

        {
            std::scoped_lock lock(mutex_);
            if (!outgoing_.contains(key)) {
                return Status{ErrorCode::unavailable,
                              "outgoing transfer ended before its requested chunk was sent"};
            }
        }
        const Status sent = transport_.send_file_chunk(
            event.friend_number, event.file_number, event.file_position,
            data.value());
        if (!sent.ok()) {
            remove_transfer(key, FileTransferState::failed, sent.message());
            static_cast<void>(transport_.control_file(
                event.friend_number, event.file_number,
                TransferControl::cancel));
            return sent;
        }
        {
            std::scoped_lock lock(mutex_);
            const auto found = outgoing_.find(key);
            if (found != outgoing_.end()) {
                found->second.record.position =
                    std::max(found->second.record.position,
                             event.file_position + event.requested_length);
                found->second.record.detail = "sent-chunk";
            }
        }
        return Status::success();
    }

    Status receive_chunk(const TransportEvent &event) {
        const TransferKey key{event.friend_number, event.file_number};
        if (event.data.size() > config_.max_chunk_bytes) {
            fail_and_remove_incoming(
                key, "incoming chunk exceeded configured safety limit");
            static_cast<void>(transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel));
            return Status{ErrorCode::resource_exhausted,
                          "incoming file chunk exceeded configured safety limit"};
        }

        if (event.data.empty()) {
            return finish_incoming(key, event.file_position);
        }

        Status chunk_status = Status::success();
        {
            std::scoped_lock lock(mutex_);
            const auto found = incoming_.find(key);
            if (found == incoming_.end()) {
                if (cancelled_incoming_.contains(key)) {
                    // A required file event may already be queued when local
                    // cancellation crosses toxcore. It has no destination or
                    // side effect and is terminal cancellation truth, not a
                    // protocol violation by the peer.
                    return Status::success();
                }
                chunk_status = Status{
                    ErrorCode::protocol_error,
                    "received file data without an accepted local destination"};
            } else if (event.file_position != found->second.record.position ||
                       event.file_position > found->second.record.file_size ||
                       event.data.size() >
                           found->second.record.file_size - event.file_position) {
                chunk_status = Status{
                    ErrorCode::io_error,
                    "incoming file chunk was out of order or exceeded the offered size"};
                found->second.descriptor.reset();
                if (!found->second.resume_in_place &&
                    !found->second.temporary_path.empty()) {
                    static_cast<void>(::unlink(found->second.temporary_path.c_str()));
                }
                incoming_.erase(found);
                incoming_offers_.erase(key);
            } else {
                // The manager owns one descriptor for the complete receive.
                // Serialize this bounded positional write with local control
                // instead of duplicating and closing that descriptor for
                // every provider-sized chunk. This removes two syscalls per
                // 1,371-byte callback while retaining the same pinned inode
                // and exact position check.
                chunk_status = pwrite_exact(
                    found->second.descriptor.get(), event.file_position,
                    event.data, found->second.temporary_path);
                if (!chunk_status.ok()) {
                    if (found->second.resume_in_place) {
                        // pwrite_exact may have committed a strict prefix of
                        // this callback before reporting an error. Restore the
                        // last completely-accounted application boundary so a
                        // later retry cannot mistake uncertain bytes for
                        // verified progress.
                        if (::ftruncate(
                                found->second.descriptor.get(),
                                static_cast<off_t>(
                                    found->second.record.position)) != 0) {
                            chunk_status = errno_status(
                                ErrorCode::io_error,
                                "unable to restore incoming resume prefix after write failure",
                                found->second.temporary_path);
                        }
                    }
                    found->second.descriptor.reset();
                    if (!found->second.resume_in_place &&
                        !found->second.temporary_path.empty()) {
                        static_cast<void>(::unlink(found->second.temporary_path.c_str()));
                    }
                    incoming_.erase(found);
                    incoming_offers_.erase(key);
                } else {
                    found->second.record.position += event.data.size();
                    found->second.record.detail = "received-chunk";
                }
            }
        }
        if (!chunk_status.ok()) {
            static_cast<void>(transport_.control_file(
                event.friend_number, event.file_number, TransferControl::cancel));
            return chunk_status;
        }
        return Status::success();
    }

    Status finish_incoming(const TransferKey &key, std::uint64_t position) {
        // Completion removes the receive from incoming_ before fsync/link
        // publishes its final path. Keep that whole transition inside the
        // same lifecycle boundary as local control and dead-carrier
        // retirement: otherwise cleanup can observe neither the map entry nor
        // the final path, then race a late link() into the staging directory.
        std::scoped_lock carrier_lock(carrier_mutex_);
        std::filesystem::path temporary;
        std::filesystem::path final_path;
        UniqueFd descriptor;
        bool resume_in_place = false;
        std::optional<Status> validation_failure;
        {
            std::scoped_lock lock(mutex_);
            const auto found = incoming_.find(key);
            if (found == incoming_.end()) {
                if (cancelled_incoming_.contains(key)) {
                    return Status::success();
                }
                validation_failure = Status{
                    ErrorCode::protocol_error,
                    "incoming completion arrived without an active receiver"};
            } else if (position != found->second.record.file_size ||
                       found->second.record.position != found->second.record.file_size) {
                validation_failure = Status{
                    ErrorCode::io_error,
                    "incoming transfer ended before the offered file size was complete"};
                found->second.descriptor.reset();
                if (!found->second.resume_in_place &&
                    !found->second.temporary_path.empty()) {
                    static_cast<void>(::unlink(found->second.temporary_path.c_str()));
                }
                incoming_.erase(found);
                incoming_offers_.erase(key);
            } else {
                temporary = found->second.temporary_path;
                final_path = found->second.final_path;
                resume_in_place = found->second.resume_in_place;
                descriptor = std::move(found->second.descriptor);
                incoming_.erase(found);
                incoming_offers_.erase(key);
            }
        }
        if (validation_failure) {
            static_cast<void>(transport_.control_file(
                key.friend_number, key.file_number, TransferControl::cancel));
            return *validation_failure;
        }

        if (resume_in_place) {
            struct stat opened {};
            struct stat current {};
            if (::fstat(descriptor.get(), &opened) != 0 ||
                ::lstat(final_path.c_str(), &current) != 0) {
                const Status failed = errno_status(
                    ErrorCode::io_error,
                    "unable to revalidate completed incoming resume destination",
                    final_path);
                descriptor.reset();
                return failed;
            }
            if (!S_ISREG(opened.st_mode) || !S_ISREG(current.st_mode) ||
                opened.st_dev != current.st_dev ||
                opened.st_ino != current.st_ino || opened.st_nlink != 1U ||
                opened.st_uid != ::geteuid() ||
                (opened.st_mode & static_cast<mode_t>(0777)) !=
                    static_cast<mode_t>(0600) || opened.st_size < 0 ||
                static_cast<std::uint64_t>(opened.st_size) != position) {
                descriptor.reset();
                return Status{
                    ErrorCode::unavailable,
                    "incoming resume destination identity or private shape changed before completion"};
            }
        }

        if (::fsync(descriptor.get()) != 0) {
            const Status failed = errno_status(
                ErrorCode::io_error, "unable to sync completed incoming file", temporary);
            descriptor.reset();
            if (!resume_in_place) {
                static_cast<void>(::unlink(temporary.c_str()));
            }
            return failed;
        }
        descriptor.reset();

        if (resume_in_place) {
            // The caller deliberately supplied and retains this private
            // partial inode. It is complete but remains unpublished until the
            // upper protocol authenticates the full immutable digest.
            return fsync_directory(final_path.parent_path());
        }

        // link()+unlink() publishes without replacing an existing destination.
        // Both paths are in the same directory, so this is atomic and cannot
        // cross filesystems.
        if (::link(temporary.c_str(), final_path.c_str()) != 0) {
            const Status failed = errno == EEXIST
                                      ? Status{ErrorCode::invalid_argument,
                                               "incoming destination appeared before publication: " +
                                                   final_path.string()}
                                      : errno_status(
                                            ErrorCode::io_error,
                                            "unable to publish completed incoming file",
                                            final_path);
            static_cast<void>(::unlink(temporary.c_str()));
            return failed;
        }
        if (::unlink(temporary.c_str()) != 0) {
            return errno_status(
                ErrorCode::io_error, "unable to remove incoming temporary link", temporary);
        }
        return fsync_directory(final_path.parent_path());
    }

    Status apply_remote_control(const TransportEvent &event) {
        const TransferKey key{event.friend_number, event.file_number};
        if (event.file_control == TransferControl::cancel) {
            remove_transfer(key, FileTransferState::cancelled, "cancelled-by-peer");
            return Status::success();
        }
        std::scoped_lock lock(mutex_);
        if (const auto found = outgoing_.find(key); found != outgoing_.end()) {
            found->second.record.peer_paused =
                event.file_control == TransferControl::pause;
            refresh_pause_state(found->second.record);
            found->second.record.detail = "peer-" + to_string(event.file_control);
        }
        if (const auto found = incoming_.find(key); found != incoming_.end()) {
            found->second.record.peer_paused =
                event.file_control == TransferControl::pause;
            refresh_pause_state(found->second.record);
            found->second.record.detail = "peer-" + to_string(event.file_control);
        }
        if (const auto found = incoming_offers_.find(key);
            found != incoming_offers_.end()) {
            // An unadmitted incoming offer remains an offer even if the sender
            // independently pauses or resumes it. The destination gate is a
            // distinct local fact and stays closed until receive_to_path().
            found->second.peer_paused =
                event.file_control == TransferControl::pause;
            found->second.detail =
                "peer-" + to_string(event.file_control) + "-while-offered";
        }
        return Status::success();
    }

    static void refresh_pause_state(FileTransferRecord &record) noexcept {
        record.state = record.local_paused || record.peer_paused
                           ? FileTransferState::paused
                           : FileTransferState::active;
    }

    void fail_and_remove_incoming(const TransferKey &key, std::string detail) {
        std::scoped_lock lock(mutex_);
        const auto found = incoming_.find(key);
        if (found != incoming_.end()) {
            found->second.descriptor.reset();
            if (!found->second.resume_in_place &&
                !found->second.temporary_path.empty()) {
                static_cast<void>(::unlink(found->second.temporary_path.c_str()));
            }
            incoming_.erase(found);
        }
        incoming_offers_.erase(key);
        last_failure_ = std::move(detail);
    }

    void remember_cancelled_incoming_locked(const TransferKey &key) {
        static constexpr std::size_t kHistoryLimit = 1024U;
        cancelled_incoming_.insert(key);
        cancelled_incoming_order_.push_back(key);
        while (cancelled_incoming_order_.size() > kHistoryLimit) {
            const TransferKey oldest = cancelled_incoming_order_.front();
            cancelled_incoming_order_.pop_front();
            if (std::find(
                    cancelled_incoming_order_.begin(),
                    cancelled_incoming_order_.end(), oldest) ==
                cancelled_incoming_order_.end()) {
                cancelled_incoming_.erase(oldest);
            }
        }
    }

    void remove_transfer(
        const TransferKey &key, FileTransferState, std::string detail,
        bool remember_incoming_cancellation = false) {
        std::scoped_lock lock(mutex_);
        if (remember_incoming_cancellation) {
            remember_cancelled_incoming_locked(key);
        }
        outgoing_.erase(key);
        early_chunk_requests_.erase(key);
        const auto incoming = incoming_.find(key);
        if (incoming != incoming_.end()) {
            incoming->second.descriptor.reset();
            if (!incoming->second.resume_in_place &&
                !incoming->second.temporary_path.empty()) {
                static_cast<void>(::unlink(incoming->second.temporary_path.c_str()));
            }
            incoming_.erase(incoming);
        }
        incoming_offers_.erase(key);
        last_failure_ = std::move(detail);
    }

    void remove_friend(std::uint32_t friend_number, std::string detail) {
        std::scoped_lock lock(mutex_);
        std::erase_if(
            cancelled_incoming_order_, [friend_number](const TransferKey &key) {
                return key.friend_number == friend_number;
            });
        std::erase_if(
            cancelled_incoming_, [friend_number](const TransferKey &key) {
                return key.friend_number == friend_number;
            });
        for (auto iterator = outgoing_.begin(); iterator != outgoing_.end();) {
            if (iterator->first.friend_number == friend_number) {
                iterator = outgoing_.erase(iterator);
            } else {
                ++iterator;
            }
        }
        for (auto iterator = incoming_.begin(); iterator != incoming_.end();) {
            if (iterator->first.friend_number == friend_number) {
                iterator->second.descriptor.reset();
                if (!iterator->second.resume_in_place &&
                    !iterator->second.temporary_path.empty()) {
                    static_cast<void>(::unlink(iterator->second.temporary_path.c_str()));
                }
                iterator = incoming_.erase(iterator);
            } else {
                ++iterator;
            }
        }
        std::erase_if(incoming_offers_, [friend_number](const auto &entry) {
            return entry.first.friend_number == friend_number;
        });
        std::erase_if(early_chunk_requests_, [friend_number](const auto &entry) {
            return entry.first.friend_number == friend_number;
        });
        last_failure_ = std::move(detail);
    }

    ToxTransport &transport_;
    Config config_;
    mutable std::mutex carrier_mutex_;
    mutable std::mutex mutex_;
    bool stopped_{false};
    std::size_t send_reservations_{0U};
    std::map<TransferKey, Outgoing> outgoing_;
    std::map<TransferKey, Incoming> incoming_;
    std::map<TransferKey, FileTransferRecord> incoming_offers_;
    std::deque<TransferKey> cancelled_incoming_order_;
    std::set<TransferKey> cancelled_incoming_;
    std::map<TransferKey, TransportEvent> early_chunk_requests_;
    FileCarrierStats file_carrier_stats_;
    std::uint64_t carrier_next_ticket_{0U};
    std::string last_failure_;
};

FileTransferManager::FileTransferManager(ToxTransport &transport)
    : FileTransferManager(transport, Config{}) {}
FileTransferManager::FileTransferManager(ToxTransport &transport, Config config)
    : impl_(std::make_unique<Impl>(transport, config)) {}
FileTransferManager::~FileTransferManager() = default;
Result<FileTransferRecord> FileTransferManager::send_path(
    std::uint32_t friend_number, const std::filesystem::path &path) {
    return impl_->send_path(friend_number, path, std::nullopt);
}
Result<FileTransferRecord> FileTransferManager::send_path_with_file_id(
    std::uint32_t friend_number, const std::filesystem::path &path,
    const FileId &file_id) {
    return impl_->send_path(friend_number, path, file_id);
}
Result<FileTransferRecord> FileTransferManager::send_path_ranges_with_file_id(
    std::uint32_t friend_number, const std::filesystem::path &path,
    std::span<const FileByteRange> ranges, const FileId &file_id) {
    if (ranges.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "explicit outgoing range list must not be empty"};
    }
    return impl_->send_path(friend_number, path, file_id, ranges);
}
Result<FileTransferRecord> FileTransferManager::receive_to_path(
    std::uint32_t friend_number, std::uint32_t file_number,
    const std::filesystem::path &destination) {
    return impl_->receive_to_path(friend_number, file_number, destination);
}
Result<FileTransferRecord> FileTransferManager::receive_to_path_from_offset(
    std::uint32_t friend_number, std::uint32_t file_number,
    const std::filesystem::path &destination, std::uint64_t resume_offset) {
    return impl_->receive_to_path(
        friend_number, file_number, destination, resume_offset, true);
}
Result<FileTransferRecord> FileTransferManager::control(
    std::uint32_t friend_number, std::uint32_t file_number,
    TransferControl control) {
    return impl_->control(friend_number, file_number, control);
}
Status FileTransferManager::cancel(
    std::uint32_t friend_number, std::uint32_t file_number) {
    return impl_->cancel(friend_number, file_number);
}
Status FileTransferManager::retire_incoming(
    std::uint32_t friend_number, std::uint32_t file_number) {
    return impl_->retire_incoming(friend_number, file_number);
}
Status FileTransferManager::handle_event(const TransportEvent &event) {
    return impl_->handle_event(event);
}
Status FileTransferManager::service_carrier() {
    return impl_->service_carrier();
}
std::vector<FileTransferRecord> FileTransferManager::list() const {
    return impl_->list();
}
FileCarrierStats FileTransferManager::stats() const { return impl_->stats(); }
void FileTransferManager::stop() noexcept { impl_->stop(); }

std::string to_string(FileTransferDirection direction) {
    switch (direction) {
        case FileTransferDirection::outgoing:
            return "outgoing";
        case FileTransferDirection::incoming:
            return "incoming";
    }
    return "unknown";
}

std::string to_string(FileTransferState state) {
    switch (state) {
        case FileTransferState::offered:
            return "offered";
        case FileTransferState::active:
            return "active";
        case FileTransferState::paused:
            return "paused";
        case FileTransferState::completed:
            return "completed";
        case FileTransferState::cancelled:
            return "cancelled";
        case FileTransferState::failed:
            return "failed";
    }
    return "unknown";
}

std::string render_file_transfer(const FileTransferRecord &record) {
    std::ostringstream output;
    output << "direction=" << to_string(record.direction)
           << " state=" << to_string(record.state)
           << " friend-number=" << record.friend_number
           << " file-number=" << record.file_number
           << " kind=" << record.file_kind
           << " size=" << record.file_size
           << " position=" << record.position
           << " local-paused=" << (record.local_paused ? 1 : 0)
           << " peer-paused=" << (record.peer_paused ? 1 : 0)
           << " file-id="
           << (record.has_file_id ? bytes_hex(record.file_id) : std::string("unknown"))
           << " filename=" << escape_bytes(record.filename);
    if (!record.local_path.empty()) {
        output << " local-path=" << escape_text(record.local_path.string());
    }
    if (!record.detail.empty()) {
        output << " detail=" << escape_text(record.detail);
    }
    return output.str();
}

}  // namespace iotox
