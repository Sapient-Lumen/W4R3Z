#include "test_harness.hpp"

#include "iotox/peer_alias.hpp"
#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"

#include <filesystem>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

class TemporaryDirectory {
  public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/iotox-peer-alias-XXXXXX";
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

iotox::peer_alias::PublicKey key(std::uint8_t first) {
    iotox::peer_alias::PublicKey result{};
    result.front() = first;
    result.back() = static_cast<std::uint8_t>(first + 1U);
    return result;
}

}  // namespace

IOTOX_TEST("peer alias selectors and request codecs are unambiguous") {
    using iotox::peer_alias::SelectorKind;
    const auto public_key = key(7U);
    const std::string encoded = iotox::security::hex(public_key);
    auto numeric = iotox::peer_alias::parse_selector("17");
    auto explicit_numeric = iotox::peer_alias::parse_selector("friend:17");
    auto hex = iotox::peer_alias::parse_selector(encoded);
    auto explicit_hex = iotox::peer_alias::parse_selector("key:" + encoded);
    auto alias = iotox::peer_alias::parse_selector("workstation");
    auto explicit_alias =
        iotox::peer_alias::parse_selector("alias:workstation");
    IOTOX_CHECK(numeric.ok() && explicit_numeric.ok());
    IOTOX_CHECK(numeric.value().kind == SelectorKind::friend_number &&
                numeric.value().friend_number == 17U);
    IOTOX_CHECK(explicit_numeric.value().friend_number == 17U);
    IOTOX_CHECK(hex.ok() && explicit_hex.ok() &&
                hex.value().kind == SelectorKind::public_key &&
                hex.value().public_key == public_key &&
                explicit_hex.value().public_key == public_key);
    IOTOX_CHECK(alias.ok() && explicit_alias.ok() &&
                alias.value().kind == SelectorKind::alias &&
                alias.value().alias == "workstation" &&
                explicit_alias.value().alias == "workstation");
    IOTOX_CHECK(!iotox::peer_alias::parse_selector("Workstation").ok());
    IOTOX_CHECK(!iotox::peer_alias::parse_selector("alias:17").ok());
    IOTOX_CHECK(!iotox::peer_alias::parse_selector("friend:nope").ok());
    IOTOX_CHECK(!iotox::peer_alias::parse_selector(
                    "key:" + std::string(64U, '0')).ok());

    auto set = iotox::peer_alias::encode_set_request("workstation", public_key);
    IOTOX_CHECK(set.ok());
    auto decoded_set = iotox::peer_alias::decode_set_request(set.value());
    IOTOX_CHECK(decoded_set.ok() &&
                decoded_set.value().name == "workstation" &&
                decoded_set.value().public_key == public_key);
    set.value().push_back(0U);
    IOTOX_CHECK(!iotox::peer_alias::decode_set_request(set.value()).ok());
    auto rename = iotox::peer_alias::encode_rename_request(
        "workstation", "laptop");
    auto decoded_rename = rename
        ? iotox::peer_alias::decode_rename_request(rename.value())
        : iotox::Result<std::pair<std::string, std::string>>{
              rename.status()};
    IOTOX_CHECK(decoded_rename.ok() &&
                decoded_rename.value().first == "workstation" &&
                decoded_rename.value().second == "laptop");
}

IOTOX_TEST("peer alias store signs one-to-one explicit lifecycle") {
    auto sodium = iotox::security::Sodium::load();
    IOTOX_CHECK_MSG(sodium.ok(), sodium.status().message());
    TemporaryDirectory directory;
    auto identity = iotox::security::DeviceIdentity::load_or_create(
        directory.root() / "device.identity", sodium.value(), true);
    IOTOX_CHECK_MSG(identity.ok(), identity.status().message());
    iotox::peer_alias::Store::Config config;
    config.path = directory.root() / "aliases.store";
    auto store = iotox::peer_alias::Store::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(store.ok());
    const auto first_key = key(1U);
    const auto second_key = key(2U);
    auto first = store.value()->set("workstation", first_key);
    IOTOX_CHECK(first.ok() && first.value().changed &&
                first.value().snapshot.generation == 1U);
    auto retry = store.value()->set("workstation", first_key);
    IOTOX_CHECK(retry.ok() && !retry.value().changed &&
                retry.value().snapshot.generation == 1U);
    IOTOX_CHECK(!store.value()->set("laptop", first_key).ok());
    IOTOX_CHECK(!store.value()->set("workstation", second_key).ok());
    auto second = store.value()->set("laptop", second_key);
    IOTOX_CHECK(second.ok() && second.value().snapshot.generation == 2U);
    IOTOX_CHECK(!store.value()->rename("workstation", "laptop").ok());
    auto renamed = store.value()->rename("workstation", "desktop");
    IOTOX_CHECK(renamed.ok() && renamed.value().changed &&
                renamed.value().snapshot.generation == 3U &&
                store.value()->resolve("desktop").value() == first_key &&
                !store.value()->resolve("workstation").ok());
    auto removed = store.value()->remove("desktop");
    auto removed_retry = store.value()->remove("desktop");
    IOTOX_CHECK(removed.ok() && removed.value().changed &&
                removed.value().snapshot.generation == 4U &&
                removed_retry.ok() && !removed_retry.value().changed &&
                removed_retry.value().snapshot.generation == 4U);

    auto reopened = iotox::peer_alias::Store::open(
        config, identity.value(), sodium.value());
    IOTOX_CHECK(reopened.ok() &&
                reopened.value()->snapshot().entries.size() == 1U &&
                reopened.value()->resolve("laptop").value() == second_key);
    struct stat metadata {};
    IOTOX_CHECK(::lstat(config.path.c_str(), &metadata) == 0 &&
                S_ISREG(metadata.st_mode) && metadata.st_nlink == 1 &&
                (metadata.st_mode & 0777U) == 0600U);

    auto bytes = iotox::StateStore::read(config.path);
    IOTOX_CHECK(bytes.ok() && bytes.value().size() > 82U);
    bytes.value()[20U] ^= 0x01U;
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    config.path, bytes.value()).ok());
    IOTOX_CHECK(!iotox::peer_alias::Store::open(
                     config, identity.value(), sodium.value()).ok());
}
