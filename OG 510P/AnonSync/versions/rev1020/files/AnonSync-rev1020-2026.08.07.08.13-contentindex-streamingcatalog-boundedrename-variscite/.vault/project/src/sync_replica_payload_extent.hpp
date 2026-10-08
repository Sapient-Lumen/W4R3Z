#pragma once

#include <cstdint>

namespace anonsync {

// Product-wide complete-file extent policy. These are validation ceilings,
// never allocation requests: payload bytes are streamed through bounded
// descriptors and reconciliation ranges. A media-capable default avoids making
// ordinary large Linux files an obscure setup-time exception, while the exact
// maximum remains equal to the bounded content-defined manifest frontier.
inline constexpr std::uint64_t kSyncReplicaDefaultMaximumPayloadExtentBytes =
    64ULL * 1024ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kSyncReplicaMaximumPayloadExtentBytes =
    4ULL * 1024ULL * 1024ULL * 1024ULL * 1024ULL;

static_assert(kSyncReplicaDefaultMaximumPayloadExtentBytes > 0U);
static_assert(
    kSyncReplicaDefaultMaximumPayloadExtentBytes <=
    kSyncReplicaMaximumPayloadExtentBytes);

}  // namespace anonsync
