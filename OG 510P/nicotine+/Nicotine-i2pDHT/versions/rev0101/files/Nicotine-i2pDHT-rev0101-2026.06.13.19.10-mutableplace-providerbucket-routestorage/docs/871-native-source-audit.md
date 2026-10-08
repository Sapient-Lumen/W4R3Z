# Native source audit

`nativeaudit.py` is a small textual guard for GCC leaf sources. It is not a C verifier and does not pretend to be one. It exists to catch accidental boundary drift: a comparator leaf gaining heap allocation, I/O, network, threading, process, dynamic-loading, or other side-effect-shaped tokens.

The current C leaf is expected to expose:

```text
i2pdht_abi_version
i2pdht_xor_compare
```

The audit rejects dangerous tokens such as `malloc`, `free`, `fopen`, `socket`, `system`, `pthread`, `mmap`, and `dlopen`, rejects missing symbols, and rejects oversized source material. This keeps GCC work in the tiny-leaf category instead of letting it quietly become a second protocol implementation.
