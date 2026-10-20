# Third-party material

## EFF long passphrase word list

File: `eff_large_wordlist_2016-07-18.txt`

Source: Electronic Frontier Foundation, “EFF's New Wordlists for Random Passphrases,”
2016-07-18/19.

- Article: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
- Original list: https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt
- SHA-256: `addd35536511597a02fa0a9ff1e5284677b8883b83e986e43f15a3db996b903e`

The EFF page is published under Creative Commons Attribution. The archive includes the CC BY
3.0 legal text at `third_party/LICENSES/CC-BY-3.0.txt`.

The list is retained unmodified. IoTox code and documentation identify the source and do not
imply EFF endorsement of IoTox or RecallRoot-v1. `embedded_wordlist.cpp` is generated from the
same exact bytes in bounded C++ literals so strict Clang builds do not exceed the implementation
limit for one string literal.

## Pinned standalone source inputs

rev0015 can consume verified source trees supplied outside the cube. The fetch/build scripts
freeze these immutable inputs:

```text
c-toxcore 0.2.23
archive: https://github.com/TokTok/c-toxcore/releases/download/v0.2.23/c-toxcore-0.2.23.tar.gz
sha256: b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
license: GPL-3.0-or-later

libsodium 1.0.22
archive: https://download.libsodium.org/libsodium/releases/libsodium-1.0.22.tar.gz
sha256: adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
license: ISC

Argon2 reference 20190702
archive: https://github.com/P-H-C/phc-winner-argon2/archive/refs/tags/20190702.tar.gz
sha256: daf972a89577f8772602bf2eb38b6a3dd3d922bf5724d45e7f9589b5e830442c
license: Apache-2.0 OR CC0-1.0
```

`dependencies.lock` is authoritative for URLs, hashes, layout, and license notes. Do not replace
a hash merely because a fetch fails.

Run `tools/fetch-pinned-dependencies.sh` where outbound HTTPS is available, then
`tools/build-standalone.sh` and `tools/verify-standalone.sh`. The resulting product still has one
public executable, `iotox`; toxcore and supporting libraries are implementation dependencies,
not separate IoTox commands.

## Runtime-provider research mode

Without `IOTOX_TOXCORE_SOURCE_DIR`, IoTox can use its narrow runtime-loaded c-toxcore provider.
Without source-linked libsodium/Argon2, corresponding narrow runtime providers support exact
mock and integration work. These modes are valuable for deterministic ABI testing and operator
experiments; they are not the intended final standalone installation experience.

No c-toxcore, libsodium, or Argon2 source archive is embedded in rev0015. The standalone build
was attempted on 2026-08-14, but shell DNS could not resolve `download.libsodium.org`, so the
pinned source-linked product and real-peer lane remain externally unverified. A system-linked
`libargon2.so.1` lane did compile and pass the default CTest suite; that does not promote the
fully pinned source build to executed.
