
/*
 * BZip3 - A spiritual successor to BZip2.
 * Copyright (C) 2022-2024 Kamila Szewczyk
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * bzip4 C++20 translation note:
 * This file originates from bzip3 1.5.3 commit
 * 53984efe378df61a4d3eb41637355c453eec338f. The active translation retains
 * valid upstream encoded bytes while adding C++ allocation casts,
 * warning-clean signedness checks, allocation-before-touch cleanup, defined
 * signed wire serialization, rev0021 malformed-decoder contract hardening,
 * rev0025 borrowed block views for copy-free internal publication,
 * rev0026 checksum fusion plus checked high-level framing, rev0027 shared
 * frame-envelope planning with contracted decoder state selection, rev0028
 * alias-audited entropy addressing plus defined libsais marker transfer, and
 * rev0029 shared low-level envelope parsing, fail-fast entropy truncation,
 * exact inverse-transform terminals, and run-plane APM locality. The untouched
 * C source remains the independently compiled oracle.
 */

#include "bzip4/libbz3.h"
#include "codec_core.hpp"
#include "frame_envelope.hpp"
#include <stdlib.h>
#include <string.h>
#include "libsais.h"

#if defined(BZIP4_POISON_CODEC_WORKSPACE)
static void poison_codec_workspace(void * pointer, size_t bytes, int pattern) {
    memset(pointer, pattern, bytes);
}
#endif

#if defined(__GNUC__) || defined(__clang__)
    #define LIKELY(x)   __builtin_expect(!!(x), 1)
    #define UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
    #define LIKELY(x)   (x)
    #define UNLIKELY(x) (x)
#endif

/* CRC32 implementation. Since CRC32 generally takes less than 1% of the runtime on real-world data (e.g. the
   Silesia corpus), I decided against using hardware CRC32. This implementation is simple, fast, fool-proof and
   good enough to be used with bzip3. */

static const u32 crc32Table[256] = {
    0x00000000L, 0xF26B8303L, 0xE13B70F7L, 0x1350F3F4L, 0xC79A971FL, 0x35F1141CL, 0x26A1E7E8L, 0xD4CA64EBL, 0x8AD958CFL,
    0x78B2DBCCL, 0x6BE22838L, 0x9989AB3BL, 0x4D43CFD0L, 0xBF284CD3L, 0xAC78BF27L, 0x5E133C24L, 0x105EC76FL, 0xE235446CL,
    0xF165B798L, 0x030E349BL, 0xD7C45070L, 0x25AFD373L, 0x36FF2087L, 0xC494A384L, 0x9A879FA0L, 0x68EC1CA3L, 0x7BBCEF57L,
    0x89D76C54L, 0x5D1D08BFL, 0xAF768BBCL, 0xBC267848L, 0x4E4DFB4BL, 0x20BD8EDEL, 0xD2D60DDDL, 0xC186FE29L, 0x33ED7D2AL,
    0xE72719C1L, 0x154C9AC2L, 0x061C6936L, 0xF477EA35L, 0xAA64D611L, 0x580F5512L, 0x4B5FA6E6L, 0xB93425E5L, 0x6DFE410EL,
    0x9F95C20DL, 0x8CC531F9L, 0x7EAEB2FAL, 0x30E349B1L, 0xC288CAB2L, 0xD1D83946L, 0x23B3BA45L, 0xF779DEAEL, 0x05125DADL,
    0x1642AE59L, 0xE4292D5AL, 0xBA3A117EL, 0x4851927DL, 0x5B016189L, 0xA96AE28AL, 0x7DA08661L, 0x8FCB0562L, 0x9C9BF696L,
    0x6EF07595L, 0x417B1DBCL, 0xB3109EBFL, 0xA0406D4BL, 0x522BEE48L, 0x86E18AA3L, 0x748A09A0L, 0x67DAFA54L, 0x95B17957L,
    0xCBA24573L, 0x39C9C670L, 0x2A993584L, 0xD8F2B687L, 0x0C38D26CL, 0xFE53516FL, 0xED03A29BL, 0x1F682198L, 0x5125DAD3L,
    0xA34E59D0L, 0xB01EAA24L, 0x42752927L, 0x96BF4DCCL, 0x64D4CECFL, 0x77843D3BL, 0x85EFBE38L, 0xDBFC821CL, 0x2997011FL,
    0x3AC7F2EBL, 0xC8AC71E8L, 0x1C661503L, 0xEE0D9600L, 0xFD5D65F4L, 0x0F36E6F7L, 0x61C69362L, 0x93AD1061L, 0x80FDE395L,
    0x72966096L, 0xA65C047DL, 0x5437877EL, 0x4767748AL, 0xB50CF789L, 0xEB1FCBADL, 0x197448AEL, 0x0A24BB5AL, 0xF84F3859L,
    0x2C855CB2L, 0xDEEEDFB1L, 0xCDBE2C45L, 0x3FD5AF46L, 0x7198540DL, 0x83F3D70EL, 0x90A324FAL, 0x62C8A7F9L, 0xB602C312L,
    0x44694011L, 0x5739B3E5L, 0xA55230E6L, 0xFB410CC2L, 0x092A8FC1L, 0x1A7A7C35L, 0xE811FF36L, 0x3CDB9BDDL, 0xCEB018DEL,
    0xDDE0EB2AL, 0x2F8B6829L, 0x82F63B78L, 0x709DB87BL, 0x63CD4B8FL, 0x91A6C88CL, 0x456CAC67L, 0xB7072F64L, 0xA457DC90L,
    0x563C5F93L, 0x082F63B7L, 0xFA44E0B4L, 0xE9141340L, 0x1B7F9043L, 0xCFB5F4A8L, 0x3DDE77ABL, 0x2E8E845FL, 0xDCE5075CL,
    0x92A8FC17L, 0x60C37F14L, 0x73938CE0L, 0x81F80FE3L, 0x55326B08L, 0xA759E80BL, 0xB4091BFFL, 0x466298FCL, 0x1871A4D8L,
    0xEA1A27DBL, 0xF94AD42FL, 0x0B21572CL, 0xDFEB33C7L, 0x2D80B0C4L, 0x3ED04330L, 0xCCBBC033L, 0xA24BB5A6L, 0x502036A5L,
    0x4370C551L, 0xB11B4652L, 0x65D122B9L, 0x97BAA1BAL, 0x84EA524EL, 0x7681D14DL, 0x2892ED69L, 0xDAF96E6AL, 0xC9A99D9EL,
    0x3BC21E9DL, 0xEF087A76L, 0x1D63F975L, 0x0E330A81L, 0xFC588982L, 0xB21572C9L, 0x407EF1CAL, 0x532E023EL, 0xA145813DL,
    0x758FE5D6L, 0x87E466D5L, 0x94B49521L, 0x66DF1622L, 0x38CC2A06L, 0xCAA7A905L, 0xD9F75AF1L, 0x2B9CD9F2L, 0xFF56BD19L,
    0x0D3D3E1AL, 0x1E6DCDEEL, 0xEC064EEDL, 0xC38D26C4L, 0x31E6A5C7L, 0x22B65633L, 0xD0DDD530L, 0x0417B1DBL, 0xF67C32D8L,
    0xE52CC12CL, 0x1747422FL, 0x49547E0BL, 0xBB3FFD08L, 0xA86F0EFCL, 0x5A048DFFL, 0x8ECEE914L, 0x7CA56A17L, 0x6FF599E3L,
    0x9D9E1AE0L, 0xD3D3E1ABL, 0x21B862A8L, 0x32E8915CL, 0xC083125FL, 0x144976B4L, 0xE622F5B7L, 0xF5720643L, 0x07198540L,
    0x590AB964L, 0xAB613A67L, 0xB831C993L, 0x4A5A4A90L, 0x9E902E7BL, 0x6CFBAD78L, 0x7FAB5E8CL, 0x8DC0DD8FL, 0xE330A81AL,
    0x115B2B19L, 0x020BD8EDL, 0xF0605BEEL, 0x24AA3F05L, 0xD6C1BC06L, 0xC5914FF2L, 0x37FACCF1L, 0x69E9F0D5L, 0x9B8273D6L,
    0x88D28022L, 0x7AB90321L, 0xAE7367CAL, 0x5C18E4C9L, 0x4F48173DL, 0xBD23943EL, 0xF36E6F75L, 0x0105EC76L, 0x12551F82L,
    0xE03E9C81L, 0x34F4F86AL, 0xC69F7B69L, 0xD5CF889DL, 0x27A40B9EL, 0x79B737BAL, 0x8BDCB4B9L, 0x988C474DL, 0x6AE7C44EL,
    0xBE2DA0A5L, 0x4C4623A6L, 0x5F16D052L, 0xAD7D5351L
};

static inline u32 crc32_update_byte(u32 crc, u8 value) {
    return crc32Table[((u8)crc ^ value) & 0xff] ^ (crc >> 8);
}

static u32 crc32sum(u32 crc, const u8 * RESTRICT buf, size_t size) {
    while (size--) crc = crc32_update_byte(crc, *(buf++));
    return crc;
}

/* LZP code. These constants were manually tuned to give the best compression ratio while using relatively
   little resources. The LZP dictionary is only around 1MiB in size and the minimum match length was chosen
   so that LZP would not interfere too much with the Burrows-Wheeler transform and the arithmetic coder, and
   just collapse long redundant data instead (for a major speed-up at a low compression ratio cost - in fact,
   LZP preprocessing often improves compression in some cases). */

/* A heavily modified version of libbsc's LZP predictor w/ unaligned accesses follows. This one has single thread
   performance and provides better compression ratio. It is also mostly UB-free and less brittle during
   AFL fuzzing. */

#define LZP_DICTIONARY 18
#define LZP_MIN_MATCH 40

#define MATCH 0xf2

static u32 lzp_upcast(const u8 * ptr) {
    // val = *(u32 *)ptr; - written this way to avoid UB
    u32 val;
    memcpy(&val, ptr, sizeof(val));
    return val;
}

/**
 * @brief Check if the buffer size is sufficient for decoding a bz3 block
 * 
 * Data passed to the last step can be one of the following:
 * - original data
 * - original data + LZP
 * - original data + RLE
 * - original data + RLE + LZP
 *
 * We must ensure `buffer_size` is large enough to store the data at every step 
 * when walking backwards. The required size may be stored in  either `lzp_size`,
 * `rle_size` OR `orig_size`.
 *
 * @param buffer_size Size of the output buffer
 * @param lzp_size Size after LZP decompression (-1 if LZP not used)
 * @param rle_size Size after RLE decompression (-1 if RLE not used) 
 * @return 1 if buffer size is sufficient, 0 otherwise
 */
static int bz3_check_buffer_size(size_t buffer_size, s32 lzp_size, s32 rle_size, s32 orig_size) {
    // Handle -1 cases to avoid implicit conversion issues
    size_t effective_lzp_size = lzp_size < 0 ? 0 : (size_t)lzp_size;
    size_t effective_rle_size = rle_size < 0 ? 0 : (size_t)rle_size;
    size_t effective_orig_size = orig_size < 0 ? 0 : (size_t)orig_size;

    // Check if buffer can hold intermediate results
    return (effective_lzp_size <= buffer_size) && (effective_rle_size <= buffer_size) && (effective_orig_size <= buffer_size);
}

static s32 lzp_encode_block(const u8 * RESTRICT in, const u8 * in_end, u8 * RESTRICT out, u8 * out_end,
                            s32 * RESTRICT lut) {
    const u8 * ins = in;
    const u8 * outs = out;
    const u8 * out_eob = out_end - 8;
    const u8 * heur = in;

    u32 ctx;

    for (s32 i = 0; i < 4; ++i) *out++ = *in++;

    ctx = ((u32)in[-1]) | (((u32)in[-2]) << 8) | (((u32)in[-3]) << 16) | (((u32)in[-4]) << 24);

    while (in < in_end - LZP_MIN_MATCH - 32 && out < out_eob) {
        u32 idx = (ctx >> 15 ^ ctx ^ ctx >> 3) & ((s32)(1 << LZP_DICTIONARY) - 1);
        s32 val = lut[idx];
        lut[idx] = in - ins;
        if (val > 0) {
            const u8 * RESTRICT ref = ins + val;
            if (memcmp(in + LZP_MIN_MATCH - 4, ref + LZP_MIN_MATCH - 4, sizeof(u32)) == 0 &&
                memcmp(in, ref, sizeof(u32)) == 0) {
                if (heur > in && lzp_upcast(heur) != lzp_upcast(ref + (heur - in))) goto not_found;

                s32 len = 4;
                for (; in + len < in_end - LZP_MIN_MATCH - 32; len += sizeof(u32)) {
                    if (lzp_upcast(in + len) != lzp_upcast(ref + len)) break;
                }

                if (len < LZP_MIN_MATCH) {
                    if (heur < in + len) heur = in + len;
                    goto not_found;
                }

                len += in[len] == ref[len];
                len += in[len] == ref[len];
                len += in[len] == ref[len];

                in += len;
                ctx = ((u32)in[-1]) | (((u32)in[-2]) << 8) | (((u32)in[-3]) << 16) | (((u32)in[-4]) << 24);

                *out++ = MATCH;

                len -= LZP_MIN_MATCH;
                while (len >= 254) {
                    len -= 254;
                    *out++ = 254;
                    if (out >= out_eob) break;
                }

                *out++ = len;
            } else {
            not_found:;
                u8 next = *out++ = *in++;
                ctx = ctx << 8 | next;
                if (next == MATCH) *out++ = 255;
            }
        } else {
            ctx = (ctx << 8) | (*out++ = *in++);
        }
    }

    ctx = ((u32)in[-1]) | (((u32)in[-2]) << 8) | (((u32)in[-3]) << 16) | (((u32)in[-4]) << 24);

    while (in < in_end && out < out_eob) {
        u32 idx = (ctx >> 15 ^ ctx ^ ctx >> 3) & ((s32)(1 << LZP_DICTIONARY) - 1);
        s32 val = lut[idx];
        lut[idx] = (s32)(in - ins);

        u8 next = *out++ = *in++;
        ctx = ctx << 8 | next;
        if (next == MATCH && val > 0) *out++ = 255;
    }

    return out >= out_eob ? -1 : (s32)(out - outs);
}

template <bool TrackCrc>
static s32 lzp_decode_block(
    const u8 * RESTRICT in,
    const u8 * in_end,
    s32 * RESTRICT lut,
    u8 * RESTRICT out,
    size_t expected_size,
    u32 * RESTRICT crc) {
    if (expected_size < 4 || expected_size > static_cast<size_t>(INT32_MAX)) return -1;

    u8 * const outs = out;
    u8 * const out_end = out + expected_size;

    for (s32 i = 0; i < 4; ++i) {
        if (UNLIKELY(in == in_end)) return -1;
        const u8 value = *in++;
        *out++ = value;
        if constexpr (TrackCrc) *crc = crc32_update_byte(*crc, value);
    }

    u32 ctx = ((u32)out[-1]) | (((u32)out[-2]) << 8) |
              (((u32)out[-3]) << 16) | (((u32)out[-4]) << 24);

    while (in < in_end) {
        if (UNLIKELY(out == out_end)) return -1;

        const u32 idx = (ctx >> 15 ^ ctx ^ ctx >> 3) &
            ((s32)(1 << LZP_DICTIONARY) - 1);
        const s32 val = lut[idx];
        const size_t produced = static_cast<size_t>(out - outs);
        lut[idx] = static_cast<s32>(produced);

        if (*in == MATCH && val > 0) {
            ++in;
            if (UNLIKELY(in == in_end)) return -1;
            if (*in != 255) {
                const size_t remaining = static_cast<size_t>(out_end - out);
                size_t len = LZP_MIN_MATCH;
                if (UNLIKELY(len > remaining)) return -1;
                while (true) {
                    if (UNLIKELY(in == in_end)) return -1;
                    const u8 component = *in++;
                    if (UNLIKELY(component == 255 ||
                                 static_cast<size_t>(component) > remaining - len)) {
                        return -1;
                    }
                    len += component;
                    if (component != 254) break;
                }

                const size_t reference_offset = static_cast<size_t>(val);
                if (UNLIKELY(reference_offset >= produced)) return -1;
                const u8 * ref = outs + reference_offset;
                u8 * const match_end = out + len;
                while (out < match_end) {
                    const u8 value = *ref++;
                    *out++ = value;
                    if constexpr (TrackCrc) *crc = crc32_update_byte(*crc, value);
                }

                ctx = ((u32)out[-1]) | (((u32)out[-2]) << 8) |
                      (((u32)out[-3]) << 16) | (((u32)out[-4]) << 24);
            } else {
                ++in;
                *out++ = MATCH;
                if constexpr (TrackCrc) *crc = crc32_update_byte(*crc, MATCH);
                ctx = (ctx << 8) | MATCH;
            }
        } else {
            const u8 value = *in++;
            *out++ = value;
            if constexpr (TrackCrc) *crc = crc32_update_byte(*crc, value);
            ctx = (ctx << 8) | value;
        }
    }

    return out == out_end ? static_cast<s32>(expected_size) : -1;
}

static s32 lzp_compress(const u8 * RESTRICT in, u8 * RESTRICT out, s32 n, s32 * RESTRICT lut) {
    if (n < LZP_MIN_MATCH + 32) return -1;

    memset(lut, 0, sizeof(s32) * (1 << LZP_DICTIONARY));

    return lzp_encode_block(in, in + n, out, out + n, lut);
}

static s32 lzp_decompress(
    const u8 * RESTRICT in,
    u8 * RESTRICT out,
    s32 n,
    s32 expected,
    s32 * RESTRICT lut,
    u32 * RESTRICT crc_out) {
    if (n < 4 || expected < 4) return -1;

    memset(lut, 0, sizeof(s32) * (1 << LZP_DICTIONARY));

    if (crc_out != NULL) {
        u32 crc = 1;
        const s32 result = lzp_decode_block<true>(
            in, in + n, lut, out, static_cast<size_t>(expected), &crc);
        if (result >= 0) *crc_out = crc;
        return result;
    }
    return lzp_decode_block<false>(
        in, in + n, lut, out, static_cast<size_t>(expected), NULL);
}

int bzip4::detail::bz3_decode_lzp_exact(
    std::span<const std::uint8_t> input,
    std::span<std::uint8_t> output,
    std::span<std::int32_t> dictionary,
    std::uint32_t * crc) noexcept {
    constexpr size_t dictionary_entries = static_cast<size_t>(1) << LZP_DICTIONARY;
    if (input.size() > static_cast<size_t>(INT32_MAX) ||
        output.size() > static_cast<size_t>(INT32_MAX) ||
        dictionary.size() < dictionary_entries) {
        return BZ3_ERR_INIT;
    }
    const s32 result = lzp_decompress(
        input.data(), output.data(), static_cast<s32>(input.size()),
        static_cast<s32>(output.size()), dictionary.data(), crc);
    return result == static_cast<s32>(output.size())
        ? BZ3_OK : BZ3_ERR_MALFORMED_HEADER;
}

/* RLE code. Unlike RLE in other compressors, we collapse all runs if they yield a net gain
   for a given character and encode this as a set bit in the RLE metadata. This improves the
   performance and reduces the amount of collapsing done in normal blocks (so that BWT+AC can
   be more efficient) while we still filter out all the pathological data. */

typedef struct {
    s32 size;
    u32 crc;
} mrle_encode_result;

static mrle_encode_result mrlec_with_crc(const u8 * in, s32 inlen, u8 * out) {
    const u8 * ip = in;
    const u8 * in_end = in + inlen;
    s32 op = 0;
    s32 c, pc = -1;
    s32 t[256] = { 0 };
    s32 run = 0;
    u32 crc = 1;
    while (ip < in_end) {
        c = *ip++;
        crc = crc32_update_byte(crc, (u8)c);
        if (c == pc)
            t[c] += (++run % 255) != 0;
        else
            --t[c], run = 0;
        pc = c;
    }
    for (s32 i = 0; i < 32; ++i) {
        c = 0;
        for (s32 j = 0; j < 8; ++j) c += (t[i * 8 + j] > 0) << j;
        out[op++] = c;
    }
    ip = in;
    c = pc = -1;
    run = 0;
    do {
        c = ip < in_end ? *ip++ : -1;
        if (c == pc)
            ++run;
        else if (run > 0 && t[pc] > 0) {
            out[op++] = pc;
            for (; run > 255; run -= 255) out[op++] = 255;
            out[op++] = run - 1;
            run = 1;
        } else
            for (++run; run > 1; --run) out[op++] = pc;
        pc = c;
    } while (c != -1);

    return {op, crc};
}

static int mrled_with_crc(
    const u8 * RESTRICT in,
    u8 * RESTRICT out,
    s32 outlen,
    s32 maxin,
    u32 * RESTRICT crc_out) {
    if (outlen < 0 || maxin < 32 || crc_out == NULL) return 1;

    const size_t output_size = static_cast<size_t>(outlen);
    const size_t input_size = static_cast<size_t>(maxin);
    size_t op = 0;
    size_t ip = 0;
    s32 selected[256] = { 0 };
    u32 crc = 1;

    for (s32 i = 0; i < 32; ++i) {
        const u8 flags = in[ip++];
        for (s32 j = 0; j < 8; ++j) {
            selected[i * 8 + j] = (flags >> j) & 1;
        }
    }

    while (op < output_size) {
        if (UNLIKELY(ip == input_size)) return 1;
        const u8 value = in[ip++];
        size_t count = 1;

        if (selected[value]) {
            count = 0;
            const size_t remaining = output_size - op;
            bool terminated = false;
            while (ip < input_size) {
                const u8 component = in[ip++];
                const size_t addition = component == 255
                    ? 255U : static_cast<size_t>(component) + 1U;
                if (UNLIKELY(addition > remaining - count)) return 1;
                count += addition;
                if (component != 255) {
                    terminated = true;
                    break;
                }
            }
            if (UNLIKELY(!terminated || count == 0)) return 1;
        }

        for (size_t written = 0; written < count; ++written) {
            out[op++] = value;
            crc = crc32_update_byte(crc, value);
        }
    }

    if (UNLIKELY(ip != input_size)) return 1;
    *crc_out = crc;
    return 0;
}

int bzip4::detail::bz3_decode_mrle_exact(
    std::span<const std::uint8_t> input,
    std::span<std::uint8_t> output,
    std::uint32_t * crc) noexcept {
    if (input.size() > static_cast<size_t>(INT32_MAX) ||
        output.size() > static_cast<size_t>(INT32_MAX)) {
        return BZ3_ERR_INIT;
    }
    std::uint32_t ignored_crc = 1;
    return mrled_with_crc(
        input.data(), output.data(), static_cast<s32>(output.size()),
        static_cast<s32>(input.size()), crc != nullptr ? crc : &ignored_crc) == 0
        ? BZ3_OK : BZ3_ERR_MALFORMED_HEADER;
}


/* The entropy coder. Uses an arithmetic coder implementation outlined in Matt Mahoney's DCE. */

typedef struct {
    /* Input/output. */
    u8 *in_queue, *out_queue;
    s32 input_ptr, output_ptr, input_max;
    s32 decoded_symbols;
    int input_underflow;

    /* C0, C1 - used for making the initial prediction, C2 used for an APM with a slightly low
       learning rate (6) and 512 contexts. kanzi merges C0 and C1, uses slightly different
       counter initialisation code and prediction code which from my tests tends to be suboptimal. */
    // Group APM rows by the run-context selector. One selector is fixed for
    // all eight bit decisions of a symbol, so its 8.5 KiB plane is contiguous
    // instead of interleaved with the inactive plane at a 68-byte row stride.
    u16 C0[256], C1[256][256], C2[2][256][17];
} state;

#define update0(p, x) (p) = ((p) - ((p) >> x))
#define update1(p, x) (p) = ((p) + (((p) ^ 65535) >> x))

static void begin(state * s) {
    prefetch(s);
    for (int i = 0; i < 256; i++) s->C0[i] = 1 << 15;
    for (int i = 0; i < 256; i++)
        for (int j = 0; j < 256; j++) s->C1[i][j] = 1 << 15;
    for (int f = 0; f < 2; ++f)
        for (int ctx = 0; ctx < 256; ++ctx)
            for (int k = 0; k < 17; ++k)
                s->C2[f][ctx][k] = (k << 12) - (k == 16);
}

static void encode_bytes(state * s, u8 * buf, s32 size) {
    /* Keep the output cursor and the two active order-1 rows local to the
       symbol loop. This preserves the exact model update sequence and bytes. */
    u32 high = 0xFFFFFFFF, low = 0, c1 = 0, c2 = 0, run = 0;
    u8 * output = s->out_queue;

    for (s32 i = 0; i < size; i++) {
        u8 c = buf[i];

        if (c1 == c2)
            ++run;
        else
            run = 0;

        const int f = run > 2;
        u16 * const current_order1 = s->C1[c1];
        const u16 * const prior_order1 = s->C1[c2];
        int ctx = 1;

        while (ctx < 256) {
            // The current and prior rows intentionally can alias when the two
            // preceding symbols are equal. Capture all prediction inputs before
            // mutating the current row.
            u16& p0_state = s->C0[ctx];
            u16& p1_state = current_order1[ctx];
            const int p0 = p0_state;
            const int p1 = p1_state;
            const int p2 = prior_order1[ctx];
            const int p = ((p0 + p1) * 7 + p2 + p2) >> 4;

            const int j = p >> 12;
            u16 * const apm = s->C2[f][ctx] + j;
            const int x1 = apm[0];
            const int x2 = apm[1];
            const int ssep = x1 + (((x2 - x1) * (p & 4095)) >> 12);

            if (c & 128) {
                high = low + (((u64)(high - low) * (ssep * 3 + p)) >> 18);

                while ((low ^ high) < (1U << 24)) {
                    *output++ = static_cast<u8>(low >> 24);
                    low <<= 8;
                    high = (high << 8) + 0xFF;
                }

                update1(p0_state, 2);
                update1(p1_state, 4);
                update1(apm[0], 6);
                update1(apm[1], 6);
                ctx += ctx + 1;
            } else {
                low += (((u64)(high - low) * (ssep * 3 + p)) >> 18) + 1;

                while ((low ^ high) < (1U << 24)) {
                    *output++ = static_cast<u8>(low >> 24);
                    low <<= 8;
                    high = (high << 8) + 0xFF;
                }

                update0(p0_state, 2);
                update0(p1_state, 4);
                update0(apm[0], 6);
                update0(apm[1], 6);
                ctx += ctx;
            }

            c <<= 1;
        }

        c2 = c1;
        c1 = static_cast<u32>(ctx & 255);
    }

    *output++ = static_cast<u8>(low >> 24);
    low <<= 8;
    *output++ = static_cast<u8>(low >> 24);
    low <<= 8;
    *output++ = static_cast<u8>(low >> 24);
    low <<= 8;
    *output++ = static_cast<u8>(low >> 24);
    s->output_ptr = static_cast<s32>(output - s->out_queue);
}

static int decode_bytes(state * s, u8 * c, s32 size) {
    u32 high = 0xFFFFFFFF, low = 0, c1 = 0, c2 = 0, run = 0, code = 0;
    const u8 * input = s->in_queue;
    const u8 * const input_end = input + s->input_max;

    s->input_ptr = 0;
    s->decoded_symbols = 0;
    s->input_underflow = 0;
    if (input_end - input < 4) {
        s->input_underflow = 1;
        return 0;
    }

    code = (code << 8) | *input++;
    code = (code << 8) | *input++;
    code = (code << 8) | *input++;
    code = (code << 8) | *input++;

    for (s32 i = 0; i < size; i++) {
        if (c1 == c2)
            ++run;
        else
            run = 0;

        const int f = run > 2;
        u16 * const current_order1 = s->C1[c1];
        const u16 * const prior_order1 = s->C1[c2];
        int ctx = 1;

        while (ctx < 256) {
            // Mirror the encoder's alias-safe read/update order exactly.
            u16& p0_state = s->C0[ctx];
            u16& p1_state = current_order1[ctx];
            const int p0 = p0_state;
            const int p1 = p1_state;
            const int p2 = prior_order1[ctx];
            const int p = ((p0 + p1) * 7 + p2 + p2) >> 4;

            const int j = p >> 12;
            u16 * const apm = s->C2[f][ctx] + j;
            const int x1 = apm[0];
            const int x2 = apm[1];
            const int ssep = x1 + (((x2 - x1) * (p & 4095)) >> 12);

            const u32 mid = low + (((u64)(high - low) * (ssep * 3 + p)) >> 18);
            const u8 bit = static_cast<u8>(code <= mid);
            if (bit)
                high = mid;
            else
                low = mid + 1;
            while ((low ^ high) < (1U << 24)) {
                if (input == input_end) {
                    s->input_ptr = static_cast<s32>(input - s->in_queue);
                    s->input_underflow = 1;
                    return 0;
                }
                low <<= 8;
                high = (high << 8) + 255;
                code = (code << 8) | *input++;
            }

            if (bit) {
                update1(p0_state, 2);
                update1(p1_state, 4);
                update1(apm[0], 6);
                update1(apm[1], 6);
                ctx += ctx + 1;
            } else {
                update0(p0_state, 2);
                update0(p1_state, 4);
                update0(apm[0], 6);
                update0(apm[1], 6);
                ctx += ctx;
            }
        }

        c2 = c1;
        c[i] = static_cast<u8>(ctx & 255);
        c1 = c[i];
        s->decoded_symbols = i + 1;
    }

    s->input_ptr = static_cast<s32>(input - s->in_queue);
    return 1;
}

/* Public API. */

struct bz3_state {
    u8 * swap_buffer;
    s32 block_size;
    s32 *sais_array, *lzp_lut;
    state * cm_state;
    s8 last_error;
};

BZIP3_API s8 bz3_last_error(struct bz3_state * state) {
    return state == NULL ? static_cast<s8>(BZ3_ERR_INIT) : state->last_error;
}

bzip4::detail::Bz3EntropyDecodeStats bzip4::detail::bz3_entropy_decode_stats(
    const bz3_state * state) noexcept {
    if (state == NULL || state->cm_state == NULL) return {};
    return {
        state->cm_state->input_ptr,
        state->cm_state->decoded_symbols,
        state->cm_state->input_underflow != 0,
    };
}

BZIP3_API const char * bz3_version(void) { return VERSION; }

BZIP3_API size_t bz3_bound(size_t input_size) {
    const size_t expansion = input_size / 50;
    if (input_size > SIZE_MAX - expansion) return SIZE_MAX;
    const size_t subtotal = input_size + expansion;
    if (subtotal > SIZE_MAX - 32) return SIZE_MAX;
    return subtotal + 32;
}

static int select_high_level_block_size(u32 requested, size_t input_size, u32 * result) {
    size_t effective = requested;
    if (effective > input_size) {
        effective = bz3_bound(input_size);
        if (effective == SIZE_MAX) return 0;
    }
    if (effective < KiB(65)) effective = KiB(65);
    if (effective > MiB(511) || effective > static_cast<size_t>(INT32_MAX)) return 0;
    *result = static_cast<u32>(effective);
    return 1;
}

static int checked_size_add(size_t left, size_t right, size_t * result) {
    if (right > SIZE_MAX - left) return 0;
    *result = left + right;
    return 1;
}

static int checked_size_mul(size_t left, size_t right, size_t * result) {
    if (left != 0 && right > SIZE_MAX / left) return 0;
    *result = left * right;
    return 1;
}

BZIP3_API size_t bz3_frame_bound(u32 block_size, size_t input_size) {
    u32 effective = 0;
    if (!select_high_level_block_size(block_size, input_size, &effective)) return 0;

    const size_t block_count = input_size == 0 ? 0 : 1 + (input_size - 1) / effective;
    if (block_count > UINT32_MAX) return 0;

    const size_t full_blocks = input_size / effective;
    const size_t remainder = input_size % effective;
    const size_t full_bound = bz3_bound(effective);
    size_t full_record = 0;
    size_t full_records = 0;
    size_t total = 13;
    if (full_bound == SIZE_MAX ||
        !checked_size_add(8, full_bound, &full_record) ||
        !checked_size_mul(full_blocks, full_record, &full_records) ||
        !checked_size_add(total, full_records, &total)) {
        return 0;
    }
    if (remainder != 0) {
        const size_t remainder_bound = bz3_bound(remainder);
        size_t remainder_record = 0;
        if (remainder_bound == SIZE_MAX ||
            !checked_size_add(8, remainder_bound, &remainder_record) ||
            !checked_size_add(total, remainder_record, &total)) {
            return 0;
        }
    }
    return total;
}

BZIP3_API const char * bz3_strerror(struct bz3_state * state) {
    if (state == NULL) return "Invalid or null codec state";
    switch (state->last_error) {
        case BZ3_OK:
            return "No error";
        case BZ3_ERR_OUT_OF_BOUNDS:
            return "Data index out of bounds";
        case BZ3_ERR_BWT:
            return "Burrows-Wheeler transform failed";
        case BZ3_ERR_CRC:
            return "CRC32 check failed";
        case BZ3_ERR_MALFORMED_HEADER:
            return "Malformed header";
        case BZ3_ERR_TRUNCATED_DATA:
            return "Truncated data";
        case BZ3_ERR_DATA_TOO_BIG:
            return "Too much data";
        case BZ3_ERR_INIT:
            return "Initialization failed or an argument was invalid";
        case BZ3_ERR_DATA_SIZE_TOO_SMALL:
            return "Size of buffer `buffer_size` passed to the block decoder (bz3_decode_block) is too small. See function docs for details.";
        default:
            return "Unknown error";
    }
}

BZIP3_API struct bz3_state * bz3_new(s32 block_size) {
    if (block_size < KiB(65) || block_size > MiB(511)) {
        return NULL;
    }

    struct bz3_state * bz3_state = static_cast<struct bz3_state *>(malloc(sizeof(struct bz3_state)));

    if (!bz3_state) {
        return NULL;
    }

    bz3_state->cm_state = static_cast<state *>(malloc(sizeof(state)));

    bz3_state->swap_buffer = static_cast<u8 *>(malloc(bz3_bound(block_size)));
    bz3_state->sais_array = static_cast<s32 *>(malloc(BWT_BOUND(block_size) * sizeof(s32)));
    bz3_state->lzp_lut = static_cast<s32 *>(calloc(1 << LZP_DICTIONARY, sizeof(s32)));

    if (!bz3_state->cm_state || !bz3_state->swap_buffer || !bz3_state->sais_array || !bz3_state->lzp_lut) {
        if (bz3_state->cm_state) free(bz3_state->cm_state);
        if (bz3_state->swap_buffer) free(bz3_state->swap_buffer);
        if (bz3_state->sais_array) free(bz3_state->sais_array);
        if (bz3_state->lzp_lut) free(bz3_state->lzp_lut);
        free(bz3_state);
        return NULL;
    }

#if defined(BZIP4_POISON_CODEC_WORKSPACE)
    poison_codec_workspace(bz3_state->swap_buffer, bz3_bound(block_size), 0xa5);
    poison_codec_workspace(
        bz3_state->sais_array, sizeof(s32) * BWT_BOUND(block_size), 0x5a);
#endif
    bz3_state->block_size = block_size;
    bz3_state->cm_state->in_queue = NULL;
    bz3_state->cm_state->out_queue = NULL;
    bz3_state->cm_state->input_ptr = 0;
    bz3_state->cm_state->output_ptr = 0;
    bz3_state->cm_state->input_max = 0;
    bz3_state->cm_state->decoded_symbols = 0;
    bz3_state->cm_state->input_underflow = 0;

    bz3_state->last_error = BZ3_OK;

    return bz3_state;
}

BZIP3_API void bz3_free(struct bz3_state * state) {
    if (!state) return;
    free(state->swap_buffer);
    free(state->sais_array);
    free(state->cm_state);
    free(state->lzp_lut);
    free(state);
}

#define swap(x, y)    \
    {                 \
        u8 * tmp = x; \
        x = y;        \
        y = tmp;      \
    }

static bzip4::detail::Bz3BlockView bz3_encode_block_core(
    struct bz3_state * state, u8 * buffer, s32 data_size) {
    if (state == NULL) return {buffer, -1};
    if (buffer == NULL) {
        state->last_error = BZ3_ERR_INIT;
        return {buffer, -1};
    }
    u8 *b1 = buffer, *b2 = state->swap_buffer;

    if (data_size < 0 || data_size > state->block_size) {
        state->last_error = BZ3_ERR_DATA_TOO_BIG;
        return {buffer, -1};
    }

    // Ignore small blocks. They won't benefit from the entropy coding step.
    if (data_size < 64) {
        const u32 crc32 = crc32sum(1, b1, static_cast<size_t>(data_size));
        memmove(b1 + 8, b1, data_size);
        write_neutral_s32(b1, crc32);
        write_neutral_s32(b1 + 4, -1);
        state->last_error = BZ3_OK;
        return {b1, data_size + 8};
    }

    // Back to front:
    // bit 1: lzp | no lzp
    // bit 2: srt | no srt
    s8 model = 0;
    s32 lzp_size, rle_size;

    const mrle_encode_result rle = mrlec_with_crc(b1, data_size, b2);
    const u32 crc32 = rle.crc;
    rle_size = rle.size;
    if (rle_size < data_size) {
        swap(b1, b2);
        data_size = rle_size;
        model |= 4;
    }

    lzp_size = lzp_compress(b1, b2, data_size, state->lzp_lut);
    if (lzp_size > 0 && lzp_size < data_size) {
        swap(b1, b2);
        data_size = lzp_size;
        model |= 2;
    }

#if defined(BZIP4_POISON_CODEC_WORKSPACE)
    poison_codec_workspace(
        state->sais_array, sizeof(s32) * BWT_BOUND(state->block_size), 0x3c);
#endif
    s32 bwt_idx = libsais_bwt(b1, b2, state->sais_array, data_size, 0, NULL);
    if (bwt_idx < 0) {
        state->last_error = BZ3_ERR_BWT;
        return {buffer, -1};
    }

    // Compute the amount of overhead dwords.
    s32 overhead = 2;           // CRC32 + BWT index
    if (model & 2) overhead++;  // LZP
    if (model & 4) overhead++;  // RLE

    begin(state->cm_state);
    state->cm_state->out_queue = b1 + overhead * 4 + 1;
    state->cm_state->output_ptr = 0;
    encode_bytes(state->cm_state, b2, data_size);
    data_size = state->cm_state->output_ptr;

    // Write the header. Starting with common entries.
    write_neutral_s32(b1, crc32);
    write_neutral_s32(b1 + 4, bwt_idx);
    b1[8] = model;

    s32 p = 0;
    if (model & 2) write_neutral_s32(b1 + 9 + 4 * p++, lzp_size);
    if (model & 4) write_neutral_s32(b1 + 9 + 4 * p++, rle_size);

    state->last_error = BZ3_OK;
    return {b1, data_size + overhead * 4 + 1};
}

bzip4::detail::Bz3BlockView bzip4::detail::bz3_encode_block_view(
    bz3_state * state, std::uint8_t * buffer, std::int32_t size) noexcept {
    return bz3_encode_block_core(state, buffer, size);
}

BZIP3_API s32 bz3_encode_block(struct bz3_state * state, u8 * buffer, s32 data_size) {
    const bzip4::detail::Bz3BlockView result =
        bzip4::detail::bz3_encode_block_view(state, buffer, data_size);
    if (result.size >= 0 && result.data != buffer) {
        memcpy(buffer, result.data, static_cast<size_t>(result.size));
    }
    return result.size;
}

static bzip4::detail::Bz3BlockView bz3_decode_block_core(
    struct bz3_state * state, u8 * buffer, size_t buffer_size,
    s32 compressed_size, s32 orig_size) {
    if (state == NULL) return {buffer, -1};
    state->cm_state->input_ptr = 0;
    state->cm_state->decoded_symbols = 0;
    state->cm_state->input_underflow = 0;
    if (buffer == NULL) {
        state->last_error = BZ3_ERR_INIT;
        return {buffer, -1};
    }
    if (compressed_size < 0 || orig_size < 0) {
        state->last_error = BZ3_ERR_MALFORMED_HEADER;
        return {buffer, -1};
    }

    const size_t encoded_size = static_cast<size_t>(compressed_size);
    if (encoded_size > buffer_size) {
        state->last_error = BZ3_ERR_DATA_SIZE_TOO_SMALL;
        return {buffer, -1};
    }

    const size_t prefix_size = encoded_size < 17U ? encoded_size : 17U;
    const bzip4::detail::BlockEnvelopeValidation validation =
        bzip4::detail::validate_block_envelope(
            encoded_size,
            std::span<const std::uint8_t>(buffer, prefix_size),
            static_cast<size_t>(orig_size),
            static_cast<u32>(state->block_size));
    if (validation.error_code != BZ3_OK) {
        state->last_error = static_cast<s8>(validation.error_code);
        return {buffer, -1};
    }
    const bzip4::detail::BlockEnvelope& envelope = validation.envelope;
    const u32 crc32 = read_neutral_u32(buffer);

    if (envelope.raw) {
        const size_t literal_size = static_cast<size_t>(orig_size);
        if (literal_size > buffer_size) {
            state->last_error = BZ3_ERR_DATA_SIZE_TOO_SMALL;
            return {buffer, -1};
        }

        memmove(buffer, buffer + 8, literal_size);
        if (crc32sum(1, buffer, static_cast<s32>(literal_size)) != crc32) {
            state->last_error = BZ3_ERR_CRC;
            return {buffer, -1};
        }
        state->last_error = BZ3_OK;
        return {buffer, static_cast<s32>(literal_size)};
    }

    if (!bz3_check_buffer_size(
            buffer_size, envelope.lzp_size, envelope.rle_size, orig_size)) {
        state->last_error = BZ3_ERR_DATA_SIZE_TOO_SMALL;
        return {buffer, -1};
    }

    u8 *b1 = buffer, *b2 = state->swap_buffer;

    begin(state->cm_state);
    state->cm_state->in_queue = b1 + envelope.header_size;
    state->cm_state->input_ptr = 0;
    state->cm_state->input_max = static_cast<s32>(
        encoded_size - envelope.header_size);
    state->cm_state->decoded_symbols = 0;
    state->cm_state->input_underflow = 0;

    if (!decode_bytes(state->cm_state, b2, envelope.size_before_bwt)) {
        state->last_error = BZ3_ERR_TRUNCATED_DATA;
        return {buffer, -1};
    }
    swap(b1, b2);

    // libsais inverse BWT uses a one-based pointer table spanning [1, n]
    // and deliberately leaves the sentinel link as zero. Initialize exactly
    // that active prefix; the allocation tail and output bytes are overwrite-
    // only and need no production clear.
    const size_t unbwt_table_bytes =
        (static_cast<size_t>(envelope.size_before_bwt) + 1U) * sizeof(s32);
#if defined(BZIP4_POISON_CODEC_WORKSPACE)
    poison_codec_workspace(
        state->sais_array, sizeof(s32) * BWT_BOUND(state->block_size), 0xc3);
    poison_codec_workspace(
        b2, static_cast<size_t>(envelope.size_before_bwt), 0x96);
#endif
    memset(state->sais_array, 0, unbwt_table_bytes);
    if (libsais_unbwt(
            b1, b2, state->sais_array, envelope.size_before_bwt,
            NULL, envelope.bwt_index) < 0) {
        state->last_error = BZ3_ERR_BWT;
        return {buffer, -1};
    }
    swap(b1, b2);

    s32 size_src = envelope.size_before_bwt;
    u32 decoded_crc = 1;
    int crc_ready = 0;

    if ((envelope.model & 2U) != 0U) {
        u32 * lzp_crc = (envelope.model & 4U) != 0U ? NULL : &decoded_crc;
        const s32 expected_lzp_output = (envelope.model & 4U) != 0U
            ? envelope.rle_size : orig_size;
        const int lzp_error = bzip4::detail::bz3_decode_lzp_exact(
            std::span<const u8>(
                b1, static_cast<size_t>(envelope.lzp_size)),
            std::span<u8>(
                b2, static_cast<size_t>(expected_lzp_output)),
            std::span<s32>(
                state->lzp_lut,
                static_cast<size_t>(1) << LZP_DICTIONARY),
            lzp_crc);
        if (lzp_error != BZ3_OK) {
            state->last_error = BZ3_ERR_MALFORMED_HEADER;
            return {buffer, -1};
        }
        size_src = expected_lzp_output;
        swap(b1, b2);
        if ((envelope.model & 4U) == 0U) crc_ready = 1;
    }

    if ((envelope.model & 4U) != 0U) {
        const int rle_error = bzip4::detail::bz3_decode_mrle_exact(
            std::span<const u8>(b1, static_cast<size_t>(size_src)),
            std::span<u8>(b2, static_cast<size_t>(orig_size)),
            &decoded_crc);
        if (rle_error != BZ3_OK) {
            state->last_error = BZ3_ERR_MALFORMED_HEADER;
            return {buffer, -1};
        }
        size_src = orig_size;
        swap(b1, b2);
        crc_ready = 1;
    }

    if (size_src != orig_size) {
        state->last_error = BZ3_ERR_MALFORMED_HEADER;
        return {buffer, -1};
    }

    if (!crc_ready) {
        decoded_crc = crc32sum(1, b1, static_cast<size_t>(size_src));
    }
    if (crc32 != decoded_crc) {
        state->last_error = BZ3_ERR_CRC;
        return {buffer, -1};
    }

    state->last_error = BZ3_OK;
    return {b1, size_src};
}

bzip4::detail::Bz3BlockView bzip4::detail::bz3_decode_block_view(
    bz3_state * state, std::uint8_t * buffer, std::size_t buffer_size,
    std::int32_t compressed_size, std::int32_t original_size) noexcept {
    return bz3_decode_block_core(
        state, buffer, buffer_size, compressed_size, original_size);
}

BZIP3_API s32 bz3_decode_block(
    struct bz3_state * state, u8 * buffer, size_t buffer_size,
    s32 compressed_size, s32 orig_size) {
    const bzip4::detail::Bz3BlockView result = bzip4::detail::bz3_decode_block_view(
        state, buffer, buffer_size, compressed_size, orig_size);
    if (result.size >= 0 && result.data != buffer) {
        memcpy(buffer, result.data, static_cast<size_t>(result.size));
    }
    return result.size;
}

#undef swap

#ifdef PTHREAD

    #include <pthread.h>

typedef struct {
    struct bz3_state * state;
    u8 * buffer;
    s32 size;
} encode_thread_msg;

typedef struct {
    struct bz3_state * state;
    u8 * buffer;
    size_t buffer_size;
    s32 size;
    s32 orig_size;
} decode_thread_msg;

static void * bz3_init_encode_thread(void * _msg) {
    encode_thread_msg * msg = _msg;
    msg->size = bz3_encode_block(msg->state, msg->buffer, msg->size);
    pthread_exit(NULL);
    return NULL;  // unreachable
}

static void * bz3_init_decode_thread(void * _msg) {
    decode_thread_msg * msg = _msg;
    bz3_decode_block(msg->state, msg->buffer, msg->buffer_size, msg->size, msg->orig_size);
    pthread_exit(NULL);
    return NULL;  // unreachable
}

BZIP3_API void bz3_encode_blocks(struct bz3_state * states[], u8 * buffers[], s32 sizes[], s32 n) {
    encode_thread_msg messages[n];
    pthread_t threads[n];
    for (s32 i = 0; i < n; i++) {
        messages[i].state = states[i];
        messages[i].buffer = buffers[i];
        messages[i].size = sizes[i];
        pthread_create(&threads[i], NULL, bz3_init_encode_thread, &messages[i]);
    }
    for (s32 i = 0; i < n; i++) pthread_join(threads[i], NULL);
    for (s32 i = 0; i < n; i++) sizes[i] = messages[i].size;
}

BZIP3_API void bz3_decode_blocks(struct bz3_state * states[], u8 * buffers[], size_t buffer_sizes[], s32 sizes[], s32 orig_sizes[], s32 n) {
    decode_thread_msg messages[n];
    pthread_t threads[n];
    for (s32 i = 0; i < n; i++) {
        messages[i].state = states[i];
        messages[i].buffer = buffers[i];
        messages[i].buffer_size = buffer_sizes[i];
        messages[i].size = sizes[i];
        messages[i].orig_size = orig_sizes[i];
        pthread_create(&threads[i], NULL, bz3_init_decode_thread, &messages[i]);
    }
    for (s32 i = 0; i < n; i++) pthread_join(threads[i], NULL);
}

#endif

/* High level API implementations. */

typedef struct {
    u32 declared_block_size;
    u32 workspace_block_size;
    u32 block_count;
    size_t compression_buffer_size;
    size_t decoded_size;
} high_level_frame_plan;

static int preflight_high_level_frame(
    const u8 * in, size_t in_size, size_t output_capacity,
    high_level_frame_plan * plan) {
    plan->declared_block_size = read_neutral_u32(in + 5);
    plan->block_count = read_neutral_u32(in + 9);
    plan->decoded_size = 0;
    if (plan->declared_block_size < KiB(65) ||
        plan->declared_block_size > MiB(511)) {
        return BZ3_ERR_MALFORMED_HEADER;
    }

    const size_t available_after_header = in_size - 13;
    if (static_cast<size_t>(plan->block_count) > available_after_header / 16) {
        return BZ3_ERR_MALFORMED_HEADER;
    }

    const size_t declared_compression_bound = bz3_bound(plan->declared_block_size);
    size_t cursor = 13;
    bzip4::detail::DecoderWorkspaceRequirements workspace_requirements = {};
    for (u32 index = 0; index < plan->block_count; ++index) {
        if (cursor > in_size || in_size - cursor < 8) {
            return BZ3_ERR_TRUNCATED_DATA;
        }
        const s32 compressed_signed = read_neutral_s32(in + cursor);
        const s32 original_signed = read_neutral_s32(in + cursor + 4);
        if (compressed_signed < 0 || original_signed < 0) {
            return BZ3_ERR_MALFORMED_HEADER;
        }
        const size_t compressed = static_cast<size_t>(compressed_signed);
        const size_t original = static_cast<size_t>(original_signed);
        if (compressed > declared_compression_bound ||
            original > plan->declared_block_size) {
            return BZ3_ERR_MALFORMED_HEADER;
        }
        const size_t payload_offset = cursor + 8;
        if (compressed > in_size - payload_offset) return BZ3_ERR_TRUNCATED_DATA;

        const bzip4::detail::BlockEnvelopeValidation envelope =
            bzip4::detail::validate_block_envelope(
                compressed,
                std::span<const std::uint8_t>(in + payload_offset, compressed),
                original, plan->declared_block_size);
        if (envelope.error_code != BZ3_OK) return envelope.error_code;
        bzip4::detail::merge_decoder_requirements(
            workspace_requirements, envelope);

        if (plan->decoded_size > output_capacity ||
            original > output_capacity - plan->decoded_size) {
            return BZ3_ERR_DATA_TOO_BIG;
        }
        plan->decoded_size += original;
        cursor = payload_offset + compressed;
    }

    // The frame declaration is an upper bound. Select the smallest legal
    // state whose direct block limit covers original output and whose bz3_bound
    // covers every payload and transform intermediate. The C++ scanner uses the
    // same requirements and selector.
    plan->workspace_block_size = bzip4::detail::select_decoder_block_size(
        workspace_requirements, plan->declared_block_size);
    if (plan->workspace_block_size == 0) return BZ3_ERR_MALFORMED_HEADER;
    plan->compression_buffer_size = bz3_bound(plan->workspace_block_size);
    return BZ3_OK;
}

BZIP3_API int bz3_compress(u32 block_size, const u8 * const in, u8 * out, size_t in_size, size_t * out_size) {
    if (out_size == NULL) return BZ3_ERR_INIT;
    const size_t buf_max = *out_size;
    *out_size = 0;
    if ((in_size != 0 && in == NULL) || (buf_max != 0 && out == NULL)) return BZ3_ERR_INIT;

    u32 effective_block_size = 0;
    if (!select_high_level_block_size(block_size, in_size, &effective_block_size)) {
        return BZ3_ERR_INIT;
    }
    const size_t block_count = in_size == 0
        ? 0 : 1 + (in_size - 1) / effective_block_size;
    if (block_count > UINT32_MAX) return BZ3_ERR_DATA_TOO_BIG;
    if (buf_max < 13) return BZ3_ERR_DATA_TOO_BIG;

    if (block_count == 0) {
        out[0] = 'B';
        out[1] = 'Z';
        out[2] = '3';
        out[3] = 'v';
        out[4] = '1';
        write_neutral_u32(out + 5, effective_block_size);
        write_neutral_u32(out + 9, 0);
        *out_size = 13;
        return BZ3_OK;
    }

    struct bz3_state * state = bz3_new(static_cast<s32>(effective_block_size));
    if (!state) return BZ3_ERR_INIT;

    const size_t compression_capacity = bz3_bound(effective_block_size);
    u8 * compression_buf = static_cast<u8 *>(malloc(compression_capacity));
    if (!compression_buf) {
        bz3_free(state);
        return BZ3_ERR_INIT;
    }

    out[0] = 'B';
    out[1] = 'Z';
    out[2] = '3';
    out[3] = 'v';
    out[4] = '1';
    write_neutral_u32(out + 5, effective_block_size);
    write_neutral_u32(out + 9, static_cast<u32>(block_count));
    *out_size = 13;

    size_t in_offset = 0;
    while (in_offset < in_size) {
        const size_t remaining = in_size - in_offset;
        const size_t block_bytes = remaining < effective_block_size
            ? remaining : effective_block_size;
        memcpy(compression_buf, in + in_offset, block_bytes);

        const bzip4::detail::Bz3BlockView encoded =
            bzip4::detail::bz3_encode_block_view(
                state, compression_buf, static_cast<s32>(block_bytes));
        const s8 error = bz3_last_error(state);
        if (error != BZ3_OK || encoded.size < 0 || encoded.data == NULL) {
            const s8 result = error == BZ3_OK
                ? static_cast<s8>(BZ3_ERR_OUT_OF_BOUNDS) : error;
            bz3_free(state);
            free(compression_buf);
            return result;
        }

        const size_t encoded_bytes = static_cast<size_t>(encoded.size);
        if (encoded_bytes > compression_capacity || encoded_bytes > bz3_bound(block_bytes) ||
            encoded_bytes > static_cast<size_t>(INT32_MAX)) {
            bz3_free(state);
            free(compression_buf);
            return BZ3_ERR_OUT_OF_BOUNDS;
        }
        size_t record_bytes = 0;
        if (!checked_size_add(8, encoded_bytes, &record_bytes) ||
            *out_size > buf_max || record_bytes > buf_max - *out_size) {
            bz3_free(state);
            free(compression_buf);
            return BZ3_ERR_DATA_TOO_BIG;
        }

        write_neutral_u32(out + *out_size, static_cast<u32>(encoded_bytes));
        write_neutral_u32(out + *out_size + 4, static_cast<u32>(block_bytes));
        memcpy(out + *out_size + 8, encoded.data, encoded_bytes);
        *out_size += record_bytes;
        in_offset += block_bytes;
    }

    bz3_free(state);
    free(compression_buf);
    return BZ3_OK;
}

BZIP3_API int bz3_decompress(const uint8_t * in, uint8_t * out, size_t in_size, size_t * out_size) {
    if (out_size == NULL) return BZ3_ERR_INIT;
    const size_t buf_max = *out_size;
    *out_size = 0;
    if ((in_size != 0 && in == NULL) || (buf_max != 0 && out == NULL)) return BZ3_ERR_INIT;
    if (in_size < 13) return BZ3_ERR_MALFORMED_HEADER;
    if (in[0] != 'B' || in[1] != 'Z' || in[2] != '3' || in[3] != 'v' || in[4] != '1') {
        return BZ3_ERR_MALFORMED_HEADER;
    }

    high_level_frame_plan plan = {};
    const int preflight_error = preflight_high_level_frame(in, in_size, buf_max, &plan);
    if (preflight_error != BZ3_OK) return preflight_error;
    if (plan.block_count == 0) return BZ3_OK;

    in_size -= 13;
    in += 13;

    struct bz3_state * state = bz3_new(static_cast<s32>(plan.workspace_block_size));
    if (!state) return BZ3_ERR_INIT;

    const size_t compression_buf_size = plan.compression_buffer_size;
    u8 * compression_buf = static_cast<u8 *>(malloc(compression_buf_size));
    if (!compression_buf) {
        bz3_free(state);
        return BZ3_ERR_INIT;
    }

    for (u32 i = 0; i < plan.block_count; i++) {
        if (in_size < 8) {
        malformed_header:
            bz3_free(state);
            free(compression_buf);
            return BZ3_ERR_MALFORMED_HEADER;
        }
        const s32 size = read_neutral_s32(in);
        if (size < 0 || static_cast<size_t>(size) > compression_buf_size) goto malformed_header;
        if (static_cast<size_t>(size) > in_size - 8) {
            bz3_free(state);
            free(compression_buf);
            return BZ3_ERR_TRUNCATED_DATA;
        }
        const s32 orig_size = read_neutral_s32(in + 4);
        if (orig_size < 0 || static_cast<u32>(orig_size) > plan.workspace_block_size) {
            goto malformed_header;
        }
        if (*out_size > buf_max || static_cast<size_t>(orig_size) > buf_max - *out_size) {
            bz3_free(state);
            free(compression_buf);
            return BZ3_ERR_DATA_TOO_BIG;
        }
        memcpy(compression_buf, in + 8, static_cast<size_t>(size));
        const bzip4::detail::Bz3BlockView decoded =
            bzip4::detail::bz3_decode_block_view(
                state, compression_buf, compression_buf_size, size, orig_size);
        const s8 error = bz3_last_error(state);
        if (error != BZ3_OK || decoded.size != orig_size || decoded.data == NULL) {
            const s8 result = error == BZ3_OK
                ? static_cast<s8>(BZ3_ERR_MALFORMED_HEADER) : error;
            bz3_free(state);
            free(compression_buf);
            return result;
        }
        if (decoded.size != 0) {
            memcpy(out + *out_size, decoded.data, static_cast<size_t>(decoded.size));
        }
        *out_size += static_cast<size_t>(decoded.size);
        in += static_cast<size_t>(size) + 8;
        in_size -= static_cast<size_t>(size) + 8;
    }

    bz3_free(state);
    free(compression_buf);

    return BZ3_OK;
}

BZIP3_API size_t bz3_min_memory_needed(int32_t block_size) {
    if (block_size < KiB(65) || block_size > MiB(511)) {
        return 0;
    }

    size_t total_size = 0;

    // This is based on bz3_new.
    // Core state structure
    total_size += sizeof(struct bz3_state);

    // cm_state
    total_size += sizeof(state);

    // Swap buffer (needs to handle expanded size) (swap_buffer)
    total_size += bz3_bound(block_size);

    // SAIS array
    total_size += BWT_BOUND(block_size) * sizeof(int32_t);

    // LZP lookup table (lzp_lut)
    total_size += (1 << LZP_DICTIONARY) * sizeof(int32_t);
    return total_size;
}


BZIP3_API int bz3_orig_size_sufficient_for_decode(const u8 * block, size_t block_size, s32 orig_size) {
    if (block == NULL || orig_size < 0 || block_size < 8) return -1;

    const size_t prefix_size = block_size < 17U ? block_size : 17U;
    const bzip4::detail::BlockEnvelopeValidation validation =
        bzip4::detail::validate_block_envelope(
            block_size,
            std::span<const u8>(block, prefix_size),
            static_cast<size_t>(orig_size),
            MiB(511));
    if (validation.error_code != BZ3_OK) return -1;

    // Preserve the historical helper contract for raw blocks: it answers
    // whether transform output needs more than orig_size, not whether the
    // caller already owns enough bytes to hold the encoded input record.
    if (validation.envelope.raw) return 1;

    return bz3_check_buffer_size(
        static_cast<size_t>(orig_size),
        validation.envelope.lzp_size,
        validation.envelope.rle_size,
        orig_size);
}
