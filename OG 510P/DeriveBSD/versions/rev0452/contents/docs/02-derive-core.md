# The Derive core

DeriveBSD is designed around a boring, explicit pipeline:

1. **Spec → Lock**
   - resolve sources (git/tarball), record cryptographic hashes
   - resolve dependency constraints
   - freeze toolchain identities

2. **Lock → Plan**
   - compute a fully evaluated DAG (all steps explicit)
   - apply policy (network, time, licenses, trust)
   - normalize environment (locale, timezone, timestamps)

3. **Plan → Artifact**
   - execute in a sandbox
   - emit into store
   - record provenance; optionally emit attestations

4. **Artifact → Closure → Install/Activate**
   - compute runtime closure
   - install by referencing store paths (no copying)
   - activate atomically; track generations


## Identity chain (what gets hashed, what gets signed)

DeriveBSD treats the pipeline as a chain of immutable, hashable objects:

- **Spec digest**: canonicalized Spec-as-data (`docs/80-canonical-json-hashing-jcs.md`)
- **Lock digest**: Spec digest + resolved source identities + toolchain pins
- **Policy decision digest**: policy engine identity + policy inputs + effective constraints (`docs/93-policy-decision-records.md`)
- **Plan digest**: Lock digest + policy decision digest + fully-evaluated DAG + normalized env
- **Artifact digest**: Plan digest + realized outputs (store paths / bundle)

For runtime safety, consumers should additionally bind:
- **Closure manifest digest**: complete transitive runtime dependency set (`docs/90-closure-proof.md`)
- **Closure proof**: signature over closure manifest digest + anti-freeze metadata

Policy decides what must be signed/attested, but the baseline is:
- **verify digests**
- **verify signatures** (see `adrs/ADR-0009-artifact-verification.md`)
- optionally verify required attestations (`docs/71-attestations-dsse-in-toto-slsa.md`)

This is the foundation of “explain”: every deployed bit points back to the digests that derived it.

## Evidence spine (operations are artifacts too)

DeriveBSD should treat privileged operations the same way it treats builds: as **typed, immutable evidence**.
Configuration applies, change execution, platform posture checks, and key operational subsystems (faults, services, storage, time, PKI) should emit receipts and structured events that can be queried and bundled.

See: `docs/229-evidence-spine-overview.md`.


## Design principle: data-first, code-last

User-facing configuration must be typed data with stable merge semantics. If we allow scripting:
- it is explicit
- it is versioned
- it is hermetic by default
- it is linted and constrained

## The “single workflow” rule

We should not ship multiple parallel “recommended” flows.
One project format, one lockfile, one system activation story, one CLI surface.


Last updated: 2026-02-25
