#include "test_harness.hpp"
#include "test_support.hpp"

#include "toxsync/head.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <optional>
#include <span>
#include <string_view>

namespace {

toxsync::Digest256 named_digest(std::string_view text) {
    return toxsync::sha256(std::as_bytes(std::span(text.data(), text.size())));
}

toxsync::MutableHead head(std::uint64_t generation,
                          toxsync::Engine engine = toxsync::Engine::range_v1) {
    toxsync::MutableHead value;
    value.engine = engine;
    value.generation = generation;
    value.namespace_id = named_digest("namespace");
    value.artifact = named_digest("artifact-" + std::to_string(generation));
    value.index = named_digest("index-" + std::to_string(generation));
    value.artifact_size = 1024U + generation;
    value.index_size = 128U + generation;
    value.block_size = engine == toxsync::Engine::range_v1 ? 4096U : 0U;
    return value;
}

bool accept_signature(void*, const toxsync::MutableHead&,
                      std::span<const std::byte,
                                toxsync::kMutableHeadSigningBytes>,
                      std::span<const std::byte, 64>) {
    return true;
}

bool reject_signature(void*, const toxsync::MutableHead&,
                      std::span<const std::byte,
                                toxsync::kMutableHeadSigningBytes>,
                      std::span<const std::byte, 64>) {
    return false;
}

} // namespace

TOXSYNC_TEST(mutable_head_policy_accepts_linked_history_and_snapshot_rebase) {
    const auto genesis = head(1U);
    auto evaluated = toxsync::evaluate_mutable_head(
        genesis, std::nullopt, &accept_signature, nullptr);
    REQUIRE(evaluated.decision == toxsync::HeadDecision::accept_genesis);
    REQUIRE(evaluated.accepted());

    auto advance = head(2U);
    advance.parent = toxsync::mutable_head_record_digest(genesis);
    evaluated = toxsync::evaluate_mutable_head(
        advance, genesis, &accept_signature, nullptr);
    REQUIRE(evaluated.decision == toxsync::HeadDecision::accept_advance);
    REQUIRE(evaluated.generation_delta == 1U);

    auto wrong_parent = head(3U);
    wrong_parent.parent = named_digest("not-the-current-record");
    evaluated = toxsync::evaluate_mutable_head(
        wrong_parent, advance, &accept_signature, nullptr);
    REQUIRE(evaluated.decision == toxsync::HeadDecision::parent_mismatch);

    wrong_parent.flags |= toxsync::kHeadFlagSnapshot;
    evaluated = toxsync::evaluate_mutable_head(
        wrong_parent, advance, &accept_signature, nullptr);
    REQUIRE(evaluated.decision == toxsync::HeadDecision::accept_snapshot);
}

TOXSYNC_TEST(mutable_head_policy_rejects_forks_downgrades_gaps_and_bad_signatures) {
    const auto current = head(10U, toxsync::Engine::content_store_v2);

    auto fork = head(10U, toxsync::Engine::content_store_v2);
    fork.artifact = named_digest("fork");
    REQUIRE(toxsync::evaluate_mutable_head(
                fork, current, &accept_signature, nullptr)
                .decision == toxsync::HeadDecision::fork);

    auto downgrade = head(11U, toxsync::Engine::range_v1);
    downgrade.parent = toxsync::mutable_head_record_digest(current);
    REQUIRE(toxsync::evaluate_mutable_head(
                downgrade, current, &accept_signature, nullptr)
                .decision == toxsync::HeadDecision::engine_downgrade);

    auto gap = head(5000U, toxsync::Engine::content_store_v2);
    gap.parent = toxsync::mutable_head_record_digest(current);
    REQUIRE(toxsync::evaluate_mutable_head(
                gap, current, &accept_signature, nullptr)
                .decision == toxsync::HeadDecision::generation_gap);

    auto next = head(11U, toxsync::Engine::content_store_v2);
    next.parent = toxsync::mutable_head_record_digest(current);
    REQUIRE(toxsync::evaluate_mutable_head(
                next, current, &reject_signature, nullptr)
                .decision == toxsync::HeadDecision::invalid_signature);
}

TOXSYNC_TEST(mutable_head_state_is_atomic_fixed_size_and_detects_corruption) {
    test::TempDir temp;
    const auto path = temp.path() / "heads" / "namespace.head";
    auto value = head(7U, toxsync::Engine::content_store_v2);
    value.flags = toxsync::kHeadFlagTreepack;
    toxsync::MutableHeadStateOptions options;
    options.fsync_on_commit = false;
    toxsync::store_mutable_head_state(path, value, options);
    const auto loaded = toxsync::load_mutable_head_state(path);
    REQUIRE(loaded.has_value());
    REQUIRE(*loaded == value);

    auto bytes = test::read_file(path);
    REQUIRE(bytes.size() == 312U);
    bytes[bytes.size() / 2U] ^= std::byte{0x80};
    test::write_file(path, bytes);
    REQUIRE_THROWS(toxsync::load_mutable_head_state(path));
    REQUIRE(!toxsync::load_mutable_head_state(temp.path() / "missing").has_value());
}

TOXSYNC_TEST(ed25519_mutable_head_signatures_round_trip_when_backend_is_present) {
    if (!toxsync::ed25519_backend_available()) return;
    toxsync::Ed25519PrivateKey private_key;
    toxsync::Ed25519PublicKey public_key;
    REQUIRE(toxsync::ed25519_generate_key(private_key, public_key));
    toxsync::Ed25519PublicKey derived;
    REQUIRE(toxsync::ed25519_public_key(private_key, derived));
    REQUIRE(derived == public_key);
    auto value = head(1U);
    REQUIRE(toxsync::sign_mutable_head(value, private_key));
    REQUIRE(toxsync::verify_mutable_head(value, public_key));
    value.artifact_size += 1U;
    REQUIRE(!toxsync::verify_mutable_head(value, public_key));
}
