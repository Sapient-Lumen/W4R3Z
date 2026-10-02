#include "iotox/toxcore/linked_api.hpp"

#if defined(IOTOX_LINKED_TOXCORE)
static_assert(IOTOX_TOXCORE_SYSTEM_HEADERS == 1,
              "source-linked IoTox must compile against canonical c-toxcore headers");
static_assert(TOX_VERSION_IS_API_COMPATIBLE(0, 2, 23),
              "source-linked c-toxcore headers are older than IoTox's 0.2.23 contract");
#endif

namespace iotox::toxcore {

abi::Api linked_toxcore_api() noexcept {
    abi::Api api{};
#if defined(IOTOX_LINKED_TOXCORE)
    api.version_major = &::tox_version_major;
    api.version_minor = &::tox_version_minor;
    api.version_patch = &::tox_version_patch;
    api.version_is_compatible = &::tox_version_is_compatible;
    api.public_key_size = &::tox_public_key_size;
    api.address_size = &::tox_address_size;
    api.max_name_length = &::tox_max_name_length;
    api.max_status_message_length = &::tox_max_status_message_length;
    api.max_message_length = &::tox_max_message_length;
    api.file_id_length = &::tox_file_id_length;
    api.max_filename_length = &::tox_max_filename_length;
    api.max_friend_request_length = &::tox_max_friend_request_length;
    api.max_custom_packet_size = &::tox_max_custom_packet_size;
    api.options_new = &::tox_options_new;
    api.options_free = &::tox_options_free;
    api.options_set_udp_enabled = &::tox_options_set_udp_enabled;
    api.options_set_local_discovery_enabled = &::tox_options_set_local_discovery_enabled;
    api.options_set_dht_announcements_enabled = &::tox_options_set_dht_announcements_enabled;
    api.options_set_proxy_type = &::tox_options_set_proxy_type;
    api.options_set_proxy_host = &::tox_options_set_proxy_host;
    api.options_set_proxy_port = &::tox_options_set_proxy_port;
    api.options_set_hole_punching_enabled = &::tox_options_set_hole_punching_enabled;
    api.options_set_experimental_disable_dns = &::tox_options_set_experimental_disable_dns;
    api.options_set_savedata_type = &::tox_options_set_savedata_type;
    api.options_set_savedata_data = &::tox_options_set_savedata_data;
    api.tox_new = &::tox_new;
    api.tox_kill = &::tox_kill;
    api.bootstrap = &::tox_bootstrap;
    api.add_tcp_relay = &::tox_add_tcp_relay;
    api.get_savedata_size = &::tox_get_savedata_size;
    api.get_savedata = &::tox_get_savedata;
    api.iteration_interval = &::tox_iteration_interval;
    api.iterate = &::tox_iterate;
    api.self_get_address = &::tox_self_get_address;
    api.self_set_name = &::tox_self_set_name;
    api.self_get_name_size = &::tox_self_get_name_size;
    api.self_get_name = &::tox_self_get_name;
    api.self_set_status_message = &::tox_self_set_status_message;
    api.self_get_status_message_size = &::tox_self_get_status_message_size;
    api.self_get_status_message = &::tox_self_get_status_message;
    api.self_set_status = &::tox_self_set_status;
    api.self_get_status = &::tox_self_get_status;
    api.self_set_typing = &::tox_self_set_typing;
    api.callback_self_connection_status = &::tox_callback_self_connection_status;
    api.callback_friend_connection_status = &::tox_callback_friend_connection_status;
    api.callback_friend_name = &::tox_callback_friend_name;
    api.callback_friend_status_message = &::tox_callback_friend_status_message;
    api.callback_friend_status = &::tox_callback_friend_status;
    api.callback_friend_typing = &::tox_callback_friend_typing;
    api.callback_friend_request = &::tox_callback_friend_request;
    api.callback_friend_message = &::tox_callback_friend_message;
    api.callback_friend_read_receipt = &::tox_callback_friend_read_receipt;
    api.callback_friend_lossy_packet = &::tox_callback_friend_lossy_packet;
    api.callback_friend_lossless_packet = &::tox_callback_friend_lossless_packet;
    api.callback_file_recv_control = &::tox_callback_file_recv_control;
    api.callback_file_chunk_request = &::tox_callback_file_chunk_request;
    api.callback_file_recv = &::tox_callback_file_recv;
    api.callback_file_recv_chunk = &::tox_callback_file_recv_chunk;
    api.friend_add = &::tox_friend_add;
    api.friend_add_norequest = &::tox_friend_add_norequest;
    api.friend_delete = &::tox_friend_delete;
    api.friend_by_public_key = &::tox_friend_by_public_key;
    api.self_get_friend_list_size = &::tox_self_get_friend_list_size;
    api.self_get_friend_list = &::tox_self_get_friend_list;
    api.friend_get_public_key = &::tox_friend_get_public_key;
    api.friend_get_name_size = &::tox_friend_get_name_size;
    api.friend_get_name = &::tox_friend_get_name;
    api.friend_get_status_message_size = &::tox_friend_get_status_message_size;
    api.friend_get_status_message = &::tox_friend_get_status_message;
    api.friend_send_message = &::tox_friend_send_message;
    api.friend_send_lossy_packet = &::tox_friend_send_lossy_packet;
    api.friend_send_lossless_packet = &::tox_friend_send_lossless_packet;
    api.file_control = &::tox_file_control;
    api.file_seek = &::tox_file_seek;
    api.file_get_file_id = &::tox_file_get_file_id;
    api.file_by_id = &::tox_file_by_id;
    api.file_send = &::tox_file_send;
    api.file_send_chunk = &::tox_file_send_chunk;
#endif
    return api;
}

}  // namespace iotox::toxcore
