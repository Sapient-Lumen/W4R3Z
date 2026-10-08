#include "local_jsonl_replay_publication.hpp"

#include "frozen_publication_primitives.hpp"
#include "sha256_digest.hpp"

#include <stdexcept>
#include <string_view>
#include <utility>

namespace anonsync::persistence {
namespace {

using publication_detail::BoundedMachineText;
using publication_detail::append_json_member_prefix;
using publication_detail::append_json_string;
using publication_detail::is_lower_hex_sha256;
using publication_detail::is_sha256_or_genesis;
using publication_detail::require_nonempty_bounded_control_free;

void require_optional_bounded_control_free(std::string_view value,
                                           std::size_t maximum_bytes,
                                           std::string_view label) {
    if (value.size() > maximum_bytes) {
        throw std::runtime_error(std::string(label) + " exceeds byte budget");
    }
    if (publication_detail::contains_ascii_control(value)) {
        throw std::runtime_error(std::string(label) +
                                 " contains an ASCII control");
    }
    if (!publication_detail::is_well_formed_utf8(value)) {
        throw std::runtime_error(std::string(label) +
                                 " is not well-formed UTF-8");
    }
}

void validate_entry_fields_or_throw(
    const LocalJsonlReplayEntryFields& fields) {
    if (fields.sequence <= 0 ||
        fields.sequence > kLocalJsonlReplayMaximumExactJsonInteger) {
        throw std::runtime_error(
            "local JSONL replay entry sequence is outside exact JSON range");
    }
    if (!is_sha256_or_genesis(fields.previous_hash)) {
        throw std::runtime_error(
            "local JSONL replay entry previous hash is invalid");
    }
    if ((fields.sequence == 1) != (fields.previous_hash == "GENESIS")) {
        throw std::runtime_error(
            "local JSONL replay entry sequence and previous hash disagree");
    }

    require_nonempty_bounded_control_free(
        fields.case_id, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry case id");
    require_nonempty_bounded_control_free(
        fields.kind, kLocalJsonlReplayMaximumKindBytes,
        "local JSONL replay entry kind");
    if (fields.kind != "openapi" && fields.kind != "asyncapi") {
        throw std::runtime_error(
            "local JSONL replay entry kind is unsupported");
    }
    require_nonempty_bounded_control_free(
        fields.operation_id, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry operation id");
    require_nonempty_bounded_control_free(
        fields.contract_digest_sha256, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry contract digest");
    require_nonempty_bounded_control_free(
        fields.jti, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry jti");
    require_nonempty_bounded_control_free(
        fields.action, kLocalJsonlReplayMaximumActionBytes,
        "local JSONL replay entry action");
    require_optional_bounded_control_free(
        fields.cloud_event_source, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry CloudEvents source");
    require_optional_bounded_control_free(
        fields.cloud_event_id, kLocalJsonlReplayMaximumFieldBytes,
        "local JSONL replay entry CloudEvents id");
    if (fields.kind == "asyncapi" &&
        (fields.cloud_event_source.empty() || fields.cloud_event_id.empty())) {
        throw std::runtime_error(
            "local JSONL replay async entry requires CloudEvents source and id");
    }
    if (!is_lower_hex_sha256(fields.effect_idempotency_key)) {
        throw std::runtime_error(
            "local JSONL replay entry effect idempotency key is invalid");
    }
    if (fields.effect_state != "prepared") {
        throw std::runtime_error(
            "local JSONL replay entry effect state is unsupported");
    }
}

std::string entry_hash_material_from_fields_or_throw(
    const LocalJsonlReplayEntryFields& fields) {
    BoundedMachineText out(kLocalJsonlReplayMaximumEntryHashMaterialBytes,
                           "local JSONL replay entry hash material");
    out.append_decimal(fields.sequence);
    out.append('\n');
    out.append(fields.previous_hash);
    out.append('\n');
    out.append(fields.case_id);
    out.append('\n');
    out.append(fields.kind);
    out.append('\n');
    out.append(fields.operation_id);
    out.append('\n');
    out.append(fields.contract_digest_sha256);
    out.append('\n');
    out.append(fields.jti);
    out.append('\n');
    out.append(fields.action);
    out.append('\n');
    out.append(fields.cloud_event_source);
    out.append('\n');
    out.append(fields.cloud_event_id);
    out.append('\n');
    out.append(fields.effect_idempotency_key);
    out.append('\n');
    out.append(fields.effect_state);
    return std::move(out).finish();
}

void validate_journal_fields_or_throw(
    const LocalJsonlReplayJournalFields& fields,
    LocalJsonlReplayJournalVersion version) {
    validate_local_jsonl_replay_ledger_path_or_throw(fields.ledger_path);
    if (!is_sha256_or_genesis(fields.previous_head)) {
        throw std::runtime_error(
            "local JSONL replay journal previous head is invalid");
    }
    if (fields.previous_line_count < 0 ||
        fields.previous_line_count >
            kLocalJsonlReplayMaximumExactJsonInteger ||
        static_cast<std::uint64_t>(fields.previous_line_count) >
            kLocalJsonlReplayMaximumEntryCount) {
        throw std::runtime_error(
            "local JSONL replay journal previous line count is invalid");
    }
    if ((fields.previous_line_count == 0) !=
        (fields.previous_head == "GENESIS")) {
        throw std::runtime_error(
            "local JSONL replay journal previous count and head disagree");
    }
    if (!is_lower_hex_sha256(fields.next_head)) {
        throw std::runtime_error(
            "local JSONL replay journal next head is invalid");
    }
    if (fields.next_line_count <= fields.previous_line_count ||
        fields.next_line_count > kLocalJsonlReplayMaximumExactJsonInteger ||
        static_cast<std::uint64_t>(fields.next_line_count) >
            kLocalJsonlReplayMaximumEntryCount) {
        throw std::runtime_error(
            "local JSONL replay journal next line count is invalid");
    }
    if (!is_sha256_or_genesis(fields.last_entry_previous_hash)) {
        throw std::runtime_error(
            "local JSONL replay journal last-entry previous hash is invalid");
    }
    if (!is_lower_hex_sha256(fields.payload_sha256)) {
        throw std::runtime_error(
            "local JSONL replay journal payload digest is invalid");
    }
    if (version == LocalJsonlReplayJournalVersion::legacy_v2) {
        if (!fields.previous_payload_sha256.empty() ||
            !fields.temporary_name.empty()) {
            throw std::runtime_error(
                "local JSONL replay v2 journal carries v3-only fields");
        }
        return;
    }
    if (!is_lower_hex_sha256(fields.previous_payload_sha256)) {
        throw std::runtime_error(
            "local JSONL replay journal previous payload digest is invalid");
    }
    require_nonempty_bounded_control_free(
        fields.temporary_name,
        kLocalJsonlReplayMaximumTemporaryNameBytes,
        "local JSONL replay journal temporary name");
    if (fields.temporary_name == "." || fields.temporary_name == ".." ||
        fields.temporary_name.find('/') != std::string::npos) {
        throw std::runtime_error(
            "local JSONL replay journal temporary name is not one path component");
    }
}

}  // namespace

void validate_local_jsonl_replay_ledger_path_or_throw(
    std::string_view path) {
    require_nonempty_bounded_control_free(
        path, kLocalJsonlReplayMaximumPathBytes,
        "local JSONL replay journal ledger path");
}

FrozenLocalJsonlReplayEntry FrozenLocalJsonlReplayEntry::freeze_or_throw(
    LocalJsonlReplayEntryFields fields) {
    validate_entry_fields_or_throw(fields);
    const std::string entry_hash = anonsync::sha256_hex(
        entry_hash_material_from_fields_or_throw(fields));
    return FrozenLocalJsonlReplayEntry(std::move(fields), entry_hash);
}

std::string local_jsonl_replay_entry_hash_material_or_throw(
    const FrozenLocalJsonlReplayEntry& entry) {
    return entry_hash_material_from_fields_or_throw(entry.fields());
}

std::string encode_local_jsonl_replay_entry_json_or_throw(
    const FrozenLocalJsonlReplayEntry& entry) {
    const auto& fields = entry.fields();
    BoundedMachineText out(kLocalJsonlReplayMaximumEntryJsonBytes,
                           "local JSONL replay entry JSON");
    out.append('{');
    append_json_string(out, "sequence");
    out.append(':');
    out.append_decimal(fields.sequence);
    out.append(',');
    append_json_string(out, "previous_hash");
    out.append(':');
    append_json_string(out, fields.previous_hash);
    out.append(',');
    append_json_string(out, "entry_hash");
    out.append(':');
    append_json_string(out, entry.entry_hash());
    out.append(',');
    append_json_string(out, "case_id");
    out.append(':');
    append_json_string(out, fields.case_id);
    out.append(',');
    append_json_string(out, "kind");
    out.append(':');
    append_json_string(out, fields.kind);
    out.append(',');
    append_json_string(out, "operation_id");
    out.append(':');
    append_json_string(out, fields.operation_id);
    out.append(',');
    append_json_string(out, "contract_digest_sha256");
    out.append(':');
    append_json_string(out, fields.contract_digest_sha256);
    out.append(',');
    append_json_string(out, "jti");
    out.append(':');
    append_json_string(out, fields.jti);
    out.append(',');
    append_json_string(out, "action");
    out.append(':');
    append_json_string(out, fields.action);
    out.append(',');
    append_json_string(out, "cloud_event_source");
    out.append(':');
    append_json_string(out, fields.cloud_event_source);
    out.append(',');
    append_json_string(out, "cloud_event_id");
    out.append(':');
    append_json_string(out, fields.cloud_event_id);
    out.append(',');
    append_json_string(out, "effect_idempotency_key");
    out.append(':');
    append_json_string(out, fields.effect_idempotency_key);
    out.append(',');
    append_json_string(out, "effect_state");
    out.append(':');
    append_json_string(out, fields.effect_state);
    out.append('}');
    return std::move(out).finish();
}

FrozenLocalJsonlReplayJournal
FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
    LocalJsonlReplayJournalFields fields) {
    validate_journal_fields_or_throw(
        fields, LocalJsonlReplayJournalVersion::legacy_v2);
    return FrozenLocalJsonlReplayJournal(
        LocalJsonlReplayJournalVersion::legacy_v2, std::move(fields));
}

FrozenLocalJsonlReplayJournal
FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
    LocalJsonlReplayJournalFields fields) {
    validate_journal_fields_or_throw(
        fields, LocalJsonlReplayJournalVersion::crash_complete_v3);
    return FrozenLocalJsonlReplayJournal(
        LocalJsonlReplayJournalVersion::crash_complete_v3,
        std::move(fields));
}

std::string_view FrozenLocalJsonlReplayJournal::format() const noexcept {
    return version_ == LocalJsonlReplayJournalVersion::legacy_v2
        ? kLocalJsonlReplayJournalV2Format
        : kLocalJsonlReplayJournalV3Format;
}

std::string_view
FrozenLocalJsonlReplayJournal::commit_protocol() const noexcept {
    return version_ == LocalJsonlReplayJournalVersion::legacy_v2
        ? kLocalJsonlReplayV2CommitProtocol
        : kLocalJsonlReplayV3CommitProtocol;
}

std::string encode_local_jsonl_replay_journal_json_or_throw(
    const FrozenLocalJsonlReplayJournal& journal) {
    const auto& fields = journal.fields();
    BoundedMachineText out(kLocalJsonlReplayMaximumJournalJsonBytes,
                           "local JSONL replay journal JSON");
    out.append("{\n");
    append_json_member_prefix(out, "  ", "format");
    append_json_string(out, journal.format());
    out.append(",\n");
    append_json_member_prefix(out, "  ", "ledger_path");
    append_json_string(out, fields.ledger_path);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "previous_head");
    append_json_string(out, fields.previous_head);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "previous_line_count");
    out.append_decimal(fields.previous_line_count);
    out.append(",\n");
    if (journal.version() ==
        LocalJsonlReplayJournalVersion::crash_complete_v3) {
        append_json_member_prefix(out, "  ", "previous_payload_sha256");
        append_json_string(out, fields.previous_payload_sha256);
        out.append(",\n");
    }
    append_json_member_prefix(out, "  ", "next_head");
    append_json_string(out, fields.next_head);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "next_line_count");
    out.append_decimal(fields.next_line_count);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "last_entry_previous_hash");
    append_json_string(out, fields.last_entry_previous_hash);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "payload_sha256");
    append_json_string(out, fields.payload_sha256);
    out.append(",\n");
    if (journal.version() ==
        LocalJsonlReplayJournalVersion::crash_complete_v3) {
        append_json_member_prefix(out, "  ", "temporary_name");
        append_json_string(out, fields.temporary_name);
        out.append(",\n");
    }
    append_json_member_prefix(out, "  ", "commit_protocol");
    append_json_string(out, journal.commit_protocol());
    out.append("\n}\n");
    return std::move(out).finish();
}

}  // namespace anonsync::persistence
