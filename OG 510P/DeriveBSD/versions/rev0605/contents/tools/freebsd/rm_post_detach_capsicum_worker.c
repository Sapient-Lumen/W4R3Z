/*
 * DeriveBSD removable-media local-fallback post-detach worker scaffold.
 *
 * Build target: FreeBSD.  The broker must open the preserved capture read fd as
 * REMEDIA_INPUT_FD and the derivative output write fd as REMEDIA_OUTPUT_FD,
 * then exec this worker after the source media has been unmounted/detached.
 *
 * This source is intentionally pathless: no device path, mountpoint path, media
 * path, or output path is accepted through argv or environment.  Production
 * execution uses the delegated output fd for startup failures too; it does not
 * rely on stderr before or after closing fd 0/1/2.  After stdio is closed, the
 * only remaining data plane is the two broker-delegated descriptors.  The worker
 * closes fd 5 and above, then verifies a bounded low-fd range before cap_enter()
 * so a launcher-provided canary proves unexpected inherited fds are not kept.
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef __FreeBSD__
#include <sys/capsicum.h>
#elif defined(DERIVEBSD_CAPSICUM_COMPILE_PROBE)
#include "derivebsd_capsicum_probe_shim.h"
#else
#error "rm_post_detach_capsicum_worker.c is a FreeBSD-only worker scaffold; use the Python fixture worker outside FreeBSD."
#endif

#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define REMEDIA_INPUT_FD 3
#define REMEDIA_OUTPUT_FD 4
#define FD_AFTER_DELEGATED_SET 5
#define EXTRA_FD_SCAN_LIMIT 64
#define BUFFER_BYTES 65536

static bool standard_fds_closed = false;
static bool extra_fds_closed_before_cap_enter = false;
static bool extra_fd_canary_observed_before_closefrom = false;

struct sha256_ctx {
    uint8_t data[64];
    uint32_t datalen;
    uint64_t bitlen;
    uint32_t state[8];
};

static const uint32_t sha256_k[64] = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
    0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
    0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
    0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
    0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
    0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
    0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
    0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U
};

static uint32_t
rotr32(uint32_t x, uint32_t n)
{
    return (x >> n) | (x << (32U - n));
}

static void
sha256_transform(struct sha256_ctx *ctx, const uint8_t data[64])
{
    uint32_t a, b, c, d, e, f, g, h, i, j, t1, t2, m[64];

    for (i = 0, j = 0; i < 16; i++, j += 4) {
        m[i] = ((uint32_t)data[j] << 24) |
            ((uint32_t)data[j + 1] << 16) |
            ((uint32_t)data[j + 2] << 8) |
            (uint32_t)data[j + 3];
    }
    for (; i < 64; i++) {
        uint32_t s0 = rotr32(m[i - 15], 7) ^ rotr32(m[i - 15], 18) ^ (m[i - 15] >> 3);
        uint32_t s1 = rotr32(m[i - 2], 17) ^ rotr32(m[i - 2], 19) ^ (m[i - 2] >> 10);
        m[i] = m[i - 16] + s0 + m[i - 7] + s1;
    }

    a = ctx->state[0];
    b = ctx->state[1];
    c = ctx->state[2];
    d = ctx->state[3];
    e = ctx->state[4];
    f = ctx->state[5];
    g = ctx->state[6];
    h = ctx->state[7];

    for (i = 0; i < 64; i++) {
        uint32_t s1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25);
        uint32_t ch = (e & f) ^ ((~e) & g);
        t1 = h + s1 + ch + sha256_k[i] + m[i];
        uint32_t s0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        t2 = s0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    ctx->state[0] += a;
    ctx->state[1] += b;
    ctx->state[2] += c;
    ctx->state[3] += d;
    ctx->state[4] += e;
    ctx->state[5] += f;
    ctx->state[6] += g;
    ctx->state[7] += h;
}

static void
sha256_init(struct sha256_ctx *ctx)
{
    ctx->datalen = 0;
    ctx->bitlen = 0;
    ctx->state[0] = 0x6a09e667U;
    ctx->state[1] = 0xbb67ae85U;
    ctx->state[2] = 0x3c6ef372U;
    ctx->state[3] = 0xa54ff53aU;
    ctx->state[4] = 0x510e527fU;
    ctx->state[5] = 0x9b05688cU;
    ctx->state[6] = 0x1f83d9abU;
    ctx->state[7] = 0x5be0cd19U;
}

static void
sha256_update(struct sha256_ctx *ctx, const uint8_t *data, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        ctx->data[ctx->datalen++] = data[i];
        if (ctx->datalen == 64) {
            sha256_transform(ctx, ctx->data);
            ctx->bitlen += 512;
            ctx->datalen = 0;
        }
    }
}

static void
sha256_final(struct sha256_ctx *ctx, uint8_t hash[32])
{
    uint32_t i = ctx->datalen;

    if (ctx->datalen < 56) {
        ctx->data[i++] = 0x80;
        while (i < 56)
            ctx->data[i++] = 0x00;
    } else {
        ctx->data[i++] = 0x80;
        while (i < 64)
            ctx->data[i++] = 0x00;
        sha256_transform(ctx, ctx->data);
        memset(ctx->data, 0, 56);
    }

    ctx->bitlen += (uint64_t)ctx->datalen * 8U;
    ctx->data[63] = (uint8_t)(ctx->bitlen);
    ctx->data[62] = (uint8_t)(ctx->bitlen >> 8);
    ctx->data[61] = (uint8_t)(ctx->bitlen >> 16);
    ctx->data[60] = (uint8_t)(ctx->bitlen >> 24);
    ctx->data[59] = (uint8_t)(ctx->bitlen >> 32);
    ctx->data[58] = (uint8_t)(ctx->bitlen >> 40);
    ctx->data[57] = (uint8_t)(ctx->bitlen >> 48);
    ctx->data[56] = (uint8_t)(ctx->bitlen >> 56);
    sha256_transform(ctx, ctx->data);

    for (i = 0; i < 4; i++) {
        hash[i] = (uint8_t)((ctx->state[0] >> (24 - i * 8)) & 0xff);
        hash[i + 4] = (uint8_t)((ctx->state[1] >> (24 - i * 8)) & 0xff);
        hash[i + 8] = (uint8_t)((ctx->state[2] >> (24 - i * 8)) & 0xff);
        hash[i + 12] = (uint8_t)((ctx->state[3] >> (24 - i * 8)) & 0xff);
        hash[i + 16] = (uint8_t)((ctx->state[4] >> (24 - i * 8)) & 0xff);
        hash[i + 20] = (uint8_t)((ctx->state[5] >> (24 - i * 8)) & 0xff);
        hash[i + 24] = (uint8_t)((ctx->state[6] >> (24 - i * 8)) & 0xff);
        hash[i + 28] = (uint8_t)((ctx->state[7] >> (24 - i * 8)) & 0xff);
    }
}

static void
sha256_digest_to_prefixed_hex(const uint8_t digest[32], char out[72])
{
    static const char hex[] = "0123456789abcdef";

    memcpy(out, "sha256:", 7);
    for (size_t i = 0; i < 32; i++) {
        out[7 + i * 2] = hex[digest[i] >> 4];
        out[8 + i * 2] = hex[digest[i] & 0x0f];
    }
    out[71] = '\0';
}

static bool
write_all_best_effort(int fd, const char *buf, size_t len)
{
    while (len > 0) {
        ssize_t n = write(fd, buf, len);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return false;
        }
        if (n == 0)
            return false;
        buf += (size_t)n;
        len -= (size_t)n;
    }
    return true;
}

static const char *
failure_channel_for_current_stdio_state(void)
{
    if (standard_fds_closed)
        return "delegated-output-fd-after-stdio-close";
    return "delegated-output-fd-before-stdio-close";
}

static void
fatal_to_delegated_output(const char *error_code, bool cap_entered)
{
    char report[1024];
    int report_len;

    report_len = snprintf(report, sizeof(report),
        "{\"kind\":\"removable.media.local.freebsd.capsicum.worker.report\","
        "\"result\":\"failed\","
        "\"error_code\":\"%s\","
        "\"capsicum_mode_entered\":%s,"
        "\"input_fd\":%d,"
        "\"output_fd\":%d,"
        "\"stdio_fds_closed_before_cap_enter\":%s,"
        "\"stdio_fds_closed_before_report\":%s,"
        "\"extra_fds_closed_before_cap_enter\":%s,"
        "\"extra_fd_scan_limit\":%d,"
        "\"extra_fd_canary\":%d,"
        "\"extra_fd_canary_source\":\"broker-nonmedia-canary-not-source-media\","
        "\"extra_fd_canary_observed_before_closefrom\":%s,"
        "\"failure_report_channel\":\"%s\","
        "\"startup_failure_report_channel\":\"delegated-output-fd-before-or-after-stdio-close\","
        "\"path_arguments_accepted\":false}\n",
        error_code,
        cap_entered ? "true" : "false",
        REMEDIA_INPUT_FD,
        REMEDIA_OUTPUT_FD,
        standard_fds_closed ? "true" : "false",
        standard_fds_closed ? "true" : "false",
        extra_fds_closed_before_cap_enter ? "true" : "false",
        EXTRA_FD_SCAN_LIMIT,
        FD_AFTER_DELEGATED_SET,
        extra_fd_canary_observed_before_closefrom ? "true" : "false",
        failure_channel_for_current_stdio_state());
    if (report_len > 0 && (size_t)report_len < sizeof(report))
        (void)write_all_best_effort(REMEDIA_OUTPUT_FD, report, (size_t)report_len);
    (void)fsync(REMEDIA_OUTPUT_FD);
    _exit(1);
}

static bool
fd_is_closed(int fd)
{
    if (fstat(fd, &(struct stat){0}) == 0)
        return false;
    return errno == EBADF;
}

static void
observe_extra_fd_canary_before_closefrom(void)
{
    extra_fd_canary_observed_before_closefrom = !fd_is_closed(FD_AFTER_DELEGATED_SET);
}

static void
verify_extra_fds_closed_before_cap_enter(void)
{
    for (int fd = FD_AFTER_DELEGATED_SET; fd < EXTRA_FD_SCAN_LIMIT; fd++) {
        if (!fd_is_closed(fd))
            fatal_to_delegated_output("extra_fd_still_open_before_cap_enter", false);
    }
    extra_fds_closed_before_cap_enter = true;
}

static void
verify_delegated_fds_regular(void)
{
    struct stat input_st;
    struct stat output_st;

    if (fstat(REMEDIA_INPUT_FD, &input_st) < 0)
        fatal_to_delegated_output("input_fd_fstat_failed", true);
    if (!S_ISREG(input_st.st_mode))
        fatal_to_delegated_output("input_fd_not_regular", true);

    if (fstat(REMEDIA_OUTPUT_FD, &output_st) < 0)
        fatal_to_delegated_output("output_fd_fstat_failed", true);
    if (!S_ISREG(output_st.st_mode))
        fatal_to_delegated_output("output_fd_not_regular", true);
}

static void
close_standard_fds(void)
{
    int fds[] = { STDIN_FILENO, STDOUT_FILENO, STDERR_FILENO };

    for (size_t i = 0; i < sizeof(fds) / sizeof(fds[0]); i++) {
        if (close(fds[i]) < 0 && errno != EBADF)
            fatal_to_delegated_output("stdio_fd_close_failed", false);
    }
    standard_fds_closed = true;
}

static void
limit_delegated_rights(void)
{
    cap_rights_t input_rights;
    cap_rights_t output_rights;

    if (cap_rights_limit(REMEDIA_INPUT_FD,
        cap_rights_init(&input_rights, CAP_READ, CAP_FSTAT)) < 0)
        fatal_to_delegated_output("input_fd_rights_limit_failed", false);

    if (cap_rights_limit(REMEDIA_OUTPUT_FD,
        cap_rights_init(&output_rights, CAP_WRITE, CAP_FSTAT, CAP_FSYNC)) < 0)
        fatal_to_delegated_output("output_fd_rights_limit_failed", false);
}

int
main(int argc, char **argv)
{
    unsigned char buf[BUFFER_BYTES];
    uintmax_t total = 0;
    struct sha256_ctx input_hash;
    uint8_t input_digest[32];
    char input_sha256[72];
    char report[1408];
    int report_len;

    (void)argv;
    observe_extra_fd_canary_before_closefrom();
    if (argc != 1)
        fatal_to_delegated_output("path_arguments_rejected", false);

    /* Keep only the two broker-delegated fds.  Stdio can otherwise become
     * accidental source-media authority if the launcher is wrong.  Close it
     * before rights limiting as well as before capability mode so later failure
     * reports cannot write to a misdelegated standard descriptor. */
    close_standard_fds();
    closefrom(FD_AFTER_DELEGATED_SET);
    verify_extra_fds_closed_before_cap_enter();
    limit_delegated_rights();

    if (cap_enter() < 0)
        fatal_to_delegated_output("cap_enter_failed", false);

    verify_delegated_fds_regular();
    sha256_init(&input_hash);

    for (;;) {
        ssize_t n = read(REMEDIA_INPUT_FD, buf, sizeof(buf));
        if (n < 0) {
            if (errno == EINTR)
                continue;
            fatal_to_delegated_output("input_fd_read_failed", true);
        }
        if (n == 0)
            break;
        sha256_update(&input_hash, buf, (size_t)n);
        total += (uintmax_t)n;
    }
    sha256_final(&input_hash, input_digest);
    sha256_digest_to_prefixed_hex(input_digest, input_sha256);

    report_len = snprintf(report, sizeof(report),
        "{\"kind\":\"removable.media.local.freebsd.capsicum.worker.report\","
        "\"result\":\"passed\","
        "\"capsicum_mode\":\"entered\","
        "\"capsicum_mode_entered\":true,"
        "\"input_fd\":%d,"
        "\"output_fd\":%d,"
        "\"input_bytes\":%ju,"
        "\"input_sha256\":\"%s\","
        "\"input_fd_regular\":true,"
        "\"output_fd_regular\":true,"
        "\"delegated_fds_regular\":true,"
        "\"stdio_fds_closed_before_cap_enter\":true,"
        "\"stdio_fds_closed_before_report\":true,"
        "\"extra_fds_closed_before_cap_enter\":%s,"
        "\"extra_fd_scan_limit\":%d,"
        "\"extra_fd_canary\":%d,"
        "\"extra_fd_canary_source\":\"broker-nonmedia-canary-not-source-media\","
        "\"extra_fd_canary_observed_before_closefrom\":%s,"
        "\"failure_report_channel\":\"delegated-output-fd-after-stdio-close\","
        "\"startup_failure_report_channel\":\"delegated-output-fd-before-or-after-stdio-close\","
        "\"path_arguments_accepted\":false}\n",
        REMEDIA_INPUT_FD, REMEDIA_OUTPUT_FD, total, input_sha256,
        extra_fds_closed_before_cap_enter ? "true" : "false",
        EXTRA_FD_SCAN_LIMIT,
        FD_AFTER_DELEGATED_SET,
        extra_fd_canary_observed_before_closefrom ? "true" : "false");
    if (report_len < 0 || (size_t)report_len >= sizeof(report))
        fatal_to_delegated_output("worker_report_overflow", true);

    if (!write_all_best_effort(REMEDIA_OUTPUT_FD, report, (size_t)report_len))
        _exit(1);
    if (fsync(REMEDIA_OUTPUT_FD) < 0)
        fatal_to_delegated_output("output_fd_fsync_failed", true);
    return 0;
}
