#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/content_availability.hpp"
#include "toxsync/content_store.hpp"
#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <span>
#include <string>
#include <vector>

namespace {

toxsync::Digest256 digest_text(const char* text) {
    return toxsync::sha256(std::as_bytes(std::span(text, std::char_traits<char>::length(text))));
}

struct CollectContext {
    std::vector<toxsync::ContentChunkRef>* chunks{};
};

void collect_chunk(void* opaque, const toxsync::ContentChunkRef& chunk) {
    static_cast<CollectContext*>(opaque)->chunks->push_back(chunk);
}

} // namespace

TOXSYNC_TEST(content_availability_round_trip_preserves_membership_and_metadata) {
    toxsync::ContentAvailabilityConfig config;
    config.filter_bytes = 1024U;
    config.hash_functions = 7U;
    config.salt = 12345U;
    toxsync::ContentAvailabilitySketch sketch(config);
    const auto manifest = digest_text("manifest");
    sketch.reset(manifest, 44U, toxsync::kAvailabilityFlagComplete);

    std::vector<toxsync::Digest256> members;
    for (std::uint64_t value = 0U; value < 100U; ++value) {
        std::array<std::byte, sizeof(value)> bytes{};
        for (std::size_t index = 0U; index < bytes.size(); ++index) {
            bytes[index] = static_cast<std::byte>(value >> (index * 8U));
        }
        members.push_back(toxsync::sha256(bytes));
        sketch.add(members.back(), 4096U);
    }
    for (const auto& member : members) REQUIRE(sketch.possibly_contains(member));

    bool found_negative = false;
    for (std::uint64_t value = 1000U; value < 2000U; ++value) {
        std::array<std::byte, sizeof(value)> bytes{};
        for (std::size_t index = 0U; index < bytes.size(); ++index) {
            bytes[index] = static_cast<std::byte>(value >> (index * 8U));
        }
        if (!sketch.possibly_contains(toxsync::sha256(bytes))) {
            found_negative = true;
            break;
        }
    }
    REQUIRE(found_negative);

    const auto encoded = toxsync::encode_content_availability(sketch);
    REQUIRE(encoded.size() == 1152U);
    const auto decoded = toxsync::decode_content_availability(encoded, 1024U);
    REQUIRE(decoded.metadata() == sketch.metadata());
    REQUIRE(std::equal(decoded.bits().begin(), decoded.bits().end(),
                       sketch.bits().begin(), sketch.bits().end()));
    for (const auto& member : members) REQUIRE(decoded.possibly_contains(member));
    REQUIRE(decoded.estimated_false_positive_rate() < 0.01);
}

TOXSYNC_TEST(content_availability_rejects_corrupt_filter_and_reserved_header) {
    toxsync::ContentAvailabilitySketch sketch;
    sketch.reset(digest_text("manifest"));
    sketch.add(digest_text("chunk"));
    auto encoded = toxsync::encode_content_availability(sketch);

    auto corrupt = encoded;
    corrupt.back() ^= std::byte{1U};
    REQUIRE_THROWS(toxsync::decode_content_availability(corrupt));

    auto reserved = encoded;
    reserved[127] = std::byte{1U};
    REQUIRE_THROWS(toxsync::decode_content_availability(reserved));

    REQUIRE_THROWS(toxsync::decode_content_availability(encoded, 512U));
}

TOXSYNC_TEST(content_availability_build_streams_real_store_and_marks_missing_chunk) {
    test::TempDir temp;
    const auto artifact = temp.path() / "artifact.bin";
    const auto manifest = temp.path() / "artifact.txc";
    const auto store = temp.path() / "store";
    const auto bytes = test::pattern(2U * 1024U * 1024U, 0x11223344U);
    test::write_file(artifact, bytes);

    toxsync::ContentStoreOptions build_options;
    build_options.chunking = {.min_bytes = 4096U,
                              .average_bytes = 8192U,
                              .max_bytes = 16384U};
    build_options.fsync_on_commit = false;
    const auto built = toxsync::build_content_store(
        artifact, store, manifest, build_options);

    auto first = toxsync::build_content_availability(
        manifest, store, 7U);
    REQUIRE(first.manifest.manifest_digest == built.metadata.manifest_digest);
    REQUIRE(first.missing_chunks == 0U);
    REQUIRE((first.sketch.flags() & toxsync::kAvailabilityFlagComplete) != 0U);
    REQUIRE(first.available_bytes == bytes.size());

    std::vector<toxsync::ContentChunkRef> chunks;
    CollectContext context{.chunks = &chunks};
    const auto walked = toxsync::walk_content_manifest(
        manifest, &collect_chunk, &context);
    REQUIRE(walked.chunks_visited == chunks.size());
    REQUIRE(walked.bytes_visited == bytes.size());
    REQUIRE(!chunks.empty());
    std::filesystem::remove(toxsync::content_store_path(store, chunks.front().digest));

    auto second = toxsync::build_content_availability(
        manifest, store, 8U);
    REQUIRE(second.missing_chunks == 1U);
    REQUIRE(second.missing_bytes == chunks.front().length);
    REQUIRE((second.sketch.flags() & toxsync::kAvailabilityFlagComplete) == 0U);
}
