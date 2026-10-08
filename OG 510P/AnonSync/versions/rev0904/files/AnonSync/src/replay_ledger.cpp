#include "anonsync_core_internal.hpp"
#include "persistence/local_jsonl_replay_namespace.hpp"
#include "persistence/local_jsonl_replay_publication.hpp"

#include <cstdlib>
#include <optional>
#include <unistd.h>

namespace anonsync {

// rev0600 translation unit: explicit replay-ledger backend interface, sidecar symlink rejection, and journal-unlink interruption recovery.
// rev0599 compatibility needle: replay-ledger backend adapter with strict journal-v2 recovery and stage/commit backend boundary.
// rev0598 compatibility needle: replay-ledger backend adapter with immediate and explicit batch transaction modes.
// rev0597 compatibility needle: nonblocking lock ownership, write-ahead journal records, semantic journal recovery validation, crash-point fault injection.
// rev0597 compatibility needle: recovered journal previous head semantic journal recovery validation retained through strict v2 prefix/last-entry checks.
// rev0595 compatibility needle: atomic temp-write fsync rename directory-fsync.

namespace {

class ReplayLedgerFaultInjection final : public std::runtime_error {
public:
    explicit ReplayLedgerFaultInjection(const std::string& checkpoint)
        : std::runtime_error(
              "simulated durable replay ledger crash at checkpoint " +
              checkpoint) {}
};

std::string event_identity_key(const std::string& cloud_event_source,
                               const std::string& cloud_event_id) {
    if (cloud_event_source.empty() || cloud_event_id.empty()) return "";
    return length_prefixed_security_tuple(
        "anonsync-cloud-event-identity-v2",
        {{"source", cloud_event_source}, {"id", cloud_event_id}});
}

constexpr const char* kPreparedEffectState = "prepared";

std::string effect_idempotency_key_from_case_or_legacy(const Json& tc,
                                                        const Json& claims) {
    const std::string supplied = tc.at("effect_idempotency_key").str();
    if (!supplied.empty()) return supplied;
    // Compatibility fallback for older in-process selftests and
    // pre-normalized controls. Normalized request/event envelopes carry a
    // stronger key over their complete request or event identity.
    return sha256_hex(length_prefixed_security_tuple(
        "anonsync-effect-idempotency-legacy-v1",
        {{"case_id", tc.at("case_id").str()},
         {"kind", tc.at("kind").str()},
         {"operation_id", claims.at("operation_id").str()},
         {"contract_digest_sha256",
          claims.at("contract_digest_sha256").str()},
         {"cloud_event_source", tc.at("cloud_event_source").str()},
         {"cloud_event_id", tc.at("cloud_event_id").str()}}));
}

std::string effect_state_from_case_or_default(const Json& tc) {
    const std::string supplied = tc.at("effect_state").str();
    return supplied.empty() ? std::string(kPreparedEffectState) : supplied;
}

std::string require_json_string(const Json& value,
                                const std::string& label) {
    if (!value.is_string()) {
        throw std::runtime_error(label + " must be a JSON string");
    }
    return value.s;
}

std::int64_t require_json_integer(const Json& value,
                                  const std::string& label) {
    if (!value.is_number()) {
        throw std::runtime_error(label + " must be a JSON number");
    }
    try {
        return value.integer();
    } catch (const std::exception& error) {
        throw std::runtime_error(label + ": " + error.what());
    }
}

void require_exact_json_object_fields(
    const Json& value,
    const std::set<std::string>& expected,
    const std::string& label) {
    if (!value.is_object()) {
        throw std::runtime_error(label + " must be a JSON object");
    }
    if (value.o.size() != expected.size()) {
        throw std::runtime_error(label + " has missing or unknown fields");
    }
    for (const auto& field : expected) {
        if (value.o.find(field) == value.o.end()) {
            throw std::runtime_error(label + " is missing field " + field);
        }
    }
}

struct DecodedLedgerEntry final {
    persistence::FrozenLocalJsonlReplayEntry frozen;
};

DecodedLedgerEntry decode_ledger_entry_line_or_throw(
    const std::string& line) {
    if (line.empty()) {
        throw std::runtime_error("replay ledger contains an empty row");
    }
    if (line.size() > persistence::kLocalJsonlReplayMaximumEntryJsonBytes) {
        throw std::runtime_error("replay ledger row exceeds byte budget");
    }
    const Json entry = parse_json_text(line);
    static const std::set<std::string> kEntryFields{
        "sequence", "previous_hash", "entry_hash", "case_id", "kind",
        "operation_id", "contract_digest_sha256", "jti", "action",
        "cloud_event_source", "cloud_event_id", "effect_idempotency_key",
        "effect_state"};
    require_exact_json_object_fields(entry, kEntryFields,
                                     "replay ledger row");

    persistence::LocalJsonlReplayEntryFields fields;
    fields.sequence = require_json_integer(entry.at("sequence"),
                                           "replay ledger row sequence");
    fields.previous_hash = require_json_string(
        entry.at("previous_hash"), "replay ledger row previous_hash");
    fields.case_id = require_json_string(entry.at("case_id"),
                                         "replay ledger row case_id");
    fields.kind = require_json_string(entry.at("kind"),
                                      "replay ledger row kind");
    fields.operation_id = require_json_string(
        entry.at("operation_id"), "replay ledger row operation_id");
    fields.contract_digest_sha256 = require_json_string(
        entry.at("contract_digest_sha256"),
        "replay ledger row contract_digest_sha256");
    fields.jti = require_json_string(entry.at("jti"),
                                     "replay ledger row jti");
    fields.action = require_json_string(entry.at("action"),
                                        "replay ledger row action");
    fields.cloud_event_source = require_json_string(
        entry.at("cloud_event_source"),
        "replay ledger row cloud_event_source");
    fields.cloud_event_id = require_json_string(
        entry.at("cloud_event_id"), "replay ledger row cloud_event_id");
    fields.effect_idempotency_key = require_json_string(
        entry.at("effect_idempotency_key"),
        "replay ledger row effect_idempotency_key");
    fields.effect_state = require_json_string(
        entry.at("effect_state"), "replay ledger row effect_state");
    const std::string supplied_entry_hash = require_json_string(
        entry.at("entry_hash"), "replay ledger row entry_hash");
    if (!is_lowercase_sha256_hex(supplied_entry_hash)) {
        throw std::runtime_error("replay ledger row entry_hash is invalid");
    }

    auto frozen = persistence::FrozenLocalJsonlReplayEntry::freeze_or_throw(
        std::move(fields));
    if (supplied_entry_hash != frozen.entry_hash()) {
        throw std::runtime_error("replay ledger row hash mismatch");
    }
    if (line != persistence::encode_local_jsonl_replay_entry_json_or_throw(
                    frozen)) {
        throw std::runtime_error(
            "replay ledger row is not the canonical publication");
    }
    return DecodedLedgerEntry{std::move(frozen)};
}

struct LedgerPayloadSummary final {
    std::int64_t line_count = 0;
    std::string head = "GENESIS";
    std::string previous_head = "GENESIS";
    std::vector<std::string> heads_by_line;
};

struct ValidatedLedgerPayload final {
    LedgerPayloadSummary summary;
    std::vector<std::string> canonical_lines;
    std::unordered_set<std::string> jtis;
    std::unordered_set<std::string> event_identities;
    std::unordered_set<std::string> effect_idempotency_keys;
};

ValidatedLedgerPayload validate_ledger_payload_or_throw(
    const std::string& payload) {
    if (payload.size() > persistence::kLocalJsonlReplayMaximumLedgerBytes) {
        throw std::runtime_error("replay ledger payload exceeds byte budget");
    }
    ValidatedLedgerPayload validated;
    if (payload.empty()) return validated;
    if (payload.back() != '\n') {
        throw std::runtime_error(
            "replay ledger payload lacks its canonical final newline");
    }

    std::string expected_previous = "GENESIS";
    std::int64_t expected_sequence = 1;
    std::size_t begin = 0;
    while (begin < payload.size()) {
        if (validated.summary.line_count >=
            static_cast<std::int64_t>(
                persistence::kLocalJsonlReplayMaximumEntryCount)) {
            throw std::runtime_error(
                "replay ledger payload exceeds entry-count budget");
        }
        const std::size_t end = payload.find('\n', begin);
        if (end == std::string::npos) {
            throw std::logic_error(
                "replay ledger newline scan lost its terminator");
        }
        if (end == begin) {
            throw std::runtime_error("replay ledger contains an empty row");
        }
        const std::string line = payload.substr(begin, end - begin);
        DecodedLedgerEntry decoded = decode_ledger_entry_line_or_throw(line);
        const auto& fields = decoded.frozen.fields();
        if (fields.sequence != expected_sequence) {
            throw std::runtime_error(
                "replay ledger payload contains a sequence gap");
        }
        if (fields.previous_hash != expected_previous) {
            throw std::runtime_error(
                "replay ledger payload contains a broken hash chain");
        }
        if (!validated.jtis.insert(fields.jti).second) {
            throw std::runtime_error(
                "replay ledger payload contains a duplicate jti");
        }
        if (!validated.effect_idempotency_keys
                 .insert(fields.effect_idempotency_key)
                 .second) {
            throw std::runtime_error(
                "replay ledger payload contains a duplicate effect idempotency key");
        }
        if (fields.kind == "asyncapi") {
            const std::string identity = event_identity_key(
                fields.cloud_event_source, fields.cloud_event_id);
            if (identity.empty() ||
                !validated.event_identities.insert(identity).second) {
                throw std::runtime_error(
                    "replay ledger payload contains an invalid or duplicate event identity");
            }
        }

        validated.summary.previous_head = fields.previous_hash;
        validated.summary.head = decoded.frozen.entry_hash();
        validated.summary.heads_by_line.push_back(
            decoded.frozen.entry_hash());
        validated.canonical_lines.push_back(std::move(line));
        expected_previous = decoded.frozen.entry_hash();
        ++validated.summary.line_count;
        ++expected_sequence;
        begin = end + 1U;
    }
    return validated;
}

persistence::FrozenLocalJsonlReplayJournal decode_journal_or_throw(
    const std::string& body) {
    if (body.empty()) {
        throw std::runtime_error("durable replay ledger journal is empty");
    }
    if (body.size() > persistence::kLocalJsonlReplayMaximumJournalJsonBytes) {
        throw std::runtime_error(
            "durable replay ledger journal exceeds byte budget");
    }
    const Json journal = parse_json_text(body);
    if (!journal.is_object()) {
        throw std::runtime_error(
            "durable replay ledger journal must be a JSON object");
    }
    const std::string format = require_json_string(
        journal.at("format"), "durable replay ledger journal format");
    const bool is_v2 =
        format == persistence::kLocalJsonlReplayJournalV2Format;
    const bool is_v3 =
        format == persistence::kLocalJsonlReplayJournalV3Format;
    if (!is_v2 && !is_v3) {
        throw std::runtime_error(
            "durable replay ledger journal has unknown format");
    }

    static const std::set<std::string> kJournalV2Fields{
        "format", "ledger_path", "previous_head", "previous_line_count",
        "next_head", "next_line_count", "last_entry_previous_hash",
        "payload_sha256", "commit_protocol"};
    static const std::set<std::string> kJournalV3Fields{
        "format", "ledger_path", "previous_head", "previous_line_count",
        "previous_payload_sha256", "next_head", "next_line_count",
        "last_entry_previous_hash", "payload_sha256", "temporary_name",
        "commit_protocol"};
    require_exact_json_object_fields(
        journal, is_v2 ? kJournalV2Fields : kJournalV3Fields,
        "durable replay ledger journal");

    const std::string commit_protocol = require_json_string(
        journal.at("commit_protocol"),
        "durable replay ledger journal commit_protocol");
    const std::string_view expected_commit_protocol =
        is_v2 ? persistence::kLocalJsonlReplayV2CommitProtocol
              : persistence::kLocalJsonlReplayV3CommitProtocol;
    if (commit_protocol != expected_commit_protocol) {
        throw std::runtime_error(
            "durable replay ledger journal has unsupported commit protocol");
    }

    persistence::LocalJsonlReplayJournalFields fields;
    fields.ledger_path = require_json_string(
        journal.at("ledger_path"),
        "durable replay ledger journal ledger_path");
    fields.previous_head = require_json_string(
        journal.at("previous_head"),
        "durable replay ledger journal previous_head");
    fields.previous_line_count = require_json_integer(
        journal.at("previous_line_count"),
        "durable replay ledger journal previous_line_count");
    if (is_v3) {
        fields.previous_payload_sha256 = require_json_string(
            journal.at("previous_payload_sha256"),
            "durable replay ledger journal previous_payload_sha256");
    }
    fields.next_head = require_json_string(
        journal.at("next_head"),
        "durable replay ledger journal next_head");
    fields.next_line_count = require_json_integer(
        journal.at("next_line_count"),
        "durable replay ledger journal next_line_count");
    fields.last_entry_previous_hash = require_json_string(
        journal.at("last_entry_previous_hash"),
        "durable replay ledger journal last_entry_previous_hash");
    fields.payload_sha256 = require_json_string(
        journal.at("payload_sha256"),
        "durable replay ledger journal payload_sha256");
    if (is_v3) {
        fields.temporary_name = require_json_string(
            journal.at("temporary_name"),
            "durable replay ledger journal temporary_name");
    }

    auto frozen = is_v2
        ? persistence::FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
              std::move(fields))
        : persistence::FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
              std::move(fields));
    if (body != persistence::encode_local_jsonl_replay_journal_json_or_throw(
                    frozen)) {
        throw std::runtime_error(
            "durable replay ledger journal is not the canonical publication");
    }
    return frozen;
}
}  // namespace

std::string ReplayLedger::entry_hash_material(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key, const std::string& effect_state) {
    return std::to_string(sequence) + "\n" + previous_hash + "\n" + case_id + "\n" + kind + "\n" + operation_id + "\n" + contract_digest + "\n" + jti + "\n" + action + "\n" + cloud_event_source + "\n" + cloud_event_id + "\n" + effect_idempotency_key + "\n" + effect_state;
}

std::string ReplayLedger::compute_entry_hash(long long sequence, const std::string& previous_hash, const std::string& case_id, const std::string& kind, const std::string& operation_id, const std::string& contract_digest, const std::string& jti, const std::string& action, const std::string& cloud_event_source, const std::string& cloud_event_id, const std::string& effect_idempotency_key, const std::string& effect_state) {
    return sha256_hex(entry_hash_material(sequence, previous_hash, case_id, kind, operation_id, contract_digest, jti, action, cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state));
}

ReplayLedger::ReplayLedger() = default;

ReplayLedger::~ReplayLedger() {
    close();
}


ReplayLedgerStats ReplayLedger::stats() const {
    ReplayLedgerStats st;
    st.backend_name = backend_name();
    st.loaded_entries = loaded_entries;
    st.appended_entries = appended_entries;
    st.atomic_rewrite_commits = atomic_rewrite_commits;
    st.directory_fsync_attempts = directory_fsync_attempts;
    st.lock_acquire_attempts = lock_acquire_attempts;
    st.lock_contention_denials = lock_contention_denials;
    st.journal_records_written = journal_records_written;
    st.journal_recovered_after_commit = journal_recovered_after_commit;
    st.journal_rolled_back_before_commit =
        journal_rolled_back_before_commit;
    st.journal_rejections = journal_rejections;
    st.batch_flush_commits = ledger_batch_flush_commits;
    st.batch_pending_entries_peak = ledger_batch_pending_entries_peak;
    st.durable_line_count = durable_line_count;
    st.durable_head_hash = durable_head_hash;
    st.effect_terminal_transitions = effect_terminal_transitions;
    st.effect_transition_rejections = effect_transition_rejections;
    st.effect_transition_line_count = effect_transition_line_count;
    st.effect_transition_head_hash = effect_transition_head_hash;
    st.backend_factory_selections = 1;
    return st;
}

void ReplayLedger::release_lock() noexcept {
    if (namespace_authority) {
        namespace_authority->release_lock_noexcept();
    }
}

void ReplayLedger::maybe_inject_crash(const std::string& checkpoint) {
    const char* raw = std::getenv("ANONSYNC_LEDGER_FAULT_AT");
    if (!raw) return;
    std::string requested(raw);
    if (requested == checkpoint) {
        throw ReplayLedgerFaultInjection(checkpoint);
    }
}

void ReplayLedger::acquire_lock() {
    if (path.empty()) return;
    release_lock();
    if (!namespace_authority) {
        throw std::logic_error(
            "durable replay ledger namespace authority is absent");
    }
    lock_path = namespace_authority->absolute_lock_path();
    ++lock_acquire_attempts;
    try {
        namespace_authority->acquire_lock_or_throw(
            "durable replay ledger lock");
    } catch (const persistence::LocalJsonlReplayLockContention&) {
        ++lock_contention_denials;
        throw;
    }
}

bool ReplayLedger::write_journal_record(
    const std::string& previous_head,
    long long previous_line_count,
    const std::string& previous_payload_sha256,
    const std::string& next_head,
    long long next_line_count,
    const std::string& last_entry_previous_hash,
    const std::string& payload_sha256,
    const std::string& temporary_name,
    std::string& reason) {
    if (!namespace_authority) {
        reason = "durable replay ledger namespace authority is absent";
        return false;
    }

    persistence::LocalJsonlReplayJournalFields fields;
    fields.ledger_path = path;
    fields.previous_head = previous_head;
    fields.previous_line_count = previous_line_count;
    fields.previous_payload_sha256 = previous_payload_sha256;
    fields.next_head = next_head;
    fields.next_line_count = next_line_count;
    fields.last_entry_previous_hash = last_entry_previous_hash;
    fields.payload_sha256 = payload_sha256;
    fields.temporary_name = temporary_name;

    bool staging_created = false;
    bool journal_published = false;
    try {
        const auto journal =
            persistence::FrozenLocalJsonlReplayJournal::freeze_v3_or_throw(
                std::move(fields));
        const std::string body =
            persistence::encode_local_jsonl_replay_journal_json_or_throw(
                journal);
        auto file =
            namespace_authority->create_journal_staging_exclusive_or_throw(
                "durable replay ledger journal staging file");
        staging_created = true;
        file.write_all_or_throw(
            body, "durable replay ledger journal staging file");
        file.fsync_or_throw(
            "durable replay ledger journal staging file");
        maybe_inject_crash(
            "after-journal-stage-fsync-before-publication");
        namespace_authority->
            publish_open_journal_staging_to_journal_or_throw(
                file.descriptor(),
                "durable replay ledger journal publication");
        journal_published = true;
        file.close_or_throw("durable replay ledger journal");
        ++journal_records_written;
        return true;
    } catch (const ReplayLedgerFaultInjection&) {
        // A crash leaves the exact staging object for startup rollback. Do not
        // turn the injected process boundary into an orderly cleanup path.
        throw;
    } catch (const std::exception& error) {
        reason = error.what();
        // Once the descriptor-bound staging inode has been linked to the final
        // journal name, either the final-only state or the authorized linked
        // pair is a complete recovery witness. Strict staging cleanup refuses
        // the pair, preserving it for startup completion.
        if (staging_created && !journal_published) {
            try {
                if (namespace_authority->
                        unlink_journal_staging_if_present_or_throw(
                            "partial replay journal staging cleanup")) {
                    ++directory_fsync_attempts;
                    namespace_authority->fsync_directory_or_throw(
                        "after partial journal staging cleanup");
                }
            } catch (const std::exception& cleanup_error) {
                reason += "; partial journal staging cleanup failed: ";
                reason += cleanup_error.what();
            }
        }
        return false;
    }
}

void ReplayLedger::recover_or_reject_journal() {
    if (!namespace_authority) {
        throw std::logic_error(
            "durable replay ledger namespace authority is absent");
    }
    (void)namespace_authority->ledger_exists_or_throw(
        "durable replay ledger recovery ledger");

    auto sync_directory = [&](std::string_view phase) {
        ++directory_fsync_attempts;
        namespace_authority->fsync_directory_or_throw(phase);
    };

    try {
        auto publication_state =
            namespace_authority->journal_publication_state_or_throw(
                "durable replay ledger recovery journal publication");
        if (publication_state ==
            persistence::LocalJsonlReplayJournalPublicationState::linked_pair) {
            namespace_authority->
                complete_linked_journal_publication_or_throw(
                    "durable replay ledger linked journal publication recovery");
            sync_directory("after linked journal publication recovery");
            publication_state =
                persistence::LocalJsonlReplayJournalPublicationState::
                    journal_only;
        }
        if (publication_state ==
            persistence::LocalJsonlReplayJournalPublicationState::staging_only) {
            // The final no-overwrite publication name never became visible, so
            // this object has no durable authority to describe a transition.
            // Its bytes may also be partial, and no independent persistent
            // witness binds its inode. Preserve it rather than converting a
            // family-looking pathname into unlink authority. The validated
            // ledger remains usable, while every later commit fails closed on
            // the unresolved staging residue until explicit operator policy
            // removes it.
            ++journal_rolled_back_before_commit;
            return;
        }
        if (publication_state ==
            persistence::LocalJsonlReplayJournalPublicationState::absent) {
            return;
        }
        if (publication_state !=
            persistence::LocalJsonlReplayJournalPublicationState::journal_only) {
            throw std::logic_error(
                "durable replay ledger recovery reached an unknown journal publication state");
        }

        const std::string journal_body =
            namespace_authority->read_journal_or_throw(
                persistence::kLocalJsonlReplayMaximumJournalJsonBytes,
                "durable replay ledger journal");
        const auto journal = decode_journal_or_throw(journal_body);
        const auto& journal_fields = journal.fields();
        const bool journal_path_matches =
            journal_fields.ledger_path == path ||
            (journal.version() ==
                 persistence::LocalJsonlReplayJournalVersion::legacy_v2 &&
             journal_fields.ledger_path == legacy_selected_path_spelling);
        if (!journal_path_matches) {
            throw std::runtime_error(
                "journal path does not match the selected ledger");
        }
        if (journal.version() ==
            persistence::LocalJsonlReplayJournalVersion::crash_complete_v3) {
            namespace_authority->require_owned_temporary_name_or_throw(
                journal_fields.temporary_name,
                "durable replay ledger journal temporary name");
        }

        const std::string payload =
            namespace_authority->read_ledger_or_empty_or_throw(
                persistence::kLocalJsonlReplayMaximumLedgerBytes,
                "durable replay ledger recovery ledger");
        const ValidatedLedgerPayload validated =
            validate_ledger_payload_or_throw(payload);
        const auto& summary = validated.summary;
        const std::string payload_digest = sha256_hex(payload);

        auto require_next_state = [&](const LedgerPayloadSummary& candidate,
                                      std::string_view label) {
            if (journal_fields.next_line_count != candidate.line_count) {
                throw std::runtime_error(
                    std::string(label) +
                    " line count does not match the journal");
            }
            if (journal_fields.next_head != candidate.head) {
                throw std::runtime_error(
                    std::string(label) +
                    " head does not match the journal");
            }
            const std::int64_t previous_line_count =
                journal_fields.previous_line_count;
            if (previous_line_count < 0 ||
                previous_line_count >= candidate.line_count) {
                throw std::runtime_error(
                    std::string(label) +
                    " previous line count is out of range");
            }
            std::string prefix_head = "GENESIS";
            if (previous_line_count > 0) {
                prefix_head = candidate.heads_by_line.at(
                    static_cast<std::size_t>(previous_line_count - 1));
            }
            if (journal_fields.previous_head != prefix_head) {
                throw std::runtime_error(
                    std::string(label) +
                    " prefix head does not match the journal");
            }
            if (journal_fields.last_entry_previous_hash !=
                candidate.previous_head) {
                throw std::runtime_error(
                    std::string(label) +
                    " last-entry predecessor does not match the journal");
            }
        };

        auto retire_v3_temporary_if_present = [&]() {
                if (journal.version() !=
                    persistence::LocalJsonlReplayJournalVersion::
                        crash_complete_v3) {
                    return;
                }
                if (!namespace_authority->temporary_exists_or_throw(
                        journal_fields.temporary_name,
                        "durable replay ledger recovery temporary")) {
                    return;
                }
                const auto temporary = namespace_authority->
                    read_temporary_if_present_or_throw(
                        journal_fields.temporary_name,
                        persistence::kLocalJsonlReplayMaximumLedgerBytes,
                        "durable replay ledger recovery temporary");
                if (!temporary ||
                    sha256_hex(*temporary) !=
                        journal_fields.payload_sha256) {
                    throw std::runtime_error(
                        "journal temporary payload digest does not match the intended replacement");
                }
                const ValidatedLedgerPayload temporary_validated =
                    validate_ledger_payload_or_throw(*temporary);
                require_next_state(temporary_validated.summary,
                                   "journal temporary payload");

                // V3 publishes no journal name until the complete replacement
                // payload has been fsynced. Consequently every journal-bound
                // temporary is required to prove the exact intended bytes and
                // canonical next state before recovery gains unlink authority.
                // A pre-journal crash can leave an orphan temporary, but startup
                // deliberately does not guess or scan for such unbound names.
                if (!namespace_authority->
                        unlink_temporary_if_present_or_throw(
                            journal_fields.temporary_name,
                            "durable replay ledger recovery temporary retirement")) {
                    throw std::runtime_error(
                        "journal temporary file disappeared before retirement");
                }
                sync_directory("after recovery temporary retirement");
            };

        const bool next_state =
            payload_digest == journal_fields.payload_sha256;
        const bool previous_state =
            journal.version() ==
                persistence::LocalJsonlReplayJournalVersion::
                    crash_complete_v3 &&
            payload_digest == journal_fields.previous_payload_sha256;

        if (next_state) {
            require_next_state(summary, "committed ledger");
            retire_v3_temporary_if_present();
            if (!namespace_authority->unlink_journal_if_present_or_throw(
                    "durable replay ledger committed journal retirement")) {
                throw std::runtime_error(
                    "committed journal disappeared before retirement");
            }
            sync_directory("after committed journal retirement");
            ++journal_recovered_after_commit;
            return;
        }

        if (previous_state) {
            if (journal_fields.previous_line_count != summary.line_count ||
                journal_fields.previous_head != summary.head) {
                throw std::runtime_error(
                    "pre-commit journal does not match the previous ledger state");
            }
            retire_v3_temporary_if_present();
            if (!namespace_authority->unlink_journal_if_present_or_throw(
                    "durable replay ledger rollback journal retirement")) {
                throw std::runtime_error(
                    "pre-commit journal disappeared before rollback retirement");
            }
            sync_directory("after pre-commit journal rollback retirement");
            ++journal_rolled_back_before_commit;
            return;
        }

        if (journal.version() ==
            persistence::LocalJsonlReplayJournalVersion::legacy_v2) {
            throw std::runtime_error(
                "legacy v2 journal does not match the committed ledger payload");
        }
        throw std::runtime_error(
            "v3 journal matches neither the previous nor committed ledger payload");
    } catch (const std::exception& error) {
        ++journal_rejections;
        throw std::runtime_error(
            std::string("durable replay ledger dirty journal rejected: ") +
            error.what());
    }
}

bool ReplayLedger::durable_replace_lines(
    const std::vector<std::string>& next_lines,
    std::string& reason) {
    if (path.empty()) {
        reason = "durable replay ledger path is empty";
        return false;
    }
    if (!namespace_authority) {
        reason = "durable replay ledger namespace authority is absent";
        return false;
    }
    if (next_lines.empty()) {
        reason = "durable replay ledger refuses an empty replacement";
        return false;
    }
    if (next_lines.size() >
        persistence::kLocalJsonlReplayMaximumEntryCount) {
        reason =
            "durable replay ledger replacement exceeds entry-count budget";
        return false;
    }

    std::string payload;
    const std::uint64_t maximum_payload_bytes =
        persistence::kLocalJsonlReplayMaximumLedgerBytes;
    const std::uint64_t reserve_hint =
        canonical_payload_bytes >= maximum_payload_bytes
            ? maximum_payload_bytes
            : canonical_payload_bytes +
                  std::min<std::uint64_t>(
                      4096U,
                      maximum_payload_bytes - canonical_payload_bytes);
    payload.reserve(static_cast<std::size_t>(reserve_hint));
    for (const std::string& line : next_lines) {
        if (line.size() >
            persistence::kLocalJsonlReplayMaximumEntryJsonBytes) {
            reason = "durable replay ledger row exceeds byte budget";
            return false;
        }
        if (line.size() + 1U >
            persistence::kLocalJsonlReplayMaximumLedgerBytes -
                payload.size()) {
            reason =
                "durable replay ledger replacement exceeds byte budget";
            return false;
        }
        payload.append(line);
        payload.push_back('\n');
    }

    ValidatedLedgerPayload validated;
    try {
        validated = validate_ledger_payload_or_throw(payload);
    } catch (const std::exception& error) {
        reason = std::string(
                     "durable replay ledger refuses a noncanonical replacement: ") +
                 error.what();
        close();
        return false;
    }
    if (validated.canonical_lines.size() != next_lines.size()) {
        reason =
            "durable replay ledger replacement row count changed during validation";
        close();
        return false;
    }

    const std::string previous_head = durable_head_hash;
    const long long previous_line_count = durable_line_count;
    const std::string next_head = validated.summary.head;
    const std::string last_previous_hash =
        validated.summary.previous_head;
    const std::string next_payload_sha256 = sha256_hex(payload);
    std::string temporary_name;
    try {
        temporary_name = namespace_authority->make_temporary_name_or_throw(
            static_cast<std::int64_t>(::getpid()),
            validated.summary.line_count + 1U,
            "durable replay ledger temporary name");
        (void)namespace_authority->ledger_exists_or_throw(
            "durable replay ledger commit ledger");
        // The advisory lock coordinates cooperating AnonSync writers, but it
        // cannot prevent an unrelated process from replacing or rewriting the
        // ledger pathname. Refuse to publish a recovery witness for a previous
        // state that is no longer the exact state loaded by this authority.
        // This check deliberately precedes every journal/staging mutation.
        const std::string observed_durable_payload =
            namespace_authority->read_ledger_or_empty_or_throw(
                persistence::kLocalJsonlReplayMaximumLedgerBytes,
                "durable replay ledger commit stale-state recheck");
        if (sha256_hex(observed_durable_payload) != durable_payload_sha256) {
            reason =
                "durable replay ledger changed since load before commit witness publication";
            close();
            return false;
        }
        if (namespace_authority->journal_publication_state_or_throw(
                "durable replay ledger commit journal publication") !=
            persistence::LocalJsonlReplayJournalPublicationState::absent) {
            reason =
                "durable replay ledger refuses commit with unresolved journal publication residue";
            close();
            return false;
        }
        if (namespace_authority->temporary_exists_or_throw(
                temporary_name,
                "durable replay ledger commit temporary")) {
            reason =
                "durable replay ledger refuses an existing temporary name";
            close();
            return false;
        }
    } catch (const std::exception& error) {
        reason = error.what();
        close();
        return false;
    }

    auto sync_directory = [&](std::string_view phase) {
        ++directory_fsync_attempts;
        namespace_authority->fsync_directory_or_throw(phase);
    };

    try {
        // Materialize and fsync the complete replacement before publishing any
        // recovery witness. This deliberately trades automatic cleanup of an
        // unbound pre-journal orphan for a stronger authority law: once a v3
        // journal is visible, recovery can validate the exact temporary bytes
        // before unlinking that name on either side of the rename frontier.
        auto temporary =
            namespace_authority->create_temporary_exclusive_or_throw(
                temporary_name,
                "durable replay ledger temporary file");
        maybe_inject_crash("after-temp-create-before-write");
        temporary.write_all_or_throw(
            payload, "durable replay ledger temporary file");
        temporary.fsync_or_throw(
            "durable replay ledger temporary file");
        maybe_inject_crash("after-temp-fsync");

        if (!write_journal_record(
                previous_head, previous_line_count,
                durable_payload_sha256, next_head,
                static_cast<long long>(validated.summary.line_count),
                last_previous_hash, next_payload_sha256, temporary_name,
                reason)) {
            close();
            return false;
        }
        maybe_inject_crash(
            "after-journal-fsync-before-directory-fsync");
        sync_directory("after journal publication");
        maybe_inject_crash("after-journal-directory-fsync");
        // Retain the historical checkpoint spelling, but place it after the
        // new journal-directory durability barrier.
        maybe_inject_crash("after-journal-fsync");

        namespace_authority->rename_open_temporary_over_ledger_or_throw(
            temporary_name, temporary.descriptor(),
            "durable replay ledger replacement");
        temporary.close_or_throw(
            "durable replay ledger renamed file");
        ++atomic_rewrite_commits;
        maybe_inject_crash("after-rename-before-dir-fsync");

        sync_directory("after ledger rename");
        maybe_inject_crash(
            "after-dir-fsync-before-journal-unlink");

        if (!namespace_authority->unlink_journal_if_present_or_throw(
                "durable replay ledger journal retirement")) {
            throw std::runtime_error(
                "durable replay ledger journal disappeared before retirement");
        }
        maybe_inject_crash(
            "after-journal-unlink-before-directory-fsync");
        sync_directory("after journal retirement");
        maybe_inject_crash("after-journal-retirement-directory-fsync");

        durable_head_hash = next_head;
        durable_line_count = validated.summary.line_count;
        durable_payload_sha256 = next_payload_sha256;
        canonical_payload_bytes = payload.size();
        reason =
            "durable replay ledger backend commit retained-directory lock temp-fsync journal-fsync journal-directory-fsync rename ledger-directory-fsync journal-unlink journal-directory-fsync committed";
        return true;
    } catch (const ReplayLedgerFaultInjection&) {
        close();
        throw;
    } catch (const std::exception& error) {
        reason = error.what();
        close();
        return false;
    } catch (...) {
        close();
        throw;
    }
}

void ReplayLedger::load(const std::string& ledger_path,
                        const std::string& mode) {
    // Loading is a capability transition, not an in-place reconfiguration.
    // Expire any prior authority before validating or acquiring the next path.
    close();
    if (ledger_path.empty()) {
        path.clear();
        lock_path.clear();
        legacy_selected_path_spelling.clear();
        return;
    }
    if (mode != "immediate" && mode != "batch") {
        throw std::runtime_error("unsupported replay ledger commit mode: " +
                                 mode);
    }
    persistence::validate_local_jsonl_replay_ledger_path_or_throw(
        ledger_path);

    enabled = true;
    legacy_selected_path_spelling = ledger_path;
    path = ledger_path;
    commit_mode = mode;
    loaded_entries = 0;
    appended_entries = 0;
    atomic_rewrite_commits = 0;
    directory_fsync_attempts = 0;
    lock_acquire_attempts = 0;
    lock_contention_denials = 0;
    journal_records_written = 0;
    journal_recovered_after_commit = 0;
    journal_rolled_back_before_commit = 0;
    journal_rejections = 0;
    ledger_batch_flush_commits = 0;
    ledger_batch_pending_entries_peak = 0;
    batch_dirty = false;
    batch_pending_entries = 0;
    head_hash = "GENESIS";
    durable_head_hash = "GENESIS";
    durable_line_count = 0;
    durable_payload_sha256 = sha256_hex("");
    canonical_payload_bytes = 0;
    effect_transition_head_hash = "GENESIS";
    effect_transition_line_count = 0;
    effect_terminal_transitions = 0;
    effect_transition_rejections = 0;
    terminal_effect_states.clear();
    committed_jtis.clear();
    committed_event_identities.clear();
    committed_effect_idempotency_keys.clear();
    canonical_lines.clear();

    try {
        namespace_authority =
            std::make_unique<persistence::LocalJsonlReplayNamespace>(
                persistence::LocalJsonlReplayNamespace::open_or_throw(
                    path, "durable replay ledger namespace"));
        path = namespace_authority->absolute_ledger_path();
        lock_path = namespace_authority->absolute_lock_path();
        acquire_lock();
        recover_or_reject_journal();
        const std::string payload =
            namespace_authority->read_ledger_or_empty_or_throw(
                persistence::kLocalJsonlReplayMaximumLedgerBytes,
                "durable replay ledger");
        ValidatedLedgerPayload validated =
            validate_ledger_payload_or_throw(payload);

        loaded_entries = validated.summary.line_count;
        head_hash = validated.summary.head;
        durable_head_hash = validated.summary.head;
        durable_line_count = validated.summary.line_count;
        canonical_payload_bytes = payload.size();
        durable_payload_sha256 = sha256_hex(payload);
        canonical_lines = std::move(validated.canonical_lines);
        committed_jtis = std::move(validated.jtis);
        committed_event_identities =
            std::move(validated.event_identities);
        committed_effect_idempotency_keys =
            std::move(validated.effect_idempotency_keys);
    } catch (...) {
        // A rejected journal or chain must not leave a live lock-backed object
        // that a caller could accidentally continue using after the exception.
        close();
        throw;
    }
}

bool ReplayLedger::contains_jti(const std::string& jti) const {
    return enabled && committed_jtis.find(jti) != committed_jtis.end();
}

bool ReplayLedger::contains_event_identity(const std::string& cloud_event_source, const std::string& cloud_event_id) const {
    if (!enabled) return false;
    const std::string event_key = event_identity_key(cloud_event_source, cloud_event_id);
    return !event_key.empty() && committed_event_identities.find(event_key) != committed_event_identities.end();
}

bool ReplayLedger::contains_effect_idempotency_key(const std::string& effect_idempotency_key) const {
    return enabled && !effect_idempotency_key.empty() && committed_effect_idempotency_keys.find(effect_idempotency_key) != committed_effect_idempotency_keys.end();
}

bool ReplayLedger::append(const Json& tc, const Json& claims, const std::string& action, std::string& reason) {
    return stage(tc, claims, action, reason);
}

bool ReplayLedger::stage(const Json& tc,
                         const Json& claims,
                         const std::string& action,
                         std::string& reason) {
    if (!enabled) {
        if (!path.empty()) {
            reason = "durable replay ledger authority is closed";
            return false;
        }
        return true;
    }
    const auto maximum_exact_sequence =
        persistence::kLocalJsonlReplayMaximumExactJsonInteger;
    if (loaded_entries < 0 || appended_entries < 0 ||
        loaded_entries > maximum_exact_sequence ||
        appended_entries >= maximum_exact_sequence ||
        loaded_entries >
            maximum_exact_sequence - appended_entries - 1) {
        reason = "durable replay ledger sequence exceeds exact JSON range";
        return false;
    }
    if (canonical_lines.size() >=
        persistence::kLocalJsonlReplayMaximumEntryCount) {
        reason = "durable replay ledger entry-count budget is exhausted";
        return false;
    }

    const std::string jti = claims.at("jti").str();
    if (jti.empty()) {
        reason = "durable replay ledger append refused an empty jti";
        return false;
    }
    if (committed_jtis.find(jti) != committed_jtis.end()) {
        reason = "durable replay ledger already contains JWT jti";
        return false;
    }

    const std::int64_t sequence = loaded_entries + appended_entries + 1;
    const std::string kind = tc.at("kind").str();
    const std::string cloud_event_source =
        tc.at("cloud_event_source").str();
    const std::string cloud_event_id = tc.at("cloud_event_id").str();
    const std::string effect_idempotency_key =
        effect_idempotency_key_from_case_or_legacy(tc, claims);
    const std::string effect_state = effect_state_from_case_or_default(tc);
    if (committed_effect_idempotency_keys.find(effect_idempotency_key) !=
        committed_effect_idempotency_keys.end()) {
        reason =
            "durable replay ledger already contains prepared effect idempotency key";
        return false;
    }
    const std::string event_key =
        kind == "asyncapi"
            ? event_identity_key(cloud_event_source, cloud_event_id)
            : std::string();
    if (!event_key.empty() &&
        committed_event_identities.find(event_key) !=
            committed_event_identities.end()) {
        reason =
            "durable replay ledger already contains CloudEvents source/id identity";
        return false;
    }

    persistence::LocalJsonlReplayEntryFields fields;
    fields.sequence = sequence;
    fields.previous_hash = head_hash;
    fields.case_id = tc.at("case_id").str();
    fields.kind = kind;
    fields.operation_id = claims.at("operation_id").str();
    fields.contract_digest_sha256 =
        claims.at("contract_digest_sha256").str();
    fields.jti = jti;
    fields.action = action;
    fields.cloud_event_source = cloud_event_source;
    fields.cloud_event_id = cloud_event_id;
    fields.effect_idempotency_key = effect_idempotency_key;
    fields.effect_state = effect_state;

    std::optional<persistence::FrozenLocalJsonlReplayEntry> frozen;
    try {
        frozen.emplace(
            persistence::FrozenLocalJsonlReplayEntry::freeze_or_throw(
                std::move(fields)));
    } catch (const std::exception& error) {
        reason = std::string("durable replay ledger refuses entry: ") +
                 error.what();
        return false;
    }
    const std::string line =
        persistence::encode_local_jsonl_replay_entry_json_or_throw(*frozen);
    if (canonical_payload_bytes >
            persistence::kLocalJsonlReplayMaximumLedgerBytes ||
        line.size() + 1U >
            persistence::kLocalJsonlReplayMaximumLedgerBytes -
                canonical_payload_bytes) {
        reason = "durable replay ledger byte budget is exhausted";
        return false;
    }
    const std::uint64_t projected_payload_bytes =
        canonical_payload_bytes + line.size() + 1U;
    const std::string entry_hash = frozen->entry_hash();

    if (commit_mode == "batch") {
        // The parent copied the complete vector for every staged row, making a
        // batch of N rows perform O(N^2) line copies before its single write.
        // Ownership is already exclusive under the ledger lock, so append the
        // frozen canonical row directly and publish the vector only at commit.
        canonical_lines.push_back(line);
        canonical_payload_bytes = projected_payload_bytes;
        committed_jtis.insert(jti);
        if (!event_key.empty()) {
            committed_event_identities.insert(event_key);
        }
        committed_effect_idempotency_keys.insert(effect_idempotency_key);
        head_hash = entry_hash;
        ++appended_entries;
        batch_dirty = true;
        ++batch_pending_entries;
        ledger_batch_pending_entries_peak =
            std::max(ledger_batch_pending_entries_peak,
                     batch_pending_entries);
        reason =
            "durable replay ledger batch append staged hash-chain entry " +
            std::to_string(sequence) + " pending explicit batch flush";
        return true;
    }

    std::vector<std::string> next_lines = canonical_lines;
    next_lines.push_back(line);
    if (!durable_replace_lines(next_lines, reason)) return false;
    canonical_lines = std::move(next_lines);
    canonical_payload_bytes = projected_payload_bytes;
    committed_jtis.insert(jti);
    if (!event_key.empty()) committed_event_identities.insert(event_key);
    committed_effect_idempotency_keys.insert(effect_idempotency_key);
    head_hash = entry_hash;
    ++appended_entries;
    reason =
        "durable replay ledger append committed hash-chain entry " +
        std::to_string(sequence) +
        " via locked temp-write fsync write-ahead-journal fsync rename directory-fsync journal-unlink";
    return true;
}

bool ReplayLedger::flush(std::string& reason) {
    return commit(reason);
}

bool ReplayLedger::commit(std::string& reason) {
    if (!enabled) {
        if (!path.empty()) {
            reason = "durable replay ledger authority is closed";
            return false;
        }
        return true;
    }
    if (commit_mode != "batch") { reason = "durable replay ledger immediate mode does not require batch flush"; return true; }
    if (!batch_dirty) { reason = "durable replay ledger batch mode has no pending entries"; return true; }
    if (!durable_replace_lines(canonical_lines, reason)) return false;
    ledger_batch_flush_commits++;
    batch_dirty = false;
    batch_pending_entries = 0;
    reason = "durable replay ledger batch flush committed staged hash-chain entries with one atomic replacement";
    return true;
}

bool ReplayLedger::backup_snapshot(const std::string& snapshot_path, std::string& reason) {
    if (snapshot_path.empty()) return true;
    reason = "local-jsonl replay ledger does not support SQLite backup snapshots";
    return false;
}

void ReplayLedger::recover() {
    if (!enabled) return;
    try {
        recover_or_reject_journal();
    } catch (...) {
        close();
        throw;
    }
}

void ReplayLedger::close() {
    // Stop accepting transitions first, release the process-bound flock, and
    // finally expire the retained directory authority. No pathname operation
    // is permitted after the capability owner has been destroyed.
    enabled = false;
    release_lock();
    namespace_authority.reset();
}

}  // namespace anonsync
