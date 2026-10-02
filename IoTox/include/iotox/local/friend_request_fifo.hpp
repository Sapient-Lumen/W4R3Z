#pragma once

#include "iotox/status.hpp"
#include "iotox/toxcore/abi.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace iotox::local {

inline constexpr std::size_t kFriendRequestAddressHexBytes =
    toxcore::abi::kAddressSize * 2U;
inline constexpr std::size_t kFriendRequestSeparatorBytes = 1U;
inline constexpr std::size_t kFriendRequestMinimumMessageBytes = 1U;
inline constexpr std::size_t kFriendRequestMaximumMessageBytes =
    toxcore::abi::kMaxFriendRequestLength;
inline constexpr std::size_t kFriendRequestMinimumRecordBytes =
    kFriendRequestAddressHexBytes + kFriendRequestSeparatorBytes +
    kFriendRequestMinimumMessageBytes;
inline constexpr std::size_t kFriendRequestMaximumRecordBytes =
    kFriendRequestAddressHexBytes + kFriendRequestSeparatorBytes +
    kFriendRequestMaximumMessageBytes;

// Exact root-level ratox-successor record, excluding the LF framing byte:
//
//   <76 hexadecimal Tox address bytes><TAB><1..921 message bytes>
//
// The address field accepts upper- or lower-case hexadecimal and decodes to
// the complete 38-byte Tox address (public key, nospam, checksum). The message
// is byte-preserving. The framing service removes LF; every other byte,
// including TAB, NUL, CR, and bytes >= 0x80, belongs to the message.
struct FriendRequestFifoRecord {
    std::vector<std::uint8_t> address;
    std::vector<std::uint8_t> message;
};

[[nodiscard]] Result<FriendRequestFifoRecord>
decode_friend_request_fifo_record(std::span<const std::uint8_t> record);

}  // namespace iotox::local
