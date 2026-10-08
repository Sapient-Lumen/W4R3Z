#include "anonsync_core_internal.hpp"
#include "sync_process_incarnation.hpp"
#include "persistence/local_jsonl_replay_publication.hpp"
#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>

#if !defined(_WIN32)
#include <unistd.h>
#endif

namespace {

namespace fs = std::filesystem;
using anonsync::Json;
using anonsync::ReplayLedger;
using anonsync::json_string_value;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::sha256_hex;
using anonsync::persistence::FrozenLocalJsonlReplayJournal;
using anonsync::persistence::LocalJsonlReplayJournalFields;
using anonsync::persistence::encode_local_jsonl_replay_journal_json_or_throw;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
using namespace std::chrono_literals;
#endif

static_assert(!std::is_copy_constructible_v<ReplayLedger>);
static_assert(!std::is_copy_assignable_v<ReplayLedger>);
static_assert(!std::is_move_constructible_v<ReplayLedger>);
static_assert(!std::is_move_assignable_v<ReplayLedger>);

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
                ("anonsync-replay-backend-namespace-" +
                 std::to_string(static_cast<long long>(::getpid())) + "-" +
                 std::to_string(static_cast<long long>(
                     std::chrono::steady_clock::now()
                         .time_since_epoch()
                         .count())));
#else
        path_ = fs::temp_directory_path() / "anonsync-replay-backend-namespace";
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

class CurrentDirectoryGuard final {
public:
    CurrentDirectoryGuard() : previous_(fs::current_path()) {}
    ~CurrentDirectoryGuard() {
        std::error_code error;
        fs::current_path(previous_, error);
    }

private:
    fs::path previous_;
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

#if !defined(_WIN32)

void test_backend_survives_cwd_change(TestState& test) {
    TemporaryTree tree;
    const fs::path first = tree.path() / "first";
    const fs::path second = tree.path() / "second";
    fs::create_directories(first);
    fs::create_directories(second);
    CurrentDirectoryGuard cwd;
    fs::current_path(first);

    ReplayLedger ledger;
    ledger.load("ledger.jsonl", "batch");
    test.require(ledger.path == (first / "ledger.jsonl").generic_string(),
                 "backend replaced relative spelling with frozen absolute path");

    fs::current_path(second);
    std::string reason;
    test.require(ledger.stage(make_case("cwd-case"), make_claims("cwd-jti"),
                              "allow", reason),
                 "backend staged after cwd change: " + reason);
    test.require(ledger.commit(reason),
                 "backend committed after cwd change: " + reason);
    test.require(fs::exists(first / "ledger.jsonl"),
                 "backend committed to originally selected directory");
    test.require(!fs::exists(second / "ledger.jsonl") &&
                     !fs::exists(second / "ledger.jsonl.lock") &&
                     !fs::exists(second / "ledger.jsonl.journal"),
                 "backend created no authority artifacts in later cwd");
    test.require(ledger.directory_fsync_attempts == 3,
                 "commit executed all three directory durability barriers");
    ledger.close();

    ReplayLedger reload;
    reload.load((first / "ledger.jsonl").generic_string(), "batch");
    test.require(reload.loaded_entries == 1 && reload.contains_jti("cwd-jti"),
                 "backend reloaded exact committed state from retained path");
}

void test_legacy_v2_relative_journal_recovery(TestState& test) {
    TemporaryTree tree;
    CurrentDirectoryGuard cwd;
    fs::current_path(tree.path());

    std::string committed_head;
    {
        ReplayLedger seed;
        seed.load("ledger.jsonl", "immediate");
        std::string reason;
        test.require(seed.append(make_case("legacy-case"),
                                 make_claims("legacy-jti"), "allow", reason),
                     "legacy fixture committed: " + reason);
        committed_head = seed.durable_head_hash;
    }

    std::ifstream input("ledger.jsonl", std::ios::binary);
    const std::string payload{std::istreambuf_iterator<char>(input),
                              std::istreambuf_iterator<char>()};
    test.require(!payload.empty(), "legacy fixture payload was readable");

    LocalJsonlReplayJournalFields fields;
    fields.ledger_path = "ledger.jsonl";
    fields.previous_head = "GENESIS";
    fields.previous_line_count = 0;
    fields.next_head = committed_head;
    fields.next_line_count = 1;
    fields.last_entry_previous_hash = "GENESIS";
    fields.payload_sha256 = sha256_hex(payload);
    const std::string journal =
        encode_local_jsonl_replay_journal_json_or_throw(
            FrozenLocalJsonlReplayJournal::freeze_v2_or_throw(
                std::move(fields)));
    {
        std::ofstream output("ledger.jsonl.journal",
                             std::ios::binary | std::ios::trunc);
        output.write(journal.data(),
                     static_cast<std::streamsize>(journal.size()));
        output.close();
        test.require(static_cast<bool>(output),
                     "legacy relative v2 journal fixture was published");
    }

    ReplayLedger recovered;
    recovered.load("ledger.jsonl", "immediate");
    test.require(recovered.path ==
                     (tree.path() / "ledger.jsonl").generic_string(),
                 "legacy recovery still froze the selected absolute path");
    test.require(recovered.loaded_entries == 1 &&
                     recovered.contains_jti("legacy-jti") &&
                     recovered.journal_recovered_after_commit == 1,
                 "legacy relative v2 journal recovered committed state");
    test.require(!fs::exists("ledger.jsonl.journal"),
                 "legacy relative v2 journal was durably retired");
}

void test_backend_revokes_rebound_parent(TestState& test) {
    TemporaryTree tree;
    const fs::path live = tree.path() / "live";
    const fs::path displaced = tree.path() / "displaced";
    fs::create_directories(live);

    ReplayLedger ledger;
    ledger.load((live / "ledger.jsonl").generic_string(), "batch");
    std::string reason;
    test.require(ledger.stage(make_case("rebind-case"),
                              make_claims("rebind-jti"), "allow", reason),
                 "backend staged before parent rebinding");
    fs::rename(live, displaced);
    fs::create_directories(live);

    test.require(!ledger.commit(reason),
                 "backend rejected commit after parent rebinding");
    test.require(!ledger.is_enabled(),
                 "parent rebinding expired backend authority");
    test.require(reason.find("no longer names the retained directory") !=
                     std::string::npos,
                 "parent rebinding exposed precise rejection reason");
    test.require(!fs::exists(live / "ledger.jsonl") &&
                     !fs::exists(live / "ledger.jsonl.journal") &&
                     !fs::exists(live / "ledger.jsonl.lock"),
                 "revoked backend did not mutate replacement parent");
}

void test_backend_rejects_stale_durable_payload_before_witness(
    TestState& test) {
    TemporaryTree tree;
    const fs::path ledger_path = tree.path() / "ledger.jsonl";

    {
        ReplayLedger seed;
        seed.load(ledger_path.generic_string(), "immediate");
        std::string reason;
        test.require(seed.append(make_case("stale-seed"),
                                 make_claims("stale-seed-jti"), "allow",
                                 reason),
                     "stale-state fixture committed: " + reason);
    }

    ReplayLedger ledger;
    ledger.load(ledger_path.generic_string(), "batch");
    std::string reason;
    test.require(ledger.stage(make_case("stale-pending"),
                              make_claims("stale-pending-jti"), "allow",
                              reason),
                 "stale-state fixture staged pending row: " + reason);

    const std::string external_payload = "uncooperative-writer-payload\n";
    {
        std::ofstream output(ledger_path,
                             std::ios::binary | std::ios::trunc);
        output.write(external_payload.data(),
                     static_cast<std::streamsize>(external_payload.size()));
        output.close();
        test.require(static_cast<bool>(output),
                     "uncooperative writer fixture replaced durable bytes");
    }

    test.require(!ledger.commit(reason),
                 "backend rejected stale loaded authority before commit");
    test.require(!ledger.is_enabled(),
                 "stale durable payload rejection expired backend authority");
    test.require(reason.find("changed since load") != std::string::npos,
                 "stale durable payload exposed precise rejection reason");

    std::ifstream input(ledger_path, std::ios::binary);
    const std::string observed{std::istreambuf_iterator<char>(input),
                               std::istreambuf_iterator<char>()};
    test.require(observed == external_payload,
                 "stale-state rejection preserved external durable bytes");
    test.require(!fs::exists(ledger_path.generic_string() + ".journal") &&
                     !fs::exists(ledger_path.generic_string() +
                                 ".journal.stage"),
                 "stale-state rejection published no journal witness");
    bool temporary_residue = false;
    const std::string temporary_prefix =
        ledger_path.filename().string() + ".tmp.";
    for (const fs::directory_entry& entry :
         fs::directory_iterator(tree.path())) {
        const std::string name = entry.path().filename().string();
        if (name.rfind(temporary_prefix, 0) == 0) {
            temporary_residue = true;
        }
    }
    test.require(!temporary_residue,
                 "stale-state rejection published no temporary replacement");
}

void test_backend_child_destructor_cannot_unlock_parent(TestState& test) {
    TemporaryTree tree;
    const std::string ledger_path =
        (tree.path() / "ledger.jsonl").generic_string();
    auto owner = std::make_unique<ReplayLedger>();
    owner->load(ledger_path, "batch");

    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            owner.reset();
            return 99;
        },
        "local JSONL backend inherited destructor misuse");
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, 5s,
        "local JSONL backend inherited destructor misuse");
    test.require(
        true,
        "child backend destructor fail-stopped before inherited unlock");

    try {
        ReplayLedger contender;
        contender.load(ledger_path, "batch");
        throw std::runtime_error(
            "contender acquired lock after hostile child destructor");
    } catch (const std::exception& error) {
        test.require(std::string(error.what()).find("contention") !=
                         std::string::npos,
                     "parent lock remained held after hostile child destructor");
    }

    owner.reset();
    ReplayLedger successor;
    successor.load(ledger_path, "batch");
    test.require(successor.is_enabled(),
                 "successor acquired authority after parent owner release");
}

#endif

}  // namespace

int main() {
#if defined(_WIN32)
    std::cout << "local JSONL replay backend namespace: unavailable on Windows\n";
    return 0;
#else
    try {
        TestState test;
        test_backend_survives_cwd_change(test);
        test_legacy_v2_relative_journal_recovery(test);
        test_backend_revokes_rebound_parent(test);
        test_backend_rejects_stale_durable_payload_before_witness(test);
        test_backend_child_destructor_cannot_unlock_parent(test);
        std::cout << "local JSONL replay backend namespace: " << test.passed
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "local JSONL replay backend namespace: " << error.what()
                  << '\n';
        return 1;
    }
#endif
}
