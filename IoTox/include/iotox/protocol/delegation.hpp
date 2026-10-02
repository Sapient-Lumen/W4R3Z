#pragma once

#include "iotox/security/authority.hpp"
#include "iotox/security/authority_session.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace iotox::protocol {

inline constexpr std::uint8_t kDelegationRequestVersion = 1U;
inline constexpr std::size_t kDelegationRequestBytes =
    8U + security::kAuthorityRecordBytes;
inline constexpr std::uint8_t kDelegationResultVersion = 1U;
inline constexpr std::size_t kDelegationResultBytes = 56U;

using DelegationRequestBytes =
    std::array<std::uint8_t, kDelegationRequestBytes>;
using DelegationResultBytes =
    std::array<std::uint8_t, kDelegationResultBytes>;

enum class DelegationOutcome : std::uint8_t {
    applied = 0U,
    exact_duplicate = 1U,
    denied = 2U,
    malformed = 3U,
    conflict = 4U,
    internal_error = 5U,
};

struct DelegationRequest {
    security::AuthorityRecordBytes signed_record{};

    [[nodiscard]] bool operator==(const DelegationRequest &) const = default;
};

struct DelegationResult {
    DelegationOutcome outcome{DelegationOutcome::internal_error};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t authority_sequence{0U};
    security::Digest authority_tail_digest{};

    [[nodiscard]] bool operator==(const DelegationResult &) const = default;
};

struct DelegationApplication {
    DelegationOutcome outcome{DelegationOutcome::internal_error};
    bool ledger_changed{false};

    [[nodiscard]] bool operator==(const DelegationApplication &) const = default;
};

[[nodiscard]] Result<DelegationRequestBytes> encode_delegation_request(
    const DelegationRequest &request);
[[nodiscard]] Result<DelegationRequest> decode_delegation_request(
    std::span<const std::uint8_t> payload);
[[nodiscard]] Result<DelegationResultBytes> encode_delegation_result(
    const DelegationResult &result);
[[nodiscard]] Result<DelegationResult> decode_delegation_result(
    std::span<const std::uint8_t> payload);
[[nodiscard]] const char *to_string(DelegationOutcome outcome) noexcept;

// Structural/session gate before AuthorityLedger performs signature and full
// replay-policy validation. Only the currently connected controller may be
// delegated, and a delegation can never create another owner.
[[nodiscard]] Status validate_remote_self_delegation(
    const security::AuthorityRecord &record,
    const security::AuthoritySnapshot &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority);

[[nodiscard]] Status validate_remote_owner_mutation(
    const security::AuthorityRecord &record,
    const security::AuthoritySnapshot &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority);

// Validate and apply one complete signed record against one coherent ledger
// snapshot. Exact replay of the current tail is successful but never appends.
[[nodiscard]] DelegationApplication apply_remote_self_delegation(
    const security::AuthorityRecordBytes &signed_record,
    security::AuthorityLedger &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority,
    const security::Sodium &sodium);

[[nodiscard]] DelegationApplication apply_remote_owner_mutation(
    const security::AuthorityRecordBytes &signed_record,
    security::AuthorityLedger &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority,
    const security::Sodium &sodium);

}  // namespace iotox::protocol
