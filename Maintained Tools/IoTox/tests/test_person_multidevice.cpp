#include "test_harness.hpp"

#include "iotox/person_multidevice.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/self_swarm.hpp"
#include "iotox/state_store.hpp"
#include "iotox/toxcore/abi.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <sstream>
#include <string>
#include <system_error>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-person-XXXXXX";
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        if (char *created = ::mkdtemp(bytes.data()); created != nullptr) {
            root_ = created;
        }
    }
    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(root_, ignored);
    }
    [[nodiscard]] const std::filesystem::path &root() const { return root_; }

  private:
    std::filesystem::path root_;
};

iotox::security::SigningKeyPair keypair(
    iotox::security::Sodium &sodium, std::uint8_t tag) {
    iotox::security::SigningSeed seed{};
    seed.fill(tag);
    auto keys = sodium.signing_keypair_from_seed(seed);
    IOTOX_CHECK_MSG(keys.ok(), keys.status().message());
    return std::move(keys).value();
}

iotox::security::SigningPublicKey public_key(
    iotox::security::Sodium &sodium, std::uint8_t tag) {
    auto keys = keypair(sodium, tag);
    return keys.public_key();
}

iotox::self_swarm::Member member(
    iotox::security::Sodium &sodium, std::string alias,
    std::uint8_t principal_tag, std::uint8_t tox_tag) {
    iotox::self_swarm::Member result;
    result.alias = std::move(alias);
    result.principal = public_key(sodium, principal_tag);
    result.tox_public_key = public_key(sodium, tox_tag);
    result.role = iotox::security::PrincipalRole::operator_role;
    result.capabilities = static_cast<std::uint64_t>(
        iotox::security::Capability::interactive_terminal);
    return result;
}

std::vector<std::uint8_t> bytes(std::string_view text) {
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

iotox::person::DeliveryCard signed_card(
    iotox::security::Sodium &sodium,
    const iotox::security::SigningKeyPair &owner,
    const iotox::self_swarm::Roster &roster) {
    auto card = iotox::person::delivery_card_from_roster(roster, sodium);
    IOTOX_CHECK_MSG(card.ok(), card.status().message());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    card.value(), owner, sodium).ok());
    return card.value();
}

}  // namespace

IOTOX_TEST("person delivery card derives public routes without private roster aliases") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xA1U);

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x11U, 0x21U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    auto joined = iotox::self_swarm::add_member(
        roster.value(), member(sodium.value(), "laptop", 0x12U, 0x22U),
        sodium.value());
    IOTOX_CHECK_MSG(joined.ok(), joined.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    joined.value(), owner, sodium.value()).ok());

    auto card =
        iotox::person::delivery_card_from_roster(joined.value(), sodium.value());
    IOTOX_CHECK_MSG(card.ok(), card.status().message());
    IOTOX_CHECK(card.value().person == owner.public_key());
    IOTOX_CHECK(card.value().generation == 2U);
    IOTOX_CHECK(card.value().routes.size() == 2U);
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    card.value(), owner, sodium.value()).ok());
    auto encoded = iotox::person::encode_signed_delivery_card(card.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    const std::string encoded_text(
        reinterpret_cast<const char *>(encoded.value().data()),
        encoded.value().size());
    IOTOX_CHECK(encoded_text.find("desktop") == std::string::npos);
    IOTOX_CHECK(encoded_text.find("laptop") == std::string::npos);
    IOTOX_CHECK(encoded_text.find("route-count=2\n") != std::string::npos);

    auto decoded = iotox::person::decode_signed_delivery_card(
        encoded.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == card.value());
    IOTOX_CHECK(iotox::person::render_delivery_card(decoded.value()).find(
                    "tox-routes-are-delivery-not-personhood") !=
                std::string::npos);
    IOTOX_CHECK(iotox::person::render_delivery_card(decoded.value()).find(
                    "route-policy=not-carried-by-person-card") !=
                std::string::npos);
}

IOTOX_TEST("person delivery card rejects tamper and excludes retired routes") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xB1U);

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x31U, 0x41U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    auto joined = iotox::self_swarm::add_member(
        roster.value(), member(sodium.value(), "laptop", 0x32U, 0x42U),
        sodium.value());
    IOTOX_CHECK_MSG(joined.ok(), joined.status().message());
    auto retired =
        iotox::self_swarm::retire_member(joined.value(), "laptop", sodium.value());
    IOTOX_CHECK_MSG(retired.ok(), retired.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    retired.value(), owner, sodium.value()).ok());

    auto card =
        iotox::person::delivery_card_from_roster(retired.value(), sodium.value());
    IOTOX_CHECK_MSG(card.ok(), card.status().message());
    IOTOX_CHECK(card.value().routes.size() == 1U);
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    card.value(), owner, sodium.value()).ok());
    auto encoded = iotox::person::encode_signed_delivery_card(card.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());

    const std::string needle{"generation=3"};
    const auto found = std::search(
        encoded.value().begin(), encoded.value().end(),
        needle.begin(), needle.end());
    IOTOX_CHECK(found != encoded.value().end());
    *(found + static_cast<std::ptrdiff_t>(needle.size() - 1U)) =
        static_cast<std::uint8_t>('4');
    auto decoded = iotox::person::decode_signed_delivery_card(
        encoded.value(), sodium.value());
    IOTOX_CHECK(!decoded.ok());
}

IOTOX_TEST("person delivery card files are no clobber and load canonically") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xC1U);
    TemporaryDirectory directory;
    const std::filesystem::path path = directory.root() / "me.person.card";

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x51U, 0x61U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    auto card =
        iotox::person::delivery_card_from_roster(roster.value(), sodium.value());
    IOTOX_CHECK_MSG(card.ok(), card.status().message());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    card.value(), owner, sodium.value()).ok());
    IOTOX_CHECK(iotox::person::create_delivery_card_file(
                    path, card.value()).ok());
    IOTOX_CHECK(!iotox::person::create_delivery_card_file(
                    path, card.value()).ok());
    auto loaded = iotox::person::load_delivery_card(path, sodium.value());
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value() == card.value());
}

IOTOX_TEST("person messages sign verify and reject tamper") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto sender = keypair(sodium.value(), 0xD1U);
    auto recipient = keypair(sodium.value(), 0xD2U);
    const std::string text{"hello from a person key"};

    auto message = iotox::person::create_message_envelope(
        sender, recipient.public_key(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()),
            text.size()),
        sodium.value());
    IOTOX_CHECK_MSG(message.ok(), message.status().message());
    auto encoded =
        iotox::person::encode_signed_message_envelope(message.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() <= 1372U);

    auto decoded = iotox::person::decode_signed_message_envelope(
        encoded.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == message.value());
    IOTOX_CHECK(iotox::person::render_message_envelope(decoded.value()).find(
                    "transport-route-is-not-sender-identity") !=
                std::string::npos);

    const std::string body_hex = iotox::security::hex(message.value().body);
    const auto found = std::search(
        encoded.value().begin(), encoded.value().end(),
        body_hex.begin(), body_hex.end());
    IOTOX_CHECK(found != encoded.value().end());
    *found = *found == static_cast<std::uint8_t>('A')
        ? static_cast<std::uint8_t>('B')
        : static_cast<std::uint8_t>('A');
    auto tampered = iotox::person::decode_signed_message_envelope(
        encoded.value(), sodium.value());
    IOTOX_CHECK(!tampered.ok());
}

IOTOX_TEST("person message body bounds are enforced") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto sender = keypair(sodium.value(), 0xE1U);
    auto recipient = keypair(sodium.value(), 0xE2U);
    std::vector<std::uint8_t> too_large(
        iotox::person::kMaximumMessageBodyBytes + 1U, 0x41U);
    auto message = iotox::person::create_message_envelope(
        sender, recipient.public_key(), too_large, sodium.value());
    IOTOX_CHECK(!message.ok());
}

IOTOX_TEST("person sender delegation authorizes device-signed messages") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0x71U);
    auto recipient = keypair(sodium.value(), 0x72U);
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::self_swarm::Member desktop =
        member(sodium.value(), "desktop", 0x73U, 0x74U);
    desktop.principal = identity.value().public_key();
    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), std::move(desktop));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());

    auto delegation = iotox::person::sender_delegation_from_roster(
        roster.value(), "desktop", sodium.value());
    IOTOX_CHECK_MSG(delegation.ok(), delegation.status().message());
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    delegation.value(), owner, sodium.value()).ok());
    auto encoded_delegation =
        iotox::person::encode_signed_sender_delegation(delegation.value());
    IOTOX_CHECK_MSG(encoded_delegation.ok(),
                    encoded_delegation.status().message());
    auto decoded_delegation =
        iotox::person::decode_signed_sender_delegation(
            encoded_delegation.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded_delegation.ok(),
                    decoded_delegation.status().message());
    IOTOX_CHECK(decoded_delegation.value() == delegation.value());

    const std::string text{"hello from one of my machines"};
    auto message = iotox::person::create_device_message_envelope(
        identity.value(), delegation.value(), recipient.public_key(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()),
            text.size()),
        sodium.value());
    IOTOX_CHECK_MSG(message.ok(), message.status().message());
    auto encoded =
        iotox::person::encode_signed_device_message_envelope(message.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() <= 1372U);
    auto decoded = iotox::person::decode_signed_device_message_envelope(
        encoded.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == message.value());
    IOTOX_CHECK(iotox::person::verify_device_message_delegation(
                    decoded.value(), delegation.value(), sodium.value()).ok());

    auto wrong_delegation = delegation.value();
    wrong_delegation.device = public_key(sodium.value(), 0x75U);
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    wrong_delegation, owner, sodium.value()).ok());
    IOTOX_CHECK(!iotox::person::verify_device_message_delegation(
                    decoded.value(), wrong_delegation, sodium.value()).ok());
}

IOTOX_TEST("person delivery card floor rejects stale and same-generation forks") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0x81U);

    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), member(sodium.value(), "desktop", 0x82U, 0x83U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    auto old_card =
        iotox::person::delivery_card_from_roster(roster.value(), sodium.value());
    IOTOX_CHECK_MSG(old_card.ok(), old_card.status().message());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    old_card.value(), owner, sodium.value()).ok());

    auto joined = iotox::self_swarm::add_member(
        roster.value(), member(sodium.value(), "laptop", 0x84U, 0x85U),
        sodium.value());
    IOTOX_CHECK_MSG(joined.ok(), joined.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    joined.value(), owner, sodium.value()).ok());
    auto new_card =
        iotox::person::delivery_card_from_roster(joined.value(), sodium.value());
    IOTOX_CHECK_MSG(new_card.ok(), new_card.status().message());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    new_card.value(), owner, sodium.value()).ok());

    TemporaryDirectory directory;
    auto floor = iotox::person::commit_card_floor(
        directory.root() / "friend.floor", new_card.value(), sodium.value());
    IOTOX_CHECK_MSG(floor.ok(), floor.status().message());
    IOTOX_CHECK(!iotox::person::check_card_floor(
                    old_card.value(), floor.value(), sodium.value()).ok());

    iotox::person::DeliveryCard fork = new_card.value();
    fork.routes.back() = public_key(sodium.value(), 0x86U);
    std::sort(fork.routes.begin(), fork.routes.end());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    fork, owner, sodium.value()).ok());
    IOTOX_CHECK(!iotox::person::check_card_floor(
                    fork, floor.value(), sodium.value()).ok());
}

IOTOX_TEST("person seen store suppresses duplicate person and group messages") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto sender = keypair(sodium.value(), 0x91U);
    auto recipient = keypair(sodium.value(), 0x92U);
    const std::string text{"seen once"};
    auto message = iotox::person::create_message_envelope(
        sender, recipient.public_key(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()),
            text.size()),
        sodium.value());
    IOTOX_CHECK_MSG(message.ok(), message.status().message());
    auto entry = iotox::person::seen_entry_for_message(message.value());
    IOTOX_CHECK_MSG(entry.ok(), entry.status().message());
    TemporaryDirectory directory;
    const auto store_path = directory.root() / "seen.store";
    auto first = iotox::person::commit_seen_entry(store_path, entry.value());
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(!first.value().duplicate);
    auto second = iotox::person::commit_seen_entry(store_path, entry.value());
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().duplicate);

    auto group = iotox::person::create_group_descriptor(
        sender,
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>("ops"), 3U),
        std::vector<iotox::security::SigningPublicKey>{recipient.public_key()},
        sodium.value());
    IOTOX_CHECK_MSG(group.ok(), group.status().message());
    auto group_message = iotox::person::create_group_message_envelope(
        sender, group.value(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()),
            text.size()),
        sodium.value());
    IOTOX_CHECK_MSG(group_message.ok(), group_message.status().message());
    auto group_entry =
        iotox::person::seen_entry_for_message(group_message.value());
    IOTOX_CHECK_MSG(group_entry.ok(), group_entry.status().message());
    auto third = iotox::person::commit_seen_entry(store_path, group_entry.value());
    IOTOX_CHECK_MSG(third.ok(), third.status().message());
    IOTOX_CHECK(!third.value().duplicate);
    auto loaded = iotox::person::load_seen_store(store_path);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value().entries.size() == 2U);
}

IOTOX_TEST("person groups sign direct and delegated group messages") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xA2U);
    auto friend_person = keypair(sodium.value(), 0xA3U);
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    auto group = iotox::person::create_group_descriptor(
        owner,
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>("operators"), 9U),
        std::vector<iotox::security::SigningPublicKey>{
            friend_person.public_key()},
        sodium.value());
    IOTOX_CHECK_MSG(group.ok(), group.status().message());
    auto encoded_group =
        iotox::person::encode_signed_group_descriptor(group.value());
    IOTOX_CHECK_MSG(encoded_group.ok(), encoded_group.status().message());
    auto decoded_group = iotox::person::decode_signed_group_descriptor(
        encoded_group.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded_group.ok(), decoded_group.status().message());
    IOTOX_CHECK(decoded_group.value() == group.value());

    const std::string text{"group hello"};
    auto group_message = iotox::person::create_group_message_envelope(
        owner, group.value(),
        std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(text.data()),
            text.size()),
        sodium.value());
    IOTOX_CHECK_MSG(group_message.ok(), group_message.status().message());
    auto encoded_message =
        iotox::person::encode_signed_group_message_envelope(
            group_message.value());
    IOTOX_CHECK_MSG(encoded_message.ok(), encoded_message.status().message());
    IOTOX_CHECK(encoded_message.value().size() <= 1372U);
    auto decoded_message =
        iotox::person::decode_signed_group_message_envelope(
            encoded_message.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded_message.ok(), decoded_message.status().message());
    IOTOX_CHECK(iotox::person::verify_group_message(
                    decoded_message.value(), group.value()).ok());

    iotox::self_swarm::Member desktop =
        member(sodium.value(), "desktop", 0xA4U, 0xA5U);
    desktop.principal = identity.value().public_key();
    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), std::move(desktop));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    auto delegation = iotox::person::sender_delegation_from_roster(
        roster.value(), "desktop", sodium.value());
    IOTOX_CHECK_MSG(delegation.ok(), delegation.status().message());
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    delegation.value(), owner, sodium.value()).ok());
    auto device_message =
        iotox::person::create_group_device_message_envelope(
            identity.value(), delegation.value(), group.value(),
            std::span<const std::uint8_t>(
                reinterpret_cast<const std::uint8_t *>(text.data()),
                text.size()),
            sodium.value());
    IOTOX_CHECK_MSG(device_message.ok(), device_message.status().message());
    auto encoded_device =
        iotox::person::encode_signed_group_device_message_envelope(
            device_message.value());
    IOTOX_CHECK_MSG(encoded_device.ok(), encoded_device.status().message());
    IOTOX_CHECK(encoded_device.value().size() <= 1372U);
    auto decoded_device =
        iotox::person::decode_signed_group_device_message_envelope(
            encoded_device.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded_device.ok(), decoded_device.status().message());
    IOTOX_CHECK(iotox::person::verify_group_device_message(
                    decoded_device.value(), group.value(), delegation.value(),
                    sodium.value()).ok());
}

IOTOX_TEST("person contact book pins delivery-card floors and rejects forks") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto alice = keypair(sodium.value(), 0xB2U);
    TemporaryDirectory directory;
    const auto contacts = directory.root() / "contacts.store";

    auto roster = iotox::self_swarm::create_roster(
        alice.public_key(), member(sodium.value(), "phone", 0xB3U, 0xB4U));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), alice, sodium.value()).ok());
    auto card1 = signed_card(sodium.value(), alice, roster.value());
    auto entry1 =
        iotox::person::contact_entry_from_card("alice", card1, sodium.value());
    IOTOX_CHECK_MSG(entry1.ok(), entry1.status().message());
    auto committed1 =
        iotox::person::commit_contact_entry(contacts, entry1.value());
    IOTOX_CHECK_MSG(committed1.ok(), committed1.status().message());
    IOTOX_CHECK(committed1.value().generation == 1U);

    auto joined = iotox::self_swarm::add_member(
        roster.value(), member(sodium.value(), "laptop", 0xB5U, 0xB6U),
        sodium.value());
    IOTOX_CHECK_MSG(joined.ok(), joined.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    joined.value(), alice, sodium.value()).ok());
    auto card2 = signed_card(sodium.value(), alice, joined.value());
    auto entry2 =
        iotox::person::contact_entry_from_card("alice", card2, sodium.value());
    IOTOX_CHECK_MSG(entry2.ok(), entry2.status().message());
    auto committed2 =
        iotox::person::commit_contact_entry(contacts, entry2.value());
    IOTOX_CHECK_MSG(committed2.ok(), committed2.status().message());
    IOTOX_CHECK(committed2.value().generation == 2U);
    IOTOX_CHECK(committed2.value().routes.size() == 2U);

    IOTOX_CHECK(!iotox::person::commit_contact_entry(
                    contacts, entry1.value()).ok());

    iotox::person::DeliveryCard fork = card2;
    fork.routes.back() = public_key(sodium.value(), 0xB7U);
    std::sort(fork.routes.begin(), fork.routes.end());
    IOTOX_CHECK(iotox::person::sign_delivery_card(
                    fork, alice, sodium.value()).ok());
    auto fork_entry =
        iotox::person::contact_entry_from_card("alice", fork, sodium.value());
    IOTOX_CHECK_MSG(fork_entry.ok(), fork_entry.status().message());
    IOTOX_CHECK(!iotox::person::commit_contact_entry(
                    contacts, fork_entry.value()).ok());

    std::ostringstream noncanonical;
    noncanonical << "iotox-person-contact-book-v1\n"
                 << "contact-count=1\n"
                 << "contact=alice|" << iotox::security::hex(card2.person)
                 << '|' << card2.generation << '|'
                 << iotox::security::hex(entry2.value().card_digest) << '|'
                 << iotox::security::hex(card2.routes[1U]) << ','
                 << iotox::security::hex(card2.routes[0U]) << '\n';
    const std::string text = noncanonical.str();
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    directory.root() / "bad.contacts",
                    std::vector<std::uint8_t>(text.begin(), text.end())).ok());
    IOTOX_CHECK(!iotox::person::load_contact_book(
                    directory.root() / "bad.contacts").ok());

    auto loaded = iotox::person::load_contact_book(contacts);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    auto found = iotox::person::find_contact(loaded.value(), "alice");
    IOTOX_CHECK_MSG(found.ok(), found.status().message());
    IOTOX_CHECK(found.value() == committed2.value());
}

IOTOX_TEST("person transcript commits signed payloads and deduplicates locally") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto sender = keypair(sodium.value(), 0xC2U);
    auto recipient = keypair(sodium.value(), 0xC3U);
    TemporaryDirectory directory;
    const auto transcript = directory.root() / "messages.transcript";

    auto body = bytes("transcript hello");
    auto message = iotox::person::create_message_envelope(
        sender, recipient.public_key(), body, sodium.value());
    IOTOX_CHECK_MSG(message.ok(), message.status().message());
    auto payload =
        iotox::person::encode_signed_message_envelope(message.value());
    IOTOX_CHECK_MSG(payload.ok(), payload.status().message());
    auto entry = iotox::person::transcript_entry_from_payload(
        payload.value(), "out", sodium.value());
    IOTOX_CHECK_MSG(entry.ok(), entry.status().message());
    IOTOX_CHECK(entry.value().scope == "person");
    IOTOX_CHECK(entry.value().body == body);

    auto first =
        iotox::person::commit_transcript_entry(transcript, entry.value());
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(!first.value().duplicate);
    IOTOX_CHECK(first.value().entry.sequence == 1U);
    auto second =
        iotox::person::commit_transcript_entry(transcript, entry.value());
    IOTOX_CHECK_MSG(second.ok(), second.status().message());
    IOTOX_CHECK(second.value().duplicate);
    IOTOX_CHECK(second.value().entries == 1U);

    auto group = iotox::person::create_group_descriptor(
        sender, bytes("ops"),
        std::vector<iotox::security::SigningPublicKey>{
            recipient.public_key()},
        sodium.value());
    IOTOX_CHECK_MSG(group.ok(), group.status().message());
    auto group_message = iotox::person::create_group_message_envelope(
        sender, group.value(), bytes("group transcript"), sodium.value());
    IOTOX_CHECK_MSG(group_message.ok(), group_message.status().message());
    auto group_payload =
        iotox::person::encode_signed_group_message_envelope(
            group_message.value());
    IOTOX_CHECK_MSG(group_payload.ok(), group_payload.status().message());
    auto group_entry = iotox::person::transcript_entry_from_payload(
        group_payload.value(), "in", sodium.value());
    IOTOX_CHECK_MSG(group_entry.ok(), group_entry.status().message());
    auto third =
        iotox::person::commit_transcript_entry(transcript, group_entry.value());
    IOTOX_CHECK_MSG(third.ok(), third.status().message());
    IOTOX_CHECK(!third.value().duplicate);
    IOTOX_CHECK(third.value().entry.sequence == 2U);

    auto loaded = iotox::person::load_transcript_store(transcript);
    IOTOX_CHECK_MSG(loaded.ok(), loaded.status().message());
    IOTOX_CHECK(loaded.value().entries.size() == 2U);
    IOTOX_CHECK(loaded.value().next_sequence == 3U);
    IOTOX_CHECK(iotox::person::render_transcript_store(loaded.value()).find(
                    "not-consensus-or-all-device-delivery-proof") !=
                std::string::npos);
}

IOTOX_TEST("person receipts and outbox bind messenger delivery accounting") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xD2U);
    auto friend_person = keypair(sodium.value(), 0xD3U);
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::self_swarm::Member desktop =
        member(sodium.value(), "desktop", 0xD4U, 0xD5U);
    desktop.principal = identity.value().public_key();
    auto owner_roster = iotox::self_swarm::create_roster(
        owner.public_key(), std::move(desktop));
    IOTOX_CHECK_MSG(owner_roster.ok(), owner_roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    owner_roster.value(), owner, sodium.value()).ok());
    auto owner_delegation = iotox::person::sender_delegation_from_roster(
        owner_roster.value(), "desktop", sodium.value());
    IOTOX_CHECK_MSG(owner_delegation.ok(),
                    owner_delegation.status().message());
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    owner_delegation.value(), owner, sodium.value()).ok());

    auto inbound = iotox::person::create_message_envelope(
        friend_person, owner.public_key(), bytes("received by one device"),
        sodium.value());
    IOTOX_CHECK_MSG(inbound.ok(), inbound.status().message());
    auto inbound_payload =
        iotox::person::encode_signed_message_envelope(inbound.value());
    IOTOX_CHECK_MSG(inbound_payload.ok(), inbound_payload.status().message());
    auto receipt = iotox::person::create_receipt_record(
        identity.value(), owner_delegation.value(), inbound_payload.value(),
        123456U, sodium.value());
    IOTOX_CHECK_MSG(receipt.ok(), receipt.status().message());
    IOTOX_CHECK(iotox::person::verify_receipt_record(
                    receipt.value(), owner_delegation.value(),
                    sodium.value()).ok());
    const auto receipt_path = directory.root() / "message.receipt";
    IOTOX_CHECK(iotox::person::create_receipt_record_file(
                    receipt_path, receipt.value()).ok());
    auto loaded_receipt =
        iotox::person::load_receipt_record(receipt_path, sodium.value());
    IOTOX_CHECK_MSG(loaded_receipt.ok(),
                    loaded_receipt.status().message());
    IOTOX_CHECK(loaded_receipt.value() == receipt.value());
    const auto receipt_store_path = directory.root() / "receipts.store";
    auto receipt_commit = iotox::person::commit_receipt_record(
        receipt_store_path, receipt.value(), sodium.value());
    IOTOX_CHECK_MSG(receipt_commit.ok(),
                    receipt_commit.status().message());
    IOTOX_CHECK(!receipt_commit.value().duplicate);
    IOTOX_CHECK(receipt_commit.value().receipts == 1U);
    auto receipt_duplicate = iotox::person::commit_receipt_record(
        receipt_store_path, receipt.value(), sodium.value());
    IOTOX_CHECK_MSG(receipt_duplicate.ok(),
                    receipt_duplicate.status().message());
    IOTOX_CHECK(receipt_duplicate.value().duplicate);
    IOTOX_CHECK(receipt_duplicate.value().receipts == 1U);
    auto loaded_receipt_store =
        iotox::person::load_receipt_store(receipt_store_path, sodium.value());
    IOTOX_CHECK_MSG(loaded_receipt_store.ok(),
                    loaded_receipt_store.status().message());
    IOTOX_CHECK(loaded_receipt_store.value().receipts.size() == 1U);
    IOTOX_CHECK(iotox::person::render_receipt_store(
                    loaded_receipt_store.value()).find(
                    "content-free-device-receipt-rollup") !=
                std::string::npos);

    auto wrong_delegation = owner_delegation.value();
    wrong_delegation.person = friend_person.public_key();
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    wrong_delegation, friend_person, sodium.value()).ok());
    IOTOX_CHECK(!iotox::person::verify_receipt_record(
                    receipt.value(), wrong_delegation, sodium.value()).ok());

    auto friend_roster = iotox::self_swarm::create_roster(
        friend_person.public_key(),
        member(sodium.value(), "phone", 0xD6U, 0xD7U));
    IOTOX_CHECK_MSG(friend_roster.ok(), friend_roster.status().message());
    auto friend_joined = iotox::self_swarm::add_member(
        friend_roster.value(), member(sodium.value(), "laptop", 0xD8U, 0xD9U),
        sodium.value());
    IOTOX_CHECK_MSG(friend_joined.ok(), friend_joined.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    friend_joined.value(), friend_person, sodium.value()).ok());
    auto friend_card =
        signed_card(sodium.value(), friend_person, friend_joined.value());
    auto outbound = iotox::person::create_message_envelope(
        owner, friend_person.public_key(), bytes("queued for all routes"),
        sodium.value());
    IOTOX_CHECK_MSG(outbound.ok(), outbound.status().message());
    auto outbound_payload =
        iotox::person::encode_signed_message_envelope(outbound.value());
    IOTOX_CHECK_MSG(outbound_payload.ok(), outbound_payload.status().message());
    auto item = iotox::person::outbox_item_from_card(
        friend_card, outbound_payload.value(), sodium.value());
    IOTOX_CHECK_MSG(item.ok(), item.status().message());
    item.value().created_unix_ms = 1U;
    IOTOX_CHECK(item.value().pending_routes.size() == 2U);
    IOTOX_CHECK(item.value().sent_routes.empty());

    const auto outbox_path = directory.root() / "outbox.store";
    auto committed =
        iotox::person::commit_outbox_item(outbox_path, item.value());
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    IOTOX_CHECK(committed.value() == item.value());
    auto attempted = iotox::person::record_outbox_attempt(
        outbox_path, item.value().message_id, 2000U);
    IOTOX_CHECK_MSG(attempted.ok(), attempted.status().message());
    IOTOX_CHECK(attempted.value().attempts == 1U);
    IOTOX_CHECK(attempted.value().last_attempt_unix_ms == 2000U);
    auto marked = iotox::person::mark_outbox_route_sent(
        outbox_path, item.value().message_id, item.value().pending_routes[0U]);
    IOTOX_CHECK_MSG(marked.ok(), marked.status().message());
    IOTOX_CHECK(marked.value().pending_routes.size() == 1U);
    IOTOX_CHECK(marked.value().sent_routes.size() == 1U);
    IOTOX_CHECK(marked.value().attempts == 1U);
    auto marked_again = iotox::person::mark_outbox_route_sent(
        outbox_path, item.value().message_id, item.value().pending_routes[0U]);
    IOTOX_CHECK_MSG(marked_again.ok(), marked_again.status().message());
    IOTOX_CHECK(marked_again.value() == marked.value());
    auto loaded_outbox = iotox::person::load_outbox_store(outbox_path);
    IOTOX_CHECK_MSG(loaded_outbox.ok(), loaded_outbox.status().message());
    IOTOX_CHECK(loaded_outbox.value().items.size() == 1U);
    IOTOX_CHECK(iotox::person::render_outbox_store(
                    loaded_outbox.value()).find(
                    "native-background-retry-and-dead-letter-expiration-available") !=
                std::string::npos);
    const auto dead_letter_path = directory.root() / "dead-letter.outbox";
    auto expired = iotox::person::expire_outbox_items(
        outbox_path, dead_letter_path, 8U * 24U * 60U * 60U * 1000U,
        7U * 24U * 60U * 60U);
    IOTOX_CHECK_MSG(expired.ok(), expired.status().message());
    IOTOX_CHECK(expired.value().expired == 1U);
    IOTOX_CHECK(expired.value().dead_letter_items == 1U);
    auto source_after_expire = iotox::person::load_outbox_store(outbox_path);
    IOTOX_CHECK_MSG(source_after_expire.ok(),
                    source_after_expire.status().message());
    IOTOX_CHECK(source_after_expire.value().items.empty());
    auto dead_letter = iotox::person::load_outbox_store(dead_letter_path);
    IOTOX_CHECK_MSG(dead_letter.ok(), dead_letter.status().message());
    IOTOX_CHECK(dead_letter.value().items.size() == 1U);
    IOTOX_CHECK(dead_letter.value().items[0U].pending_routes.size() == 1U);
}

IOTOX_TEST("person Tox bridge signs normal Tox observations without person identity confusion") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    auto owner = keypair(sodium.value(), 0xE2U);
    auto stranger = keypair(sodium.value(), 0xE3U);
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "bridge-device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());

    iotox::self_swarm::Member desktop =
        member(sodium.value(), "desktop", 0xE4U, 0xE5U);
    desktop.principal = identity.value().public_key();
    auto roster = iotox::self_swarm::create_roster(
        owner.public_key(), std::move(desktop));
    IOTOX_CHECK_MSG(roster.ok(), roster.status().message());
    IOTOX_CHECK(iotox::self_swarm::sign_roster(
                    roster.value(), owner, sodium.value()).ok());
    auto delegation = iotox::person::sender_delegation_from_roster(
        roster.value(), "desktop", sodium.value());
    IOTOX_CHECK_MSG(delegation.ok(), delegation.status().message());
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    delegation.value(), owner, sodium.value()).ok());

    iotox::person::ToxPublicKey external{};
    external.fill(0xEFU);
    external[0U] = 0x42U;
    auto bridge = iotox::person::create_tox_bridge_message_envelope(
        identity.value(), delegation.value(), "in", "message", external,
        bytes("hello from normal tox"), 123456789U, sodium.value());
    IOTOX_CHECK_MSG(bridge.ok(), bridge.status().message());
    IOTOX_CHECK(bridge.value().observer_person == owner.public_key());
    IOTOX_CHECK(bridge.value().external_tox_key == external);
    auto encoded =
        iotox::person::encode_signed_tox_bridge_message_envelope(
            bridge.value());
    IOTOX_CHECK_MSG(encoded.ok(), encoded.status().message());
    IOTOX_CHECK(encoded.value().size() < iotox::toxcore::abi::kMaxMessageLength);
    auto decoded =
        iotox::person::decode_signed_tox_bridge_message_envelope(
            encoded.value(), sodium.value());
    IOTOX_CHECK_MSG(decoded.ok(), decoded.status().message());
    IOTOX_CHECK(decoded.value() == bridge.value());
    IOTOX_CHECK(iotox::person::verify_tox_bridge_message_delegation(
                    decoded.value(), delegation.value(), sodium.value()).ok());

    auto wrong_delegation = delegation.value();
    wrong_delegation.person = stranger.public_key();
    IOTOX_CHECK(iotox::person::sign_sender_delegation(
                    wrong_delegation, stranger, sodium.value()).ok());
    IOTOX_CHECK(!iotox::person::verify_tox_bridge_message_delegation(
                    decoded.value(), wrong_delegation, sodium.value()).ok());

    auto tampered = encoded.value();
    tampered[tampered.size() - 20U] ^= 0x01U;
    IOTOX_CHECK(!iotox::person::decode_signed_tox_bridge_message_envelope(
                    tampered, sodium.value()).ok());

    auto entry = iotox::person::tox_bridge_entry_from_payload(
        encoded.value(), delegation.value(), sodium.value());
    IOTOX_CHECK_MSG(entry.ok(), entry.status().message());
    IOTOX_CHECK(entry.value().direction == "in");
    IOTOX_CHECK(entry.value().tox_kind == "message");
    IOTOX_CHECK(entry.value().body == bytes("hello from normal tox"));
    const auto store_path = directory.root() / "tox.bridge";
    auto committed =
        iotox::person::commit_tox_bridge_entry(store_path, entry.value());
    IOTOX_CHECK_MSG(committed.ok(), committed.status().message());
    IOTOX_CHECK(!committed.value().duplicate);
    auto duplicate =
        iotox::person::commit_tox_bridge_entry(store_path, entry.value());
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK(duplicate.value().duplicate);
    auto store = iotox::person::load_tox_bridge_store(store_path);
    IOTOX_CHECK_MSG(store.ok(), store.status().message());
    IOTOX_CHECK(store.value().entries.size() == 1U);
    IOTOX_CHECK(iotox::person::render_tox_bridge_store(store.value()).find(
                    "external-tox-keys-are-not-iotox-person-identities") !=
                std::string::npos);
}
