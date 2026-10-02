#include "iotox/local/friend_request_fifo.hpp"

#include "iotox/security/sodium.hpp"

#include <string_view>
#include <utility>

namespace iotox::local {

Result<FriendRequestFifoRecord>
decode_friend_request_fifo_record(std::span<const std::uint8_t> record) {
    if (record.size() < kFriendRequestMinimumRecordBytes ||
        record.size() > kFriendRequestMaximumRecordBytes) {
        return Status{
            ErrorCode::invalid_argument,
            "outgoing friend request record must contain a 76-character Tox address, one TAB, and a 1..921-byte message"};
    }
    if (record[kFriendRequestAddressHexBytes] !=
        static_cast<std::uint8_t>('\t')) {
        return Status{
            ErrorCode::invalid_argument,
            "outgoing friend request record byte 77 must be one literal TAB separator"};
    }

    const auto *address_characters =
        reinterpret_cast<const char *>(record.data());
    const std::string_view encoded_address(
        address_characters, kFriendRequestAddressHexBytes);
    auto decoded_address = security::decode_hex_exact(
        encoded_address, toxcore::abi::kAddressSize,
        "outgoing friend request Tox address");
    if (!decoded_address) {
        return decoded_address.status();
    }

    FriendRequestFifoRecord decoded;
    decoded.address = std::move(decoded_address).value();
    decoded.message.assign(
        record.begin() +
            static_cast<std::ptrdiff_t>(kFriendRequestAddressHexBytes +
                                        kFriendRequestSeparatorBytes),
        record.end());
    if (decoded.message.empty() ||
        decoded.message.size() > kFriendRequestMaximumMessageBytes) {
        return Status{ErrorCode::invalid_argument,
                      "outgoing friend request message must contain 1..921 bytes"};
    }
    return decoded;
}

}  // namespace iotox::local
