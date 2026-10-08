#include "anonsync_core_internal.hpp"
#include "persistence/local_jsonl_replay_publication.hpp"

#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

#if !defined(_WIN32)
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using anonsync::Json;
using anonsync::ReplayLedger;
using anonsync::json_string_value;
using anonsync::sha256_hex;
using anonsync::persistence::kLocalJsonlReplayJournalV3Format;
using anonsync::persistence::kLocalJsonlReplayV3CommitProtocol;

struct TestState final {
    std::uint64_t passed = 0;

    void require(bool condition, const std::string& label) {
        if (!condition) throw std::runtime_error(label);
        ++passed;
    }
};

class TemporaryTree final {
public:
    TemporaryTree() {
#if !defined(_WIN32)
        path_ = fs::temp_directory_path() /
                ("anonsync-local-jsonl-crash-state-" +
                 std::to_string(static_cast<long long>(::getpid())) + "-" +
                 std::to_string(static_cast<long long>(
                     std::chrono::steady_clock::now()
                         .time_since_epoch()
                         .count())));
#else
        path_ = fs::temp_directory_path() / "anonsync-local-jsonl-crash-state";
#endif
        fs::create_directories(path_);
    }

    ~TemporaryTree() {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

class FaultEnvironmentGuard final {
public:
    explicit FaultEnvironmentGuard(std::string_view checkpoint) {
#if !defined(_WIN32)
        if (::setenv("ANONSYNC_LEDGER_FAULT_AT",
                     std::string(checkpoint).c_str(), 1) != 0) {
            throw std::runtime_error("could not set crash checkpoint");
        }
#else
        (void)checkpoint;
#endif
    }

    ~FaultEnvironmentGuard() {
#if !defined(_WIN32)
        (void)::unsetenv("ANONSYNC_LEDGER_FAULT_AT");
#endif
    }
};

Json make_case(const std::string& case_id) {
    Json value;
    value.type = Json::Type::Object;
    value.o["case_id"] = json_string_value(case_id);
    value.o["kind"] = json_string_value("openapi");
    value.o["cloud_event_source"] = json_string_value("");
    value.o["cloud_event_id"] = json_string_value("");
    return value;
}

Json make_claims(const std::string& jti) {
    Json value;
    value.type = Json::Type::Object;
    value.o["operation_id"] = json_string_value("objects.publish");
    value.o["contract_digest_sha256"] =
        json_string_value(sha256_hex("contract"));
    value.o["jti"] = json_string_value(jti);
    return value;
}

std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("could not read fixture: " +
                                 path.generic_string());
    }
    return std::string(std::istreambuf_iterator<char>(input),
                       std::istreambuf_iterator<char>());
}

void write_bytes(const fs::path& path, const std::string& bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("could not create fixture: " +
                                 path.generic_string());
    }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) {
        throw std::runtime_error("could not publish fixture: " +
                                 path.generic_string());
    }
}

void seed_one(const fs::path& ledger_path) {
    ReplayLedger ledger;
    ledger.load(ledger_path.generic_string(), "immediate");
    std::string reason;
    if (!ledger.append(make_case("seed-case"), make_claims("seed-jti"),
                       "allow", reason)) {
        throw std::runtime_error("seed append rejected: " + reason);
    }
}

void inject_append(const fs::path& ledger_path,
                   std::string_view checkpoint,
                   const std::string& jti) {
    FaultEnvironmentGuard fault(checkpoint);
    try {
        ReplayLedger ledger;
        ledger.load(ledger_path.generic_string(), "immediate");
        std::string reason;
        const bool appended = ledger.append(
            make_case("fault-" + jti), make_claims(jti), "allow", reason);
        throw std::runtime_error(
            "checkpoint did not interrupt append: " +
            std::string(checkpoint) + "; append_result=" +
            (appended ? "true" : "false") + "; reason=" + reason);
    } catch (const std::exception& error) {
        const std::string message = error.what();
        if (message.find("simulated durable replay ledger crash at checkpoint ") !=
            std::string::npos) {
            return;
        }
        throw;
    }
}

std::vector<fs::path> temporary_residue_paths(
    const fs::path& ledger_path) {
    const std::string prefix = ledger_path.filename().string() + ".tmp.";
    std::vector<fs::path> residues;
    std::error_code error;
    for (const auto& entry :
         fs::directory_iterator(ledger_path.parent_path(), error)) {
        if (error) break;
        const std::string name = entry.path().filename().string();
        if (name.starts_with(prefix)) residues.push_back(entry.path());
    }
    if (error) {
        throw std::runtime_error("could not enumerate temporary residues: " +
                                 error.message());
    }
    return residues;
}

bool has_temporary_residue(const fs::path& ledger_path) {
    return !temporary_residue_paths(ledger_path).empty();
}

fs::path require_single_temporary_residue(const fs::path& ledger_path,
                                          std::string_view label) {
    const auto residues = temporary_residue_paths(ledger_path);
    if (residues.size() != 1U) {
        throw std::runtime_error(std::string(label) +
                                 " expected exactly one temporary residue");
    }
    return residues.front();
}

void test_journal_staging_rollback(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    seed_one(ledger_path);
    inject_append(ledger_path,
                  "after-journal-stage-fsync-before-publication",
                  "stage-jti");

    const fs::path staging_path =
        ledger_path.string() + ".journal.stage";
    test.require(fs::exists(staging_path) &&
                     !fs::exists(ledger_path.string() + ".journal"),
                 "pre-publication crash exposed only the reserved staging name");
    // Model a crash at an arbitrary instruction during the write rather than
    // only the deterministic post-fsync checkpoint. Startup must not parse or
    // trust a staging object that was never atomically promoted to journal.
    write_bytes(staging_path, "{partial-journal");

    ReplayLedger reload;
    reload.load(ledger_path.generic_string(), "immediate");
    test.require(reload.loaded_entries == 1 &&
                     reload.contains_jti("seed-jti") &&
                     !reload.contains_jti("stage-jti"),
                 "partial journal staging rollback retained previous ledger");
    test.require(reload.journal_rolled_back_before_commit == 1 &&
                     reload.journal_recovered_after_commit == 0 &&
                     reload.journal_rejections == 0,
                 "partial journal staging rollback was classified cleanly");
    test.require(fs::exists(staging_path) &&
                     read_bytes(staging_path) == "{partial-journal" &&
                     !fs::exists(ledger_path.string() + ".journal") &&
                     has_temporary_residue(ledger_path),
                 "partial journal staging and unbound temporary remained operator evidence");
}

void test_linked_journal_publication_completion(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    seed_one(ledger_path);
    inject_append(ledger_path,
                  "after-journal-stage-fsync-before-publication",
                  "linked-jti");

    const fs::path staging_path =
        ledger_path.string() + ".journal.stage";
    const fs::path journal_path = ledger_path.string() + ".journal";
    fs::create_hard_link(staging_path, journal_path);
    struct stat staging_status {};
    struct stat journal_status {};
    test.require(::lstat(staging_path.c_str(), &staging_status) == 0 &&
                     ::lstat(journal_path.c_str(), &journal_status) == 0 &&
                     staging_status.st_dev == journal_status.st_dev &&
                     staging_status.st_ino == journal_status.st_ino &&
                     staging_status.st_nlink == 2,
                 "fixture modeled the crash window between journal link and staging unlink");

    ReplayLedger reload;
    reload.load(ledger_path.generic_string(), "immediate");
    test.require(reload.loaded_entries == 1 &&
                     reload.contains_jti("seed-jti") &&
                     !reload.contains_jti("linked-jti"),
                 "linked journal publication recovered the exact previous ledger state");
    test.require(reload.journal_rolled_back_before_commit == 1 &&
                     reload.journal_recovered_after_commit == 0 &&
                     reload.journal_rejections == 0,
                 "linked journal publication completed and then rolled back cleanly");
    test.require(!fs::exists(staging_path) && !fs::exists(journal_path) &&
                     !has_temporary_residue(ledger_path),
                 "linked journal recovery retired both publication names");
}

void test_precommit_rollback_frontiers(TestState& test) {
    const std::vector<std::string> checkpoints{
        "after-journal-fsync-before-directory-fsync",
        "after-journal-directory-fsync",
        "after-journal-fsync",
    };
    for (const std::string& checkpoint : checkpoints) {
        TemporaryTree tree;
        const fs::path ledger_path = tree.path() / "ledger.jsonl";
        seed_one(ledger_path);
        const std::string fault_jti = "fault-" + checkpoint;
        inject_append(ledger_path, checkpoint, fault_jti);

        test.require(fs::exists(ledger_path.string() + ".journal"),
                     checkpoint + " retained a recovery witness");
        const std::string journal =
            read_bytes(ledger_path.string() + ".journal");
        test.require(journal.find(std::string(kLocalJsonlReplayJournalV3Format)) !=
                         std::string::npos &&
                         journal.find(std::string(kLocalJsonlReplayV3CommitProtocol)) !=
                             std::string::npos &&
                         journal.find("\"previous_payload_sha256\"") !=
                             std::string::npos &&
                         journal.find("\"temporary_name\"") !=
                             std::string::npos,
                     checkpoint + " minted one complete v3 witness");

        ReplayLedger reload;
        reload.load(ledger_path.generic_string(), "immediate");
        test.require(reload.loaded_entries == 1 &&
                         reload.contains_jti("seed-jti") &&
                         !reload.contains_jti(fault_jti),
                     checkpoint + " selected the exact previous state");
        test.require(reload.journal_rolled_back_before_commit == 1 &&
                         reload.journal_recovered_after_commit == 0 &&
                         reload.journal_rejections == 0,
                     checkpoint + " recorded one clean rollback");
        test.require(!fs::exists(ledger_path.string() + ".journal") &&
                         !has_temporary_residue(ledger_path),
                     checkpoint + " retired journal and intended temporary");
    }
}

void test_prejournal_temporary_frontiers(TestState& test) {
    const std::vector<std::string> checkpoints{
        "after-temp-create-before-write",
        "after-temp-fsync",
    };
    for (const std::string& checkpoint : checkpoints) {
        TemporaryTree tree;
        const fs::path ledger_path = tree.path() / "ledger.jsonl";
        seed_one(ledger_path);
        const std::string fault_jti = "fault-" + checkpoint;
        inject_append(ledger_path, checkpoint, fault_jti);

        const fs::path residue = require_single_temporary_residue(
            ledger_path, checkpoint);
        test.require(!fs::exists(ledger_path.string() + ".journal") &&
                         !fs::exists(ledger_path.string() + ".journal.stage"),
                     checkpoint +
                         " exposed no recovery witness before complete temporary authority");
        const std::string residue_bytes = read_bytes(residue);
        test.require(
            checkpoint == "after-temp-create-before-write"
                ? residue_bytes.empty()
                : residue_bytes.find(fault_jti) != std::string::npos,
            checkpoint + " retained the expected unbound temporary bytes");

        ReplayLedger reload;
        reload.load(ledger_path.generic_string(), "immediate");
        test.require(reload.loaded_entries == 1 &&
                         reload.contains_jti("seed-jti") &&
                         !reload.contains_jti(fault_jti),
                     checkpoint + " retained the exact previous ledger state");
        test.require(reload.journal_rolled_back_before_commit == 0 &&
                         reload.journal_recovered_after_commit == 0 &&
                         reload.journal_rejections == 0,
                     checkpoint +
                         " did not invent recovery authority without a journal");
        test.require(fs::exists(residue) &&
                         require_single_temporary_residue(ledger_path,
                                                          checkpoint) ==
                             residue,
                     checkpoint +
                         " preserved the unbound orphan for explicit operator policy");
    }
}

void test_postcommit_recovery_frontiers(TestState& test) {
    const std::vector<std::string> checkpoints{
        "after-rename-before-dir-fsync",
        "after-dir-fsync-before-journal-unlink",
    };
    for (const std::string& checkpoint : checkpoints) {
        TemporaryTree tree;
        const fs::path ledger_path = tree.path() / "ledger.jsonl";
        seed_one(ledger_path);
        const std::string fault_jti = "fault-" + checkpoint;
        inject_append(ledger_path, checkpoint, fault_jti);

        ReplayLedger reload;
        reload.load(ledger_path.generic_string(), "immediate");
        test.require(reload.loaded_entries == 2 &&
                         reload.contains_jti("seed-jti") &&
                         reload.contains_jti(fault_jti),
                     checkpoint + " selected the exact next state");
        test.require(reload.journal_recovered_after_commit == 1 &&
                         reload.journal_rolled_back_before_commit == 0 &&
                         reload.journal_rejections == 0,
                     checkpoint + " recorded one committed recovery");
        test.require(!fs::exists(ledger_path.string() + ".journal") &&
                         !has_temporary_residue(ledger_path),
                     checkpoint + " retired committed recovery artifacts");
    }
}

void test_retired_journal_frontier(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    seed_one(ledger_path);
    inject_append(ledger_path, "after-journal-unlink-before-directory-fsync",
                  "unlink-jti");
    test.require(!fs::exists(ledger_path.string() + ".journal"),
                 "journal-unlink frontier removed the witness name");

    ReplayLedger reload;
    reload.load(ledger_path.generic_string(), "immediate");
    test.require(reload.loaded_entries == 2 &&
                     reload.contains_jti("unlink-jti"),
                 "journal-unlink frontier retained committed ledger state");
    test.require(reload.journal_recovered_after_commit == 0 &&
                     reload.journal_rolled_back_before_commit == 0 &&
                     reload.journal_rejections == 0,
                 "journal-unlink frontier needed no witness recovery");
}

void test_normal_commit_barriers(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    ReplayLedger ledger;
    ledger.load(ledger_path.generic_string(), "batch");
    std::string reason;
    test.require(ledger.stage(make_case("normal-case"),
                              make_claims("normal-jti"), "allow", reason),
                 "normal batch row staged: " + reason);
    test.require(ledger.commit(reason), "normal batch committed: " + reason);
    test.require(ledger.atomic_rewrite_commits == 1 &&
                     ledger.journal_records_written == 1 &&
                     ledger.directory_fsync_attempts == 3,
                 "normal commit crossed journal-create, rename, and retirement directory barriers");
    test.require(!fs::exists(ledger_path.string() + ".journal") &&
                     !has_temporary_residue(ledger_path),
                 "normal commit left no recovery artifacts");
}

void test_forged_temporary_name_cannot_delete(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    seed_one(ledger_path);
    inject_append(ledger_path, "after-journal-fsync", "forged-jti");

    const fs::path journal_path = ledger_path.string() + ".journal";
    std::string journal = read_bytes(journal_path);
    const std::string key = "  \"temporary_name\": \"";
    const std::size_t value_begin = journal.find(key);
    if (value_begin == std::string::npos) {
        throw std::runtime_error("v3 journal temporary name was absent");
    }
    const std::size_t begin = value_begin + key.size();
    const std::size_t end = journal.find('"', begin);
    if (end == std::string::npos) {
        throw std::runtime_error("v3 journal temporary name was unterminated");
    }
    const std::string forged_name = "ledger.jsonl.tmp.notes.1";
    journal.replace(begin, end - begin, forged_name);
    write_bytes(journal_path, journal);

    const fs::path sentinel = tree.path() / forged_name;
    write_bytes(sentinel, "do-not-delete");
    try {
        ReplayLedger reload;
        reload.load(ledger_path.generic_string(), "immediate");
        throw std::runtime_error("forged temporary name was accepted");
    } catch (const std::exception& error) {
        const std::string message = error.what();
        test.require(message.find("dirty journal rejected") != std::string::npos &&
                         message.find("temporary name") != std::string::npos &&
                         (message.find("invalid") != std::string::npos ||
                          message.find("canonical positive decimal") !=
                              std::string::npos),
                     "forged temporary name failed at exact ownership grammar: " +
                         message);
    }
    test.require(fs::exists(sentinel) && read_bytes(sentinel) == "do-not-delete",
                 "forged journal could not delete a family-looking sentinel");
    test.require(fs::exists(journal_path),
                 "rejected forged journal remained for operator evidence");
}

void test_precommit_rebound_temporary_bytes_are_preserved(TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";
    seed_one(ledger_path);
    inject_append(ledger_path, "after-journal-fsync", "rebound-jti");

    const fs::path journal_path = ledger_path.string() + ".journal";
    const fs::path temporary_path = require_single_temporary_residue(
        ledger_path, "rebound temporary fixture");
    write_bytes(temporary_path, "unrelated-operator-bytes");

    try {
        ReplayLedger reload;
        reload.load(ledger_path.generic_string(), "immediate");
        throw std::runtime_error(
            "rebound precommit temporary bytes were accepted");
    } catch (const std::exception& error) {
        const std::string message = error.what();
        test.require(
            message.find("dirty journal rejected") != std::string::npos &&
                message.find("temporary payload digest") !=
                    std::string::npos,
            "rebound precommit temporary failed exact-byte authority: " +
                message);
    }
    test.require(fs::exists(journal_path) && fs::exists(temporary_path) &&
                     read_bytes(temporary_path) ==
                         "unrelated-operator-bytes",
                 "rejected rebound temporary and journal remained operator evidence");
    const std::string ledger_bytes = read_bytes(ledger_path);
    test.require(ledger_bytes.find("seed-jti") != std::string::npos &&
                     ledger_bytes.find("rebound-jti") == std::string::npos,
                 "rebound temporary rejection preserved the previous ledger bytes");
}

}  // namespace

int main() {
#if defined(_WIN32)
    std::cout << "local JSONL replay crash state machine: unavailable on Windows\n";
    return 0;
#else
    try {
        TestState test;
        test_journal_staging_rollback(test);
        test_linked_journal_publication_completion(test);
        test_prejournal_temporary_frontiers(test);
        test_precommit_rollback_frontiers(test);
        test_postcommit_recovery_frontiers(test);
        test_retired_journal_frontier(test);
        test_normal_commit_barriers(test);
        test_forged_temporary_name_cannot_delete(test);
        test_precommit_rebound_temporary_bytes_are_preserved(test);
        std::cout << "local JSONL replay crash state machine: " << test.passed
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "local JSONL replay crash state machine: " << error.what()
                  << '\n';
        return 1;
    }
#endif
}
