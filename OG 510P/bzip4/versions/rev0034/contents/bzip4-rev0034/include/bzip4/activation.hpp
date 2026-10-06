#pragma once

#include <cstddef>
#include <cstdint>

namespace bzip4 {

enum class WakeMode {
    active_only,
    all_retained,
};

struct ActivationPolicy {
    std::size_t retained_background_workers{};
    std::size_t max_active_lanes{}; // 0 means no policy cap.
    std::size_t minimum_blocks_per_active_lane{1};
    std::size_t minimum_bytes_per_active_lane{1};
    bool caller_participates{true};
    WakeMode wake_mode{WakeMode::active_only};
};

struct ActivationPlan {
    std::size_t active_lanes{};
    std::size_t active_background_workers{};
    std::size_t workers_notified{};
    std::size_t blocks{};
    std::size_t logical_bytes{};
    bool caller_participates{};
};

/**
 * Centralized floor-grain planning. A configured minimum is a true minimum:
 * five blocks at four blocks/lane activates one lane, never two.
 */
[[nodiscard]] ActivationPlan make_activation_plan(
    std::size_t block_count,
    std::size_t logical_bytes,
    const ActivationPolicy& policy) noexcept;

} // namespace bzip4
