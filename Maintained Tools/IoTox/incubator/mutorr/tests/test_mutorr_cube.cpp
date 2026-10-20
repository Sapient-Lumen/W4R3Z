#include "test_harness.hpp"

#include "iotox/mutorr/cube.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <numeric>
#include <random>
#include <vector>

namespace {

std::vector<iotox::mutorr::Id256> make_members(std::size_t count) {
    std::vector<iotox::mutorr::Id256> members;
    members.reserve(count);
    for (std::size_t index = 0U; index < count; ++index) {
        members.push_back(iotox::mutorr::synthetic_id(static_cast<std::uint64_t>(index + 1U), 0x4E4F4445U));
    }
    return members;
}

}  // namespace

IOTOX_TEST("thirty-device cube replaces the full mesh with sixty symmetric links") {
    const auto members = make_members(30U);
    auto cube_result = iotox::mutorr::Cube::build(members, {.neighbor_count = 4U, .replication_factor = 3U});
    IOTOX_CHECK(cube_result);
    const auto &cube = cube_result.value();

    IOTOX_CHECK(cube.size() == 30U);
    IOTOX_CHECK(cube.max_degree() == 4U);
    IOTOX_CHECK(cube.edge_count() == 60U);
    IOTOX_CHECK(cube.diameter() == 8U);

    for (std::size_t source = 0U; source < cube.size(); ++source) {
        const auto neighbors = cube.neighbor_indices(source);
        IOTOX_CHECK(neighbors.size() == 4U);
        IOTOX_CHECK(std::find(neighbors.begin(), neighbors.end(), source) == neighbors.end());
        for (const std::size_t target : neighbors) {
            const auto reverse = cube.neighbor_indices(target);
            IOTOX_CHECK(std::find(reverse.begin(), reverse.end(), source) != reverse.end());
        }
    }
}

IOTOX_TEST("cube topology is independent of discovery order") {
    auto members = make_members(30U);
    auto first = iotox::mutorr::Cube::build(members);
    IOTOX_CHECK(first);

    std::mt19937_64 generator(123456U);
    std::shuffle(members.begin(), members.end(), generator);
    auto second = iotox::mutorr::Cube::build(members);
    IOTOX_CHECK(second);

    IOTOX_CHECK(first.value().members().size() == second.value().members().size());
    IOTOX_CHECK(std::equal(
        first.value().members().begin(), first.value().members().end(), second.value().members().begin()));
    IOTOX_CHECK(first.value().edges() == second.value().edges());
}

IOTOX_TEST("small cubes collapse safely to a complete local circle") {
    const auto members = make_members(4U);
    auto cube = iotox::mutorr::Cube::build(members);
    IOTOX_CHECK(cube);
    IOTOX_CHECK(cube.value().max_degree() == 3U);
    IOTOX_CHECK(cube.value().edge_count() == 6U);
    IOTOX_CHECK(cube.value().diameter() == 1U);
}

IOTOX_TEST("single-member cube has no edges and remains its own custodian") {
    const auto members = make_members(1U);
    auto cube = iotox::mutorr::Cube::build(members);
    IOTOX_CHECK(cube);
    IOTOX_CHECK(cube.value().neighbor_indices(0U).empty());
    IOTOX_CHECK(cube.value().edge_count() == 0U);
    IOTOX_CHECK(cube.value().diameter() == 0U);

    const auto namespace_id = iotox::mutorr::synthetic_id(1U, 0x4E414D45U);
    const auto custodians = cube.value().custodians(namespace_id);
    IOTOX_CHECK(custodians.size() == 1U);
    IOTOX_CHECK(custodians.front() == members.front());
}

IOTOX_TEST("one joining peer only perturbs the local ring neighborhood") {
    auto before_members = make_members(30U);
    auto before = iotox::mutorr::Cube::build(before_members);
    IOTOX_CHECK(before);

    auto after_members = before_members;
    const auto joining = iotox::mutorr::synthetic_id(9999U, 0x4E4F4445U);
    after_members.push_back(joining);
    auto after = iotox::mutorr::Cube::build(after_members);
    IOTOX_CHECK(after);

    std::size_t changed = 0U;
    for (const auto &member : before_members) {
        auto old_neighbors = before.value().neighbors(member);
        auto new_neighbors = after.value().neighbors(member);
        IOTOX_CHECK(old_neighbors);
        IOTOX_CHECK(new_neighbors);
        if (old_neighbors.value() != new_neighbors.value()) {
            ++changed;
        }
    }
    IOTOX_CHECK_MSG(changed <= 4U, "bounded ring insertion changed too many existing neighborhoods");
}

IOTOX_TEST("rendezvous custodians are deterministic balanced and minimally disrupted") {
    const auto members = make_members(30U);
    auto cube = iotox::mutorr::Cube::build(members, {.neighbor_count = 4U, .replication_factor = 3U});
    IOTOX_CHECK(cube);

    std::vector<std::size_t> load(members.size(), 0U);
    std::array<std::size_t, 3U> fast_path{};
    for (std::size_t item = 0U; item < 30000U; ++item) {
        const auto namespace_id =
            iotox::mutorr::synthetic_id(static_cast<std::uint64_t>(item + 1U), 0x4E414D45U);
        const auto custodians = cube.value().custodian_indices(namespace_id);
        IOTOX_CHECK(custodians.size() == 3U);
        IOTOX_CHECK(cube.value().custodian_indices_into(namespace_id, fast_path) == 3U);
        IOTOX_CHECK(std::equal(custodians.begin(), custodians.end(), fast_path.begin()));
        IOTOX_CHECK(custodians[0] != custodians[1]);
        IOTOX_CHECK(custodians[1] != custodians[2]);
        IOTOX_CHECK(custodians[0] != custodians[2]);
        for (const std::size_t selected : custodians) {
            ++load[selected];
        }
    }

    const auto [minimum, maximum] = std::minmax_element(load.begin(), load.end());
    IOTOX_CHECK(*minimum > 2600U);
    IOTOX_CHECK(*maximum < 3400U);

    auto expanded_members = members;
    const auto joining = iotox::mutorr::synthetic_id(60000U, 0x4E4F4445U);
    expanded_members.push_back(joining);
    auto expanded = iotox::mutorr::Cube::build(expanded_members, {.neighbor_count = 4U, .replication_factor = 3U});
    IOTOX_CHECK(expanded);

    for (std::size_t item = 0U; item < 3000U; ++item) {
        const auto namespace_id =
            iotox::mutorr::synthetic_id(static_cast<std::uint64_t>(item + 100000U), 0x4E414D45U);
        const auto old_set = cube.value().custodians(namespace_id);
        const auto new_set = expanded.value().custodians(namespace_id);
        for (const auto &member : new_set) {
            if (member != joining) {
                IOTOX_CHECK(std::find(old_set.begin(), old_set.end(), member) != old_set.end());
            }
        }
    }
}

IOTOX_TEST("invalid cube configurations fail closed") {
    const auto members = make_members(5U);
    IOTOX_CHECK(!iotox::mutorr::Cube::build({}, {}));
    IOTOX_CHECK(!iotox::mutorr::Cube::build(members, {.neighbor_count = 3U, .replication_factor = 3U}));

    auto duplicates = members;
    duplicates.push_back(members.front());
    IOTOX_CHECK(!iotox::mutorr::Cube::build(duplicates));

    auto with_zero = members;
    with_zero.front() = {};
    IOTOX_CHECK(!iotox::mutorr::Cube::build(with_zero));
}
