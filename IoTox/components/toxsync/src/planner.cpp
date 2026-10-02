#include "toxsync/planner.hpp"
#include "toxsync/rolling_checksum.hpp"

#include <algorithm>
#include <bit>
#include <cerrno>
#include <cstring>
#include <fstream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace toxsync {
namespace {

class RandomAccessReader final {
public:
    explicit RandomAccessReader(const std::filesystem::path& path)
        : path_text_(path.string()) {
#if defined(__unix__) || defined(__APPLE__)
        fd_ = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
        if (fd_ < 0) throw std::runtime_error("cannot open basis file: " + path_text_ + ": " + std::strerror(errno));
#if defined(POSIX_FADV_SEQUENTIAL)
        (void)::posix_fadvise(fd_, 0, 0, POSIX_FADV_SEQUENTIAL);
#endif
#else
        input_.open(path, std::ios::binary);
        if (!input_) throw std::runtime_error("cannot open basis file: " + path_text_);
#endif
    }

    ~RandomAccessReader() {
#if defined(__unix__) || defined(__APPLE__)
        if (fd_ >= 0) (void)::close(fd_);
#endif
    }

    RandomAccessReader(const RandomAccessReader&) = delete;
    RandomAccessReader& operator=(const RandomAccessReader&) = delete;

    void read_exact(std::uint64_t offset, std::span<std::byte> output) {
        if (output.empty()) return;
        ++read_calls_;
#if defined(__unix__) || defined(__APPLE__)
        std::size_t done{};
        while (done < output.size()) {
            const auto absolute = offset + done;
            if (absolute > static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
                throw std::runtime_error("basis offset exceeds platform file limits");
            }
            const auto result = ::pread(fd_, output.data() + done, output.size() - done,
                                        static_cast<off_t>(absolute));
            if (result > 0) {
                done += static_cast<std::size_t>(result);
                continue;
            }
            if (result < 0 && errno == EINTR) continue;
            if (result == 0) throw std::runtime_error("basis file ended during scan: " + path_text_);
            throw std::runtime_error("basis read failed: " + path_text_ + ": " + std::strerror(errno));
        }
#else
        input_.clear();
        input_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        if (!input_) throw std::runtime_error("basis seek failed: " + path_text_);
        input_.read(reinterpret_cast<char*>(output.data()), static_cast<std::streamsize>(output.size()));
        if (static_cast<std::size_t>(input_.gcount()) != output.size()) {
            throw std::runtime_error("basis file ended during scan: " + path_text_);
        }
#endif
    }

    [[nodiscard]] std::uint64_t read_calls() const noexcept { return read_calls_; }

private:
    std::string path_text_;
    std::uint64_t read_calls_{};
#if defined(__unix__) || defined(__APPLE__)
    int fd_{-1};
#else
    std::ifstream input_;
#endif
};

class WeakIndex final {
public:
    WeakIndex(const Index& index, std::uint32_t length)
        : index_(index) {
        for (const auto& block : index.blocks) {
            if (block.length == length) ++candidate_count_;
        }
        if (candidate_count_ == 0U) return;
        if (candidate_count_ == 1U) {
            for (std::uint32_t i = 0; i < index.blocks.size(); ++i) {
                if (index.blocks[i].length == length) {
                    single_ = i;
                    return;
                }
            }
        }
        if (candidate_count_ > std::numeric_limits<std::size_t>::max() / 2U) {
            throw std::length_error("toxsync weak index is too large");
        }
        const auto requested = std::max<std::size_t>(2U, candidate_count_ * 2U);
        const auto bucket_count = std::bit_ceil(requested);
        heads_.assign(bucket_count, kNone);
        next_ = std::make_unique_for_overwrite<std::uint32_t[]>(index.blocks.size());
        mask_ = bucket_count - 1U;
        for (std::uint32_t i = 0; i < index.blocks.size(); ++i) {
            if (index.blocks[i].length != length) continue;
            const auto bucket = mix(index.blocks[i].weak) & mask_;
            next_[i] = heads_[bucket];
            heads_[bucket] = i;
        }
    }

    template <typename Callback>
    void for_each(std::uint32_t weak, Callback&& callback) const {
        if (candidate_count_ == 0U) return;
        if (candidate_count_ == 1U) {
            if (index_.blocks[single_].weak == weak) callback(single_);
            return;
        }
        auto cursor = heads_[mix(weak) & mask_];
        while (cursor != kNone) {
            if (index_.blocks[cursor].weak == weak) callback(cursor);
            cursor = next_[cursor];
        }
    }

    [[nodiscard]] std::size_t candidate_count() const noexcept { return candidate_count_; }
    [[nodiscard]] std::size_t resident_bytes() const noexcept {
        return heads_.capacity() * sizeof(std::uint32_t) +
               (next_ == nullptr ? 0U : index_.blocks.size() * sizeof(std::uint32_t));
    }

private:
    static constexpr std::uint32_t kNone = std::numeric_limits<std::uint32_t>::max();
    static std::size_t mix(std::uint32_t value) noexcept {
        return static_cast<std::size_t>(value ^ (value >> 16U));
    }

    const Index& index_;
    std::vector<std::uint32_t> heads_;
    std::unique_ptr<std::uint32_t[]> next_;
    std::size_t mask_{};
    std::size_t candidate_count_{};
    std::uint32_t single_{kNone};
};

[[nodiscard]] std::uint64_t checked_file_size(const std::filesystem::path& path) {
    std::error_code error;
    const auto size = std::filesystem::file_size(path, error);
    if (error) throw std::runtime_error("cannot determine basis size: " + path.string() + ": " + error.message());
    return size;
}

void probe_aligned(const Index& index,
                   RandomAccessReader& input,
                   std::uint64_t basis_size,
                   std::size_t scan_buffer_bytes,
                   std::uint64_t required_reuse_bytes,
                   std::vector<std::uint64_t>& offsets,
                   PlanStats& stats) {
    if (index.blocks.empty() || basis_size == 0U) return;
    const auto block_bytes = static_cast<std::size_t>(index.block_size);
    const auto requested = std::max(scan_buffer_bytes, block_bytes);
    const auto buffer_bytes = (requested / block_bytes) * block_bytes;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    stats.temporary_bytes_peak = std::max<std::uint64_t>(
        stats.temporary_bytes_peak, static_cast<std::uint64_t>(buffer_bytes));

    std::size_t block_index{};
    std::uint64_t target_offset{};
    while (block_index < index.blocks.size() && target_offset < basis_size) {
        std::size_t batch_end = block_index;
        std::size_t batch_length{};
        while (batch_end < index.blocks.size()) {
            const auto length = static_cast<std::size_t>(index.blocks[batch_end].length);
            if (target_offset + batch_length + length > basis_size) break;
            if (batch_length != 0U && length > buffer_bytes - batch_length) break;
            batch_length += length;
            ++batch_end;
            if (batch_length == buffer_bytes) break;
        }
        if (batch_end == block_index) break;

        input.read_exact(target_offset, std::span<std::byte>(buffer.get(), batch_length));
        std::size_t local_offset{};
        for (auto i = block_index; i < batch_end; ++i) {
            const auto length = static_cast<std::size_t>(index.blocks[i].length);
            ++stats.aligned_blocks_checked;
            ++stats.strong_checks;
            if (fast_hash128(std::span<const std::byte>(buffer.get() + local_offset, length)) ==
                index.blocks[i].strong) {
                offsets[i] = target_offset + local_offset;
                ++stats.aligned_blocks_matched;
                stats.aligned_reused_bytes += length;
            }
            local_offset += length;
        }
        target_offset += batch_length;
        stats.aligned_bytes_examined = target_offset;
        block_index = batch_end;

        // Adaptive mode can abandon the aligned pass as soon as reaching the
        // configured reuse threshold becomes mathematically impossible. This
        // preserves every match already found and lets rolling search continue
        // from those anchors without paying for a doomed full second pass.
        if (required_reuse_bytes != 0U) {
            const auto aligned_limit = std::min(index.target_size, basis_size);
            const auto remaining_matchable = target_offset < aligned_limit
                ? aligned_limit - target_offset
                : 0U;
            if (stats.aligned_reused_bytes + remaining_matchable < required_reuse_bytes) {
                stats.aligned_probe_aborted_early = true;
                return;
            }
        }
    }
}

[[nodiscard]] bool adaptive_aligned_plan_is_enough(const Index& index,
                                                    const PlannerOptions& options,
                                                    const PlanStats& stats) noexcept {
    if (index.target_size == 0U) return true;
    return stats.aligned_reused_bytes * 100U >=
           index.target_size * options.adaptive_min_aligned_reuse_percent;
}

void scan_length(const Index& index,
                 RandomAccessReader& input,
                 std::uint64_t basis_size,
                 std::uint32_t window_length,
                 std::size_t scan_buffer_bytes,
                 std::vector<std::uint64_t>& offsets,
                 PlanStats& stats) {
    if (window_length == 0U || basis_size < window_length) return;

    std::size_t remaining{};
    for (std::size_t i = 0; i < index.blocks.size(); ++i) {
        if (index.blocks[i].length == window_length && offsets[i] == kMissingBasisOffset) ++remaining;
    }
    if (remaining == 0U) return;
    ++stats.rolling_passes;

    WeakIndex lookup(index, window_length);
    const auto max_starts = std::max<std::size_t>(1U, scan_buffer_bytes);
    const auto max_buffer = max_starts + static_cast<std::size_t>(window_length) - 1U;
    if (max_buffer < max_starts) throw std::length_error("planner scan buffer size overflow");
    const auto actual_buffer = static_cast<std::size_t>(
        std::min<std::uint64_t>(basis_size, static_cast<std::uint64_t>(max_buffer)));
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(actual_buffer);
    stats.temporary_bytes_peak = std::max<std::uint64_t>(
        stats.temporary_bytes_peak,
        static_cast<std::uint64_t>(actual_buffer) + static_cast<std::uint64_t>(lookup.resident_bytes()));

    const auto final_start = basis_size - window_length;
    std::uint64_t position{};
    while (position <= final_start && remaining != 0U) {
        const auto available_starts = final_start - position + 1U;
        const auto starts = static_cast<std::size_t>(
            std::min<std::uint64_t>(available_starts, static_cast<std::uint64_t>(max_starts)));
        const auto needed = starts + static_cast<std::size_t>(window_length) - 1U;
        input.read_exact(position, std::span<std::byte>(buffer.get(), needed));
        const auto chunk_end = position + starts;
        auto local_position = position;
        auto local_offset = std::size_t{};
        auto rolling = RollingChecksum::compute(
            std::span<const std::byte>(buffer.get(), static_cast<std::size_t>(window_length)));

        while (local_position < chunk_end && remaining != 0U) {
            ++stats.scanned_windows;
            bool weak_hit{};
            bool strong_ready{};
            bool any_known_match{};
            Hash128 strong{};
            const auto weak = rolling.value();
            const auto candidate = std::span<const std::byte>(
                buffer.get() + local_offset, static_cast<std::size_t>(window_length));
            lookup.for_each(weak, [&](std::uint32_t target_index) {
                weak_hit = true;
                if (!strong_ready) {
                    strong = fast_hash128(candidate);
                    strong_ready = true;
                    ++stats.strong_checks;
                }
                if (index.blocks[target_index].strong != strong) return;
                any_known_match = true;
                if (offsets[target_index] == kMissingBasisOffset) {
                    offsets[target_index] = local_position;
                    --remaining;
                }
            });
            if (weak_hit) ++stats.weak_hits;
            if (remaining == 0U) break;

            if (any_known_match) {
                local_position += window_length;
                local_offset += window_length;
                if (local_position >= chunk_end) break;
                rolling = RollingChecksum::compute(std::span<const std::byte>(
                    buffer.get() + local_offset, static_cast<std::size_t>(window_length)));
                continue;
            }

            ++local_position;
            ++local_offset;
            if (local_position >= chunk_end) break;
            rolling.roll(buffer[local_offset - 1U],
                         buffer[local_offset + static_cast<std::size_t>(window_length) - 1U]);
        }
        position = local_position;
    }
}

} // namespace

Plan plan_file(const Index& index, const std::filesystem::path& basis, const PlannerOptions& options) {
    index.validate();
    if (options.aligned_buffer_bytes == 0U) {
        throw std::invalid_argument("planner aligned buffer size must be nonzero");
    }
    if (options.rolling_buffer_bytes == 0U) {
        throw std::invalid_argument("planner rolling buffer size must be nonzero");
    }

    Plan plan;
    plan.basis_offsets.assign(index.blocks.size(), kMissingBasisOffset);
    plan.stats.basis_size = checked_file_size(basis);
    if (plan.stats.basis_size > options.max_basis_size) throw std::runtime_error("basis exceeds configured size limit");

    if (options.adaptive_min_aligned_reuse_percent > 100U) {
        throw std::invalid_argument("adaptive aligned reuse threshold must be at most 100 percent");
    }

    if (!index.blocks.empty() && plan.stats.basis_size != 0U) {
        RandomAccessReader input(basis);
        const bool use_aligned_probe = options.search_mode != PlannerSearchMode::exhaustive_rolling;
        if (use_aligned_probe) {
            const auto required_reuse_bytes = options.search_mode == PlannerSearchMode::adaptive
                ? (index.target_size * options.adaptive_min_aligned_reuse_percent + 99U) / 100U
                : 0U;
            probe_aligned(index, input, plan.stats.basis_size, options.aligned_buffer_bytes,
                          required_reuse_bytes, plan.basis_offsets, plan.stats);
        }
        const bool use_rolling = options.search_mode == PlannerSearchMode::exhaustive_rolling ||
            (options.search_mode == PlannerSearchMode::adaptive &&
             !adaptive_aligned_plan_is_enough(index, options, plan.stats));
        if (use_rolling) {
            scan_length(index, input, plan.stats.basis_size, index.block_size, options.rolling_buffer_bytes,
                        plan.basis_offsets, plan.stats);
            const auto tail_length = index.blocks.back().length;
            if (tail_length != index.block_size) {
                scan_length(index, input, plan.stats.basis_size, tail_length, options.rolling_buffer_bytes,
                            plan.basis_offsets, plan.stats);
            }
        }
        plan.stats.basis_read_calls = input.read_calls();
    }

    std::uint64_t target_offset{};
    for (std::size_t i = 0; i < index.blocks.size(); ++i) {
        const auto length = static_cast<std::uint64_t>(index.blocks[i].length);
        if (plan.basis_offsets[i] == kMissingBasisOffset) {
            plan.stats.missing_bytes += length;
            if (!plan.missing_ranges.empty() &&
                plan.missing_ranges.back().offset + plan.missing_ranges.back().length == target_offset) {
                plan.missing_ranges.back().length += length;
            } else {
                plan.missing_ranges.push_back({target_offset, length});
            }
        } else {
            ++plan.stats.matched_blocks;
            plan.stats.reused_bytes += length;
        }
        target_offset += length;
    }
    return plan;
}

} // namespace toxsync
