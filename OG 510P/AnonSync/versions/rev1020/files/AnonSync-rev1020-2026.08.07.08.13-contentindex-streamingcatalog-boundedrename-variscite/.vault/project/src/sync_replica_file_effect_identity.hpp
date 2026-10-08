#pragma once

#include "sync_replica_model.hpp"

#include <string>

namespace anonsync {

// Stable identity for one immutable file effect. This is a structural SHA-256
// commitment to folder, operation, canonical path, content digest, and size;
// it is not authentication and does not replace the authenticated delivery
// channel or the receiver's durable publication cutpoint.
[[nodiscard]] std::string make_sync_replica_file_effect_id_or_throw(
    const SyncReplicaOperation& operation);

}  // namespace anonsync
