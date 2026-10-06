# Reproducibility variation harness (reprotest + diffoscope + optional stabilization)

Bit-for-bit reproducibility is the strongest form of supply-chain assurance.
In practice, some packages remain non-deterministic for mundane reasons (timestamps, paths, file ordering).
DeriveBSD should make this **measurable** and **explainable**, and allow policy to decide what is acceptable.

This document proposes a *variation harness* lane that:

- builds the same Plan twice (or more) under controlled **environment variations**
- records whether the artifacts are bit-identical
- when they are not, produces a deep diff report for triage
- optionally, applies **stabilizers** that strip known-useless nondeterminism to test *functional equivalence* (never a replacement for bit-identical checks)

## Prior art

- **reprotest**: builds the same source twice in different environments and checks for differences.
- **diffoscope**: recursively explains where two artifacts differ (archives, ISOs, binaries, etc.).
- **OSS-Rebuild stabilizers**: “stabilization” transforms artifacts to remove observable environment noise while preserving semantics, enabling functional comparison at scale.

## DeriveBSD shape

### Evidence objects

For a Plan `P` and resulting artifact digest `A`:

- `repro.check.json` (JCS-hashable)
  - plan digest, artifact digest, toolchain capsule digest
  - variations applied (matrix)
  - verdict: `identical | differs | waived`
  - pointers to diff reports (store object digests)
- `repro.diffoscope.html.zst` (optional)
  - stored as an artifact-adjacent evidence object
- `repro.stabilize.json` (optional)
  - stabilizer set used
  - stabilized digests of both artifacts
  - verdict: `equivalent | differs`

### Variation matrix

DeriveBSD should start small and expand carefully:

- `SOURCE_DATE_EPOCH` presence/absence (policy-controlled)
- build directory / path randomization
- locale / timezone
- `umask`
- randomized file ordering when packaging
- CPU count

Every variation is declared and recorded; nothing “just happens”.

### Policy hooks

Policy may require any combination of:

- *bit-identical* for specific packages/classes
- *witness rebuild quorum* + identical digests
- allow `differs` but require a diffoscope report + manual approval
- allow “stabilized equivalence” only for low-risk artifact classes

## Why this matters for DeriveBSD

- Fits the core promise: **explainable** (“why do these bits differ?”) and **verifiable**.
- Makes “treat builders hostile” actionable: independent rebuilders can *prove* agreement or show a tight diff.
- Helps prioritize engineering effort: quantify nondeterminism hotspots rather than guessing.

See also:
- `docs/116-witness-rebuilders-diffoscope.md`
- `docs/141-build-records-buildinfo-and-rebuilders.md`
