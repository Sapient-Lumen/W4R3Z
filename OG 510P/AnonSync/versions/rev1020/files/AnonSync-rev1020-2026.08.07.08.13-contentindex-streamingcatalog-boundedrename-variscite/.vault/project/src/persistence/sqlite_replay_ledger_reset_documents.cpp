#include "sqlite_replay_ledger_reset_documents.hpp"

#include "sha256_digest.hpp"

#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync::persistence {
namespace {

std::string json_escape_document_text(std::string_view value) {
    constexpr char kHex[] = "0123456789abcdef";
    std::string escaped;
    escaped.reserve(value.size());
    for (const unsigned char character : value) {
        switch (character) {
            case '"':
                escaped += "\\\"";
                break;
            case '\\':
                escaped += "\\\\";
                break;
            case '\b':
                escaped += "\\b";
                break;
            case '\f':
                escaped += "\\f";
                break;
            case '\n':
                escaped += "\\n";
                break;
            case '\r':
                escaped += "\\r";
                break;
            case '\t':
                escaped += "\\t";
                break;
            default:
                if (character < 0x20U) {
                    escaped += "\\u00";
                    escaped.push_back(kHex[(character >> 4U) & 0x0fU]);
                    escaped.push_back(kHex[character & 0x0fU]);
                } else {
                    escaped.push_back(static_cast<char>(character));
                }
                break;
        }
    }
    return escaped;
}

std::string expectation_json(
    const SqliteReplayLedgerResetExpectation& expected,
    std::string_view indent) {
    std::ostringstream out;
    out << indent << "{\n"
        << indent << "  \"namespace_identity\": {\n"
        << indent << "    \"parent_device\": \""
        << expected.namespace_identity.parent_device << "\",\n"
        << indent << "    \"parent_inode\": \""
        << expected.namespace_identity.parent_inode << "\",\n"
        << indent << "    \"database_device\": \""
        << expected.namespace_identity.database_device << "\",\n"
        << indent << "    \"database_inode\": \""
        << expected.namespace_identity.database_inode << "\"\n"
        << indent << "  },\n"
        << indent << "  \"ledger_instance_id\": \""
        << json_escape_document_text(expected.ledger_instance_id) << "\",\n"
        << indent << "  \"state_sha256\": \""
        << expected.state_sha256 << "\",\n"
        << indent << "  \"durable_line_count\": "
        << expected.durable_line_count << ",\n"
        << indent << "  \"durable_head_hash\": \""
        << json_escape_document_text(expected.durable_head_hash) << "\",\n"
        << indent << "  \"effect_transition_line_count\": "
        << expected.effect_transition_line_count << ",\n"
        << indent << "  \"effect_transition_head_hash\": \""
        << json_escape_document_text(expected.effect_transition_head_hash)
        << "\",\n"
        << indent << "  \"ledger_entry_rows\": "
        << expected.ledger_entry_rows << ",\n"
        << indent << "  \"effect_transition_rows\": "
        << expected.effect_transition_rows << ",\n"
        << indent << "  \"effect_outbox_rows\": "
        << expected.effect_outbox_rows << ",\n"
        << indent << "  \"ingress_sender_replay_rows\": "
        << expected.ingress_sender_replay_rows << "\n"
        << indent << "}";
    return out.str();
}

}  // namespace

SqliteReplayLedgerResetExpectation
sqlite_replay_ledger_reset_expectation_from_state(
    const SqliteReplayLedgerResetState& state) {
    SqliteReplayLedgerResetExpectation expected;
    expected.namespace_identity = state.namespace_identity;
    expected.ledger_instance_id = state.ledger_instance_id;
    expected.state_sha256 = state.state_sha256;
    expected.durable_line_count = state.durable_line_count;
    expected.durable_head_hash = state.durable_head_hash;
    expected.effect_transition_line_count =
        state.effect_transition_line_count;
    expected.effect_transition_head_hash =
        state.effect_transition_head_hash;
    expected.ledger_entry_rows = state.ledger_entry_rows;
    expected.effect_transition_rows = state.effect_transition_rows;
    expected.effect_outbox_rows = state.effect_outbox_rows;
    expected.ingress_sender_replay_rows = state.ingress_sender_replay_rows;
    return expected;
}

std::string sqlite_replay_ledger_reset_state_report_json(
    const SqliteReplayLedgerResetState& state) {
    const SqliteReplayLedgerResetExpectation expected =
        sqlite_replay_ledger_reset_expectation_from_state(state);
    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << kSqliteReplayLedgerResetStateFormat
        << "\",\n"
        << "  \"backend_name\": \"sqlite-wal\",\n"
        << "  \"ledger_path\": \""
        << json_escape_document_text(state.normalized_ledger_path) << "\",\n"
        << "  \"expected\": " << expectation_json(expected, "  ")
        << ",\n"
        << "  \"observation\": {\n"
        << "    \"connection_owner_generation\": \""
        << state.connection_owner_generation << "\"\n"
        << "  }\n"
        << "}\n";
    return out.str();
}

std::string sqlite_replay_ledger_reset_receipt_json(
    const SqliteReplayLedgerResetRequest& request,
    std::string_view request_sha256) {
    const std::string request_digest(request_sha256);
    if (!is_lowercase_sha256_hex(request_digest)) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset receipt requires the lowercase SHA-256 of exact request bytes");
    }

    // This validates the complete request, including an absolute normalized
    // path and every exact prior-state field, before any document bytes exist.
    const std::string durable_receipt =
        sqlite_replay_ledger_reset_receipt_sha256(request);
    const std::string reason_sha256 = sha256_hex(request.reason);

    std::ostringstream out;
    out << "{\n"
        << "  \"format\": \"" << kSqliteReplayLedgerResetReceiptFormat
        << "\",\n"
        << "  \"backend_name\": \"sqlite-wal\",\n"
        << "  \"durable_outcome\": \"committed\",\n"
        << "  \"request_sha256\": \"" << request_digest << "\",\n"
        << "  \"reset_intent_id\": \""
        << json_escape_document_text(request.reset_intent_id) << "\",\n"
        << "  \"operator_id\": \""
        << json_escape_document_text(request.operator_id) << "\",\n"
        << "  \"reason_sha256\": \"" << reason_sha256 << "\",\n"
        << "  \"ledger_path\": \""
        << json_escape_document_text(request.ledger_path.generic_string())
        << "\",\n"
        << "  \"prior\": " << expectation_json(request.expected, "  ")
        << ",\n"
        << "  \"new\": {\n"
        << "    \"ledger_instance_id\": \"" << durable_receipt << "\",\n"
        << "    \"durable_line_count\": 0,\n"
        << "    \"durable_head_hash\": \"GENESIS\",\n"
        << "    \"effect_transition_line_count\": 0,\n"
        << "    \"effect_transition_head_hash\": \"GENESIS\",\n"
        << "    \"ledger_entry_rows\": 0,\n"
        << "    \"effect_transition_rows\": 0,\n"
        << "    \"effect_outbox_rows\": 0,\n"
        << "    \"ingress_sender_replay_rows\": 0\n"
        << "  },\n"
        << "  \"commit_protocol\": "
           "\"sqlite-wal-begin-immediate-exact-state-in-place-no-namespace-delete\",\n"
        << "  \"recovery_protocol\": "
           "\"replay-exact-digest-pinned-request-to-fresh-immutable-receipt-path\",\n"
        << "  \"reset_receipt_sha256\": \"" << durable_receipt
        << "\"\n"
        << "}\n";
    return out.str();
}

}  // namespace anonsync::persistence
