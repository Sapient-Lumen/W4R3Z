#include "sha256_digest.hpp"
#include "sync_replica_file_payload_terminal_verification_state.hpp"

#if !defined(_WIN32)

#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

#include <sys/stat.h>

namespace {

std::uint64_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_invalid(
    Callable&& callable,
    std::string_view expected,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::invalid_argument& error) {
        if (std::string_view(error.what()).find(expected) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected diagnostic: " + error.what());
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no error was thrown");
}

anonsync::SyncPosixRegularFileSnapshotMetadata metadata(
    std::uint64_t inode,
    std::uint64_t size,
    std::int64_t seconds) {
    return {
        71U,
        inode,
        size,
        1U,
        1001U,
        1002U,
        static_cast<std::uint32_t>(S_IFREG | S_IRUSR | S_IWUSR),
        seconds,
        123456789U,
        seconds + 1,
        987654321U};
}

anonsync::SyncReplicaFilePayloadTerminalVerificationState progress_state(
    std::uint64_t generation = 4U) {
    const std::string prefix = "bounded terminal prefix";
    anonsync::ResumableSha256 hash;
    hash.update(prefix);

    anonsync::SyncReplicaFilePayloadTerminalVerificationState state;
    state.store_identity_sha256 = anonsync::sha256_hex("store identity");
    state.store_identity_metadata = metadata(501U, 173U, -7);
    state.generation = generation;
    state.content_sha256 = anonsync::sha256_hex(prefix + " tail");
    state.total_size_bytes = prefix.size() + 5U;
    state.staged_prefix_metadata = metadata(601U, state.total_size_bytes, 12);
    state.verified_offset_bytes = prefix.size();
    state.hash = hash.checkpoint();
    return state;
}

void reseal(std::string& encoded) {
    encoded.replace(
        encoded.size() - 64U, 64U,
        anonsync::sha256_hex(encoded.substr(0U, encoded.size() - 64U)));
}

void test_slot_round_trip_and_terminal_rejection() {
    const auto progress = progress_state();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
            progress, 1024U, "progress fixture");
    require(
        encoded.size() ==
            anonsync::sync_replica_file_payload_terminal_verification_slot_exact_bytes(),
        "terminal verification slot width drifted");
    require(
        anonsync::parse_sync_replica_file_payload_terminal_verification_state_or_throw(
            encoded, 1024U, "progress fixture") == progress,
        "terminal verification progress round trip changed fields");

    auto terminal = progress;
    anonsync::ResumableSha256 completed(terminal.hash);
    completed.update(" tail");
    terminal.hash = completed.checkpoint();
    terminal.verified_offset_bytes = terminal.total_size_bytes;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                terminal, 1024U, "terminal fixture");
        },
        "canonical nonterminal",
        "terminal SHA-256 state was persisted as publication authority");
}

void test_dual_slot_torn_update_recovery() {
    const auto first = progress_state(7U);
    std::string journal =
        anonsync::initial_sync_replica_file_payload_terminal_verification_journal_or_throw(
            first, 1024U, "initial journal");
    require(
        journal.size() ==
            anonsync::sync_replica_file_payload_terminal_verification_journal_exact_bytes(),
        "terminal verification journal width drifted");
    auto observed =
        anonsync::parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
            journal, 1024U, "initial journal");
    require(
        observed.latest_state == first && observed.latest_slot_index == 0U &&
            observed.valid_slot_count == 1U &&
            observed.invalid_nonzero_slot_count == 0U,
        "initial terminal journal did not select slot zero");

    auto second = first;
    second.generation = 8U;
    const std::string second_slot =
        anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
            second, 1024U, "second slot");
    const std::size_t slot_bytes = static_cast<std::size_t>(
        anonsync::sync_replica_file_payload_terminal_verification_slot_exact_bytes());
    journal.replace(slot_bytes, slot_bytes, second_slot);
    observed =
        anonsync::parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
            journal, 1024U, "two-slot journal");
    require(
        observed.latest_state == second && observed.latest_slot_index == 1U &&
            observed.valid_slot_count == 2U,
        "newer terminal journal generation was not selected");
    require(
        anonsync::sync_replica_file_payload_terminal_verification_next_slot_index(
            observed) == 0U,
        "terminal journal did not rotate back to the older slot");

    std::string conflicting = journal;
    auto equal_generation = second;
    equal_generation.generation = first.generation;
    ++equal_generation.staged_prefix_metadata.modification_nanoseconds;
    const std::string conflicting_slot =
        anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
            equal_generation, 1024U, "conflicting equal-generation slot");
    conflicting.replace(slot_bytes, slot_bytes, conflicting_slot);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
                conflicting, 1024U, "conflicting equal-generation journal");
        },
        "conflicting equal generations",
        "different terminal states with one generation were accepted");

    journal[slot_bytes + 11U] =
        static_cast<char>(journal[slot_bytes + 11U] ^ 0x20);
    observed =
        anonsync::parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
            journal, 1024U, "torn newer slot");
    require(
        observed.latest_state == first && observed.latest_slot_index == 0U &&
            observed.valid_slot_count == 1U &&
            observed.invalid_nonzero_slot_count == 1U,
        "torn newer slot did not preserve the prior committed generation");
}

void test_framing_and_semantic_rejection() {
    const auto progress = progress_state();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
            progress, 1024U, "rejection fixture");

    std::string damaged = encoded;
    damaged[17U] = static_cast<char>(damaged[17U] ^ 0x01);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_terminal_verification_state_or_throw(
                damaged, 1024U, "damaged fixture");
        },
        "checksum", "damaged terminal verification slot was accepted");

    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_terminal_verification_state_or_throw(
                encoded.substr(1U), 1024U, "truncated fixture");
        },
        "length", "truncated terminal verification slot was accepted");

    auto zero_generation = progress;
    zero_generation.generation = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                zero_generation, 1024U, "zero generation");
        },
        "generation zero", "zero terminal generation was accepted");

    auto extent_mismatch = progress;
    --extent_mismatch.staged_prefix_metadata.size_bytes;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                extent_mismatch, 1024U, "extent mismatch");
        },
        "metadata or progress", "terminal staged-prefix extent mismatch was accepted");

    auto hash_mismatch = progress;
    ++hash_mismatch.hash.total_bytes;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                hash_mismatch, 1024U, "hash mismatch");
        },
        "hash", "terminal hash progress mismatch was accepted");

    auto terminal_checkpoint = progress;
    anonsync::ResumableSha256 completed(terminal_checkpoint.hash);
    completed.update(" tail");
    terminal_checkpoint.hash = completed.checkpoint();
    terminal_checkpoint.verified_offset_bytes =
        terminal_checkpoint.total_size_bytes;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
                terminal_checkpoint, 1024U, "terminal checkpoint");
        },
        "canonical nonterminal",
        "terminal computational state was accepted as durable authority");

    std::string unknown_generation = encoded;
    const std::size_t magic_bytes = std::string_view(
        "anonsync:sync-replica-file-payload-terminal-verification-slot:v1\n")
                                        .size();
    const std::size_t generation_offset = magic_bytes + 64U + 88U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        unknown_generation[generation_offset + index] = '\0';
    }
    reseal(unknown_generation);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_terminal_verification_state_or_throw(
                unknown_generation, 1024U, "zero encoded generation");
        },
        "generation zero", "checksum-valid zero generation was accepted");

    std::string empty_journal(
        static_cast<std::size_t>(
            anonsync::sync_replica_file_payload_terminal_verification_journal_exact_bytes()),
        '\0');
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
                empty_journal, 1024U, "empty journal");
        },
        "no valid", "empty terminal verification journal was accepted");
}

void test_public_bounds() {
    require(
        anonsync::kSyncReplicaFilePayloadTerminalVerificationBasenamePrefix ==
            ".anonsync-payload-prefix-verification-v1-",
        "terminal verification basename prefix drifted");
    require(
        anonsync::kSyncReplicaFilePayloadTerminalVerificationMaximumAdvanceBytes ==
            32ULL * 1024ULL * 1024ULL,
        "terminal verification advance frontier drifted");
    require(
        anonsync::sync_replica_file_payload_terminal_verification_journal_exact_bytes() ==
            2U * anonsync::sync_replica_file_payload_terminal_verification_slot_exact_bytes(),
        "terminal verification journal is not exactly two slots");
}

}  // namespace

int main() {
    try {
        test_slot_round_trip_and_terminal_rejection();
        test_dual_slot_torn_update_recovery();
        test_framing_and_semantic_rejection();
        test_public_bounds();
        std::cout << "sync replica file payload terminal verification state: "
                  << checks << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "sync replica file payload terminal verification state failure: "
            << error.what() << '\n';
        return 1;
    }
}

#else
int main() { return 0; }
#endif
