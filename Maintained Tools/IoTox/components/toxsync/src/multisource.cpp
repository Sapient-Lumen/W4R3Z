#include "toxsync/multisource.hpp"

#include <algorithm>
#include <bit>
#include <limits>
#include <stdexcept>
#include <utility>

namespace toxsync {
namespace {

[[nodiscard]] bool bit_at(std::span<const std::byte> bytes,
                          std::uint64_t index) noexcept {
    const auto byte_index = static_cast<std::size_t>(index / 8U);
    const auto bit_index = static_cast<unsigned>(index % 8U);
    if (byte_index >= bytes.size()) return false;
    return (std::to_integer<unsigned char>(bytes[byte_index]) &
            static_cast<unsigned char>(1U << bit_index)) != 0U;
}

[[nodiscard]] std::size_t checked_add(std::size_t left,
                                      std::size_t right,
                                      const char* message) {
    if (left > std::numeric_limits<std::size_t>::max() - right) {
        throw std::length_error(message);
    }
    return left + right;
}

[[nodiscard]] std::size_t checked_multiply(std::size_t left,
                                           std::size_t right,
                                           const char* message) {
    if (left != 0U && right > std::numeric_limits<std::size_t>::max() / left) {
        throw std::length_error(message);
    }
    return left * right;
}

[[nodiscard]] std::size_t request_table_capacity(std::size_t maximum_inflight) {
    const auto doubled = checked_multiply(
        std::max<std::size_t>(1U, maximum_inflight), 2U,
        "multi-source request table size overflows");
    constexpr auto digits = std::numeric_limits<std::size_t>::digits;
    const auto largest_power = std::size_t{1U} << (digits - 1U);
    if (doubled > largest_power) {
        throw std::length_error("multi-source request table cannot be represented");
    }
    return std::bit_ceil(std::max<std::size_t>(2U, doubled));
}

} // namespace

class MultiSourceScheduler::Impl final {
public:
    static constexpr std::uint32_t kNoPeer =
        std::numeric_limits<std::uint32_t>::max();

    // A zero peer id is the empty-slot sentinel; public peer ids are required
    // to be nonzero. The slot remains compact and cache-friendly for the
    // expected small-computer deployment while allowing a runtime-sized set.
    struct PeerSlot {
        SourcePeerId id{};
        std::uint64_t useful_bytes_per_second{};
        std::uint32_t recent_failures{};
        std::uint16_t maximum_lanes{1U};
        std::uint16_t active_lanes{};
    };

    union AvailabilityState {
        std::uint32_t inline_mask;
        std::uint32_t dynamic_count;

        constexpr AvailabilityState() noexcept : inline_mask(0U) {}
    };

    // Up to 32 peers use availability.inline_mask. Larger configurations use
    // dynamic_availability and availability.dynamic_count. This preserves the
    // old one-AND/popcount hot path for common deployments without imposing a
    // protocol-wide peer ceiling.
    struct ChunkSlot {
        std::uint64_t request_id{};
        SourcePeerId last_failed_peer{};
        std::uint32_t assigned_peer{kNoPeer};
        AvailabilityState availability{};
        std::uint16_t attempts{};
        ScheduledChunkState state{ScheduledChunkState::pending};
        std::uint8_t reserved{};
    };

    enum class RequestSlotState : std::uint8_t {
        empty,
        occupied,
        tombstone,
    };

    struct RequestSlot {
        std::uint64_t request_id{};
        std::uint32_t chunk_local{};
        RequestSlotState state{RequestSlotState::empty};
    };

    explicit Impl(MultiSourceSchedulerLimits requested) : limits(requested) {
        if (limits.maximum_peers == 0U || limits.maximum_window_chunks == 0U ||
            limits.maximum_lanes_per_peer == 0U ||
            limits.maximum_attempts_per_chunk == 0U ||
            limits.maximum_inflight_requests == 0U ||
            limits.workspace_budget_bytes == 0U) {
            throw std::invalid_argument(
                "multi-source scheduler limits and budgets must be nonzero");
        }
        if (limits.maximum_peers >
            static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
            throw std::invalid_argument(
                "multi-source scheduler peer count exceeds uint32 indexing");
        }
        if (limits.maximum_window_chunks >
            static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max())) {
            throw std::invalid_argument(
                "multi-source scheduler window exceeds uint32 indexing");
        }

        const auto possible_inflight = limits.maximum_peers >
                std::numeric_limits<std::size_t>::max() /
                    static_cast<std::size_t>(limits.maximum_lanes_per_peer)
            ? std::numeric_limits<std::size_t>::max()
            : limits.maximum_peers *
                  static_cast<std::size_t>(limits.maximum_lanes_per_peer);
        maximum_inflight = std::min(
            limits.maximum_inflight_requests, possible_inflight);
        if (maximum_inflight == 0U) {
            throw std::invalid_argument(
                "multi-source scheduler has no representable in-flight capacity");
        }
        request_table_slots = request_table_capacity(maximum_inflight);

        inline_availability = limits.maximum_peers <= 32U;
        if (!inline_availability) {
            availability_words_per_chunk =
                checked_add(limits.maximum_peers, 63U,
                            "multi-source availability word count overflows") /
                64U;
            availability_word_count = checked_multiply(
                availability_words_per_chunk, limits.maximum_window_chunks,
                "multi-source availability matrix overflows");
        }

        retained_bytes = calculate_resident_bytes();
        if (retained_bytes > limits.workspace_budget_bytes) {
            throw std::length_error(
                "multi-source scheduler exceeds configured workspace budget");
        }

        peers = std::make_unique_for_overwrite<PeerSlot[]>(limits.maximum_peers);
        chunks = std::make_unique_for_overwrite<ChunkSlot[]>(
            limits.maximum_window_chunks);
        heap_storage = std::make_unique_for_overwrite<std::uint32_t[]>(
            checked_multiply(limits.maximum_window_chunks, 2U,
                             "multi-source heap storage overflows"));
        if (limits.window_storage == MultiSourceWindowStorage::owned) {
            owned_refs = std::make_unique_for_overwrite<ContentChunkRef[]>(
                limits.maximum_window_chunks);
        }
        requests = std::make_unique_for_overwrite<RequestSlot[]>(
            request_table_slots);
        if (!inline_availability) {
            dynamic_availability = std::make_unique_for_overwrite<std::uint64_t[]>(
                availability_word_count);
            capacity_words = std::make_unique_for_overwrite<std::uint64_t[]>(
                availability_words_per_chunk);
        }
        for (std::size_t index = 0U; index < limits.maximum_peers; ++index) {
            peers[index] = PeerSlot{};
        }
        for (std::size_t index = 0U; index < request_table_slots; ++index) {
            requests[index] = RequestSlot{};
        }
        if (!inline_availability) {
            std::fill_n(dynamic_availability.get(), availability_word_count, 0U);
            std::fill_n(capacity_words.get(), availability_words_per_chunk, 0U);
        }
    }

    [[nodiscard]] std::size_t calculate_resident_bytes() const {
        std::size_t bytes = sizeof(Impl);
        bytes = checked_add(
            bytes,
            checked_multiply(limits.maximum_peers, sizeof(PeerSlot),
                             "multi-source peer storage overflows"),
            "multi-source retained storage overflows");
        bytes = checked_add(
            bytes,
            checked_multiply(limits.maximum_window_chunks, sizeof(ChunkSlot),
                             "multi-source chunk storage overflows"),
            "multi-source retained storage overflows");
        bytes = checked_add(
            bytes,
            checked_multiply(
                checked_multiply(limits.maximum_window_chunks, 2U,
                                 "multi-source heap storage overflows"),
                sizeof(std::uint32_t),
                "multi-source heap storage overflows"),
            "multi-source retained storage overflows");
        if (limits.window_storage == MultiSourceWindowStorage::owned) {
            bytes = checked_add(
                bytes,
                checked_multiply(limits.maximum_window_chunks,
                                 sizeof(ContentChunkRef),
                                 "multi-source owned window overflows"),
                "multi-source retained storage overflows");
        }
        bytes = checked_add(
            bytes,
            checked_multiply(request_table_slots, sizeof(RequestSlot),
                             "multi-source request storage overflows"),
            "multi-source retained storage overflows");
        if (!inline_availability) {
            bytes = checked_add(
                bytes,
                checked_multiply(availability_word_count, sizeof(std::uint64_t),
                                 "multi-source availability storage overflows"),
                "multi-source retained storage overflows");
            bytes = checked_add(
                bytes,
                checked_multiply(availability_words_per_chunk,
                                 sizeof(std::uint64_t),
                                 "multi-source capacity storage overflows"),
                "multi-source retained storage overflows");
        }
        return bytes;
    }

    [[nodiscard]] std::size_t request_hash(
        std::uint64_t request_id) const noexcept {
        // SplitMix64 finalizer. The table size is a power of two, so masking is
        // sufficient after the avalanche step.
        auto value = request_id;
        value ^= value >> 30U;
        value *= 0xbf58476d1ce4e5b9ULL;
        value ^= value >> 27U;
        value *= 0x94d049bb133111ebULL;
        value ^= value >> 31U;
        return static_cast<std::size_t>(value) & (request_table_slots - 1U);
    }

    [[nodiscard]] std::size_t find_request(
        std::uint64_t request_id) const noexcept {
        auto slot = request_hash(request_id);
        for (std::size_t probe = 0U; probe < request_table_slots; ++probe) {
            const auto& entry = requests[slot];
            if (entry.state == RequestSlotState::empty) {
                return request_table_slots;
            }
            if (entry.state == RequestSlotState::occupied &&
                entry.request_id == request_id) {
                return slot;
            }
            slot = (slot + 1U) & (request_table_slots - 1U);
        }
        return request_table_slots;
    }

    void insert_request(std::uint64_t request_id, std::size_t chunk_local) {
        if (active_requests >= maximum_inflight) {
            throw std::runtime_error(
                "multi-source global in-flight capacity exhausted");
        }
        auto slot = request_hash(request_id);
        auto first_tombstone = request_table_slots;
        for (std::size_t probe = 0U; probe < request_table_slots; ++probe) {
            auto& entry = requests[slot];
            if (entry.state == RequestSlotState::occupied) {
                if (entry.request_id == request_id) {
                    throw std::invalid_argument(
                        "multi-source request id is already in flight");
                }
            } else if (entry.state == RequestSlotState::tombstone) {
                if (first_tombstone == request_table_slots) {
                    first_tombstone = slot;
                }
            } else {
                const auto destination = first_tombstone == request_table_slots
                    ? slot
                    : first_tombstone;
                requests[destination] = RequestSlot{
                    .request_id = request_id,
                    .chunk_local = static_cast<std::uint32_t>(chunk_local),
                    .state = RequestSlotState::occupied,
                };
                ++active_requests;
                return;
            }
            slot = (slot + 1U) & (request_table_slots - 1U);
        }
        if (first_tombstone != request_table_slots) {
            requests[first_tombstone] = RequestSlot{
                .request_id = request_id,
                .chunk_local = static_cast<std::uint32_t>(chunk_local),
                .state = RequestSlotState::occupied,
            };
            ++active_requests;
            return;
        }
        throw std::runtime_error("multi-source request table is full");
    }

    void erase_request_slot(std::size_t slot) noexcept {
        if (slot >= request_table_slots ||
            requests[slot].state != RequestSlotState::occupied) {
            return;
        }
        requests[slot].request_id = 0U;
        requests[slot].chunk_local = 0U;
        requests[slot].state = RequestSlotState::tombstone;
        if (active_requests != 0U) --active_requests;
    }

    void erase_request(std::uint64_t request_id) noexcept {
        erase_request_slot(find_request(request_id));
    }

    void clear_requests() noexcept {
        for (std::size_t index = 0U; index < request_table_slots; ++index) {
            requests[index] = RequestSlot{};
        }
        active_requests = 0U;
    }

    [[nodiscard]] std::size_t find_peer(SourcePeerId id) const noexcept {
        if (id == 0U) return limits.maximum_peers;
        for (std::size_t index = 0U; index < limits.maximum_peers; ++index) {
            if (peers[index].id == id) return index;
        }
        return limits.maximum_peers;
    }

    [[nodiscard]] std::size_t find_or_create_peer(SourcePeerId id) {
        auto index = find_peer(id);
        if (index != limits.maximum_peers) return index;
        for (index = 0U; index < limits.maximum_peers; ++index) {
            if (peers[index].id == 0U) {
                peers[index] = PeerSlot{.id = id};
                ++peer_count;
                return index;
            }
        }
        throw std::runtime_error(
            "multi-source scheduler peer capacity exhausted");
    }

    [[nodiscard]] std::uint64_t* availability_words(
        std::size_t chunk_local) noexcept {
        return dynamic_availability.get() +
            chunk_local * availability_words_per_chunk;
    }

    [[nodiscard]] const std::uint64_t* availability_words(
        std::size_t chunk_local) const noexcept {
        return dynamic_availability.get() +
            chunk_local * availability_words_per_chunk;
    }

    [[nodiscard]] bool available(std::size_t peer_index,
                                 std::size_t chunk_local) const noexcept {
        if (inline_availability) {
            const auto bit = std::uint32_t{1U} <<
                static_cast<unsigned>(peer_index);
            return (chunks[chunk_local].availability.inline_mask & bit) != 0U;
        }
        const auto word = peer_index / 64U;
        const auto bit = static_cast<unsigned>(peer_index % 64U);
        return (availability_words(chunk_local)[word] &
                (std::uint64_t{1U} << bit)) != 0U;
    }

    void set_available(std::size_t peer_index,
                       std::size_t chunk_local,
                       bool value) noexcept {
        auto& chunk = chunks[chunk_local];
        if (inline_availability) {
            const auto bit = std::uint32_t{1U} <<
                static_cast<unsigned>(peer_index);
            chunk.availability.inline_mask = value
                ? (chunk.availability.inline_mask | bit)
                : (chunk.availability.inline_mask & ~bit);
            return;
        }
        const auto word_index = peer_index / 64U;
        const auto bit_index = static_cast<unsigned>(peer_index % 64U);
        const auto bit = std::uint64_t{1U} << bit_index;
        auto& word = availability_words(chunk_local)[word_index];
        const bool previous = (word & bit) != 0U;
        if (previous == value) return;
        if (value) {
            word |= bit;
            ++chunk.availability.dynamic_count;
        } else {
            word &= ~bit;
            if (chunk.availability.dynamic_count != 0U) {
                --chunk.availability.dynamic_count;
            }
        }
    }

    [[nodiscard]] std::uint32_t rarity(
        std::size_t chunk_local) const noexcept {
        const auto& chunk = chunks[chunk_local];
        return inline_availability
            ? static_cast<std::uint32_t>(
                  std::popcount(chunk.availability.inline_mask))
            : chunk.availability.dynamic_count;
    }

    [[nodiscard]] bool any_available(
        std::size_t chunk_local) const noexcept {
        const auto& chunk = chunks[chunk_local];
        return inline_availability
            ? chunk.availability.inline_mask != 0U
            : chunk.availability.dynamic_count != 0U;
    }

    [[nodiscard]] bool refresh_capacity() noexcept {
        if (active_requests >= maximum_inflight) return false;
        if (inline_availability) {
            inline_capacity_mask = 0U;
            for (std::size_t index = 0U; index < limits.maximum_peers; ++index) {
                const auto& peer = peers[index];
                if (peer.id != 0U && peer.active_lanes < peer.maximum_lanes) {
                    inline_capacity_mask |= std::uint32_t{1U} <<
                        static_cast<unsigned>(index);
                }
            }
            return inline_capacity_mask != 0U;
        }
        std::fill_n(capacity_words.get(), availability_words_per_chunk, 0U);
        bool any{};
        for (std::size_t index = 0U; index < limits.maximum_peers; ++index) {
            const auto& peer = peers[index];
            if (peer.id == 0U || peer.active_lanes >= peer.maximum_lanes) {
                continue;
            }
            capacity_words[index / 64U] |=
                std::uint64_t{1U} << static_cast<unsigned>(index % 64U);
            any = true;
        }
        return any;
    }

    [[nodiscard]] bool has_capacity_source(
        std::size_t chunk_local) const noexcept {
        if (inline_availability) {
            return (chunks[chunk_local].availability.inline_mask &
                    inline_capacity_mask) != 0U;
        }
        const auto* words = availability_words(chunk_local);
        for (std::size_t word = 0U; word < availability_words_per_chunk;
             ++word) {
            if ((words[word] & capacity_words[word]) != 0U) return true;
        }
        return false;
    }

    template <typename Better>
    [[nodiscard]] std::size_t best_capacity_source(
        std::size_t chunk_local, Better&& better) const noexcept {
        std::size_t selected = limits.maximum_peers;
        if (inline_availability) {
            auto eligible = chunks[chunk_local].availability.inline_mask &
                inline_capacity_mask;
            while (eligible != 0U) {
                const auto peer_index = static_cast<std::size_t>(
                    std::countr_zero(eligible));
                eligible &= eligible - 1U;
                if (better(peer_index, selected)) selected = peer_index;
            }
            return selected;
        }
        const auto* words = availability_words(chunk_local);
        for (std::size_t word_index = 0U;
             word_index < availability_words_per_chunk; ++word_index) {
            auto eligible = words[word_index] & capacity_words[word_index];
            while (eligible != 0U) {
                const auto bit = static_cast<std::size_t>(
                    std::countr_zero(eligible));
                eligible &= eligible - 1U;
                const auto peer_index = word_index * 64U + bit;
                if (peer_index < limits.maximum_peers &&
                    better(peer_index, selected)) {
                    selected = peer_index;
                }
            }
        }
        return selected;
    }

    [[nodiscard]] bool heap_less(std::uint32_t left_local,
                                 std::uint32_t right_local) const noexcept {
        const auto& left = chunks[left_local];
        const auto& right = chunks[right_local];
        const auto left_rarity = rarity(left_local);
        const auto right_rarity = rarity(right_local);
        if (left_rarity != right_rarity) return left_rarity < right_rarity;
        if (left.attempts != right.attempts) {
            return left.attempts < right.attempts;
        }
        return ref(left_local).index < ref(right_local).index;
    }

    void heap_push(std::uint32_t local) noexcept {
        if (heap_size >= limits.maximum_window_chunks) return;
        auto position = heap_size++;
        heap_storage[position] = local;
        while (position != 0U) {
            const auto parent = (position - 1U) / 2U;
            if (!heap_less(heap_storage[position], heap_storage[parent])) break;
            std::swap(heap_storage[position], heap_storage[parent]);
            position = parent;
        }
    }

    void heap_sift_down(std::size_t position) noexcept {
        while (true) {
            const auto left = position * 2U + 1U;
            if (left >= heap_size) break;
            const auto right = left + 1U;
            auto better = left;
            if (right < heap_size &&
                heap_less(heap_storage[right], heap_storage[left])) {
                better = right;
            }
            if (!heap_less(heap_storage[better], heap_storage[position])) break;
            std::swap(heap_storage[position], heap_storage[better]);
            position = better;
        }
    }

    [[nodiscard]] std::uint32_t heap_pop() noexcept {
        const auto result = heap_storage[0U];
        --heap_size;
        if (heap_size != 0U) {
            heap_storage[0U] = heap_storage[heap_size];
            heap_sift_down(0U);
        }
        return result;
    }

    void rebuild_heap() noexcept {
        heap_size = 0U;
        for (std::size_t local = 0U; local < chunk_count; ++local) {
            const auto& chunk = chunks[local];
            if (chunk.state == ScheduledChunkState::pending &&
                any_available(local)) {
                heap_storage[heap_size++] = static_cast<std::uint32_t>(local);
            }
        }
        // Bottom-up heap construction is linear and matters when a large
        // inventory update invalidates the ordering for an entire window.
        for (auto position = heap_size / 2U; position != 0U; --position) {
            heap_sift_down(position - 1U);
        }
        heap_dirty = false;
    }

    [[nodiscard]] std::uint32_t* deferred() noexcept {
        return heap_storage.get() + limits.maximum_window_chunks;
    }

    [[nodiscard]] std::size_t local_index(std::uint64_t global) const {
        if (global < window_first || global - window_first >= chunk_count) {
            throw std::out_of_range(
                "chunk index is outside the scheduler window");
        }
        return static_cast<std::size_t>(global - window_first);
    }

    [[nodiscard]] const ContentChunkRef& ref(
        std::size_t local) const noexcept {
        return window_refs[local];
    }

    MultiSourceSchedulerLimits limits{};
    std::unique_ptr<PeerSlot[]> peers{};
    std::unique_ptr<ChunkSlot[]> chunks{};
    // First half is the pending min-heap; second half temporarily holds
    // capacity-blocked heap entries while next() chooses feasible work.
    std::unique_ptr<std::uint32_t[]> heap_storage{};
    std::unique_ptr<ContentChunkRef[]> owned_refs{};
    const ContentChunkRef* window_refs{};
    std::unique_ptr<RequestSlot[]> requests{};
    std::unique_ptr<std::uint64_t[]> dynamic_availability{};
    std::unique_ptr<std::uint64_t[]> capacity_words{};
    std::size_t request_table_slots{};
    std::size_t maximum_inflight{};
    std::size_t active_requests{};
    std::size_t availability_words_per_chunk{};
    std::size_t availability_word_count{};
    std::size_t retained_bytes{};
    std::size_t heap_size{};
    bool inline_availability{};
    bool heap_dirty{};
    std::uint32_t inline_capacity_mask{};
    std::uint64_t window_first{};
    std::size_t chunk_count{};
    std::size_t peer_count{};
    std::uint64_t completed_bytes{};
    std::uint64_t assignments{};
    std::uint64_t retries{};
};

MultiSourceScheduler::MultiSourceScheduler(MultiSourceSchedulerLimits limits)
    : impl_(std::make_unique<Impl>(limits)) {}

MultiSourceScheduler::~MultiSourceScheduler() = default;
MultiSourceScheduler::MultiSourceScheduler(
    MultiSourceScheduler&&) noexcept = default;
MultiSourceScheduler& MultiSourceScheduler::operator=(
    MultiSourceScheduler&&) noexcept = default;

void MultiSourceScheduler::set_window(
    std::uint64_t first_chunk,
    std::span<const ContentChunkRef> chunks) {
    if (chunks.size() > impl_->limits.maximum_window_chunks) {
        throw std::length_error(
            "multi-source scheduler window exceeds configured capacity");
    }
    std::uint64_t expected_index = first_chunk;
    std::uint64_t expected_offset = chunks.empty()
        ? 0U
        : chunks.front().artifact_offset;
    for (std::size_t local = 0U; local < chunks.size(); ++local) {
        const auto& chunk = chunks[local];
        if (chunk.index != expected_index || chunk.length == 0U ||
            chunk.artifact_offset != expected_offset) {
            throw std::invalid_argument(
                "multi-source scheduler window is not contiguous");
        }
        if (expected_offset >
            std::numeric_limits<std::uint64_t>::max() - chunk.length) {
            throw std::overflow_error(
                "multi-source scheduler artifact offset overflows");
        }
        impl_->chunks[local] = Impl::ChunkSlot{};
        if (impl_->limits.window_storage == MultiSourceWindowStorage::owned) {
            impl_->owned_refs[local] = chunk;
        }
        ++expected_index;
        expected_offset += chunk.length;
    }
    if (!impl_->inline_availability && !chunks.empty()) {
        std::fill_n(
            impl_->dynamic_availability.get(),
            chunks.size() * impl_->availability_words_per_chunk, 0U);
    }
    impl_->window_refs = chunks.empty()
        ? nullptr
        : (impl_->limits.window_storage == MultiSourceWindowStorage::owned
               ? impl_->owned_refs.get()
               : chunks.data());
    impl_->window_first = first_chunk;
    impl_->chunk_count = chunks.size();
    impl_->completed_bytes = 0U;
    impl_->assignments = 0U;
    impl_->retries = 0U;
    impl_->heap_size = 0U;
    impl_->heap_dirty = true;
    impl_->clear_requests();
    for (std::size_t peer = 0U; peer < impl_->limits.maximum_peers; ++peer) {
        impl_->peers[peer].active_lanes = 0U;
    }
}

void MultiSourceScheduler::clear() noexcept {
    impl_->window_first = 0U;
    impl_->chunk_count = 0U;
    impl_->window_refs = nullptr;
    impl_->completed_bytes = 0U;
    impl_->assignments = 0U;
    impl_->retries = 0U;
    impl_->heap_size = 0U;
    impl_->heap_dirty = false;
    impl_->clear_requests();
    for (std::size_t peer = 0U; peer < impl_->limits.maximum_peers; ++peer) {
        impl_->peers[peer].active_lanes = 0U;
    }
}

void MultiSourceScheduler::update_peer(
    const SourcePeerUpdate& update,
    std::uint64_t first_chunk,
    std::uint32_t bit_count,
    std::span<const std::byte> availability_bits) {
    if (update.peer_id == 0U || update.maximum_lanes == 0U ||
        update.maximum_lanes > impl_->limits.maximum_lanes_per_peer) {
        throw std::invalid_argument(
            "multi-source peer update violates scheduler limits");
    }
    const auto required_bytes =
        (static_cast<std::uint64_t>(bit_count) + 7U) / 8U;
    if (required_bytes > availability_bits.size()) {
        throw std::invalid_argument(
            "multi-source availability bitmap is truncated");
    }
    if (first_chunk >
        std::numeric_limits<std::uint64_t>::max() - bit_count) {
        throw std::invalid_argument(
            "multi-source availability range overflows");
    }

    const auto peer_index = impl_->find_or_create_peer(update.peer_id);
    auto& peer = impl_->peers[peer_index];
    peer.maximum_lanes = update.maximum_lanes;
    peer.useful_bytes_per_second = update.useful_bytes_per_second;
    peer.recent_failures = update.recent_failures;
    // Merge the supplied exact range into the current window. set_window()
    // clears every per-chunk peer bit, while subsequent inventory pages can
    // update disjoint portions without erasing earlier knowledge.
    const auto update_end = first_chunk + bit_count;
    const auto window_end = impl_->window_first + impl_->chunk_count;
    const auto intersection_begin = std::max(first_chunk, impl_->window_first);
    const auto intersection_end = std::min(update_end, window_end);
    for (auto global = intersection_begin; global < intersection_end; ++global) {
        const auto source_bit = global - first_chunk;
        const auto target_bit = static_cast<std::size_t>(
            global - impl_->window_first);
        const auto replacement = bit_at(availability_bits, source_bit);
        if (impl_->available(peer_index, target_bit) != replacement) {
            impl_->set_available(peer_index, target_bit, replacement);
            impl_->heap_dirty = true;
        }
    }
}

void MultiSourceScheduler::remove_peer(SourcePeerId peer_id) noexcept {
    const auto peer_index = impl_->find_peer(peer_id);
    if (peer_index == impl_->limits.maximum_peers) return;
    for (std::size_t local = 0U; local < impl_->chunk_count; ++local) {
        auto& chunk = impl_->chunks[local];
        impl_->set_available(peer_index, local, false);
        if (chunk.state == ScheduledChunkState::in_flight &&
            chunk.assigned_peer == peer_index) {
            impl_->erase_request(chunk.request_id);
            chunk.state = ScheduledChunkState::pending;
            chunk.request_id = 0U;
            chunk.assigned_peer = Impl::kNoPeer;
            chunk.last_failed_peer = peer_id;
            ++impl_->retries;
        }
    }
    impl_->heap_dirty = true;
    impl_->peers[peer_index] = Impl::PeerSlot{};
    if (impl_->peer_count != 0U) --impl_->peer_count;
}

std::optional<ChunkAssignment> MultiSourceScheduler::next(
    std::uint64_t request_id) {
    if (request_id == 0U) {
        throw std::invalid_argument(
            "multi-source request id must be nonzero");
    }
    if (impl_->find_request(request_id) != impl_->request_table_slots) {
        throw std::invalid_argument(
            "multi-source request id is already in flight");
    }
    if (!impl_->refresh_capacity()) return std::nullopt;
    if (impl_->heap_dirty) impl_->rebuild_heap();

    std::size_t deferred_count{};
    auto* deferred = impl_->deferred();
    std::size_t selected_chunk = impl_->chunk_count;
    while (impl_->heap_size != 0U) {
        const auto candidate = impl_->heap_pop();
        const auto& chunk = impl_->chunks[candidate];
        if (chunk.state != ScheduledChunkState::pending ||
            !impl_->any_available(candidate)) {
            continue;
        }
        if (impl_->has_capacity_source(candidate)) {
            selected_chunk = candidate;
            break;
        }
        deferred[deferred_count++] = candidate;
    }
    for (std::size_t index = 0U; index < deferred_count; ++index) {
        impl_->heap_push(deferred[index]);
    }
    if (selected_chunk == impl_->chunk_count) return std::nullopt;
    const auto& chosen_chunk = impl_->chunks[selected_chunk];

    const auto better_peer = [&](std::size_t candidate,
                                 std::size_t current) noexcept {
        if (current == impl_->limits.maximum_peers) return true;
        const auto& left = impl_->peers[candidate];
        const auto& right = impl_->peers[current];
        const bool left_is_last = left.id == chosen_chunk.last_failed_peer;
        const bool right_is_last = right.id == chosen_chunk.last_failed_peer;
        if (left_is_last != right_is_last) return !left_is_last;
        const auto left_scaled = left.useful_bytes_per_second /
            static_cast<std::uint64_t>(left.active_lanes + 1U);
        const auto right_scaled = right.useful_bytes_per_second /
            static_cast<std::uint64_t>(right.active_lanes + 1U);
        if (left_scaled != right_scaled) return left_scaled > right_scaled;
        if (left.recent_failures != right.recent_failures) {
            return left.recent_failures < right.recent_failures;
        }
        if (left.active_lanes != right.active_lanes) {
            return left.active_lanes < right.active_lanes;
        }
        return left.id < right.id;
    };

    const auto selected_peer = impl_->best_capacity_source(
        selected_chunk, better_peer);
    if (selected_peer == impl_->limits.maximum_peers) return std::nullopt;

    auto& chunk = impl_->chunks[selected_chunk];
    auto& peer = impl_->peers[selected_peer];
    if (chunk.attempts == std::numeric_limits<std::uint16_t>::max()) {
        chunk.state = ScheduledChunkState::failed;
        return std::nullopt;
    }
    ++chunk.attempts;
    impl_->insert_request(request_id, selected_chunk);
    chunk.state = ScheduledChunkState::in_flight;
    chunk.assigned_peer = static_cast<std::uint32_t>(selected_peer);
    chunk.request_id = request_id;
    ++peer.active_lanes;
    ++impl_->assignments;
    return ChunkAssignment{
        .request_id = request_id,
        .peer_id = peer.id,
        .chunk = impl_->ref(selected_chunk),
        .attempt = chunk.attempts,
    };
}

std::optional<ChunkAssignment> MultiSourceScheduler::assignment(
    std::uint64_t request_id) const noexcept {
    const auto request_slot = impl_->find_request(request_id);
    if (request_slot == impl_->request_table_slots) return std::nullopt;
    const auto local = static_cast<std::size_t>(
        impl_->requests[request_slot].chunk_local);
    if (local >= impl_->chunk_count) return std::nullopt;
    const auto& chunk = impl_->chunks[local];
    if (chunk.state != ScheduledChunkState::in_flight ||
        chunk.request_id != request_id ||
        chunk.assigned_peer >= impl_->limits.maximum_peers) {
        return std::nullopt;
    }
    return ChunkAssignment{
        .request_id = request_id,
        .peer_id = impl_->peers[chunk.assigned_peer].id,
        .chunk = impl_->ref(local),
        .attempt = chunk.attempts,
    };
}

bool MultiSourceScheduler::complete(std::uint64_t request_id) noexcept {
    const auto request_slot = impl_->find_request(request_id);
    if (request_slot == impl_->request_table_slots) return false;
    const auto local = static_cast<std::size_t>(
        impl_->requests[request_slot].chunk_local);
    if (local >= impl_->chunk_count) {
        impl_->erase_request_slot(request_slot);
        return false;
    }
    auto& chunk = impl_->chunks[local];
    if (chunk.state != ScheduledChunkState::in_flight ||
        chunk.request_id != request_id) {
        impl_->erase_request_slot(request_slot);
        return false;
    }
    if (chunk.assigned_peer < impl_->limits.maximum_peers) {
        auto& peer = impl_->peers[chunk.assigned_peer];
        if (peer.active_lanes != 0U) --peer.active_lanes;
    }
    impl_->erase_request_slot(request_slot);
    chunk.state = ScheduledChunkState::complete;
    chunk.request_id = 0U;
    chunk.assigned_peer = Impl::kNoPeer;
    impl_->completed_bytes += impl_->ref(local).length;
    return true;
}

bool MultiSourceScheduler::fail(
    std::uint64_t request_id,
    SourceFailureDisposition disposition) noexcept {
    const auto request_slot = impl_->find_request(request_id);
    if (request_slot == impl_->request_table_slots) return false;
    const auto local = static_cast<std::size_t>(
        impl_->requests[request_slot].chunk_local);
    if (local >= impl_->chunk_count) {
        impl_->erase_request_slot(request_slot);
        return false;
    }
    auto& chunk = impl_->chunks[local];
    if (chunk.state != ScheduledChunkState::in_flight ||
        chunk.request_id != request_id) {
        impl_->erase_request_slot(request_slot);
        return false;
    }
    SourcePeerId peer_id{};
    if (chunk.assigned_peer < impl_->limits.maximum_peers) {
        auto& peer = impl_->peers[chunk.assigned_peer];
        peer_id = peer.id;
        if (peer.active_lanes != 0U) --peer.active_lanes;
        if (disposition ==
            SourceFailureDisposition::remove_source_for_chunk) {
            impl_->set_available(chunk.assigned_peer, local, false);
        }
    }
    impl_->erase_request_slot(request_slot);
    chunk.request_id = 0U;
    chunk.assigned_peer = Impl::kNoPeer;
    chunk.last_failed_peer = peer_id;
    ++impl_->retries;
    if (disposition == SourceFailureDisposition::permanent ||
        chunk.attempts >= impl_->limits.maximum_attempts_per_chunk) {
        chunk.state = ScheduledChunkState::failed;
    } else {
        chunk.state = ScheduledChunkState::pending;
        if (!impl_->heap_dirty && impl_->any_available(local)) {
            impl_->heap_push(static_cast<std::uint32_t>(local));
        }
    }
    return true;
}

bool MultiSourceScheduler::mark_complete(
    std::uint64_t chunk_index) noexcept {
    if (chunk_index < impl_->window_first ||
        chunk_index - impl_->window_first >= impl_->chunk_count) {
        return false;
    }
    const auto local = static_cast<std::size_t>(
        chunk_index - impl_->window_first);
    auto& chunk = impl_->chunks[local];
    if (chunk.state == ScheduledChunkState::complete) return true;
    if (chunk.state == ScheduledChunkState::in_flight &&
        chunk.assigned_peer < impl_->limits.maximum_peers) {
        auto& peer = impl_->peers[chunk.assigned_peer];
        if (peer.active_lanes != 0U) --peer.active_lanes;
        impl_->erase_request(chunk.request_id);
    }
    chunk.state = ScheduledChunkState::complete;
    chunk.request_id = 0U;
    chunk.assigned_peer = Impl::kNoPeer;
    impl_->completed_bytes += impl_->ref(local).length;
    return true;
}

ScheduledChunkState MultiSourceScheduler::state(
    std::uint64_t chunk_index) const {
    return impl_->chunks[impl_->local_index(chunk_index)].state;
}

MultiSourceSchedulerStats MultiSourceScheduler::stats() const noexcept {
    MultiSourceSchedulerStats result;
    result.peers = impl_->peer_count;
    result.window_chunks = impl_->chunk_count;
    result.maximum_inflight_requests = impl_->maximum_inflight;
    result.availability_words_per_chunk = impl_->inline_availability
        ? 1U
        : impl_->availability_words_per_chunk;
    result.availability_bytes = impl_->inline_availability
        ? impl_->limits.maximum_window_chunks * sizeof(std::uint32_t)
        : impl_->availability_word_count * sizeof(std::uint64_t);
    result.completed_bytes = impl_->completed_bytes;
    result.assignments = impl_->assignments;
    result.retries = impl_->retries;
    result.resident_bytes = resident_bytes();
    for (std::size_t local = 0U; local < impl_->chunk_count; ++local) {
        switch (impl_->chunks[local].state) {
            case ScheduledChunkState::pending:
                ++result.pending_chunks;
                break;
            case ScheduledChunkState::in_flight:
                ++result.in_flight_chunks;
                break;
            case ScheduledChunkState::complete:
                ++result.completed_chunks;
                break;
            case ScheduledChunkState::failed:
                ++result.failed_chunks;
                break;
        }
    }
    return result;
}

std::size_t MultiSourceScheduler::resident_bytes() const noexcept {
    return impl_->retained_bytes;
}

std::uint64_t MultiSourceScheduler::first_chunk() const noexcept {
    return impl_->window_first;
}

std::size_t MultiSourceScheduler::window_size() const noexcept {
    return impl_->chunk_count;
}

} // namespace toxsync
