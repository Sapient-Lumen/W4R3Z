#include "iotox/toxcore/abi.hpp"
#include "iotox/interactive.hpp"
#include "iotox/protocol/frame.hpp"
#include "iotox/protocol/ratox.hpp"
#include "iotox/protocol/session.hpp"
#include "iotox/protocol/command.hpp"
#include "iotox/route_binding.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/sync_content.hpp"
#include "iotox/sync_content_wire.hpp"
#include "iotox/sync_head.hpp"
#include "iotox/sync_wire.hpp"
#include "iotox/version.hpp"

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <array>
#include <chrono>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <limits>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>
#include <unordered_map>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

#if defined(__GNUC__) || defined(__clang__)
#define IOTOX_MOCK_EXPORT extern "C" __attribute__((visibility("default")))
#else
#define IOTOX_MOCK_EXPORT extern "C"
#endif

namespace {

using iotox::toxcore::abi::FriendConnectionCallback;
using iotox::toxcore::abi::FriendLosslessPacketCallback;
using iotox::toxcore::abi::FriendMessageCallback;
using iotox::toxcore::abi::FriendMessageId;
using iotox::toxcore::abi::FriendNameCallback;
using iotox::toxcore::abi::FriendNumber;
using iotox::toxcore::abi::FriendReadReceiptCallback;
using iotox::toxcore::abi::FriendRequestCallback;
using iotox::toxcore::abi::FriendLossyPacketCallback;
using iotox::toxcore::abi::FriendStatusCallback;
using iotox::toxcore::abi::FriendStatusMessageCallback;
using iotox::toxcore::abi::FriendTypingCallback;
using iotox::toxcore::abi::FileChunkRequestCallback;
using iotox::toxcore::abi::FileNumber;
using iotox::toxcore::abi::FileRecvCallback;
using iotox::toxcore::abi::FileRecvChunkCallback;
using iotox::toxcore::abi::FileRecvControlCallback;
using iotox::toxcore::abi::SelfConnectionCallback;

constexpr std::array<std::uint8_t, 4> kSavedataMagicV1 = {'I', 'T', 'M', '1'};
constexpr std::array<std::uint8_t, 4> kSavedataMagicV2 = {'I', 'T', 'M', '2'};
constexpr std::array<std::uint8_t, 4> kSavedataMagicV3 = {'I', 'T', 'M', '3'};
constexpr std::size_t kSavedFriendRecordSize = 1U + iotox::toxcore::abi::kPublicKeySize;

struct PendingPacket {
    FriendNumber friend_number{0};
    std::vector<std::uint8_t> data;
};

struct PendingMessage {
    FriendNumber friend_number{0U};
    Tox_Message_Type type{TOX_MESSAGE_TYPE_NORMAL};
    FriendMessageId message_id{0U};
    std::vector<std::uint8_t> data;
};

struct PendingTyping {
    FriendNumber friend_number{0U};
    bool typing{false};
};

struct MockTransfer {
    FriendNumber friend_number{0U};
    FileNumber file_number{0U};
    std::uint32_t kind{0U};
    std::uint64_t file_size{0U};
    std::array<std::uint8_t, iotox::toxcore::abi::kFileIdLength> file_id{};
    std::vector<std::uint8_t> filename;
    std::uint64_t position{0U};
    std::size_t requested_length{0U};
    bool receiving{false};
    bool local_paused{false};
    bool peer_paused{false};
    bool file_id_read{false};
    bool finished{false};
    std::vector<std::uint8_t> sent_data;
    std::vector<std::uint8_t> incoming_data;
};

struct PendingFileChunkRequest {
    FriendNumber friend_number{0U};
    FileNumber file_number{0U};
    std::uint64_t position{0U};
    std::size_t length{0U};
};

struct PendingFileChunk {
    FriendNumber friend_number{0U};
    FileNumber file_number{0U};
    std::uint64_t position{0U};
    std::vector<std::uint8_t> data;
};

struct PendingIncomingFileOffer {
    FriendNumber friend_number{0U};
    FileNumber file_number{0U};
};

template <typename Error>
void set_error(Error *error, Error value) {
    if (error != nullptr) {
        *error = value;
    }
}

void write_u32(std::uint8_t *output, std::uint32_t value) {
    output[0] = static_cast<std::uint8_t>((value >> 24U) & 0xFFU);
    output[1] = static_cast<std::uint8_t>((value >> 16U) & 0xFFU);
    output[2] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
    output[3] = static_cast<std::uint8_t>(value & 0xFFU);
}

std::uint32_t read_u32(const std::uint8_t *input) {
    return (static_cast<std::uint32_t>(input[0]) << 24U) |
           (static_cast<std::uint32_t>(input[1]) << 16U) |
           (static_cast<std::uint32_t>(input[2]) << 8U) |
           static_cast<std::uint32_t>(input[3]);
}

std::string environment_value(const char *name) {
    const char *value = std::getenv(name);
    return value == nullptr ? std::string{} : std::string(value);
}

std::optional<std::vector<std::uint8_t>> read_mock_file(
    const std::string &path) {
    if (path.empty()) return std::nullopt;
    std::ifstream input(path, std::ios::binary);
    if (!input) return std::nullopt;
    std::vector<std::uint8_t> bytes;
    std::array<char, 4096U> buffer{};
    while (input) {
        input.read(buffer.data(),
                   static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0) {
            const auto amount = static_cast<std::size_t>(count);
            bytes.insert(bytes.end(), buffer.begin(),
                         buffer.begin() +
                             static_cast<std::ptrdiff_t>(amount));
        }
    }
    if (!input.eof()) return std::nullopt;
    return bytes;
}

std::chrono::milliseconds parse_mock_send_delay(const std::string &configured) {
    const char *text = configured.c_str();
    if (configured.empty()) {
        return std::chrono::milliseconds::zero();
    }
    char *end = nullptr;
    const unsigned long value = std::strtoul(text, &end, 10);
    if (end == text || *end != '\0' || value > 60000UL) {
        return std::chrono::milliseconds::zero();
    }
    return std::chrono::milliseconds(value);
}

std::uint32_t parse_mock_count(const std::string &configured) {
    if (configured.empty()) {
        return 0U;
    }
    char *end = nullptr;
    const unsigned long value = std::strtoul(configured.c_str(), &end, 10);
    if (end == configured.c_str() || *end != '\0' ||
        value > static_cast<unsigned long>(
                    std::numeric_limits<std::uint32_t>::max())) {
        return 0U;
    }
    return static_cast<std::uint32_t>(value);
}

}  // namespace

struct Tox_Options {
    bool udp_enabled{true};
    bool local_discovery_enabled{true};
    bool dht_announcements_enabled{true};
    bool hole_punching_enabled{true};
    bool experimental_disable_dns{false};
    Tox_Proxy_Type proxy_type{TOX_PROXY_TYPE_NONE};
    std::string proxy_host;
    std::uint16_t proxy_port{0U};
    Tox_Savedata_Type savedata_type{TOX_SAVEDATA_TYPE_NONE};
    std::vector<std::uint8_t> savedata;
};

struct MockIoToxPeerSession {
    std::unique_ptr<iotox::protocol::PeerSessionRegistry> protocol_registry;
    std::optional<iotox::protocol::Frame> authority_challenge_frame;
    std::optional<iotox::security::AuthorityChallenge> authority_challenge;
    std::optional<iotox::protocol::Frame> authority_proof_frame;
    std::optional<iotox::protocol::Frame> private_route_inventory_frame;
    std::optional<iotox::protocol::Frame> preauthority_describe_request;
    std::optional<iotox::protocol::Frame> authorized_describe_request;
    std::optional<iotox::protocol::Frame> authorized_profile_status_request;
    std::optional<iotox::protocol::Frame> authorized_update_stage_request;
    std::vector<std::uint8_t> peer_challenge_payload;
    std::vector<std::uint8_t> peer_private_route_inventory_payload;
    iotox::security::SigningPublicKey agent_principal{};
    bool agent_authority_proof_verified{false};
    bool preauthority_describe_denied{false};
    bool preauthority_describe_received{false};
    bool authorized_describe_succeeded{false};
    bool authorized_describe_received{false};
    bool authorized_describe_duplicate_sent{false};
    bool authorized_describe_duplicate_succeeded{false};
    std::vector<std::uint8_t> authorized_describe_result_packet;
    bool authorized_profile_status_received{false};
    bool authorized_profile_status_succeeded{false};
    bool authorized_profile_status_duplicate_sent{false};
    bool authorized_profile_status_duplicate_succeeded{false};
    std::vector<std::uint8_t> authorized_profile_status_result_packet;
    bool authorized_update_stage_received{false};
    bool authorized_update_stage_succeeded{false};
    bool authorized_update_stage_duplicate_sent{false};
    bool authorized_update_stage_duplicate_succeeded{false};
    std::vector<std::uint8_t> authorized_update_stage_result_packet;
    std::unordered_map<std::uint64_t, std::vector<std::uint8_t>>
        frozen_incoming_command_requests;
    std::unordered_map<std::uint64_t, std::vector<std::uint8_t>>
        frozen_incoming_command_receipts;
    std::unordered_map<std::uint64_t, std::vector<std::uint8_t>>
        frozen_incoming_command_results;
};

struct Tox {
    std::array<std::uint8_t, iotox::toxcore::abi::kAddressSize> address{};
    std::vector<std::uint8_t> name;
    std::vector<std::uint8_t> status_message;
    Tox_User_Status user_status{TOX_USER_STATUS_NONE};
    bool emitted_self_connection{false};
    bool suppress_self_connection{false};
    bool emitted_friend_request{false};
    bool emitted_file_offer{false};
    bool start_friends_offline{false};
    bool require_inline_file_chunks{false};
    bool advertise_ratox_interactive{false};
    bool emulate_ratox_host{false};
    bool emit_profile_status_command{false};
    std::string update_stage_head_file;
    bool stop_after_self_status_call{false};
    bool stopped_after_self_status_call{false};
    iotox::protocol::CommandRequest::ProfileStatus profile_status_command_desired{
        iotox::protocol::CommandRequest::ProfileStatus::away};
    iotox::protocol::CommandRequest::ProfileStatus remote_profile_status{
        iotox::protocol::CommandRequest::ProfileStatus::available};
    std::uint32_t remote_profile_status_applications{0U};
    std::uint32_t self_status_set_calls{0U};
    bool inside_file_chunk_request_callback{false};
    std::vector<std::optional<std::array<std::uint8_t, iotox::toxcore::abi::kPublicKeySize>>> friends;
    std::deque<FriendNumber> pending_friend_connections;
    std::deque<PendingPacket> pending_packets;
    std::deque<PendingPacket> pending_lossy_packets;
    std::unordered_map<FriendNumber, MockIoToxPeerSession> iotox_sessions;
    std::deque<PendingMessage> pending_messages;
    std::deque<std::pair<FriendNumber, FriendMessageId>> pending_receipts;
    std::deque<PendingTyping> pending_typing;
    FriendMessageId next_message_id{0U};
    std::vector<MockTransfer> transfers;
    FileNumber next_outgoing_file_number{0U};
    std::uint32_t next_incoming_file_slot{0U};
    std::deque<PendingFileChunkRequest> pending_file_chunk_requests;
    std::deque<PendingFileChunk> pending_file_chunks;
    std::deque<PendingIncomingFileOffer> pending_incoming_file_offers;
    std::chrono::milliseconds send_delay{0};
    std::uint32_t text_not_connected_failures{0U};
    std::uint32_t text_sendq_failures{0U};
    std::uint32_t text_disconnects_before_receipt{0U};
    std::uint32_t lossless_sendq_failures{0U};
    bool probe_sendq_failures_initialized{false};
    std::uint32_t probe_sendq_failures{0U};
    std::uint32_t hello_sendq_failures{0U};
    std::uint32_t confirmation_sendq_failures{0U};
    std::uint32_t hello_accepted_drops{0U};
    std::uint32_t confirmation_accepted_drops{0U};
    std::uint32_t authority_challenge_sendq_failures{0U};
    std::uint32_t authority_proof_sendq_failures{0U};
    std::uint32_t command_sendq_failures{0U};
    std::uint32_t command_result_sendq_failures_per_request{0U};
    std::uint32_t ratox_sendq_failures{0U};
    std::uint32_t ratox_open_result_sendq_failures{0U};
    std::vector<std::uint8_t> failed_authority_challenge;
    std::vector<std::uint8_t> failed_authority_proof;
    std::vector<std::uint8_t> failed_command;
    std::vector<std::uint8_t> failed_ratox_packet;
    std::vector<std::uint8_t> failed_ratox_open_result;
    std::unordered_map<std::uint64_t, std::uint32_t>
        command_result_sendq_remaining;
    std::unordered_map<std::uint64_t, std::vector<std::uint8_t>>
        frozen_command_results;
    std::optional<iotox::security::Sodium> sodium;
    std::optional<iotox::security::SigningKeyPair> authority_keys;
    std::optional<iotox::security::DeviceIdentity> device_identity;
    std::string authority_audit_path;
    std::string capture_sent_file_path;
    std::string incoming_friend_request;
    std::string incoming_file;
    std::uint32_t incoming_file_count{1U};
    bool defer_incoming_file{false};
    std::uint32_t file_pause_already_paused_remaining{0U};
    std::string sync_namespace;
    std::optional<iotox::sync::SignedHead> sync_head;
    std::optional<iotox::sync::NamespacePolicy> sync_content_policy;
    std::vector<std::uint8_t> sync_artifact;
    std::vector<std::uint8_t> sync_manifest;
    std::uint32_t sync_disconnect_self_first_byte{256U};
    std::uint32_t sync_disconnect_after_file_bytes{0U};
    std::optional<FriendNumber> pending_sync_disconnect;
    std::optional<FriendNumber> pending_sync_disconnect_after_file_chunk;
    bool sync_disconnect_fired{false};

    SelfConnectionCallback *self_connection_callback{nullptr};
    FriendConnectionCallback *friend_connection_callback{nullptr};
    FriendNameCallback *friend_name_callback{nullptr};
    FriendStatusMessageCallback *friend_status_message_callback{nullptr};
    FriendStatusCallback *friend_status_callback{nullptr};
    FriendTypingCallback *friend_typing_callback{nullptr};
    FriendRequestCallback *friend_request_callback{nullptr};
    FriendMessageCallback *friend_message_callback{nullptr};
    FriendReadReceiptCallback *friend_read_receipt_callback{nullptr};
    FriendLossyPacketCallback *friend_lossy_packet_callback{nullptr};
    FriendLosslessPacketCallback *friend_lossless_packet_callback{nullptr};
    FileRecvControlCallback *file_recv_control_callback{nullptr};
    FileChunkRequestCallback *file_chunk_request_callback{nullptr};
    FileRecvCallback *file_recv_callback{nullptr};
    FileRecvChunkCallback *file_recv_chunk_callback{nullptr};
};

namespace {

FriendNumber add_friend_record(
    Tox *tox, const std::uint8_t *public_key, Tox_Err_Friend_Add *error) {
    using namespace iotox::toxcore;
    if (tox == nullptr || public_key == nullptr) {
        set_error(error, TOX_ERR_FRIEND_ADD_NULL);
        return abi::kFriendNumberFailure;
    }
    if (std::equal(public_key, public_key + abi::kPublicKeySize, tox->address.begin())) {
        set_error(error, TOX_ERR_FRIEND_ADD_OWN_KEY);
        return abi::kFriendNumberFailure;
    }
    for (std::size_t index = 0U; index < tox->friends.size(); ++index) {
        if (tox->friends[index] &&
            std::equal(public_key, public_key + abi::kPublicKeySize,
                       tox->friends[index]->begin())) {
            set_error(error, TOX_ERR_FRIEND_ADD_ALREADY_SENT);
            return abi::kFriendNumberFailure;
        }
    }

    std::array<std::uint8_t, abi::kPublicKeySize> key{};
    std::copy_n(public_key, key.size(), key.begin());
    std::size_t slot = 0U;
    for (; slot < tox->friends.size(); ++slot) {
        if (!tox->friends[slot]) {
            tox->friends[slot] = key;
            break;
        }
    }
    if (slot == tox->friends.size()) {
        tox->friends.push_back(key);
    }
    if (slot > std::numeric_limits<FriendNumber>::max()) {
        set_error(error, TOX_ERR_FRIEND_ADD_MALLOC);
        return abi::kFriendNumberFailure;
    }

    const auto friend_number = static_cast<FriendNumber>(slot);
    if (!tox->start_friends_offline) {
        tox->pending_friend_connections.push_back(friend_number);
    }
    set_error(error, TOX_ERR_FRIEND_ADD_OK);
    return friend_number;
}

bool valid_friend(const Tox *tox, FriendNumber friend_number) {
    return tox != nullptr && friend_number < tox->friends.size() &&
           tox->friends[friend_number].has_value();
}

std::vector<std::uint8_t> mock_friend_name(FriendNumber friend_number) {
    const std::string text = "mock-peer-" + std::to_string(friend_number);
    return {text.begin(), text.end()};
}

std::vector<std::uint8_t> mock_friend_status_message(FriendNumber friend_number) {
    const std::string text = "mock transport peer " + std::to_string(friend_number);
    return {text.begin(), text.end()};
}

Tox_User_Status mock_friend_status(FriendNumber friend_number) {
    switch (friend_number % 3U) {
        case 1U:
            return TOX_USER_STATUS_AWAY;
        case 2U:
            return TOX_USER_STATUS_BUSY;
        default:
            return TOX_USER_STATUS_NONE;
    }
}

bool load_v3_savedata(Tox *tox, const std::vector<std::uint8_t> &savedata) {
    using namespace iotox::toxcore;
    const std::size_t minimum = kSavedataMagicV3.size() + abi::kAddressSize +
                                sizeof(std::uint32_t) + sizeof(std::uint32_t) +
                                sizeof(std::uint32_t) + 1U;
    if (tox == nullptr || savedata.size() < minimum ||
        !std::equal(kSavedataMagicV3.begin(), kSavedataMagicV3.end(), savedata.begin())) {
        return false;
    }

    std::size_t offset = kSavedataMagicV3.size();
    const auto require = [&savedata, &offset](std::size_t count) {
        return offset <= savedata.size() && count <= savedata.size() - offset;
    };
    if (!require(tox->address.size())) {
        return false;
    }
    std::copy_n(savedata.begin() + static_cast<std::ptrdiff_t>(offset),
                tox->address.size(), tox->address.begin());
    offset += tox->address.size();

    if (!require(sizeof(std::uint32_t))) {
        return false;
    }
    const std::uint32_t slots = read_u32(savedata.data() + offset);
    offset += sizeof(std::uint32_t);
    if (static_cast<std::size_t>(slots) >
        (savedata.size() - offset) / kSavedFriendRecordSize) {
        return false;
    }
    tox->friends.resize(slots);
    for (std::uint32_t index = 0U; index < slots; ++index) {
        if (!require(kSavedFriendRecordSize)) {
            return false;
        }
        const bool present = savedata[offset] != 0U;
        ++offset;
        if (present) {
            std::array<std::uint8_t, abi::kPublicKeySize> key{};
            std::copy_n(savedata.begin() + static_cast<std::ptrdiff_t>(offset),
                        key.size(), key.begin());
            tox->friends[index] = key;
            if (!tox->start_friends_offline) {
                tox->pending_friend_connections.push_back(index);
            }
        }
        offset += abi::kPublicKeySize;
    }

    const auto read_bytes = [&savedata, &offset, &require](
                                std::size_t maximum,
                                std::vector<std::uint8_t> &destination) -> bool {
        if (!require(sizeof(std::uint32_t))) {
            return false;
        }
        const std::uint32_t length = read_u32(savedata.data() + offset);
        offset += sizeof(std::uint32_t);
        if (length > maximum || !require(length)) {
            return false;
        }
        destination.assign(
            savedata.begin() + static_cast<std::ptrdiff_t>(offset),
            savedata.begin() + static_cast<std::ptrdiff_t>(offset + length));
        offset += length;
        return true;
    };
    if (!read_bytes(abi::kMaxNameLength, tox->name) ||
        !read_bytes(abi::kMaxStatusMessageLength, tox->status_message) ||
        !require(1U)) {
        return false;
    }
    const std::uint8_t raw_status = savedata[offset++];
    if (raw_status > static_cast<std::uint8_t>(TOX_USER_STATUS_BUSY) ||
        offset != savedata.size()) {
        return false;
    }
    tox->user_status = static_cast<Tox_User_Status>(raw_status);
    return true;
}

MockTransfer *find_transfer(
    Tox *tox, FriendNumber friend_number, FileNumber file_number) {
    if (tox == nullptr) {
        return nullptr;
    }
    const auto found = std::find_if(
        tox->transfers.begin(), tox->transfers.end(),
        [friend_number, file_number](const MockTransfer &transfer) {
            return transfer.friend_number == friend_number &&
                   transfer.file_number == file_number && !transfer.finished;
        });
    return found == tox->transfers.end() ? nullptr : &*found;
}

std::size_t next_request_length(const MockTransfer &transfer) {
    constexpr std::size_t kMockChunk = 4U;
    if (transfer.file_size == UINT64_MAX) {
        return kMockChunk;
    }
    if (transfer.position >= transfer.file_size) {
        return 0U;
    }
    const auto remaining = transfer.file_size - transfer.position;
    return static_cast<std::size_t>(std::min<std::uint64_t>(remaining, kMockChunk));
}

void capture_sent_file(const MockTransfer &transfer, const std::string &path) {
    if (path.empty()) {
        return;
    }
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0600);
    if (descriptor < 0) {
        return;
    }
    std::size_t offset = 0U;
    while (offset < transfer.sent_data.size()) {
        const ssize_t count = ::write(
            descriptor, transfer.sent_data.data() + offset,
            transfer.sent_data.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count <= 0) {
            break;
        }
        offset += static_cast<std::size_t>(count);
    }
    static_cast<void>(::fsync(descriptor));
    static_cast<void>(::close(descriptor));
}

std::string hex_bytes(std::span<const std::uint8_t> bytes) {
    static constexpr char kHex[] = "0123456789ABCDEF";
    std::string output;
    output.reserve(bytes.size() * 2U);
    for (const std::uint8_t byte : bytes) {
        output.push_back(kHex[(byte >> 4U) & 0x0FU]);
        output.push_back(kHex[byte & 0x0FU]);
    }
    return output;
}

std::uint64_t next_mock_protocol_message_id() {
    static std::atomic<std::uint64_t> sequence{0x4D4F434B00000001ULL};
    return sequence.fetch_add(1U);
}

iotox::protocol::SessionNonce mock_peer_nonce(
    std::span<const std::uint8_t> peer_key) {
    static std::atomic<std::uint64_t> sequence{1U};
    const std::uint64_t epoch = sequence.fetch_add(1U);
    iotox::protocol::SessionNonce nonce{};
    for (std::size_t index = 0U; index < nonce.size(); ++index) {
        const unsigned int shift =
            static_cast<unsigned int>((index % 8U) * 8U);
        const std::uint8_t epoch_byte =
            static_cast<std::uint8_t>((epoch >> shift) & 0xFFU);
        nonce[index] = static_cast<std::uint8_t>(
            peer_key[index % peer_key.size()] ^ epoch_byte ^
            static_cast<std::uint8_t>(0xA5U + index));
    }
    if (std::all_of(nonce.begin(), nonce.end(),
                    [](std::uint8_t value) { return value == 0U; })) {
        nonce.front() = 1U;
    }
    return nonce;
}

constexpr iotox::security::SigningSeed kMockAuthoritySeed{
    0x9D, 0x61, 0xB1, 0x9D, 0xEF, 0xFD, 0x5A, 0x60,
    0xBA, 0x84, 0x4A, 0xF4, 0x92, 0xEC, 0x2C, 0xC4,
    0x44, 0x49, 0xC5, 0x69, 0x7B, 0x32, 0x69, 0x19,
    0x70, 0x3B, 0xAC, 0x03, 0x1C, 0xAE, 0x7F, 0x60,
};

constexpr iotox::security::SigningPublicKey kMockAuthorityPublicKey{
    0xD7, 0x5A, 0x98, 0x01, 0x82, 0xB1, 0x0A, 0xB7,
    0xD5, 0x4B, 0xFE, 0xD3, 0xC9, 0x64, 0x07, 0x3A,
    0x0E, 0xE1, 0x72, 0xF3, 0xDA, 0xA6, 0x23, 0x25,
    0xAF, 0x02, 0x1A, 0x68, 0xF7, 0x07, 0x51, 0x1A,
};

iotox::Result<iotox::security::DeviceIdentity> mock_device_identity(
    const iotox::security::Sodium &sodium) {
    std::array<std::uint8_t, iotox::security::kDeviceIdentityFileBytes> bytes{};
    constexpr std::array<std::uint8_t, 8U> magic{
        'I', 'O', 'T', 'O', 'X', 'I', 'D', '1'};
    std::copy(magic.begin(), magic.end(), bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = 1U;
    std::copy(kMockAuthoritySeed.begin(), kMockAuthoritySeed.end(),
              bytes.begin() + 16U);
    std::copy(kMockAuthorityPublicKey.begin(), kMockAuthorityPublicKey.end(),
              bytes.begin() + 48U);
    char path[] = "/tmp/iotox-mock-device-XXXXXX";
    const int descriptor = ::mkstemp(path);
    if (descriptor < 0 ||
        ::fchmod(descriptor, static_cast<mode_t>(0600)) != 0) {
        if (descriptor >= 0) static_cast<void>(::close(descriptor));
        if (descriptor >= 0) static_cast<void>(::unlink(path));
        return iotox::Status{iotox::ErrorCode::io_error,
                             "mock device identity creation failed"};
    }
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t written = ::write(
            descriptor, bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (written < 0 && errno == EINTR) continue;
        if (written <= 0) break;
        offset += static_cast<std::size_t>(written);
    }
    const bool complete = offset == bytes.size();
    const int closed = ::close(descriptor);
    if (!complete || closed != 0) {
        static_cast<void>(::unlink(path));
        return iotox::Status{iotox::ErrorCode::io_error,
                             "mock device identity write failed"};
    }
    auto identity = iotox::security::DeviceIdentity::load(path, sodium);
    static_cast<void>(::unlink(path));
    return identity;
}

struct MockPeerOutcome {
    bool handled{false};
    std::vector<std::vector<std::uint8_t>> replies;
};

std::uint64_t unix_time_ms() {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch())
            .count());
}

bool exact_retry_sendq(
    std::uint32_t &remaining_failures,
    std::vector<std::uint8_t> &frozen_failed_packet,
    std::span<const std::uint8_t> outgoing,
    Tox_Err_Friend_Custom_Packet *error) {
    if (!frozen_failed_packet.empty() &&
        (frozen_failed_packet.size() != outgoing.size() ||
         !std::equal(outgoing.begin(), outgoing.end(),
                     frozen_failed_packet.begin(), frozen_failed_packet.end()))) {
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_INVALID);
        return true;
    }
    if (remaining_failures != 0U) {
        if (frozen_failed_packet.empty()) {
            frozen_failed_packet.assign(outgoing.begin(), outgoing.end());
        }
        --remaining_failures;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
        return true;
    }
    frozen_failed_packet.clear();
    return false;
}

void append_authority_audit(const Tox &tox, std::string_view line) {
    if (tox.authority_audit_path.empty()) {
        return;
    }
    const int descriptor = ::open(
        tox.authority_audit_path.c_str(),
        O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0600);
    if (descriptor < 0) {
        return;
    }
    const std::string record = std::string(line) + "\n";
    std::size_t offset = 0U;
    while (offset < record.size()) {
        const ssize_t count = ::write(
            descriptor, record.data() + offset, record.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count <= 0) {
            break;
        }
        offset += static_cast<std::size_t>(count);
    }
    static_cast<void>(::fsync(descriptor));
    static_cast<void>(::close(descriptor));
}

std::optional<std::vector<std::uint8_t>> encode_frame_bytes(
    const iotox::protocol::Frame &frame) {
    auto encoded = iotox::protocol::encode(frame);
    if (!encoded) {
        return std::nullopt;
    }
    return std::move(encoded).value();
}

std::optional<iotox::protocol::PeerSessionSnapshot> mock_session_snapshot(
    MockIoToxPeerSession &session, FriendNumber friend_number) {
    if (!session.protocol_registry) {
        return std::nullopt;
    }
    auto snapshot = session.protocol_registry->get(friend_number);
    if (!snapshot) {
        return std::nullopt;
    }
    return snapshot.value();
}

std::optional<iotox::protocol::Frame> make_mock_authority_challenge(
    Tox &tox, MockIoToxPeerSession &session,
    const iotox::protocol::PeerSessionSnapshot &snapshot) {
    using namespace iotox;
    if (!tox.sodium || !tox.authority_keys) {
        return std::nullopt;
    }
    if (session.authority_challenge_frame) {
        return session.authority_challenge_frame;
    }

    security::AuthorityChallenge challenge;
    challenge.verifier_device = tox.authority_keys->public_key();
    challenge.ownership_epoch = 1U;
    challenge.authority_sequence = 1U;
    auto tail = tox.sodium->hash(
        "iotox.mock.authority-tail.v1",
        std::span<const std::uint8_t>{tox.authority_keys->public_key()});
    auto transcript = security::authority_session_transcript_digest(
        snapshot, *tox.sodium);
    if (!tail || !transcript) {
        return std::nullopt;
    }
    challenge.authority_tail_digest = tail.value();
    challenge.session_transcript_digest = transcript.value();
    auto nonce = tox.sodium->hash(
        "iotox.mock.authority-nonce.v1",
        std::span<const std::uint8_t>{challenge.session_transcript_digest});
    if (!nonce) {
        return std::nullopt;
    }
    challenge.nonce = nonce.value();

    auto payload = security::encode_authority_challenge(challenge);
    if (!payload) {
        return std::nullopt;
    }
    protocol::Frame frame;
    frame.major = snapshot.negotiated.selected.major;
    frame.minor = snapshot.negotiated.selected.minor;
    frame.type = protocol::MessageType::authority_challenge;
    frame.message_id = next_mock_protocol_message_id();
    frame.correlation_id = snapshot.peer_confirmation_message_id;
    frame.sequence = security::kAuthorityChallengeSequence;
    frame.payload.assign(payload.value().begin(), payload.value().end());
    session.authority_challenge = challenge;
    session.authority_challenge_frame = frame;
    return frame;
}

std::optional<iotox::protocol::Frame> make_mock_device_describe_request(
    const iotox::protocol::PeerSessionSnapshot &snapshot) {
    constexpr std::uint64_t kMockDurableSenderEpoch =
        0x4d4f434b00000001ULL;
    iotox::protocol::CommandRequest request;
    request.operation =
        iotox::protocol::CommandOperation::device_describe;
    auto payload = iotox::protocol::encode_command_request(request);
    if (!payload) {
        return std::nullopt;
    }
    iotox::protocol::Frame frame;
    frame.major = snapshot.negotiated.selected.major;
    frame.minor = snapshot.negotiated.selected.minor;
    frame.type = iotox::protocol::MessageType::command;
    frame.message_id = next_mock_protocol_message_id();
    frame.correlation_id = 0U;
    frame.sequence =
        (snapshot.negotiated.shared_features &
         iotox::protocol::feature_bit(
             iotox::protocol::Feature::durable_commands_v1)) != 0U
            ? kMockDurableSenderEpoch
            : 0U;
    frame.expiry_unix_ms = 0U;
    frame.payload.assign(payload.value().begin(), payload.value().end());
    return frame;
}

std::optional<iotox::protocol::Frame> make_mock_profile_status_request(
    const iotox::protocol::PeerSessionSnapshot &snapshot,
    iotox::protocol::CommandRequest::ProfileStatus desired) {
    constexpr std::uint64_t kMockDurableSenderEpoch =
        0x4d4f434b00000001ULL;
    iotox::protocol::CommandRequest request{
        iotox::protocol::CommandOperation::profile_status_set, desired};
    auto payload = iotox::protocol::encode_command_request(request);
    if (!payload) {
        return std::nullopt;
    }
    iotox::protocol::Frame frame;
    frame.major = snapshot.negotiated.selected.major;
    frame.minor = snapshot.negotiated.selected.minor;
    frame.type = iotox::protocol::MessageType::command;
    // Keep the fixture identity stable across mock-provider restarts while
    // assigning each bounded desired value a distinct durable command key.
    // This lets the process gate crash and recover one exact request without
    // colliding with the earlier away-state duplicate/replay fixture.
    frame.message_id = 0x5052465300000001ULL +
        static_cast<std::uint64_t>(desired);
    frame.correlation_id = 0U;
    frame.sequence = kMockDurableSenderEpoch;
    frame.expiry_unix_ms = 0U;
    frame.payload.assign(payload.value().begin(), payload.value().end());
    return frame;
}

std::optional<iotox::protocol::Frame> make_mock_update_stage_request(
    const iotox::protocol::PeerSessionSnapshot &snapshot,
    const iotox::protocol::UpdateHeadRecord &head) {
    constexpr std::uint64_t kMockDurableSenderEpoch =
        0x4d4f434b00000001ULL;
    iotox::protocol::CommandRequest request;
    request.operation = iotox::protocol::CommandOperation::update_stage;
    request.expected_update_head = head;
    auto payload = iotox::protocol::encode_command_request(request);
    if (!payload) return std::nullopt;
    iotox::protocol::Frame frame;
    frame.major = snapshot.negotiated.selected.major;
    frame.minor = snapshot.negotiated.selected.minor;
    frame.type = iotox::protocol::MessageType::command;
    frame.message_id = 0x5550445300000001ULL;
    frame.sequence = kMockDurableSenderEpoch;
    frame.payload = std::move(payload).value();
    return frame;
}

void write_ratox_u16(
    std::span<std::uint8_t> output, std::uint16_t value) {
    output[0U] = static_cast<std::uint8_t>(value >> 8U);
    output[1U] = static_cast<std::uint8_t>(value);
}

void write_ratox_u64(
    std::span<std::uint8_t> output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[index] = static_cast<std::uint8_t>(
            value >> static_cast<unsigned>((7U - index) * 8U));
    }
}

std::uint64_t read_ratox_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (const std::uint8_t byte : input.first(8U)) {
        value = (value << 8U) | byte;
    }
    return value;
}

MockPeerOutcome mock_ratox_peer_packet(
    Tox *tox, FriendNumber friend_number,
    std::span<const std::uint8_t> packet) {
    using namespace iotox;
    MockPeerOutcome outcome;
    if (tox == nullptr || !tox->advertise_ratox_interactive ||
        !tox->emulate_ratox_host ||
        !valid_friend(tox, friend_number) || packet.empty() ||
        packet.front() != protocol::ratox::kPacketId) {
        return outcome;
    }
    auto decoded = protocol::ratox::decode(packet);
    if (!decoded) return outcome;
    const protocol::ratox::Frame &request = decoded.value();

    protocol::ratox::Frame response;
    response.message_id = request.message_id ^ 0x6D6F636B7261746FULL;
    if (response.message_id == 0U) response.message_id = 1U;
    response.correlation_id = request.message_id;
    response.session_id = request.session_id;
    response.principal_id = request.principal_id;
    response.attachment_nonce = request.attachment_nonce;
    response.incarnation = request.incarnation;
    response.generation = request.generation;

    switch (request.type) {
        case protocol::ratox::FrameType::open:
            response.type = protocol::ratox::FrameType::open_result;
            response.incarnation = 0x4D4F434B00000001ULL;
            response.generation = 1U;
            response.payload.resize(12U, 0U);
            response.payload[2U] = 1U;
            write_ratox_u16(
                std::span<std::uint8_t>{response.payload}.subspan(4U, 2U),
                80U);
            write_ratox_u16(
                std::span<std::uint8_t>{response.payload}.subspan(6U, 2U),
                24U);
            break;
        case protocol::ratox::FrameType::resume: {
            response.type = protocol::ratox::FrameType::resume_result;
            response.generation = request.generation + 1U;
            response.payload.resize(28U, 0U);
            const std::uint64_t input_base = read_ratox_u64(
                std::span<const std::uint8_t>{request.payload}.first(8U));
            const std::uint64_t output_base = read_ratox_u64(
                std::span<const std::uint8_t>{request.payload}.subspan(8U, 8U));
            write_ratox_u64(
                std::span<std::uint8_t>{response.payload}.subspan(4U, 8U),
                input_base);
            write_ratox_u64(
                std::span<std::uint8_t>{response.payload}.subspan(12U, 8U),
                output_base);
            write_ratox_u64(
                std::span<std::uint8_t>{response.payload}.subspan(20U, 8U),
                output_base);
            break;
        }
        case protocol::ratox::FrameType::ping:
            response.type = protocol::ratox::FrameType::pong;
            break;
        case protocol::ratox::FrameType::input:
            response.type = protocol::ratox::FrameType::input_ack;
            response.acknowledgement =
                request.sequence + request.payload.size();
            break;
        case protocol::ratox::FrameType::close:
            response.type = protocol::ratox::FrameType::exit_status;
            response.payload.resize(8U, 0U);
            break;
        case protocol::ratox::FrameType::attach:
        case protocol::ratox::FrameType::detach:
        case protocol::ratox::FrameType::output_ack:
        case protocol::ratox::FrameType::resize:
            outcome.handled = true;
            return outcome;
        case protocol::ratox::FrameType::open_result:
        case protocol::ratox::FrameType::attach_result:
        case protocol::ratox::FrameType::input_ack:
        case protocol::ratox::FrameType::output:
        case protocol::ratox::FrameType::pong:
        case protocol::ratox::FrameType::exit_status:
        case protocol::ratox::FrameType::resume_result:
        case protocol::ratox::FrameType::output_gap:
            return outcome;
    }
    auto encoded = protocol::ratox::encode(response);
    if (!encoded) return outcome;
    outcome.handled = true;
    outcome.replies.push_back(std::move(encoded).value());
    return outcome;
}

MockPeerOutcome mock_peer_packet(
    Tox *tox, FriendNumber friend_number,
    std::span<const std::uint8_t> packet) {
    using namespace iotox;
    MockPeerOutcome outcome;
    if (tox == nullptr || !valid_friend(tox, friend_number) ||
        packet.empty() || packet.front() != protocol::kToxLosslessPacketId) {
        return outcome;
    }
    auto decoded = protocol::decode(packet);
    if (!decoded) {
        return outcome;
    }
    const protocol::Frame incoming = decoded.value();
    MockIoToxPeerSession &session = tox->iotox_sessions[friend_number];
    const auto &peer_key = *tox->friends[friend_number];
    const std::string peer_key_hex = hex_bytes(peer_key);
    const std::string agent_key_hex = hex_bytes(
        std::span<const std::uint8_t>{tox->address}.first(
            toxcore::abi::kPublicKeySize));
    const std::uint64_t now = unix_time_ms();

    if (incoming.type == protocol::MessageType::hello) {
        auto agent_hello = protocol::decode_hello_payload(incoming.payload);
        if (!agent_hello) {
            return outcome;
        }
        outcome.handled = true;
        if (!session.protocol_registry) {
            session.protocol_registry =
                std::make_unique<protocol::PeerSessionRegistry>(
                    agent_hello.value().maximum_finite_file_bytes);
            std::uint64_t peer_features = protocol::kImplementedFeatureMask;
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::route_binding_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::route_binding_v1);
            }
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::private_route_binding_v2)) != 0U &&
                (peer_features & protocol::feature_bit(
                     protocol::Feature::route_binding_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::private_route_binding_v2);
            }
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::state_sync_v1);
            }
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_ranges_v1)) != 0U &&
                (peer_features & protocol::feature_bit(
                     protocol::Feature::state_sync_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::state_sync_ranges_v1);
            }
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::state_sync_content_v2)) != 0U &&
                (peer_features & protocol::feature_bit(
                     protocol::Feature::state_sync_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::state_sync_content_v2);
            }
            if ((agent_hello.value().supported_features &
                 protocol::feature_bit(
                     protocol::Feature::signed_ota_v1)) != 0U) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::signed_ota_v1);
            }
            if (tox->advertise_ratox_interactive) {
                peer_features |= protocol::feature_bit(
                    protocol::Feature::ratox_interactive_v1);
            }
            if (peer_features != protocol::kImplementedFeatureMask) {
                const Status features =
                    session.protocol_registry->set_supported_features(
                        peer_features);
                if (!features.ok()) {
                    session.protocol_registry.reset();
                    return outcome;
                }
            }
            const Status local_key =
                session.protocol_registry->set_local_public_key(peer_key_hex);
            const Status peer = session.protocol_registry->ensure_offline_peer(
                friend_number, agent_key_hex, now);
            auto online = session.protocol_registry->peer_online(
                friend_number, agent_key_hex, TOX_CONNECTION_UDP,
                mock_peer_nonce(peer_key), now);
            if (!local_key.ok() || !peer.ok() || !online) {
                session.protocol_registry.reset();
                return outcome;
            }
        }
        if (!session.protocol_registry->receive_hello(
                friend_number, agent_key_hex, incoming, now).ok()) {
            return outcome;
        }
        auto snapshot = session.protocol_registry->get(friend_number);
        if (!snapshot) {
            return outcome;
        }
        const std::uint64_t message_id =
            snapshot.value().local_hello_message_id == 0U
                ? next_mock_protocol_message_id()
                : snapshot.value().local_hello_message_id;
        auto reply = session.protocol_registry->make_hello_frame(
            friend_number, message_id);
        if (!reply || !session.protocol_registry->mark_hello_sent(
                          friend_number, reply.value().message_id, now).ok()) {
            return outcome;
        }
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) {
            outcome.replies.push_back(std::move(*encoded));
        }
        return outcome;
    }

    if (!session.protocol_registry) {
        return outcome;
    }

    if (incoming.type == protocol::MessageType::capabilities) {
        if (!session.protocol_registry->receive_confirmation(
                friend_number, agent_key_hex, incoming, now).ok()) {
            return outcome;
        }
        outcome.handled = true;
        auto snapshot = session.protocol_registry->get(friend_number);
        if (!snapshot) {
            return outcome;
        }
        const std::uint64_t message_id =
            snapshot.value().local_confirmation_message_id == 0U
                ? next_mock_protocol_message_id()
                : snapshot.value().local_confirmation_message_id;
        auto reply = session.protocol_registry->make_confirmation_frame(
            friend_number, message_id);
        if (!reply || !session.protocol_registry->mark_confirmation_sent(
                          friend_number, reply.value().message_id, now).ok()) {
            return outcome;
        }
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) {
            outcome.replies.push_back(std::move(*encoded));
        }
        snapshot = session.protocol_registry->get(friend_number);
        if (!snapshot || !protocol::is_application_ready(snapshot.value())) {
            return outcome;
        }
        auto challenge = make_mock_authority_challenge(
            *tox, session, snapshot.value());
        if (challenge) {
            auto challenge_bytes = encode_frame_bytes(*challenge);
            if (challenge_bytes) {
                outcome.replies.push_back(std::move(*challenge_bytes));
            }
        }
        return outcome;
    }

    auto snapshot = mock_session_snapshot(session, friend_number);
    if (!snapshot || !protocol::is_application_ready(*snapshot)) {
        return outcome;
    }

    if (incoming.type == protocol::MessageType::route_binding) {
        outcome.handled = true;
        if (!tox->sodium || !tox->device_identity ||
            (snapshot->negotiated.shared_features & protocol::feature_bit(
                 protocol::Feature::route_binding_v1)) == 0U) {
            return outcome;
        }
        routes::ToxPublicKey coordinator_key{};
        coordinator_key.fill(0x42U);
        routes::ToxPublicKey member_key = peer_key;
        if (member_key == coordinator_key) return outcome;
        routes::RouteSet route_set;
        route_set.generation = 1U;
        route_set.stable_device_principal =
            tox->device_identity->public_key();
        route_set.coordinator_tox_public_key = coordinator_key;
        route_set.members = {
            {coordinator_key, routes::Role::protected_route,
             routes::ConnectionClass::tcp, 1U, 1U, 0U},
            {member_key, routes::Role::bulk,
             routes::ConnectionClass::tcp, 8U, 1U, 0U},
        };
        auto signed_set = routes::sign_route_set(
            route_set, *tox->device_identity);
        if (!signed_set) return outcome;
        auto reply = routes::make_route_binding_frame(
            signed_set.value(), route_set, member_key, *snapshot,
            *tox->device_identity, *tox->sodium,
            next_mock_protocol_message_id());
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type ==
        protocol::MessageType::private_route_member_binding) {
        outcome.handled = true;
        if (!tox->sodium || !tox->device_identity ||
            incoming.payload.size() !=
                routes::kPrivateRouteMemberBindingArtifactBytes ||
            (snapshot->negotiated.shared_features & protocol::feature_bit(
                 protocol::Feature::private_route_binding_v2)) == 0U) {
            return outcome;
        }

        const auto read_u64_be = [](std::span<const std::uint8_t> bytes,
                                    std::size_t offset) {
            std::uint64_t value = 0U;
            for (std::size_t index = 0U; index < 8U; ++index) {
                value = (value << 8U) | bytes[offset + index];
            }
            return value;
        };
        routes::PrivateRouteInventory expected_agent_inventory;
        expected_agent_inventory.route_set.generation =
            read_u64_be(incoming.payload, 16U);
        std::copy_n(incoming.payload.begin() + 24U,
                    expected_agent_inventory.route_set.
                        stable_device_principal.size(),
                    expected_agent_inventory.route_set.
                        stable_device_principal.begin());
        std::copy_n(incoming.payload.begin() + 56U,
                    expected_agent_inventory.route_set.
                        coordinator_tox_public_key.size(),
                    expected_agent_inventory.route_set.
                        coordinator_tox_public_key.begin());
        routes::ToxPublicKey agent_member_key{};
        std::copy_n(incoming.payload.begin() + 88U,
                    agent_member_key.size(), agent_member_key.begin());
        expected_agent_inventory.route_set.members = {
            {agent_member_key,
             static_cast<routes::Role>(incoming.payload[10U]),
             static_cast<routes::ConnectionClass>(incoming.payload[11U]),
             1U, 1U, 0U},
        };
        std::copy_n(incoming.payload.begin() + 152U,
                    expected_agent_inventory.artifact_digest.size(),
                    expected_agent_inventory.artifact_digest.begin());

        protocol::PeerSessionSnapshot primary = *snapshot;
        primary.friend_number = 77U;
        primary.online_epoch = 1U;
        primary.public_key = public_key_hex(
            expected_agent_inventory.route_set.
                coordinator_tox_public_key);
        routes::ToxPublicKey mock_coordinator_key{};
        mock_coordinator_key.fill(0x42U);
        primary.local_public_key =
            public_key_hex(mock_coordinator_key);
        expected_agent_inventory.primary_friend_number =
            primary.friend_number;
        expected_agent_inventory.primary_online_epoch =
            primary.online_epoch;

        security::PeerAuthoritySnapshot primary_authority;
        primary_authority.friend_number = primary.friend_number;
        primary_authority.transport_public_key = primary.public_key;
        primary_authority.online_epoch = primary.online_epoch;
        primary_authority.connected = true;
        primary_authority.feature_negotiated = true;
        primary_authority.remote_authorized = true;
        primary_authority.remote_principal =
            expected_agent_inventory.route_set.stable_device_principal;
        auto primary_digest =
            security::authority_session_transcript_digest(
                primary, *tox->sodium);
        if (!primary_digest) return outcome;
        primary_authority.session_transcript_digest =
            primary_digest.value();
        if (!routes::verify_private_route_member_binding_frame(
                 incoming, expected_agent_inventory, primary, *snapshot,
                 primary_authority, *tox->sodium).ok()) {
            return outcome;
        }
        append_authority_audit(
            *tox, "private-route-member-verified");

        routes::ToxPublicKey member_key = peer_key;
        if (member_key == mock_coordinator_key) return outcome;
        routes::RouteSet route_set;
        route_set.generation = 1U;
        route_set.stable_device_principal =
            tox->device_identity->public_key();
        route_set.coordinator_tox_public_key = mock_coordinator_key;
        route_set.members = {
            {mock_coordinator_key, routes::Role::protected_route,
             routes::ConnectionClass::tcp, 1U, 1U, 0U},
            {member_key, routes::Role::bulk,
             routes::ConnectionClass::tcp, 8U, 1U, 0U},
        };
        auto signed_set = routes::sign_route_set(
            route_set, *tox->device_identity);
        if (!signed_set) return outcome;
        auto reply = routes::make_private_route_member_binding_frame(
            signed_set.value(), route_set, member_key,
            expected_agent_inventory, primary, *snapshot,
            primary_authority, *tox->device_identity, *tox->sodium,
            next_mock_protocol_message_id());
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type ==
        protocol::MessageType::private_route_inventory) {
        outcome.handled = true;
        if (!tox->sodium || !tox->device_identity ||
            !session.agent_authority_proof_verified ||
            (snapshot->negotiated.shared_features & protocol::feature_bit(
                 protocol::Feature::private_route_binding_v2)) == 0U) {
            return outcome;
        }
        auto agent_routes = routes::verify_route_set(
            incoming.payload, session.agent_principal, 1U, *tox->sodium);
        routes::ToxPublicKey agent_coordinator{};
        std::copy_n(tox->address.begin(), agent_coordinator.size(),
                    agent_coordinator.begin());
        if (!agent_routes ||
            agent_routes.value().coordinator_tox_public_key !=
                agent_coordinator) {
            return outcome;
        }
        append_authority_audit(
            *tox, "private-route-inventory-verified");
        if (!session.peer_private_route_inventory_payload.empty() &&
            session.peer_private_route_inventory_payload !=
                incoming.payload) {
            return outcome;
        }
        session.peer_private_route_inventory_payload = incoming.payload;
        if (!session.private_route_inventory_frame) {
            routes::ToxPublicKey mock_coordinator{};
            mock_coordinator = peer_key;
            routes::ToxPublicKey mock_auxiliary{};
            mock_auxiliary.fill(0x43U);
            if (mock_auxiliary == mock_coordinator) return outcome;
            routes::RouteSet route_set;
            route_set.generation = 1U;
            route_set.stable_device_principal =
                tox->device_identity->public_key();
            route_set.coordinator_tox_public_key = mock_coordinator;
            route_set.members = {
                {mock_coordinator, routes::Role::protected_route,
                 routes::ConnectionClass::tcp, 1U, 1U, 0U},
                {mock_auxiliary, routes::Role::bulk,
                 routes::ConnectionClass::tcp, 8U, 1U, 0U},
            };
            auto signed_set = routes::sign_route_set(
                route_set, *tox->device_identity);
            if (!signed_set) return outcome;
            security::PeerAuthoritySnapshot primary_authority;
            primary_authority.friend_number = snapshot->friend_number;
            primary_authority.transport_public_key = snapshot->public_key;
            primary_authority.online_epoch = snapshot->online_epoch;
            primary_authority.connected = true;
            primary_authority.feature_negotiated = true;
            primary_authority.remote_authorized = true;
            primary_authority.remote_principal = session.agent_principal;
            auto transcript =
                security::authority_session_transcript_digest(
                    *snapshot, *tox->sodium);
            if (!transcript) return outcome;
            primary_authority.session_transcript_digest =
                transcript.value();
            auto reply = routes::make_private_route_inventory_frame(
                signed_set.value(), route_set, *snapshot,
                primary_authority, *tox->device_identity, *tox->sodium,
                next_mock_protocol_message_id());
            if (!reply) return outcome;
            session.private_route_inventory_frame =
                std::move(reply).value();
        }
        auto encoded = encode_frame_bytes(
            *session.private_route_inventory_frame);
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type == protocol::MessageType::authority_challenge) {
        outcome.handled = true;
        if (!tox->sodium || !tox->authority_keys ||
            !security::validate_authority_challenge_frame(
                *snapshot, incoming).ok()) {
            return outcome;
        }
        auto challenge = security::decode_authority_challenge(incoming.payload);
        auto transcript = security::authority_session_transcript_digest(
            *snapshot, *tox->sodium);
        if (!challenge || !transcript ||
            challenge.value().session_transcript_digest != transcript.value()) {
            return outcome;
        }
        if (!session.peer_challenge_payload.empty() &&
            (session.peer_challenge_payload != incoming.payload ||
             !session.authority_proof_frame ||
             session.authority_proof_frame->correlation_id != incoming.message_id)) {
            return outcome;
        }
        if (!session.authority_proof_frame) {
            security::AuthorityProof proof;
            proof.authority_format = challenge.value().authority_format;
            proof.verifier_device = challenge.value().verifier_device;
            proof.claimant_principal = tox->authority_keys->public_key();
            proof.ownership_epoch = challenge.value().ownership_epoch;
            proof.authority_sequence = challenge.value().authority_sequence;
            proof.authority_tail_digest = challenge.value().authority_tail_digest;
            proof.session_transcript_digest = challenge.value().session_transcript_digest;
            proof.challenge_nonce = challenge.value().nonce;
            proof.challenge_message_id = incoming.message_id;
            auto body = security::encode_authority_proof_body(proof);
            if (!body) {
                return outcome;
            }
            auto signed_proof = security::sign_authority_proof_body(
                body.value(), tox->authority_keys->secret_key(), *tox->sodium);
            if (!signed_proof) {
                return outcome;
            }
            protocol::Frame reply;
            reply.major = snapshot->negotiated.selected.major;
            reply.minor = snapshot->negotiated.selected.minor;
            reply.type = protocol::MessageType::authority_proof;
            reply.message_id = next_mock_protocol_message_id();
            reply.correlation_id = incoming.message_id;
            reply.sequence = security::kAuthorityProofSequence;
            reply.payload.assign(
                signed_proof.value().begin(), signed_proof.value().end());
            session.peer_challenge_payload = incoming.payload;
            session.authority_proof_frame = std::move(reply);
        }
        if (!session.preauthority_describe_request) {
            session.preauthority_describe_request =
                make_mock_device_describe_request(*snapshot);
        }
        if (session.preauthority_describe_request) {
            auto early = encode_frame_bytes(
                *session.preauthority_describe_request);
            if (early) {
                outcome.replies.push_back(std::move(*early));
            }
        }
        auto encoded = encode_frame_bytes(*session.authority_proof_frame);
        if (encoded) {
            outcome.replies.push_back(std::move(*encoded));
        }
        return outcome;
    }

    if (incoming.type == protocol::MessageType::authority_proof) {
        outcome.handled = true;
        if (!tox->sodium || !session.authority_challenge_frame ||
            !session.authority_challenge ||
            !security::validate_authority_proof_frame(
                *snapshot, session.authority_challenge_frame->message_id,
                incoming).ok()) {
            return outcome;
        }
        auto proof = security::decode_authority_proof(incoming.payload);
        if (!proof || !security::verify_authority_proof(
                          proof.value(), *tox->sodium).ok()) {
            return outcome;
        }
        const auto &challenge = *session.authority_challenge;
        if (proof.value().verifier_device != challenge.verifier_device ||
            proof.value().ownership_epoch != challenge.ownership_epoch ||
            proof.value().authority_sequence != challenge.authority_sequence ||
            proof.value().authority_tail_digest != challenge.authority_tail_digest ||
            proof.value().session_transcript_digest !=
                challenge.session_transcript_digest ||
            proof.value().challenge_nonce != challenge.nonce ||
            proof.value().challenge_message_id !=
                session.authority_challenge_frame->message_id) {
            return outcome;
        }
        session.agent_principal = proof.value().claimant_principal;
        session.agent_authority_proof_verified = true;
        append_authority_audit(
            *tox, "agent-proof-verified principal=" +
                      security::hex(proof.value().claimant_principal));
        if (!session.authorized_describe_request) {
            session.authorized_describe_request =
                make_mock_device_describe_request(*snapshot);
        }
        if (session.authorized_describe_request) {
            auto command = encode_frame_bytes(
                *session.authorized_describe_request);
            if (command) {
                outcome.replies.push_back(std::move(*command));
            }
        }
        if (tox->emit_profile_status_command &&
            !session.authorized_profile_status_request) {
            session.authorized_profile_status_request =
                make_mock_profile_status_request(
                    *snapshot, tox->profile_status_command_desired);
        }
        if (session.authorized_profile_status_request) {
            auto command = encode_frame_bytes(
                *session.authorized_profile_status_request);
            if (command) {
                outcome.replies.push_back(std::move(*command));
            }
        }
        return outcome;
    }

    if (incoming.type == protocol::MessageType::sync_head_request) {
        outcome.handled = true;
        if (!tox->sync_head ||
            !sync::validate_sync_head_request_frame(incoming).ok()) {
            return outcome;
        }
        auto request = sync::decode_sync_head_request(incoming.payload);
        if (!request) return outcome;
        sync::SyncHeadResult result;
        if (request.value().namespace_id == tox->sync_namespace) {
            result.status = sync::SyncHeadResultStatus::available;
            result.head = *tox->sync_head;
        } else {
            result.status = sync::SyncHeadResultStatus::absent;
        }
        auto reply = sync::make_sync_head_result_frame(
            result, next_mock_protocol_message_id(), incoming.message_id);
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type == protocol::MessageType::sync_object_request) {
        outcome.handled = true;
        if (!tox->sync_head || !tox->sodium ||
            !sync::validate_sync_object_request_frame(incoming).ok()) {
            return outcome;
        }
        auto request = sync::decode_sync_object_request(incoming.payload);
        auto head_record = sync::signed_head_record_digest(
            *tox->sync_head, *tox->sodium);
        if (!request || !head_record) return outcome;
        sync::SyncObjectResult result;
        result.kind = request.value().kind;
        result.head_record = request.value().head_record;
        result.transfer_id = request.value().transfer_id;
        result.status = sync::SyncObjectResultStatus::object_absent;
        if (request.value().namespace_id == tox->sync_namespace &&
            request.value().head_record == head_record.value()) {
            const std::vector<std::uint8_t> &bytes =
                request.value().kind == sync::SyncObjectKind::artifact
                    ? tox->sync_artifact
                    : tox->sync_manifest;
            MockTransfer transfer;
            transfer.friend_number = friend_number;
            const std::uint32_t slot = tox->next_incoming_file_slot++;
            transfer.file_number = (slot + 1U) << 16U;
            transfer.kind = toxcore::abi::kFileKindData;
            transfer.file_size = static_cast<std::uint64_t>(bytes.size());
            transfer.file_id = request.value().transfer_id;
            transfer.filename = {'i', 'g', 'n', 'o', 'r', 'e', 'd'};
            transfer.receiving = true;
            transfer.local_paused = true;
            transfer.incoming_data = bytes;
            tox->transfers.push_back(std::move(transfer));
            tox->pending_incoming_file_offers.push_back(
                {friend_number, tox->transfers.back().file_number});
            result.status = sync::SyncObjectResultStatus::offered;
        }
        auto reply = sync::make_sync_object_result_frame(
            result, next_mock_protocol_message_id(), incoming.message_id);
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        if (!tox->sync_disconnect_fired &&
            tox->sync_disconnect_self_first_byte <= 0xffU &&
            tox->sync_disconnect_after_file_bytes == 0U &&
            tox->address.front() == static_cast<std::uint8_t>(
                tox->sync_disconnect_self_first_byte)) {
            tox->sync_disconnect_fired = true;
            tox->pending_sync_disconnect = friend_number;
            append_authority_audit(
                *tox, "sync-forced-disconnect self-first-byte=" +
                          std::to_string(tox->address.front()) +
                          " friend=" + std::to_string(friend_number));
        }
        return outcome;
    }

    if (incoming.type == protocol::MessageType::sync_content_object_request) {
        outcome.handled = true;
        if (!tox->sync_head || !tox->sync_content_policy || !tox->sodium ||
            !sync::validate_sync_content_object_request_frame(incoming).ok()) {
            return outcome;
        }
        auto request =
            sync::decode_sync_content_object_request(incoming.payload);
        auto head_record = sync::signed_head_record_digest(
            *tox->sync_head, *tox->sodium);
        if (!request || !head_record) return outcome;
        sync::SyncContentObjectResult result;
        result.kind = request.value().kind;
        result.head_record = request.value().head_record;
        result.object = request.value().object;
        result.transfer_id = request.value().transfer_id;
        result.logical_index = request.value().logical_index;
        result.object_bytes = request.value().object_bytes;
        result.status = sync::SyncContentObjectResultStatus::object_absent;
        if (request.value().namespace_id == tox->sync_namespace &&
            request.value().head_record == head_record.value()) {
            auto resolved = sync::resolve_sync_content_object(
                *tox->sync_content_policy, *tox->sync_head,
                request.value().kind, request.value().logical_index);
            if (resolved && resolved.value().object == request.value().object &&
                resolved.value().object_bytes ==
                    request.value().object_bytes) {
                auto bytes = read_mock_file(resolved.value().path.string());
                if (bytes) {
                    MockTransfer transfer;
                    transfer.friend_number = friend_number;
                    const std::uint32_t slot = tox->next_incoming_file_slot++;
                    transfer.file_number = (slot + 1U) << 16U;
                    transfer.kind = toxcore::abi::kFileKindData;
                    transfer.file_size =
                        static_cast<std::uint64_t>(bytes->size());
                    transfer.file_id = request.value().transfer_id;
                    transfer.filename = {'i', 'g', 'n', 'o', 'r', 'e', 'd'};
                    transfer.receiving = true;
                    transfer.local_paused = true;
                    transfer.incoming_data = std::move(*bytes);
                    tox->transfers.push_back(std::move(transfer));
                    tox->pending_incoming_file_offers.push_back(
                        {friend_number,
                         tox->transfers.back().file_number});
                    result.status =
                        sync::SyncContentObjectResultStatus::offered;
                }
            }
        }
        auto reply = sync::make_sync_content_object_result_frame(
            result, next_mock_protocol_message_id(), incoming.message_id);
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type == protocol::MessageType::sync_range_request) {
        outcome.handled = true;
        if (!tox->sync_head || !tox->sodium ||
            !sync::validate_sync_range_request_frame(incoming).ok()) {
            return outcome;
        }
        auto request = sync::decode_sync_range_request(incoming.payload);
        auto head_record = sync::signed_head_record_digest(
            *tox->sync_head, *tox->sodium);
        if (!request || !head_record) return outcome;
        sync::SyncRangeResult result;
        result.head_record = request.value().head_record;
        result.transfer_id = request.value().transfer_id;
        result.status = sync::SyncRangeResultStatus::unavailable;
        std::vector<std::uint8_t> bundle;
        bool bounded = true;
        for (const sync::SyncRangeRecord &range : request.value().ranges) {
            if (range.offset > tox->sync_artifact.size() ||
                range.length > tox->sync_artifact.size() - range.offset) {
                bounded = false;
                break;
            }
            const auto begin = tox->sync_artifact.begin() +
                static_cast<std::ptrdiff_t>(range.offset);
            const auto end = begin +
                static_cast<std::ptrdiff_t>(range.length);
            bundle.insert(bundle.end(), begin, end);
        }
        if (request.value().namespace_id == tox->sync_namespace &&
            request.value().head_record == head_record.value() && bounded) {
            MockTransfer transfer;
            transfer.friend_number = friend_number;
            const std::uint32_t slot = tox->next_incoming_file_slot++;
            transfer.file_number = (slot + 1U) << 16U;
            transfer.kind = toxcore::abi::kFileKindData;
            transfer.file_size = static_cast<std::uint64_t>(bundle.size());
            transfer.file_id = request.value().transfer_id;
            transfer.filename = {'i', 'g', 'n', 'o', 'r', 'e', 'd'};
            transfer.receiving = true;
            transfer.local_paused = true;
            transfer.incoming_data = std::move(bundle);
            tox->transfers.push_back(std::move(transfer));
            tox->pending_incoming_file_offers.push_back(
                {friend_number, tox->transfers.back().file_number});
            result.status = sync::SyncRangeResultStatus::offered;
        }
        auto reply = sync::make_sync_range_result_frame(
            result, next_mock_protocol_message_id(), incoming.message_id);
        if (!reply) return outcome;
        auto encoded = encode_frame_bytes(reply.value());
        if (encoded) outcome.replies.push_back(std::move(*encoded));
        return outcome;
    }

    if (incoming.type == protocol::MessageType::command) {
        outcome.handled = true;
        const bool durable =
            (snapshot->negotiated.shared_features &
             protocol::feature_bit(
                 protocol::Feature::durable_commands_v1)) != 0U;
        auto request = protocol::decode_command_request(incoming.payload);
        if (!request || incoming.flags != 0U ||
            incoming.correlation_id != 0U ||
            (durable ? incoming.sequence == 0U
                     : incoming.sequence != 0U) ||
            incoming.expiry_unix_ms != 0U) {
            return outcome;
        }

        auto frozen_request =
            session.frozen_incoming_command_requests.find(
                incoming.message_id);
        if (frozen_request !=
            session.frozen_incoming_command_requests.end()) {
            if (frozen_request->second.size() != packet.size() ||
                !std::equal(packet.begin(), packet.end(),
                            frozen_request->second.begin())) {
                append_authority_audit(
                    *tox, "mock-command-key-conflict message-id=" +
                              std::to_string(incoming.message_id));
                return outcome;
            }
            const auto receipt =
                session.frozen_incoming_command_receipts.find(
                    incoming.message_id);
            if (receipt !=
                session.frozen_incoming_command_receipts.end()) {
                outcome.replies.push_back(receipt->second);
            }
            const auto result =
                session.frozen_incoming_command_results.find(
                    incoming.message_id);
            if (result !=
                session.frozen_incoming_command_results.end()) {
                outcome.replies.push_back(result->second);
            }
            append_authority_audit(
                *tox, "mock-command-duplicate-replayed-exact message-id=" +
                          std::to_string(incoming.message_id));
            return outcome;
        }

        session.frozen_incoming_command_requests.emplace(
            incoming.message_id,
            std::vector<std::uint8_t>(packet.begin(), packet.end()));
        if (durable) {
            auto receipt_payload = protocol::encode_command_receipt(
                protocol::CommandReceipt{
                    protocol::CommandReceiptStage::received});
            if (!receipt_payload) {
                return outcome;
            }
            protocol::Frame receipt;
            receipt.major = snapshot->negotiated.selected.major;
            receipt.minor = snapshot->negotiated.selected.minor;
            receipt.type = protocol::MessageType::acknowledgement;
            receipt.message_id = next_mock_protocol_message_id();
            receipt.correlation_id = incoming.message_id;
            receipt.sequence = incoming.sequence;
            receipt.expiry_unix_ms = 0U;
            receipt.payload.assign(
                receipt_payload.value().begin(),
                receipt_payload.value().end());
            auto encoded_receipt = encode_frame_bytes(receipt);
            if (!encoded_receipt) {
                return outcome;
            }
            session.frozen_incoming_command_receipts.emplace(
                incoming.message_id, *encoded_receipt);
            outcome.replies.push_back(std::move(*encoded_receipt));
        }

        protocol::CommandResultPayload result;
        result.operation = request.value().operation;
        if (!session.agent_authority_proof_verified ||
                   !tox->authority_keys) {
            result.outcome = protocol::CommandOutcome::denied;
        } else if (request.value().operation ==
                   protocol::CommandOperation::device_describe) {
            protocol::DeviceDescription description;
            description.revision_number = iotox::kRevisionNumber;
            description.version_major = iotox::kVersionMajor;
            description.version_minor = iotox::kVersionMinor;
            description.version_patch = iotox::kVersionPatch;
            description.protocol = snapshot->negotiated.selected;
            description.device_principal =
                tox->authority_keys->public_key();
            description.supported_features =
                protocol::kImplementedFeatureMask;
            description.offered_operations =
                protocol::implemented_operation_mask();
            auto description_bytes =
                protocol::encode_device_description(description);
            if (!description_bytes) {
                result.outcome =
                    protocol::CommandOutcome::internal_error;
            } else {
                result.outcome = protocol::CommandOutcome::succeeded;
                result.body.assign(description_bytes.value().begin(),
                                   description_bytes.value().end());
            }
        } else if (request.value().operation ==
                   protocol::CommandOperation::system_summary) {
            protocol::SystemSummary summary;
            summary.health = protocol::SystemHealth::healthy;
            summary.flags = protocol::kSystemSummaryKnownFlags;
            summary.uptime_minutes = 720U;
            summary.memory_total_64mib = 64U;
            summary.memory_available_64mib = 24U;
            summary.load_milli = 300U;
            summary.process_count = 42U;
            auto summary_bytes = protocol::encode_system_summary(summary);
            if (!summary_bytes) {
                result.outcome = protocol::CommandOutcome::internal_error;
            } else {
                result.outcome = protocol::CommandOutcome::succeeded;
                result.body.assign(summary_bytes.value().begin(),
                                   summary_bytes.value().end());
            }
        } else if (request.value().operation ==
                   protocol::CommandOperation::profile_status_set &&
                   request.value().desired_profile_status.has_value()) {
            tox->remote_profile_status =
                *request.value().desired_profile_status;
            ++tox->remote_profile_status_applications;
            protocol::ProfileStatusEvidence evidence;
            evidence.desired = tox->remote_profile_status;
            evidence.observed = tox->remote_profile_status;
            auto evidence_bytes =
                protocol::encode_profile_status_evidence(evidence);
            if (!evidence_bytes) {
                result.outcome = protocol::CommandOutcome::internal_error;
            } else {
                result.outcome = protocol::CommandOutcome::succeeded;
                result.body.assign(evidence_bytes.value().begin(),
                                   evidence_bytes.value().end());
                append_authority_audit(
                    *tox,
                    "mock-profile-status-set desired=" +
                        protocol::to_string(tox->remote_profile_status) +
                        " applications=" +
                        std::to_string(
                            tox->remote_profile_status_applications));
            }
        } else if (request.value().operation ==
                       protocol::CommandOperation::update_stage &&
                   request.value().expected_update_head.has_value() &&
                   (snapshot->negotiated.shared_features &
                    protocol::feature_bit(
                        protocol::Feature::signed_ota_v1)) != 0U) {
            protocol::UpdateStageEvidence evidence;
            evidence.release_sequence = 1U;
            evidence.accepted_head =
                *request.value().expected_update_head;
            evidence.manifest_record.fill(0x5aU);
            auto evidence_bytes =
                protocol::encode_update_stage_evidence(evidence);
            if (!evidence_bytes) {
                result.outcome = protocol::CommandOutcome::internal_error;
            } else {
                result.outcome = protocol::CommandOutcome::succeeded;
                result.body.assign(evidence_bytes.value().begin(),
                                   evidence_bytes.value().end());
                append_authority_audit(
                    *tox, "mock-update-stage head=" +
                              security::hex(evidence.accepted_head));
            }
        } else {
            result.outcome = protocol::CommandOutcome::unsupported;
        }
        auto result_payload = protocol::encode_command_result(result);
        if (!result_payload) {
            return outcome;
        }
        protocol::Frame reply;
        reply.major = snapshot->negotiated.selected.major;
        reply.minor = snapshot->negotiated.selected.minor;
        reply.type = protocol::MessageType::command_result;
        reply.message_id = next_mock_protocol_message_id();
        reply.correlation_id = incoming.message_id;
        reply.sequence = incoming.sequence;
        reply.expiry_unix_ms = 0U;
        reply.payload = std::move(result_payload).value();
        auto encoded = encode_frame_bytes(reply);
        if (encoded) {
            session.frozen_incoming_command_results.emplace(
                incoming.message_id, *encoded);
            outcome.replies.push_back(std::move(*encoded));
            append_authority_audit(
                *tox, "mock-device-describe-response-sent correlation=" +
                          std::to_string(incoming.message_id) + " outcome=" +
                          protocol::to_string(result.outcome));
        }
        return outcome;
    }

    if (incoming.type == protocol::MessageType::acknowledgement) {
        outcome.handled = true;
        auto receipt = protocol::decode_command_receipt(incoming.payload);
        if (!receipt || incoming.flags != 0U ||
            incoming.correlation_id == 0U ||
            incoming.expiry_unix_ms != 0U) {
            return outcome;
        }
        if (session.preauthority_describe_request &&
            incoming.correlation_id ==
                session.preauthority_describe_request->message_id &&
            incoming.sequence ==
                session.preauthority_describe_request->sequence) {
            session.preauthority_describe_received = true;
            append_authority_audit(
                *tox, "preauthority-device-describe-received stage=" +
                          protocol::to_string(receipt.value().stage));
            return outcome;
        }
        if (session.authorized_describe_request &&
            incoming.correlation_id ==
                session.authorized_describe_request->message_id &&
            incoming.sequence ==
                session.authorized_describe_request->sequence) {
            session.authorized_describe_received = true;
            append_authority_audit(
                *tox, "authorized-device-describe-received stage=" +
                          protocol::to_string(receipt.value().stage));
        }
        if (session.authorized_profile_status_request &&
            incoming.correlation_id ==
                session.authorized_profile_status_request->message_id &&
            incoming.sequence ==
                session.authorized_profile_status_request->sequence) {
            session.authorized_profile_status_received = true;
            append_authority_audit(
                *tox, "authorized-profile-status-received stage=" +
                          protocol::to_string(receipt.value().stage));
        }
        if (session.authorized_update_stage_request &&
            incoming.correlation_id ==
                session.authorized_update_stage_request->message_id &&
            incoming.sequence ==
                session.authorized_update_stage_request->sequence) {
            session.authorized_update_stage_received = true;
            append_authority_audit(
                *tox, "authorized-update-stage-received stage=" +
                          protocol::to_string(receipt.value().stage));
        }
        return outcome;
    }

    if (incoming.type == protocol::MessageType::command_result) {
        outcome.handled = true;
        auto result = protocol::decode_command_result(incoming.payload);
        if (!result || incoming.flags != 0U ||
            incoming.correlation_id == 0U ||
            incoming.expiry_unix_ms != 0U) {
            return outcome;
        }
        if (session.preauthority_describe_request &&
            incoming.correlation_id ==
                session.preauthority_describe_request->message_id &&
            incoming.sequence ==
                session.preauthority_describe_request->sequence) {
            if (result.value().operation ==
                    protocol::CommandOperation::device_describe &&
                result.value().outcome ==
                    protocol::CommandOutcome::denied &&
                result.value().body.empty()) {
                session.preauthority_describe_denied = true;
                append_authority_audit(
                    *tox, "preauthority-device-describe-denied");
            }
            return outcome;
        }
        if (session.authorized_update_stage_request &&
            incoming.correlation_id ==
                session.authorized_update_stage_request->message_id &&
            incoming.sequence ==
                session.authorized_update_stage_request->sequence) {
            auto requested = protocol::decode_command_request(
                session.authorized_update_stage_request->payload);
            auto evidence = protocol::decode_update_stage_evidence(
                result.value().body);
            if (!requested || !requested.value().expected_update_head ||
                result.value().operation !=
                    protocol::CommandOperation::update_stage ||
                result.value().outcome !=
                    protocol::CommandOutcome::succeeded ||
                !evidence || evidence.value().accepted_head !=
                    *requested.value().expected_update_head) {
                return outcome;
            }
            if (!session.authorized_update_stage_succeeded) {
                session.authorized_update_stage_succeeded = true;
                session.authorized_update_stage_result_packet.assign(
                    packet.begin(), packet.end());
                append_authority_audit(
                    *tox, "authorized-update-stage-succeeded sequence=" +
                              std::to_string(
                                  evidence.value().release_sequence));
                auto duplicate = encode_frame_bytes(
                    *session.authorized_update_stage_request);
                if (duplicate) {
                    session.authorized_update_stage_duplicate_sent = true;
                    outcome.replies.push_back(std::move(*duplicate));
                }
                return outcome;
            }
            if (session.authorized_update_stage_duplicate_sent &&
                !session.authorized_update_stage_duplicate_succeeded &&
                session.authorized_update_stage_result_packet.size() ==
                    packet.size() &&
                std::equal(
                    packet.begin(), packet.end(),
                    session.authorized_update_stage_result_packet.begin())) {
                session.authorized_update_stage_duplicate_succeeded = true;
                append_authority_audit(
                    *tox, "authorized-update-stage-duplicate-replayed-exact");
            }
            return outcome;
        }
        if (session.authorized_profile_status_request &&
            incoming.correlation_id ==
                session.authorized_profile_status_request->message_id &&
            incoming.sequence ==
                session.authorized_profile_status_request->sequence) {
            auto evidence = protocol::decode_profile_status_evidence(
                result.value().body);
            if (result.value().operation !=
                    protocol::CommandOperation::profile_status_set ||
                result.value().outcome !=
                    protocol::CommandOutcome::succeeded ||
                !evidence || evidence.value().desired !=
                    tox->profile_status_command_desired ||
                evidence.value().observed !=
                    tox->profile_status_command_desired) {
                return outcome;
            }
            if (!session.authorized_profile_status_succeeded) {
                session.authorized_profile_status_succeeded = true;
                session.authorized_profile_status_result_packet.assign(
                    packet.begin(), packet.end());
                append_authority_audit(
                    *tox,
                    "authorized-profile-status-succeeded desired=" +
                        protocol::to_string(
                            tox->profile_status_command_desired) +
                        " observed=" + protocol::to_string(
                            tox->profile_status_command_desired));
                if (!session.authorized_profile_status_duplicate_sent) {
                    auto duplicate = encode_frame_bytes(
                        *session.authorized_profile_status_request);
                    if (duplicate) {
                        session.authorized_profile_status_duplicate_sent = true;
                        outcome.replies.push_back(std::move(*duplicate));
                    }
                }
                return outcome;
            }
            if (session.authorized_profile_status_duplicate_sent &&
                !session.authorized_profile_status_duplicate_succeeded &&
                session.authorized_profile_status_result_packet.size() ==
                    packet.size() &&
                std::equal(
                    packet.begin(), packet.end(),
                    session.authorized_profile_status_result_packet.begin())) {
                session.authorized_profile_status_duplicate_succeeded = true;
                append_authority_audit(
                    *tox,
                    "authorized-profile-status-duplicate-replayed-exact");
            }
            return outcome;
        }
        if (!session.authorized_describe_request ||
            incoming.correlation_id !=
                session.authorized_describe_request->message_id ||
            incoming.sequence !=
                session.authorized_describe_request->sequence ||
            result.value().operation !=
                protocol::CommandOperation::device_describe ||
            result.value().outcome !=
                protocol::CommandOutcome::succeeded) {
            return outcome;
        }
        auto description =
            protocol::decode_device_description(result.value().body);
        if (!description ||
            description.value().device_principal !=
                session.agent_principal ||
            (description.value().offered_operations &
             protocol::kDeviceDescribeOperationBit) == 0U) {
            return outcome;
        }
        if (!session.authorized_describe_succeeded) {
            session.authorized_describe_succeeded = true;
            session.authorized_describe_result_packet.assign(
                packet.begin(), packet.end());
            append_authority_audit(
                *tox, "authorized-device-describe-succeeded principal=" +
                          security::hex(description.value().device_principal) +
                          " revision=" +
                          std::to_string(description.value().revision_number));
            if (!session.authorized_describe_duplicate_sent) {
                auto duplicate = encode_frame_bytes(
                    *session.authorized_describe_request);
                if (duplicate) {
                    session.authorized_describe_duplicate_sent = true;
                    outcome.replies.push_back(std::move(*duplicate));
                }
            }
            return outcome;
        }
        if (session.authorized_describe_duplicate_sent &&
            !session.authorized_describe_duplicate_succeeded &&
            session.authorized_describe_result_packet.size() == packet.size() &&
            std::equal(packet.begin(), packet.end(),
                       session.authorized_describe_result_packet.begin(),
                       session.authorized_describe_result_packet.end())) {
            session.authorized_describe_duplicate_succeeded = true;
            append_authority_audit(
                *tox,
                "authorized-device-describe-duplicate-replayed-exact");
        }
        return outcome;
    }

    return outcome;
}

}  // namespace

IOTOX_MOCK_EXPORT std::uint32_t tox_version_major() { return 0U; }
IOTOX_MOCK_EXPORT std::uint32_t tox_version_minor() { return 2U; }
IOTOX_MOCK_EXPORT std::uint32_t tox_version_patch() { return 23U; }
IOTOX_MOCK_EXPORT bool tox_version_is_compatible(
    std::uint32_t major, std::uint32_t minor, std::uint32_t patch) {
    return major == 0U && minor == 2U && patch <= 23U;
}
IOTOX_MOCK_EXPORT std::uint32_t tox_public_key_size() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kPublicKeySize);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_address_size() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kAddressSize);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_name_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxNameLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_status_message_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxStatusMessageLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_message_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxMessageLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_file_id_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kFileIdLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_filename_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxFilenameLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_friend_request_length() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxFriendRequestLength);
}
IOTOX_MOCK_EXPORT std::uint32_t tox_max_custom_packet_size() {
    return static_cast<std::uint32_t>(iotox::toxcore::abi::kMaxCustomPacketSize);
}

IOTOX_MOCK_EXPORT Tox_Options *tox_options_new(Tox_Err_Options_New *error) {
    set_error(error, TOX_ERR_OPTIONS_NEW_OK);
    return new Tox_Options{};
}

IOTOX_MOCK_EXPORT void tox_options_free(Tox_Options *options) { delete options; }

IOTOX_MOCK_EXPORT void tox_options_set_udp_enabled(Tox_Options *options, bool enabled) {
    if (options != nullptr) {
        options->udp_enabled = enabled;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_local_discovery_enabled(
    Tox_Options *options, bool enabled) {
    if (options != nullptr) {
        options->local_discovery_enabled = enabled;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_dht_announcements_enabled(
    Tox_Options *options, bool enabled) {
    if (options != nullptr) {
        options->dht_announcements_enabled = enabled;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_proxy_type(
    Tox_Options *options, Tox_Proxy_Type type) {
    if (options != nullptr) {
        options->proxy_type = type;
    }
}

IOTOX_MOCK_EXPORT bool tox_options_set_proxy_host(Tox_Options *options, const char *host) {
    if (options == nullptr || host == nullptr) {
        return false;
    }
    options->proxy_host = host;
    return true;
}

IOTOX_MOCK_EXPORT void tox_options_set_proxy_port(
    Tox_Options *options, std::uint16_t port) {
    if (options != nullptr) {
        options->proxy_port = port;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_hole_punching_enabled(
    Tox_Options *options, bool enabled) {
    if (options != nullptr) {
        options->hole_punching_enabled = enabled;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_experimental_disable_dns(
    Tox_Options *options, bool disabled) {
    if (options != nullptr) {
        options->experimental_disable_dns = disabled;
    }
}

IOTOX_MOCK_EXPORT void tox_options_set_savedata_type(
    Tox_Options *options, Tox_Savedata_Type type) {
    if (options != nullptr) {
        options->savedata_type = type;
    }
}

IOTOX_MOCK_EXPORT bool tox_options_set_savedata_data(
    Tox_Options *options, const std::uint8_t *data, std::size_t length) {
    if (options == nullptr || (data == nullptr && length != 0U)) {
        return false;
    }
    if (length == 0U) {
        options->savedata.clear();
    } else {
        options->savedata.assign(data, data + length);
    }
    return true;
}

IOTOX_MOCK_EXPORT Tox *tox_new(const Tox_Options *options, Tox_Err_New *error) {
    using namespace iotox::toxcore;
    set_error(error, TOX_ERR_NEW_OK);
    auto *tox = new Tox{};
    if (const std::string options_audit =
            environment_value("IOTOX_MOCK_OPTIONS_AUDIT");
        !options_audit.empty() && options != nullptr) {
        std::ofstream output(options_audit, std::ios::app);
        output << "udp=" << (options->udp_enabled ? 1 : 0)
               << " local-discovery="
               << (options->local_discovery_enabled ? 1 : 0)
               << " dht-announcements="
               << (options->dht_announcements_enabled ? 1 : 0)
               << " hole-punching="
               << (options->hole_punching_enabled ? 1 : 0)
               << " proxy=" << static_cast<int>(options->proxy_type)
               << " proxy-host=" << options->proxy_host
               << " proxy-port=" << options->proxy_port
               << " disable-dns="
               << (options->experimental_disable_dns ? 1 : 0) << '\n';
    }
    tox->send_delay = parse_mock_send_delay(environment_value("IOTOX_MOCK_SEND_DELAY_MS"));
    tox->start_friends_offline = parse_mock_count(
        environment_value("IOTOX_MOCK_START_FRIENDS_OFFLINE")) != 0U;
    tox->suppress_self_connection = parse_mock_count(
        environment_value("IOTOX_MOCK_SUPPRESS_SELF_CONNECTION")) != 0U;
    tox->require_inline_file_chunks = parse_mock_count(
        environment_value("IOTOX_MOCK_REQUIRE_INLINE_FILE_CHUNKS")) != 0U;
    tox->advertise_ratox_interactive = parse_mock_count(
        environment_value("IOTOX_MOCK_RATOX_INTERACTIVE")) != 0U;
    tox->emulate_ratox_host = parse_mock_count(
        environment_value("IOTOX_MOCK_RATOX_HOST")) != 0U;
    tox->emit_profile_status_command = parse_mock_count(
        environment_value("IOTOX_MOCK_PROFILE_STATUS_COMMAND")) != 0U;
    tox->update_stage_head_file =
        environment_value("IOTOX_MOCK_UPDATE_STAGE_HEAD_FILE");
    tox->stop_after_self_status_call = parse_mock_count(
        environment_value("IOTOX_MOCK_STOP_AFTER_SELF_STATUS_CALL")) != 0U;
    const std::string profile_status_desired =
        environment_value("IOTOX_MOCK_PROFILE_STATUS_DESIRED");
    if (profile_status_desired == "available") {
        tox->profile_status_command_desired =
            iotox::protocol::CommandRequest::ProfileStatus::available;
    } else if (profile_status_desired == "busy") {
        tox->profile_status_command_desired =
            iotox::protocol::CommandRequest::ProfileStatus::busy;
    }
    tox->text_not_connected_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_TEXT_NOT_CONNECTED_FAILURES"));
    tox->text_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_TEXT_SENDQ_FAILURES"));
    tox->text_disconnects_before_receipt = parse_mock_count(
        environment_value("IOTOX_MOCK_TEXT_DISCONNECTS_BEFORE_RECEIPT"));
    tox->lossless_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_LOSSLESS_SENDQ_FAILURES"));
    tox->hello_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_HELLO_SENDQ_FAILURES"));
    tox->confirmation_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_CONFIRMATION_SENDQ_FAILURES"));
    tox->hello_accepted_drops = parse_mock_count(
        environment_value("IOTOX_MOCK_HELLO_ACCEPTED_DROPS"));
    tox->confirmation_accepted_drops = parse_mock_count(
        environment_value("IOTOX_MOCK_CONFIRMATION_ACCEPTED_DROPS"));
    tox->authority_challenge_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_AUTHORITY_CHALLENGE_SENDQ_FAILURES"));
    tox->authority_proof_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_AUTHORITY_PROOF_SENDQ_FAILURES"));
    tox->command_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_COMMAND_SENDQ_FAILURES"));
    tox->command_result_sendq_failures_per_request = parse_mock_count(
        environment_value(
            "IOTOX_MOCK_COMMAND_RESULT_SENDQ_FAILURES_PER_REQUEST"));
    tox->ratox_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_RATOX_SENDQ_FAILURES"));
    tox->ratox_open_result_sendq_failures = parse_mock_count(
        environment_value("IOTOX_MOCK_RATOX_OPEN_RESULT_SENDQ_FAILURES"));
    tox->authority_audit_path = environment_value("IOTOX_MOCK_AUTHORITY_AUDIT");
    tox->capture_sent_file_path = environment_value("IOTOX_MOCK_CAPTURE_SENT_FILE");
    tox->incoming_friend_request = environment_value("IOTOX_MOCK_INCOMING_FRIEND_REQUEST");
    tox->incoming_file = environment_value("IOTOX_MOCK_INCOMING_FILE");
    const std::uint32_t incoming_file_count = parse_mock_count(
        environment_value("IOTOX_MOCK_INCOMING_FILE_COUNT"));
    tox->incoming_file_count = incoming_file_count == 0U
        ? 1U
        : incoming_file_count;
    tox->defer_incoming_file =
        environment_value("IOTOX_MOCK_DEFER_INCOMING_FILE") == "1";
    tox->file_pause_already_paused_remaining = parse_mock_count(
        environment_value("IOTOX_MOCK_FILE_PAUSE_ALREADY_PAUSED_COUNT"));
    tox->sync_namespace = environment_value("IOTOX_MOCK_SYNC_NAMESPACE");
    const std::uint32_t sync_disconnect_self_first_byte = parse_mock_count(
        environment_value(
            "IOTOX_MOCK_SYNC_DISCONNECT_SELF_FIRST_BYTE"));
    tox->sync_disconnect_self_first_byte =
        sync_disconnect_self_first_byte <= 0xffU &&
                !environment_value(
                    "IOTOX_MOCK_SYNC_DISCONNECT_SELF_FIRST_BYTE").empty()
            ? sync_disconnect_self_first_byte
            : 256U;
    tox->sync_disconnect_after_file_bytes = parse_mock_count(
        environment_value(
            "IOTOX_MOCK_SYNC_DISCONNECT_AFTER_FILE_BYTES"));
    const std::string sync_artifact_path =
        environment_value("IOTOX_MOCK_SYNC_ARTIFACT");
    const std::string sync_manifest_path =
        environment_value("IOTOX_MOCK_SYNC_MANIFEST");
    const std::string sync_parent_artifact_path =
        environment_value("IOTOX_MOCK_SYNC_PARENT_ARTIFACT");
    const std::string sync_parent_manifest_path =
        environment_value("IOTOX_MOCK_SYNC_PARENT_MANIFEST");
    const std::string sync_content_policy_path =
        environment_value("IOTOX_MOCK_SYNC_CONTENT_POLICY");

    auto sodium = iotox::security::Sodium::load();
    if (!sodium) {
        delete tox;
        set_error(error, TOX_ERR_NEW_MALLOC);
        return nullptr;
    }
    tox->sodium.emplace(std::move(sodium).value());
    auto authority_keys =
        tox->sodium->signing_keypair_from_seed(kMockAuthoritySeed);
    if (!authority_keys ||
        authority_keys.value().public_key() != kMockAuthorityPublicKey) {
        delete tox;
        set_error(error, TOX_ERR_NEW_MALLOC);
        return nullptr;
    }
    tox->authority_keys.emplace(std::move(authority_keys).value());
    auto device_identity = mock_device_identity(*tox->sodium);
    if (!device_identity ||
        device_identity.value().public_key() != kMockAuthorityPublicKey) {
        delete tox;
        set_error(error, TOX_ERR_NEW_MALLOC);
        return nullptr;
    }
    tox->device_identity.emplace(std::move(device_identity).value());

    if (!sync_content_policy_path.empty()) {
        auto encoded_policy = read_mock_file(sync_content_policy_path);
        auto policy = encoded_policy
                          ? iotox::sync::decode_namespace_policy(
                                *encoded_policy)
                          : iotox::Result<iotox::sync::NamespacePolicy>{
                                iotox::Status{
                                    iotox::ErrorCode::not_found,
                                    "mock content policy is absent"}};
        if (!policy || policy.value().engine !=
                           iotox::sync::Engine::content_v2 ||
            policy.value().id != tox->sync_namespace) {
            delete tox;
            set_error(error, TOX_ERR_NEW_MALLOC);
            return nullptr;
        }
        iotox::sync::SignedHeadStore heads(policy.value().root);
        auto head = heads.load(policy.value(), *tox->sodium);
        if (!head || !head.value().has_value()) {
            delete tox;
            set_error(error, TOX_ERR_NEW_MALLOC);
            return nullptr;
        }
        tox->sync_content_policy.emplace(std::move(policy).value());
        tox->sync_head.emplace(std::move(*head.value()));
    } else if (!tox->sync_namespace.empty() || !sync_artifact_path.empty() ||
        !sync_manifest_path.empty() ||
        !sync_parent_artifact_path.empty() ||
        !sync_parent_manifest_path.empty()) {
        auto artifact = read_mock_file(sync_artifact_path);
        auto manifest = read_mock_file(sync_manifest_path);
        auto artifact_digest =
            iotox::sync::hash_sync_file_sha256(sync_artifact_path);
        auto manifest_digest =
            iotox::sync::hash_sync_file_sha256(sync_manifest_path);
        iotox::sync::NamespacePolicy policy;
        policy.id = tox->sync_namespace;
        policy.root = "/tmp/iotox-mock-sync-fixture";
        policy.writers = {tox->device_identity->public_key()};
        iotox::sync::SignedHeadPublicationRequest publication;
        if (!artifact || !manifest || !artifact_digest ||
            !manifest_digest) {
            delete tox;
            set_error(error, TOX_ERR_NEW_MALLOC);
            return nullptr;
        }
        publication.artifact = artifact_digest.value();
        publication.manifest = manifest_digest.value();
        publication.artifact_bytes =
            static_cast<std::uint64_t>(artifact->size());
        publication.manifest_bytes =
            static_cast<std::uint64_t>(manifest->size());
        std::optional<iotox::sync::SignedHead> previous;
        if (!sync_parent_artifact_path.empty() ||
            !sync_parent_manifest_path.empty()) {
            auto parent_artifact = read_mock_file(
                sync_parent_artifact_path);
            auto parent_manifest = read_mock_file(
                sync_parent_manifest_path);
            auto parent_artifact_digest =
                iotox::sync::hash_sync_file_sha256(
                    sync_parent_artifact_path);
            auto parent_manifest_digest =
                iotox::sync::hash_sync_file_sha256(
                    sync_parent_manifest_path);
            if (!parent_artifact || !parent_manifest ||
                !parent_artifact_digest || !parent_manifest_digest) {
                delete tox;
                set_error(error, TOX_ERR_NEW_MALLOC);
                return nullptr;
            }
            iotox::sync::SignedHeadPublicationRequest parent_publication;
            parent_publication.artifact = parent_artifact_digest.value();
            parent_publication.manifest = parent_manifest_digest.value();
            parent_publication.artifact_bytes =
                static_cast<std::uint64_t>(parent_artifact->size());
            parent_publication.manifest_bytes =
                static_cast<std::uint64_t>(parent_manifest->size());
            auto parent = iotox::sync::create_signed_head(
                policy, parent_publication, std::nullopt,
                *tox->device_identity, *tox->sodium);
            if (!parent) {
                delete tox;
                set_error(error, TOX_ERR_NEW_MALLOC);
                return nullptr;
            }
            previous.emplace(std::move(parent).value());
        }
        auto head = iotox::sync::create_signed_head(
            policy, publication, previous, *tox->device_identity,
            *tox->sodium);
        if (!head) {
            delete tox;
            set_error(error, TOX_ERR_NEW_MALLOC);
            return nullptr;
        }
        tox->sync_artifact = std::move(*artifact);
        tox->sync_manifest = std::move(*manifest);
        tox->sync_head = std::move(head).value();
    }

    bool loaded = false;
    if (options != nullptr && options->savedata_type == TOX_SAVEDATA_TYPE_TOX_SAVE &&
        load_v3_savedata(tox, options->savedata)) {
        loaded = true;
    } else if (options != nullptr && options->savedata_type == TOX_SAVEDATA_TYPE_TOX_SAVE &&
        options->savedata.size() == kSavedataMagicV1.size() + abi::kAddressSize &&
        std::equal(kSavedataMagicV1.begin(), kSavedataMagicV1.end(),
                   options->savedata.begin())) {
        std::copy_n(
            options->savedata.begin() + static_cast<std::ptrdiff_t>(kSavedataMagicV1.size()),
            tox->address.size(), tox->address.begin());
        loaded = true;
    } else if (options != nullptr && options->savedata_type == TOX_SAVEDATA_TYPE_TOX_SAVE &&
               options->savedata.size() >=
                   kSavedataMagicV2.size() + abi::kAddressSize + sizeof(std::uint32_t) &&
               std::equal(kSavedataMagicV2.begin(), kSavedataMagicV2.end(),
                          options->savedata.begin())) {
        std::size_t offset = kSavedataMagicV2.size();
        std::copy_n(options->savedata.begin() + static_cast<std::ptrdiff_t>(offset),
                    tox->address.size(), tox->address.begin());
        offset += tox->address.size();
        const std::uint32_t slots = read_u32(options->savedata.data() + offset);
        offset += sizeof(std::uint32_t);
        const std::size_t expected = offset + static_cast<std::size_t>(slots) * kSavedFriendRecordSize;
        if (expected == options->savedata.size()) {
            tox->friends.resize(slots);
            for (std::uint32_t index = 0U; index < slots; ++index) {
                const bool present = options->savedata[offset] != 0U;
                ++offset;
                if (present) {
                    std::array<std::uint8_t, abi::kPublicKeySize> key{};
                    std::copy_n(options->savedata.begin() + static_cast<std::ptrdiff_t>(offset),
                                key.size(), key.begin());
                    tox->friends[index] = key;
                    if (!tox->start_friends_offline) {
                        tox->pending_friend_connections.push_back(index);
                    }
                }
                offset += abi::kPublicKeySize;
            }
            loaded = true;
        }
    }

    if (!loaded) {
        for (std::size_t index = 0U; index < tox->address.size(); ++index) {
            tox->address[index] = static_cast<std::uint8_t>((index * 7U + 3U) & 0xFFU);
        }
        const std::string address_tag_text =
            environment_value("IOTOX_MOCK_ADDRESS_TAG");
        const std::uint32_t address_tag = parse_mock_count(address_tag_text);
        if (!address_tag_text.empty() && address_tag > 0U &&
            address_tag <= 255U) {
            tox->address[0U] ^= static_cast<std::uint8_t>(address_tag);
        }
    }
    return tox;
}

IOTOX_MOCK_EXPORT void tox_kill(Tox *tox) { delete tox; }

IOTOX_MOCK_EXPORT bool tox_bootstrap(
    Tox *tox, const char *host, std::uint16_t port, const std::uint8_t *public_key,
    Tox_Err_Bootstrap *error) {
    if (tox == nullptr || host == nullptr || public_key == nullptr) {
        set_error(error, TOX_ERR_BOOTSTRAP_NULL);
        return false;
    }
    if (port == 0U) {
        set_error(error, TOX_ERR_BOOTSTRAP_BAD_PORT);
        return false;
    }
    set_error(error, TOX_ERR_BOOTSTRAP_OK);
    return true;
}

IOTOX_MOCK_EXPORT bool tox_add_tcp_relay(
    Tox *tox, const char *host, std::uint16_t port, const std::uint8_t *public_key,
    Tox_Err_Bootstrap *error) {
    return tox_bootstrap(tox, host, port, public_key, error);
}

IOTOX_MOCK_EXPORT std::size_t tox_get_savedata_size(const Tox *tox) {
    const std::size_t slots = tox == nullptr ? 0U : tox->friends.size();
    const std::size_t name_size = tox == nullptr ? 0U : tox->name.size();
    const std::size_t status_size = tox == nullptr ? 0U : tox->status_message.size();
    return kSavedataMagicV3.size() + iotox::toxcore::abi::kAddressSize +
           sizeof(std::uint32_t) + slots * kSavedFriendRecordSize +
           sizeof(std::uint32_t) + name_size + sizeof(std::uint32_t) +
           status_size + 1U;
}

IOTOX_MOCK_EXPORT void tox_get_savedata(const Tox *tox, std::uint8_t *savedata) {
    if (tox == nullptr || savedata == nullptr) {
        return;
    }
    std::size_t offset = 0U;
    std::copy(kSavedataMagicV3.begin(), kSavedataMagicV3.end(), savedata + offset);
    offset += kSavedataMagicV3.size();
    std::copy(tox->address.begin(), tox->address.end(), savedata + offset);
    offset += tox->address.size();
    write_u32(savedata + offset, static_cast<std::uint32_t>(tox->friends.size()));
    offset += sizeof(std::uint32_t);
    for (const auto &friend_key : tox->friends) {
        savedata[offset++] = friend_key ? 1U : 0U;
        if (friend_key) {
            std::copy(friend_key->begin(), friend_key->end(), savedata + offset);
        } else {
            std::fill_n(savedata + offset, iotox::toxcore::abi::kPublicKeySize, 0U);
        }
        offset += iotox::toxcore::abi::kPublicKeySize;
    }
    write_u32(savedata + offset, static_cast<std::uint32_t>(tox->name.size()));
    offset += sizeof(std::uint32_t);
    std::copy(tox->name.begin(), tox->name.end(), savedata + offset);
    offset += tox->name.size();
    write_u32(
        savedata + offset, static_cast<std::uint32_t>(tox->status_message.size()));
    offset += sizeof(std::uint32_t);
    std::copy(
        tox->status_message.begin(), tox->status_message.end(), savedata + offset);
    offset += tox->status_message.size();
    savedata[offset] = static_cast<std::uint8_t>(tox->user_status);
}

IOTOX_MOCK_EXPORT std::uint32_t tox_iteration_interval(const Tox *) {
    const std::uint32_t configured =
        parse_mock_count(environment_value("IOTOX_MOCK_ITERATION_INTERVAL_MS"));
    return configured == 0U ? 5U : configured;
}

IOTOX_MOCK_EXPORT void tox_iterate(Tox *tox, void *user_data) {
    if (tox == nullptr) {
        return;
    }

    if (!tox->emitted_self_connection && !tox->suppress_self_connection) {
        tox->emitted_self_connection = true;
        if (tox->self_connection_callback != nullptr) {
            tox->self_connection_callback(tox, TOX_CONNECTION_TCP, user_data);
        }
    }

    if (!tox->emitted_friend_request && tox->friend_request_callback != nullptr) {
        if (!tox->incoming_friend_request.empty()) {
            tox->emitted_friend_request = true;
            std::array<std::uint8_t, iotox::toxcore::abi::kPublicKeySize> key{};
            key.fill(0xA7U);
            const std::string &text = tox->incoming_friend_request;
            tox->friend_request_callback(
                tox, key.data(), reinterpret_cast<const std::uint8_t *>(text.data()),
                text.size(), user_data);
        }
    }

    if (!tox->emitted_file_offer && tox->file_recv_callback != nullptr &&
        valid_friend(tox, 0U)) {
        if (!tox->incoming_file.empty()) {
            tox->emitted_file_offer = true;
            for (std::uint32_t ordinal = 0U;
                 ordinal < tox->incoming_file_count; ++ordinal) {
                MockTransfer transfer;
                transfer.friend_number = 0U;
                const std::uint32_t slot = tox->next_incoming_file_slot++;
                transfer.file_number = (slot + 1U) << 16U;
                transfer.kind = iotox::toxcore::abi::kFileKindData;
                transfer.file_size = 4U;
                transfer.file_id.fill(
                    static_cast<std::uint8_t>(0xD4U + ordinal));
                const std::string &name = tox->incoming_file;
                transfer.filename.assign(name.begin(), name.end());
                transfer.receiving = true;
                transfer.local_paused = true;
                transfer.incoming_data = {'D', 'A', 'T', 'A'};
                tox->transfers.push_back(transfer);
                tox->file_recv_callback(
                    tox, transfer.friend_number, transfer.file_number,
                    transfer.kind, transfer.file_size,
                    transfer.filename.data(), transfer.filename.size(),
                    user_data);
            }
        }
    }

    while (!tox->pending_friend_connections.empty()) {
        const FriendNumber friend_number = tox->pending_friend_connections.front();
        tox->pending_friend_connections.pop_front();
        if (tox->friend_connection_callback != nullptr && valid_friend(tox, friend_number)) {
            tox->friend_connection_callback(tox, friend_number, TOX_CONNECTION_TCP, user_data);
        }
        if (valid_friend(tox, friend_number)) {
            const std::vector<std::uint8_t> name = mock_friend_name(friend_number);
            const std::vector<std::uint8_t> status_message =
                mock_friend_status_message(friend_number);
            if (tox->friend_name_callback != nullptr) {
                tox->friend_name_callback(
                    tox, friend_number, name.data(), name.size(), user_data);
            }
            if (tox->friend_status_message_callback != nullptr) {
                tox->friend_status_message_callback(
                    tox, friend_number, status_message.data(), status_message.size(),
                    user_data);
            }
            if (tox->friend_status_callback != nullptr) {
                tox->friend_status_callback(
                    tox, friend_number, mock_friend_status(friend_number), user_data);
            }
            if (tox->friend_typing_callback != nullptr) {
                tox->friend_typing_callback(tox, friend_number, false, user_data);
            }
        }
    }

    if (!tox->update_stage_head_file.empty() &&
        tox->friend_lossless_packet_callback != nullptr) {
        for (auto &[friend_number, session] : tox->iotox_sessions) {
            if (session.authorized_update_stage_request.has_value() ||
                !session.agent_authority_proof_verified ||
                !session.protocol_registry) {
                continue;
            }
            auto snapshot = session.protocol_registry->get(friend_number);
            if (!snapshot ||
                (snapshot.value().negotiated.shared_features &
                 iotox::protocol::feature_bit(
                     iotox::protocol::Feature::signed_ota_v1)) == 0U) {
                continue;
            }
            std::ifstream input(tox->update_stage_head_file);
            std::string encoded_head;
            if (!input || !std::getline(input, encoded_head)) continue;
            auto decoded = iotox::security::decode_hex_exact(
                encoded_head, iotox::protocol::kUpdateHeadRecordBytes,
                "mock update HEAD");
            if (!decoded) continue;
            iotox::protocol::UpdateHeadRecord head{};
            std::copy(decoded.value().begin(), decoded.value().end(),
                      head.begin());
            session.authorized_update_stage_request =
                make_mock_update_stage_request(snapshot.value(), head);
            if (!session.authorized_update_stage_request) continue;
            auto packet = encode_frame_bytes(
                *session.authorized_update_stage_request);
            if (!packet) continue;
            tox->friend_lossless_packet_callback(
                tox, friend_number, packet->data(), packet->size(),
                user_data);
            append_authority_audit(
                *tox, "authorized-update-stage-sent head=" +
                          iotox::security::hex(head));
        }
    }

    while (!tox->pending_incoming_file_offers.empty()) {
        const PendingIncomingFileOffer pending =
            tox->pending_incoming_file_offers.front();
        tox->pending_incoming_file_offers.pop_front();
        MockTransfer *transfer = find_transfer(
            tox, pending.friend_number, pending.file_number);
        if (transfer == nullptr || transfer->finished ||
            tox->file_recv_callback == nullptr ||
            !valid_friend(tox, pending.friend_number)) {
            continue;
        }
        tox->file_recv_callback(
            tox, transfer->friend_number, transfer->file_number,
            transfer->kind, transfer->file_size,
            transfer->filename.empty() ? nullptr :
                transfer->filename.data(),
            transfer->filename.size(), user_data);
    }

    while (!tox->pending_packets.empty()) {
        PendingPacket packet = std::move(tox->pending_packets.front());
        tox->pending_packets.pop_front();
        if (tox->friend_lossless_packet_callback != nullptr &&
            valid_friend(tox, packet.friend_number)) {
            tox->friend_lossless_packet_callback(
                tox, packet.friend_number, packet.data.data(), packet.data.size(), user_data);
        }
    }

    if (tox->pending_sync_disconnect) {
        const FriendNumber friend_number = *tox->pending_sync_disconnect;
        tox->pending_sync_disconnect.reset();
        if (tox->friend_connection_callback != nullptr &&
            valid_friend(tox, friend_number)) {
            tox->friend_connection_callback(
                tox, friend_number, TOX_CONNECTION_NONE, user_data);
        }
    }

    while (!tox->pending_lossy_packets.empty()) {
        PendingPacket packet = std::move(tox->pending_lossy_packets.front());
        tox->pending_lossy_packets.pop_front();
        if (tox->friend_lossy_packet_callback != nullptr &&
            valid_friend(tox, packet.friend_number)) {
            tox->friend_lossy_packet_callback(
                tox, packet.friend_number, packet.data.data(),
                packet.data.size(), user_data);
        }
    }

    while (!tox->pending_messages.empty()) {
        PendingMessage pending = std::move(tox->pending_messages.front());
        tox->pending_messages.pop_front();
        if (tox->friend_message_callback != nullptr &&
            valid_friend(tox, pending.friend_number)) {
            tox->friend_message_callback(
                tox, pending.friend_number, pending.type, pending.data.data(),
                pending.data.size(), user_data);
        }
    }

    if (tox->text_disconnects_before_receipt != 0U &&
        !tox->pending_receipts.empty()) {
        --tox->text_disconnects_before_receipt;
        const FriendNumber friend_number = tox->pending_receipts.front().first;
        std::erase_if(
            tox->pending_receipts,
            [friend_number](const auto &receipt) {
                return receipt.first == friend_number;
            });
        if (tox->friend_connection_callback != nullptr &&
            valid_friend(tox, friend_number)) {
            tox->friend_connection_callback(
                tox, friend_number, TOX_CONNECTION_NONE, user_data);
        }
    }

    while (!tox->pending_typing.empty()) {
        const PendingTyping pending = tox->pending_typing.front();
        tox->pending_typing.pop_front();
        if (tox->friend_typing_callback != nullptr &&
            valid_friend(tox, pending.friend_number)) {
            tox->friend_typing_callback(
                tox, pending.friend_number, pending.typing, user_data);
        }
    }

    while (!tox->pending_receipts.empty()) {
        const auto [friend_number, message_id] = tox->pending_receipts.front();
        tox->pending_receipts.pop_front();
        if (tox->friend_read_receipt_callback != nullptr &&
            valid_friend(tox, friend_number)) {
            tox->friend_read_receipt_callback(
                tox, friend_number, message_id, user_data);
        }
    }


    std::size_t chunk_requests_to_deliver = tox->pending_file_chunk_requests.size();
    while (chunk_requests_to_deliver-- != 0U &&
           !tox->pending_file_chunk_requests.empty()) {
        const PendingFileChunkRequest pending =
            tox->pending_file_chunk_requests.front();
        tox->pending_file_chunk_requests.pop_front();
        MockTransfer *transfer =
            find_transfer(tox, pending.friend_number, pending.file_number);
        if (transfer != nullptr &&
            (transfer->local_paused || transfer->peer_paused)) {
            // c-toxcore does not issue chunk requests while either side has
            // paused an active transfer. Preserve an already queued mock
            // request until both pause conditions clear.
            tox->pending_file_chunk_requests.push_back(pending);
            continue;
        }
        if (pending.length == 0U && transfer != nullptr &&
            transfer->file_size == 0U && !transfer->file_id_read) {
            // The real core cannot complete a zero-byte transfer before the
            // remote peer acknowledges it. Deferring until IoTox has queried
            // the stable file id prevents this deterministic mock from
            // creating an impossible same-turn completion race.
            tox->pending_file_chunk_requests.push_back(pending);
            continue;
        }
        if (pending.length == 0U && transfer != nullptr &&
            transfer->file_size == 0U && !transfer->finished) {
            capture_sent_file(*transfer, tox->capture_sent_file_path);
            transfer->finished = true;
        }
        if (tox->file_chunk_request_callback != nullptr) {
            const bool previously_inside =
                tox->inside_file_chunk_request_callback;
            tox->inside_file_chunk_request_callback = true;
            tox->file_chunk_request_callback(
                tox, pending.friend_number, pending.file_number,
                pending.position, pending.length, user_data);
            tox->inside_file_chunk_request_callback = previously_inside;
        }
    }

    while (!tox->pending_file_chunks.empty()) {
        PendingFileChunk pending = std::move(tox->pending_file_chunks.front());
        tox->pending_file_chunks.pop_front();
        if (tox->file_recv_chunk_callback != nullptr) {
            const std::uint8_t *data =
                pending.data.empty() ? nullptr : pending.data.data();
            tox->file_recv_chunk_callback(
                tox, pending.friend_number, pending.file_number,
                pending.position, data, pending.data.size(), user_data);
        }
        if (tox->pending_sync_disconnect_after_file_chunk &&
            *tox->pending_sync_disconnect_after_file_chunk ==
                pending.friend_number) {
            tox->pending_sync_disconnect_after_file_chunk.reset();
            if (tox->friend_connection_callback != nullptr &&
                valid_friend(tox, pending.friend_number)) {
                tox->friend_connection_callback(
                    tox, pending.friend_number, TOX_CONNECTION_NONE,
                    user_data);
            }
            break;
        }
    }
}

IOTOX_MOCK_EXPORT void tox_self_get_address(const Tox *tox, std::uint8_t *address) {
    if (tox != nullptr && address != nullptr) {
        std::copy(tox->address.begin(), tox->address.end(), address);
    }
}

IOTOX_MOCK_EXPORT bool tox_self_set_name(
    Tox *tox, const std::uint8_t *name, std::size_t length,
    Tox_Err_Set_Info *error) {
    if (tox == nullptr || (name == nullptr && length != 0U)) {
        set_error(error, TOX_ERR_SET_INFO_NULL);
        return false;
    }
    if (length > iotox::toxcore::abi::kMaxNameLength) {
        set_error(error, TOX_ERR_SET_INFO_TOO_LONG);
        return false;
    }
    if (length == 0U) {
        tox->name.clear();
    } else {
        tox->name.assign(name, name + length);
    }
    set_error(error, TOX_ERR_SET_INFO_OK);
    return true;
}

IOTOX_MOCK_EXPORT std::size_t tox_self_get_name_size(const Tox *tox) {
    return tox == nullptr ? 0U : tox->name.size();
}

IOTOX_MOCK_EXPORT void tox_self_get_name(const Tox *tox, std::uint8_t *name) {
    if (tox != nullptr && name != nullptr) {
        std::copy(tox->name.begin(), tox->name.end(), name);
    }
}

IOTOX_MOCK_EXPORT bool tox_self_set_status_message(
    Tox *tox, const std::uint8_t *status_message, std::size_t length,
    Tox_Err_Set_Info *error) {
    if (tox == nullptr || (status_message == nullptr && length != 0U)) {
        set_error(error, TOX_ERR_SET_INFO_NULL);
        return false;
    }
    if (length > iotox::toxcore::abi::kMaxStatusMessageLength) {
        set_error(error, TOX_ERR_SET_INFO_TOO_LONG);
        return false;
    }
    if (length == 0U) {
        tox->status_message.clear();
    } else {
        tox->status_message.assign(status_message, status_message + length);
    }
    set_error(error, TOX_ERR_SET_INFO_OK);
    return true;
}

IOTOX_MOCK_EXPORT std::size_t tox_self_get_status_message_size(const Tox *tox) {
    return tox == nullptr ? 0U : tox->status_message.size();
}

IOTOX_MOCK_EXPORT void tox_self_get_status_message(
    const Tox *tox, std::uint8_t *status_message) {
    if (tox != nullptr && status_message != nullptr) {
        std::copy(
            tox->status_message.begin(), tox->status_message.end(), status_message);
    }
}

IOTOX_MOCK_EXPORT void tox_self_set_status(Tox *tox, Tox_User_Status status) {
    if (tox != nullptr) {
        tox->user_status = status;
        ++tox->self_status_set_calls;
        append_authority_audit(
            *tox, "self-status-set value=" +
                      std::to_string(static_cast<unsigned>(status)) +
                      " calls=" +
                      std::to_string(tox->self_status_set_calls));
        if (tox->stop_after_self_status_call &&
            !tox->stopped_after_self_status_call) {
            tox->stopped_after_self_status_call = true;
            append_authority_audit(
                *tox,
                "self-status-provider-effect-complete-before-savedata");
            static_cast<void>(::raise(SIGSTOP));
        }
    }
}

IOTOX_MOCK_EXPORT Tox_User_Status tox_self_get_status(const Tox *tox) {
    return tox == nullptr ? TOX_USER_STATUS_NONE : tox->user_status;
}

IOTOX_MOCK_EXPORT bool tox_self_set_typing(
    Tox *tox, Tox_Friend_Number friend_number, bool typing,
    Tox_Err_Set_Typing *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_SET_TYPING_FRIEND_NOT_FOUND);
        return false;
    }
    tox->pending_typing.push_back({friend_number, typing});
    set_error(error, TOX_ERR_SET_TYPING_OK);
    return true;
}

IOTOX_MOCK_EXPORT void tox_callback_self_connection_status(
    Tox *tox, SelfConnectionCallback *callback) {
    if (tox != nullptr) {
        tox->self_connection_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_connection_status(
    Tox *tox, FriendConnectionCallback *callback) {
    if (tox != nullptr) {
        tox->friend_connection_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_name(
    Tox *tox, FriendNameCallback *callback) {
    if (tox != nullptr) {
        tox->friend_name_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_status_message(
    Tox *tox, FriendStatusMessageCallback *callback) {
    if (tox != nullptr) {
        tox->friend_status_message_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_status(
    Tox *tox, FriendStatusCallback *callback) {
    if (tox != nullptr) {
        tox->friend_status_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_typing(
    Tox *tox, FriendTypingCallback *callback) {
    if (tox != nullptr) {
        tox->friend_typing_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_request(
    Tox *tox, FriendRequestCallback *callback) {
    if (tox != nullptr) {
        tox->friend_request_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_message(
    Tox *tox, FriendMessageCallback *callback) {
    if (tox != nullptr) {
        tox->friend_message_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_read_receipt(
    Tox *tox, FriendReadReceiptCallback *callback) {
    if (tox != nullptr) {
        tox->friend_read_receipt_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_lossless_packet(
    Tox *tox, FriendLosslessPacketCallback *callback) {
    if (tox != nullptr) {
        tox->friend_lossless_packet_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_friend_lossy_packet(
    Tox *tox, FriendLossyPacketCallback *callback) {
    if (tox != nullptr) {
        tox->friend_lossy_packet_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_file_recv_control(
    Tox *tox, FileRecvControlCallback *callback) {
    if (tox != nullptr) {
        tox->file_recv_control_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_file_chunk_request(
    Tox *tox, FileChunkRequestCallback *callback) {
    if (tox != nullptr) {
        tox->file_chunk_request_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_file_recv(
    Tox *tox, FileRecvCallback *callback) {
    if (tox != nullptr) {
        tox->file_recv_callback = callback;
    }
}

IOTOX_MOCK_EXPORT void tox_callback_file_recv_chunk(
    Tox *tox, FileRecvChunkCallback *callback) {
    if (tox != nullptr) {
        tox->file_recv_chunk_callback = callback;
    }
}

IOTOX_MOCK_EXPORT Tox_Friend_Number tox_friend_add(
    Tox *tox, const std::uint8_t *address, const std::uint8_t *message,
    std::size_t length, Tox_Err_Friend_Add *error) {
    if (address == nullptr || message == nullptr) {
        set_error(error, TOX_ERR_FRIEND_ADD_NULL);
        return iotox::toxcore::abi::kFriendNumberFailure;
    }
    if (length == 0U) {
        set_error(error, TOX_ERR_FRIEND_ADD_NO_MESSAGE);
        return iotox::toxcore::abi::kFriendNumberFailure;
    }
    if (length > iotox::toxcore::abi::kMaxFriendRequestLength) {
        set_error(error, TOX_ERR_FRIEND_ADD_TOO_LONG);
        return iotox::toxcore::abi::kFriendNumberFailure;
    }
    return add_friend_record(tox, address, error);
}

IOTOX_MOCK_EXPORT Tox_Friend_Number tox_friend_add_norequest(
    Tox *tox, const std::uint8_t *public_key, Tox_Err_Friend_Add *error) {
    return add_friend_record(tox, public_key, error);
}

IOTOX_MOCK_EXPORT bool tox_friend_delete(
    Tox *tox, Tox_Friend_Number friend_number, Tox_Err_Friend_Delete *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_DELETE_FRIEND_NOT_FOUND);
        return false;
    }
    tox->friends[friend_number].reset();
    tox->iotox_sessions.erase(friend_number);
    std::erase(tox->pending_friend_connections, friend_number);
    std::erase_if(
        tox->pending_packets,
        [friend_number](const PendingPacket &packet) {
            return packet.friend_number == friend_number;
        });
    std::erase_if(
        tox->pending_lossy_packets,
        [friend_number](const PendingPacket &packet) {
            return packet.friend_number == friend_number;
        });
    std::erase_if(
        tox->pending_messages,
        [friend_number](const PendingMessage &message) {
            return message.friend_number == friend_number;
        });
    std::erase_if(
        tox->pending_receipts,
        [friend_number](const auto &receipt) {
            return receipt.first == friend_number;
        });
    std::erase_if(
        tox->pending_typing,
        [friend_number](const PendingTyping &typing) {
            return typing.friend_number == friend_number;
        });
    std::erase_if(
        tox->transfers,
        [friend_number](const MockTransfer &transfer) {
            return transfer.friend_number == friend_number;
        });
    std::erase_if(
        tox->pending_file_chunk_requests,
        [friend_number](const PendingFileChunkRequest &request) {
            return request.friend_number == friend_number;
        });
    std::erase_if(
        tox->pending_file_chunks,
        [friend_number](const PendingFileChunk &chunk) {
            return chunk.friend_number == friend_number;
        });
    tox->failed_ratox_packet.clear();
    tox->failed_ratox_open_result.clear();
    tox->command_result_sendq_remaining.clear();
    tox->frozen_command_results.clear();
    set_error(error, TOX_ERR_FRIEND_DELETE_OK);
    return true;
}

IOTOX_MOCK_EXPORT Tox_Friend_Number tox_friend_by_public_key(
    const Tox *tox, const std::uint8_t *public_key,
    Tox_Err_Friend_By_Public_Key *error) {
    if (tox == nullptr || public_key == nullptr) {
        set_error(error, TOX_ERR_FRIEND_BY_PUBLIC_KEY_NULL);
        return iotox::toxcore::abi::kFriendNumberFailure;
    }
    for (std::size_t index = 0U; index < tox->friends.size(); ++index) {
        if (tox->friends[index] &&
            std::equal(public_key,
                       public_key + iotox::toxcore::abi::kPublicKeySize,
                       tox->friends[index]->begin())) {
            set_error(error, TOX_ERR_FRIEND_BY_PUBLIC_KEY_OK);
            return static_cast<Tox_Friend_Number>(index);
        }
    }
    set_error(error, TOX_ERR_FRIEND_BY_PUBLIC_KEY_NOT_FOUND);
    return iotox::toxcore::abi::kFriendNumberFailure;
}

IOTOX_MOCK_EXPORT std::size_t tox_self_get_friend_list_size(const Tox *tox) {
    if (tox == nullptr) {
        return 0U;
    }
    return static_cast<std::size_t>(std::count_if(
        tox->friends.begin(), tox->friends.end(), [](const auto &entry) { return entry.has_value(); }));
}

IOTOX_MOCK_EXPORT void tox_self_get_friend_list(
    const Tox *tox, Tox_Friend_Number *friend_list) {
    if (tox == nullptr || friend_list == nullptr) {
        return;
    }
    std::size_t output = 0U;
    for (std::size_t index = 0U; index < tox->friends.size(); ++index) {
        if (tox->friends[index]) {
            friend_list[output++] = static_cast<Tox_Friend_Number>(index);
        }
    }
}

IOTOX_MOCK_EXPORT bool tox_friend_get_public_key(
    const Tox *tox, Tox_Friend_Number friend_number, std::uint8_t *public_key,
    Tox_Err_Friend_Get_Public_Key *error) {
    if (!valid_friend(tox, friend_number) || public_key == nullptr) {
        set_error(error, TOX_ERR_FRIEND_GET_PUBLIC_KEY_FRIEND_NOT_FOUND);
        return false;
    }
    std::copy(tox->friends[friend_number]->begin(), tox->friends[friend_number]->end(),
              public_key);
    set_error(error, TOX_ERR_FRIEND_GET_PUBLIC_KEY_OK);
    return true;
}

IOTOX_MOCK_EXPORT std::size_t tox_friend_get_name_size(
    const Tox *tox, Tox_Friend_Number friend_number,
    Tox_Err_Friend_Query *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND);
        return 0U;
    }
    set_error(error, TOX_ERR_FRIEND_QUERY_OK);
    return mock_friend_name(friend_number).size();
}

IOTOX_MOCK_EXPORT bool tox_friend_get_name(
    const Tox *tox, Tox_Friend_Number friend_number, std::uint8_t *name,
    Tox_Err_Friend_Query *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND);
        return false;
    }
    const std::vector<std::uint8_t> value = mock_friend_name(friend_number);
    if (name == nullptr && !value.empty()) {
        set_error(error, TOX_ERR_FRIEND_QUERY_NULL);
        return false;
    }
    std::copy(value.begin(), value.end(), name);
    set_error(error, TOX_ERR_FRIEND_QUERY_OK);
    return true;
}

IOTOX_MOCK_EXPORT std::size_t tox_friend_get_status_message_size(
    const Tox *tox, Tox_Friend_Number friend_number,
    Tox_Err_Friend_Query *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND);
        return 0U;
    }
    set_error(error, TOX_ERR_FRIEND_QUERY_OK);
    return mock_friend_status_message(friend_number).size();
}

IOTOX_MOCK_EXPORT bool tox_friend_get_status_message(
    const Tox *tox, Tox_Friend_Number friend_number,
    std::uint8_t *status_message, Tox_Err_Friend_Query *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND);
        return false;
    }
    const std::vector<std::uint8_t> value =
        mock_friend_status_message(friend_number);
    if (status_message == nullptr && !value.empty()) {
        set_error(error, TOX_ERR_FRIEND_QUERY_NULL);
        return false;
    }
    std::copy(value.begin(), value.end(), status_message);
    set_error(error, TOX_ERR_FRIEND_QUERY_OK);
    return true;
}

IOTOX_MOCK_EXPORT Tox_Friend_Message_Id tox_friend_send_message(
    Tox *tox, Tox_Friend_Number friend_number, Tox_Message_Type type,
    const std::uint8_t *message, std::size_t length,
    Tox_Err_Friend_Send_Message *error) {
    if (tox == nullptr || (message == nullptr && length != 0U)) {
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_NULL);
        return 0U;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_FOUND);
        return 0U;
    }
    if (length == 0U) {
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_EMPTY);
        return 0U;
    }
    if (length > iotox::toxcore::abi::kMaxMessageLength) {
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_TOO_LONG);
        return 0U;
    }
    if (tox->text_not_connected_failures != 0U) {
        --tox->text_not_connected_failures;
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_CONNECTED);
        return 0U;
    }
    if (tox->text_sendq_failures != 0U) {
        --tox->text_sendq_failures;
        set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_SENDQ);
        return 0U;
    }
    const FriendMessageId message_id = tox->next_message_id++;
    PendingMessage pending;
    pending.friend_number = friend_number;
    pending.type = type;
    pending.message_id = message_id;
    pending.data.assign(message, message + length);
    tox->pending_messages.push_back(std::move(pending));
    tox->pending_receipts.emplace_back(friend_number, message_id);
    set_error(error, TOX_ERR_FRIEND_SEND_MESSAGE_OK);
    return message_id;
}

IOTOX_MOCK_EXPORT bool tox_friend_send_lossy_packet(
    Tox *tox, Tox_Friend_Number friend_number, const std::uint8_t *data,
    std::size_t length, Tox_Err_Friend_Custom_Packet *error) {
    if (tox == nullptr || data == nullptr || length == 0U) {
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_NULL);
        return false;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_FOUND);
        return false;
    }
    if (length > iotox::toxcore::abi::kMaxCustomPacketSize ||
        data[0] < 192U || data[0] > 254U) {
        set_error(
            error, length > iotox::toxcore::abi::kMaxCustomPacketSize
                       ? TOX_ERR_FRIEND_CUSTOM_PACKET_TOO_LONG
                       : TOX_ERR_FRIEND_CUSTOM_PACKET_INVALID);
        return false;
    }
    if (length >= iotox::interactive::kProbePacketSize &&
        length <= iotox::interactive::kMaximumResearchProbePacketSize &&
        data[0] == iotox::interactive::kLossyProbePacketId &&
        data[1] == static_cast<std::uint8_t>(
            iotox::interactive::ProbeKind::request)) {
        if (!tox->probe_sendq_failures_initialized) {
            const std::string configured =
                environment_value("IOTOX_MOCK_PROBE_SENDQ_FAILURES");
            if (!configured.empty()) {
                tox->probe_sendq_failures = parse_mock_count(configured);
                tox->probe_sendq_failures_initialized = true;
            }
        }
        if (tox->probe_sendq_failures != 0U) {
            --tox->probe_sendq_failures;
            set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
            return false;
        }
    }
    PendingPacket pending;
    pending.friend_number = friend_number;
    pending.data.assign(data, data + length);
    tox->pending_lossy_packets.push_back(std::move(pending));
    set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_OK);
    return true;
}

IOTOX_MOCK_EXPORT bool tox_friend_send_lossless_packet(
    Tox *tox, Tox_Friend_Number friend_number, const std::uint8_t *data,
    std::size_t length, Tox_Err_Friend_Custom_Packet *error) {
    if (tox == nullptr || data == nullptr || length == 0U) {
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_NULL);
        return false;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_FOUND);
        return false;
    }
    if (tox->send_delay > std::chrono::milliseconds::zero()) {
        std::this_thread::sleep_for(tox->send_delay);
    }
    const std::span<const std::uint8_t> outgoing{data, length};
    std::optional<iotox::protocol::ratox::FrameType> outgoing_ratox_type;
    if (outgoing.front() == iotox::protocol::ratox::kPacketId) {
        auto decoded_ratox = iotox::protocol::ratox::decode(outgoing);
        if (decoded_ratox) {
            outgoing_ratox_type = decoded_ratox.value().type;
        }
    }
    if (outgoing_ratox_type &&
        exact_retry_sendq(
            tox->ratox_sendq_failures,
            tox->failed_ratox_packet,
            outgoing, error)) {
        append_authority_audit(
            *tox, "ratox-sendq type=" +
                      std::string(iotox::protocol::ratox::to_string(
                          *outgoing_ratox_type)) +
                      " size=" + std::to_string(length));
        return false;
    }
    if (outgoing_ratox_type ==
            iotox::protocol::ratox::FrameType::open_result &&
        exact_retry_sendq(
            tox->ratox_open_result_sendq_failures,
            tox->failed_ratox_open_result,
            outgoing, error)) {
        append_authority_audit(
            *tox, "ratox-open-result-sendq size=" +
                      std::to_string(length));
        return false;
    }
    auto outgoing_frame = iotox::protocol::decode(outgoing);
    if (outgoing_frame &&
        outgoing_frame.value().type == iotox::protocol::MessageType::hello &&
        tox->hello_sendq_failures != 0U) {
        --tox->hello_sendq_failures;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
        return false;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type == iotox::protocol::MessageType::capabilities &&
        tox->confirmation_sendq_failures != 0U) {
        --tox->confirmation_sendq_failures;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
        return false;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type ==
            iotox::protocol::MessageType::authority_challenge &&
        exact_retry_sendq(
            tox->authority_challenge_sendq_failures,
            tox->failed_authority_challenge, outgoing, error)) {
        return false;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type ==
            iotox::protocol::MessageType::authority_proof &&
        exact_retry_sendq(
            tox->authority_proof_sendq_failures,
            tox->failed_authority_proof, outgoing, error)) {
        return false;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type ==
            iotox::protocol::MessageType::command &&
        exact_retry_sendq(
            tox->command_sendq_failures,
            tox->failed_command, outgoing, error)) {
        return false;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type ==
            iotox::protocol::MessageType::command_result &&
        tox->command_result_sendq_failures_per_request != 0U) {
        const std::uint64_t correlation =
            outgoing_frame.value().correlation_id;
        auto [remaining, inserted] =
            tox->command_result_sendq_remaining.try_emplace(
                correlation,
                tox->command_result_sendq_failures_per_request);
        auto [frozen, frozen_inserted] =
            tox->frozen_command_results.try_emplace(
                correlation, outgoing.begin(), outgoing.end());
        static_cast<void>(inserted);
        static_cast<void>(frozen_inserted);
        if (frozen->second.size() != outgoing.size() ||
            !std::equal(outgoing.begin(), outgoing.end(),
                        frozen->second.begin(), frozen->second.end())) {
            set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_INVALID);
            return false;
        }
        if (remaining->second != 0U) {
            --remaining->second;
            append_authority_audit(
                *tox,
                "command-result-sendq correlation=" +
                    std::to_string(correlation));
            set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
            return false;
        }
    }
    if (tox->lossless_sendq_failures != 0U) {
        --tox->lossless_sendq_failures;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
        return false;
    }
    // Model a packet that toxcore accepted locally just before the far side
    // admitted its new application epoch. There is deliberately no SENDQ
    // signal for the caller to use; only exact-record handshake retry can
    // recover this edge.
    if (outgoing_frame &&
        outgoing_frame.value().type == iotox::protocol::MessageType::hello &&
        tox->hello_accepted_drops != 0U) {
        --tox->hello_accepted_drops;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_OK);
        return true;
    }
    if (outgoing_frame &&
        outgoing_frame.value().type ==
            iotox::protocol::MessageType::capabilities &&
        tox->confirmation_accepted_drops != 0U) {
        --tox->confirmation_accepted_drops;
        set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_OK);
        return true;
    }
    if (length >= iotox::interactive::kProbePacketSize &&
        length <= iotox::interactive::kMaximumResearchProbePacketSize &&
        data[0] == iotox::interactive::kLosslessProbePacketId &&
        data[1] == static_cast<std::uint8_t>(
            iotox::interactive::ProbeKind::request)) {
        if (!tox->probe_sendq_failures_initialized) {
            const std::string configured =
                environment_value("IOTOX_MOCK_PROBE_SENDQ_FAILURES");
            if (!configured.empty()) {
                tox->probe_sendq_failures = parse_mock_count(configured);
                tox->probe_sendq_failures_initialized = true;
            }
        }
        if (tox->probe_sendq_failures != 0U) {
            --tox->probe_sendq_failures;
            set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ);
            return false;
        }
    }
    set_error(error, TOX_ERR_FRIEND_CUSTOM_PACKET_OK);
    MockPeerOutcome peer = outgoing_ratox_type && tox->emulate_ratox_host
        ? mock_ratox_peer_packet(tox, friend_number, outgoing)
        : mock_peer_packet(tox, friend_number, outgoing);
    if (!peer.handled) {
        tox->pending_packets.push_back(
            {friend_number, std::vector<std::uint8_t>(data, data + length)});
    } else {
        for (auto &reply : peer.replies) {
            tox->pending_packets.push_back(
                {friend_number, std::move(reply)});
        }
    }
    if (outgoing_ratox_type) {
        append_authority_audit(
            *tox, "ratox-sent type=" +
                      std::string(iotox::protocol::ratox::to_string(
                          *outgoing_ratox_type)) +
                      " size=" + std::to_string(length));
    }
    return true;
}

IOTOX_MOCK_EXPORT bool tox_file_control(
    Tox *tox, Tox_Friend_Number friend_number, Tox_File_Number file_number,
    Tox_File_Control control, Tox_Err_File_Control *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_CONTROL_FRIEND_NOT_FOUND);
        return false;
    }
    MockTransfer *transfer = find_transfer(tox, friend_number, file_number);
    if (transfer == nullptr) {
        set_error(error, TOX_ERR_FILE_CONTROL_NOT_FOUND);
        return false;
    }

    switch (control) {
        case TOX_FILE_CONTROL_RESUME:
            transfer->local_paused = false;
            if (transfer->receiving && !transfer->peer_paused &&
                transfer->position < transfer->file_size &&
                transfer->position <= transfer->incoming_data.size() &&
                !tox->defer_incoming_file) {
                const auto offset = static_cast<std::size_t>(
                    transfer->position);
                const bool disconnect_after_prefix =
                    !tox->sync_disconnect_fired &&
                    tox->sync_disconnect_self_first_byte <= 0xffU &&
                    tox->sync_disconnect_after_file_bytes != 0U &&
                    tox->address.front() == static_cast<std::uint8_t>(
                        tox->sync_disconnect_self_first_byte);
                if (disconnect_after_prefix) {
                    const std::size_t remaining =
                        transfer->incoming_data.size() - offset;
                    const std::size_t prefix = std::min(
                        remaining,
                        static_cast<std::size_t>(
                            tox->sync_disconnect_after_file_bytes));
                    tox->pending_file_chunks.push_back(
                        {friend_number, file_number, transfer->position,
                         std::vector<std::uint8_t>(
                             transfer->incoming_data.begin() +
                                 static_cast<std::ptrdiff_t>(offset),
                             transfer->incoming_data.begin() +
                                 static_cast<std::ptrdiff_t>(offset + prefix))});
                    transfer->position +=
                        static_cast<std::uint64_t>(prefix);
                    tox->sync_disconnect_fired = true;
                    tox->pending_sync_disconnect_after_file_chunk =
                        friend_number;
                    append_authority_audit(
                        *tox, "sync-forced-disconnect self-first-byte=" +
                                  std::to_string(tox->address.front()) +
                                  " friend=" +
                                  std::to_string(friend_number) +
                                  " after-file-bytes=" +
                                  std::to_string(prefix));
                } else {
                    tox->pending_file_chunks.push_back(
                        {friend_number, file_number, transfer->position,
                         std::vector<std::uint8_t>(
                             transfer->incoming_data.begin() +
                                 static_cast<std::ptrdiff_t>(offset),
                             transfer->incoming_data.end())});
                    tox->pending_file_chunks.push_back(
                        {friend_number, file_number, transfer->file_size, {}});
                    transfer->position = transfer->file_size;
                    transfer->finished = true;
                }
            }
            break;
        case TOX_FILE_CONTROL_PAUSE:
            if (tox->file_pause_already_paused_remaining != 0U) {
                --tox->file_pause_already_paused_remaining;
                transfer->local_paused = true;
                set_error(error, TOX_ERR_FILE_CONTROL_ALREADY_PAUSED);
                return false;
            }
            transfer->local_paused = true;
            break;
        case TOX_FILE_CONTROL_CANCEL:
            transfer->finished = true;
            break;
        default:
            set_error(error, TOX_ERR_FILE_CONTROL_DENIED);
            return false;
    }

    set_error(error, TOX_ERR_FILE_CONTROL_OK);
    return true;
}

IOTOX_MOCK_EXPORT bool tox_file_seek(
    Tox *tox, Tox_Friend_Number friend_number, Tox_File_Number file_number,
    std::uint64_t position, Tox_Err_File_Seek *error) {
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_SEEK_FRIEND_NOT_FOUND);
        return false;
    }
    MockTransfer *transfer = find_transfer(tox, friend_number, file_number);
    if (transfer == nullptr) {
        set_error(error, TOX_ERR_FILE_SEEK_NOT_FOUND);
        return false;
    }
    if (!transfer->receiving ||
        (!transfer->local_paused && !transfer->peer_paused)) {
        set_error(error, TOX_ERR_FILE_SEEK_DENIED);
        return false;
    }
    if (transfer->file_size != UINT64_MAX && position > transfer->file_size) {
        set_error(error, TOX_ERR_FILE_SEEK_INVALID_POSITION);
        return false;
    }
    transfer->position = position;
    set_error(error, TOX_ERR_FILE_SEEK_OK);
    return true;
}

IOTOX_MOCK_EXPORT bool tox_file_get_file_id(
    const Tox *tox, Tox_Friend_Number friend_number,
    Tox_File_Number file_number, std::uint8_t *file_id,
    Tox_Err_File_Get *error) {
    if (file_id == nullptr) {
        set_error(error, TOX_ERR_FILE_GET_NULL);
        return false;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_GET_FRIEND_NOT_FOUND);
        return false;
    }
    MockTransfer *transfer =
        find_transfer(const_cast<Tox *>(tox), friend_number, file_number);
    if (transfer == nullptr) {
        set_error(error, TOX_ERR_FILE_GET_NOT_FOUND);
        return false;
    }
    transfer->file_id_read = true;
    std::copy(transfer->file_id.begin(), transfer->file_id.end(), file_id);
    set_error(error, TOX_ERR_FILE_GET_OK);
    return true;
}

IOTOX_MOCK_EXPORT Tox_File_Number tox_file_by_id(
    const Tox *tox, Tox_Friend_Number friend_number,
    const std::uint8_t *file_id, Tox_Err_File_By_Id *error) {
    if (file_id == nullptr) {
        set_error(error, TOX_ERR_FILE_BY_ID_NULL);
        return iotox::toxcore::abi::kFileNumberFailure;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_BY_ID_FRIEND_NOT_FOUND);
        return iotox::toxcore::abi::kFileNumberFailure;
    }
    const auto found = std::find_if(
        tox->transfers.begin(), tox->transfers.end(),
        [friend_number, file_id](const MockTransfer &transfer) {
            return transfer.friend_number == friend_number && !transfer.finished &&
                   std::equal(transfer.file_id.begin(), transfer.file_id.end(), file_id);
        });
    if (found == tox->transfers.end()) {
        set_error(error, TOX_ERR_FILE_BY_ID_NOT_FOUND);
        return iotox::toxcore::abi::kFileNumberFailure;
    }
    set_error(error, TOX_ERR_FILE_BY_ID_OK);
    return found->file_number;
}

IOTOX_MOCK_EXPORT Tox_File_Number tox_file_send(
    Tox *tox, Tox_Friend_Number friend_number, std::uint32_t kind,
    std::uint64_t file_size, const std::uint8_t *file_id,
    const std::uint8_t *filename, std::size_t filename_length,
    Tox_Err_File_Send *error) {
    if (tox == nullptr || (filename == nullptr && filename_length != 0U)) {
        set_error(error, TOX_ERR_FILE_SEND_NULL);
        return iotox::toxcore::abi::kFileNumberFailure;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_SEND_FRIEND_NOT_FOUND);
        return iotox::toxcore::abi::kFileNumberFailure;
    }
    if (filename_length > iotox::toxcore::abi::kMaxFilenameLength) {
        set_error(error, TOX_ERR_FILE_SEND_NAME_TOO_LONG);
        return iotox::toxcore::abi::kFileNumberFailure;
    }

    MockTransfer transfer;
    transfer.friend_number = friend_number;
    transfer.file_number = tox->next_outgoing_file_number++;
    transfer.kind = kind;
    transfer.file_size = file_size;
    transfer.receiving = false;
    if (file_id != nullptr) {
        std::copy_n(file_id, transfer.file_id.size(), transfer.file_id.begin());
    } else {
        for (std::size_t index = 0U; index < transfer.file_id.size(); ++index) {
            transfer.file_id[index] = static_cast<std::uint8_t>(
                (static_cast<std::uint64_t>(transfer.file_number) * 17U + index) & 0xFFU);
        }
    }
    if (filename_length != 0U) {
        transfer.filename.assign(filename, filename + filename_length);
    }
    if (file_size != UINT64_MAX &&
        file_size <= static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        transfer.sent_data.resize(static_cast<std::size_t>(file_size));
    }
    transfer.requested_length = next_request_length(transfer);
    tox->transfers.push_back(transfer);
    tox->pending_file_chunk_requests.push_back(
        {friend_number, transfer.file_number, transfer.position,
         transfer.requested_length});
    set_error(error, TOX_ERR_FILE_SEND_OK);
    return transfer.file_number;
}

IOTOX_MOCK_EXPORT bool tox_file_send_chunk(
    Tox *tox, Tox_Friend_Number friend_number, Tox_File_Number file_number,
    std::uint64_t position, const std::uint8_t *data, std::size_t length,
    Tox_Err_File_Send_Chunk *error) {
    if (length != 0U && data == nullptr) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_NULL);
        return false;
    }
    if (!valid_friend(tox, friend_number)) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_FRIEND_NOT_FOUND);
        return false;
    }
    if (tox->require_inline_file_chunks &&
        !tox->inside_file_chunk_request_callback) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_SENDQ);
        return false;
    }
    MockTransfer *transfer = find_transfer(tox, friend_number, file_number);
    if (transfer == nullptr) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_NOT_FOUND);
        return false;
    }
    if (transfer->receiving || transfer->local_paused ||
        transfer->peer_paused) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_NOT_TRANSFERRING);
        return false;
    }
    if (position != transfer->position) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_WRONG_POSITION);
        return false;
    }
    if (length != transfer->requested_length) {
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_INVALID_LENGTH);
        return false;
    }

    if (length == 0U) {
        transfer->finished = true;
        set_error(error, TOX_ERR_FILE_SEND_CHUNK_OK);
        return true;
    }

    if (!transfer->sent_data.empty() &&
        position <= transfer->sent_data.size() &&
        length <= transfer->sent_data.size() - static_cast<std::size_t>(position)) {
        std::copy_n(
            data, length,
            transfer->sent_data.begin() + static_cast<std::ptrdiff_t>(position));
    }
    transfer->position += length;
    transfer->requested_length = next_request_length(*transfer);
    tox->pending_file_chunk_requests.push_back(
        {friend_number, file_number, transfer->position,
         transfer->requested_length});
    if (transfer->requested_length == 0U &&
        transfer->file_size != std::numeric_limits<std::uint64_t>::max()) {
        // In c-toxcore a zero-length chunk-request callback is terminal: the
        // sender releases its resources and must not answer it with another
        // tox_file_send_chunk call. Keep the callback queued, but make the
        // transfer unavailable to further API operations.
        capture_sent_file(*transfer, tox->capture_sent_file_path);
        transfer->finished = true;
    }
    set_error(error, TOX_ERR_FILE_SEND_CHUNK_OK);
    return true;
}
