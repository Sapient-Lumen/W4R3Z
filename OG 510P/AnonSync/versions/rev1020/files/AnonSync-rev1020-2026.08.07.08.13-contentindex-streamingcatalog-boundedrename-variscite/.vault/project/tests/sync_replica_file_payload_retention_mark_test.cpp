#include "sha256_digest.hpp"
#include "sync_replica_file_payload_retention_mark.hpp"

#if !defined(_WIN32)

#include <sys/stat.h>

#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

std::uint64_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_invalid(
    Function&& function,
    std::string_view expected,
    std::string_view message) {
    ++checks;
    try {
        function();
    } catch (const std::invalid_argument& error) {
        if (std::string_view(error.what()).find(expected) ==
            std::string_view::npos) {
            throw std::runtime_error(
                std::string(message) + ": unexpected diagnostic: " +
                error.what());
        }
        return;
    }
    throw std::runtime_error(std::string(message) + ": no error was thrown");
}

anonsync::SyncPosixRegularFileSnapshotMetadata identity_metadata() {
    return {
        17U,
        31U,
        211U,
        1U,
        1000U,
        1000U,
        static_cast<std::uint32_t>(S_IFREG | S_IRUSR | S_IWUSR),
        9000,
        123456789U,
        9001,
        987654321U};
}

anonsync::SyncReplicaFilePayloadRetentionMark fixture() {
    anonsync::SyncReplicaFilePayloadRetentionMark mark;
    mark.store_identity_sha256 = anonsync::sha256_hex("store identity");
    mark.store_identity_metadata = identity_metadata();
    mark.generation = 7U;
    mark.marked_at_unix_seconds = 1'800'000'000U;
    mark.source_replica_state_generation = 41U;
    mark.policy = {
        .minimum_grace_seconds = 86'400U,
        .maximum_candidate_payload_count = 100U,
        .maximum_candidate_payload_bytes = 1'000'000U,
        .maximum_collection_payload_count = 8U,
        .maximum_collection_payload_bytes = 65'536U,
    };
    mark.source_operation_set_digest = anonsync::sha256_hex("operations");
    mark.source_evidence_set_digest = anonsync::sha256_hex("evidence");
    mark.source_historical_version_pin_set_digest =
        anonsync::sha256_hex("pins");
    mark.source_visible_state_digest = anonsync::sha256_hex("visible");
    mark.source_payload_snapshot_digest = anonsync::sha256_hex("payloads");
    mark.source_payload_transient_namespace_digest =
        anonsync::sha256_hex("transients");
    mark.unreferenced_candidate_set_digest =
        anonsync::sha256_hex("candidates");
    mark.durable_candidate_witness_digest =
        anonsync::sha256_hex("witness");
    mark.unreferenced_candidate_payload_count = 12U;
    mark.unreferenced_candidate_payload_bytes = 987'654U;
    return mark;
}

void test_round_trip_and_digest() {
    const auto mark = fixture();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
            mark, 1000U, 2'000'000U, "retention-mark fixture");
    require(
        encoded.size() ==
            anonsync::sync_replica_file_payload_retention_mark_exact_bytes(),
        "retention-mark exact byte count drifted");
    require(
        anonsync::parse_sync_replica_file_payload_retention_mark_or_throw(
            encoded, 1000U, 2'000'000U, "retention-mark fixture") == mark,
        "retention-mark round trip changed fields");
    require(
        anonsync::sync_replica_file_payload_retention_mark_digest_or_throw(
            mark, 1000U, 2'000'000U, "retention-mark fixture") ==
            encoded.substr(encoded.size() - 64U),
        "retention-mark digest did not equal framed checksum");
    require(
        anonsync::kSyncReplicaFilePayloadRetentionMarkBasename ==
            ".anonsync-payload-retention-mark-v1",
        "retention-mark basename drifted");
}

void test_checksum_and_framing_rejection() {
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
            fixture(), 1000U, 2'000'000U, "retention-mark corruption");
    std::string corrupted = encoded;
    corrupted[23U] = static_cast<char>(corrupted[23U] ^ 0x01);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_retention_mark_or_throw(
                corrupted, 1000U, 2'000'000U,
                "retention-mark corruption");
        },
        "checksum",
        "retention-mark checksum corruption was accepted");
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_retention_mark_or_throw(
                std::string_view(encoded).substr(0U, encoded.size() - 1U),
                1000U, 2'000'000U, "retention-mark truncation");
        },
        "exact v1 size",
        "truncated retention mark was accepted");
    std::string extended = encoded;
    extended.push_back('x');
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_retention_mark_or_throw(
                extended, 1000U, 2'000'000U,
                "retention-mark extension");
        },
        "exact v1 size",
        "extended retention mark was accepted");
}

void test_policy_and_candidate_rejection() {
    {
        const auto valid = fixture();
        anonsync::validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
            valid.policy, valid.marked_at_unix_seconds, 100U, 1'000'000U,
            "direct store policy");
        require(true, "valid store-aware retention policy was rejected");
    }

    {
        auto invalid_count = fixture();
        invalid_count.policy.maximum_candidate_payload_count = 101U;
        require_invalid(
            [&] {
                anonsync::validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
                    invalid_count.policy,
                    invalid_count.marked_at_unix_seconds, 100U, 1'000'000U,
                    "direct store count policy");
            },
            "candidate count exceeds store capacity",
            "store-aware retention policy accepted an impossible candidate count");
    }

    {
        auto invalid_bytes = fixture();
        invalid_bytes.policy.maximum_candidate_payload_bytes = 1'000'001U;
        require_invalid(
            [&] {
                anonsync::validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
                    invalid_bytes.policy,
                    invalid_bytes.marked_at_unix_seconds, 100U, 1'000'000U,
                    "direct store byte policy");
            },
            "candidate bytes exceed store capacity",
            "store-aware retention policy accepted an impossible byte frontier");
    }

    auto mark = fixture();
    mark.policy.minimum_grace_seconds = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero grace");
        },
        "grace seconds",
        "zero retention grace was accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_count = 101U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "collection count");
        },
        "collection count",
        "collection count above candidate cap was accepted");

    mark = fixture();
    mark.unreferenced_candidate_payload_count = 101U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "candidate count");
        },
        "candidate count",
        "observed candidate count above policy was accepted");

    mark = fixture();
    mark.unreferenced_candidate_payload_bytes = 1'000'001U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "candidate bytes");
        },
        "candidate bytes",
        "observed candidate bytes above policy were accepted");

    mark = fixture();
    mark.unreferenced_candidate_payload_count = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "empty candidates");
        },
        "no unreferenced",
        "empty retention mark was accepted");

    mark = fixture();
    mark.marked_at_unix_seconds = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero mark time");
        },
        "mark time",
        "zero retention mark time was accepted");

    mark = fixture();
    mark.policy.minimum_grace_seconds =
        anonsync::kSyncReplicaFilePayloadRetentionMarkMaximumGraceSeconds + 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "excess grace");
        },
        "grace seconds",
        "retention grace above the fixed horizon was accepted");

    mark = fixture();
    mark.marked_at_unix_seconds =
        std::numeric_limits<std::uint64_t>::max();
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "deadline overflow");
        },
        "deadline overflows",
        "retention grace deadline overflow was accepted");

    mark = fixture();
    mark.policy.maximum_candidate_payload_count = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero candidate frontier");
        },
        "candidate count frontier is zero",
        "zero candidate-count policy frontier was accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_count = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero collection frontier");
        },
        "collection count",
        "zero collection-count policy frontier was accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_bytes =
        mark.policy.maximum_candidate_payload_bytes + 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "collection byte frontier");
        },
        "collection bytes",
        "collection-byte frontier above candidate bytes was accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_bytes = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero collection bytes");
        },
        "zero collection bytes",
        "nonzero candidate bytes with zero collection bytes were accepted");

    mark = fixture();
    mark.policy.maximum_candidate_payload_count = 1001U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "store count capacity");
        },
        "store capacity",
        "policy candidate count above store capacity was accepted");

    mark = fixture();
    mark.policy.maximum_candidate_payload_bytes = 2'000'001U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "store byte capacity");
        },
        "store capacity",
        "policy candidate bytes above store capacity were accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_count = 13U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "collection observed count");
        },
        "candidates",
        "collection count above the observed candidate set was accepted");

    mark = fixture();
    mark.policy.maximum_collection_payload_bytes = 987'655U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "collection observed bytes");
        },
        "candidates",
        "collection bytes above the observed candidate set were accepted");

    mark = fixture();
    mark.source_replica_state_generation = 0U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero source generation");
        },
        "source replica generation",
        "zero replica source generation was accepted");

    mark = fixture();
    mark.durable_candidate_witness_digest[0] = 'X';
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "invalid witness digest");
        },
        "durable-candidate-witness",
        "noncanonical candidate witness digest was accepted");

    mark = fixture();
    mark.store_identity_metadata.link_count = 2U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "linked identity");
        },
        "link",
        "multiply linked store identity metadata was accepted");

    mark = fixture();
    mark.policy.maximum_candidate_payload_bytes = 0U;
    mark.policy.maximum_collection_payload_bytes = 0U;
    mark.unreferenced_candidate_payload_bytes = 0U;
    require(
        anonsync::parse_sync_replica_file_payload_retention_mark_or_throw(
            anonsync::serialize_sync_replica_file_payload_retention_mark_or_throw(
                mark, 1000U, 2'000'000U, "zero-byte candidates"),
            1000U, 2'000'000U, "zero-byte candidates") == mark,
        "valid nonempty zero-byte candidate set did not round trip");
}

}  // namespace

int main() {
    try {
        test_round_trip_and_digest();
        test_checksum_and_framing_rejection();
        test_policy_and_candidate_rejection();
        std::cout << "sync replica payload retention mark: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica payload retention mark failure after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
