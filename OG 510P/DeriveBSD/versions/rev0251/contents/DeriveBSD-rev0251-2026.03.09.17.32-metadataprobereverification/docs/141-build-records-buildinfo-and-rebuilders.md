# Build records (`.buildinfo` lessons) + witness rebuilders

Reproducible-build ecosystems learned that **“it built once”** is not the same as **“it can be rebuilt”**.
Debian’s `.buildinfo` files are a concrete, widely-used mechanism: they capture enough build environment
detail so *independent rebuilders* can attempt bit-for-bit reproduction.

References:
- Debian “BuildinfoFiles” (what a buildinfo records): https://wiki.debian.org/ReproducibleBuilds/BuildinfoFiles
- reproduce.debian.net (rebuilds packages using `.buildinfo`): https://reproduce.debian.net/

## DeriveBSD direction

DeriveBSD already has Spec → Lock → Plan → Artifact. The missing evidentiary object is a canonical
**Build Record** that binds:

- Plan digest
- builder capsule digest (the “hostile builder” environment)
- toolchain identities + versions
- environment knobs that affect determinism (TZ, locale, SOURCE_DATE_EPOCH)
- declared build inputs (closure) and their digests

The record must be:
- **canonical + hashable** (JCS / stable ordering)
- **small** (references digests, does not inline huge manifests)
- **signed** by the builder identity

## How it works with witness rebuilders

Witness rebuilders (docs/116) should attest over:
- the Build Record digest
- the produced Artifact digest
- any diff metadata (if policy allows explainable divergence)

This gives a clean separation:
- “bytes are authentic” (cache signatures)
- “build was reproducible” (N independent witnesses)
- “why it wasn’t” (diff summaries)

## v1 minimalism

- Only require Build Records for high-value artifacts (base sets, runtimes).
- If we already have a Plan and capsule digest, start with a **thin record** and grow fields only
  when a real divergence requires it.

See RFC-0093.

## Toolchains are special

For compilers, “rebuildable” is not enough: a compromised compiler can reproduce its own compromise.
High-assurance channels may require **Diverse Double-Compiling (DDC)** results as additional evidence.

See: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md` (RFC-0126).
