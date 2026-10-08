#include "sha256_digest.hpp"
#include "sync_replica_file_payload_verification_index.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#if !defined(_WIN32)

#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
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


template <typename Callable>
void require_overflow(Callable&& callable, const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::overflow_error&) {
        return;
    } catch (const std::exception& error) {
        fail(message + ": wrong exception type: " + error.what());
    }
    fail(message + ": no overflow error was thrown");
}

constexpr std::string_view kVerificationIndexMagic =
    "anonsync:sync-replica-file-payload-verification-index:v1\n";
constexpr std::size_t kEncodedDigestBytes = 64U;
constexpr std::size_t kEncodedU64Bytes = 8U;
constexpr std::size_t kMetadataFieldCount = 11U;
constexpr std::size_t kEncodedMetadataBytes =
    kMetadataFieldCount * kEncodedU64Bytes;
constexpr std::size_t kEntryCountOffset =
    kVerificationIndexMagic.size() + kEncodedDigestBytes +
    kEncodedMetadataBytes;
constexpr std::size_t kFirstEntryDigestOffset =
    kEntryCountOffset + (2U * kEncodedU64Bytes);

void write_u64_be(
    std::string& encoded,
    std::size_t offset,
    std::uint64_t value) {
    if (offset > encoded.size() ||
        kEncodedU64Bytes > encoded.size() - offset) {
        fail("verification-index test mutation exceeded encoded bytes");
    }
    for (std::size_t index = 0U; index < kEncodedU64Bytes; ++index) {
        const unsigned shift =
            static_cast<unsigned>((kEncodedU64Bytes - 1U - index) * 8U);
        encoded[offset + index] =
            static_cast<char>((value >> shift) & 0xffU);
    }
}

void reseal(std::string& encoded) {
    if (encoded.size() < kEncodedDigestBytes) {
        fail("verification-index test cannot reseal a short record");
    }
    const std::size_t payload_bytes = encoded.size() - kEncodedDigestBytes;
    encoded.replace(
        payload_bytes, kEncodedDigestBytes,
        anonsync::sha256_hex(encoded.substr(0U, payload_bytes)));
}

[[nodiscard]] anonsync::SyncPosixRegularFileSnapshotMetadata metadata(
    std::uint64_t inode,
    std::uint64_t size,
    std::int64_t seconds) {
    return anonsync::SyncPosixRegularFileSnapshotMetadata{
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

[[nodiscard]] anonsync::SyncReplicaFilePayloadVerificationIndex fixture() {
    anonsync::SyncReplicaFilePayloadVerificationIndex index;
    index.store_identity_sha256 = anonsync::sha256_hex("identity-v3-bytes");
    index.store_identity_metadata = metadata(501U, 173U, -7);
    index.entries.push_back({anonsync::sha256_hex("alpha"), metadata(601U, 5U, 11)});
    index.entries.push_back({anonsync::sha256_hex("bravo-payload"), metadata(602U, 13U, 12)});
    if (index.entries[1].content_sha256 < index.entries[0].content_sha256) {
        std::swap(index.entries[0], index.entries[1]);
    }
    index.indexed_bytes = 18U;
    return index;
}

void test_shared_metadata_codec_contract() {
    const auto observed = metadata(499U, 77U, -19);
    std::string encoded;
    anonsync::append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, observed);
    require(
        encoded.size() ==
            anonsync::kSyncPosixRegularFileSnapshotMetadataEncodedBytes,
        "shared POSIX metadata codec width drifted from eleven fields");
    require(
        anonsync::parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            encoded, "shared metadata codec round trip") == observed,
        "shared POSIX metadata codec changed an exact field");
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
                std::string_view(encoded).substr(0U, encoded.size() - 1U),
                "shared metadata codec truncated");
        },
        "canonical eleven-field width",
        "shared POSIX metadata codec accepted a truncated projection");
    std::string extended = encoded;
    extended.push_back('x');
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
                extended, "shared metadata codec extended");
        },
        "canonical eleven-field width",
        "shared POSIX metadata codec accepted an extended projection");
    auto nonprivate = observed;
    nonprivate.mode |= S_IRGRP;
    require_invalid(
        [&] {
            anonsync::validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
                nonprivate, std::nullopt,
                "shared metadata codec private-file validation");
        },
        "exact mode 0600",
        "shared POSIX metadata validation admitted a nonprivate inode");
}

void test_round_trip_and_exact_size() {
    const auto index = fixture();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
            index, 8U, 1024U, "verification-index round trip");
    const auto decoded =
        anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
            encoded, 8U, 1024U, "verification-index round trip");
    require(decoded == index, "verification-index round trip changed exact fields");
    require(
        encoded.size() ==
            anonsync::sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
                2U, "verification-index exact maximum"),
        "verification-index exact encoding size drifted from its published bound");
    require(
        encoded.size() <
            anonsync::sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
                8U, "verification-index larger maximum"),
        "verification-index larger entry ceiling did not increase its encoded bound");
    require(
        anonsync::kSyncReplicaFilePayloadVerificationIndexBasename ==
            ".anonsync-payload-verification-index-v1",
        "verification-index basename drifted from the v1 namespace contract");
}

void test_checksum_length_and_generation_rejection() {
    const auto index = fixture();
    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
            index, 8U, 1024U, "verification-index corruption fixture");

    std::string corrupted = encoded;
    corrupted[17U] = static_cast<char>(corrupted[17U] ^ 0x01);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                corrupted, 8U, 1024U, "verification-index corrupted");
        },
        "checksum",
        "verification-index corruption escaped the trailing checksum");

    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                std::string_view(encoded).substr(0U, encoded.size() - 1U),
                8U, 1024U, "verification-index truncated");
        },
        "checksum",
        "verification-index truncation was accepted");

    std::string extended = encoded;
    extended.push_back('x');
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                extended, 8U, 1024U, "verification-index extended");
        },
        "checksum",
        "verification-index trailing bytes were accepted");

    std::string incompatible_generation = encoded;
    incompatible_generation[0U] = 'A';
    reseal(incompatible_generation);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                incompatible_generation, 8U, 1024U,
                "verification-index incompatible generation");
        },
        "incompatible format generation",
        "checksum-valid incompatible verification-index generation was accepted");

    std::string false_entry_count = encoded;
    write_u64_be(false_entry_count, kEntryCountOffset, 3U);
    reseal(false_entry_count);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                false_entry_count, 8U, 1024U,
                "verification-index false count");
        },
        "length does not match",
        "checksum-valid false verification-index entry count was accepted");

    std::string invalid_payload_digest = encoded;
    invalid_payload_digest[kFirstEntryDigestOffset] = 'G';
    reseal(invalid_payload_digest);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                invalid_payload_digest, 8U, 1024U,
                "verification-index invalid payload digest");
        },
        "invalid payload digest",
        "checksum-valid invalid payload digest was accepted");

    std::string nonprivate_payload = encoded;
    const std::size_t first_entry_mode_offset =
        kFirstEntryDigestOffset + kEncodedDigestBytes +
        (6U * kEncodedU64Bytes);
    write_u64_be(
        nonprivate_payload, first_entry_mode_offset,
        static_cast<std::uint64_t>(S_IFREG | S_IRUSR | S_IWUSR | S_IRGRP));
    reseal(nonprivate_payload);
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                nonprivate_payload, 8U, 1024U,
                "verification-index nonprivate payload");
        },
        "exact mode 0600",
        "checksum-valid nonprivate payload metadata was accepted");
}

void test_semantic_invariants() {
    auto index = fixture();
    std::swap(index.entries[0], index.entries[1]);
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 8U, 1024U, "verification-index unsorted");
        },
        "strictly sorted",
        "verification-index serializer accepted an unsorted payload map");

    index = fixture();
    index.indexed_bytes += 1U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 8U, 1024U, "verification-index byte mismatch");
        },
        "does not match",
        "verification-index serializer accepted a false aggregate byte total");

    index = fixture();
    index.entries[0].metadata.link_count = 2U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 8U, 1024U, "verification-index linked entry");
        },
        "single link",
        "verification-index serializer admitted linked-file metadata");

    index = fixture();
    index.entries[0].metadata.status_change_nanoseconds = 1000000000U;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 8U, 1024U, "verification-index invalid time");
        },
        "timestamp fraction",
        "verification-index serializer admitted an invalid timestamp fraction");

    index = fixture();
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 1U, 1024U, "verification-index count ceiling");
        },
        "entry count",
        "verification-index serializer ignored the configured entry ceiling");

    index = fixture();
    index.entries[1].content_sha256 = index.entries[0].content_sha256;
    require_invalid(
        [&] {
            (void)anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
                index, 8U, 1024U, "verification-index duplicate digest");
        },
        "strictly sorted",
        "verification-index serializer admitted a duplicate payload digest");

    const std::string encoded =
        anonsync::serialize_sync_replica_file_payload_verification_index_or_throw(
            fixture(), 8U, 1024U, "verification-index parser ceilings");
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                encoded, 1U, 1024U, "verification-index parser count ceiling");
        },
        "encoded-size ceiling",
        "verification-index parser ignored the encoded entry ceiling");
    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                encoded, 8U, 17U, "verification-index parser byte ceiling");
        },
        "aggregate bytes",
        "verification-index parser ignored the aggregate payload-byte ceiling");

    require_overflow(
        [&] {
            (void)anonsync::sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
                std::numeric_limits<std::uint64_t>::max(),
                "verification-index overflow ceiling");
        },
        "verification-index maximum-size arithmetic did not reject overflow");

    require_invalid(
        [&] {
            (void)anonsync::parse_sync_replica_file_payload_verification_index_or_throw(
                "too-short", 8U, 1024U, "verification-index short");
        },
        "truncated",
        "verification-index parser accepted a short record");
}

}  // namespace

int main() {
    try {
        test_shared_metadata_codec_contract();
        test_round_trip_and_exact_size();
        test_checksum_length_and_generation_rejection();
        test_semantic_invariants();
        std::cout << "sync replica payload verification-index tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica payload verification-index tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
