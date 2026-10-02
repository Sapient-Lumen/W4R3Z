#include "iotox/local/peer_fifo.hpp"

#include "iotox/toxcore/abi.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <exception>
#include <fcntl.h>
#include <map>
#include <mutex>
#include <poll.h>
#include <set>
#include <string>
#include <string_view>
#include <sys/eventfd.h>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::local {
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
            reset(std::exchange(other.descriptor_, -1));
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] explicit operator bool() const noexcept {
        return descriptor_ >= 0;
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) {
            static_cast<void>(::close(descriptor_));
        }
        descriptor_ = descriptor;
    }

  private:
    int descriptor_{-1};
};

Status system_status(std::string operation,
                     const std::filesystem::path &path = {}) {
    std::string message = std::move(operation);
    if (!path.empty()) {
        message += " '" + path.string() + "'";
    }
    message += ": ";
    message += std::strerror(errno);
    return Status{ErrorCode::io_error, std::move(message)};
}

bool valid_public_key(std::string_view value) {
    if (value.size() != toxcore::abi::kPublicKeySize * 2U) {
        return false;
    }
    return std::all_of(value.begin(), value.end(), [](char character) {
        return (character >= '0' && character <= '9') ||
               (character >= 'A' && character <= 'F');
    });
}

bool valid_lane_name(std::string_view value) {
    if (value.empty() || value.size() > 64U || value == "." || value == "..") {
        return false;
    }
    return std::all_of(value.begin(), value.end(), [](char character) {
        return (character >= 'a' && character <= 'z') ||
               (character >= '0' && character <= '9') ||
               character == '-' || character == '_' || character == '.';
    });
}

bool same_fifo(const struct stat &left, const struct stat &right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

struct FifoKey {
    std::string public_key;
    std::size_t lane_index{0U};

    [[nodiscard]] bool operator<(const FifoKey &other) const noexcept {
        if (public_key != other.public_key) {
            return public_key < other.public_key;
        }
        return lane_index < other.lane_index;
    }
};

}  // namespace

class PeerFifoServer::Impl {
  public:
    Impl(Config config, Handler handler, ErrorHandler error_handler)
        : config_(std::move(config)), handler_(std::move(handler)),
          error_handler_(std::move(error_handler)),
          lane_fifo_counts_(config_.lanes.size(), 0U) {}

    ~Impl() { stop(); }

    Status start() {
        bool expected = false;
        if (!start_called_.compare_exchange_strong(expected, true)) {
            return Status{ErrorCode::invalid_argument,
                          "peer FIFO server start() may only be called once"};
        }
        const Status config_status = validate_config();
        if (!config_status.ok()) {
            return config_status;
        }

        struct stat root_metadata {};
        if (::lstat(config_.peers_root.c_str(), &root_metadata) != 0) {
            return system_status("unable to inspect peer FIFO root",
                                 config_.peers_root);
        }
        if (!S_ISDIR(root_metadata.st_mode) ||
            S_ISLNK(root_metadata.st_mode) ||
            root_metadata.st_uid != ::geteuid() ||
            (root_metadata.st_mode & 0077U) != 0U) {
            return {ErrorCode::io_error,
                    "peer FIFO root must be a private real directory owned by the daemon user: " +
                        config_.peers_root.string()};
        }

        UniqueFd wake(::eventfd(0U, EFD_CLOEXEC | EFD_NONBLOCK));
        if (!wake) {
            return system_status("unable to create peer FIFO wake event");
        }
        wake_ = std::move(wake);
        stop_requested_.store(false);
        scan_fifos();
        if (config_.layout == PeerFifoLayout::root_lanes) {
            const PeerFifoStats initial = stats();
            if (initial.total_fifo_count != config_.lanes.size()) {
                clear_fifos();
                wake_.reset();
                return Status{
                    ErrorCode::io_error,
                    "peer FIFO server could not establish every required root lane at startup"};
            }
        }
        running_.store(true);
        try {
            worker_ = std::thread([this] { worker_main(); });
        } catch (const std::exception &exception) {
            running_.store(false);
            clear_fifos();
            wake_.reset();
            return {ErrorCode::resource_exhausted,
                    "unable to start peer FIFO worker: " +
                        std::string(exception.what())};
        } catch (...) {
            running_.store(false);
            clear_fifos();
            wake_.reset();
            return {ErrorCode::resource_exhausted,
                    "unable to start peer FIFO worker"};
        }
        return Status::success();
    }

    void stop() {
        stop_requested_.store(true);
        if (wake_) {
            const std::uint64_t one = 1U;
            const auto wake_result = ::write(wake_.get(), &one, sizeof(one));
            static_cast<void>(wake_result); // Best effort: stop also closes the descriptors.
        }
        if (worker_.joinable()) {
            if (worker_.get_id() == std::this_thread::get_id()) {
                return;
            }
            worker_.join();
        }
        running_.store(false);
        clear_fifos();
        wake_.reset();
    }

    [[nodiscard]] bool running() const noexcept { return running_.load(); }

    [[nodiscard]] PeerFifoStats stats() const {
        PeerFifoStats result;
        result.running = running();
        std::scoped_lock lock(stats_mutex_);
        result.total_fifo_count = total_fifo_count_;
        result.lane_fifo_counts.reserve(config_.lanes.size());
        for (std::size_t index = 0U; index < config_.lanes.size(); ++index) {
            result.lane_fifo_counts.emplace_back(
                config_.lanes[index].name,
                index < lane_fifo_counts_.size()
                    ? lane_fifo_counts_[index]
                    : 0U);
        }
        return result;
    }

    [[nodiscard]] std::size_t monitored_fifo_count(
        std::string_view lane) const {
        std::scoped_lock lock(stats_mutex_);
        for (std::size_t index = 0U; index < config_.lanes.size(); ++index) {
            if (config_.lanes[index].name == lane &&
                index < lane_fifo_counts_.size()) {
                return lane_fifo_counts_[index];
            }
        }
        return 0U;
    }

    [[nodiscard]] const std::filesystem::path &peers_root() const noexcept {
        return config_.peers_root;
    }

  private:
    struct Fifo {
        std::string public_key;
        std::size_t lane_index{0U};
        std::filesystem::path path;
        struct stat metadata {};
        long pipe_buf{0L};
        UniqueFd read_descriptor;
        UniqueFd hold_writer;
        std::vector<std::uint8_t> partial;
        bool discarding{false};
        std::chrono::steady_clock::time_point last_record_byte{};
    };

    [[nodiscard]] Status validate_config() {
        if (!handler_) {
            return {ErrorCode::invalid_argument,
                    "peer FIFO server handler is empty"};
        }
        switch (config_.layout) {
            case PeerFifoLayout::public_key_directories:
            case PeerFifoLayout::root_lanes:
                break;
            default:
                return {ErrorCode::invalid_argument,
                        "peer FIFO server layout is not recognized"};
        }
        if (config_.peers_root.empty() || !config_.peers_root.is_absolute()) {
            return {ErrorCode::invalid_argument,
                    "peer FIFO root must be an absolute path"};
        }
        if (config_.lanes.empty()) {
            return {ErrorCode::invalid_argument,
                    "peer FIFO server requires at least one lane"};
        }
        std::set<std::string> names;
        for (const PeerFifoLane &lane : config_.lanes) {
            if (!valid_lane_name(lane.name)) {
                return {ErrorCode::invalid_argument,
                        "peer FIFO lane name is not a safe local filename: " +
                            lane.name};
            }
            if (!names.insert(lane.name).second) {
                return {ErrorCode::invalid_argument,
                        "peer FIFO lane name is duplicated: " + lane.name};
            }
            if (lane.maximum_record_bytes == 0U ||
                lane.maximum_record_bytes > 64U * 1024U) {
                return {ErrorCode::invalid_argument,
                        "peer FIFO lane '" + lane.name +
                            "' record limit must be between 1 and 65536 bytes"};
            }
        }
        if (config_.rescan_interval < std::chrono::milliseconds(10) ||
            config_.rescan_interval > std::chrono::seconds(10)) {
            return {ErrorCode::invalid_argument,
                    "peer FIFO rescan interval must be between 10ms and 10s"};
        }
        if (config_.partial_record_timeout < std::chrono::milliseconds(100) ||
            config_.partial_record_timeout > std::chrono::minutes(5)) {
            return {ErrorCode::invalid_argument,
                    "peer FIFO partial-record timeout must be between 100ms and 5m"};
        }
        {
            std::scoped_lock lock(stats_mutex_);
            lane_fifo_counts_.assign(config_.lanes.size(), 0U);
            total_fifo_count_ = 0U;
        }
        return Status::success();
    }

    [[nodiscard]] const PeerFifoLane &lane(const Fifo &fifo) const {
        return config_.lanes[fifo.lane_index];
    }

    void report_error(std::string_view public_key, std::string_view lane_name,
                      const Status &status) noexcept {
        if (!error_handler_) {
            return;
        }
        try {
            error_handler_(public_key, lane_name, status);
        } catch (...) {
        }
    }

    void deliver(Fifo &fifo) noexcept {
        const PeerFifoLane &selected = lane(fifo);
        if (fifo.partial.empty() && !selected.allow_empty) {
            report_error(
                fifo.public_key, selected.name,
                {ErrorCode::invalid_argument,
                 "peer FIFO lane '" + selected.name +
                     "' does not accept an empty record"});
            return;
        }
        try {
            handler_(fifo.public_key, selected.name, fifo.partial);
        } catch (const std::exception &exception) {
            report_error(
                fifo.public_key, selected.name,
                {ErrorCode::internal_error,
                 "peer FIFO lane '" + selected.name +
                     "' handler failed: " + exception.what()});
        } catch (...) {
            report_error(
                fifo.public_key, selected.name,
                {ErrorCode::internal_error,
                 "peer FIFO lane '" + selected.name +
                     "' handler failed unexpectedly"});
        }
    }

    Result<Fifo> open_fifo(std::string public_key, std::size_t lane_index,
                           const std::filesystem::path &path,
                           const struct stat &expected) {
        const PeerFifoLane &selected = config_.lanes[lane_index];
        UniqueFd reader(::open(path.c_str(),
                               O_RDONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW));
        if (!reader) {
            return system_status("unable to open peer FIFO lane '" +
                                     selected.name + "'",
                                 path);
        }
        struct stat opened {};
        if (::fstat(reader.get(), &opened) != 0) {
            return system_status("unable to inspect opened peer FIFO lane '" +
                                     selected.name + "'",
                                 path);
        }
        if (!same_fifo(expected, opened) || !S_ISFIFO(opened.st_mode) ||
            opened.st_uid != ::geteuid() || (opened.st_mode & 0777U) != 0600U) {
            return Status{
                ErrorCode::io_error,
                "peer FIFO lane '" + selected.name +
                    "' changed or is not a private daemon-owned FIFO: " +
                    path.string()};
        }

        errno = 0;
        const long pipe_buf = ::fpathconf(reader.get(), _PC_PIPE_BUF);
        if (pipe_buf < 0L) {
            if (errno != 0) {
                return system_status(
                    "unable to query PIPE_BUF for peer FIFO lane '" +
                        selected.name + "'",
                    path);
            }
            return Status{
                ErrorCode::unsupported,
                "peer FIFO lane '" + selected.name +
                    "' has an indeterminate PIPE_BUF; atomic record contract cannot be enforced"};
        }
        const std::size_t required_atomic_bytes =
            selected.maximum_record_bytes + 1U;
        if (static_cast<unsigned long>(pipe_buf) < required_atomic_bytes) {
            return Status{
                ErrorCode::unsupported,
                "peer FIFO lane '" + selected.name + "' requires PIPE_BUF >= " +
                    std::to_string(required_atomic_bytes) + " but filesystem reports " +
                    std::to_string(pipe_buf)};
        }

        UniqueFd writer(::open(path.c_str(),
                               O_WRONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW));
        if (!writer) {
            return system_status("unable to hold peer FIFO lane '" +
                                     selected.name + "' open",
                                 path);
        }
        struct stat writer_opened {};
        if (::fstat(writer.get(), &writer_opened) != 0) {
            return system_status("unable to inspect peer FIFO lane '" +
                                     selected.name + "' hold writer",
                                 path);
        }
        if (!same_fifo(opened, writer_opened) ||
            !S_ISFIFO(writer_opened.st_mode) ||
            writer_opened.st_uid != ::geteuid() ||
            (writer_opened.st_mode & 0777U) != 0600U) {
            return Status{
                ErrorCode::io_error,
                "peer FIFO lane '" + selected.name +
                    "' changed while opening its hold writer: " + path.string()};
        }

        Fifo fifo;
        fifo.public_key = std::move(public_key);
        fifo.lane_index = lane_index;
        fifo.path = path;
        fifo.metadata = opened;
        fifo.pipe_buf = pipe_buf;
        fifo.read_descriptor = std::move(reader);
        fifo.hold_writer = std::move(writer);
        fifo.partial.reserve(selected.maximum_record_bytes);
        return fifo;
    }

    void scan_root_lanes() noexcept {
        try {
            std::set<FifoKey> present;
            const FifoKey global_scan_key{{}, config_.lanes.size() + 1U};
            for (std::size_t lane_index = 0U;
                 lane_index < config_.lanes.size(); ++lane_index) {
                const PeerFifoLane &selected = config_.lanes[lane_index];
                const FifoKey key{{}, lane_index};
                const std::filesystem::path path =
                    config_.peers_root / selected.name;
                struct stat metadata {};
                if (::lstat(path.c_str(), &metadata) != 0) {
                    if (errno != ENOENT) {
                        report_scan_error_once(
                            key, selected.name,
                            system_status("unable to inspect root FIFO lane '" +
                                              selected.name + "'",
                                          path));
                    } else {
                        scan_errors_.erase(key);
                    }
                    continue;
                }
                if (!S_ISFIFO(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
                    metadata.st_uid != ::geteuid() ||
                    (metadata.st_mode & 0777U) != 0600U) {
                    report_scan_error_once(
                        key, selected.name,
                        {ErrorCode::io_error,
                         "root FIFO lane '" + selected.name +
                             "' is not a private daemon-owned FIFO: " +
                             path.string()});
                    continue;
                }
                present.insert(key);
                auto existing = fifos_.find(key);
                if (existing != fifos_.end() &&
                    same_fifo(existing->second.metadata, metadata)) {
                    scan_errors_.erase(key);
                    continue;
                }
                if (existing != fifos_.end()) {
                    fifos_.erase(existing);
                }
                auto opened = open_fifo({}, lane_index, path, metadata);
                if (!opened) {
                    report_scan_error_once(key, selected.name, opened.status());
                    continue;
                }
                scan_errors_.erase(key);
                fifos_.emplace(key, std::move(opened).value());
            }
            for (auto iterator = fifos_.begin(); iterator != fifos_.end();) {
                if (!present.contains(iterator->first)) {
                    scan_errors_.erase(iterator->first);
                    iterator = fifos_.erase(iterator);
                } else {
                    ++iterator;
                }
            }
            scan_errors_.erase(global_scan_key);
            publish_counts();
        } catch (const std::exception &exception) {
            report_scan_error_once(
                FifoKey{{}, config_.lanes.size() + 1U}, {},
                {ErrorCode::internal_error,
                 "root FIFO scan failed: " + std::string(exception.what())});
        } catch (...) {
            report_scan_error_once(
                FifoKey{{}, config_.lanes.size() + 1U}, {},
                {ErrorCode::internal_error,
                 "root FIFO scan failed unexpectedly"});
        }
    }

    void scan_fifos() noexcept {
        if (config_.layout == PeerFifoLayout::root_lanes) {
            scan_root_lanes();
            return;
        }
        scan_peers();
    }

    void scan_peers() noexcept {
        try {
            std::set<FifoKey> present;
            std::set<std::string> seen_peers;
            const FifoKey global_scan_key{{}, config_.lanes.size() + 1U};
            std::error_code iterator_error;
            for (std::filesystem::directory_iterator iterator(
                     config_.peers_root, iterator_error),
                 end;
                 !iterator_error && iterator != end;
                 iterator.increment(iterator_error)) {
                const std::string public_key =
                    iterator->path().filename().string();
                if (!valid_public_key(public_key)) {
                    continue;
                }
                seen_peers.insert(public_key);
                const FifoKey directory_key{public_key, config_.lanes.size()};
                struct stat directory_metadata {};
                if (::lstat(iterator->path().c_str(), &directory_metadata) != 0 ||
                    !S_ISDIR(directory_metadata.st_mode) ||
                    S_ISLNK(directory_metadata.st_mode) ||
                    directory_metadata.st_uid != ::geteuid() ||
                    (directory_metadata.st_mode & 0077U) != 0U) {
                    report_scan_error_once(
                        directory_key, {},
                        {ErrorCode::io_error,
                         "peer FIFO directory is not a private real daemon-owned directory: " +
                             iterator->path().string()});
                    continue;
                }
                scan_errors_.erase(directory_key);

                for (std::size_t lane_index = 0U;
                     lane_index < config_.lanes.size(); ++lane_index) {
                    const PeerFifoLane &selected = config_.lanes[lane_index];
                    const FifoKey key{public_key, lane_index};
                    const std::filesystem::path path =
                        iterator->path() / selected.name;
                    struct stat metadata {};
                    if (::lstat(path.c_str(), &metadata) != 0) {
                        if (errno != ENOENT) {
                            report_scan_error_once(
                                key, selected.name,
                                system_status("unable to inspect peer FIFO lane '" +
                                                  selected.name + "'",
                                              path));
                        } else {
                            scan_errors_.erase(key);
                        }
                        continue;
                    }
                    if (!S_ISFIFO(metadata.st_mode) || S_ISLNK(metadata.st_mode) ||
                        metadata.st_uid != ::geteuid() ||
                        (metadata.st_mode & 0777U) != 0600U) {
                        report_scan_error_once(
                            key, selected.name,
                            {ErrorCode::io_error,
                             "peer FIFO lane '" + selected.name +
                                 "' is not a private daemon-owned FIFO: " +
                                 path.string()});
                        continue;
                    }
                    present.insert(key);
                    auto existing = fifos_.find(key);
                    if (existing != fifos_.end() &&
                        same_fifo(existing->second.metadata, metadata)) {
                        scan_errors_.erase(key);
                        continue;
                    }
                    if (existing != fifos_.end()) {
                        fifos_.erase(existing);
                    }
                    auto opened =
                        open_fifo(public_key, lane_index, path, metadata);
                    if (!opened) {
                        report_scan_error_once(
                            key, selected.name, opened.status());
                        continue;
                    }
                    scan_errors_.erase(key);
                    fifos_.emplace(key, std::move(opened).value());
                }
            }
            if (iterator_error) {
                report_scan_error_once(
                    global_scan_key, {},
                    {ErrorCode::io_error,
                     "unable to enumerate peer FIFO directories: " +
                         iterator_error.message()});
            }
            for (auto iterator = fifos_.begin(); iterator != fifos_.end();) {
                if (!present.contains(iterator->first)) {
                    scan_errors_.erase(iterator->first);
                    iterator = fifos_.erase(iterator);
                } else {
                    ++iterator;
                }
            }
            for (auto iterator = scan_errors_.begin();
                 iterator != scan_errors_.end();) {
                if (!iterator->first.public_key.empty() &&
                    !seen_peers.contains(iterator->first.public_key)) {
                    iterator = scan_errors_.erase(iterator);
                } else {
                    ++iterator;
                }
            }
            scan_errors_.erase(global_scan_key);
            publish_counts();
        } catch (const std::exception &exception) {
            report_scan_error_once(
                FifoKey{{}, config_.lanes.size() + 1U}, {},
                {ErrorCode::internal_error,
                 "peer FIFO scan failed: " + std::string(exception.what())});
        } catch (...) {
            report_scan_error_once(
                FifoKey{{}, config_.lanes.size() + 1U}, {},
                {ErrorCode::internal_error,
                 "peer FIFO scan failed unexpectedly"});
        }
    }

    void report_scan_error_once(const FifoKey &key,
                                std::string_view lane_name,
                                const Status &status) noexcept {
        const std::string fingerprint =
            std::to_string(static_cast<int>(status.code())) + ":" +
            status.message();
        const auto found = scan_errors_.find(key);
        if (found != scan_errors_.end() && found->second == fingerprint) {
            return;
        }
        scan_errors_[key] = fingerprint;
        report_error(key.public_key, lane_name, status);
    }

    void consume_byte(Fifo &fifo, std::uint8_t value) noexcept {
        const auto now = std::chrono::steady_clock::now();
        const PeerFifoLane &selected = lane(fifo);
        if (fifo.discarding) {
            if (value == static_cast<std::uint8_t>('\n')) {
                fifo.discarding = false;
                fifo.partial.clear();
                fifo.last_record_byte = {};
            } else {
                fifo.last_record_byte = now;
            }
            return;
        }
        if (value == static_cast<std::uint8_t>('\n')) {
            deliver(fifo);
            fifo.partial.clear();
            fifo.last_record_byte = {};
            return;
        }
        if (selected.policy == PeerFifoRecordPolicy::printable_ascii &&
            (value < 0x20U || value > 0x7EU)) {
            fifo.partial.clear();
            fifo.discarding = true;
            fifo.last_record_byte = now;
            report_error(
                fifo.public_key, selected.name,
                {ErrorCode::invalid_argument,
                 "peer FIFO lane '" + selected.name +
                     "' record contains a non-printable ASCII byte"});
            return;
        }
        if (fifo.partial.size() >= selected.maximum_record_bytes) {
            fifo.partial.clear();
            fifo.discarding = true;
            fifo.last_record_byte = now;
            report_error(
                fifo.public_key, selected.name,
                {ErrorCode::resource_exhausted,
                 "peer FIFO lane '" + selected.name + "' record exceeds " +
                     std::to_string(selected.maximum_record_bytes) + " bytes"});
            return;
        }
        fifo.partial.push_back(value);
        fifo.last_record_byte = now;
    }

    void expire_incomplete_records() noexcept {
        const auto now = std::chrono::steady_clock::now();
        for (auto &[key, fifo] : fifos_) {
            static_cast<void>(key);
            if (fifo.last_record_byte ==
                    std::chrono::steady_clock::time_point{} ||
                now - fifo.last_record_byte < config_.partial_record_timeout) {
                continue;
            }
            const bool was_discarding = fifo.discarding;
            const std::string lane_name = lane(fifo).name;
            fifo.partial.clear();
            fifo.discarding = false;
            fifo.last_record_byte = {};
            report_error(
                fifo.public_key, lane_name,
                {ErrorCode::invalid_argument,
                 std::string(was_discarding
                                 ? "unterminated rejected peer FIFO record expired in lane '"
                                 : "unterminated peer FIFO record expired in lane '") +
                     lane_name + "' after " +
                     std::to_string(config_.partial_record_timeout.count()) +
                     "ms"});
        }
    }

    void drain(Fifo &fifo) noexcept {
        std::array<std::uint8_t, 4096U> buffer{};
        while (!stop_requested_.load()) {
            ssize_t count = -1;
            do {
                count = ::read(fifo.read_descriptor.get(), buffer.data(),
                               buffer.size());
            } while (count < 0 && errno == EINTR);
            if (count > 0) {
                for (ssize_t index = 0; index < count; ++index) {
                    consume_byte(
                        fifo, buffer[static_cast<std::size_t>(index)]);
                }
                continue;
            }
            if (count == 0 || errno == EAGAIN || errno == EWOULDBLOCK) {
                return;
            }
            report_error(
                fifo.public_key, lane(fifo).name,
                system_status("unable to read peer FIFO lane '" +
                                  lane(fifo).name + "'",
                              fifo.path));
            return;
        }
    }

    void worker_main() noexcept {
        try {
            while (!stop_requested_.load()) {
                std::vector<struct pollfd> descriptors;
                std::vector<Fifo *> order;
                descriptors.reserve(fifos_.size() + 1U);
                order.reserve(fifos_.size());
                descriptors.push_back({wake_.get(), POLLIN, 0});
                for (auto &[key, fifo] : fifos_) {
                    static_cast<void>(key);
                    descriptors.push_back(
                        {fifo.read_descriptor.get(), POLLIN, 0});
                    order.push_back(&fifo);
                }
                int ready = -1;
                do {
                    ready = ::poll(
                        descriptors.data(),
                        static_cast<nfds_t>(descriptors.size()),
                        static_cast<int>(config_.rescan_interval.count()));
                } while (ready < 0 && errno == EINTR);
                if (ready < 0) {
                    report_error({}, {},
                                 system_status("peer FIFO poll failed"));
                    break;
                }
                if ((descriptors.front().revents & POLLIN) != 0) {
                    break;
                }
                for (std::size_t index = 0U; index < order.size(); ++index) {
                    const short revents = descriptors[index + 1U].revents;
                    if ((revents & POLLIN) != 0) {
                        drain(*order[index]);
                    }
                    if ((revents & (POLLERR | POLLNVAL)) != 0) {
                        report_error(
                            order[index]->public_key, lane(*order[index]).name,
                            {ErrorCode::io_error,
                             "peer FIFO poll reported an invalid descriptor for lane '" +
                                 lane(*order[index]).name + "'"});
                    }
                }
                expire_incomplete_records();
                scan_fifos();
            }
        } catch (const std::exception &exception) {
            report_error(
                {}, {},
                {ErrorCode::internal_error,
                 "peer FIFO worker failed: " +
                     std::string(exception.what())});
        } catch (...) {
            report_error(
                {}, {},
                {ErrorCode::internal_error,
                 "peer FIFO worker failed unexpectedly"});
        }
        running_.store(false);
    }

    void publish_counts() {
        std::vector<std::size_t> counts(config_.lanes.size(), 0U);
        for (const auto &[key, fifo] : fifos_) {
            static_cast<void>(key);
            if (fifo.lane_index < counts.size()) {
                ++counts[fifo.lane_index];
            }
        }
        std::scoped_lock lock(stats_mutex_);
        lane_fifo_counts_ = std::move(counts);
        total_fifo_count_ = fifos_.size();
    }

    void clear_fifos() {
        fifos_.clear();
        scan_errors_.clear();
        std::scoped_lock lock(stats_mutex_);
        lane_fifo_counts_.assign(config_.lanes.size(), 0U);
        total_fifo_count_ = 0U;
    }

    Config config_;
    Handler handler_;
    ErrorHandler error_handler_;
    std::atomic<bool> start_called_{false};
    std::atomic<bool> stop_requested_{false};
    std::atomic<bool> running_{false};
    UniqueFd wake_;
    std::thread worker_;
    std::map<FifoKey, Fifo> fifos_;
    std::map<FifoKey, std::string> scan_errors_;
    mutable std::mutex stats_mutex_;
    std::vector<std::size_t> lane_fifo_counts_;
    std::size_t total_fifo_count_{0U};
};

PeerFifoServer::PeerFifoServer(Config config, Handler handler,
                               ErrorHandler error_handler)
    : impl_(std::make_unique<Impl>(std::move(config), std::move(handler),
                                   std::move(error_handler))) {}
PeerFifoServer::~PeerFifoServer() = default;
Status PeerFifoServer::start() { return impl_->start(); }
void PeerFifoServer::stop() { impl_->stop(); }
bool PeerFifoServer::running() const noexcept { return impl_->running(); }
PeerFifoStats PeerFifoServer::stats() const { return impl_->stats(); }
std::size_t PeerFifoServer::monitored_fifo_count(
    std::string_view lane) const {
    return impl_->monitored_fifo_count(lane);
}
const std::filesystem::path &PeerFifoServer::peers_root() const noexcept {
    return impl_->peers_root();
}

std::string to_string(PeerFifoRecordPolicy policy) {
    switch (policy) {
        case PeerFifoRecordPolicy::printable_ascii:
            return "printable-ascii";
        case PeerFifoRecordPolicy::byte_line:
            return "byte-line";
    }
    return "unknown";
}

}  // namespace iotox::local
