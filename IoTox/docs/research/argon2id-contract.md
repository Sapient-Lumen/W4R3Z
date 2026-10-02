# Argon2id contract research notes

**Accessed:** 2026-08-13  
**Revision:** rev0002

## Primary references

- RFC 9106, *Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications*: https://www.rfc-editor.org/rfc/rfc9106
- Argon2 reference implementation: https://github.com/P-H-C/phc-winner-argon2
- Public Argon2 header/ABI: https://github.com/P-H-C/phc-winner-argon2/blob/master/include/argon2.h
- EFF long word-list explanation: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
- Pinned EFF list: https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt

RFC 9106 describes Argon2 version 1.3 and names Argon2id with 64 MiB, three iterations, four lanes, a 128-bit salt, and a 256-bit tag as its second recommended uniformly safe option for memory-constrained environments. RecallRoot-v1 freezes that parameter set rather than tuning it per machine because cross-implementation reproducibility is the requirement.

## Word-list retention

The archive includes the EFF long list under `third_party/eff_large_wordlist_2016-07-18.txt` with attribution and the CC BY 3.0 legal text.

Recorded properties:

```text
entries: 7776
first:   11111<TAB>abacus
last:    66666<TAB>zoom
sha256:  addd35536511597a02fa0a9ff1e5284677b8883b83e986e43f15a3db996b903e
```

The C++ loader verifies all 7,776 ordered dice codes, unique words, and restricted ASCII syntax. Package checksums additionally retain the exact file digest.

## Known-answer vector

RecallRoot-v1 public test phrase:

```text
abacus abdomen abdominal abide abiding ability ablaze able
```

Expected 32-byte output:

```text
87184eb373901af775366823ef670f4291806d062292ff2b2bff956337df2804
```

The value was independently generated through Python `argon2-cffi` 25.1.0 and reproduced by the C++ runtime adapter using the container's `libargon2.so.1`.

## Implementation shape

IoTox does not implement Argon2. It loads the reference-compatible C ABI through an isolated C++ adapter. When development headers are present, the adapter consumes the official types. Otherwise, one fallback header reproduces only the public `argon2_context` ABI and two consumed function signatures.

The low-level `argon2id_ctx` call is used instead of the high-level raw helper so the algorithm version can be set explicitly to `0x13`. The context requests password-buffer clearing, and IoTox also explicitly wipes its mutable password copy, salt copy, temporary output copy, `RecallPhrase`, and `RecoveryRoot` storage.

This is defense-in-depth, not a guarantee that compilers, allocators, swap, crash dumps, terminal buffers, or callers retain no copies. Production phrase entry needs a dedicated secure-input design and target-specific memory controls.

## Dependency state

rev0002 dynamically exercises the system `libargon2.so.1`; it does not vendor or reproducibly build a pinned Argon2 source release. A production build should pin and package a reviewed implementation while retaining the same RecallRoot-v1 output contract.
