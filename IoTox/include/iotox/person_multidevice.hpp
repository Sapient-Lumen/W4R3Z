#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/self_swarm.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::person {

inline constexpr std::size_t kMaximumDeliveryRoutes = 64U;
inline constexpr std::size_t kMessageNonceBytes = 16U;
// Keep canonical v1 text envelopes below the normal Tox text-message bound.
inline constexpr std::size_t kMaximumMessageBodyBytes = 320U;
inline constexpr std::size_t kMaximumDelegationLabelBytes = 64U;
inline constexpr std::size_t kMaximumSeenEntries = 4096U;
inline constexpr std::size_t kMaximumGroupMembers = 64U;
inline constexpr std::size_t kMaximumGroupTitleBytes = 120U;
inline constexpr std::size_t kMaximumContacts = 256U;
inline constexpr std::size_t kMaximumTranscriptEntries = 8192U;
inline constexpr std::size_t kMaximumReceiptRecords = 8192U;
inline constexpr std::size_t kMaximumOutboxItems = 1024U;
inline constexpr std::size_t kToxPublicKeyBytes = 32U;
inline constexpr std::size_t kMaximumToxBridgeEntries = 8192U;

using DeliveryRouteKey = security::SigningPublicKey;
using ToxPublicKey = std::array<std::uint8_t, kToxPublicKeyBytes>;
using MessageNonce = std::array<std::uint8_t, kMessageNonceBytes>;

struct DeliveryCard {
    security::SigningPublicKey person{};
    std::uint64_t generation{0U};
    security::Digest roster_digest{};
    std::vector<DeliveryRouteKey> routes;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const DeliveryCard &) const = default;
};

struct MessageEnvelope {
    security::SigningPublicKey from_person{};
    security::SigningPublicKey to_person{};
    MessageNonce nonce{};
    security::Digest message_id{};
    std::vector<std::uint8_t> body;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const MessageEnvelope &) const = default;
};

struct SenderDelegation {
    security::SigningPublicKey person{};
    security::SigningPublicKey device{};
    std::uint64_t generation{0U};
    security::Digest roster_digest{};
    std::string label;
    // Zero means "not encoded as a clock expiry yet"; non-zero values are
    // carried and signed for future policy, but parser verification remains
    // deterministic and clock-free.
    std::uint64_t expires_unix_ms{0U};
    security::Signature signature{};

    [[nodiscard]] bool operator==(const SenderDelegation &) const = default;
};

struct DeviceMessageEnvelope {
    security::SigningPublicKey from_person{};
    security::SigningPublicKey from_device{};
    security::SigningPublicKey to_person{};
    security::Digest delegation_digest{};
    MessageNonce nonce{};
    security::Digest message_id{};
    std::vector<std::uint8_t> body;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const DeviceMessageEnvelope &) const = default;
};

struct CardFloor {
    security::SigningPublicKey person{};
    std::uint64_t generation{0U};
    security::Digest digest{};

    [[nodiscard]] bool operator==(const CardFloor &) const = default;
};

struct SeenEntry {
    std::string scope;
    security::SigningPublicKey person{};
    security::Digest group{};
    security::Digest message_id{};

    [[nodiscard]] bool operator==(const SeenEntry &) const = default;
};

struct SeenStore {
    std::vector<SeenEntry> entries;

    [[nodiscard]] bool operator==(const SeenStore &) const = default;
};

struct SeenCommit {
    SeenEntry entry;
    bool duplicate{false};
    std::size_t entries{0U};
};

struct GroupDescriptor {
    security::Digest group_id{};
    security::SigningPublicKey creator_person{};
    std::uint64_t generation{0U};
    MessageNonce group_nonce{};
    std::vector<std::uint8_t> title;
    std::vector<security::SigningPublicKey> members;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const GroupDescriptor &) const = default;
};

struct GroupMessageEnvelope {
    security::Digest group_id{};
    security::SigningPublicKey from_person{};
    MessageNonce nonce{};
    security::Digest message_id{};
    std::vector<std::uint8_t> body;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const GroupMessageEnvelope &) const = default;
};

struct GroupDeviceMessageEnvelope {
    security::Digest group_id{};
    security::SigningPublicKey from_person{};
    security::SigningPublicKey from_device{};
    security::Digest delegation_digest{};
    MessageNonce nonce{};
    security::Digest message_id{};
    std::vector<std::uint8_t> body;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const GroupDeviceMessageEnvelope &) const = default;
};

struct ContactEntry {
    std::string name;
    security::SigningPublicKey person{};
    std::uint64_t generation{0U};
    security::Digest card_digest{};
    std::vector<DeliveryRouteKey> routes;

    [[nodiscard]] bool operator==(const ContactEntry &) const = default;
};

struct ContactBook {
    std::vector<ContactEntry> contacts;

    [[nodiscard]] bool operator==(const ContactBook &) const = default;
};

struct TranscriptEntry {
    std::uint64_t sequence{0U};
    std::string direction;
    std::string scope;
    security::SigningPublicKey from_person{};
    security::SigningPublicKey to_person{};
    security::Digest group{};
    security::Digest message_id{};
    security::Digest payload_digest{};
    std::vector<std::uint8_t> body;

    [[nodiscard]] bool operator==(const TranscriptEntry &) const = default;
};

struct TranscriptStore {
    std::uint64_t next_sequence{1U};
    std::vector<TranscriptEntry> entries;

    [[nodiscard]] bool operator==(const TranscriptStore &) const = default;
};

struct TranscriptCommit {
    TranscriptEntry entry;
    bool duplicate{false};
    std::size_t entries{0U};
};

struct ReceiptRecord {
    std::string scope;
    security::Digest message_id{};
    security::Digest group{};
    security::SigningPublicKey recipient_person{};
    security::SigningPublicKey recipient_device{};
    security::Digest delegation_digest{};
    std::uint64_t received_unix_ms{0U};
    security::Signature signature{};

    [[nodiscard]] bool operator==(const ReceiptRecord &) const = default;
};

struct ReceiptStore {
    std::vector<ReceiptRecord> receipts;

    [[nodiscard]] bool operator==(const ReceiptStore &) const = default;
};

struct ReceiptCommit {
    ReceiptRecord receipt;
    bool duplicate{false};
    std::size_t receipts{0U};
};

struct OutboxItem {
    security::Digest message_id{};
    security::SigningPublicKey recipient_person{};
    std::uint64_t card_generation{0U};
    security::Digest card_digest{};
    security::Digest payload_digest{};
    std::vector<std::uint8_t> payload;
    std::vector<DeliveryRouteKey> pending_routes;
    std::vector<DeliveryRouteKey> sent_routes;
    std::uint64_t created_unix_ms{0U};
    std::uint64_t last_attempt_unix_ms{0U};
    std::uint64_t attempts{0U};

    [[nodiscard]] bool operator==(const OutboxItem &) const = default;
};

struct OutboxStore {
    std::vector<OutboxItem> items;

    [[nodiscard]] bool operator==(const OutboxStore &) const = default;
};

struct OutboxExpireResult {
    std::size_t kept{0U};
    std::size_t expired{0U};
    std::size_t dead_letter_items{0U};
};

struct ToxBridgeMessageEnvelope {
    std::string direction;
    std::string tox_kind;
    security::SigningPublicKey observer_person{};
    security::SigningPublicKey observer_device{};
    security::Digest delegation_digest{};
    ToxPublicKey external_tox_key{};
    std::uint64_t observed_unix_ms{0U};
    MessageNonce nonce{};
    security::Digest message_id{};
    std::vector<std::uint8_t> body;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const ToxBridgeMessageEnvelope &) const =
        default;
};

struct ToxBridgeEntry {
    std::uint64_t sequence{0U};
    std::string direction;
    std::string tox_kind;
    security::SigningPublicKey observer_person{};
    security::SigningPublicKey observer_device{};
    ToxPublicKey external_tox_key{};
    std::uint64_t observed_unix_ms{0U};
    security::Digest message_id{};
    security::Digest payload_digest{};
    std::vector<std::uint8_t> body;

    [[nodiscard]] bool operator==(const ToxBridgeEntry &) const = default;
};

struct ToxBridgeStore {
    std::uint64_t next_sequence{1U};
    std::vector<ToxBridgeEntry> entries;

    [[nodiscard]] bool operator==(const ToxBridgeStore &) const = default;
};

struct ToxBridgeCommit {
    ToxBridgeEntry entry;
    bool duplicate{false};
    std::size_t entries{0U};
};

[[nodiscard]] Result<DeliveryCard> delivery_card_from_roster(
    const self_swarm::Roster &roster, const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_delivery_card(
    const DeliveryCard &card);
[[nodiscard]] Result<security::Digest> delivery_card_digest(
    const DeliveryCard &card, const security::Sodium &sodium);
[[nodiscard]] Status sign_delivery_card(
    DeliveryCard &card, const security::SigningKeyPair &person_keys,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_delivery_card(
    const DeliveryCard &card);
[[nodiscard]] Result<DeliveryCard> decode_signed_delivery_card(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<DeliveryCard> load_delivery_card(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_delivery_card(
    const std::filesystem::path &path, const DeliveryCard &card);
[[nodiscard]] Status create_delivery_card_file(
    const std::filesystem::path &path, const DeliveryCard &card);
[[nodiscard]] std::string render_delivery_card(const DeliveryCard &card);

[[nodiscard]] Result<MessageEnvelope> create_message_envelope(
    const security::SigningKeyPair &from_person_keys,
    const security::SigningPublicKey &to_person,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_message_envelope(
    const MessageEnvelope &message);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_message_envelope(
    const MessageEnvelope &message);
[[nodiscard]] Result<MessageEnvelope> decode_signed_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> message_digest(
    const MessageEnvelope &message, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> compute_message_id(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &to_person,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_message_envelope(
    const MessageEnvelope &message);

[[nodiscard]] Result<SenderDelegation> sender_delegation_from_roster(
    const self_swarm::Roster &roster, std::string_view alias,
    const security::Sodium &sodium,
    std::uint64_t expires_unix_ms = 0U);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_sender_delegation(
    const SenderDelegation &delegation);
[[nodiscard]] Result<security::Digest> sender_delegation_digest(
    const SenderDelegation &delegation, const security::Sodium &sodium);
[[nodiscard]] Status sign_sender_delegation(
    SenderDelegation &delegation,
    const security::SigningKeyPair &person_keys,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_sender_delegation(
    const SenderDelegation &delegation);
[[nodiscard]] Result<SenderDelegation> decode_signed_sender_delegation(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<SenderDelegation> load_sender_delegation(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_sender_delegation(
    const std::filesystem::path &path, const SenderDelegation &delegation);
[[nodiscard]] Status create_sender_delegation_file(
    const std::filesystem::path &path, const SenderDelegation &delegation);
[[nodiscard]] std::string render_sender_delegation(
    const SenderDelegation &delegation);

[[nodiscard]] Result<DeviceMessageEnvelope> create_device_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    const security::SigningPublicKey &to_person,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_unsigned_device_message_envelope(
    const DeviceMessageEnvelope &message);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_signed_device_message_envelope(
    const DeviceMessageEnvelope &message);
[[nodiscard]] Result<DeviceMessageEnvelope>
decode_signed_device_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> device_message_digest(
    const DeviceMessageEnvelope &message, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> compute_device_message_id(
    const security::SigningPublicKey &from_person,
    const security::SigningPublicKey &from_device,
    const security::SigningPublicKey &to_person,
    const security::Digest &delegation_digest,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Status verify_device_message_delegation(
    const DeviceMessageEnvelope &message,
    const SenderDelegation &delegation,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_device_message_envelope(
    const DeviceMessageEnvelope &message);

[[nodiscard]] Result<CardFloor> card_floor_from_card(
    const DeliveryCard &card, const security::Sodium &sodium);
[[nodiscard]] Status check_card_floor(
    const DeliveryCard &card, const CardFloor &floor,
    const security::Sodium &sodium);
[[nodiscard]] Result<CardFloor> load_card_floor(
    const std::filesystem::path &path);
[[nodiscard]] Status write_card_floor(
    const std::filesystem::path &path, const CardFloor &floor);
[[nodiscard]] Result<CardFloor> commit_card_floor(
    const std::filesystem::path &path, const DeliveryCard &card,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_card_floor(const CardFloor &floor);

[[nodiscard]] Result<SeenEntry> seen_entry_for_message(
    const MessageEnvelope &message);
[[nodiscard]] Result<SeenEntry> seen_entry_for_message(
    const DeviceMessageEnvelope &message);
[[nodiscard]] Result<SeenEntry> seen_entry_for_message(
    const GroupMessageEnvelope &message);
[[nodiscard]] Result<SeenEntry> seen_entry_for_message(
    const GroupDeviceMessageEnvelope &message);
[[nodiscard]] Result<SeenStore> load_seen_store(
    const std::filesystem::path &path);
[[nodiscard]] Status write_seen_store(
    const std::filesystem::path &path, const SeenStore &store);
[[nodiscard]] Result<SeenCommit> commit_seen_entry(
    const std::filesystem::path &path, const SeenEntry &entry);
[[nodiscard]] std::string render_seen_store(const SeenStore &store);

[[nodiscard]] Result<GroupDescriptor> create_group_descriptor(
    const security::SigningKeyPair &creator_person_keys,
    std::span<const std::uint8_t> title,
    std::vector<security::SigningPublicKey> members,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_group_descriptor(
    const GroupDescriptor &group);
[[nodiscard]] Result<security::Digest> compute_group_id(
    const GroupDescriptor &group, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> group_descriptor_digest(
    const GroupDescriptor &group, const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_group_descriptor(
    const GroupDescriptor &group);
[[nodiscard]] Result<GroupDescriptor> decode_signed_group_descriptor(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<GroupDescriptor> load_group_descriptor(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_group_descriptor(
    const std::filesystem::path &path, const GroupDescriptor &group);
[[nodiscard]] Status create_group_descriptor_file(
    const std::filesystem::path &path, const GroupDescriptor &group);
[[nodiscard]] Status verify_group_member(
    const GroupDescriptor &group,
    const security::SigningPublicKey &person);
[[nodiscard]] std::string render_group_descriptor(
    const GroupDescriptor &group);

[[nodiscard]] Result<GroupMessageEnvelope> create_group_message_envelope(
    const security::SigningKeyPair &from_person_keys,
    const GroupDescriptor &group,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_unsigned_group_message_envelope(
    const GroupMessageEnvelope &message);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_signed_group_message_envelope(
    const GroupMessageEnvelope &message);
[[nodiscard]] Result<GroupMessageEnvelope> decode_signed_group_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Status verify_group_message(
    const GroupMessageEnvelope &message, const GroupDescriptor &group);
[[nodiscard]] std::string render_group_message_envelope(
    const GroupMessageEnvelope &message);

[[nodiscard]] Result<GroupDeviceMessageEnvelope>
create_group_device_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    const GroupDescriptor &group,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_unsigned_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_signed_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message);
[[nodiscard]] Result<GroupDeviceMessageEnvelope>
decode_signed_group_device_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Status verify_group_device_message(
    const GroupDeviceMessageEnvelope &message,
    const GroupDescriptor &group,
    const SenderDelegation &delegation,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_group_device_message_envelope(
    const GroupDeviceMessageEnvelope &message);

[[nodiscard]] Result<ContactEntry> contact_entry_from_card(
    std::string_view name, const DeliveryCard &card,
    const security::Sodium &sodium);
[[nodiscard]] Result<ContactBook> load_contact_book(
    const std::filesystem::path &path);
[[nodiscard]] Status write_contact_book(
    const std::filesystem::path &path, const ContactBook &book);
[[nodiscard]] Result<ContactEntry> commit_contact_entry(
    const std::filesystem::path &path, const ContactEntry &entry);
[[nodiscard]] Result<ContactEntry> find_contact(
    const ContactBook &book, std::string_view name);
[[nodiscard]] std::string render_contact_book(const ContactBook &book);
[[nodiscard]] std::string render_contact_entry(const ContactEntry &entry);

[[nodiscard]] Result<TranscriptEntry> transcript_entry_from_payload(
    std::span<const std::uint8_t> payload,
    std::string_view direction,
    const security::Sodium &sodium);
[[nodiscard]] Result<TranscriptStore> load_transcript_store(
    const std::filesystem::path &path);
[[nodiscard]] Status write_transcript_store(
    const std::filesystem::path &path, const TranscriptStore &store);
[[nodiscard]] Result<TranscriptCommit> commit_transcript_entry(
    const std::filesystem::path &path, const TranscriptEntry &entry);
[[nodiscard]] std::string render_transcript_store(
    const TranscriptStore &store);

[[nodiscard]] Result<ReceiptRecord> create_receipt_record(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    std::span<const std::uint8_t> payload,
    std::uint64_t received_unix_ms,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned_receipt_record(
    const ReceiptRecord &receipt);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed_receipt_record(
    const ReceiptRecord &receipt);
[[nodiscard]] Result<ReceiptRecord> decode_signed_receipt_record(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> receipt_record_digest(
    const ReceiptRecord &receipt, const security::Sodium &sodium);
[[nodiscard]] Status verify_receipt_record(
    const ReceiptRecord &receipt,
    const SenderDelegation &delegation,
    const security::Sodium &sodium);
[[nodiscard]] Result<ReceiptRecord> load_receipt_record(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_receipt_record(
    const std::filesystem::path &path, const ReceiptRecord &receipt);
[[nodiscard]] Status create_receipt_record_file(
    const std::filesystem::path &path, const ReceiptRecord &receipt);
[[nodiscard]] std::string render_receipt_record(
    const ReceiptRecord &receipt);
[[nodiscard]] Result<ReceiptStore> load_receipt_store(
    const std::filesystem::path &path, const security::Sodium &sodium);
[[nodiscard]] Status write_receipt_store(
    const std::filesystem::path &path, const ReceiptStore &store);
[[nodiscard]] Result<ReceiptCommit> commit_receipt_record(
    const std::filesystem::path &path, const ReceiptRecord &receipt,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_receipt_store(
    const ReceiptStore &store);

[[nodiscard]] Result<OutboxItem> outbox_item_from_card(
    const DeliveryCard &card,
    std::span<const std::uint8_t> payload,
    const security::Sodium &sodium);
[[nodiscard]] Result<OutboxStore> load_outbox_store(
    const std::filesystem::path &path);
[[nodiscard]] Status write_outbox_store(
    const std::filesystem::path &path, const OutboxStore &store);
[[nodiscard]] Result<OutboxItem> commit_outbox_item(
    const std::filesystem::path &path, const OutboxItem &item);
[[nodiscard]] Result<OutboxItem> mark_outbox_route_sent(
    const std::filesystem::path &path,
    const security::Digest &message_id,
    const DeliveryRouteKey &route);
[[nodiscard]] Result<OutboxItem> record_outbox_attempt(
    const std::filesystem::path &path,
    const security::Digest &message_id,
    std::uint64_t attempted_unix_ms);
[[nodiscard]] Result<OutboxExpireResult> expire_outbox_items(
    const std::filesystem::path &path,
    const std::filesystem::path &dead_letter_path,
    std::uint64_t now_unix_ms,
    std::uint64_t expire_after_seconds);
[[nodiscard]] std::string render_outbox_store(const OutboxStore &store);

[[nodiscard]] Result<ToxBridgeMessageEnvelope>
create_tox_bridge_message_envelope(
    const security::DeviceIdentity &device_identity,
    const SenderDelegation &delegation,
    std::string_view direction,
    std::string_view tox_kind,
    const ToxPublicKey &external_tox_key,
    std::span<const std::uint8_t> body,
    std::uint64_t observed_unix_ms,
    const security::Sodium &sodium);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_unsigned_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_signed_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message);
[[nodiscard]] Result<ToxBridgeMessageEnvelope>
decode_signed_tox_bridge_message_envelope(
    std::span<const std::uint8_t> bytes, const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> tox_bridge_message_digest(
    const ToxBridgeMessageEnvelope &message,
    const security::Sodium &sodium);
[[nodiscard]] Result<security::Digest> compute_tox_bridge_message_id(
    std::string_view direction,
    std::string_view tox_kind,
    const security::SigningPublicKey &observer_person,
    const security::SigningPublicKey &observer_device,
    const security::Digest &delegation_digest,
    const ToxPublicKey &external_tox_key,
    std::uint64_t observed_unix_ms,
    const MessageNonce &nonce,
    std::span<const std::uint8_t> body,
    const security::Sodium &sodium);
[[nodiscard]] Status verify_tox_bridge_message_delegation(
    const ToxBridgeMessageEnvelope &message,
    const SenderDelegation &delegation,
    const security::Sodium &sodium);
[[nodiscard]] std::string render_tox_bridge_message_envelope(
    const ToxBridgeMessageEnvelope &message);

[[nodiscard]] Result<ToxBridgeEntry> tox_bridge_entry_from_payload(
    std::span<const std::uint8_t> payload,
    const SenderDelegation &delegation,
    const security::Sodium &sodium);
[[nodiscard]] Result<ToxBridgeStore> load_tox_bridge_store(
    const std::filesystem::path &path);
[[nodiscard]] Status write_tox_bridge_store(
    const std::filesystem::path &path,
    const ToxBridgeStore &store);
[[nodiscard]] Result<ToxBridgeCommit> commit_tox_bridge_entry(
    const std::filesystem::path &path,
    const ToxBridgeEntry &entry);
[[nodiscard]] std::string render_tox_bridge_store(
    const ToxBridgeStore &store);

}  // namespace iotox::person
