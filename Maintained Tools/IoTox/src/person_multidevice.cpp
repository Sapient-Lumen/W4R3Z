#include "iotox/person_multidevice.hpp"

#include "iotox/peer_alias.hpp"
#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"
#include "iotox/toxcore/abi.hpp"

#include <algorithm>
#include <charconv>
#include <filesystem>
#include <sstream>
#include <string>
#include <system_error>
#include <tuple>
#include <vector>

namespace iotox::person {
namespace {

constexpr std::string_view kCardHeader = "iotox-person-delivery-card-v1";
constexpr std::string_view kMessageHeader = "iotox-person-message-v1";
constexpr std::string_view kDelegationHeader =
    "iotox-person-sender-delegation-v1";
constexpr std::string_view kDeviceMessageHeader =
    "iotox-person-device-message-v1";
constexpr std::string_view kCardFloorHeader = "iotox-person-card-floor-v1";
constexpr std::string_view kSeenHeader = "iotox-person-seen-v1";
constexpr std::string_view kGroupHeader = "iotox-person-group-v1";
constexpr std::string_view kGroupMessageHeader =
    "iotox-person-group-message-v1";
constexpr std::string_view kGroupDeviceMessageHeader =
    "iotox-person-group-device-message-v1";
constexpr std::string_view kContactBookHeader =
    "iotox-person-contact-book-v1";
constexpr std::string_view kTranscriptHeader =
    "iotox-person-transcript-v1";
constexpr std::string_view kReceiptHeader =
    "iotox-person-receipt-v1";
constexpr std::string_view kReceiptStoreHeader =
    "iotox-person-receipt-store-v1";
constexpr std::string_view kOutboxHeader =
    "iotox-person-outbox-v1";
constexpr std::string_view kToxBridgeMessageHeader =
    "iotox-person-tox-bridge-message-v1";
constexpr std::string_view kToxBridgeStoreHeader =
    "iotox-person-tox-bridge-store-v1";
constexpr std::string_view kCardDigestDomain =
    "iotox-person-delivery-card-digest-v1";
constexpr std::string_view kMessageDigestDomain =
    "iotox-person-message-digest-v1";
constexpr std::string_view kMessageIdDomain =
    "iotox-person-message-id-v1";
constexpr std::string_view kDelegationDigestDomain =
    "iotox-person-sender-delegation-digest-v1";
constexpr std::string_view kDeviceMessageDigestDomain =
    "iotox-person-device-message-digest-v1";
constexpr std::string_view kDeviceMessageIdDomain =
    "iotox-person-device-message-id-v1";
constexpr std::string_view kGroupIdDomain = "iotox-person-group-id-v1";
constexpr std::string_view kGroupDigestDomain =
    "iotox-person-group-digest-v1";
constexpr std::string_view kGroupMessageDigestDomain =
    "iotox-person-group-message-digest-v1";
constexpr std::string_view kGroupMessageIdDomain =
    "iotox-person-group-message-id-v1";
constexpr std::string_view kGroupDeviceMessageDigestDomain =
    "iotox-person-group-device-message-digest-v1";
constexpr std::string_view kGroupDeviceMessageIdDomain =
    "iotox-person-group-device-message-id-v1";
constexpr std::string_view kPayloadDigestDomain =
    "iotox-person-payload-digest-v1";
constexpr std::string_view kReceiptDigestDomain =
    "iotox-person-receipt-digest-v1";
constexpr std::string_view kToxBridgeMessageDigestDomain =
    "iotox-person-tox-bridge-message-digest-v1";
constexpr std::string_view kToxBridgeMessageIdDomain =
    "iotox-person-tox-bridge-message-id-v1";
constexpr std::string_view kToxBridgePayloadDigestDomain =
    "iotox-person-tox-bridge-payload-digest-v1";

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t value) {
        return value == 0U;
    });
}

[[nodiscard]] bool nonzero_key(
    const security::SigningPublicKey &key) noexcept {
    return !all_zero(key);
}

[[nodiscard]] Result<std::uint64_t> parse_u64_decimal(
    std::string_view text, std::string_view label) {
    if (text.empty()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " is empty"};
    }
    std::uint64_t value = 0U;
    const auto parsed =
        std::from_chars(text.data(), text.data() + text.size(), value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " is not a canonical decimal integer"};
    }
    if (text.size() > 1U && text.front() == '0') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has a leading zero"};
    }
    return value;
}

[[nodiscard]] int hex_nibble(char value) {
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'A' && value <= 'F') return 10 + value - 'A';
    return -1;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> parse_hex_any(
    std::string_view text, std::string_view label) {
    if (text.size() % 2U != 0U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " must contain an even number of hexadecimal characters"};
    }
    std::vector<std::uint8_t> output;
    output.reserve(text.size() / 2U);
    for (std::size_t index = 0U; index < text.size(); index += 2U) {
        const int high = hex_nibble(text[index]);
        const int low = hex_nibble(text[index + 1U]);
        if (high < 0 || low < 0) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) +
                              " contains a non-canonical uppercase hexadecimal character"};
        }
        output.push_back(static_cast<std::uint8_t>((high << 4) | low));
    }
    if (security::hex(output) != text) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " is not canonical uppercase hexadecimal"};
    }
    return output;
}

template <std::size_t Size>
[[nodiscard]] Result<std::array<std::uint8_t, Size>> parse_hex_array(
    std::string_view text, std::string_view label) {
    auto decoded = security::decode_hex_exact(text, Size, label);
    if (!decoded) return decoded.status();
    if (security::hex(decoded.value()) != text) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " is not canonical uppercase hexadecimal"};
    }
    std::array<std::uint8_t, Size> result{};
    std::copy_n(decoded.value().begin(), Size, result.begin());
    return result;
}

[[nodiscard]] Result<std::vector<std::string_view>> split_lines(
    std::span<const std::uint8_t> bytes, std::string_view label) {
    if (bytes.empty() || bytes.back() != static_cast<std::uint8_t>('\n')) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " must end with exactly one LF"};
    }
    const std::string_view text(
        reinterpret_cast<const char *>(bytes.data()), bytes.size());
    std::vector<std::string_view> lines;
    std::size_t begin = 0U;
    while (begin < text.size()) {
        const std::size_t end = text.find('\n', begin);
        if (end == std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " line parser lost final LF"};
        }
        if (end > begin && text[end - 1U] == '\r') {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " may not contain CRLF"};
        }
        lines.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    if (!lines.empty() && lines.back().empty()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has an extra blank trailing line"};
    }
    return lines;
}

[[nodiscard]] Result<std::string_view> field(
    std::string_view line, std::string_view prefix,
    std::string_view label) {
    if (!line.starts_with(prefix)) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " expected field " +
                          std::string(prefix)};
    }
    return line.substr(prefix.size());
}

[[nodiscard]] Status validate_card_shape(const DeliveryCard &card) {
    if (!nonzero_key(card.person)) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card person key is zero"};
    }
    if (card.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card generation must be nonzero"};
    }
    if (all_zero(card.roster_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card roster digest is zero"};
    }
    if (card.routes.empty() ||
        card.routes.size() > kMaximumDeliveryRoutes) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card must contain 1..64 routes"};
    }
    for (std::size_t index = 0U; index < card.routes.size(); ++index) {
        if (!nonzero_key(card.routes[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person delivery card route key is zero"};
        }
        if (index > 0U && !(card.routes[index - 1U] < card.routes[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person delivery card routes must be sorted and unique"};
        }
    }
    return Status::success();
}

[[nodiscard]] Status validate_message_shape(
    const MessageEnvelope &message, bool require_signature) {
    if (!nonzero_key(message.from_person) ||
        !nonzero_key(message.to_person)) {
        return Status{ErrorCode::invalid_argument,
                      "person message endpoint key is zero"};
    }
    if (all_zero(message.nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "person message nonce is zero"};
    }
    if (all_zero(message.message_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person message id is zero"};
    }
    if (message.body.empty() ||
        message.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person message body must contain 1..320 bytes"};
    }
    if (require_signature && all_zero(message.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person message signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_label(std::string_view label) {
    if (label.empty() || label.size() > kMaximumDelegationLabelBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation label must contain 1..64 bytes"};
    }
    return peer_alias::validate_name(label);
}

[[nodiscard]] Status validate_sender_delegation_shape(
    const SenderDelegation &delegation, bool require_signature) {
    if (!nonzero_key(delegation.person) || !nonzero_key(delegation.device)) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation key is zero"};
    }
    if (delegation.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation generation must be nonzero"};
    }
    if (all_zero(delegation.roster_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation roster digest is zero"};
    }
    const Status label = validate_label(delegation.label);
    if (!label.ok()) {
        return Status{label.code(),
                      "person sender delegation label is invalid: " +
                          label.message()};
    }
    if (require_signature && all_zero(delegation.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_device_message_shape(
    const DeviceMessageEnvelope &message, bool require_signature) {
    if (!nonzero_key(message.from_person) ||
        !nonzero_key(message.from_device) ||
        !nonzero_key(message.to_person)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message endpoint key is zero"};
    }
    if (all_zero(message.delegation_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message delegation digest is zero"};
    }
    if (all_zero(message.nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message nonce is zero"};
    }
    if (all_zero(message.message_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message id is zero"};
    }
    if (message.body.empty() ||
        message.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person device message body must contain 1..320 bytes"};
    }
    if (require_signature && all_zero(message.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_card_floor_shape(const CardFloor &floor) {
    if (!nonzero_key(floor.person)) {
        return Status{ErrorCode::invalid_argument,
                      "person card floor person key is zero"};
    }
    if (floor.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person card floor generation must be nonzero"};
    }
    if (all_zero(floor.digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person card floor digest is zero"};
    }
    return Status::success();
}

[[nodiscard]] bool seen_entry_less(
    const SeenEntry &left, const SeenEntry &right) {
    return std::tie(left.scope, left.person, left.group, left.message_id) <
           std::tie(right.scope, right.person, right.group, right.message_id);
}

[[nodiscard]] Status validate_seen_entry(const SeenEntry &entry) {
    if (entry.scope != "person" && entry.scope != "group") {
        return Status{ErrorCode::invalid_argument,
                      "person seen entry scope must be person or group"};
    }
    if (!nonzero_key(entry.person)) {
        return Status{ErrorCode::invalid_argument,
                      "person seen entry speaker key is zero"};
    }
    if (all_zero(entry.message_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person seen entry message id is zero"};
    }
    const bool group_zero = all_zero(entry.group);
    if (entry.scope == "person" && !group_zero) {
        return Status{ErrorCode::invalid_argument,
                      "person seen entry must not carry a group id"};
    }
    if (entry.scope == "group" && group_zero) {
        return Status{ErrorCode::invalid_argument,
                      "group seen entry group id is zero"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_seen_store_shape(const SeenStore &store) {
    if (store.entries.size() > kMaximumSeenEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person seen store exceeds 4096 entries"};
    }
    for (std::size_t index = 0U; index < store.entries.size(); ++index) {
        const Status valid = validate_seen_entry(store.entries[index]);
        if (!valid.ok()) return valid;
        if (index > 0U &&
            !seen_entry_less(store.entries[index - 1U],
                             store.entries[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person seen store entries must be sorted and unique"};
        }
    }
    return Status::success();
}

[[nodiscard]] Status validate_group_shape(
    const GroupDescriptor &group, bool require_signature) {
    if (all_zero(group.group_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person group id is zero"};
    }
    if (!nonzero_key(group.creator_person)) {
        return Status{ErrorCode::invalid_argument,
                      "person group creator is zero"};
    }
    if (group.generation == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person group generation must be nonzero"};
    }
    if (all_zero(group.group_nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "person group nonce is zero"};
    }
    if (group.title.empty() ||
        group.title.size() > kMaximumGroupTitleBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group title must contain 1..120 bytes"};
    }
    if (group.members.empty() ||
        group.members.size() > kMaximumGroupMembers) {
        return Status{ErrorCode::invalid_argument,
                      "person group must contain 1..64 members"};
    }
    bool creator_seen = false;
    for (std::size_t index = 0U; index < group.members.size(); ++index) {
        if (!nonzero_key(group.members[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person group member key is zero"};
        }
        if (index > 0U && !(group.members[index - 1U] < group.members[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person group members must be sorted and unique"};
        }
        creator_seen = creator_seen ||
            group.members[index] == group.creator_person;
    }
    if (!creator_seen) {
        return Status{ErrorCode::invalid_argument,
                      "person group creator must be a member"};
    }
    if (require_signature && all_zero(group.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person group signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_group_message_shape(
    const GroupMessageEnvelope &message, bool require_signature) {
    if (all_zero(message.group_id) || all_zero(message.nonce) ||
        all_zero(message.message_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person group message id material is zero"};
    }
    if (!nonzero_key(message.from_person)) {
        return Status{ErrorCode::invalid_argument,
                      "person group message speaker is zero"};
    }
    if (message.body.empty() ||
        message.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group message body must contain 1..320 bytes"};
    }
    if (require_signature && all_zero(message.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person group message signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_group_device_message_shape(
    const GroupDeviceMessageEnvelope &message, bool require_signature) {
    if (all_zero(message.group_id) || all_zero(message.delegation_digest) ||
        all_zero(message.nonce) || all_zero(message.message_id)) {
        return Status{ErrorCode::invalid_argument,
                      "person group device message id material is zero"};
    }
    if (!nonzero_key(message.from_person) ||
        !nonzero_key(message.from_device)) {
        return Status{ErrorCode::invalid_argument,
                      "person group device message speaker key is zero"};
    }
    if (message.body.empty() ||
        message.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group device message body must contain 1..320 bytes"};
    }
    if (require_signature && all_zero(message.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person group device message signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_direction(std::string_view direction);

[[nodiscard]] Status validate_tox_message_kind(std::string_view kind) {
    if (kind == "message" || kind == "action") return Status::success();
    return Status{ErrorCode::invalid_argument,
                  "person Tox bridge kind must be message or action"};
}

[[nodiscard]] Status validate_tox_bridge_message_shape(
    const ToxBridgeMessageEnvelope &message, bool require_signature) {
    const Status direction = validate_direction(message.direction);
    if (!direction.ok()) return direction;
    const Status kind = validate_tox_message_kind(message.tox_kind);
    if (!kind.ok()) return kind;
    if (!nonzero_key(message.observer_person) ||
        !nonzero_key(message.observer_device) ||
        all_zero(message.delegation_digest) ||
        all_zero(message.external_tox_key) ||
        all_zero(message.nonce) || all_zero(message.message_id) ||
        message.observed_unix_ms == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge message identity material is invalid"};
    }
    if (message.body.empty() ||
        message.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge body must contain 1..320 bytes"};
    }
    if (require_signature && all_zero(message.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] Status validate_tox_bridge_entry(
    const ToxBridgeEntry &entry, bool require_sequence) {
    if (require_sequence && entry.sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge entry sequence is zero"};
    }
    const Status direction = validate_direction(entry.direction);
    if (!direction.ok()) return direction;
    const Status kind = validate_tox_message_kind(entry.tox_kind);
    if (!kind.ok()) return kind;
    if (!nonzero_key(entry.observer_person) ||
        !nonzero_key(entry.observer_device) ||
        all_zero(entry.external_tox_key) || all_zero(entry.message_id) ||
        all_zero(entry.payload_digest) || entry.observed_unix_ms == 0U ||
        entry.body.empty() ||
        entry.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge entry identity or body is invalid"};
    }
    return Status::success();
}

[[nodiscard]] bool same_tox_bridge_identity(
    const ToxBridgeEntry &left, const ToxBridgeEntry &right) {
    return left.direction == right.direction &&
           left.observer_person == right.observer_person &&
           left.external_tox_key == right.external_tox_key &&
           left.message_id == right.message_id;
}

[[nodiscard]] Status validate_tox_bridge_store_shape(
    const ToxBridgeStore &store) {
    if (store.next_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge next sequence is zero"};
    }
    if (store.entries.size() > kMaximumToxBridgeEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person Tox bridge store exceeds 8192 entries"};
    }
    std::uint64_t previous_sequence = 0U;
    for (std::size_t index = 0U; index < store.entries.size(); ++index) {
        const ToxBridgeEntry &entry = store.entries[index];
        const Status valid = validate_tox_bridge_entry(entry, true);
        if (!valid.ok()) return valid;
        if (entry.sequence <= previous_sequence ||
            entry.sequence >= store.next_sequence) {
            return Status{ErrorCode::invalid_argument,
                          "person Tox bridge sequences are not canonical"};
        }
        for (std::size_t prior = 0U; prior < index; ++prior) {
            if (same_tox_bridge_identity(store.entries[prior], entry)) {
                return Status{ErrorCode::invalid_argument,
                              "person Tox bridge store repeats a message id"};
            }
        }
        previous_sequence = entry.sequence;
    }
    return Status::success();
}

[[nodiscard]] std::vector<std::string_view> split_delimited(
    std::string_view text, char delimiter) {
    std::vector<std::string_view> fields;
    std::size_t begin = 0U;
    while (begin <= text.size()) {
        const std::size_t end = text.find(delimiter, begin);
        if (end == std::string_view::npos) {
            fields.push_back(text.substr(begin));
            break;
        }
        fields.push_back(text.substr(begin, end - begin));
        begin = end + 1U;
    }
    return fields;
}

[[nodiscard]] Status validate_contact_entry(const ContactEntry &entry) {
    const Status name = peer_alias::validate_name(entry.name);
    if (!name.ok()) {
        return Status{name.code(),
                      "person contact name is invalid: " + name.message()};
    }
    if (!nonzero_key(entry.person)) {
        return Status{ErrorCode::invalid_argument,
                      "person contact person key is zero"};
    }
    if (entry.generation == 0U || all_zero(entry.card_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person contact card generation or digest is invalid"};
    }
    if (entry.routes.empty() ||
        entry.routes.size() > kMaximumDeliveryRoutes) {
        return Status{ErrorCode::invalid_argument,
                      "person contact must contain 1..64 routes"};
    }
    for (std::size_t index = 0U; index < entry.routes.size(); ++index) {
        if (!nonzero_key(entry.routes[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person contact route key is zero"};
        }
        if (index > 0U && !(entry.routes[index - 1U] < entry.routes[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person contact routes must be sorted and unique"};
        }
    }
    return Status::success();
}

[[nodiscard]] bool contact_entry_less(
    const ContactEntry &left, const ContactEntry &right) {
    return left.name < right.name;
}

[[nodiscard]] Status validate_contact_book_shape(const ContactBook &book) {
    if (book.contacts.size() > kMaximumContacts) {
        return Status{ErrorCode::resource_exhausted,
                      "person contact book exceeds 256 contacts"};
    }
    std::vector<security::SigningPublicKey> people;
    people.reserve(book.contacts.size());
    for (std::size_t index = 0U; index < book.contacts.size(); ++index) {
        const Status valid = validate_contact_entry(book.contacts[index]);
        if (!valid.ok()) return valid;
        if (index > 0U &&
            !contact_entry_less(book.contacts[index - 1U],
                                book.contacts[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person contact book entries must be sorted by name"};
        }
        if (std::find(people.begin(), people.end(),
                      book.contacts[index].person) != people.end()) {
            return Status{ErrorCode::invalid_argument,
                          "person contact book repeats a person key"};
        }
        people.push_back(book.contacts[index].person);
    }
    return Status::success();
}

[[nodiscard]] Status validate_direction(std::string_view direction) {
    if (direction == "in" || direction == "out") return Status::success();
    return Status{ErrorCode::invalid_argument,
                  "person transcript direction must be in or out"};
}

[[nodiscard]] Status validate_transcript_entry(
    const TranscriptEntry &entry, bool require_sequence) {
    if (require_sequence && entry.sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person transcript entry sequence is zero"};
    }
    const Status direction = validate_direction(entry.direction);
    if (!direction.ok()) return direction;
    if (entry.scope != "person" && entry.scope != "group") {
        return Status{ErrorCode::invalid_argument,
                      "person transcript scope must be person or group"};
    }
    if (!nonzero_key(entry.from_person) || all_zero(entry.message_id) ||
        all_zero(entry.payload_digest) || entry.body.empty() ||
        entry.body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person transcript entry has invalid identity or body"};
    }
    if (entry.scope == "person") {
        if (!nonzero_key(entry.to_person) || !all_zero(entry.group)) {
            return Status{ErrorCode::invalid_argument,
                          "person transcript entry endpoint is invalid"};
        }
    } else {
        if (all_zero(entry.group) || !all_zero(entry.to_person)) {
            return Status{ErrorCode::invalid_argument,
                          "group transcript entry endpoint is invalid"};
        }
    }
    return Status::success();
}

[[nodiscard]] bool same_transcript_identity(
    const TranscriptEntry &left, const TranscriptEntry &right) {
    return left.scope == right.scope && left.group == right.group &&
           left.message_id == right.message_id;
}

[[nodiscard]] Status validate_transcript_store_shape(
    const TranscriptStore &store) {
    if (store.next_sequence == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person transcript next sequence is zero"};
    }
    if (store.entries.size() > kMaximumTranscriptEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person transcript exceeds 8192 entries"};
    }
    std::uint64_t previous_sequence = 0U;
    for (std::size_t index = 0U; index < store.entries.size(); ++index) {
        const TranscriptEntry &entry = store.entries[index];
        const Status valid = validate_transcript_entry(entry, true);
        if (!valid.ok()) return valid;
        if (entry.sequence <= previous_sequence ||
            entry.sequence >= store.next_sequence) {
            return Status{ErrorCode::invalid_argument,
                          "person transcript sequences are not canonical"};
        }
        for (std::size_t prior = 0U; prior < index; ++prior) {
            if (same_transcript_identity(store.entries[prior], entry)) {
                return Status{ErrorCode::invalid_argument,
                              "person transcript repeats a message id"};
            }
        }
        previous_sequence = entry.sequence;
    }
    return Status::success();
}

[[nodiscard]] Status validate_receipt_shape(
    const ReceiptRecord &receipt, bool require_signature) {
    if (receipt.scope != "person" && receipt.scope != "group") {
        return Status{ErrorCode::invalid_argument,
                      "person receipt scope must be person or group"};
    }
    if (all_zero(receipt.message_id) ||
        !nonzero_key(receipt.recipient_person) ||
        !nonzero_key(receipt.recipient_device) ||
        all_zero(receipt.delegation_digest)) {
        return Status{ErrorCode::invalid_argument,
                      "person receipt identity material is invalid"};
    }
    if (receipt.scope == "person" && !all_zero(receipt.group)) {
        return Status{ErrorCode::invalid_argument,
                      "person receipt must not carry a group id"};
    }
    if (receipt.scope == "group" && all_zero(receipt.group)) {
        return Status{ErrorCode::invalid_argument,
                      "group receipt group id is zero"};
    }
    if (require_signature && all_zero(receipt.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person receipt signature is empty"};
    }
    return Status::success();
}

[[nodiscard]] bool same_receipt_identity(
    const ReceiptRecord &left, const ReceiptRecord &right) {
    return left.scope == right.scope && left.group == right.group &&
           left.message_id == right.message_id &&
           left.recipient_person == right.recipient_person &&
           left.recipient_device == right.recipient_device;
}

[[nodiscard]] bool receipt_less(
    const ReceiptRecord &left, const ReceiptRecord &right) {
    return std::tie(left.scope, left.group, left.message_id,
                    left.recipient_person, left.recipient_device) <
           std::tie(right.scope, right.group, right.message_id,
                    right.recipient_person, right.recipient_device);
}

[[nodiscard]] Status validate_receipt_store_shape(
    const ReceiptStore &store) {
    if (store.receipts.size() > kMaximumReceiptRecords) {
        return Status{ErrorCode::resource_exhausted,
                      "person receipt store exceeds 8192 receipts"};
    }
    for (std::size_t index = 0U; index < store.receipts.size(); ++index) {
        const Status valid = validate_receipt_shape(store.receipts[index], true);
        if (!valid.ok()) return valid;
        if (index > 0U &&
            !receipt_less(store.receipts[index - 1U],
                          store.receipts[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person receipt store entries must be sorted and unique"};
        }
    }
    return Status::success();
}

[[nodiscard]] Status validate_outbox_item(const OutboxItem &item) {
    if (all_zero(item.message_id) || !nonzero_key(item.recipient_person) ||
        item.card_generation == 0U || all_zero(item.card_digest) ||
        all_zero(item.payload_digest) || item.payload.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox item identity material is invalid"};
    }
    if (item.payload.size() > toxcore::abi::kMaxMessageLength) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox payload exceeds Tox text bound"};
    }
    if (item.pending_routes.size() + item.sent_routes.size() == 0U ||
        item.pending_routes.size() + item.sent_routes.size() >
            kMaximumDeliveryRoutes) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox route set is empty or too large"};
    }
    if ((item.attempts == 0U && item.last_attempt_unix_ms != 0U) ||
        (item.attempts != 0U && item.last_attempt_unix_ms == 0U)) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox scheduler attempt metadata is inconsistent"};
    }
    if (item.created_unix_ms != 0U && item.last_attempt_unix_ms != 0U &&
        item.last_attempt_unix_ms < item.created_unix_ms) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox last attempt predates creation"};
    }
    const auto validate_routes = [](const std::vector<DeliveryRouteKey> &routes,
                                    std::string_view label) -> Status {
        for (std::size_t index = 0U; index < routes.size(); ++index) {
            if (!nonzero_key(routes[index])) {
                return Status{ErrorCode::invalid_argument,
                              std::string(label) + " route key is zero"};
            }
            if (index > 0U && !(routes[index - 1U] < routes[index])) {
                return Status{ErrorCode::invalid_argument,
                              std::string(label) +
                                  " routes must be sorted and unique"};
            }
        }
        return Status::success();
    };
    Status valid = validate_routes(item.pending_routes, "person outbox pending");
    if (!valid.ok()) return valid;
    valid = validate_routes(item.sent_routes, "person outbox sent");
    if (!valid.ok()) return valid;
    for (const auto &route : item.pending_routes) {
        if (std::binary_search(item.sent_routes.begin(),
                               item.sent_routes.end(), route)) {
            return Status{ErrorCode::invalid_argument,
                          "person outbox route is both pending and sent"};
        }
    }
    return Status::success();
}

[[nodiscard]] bool outbox_item_less(
    const OutboxItem &left, const OutboxItem &right) {
    return std::tie(left.recipient_person, left.message_id) <
           std::tie(right.recipient_person, right.message_id);
}

[[nodiscard]] Status validate_outbox_store_shape(const OutboxStore &store) {
    if (store.items.size() > kMaximumOutboxItems) {
        return Status{ErrorCode::resource_exhausted,
                      "person outbox exceeds 1024 items"};
    }
    for (std::size_t index = 0U; index < store.items.size(); ++index) {
        const Status valid = validate_outbox_item(store.items[index]);
        if (!valid.ok()) return valid;
        if (index > 0U &&
            !outbox_item_less(store.items[index - 1U], store.items[index])) {
            return Status{ErrorCode::invalid_argument,
                          "person outbox items must be sorted and unique"};
        }
    }
    return Status::success();
}

void append_bytes(
    std::vector<std::uint8_t> &output,
    std::span<const std::uint8_t> bytes) {
    output.insert(output.end(), bytes.begin(), bytes.end());
}

void append_u64_be(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(
            static_cast<std::uint8_t>((value >> shift) & 0xFFU));
    }
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_message_id_input(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &to_person,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body) {
    if (!nonzero_key(from_person) || !nonzero_key(to_person)) {
        return Status{ErrorCode::invalid_argument,
                      "person message endpoint key is zero"};
    }
    if (all_zero(nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "person message nonce is zero"};
    }
    if (body.empty() || body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person message body must contain 1..320 bytes"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(from_person.size() + to_person.size() + nonce.size() +
                  body.size());
    append_bytes(input, from_person);
    append_bytes(input, to_person);
    append_bytes(input, nonce);
    append_bytes(input, body);
    return input;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_device_message_id_input(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &from_device,
    const security::SigningPublicKey &to_person,
    const security::Digest &delegation_digest,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body) {
    if (!nonzero_key(from_person) || !nonzero_key(from_device) ||
        !nonzero_key(to_person) || all_zero(delegation_digest) ||
        all_zero(nonce)) {
        return Status{ErrorCode::invalid_argument,
                      "person device message id material is invalid"};
    }
    if (body.empty() || body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person device message body must contain 1..320 bytes"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(from_person.size() + from_device.size() + to_person.size() +
                  delegation_digest.size() + nonce.size() + body.size());
    append_bytes(input, from_person);
    append_bytes(input, from_device);
    append_bytes(input, to_person);
    append_bytes(input, delegation_digest);
    append_bytes(input, nonce);
    append_bytes(input, body);
    return input;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_group_id_input(
    const GroupDescriptor &group) {
    if (!nonzero_key(group.creator_person) || group.generation == 0U ||
        all_zero(group.group_nonce) || group.title.empty() ||
        group.title.size() > kMaximumGroupTitleBytes ||
        group.members.empty() || group.members.size() > kMaximumGroupMembers) {
        return Status{ErrorCode::invalid_argument,
                      "person group id input is invalid"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(group.creator_person.size() + group.group_nonce.size() +
                  group.title.size() + (group.members.size() * 32U) + 16U);
    append_bytes(input, group.creator_person);
    append_u64_be(input, group.generation);
    append_bytes(input, group.group_nonce);
    append_u64_be(input, static_cast<std::uint64_t>(group.title.size()));
    append_bytes(input, group.title);
    for (const auto &member : group.members) {
        append_bytes(input, member);
    }
    return input;
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_group_message_id_input(
    const security::Digest &group_id,
    const security::SigningPublicKey &from_person,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body) {
    if (all_zero(group_id) || !nonzero_key(from_person) || all_zero(nonce) ||
        body.empty() || body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group message id material is invalid"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(group_id.size() + from_person.size() + nonce.size() +
                  body.size());
    append_bytes(input, group_id);
    append_bytes(input, from_person);
    append_bytes(input, nonce);
    append_bytes(input, body);
    return input;
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_group_device_message_id_input(
    const security::Digest &group_id,
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &from_device,
    const security::Digest &delegation_digest,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body) {
    if (all_zero(group_id) || !nonzero_key(from_person) ||
        !nonzero_key(from_device) || all_zero(delegation_digest) ||
        all_zero(nonce) || body.empty() ||
        body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group device message id material is invalid"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(group_id.size() + from_person.size() + from_device.size() +
                  delegation_digest.size() + nonce.size() + body.size());
    append_bytes(input, group_id);
    append_bytes(input, from_person);
    append_bytes(input, from_device);
    append_bytes(input, delegation_digest);
    append_bytes(input, nonce);
    append_bytes(input, body);
    return input;
}

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tox_bridge_message_id_input(
    std::string_view direction,
    std::string_view tox_kind,
    const security::SigningPublicKey &observer_person,
    const security::SigningPublicKey &observer_device,
    const security::Digest &delegation_digest,
    const ToxPublicKey &external_tox_key,
    std::uint64_t observed_unix_ms,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body) {
    const Status direction_status = validate_direction(direction);
    if (!direction_status.ok()) return direction_status;
    const Status kind_status = validate_tox_message_kind(tox_kind);
    if (!kind_status.ok()) return kind_status;
    if (!nonzero_key(observer_person) || !nonzero_key(observer_device) ||
        all_zero(delegation_digest) || all_zero(external_tox_key) ||
        observed_unix_ms == 0U || all_zero(nonce) || body.empty() ||
        body.size() > kMaximumMessageBodyBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person Tox bridge message id material is invalid"};
    }
    std::vector<std::uint8_t> input;
    input.reserve(direction.size() + tox_kind.size() + observer_person.size() +
                  observer_device.size() + delegation_digest.size() +
                  external_tox_key.size() + sizeof(std::uint64_t) +
                  nonce.size() + body.size() + 2U);
    input.insert(input.end(), direction.begin(), direction.end());
    input.push_back(0U);
    input.insert(input.end(), tox_kind.begin(), tox_kind.end());
    input.push_back(0U);
    append_bytes(input, observer_person);
    append_bytes(input, observer_device);
    append_bytes(input, delegation_digest);
    append_bytes(input, external_tox_key);
    append_u64_be(input, observed_unix_ms);
    append_bytes(input, nonce);
    append_bytes(input, body);
    return input;
}

[[nodiscard]] Result<MessageNonce> random_message_nonce() {
    auto nonce = security::random_nonce_128();
    if (!nonce) return nonce.status();
    return MessageNonce{nonce.value()};
}

[[nodiscard]] Result<MessageEnvelope> parse_message_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 7U || lines[0U] != kMessageHeader) {
        return Status{ErrorCode::protocol_error,
                      "person message header or size is invalid"};
    }
    MessageEnvelope message;
    auto from =
        field(lines[1U], "from-person=", "person message");
    auto to = field(lines[2U], "to-person=", "person message");
    auto nonce = field(lines[3U], "nonce=", "person message");
    auto message_id =
        field(lines[4U], "message-id=", "person message");
    auto body = field(lines[5U], "body-hex=", "person message");
    auto signature =
        field(lines[6U], "signature=", "person message");
    if (!from) return from.status();
    if (!to) return to.status();
    if (!nonce) return nonce.status();
    if (!message_id) return message_id.status();
    if (!body) return body.status();
    if (!signature) return signature.status();
    auto from_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from.value(), "person message sender");
    auto to_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        to.value(), "person message recipient");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(nonce.value(), "person message nonce");
    auto id = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person message id");
    auto body_bytes =
        parse_hex_any(body.value(), "person message body");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person message signature");
    if (!from_key) return from_key.status();
    if (!to_key) return to_key.status();
    if (!nonce_value) return nonce_value.status();
    if (!id) return id.status();
    if (!body_bytes) return body_bytes.status();
    if (!sig) return sig.status();
    message.from_person = from_key.value();
    message.to_person = to_key.value();
    message.nonce = nonce_value.value();
    message.message_id = id.value();
    message.body = std::move(body_bytes).value();
    message.signature = sig.value();
    return message;
}

[[nodiscard]] Result<SenderDelegation> parse_delegation_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 8U || lines[0U] != kDelegationHeader) {
        return Status{ErrorCode::protocol_error,
                      "person sender delegation header or size is invalid"};
    }
    SenderDelegation delegation;
    auto person = field(lines[1U], "person=", "person sender delegation");
    auto device = field(lines[2U], "device=", "person sender delegation");
    auto generation =
        field(lines[3U], "generation=", "person sender delegation");
    auto roster_digest =
        field(lines[4U], "roster-digest=", "person sender delegation");
    auto label = field(lines[5U], "label=", "person sender delegation");
    auto expires =
        field(lines[6U], "expires-unix-ms=", "person sender delegation");
    auto signature =
        field(lines[7U], "signature=", "person sender delegation");
    if (!person) return person.status();
    if (!device) return device.status();
    if (!generation) return generation.status();
    if (!roster_digest) return roster_digest.status();
    if (!label) return label.status();
    if (!expires) return expires.status();
    if (!signature) return signature.status();
    auto person_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        person.value(), "person sender delegation person");
    auto device_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        device.value(), "person sender delegation device");
    auto generation_value = parse_u64_decimal(
        generation.value(), "person sender delegation generation");
    auto roster_digest_value = parse_hex_array<security::kDigestBytes>(
        roster_digest.value(), "person sender delegation roster digest");
    auto expires_value = parse_u64_decimal(
        expires.value(), "person sender delegation expires-unix-ms");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person sender delegation signature");
    if (!person_key) return person_key.status();
    if (!device_key) return device_key.status();
    if (!generation_value) return generation_value.status();
    if (!roster_digest_value) return roster_digest_value.status();
    if (!expires_value) return expires_value.status();
    if (!sig) return sig.status();
    delegation.person = person_key.value();
    delegation.device = device_key.value();
    delegation.generation = generation_value.value();
    delegation.roster_digest = roster_digest_value.value();
    delegation.label = std::string(label.value());
    delegation.expires_unix_ms = expires_value.value();
    delegation.signature = sig.value();
    return delegation;
}

[[nodiscard]] Result<DeviceMessageEnvelope> parse_device_message_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 9U || lines[0U] != kDeviceMessageHeader) {
        return Status{ErrorCode::protocol_error,
                      "person device message header or size is invalid"};
    }
    DeviceMessageEnvelope message;
    auto from_person =
        field(lines[1U], "from-person=", "person device message");
    auto from_device =
        field(lines[2U], "from-device=", "person device message");
    auto to_person = field(lines[3U], "to-person=", "person device message");
    auto delegation = field(
        lines[4U], "delegation-digest=", "person device message");
    auto nonce = field(lines[5U], "nonce=", "person device message");
    auto message_id =
        field(lines[6U], "message-id=", "person device message");
    auto body = field(lines[7U], "body-hex=", "person device message");
    auto signature =
        field(lines[8U], "signature=", "person device message");
    if (!from_person) return from_person.status();
    if (!from_device) return from_device.status();
    if (!to_person) return to_person.status();
    if (!delegation) return delegation.status();
    if (!nonce) return nonce.status();
    if (!message_id) return message_id.status();
    if (!body) return body.status();
    if (!signature) return signature.status();
    auto from_person_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from_person.value(), "person device message sender person");
    auto from_device_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from_device.value(), "person device message sender device");
    auto to_person_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        to_person.value(), "person device message recipient");
    auto delegation_digest = parse_hex_array<security::kDigestBytes>(
        delegation.value(), "person device message delegation digest");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(nonce.value(),
                                            "person device message nonce");
    auto id = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person device message id");
    auto body_bytes =
        parse_hex_any(body.value(), "person device message body");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person device message signature");
    if (!from_person_key) return from_person_key.status();
    if (!from_device_key) return from_device_key.status();
    if (!to_person_key) return to_person_key.status();
    if (!delegation_digest) return delegation_digest.status();
    if (!nonce_value) return nonce_value.status();
    if (!id) return id.status();
    if (!body_bytes) return body_bytes.status();
    if (!sig) return sig.status();
    message.from_person = from_person_key.value();
    message.from_device = from_device_key.value();
    message.to_person = to_person_key.value();
    message.delegation_digest = delegation_digest.value();
    message.nonce = nonce_value.value();
    message.message_id = id.value();
    message.body = std::move(body_bytes).value();
    message.signature = sig.value();
    return message;
}

[[nodiscard]] Result<ToxBridgeMessageEnvelope>
parse_tox_bridge_message_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 12U || lines[0U] != kToxBridgeMessageHeader) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge message header or size is invalid"};
    }
    ToxBridgeMessageEnvelope message;
    auto direction = field(lines[1U], "direction=", "person Tox bridge");
    auto kind = field(lines[2U], "tox-kind=", "person Tox bridge");
    auto observer_person =
        field(lines[3U], "observer-person=", "person Tox bridge");
    auto observer_device =
        field(lines[4U], "observer-device=", "person Tox bridge");
    auto delegation = field(
        lines[5U], "delegation-digest=", "person Tox bridge");
    auto external =
        field(lines[6U], "external-tox-key=", "person Tox bridge");
    auto observed =
        field(lines[7U], "observed-unix-ms=", "person Tox bridge");
    auto nonce = field(lines[8U], "nonce=", "person Tox bridge");
    auto message_id =
        field(lines[9U], "message-id=", "person Tox bridge");
    auto body = field(lines[10U], "body-hex=", "person Tox bridge");
    auto signature =
        field(lines[11U], "signature=", "person Tox bridge");
    if (!direction) return direction.status();
    if (!kind) return kind.status();
    if (!observer_person) return observer_person.status();
    if (!observer_device) return observer_device.status();
    if (!delegation) return delegation.status();
    if (!external) return external.status();
    if (!observed) return observed.status();
    if (!nonce) return nonce.status();
    if (!message_id) return message_id.status();
    if (!body) return body.status();
    if (!signature) return signature.status();
    auto observer_person_key =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            observer_person.value(), "person Tox bridge observer person");
    auto observer_device_key =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            observer_device.value(), "person Tox bridge observer device");
    auto delegation_digest = parse_hex_array<security::kDigestBytes>(
        delegation.value(), "person Tox bridge delegation digest");
    auto external_key = parse_hex_array<kToxPublicKeyBytes>(
        external.value(), "person Tox bridge external Tox key");
    auto observed_value = parse_u64_decimal(
        observed.value(), "person Tox bridge observed-unix-ms");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(nonce.value(),
                                            "person Tox bridge nonce");
    auto id = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person Tox bridge message id");
    auto body_bytes =
        parse_hex_any(body.value(), "person Tox bridge body");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person Tox bridge signature");
    if (!observer_person_key) return observer_person_key.status();
    if (!observer_device_key) return observer_device_key.status();
    if (!delegation_digest) return delegation_digest.status();
    if (!external_key) return external_key.status();
    if (!observed_value) return observed_value.status();
    if (!nonce_value) return nonce_value.status();
    if (!id) return id.status();
    if (!body_bytes) return body_bytes.status();
    if (!sig) return sig.status();
    message.direction = std::string(direction.value());
    message.tox_kind = std::string(kind.value());
    message.observer_person = observer_person_key.value();
    message.observer_device = observer_device_key.value();
    message.delegation_digest = delegation_digest.value();
    message.external_tox_key = external_key.value();
    message.observed_unix_ms = observed_value.value();
    message.nonce = nonce_value.value();
    message.message_id = id.value();
    message.body = std::move(body_bytes).value();
    message.signature = sig.value();
    return message;
}

[[nodiscard]] Result<CardFloor> parse_card_floor_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 4U || lines[0U] != kCardFloorHeader) {
        return Status{ErrorCode::protocol_error,
                      "person card floor header or size is invalid"};
    }
    CardFloor floor;
    auto person = field(lines[1U], "person=", "person card floor");
    auto generation = field(lines[2U], "generation=", "person card floor");
    auto digest = field(lines[3U], "digest=", "person card floor");
    if (!person) return person.status();
    if (!generation) return generation.status();
    if (!digest) return digest.status();
    auto person_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        person.value(), "person card floor person");
    auto generation_value =
        parse_u64_decimal(generation.value(), "person card floor generation");
    auto digest_value = parse_hex_array<security::kDigestBytes>(
        digest.value(), "person card floor digest");
    if (!person_key) return person_key.status();
    if (!generation_value) return generation_value.status();
    if (!digest_value) return digest_value.status();
    floor.person = person_key.value();
    floor.generation = generation_value.value();
    floor.digest = digest_value.value();
    return floor;
}

[[nodiscard]] Result<SeenEntry> parse_seen_entry(std::string_view line) {
    auto payload = field(line, "entry=", "person seen store");
    if (!payload) return payload.status();
    std::vector<std::string_view> parts;
    std::size_t begin = 0U;
    while (begin <= payload.value().size()) {
        const std::size_t end = payload.value().find('|', begin);
        if (end == std::string_view::npos) {
            parts.push_back(payload.value().substr(begin));
            break;
        }
        parts.push_back(payload.value().substr(begin, end - begin));
        begin = end + 1U;
    }
    if (parts.size() != 4U) {
        return Status{ErrorCode::protocol_error,
                      "person seen entry must have four fields"};
    }
    SeenEntry entry;
    entry.scope = std::string(parts[0U]);
    auto person = parse_hex_array<security::kSigningPublicKeyBytes>(
        parts[1U], "person seen entry person");
    auto group = parse_hex_array<security::kDigestBytes>(
        parts[2U], "person seen entry group");
    auto message_id = parse_hex_array<security::kDigestBytes>(
        parts[3U], "person seen entry message id");
    if (!person) return person.status();
    if (!group) return group.status();
    if (!message_id) return message_id.status();
    entry.person = person.value();
    entry.group = group.value();
    entry.message_id = message_id.value();
    return entry;
}

[[nodiscard]] Result<GroupDescriptor> parse_group_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() < 9U || lines[0U] != kGroupHeader) {
        return Status{ErrorCode::protocol_error,
                      "person group header is invalid"};
    }
    GroupDescriptor group;
    auto id = field(lines[1U], "group-id=", "person group");
    auto creator = field(lines[2U], "creator-person=", "person group");
    auto generation = field(lines[3U], "generation=", "person group");
    auto nonce = field(lines[4U], "group-nonce=", "person group");
    auto title = field(lines[5U], "title-hex=", "person group");
    auto member_count = field(lines[6U], "member-count=", "person group");
    if (!id) return id.status();
    if (!creator) return creator.status();
    if (!generation) return generation.status();
    if (!nonce) return nonce.status();
    if (!title) return title.status();
    if (!member_count) return member_count.status();
    auto group_id =
        parse_hex_array<security::kDigestBytes>(id.value(), "person group id");
    auto creator_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        creator.value(), "person group creator");
    auto generation_value =
        parse_u64_decimal(generation.value(), "person group generation");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(nonce.value(), "person group nonce");
    auto title_bytes = parse_hex_any(title.value(), "person group title");
    auto count =
        parse_u64_decimal(member_count.value(), "person group member count");
    if (!group_id) return group_id.status();
    if (!creator_key) return creator_key.status();
    if (!generation_value) return generation_value.status();
    if (!nonce_value) return nonce_value.status();
    if (!title_bytes) return title_bytes.status();
    if (!count) return count.status();
    if (count.value() > kMaximumGroupMembers) {
        return Status{ErrorCode::protocol_error,
                      "person group member count exceeds bound"};
    }
    if (lines.size() != 8U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person group member count does not match line count"};
    }
    group.group_id = group_id.value();
    group.creator_person = creator_key.value();
    group.generation = generation_value.value();
    group.group_nonce = nonce_value.value();
    group.title = std::move(title_bytes).value();
    group.members.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto member =
            field(lines[7U + index], "member=", "person group");
        if (!member) return member.status();
        auto member_key = parse_hex_array<security::kSigningPublicKeyBytes>(
            member.value(), "person group member");
        if (!member_key) return member_key.status();
        group.members.push_back(member_key.value());
    }
    auto signature_line = field(
        lines.back(), "signature=", "person group");
    if (!signature_line) return signature_line.status();
    auto signature = parse_hex_array<security::kSignatureBytes>(
        signature_line.value(), "person group signature");
    if (!signature) return signature.status();
    group.signature = signature.value();
    return group;
}

[[nodiscard]] Result<GroupMessageEnvelope> parse_group_message_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 7U || lines[0U] != kGroupMessageHeader) {
        return Status{ErrorCode::protocol_error,
                      "person group message header or size is invalid"};
    }
    GroupMessageEnvelope message;
    auto group_id = field(lines[1U], "group-id=", "person group message");
    auto from = field(lines[2U], "from-person=", "person group message");
    auto nonce = field(lines[3U], "nonce=", "person group message");
    auto message_id =
        field(lines[4U], "message-id=", "person group message");
    auto body = field(lines[5U], "body-hex=", "person group message");
    auto signature =
        field(lines[6U], "signature=", "person group message");
    if (!group_id) return group_id.status();
    if (!from) return from.status();
    if (!nonce) return nonce.status();
    if (!message_id) return message_id.status();
    if (!body) return body.status();
    if (!signature) return signature.status();
    auto group = parse_hex_array<security::kDigestBytes>(
        group_id.value(), "person group message group id");
    auto from_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from.value(), "person group message sender");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(nonce.value(),
                                            "person group message nonce");
    auto id = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person group message id");
    auto body_bytes =
        parse_hex_any(body.value(), "person group message body");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person group message signature");
    if (!group) return group.status();
    if (!from_key) return from_key.status();
    if (!nonce_value) return nonce_value.status();
    if (!id) return id.status();
    if (!body_bytes) return body_bytes.status();
    if (!sig) return sig.status();
    message.group_id = group.value();
    message.from_person = from_key.value();
    message.nonce = nonce_value.value();
    message.message_id = id.value();
    message.body = std::move(body_bytes).value();
    message.signature = sig.value();
    return message;
}

[[nodiscard]] Result<GroupDeviceMessageEnvelope>
parse_group_device_message_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 9U || lines[0U] != kGroupDeviceMessageHeader) {
        return Status{ErrorCode::protocol_error,
                      "person group device message header or size is invalid"};
    }
    GroupDeviceMessageEnvelope message;
    auto group_id =
        field(lines[1U], "group-id=", "person group device message");
    auto from_person =
        field(lines[2U], "from-person=", "person group device message");
    auto from_device =
        field(lines[3U], "from-device=", "person group device message");
    auto delegation = field(
        lines[4U], "delegation-digest=", "person group device message");
    auto nonce = field(lines[5U], "nonce=", "person group device message");
    auto message_id =
        field(lines[6U], "message-id=", "person group device message");
    auto body = field(lines[7U], "body-hex=", "person group device message");
    auto signature =
        field(lines[8U], "signature=", "person group device message");
    if (!group_id) return group_id.status();
    if (!from_person) return from_person.status();
    if (!from_device) return from_device.status();
    if (!delegation) return delegation.status();
    if (!nonce) return nonce.status();
    if (!message_id) return message_id.status();
    if (!body) return body.status();
    if (!signature) return signature.status();
    auto group = parse_hex_array<security::kDigestBytes>(
        group_id.value(), "person group device message group id");
    auto from_person_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from_person.value(), "person group device message sender person");
    auto from_device_key = parse_hex_array<security::kSigningPublicKeyBytes>(
        from_device.value(), "person group device message sender device");
    auto delegation_digest = parse_hex_array<security::kDigestBytes>(
        delegation.value(), "person group device message delegation digest");
    auto nonce_value =
        parse_hex_array<kMessageNonceBytes>(
            nonce.value(), "person group device message nonce");
    auto id = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person group device message id");
    auto body_bytes =
        parse_hex_any(body.value(), "person group device message body");
    auto sig = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person group device message signature");
    if (!group) return group.status();
    if (!from_person_key) return from_person_key.status();
    if (!from_device_key) return from_device_key.status();
    if (!delegation_digest) return delegation_digest.status();
    if (!nonce_value) return nonce_value.status();
    if (!id) return id.status();
    if (!body_bytes) return body_bytes.status();
    if (!sig) return sig.status();
    message.group_id = group.value();
    message.from_person = from_person_key.value();
    message.from_device = from_device_key.value();
    message.delegation_digest = delegation_digest.value();
    message.nonce = nonce_value.value();
    message.message_id = id.value();
    message.body = std::move(body_bytes).value();
    message.signature = sig.value();
    return message;
}

}  // namespace

Result<DeliveryCard> delivery_card_from_roster(
    const self_swarm::Roster &roster, const security::Sodium &sodium) {
    auto digest = self_swarm::roster_digest(roster, sodium);
    if (!digest) return digest.status();
    DeliveryCard card;
    card.person = roster.owner;
    card.generation = roster.generation;
    card.roster_digest = digest.value();
    card.routes.reserve(roster.members.size());
    for (const self_swarm::Member &member : roster.members) {
        if (member.status == self_swarm::MemberStatus::active) {
            card.routes.push_back(member.tox_public_key);
        }
    }
    std::sort(card.routes.begin(), card.routes.end());
    card.routes.erase(
        std::unique(card.routes.begin(), card.routes.end()),
        card.routes.end());
    const Status valid = validate_card_shape(card);
    if (!valid.ok()) return valid;
    return card;
}

Result<std::vector<std::uint8_t>> encode_unsigned_delivery_card(
    const DeliveryCard &card) {
    const Status valid = validate_card_shape(card);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kCardHeader << '\n'
           << "person=" << security::hex(card.person) << '\n'
           << "generation=" << card.generation << '\n'
           << "roster-digest=" << security::hex(card.roster_digest) << '\n'
           << "route-count=" << card.routes.size() << '\n';
    for (const DeliveryRouteKey &route : card.routes) {
        output << "route=" << security::hex(route) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> delivery_card_digest(
    const DeliveryCard &card, const security::Sodium &sodium) {
    auto bytes = encode_unsigned_delivery_card(card);
    if (!bytes) return bytes.status();
    return sodium.hash(kCardDigestDomain, bytes.value());
}

Status sign_delivery_card(
    DeliveryCard &card, const security::SigningKeyPair &person_keys,
    const security::Sodium &sodium) {
    if (card.person != person_keys.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "RecallRoot owner does not match person delivery card"};
    }
    auto digest = delivery_card_digest(card, sodium);
    if (!digest) return digest.status();
    auto signature =
        sodium.sign_detached(digest.value(), person_keys.secret_key());
    if (!signature) return signature.status();
    card.signature = signature.value();
    return Status::success();
}

Result<std::vector<std::uint8_t>> encode_signed_delivery_card(
    const DeliveryCard &card) {
    const Status valid = validate_card_shape(card);
    if (!valid.ok()) return valid;
    if (all_zero(card.signature)) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card signature is empty"};
    }
    auto bytes = encode_unsigned_delivery_card(card);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(card.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<DeliveryCard> decode_signed_delivery_card(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person delivery card");
    if (!lines) return lines.status();
    if (lines.value().size() < 6U || lines.value()[0U] != kCardHeader) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card header is invalid"};
    }
    DeliveryCard card;
    auto person_key = field(
        lines.value()[1U], "person=", "person delivery card");
    auto generation = field(
        lines.value()[2U], "generation=", "person delivery card");
    auto roster_digest = field(
        lines.value()[3U], "roster-digest=", "person delivery card");
    auto route_count = field(
        lines.value()[4U], "route-count=", "person delivery card");
    if (!person_key) return person_key.status();
    if (!generation) return generation.status();
    if (!roster_digest) return roster_digest.status();
    if (!route_count) return route_count.status();
    auto person = parse_hex_array<security::kSigningPublicKeyBytes>(
        person_key.value(), "person delivery card person");
    auto generation_value =
        parse_u64_decimal(generation.value(), "person delivery card generation");
    auto roster_digest_value = parse_hex_array<security::kDigestBytes>(
        roster_digest.value(), "person delivery card roster digest");
    auto count = parse_u64_decimal(
        route_count.value(), "person delivery card route count");
    if (!person) return person.status();
    if (!generation_value) return generation_value.status();
    if (!roster_digest_value) return roster_digest_value.status();
    if (!count) return count.status();
    if (count.value() > kMaximumDeliveryRoutes) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card route count exceeds bound"};
    }
    if (lines.value().size() != 6U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card route count does not match line count"};
    }
    card.person = person.value();
    card.generation = generation_value.value();
    card.roster_digest = roster_digest_value.value();
    card.routes.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto route = field(
            lines.value()[5U + index], "route=", "person delivery card");
        if (!route) return route.status();
        auto key = parse_hex_array<security::kSigningPublicKeyBytes>(
            route.value(), "person delivery card route");
        if (!key) return key.status();
        card.routes.push_back(key.value());
    }
    auto signature_line = field(
        lines.value().back(), "signature=", "person delivery card");
    if (!signature_line) return signature_line.status();
    auto signature = parse_hex_array<security::kSignatureBytes>(
        signature_line.value(), "person delivery card signature");
    if (!signature) return signature.status();
    card.signature = signature.value();
    const Status valid = validate_card_shape(card);
    if (!valid.ok()) return valid;

    auto canonical = encode_signed_delivery_card(card);
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card bytes are noncanonical"};
    }
    auto digest = delivery_card_digest(card, sodium);
    if (!digest) return digest.status();
    const Status verified =
        sodium.verify_detached(card.signature, digest.value(), card.person);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card signature is invalid"};
    }
    return card;
}

Result<DeliveryCard> load_delivery_card(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_signed_delivery_card(bytes.value(), sodium);
}

Status write_delivery_card(
    const std::filesystem::path &path, const DeliveryCard &card) {
    auto bytes = encode_signed_delivery_card(card);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status create_delivery_card_file(
    const std::filesystem::path &path, const DeliveryCard &card) {
    std::error_code exists_error;
    if (std::filesystem::exists(path, exists_error)) {
        return Status{ErrorCode::invalid_argument,
                      "person delivery card already exists: " + path.string()};
    }
    if (exists_error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect person delivery card path '" +
                          path.string() + "': " + exists_error.message()};
    }
    return write_delivery_card(path, card);
}

std::string render_delivery_card(const DeliveryCard &card) {
    std::ostringstream output;
    output << "iotox-person-delivery-card-v1\n"
           << "person=" << security::hex(card.person) << '\n'
           << "generation=" << card.generation << '\n'
           << "roster-digest=" << security::hex(card.roster_digest) << '\n'
           << "routes=" << card.routes.size() << '\n';
    for (const DeliveryRouteKey &route : card.routes) {
        output << "route=" << security::hex(route) << '\n';
    }
    output << "signature=valid\n"
           << "route-policy=not-carried-by-person-card\n"
           << "route-policy-authority=route-set-v2-and-explicit-run-config\n"
           << "privacy-fallback=not-authorized-by-card\n"
           << "boundary=public-delivery-card; no-private-aliases-or-authority-principals; tox-routes-are-delivery-not-personhood; route-class-policy-is-separate\n";
    return output.str();
}

Result<security::Digest> compute_message_id(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &to_person,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    auto input = encode_message_id_input(from_person, to_person, nonce, body);
    if (!input) return input.status();
    return sodium.hash(kMessageIdDomain, input.value());
}

Result<MessageEnvelope> create_message_envelope(
    const security::SigningKeyPair &from_person_keys,
    const security::SigningPublicKey &to_person,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    MessageEnvelope message;
    message.from_person = from_person_keys.public_key();
    message.to_person = to_person;
    message.nonce = nonce.value();
    message.body.assign(body.begin(), body.end());
    auto id = compute_message_id(
        message.from_person, message.to_person, message.nonce,
        message.body, sodium);
    if (!id) return id.status();
    message.message_id = id.value();
    const Status valid = validate_message_shape(message, false);
    if (!valid.ok()) return valid;
    auto digest = message_digest(message, sodium);
    if (!digest) return digest.status();
    auto signature =
        sodium.sign_detached(digest.value(), from_person_keys.secret_key());
    if (!signature) return signature.status();
    message.signature = signature.value();
    return message;
}

Result<std::vector<std::uint8_t>> encode_unsigned_message_envelope(
    const MessageEnvelope &message) {
    const Status valid = validate_message_shape(message, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kMessageHeader << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "to-person=" << security::hex(message.to_person) << '\n'
           << "nonce=" << security::hex(message.nonce) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-hex=" << security::hex(message.body) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> message_digest(
    const MessageEnvelope &message, const security::Sodium &sodium) {
    auto bytes = encode_unsigned_message_envelope(message);
    if (!bytes) return bytes.status();
    return sodium.hash(kMessageDigestDomain, bytes.value());
}

Result<std::vector<std::uint8_t>> encode_signed_message_envelope(
    const MessageEnvelope &message) {
    const Status valid = validate_message_shape(message, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_message_envelope(message);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(message.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<MessageEnvelope> decode_signed_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person message");
    if (!lines) return lines.status();
    auto message = parse_message_lines(lines.value());
    if (!message) return message.status();
    const Status valid = validate_message_shape(message.value(), true);
    if (!valid.ok()) return valid;

    auto canonical = encode_signed_message_envelope(message.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person message bytes are noncanonical"};
    }
    auto expected_id = compute_message_id(
        message.value().from_person, message.value().to_person,
        message.value().nonce, message.value().body, sodium);
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != message.value().message_id) {
        return Status{ErrorCode::protocol_error,
                      "person message id does not match envelope contents"};
    }
    auto digest = message_digest(message.value(), sodium);
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        message.value().signature, digest.value(), message.value().from_person);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person message signature is invalid"};
    }
    return message;
}

std::string render_message_envelope(const MessageEnvelope &message) {
    std::ostringstream output;
    output << "iotox-person-message-v1\n"
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "to-person=" << security::hex(message.to_person) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-bytes=" << message.body.size() << '\n'
           << "body-hex=" << security::hex(message.body) << '\n'
           << "signature=valid\n"
           << "boundary=person-signed-envelope; transport-route-is-not-sender-identity\n";
    return output.str();
}

Result<SenderDelegation> sender_delegation_from_roster(
    const self_swarm::Roster &roster, std::string_view alias,
    const security::Sodium &sodium, std::uint64_t expires_unix_ms) {
    auto member = self_swarm::find_member(roster, alias);
    if (!member) return member.status();
    if (member.value().status != self_swarm::MemberStatus::active) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation target is retired"};
    }
    auto digest = self_swarm::roster_digest(roster, sodium);
    if (!digest) return digest.status();
    SenderDelegation delegation;
    delegation.person = roster.owner;
    delegation.device = member.value().principal;
    delegation.generation = roster.generation;
    delegation.roster_digest = digest.value();
    delegation.label = member.value().alias;
    delegation.expires_unix_ms = expires_unix_ms;
    const Status valid = validate_sender_delegation_shape(delegation, false);
    if (!valid.ok()) return valid;
    return delegation;
}

Result<std::vector<std::uint8_t>> encode_unsigned_sender_delegation(
    const SenderDelegation &delegation) {
    const Status valid = validate_sender_delegation_shape(delegation, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kDelegationHeader << '\n'
           << "person=" << security::hex(delegation.person) << '\n'
           << "device=" << security::hex(delegation.device) << '\n'
           << "generation=" << delegation.generation << '\n'
           << "roster-digest=" << security::hex(delegation.roster_digest)
           << '\n'
           << "label=" << delegation.label << '\n'
           << "expires-unix-ms=" << delegation.expires_unix_ms << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> sender_delegation_digest(
    const SenderDelegation &delegation, const security::Sodium &sodium) {
    auto bytes = encode_signed_sender_delegation(delegation);
    if (!bytes) return bytes.status();
    return sodium.hash(kDelegationDigestDomain, bytes.value());
}

Status sign_sender_delegation(
    SenderDelegation &delegation,
    const security::SigningKeyPair &person_keys,
    const security::Sodium &sodium) {
    if (delegation.person != person_keys.public_key()) {
        return Status{ErrorCode::invalid_argument,
                      "RecallRoot owner does not match person sender delegation"};
    }
    auto bytes = encode_unsigned_sender_delegation(delegation);
    if (!bytes) return bytes.status();
    auto digest = sodium.hash(kDelegationDigestDomain, bytes.value());
    if (!digest) return digest.status();
    auto signature =
        sodium.sign_detached(digest.value(), person_keys.secret_key());
    if (!signature) return signature.status();
    delegation.signature = signature.value();
    return Status::success();
}

Result<std::vector<std::uint8_t>> encode_signed_sender_delegation(
    const SenderDelegation &delegation) {
    const Status valid = validate_sender_delegation_shape(delegation, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_sender_delegation(delegation);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(delegation.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<SenderDelegation> decode_signed_sender_delegation(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person sender delegation");
    if (!lines) return lines.status();
    auto delegation = parse_delegation_lines(lines.value());
    if (!delegation) return delegation.status();
    const Status valid =
        validate_sender_delegation_shape(delegation.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_sender_delegation(delegation.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person sender delegation bytes are noncanonical"};
    }
    auto unsigned_bytes = encode_unsigned_sender_delegation(delegation.value());
    if (!unsigned_bytes) return unsigned_bytes.status();
    auto digest = sodium.hash(kDelegationDigestDomain, unsigned_bytes.value());
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        delegation.value().signature, digest.value(),
        delegation.value().person);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person sender delegation signature is invalid"};
    }
    return delegation.value();
}

Result<SenderDelegation> load_sender_delegation(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_signed_sender_delegation(bytes.value(), sodium);
}

Status write_sender_delegation(
    const std::filesystem::path &path, const SenderDelegation &delegation) {
    auto bytes = encode_signed_sender_delegation(delegation);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status create_sender_delegation_file(
    const std::filesystem::path &path, const SenderDelegation &delegation) {
    std::error_code error;
    if (std::filesystem::exists(path, error)) {
        return Status{ErrorCode::invalid_argument,
                      "person sender delegation already exists: " +
                          path.string()};
    }
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect person sender delegation path '" +
                          path.string() + "': " + error.message()};
    }
    return write_sender_delegation(path, delegation);
}

std::string render_sender_delegation(const SenderDelegation &delegation) {
    std::ostringstream output;
    output << "iotox-person-sender-delegation-v1\n"
           << "person=" << security::hex(delegation.person) << '\n'
           << "device=" << security::hex(delegation.device) << '\n'
           << "generation=" << delegation.generation << '\n'
           << "roster-digest=" << security::hex(delegation.roster_digest)
           << '\n'
           << "label=" << delegation.label << '\n'
           << "expires-unix-ms=" << delegation.expires_unix_ms << '\n'
           << "signature=valid\n"
           << "boundary=person-signed-device-sender; daily-chat-does-not-require-recallroot; retirement-needs-new-card-and-delegation-floor\n";
    return output.str();
}

Result<security::Digest> compute_device_message_id(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &from_device,
    const security::SigningPublicKey &to_person,
    const security::Digest &delegation_digest,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    auto input = encode_device_message_id_input(
        from_person, from_device, to_person, delegation_digest, nonce, body);
    if (!input) return input.status();
    return sodium.hash(kDeviceMessageIdDomain, input.value());
}

Result<DeviceMessageEnvelope> create_device_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    const security::SigningPublicKey &to_person,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    if (device_identity.public_key() != delegation.device) {
        return Status{ErrorCode::invalid_argument,
                      "--identity does not match the sender delegation device"};
    }
    auto delegation_digest = sender_delegation_digest(delegation, sodium);
    if (!delegation_digest) return delegation_digest.status();
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    DeviceMessageEnvelope message;
    message.from_person = delegation.person;
    message.from_device = delegation.device;
    message.to_person = to_person;
    message.delegation_digest = delegation_digest.value();
    message.nonce = nonce.value();
    message.body.assign(body.begin(), body.end());
    auto id = compute_device_message_id(
        message.from_person, message.from_device, message.to_person,
        message.delegation_digest, message.nonce, message.body, sodium);
    if (!id) return id.status();
    message.message_id = id.value();
    const Status valid = validate_device_message_shape(message, false);
    if (!valid.ok()) return valid;
    auto digest = device_message_digest(message, sodium);
    if (!digest) return digest.status();
    auto signature = device_identity.sign(digest.value());
    if (!signature) return signature.status();
    message.signature = signature.value();
    return message;
}

Result<std::vector<std::uint8_t>> encode_unsigned_device_message_envelope(
    const DeviceMessageEnvelope &message) {
    const Status valid = validate_device_message_shape(message, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kDeviceMessageHeader << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "from-device=" << security::hex(message.from_device) << '\n'
           << "to-person=" << security::hex(message.to_person) << '\n'
           << "delegation-digest=" << security::hex(message.delegation_digest)
           << '\n'
           << "nonce=" << security::hex(message.nonce) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-hex=" << security::hex(message.body) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> device_message_digest(
    const DeviceMessageEnvelope &message, const security::Sodium &sodium) {
    auto bytes = encode_unsigned_device_message_envelope(message);
    if (!bytes) return bytes.status();
    return sodium.hash(kDeviceMessageDigestDomain, bytes.value());
}

Result<std::vector<std::uint8_t>> encode_signed_device_message_envelope(
    const DeviceMessageEnvelope &message) {
    const Status valid = validate_device_message_shape(message, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_device_message_envelope(message);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(message.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<DeviceMessageEnvelope> decode_signed_device_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person device message");
    if (!lines) return lines.status();
    auto message = parse_device_message_lines(lines.value());
    if (!message) return message.status();
    const Status valid = validate_device_message_shape(message.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_device_message_envelope(message.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person device message bytes are noncanonical"};
    }
    auto expected_id = compute_device_message_id(
        message.value().from_person, message.value().from_device,
        message.value().to_person, message.value().delegation_digest,
        message.value().nonce, message.value().body, sodium);
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != message.value().message_id) {
        return Status{ErrorCode::protocol_error,
                      "person device message id does not match envelope contents"};
    }
    auto digest = device_message_digest(message.value(), sodium);
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        message.value().signature, digest.value(),
        message.value().from_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person device message signature is invalid"};
    }
    return message.value();
}

Status verify_device_message_delegation(
    const DeviceMessageEnvelope &message,
    const SenderDelegation &delegation,
    const security::Sodium &sodium) {
    auto digest = sender_delegation_digest(delegation, sodium);
    if (!digest) return digest.status();
    if (message.delegation_digest != digest.value() ||
        message.from_person != delegation.person ||
        message.from_device != delegation.device) {
        return Status{ErrorCode::protocol_error,
                      "person device message does not match sender delegation"};
    }
    return Status::success();
}

std::string render_device_message_envelope(
    const DeviceMessageEnvelope &message) {
    std::ostringstream output;
    output << "iotox-person-device-message-v1\n"
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "from-device=" << security::hex(message.from_device) << '\n'
           << "to-person=" << security::hex(message.to_person) << '\n'
           << "delegation-digest=" << security::hex(message.delegation_digest)
           << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-bytes=" << message.body.size() << '\n'
           << "body-hex=" << security::hex(message.body) << '\n'
           << "signature=valid\n"
           << "boundary=device-signed-envelope-authorized-by-person-delegation; transport-route-is-not-speaker-identity\n";
    return output.str();
}

Result<security::Digest> compute_tox_bridge_message_id(
    std::string_view direction,
    std::string_view tox_kind,
    const security::SigningPublicKey &observer_person,
    const security::SigningPublicKey &observer_device,
    const security::Digest &delegation_digest,
    const ToxPublicKey &external_tox_key,
    std::uint64_t observed_unix_ms,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    auto input = encode_tox_bridge_message_id_input(
        direction, tox_kind, observer_person, observer_device,
        delegation_digest, external_tox_key, observed_unix_ms, nonce, body);
    if (!input) return input.status();
    return sodium.hash(kToxBridgeMessageIdDomain, input.value());
}

Result<ToxBridgeMessageEnvelope> create_tox_bridge_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    std::string_view direction,
    std::string_view tox_kind,
    const ToxPublicKey &external_tox_key,
    std::span<const std::uint8_t> body,
    std::uint64_t observed_unix_ms,
    const security::Sodium &sodium) {
    if (device_identity.public_key() != delegation.device) {
        return Status{ErrorCode::invalid_argument,
                      "--identity does not match the Tox bridge delegation device"};
    }
    auto delegation_digest = sender_delegation_digest(delegation, sodium);
    if (!delegation_digest) return delegation_digest.status();
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    ToxBridgeMessageEnvelope message;
    message.direction = std::string(direction);
    message.tox_kind = std::string(tox_kind);
    message.observer_person = delegation.person;
    message.observer_device = delegation.device;
    message.delegation_digest = delegation_digest.value();
    message.external_tox_key = external_tox_key;
    message.observed_unix_ms = observed_unix_ms;
    message.nonce = nonce.value();
    message.body.assign(body.begin(), body.end());
    auto id = compute_tox_bridge_message_id(
        message.direction, message.tox_kind, message.observer_person,
        message.observer_device, message.delegation_digest,
        message.external_tox_key, message.observed_unix_ms, message.nonce,
        message.body, sodium);
    if (!id) return id.status();
    message.message_id = id.value();
    const Status valid = validate_tox_bridge_message_shape(message, false);
    if (!valid.ok()) return valid;
    auto digest = tox_bridge_message_digest(message, sodium);
    if (!digest) return digest.status();
    auto signature = device_identity.sign(digest.value());
    if (!signature) return signature.status();
    message.signature = signature.value();
    return message;
}

Result<std::vector<std::uint8_t>>
encode_unsigned_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message) {
    const Status valid = validate_tox_bridge_message_shape(message, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kToxBridgeMessageHeader << '\n'
           << "direction=" << message.direction << '\n'
           << "tox-kind=" << message.tox_kind << '\n'
           << "observer-person=" << security::hex(message.observer_person)
           << '\n'
           << "observer-device=" << security::hex(message.observer_device)
           << '\n'
           << "delegation-digest="
           << security::hex(message.delegation_digest) << '\n'
           << "external-tox-key=" << security::hex(message.external_tox_key)
           << '\n'
           << "observed-unix-ms=" << message.observed_unix_ms << '\n'
           << "nonce=" << security::hex(message.nonce) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-hex=" << security::hex(message.body) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> tox_bridge_message_digest(
    const ToxBridgeMessageEnvelope &message,
    const security::Sodium &sodium) {
    auto bytes = encode_unsigned_tox_bridge_message_envelope(message);
    if (!bytes) return bytes.status();
    return sodium.hash(kToxBridgeMessageDigestDomain, bytes.value());
}

Result<std::vector<std::uint8_t>>
encode_signed_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message) {
    const Status valid = validate_tox_bridge_message_shape(message, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_tox_bridge_message_envelope(message);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(message.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<ToxBridgeMessageEnvelope>
decode_signed_tox_bridge_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person Tox bridge message");
    if (!lines) return lines.status();
    auto message = parse_tox_bridge_message_lines(lines.value());
    if (!message) return message.status();
    const Status valid =
        validate_tox_bridge_message_shape(message.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_tox_bridge_message_envelope(message.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge message bytes are noncanonical"};
    }
    auto expected_id = compute_tox_bridge_message_id(
        message.value().direction, message.value().tox_kind,
        message.value().observer_person, message.value().observer_device,
        message.value().delegation_digest, message.value().external_tox_key,
        message.value().observed_unix_ms, message.value().nonce,
        message.value().body, sodium);
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != message.value().message_id) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge message id does not match envelope contents"};
    }
    auto digest = tox_bridge_message_digest(message.value(), sodium);
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        message.value().signature, digest.value(),
        message.value().observer_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge message signature is invalid"};
    }
    return message.value();
}

Status verify_tox_bridge_message_delegation(
    const ToxBridgeMessageEnvelope &message,
    const SenderDelegation &delegation,
    const security::Sodium &sodium) {
    auto digest = sender_delegation_digest(delegation, sodium);
    if (!digest) return digest.status();
    if (message.delegation_digest != digest.value() ||
        message.observer_person != delegation.person ||
        message.observer_device != delegation.device) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge message does not match sender delegation"};
    }
    return Status::success();
}

std::string render_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message) {
    std::ostringstream output;
    output << "iotox-person-tox-bridge-message-v1\n"
           << "direction=" << message.direction << '\n'
           << "tox-kind=" << message.tox_kind << '\n'
           << "observer-person=" << security::hex(message.observer_person)
           << '\n'
           << "observer-device=" << security::hex(message.observer_device)
           << '\n'
           << "external-tox-key=" << security::hex(message.external_tox_key)
           << '\n'
           << "observed-unix-ms=" << message.observed_unix_ms << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-bytes=" << message.body.size() << '\n'
           << "body-hex=" << security::hex(message.body) << '\n'
           << "signature=valid\n"
           << "boundary=normal-tox-edge-compatibility; external-tox-key-is-not-iotox-person-identity\n";
    return output.str();
}

Result<CardFloor> card_floor_from_card(
    const DeliveryCard &card, const security::Sodium &sodium) {
    auto digest = delivery_card_digest(card, sodium);
    if (!digest) return digest.status();
    CardFloor floor;
    floor.person = card.person;
    floor.generation = card.generation;
    floor.digest = digest.value();
    const Status valid = validate_card_floor_shape(floor);
    if (!valid.ok()) return valid;
    return floor;
}

Status check_card_floor(
    const DeliveryCard &card, const CardFloor &floor,
    const security::Sodium &sodium) {
    auto current = card_floor_from_card(card, sodium);
    if (!current) return current.status();
    if (current.value().person != floor.person) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card person is not the durable floor person"};
    }
    if (current.value().generation < floor.generation) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card generation is below the durable floor"};
    }
    if (current.value().generation == floor.generation &&
        current.value().digest != floor.digest) {
        return Status{ErrorCode::protocol_error,
                      "person delivery card conflicts with the durable floor digest"};
    }
    return Status::success();
}

namespace {

Result<std::vector<std::uint8_t>> encode_card_floor_bytes(
    const CardFloor &floor) {
    const Status valid = validate_card_floor_shape(floor);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kCardFloorHeader << '\n'
           << "person=" << security::hex(floor.person) << '\n'
           << "generation=" << floor.generation << '\n'
           << "digest=" << security::hex(floor.digest) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<SeenStore> decode_seen_store_bytes(std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes, "person seen store");
    if (!lines) return lines.status();
    if (lines.value().size() < 2U || lines.value()[0U] != kSeenHeader) {
        return Status{ErrorCode::protocol_error,
                      "person seen store header is invalid"};
    }
    auto count_field =
        field(lines.value()[1U], "entry-count=", "person seen store");
    if (!count_field) return count_field.status();
    auto count =
        parse_u64_decimal(count_field.value(), "person seen entry count");
    if (!count) return count.status();
    if (count.value() > kMaximumSeenEntries ||
        lines.value().size() != 2U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person seen store entry count is invalid"};
    }
    SeenStore store;
    store.entries.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto entry = parse_seen_entry(lines.value()[2U + index]);
        if (!entry) return entry.status();
        store.entries.push_back(std::move(entry).value());
    }
    const Status valid = validate_seen_store_shape(store);
    if (!valid.ok()) return valid;
    return store;
}

Result<std::vector<std::uint8_t>> encode_seen_store_bytes(
    const SeenStore &store) {
    const Status valid = validate_seen_store_shape(store);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kSeenHeader << '\n'
           << "entry-count=" << store.entries.size() << '\n';
    for (const SeenEntry &entry : store.entries) {
        output << "entry=" << entry.scope << '|'
               << security::hex(entry.person) << '|'
               << security::hex(entry.group) << '|'
               << security::hex(entry.message_id) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

bool group_has_member(
    const GroupDescriptor &group,
    const security::SigningPublicKey &person) {
    return std::binary_search(group.members.begin(), group.members.end(), person);
}

std::string encode_routes_csv(const std::vector<DeliveryRouteKey> &routes) {
    std::ostringstream output;
    for (std::size_t index = 0U; index < routes.size(); ++index) {
        if (index != 0U) output << ',';
        output << security::hex(routes[index]);
    }
    return output.str();
}

Result<std::vector<DeliveryRouteKey>> parse_routes_csv(
    std::string_view text, std::string_view label) {
    if (text.empty()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " route list is empty"};
    }
    std::vector<DeliveryRouteKey> routes;
    for (std::string_view part : split_delimited(text, ',')) {
        auto route = parse_hex_array<security::kSigningPublicKeyBytes>(
            part, std::string(label) + " route");
        if (!route) return route.status();
        routes.push_back(route.value());
    }
    std::sort(routes.begin(), routes.end());
    routes.erase(std::unique(routes.begin(), routes.end()), routes.end());
    if (routes.empty() || routes.size() > kMaximumDeliveryRoutes) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " route count is invalid"};
    }
    return routes;
}

Result<ContactEntry> parse_contact_line(std::string_view line) {
    auto payload = field(line, "contact=", "person contact book");
    if (!payload) return payload.status();
    const auto parts = split_delimited(payload.value(), '|');
    if (parts.size() != 5U) {
        return Status{ErrorCode::protocol_error,
                      "person contact line must have five fields"};
    }
    ContactEntry entry;
    entry.name = std::string(parts[0U]);
    auto person = parse_hex_array<security::kSigningPublicKeyBytes>(
        parts[1U], "person contact person");
    auto generation =
        parse_u64_decimal(parts[2U], "person contact generation");
    auto digest = parse_hex_array<security::kDigestBytes>(
        parts[3U], "person contact card digest");
    auto routes = parse_routes_csv(parts[4U], "person contact");
    if (!person) return person.status();
    if (!generation) return generation.status();
    if (!digest) return digest.status();
    if (!routes) return routes.status();
    entry.person = person.value();
    entry.generation = generation.value();
    entry.card_digest = digest.value();
    entry.routes = std::move(routes).value();
    const Status valid = validate_contact_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<ContactBook> decode_contact_book_bytes(
    std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes, "person contact book");
    if (!lines) return lines.status();
    if (lines.value().size() < 2U || lines.value()[0U] != kContactBookHeader) {
        return Status{ErrorCode::protocol_error,
                      "person contact book header is invalid"};
    }
    auto count_field =
        field(lines.value()[1U], "contact-count=", "person contact book");
    if (!count_field) return count_field.status();
    auto count = parse_u64_decimal(
        count_field.value(), "person contact count");
    if (!count) return count.status();
    if (count.value() > kMaximumContacts ||
        lines.value().size() != 2U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person contact count is invalid"};
    }
    ContactBook book;
    book.contacts.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto contact = parse_contact_line(lines.value()[2U + index]);
        if (!contact) return contact.status();
        book.contacts.push_back(std::move(contact).value());
    }
    const Status valid = validate_contact_book_shape(book);
    if (!valid.ok()) return valid;
    return book;
}

Result<std::vector<std::uint8_t>> encode_contact_book_bytes(
    const ContactBook &book) {
    const Status valid = validate_contact_book_shape(book);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kContactBookHeader << '\n'
           << "contact-count=" << book.contacts.size() << '\n';
    for (const ContactEntry &entry : book.contacts) {
        output << "contact=" << entry.name << '|'
               << security::hex(entry.person) << '|'
               << entry.generation << '|'
               << security::hex(entry.card_digest) << '|'
               << encode_routes_csv(entry.routes) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<TranscriptEntry> parse_transcript_line(std::string_view line) {
    auto payload = field(line, "entry=", "person transcript");
    if (!payload) return payload.status();
    const auto parts = split_delimited(payload.value(), '|');
    if (parts.size() != 9U) {
        return Status{ErrorCode::protocol_error,
                      "person transcript entry must have nine fields"};
    }
    TranscriptEntry entry;
    auto sequence =
        parse_u64_decimal(parts[0U], "person transcript sequence");
    auto from = parse_hex_array<security::kSigningPublicKeyBytes>(
        parts[3U], "person transcript sender");
    auto to = parse_hex_array<security::kSigningPublicKeyBytes>(
        parts[4U], "person transcript recipient");
    auto group =
        parse_hex_array<security::kDigestBytes>(parts[5U],
                                                "person transcript group");
    auto message_id =
        parse_hex_array<security::kDigestBytes>(parts[6U],
                                                "person transcript message id");
    auto payload_digest =
        parse_hex_array<security::kDigestBytes>(
            parts[7U], "person transcript payload digest");
    auto body = parse_hex_any(parts[8U], "person transcript body");
    if (!sequence) return sequence.status();
    if (!from) return from.status();
    if (!to) return to.status();
    if (!group) return group.status();
    if (!message_id) return message_id.status();
    if (!payload_digest) return payload_digest.status();
    if (!body) return body.status();
    entry.sequence = sequence.value();
    entry.direction = std::string(parts[1U]);
    entry.scope = std::string(parts[2U]);
    entry.from_person = from.value();
    entry.to_person = to.value();
    entry.group = group.value();
    entry.message_id = message_id.value();
    entry.payload_digest = payload_digest.value();
    entry.body = std::move(body).value();
    const Status valid = validate_transcript_entry(entry, true);
    if (!valid.ok()) return valid;
    return entry;
}

Result<TranscriptStore> decode_transcript_store_bytes(
    std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes, "person transcript");
    if (!lines) return lines.status();
    if (lines.value().size() < 3U || lines.value()[0U] != kTranscriptHeader) {
        return Status{ErrorCode::protocol_error,
                      "person transcript header is invalid"};
    }
    auto next_field =
        field(lines.value()[1U], "next-sequence=", "person transcript");
    auto count_field =
        field(lines.value()[2U], "entry-count=", "person transcript");
    if (!next_field) return next_field.status();
    if (!count_field) return count_field.status();
    auto next =
        parse_u64_decimal(next_field.value(), "person transcript next sequence");
    auto count =
        parse_u64_decimal(count_field.value(), "person transcript entry count");
    if (!next) return next.status();
    if (!count) return count.status();
    if (count.value() > kMaximumTranscriptEntries ||
        lines.value().size() != 3U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person transcript entry count is invalid"};
    }
    TranscriptStore store;
    store.next_sequence = next.value();
    store.entries.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto entry = parse_transcript_line(lines.value()[3U + index]);
        if (!entry) return entry.status();
        store.entries.push_back(std::move(entry).value());
    }
    const Status valid = validate_transcript_store_shape(store);
    if (!valid.ok()) return valid;
    return store;
}

Result<std::vector<std::uint8_t>> encode_transcript_store_bytes(
    const TranscriptStore &store) {
    const Status valid = validate_transcript_store_shape(store);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kTranscriptHeader << '\n'
           << "next-sequence=" << store.next_sequence << '\n'
           << "entry-count=" << store.entries.size() << '\n';
    for (const TranscriptEntry &entry : store.entries) {
        output << "entry=" << entry.sequence << '|'
               << entry.direction << '|'
               << entry.scope << '|'
               << security::hex(entry.from_person) << '|'
               << security::hex(entry.to_person) << '|'
               << security::hex(entry.group) << '|'
               << security::hex(entry.message_id) << '|'
               << security::hex(entry.payload_digest) << '|'
               << security::hex(entry.body) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<ToxBridgeEntry> parse_tox_bridge_entry_line(std::string_view line) {
    auto payload = field(line, "entry=", "person Tox bridge store");
    if (!payload) return payload.status();
    const auto parts = split_delimited(payload.value(), '|');
    if (parts.size() != 10U) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge entry must have ten fields"};
    }
    ToxBridgeEntry entry;
    auto sequence =
        parse_u64_decimal(parts[0U], "person Tox bridge sequence");
    auto observer_person =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            parts[3U], "person Tox bridge observer person");
    auto observer_device =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            parts[4U], "person Tox bridge observer device");
    auto external = parse_hex_array<kToxPublicKeyBytes>(
        parts[5U], "person Tox bridge external Tox key");
    auto observed =
        parse_u64_decimal(parts[6U], "person Tox bridge observed-unix-ms");
    auto message_id =
        parse_hex_array<security::kDigestBytes>(
            parts[7U], "person Tox bridge message id");
    auto payload_digest =
        parse_hex_array<security::kDigestBytes>(
            parts[8U], "person Tox bridge payload digest");
    auto body = parse_hex_any(parts[9U], "person Tox bridge body");
    if (!sequence) return sequence.status();
    if (!observer_person) return observer_person.status();
    if (!observer_device) return observer_device.status();
    if (!external) return external.status();
    if (!observed) return observed.status();
    if (!message_id) return message_id.status();
    if (!payload_digest) return payload_digest.status();
    if (!body) return body.status();
    entry.sequence = sequence.value();
    entry.direction = std::string(parts[1U]);
    entry.tox_kind = std::string(parts[2U]);
    entry.observer_person = observer_person.value();
    entry.observer_device = observer_device.value();
    entry.external_tox_key = external.value();
    entry.observed_unix_ms = observed.value();
    entry.message_id = message_id.value();
    entry.payload_digest = payload_digest.value();
    entry.body = std::move(body).value();
    const Status valid = validate_tox_bridge_entry(entry, true);
    if (!valid.ok()) return valid;
    return entry;
}

Result<ToxBridgeStore> decode_tox_bridge_store_bytes(
    std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes, "person Tox bridge store");
    if (!lines) return lines.status();
    if (lines.value().size() < 3U ||
        lines.value()[0U] != kToxBridgeStoreHeader) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge store header is invalid"};
    }
    auto next_field =
        field(lines.value()[1U], "next-sequence=", "person Tox bridge store");
    auto count_field =
        field(lines.value()[2U], "entry-count=", "person Tox bridge store");
    if (!next_field) return next_field.status();
    if (!count_field) return count_field.status();
    auto next = parse_u64_decimal(
        next_field.value(), "person Tox bridge next sequence");
    auto count = parse_u64_decimal(
        count_field.value(), "person Tox bridge entry count");
    if (!next) return next.status();
    if (!count) return count.status();
    if (count.value() > kMaximumToxBridgeEntries ||
        lines.value().size() != 3U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge entry count is invalid"};
    }
    ToxBridgeStore store;
    store.next_sequence = next.value();
    store.entries.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto entry = parse_tox_bridge_entry_line(lines.value()[3U + index]);
        if (!entry) return entry.status();
        store.entries.push_back(std::move(entry).value());
    }
    const Status valid = validate_tox_bridge_store_shape(store);
    if (!valid.ok()) return valid;
    return store;
}

Result<std::vector<std::uint8_t>> encode_tox_bridge_store_bytes(
    const ToxBridgeStore &store) {
    const Status valid = validate_tox_bridge_store_shape(store);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kToxBridgeStoreHeader << '\n'
           << "next-sequence=" << store.next_sequence << '\n'
           << "entry-count=" << store.entries.size() << '\n';
    for (const ToxBridgeEntry &entry : store.entries) {
        output << "entry=" << entry.sequence << '|'
               << entry.direction << '|'
               << entry.tox_kind << '|'
               << security::hex(entry.observer_person) << '|'
               << security::hex(entry.observer_device) << '|'
               << security::hex(entry.external_tox_key) << '|'
               << entry.observed_unix_ms << '|'
               << security::hex(entry.message_id) << '|'
               << security::hex(entry.payload_digest) << '|'
               << security::hex(entry.body) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<ReceiptRecord> parse_receipt_lines(
    const std::vector<std::string_view> &lines) {
    if (lines.size() != 9U || lines[0U] != kReceiptHeader) {
        return Status{ErrorCode::protocol_error,
                      "person receipt header or size is invalid"};
    }
    ReceiptRecord receipt;
    auto scope = field(lines[1U], "scope=", "person receipt");
    auto message_id = field(lines[2U], "message-id=", "person receipt");
    auto group = field(lines[3U], "group=", "person receipt");
    auto recipient_person =
        field(lines[4U], "recipient-person=", "person receipt");
    auto recipient_device =
        field(lines[5U], "recipient-device=", "person receipt");
    auto delegation =
        field(lines[6U], "delegation-digest=", "person receipt");
    auto received =
        field(lines[7U], "received-unix-ms=", "person receipt");
    auto signature = field(lines[8U], "signature=", "person receipt");
    if (!scope) return scope.status();
    if (!message_id) return message_id.status();
    if (!group) return group.status();
    if (!recipient_person) return recipient_person.status();
    if (!recipient_device) return recipient_device.status();
    if (!delegation) return delegation.status();
    if (!received) return received.status();
    if (!signature) return signature.status();
    auto message_id_value = parse_hex_array<security::kDigestBytes>(
        message_id.value(), "person receipt message id");
    auto group_value = parse_hex_array<security::kDigestBytes>(
        group.value(), "person receipt group");
    auto recipient_person_value =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            recipient_person.value(), "person receipt recipient person");
    auto recipient_device_value =
        parse_hex_array<security::kSigningPublicKeyBytes>(
            recipient_device.value(), "person receipt recipient device");
    auto delegation_value = parse_hex_array<security::kDigestBytes>(
        delegation.value(), "person receipt delegation digest");
    auto received_value =
        parse_u64_decimal(received.value(), "person receipt received time");
    auto signature_value = parse_hex_array<security::kSignatureBytes>(
        signature.value(), "person receipt signature");
    if (!message_id_value) return message_id_value.status();
    if (!group_value) return group_value.status();
    if (!recipient_person_value) return recipient_person_value.status();
    if (!recipient_device_value) return recipient_device_value.status();
    if (!delegation_value) return delegation_value.status();
    if (!received_value) return received_value.status();
    if (!signature_value) return signature_value.status();
    receipt.scope = std::string(scope.value());
    receipt.message_id = message_id_value.value();
    receipt.group = group_value.value();
    receipt.recipient_person = recipient_person_value.value();
    receipt.recipient_device = recipient_device_value.value();
    receipt.delegation_digest = delegation_value.value();
    receipt.received_unix_ms = received_value.value();
    receipt.signature = signature_value.value();
    return receipt;
}

Result<ReceiptStore> decode_receipt_store_bytes(
    std::span<const std::uint8_t> bytes,
    const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person receipt store");
    if (!lines) return lines.status();
    if (lines.value().size() < 2U ||
        lines.value()[0U] != kReceiptStoreHeader) {
        return Status{ErrorCode::protocol_error,
                      "person receipt store header is invalid"};
    }
    auto count_field =
        field(lines.value()[1U], "receipt-count=", "person receipt store");
    if (!count_field) return count_field.status();
    auto count = parse_u64_decimal(
        count_field.value(), "person receipt store receipt count");
    if (!count) return count.status();
    if (count.value() > kMaximumReceiptRecords ||
        lines.value().size() != 2U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person receipt store receipt count is invalid"};
    }
    ReceiptStore store;
    store.receipts.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto encoded =
            field(lines.value()[2U + index], "receipt=", "person receipt store");
        if (!encoded) return encoded.status();
        auto receipt_bytes =
            parse_hex_any(encoded.value(), "person receipt store receipt");
        if (!receipt_bytes) return receipt_bytes.status();
        auto receipt = decode_signed_receipt_record(
            receipt_bytes.value(), sodium);
        if (!receipt) return receipt.status();
        store.receipts.push_back(std::move(receipt).value());
    }
    const Status valid = validate_receipt_store_shape(store);
    if (!valid.ok()) return valid;
    return store;
}

Result<std::vector<std::uint8_t>> encode_receipt_store_bytes(
    const ReceiptStore &store) {
    const Status valid = validate_receipt_store_shape(store);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kReceiptStoreHeader << '\n'
           << "receipt-count=" << store.receipts.size() << '\n';
    for (const ReceiptRecord &receipt : store.receipts) {
        auto encoded = encode_signed_receipt_record(receipt);
        if (!encoded) return encoded.status();
        output << "receipt=" << security::hex(encoded.value()) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<OutboxItem> parse_outbox_line(std::string_view line) {
    auto payload = field(line, "item=", "person outbox");
    if (!payload) return payload.status();
    const auto parts = split_delimited(payload.value(), '|');
    if (parts.size() != 8U && parts.size() != 11U) {
        return Status{ErrorCode::protocol_error,
                      "person outbox item must have eight or eleven fields"};
    }
    OutboxItem item;
    auto message_id = parse_hex_array<security::kDigestBytes>(
        parts[0U], "person outbox message id");
    auto recipient = parse_hex_array<security::kSigningPublicKeyBytes>(
        parts[1U], "person outbox recipient");
    auto generation =
        parse_u64_decimal(parts[2U], "person outbox card generation");
    auto card_digest = parse_hex_array<security::kDigestBytes>(
        parts[3U], "person outbox card digest");
    auto payload_digest = parse_hex_array<security::kDigestBytes>(
        parts[4U], "person outbox payload digest");
    auto payload_bytes = parse_hex_any(parts[5U], "person outbox payload");
    std::vector<DeliveryRouteKey> pending_routes;
    if (!parts[6U].empty()) {
        auto pending = parse_routes_csv(parts[6U], "person outbox pending");
        if (!pending) return pending.status();
        pending_routes = std::move(pending).value();
    }
    std::vector<DeliveryRouteKey> sent_routes;
    if (!parts[7U].empty()) {
        auto sent = parse_routes_csv(parts[7U], "person outbox sent");
        if (!sent) return sent.status();
        sent_routes = std::move(sent).value();
    }
    if (!message_id) return message_id.status();
    if (!recipient) return recipient.status();
    if (!generation) return generation.status();
    if (!card_digest) return card_digest.status();
    if (!payload_digest) return payload_digest.status();
    if (!payload_bytes) return payload_bytes.status();
    item.message_id = message_id.value();
    item.recipient_person = recipient.value();
    item.card_generation = generation.value();
    item.card_digest = card_digest.value();
    item.payload_digest = payload_digest.value();
    item.payload = std::move(payload_bytes).value();
    item.pending_routes = std::move(pending_routes);
    item.sent_routes = std::move(sent_routes);
    if (parts.size() == 11U) {
        auto created =
            parse_u64_decimal(parts[8U], "person outbox created time");
        auto last_attempt =
            parse_u64_decimal(parts[9U], "person outbox last attempt time");
        auto attempts =
            parse_u64_decimal(parts[10U], "person outbox attempts");
        if (!created) return created.status();
        if (!last_attempt) return last_attempt.status();
        if (!attempts) return attempts.status();
        item.created_unix_ms = created.value();
        item.last_attempt_unix_ms = last_attempt.value();
        item.attempts = attempts.value();
    }
    const Status valid = validate_outbox_item(item);
    if (!valid.ok()) return valid;
    return item;
}

Result<OutboxStore> decode_outbox_store_bytes(
    std::span<const std::uint8_t> bytes) {
    auto lines = split_lines(bytes, "person outbox");
    if (!lines) return lines.status();
    if (lines.value().size() < 2U || lines.value()[0U] != kOutboxHeader) {
        return Status{ErrorCode::protocol_error,
                      "person outbox header is invalid"};
    }
    auto count_field =
        field(lines.value()[1U], "item-count=", "person outbox");
    if (!count_field) return count_field.status();
    auto count = parse_u64_decimal(
        count_field.value(), "person outbox item count");
    if (!count) return count.status();
    if (count.value() > kMaximumOutboxItems ||
        lines.value().size() != 2U + count.value()) {
        return Status{ErrorCode::protocol_error,
                      "person outbox item count is invalid"};
    }
    OutboxStore store;
    store.items.reserve(static_cast<std::size_t>(count.value()));
    for (std::size_t index = 0U; index < count.value(); ++index) {
        auto item = parse_outbox_line(lines.value()[2U + index]);
        if (!item) return item.status();
        store.items.push_back(std::move(item).value());
    }
    const Status valid = validate_outbox_store_shape(store);
    if (!valid.ok()) return valid;
    return store;
}

Result<std::vector<std::uint8_t>> encode_outbox_store_bytes(
    const OutboxStore &store) {
    const Status valid = validate_outbox_store_shape(store);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kOutboxHeader << '\n'
           << "item-count=" << store.items.size() << '\n';
    for (const OutboxItem &item : store.items) {
        output << "item=" << security::hex(item.message_id) << '|'
               << security::hex(item.recipient_person) << '|'
               << item.card_generation << '|'
               << security::hex(item.card_digest) << '|'
               << security::hex(item.payload_digest) << '|'
               << security::hex(item.payload) << '|'
               << encode_routes_csv(item.pending_routes) << '|'
               << encode_routes_csv(item.sent_routes);
        if (item.created_unix_ms != 0U ||
            item.last_attempt_unix_ms != 0U ||
            item.attempts != 0U) {
            output << '|' << item.created_unix_ms
                   << '|' << item.last_attempt_unix_ms
                   << '|' << item.attempts;
        }
        output << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

}  // namespace

Result<CardFloor> load_card_floor(const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto lines = split_lines(bytes.value(), "person card floor");
    if (!lines) return lines.status();
    auto floor = parse_card_floor_lines(lines.value());
    if (!floor) return floor.status();
    auto canonical = encode_card_floor_bytes(floor.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person card floor bytes are noncanonical"};
    }
    return floor.value();
}

Status write_card_floor(
    const std::filesystem::path &path, const CardFloor &floor) {
    auto bytes = encode_card_floor_bytes(floor);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<CardFloor> commit_card_floor(
    const std::filesystem::path &path, const DeliveryCard &card,
    const security::Sodium &sodium) {
    auto next = card_floor_from_card(card, sodium);
    if (!next) return next.status();
    auto current = load_card_floor(path);
    if (current) {
        if (current.value().person != next.value().person) {
            return Status{ErrorCode::protocol_error,
                          "person card floor person does not match card person"};
        }
        if (next.value().generation < current.value().generation) {
            return Status{ErrorCode::protocol_error,
                          "person delivery card generation is below the durable floor"};
        }
        if (next.value().generation == current.value().generation &&
            next.value().digest != current.value().digest) {
            return Status{ErrorCode::protocol_error,
                          "person delivery card conflicts with the durable floor digest"};
        }
        if (next.value().generation == current.value().generation) {
            return current.value();
        }
    } else if (current.status().code() != ErrorCode::not_found) {
        return current.status();
    }
    const Status written = write_card_floor(path, next.value());
    if (!written.ok()) return written;
    return next.value();
}

std::string render_card_floor(const CardFloor &floor) {
    std::ostringstream output;
    output << "iotox-person-card-floor-v1\n"
           << "person=" << security::hex(floor.person) << '\n'
           << "generation=" << floor.generation << '\n'
           << "digest=" << security::hex(floor.digest) << '\n'
           << "boundary=contact-side-delivery-card-high-water; rejects-stale-and-same-generation-forks\n";
    return output.str();
}

Result<SeenEntry> seen_entry_for_message(const MessageEnvelope &message) {
    SeenEntry entry;
    entry.scope = "person";
    entry.person = message.from_person;
    entry.group.fill(0U);
    entry.message_id = message.message_id;
    const Status valid = validate_seen_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<SeenEntry> seen_entry_for_message(
    const DeviceMessageEnvelope &message) {
    SeenEntry entry;
    entry.scope = "person";
    entry.person = message.from_person;
    entry.group.fill(0U);
    entry.message_id = message.message_id;
    const Status valid = validate_seen_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<SeenEntry> seen_entry_for_message(const GroupMessageEnvelope &message) {
    SeenEntry entry;
    entry.scope = "group";
    entry.person = message.from_person;
    entry.group = message.group_id;
    entry.message_id = message.message_id;
    const Status valid = validate_seen_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<SeenEntry> seen_entry_for_message(
    const GroupDeviceMessageEnvelope &message) {
    SeenEntry entry;
    entry.scope = "group";
    entry.person = message.from_person;
    entry.group = message.group_id;
    entry.message_id = message.message_id;
    const Status valid = validate_seen_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<SeenStore> load_seen_store(const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_seen_store_bytes(bytes.value());
}

Status write_seen_store(
    const std::filesystem::path &path, const SeenStore &store) {
    auto bytes = encode_seen_store_bytes(store);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<SeenCommit> commit_seen_entry(
    const std::filesystem::path &path, const SeenEntry &entry) {
    const Status entry_valid = validate_seen_entry(entry);
    if (!entry_valid.ok()) return entry_valid;
    SeenStore store;
    auto loaded = load_seen_store(path);
    if (loaded) {
        store = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    const auto found = std::lower_bound(
        store.entries.begin(), store.entries.end(), entry, seen_entry_less);
    if (found != store.entries.end() && *found == entry) {
        return SeenCommit{entry, true, store.entries.size()};
    }
    if (store.entries.size() >= kMaximumSeenEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person seen store is full"};
    }
    store.entries.insert(found, entry);
    const Status written = write_seen_store(path, store);
    if (!written.ok()) return written;
    return SeenCommit{entry, false, store.entries.size()};
}

std::string render_seen_store(const SeenStore &store) {
    std::ostringstream output;
    output << "iotox-person-seen-v1\n"
           << "entries=" << store.entries.size() << '\n';
    for (const SeenEntry &entry : store.entries) {
        output << "entry scope=" << entry.scope
               << " person=" << security::hex(entry.person);
        if (entry.scope == "group") {
            output << " group=" << security::hex(entry.group);
        }
        output << " message-id=" << security::hex(entry.message_id) << '\n';
    }
    output << "boundary=local-duplicate-suppression-only; not-a-delivery-receipt-or-transcript-authority\n";
    return output.str();
}

Result<security::Digest> compute_group_id(
    const GroupDescriptor &group, const security::Sodium &sodium) {
    auto input = encode_group_id_input(group);
    if (!input) return input.status();
    return sodium.hash(kGroupIdDomain, input.value());
}

Result<GroupDescriptor> create_group_descriptor(
    const security::SigningKeyPair &creator_person_keys,
    std::span<const std::uint8_t> title,
    std::vector<security::SigningPublicKey> members,
    const security::Sodium &sodium) {
    if (title.empty() || title.size() > kMaximumGroupTitleBytes) {
        return Status{ErrorCode::invalid_argument,
                      "person group title must contain 1..120 bytes"};
    }
    members.push_back(creator_person_keys.public_key());
    std::sort(members.begin(), members.end());
    members.erase(std::unique(members.begin(), members.end()), members.end());
    if (members.size() > kMaximumGroupMembers) {
        return Status{ErrorCode::invalid_argument,
                      "person group member count exceeds 64"};
    }
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    GroupDescriptor group;
    group.creator_person = creator_person_keys.public_key();
    group.generation = 1U;
    group.group_nonce = nonce.value();
    group.title.assign(title.begin(), title.end());
    group.members = std::move(members);
    auto id = compute_group_id(group, sodium);
    if (!id) return id.status();
    group.group_id = id.value();
    const Status valid = validate_group_shape(group, false);
    if (!valid.ok()) return valid;
    auto digest = group_descriptor_digest(group, sodium);
    if (!digest) return digest.status();
    auto signature =
        sodium.sign_detached(digest.value(), creator_person_keys.secret_key());
    if (!signature) return signature.status();
    group.signature = signature.value();
    return group;
}

Result<std::vector<std::uint8_t>> encode_unsigned_group_descriptor(
    const GroupDescriptor &group) {
    const Status valid = validate_group_shape(group, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kGroupHeader << '\n'
           << "group-id=" << security::hex(group.group_id) << '\n'
           << "creator-person=" << security::hex(group.creator_person) << '\n'
           << "generation=" << group.generation << '\n'
           << "group-nonce=" << security::hex(group.group_nonce) << '\n'
           << "title-hex=" << security::hex(group.title) << '\n'
           << "member-count=" << group.members.size() << '\n';
    for (const auto &member : group.members) {
        output << "member=" << security::hex(member) << '\n';
    }
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> group_descriptor_digest(
    const GroupDescriptor &group, const security::Sodium &sodium) {
    auto bytes = encode_unsigned_group_descriptor(group);
    if (!bytes) return bytes.status();
    return sodium.hash(kGroupDigestDomain, bytes.value());
}

Result<std::vector<std::uint8_t>> encode_signed_group_descriptor(
    const GroupDescriptor &group) {
    const Status valid = validate_group_shape(group, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_group_descriptor(group);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(group.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<GroupDescriptor> decode_signed_group_descriptor(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person group");
    if (!lines) return lines.status();
    auto group = parse_group_lines(lines.value());
    if (!group) return group.status();
    const Status valid = validate_group_shape(group.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_group_descriptor(group.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person group bytes are noncanonical"};
    }
    auto expected_id = compute_group_id(group.value(), sodium);
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != group.value().group_id) {
        return Status{ErrorCode::protocol_error,
                      "person group id does not match descriptor contents"};
    }
    auto digest = group_descriptor_digest(group.value(), sodium);
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        group.value().signature, digest.value(), group.value().creator_person);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person group signature is invalid"};
    }
    return group.value();
}

Result<GroupDescriptor> load_group_descriptor(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_signed_group_descriptor(bytes.value(), sodium);
}

Status write_group_descriptor(
    const std::filesystem::path &path, const GroupDescriptor &group) {
    auto bytes = encode_signed_group_descriptor(group);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status create_group_descriptor_file(
    const std::filesystem::path &path, const GroupDescriptor &group) {
    std::error_code error;
    if (std::filesystem::exists(path, error)) {
        return Status{ErrorCode::invalid_argument,
                      "person group descriptor already exists: " +
                          path.string()};
    }
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect person group descriptor path '" +
                          path.string() + "': " + error.message()};
    }
    return write_group_descriptor(path, group);
}

Status verify_group_member(
    const GroupDescriptor &group,
    const security::SigningPublicKey &person) {
    if (group_has_member(group, person)) return Status::success();
    return Status{ErrorCode::protocol_error,
                  "person is not a member of the group descriptor"};
}

std::string render_group_descriptor(const GroupDescriptor &group) {
    std::ostringstream output;
    output << "iotox-person-group-v1\n"
           << "group-id=" << security::hex(group.group_id) << '\n'
           << "creator-person=" << security::hex(group.creator_person) << '\n'
           << "generation=" << group.generation << '\n'
           << "title-hex=" << security::hex(group.title) << '\n'
           << "members=" << group.members.size() << '\n';
    for (const auto &member : group.members) {
        output << "member=" << security::hex(member) << '\n';
    }
    output << "signature=valid\n"
           << "boundary=group-membership-is-person-key-state; delivery-still-uses-each-person-card\n";
    return output.str();
}

Result<GroupMessageEnvelope> create_group_message_envelope(
    const security::SigningKeyPair &from_person_keys,
    const GroupDescriptor &group,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    const Status member =
        verify_group_member(group, from_person_keys.public_key());
    if (!member.ok()) return member;
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    GroupMessageEnvelope message;
    message.group_id = group.group_id;
    message.from_person = from_person_keys.public_key();
    message.nonce = nonce.value();
    message.body.assign(body.begin(), body.end());
    auto input = encode_group_message_id_input(
        message.group_id, message.from_person, message.nonce, message.body);
    if (!input) return input.status();
    auto id = sodium.hash(kGroupMessageIdDomain, input.value());
    if (!id) return id.status();
    message.message_id = id.value();
    const Status valid = validate_group_message_shape(message, false);
    if (!valid.ok()) return valid;
    auto unsigned_bytes = encode_unsigned_group_message_envelope(message);
    if (!unsigned_bytes) return unsigned_bytes.status();
    auto digest =
        sodium.hash(kGroupMessageDigestDomain, unsigned_bytes.value());
    if (!digest) return digest.status();
    auto signature =
        sodium.sign_detached(digest.value(), from_person_keys.secret_key());
    if (!signature) return signature.status();
    message.signature = signature.value();
    return message;
}

Result<std::vector<std::uint8_t>> encode_unsigned_group_message_envelope(
    const GroupMessageEnvelope &message) {
    const Status valid = validate_group_message_shape(message, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kGroupMessageHeader << '\n'
           << "group-id=" << security::hex(message.group_id) << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "nonce=" << security::hex(message.nonce) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-hex=" << security::hex(message.body) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<std::vector<std::uint8_t>> encode_signed_group_message_envelope(
    const GroupMessageEnvelope &message) {
    const Status valid = validate_group_message_shape(message, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_group_message_envelope(message);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(message.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<GroupMessageEnvelope> decode_signed_group_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person group message");
    if (!lines) return lines.status();
    auto message = parse_group_message_lines(lines.value());
    if (!message) return message.status();
    const Status valid = validate_group_message_shape(message.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_group_message_envelope(message.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person group message bytes are noncanonical"};
    }
    auto input = encode_group_message_id_input(
        message.value().group_id, message.value().from_person,
        message.value().nonce, message.value().body);
    if (!input) return input.status();
    auto expected_id = sodium.hash(kGroupMessageIdDomain, input.value());
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != message.value().message_id) {
        return Status{ErrorCode::protocol_error,
                      "person group message id does not match envelope contents"};
    }
    auto unsigned_bytes = encode_unsigned_group_message_envelope(message.value());
    if (!unsigned_bytes) return unsigned_bytes.status();
    auto digest = sodium.hash(kGroupMessageDigestDomain, unsigned_bytes.value());
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        message.value().signature, digest.value(), message.value().from_person);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person group message signature is invalid"};
    }
    return message.value();
}

Status verify_group_message(
    const GroupMessageEnvelope &message, const GroupDescriptor &group) {
    if (message.group_id != group.group_id) {
        return Status{ErrorCode::protocol_error,
                      "person group message group id does not match descriptor"};
    }
    return verify_group_member(group, message.from_person);
}

std::string render_group_message_envelope(
    const GroupMessageEnvelope &message) {
    std::ostringstream output;
    output << "iotox-person-group-message-v1\n"
           << "group-id=" << security::hex(message.group_id) << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-bytes=" << message.body.size() << '\n'
           << "body-hex=" << security::hex(message.body) << '\n'
           << "signature=valid\n"
           << "boundary=group-speaker-is-person-key; route-fanout-is-separate-delivery\n";
    return output.str();
}

Result<GroupDeviceMessageEnvelope> create_group_device_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    const GroupDescriptor &group,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium) {
    if (device_identity.public_key() != delegation.device) {
        return Status{ErrorCode::invalid_argument,
                      "--identity does not match the sender delegation device"};
    }
    const Status member = verify_group_member(group, delegation.person);
    if (!member.ok()) return member;
    auto delegation_digest = sender_delegation_digest(delegation, sodium);
    if (!delegation_digest) return delegation_digest.status();
    auto nonce = random_message_nonce();
    if (!nonce) return nonce.status();
    GroupDeviceMessageEnvelope message;
    message.group_id = group.group_id;
    message.from_person = delegation.person;
    message.from_device = delegation.device;
    message.delegation_digest = delegation_digest.value();
    message.nonce = nonce.value();
    message.body.assign(body.begin(), body.end());
    auto input = encode_group_device_message_id_input(
        message.group_id, message.from_person, message.from_device,
        message.delegation_digest, message.nonce, message.body);
    if (!input) return input.status();
    auto id = sodium.hash(kGroupDeviceMessageIdDomain, input.value());
    if (!id) return id.status();
    message.message_id = id.value();
    const Status valid = validate_group_device_message_shape(message, false);
    if (!valid.ok()) return valid;
    auto unsigned_bytes = encode_unsigned_group_device_message_envelope(message);
    if (!unsigned_bytes) return unsigned_bytes.status();
    auto digest =
        sodium.hash(kGroupDeviceMessageDigestDomain, unsigned_bytes.value());
    if (!digest) return digest.status();
    auto signature = device_identity.sign(digest.value());
    if (!signature) return signature.status();
    message.signature = signature.value();
    return message;
}

Result<std::vector<std::uint8_t>>
encode_unsigned_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message) {
    const Status valid = validate_group_device_message_shape(message, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kGroupDeviceMessageHeader << '\n'
           << "group-id=" << security::hex(message.group_id) << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "from-device=" << security::hex(message.from_device) << '\n'
           << "delegation-digest=" << security::hex(message.delegation_digest)
           << '\n'
           << "nonce=" << security::hex(message.nonce) << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-hex=" << security::hex(message.body) << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<std::vector<std::uint8_t>>
encode_signed_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message) {
    const Status valid = validate_group_device_message_shape(message, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_group_device_message_envelope(message);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(message.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<GroupDeviceMessageEnvelope> decode_signed_group_device_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person group device message");
    if (!lines) return lines.status();
    auto message = parse_group_device_message_lines(lines.value());
    if (!message) return message.status();
    const Status valid =
        validate_group_device_message_shape(message.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_group_device_message_envelope(message.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person group device message bytes are noncanonical"};
    }
    auto input = encode_group_device_message_id_input(
        message.value().group_id, message.value().from_person,
        message.value().from_device, message.value().delegation_digest,
        message.value().nonce, message.value().body);
    if (!input) return input.status();
    auto expected_id = sodium.hash(kGroupDeviceMessageIdDomain, input.value());
    if (!expected_id) return expected_id.status();
    if (expected_id.value() != message.value().message_id) {
        return Status{ErrorCode::protocol_error,
                      "person group device message id does not match envelope contents"};
    }
    auto unsigned_bytes =
        encode_unsigned_group_device_message_envelope(message.value());
    if (!unsigned_bytes) return unsigned_bytes.status();
    auto digest =
        sodium.hash(kGroupDeviceMessageDigestDomain, unsigned_bytes.value());
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        message.value().signature, digest.value(), message.value().from_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person group device message signature is invalid"};
    }
    return message.value();
}

Status verify_group_device_message(
    const GroupDeviceMessageEnvelope &message,
    const GroupDescriptor &group,
    const SenderDelegation &delegation,
    const security::Sodium &sodium) {
    if (message.group_id != group.group_id) {
        return Status{ErrorCode::protocol_error,
                      "person group device message group id does not match descriptor"};
    }
    if (!group_has_member(group, message.from_person)) {
        return Status{ErrorCode::protocol_error,
                      "person group device message speaker is not a group member"};
    }
    auto digest = sender_delegation_digest(delegation, sodium);
    if (!digest) return digest.status();
    if (message.delegation_digest != digest.value() ||
        message.from_person != delegation.person ||
        message.from_device != delegation.device) {
        return Status{ErrorCode::protocol_error,
                      "person group device message does not match sender delegation"};
    }
    return Status::success();
}

std::string render_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message) {
    std::ostringstream output;
    output << "iotox-person-group-device-message-v1\n"
           << "group-id=" << security::hex(message.group_id) << '\n'
           << "from-person=" << security::hex(message.from_person) << '\n'
           << "from-device=" << security::hex(message.from_device) << '\n'
           << "delegation-digest=" << security::hex(message.delegation_digest)
           << '\n'
           << "message-id=" << security::hex(message.message_id) << '\n'
           << "body-bytes=" << message.body.size() << '\n'
           << "body-hex=" << security::hex(message.body) << '\n'
           << "signature=valid\n"
           << "boundary=group-speaker-is-person-key-authorized-through-device-delegation\n";
    return output.str();
}

Result<ContactEntry> contact_entry_from_card(
    std::string_view name, const DeliveryCard &card,
    const security::Sodium &sodium) {
    auto digest = delivery_card_digest(card, sodium);
    if (!digest) return digest.status();
    ContactEntry entry;
    entry.name = std::string(name);
    entry.person = card.person;
    entry.generation = card.generation;
    entry.card_digest = digest.value();
    entry.routes = card.routes;
    const Status valid = validate_contact_entry(entry);
    if (!valid.ok()) return valid;
    return entry;
}

Result<ContactBook> load_contact_book(const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto book = decode_contact_book_bytes(bytes.value());
    if (!book) return book.status();
    auto canonical = encode_contact_book_bytes(book.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person contact book bytes are noncanonical"};
    }
    return book.value();
}

Status write_contact_book(
    const std::filesystem::path &path, const ContactBook &book) {
    auto bytes = encode_contact_book_bytes(book);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<ContactEntry> commit_contact_entry(
    const std::filesystem::path &path, const ContactEntry &entry) {
    const Status entry_valid = validate_contact_entry(entry);
    if (!entry_valid.ok()) return entry_valid;
    ContactBook book;
    auto loaded = load_contact_book(path);
    if (loaded) {
        book = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    auto found = std::lower_bound(
        book.contacts.begin(), book.contacts.end(), entry, contact_entry_less);
    if (found != book.contacts.end() && found->name == entry.name) {
        if (found->person != entry.person) {
            return Status{ErrorCode::protocol_error,
                          "person contact name already belongs to another person"};
        }
        if (entry.generation < found->generation) {
            return Status{ErrorCode::protocol_error,
                          "person contact card generation is below contact floor"};
        }
        if (entry.generation == found->generation &&
            entry.card_digest != found->card_digest) {
            return Status{ErrorCode::protocol_error,
                          "person contact card conflicts with same-generation floor"};
        }
        if (entry.generation == found->generation) {
            return *found;
        }
        *found = entry;
    } else {
        for (const ContactEntry &contact : book.contacts) {
            if (contact.person == entry.person) {
                return Status{ErrorCode::protocol_error,
                              "person contact person already has a different name"};
            }
        }
        if (book.contacts.size() >= kMaximumContacts) {
            return Status{ErrorCode::resource_exhausted,
                          "person contact book is full"};
        }
        found = book.contacts.insert(found, entry);
    }
    const Status written = write_contact_book(path, book);
    if (!written.ok()) return written;
    return *found;
}

Result<ContactEntry> find_contact(
    const ContactBook &book, std::string_view name) {
    const auto found = std::find_if(
        book.contacts.begin(), book.contacts.end(),
        [&](const ContactEntry &entry) { return entry.name == name; });
    if (found == book.contacts.end()) {
        return Status{ErrorCode::not_found,
                      "person contact name is not present"};
    }
    return *found;
}

std::string render_contact_entry(const ContactEntry &entry) {
    std::ostringstream output;
    output << "iotox-person-contact-v1\n"
           << "name=" << entry.name << '\n'
           << "person=" << security::hex(entry.person) << '\n'
           << "generation=" << entry.generation << '\n'
           << "card-digest=" << security::hex(entry.card_digest) << '\n'
           << "routes=" << entry.routes.size() << '\n';
    for (const DeliveryRouteKey &route : entry.routes) {
        output << "route=" << security::hex(route) << '\n';
    }
    output << "boundary=contact-book-is-local-card-floor-and-route-cache; not-private-roster-or-directory-service\n";
    return output.str();
}

std::string render_contact_book(const ContactBook &book) {
    std::ostringstream output;
    output << "iotox-person-contact-book-v1\n"
           << "contacts=" << book.contacts.size() << '\n';
    for (const ContactEntry &entry : book.contacts) {
        output << "contact name=" << entry.name
               << " person=" << security::hex(entry.person)
               << " generation=" << entry.generation
               << " routes=" << entry.routes.size()
               << " card-digest=" << security::hex(entry.card_digest) << '\n';
    }
    output << "boundary=owner-private-local-address-book; no-background-refresh-claim\n";
    return output.str();
}

Result<TranscriptEntry> transcript_entry_from_payload(
    std::span<const std::uint8_t> payload,
    std::string_view direction,
    const security::Sodium &sodium) {
    const Status direction_valid = validate_direction(direction);
    if (!direction_valid.ok()) return direction_valid;
    auto payload_digest = sodium.hash(kPayloadDigestDomain, payload);
    if (!payload_digest) return payload_digest.status();
    TranscriptEntry entry;
    entry.sequence = 0U;
    entry.direction = std::string(direction);
    entry.payload_digest = payload_digest.value();
    if (auto message = decode_signed_message_envelope(payload, sodium);
        message.ok()) {
        entry.scope = "person";
        entry.from_person = message.value().from_person;
        entry.to_person = message.value().to_person;
        entry.group.fill(0U);
        entry.message_id = message.value().message_id;
        entry.body = message.value().body;
    } else if (auto device_message =
                   decode_signed_device_message_envelope(payload, sodium);
               device_message.ok()) {
        entry.scope = "person";
        entry.from_person = device_message.value().from_person;
        entry.to_person = device_message.value().to_person;
        entry.group.fill(0U);
        entry.message_id = device_message.value().message_id;
        entry.body = device_message.value().body;
    } else if (auto group_message =
                   decode_signed_group_message_envelope(payload, sodium);
               group_message.ok()) {
        entry.scope = "group";
        entry.from_person = group_message.value().from_person;
        entry.to_person.fill(0U);
        entry.group = group_message.value().group_id;
        entry.message_id = group_message.value().message_id;
        entry.body = group_message.value().body;
    } else if (auto group_device_message =
                   decode_signed_group_device_message_envelope(payload, sodium);
               group_device_message.ok()) {
        entry.scope = "group";
        entry.from_person = group_device_message.value().from_person;
        entry.to_person.fill(0U);
        entry.group = group_device_message.value().group_id;
        entry.message_id = group_device_message.value().message_id;
        entry.body = group_device_message.value().body;
    } else {
        return Status{ErrorCode::protocol_error,
                      "payload is not a recognized signed person message"};
    }
    const Status valid = validate_transcript_entry(entry, false);
    if (!valid.ok()) return valid;
    return entry;
}

Result<TranscriptStore> load_transcript_store(
    const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto store = decode_transcript_store_bytes(bytes.value());
    if (!store) return store.status();
    auto canonical = encode_transcript_store_bytes(store.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person transcript bytes are noncanonical"};
    }
    return store.value();
}

Status write_transcript_store(
    const std::filesystem::path &path, const TranscriptStore &store) {
    auto bytes = encode_transcript_store_bytes(store);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<TranscriptCommit> commit_transcript_entry(
    const std::filesystem::path &path, const TranscriptEntry &entry) {
    const Status entry_valid = validate_transcript_entry(entry, false);
    if (!entry_valid.ok()) return entry_valid;
    TranscriptStore store;
    auto loaded = load_transcript_store(path);
    if (loaded) {
        store = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    for (const TranscriptEntry &existing : store.entries) {
        if (same_transcript_identity(existing, entry)) {
            return TranscriptCommit{existing, true, store.entries.size()};
        }
    }
    if (store.entries.size() >= kMaximumTranscriptEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person transcript is full"};
    }
    TranscriptEntry stored = entry;
    stored.sequence = store.next_sequence;
    if (++store.next_sequence == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "person transcript sequence overflow"};
    }
    store.entries.push_back(stored);
    const Status written = write_transcript_store(path, store);
    if (!written.ok()) return written;
    return TranscriptCommit{stored, false, store.entries.size()};
}

std::string render_transcript_store(const TranscriptStore &store) {
    std::ostringstream output;
    output << "iotox-person-transcript-v1\n"
           << "entries=" << store.entries.size() << '\n'
           << "next-sequence=" << store.next_sequence << '\n';
    for (const TranscriptEntry &entry : store.entries) {
        output << "entry sequence=" << entry.sequence
               << " direction=" << entry.direction
               << " scope=" << entry.scope
               << " from-person=" << security::hex(entry.from_person);
        if (entry.scope == "person") {
            output << " to-person=" << security::hex(entry.to_person);
        } else {
            output << " group=" << security::hex(entry.group);
        }
        output << " message-id=" << security::hex(entry.message_id)
               << " body-bytes=" << entry.body.size() << '\n';
    }
    output << "boundary=owner-private-contentful-transcript; not-consensus-or-all-device-delivery-proof\n";
    return output.str();
}

Result<std::vector<std::uint8_t>> encode_unsigned_receipt_record(
    const ReceiptRecord &receipt) {
    const Status valid = validate_receipt_shape(receipt, false);
    if (!valid.ok()) return valid;
    std::ostringstream output;
    output << kReceiptHeader << '\n'
           << "scope=" << receipt.scope << '\n'
           << "message-id=" << security::hex(receipt.message_id) << '\n'
           << "group=" << security::hex(receipt.group) << '\n'
           << "recipient-person=" << security::hex(receipt.recipient_person)
           << '\n'
           << "recipient-device=" << security::hex(receipt.recipient_device)
           << '\n'
           << "delegation-digest=" << security::hex(receipt.delegation_digest)
           << '\n'
           << "received-unix-ms=" << receipt.received_unix_ms << '\n';
    const std::string text = output.str();
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

Result<security::Digest> receipt_record_digest(
    const ReceiptRecord &receipt, const security::Sodium &sodium) {
    auto bytes = encode_unsigned_receipt_record(receipt);
    if (!bytes) return bytes.status();
    return sodium.hash(kReceiptDigestDomain, bytes.value());
}

Result<ReceiptRecord> create_receipt_record(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    std::span<const std::uint8_t> payload,
    std::uint64_t received_unix_ms,
    const security::Sodium &sodium) {
    if (device_identity.public_key() != delegation.device) {
        return Status{ErrorCode::invalid_argument,
                      "--identity does not match the receipt delegation device"};
    }
    auto entry = transcript_entry_from_payload(payload, "in", sodium);
    if (!entry) return entry.status();
    if (entry.value().scope == "person" &&
        entry.value().to_person != delegation.person) {
        return Status{ErrorCode::protocol_error,
                      "person receipt delegation is not the message recipient"};
    }
    auto delegation_digest = sender_delegation_digest(delegation, sodium);
    if (!delegation_digest) return delegation_digest.status();
    ReceiptRecord receipt;
    receipt.scope = entry.value().scope;
    receipt.message_id = entry.value().message_id;
    receipt.group = entry.value().group;
    receipt.recipient_person = delegation.person;
    receipt.recipient_device = delegation.device;
    receipt.delegation_digest = delegation_digest.value();
    receipt.received_unix_ms = received_unix_ms;
    auto digest = receipt_record_digest(receipt, sodium);
    if (!digest) return digest.status();
    auto signature = device_identity.sign(digest.value());
    if (!signature) return signature.status();
    receipt.signature = signature.value();
    return receipt;
}

Result<std::vector<std::uint8_t>> encode_signed_receipt_record(
    const ReceiptRecord &receipt) {
    const Status valid = validate_receipt_shape(receipt, true);
    if (!valid.ok()) return valid;
    auto bytes = encode_unsigned_receipt_record(receipt);
    if (!bytes) return bytes.status();
    const std::string signature =
        "signature=" + security::hex(receipt.signature) + "\n";
    bytes.value().insert(bytes.value().end(), signature.begin(),
                         signature.end());
    return bytes;
}

Result<ReceiptRecord> decode_signed_receipt_record(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium) {
    auto lines = split_lines(bytes, "person receipt");
    if (!lines) return lines.status();
    auto receipt = parse_receipt_lines(lines.value());
    if (!receipt) return receipt.status();
    const Status valid = validate_receipt_shape(receipt.value(), true);
    if (!valid.ok()) return valid;
    auto canonical = encode_signed_receipt_record(receipt.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "person receipt bytes are noncanonical"};
    }
    auto digest = receipt_record_digest(receipt.value(), sodium);
    if (!digest) return digest.status();
    const Status verified = sodium.verify_detached(
        receipt.value().signature, digest.value(),
        receipt.value().recipient_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "person receipt signature is invalid"};
    }
    return receipt.value();
}

Status verify_receipt_record(
    const ReceiptRecord &receipt,
    const SenderDelegation &delegation,
    const security::Sodium &sodium) {
    auto digest = sender_delegation_digest(delegation, sodium);
    if (!digest) return digest.status();
    if (receipt.delegation_digest != digest.value() ||
        receipt.recipient_person != delegation.person ||
        receipt.recipient_device != delegation.device) {
        return Status{ErrorCode::protocol_error,
                      "person receipt does not match sender delegation"};
    }
    return Status::success();
}

Result<ReceiptRecord> load_receipt_record(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    return decode_signed_receipt_record(bytes.value(), sodium);
}

Status write_receipt_record(
    const std::filesystem::path &path, const ReceiptRecord &receipt) {
    auto bytes = encode_signed_receipt_record(receipt);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status create_receipt_record_file(
    const std::filesystem::path &path, const ReceiptRecord &receipt) {
    std::error_code error;
    if (std::filesystem::exists(path, error)) {
        return Status{ErrorCode::invalid_argument,
                      "person receipt already exists: " + path.string()};
    }
    if (error) {
        return Status{ErrorCode::io_error,
                      "unable to inspect person receipt path '" +
                          path.string() + "': " + error.message()};
    }
    return write_receipt_record(path, receipt);
}

std::string render_receipt_record(const ReceiptRecord &receipt) {
    std::ostringstream output;
    output << "iotox-person-receipt-v1\n"
           << "scope=" << receipt.scope << '\n'
           << "message-id=" << security::hex(receipt.message_id) << '\n'
           << "group=" << security::hex(receipt.group) << '\n'
           << "recipient-person=" << security::hex(receipt.recipient_person)
           << '\n'
           << "recipient-device=" << security::hex(receipt.recipient_device)
           << '\n'
           << "delegation-digest=" << security::hex(receipt.delegation_digest)
           << '\n'
           << "received-unix-ms=" << receipt.received_unix_ms << '\n'
           << "signature=valid\n"
           << "boundary=device-receipt-under-person-delegation; not-aggregate-person-or-all-device-proof\n";
    return output.str();
}

Result<ReceiptStore> load_receipt_store(
    const std::filesystem::path &path, const security::Sodium &sodium) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto store = decode_receipt_store_bytes(bytes.value(), sodium);
    if (!store) return store.status();
    auto canonical = encode_receipt_store_bytes(store.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person receipt store bytes are noncanonical"};
    }
    return store.value();
}

Status write_receipt_store(
    const std::filesystem::path &path, const ReceiptStore &store) {
    auto bytes = encode_receipt_store_bytes(store);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<ReceiptCommit> commit_receipt_record(
    const std::filesystem::path &path, const ReceiptRecord &receipt,
    const security::Sodium &sodium) {
    const Status receipt_valid = validate_receipt_shape(receipt, true);
    if (!receipt_valid.ok()) return receipt_valid;
    ReceiptStore store;
    auto loaded = load_receipt_store(path, sodium);
    if (loaded) {
        store = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    auto found = std::lower_bound(
        store.receipts.begin(), store.receipts.end(), receipt, receipt_less);
    if (found != store.receipts.end() &&
        same_receipt_identity(*found, receipt)) {
        return ReceiptCommit{*found, true, store.receipts.size()};
    }
    if (store.receipts.size() >= kMaximumReceiptRecords) {
        return Status{ErrorCode::resource_exhausted,
                      "person receipt store is full"};
    }
    found = store.receipts.insert(found, receipt);
    const Status written = write_receipt_store(path, store);
    if (!written.ok()) return written;
    return ReceiptCommit{*found, false, store.receipts.size()};
}

std::string render_receipt_store(const ReceiptStore &store) {
    std::ostringstream output;
    output << "iotox-person-receipt-store-v1\n"
           << "receipts=" << store.receipts.size() << '\n';
    for (const ReceiptRecord &receipt : store.receipts) {
        output << "receipt scope=" << receipt.scope
               << " message-id=" << security::hex(receipt.message_id)
               << " recipient-person="
               << security::hex(receipt.recipient_person)
               << " recipient-device="
               << security::hex(receipt.recipient_device)
               << " received-unix-ms=" << receipt.received_unix_ms;
        if (receipt.scope == "group") {
            output << " group=" << security::hex(receipt.group);
        }
        output << '\n';
    }
    output << "boundary=content-free-device-receipt-rollup; aggregate-person-read-status-requires-explicit-expected-device-set\n";
    return output.str();
}

Result<OutboxItem> outbox_item_from_card(
    const DeliveryCard &card,
    std::span<const std::uint8_t> payload,
    const security::Sodium &sodium) {
    auto entry = transcript_entry_from_payload(payload, "out", sodium);
    if (!entry) return entry.status();
    if (entry.value().scope == "person" && entry.value().to_person != card.person) {
        return Status{ErrorCode::protocol_error,
                      "person outbox recipient card does not match payload recipient"};
    }
    auto card_digest = delivery_card_digest(card, sodium);
    if (!card_digest) return card_digest.status();
    OutboxItem item;
    item.message_id = entry.value().message_id;
    item.recipient_person = card.person;
    item.card_generation = card.generation;
    item.card_digest = card_digest.value();
    item.payload_digest = entry.value().payload_digest;
    item.payload.assign(payload.begin(), payload.end());
    item.pending_routes = card.routes;
    item.sent_routes.clear();
    const Status valid = validate_outbox_item(item);
    if (!valid.ok()) return valid;
    return item;
}

Result<OutboxStore> load_outbox_store(const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto store = decode_outbox_store_bytes(bytes.value());
    if (!store) return store.status();
    auto canonical = encode_outbox_store_bytes(store.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person outbox bytes are noncanonical"};
    }
    return store.value();
}

Status write_outbox_store(
    const std::filesystem::path &path, const OutboxStore &store) {
    auto bytes = encode_outbox_store_bytes(store);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<OutboxItem> commit_outbox_item(
    const std::filesystem::path &path, const OutboxItem &item) {
    const Status item_valid = validate_outbox_item(item);
    if (!item_valid.ok()) return item_valid;
    OutboxStore store;
    auto loaded = load_outbox_store(path);
    if (loaded) {
        store = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    auto found = std::lower_bound(
        store.items.begin(), store.items.end(), item, outbox_item_less);
    if (found != store.items.end() &&
        found->recipient_person == item.recipient_person &&
        found->message_id == item.message_id) {
        return *found;
    }
    if (store.items.size() >= kMaximumOutboxItems) {
        return Status{ErrorCode::resource_exhausted,
                      "person outbox is full"};
    }
    found = store.items.insert(found, item);
    const Status written = write_outbox_store(path, store);
    if (!written.ok()) return written;
    return *found;
}

Result<OutboxItem> mark_outbox_route_sent(
    const std::filesystem::path &path,
    const security::Digest &message_id,
    const DeliveryRouteKey &route) {
    auto loaded = load_outbox_store(path);
    if (!loaded) return loaded.status();
    OutboxStore store = std::move(loaded).value();
    for (OutboxItem &item : store.items) {
        if (item.message_id != message_id) continue;
        auto pending = std::lower_bound(
            item.pending_routes.begin(), item.pending_routes.end(), route);
        if (pending != item.pending_routes.end() && *pending == route) {
            item.pending_routes.erase(pending);
            item.sent_routes.push_back(route);
            std::sort(item.sent_routes.begin(), item.sent_routes.end());
            item.sent_routes.erase(
                std::unique(item.sent_routes.begin(), item.sent_routes.end()),
                item.sent_routes.end());
            const Status written = write_outbox_store(path, store);
            if (!written.ok()) return written;
            return item;
        }
        if (std::binary_search(item.sent_routes.begin(),
                               item.sent_routes.end(), route)) {
            return item;
        }
        return Status{ErrorCode::not_found,
                      "person outbox route is not part of the item"};
    }
    return Status{ErrorCode::not_found,
                  "person outbox message id is not present"};
}

Result<OutboxItem> record_outbox_attempt(
    const std::filesystem::path &path,
    const security::Digest &message_id,
    std::uint64_t attempted_unix_ms) {
    if (attempted_unix_ms == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox attempted time must be nonzero"};
    }
    auto loaded = load_outbox_store(path);
    if (!loaded) return loaded.status();
    OutboxStore store = std::move(loaded).value();
    for (OutboxItem &item : store.items) {
        if (item.message_id != message_id) continue;
        if (item.created_unix_ms == 0U) {
            item.created_unix_ms = attempted_unix_ms;
        }
        item.last_attempt_unix_ms = attempted_unix_ms;
        if (++item.attempts == 0U) {
            return Status{ErrorCode::resource_exhausted,
                          "person outbox attempt counter overflow"};
        }
        const Status valid = validate_outbox_item(item);
        if (!valid.ok()) return valid;
        const Status written = write_outbox_store(path, store);
        if (!written.ok()) return written;
        return item;
    }
    return Status{ErrorCode::not_found,
                  "person outbox message id is not present"};
}

Result<OutboxExpireResult> expire_outbox_items(
    const std::filesystem::path &path,
    const std::filesystem::path &dead_letter_path,
    std::uint64_t now_unix_ms,
    std::uint64_t expire_after_seconds) {
    if (now_unix_ms == 0U || expire_after_seconds == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "person outbox expiration requires nonzero time bounds"};
    }
    auto loaded = load_outbox_store(path);
    if (!loaded) return loaded.status();
    OutboxStore store = std::move(loaded).value();
    OutboxStore retained;
    OutboxStore expired;
    const std::uint64_t expire_after_ms = expire_after_seconds * 1000U;
    for (const OutboxItem &item : store.items) {
        const bool expirable =
            item.created_unix_ms != 0U &&
            now_unix_ms >= item.created_unix_ms &&
            now_unix_ms - item.created_unix_ms >= expire_after_ms &&
            !item.pending_routes.empty();
        if (expirable) {
            expired.items.push_back(item);
        } else {
            retained.items.push_back(item);
        }
    }
    if (expired.items.empty()) {
        return OutboxExpireResult{retained.items.size(), 0U, 0U};
    }

    OutboxStore dead_letters;
    auto loaded_dead = load_outbox_store(dead_letter_path);
    if (loaded_dead) {
        dead_letters = std::move(loaded_dead).value();
    } else if (loaded_dead.status().code() != ErrorCode::not_found) {
        return loaded_dead.status();
    }
    for (const OutboxItem &item : expired.items) {
        auto found = std::lower_bound(dead_letters.items.begin(),
                                      dead_letters.items.end(), item,
                                      outbox_item_less);
        if (found == dead_letters.items.end() ||
            found->recipient_person != item.recipient_person ||
            found->message_id != item.message_id) {
            if (dead_letters.items.size() >= kMaximumOutboxItems) {
                return Status{ErrorCode::resource_exhausted,
                              "person dead-letter outbox is full"};
            }
            dead_letters.items.insert(found, item);
        }
    }
    const Status dead_written =
        write_outbox_store(dead_letter_path, dead_letters);
    if (!dead_written.ok()) return dead_written;
    const Status retained_written = write_outbox_store(path, retained);
    if (!retained_written.ok()) return retained_written;
    return OutboxExpireResult{
        retained.items.size(), expired.items.size(), dead_letters.items.size()};
}

std::string render_outbox_store(const OutboxStore &store) {
    std::ostringstream output;
    output << "iotox-person-outbox-v1\n"
           << "items=" << store.items.size() << '\n';
    for (const OutboxItem &item : store.items) {
        output << "item message-id=" << security::hex(item.message_id)
               << " recipient-person=" << security::hex(item.recipient_person)
               << " card-generation=" << item.card_generation
               << " pending-routes=" << item.pending_routes.size()
               << " sent-routes=" << item.sent_routes.size()
               << " attempts=" << item.attempts
               << " created-unix-ms=" << item.created_unix_ms
               << " last-attempt-unix-ms=" << item.last_attempt_unix_ms
               << " payload-bytes=" << item.payload.size() << '\n';
    }
    output << "boundary=durable-reviewed-send-plan; native-background-retry-and-dead-letter-expiration-available; remote-receipt-is-separate\n";
    return output.str();
}

Result<ToxBridgeEntry> tox_bridge_entry_from_payload(
    std::span<const std::uint8_t> payload,
    const SenderDelegation &delegation,
    const security::Sodium &sodium) {
    auto message = decode_signed_tox_bridge_message_envelope(payload, sodium);
    if (!message) return message.status();
    const Status authorized =
        verify_tox_bridge_message_delegation(
            message.value(), delegation, sodium);
    if (!authorized.ok()) return authorized;
    auto payload_digest = sodium.hash(kToxBridgePayloadDigestDomain, payload);
    if (!payload_digest) return payload_digest.status();
    ToxBridgeEntry entry;
    entry.sequence = 0U;
    entry.direction = message.value().direction;
    entry.tox_kind = message.value().tox_kind;
    entry.observer_person = message.value().observer_person;
    entry.observer_device = message.value().observer_device;
    entry.external_tox_key = message.value().external_tox_key;
    entry.observed_unix_ms = message.value().observed_unix_ms;
    entry.message_id = message.value().message_id;
    entry.payload_digest = payload_digest.value();
    entry.body = message.value().body;
    const Status valid = validate_tox_bridge_entry(entry, false);
    if (!valid.ok()) return valid;
    return entry;
}

Result<ToxBridgeStore> load_tox_bridge_store(
    const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    auto store = decode_tox_bridge_store_bytes(bytes.value());
    if (!store) return store.status();
    auto canonical = encode_tox_bridge_store_bytes(store.value());
    if (!canonical) return canonical.status();
    if (canonical.value().size() != bytes.value().size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.value().begin())) {
        return Status{ErrorCode::protocol_error,
                      "person Tox bridge store bytes are noncanonical"};
    }
    return store.value();
}

Status write_tox_bridge_store(
    const std::filesystem::path &path,
    const ToxBridgeStore &store) {
    auto bytes = encode_tox_bridge_store_bytes(store);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Result<ToxBridgeCommit> commit_tox_bridge_entry(
    const std::filesystem::path &path,
    const ToxBridgeEntry &entry) {
    const Status entry_valid = validate_tox_bridge_entry(entry, false);
    if (!entry_valid.ok()) return entry_valid;
    ToxBridgeStore store;
    auto loaded = load_tox_bridge_store(path);
    if (loaded) {
        store = std::move(loaded).value();
    } else if (loaded.status().code() != ErrorCode::not_found) {
        return loaded.status();
    }
    for (const ToxBridgeEntry &existing : store.entries) {
        if (same_tox_bridge_identity(existing, entry)) {
            return ToxBridgeCommit{existing, true, store.entries.size()};
        }
    }
    if (store.entries.size() >= kMaximumToxBridgeEntries) {
        return Status{ErrorCode::resource_exhausted,
                      "person Tox bridge store is full"};
    }
    ToxBridgeEntry stored = entry;
    stored.sequence = store.next_sequence;
    if (++store.next_sequence == 0U) {
        return Status{ErrorCode::resource_exhausted,
                      "person Tox bridge sequence overflow"};
    }
    store.entries.push_back(stored);
    const Status written = write_tox_bridge_store(path, store);
    if (!written.ok()) return written;
    return ToxBridgeCommit{stored, false, store.entries.size()};
}

std::string render_tox_bridge_store(const ToxBridgeStore &store) {
    std::ostringstream output;
    output << "iotox-person-tox-bridge-store-v1\n"
           << "entries=" << store.entries.size() << '\n'
           << "next-sequence=" << store.next_sequence << '\n';
    for (const ToxBridgeEntry &entry : store.entries) {
        output << "entry sequence=" << entry.sequence
               << " direction=" << entry.direction
               << " tox-kind=" << entry.tox_kind
               << " observer-person="
               << security::hex(entry.observer_person)
               << " observer-device="
               << security::hex(entry.observer_device)
               << " external-tox-key="
               << security::hex(entry.external_tox_key)
               << " observed-unix-ms=" << entry.observed_unix_ms
               << " message-id=" << security::hex(entry.message_id)
               << " body-bytes=" << entry.body.size() << '\n';
    }
    output << "boundary=owner-private-normal-tox-compatibility-log; external-tox-keys-are-not-iotox-person-identities\n";
    return output.str();
}

}  // namespace iotox::person
