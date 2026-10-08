#include "sync_sqlite_manifest_chunk_subset.hpp"

#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

namespace {

using anonsync::SyncChunkRange;
using anonsync::SyncSqliteDb;
using anonsync::SyncSqliteManifestChunkSubsetEvidence;
using anonsync::SyncSqliteManifestChunkSubsetLimits;
using anonsync::SyncSqliteManifestChunkSubsetVerifier;

static_assert(!std::is_copy_constructible_v<
              SyncSqliteManifestChunkSubsetVerifier>);
static_assert(!std::is_copy_assignable_v<
              SyncSqliteManifestChunkSubsetVerifier>);
static_assert(!std::is_move_constructible_v<
              SyncSqliteManifestChunkSubsetVerifier>);
static_assert(!std::is_move_assignable_v<
              SyncSqliteManifestChunkSubsetVerifier>);

std::uint64_t checks = 0;

[[noreturn]] void fail(const std::string& message) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(1);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Fn>
void require_error(Fn&& fn,
                   std::string_view expected_fragment,
                   const std::string& message) {
    try {
        std::forward<Fn>(fn)();
    } catch (const std::exception& error) {
        require(std::string_view(error.what()).find(expected_fragment) !=
                    std::string_view::npos,
                message + " returned unexpected error: " + error.what());
        return;
    }
    fail(message + " did not reject");
}

SyncSqliteDb open_memory_database() {
    SyncSqliteDb owner;
    const int rc = sqlite3_open_v2(
        ":memory:", owner.db.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX |
            SQLITE_OPEN_PRIVATECACHE,
        nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "manifest subset test could not open database"));
    }
    return owner;
}

void exec(SyncSqliteDb& db, const std::string& sql) {
    anonsync::sqlite_exec_or_throw(
        db.db, sql, "manifest subset test SQL");
}

SyncSqliteManifestChunkSubsetLimits generous_limits() {
    return {
        .max_manifest_rows = 16,
        .max_required_rows = 8,
        .max_required_metadata_bytes =
            8 * anonsync::kSyncManifestChunkSubsetEvidenceBytesPerRow,
        .max_required_chunk_bytes = 64,
    };
}

const std::string kHashA(64, 'a');
const std::string kHashB(64, 'b');
const std::string kHashC(64, 'c');

std::vector<SyncChunkRange> full_chunks() {
    return {
        {0, 3, kHashA},
        {3, 2, kHashB},
        {5, 4, kHashC},
    };
}

SyncSqliteManifestChunkSubsetEvidence verify(
    SyncSqliteManifestChunkSubsetVerifier& verifier,
    std::span<const SyncChunkRange> chunks,
    SyncSqliteManifestChunkSubsetLimits limits = generous_limits(),
    std::uint64_t file_size = 9,
    std::uint64_t expected_rows = 3) {
    return verifier.verify_source_chunks_or_throw(
        "session-a", "docs/file.bin", file_size, expected_rows, chunks,
        limits, "manifest subset test");
}

}  // namespace

int main() {
    try {
        SyncSqliteDb db = open_memory_database();
        exec(db,
             "CREATE TABLE main.sync_session_manifest_chunks("
             "session_id, role, path, chunk_offset, chunk_length, "
             "chunk_sha256, chunk_index);"
             "INSERT INTO main.sync_session_manifest_chunks VALUES"
             "('session-a','source','docs/file.bin',0,3,'" + kHashA + "',0),"
             "('session-a','source','docs/file.bin',3,2,'" + kHashB + "',1),"
             "('session-a','source','docs/file.bin',5,4,'" + kHashC + "',2),"
             "('session-a','destination','docs/file.bin',0,999,'" + kHashC + "',99),"
             "('session-b','source','docs/file.bin',0,999,'" + kHashC + "',99);"
             "CREATE TEMP TABLE sync_session_manifest_chunks("
             "session_id, role, path, chunk_offset, chunk_length, "
             "chunk_sha256, chunk_index);"
             "INSERT INTO temp.sync_session_manifest_chunks VALUES"
             "('session-a','source','docs/file.bin',0,999,'" + kHashC + "',99);");

        SyncSqliteManifestChunkSubsetVerifier verifier(
            db.db, "manifest subset test owner");
        require(verifier.owner_generation() == db.db.generation(),
                "owner pins the exact database generation");

        const std::vector<SyncChunkRange> all = full_chunks();
        const SyncSqliteManifestChunkSubsetEvidence all_evidence =
            verify(verifier, all);
        require(all_evidence.expected_manifest_rows == 3 &&
                    all_evidence.required_rows == 3 &&
                    all_evidence.required_metadata_bytes ==
                        3 * anonsync::kSyncManifestChunkSubsetEvidenceBytesPerRow &&
                    all_evidence.required_chunk_bytes == 9 &&
                    all_evidence.first_manifest_chunk_index == 0 &&
                    all_evidence.last_manifest_chunk_index == 2,
                "complete selected subset returns exact bounded evidence");

        const std::vector<SyncChunkRange> sparse{all.front(), all.back()};
        const auto sparse_evidence = verify(verifier, sparse);
        require(sparse_evidence.required_rows == 2 &&
                    sparse_evidence.required_chunk_bytes == 7 &&
                    sparse_evidence.first_manifest_chunk_index == 0 &&
                    sparse_evidence.last_manifest_chunk_index == 2,
                "sparse ordered subset uses point probes without full materialization");
        require(sparse_evidence.required_chunk_bytes != 999,
                "explicit main binding ignores malicious TEMP shadow evidence");

        require(
            anonsync::sync_manifest_chunk_subset_metadata_bytes_or_throw(
                2, "metadata test") ==
                2 * anonsync::kSyncManifestChunkSubsetEvidenceBytesPerRow,
            "metadata accounting is exact");
        require_error(
            [] {
                (void)anonsync::
                    sync_manifest_chunk_subset_metadata_bytes_or_throw(
                        std::numeric_limits<std::uint64_t>::max() /
                                anonsync::kSyncManifestChunkSubsetEvidenceBytesPerRow +
                            1,
                        "metadata test");
            },
            "overflow", "metadata accounting rejects uint64 overflow");

        SyncSqliteManifestChunkSubsetLimits limits = generous_limits();
        limits.max_manifest_rows = 0;
        require_error([&] { (void)verify(verifier, all, limits); },
                      "must be positive", "zero manifest limit is rejected");
        limits = generous_limits();
        limits.max_required_rows = limits.max_manifest_rows + 1;
        require_error([&] { (void)verify(verifier, all, limits); },
                      "required-row limit", "incoherent row limits are rejected");
        require_error(
            [&] {
                (void)verifier.verify_source_chunks_or_throw(
                    "SESSION-A", "docs/file.bin", 9, 3, all,
                    generous_limits(), "manifest subset test");
            },
            "session id", "invalid session namespace is rejected");
        require_error(
            [&] {
                (void)verifier.verify_source_chunks_or_throw(
                    "session-a", "docs/../secret", 9, 3, all,
                    generous_limits(), "manifest subset test");
            },
            "path is invalid", "invalid relative path is rejected");
        require_error([&] { (void)verify(verifier, all, generous_limits(), 0); },
                      "nonempty file", "zero file size is rejected");
        require_error([&] { (void)verify(verifier, all, generous_limits(), 9, 0); },
                      "must be positive", "zero expected row count is rejected");
        require_error([&] { (void)verify(verifier, all, generous_limits(), 9, 17); },
                      "exceeds its limit", "manifest row ceiling is enforced");
        const std::vector<SyncChunkRange> empty;
        require_error([&] { (void)verify(verifier, empty); }, "must not be empty",
                      "empty selected subset is rejected");
        limits = generous_limits();
        limits.max_required_rows = 2;
        require_error([&] { (void)verify(verifier, all, limits); },
                      "count exceeds", "selected row ceiling is enforced");
        limits = generous_limits();
        limits.max_required_metadata_bytes =
            3 * anonsync::kSyncManifestChunkSubsetEvidenceBytesPerRow - 1;
        require_error([&] { (void)verify(verifier, all, limits); },
                      "metadata exceeds", "selected metadata ceiling is enforced");
        limits = generous_limits();
        limits.max_required_chunk_bytes = 8;
        require_error([&] { (void)verify(verifier, all, limits); },
                      "bytes exceed", "selected payload ceiling is enforced");
        require_error([&] { (void)verify(verifier, all, generous_limits(), 9, 2); },
                      "count exceeds expected", "selected rows cannot exceed frozen row count");

        std::vector<SyncChunkRange> malformed = all;
        malformed[1].length = 0;
        require_error([&] { (void)verify(verifier, malformed); },
                      "length must be positive", "zero-length chunk is rejected");
        malformed = all;
        malformed[1].sha256[0] = 'A';
        require_error([&] { (void)verify(verifier, malformed); },
                      "SHA-256", "noncanonical hash is rejected");
        malformed = all;
        malformed[1].offset =
            static_cast<std::uint64_t>(
                std::numeric_limits<sqlite3_int64>::max()) + 1;
        malformed[1].length = 1;
        require_error([&] {
                          (void)verify(verifier, malformed, generous_limits(),
                                       std::numeric_limits<std::uint64_t>::max());
                      },
                      "SQLite integer range", "unrepresentable point key is rejected in preflight");
        const std::vector<SyncChunkRange> unrepresentable_length{{
            0,
            static_cast<std::uint64_t>(
                std::numeric_limits<sqlite3_int64>::max()) + 1,
            kHashA,
        }};
        limits = generous_limits();
        limits.max_required_chunk_bytes =
            std::numeric_limits<std::uint64_t>::max();
        require_error(
            [&] {
                (void)verify(
                    verifier, unrepresentable_length, limits,
                    std::numeric_limits<std::uint64_t>::max(), 1);
            },
            "length exceeds SQLite integer range",
            "unrepresentable stored length is rejected in preflight");
        malformed = all;
        malformed[1].offset = static_cast<std::uint64_t>(
            std::numeric_limits<sqlite3_int64>::max());
        malformed[1].length =
            std::numeric_limits<std::uint64_t>::max() - malformed[1].offset + 1;
        require_error([&] {
                          (void)verify(verifier, malformed, generous_limits(),
                                       std::numeric_limits<std::uint64_t>::max());
                      },
                      "overflows", "chunk-end overflow is rejected");
        malformed = all;
        malformed.back().length = 5;
        require_error([&] { (void)verify(verifier, malformed); },
                      "file size", "out-of-file chunk is rejected");
        malformed = all;
        malformed[1].offset = 2;
        malformed[1].length = 3;
        require_error([&] { (void)verify(verifier, malformed); },
                      "overlap", "overlapping selected chunks are rejected");

        exec(db,
             "DELETE FROM main.sync_session_manifest_chunks "
             "WHERE session_id='session-a' AND role='source' AND path='docs/file.bin' AND chunk_offset=3;");
        require_error([&] { (void)verify(verifier, all); }, "absent",
                      "missing selected row is rejected");
        exec(db, "INSERT INTO main.sync_session_manifest_chunks VALUES"
                 "('session-a','source','docs/file.bin',3,2,'" + kHashB + "',1);");
        require(verify(verifier, all).required_rows == 3,
                "statement is reusable after missing-row rejection");

        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_length=7 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");
        require_error([&] { (void)verify(verifier, all); }, "exactly match",
                      "persisted length mismatch is rejected");
        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_length=2 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");

        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_sha256='" +
                 kHashA + "' WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");
        require_error([&] { (void)verify(verifier, all); }, "exactly match",
                      "persisted hash mismatch is rejected");
        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_sha256='" +
                 kHashB + "' WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");

        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_length='2' "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");
        require_error([&] { (void)verify(verifier, all); }, "wrong_storage_class",
                      "TEXT integer is rejected by exact decoding");
        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_length=2 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=3;");

        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_index=3 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=5;");
        require_error([&] { (void)verify(verifier, all); }, "exceeds expected",
                      "stored ordinal outside frozen row count is rejected");
        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_index=0 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=5;");
        require_error([&] { (void)verify(verifier, all); }, "strictly increasing",
                      "nonmonotone stored ordinals are rejected");
        exec(db,
             "UPDATE main.sync_session_manifest_chunks SET chunk_index=2 "
             "WHERE session_id='session-a' AND role='source' AND chunk_offset=5;");

        exec(db, "INSERT INTO main.sync_session_manifest_chunks VALUES"
                 "('session-a','source','docs/file.bin',3,2,'" + kHashB + "',1);");
        require_error([&] { (void)verify(verifier, all); }, "not unique",
                      "duplicate point evidence is rejected after bounded sentinel row");
        exec(db,
             "DELETE FROM main.sync_session_manifest_chunks WHERE rowid IN ("
             "SELECT rowid FROM main.sync_session_manifest_chunks "
             "WHERE session_id='session-a' AND role='source' AND path='docs/file.bin' "
             "AND chunk_offset=3 ORDER BY rowid DESC LIMIT 1);");
        require(verify(verifier, sparse).required_rows == 2,
                "owner remains reusable after duplicate-row rejection");

        std::cout << "sync sqlite manifest chunk subset checks: " << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: unexpected exception: " << error.what() << '\n';
        return 1;
    }
}
