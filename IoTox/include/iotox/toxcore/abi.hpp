#pragma once

#include <cstddef>
#include <cstdint>

// Prefer canonical c-toxcore declarations when headers are installed. The
// fallback reproduces only the public 0.2.23 ABI consumed by IoTox's provider
// table and exact test double. Numeric constants are validated at runtime
// because c-toxcore explicitly excludes them from its ABI promise.
#if __has_include(<tox/tox.h>) && !defined(IOTOX_FORCE_BUILTIN_TOXCORE_ABI)
#include <tox/tox.h>
#define IOTOX_TOXCORE_SYSTEM_HEADERS 1
#elif __has_include(<toxcore/tox.h>) && !defined(IOTOX_FORCE_BUILTIN_TOXCORE_ABI)
#include <toxcore/tox.h>
#define IOTOX_TOXCORE_SYSTEM_HEADERS 1
#else
#define IOTOX_TOXCORE_SYSTEM_HEADERS 0

extern "C" {

typedef struct Tox Tox;
typedef struct Tox_Options Tox_Options;
typedef std::uint32_t Tox_Friend_Number;
typedef std::uint32_t Tox_Friend_Message_Id;
typedef std::uint32_t Tox_File_Number;

typedef enum Tox_Connection {
    TOX_CONNECTION_NONE,
    TOX_CONNECTION_TCP,
    TOX_CONNECTION_UDP,
} Tox_Connection;

typedef enum Tox_Proxy_Type {
    TOX_PROXY_TYPE_NONE,
    TOX_PROXY_TYPE_HTTP,
    TOX_PROXY_TYPE_SOCKS5,
} Tox_Proxy_Type;

typedef enum Tox_Savedata_Type {
    TOX_SAVEDATA_TYPE_NONE,
    TOX_SAVEDATA_TYPE_TOX_SAVE,
    TOX_SAVEDATA_TYPE_SECRET_KEY,
} Tox_Savedata_Type;

typedef enum Tox_User_Status {
    TOX_USER_STATUS_NONE,
    TOX_USER_STATUS_AWAY,
    TOX_USER_STATUS_BUSY,
} Tox_User_Status;

typedef enum Tox_Message_Type {
    TOX_MESSAGE_TYPE_NORMAL,
    TOX_MESSAGE_TYPE_ACTION,
} Tox_Message_Type;

typedef enum Tox_File_Control {
    TOX_FILE_CONTROL_RESUME,
    TOX_FILE_CONTROL_PAUSE,
    TOX_FILE_CONTROL_CANCEL,
} Tox_File_Control;

typedef enum Tox_Err_Options_New {
    TOX_ERR_OPTIONS_NEW_OK,
    TOX_ERR_OPTIONS_NEW_MALLOC,
} Tox_Err_Options_New;

typedef enum Tox_Err_New {
    TOX_ERR_NEW_OK,
    TOX_ERR_NEW_NULL,
    TOX_ERR_NEW_MALLOC,
    TOX_ERR_NEW_PORT_ALLOC,
    TOX_ERR_NEW_PROXY_BAD_TYPE,
    TOX_ERR_NEW_PROXY_BAD_HOST,
    TOX_ERR_NEW_PROXY_BAD_PORT,
    TOX_ERR_NEW_PROXY_NOT_FOUND,
    TOX_ERR_NEW_LOAD_ENCRYPTED,
    TOX_ERR_NEW_LOAD_BAD_FORMAT,
} Tox_Err_New;

typedef enum Tox_Err_Bootstrap {
    TOX_ERR_BOOTSTRAP_OK,
    TOX_ERR_BOOTSTRAP_NULL,
    TOX_ERR_BOOTSTRAP_BAD_HOST,
    TOX_ERR_BOOTSTRAP_BAD_PORT,
} Tox_Err_Bootstrap;

typedef enum Tox_Err_Set_Info {
    TOX_ERR_SET_INFO_OK,
    TOX_ERR_SET_INFO_NULL,
    TOX_ERR_SET_INFO_TOO_LONG,
} Tox_Err_Set_Info;

typedef enum Tox_Err_Friend_Add {
    TOX_ERR_FRIEND_ADD_OK,
    TOX_ERR_FRIEND_ADD_NULL,
    TOX_ERR_FRIEND_ADD_TOO_LONG,
    TOX_ERR_FRIEND_ADD_NO_MESSAGE,
    TOX_ERR_FRIEND_ADD_OWN_KEY,
    TOX_ERR_FRIEND_ADD_ALREADY_SENT,
    TOX_ERR_FRIEND_ADD_BAD_CHECKSUM,
    TOX_ERR_FRIEND_ADD_SET_NEW_NOSPAM,
    TOX_ERR_FRIEND_ADD_MALLOC,
} Tox_Err_Friend_Add;

typedef enum Tox_Err_Friend_Delete {
    TOX_ERR_FRIEND_DELETE_OK,
    TOX_ERR_FRIEND_DELETE_FRIEND_NOT_FOUND,
} Tox_Err_Friend_Delete;

typedef enum Tox_Err_Friend_By_Public_Key {
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_OK,
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_NULL,
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_NOT_FOUND,
} Tox_Err_Friend_By_Public_Key;

typedef enum Tox_Err_Friend_Get_Public_Key {
    TOX_ERR_FRIEND_GET_PUBLIC_KEY_OK,
    TOX_ERR_FRIEND_GET_PUBLIC_KEY_FRIEND_NOT_FOUND,
} Tox_Err_Friend_Get_Public_Key;

typedef enum Tox_Err_Friend_Query {
    TOX_ERR_FRIEND_QUERY_OK,
    TOX_ERR_FRIEND_QUERY_NULL,
    TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND,
} Tox_Err_Friend_Query;

typedef enum Tox_Err_Set_Typing {
    TOX_ERR_SET_TYPING_OK,
    TOX_ERR_SET_TYPING_FRIEND_NOT_FOUND,
} Tox_Err_Set_Typing;

typedef enum Tox_Err_Friend_Send_Message {
    TOX_ERR_FRIEND_SEND_MESSAGE_OK,
    TOX_ERR_FRIEND_SEND_MESSAGE_NULL,
    TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_FOUND,
    TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_CONNECTED,
    TOX_ERR_FRIEND_SEND_MESSAGE_SENDQ,
    TOX_ERR_FRIEND_SEND_MESSAGE_TOO_LONG,
    TOX_ERR_FRIEND_SEND_MESSAGE_EMPTY,
} Tox_Err_Friend_Send_Message;

typedef enum Tox_Err_Friend_Custom_Packet {
    TOX_ERR_FRIEND_CUSTOM_PACKET_OK,
    TOX_ERR_FRIEND_CUSTOM_PACKET_NULL,
    TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_FOUND,
    TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_CONNECTED,
    TOX_ERR_FRIEND_CUSTOM_PACKET_INVALID,
    TOX_ERR_FRIEND_CUSTOM_PACKET_EMPTY,
    TOX_ERR_FRIEND_CUSTOM_PACKET_TOO_LONG,
    TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ,
} Tox_Err_Friend_Custom_Packet;

typedef enum Tox_Err_File_Control {
    TOX_ERR_FILE_CONTROL_OK,
    TOX_ERR_FILE_CONTROL_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_CONTROL_FRIEND_NOT_CONNECTED,
    TOX_ERR_FILE_CONTROL_NOT_FOUND,
    TOX_ERR_FILE_CONTROL_NOT_PAUSED,
    TOX_ERR_FILE_CONTROL_DENIED,
    TOX_ERR_FILE_CONTROL_ALREADY_PAUSED,
    TOX_ERR_FILE_CONTROL_SENDQ,
} Tox_Err_File_Control;

typedef enum Tox_Err_File_Seek {
    TOX_ERR_FILE_SEEK_OK,
    TOX_ERR_FILE_SEEK_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_SEEK_FRIEND_NOT_CONNECTED,
    TOX_ERR_FILE_SEEK_NOT_FOUND,
    TOX_ERR_FILE_SEEK_DENIED,
    TOX_ERR_FILE_SEEK_INVALID_POSITION,
    TOX_ERR_FILE_SEEK_SENDQ,
} Tox_Err_File_Seek;

typedef enum Tox_Err_File_Get {
    TOX_ERR_FILE_GET_OK,
    TOX_ERR_FILE_GET_NULL,
    TOX_ERR_FILE_GET_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_GET_NOT_FOUND,
} Tox_Err_File_Get;

typedef enum Tox_Err_File_By_Id {
    TOX_ERR_FILE_BY_ID_OK,
    TOX_ERR_FILE_BY_ID_NULL,
    TOX_ERR_FILE_BY_ID_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_BY_ID_NOT_FOUND,
} Tox_Err_File_By_Id;

typedef enum Tox_Err_File_Send {
    TOX_ERR_FILE_SEND_OK,
    TOX_ERR_FILE_SEND_NULL,
    TOX_ERR_FILE_SEND_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_SEND_FRIEND_NOT_CONNECTED,
    TOX_ERR_FILE_SEND_NAME_TOO_LONG,
    TOX_ERR_FILE_SEND_TOO_MANY,
} Tox_Err_File_Send;

typedef enum Tox_Err_File_Send_Chunk {
    TOX_ERR_FILE_SEND_CHUNK_OK,
    TOX_ERR_FILE_SEND_CHUNK_NULL,
    TOX_ERR_FILE_SEND_CHUNK_FRIEND_NOT_FOUND,
    TOX_ERR_FILE_SEND_CHUNK_FRIEND_NOT_CONNECTED,
    TOX_ERR_FILE_SEND_CHUNK_NOT_FOUND,
    TOX_ERR_FILE_SEND_CHUNK_NOT_TRANSFERRING,
    TOX_ERR_FILE_SEND_CHUNK_INVALID_LENGTH,
    TOX_ERR_FILE_SEND_CHUNK_SENDQ,
    TOX_ERR_FILE_SEND_CHUNK_WRONG_POSITION,
} Tox_Err_File_Send_Chunk;

}  // extern "C"
#endif

namespace iotox::toxcore::abi {

using Tox = ::Tox;
using ToxOptions = ::Tox_Options;
using FriendNumber = ::Tox_Friend_Number;
using FriendMessageId = ::Tox_Friend_Message_Id;
using FileNumber = ::Tox_File_Number;
using Connection = ::Tox_Connection;
using ProxyType = ::Tox_Proxy_Type;
using SavedataType = ::Tox_Savedata_Type;
using UserStatus = ::Tox_User_Status;
using MessageType = ::Tox_Message_Type;
using FileControl = ::Tox_File_Control;
using OptionsNewError = ::Tox_Err_Options_New;
using NewError = ::Tox_Err_New;
using BootstrapError = ::Tox_Err_Bootstrap;
using SetInfoError = ::Tox_Err_Set_Info;
using FriendAddError = ::Tox_Err_Friend_Add;
using FriendDeleteError = ::Tox_Err_Friend_Delete;
using FriendByPublicKeyError = ::Tox_Err_Friend_By_Public_Key;
using FriendGetPublicKeyError = ::Tox_Err_Friend_Get_Public_Key;
using FriendQueryError = ::Tox_Err_Friend_Query;
using SetTypingError = ::Tox_Err_Set_Typing;
using FriendSendMessageError = ::Tox_Err_Friend_Send_Message;
using FriendCustomPacketError = ::Tox_Err_Friend_Custom_Packet;
using FileControlError = ::Tox_Err_File_Control;
using FileSeekError = ::Tox_Err_File_Seek;
using FileGetError = ::Tox_Err_File_Get;
using FileByIdError = ::Tox_Err_File_By_Id;
using FileSendError = ::Tox_Err_File_Send;
using FileSendChunkError = ::Tox_Err_File_Send_Chunk;

inline constexpr std::size_t kPublicKeySize = 32U;
inline constexpr std::size_t kAddressSize = 38U;
inline constexpr std::size_t kMaxNameLength = 128U;
inline constexpr std::size_t kMaxStatusMessageLength = 1007U;
inline constexpr std::size_t kMaxMessageLength = 1372U;
inline constexpr std::size_t kFileIdLength = 32U;
inline constexpr std::size_t kMaxFilenameLength = 255U;
inline constexpr std::size_t kMaxFriendRequestLength = 921U;
inline constexpr std::size_t kMaxCustomPacketSize = 1373U;
inline constexpr Connection kConnectionNone = TOX_CONNECTION_NONE;
inline constexpr Connection kConnectionTcp = TOX_CONNECTION_TCP;
inline constexpr Connection kConnectionUdp = TOX_CONNECTION_UDP;
inline constexpr ProxyType kProxyNone = TOX_PROXY_TYPE_NONE;
inline constexpr ProxyType kProxyHttp = TOX_PROXY_TYPE_HTTP;
inline constexpr ProxyType kProxySocks5 = TOX_PROXY_TYPE_SOCKS5;
inline constexpr SavedataType kSavedataNone = TOX_SAVEDATA_TYPE_NONE;
inline constexpr SavedataType kSavedataToxSave = TOX_SAVEDATA_TYPE_TOX_SAVE;
inline constexpr UserStatus kUserStatusNone = TOX_USER_STATUS_NONE;
inline constexpr UserStatus kUserStatusAway = TOX_USER_STATUS_AWAY;
inline constexpr UserStatus kUserStatusBusy = TOX_USER_STATUS_BUSY;
inline constexpr MessageType kMessageTypeNormal = TOX_MESSAGE_TYPE_NORMAL;
inline constexpr MessageType kMessageTypeAction = TOX_MESSAGE_TYPE_ACTION;
inline constexpr FileControl kFileControlResume = TOX_FILE_CONTROL_RESUME;
inline constexpr FileControl kFileControlPause = TOX_FILE_CONTROL_PAUSE;
inline constexpr FileControl kFileControlCancel = TOX_FILE_CONTROL_CANCEL;
inline constexpr std::uint32_t kFileKindData = 0U;
inline constexpr OptionsNewError kOptionsNewOk = TOX_ERR_OPTIONS_NEW_OK;
inline constexpr NewError kNewOk = TOX_ERR_NEW_OK;
inline constexpr BootstrapError kBootstrapOk = TOX_ERR_BOOTSTRAP_OK;
inline constexpr SetInfoError kSetInfoOk = TOX_ERR_SET_INFO_OK;
inline constexpr FriendAddError kFriendAddOk = TOX_ERR_FRIEND_ADD_OK;
inline constexpr FriendDeleteError kFriendDeleteOk = TOX_ERR_FRIEND_DELETE_OK;
inline constexpr FriendDeleteError kFriendDeleteNotFound =
    TOX_ERR_FRIEND_DELETE_FRIEND_NOT_FOUND;
inline constexpr FriendByPublicKeyError kFriendByPublicKeyOk =
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_OK;
inline constexpr FriendByPublicKeyError kFriendByPublicKeyNull =
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_NULL;
inline constexpr FriendByPublicKeyError kFriendByPublicKeyNotFound =
    TOX_ERR_FRIEND_BY_PUBLIC_KEY_NOT_FOUND;
inline constexpr FriendGetPublicKeyError kFriendGetPublicKeyOk =
    TOX_ERR_FRIEND_GET_PUBLIC_KEY_OK;
inline constexpr FriendQueryError kFriendQueryOk = TOX_ERR_FRIEND_QUERY_OK;
inline constexpr SetTypingError kSetTypingOk = TOX_ERR_SET_TYPING_OK;
inline constexpr FriendSendMessageError kFriendSendMessageOk =
    TOX_ERR_FRIEND_SEND_MESSAGE_OK;
inline constexpr FriendSendMessageError kFriendSendMessageNull =
    TOX_ERR_FRIEND_SEND_MESSAGE_NULL;
inline constexpr FriendSendMessageError kFriendSendMessageFriendNotFound =
    TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_FOUND;
inline constexpr FriendSendMessageError kFriendSendMessageFriendNotConnected =
    TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_CONNECTED;
inline constexpr FriendSendMessageError kFriendSendMessageSendQueueFull =
    TOX_ERR_FRIEND_SEND_MESSAGE_SENDQ;
inline constexpr FriendSendMessageError kFriendSendMessageTooLong =
    TOX_ERR_FRIEND_SEND_MESSAGE_TOO_LONG;
inline constexpr FriendSendMessageError kFriendSendMessageEmpty =
    TOX_ERR_FRIEND_SEND_MESSAGE_EMPTY;
inline constexpr FriendCustomPacketError kFriendCustomPacketOk =
    TOX_ERR_FRIEND_CUSTOM_PACKET_OK;
inline constexpr FriendCustomPacketError kFriendCustomPacketNull =
    TOX_ERR_FRIEND_CUSTOM_PACKET_NULL;
inline constexpr FriendCustomPacketError kFriendCustomPacketFriendNotFound =
    TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_FOUND;
inline constexpr FriendCustomPacketError kFriendCustomPacketFriendNotConnected =
    TOX_ERR_FRIEND_CUSTOM_PACKET_FRIEND_NOT_CONNECTED;
inline constexpr FriendCustomPacketError kFriendCustomPacketInvalid =
    TOX_ERR_FRIEND_CUSTOM_PACKET_INVALID;
inline constexpr FriendCustomPacketError kFriendCustomPacketEmpty =
    TOX_ERR_FRIEND_CUSTOM_PACKET_EMPTY;
inline constexpr FriendCustomPacketError kFriendCustomPacketTooLong =
    TOX_ERR_FRIEND_CUSTOM_PACKET_TOO_LONG;
inline constexpr FriendCustomPacketError kFriendCustomPacketSendQueueFull =
    TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ;
inline constexpr FileControlError kFileControlOk = TOX_ERR_FILE_CONTROL_OK;
inline constexpr FileControlError kFileControlAlreadyPaused =
    TOX_ERR_FILE_CONTROL_ALREADY_PAUSED;
inline constexpr FileSeekError kFileSeekOk = TOX_ERR_FILE_SEEK_OK;
inline constexpr FileGetError kFileGetOk = TOX_ERR_FILE_GET_OK;
inline constexpr FileByIdError kFileByIdOk = TOX_ERR_FILE_BY_ID_OK;
inline constexpr FileSendError kFileSendOk = TOX_ERR_FILE_SEND_OK;
inline constexpr FileSendChunkError kFileSendChunkOk = TOX_ERR_FILE_SEND_CHUNK_OK;
inline constexpr FileSendChunkError kFileSendChunkNull =
    TOX_ERR_FILE_SEND_CHUNK_NULL;
inline constexpr FileSendChunkError kFileSendChunkFriendNotFound =
    TOX_ERR_FILE_SEND_CHUNK_FRIEND_NOT_FOUND;
inline constexpr FileSendChunkError kFileSendChunkFriendNotConnected =
    TOX_ERR_FILE_SEND_CHUNK_FRIEND_NOT_CONNECTED;
inline constexpr FileSendChunkError kFileSendChunkNotFound =
    TOX_ERR_FILE_SEND_CHUNK_NOT_FOUND;
inline constexpr FileSendChunkError kFileSendChunkNotTransferring =
    TOX_ERR_FILE_SEND_CHUNK_NOT_TRANSFERRING;
inline constexpr FileSendChunkError kFileSendChunkInvalidLength =
    TOX_ERR_FILE_SEND_CHUNK_INVALID_LENGTH;
inline constexpr FileSendChunkError kFileSendChunkSendQueueFull =
    TOX_ERR_FILE_SEND_CHUNK_SENDQ;
inline constexpr FileSendChunkError kFileSendChunkWrongPosition =
    TOX_ERR_FILE_SEND_CHUNK_WRONG_POSITION;
inline constexpr FriendNumber kFriendNumberFailure = UINT32_MAX;
inline constexpr FileNumber kFileNumberFailure = UINT32_MAX;
inline constexpr bool kUsingSystemHeaders = IOTOX_TOXCORE_SYSTEM_HEADERS != 0;

using SelfConnectionCallback = void(Tox *, Connection, void *);
using FriendConnectionCallback = void(Tox *, FriendNumber, Connection, void *);
using FriendNameCallback =
    void(Tox *, FriendNumber, const std::uint8_t *, std::size_t, void *);
using FriendStatusMessageCallback =
    void(Tox *, FriendNumber, const std::uint8_t *, std::size_t, void *);
using FriendStatusCallback = void(Tox *, FriendNumber, UserStatus, void *);
using FriendTypingCallback = void(Tox *, FriendNumber, bool, void *);
using FriendRequestCallback =
    void(Tox *, const std::uint8_t *, const std::uint8_t *, std::size_t, void *);
using FriendMessageCallback = void(
    Tox *, FriendNumber, MessageType, const std::uint8_t *, std::size_t, void *);
using FriendReadReceiptCallback = void(Tox *, FriendNumber, FriendMessageId, void *);
using FriendLossyPacketCallback =
    void(Tox *, FriendNumber, const std::uint8_t *, std::size_t, void *);
using FriendLosslessPacketCallback =
    void(Tox *, FriendNumber, const std::uint8_t *, std::size_t, void *);
using FileRecvControlCallback =
    void(Tox *, FriendNumber, FileNumber, FileControl, void *);
using FileChunkRequestCallback =
    void(Tox *, FriendNumber, FileNumber, std::uint64_t, std::size_t, void *);
using FileRecvCallback = void(
    Tox *, FriendNumber, FileNumber, std::uint32_t, std::uint64_t,
    const std::uint8_t *, std::size_t, void *);
using FileRecvChunkCallback = void(
    Tox *, FriendNumber, FileNumber, std::uint64_t,
    const std::uint8_t *, std::size_t, void *);

struct Api {
    std::uint32_t (*version_major)(){};
    std::uint32_t (*version_minor)(){};
    std::uint32_t (*version_patch)(){};
    bool (*version_is_compatible)(std::uint32_t, std::uint32_t, std::uint32_t){};

    std::uint32_t (*public_key_size)(){};
    std::uint32_t (*address_size)(){};
    std::uint32_t (*max_name_length)(){};
    std::uint32_t (*max_status_message_length)(){};
    std::uint32_t (*max_message_length)(){};
    std::uint32_t (*file_id_length)(){};
    std::uint32_t (*max_filename_length)(){};
    std::uint32_t (*max_friend_request_length)(){};
    std::uint32_t (*max_custom_packet_size)(){};

    ToxOptions *(*options_new)(OptionsNewError *){};
    void (*options_free)(ToxOptions *){};
    void (*options_set_udp_enabled)(ToxOptions *, bool){};
    void (*options_set_local_discovery_enabled)(ToxOptions *, bool){};
    void (*options_set_dht_announcements_enabled)(ToxOptions *, bool){};
    void (*options_set_proxy_type)(ToxOptions *, ProxyType){};
    bool (*options_set_proxy_host)(ToxOptions *, const char *){};
    void (*options_set_proxy_port)(ToxOptions *, std::uint16_t){};
    void (*options_set_hole_punching_enabled)(ToxOptions *, bool){};
    void (*options_set_experimental_disable_dns)(ToxOptions *, bool){};
    void (*options_set_savedata_type)(ToxOptions *, SavedataType){};
    bool (*options_set_savedata_data)(ToxOptions *, const std::uint8_t *, std::size_t){};

    Tox *(*tox_new)(const ToxOptions *, NewError *){};
    void (*tox_kill)(Tox *){};
    bool (*bootstrap)(Tox *, const char *, std::uint16_t, const std::uint8_t *, BootstrapError *){};
    bool (*add_tcp_relay)(Tox *, const char *, std::uint16_t, const std::uint8_t *, BootstrapError *){};
    std::size_t (*get_savedata_size)(const Tox *){};
    void (*get_savedata)(const Tox *, std::uint8_t *){};
    std::uint32_t (*iteration_interval)(const Tox *){};
    void (*iterate)(Tox *, void *){};
    void (*self_get_address)(const Tox *, std::uint8_t *){};
    bool (*self_set_name)(Tox *, const std::uint8_t *, std::size_t, SetInfoError *){};
    std::size_t (*self_get_name_size)(const Tox *){};
    void (*self_get_name)(const Tox *, std::uint8_t *){};
    bool (*self_set_status_message)(Tox *, const std::uint8_t *, std::size_t, SetInfoError *){};
    std::size_t (*self_get_status_message_size)(const Tox *){};
    void (*self_get_status_message)(const Tox *, std::uint8_t *){};
    void (*self_set_status)(Tox *, UserStatus){};
    UserStatus (*self_get_status)(const Tox *){};
    bool (*self_set_typing)(Tox *, FriendNumber, bool, SetTypingError *){};

    void (*callback_self_connection_status)(Tox *, SelfConnectionCallback *){};
    void (*callback_friend_connection_status)(Tox *, FriendConnectionCallback *){};
    void (*callback_friend_name)(Tox *, FriendNameCallback *){};
    void (*callback_friend_status_message)(Tox *, FriendStatusMessageCallback *){};
    void (*callback_friend_status)(Tox *, FriendStatusCallback *){};
    void (*callback_friend_typing)(Tox *, FriendTypingCallback *){};
    void (*callback_friend_request)(Tox *, FriendRequestCallback *){};
    void (*callback_friend_message)(Tox *, FriendMessageCallback *){};
    void (*callback_friend_read_receipt)(Tox *, FriendReadReceiptCallback *){};
    void (*callback_friend_lossy_packet)(Tox *, FriendLossyPacketCallback *){};
    void (*callback_friend_lossless_packet)(Tox *, FriendLosslessPacketCallback *){};
    void (*callback_file_recv_control)(Tox *, FileRecvControlCallback *){};
    void (*callback_file_chunk_request)(Tox *, FileChunkRequestCallback *){};
    void (*callback_file_recv)(Tox *, FileRecvCallback *){};
    void (*callback_file_recv_chunk)(Tox *, FileRecvChunkCallback *){};

    FriendNumber (*friend_add)(
        Tox *, const std::uint8_t *, const std::uint8_t *, std::size_t, FriendAddError *){};
    FriendNumber (*friend_add_norequest)(Tox *, const std::uint8_t *, FriendAddError *){};
    bool (*friend_delete)(Tox *, FriendNumber, FriendDeleteError *){};
    FriendNumber (*friend_by_public_key)(
        const Tox *, const std::uint8_t *, FriendByPublicKeyError *){};
    std::size_t (*self_get_friend_list_size)(const Tox *){};
    void (*self_get_friend_list)(const Tox *, FriendNumber *){};
    bool (*friend_get_public_key)(
        const Tox *, FriendNumber, std::uint8_t *, FriendGetPublicKeyError *){};
    std::size_t (*friend_get_name_size)(const Tox *, FriendNumber, FriendQueryError *){};
    bool (*friend_get_name)(const Tox *, FriendNumber, std::uint8_t *, FriendQueryError *){};
    std::size_t (*friend_get_status_message_size)(const Tox *, FriendNumber, FriendQueryError *){};
    bool (*friend_get_status_message)(
        const Tox *, FriendNumber, std::uint8_t *, FriendQueryError *){};
    FriendMessageId (*friend_send_message)(
        Tox *, FriendNumber, MessageType, const std::uint8_t *, std::size_t,
        FriendSendMessageError *){};
    bool (*friend_send_lossy_packet)(
        Tox *, FriendNumber, const std::uint8_t *, std::size_t, FriendCustomPacketError *){};
    bool (*friend_send_lossless_packet)(
        Tox *, FriendNumber, const std::uint8_t *, std::size_t, FriendCustomPacketError *){};

    bool (*file_control)(
        Tox *, FriendNumber, FileNumber, FileControl, FileControlError *){};
    bool (*file_seek)(
        Tox *, FriendNumber, FileNumber, std::uint64_t, FileSeekError *){};
    bool (*file_get_file_id)(
        const Tox *, FriendNumber, FileNumber, std::uint8_t *, FileGetError *){};
    FileNumber (*file_by_id)(
        const Tox *, FriendNumber, const std::uint8_t *, FileByIdError *){};
    FileNumber (*file_send)(
        Tox *, FriendNumber, std::uint32_t, std::uint64_t,
        const std::uint8_t *, const std::uint8_t *, std::size_t, FileSendError *){};
    bool (*file_send_chunk)(
        Tox *, FriendNumber, FileNumber, std::uint64_t,
        const std::uint8_t *, std::size_t, FileSendChunkError *){};
};

}  // namespace iotox::toxcore::abi
