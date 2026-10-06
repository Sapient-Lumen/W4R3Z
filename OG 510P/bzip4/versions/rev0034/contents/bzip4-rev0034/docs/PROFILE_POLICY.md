# Versioned codec profile policy — rev0034

## Purpose

bzip4 now exposes named profiles so Datacube can choose a stable byte policy
without repeating a fragile list of numeric command-line arguments. A profile
commits the requested block size. That choice changes frame partitioning and
therefore encoded bytes. Lane count and workspace budget are realization
settings: fitting either downward changes elapsed time, not BZ3v1 bytes.

The profile layer does not create a new wire format. Frames remain the same
13-byte, count-bearing BZ3v1 high-level envelope used throughout this project.

## Registry

| Identifier | Intended use | Requested block | Requested lanes | Default codec budget |
|---|---|---:|---:|---:|
| `datacube-capsule-speed-v1` | Small carried-source capsules where latency dominates | 256 KiB | 8 | 128 MiB |
| `cloudtainer-speed-v1` | General Datacube/cloudtainer throughput | 1 MiB | 8 | 128 MiB |
| `cloudtainer-balanced-v1` | Explicit speed/size compromise | 2 MiB | 8 | 128 MiB |

The planner limits active lanes by block count and workspace before codec
states are created. At eight useful blocks, the maximum codec-arena charges are
22,421,408 bytes, 60,925,136 bytes, and 112,263,440 bytes respectively. These
charges are admission bounds, not predictions of process RSS.

## Production command path

The named commands are the recommended operational interface:

```sh
bzip4_codec profiles
bzip4_codec profile-plan cloudtainer-speed-v1 INPUT_BYTES
bzip4_codec compress-profile cloudtainer-speed-v1 INPUT OUTPUT.bz3
bzip4_codec decompress-profile cloudtainer-speed-v1 \
  OUTPUT.bz3 RESTORED MAX_OUTPUT_BYTES
```

An optional workspace argument can lower the runtime lane count. It cannot
silently lower the block size. If one lane cannot fit, the operation fails
before destination publication.

The older `compress`, `compress-fit`, `decompress`, and `decompress-fit`
commands remain for experiments and compatibility. In particular,
`compress INPUT OUTPUT` still means the historical 16 MiB scalar policy. It is
not the recommended Datacube default and must not be mistaken for
`cloudtainer-speed-v1`.

## What the frame can and cannot prove

BZ3v1 stores the effective block size, not a bzip4 profile identifier. A decoder
can prove that a validated frame is compatible with a profile's block law. It
cannot prove which external profile name the encoder intended.

Small inputs make this especially visible. The codec clamps requested block
size to the legal minimum and to input length, so two profiles can converge to
the same effective block size. Therefore Datacube must authenticate and retain:

- the exact profile identifier;
- the bzip4 source/build identity admitted for that carrier;
- stored and plaintext content identities;
- maximum output and codec-workspace limits; and
- unsupported-reader semantics.

The profile-aware decoder still performs complete envelope preflight before it
creates a destination. For a large enough frame, requesting an incompatible
profile fails with codec status 65 and leaves no output path.

## Stability rules

1. Never alter an existing profile's requested block size. Add a new identifier.
2. Runtime lane fitting is allowed because lane count does not affect bytes.
3. A compiler change is allowed only after byte-identity and strict validation.
4. A codec change that changes block records requires a new format or an
   explicitly distinct codec contract, not a silent profile edit.
5. Automatic content classification remains outside these profiles. A stable
   profile must be reproducible from authenticated metadata alone.
6. The 256 MiB setting is not eligible for any profile while its observed
   decode-time pathology remains unexplained.

## Regression witness

The rev0034 command-level regression uses a 3,479,061-byte deterministic input.
`cloudtainer-speed-v1` plans four useful lanes, encodes four 1 MiB-policy blocks,
round-trips exactly, and rejects decoding under
`datacube-capsule-speed-v1` before destination creation. Machine-readable
results are in `evidence/profile-policy-regression.json`.
