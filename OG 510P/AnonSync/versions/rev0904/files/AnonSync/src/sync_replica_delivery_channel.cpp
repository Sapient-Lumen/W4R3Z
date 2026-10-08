#include "sync_replica_delivery_channel.hpp"

#include "sync_manifest_validation.hpp"

#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {

SyncReplicaDeliveryChannelAuthority::SyncReplicaDeliveryChannelAuthority(
    SyncReplicaDeliveryChannelContext context,
    std::shared_ptr<const detail::SyncReplicaDeliveryChannelVerifier> verifier,
    std::string_view label)
    : context_(std::move(context)),
      owner_process_(current_sync_process_incarnation_noexcept()),
      owner_thread_(current_sync_thread_incarnation_noexcept()),
      verifier_(std::move(verifier)),
      valid_(true) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica delivery channel authority label must not be empty");
    }
    if (!sync_id_is_valid(context_.peer_actor.device_id) ||
        context_.peer_actor.epoch == 0U) {
        throw std::invalid_argument(
            std::string(label) + " peer actor identity is invalid");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        context_.binding, std::string(label));
    if (!owner_process_.valid() || !owner_thread_.valid()) {
        throw std::logic_error(
            std::string(label) + " could not bind live process/thread authority");
    }
}

SyncReplicaDeliveryChannelAuthority::SyncReplicaDeliveryChannelAuthority(
    SyncReplicaDeliveryChannelAuthority&& other) noexcept
    : context_(std::move(other.context_)),
      owner_process_(std::exchange(other.owner_process_, {})),
      owner_thread_(std::exchange(other.owner_thread_, {})),
      verifier_(std::move(other.verifier_)),
      valid_(std::exchange(other.valid_, false)) {}

SyncReplicaDeliveryChannelAuthority&
SyncReplicaDeliveryChannelAuthority::operator=(
    SyncReplicaDeliveryChannelAuthority&& other) noexcept {
    if (this != &other) {
        context_ = std::move(other.context_);
        owner_process_ = std::exchange(other.owner_process_, {});
        owner_thread_ = std::exchange(other.owner_thread_, {});
        verifier_ = std::move(other.verifier_);
        valid_ = std::exchange(other.valid_, false);
    }
    return *this;
}

void SyncReplicaDeliveryChannelAuthority::require_current_or_throw(
    std::string_view label) const {
    if (!valid_) {
        throw std::logic_error(
            std::string(label) +
            " authenticated delivery channel authority is empty or moved-from");
    }
    require_sync_process_incarnation_or_fail_stop(owner_process_, label);
    require_sync_thread_incarnation_or_throw(owner_thread_, label);
    if (verifier_) verifier_->validate_or_throw(label);
}

}  // namespace anonsync
