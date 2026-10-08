#include "sqlite_replay_ledger_reset_receipt_protocol.hpp"

#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_reset_documents.hpp"
#include "sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"

#include <array>
#include <exception>
#include <filesystem>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::persistence {
namespace {

namespace fs = std::filesystem;
using atomic_file_publication_detail::
    PreparedImmutableJsonPublicationObserverAccess;

constexpr std::string_view kProtocolLabel =
    "sqlite-wal replay ledger reset receipt protocol";

[[nodiscard]] fs::path absolute_normal_path_or_throw(
    const fs::path& path,
    std::string_view label) {
    if (path.empty()) {
        throw std::runtime_error(std::string(label) + " path is empty");
    }
    std::error_code error;
    fs::path absolute = fs::absolute(path, error);
    if (error || absolute.empty() || !absolute.is_absolute()) {
        throw std::runtime_error(std::string(label) +
                                 " path could not be made absolute");
    }
    return absolute.lexically_normal();
}

[[nodiscard]] bool existing_paths_are_equivalent(
    const fs::path& first,
    const fs::path& second) noexcept {
    std::error_code first_error;
    const bool first_exists = fs::exists(first, first_error);
    std::error_code second_error;
    const bool second_exists = fs::exists(second, second_error);
    if (first_error || second_error || !first_exists || !second_exists) {
        return false;
    }
    std::error_code equivalent_error;
    const bool equivalent = fs::equivalent(first, second, equivalent_error);
    return !equivalent_error && equivalent;
}

void reject_receipt_inside_ledger_namespace_or_throw(
    const fs::path& ledger_path,
    const fs::path& receipt_path) {
    const fs::path ledger = absolute_normal_path_or_throw(
        ledger_path, "sqlite-wal replay ledger reset ledger");
    const fs::path receipt = absolute_normal_path_or_throw(
        receipt_path, "sqlite-wal replay ledger reset receipt");
    constexpr std::array<std::string_view, 7> kFamilySuffixes{{
        "", "-wal", "-shm", "-journal", ".write.lock", ".restore.lock",
        ".reset.lock"}};
    for (const std::string_view suffix : kFamilySuffixes) {
        const fs::path family_member =
            fs::path(ledger.string() + std::string(suffix));
        if (receipt == family_member ||
            existing_paths_are_equivalent(receipt, family_member)) {
            throw std::runtime_error(
                "sqlite-wal replay ledger reset receipt refuses publication inside the SQLite ledger namespace");
        }
    }
}

[[nodiscard]] bool expectation_equals(
    const SqliteReplayLedgerResetExpectation& left,
    const SqliteReplayLedgerResetExpectation& right) noexcept {
    return left.namespace_identity == right.namespace_identity &&
           left.ledger_instance_id == right.ledger_instance_id &&
           left.state_sha256 == right.state_sha256 &&
           left.durable_line_count == right.durable_line_count &&
           left.durable_head_hash == right.durable_head_hash &&
           left.effect_transition_line_count ==
               right.effect_transition_line_count &&
           left.effect_transition_head_hash ==
               right.effect_transition_head_hash &&
           left.ledger_entry_rows == right.ledger_entry_rows &&
           left.effect_transition_rows == right.effect_transition_rows &&
           left.effect_outbox_rows == right.effect_outbox_rows &&
           left.ingress_sender_replay_rows ==
               right.ingress_sender_replay_rows;
}

struct DurableEvidenceInspection final {
    SqliteReplayLedgerResetReceiptDurableEvidence evidence{
        SqliteReplayLedgerResetReceiptDurableEvidence::
            DurableIdentityIndeterminate};
    std::string detail;
};

[[nodiscard]] DurableEvidenceInspection
inspect_exact_request_durable_evidence(
    const SqliteReplayLedgerResetRequest& request,
    std::string_view expected_receipt) {
    try {
        const SqliteReplayLedgerResetState observed =
            inspect_sqlite_replay_ledger_reset_state(request.ledger_path);
        if (observed.normalized_ledger_path !=
            request.ledger_path.generic_string()) {
            return {
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    DurableIdentityIndeterminate,
                "independent reopen observed a different normalized ledger path"};
        }
        if (!(observed.namespace_identity ==
              request.expected.namespace_identity)) {
            return {
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    DurableIdentityIndeterminate,
                "independent reopen observed a different SQLite namespace identity"};
        }
        if (observed.ledger_instance_id != expected_receipt) {
            return {
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    DurableIdentityIndeterminate,
                "independent reopen observed ledger identity " +
                    observed.ledger_instance_id +
                    " instead of the exact request receipt identity"};
        }
        return {
            SqliteReplayLedgerResetReceiptDurableEvidence::
                ExactRequestDurable,
            "independent reopen bound the current SQLite namespace and ledger identity to the exact request receipt"};
    } catch (const std::exception& error) {
        return {
            SqliteReplayLedgerResetReceiptDurableEvidence::
                DurableIdentityIndeterminate,
            std::string("independent reopen could not bind durable identity: ") +
                error.what()};
    } catch (...) {
        return {
            SqliteReplayLedgerResetReceiptDurableEvidence::
                DurableIdentityIndeterminate,
            "independent reopen could not bind durable identity: non-standard exception"};
    }
}

void verify_reset_result_binding_or_throw(
    const SqliteReplayLedgerResetRequest& request,
    std::string_view expected_receipt,
    const SqliteReplayLedgerResetResult& result) {
    if (!expectation_equals(result.prior, request.expected)) {
        throw std::logic_error(
            "reset result prior-state evidence is not bound to the protocol request");
    }
    if (result.normalized_ledger_path != request.ledger_path.generic_string()) {
        throw std::logic_error(
            "reset result ledger path is not bound to the protocol request");
    }
    if (result.new_ledger_instance_id != expected_receipt ||
        result.reset_receipt_sha256 != expected_receipt) {
        throw std::logic_error(
            "reset result durable identity is not bound to the prepared receipt");
    }
    if (result.reason_sha256 != sha256_hex(request.reason)) {
        throw std::logic_error(
            "reset result reason digest is not bound to the protocol request");
    }
    if (result.connection_owner_generation == 0) {
        throw std::logic_error(
            "reset result omitted its connection-owner generation evidence");
    }
    if (result.outcome == SqliteReplayLedgerResetOutcome::Committed &&
        result.state_advanced_after_commit) {
        throw std::logic_error(
            "first reset commit cannot already report later-state advancement");
    }
}

[[nodiscard]] std::string failure_message(
    SqliteReplayLedgerResetReceiptProtocolFailure failure,
    std::string_view detail) {
    std::ostringstream out;
    out << kProtocolLabel << " failed at "
        << sqlite_replay_ledger_reset_receipt_protocol_failure_name(failure)
        << ": " << detail;
    return out.str();
}

[[noreturn]] void throw_protocol_error(
    SqliteReplayLedgerResetReceiptProtocolFailure failure,
    SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
    SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
    std::string expected_reset_receipt_sha256,
    std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
        publication_effect,
    std::string_view detail) {
    throw detail::SqliteReplayLedgerResetReceiptProtocolErrorAccess::make(
        failure, durable_evidence, recovery_action, reported_reset_outcome,
        std::move(expected_reset_receipt_sha256), publication_effect,
        failure_message(failure, detail));
}

[[nodiscard]] std::string describe_exception(
    const std::exception_ptr& cause) {
    try {
        if (cause != nullptr) std::rethrow_exception(cause);
    } catch (const std::exception& error) {
        return error.what();
    } catch (...) {
        return "non-standard exception";
    }
    return "missing exception";
}

[[noreturn]] void throw_exception_as_protocol_error(
    const std::exception_ptr& cause,
    SqliteReplayLedgerResetReceiptProtocolFailure failure,
    SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
    SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
    std::string expected_reset_receipt_sha256,
    std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
        publication_effect,
    std::string_view additional_detail = {}) {
    std::string detail = describe_exception(cause);
    if (!additional_detail.empty()) {
        detail += "; ";
        detail += additional_detail;
    }
    try {
        if (cause != nullptr) std::rethrow_exception(cause);
    } catch (...) {
        throw_protocol_error(
            failure, durable_evidence, recovery_action, reported_reset_outcome,
            std::move(expected_reset_receipt_sha256), publication_effect,
            detail);
    }
    throw std::logic_error("protocol error wrapper received no exception");
}

[[noreturn]] void rethrow_current_as_protocol_error(
    SqliteReplayLedgerResetReceiptProtocolFailure failure,
    SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
    SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
    std::string expected_reset_receipt_sha256,
    std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
        publication_effect,
    std::string_view additional_detail = {}) {
    throw_exception_as_protocol_error(
        std::current_exception(), failure, durable_evidence, recovery_action,
        reported_reset_outcome, std::move(expected_reset_receipt_sha256),
        publication_effect, additional_detail);
}

[[noreturn]] void rethrow_after_durable_reset_frontier_as_protocol_error(
    const std::exception_ptr& cause,
    const SqliteReplayLedgerResetRequest& request,
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
    std::string expected_receipt,
    std::string_view classifier_context = {}) {
    const DurableEvidenceInspection inspection =
        inspect_exact_request_durable_evidence(request, expected_receipt);
    std::string detail;
    if (!classifier_context.empty()) {
        detail.assign(classifier_context);
        detail += "; ";
    }
    detail += inspection.detail;
    const bool exact =
        inspection.evidence ==
        SqliteReplayLedgerResetReceiptDurableEvidence::ExactRequestDurable;
    throw_exception_as_protocol_error(
        cause,
        exact ? SqliteReplayLedgerResetReceiptProtocolFailure::
                    ResetAfterExactDurableOutcome
              : SqliteReplayLedgerResetReceiptProtocolFailure::
                    ResetDurableIdentityIndeterminate,
        inspection.evidence,
        exact ? SqliteReplayLedgerResetReceiptRecoveryAction::
                    ReplayExactRequestToFreshReceiptPath
              : SqliteReplayLedgerResetReceiptRecoveryAction::
                    ResolveDurableIdentityBeforeRecovery,
        reported_reset_outcome, std::move(expected_receipt), std::nullopt,
        detail);
}

}  // namespace

const char* sqlite_replay_ledger_reset_receipt_durable_evidence_name(
    SqliteReplayLedgerResetReceiptDurableEvidence evidence) noexcept {
    switch (evidence) {
        case SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable:
            return "not_durable";
        case SqliteReplayLedgerResetReceiptDurableEvidence::
            ExactRequestDurable:
            return "exact_request_durable";
        case SqliteReplayLedgerResetReceiptDurableEvidence::
            DurableIdentityIndeterminate:
            return "durable_identity_indeterminate";
    }
    return "unknown";
}

const char* sqlite_replay_ledger_reset_receipt_protocol_failure_name(
    SqliteReplayLedgerResetReceiptProtocolFailure failure) noexcept {
    switch (failure) {
        case SqliteReplayLedgerResetReceiptProtocolFailure::Preparation:
            return "preparation";
        case SqliteReplayLedgerResetReceiptProtocolFailure::
            ResetBeforeDurableOutcome:
            return "reset_before_durable_outcome";
        case SqliteReplayLedgerResetReceiptProtocolFailure::
            ResetAfterExactDurableOutcome:
            return "reset_after_exact_durable_outcome";
        case SqliteReplayLedgerResetReceiptProtocolFailure::
            ResetDurableIdentityIndeterminate:
            return "reset_durable_identity_indeterminate";
        case SqliteReplayLedgerResetReceiptProtocolFailure::
            ReceiptPublicationAfterExactDurableOutcome:
            return "receipt_publication_after_exact_durable_outcome";
    }
    return "unknown";
}

const char* sqlite_replay_ledger_reset_receipt_recovery_action_name(
    SqliteReplayLedgerResetReceiptRecoveryAction action) noexcept {
    switch (action) {
        case SqliteReplayLedgerResetReceiptRecoveryAction::None:
            return "none";
        case SqliteReplayLedgerResetReceiptRecoveryAction::
            ResolveDurableIdentityBeforeRecovery:
            return "resolve_durable_identity_before_recovery";
        case SqliteReplayLedgerResetReceiptRecoveryAction::
            ReplayExactRequestToFreshReceiptPath:
            return "replay_exact_request_to_fresh_receipt_path";
    }
    return "unknown";
}

SqliteReplayLedgerResetReceiptProtocolError::
    SqliteReplayLedgerResetReceiptProtocolError(
        SqliteReplayLedgerResetReceiptProtocolFailure failure,
        SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
        SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
        std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
        std::string expected_reset_receipt_sha256,
        std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
            publication_effect,
        std::string message)
    : std::runtime_error(std::move(message)),
      failure_(failure),
      durable_evidence_(durable_evidence),
      recovery_action_(recovery_action),
      reported_reset_outcome_(reported_reset_outcome),
      expected_reset_receipt_sha256_(
          std::move(expected_reset_receipt_sha256)),
      publication_effect_(publication_effect) {
    const bool before_durable =
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::Preparation ||
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::
                        ResetBeforeDurableOutcome;
    const bool exact_durable =
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::
                        ResetAfterExactDurableOutcome ||
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::
                        ReceiptPublicationAfterExactDurableOutcome;
    const bool indeterminate =
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::
                        ResetDurableIdentityIndeterminate;
    const bool evidence_matches_phase =
        (before_durable &&
         durable_evidence_ ==
             SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable) ||
        (exact_durable &&
         durable_evidence_ ==
             SqliteReplayLedgerResetReceiptDurableEvidence::
                 ExactRequestDurable) ||
        (indeterminate &&
         durable_evidence_ ==
             SqliteReplayLedgerResetReceiptDurableEvidence::
                 DurableIdentityIndeterminate);
    const bool recovery_matches_evidence =
        (before_durable &&
         recovery_action_ ==
             SqliteReplayLedgerResetReceiptRecoveryAction::None) ||
        (exact_durable &&
         recovery_action_ ==
             SqliteReplayLedgerResetReceiptRecoveryAction::
                 ReplayExactRequestToFreshReceiptPath) ||
        (indeterminate &&
         recovery_action_ ==
             SqliteReplayLedgerResetReceiptRecoveryAction::
                 ResolveDurableIdentityBeforeRecovery);
    const bool outcome_matches_evidence =
        reported_reset_outcome_.has_value() == !before_durable;
    const bool publication_matches_phase =
        !publication_effect_.has_value() ||
        failure_ == SqliteReplayLedgerResetReceiptProtocolFailure::
                        ReceiptPublicationAfterExactDurableOutcome;
    const bool expected_identity_valid =
        expected_reset_receipt_sha256_.empty()
            ? failure_ ==
                  SqliteReplayLedgerResetReceiptProtocolFailure::Preparation
            : is_lowercase_sha256_hex(expected_reset_receipt_sha256_);
    if (!evidence_matches_phase || !recovery_matches_evidence ||
        !outcome_matches_evidence || !publication_matches_phase ||
        !expected_identity_valid) {
        throw std::logic_error(
            "invalid sqlite reset/receipt protocol error evidence");
    }
}

SqliteReplayLedgerResetReceiptProtocolError detail::
    SqliteReplayLedgerResetReceiptProtocolErrorAccess::make(
        SqliteReplayLedgerResetReceiptProtocolFailure failure,
        SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence,
        SqliteReplayLedgerResetReceiptRecoveryAction recovery_action,
        std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome,
        std::string expected_reset_receipt_sha256,
        std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
            publication_effect,
        std::string message) {
    return SqliteReplayLedgerResetReceiptProtocolError(
        failure, durable_evidence, recovery_action, reported_reset_outcome,
        std::move(expected_reset_receipt_sha256), publication_effect,
        std::move(message));
}

SqliteReplayLedgerResetReceiptProtocolFailure
SqliteReplayLedgerResetReceiptProtocolError::failure() const noexcept {
    return failure_;
}

SqliteReplayLedgerResetReceiptDurableEvidence
SqliteReplayLedgerResetReceiptProtocolError::durable_evidence() const noexcept {
    return durable_evidence_;
}

SqliteReplayLedgerResetReceiptRecoveryAction
SqliteReplayLedgerResetReceiptProtocolError::recovery_action() const noexcept {
    return recovery_action_;
}

const std::optional<SqliteReplayLedgerResetOutcome>&
SqliteReplayLedgerResetReceiptProtocolError::reported_reset_outcome()
    const noexcept {
    return reported_reset_outcome_;
}

const std::string&
SqliteReplayLedgerResetReceiptProtocolError::expected_reset_receipt_sha256()
    const noexcept {
    return expected_reset_receipt_sha256_;
}

const std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>&
SqliteReplayLedgerResetReceiptProtocolError::publication_effect()
    const noexcept {
    return publication_effect_;
}

SqliteReplayLedgerResetReceiptProtocolResult
execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(
    const SqliteReplayLedgerResetRequest& request,
    const std::string& request_sha256,
    const fs::path& receipt_path) {
    return detail::SqliteReplayLedgerResetReceiptProtocolObserverAccess::
        execute_or_throw(request, request_sha256, receipt_path, nullptr, nullptr,
                         nullptr, nullptr, nullptr, nullptr);
}

SqliteReplayLedgerResetReceiptProtocolResult detail::
    SqliteReplayLedgerResetReceiptProtocolObserverAccess::execute_or_throw(
        const SqliteReplayLedgerResetRequest& request,
        const std::string& request_sha256,
        const fs::path& receipt_path,
        SqliteReplayLedgerResetObserver reset_observer,
        void* reset_observer_context,
        SqliteReplayLedgerResetResultBindingObserver result_binding_observer,
        void* result_binding_observer_context,
        atomic_file_publication_detail::AtomicFilePublicationObserver
            publication_observer,
        void* publication_observer_context) {
    std::string expected_receipt;
    SyncPreparedImmutableJsonPublication publication;
    try {
        reject_receipt_inside_ledger_namespace_or_throw(request.ledger_path,
                                                        receipt_path);
        expected_receipt =
            sqlite_replay_ledger_reset_receipt_sha256(request);
        std::string receipt_document =
            sqlite_replay_ledger_reset_receipt_json(request, request_sha256);
        publication =
            prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(
                receipt_path, std::move(receipt_document),
                "sqlite-wal replay ledger reset receipt");
    } catch (...) {
        rethrow_current_as_protocol_error(
            SqliteReplayLedgerResetReceiptProtocolFailure::Preparation,
            SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable,
            SqliteReplayLedgerResetReceiptRecoveryAction::None, std::nullopt,
            std::move(expected_receipt), std::nullopt);
    }

    SqliteReplayLedgerResetResult reset_result;
    try {
        reset_result = reset_sqlite_replay_ledger(
            request, reset_observer, reset_observer_context);
    } catch (const SqliteReplayLedgerResetDurableOutcomeError& error) {
        const std::exception_ptr cause = std::current_exception();
        const std::string_view classifier_context =
            error.reset_receipt_sha256() == expected_receipt
                ? std::string_view{}
                : std::string_view(
                      "reset durable-outcome error reported a different candidate receipt identity");
        rethrow_after_durable_reset_frontier_as_protocol_error(
            cause, request, error.outcome(), std::move(expected_receipt),
            classifier_context);
    } catch (...) {
        rethrow_current_as_protocol_error(
            SqliteReplayLedgerResetReceiptProtocolFailure::
                ResetBeforeDurableOutcome,
            SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable,
            SqliteReplayLedgerResetReceiptRecoveryAction::None, std::nullopt,
            expected_receipt, std::nullopt);
    }

    try {
        if (result_binding_observer != nullptr) {
            result_binding_observer(reset_result,
                                    result_binding_observer_context);
        }
        verify_reset_result_binding_or_throw(request, expected_receipt,
                                             reset_result);
    } catch (...) {
        rethrow_after_durable_reset_frontier_as_protocol_error(
            std::current_exception(), request, reset_result.outcome,
            std::move(expected_receipt));
    }

    try {
        PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(
            publication, publication_observer, publication_observer_context);
    } catch (const SyncAtomicFilePublicationError& error) {
        throw_protocol_error(
            SqliteReplayLedgerResetReceiptProtocolFailure::
                ReceiptPublicationAfterExactDurableOutcome,
            SqliteReplayLedgerResetReceiptDurableEvidence::
                ExactRequestDurable,
            SqliteReplayLedgerResetReceiptRecoveryAction::
                ReplayExactRequestToFreshReceiptPath,
            reset_result.outcome, expected_receipt,
            SqliteReplayLedgerResetReceiptPublicationEffect{error.outcome(),
                                                             error.residue()},
            error.what());
    } catch (...) {
        rethrow_current_as_protocol_error(
            SqliteReplayLedgerResetReceiptProtocolFailure::
                ReceiptPublicationAfterExactDurableOutcome,
            SqliteReplayLedgerResetReceiptDurableEvidence::
                ExactRequestDurable,
            SqliteReplayLedgerResetReceiptRecoveryAction::
                ReplayExactRequestToFreshReceiptPath,
            reset_result.outcome, expected_receipt, std::nullopt);
    }

    return SqliteReplayLedgerResetReceiptProtocolResult{
        std::move(reset_result),
        {SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced,
         SyncAtomicFilePublicationResidue::None}};
}

}  // namespace anonsync::persistence
