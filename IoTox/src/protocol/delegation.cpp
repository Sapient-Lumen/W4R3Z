#include "iotox/protocol/delegation.hpp"

#include <algorithm>
#include <array>
#include <limits>

namespace iotox::protocol {
namespace {

constexpr std::array<std::uint8_t, 4U> kRequestMagic{'I', 'R', 'D', '1'};
constexpr std::array<std::uint8_t, 4U> kResultMagic{'I', 'R', 'R', '1'};

void write_u64(std::span<std::uint8_t> output, std::size_t offset,
               std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[offset + index] = static_cast<std::uint8_t>(
            (value >> ((7U - index) * 8U)) & 0xffU);
    }
}

std::uint64_t read_u64(std::span<const std::uint8_t> input,
                       std::size_t offset) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | input[offset + index];
    }
    return value;
}

bool known_outcome(std::uint8_t value) noexcept {
    return value <= static_cast<std::uint8_t>(
                        DelegationOutcome::internal_error);
}

}  // namespace

Result<DelegationRequestBytes> encode_delegation_request(
    const DelegationRequest &request) {
    auto decoded = security::decode_authority_record(request.signed_record);
    if (!decoded) {
        return Status{ErrorCode::invalid_argument,
                      "delegation request requires a canonical authority record"};
    }
    DelegationRequestBytes output{};
    std::copy(kRequestMagic.begin(), kRequestMagic.end(), output.begin());
    output[4U] = kDelegationRequestVersion;
    std::copy(request.signed_record.begin(), request.signed_record.end(),
              output.begin() + 8);
    return output;
}

Result<DelegationRequest> decode_delegation_request(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kDelegationRequestBytes) {
        return Status{ErrorCode::protocol_error,
                      "delegation request must be exactly 264 bytes"};
    }
    if (!std::equal(kRequestMagic.begin(), kRequestMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "delegation request magic is invalid"};
    }
    if (payload[4U] != kDelegationRequestVersion) {
        return Status{ErrorCode::unsupported,
                      "delegation request version is unsupported"};
    }
    if (payload[5U] != 0U || payload[6U] != 0U || payload[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "delegation request reserved bytes must be zero"};
    }
    DelegationRequest request;
    std::copy(payload.begin() + 8, payload.end(), request.signed_record.begin());
    auto decoded = security::decode_authority_record(request.signed_record);
    if (!decoded) {
        return Status{ErrorCode::protocol_error,
                      "delegation request authority record is malformed"};
    }
    return request;
}

Result<DelegationResultBytes> encode_delegation_result(
    const DelegationResult &result) {
    if (!known_outcome(static_cast<std::uint8_t>(result.outcome))) {
        return Status{ErrorCode::invalid_argument,
                      "delegation result outcome is invalid"};
    }
    DelegationResultBytes output{};
    std::copy(kResultMagic.begin(), kResultMagic.end(), output.begin());
    output[4U] = kDelegationResultVersion;
    output[5U] = static_cast<std::uint8_t>(result.outcome);
    write_u64(output, 8U, result.ownership_epoch);
    write_u64(output, 16U, result.authority_sequence);
    std::copy(result.authority_tail_digest.begin(),
              result.authority_tail_digest.end(), output.begin() + 24);
    return output;
}

Result<DelegationResult> decode_delegation_result(
    std::span<const std::uint8_t> payload) {
    if (payload.size() != kDelegationResultBytes) {
        return Status{ErrorCode::protocol_error,
                      "delegation result must be exactly 56 bytes"};
    }
    if (!std::equal(kResultMagic.begin(), kResultMagic.end(), payload.begin())) {
        return Status{ErrorCode::protocol_error,
                      "delegation result magic is invalid"};
    }
    if (payload[4U] != kDelegationResultVersion) {
        return Status{ErrorCode::unsupported,
                      "delegation result version is unsupported"};
    }
    if (!known_outcome(payload[5U]) || payload[6U] != 0U || payload[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "delegation result outcome/reserved bytes are invalid"};
    }
    DelegationResult result;
    result.outcome = static_cast<DelegationOutcome>(payload[5U]);
    result.ownership_epoch = read_u64(payload, 8U);
    result.authority_sequence = read_u64(payload, 16U);
    std::copy(payload.begin() + 24, payload.end(),
              result.authority_tail_digest.begin());
    return result;
}

const char *to_string(DelegationOutcome outcome) noexcept {
    switch (outcome) {
        case DelegationOutcome::applied: return "applied";
        case DelegationOutcome::exact_duplicate: return "exact-duplicate";
        case DelegationOutcome::denied: return "denied";
        case DelegationOutcome::malformed: return "malformed";
        case DelegationOutcome::conflict: return "conflict";
        case DelegationOutcome::internal_error: return "internal-error";
    }
    return "unknown";
}

Status validate_remote_self_delegation(
    const security::AuthorityRecord &record,
    const security::AuthoritySnapshot &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority) {
    const auto manage_principals = static_cast<std::uint64_t>(
        security::Capability::manage_principals);
    if (!local_authority.initialized || !peer_authority.connected ||
        !peer_authority.feature_negotiated ||
        !peer_authority.remote_authorized ||
        peer_authority.remote_role != security::PrincipalRole::owner ||
        (peer_authority.remote_capabilities & manage_principals) == 0U) {
        return Status{ErrorCode::unavailable,
                      "remote self-delegation requires a currently proven owner"};
    }
    if (peer_authority.local_authority_format != local_authority.format ||
        peer_authority.local_authority_epoch !=
            local_authority.ownership_epoch ||
        peer_authority.local_authority_sequence != local_authority.sequence ||
        peer_authority.local_authority_tail_digest !=
            local_authority.tail_digest) {
        return Status{ErrorCode::unavailable,
                      "remote self-delegation proof targets a stale authority head"};
    }
    if (record.action != security::AuthorityAction::grant ||
        record.role == security::PrincipalRole::none ||
        record.role == security::PrincipalRole::owner) {
        return Status{ErrorCode::unavailable,
                      "remote self-delegation must grant a non-owner role"};
    }
    if (record.format != local_authority.format) {
        return Status{ErrorCode::protocol_error,
                      "remote self-delegation record format does not match the challenged ledger"};
    }
    if (record.device != local_authority.device ||
        record.issuer != peer_authority.remote_principal ||
        record.subject != peer_authority.peer_verifier_device) {
        return Status{ErrorCode::unavailable,
                      "remote self-delegation is not bound to this device, owner, and controller"};
    }
    if (record.ownership_epoch != local_authority.ownership_epoch ||
        record.sequence != local_authority.sequence + 1U ||
        record.previous_digest != local_authority.tail_digest) {
        return Status{ErrorCode::protocol_error,
                      "remote self-delegation does not extend the exact challenged authority head"};
    }
    return Status::success();
}

Status validate_remote_owner_mutation(
    const security::AuthorityRecord &record,
    const security::AuthoritySnapshot &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority) {
    const auto manage_principals = static_cast<std::uint64_t>(
        security::Capability::manage_principals);
    if (!local_authority.initialized || !peer_authority.connected ||
        !peer_authority.feature_negotiated ||
        !peer_authority.remote_authorized ||
        peer_authority.remote_role != security::PrincipalRole::owner ||
        (peer_authority.remote_capabilities & manage_principals) == 0U) {
        return Status{ErrorCode::unavailable,
                      "remote authority mutation requires a currently proven owner"};
    }
    if (peer_authority.local_authority_format != local_authority.format ||
        peer_authority.local_authority_epoch !=
            local_authority.ownership_epoch ||
        peer_authority.local_authority_sequence != local_authority.sequence ||
        peer_authority.local_authority_tail_digest !=
            local_authority.tail_digest) {
        return Status{ErrorCode::unavailable,
                      "remote authority mutation proof targets a stale authority head"};
    }
    if (record.device != local_authority.device ||
        record.issuer != peer_authority.remote_principal) {
        return Status{ErrorCode::unavailable,
                      "remote authority mutation is not bound to this device and owner"};
    }
    const bool migration_v2 =
        record.action == security::AuthorityAction::migrate_v2;
    const bool migration_v3 =
        record.action == security::AuthorityAction::migrate_v3;
    if (migration_v2) {
        if (!peer_authority.authority_v2_negotiated) {
            return Status{ErrorCode::unsupported,
                          "remote authority v2 migration was not negotiated for this session"};
        }
        if (local_authority.format != security::AuthorityLedgerFormat::v1 ||
            record.format != security::AuthorityLedgerFormat::v2) {
            return Status{ErrorCode::protocol_error,
                          "remote authority v2 migration has an invalid format boundary"};
        }
    } else if (migration_v3) {
        if (!peer_authority.authority_v2_negotiated ||
            !peer_authority.authority_v3_negotiated) {
            return Status{
                ErrorCode::unsupported,
                "remote authority v3 migration was not negotiated for this session"};
        }
        if (local_authority.format != security::AuthorityLedgerFormat::v2 ||
            record.format != security::AuthorityLedgerFormat::v3) {
            return Status{
                ErrorCode::protocol_error,
                "remote authority v3 migration has an invalid format boundary"};
        }
    } else if (record.format != local_authority.format) {
        return Status{ErrorCode::protocol_error,
                      "remote authority record format does not match the challenged ledger"};
    }
    if (record.action == security::AuthorityAction::epoch_transition) {
        if (local_authority.ownership_epoch ==
                std::numeric_limits<std::uint64_t>::max() ||
            record.ownership_epoch != local_authority.ownership_epoch + 1U ||
            record.sequence != 1U ||
            record.previous_digest != local_authority.tail_digest) {
            return Status{ErrorCode::protocol_error,
                          "remote epoch transition does not advance the exact challenged authority head"};
        }
        const auto successor = std::find_if(
            local_authority.principals.begin(),
            local_authority.principals.end(),
            [&](const security::PrincipalState &candidate) {
                return candidate.public_key == record.issuer;
            });
        if (record.role != security::PrincipalRole::owner ||
            record.subject != record.issuer ||
            local_authority.nominated_successor != record.issuer ||
            successor == local_authority.principals.end() ||
            !successor->active ||
            successor->role != security::PrincipalRole::owner ||
            record.capabilities != successor->capabilities) {
            return Status{ErrorCode::unavailable,
                          "remote epoch transition requires the proven nominated successor and its exact capability set"};
        }
        return Status::success();
    }
    if (local_authority.sequence ==
            std::numeric_limits<std::uint64_t>::max() ||
        record.ownership_epoch != local_authority.ownership_epoch ||
        record.sequence != local_authority.sequence + 1U ||
        record.previous_digest != local_authority.tail_digest) {
        return Status{ErrorCode::protocol_error,
                      "remote authority mutation does not extend the exact challenged authority head"};
    }
    if (migration_v2) {
        if (record.role != security::PrincipalRole::owner ||
            record.capabilities != security::kAuthorityV1Capabilities ||
            record.subject != record.issuer) {
            return Status{ErrorCode::unavailable,
                          "remote authority v2 migration must preserve the proven v1 owner exactly"};
        }
        return Status::success();
    }
    if (migration_v3) {
        if (record.role != security::PrincipalRole::owner ||
            record.capabilities != peer_authority.remote_capabilities ||
            (record.capabilities & ~security::kAuthorityV2Capabilities) != 0U ||
            record.subject != record.issuer) {
            return Status{
                ErrorCode::unavailable,
                "remote authority v3 migration must preserve the proven v2 "
                "owner exactly"};
        }
        return Status::success();
    }
    if (record.action == security::AuthorityAction::grant) {
        if (record.role == security::PrincipalRole::owner) {
            const auto subject = std::find_if(
                local_authority.principals.begin(),
                local_authority.principals.end(),
                [&](const security::PrincipalState &candidate) {
                    return candidate.public_key == record.subject;
                });
            if (record.subject == record.issuer) {
                const std::uint64_t current_capabilities =
                    subject == local_authority.principals.end()
                        ? 0U
                        : subject->capabilities;
                const std::uint64_t added_capabilities =
                    record.capabilities & ~current_capabilities;
                const std::uint64_t removed_capabilities =
                    current_capabilities & ~record.capabilities;
                if (subject == local_authority.principals.end() ||
                    !subject->active ||
                    subject->role != security::PrincipalRole::owner ||
                    record.format == security::AuthorityLedgerFormat::v1 ||
                    added_capabilities == 0U || removed_capabilities != 0U ||
                    (record.capabilities & ~security::authority_capability_mask(
                                               record.format)) != 0U ||
                    (record.capabilities &
                     security::kConstitutionalOwnerCapabilities) !=
                        security::kConstitutionalOwnerCapabilities) {
                    return Status{
                        ErrorCode::unavailable,
                        "remote owner capability activation requires the "
                        "proven active owner"};
                }
                return Status::success();
            }
            if ((record.capabilities &
                 security::kConstitutionalOwnerCapabilities) !=
                    security::kConstitutionalOwnerCapabilities ||
                (record.capabilities &
                 ~security::authority_capability_mask(record.format)) != 0U ||
                (subject != local_authority.principals.end() &&
                 subject->active &&
                 subject->role == security::PrincipalRole::owner)) {
                return Status{ErrorCode::unavailable,
                              "remote successor nomination requires a distinct non-owner subject"};
            }
            return Status::success();
        }
        return validate_remote_self_delegation(
            record, local_authority, peer_authority);
    }
    if (record.action != security::AuthorityAction::revoke ||
        record.role != security::PrincipalRole::none ||
        record.capabilities != 0U) {
        return Status{ErrorCode::unavailable,
                      "remote authority mutation is neither self-grant nor revocation"};
    }
    const auto subject = std::find_if(
        local_authority.principals.begin(), local_authority.principals.end(),
        [&](const security::PrincipalState &candidate) {
            return candidate.public_key == record.subject;
        });
    if (subject == local_authority.principals.end() || !subject->active ||
        subject->role == security::PrincipalRole::owner) {
        return Status{ErrorCode::unavailable,
                      "remote revocation requires an active non-owner subject"};
    }
    return Status::success();
}

DelegationApplication apply_remote_self_delegation(
    const security::AuthorityRecordBytes &signed_record,
    security::AuthorityLedger &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority,
    const security::Sodium &sodium) {
    return apply_remote_owner_mutation(
        signed_record, local_authority, peer_authority, sodium);
}

DelegationApplication apply_remote_owner_mutation(
    const security::AuthorityRecordBytes &signed_record,
    security::AuthorityLedger &local_authority,
    const security::PeerAuthoritySnapshot &peer_authority,
    const security::Sodium &sodium) {
    auto record = security::decode_authority_record(signed_record);
    if (!record) {
        return {DelegationOutcome::malformed, false};
    }
    const security::AuthoritySnapshot before = local_authority.snapshot();
    auto digest = security::authority_record_digest(signed_record, sodium);
    if (!digest) {
        return {DelegationOutcome::internal_error, false};
    }

    const bool duplicate = record.value().sequence > 0U &&
        before.sequence == record.value().sequence &&
        before.tail_digest == digest.value();
    if (duplicate) {
        const bool recognized_mutation =
            record.value().action == security::AuthorityAction::revoke ||
            record.value().action == security::AuthorityAction::migrate_v2 ||
            record.value().action == security::AuthorityAction::migrate_v3 ||
            record.value().action ==
                security::AuthorityAction::epoch_transition ||
            (record.value().action == security::AuthorityAction::grant &&
             (record.value().role == security::PrincipalRole::owner ||
              record.value().subject == peer_authority.peer_verifier_device));
        // An exact tail duplicate is a content-addressed no-op. The mutation
        // that produced it invalidates the just-used authority proof, so an
        // idempotent transport retry cannot require that stale proof to remain
        // authorized. Keep the acknowledgement bound to a connected,
        // negotiated peer and to this device, but never append or reinterpret
        // the bytes.
        const bool format_negotiated =
            record.value().format == security::AuthorityLedgerFormat::v3
                ? (peer_authority.authority_v2_negotiated &&
                   peer_authority.authority_v3_negotiated)
                : (record.value().format !=
                       security::AuthorityLedgerFormat::v2 ||
                   peer_authority.authority_v2_negotiated);
        const bool same_controller =
            peer_authority.connected && peer_authority.feature_negotiated &&
            format_negotiated && record.value().device == before.device &&
            recognized_mutation;
        return {same_controller ? DelegationOutcome::exact_duplicate
                                : DelegationOutcome::denied,
                false};
    }
    security::AuthoritySnapshot validation_head = before;
    const Status bound = validate_remote_owner_mutation(
        record.value(), validation_head, peer_authority);
    if (!bound.ok()) {
        return {bound.code() == ErrorCode::protocol_error
                    ? DelegationOutcome::conflict
                    : DelegationOutcome::denied,
                false};
    }
    const Status appended = local_authority.append(signed_record);
    if (!appended.ok()) {
        if (appended.code() == ErrorCode::protocol_error) {
            return {DelegationOutcome::conflict, false};
        }
        if (appended.code() == ErrorCode::invalid_argument ||
            appended.code() == ErrorCode::unsupported ||
            appended.code() == ErrorCode::not_found) {
            return {DelegationOutcome::denied, false};
        }
        return {DelegationOutcome::internal_error, false};
    }
    return {DelegationOutcome::applied, true};
}

}  // namespace iotox::protocol
