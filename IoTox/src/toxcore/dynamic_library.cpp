#include "iotox/toxcore/dynamic_library.hpp"

#include "iotox/toxcore/linked_api.hpp"

#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <sstream>
#include <string_view>
#include <utility>
#include <vector>

namespace iotox::toxcore {
namespace {

template <typename FunctionPointer>
Result<FunctionPointer> load_symbol(void *handle, const char *name) {
    ::dlerror();
    void *raw = ::dlsym(handle, name);
    const char *error = ::dlerror();
    if (error != nullptr || raw == nullptr) {
        return Status{ErrorCode::library_error,
                      "c-toxcore symbol '" + std::string(name) + "' is unavailable: " +
                          (error == nullptr ? std::string("unknown dlsym failure") : std::string(error))};
    }

    static_assert(sizeof(FunctionPointer) == sizeof(raw));
    FunctionPointer function{};
    std::memcpy(&function, &raw, sizeof(function));
    return function;
}

template <typename FunctionPointer>
Status assign_symbol(void *handle, const char *name, FunctionPointer &destination) {
    auto symbol = load_symbol<FunctionPointer>(handle, name);
    if (!symbol) {
        return symbol.status();
    }
    destination = symbol.value();
    return Status::success();
}

Status load_api(void *handle, abi::Api &api) {
#define IOTOX_LOAD(field, symbol_name)                         \
    do {                                                       \
        const Status status = assign_symbol(handle, symbol_name, api.field); \
        if (!status.ok()) {                                    \
            return status;                                     \
        }                                                      \
    } while (false)

    IOTOX_LOAD(version_major, "tox_version_major");
    IOTOX_LOAD(version_minor, "tox_version_minor");
    IOTOX_LOAD(version_patch, "tox_version_patch");
    IOTOX_LOAD(version_is_compatible, "tox_version_is_compatible");
    IOTOX_LOAD(public_key_size, "tox_public_key_size");
    IOTOX_LOAD(address_size, "tox_address_size");
    IOTOX_LOAD(max_name_length, "tox_max_name_length");
    IOTOX_LOAD(max_status_message_length, "tox_max_status_message_length");
    IOTOX_LOAD(max_message_length, "tox_max_message_length");
    IOTOX_LOAD(file_id_length, "tox_file_id_length");
    IOTOX_LOAD(max_filename_length, "tox_max_filename_length");
    IOTOX_LOAD(max_friend_request_length, "tox_max_friend_request_length");
    IOTOX_LOAD(max_custom_packet_size, "tox_max_custom_packet_size");
    IOTOX_LOAD(options_new, "tox_options_new");
    IOTOX_LOAD(options_free, "tox_options_free");
    IOTOX_LOAD(options_set_udp_enabled, "tox_options_set_udp_enabled");
    IOTOX_LOAD(options_set_local_discovery_enabled, "tox_options_set_local_discovery_enabled");
    IOTOX_LOAD(options_set_dht_announcements_enabled, "tox_options_set_dht_announcements_enabled");
    IOTOX_LOAD(options_set_proxy_type, "tox_options_set_proxy_type");
    IOTOX_LOAD(options_set_proxy_host, "tox_options_set_proxy_host");
    IOTOX_LOAD(options_set_proxy_port, "tox_options_set_proxy_port");
    IOTOX_LOAD(options_set_hole_punching_enabled, "tox_options_set_hole_punching_enabled");
    IOTOX_LOAD(options_set_experimental_disable_dns, "tox_options_set_experimental_disable_dns");
    IOTOX_LOAD(options_set_savedata_type, "tox_options_set_savedata_type");
    IOTOX_LOAD(options_set_savedata_data, "tox_options_set_savedata_data");
    IOTOX_LOAD(tox_new, "tox_new");
    IOTOX_LOAD(tox_kill, "tox_kill");
    IOTOX_LOAD(bootstrap, "tox_bootstrap");
    IOTOX_LOAD(add_tcp_relay, "tox_add_tcp_relay");
    IOTOX_LOAD(get_savedata_size, "tox_get_savedata_size");
    IOTOX_LOAD(get_savedata, "tox_get_savedata");
    IOTOX_LOAD(iteration_interval, "tox_iteration_interval");
    IOTOX_LOAD(iterate, "tox_iterate");
    IOTOX_LOAD(self_get_address, "tox_self_get_address");
    IOTOX_LOAD(self_set_name, "tox_self_set_name");
    IOTOX_LOAD(self_get_name_size, "tox_self_get_name_size");
    IOTOX_LOAD(self_get_name, "tox_self_get_name");
    IOTOX_LOAD(self_set_status_message, "tox_self_set_status_message");
    IOTOX_LOAD(self_get_status_message_size, "tox_self_get_status_message_size");
    IOTOX_LOAD(self_get_status_message, "tox_self_get_status_message");
    IOTOX_LOAD(self_set_status, "tox_self_set_status");
    IOTOX_LOAD(self_get_status, "tox_self_get_status");
    IOTOX_LOAD(self_set_typing, "tox_self_set_typing");
    IOTOX_LOAD(callback_self_connection_status, "tox_callback_self_connection_status");
    IOTOX_LOAD(callback_friend_connection_status, "tox_callback_friend_connection_status");
    IOTOX_LOAD(callback_friend_name, "tox_callback_friend_name");
    IOTOX_LOAD(callback_friend_status_message, "tox_callback_friend_status_message");
    IOTOX_LOAD(callback_friend_status, "tox_callback_friend_status");
    IOTOX_LOAD(callback_friend_typing, "tox_callback_friend_typing");
    IOTOX_LOAD(callback_friend_request, "tox_callback_friend_request");
    IOTOX_LOAD(callback_friend_message, "tox_callback_friend_message");
    IOTOX_LOAD(callback_friend_read_receipt, "tox_callback_friend_read_receipt");
    IOTOX_LOAD(callback_friend_lossy_packet, "tox_callback_friend_lossy_packet");
    IOTOX_LOAD(callback_friend_lossless_packet, "tox_callback_friend_lossless_packet");
    IOTOX_LOAD(callback_file_recv_control, "tox_callback_file_recv_control");
    IOTOX_LOAD(callback_file_chunk_request, "tox_callback_file_chunk_request");
    IOTOX_LOAD(callback_file_recv, "tox_callback_file_recv");
    IOTOX_LOAD(callback_file_recv_chunk, "tox_callback_file_recv_chunk");
    IOTOX_LOAD(friend_add, "tox_friend_add");
    IOTOX_LOAD(friend_add_norequest, "tox_friend_add_norequest");
    IOTOX_LOAD(friend_delete, "tox_friend_delete");
    IOTOX_LOAD(friend_by_public_key, "tox_friend_by_public_key");
    IOTOX_LOAD(self_get_friend_list_size, "tox_self_get_friend_list_size");
    IOTOX_LOAD(self_get_friend_list, "tox_self_get_friend_list");
    IOTOX_LOAD(friend_get_public_key, "tox_friend_get_public_key");
    IOTOX_LOAD(friend_get_name_size, "tox_friend_get_name_size");
    IOTOX_LOAD(friend_get_name, "tox_friend_get_name");
    IOTOX_LOAD(friend_get_status_message_size, "tox_friend_get_status_message_size");
    IOTOX_LOAD(friend_get_status_message, "tox_friend_get_status_message");
    IOTOX_LOAD(friend_send_message, "tox_friend_send_message");
    IOTOX_LOAD(friend_send_lossy_packet, "tox_friend_send_lossy_packet");
    IOTOX_LOAD(friend_send_lossless_packet, "tox_friend_send_lossless_packet");
    IOTOX_LOAD(file_control, "tox_file_control");
    IOTOX_LOAD(file_seek, "tox_file_seek");
    IOTOX_LOAD(file_get_file_id, "tox_file_get_file_id");
    IOTOX_LOAD(file_by_id, "tox_file_by_id");
    IOTOX_LOAD(file_send, "tox_file_send");
    IOTOX_LOAD(file_send_chunk, "tox_file_send_chunk");

#undef IOTOX_LOAD
    return Status::success();
}

std::vector<std::string> library_candidates(const std::filesystem::path &explicit_path) {
    if (!explicit_path.empty()) {
        return {explicit_path.string()};
    }
    if (const char *environment = std::getenv("IOTOX_TOXCORE_LIBRARY"); environment != nullptr && environment[0] != '\0') {
        return {environment};
    }
    return {"libtoxcore.so.2", "libtoxcore.so"};
}

}  // namespace

std::string LibraryVersion::str() const {
    return std::to_string(major) + "." + std::to_string(minor) + "." + std::to_string(patch);
}

DynamicToxcore::~DynamicToxcore() {
    if (handle_ != nullptr) {
        ::dlclose(handle_);
    }
}

DynamicToxcore::DynamicToxcore(DynamicToxcore &&other) noexcept
    : handle_(std::exchange(other.handle_, nullptr)), api_(other.api_), loaded_path_(std::move(other.loaded_path_)) {
    other.api_ = {};
}

DynamicToxcore &DynamicToxcore::operator=(DynamicToxcore &&other) noexcept {
    if (this != &other) {
        if (handle_ != nullptr) {
            ::dlclose(handle_);
        }
        handle_ = std::exchange(other.handle_, nullptr);
        api_ = other.api_;
        loaded_path_ = std::move(other.loaded_path_);
        other.api_ = {};
    }
    return *this;
}

Result<DynamicToxcore> DynamicToxcore::load(const std::filesystem::path &explicit_path) {
#if defined(IOTOX_LINKED_TOXCORE)
    const char *environment = std::getenv("IOTOX_TOXCORE_LIBRARY");
    const bool explicit_dynamic = !explicit_path.empty() ||
                                  (environment != nullptr && environment[0] != '\0');
    if (!explicit_dynamic) {
        DynamicToxcore library;
        library.api_ = linked_toxcore_api();
#if defined(IOTOX_LINKED_TOXCORE_VARIANT)
        library.loaded_path_ =
            "linked:c-toxcore+" IOTOX_LINKED_TOXCORE_VARIANT;
#else
        library.loaded_path_ = "linked:c-toxcore";
#endif
        return library;
    }
#endif
    std::ostringstream failures;
    for (const std::string &candidate : library_candidates(explicit_path)) {
        ::dlerror();
        void *handle = ::dlopen(candidate.c_str(), RTLD_NOW | RTLD_LOCAL);
        if (handle == nullptr) {
            const char *message = ::dlerror();
            failures << candidate << ": " << (message == nullptr ? "unknown dlopen failure" : message) << "\n";
            continue;
        }

        abi::Api api{};
        const Status load_status = load_api(handle, api);
        if (!load_status.ok()) {
            failures << candidate << ": " << load_status.message() << "\n";
            ::dlclose(handle);
            continue;
        }

        DynamicToxcore library;
        library.handle_ = handle;
        library.api_ = api;
        library.loaded_path_ = candidate;
        return library;
    }

    return Status{ErrorCode::unavailable,
                  "unable to load a compatible c-toxcore shared library:\n" + failures.str()};
}

LibraryVersion DynamicToxcore::version() const {
    return {api_.version_major(), api_.version_minor(), api_.version_patch()};
}

}  // namespace iotox::toxcore
