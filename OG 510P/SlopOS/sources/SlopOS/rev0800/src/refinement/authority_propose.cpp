#include "slopos/k0/authority_propose_refinement.hpp"
#include "slopos/k0/sequence.hpp"

#include <cstddef>
#include <limits>
#include <sstream>
#include <type_traits>

namespace slopos::k0 {
namespace {

static_assert(std::is_unsigned_v<std::uint16_t>);
static_assert(std::is_unsigned_v<std::uint32_t>);
static_assert(std::is_unsigned_v<std::uint64_t>);
static_assert(std::numeric_limits<std::uint16_t>::digits == 16);
static_assert(std::numeric_limits<std::uint32_t>::digits == 32);
static_assert(std::numeric_limits<std::uint64_t>::digits == 64);
static_assert(kAuthorityProposalCapacity == 8U);
static_assert(kAuthorityLeaseCapacity == 8U);
static_assert(kAuthorityResourceCapacity == 4U);

[[nodiscard]] bool valid_resource(const std::uint16_t resource) noexcept {
    return static_cast<std::size_t>(resource) < kAuthorityResourceCapacity;
}

[[nodiscard]] bool valid_action(const AuthorityAction action) noexcept {
    return action == AuthorityAction::increment;
}

[[nodiscard]] std::uint64_t observed_value(
    const AuthorityValueSnapshot& image,
    const std::uint16_t resource) noexcept {
    return valid_resource(resource) ? image.resources[resource].value : 0U;
}

[[nodiscard]] AuthorityOutcome denial(
    const AuthorityDecision decision,
    const AuthorityValueSnapshot& before,
    const AuthorityCommand& command) noexcept {
    const std::uint64_t value = observed_value(before, command.resource);
    return AuthorityOutcome{decision, false, command.resource, value, value,
                            before.sequence};
}

[[nodiscard]] std::size_t proposal_count(
    const AuthorityValueSnapshot& image) noexcept {
    std::size_t count = 0U;
    while (count < image.proposals.size() && image.proposals[count].occupied) {
        ++count;
    }
    return count;
}

[[nodiscard]] bool has_proposal(
    const AuthorityValueSnapshot& image,
    const std::uint16_t id) noexcept {
    for (const AuthorityProposal& proposal : image.proposals) {
        if (!proposal.occupied) {
            break;
        }
        if (proposal.id == id) {
            return true;
        }
    }
    return false;
}

void insert_proposal(
    AuthorityValueSnapshot& image,
    const AuthorityCommand& command) noexcept {
    const std::size_t count = proposal_count(image);
    std::size_t insertion = 0U;
    while (insertion < count &&
           image.proposals[insertion].id < command.proposal_id) {
        ++insertion;
    }
    for (std::size_t index = count; index > insertion; --index) {
        image.proposals[index] = image.proposals[index - 1U];
    }
    image.proposals[insertion] = AuthorityProposal{
        true,
        command.proposal_id,
        command.subject,
        command.resource,
        command.action,
        command.amount,
        false,
    };
}

[[nodiscard]] bool proposal_well_formed(
    const AuthorityProposal& proposal) noexcept {
    return proposal.occupied && proposal.id != 0U && proposal.subject != 0U &&
           valid_resource(proposal.resource) && valid_action(proposal.action) &&
           proposal.amount != 0U;
}

[[nodiscard]] bool lease_well_formed(const AuthorityLease& lease) noexcept {
    return lease.occupied && lease.id != 0U && lease.subject != 0U &&
           valid_resource(lease.resource) && valid_action(lease.action) &&
           lease.max_amount != 0U && lease.not_before <= lease.expires_at;
}

[[nodiscard]] AuthorityCommand witness_propose(
    const std::uint16_t id,
    const std::uint16_t subject = 2U,
    const std::uint16_t resource = 0U,
    const std::uint64_t amount = 1U) noexcept {
    AuthorityCommand command{};
    command.operation = AuthorityOperation::propose;
    command.actor = subject;
    command.proposal_id = id;
    command.subject = subject;
    command.resource = resource;
    command.amount = amount;
    return command;
}

[[nodiscard]] bool check_concrete_step(
    AuthorityCore& core,
    AuthorityReference& reference,
    const AuthorityCommand& command,
    std::uint64_t& checks,
    std::ostringstream& error) {
    const AuthorityValueSnapshot before = core.snapshot();
    if (before != reference.snapshot()) {
        error << "core/reference pre-snapshot mismatch";
        return false;
    }
    const AuthorityOutcome actual = core.apply(command);
    const AuthorityOutcome model = reference.apply(command);
    const AuthorityValueSnapshot after = core.snapshot();
    if (actual != model || after != reference.snapshot()) {
        error << "core/reference concrete mismatch for "
              << authority_command_text(command);
        return false;
    }
    const AuthorityProposeRefinementCheck refined =
        check_authority_propose_step(before, command, actual, after);
    ++checks;
    if (!refined.ok) {
        error << "refinement failure="
              << authority_propose_refinement_fault_name(refined.fault)
              << " guard=" << authority_propose_guard_name(refined.guard)
              << " command={" << authority_command_text(command) << '}';
        return false;
    }
    return true;
}

} // namespace

bool authority_value_snapshot_well_formed(
    const AuthorityValueSnapshot& image) noexcept {
    bool empty_tail = false;
    std::uint16_t previous_id = 0U;
    for (const AuthorityProposal& proposal : image.proposals) {
        if (!proposal.occupied) {
            empty_tail = true;
            if (proposal != AuthorityProposal{}) {
                return false;
            }
            continue;
        }
        if (empty_tail || !proposal_well_formed(proposal) ||
            proposal.id <= previous_id) {
            return false;
        }
        previous_id = proposal.id;
    }

    empty_tail = false;
    previous_id = 0U;
    for (const AuthorityLease& lease : image.leases) {
        if (!lease.occupied) {
            empty_tail = true;
            if (lease != AuthorityLease{}) {
                return false;
            }
            continue;
        }
        if (empty_tail || !lease_well_formed(lease) || lease.id <= previous_id) {
            return false;
        }
        previous_id = lease.id;
    }
    return true;
}

AuthorityProposeGuard classify_authority_propose(
    const AuthorityValueSnapshot& before,
    const AuthorityCommand& command) noexcept {
    if (command.operation != AuthorityOperation::propose) {
        return AuthorityProposeGuard::out_of_scope;
    }
    if (command.proposal_id == 0U || command.actor == 0U ||
        command.actor != command.subject || !valid_resource(command.resource) ||
        !valid_action(command.action) || command.amount == 0U) {
        return AuthorityProposeGuard::invalid;
    }
    if (has_proposal(before, command.proposal_id)) {
        return AuthorityProposeGuard::duplicate;
    }
    if (proposal_count(before) >= kAuthorityProposalCapacity) {
        return AuthorityProposeGuard::capacity;
    }
    if (!accepted_sequence_available(before.sequence)) {
        return AuthorityProposeGuard::sequence_exhausted;
    }
    return AuthorityProposeGuard::accepted;
}

AuthorityProposeExpectation authority_propose_expected(
    const AuthorityValueSnapshot& before,
    const AuthorityCommand& command) noexcept {
    AuthorityProposeExpectation expected{};
    expected.guard = classify_authority_propose(before, command);
    expected.after = before;

    switch (expected.guard) {
    case AuthorityProposeGuard::out_of_scope:
        expected.outcome = denial(AuthorityDecision::denied_invalid, before, command);
        return expected;
    case AuthorityProposeGuard::invalid:
        expected.outcome = denial(AuthorityDecision::denied_invalid, before, command);
        return expected;
    case AuthorityProposeGuard::duplicate:
        expected.outcome = denial(AuthorityDecision::denied_duplicate, before, command);
        return expected;
    case AuthorityProposeGuard::capacity:
        expected.outcome = denial(AuthorityDecision::denied_capacity, before, command);
        return expected;
    case AuthorityProposeGuard::sequence_exhausted:
        expected.outcome = denial(
            AuthorityDecision::denied_sequence_exhausted, before, command);
        return expected;
    case AuthorityProposeGuard::accepted:
        insert_proposal(expected.after, command);
        expected.after.sequence = accepted_sequence_advance(before.sequence).next;
        break;
    }

    const std::uint64_t value = observed_value(before, command.resource);
    expected.outcome = AuthorityOutcome{
        AuthorityDecision::accepted,
        false,
        command.resource,
        value,
        value,
        expected.after.sequence,
    };
    return expected;
}

AuthorityProposeRefinementCheck check_authority_propose_step(
    const AuthorityValueSnapshot& before,
    const AuthorityCommand& command,
    const AuthorityOutcome& observed_outcome,
    const AuthorityValueSnapshot& after) noexcept {
    AuthorityProposeRefinementCheck result{};
    if (!authority_value_snapshot_well_formed(before)) {
        result.fault = AuthorityProposeRefinementFault::malformed_before;
        return result;
    }
    result.guard = classify_authority_propose(before, command);
    if (result.guard == AuthorityProposeGuard::out_of_scope) {
        result.fault = AuthorityProposeRefinementFault::out_of_scope;
        return result;
    }
    if (!authority_value_snapshot_well_formed(after)) {
        result.fault = AuthorityProposeRefinementFault::malformed_after;
        return result;
    }
    const AuthorityProposeExpectation expected =
        authority_propose_expected(before, command);
    if (observed_outcome != expected.outcome) {
        result.fault = AuthorityProposeRefinementFault::outcome_mismatch;
        return result;
    }
    if (after != expected.after) {
        result.fault = AuthorityProposeRefinementFault::state_mismatch;
        return result;
    }
    result.ok = true;
    result.fault = AuthorityProposeRefinementFault::none;
    return result;
}

std::string_view authority_propose_guard_name(
    const AuthorityProposeGuard guard) noexcept {
    switch (guard) {
    case AuthorityProposeGuard::out_of_scope: return "OUT_OF_SCOPE";
    case AuthorityProposeGuard::invalid: return "INVALID";
    case AuthorityProposeGuard::duplicate: return "DUPLICATE";
    case AuthorityProposeGuard::capacity: return "CAPACITY";
    case AuthorityProposeGuard::sequence_exhausted: return "SEQUENCE_EXHAUSTED";
    case AuthorityProposeGuard::accepted: return "ACCEPTED";
    }
    return "UNKNOWN";
}

std::string_view authority_propose_refinement_fault_name(
    const AuthorityProposeRefinementFault fault) noexcept {
    switch (fault) {
    case AuthorityProposeRefinementFault::none: return "NONE";
    case AuthorityProposeRefinementFault::out_of_scope: return "OUT_OF_SCOPE";
    case AuthorityProposeRefinementFault::malformed_before: return "MALFORMED_BEFORE";
    case AuthorityProposeRefinementFault::malformed_after: return "MALFORMED_AFTER";
    case AuthorityProposeRefinementFault::outcome_mismatch: return "OUTCOME_MISMATCH";
    case AuthorityProposeRefinementFault::state_mismatch: return "STATE_MISMATCH";
    }
    return "UNKNOWN";
}

AuthorityRunReport authority_propose_refinement_witness() {
    AuthorityRunReport report{};
    std::ostringstream error;
    std::uint64_t checks = 0U;
    std::uint64_t rejected_mutations = 0U;

    AuthorityCore core{};
    AuthorityReference reference{};
    const AuthorityCommand first = witness_propose(11U, 2U, 1U, 3U);
    if (!check_concrete_step(core, reference, first, checks, error) ||
        !check_concrete_step(core, reference, first, checks, error)) {
        report.diagnostic = error.str();
        return report;
    }

    AuthorityCommand invalid = witness_propose(0U);
    if (!check_concrete_step(core, reference, invalid, checks, error)) {
        report.diagnostic = error.str();
        return report;
    }

    AuthorityCore finite{};
    AuthorityReference finite_reference{};
    for (std::uint16_t id = 1U;
         id <= static_cast<std::uint16_t>(kAuthorityProposalCapacity); ++id) {
        if (!check_concrete_step(
                finite, finite_reference,
                witness_propose(static_cast<std::uint16_t>(100U + id)),
                checks, error)) {
            report.diagnostic = error.str();
            return report;
        }
    }
    if (!check_concrete_step(
            finite, finite_reference, witness_propose(999U), checks, error)) {
        report.diagnostic = error.str();
        return report;
    }

    AuthorityValueSnapshot terminal{};
    terminal.sequence = kAcceptedSequenceMaximum;
    const AuthorityCommand terminal_command = witness_propose(71U);
    const AuthorityProposeExpectation terminal_expected =
        authority_propose_expected(terminal, terminal_command);
    const AuthorityProposeRefinementCheck terminal_check =
        check_authority_propose_step(
            terminal, terminal_command, terminal_expected.outcome,
            terminal_expected.after);
    ++checks;
    if (!terminal_check.ok ||
        terminal_check.guard != AuthorityProposeGuard::sequence_exhausted) {
        report.diagnostic = "terminal pure-value frame was not accepted by checker";
        return report;
    }

    AuthorityValueSnapshot penultimate{};
    penultimate.sequence = kAcceptedSequenceMaximum - 1U;
    const AuthorityProposeExpectation final_accept =
        authority_propose_expected(penultimate, witness_propose(72U));
    const AuthorityProposeRefinementCheck final_accept_check =
        check_authority_propose_step(
            penultimate, witness_propose(72U), final_accept.outcome,
            final_accept.after);
    ++checks;
    if (!final_accept_check.ok ||
        final_accept.after.sequence != kAcceptedSequenceMaximum) {
        report.diagnostic = "max-minus-one pure-value acceptance failed";
        return report;
    }

    const AuthorityValueSnapshot empty{};
    const AuthorityCommand mutation_command = witness_propose(80U);
    const AuthorityProposeExpectation expected =
        authority_propose_expected(empty, mutation_command);

    AuthorityOutcome wrong_outcome = expected.outcome;
    wrong_outcome.decision = AuthorityDecision::denied_invalid;
    if (check_authority_propose_step(
            empty, mutation_command, wrong_outcome, expected.after).ok) {
        report.diagnostic = "outcome mutation escaped checker";
        return report;
    }
    ++rejected_mutations;

    if (check_authority_propose_step(
            empty, mutation_command, expected.outcome, empty).ok) {
        report.diagnostic = "missing insertion escaped checker";
        return report;
    }
    ++rejected_mutations;

    AuthorityValueSnapshot wrong_sequence = expected.after;
    wrong_sequence.sequence = empty.sequence;
    if (check_authority_propose_step(
            empty, mutation_command, expected.outcome, wrong_sequence).ok) {
        report.diagnostic = "sequence mutation escaped checker";
        return report;
    }
    ++rejected_mutations;

    AuthorityValueSnapshot wrong_resource = expected.after;
    wrong_resource.resources[0].value = 1U;
    if (check_authority_propose_step(
            empty, mutation_command, expected.outcome, wrong_resource).ok) {
        report.diagnostic = "resource-frame mutation escaped checker";
        return report;
    }
    ++rejected_mutations;

    AuthorityValueSnapshot malformed = empty;
    malformed.proposals[1] = AuthorityProposal{
        true, 91U, 2U, 0U, AuthorityAction::increment, 1U, false};
    if (check_authority_propose_step(
            malformed, mutation_command, expected.outcome, expected.after).fault !=
        AuthorityProposeRefinementFault::malformed_before) {
        report.diagnostic = "malformed source image escaped checker";
        return report;
    }
    ++rejected_mutations;

    AuthorityCommand out_of_scope{};
    out_of_scope.operation = AuthorityOperation::observe;
    if (check_authority_propose_step(
            empty, out_of_scope, AuthorityOutcome{}, empty).fault !=
        AuthorityProposeRefinementFault::out_of_scope) {
        report.diagnostic = "out-of-scope command escaped checker";
        return report;
    }
    ++rejected_mutations;

    report.ok = true;
    report.traces = checks;
    report.transitions = rejected_mutations;
    std::ostringstream summary;
    summary << "AUTHORITY PROPOSE REFINEMENT PASS checks=" << checks
            << " rejected_mutations=" << rejected_mutations;
    report.diagnostic = summary.str();
    return report;
}

} // namespace slopos::k0
