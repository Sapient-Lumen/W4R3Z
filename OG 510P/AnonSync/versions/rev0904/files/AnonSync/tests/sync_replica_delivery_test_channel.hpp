#pragma once

#include "sync_replica_delivery_channel.hpp"

#include <string>
#include <string_view>

namespace anonsync::testing {

// Separately linked deterministic authority mint for delivery-service tests.
// Production libraries do not expose or link this constructor path.
class SyncReplicaDeliveryTestChannelFactory final {
public:
    [[nodiscard]] static SyncReplicaDeliveryChannelAuthority make_or_throw(
        SyncReplicaActor peer_actor,
        std::string_view transcript,
        std::string binding_type = "test-channel");
};

}  // namespace anonsync::testing
