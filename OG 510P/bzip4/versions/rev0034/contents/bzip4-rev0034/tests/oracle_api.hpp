#pragma once

#include <cstddef>
#include <cstdint>

struct bz3_state;

extern "C" {
std::int8_t oracle_bz3_last_error(bz3_state* state);
const char* oracle_bz3_strerror(bz3_state* state);
bz3_state* oracle_bz3_new(std::int32_t block_size);
void oracle_bz3_free(bz3_state* state);
std::int32_t oracle_bz3_encode_block(
    bz3_state* state, std::uint8_t* buffer, std::int32_t data_size);
std::int32_t oracle_bz3_decode_block(
    bz3_state* state, std::uint8_t* buffer, std::size_t buffer_size,
    std::int32_t compressed_size, std::int32_t original_size);
int oracle_bz3_compress(std::uint32_t block_size, const std::uint8_t* input,
                        std::uint8_t* output, std::size_t input_size,
                        std::size_t* output_size);
int oracle_bz3_decompress(const std::uint8_t* input, std::uint8_t* output,
                          std::size_t input_size, std::size_t* output_size);
std::size_t oracle_bz3_bound(std::size_t input_size);
}
