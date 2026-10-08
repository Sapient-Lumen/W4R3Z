#include <stddef.h>
#include <stdint.h>

int i2pdht_abi_version(void) {
    return 1;
}

int i2pdht_xor_compare(const uint8_t *pivot, const uint8_t *left, const uint8_t *right, size_t len) {
    if (pivot == 0 || left == 0 || right == 0 || len == 0) {
        return 0;
    }
    for (size_t i = 0; i < len; i++) {
        uint8_t ld = (uint8_t)(pivot[i] ^ left[i]);
        uint8_t rd = (uint8_t)(pivot[i] ^ right[i]);
        if (ld < rd) {
            return -1;
        }
        if (ld > rd) {
            return 1;
        }
    }
    return 0;
}
