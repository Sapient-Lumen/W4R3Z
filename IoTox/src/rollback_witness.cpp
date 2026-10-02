#include "iotox/rollback_witness.hpp"

#include <algorithm>
#include <limits>

namespace iotox::rollback_witness {
namespace {

[[nodiscard]] bool all_zero(std::span<const std::uint8_t> bytes) {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::uint8_t byte) { return byte == 0U; });
}

}  // namespace

std::string_view lane_name(Lane lane) noexcept {
    switch (lane) {
        case Lane::authority: return "authority";
        case Lane::application_incarnation: return "application-incarnation";
        case Lane::ratox_incarnation: return "ratox-incarnation";
        case Lane::route_generation: return "route-generation";
        case Lane::terminal_policy: return "terminal-policy";
        case Lane::command_effect: return "command-effect";
        case Lane::sync_policy: return "sync-policy";
        case Lane::update_lifecycle: return "update-lifecycle";
        case Lane::sync_guarded_state: return "sync-guarded-state";
        case Lane::tree_v2_state: return "tree-v2-state";
    }
    return "invalid";
}

Status validate(const Record &record) {
    if (all_zero(record.domain) || all_zero(record.device) ||
        record.witness_epoch == 0U || lane_name(record.lane) == "invalid") {
        return Status{ErrorCode::invalid_argument,
                      "rollback witness identity, epoch, or lane is invalid"};
    }
    if ((record.committed.position == 0U) !=
        all_zero(record.committed.digest)) {
        return Status{ErrorCode::invalid_argument,
                      "rollback witness position and digest initialization disagree"};
    }
    if ((record.pending.has_value() != record.nonce.has_value())) {
        return Status{ErrorCode::invalid_argument,
                      "rollback witness pending head and nonce must appear together"};
    }
    if (record.pending) {
        if (all_zero(*record.nonce) ||
            record.committed.position ==
                std::numeric_limits<std::uint64_t>::max() ||
            record.pending->position != record.committed.position + 1U ||
            all_zero(record.pending->digest) ||
            record.pending->digest == record.committed.digest) {
            return Status{ErrorCode::invalid_argument,
                          "rollback witness pending transition is not one exact forward step"};
        }
    }
    return Status::success();
}

Result<Record> begin(const Record &committed, const Head &next,
                     const TransactionNonce &nonce) {
    const Status valid = validate(committed);
    if (!valid.ok()) return valid;
    if (committed.pending || committed.nonce) {
        return Status{ErrorCode::invalid_argument,
                      "rollback witness already has a pending transition"};
    }
    Record result = committed;
    result.pending = next;
    result.nonce = nonce;
    const Status result_valid = validate(result);
    if (!result_valid.ok()) return result_valid;
    return result;
}

Result<Record> finish(const Record &pending) {
    const Status valid = validate(pending);
    if (!valid.ok()) return valid;
    if (!pending.pending || !pending.nonce) {
        return Status{ErrorCode::invalid_argument,
                      "rollback witness has no pending transition"};
    }
    Record result = pending;
    result.committed = *pending.pending;
    result.pending.reset();
    result.nonce.reset();
    const Status result_valid = validate(result);
    if (!result_valid.ok()) return result_valid;
    return result;
}

Status validate_transition(const Record &expected, const Record &desired) {
    const Status expected_valid = validate(expected);
    if (!expected_valid.ok()) return expected_valid;
    const Status desired_valid = validate(desired);
    if (!desired_valid.ok()) return desired_valid;
    if (expected.domain != desired.domain || expected.device != desired.device ||
        expected.witness_epoch != desired.witness_epoch ||
        expected.lane != desired.lane) {
        return Status{ErrorCode::protocol_error,
                      "rollback witness transition changes its closed identity"};
    }
    if (expected.pending) {
        auto completed = finish(expected);
        if (!completed || !(completed.value() == desired)) {
            return Status{ErrorCode::protocol_error,
                          "rollback witness transition is not the exact pending commit"};
        }
        return Status::success();
    }
    if (!desired.pending || desired.committed != expected.committed) {
        return Status{ErrorCode::protocol_error,
                      "rollback witness transition is not an exact pending begin"};
    }
    auto begun = begin(expected, *desired.pending, *desired.nonce);
    if (!begun || !(begun.value() == desired)) {
        return Status{ErrorCode::protocol_error,
                      "rollback witness transition is not one exact forward step"};
    }
    return Status::success();
}

}  // namespace iotox::rollback_witness
