#include "mtgsim/engine.hpp"

#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr std::uint64_t kDemoSeed = 0xC0FFEEULL;

void print_usage(std::ostream& out) {
    out << "MTGSim deterministic rules-kernel demo\n"
        << "usage:\n"
        << "  mtgsim_cli --demo\n"
        << "  mtgsim_cli --write-demo-replay SNAPSHOT TRACE\n"
        << "  mtgsim_cli --write-paid-action-journal-demo JOURNAL\n"
        << "  mtgsim_cli --verify-paid-action-journal JOURNAL\n"
        << "  mtgsim_cli --paid-action-journal-roundtrip JOURNAL\n"
        << "  mtgsim_cli --verify-replay SNAPSHOT TRACE\n"
        << "  mtgsim_cli --artifact-roundtrip SNAPSHOT TRACE\n"
        << "  mtgsim_cli --write-demo-replay-bundle SNAPSHOT TRACE MANIFEST\n"
        << "  mtgsim_cli --verify-replay-bundle SNAPSHOT TRACE MANIFEST\n"
        << "  mtgsim_cli --write-paid-replay-bundle-demo SNAPSHOT TRACE JOURNAL MANIFEST\n"
        << "  mtgsim_cli --verify-paid-replay-bundle SNAPSHOT TRACE JOURNAL MANIFEST\n"
        << "  mtgsim_cli --paid-replay-bundle-roundtrip SNAPSHOT TRACE JOURNAL MANIFEST\n"
        << "  mtgsim_cli --inspect-replay-bundle SNAPSHOT TRACE MANIFEST\n"
        << "  mtgsim_cli --write-replay-prefix SNAPSHOT TRACE MANIFEST PREFIX_TRACE PREFIX_MANIFEST\n"
        << "  mtgsim_cli --write-replay-resume-probe SNAPSHOT TRACE MANIFEST RESUME_SNAPSHOT SUFFIX_TRACE SUFFIX_MANIFEST\n"
        << "  mtgsim_cli --artifact-bundle-roundtrip SNAPSHOT TRACE MANIFEST\n"
        << "  mtgsim_cli --artifact-bundle-inspect-roundtrip SNAPSHOT TRACE MANIFEST\n"
        << "  mtgsim_cli --artifact-bundle-prefix-roundtrip SNAPSHOT TRACE MANIFEST PREFIX_TRACE PREFIX_MANIFEST\n"
        << "  mtgsim_cli --artifact-bundle-resume-roundtrip SNAPSHOT TRACE MANIFEST RESUME_SNAPSHOT SUFFIX_TRACE SUFFIX_MANIFEST\n";
}

[[nodiscard]] const char* replay_failure_name(mtgsim::ActionReplayFailureKind kind) noexcept {
    switch (kind) {
        case mtgsim::ActionReplayFailureKind::None: return "none";
        case mtgsim::ActionReplayFailureKind::CheckpointSchemaMismatch: return "checkpoint_schema_mismatch";
        case mtgsim::ActionReplayFailureKind::CheckpointHashMismatch: return "checkpoint_hash_mismatch";
        case mtgsim::ActionReplayFailureKind::ChoiceQueueHashMismatch: return "choice_queue_hash_mismatch";
        case mtgsim::ActionReplayFailureKind::ChoiceRequestHashMismatch: return "choice_request_hash_mismatch";
        case mtgsim::ActionReplayFailureKind::ChoiceValidationSourceMismatch: return "choice_validation_source_mismatch";
        case mtgsim::ActionReplayFailureKind::ChoicePageLocationMismatch: return "choice_page_location_mismatch";
        case mtgsim::ActionReplayFailureKind::ActionHashMismatch: return "action_hash_mismatch";
        case mtgsim::ActionReplayFailureKind::StateHashSchemaMismatch: return "state_hash_schema_mismatch";
        case mtgsim::ActionReplayFailureKind::StateHashBeforeMismatch: return "state_hash_before_mismatch";
        case mtgsim::ActionReplayFailureKind::ApplyResultMismatch: return "apply_result_mismatch";
        case mtgsim::ActionReplayFailureKind::StateHashAfterMismatch: return "state_hash_after_mismatch";
        case mtgsim::ActionReplayFailureKind::Count: return "count";
    }
    return "unknown";
}


[[nodiscard]] const char* paid_action_journal_failure_name(mtgsim::PaidActionTransactionJournalVerifyFailureKind kind) noexcept {
    switch (kind) {
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::None: return "none";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::ParseFailed: return "parse_failed";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::UnsupportedSchema: return "unsupported_schema";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::RecordCountMismatch: return "record_count_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::RecordSequenceMismatch: return "record_sequence_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::TransactionHashMismatch: return "transaction_hash_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::ExportedTransactionHashMismatch: return "exported_transaction_hash_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::SnapshotPresenceMismatch: return "snapshot_presence_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::CommittedSnapshotHashMismatch: return "committed_snapshot_hash_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::SpeculativeSnapshotHashMismatch: return "speculative_snapshot_hash_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::OutcomeFlagMismatch: return "outcome_flag_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::StateBindingMismatch: return "state_binding_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::RecordPayloadHashMismatch: return "record_payload_hash_mismatch";
        case mtgsim::PaidActionTransactionJournalVerifyFailureKind::Count: return "count";
    }
    return "unknown";
}

[[nodiscard]] const char* replay_artifact_failure_name(mtgsim::ReplayArtifactFailureKind kind) noexcept {
    switch (kind) {
        case mtgsim::ReplayArtifactFailureKind::None: return "none";
        case mtgsim::ReplayArtifactFailureKind::UnsupportedFormat: return "unsupported_format";
        case mtgsim::ReplayArtifactFailureKind::ManifestSchemaMismatch: return "manifest_schema_mismatch";
        case mtgsim::ReplayArtifactFailureKind::ManifestBundleHashMismatch: return "manifest_bundle_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::SnapshotTextHashMismatch: return "snapshot_text_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::TraceTextHashMismatch: return "trace_text_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::SnapshotParseFailed: return "snapshot_parse_failed";
        case mtgsim::ReplayArtifactFailureKind::CheckpointSealMismatch: return "checkpoint_seal_mismatch";
        case mtgsim::ReplayArtifactFailureKind::TraceParseFailed: return "trace_parse_failed";
        case mtgsim::ReplayArtifactFailureKind::ActionCountMismatch: return "action_count_mismatch";
        case mtgsim::ReplayArtifactFailureKind::TraceReplayFailed: return "trace_replay_failed";
        case mtgsim::ReplayArtifactFailureKind::FinalStateHashMismatch: return "final_state_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalMissing: return "paid_action_journal_missing";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalTextHashMismatch: return "paid_action_journal_text_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalVerifyFailed: return "paid_action_journal_verify_failed";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalRecordCountMismatch: return "paid_action_journal_record_count_mismatch";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalStateHashMismatch: return "paid_action_journal_state_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalHashMismatch: return "paid_action_journal_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::PaidActionJournalPayloadHashMismatch: return "paid_action_journal_payload_hash_mismatch";
        case mtgsim::ReplayArtifactFailureKind::Count: return "count";
    }
    return "unknown";
}

[[nodiscard]] mtgsim::GameState make_demo_game() {
    std::vector<mtgsim::CardDefinition> defs = {
        {"Sample Creature", mtgsim::TypeCreature, 2, 2},
        {"Sample Instant", mtgsim::TypeInstant, 0, 0}
    };
    std::vector<mtgsim::PlayerDeck> decks = {
        {"Ada", std::vector<mtgsim::u32>(4, 0)},
        {"Babbage", std::vector<mtgsim::u32>(4, 1)}
    };
    auto game = mtgsim::make_game(std::move(defs), decks, kDemoSeed);
    mtgsim::StartOptions options;
    options.opening_hand_size = 0;
    options.shuffle_libraries = false;
    mtgsim::start_game(game, options);
    return game;
}

[[nodiscard]] bool apply_demo_actions(mtgsim::GameState& game, std::ostream& err) {
    for (int i = 0; i < 4; ++i) {
        mtgsim::LegalAction pass{};
        pass.kind = mtgsim::ActionKind::PassPriority;
        pass.player = game.priority_player;
        if (!mtgsim::apply_action(game, pass)) {
            err << "demo action " << (i + 1) << " failed to apply\n";
            return false;
        }
    }
    return true;
}

[[nodiscard]] mtgsim::GameState make_paid_action_journal_demo_game() {
    mtgsim::CardDefinition forest;
    forest.name = "Journal Forest";
    forest.type_mask = mtgsim::TypeLand;
    forest.taps_for_mana = true;
    forest.tap_mana_symbol = mtgsim::ManaSymbol::Green;

    mtgsim::CardDefinition bear;
    bear.name = "Journal Bear";
    bear.type_mask = mtgsim::TypeCreature;
    bear.printed_power = 2;
    bear.printed_toughness = 2;
    bear.mana_cost.generic = 1;
    bear.mana_cost.green = 1;

    std::vector<mtgsim::CardDefinition> defs = {forest, bear};
    std::vector<mtgsim::PlayerDeck> decks = {
        {"Ada", {0, 1}},
        {"Babbage", {0, 0}}
    };
    auto game = mtgsim::make_game(std::move(defs), decks, kDemoSeed ^ 0x6012fULL);
    mtgsim::StartOptions options;
    options.opening_hand_size = 0;
    options.shuffle_libraries = false;
    mtgsim::start_game(game, options);
    game.active_player = mtgsim::PlayerId{1};
    game.priority_player = mtgsim::PlayerId{1};
    game.step = mtgsim::Step::Main1;
    game.consecutive_priority_passes = 0;
    return game;
}

[[nodiscard]] bool apply_paid_action_journal_demo(mtgsim::GameState& game, std::ostream& err) {
    mtgsim::draw_card(game, mtgsim::PlayerId{1});
    const auto& hand = mtgsim::zone(game, mtgsim::PlayerId{1}, mtgsim::Zone::Hand);
    if (hand.empty()) {
        err << "paid-action journal demo did not draw a spell\n";
        return false;
    }
    const auto spell = hand.back();
    const auto& library = mtgsim::zone(game, mtgsim::PlayerId{1}, mtgsim::Zone::Library);
    if (library.empty()) {
        err << "paid-action journal demo has no land to move\n";
        return false;
    }
    const auto forest = library.back();
    mtgsim::move_object(game, forest, mtgsim::PlayerId{1}, mtgsim::Zone::Battlefield);
    mtgsim::tap_permanent_for_mana(game, mtgsim::PlayerId{1}, forest);
    mtgsim::add_mana(game, mtgsim::PlayerId{1}, mtgsim::ManaSymbol::Colorless);
    if (!mtgsim::cast_from_hand_to_stack_paying_mana(game, mtgsim::PlayerId{1}, spell)) {
        err << "paid-action journal demo failed to cast the paid spell\n";
        return false;
    }
    return true;
}

[[nodiscard]] bool write_text_file(const std::string& path, const std::string& text, std::ostream& err) {
    std::ofstream out(path, std::ios::binary);
    if (!out) {
        err << "could not open for write: " << path << "\n";
        return false;
    }
    out << text;
    if (!out) {
        err << "failed while writing: " << path << "\n";
        return false;
    }
    return true;
}

[[nodiscard]] bool read_text_file(const std::string& path, std::string& text, std::ostream& err) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        err << "could not open for read: " << path << "\n";
        return false;
    }
    std::ostringstream buffer;
    buffer << in.rdbuf();
    if (!in.good() && !in.eof()) {
        err << "failed while reading: " << path << "\n";
        return false;
    }
    text = buffer.str();
    return true;
}

[[nodiscard]] int write_paid_action_journal_demo_artifact(const std::string& journal_path, std::ostream& out, std::ostream& err) {
    auto game = make_paid_action_journal_demo_game();
    if (!apply_paid_action_journal_demo(game, err)) {
        return 3;
    }

    const auto journal_text = mtgsim::serialize_paid_action_transaction_journal(game);
    if (!write_text_file(journal_path, journal_text, err)) {
        return 2;
    }

    out << "wrote paid-action transaction journal"
        << " journal=" << journal_path
        << " records=" << mtgsim::paid_action_transaction_record_count(game)
        << " text_hash=" << mtgsim::paid_action_transaction_journal_text_hash(journal_text)
        << " state_hash=" << mtgsim::canonical_state_hash(game)
        << " journal_hash=" << mtgsim::journal_hash(game)
        << "\n";
    return 0;
}

[[nodiscard]] int verify_paid_action_journal_artifact(const std::string& journal_path, std::ostream& out, std::ostream& err) {
    std::string journal_text;
    if (!read_text_file(journal_path, journal_text, err)) {
        return 2;
    }

    const auto result = mtgsim::verify_paid_action_transaction_journal(journal_text);
    if (!result.ok) {
        err << "paid-action journal verification failed failure=" << paid_action_journal_failure_name(result.failure)
            << " error=" << result.error
            << " line=" << result.error_line
            << " record=" << result.record_index
            << " expected=" << result.expected
            << " actual=" << result.actual
            << " text_hash=" << result.text_hash
            << "\n";
        return 4;
    }

    out << "paid-action journal ok"
        << " records=" << result.parse.journal.records.size()
        << " text_hash=" << result.text_hash
        << " state_hash=" << result.parse.journal.header.state_hash
        << " journal_hash=" << result.parse.journal.header.journal_hash
        << " record_payload_hash=" << result.parse.journal.header.record_payload_hash
        << " first_sequence=" << result.parse.journal.header.first_transaction_sequence
        << " last_sequence=" << result.parse.journal.header.last_transaction_sequence
        << " declarations=" << result.parse.journal.header.declaration_record_count
        << " stack_placements=" << result.parse.journal.header.stack_placement_record_count
        << "\n";
    return 0;
}

[[nodiscard]] int write_demo_replay_artifacts(const std::string& snapshot_path, const std::string& trace_path, std::ostream& out, std::ostream& err) {
    const auto checkpoint = make_demo_game();
    auto traced = checkpoint;
    if (!apply_demo_actions(traced, err)) {
        return 3;
    }

    const auto snapshot_text = mtgsim::serialize_state_core_snapshot(checkpoint);
    const auto trace = mtgsim::export_action_trace(traced);
    const auto trace_text = mtgsim::serialize_action_trace(trace);
    if (!write_text_file(snapshot_path, snapshot_text, err) || !write_text_file(trace_path, trace_text, err)) {
        return 2;
    }

    out << "wrote replay artifacts"
        << " snapshot=" << snapshot_path
        << " trace=" << trace_path
        << " actions=" << trace.size()
        << " checkpoint_state_hash=" << mtgsim::canonical_state_hash(checkpoint)
        << " final_state_hash=" << mtgsim::canonical_state_hash(traced)
        << "\n";
    return 0;
}

[[nodiscard]] int verify_replay_artifacts(const std::string& snapshot_path, const std::string& trace_path, std::ostream& out, std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) || !read_text_file(trace_path, trace_text, err)) {
        return 2;
    }

    const auto snapshot = mtgsim::parse_state_core_snapshot(snapshot_text);
    if (!snapshot.ok) {
        err << "snapshot parse failed line=" << snapshot.error_line << " error=" << snapshot.error << "\n";
        return 3;
    }
    const auto trace = mtgsim::parse_action_trace(trace_text);
    if (!trace.ok) {
        err << "trace parse failed line=" << trace.error_line << " error=" << trace.error << "\n";
        return 4;
    }

    auto replay = snapshot.game;
    const auto result = mtgsim::replay_action_trace(replay, trace.trace);
    if (!result.ok) {
        err << "replay failed failure=" << replay_failure_name(result.failure)
            << " mismatch_index=" << result.mismatch_index
            << " attempted=" << result.attempted
            << " expected_state_hash=" << result.expected_state_hash
            << " actual_state_hash=" << result.actual_state_hash
            << " expected_action_hash=" << result.expected_action_hash
            << " actual_action_hash=" << result.actual_action_hash
            << " expected_choice_hash=" << result.expected_choice_request_hash
            << " actual_choice_hash=" << result.actual_choice_request_hash
            << " expected_choice_count=" << result.expected_choice_action_count
            << " actual_choice_count=" << result.actual_choice_action_count
            << " expected_choice_kind=" << mtgsim::to_string(result.expected_choice_kind)
            << " actual_choice_kind=" << mtgsim::to_string(result.actual_choice_kind)
            << " expected_applied=" << (result.expected_applied ? 1 : 0)
            << " actual_applied=" << (result.actual_applied ? 1 : 0)
            << "\n";
        return 5;
    }

    out << "replay ok"
        << " actions=" << trace.trace.size()
        << " attempted=" << result.attempted
        << " applied=" << result.applied
        << " checkpoint_state_hash=" << snapshot.source_checkpoint.state_hash
        << " replay_start_state_hash=" << mtgsim::canonical_state_hash(snapshot.game)
        << " final_state_hash=" << mtgsim::canonical_state_hash(replay)
        << " source_journal_entries=" << snapshot.source_checkpoint.journal_entries
        << " replay_journal_entries=" << mtgsim::journal_entry_count(replay)
        << "\n";
    return 0;
}

[[nodiscard]] int write_demo_replay_bundle_artifacts(const std::string& snapshot_path,
                                                     const std::string& trace_path,
                                                     const std::string& manifest_path,
                                                     std::ostream& out,
                                                     std::ostream& err) {
    const auto checkpoint = make_demo_game();
    auto traced = checkpoint;
    if (!apply_demo_actions(traced, err)) {
        return 3;
    }

    const auto snapshot_text = mtgsim::serialize_state_core_snapshot(checkpoint);
    const auto trace = mtgsim::export_action_trace(traced);
    const auto trace_text = mtgsim::serialize_action_trace(trace);
    const auto manifest = mtgsim::make_replay_artifact_manifest(snapshot_text, trace_text, traced);
    const auto manifest_text = mtgsim::serialize_replay_artifact_manifest(manifest);
    if (!write_text_file(snapshot_path, snapshot_text, err) ||
        !write_text_file(trace_path, trace_text, err) ||
        !write_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    out << "wrote replay bundle"
        << " snapshot=" << snapshot_path
        << " trace=" << trace_path
        << " manifest=" << manifest_path
        << " actions=" << trace.size()
        << " manifest_schema=" << manifest.schema_version
        << " snapshot_hash=" << manifest.snapshot_text_hash
        << " trace_hash=" << manifest.trace_text_hash
        << " checkpoint_state_hash=" << manifest.checkpoint_state_hash
        << " final_state_hash=" << manifest.final_state_hash
        << " bundle_hash=" << manifest.bundle_hash
        << "\n";
    return 0;
}

[[nodiscard]] int write_demo_paid_replay_bundle_artifacts(const std::string& snapshot_path,
                                                           const std::string& trace_path,
                                                           const std::string& journal_path,
                                                           const std::string& manifest_path,
                                                           std::ostream& out,
                                                           std::ostream& err) {
    auto setup = make_paid_action_journal_demo_game();
    mtgsim::draw_card(setup, mtgsim::PlayerId{1});
    const auto& hand = mtgsim::zone(setup, mtgsim::PlayerId{1}, mtgsim::Zone::Hand);
    if (hand.empty()) {
        err << "paid replay bundle demo did not draw a spell\n";
        return 3;
    }
    const auto spell = hand.back();
    const auto& library = mtgsim::zone(setup, mtgsim::PlayerId{1}, mtgsim::Zone::Library);
    if (library.empty()) {
        err << "paid replay bundle demo has no land to move\n";
        return 3;
    }
    const auto forest = library.back();
    mtgsim::move_object(setup, forest, mtgsim::PlayerId{1}, mtgsim::Zone::Battlefield);
    mtgsim::add_mana(setup, mtgsim::PlayerId{1}, mtgsim::ManaSymbol::Colorless);

    auto traced = mtgsim::make_branch_state(setup, mtgsim::JournalRetention::ClearAll);
    const auto snapshot_text = mtgsim::serialize_state_core_snapshot(traced);

    mtgsim::LegalAction tap_action{};
    tap_action.kind = mtgsim::ActionKind::ActivateTapManaAbility;
    tap_action.player = mtgsim::PlayerId{1};
    tap_action.object = forest;
    tap_action.label = "tap forest";
    if (!mtgsim::apply_action(traced, tap_action)) {
        err << "paid replay bundle demo failed to activate tap mana ability\n";
        return 4;
    }

    mtgsim::LegalAction cast_action{};
    cast_action.kind = mtgsim::ActionKind::CastSpellFromHandPaid;
    cast_action.player = mtgsim::PlayerId{1};
    cast_action.object = spell;
    cast_action.label = "cast paid spell";
    if (!mtgsim::apply_action(traced, cast_action)) {
        err << "paid replay bundle demo failed to cast paid spell through the action surface\n";
        return 4;
    }

    const auto trace_text = mtgsim::serialize_action_trace(mtgsim::export_action_trace(traced));
    const auto journal_text = mtgsim::serialize_paid_action_transaction_journal(traced);
    const auto journal_verify = mtgsim::verify_paid_action_transaction_journal_for_state(traced, journal_text);
    if (!journal_verify.ok) {
        err << "generated paid-action journal failed state-bound verification failure="
            << paid_action_journal_failure_name(journal_verify.failure)
            << " error=" << journal_verify.error << "\n";
        return 5;
    }
    const auto manifest = mtgsim::make_replay_artifact_manifest_with_paid_action_journal(snapshot_text, trace_text, traced, journal_text);
    const auto manifest_text = mtgsim::serialize_replay_artifact_manifest(manifest);

    if (!write_text_file(snapshot_path, snapshot_text, err) ||
        !write_text_file(trace_path, trace_text, err) ||
        !write_text_file(journal_path, journal_text, err) ||
        !write_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    out << "wrote paid replay bundle"
        << " snapshot=" << snapshot_path
        << " trace=" << trace_path
        << " journal=" << journal_path
        << " manifest=" << manifest_path
        << " actions=" << manifest.action_count
        << " manifest_schema=" << manifest.schema_version
        << " paid_action_journal_attached=" << (manifest.paid_action_journal_attached ? 1 : 0)
        << " paid_action_journal_text_hash=" << manifest.paid_action_journal_text_hash
        << " paid_action_journal_records=" << manifest.paid_action_journal_record_count
        << " final_state_hash=" << manifest.final_state_hash
        << " bundle_hash=" << manifest.bundle_hash
        << "\n";
    return 0;
}

[[nodiscard]] int verify_replay_bundle_artifacts(const std::string& snapshot_path,
                                                 const std::string& trace_path,
                                                 const std::string& manifest_path,
                                                 std::ostream& out,
                                                 std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    std::string manifest_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) ||
        !read_text_file(trace_path, trace_text, err) ||
        !read_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    const auto manifest = mtgsim::parse_replay_artifact_manifest(manifest_text);
    if (!manifest.ok) {
        err << "manifest parse failed line=" << manifest.error_line << " error=" << manifest.error << "\n";
        return 3;
    }

    const auto result = mtgsim::verify_replay_artifact_bundle(snapshot_text, trace_text, manifest.manifest);
    if (!result.ok) {
        err << "bundle verification failed failure=" << replay_artifact_failure_name(result.failure)
            << " error=" << result.error
            << " line=" << result.error_line
            << " expected_snapshot_hash=" << result.expected_snapshot_text_hash
            << " actual_snapshot_hash=" << result.actual_snapshot_text_hash
            << " expected_trace_hash=" << result.expected_trace_text_hash
            << " actual_trace_hash=" << result.actual_trace_text_hash
            << " expected_checkpoint_state_hash=" << result.expected_checkpoint_state_hash
            << " actual_checkpoint_state_hash=" << result.actual_checkpoint_state_hash
            << " expected_checkpoint_journal_hash=" << result.expected_checkpoint_journal_hash
            << " actual_checkpoint_journal_hash=" << result.actual_checkpoint_journal_hash
            << " expected_checkpoint_journal_entries=" << result.expected_checkpoint_journal_entries
            << " actual_checkpoint_journal_entries=" << result.actual_checkpoint_journal_entries
            << " expected_action_count=" << result.expected_action_count
            << " actual_action_count=" << result.actual_action_count
            << " expected_final_state_hash=" << result.expected_final_state_hash
            << " actual_final_state_hash=" << result.actual_final_state_hash
            << " replay_failure=" << replay_failure_name(result.replay.failure)
            << " replay_mismatch_index=" << result.replay.mismatch_index
            << "\n";
        return 4;
    }

    out << "replay bundle ok"
        << " actions=" << result.action_count
        << " attempted=" << result.replay.attempted
        << " applied=" << result.replay.applied
        << " manifest_schema=" << manifest.manifest.schema_version
        << " snapshot_hash=" << result.actual_snapshot_text_hash
        << " trace_hash=" << result.actual_trace_text_hash
        << " checkpoint_state_hash=" << manifest.manifest.checkpoint_state_hash
        << " final_state_hash=" << result.actual_final_state_hash
        << " bundle_hash=" << manifest.manifest.bundle_hash
        << "\n";
    return 0;
}


[[nodiscard]] int verify_paid_replay_bundle_artifacts(const std::string& snapshot_path,
                                                      const std::string& trace_path,
                                                      const std::string& journal_path,
                                                      const std::string& manifest_path,
                                                      std::ostream& out,
                                                      std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    std::string journal_text;
    std::string manifest_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) ||
        !read_text_file(trace_path, trace_text, err) ||
        !read_text_file(journal_path, journal_text, err) ||
        !read_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    const auto manifest = mtgsim::parse_replay_artifact_manifest(manifest_text);
    if (!manifest.ok) {
        err << "manifest parse failed line=" << manifest.error_line << " error=" << manifest.error << "\n";
        return 3;
    }

    const auto result = mtgsim::verify_replay_artifact_bundle_with_paid_action_journal(snapshot_text, trace_text, journal_text, manifest.manifest);
    if (!result.ok) {
        err << "paid replay bundle verification failed failure=" << replay_artifact_failure_name(result.failure)
            << " error=" << result.error
            << " line=" << result.error_line
            << " expected_paid_action_journal_text_hash=" << result.expected_paid_action_journal_text_hash
            << " actual_paid_action_journal_text_hash=" << result.actual_paid_action_journal_text_hash
            << " expected_paid_action_journal_records=" << result.expected_paid_action_journal_record_count
            << " actual_paid_action_journal_records=" << result.actual_paid_action_journal_record_count
            << " expected_paid_action_journal_state_hash=" << result.expected_paid_action_journal_state_hash
            << " actual_paid_action_journal_state_hash=" << result.actual_paid_action_journal_state_hash
            << " expected_paid_action_journal_journal_hash=" << result.expected_paid_action_journal_journal_hash
            << " actual_paid_action_journal_journal_hash=" << result.actual_paid_action_journal_journal_hash
            << " expected_paid_action_journal_payload_hash=" << result.expected_paid_action_journal_record_payload_hash
            << " actual_paid_action_journal_payload_hash=" << result.actual_paid_action_journal_record_payload_hash
            << " paid_action_journal_failure=" << paid_action_journal_failure_name(result.paid_action_journal_verify.failure)
            << " replay_failure=" << replay_failure_name(result.replay.failure)
            << " replay_mismatch_index=" << result.replay.mismatch_index
            << "\n";
        return 4;
    }

    out << "paid replay bundle ok"
        << " actions=" << result.action_count
        << " attempted=" << result.replay.attempted
        << " applied=" << result.replay.applied
        << " manifest_schema=" << manifest.manifest.schema_version
        << " paid_action_journal_attached=" << (manifest.manifest.paid_action_journal_attached ? 1 : 0)
        << " paid_action_journal_text_hash=" << result.actual_paid_action_journal_text_hash
        << " paid_action_journal_records=" << result.actual_paid_action_journal_record_count
        << " paid_action_journal_state_hash=" << result.actual_paid_action_journal_state_hash
        << " paid_action_journal_journal_hash=" << result.actual_paid_action_journal_journal_hash
        << " paid_action_journal_payload_hash=" << result.actual_paid_action_journal_record_payload_hash
        << " final_state_hash=" << result.actual_final_state_hash
        << " bundle_hash=" << manifest.manifest.bundle_hash
        << "\n";
    return 0;
}

[[nodiscard]] int inspect_replay_bundle_artifacts(const std::string& snapshot_path,
                                                  const std::string& trace_path,
                                                  const std::string& manifest_path,
                                                  std::ostream& out,
                                                  std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    std::string manifest_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) ||
        !read_text_file(trace_path, trace_text, err) ||
        !read_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    out << "replay bundle inspection"
        << " snapshot=" << snapshot_path
        << " trace=" << trace_path
        << " manifest=" << manifest_path
        << " snapshot_bytes=" << snapshot_text.size()
        << " trace_bytes=" << trace_text.size()
        << " manifest_bytes=" << manifest_text.size()
        << " actual_snapshot_hash=" << mtgsim::replay_artifact_text_hash(snapshot_text)
        << " actual_trace_hash=" << mtgsim::replay_artifact_text_hash(trace_text)
        << "\n";

    const auto snapshot = mtgsim::parse_state_core_snapshot(snapshot_text);
    out << "snapshot_parse_ok=" << (snapshot.ok ? 1 : 0);
    if (snapshot.ok) {
        out << " checkpoint_state_hash=" << snapshot.source_checkpoint.state_hash
            << " checkpoint_journal_hash=" << snapshot.source_checkpoint.journal_hash
            << " checkpoint_journal_entries=" << snapshot.source_checkpoint.journal_entries
            << " reconstructed_state_hash=" << mtgsim::canonical_state_hash(snapshot.game)
            << " reconstructed_journal_entries=" << mtgsim::journal_entry_count(snapshot.game);
    } else {
        out << " snapshot_error_line=" << snapshot.error_line
            << " snapshot_error=" << snapshot.error;
    }
    out << "\n";

    const auto trace = mtgsim::parse_action_trace(trace_text);
    out << "trace_parse_ok=" << (trace.ok ? 1 : 0);
    if (trace.ok) {
        out << " actions=" << trace.trace.size();
        if (!trace.trace.empty()) {
            out << " first_action_hash=" << trace.trace.front().expected_action_hash
                << " first_state_before=" << trace.trace.front().expected_state_hash_before
                << " last_state_after=" << trace.trace.back().expected_state_hash_after;
        }
    } else {
        out << " trace_error_line=" << trace.error_line
            << " trace_error=" << trace.error;
    }
    out << "\n";

    const auto manifest = mtgsim::parse_replay_artifact_manifest(manifest_text);
    out << "manifest_parse_ok=" << (manifest.ok ? 1 : 0);
    if (!manifest.ok) {
        out << " manifest_error_line=" << manifest.error_line
            << " manifest_error=" << manifest.error << "\n";
        return 3;
    }

    out << " expected_manifest_schema=" << manifest.manifest.schema_version
        << " actual_manifest_schema=" << mtgsim::kReplayArtifactManifestSchemaVersion
        << " expected_snapshot_hash=" << manifest.manifest.snapshot_text_hash
        << " expected_trace_hash=" << manifest.manifest.trace_text_hash
        << " expected_checkpoint_state_hash=" << manifest.manifest.checkpoint_state_hash
        << " expected_checkpoint_journal_hash=" << manifest.manifest.checkpoint_journal_hash
        << " expected_checkpoint_journal_entries=" << manifest.manifest.checkpoint_journal_entries
        << " expected_action_count=" << manifest.manifest.action_count
        << " expected_final_state_hash=" << manifest.manifest.final_state_hash
        << " paid_action_journal_attached=" << (manifest.manifest.paid_action_journal_attached ? 1 : 0)
        << " paid_action_journal_format=" << manifest.manifest.paid_action_journal_format
        << " paid_action_journal_text_hash=" << manifest.manifest.paid_action_journal_text_hash
        << " paid_action_journal_records=" << manifest.manifest.paid_action_journal_record_count
        << " bundle_hash=" << manifest.manifest.bundle_hash
        << "\n";

    const auto verify = mtgsim::verify_replay_artifact_bundle(snapshot_text, trace_text, manifest.manifest);
    out << "verification_ok=" << (verify.ok ? 1 : 0)
        << " failure=" << replay_artifact_failure_name(verify.failure)
        << " error=" << verify.error
        << " line=" << verify.error_line
        << " expected_action_count=" << verify.expected_action_count
        << " actual_action_count=" << verify.actual_action_count
        << " expected_final_state_hash=" << verify.expected_final_state_hash
        << " actual_final_state_hash=" << verify.actual_final_state_hash
        << " replay_failure=" << replay_failure_name(verify.replay.failure)
        << " replay_mismatch_index=" << verify.replay.mismatch_index
        << "\n";
    return verify.ok ? 0 : 4;
}

[[nodiscard]] int write_replay_prefix_artifacts(const std::string& snapshot_path,
                                                const std::string& trace_path,
                                                const std::string& manifest_path,
                                                const std::string& prefix_trace_path,
                                                const std::string& prefix_manifest_path,
                                                std::ostream& out,
                                                std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    std::string manifest_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) ||
        !read_text_file(trace_path, trace_text, err) ||
        !read_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    const auto manifest = mtgsim::parse_replay_artifact_manifest(manifest_text);
    if (!manifest.ok) {
        err << "manifest parse failed line=" << manifest.error_line << " error=" << manifest.error << "\n";
        return 3;
    }

    const auto prefix = mtgsim::make_replay_artifact_prefix_bundle(snapshot_text, trace_text, manifest.manifest);
    if (!prefix.ok) {
        err << "prefix generation failed failure=" << replay_artifact_failure_name(prefix.source_failure)
            << " error=" << prefix.error
            << " source_error=" << prefix.source_verify.error
            << " replay_mismatch_index=" << prefix.source_verify.replay.mismatch_index
            << "\n";
        return 4;
    }

    const auto prefix_verify = mtgsim::verify_replay_artifact_bundle(snapshot_text, prefix.prefix_trace_text, prefix.prefix_manifest);
    if (!prefix_verify.ok) {
        err << "generated prefix failed verification failure=" << replay_artifact_failure_name(prefix_verify.failure)
            << " error=" << prefix_verify.error << "\n";
        return 5;
    }

    if (!write_text_file(prefix_trace_path, prefix.prefix_trace_text, err) ||
        !write_text_file(prefix_manifest_path, prefix.prefix_manifest_text, err)) {
        return 2;
    }

    out << "wrote replay prefix"
        << " source_failure=" << replay_artifact_failure_name(prefix.source_failure)
        << " source_ok=" << (prefix.source_verify.ok ? 1 : 0)
        << " prefix_trace=" << prefix_trace_path
        << " prefix_manifest=" << prefix_manifest_path
        << " prefix_actions=" << prefix.prefix_action_count
        << " next_bad_step=" << prefix.next_bad_step
        << " prefix_final_state_hash=" << prefix.prefix_final_state_hash
        << " prefix_bundle_hash=" << prefix.prefix_manifest.bundle_hash
        << "\n";
    return 0;
}

[[nodiscard]] int write_replay_resume_probe_artifacts(const std::string& snapshot_path,
                                                      const std::string& trace_path,
                                                      const std::string& manifest_path,
                                                      const std::string& resume_snapshot_path,
                                                      const std::string& suffix_trace_path,
                                                      const std::string& suffix_manifest_path,
                                                      std::ostream& out,
                                                      std::ostream& err) {
    std::string snapshot_text;
    std::string trace_text;
    std::string manifest_text;
    if (!read_text_file(snapshot_path, snapshot_text, err) ||
        !read_text_file(trace_path, trace_text, err) ||
        !read_text_file(manifest_path, manifest_text, err)) {
        return 2;
    }

    const auto manifest = mtgsim::parse_replay_artifact_manifest(manifest_text);
    if (!manifest.ok) {
        err << "manifest parse failed line=" << manifest.error_line << " error=" << manifest.error << "\n";
        return 3;
    }

    const auto resume = mtgsim::make_replay_artifact_resume_probe(snapshot_text, trace_text, manifest.manifest);
    if (!resume.ok) {
        err << "resume probe generation failed failure=" << replay_artifact_failure_name(resume.source_failure)
            << " error=" << resume.error
            << " source_error=" << resume.source_verify.error
            << " replay_mismatch_index=" << resume.source_verify.replay.mismatch_index
            << "\n";
        return 4;
    }

    if (!write_text_file(resume_snapshot_path, resume.resume_snapshot_text, err) ||
        !write_text_file(suffix_trace_path, resume.suffix_trace_text, err) ||
        !write_text_file(suffix_manifest_path, resume.suffix_manifest_text, err)) {
        return 2;
    }

    out << "wrote replay resume probe"
        << " source_failure=" << replay_artifact_failure_name(resume.source_failure)
        << " source_ok=" << (resume.source_verify.ok ? 1 : 0)
        << " resume_snapshot=" << resume_snapshot_path
        << " suffix_trace=" << suffix_trace_path
        << " suffix_manifest=" << suffix_manifest_path
        << " prefix_actions=" << resume.prefix_action_count
        << " suffix_actions=" << resume.suffix_action_count
        << " next_bad_step=" << resume.next_bad_step
        << " resume_state_hash=" << resume.resume_state_hash
        << " suffix_verify_ok=" << (resume.suffix_verify.ok ? 1 : 0)
        << " suffix_failure=" << replay_artifact_failure_name(resume.suffix_verify.failure)
        << " suffix_replay_mismatch_index=" << resume.suffix_verify.replay.mismatch_index
        << " suffix_bundle_hash=" << resume.suffix_manifest.bundle_hash
        << "\n";
    return 0;
}


[[nodiscard]] int run_demo() {
    auto game = make_demo_game();
    std::cout << mtgsim::debug_summary(game) << "\n";

    if (!apply_demo_actions(game, std::cerr)) {
        return 3;
    }
    std::cout << "\nAfter four replay-boundary actions:\n" << mtgsim::debug_summary(game) << "\n";
    std::cout << "StateCore hash: " << mtgsim::canonical_state_hash(game) << "\n";
    std::cout << "Action receipts: " << mtgsim::action_receipt_record_count(game) << "\n";
    return 0;
}

} // namespace

int main(int argc, char** argv) {
    if (argc <= 1) {
        print_usage(std::cout);
        return 0;
    }

    const std::string command = argv[1];
    if (command == "--demo") {
        return run_demo();
    }
    if (command == "--write-demo-replay" && argc == 4) {
        return write_demo_replay_artifacts(argv[2], argv[3], std::cout, std::cerr);
    }
    if (command == "--write-paid-action-journal-demo" && argc == 3) {
        return write_paid_action_journal_demo_artifact(argv[2], std::cout, std::cerr);
    }
    if (command == "--verify-paid-action-journal" && argc == 3) {
        return verify_paid_action_journal_artifact(argv[2], std::cout, std::cerr);
    }
    if (command == "--paid-action-journal-roundtrip" && argc == 3) {
        const int write_status = write_paid_action_journal_demo_artifact(argv[2], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return verify_paid_action_journal_artifact(argv[2], std::cout, std::cerr);
    }
    if (command == "--verify-replay" && argc == 4) {
        return verify_replay_artifacts(argv[2], argv[3], std::cout, std::cerr);
    }
    if (command == "--artifact-roundtrip" && argc == 4) {
        const int write_status = write_demo_replay_artifacts(argv[2], argv[3], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return verify_replay_artifacts(argv[2], argv[3], std::cout, std::cerr);
    }
    if (command == "--write-demo-replay-bundle" && argc == 5) {
        return write_demo_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
    }
    if (command == "--verify-replay-bundle" && argc == 5) {
        return verify_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
    }
    if (command == "--write-paid-replay-bundle-demo" && argc == 6) {
        return write_demo_paid_replay_bundle_artifacts(argv[2], argv[3], argv[4], argv[5], std::cout, std::cerr);
    }
    if (command == "--verify-paid-replay-bundle" && argc == 6) {
        return verify_paid_replay_bundle_artifacts(argv[2], argv[3], argv[4], argv[5], std::cout, std::cerr);
    }
    if (command == "--paid-replay-bundle-roundtrip" && argc == 6) {
        const int write_status = write_demo_paid_replay_bundle_artifacts(argv[2], argv[3], argv[4], argv[5], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return verify_paid_replay_bundle_artifacts(argv[2], argv[3], argv[4], argv[5], std::cout, std::cerr);
    }
    if (command == "--inspect-replay-bundle" && argc == 5) {
        return inspect_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
    }
    if (command == "--write-replay-prefix" && argc == 7) {
        return write_replay_prefix_artifacts(argv[2], argv[3], argv[4], argv[5], argv[6], std::cout, std::cerr);
    }
    if (command == "--write-replay-resume-probe" && argc == 8) {
        return write_replay_resume_probe_artifacts(argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], std::cout, std::cerr);
    }
    if (command == "--artifact-bundle-roundtrip" && argc == 5) {
        const int write_status = write_demo_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return verify_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
    }
    if (command == "--artifact-bundle-inspect-roundtrip" && argc == 5) {
        const int write_status = write_demo_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return inspect_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
    }
    if (command == "--artifact-bundle-prefix-roundtrip" && argc == 7) {
        const int write_status = write_demo_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return write_replay_prefix_artifacts(argv[2], argv[3], argv[4], argv[5], argv[6], std::cout, std::cerr);
    }
    if (command == "--artifact-bundle-resume-roundtrip" && argc == 8) {
        const int write_status = write_demo_replay_bundle_artifacts(argv[2], argv[3], argv[4], std::cout, std::cerr);
        if (write_status != 0) {
            return write_status;
        }
        return write_replay_resume_probe_artifacts(argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], std::cout, std::cerr);
    }
    if (command == "--help") {
        print_usage(std::cout);
        return 0;
    }

    std::cerr << "unknown or malformed command: " << command << "\n";
    print_usage(std::cerr);
    return 2;
}
