#include "test_harness.hpp"

#include "iotox/toxcore/abi.hpp"

#include <cstdint>
#include <type_traits>

namespace {

using namespace iotox::toxcore;

IOTOX_TEST("toxcore runtime table preserves the official 0.2 ABI types") {
    using Api = abi::Api;

    static_assert(std::is_same_v<abi::FriendNumber, std::uint32_t>);
    static_assert(std::is_same_v<abi::FileNumber, std::uint32_t>);
    static_assert(std::is_same_v<decltype(Api{}.options_new),
                                 abi::ToxOptions *(*)(abi::OptionsNewError *)>);
    static_assert(std::is_same_v<decltype(Api{}.options_set_savedata_type),
                                 void (*)(abi::ToxOptions *, abi::SavedataType)>);
    static_assert(std::is_same_v<decltype(Api{}.version_is_compatible),
                                 bool (*)(std::uint32_t, std::uint32_t, std::uint32_t)>);
    static_assert(std::is_same_v<decltype(Api{}.public_key_size), std::uint32_t (*)()>);
    static_assert(std::is_same_v<decltype(Api{}.address_size), std::uint32_t (*)()>);
    static_assert(std::is_same_v<decltype(Api{}.options_set_proxy_type),
                                 void (*)(abi::ToxOptions *, abi::ProxyType)>);
    static_assert(std::is_same_v<decltype(Api{}.options_set_experimental_disable_dns),
                                 void (*)(abi::ToxOptions *, bool)>);
    static_assert(std::is_same_v<decltype(Api{}.tox_new),
                                 abi::Tox *(*)(const abi::ToxOptions *, abi::NewError *)>);
    static_assert(std::is_same_v<decltype(Api{}.callback_self_connection_status),
                                 void (*)(abi::Tox *, abi::SelfConnectionCallback *)>);
    static_assert(std::is_same_v<decltype(Api{}.callback_friend_connection_status),
                                 void (*)(abi::Tox *, abi::FriendConnectionCallback *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_add_norequest),
                                 abi::FriendNumber (*)(abi::Tox *, const std::uint8_t *,
                                                       abi::FriendAddError *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_add),
                                 abi::FriendNumber (*)(abi::Tox *, const std::uint8_t *,
                                                       const std::uint8_t *, std::size_t,
                                                       abi::FriendAddError *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_delete),
                                 bool (*)(abi::Tox *, abi::FriendNumber,
                                          abi::FriendDeleteError *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_by_public_key),
                                 abi::FriendNumber (*)(
                                     const abi::Tox *, const std::uint8_t *,
                                     abi::FriendByPublicKeyError *)>);
    static_assert(std::is_same_v<decltype(Api{}.self_get_friend_list),
                                 void (*)(const abi::Tox *, abi::FriendNumber *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_get_public_key),
                                 bool (*)(const abi::Tox *, abi::FriendNumber,
                                          std::uint8_t *, abi::FriendGetPublicKeyError *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_send_lossless_packet),
                                 bool (*)(abi::Tox *, abi::FriendNumber,
                                          const std::uint8_t *, std::size_t,
                                          abi::FriendCustomPacketError *)>);
    static_assert(std::is_same_v<decltype(Api{}.friend_send_lossy_packet),
                                 bool (*)(abi::Tox *, abi::FriendNumber,
                                          const std::uint8_t *, std::size_t,
                                          abi::FriendCustomPacketError *)>);
    static_assert(std::is_same_v<decltype(Api{}.callback_file_recv),
                                 void (*)(abi::Tox *, abi::FileRecvCallback *)>);
    static_assert(std::is_same_v<decltype(Api{}.callback_file_chunk_request),
                                 void (*)(abi::Tox *, abi::FileChunkRequestCallback *)>);
    static_assert(std::is_same_v<decltype(Api{}.file_send),
                                 abi::FileNumber (*)(
                                     abi::Tox *, abi::FriendNumber, std::uint32_t,
                                     std::uint64_t, const std::uint8_t *,
                                     const std::uint8_t *, std::size_t,
                                     abi::FileSendError *)>);
    static_assert(std::is_same_v<decltype(Api{}.file_send_chunk),
                                 bool (*)(
                                     abi::Tox *, abi::FriendNumber, abi::FileNumber,
                                     std::uint64_t, const std::uint8_t *, std::size_t,
                                     abi::FileSendChunkError *)>);
    static_assert(std::is_same_v<decltype(Api{}.file_get_file_id),
                                 bool (*)(
                                     const abi::Tox *, abi::FriendNumber,
                                     abi::FileNumber, std::uint8_t *,
                                     abi::FileGetError *)>);

    IOTOX_CHECK(static_cast<int>(abi::kConnectionNone) == 0);
    IOTOX_CHECK(static_cast<int>(abi::kConnectionTcp) == 1);
    IOTOX_CHECK(static_cast<int>(abi::kConnectionUdp) == 2);
    IOTOX_CHECK(static_cast<int>(abi::kSavedataToxSave) == 1);
    IOTOX_CHECK(abi::kFriendNumberFailure == UINT32_MAX);
    IOTOX_CHECK(abi::kFileNumberFailure == UINT32_MAX);
    IOTOX_CHECK(abi::kFileIdLength == 32U);
    IOTOX_CHECK(abi::kMaxFilenameLength == 255U);
    IOTOX_CHECK(static_cast<int>(abi::kFileSendChunkSendQueueFull) == 7);
}

}  // namespace
