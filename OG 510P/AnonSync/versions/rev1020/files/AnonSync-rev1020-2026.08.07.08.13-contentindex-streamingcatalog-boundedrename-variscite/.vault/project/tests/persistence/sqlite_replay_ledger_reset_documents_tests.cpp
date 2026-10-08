#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_reset_documents.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

class TestState final {
public:
    void check(bool condition, const std::string& label) {
        ++total_;
        if (condition) {
            ++passed_;
        } else {
            std::cerr << "FAIL: " << label << '\n';
        }
    }

    int finish() const {
        std::cout << "sqlite replay-ledger reset documents: " << passed_
                  << "/" << total_ << " checks passed\n";
        return passed_ == total_ ? 0 : 1;
    }

private:
    int total_ = 0;
    int passed_ = 0;
};

anonsync::persistence::SqliteReplayLedgerResetState make_state() {
    anonsync::persistence::SqliteReplayLedgerResetState state;
    state.normalized_ledger_path =
        std::filesystem::absolute(
            std::filesystem::path("reset-documents") / "ledger.sqlite")
            .lexically_normal()
            .generic_string();
    state.namespace_identity.parent_device = 11;
    state.namespace_identity.parent_inode = 12;
    state.namespace_identity.database_device = 13;
    state.namespace_identity.database_inode = 14;
    state.ledger_instance_id = std::string(64, '1');
    state.state_sha256 = std::string(64, '2');
    state.durable_line_count = 1;
    state.durable_head_hash = std::string(64, '3');
    state.effect_transition_line_count = 1;
    state.effect_transition_head_hash = std::string(64, '4');
    state.ledger_entry_rows = 1;
    state.effect_transition_rows = 1;
    state.effect_outbox_rows = 1;
    state.ingress_sender_replay_rows = 1;
    state.connection_owner_generation = 97;
    return state;
}

bool throws_invalid_request_hash(
    const anonsync::persistence::SqliteReplayLedgerResetRequest& request) {
    try {
        (void)anonsync::persistence::sqlite_replay_ledger_reset_receipt_json(
            request, "not-a-digest");
        return false;
    } catch (const std::invalid_argument&) {
        return true;
    }
}

}  // namespace

int main() {
    using anonsync::persistence::SqliteReplayLedgerResetRequest;
    using anonsync::persistence::sqlite_replay_ledger_reset_expectation_from_state;
    using anonsync::persistence::sqlite_replay_ledger_reset_receipt_json;
    using anonsync::persistence::sqlite_replay_ledger_reset_receipt_sha256;
    using anonsync::persistence::sqlite_replay_ledger_reset_state_report_json;

    TestState tests;
    const auto state = make_state();
    const auto expected =
        sqlite_replay_ledger_reset_expectation_from_state(state);
    tests.check(expected.namespace_identity == state.namespace_identity,
                "expectation preserves exact namespace identity");
    tests.check(expected.ledger_instance_id == state.ledger_instance_id &&
                    expected.state_sha256 == state.state_sha256,
                "expectation preserves durable identity and state digest");
    tests.check(expected.durable_line_count == state.durable_line_count &&
                    expected.durable_head_hash == state.durable_head_hash &&
                    expected.effect_transition_line_count ==
                        state.effect_transition_line_count &&
                    expected.effect_transition_head_hash ==
                        state.effect_transition_head_hash,
                "expectation preserves both chain summaries");
    tests.check(expected.ledger_entry_rows == state.ledger_entry_rows &&
                    expected.effect_transition_rows ==
                        state.effect_transition_rows &&
                    expected.effect_outbox_rows == state.effect_outbox_rows &&
                    expected.ingress_sender_replay_rows ==
                        state.ingress_sender_replay_rows,
                "expectation preserves every operational row count");

    const std::string state_report =
        sqlite_replay_ledger_reset_state_report_json(state);
    tests.check(state_report.find(
                    "\"format\": \"anonsync-sqlite-replay-ledger-reset-state-v2\"") !=
                    std::string::npos,
                "state report owns the exact state-document format");
    tests.check(state_report.find(
                    "\"connection_owner_generation\": \"97\"") !=
                    std::string::npos,
                "state report retains explicitly observation-local evidence");
    tests.check(state_report.find("\"database_inode\": \"14\"") !=
                    std::string::npos,
                "state report renders namespace identity as exact decimal text");

    SqliteReplayLedgerResetRequest request;
    request.ledger_path = state.normalized_ledger_path;
    request.reset_intent_id = "documents-test-001";
    request.operator_id = "operator-\"alpha";
    request.reason = "canonical receipt hashes exact operator reason bytes";
    request.expected = expected;
    const std::string request_sha256(64, 'a');

    const std::string first =
        sqlite_replay_ledger_reset_receipt_json(request, request_sha256);
    const std::string second =
        sqlite_replay_ledger_reset_receipt_json(request, request_sha256);
    const std::string durable_identity =
        sqlite_replay_ledger_reset_receipt_sha256(request);

    tests.check(first == second,
                "receipt rendering is byte-identical for the exact same evidence");
    tests.check(first.find(
                    "\"format\": \"anonsync-sqlite-replay-ledger-reset-receipt-v4\"") !=
                    std::string::npos,
                "receipt owns a new canonical format version");
    tests.check(first.find("\"durable_outcome\": \"committed\"") !=
                    std::string::npos,
                "receipt describes the durable event rather than the current attempt");
    tests.check(first.find("\"reset_receipt_sha256\": \"" +
                               durable_identity + "\"") != std::string::npos &&
                    first.find("\"ledger_instance_id\": \"" +
                               durable_identity + "\"") != std::string::npos,
                "receipt binds the new durable identity to the reset digest");
    tests.check(first.find("\"request_sha256\": \"" + request_sha256 +
                               "\"") != std::string::npos,
                "receipt binds exact request-file bytes");
    tests.check(first.find("operator-\\\"alpha") != std::string::npos,
                "receipt JSON escaping preserves operator-controlled text");
    tests.check(first.find("\"outcome\"") == std::string::npos &&
                    first.find("connection_owner_generation") ==
                        std::string::npos &&
                    first.find("state_advanced_after_commit") ==
                        std::string::npos,
                "receipt excludes attempt-local and later-state observations");
    tests.check(first.find(
                    "replay-exact-digest-pinned-request-to-fresh-immutable-receipt-path") !=
                    std::string::npos,
                "receipt names the fresh-path immutable recovery protocol");

    const std::string changed_request_bytes =
        sqlite_replay_ledger_reset_receipt_json(request, std::string(64, 'b'));
    tests.check(changed_request_bytes != first,
                "changing the exact request-file digest changes receipt bytes");
    tests.check(throws_invalid_request_hash(request),
                "receipt rejects malformed request-byte evidence");
    tests.check(anonsync::is_lowercase_sha256_hex(anonsync::sha256_hex(first)),
                "canonical receipt bytes have stable digestable representation");

    return tests.finish();
}
