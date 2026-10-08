# AnonSync rev0899 research and speculation

Research was rechecked on 2026-07-25 against primary implementation-owner
sources. Proposed changes are explicitly design hypotheses until implemented and
tested.

## SQLite role identity and file binding

- `PRAGMA application_id`: https://sqlite.org/pragma.html#pragma_application_id
- SQLite database file format: https://www.sqlite.org/fileformat.html

SQLite reserves the signed 32-bit header field at offset 68 for an application
identifier. Rev0899 uses distinct role values only as early wrong-file
classification. The field is not secret, collision-resistant, or sufficient
authority; exact schema and deployment-row attestation remain mandatory.

## WAL, sidecars, and store-set atomicity

- Write-Ahead Logging: https://www.sqlite.org/wal.html
- ATTACH DATABASE: https://sqlite.org/lang_attach.html
- Temporary files and super-journals: https://www.sqlite.org/tempfiles.html
- Atomic commit assumptions: https://www.sqlite.org/atomiccommit.html

WAL and shared-memory files are persistent members of the live database state,
which supports rejecting orphan `-wal`/`-shm` names during fresh bootstrap.
SQLite also documents that transactions spanning attached databases are not
atomic as one set under WAL. Speculation: future multi-store transitions need a
durable coordinator with explicit prepare/commit/recovery records, or a schema
consolidation that makes the transaction truly single-database.

SQLite durability claims depend on VFS, filesystem, kernel, controller, and
mount behavior honoring flush and atomicity assumptions. Rev0899 therefore does
not claim universal power-loss behavior on unusual or broken storage stacks.

## SQLite dependency freshness

- SQLite 3.53.4 release log: https://sqlite.org/releaselog/3_53_4.html
- Official download and hashes: https://sqlite.org/download.html

SQLite 3.53.4 was released on 2026-07-24 and fixes issues present in 3.53.0
through 3.53.3. The official source ID is
`bf7c7f30031888f4e796e429ab3978879485813aaca6f641c7b33e4e09459bcc`.
The official page publishes SHA3-256
`67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`
for `sqlite3.c` and
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`
for the 3.53.4 amalgamation archive.

Rev0899 keeps the reviewed 3.53.3 pin because the cloudtainer could not obtain
and independently verify the official archive bytes. Speculation: the next
dependency-only revision should import the exact official archive, prove both
published SHA3 values plus local SHA-256 pins, then rerun SQLite boundary,
crash/process, and full registered lanes.

## CSPRNG deployment identity

- OpenSSL `RAND_bytes`: https://docs.openssl.org/3.6/man3/RAND_bytes/

OpenSSL documents `RAND_bytes` as cryptographically secure when it succeeds and
requires callers to check the return value. Rev0899 fails closed unless the full
32-byte deployment ID is produced, then encodes it as exactly 64 lowercase hex
characters. Speculation: if hostile local writers become in-scope, bind the
manifest and store rows with an operator or hardware-backed signing key held
outside the writable deployment resources; placing an HMAC key beside the data
would not change the attacker's power.

## Descriptor-rooted path authority

- Linux `openat2(2)`: https://man7.org/linux/man-pages/man2/openat2.2.html

Resolution controls such as `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`,
`RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_MAGICLINKS` suggest a stronger Linux
boundary than canonical strings plus final-component no-follow. Speculation:
introduce one deployment-root directory capability and resolve portable relative
resource names through it, with a reviewed component walk or native equivalent
on non-Linux platforms.

## Build-cost correction

- CMake compiler launchers:
  https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_COMPILER_LAUNCHER.html
- CMake `UNITY_BUILD`: https://cmake.org/cmake/help/latest/prop_tgt/UNITY_BUILD.html
- CMake compile job pools:
  https://cmake.org/cmake/help/latest/prop_tgt/JOB_POOL_COMPILE.html

The explicitly clean Debug graph scheduled 426 actions, while the complete test
registry ran in 18.30 seconds. Speculation: measure `ccache`/`sccache` hit rate,
header fan-out, and a product-only target lane before considering target-scoped
unity builds. Global unity mode could hide dependency errors, macro collisions,
and ODR problems, so it should not be used merely to conceal graph fragmentation.

## Privacy nonclaim

Mutual TLS and SPKI authorization authenticate peers and protect transport
contents. They do not by themselves provide anonymity, endpoint hiding,
unlinkability, cover traffic, metadata minimization, or traffic-analysis
resistance. Those remain separate product and threat-model workstreams.
