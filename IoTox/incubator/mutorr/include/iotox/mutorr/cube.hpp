#pragma once

#include "iotox/mutorr/id.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <span>
#include <vector>

namespace iotox::mutorr {

struct CubeConfig {
    // The normal topology uses an even number so each member takes the same
    // number of clockwise and counter-clockwise ring neighbors.
    std::size_t neighbor_count{4U};
    std::size_t replication_factor{3U};
};

struct CubeEdge {
    std::size_t first{0U};
    std::size_t second{0U};

    friend bool operator==(const CubeEdge &, const CubeEdge &) = default;
};

// A Cube is a deterministic, namespace-scoped membership snapshot. Every peer
// given the same member set and configuration computes the same bounded-degree
// circle mesh and the same rendezvous-hashed custodian set.
class Cube {
  public:
    [[nodiscard]] static Result<Cube> build(
        std::span<const Id256> members, CubeConfig config = {});

    [[nodiscard]] std::size_t size() const noexcept { return members_.size(); }
    [[nodiscard]] bool empty() const noexcept { return members_.empty(); }
    [[nodiscard]] const CubeConfig &config() const noexcept { return config_; }
    [[nodiscard]] std::span<const Id256> members() const noexcept { return members_; }
    [[nodiscard]] const Id256 &member(std::size_t index) const;

    [[nodiscard]] Result<std::size_t> index_of(const Id256 &member_id) const;
    [[nodiscard]] std::span<const std::size_t> neighbor_indices(std::size_t member_index) const;
    [[nodiscard]] Result<std::vector<Id256>> neighbors(const Id256 &member_id) const;

    [[nodiscard]] std::vector<std::size_t> custodian_indices(
        const Id256 &namespace_id, std::size_t replica_count = 0U) const;
    // Allocation-free hot path. The output span length is the requested
    // replica count; at most 32 entries are filled.
    [[nodiscard]] std::size_t custodian_indices_into(
        const Id256 &namespace_id, std::span<std::size_t> output) const noexcept;
    [[nodiscard]] std::vector<Id256> custodians(
        const Id256 &namespace_id, std::size_t replica_count = 0U) const;
    [[nodiscard]] bool is_custodian(
        const Id256 &member_id, const Id256 &namespace_id, std::size_t replica_count = 0U) const;

    [[nodiscard]] std::vector<CubeEdge> edges() const;
    [[nodiscard]] std::size_t edge_count() const noexcept { return adjacency_.size() / 2U; }
    [[nodiscard]] std::size_t max_degree() const noexcept;
    [[nodiscard]] std::size_t diameter() const;

  private:
    CubeConfig config_{};
    std::vector<Id256> members_;
    std::vector<std::size_t> offsets_;
    std::vector<std::size_t> adjacency_;
};

}  // namespace iotox::mutorr
