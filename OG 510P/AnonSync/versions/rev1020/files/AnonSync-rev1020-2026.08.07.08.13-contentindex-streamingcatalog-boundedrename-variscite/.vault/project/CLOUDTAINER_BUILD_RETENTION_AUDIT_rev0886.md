# Cloudtainer Build-Retention Audit — rev0886

## Finding

During rev0886 validation, the cloudtainer root filesystem reached 100% use.
The dominant reclaimable material was a succession of complete Debug, Release,
ASan/UBSan, and abandoned experimental build trees retained beside every source
handoff. The failure blocked new compiler output and therefore blocked release
validation even though the source and evidence surfaces were intact.

This was a resource-ownership failure: generated outputs had no retention owner,
expiry, quota, or canonical identity. Their directory names made them appear
valuable, but they were reproducible caches rather than authoritative evidence.

## Correction applied

Only regenerable build products from older revisions were removed. The cleanup
preserved:

- source workspaces and their design records;
- compact `REVISION_EVIDENCE` material;
- parent and released ZIP archives;
- final validation logs selected into the current evidence set; and
- the active rev0886 GCC, Clang, and sanitizer trees needed to finish validation.

The cleanup recovered approximately 21 GiB and restored enough headroom to
finish the full GCC graph, compiler-diverse focused builds, sanitizer execution,
stress, evidence generation, and package verification.

## Policy boundary

A build directory is a cache unless an external provenance system binds all
transitive inputs, toolchain identity, command line, environment policy, and
output digest. Local directory existence alone does not make a build product
authoritative. Conversely, a source or evidence filename containing the word
`build` is not a build tree. Rev0886 therefore also corrected the release-path
verifier to classify directory components, not arbitrary filename substrings.

Recommended ongoing policy:

1. Keep at most the current GCC all-target tree plus current focused Clang and
   sanitizer trees while a revision is open.
2. After sealing, retain the source ZIP, compact evidence, and externally useful
   logs; remove ordinary object, archive, binary, CMake, Ninja, sanitizer, and
   temporary test trees.
3. Place any reusable compiler cache under one quota-managed root with explicit
   age and size eviction.
4. Before deleting, prove a path is generated output and is not inside a source
   handoff, evidence index, or sealed archive.
5. Treat disk-pressure cleanup as fail-closed administration: never infer safety
   from a name alone, and never overwrite a concurrent session's workspace.

## Severe waste corrected over time

The prior workflow multiplied hundreds of megabytes of object code per lane by
many revisions. This consumed tens of gigabytes while the compact current
revision evidence remained well below one megabyte. The ratio is a warning that
build persistence had become accidental archival policy.

Future revisions should record only the build graph summary, selected logs,
compiler identities, runtime results, source projection, and immutable package
hash. Rebuildable trees should expire after the sealed archive passes its own
verifier.

## Nonclaims

This cleanup does not provide hermetic or reproducible builds, remote cache
integrity, signed provenance, supply-chain isolation, or proof that every old
build tree was unnecessary. It records the observed local failure and applies a
conservative retention boundary sufficient to continue validation without
removing authoritative source or sealed artifacts.
