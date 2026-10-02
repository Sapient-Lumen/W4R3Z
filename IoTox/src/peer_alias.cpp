#include "iotox/peer_alias.hpp"

#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstring>
#include <fcntl.h>
#include <iomanip>
#include <limits>
#include <sstream>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>

namespace iotox::peer_alias {
namespace {

constexpr std::array<std::uint8_t, 8U> kMagic{
    'I', 'O', 'T', 'X', 'A', 'L', 'S', '1'};
constexpr std::size_t kHeaderBytes = 18U;
constexpr std::string_view kDomain = "peer-alias-store-v1";

class FileDescriptor {
  public:
    explicit FileDescriptor(int value) : value_(value) {}
    ~FileDescriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    [[nodiscard]] int get() const noexcept { return value_; }
  private:
    int value_{-1};
};

void append_u16(std::vector<std::uint8_t> &output, std::uint16_t value) {
    output.push_back(static_cast<std::uint8_t>(value >> 8U));
    output.push_back(static_cast<std::uint8_t>(value));
}

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        output.push_back(static_cast<std::uint8_t>(
            value >> static_cast<unsigned>(shift)));
    }
}

[[nodiscard]] std::uint16_t read_u16(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    return static_cast<std::uint16_t>(
        (static_cast<std::uint16_t>(bytes[offset]) << 8U) |
        bytes[offset + 1U]);
}

[[nodiscard]] std::uint64_t read_u64(
    std::span<const std::uint8_t> bytes, std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[offset + index];
    }
    return value;
}

[[nodiscard]] bool nonzero_key(const PublicKey &key) noexcept {
    return std::any_of(key.begin(), key.end(), [](std::uint8_t byte) {
        return byte != 0U;
    });
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_unsigned(
    const Snapshot &snapshot) {
    if (snapshot.entries.size() > kMaximumAliases ||
        (!snapshot.entries.empty() && snapshot.generation == 0U) ||
        snapshot.entries.size() > std::numeric_limits<std::uint16_t>::max()) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias snapshot exceeds its entry bound"};
    }
    std::vector<std::uint8_t> output;
    output.reserve(kHeaderBytes + snapshot.entries.size() * 64U);
    output.insert(output.end(), kMagic.begin(), kMagic.end());
    append_u64(output, snapshot.generation);
    append_u16(output,
               static_cast<std::uint16_t>(snapshot.entries.size()));
    std::string previous;
    std::vector<PublicKey> seen_keys;
    seen_keys.reserve(snapshot.entries.size());
    for (const Entry &entry : snapshot.entries) {
        const Status valid = validate_name(entry.name);
        if (!valid.ok() || !nonzero_key(entry.public_key) ||
            (!previous.empty() && entry.name <= previous) ||
            std::find(seen_keys.begin(), seen_keys.end(), entry.public_key) !=
                seen_keys.end()) {
            return Status{ErrorCode::invalid_argument,
                          "peer alias snapshot is not canonical and one-to-one"};
        }
        output.push_back(static_cast<std::uint8_t>(entry.name.size()));
        output.insert(output.end(), entry.name.begin(), entry.name.end());
        output.insert(output.end(), entry.public_key.begin(),
                      entry.public_key.end());
        previous = entry.name;
        seen_keys.push_back(entry.public_key);
    }
    return output;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_signed(
    const Snapshot &snapshot, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    auto bytes = encode_unsigned(snapshot);
    if (!bytes) return bytes.status();
    auto digest = sodium.hash(kDomain, bytes.value());
    if (!digest) return digest.status();
    auto signature = identity.sign(digest.value());
    if (!signature) return signature.status();
    bytes.value().insert(bytes.value().end(), signature.value().begin(),
                         signature.value().end());
    return bytes;
}

[[nodiscard]] Result<Snapshot> decode_signed(
    std::span<const std::uint8_t> bytes,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium) {
    if (bytes.size() < kHeaderBytes + security::kSignatureBytes ||
        !std::equal(kMagic.begin(), kMagic.end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "peer alias store header or size is invalid"};
    }
    const std::size_t unsigned_size =
        bytes.size() - security::kSignatureBytes;
    const auto unsigned_bytes = bytes.first(unsigned_size);
    auto digest = sodium.hash(kDomain, unsigned_bytes);
    if (!digest) return digest.status();
    security::Signature signature{};
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(unsigned_size),
                signature.size(), signature.begin());
    const Status verified = sodium.verify_detached(
        signature, digest.value(), expected_device);
    if (!verified.ok()) {
        return Status{ErrorCode::protocol_error,
                      "peer alias store signature is invalid"};
    }
    Snapshot snapshot;
    snapshot.generation = read_u64(bytes, 8U);
    const std::size_t count = read_u16(bytes, 16U);
    if (count > kMaximumAliases) {
        return Status{ErrorCode::protocol_error,
                      "peer alias store count exceeds its bound"};
    }
    std::size_t offset = kHeaderBytes;
    snapshot.entries.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        if (offset >= unsigned_size) {
            return Status{ErrorCode::protocol_error,
                          "peer alias store entry is truncated"};
        }
        const std::size_t name_size = bytes[offset++];
        if (name_size == 0U || name_size > kMaximumNameBytes ||
            name_size + kPublicKeyBytes > unsigned_size - offset) {
            return Status{ErrorCode::protocol_error,
                          "peer alias store entry length is invalid"};
        }
        Entry entry;
        entry.name.assign(
            reinterpret_cast<const char *>(bytes.data() + offset),
            name_size);
        offset += name_size;
        std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                    entry.public_key.size(), entry.public_key.begin());
        offset += entry.public_key.size();
        snapshot.entries.push_back(std::move(entry));
    }
    if (offset != unsigned_size) {
        return Status{ErrorCode::protocol_error,
                      "peer alias store has trailing bytes"};
    }
    auto canonical = encode_unsigned(snapshot);
    if (!canonical || canonical.value().size() != unsigned_size ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    unsigned_bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "peer alias store bytes are noncanonical"};
    }
    return snapshot;
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_private(
    const std::filesystem::path &path) {
    int opened = -1;
    do {
        opened = ::open(path.c_str(),
                        O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    } while (opened < 0 && errno == EINTR);
    if (opened < 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          "peer alias store does not exist"};
        }
        return Status{ErrorCode::io_error,
                      "unable to open peer alias store: " +
                          std::string(std::strerror(errno))};
    }
    FileDescriptor descriptor(opened);
    struct stat before {};
    const std::size_t maximum = kHeaderBytes +
        kMaximumAliases * (1U + kMaximumNameBytes + kPublicKeyBytes) +
        security::kSignatureBytes;
    if (::fstat(descriptor.get(), &before) != 0 ||
        !S_ISREG(before.st_mode) || before.st_nlink != 1 ||
        before.st_uid != ::geteuid() ||
        (before.st_mode & S_IRUSR) == 0U ||
        (before.st_mode & (S_IRWXG | S_IRWXO)) != 0U ||
        before.st_size < 0 ||
        static_cast<std::uint64_t>(before.st_size) > maximum) {
        return Status{ErrorCode::io_error,
                      "peer alias store is not one bounded owner-private regular file"};
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(before.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor.get(), bytes.data() + offset, bytes.size() - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            return Status{ErrorCode::io_error,
                          "peer alias store changed or ended during read"};
        }
        offset += static_cast<std::size_t>(count);
    }
    struct stat after {};
    if (::fstat(descriptor.get(), &after) != 0 ||
        before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
        before.st_mode != after.st_mode || before.st_nlink != after.st_nlink ||
        before.st_uid != after.st_uid || before.st_size != after.st_size ||
        before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
        before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
        before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
        before.st_ctim.tv_nsec != after.st_ctim.tv_nsec) {
        return Status{ErrorCode::io_error,
                      "peer alias store changed while it was read"};
    }
    return bytes;
}

[[nodiscard]] Result<std::uint32_t> parse_friend_number(
    std::string_view text) {
    if (text.empty() || text.front() == '-') {
        return Status{ErrorCode::invalid_argument,
                      "friend selector must contain decimal digits"};
    }
    std::uint64_t value = 0U;
    const auto parsed = std::from_chars(
        text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != text.data() + text.size() ||
        value > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::invalid_argument,
                      "friend selector is not one uint32 number"};
    }
    return static_cast<std::uint32_t>(value);
}

[[nodiscard]] Result<PublicKey> parse_key(std::string_view text) {
    auto decoded = security::decode_hex_exact(
        text, kPublicKeyBytes, "peer public key selector");
    if (!decoded) return decoded.status();
    PublicKey key{};
    std::copy(decoded.value().begin(), decoded.value().end(), key.begin());
    if (!nonzero_key(key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer public key selector cannot be all zero"};
    }
    return key;
}

}  // namespace

Status validate_name(std::string_view name) {
    if (name.empty() || name.size() > kMaximumNameBytes ||
        name.front() < 'a' || name.front() > 'z') {
        return Status{ErrorCode::invalid_argument,
                      "peer alias must be 1..63 bytes and begin with a-z"};
    }
    for (const char character : name) {
        const bool valid =
            (character >= 'a' && character <= 'z') ||
            (character >= '0' && character <= '9') || character == '-' ||
            character == '_' || character == '.';
        if (!valid) {
            return Status{ErrorCode::invalid_argument,
                          "peer alias accepts only lowercase a-z, 0-9, dot, underscore, and hyphen"};
        }
    }
    return Status::success();
}

Result<Selector> parse_selector(std::string_view text) {
    if (text.starts_with("friend:")) {
        auto number = parse_friend_number(text.substr(7U));
        if (!number) return number.status();
        Selector result;
        result.kind = SelectorKind::friend_number;
        result.friend_number = number.value();
        return result;
    }
    if (text.starts_with("key:")) {
        auto key = parse_key(text.substr(4U));
        if (!key) return key.status();
        Selector result;
        result.kind = SelectorKind::public_key;
        result.public_key = key.value();
        return result;
    }
    if (text.starts_with("alias:")) {
        const std::string_view name = text.substr(6U);
        const Status valid = validate_name(name);
        if (!valid.ok()) return valid;
        Selector result;
        result.kind = SelectorKind::alias;
        result.alias = name;
        return result;
    }
    auto number = parse_friend_number(text);
    if (number) {
        Selector result;
        result.kind = SelectorKind::friend_number;
        result.friend_number = number.value();
        return result;
    }
    if (text.size() == kPublicKeyBytes * 2U) {
        auto key = parse_key(text);
        if (key) {
            Selector result;
            result.kind = SelectorKind::public_key;
            result.public_key = key.value();
            return result;
        }
    }
    const Status valid = validate_name(text);
    if (!valid.ok()) {
        return Status{ErrorCode::invalid_argument,
                      "peer selector must be friend:N, key:64HEX, alias:NAME, bare uint32, bare 64-hex, or a canonical alias"};
    }
    Selector result;
    result.kind = SelectorKind::alias;
    result.alias = text;
    return result;
}

Result<std::vector<std::uint8_t>> encode_name_request(
    std::string_view name) {
    const Status valid = validate_name(name);
    if (!valid.ok()) return valid;
    std::vector<std::uint8_t> output;
    output.reserve(1U + name.size());
    output.push_back(static_cast<std::uint8_t>(name.size()));
    for (const char byte : name) {
        output.push_back(static_cast<std::uint8_t>(byte));
    }
    return output;
}

Result<std::string> decode_name_request(
    std::span<const std::uint8_t> bytes) {
    if (bytes.empty() || bytes.front() == 0U ||
        bytes.front() > kMaximumNameBytes ||
        bytes.size() != 1U + bytes.front()) {
        return Status{ErrorCode::protocol_error,
                      "peer alias name request is noncanonical"};
    }
    std::string name(
        reinterpret_cast<const char *>(bytes.data() + 1U), bytes.front());
    const Status valid = validate_name(name);
    if (!valid.ok()) return valid;
    return name;
}

Result<std::vector<std::uint8_t>> encode_set_request(
    std::string_view name, const PublicKey &public_key) {
    auto output = encode_name_request(name);
    if (!output) return output.status();
    if (!nonzero_key(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias public key cannot be all zero"};
    }
    output.value().insert(output.value().end(), public_key.begin(),
                          public_key.end());
    return output;
}

Result<Entry> decode_set_request(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < 1U + kPublicKeyBytes) {
        return Status{ErrorCode::protocol_error,
                      "peer alias set request is truncated"};
    }
    const std::size_t name_bytes = 1U + bytes.front();
    if (name_bytes + kPublicKeyBytes != bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "peer alias set request length is noncanonical"};
    }
    auto name = decode_name_request(bytes.first(name_bytes));
    if (!name) return name.status();
    Entry entry;
    entry.name = std::move(name).value();
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(name_bytes),
                entry.public_key.size(), entry.public_key.begin());
    if (!nonzero_key(entry.public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias public key cannot be all zero"};
    }
    return entry;
}

Result<std::vector<std::uint8_t>> encode_rename_request(
    std::string_view old_name, std::string_view new_name) {
    auto old_bytes = encode_name_request(old_name);
    if (!old_bytes) return old_bytes.status();
    auto new_bytes = encode_name_request(new_name);
    if (!new_bytes) return new_bytes.status();
    old_bytes.value().insert(old_bytes.value().end(),
                             new_bytes.value().begin(),
                             new_bytes.value().end());
    return old_bytes;
}

Result<std::pair<std::string, std::string>> decode_rename_request(
    std::span<const std::uint8_t> bytes) {
    if (bytes.empty()) {
        return Status{ErrorCode::protocol_error,
                      "peer alias rename request is empty"};
    }
    const std::size_t old_size = 1U + bytes.front();
    if (old_size >= bytes.size()) {
        return Status{ErrorCode::protocol_error,
                      "peer alias rename request is truncated"};
    }
    auto old_name = decode_name_request(bytes.first(old_size));
    auto new_name = decode_name_request(bytes.subspan(old_size));
    if (!old_name) return old_name.status();
    if (!new_name) return new_name.status();
    return std::pair<std::string, std::string>{
        std::move(old_name).value(), std::move(new_name).value()};
}

Store::Store(Config config, const security::DeviceIdentity &identity,
             const security::Sodium &sodium, Snapshot state)
    : config_(std::move(config)), identity_(&identity), sodium_(&sodium),
      state_(std::move(state)) {
    for (const Entry &entry : state_.entries) {
        aliases_.emplace(entry.name, entry.public_key);
    }
}

Result<std::unique_ptr<Store>> Store::open(
    Config config, const security::DeviceIdentity &identity,
    const security::Sodium &sodium) {
    if (config.path.empty() || !config.path.is_absolute() ||
        config.path == config.path.root_path() ||
        config.path.lexically_normal() != config.path) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias store requires one normalized absolute path"};
    }
    Snapshot state;
    auto bytes = read_private(config.path);
    if (bytes) {
        auto decoded = decode_signed(
            bytes.value(), identity.public_key(), sodium);
        if (!decoded) return decoded.status();
        state = std::move(decoded).value();
    } else if (bytes.status().code() != ErrorCode::not_found) {
        return bytes.status();
    }
    return std::unique_ptr<Store>(new Store(
        std::move(config), identity, sodium, std::move(state)));
}

Snapshot Store::snapshot() const {
    std::scoped_lock lock(mutex_);
    return state_;
}

Result<PublicKey> Store::resolve(std::string_view name) const {
    const Status valid = validate_name(name);
    if (!valid.ok()) return valid;
    std::scoped_lock lock(mutex_);
    const auto found = aliases_.find(std::string(name));
    if (found == aliases_.end()) {
        return Status{ErrorCode::not_found,
                      "peer alias is not bound: " + std::string(name)};
    }
    return found->second;
}

Result<Mutation> Store::commit(std::map<std::string, PublicKey> next) {
    if (state_.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "peer alias generation is exhausted"};
    }
    Snapshot snapshot;
    snapshot.generation = state_.generation + 1U;
    snapshot.entries.reserve(next.size());
    for (const auto &[name, key] : next) {
        snapshot.entries.push_back(Entry{name, key});
    }
    auto encoded = encode_signed(snapshot, *identity_, *sodium_);
    if (!encoded) return encoded.status();
    const Status stored = StateStore::write_atomic(
        config_.path, encoded.value());
    if (!stored.ok()) return stored;
    aliases_ = std::move(next);
    state_ = snapshot;
    return Mutation{state_, true};
}

Result<Mutation> Store::set(
    std::string_view name, const PublicKey &public_key) {
    const Status valid = validate_name(name);
    if (!valid.ok()) return valid;
    if (!nonzero_key(public_key)) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias public key cannot be all zero"};
    }
    std::scoped_lock lock(mutex_);
    const auto existing = aliases_.find(std::string(name));
    if (existing != aliases_.end()) {
        if (existing->second == public_key) {
            return Mutation{state_, false};
        }
        return Status{ErrorCode::invalid_argument,
                      "peer alias is already bound; remove it explicitly before rebinding"};
    }
    const auto key_owner = std::find_if(
        aliases_.begin(), aliases_.end(),
        [&public_key](const auto &entry) {
            return entry.second == public_key;
        });
    if (key_owner != aliases_.end()) {
        return Status{ErrorCode::invalid_argument,
                      "peer public key already has alias " + key_owner->first +
                          "; use peer-alias-rename"};
    }
    if (aliases_.size() >= kMaximumAliases) {
        return Status{ErrorCode::resource_exhausted,
                      "peer alias store reached its 256-entry bound"};
    }
    auto next = aliases_;
    next.emplace(name, public_key);
    return commit(std::move(next));
}

Result<Mutation> Store::rename(
    std::string_view old_name, std::string_view new_name) {
    const Status old_valid = validate_name(old_name);
    const Status new_valid = validate_name(new_name);
    if (!old_valid.ok()) return old_valid;
    if (!new_valid.ok()) return new_valid;
    std::scoped_lock lock(mutex_);
    const auto existing = aliases_.find(std::string(old_name));
    if (existing == aliases_.end()) {
        return Status{ErrorCode::not_found,
                      "peer alias to rename does not exist: " +
                          std::string(old_name)};
    }
    if (old_name == new_name) {
        return Mutation{state_, false};
    }
    if (aliases_.contains(std::string(new_name))) {
        return Status{ErrorCode::invalid_argument,
                      "peer alias rename target already exists: " +
                          std::string(new_name)};
    }
    auto next = aliases_;
    const PublicKey key = existing->second;
    next.erase(std::string(old_name));
    next.emplace(new_name, key);
    return commit(std::move(next));
}

Result<Mutation> Store::remove(std::string_view name) {
    const Status valid = validate_name(name);
    if (!valid.ok()) return valid;
    std::scoped_lock lock(mutex_);
    if (!aliases_.contains(std::string(name))) {
        return Mutation{state_, false};
    }
    auto next = aliases_;
    next.erase(std::string(name));
    return commit(std::move(next));
}

std::string render_snapshot(const Snapshot &snapshot) {
    std::ostringstream output;
    output << "iotox-peer-aliases-v1\n"
           << "generation=" << snapshot.generation << '\n'
           << "count=" << snapshot.entries.size() << '\n';
    for (const Entry &entry : snapshot.entries) {
        output << "alias=" << entry.name
               << " public-key=" << security::hex(entry.public_key) << '\n';
    }
    return output.str();
}

std::string render_mutation(
    std::string_view operation, std::string_view name,
    const Mutation &mutation) {
    std::ostringstream output;
    output << "operation=" << operation << '\n'
           << "alias=" << name << '\n'
           << "generation=" << mutation.snapshot.generation << '\n'
           << "changed=" << (mutation.changed ? 1 : 0) << '\n';
    return output.str();
}

std::filesystem::path default_store_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) return {};
    std::filesystem::path parent = tox_savedata_path.parent_path();
    if (parent.empty()) parent = ".";
    std::filesystem::path name = tox_savedata_path.filename();
    name += ".peer-aliases";
    return parent / ".iotox-aliases" / name;
}

}  // namespace iotox::peer_alias
