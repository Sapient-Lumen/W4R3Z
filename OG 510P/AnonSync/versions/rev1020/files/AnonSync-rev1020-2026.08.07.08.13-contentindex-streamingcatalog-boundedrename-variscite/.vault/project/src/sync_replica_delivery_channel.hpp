#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_replica_delivery_protocol.hpp"
#include "sync_thread_incarnation.hpp"

#include <memory>
#include <string>
#include <string_view>

namespace anonsync {

namespace detail {

// Internal transport hook retained by a delivery authority. A transport can
// revalidate that its exact authenticated session is still live immediately
// before the service touches durable state. This interface is visible only so
// independently compiled adapters can implement it; callers cannot attach one
// to an authority because the authority constructor remains private.
class SyncReplicaDeliveryChannelVerifier {
public:
    virtual ~SyncReplicaDeliveryChannelVerifier() = default;
    virtual void validate_or_throw(std::string_view label) const = 0;
};

}  // namespace detail

class SyncReplicaDeliveryService;
class SyncReplicaFileDeliveryService;
class SyncReplicaReconciliationService;
class SyncReplicaTlsAuthenticatedChannel;

namespace testing {
class SyncReplicaDeliveryTestChannelFactory;
}

// Public observation carried by one authenticated transport capability. The
// fields are intentionally inspectable for protocol construction and logging,
// but this value alone is not authority to invoke the delivery service.
struct SyncReplicaDeliveryChannelContext final {
    SyncReplicaActor peer_actor;
    SyncReplicaDeliveryChannelBinding binding;

    bool operator==(const SyncReplicaDeliveryChannelContext&) const = default;
};

// Move-only process/thread-local authority minted only by a reviewed transport
// adapter (or the separately linked test factory). The delivery service accepts
// this capability rather than a caller-fabricable context value, preventing an
// application caller from accidentally treating actor/binding bytes as proof
// that peer authentication actually happened.
//
// This is domain separation inside one process, not a security boundary against
// hostile code already executing there. The capability must not cross fork or
// thread lifetime boundaries. A fork-inherited use fail-stops before durable or
// transport work; foreign-thread use throws before owner access.
class SyncReplicaDeliveryChannelAuthority final {
public:
    SyncReplicaDeliveryChannelAuthority() = delete;
    SyncReplicaDeliveryChannelAuthority(
        const SyncReplicaDeliveryChannelAuthority&) = delete;
    SyncReplicaDeliveryChannelAuthority& operator=(
        const SyncReplicaDeliveryChannelAuthority&) = delete;
    SyncReplicaDeliveryChannelAuthority(
        SyncReplicaDeliveryChannelAuthority&& other) noexcept;
    SyncReplicaDeliveryChannelAuthority& operator=(
        SyncReplicaDeliveryChannelAuthority&& other) noexcept;
    ~SyncReplicaDeliveryChannelAuthority() = default;

    [[nodiscard]] bool valid() const noexcept {
        return valid_;
    }

    [[nodiscard]] const SyncReplicaDeliveryChannelContext& context() const
        noexcept {
        return context_;
    }

private:
    explicit SyncReplicaDeliveryChannelAuthority(
        SyncReplicaDeliveryChannelContext context,
        std::shared_ptr<const detail::SyncReplicaDeliveryChannelVerifier>
            verifier,
        std::string_view label);

    void require_current_or_throw(std::string_view label) const;

    SyncReplicaDeliveryChannelContext context_;
    SyncProcessIncarnation owner_process_;
    SyncThreadIncarnation owner_thread_;
    std::shared_ptr<const detail::SyncReplicaDeliveryChannelVerifier> verifier_;
    bool valid_ = false;

    friend class SyncReplicaDeliveryService;
    friend class SyncReplicaFileDeliveryService;
    friend class SyncReplicaReconciliationService;
    friend class SyncReplicaTlsAuthenticatedChannel;
    friend class testing::SyncReplicaDeliveryTestChannelFactory;
};

}  // namespace anonsync
