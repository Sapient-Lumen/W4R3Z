#include "self_exec_test_process.hpp"
#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_reset.hpp"
#include "sqlite_replay_ledger_reset_documents.hpp"
#include "sqlite_replay_ledger_reset_receipt_protocol.hpp"
#include "sqlite_replay_ledger_reset_receipt_protocol_internal.hpp"
#include "sqlite_replay_ledger_reset_fixture.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_atomic_file_publication_internal.hpp"

#include <array>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;
namespace publication = anonsync::atomic_file_publication_detail;
namespace reset_fixture =
    anonsync::test::sqlite_replay_ledger_reset_fixture;

using anonsync::SyncAtomicFilePublicationOutcome;
using anonsync::is_lowercase_sha256_hex;
using anonsync::SyncAtomicFilePublicationResidue;
using anonsync::sha256_hex;
using anonsync::test::current_self_executable_or_throw;
using anonsync::test::spawn_self_exec_test_process_or_throw;
using anonsync::test::verify_self_exec_child_boundary_or_throw;
using anonsync::persistence::SqliteReplayLedgerResetCutpoint;
using anonsync::persistence::SqliteReplayLedgerResetOutcome;
using anonsync::persistence::SqliteReplayLedgerResetObserver;
using anonsync::persistence::SqliteReplayLedgerResetReceiptProtocolError;
using anonsync::persistence::SqliteReplayLedgerResetReceiptDurableEvidence;
using anonsync::persistence::SqliteReplayLedgerResetReceiptProtocolFailure;
using anonsync::persistence::SqliteReplayLedgerResetReceiptProtocolResult;
using anonsync::persistence::SqliteReplayLedgerResetReceiptPublicationEffect;
using anonsync::persistence::SqliteReplayLedgerResetReceiptRecoveryAction;
using anonsync::persistence::SqliteReplayLedgerResetRequest;
using anonsync::persistence::SqliteReplayLedgerResetResult;
using anonsync::persistence::SqliteReplayLedgerResetState;
using anonsync::persistence::execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw;
using anonsync::persistence::inspect_sqlite_replay_ledger_reset_state;
using anonsync::persistence::sqlite_replay_ledger_reset_receipt_json;
using anonsync::persistence::sqlite_replay_ledger_reset_receipt_sha256;
using anonsync::persistence::detail::
    SqliteReplayLedgerResetReceiptProtocolObserverAccess;
using publication::AtomicFilePublicationCutpoint;
using publication::AtomicFilePublicationObservation;

constexpr int kResetCrashExit = 71;
constexpr int kPublicationCrashExitBase = 80;
constexpr int kUnexpectedChildReturn = 220;
constexpr int kUnexpectedChildException = 221;
constexpr int kUnexpectedObservation = 222;
constexpr int kHelperBoundaryFailure = 223;
constexpr int kHelperInstructionFailure = 224;
constexpr std::string_view kCrashHelperFlag =
    "--anonsync-reset-receipt-crash-helper-v1";

constexpr std::array<AtomicFilePublicationCutpoint, 11>
    kPreparedPosixPublicationCutpoints{{
        AtomicFilePublicationCutpoint::TempReserved,
        AtomicFilePublicationCutpoint::PayloadWritten,
        AtomicFilePublicationCutpoint::TempFileSynced,
        AtomicFilePublicationCutpoint::TempNameRevalidated,
        AtomicFilePublicationCutpoint::ParentDirectoryRevalidated,
        AtomicFilePublicationCutpoint::FinalEntryRevalidated,
        AtomicFilePublicationCutpoint::NamespacePublished,
        AtomicFilePublicationCutpoint::DirectorySynced,
        AtomicFilePublicationCutpoint::
            ParentDirectoryPostpublicationRevalidated,
        AtomicFilePublicationCutpoint::TempDescriptorClosed,
        AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed,
    }};

void require(bool condition,
             const std::string& message,
             std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        char pattern[] = "/tmp/anonsync-reset-publication-frontier-XXXXXX";
        char* created = ::mkdtemp(pattern);
        if (created == nullptr) {
            throw std::runtime_error(
                "could not create reset/publication frontier directory");
        }
        path_ = fs::path(created);
    }

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

void write_bytes(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("could not open frontier fixture for writing");
    }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!output) {
        throw std::runtime_error("could not write frontier fixture bytes");
    }
}

[[nodiscard]] std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("could not open frontier fixture for reading");
    }
    return std::string(std::istreambuf_iterator<char>(input),
                       std::istreambuf_iterator<char>());
}

[[nodiscard]] std::vector<fs::path> publication_temps(
    const fs::path& directory) {
    std::vector<fs::path> paths;
    for (const fs::directory_entry& entry : fs::directory_iterator(directory)) {
        const std::string name = entry.path().filename().string();
        if (name.starts_with(".anonsync-publish-v1-") &&
            name.ends_with(".tmp")) {
            paths.push_back(entry.path());
        }
    }
    return paths;
}

struct PathSnapshot final {
    std::uint64_t device = 0;
    std::uint64_t inode = 0;
    std::uint64_t size = 0;
    std::string bytes;
};

[[nodiscard]] PathSnapshot snapshot_regular_file(const fs::path& path) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0 || !S_ISREG(status.st_mode) ||
        status.st_size < 0) {
        throw std::runtime_error(
            "frontier residue is not one inspectable regular file");
    }
    PathSnapshot snapshot;
    snapshot.device = static_cast<std::uint64_t>(status.st_dev);
    snapshot.inode = static_cast<std::uint64_t>(status.st_ino);
    snapshot.size = static_cast<std::uint64_t>(status.st_size);
    snapshot.bytes = read_bytes(path);
    return snapshot;
}

[[nodiscard]] bool namespace_was_published_at(
    AtomicFilePublicationCutpoint cutpoint) noexcept {
    switch (cutpoint) {
        case AtomicFilePublicationCutpoint::NamespacePublished:
        case AtomicFilePublicationCutpoint::DirectorySynced:
        case AtomicFilePublicationCutpoint::
            ParentDirectoryPostpublicationRevalidated:
        case AtomicFilePublicationCutpoint::TempDescriptorClosed:
        case AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed:
            return true;
        case AtomicFilePublicationCutpoint::TempReserved:
        case AtomicFilePublicationCutpoint::PayloadWritten:
        case AtomicFilePublicationCutpoint::TempFileSynced:
        case AtomicFilePublicationCutpoint::TempNameRevalidated:
        case AtomicFilePublicationCutpoint::ParentDirectoryRevalidated:
        case AtomicFilePublicationCutpoint::FinalEntryRevalidated:
            return false;
    }
    return false;
}

[[nodiscard]] bool directory_was_synced_at(
    AtomicFilePublicationCutpoint cutpoint) noexcept {
    switch (cutpoint) {
        case AtomicFilePublicationCutpoint::DirectorySynced:
        case AtomicFilePublicationCutpoint::
            ParentDirectoryPostpublicationRevalidated:
        case AtomicFilePublicationCutpoint::TempDescriptorClosed:
        case AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed:
            return true;
        default:
            return false;
    }
}

[[nodiscard]] SyncAtomicFilePublicationOutcome expected_outcome_at(
    AtomicFilePublicationCutpoint cutpoint) noexcept {
    if (directory_was_synced_at(cutpoint)) {
        return SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
    }
    if (namespace_was_published_at(cutpoint)) {
        return SyncAtomicFilePublicationOutcome::
            PublishedDurabilityIndeterminate;
    }
    return SyncAtomicFilePublicationOutcome::NotPublished;
}

[[nodiscard]] SyncAtomicFilePublicationResidue expected_residue_at(
    AtomicFilePublicationCutpoint cutpoint) noexcept {
    return namespace_was_published_at(cutpoint)
               ? SyncAtomicFilePublicationResidue::None
               : SyncAtomicFilePublicationResidue::
                     TemporaryArtifactMayRemain;
}

void verify_empty_reset_state(const SqliteReplayLedgerResetState& state,
                              std::string_view expected_receipt,
                              const std::string& label,
                              std::uint64_t& checks) {
    require(state.ledger_instance_id == expected_receipt,
            label + " did not preserve the durable reset identity", checks);
    require(state.durable_line_count == 0 &&
                state.durable_head_hash == "GENESIS" &&
                state.effect_transition_line_count == 0 &&
                state.effect_transition_head_hash == "GENESIS" &&
                state.ledger_entry_rows == 0 &&
                state.effect_transition_rows == 0 &&
                state.effect_outbox_rows == 0 &&
                state.ingress_sender_replay_rows == 0,
            label + " did not preserve the complete empty reset state", checks);
}

[[nodiscard]] bool same_durable_reset_state(
    const SqliteReplayLedgerResetState& left,
    const SqliteReplayLedgerResetState& right) noexcept {
    return left.normalized_ledger_path == right.normalized_ledger_path &&
           left.namespace_identity == right.namespace_identity &&
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

void append_exception_chain(const std::exception& error,
                            std::string& chain,
                            std::uint32_t depth = 0) {
    if (!chain.empty()) chain += " <- ";
    chain += error.what();
    if (depth >= 8) return;
    try {
        std::rethrow_if_nested(error);
    } catch (const std::exception& nested) {
        append_exception_chain(nested, chain, depth + 1);
    } catch (...) {
        chain += " <- non-standard exception";
    }
}

struct PublicationCrashContext final {
    AtomicFilePublicationCutpoint target;
    SyncAtomicFilePublicationOutcome expected_outcome;
    SyncAtomicFilePublicationResidue expected_residue;
    int exit_code = 0;
};

void crash_at_publication_frontier(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    const auto& context =
        *static_cast<const PublicationCrashContext*>(raw_context);
    if (observation.cutpoint == context.target) {
        if (observation.outcome != context.expected_outcome ||
            observation.residue != context.expected_residue) {
            ::_exit(kUnexpectedObservation);
        }
        ::_exit(context.exit_code);
    }
}

void crash_at_durable_reset_frontier(SqliteReplayLedgerResetCutpoint cutpoint,
                                     void*) {
    if (cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        ::_exit(kUnexpectedChildReturn);
    }
    ::_exit(kResetCrashExit);
}

struct ThrowContext final {
    AtomicFilePublicationCutpoint target;
    bool observed = false;
    SyncAtomicFilePublicationOutcome outcome =
        SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced;
    SyncAtomicFilePublicationResidue residue =
        SyncAtomicFilePublicationResidue::TemporaryArtifactMayRemain;
};

void throw_at_publication_frontier(
    const AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context = *static_cast<ThrowContext*>(raw_context);
    if (observation.cutpoint == context.target) {
        context.observed = true;
        context.outcome = observation.outcome;
        context.residue = observation.residue;
        throw std::runtime_error(
            "injected prepared-publication frontier failure");
    }
}

struct ProtocolFixture final {
    std::string case_name;
    fs::path root;
    fs::path ledger;
    fs::path receipt_directory;
    fs::path receipt;
    fs::path recovery_receipt;
    SqliteReplayLedgerResetRequest request;
    std::string request_sha256;
    std::string receipt_sha256;
    std::string receipt_document;
};

[[nodiscard]] bool valid_helper_case_name(std::string_view case_name) noexcept {
    if (case_name.empty() || case_name.size() > 128) return false;
    for (const char character : case_name) {
        const bool lowercase = character >= 'a' && character <= 'z';
        const bool digit = character >= '0' && character <= '9';
        if (!lowercase && !digit && character != '-') return false;
    }
    return true;
}

[[nodiscard]] std::string canonical_case_component(std::string_view name) {
    std::string canonical;
    canonical.reserve(name.size());
    for (const char character : name) {
        canonical.push_back(character == '_' ? '-' : character);
    }
    if (!valid_helper_case_name(canonical)) {
        throw std::runtime_error(
            "publication cutpoint name cannot form a canonical fixture case");
    }
    return canonical;
}

[[nodiscard]] ProtocolFixture load_protocol_fixture_from_existing_root(
    const fs::path& fixture_root,
    const std::string& case_name) {
    if (!valid_helper_case_name(case_name)) {
        throw std::runtime_error("crash helper case name is not canonical");
    }

    ProtocolFixture fixture;
    fixture.case_name = case_name;
    fixture.root = fs::absolute(fixture_root).lexically_normal();
    if (!fixture.root.is_absolute() ||
        fixture.root.filename().generic_string() != case_name) {
        throw std::runtime_error(
            "crash helper root is not bound to its exact case name");
    }
    fixture.receipt_directory = fixture.root / "receipts";
    fixture.ledger =
        fs::absolute(fixture.root / "ledger.sqlite").lexically_normal();
    fixture.receipt = fixture.receipt_directory / "reset-receipt.json";
    fixture.recovery_receipt =
        fixture.receipt_directory / "reset-receipt-recovered.json";
    if (!fs::is_directory(fixture.receipt_directory) ||
        !fs::is_regular_file(fixture.ledger)) {
        throw std::runtime_error(
            "crash helper fixture does not contain its prepared namespace");
    }

    const SqliteReplayLedgerResetState state =
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger);
    fixture.request = reset_fixture::request_for(
        fixture.ledger, state, "combined-frontier-" + case_name);
    fixture.request_sha256 = sha256_hex("request-bytes:" + case_name);
    fixture.receipt_sha256 =
        sqlite_replay_ledger_reset_receipt_sha256(fixture.request);
    fixture.receipt_document = sqlite_replay_ledger_reset_receipt_json(
        fixture.request, fixture.request_sha256);
    return fixture;
}

[[nodiscard]] ProtocolFixture make_protocol_fixture(
    const fs::path& parent,
    const std::string& case_name) {
    if (!valid_helper_case_name(case_name)) {
        throw std::runtime_error("frontier fixture case name is not canonical");
    }
    const fs::path root =
        fs::absolute(parent / case_name).lexically_normal();
    fs::create_directories(root / "receipts");
    reset_fixture::seed_nonempty_ledger(root / "ledger.sqlite");
    return load_protocol_fixture_from_existing_root(root, case_name);
}

struct ProtocolFailure final {
    bool caught = false;
    SqliteReplayLedgerResetReceiptProtocolFailure failure{
        SqliteReplayLedgerResetReceiptProtocolFailure::Preparation};
    SqliteReplayLedgerResetReceiptRecoveryAction recovery_action{
        SqliteReplayLedgerResetReceiptRecoveryAction::None};
    std::optional<SqliteReplayLedgerResetOutcome> reported_reset_outcome;
    std::optional<SqliteReplayLedgerResetReceiptPublicationEffect>
        publication_effect;
    std::string expected_receipt_sha256;
    SqliteReplayLedgerResetReceiptDurableEvidence durable_evidence{
        SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable};
    std::string exception_chain;
};

[[nodiscard]] ProtocolFailure
execute_protocol_with_result_binding_observer_and_capture(
    const ProtocolFixture& fixture,
    SqliteReplayLedgerResetObserver reset_observer,
    void* reset_observer_context,
    anonsync::persistence::detail::
        SqliteReplayLedgerResetResultBindingObserver result_binding_observer,
    void* result_binding_observer_context,
    publication::AtomicFilePublicationObserver publication_observer,
    void* publication_observer_context) {
    ProtocolFailure failure;
    try {
        (void)SqliteReplayLedgerResetReceiptProtocolObserverAccess::
            execute_or_throw(
                fixture.request, fixture.request_sha256, fixture.receipt,
                reset_observer, reset_observer_context,
                result_binding_observer, result_binding_observer_context,
                publication_observer, publication_observer_context);
    } catch (const SqliteReplayLedgerResetReceiptProtocolError& error) {
        failure.caught = true;
        failure.failure = error.failure();
        failure.recovery_action = error.recovery_action();
        failure.reported_reset_outcome = error.reported_reset_outcome();
        failure.publication_effect = error.publication_effect();
        failure.expected_receipt_sha256 =
            error.expected_reset_receipt_sha256();
        failure.durable_evidence = error.durable_evidence();
        append_exception_chain(error, failure.exception_chain);
    }
    return failure;
}

[[nodiscard]] ProtocolFailure execute_protocol_and_capture(
    const ProtocolFixture& fixture,
    SqliteReplayLedgerResetObserver reset_observer,
    void* reset_observer_context,
    publication::AtomicFilePublicationObserver publication_observer,
    void* publication_observer_context) {
    return execute_protocol_with_result_binding_observer_and_capture(
        fixture, reset_observer, reset_observer_context, nullptr, nullptr,
        publication_observer, publication_observer_context);
}


enum class CrashHelperAction {
    ResetAfterDurableCommit,
    PublicationCutpoint,
};

struct CrashHelperInstruction final {
    CrashHelperAction action{CrashHelperAction::ResetAfterDurableCommit};
    fs::path fixture_root;
    std::string case_name;
    std::string expected_state_sha256;
    std::string expected_receipt_sha256;
    std::string request_sha256;
    std::optional<std::size_t> publication_index;
};

[[nodiscard]] std::size_t parse_publication_index_or_throw(
    std::string_view token) {
    std::size_t value = 0;
    const auto parsed =
        std::from_chars(token.data(), token.data() + token.size(), value);
    if (token.empty() || parsed.ec != std::errc{} ||
        parsed.ptr != token.data() + token.size() ||
        value >= kPreparedPosixPublicationCutpoints.size()) {
        throw std::runtime_error(
            "crash helper publication index is outside the reviewed frontier");
    }
    return value;
}

[[nodiscard]] CrashHelperInstruction parse_crash_helper_instruction_or_throw(
    int argc,
    char** argv) {
    if (argc != 9 || std::string_view(argv[1]) != kCrashHelperFlag) {
        throw std::runtime_error(
            "crash helper instruction has the wrong version or field count");
    }

    CrashHelperInstruction instruction;
    const std::string_view action(argv[2]);
    if (action == "reset-after-durable-commit") {
        instruction.action = CrashHelperAction::ResetAfterDurableCommit;
        if (std::string_view(argv[8]) != "none") {
            throw std::runtime_error(
                "reset crash helper carried a publication index");
        }
    } else if (action == "publication-cutpoint") {
        instruction.action = CrashHelperAction::PublicationCutpoint;
        instruction.publication_index =
            parse_publication_index_or_throw(argv[8]);
    } else {
        throw std::runtime_error("crash helper action is not recognized");
    }

    const std::string root_text(argv[3]);
    instruction.fixture_root = fs::path(root_text).lexically_normal();
    if (!instruction.fixture_root.is_absolute() ||
        instruction.fixture_root.generic_string() != root_text) {
        throw std::runtime_error(
            "crash helper fixture root is not an absolute normalized path");
    }
    instruction.case_name = argv[4];
    if (!valid_helper_case_name(instruction.case_name) ||
        instruction.fixture_root.filename().generic_string() !=
            instruction.case_name) {
        throw std::runtime_error(
            "crash helper case identity is not bound to its root path");
    }

    instruction.expected_state_sha256 = argv[5];
    instruction.expected_receipt_sha256 = argv[6];
    instruction.request_sha256 = argv[7];
    if (!is_lowercase_sha256_hex(instruction.expected_state_sha256) ||
        !is_lowercase_sha256_hex(instruction.expected_receipt_sha256) ||
        !is_lowercase_sha256_hex(instruction.request_sha256)) {
        throw std::runtime_error(
            "crash helper digest evidence is not canonical lowercase SHA-256");
    }
    return instruction;
}

[[nodiscard]] ProtocolFixture bind_crash_helper_fixture_or_throw(
    const CrashHelperInstruction& instruction) {
    ProtocolFixture fixture = load_protocol_fixture_from_existing_root(
        instruction.fixture_root, instruction.case_name);
    if (fixture.request.expected.state_sha256 !=
            instruction.expected_state_sha256 ||
        fixture.receipt_sha256 != instruction.expected_receipt_sha256 ||
        fixture.request_sha256 != instruction.request_sha256) {
        throw std::runtime_error(
            "crash helper reopened evidence does not match the exact parent instruction");
    }
    return fixture;
}

[[nodiscard]] anonsync::test::SelfExecTestProcess
spawn_frontier_self_exec_helper(
    const ProtocolFixture& fixture,
    CrashHelperAction action,
    std::optional<std::size_t> publication_index = std::nullopt) {
    if ((action == CrashHelperAction::PublicationCutpoint) !=
        publication_index.has_value()) {
        throw std::logic_error(
            "frontier helper action/index product is invalid");
    }
    const std::string action_name =
        action == CrashHelperAction::ResetAfterDurableCommit
            ? "reset-after-durable-commit"
            : "publication-cutpoint";
    const std::string index_token = publication_index.has_value()
                                        ? std::to_string(*publication_index)
                                        : "none";
    return spawn_self_exec_test_process_or_throw(
        current_self_executable_or_throw(),
        {std::string(kCrashHelperFlag), action_name,
         fixture.root.generic_string(), fixture.case_name,
         fixture.request.expected.state_sha256, fixture.receipt_sha256,
         fixture.request_sha256, index_token});
}

int run_crash_helper(int argc, char** argv) {
    try {
        verify_self_exec_child_boundary_or_throw();
    } catch (const std::exception& error) {
        std::cerr << "crash helper boundary failure: " << error.what() << "\n";
        return kHelperBoundaryFailure;
    }

    CrashHelperInstruction instruction;
    ProtocolFixture fixture;
    try {
        instruction = parse_crash_helper_instruction_or_throw(argc, argv);
        fixture = bind_crash_helper_fixture_or_throw(instruction);
    } catch (const std::exception& error) {
        std::cerr << "crash helper instruction failure: " << error.what()
                  << "\n";
        return kHelperInstructionFailure;
    }

    try {
        if (instruction.action == CrashHelperAction::ResetAfterDurableCommit) {
            (void)SqliteReplayLedgerResetReceiptProtocolObserverAccess::
                execute_or_throw(
                    fixture.request, fixture.request_sha256, fixture.receipt,
                    crash_at_durable_reset_frontier, nullptr, nullptr, nullptr,
                    nullptr, nullptr);
        } else {
            const std::size_t index = *instruction.publication_index;
            const AtomicFilePublicationCutpoint cutpoint =
                kPreparedPosixPublicationCutpoints[index];
            PublicationCrashContext context{
                cutpoint, expected_outcome_at(cutpoint),
                expected_residue_at(cutpoint),
                kPublicationCrashExitBase + static_cast<int>(index)};
            (void)SqliteReplayLedgerResetReceiptProtocolObserverAccess::
                execute_or_throw(
                    fixture.request, fixture.request_sha256, fixture.receipt,
                    nullptr, nullptr, nullptr, nullptr,
                    crash_at_publication_frontier, &context);
        }
        return kUnexpectedChildReturn;
    } catch (...) {
        return kUnexpectedChildException;
    }
}

void recover_receipt_to_fresh_path(ProtocolFixture& fixture,
                                   const std::string& label,
                                   std::uint64_t& checks) {
    const SqliteReplayLedgerResetReceiptProtocolResult replay =
        execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(
            fixture.request, fixture.request_sha256,
            fixture.recovery_receipt);
    require(replay.reset.outcome ==
                SqliteReplayLedgerResetOutcome::AlreadyCommitted,
            label + " exact replay did not recover the committed reset", checks);
    require(replay.reset.reset_receipt_sha256 == fixture.receipt_sha256,
            label + " exact replay changed the durable receipt identity", checks);
    require(replay.publication.outcome ==
                SyncAtomicFilePublicationOutcome::PublishedAndDirectorySynced &&
                replay.publication.residue ==
                    SyncAtomicFilePublicationResidue::None,
            label + " recovery did not return a durable residue-free receipt",
            checks);
    require(read_bytes(fixture.recovery_receipt) == fixture.receipt_document,
            label + " recovery publication changed canonical receipt bytes", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, label + " recovered ledger", checks);
}

void test_reset_crash_frontier(const fs::path& root, std::uint64_t& checks) {
    ProtocolFixture fixture = make_protocol_fixture(root, "reset-durable-crash");
    auto child = spawn_frontier_self_exec_helper(
        fixture, CrashHelperAction::ResetAfterDurableCommit);
    child.wait_for_exact_exit(kResetCrashExit, 10s,
                              "durable reset crash frontier");
    require(!child.active(),
            "durable reset crash helper retained process authority after wait",
            checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "durable reset crash frontier", checks);
    require(!fs::exists(fixture.receipt),
            "durable reset crash frontier published an unstarted receipt", checks);
    require(publication_temps(fixture.receipt_directory).empty(),
            "durable reset crash frontier reserved a publication temp", checks);
    recover_receipt_to_fresh_path(
        fixture, "durable reset crash frontier", checks);
}

void test_publication_process_crash_frontiers(const fs::path& root,
                                              std::uint64_t& checks) {
    for (std::size_t index = 0;
         index < kPreparedPosixPublicationCutpoints.size(); ++index) {
        const AtomicFilePublicationCutpoint cutpoint =
            kPreparedPosixPublicationCutpoints[index];
        const std::string cutpoint_name =
            publication::atomic_file_publication_cutpoint_name(cutpoint);
        ProtocolFixture fixture =
            make_protocol_fixture(
                root, "crash-" + canonical_case_component(cutpoint_name));
        const int crash_exit =
            kPublicationCrashExitBase + static_cast<int>(index);
        auto child = spawn_frontier_self_exec_helper(
            fixture, CrashHelperAction::PublicationCutpoint, index);

        const std::string label =
            "prepared publication process crash at " + cutpoint_name;
        child.wait_for_exact_exit(crash_exit, 10s, label);
        require(!child.active(),
                label + " retained process authority after bounded wait",
                checks);
        verify_empty_reset_state(
            inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
            fixture.receipt_sha256, label, checks);

        const bool published = namespace_was_published_at(cutpoint);
        require(fs::exists(fixture.receipt) == published,
                label + " produced the wrong final-name state", checks);
        if (published) {
            require(read_bytes(fixture.receipt) == fixture.receipt_document,
                    label + " published noncanonical receipt bytes", checks);
        }

        const std::vector<fs::path> temps =
            publication_temps(fixture.receipt_directory);
        require(temps.size() == (published ? 0U : 1U),
                label + " produced the wrong temporary-residue count", checks);
        PathSnapshot residue_before;
        if (!published) {
            residue_before = snapshot_regular_file(temps.front());
        }
        PathSnapshot published_before;
        if (published) {
            published_before = snapshot_regular_file(fixture.receipt);
        }

        recover_receipt_to_fresh_path(fixture, label, checks);
        if (!published) {
            const PathSnapshot residue_after =
                snapshot_regular_file(temps.front());
            require(residue_after.device == residue_before.device &&
                        residue_after.inode == residue_before.inode &&
                        residue_after.size == residue_before.size &&
                        residue_after.bytes == residue_before.bytes,
                    label +
                        " recovery guessed authority over the crash residue",
                    checks);
        } else {
            const PathSnapshot published_after =
                snapshot_regular_file(fixture.receipt);
            require(published_after.device == published_before.device &&
                        published_after.inode == published_before.inode &&
                        published_after.bytes == fixture.receipt_document,
                    label + " recovery replaced the first immutable receipt",
                    checks);
            require(read_bytes(fixture.recovery_receipt) ==
                        read_bytes(fixture.receipt),
                    label +
                        " first and recovery receipts were not byte-identical",
                    checks);
        }
    }
}

void test_protocol_caught_failure_frontiers(const fs::path& root,
                                            std::uint64_t& checks) {
    for (const AtomicFilePublicationCutpoint cutpoint :
         kPreparedPosixPublicationCutpoints) {
        const std::string cutpoint_name =
            publication::atomic_file_publication_cutpoint_name(cutpoint);
        ProtocolFixture fixture =
            make_protocol_fixture(
                root, "caught-" + canonical_case_component(cutpoint_name));
        ThrowContext context{cutpoint};
        const ProtocolFailure failure = execute_protocol_and_capture(
            fixture, nullptr, nullptr, throw_at_publication_frontier,
            &context);
        const std::string label =
            "protocol caught failure at " + cutpoint_name;
        require(failure.caught,
                label + " did not propagate a typed protocol error", checks);
        require(failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::
                        ReceiptPublicationAfterExactDurableOutcome,
                label + " lost the cross-resource failure phase", checks);
        require(failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::
                        ReplayExactRequestToFreshReceiptPath,
                label + " did not preserve exact replay authority", checks);
        require(failure.reported_reset_outcome.has_value() &&
                    *failure.reported_reset_outcome ==
                        SqliteReplayLedgerResetOutcome::Committed,
                label + " lost the durable reset outcome", checks);
        require(failure.expected_receipt_sha256 == fixture.receipt_sha256,
                label + " changed the durable receipt identity", checks);
        require(failure.publication_effect.has_value(),
                label + " lost the publication effect classification", checks);
        require(failure.publication_effect->outcome ==
                    expected_outcome_at(cutpoint),
                label + " reported the wrong publication outcome", checks);
        require(failure.publication_effect->residue ==
                    expected_residue_at(cutpoint),
                label + " reported the wrong residue authority", checks);
        require(context.observed,
                label + " did not observe the selected frontier", checks);
        require(context.outcome == failure.publication_effect->outcome &&
                    context.residue == failure.publication_effect->residue,
                label + " changed effect evidence while wrapping the failure",
                checks);
        require(failure.durable_evidence ==
                    SqliteReplayLedgerResetReceiptDurableEvidence::
                        ExactRequestDurable &&
                    failure.exception_chain.find(
                        "injected prepared-publication frontier failure") !=
                        std::string::npos,
                label + " lost the nested publication cause", checks);

        const bool published = namespace_was_published_at(cutpoint);
        require(fs::exists(fixture.receipt) == published,
                label + " produced the wrong final-name state", checks);
        if (published) {
            require(read_bytes(fixture.receipt) == fixture.receipt_document,
                    label + " published noncanonical receipt bytes", checks);
        }
        require(publication_temps(fixture.receipt_directory).size() ==
                    (published ? 0U : 1U),
                label + " produced the wrong residue count", checks);
        verify_empty_reset_state(
            inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
            fixture.receipt_sha256, label, checks);
        recover_receipt_to_fresh_path(fixture, label, checks);
    }
}

void test_protocol_public_success(const fs::path& root,
                                  std::uint64_t& checks) {
    ProtocolFixture fixture = make_protocol_fixture(root, "protocol-success");
    const SqliteReplayLedgerResetReceiptProtocolResult result =
        execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw(
            fixture.request, fixture.request_sha256, fixture.receipt);
    require(result.reset.outcome == SqliteReplayLedgerResetOutcome::Committed,
            "protocol success did not report the first durable reset", checks);
    require(result.reset.reset_receipt_sha256 == fixture.receipt_sha256 &&
                result.reset.new_ledger_instance_id == fixture.receipt_sha256 &&
                result.reset.prior.state_sha256 ==
                    fixture.request.expected.state_sha256,
            "protocol success lost request-bound reset evidence", checks);
    require(result.publication.outcome ==
                    SyncAtomicFilePublicationOutcome::
                        PublishedAndDirectorySynced &&
                result.publication.residue ==
                    SyncAtomicFilePublicationResidue::None,
            "protocol success did not prove durable receipt publication",
            checks);
    require(read_bytes(fixture.receipt) == fixture.receipt_document,
            "protocol success published noncanonical receipt bytes", checks);
    require(publication_temps(fixture.receipt_directory).empty(),
            "protocol success left temporary publication residue", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "protocol success", checks);
}

void test_protocol_preparation_denial(const fs::path& root,
                                      std::uint64_t& checks) {
    ProtocolFixture fixture =
        make_protocol_fixture(root, "protocol-preparation-denial");
    const SqliteReplayLedgerResetState state_before =
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger);
    const std::string competitor = "unrelated-existing-evidence";
    write_bytes(fixture.receipt, competitor);
    const PathSnapshot competitor_before =
        snapshot_regular_file(fixture.receipt);

    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, nullptr, nullptr, nullptr, nullptr);
    require(failure.caught &&
                failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::Preparation &&
                failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::None &&
                failure.durable_evidence ==
                    SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable &&
                !failure.reported_reset_outcome.has_value() &&
                !failure.publication_effect.has_value(),
            "occupied receipt was not a typed pre-reset preparation denial",
            checks);
    require(failure.expected_receipt_sha256 == fixture.receipt_sha256,
            "preparation denial lost the deterministic candidate identity",
            checks);
    const PathSnapshot competitor_after =
        snapshot_regular_file(fixture.receipt);
    require(competitor_after.device == competitor_before.device &&
                competitor_after.inode == competitor_before.inode &&
                competitor_after.bytes == competitor,
            "preparation denial replaced unrelated existing evidence", checks);
    require(publication_temps(fixture.receipt_directory).empty(),
            "preparation denial reserved a temporary artifact", checks);
    require(same_durable_reset_state(
                state_before,
                inspect_sqlite_replay_ledger_reset_state(fixture.ledger)),
            "preparation denial changed durable ledger state", checks);
}

void test_protocol_reset_precondition_denial(const fs::path& root,
                                             std::uint64_t& checks) {
    ProtocolFixture fixture =
        make_protocol_fixture(root, "protocol-reset-precondition-denial");
    {
        reset_fixture::Database database(fixture.ledger,
                                         SQLITE_OPEN_READWRITE);
        database.exec(
            "UPDATE effect_outbox SET dispatch_attempts=2 "
            "WHERE effect_idempotency_key='" +
            std::string(reset_fixture::kEffectKey) + "';");
    }
    const SqliteReplayLedgerResetState changed =
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger);
    require(changed.state_sha256 != fixture.request.expected.state_sha256,
            "stale-request fixture did not change exact durable state", checks);

    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, nullptr, nullptr, nullptr, nullptr);
    require(failure.caught &&
                failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::
                        ResetBeforeDurableOutcome &&
                failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::None &&
                failure.durable_evidence ==
                    SqliteReplayLedgerResetReceiptDurableEvidence::NotDurable &&
                !failure.reported_reset_outcome.has_value() &&
                !failure.publication_effect.has_value(),
            "stale request was not a typed pre-durable reset denial", checks);
    require(failure.expected_receipt_sha256 == fixture.receipt_sha256,
            "pre-durable reset denial changed the prepared candidate identity",
            checks);
    require(!fs::exists(fixture.receipt) &&
                publication_temps(fixture.receipt_directory).empty(),
            "pre-durable reset denial produced publication effects", checks);
    require(same_durable_reset_state(
                changed,
                inspect_sqlite_replay_ledger_reset_state(fixture.ledger)),
            "pre-durable reset denial changed the mismatched ledger", checks);
}

void throw_after_durable_reset_observation(
    SqliteReplayLedgerResetCutpoint cutpoint,
    void*) {
    if (cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        throw std::runtime_error(
            "protocol postcommit observer received an unexpected cutpoint");
    }
    throw std::runtime_error(
        "focused protocol postcommit observer failure");
}

void test_protocol_postcommit_failure(const fs::path& root,
                                      std::uint64_t& checks) {
    ProtocolFixture fixture =
        make_protocol_fixture(root, "protocol-postcommit-failure");
    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, throw_after_durable_reset_observation, nullptr, nullptr,
        nullptr);
    require(failure.caught &&
                failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::
                        ResetAfterExactDurableOutcome &&
                failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::
                        ReplayExactRequestToFreshReceiptPath &&
                failure.durable_evidence ==
                    SqliteReplayLedgerResetReceiptDurableEvidence::
                        ExactRequestDurable &&
                failure.reported_reset_outcome.has_value() &&
                *failure.reported_reset_outcome ==
                    SqliteReplayLedgerResetOutcome::Committed &&
                !failure.publication_effect.has_value(),
            "postcommit reset failure lost typed recovery authority", checks);
    require(failure.expected_receipt_sha256 == fixture.receipt_sha256,
            "postcommit reset failure lost expected durable identity", checks);
    require(failure.exception_chain.find(
                "focused protocol postcommit observer failure") !=
                std::string::npos,
            "postcommit reset failure lost its nested observer cause", checks);
    require(!fs::exists(fixture.receipt) &&
                publication_temps(fixture.receipt_directory).empty(),
            "postcommit reset failure attempted receipt publication", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "protocol postcommit failure", checks);
    recover_receipt_to_fresh_path(
        fixture, "protocol postcommit failure", checks);
}

void corrupt_returned_reason_digest(
    SqliteReplayLedgerResetResult& result,
    void*) {
    result.reason_sha256 =
        sha256_hex("contradictory returned reset result reason");
}

void test_result_binding_contradiction_promotes_only_after_reopen(
    const fs::path& root,
    std::uint64_t& checks) {
    ProtocolFixture fixture =
        make_protocol_fixture(root, "result-binding-reopen-promotion");
    const ProtocolFailure failure =
        execute_protocol_with_result_binding_observer_and_capture(
            fixture, nullptr, nullptr, corrupt_returned_reason_digest, nullptr,
            nullptr, nullptr);
    require(
        failure.caught &&
            failure.failure ==
                SqliteReplayLedgerResetReceiptProtocolFailure::
                    ResetAfterExactDurableOutcome &&
            failure.durable_evidence ==
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    ExactRequestDurable &&
            failure.recovery_action ==
                SqliteReplayLedgerResetReceiptRecoveryAction::
                    ReplayExactRequestToFreshReceiptPath &&
            failure.reported_reset_outcome.has_value() &&
            *failure.reported_reset_outcome ==
                SqliteReplayLedgerResetOutcome::Committed &&
            !failure.publication_effect.has_value(),
        "contradictory returned result was not promoted only after exact independent reopen",
        checks);
    require(
        failure.exception_chain.find(
            "reset result reason digest is not bound to the protocol request") !=
            std::string::npos &&
            failure.exception_chain.find(
                "independent reopen bound the current SQLite namespace") !=
                std::string::npos,
        "result-binding promotion lost its contradiction or independent-reopen evidence",
        checks);
    require(!fs::exists(fixture.receipt) &&
                publication_temps(fixture.receipt_directory).empty(),
            "result-binding contradiction attempted receipt publication", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "result-binding reopen promotion", checks);
    recover_receipt_to_fresh_path(
        fixture, "result-binding reopen promotion", checks);
}

struct IdentityReplacementContext final {
    fs::path ledger;
    std::string replacement_identity;
    bool replaced = false;
};

void contradict_returned_result_and_replace_durable_identity(
    SqliteReplayLedgerResetResult& result,
    void* raw_context) {
    auto& context = *static_cast<IdentityReplacementContext*>(raw_context);
    result.reason_sha256 =
        sha256_hex("contradictory result while durable identity advances");
    reset_fixture::Database database(context.ledger, SQLITE_OPEN_READWRITE);
    database.exec(
        "UPDATE ledger_identity SET ledger_instance_id='" +
        context.replacement_identity + "' WHERE id=1;");
    context.replaced = true;
}

void test_result_binding_indeterminate_blocks_replay_authority(
    const fs::path& root,
    std::uint64_t& checks) {
    ProtocolFixture fixture = make_protocol_fixture(
        root, "result-binding-identity-indeterminate");
    IdentityReplacementContext context{
        fixture.ledger,
        sha256_hex("different identity after a contradictory returned result")};
    const ProtocolFailure failure =
        execute_protocol_with_result_binding_observer_and_capture(
            fixture, nullptr, nullptr,
            contradict_returned_result_and_replace_durable_identity, &context,
            nullptr, nullptr);
    require(
        failure.caught && context.replaced &&
            failure.failure ==
                SqliteReplayLedgerResetReceiptProtocolFailure::
                    ResetDurableIdentityIndeterminate &&
            failure.durable_evidence ==
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    DurableIdentityIndeterminate &&
            failure.recovery_action ==
                SqliteReplayLedgerResetReceiptRecoveryAction::
                    ResolveDurableIdentityBeforeRecovery &&
            failure.reported_reset_outcome.has_value() &&
            *failure.reported_reset_outcome ==
                SqliteReplayLedgerResetOutcome::Committed &&
            !failure.publication_effect.has_value(),
        "contradictory returned result incorrectly authorized replay after durable identity drift",
        checks);
    require(
        failure.exception_chain.find(
            "reset result reason digest is not bound to the protocol request") !=
                std::string::npos &&
            failure.exception_chain.find(context.replacement_identity) !=
                std::string::npos,
        "contradictory-result indeterminate classification lost its binding cause or reopened identity",
        checks);
    const SqliteReplayLedgerResetState observed =
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger);
    require(observed.ledger_instance_id == context.replacement_identity,
            "contradictory-result test did not retain the competing durable identity",
            checks);
    require(!fs::exists(fixture.receipt) &&
                publication_temps(fixture.receipt_directory).empty(),
            "contradictory-result indeterminate state attempted receipt publication",
            checks);
}

void replace_durable_identity_before_postcommit_verification(
    SqliteReplayLedgerResetCutpoint cutpoint,
    void* raw_context) {
    if (cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        throw std::runtime_error(
            "unexpected durable-identity replacement cutpoint");
    }
    auto& context = *static_cast<IdentityReplacementContext*>(raw_context);
    reset_fixture::Database database(context.ledger, SQLITE_OPEN_READWRITE);
    database.exec(
        "UPDATE ledger_identity SET ledger_instance_id='" +
        context.replacement_identity + "' WHERE id=1;");
    context.replaced = true;
}

void test_durable_identity_indeterminate_blocks_replay_authority(
    const fs::path& root,
    std::uint64_t& checks) {
    ProtocolFixture fixture =
        make_protocol_fixture(root, "durable-identity-indeterminate");
    IdentityReplacementContext context{
        fixture.ledger,
        sha256_hex("different durable identity after reset commit")};
    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, replace_durable_identity_before_postcommit_verification,
        &context, nullptr, nullptr);
    require(
        failure.caught && context.replaced &&
            failure.failure ==
                SqliteReplayLedgerResetReceiptProtocolFailure::
                    ResetDurableIdentityIndeterminate &&
            failure.durable_evidence ==
                SqliteReplayLedgerResetReceiptDurableEvidence::
                    DurableIdentityIndeterminate &&
            failure.recovery_action ==
                SqliteReplayLedgerResetReceiptRecoveryAction::
                    ResolveDurableIdentityBeforeRecovery &&
            failure.reported_reset_outcome.has_value() &&
            *failure.reported_reset_outcome ==
                SqliteReplayLedgerResetOutcome::Committed &&
            !failure.publication_effect.has_value(),
        "changed postcommit identity incorrectly retained automatic replay authority",
        checks);
    require(
        failure.exception_chain.find(
            "durable receipt identity") != std::string::npos ||
            failure.exception_chain.find(
                "committed postcondition is incomplete") != std::string::npos,
        "indeterminate durable identity lost the reset postcommit cause", checks);
    require(
        failure.exception_chain.find(context.replacement_identity) !=
            std::string::npos,
        "indeterminate durable identity did not report the independently reopened identity",
        checks);
    const SqliteReplayLedgerResetState observed =
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger);
    require(observed.ledger_instance_id == context.replacement_identity,
            "indeterminate test did not retain the competing durable identity",
            checks);
    require(!fs::exists(fixture.receipt) &&
                publication_temps(fixture.receipt_directory).empty(),
            "indeterminate durable identity attempted receipt publication", checks);
}

struct RebindContext final {
    fs::path live_parent;
    fs::path parked_parent;
    std::string sentinel;
};

void rebind_receipt_parent_after_reset(SqliteReplayLedgerResetCutpoint cutpoint,
                                       void* raw_context) {
    if (cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        throw std::runtime_error("unexpected reset rebind cutpoint");
    }
    auto& context = *static_cast<RebindContext*>(raw_context);
    fs::rename(context.live_parent, context.parked_parent);
    fs::create_directory(context.live_parent);
    write_bytes(context.live_parent / "replacement-sentinel.txt",
                context.sentinel);
}

void test_parent_rebind_after_durable_reset(const fs::path& root,
                                            std::uint64_t& checks) {
    ProtocolFixture fixture = make_protocol_fixture(root, "parent-rebind");
    const fs::path parked = fixture.root / "receipts-parked";
    RebindContext context{fixture.receipt_directory, parked,
                          "replacement-parent-must-survive"};
    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, rebind_receipt_parent_after_reset, &context, nullptr,
        nullptr);
    require(failure.caught &&
                failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::
                        ReceiptPublicationAfterExactDurableOutcome &&
                failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::
                        ReplayExactRequestToFreshReceiptPath &&
                failure.reported_reset_outcome.has_value() &&
                *failure.reported_reset_outcome ==
                    SqliteReplayLedgerResetOutcome::Committed &&
                failure.publication_effect.has_value() &&
                failure.publication_effect->outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                failure.publication_effect->residue ==
                    SyncAtomicFilePublicationResidue::None,
            "parent rebind after durable reset was not a typed residue-free denial",
            checks);
    require(!fs::exists(parked / fixture.receipt.filename()) &&
                !fs::exists(fixture.receipt),
            "parent-rebind denial published into an old or replacement parent",
            checks);
    require(publication_temps(parked).empty() &&
                publication_temps(fixture.receipt_directory).empty(),
            "parent-rebind denial reserved a temporary artifact", checks);
    require(read_bytes(fixture.receipt_directory /
                       "replacement-sentinel.txt") == context.sentinel,
            "parent-rebind denial changed the replacement directory", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "parent-rebind durable reset", checks);
    recover_receipt_to_fresh_path(fixture, "parent-rebind durable reset", checks);
}

struct CompetitorContext final {
    fs::path receipt;
    std::string bytes;
};

void create_competing_receipt_after_reset(
    SqliteReplayLedgerResetCutpoint cutpoint,
    void* raw_context) {
    if (cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        throw std::runtime_error("unexpected reset competitor cutpoint");
    }
    auto& context = *static_cast<CompetitorContext*>(raw_context);
    write_bytes(context.receipt, context.bytes);
}

void test_competing_final_after_durable_reset(const fs::path& root,
                                              std::uint64_t& checks) {
    ProtocolFixture fixture = make_protocol_fixture(root, "final-competitor");
    CompetitorContext context{fixture.receipt,
                              "competitor-must-not-be-replaced"};
    const ProtocolFailure failure = execute_protocol_and_capture(
        fixture, create_competing_receipt_after_reset, &context, nullptr,
        nullptr);
    const PathSnapshot competitor_before =
        snapshot_regular_file(fixture.receipt);
    require(failure.caught &&
                failure.failure ==
                    SqliteReplayLedgerResetReceiptProtocolFailure::
                        ReceiptPublicationAfterExactDurableOutcome &&
                failure.recovery_action ==
                    SqliteReplayLedgerResetReceiptRecoveryAction::
                        ReplayExactRequestToFreshReceiptPath &&
                failure.reported_reset_outcome.has_value() &&
                *failure.reported_reset_outcome ==
                    SqliteReplayLedgerResetOutcome::Committed &&
                failure.publication_effect.has_value() &&
                failure.publication_effect->outcome ==
                    SyncAtomicFilePublicationOutcome::NotPublished &&
                failure.publication_effect->residue ==
                    SyncAtomicFilePublicationResidue::None,
            "competing final after durable reset was not a typed residue-free denial",
            checks);
    const PathSnapshot competitor_after =
        snapshot_regular_file(fixture.receipt);
    require(competitor_after.device == competitor_before.device &&
                competitor_after.inode == competitor_before.inode &&
                competitor_after.bytes == context.bytes,
            "competing final was replaced after the durable reset", checks);
    require(publication_temps(fixture.receipt_directory).empty(),
            "competing-final denial reserved a temporary artifact", checks);
    verify_empty_reset_state(
        inspect_sqlite_replay_ledger_reset_state(fixture.ledger),
        fixture.receipt_sha256, "final-competitor durable reset", checks);
    recover_receipt_to_fresh_path(
        fixture, "final-competitor durable reset", checks);
    require(snapshot_regular_file(fixture.receipt).inode ==
                competitor_before.inode,
            "fresh-path recovery replaced the competing final", checks);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc >= 2 && std::string_view(argv[1]) == kCrashHelperFlag) {
        return run_crash_helper(argc, argv);
    }

    std::uint64_t checks = 0;
    try {
        if (argc != 1) {
            throw std::runtime_error(
                "usage: anonsync_sqlite_replay_ledger_reset_crash_frontier_test");
        }
        TemporaryDirectory temporary;
        test_protocol_public_success(temporary.path(), checks);
        test_protocol_preparation_denial(temporary.path(), checks);
        test_protocol_reset_precondition_denial(temporary.path(), checks);
        test_protocol_postcommit_failure(temporary.path(), checks);
        test_result_binding_contradiction_promotes_only_after_reopen(
            temporary.path(), checks);
        test_result_binding_indeterminate_blocks_replay_authority(
            temporary.path(), checks);
        test_durable_identity_indeterminate_blocks_replay_authority(
            temporary.path(), checks);
        test_reset_crash_frontier(temporary.path(), checks);
        test_publication_process_crash_frontiers(temporary.path(), checks);
        test_protocol_caught_failure_frontiers(temporary.path(), checks);
        test_parent_rebind_after_durable_reset(temporary.path(), checks);
        test_competing_final_after_durable_reset(temporary.path(), checks);
        std::cout
            << "anonsync_sqlite_replay_ledger_reset_crash_frontier_test checks="
            << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "anonsync_sqlite_replay_ledger_reset_crash_frontier_test failure after "
            << checks << " checks: " << error.what() << "\n";
        return 2;
    }
}
