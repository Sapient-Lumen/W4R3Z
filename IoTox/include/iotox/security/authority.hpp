#pragma once

#include "iotox/security/recovery.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/rollback_witness.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::security {

inline constexpr std::size_t kAuthorityRecordBodyBytes = 192U;
inline constexpr std::size_t kAuthorityRecordBytes = 256U;
inline constexpr std::size_t kAuthorityPrepareBytes = 80U;
inline constexpr std::size_t kAuthorityLedgerHeaderBytes = 16U;
inline constexpr std::size_t kAuthorityRollbackGuardBytes = 192U;
inline constexpr std::size_t kDefaultMaximumAuthorityRecords = 4096U;

using AuthorityRecordBody = std::array<std::uint8_t, kAuthorityRecordBodyBytes>;
using AuthorityRecordBytes = std::array<std::uint8_t, kAuthorityRecordBytes>;

enum class AuthorityLedgerFormat : std::uint8_t {
    v1 = 1U,
    v2 = 2U,
    v3 = 3U,
};

// These bit positions are a durable policy contract. Unknown bits are rejected.
enum class Capability : std::uint64_t {
    read_telemetry = 1ULL << 0U,
    write_settings = 1ULL << 1U,
    actuate = 1ULL << 2U,
    manage_principals = 1ULL << 3U,
    install_firmware = 1ULL << 4U,
    export_diagnostics = 1ULL << 5U,
    factory_reset = 1ULL << 6U,
    interactive_terminal = 1ULL << 7U,
    sync_admin = 1ULL << 8U,
    sync_publish = 1ULL << 9U,
    sync_subscribe = 1ULL << 10U,
    sync_activate = 1ULL << 11U,
};

inline constexpr std::uint64_t kAuthorityV1Capabilities = (1ULL << 7U) - 1ULL;
inline constexpr std::uint64_t kAuthorityV2Capabilities = (1ULL << 8U) - 1ULL;
inline constexpr std::uint64_t kAuthorityV3Capabilities = (1ULL << 12U) - 1ULL;
inline constexpr std::uint64_t kConstitutionalOwnerCapabilities =
    kAuthorityV1Capabilities;
// Preserve the source-level meaning shipped by authority-ledger v1. Existing
// callers that used `kAllCapabilities` must not silently acquire terminal
// authority after recompilation; v2 callers opt in with the explicit mask.
inline constexpr std::uint64_t kAllCapabilities = kAuthorityV1Capabilities;

enum class PrincipalRole : std::uint8_t {
    none = 0U,
    owner = 1U,
    administrator = 2U,
    operator_role = 3U,
    viewer = 4U,
    automation = 5U,
    service = 6U,
};

enum class AuthorityAction : std::uint8_t {
    bootstrap = 1U,
    grant = 2U,
    revoke = 3U,
    epoch_transition = 4U,
    migrate_v2 = 5U,
    migrate_v3 = 6U,
};

struct AuthorityPrepareRequest {
    AuthorityAction action{AuthorityAction::bootstrap};
    PrincipalRole role{PrincipalRole::none};
    std::uint64_t capabilities{0U};
    SigningPublicKey issuer{};
    SigningPublicKey subject{};

    [[nodiscard]] bool operator==(const AuthorityPrepareRequest &) const = default;
};

struct AuthorityRecord {
    AuthorityLedgerFormat format{AuthorityLedgerFormat::v1};
    AuthorityAction action{AuthorityAction::bootstrap};
    PrincipalRole role{PrincipalRole::none};
    std::uint64_t sequence{0U};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t not_before_unix_ms{0U};
    std::uint64_t not_after_unix_ms{0U};
    std::uint64_t capabilities{0U};
    SigningPublicKey device{};
    SigningPublicKey issuer{};
    SigningPublicKey subject{};
    Digest previous_digest{};
    Signature signature{};

    [[nodiscard]] bool operator==(const AuthorityRecord &) const = default;
};

struct PrincipalState {
    SigningPublicKey public_key{};
    PrincipalRole role{PrincipalRole::none};
    std::uint64_t capabilities{0U};
    std::uint64_t last_sequence{0U};
    bool active{false};

    [[nodiscard]] bool operator==(const PrincipalState &) const = default;
};

struct AuthoritySnapshot {
    SigningPublicKey device{};
    AuthorityLedgerFormat format{AuthorityLedgerFormat::v1};
    bool initialized{false};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t sequence{0U};
    std::size_t record_count{0U};
    Digest tail_digest{};
    // A non-zero value names the owner granted by the immediately preceding
    // record as the only principal allowed to sign an epoch transition.
    SigningPublicKey nominated_successor{};
    std::vector<PrincipalState> principals;
};

[[nodiscard]] std::string to_string(AuthorityLedgerFormat format);
[[nodiscard]] std::string to_string(Capability capability);
[[nodiscard]] std::string to_string(PrincipalRole role);
[[nodiscard]] std::string to_string(AuthorityAction action);
[[nodiscard]] Result<PrincipalRole> parse_principal_role(std::string_view value);
[[nodiscard]] Result<std::uint64_t> parse_capability_set(std::string_view value);
[[nodiscard]] std::string render_capability_set(std::uint64_t capabilities);
[[nodiscard]] std::uint64_t authority_capability_mask(
    AuthorityLedgerFormat format) noexcept;
[[nodiscard]] std::uint64_t role_capability_ceiling(
    PrincipalRole role, AuthorityLedgerFormat format) noexcept;
[[nodiscard]] inline std::uint64_t role_capability_ceiling(
    PrincipalRole role) noexcept {
    // Preserve the source-level v1 contract. Callers that intentionally
    // operate on a v2 ledger must pass the format explicitly.
    return role_capability_ceiling(role, AuthorityLedgerFormat::v1);
}

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_authority_prepare_request(
    const AuthorityPrepareRequest &request);
[[nodiscard]] Result<AuthorityPrepareRequest> decode_authority_prepare_request(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<AuthorityRecordBody> encode_authority_record_body(
    const AuthorityRecord &record);
[[nodiscard]] Result<AuthorityRecord> decode_authority_record(
    std::span<const std::uint8_t> bytes);
[[nodiscard]] Result<AuthorityRecordBytes> sign_authority_record_body(
    std::span<const std::uint8_t, kAuthorityRecordBodyBytes> body,
    std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key,
    const Sodium &sodium);
[[nodiscard]] Result<Digest> authority_record_digest(
    std::span<const std::uint8_t, kAuthorityRecordBytes> record,
    const Sodium &sodium);

// RecallRoot-v1 intentionally derives one stable owner signing principal. This
// is the mechanism that makes "from memory, reach your devices" possible. It
// also makes owner identity linkable across devices unless a later delegated
// per-device principal layer is used; that tradeoff is explicit, not hidden.
[[nodiscard]] Result<SigningSeed> derive_owner_signing_seed(
    const RecoveryRoot &root, const Sodium &sodium);

class AuthorityLedger {
  public:
    struct Config {
        std::filesystem::path path;
        std::size_t maximum_records{kDefaultMaximumAuthorityRecords};
        // Empty selects `<path>.guard`. The guard is deliberately separate
        // from the append-only signed history so interrupted atomic replaces
        // can be distinguished from a stale or forked ledger head.
        std::filesystem::path rollback_guard_path;
        // Optional external freshness boundary. Production configurations
        // require an independently controlled authenticated exact-CAS backend;
        // the explicit test exception can never support a deployment claim.
        std::shared_ptr<rollback_witness::Backend> rollback_witness;
        rollback_witness::DomainId rollback_witness_domain{};
        std::uint64_t rollback_witness_epoch{0U};
        std::filesystem::path rollback_witness_intent_path;
        bool allow_non_independent_witness_for_testing{false};
    };

    AuthorityLedger(const AuthorityLedger &) = delete;
    AuthorityLedger &operator=(const AuthorityLedger &) = delete;
    AuthorityLedger(AuthorityLedger &&) = delete;
    AuthorityLedger &operator=(AuthorityLedger &&) = delete;
    ~AuthorityLedger() = default;

    [[nodiscard]] static Result<std::unique_ptr<AuthorityLedger>> open(
        Config config,
        const SigningPublicKey &device,
        const Sodium &sodium);

    [[nodiscard]] AuthoritySnapshot snapshot() const;
    [[nodiscard]] Result<AuthorityRecordBody> prepare(
        const AuthorityPrepareRequest &request) const;
    [[nodiscard]] Status append(
        std::span<const std::uint8_t, kAuthorityRecordBytes> record);
    [[nodiscard]] Result<PrincipalState> principal(
        const SigningPublicKey &public_key) const;
    [[nodiscard]] bool authorized(
        const SigningPublicKey &public_key, std::uint64_t required_capabilities) const;

    [[nodiscard]] const std::filesystem::path &path() const noexcept { return config_.path; }

  private:
    AuthorityLedger(Config config, SigningPublicKey device, const Sodium &sodium)
        : config_(std::move(config)), device_(device), sodium_(&sodium) {}

    [[nodiscard]] Status load();
    [[nodiscard]] Status replay(
        std::span<const AuthorityRecordBytes> records,
        AuthoritySnapshot &snapshot) const;
    [[nodiscard]] Status apply(
        const AuthorityRecordBytes &bytes,
        AuthoritySnapshot &snapshot) const;
    [[nodiscard]] Status write_records(
        std::span<const AuthorityRecordBytes> records,
        AuthorityLedgerFormat format) const;
    [[nodiscard]] Status verify_or_adopt_rollback_guard(
        const AuthoritySnapshot &snapshot,
        bool ledger_present);
    [[nodiscard]] Status begin_rollback_guard_transition(
        const AuthoritySnapshot &current,
        const AuthoritySnapshot &next);
    [[nodiscard]] Status finish_rollback_guard_transition(
        const AuthoritySnapshot &current);
    [[nodiscard]] Status reconcile_rollback_witness();
    [[nodiscard]] Status begin_rollback_witness_transition(
        const AuthoritySnapshot &current,
        const AuthoritySnapshot &next,
        const AuthorityRecordBytes &record,
        rollback_witness::Record &committed,
        rollback_witness::Record &pending);
    [[nodiscard]] Status finish_rollback_witness_transition(
        const rollback_witness::Record &pending);

    Config config_;
    SigningPublicKey device_{};
    const Sodium *sodium_{nullptr};

    mutable std::mutex mutex_;
    std::vector<AuthorityRecordBytes> records_;
    AuthoritySnapshot snapshot_;
    bool rollback_guard_established_{false};
};

[[nodiscard]] std::filesystem::path default_authority_ledger_path(
    const std::filesystem::path &tox_savedata_path);
[[nodiscard]] std::filesystem::path default_authority_rollback_guard_path(
    const std::filesystem::path &authority_ledger_path);
[[nodiscard]] std::string render_authority_snapshot(const AuthoritySnapshot &snapshot);
[[nodiscard]] std::string render_principals(const AuthoritySnapshot &snapshot);

}  // namespace iotox::security
