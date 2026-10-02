#pragma once

#include "iotox/status.hpp"
#include "iotox/transport.hpp"

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace iotox {

inline constexpr std::size_t kQualifiedSingleAgentTransferCeiling = 32U;

enum class FileTransferDirection {
    outgoing,
    incoming,
};

enum class FileTransferState {
    offered,
    active,
    paused,
    completed,
    cancelled,
    failed,
};

struct FileTransferRecord {
    FileTransferDirection direction{FileTransferDirection::incoming};
    FileTransferState state{FileTransferState::offered};
    std::uint32_t friend_number{0U};
    std::uint32_t file_number{0U};
    std::uint32_t file_kind{toxcore::abi::kFileKindData};
    std::uint64_t file_size{0U};
    std::uint64_t position{0U};
    // c-toxcore keeps independent pause state for each side. A transfer moves
    // only when neither side is paused. Keeping both facts prevents a local
    // RESUME from falsely projecting an active transfer that the peer still
    // has paused.
    bool local_paused{false};
    bool peer_paused{false};
    FileId file_id{};
    bool has_file_id{false};
    std::vector<std::uint8_t> filename;
    std::filesystem::path local_path;
    std::string detail;

    [[nodiscard]] bool operator==(const FileTransferRecord &) const = default;
};

struct FileByteRange {
    std::uint64_t offset{0U};
    std::uint64_t length{0U};

    [[nodiscard]] bool operator==(const FileByteRange &) const = default;
};

struct FileCarrierStats {
    std::size_t window_per_peer{0U};
    std::uint64_t rotation_quantum_ms{0U};
    std::size_t runnable_receives{0U};
    std::size_t waiting_receives{0U};
    std::uint64_t admission_count{0U};
    std::uint64_t rotation_count{0U};
    std::uint64_t pause_count{0U};
    std::uint64_t resume_count{0U};
    std::uint64_t control_failure_count{0U};
    std::uint64_t total_wait_us{0U};
    std::uint64_t maximum_wait_us{0U};
};

// FileTransferManager turns c-toxcore's callback-oriented file API into explicit
// local filesystem operations. It intentionally supports only finite regular
// files in this revision. Incoming offers remain paused until receive_to_path()
// has acquired a private temporary file in the destination directory. A
// successful receive_to_path() result acknowledges local admission and either
// an accepted RESUME or a bounded carrier-window wait. Completion and safe
// publication are asynchronous and a tiny transfer may already be terminal
// when the result reaches its caller.
class FileTransferManager {
  public:
    struct Config {
        // Thirty-two is the qualified single-Agent ceiling. Larger explicit
        // values remain available for bounded experiments, but are not a
        // release-qualified way to add capacity (ADR 0165).
        std::size_t max_active_sends{
            kQualifiedSingleAgentTransferCeiling};
        std::size_t max_active_receives{
            kQualifiedSingleAgentTransferCeiling};
        std::size_t max_pending_offers{256U};
        std::uint64_t max_file_bytes{1024ULL * 1024ULL * 1024ULL};
        std::size_t max_chunk_bytes{4U * 1024U * 1024U};
        // Bound locally resumed incoming transfers per peer before toxcore's
        // shared reliable carrier is congested. Waiting transfers rotate in
        // oldest-first order without changing file bytes or protocol framing.
        std::size_t carrier_window_per_peer{1U};
        std::chrono::milliseconds carrier_rotation_quantum{50};
    };

    explicit FileTransferManager(ToxTransport &transport);
    FileTransferManager(ToxTransport &transport, Config config);
    ~FileTransferManager();

    FileTransferManager(const FileTransferManager &) = delete;
    FileTransferManager &operator=(const FileTransferManager &) = delete;
    FileTransferManager(FileTransferManager &&) = delete;
    FileTransferManager &operator=(FileTransferManager &&) = delete;

    [[nodiscard]] Result<FileTransferRecord> send_path(
        std::uint32_t friend_number, const std::filesystem::path &path);
    // Offers path with an application-chosen Tox file ID. This is the
    // correlation primitive used by protocols which must bind a prior signed
    // request to a later file offer without trusting the remote filename.
    [[nodiscard]] Result<FileTransferRecord> send_path_with_file_id(
        std::uint32_t friend_number, const std::filesystem::path &path,
        const FileId &file_id);
    // Offers the canonical concatenation of nonempty, sorted, nonoverlapping,
    // nonadjacent source ranges under one explicit FileId. The source is held
    // open and mutation-checked for the transfer lifetime; no temporary bundle
    // is materialized on disk.
    [[nodiscard]] Result<FileTransferRecord> send_path_ranges_with_file_id(
        std::uint32_t friend_number, const std::filesystem::path &path,
        std::span<const FileByteRange> ranges, const FileId &file_id);
    [[nodiscard]] Result<FileTransferRecord> receive_to_path(
        std::uint32_t friend_number, std::uint32_t file_number,
        const std::filesystem::path &destination);
    // Receives an offered full-size file into an exact existing private
    // prefix. Offset zero admits an empty caller-owned partial without a Tox
    // seek; a nonzero offset seeks before resume.
    // The prefix inode is written in place and intentionally preserved on
    // cancellation/loss; the caller must authenticate the complete file
    // before publication and explicitly remove an unusable prefix.
    [[nodiscard]] Result<FileTransferRecord> receive_to_path_from_offset(
        std::uint32_t friend_number, std::uint32_t file_number,
        const std::filesystem::path &destination,
        std::uint64_t resume_offset);
    [[nodiscard]] Result<FileTransferRecord> control(
        std::uint32_t friend_number, std::uint32_t file_number,
        TransferControl control);
    [[nodiscard]] Status cancel(
        std::uint32_t friend_number, std::uint32_t file_number);
    // Close one incoming receive and retire its local destination without
    // attempting a transport control. This is the loss-path primitive used
    // after a carrier has already become unreachable. It is idempotent so a
    // transport-owned offline event and its parent lifecycle fence may race
    // without reopening or retaining the receive resource.
    [[nodiscard]] Status retire_incoming(
        std::uint32_t friend_number, std::uint32_t file_number);

    // Called by the single Agent event pump. The manager may synchronously
    // answer chunk requests through the transport owner thread.
    [[nodiscard]] Status handle_event(const TransportEvent &event);

    // Called periodically outside the transport callback. It admits waiting
    // receives and performs at most one due pause/resume rotation per peer.
    [[nodiscard]] Status service_carrier();

    [[nodiscard]] std::vector<FileTransferRecord> list() const;
    [[nodiscard]] FileCarrierStats stats() const;
    void stop() noexcept;

  private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

[[nodiscard]] std::string to_string(FileTransferDirection direction);
[[nodiscard]] std::string to_string(FileTransferState state);
[[nodiscard]] std::string render_file_transfer(const FileTransferRecord &record);

}  // namespace iotox
