#include "sync_replica_delivery_test_channel.hpp"

#include <string>
#include <string_view>
#include <utility>

namespace anonsync::testing {

SyncReplicaDeliveryChannelAuthority
SyncReplicaDeliveryTestChannelFactory::make_or_throw(
    SyncReplicaActor peer_actor,
    std::string_view transcript,
    std::string binding_type) {
    SyncReplicaDeliveryChannelContext context{
        std::move(peer_actor),
        make_sync_replica_delivery_channel_binding_or_throw(
            std::move(binding_type), transcript),
    };
    return SyncReplicaDeliveryChannelAuthority(
        std::move(context), {}, "sync replica delivery test channel");
}

}  // namespace anonsync::testing
