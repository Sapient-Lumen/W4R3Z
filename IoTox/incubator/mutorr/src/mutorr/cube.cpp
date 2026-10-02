#include "iotox/mutorr/cube.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <deque>
#include <limits>
#include <stdexcept>

namespace iotox::mutorr {
namespace {

std::uint64_t mix64(std::uint64_t value) noexcept {
    value += 0x9E3779B97F4A7C15ULL;
    value = (value ^ (value >> 30U)) * 0xBF58476D1CE4E5B9ULL;
    value = (value ^ (value >> 27U)) * 0x94D049BB133111EBULL;
    return value ^ (value >> 31U);
}

std::uint64_t load_u64_be(const std::uint8_t *bytes) noexcept {
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < 8U; ++index) {
        value = (value << 8U) | bytes[index];
    }
    return value;
}

std::uint64_t placement_score(const Id256 &namespace_id, const Id256 &member_id) noexcept {
    std::uint64_t state = 0x243F6A8885A308D3ULL;
    for (std::size_t lane = 0U; lane < kIdSize / 8U; ++lane) {
        const std::uint64_t namespace_lane = load_u64_be(namespace_id.bytes.data() + lane * 8U);
        const std::uint64_t member_lane = load_u64_be(member_id.bytes.data() + lane * 8U);
        state = mix64(state ^ mix64(namespace_lane + 0x9E3779B97F4A7C15ULL * (lane + 1U)));
        state = mix64(state ^ mix64(member_lane + 0xD1B54A32D192ED03ULL * (lane + 1U)));
    }
    return mix64(state ^ 0xA4093822299F31D0ULL);
}

struct Candidate {
    std::uint64_t score{0U};
    std::size_t member_index{0U};
};

bool candidate_is_better(
    const Candidate &left, const Candidate &right, std::span<const Id256> members) noexcept {
    if (left.score != right.score) {
        return left.score > right.score;
    }
    return members[left.member_index] < members[right.member_index];
}

}  // namespace

Result<Cube> Cube::build(std::span<const Id256> members, CubeConfig config) {
    if (members.empty()) {
        return Status{ErrorCode::invalid_argument, "a cube requires at least one member"};
    }
    if (config.neighbor_count == 0U && members.size() > 1U) {
        return Status{ErrorCode::invalid_argument, "neighbor count must be non-zero for a multi-member cube"};
    }
    if ((config.neighbor_count % 2U) != 0U) {
        return Status{ErrorCode::invalid_argument, "neighbor count must be even for a symmetric circle mesh"};
    }
    if (config.neighbor_count > 64U) {
        return Status{ErrorCode::invalid_argument, "neighbor count exceeds the supported bound of 64"};
    }
    if (config.replication_factor == 0U || config.replication_factor > 32U) {
        return Status{ErrorCode::invalid_argument, "replication factor must be between 1 and 32"};
    }

    Cube cube;
    cube.config_ = config;
    cube.members_.assign(members.begin(), members.end());
    std::sort(cube.members_.begin(), cube.members_.end());
    if (!cube.members_.empty() && cube.members_.front().is_zero()) {
        return Status{ErrorCode::invalid_argument, "cube membership contains the reserved zero identifier"};
    }
    if (std::adjacent_find(cube.members_.begin(), cube.members_.end()) != cube.members_.end()) {
        return Status{ErrorCode::invalid_argument, "cube membership contains a duplicate identifier"};
    }

    const std::size_t member_count = cube.members_.size();
    const std::size_t effective_degree = std::min(config.neighbor_count, member_count - 1U);
    cube.offsets_.reserve(member_count + 1U);
    cube.adjacency_.reserve(member_count * effective_degree);
    cube.offsets_.push_back(0U);

    for (std::size_t index = 0U; index < member_count; ++index) {
        if (member_count - 1U <= config.neighbor_count) {
            for (std::size_t candidate = 0U; candidate < member_count; ++candidate) {
                if (candidate != index) {
                    cube.adjacency_.push_back(candidate);
                }
            }
        } else {
            const std::size_t radius = config.neighbor_count / 2U;
            std::array<std::size_t, 64U> local{};
            std::size_t local_size = 0U;
            for (std::size_t distance = 1U; distance <= radius; ++distance) {
                local[local_size++] = (index + member_count - distance) % member_count;
                local[local_size++] = (index + distance) % member_count;
            }
            std::sort(local.begin(), local.begin() + static_cast<std::ptrdiff_t>(local_size));
            cube.adjacency_.insert(
                cube.adjacency_.end(), local.begin(), local.begin() + static_cast<std::ptrdiff_t>(local_size));
        }
        cube.offsets_.push_back(cube.adjacency_.size());
    }

    return cube;
}

const Id256 &Cube::member(std::size_t index) const {
    if (index >= members_.size()) {
        throw std::out_of_range("cube member index is out of range");
    }
    return members_[index];
}

Result<std::size_t> Cube::index_of(const Id256 &member_id) const {
    const auto iterator = std::lower_bound(members_.begin(), members_.end(), member_id);
    if (iterator == members_.end() || *iterator != member_id) {
        return Status{ErrorCode::not_found, "member is not present in this cube"};
    }
    return static_cast<std::size_t>(std::distance(members_.begin(), iterator));
}

std::span<const std::size_t> Cube::neighbor_indices(std::size_t member_index) const {
    if (member_index >= members_.size()) {
        return {};
    }
    const std::size_t begin = offsets_[member_index];
    const std::size_t end = offsets_[member_index + 1U];
    if (begin == end) {
        return {};
    }
    return std::span<const std::size_t>(adjacency_.data() + begin, end - begin);
}

Result<std::vector<Id256>> Cube::neighbors(const Id256 &member_id) const {
    auto index = index_of(member_id);
    if (!index) {
        return index.status();
    }

    const auto local = neighbor_indices(index.value());
    std::vector<Id256> output;
    output.reserve(local.size());
    for (const std::size_t neighbor : local) {
        output.push_back(members_[neighbor]);
    }
    return output;
}

std::vector<std::size_t> Cube::custodian_indices(
    const Id256 &namespace_id, std::size_t replica_count) const {
    const std::size_t requested = replica_count == 0U ? config_.replication_factor : replica_count;
    const std::size_t count = std::min({requested, members_.size(), std::size_t{32U}});
    std::vector<std::size_t> output(count);
    const std::size_t written = custodian_indices_into(namespace_id, output);
    output.resize(written);
    return output;
}

std::size_t Cube::custodian_indices_into(
    const Id256 &namespace_id, std::span<std::size_t> output) const noexcept {
    const std::size_t count = std::min({output.size(), members_.size(), std::size_t{32U}});
    if (count == 0U) {
        return 0U;
    }

    std::array<Candidate, 32U> best{};
    std::size_t best_size = 0U;
    const auto member_span = std::span<const Id256>(members_);

    for (std::size_t index = 0U; index < members_.size(); ++index) {
        const Candidate candidate{placement_score(namespace_id, members_[index]), index};
        std::size_t position = 0U;
        while (position < best_size && !candidate_is_better(candidate, best[position], member_span)) {
            ++position;
        }

        if (position >= count) {
            continue;
        }
        const std::size_t new_size = std::min(best_size + 1U, count);
        for (std::size_t move = new_size; move > position + 1U; --move) {
            best[move - 1U] = best[move - 2U];
        }
        best[position] = candidate;
        best_size = new_size;
    }

    for (std::size_t index = 0U; index < best_size; ++index) {
        output[index] = best[index].member_index;
    }
    return best_size;
}

std::vector<Id256> Cube::custodians(const Id256 &namespace_id, std::size_t replica_count) const {
    const auto indices = custodian_indices(namespace_id, replica_count);
    std::vector<Id256> output;
    output.reserve(indices.size());
    for (const std::size_t index : indices) {
        output.push_back(members_[index]);
    }
    return output;
}

bool Cube::is_custodian(
    const Id256 &member_id, const Id256 &namespace_id, std::size_t replica_count) const {
    auto index = index_of(member_id);
    if (!index) {
        return false;
    }
    const std::size_t requested = replica_count == 0U ? config_.replication_factor : replica_count;
    std::array<std::size_t, 32U> selected{};
    const std::size_t written =
        custodian_indices_into(namespace_id, std::span<std::size_t>(selected).first(std::min(requested, selected.size())));
    return std::find(selected.begin(), selected.begin() + static_cast<std::ptrdiff_t>(written), index.value()) !=
           selected.begin() + static_cast<std::ptrdiff_t>(written);
}

std::vector<CubeEdge> Cube::edges() const {
    std::vector<CubeEdge> output;
    output.reserve(edge_count());
    for (std::size_t source = 0U; source < members_.size(); ++source) {
        for (const std::size_t target : neighbor_indices(source)) {
            if (source < target) {
                output.push_back({source, target});
            }
        }
    }
    return output;
}

std::size_t Cube::max_degree() const noexcept {
    std::size_t maximum = 0U;
    for (std::size_t index = 0U; index < members_.size(); ++index) {
        maximum = std::max(maximum, offsets_[index + 1U] - offsets_[index]);
    }
    return maximum;
}

std::size_t Cube::diameter() const {
    if (members_.size() < 2U) {
        return 0U;
    }

    std::size_t maximum_distance = 0U;
    std::vector<std::size_t> distances(members_.size());
    std::deque<std::size_t> queue;

    for (std::size_t source = 0U; source < members_.size(); ++source) {
        std::fill(distances.begin(), distances.end(), std::numeric_limits<std::size_t>::max());
        distances[source] = 0U;
        queue.clear();
        queue.push_back(source);

        while (!queue.empty()) {
            const std::size_t current = queue.front();
            queue.pop_front();
            for (const std::size_t neighbor : neighbor_indices(current)) {
                if (distances[neighbor] == std::numeric_limits<std::size_t>::max()) {
                    distances[neighbor] = distances[current] + 1U;
                    queue.push_back(neighbor);
                }
            }
        }

        for (const std::size_t distance : distances) {
            if (distance == std::numeric_limits<std::size_t>::max()) {
                return std::numeric_limits<std::size_t>::max();
            }
            maximum_distance = std::max(maximum_distance, distance);
        }
    }
    return maximum_distance;
}

}  // namespace iotox::mutorr
