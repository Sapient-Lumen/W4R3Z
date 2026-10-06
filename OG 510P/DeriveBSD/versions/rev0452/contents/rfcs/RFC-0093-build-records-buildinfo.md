# RFC-0093: Build Records (`.buildinfo` lessons)

Status: draft

## Motivation

We want to treat builders as hostile and still be able to *prove* what happened.
Reproducible-build ecosystems use explicit build environment records (e.g. Debian `.buildinfo`) to make
independent rebuilding tractable.

References:
- Debian buildinfo overview: https://wiki.debian.org/ReproducibleBuilds/BuildinfoFiles
- reproduce.debian.net uses `.buildinfo` to attempt bit-for-bit rebuilds: https://reproduce.debian.net/

## Proposal

Add a canonical Build Record object produced at build time:

`build.record.json` (JCS canonical)

It binds:
- Plan digest
- builder capsule digest
- build inputs (closure digest reference)
- toolchain identities and versions
- determinism knobs (TZ/LC_* / SOURCE_DATE_EPOCH)
- build script digest / derivation digest

It is signed by the builder identity and may be included inside DSSE/in-toto attestations.

## Policy use

Policies can require:
- Build Record exists and is signed
- N witness rebuilders attest to reproduction using the same Build Record digest

## Minimalism

- Start with a *thin* Build Record: only fields known to influence determinism.
- Expand fields only when divergence analysis requires it.
