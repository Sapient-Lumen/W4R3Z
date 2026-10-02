#include <toxcore/tox.h>

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

enum {
    MAX_SAVEDATA_BYTES = 16 * 1024 * 1024,
};

static void fail(const char *message)
{
    fprintf(stderr, "provider fixture: %s\n", message);
    exit(EXIT_FAILURE);
}

static uint8_t *read_file(const char *path, size_t *size)
{
    FILE *stream = fopen(path, "rb");

    if (stream == NULL) {
        fail("unable to open savedata input");
    }

    if (fseek(stream, 0, SEEK_END) != 0) {
        fail("unable to seek savedata input");
    }

    const long length = ftell(stream);

    if (length <= 0 || length > MAX_SAVEDATA_BYTES || fseek(stream, 0, SEEK_SET) != 0) {
        fail("savedata input has an invalid size");
    }

    uint8_t *data = (uint8_t *)malloc((size_t)length);

    if (data == NULL || fread(data, 1, (size_t)length, stream) != (size_t)length) {
        fail("unable to read savedata input");
    }

    if (fclose(stream) != 0) {
        fail("unable to close savedata input");
    }

    *size = (size_t)length;
    return data;
}

static void write_savedata(const Tox *tox, const char *path)
{
    const size_t size = tox_get_savedata_size(tox);

    if (size == 0 || size > MAX_SAVEDATA_BYTES) {
        fail("provider returned an invalid savedata size");
    }

    uint8_t *data = (uint8_t *)malloc(size);

    if (data == NULL) {
        fail("unable to allocate savedata output");
    }

    tox_get_savedata(tox, data);
    FILE *stream = fopen(path, "wb");

    if (stream == NULL || chmod(path, S_IRUSR | S_IWUSR) != 0 ||
        fwrite(data, 1, size, stream) != size || fflush(stream) != 0 ||
        fclose(stream) != 0) {
        free(data);
        fail("unable to write private savedata output");
    }

    free(data);
}

static Tox *open_tox_with_route(const char *savedata_path, bool udp_enabled)
{
    Tox_Err_Options_New options_error;
    Tox_Options *options = tox_options_new(&options_error);

    if (options == NULL || options_error != TOX_ERR_OPTIONS_NEW_OK) {
        fail("unable to allocate provider options");
    }

    tox_options_default(options);
    tox_options_set_ipv6_enabled(options, false);
    tox_options_set_udp_enabled(options, udp_enabled);
    tox_options_set_local_discovery_enabled(options, false);
    uint8_t *savedata = NULL;

    if (savedata_path != NULL) {
        size_t savedata_size = 0;
        savedata = read_file(savedata_path, &savedata_size);
        tox_options_set_savedata_type(options, TOX_SAVEDATA_TYPE_TOX_SAVE);
        tox_options_set_savedata_data(options, savedata, savedata_size);
    }

    Tox_Err_New tox_error;
    Tox *tox = tox_new(options, &tox_error);
    tox_options_free(options);
    free(savedata);

    if (tox == NULL || tox_error != TOX_ERR_NEW_OK) {
        fail("provider refused savedata");
    }

    return tox;
}

static Tox *open_tox(const char *savedata_path)
{
    return open_tox_with_route(savedata_path, true);
}

static void print_hex(const uint8_t *data, size_t size)
{
    static const char digits[] = "0123456789ABCDEF";

    for (size_t index = 0; index < size; ++index) {
        putchar(digits[data[index] >> 4]);
        putchar(digits[data[index] & 0x0f]);
    }
}

static uint8_t decode_nibble(char value)
{
    if (value >= '0' && value <= '9') {
        return (uint8_t)(value - '0');
    }

    if (value >= 'a' && value <= 'f') {
        return (uint8_t)(value - 'a' + 10);
    }

    if (value >= 'A' && value <= 'F') {
        return (uint8_t)(value - 'A' + 10);
    }

    fail("public key contains non-hexadecimal data");
    return 0;
}

static void decode_public_key(const char *text, uint8_t key[TOX_PUBLIC_KEY_SIZE])
{
    if (strlen(text) != TOX_PUBLIC_KEY_SIZE * 2) {
        fail("public key has the wrong size");
    }

    for (size_t index = 0; index < TOX_PUBLIC_KEY_SIZE; ++index) {
        key[index] = (uint8_t)((decode_nibble(text[index * 2]) << 4) |
                              decode_nibble(text[index * 2 + 1]));
    }
}

static void print_profile_bytes(const char *label, const uint8_t *data, size_t size)
{
    printf("%s=", label);
    print_hex(data, size);
    putchar('\n');
}

static void inspect(const char *path)
{
    Tox *tox = open_tox(path);
    uint8_t address[TOX_ADDRESS_SIZE];
    uint8_t public_key[TOX_PUBLIC_KEY_SIZE];
    tox_self_get_address(tox, address);
    tox_self_get_public_key(tox, public_key);
    printf("provider-version=%" PRIu32 ".%" PRIu32 ".%" PRIu32 "\n",
           tox_version_major(), tox_version_minor(), tox_version_patch());
    printf("address=");
    print_hex(address, sizeof(address));
    printf("\npublic-key=");
    print_hex(public_key, sizeof(public_key));
    putchar('\n');

    const size_t name_size = tox_self_get_name_size(tox);
    uint8_t name[TOX_MAX_NAME_LENGTH];

    if (name_size > sizeof(name)) {
        fail("provider returned an oversized name");
    }

    tox_self_get_name(tox, name);
    print_profile_bytes("name-hex", name, name_size);
    const size_t status_size = tox_self_get_status_message_size(tox);
    uint8_t status_message[TOX_MAX_STATUS_MESSAGE_LENGTH];

    if (status_size > sizeof(status_message)) {
        fail("provider returned an oversized status message");
    }

    tox_self_get_status_message(tox, status_message);
    print_profile_bytes("status-message-hex", status_message, status_size);
    printf("status=%u\n", (unsigned int)tox_self_get_status(tox));

    const size_t friend_count = tox_self_get_friend_list_size(tox);
    printf("friend-count=%zu\n", friend_count);

    if (friend_count > 1024) {
        fail("provider returned an excessive friend count");
    }

    uint32_t *friends = friend_count == 0 ? NULL : (uint32_t *)calloc(friend_count, sizeof(uint32_t));

    if (friend_count != 0 && friends == NULL) {
        fail("unable to allocate friend inventory");
    }

    tox_self_get_friend_list(tox, friends);

    for (size_t index = 0; index < friend_count; ++index) {
        uint8_t friend_key[TOX_PUBLIC_KEY_SIZE];
        Tox_Err_Friend_Get_Public_Key error;

        if (!tox_friend_get_public_key(tox, friends[index], friend_key, &error) ||
            error != TOX_ERR_FRIEND_GET_PUBLIC_KEY_OK) {
            fail("unable to read friend public key");
        }

        printf("friend-%zu=", index);
        print_hex(friend_key, sizeof(friend_key));
        putchar('\n');
    }

    free(friends);
    tox_kill(tox);
}

static void create_savedata(const char *path, const char *name, const char *status_message)
{
    Tox *tox = open_tox(NULL);
    Tox_Err_Set_Info error;

    if (!tox_self_set_name(tox, (const uint8_t *)name, strlen(name), &error) ||
        error != TOX_ERR_SET_INFO_OK ||
        !tox_self_set_status_message(tox, (const uint8_t *)status_message,
                                     strlen(status_message), &error) ||
        error != TOX_ERR_SET_INFO_OK) {
        fail("unable to set fixture profile");
    }

    tox_self_set_status(tox, TOX_USER_STATUS_AWAY);
    write_savedata(tox, path);
    tox_kill(tox);
}

static void add_friend(const char *input, const char *peer_key_text, const char *output)
{
    Tox *tox = open_tox(input);
    uint8_t peer_key[TOX_PUBLIC_KEY_SIZE];
    decode_public_key(peer_key_text, peer_key);
    Tox_Err_Friend_Add error;
    const uint32_t friend_number = tox_friend_add_norequest(tox, peer_key, &error);

    if (friend_number == UINT32_MAX || error != TOX_ERR_FRIEND_ADD_OK) {
        fail("unable to add fixture friend");
    }

    write_savedata(tox, output);
    tox_kill(tox);
}

static void rewrite_savedata(const char *input, const char *output)
{
    Tox *tox = open_tox(input);
    write_savedata(tox, output);
    tox_kill(tox);
}

struct Exchange_State {
    uint32_t friend_number;
    const char *expected_message;
    size_t expected_message_size;
    bool received;
};

static void receive_message(Tox *tox, uint32_t friend_number,
                            Tox_Message_Type type, const uint8_t *message,
                            size_t length, void *user_data)
{
    (void)tox;
    struct Exchange_State *state = (struct Exchange_State *)user_data;

    if (friend_number == state->friend_number && type == TOX_MESSAGE_TYPE_NORMAL &&
        length == state->expected_message_size &&
        memcmp(message, state->expected_message, length) == 0) {
        state->received = true;
    }
}

static uint16_t decode_port(const char *text)
{
    errno = 0;
    char *end = NULL;
    const unsigned long value = strtoul(text, &end, 10);

    if (errno != 0 || end == text || *end != '\0' || value == 0 || value > UINT16_MAX) {
        fail("bootstrap port is invalid");
    }

    return (uint16_t)value;
}

static uint64_t monotonic_milliseconds(void)
{
    struct timespec value;

    if (clock_gettime(CLOCK_MONOTONIC, &value) != 0) {
        fail("monotonic clock is unavailable");
    }

    return (uint64_t)value.tv_sec * UINT64_C(1000) + (uint64_t)value.tv_nsec / UINT64_C(1000000);
}

static const char *connection_name(Tox_Connection connection)
{
    switch (connection) {
        case TOX_CONNECTION_TCP:
            return "tcp";
        case TOX_CONNECTION_UDP:
            return "udp";
        case TOX_CONNECTION_NONE:
            return "none";
    }

    fail("provider returned an unknown connection kind");
    return "unknown";
}

static void exchange(const char *input, const char *peer_key_text,
                     const char *bootstrap_host, const char *bootstrap_port_text,
                     const char *bootstrap_key_text, const char *route,
                     const char *send_message, const char *expected_message,
                     const char *output)
{
    const bool udp_enabled = strcmp(route, "direct-udp") == 0;

    if (!udp_enabled && strcmp(route, "forced-tcp") != 0) {
        fail("route must be direct-udp or forced-tcp");
    }

    const size_t send_size = strlen(send_message);
    const size_t expected_size = strlen(expected_message);

    if (send_size == 0 || send_size > TOX_MAX_MESSAGE_LENGTH || expected_size == 0 ||
        expected_size > TOX_MAX_MESSAGE_LENGTH) {
        fail("exchange message has an invalid size");
    }

    uint8_t peer_key[TOX_PUBLIC_KEY_SIZE];
    uint8_t bootstrap_key[TOX_DHT_ID_SIZE];
    decode_public_key(peer_key_text, peer_key);
    decode_public_key(bootstrap_key_text, bootstrap_key);
    const uint16_t bootstrap_port = decode_port(bootstrap_port_text);
    Tox *tox = open_tox_with_route(input, udp_enabled);
    Tox_Err_Friend_By_Public_Key friend_error;
    const uint32_t friend_number = tox_friend_by_public_key(tox, peer_key, &friend_error);

    if (friend_number == UINT32_MAX || friend_error != TOX_ERR_FRIEND_BY_PUBLIC_KEY_OK) {
        fail("peer is absent from exchange savedata");
    }

    Tox_Err_Bootstrap bootstrap_error;

    if (!tox_bootstrap(tox, bootstrap_host, bootstrap_port, bootstrap_key, &bootstrap_error) ||
        bootstrap_error != TOX_ERR_BOOTSTRAP_OK) {
        fail("provider refused bootstrap endpoint");
    }

    if (!udp_enabled &&
        (!tox_add_tcp_relay(tox, bootstrap_host, bootstrap_port, bootstrap_key,
                            &bootstrap_error) ||
         bootstrap_error != TOX_ERR_BOOTSTRAP_OK)) {
        fail("provider refused TCP relay endpoint");
    }

    struct Exchange_State state = {
        .friend_number = friend_number,
        .expected_message = expected_message,
        .expected_message_size = expected_size,
        .received = false,
    };
    tox_callback_friend_message(tox, receive_message);
    const Tox_Connection expected_connection =
        udp_enabled ? TOX_CONNECTION_UDP : TOX_CONNECTION_TCP;
    Tox_Connection observed_self = TOX_CONNECTION_NONE;
    Tox_Connection observed_friend = TOX_CONNECTION_NONE;
    bool sent = false;
    const uint64_t deadline = monotonic_milliseconds() + UINT64_C(180000);
    uint64_t next_bootstrap = 0;

    while (monotonic_milliseconds() < deadline && (!sent || !state.received)) {
        tox_iterate(tox, &state);
        observed_self = tox_self_get_connection_status(tox);
        Tox_Err_Friend_Query query_error;
        observed_friend = tox_friend_get_connection_status(tox, friend_number, &query_error);

        if (query_error != TOX_ERR_FRIEND_QUERY_OK) {
            tox_kill(tox);
            fail("unable to query exchange friend connection");
        }

        const uint64_t now = monotonic_milliseconds();

        if (now >= next_bootstrap && observed_self == TOX_CONNECTION_NONE) {
            (void)tox_bootstrap(tox, bootstrap_host, bootstrap_port, bootstrap_key,
                                &bootstrap_error);

            if (!udp_enabled) {
                (void)tox_add_tcp_relay(tox, bootstrap_host, bootstrap_port,
                                        bootstrap_key, &bootstrap_error);
            }

            next_bootstrap = now + UINT64_C(5000);
        }

        if (!sent && observed_friend == expected_connection) {
            Tox_Err_Friend_Send_Message send_error;
            (void)tox_friend_send_message(tox, friend_number, TOX_MESSAGE_TYPE_NORMAL,
                                          (const uint8_t *)send_message, send_size,
                                          &send_error);

            if (send_error != TOX_ERR_FRIEND_SEND_MESSAGE_OK) {
                tox_kill(tox);
                fail("provider failed to enqueue exchange message");
            }

            sent = true;
        }

        uint32_t delay = tox_iteration_interval(tox);

        if (delay > 50) {
            delay = 50;
        }

        usleep((useconds_t)delay * 1000U);
    }

    if (!sent || !state.received || observed_friend != expected_connection) {
        tox_kill(tox);
        fail("timed out before the mixed-provider exchange completed");
    }

    write_savedata(tox, output);
    printf("provider-version=%" PRIu32 ".%" PRIu32 ".%" PRIu32 "\n",
           tox_version_major(), tox_version_minor(), tox_version_patch());
    printf("route=%s\n", route);
    printf("self-connection=%s\n", connection_name(observed_self));
    printf("friend-connection=%s\n", connection_name(observed_friend));
    printf("sent=1\nreceived=1\n");
    tox_kill(tox);
}

int main(int argc, char **argv)
{
    if (argc == 5 && strcmp(argv[1], "create") == 0) {
        create_savedata(argv[2], argv[3], argv[4]);
        return EXIT_SUCCESS;
    }

    if (argc == 3 && strcmp(argv[1], "inspect") == 0) {
        inspect(argv[2]);
        return EXIT_SUCCESS;
    }

    if (argc == 5 && strcmp(argv[1], "friend") == 0) {
        add_friend(argv[2], argv[3], argv[4]);
        return EXIT_SUCCESS;
    }

    if (argc == 4 && strcmp(argv[1], "rewrite") == 0) {
        rewrite_savedata(argv[2], argv[3]);
        return EXIT_SUCCESS;
    }

    if (argc == 11 && strcmp(argv[1], "exchange") == 0) {
        exchange(argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], argv[8],
                 argv[9], argv[10]);
        return EXIT_SUCCESS;
    }

    fprintf(stderr,
            "usage: %s create SAVE NAME STATUS | inspect SAVE | "
            "friend INPUT PEER_PUBLIC_KEY OUTPUT | rewrite INPUT OUTPUT | "
            "exchange INPUT PEER_PUBLIC_KEY HOST PORT BOOTSTRAP_PUBLIC_KEY "
            "direct-udp|forced-tcp SEND EXPECT OUTPUT\n",
            argv[0]);
    return 2;
}
