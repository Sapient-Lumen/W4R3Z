# libsodium, Ed25519, stable principals, and authority-ledger v1 — rev0009

**Research date:** 2026-08-14 America/New_York  
**Implementation revision:** IoTox rev0009  
**Question:** What cryptographic and persistence contract should separate durable IoTox ownership from replaceable Tox transport identity?

## 1. Primary sources reviewed

```text
https://github.com/jedisct1/libsodium/releases/tag/1.0.22-RELEASE
https://raw.githubusercontent.com/jedisct1/libsodium/1.0.22-RELEASE/src/libsodium/include/sodium/crypto_sign_ed25519.h
https://raw.githubusercontent.com/jedisct1/libsodium/1.0.22-RELEASE/src/libsodium/include/sodium/crypto_generichash.h
https://raw.githubusercontent.com/jedisct1/libsodium-doc/master/public-key_cryptography/public-key_signatures.md
https://raw.githubusercontent.com/jedisct1/libsodium-doc/master/hashing/generic_hashing.md
https://www.rfc-editor.org/rfc/rfc8032.html
https://www.rfc-editor.org/rfc/rfc7693.html
https://www.rfc-editor.org/rfc/rfc9106.html
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://toktok.ltd/spec.html
```

The code does not copy an upstream protocol. Ed25519 and BLAKE2b are upstream primitives;
the IoTox identity file, domains, ledger bytes, roles, capability ceilings, and mutation rules
are an IoTox contract and therefore require IoTox interoperability tests.

## 2. Current upstream facts

As reviewed on 2026-08-14:

```text
libsodium latest release: 1.0.22
c-toxcore latest release: 0.2.23
```

The source-linked product path pins immutable release archives and SHA-256 values in
`dependencies.lock`. The cloudtainer could not resolve those upstream hosts, so the complete
pinned source-linked lane did not run here. The dynamic research path did execute against the
system `libsodium.so.23`, which reports libsodium 1.0.18. That proves the consumed stable API
subset on this host; it does not prove the pinned 1.0.22 archive/build.

## 3. Why Ed25519 is the rev0009 principal primitive

The libsodium signing API provides:

```text
32-byte deterministic seed
32-byte Ed25519 public key
64-byte libsodium Ed25519 secret-key representation
64-byte detached signature
```

`crypto_sign_seed_keypair()` derives the same key pair from the same 32-byte seed.
`crypto_sign_detached()` and `crypto_sign_verify_detached()` provide a fixed-size detached
signature. RFC 8032 supplies independent Ed25519 test vectors; rev0009 executes test vector 1
for the empty message.

Ed25519 is used here because it gives a compact, widely implemented, deterministic signature
identity suitable for canonical fixed-size records. This is not a claim that Ed25519 alone
solves ownership. A signature proves that the holder of a secret corresponding to a public key
signed exact bytes. The authorization ledger establishes which public key the device currently
recognizes and what that key may do.

The rev0009 code uses the one-shot Ed25519 API over a bounded message. It does not use Ed25519ph,
convert keys to X25519, or use application signing keys as encryption keys.

## 4. Why BLAKE2b-256 is used, and where it is not used

Libsodium's generic-hash API is BLAKE2b. It supports fixed-length unkeyed hashes and keyed use
as a pseudorandom function. IoTox fixes 32-byte output and prefixes every use with an explicit
protocol domain.

Unkeyed hash contract:

```text
BLAKE2b-256(
    "IOTOXH1" ||
    uint16_be(domain_length) ||
    domain ||
    payload
)
```

Keyed derivation contract:

```text
BLAKE2b-256-keyed(
    key = 32-byte root,
    message =
        "IOTOXK1" ||
        uint16_be(domain_length) ||
        domain ||
        context
)
```

Current domains include:

```text
iotox-owner-signing-seed-v1
iotox-authority-record-digest-v1
iotox-authority-record-signature-v1
```

BLAKE2b is not used as the password function. RecallRoot-v1 first derives a 32-byte root using
the separately frozen Argon2id contract. Keyed BLAKE2b derives purpose-specific material from
that root.

## 5. Root and principal separation

rev0009 implements three distinct identities:

```text
RecallRoot-v1
    permanent reconstructible owner root derived from a generated phrase

IoTox owner principal
    Ed25519 key deterministically derived from RecallRoot-v1 with
    domain "iotox-owner-signing-seed-v1"

IoTox device principal
    independent random Ed25519 seed generated and stored by the device

Tox route identity
    c-toxcore savedata identity used for Tox addressing and sessions
```

The owner principal is stable across devices when the same permanent phrase is used. That is
the desired re-entry property and also creates cross-device linkability wherever the public
owner key is visible. A future delegated per-device controller layer may reduce routine
linkability without changing the permanent root contract.

The stable device principal survives replacement of Tox savedata and future route-specific Tox
keys. rev0009 does not yet sign a Tox endpoint binding or prove the device principal over the
network.

## 6. Stable device identity file v1

The device identity file is exactly 80 bytes:

```text
offset  size  field
0       8     ASCII "IOTOXID1"
8       1     format = 1
9       1     algorithm = Ed25519 = 1
10      6     reserved = zero
16      32    Ed25519 seed
48      32    Ed25519 public key
```

Load requirements:

```text
regular file
owned by effective user
no group or other permission bits
exactly 80 bytes
recognized magic/version/algorithm
reserved bytes zero
public key exactly re-derives from stored seed
```

Creation uses the operating-system CSPRNG and atomic `0600` state replacement. If a non-empty
or merely present authority-ledger path exists while the identity file is absent, the agent
refuses to generate an unrelated identity. This avoids silently detaching an existing ledger
from its device principal.

The seed is currently plaintext at rest behind Unix permissions. This is a development and
Linux-appliance baseline, not secure-element protection. Keystore integration must preserve
stable public identity and explicit export/recovery policy.

## 7. Signed authority record v1

Each record is exactly 256 bytes. The first 192 bytes are signed; the final 64 bytes are the
Ed25519 signature.

```text
offset  size  field
0       4     ASCII "IAL1"
4       1     record format = 1
5       1     action: bootstrap=1, grant=2, revoke=3
6       1     role
7       1     reserved = zero
8       8     sequence, unsigned big-endian
16      8     ownership epoch, unsigned big-endian
24      8     not-before Unix ms; v1 requires zero
32      8     not-after Unix ms; v1 requires zero
40      8     capability mask, unsigned big-endian
48      32    stable IoTox device public key
80      32    issuer public key
112     32    subject public key
144     32    digest of complete previous record; zero for bootstrap
176     16    reserved = zero
192     64    detached Ed25519 signature by issuer
```

The bytes signed are:

```text
"IOTOXS1" ||
uint16_be(length("iotox-authority-record-signature-v1")) ||
"iotox-authority-record-signature-v1" ||
record_body_192
```

The chain digest is the IoTox unkeyed BLAKE2b-256 contract with domain
`iotox-authority-record-digest-v1` over all 256 record bytes.

The signature domain is deliberately included in the signed message rather than relying on an
informal call-site convention. Reserved fields are zero so later formats cannot be confused
with v1 records.

## 8. Ledger file v1

The ledger is a 16-byte header followed by complete 256-byte records:

```text
offset  size  field
0       8     ASCII "IOTOXAL1"
8       1     ledger format = 1
9       1     record format = 1
10      2     reserved = zero
12      4     record count, unsigned big-endian
16      ...   exactly record_count records
```

The configured default maximum is 4096 records. The file is read with `O_NOFOLLOW`, must be a
private regular file owned by the effective user, and must match the bounded exact length.
Every append first replays and validates the candidate in memory, then atomically rewrites the
complete bounded file, synchronizes it, and publishes the new snapshot only after persistence
succeeds.

This is append-only in logical history, not append-in-place on disk. The design favors simple
crash behavior and deterministic replay while the ledger remains bounded. Compaction and an
ownership-epoch transition format are not implemented.

## 9. Bootstrap, grant, revoke, and succession rules

First record:

```text
action = bootstrap
sequence = 1
ownership_epoch = 1
role = owner
capabilities = all v1 capabilities
issuer = subject
previous_digest = zero
self-signed by that owner
```

Every later record must:

```text
use sequence current + 1
use the current ownership epoch
name the same stable device principal
carry the exact previous record digest
be signed by an active issuer
come from an issuer holding manage.principals
```

A grant must:

```text
use a non-none role
use a non-empty known capability set
stay within the fixed role ceiling
stay within the issuer's own capability set
be issued by an owner when granting owner role
assign all v1 capabilities to an owner
not demote an active owner by overwriting it with another role
```

The owner-demotion rule is important. Without it, an administrator with
`manage.principals` could target an existing owner with a viewer grant and bypass both the
owner-only revoke rule and last-owner protection. rev0009 validates this at both preparation
and append/replay. Preparation is a convenience and race-reduction boundary; append/replay is
the security boundary because callers can construct signed bytes independently.

A revoke must:

```text
use role none and zero capabilities
target an active principal
be issued by an owner when the subject is an owner
leave at least one active owner
```

Changing owners is therefore explicit:

```text
grant successor owner -> successor becomes active
revoke prior owner     -> prior owner becomes inactive
```

The v1 ledger does not yet define a single-record ownership transfer or epoch increment.

## 10. Roles and capability ceilings

Roles are display and policy classes; authorization checks use the capability mask.

```text
owner
    all capabilities

administrator
    all except factory.reset

operator
    read.telemetry, write.settings, actuate

viewer
    read.telemetry

automation
    read.telemetry, write.settings, actuate

service
    read.telemetry, write.settings, export.diagnostics
```

Capabilities are frozen bit positions:

```text
0  read.telemetry
1  write.settings
2  actuate
3  manage.principals
4  install.firmware
5  export.diagnostics
6  factory.reset
```

Unknown roles, actions, capability bits, non-zero reserved bytes, zero public keys, invalid
sequence/epoch values, malformed lengths, bad signatures, wrong-device records, stale tails,
and unauthorized mutations fail closed.

## 11. RecallRoot local mutation ceremony

The one `iotox` binary supports:

```text
authority-bootstrap-recall-stdin
authority-grant-recall-stdin PUBLIC_KEY ROLE CAPABILITIES
authority-revoke-recall-stdin PUBLIC_KEY
```

The CLI:

1. reads the permanent phrase from standard input with a strict bound;
2. validates/canonicalizes it under RecallRoot-v1;
3. runs Argon2id locally;
4. derives the stable owner signing seed locally;
5. asks the agent to prepare exact canonical record-body bytes;
6. signs those exact bytes locally;
7. sends only the signed record to the agent;
8. wipes temporary phrase, root, seed, secret-key, and signing-message storage where the C++
   process controls it.

The agent never receives the phrase, RecallRoot, owner seed, or owner secret key. The local
Unix account remains a trust boundary: a hostile process with equal privileges may inspect or
interfere with process input, libraries, files, or IPC.

`authority-append-hex` is retained as an expert/interoperability seam. It does not bypass
signature, chain, device, issuer, role, capability, or last-owner validation.

## 12. What rev0009 proves

Executed in this cloudtainer:

```text
libsodium dynamic API loading against system libsodium 1.0.18
RFC 8032 Ed25519 test vector 1
stable device identity create/load/re-derive/corruption rejection
canonical authority prepare/record encode/decode
bootstrap, grant, revoke, restart replay
signature tamper rejection
wrong policy rejection
implicit owner-demotion rejection at prepare and append
last-owner protection before signing
explicit grant-successor then revoke-prior-owner succession
private file permissions and bounded persistence
one-binary CLI -> local socket -> agent mutation process path
Clang ASan/UBSan, GCC TSan, and authority decoder libFuzzer smoke in the retained matrix
```

## 13. What rev0009 does not prove

```text
pinned libsodium 1.0.22 source-linked build in this cloudtainer
real c-toxcore peer operation
remote proof of owner or device principal
binding of either principal to the current confirmed Tox transcript
wire authorization feature negotiation
authorization of any remote command
ledger rollback resistance after whole-file restoration
trusted-clock expiry policy
ownership epoch transition
multi-signature or quorum policy
secure-element protection
post-quantum signature security
formal protocol analysis or independent audit
```

The runtime continues to publish:

```text
authorization=none-transport-session-only
```

until a fresh transcript-bound proof is implemented and tested. `authorization-ledger-v1`
remains unadvertised on the wire.

## 14. Next cryptographic construction boundary

The next network step should not send the permanent phrase or stable secret. It should define a
fresh challenge/proof over the already confirmed online-epoch transcript, including at least:

```text
protocol and proof format version
stable device principal
claiming principal
current ownership epoch
current ledger sequence/tail digest
both Tox transport public keys or the canonical confirmed-session digest
fresh challenge/nonces from both sides
requested proof purpose
expiry or bounded session lifetime without assuming a trusted wall clock
```

The proof must be signed by the claimed application principal and verified against the local
ledger. Friendship and transcript confirmation remain necessary transport/session conditions,
but neither is sufficient authority.

A future device signature may attest the route binding and challenge response. That does not
replace owner authorization; it proves that the responder controls the stable device principal
whose ledger the owner recognizes.

## 15. Security posture

The selected primitives are mature; the composition is new. The strongest current claims are
therefore mechanical:

```text
fixed bytes
fixed domains
fixed roles and bits
strict parser
independent signature verification
bounded deterministic replay
explicit evidence boundary
```

Do not translate those properties into “production secure.” The next office holder should
prefer narrow interoperable records, adversarial tests, external review, and an easy dependency
update path over clever undocumented cryptographic composition.
