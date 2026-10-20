#include "iotox/security/authority.hpp"

#include "iotox/security/random.hpp"
#include "iotox/state_store.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::security {
namespace {

constexpr std::array<std::uint8_t, 4U> kRecordMagicV1 = {'I', 'A', 'L', '1'};
constexpr std::array<std::uint8_t, 4U> kRecordMagicV2 = {'I', 'A', 'L', '2'};
constexpr std::array<std::uint8_t, 4U> kRecordMagicV3 = {'I', 'A', 'L', '3'};
constexpr std::array<std::uint8_t, 8U> kLedgerMagicV1 = {
    'I', 'O', 'T', 'O', 'X', 'A', 'L', '1'};
constexpr std::array<std::uint8_t, 8U> kLedgerMagicV2 = {
    'I', 'O', 'T', 'O', 'X', 'A', 'L', '2'};
constexpr std::array<std::uint8_t, 8U> kLedgerMagicV3 = {'I', 'O', 'T', 'O',
                                                         'X', 'A', 'L', '3'};
constexpr std::array<std::uint8_t, 8U> kRollbackGuardMagic = {
    'I', 'O', 'T', 'O', 'X', 'A', 'G', '2'};
constexpr std::array<std::uint8_t, 8U> kWitnessIntentMagic = {
    'I', 'O', 'T', 'O', 'X', 'A', 'W', '1'};
constexpr std::size_t kWitnessIntentBytes = 448U;
constexpr std::uint8_t kRecordFormatV1 = 1U;
constexpr std::uint8_t kRecordFormatV2 = 2U;
constexpr std::uint8_t kRecordFormatV3 = 3U;
constexpr std::uint8_t kLedgerFormatV1 = 1U;
constexpr std::uint8_t kLedgerFormatV2 = 2U;
constexpr std::uint8_t kLedgerFormatV3 = 3U;
constexpr std::uint8_t kRollbackGuardFormat = 2U;
constexpr std::uint8_t kRollbackGuardPending = 1U << 0U;
constexpr std::size_t kRollbackGuardDeviceOffset = 16U;
constexpr std::size_t kRollbackGuardCommittedOffset = 48U;
constexpr std::size_t kRollbackGuardPendingOffset = 112U;
constexpr std::size_t kRollbackGuardHeadBytes = 64U;
constexpr std::string_view kSignatureDomainV1 =
    "iotox-authority-record-signature-v1";
constexpr std::string_view kSignatureDomainV2 =
    "iotox-authority-record-signature-v2";
constexpr std::string_view kSignatureDomainV3 =
    "iotox-authority-record-signature-v3";
constexpr std::string_view kDigestDomainV1 =
    "iotox-authority-record-digest-v1";
constexpr std::string_view kDigestDomainV2 =
    "iotox-authority-record-digest-v2";
constexpr std::string_view kDigestDomainV3 = "iotox-authority-record-digest-v3";
constexpr std::string_view kOwnerSeedDomain = "iotox-owner-signing-seed-v1";
constexpr std::array<std::uint8_t, 7U> kSignaturePrefix = {
    'I', 'O', 'T', 'O', 'X', 'S', '1'};

using PrincipalMap = std::map<SigningPublicKey, PrincipalState>;

struct RollbackGuardHead {
    bool initialized{false};
    AuthorityLedgerFormat format{AuthorityLedgerFormat::v1};
    std::uint64_t record_count{0U};
    std::uint64_t ownership_epoch{0U};
    std::uint64_t sequence{0U};
    Digest tail_digest{};

    [[nodiscard]] bool operator==(const RollbackGuardHead &) const = default;
};

struct RollbackGuardState {
    SigningPublicKey device{};
    RollbackGuardHead committed;
    bool has_pending{false};
    RollbackGuardHead pending;
};

struct WitnessIntent {
    rollback_witness::DomainId domain{};
    SigningPublicKey device{};
    std::uint64_t witness_epoch{0U};
    rollback_witness::Lane lane{rollback_witness::Lane::authority};
    rollback_witness::Head current;
    rollback_witness::Head next;
    rollback_witness::TransactionNonce nonce{};
    AuthorityRecordBytes record{};
};

void put_u32(std::span<std::uint8_t> output, std::uint32_t value) {
    output[0U] = static_cast<std::uint8_t>((value >> 24U) & 0xFFU);
    output[1U] = static_cast<std::uint8_t>((value >> 16U) & 0xFFU);
    output[2U] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
    output[3U] = static_cast<std::uint8_t>(value & 0xFFU);
}

std::uint32_t get_u32(std::span<const std::uint8_t> input) {
    std::uint32_t value = 0U;
    for (std::size_t index = 0U; index < 4U; ++index) {
        value = static_cast<std::uint32_t>((value << 8U) | input[index]);
    }
    return value;
}

void put_u64(std::span<std::uint8_t> output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index) {
        output[7U - index] = static_cast<std::uint8_t>(value & 0xFFU);
        value >>= 8U;
    }
}

std::uint64_t get_u64(std::span<const std::uint8_t> input) {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | input[index];
    }
    return value;
}

rollback_witness::Head witness_head(
    const AuthoritySnapshot &snapshot) noexcept {
    rollback_witness::Head head;
    head.position = static_cast<std::uint64_t>(snapshot.record_count);
    head.digest = snapshot.tail_digest;
    return head;
}

rollback_witness::Record expected_witness_record(
    const AuthorityLedger::Config &config,
    const SigningPublicKey &device,
    const AuthoritySnapshot &snapshot) {
    rollback_witness::Record record;
    record.domain = config.rollback_witness_domain;
    record.device = device;
    record.witness_epoch = config.rollback_witness_epoch;
    record.lane = rollback_witness::Lane::authority;
    record.committed = witness_head(snapshot);
    return record;
}

bool all_zero(std::span<const std::uint8_t> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::uint8_t value) {
        return value == 0U;
    });
}

bool known_format(AuthorityLedgerFormat format) noexcept {
    return format == AuthorityLedgerFormat::v1 ||
           format == AuthorityLedgerFormat::v2 ||
           format == AuthorityLedgerFormat::v3;
}

RollbackGuardHead rollback_guard_head(
    const AuthoritySnapshot &snapshot) noexcept {
    RollbackGuardHead head;
    head.initialized = snapshot.initialized;
    head.format = snapshot.format;
    head.record_count = static_cast<std::uint64_t>(snapshot.record_count);
    head.ownership_epoch = snapshot.ownership_epoch;
    head.sequence = snapshot.sequence;
    head.tail_digest = snapshot.tail_digest;
    return head;
}

Status validate_rollback_guard_head(
    const RollbackGuardHead &head,
    std::string_view label) {
    if (!known_format(head.format)) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " uses an unknown ledger format"};
    }
    if (!head.initialized) {
        if (head.format != AuthorityLedgerFormat::v1 ||
            head.record_count != 0U || head.ownership_epoch != 0U ||
            head.sequence != 0U || !all_zero(head.tail_digest)) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) +
                              " encodes a non-empty uninitialized authority head"};
        }
        return Status::success();
    }
    if (head.record_count == 0U || head.ownership_epoch == 0U ||
        head.sequence == 0U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " encodes an initialized authority head with a zero counter"};
    }
    return Status::success();
}

void encode_rollback_guard_head(
    const RollbackGuardHead &head,
    std::span<std::uint8_t, kRollbackGuardHeadBytes> output) {
    std::fill(output.begin(), output.end(), 0U);
    output[0U] = head.initialized ? 1U : 0U;
    output[1U] = static_cast<std::uint8_t>(head.format);
    put_u64(output.subspan(8U, 8U), head.record_count);
    put_u64(output.subspan(16U, 8U), head.ownership_epoch);
    put_u64(output.subspan(24U, 8U), head.sequence);
    std::copy(head.tail_digest.begin(), head.tail_digest.end(),
              output.begin() + 32U);
}

Result<RollbackGuardHead> decode_rollback_guard_head(
    std::span<const std::uint8_t, kRollbackGuardHeadBytes> input,
    std::string_view label) {
    if (input[0U] > 1U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " has an invalid initialized flag"};
    }
    for (std::size_t index = 2U; index < 8U; ++index) {
        if (input[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " has non-zero reserved bytes"};
        }
    }
    RollbackGuardHead head;
    head.initialized = input[0U] == 1U;
    head.format = static_cast<AuthorityLedgerFormat>(input[1U]);
    head.record_count = get_u64(input.subspan(8U, 8U));
    head.ownership_epoch = get_u64(input.subspan(16U, 8U));
    head.sequence = get_u64(input.subspan(24U, 8U));
    std::copy_n(input.begin() + 32U, head.tail_digest.size(),
                head.tail_digest.begin());
    const Status valid = validate_rollback_guard_head(head, label);
    if (!valid.ok()) {
        return valid;
    }
    return head;
}

Result<std::array<std::uint8_t, kAuthorityRollbackGuardBytes>>
encode_rollback_guard(const RollbackGuardState &guard) {
    if (all_zero(guard.device)) {
        return Status{ErrorCode::invalid_argument,
                      "authority rollback guard requires a non-zero device key"};
    }
    const Status committed = validate_rollback_guard_head(
        guard.committed, "authority rollback guard committed head");
    if (!committed.ok()) {
        return committed;
    }
    if (guard.has_pending) {
        const Status pending = validate_rollback_guard_head(
            guard.pending, "authority rollback guard pending head");
        if (!pending.ok()) {
            return pending;
        }
    }

    std::array<std::uint8_t, kAuthorityRollbackGuardBytes> bytes{};
    std::copy(kRollbackGuardMagic.begin(), kRollbackGuardMagic.end(),
              bytes.begin());
    bytes[8U] = kRollbackGuardFormat;
    bytes[9U] = guard.has_pending ? kRollbackGuardPending : 0U;
    std::copy(guard.device.begin(), guard.device.end(),
              bytes.begin() + static_cast<std::ptrdiff_t>(
                                  kRollbackGuardDeviceOffset));
    encode_rollback_guard_head(
        guard.committed,
        std::span<std::uint8_t, kRollbackGuardHeadBytes>{
            bytes.data() + kRollbackGuardCommittedOffset,
            kRollbackGuardHeadBytes});
    if (guard.has_pending) {
        encode_rollback_guard_head(
            guard.pending,
            std::span<std::uint8_t, kRollbackGuardHeadBytes>{
                bytes.data() + kRollbackGuardPendingOffset,
                kRollbackGuardHeadBytes});
    }
    return bytes;
}

Result<RollbackGuardState> decode_rollback_guard(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityRollbackGuardBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback guard must contain exactly 192 bytes"};
    }
    if (!std::equal(kRollbackGuardMagic.begin(), kRollbackGuardMagic.end(),
                    bytes.begin()) ||
        bytes[8U] != kRollbackGuardFormat ||
        (bytes[9U] & ~kRollbackGuardPending) != 0U) {
        return Status{ErrorCode::unsupported,
                      "authority rollback guard magic, format, or flags are unsupported"};
    }
    for (std::size_t index = 10U; index < 16U; ++index) {
        if (bytes[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority rollback guard header reserved bytes are non-zero"};
        }
    }
    for (std::size_t index = 176U; index < bytes.size(); ++index) {
        if (bytes[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority rollback guard trailer reserved bytes are non-zero"};
        }
    }

    RollbackGuardState guard;
    std::copy_n(bytes.begin() + kRollbackGuardDeviceOffset,
                guard.device.size(), guard.device.begin());
    if (all_zero(guard.device)) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback guard contains a zero device key"};
    }
    auto committed = decode_rollback_guard_head(
        std::span<const std::uint8_t, kRollbackGuardHeadBytes>{
            bytes.data() + kRollbackGuardCommittedOffset,
            kRollbackGuardHeadBytes},
        "authority rollback guard committed head");
    if (!committed) {
        return committed.status();
    }
    guard.committed = committed.value();
    guard.has_pending = (bytes[9U] & kRollbackGuardPending) != 0U;
    if (guard.has_pending) {
        auto pending = decode_rollback_guard_head(
            std::span<const std::uint8_t, kRollbackGuardHeadBytes>{
                bytes.data() + kRollbackGuardPendingOffset,
                kRollbackGuardHeadBytes},
            "authority rollback guard pending head");
        if (!pending) {
            return pending.status();
        }
        guard.pending = pending.value();
    } else if (!all_zero(bytes.subspan(
                   kRollbackGuardPendingOffset, kRollbackGuardHeadBytes))) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback guard has pending bytes without the pending flag"};
    }
    return guard;
}

const std::array<std::uint8_t, 4U> &record_magic(
    AuthorityLedgerFormat format) noexcept {
    switch (format) {
    case AuthorityLedgerFormat::v3:
        return kRecordMagicV3;
    case AuthorityLedgerFormat::v2:
        return kRecordMagicV2;
    case AuthorityLedgerFormat::v1:
        return kRecordMagicV1;
    }
    return kRecordMagicV1;
}

const std::array<std::uint8_t, 8U> &ledger_magic(
    AuthorityLedgerFormat format) noexcept {
    switch (format) {
    case AuthorityLedgerFormat::v3:
        return kLedgerMagicV3;
    case AuthorityLedgerFormat::v2:
        return kLedgerMagicV2;
    case AuthorityLedgerFormat::v1:
        return kLedgerMagicV1;
    }
    return kLedgerMagicV1;
}

std::uint8_t record_format_byte(AuthorityLedgerFormat format) noexcept {
    return static_cast<std::uint8_t>(format);
}

std::uint8_t ledger_format_byte(AuthorityLedgerFormat format) noexcept {
    return static_cast<std::uint8_t>(format);
}

std::string_view signature_domain(AuthorityLedgerFormat format) noexcept {
    switch (format) {
    case AuthorityLedgerFormat::v3:
        return kSignatureDomainV3;
    case AuthorityLedgerFormat::v2:
        return kSignatureDomainV2;
    case AuthorityLedgerFormat::v1:
        return kSignatureDomainV1;
    }
    return kSignatureDomainV1;
}

std::string_view digest_domain(AuthorityLedgerFormat format) noexcept {
    switch (format) {
    case AuthorityLedgerFormat::v3:
        return kDigestDomainV3;
    case AuthorityLedgerFormat::v2:
        return kDigestDomainV2;
    case AuthorityLedgerFormat::v1:
        return kDigestDomainV1;
    }
    return kDigestDomainV1;
}

Result<AuthorityLedgerFormat> record_format_from_prefix(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() < 5U) {
        return Status{ErrorCode::protocol_error,
                      "authority record prefix is truncated"};
    }
    if (std::equal(kRecordMagicV1.begin(), kRecordMagicV1.end(), bytes.begin()) &&
        bytes[4U] == kRecordFormatV1) {
        return AuthorityLedgerFormat::v1;
    }
    if (std::equal(kRecordMagicV2.begin(), kRecordMagicV2.end(), bytes.begin()) &&
        bytes[4U] == kRecordFormatV2) {
        return AuthorityLedgerFormat::v2;
    }
    if (std::equal(kRecordMagicV3.begin(), kRecordMagicV3.end(),
                   bytes.begin()) &&
        bytes[4U] == kRecordFormatV3) {
        return AuthorityLedgerFormat::v3;
    }
    return Status{ErrorCode::unsupported,
                  "authority record magic or format is unsupported"};
}

Result<AuthorityLedgerFormat> ledger_format_from_header(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kAuthorityLedgerHeaderBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority ledger header is truncated"};
    }
    if (std::equal(kLedgerMagicV1.begin(), kLedgerMagicV1.end(), bytes.begin()) &&
        bytes[8U] == kLedgerFormatV1 && bytes[9U] == kRecordFormatV1) {
        return AuthorityLedgerFormat::v1;
    }
    if (std::equal(kLedgerMagicV2.begin(), kLedgerMagicV2.end(), bytes.begin()) &&
        bytes[8U] == kLedgerFormatV2 && bytes[9U] == 0U) {
        return AuthorityLedgerFormat::v2;
    }
    if (std::equal(kLedgerMagicV3.begin(), kLedgerMagicV3.end(),
                   bytes.begin()) &&
        bytes[8U] == kLedgerFormatV3 && bytes[9U] == 0U) {
        return AuthorityLedgerFormat::v3;
    }
    return Status{ErrorCode::unsupported,
                  "authority ledger header format is unsupported"};
}

bool known_action(AuthorityAction action) noexcept {
    switch (action) {
        case AuthorityAction::bootstrap:
        case AuthorityAction::grant:
        case AuthorityAction::revoke:
        case AuthorityAction::epoch_transition:
        case AuthorityAction::migrate_v2:
        case AuthorityAction::migrate_v3:
            return true;
        }
    return false;
}

bool known_role(PrincipalRole role) noexcept {
    switch (role) {
        case PrincipalRole::none:
        case PrincipalRole::owner:
        case PrincipalRole::administrator:
        case PrincipalRole::operator_role:
        case PrincipalRole::viewer:
        case PrincipalRole::automation:
        case PrincipalRole::service:
            return true;
    }
    return false;
}

Result<std::vector<std::uint8_t>> signature_message(
    std::span<const std::uint8_t, kAuthorityRecordBodyBytes> body) {
    auto format = record_format_from_prefix(body);
    if (!format) {
        return format.status();
    }
    const std::string_view domain = signature_domain(format.value());
    std::vector<std::uint8_t> message;
    message.reserve(kSignaturePrefix.size() + 2U + domain.size() + body.size());
    message.insert(message.end(), kSignaturePrefix.begin(), kSignaturePrefix.end());
    message.push_back(static_cast<std::uint8_t>((domain.size() >> 8U) & 0xFFU));
    message.push_back(static_cast<std::uint8_t>(domain.size() & 0xFFU));
    message.insert(message.end(), domain.begin(), domain.end());
    message.insert(message.end(), body.begin(), body.end());
    return message;
}

PrincipalMap map_from_snapshot(const AuthoritySnapshot &snapshot) {
    PrincipalMap principals;
    for (const PrincipalState &principal : snapshot.principals) {
        principals.emplace(principal.public_key, principal);
    }
    return principals;
}

void snapshot_from_map(AuthoritySnapshot &snapshot, const PrincipalMap &principals) {
    snapshot.principals.clear();
    snapshot.principals.reserve(principals.size());
    for (const auto &[key, principal] : principals) {
        (void)key;
        snapshot.principals.push_back(principal);
    }
}

std::size_t active_owner_count(const PrincipalMap &principals) {
    return static_cast<std::size_t>(std::count_if(
        principals.begin(), principals.end(), [](const auto &entry) {
            return entry.second.active && entry.second.role == PrincipalRole::owner;
        }));
}

Status validate_grant_policy(
    const AuthorityRecord &record,
    const PrincipalState &issuer,
    const PrincipalMap &principals) {
    const std::uint64_t format_mask = authority_capability_mask(record.format);
    const std::uint64_t interactive =
        static_cast<std::uint64_t>(Capability::interactive_terminal);
    if (record.role == PrincipalRole::none) {
        return Status{ErrorCode::protocol_error, "grant record requires a non-none role"};
    }
    if (record.capabilities == 0U ||
        (record.capabilities & ~format_mask) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "grant record contains an empty or unknown capability set"};
    }
    if ((record.capabilities &
         ~role_capability_ceiling(record.role, record.format)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "grant record exceeds the fixed capability ceiling for its role"};
    }

    const std::uint64_t missing_from_issuer =
        record.capabilities & ~issuer.capabilities;
    const bool v2_owner_activation =
        record.format == AuthorityLedgerFormat::v2 &&
        issuer.role == PrincipalRole::owner &&
        (missing_from_issuer & ~interactive) == 0U;
    const std::uint64_t v3_extension_capabilities =
        kAuthorityV3Capabilities & ~kConstitutionalOwnerCapabilities;
    const bool v3_owner_activation =
        record.format == AuthorityLedgerFormat::v3 &&
        issuer.role == PrincipalRole::owner &&
        constant_time_equal(record.subject, issuer.public_key) &&
        (issuer.capabilities & ~record.capabilities) == 0U &&
        (missing_from_issuer & ~v3_extension_capabilities) == 0U;
    if (missing_from_issuer != 0U && !v2_owner_activation &&
        !v3_owner_activation) {
        return Status{ErrorCode::protocol_error,
                      "issuer attempted to grant capabilities it does not possess"};
    }
    if (record.role == PrincipalRole::owner && issuer.role != PrincipalRole::owner) {
        return Status{ErrorCode::protocol_error,
                      "only an active owner may grant another owner principal"};
    }
    if (record.role == PrincipalRole::owner &&
        (record.capabilities & kConstitutionalOwnerCapabilities) !=
            kConstitutionalOwnerCapabilities) {
        return Status{ErrorCode::protocol_error,
                      "owner principals must receive every constitutional capability"};
    }
    if (record.format == AuthorityLedgerFormat::v1 &&
        record.role == PrincipalRole::owner &&
        record.capabilities != kAuthorityV1Capabilities) {
        return Status{ErrorCode::protocol_error,
                      "owner principals must receive the complete v1 capability set"};
    }

    const auto subject = principals.find(record.subject);
    if (subject != principals.end() && subject->second.active &&
        subject->second.role == PrincipalRole::owner &&
        record.role != PrincipalRole::owner) {
        return Status{ErrorCode::protocol_error,
                      "an active owner may not be demoted by a grant; revoke explicitly first"};
    }
    return Status::success();
}

Status validate_revoke_policy(
    const AuthorityRecord &record,
    const PrincipalState &issuer,
    const PrincipalMap &principals) {
    if (record.role != PrincipalRole::none || record.capabilities != 0U) {
        return Status{ErrorCode::protocol_error,
                      "revoke record must use role none and zero capabilities"};
    }
    const auto subject = principals.find(record.subject);
    if (subject == principals.end() || !subject->second.active) {
        return Status{ErrorCode::protocol_error,
                      "revoke record subject is not an active principal"};
    }
    if (subject->second.role == PrincipalRole::owner &&
        issuer.role != PrincipalRole::owner) {
        return Status{ErrorCode::protocol_error,
                      "only an owner may revoke an owner principal"};
    }
    if (subject->second.role == PrincipalRole::owner &&
        active_owner_count(principals) <= 1U) {
        return Status{ErrorCode::protocol_error,
                      "authority ledger may not revoke its last active owner"};
    }
    return Status::success();
}

Status validate_epoch_transition_policy(
    const AuthorityRecord &record,
    const PrincipalState &issuer,
    const AuthoritySnapshot &snapshot) {
    if (record.role != PrincipalRole::owner ||
        !constant_time_equal(record.issuer, record.subject)) {
        return Status{ErrorCode::protocol_error,
                      "epoch transition must be a self-signed owner record"};
    }
    if (issuer.role != PrincipalRole::owner ||
        !constant_time_equal(snapshot.nominated_successor, record.issuer)) {
        return Status{ErrorCode::protocol_error,
                      "epoch transition issuer is not the immediately nominated successor owner"};
    }
    if (record.capabilities != issuer.capabilities ||
        (record.capabilities & kConstitutionalOwnerCapabilities) !=
            kConstitutionalOwnerCapabilities ||
        (record.capabilities & ~authority_capability_mask(record.format)) != 0U) {
        return Status{ErrorCode::protocol_error,
                      "epoch transition must preserve the nominated owner's exact capabilities"};
    }
    return Status::success();
}

Status validate_v2_migration_policy(
    const AuthorityRecord &record,
    const PrincipalState &issuer,
    const AuthoritySnapshot &snapshot) {
    if (snapshot.format != AuthorityLedgerFormat::v1 ||
        record.format != AuthorityLedgerFormat::v2 ||
        record.action != AuthorityAction::migrate_v2 ||
        record.role != PrincipalRole::owner ||
        issuer.role != PrincipalRole::owner ||
        record.capabilities != issuer.capabilities ||
        record.capabilities != kAuthorityV1Capabilities ||
        !constant_time_equal(record.issuer, record.subject)) {
        return Status{ErrorCode::protocol_error,
                      "authority v2 migration must be an exact self-signed v1 owner transition with no capability widening"};
    }
    return Status::success();
}

Status validate_v3_migration_policy(const AuthorityRecord &record,
                                    const PrincipalState &issuer,
                                    const AuthoritySnapshot &snapshot) {
    if (snapshot.format != AuthorityLedgerFormat::v2 ||
        record.format != AuthorityLedgerFormat::v3 ||
        record.action != AuthorityAction::migrate_v3 ||
        record.role != PrincipalRole::owner ||
        issuer.role != PrincipalRole::owner ||
        record.capabilities != issuer.capabilities ||
        (record.capabilities & ~kAuthorityV2Capabilities) != 0U ||
        !constant_time_equal(record.issuer, record.subject)) {
        return Status{ErrorCode::protocol_error,
                      "authority v3 migration must be an exact self-signed v2 "
                      "owner transition with no capability widening"};
    }
    return Status::success();
}

Result<std::vector<std::uint8_t>> read_private_bounded(
    const std::filesystem::path &path,
    std::size_t maximum_bytes,
    std::string_view label) {
    int descriptor = -1;
    do {
        descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        if (errno == ENOENT) {
            return Status{ErrorCode::not_found,
                          std::string(label) + " does not exist: " + path.string()};
        }
        return Status{ErrorCode::io_error,
                      "unable to open " + std::string(label) + " '" + path.string() + "': " +
                          std::strerror(errno)};
    }

    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        const int saved = errno;
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      "unable to inspect " + std::string(label) + " '" + path.string() + "': " +
                          std::strerror(saved)};
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid != ::geteuid()) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      std::string(label) + " must be a regular file owned by the running user: " +
                          path.string()};
    }
    if ((metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0) {
        (void)::close(descriptor);
        return Status{ErrorCode::io_error,
                      std::string(label) + " permissions must be private (0600): " + path.string()};
    }
    if (metadata.st_size < 0 ||
        static_cast<std::uintmax_t>(metadata.st_size) > maximum_bytes) {
        (void)::close(descriptor);
        return Status{ErrorCode::resource_exhausted,
                      std::string(label) + " exceeds its configured size bound"};
    }

    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(metadata.st_size));
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::read(
            descriptor, bytes.data() + static_cast<std::ptrdiff_t>(offset),
            bytes.size() - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            const int saved = errno;
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          "unable to read " + std::string(label) + " '" + path.string() + "': " +
                              std::strerror(saved)};
        }
        if (count == 0) {
            (void)::close(descriptor);
            return Status{ErrorCode::io_error,
                          std::string(label) + " ended before its declared size"};
        }
        offset += static_cast<std::size_t>(count);
    }
    if (::close(descriptor) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close " + std::string(label) + " '" + path.string() + "': " +
                          std::strerror(errno)};
    }
    return bytes;
}

Result<RollbackGuardState> read_rollback_guard_file(
    const std::filesystem::path &path) {
    auto bytes = read_private_bounded(
        path, kAuthorityRollbackGuardBytes, "authority rollback guard");
    if (!bytes) {
        return bytes.status();
    }
    return decode_rollback_guard(bytes.value());
}

Result<std::vector<std::uint8_t>> encode_witness_intent(
    const WitnessIntent &intent) {
    rollback_witness::Record committed;
    committed.domain = intent.domain;
    committed.device = intent.device;
    committed.witness_epoch = intent.witness_epoch;
    committed.lane = intent.lane;
    committed.committed = intent.current;
    auto pending = rollback_witness::begin(committed, intent.next,
                                           intent.nonce);
    if (!pending) return pending.status();

    std::vector<std::uint8_t> bytes(kWitnessIntentBytes, 0U);
    std::copy(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
              bytes.begin());
    bytes[8U] = 1U;
    bytes[9U] = static_cast<std::uint8_t>(intent.lane);
    std::copy(intent.domain.begin(), intent.domain.end(), bytes.begin() + 16U);
    std::copy(intent.device.begin(), intent.device.end(), bytes.begin() + 32U);
    put_u64(std::span<std::uint8_t>{bytes}.subspan(64U, 8U),
            intent.witness_epoch);
    put_u64(std::span<std::uint8_t>{bytes}.subspan(72U, 8U),
            intent.current.position);
    std::copy(intent.current.digest.begin(), intent.current.digest.end(),
              bytes.begin() + 80U);
    put_u64(std::span<std::uint8_t>{bytes}.subspan(112U, 8U),
            intent.next.position);
    std::copy(intent.next.digest.begin(), intent.next.digest.end(),
              bytes.begin() + 120U);
    std::copy(intent.nonce.begin(), intent.nonce.end(), bytes.begin() + 152U);
    std::copy(intent.record.begin(), intent.record.end(), bytes.begin() + 184U);
    return bytes;
}

Result<WitnessIntent> decode_witness_intent(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kWitnessIntentBytes ||
        !std::equal(kWitnessIntentMagic.begin(), kWitnessIntentMagic.end(),
                    bytes.begin()) ||
        bytes[8U] != 1U ||
        bytes[9U] !=
            static_cast<std::uint8_t>(rollback_witness::Lane::authority) ||
        !all_zero(bytes.subspan(10U, 6U)) ||
        !all_zero(bytes.subspan(440U, 8U))) {
        return Status{ErrorCode::protocol_error,
                      "authority witness intent shape, format, lane, or reserved bytes are invalid"};
    }
    WitnessIntent intent;
    std::copy_n(bytes.begin() + 16U, intent.domain.size(),
                intent.domain.begin());
    std::copy_n(bytes.begin() + 32U, intent.device.size(),
                intent.device.begin());
    intent.witness_epoch = get_u64(bytes.subspan(64U, 8U));
    intent.lane = rollback_witness::Lane::authority;
    intent.current.position = get_u64(bytes.subspan(72U, 8U));
    std::copy_n(bytes.begin() + 80U, intent.current.digest.size(),
                intent.current.digest.begin());
    intent.next.position = get_u64(bytes.subspan(112U, 8U));
    std::copy_n(bytes.begin() + 120U, intent.next.digest.size(),
                intent.next.digest.begin());
    std::copy_n(bytes.begin() + 152U, intent.nonce.size(),
                intent.nonce.begin());
    std::copy_n(bytes.begin() + 184U, intent.record.size(),
                intent.record.begin());
    auto canonical = encode_witness_intent(intent);
    if (!canonical || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(),
                    bytes.begin())) {
        return Status{ErrorCode::protocol_error,
                      "authority witness intent is not canonical"};
    }
    return intent;
}

Result<WitnessIntent> read_witness_intent(
    const std::filesystem::path &path) {
    auto bytes = read_private_bounded(path, kWitnessIntentBytes,
                                      "authority witness intent");
    if (!bytes) return bytes.status();
    return decode_witness_intent(bytes.value());
}

Status write_witness_intent(const std::filesystem::path &path,
                            const WitnessIntent &intent) {
    auto bytes = encode_witness_intent(intent);
    if (!bytes) return bytes.status();
    return StateStore::write_atomic(path, bytes.value());
}

Status remove_witness_intent(const std::filesystem::path &path) {
    const std::filesystem::path parent = path.has_parent_path()
        ? path.parent_path()
        : std::filesystem::path{"."};
    const int directory = ::open(parent.c_str(),
                                 O_RDONLY | O_DIRECTORY | O_CLOEXEC |
                                     O_NOFOLLOW);
    if (directory < 0) {
        return Status{ErrorCode::io_error,
                      "unable to open authority witness intent directory '" +
                          parent.string() + "': " + std::strerror(errno)};
    }
    struct stat metadata {};
    if (::fstatat(directory, path.filename().c_str(), &metadata,
                  AT_SYMLINK_NOFOLLOW) != 0) {
        const int error_number = errno;
        static_cast<void>(::close(directory));
        if (error_number == ENOENT) return Status::success();
        return Status{ErrorCode::io_error,
                      "unable to inspect authority witness intent '" +
                          path.string() + "': " +
                          std::strerror(error_number)};
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_nlink != 1 ||
        metadata.st_uid != ::geteuid() ||
        (metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0) {
        static_cast<void>(::close(directory));
        return Status{ErrorCode::protocol_error,
                      "authority witness intent is not one private owner-owned regular file"};
    }
    if (::unlinkat(directory, path.filename().c_str(), 0) != 0) {
        const int error_number = errno;
        static_cast<void>(::close(directory));
        return Status{ErrorCode::io_error,
                      "unable to remove authority witness intent '" +
                          path.string() + "': " +
                          std::strerror(error_number)};
    }
    if (::fsync(directory) != 0) {
        const int error_number = errno;
        static_cast<void>(::close(directory));
        return Status{ErrorCode::io_error,
                      "unable to fsync authority witness intent directory '" +
                          parent.string() + "': " +
                          std::strerror(error_number)};
    }
    if (::close(directory) != 0) {
        return Status{ErrorCode::io_error,
                      "unable to close authority witness intent directory '" +
                          parent.string() + "': " + std::strerror(errno)};
    }
    return Status::success();
}

Status write_rollback_guard_file(
    const std::filesystem::path &path,
    const RollbackGuardState &guard) {
    auto encoded = encode_rollback_guard(guard);
    if (!encoded) {
        return encoded.status();
    }
    return StateStore::write_atomic(path, encoded.value());
}

}  // namespace

std::string to_string(AuthorityLedgerFormat format) {
    switch (format) {
        case AuthorityLedgerFormat::v1: return "v1";
        case AuthorityLedgerFormat::v2: return "v2";
        case AuthorityLedgerFormat::v3:
            return "v3";
        }
    return "unknown";
}

std::string to_string(Capability capability) {
    switch (capability) {
        case Capability::read_telemetry: return "read.telemetry";
        case Capability::write_settings: return "write.settings";
        case Capability::actuate: return "actuate";
        case Capability::manage_principals: return "manage.principals";
        case Capability::install_firmware: return "install.firmware";
        case Capability::export_diagnostics: return "export.diagnostics";
        case Capability::factory_reset: return "factory.reset";
        case Capability::interactive_terminal: return "interactive.terminal";
        case Capability::sync_admin:
            return "sync.admin";
        case Capability::sync_publish:
            return "sync.publish";
        case Capability::sync_subscribe:
            return "sync.subscribe";
        case Capability::sync_activate:
            return "sync.activate";
        }
    return "unknown";
}

std::string to_string(PrincipalRole role) {
    switch (role) {
        case PrincipalRole::none: return "none";
        case PrincipalRole::owner: return "owner";
        case PrincipalRole::administrator: return "administrator";
        case PrincipalRole::operator_role: return "operator";
        case PrincipalRole::viewer: return "viewer";
        case PrincipalRole::automation: return "automation";
        case PrincipalRole::service: return "service";
    }
    return "unknown";
}

std::string to_string(AuthorityAction action) {
    switch (action) {
        case AuthorityAction::bootstrap: return "bootstrap";
        case AuthorityAction::grant: return "grant";
        case AuthorityAction::revoke: return "revoke";
        case AuthorityAction::epoch_transition: return "epoch-transition";
        case AuthorityAction::migrate_v2: return "migrate-v2";
        case AuthorityAction::migrate_v3:
            return "migrate-v3";
        }
    return "unknown";
}

Result<PrincipalRole> parse_principal_role(std::string_view value) {
    if (value == "owner") return PrincipalRole::owner;
    if (value == "administrator" || value == "admin") return PrincipalRole::administrator;
    if (value == "operator") return PrincipalRole::operator_role;
    if (value == "viewer") return PrincipalRole::viewer;
    if (value == "automation") return PrincipalRole::automation;
    if (value == "service") return PrincipalRole::service;
    if (value == "none") return PrincipalRole::none;
    return Status{ErrorCode::invalid_argument,
                  "unknown principal role: " + std::string(value)};
}

Result<std::uint64_t> parse_capability_set(std::string_view value) {
    if (value == "all") {
        return kAuthorityV1Capabilities;
    }
    if (value == "all-v1" || value == "legacy-all") {
        return kAuthorityV1Capabilities;
    }
    if (value == "all-v2" || value == "all-with-terminal") {
        return kAuthorityV2Capabilities;
    }
    if (value == "all-v3" || value == "all-with-sync") {
        return kAuthorityV3Capabilities;
    }
    if (value == "none" || value.empty()) {
        return static_cast<std::uint64_t>(0U);
    }
    std::uint64_t capabilities = 0U;
    std::size_t begin = 0U;
    while (begin <= value.size()) {
        const std::size_t comma = value.find(',', begin);
        const std::string_view token = comma == std::string_view::npos
                                           ? value.substr(begin)
                                           : value.substr(begin, comma - begin);
        Capability capability{};
        if (token == "read.telemetry") capability = Capability::read_telemetry;
        else if (token == "write.settings") capability = Capability::write_settings;
        else if (token == "actuate") capability = Capability::actuate;
        else if (token == "manage.principals") capability = Capability::manage_principals;
        else if (token == "install.firmware") capability = Capability::install_firmware;
        else if (token == "export.diagnostics") capability = Capability::export_diagnostics;
        else if (token == "factory.reset") capability = Capability::factory_reset;
        else if (token == "interactive.terminal") capability = Capability::interactive_terminal;
        else if (token == "sync.admin")
            capability = Capability::sync_admin;
        else if (token == "sync.publish")
            capability = Capability::sync_publish;
        else if (token == "sync.subscribe")
            capability = Capability::sync_subscribe;
        else if (token == "sync.activate")
            capability = Capability::sync_activate;
        else {
            return Status{ErrorCode::invalid_argument,
                          "unknown capability: " + std::string(token)};
        }
        const std::uint64_t bit = static_cast<std::uint64_t>(capability);
        if ((capabilities & bit) != 0U) {
            return Status{ErrorCode::invalid_argument,
                          "capability appears more than once: " + std::string(token)};
        }
        capabilities |= bit;
        if (comma == std::string_view::npos) {
            break;
        }
        begin = comma + 1U;
        if (begin == value.size()) {
            return Status{ErrorCode::invalid_argument,
                          "capability list may not end with a comma"};
        }
    }
    return capabilities;
}

std::string render_capability_set(std::uint64_t capabilities) {
    if (capabilities == 0U) {
        return "none";
    }
    std::ostringstream output;
    bool first = true;
    for (const Capability capability :
         {Capability::read_telemetry, Capability::write_settings,
          Capability::actuate, Capability::manage_principals,
          Capability::install_firmware, Capability::export_diagnostics,
          Capability::factory_reset, Capability::interactive_terminal,
          Capability::sync_admin, Capability::sync_publish,
          Capability::sync_subscribe, Capability::sync_activate}) {
        const std::uint64_t bit = static_cast<std::uint64_t>(capability);
        if ((capabilities & bit) == 0U) {
            continue;
        }
        if (!first) {
            output << ',';
        }
        output << to_string(capability);
        first = false;
    }
    if ((capabilities & ~kAuthorityV3Capabilities) != 0U) {
        if (!first) {
            output << ',';
        }
        output << "unknown(0x" << std::hex
               << (capabilities & ~kAuthorityV3Capabilities) << ')';
    }
    return output.str();
}

std::uint64_t authority_capability_mask(
    AuthorityLedgerFormat format) noexcept {
    switch (format) {
        case AuthorityLedgerFormat::v1:
            return kAuthorityV1Capabilities;
        case AuthorityLedgerFormat::v2:
            return kAuthorityV2Capabilities;
        case AuthorityLedgerFormat::v3:
            return kAuthorityV3Capabilities;
        }
    return 0U;
}

std::uint64_t role_capability_ceiling(
    PrincipalRole role, AuthorityLedgerFormat format) noexcept {
    const auto bit = [](Capability capability) {
        return static_cast<std::uint64_t>(capability);
    };
    const std::uint64_t mask = authority_capability_mask(format);
    switch (role) {
        case PrincipalRole::owner:
            return mask;
        case PrincipalRole::administrator:
            return mask & ~bit(Capability::factory_reset);
        case PrincipalRole::operator_role:
            return (bit(Capability::read_telemetry) |
                    bit(Capability::write_settings) | bit(Capability::actuate) |
                    bit(Capability::interactive_terminal) |
                    bit(Capability::sync_subscribe) |
                    bit(Capability::sync_activate)) &
                   mask;
        case PrincipalRole::viewer:
            return (bit(Capability::read_telemetry) |
                    bit(Capability::sync_subscribe)) &
                   mask;
        case PrincipalRole::automation:
            return (bit(Capability::read_telemetry) |
                    bit(Capability::write_settings) | bit(Capability::actuate) |
                    bit(Capability::sync_publish) |
                    bit(Capability::sync_subscribe) |
                    bit(Capability::sync_activate)) &
                   mask;
        case PrincipalRole::service:
            return (bit(Capability::read_telemetry) |
                    bit(Capability::write_settings) |
                    bit(Capability::export_diagnostics) |
                    bit(Capability::sync_publish) |
                    bit(Capability::sync_subscribe)) &
                   mask;
        case PrincipalRole::none:
            return 0U;
    }
    return 0U;
}

Result<std::vector<std::uint8_t>> encode_authority_prepare_request(
    const AuthorityPrepareRequest &request) {
    if (!known_action(request.action) || !known_role(request.role) ||
        (request.capabilities & ~kAuthorityV3Capabilities) != 0U ||
        all_zero(request.issuer) || all_zero(request.subject)) {
        return Status{ErrorCode::invalid_argument,
                      "authority prepare request contains an invalid action, role, capability, or key"};
    }
    std::vector<std::uint8_t> bytes(kAuthorityPrepareBytes, 0U);
    bytes[0U] = static_cast<std::uint8_t>(request.action);
    bytes[1U] = static_cast<std::uint8_t>(request.role);
    put_u64(std::span<std::uint8_t>{bytes}.subspan(8U, 8U), request.capabilities);
    std::copy(request.issuer.begin(), request.issuer.end(), bytes.begin() + 16U);
    std::copy(request.subject.begin(), request.subject.end(), bytes.begin() + 48U);
    return bytes;
}

Result<AuthorityPrepareRequest> decode_authority_prepare_request(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityPrepareBytes) {
        return Status{ErrorCode::invalid_argument,
                      "authority prepare request must contain exactly 80 bytes"};
    }
    for (std::size_t index = 2U; index < 8U; ++index) {
        if (bytes[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority prepare request reserved bytes are non-zero"};
        }
    }
    AuthorityPrepareRequest request;
    request.action = static_cast<AuthorityAction>(bytes[0U]);
    request.role = static_cast<PrincipalRole>(bytes[1U]);
    request.capabilities = get_u64(bytes.subspan(8U, 8U));
    std::copy_n(bytes.begin() + 16U, request.issuer.size(), request.issuer.begin());
    std::copy_n(bytes.begin() + 48U, request.subject.size(), request.subject.begin());
    if (!known_action(request.action) || !known_role(request.role) ||
        (request.capabilities & ~kAuthorityV3Capabilities) != 0U ||
        all_zero(request.issuer) || all_zero(request.subject)) {
        return Status{ErrorCode::protocol_error,
                      "authority prepare request has an unknown value or zero key"};
    }
    return request;
}

Result<AuthorityRecordBody> encode_authority_record_body(
    const AuthorityRecord &record) {
    if (!known_format(record.format) || !known_action(record.action) ||
        !known_role(record.role) || record.sequence == 0U ||
        record.ownership_epoch == 0U ||
        (record.capabilities & ~authority_capability_mask(record.format)) != 0U ||
        all_zero(record.device) || all_zero(record.issuer) ||
        all_zero(record.subject)) {
        return Status{ErrorCode::invalid_argument,
                      "authority record body contains an invalid field"};
    }
    if (record.action == AuthorityAction::migrate_v2 &&
        record.format != AuthorityLedgerFormat::v2) {
        return Status{ErrorCode::invalid_argument,
                      "authority migration records require v2 format"};
    }
    if (record.action == AuthorityAction::migrate_v3 &&
        record.format != AuthorityLedgerFormat::v3) {
        return Status{ErrorCode::invalid_argument,
                      "authority v3 migration records require v3 format"};
    }
    AuthorityRecordBody body{};
    const auto &magic = record_magic(record.format);
    std::copy(magic.begin(), magic.end(), body.begin());
    body[4U] = record_format_byte(record.format);
    body[5U] = static_cast<std::uint8_t>(record.action);
    body[6U] = static_cast<std::uint8_t>(record.role);
    body[7U] = 0U;
    put_u64(std::span<std::uint8_t>{body}.subspan(8U, 8U), record.sequence);
    put_u64(std::span<std::uint8_t>{body}.subspan(16U, 8U), record.ownership_epoch);
    put_u64(std::span<std::uint8_t>{body}.subspan(24U, 8U), record.not_before_unix_ms);
    put_u64(std::span<std::uint8_t>{body}.subspan(32U, 8U), record.not_after_unix_ms);
    put_u64(std::span<std::uint8_t>{body}.subspan(40U, 8U), record.capabilities);
    std::copy(record.device.begin(), record.device.end(), body.begin() + 48U);
    std::copy(record.issuer.begin(), record.issuer.end(), body.begin() + 80U);
    std::copy(record.subject.begin(), record.subject.end(), body.begin() + 112U);
    std::copy(record.previous_digest.begin(), record.previous_digest.end(), body.begin() + 144U);
    return body;
}

Result<AuthorityRecord> decode_authority_record(
    std::span<const std::uint8_t> bytes) {
    if (bytes.size() != kAuthorityRecordBytes) {
        return Status{ErrorCode::protocol_error,
                      "authority record must contain exactly 256 bytes"};
    }
    auto format = record_format_from_prefix(bytes);
    if (!format) {
        return format.status();
    }
    if (bytes[7U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority record flags are invalid"};
    }
    for (std::size_t index = 176U; index < 192U; ++index) {
        if (bytes[index] != 0U) {
            return Status{ErrorCode::protocol_error,
                          "authority record reserved bytes are non-zero"};
        }
    }
    AuthorityRecord record;
    record.format = format.value();
    record.action = static_cast<AuthorityAction>(bytes[5U]);
    record.role = static_cast<PrincipalRole>(bytes[6U]);
    record.sequence = get_u64(bytes.subspan(8U, 8U));
    record.ownership_epoch = get_u64(bytes.subspan(16U, 8U));
    record.not_before_unix_ms = get_u64(bytes.subspan(24U, 8U));
    record.not_after_unix_ms = get_u64(bytes.subspan(32U, 8U));
    record.capabilities = get_u64(bytes.subspan(40U, 8U));
    std::copy_n(bytes.begin() + 48U, record.device.size(), record.device.begin());
    std::copy_n(bytes.begin() + 80U, record.issuer.size(), record.issuer.begin());
    std::copy_n(bytes.begin() + 112U, record.subject.size(), record.subject.begin());
    std::copy_n(bytes.begin() + 144U, record.previous_digest.size(), record.previous_digest.begin());
    std::copy_n(bytes.begin() + 192U, record.signature.size(), record.signature.begin());
    if (!known_action(record.action) || !known_role(record.role) ||
        record.sequence == 0U || record.ownership_epoch == 0U ||
        (record.capabilities & ~authority_capability_mask(record.format)) != 0U ||
        all_zero(record.device) || all_zero(record.issuer) || all_zero(record.subject)) {
        return Status{ErrorCode::protocol_error,
                      "authority record contains an unknown value, zero sequence, or zero key"};
    }
    if (record.action == AuthorityAction::migrate_v2 &&
        record.format != AuthorityLedgerFormat::v2) {
        return Status{ErrorCode::protocol_error,
                      "authority migration record is not encoded as v2"};
    }
    if (record.action == AuthorityAction::migrate_v3 &&
        record.format != AuthorityLedgerFormat::v3) {
        return Status{ErrorCode::protocol_error,
                      "authority v3 migration record is not encoded as v3"};
    }
    return record;
}

Result<AuthorityRecordBytes> sign_authority_record_body(
    std::span<const std::uint8_t, kAuthorityRecordBodyBytes> body,
    std::span<const std::uint8_t, kSigningSecretKeyBytes> secret_key,
    const Sodium &sodium) {
    auto message = signature_message(body);
    if (!message) {
        return message.status();
    }
    auto signature = sodium.sign_detached(message.value(), secret_key);
    secure_wipe(message.value());
    if (!signature) {
        return signature.status();
    }
    AuthorityRecordBytes bytes{};
    std::copy(body.begin(), body.end(), bytes.begin());
    std::copy(signature.value().begin(), signature.value().end(), bytes.begin() + 192U);
    return bytes;
}

Result<Digest> authority_record_digest(
    std::span<const std::uint8_t, kAuthorityRecordBytes> record,
    const Sodium &sodium) {
    auto format = record_format_from_prefix(record);
    if (!format) {
        return format.status();
    }
    return sodium.hash(digest_domain(format.value()), record);
}

Result<SigningSeed> derive_owner_signing_seed(
    const RecoveryRoot &root, const Sodium &sodium) {
    auto derived = sodium.derive_key(kOwnerSeedDomain, root.bytes());
    if (!derived) {
        return derived.status();
    }
    SigningSeed seed = derived.value();
    return seed;
}

Result<std::unique_ptr<AuthorityLedger>> AuthorityLedger::open(
    Config config,
    const SigningPublicKey &device,
    const Sodium &sodium) {
    if (config.path.empty()) {
        return Status{ErrorCode::invalid_argument, "authority ledger path is empty"};
    }
    if (config.maximum_records == 0U || config.maximum_records > (1U << 20U)) {
        return Status{ErrorCode::invalid_argument,
                      "authority ledger maximum record count must be in 1..1048576"};
    }
    if (all_zero(device)) {
        return Status{ErrorCode::invalid_argument,
                      "authority ledger requires a non-zero device public key"};
    }
    if (config.rollback_guard_path.empty()) {
        config.rollback_guard_path =
            default_authority_rollback_guard_path(config.path);
    }
    if (config.rollback_guard_path.empty() ||
        config.rollback_guard_path == config.path) {
        return Status{ErrorCode::invalid_argument,
                      "authority rollback guard path must be distinct from the ledger path"};
    }
    if (config.rollback_witness) {
        if (all_zero(config.rollback_witness_domain) ||
            config.rollback_witness_epoch == 0U) {
            return Status{ErrorCode::invalid_argument,
                          "authority rollback witness requires a nonzero domain and epoch"};
        }
        if (!config.rollback_witness->independently_controlled() &&
            !config.allow_non_independent_witness_for_testing) {
            return Status{
                ErrorCode::invalid_argument,
                "authority rollback witness is not independently controlled; only the explicit test exception may use a same-domain backend"};
        }
        if (config.rollback_witness_intent_path.empty()) {
            config.rollback_witness_intent_path = config.path;
            config.rollback_witness_intent_path += ".witness-intent";
        }
        if (config.rollback_witness_intent_path == config.path ||
            config.rollback_witness_intent_path ==
                config.rollback_guard_path) {
            return Status{ErrorCode::invalid_argument,
                          "authority witness intent must be distinct from ledger and guard"};
        }
    } else if (!all_zero(config.rollback_witness_domain) ||
               config.rollback_witness_epoch != 0U ||
               !config.rollback_witness_intent_path.empty() ||
               config.allow_non_independent_witness_for_testing) {
        return Status{ErrorCode::invalid_argument,
                      "authority witness parameters require a witness backend"};
    }
    auto ledger = std::unique_ptr<AuthorityLedger>(
        new AuthorityLedger(std::move(config), device, sodium));
    const Status loaded = ledger->load();
    if (!loaded.ok()) {
        return loaded;
    }
    const Status witnessed = ledger->reconcile_rollback_witness();
    if (!witnessed.ok()) return witnessed;
    return ledger;
}

Status AuthorityLedger::load() {
    const std::size_t maximum_bytes =
        kAuthorityLedgerHeaderBytes + config_.maximum_records * kAuthorityRecordBytes;
    auto bytes = read_private_bounded(config_.path, maximum_bytes, "authority ledger");
    if (!bytes) {
        if (bytes.status().code() == ErrorCode::not_found) {
            AuthoritySnapshot empty;
            empty.device = device_;
            empty.format = AuthorityLedgerFormat::v1;
            const Status guarded = verify_or_adopt_rollback_guard(empty, false);
            if (!guarded.ok()) {
                return guarded;
            }
            std::scoped_lock lock(mutex_);
            records_.clear();
            snapshot_ = std::move(empty);
            return Status::success();
        }
        return bytes.status();
    }
    auto header_format = ledger_format_from_header(bytes.value());
    if (!header_format) {
        return header_format.status();
    }
    if (bytes.value()[10U] != 0U || bytes.value()[11U] != 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority ledger reserved header bytes are nonzero"};
    }
    const std::uint32_t count = get_u32(
        std::span<const std::uint8_t>{bytes.value()}.subspan(12U, 4U));
    if (count > config_.maximum_records) {
        return Status{ErrorCode::resource_exhausted,
                      "authority ledger record count exceeds configured maximum"};
    }
    const std::size_t expected =
        kAuthorityLedgerHeaderBytes + static_cast<std::size_t>(count) * kAuthorityRecordBytes;
    if (bytes.value().size() != expected) {
        return Status{ErrorCode::protocol_error,
                      "authority ledger byte length does not match its record count"};
    }

    std::vector<AuthorityRecordBytes> loaded_records(count);
    for (std::size_t index = 0U; index < loaded_records.size(); ++index) {
        const std::size_t offset = kAuthorityLedgerHeaderBytes + index * kAuthorityRecordBytes;
        std::copy_n(
            bytes.value().begin() + static_cast<std::ptrdiff_t>(offset),
            kAuthorityRecordBytes, loaded_records[index].begin());
    }
    AuthoritySnapshot rebuilt;
    rebuilt.device = device_;
    const Status replayed = replay(loaded_records, rebuilt);
    if (!replayed.ok()) {
        return replayed;
    }
    if (rebuilt.format != header_format.value()) {
        return Status{ErrorCode::protocol_error,
                      "authority ledger header format does not match its signed record history"};
    }
    const Status guarded = verify_or_adopt_rollback_guard(rebuilt, true);
    if (!guarded.ok()) {
        return guarded;
    }

    std::scoped_lock lock(mutex_);
    records_ = std::move(loaded_records);
    snapshot_ = std::move(rebuilt);
    return Status::success();
}

Status AuthorityLedger::verify_or_adopt_rollback_guard(
    const AuthoritySnapshot &snapshot,
    bool ledger_present) {
    const RollbackGuardHead current = rollback_guard_head(snapshot);
    auto loaded = read_rollback_guard_file(config_.rollback_guard_path);
    if (!loaded) {
        if (loaded.status().code() != ErrorCode::not_found) {
            return loaded.status();
        }
        if (snapshot.initialized &&
            (snapshot.format == AuthorityLedgerFormat::v2 ||
             snapshot.format == AuthorityLedgerFormat::v3)) {
            return Status{
                ErrorCode::protocol_error,
                "persisted authority-ledger v2/v3 is missing its rollback guard"};
        }
        if (!ledger_present) {
            rollback_guard_established_ = false;
            return Status::success();
        }

        RollbackGuardState adopted;
        adopted.device = device_;
        adopted.committed = current;
        const Status written = write_rollback_guard_file(
            config_.rollback_guard_path, adopted);
        if (!written.ok()) {
            return Status{
                written.code(),
                "unable to adopt legacy authority-ledger v1 into the rollback guard: " +
                    written.message()};
        }
        rollback_guard_established_ = true;
        return Status::success();
    }

    RollbackGuardState guard = loaded.value();
    if (!constant_time_equal(guard.device, device_)) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback guard is bound to another device identity"};
    }

    const bool matches_committed = guard.committed == current;
    const bool matches_pending =
        guard.has_pending && guard.pending == current;
    if (!matches_committed && !matches_pending) {
        return Status{
            ErrorCode::protocol_error,
            "authority ledger head does not match the rollback guard; rollback, deletion, or fork detected"};
    }

    if (guard.has_pending) {
        // `current == pending` is an interrupted final guard commit after the
        // ledger replace. `current == committed` is an interrupted or failed
        // ledger replace. Both exact states are recoverable; every third head
        // is rejected above.
        if (matches_pending) {
            guard.committed = current;
        }
        guard.has_pending = false;
        guard.pending = {};
        const Status reconciled = write_rollback_guard_file(
            config_.rollback_guard_path, guard);
        if (!reconciled.ok()) {
            return Status{
                reconciled.code(),
                "unable to reconcile the authority rollback guard: " +
                    reconciled.message()};
        }
    }

    rollback_guard_established_ = true;
    return Status::success();
}

Status AuthorityLedger::begin_rollback_guard_transition(
    const AuthoritySnapshot &current_snapshot,
    const AuthoritySnapshot &next_snapshot) {
    const RollbackGuardHead current = rollback_guard_head(current_snapshot);
    const RollbackGuardHead next = rollback_guard_head(next_snapshot);
    auto loaded = read_rollback_guard_file(config_.rollback_guard_path);

    RollbackGuardState guard;
    if (!loaded) {
        if (loaded.status().code() != ErrorCode::not_found) {
            return loaded.status();
        }
        if (rollback_guard_established_ ||
            (current_snapshot.initialized &&
             (current_snapshot.format == AuthorityLedgerFormat::v2 ||
              current_snapshot.format == AuthorityLedgerFormat::v3))) {
            return Status{ErrorCode::protocol_error,
                          "authority rollback guard disappeared during the live ledger session"};
        }
        guard.device = device_;
        guard.committed = current;
    } else {
        guard = loaded.value();
        if (!constant_time_equal(guard.device, device_)) {
            return Status{ErrorCode::protocol_error,
                          "authority rollback guard is bound to another device identity"};
        }

        if (guard.has_pending) {
            if (guard.pending == current) {
                guard.committed = current;
            } else if (!(guard.committed == current)) {
                return Status{
                    ErrorCode::protocol_error,
                    "authority rollback guard pending transition does not match the live ledger head"};
            }
            guard.has_pending = false;
            guard.pending = {};
        } else if (!(guard.committed == current)) {
            return Status{
                ErrorCode::protocol_error,
                "authority ledger head diverged from its live rollback guard"};
        }
    }

    guard.committed = current;
    guard.has_pending = true;
    guard.pending = next;
    const Status written = write_rollback_guard_file(
        config_.rollback_guard_path, guard);
    if (!written.ok()) {
        return Status{
            written.code(),
            "unable to publish the authority rollback guard transition: " +
                written.message()};
    }
    rollback_guard_established_ = true;
    return Status::success();
}

Status AuthorityLedger::finish_rollback_guard_transition(
    const AuthoritySnapshot &current_snapshot) {
    const RollbackGuardHead current = rollback_guard_head(current_snapshot);
    auto loaded = read_rollback_guard_file(config_.rollback_guard_path);
    if (!loaded) {
        return Status{
            loaded.status().code(),
            "authority ledger advanced but its rollback guard cannot be read: " +
                loaded.status().message()};
    }
    RollbackGuardState guard = loaded.value();
    if (!constant_time_equal(guard.device, device_)) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback guard is bound to another device identity"};
    }
    if (!guard.has_pending) {
        if (guard.committed == current) {
            return Status::success();
        }
        return Status{
            ErrorCode::protocol_error,
            "authority rollback guard lost the pending head for the committed ledger"};
    }
    if (!(guard.pending == current)) {
        return Status{
            ErrorCode::protocol_error,
            "authority rollback guard pending head does not match the committed ledger"};
    }
    guard.committed = current;
    guard.has_pending = false;
    guard.pending = {};
    const Status written = write_rollback_guard_file(
        config_.rollback_guard_path, guard);
    if (!written.ok()) {
        return Status{
            written.code(),
            "authority ledger committed but final rollback guard publication failed: " +
                written.message()};
    }
    return Status::success();
}

Status AuthorityLedger::reconcile_rollback_witness() {
    if (!config_.rollback_witness) return Status::success();
    std::scoped_lock lock(mutex_);
    auto observed = config_.rollback_witness->query();
    if (!observed) {
        return Status{observed.status().code(),
                      "unable to query authority rollback witness: " +
                          observed.status().message()};
    }
    const Status valid = rollback_witness::validate(observed.value());
    if (!valid.ok()) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback witness returned an invalid record: " +
                          valid.message()};
    }
    if (observed.value().domain != config_.rollback_witness_domain ||
        !constant_time_equal(observed.value().device, device_) ||
        observed.value().witness_epoch != config_.rollback_witness_epoch ||
        observed.value().lane != rollback_witness::Lane::authority) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback witness identity, device, epoch, or lane does not match configuration"};
    }

    auto loaded_intent =
        read_witness_intent(config_.rollback_witness_intent_path);
    const bool has_intent = loaded_intent.ok();
    if (!has_intent &&
        loaded_intent.status().code() != ErrorCode::not_found) {
        return loaded_intent.status();
    }
    const rollback_witness::Head local = witness_head(snapshot_);

    const auto intent_identity_valid = [&](const WitnessIntent &intent) {
        return intent.domain == config_.rollback_witness_domain &&
            constant_time_equal(intent.device, device_) &&
            intent.witness_epoch == config_.rollback_witness_epoch &&
            intent.lane == rollback_witness::Lane::authority;
    };

    if (!observed.value().pending) {
        if (!(local == observed.value().committed)) {
            return Status{
                ErrorCode::protocol_error,
                "authority ledger does not match the independently committed witness head; rollback, deletion, or fork detected"};
        }
        if (!has_intent) return Status::success();
        const WitnessIntent &intent = loaded_intent.value();
        if (!intent_identity_valid(intent)) {
            return Status{ErrorCode::protocol_error,
                          "authority witness intent identity does not match configuration"};
        }
        if (intent.current == local) {
            // The intent was durable but the external pending CAS did not
            // become visible. No authoritative local state was advanced.
            return remove_witness_intent(
                config_.rollback_witness_intent_path);
        }
        if (intent.next == local && !records_.empty() &&
            records_.back() == intent.record) {
            // The witness commit landed and only intent cleanup was lost.
            return remove_witness_intent(
                config_.rollback_witness_intent_path);
        }
        return Status{ErrorCode::protocol_error,
                      "authority witness intent does not join the committed local and external head"};
    }

    if (!has_intent) {
        return Status{
            ErrorCode::protocol_error,
            "authority rollback witness is pending but the required durable local intent is missing"};
    }
    const WitnessIntent &intent = loaded_intent.value();
    if (!intent_identity_valid(intent) ||
        !(intent.current == observed.value().committed) ||
        !(intent.next == *observed.value().pending) ||
        intent.nonce != *observed.value().nonce) {
        return Status{ErrorCode::protocol_error,
                      "authority witness pending transition does not match the exact local intent"};
    }

    if (local == intent.current) {
        AuthoritySnapshot next = snapshot_;
        const Status applied = apply(intent.record, next);
        if (!applied.ok() || !(witness_head(next) == intent.next)) {
            return Status{ErrorCode::protocol_error,
                          "authority witness intent record does not produce its declared next head"};
        }
        const Status guarded = begin_rollback_guard_transition(snapshot_, next);
        if (!guarded.ok()) return guarded;
        std::vector<AuthorityRecordBytes> next_records = records_;
        next_records.push_back(intent.record);
        const Status written = write_records(next_records, next.format);
        if (!written.ok()) return written;
        records_ = std::move(next_records);
        snapshot_ = std::move(next);
        const Status guard_finished =
            finish_rollback_guard_transition(snapshot_);
        if (!guard_finished.ok()) return guard_finished;
    } else if (!(local == intent.next) || records_.empty() ||
               !(records_.back() == intent.record)) {
        return Status{ErrorCode::protocol_error,
                      "authority local head is neither exact side of the pending witness transition"};
    }

    auto committed = rollback_witness::finish(observed.value());
    if (!committed) return committed.status();
    const Status exchanged = config_.rollback_witness->compare_exchange(
        observed.value(), committed.value());
    if (!exchanged.ok()) {
        auto resolved = config_.rollback_witness->query();
        if (!resolved || !(resolved.value() == committed.value())) {
            return Status{
                exchanged.code(),
                "unable to commit recovered authority witness transition: " +
                    exchanged.message()};
        }
    }
    return remove_witness_intent(config_.rollback_witness_intent_path);
}

Status AuthorityLedger::begin_rollback_witness_transition(
    const AuthoritySnapshot &current, const AuthoritySnapshot &next,
    const AuthorityRecordBytes &record,
    rollback_witness::Record &committed,
    rollback_witness::Record &pending) {
    if (!config_.rollback_witness) return Status::success();
    auto observed = config_.rollback_witness->query();
    if (!observed) {
        return Status{observed.status().code(),
                      "unable to query authority rollback witness before mutation: " +
                          observed.status().message()};
    }
    committed = expected_witness_record(config_, device_, current);
    const Status valid = rollback_witness::validate(observed.value());
    if (!valid.ok() || !(observed.value() == committed)) {
        return Status{ErrorCode::protocol_error,
                      "authority rollback witness does not equal the exact current ledger head"};
    }
    rollback_witness::TransactionNonce nonce{};
    const Status random = fill_random(nonce);
    if (!random.ok()) return random;
    auto next_record = rollback_witness::begin(
        committed, witness_head(next), nonce);
    if (!next_record) return next_record.status();
    pending = next_record.value();
    WitnessIntent intent;
    intent.domain = config_.rollback_witness_domain;
    intent.device = device_;
    intent.witness_epoch = config_.rollback_witness_epoch;
    intent.current = committed.committed;
    intent.next = witness_head(next);
    intent.nonce = nonce;
    intent.record = record;
    const Status intent_written = write_witness_intent(
        config_.rollback_witness_intent_path, intent);
    if (!intent_written.ok()) return intent_written;
    const Status exchanged = config_.rollback_witness->compare_exchange(
        committed, pending);
    if (!exchanged.ok()) {
        auto resolved = config_.rollback_witness->query();
        if (!resolved || !(resolved.value() == pending)) {
            return Status{
                exchanged.code(),
                "unable to begin authority rollback witness transition: " +
                    exchanged.message()};
        }
    }
    return Status::success();
}

Status AuthorityLedger::finish_rollback_witness_transition(
    const rollback_witness::Record &pending) {
    if (!config_.rollback_witness) return Status::success();
    auto committed = rollback_witness::finish(pending);
    if (!committed) return committed.status();
    const Status exchanged = config_.rollback_witness->compare_exchange(
        pending, committed.value());
    if (!exchanged.ok()) {
        auto resolved = config_.rollback_witness->query();
        if (!resolved || !(resolved.value() == committed.value())) {
            return Status{
                exchanged.code(),
                "authority ledger committed locally but external witness commit remains unresolved: " +
                    exchanged.message()};
        }
    }
    return remove_witness_intent(config_.rollback_witness_intent_path);
}

Status AuthorityLedger::replay(
    std::span<const AuthorityRecordBytes> records,
    AuthoritySnapshot &snapshot) const {
    snapshot = {};
    snapshot.device = device_;
    for (const AuthorityRecordBytes &record : records) {
        const Status status = apply(record, snapshot);
        if (!status.ok()) {
            return Status{status.code(),
                          "authority ledger replay failed at record " +
                              std::to_string(snapshot.record_count + 1U) + ": " +
                              status.message()};
        }
    }
    return Status::success();
}

Status AuthorityLedger::apply(
    const AuthorityRecordBytes &bytes,
    AuthoritySnapshot &snapshot) const {
    auto decoded = decode_authority_record(bytes);
    if (!decoded) {
        return decoded.status();
    }
    const AuthorityRecord &record = decoded.value();
    if (!constant_time_equal(record.device, device_)) {
        return Status{ErrorCode::protocol_error,
                      "authority record is bound to a different IoTox device identity"};
    }
    if (record.not_before_unix_ms != 0U || record.not_after_unix_ms != 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority ledgers require zero time fields; trusted-clock policy is not implemented"};
    }

    AuthorityRecordBody body{};
    std::copy_n(bytes.begin(), body.size(), body.begin());
    auto message = signature_message(body);
    if (!message) {
        return message.status();
    }
    const Status signature_status = sodium_->verify_detached(
        record.signature, message.value(), record.issuer);
    secure_wipe(message.value());
    if (!signature_status.ok()) {
        return signature_status;
    }

    auto digest = authority_record_digest(bytes, *sodium_);
    if (!digest) {
        return digest.status();
    }

    PrincipalMap principals = map_from_snapshot(snapshot);
    if (!snapshot.initialized) {
        if (record.format != AuthorityLedgerFormat::v1 ||
            record.action != AuthorityAction::bootstrap || record.sequence != 1U ||
            record.ownership_epoch != 1U || record.role != PrincipalRole::owner ||
            record.capabilities != kAuthorityV1Capabilities ||
            !constant_time_equal(record.issuer, record.subject) ||
            !all_zero(record.previous_digest)) {
            return Status{ErrorCode::protocol_error,
                          "the first authority record must be a self-signed v1 owner bootstrap at sequence and epoch 1"};
        }
        PrincipalState owner;
        owner.public_key = record.subject;
        owner.role = PrincipalRole::owner;
        owner.capabilities = record.capabilities;
        owner.last_sequence = 1U;
        owner.active = true;
        principals[owner.public_key] = owner;
        snapshot.format = AuthorityLedgerFormat::v1;
        snapshot.initialized = true;
        snapshot.ownership_epoch = 1U;
        snapshot.sequence = 1U;
        snapshot.record_count = 1U;
        snapshot.tail_digest = digest.value();
        snapshot_from_map(snapshot, principals);
        return Status::success();
    }

    if (record.action == AuthorityAction::bootstrap) {
        return Status{ErrorCode::protocol_error,
                      "authority bootstrap may appear only as the first record"};
    }

    const bool migration_v2 = record.action == AuthorityAction::migrate_v2;
    const bool migration_v3 = record.action == AuthorityAction::migrate_v3;
    if (migration_v2) {
        if (snapshot.format != AuthorityLedgerFormat::v1 ||
            record.format != AuthorityLedgerFormat::v2) {
            return Status{ErrorCode::protocol_error,
                          "authority v2 migration may occur exactly once after a v1 history"};
        }
    } else if (migration_v3) {
        if (snapshot.format != AuthorityLedgerFormat::v2 ||
            record.format != AuthorityLedgerFormat::v3) {
            return Status{
                ErrorCode::protocol_error,
                "authority v3 migration may occur exactly once after a v2 history"};
        }
    } else if (record.format != snapshot.format) {
        return Status{ErrorCode::protocol_error,
                      "authority record format does not match the active ledger format"};
    }

    if (record.action == AuthorityAction::epoch_transition) {
        if (snapshot.ownership_epoch == std::numeric_limits<std::uint64_t>::max() ||
            record.sequence != 1U ||
            record.ownership_epoch != snapshot.ownership_epoch + 1U ||
            !constant_time_equal(record.previous_digest, snapshot.tail_digest)) {
            return Status{ErrorCode::protocol_error,
                          "epoch transition must advance the epoch once, reset sequence to one, and extend the exact tail"};
        }
    } else if (snapshot.sequence == std::numeric_limits<std::uint64_t>::max() ||
               record.sequence != snapshot.sequence + 1U ||
               record.ownership_epoch != snapshot.ownership_epoch ||
               !constant_time_equal(record.previous_digest, snapshot.tail_digest)) {
        return Status{ErrorCode::protocol_error,
                      "authority record sequence, epoch, or previous digest does not extend the current ledger tail"};
    }

    const auto issuer_iterator = principals.find(record.issuer);
    if (issuer_iterator == principals.end() || !issuer_iterator->second.active) {
        return Status{ErrorCode::protocol_error,
                      "authority record issuer is not an active principal"};
    }
    const PrincipalState &issuer = issuer_iterator->second;
    const std::uint64_t manage =
        static_cast<std::uint64_t>(Capability::manage_principals);
    if ((issuer.capabilities & manage) == 0U) {
        return Status{ErrorCode::protocol_error,
                      "authority record issuer lacks manage.principals"};
    }

    if (record.action == AuthorityAction::grant) {
        const auto prior_subject = principals.find(record.subject);
        const bool nominates_successor =
            record.role == PrincipalRole::owner &&
            (prior_subject == principals.end() || !prior_subject->second.active ||
             prior_subject->second.role != PrincipalRole::owner);
        const Status policy = validate_grant_policy(record, issuer, principals);
        if (!policy.ok()) {
            return policy;
        }
        PrincipalState subject;
        subject.public_key = record.subject;
        subject.role = record.role;
        subject.capabilities = record.capabilities;
        subject.last_sequence = record.sequence;
        subject.active = true;
        principals[subject.public_key] = subject;
        snapshot.nominated_successor.fill(0U);
        if (nominates_successor) {
            snapshot.nominated_successor = record.subject;
        }
    } else if (record.action == AuthorityAction::revoke) {
        const Status policy = validate_revoke_policy(record, issuer, principals);
        if (!policy.ok()) {
            return policy;
        }
        auto subject = principals.find(record.subject);
        subject->second.active = false;
        subject->second.role = PrincipalRole::none;
        subject->second.capabilities = 0U;
        subject->second.last_sequence = record.sequence;
        snapshot.nominated_successor.fill(0U);
    } else if (record.action == AuthorityAction::epoch_transition) {
        const Status policy = validate_epoch_transition_policy(
            record, issuer, snapshot);
        if (!policy.ok()) {
            return policy;
        }
        principals.clear();
        PrincipalState owner;
        owner.public_key = record.subject;
        owner.role = PrincipalRole::owner;
        owner.capabilities = record.capabilities;
        owner.last_sequence = 1U;
        owner.active = true;
        principals[owner.public_key] = owner;
        snapshot.ownership_epoch = record.ownership_epoch;
        snapshot.nominated_successor.fill(0U);
    } else if (migration_v2) {
        const Status policy = validate_v2_migration_policy(
            record, issuer, snapshot);
        if (!policy.ok()) {
            return policy;
        }
        snapshot.format = AuthorityLedgerFormat::v2;
        snapshot.nominated_successor.fill(0U);
    } else if (migration_v3) {
        const Status policy =
            validate_v3_migration_policy(record, issuer, snapshot);
        if (!policy.ok()) {
            return policy;
        }
        snapshot.format = AuthorityLedgerFormat::v3;
        snapshot.nominated_successor.fill(0U);
    } else {
        return Status{ErrorCode::unsupported,
                      "authority action is not implemented"};
    }

    snapshot.sequence = record.sequence;
    snapshot.record_count += 1U;
    snapshot.tail_digest = digest.value();
    snapshot_from_map(snapshot, principals);
    return Status::success();
}

AuthoritySnapshot AuthorityLedger::snapshot() const {
    std::scoped_lock lock(mutex_);
    return snapshot_;
}

Result<AuthorityRecordBody> AuthorityLedger::prepare(
    const AuthorityPrepareRequest &request) const {
    std::scoped_lock lock(mutex_);
    if (!known_action(request.action) || !known_role(request.role) ||
        (request.capabilities & ~kAuthorityV3Capabilities) != 0U ||
        all_zero(request.issuer) || all_zero(request.subject)) {
        return Status{ErrorCode::invalid_argument,
                      "authority prepare request contains an invalid field"};
    }

    AuthorityRecord record;
    record.action = request.action;
    record.role = request.role;
    record.capabilities = request.capabilities;
    record.device = device_;
    record.issuer = request.issuer;
    record.subject = request.subject;
    if (!snapshot_.initialized) {
        record.format = AuthorityLedgerFormat::v1;
        if (request.action != AuthorityAction::bootstrap ||
            request.role != PrincipalRole::owner ||
            request.capabilities != kAuthorityV1Capabilities ||
            !constant_time_equal(request.issuer, request.subject)) {
            return Status{ErrorCode::invalid_argument,
                          "an empty ledger can prepare only a self-signed v1 owner bootstrap"};
        }
        record.sequence = 1U;
        record.ownership_epoch = 1U;
        return encode_authority_record_body(record);
    }

    if (request.action == AuthorityAction::bootstrap) {
        return Status{ErrorCode::invalid_argument,
                      "an initialized ledger cannot prepare another bootstrap record"};
    }
    const auto issuer = std::find_if(
        snapshot_.principals.begin(), snapshot_.principals.end(),
        [&request](const PrincipalState &principal) {
            return constant_time_equal(principal.public_key, request.issuer);
        });
    if (issuer == snapshot_.principals.end() || !issuer->active ||
        (issuer->capabilities &
         static_cast<std::uint64_t>(Capability::manage_principals)) == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "authority prepare issuer is not an active principal manager"};
    }
    if (request.action != AuthorityAction::epoch_transition &&
        snapshot_.sequence == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "authority sequence is exhausted"};
    }

    const PrincipalMap principals = map_from_snapshot(snapshot_);
    if (request.action == AuthorityAction::migrate_v2) {
        record.format = AuthorityLedgerFormat::v2;
        const Status policy = validate_v2_migration_policy(
            record, *issuer, snapshot_);
        if (!policy.ok()) {
            return policy;
        }
        record.sequence = snapshot_.sequence + 1U;
        record.ownership_epoch = snapshot_.ownership_epoch;
        record.previous_digest = snapshot_.tail_digest;
        return encode_authority_record_body(record);
    }

    if (request.action == AuthorityAction::migrate_v3) {
        record.format = AuthorityLedgerFormat::v3;
        const Status policy =
            validate_v3_migration_policy(record, *issuer, snapshot_);
        if (!policy.ok()) {
            return policy;
        }
        record.sequence = snapshot_.sequence + 1U;
        record.ownership_epoch = snapshot_.ownership_epoch;
        record.previous_digest = snapshot_.tail_digest;
        return encode_authority_record_body(record);
    }

    record.format = snapshot_.format;
    if ((request.capabilities &
         ~authority_capability_mask(record.format)) != 0U) {
        return Status{ErrorCode::invalid_argument,
                      "requested capability is not defined by the active authority ledger format"};
    }
    if (request.action == AuthorityAction::grant) {
        const Status policy = validate_grant_policy(record, *issuer, principals);
        if (!policy.ok()) {
            return policy;
        }
    } else if (request.action == AuthorityAction::revoke) {
        const Status policy = validate_revoke_policy(record, *issuer, principals);
        if (!policy.ok()) {
            return policy;
        }
    } else if (request.action == AuthorityAction::epoch_transition) {
        const Status policy = validate_epoch_transition_policy(
            record, *issuer, snapshot_);
        if (!policy.ok()) {
            return policy;
        }
        if (snapshot_.ownership_epoch ==
            std::numeric_limits<std::uint64_t>::max()) {
            return Status{ErrorCode::resource_exhausted,
                          "authority ownership epoch is exhausted"};
        }
        record.sequence = 1U;
        record.ownership_epoch = snapshot_.ownership_epoch + 1U;
        record.previous_digest = snapshot_.tail_digest;
        return encode_authority_record_body(record);
    } else {
        return Status{ErrorCode::unsupported,
                      "authority prepare action is not implemented"};
    }

    record.sequence = snapshot_.sequence + 1U;
    record.ownership_epoch = snapshot_.ownership_epoch;
    record.previous_digest = snapshot_.tail_digest;
    return encode_authority_record_body(record);
}

Status AuthorityLedger::write_records(
    std::span<const AuthorityRecordBytes> records,
    AuthorityLedgerFormat format) const {
    if (!known_format(format)) {
        return Status{ErrorCode::invalid_argument,
                      "authority ledger format is invalid"};
    }
    if (records.size() > config_.maximum_records ||
        records.size() > static_cast<std::size_t>(UINT32_MAX)) {
        return Status{ErrorCode::resource_exhausted,
                      "authority ledger reached its configured record limit"};
    }
    std::vector<std::uint8_t> bytes(
        kAuthorityLedgerHeaderBytes + records.size() * kAuthorityRecordBytes, 0U);
    const auto &magic = ledger_magic(format);
    std::copy(magic.begin(), magic.end(), bytes.begin());
    bytes[8U] = ledger_format_byte(format);
    bytes[9U] = format == AuthorityLedgerFormat::v1 ? kRecordFormatV1 : 0U;
    put_u32(
        std::span<std::uint8_t>{bytes}.subspan(12U, 4U),
        static_cast<std::uint32_t>(records.size()));
    for (std::size_t index = 0U; index < records.size(); ++index) {
        std::copy(
            records[index].begin(), records[index].end(),
            bytes.begin() + static_cast<std::ptrdiff_t>(
                                kAuthorityLedgerHeaderBytes + index * kAuthorityRecordBytes));
    }
    return StateStore::write_atomic(config_.path, bytes);
}

Status AuthorityLedger::append(
    std::span<const std::uint8_t, kAuthorityRecordBytes> record) {
    std::scoped_lock lock(mutex_);
    if (records_.size() >= config_.maximum_records) {
        return Status{ErrorCode::resource_exhausted,
                      "authority ledger reached its configured record limit"};
    }
    AuthorityRecordBytes copy{};
    std::copy(record.begin(), record.end(), copy.begin());
    AuthoritySnapshot next = snapshot_;
    const Status applied = apply(copy, next);
    if (!applied.ok()) {
        return applied;
    }
    std::vector<AuthorityRecordBytes> next_records = records_;
    next_records.push_back(copy);
    rollback_witness::Record witness_committed;
    rollback_witness::Record witness_pending;
    const Status witnessed = begin_rollback_witness_transition(
        snapshot_, next, copy, witness_committed, witness_pending);
    if (!witnessed.ok()) return witnessed;
    const Status guarded = begin_rollback_guard_transition(snapshot_, next);
    if (!guarded.ok()) {
        return guarded;
    }
    const Status written = write_records(next_records, next.format);
    if (!written.ok()) {
        // Do not throw while inspecting the interrupted first-append case.
        // The pending guard remains intentional: the next live append or the
        // next open can discard it only when the exact committed head is still
        // present, or promote it only when the exact pending head landed.
        std::error_code existence_error;
        (void)std::filesystem::exists(config_.path, existence_error);
        if (existence_error) {
            return Status{
                written.code(),
                written.message() +
                    "; unable to inspect the authority ledger after the failed replace: " +
                    existence_error.message()};
        }
        return written;
    }
    records_ = std::move(next_records);
    snapshot_ = std::move(next);
    const Status guard_finished = finish_rollback_guard_transition(snapshot_);
    if (!guard_finished.ok()) return guard_finished;
    return finish_rollback_witness_transition(witness_pending);
}

Result<PrincipalState> AuthorityLedger::principal(
    const SigningPublicKey &public_key) const {
    std::scoped_lock lock(mutex_);
    const auto found = std::find_if(
        snapshot_.principals.begin(), snapshot_.principals.end(),
        [&public_key](const PrincipalState &principal) {
            return constant_time_equal(principal.public_key, public_key);
        });
    if (found == snapshot_.principals.end()) {
        return Status{ErrorCode::not_found, "authority principal is not present"};
    }
    return *found;
}

bool AuthorityLedger::authorized(
    const SigningPublicKey &public_key, std::uint64_t required_capabilities) const {
    std::scoped_lock lock(mutex_);
    if ((required_capabilities &
         ~authority_capability_mask(snapshot_.format)) != 0U) {
        return false;
    }
    const auto found = std::find_if(
        snapshot_.principals.begin(), snapshot_.principals.end(),
        [&public_key](const PrincipalState &principal) {
            return constant_time_equal(principal.public_key, public_key);
        });
    return found != snapshot_.principals.end() && found->active &&
           (found->capabilities & required_capabilities) == required_capabilities;
}

std::filesystem::path default_authority_ledger_path(
    const std::filesystem::path &tox_savedata_path) {
    if (tox_savedata_path.empty()) {
        return {};
    }
    const std::filesystem::path parent =
        tox_savedata_path.has_parent_path() ? tox_savedata_path.parent_path() :
                                              std::filesystem::path{"."};
    return parent / "authority.ledger";
}

std::filesystem::path default_authority_rollback_guard_path(
    const std::filesystem::path &authority_ledger_path) {
    if (authority_ledger_path.empty()) {
        return {};
    }
    std::filesystem::path guard = authority_ledger_path;
    guard += ".guard";
    return guard;
}

std::string render_authority_snapshot(const AuthoritySnapshot &snapshot) {
    std::size_t active = 0U;
    std::size_t owners = 0U;
    for (const PrincipalState &principal : snapshot.principals) {
        if (principal.active) {
            ++active;
            if (principal.role == PrincipalRole::owner) {
                ++owners;
            }
        }
    }
    std::ostringstream output;
    output << "device-public-key=" << hex(snapshot.device) << '\n'
           << "ledger-format=" << to_string(snapshot.format) << '\n'
           << "initialized=" << (snapshot.initialized ? 1 : 0) << '\n'
           << "ownership-epoch=" << snapshot.ownership_epoch << '\n'
           << "sequence=" << snapshot.sequence << '\n'
           << "record-count=" << snapshot.record_count << '\n'
           << "tail-digest=" << hex(snapshot.tail_digest) << '\n'
           << "nominated-successor="
           << (all_zero(snapshot.nominated_successor)
                   ? std::string{"none"}
                   : hex(snapshot.nominated_successor))
           << '\n'
           << "principal-count=" << snapshot.principals.size() << '\n'
           << "active-principal-count=" << active << '\n'
           << "active-owner-count=" << owners << '\n';
    return output.str();
}

std::string render_principals(const AuthoritySnapshot &snapshot) {
    std::ostringstream output;
    for (const PrincipalState &principal : snapshot.principals) {
        output << "public-key=" << hex(principal.public_key)
               << " active=" << (principal.active ? 1 : 0)
               << " role=" << to_string(principal.role)
               << " capabilities=" << render_capability_set(principal.capabilities)
               << " last-sequence=" << principal.last_sequence << '\n';
    }
    return output.str();
}

}  // namespace iotox::security
