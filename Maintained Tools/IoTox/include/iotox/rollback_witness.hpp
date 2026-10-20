#pragma once

#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <array>
#include <cstdint>
#include <memory>
#include <optional>
#include <string_view>

namespace iotox::rollback_witness {

using DomainId = std::array<std::uint8_t, 16U>;
using TransactionNonce = std::array<std::uint8_t, 32U>;

enum class Lane : std::uint8_t {
    authority = 1U,
    application_incarnation = 2U,
    ratox_incarnation = 3U,
    route_generation = 4U,
    terminal_policy = 5U,
    command_effect = 6U,
    sync_policy = 7U,
    update_lifecycle = 8U,
    sync_guarded_state = 9U,
    tree_v2_state = 10U,
};

[[nodiscard]] std::string_view lane_name(Lane lane) noexcept;

struct Head {
    // A lane-global monotonic position. For authority this is record_count,
    // not the per-ownership-epoch record sequence (which may reset).
    std::uint64_t position{0U};
    security::Digest digest{};

    [[nodiscard]] bool operator==(const Head &) const = default;
};

struct Record {
    DomainId domain{};
    security::SigningPublicKey device{};
    std::uint64_t witness_epoch{0U};
    Lane lane{Lane::authority};
    Head committed{};
    std::optional<Head> pending;
    std::optional<TransactionNonce> nonce;

    [[nodiscard]] bool operator==(const Record &) const = default;
};

[[nodiscard]] Status validate(const Record &record);
[[nodiscard]] Result<Record> begin(const Record &committed,
                                   const Head &next,
                                   const TransactionNonce &nonce);
[[nodiscard]] Result<Record> finish(const Record &pending);
[[nodiscard]] Status validate_transition(const Record &expected,
                                         const Record &desired);

// Authenticated exact-CAS transport contract. Implementations must bind the
// domain, device, epoch, and lane and authenticate both requests and replies.
// `unavailable` is deliberately ambiguous; callers query and retry the exact
// idempotent CAS. A backend sharing the Agent's disk/admin/failure domain must
// return false and is never sufficient for a production freshness claim.
class Backend {
  public:
    virtual ~Backend() = default;
    [[nodiscard]] virtual Result<Record> query() = 0;
    [[nodiscard]] virtual Status compare_exchange(const Record &expected,
                                                  const Record &desired) = 0;
    [[nodiscard]] virtual bool independently_controlled() const noexcept = 0;
};

}  // namespace iotox::rollback_witness
