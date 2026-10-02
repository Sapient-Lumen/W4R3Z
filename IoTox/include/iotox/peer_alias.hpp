#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <map>
#include <memory>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::peer_alias {

inline constexpr std::size_t kPublicKeyBytes = 32U;
inline constexpr std::size_t kMaximumNameBytes = 63U;
inline constexpr std::size_t kMaximumAliases = 256U;

using PublicKey = std::array<std::uint8_t, kPublicKeyBytes>;

struct Entry {
    std::string name;
    PublicKey public_key{};

    [[nodiscard]] bool operator==(const Entry &) const = default;
};

struct Snapshot {
    std::uint64_t generation{0U};
    std::vector<Entry> entries;
};

struct Mutation {
    Snapshot snapshot;
    bool changed{false};
};

enum class SelectorKind : std::uint8_t {
    friend_number = 1U,
    public_key = 2U,
    alias = 3U,
};

struct Selector {
    SelectorKind kind{SelectorKind::alias};
    std::uint32_t friend_number{0U};
    PublicKey public_key{};
    std::string alias;
};

[[nodiscard]] Status validate_name(std::string_view name);
// Bare compatibility order is uint32 friend number, exact 64-hex key, then
// canonical alias. Explicit friend:/key:/alias: forms are never ambiguous.
[[nodiscard]] Result<Selector> parse_selector(std::string_view text);

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_name_request(
    std::string_view name);
[[nodiscard]] Result<std::string> decode_name_request(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_set_request(
    std::string_view name, const PublicKey &public_key);
[[nodiscard]] Result<Entry> decode_set_request(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<std::vector<std::uint8_t>> encode_rename_request(
    std::string_view old_name, std::string_view new_name);
[[nodiscard]] Result<std::pair<std::string, std::string>>
decode_rename_request(std::span<const std::uint8_t> bytes);

class Store {
  public:
    struct Config {
        std::filesystem::path path;
    };

    [[nodiscard]] static Result<std::unique_ptr<Store>> open(
        Config config, const security::DeviceIdentity &identity,
        const security::Sodium &sodium);

    [[nodiscard]] Snapshot snapshot() const;
    [[nodiscard]] Result<PublicKey> resolve(std::string_view name) const;
    [[nodiscard]] Result<Mutation> set(
        std::string_view name, const PublicKey &public_key);
    [[nodiscard]] Result<Mutation> rename(
        std::string_view old_name, std::string_view new_name);
    [[nodiscard]] Result<Mutation> remove(std::string_view name);

  private:
    Store(Config config, const security::DeviceIdentity &identity,
          const security::Sodium &sodium, Snapshot state);

    [[nodiscard]] Result<Mutation> commit(
        std::map<std::string, PublicKey> next);

    Config config_;
    const security::DeviceIdentity *identity_{nullptr};
    const security::Sodium *sodium_{nullptr};
    mutable std::mutex mutex_;
    Snapshot state_;
    std::map<std::string, PublicKey> aliases_;
};

[[nodiscard]] std::string render_snapshot(const Snapshot &snapshot);
[[nodiscard]] std::string render_mutation(
    std::string_view operation, std::string_view name,
    const Mutation &mutation);
[[nodiscard]] std::filesystem::path default_store_path(
    const std::filesystem::path &tox_savedata_path);

}  // namespace iotox::peer_alias
