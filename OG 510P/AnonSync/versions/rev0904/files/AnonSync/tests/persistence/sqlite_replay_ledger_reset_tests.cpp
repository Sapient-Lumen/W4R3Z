#include "self_exec_test_process.hpp"
#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_reset.hpp"
#include "sqlite_replay_ledger_reset_fixture.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"
#include "sqlite_replay_ledger_write_gate.hpp"
#include "sync_process_incarnation.hpp"

#include <sqlite3.h>

#include <atomic>
#include <chrono>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>

#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;
using anonsync::Sha256DigestBuilder;
using anonsync::is_lowercase_sha256_hex;
using anonsync::sha256_hex;
using anonsync::test::current_self_executable_or_throw;
using anonsync::test::spawn_self_exec_test_process_or_throw;
using anonsync::test::verify_self_exec_child_boundary_or_throw;
using anonsync::persistence::SqliteReplayLedgerResetCutpoint;
using anonsync::persistence::SqliteReplayLedgerResetDurableOutcomeError;
using anonsync::persistence::SqliteReplayLedgerResetExpectation;
using anonsync::persistence::SqliteReplayLedgerResetOutcome;
using anonsync::persistence::SqliteReplayLedgerResetRequest;
using anonsync::persistence::SqliteReplayLedgerResetState;
using anonsync::persistence::SqliteReplayLedgerWriteGate;
using anonsync::persistence::inspect_sqlite_replay_ledger_reset_state;
using anonsync::persistence::reset_sqlite_replay_ledger;
using anonsync::persistence::sqlite_replay_ledger_reset_receipt_sha256;
using anonsync::persistence::sqlite_replay_ledger_schema_contract;
using anonsync::persistence::sqlite_replay_ledger_schema_create_statement;
namespace reset_fixture = anonsync::test::sqlite_replay_ledger_reset_fixture;
using reset_fixture::Database;
using reset_fixture::cleanup_family;
using reset_fixture::kEffectKey;
using reset_fixture::kInitialIdentity;
using reset_fixture::request_for;
using reset_fixture::seed_nonempty_ledger;

constexpr std::string_view kFocusedHelperFlag =
    "--anonsync-reset-focused-helper-v1";
constexpr int kFocusedHelperBoundaryFailure = 96;
constexpr int kFocusedHelperInstructionFailure = 97;
constexpr int kFocusedHelperUnexpectedReturn = 98;
constexpr int kFocusedHelperException = 99;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

template <typename Callable>
void expect_rejection(Callable&& callable,
                      std::string_view expected_fragment,
                      std::uint64_t& checks) {
    bool rejected = false;
    try {
        callable();
    } catch (const std::exception& error) {
        rejected = std::string(error.what()).find(expected_fragment) !=
                   std::string::npos;
        if (!rejected) {
            throw std::runtime_error(
                "unexpected rejection text: " + std::string(error.what()));
        }
    }
    require(rejected,
            "expected rejection containing: " + std::string(expected_fragment),
            checks);
}

[[nodiscard]] bool exception_chain_contains(
    const std::exception& error,
    std::string_view expected,
    std::uint32_t depth = 0) {
    if (std::string_view(error.what()).find(expected) != std::string_view::npos) {
        return true;
    }
    if (depth >= 8) return false;
    try {
        std::rethrow_if_nested(error);
    } catch (const std::exception& nested) {
        return exception_chain_contains(nested, expected, depth + 1);
    } catch (...) {
        return false;
    }
    return false;
}

std::pair<dev_t, ino_t> identity_of(const fs::path& path) {
    struct stat status {};
    if (::stat(path.c_str(), &status) != 0) {
        throw std::runtime_error("could not stat focused ledger fixture");
    }
    return {status.st_dev, status.st_ino};
}

void mutate_digest_only(const fs::path& path) {
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("PRAGMA foreign_keys=ON;");
    database.exec(
        "UPDATE effect_outbox SET dispatch_attempts=dispatch_attempts+1 "
        "WHERE effect_idempotency_key='" + std::string(kEffectKey) + "';");
}

void append_after_reset(const fs::path& path) {
    const std::string new_entry_hash(64, '5');
    const std::string new_effect_key(64, '6');
    const std::string new_contract_hash(64, '7');
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("PRAGMA foreign_keys=ON;");
    database.exec("BEGIN IMMEDIATE;");
    database.exec(
        "INSERT INTO ledger_entries(sequence, previous_hash, entry_hash, case_id, "
        "kind, operation_id, contract_digest_sha256, jti, action, "
        "cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state) "
        "VALUES(1, 'GENESIS', '" + new_entry_hash +
        "', 'post-reset-case', 'openapi', 'post-reset-operation', '" +
        new_contract_hash +
        "', 'post-reset-jti', 'allow', '', '', '" + new_effect_key +
        "', 'prepared');");
    database.exec(
        "INSERT INTO effect_outbox(effect_idempotency_key, prepared_sequence, "
        "prepared_entry_hash, outbox_state, dispatch_attempts, worker_claim_id, "
        "worker_id, claimed_at_epoch, lease_expires_at_epoch, "
        "last_result_digest_sha256, updated_at_sequence) VALUES('" +
        new_effect_key + "', 1, '" + new_entry_hash +
        "', 'reserved', 0, '', '', 0, 0, '', 1);");
    database.exec("UPDATE metadata SET line_count=1, head_hash='" +
                  new_entry_hash + "' WHERE id=1;");
    database.exec("COMMIT;");
}


enum class FocusedHelperAction {
    WriteGateLifetimeInversion,
    WriteGateCrossThreadDestruction,
    CommitBeforeReportLoss,
};

struct FocusedHelperInstruction final {
    FocusedHelperAction action{FocusedHelperAction::WriteGateLifetimeInversion};
    fs::path ledger_path;
    std::string reason;
    std::string expected_state_sha256;
    std::string expected_receipt_sha256;
};

[[nodiscard]] FocusedHelperInstruction
parse_focused_helper_instruction_or_throw(int argc, char** argv) {
    if (argc != 7 || std::string_view(argv[1]) != kFocusedHelperFlag) {
        throw std::runtime_error(
            "focused reset helper has the wrong version or field count");
    }

    FocusedHelperInstruction instruction;
    const std::string_view action(argv[2]);
    if (action == "write-gate-lifetime-inversion") {
        instruction.action = FocusedHelperAction::WriteGateLifetimeInversion;
    } else if (action == "write-gate-cross-thread-destruction") {
        instruction.action =
            FocusedHelperAction::WriteGateCrossThreadDestruction;
    } else if (action == "commit-before-report-loss") {
        instruction.action = FocusedHelperAction::CommitBeforeReportLoss;
    } else {
        throw std::runtime_error("focused reset helper action is not recognized");
    }

    const std::string path_text(argv[3]);
    instruction.ledger_path = fs::path(path_text).lexically_normal();
    if (!instruction.ledger_path.is_absolute() ||
        instruction.ledger_path.generic_string() != path_text ||
        !fs::is_directory(instruction.ledger_path.parent_path())) {
        throw std::runtime_error(
            "focused reset helper path is not absolute, normalized, and parent-bound");
    }

    instruction.reason = argv[4];
    instruction.expected_state_sha256 = argv[5];
    instruction.expected_receipt_sha256 = argv[6];
    if (instruction.action == FocusedHelperAction::CommitBeforeReportLoss) {
        if (instruction.reason.empty() || instruction.reason == "none" ||
            instruction.reason.size() > 256 ||
            !is_lowercase_sha256_hex(instruction.expected_state_sha256) ||
            !is_lowercase_sha256_hex(instruction.expected_receipt_sha256)) {
            throw std::runtime_error(
                "focused reset helper commit evidence is not canonical");
        }
    } else if (instruction.reason != "none" ||
               instruction.expected_state_sha256 != "none" ||
               instruction.expected_receipt_sha256 != "none") {
        throw std::runtime_error(
            "focused reset write-gate helper carried unrelated durable evidence");
    }
    return instruction;
}

[[nodiscard]] anonsync::test::SelfExecTestProcess
spawn_focused_reset_helper(
    FocusedHelperAction action,
    const fs::path& ledger_path,
    std::string reason = "none",
    std::string expected_state_sha256 = "none",
    std::string expected_receipt_sha256 = "none") {
    std::string action_name;
    switch (action) {
        case FocusedHelperAction::WriteGateLifetimeInversion:
            action_name = "write-gate-lifetime-inversion";
            break;
        case FocusedHelperAction::WriteGateCrossThreadDestruction:
            action_name = "write-gate-cross-thread-destruction";
            break;
        case FocusedHelperAction::CommitBeforeReportLoss:
            action_name = "commit-before-report-loss";
            break;
    }
    return spawn_self_exec_test_process_or_throw(
        current_self_executable_or_throw(),
        {std::string(kFocusedHelperFlag), action_name,
         ledger_path.generic_string(), std::move(reason),
         std::move(expected_state_sha256),
         std::move(expected_receipt_sha256)});
}

int run_focused_reset_helper(int argc, char** argv) {
    try {
        verify_self_exec_child_boundary_or_throw();
    } catch (const std::exception& error) {
        std::cerr << "focused reset helper boundary failure: " << error.what()
                  << "\n";
        return kFocusedHelperBoundaryFailure;
    }

    FocusedHelperInstruction instruction;
    try {
        instruction = parse_focused_helper_instruction_or_throw(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "focused reset helper instruction failure: " << error.what()
                  << "\n";
        return kFocusedHelperInstructionFailure;
    }

    try {
        if (instruction.action ==
            FocusedHelperAction::WriteGateLifetimeInversion) {
            auto outer =
                std::make_unique<SqliteReplayLedgerWriteGate>(
                    instruction.ledger_path);
            auto inner =
                std::make_unique<SqliteReplayLedgerWriteGate>(
                    instruction.ledger_path);
            outer.reset();
            (void)inner;
            return kFocusedHelperUnexpectedReturn;
        }
        if (instruction.action ==
            FocusedHelperAction::WriteGateCrossThreadDestruction) {
            std::unique_ptr<SqliteReplayLedgerWriteGate> transferred;
            std::atomic<bool> acquired{false};
            std::thread origin([&] {
                transferred =
                    std::make_unique<SqliteReplayLedgerWriteGate>(
                        instruction.ledger_path);
                acquired.store(transferred->owns_exclusive_gate(),
                               std::memory_order_release);
            });
            origin.join();
            if (!acquired.load(std::memory_order_acquire) || !transferred) {
                return kFocusedHelperInstructionFailure;
            }
            transferred.reset();
            return kFocusedHelperUnexpectedReturn;
        }

        const SqliteReplayLedgerResetState state =
            inspect_sqlite_replay_ledger_reset_state(instruction.ledger_path);
        if (state.state_sha256 != instruction.expected_state_sha256) {
            return kFocusedHelperInstructionFailure;
        }
        const SqliteReplayLedgerResetRequest request = request_for(
            instruction.ledger_path, state, instruction.reason);
        if (sqlite_replay_ledger_reset_receipt_sha256(request) !=
            instruction.expected_receipt_sha256) {
            return kFocusedHelperInstructionFailure;
        }
        const auto result = reset_sqlite_replay_ledger(request);
        return result.outcome == SqliteReplayLedgerResetOutcome::Committed ? 0
                                                                           : 3;
    } catch (...) {
        return kFocusedHelperException;
    }
}

void test_streaming_digest(std::uint64_t& checks) {
    Sha256DigestBuilder builder;
    builder.update("a");
    builder.update("bc");
    require(builder.finish_hex() == sha256_hex("abc"),
            "incremental SHA-256 diverged from one-shot digest", checks);
    expect_rejection([&] { builder.update("late"); }, "not updateable", checks);
    expect_rejection([&] { (void)builder.finish_hex(); }, "not finishable",
                     checks);
}

void test_write_gate_scope_fences(const fs::path& root,
                                  std::uint64_t& checks) {
    const fs::path path =
        fs::absolute(root / "write-gate-lifetime.sqlite").lexically_normal();
    cleanup_family(path);
    {
        SqliteReplayLedgerWriteGate outer(path);
        require(outer.owns_exclusive_gate(),
                "outer write-gate scope did not own the kernel lock", checks);
        {
            SqliteReplayLedgerWriteGate inner(path);
            require(inner.owns_exclusive_gate(),
                    "reviewed nested write-gate scope lost authority", checks);
        }
        require(outer.owns_exclusive_gate(),
                "outer write-gate scope lost authority after LIFO release",
                checks);
    }

    auto inverted_child = spawn_focused_reset_helper(
        FocusedHelperAction::WriteGateLifetimeInversion, path);
    inverted_child.wait_for_exact_exit(
        anonsync::kSyncProcessCapabilityViolationExitCode, 10s,
        "write-gate lifetime-inversion helper");
    require(!inverted_child.active(),
            "nested write-gate lifetime inversion did not fail stopped",
            checks);

    auto cross_thread_child = spawn_focused_reset_helper(
        FocusedHelperAction::WriteGateCrossThreadDestruction, path);
    cross_thread_child.wait_for_exact_exit(
        anonsync::kSyncProcessCapabilityViolationExitCode, 10s,
        "write-gate cross-thread helper");
    require(!cross_thread_child.active(),
            "cross-thread write-gate destruction did not fail stopped",
            checks);
    cleanup_family(path);
}

void test_reset_protocol(const fs::path& root, std::uint64_t& checks) {
    const fs::path path = fs::absolute(root / "reset.sqlite").lexically_normal();
    seed_nonempty_ledger(path);
    const auto inode_before = identity_of(path);

    const SqliteReplayLedgerResetState first =
        inspect_sqlite_replay_ledger_reset_state(path);
    require(first.normalized_ledger_path == path.generic_string(),
            "inspection did not bind normalized path", checks);
    const auto [device_before, inode_value_before] = inode_before;
    require(first.namespace_identity.database_device ==
                static_cast<std::uint64_t>(device_before) &&
                first.namespace_identity.database_inode ==
                static_cast<std::uint64_t>(inode_value_before),
            "inspection did not bind the exact database namespace object", checks);
    struct stat parent_status {};
    if (::stat(path.parent_path().c_str(), &parent_status) != 0) {
        throw std::runtime_error("could not stat focused ledger parent");
    }
    require(first.namespace_identity.parent_device ==
                static_cast<std::uint64_t>(parent_status.st_dev) &&
                first.namespace_identity.parent_inode ==
                static_cast<std::uint64_t>(parent_status.st_ino),
            "inspection did not bind the exact parent namespace object", checks);
    require(first.ledger_instance_id == kInitialIdentity,
            "inspection returned wrong ledger identity", checks);
    require(is_lowercase_sha256_hex(first.state_sha256),
            "inspection did not mint exact state digest", checks);
    require(first.durable_line_count == 1 && first.ledger_entry_rows == 1,
            "inspection lost decision rows", checks);
    require(first.effect_transition_line_count == 1 &&
                first.effect_transition_rows == 1,
            "inspection lost transition rows", checks);
    require(first.effect_outbox_rows == 1 &&
                first.ingress_sender_replay_rows == 1,
            "inspection lost related durable rows", checks);
    require(first.connection_owner_generation > 0,
            "inspection did not expose owner generation", checks);
    const SqliteReplayLedgerResetState repeated =
        inspect_sqlite_replay_ledger_reset_state(path);
    require(repeated.state_sha256 == first.state_sha256,
            "canonical state digest was nondeterministic", checks);
    require(repeated.namespace_identity == first.namespace_identity,
            "namespace identity changed without path replacement", checks);

    SqliteReplayLedgerResetRequest stale = request_for(path, first);
    const std::string stale_receipt =
        sqlite_replay_ledger_reset_receipt_sha256(stale);
    require(is_lowercase_sha256_hex(stale_receipt) &&
                stale_receipt != first.ledger_instance_id,
            "reset receipt was not a distinct deterministic identity", checks);
    require(sqlite_replay_ledger_reset_receipt_sha256(stale) == stale_receipt,
            "reset receipt derivation was nondeterministic", checks);

    SqliteReplayLedgerResetRequest bad_digest = stale;
    bad_digest.expected.state_sha256 = std::string(64, '0');
    expect_rejection(
        [&] { (void)reset_sqlite_replay_ledger(bad_digest); },
        "precondition mismatch", checks);
    require(inspect_sqlite_replay_ledger_reset_state(path).state_sha256 ==
                first.state_sha256,
            "mismatched digest request mutated the ledger", checks);

    // The summaries remain unchanged, but one durable field changes. Identity-
    // only or count/head-only authorization would erase this later write.
    mutate_digest_only(path);
    const SqliteReplayLedgerResetState changed =
        inspect_sqlite_replay_ledger_reset_state(path);
    require(changed.ledger_instance_id == first.ledger_instance_id &&
                changed.durable_line_count == first.durable_line_count &&
                changed.durable_head_hash == first.durable_head_hash &&
                changed.state_sha256 != first.state_sha256,
            "digest-only mutation did not isolate stale-intent hazard", checks);
    expect_rejection(
        [&] { (void)reset_sqlite_replay_ledger(stale); },
        "precondition mismatch", checks);
    require(inspect_sqlite_replay_ledger_reset_state(path).state_sha256 ==
                changed.state_sha256,
            "stale reset intent erased later durable state", checks);

    SqliteReplayLedgerResetRequest current = request_for(path, changed);
    {
        SqliteReplayLedgerWriteGate held(path);
        require(held.owns_exclusive_gate(),
                "focused test could not hold same-thread write gate", checks);
        expect_rejection(
            [&] { (void)reset_sqlite_replay_ledger(current); },
            "rejects same-thread nested ownership", checks);
    }
    require(inspect_sqlite_replay_ledger_reset_state(path).state_sha256 ==
                changed.state_sha256,
            "same-thread nested reset mutated durable state", checks);

    std::string contention_reason;
    {
        SqliteReplayLedgerWriteGate held(path);
        require(held.owns_exclusive_gate(),
                "focused test could not hold cross-thread write gate", checks);
        std::thread contender([&] {
            try {
                (void)reset_sqlite_replay_ledger(current);
            } catch (const std::exception& error) {
                contention_reason = error.what();
            }
        });
        contender.join();
    }
    require(contention_reason.find("lock contention") != std::string::npos,
            "cross-thread reset bypassed exclusive write gate", checks);

    const std::string receipt =
        sqlite_replay_ledger_reset_receipt_sha256(current);
    const auto committed = reset_sqlite_replay_ledger(current);
    require(committed.outcome == SqliteReplayLedgerResetOutcome::Committed,
            "fresh exact request did not commit", checks);
    require(!committed.state_advanced_after_commit,
            "fresh commit incorrectly reported later state", checks);
    require(committed.reset_receipt_sha256 == receipt &&
                committed.new_ledger_instance_id == receipt,
            "committed reset did not rotate identity to receipt", checks);
    require(committed.prior.state_sha256 == changed.state_sha256,
            "committed receipt lost prior state digest", checks);
    require(is_lowercase_sha256_hex(committed.reason_sha256),
            "committed receipt lost reason digest", checks);
    require(identity_of(path) == inode_before,
            "reset replaced or deleted the main database inode", checks);

    const SqliteReplayLedgerResetState empty =
        inspect_sqlite_replay_ledger_reset_state(path);
    require(empty.ledger_instance_id == receipt,
            "post-reset identity is not the durable receipt", checks);
    require(empty.durable_line_count == 0 &&
                empty.effect_transition_line_count == 0 &&
                empty.ledger_entry_rows == 0 &&
                empty.effect_transition_rows == 0 &&
                empty.effect_outbox_rows == 0 &&
                empty.ingress_sender_replay_rows == 0,
            "post-reset operational state is not empty", checks);

    const auto replayed = reset_sqlite_replay_ledger(current);
    require(replayed.outcome ==
                SqliteReplayLedgerResetOutcome::AlreadyCommitted,
            "exact post-commit replay was not idempotent", checks);
    require(replayed.reset_receipt_sha256 == receipt,
            "idempotent replay changed receipt", checks);
    require(!replayed.state_advanced_after_commit,
            "empty idempotent replay incorrectly reported later state", checks);

    append_after_reset(path);
    const auto advanced_replay = reset_sqlite_replay_ledger(current);
    require(advanced_replay.outcome ==
                SqliteReplayLedgerResetOutcome::AlreadyCommitted,
            "receipt recovery after a later append lost committed identity", checks);
    require(advanced_replay.state_advanced_after_commit,
            "receipt recovery did not report later durable state", checks);
    {
        Database database(path, SQLITE_OPEN_READWRITE);
        require(database.integer("SELECT count(*) FROM ledger_entries;") == 1,
                "replayed old reset wiped post-reset append", checks);
    }
    cleanup_family(path);
}

void fail_after_durable_reset_observation(
    SqliteReplayLedgerResetCutpoint cutpoint,
    void* context) {
    auto* observed = static_cast<bool*>(context);
    if (observed == nullptr ||
        cutpoint != SqliteReplayLedgerResetCutpoint::
                        DurableOutcomeObservedBeforePostcommitVerification) {
        throw std::runtime_error("reset cutpoint observer received invalid evidence");
    }
    *observed = true;
    throw std::runtime_error("focused injected post-commit verification failure");
}

void test_typed_postcommit_failure(const fs::path& root,
                                   std::uint64_t& checks) {
    const fs::path path =
        fs::absolute(root / "postcommit-failure.sqlite").lexically_normal();
    seed_nonempty_ledger(path);
    const SqliteReplayLedgerResetState state =
        inspect_sqlite_replay_ledger_reset_state(path);
    const SqliteReplayLedgerResetRequest request =
        request_for(path, state, "focused-reset-postcommit-failure");
    const std::string receipt =
        sqlite_replay_ledger_reset_receipt_sha256(request);

    bool cutpoint_observed = false;
    bool typed_failure = false;
    try {
        (void)reset_sqlite_replay_ledger(
            request, fail_after_durable_reset_observation,
            &cutpoint_observed);
    } catch (const SqliteReplayLedgerResetDurableOutcomeError& error) {
        typed_failure = true;
        require(error.outcome() == SqliteReplayLedgerResetOutcome::Committed,
                "typed post-commit error lost committed outcome", checks);
        require(error.reset_receipt_sha256() == receipt,
                "typed post-commit error lost deterministic receipt", checks);
        require(exception_chain_contains(
                    error,
                    "focused injected post-commit verification failure"),
                "typed post-commit error lost its nested root cause", checks);
    }
    require(cutpoint_observed,
            "post-commit observer did not run after the durable outcome", checks);
    require(typed_failure,
            "post-commit failure was reported as an ordinary pre-commit error",
            checks);

    {
        Database database(path, SQLITE_OPEN_READWRITE);
        require(database.text(
                    "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;") ==
                    receipt,
                "typed post-commit failure did not leave durable receipt identity",
                checks);
        require(database.integer("SELECT count(*) FROM ledger_entries;") == 0,
                "typed post-commit failure did not leave committed empty state",
                checks);
    }
    const auto recovered = reset_sqlite_replay_ledger(request);
    require(recovered.outcome ==
                SqliteReplayLedgerResetOutcome::AlreadyCommitted,
            "typed post-commit failure was not recoverable by exact replay",
            checks);
    cleanup_family(path);
}

void test_commit_before_report_recovery(const fs::path& root,
                                        std::uint64_t& checks) {
    const fs::path path =
        fs::absolute(root / "crash-window.sqlite").lexically_normal();
    seed_nonempty_ledger(path);
    const SqliteReplayLedgerResetState state =
        inspect_sqlite_replay_ledger_reset_state(path);
    const SqliteReplayLedgerResetRequest request =
        request_for(path, state, "focused-reset-intent-crash-window");
    const std::string receipt =
        sqlite_replay_ledger_reset_receipt_sha256(request);

    auto child = spawn_focused_reset_helper(
        FocusedHelperAction::CommitBeforeReportLoss, path,
        "focused-reset-intent-crash-window", state.state_sha256, receipt);
    child.wait_for_exact_exit(0, 10s,
                              "commit-before-report-loss helper");
    require(!child.active(),
            "child did not commit reset before simulated report loss", checks);

    const auto recovered = reset_sqlite_replay_ledger(request);
    require(recovered.outcome ==
                SqliteReplayLedgerResetOutcome::AlreadyCommitted,
            "lost-report retry did not recover committed outcome", checks);
    require(recovered.reset_receipt_sha256 == receipt,
            "lost-report retry did not reproduce receipt", checks);
    require(inspect_sqlite_replay_ledger_reset_state(path).ledger_instance_id ==
                receipt,
            "lost-report recovery did not preserve receipt identity", checks);
    cleanup_family(path);
}

void test_exact_namespace_precondition(const fs::path& root,
                                       std::uint64_t& checks) {
    const fs::path path =
        fs::absolute(root / "namespace-bound.sqlite").lexically_normal();
    const fs::path replacement =
        fs::absolute(root / "namespace-replacement.sqlite").lexically_normal();
    const fs::path parked =
        fs::absolute(root / "namespace-parked.sqlite").lexically_normal();
    seed_nonempty_ledger(path);
    seed_nonempty_ledger(replacement);
    const SqliteReplayLedgerResetState inspected =
        inspect_sqlite_replay_ledger_reset_state(path);
    const SqliteReplayLedgerResetState replacement_state =
        inspect_sqlite_replay_ledger_reset_state(replacement);
    require(replacement_state.state_sha256 == inspected.state_sha256 &&
                replacement_state.ledger_instance_id ==
                    inspected.ledger_instance_id,
            "replacement fixture is not logically byte-equivalent evidence", checks);
    const SqliteReplayLedgerResetRequest request =
        request_for(path, inspected, "focused-reset-namespace-replacement");

    std::error_code error;
    fs::rename(path, parked, error);
    if (error) {
        throw std::runtime_error(
            "could not park original namespace fixture: " + error.message());
    }
    fs::rename(replacement, path, error);
    if (error) {
        throw std::runtime_error(
            "could not install replacement namespace fixture: " +
            error.message());
    }
    expect_rejection(
        [&] { (void)reset_sqlite_replay_ledger(request); },
        "namespace precondition mismatch", checks);
    require(inspect_sqlite_replay_ledger_reset_state(path).ledger_entry_rows == 1,
            "namespace-mismatched reset mutated replacement database", checks);
    cleanup_family(path);
    cleanup_family(parked);

    const fs::path missing_parent = root / "must-not-be-created";
    const fs::path missing_ledger = missing_parent / "ledger.sqlite";
    require(!fs::exists(missing_parent),
            "missing-parent fixture unexpectedly exists", checks);
    expect_rejection(
        [&] { (void)inspect_sqlite_replay_ledger_reset_state(missing_ledger); },
        "parent directory was not established", checks);
    require(!fs::exists(missing_parent),
            "reset-state inspection created an unauthorized parent directory",
            checks);
}

void test_bound_namespace_identity_recheck(const fs::path& root,
                                           std::uint64_t& checks) {
    const fs::path approved =
        fs::absolute(root / "bound-identity-approved.sqlite").lexically_normal();
    const fs::path replacement =
        fs::absolute(root / "bound-identity-replacement.sqlite").lexically_normal();
    const fs::path displaced =
        fs::absolute(root / "bound-identity-displaced.sqlite").lexically_normal();
    for (const auto& path : {approved, replacement, displaced}) cleanup_family(path);
    seed_nonempty_ledger(approved);
    seed_nonempty_ledger(replacement);

    auto guard = anonsync::guard_sqlite_path_family_or_throw(
        approved, false, {"-wal", "-shm", "-journal", ".write.lock"},
        "reset focused bound identity");
    const anonsync::SqlitePathIdentity original = guard.bound_path_identity_or_throw(
        "reset focused bound identity first observation");
    require(original.database_inode != 0,
            "bound path identity did not retain the approved database inode",
            checks);

    fs::rename(approved, displaced);
    fs::rename(replacement, approved);
    bool rejected = false;
    std::string reason;
    try {
        (void)guard.bound_path_identity_or_throw(
            "reset focused bound identity replacement observation");
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected,
            "bound path identity accepted a replaced database object", checks);
    require(reason.find("SQLite main database identity changed") !=
                std::string::npos,
            "bound path identity replacement returned the wrong rejection: " +
                reason,
            checks);

    cleanup_family(approved);
    cleanup_family(displaced);
}

void test_namespace_and_schema_rejections(const fs::path& root,
                                          std::uint64_t& checks) {
    const fs::path target =
        fs::absolute(root / "target.sqlite").lexically_normal();
    const fs::path alias =
        fs::absolute(root / "alias.sqlite").lexically_normal();
    seed_nonempty_ledger(target);
    std::error_code error;
    fs::create_symlink(target, alias, error);
    if (error) throw std::runtime_error("could not create focused symlink");
    expect_rejection(
        [&] { (void)inspect_sqlite_replay_ledger_reset_state(alias); },
        "symbolic-link", checks);
    fs::remove(alias, error);

    {
        Database database(target, SQLITE_OPEN_READWRITE);
        database.exec("CREATE TABLE unexpected_reset_authority(x TEXT);");
    }
    expect_rejection(
        [&] { (void)inspect_sqlite_replay_ledger_reset_state(target); },
        "exact schema rejected", checks);
    cleanup_family(target);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc >= 2 && std::string_view(argv[1]) == kFocusedHelperFlag) {
        return run_focused_reset_helper(argc, argv);
    }

    std::uint64_t checks = 0;
    fs::path root;
    try {
        if (argc == 3 && std::string_view(argv[1]) == "--seed-ledger") {
            const fs::path path = fs::absolute(argv[2]).lexically_normal();
            cleanup_family(path);
            seed_nonempty_ledger(path);
            std::cout << path.generic_string() << "\n";
            return 0;
        }
        if (argc == 3 &&
            std::string_view(argv[1]) == "--append-after-reset") {
            const fs::path path = fs::absolute(argv[2]).lexically_normal();
            append_after_reset(path);
            std::cout << path.generic_string() << "\n";
            return 0;
        }
        if (argc != 1) {
            throw std::runtime_error(
                "usage: anonsync_sqlite_replay_ledger_reset_test "
                "[--seed-ledger path | --append-after-reset path]");
        }
        char pattern[] = "/tmp/anonsync-sqlite-reset-XXXXXX";
        char* created = ::mkdtemp(pattern);
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
        root = fs::path(created);
        test_streaming_digest(checks);
        test_write_gate_scope_fences(root, checks);
        test_reset_protocol(root, checks);
        test_typed_postcommit_failure(root, checks);
        test_commit_before_report_recovery(root, checks);
        test_exact_namespace_precondition(root, checks);
        test_bound_namespace_identity_recheck(root, checks);
        test_namespace_and_schema_rejections(root, checks);
        std::error_code ignored;
        fs::remove_all(root, ignored);
        std::cout << "anonsync_sqlite_replay_ledger_reset_test checks="
                  << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        if (!root.empty()) {
            std::error_code ignored;
            fs::remove_all(root, ignored);
        }
        std::cerr << "anonsync_sqlite_replay_ledger_reset_test failure after "
                  << checks << " checks: " << error.what() << "\n";
        return 2;
    }
}
