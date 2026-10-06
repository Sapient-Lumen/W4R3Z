# Datacube bzip4 weldpoint analysis — rev0034

## Observed state

The supplied Datacube rev0117 deliberately declares:

```text
compression_codec = none-v1
```

Its bzip4 weldpoint grants no codec, parser, profile, or decompression authority.
rev0034 respects that boundary and does not modify or republish Datacube.

The reference artifact carries a 1,868,846-byte plaintext source capsule with
292 members and 1,717,079 source-member bytes. Its environment observation
reported 4 GiB total memory, about 3.25 GiB available, 56 visible CPUs, a 64 MiB
`/dev/shm`, and no readable cgroup limit. Those are dated observations, not
provider guarantees.

The immediate blocker is source budgeting. Datacube rev0117 reports a
1,244,509-byte native closure against a 1,245,184-byte ceiling, leaving only 675
bytes. A real weld needs a deliberate source-budget revision or separately
budgeted carried component. An external-only decoder would violate Datacube's
admission contract.

## Admission mapping

| Datacube requirement | bzip4 rev0034 state | Remaining Datacube work |
|---|---|---|
| Carried source/licensing | Complete source, notice, pristine bzip3 1.5.3 reference | Carry selected closure inside Datacube's audited source relation |
| Stable codec/profile | Count-bearing BZ3v1 frame plus immutable `CodecProfile` registry | Authenticate exact profile and admitted source/build identity in carrier metadata |
| Deterministic bytes | Fixed input/block policy is deterministic; lanes do not affect bytes | Add carrier vectors and canonical plan receipts |
| Stored/plain identities | Exact reconstruction; codec does not own Datacube identity law | Hash stored bytes before decode and canonical plaintext after decode |
| Bounded decode | Complete envelope preflight, output ceiling, contracted workspace, lane fitting | Intersect with Datacube effective policy and record planner/process receipts |
| Corruption canaries | Codec, truncation, mutation, and differential tests | Add carrier-level stored/profile/footer mutations and unsupported-reader tests |
| Source-only rebuild | Source-bearing release and reproducible local static builds | Weld into whole-Datacube source-only exact rebuild gate |
| Old-reader behavior | Outside codec authority | Fail closed on unsupported codec/profile IDs before decode |

## First profile contract

The codec-side identifier now exists:

```text
datacube-capsule-speed-v1
```

It requests 256 KiB blocks, up to eight lanes, and a 128 MiB codec-workspace
budget. Eight useful lanes charge 22,421,408 bytes. The supplied capsule witness
encoded to 368,948 bytes and decoded in about 27.6 ms. A single maximum-size
block encoded to 315,163 bytes but decoded in about 122.9 ms. Under the declared
priority, saving roughly 54 KiB does not justify about four times startup decode
latency.

The Datacube carrier should commit at least:

```text
compression_codec         = bzip4-bz3v1-counted-v1
compression_profile       = datacube-capsule-speed-v1
admitted_source_identity  = <committed bzip4 closure/build identity>
frame_envelope             = BZ3v1-count-bearing-high-level
requested_block_size       = 262144
reject_trailing_bytes      = true
max_stored_bytes           = <committed bound>
max_plaintext_bytes        = <committed bound>
max_block_count            = <committed bound>
max_codec_workspace_bytes  = 134217728
plaintext_sha256           = <canonical capsule identity>
stored_sha256              = <stored representation identity>
```

Names and exact field encoding remain Datacube authority, but their semantics
must be explicit. Requested lanes need not be identity-bearing because the
planner may reduce them without changing bytes.

## Critical profile caveat

BZ3v1 stores effective block size, not `datacube-capsule-speed-v1`. The
profile-aware decoder can prove compatibility with that profile's block law.
It cannot prove the external name was the encoder's intent. Small inputs can
make multiple profiles converge to the same legal effective block size.
Therefore the profile identifier and admitted implementation identity must be
authenticated by Datacube's carrier, not inferred from the compressed frame.

## Safe carrier order

```text
canonical members
  -> canonical plaintext capsule
  -> bzip4 encoding under authenticated profile
  -> optional representation transform
  -> stored bytes
  -> footer / identities
```

Read path:

1. verify the externally supplied whole-artifact digest before parser/decoder;
2. parse a fixed bounded carrier header and reject unknown codec/profile IDs;
3. validate stored length and stored digest;
4. preflight the complete count-bearing frame, trailing-byte rule, output limit,
   block count, profile compatibility, and decoder workspace;
5. fit scheduling lanes to the runtime workspace policy;
6. decode to an unpublished destination;
7. verify canonical plaintext length and digest;
8. only then parse members and continue Datacube identity checks.

Write path: freeze canonical plaintext and its identity before compression;
use the profile's fixed block law; permit lane fitting only; hash the stored
representation; and publish index/footer last under Datacube's atomic protocol.

## Binary and linking shape

rev0034 includes fully static Linux x86-64 tools built with Clang 17 `-O3` and
no IPO. They have no dynamic loader dependency and pass the 23-group suite.
This is useful operational evidence because Datacube rejects dynamically loaded
project programs.

It is not admission. The executable is architecture-specific and Datacube does
not yet carry it or its source in its own closure. The likely low-latency final
shape is a narrow linked decoder API or retained service/pool, with complete
source and tests carried under a revised budget.

## Monolithic versus per-member

The first weld should compress the canonical capsule as one multi-block stream,
not hundreds of independent frames. One stream preserves cross-file BWT context,
avoids per-member envelopes, and allows block-parallel work. Canonical member
offsets may remain in plaintext identity metadata.

Independent member frames are a future random-access profile, not an implicit
optimization. They add metadata, attack surface, and a different benchmark.

## Decision

bzip4 is technically close to Datacube's codec requirements but is not yet
constitutionally admitted. The next Datacube-side revision should make source
budget, carry the decoder and notices, authenticate the profile/build contract,
add identities and carrier canaries, and prove exact source-only rebuilding.
No additional ratio feature is required for the first weld.

Machine-readable observations are in
`evidence/datacube-weldpoint-observation.json`,
`evidence/datacube-capsule-speed-frontier.json`, and
`evidence/profile-policy-regression.json`.
