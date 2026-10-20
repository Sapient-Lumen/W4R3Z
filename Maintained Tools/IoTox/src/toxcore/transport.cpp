#include "iotox/transport.hpp"

#include "iotox/latency_histogram.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"
#include "iotox/toxcore/dynamic_library.hpp"
#include "iotox/version.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <condition_variable>
#include <deque>
#include <exception>
#include <functional>
#include <future>
#include <iomanip>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <sstream>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <utility>

namespace iotox {
namespace {

std::string hex_encode(const std::uint8_t *data, std::size_t size) {
    std::ostringstream output;
    output << std::hex << std::setfill('0') << std::uppercase;
    for (std::size_t index = 0U; index < size; ++index) {
        output << std::setw(2) << static_cast<unsigned int>(data[index]);
    }
    return output.str();
}

bool valid_lossless_packet_id(std::uint8_t value) {
    return value == 69U || (value >= 160U && value <= 191U);
}

bool valid_lossy_packet_id(std::uint8_t value) {
    // 192..199 are reserved to ToxAV/conference traffic. Public IoTox
    // callers may use only c-toxcore's custom application range.
    return value >= 200U && value <= 254U;
}

void saturating_increment(std::uint64_t &value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) {
        ++value;
    }
}

void saturating_add(std::uint64_t &value, std::uint64_t increment) noexcept {
    value = increment > std::numeric_limits<std::uint64_t>::max() - value
        ? std::numeric_limits<std::uint64_t>::max()
        : value + increment;
}

// std::function copies its closure while a command crosses to toxcore's owner
// thread. Capturing a vector directly therefore leaves one or more ordinary
// heap buffers behind after deallocation. A shared wiping payload keeps a
// single byte allocation across those closure copies and clears it when the
// final command reference is released, including cancellation paths.
class SensitivePacketPayload {
  public:
    explicit SensitivePacketPayload(std::span<const std::uint8_t> packet)
        : bytes_(packet.begin(), packet.end()) {}

    ~SensitivePacketPayload() {
        security::secure_wipe(bytes_);
        bytes_.clear();
    }

    SensitivePacketPayload(const SensitivePacketPayload &) = delete;
    SensitivePacketPayload &operator=(const SensitivePacketPayload &) = delete;
    SensitivePacketPayload(SensitivePacketPayload &&) = delete;
    SensitivePacketPayload &operator=(SensitivePacketPayload &&) = delete;

    [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept {
        return bytes_;
    }

  private:
    std::vector<std::uint8_t> bytes_;
};

Status text_message_failure(toxcore::abi::FriendSendMessageError error) {
    const std::string suffix =
        " (c-toxcore error " + std::to_string(static_cast<int>(error)) + ")";
    if (error == toxcore::abi::kFriendSendMessageFriendNotFound) {
        return Status{ErrorCode::not_found,
                      "text-message peer does not exist" + suffix};
    }
    if (error == toxcore::abi::kFriendSendMessageFriendNotConnected) {
        return Status{ErrorCode::unavailable,
                      "text-message peer is not connected" + suffix};
    }
    if (error == toxcore::abi::kFriendSendMessageSendQueueFull) {
        return Status{ErrorCode::resource_exhausted,
                      "c-toxcore text send queue is full; retry after iteration" +
                          suffix};
    }
    if (error == toxcore::abi::kFriendSendMessageNull ||
        error == toxcore::abi::kFriendSendMessageTooLong ||
        error == toxcore::abi::kFriendSendMessageEmpty) {
        return Status{ErrorCode::invalid_argument,
                      "c-toxcore rejected the text-message contract" + suffix};
    }
    return Status{ErrorCode::library_error,
                  "tox_friend_send_message failed" + suffix};
}

Status custom_packet_failure(
    toxcore::abi::FriendCustomPacketError error, std::string_view carrier) {
    const std::string suffix =
        " (c-toxcore error " + std::to_string(static_cast<int>(error)) + ")";
    if (error == toxcore::abi::kFriendCustomPacketFriendNotFound) {
        return Status{ErrorCode::not_found,
                      std::string(carrier) + "-packet peer does not exist" + suffix};
    }
    if (error == toxcore::abi::kFriendCustomPacketFriendNotConnected) {
        return Status{ErrorCode::unavailable,
                      std::string(carrier) + "-packet peer is not connected" + suffix};
    }
    if (error == toxcore::abi::kFriendCustomPacketSendQueueFull) {
        return Status{ErrorCode::resource_exhausted,
                      "c-toxcore " + std::string(carrier) +
                          " send queue is full; retry after iteration" +
                          suffix};
    }
    if (error == toxcore::abi::kFriendCustomPacketNull ||
        error == toxcore::abi::kFriendCustomPacketInvalid ||
        error == toxcore::abi::kFriendCustomPacketEmpty ||
        error == toxcore::abi::kFriendCustomPacketTooLong) {
        return Status{ErrorCode::invalid_argument,
                      "c-toxcore rejected the " + std::string(carrier) +
                          " packet contract" + suffix};
    }
    return Status{ErrorCode::library_error,
                  "tox_friend_send_" + std::string(carrier) +
                      "_packet failed" + suffix};
}

Status file_chunk_failure(toxcore::abi::FileSendChunkError error) {
    const std::string suffix =
        " (c-toxcore error " + std::to_string(static_cast<int>(error)) + ")";
    if (error == toxcore::abi::kFileSendChunkFriendNotFound ||
        error == toxcore::abi::kFileSendChunkNotFound) {
        return Status{ErrorCode::not_found,
                      "c-toxcore file transfer does not exist" + suffix};
    }
    if (error == toxcore::abi::kFileSendChunkFriendNotConnected ||
        error == toxcore::abi::kFileSendChunkNotTransferring) {
        return Status{ErrorCode::unavailable,
                      "c-toxcore file transfer is not active" + suffix};
    }
    if (error == toxcore::abi::kFileSendChunkSendQueueFull) {
        return Status{ErrorCode::resource_exhausted,
                      "c-toxcore file send queue is full" + suffix};
    }
    if (error == toxcore::abi::kFileSendChunkNull ||
        error == toxcore::abi::kFileSendChunkInvalidLength ||
        error == toxcore::abi::kFileSendChunkWrongPosition) {
        return Status{ErrorCode::invalid_argument,
                      "c-toxcore rejected the file-chunk contract" + suffix};
    }
    return Status{ErrorCode::library_error,
                  "tox_file_send_chunk failed" + suffix};
}

bool event_requires_delivery(TransportEventKind kind) {
    switch (kind) {
        case TransportEventKind::friend_request:
        case TransportEventKind::friend_added:
        case TransportEventKind::friend_removed:
        case TransportEventKind::friend_connection:
        case TransportEventKind::friend_name:
        case TransportEventKind::friend_status_message:
        case TransportEventKind::friend_status:
        case TransportEventKind::friend_typing:
        case TransportEventKind::message_sent:
        case TransportEventKind::friend_message:
        case TransportEventKind::friend_read_receipt:
        case TransportEventKind::lossless_packet:
        case TransportEventKind::file_offer:
        case TransportEventKind::file_control:
        case TransportEventKind::file_chunk_request:
        case TransportEventKind::file_chunk:
            return true;
        case TransportEventKind::backend_ready:
        case TransportEventKind::self_connection:
        case TransportEventKind::bootstrap:
        case TransportEventKind::tcp_relay:
        case TransportEventKind::lossy_packet:
        case TransportEventKind::diagnostic:
            return false;
    }
    return false;
}

toxcore::abi::FileControl to_abi_control(TransferControl control) {
    switch (control) {
        case TransferControl::resume:
            return toxcore::abi::kFileControlResume;
        case TransferControl::pause:
            return toxcore::abi::kFileControlPause;
        case TransferControl::cancel:
            return toxcore::abi::kFileControlCancel;
    }
    return toxcore::abi::kFileControlCancel;
}

std::optional<TransferControl> from_abi_control(
    toxcore::abi::FileControl control) {
    if (control == toxcore::abi::kFileControlResume) {
        return TransferControl::resume;
    }
    if (control == toxcore::abi::kFileControlPause) {
        return TransferControl::pause;
    }
    if (control == toxcore::abi::kFileControlCancel) {
        return TransferControl::cancel;
    }
    return std::nullopt;
}

toxcore::abi::UserStatus to_abi_status(PresenceStatus status) {
    switch (status) {
        case PresenceStatus::available:
            return toxcore::abi::kUserStatusNone;
        case PresenceStatus::away:
            return toxcore::abi::kUserStatusAway;
        case PresenceStatus::busy:
            return toxcore::abi::kUserStatusBusy;
    }
    return toxcore::abi::kUserStatusNone;
}

PresenceStatus from_abi_status(toxcore::abi::UserStatus status) {
    if (status == toxcore::abi::kUserStatusAway) {
        return PresenceStatus::away;
    }
    if (status == toxcore::abi::kUserStatusBusy) {
        return PresenceStatus::busy;
    }
    return PresenceStatus::available;
}

toxcore::abi::MessageType to_abi_message_type(TextMessageKind kind) {
    return kind == TextMessageKind::action ? toxcore::abi::kMessageTypeAction
                                           : toxcore::abi::kMessageTypeNormal;
}

std::optional<TextMessageKind> from_abi_message_type(
    toxcore::abi::MessageType kind) {
    if (kind == toxcore::abi::kMessageTypeNormal) {
        return TextMessageKind::normal;
    }
    if (kind == toxcore::abi::kMessageTypeAction) {
        return TextMessageKind::action;
    }
    return std::nullopt;
}

std::uint64_t text_message_key(
    toxcore::abi::FriendNumber friend_number,
    toxcore::abi::FriendMessageId message_id) {
    return (static_cast<std::uint64_t>(friend_number) << 32U) |
           static_cast<std::uint64_t>(message_id);
}

std::uint64_t file_transfer_key(
    toxcore::abi::FriendNumber friend_number,
    toxcore::abi::FileNumber file_number) {
    return (static_cast<std::uint64_t>(friend_number) << 32U) |
           static_cast<std::uint64_t>(file_number);
}

enum class CommandStage {
    queued,
    started,
    cancelled,
    finished,
};

class OwnerCommandBase {
  public:
    explicit OwnerCommandBase(TransportTrafficClass traffic_class)
        : traffic_class_(traffic_class), queued_at_(std::chrono::steady_clock::now()) {}
    virtual ~OwnerCommandBase() = default;
    virtual bool execute() noexcept = 0;
    virtual bool cancel(const Status &reason) noexcept = 0;

    [[nodiscard]] TransportTrafficClass traffic_class() const noexcept {
        return traffic_class_;
    }
    [[nodiscard]] std::chrono::steady_clock::time_point queued_at() const noexcept {
        return queued_at_;
    }

  private:
    TransportTrafficClass traffic_class_;
    std::chrono::steady_clock::time_point queued_at_;
};

template <typename T>
class OwnerCommand final : public OwnerCommandBase {
  public:
    using Operation = std::function<T()>;
    using ErrorFactory = std::function<T(const Status &)>;

    OwnerCommand(
        TransportTrafficClass traffic_class, Operation operation,
        ErrorFactory error_factory)
        : OwnerCommandBase(traffic_class),
          operation_(std::move(operation)),
          error_factory_(std::move(error_factory)) {}

    [[nodiscard]] std::future<T> future() { return promise_.get_future(); }

    bool execute() noexcept override {
        CommandStage expected = CommandStage::queued;
        if (!stage_.compare_exchange_strong(expected, CommandStage::started)) {
            return false;
        }
        try {
            promise_.set_value(operation_());
        } catch (...) {
            try {
                promise_.set_exception(std::current_exception());
            } catch (...) {
                // A promise may already have been satisfied only if this class is
                // broken. There is no useful recovery on the owner thread.
            }
        }
        stage_.store(CommandStage::finished);
        return true;
    }

    bool cancel(const Status &reason) noexcept override {
        CommandStage expected = CommandStage::queued;
        if (!stage_.compare_exchange_strong(expected, CommandStage::cancelled)) {
            return false;
        }
        try {
            promise_.set_value(error_factory_(reason));
        } catch (...) {
            try {
                promise_.set_exception(std::current_exception());
            } catch (...) {
            }
        }
        return true;
    }

  private:
    std::atomic<CommandStage> stage_{CommandStage::queued};
    std::promise<T> promise_;
    Operation operation_;
    ErrorFactory error_factory_;
};

}  // namespace

class ToxTransport::Impl {
    struct FileChunkSourceState {
        FileChunkSource source;
        std::uint64_t file_size{0U};
    };

    struct PacedFile {
        toxcore::abi::FriendNumber friend_number{0U};
        toxcore::abi::FileNumber file_number{0U};
        std::chrono::steady_clock::time_point paused_at{};
    };

    struct PendingFilePause {
        toxcore::abi::FriendNumber friend_number{0U};
        toxcore::abi::FileNumber file_number{0U};
    };

  public:
    explicit Impl(Config config)
        : config_(std::move(config)),
          maximum_iteration_interval_ms_(static_cast<std::uint32_t>(
              config_.maximum_iteration_interval.count())) {}

    ~Impl() { stop(); }

    Status expect_public_key(
        const std::array<std::uint8_t, toxcore::abi::kPublicKeySize> &key) {
        if (start_called_.load()) {
            return Status{ErrorCode::invalid_argument,
                          "expected Tox public key cannot change after start"};
        }
        if (config_.expected_public_key && config_.expected_public_key != key) {
            return Status{ErrorCode::protocol_error,
                          "conflicting expected Tox public keys were configured"};
        }
        config_.expected_public_key = key;
        return Status::success();
    }

    Status start() {
        bool expected = false;
        if (!start_called_.compare_exchange_strong(expected, true)) {
            return Status{ErrorCode::invalid_argument,
                          "Tox transport start() may only be called once"};
        }

        stop_requested_.store(false);
        std::future<Status> startup = startup_promise_.get_future();
        worker_ = std::thread([this] { worker_main(); });
        Status status = startup.get();
        if (!status.ok() && worker_.joinable()) {
            worker_.join();
        }
        return status;
    }

    void stop() {
        stop_requested_.store(true);
        cancel_pending_commands(
            Status{ErrorCode::unavailable, "Tox transport is stopping"});
        command_cv_.notify_all();
        event_cv_.notify_all();
        event_space_cv_.notify_all();
        if (worker_.joinable() && worker_.get_id() != std::this_thread::get_id()) {
            worker_.join();
        }
    }

    Status set_maximum_iteration_interval(
        std::chrono::milliseconds interval) {
        if (interval < std::chrono::milliseconds{1} ||
            interval > std::chrono::milliseconds{1000}) {
            return Status{
                ErrorCode::invalid_argument,
                "maximum toxcore iteration interval must be between 1 and 1000 ms"};
        }
        {
            std::scoped_lock lock(command_mutex_);
            maximum_iteration_interval_ms_.store(
                static_cast<std::uint32_t>(interval.count()));
            iteration_interval_changed_ = true;
        }
        command_cv_.notify_one();
        return Status::success();
    }

    [[nodiscard]] bool running() const noexcept { return running_.load(); }

    [[nodiscard]] std::string address_hex() const {
        std::scoped_lock lock(identity_mutex_);
        return address_hex_;
    }

    Result<SelfProfile> self_profile() {
        return invoke_owner<Result<SelfProfile>>(
            [this] { return self_profile_on_owner_thread(); },
            [](const Status &status) { return Result<SelfProfile>{status}; });
    }

    Status set_self_name(const std::vector<std::uint8_t> &name) {
        if (name.size() > toxcore::abi::kMaxNameLength) {
            return Status{ErrorCode::invalid_argument,
                          "Tox name exceeds 128 bytes"};
        }
        return invoke_owner<Status>(
            [this, name] {
                toxcore::abi::SetInfoError error = toxcore::abi::kSetInfoOk;
                const std::uint8_t *data = name.empty() ? nullptr : name.data();
                const bool changed = library_->api().self_set_name(
                    tox_, data, name.size(), &error);
                if (!changed || error != toxcore::abi::kSetInfoOk) {
                    return Status{ErrorCode::library_error,
                                  "tox_self_set_name failed with error " +
                                      std::to_string(static_cast<int>(error))};
                }
                if (config_.save_state_after_mutation) {
                    const Status saved = save_state_on_owner_thread();
                    if (!saved.ok()) {
                        return saved;
                    }
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status set_self_status_message(
        const std::vector<std::uint8_t> &status_message) {
        if (status_message.size() > toxcore::abi::kMaxStatusMessageLength) {
            return Status{ErrorCode::invalid_argument,
                          "Tox status message exceeds 1007 bytes"};
        }
        return invoke_owner<Status>(
            [this, status_message] {
                toxcore::abi::SetInfoError error = toxcore::abi::kSetInfoOk;
                const std::uint8_t *data =
                    status_message.empty() ? nullptr : status_message.data();
                const bool changed = library_->api().self_set_status_message(
                    tox_, data, status_message.size(), &error);
                if (!changed || error != toxcore::abi::kSetInfoOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_self_set_status_message failed with error " +
                            std::to_string(static_cast<int>(error))};
                }
                if (config_.save_state_after_mutation) {
                    const Status saved = save_state_on_owner_thread();
                    if (!saved.ok()) {
                        return saved;
                    }
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status set_self_status(PresenceStatus status) {
        return invoke_owner<Status>(
            [this, status] {
                library_->api().self_set_status(tox_, to_abi_status(status));
                if (config_.save_state_after_mutation) {
                    const Status saved = save_state_on_owner_thread();
                    if (!saved.ok()) {
                        return saved;
                    }
                }
                return Status::success();
            },
            [](const Status &operation_status) { return operation_status; });
    }

    Result<std::uint32_t> request_friend(
        const std::vector<std::uint8_t> &address,
        const std::vector<std::uint8_t> &message) {
        if (address.size() != toxcore::abi::kAddressSize) {
            return Status{ErrorCode::invalid_argument,
                          "Tox address must contain exactly 38 bytes"};
        }
        if (message.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "Tox friend request message may not be empty"};
        }
        if (message.size() > toxcore::abi::kMaxFriendRequestLength) {
            return Status{ErrorCode::invalid_argument,
                          "Tox friend request message exceeds 921 bytes"};
        }

        return invoke_owner<Result<std::uint32_t>>(
            [this, address, message] {
                toxcore::abi::FriendAddError error = toxcore::abi::kFriendAddOk;
                const toxcore::abi::FriendNumber friend_number =
                    library_->api().friend_add(
                        tox_, address.data(), message.data(), message.size(), &error);
                if (error != toxcore::abi::kFriendAddOk ||
                    friend_number == toxcore::abi::kFriendNumberFailure) {
                    return Result<std::uint32_t>{
                        Status{ErrorCode::library_error,
                               "tox_friend_add failed with error " +
                                   std::to_string(static_cast<int>(error))}};
                }
                friend_connections_[friend_number] = toxcore::abi::kConnectionNone;
                friend_statuses_[friend_number] = PresenceStatus::available;
                friend_typing_[friend_number] = false;
                TransportEvent event;
                event.kind = TransportEventKind::friend_added;
                event.friend_number = friend_number;
                event.public_key.assign(
                    address.begin(),
                    address.begin() +
                        static_cast<std::ptrdiff_t>(toxcore::abi::kPublicKeySize));
                event.message =
                    "outgoing Tox friend request recorded; no IoTox authority granted";
                emit(std::move(event));
                if (config_.save_state_after_mutation) {
                    static_cast<void>(save_state_on_owner_thread());
                }
                return Result<std::uint32_t>{static_cast<std::uint32_t>(friend_number)};
            },
            [](const Status &status) { return Result<std::uint32_t>{status}; });
    }

    Result<std::uint32_t> accept_friend(
        const std::vector<std::uint8_t> &public_key) {
        if (public_key.size() != toxcore::abi::kPublicKeySize) {
            return Status{ErrorCode::invalid_argument,
                          "Tox public key must contain exactly 32 bytes"};
        }

        return invoke_owner<Result<std::uint32_t>>(
            [this, public_key] {
                toxcore::abi::FriendAddError error = toxcore::abi::kFriendAddOk;
                const toxcore::abi::FriendNumber friend_number =
                    library_->api().friend_add_norequest(
                        tox_, public_key.data(), &error);
                if (error != toxcore::abi::kFriendAddOk ||
                    friend_number == toxcore::abi::kFriendNumberFailure) {
                    return Result<std::uint32_t>{
                        Status{ErrorCode::library_error,
                               "tox_friend_add_norequest failed with error " +
                                   std::to_string(static_cast<int>(error))}};
                }
                friend_connections_[friend_number] = toxcore::abi::kConnectionNone;
                friend_statuses_[friend_number] = PresenceStatus::available;
                friend_typing_[friend_number] = false;
                TransportEvent event;
                event.kind = TransportEventKind::friend_added;
                event.friend_number = friend_number;
                event.public_key = public_key;
                event.message =
                    "Tox friend accepted; no IoTox authority granted";
                emit(std::move(event));
                if (config_.save_state_after_mutation) {
                    static_cast<void>(save_state_on_owner_thread());
                }
                return Result<std::uint32_t>{static_cast<std::uint32_t>(friend_number)};
            },
            [](const Status &status) { return Result<std::uint32_t>{status}; });
    }

    void finish_friend_removal(
        toxcore::abi::FriendNumber friend_number,
        std::vector<std::uint8_t> public_key) {
        friend_connections_.erase(friend_number);
        friend_statuses_.erase(friend_number);
        friend_typing_.erase(friend_number);
        static_cast<void>(erase_sent_text_receipts_for_friend(friend_number));
        static_cast<void>(erase_file_chunk_sources_for_friend(friend_number));
        emit({TransportEventKind::friend_removed,
              friend_number,
              static_cast<int>(toxcore::abi::kConnectionNone),
              std::move(public_key),
              {},
              "Tox friend removed; application authorization must be revoked separately"});
        if (config_.save_state_after_mutation) {
            static_cast<void>(save_state_on_owner_thread());
        }
    }

    Status remove_friend(std::uint32_t friend_number) {
        return invoke_owner<Status>(
            [this, friend_number] {
                std::vector<std::uint8_t> public_key(
                    toxcore::abi::kPublicKeySize, 0U);
                toxcore::abi::FriendGetPublicKeyError key_error =
                    toxcore::abi::kFriendGetPublicKeyOk;
                const bool key_read = library_->api().friend_get_public_key(
                    tox_, friend_number, public_key.data(), &key_error);
                if (!key_read ||
                    key_error != toxcore::abi::kFriendGetPublicKeyOk) {
                    return Status{
                        ErrorCode::not_found,
                        "toxcore friend number does not currently identify a friend"};
                }

                toxcore::abi::FriendDeleteError error =
                    toxcore::abi::kFriendDeleteOk;
                const bool removed = library_->api().friend_delete(
                    tox_, friend_number, &error);
                if (!removed || error != toxcore::abi::kFriendDeleteOk) {
                    return Status{
                        error == toxcore::abi::kFriendDeleteNotFound
                            ? ErrorCode::not_found
                            : ErrorCode::library_error,
                        "tox_friend_delete failed with error " +
                            std::to_string(static_cast<int>(error))};
                }
                finish_friend_removal(friend_number, std::move(public_key));
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Result<std::uint32_t> remove_friend_by_public_key(
        const std::vector<std::uint8_t> &public_key) {
        if (public_key.size() != toxcore::abi::kPublicKeySize) {
            return Status{ErrorCode::invalid_argument,
                          "Tox public key must contain exactly 32 bytes"};
        }
        return invoke_owner<Result<std::uint32_t>>(
            [this, public_key] {
                toxcore::abi::FriendByPublicKeyError lookup_error =
                    toxcore::abi::kFriendByPublicKeyOk;
                const toxcore::abi::FriendNumber friend_number =
                    library_->api().friend_by_public_key(
                        tox_, public_key.data(), &lookup_error);
                if (lookup_error != toxcore::abi::kFriendByPublicKeyOk ||
                    friend_number == toxcore::abi::kFriendNumberFailure) {
                    return Result<std::uint32_t>{Status{
                        lookup_error == toxcore::abi::kFriendByPublicKeyNotFound
                            ? ErrorCode::not_found
                            : ErrorCode::library_error,
                        "tox_friend_by_public_key failed with error " +
                            std::to_string(static_cast<int>(lookup_error))}};
                }

                toxcore::abi::FriendDeleteError delete_error =
                    toxcore::abi::kFriendDeleteOk;
                const bool removed = library_->api().friend_delete(
                    tox_, friend_number, &delete_error);
                if (!removed ||
                    delete_error != toxcore::abi::kFriendDeleteOk) {
                    return Result<std::uint32_t>{Status{
                        delete_error == toxcore::abi::kFriendDeleteNotFound
                            ? ErrorCode::not_found
                            : ErrorCode::library_error,
                        "tox_friend_delete failed after public-key lookup with error " +
                            std::to_string(static_cast<int>(delete_error))}};
                }
                finish_friend_removal(friend_number, public_key);
                return Result<std::uint32_t>{
                    static_cast<std::uint32_t>(friend_number)};
            },
            [](const Status &status) {
                return Result<std::uint32_t>{status};
            });
    }

    Result<std::vector<TransportPeer>> list_friends() {
        return invoke_owner<Result<std::vector<TransportPeer>>>(
            [this] { return list_friends_on_owner_thread(); },
            [](const Status &status) {
                return Result<std::vector<TransportPeer>>{status};
            });
    }

    Result<std::uint32_t> send_message(
        std::uint32_t friend_number, TextMessageKind kind,
        const std::vector<std::uint8_t> &message) {
        if (message.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "Tox text message may not be empty"};
        }
        if (message.size() > toxcore::abi::kMaxMessageLength) {
            return Status{ErrorCode::invalid_argument,
                          "Tox text message exceeds 1372 bytes"};
        }

        return invoke_owner<Result<std::uint32_t>>(
            TransportTrafficClass::interactive,
            [this, friend_number, kind, message] {
                toxcore::abi::FriendSendMessageError error =
                    toxcore::abi::kFriendSendMessageOk;
                const toxcore::abi::FriendMessageId message_id =
                    library_->api().friend_send_message(
                        tox_, friend_number, to_abi_message_type(kind),
                        message.data(), message.size(), &error);
                if (error != toxcore::abi::kFriendSendMessageOk) {
                    return Result<std::uint32_t>{text_message_failure(error)};
                }
                sent_message_kinds_[text_message_key(friend_number, message_id)] =
                    kind;
                TransportEvent event;
                event.kind = TransportEventKind::message_sent;
                event.friend_number = friend_number;
                event.text_kind = kind;
                event.message_id = message_id;
                event.data = message;
                event.message =
                    "text message accepted by c-toxcore; read receipt is separate";
                emit(std::move(event));
                return Result<std::uint32_t>{
                    static_cast<std::uint32_t>(message_id)};
            },
            [](const Status &status) { return Result<std::uint32_t>{status}; });
    }

    Status set_typing(std::uint32_t friend_number, bool typing) {
        return invoke_owner<Status>(
            TransportTrafficClass::interactive,
            [this, friend_number, typing] {
                toxcore::abi::SetTypingError error = toxcore::abi::kSetTypingOk;
                const bool changed = library_->api().self_set_typing(
                    tox_, friend_number, typing, &error);
                if (!changed || error != toxcore::abi::kSetTypingOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_self_set_typing failed with error " +
                            std::to_string(static_cast<int>(error))};
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status send_lossless(
        std::uint32_t friend_number,
        const std::vector<std::uint8_t> &packet,
        TransportTrafficClass traffic_class) {
        if (packet.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "lossless packet may not be empty"};
        }
        if (packet.size() > toxcore::abi::kMaxCustomPacketSize) {
            return Status{ErrorCode::invalid_argument,
                          "lossless packet exceeds c-toxcore capacity"};
        }
        if (!valid_lossless_packet_id(packet.front())) {
            return Status{
                ErrorCode::invalid_argument,
                "first lossless packet byte is outside c-toxcore's application ranges"};
        }

        return invoke_owner<Status>(
            traffic_class,
            [this, friend_number, packet] {
                toxcore::abi::FriendCustomPacketError error =
                    toxcore::abi::kFriendCustomPacketOk;
                const bool sent = library_->api().friend_send_lossless_packet(
                    tox_, friend_number, packet.data(), packet.size(), &error);
                if (!sent || error != toxcore::abi::kFriendCustomPacketOk) {
                    return custom_packet_failure(error, "lossless");
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status send_sensitive_lossless(
        std::uint32_t friend_number,
        std::span<const std::uint8_t> packet,
        TransportTrafficClass traffic_class) {
        if (packet.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "sensitive lossless packet may not be empty"};
        }
        if (packet.size() > toxcore::abi::kMaxCustomPacketSize) {
            return Status{ErrorCode::invalid_argument,
                          "sensitive lossless packet exceeds c-toxcore capacity"};
        }
        if (!valid_lossless_packet_id(packet.front())) {
            return Status{
                ErrorCode::invalid_argument,
                "first sensitive lossless packet byte is outside c-toxcore's application ranges"};
        }

        {
            std::scoped_lock lock(sensitive_lossless_stats_mutex_);
            saturating_increment(sensitive_lossless_stats_.calls);
        }
        auto payload = std::make_shared<SensitivePacketPayload>(packet);
        return invoke_owner<Status>(
            traffic_class,
            [this, friend_number, payload] {
                {
                    std::scoped_lock lock(sensitive_lossless_stats_mutex_);
                    saturating_increment(
                        sensitive_lossless_stats_.toxcore_attempts);
                }
                const std::span<const std::uint8_t> bytes = payload->bytes();
                toxcore::abi::FriendCustomPacketError error =
                    toxcore::abi::kFriendCustomPacketOk;
                const bool sent = library_->api().friend_send_lossless_packet(
                    tox_, friend_number, bytes.data(), bytes.size(), &error);
                {
                    std::scoped_lock lock(sensitive_lossless_stats_mutex_);
                    if (!sent || error != toxcore::abi::kFriendCustomPacketOk) {
                        if (error ==
                            toxcore::abi::kFriendCustomPacketSendQueueFull) {
                            saturating_increment(
                                sensitive_lossless_stats_.send_queue_full);
                        } else if (
                            error ==
                            toxcore::abi::kFriendCustomPacketFriendNotConnected) {
                            saturating_increment(
                                sensitive_lossless_stats_.peer_not_connected);
                        } else if (
                            error ==
                            toxcore::abi::kFriendCustomPacketFriendNotFound) {
                            saturating_increment(
                                sensitive_lossless_stats_.peer_not_found);
                        } else if (
                            error == toxcore::abi::kFriendCustomPacketNull ||
                            error == toxcore::abi::kFriendCustomPacketInvalid ||
                            error == toxcore::abi::kFriendCustomPacketEmpty ||
                            error == toxcore::abi::kFriendCustomPacketTooLong) {
                            saturating_increment(
                                sensitive_lossless_stats_.contract_rejections);
                        } else {
                            saturating_increment(
                                sensitive_lossless_stats_.other_failures);
                        }
                    } else {
                        saturating_increment(sensitive_lossless_stats_.accepted);
                    }
                }
                if (!sent || error != toxcore::abi::kFriendCustomPacketOk) {
                    return custom_packet_failure(error, "lossless");
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status send_lossy(
        std::uint32_t friend_number,
        const std::vector<std::uint8_t> &packet,
        TransportTrafficClass traffic_class) {
        if (packet.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "lossy packet may not be empty"};
        }
        if (packet.size() > toxcore::abi::kMaxCustomPacketSize) {
            return Status{ErrorCode::invalid_argument,
                          "lossy packet exceeds c-toxcore capacity"};
        }
        if (!valid_lossy_packet_id(packet.front())) {
            return Status{
                ErrorCode::invalid_argument,
                "first lossy packet byte is outside c-toxcore's application range"};
        }

        return invoke_owner<Status>(
            traffic_class,
            [this, friend_number, packet] {
                toxcore::abi::FriendCustomPacketError error =
                    toxcore::abi::kFriendCustomPacketOk;
                const bool sent = library_->api().friend_send_lossy_packet(
                    tox_, friend_number, packet.data(), packet.size(), &error);
                if (!sent || error != toxcore::abi::kFriendCustomPacketOk) {
                    return custom_packet_failure(error, "lossy");
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Result<std::uint32_t> offer_file(
        std::uint32_t friend_number, std::uint32_t kind,
        std::uint64_t file_size, const std::optional<FileId> &file_id,
        const std::vector<std::uint8_t> &filename,
        FileChunkSource chunk_source) {
        if (filename.size() > toxcore::abi::kMaxFilenameLength) {
            return Status{ErrorCode::invalid_argument,
                          "file name exceeds c-toxcore's 255-byte limit"};
        }

        return invoke_owner<Result<std::uint32_t>>(
            TransportTrafficClass::bulk,
            [this, friend_number, kind, file_size, file_id, filename,
             chunk_source = std::move(chunk_source)]() mutable {
                toxcore::abi::FileSendError error = toxcore::abi::kFileSendOk;
                const std::uint8_t *id_pointer =
                    file_id ? file_id->data() : nullptr;
                const std::uint8_t *name_pointer =
                    filename.empty() ? nullptr : filename.data();
                const toxcore::abi::FileNumber file_number =
                    library_->api().file_send(
                        tox_, friend_number, kind, file_size, id_pointer,
                        name_pointer, filename.size(), &error);
                if (error != toxcore::abi::kFileSendOk ||
                    file_number == toxcore::abi::kFileNumberFailure) {
                    return Result<std::uint32_t>{Status{
                        ErrorCode::library_error,
                        "tox_file_send failed with error " +
                            std::to_string(static_cast<int>(error))}};
                }
                if (chunk_source) {
                    file_chunk_sources_.insert_or_assign(
                        file_transfer_key(friend_number, file_number),
                        FileChunkSourceState{
                            std::move(chunk_source), file_size});
                }
                return Result<std::uint32_t>{
                    static_cast<std::uint32_t>(file_number)};
            },
            [](const Status &status) { return Result<std::uint32_t>{status}; });
    }

    Status control_file(
        std::uint32_t friend_number, std::uint32_t file_number,
        TransferControl control) {
        return invoke_owner<Status>(
            [this, friend_number, file_number, control] {
                const std::uint64_t key =
                    file_transfer_key(friend_number, file_number);
                if (control == TransferControl::pause &&
                    paced_files_.contains(key)) {
                    // The explicit caller takes ownership of an already
                    // scheduler-paused transfer. Do not ask c-toxcore to
                    // pause the same local side twice, and never auto-resume
                    // a user pause.
                    forget_paced_file_on_owner_thread(key);
                    return Status::success();
                }
                // A scheduled pause has not crossed the c-toxcore API yet.
                // Let an explicit caller issue and own this pause instead.
                if (control == TransferControl::pause) {
                    pending_file_pauses_.erase(key);
                }
                toxcore::abi::FileControlError error =
                    toxcore::abi::kFileControlOk;
                const bool sent = library_->api().file_control(
                    tox_, friend_number, file_number, to_abi_control(control),
                    &error);
                if (!sent || error != toxcore::abi::kFileControlOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_file_control failed with error " +
                            std::to_string(static_cast<int>(error))};
                }
                if (control == TransferControl::cancel) {
                    file_chunk_sources_.erase(key);
                }
                if (control == TransferControl::resume ||
                    control == TransferControl::cancel) {
                    forget_paced_file_on_owner_thread(key);
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Status seek_file(
        std::uint32_t friend_number, std::uint32_t file_number,
        std::uint64_t position) {
        return invoke_owner<Status>(
            TransportTrafficClass::bulk,
            [this, friend_number, file_number, position] {
                toxcore::abi::FileSeekError error = toxcore::abi::kFileSeekOk;
                const bool sent = library_->api().file_seek(
                    tox_, friend_number, file_number, position, &error);
                if (!sent || error != toxcore::abi::kFileSeekOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_file_seek failed with error " +
                            std::to_string(static_cast<int>(error))};
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    Result<FileId> get_file_id(
        std::uint32_t friend_number, std::uint32_t file_number) {
        return invoke_owner<Result<FileId>>(
            [this, friend_number, file_number] {
                FileId file_id{};
                toxcore::abi::FileGetError error = toxcore::abi::kFileGetOk;
                const bool copied = library_->api().file_get_file_id(
                    tox_, friend_number, file_number, file_id.data(), &error);
                if (!copied || error != toxcore::abi::kFileGetOk) {
                    return Result<FileId>{Status{
                        ErrorCode::library_error,
                        "tox_file_get_file_id failed with error " +
                            std::to_string(static_cast<int>(error))}};
                }
                return Result<FileId>{file_id};
            },
            [](const Status &status) { return Result<FileId>{status}; });
    }

    Result<std::uint32_t> find_file(
        std::uint32_t friend_number, const FileId &file_id) {
        return invoke_owner<Result<std::uint32_t>>(
            [this, friend_number, file_id] {
                toxcore::abi::FileByIdError error = toxcore::abi::kFileByIdOk;
                const toxcore::abi::FileNumber file_number =
                    library_->api().file_by_id(
                        tox_, friend_number, file_id.data(), &error);
                if (error != toxcore::abi::kFileByIdOk ||
                    file_number == toxcore::abi::kFileNumberFailure) {
                    return Result<std::uint32_t>{Status{
                        ErrorCode::library_error,
                        "tox_file_by_id failed with error " +
                            std::to_string(static_cast<int>(error))}};
                }
                return Result<std::uint32_t>{
                    static_cast<std::uint32_t>(file_number)};
            },
            [](const Status &status) { return Result<std::uint32_t>{status}; });
    }

    Status send_file_chunk(
        std::uint32_t friend_number, std::uint32_t file_number,
        std::uint64_t position, const std::vector<std::uint8_t> &data) {
        return invoke_owner<Status>(
            TransportTrafficClass::bulk,
            [this, friend_number, file_number, position, data] {
                toxcore::abi::FileSendChunkError error =
                    toxcore::abi::kFileSendChunkOk;
                const std::uint8_t *data_pointer =
                    data.empty() ? nullptr : data.data();
                const bool sent = library_->api().file_send_chunk(
                    tox_, friend_number, file_number, position, data_pointer,
                    data.size(), &error);
                if (!sent || error != toxcore::abi::kFileSendChunkOk) {
                    return file_chunk_failure(error);
                }
                return Status::success();
            },
            [](const Status &status) { return status; });
    }

    std::optional<TransportEvent> poll_event(
        std::chrono::milliseconds timeout) {
        std::unique_lock lock(event_mutex_);
        event_cv_.wait_for(lock, timeout, [this] {
            return !events_.empty() ||
                   (!running_.load() && stop_requested_.load());
        });
        if (events_.empty()) {
            return std::nullopt;
        }
        TransportEvent event = std::move(events_.front());
        events_.pop_front();
        const bool wake_pacing =
            file_pacing_paused_transfers_.load() != 0U &&
            events_.size() <= config_.file_pacing_low_watermark;
        lock.unlock();
        event_space_cv_.notify_one();
        if (wake_pacing) {
            {
                std::scoped_lock command_lock(command_mutex_);
                file_pacing_wake_requested_ = true;
            }
            command_cv_.notify_one();
        }
        return event;
    }

    [[nodiscard]] TransportStats stats() const {
        TransportStats result;
        result.iteration_count = iteration_count_.load();
        result.requested_iteration_interval_ms =
            requested_iteration_interval_ms_.load();
        result.effective_iteration_interval_ms =
            effective_iteration_interval_ms_.load();
        {
            std::scoped_lock lock(sensitive_lossless_stats_mutex_);
            result.sensitive_lossless = sensitive_lossless_stats_;
        }
        {
            std::scoped_lock lock(command_mutex_);
            for (std::size_t index = 0U; index < command_queues_.size(); ++index) {
                result.pending_commands += command_queues_[index].size();
                command_stats_[index].pending_commands =
                    command_queues_[index].size();
            }
            const auto projected_stats = [this](std::size_t index) {
                TransportTrafficStats stats = command_stats_[index];
                const LatencyHistogram::Summary latency =
                    command_wait_histograms_[index].summary();
                stats.queue_wait_p50_upper_bound_us =
                    latency.p50.upper_bound_us;
                stats.queue_wait_p95_upper_bound_us =
                    latency.p95.upper_bound_us;
                stats.queue_wait_p99_upper_bound_us =
                    latency.p99.upper_bound_us;
                stats.queue_wait_p50_exact = latency.p50.exact;
                stats.queue_wait_p95_exact = latency.p95.exact;
                stats.queue_wait_p99_exact = latency.p99.exact;
                stats.queue_wait_at_or_above_2000_us =
                    latency.at_or_above_interactive_gate;
                return stats;
            };
            result.interactive = projected_stats(traffic_index(
                TransportTrafficClass::interactive));
            result.control = projected_stats(traffic_index(
                TransportTrafficClass::control));
            result.bulk = projected_stats(traffic_index(
                TransportTrafficClass::bulk));
        }
        {
            std::scoped_lock lock(event_mutex_);
            result.pending_events = events_.size();
            result.maximum_pending_events = maximum_pending_events_;
            result.dropped_events = dropped_events_;
            result.required_event_backpressure_count =
                required_event_backpressure_count_;
            result.required_event_backpressure_total_us =
                required_event_backpressure_total_us_;
            result.required_event_backpressure_maximum_us =
                required_event_backpressure_maximum_us_;
        }
        result.file_pacing_paused_transfers =
            file_pacing_paused_transfers_.load();
        result.file_pacing_high_watermark =
            config_.file_pacing_high_watermark;
        result.file_pacing_low_watermark =
            config_.file_pacing_low_watermark;
        result.file_pacing_minimum_hold_us = static_cast<std::uint64_t>(
            config_.file_pacing_minimum_hold.count());
        result.file_pacing_resume_batch_limit =
            config_.file_pacing_resume_batch_limit;
        {
            std::scoped_lock lock(file_pacing_stats_mutex_);
            result.file_pacing_pause_count = file_pacing_pause_count_;
            result.file_pacing_resume_count = file_pacing_resume_count_;
            result.file_pacing_resume_batch_count =
                file_pacing_resume_batch_count_;
            result.file_pacing_resume_batch_maximum =
                file_pacing_resume_batch_maximum_;
            result.file_pacing_external_pause_count =
                file_pacing_external_pause_count_;
            result.file_pacing_pause_failure_count =
                file_pacing_pause_failure_count_;
            result.file_pacing_resume_failure_count =
                file_pacing_resume_failure_count_;
            result.file_pacing_total_hold_us =
                file_pacing_total_hold_us_;
            result.file_pacing_maximum_hold_us =
                file_pacing_maximum_hold_us_;
        }
        return result;
    }

  private:
    static constexpr std::size_t traffic_index(
        TransportTrafficClass traffic_class) noexcept {
        return static_cast<std::size_t>(traffic_class);
    }

    [[nodiscard]] std::size_t pending_command_count_locked() const noexcept {
        std::size_t count = 0U;
        for (const auto &queue : command_queues_) {
            count += queue.size();
        }
        return count;
    }

    template <typename T>
    T invoke_owner(
        TransportTrafficClass traffic_class,
        typename OwnerCommand<T>::Operation operation,
        typename OwnerCommand<T>::ErrorFactory error_factory) {
        if (!running() || stop_requested_.load()) {
            return error_factory(
                Status{ErrorCode::unavailable, "Tox transport is not running"});
        }

        auto command = std::make_shared<OwnerCommand<T>>(
            traffic_class, std::move(operation), error_factory);
        std::future<T> future = command->future();
        {
            std::scoped_lock lock(command_mutex_);
            if (!running_.load() || stop_requested_.load()) {
                return error_factory(
                    Status{ErrorCode::unavailable, "Tox transport is not running"});
            }
            if (pending_command_count_locked() >= config_.max_pending_commands) {
                return error_factory(Status{
                    ErrorCode::resource_exhausted,
                    "Tox owner command queue reached its configured limit"});
            }
            const std::size_t index = traffic_index(traffic_class);
            const bool class_was_empty = command_queues_[index].empty();
            command_queues_[index].push_back(command);
            ++command_stats_[index].admitted_commands;
            if (traffic_class == TransportTrafficClass::interactive &&
                class_was_empty) {
                // A newly active latency-sensitive lane starts at the front
                // without rewinding the weighted cycle. The next scheduled
                // selection still advances toward control and bulk, so sparse
                // interactive arrivals cannot starve either lower class.
                interactive_boost_pending_ = true;
            }
        }
        command_cv_.notify_one();

        if (future.wait_for(config_.owner_command_timeout) !=
            std::future_status::ready) {
            const Status timed_out{
                ErrorCode::timeout,
                "timed out before the Tox owner thread began the operation; operation cancelled"};
            if (command->cancel(timed_out)) {
                return future.get();
            }
            // The owner thread has begun the c-toxcore call. Returning a timeout
            // here would be ambiguous because the operation may already have
            // taken effect. c-toxcore client calls are expected to be bounded;
            // once started, wait for the exact result.
        }

        try {
            return future.get();
        } catch (const std::exception &exception) {
            return error_factory(Status{
                ErrorCode::internal_error,
                "Tox owner operation raised an exception: " +
                    std::string(exception.what())});
        } catch (...) {
            return error_factory(Status{
                ErrorCode::internal_error,
                "Tox owner operation raised an unknown exception"});
        }
    }

    template <typename T>
    T invoke_owner(
        typename OwnerCommand<T>::Operation operation,
        typename OwnerCommand<T>::ErrorFactory error_factory) {
        return invoke_owner<T>(
            TransportTrafficClass::control, std::move(operation),
            std::move(error_factory));
    }

    std::size_t erase_sent_text_receipts_for_friend(
        std::uint32_t friend_number) {
        return std::erase_if(
            sent_message_kinds_, [friend_number](const auto &entry) {
                return static_cast<std::uint32_t>(entry.first >> 32U) ==
                       friend_number;
            });
    }

    std::size_t erase_file_chunk_sources_for_friend(
        std::uint32_t friend_number) {
        const std::size_t erased = std::erase_if(
            file_chunk_sources_, [friend_number](const auto &entry) {
                return static_cast<std::uint32_t>(entry.first >> 32U) ==
                       friend_number;
            });
        forget_paced_files_for_friend_on_owner_thread(friend_number);
        return erased;
    }

    [[nodiscard]] bool file_pacing_enabled() const noexcept {
        return config_.file_pacing_high_watermark != 0U;
    }

    [[nodiscard]] bool file_pacing_pressure() const {
        if (!file_pacing_enabled()) {
            return false;
        }
        std::scoped_lock lock(event_mutex_);
        return events_.size() >= config_.file_pacing_high_watermark;
    }

    void update_file_pacing_paused_count_on_owner_thread() noexcept {
        file_pacing_paused_transfers_.store(paced_files_.size());
    }

    void forget_paced_file_on_owner_thread(std::uint64_t key) noexcept {
        static_cast<void>(pending_file_pauses_.erase(key));
        static_cast<void>(paced_files_.erase(key));
        update_file_pacing_paused_count_on_owner_thread();
    }

    void forget_paced_files_for_friend_on_owner_thread(
        std::uint32_t friend_number) noexcept {
        static_cast<void>(std::erase_if(
            paced_files_, [friend_number](const auto &entry) {
                return static_cast<std::uint32_t>(entry.first >> 32U) ==
                       friend_number;
            }));
        static_cast<void>(std::erase_if(
            pending_file_pauses_, [friend_number](const auto &entry) {
                return static_cast<std::uint32_t>(entry.first >> 32U) ==
                       friend_number;
            }));
        update_file_pacing_paused_count_on_owner_thread();
    }

    void maybe_schedule_file_pause_on_owner_thread(
        toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FileNumber file_number) {
        if (!file_pacing_pressure()) {
            return;
        }
        const std::uint64_t key =
            file_transfer_key(friend_number, file_number);
        if (paced_files_.contains(key) || pending_file_pauses_.contains(key)) {
            return;
        }

        // tox_file_control is an ordinary public API, not one of the narrow
        // callback-only APIs. Defer it until tox_iterate has returned so the
        // provider is never entered recursively from a callback.
        pending_file_pauses_.insert_or_assign(
            key, PendingFilePause{friend_number, file_number});
    }

    void apply_scheduled_file_pauses_on_owner_thread() {
        for (const auto &[key, file] : pending_file_pauses_) {
            if (paced_files_.contains(key)) {
                continue;
            }

            toxcore::abi::FileControlError error =
                toxcore::abi::kFileControlOk;
            const bool paused = library_->api().file_control(
                tox_, file.friend_number, file.file_number,
                to_abi_control(TransferControl::pause), &error);
            if (!paused || error != toxcore::abi::kFileControlOk) {
                std::scoped_lock lock(file_pacing_stats_mutex_);
                if (error == toxcore::abi::kFileControlAlreadyPaused) {
                    // Another local owner (the receiver carrier window or an
                    // explicit caller) crossed the provider boundary after
                    // this callback scheduled its reactive pause. It owns the
                    // pause and must be the only layer allowed to resume it.
                    saturating_increment(file_pacing_external_pause_count_);
                } else {
                    saturating_increment(file_pacing_pause_failure_count_);
                }
                continue;
            }

            paced_files_.insert_or_assign(
                key, PacedFile{
                         file.friend_number, file.file_number,
                         std::chrono::steady_clock::now()});
            std::scoped_lock lock(file_pacing_stats_mutex_);
            saturating_increment(file_pacing_pause_count_);
        }
        pending_file_pauses_.clear();
        update_file_pacing_paused_count_on_owner_thread();
    }

    void resume_paced_files_on_owner_thread() {
        if (paced_files_.empty()) {
            return;
        }
        {
            std::scoped_lock lock(event_mutex_);
            if (events_.size() > config_.file_pacing_low_watermark) {
                return;
            }
        }

        std::size_t resumed_in_batch = 0U;
        std::size_t attempted_in_batch = 0U;
        while (attempted_in_batch <
               config_.file_pacing_resume_batch_limit) {
            const auto now = std::chrono::steady_clock::now();
            auto candidate = paced_files_.end();
            for (auto iterator = paced_files_.begin();
                 iterator != paced_files_.end(); ++iterator) {
                const PacedFile &file = iterator->second;
                if (now - file.paused_at <
                    config_.file_pacing_minimum_hold) {
                    continue;
                }
                if (candidate == paced_files_.end() ||
                    file.paused_at < candidate->second.paused_at ||
                    (file.paused_at == candidate->second.paused_at &&
                     iterator->first < candidate->first)) {
                    candidate = iterator;
                }
            }
            if (candidate == paced_files_.end()) {
                break;
            }
            ++attempted_in_batch;
            PacedFile &file = candidate->second;

            toxcore::abi::FileControlError error =
                toxcore::abi::kFileControlOk;
            const bool resumed = library_->api().file_control(
                tox_, file.friend_number, file.file_number,
                to_abi_control(TransferControl::resume), &error);
            if (!resumed || error != toxcore::abi::kFileControlOk) {
                file.paused_at = now;
                std::scoped_lock lock(file_pacing_stats_mutex_);
                saturating_increment(file_pacing_resume_failure_count_);
                continue;
            }

            const auto held = std::chrono::duration_cast<
                std::chrono::microseconds>(now - file.paused_at);
            const std::uint64_t held_us = held.count() <= 0
                ? 0U
                : static_cast<std::uint64_t>(held.count());
            {
                std::scoped_lock lock(file_pacing_stats_mutex_);
                saturating_increment(file_pacing_resume_count_);
                saturating_add(file_pacing_total_hold_us_, held_us);
                file_pacing_maximum_hold_us_ = std::max(
                    file_pacing_maximum_hold_us_, held_us);
            }
            paced_files_.erase(candidate);
            ++resumed_in_batch;
        }
        if (resumed_in_batch != 0U) {
            std::scoped_lock lock(file_pacing_stats_mutex_);
            saturating_increment(file_pacing_resume_batch_count_);
            file_pacing_resume_batch_maximum_ = std::max(
                file_pacing_resume_batch_maximum_, resumed_in_batch);
        }
        update_file_pacing_paused_count_on_owner_thread();
    }

    [[nodiscard]] std::optional<std::chrono::microseconds>
    paced_file_resume_wait_on_owner_thread() const {
        if (paced_files_.empty()) {
            return std::nullopt;
        }
        {
            std::scoped_lock lock(event_mutex_);
            if (events_.size() > config_.file_pacing_low_watermark) {
                return std::nullopt;
            }
        }

        const auto now = std::chrono::steady_clock::now();
        std::optional<std::chrono::microseconds> wait;
        for (const auto &[key, file] : paced_files_) {
            static_cast<void>(key);
            const auto ready =
                file.paused_at + config_.file_pacing_minimum_hold;
            const auto candidate = ready <= now
                ? std::chrono::microseconds::zero()
                : std::chrono::duration_cast<std::chrono::microseconds>(
                      ready - now);
            wait = wait ? std::min(*wait, candidate) : candidate;
        }
        return wait;
    }

    void worker_main() noexcept {
        bool startup_reported = false;
        try {
            const Status initialization = initialize_on_owner_thread();
            if (!initialization.ok()) {
                startup_promise_.set_value(initialization);
                startup_reported = true;
                cleanup_on_owner_thread();
                return;
            }

            running_.store(true);
            startup_promise_.set_value(Status::success());
            startup_reported = true;
            emit({TransportEventKind::backend_ready,
                  0U,
                  0,
                  {},
                  {},
                  "c-toxcore " + library_->version().str() + " loaded from " +
                      library_->loaded_path()});

            while (!stop_requested_.load()) {
                run_pending_commands();
                if (stop_requested_.load()) {
                    break;
                }
                resume_paced_files_on_owner_thread();
                library_->api().iterate(tox_, this);
                ++iteration_count_;
                apply_scheduled_file_pauses_on_owner_thread();
                flush_deferred_file_offers_on_owner_thread();
                maybe_rebootstrap_on_owner_thread();

                const std::uint32_t requested_ms =
                    library_->api().iteration_interval(tox_);
                requested_iteration_interval_ms_.store(requested_ms);
                const std::uint32_t maximum_ms =
                    maximum_iteration_interval_ms_.load();
                const std::uint32_t effective_ms =
                    std::clamp<std::uint32_t>(requested_ms, 1U, maximum_ms);
                effective_iteration_interval_ms_.store(effective_ms);
                auto sleep_time = std::chrono::duration_cast<
                    std::chrono::microseconds>(
                    std::chrono::milliseconds(effective_ms));
                if (const auto pacing_wait =
                        paced_file_resume_wait_on_owner_thread()) {
                    sleep_time = std::min(sleep_time, *pacing_wait);
                }
                std::unique_lock lock(command_mutex_);
                command_cv_.wait_for(lock, sleep_time, [this] {
                    return stop_requested_.load() ||
                           iteration_interval_changed_ ||
                           pending_command_count_locked() != 0U ||
                           file_pacing_wake_requested_;
                });
                iteration_interval_changed_ = false;
                file_pacing_wake_requested_ = false;
            }

            cancel_pending_commands(
                Status{ErrorCode::unavailable, "Tox transport stopped before operation began"});
            if (config_.save_state_on_stop) {
                static_cast<void>(save_state_on_owner_thread());
            }
            cleanup_on_owner_thread();
            running_.store(false);
            event_cv_.notify_all();
        } catch (const std::exception &exception) {
            handle_worker_failure(
                startup_reported,
                "Tox owner thread failed: " + std::string(exception.what()));
        } catch (...) {
            handle_worker_failure(
                startup_reported,
                "Tox owner thread failed unexpectedly");
        }
    }

    void handle_worker_failure(bool startup_reported, const std::string &message) noexcept {
        running_.store(false);
        cancel_pending_commands(Status{ErrorCode::internal_error, message});
        if (!startup_reported) {
            try {
                startup_promise_.set_value(
                    Status{ErrorCode::internal_error, message});
            } catch (...) {
            }
        } else {
            emit({TransportEventKind::diagnostic, 0U, 0, {}, {}, message});
        }
        cleanup_on_owner_thread();
        event_cv_.notify_all();
    }

    Status validate_config() const {
        const Status route = ToxTransport::validate_route_config(config_);
        if (!route.ok()) return route;
        if (config_.bootstrap_retry_interval <=
            std::chrono::milliseconds::zero()) {
            return Status{ErrorCode::invalid_argument,
                          "bootstrap retry interval must be positive"};
        }
        if (config_.owner_command_timeout <=
            std::chrono::milliseconds::zero()) {
            return Status{ErrorCode::invalid_argument,
                          "owner command timeout must be positive"};
        }
        if (config_.maximum_iteration_interval < std::chrono::milliseconds(1) ||
            config_.maximum_iteration_interval > std::chrono::milliseconds(1000)) {
            return Status{
                ErrorCode::invalid_argument,
                "maximum toxcore iteration interval must be between 1 and 1000 ms"};
        }
        if (config_.max_pending_commands == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "owner command queue limit must be positive"};
        }
        if (config_.max_owner_commands_per_iteration == 0U) {
            return Status{
                ErrorCode::invalid_argument,
                "owner command per-iteration limit must be positive"};
        }
        if (config_.max_pending_events == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "transport event queue limit must be positive"};
        }
        const bool pacing_disabled =
            config_.file_pacing_high_watermark == 0U &&
            config_.file_pacing_low_watermark == 0U;
        if (!pacing_disabled &&
            (config_.file_pacing_high_watermark == 0U ||
             config_.file_pacing_high_watermark >=
                 config_.max_pending_events ||
             config_.file_pacing_low_watermark >=
                 config_.file_pacing_high_watermark)) {
            return Status{
                ErrorCode::invalid_argument,
                "file pacing requires 0 <= low-watermark < high-watermark < event limit"};
        }
        if (!pacing_disabled &&
            (config_.file_pacing_minimum_hold <
                 std::chrono::microseconds(100U) ||
             config_.file_pacing_minimum_hold >
                 std::chrono::seconds(1))) {
            return Status{
                ErrorCode::invalid_argument,
                "file pacing minimum hold must be in 100..1000000 us"};
        }
        if (config_.file_pacing_resume_batch_limit == 0U ||
            config_.file_pacing_resume_batch_limit >
                config_.max_pending_events) {
            return Status{
                ErrorCode::invalid_argument,
                "file pacing resume batch must be in 1..event limit"};
        }
        return Status::success();
    }

    Status validate_runtime_abi() const {
        const toxcore::abi::Api &api = library_->api();
        if (!api.version_is_compatible(0U, 2U, 23U)) {
            return Status{
                ErrorCode::library_error,
                std::string(kProjectName) + " " + std::string(kRevision) +
                    " requires c-toxcore ABI " + std::string(kToxcoreTarget) +
                    "; found " + library_->version().str()};
        }
        if (api.public_key_size() != toxcore::abi::kPublicKeySize ||
            api.address_size() != toxcore::abi::kAddressSize ||
            api.max_name_length() != toxcore::abi::kMaxNameLength ||
            api.max_status_message_length() !=
                toxcore::abi::kMaxStatusMessageLength ||
            api.max_message_length() != toxcore::abi::kMaxMessageLength ||
            api.file_id_length() != toxcore::abi::kFileIdLength ||
            api.max_filename_length() != toxcore::abi::kMaxFilenameLength ||
            api.max_friend_request_length() !=
                toxcore::abi::kMaxFriendRequestLength ||
            api.max_custom_packet_size() !=
                toxcore::abi::kMaxCustomPacketSize) {
            return Status{
                ErrorCode::library_error,
                "c-toxcore runtime constants do not match the IoTox 0.2.23 ABI contract"};
        }
        return Status::success();
    }

    Status initialize_on_owner_thread() {
        const Status config_status = validate_config();
        if (!config_status.ok()) {
            return config_status;
        }

        auto loaded = toxcore::DynamicToxcore::load(config_.toxcore_library);
        if (!loaded) {
            return loaded.status();
        }
        library_.emplace(std::move(loaded).value());

        const Status abi_status = validate_runtime_abi();
        if (!abi_status.ok()) {
            return abi_status;
        }

        std::vector<std::uint8_t> savedata;
        if (!config_.state_path.empty()) {
            auto state = StateStore::read(config_.state_path);
            if (state) {
                savedata = std::move(state).value();
            } else if (state.status().code() != ErrorCode::not_found) {
                return state.status();
            }
        }

        toxcore::abi::OptionsNewError options_error =
            toxcore::abi::kOptionsNewOk;
        toxcore::abi::ToxOptions *options =
            library_->api().options_new(&options_error);
        if (options == nullptr || options_error != toxcore::abi::kOptionsNewOk) {
            return Status{
                ErrorCode::library_error,
                "tox_options_new failed with error " +
                    std::to_string(static_cast<int>(options_error))};
        }

        const bool native_network =
            config_.network.tox_route == ToxRoute::native;
        const bool udp_enabled =
            native_network && config_.native_udp_enabled;
        library_->api().options_set_udp_enabled(
            options, udp_enabled);
        library_->api().options_set_local_discovery_enabled(
            options, udp_enabled);
        library_->api().options_set_dht_announcements_enabled(
            options, udp_enabled);
        library_->api().options_set_hole_punching_enabled(
            options, udp_enabled);
        if (is_strict_socks_tox_route(config_.network.tox_route)) {
            library_->api().options_set_proxy_type(
                options, toxcore::abi::kProxySocks5);
            if (!library_->api().options_set_proxy_host(
                    options, config_.socks5_proxy->host.c_str())) {
                library_->api().options_free(options);
                return Status{
                    ErrorCode::library_error,
                    "c-toxcore could not copy the SOCKS5 proxy host"};
            }
            library_->api().options_set_proxy_port(
                options, config_.socks5_proxy->port);
            library_->api().options_set_experimental_disable_dns(
                options, true);
        } else {
            library_->api().options_set_proxy_type(
                options, toxcore::abi::kProxyNone);
            library_->api().options_set_experimental_disable_dns(
                options, false);
        }
        if (!savedata.empty()) {
            library_->api().options_set_savedata_type(
                options, toxcore::abi::kSavedataToxSave);
            if (!library_->api().options_set_savedata_data(
                    options, savedata.data(), savedata.size())) {
                library_->api().options_free(options);
                return Status{
                    ErrorCode::library_error,
                    "c-toxcore could not copy savedata into Tox options"};
            }
        }

        toxcore::abi::NewError creation_error = toxcore::abi::kNewOk;
        tox_ = library_->api().tox_new(options, &creation_error);
        library_->api().options_free(options);
        if (tox_ == nullptr || creation_error != toxcore::abi::kNewOk) {
            return Status{
                ErrorCode::library_error,
                "tox_new failed with error " +
                    std::to_string(static_cast<int>(creation_error))};
        }

        library_->api().callback_self_connection_status(
            tox_, &Impl::on_self_connection);
        library_->api().callback_friend_connection_status(
            tox_, &Impl::on_friend_connection);
        library_->api().callback_friend_name(tox_, &Impl::on_friend_name);
        library_->api().callback_friend_status_message(
            tox_, &Impl::on_friend_status_message);
        library_->api().callback_friend_status(tox_, &Impl::on_friend_status);
        library_->api().callback_friend_typing(tox_, &Impl::on_friend_typing);
        library_->api().callback_friend_request(tox_, &Impl::on_friend_request);
        library_->api().callback_friend_message(tox_, &Impl::on_friend_message);
        library_->api().callback_friend_read_receipt(
            tox_, &Impl::on_friend_read_receipt);
        library_->api().callback_friend_lossy_packet(
            tox_, &Impl::on_lossy_packet);
        library_->api().callback_friend_lossless_packet(
            tox_, &Impl::on_lossless_packet);
        library_->api().callback_file_recv_control(
            tox_, &Impl::on_file_control);
        library_->api().callback_file_chunk_request(
            tox_, &Impl::on_file_chunk_request);
        library_->api().callback_file_recv(tox_, &Impl::on_file_offer);
        library_->api().callback_file_recv_chunk(
            tox_, &Impl::on_file_chunk);

        std::array<std::uint8_t, toxcore::abi::kAddressSize> address{};
        library_->api().self_get_address(tox_, address.data());
        if (config_.expected_public_key &&
            !std::equal(config_.expected_public_key->begin(),
                        config_.expected_public_key->end(), address.begin())) {
            return Status{
                ErrorCode::protocol_error,
                "loaded Tox identity does not match the configured expected public key"};
        }
        {
            std::scoped_lock lock(identity_mutex_);
            address_hex_ = hex_encode(address.data(), address.size());
        }

        const auto initial_friends = list_friends_on_owner_thread();
        if (!initial_friends) {
            return initial_friends.status();
        }

        retry_connectivity_on_owner_thread("startup");
        return Status::success();
    }

    Result<SelfProfile> self_profile_on_owner_thread() {
        SelfProfile profile;
        const std::size_t name_size = library_->api().self_get_name_size(tox_);
        if (name_size > toxcore::abi::kMaxNameLength) {
            return Status{ErrorCode::library_error,
                          "c-toxcore returned an oversized self name"};
        }
        profile.name.resize(name_size);
        if (!profile.name.empty()) {
            library_->api().self_get_name(tox_, profile.name.data());
        }

        const std::size_t status_size =
            library_->api().self_get_status_message_size(tox_);
        if (status_size > toxcore::abi::kMaxStatusMessageLength) {
            return Status{ErrorCode::library_error,
                          "c-toxcore returned an oversized self status message"};
        }
        profile.status_message.resize(status_size);
        if (!profile.status_message.empty()) {
            library_->api().self_get_status_message(
                tox_, profile.status_message.data());
        }
        profile.status = from_abi_status(library_->api().self_get_status(tox_));
        return profile;
    }

    Result<std::vector<TransportPeer>> list_friends_on_owner_thread() {
        const std::size_t count =
            library_->api().self_get_friend_list_size(tox_);
        std::vector<toxcore::abi::FriendNumber> numbers(count);
        if (!numbers.empty()) {
            library_->api().self_get_friend_list(tox_, numbers.data());
        }

        std::vector<TransportPeer> peers;
        peers.reserve(numbers.size());
        for (const toxcore::abi::FriendNumber friend_number : numbers) {
            TransportPeer peer;
            peer.friend_number = friend_number;
            toxcore::abi::FriendGetPublicKeyError error =
                toxcore::abi::kFriendGetPublicKeyOk;
            const bool copied = library_->api().friend_get_public_key(
                tox_, friend_number, peer.public_key.data(), &error);
            if (!copied || error != toxcore::abi::kFriendGetPublicKeyOk) {
                return Status{
                    ErrorCode::library_error,
                    "tox_friend_get_public_key failed with error " +
                        std::to_string(static_cast<int>(error))};
            }

            toxcore::abi::FriendQueryError name_error =
                toxcore::abi::kFriendQueryOk;
            const std::size_t name_size = library_->api().friend_get_name_size(
                tox_, friend_number, &name_error);
            if (name_error != toxcore::abi::kFriendQueryOk ||
                name_size > toxcore::abi::kMaxNameLength) {
                return Status{
                    ErrorCode::library_error,
                    "tox_friend_get_name_size failed with error " +
                        std::to_string(static_cast<int>(name_error))};
            }
            peer.name.resize(name_size);
            if (!peer.name.empty()) {
                name_error = toxcore::abi::kFriendQueryOk;
                const bool name_copied = library_->api().friend_get_name(
                    tox_, friend_number, peer.name.data(), &name_error);
                if (!name_copied || name_error != toxcore::abi::kFriendQueryOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_friend_get_name failed with error " +
                            std::to_string(static_cast<int>(name_error))};
                }
            }

            toxcore::abi::FriendQueryError status_error =
                toxcore::abi::kFriendQueryOk;
            const std::size_t status_size =
                library_->api().friend_get_status_message_size(
                    tox_, friend_number, &status_error);
            if (status_error != toxcore::abi::kFriendQueryOk ||
                status_size > toxcore::abi::kMaxStatusMessageLength) {
                return Status{
                    ErrorCode::library_error,
                    "tox_friend_get_status_message_size failed with error " +
                        std::to_string(static_cast<int>(status_error))};
            }
            peer.status_message.resize(status_size);
            if (!peer.status_message.empty()) {
                status_error = toxcore::abi::kFriendQueryOk;
                const bool status_copied =
                    library_->api().friend_get_status_message(
                        tox_, friend_number, peer.status_message.data(),
                        &status_error);
                if (!status_copied ||
                    status_error != toxcore::abi::kFriendQueryOk) {
                    return Status{
                        ErrorCode::library_error,
                        "tox_friend_get_status_message failed with error " +
                            std::to_string(static_cast<int>(status_error))};
                }
            }

            const auto connection = friend_connections_.find(friend_number);
            if (connection == friend_connections_.end()) {
                friend_connections_[friend_number] =
                    toxcore::abi::kConnectionNone;
                peer.connection_status =
                    static_cast<int>(toxcore::abi::kConnectionNone);
            } else {
                peer.connection_status =
                    static_cast<int>(connection->second);
            }
            const auto status = friend_statuses_.find(friend_number);
            if (status == friend_statuses_.end()) {
                friend_statuses_[friend_number] = PresenceStatus::available;
                peer.status = PresenceStatus::available;
            } else {
                peer.status = status->second;
            }
            const auto typing = friend_typing_.find(friend_number);
            if (typing == friend_typing_.end()) {
                friend_typing_[friend_number] = false;
                peer.typing = false;
            } else {
                peer.typing = typing->second;
            }
            peers.push_back(peer);
        }
        std::sort(peers.begin(), peers.end(), [](const auto &left, const auto &right) {
            return left.friend_number < right.friend_number;
        });
        return peers;
    }

    void flush_deferred_file_offers_on_owner_thread() {
        while (!deferred_file_offers_.empty()) {
            TransportEvent event = std::move(deferred_file_offers_.front());
            deferred_file_offers_.pop_front();

            toxcore::abi::FileGetError error = toxcore::abi::kFileGetOk;
            const bool copied = library_->api().file_get_file_id(
                tox_, event.friend_number, event.file_number,
                event.file_id.data(), &error);
            event.has_file_id = copied && error == toxcore::abi::kFileGetOk;
            if (!event.has_file_id) {
                TransportEvent diagnostic;
                diagnostic.kind = TransportEventKind::diagnostic;
                diagnostic.friend_number = event.friend_number;
                diagnostic.file_number = event.file_number;
                diagnostic.message =
                    "tox_file_get_file_id failed while completing incoming offer; error=" +
                    std::to_string(static_cast<int>(error));
                emit(std::move(diagnostic));
            }
            emit(std::move(event));
        }
    }

    void configure_tcp_relays_on_owner_thread(std::string_view reason) {
        for (const toxcore::BootstrapEndpoint &endpoint : config_.tcp_relays) {
            toxcore::abi::BootstrapError error = toxcore::abi::kBootstrapOk;
            const bool accepted = library_->api().add_tcp_relay(
                tox_, endpoint.host.c_str(), endpoint.port,
                endpoint.public_key.data(), &error);
            emit({TransportEventKind::tcp_relay,
                  0U,
                  0,
                  {},
                  {},
                  std::string(reason) + ' ' +
                      std::string(
                          accepted && error == toxcore::abi::kBootstrapOk
                              ? "accepted "
                              : "rejected ") +
                      toxcore::format_bootstrap_endpoint(endpoint) +
                      " error=" +
                      std::to_string(static_cast<int>(error))});
        }
    }

    void bootstrap_on_owner_thread(std::string_view reason) {
        if (config_.bootstrap_nodes.empty()) {
            return;
        }

        for (const toxcore::BootstrapEndpoint &endpoint :
             config_.bootstrap_nodes) {
            toxcore::abi::BootstrapError error = toxcore::abi::kBootstrapOk;
            const bool accepted = library_->api().bootstrap(
                tox_, endpoint.host.c_str(), endpoint.port,
                endpoint.public_key.data(), &error);
            emit({TransportEventKind::bootstrap,
                  0U,
                  0,
                  {},
                  {},
                  std::string(reason) + ' ' +
                      (accepted && error == toxcore::abi::kBootstrapOk
                           ? "accepted "
                           : "rejected ") +
                      toxcore::format_bootstrap_endpoint(endpoint) +
                      " error=" +
                      std::to_string(static_cast<int>(error))});
        }
    }

    void retry_connectivity_on_owner_thread(std::string_view reason) {
        configure_tcp_relays_on_owner_thread(reason);
        bootstrap_on_owner_thread(reason);
        next_bootstrap_attempt_ =
            std::chrono::steady_clock::now() +
            config_.bootstrap_retry_interval;
    }

    void maybe_rebootstrap_on_owner_thread() {
        if ((config_.bootstrap_nodes.empty() && config_.tcp_relays.empty()) ||
            self_connection_ != toxcore::abi::kConnectionNone ||
            std::chrono::steady_clock::now() < next_bootstrap_attempt_) {
            return;
        }
        retry_connectivity_on_owner_thread("retry");
    }

    Status save_state_on_owner_thread() {
        if (config_.state_path.empty()) {
            return Status::success();
        }
        if (tox_ == nullptr || !library_) {
            return Status{ErrorCode::internal_error,
                          "cannot persist tox savedata without a live provider"};
        }
        const std::size_t size = library_->api().get_savedata_size(tox_);
        if (size == 0U) {
            const Status status{
                ErrorCode::library_error,
                "c-toxcore returned an empty savedata size"};
            emit({TransportEventKind::diagnostic, 0U, 0, {}, {},
                  status.message()});
            return status;
        }
        std::vector<std::uint8_t> savedata(size);
        library_->api().get_savedata(tox_, savedata.data());
        const Status status =
            StateStore::write_atomic(config_.state_path, savedata);
        if (!status.ok()) {
            emit({TransportEventKind::diagnostic,
                  0U,
                  0,
                  {},
                  {},
                  status.message()});
        }
        return status;
    }

    void cleanup_on_owner_thread() noexcept {
        pending_file_pauses_.clear();
        paced_files_.clear();
        update_file_pacing_paused_count_on_owner_thread();
        if (tox_ != nullptr && library_) {
            library_->api().tox_kill(tox_);
            tox_ = nullptr;
        }
        library_.reset();
    }

    void run_pending_commands() {
        static constexpr std::array<TransportTrafficClass, 13U> schedule{
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::interactive,
            TransportTrafficClass::control,
            TransportTrafficClass::control,
            TransportTrafficClass::control,
            TransportTrafficClass::control,
            TransportTrafficClass::bulk,
        };

        std::size_t serviced = 0U;
        bool allow_interactive_boost = true;
        while (!stop_requested_.load() &&
               serviced < config_.max_owner_commands_per_iteration) {
            std::shared_ptr<OwnerCommandBase> command;
            {
                std::scoped_lock lock(command_mutex_);
                if (pending_command_count_locked() == 0U) {
                    return;
                }
                auto &interactive_queue = command_queues_[traffic_index(
                    TransportTrafficClass::interactive)];
                // Reserve room for a scheduled selection after a boost. With
                // a one-command visit, use the weighted cursor directly;
                // otherwise sparse interactive arrivals could consume every
                // visit without ever advancing toward control or bulk.
                const bool room_after_boost =
                    serviced + 1U < config_.max_owner_commands_per_iteration;
                if (allow_interactive_boost && room_after_boost &&
                    interactive_boost_pending_ && !interactive_queue.empty()) {
                    command = std::move(interactive_queue.front());
                    interactive_queue.pop_front();
                    interactive_boost_pending_ = false;
                    allow_interactive_boost = false;
                } else {
                    interactive_boost_pending_ = false;
                    for (std::size_t attempt = 0U; attempt < schedule.size(); ++attempt) {
                        const TransportTrafficClass selected =
                            schedule[scheduler_slot_];
                        scheduler_slot_ =
                            (scheduler_slot_ + 1U) % schedule.size();
                        auto &queue = command_queues_[traffic_index(selected)];
                        if (!queue.empty()) {
                            command = std::move(queue.front());
                            queue.pop_front();
                            break;
                        }
                    }
                    allow_interactive_boost = true;
                }
                if (!command) {
                    // Every class occurs in the schedule, so reaching this
                    // branch would mean the queue accounting is inconsistent.
                    return;
                }
            }
            const auto wait = std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now() - command->queued_at());
            const bool executed = command->execute();
            if (executed) {
                const std::uint64_t wait_us = wait.count() <= 0
                    ? 0U
                    : static_cast<std::uint64_t>(wait.count());
                std::scoped_lock lock(command_mutex_);
                auto &stats = command_stats_[traffic_index(
                    command->traffic_class())];
                ++stats.executed_commands;
                stats.total_queue_wait_us =
                    wait_us > std::numeric_limits<std::uint64_t>::max() -
                                  stats.total_queue_wait_us
                        ? std::numeric_limits<std::uint64_t>::max()
                        : stats.total_queue_wait_us + wait_us;
                stats.maximum_queue_wait_us =
                    std::max(stats.maximum_queue_wait_us, wait_us);
                command_wait_histograms_[traffic_index(
                    command->traffic_class())].observe(wait_us);
            }
            ++serviced;
        }
        if (stop_requested_.load()) {
            cancel_pending_commands(
                Status{ErrorCode::unavailable,
                       "Tox transport stopped before operation began"});
        }
    }

    void cancel_pending_commands(const Status &reason) noexcept {
        std::array<std::deque<std::shared_ptr<OwnerCommandBase>>, 3U> pending;
        {
            std::scoped_lock lock(command_mutex_);
            pending.swap(command_queues_);
        }
        for (const auto &queue : pending) {
            for (const auto &command : queue) {
                static_cast<void>(command->cancel(reason));
            }
        }
    }

    void emit(TransportEvent event) {
        std::unique_lock lock(event_mutex_);
        const bool required = event_requires_delivery(event.kind);
        std::optional<std::chrono::steady_clock::time_point>
            backpressure_started;

        auto oldest_observational = [this] {
            return std::find_if(events_.begin(), events_.end(), [](const TransportEvent &queued) {
                return !event_requires_delivery(queued.kind);
            });
        };

        while (events_.size() >= config_.max_pending_events) {
            const auto disposable = oldest_observational();
            if (disposable != events_.end()) {
                events_.erase(disposable);
                ++dropped_events_;
                break;
            }
            if (!required) {
                ++dropped_events_;
                return;
            }

            if (!backpressure_started) {
                backpressure_started = std::chrono::steady_clock::now();
            }

            // Friendship, application packets, and future transfer events must
            // not disappear merely because a consumer is briefly slow. Apply
            // bounded backpressure to the sole toxcore owner thread until the
            // consumer frees capacity or shutdown begins.
            event_space_cv_.wait(lock, [this] {
                return stop_requested_.load() ||
                       events_.size() < config_.max_pending_events ||
                       std::any_of(events_.begin(), events_.end(), [](const TransportEvent &queued) {
                           return !event_requires_delivery(queued.kind);
                       });
            });
            if (stop_requested_.load()) {
                return;
            }
        }

        event.dropped_events_before = dropped_events_;
        events_.push_back(std::move(event));
        maximum_pending_events_ = std::max(
            maximum_pending_events_, events_.size());
        if (backpressure_started) {
            const auto elapsed = std::chrono::duration_cast<
                std::chrono::microseconds>(
                std::chrono::steady_clock::now() - *backpressure_started);
            const std::uint64_t elapsed_us = elapsed.count() <= 0
                ? 0U
                : static_cast<std::uint64_t>(elapsed.count());
            saturating_increment(required_event_backpressure_count_);
            saturating_add(
                required_event_backpressure_total_us_, elapsed_us);
            required_event_backpressure_maximum_us_ = std::max(
                required_event_backpressure_maximum_us_, elapsed_us);
        }
        lock.unlock();
        event_cv_.notify_one();
    }

    static void on_self_connection(
        toxcore::abi::Tox *, toxcore::abi::Connection connection,
        void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        self->self_connection_ = connection;
        if (connection == toxcore::abi::kConnectionNone) {
            self->next_bootstrap_attempt_ =
                std::chrono::steady_clock::now() +
                self->config_.bootstrap_retry_interval;
        }
        self->emit({TransportEventKind::self_connection,
                    0U,
                    static_cast<int>(connection),
                    {},
                    {},
                    "self connection is " +
                        transport_connection_name(static_cast<int>(connection))});
    }

    static void on_friend_connection(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::Connection connection, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        self->friend_connections_[friend_number] = connection;
        if (connection == toxcore::abi::kConnectionNone) {
            static_cast<void>(
                self->erase_file_chunk_sources_for_friend(friend_number));
            const std::size_t abandoned =
                self->erase_sent_text_receipts_for_friend(friend_number);
            if (abandoned != 0U) {
                self->emit({
                    TransportEventKind::diagnostic,
                    friend_number,
                    static_cast<int>(connection),
                    {},
                    {},
                    "friend disconnected; abandoned " +
                        std::to_string(abandoned) +
                        " pending c-toxcore text receipt correlation(s) because "
                        "c-toxcore clears pending receipts on disconnect"});
            }
        }
        self->emit({TransportEventKind::friend_connection,
                    friend_number,
                    static_cast<int>(connection),
                    {},
                    {},
                    "friend connection is " +
                        transport_connection_name(static_cast<int>(connection))});
    }

    static void on_friend_name(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        const std::uint8_t *name, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if ((name == nullptr && length != 0U) ||
            length > toxcore::abi::kMaxNameLength) {
            self->emit({TransportEventKind::diagnostic,
                        friend_number,
                        0,
                        {},
                        {},
                        "rejected malformed friend-name callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::friend_name;
        event.friend_number = friend_number;
        if (length != 0U) {
            event.data.assign(name, name + length);
        }
        event.message = "friend transport nickname changed";
        self->emit(std::move(event));
    }

    static void on_friend_status_message(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        const std::uint8_t *message, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if ((message == nullptr && length != 0U) ||
            length > toxcore::abi::kMaxStatusMessageLength) {
            self->emit({TransportEventKind::diagnostic,
                        friend_number,
                        0,
                        {},
                        {},
                        "rejected malformed friend-status-message callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::friend_status_message;
        event.friend_number = friend_number;
        if (length != 0U) {
            event.data.assign(message, message + length);
        }
        event.message = "friend transport status message changed";
        self->emit(std::move(event));
    }

    static void on_friend_status(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::UserStatus status, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        const PresenceStatus converted = from_abi_status(status);
        self->friend_statuses_[friend_number] = converted;
        TransportEvent event;
        event.kind = TransportEventKind::friend_status;
        event.friend_number = friend_number;
        event.presence_status = converted;
        event.message = "friend transport presence changed to " +
                        to_string(converted);
        self->emit(std::move(event));
    }

    static void on_friend_typing(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        bool typing, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        self->friend_typing_[friend_number] = typing;
        TransportEvent event;
        event.kind = TransportEventKind::friend_typing;
        event.friend_number = friend_number;
        event.typing = typing;
        event.message = typing ? "friend is typing" : "friend stopped typing";
        self->emit(std::move(event));
    }

    static void on_friend_message(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::MessageType type, const std::uint8_t *message,
        std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        const auto kind = from_abi_message_type(type);
        if (!kind || message == nullptr || length == 0U ||
            length > toxcore::abi::kMaxMessageLength) {
            self->emit({TransportEventKind::diagnostic,
                        friend_number,
                        0,
                        {},
                        {},
                        "rejected malformed friend-message callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::friend_message;
        event.friend_number = friend_number;
        event.text_kind = *kind;
        event.data.assign(message, message + length);
        event.message = "friend text message received";
        self->emit(std::move(event));
    }

    static void on_friend_read_receipt(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FriendMessageId message_id, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        TransportEvent event;
        event.kind = TransportEventKind::friend_read_receipt;
        event.friend_number = friend_number;
        event.message_id = message_id;
        const auto found = self->sent_message_kinds_.find(
            text_message_key(friend_number, message_id));
        if (found != self->sent_message_kinds_.end()) {
            event.text_kind = found->second;
            self->sent_message_kinds_.erase(found);
        }
        event.message =
            "friend received the Tox text message; no IoTox command execution is implied";
        self->emit(std::move(event));
    }

    static void on_friend_request(
        toxcore::abi::Tox *, const std::uint8_t *public_key,
        const std::uint8_t *message, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if (public_key == nullptr ||
            (message == nullptr && length != 0U) ||
            length > toxcore::abi::kMaxFriendRequestLength) {
            self->emit({TransportEventKind::diagnostic,
                        0U,
                        0,
                        {},
                        {},
                        "rejected malformed friend-request callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::friend_request;
        event.public_key.assign(
            public_key,
            public_key + toxcore::abi::kPublicKeySize);
        if (length != 0U) {
            event.data.assign(message, message + length);
        }
        event.message =
            "friend request received; explicit acceptance and application authorization are required";
        self->emit(std::move(event));
    }

    static void on_lossless_packet(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        const std::uint8_t *data, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if (data == nullptr || length == 0U ||
            length > toxcore::abi::kMaxCustomPacketSize) {
            self->emit({TransportEventKind::diagnostic,
                        friend_number,
                        0,
                        {},
                        {},
                        "rejected malformed lossless-packet callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::lossless_packet;
        event.friend_number = friend_number;
        event.data.assign(data, data + length);
        event.message = "lossless packet received";
        self->emit(std::move(event));
    }

    static void on_lossy_packet(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        const std::uint8_t *data, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if (data == nullptr || length == 0U ||
            length > toxcore::abi::kMaxCustomPacketSize) {
            self->emit({TransportEventKind::diagnostic,
                        friend_number,
                        0,
                        {},
                        {},
                        "rejected malformed lossy-packet callback from c-toxcore"});
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::lossy_packet;
        event.friend_number = friend_number;
        event.data.assign(data, data + length);
        event.message = "lossy packet received";
        self->emit(std::move(event));
    }

    static void on_file_control(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FileNumber file_number,
        toxcore::abi::FileControl control, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        const auto translated = from_abi_control(control);
        if (!translated) {
            TransportEvent diagnostic;
            diagnostic.kind = TransportEventKind::diagnostic;
            diagnostic.friend_number = friend_number;
            diagnostic.file_number = file_number;
            diagnostic.message =
                "rejected unknown file-control callback from c-toxcore";
            self->emit(std::move(diagnostic));
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::file_control;
        event.friend_number = friend_number;
        event.file_number = file_number;
        event.file_control = *translated;
        event.message = "file control received: " + to_string(*translated);
        if (*translated == TransferControl::cancel) {
            const std::uint64_t key =
                file_transfer_key(friend_number, file_number);
            self->file_chunk_sources_.erase(key);
            self->forget_paced_file_on_owner_thread(key);
        }
        self->emit(std::move(event));
    }

    static void on_file_chunk_request(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FileNumber file_number, std::uint64_t position,
        std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        TransportEvent event;
        event.kind = TransportEventKind::file_chunk_request;
        event.friend_number = friend_number;
        event.file_number = file_number;
        event.file_position = position;
        event.requested_length = length;
        const std::uint64_t key = file_transfer_key(friend_number, file_number);
        if (length == 0U) {
            self->file_chunk_sources_.erase(key);
            self->forget_paced_file_on_owner_thread(key);
            event.message = "file sender completed";
            self->emit(std::move(event));
            return;
        }

        const auto source = self->file_chunk_sources_.find(key);
        if (source == self->file_chunk_sources_.end()) {
            event.message = "file chunk requested";
            self->emit(std::move(event));
            return;
        }

        event.file_chunk_source_attempted = true;
        Result<std::vector<std::uint8_t>> chunk{Status{
            ErrorCode::internal_error, "file chunk source did not run"}};
        try {
            chunk = source->second.source(position, length);
        } catch (const std::exception &exception) {
            chunk = Status{
                ErrorCode::internal_error,
                "file chunk source raised an exception: " +
                    std::string(exception.what())};
        } catch (...) {
            chunk = Status{ErrorCode::internal_error,
                           "file chunk source raised an unknown exception"};
        }

        if (!chunk) {
            event.file_chunk_status = chunk.status();
        } else if (chunk.value().size() != length) {
            event.file_chunk_status = Status{
                ErrorCode::invalid_argument,
                "file chunk source returned " +
                    std::to_string(chunk.value().size()) + " bytes for a " +
                    std::to_string(length) + "-byte request"};
        } else {
            toxcore::abi::FileSendChunkError error =
                toxcore::abi::kFileSendChunkOk;
            const bool sent = self->library_->api().file_send_chunk(
                self->tox_, friend_number, file_number, position,
                chunk.value().data(), chunk.value().size(), &error);
            if (sent && error == toxcore::abi::kFileSendChunkOk) {
                event.file_chunk_sent_inline = true;
                event.file_chunk_status = Status::success();
            } else {
                event.file_chunk_status = file_chunk_failure(error);
            }
        }

        if (!event.file_chunk_sent_inline) {
            self->file_chunk_sources_.erase(key);
            self->forget_paced_file_on_owner_thread(key);
            // Without a successful synchronous response c-toxcore may request
            // the same position repeatedly during this iterate. Cancel now to
            // bound that failure and notify the remote peer; the event still
            // carries the original source/send error for diagnosis.
            toxcore::abi::FileControlError cancel_error =
                toxcore::abi::kFileControlOk;
            static_cast<void>(self->library_->api().file_control(
                self->tox_, friend_number, file_number,
                to_abi_control(TransferControl::cancel), &cancel_error));
            event.message = event.file_chunk_status.message();
        } else {
            event.message = "file chunk supplied synchronously";
        }
        const bool may_have_more = event.file_chunk_sent_inline &&
            (source->second.file_size ==
                 std::numeric_limits<std::uint64_t>::max() ||
             (length <= source->second.file_size &&
              position < source->second.file_size - length));
        self->emit(std::move(event));
        if (may_have_more) {
            self->maybe_schedule_file_pause_on_owner_thread(
                friend_number, file_number);
        }
    }

    static void on_file_offer(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FileNumber file_number, std::uint32_t kind,
        std::uint64_t file_size, const std::uint8_t *filename,
        std::size_t filename_length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if ((filename == nullptr && filename_length != 0U) ||
            filename_length > toxcore::abi::kMaxFilenameLength) {
            TransportEvent diagnostic;
            diagnostic.kind = TransportEventKind::diagnostic;
            diagnostic.friend_number = friend_number;
            diagnostic.file_number = file_number;
            diagnostic.message =
                "rejected malformed file-offer callback from c-toxcore";
            self->emit(std::move(diagnostic));
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::file_offer;
        event.friend_number = friend_number;
        event.file_number = file_number;
        event.file_kind = kind;
        event.file_size = file_size;
        if (filename_length != 0U) {
            event.filename.assign(filename, filename + filename_length);
        }
        event.message =
            "file offer received in paused state; explicit policy must resume or cancel";
        // Calling tox_file_get_file_id from inside tox_iterate would make the
        // public API re-entrant. Complete the offer after tox_iterate returns.
        self->deferred_file_offers_.push_back(std::move(event));
    }

    static void on_file_chunk(
        toxcore::abi::Tox *, toxcore::abi::FriendNumber friend_number,
        toxcore::abi::FileNumber file_number, std::uint64_t position,
        const std::uint8_t *data, std::size_t length, void *user_data) {
        auto *self = static_cast<Impl *>(user_data);
        if (data == nullptr && length != 0U) {
            TransportEvent diagnostic;
            diagnostic.kind = TransportEventKind::diagnostic;
            diagnostic.friend_number = friend_number;
            diagnostic.file_number = file_number;
            diagnostic.message =
                "rejected malformed file-chunk callback from c-toxcore";
            self->emit(std::move(diagnostic));
            return;
        }
        TransportEvent event;
        event.kind = TransportEventKind::file_chunk;
        event.friend_number = friend_number;
        event.file_number = file_number;
        event.file_position = position;
        if (length != 0U) {
            event.data.assign(data, data + length);
        }
        event.message = length == 0U ? "file receive completed"
                                     : "file chunk received";
        self->emit(std::move(event));
        if (length != 0U) {
            self->maybe_schedule_file_pause_on_owner_thread(
                friend_number, file_number);
        } else {
            self->forget_paced_file_on_owner_thread(
                file_transfer_key(friend_number, file_number));
        }
    }

    Config config_;
    std::atomic<bool> start_called_{false};
    std::atomic<bool> stop_requested_{false};
    std::atomic<bool> running_{false};
    std::atomic<std::uint64_t> iteration_count_{0U};
    std::atomic<std::uint32_t> requested_iteration_interval_ms_{0U};
    std::atomic<std::uint32_t> effective_iteration_interval_ms_{0U};
    std::atomic<std::uint32_t> maximum_iteration_interval_ms_{20U};
    std::thread worker_;
    std::promise<Status> startup_promise_;

    std::optional<toxcore::DynamicToxcore> library_;
    toxcore::abi::Tox *tox_{nullptr};
    toxcore::abi::Connection self_connection_{
        toxcore::abi::kConnectionNone};
    std::unordered_map<toxcore::abi::FriendNumber, toxcore::abi::Connection>
        friend_connections_;
    std::unordered_map<toxcore::abi::FriendNumber, PresenceStatus>
        friend_statuses_;
    std::unordered_map<toxcore::abi::FriendNumber, bool> friend_typing_;
    std::unordered_map<std::uint64_t, TextMessageKind> sent_message_kinds_;
    std::unordered_map<std::uint64_t, FileChunkSourceState>
        file_chunk_sources_;
    std::unordered_map<std::uint64_t, PendingFilePause>
        pending_file_pauses_;
    std::unordered_map<std::uint64_t, PacedFile> paced_files_;
    std::deque<TransportEvent> deferred_file_offers_;
    std::chrono::steady_clock::time_point next_bootstrap_attempt_{};

    mutable std::mutex identity_mutex_;
    std::string address_hex_;

    mutable std::mutex command_mutex_;
    std::condition_variable command_cv_;
    bool iteration_interval_changed_{false};
    bool file_pacing_wake_requested_{false};
    std::array<std::deque<std::shared_ptr<OwnerCommandBase>>, 3U>
        command_queues_;
    mutable std::array<TransportTrafficStats, 3U> command_stats_{};
    std::array<LatencyHistogram, 3U> command_wait_histograms_{};

    mutable std::mutex sensitive_lossless_stats_mutex_;
    SensitiveLosslessTransportStats sensitive_lossless_stats_{};

    std::size_t scheduler_slot_{0U};
    bool interactive_boost_pending_{false};

    mutable std::mutex event_mutex_;
    std::condition_variable event_cv_;
    std::condition_variable event_space_cv_;
    std::deque<TransportEvent> events_;
    std::size_t maximum_pending_events_{0U};
    std::uint64_t dropped_events_{0U};
    std::uint64_t required_event_backpressure_count_{0U};
    std::uint64_t required_event_backpressure_total_us_{0U};
    std::uint64_t required_event_backpressure_maximum_us_{0U};

    std::atomic<std::size_t> file_pacing_paused_transfers_{0U};
    mutable std::mutex file_pacing_stats_mutex_;
    std::uint64_t file_pacing_pause_count_{0U};
    std::uint64_t file_pacing_resume_count_{0U};
    std::uint64_t file_pacing_resume_batch_count_{0U};
    std::size_t file_pacing_resume_batch_maximum_{0U};
    std::uint64_t file_pacing_external_pause_count_{0U};
    std::uint64_t file_pacing_pause_failure_count_{0U};
    std::uint64_t file_pacing_resume_failure_count_{0U};
    std::uint64_t file_pacing_total_hold_us_{0U};
    std::uint64_t file_pacing_maximum_hold_us_{0U};
};

ToxTransport::ToxTransport(Config config)
    : impl_(std::make_unique<Impl>(std::move(config))) {}
ToxTransport::~ToxTransport() = default;
Status ToxTransport::validate_route_config(const Config &config) {
    if (!config.network.implemented()) {
        return Status{
            ErrorCode::unsupported,
            config.network.name() +
                " is reserved by the architecture but not enabled in " +
                std::string(kRevision)};
    }
    if (config.network.tox_route == ToxRoute::native) {
        if (config.socks5_proxy) {
            return Status{
                ErrorCode::invalid_argument,
                "Tox/native refuses a SOCKS5 proxy; select an explicit strict routed-Tox network"};
        }
        return Status::success();
    }
    if (!is_strict_socks_tox_route(config.network.tox_route)) {
        return Status{ErrorCode::unsupported,
                      config.network.name() + " is not implemented"};
    }
    const std::string route_name = config.network.name();
    if (!config.socks5_proxy || config.socks5_proxy->port == 0U ||
        !is_numeric_ip_address(config.socks5_proxy->host)) {
        return Status{
            ErrorCode::invalid_argument,
            route_name + " requires one numeric --socks5-proxy IP:PORT"};
    }
    if (config.native_udp_enabled) {
        return Status{
            ErrorCode::invalid_argument,
            route_name + " requires UDP, discovery, announcements, and hole punching disabled"};
    }
    if (config.bootstrap_nodes.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            route_name + " requires at least one explicit numeric bootstrap record for TCP-only paths"};
    }
    if (config.tcp_relays.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            route_name + " requires at least one explicit numeric TCP relay"};
    }
    for (const toxcore::BootstrapEndpoint &bootstrap :
         config.bootstrap_nodes) {
        if (bootstrap.port == 0U ||
            !is_numeric_ip_address(bootstrap.host)) {
            return Status{
                ErrorCode::invalid_argument,
                route_name + " bootstrap records require a nonzero port and numeric IP address under disabled native DNS"};
        }
    }
    for (const toxcore::BootstrapEndpoint &relay : config.tcp_relays) {
        if (relay.port == 0U || !is_numeric_ip_address(relay.host)) {
            return Status{
                ErrorCode::invalid_argument,
                route_name + " TCP relays require a nonzero port and numeric IP address because c-toxcore SOCKS5 does not proxy relay DNS"};
        }
    }
    return Status::success();
}
Status ToxTransport::start() { return impl_->start(); }
void ToxTransport::stop() { impl_->stop(); }
Status ToxTransport::set_maximum_iteration_interval(
    std::chrono::milliseconds interval) {
    return impl_->set_maximum_iteration_interval(interval);
}
Status ToxTransport::expect_public_key(
    const std::array<std::uint8_t, toxcore::abi::kPublicKeySize> &key) {
    return impl_->expect_public_key(key);
}
bool ToxTransport::running() const noexcept { return impl_->running(); }
std::string ToxTransport::address_hex() const { return impl_->address_hex(); }
Result<SelfProfile> ToxTransport::self_profile() { return impl_->self_profile(); }
Status ToxTransport::set_self_name(const std::vector<std::uint8_t> &name) {
    return impl_->set_self_name(name);
}
Status ToxTransport::set_self_status_message(
    const std::vector<std::uint8_t> &status_message) {
    return impl_->set_self_status_message(status_message);
}
Status ToxTransport::set_self_status(PresenceStatus status) {
    return impl_->set_self_status(status);
}
Result<std::uint32_t> ToxTransport::request_friend(
    const std::vector<std::uint8_t> &address,
    const std::vector<std::uint8_t> &message) {
    return impl_->request_friend(address, message);
}
Result<std::uint32_t> ToxTransport::accept_friend(
    const std::vector<std::uint8_t> &public_key) {
    return impl_->accept_friend(public_key);
}
Status ToxTransport::remove_friend(std::uint32_t friend_number) {
    return impl_->remove_friend(friend_number);
}
Result<std::uint32_t> ToxTransport::remove_friend_by_public_key(
    const std::vector<std::uint8_t> &public_key) {
    return impl_->remove_friend_by_public_key(public_key);
}
Result<std::vector<TransportPeer>> ToxTransport::list_friends() {
    return impl_->list_friends();
}
Result<std::uint32_t> ToxTransport::send_message(
    std::uint32_t friend_number, TextMessageKind kind,
    const std::vector<std::uint8_t> &message) {
    return impl_->send_message(friend_number, kind, message);
}
Status ToxTransport::set_typing(std::uint32_t friend_number, bool typing) {
    return impl_->set_typing(friend_number, typing);
}
Status ToxTransport::send_lossless(
    std::uint32_t friend_number,
    const std::vector<std::uint8_t> &packet,
    TransportTrafficClass traffic_class) {
    return impl_->send_lossless(friend_number, packet, traffic_class);
}
Status ToxTransport::send_sensitive_lossless(
    std::uint32_t friend_number,
    std::span<const std::uint8_t> packet,
    TransportTrafficClass traffic_class) {
    return impl_->send_sensitive_lossless(
        friend_number, packet, traffic_class);
}
Status ToxTransport::send_lossy(
    std::uint32_t friend_number,
    const std::vector<std::uint8_t> &packet,
    TransportTrafficClass traffic_class) {
    return impl_->send_lossy(friend_number, packet, traffic_class);
}
Result<std::uint32_t> ToxTransport::offer_file(
    std::uint32_t friend_number, std::uint32_t kind,
    std::uint64_t file_size, const std::optional<FileId> &file_id,
    const std::vector<std::uint8_t> &filename,
    FileChunkSource chunk_source) {
    return impl_->offer_file(
        friend_number, kind, file_size, file_id, filename,
        std::move(chunk_source));
}
Status ToxTransport::control_file(
    std::uint32_t friend_number, std::uint32_t file_number,
    TransferControl control) {
    return impl_->control_file(friend_number, file_number, control);
}
Status ToxTransport::seek_file(
    std::uint32_t friend_number, std::uint32_t file_number,
    std::uint64_t position) {
    return impl_->seek_file(friend_number, file_number, position);
}
Result<FileId> ToxTransport::get_file_id(
    std::uint32_t friend_number, std::uint32_t file_number) {
    return impl_->get_file_id(friend_number, file_number);
}
Result<std::uint32_t> ToxTransport::find_file(
    std::uint32_t friend_number, const FileId &file_id) {
    return impl_->find_file(friend_number, file_id);
}
Status ToxTransport::send_file_chunk(
    std::uint32_t friend_number, std::uint32_t file_number,
    std::uint64_t position, const std::vector<std::uint8_t> &data) {
    return impl_->send_file_chunk(friend_number, file_number, position, data);
}
std::optional<TransportEvent> ToxTransport::poll_event(
    std::chrono::milliseconds timeout) {
    return impl_->poll_event(timeout);
}
TransportStats ToxTransport::stats() const { return impl_->stats(); }

std::string to_string(TransportEventKind kind) {
    switch (kind) {
        case TransportEventKind::backend_ready:
            return "backend-ready";
        case TransportEventKind::self_connection:
            return "self-connection";
        case TransportEventKind::friend_connection:
            return "friend-connection";
        case TransportEventKind::friend_request:
            return "friend-request";
        case TransportEventKind::friend_added:
            return "friend-added";
        case TransportEventKind::friend_removed:
            return "friend-removed";
        case TransportEventKind::friend_name:
            return "friend-name";
        case TransportEventKind::friend_status_message:
            return "friend-status-message";
        case TransportEventKind::friend_status:
            return "friend-status";
        case TransportEventKind::friend_typing:
            return "friend-typing";
        case TransportEventKind::message_sent:
            return "message-sent";
        case TransportEventKind::friend_message:
            return "friend-message";
        case TransportEventKind::friend_read_receipt:
            return "friend-read-receipt";
        case TransportEventKind::lossy_packet:
            return "lossy-packet";
        case TransportEventKind::lossless_packet:
            return "lossless-packet";
        case TransportEventKind::file_offer:
            return "file-offer";
        case TransportEventKind::file_control:
            return "file-control";
        case TransportEventKind::file_chunk_request:
            return "file-chunk-request";
        case TransportEventKind::file_chunk:
            return "file-chunk";
        case TransportEventKind::bootstrap:
            return "bootstrap";
        case TransportEventKind::tcp_relay:
            return "tcp-relay";
        case TransportEventKind::diagnostic:
            return "diagnostic";
    }
    return "unknown";
}

std::string to_string(TransferControl control) {
    switch (control) {
        case TransferControl::resume:
            return "resume";
        case TransferControl::pause:
            return "pause";
        case TransferControl::cancel:
            return "cancel";
    }
    return "unknown";
}

std::string to_string(PresenceStatus status) {
    switch (status) {
        case PresenceStatus::available:
            return "available";
        case PresenceStatus::away:
            return "away";
        case PresenceStatus::busy:
            return "busy";
    }
    return "unknown";
}

std::string to_string(TextMessageKind kind) {
    switch (kind) {
        case TextMessageKind::normal:
            return "normal";
        case TextMessageKind::action:
            return "action";
    }
    return "unknown";
}

std::string to_string(TransportTrafficClass traffic_class) {
    switch (traffic_class) {
        case TransportTrafficClass::interactive:
            return "interactive";
        case TransportTrafficClass::control:
            return "control";
        case TransportTrafficClass::bulk:
            return "bulk";
    }
    return "unknown";
}

std::string transport_connection_name(int connection_status) {
    switch (static_cast<toxcore::abi::Connection>(connection_status)) {
        case toxcore::abi::kConnectionNone:
            return "offline";
        case toxcore::abi::kConnectionTcp:
            return "tcp";
        case toxcore::abi::kConnectionUdp:
            return "udp";
        default:
            return "unknown(" + std::to_string(connection_status) + ")";
    }
}

std::string public_key_hex(
    const std::array<std::uint8_t, toxcore::abi::kPublicKeySize> &key) {
    return hex_encode(key.data(), key.size());
}

}  // namespace iotox
