#include "local_jsonl_replay_publication.hpp"

#include <functional>
#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::persistence::FrozenLocalJsonlReplayEntry;
using anonsync::persistence::FrozenLocalJsonlReplayJournal;
using anonsync::persistence::LocalJsonlReplayEntryFields;
using anonsync::persistence::LocalJsonlReplayJournalFields;
using anonsync::persistence::LocalJsonlReplayJournalVersion;
using anonsync::persistence::encode_local_jsonl_replay_entry_json_or_throw;
using anonsync::persistence::encode_local_jsonl_replay_journal_json_or_throw;
using anonsync::persistence::kLocalJsonlReplayMaximumEntryCount;
using anonsync::persistence::kLocalJsonlReplayMaximumExactJsonInteger;
using anonsync::persistence::kLocalJsonlReplayMaximumFieldBytes;
using anonsync::persistence::kLocalJsonlReplayMaximumPathBytes;
using anonsync::persistence::kLocalJsonlReplayMaximumTemporaryNameBytes;
using anonsync::persistence::kLocalJsonlReplayJournalV3Format;
using anonsync::persistence::kLocalJsonlReplayV3CommitProtocol;
using anonsync::persistence::local_jsonl_replay_entry_hash_material_or_throw;

class GroupedNumbers final : public std::numpunct<char> {
protected:
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\3"; }
};

class GlobalLocaleGuard final {
public:
    GlobalLocaleGuard() : previous_(std::locale()) {}
    ~GlobalLocaleGuard() { std::locale::global(previous_); }

private:
    std::locale previous_;
};

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

void require_throws(const std::function<void()>& operation,
                    const std::string& message,
                    int& checks) {
    try {
        operation();
    } catch (const std::exception&) {
        ++checks;
        return;
    }
    throw std::runtime_error(message);
}

LocalJsonlReplayEntryFields valid_entry_fields() {
    LocalJsonlReplayEntryFields fields;
    fields.sequence = 7000;
    fields.previous_hash = std::string(64, 'a');
    fields.case_id = "case-\"quoted\\path-\xc3\xa9";
    fields.kind = "openapi";
    fields.operation_id = "objects.publish";
    fields.contract_digest_sha256 = "contract-digest-v1";
    fields.jti = "jwt-id-7000";
    fields.action = "allow";
    fields.cloud_event_source.clear();
    fields.cloud_event_id.clear();
    fields.effect_idempotency_key = std::string(64, 'b');
    fields.effect_state = "prepared";
    return fields;
}

LocalJsonlReplayJournalFields valid_journal_fields() {
    LocalJsonlReplayJournalFields fields;
    fields.ledger_path = "/tmp/ledger-\"quoted\\path-\xc3\xa9.jsonl";
    fields.previous_head = std::string(64, 'a');
    fields.previous_line_count = 6999;
    fields.next_head = std::string(64, 'b');
    fields.next_line_count = 7000;
    fields.last_entry_previous_hash = std::string(64, 'a');
    fields.payload_sha256 = std::string(64, 'c');
    return fields;
}

LocalJsonlReplayJournalFields valid_journal_v3_fields() {
    auto fields = valid_journal_fields();
    fields.previous_payload_sha256 = std::string(64, 'd');
    fields.temporary_name = "ledger.jsonl.tmp.7000.7000";
    return fields;
}

}  // namespace

int main() {
    try {
        int checks = 0;
        GlobalLocaleGuard locale_guard;
        std::locale::global(
            std::locale(std::locale::classic(), new GroupedNumbers));

        const auto entry =
            FrozenLocalJsonlReplayEntry::freeze_or_throw(valid_entry_fields());
        const std::string material =
            local_jsonl_replay_entry_hash_material_or_throw(entry);
        const std::string expected_material =
            std::string("7000\n") + std::string(64, 'a') +
            "\ncase-\"quoted\\path-\xc3\xa9\nopenapi\nobjects.publish\n"
            "contract-digest-v1\njwt-id-7000\nallow\n\n\n" +
            std::string(64, 'b') + "\nprepared";
        require(material == expected_material,
                "entry material changed its legacy compatible bytes", checks);
        require(material.find("7_000") == std::string::npos,
                "entry material inherited the global grouping locale", checks);
        require(entry.entry_hash().size() == 64,
                "entry hash does not have SHA-256 text width", checks);
        require(entry.entry_hash().find_first_not_of("0123456789abcdef") ==
                    std::string::npos,
                "entry hash is not lowercase hexadecimal", checks);

        const std::string entry_json =
            encode_local_jsonl_replay_entry_json_or_throw(entry);
        const std::string expected_json =
            std::string("{\"sequence\":7000,\"previous_hash\":\"") +
            std::string(64, 'a') + "\",\"entry_hash\":\"" +
            entry.entry_hash() +
            "\",\"case_id\":\"case-\\\"quoted\\\\path-\xc3\xa9\","
            "\"kind\":\"openapi\",\"operation_id\":\"objects.publish\","
            "\"contract_digest_sha256\":\"contract-digest-v1\","
            "\"jti\":\"jwt-id-7000\",\"action\":\"allow\","
            "\"cloud_event_source\":\"\",\"cloud_event_id\":\"\","
            "\"effect_idempotency_key\":\"" +
            std::string(64, 'b') +
            "\",\"effect_state\":\"prepared\"}";
        require(entry_json == expected_json,
                "entry JSON is not the exact canonical compatibility row", checks);
        require(entry_json.find("7_000") == std::string::npos,
                "entry JSON inherited the global grouping locale", checks);

        auto changed_fields = valid_entry_fields();
        changed_fields.jti = "jwt-id-7001";
        const auto changed = FrozenLocalJsonlReplayEntry::freeze_or_throw(
            std::move(changed_fields));
        require(changed.entry_hash() != entry.entry_hash(),
                "entry hash did not bind a changed field", checks);

        auto first_fields = valid_entry_fields();
        first_fields.sequence = 1;
        first_fields.previous_hash = "GENESIS";
        require(FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(first_fields))
                        .fields()
                        .sequence == 1,
                "first entry was rejected", checks);

        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.case_id = "bad\ncase";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted a delimiter-bearing control", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.jti = std::string("bad\xc3\x28", 5);
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted malformed UTF-8", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.sequence = 0;
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted sequence zero", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.sequence = kLocalJsonlReplayMaximumExactJsonInteger + 1;
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted a non-interoperable JSON integer", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.previous_hash = "GENESIS";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted GENESIS after sequence one", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.previous_hash = "bad";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted an invalid predecessor hash", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.case_id.clear();
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted an empty required field", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.kind = "other";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted an unsupported kind", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.kind = "asyncapi";
                fields.cloud_event_source.clear();
                fields.cloud_event_id = "event";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "async entry accepted a missing source", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.effect_idempotency_key = std::string(63, 'b');
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted an invalid effect key", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.effect_state = "applied";
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted a non-prepared state", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.operation_id.assign(
                    kLocalJsonlReplayMaximumFieldBytes + 1, 'x');
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted an oversized field", checks);
        require_throws(
            [] {
                auto fields = valid_entry_fields();
                fields.case_id.assign(kLocalJsonlReplayMaximumFieldBytes, 'c');
                fields.operation_id.assign(kLocalJsonlReplayMaximumFieldBytes,
                                           'o');
                fields.contract_digest_sha256.assign(
                    kLocalJsonlReplayMaximumFieldBytes, 'd');
                fields.jti.assign(kLocalJsonlReplayMaximumFieldBytes, 'j');
                (void)FrozenLocalJsonlReplayEntry::freeze_or_throw(
                    std::move(fields));
            },
            "entry accepted hash material over its document budget", checks);

        const auto journal = FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
            valid_journal_fields());
        const std::string journal_json =
            encode_local_jsonl_replay_journal_json_or_throw(journal);
        const std::string expected_journal =
            std::string("{\n  \"format\": \"anonsync-replay-ledger-journal-v2\",\n") +
            "  \"ledger_path\": \"/tmp/ledger-\\\"quoted\\\\path-\xc3\xa9.jsonl\",\n"
            "  \"previous_head\": \"" + std::string(64, 'a') +
            "\",\n  \"previous_line_count\": 6999,\n"
            "  \"next_head\": \"" + std::string(64, 'b') +
            "\",\n  \"next_line_count\": 7000,\n"
            "  \"last_entry_previous_hash\": \"" +
            std::string(64, 'a') +
            "\",\n  \"payload_sha256\": \"" + std::string(64, 'c') +
            "\",\n  \"commit_protocol\": \"lock write-journal fsync-journal temp-write fsync rename fsync-dir unlink-journal\"\n}\n";
        require(journal_json == expected_journal,
                "journal JSON is not the exact v2 compatibility publication",
                checks);
        require(journal_json.find("7_000") == std::string::npos,
                "journal JSON inherited the global grouping locale", checks);

        const auto journal_v3 =
            FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                valid_journal_v3_fields());
        require(journal_v3.version() ==
                    LocalJsonlReplayJournalVersion::crash_complete_v3,
                "v3 journal did not retain its version", checks);
        require(journal_v3.format() == kLocalJsonlReplayJournalV3Format,
                "v3 journal did not retain its format", checks);
        require(journal_v3.commit_protocol() ==
                    kLocalJsonlReplayV3CommitProtocol,
                "v3 journal did not retain its crash-complete protocol",
                checks);
        const std::string journal_v3_json =
            encode_local_jsonl_replay_journal_json_or_throw(journal_v3);
        const std::string expected_journal_v3 =
            std::string("{\n  \"format\": \"anonsync-replay-ledger-journal-v3\",\n") +
            "  \"ledger_path\": \"/tmp/ledger-\\\"quoted\\\\path-\xc3\xa9.jsonl\",\n"
            "  \"previous_head\": \"" + std::string(64, 'a') +
            "\",\n  \"previous_line_count\": 6999,\n"
            "  \"previous_payload_sha256\": \"" + std::string(64, 'd') +
            "\",\n  \"next_head\": \"" + std::string(64, 'b') +
            "\",\n  \"next_line_count\": 7000,\n"
            "  \"last_entry_previous_hash\": \"" +
            std::string(64, 'a') +
            "\",\n  \"payload_sha256\": \"" + std::string(64, 'c') +
            "\",\n  \"temporary_name\": \"ledger.jsonl.tmp.7000.7000\",\n"
            "  \"commit_protocol\": \"lock create-temp write-temp fsync-temp create-journal-stage write-journal-stage fsync-journal-stage link-journal-stage-to-journal unlink-journal-stage fsync-directory rename-temp-to-ledger fsync-directory unlink-journal fsync-directory\"\n}\n";
        require(journal_v3_json == expected_journal_v3,
                "journal JSON is not the exact v3 crash-complete publication",
                checks);
        require(journal_v3_json.find("7_000") == std::string::npos,
                "v3 journal JSON inherited the global grouping locale", checks);

        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.ledger_path = "bad\npath";
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted a delimiter-bearing path", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.ledger_path = std::string("bad\xc3\x28", 5);
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted malformed UTF-8", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.previous_line_count = 0;
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted a GENESIS/count mismatch", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.next_line_count = fields.previous_line_count;
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted a non-advancing replacement", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.next_head = "GENESIS";
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted a GENESIS next head", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.payload_sha256 = "bad";
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted an invalid payload digest", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.next_line_count =
                    static_cast<std::int64_t>(
                        kLocalJsonlReplayMaximumEntryCount) +
                    1;
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted an entry count over budget", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                fields.ledger_path.assign(kLocalJsonlReplayMaximumPathBytes + 1,
                                          'p');
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "journal accepted an oversized path", checks);
        require_throws(
            [] {
                auto fields = valid_journal_v3_fields();
                fields.previous_payload_sha256 = "bad";
                (void)FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                    std::move(fields));
            },
            "v3 journal accepted an invalid previous payload digest", checks);
        require_throws(
            [] {
                auto fields = valid_journal_v3_fields();
                fields.temporary_name = "outside/name";
                (void)FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                    std::move(fields));
            },
            "v3 journal accepted a multi-component temporary name", checks);
        require_throws(
            [] {
                auto fields = valid_journal_v3_fields();
                fields.temporary_name.clear();
                (void)FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                    std::move(fields));
            },
            "v3 journal accepted an empty temporary name", checks);
        require_throws(
            [] {
                auto fields = valid_journal_v3_fields();
                fields.temporary_name.assign(
                    kLocalJsonlReplayMaximumTemporaryNameBytes + 1, 't');
                (void)FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                    std::move(fields));
            },
            "v3 journal accepted an oversized temporary name", checks);
        require_throws(
            [] {
                auto fields = valid_journal_v3_fields();
                (void)FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                    std::move(fields));
            },
            "v2 journal accepted v3-only fields", checks);
        require_throws(
            [] {
                auto fields = valid_journal_fields();
                (void)FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                    std::move(fields));
            },
            "v3 journal accepted missing v3-only fields", checks);

        std::cout << "local JSONL replay publication: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "local JSONL replay publication: " << error.what()
                  << '\n';
        return 1;
    }
}
