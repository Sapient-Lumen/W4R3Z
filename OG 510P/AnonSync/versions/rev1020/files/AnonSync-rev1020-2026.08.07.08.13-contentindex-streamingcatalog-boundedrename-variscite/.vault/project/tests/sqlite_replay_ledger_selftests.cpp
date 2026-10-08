#include "anonsync_core_internal.hpp"
#include "inherited_test_process.hpp"
#include "anonsync_selftest_api.hpp"
#include "sqlite_exact_value.hpp"
#include "sqlite_replay_ledger_selftest_bridge.hpp"
#include "sqlite_replay_ledger_restore_lock.hpp"
#include "sqlite_replay_ledger_write_gate.hpp"
#include "sqlite_verification_budget.hpp"
#include "self_exec_test_process.hpp"

#include <sqlite3.h>

#include <charconv>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace anonsync {
namespace {

using namespace std::chrono_literals;

[[nodiscard]] int sqlite_open_flags_for_ledger() noexcept {
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    return flags;
}

void sqlite_close_best_effort(sqlite3*& db) noexcept {
    if (db != nullptr) (void)sqlite3_close_v2(db);
    db = nullptr;
}

void sqlite_close_or_throw(sqlite3*& db, const std::string& label) {
    if (db == nullptr) return;
    const int rc = sqlite3_close(db);
    if (rc != SQLITE_OK) {
        const std::string message = sqlite3_errmsg(db);
        (void)sqlite3_close_v2(db);
        db = nullptr;
        throw std::runtime_error(label + ": " + message);
    }
    db = nullptr;
}

[[nodiscard]] sqlite3* sqlite_open_or_throw(
    const std::string& path, int flags, const std::string& label) {
    sqlite3* db = nullptr;
    if (sqlite3_open_v2(path.c_str(), &db, flags, nullptr) != SQLITE_OK) {
        const std::string message =
            db != nullptr ? sqlite3_errmsg(db) : "sqlite open failed";
        sqlite_close_best_effort(db);
        throw std::runtime_error(label + ": " + message);
    }
    return db;
}

void sqlite_exec_or_throw(sqlite3* db,
                          const std::string& sql,
                          const std::string& label) {
    if (sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr) != SQLITE_OK) {
        throw std::runtime_error(label + ": " + sqlite3_errmsg(db));
    }
}

[[nodiscard]] long long sqlite_query_single_int64(
    sqlite3* db, const std::string& sql, const std::string& label) {
    sqlite3_stmt* statement = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &statement, nullptr) != SQLITE_OK) {
        throw std::runtime_error(label + " prepare: " + sqlite3_errmsg(db));
    }
    try {
        if (sqlite3_step(statement) != SQLITE_ROW) {
            throw std::runtime_error(label + " did not return one exact integer row");
        }
        const std::int64_t value = persistence::sqlite_exact_i64_or_throw(
            statement, 0, label + " exact integer row");
        if (sqlite3_step(statement) != SQLITE_DONE) {
            throw std::runtime_error(label + " returned more than one row");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            statement = nullptr;
            throw std::runtime_error(label + " finalize failed: " + sqlite3_errmsg(db));
        }
        statement = nullptr;
        return static_cast<long long>(value);
    } catch (...) {
        if (statement != nullptr) (void)sqlite3_finalize(statement);
        throw;
    }
}

[[nodiscard]] long long parse_helper_seconds_or_throw(std::string_view text) {
    long long seconds = 0;
    const auto result = std::from_chars(text.data(), text.data() + text.size(), seconds);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size() ||
        seconds < 1 || seconds > 30) {
        throw std::runtime_error(
            "sqlite replay-ledger self-exec helper seconds must be an exact integer in [1,30]");
    }
    return seconds;
}

[[nodiscard]] std::string normalized_absolute_helper_path_or_throw(
    std::string_view text) {
    if (text.empty() || text.size() > 4096U) {
        throw std::runtime_error(
            "sqlite replay-ledger self-exec helper path length is invalid");
    }
    const std::filesystem::path path{std::string(text)};
    if (!path.is_absolute() || path.lexically_normal() != path) {
        throw std::runtime_error(
            "sqlite replay-ledger self-exec helper path must be absolute and lexically normalized");
    }
    return path.string();
}

void wait_for_lock_owner_marker_or_throw(
    const std::string& marker_path,
    pid_t expected_process,
    std::chrono::milliseconds timeout,
    const std::string& label) {
    const std::string expected =
        "pid=" + std::to_string(static_cast<long long>(expected_process)) + "\n";
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
        std::ifstream input(marker_path, std::ios::binary);
        if (input) {
            const std::string observed(
                (std::istreambuf_iterator<char>(input)),
                std::istreambuf_iterator<char>());
            if (observed == expected) return;
        }
        std::this_thread::sleep_for(10ms);
    }
    throw std::runtime_error(
        label + " did not observe the exact lock-owner marker before deadline");
}



}  // namespace

int dispatch_sqlite_replay_ledger_self_exec_helper(int argc, char** argv) {
    constexpr std::string_view mode =
        "--anonsync-sqlite-replay-ledger-lock-holder-helper-v1";
    if (argc < 2 || argv == nullptr || argv[1] == nullptr ||
        std::string_view(argv[1]) != mode) {
        return kSqliteReplayLedgerSelfExecHelperNotMatched;
    }

    try {
        // This proof runs immediately after exec and before path parsing or
        // SQLite/filesystem authority is acquired.
        test::verify_self_exec_child_boundary_or_throw();
        if (argc != 5 || argv[2] == nullptr || argv[3] == nullptr ||
            argv[4] == nullptr) {
            throw std::runtime_error(
                "sqlite replay-ledger self-exec helper requires exact v1 argv");
        }
        const std::string action(argv[2]);
        const std::string path =
            normalized_absolute_helper_path_or_throw(argv[3]);
        const long long seconds = parse_helper_seconds_or_throw(argv[4]);
        if (action == "write-gate") {
            return run_sqlite_write_gate_holder(path, seconds);
        }
        if (action == "restore-lock") {
            return run_sqlite_restore_lock_holder(path, seconds);
        }
        throw std::runtime_error(
            "sqlite replay-ledger self-exec helper action is not recognized");
    } catch (const std::exception& e) {
        std::cerr << "sqlite replay-ledger self-exec helper failed: "
                  << e.what() << "\n";
        return 64;
    }
}

int run_ledger_sqlite_readonly_snapshot_verifier_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0625_readonly_snapshot_verifier_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + "-journal").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& kind, const std::string& op, const std::string& source, const std::string& id) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value(kind);
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("readonly-snapshot-verifier-digest");
        tc.o["cloud_event_source"] = json_string_value(source);
        tc.o["cloud_event_id"] = json_string_value(id);
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("readonly-snapshot-verifier-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string bad_snapshot = "/tmp/" + stem + "_bad_schema.sqlite";
    const std::string hidden_suffix_snapshot =
        "/tmp/" + stem + "_hidden_suffix.sqlite";
    const std::string fractional_count_snapshot =
        "/tmp/" + stem + "_fractional_count.sqlite";
    try {
        cleanup_path(source);
        cleanup_path(snapshot);
        cleanup_path(bad_snapshot);
        cleanup_path(hidden_suffix_snapshot);
        cleanup_path(fractional_count_snapshot);
        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, "batch");
        if (!backend->stage(make_tc("readonly-openapi", "openapi", "readonlyVerifierOpenapi", "", ""), make_claims("readonly-jti-1", "readonlyVerifierOpenapi"), "allow", reason)) {
            throw std::runtime_error("read-only snapshot verifier selftest openapi stage failed: " + reason);
        }
        if (!backend->stage(make_tc("readonly-async", "asyncapi", "readonlyVerifierAsync", "urn:anonsync:readonly", "event-1"), make_claims("readonly-jti-2", "readonlyVerifierAsync"), "accept", reason)) {
            throw std::runtime_error("read-only snapshot verifier selftest async stage failed: " + reason);
        }
        if (!backend->commit(reason)) throw std::runtime_error("read-only snapshot verifier selftest commit failed: " + reason);
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("read-only snapshot verifier selftest backup failed: " + reason);
        backend->close();

        if (std::filesystem::exists(snapshot + ".write.lock") || std::filesystem::exists(snapshot + ".restore.lock")) {
            failed++; std::cerr << "read-only snapshot verifier created mutable lock sidecars for valid snapshot\n";
        } else passed++;

        try {
            ReplayLedgerStats st = verify_sqlite_ledger_snapshot_readonly_for_selftest(snapshot, "read-only snapshot verifier selftest valid snapshot");
            if (st.durable_line_count == 2 && st.loaded_entries == 2 && st.durable_head_hash != "GENESIS" && st.sqlite_integrity_checks == 1 && st.sqlite_profile_checks == 1) passed++;
            else { failed++; std::cerr << "read-only snapshot verifier valid snapshot stats mismatch\n"; }
        } catch (const std::exception& e) {
            failed++; std::cerr << "read-only snapshot verifier rejected valid snapshot: " << e.what() << "\n";
        }
        if (std::filesystem::exists(snapshot + ".write.lock") || std::filesystem::exists(snapshot + ".restore.lock")) {
            failed++; std::cerr << "read-only snapshot verifier left mutable sidecars after direct verification\n";
        } else passed++;

        // The resource guard is not a decorative helper. A caller-tightened
        // row ceiling must fail through the production verifier with a typed,
        // value-free reason before the connection can continue scanning.
        try {
            (void)verify_sqlite_ledger_snapshot_readonly_with_row_limit_for_selftest(
                snapshot,
                "read-only snapshot verifier selftest tight row budget",
                1U);
            failed++;
            std::cerr << "read-only snapshot verifier ignored a tight row budget\n";
        } catch (const persistence::SqliteVerificationBudgetException& e) {
            if (e.failure() ==
                    persistence::SqliteVerificationBudgetFailure::row_limit &&
                e.observed() == 2U && e.limit() == 1U) {
                passed++;
            } else {
                failed++;
                std::cerr << "read-only snapshot verifier tight budget reason mismatch: "
                          << e.what() << "\n";
            }
        } catch (const std::exception& e) {
            failed++;
            std::cerr << "read-only snapshot verifier tight budget type mismatch: "
                      << e.what() << "\n";
        }

        // A report used to verify in one autocommit read transaction and then
        // project pending rows in another. Prove that a writer may commit in
        // between while the report remains pinned to the verified snapshot.
        try {
            const std::string fenced_report =
                sqlite_effect_pending_report_json_for_selftest(source, [&] {
                    sqlite3* writer = sqlite_open_or_throw(
                        source,
                        sqlite_open_flags_for_ledger(),
                        "pending report snapshot fence writer open failed");
                    try {
                        sqlite3_busy_timeout(writer, 1000);
                        sqlite_exec_or_throw(
                            writer,
                            "BEGIN IMMEDIATE; "
                            "DELETE FROM effect_outbox WHERE prepared_sequence=2; "
                            "COMMIT;",
                            "pending report snapshot fence writer commit failed");
                        sqlite_close_or_throw(
                            writer,
                            "pending report snapshot fence writer close failed");
                    } catch (...) {
                        sqlite_close_best_effort(writer);
                        throw;
                    }
                });
            const Json report = parse_json_text(fenced_report);
            sqlite3* current = sqlite_open_or_throw(
                source, SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX,
                "pending report snapshot fence current-state open failed");
            const long long current_outbox_rows = sqlite_query_single_int64(
                current, "SELECT count(*) FROM effect_outbox;",
                "pending report snapshot fence current-state count failed");
            sqlite_close_or_throw(
                current,
                "pending report snapshot fence current-state close failed");
            if (report.at("prepared_effect_count").integer(-1) == 2 &&
                report.at("pending_effect_count").integer(-1) == 2 &&
                current_outbox_rows == 1) {
                passed++;
            } else {
                failed++;
                std::cerr << "pending report did not preserve its verified read snapshot\n";
            }
        } catch (const std::exception& e) {
            failed++;
            std::cerr << "pending report snapshot fence proof failed: "
                      << e.what() << "\n";
        }

        // The byte identity recorded by a snapshot manifest covers one main
        // database file.  SQLite's normal read-only open can nevertheless
        // merge sibling WAL state.  Every portable-snapshot sidecar therefore
        // has to fail before any logical row is treated as verified evidence.
        for (const char* suffix : {"-wal", "-shm", "-journal"}) {
            write_file(snapshot + suffix,
                       "attacker-controlled unsigned SQLite sidecar\n");
            try {
                (void)verify_sqlite_ledger_snapshot_readonly_for_selftest(
                    snapshot,
                    "read-only snapshot verifier selftest sidecar exclusion");
                failed++;
                std::cerr << "read-only snapshot verifier accepted sidecar "
                          << suffix << "\n";
            } catch (const std::exception& e) {
                const std::string expected =
                    std::string("snapshot sidecar ") + suffix;
                if (std::string(e.what()).find(expected) != std::string::npos) {
                    passed++;
                } else {
                    failed++;
                    std::cerr
                        << "read-only snapshot verifier sidecar rejection reason mismatch: "
                        << e.what() << "\n";
                }
            }
            std::remove((snapshot + suffix).c_str());
        }

        // A SQLite TEXT value may contain an embedded NUL. The old C-string
        // decoder discarded every byte after that NUL, allowing uncommitted
        // suffix bytes to sit outside the replay hash chain while verification
        // recomputed the original prefix-only hash.
        std::filesystem::copy_file(
            snapshot,
            hidden_suffix_snapshot,
            std::filesystem::copy_options::overwrite_existing);
        sqlite3* hidden_db = sqlite_open_or_throw(
            hidden_suffix_snapshot,
            sqlite_open_flags_for_ledger(),
            "read-only snapshot verifier hidden-suffix open failed");
        sqlite_exec_or_throw(
            hidden_db,
            "UPDATE ledger_entries "
            "SET case_id = case_id || CAST(X'0068696464656e' AS TEXT) "
            "WHERE sequence=1;",
            "read-only snapshot verifier hidden-suffix injection failed");
        sqlite_close_or_throw(
            hidden_db,
            "read-only snapshot verifier hidden-suffix close failed");
        try {
            (void)verify_sqlite_ledger_snapshot_readonly_for_selftest(
                hidden_suffix_snapshot,
                "read-only snapshot verifier selftest hidden suffix");
            failed++;
            std::cerr << "read-only snapshot verifier accepted hash-chain text with a hidden NUL suffix\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("entry hash mismatch") !=
                std::string::npos) {
                passed++;
            } else {
                failed++;
                std::cerr << "read-only snapshot verifier hidden-suffix rejection reason mismatch: "
                          << e.what() << "\n";
            }
        }

        // SQLite's dynamic typing permits a REAL in this INTEGER-affinity
        // column, and its CHECK constraint still holds. column_i64()
        // used to truncate 2.75 to 2, laundering a non-integral durable value
        // into the expected row count.
        std::filesystem::copy_file(
            snapshot,
            fractional_count_snapshot,
            std::filesystem::copy_options::overwrite_existing);
        sqlite3* fractional_db = sqlite_open_or_throw(
            fractional_count_snapshot,
            sqlite_open_flags_for_ledger(),
            "read-only snapshot verifier fractional-count open failed");
        sqlite_exec_or_throw(
            fractional_db,
            "UPDATE metadata SET line_count=2.75 WHERE id=1;",
            "read-only snapshot verifier fractional-count injection failed");
        sqlite_close_or_throw(
            fractional_db,
            "read-only snapshot verifier fractional-count close failed");
        try {
            (void)verify_sqlite_ledger_snapshot_readonly_for_selftest(
                fractional_count_snapshot,
                "read-only snapshot verifier selftest fractional count");
            failed++;
            std::cerr << "read-only snapshot verifier accepted a fractional durable row count\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("wrong_storage_class") !=
                std::string::npos) {
                passed++;
            } else {
                failed++;
                std::cerr << "read-only snapshot verifier fractional-count rejection reason mismatch: "
                          << e.what() << "\n";
            }
        }

        std::filesystem::copy_file(snapshot, bad_snapshot, std::filesystem::copy_options::overwrite_existing);
        sqlite3* db = sqlite_open_or_throw(bad_snapshot, sqlite_open_flags_for_ledger(), "read-only snapshot verifier bad-schema open failed");
        sqlite_exec_or_throw(db, "CREATE VIEW anonsync_bad_view AS SELECT 1 AS x;", "read-only snapshot verifier bad-schema injection failed");
        sqlite_close_or_throw(db, "read-only snapshot verifier bad-schema close failed");
        try {
            (void)verify_sqlite_ledger_snapshot_readonly_for_selftest(bad_snapshot, "read-only snapshot verifier selftest bad schema");
            failed++; std::cerr << "read-only snapshot verifier accepted snapshot with unexpected schema view\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find(
                    "sqlite_replay_ledger_schema[unexpected_object]") !=
                std::string::npos) {
                passed++;
            } else {
                failed++;
                std::cerr << "read-only snapshot verifier bad-schema rejection reason mismatch: "
                          << e.what() << "\n";
            }
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "read-only snapshot verifier selftest exception: " << e.what() << "\n";
    }
    cleanup_path(source);
    cleanup_path(snapshot);
    cleanup_path(bad_snapshot);
    cleanup_path(hidden_suffix_snapshot);
    cleanup_path(fractional_count_snapshot);
    std::cout << "anonsync_core sqlite read-only snapshot verifier selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_ledger_sqlite_restore_prefix_continuity_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0619_restore_prefix_continuity_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + "-journal").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-prefix-continuity-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-prefix-continuity-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("restore prefix-continuity seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore prefix-continuity seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore prefix-continuity snapshot failed: " + reason);
        backend->close();
    };
    auto stats_for = [&](const std::string& path) {
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        ReplayLedgerStats st = backend->stats();
        backend->close();
        return st;
    };
    const std::string good_source = "/tmp/" + stem + "_good_source.sqlite";
    const std::string good_snapshot = "/tmp/" + stem + "_good_snapshot.sqlite";
    const std::string good_dst = "/tmp/" + stem + "_good_dst.sqlite";
    const std::string bad_source = "/tmp/" + stem + "_bad_source.sqlite";
    const std::string bad_snapshot = "/tmp/" + stem + "_bad_snapshot.sqlite";
    const std::string bad_dst = "/tmp/" + stem + "_bad_dst.sqlite";
    const std::string empty_dst = "/tmp/" + stem + "_empty_dst.sqlite";
    const std::string same_source = "/tmp/" + stem + "_same_source.sqlite";
    const std::string same_snapshot = "/tmp/" + stem + "_same_snapshot.sqlite";
    const std::string same_dst = "/tmp/" + stem + "_same_dst.sqlite";
    const std::string divergent_source = "/tmp/" + stem + "_divergent_source.sqlite";
    const std::string divergent_snapshot = "/tmp/" + stem + "_divergent_snapshot.sqlite";
    const std::string divergent_dst = "/tmp/" + stem + "_divergent_dst.sqlite";
    try {
        seed_ledger(good_source, {"prefix-a", "prefix-b", "prefix-c"}, "sqlite-prefix-op");
        seed_ledger(good_dst, {"prefix-a", "prefix-b"}, "sqlite-prefix-op");
        snapshot_from(good_source, good_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(good_snapshot, good_dst);
            ReplayLedgerStats st = stats_for(good_dst);
            if (st.durable_line_count == 3) passed++; else { failed++; std::cerr << "restore prefix-continuity good extension line_count mismatch\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity good extension failed: " << e.what() << "\n"; }

        seed_ledger(bad_source, {"other-a", "other-b", "other-c"}, "sqlite-prefix-op");
        seed_ledger(bad_dst, {"prefix-a", "prefix-b"}, "sqlite-prefix-op");
        snapshot_from(bad_source, bad_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(bad_snapshot, bad_dst);
            failed++; std::cerr << "restore prefix-continuity accepted non-extending newer snapshot\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("append-continuity guard") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore prefix-continuity rejection reason mismatch: " << e.what() << "\n"; }
        }

        try {
            cleanup_path(empty_dst);
            restore_sqlite_snapshot_into_ledger(bad_snapshot, empty_dst);
            ReplayLedgerStats st = stats_for(empty_dst);
            if (st.durable_line_count == 3) passed++; else { failed++; std::cerr << "restore prefix-continuity empty destination line_count mismatch\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity empty destination restore failed: " << e.what() << "\n"; }

        seed_ledger(same_source, {"same-a", "same-b"}, "sqlite-prefix-op");
        seed_ledger(same_dst, {"same-a", "same-b"}, "sqlite-prefix-op");
        snapshot_from(same_source, same_snapshot);
        try { restore_sqlite_snapshot_into_ledger(same_snapshot, same_dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore prefix-continuity idempotent same-head restore failed: " << e.what() << "\n"; }

        seed_ledger(divergent_source, {"div-a", "div-b"}, "sqlite-prefix-op");
        seed_ledger(divergent_dst, {"same-a", "same-b"}, "sqlite-prefix-op");
        snapshot_from(divergent_source, divergent_snapshot);
        try {
            restore_sqlite_snapshot_into_ledger(divergent_snapshot, divergent_dst);
            failed++; std::cerr << "restore prefix-continuity accepted divergent same-height restore\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("divergent same-height") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore prefix-continuity divergent same-height reason mismatch: " << e.what() << "\n"; }
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore prefix-continuity selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {good_source, good_snapshot, good_dst, bad_source, bad_snapshot, bad_dst, empty_dst, same_source, same_snapshot, same_dst, divergent_source, divergent_snapshot, divergent_dst}) cleanup_path(p);
    std::cout << "anonsync_core ledger sqlite restore prefix-continuity selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_sqlite_write_gate_holder(const std::string& ledger_path, long long seconds) {
    try {
        persistence::SqliteReplayLedgerWriteGate lock(ledger_path);
        std::cout << "anonsync_core sqlite write-gate holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sqlite write-gate holder failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_sqlite_restore_write_gate_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_write_gate_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + "-journal").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-write-gate-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-write-gate-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("restore write-gate seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore write-gate seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore write-gate snapshot failed: " + reason);
        backend->close();
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    const std::string dst_gate_locked = "/tmp/" + stem + "_dst_gate_locked.sqlite";
    const std::string dst_symlink = "/tmp/" + stem + "_dst_symlink.sqlite";
    const std::string dst_hardlink = "/tmp/" + stem + "_dst_hardlink.sqlite";
    const std::string dst_stale_gate = "/tmp/" + stem + "_dst_stale_gate.sqlite";
    const std::string fork_gate = "/tmp/" + stem + "_fork_gate.sqlite";
    const std::string fork_restore = "/tmp/" + stem + "_fork_restore.sqlite";
    const std::string target = "/tmp/" + stem + "_target.txt";
    try {
        seed_ledger(source, {"restore-write-gate-jti-1", "restore-write-gate-jti-2"}, "sqlite-restore-write-gate-op");
        snapshot_from(source, snapshot);
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore write-gate valid restore failed: " << e.what() << "\n"; }

        auto write_gate_holder = test::spawn_self_exec_test_process_or_throw(
            test::current_self_executable_or_throw(),
            {"--anonsync-sqlite-replay-ledger-lock-holder-helper-v1",
             "write-gate",
             std::filesystem::path(dst_gate_locked).lexically_normal().string(),
             "3"});
        wait_for_lock_owner_marker_or_throw(
            dst_gate_locked + ".write.lock",
            write_gate_holder.process_id(), 2500ms,
            "restore write-gate isolated holder");
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_gate_locked);
            failed++; std::cerr << "restore write-gate accepted restore while destination write gate was held\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("write-gate lock contention") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore write-gate contention reason mismatch: " << e.what() << "\n"; }
        }
        write_gate_holder.wait_for_exact_exit(
            0, 5s, "restore write-gate isolated holder");
        passed++;

        write_file(target, "target");
        std::remove((dst_symlink + ".write.lock").c_str());
        if (::symlink(target.c_str(), (dst_symlink + ".write.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_symlink);
                failed++; std::cerr << "restore write-gate accepted symbolic-link write gate sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("write-gate refuses symbolic-link") != std::string::npos ||
                    std::string(e.what()).find("refuses symbolic-link ledger or sidecar") != std::string::npos ||
                    std::string(e.what()).find("symbolic-link SQLite family member") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore write-gate symlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore write-gate could not create symlink\n"; }

        std::remove((dst_hardlink + ".write.lock").c_str());
        if (::link(target.c_str(), (dst_hardlink + ".write.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_hardlink);
                failed++; std::cerr << "restore write-gate accepted multiply-linked write gate sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("multiply-linked SQLite family member") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore write-gate hardlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore write-gate could not create hardlink\n"; }

        write_file(dst_stale_gate + ".write.lock", "stale regular write-gate file\n");
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_stale_gate);
            struct stat lock_status{};
            if (::stat((dst_stale_gate + ".write.lock").c_str(), &lock_status) == 0 &&
                (lock_status.st_mode & 0777) == 0600) passed++;
            else { failed++; std::cerr << "restore write-gate did not normalize stale lock permissions\n"; }
        }
        catch (const std::exception& e) { failed++; std::cerr << "restore write-gate rejected stale regular write-gate file: " << e.what() << "\n"; }

        {
            auto inherited_lock =
                std::make_unique<persistence::SqliteReplayLedgerWriteGate>(fork_gate);
            auto inherited_child = test::spawn_inherited_test_process_or_throw(
                [&] {
                    inherited_lock.reset();
                    return 97;
                },
                "restore write-gate inherited-destructor probe");
            const int inherited_status = inherited_child.wait_for_exit(
                5s, "restore write-gate inherited-destructor probe");
            const int inherited_exit =
                WIFEXITED(inherited_status)
                    ? WEXITSTATUS(inherited_status)
                    : (WIFSIGNALED(inherited_status)
                           ? 128 + WTERMSIG(inherited_status)
                           : -1);
            if (inherited_exit == kSyncProcessCapabilityViolationExitCode) {
                passed++;
            } else {
                failed++;
                std::cerr << "restore write-gate inherited destructor did not fail stop\n";
            }
        }

        {
            persistence::SqliteReplayLedgerWriteGate parent_lock(fork_gate);
            auto recursion_child = test::spawn_inherited_test_process_or_throw(
                [&] {
                    try {
                        persistence::SqliteReplayLedgerWriteGate child_lock(fork_gate);
                        return 98;
                    } catch (const std::exception& e) {
                        return std::string(e.what()).find(
                                   "write-gate lock contention") !=
                                       std::string::npos
                                   ? 0
                                   : 99;
                    }
                },
                "restore write-gate recursion-incarnation probe");
            const int recursion_status = recursion_child.wait_for_exit(
                5s, "restore write-gate recursion-incarnation probe");
            const int recursion_exit =
                WIFEXITED(recursion_status) ? WEXITSTATUS(recursion_status)
                                           : -1;
            if (recursion_exit == 0) {
                passed++;
            } else {
                failed++;
                std::cerr << "restore write-gate inherited recursion evidence "
                             "bypassed child-local lock acquisition\n";
            }
        }

        {
            auto inherited_lock =
                std::make_unique<persistence::SqliteReplayLedgerRestoreLock>(fork_restore);
            auto inherited_child = test::spawn_inherited_test_process_or_throw(
                [&] {
                    inherited_lock.reset();
                    return 97;
                },
                "restore-lock inherited-destructor probe");
            const int inherited_status = inherited_child.wait_for_exit(
                5s, "restore-lock inherited-destructor probe");
            const int inherited_exit =
                WIFEXITED(inherited_status)
                    ? WEXITSTATUS(inherited_status)
                    : (WIFSIGNALED(inherited_status)
                           ? 128 + WTERMSIG(inherited_status)
                           : -1);
            if (inherited_exit == kSyncProcessCapabilityViolationExitCode) {
                passed++;
            } else {
                failed++;
                std::cerr << "restore lock inherited destructor did not fail stop\n";
            }
        }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore write-gate selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source, snapshot, dst, dst_gate_locked, dst_symlink,
                          dst_hardlink, dst_stale_gate, fork_gate,
                          fork_restore}) {
        cleanup_path(p);
    }
    std::remove(target.c_str());
    std::cout << "anonsync_core ledger sqlite restore write-gate selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

int run_sqlite_restore_lock_holder(const std::string& ledger_path, long long seconds) {
    try {
        persistence::SqliteReplayLedgerRestoreLock lock(ledger_path);
        std::cout << "anonsync_core sqlite restore lock holder acquired " << ledger_path << " for " << seconds << " seconds\n" << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(seconds));
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sqlite restore lock holder failed: " << e.what() << "\n";
        return 1;
    }
}

int run_ledger_sqlite_restore_locking_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_locking_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + "-journal").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-lock-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-lock-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("restore locking seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore locking seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore locking snapshot failed: " + reason);
        backend->close();
    };
    const std::string source = "/tmp/" + stem + "_source.sqlite";
    const std::string snapshot = "/tmp/" + stem + "_snapshot.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    const std::string dst_locked = "/tmp/" + stem + "_dst_locked.sqlite";
    const std::string dst_symlink = "/tmp/" + stem + "_dst_symlink.sqlite";
    const std::string dst_hardlink = "/tmp/" + stem + "_dst_hardlink.sqlite";
    const std::string dst_stale_lock = "/tmp/" + stem + "_dst_stale.sqlite";
    const std::string target = "/tmp/" + stem + "_target.txt";
    try {
        seed_ledger(source, {"restore-lock-jti-1", "restore-lock-jti-2"}, "sqlite-restore-lock-op");
        snapshot_from(source, snapshot);
        try { restore_sqlite_snapshot_into_ledger(snapshot, dst); passed++; }
        catch (const std::exception& e) { failed++; std::cerr << "restore locking valid restore failed: " << e.what() << "\n"; }

        // Isolation probes execute a fresh image rather than performing C++
        // application work in a copied multithreaded process. Exact owner
        // markers replace scheduler-dependent sleeps as readiness evidence.
        auto restore_lock_holder = test::spawn_self_exec_test_process_or_throw(
            test::current_self_executable_or_throw(),
            {"--anonsync-sqlite-replay-ledger-lock-holder-helper-v1",
             "restore-lock",
             std::filesystem::path(dst_locked).lexically_normal().string(),
             "3"});
        wait_for_lock_owner_marker_or_throw(
            dst_locked + ".restore.lock",
            restore_lock_holder.process_id(), 2500ms,
            "restore-lock isolated holder");
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_locked);
            failed++; std::cerr << "restore locking accepted concurrent restore while lock holder was active\n";
        } catch (const std::exception& e) {
            if (std::string(e.what()).find("restore lock contention") != std::string::npos) passed++;
            else { failed++; std::cerr << "restore locking contention reason mismatch: " << e.what() << "\n"; }
        }
        restore_lock_holder.wait_for_exact_exit(
            0, 5s, "restore-lock isolated holder");
        passed++;

        write_file(target, "target");
        std::remove((dst_symlink + ".restore.lock").c_str());
        if (::symlink(target.c_str(), (dst_symlink + ".restore.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_symlink);
                failed++; std::cerr << "restore locking accepted symbolic-link restore lock sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("restore lock refuses symbolic-link") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore locking symlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore locking could not create lock symlink\n"; }

        std::remove((dst_hardlink + ".restore.lock").c_str());
        if (::link(target.c_str(), (dst_hardlink + ".restore.lock").c_str()) == 0) {
            try {
                restore_sqlite_snapshot_into_ledger(snapshot, dst_hardlink);
                failed++; std::cerr << "restore locking accepted multiply-linked restore lock sidecar\n";
            } catch (const std::exception& e) {
                if (std::string(e.what()).find("multiply-linked SQLite family member") != std::string::npos) passed++;
                else { failed++; std::cerr << "restore locking hardlink reason mismatch: " << e.what() << "\n"; }
            }
        } else { failed++; std::cerr << "restore locking could not create lock hardlink\n"; }

        write_file(dst_stale_lock + ".restore.lock", "stale regular lock file\n");
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, dst_stale_lock);
            struct stat lock_status{};
            if (::stat((dst_stale_lock + ".restore.lock").c_str(), &lock_status) == 0 &&
                (lock_status.st_mode & 0777) == 0600) passed++;
            else { failed++; std::cerr << "restore locking did not normalize stale lock permissions\n"; }
        }
        catch (const std::exception& e) { failed++; std::cerr << "restore locking rejected stale regular lock file: " << e.what() << "\n"; }
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore locking selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source, snapshot, dst, dst_locked, dst_symlink, dst_hardlink, dst_stale_lock}) cleanup_path(p);
    std::remove(target.c_str());
    std::cout << "anonsync_core ledger sqlite restore locking selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}



int run_ledger_sqlite_restore_manifest_binding_selftest() {
    int passed = 0;
    int failed = 0;
    const std::string stem = "anonsync_core_rev0616_restore_manifest_binding_" + std::to_string(static_cast<long long>(std::time(nullptr))) + "_" + std::to_string(static_cast<long long>(::getpid()));
    auto cleanup_path = [](const std::string& p) {
        std::remove(p.c_str());
        std::remove((p + "-wal").c_str());
        std::remove((p + "-shm").c_str());
        std::remove((p + "-journal").c_str());
        std::remove((p + ".restore.lock").c_str());
        std::remove((p + ".write.lock").c_str());
    };
    auto make_tc = [](const std::string& case_id, const std::string& op) {
        Json tc; tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value(case_id);
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value(op);
        tc.o["contract_digest_sha256"] = json_string_value("sqlite-restore-manifest-binding-digest");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");
        return tc;
    };
    auto make_claims = [](const std::string& jti, const std::string& op) {
        Json claims; claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value(op);
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("sqlite-restore-manifest-binding-digest"));
        claims.o["jti"] = json_string_value(jti);
        return claims;
    };
    auto seed_ledger = [&](const std::string& path, const std::vector<std::string>& jtis, const std::string& op) {
        std::string reason;
        cleanup_path(path);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        for (size_t i = 0; i < jtis.size(); ++i) {
            if (!backend->stage(make_tc("case-" + std::to_string(i + 1), op), make_claims(jtis[i], op), "allow", reason)) {
                throw std::runtime_error("restore manifest binding seed stage failed: " + reason);
            }
        }
        if (!backend->commit(reason)) throw std::runtime_error("restore manifest binding seed commit failed: " + reason);
        backend->close();
    };
    auto snapshot_from = [&](const std::string& source, const std::string& snapshot) {
        std::string reason;
        cleanup_path(snapshot);
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, "batch");
        if (!backend->backup_snapshot(snapshot, reason)) throw std::runtime_error("restore manifest binding snapshot failed: " + reason);
        backend->close();
    };
    auto stats_for = [&](const std::string& path) {
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        ReplayLedgerStats st = backend->stats();
        backend->close();
        return st;
    };
    auto expected_for = [&](const std::string& snapshot) {
        // Snapshot evidence is never opened through the mutable WAL backend to
        // compute its own signed summary. That path changes page-1 format bytes
        // before authority is checked. Consume the same sealed, namespace-free
        // read-only verifier used by production restore.
        ReplayLedgerStats st = verify_sqlite_ledger_snapshot_readonly_for_selftest(
            snapshot,
            "restore manifest binding expected snapshot read-only verifier");
        SqliteSnapshotManifestVerification v;
        v.line_count = st.durable_line_count;
        v.head_hash = st.durable_head_hash;
        v.snapshot_sha256 = sha256_hex(read_file(snapshot));
        v.signer_kid = "rev0616-selftest-restore-root";
        return v;
    };
    auto expect_reject = [&](const std::string& label, const std::string& snapshot, const std::string& dst, const SqliteSnapshotManifestVerification& expected) {
        cleanup_path(dst);
        try {
            restore_sqlite_snapshot_into_ledger_verified(snapshot, dst, expected);
            failed++; std::cerr << "restore manifest binding accepted hostile case " << label << "\n";
        } catch (const std::exception&) { passed++; }
    };
    auto expect_accept = [&](const std::string& label, const std::string& snapshot, const std::string& dst, const SqliteSnapshotManifestVerification& expected, long long rows) {
        cleanup_path(dst);
        try {
            restore_sqlite_snapshot_into_ledger_verified(snapshot, dst, expected);
            ReplayLedgerStats st = stats_for(dst);
            if (st.durable_line_count == rows && st.durable_head_hash == expected.head_hash) passed++;
            else { failed++; std::cerr << "restore manifest binding accepted " << label << " but restored wrong state\n"; }
        } catch (const std::exception& e) { failed++; std::cerr << "restore manifest binding rejected valid case " << label << ": " << e.what() << "\n"; }
    };
    const std::string source1 = "/tmp/" + stem + "_source1.sqlite";
    const std::string source2 = "/tmp/" + stem + "_source2.sqlite";
    const std::string snapshot1 = "/tmp/" + stem + "_snapshot1.sqlite";
    const std::string snapshot2 = "/tmp/" + stem + "_snapshot2.sqlite";
    const std::string dst = "/tmp/" + stem + "_dst.sqlite";
    try {
        seed_ledger(source1, {"restore-manifest-jti-1", "restore-manifest-jti-2"}, "sqlite-restore-manifest-op-a");
        seed_ledger(source2, {"restore-manifest-jti-3", "restore-manifest-jti-4", "restore-manifest-jti-5"}, "sqlite-restore-manifest-op-b");
        snapshot_from(source1, snapshot1);
        snapshot_from(source2, snapshot2);
        SqliteSnapshotManifestVerification expected1 = expected_for(snapshot1);
        SqliteSnapshotManifestVerification expected2 = expected_for(snapshot2);
        expect_accept("valid manifest-bound restore", snapshot1, dst, expected1, 2);

        auto bad_digest = expected1;
        bad_digest.snapshot_sha256 = std::string(64, '0');
        expect_reject("wrong snapshot digest", snapshot1, dst, bad_digest);

        auto bad_head = expected1;
        bad_head.head_hash = std::string(64, '1');
        expect_reject("wrong snapshot head", snapshot1, dst, bad_head);

        auto bad_count = expected1;
        bad_count.line_count = expected1.line_count + 1;
        expect_reject("wrong snapshot line count", snapshot1, dst, bad_count);

        cleanup_path(snapshot1);
        std::filesystem::copy_file(snapshot2, snapshot1, std::filesystem::copy_options::overwrite_existing);
        expect_reject("source path swapped after manifest verification", snapshot1, dst, expected1);
        expect_accept("valid manifest-bound restore after recomputing expected summary", snapshot1, dst, expected2, 3);
    } catch (const std::exception& e) {
        failed++; std::cerr << "ledger sqlite restore manifest binding selftest exception: " << e.what() << "\n";
    }
    for (const auto& p : {source1, source2, snapshot1, snapshot2, dst}) cleanup_path(p);
    std::cout << "anonsync_core ledger sqlite restore manifest binding selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}


}  // namespace anonsync
