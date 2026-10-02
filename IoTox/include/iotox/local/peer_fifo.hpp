#pragma once

#include "iotox/status.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace iotox::local {

// A lane describes one private FIFO projected into every live peer directory.
// `printable_ascii` is suitable for tiny operation names. `byte_line` preserves
// every byte other than the LF record delimiter. Encoding and interoperability
// rules belong to the semantic lane above this framing service.
enum class PeerFifoRecordPolicy {
    printable_ascii,
    byte_line,
};

// Most lanes live below a canonical uppercase Tox public-key directory. A
// small number of process-wide entrances, such as the outgoing friend-request
// lane, live directly below the configured private root. Both layouts retain
// the same framing, inode, ownership, mode, timeout, and PIPE_BUF contract.
enum class PeerFifoLayout {
    public_key_directories,
    root_lanes,
};

struct PeerFifoLane {
    std::string name;
    std::size_t maximum_record_bytes{0U};
    bool allow_empty{false};
    PeerFifoRecordPolicy policy{PeerFifoRecordPolicy::byte_line};

    [[nodiscard]] bool operator==(const PeerFifoLane &) const = default;
};

struct PeerFifoStats {
    bool running{false};
    std::size_t total_fifo_count{0U};
    std::vector<std::pair<std::string, std::size_t>> lane_fifo_counts;
};

// PeerFifoServer is a framed local ingress adapter. It owns no durable queue,
// no Tox object, and no product semantics. Each complete LF-delimited record is
// handed synchronously to the Agent. Kernel FIFO buffering is backpressure, not
// authoritative storage. A conforming producer writes one whole record, LF
// included, in one write no larger than the FIFO's reported PIPE_BUF.
class PeerFifoServer {
  public:
    using Handler = std::function<void(
        std::string_view public_key, std::string_view lane,
        std::span<const std::uint8_t> record)>;
    using ErrorHandler = std::function<void(
        std::string_view public_key, std::string_view lane,
        const Status &status)>;

    struct Config {
        std::filesystem::path peers_root;
        PeerFifoLayout layout{PeerFifoLayout::public_key_directories};
        std::vector<PeerFifoLane> lanes;
        std::chrono::milliseconds rescan_interval{
            std::chrono::milliseconds(100)};
        // FIFO writer boundaries are not observable. An incomplete record must
        // expire before a later writer can accidentally complete it.
        std::chrono::milliseconds partial_record_timeout{
            std::chrono::seconds(2)};
    };

    PeerFifoServer(Config config, Handler handler,
                   ErrorHandler error_handler = {});
    ~PeerFifoServer();

    PeerFifoServer(const PeerFifoServer &) = delete;
    PeerFifoServer &operator=(const PeerFifoServer &) = delete;
    PeerFifoServer(PeerFifoServer &&) = delete;
    PeerFifoServer &operator=(PeerFifoServer &&) = delete;

    [[nodiscard]] Status start();
    void stop();

    [[nodiscard]] bool running() const noexcept;
    [[nodiscard]] PeerFifoStats stats() const;
    [[nodiscard]] std::size_t monitored_fifo_count(
        std::string_view lane) const;
    [[nodiscard]] const std::filesystem::path &peers_root() const noexcept;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] std::string to_string(PeerFifoRecordPolicy policy);

}  // namespace iotox::local
